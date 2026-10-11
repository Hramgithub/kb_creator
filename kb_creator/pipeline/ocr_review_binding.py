"""Bind existing full-block visual corrections to verified Stage04 packets."""
from __future__ import annotations

import json
import shutil
from pathlib import Path

from .identity import assert_existing_path_components_are_not_reparse, file_identity
from . import mechanical_reconstruction as mechanical
from . import five_step_language as storage

SCHEMA = "kb_creator.bound_ocr_review.v1"
VIEW = "original_pipeline_ocr"


def _read(path: Path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def _local(root: Path, name: str) -> Path:
    if not isinstance(name, str) or not name or Path(name).is_absolute() or ":" in name:
        raise ValueError("review evidence path must be relative")
    path = root / name
    assert_existing_path_components_are_not_reparse(path)
    path = path.resolve(strict=True)
    if not path.is_relative_to(root.resolve()):
        raise ValueError("review evidence escapes its root")
    return path


def _pages(rows: list, key: str, count: int) -> dict:
    if not isinstance(rows, list):
        raise ValueError("page coverage must be a list")
    result = {}
    for row in rows:
        number = row.get(key) if isinstance(row, dict) else None
        if type(number) is not int or number in result or not 1 <= number <= count:
            raise ValueError("duplicate or invalid review page")
        result[number] = row
    if set(result) != set(range(1, count + 1)):
        raise ValueError("review coverage must include every source page")
    return result


def bind_ocr_reviews(run_root: Path, coverage_path: Path, source_review_path: Path,
                     render_root: Path, metadata_path: Path, output: Path,
                     *, authority_validator=None) -> dict:
    paths = (run_root, coverage_path, source_review_path, render_root, metadata_path, output)
    for path in paths:
        assert_existing_path_components_are_not_reparse(path)
    run_root, coverage_path, source_review_path, render_root, metadata_path, output = (p.resolve() for p in paths)
    if output.exists() or any(output.is_relative_to(p) or p.is_relative_to(output)
                              for p in (run_root, coverage_path, source_review_path, render_root, metadata_path)):
        raise ValueError("bound review output must be new and outside inputs")
    stage = mechanical._verify_stage04(run_root, authority_validator)
    run = _read(run_root / "run.json")
    count = run["source"]["page_count"]
    source_hash = run["source"]["sha256"]
    coverage, source_review = _read(coverage_path), _read(source_review_path)
    if coverage.get("source_sha256") != source_hash or coverage.get("page_count") != count:
        raise ValueError("OCR review source identity differs from run")
    if source_review.get("schema") != "kb_creator.source_review_coverage.v1" or source_review.get("source", {}).get("sha256") != source_hash or source_review["source"].get("pages") != count:
        raise ValueError("source visual review identity differs from run")
    if not metadata_path.is_relative_to(run_root / "outputs/02-mineru-three-view/views" / VIEW):
        raise ValueError("metadata must belong to verified original OCR view")
    metadata_id = file_identity(metadata_path)
    if metadata_id["sha256"] != coverage.get("metadata_sha256"):
        raise ValueError("review metadata identity mismatch")
    metadata = _read(metadata_path)
    if not isinstance(metadata, list):
        raise ValueError("OCR content list must be a list")
    covered = _pages(coverage.get("pages"), "source_page", count)
    visuals = _pages(source_review.get("pages"), "page", count)
    packets = {number: (path, value) for number, path, value in mechanical._load_packets(stage)}
    if set(packets) != set(covered):
        raise ValueError("Stage04 packet coverage differs from review")
    reports, report_pages, evidence_files, rows, pages = {}, {}, {}, [], []
    for number in range(1, count + 1):
        item, visual = covered[number], visuals[number]
        report_path = _local(coverage_path.parent, item["report"])
        report_id = file_identity(report_path)
        if report_id["sha256"] != item.get("report_sha256"):
            raise ValueError("review report identity mismatch")
        if report_path not in reports:
            report = _read(report_path)
            if report.get("schema") not in {"kb_creator.preliminary_ocr_visual_review.v1", "kb_creator.preliminary_ocr_visual_review.v2"}:
                raise ValueError("unsupported OCR review report schema")
            view = report.get("ocr_view", {})
            if report.get("view", view.get("name")) != VIEW or report.get("metadata_sha256", view.get("source_content_list_sha256")) != metadata_id["sha256"]:
                raise ValueError("report OCR view/metadata mismatch")
            if "source" in report and report["source"].get("sha256") != source_hash:
                raise ValueError("report source mismatch")
            selected = {}
            for page in report["pages"]:
                n = page["source_page"]
                if n in selected or n not in covered or covered[n]["report"] != item["report"]:
                    raise ValueError("report page duplicated, stale or not selected by coverage")
                selected[n] = page
            reports[report_path], report_pages[report_path] = report, selected
            evidence_name = "reports/" + report_path.name
            if evidence_name in evidence_files and evidence_files[evidence_name] != report_path:
                raise ValueError("review report filenames collide in evidence bundle")
            evidence_files[evidence_name] = report_path
        page = report_pages[report_path].get(number)
        render_path = _local(render_root, visual["render"])
        render_id = file_identity(render_path)
        if page is None or any(value != render_id["sha256"] for value in (visual.get("sha256"), item.get("visual_sha256"), page.get("visual_sha256"))):
            raise ValueError("review source render identity mismatch")
        packet_path, packet = packets[number]
        blocks = {r["raw_index"]: r for r in packet["views"][VIEW]["blocks"]}
        if len(blocks) != len(packet["views"][VIEW]["blocks"]):
            raise ValueError("duplicate packet block selector")
        indices = page.get("ordered_raw_indices")
        if not isinstance(indices, list) or any(type(raw) is not int for raw in indices) or len(set(indices)) != len(indices):
            raise ValueError("review block coverage differs from packet")
        accounted = set(indices)
        # Some reviewed reports keep ornamental and empty continuation blocks
        # outside prose order. Account for their explicit rows, never infer deletion.
        dispositions = {}
        for name in ("source_furniture", "furniture_dispositions", "empty_continuations", "continuation_dispositions"):
            items = page.get(name, [])
            if not isinstance(items, list) or any(not isinstance(row, dict) or type(row.get("raw_index")) is not int for row in items):
                raise ValueError("review block disposition invalid")
            dispositions[name] = items
            accounted.update(row["raw_index"] for row in items)
        if not accounted <= set(blocks):
            raise ValueError("review block coverage differs from packet")
        unreviewed = sorted(set(blocks) - accounted)
        corrected = set()
        for correction in page.get("ocr_corrections", []):
            if not isinstance(correction, dict) or set(correction) != {"raw_index", "before", "after", "reason"}:
                raise ValueError("full-block correction contract required")
            raw, before, after = (correction[k] for k in ("raw_index", "before", "after"))
            if type(raw) is not int or raw in corrected or raw not in accounted or not 0 <= raw < len(metadata):
                raise ValueError("duplicate or invalid correction selector")
            if not all(isinstance(correction[k], str) and correction[k].strip() for k in ("before", "after", "reason")) or before == after:
                raise ValueError("correction text/reason invalid")
            original = metadata[raw]
            if blocks[raw].get("text", "") != before or original.get("text", "") != before or original.get("page_idx") != number - 1:
                raise ValueError("correction before text does not bind exact packet/metadata block")
            if any(ord(ch) < 32 and ch not in "\t\r\n" for ch in after):
                raise ValueError("correction after contains control characters")
            corrected.add(raw)
            rows.append({"source_page": number, "view": VIEW, **correction,
                         "before_sha256": mechanical._sha(before.encode()),
                         "after_sha256": mechanical._sha(after.encode()),
                         "packet": {"path": str(packet_path.relative_to(run_root)), **file_identity(packet_path)},
                         "report": {"path": "reports/" + report_path.name, **report_id},
                         "source_render": {"path": str(render_path), **render_id}})
        pages.append({"source_page": number, "corrected_raw_indices": sorted(corrected),
                      "ordered_raw_indices": indices, "reviewed_dispositions": dispositions,
                      "unreviewed_raw_indices": unreviewed,
                      "unresolved": page.get("unresolved", []), "source_render": render_id})
    if len(rows) != coverage.get("exact_full_block_corrections"):
        raise ValueError("review correction count mismatch")
    evidence_files.update({"coverage.json": coverage_path, "source-review.json": source_review_path})
    evidence = {name: file_identity(path) for name, path in evidence_files.items()}
    result = {"schema": SCHEMA, "state": "bound_reviewed_corrections_candidate_only",
              "source": run["source"], "metadata": {"path": str(metadata_path.relative_to(run_root)), **metadata_id},
              "run_root": str(run_root), "page_count": count, "pages": pages, "corrections": rows,
              "evidence": evidence, "reconstruction_accepted": False}
    result["ledger_sha256"] = mechanical._sha(mechanical._canonical(result))

    def build(staging):
        for name, path in evidence_files.items():
            destination = staging / name
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(path, destination)
            if file_identity(destination) != evidence[name]:
                raise ValueError("review evidence changed during copy")
        storage._write(staging / "bound-corrections.json", result)

    storage._atomic(output, build)
    return result
