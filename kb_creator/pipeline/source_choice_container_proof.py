"""Re-derive complete composite proof rows from an already verified v2 ledger."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping

from .identity import canonical_bytes, file_identity, sha256_bytes
from .semantic_structure import _normalized, apply_block_boundaries
from .source_choice_slice import SourceSlice, apply_sealed_slices
from .structural_projection import (project_interval, project_structural_page,
                                    retained_assertion_key, validate_ornament_source,
                                    validate_retained_owner_projection)


def _digest(text: str) -> str:
    return sha256_bytes(text.encode("utf-8"))


def _open(record: Mapping[str, Any], root: Path | None = None) -> tuple[Path, dict]:
    if not isinstance(record, Mapping) or set(record) != {"path", "bytes", "sha256"}:
        raise ValueError("container authority record is malformed")
    path = Path(record["path"])
    if root is not None:
        path = root / path
    if not path.is_file() or file_identity(path) != {k: record[k] for k in ("bytes", "sha256")}:
        raise ValueError("container authority identity drift")
    return path.resolve(), json.loads(path.read_text(encoding="utf-8"))


def open_structural_projection_context(*, input_path: Path, binding_root: Path) -> dict[str, Any] | None:
    """Reopen a sealed structural successor and its complete edit authority."""
    from .review_draft_preparation import validate_review_draft_author_input
    from .review_draft import validate_review_draft_evidence

    input_path, binding_root = Path(input_path).resolve(), Path(binding_root).resolve()
    validate_review_draft_author_input(input_path=input_path, binding_root=binding_root)
    value = json.loads(input_path.read_text(encoding="utf-8"))
    bindings = value["bindings"]
    names = {"structural_predecessor_input", "structural_predecessor_evidence", "structural_edits"}
    present = names & set(bindings)
    if not present:
        return None
    if present != names or not input_path.is_relative_to(binding_root):
        raise ValueError("structural projection binding domain is incomplete")
    paths = {name: _open(bindings[name], binding_root) for name in names}
    predecessor_path, predecessor = paths["structural_predecessor_input"]
    evidence_path, evidence = paths["structural_predecessor_evidence"]
    edits_path, edits = paths["structural_edits"]
    validate_review_draft_author_input(input_path=predecessor_path, binding_root=binding_root)
    validate_review_draft_evidence(evidence)
    if evidence["input_sha256"] != predecessor["input_sha256"]:
        raise ValueError("structural predecessor evidence does not bind its input")
    if "decision_set" not in evidence["authored"]:
        raise ValueError("structural predecessor evidence lacks a decision set")
    for identity in evidence["authored"].values():
        path = (evidence_path.parent / identity["path"]).resolve()
        if (not path.is_relative_to(evidence_path.parent) or not path.is_file()
                or file_identity(path) != {key: identity[key] for key in ("bytes", "sha256")}):
            raise ValueError("structural predecessor authored identity is stale")
    if (edits.get("schema") != "kb_creator.review_draft_structural_successor.v1"
            or set(edits) != {"schema", "predecessor_input", "predecessor_evidence", "source_marker_dispositions",
                                  "structural_post_patches", "retained_owner_assertions", "page_units"}
            or edits.get("predecessor_input") != {"path": predecessor_path.name, **file_identity(predecessor_path)}
            or edits.get("predecessor_evidence") != {"path": evidence_path.name, **file_identity(evidence_path)}):
        raise ValueError("structural projection edits are stale or malformed")
    sidecar_record = edits.get("source_marker_dispositions")
    sidecar_path, sidecar = _open(sidecar_record, edits_path.parent)
    if sidecar_path.parent != edits_path.parent or sidecar.get("schema") != "kb_creator.source_marker_dispositions.v1":
        raise ValueError("structural projection marker sidecar is foreign")
    rows = edits.get("structural_post_patches")
    if not isinstance(rows, list) or not isinstance(sidecar.get("candidates"), list) or not isinstance(sidecar.get("dispositions"), list):
        raise ValueError("structural projection edit domain is malformed")
    by_page: dict[int, list[dict[str, Any]]] = {}
    for row in rows:
        if (not isinstance(row, dict) or set(row) != {"source_page", "patches"}
                or type(row["source_page"]) is not int or row["source_page"] in by_page
                or not isinstance(row["patches"], list)):
            raise ValueError("structural projection patch domain is malformed")
        by_page[row["source_page"]] = row["patches"]
    candidates = {(item["source_page"], item["view"], item["raw_index"])
                  for item in sidecar["candidates"]}
    dispositions = {(item["source_page"], item["view"], item["raw_index"]): item["disposition"]
                    for item in sidecar["dispositions"]}
    if len(candidates) != len(sidecar["candidates"]) or len(dispositions) != len(sidecar["dispositions"]) or candidates != set(dispositions):
        raise ValueError("structural projection marker domain is incomplete")
    run_record = predecessor["bindings"].get("candidate_manifest")
    if run_record is None:
        raise ValueError("structural projection lacks replay manifest")
    manifest_path, manifest = _open(run_record, binding_root)
    run_root = Path(manifest["run_root"]).resolve()
    selected_by_page: dict[int, set[tuple[str, int]]] = {}
    predecessor_pages: dict[int, dict[str, Any]] = {}
    packet_cache: dict[int, dict[str, Any]] = {}
    def predecessor_page(page: int) -> dict[str, Any]:
        if page not in predecessor_pages:
            decision_path = evidence_path.parent / "pages" / f"page-{page:03d}.json"
            decision_set_path, decision_set = _open(evidence["authored"]["decision_set"], evidence_path.parent)
            records = [item for item in decision_set["decisions"] if item.get("source_page") == page]
            if len(records) != 1 or records[0].get("path") != f"pages/page-{page:03d}.json" or file_identity(decision_path) != {key: records[0][key] for key in ("bytes", "sha256")}:
                raise ValueError("structural projection predecessor page identity is stale")
            predecessor_pages[page] = json.loads(decision_path.read_text(encoding="utf-8"))
            selected_by_page[page] = {(item["view"], item["raw_index"]) for item in predecessor_pages[page]["selected_blocks"]
                                      if item.get("purpose") != "asset"}
        return predecessor_pages[page]
    def packet(page: int) -> dict[str, Any]:
        if page not in packet_cache:
            packet_cache[page] = json.loads((run_root / f"outputs/04-visual-merge-bundle/merge_packets/pages/page-{page:03d}.json").read_text(encoding="utf-8"))
        return packet_cache[page]
    from .source_marker_dispositions import _closed_occurrence
    for candidate in sidecar["candidates"]:
        _closed_occurrence(candidate, disposition=False)
        page, view, raw = candidate["source_page"], candidate["view"], candidate["raw_index"]
        decision = predecessor_page(page)
        blocks = packet(page).get("views", {}).get(view, {}).get("blocks", [])
        found = [block for block in blocks if block.get("raw_index") == raw]
        if (len(found) != 1 or not isinstance(found[0].get("text"), str)
                or _digest(found[0]["text"]) != candidate["reader_preimage_sha256"]
                or (view, raw) not in selected_by_page[page]
                or decision.get("semantic_structure", {}).get("review", {}).get("visual") != candidate["visual"]):
            raise ValueError("structural projection marker candidate is stale or foreign")
    for disposition in sidecar["dispositions"]:
        _closed_occurrence(disposition, disposition=True)
        candidate = next(item for item in sidecar["candidates"] if (item["source_page"], item["view"], item["raw_index"])
                         == (disposition["source_page"], disposition["view"], disposition["raw_index"]))
        if any(disposition[key] != candidate[key] for key in candidate):
            raise ValueError("structural projection disposition identity differs from candidate")
    patch_keys: set[tuple[int, str, int]] = set()
    for page, patches in by_page.items():
        predecessor_page(page)
        for patch in patches:
            if not isinstance(patch, dict) or not isinstance(patch.get("source_occurrences"), list) or not patch["source_occurrences"]:
                raise ValueError("structural projection patch is malformed")
            for item in patch["source_occurrences"]:
                key = (page, item["view"], item["raw_index"])
                blocks = packet(page).get("views", {}).get(item["view"], {}).get("blocks", [])
                found = [block for block in blocks if block.get("raw_index") == item["raw_index"]]
                if (key in patch_keys or len(found) != 1 or not isinstance(found[0].get("text"), str)
                        or (item["view"], item["raw_index"]) not in selected_by_page[page]
                        or _digest(found[0]["text"]) != item["source_text_sha256"]):
                    raise ValueError("structural projection source occurrence is stale or foreign")
                patch_keys.add(key)
            selected_order = {(item["view"], item["raw_index"]): index
                              for index, item in enumerate(predecessor_pages[page]["selected_blocks"])
                              if item.get("purpose") != "asset"}
            positions = [selected_order[(item["view"], item["raw_index"])]
                         for item in patch["source_occurrences"]]
            if positions != sorted(positions):
                raise ValueError("structural projection source occurrences are out of order")
    list_keys = {key for key, value in dispositions.items() if value == "unordered_list_item"}
    non_list_keys = {key for key, value in dispositions.items() if value == "non_list"}
    if (not list_keys <= patch_keys or patch_keys & non_list_keys
            or any(not {(page, item["view"], item["raw_index"]) for item in patch["source_occurrences"]} & list_keys
                   for page, patches in by_page.items() for patch in patches)):
        raise ValueError("structural projection marker domain differs from patches")
    assertions = edits.get("retained_owner_assertions")
    if not isinstance(assertions, list):
        raise ValueError("structural projection retained assertions are malformed")
    retained_keys: set[tuple[int, str, int]] = set()
    retained_owners: set[tuple[int, str]] = set()
    for assertion in assertions:
        page, view, raw = retained_assertion_key(assertion)
        if (page, view, raw) in retained_keys or (page, assertion["owner_id"]) in retained_owners:
            raise ValueError("structural projection retained assertion is duplicated")
        retained_keys.add((page, view, raw))
        retained_owners.add((page, assertion["owner_id"]))
        decision = predecessor_page(page)
        blocks = packet(page).get("views", {}).get(view, {}).get("blocks", [])
        found = [block for block in blocks if block.get("raw_index") == raw]
        owners = [unit for unit in decision["semantic_structure"]["units"] if unit.get("id") == assertion["owner_id"]
                  and unit.get("kind") == "list" and unit.get("representation") == "unordered_list"
                  and {"view": view, "raw_index": raw} in unit.get("source_blocks", [])]
        if (len(found) != 1 or _digest(found[0]["text"]).upper() != assertion["source_text_sha256"].upper()
                or (view, raw) not in selected_by_page[page] or len(owners) != 1):
            raise ValueError("structural projection retained owner is stale or changed")
        supporting_patches = [patch for patch in by_page.get(page, [])
                              if any((item["view"], item["raw_index"]) == (view, raw)
                                     for item in patch["source_occurrences"])]
        for patch in supporting_patches:
            interval_map = patch.get("interval_map")
            segments = interval_map.get("segments", []) if isinstance(interval_map, dict) else []
            retained_segments = [index for index, segment in enumerate(segments) if isinstance(segment, dict)
                                 and segment.get("kind") == "copy" and {"view": view, "raw_index": raw}
                                 in segment.get("source_occurrences", [])]
            if (not retained_segments or any(index > 0 and segments[index - 1].get("kind") == "literal"
                                             for index in retained_segments)):
                raise ValueError("structural projection retained owner receives a marker")
        predecessor_spec_prefix = ("source_choice_successor_spec-" if any(name.startswith("source_choice_successor_spec-") for name in predecessor["bindings"])
                                   else "input_")
        predecessor_spec_records = [record for name, record in sorted(predecessor["bindings"].items())
                                    if name.startswith(predecessor_spec_prefix)]
        previous_units = [unit for _, spec in (_open(record, binding_root) for record in predecessor_spec_records)
                          for page_spec in spec.get("pages", []) if page_spec.get("source_page") == page
                          for unit in page_spec.get("units", []) if unit.get("id") == assertion["owner_id"]]
        new_units = [unit for row in edits["page_units"] if row.get("source_page") == page
                     for unit in row.get("units", []) if unit.get("id") == assertion["owner_id"]]
        if len(previous_units) != 1 or len(new_units) != 1:
            raise ValueError("structural projection retained owner unit is missing or changed")
        validate_retained_owner_projection(
            assertion=assertion, owner=owners[0], predecessor_definition=previous_units[0],
            successor_definition=new_units[0], predecessor_markdown=decision["markdown"],
            effective_markdown=apply_block_boundaries(decision["markdown"], decision.get("block_boundaries")),
            default_view=decision.get("overlay_preference"), patches=by_page.get(page, []))
    unit_rows = edits["page_units"]
    if not isinstance(unit_rows, list) or any(not isinstance(row, dict) or set(row) != {"source_page", "units"}
                                               or type(row["source_page"]) is not int or not isinstance(row["units"], list)
                                               for row in unit_rows):
        raise ValueError("structural projection unit domain is malformed")
    units_by_page = {row["source_page"]: row["units"] for row in unit_rows}
    if len(units_by_page) != len(unit_rows) or not set(by_page) <= set(units_by_page):
        raise ValueError("structural projection unit domain is incomplete")
    predecessor_spec_prefix = ("source_choice_successor_spec-" if any(
        name.startswith("source_choice_successor_spec-") for name in predecessor["bindings"]) else "input_")
    predecessor_spec_records = [record for name, record in sorted(predecessor["bindings"].items())
                                if name.startswith(predecessor_spec_prefix)]
    predecessor_specs = [_open(record, binding_root)[1] for record in predecessor_spec_records]
    required_retained = {(page, unit["id"])
                         for spec in predecessor_specs
                         for page_spec in spec.get("pages", [])
                         for page in units_by_page if page_spec.get("source_page") == page
                         for unit in page_spec.get("units", [])
                         if unit.get("kind") == "list" and unit.get("representation") == "unordered_list"}
    if required_retained != retained_owners:
        raise ValueError("structural projection retained assertion domain is incomplete or foreign")
    def source_text(page: int, view: str, raw_index: int) -> str:
        blocks = packet(page)["views"][view]["blocks"]
        return next(block["text"] for block in blocks if block["raw_index"] == raw_index)
    for page, patches in by_page.items():
        current = predecessor_page(page)["markdown"]
        for patch in patches:
            validate_ornament_source(patch, page, list_keys, source_text, current)
            current, _ = project_structural_page(current, [patch])
    for page in set(by_page) | set(units_by_page):
        patches = by_page.get(page, [])
        spec_prefix = ("source_choice_successor_spec-" if any(name.startswith("source_choice_successor_spec-") for name in bindings)
                       else "input_")
        spec_records = [record for name, record in sorted(bindings.items()) if name.startswith(spec_prefix)]
        if not spec_records:
            raise ValueError("structural projection lacks bound author specs")
        opened_specs = [_open(record, binding_root) for record in spec_records]
        for spec_path, spec in opened_specs:
            marker_binding = spec.get("source_marker_dispositions")
            if marker_binding is None:
                raise ValueError("structural projection author spec lacks marker authority")
            from .source_marker_dispositions import load_bound_inputs
            loaded_markers = load_bound_inputs([spec_path])
            if len(loaded_markers) != 1:
                raise ValueError("structural projection author marker domain is incomplete")
            bound_marker_path = loaded_markers[0]["path"]
            if file_identity(bound_marker_path) != file_identity(sidecar_path):
                raise ValueError("structural projection author marker differs from sealed edits")
        spec_rows = [row for _, spec in opened_specs for row in spec.get("pages", [])
                     if row.get("source_page") == page]
        projection = [{key: patch[key] for key in ("before", "after", "count")} for patch in patches]
        if (len(spec_rows) != 1 or (patches and spec_rows[0].get("structural_post_patches") != projection)
                or (not patches and spec_rows[0].get("structural_post_patches"))
                or spec_rows[0].get("units") != units_by_page[page]):
            raise ValueError("structural projection author spec differs from sealed edits")
        project_structural_page(predecessor_page(page)["markdown"], patches)
    return {"authority": {"input": {"path": str(input_path), **file_identity(input_path)},
                           "binding_root": str(binding_root)}, "pages": by_page,
            "predecessor_pages": predecessor_pages, "input_sha256": value["input_sha256"]}


def derive_container_proof(*, ledger_record: Mapping[str, Any], ledger: Mapping[str, Any],
                           verified: Mapping[str, Any], page: int, key: tuple[str, int],
                           current_markdown: str | None = None,
                           current_mapping: Mapping[str, Any] | None = None,
                           structural_context: Mapping[str, Any] | None = None) -> dict:
    """Replay exact page and container intervals; never discover them by text search.

    The caller verifies the ledger once per operation. This function reopens its
    queue and predecessor evidence, and is shared by producer and consumer so a
    self-consistent forged output cannot replace the sealed source authority.
    """
    if type(page) is not int or page < 1:
        raise ValueError("container source page is malformed")
    queue_path, queue = _open(ledger["queue"])
    if queue_path != Path(verified["queue"]).resolve():
        raise ValueError("container verified queue differs")
    master_root = Path(queue["review_master"]["path"]).parent
    by_issue = {r["issue_id"]: r for r in queue["choices"]}
    page_choices = [r for r in ledger["source_choices"]
                    if r.get("disposition") == "selected_alternative"
                    and by_issue[r["issue_id"]]["source_page"] == page]
    anchor = {"view": key[0], "raw_index": key[1], "field": "text"}
    group = [r for r in page_choices if r["raw_reader_replay"].get("anchor_source_locator") == anchor]
    if not group or any(r["raw_reader_replay"].get("anchor_mode") != "composite_source_slice_v1" for r in group):
        raise ValueError("container choices are absent or mix direct/composite modes")
    group.sort(key=lambda r: (r["raw_reader_replay"]["raw_source_slice"]["raw_character_start"],
                             r["raw_reader_replay"]["raw_source_slice"]["raw_character_end"], r["issue_id"]))
    if len({r["issue_id"] for r in group}) != len(group):
        raise ValueError("container choice is duplicated")
    replay = group[0]["raw_reader_replay"]
    _, predecessor = _open(replay["decision"], master_root)
    markdown = predecessor["markdown"]
    if predecessor.get("source_page") != page:
        raise ValueError("container predecessor page differs")
    for choice in page_choices:
        if choice["raw_reader_replay"]["decision"] != replay["decision"]:
            raise ValueError("container page choices disagree on predecessor")
        span = choice["r0_reader_span"]
        if span.get("decision_markdown_sha256") != _digest(markdown):
            raise ValueError("container predecessor page hash differs")
    unit_id = replay["semantic_unit_id"]
    units = [r for r in predecessor.get("semantic_structure", {}).get("units", []) if r.get("id") == unit_id]
    if len(units) != 1:
        raise ValueError("container predecessor semantic unit is absent or ambiguous")
    span = units[0]["markdown_span"]
    lines = markdown.split("\n")
    low, high = span["start_line"], span["end_line"]
    if type(low) is not int or type(high) is not int or not 1 <= low <= high <= len(lines):
        raise ValueError("container predecessor semantic span is malformed")
    before = "\n".join(lines[low - 1:high])
    r0_start = sum(len(s) + 1 for s in lines[:low - 1])
    r0_end = r0_start + len(before)
    if _digest(before) != span["sha256"] or _digest(before) != replay["anchor_container_sha256"]:
        raise ValueError("container semantic text is not the exact raw container")
    evidence_path, evidence = _open(queue["final_evidence"])
    from .source_choice_translation import _stage05_pages
    stage = _stage05_pages(evidence_path, evidence)[page]
    selected_rows = [r for r in stage["ordered_proof_stream"] if r.get("kind") == "selected"
                     and (r.get("unit", {}).get("view_id"), r.get("unit", {}).get("raw_index")) == key]
    if len(selected_rows) != 1:
        raise ValueError("container predecessor selected row is absent or ambiguous")
    selected = selected_rows[0]
    selected_sha = sha256_bytes(canonical_bytes(selected))
    normalized_r0 = [len(_normalized(markdown[:r0_start])), len(_normalized(markdown[:r0_end]))]
    if (selected["markdown_span"] != normalized_r0 or selected["unit"].get("source_page") != page
            or selected["unit"].get("original_text_sha256") != _digest(before)):
        raise ValueError("container predecessor selected mapping disagrees with coordinates")
    edits = []
    for choice in page_choices:
        s = choice["r0_reader_span"]; after = choice["intended_reader_successor"]
        if after["text_sha256"] != _digest(after["text"]):
            raise ValueError("container chosen successor hash differs")
        edits.append(SourceSlice(s["character_start"], s["character_end"], s["text_sha256"], after["text"]))
    successor_page = apply_sealed_slices(markdown, edits, container_sha256=_digest(markdown))
    structural = structural_context is not None and page in structural_context["pages"]
    if structural:
        predecessor_page = structural_context["predecessor_pages"].get(page)
        if not isinstance(predecessor_page, Mapping) or predecessor_page.get("markdown") != successor_page:
            raise ValueError("structural predecessor differs from complete lexical replay")
        projected_page, origins = project_structural_page(successor_page, structural_context["pages"][page])
    else:
        projected_page, origins = successor_page, list(range(len(successor_page)))
    if current_markdown is not None and current_markdown != projected_page:
        raise ValueError("container current page differs from complete structural projection")
    raw_edits = []
    for choice in group:
        r = choice["raw_reader_replay"]; interval = r["raw_source_slice"]; s = choice["r0_reader_span"]
        if (r.get("anchor_container_sha256") != _digest(before) or r.get("semantic_unit_id") != unit_id
                or r["selected_row_proof"]["row_sha256"] != selected_sha
                or s["character_start"] != r0_start + interval["raw_character_start"]
                or s["character_end"] != r0_start + interval["raw_character_end"]
                or s["text_sha256"] != interval["raw_text_sha256"]):
            raise ValueError("container raw/page/selected-row authority differs")
        raw_edits.append(SourceSlice(interval["raw_character_start"], interval["raw_character_end"],
                                    interval["raw_text_sha256"], choice["intended_reader_successor"]["text"]))
    after = apply_sealed_slices(before, raw_edits, container_sha256=_digest(before))
    for edit, choice in zip(edits, page_choices):
        if max(edit.start, r0_start) < min(edit.end, r0_end) and choice not in group:
            raise ValueError("another choice overlaps selected container")
    r1_start = r0_start + sum(len(e.after) - (e.end - e.start) for e in edits if e.end <= r0_start)
    r1_end = r1_start + len(after)
    if successor_page[r1_start:r1_end] != after:
        raise ValueError("container raw and full-page replay disagree")
    normalized_r1 = [len(_normalized(successor_page[:r1_start])), len(_normalized(successor_page[:r1_end]))]
    current_span = project_interval(projected_page, origins, r1_start, r1_end,
                                    allow_ornament_deletion=True)
    normalized_current = [len(_normalized(projected_page[:current_span["character_start"]])),
                          len(_normalized(projected_page[:current_span["character_end"]]))]
    mapping = {"kind": "selected", "unit": selected["unit"], "markdown_span": normalized_current}
    if current_mapping is not None and current_mapping != mapping:
        raise ValueError("container current selected mapping differs from rederived source")
    witnesses = []; delta = 0
    for choice, edit in zip(group, raw_edits):
        start = r1_start + edit.start + delta; end = start + len(edit.after)
        witnesses.append({"issue_id": choice["issue_id"], "alternative_id": choice["alternative_id"],
                          "raw_reader_replay": choice["raw_reader_replay"], "r0_reader_span": choice["r0_reader_span"],
                          "r1_reader_span": {"character_start": start, "character_end": end, "text_sha256": _digest(edit.after)},
                          "r0_preimage_sha256": edit.before_sha256, "r1_text": edit.after, "r1_text_sha256": _digest(edit.after),
                          "selected_raw_locator": choice["chosen_raw_alternative"]["source_locator"],
                          "selected_raw_text_sha256": choice["chosen_raw_alternative"]["text_sha256"]})
        delta += len(edit.after) - (edit.end - edit.start)
    value = {"kind": "linguistic_source_choice_container_v1", "unit": selected["unit"], "markdown_span": normalized_current,
             "r0_container": {"source_key": {"view": key[0], "raw_index": key[1]}, "text_sha256": _digest(before),
                              "page_character_span": {"character_start": r0_start, "character_end": r0_end, "text_sha256": _digest(before)},
                              "selected_row_sha256": selected_sha},
             "r1_container": {"text": after, "text_sha256": _digest(after),
                              "page_character_span": {"character_start": r1_start, "character_end": r1_end, "text_sha256": _digest(after)},
                              "normalized_page_span": normalized_r1},
             "ledger": dict(ledger_record), "ledger_identity": verified["ledger_sha256"], "diagnostic_witnesses": witnesses}
    if structural:
        current_witnesses = []
        for witness in witnesses:
            old = witness["r1_reader_span"]
            span = project_interval(projected_page, origins, old["character_start"], old["character_end"])
            if span["text_sha256"] != witness["r1_text_sha256"]:
                raise ValueError("structural projection changes a chosen lexical witness")
            current_witnesses.append({"issue_id": witness["issue_id"], "span": span})
        value["structural_projection"] = {
            "schema": "kb_creator.source_choice_structural_projection.v1",
            "authority": structural_context["authority"],
            "lexical_page_sha256": _digest(successor_page),
            "current_page_sha256": _digest(projected_page),
            "current_container": {"text": projected_page[current_span["character_start"]:current_span["character_end"]],
                                  "text_sha256": current_span["text_sha256"],
                                  "page_character_span": current_span,
                                  "normalized_page_span": normalized_current},
            "current_witness_spans": current_witnesses,
        }
    value["row_sha256"] = sha256_bytes(canonical_bytes(value))
    return value
