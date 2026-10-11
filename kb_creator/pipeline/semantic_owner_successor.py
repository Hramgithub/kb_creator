"""Prepare additive semantic owners after a sealed lexical successor.

This is an input producer. It proves local recorded identities and semantic
compatibility, then leaves fresh archive/source certification to the public
author and materialization gates.
"""
from __future__ import annotations

import copy
import json
import shutil
from pathlib import Path
from typing import Any

from .identity import canonical_bytes, file_identity, sha256_bytes
from .manifests import validate_seal
from .review_draft import INPUT_SCHEMA, validate_review_draft_input
from .review_draft_materialization import _stage06_proof_keys
from .review_draft_preparation import validate_review_draft_author_input
from .source_choice_selectors import rebind_unit_selectors
from .source_choice_slice import SourceSlice
from .source_choice_translation import (
    LEDGER_SCHEMA_V2, QUEUE_SCHEMA_V2, SUBMISSION_SCHEMA_V2, _check_tree,
    _decision_records_v2,
)
from .source_marker_dispositions import copy_bound_input
from kb_creator.scripts.author_reviewed_semantic_decisions import (
    _build_semantic_unit, _definition_span, _shared_unit_sources,
)


class SemanticOwnerSuccessorError(ValueError):
    """An additive owner cannot be grounded in the sealed lexical lineage."""


def _read(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8-sig"))
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        raise SemanticOwnerSuccessorError(f"cannot read recorded JSON: {path}") from error
    if not isinstance(value, dict):
        raise SemanticOwnerSuccessorError("recorded JSON is not an object")
    return value


def _write(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _bound_path(root: Path, record: Any, label: str) -> Path:
    if not isinstance(record, dict) or set(record) != {"path", "bytes", "sha256"}:
        raise SemanticOwnerSuccessorError(f"{label} identity is malformed")
    relative = Path(record["path"])
    if relative.is_absolute() or ".." in relative.parts:
        raise SemanticOwnerSuccessorError(f"{label} path escapes binding root")
    path = (root / relative).resolve()
    if not path.is_file() or file_identity(path) != {key: record[key] for key in ("bytes", "sha256")}:
        raise SemanticOwnerSuccessorError(f"{label} identity drift")
    return path


def _absolute_record(record: Any, label: str) -> Path:
    if not isinstance(record, dict) or set(record) != {"path", "bytes", "sha256"}:
        raise SemanticOwnerSuccessorError(f"{label} identity is malformed")
    path = Path(record["path"])
    if not path.is_absolute() or not path.is_file() or file_identity(path) != {
            key: record[key] for key in ("bytes", "sha256")}:
        raise SemanticOwnerSuccessorError(f"{label} identity drift")
    return path.resolve()


def _portable(path: Path, root: Path) -> dict[str, Any]:
    try:
        relative = path.resolve().relative_to(root).as_posix()
    except ValueError as error:
        raise SemanticOwnerSuccessorError("successor binding escapes root") from error
    return {"path": relative, **file_identity(path)}


def _spec_pages(specs: list[dict[str, Any]]) -> dict[int, tuple[int, dict[str, Any]]]:
    result: dict[int, tuple[int, dict[str, Any]]] = {}
    for index, spec in enumerate(specs):
        pages = spec.get("pages")
        if not isinstance(pages, list):
            raise SemanticOwnerSuccessorError("semantic spec page list is malformed")
        for row in pages:
            page = row.get("source_page") if isinstance(row, dict) else None
            if type(page) is not int or page < 1 or page in result:
                raise SemanticOwnerSuccessorError("semantic spec page domain is duplicate or malformed")
            result[page] = index, row
    return result


def _local_ledger(lexical: dict[str, Any], root: Path) -> tuple[dict[str, Any], dict[str, Any], Path, Path]:
    bindings = lexical["bindings"]
    predecessor_path = _bound_path(root, bindings.get("source_choice_predecessor"), "original predecessor")
    predecessor = _read(predecessor_path)
    validate_review_draft_author_input(input_path=predecessor_path, binding_root=root)
    queue_path = _bound_path(root, bindings.get("source_choice_queue"), "source-choice queue")
    ledger_path = _bound_path(root, bindings.get("source_choice_ledger"), "source-choice ledger")
    queue, ledger = _read(queue_path), _read(ledger_path)
    submission_path = ledger_path.parent / "SOURCE_CHOICE_SUBMISSION.v2.json"
    submission = _read(submission_path)
    for value, field in ((queue, "queue_sha256"), (ledger, "ledger_sha256"),
                         (submission, "submission_sha256")):
        validate_seal(value, field)
    if (queue.get("schema") != QUEUE_SCHEMA_V2 or ledger.get("schema") != LEDGER_SCHEMA_V2
            or submission.get("schema") != SUBMISSION_SCHEMA_V2
            or _absolute_record(ledger.get("queue"), "ledger queue") != queue_path
            or _absolute_record(submission.get("queue"), "submission queue") != queue_path):
        raise SemanticOwnerSuccessorError("source-choice records disagree on queue authority")
    expected_submission, expected_ledger = _decision_records_v2(queue_path, queue, submission.get("choices"))
    if submission != expected_submission or ledger != expected_ledger:
        raise SemanticOwnerSuccessorError("source-choice ledger/submission differs from sealed decisions")
    evidence = _read(_absolute_record(queue.get("final_evidence"), "queue final evidence"))
    if predecessor["input_sha256"] != evidence.get("input_sha256"):
        raise SemanticOwnerSuccessorError("original predecessor differs from queue evidence")
    return predecessor, queue, ledger_path, queue_path


def _recorded_authorities(queue: dict[str, Any]) -> tuple[Path, Path, dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any]]:
    master = _absolute_record(queue.get("review_master"), "review master").parent
    manifest_path = _absolute_record(queue.get("review_manifest"), "review master manifest")
    if manifest_path != (master / "MANIFEST.json").resolve():
        raise SemanticOwnerSuccessorError("review master manifest differs from queued master")
    manifest = _read(manifest_path)
    inventory_path = _bound_path(master, manifest.get("inventory"), "review master inventory")
    inventory = _read(inventory_path)
    master_rows = {row["path"]: row for row in inventory.get("rows", [])}
    candidate = _check_tree(queue.get("candidate"), "mechanical candidate")
    candidate_manifest = _read(candidate / "mechanical_draft.json")
    run = Path(candidate_manifest["run_root"]).resolve()
    stage_path = run / "stages/04-visual-merge-bundle/stage.json"
    stage = _read(stage_path)
    if stage.get("reproducible_sha256") != sha256_bytes(canonical_bytes(stage.get("reproducible"))):
        raise SemanticOwnerSuccessorError("Stage04 recorded inventory seal is invalid")
    stage_rows = {row["path"]: row for row in stage["reproducible"]["outputs"]["files"]}
    output = run / "outputs/04-visual-merge-bundle"
    evidence_path = _absolute_record(queue.get("final_evidence"), "queue final evidence")
    final = _read(evidence_path)
    allow_record = final.get("authored", {}).get("reviewed_allowlist")
    if not isinstance(allow_record, dict) or set(allow_record) != {"path", "bytes", "sha256"}:
        raise SemanticOwnerSuccessorError("review allowlist identity is absent")
    allowlist = _read(_bound_path(evidence_path.parent, allow_record, "review allowlist"))
    visual = _read(_bound_path(output, stage_rows.get("visual/visual_manifest.json"), "visual manifest"))
    geometry = _read(_bound_path(output, stage_rows.get("visual/geometry_plan.json"), "geometry plan"))
    visual_inventory = {
        str((output / row["path"]).relative_to(run)).replace("\\", "/"):
        {key: row[key] for key in ("bytes", "sha256")}
        for row in visual["files"]
    }
    return master, output, master_rows, stage_rows, allowlist, {"geometry": geometry, "visuals": visual_inventory}


def _recorded_page(root: Path, row: Any, relative: str) -> dict[str, Any]:
    if not isinstance(row, dict) or row.get("path") != relative:
        raise SemanticOwnerSuccessorError(f"recorded page absent: {relative}")
    return _read(_bound_path(root, row, relative))


def prepare_review_draft_semantic_owner_successor(*, lexical_input: Path, binding_root: Path,
        reviewed_spec_paths: list[Path], output_dir: Path) -> dict[str, Any]:
    """Seal new spec/input identities for validated additive owners; no acceptance."""
    lexical_input, root = Path(lexical_input).resolve(), Path(binding_root).resolve()
    output_dir = Path(output_dir).resolve()
    reviewed_paths = [Path(path).resolve() for path in reviewed_spec_paths]
    if (not reviewed_paths or len(set(reviewed_paths)) != len(reviewed_paths)
            or not root.is_dir() or not lexical_input.is_file() or output_dir.exists()
            or not output_dir.parent.is_dir()):
        raise SemanticOwnerSuccessorError("owner successor inputs or destination are unavailable")
    try:
        lexical_input.relative_to(root)
        output_dir.relative_to(root)
    except ValueError as error:
        raise SemanticOwnerSuccessorError("owner successor escapes binding root") from error
    lexical = _read(lexical_input)
    validate_review_draft_author_input(input_path=lexical_input, binding_root=root)
    predecessor, queue, ledger_path, queue_path = _local_ledger(lexical, root)
    bindings = lexical["bindings"]
    old_names = sorted(name for name in predecessor["bindings"] if name.startswith("input_"))
    lexical_names = sorted(name for name in bindings if name.startswith("source_choice_successor_spec-"))
    if not old_names or len(old_names) != len(lexical_names) or len(old_names) != len(reviewed_paths):
        raise SemanticOwnerSuccessorError("original, lexical and reviewed spec counts differ")
    original_specs = [_read(_bound_path(root, predecessor["bindings"][name], name)) for name in old_names]
    lexical_specs = [_read(_bound_path(root, bindings[name], name)) for name in lexical_names]
    reviewed_specs = [_read(path) for path in reviewed_paths]
    original_pages, lexical_pages, reviewed_pages = map(_spec_pages,
        (original_specs, lexical_specs, reviewed_specs))
    if not original_pages or set(original_pages) != set(lexical_pages) or set(original_pages) != set(reviewed_pages):
        raise SemanticOwnerSuccessorError("semantic spec page domains differ")
    for old, reviewed in zip(original_specs, reviewed_specs):
        if {key: value for key, value in old.items() if key != "pages"} != {
                key: value for key, value in reviewed.items() if key != "pages"}:
            raise SemanticOwnerSuccessorError("reviewed spec changes non-page authority")
    for page, (index, old_row) in original_pages.items():
        if reviewed_pages[page][0] != index or lexical_pages[page][0] != index:
            raise SemanticOwnerSuccessorError("spec fragment ownership changed")
        reviewed_row = reviewed_pages[page][1]
        if {key: value for key, value in old_row.items() if key != "units"} != {
                key: value for key, value in reviewed_row.items() if key != "units"}:
            raise SemanticOwnerSuccessorError(f"page {page}: reviewed spec changes non-unit fields")
        old_units, new_units = old_row.get("units", []), reviewed_row.get("units", [])
        if not isinstance(old_units, list) or not isinstance(new_units, list):
            raise SemanticOwnerSuccessorError("semantic unit list is malformed")
        cursor = iter(new_units)
        if any(not any(candidate == unit for candidate in cursor) for unit in old_units):
            raise SemanticOwnerSuccessorError(f"page {page}: old unit changed or removed")
    master, stage_output, master_rows, stage_rows, allowlist, visual_context = _recorded_authorities(queue)
    queue_by_issue = {row["issue_id"]: row for row in queue["choices"]}
    ledger = _read(ledger_path)
    choices: dict[int, list[SourceSlice]] = {}
    for row in ledger["source_choices"]:
        if row["disposition"] != "selected_alternative":
            continue
        page = queue_by_issue[row["issue_id"]]["source_page"]
        span = row["r0_reader_span"]
        choices.setdefault(page, []).append(SourceSlice(span["character_start"], span["character_end"],
            span["text_sha256"], row["intended_reader_successor"]["text"]))
    decisions: dict[int, dict[str, Any]] = {}
    packets: dict[int, dict[str, Any]] = {}
    additions: dict[int, list[dict[str, Any]]] = {}
    all_ids: set[str] = set()
    for page, (_, old_row) in sorted(original_pages.items()):
        decision_rel = f"evidence/review/page-{page:03d}.json"
        packet_rel = f"merge_packets/pages/page-{page:03d}.json"
        decision = _recorded_page(master, master_rows.get(decision_rel), decision_rel)
        packet = _recorded_page(stage_output, stage_rows.get(packet_rel), packet_rel)
        old_units = old_row.get("units", [])
        reviewed_units = reviewed_pages[page][1].get("units", [])
        old_ids = {unit["id"] for unit in old_units}
        extra = [unit for unit in reviewed_units if unit.get("id") not in old_ids]
        ids = [unit.get("id") for unit in reviewed_units]
        if (len(ids) != len(set(ids)) or any(not isinstance(name, str) or not name or name in all_ids
                                             for name in ids)):
            raise SemanticOwnerSuccessorError(f"page {page}: semantic owner ID is duplicate or malformed")
        all_ids.update(ids)
        if extra:
            lines = decision["markdown"].split("\n")
            shared = _shared_unit_sources(reviewed_pages[page][1], decision["overlay_preference"])
            built = []
            for definition in extra:
                _definition_span(lines, definition, page)
                built.append(_build_semantic_unit(packet, definition, decision["overlay_preference"],
                    page, lines, shared, original_specs[original_pages[page][0]]["semantic_structure_profile"]))
            augmented = copy.deepcopy(decision)
            augmented["semantic_structure"]["units"].extend(built)
            augmented["semantic_structure"]["units"].sort(key=lambda unit: (
                unit["markdown_span"]["start_line"], -unit["markdown_span"]["end_line"]))
            decisions[page] = augmented
            additions[page] = extra
        else:
            decisions[page] = decision
        packets[page] = packet
        projected = (rebind_unit_selectors(old_row, decision["markdown"],
            decision["semantic_structure"]["units"], choices[page],
            markdown_sha256=sha256_bytes(decision["markdown"].encode()))
            if page in choices else old_row)
        if projected["units"] != lexical_pages[page][1]["units"]:
            raise SemanticOwnerSuccessorError(f"page {page}: preserved lexical owner projection differs")
    if not additions:
        raise SemanticOwnerSuccessorError("reviewed spec contains no additional semantic owners")
    _stage06_proof_keys(decisions, packets, allowlist,
        visual_context["visuals"], visual_context["geometry"])
    copied_specs = copy.deepcopy(lexical_specs)
    for page, added in additions.items():
        decision = decisions[page]
        original_decision = _recorded_page(master, master_rows[f"evidence/review/page-{page:03d}.json"],
            f"evidence/review/page-{page:03d}.json")
        projected = rebind_unit_selectors({"units": added}, original_decision["markdown"],
            decision["semantic_structure"]["units"], choices.get(page, []),
            markdown_sha256=sha256_bytes(original_decision["markdown"].encode()))["units"]
        row = copied_specs[lexical_pages[page][0]]["pages"]
        target = next(item for item in row if item["source_page"] == page)
        target["units"].extend(projected)
        target["units"].sort(key=lambda unit: (unit["start_line"], -unit["end_line"]))
        old_projected = lexical_pages[page][1]["units"]
        if [unit for unit in target["units"] if unit["id"] in {old["id"] for old in old_projected}] != old_projected:
            raise SemanticOwnerSuccessorError(f"page {page}: old owner order changed")
    page_bindings = {name: record for name, record in bindings.items()
                     if name.startswith("source_choice_successor_page-")}
    draft_roots = {(_bound_path(root, record, name)).parent for name, record in page_bindings.items()}
    if not page_bindings or len(draft_roots) != 1 or len(page_bindings) != len(original_pages):
        raise SemanticOwnerSuccessorError("lexical draft-page binding domain differs")
    drafts_root = draft_roots.pop()
    stage = output_dir.parent / f".{output_dir.name}.staging"
    if stage.exists():
        raise SemanticOwnerSuccessorError("owner successor staging path already exists")
    try:
        stage.mkdir()
        new_bindings = copy.deepcopy(bindings)
        for index, (source, spec) in enumerate(zip(reviewed_paths, copied_specs)):
            target = stage / "author-specs" / f"spec-{index:02d}.json"
            _write(target, spec)
            copy_bound_input(source, target)
            future = output_dir / target.relative_to(stage)
            identity = {"path": future.relative_to(root).as_posix(), **file_identity(target)}
            new_bindings[f"source_choice_successor_spec-{index:02d}"] = identity
            new_bindings[f"semantic_owner_reviewed_spec_{index:02d}"] = _portable(source, root)
        new_bindings["semantic_owner_predecessor_input"] = _portable(lexical_input, root)
        successor = {"schema": INPUT_SCHEMA, "bindings": new_bindings,
                     "source_issues": lexical["source_issues"],
                     "unresolved_dispositions": lexical["unresolved_dispositions"]}
        successor["input_sha256"] = sha256_bytes(canonical_bytes(successor))
        validate_review_draft_input(successor)
        _write(stage / "review-draft-input.json", successor)
        stage.replace(output_dir)
        output_input = output_dir / "review-draft-input.json"
        validate_review_draft_author_input(input_path=output_input, binding_root=root)
        return {"state": "prepared_pending_validation", "input_path": str(output_input),
                "spec_paths": [str(output_dir / "author-specs" / f"spec-{i:02d}.json")
                               for i in range(len(copied_specs))],
                "draft_pages": str(drafts_root),
                "added_owner_count": sum(map(len, additions.values())),
                "page_count": len(original_pages)}
    finally:
        if stage.exists():
            shutil.rmtree(stage)
