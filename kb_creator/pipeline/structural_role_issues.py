"""Exact authority for unresolved source-role comparison conflicts.

Structural role questions are review provenance.  They are deliberately kept
separate from lexical source-choice alternatives and from page ``unresolved``
strings, which have a different disposition lifecycle.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping

from .identity import assert_existing_path_components_are_not_reparse, file_identity, sha256_bytes


class StructuralRoleIssueError(ValueError):
    pass


STRUCTURAL_KIND = "source_structure_role_pending"
SELECTOR_KEY = "comparison_structural_role_v1"


def read_preview_decisions(preview: Path, queue: Mapping[str, Any]) -> tuple[dict[int, dict], dict]:
    """Check provisional page inventory without asserting visual acceptance."""
    preview = Path(preview)
    assert_existing_path_components_are_not_reparse(preview)
    manifest = json.loads((preview / "decision_set.json").read_text(encoding="utf-8"))
    expected_keys = {"schema", "review_queue_sha256", "contract_sha256", "source_sha256",
                     "decisions", "reviewed_allowlist", "semantic_structure_profile", "submission_state"}
    if (not isinstance(manifest, dict) or set(manifest) != expected_keys
            or manifest["schema"] != "kb_creator.reconstruction_decision_set.v2"
            or manifest["submission_state"] != "submitted_for_validation"
            or manifest["semantic_structure_profile"] not in {
                "visually_reviewed_semantic_containers_v1", "reviewed_role_outline_and_partitions_v2"}
            or any(manifest[field] != queue[other] for field, other in (
                ("review_queue_sha256", "queue_sha256"), ("contract_sha256", "contract_sha256"),
                ("source_sha256", "source_sha256")))):
        raise StructuralRoleIssueError("preview decision set schema or queue authority mismatch")
    expected = [row["source_page"] for row in queue["items"]]
    rows = manifest["decisions"]
    if (not isinstance(rows, list) or len(expected) != len(set(expected))
            or len(rows) != len(expected) or any(not isinstance(row, dict) for row in rows)
            or [row.get("source_page") for row in rows] != expected):
        raise StructuralRoleIssueError("preview decision set page domain mismatch")
    if {p.name for p in (preview / "pages").glob("page-*.json")} != {f"page-{p:03d}.json" for p in expected}:
        raise StructuralRoleIssueError("preview page files differ from queue domain")
    pages = {}
    for row in rows:
        page = row["source_page"]
        if set(row) != {"source_page", "path", "bytes", "sha256"} or row["path"] != f"pages/page-{page:03d}.json":
            raise StructuralRoleIssueError("preview page record path mismatch")
        path = preview / row["path"]
        assert_existing_path_components_are_not_reparse(path)
        if file_identity(path) != {key: row[key] for key in ("bytes", "sha256")}:
            raise StructuralRoleIssueError("preview page identity mismatch")
        decision = json.loads(path.read_text(encoding="utf-8"))
        if decision.get("source_page") != page or decision.get("schema") != queue["required_decision_schema"]:
            raise StructuralRoleIssueError("preview page content domain mismatch")
        pages[page] = decision
    allow = manifest["reviewed_allowlist"]
    if (not isinstance(allow, dict) or set(allow) != {"path", "bytes", "sha256"}
            or allow["path"] != "reviewed_allowlist.v3.json"):
        raise StructuralRoleIssueError("preview reviewed allowlist path mismatch")
    path = preview / allow["path"]
    assert_existing_path_components_are_not_reparse(path)
    if file_identity(path) != {key: allow[key] for key in ("bytes", "sha256")}:
        raise StructuralRoleIssueError("preview reviewed allowlist identity mismatch")
    return pages, json.loads(path.read_text(encoding="utf-8"))


def load_structural_preview(run_root: Path, preview: Path) -> dict[str, Any]:
    """Reopen sealed archive and exact provisional pages used for source issues."""
    from .review_draft import ArchiveConsumptionAuthorities, build_archive_consumption_context
    from .reconstruction_replay_resume import validate_replay_review_queue, _validate_allowlist
    from .review_draft_materialization import _stage06_proof_keys
    from kb_creator.scripts.author_reviewed_semantic_decisions import _visual_inventory

    archive = build_archive_consumption_context(source_run_root=run_root, target_run_root=run_root)
    paths = {key: Path(value) for key, value in archive["checked_paths"].items()}
    authority = ArchiveConsumptionAuthorities(run_root=run_root, bridge_sha256=archive["target"]["bridge_sha256"],
        **{key: paths[key] for key in ("stage_02_root", "comparison", "merge_packets", "visual_manifest", "geometry_plan")})
    queue = validate_replay_review_queue(authority)
    decisions, allowlist = read_preview_decisions(preview, queue.queue)
    _validate_allowlist(preview / "reviewed_allowlist.v3.json", queue, authority)
    packets = {page: json.loads((paths["merge_packets"] / "pages" / f"page-{page:03d}.json").read_text(encoding="utf-8"))
               for page in decisions}
    geometry = json.loads(paths["geometry_plan"].read_text(encoding="utf-8"))
    stage06 = _stage06_proof_keys(decisions, packets, allowlist, _visual_inventory(run_root), geometry)
    return {"paths": paths, "queue": queue.queue, "decisions": decisions, "packets": packets,
            "comparison": json.loads(paths["comparison"].read_text(encoding="utf-8")),
            "geometry": geometry,
            "reference_proof_keys": stage06.reference_proof_keys,
            "split_structure_proof_keys": stage06.split_structure_proof_keys,
            "visual_assertions": stage06.visual_assertions}


def pending_structural_conflicts(decisions: Mapping[int, dict], packets: Mapping[int, dict],
        comparison: dict, reference_proof_keys: set, split_structure_proof_keys: set,
        visual_assertions: Mapping[str, Mapping[str, Any]] | None = None):
    from kb_creator.scripts.materialize_mineru_ai_merge import _selected_conflicts, _resolved_semantic_conflict
    for page, decision in decisions.items():
        for conflict, units in _selected_conflicts(comparison, _selected(decision, packets[page])):
            if not _resolved_semantic_conflict(conflict, units, decision,
                    reference_proof_keys, split_structure_proof_keys, packets[page], visual_assertions):
                yield page, conflict, units


def selected_source_key(issue: Mapping[str, Any]) -> tuple[str, int] | None:
    """Return the one source occurrence authorized by a structural selector."""
    selector = issue.get("source_selector", {}).get(SELECTOR_KEY)
    key = selector.get("selected_source_key") if isinstance(selector, Mapping) else None
    if not isinstance(key, Mapping) or set(key) != {"view", "raw_index"}:
        return None
    view, raw = key.get("view"), key.get("raw_index")
    return (view, raw) if isinstance(view, str) and type(raw) is int else None


def validate_structural_issue(issue: Mapping[str, Any]) -> None:
    """Validate the closed selector shape before it becomes authority."""
    if issue.get("kind") != STRUCTURAL_KIND:
        raise StructuralRoleIssueError("issue is not a structural role issue")
    selector = issue.get("source_selector", {}).get(SELECTOR_KEY)
    required = {"selected_source_key", "provisional_selection_purpose",
                "provisional_block_type", "comparison_records"}
    if not isinstance(selector, Mapping) or set(selector) != required:
        raise StructuralRoleIssueError("structural selector is not closed")
    if selected_source_key(issue) is None:
        raise StructuralRoleIssueError("structural selector source key is invalid")
    if selector["provisional_selection_purpose"] not in {"text", "structure", "asset", "visual"}:
        raise StructuralRoleIssueError("structural selector purpose is invalid")
    if not isinstance(selector["provisional_block_type"], str) or not selector["provisional_block_type"]:
        raise StructuralRoleIssueError("structural selector block type is invalid")
    rows = selector["comparison_records"]
    if not isinstance(rows, list) or not rows:
        raise StructuralRoleIssueError("structural selector has no comparison records")
    seen = set()
    for row in rows:
        if not isinstance(row, Mapping) or set(row) != {"pair_name", "semantic_conflict_index", "record_sha256"}:
            raise StructuralRoleIssueError("structural comparison record is malformed")
        key = (row.get("pair_name"), row.get("semantic_conflict_index"), row.get("record_sha256"))
        if (not isinstance(key[0], str) or "__vs__" not in key[0] or type(key[1]) is not int
                or key[1] < 0 or not isinstance(key[2], str) or len(key[2]) != 64 or key in seen):
            raise StructuralRoleIssueError("structural comparison locator is invalid or duplicated")
        seen.add(key)
    span = issue.get("candidate_span")
    key = selected_source_key(issue)
    if not isinstance(span, Mapping) or span != {"binding": "ordered_selected_source_v1",
            "source_page": issue.get("source_page"), "source_key": {"view": key[0], "raw_index": key[1]}}:
        raise StructuralRoleIssueError("structural candidate span is invalid")


def _selected(decision: Mapping[str, Any], packet: Mapping[str, Any]) -> dict[tuple[str, int], dict[str, Any]]:
    views = packet.get("views")
    if not isinstance(views, Mapping):
        raise StructuralRoleIssueError("packet views are invalid")
    result = {}
    for row in decision.get("selected_blocks", []):
        if not isinstance(row, Mapping):
            raise StructuralRoleIssueError("selected block is invalid")
        key = (row.get("view"), row.get("raw_index"))
        purpose = row.get("purpose")
        blocks = views.get(key[0], {}).get("blocks", []) if isinstance(key[0], str) else []
        match = [block for block in blocks if isinstance(block, Mapping) and block.get("raw_index") == key[1]]
        if len(match) != 1 or not isinstance(purpose, str):
            raise StructuralRoleIssueError("selected block does not bind packet")
        if purpose != "asset":
            result[key] = {**match[0], "_selection_purpose": purpose}
        else:
            result.setdefault(key, {**match[0], "_selection_purpose": purpose})
    return result


def _audit_mapping(stage05_pages: list[dict[str, Any]], page: int, key: tuple[str, int], *,
                   ledger_context: dict[Path, tuple[dict[str, Any], dict[str, Any]]] | None = None) -> dict[str, Any]:
    rows = [row for row in stage05_pages if isinstance(row, Mapping) and row.get("source_page") == page]
    if len(rows) != 1:
        raise StructuralRoleIssueError("Stage05 page proof is missing or duplicated")
    selected = [row for row in rows[0].get("ordered_proof_stream", []) if isinstance(row, Mapping)
                and row.get("kind") in {"selected", "linguistic_source_choice_v1", "linguistic_source_choice_container_v1"}
                and (row.get("unit", {}).get("view_id"), row.get("unit", {}).get("raw_index")) == key]
    if len(selected) != 1:
        raise StructuralRoleIssueError("structural issue lacks one ordered selected-source proof")
    span = selected[0].get("markdown_span")
    if not isinstance(span, list) or len(span) != 2 or any(type(item) is not int for item in span) or span[0] >= span[1]:
        raise StructuralRoleIssueError("ordered selected-source proof span is invalid")
    if selected[0].get("kind") in {"linguistic_source_choice_v1", "linguistic_source_choice_container_v1"}:
        from .reader_occurrence_projection import ReaderOccurrenceError, validate_linguistic_source_choice_stage05_row
        try:
            validate_linguistic_source_choice_stage05_row(selected[0], key, ledger_context=ledger_context)
        except ReaderOccurrenceError as error:
            raise StructuralRoleIssueError(f"linguistic Stage05 proof is invalid: {error}") from error
    return selected[0]


def derive_structural_role_conflict_proofs(*, review_input: Mapping[str, Any], input_path: Path,
        binding_root: Path, run_root: Path, decisions: Mapping[int, dict[str, Any]],
        packets: Mapping[int, dict[str, Any]], comparison: Mapping[str, Any],
        stage05_pages: list[dict[str, Any]]) -> dict[tuple[int, str, int, str], dict[str, Any]]:
    """Re-derive one-to-one proof ownership after a successful Stage05 audit.

    The returned map is passed explicitly into Stage06.  It never derives
    authority from prose, a page-wide unresolved string, or a lexical issue.
    """
    from .review_draft import validate_review_draft_input
    from .review_draft_preparation import validate_review_draft_author_input
    from kb_creator.scripts.materialize_mineru_ai_merge import _selected_conflicts, structural_conflict_locator

    try:
        sealed = validate_review_draft_input(dict(review_input))
        if json.loads(Path(input_path).read_text(encoding="utf-8")) != sealed.value:
            raise ValueError("input file differs from supplied authority")
        validate_review_draft_author_input(input_path=Path(input_path), binding_root=Path(binding_root))
    except (OSError, json.JSONDecodeError, ValueError) as error:
        raise StructuralRoleIssueError(f"review input authority is invalid: {error}") from error
    issues = [row for row in sealed.source_issues if row.get("kind") == STRUCTURAL_KIND]
    if not issues:
        return {}
    bindings = sealed.value["bindings"]
    preview_ref = bindings.get("structural_preview_decision_set")
    comparison_ref = bindings.get("comparison")
    if not isinstance(preview_ref, dict) or not isinstance(comparison_ref, dict):
        raise StructuralRoleIssueError("structural source bindings are missing")
    preview_path = Path(binding_root) / preview_ref["path"]
    if preview_path.name != "decision_set.json":
        raise StructuralRoleIssueError("structural preview must bind its decision set")
    checked = load_structural_preview(Path(run_root), preview_path.parent)
    if ((Path(binding_root) / comparison_ref["path"]).resolve() != checked["paths"]["comparison"].resolve()
            or comparison != checked["comparison"]):
        raise StructuralRoleIssueError("structural comparison differs from sealed archive")
    if set(decisions) != set(checked["decisions"]) or packets != checked["packets"]:
        raise StructuralRoleIssueError("structural current page domain or packets differ from archive")
    from kb_creator.scripts.audit_mineru_ai_merge_fidelity import _v3_page_context
    fresh_mappings = {}
    linguistic_ledger_context: dict[Path, tuple[dict[str, Any], dict[str, Any]]] = {}
    for page in {issue["source_page"] for issue in issues}:
        errors: list[str] = []
        context = _v3_page_context(page, packets[page], decisions[page], checked["geometry"], errors)
        if errors:
            raise StructuralRoleIssueError("structural current reader mapping failed: " + "; ".join(errors))
        fresh_mappings[page] = context["mappings"]
    run = json.loads((Path(run_root) / "run.json").read_text(encoding="utf-8"))
    source_sha = run.get("source", {}).get("sha256")
    declared: dict[tuple[int, str, int, str], Mapping[str, Any]] = {}
    for issue in issues:
        validate_structural_issue(issue)
        if issue.get("source_pdf_sha256") != source_sha:
            raise StructuralRoleIssueError("structural issue source PDF differs from run")
        page, key = issue.get("source_page"), selected_source_key(issue)
        if type(page) is not int or key is None or page not in decisions or page not in packets:
            raise StructuralRoleIssueError("structural issue page or source key is absent")
        audit_mapping = _audit_mapping(stage05_pages, page, key, ledger_context=linguistic_ledger_context)
        mappings = [row for row in fresh_mappings[page]
                    if (row["unit"]["view_id"], row["unit"]["raw_index"]) == key]
        if (len(mappings) != 1 or mappings[0].get("unit") != audit_mapping.get("unit")
                or mappings[0].get("markdown_span") != audit_mapping.get("markdown_span")):
            raise StructuralRoleIssueError("structural Stage05 mapping differs from fresh source proof")
        for row in issue["source_selector"][SELECTOR_KEY]["comparison_records"]:
            locator = (page, row["pair_name"], row["semantic_conflict_index"], row["record_sha256"])
            if locator in declared:
                raise StructuralRoleIssueError("structural comparison record has duplicate ownership")
            declared[locator] = issue
    expected = {}
    for page, conflict, units in pending_structural_conflicts(checked["decisions"], checked["packets"],
            checked["comparison"], checked["reference_proof_keys"], checked["split_structure_proof_keys"],
            checked["visual_assertions"]):
        if len(units) != 1:
            raise StructuralRoleIssueError("preview conflict has ambiguous source ownership")
        expected[structural_conflict_locator(page, conflict)] = units[0]
    if set(declared) != set(expected):
        raise StructuralRoleIssueError("structural issues do not exactly cover unresolved preview conflicts")
    actual: dict[tuple[int, str, int, str], tuple[Mapping[str, Any], Mapping[str, Any]]] = {}
    for page, decision in decisions.items():
        selected = _selected(decision, packets[page])
        for conflict, units in _selected_conflicts(dict(comparison), selected):
            locator = structural_conflict_locator(page, conflict)
            if locator in actual:
                raise StructuralRoleIssueError("comparison conflict locator is not unique")
            actual[locator] = (conflict, units[0])
    proofs: dict[tuple[int, str, int, str], dict[str, Any]] = {}
    for locator, issue in declared.items():
        found = actual.get(locator)
        if found is None:
            raise StructuralRoleIssueError("structural comparison locator is stale or absent")
        conflict, selected = found
        key = selected_source_key(issue)
        original = expected[locator]
        if ((selected.get("view"), selected.get("raw_index")) != key
                or (original.get("view"), original.get("raw_index")) != key):
            raise StructuralRoleIssueError("structural issue does not own selected conflict occurrence")
        selector = issue["source_selector"][SELECTOR_KEY]
        if (selected.get("block", {}).get("_selection_purpose") != selector["provisional_selection_purpose"]
                or original.get("block", {}).get("_selection_purpose") != selector["provisional_selection_purpose"]
                or selected.get("block", {}).get("type") != selector["provisional_block_type"]):
            raise StructuralRoleIssueError("structural issue provisional role changed")
        excerpt = selected.get("block", {}).get("text")
        if not isinstance(excerpt, str) or excerpt != issue.get("source_excerpt_en") or sha256_bytes(excerpt.encode()) != issue.get("source_excerpt_sha256"):
            raise StructuralRoleIssueError("structural issue source excerpt differs")
        proofs[locator] = {"issue_id": issue["issue_id"], "selected_source_key": {"view": key[0], "raw_index": key[1]}}
    # Every selected unresolved conflict must either be explicitly resolved by
    # the normal Stage06 proof path or supplied to Stage06 for exact handling.
    # This function returns only declared issue proof; Stage06 makes the final
    # resolved-or-covered decision for each conflict.
    return proofs
