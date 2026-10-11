"""Resume language work from verified MASTER_EN without replaying extraction."""

from __future__ import annotations

import json
import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from . import five_step, five_step_intake, five_step_language
from .identity import (assert_existing_path_components_are_not_reparse,
                       deterministic_inventory, file_identity)
from .manifests import sealed, validate_seal

SCHEMA = "kb_creator.language_continuation.v1"
MANIFEST = "CONTINUATION.json"


class LanguageContinuationError(ValueError):
    pass


@dataclass(frozen=True)
class _VerificationContext:
    """MASTER_EN authority verified once for one public continuation check."""

    inputs: dict[str, Any]
    master: Path
    predecessor_root: Path


def _read(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(value, dict):
        raise LanguageContinuationError(f"object required: {path}")
    return value


def _write(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _reference(path: Path) -> dict[str, Any]:
    return {"path": str(path.resolve(strict=True)), "identity": file_identity(path)}


def _check_reference(record: dict[str, Any]) -> Path:
    path = Path(record["path"])
    assert_existing_path_components_are_not_reparse(path)
    if not path.is_file() or file_identity(path) != record["identity"]:
        raise LanguageContinuationError(f"changed input: {path}")
    return path.resolve(strict=True)


def _codes() -> list[dict[str, Any]]:
    rows = {row["path"]: row for step in (3, 4) for row in five_step._codes(step)}
    for name in ("pipeline/language_continuation.py", "scripts/continue_language.py", "pipeline/coc_glossary.py"):
        path = five_step.ROOT / "kb_creator" / name
        relative = path.relative_to(five_step.ROOT).as_posix()
        rows[relative] = {"path": relative, **file_identity(path)}
    return [rows[key] for key in sorted(rows)]


def _verified_master(run_root: Path, *, review_binding_root: Path | None = None) -> tuple[dict[str, Any], Path]:
    """Reuse Step 2 only; historical language code may legitimately have changed."""
    assert_existing_path_components_are_not_reparse(run_root)
    run_root = run_root.resolve(strict=True)
    review_manifest = run_root / "MANIFEST.json"
    if review_manifest.is_file():
        manifest = _read(review_manifest)
        if manifest.get("schema") == "kb_creator.review_master_en_manifest.v1":
            v2_bindings = run_root / "ISSUE_EN_BINDINGS.v2.json"
            if v2_bindings.is_file() and review_binding_root is None:
                raise LanguageContinuationError("review MASTER_EN v2 requires an explicit review binding root")
            try:
                five_step_intake.verify_master_en(run_root, binding_root=review_binding_root)
            except ValueError as error:
                raise LanguageContinuationError(f"invalid review MASTER_EN: {error}") from error
            evidence_record = manifest["final_evidence"]
            evidence_path = Path(evidence_record["path"])
            if file_identity(evidence_path) != {key: evidence_record[key] for key in ("bytes", "sha256")}:
                raise LanguageContinuationError("review MASTER_EN final evidence identity drift")
            evidence = _read(evidence_path)
            blocking_issues = [
                issue["issue_id"] for issue in evidence["source_issues"]["issues"]
                if issue["kind"] in {"translation_source_choice_pending", "source_material_blocked"}
            ]
            if blocking_issues:
                raise LanguageContinuationError(
                    "resolve source choices or missing source material before language preparation: "
                    + ", ".join(blocking_issues)
                )
            provenance = _read(run_root / "MASTER_EN.provenance.json")
            source = provenance.get("source")
            if not isinstance(source, dict) or not isinstance(source.get("path"), str):
                raise LanguageContinuationError("review MASTER_EN lacks source PDF authority")
            source_path = Path(source["path"])
            if not source_path.is_file() or file_identity(source_path) != {key: source.get(key) for key in ("bytes", "sha256")}:
                raise LanguageContinuationError("review MASTER_EN source PDF identity drift")
            issues = v2_bindings if v2_bindings.is_file() else run_root / "ISSUE_EN_BINDINGS.v1.json"
            if not issues.is_file():
                raise LanguageContinuationError("review MASTER_EN lacks issue EN bindings")
            master = run_root / "MASTER_EN.md"
            return {
                "predecessor_kind": "verified_review_draft",
                "review_master": _reference(review_manifest),
                "review_binding_root": (str(Path(review_binding_root).resolve()) if review_binding_root is not None else None),
                "source_pdf": _reference(source_path), "master_en": _reference(master),
                "issue_en_bindings": _reference(issues),
                "final_evidence": manifest["final_evidence"],
            }, master
        raise LanguageContinuationError("unsupported review MASTER_EN manifest")
    state = _read(run_root / "state.json")
    validate_seal(state, "state_sha256")
    if state.get("schema") != five_step.SCHEMA:
        raise LanguageContinuationError("unsupported predecessor run")
    source = _check_reference(state["source"])
    master = Path(state["paths"]["master_en"])
    assert_existing_path_components_are_not_reparse(master)
    master = master.resolve(strict=True)
    if not master.is_relative_to(run_root) or master.name != "MASTER_EN.md":
        raise LanguageContinuationError("MASTER_EN escapes predecessor run")
    records = [row for row in state["evidence"] if row["step"] == 2]
    if len(records) != 1:
        raise LanguageContinuationError("exactly one Step 2 evidence record required")
    record = records[0]
    base = (run_root / record["root"]).resolve(strict=True)
    if base != master.parent or not base.is_relative_to(run_root):
        raise LanguageContinuationError("Step 2 evidence does not bind MASTER_EN")
    if record["files"] != deterministic_inventory(base):
        raise LanguageContinuationError("changed Step 2 evidence")
    if record["code"] != five_step._codes(2):
        raise LanguageContinuationError("Step 2 implementation changed")
    five_step_intake.verify_master_en(base)
    provenance = _read(base / "MASTER_EN.provenance.json")
    if any(provenance["source"].get(key) != state["source"]["identity"][key]
           for key in ("bytes", "sha256")):
        raise LanguageContinuationError("MASTER_EN source identity differs from run PDF")
    return {"predecessor_kind": "strict_step2", "run_state": _reference(run_root / "state.json"),
            "source_pdf": _reference(source), "master_en": _reference(master)}, master


def _new_root(output: Path, forbidden: list[Path]) -> Path:
    assert_existing_path_components_are_not_reparse(output)
    root = output.resolve()
    if root.exists():
        raise LanguageContinuationError("output already exists; use a new successor directory")
    for path in forbidden:
        protected = path.resolve()
        if root.is_relative_to(protected) or protected.is_relative_to(root):
            raise LanguageContinuationError("output overlaps immutable predecessor")
    root.mkdir(parents=True)
    return root


def _finish(root: Path, body: dict[str, Any]) -> dict[str, Any]:
    body = {**body, "code": _codes(), "files": deterministic_inventory(root),
            "book_acceptance": "pending", "docx_package": "pending"}
    _write(root / MANIFEST, sealed(SCHEMA, body, digest_key="continuation_sha256"))
    return verify_continuation(root)


def _same_file(left: Path, right: Path) -> None:
    if file_identity(left) != file_identity(right):
        raise LanguageContinuationError(f"archived parent evidence differs: {left.name}")


def _same_submission(archived: Path, supplied: Path, schema: str) -> None:
    value = _read(archived)
    five_step_language._seal_ok(value, "submission_sha256", schema)
    strip = lambda record: {key: item for key, item in record.items() if key != "submission_sha256"}
    if strip(value) != strip(_read(supplied)):
        raise LanguageContinuationError("archived submission differs from supplied submission")


def _verify_draft(result: Path, language_root: Path, submission: Path) -> None:
    language = five_step_language
    task_path = language_root / "draft.task.json"
    task = _read(task_path)
    _same_file(result / "evidence/draft.task.json", task_path)
    _same_submission(result / "evidence/draft.submission.json", submission,
                     "kb_creator.five_step_language_draft_submission.v2")
    master = language._source(task, "master_en")
    unit_context = language._verified_unit_context(task, master)
    rows = language._draft_rows(task, language._id(task_path, language_root),
                               _read(submission), language._source(task, "glossary"), unit_context)
    draft = _read(result / "documentary_draft.json")
    language._seal_ok(draft, "draft_sha256", "kb_creator.five_step_documentary_draft.v2")
    expected = {"task": language._id(result / "evidence/draft.task.json", result),
                "submission": language._id(result / "evidence/draft.submission.json", result),
                "master_en": task["master_en"], "glossary": task["glossary"],
                "units": rows, "mechanical_findings": []}
    if any(draft.get(key) != value for key, value in expected.items()):
        raise LanguageContinuationError("documentary draft does not match source submission")
    proof = _read(result / "proofread.task.json")
    language._seal_ok(proof, "task_sha256", "kb_creator.five_step_language_proofread_task.v2")
    expected_units = [{"unit_id": row["unit_id"], "source_hash": row["source_hash"],
                       "source_text": row["source_text"], "parent_unit_id": row.get("parent_unit_id"),
                       "part_index": row.get("part_index"), "part_count": row.get("part_count"),
                       "draft_ru_text": row["ru_text"],
                       "draft_ru_sha256": language._sha(row["ru_text"].encode())} for row in rows]
    if (proof.get("units") != expected_units or proof.get("language_task") != expected["task"] or
            proof.get("draft") != language._id(result / "documentary_draft.json", result) or
            proof.get("master_en") != task["master_en"] or proof.get("glossary") != task["glossary"]):
        raise LanguageContinuationError("proofread task does not match documentary draft")


def prepare_continuation(run_root: Path, glossary: Path, output: Path, *,
                         shared_registry: Path | None = None, book_id: str | None = None,
                         review_binding_root: Path | None = None) -> dict[str, Any]:
    inputs, master = _verified_master(run_root, review_binding_root=review_binding_root)
    glossary_source = _reference(glossary)
    five_step_language._terms(glossary)
    root = _new_root(output, [run_root, glossary.parent])
    try:
        if shared_registry is not None:
            from .coc_glossary import compose_glossary
            if not book_id:
                raise LanguageContinuationError("book_id required for shared CoC glossary")
            composition = compose_glossary(shared_registry, glossary, book_id, root / "terminology")
            if composition["state"] != "ready":
                raise LanguageContinuationError("shared/book terminology conflicts; inspect terminology/conflicts.json")
            glossary = Path(composition["glossary_path"])
            glossary_source = _reference(glossary)
        shutil.copyfile(glossary, root / "glossary.json")
        predecessor = inputs.get("run_state") if inputs["predecessor_kind"] == "strict_step2" else inputs["review_master"]
        shutil.copyfile(Path(predecessor["path"]), root / ("predecessor-state.json" if inputs["predecessor_kind"] == "strict_step2" else "predecessor-review-master.json"))
        if inputs["predecessor_kind"] == "verified_review_draft":
            shutil.copyfile(Path(inputs["issue_en_bindings"]["path"]),
                            root / Path(inputs["issue_en_bindings"]["path"]).name)
        if file_identity(root / "glossary.json") != glossary_source["identity"]:
            raise LanguageContinuationError("glossary changed during copy")
        five_step_language.prepare_language(master, root / "glossary.json", root / "language")
        return _finish(root, {"phase": "documentary_draft", "inputs": inputs,
                             "glossary_source": glossary_source, "parent": None})
    except Exception as error:
        _write(root / "FAILED.json", {"error": str(error), "usable": False})
        raise


def _predecessor_reference(inputs: object) -> dict[str, Any]:
    if not isinstance(inputs, dict):
        raise LanguageContinuationError("continuation inputs are missing")
    predecessor = (inputs.get("run_state") if inputs.get("predecessor_kind") == "strict_step2"
                   else inputs.get("review_master"))
    if not isinstance(predecessor, dict):
        raise LanguageContinuationError("continuation predecessor authority is missing")
    return predecessor


def _verification_context(root: Path) -> _VerificationContext:
    """Derive producer authority once without carrying it across public calls."""
    value = _read(root / MANIFEST)
    validate_seal(value, "continuation_sha256")
    if value.get("schema") != SCHEMA:
        raise LanguageContinuationError("unsupported language continuation")
    predecessor = _check_reference(_predecessor_reference(value.get("inputs")))
    review_binding_root = value["inputs"].get("review_binding_root")
    if review_binding_root is not None and not isinstance(review_binding_root, str):
        raise LanguageContinuationError("review binding root is malformed")
    inputs, master = _verified_master(predecessor.parent,
                                      review_binding_root=Path(review_binding_root) if review_binding_root else None)
    if inputs != value["inputs"]:
        raise LanguageContinuationError("predecessor identity mismatch")
    return _VerificationContext(inputs=inputs, master=master, predecessor_root=predecessor.parent)


def verify_continuation(root: Path) -> dict[str, Any]:
    """Verify one immutable chain with fresh producer authority for this call."""
    assert_existing_path_components_are_not_reparse(root)
    root = root.resolve(strict=True)
    return _verify_continuation(root, _verification_context(root), depth=0)


def _verify_continuation(root: Path, context: _VerificationContext, *, depth: int) -> dict[str, Any]:
    if depth > 2:
        raise LanguageContinuationError("invalid continuation chain depth")
    assert_existing_path_components_are_not_reparse(root)
    root = root.resolve(strict=True)
    value = _read(root / MANIFEST)
    validate_seal(value, "continuation_sha256")
    if value.get("schema") != SCHEMA or value.get("phase") not in {
        "documentary_draft", "proofread_final", "language_complete"
    }:
        raise LanguageContinuationError("unsupported language continuation")
    if (root / "FAILED.json").exists():
        raise LanguageContinuationError("incomplete continuation")
    if value["code"] != _codes():
        raise LanguageContinuationError("language implementation changed; new successor required")
    observed = [row for row in deterministic_inventory(root) if row["path"] != MANIFEST]
    if observed != value["files"]:
        raise LanguageContinuationError("continuation inventory mismatch")
    predecessor = _predecessor_reference(value.get("inputs"))
    old_predecessor = _check_reference(predecessor)
    if old_predecessor.parent != context.predecessor_root or value["inputs"] != context.inputs:
        raise LanguageContinuationError("predecessor identity mismatch")
    inputs, master = context.inputs, context.master
    if inputs["predecessor_kind"] == "verified_review_draft":
        archived_issues = root / Path(inputs["issue_en_bindings"]["path"]).name
        if (not archived_issues.is_file() or
                file_identity(archived_issues) != inputs["issue_en_bindings"]["identity"]):
            raise LanguageContinuationError("archived issue EN bindings mismatch")
    phase = value["phase"]
    parent = value["parent"]
    if phase == "documentary_draft":
        if parent is not None:
            raise LanguageContinuationError("prepared continuation cannot have a parent")
        archived = root / ("predecessor-state.json" if inputs["predecessor_kind"] == "strict_step2" else "predecessor-review-master.json")
        if file_identity(archived) != predecessor["identity"]:
            raise LanguageContinuationError("archived predecessor authority mismatch")
        if file_identity(root / "glossary.json") != value["glossary_source"]["identity"]:
            raise LanguageContinuationError("archived glossary mismatch")
        five_step_language._terms(root / "glossary.json")
        if (root / "terminology").exists():
            from .coc_glossary import verify_glossary
            composition = verify_glossary(root / "terminology")
            if composition["state"] != "ready":
                raise LanguageContinuationError("shared glossary remains conflicted")
            _same_file(root / "glossary.json", Path(composition["glossary_path"]))
        language_root = root / "language"
        task = _read(language_root / "draft.task.json")
        validate_seal(task, "task_sha256")
        if (Path(task["master_en_path"]) != master or
                Path(task["glossary_path"]) != root / "glossary.json"):
            raise LanguageContinuationError("language task input path mismatch")
        for name in ("master_en", "glossary", "source_spans"):
            five_step_language._source(task, name)
        expected_units, _ = five_step_language._units(master, task["max_batch_chars"])
        if task["units"] != [five_step_language._unit(row) for row in expected_units]:
            raise LanguageContinuationError("language task unit coverage differs from MASTER_EN")
        five_step_language._verified_unit_context(task, master)
        result = {"language_root": str(language_root), "task_path": str(language_root / "draft.task.json"),
                  "template_path": str(language_root / "draft.template.json")}
    else:
        parent_manifest = _check_reference(parent)
        if parent_manifest.name != MANIFEST or parent_manifest.parent == root:
            raise LanguageContinuationError("invalid continuation parent")
        previous = _verify_continuation(parent_manifest.parent, context, depth=depth + 1)
        expected = "documentary_draft" if phase == "proofread_final" else "proofread_final"
        if previous["phase"] != expected or previous["inputs"] != inputs:
            raise LanguageContinuationError("continuation phase or input lineage mismatch")
        result = {"language_root": previous["language_root"]}
        if file_identity(root / "submission.json") != value["submission_source"]["identity"]:
            raise LanguageContinuationError("archived submission source identity mismatch")
        if phase == "proofread_final":
            _verify_draft(root / "result", Path(previous["language_root"]), root / "submission.json")
            result.update(draft_root=str(root / "result"), task_path=str(root / "result/proofread.task.json"),
                          template_path=str(root / "result/proofread.template.json"))
        else:
            draft_root = Path(previous["draft_root"])
            for name in ("documentary_draft.json", "proofread.task.json"):
                _same_file(root / "result/evidence" / name, draft_root / name)
            for name in ("draft.task.json", "draft.submission.json"):
                _same_file(root / "result/evidence" / name, draft_root / "evidence" / name)
            _same_submission(root / "result/evidence/proofread.submission.json", root / "submission.json",
                             "kb_creator.five_step_language_proofread_submission.v2")
            verified = five_step_language.verify_language_result(root / "result")
            result.update(final_root=str(root / "result"), language_verification=verified)
    return {"state": "verified", "phase": phase, "root": str(root), "inputs": inputs,
            "book_acceptance": "pending", "docx_package": "pending", **result}


def submit_continuation(root: Path, submission: Path, output: Path) -> dict[str, Any]:
    previous = verify_continuation(root)
    phase = previous["phase"]
    if phase == "language_complete":
        raise LanguageContinuationError("language already complete")
    submitted = _reference(submission)
    predecessor = (previous["inputs"].get("run_state")
                   if previous["inputs"]["predecessor_kind"] == "strict_step2"
                   else previous["inputs"].get("review_master"))
    if not isinstance(predecessor, dict):
        raise LanguageContinuationError("continuation predecessor authority is missing")
    target = _new_root(output, [root, Path(predecessor["path"]).parent])
    try:
        shutil.copyfile(submission, target / "submission.json")
        if file_identity(target / "submission.json") != submitted["identity"]:
            raise LanguageContinuationError("submission changed during copy")
        if previous["inputs"]["predecessor_kind"] == "verified_review_draft":
            issues = Path(previous["inputs"]["issue_en_bindings"]["path"])
            target_issues = target / issues.name
            shutil.copyfile(issues, target_issues)
            if file_identity(target_issues) != previous["inputs"]["issue_en_bindings"]["identity"]:
                raise LanguageContinuationError("issue EN bindings changed during copy")
        language_root = Path(previous["language_root"])
        if phase == "documentary_draft":
            five_step_language.submit_draft(language_root, target / "submission.json", target / "result")
            next_phase = "proofread_final"
        else:
            five_step_language.submit_proofread(language_root, Path(previous["draft_root"]),
                                               target / "submission.json", target / "result")
            next_phase = "language_complete"
        return _finish(target, {"phase": next_phase, "inputs": previous["inputs"],
                               "submission_source": submitted, "parent": _reference(root / MANIFEST)})
    except Exception as error:
        _write(target / "FAILED.json", {"error": str(error), "usable": False})
        raise
