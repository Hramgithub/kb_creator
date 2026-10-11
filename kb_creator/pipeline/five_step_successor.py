"""Versioned correction successor for a completed five-step run.

The route deliberately reuses only the sealed language authority.  It never
modifies the predecessor state or attempts to make historical implementation
hashes describe current code.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

from .identity import deterministic_inventory, file_identity, implementation_inventory
from .manifests import sealed, validate_seal


SCHEMA = "kb_creator.five_step_successor.v1"


class FiveStepSuccessorError(ValueError):
    pass


def _json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8-sig"))
    except (OSError, json.JSONDecodeError) as error:
        raise FiveStepSuccessorError(f"invalid JSON: {path}") from error
    if not isinstance(value, dict):
        raise FiveStepSuccessorError(f"JSON object required: {path}")
    return value


def _write(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(value, ensure_ascii=False, indent=2, default=str) + "\n", encoding="utf-8", newline="\n")
    os.replace(temporary, path)


def _save(root: Path, state: dict[str, Any]) -> None:
    unsigned = {key: value for key, value in state.items() if key != "state_sha256"}
    _write(root / "state.json", sealed(SCHEMA, unsigned, digest_key="state_sha256"))


def _identity(path: Path, root: Path) -> dict[str, Any]:
    path = path.resolve(strict=True)
    try:
        relative = path.relative_to(root.resolve())
    except ValueError as error:
        raise FiveStepSuccessorError(f"artifact escapes root: {path}") from error
    return {"path": relative.as_posix(), **file_identity(path)}


def _resolve(root: Path, identity: object, label: str) -> Path:
    if not isinstance(identity, dict) or set(identity) != {"path", "bytes", "sha256"}:
        raise FiveStepSuccessorError(f"invalid {label} identity")
    path = (root / str(identity["path"])).resolve()
    try:
        path.relative_to(root.resolve())
    except ValueError as error:
        raise FiveStepSuccessorError(f"{label} escapes successor") from error
    if not path.is_file() or file_identity(path) != {key: identity[key] for key in ("bytes", "sha256")}:
        raise FiveStepSuccessorError(f"{label} identity mismatch")
    return path


def _verify_predecessor(root: Path) -> dict[str, Any]:
    state = _json(root / "state.json")
    try:
        validate_seal(state, "state_sha256")
    except ValueError as error:
        raise FiveStepSuccessorError(f"predecessor state seal: {error}") from error
    if state.get("schema") not in {"kb_creator.five_step_run.v1", "kb_creator.five_step_run.v2"}:
        raise FiveStepSuccessorError("unsupported predecessor state")
    for key in ("source", "glossary"):
        record = state.get(key)
        if not isinstance(record, dict) or not isinstance(record.get("path"), str) or not isinstance(record.get("identity"), dict):
            raise FiveStepSuccessorError(f"predecessor {key} authority is missing")
        path = Path(record["path"]).resolve()
        if not path.is_file() or file_identity(path) != record["identity"]:
            raise FiveStepSuccessorError(f"predecessor {key} identity mismatch")
    evidence_by_root: dict[str, list[dict[str, Any]]] = {}
    for record in state.get("evidence", []):
        if not isinstance(record, dict) or not isinstance(record.get("root"), str) or not isinstance(record.get("files"), list):
            raise FiveStepSuccessorError("predecessor evidence is malformed")
        evidence_root = (root / record["root"]).resolve()
        if not evidence_root.is_dir() or not evidence_root.is_relative_to(root):
            raise FiveStepSuccessorError("predecessor evidence root escapes run")
        actual = {item["path"]: item for item in deterministic_inventory(evidence_root)}
        for item in record["files"]:
            observed = actual.get(item.get("path"))
            if observed != item:
                raise FiveStepSuccessorError(f"predecessor evidence inventory mismatch: {record['root']}")
        evidence_by_root.setdefault(record["root"], []).append(record)
    # A run can record a growing reconstruction root more than once.  Each
    # historical snapshot must still match, while the largest snapshot closes
    # the root against unrecorded additions.
    for relative, records in evidence_by_root.items():
        latest = max(records, key=lambda record: len(record["files"]))
        evidence_root = (root / relative).resolve(strict=True)
        if deterministic_inventory(evidence_root) != latest["files"]:
            raise FiveStepSuccessorError(f"predecessor evidence inventory mismatch: {relative}")
    paths = state.get("paths")
    if not isinstance(paths, dict):
        raise FiveStepSuccessorError("predecessor paths are missing")
    for key in ("language", "draft", "final"):
        path = Path(str(paths.get(key, ""))).resolve()
        if not path.is_dir() or not path.is_relative_to(root):
            raise FiveStepSuccessorError(f"predecessor {key} root is missing or escapes run")
    from .five_step_language import verify_language_result
    try:
        verify_language_result(Path(paths["final"]))
    except Exception as error:
        raise FiveStepSuccessorError(f"predecessor language authority failed: {error}") from error
    return state


def _code_snapshot() -> dict[str, Any]:
    repo = Path(__file__).resolve().parents[2]
    paths = [
        Path(__file__), repo / "kb_creator/pipeline/five_step_language.py",
        repo / "kb_creator/pipeline/language_context.py", repo / "kb_creator/pipeline/language_numeric.py",
        repo / "kb_creator/pipeline/five_step_docx.py", repo / "kb_creator/pipeline/reader_projection.py",
        repo / "kb_creator/pipeline/reader_block_relocation.py",
        repo / "kb_creator/scripts/production_docx.py", repo / "translator/translator.py",
    ]
    return implementation_inventory(repo, paths)


def _state(root: Path) -> dict[str, Any]:
    state = _json(root / "state.json")
    try:
        validate_seal(state, "state_sha256")
    except ValueError as error:
        raise FiveStepSuccessorError(f"successor state seal: {error}") from error
    if state.get("schema") != SCHEMA:
        raise FiveStepSuccessorError("unsupported successor state")
    return state


def _record_output(root: Path, state: dict[str, Any], key: str, directory: Path) -> None:
    state.setdefault("outputs", {})[key] = {"root": directory.relative_to(root).as_posix(), "inventory": deterministic_inventory(directory)}


def _bound_reflow_submission(predecessor_final: Path, submission: Path, target: Path) -> Path:
    """Bind only content-conserving prose reflows to the sealed predecessor final."""
    previous = _json(predecessor_final / "evidence" / "proofread.submission.json")
    supplied = _json(submission)
    old_rows = {row.get("unit_id"): row for row in previous.get("units", []) if isinstance(row, dict)}
    rows = []
    authority = []
    for row in supplied.get("units", []):
        copied = dict(row)
        old = old_rows.get(copied.get("unit_id"))
        reason = str(copied.get("reason") or "").lower()
        if isinstance(old, dict) and any(token in reason for token in ("reflow", "перенос")):
            old_text = old.get("final_ru_text")
            new_text = copied.get("final_ru_text")
            if isinstance(old_text, str) and isinstance(new_text, str) and " ".join(old_text.split()) == " ".join(new_text.split()):
                authority.append({"unit_id": copied["unit_id"]})
        rows.append(copied)
    bound = {key: value for key, value in supplied.items() if key != "submission_sha256"}
    bound.update(units=rows, reflow_authority={"schema": "kb_creator.five_step_reflow_authority.v1", "predecessor_submission": previous, "rows": authority})
    bound = sealed("kb_creator.five_step_language_proofread_submission.v2", bound, digest_key="submission_sha256")
    path = target / "proofread-submission.bound.json"
    _write(path, bound)
    _write(target / "reflow-authority.json", bound["reflow_authority"])
    return path


def successor_prepare(from_run: Path, run_root: Path, proofread_submission: Path) -> dict[str, Any]:
    """Create a fresh verified final from a complete correction submission."""
    predecessor = from_run.resolve(strict=True)
    target = run_root.resolve()
    submission = proofread_submission.resolve()
    if target.exists() or not target.parent.is_dir() or not submission.is_file():
        raise FiveStepSuccessorError("successor root must be absent below an existing parent and submission must be a file")
    old = _verify_predecessor(predecessor)
    language, draft = (Path(old["paths"][key]).resolve(strict=True) for key in ("language", "draft"))
    target.mkdir()
    state = {
        "profile": "five_step_successor_v1", "phase": "prepare", "state": "running",
        "predecessor": {"root": str(predecessor), "state": {"bytes": (predecessor / "state.json").stat().st_size, "sha256": file_identity(predecessor / "state.json")["sha256"]}, "source": old["source"], "glossary": old["glossary"], "historical_code": [row.get("code", []) for row in old.get("evidence", [])]},
        "current_code": _code_snapshot(), "proofread_submission": {"path": str(submission), "identity": file_identity(submission)}, "outputs": {}, "title": old.get("title", "Successor"),
    }
    _save(target, state)
    try:
        from .five_step_language import submit_proofread, verify_language_result
        final = target / "final-001"
        bound_submission = _bound_reflow_submission(Path(old["paths"]["final"]), submission, target)
        result = submit_proofread(language, draft, bound_submission, final)
        verify_language_result(final)
        _record_output(target, state, "final", final)
        state.update(phase="reader_options", state="needs_reader_options", master_ru=_identity(result["master_ru"], target), reason=None)
    except Exception as error:
        state.update(state="failed", reason=f"{type(error).__name__}: {error}")
    _save(target, state)
    return status(target)


def _reader_options(final: Path, options: Path) -> dict[str, Any]:
    value = _json(options)
    allowed = {"schema", "master_ru", "ru_projection", "source_toc", "body_links", "asset_choices", "hit_points", "display_roles", "options_sha256"}
    if set(value) != allowed or value.get("schema") != "kb_creator.five_step_reader_options.v1":
        raise FiveStepSuccessorError("unsupported reader options")
    try:
        validate_seal(value, "options_sha256")
    except ValueError as error:
        raise FiveStepSuccessorError(f"reader options seal: {error}") from error
    for key, path in (("master_ru", final / "MASTER_RU.md"), ("ru_projection", final / "semantic_context" / "RU_PROJECTION.json")):
        expected = {"path": path.relative_to(final).as_posix(), **file_identity(path)}
        if value.get(key) != expected:
            raise FiveStepSuccessorError(f"reader options {key} does not bind successor final")
    return value


def successor_build(run_root: Path, reader_options: Path, docx_config: Path, runtime: dict[str, Any] | None,
                    fidelity_plan: Path | None = None) -> dict[str, Any]:
    if fidelity_plan is None:
        raise FiveStepSuccessorError("source-fidelity plan is required before DOCX successor build")
    root = run_root.resolve(strict=True)
    state = _state(root)
    final_record = state.get("outputs", {}).get("final")
    retry = state.get("state") == "failed" and state.get("phase") == "reader_options" and final_record and not state.get("active_docx")
    if state.get("state") not in {"needs_reader_options", "needs_visual_review", "ready_for_docx_review"} and not retry:
        raise FiveStepSuccessorError("successor is not ready for reader options")
    final = root / final_record["root"]
    from .five_step_language import verify_language_result
    verify_language_result(final)
    from .reader_fidelity import validate_plan
    plan = validate_plan(fidelity_plan, master_ru=final / "MASTER_RU.md")
    if (Path(plan["source_pdf"]["path"]).resolve() != Path(state["predecessor"]["source"]["path"]).resolve()
            or plan["source_pdf"]["sha256"] != state["predecessor"]["source"]["identity"]["sha256"]
            or plan["source_pdf"]["bytes"] != state["predecessor"]["source"]["identity"]["bytes"]):
        raise FiveStepSuccessorError("successor source PDF differs from reviewed fidelity plan")
    if plan["config"] != {"path": str(docx_config.resolve(strict=True)), **file_identity(docx_config)}:
        raise FiveStepSuccessorError("successor DOCX config differs from fidelity plan")
    _reader_options(final, reader_options.resolve(strict=True))
    if not docx_config.resolve(strict=True).is_file():
        raise FiveStepSuccessorError("DOCX config is missing")
    attempts = [int(path.name.split("-", 1)[1]) for path in root.glob("docx-*") if path.is_dir() and path.name[5:].isdigit()]
    output = root / f"docx-{(max(attempts) + 1) if attempts else 1:03}"
    try:
        from .five_step_docx import build_docx_package, verify_docx_package
        result = build_docx_package(final, output, title=state["title"], config=docx_config.resolve(), runtime=(runtime or {}).get("docx"), reader_options=reader_options.resolve(), fidelity_plan=fidelity_plan)
        verify_docx_package(output)
        _record_output(root, state, output.name, output)
        state.update(phase="visual_review", state="needs_visual_review", build_code=_code_snapshot(), reader_options={"path": str(reader_options.resolve()), "identity": file_identity(reader_options.resolve())}, docx_config={"path": str(docx_config.resolve()), "identity": file_identity(docx_config.resolve())}, active_docx=output.name, reason=None)
        _write_visual_task(root, state, result)
    except Exception as error:
        state.update(state="failed", reason=f"{type(error).__name__}: {error}")
    _save(root, state)
    return status(root)


def _write_visual_task(root: Path, state: dict[str, Any], result: dict[str, Any]) -> None:
    package = root / state["active_docx"]
    pages = result.get("render_pages") or []
    if not pages:
        raise FiveStepSuccessorError("DOCX was not rendered; no visual review can be requested")
    records = []
    for index, item in enumerate(pages, 1):
        path = Path(item).resolve(strict=True)
        if not path.is_relative_to(package):
            raise FiveStepSuccessorError("render page escapes DOCX package")
        records.append({"page": index, "path": path.relative_to(package).as_posix(), **file_identity(path)})
    task = sealed("kb_creator.five_step_visual_task.v1", {"kind": "docx_visual", "docx": _identity(Path(result["docx_path"]), root), "pages": records, "instructions": "Inspect every rendered page; report resolved findings and no unresolved findings."}, digest_key="task_sha256")
    attempts = [int(path.name.split("-", 2)[2]) for path in root.glob("visual-task-*") if path.is_dir() and path.name[12:].isdigit()]
    task_root = root / f"visual-task-{(max(attempts) + 1) if attempts else 1:03}"
    task_root.mkdir()
    _write(task_root / "task.json", task)
    _write(task_root / "submission.template.json", {"schema": "kb_creator.five_step_visual_submission.v1", "task_sha256": task["task_sha256"], "reviewer_role": "agent", "pages": [{"page": row["page"], "reviewed": False, "findings": []} for row in records], "unresolved": []})
    _record_output(root, state, task_root.name, task_root)
    state["visual_task"] = _identity(task_root / "task.json", root)


def successor_review(run_root: Path, submission: Path) -> dict[str, Any]:
    root = run_root.resolve(strict=True)
    state = _state(root)
    if state.get("state") != "needs_visual_review":
        raise FiveStepSuccessorError("successor is not awaiting visual review")
    task = _json(_resolve(root, state.get("visual_task"), "visual task"))
    value = _json(submission.resolve(strict=True))
    expected = [{"page": row["page"], "reviewed": True, "findings": []} for row in task["pages"]]
    if set(value) != {"schema", "task_sha256", "reviewer_role", "pages", "unresolved"} or value.get("schema") != "kb_creator.five_step_visual_submission.v1" or value.get("task_sha256") != task["task_sha256"] or value.get("reviewer_role") not in {"agent", "user"} or value.get("unresolved") != [] or value.get("pages") != expected:
        raise FiveStepSuccessorError("all rendered pages require explicit clean visual review")
    from .five_step_docx import verify_docx_package
    verify_docx_package(root / state["active_docx"])
    attempts = [int(path.name.rsplit("-", 1)[1]) for path in root.glob("visual-review-*") if path.is_dir() and path.name.rsplit("-", 1)[1].isdigit()]
    review = root / f"visual-review-{max(attempts) + 1 if attempts else 1:03}"
    review.mkdir(); _write(review / "review.json", value); _record_output(root, state, review.name, review)
    state.update(phase="complete", state="ready_for_docx_review", reason=None)
    _save(root, state)
    return status(root)


def status(run_root: Path) -> dict[str, Any]:
    root = run_root.resolve(strict=True)
    state = _state(root)
    for record in state.get("outputs", {}).values():
        directory = root / record["root"]
        if not directory.is_dir() or deterministic_inventory(directory) != record["inventory"]:
            raise FiveStepSuccessorError(f"successor output inventory mismatch: {record.get('root')}")
    return {"schema": SCHEMA, "run_root": str(root), "state": state["state"], "phase": state["phase"], "reason": state.get("reason"), "active_docx": state.get("active_docx"), "visual_task": state.get("visual_task"), "exit_code": 2 if state["state"] == "failed" else 0}


def verify_successor(run_root: Path) -> dict[str, Any]:
    result = status(run_root)
    root = Path(result["run_root"])
    state = _state(root)
    final = state.get("outputs", {}).get("final")
    if final:
        from .five_step_language import verify_language_result
        verify_language_result(root / final["root"])
    if state.get("active_docx"):
        from .five_step_docx import verify_docx_package
        verify_docx_package(root / state["active_docx"])
    for key in ("reader_options", "docx_config"):
        record = state.get(key)
        if record and (not Path(record["path"]).is_file() or file_identity(Path(record["path"])) != record["identity"]):
            raise FiveStepSuccessorError(f"external {key} identity mismatch")
    return {**result, "verification": "verified", "current_code": state["current_code"], "historical_code": state["predecessor"]["historical_code"]}
