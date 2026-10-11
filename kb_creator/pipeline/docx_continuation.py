"""Immutable DOCX continuation and explicit full-artifact review evidence."""
from __future__ import annotations

import json
import shutil
from pathlib import Path
from typing import Any

from . import (docx_text_review, five_step, five_step_docx, language_continuation,
               reader_projection, source_issue_projection)
from .identity import assert_existing_path_components_are_not_reparse, deterministic_inventory, file_identity
from .manifests import sealed, validate_seal

SCHEMA = "kb_creator.docx_continuation.v1"
REVIEW_SCHEMA = "kb_creator.docx_continuation_review_result.v1"
MANIFEST = "CONTINUATION.json"
REVIEW = "REVIEW_RESULT.json"
_read = language_continuation._read
_write = language_continuation._write
_reference = language_continuation._reference
_check_reference = language_continuation._check_reference


def _codes() -> list[dict]:
    rows = {row["path"]: row for row in five_step._codes(5)}
    for name in ("pipeline/docx_continuation.py", "scripts/continue_docx.py"):
        path = five_step.ROOT / "kb_creator" / name
        relative = path.relative_to(five_step.ROOT).as_posix()
        rows[relative] = {"path": relative, **file_identity(path)}
    return [rows[key] for key in sorted(rows)]


def _inventory(root: Path, marker: str) -> list[dict]:
    return [row for row in deterministic_inventory(root) if row["path"] != marker]


def _language(reference: dict) -> tuple[dict, Path]:
    path = _check_reference(reference)
    if path.name != language_continuation.MANIFEST:
        raise ValueError("language continuation manifest required")
    result = language_continuation.verify_continuation(path.parent)
    if result["phase"] != "language_complete":
        raise ValueError("DOCX requires language_complete")
    return result, Path(result["final_root"]) / "MASTER_RU.md"


def _visual_task(package: Path) -> dict | None:
    manifest = _read(package / five_step_docx.MANIFEST)
    if manifest["state"] == "built_pending_render":
        if manifest["render"] is not None or (package / "render").exists():
            raise ValueError("pending render has contradictory evidence")
        return None
    index = _read(package / "render/review_index.json")
    inventory = _read(package / "render/render_inventory.json")
    count = index["page_count"]
    if (type(count) is not int or count < 1 or count != inventory["page_count"]
            or len(index["pages"]) != count or len(inventory["pages"]) != count
            or not isinstance(manifest["render"], dict) or manifest["render"].get("page_count") != count):
        raise ValueError("render page count mismatch")
    rows = []
    for number, (row, detailed) in enumerate(zip(index["pages"], inventory["pages"]), 1):
        name = f"page-{number:03d}.png"
        path = package / "render" / name
        expected = {"path": name, **file_identity(path)}
        if row["page"] != number or detailed["page"] != number or row["image"] != expected or detailed["image"] != expected:
            raise ValueError("render page identity/order mismatch")
        rows.append({"path": "package/render/" + name, "identity": file_identity(path)})
    if {p.name for p in (package / "render").glob("*.png")} != {Path(row["path"]).name for row in rows}:
        raise ValueError("render PNG coverage mismatch")
    docx = package / "docx/document.docx"
    return sealed("kb_creator.docx_visual_review_task.v1", {
        "docx": {"path": "package/docx/document.docx", **file_identity(docx)}, "pages": rows,
    }, digest_key="task_sha256")


def build_docx_continuation(language_root: Path, output_root: Path, *, title: str,
                            reader_options: Path, config: Path | None = None,
                            runtime: dict[str, Any] | None = None,
                            fidelity_plan: Path | None = None) -> dict:
    if fidelity_plan is None:
        raise ValueError("source-fidelity plan is required before DOCX continuation")
    parent = _reference(Path(language_root) / language_continuation.MANIFEST)
    language, master = _language(parent)
    if config is None:
        raise ValueError("guarded DOCX continuation requires an explicit config")
    from .reader_fidelity import validate_plan
    plan = validate_plan(fidelity_plan, master_ru=master)
    if (Path(plan["source_pdf"]["path"]).resolve() != Path(language["inputs"]["source_pdf"]["path"]).resolve()
            or plan["source_pdf"]["sha256"] != language["inputs"]["source_pdf"]["identity"]["sha256"]
            or plan["source_pdf"]["bytes"] != language["inputs"]["source_pdf"]["identity"]["bytes"]):
        raise ValueError("DOCX continuation source PDF differs from reviewed fidelity plan")
    if plan["config"] != {"path": str(config.resolve(strict=True)), **file_identity(config)}:
        raise ValueError("DOCX continuation config differs from fidelity plan")
    options_ref = _reference(reader_options)
    options = reader_projection.load_options(reader_options, master, master.parent / "semantic_context/RU_PROJECTION.json")
    if options["source_toc"]["source_pdf_sha256"] != language["inputs"]["source_pdf"]["identity"]["sha256"]:
        raise ValueError("reader options source PDF mismatch")
    config_ref = _reference(config)
    predecessor = language_continuation._predecessor_reference(language["inputs"])
    protected = [Path(language_root), Path(predecessor["path"]).parent,
                 Path(reader_options).parent]
    if config:
        protected.append(Path(config).parent)
    root = language_continuation._new_root(output_root, protected)
    try:
        issue_projection = None
        if language["inputs"].get("predecessor_kind") == "verified_review_draft":
            inputs = language["inputs"]
            required = {"master_en", "issue_en_bindings", "final_evidence"}
            if not required.issubset(inputs):
                raise ValueError("verified review-draft DOCX route lacks source issue authority")
            issue_projection = source_issue_projection.derive_source_issue_projection(
                master_en=Path(inputs["master_en"]["path"]), master_ru=master,
                ru_projection=master.parent / "semantic_context" / "RU_PROJECTION.json",
                issue_en_bindings=Path(inputs["issue_en_bindings"]["path"]),
                final_evidence=Path(inputs["final_evidence"]["path"]),
                language_task=Path(language["language_root"]) / "draft.task.json",
            )
        five_step_docx.build_docx_package(master, root / "package", title=title,
                                        config=config, runtime=runtime, reader_options=reader_options,
                                        source_issue_projection=issue_projection, fidelity_plan=fidelity_plan)
        five_step_docx.verify_docx_package(root / "package")
        if file_identity(root / "package/reader_options.json") != file_identity(reader_options):
            # The builder normalizes JSON formatting; compare parsed decisions.
            if _read(root / "package/reader_options.json") != options:
                raise ValueError("reader decisions changed during build")
        if config:
            shutil.copyfile(config, root / "source-config.json")
        _write(root / "text-review-task.json", docx_text_review.prepare_docx_text_review(root / "package/docx/document.docx"))
        visual = _visual_task(root / "package")
        if visual:
            _write(root / "visual-review-task.json", visual)
        body = {"state": "visual_review_task_ready" if visual else "pending_render",
                "language": parent, "inputs": language["inputs"], "reader_options": options_ref,
                "config": config_ref, "code": _codes(), "book_acceptance": "pending",
                "files": _inventory(root, MANIFEST)}
        _write(root / MANIFEST, sealed(SCHEMA, body, digest_key="continuation_sha256"))
        return verify_docx_continuation(root)
    except Exception as error:
        if (root / MANIFEST).exists():
            (root / MANIFEST).rename(root / "REJECTED_CONTINUATION.json")
        _write(root / "FAILED.json", {"usable": False, "error": str(error)})
        raise


def verify_docx_continuation(root: Path) -> dict:
    root = Path(root)
    assert_existing_path_components_are_not_reparse(root)
    value = _read(root / MANIFEST)
    validate_seal(value, "continuation_sha256")
    if value.get("schema") != SCHEMA or value.get("state") not in {"pending_render", "visual_review_task_ready"}:
        raise ValueError("unsupported DOCX continuation")
    if value["code"] != _codes() or value["files"] != _inventory(root, MANIFEST):
        raise ValueError("DOCX continuation code/inventory mismatch")
    language, master = _language(value["language"])
    if language["inputs"] != value["inputs"] or value["book_acceptance"] != "pending":
        raise ValueError("DOCX input lineage mismatch")
    options_path = _check_reference(value["reader_options"])
    options = reader_projection.load_options(options_path, master, master.parent / "semantic_context/RU_PROJECTION.json")
    if options != _read(root / "package/reader_options.json") or options["source_toc"]["source_pdf_sha256"] != language["inputs"]["source_pdf"]["identity"]["sha256"]:
        raise ValueError("reader options lineage mismatch")
    if value["config"]:
        config = _check_reference(value["config"])
        if file_identity(config) != file_identity(root / "source-config.json"):
            raise ValueError("source config mismatch")
    five_step_docx.verify_docx_package(root / "package")
    if file_identity(master) != file_identity(root / "package/MASTER_RU.md"):
        raise ValueError("DOCX MASTER_RU binding mismatch")
    task = docx_text_review.prepare_docx_text_review(root / "package/docx/document.docx")
    if task != _read(root / "text-review-task.json"):
        raise ValueError("DOCX text task mismatch")
    visual = _visual_task(root / "package")
    if visual is None:
        if value["state"] != "pending_render" or (root / "visual-review-task.json").exists():
            raise ValueError("render state mismatch")
    elif value["state"] != "visual_review_task_ready" or visual != _read(root / "visual-review-task.json"):
        raise ValueError("visual task mismatch")
    return value


def _validate_reviews(root: Path, text: dict, visual: dict) -> dict:
    task = _read(root / "text-review-task.json")
    record = docx_text_review.validate_docx_text_review(task, text)
    expected = _read(root / "visual-review-task.json")
    if (set(visual) != {"schema", "task_sha256", "docx", "reviewer_role", "pages", "findings"}
            or visual["schema"] != "kb_creator.docx_visual_review_submission.v1"
            or visual["task_sha256"] != expected["task_sha256"] or visual["docx"] != expected["docx"]
            or visual["reviewer_role"] != "agent" or visual["findings"] != []
            or not isinstance(visual["pages"], list) or len(visual["pages"]) != len(expected["pages"])):
        raise ValueError("stale, incomplete or unresolved visual review")
    for want, row in zip(expected["pages"], visual["pages"]):
        if row != {**want, "read": True} or row.get("read") is not True:
            raise ValueError("visual review page identity/order/read mismatch")
    return record


def submit_docx_reviews(root: Path, output_root: Path, *, text_submission: Path, visual_submission: Path) -> dict:
    root = Path(root)
    envelope = verify_docx_continuation(root)
    if envelope["state"] != "visual_review_task_ready":
        raise ValueError("rendered visual review required")
    text, visual = _read(text_submission), _read(visual_submission)
    record = _validate_reviews(root, text, visual)
    destination = language_continuation._new_root(output_root, [root, Path(text_submission).parent, Path(visual_submission).parent])
    try:
        _write(destination / "text-submission.json", text)
        _write(destination / "visual-submission.json", visual)
        body = {"state": "ready_for_independent_release", "continuation": _reference(root / MANIFEST),
                "text_review": record, "book_acceptance": "pending", "code": _codes(),
                "files": _inventory(destination, REVIEW)}
        _write(destination / REVIEW, sealed(REVIEW_SCHEMA, body, digest_key="review_sha256"))
        return verify_docx_review(destination)
    except Exception as error:
        if (destination / REVIEW).exists():
            (destination / REVIEW).rename(destination / "REJECTED_REVIEW.json")
        _write(destination / "FAILED.json", {"usable": False, "error": str(error)})
        raise


def verify_docx_review(root: Path) -> dict:
    root = Path(root)
    assert_existing_path_components_are_not_reparse(root)
    value = _read(root / REVIEW)
    validate_seal(value, "review_sha256")
    if value.get("schema") != REVIEW_SCHEMA or value.get("state") != "ready_for_independent_release" or value.get("book_acceptance") != "pending":
        raise ValueError("unsupported DOCX review result")
    if value["files"] != _inventory(root, REVIEW) or value["code"] != _codes():
        raise ValueError("DOCX review code/inventory mismatch")
    parent = _check_reference(value["continuation"]).parent
    if verify_docx_continuation(parent)["state"] != "visual_review_task_ready":
        raise ValueError("rendered review parent required")
    record = _validate_reviews(parent, _read(root / "text-submission.json"), _read(root / "visual-submission.json"))
    if record != value["text_review"]:
        raise ValueError("text review record mismatch")
    return value
