"""Validate saved OCR review evidence before consuming its correction claims."""
from __future__ import annotations

import json
from pathlib import Path

from . import mechanical_reconstruction as mechanical
from .identity import assert_existing_path_components_are_not_reparse, file_identity
from .ocr_review_binding import SCHEMA, VIEW, _pages


def _read(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def _file(root, record):
    if not isinstance(record, dict) or set(record) != {"path", "bytes", "sha256"}:
        raise ValueError("invalid bound file reference")
    name = record["path"]
    if not isinstance(name, str) or not name or Path(name).is_absolute() or ":" in name:
        raise ValueError("bound evidence must use a relative path")
    path = root / name
    assert_existing_path_components_are_not_reparse(path)
    path = path.resolve(strict=True)
    if not path.is_relative_to(root.resolve()) or not path.is_file():
        raise ValueError("bound evidence escapes its root")
    if file_identity(path) != {key: record[key] for key in ("bytes", "sha256")}:
        raise ValueError("bound evidence identity mismatch")
    return path


def load_bound_ocr_reviews(run_root: Path, ledger_path: Path, *, authority_validator=None):
    for path in (run_root, ledger_path):
        assert_existing_path_components_are_not_reparse(path)
    run_root, ledger_path = run_root.resolve(strict=True), ledger_path.resolve(strict=True)
    stage = mechanical._verify_stage04(run_root, authority_validator)
    ledger = _read(ledger_path)
    fields = {"schema", "state", "source", "metadata", "run_root", "page_count", "pages", "corrections", "evidence", "reconstruction_accepted", "ledger_sha256"}
    if (set(ledger) != fields or ledger["schema"] != SCHEMA
            or ledger["state"] != "bound_reviewed_corrections_candidate_only"
            or ledger["reconstruction_accepted"] is not False
            or ledger["ledger_sha256"] != mechanical._sha(mechanical._canonical({k: v for k, v in ledger.items() if k != "ledger_sha256"}))):
        raise ValueError("bound OCR ledger seal/contract mismatch")
    run = _read(run_root / "run.json")
    count = run["source"]["page_count"]
    if ledger["run_root"] != str(run_root) or ledger["source"] != run["source"] or ledger["page_count"] != count:
        raise ValueError("bound OCR ledger run/source mismatch")
    pages = _pages(ledger["pages"], "source_page", count)
    evidence = ledger["evidence"]
    if not isinstance(evidence, dict) or not {"coverage.json", "source-review.json"} <= set(evidence):
        raise ValueError("bound review evidence inventory incomplete")
    paths = {name: _file(ledger_path.parent, {"path": name, **identity}) for name, identity in evidence.items()}
    coverage, source_review = (_read(paths[name]) for name in ("coverage.json", "source-review.json"))
    metadata_path = _file(run_root, ledger["metadata"])
    if not metadata_path.is_relative_to(run_root / "outputs/02-mineru-three-view/views" / VIEW):
        raise ValueError("metadata belongs to a different view")
    metadata = _read(metadata_path)
    if (not isinstance(metadata, list) or coverage.get("metadata_sha256") != ledger["metadata"]["sha256"]
            or coverage.get("source_sha256") != run["source"]["sha256"] or coverage.get("page_count") != count
            or source_review.get("schema") != "kb_creator.source_review_coverage.v1"
            or source_review.get("source", {}).get("sha256") != run["source"]["sha256"]
            or source_review["source"].get("pages") != count):
        raise ValueError("review coverage/source/metadata mismatch")
    covered = _pages(coverage.get("pages"), "source_page", count)
    visuals = _pages(source_review.get("pages"), "page", count)
    packets = {number: (path, value) for number, path, value in mechanical._load_packets(stage)}
    if set(packets) != set(covered):
        raise ValueError("bound review packet page coverage mismatch")
    expected, reports = {}, {}
    selected_reports = set()
    for number in range(1, count + 1):
        item = covered[number]
        name = "reports/" + Path(item["report"]).name
        selected_reports.add(name)
        if name not in paths or evidence[name]["sha256"] != item.get("report_sha256"):
            raise ValueError("coverage report identity mismatch")
        report = reports.setdefault(name, _read(paths[name]))
        if report.get("schema") not in {"kb_creator.preliminary_ocr_visual_review.v1", "kb_creator.preliminary_ocr_visual_review.v2"}:
            raise ValueError("unsupported reviewed report schema")
        ocr_view = report.get("ocr_view", {})
        if (report.get("view", ocr_view.get("name")) != VIEW
                or report.get("metadata_sha256", ocr_view.get("source_content_list_sha256")) != ledger["metadata"]["sha256"]
                or "source" in report and report["source"].get("sha256") != run["source"]["sha256"]):
            raise ValueError("report view/metadata binding mismatch")
        report_pages = [row for row in report.get("pages", []) if row.get("source_page") == number]
        if len(report_pages) != 1:
            raise ValueError("report page binding ambiguous")
        page = report_pages[0]
        visual_sha = visuals[number]["sha256"]
        if page.get("visual_sha256") != visual_sha or item.get("visual_sha256") != visual_sha or pages[number].get("source_render", {}).get("sha256") != visual_sha:
            raise ValueError("report source-render binding mismatch")
        for correction in page.get("ocr_corrections", []):
            key = (number, VIEW, correction.get("raw_index"))
            if key in expected:
                raise ValueError("duplicate reviewed correction")
            expected[key] = (correction, name, visual_sha)
    if set(paths) != selected_reports | {"coverage.json", "source-review.json"}:
        raise ValueError("unselected evidence file in bound ledger")
    rows = ledger["corrections"]
    if not isinstance(rows, list) or len(rows) != coverage.get("exact_full_block_corrections") or len(rows) != len(expected):
        raise ValueError("ledger correction coverage incomplete")
    result = {}
    for row in rows:
        required = {"source_page", "view", "raw_index", "before", "after", "reason", "before_sha256", "after_sha256", "packet", "report", "source_render"}
        if not isinstance(row, dict) or set(row) != required or type(row["source_page"]) is not int or type(row["raw_index"]) is not int:
            raise ValueError("bound correction contract invalid")
        key = (row["source_page"], row["view"], row["raw_index"])
        if key in result or key not in expected:
            raise ValueError("duplicate or foreign correction selector")
        correction, report_name, visual_sha = expected[key]
        if {k: row[k] for k in ("raw_index", "before", "after", "reason")} != correction:
            raise ValueError("ledger correction differs from reviewed report")
        if (not all(isinstance(row[k], str) and row[k].strip() for k in ("before", "after", "reason"))
                or row["before"] == row["after"] or mechanical._c0(row["after"])
                or row["before_sha256"] != mechanical._sha(row["before"].encode())
                or row["after_sha256"] != mechanical._sha(row["after"].encode())):
            raise ValueError("bound correction text/hash mismatch")
        packet_path, packet = packets[key[0]]
        if _file(run_root, row["packet"]) != packet_path.resolve():
            raise ValueError("correction packet selector mismatch")
        blocks = [b for b in packet["views"][VIEW]["blocks"] if b.get("raw_index") == key[2]]
        if (len(blocks) != 1 or blocks[0].get("text") != row["before"] or not 0 <= key[2] < len(metadata)
                or metadata[key[2]].get("text") != row["before"] or metadata[key[2]].get("page_idx") != key[0] - 1):
            raise ValueError("correction raw packet/metadata preimage mismatch")
        if row["report"] != {"path": report_name, **evidence[report_name]}:
            raise ValueError("correction report reference mismatch")
        render = row["source_render"]
        if not isinstance(render, dict) or set(render) != {"path", "bytes", "sha256"}:
            raise ValueError("source-render reference invalid")
        render_path = Path(render["path"])
        assert_existing_path_components_are_not_reparse(render_path)
        if (not render_path.is_absolute() or not render_path.is_file()
                or render["sha256"] != visual_sha or render_path.name != Path(visuals[key[0]]["render"]).name
                or file_identity(render_path) != {k: render[k] for k in ("bytes", "sha256")}):
            raise ValueError("source-render evidence mismatch")
        result[key] = row
    if set(result) != set(expected):
        raise ValueError("report correction omitted from ledger")
    return ledger, result
