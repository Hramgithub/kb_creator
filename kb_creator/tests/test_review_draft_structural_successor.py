import hashlib
import importlib.util
import json
import shutil
from copy import deepcopy
from pathlib import Path

import pytest

from kb_creator.pipeline.identity import canonical_bytes, file_identity, sha256_bytes
from kb_creator.pipeline.review_draft_preparation import prepare_review_draft_structural_successor


def _write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return path


def _composite_fixture():
    path = Path(__file__).with_name("test_source_choice_composite_integration.py")
    spec = importlib.util.spec_from_file_location("structural_composite_fixture", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _sealed_two_page_predecessor(root, *, new_item="new item", repeat_page2_raw=False):
    """A compact sealed preparation boundary with an already authored list."""
    from kb_creator.pipeline.review_draft import INPUT_SCHEMA, ISSUES_SCHEMA, finalize_review_draft_evidence

    run = root / "run"
    page2_raw = 11 if repeat_page2_raw else 20
    source_blocks = {1: [(10, new_item), (11, "retained item")], 2: [(page2_raw, "unchanged prose")]}
    for page, blocks in source_blocks.items():
        _write(run / f"outputs/04-visual-merge-bundle/merge_packets/pages/page-{page:03d}.json", {
            "views": {"original_pipeline_txt": {"blocks": [
                {"raw_index": raw, "text": value} for raw, value in blocks]}}})
    candidate_manifest = _write(root / "mechanical/mechanical_draft.json", {"run_root": str(run)})
    predecessor_root = root / "predecessor"
    retained_line = new_item.count("\n") + 2
    retained_definition = {"id": "retained", "kind": "list", "representation": "unordered_list",
                           "view": "original_pipeline_txt", "raw_indices": [11],
                           "start_line": retained_line, "end_line": retained_line, "item_count": 1}
    spec = _write(predecessor_root / "author-specs/spec-00.json", {"pages": [
        {"source_page": 1, "units": [retained_definition]},
        {"source_page": 2, "units": []}]})
    drafts = {}
    for page, text in ((1, new_item + "\n- retained item"), (2, "unchanged prose")):
        drafts[page] = _write(predecessor_root / f"draft-pages/page-{page:03d}.json", {
            "source_page": page, "markdown": text})
    def bound(path):
        return {"path": path.relative_to(root).as_posix(), **file_identity(path)}
    predecessor = {"schema": INPUT_SCHEMA, "bindings": {
        "candidate_manifest": bound(candidate_manifest), "input_00": bound(spec),
        **{f"draft_page-{page:03d}": bound(path) for page, path in drafts.items()}},
        "source_issues": {"schema": ISSUES_SCHEMA, "issues": []}, "unresolved_dispositions": []}
    predecessor["input_sha256"] = sha256_bytes(canonical_bytes(predecessor))
    predecessor_input = _write(predecessor_root / "review-draft-input.json", predecessor)

    authored = root / "authored"
    decision_paths = {}
    visual = {"path": "visual/page-001.png", "bytes": 1, "sha256": "A" * 64}
    for page, blocks in source_blocks.items():
        decision_paths[page] = _write(authored / f"pages/page-{page:03d}.json", {
            "source_page": page,
            "markdown": new_item + "\n- retained item" if page == 1 else "unchanged prose",
            "selected_blocks": [{"view": "original_pipeline_txt", "raw_index": raw, "purpose": "text"}
                                for raw, _ in blocks],
            "semantic_structure": {"review": {"visual": visual}, "units": ([{"id": "retained", "kind": "list",
                "representation": "unordered_list", "source_blocks": [
                    {"view": "original_pipeline_txt", "raw_index": 11}],
                "markdown_span": {"start_line": retained_line, "end_line": retained_line,
                    "sha256": sha256_bytes(b"- retained item")},
                "container_parent": None, "semantic_parent": None, "continuation_of": None,
                "heading_level": None, "item_count": 1}] if page == 1 else [])}})
    decision_set = _write(authored / "decision_set.json", {"decisions": [
        {"source_page": page, "path": f"pages/page-{page:03d}.json", **file_identity(path)}
        for page, path in decision_paths.items()]})
    evidence = finalize_review_draft_evidence(predecessor, authored={"decision_set": {
        "path": decision_set.name, **file_identity(decision_set)}},
        audit={"passed": True, "errors": []}, visual_reviewed_false_pages=[])
    evidence_path = _write(authored / "review-draft-evidence.json", evidence)
    candidate = {"source_page": 1, "view": "original_pipeline_txt", "raw_index": 10,
                 "reader_preimage_sha256": sha256_bytes(new_item.encode()), "visual": visual}
    candidates = [candidate]
    if repeat_page2_raw:
        candidates.append({"source_page": 2, "view": "original_pipeline_txt", "raw_index": page2_raw,
                           "reader_preimage_sha256": sha256_bytes(b"unchanged prose"), "visual": visual})
    sidecar = _write(root / "edits/marker-dispositions.json", {
        "schema": "kb_creator.source_marker_dispositions.v1", "candidates": candidates,
        "dispositions": [{**row, "disposition": "unordered_list_item", "rationale": "Reviewed bullet."}
                         for row in candidates]})
    before, after = new_item, "- " + new_item
    edits = {"schema": "kb_creator.review_draft_structural_successor.v1",
             "predecessor_input": {"path": predecessor_input.name, **file_identity(predecessor_input)},
             "predecessor_evidence": {"path": evidence_path.name, **file_identity(evidence_path)},
             "source_marker_dispositions": {"path": sidecar.name, **file_identity(sidecar)},
             "structural_post_patches": [{"source_page": 1, "patches": [{
                 "source_occurrences": [{"view": "original_pipeline_txt", "raw_index": 10,
                                         "source_text_sha256": sha256_bytes(before.encode())}],
                 "before": before, "before_sha256": sha256_bytes(before.encode()),
                 "after": after, "after_sha256": sha256_bytes(after.encode()), "count": 1}]}],
             "retained_owner_assertions": [{"source_page": 1, "view": "original_pipeline_txt", "raw_index": 11,
                 "source_text_sha256": sha256_bytes(b"retained item"), "owner_id": "retained",
                 "representation": "unordered_list", "visual_group_id": "group-1"}],
             "page_units": [{"source_page": 1, "units": [
                 {"id": "new", "kind": "list", "representation": "unordered_list", "item_count": 1},
                 deepcopy(retained_definition)]}]}
    if repeat_page2_raw:
        second = "unchanged prose"
        edits["structural_post_patches"].append({"source_page": 2, "patches": [{
            "source_occurrences": [{"view": "original_pipeline_txt", "raw_index": page2_raw,
                                    "source_text_sha256": sha256_bytes(second.encode())}],
            "before": second, "before_sha256": sha256_bytes(second.encode()),
            "after": "- " + second, "after_sha256": sha256_bytes(("- " + second).encode()),
            "count": 1}]})
        edits["page_units"].append({"source_page": 2, "units": [{
            "id": "new-page2", "kind": "list", "representation": "unordered_list", "item_count": 1}]})
    edits_path = _write(root / "edits/edits.json", edits)
    return predecessor_input, authored, edits_path


def test_retained_owner_and_unaffected_second_page_are_preserved(tmp_path):
    predecessor_input, authored, edits_path = _sealed_two_page_predecessor(tmp_path)
    output = tmp_path / "successor"
    result = prepare_review_draft_structural_successor(
        predecessor_input=predecessor_input, predecessor_authored=authored,
        binding_root=tmp_path, edits_path=edits_path, output_dir=output)
    assert result["affected_pages"] == [1]
    assert (output / "draft-pages/page-002.json").read_bytes() == (
        predecessor_input.parent / "draft-pages/page-002.json").read_bytes()
    predecessor_spec = json.loads((predecessor_input.parent / "author-specs/spec-00.json").read_text(encoding="utf-8"))
    successor_spec = json.loads((output / "author-specs/spec-00.json").read_text(encoding="utf-8"))
    assert successor_spec["pages"][1] == predecessor_spec["pages"][1]
    assert successor_spec["pages"][0]["units"][1] == predecessor_spec["pages"][0]["units"][0]
    assert successor_spec["pages"][0]["structural_post_patches"] == [
        {"before": "new item", "after": "- new item", "count": 1}]


def test_repeated_raw_index_on_another_page_does_not_mark_retained_owner(tmp_path):
    from kb_creator.pipeline.source_choice_container_proof import open_structural_projection_context

    predecessor_input, authored, edits_path = _sealed_two_page_predecessor(
        tmp_path, repeat_page2_raw=True)
    result = prepare_review_draft_structural_successor(
        predecessor_input=predecessor_input, predecessor_authored=authored,
        binding_root=tmp_path, edits_path=edits_path, output_dir=tmp_path / "successor")
    assert result["affected_pages"] == [1, 2]
    context = open_structural_projection_context(
        input_path=Path(result["input"]["path"]), binding_root=tmp_path)
    assert set(context["pages"]) == {1, 2}


def _ornament_interval_patch(edits_path, before, removed_at):
    edits = json.loads(edits_path.read_text(encoding="utf-8"))
    patch = edits["structural_post_patches"][0]["patches"][0]
    key = {"view": "original_pipeline_txt", "raw_index": 10}
    after = "- " + before[:removed_at] + before[removed_at + 1:]
    segments = [{"kind": "literal", "text": "- ", "sha256": sha256_bytes(b"- ")}]
    if removed_at:
        segments.append({"kind": "copy", "start": 0, "end": removed_at,
                         "sha256": sha256_bytes(before[:removed_at].encode()), "source_occurrences": [key]})
    segments.append({"kind": "copy", "start": removed_at + 1, "end": len(before),
                     "sha256": sha256_bytes(before[removed_at + 1:].encode()),
                     "source_occurrences": [key]})
    patch.update(before=before, before_sha256=sha256_bytes(before.encode()),
                 after=after, after_sha256=sha256_bytes(after.encode()), interval_map={
        "segments": segments, "removed_intervals": [{"start": removed_at, "end": removed_at + 1,
        "sha256": sha256_bytes(before[removed_at].encode()), "reason": "reviewed_ornament",
        "source_occurrence": key}]})
    _write(edits_path, edits)


def _sliced_ornament_patch(edits_path, before, *, interval):
    if interval:
        _ornament_interval_patch(edits_path, before, 0)
        return
    edits = json.loads(edits_path.read_text(encoding="utf-8"))
    patch = edits["structural_post_patches"][0]["patches"][0]
    after = "-" + before[1:]
    patch.update(before=before, before_sha256=sha256_bytes(before.encode()),
                 after=after, after_sha256=sha256_bytes(after.encode()))
    patch.pop("interval_map", None)
    _write(edits_path, edits)


def _reseal_sliced_successor(successor_input, edits_path, root):
    successor = json.loads(successor_input.read_text(encoding="utf-8"))
    successor["bindings"]["structural_edits"].update(file_identity(edits_path))
    spec_path = root / "successor/author-specs/spec-00.json"
    spec = json.loads(spec_path.read_text(encoding="utf-8"))
    altered_patch = json.loads(edits_path.read_text(encoding="utf-8"))["structural_post_patches"][0]["patches"][0]
    spec["pages"][0]["structural_post_patches"][0].update(
        before=altered_patch["before"], after=altered_patch["after"])
    _write(spec_path, spec)
    successor["bindings"]["input_00"].update(file_identity(spec_path))
    draft_path = root / "successor/draft-pages/page-001.json"
    draft = json.loads(draft_path.read_text(encoding="utf-8"))
    old_before = json.loads((root / "predecessor/draft-pages/page-001.json").read_text(encoding="utf-8"))["markdown"]
    assert old_before.count(altered_patch["before"]) == 1
    draft["markdown"] = old_before.replace(altered_patch["before"], altered_patch["after"])
    _write(draft_path, draft)
    successor["bindings"]["draft_page-001"].update(file_identity(draft_path))
    successor.pop("input_sha256")
    successor["input_sha256"] = sha256_bytes(canonical_bytes(successor))
    _write(successor_input, successor)


@pytest.mark.parametrize("ornament", "HUT")
@pytest.mark.parametrize("interval,later_line", [(False, False), (True, False),
                                                   (False, True), (True, True)])
def test_sliced_source_ornament_rejected_by_producer_and_reopener(
        tmp_path, ornament, interval, later_line):
    from kb_creator.pipeline.source_choice_container_proof import open_structural_projection_context

    raw = (ornament + " lead\n" + ornament + " ID6" if later_line
           else ornament + " T" + ornament + " ID6")
    sliced = ornament + " ID6"
    predecessor_input, authored, edits_path = _sealed_two_page_predecessor(tmp_path, new_item=raw)
    _sliced_ornament_patch(edits_path, sliced, interval=interval)
    with pytest.raises(ValueError, match="position"):
        prepare_review_draft_structural_successor(
            predecessor_input=predecessor_input, predecessor_authored=authored,
            binding_root=tmp_path, edits_path=edits_path, output_dir=tmp_path / "rejected")
    assert not (tmp_path / "rejected").exists()

    valid_root = tmp_path / "valid"
    valid_input, valid_authored, valid_edits = _sealed_two_page_predecessor(
        valid_root, new_item=raw)
    if interval:
        _ornament_interval_patch(valid_edits, raw, 0)
    else:
        _sliced_ornament_patch(valid_edits, raw, interval=False)
    result = prepare_review_draft_structural_successor(
        predecessor_input=valid_input, predecessor_authored=valid_authored,
        binding_root=valid_root, edits_path=valid_edits, output_dir=valid_root / "successor")
    successor_input = Path(result["input"]["path"])
    assert open_structural_projection_context(input_path=successor_input,
                                              binding_root=valid_root) is not None
    _sliced_ornament_patch(valid_edits, sliced, interval=interval)
    _reseal_sliced_successor(successor_input, valid_edits, valid_root)
    with pytest.raises(ValueError, match="position"):
        open_structural_projection_context(input_path=successor_input,
                                           binding_root=valid_root)


@pytest.mark.parametrize("interior", "HUT")
def test_interior_ornament_rejected_by_producer_and_reopener(tmp_path, interior):
    from kb_creator.pipeline.source_choice_container_proof import open_structural_projection_context

    before = "T" + interior + "ORN ID6"
    predecessor_input, authored, edits_path = _sealed_two_page_predecessor(tmp_path, new_item=before)
    _ornament_interval_patch(edits_path, before, 1)
    with pytest.raises(ValueError, match="ornament"):
        prepare_review_draft_structural_successor(
            predecessor_input=predecessor_input, predecessor_authored=authored,
            binding_root=tmp_path, edits_path=edits_path, output_dir=tmp_path / "rejected")
    assert not (tmp_path / "rejected").exists()
    # A successfully sealed successor is tampered, then its binding is re-sealed
    # to prove the standalone consumer also applies the semantic boundary check.
    valid_before = "H T" + interior + "ORN ID6"
    valid_predecessor, valid_authored, valid_edits = _sealed_two_page_predecessor(
        tmp_path / "valid", new_item=valid_before)
    _ornament_interval_patch(valid_edits, valid_before, 0)
    result = prepare_review_draft_structural_successor(
        predecessor_input=valid_predecessor, predecessor_authored=valid_authored,
        binding_root=tmp_path / "valid", edits_path=valid_edits,
        output_dir=tmp_path / "valid/successor")
    successor_input = Path(result["input"]["path"])
    assert open_structural_projection_context(input_path=successor_input,
                                              binding_root=tmp_path / "valid") is not None
    _ornament_interval_patch(valid_edits, valid_before, 3)
    successor = json.loads(successor_input.read_text(encoding="utf-8"))
    successor["bindings"]["structural_edits"].update(file_identity(valid_edits))
    spec_path = tmp_path / "valid/successor/author-specs/spec-00.json"
    spec = json.loads(spec_path.read_text(encoding="utf-8"))
    altered_patch = json.loads(valid_edits.read_text(encoding="utf-8"))["structural_post_patches"][0]["patches"][0]
    spec["pages"][0]["structural_post_patches"][0]["after"] = altered_patch["after"]
    _write(spec_path, spec)
    successor["bindings"]["input_00"].update(file_identity(spec_path))
    draft_path = tmp_path / "valid/successor/draft-pages/page-001.json"
    draft = json.loads(draft_path.read_text(encoding="utf-8"))
    draft["markdown"] = altered_patch["after"] + "\n- retained item"
    _write(draft_path, draft)
    successor["bindings"]["draft_page-001"].update(file_identity(draft_path))
    successor.pop("input_sha256")
    successor["input_sha256"] = sha256_bytes(canonical_bytes(successor))
    _write(successor_input, successor)
    with pytest.raises(ValueError, match="ornament"):
        open_structural_projection_context(input_path=successor_input,
                                           binding_root=tmp_path / "valid")


def test_retained_owner_replacement_cannot_drop_existing_unit(tmp_path):
    predecessor_input, authored, edits_path = _sealed_two_page_predecessor(tmp_path)
    edits = json.loads(edits_path.read_text(encoding="utf-8"))
    edits["page_units"][0]["units"] = edits["page_units"][0]["units"][:1]
    _write(edits_path, edits)
    output = tmp_path / "rejected-successor"
    with pytest.raises(ValueError, match="retained owner unit is missing"):
        prepare_review_draft_structural_successor(
            predecessor_input=predecessor_input, predecessor_authored=authored,
            binding_root=tmp_path, edits_path=edits_path, output_dir=output)
    assert not output.exists()


def test_same_raw_index_in_foreign_view_cannot_bind_patch(tmp_path):
    predecessor_input, authored, edits_path = _sealed_two_page_predecessor(tmp_path)
    packet_path = tmp_path / "run/outputs/04-visual-merge-bundle/merge_packets/pages/page-001.json"
    packet = json.loads(packet_path.read_text(encoding="utf-8"))
    packet["views"]["original_pipeline_ocr"] = {"blocks": [{"raw_index": 10, "text": "new item"}]}
    _write(packet_path, packet)
    edits = json.loads(edits_path.read_text(encoding="utf-8"))
    edits["structural_post_patches"][0]["patches"][0]["source_occurrences"][0]["view"] = "original_pipeline_ocr"
    _write(edits_path, edits)
    output = tmp_path / "rejected-successor"
    with pytest.raises(ValueError, match="stale or foreign"):
        prepare_review_draft_structural_successor(
            predecessor_input=predecessor_input, predecessor_authored=authored,
            binding_root=tmp_path, edits_path=edits_path, output_dir=output)
    assert not output.exists()


def _permuted_retained_edits(edits_path, *, relocate=True):
    edits = json.loads(edits_path.read_text(encoding="utf-8"))
    patch = edits["structural_post_patches"][0]["patches"][0]
    before = "new item\n- retained item"
    after = "- retained item\n- new item"
    new_key = {"view": "original_pipeline_txt", "raw_index": 10}
    retained_key = {"view": "original_pipeline_txt", "raw_index": 11}
    patch["source_occurrences"].append({**retained_key, "source_text_sha256": sha256_bytes(b"retained item")})
    patch.update(before=before, before_sha256=sha256_bytes(before.encode()),
                 after=after, after_sha256=sha256_bytes(after.encode()))
    def copied(start, end, key):
        return {"kind": "copy", "start": start, "end": end,
                "sha256": sha256_bytes(before[start:end].encode()), "source_occurrences": [key]}
    retained_start = before.index("- retained item")
    patch["interval_map"] = {"segments": [
        copied(retained_start, len(before), retained_key),
        copied(retained_start - 1, retained_start, new_key),
        {"kind": "literal", "text": "- ", "sha256": sha256_bytes(b"- ")},
        copied(0, retained_start - 1, new_key)], "removed_intervals": []}
    if relocate:
        edits["page_units"][0]["units"][1]["start_line"] = 1
        edits["page_units"][0]["units"][1]["end_line"] = 1
    _write(edits_path, edits)


def test_whole_page_permutation_keeps_retained_owner_as_copied_source(tmp_path):
    from kb_creator.pipeline.source_choice_container_proof import open_structural_projection_context

    predecessor_input, authored, edits_path = _sealed_two_page_predecessor(tmp_path)
    _permuted_retained_edits(edits_path)
    result = prepare_review_draft_structural_successor(
        predecessor_input=predecessor_input, predecessor_authored=authored,
        binding_root=tmp_path, edits_path=edits_path, output_dir=tmp_path / "permuted")
    assert result["affected_pages"] == [1]
    spec = json.loads((tmp_path / "permuted/author-specs/spec-00.json").read_text(encoding="utf-8"))
    assert spec["pages"][0]["structural_post_patches"] == [
        {"before": "new item\n- retained item", "after": "- retained item\n- new item", "count": 1}]
    assert spec["pages"][0]["units"][1]["id"] == "retained"
    assert (spec["pages"][0]["units"][1]["start_line"],
            spec["pages"][0]["units"][1]["end_line"]) == (1, 1)
    context = open_structural_projection_context(
        input_path=Path(result["input"]["path"]), binding_root=tmp_path)
    assert context["pages"][1][0]["interval_map"]


def test_stale_retained_selector_rejected_by_producer_and_resealed_reopener(tmp_path):
    from kb_creator.pipeline.source_choice_container_proof import open_structural_projection_context

    rejected = tmp_path / "rejected"
    predecessor, authored, edits_path = _sealed_two_page_predecessor(rejected)
    _permuted_retained_edits(edits_path, relocate=False)
    with pytest.raises(ValueError, match="selector differs from projected interval"):
        prepare_review_draft_structural_successor(
            predecessor_input=predecessor, predecessor_authored=authored,
            binding_root=rejected, edits_path=edits_path, output_dir=rejected / "successor")
    assert not (rejected / "successor").exists()

    valid = tmp_path / "valid"
    predecessor, authored, edits_path = _sealed_two_page_predecessor(valid)
    _permuted_retained_edits(edits_path)
    result = prepare_review_draft_structural_successor(
        predecessor_input=predecessor, predecessor_authored=authored,
        binding_root=valid, edits_path=edits_path, output_dir=valid / "successor")
    successor_input = Path(result["input"]["path"])
    edits = json.loads(edits_path.read_text(encoding="utf-8"))
    edits["page_units"][0]["units"][1].update(start_line=2, end_line=2)
    _write(edits_path, edits)
    spec_path = valid / "successor/author-specs/spec-00.json"
    spec = json.loads(spec_path.read_text(encoding="utf-8"))
    spec["pages"][0]["units"][1].update(start_line=2, end_line=2)
    _write(spec_path, spec)
    successor = json.loads(successor_input.read_text(encoding="utf-8"))
    successor["bindings"]["structural_edits"].update(file_identity(edits_path))
    successor["bindings"]["input_00"].update(file_identity(spec_path))
    successor.pop("input_sha256")
    successor["input_sha256"] = sha256_bytes(canonical_bytes(successor))
    _write(successor_input, successor)
    with pytest.raises(ValueError, match="selector differs from projected interval"):
        open_structural_projection_context(input_path=successor_input, binding_root=valid)


def test_resealed_equal_text_occurrence_cannot_replace_retained_origin(tmp_path):
    from kb_creator.pipeline.source_choice_container_proof import open_structural_projection_context

    line = "- retained item"
    predecessor, authored, edits_path = _sealed_two_page_predecessor(tmp_path, new_item=line)
    edits = json.loads(edits_path.read_text(encoding="utf-8"))
    patch = edits["structural_post_patches"][0]["patches"][0]
    before = line + "\n" + line
    new_key = {"view": "original_pipeline_txt", "raw_index": 10}
    retained_key = {"view": "original_pipeline_txt", "raw_index": 11}
    patch["source_occurrences"].append({**retained_key, "source_text_sha256": sha256_bytes(b"retained item")})
    patch.update(before=before, before_sha256=sha256_bytes(before.encode()),
                 after=before, after_sha256=sha256_bytes(before.encode()),
                 interval_map={"segments": [
                     {"kind": "copy", "start": len(line) + 1, "end": len(before),
                      "sha256": sha256_bytes(line.encode()), "source_occurrences": [retained_key]},
                     {"kind": "copy", "start": len(line), "end": len(line) + 1,
                      "sha256": sha256_bytes(b"\n"), "source_occurrences": [new_key]},
                     {"kind": "copy", "start": 0, "end": len(line),
                      "sha256": sha256_bytes(line.encode()), "source_occurrences": [new_key]}],
                     "removed_intervals": []})
    edits["page_units"][0]["units"][1].update(start_line=1, end_line=1)
    _write(edits_path, edits)
    result = prepare_review_draft_structural_successor(
        predecessor_input=predecessor, predecessor_authored=authored,
        binding_root=tmp_path, edits_path=edits_path, output_dir=tmp_path / "successor")
    successor_input = Path(result["input"]["path"])
    assert open_structural_projection_context(input_path=successor_input, binding_root=tmp_path)
    edits["page_units"][0]["units"][1].update(start_line=2, end_line=2)
    _write(edits_path, edits)
    spec_path = tmp_path / "successor/author-specs/spec-00.json"
    spec = json.loads(spec_path.read_text(encoding="utf-8"))
    spec["pages"][0]["units"][1].update(start_line=2, end_line=2)
    _write(spec_path, spec)
    successor = json.loads(successor_input.read_text(encoding="utf-8"))
    successor["bindings"]["structural_edits"].update(file_identity(edits_path))
    successor["bindings"]["input_00"].update(file_identity(spec_path))
    successor.pop("input_sha256")
    successor["input_sha256"] = sha256_bytes(canonical_bytes(successor))
    _write(successor_input, successor)
    with pytest.raises(ValueError, match="selector differs from projected interval"):
        open_structural_projection_context(input_path=successor_input, binding_root=tmp_path)


def test_relocated_retained_list_reaches_author_and_final_verifier(tmp_path, monkeypatch):
    from kb_creator.pipeline import source_choice_translation as choices
    from kb_creator.pipeline.source_choice_successor_preparation import prepare_source_choice_successor
    from kb_creator.pipeline.review_draft_materialization import verify_final_review_draft
    from kb_creator.scripts import author_reviewed_semantic_decisions as author

    fixture = _composite_fixture()
    renderer = shutil.which("pdftoppm")
    assert renderer is not None
    monkeypatch.setenv("KB_CREATOR_PDFTOPPM", renderer)
    built = fixture._build_r0(tmp_path, monkeypatch, whole_block_correction=True,
                              retained_strong=True)
    # Author the retained list before R1 so its marker is part of the genuine
    # predecessor semantic span, rather than a post-R1 patch in the test.
    r0_spec_path = built["spec_paths"][0]
    r0_spec = json.loads(r0_spec_path.read_text(encoding="utf-8"))
    r0_page = r0_spec["pages"][0]
    r0_page["post_patches"][0]["after"] = "- Seed. Retained continuation **INT**."
    r0_page["post_patches"][1]["after"] = "- Good second paragraph."
    r0_page["reviewed_prose_bindings_v1"] = []
    first_definition = {"id": "first-list", "kind": "list", "representation": "unordered_list",
                        "view": "original_pipeline_txt", "raw_indices": [built["raws"]["original_pipeline_txt"][0]],
                        "start_line": 1, "end_line": 1, "item_count": 1}
    retained_definition = {"id": "retained", "kind": "list", "representation": "unordered_list",
                           "view": "original_pipeline_txt", "raw_indices": [built["raws"]["original_pipeline_txt"][1]],
                           "start_line": 3, "end_line": 3, "item_count": 1}
    r0_page["units"] = [first_definition, retained_definition]
    _write(r0_spec_path, r0_spec)
    r0_input = json.loads(built["r0_input"].read_text(encoding="utf-8"))
    r0_input["bindings"]["input_00"].update(file_identity(r0_spec_path))
    r0_input.pop("input_sha256")
    r0_input["input_sha256"] = sha256_bytes(canonical_bytes(r0_input))
    _write(built["r0_input"], r0_input)
    r0_authored = tmp_path / "list-r0-authored"
    author.author_drafts(built["run"], built["draft_pages"], r0_authored,
                         [r0_spec_path], mode="review_draft", draft_input=built["r0_input"],
                         binding_root=tmp_path)
    r0_decision = json.loads((r0_authored / "pages/page-001.json").read_text(encoding="utf-8"))
    assert r0_decision["semantic_structure"]["units"][1]["markdown_span"]["start_line"] == 3
    r0_descriptor = verify_final_review_draft(
        run_root=built["run"], authored_root=r0_authored, input_path=built["r0_input"],
        evidence_path=r0_authored / "review-draft-evidence.json", binding_root=tmp_path)
    materialized = tmp_path / "list-r0-materialized"
    fixture.materializer.materialize(Path(r0_descriptor["bundle_root"]), Path(r0_descriptor["raw_root"]),
        Path(r0_descriptor["decisions_root"]), materialized,
        review_draft_authority=r0_descriptor, review_draft_binding_root=tmp_path)
    master = tmp_path / "list-r0-master"
    fixture.build_review_master_en(materialized, r0_authored / "review-draft-evidence.json",
                                   master, binding_root=tmp_path)
    queue_path = Path(choices.prepare_v2(
        master, built["mechanical"], tmp_path / "queue", binding_root=tmp_path)["queue"])
    queue = json.loads(queue_path.read_text(encoding="utf-8"))
    selections = [(row["issue_id"], row["provisional_alternative_id"]) for row in queue["choices"]]
    ledger = Path(choices.record_decisions_v2(
        queue_path, fixture._submission_choices(queue_path, selections, tmp_path / "submission.json"),
        tmp_path / "ledger")["ledger"])
    r1 = prepare_source_choice_successor(
        input_path=built["r0_input"], binding_root=tmp_path, ledger_path=ledger,
        draft_pages=built["draft_pages"], spec_paths=built["spec_paths"], output_dir=tmp_path / "r1")
    predecessor_input = Path(r1["input"]["path"])
    spec_path = Path(r1["spec_paths"][0])
    spec = json.loads(spec_path.read_text(encoding="utf-8"))
    page_spec = spec["pages"][0]
    assert page_spec["units"] == [first_definition, retained_definition]
    _write(spec_path, spec)
    predecessor = json.loads(predecessor_input.read_text(encoding="utf-8"))
    predecessor["bindings"]["source_choice_successor_spec-00"].update(file_identity(spec_path))
    predecessor.pop("input_sha256")
    predecessor["input_sha256"] = sha256_bytes(canonical_bytes(predecessor))
    _write(predecessor_input, predecessor)
    authored = tmp_path / "r1-authored"
    author.author_drafts(built["run"], Path(r1["draft_pages"]), authored,
                         [spec_path], mode="review_draft", draft_input=predecessor_input,
                         binding_root=tmp_path)
    decision = json.loads((authored / "pages/page-001.json").read_text(encoding="utf-8"))
    owner = next(unit for unit in decision["semantic_structure"]["units"] if unit["id"] == "retained")
    assert owner["markdown_span"]["start_line"] == 3
    before = decision["markdown"]
    first_end = before.index("\n")
    retained_start = before.rfind("\n") + 1
    assert before[first_end:retained_start] == "\n\n"
    after = before[:first_end + 1] + before[retained_start:] + before[first_end + 1:retained_start]
    first_key = {"view": "original_pipeline_txt", "raw_index": built["raws"]["original_pipeline_txt"][0]}
    retained_key = {"view": "original_pipeline_txt", "raw_index": built["raws"]["original_pipeline_txt"][1]}
    packet = json.loads((built["run"] / "outputs/04-visual-merge-bundle/merge_packets/pages/page-001.json").read_text(encoding="utf-8"))
    def raw(key):
        return next(block["text"] for block in packet["views"][key["view"]]["blocks"]
                    if block["raw_index"] == key["raw_index"])
    visual = decision["semantic_structure"]["review"]["visual"]
    candidates = [{"source_page": 1, **key,
                   "reader_preimage_sha256": sha256_bytes(raw(key).encode("utf-8")),
                   "visual": visual} for key in (first_key, retained_key)]
    sidecar = _write(tmp_path / "edits/marker-dispositions.json", {
        "schema": "kb_creator.source_marker_dispositions.v1", "candidates": candidates,
        "dispositions": [{**candidate, "disposition": "unordered_list_item",
                          "rationale": "Synthetic retained source list."} for candidate in candidates]})
    def copied(start, end, key):
        return {"kind": "copy", "start": start, "end": end,
                "sha256": sha256_bytes(before[start:end].encode("utf-8")),
                "source_occurrences": [key]}
    patch = {"source_occurrences": [{**key, "source_text_sha256": sha256_bytes(raw(key).encode("utf-8"))}
                                    for key in (first_key, retained_key)],
             "before": before, "before_sha256": sha256_bytes(before.encode("utf-8")),
             "after": after, "after_sha256": sha256_bytes(after.encode("utf-8")), "count": 1,
             "interval_map": {"segments": [copied(0, first_end + 1, first_key),
                                           copied(retained_start, len(before), retained_key),
                                           copied(first_end + 1, retained_start, first_key)],
                              "removed_intervals": []}}
    successor_definition = {**retained_definition, "start_line": 2, "end_line": 2}
    edits = {"schema": "kb_creator.review_draft_structural_successor.v1",
             "predecessor_input": {"path": predecessor_input.name, **file_identity(predecessor_input)},
             "predecessor_evidence": {"path": "review-draft-evidence.json",
                                      **file_identity(authored / "review-draft-evidence.json")},
             "source_marker_dispositions": {"path": sidecar.name, **file_identity(sidecar)},
             "structural_post_patches": [{"source_page": 1, "patches": [patch]}],
             "retained_owner_assertions": [{"source_page": 1, **key,
                 "source_text_sha256": sha256_bytes(raw(key).encode("utf-8")),
                 "owner_id": owner_id, "representation": "unordered_list",
                 "visual_group_id": "synthetic-retained"}
                 for key, owner_id in ((first_key, "first-list"), (retained_key, "retained"))],
             "page_units": [{"source_page": 1, "units": [first_definition, successor_definition]}]}
    edits_path = _write(tmp_path / "edits/edits.json", edits)
    prepared = prepare_review_draft_structural_successor(
        predecessor_input=predecessor_input, predecessor_authored=authored,
        binding_root=tmp_path, edits_path=edits_path, output_dir=tmp_path / "structural-input")
    successor_input = Path(prepared["input"]["path"])
    final_authored = tmp_path / "structural-authored"
    author.author_drafts(built["run"], tmp_path / "structural-input/draft-pages", final_authored,
                         [tmp_path / "structural-input/author-specs/spec-00.json"],
                         mode="review_draft", draft_input=successor_input, binding_root=tmp_path)
    final_decision = json.loads((final_authored / "pages/page-001.json").read_text(encoding="utf-8"))
    final_owner = next(unit for unit in final_decision["semantic_structure"]["units"]
                       if unit["id"] == "retained")
    assert final_decision["markdown"] == after
    assert final_owner["markdown_span"]["start_line"] == 2
    assert final_owner["markdown_span"]["sha256"] == owner["markdown_span"]["sha256"]
    assert {key: value for key, value in final_owner.items() if key != "markdown_span"} == {
        key: value for key, value in owner.items() if key != "markdown_span"}
    assert final_owner["item_count"] == owner["item_count"] == 1
    final_descriptor = verify_final_review_draft(run_root=built["run"], authored_root=final_authored,
        input_path=successor_input, evidence_path=final_authored / "review-draft-evidence.json",
        binding_root=tmp_path)
    fixture.materializer.materialize(Path(final_descriptor["bundle_root"]),
        Path(final_descriptor["raw_root"]), Path(final_descriptor["decisions_root"]),
        tmp_path / "structural-materialized", review_draft_authority=final_descriptor,
        review_draft_binding_root=tmp_path)


@pytest.mark.parametrize("change", ["count", "source", "view", "representation", "parent",
                                    "extra", "presence", "missing_assertion", "duplicate_assertion"])
def test_retained_authority_changes_rejected_before_publication(tmp_path, change):
    predecessor, authored, edits_path = _sealed_two_page_predecessor(tmp_path)
    edits = json.loads(edits_path.read_text(encoding="utf-8"))
    unit = edits["page_units"][0]["units"][1]
    if change == "count": unit["item_count"] = 2
    elif change == "source": unit["raw_indices"] = [10]
    elif change == "view": unit["view"] = "raster_pipeline_ocr"
    elif change == "representation": unit["representation"] = "ordered_list"
    elif change == "parent": unit["container_parent"] = "foreign"
    elif change == "extra": unit["foreign"] = None
    elif change == "presence": unit.pop("item_count")
    elif change == "missing_assertion": edits["retained_owner_assertions"] = []
    else: edits["retained_owner_assertions"].append(deepcopy(edits["retained_owner_assertions"][0]))
    _write(edits_path, edits)
    with pytest.raises(ValueError):
        prepare_review_draft_structural_successor(
            predecessor_input=predecessor, predecessor_authored=authored,
            binding_root=tmp_path, edits_path=edits_path, output_dir=tmp_path / "rejected")
    assert not (tmp_path / "rejected").exists()


def test_resealed_reopener_rejects_missing_retained_assertion(tmp_path):
    from kb_creator.pipeline.source_choice_container_proof import open_structural_projection_context

    predecessor, authored, edits_path = _sealed_two_page_predecessor(tmp_path)
    result = prepare_review_draft_structural_successor(
        predecessor_input=predecessor, predecessor_authored=authored,
        binding_root=tmp_path, edits_path=edits_path, output_dir=tmp_path / "successor")
    successor_input = Path(result["input"]["path"])
    edits = json.loads(edits_path.read_text(encoding="utf-8"))
    edits["retained_owner_assertions"] = []
    _write(edits_path, edits)
    successor = json.loads(successor_input.read_text(encoding="utf-8"))
    successor["bindings"]["structural_edits"].update(file_identity(edits_path))
    successor.pop("input_sha256")
    successor["input_sha256"] = sha256_bytes(canonical_bytes(successor))
    _write(successor_input, successor)
    with pytest.raises(ValueError, match="retained assertion domain is incomplete"):
        open_structural_projection_context(input_path=successor_input, binding_root=tmp_path)


def test_interval_map_cannot_prepend_second_marker_to_retained_owner(tmp_path):
    predecessor_input, authored, edits_path = _sealed_two_page_predecessor(tmp_path)
    edits = json.loads(edits_path.read_text(encoding="utf-8"))
    patch = edits["structural_post_patches"][0]["patches"][0]
    before = "new item\n- retained item"
    after = "new item\n- - retained item"
    retained_key = {"view": "original_pipeline_txt", "raw_index": 11}
    new_key = {"view": "original_pipeline_txt", "raw_index": 10}
    patch["source_occurrences"].append({**retained_key, "source_text_sha256": sha256_bytes(b"retained item")})
    patch.update(before=before, before_sha256=sha256_bytes(before.encode()),
                 after=after, after_sha256=sha256_bytes(after.encode()))
    start = before.index("- retained item")
    patch["interval_map"] = {"segments": [
        {"kind": "copy", "start": 0, "end": start, "sha256": sha256_bytes(before[:start].encode()),
         "source_occurrences": [new_key]},
        {"kind": "literal", "text": "- ", "sha256": sha256_bytes(b"- ")},
        {"kind": "copy", "start": start, "end": len(before), "sha256": sha256_bytes(before[start:].encode()),
         "source_occurrences": [retained_key]}], "removed_intervals": []}
    _write(edits_path, edits)
    output = tmp_path / "rejected-double-marker"
    with pytest.raises(ValueError, match="retained owner assertion receives a marker"):
        prepare_review_draft_structural_successor(
            predecessor_input=predecessor_input, predecessor_authored=authored,
            binding_root=tmp_path, edits_path=edits_path, output_dir=output)
    assert not output.exists()


def test_composite_source_occurrences_keep_predecessor_order(tmp_path):
    predecessor_input, authored, edits_path = _sealed_two_page_predecessor(tmp_path)
    edits = json.loads(edits_path.read_text(encoding="utf-8"))
    patch = edits["structural_post_patches"][0]["patches"][0]
    patch["source_occurrences"].insert(0, {"view": "original_pipeline_txt", "raw_index": 11,
                                           "source_text_sha256": sha256_bytes(b"retained item")})
    _write(edits_path, edits)
    output = tmp_path / "rejected-order"
    with pytest.raises(ValueError, match="out of order"):
        prepare_review_draft_structural_successor(
            predecessor_input=predecessor_input, predecessor_authored=authored,
            binding_root=tmp_path, edits_path=edits_path, output_dir=output)
    assert not output.exists()


@pytest.fixture
def structural_route(tmp_path, monkeypatch):
    from kb_creator.pipeline import source_choice_translation as choices
    from kb_creator.pipeline.source_choice_successor_preparation import prepare_source_choice_successor
    from kb_creator.scripts import author_reviewed_semantic_decisions as author

    fixture = _composite_fixture()
    renderer = shutil.which("pdftoppm")
    assert renderer is not None
    monkeypatch.setenv("KB_CREATOR_PDFTOPPM", renderer)
    built, queue, choice, alternate = fixture._prepare_composite_queue(tmp_path, monkeypatch)
    submission = fixture._submission(queue, choice["issue_id"], alternate["alternative_id"], tmp_path / "submission.json")
    ledger = Path(choices.record_decisions_v2(queue, submission, tmp_path / "ledger")["ledger"])
    predecessor = prepare_source_choice_successor(
        input_path=built["r0_input"], binding_root=tmp_path, ledger_path=ledger,
        draft_pages=built["draft_pages"], spec_paths=built["spec_paths"], output_dir=tmp_path / "r1-input")
    predecessor_input = Path(predecessor["input"]["path"])
    authored = tmp_path / "r1-authored"
    author.author_drafts(built["run"], Path(predecessor["draft_pages"]), authored,
                         [Path(path) for path in predecessor["spec_paths"]], mode="review_draft",
                         draft_input=predecessor_input, binding_root=tmp_path)
    packet = json.loads((built["run"] / "outputs/04-visual-merge-bundle/merge_packets/pages/page-001.json").read_text(encoding="utf-8"))
    decision = json.loads((authored / "pages/page-001.json").read_text(encoding="utf-8"))
    key = {"view": "raster_pipeline_ocr", "raw_index": built["raws"]["selected_raster_container"]}
    source = next(block["text"] for block in packet["views"][key["view"]]["blocks"] if block["raw_index"] == key["raw_index"])
    visual = decision["semantic_structure"]["review"]["visual"]
    candidate = {"source_page": 1, **key, "reader_preimage_sha256": sha256_bytes(source.encode("utf-8")), "visual": visual}
    sidecar = _write(tmp_path / "edits/marker-dispositions.json", {
        "schema": "kb_creator.source_marker_dispositions.v1", "candidates": [candidate],
        "dispositions": [{**candidate, "disposition": "unordered_list_item", "rationale": "Synthetic reviewed bullet."}],
    })
    before = fixture.PREFIX + fixture.ALTERNATE + fixture.SUFFIX
    patch = {"source_occurrences": [{**key, "source_text_sha256": sha256_bytes(source.encode("utf-8"))}],
             "before": before, "before_sha256": sha256_bytes(before.encode("utf-8")),
             "after": "- " + before, "after_sha256": sha256_bytes(("- " + before).encode("utf-8")), "count": 1}
    edits = {"schema": "kb_creator.review_draft_structural_successor.v1",
             "predecessor_input": {"path": predecessor_input.name, **file_identity(predecessor_input)},
             "predecessor_evidence": {"path": "review-draft-evidence.json", **file_identity(authored / "review-draft-evidence.json")},
             "source_marker_dispositions": {"path": sidecar.name, **file_identity(sidecar)},
             "structural_post_patches": [{"source_page": 1, "patches": [patch]}],
             "retained_owner_assertions": [],
             "page_units": [{"source_page": 1, "units": [{"id": "composite-list", "kind": "list",
                 "representation": "unordered_list", "view": key["view"], "raw_indices": [key["raw_index"]],
                 "start_line": 1, "end_line": 1, "item_count": 1}]}]}
    edits_path = _write(tmp_path / "edits/edits.json", edits)
    return {"root": tmp_path, "run": built["run"], "predecessor": predecessor, "input": predecessor_input,
            "authored": authored, "edits": edits, "edits_path": edits_path, "key": key, "before": before}


def test_synthetic_api_to_author_preserves_source_choice(structural_route):
    from kb_creator.scripts import author_reviewed_semantic_decisions as author

    case = structural_route
    output = case["root"] / "structural-input"
    result = prepare_review_draft_structural_successor(
        predecessor_input=case["input"], predecessor_authored=case["authored"],
        binding_root=case["root"], edits_path=case["edits_path"], output_dir=output)
    assert result["affected_pages"] == [1]
    successor_input = Path(result["input"]["path"])
    successor = json.loads(successor_input.read_text(encoding="utf-8"))
    predecessor = json.loads(case["input"].read_text(encoding="utf-8"))
    assert successor["source_issues"] == predecessor["source_issues"]
    assert successor["bindings"]["source_choice_ledger"] == predecessor["bindings"]["source_choice_ledger"]
    authored = case["root"] / "structural-authored"
    author.author_drafts(case["run"], output / "draft-pages", authored,
                         sorted((output / "author-specs").glob("spec-*.json")), mode="review_draft",
                         draft_input=successor_input, binding_root=case["root"])
    decision = json.loads((authored / "pages/page-001.json").read_text(encoding="utf-8"))
    assert decision["markdown"] == "- " + case["before"]
    assert decision["semantic_structure"]["units"][0]["representation"] == "unordered_list"
    assert decision["linguistic_source_choice_corrections"] == json.loads(
        (case["authored"] / "pages/page-001.json").read_text(encoding="utf-8"))["linguistic_source_choice_corrections"]
    from kb_creator.pipeline.review_draft_materialization import verify_final_review_draft
    verify_final_review_draft(run_root=case["run"], authored_root=authored,
                              input_path=successor_input, evidence_path=authored / "review-draft-evidence.json",
                              binding_root=case["root"])


def test_public_audit_rechecks_structural_authority_before_return(structural_route, monkeypatch):
    from kb_creator.scripts import audit_mineru_ai_merge_fidelity as audit

    case = structural_route
    result = prepare_review_draft_structural_successor(
        predecessor_input=case["input"], predecessor_authored=case["authored"],
        binding_root=case["root"], edits_path=case["edits_path"],
        output_dir=case["root"] / "structural-input")
    def drift_after_open(*args, **kwargs):
        assert kwargs["_structural_context"] is not None
        case["edits_path"].write_bytes(case["edits_path"].read_bytes() + b" ")
        return {"passed": True}
    monkeypatch.setattr(audit, "_audit_v3_content", drift_after_open)
    with pytest.raises(ValueError, match="identity drift"):
        audit.audit_v3_content(structural_input_path=Path(result["input"]["path"]),
                               structural_binding_root=case["root"])


def test_synthetic_structural_container_consumer_rederives_current_witness(structural_route):
    from kb_creator.pipeline import source_choice_translation as choices
    from kb_creator.pipeline.source_choice_container_proof import (
        derive_container_proof, open_structural_projection_context)
    from kb_creator.pipeline.reader_occurrence_projection import (
        validate_linguistic_source_choice_stage05_row, resolve_issue_reader_occurrence)

    case = structural_route
    output = case["root"] / "structural-input"
    result = prepare_review_draft_structural_successor(
        predecessor_input=case["input"], predecessor_authored=case["authored"],
        binding_root=case["root"], edits_path=case["edits_path"], output_dir=output)
    context = open_structural_projection_context(input_path=Path(result["input"]["path"]),
                                                 binding_root=case["root"])
    assert context is not None
    audit = json.loads((case["authored"] / "review-draft-stage05-audit.json").read_text(encoding="utf-8"))
    predecessor_proof = next(row for row in audit["pages"][0]["ordered_proof_stream"]
                             if row["kind"] == "linguistic_source_choice_container_v1")
    ledger_record = predecessor_proof["ledger"]
    ledger_path = Path(ledger_record["path"])
    ledger = json.loads(ledger_path.read_text(encoding="utf-8"))
    verified = choices.verify_ledger_v2(ledger_path)
    current = "- " + case["before"]
    key = (case["key"]["view"], case["key"]["raw_index"])
    proof = derive_container_proof(ledger_record=ledger_record, ledger=ledger, verified=verified,
                                   page=1, key=key, current_markdown=current, structural_context=context)
    assert proof["r1_container"]["text"] == case["before"]
    assert proof["structural_projection"]["current_container"]["page_character_span"]["character_start"] == 2
    validate_linguistic_source_choice_stage05_row(proof, key)
    issue = {"source_page": 1, "source_excerpt_en": "1D6", "source_excerpt_sha256": sha256_bytes(b"1D6"),
             "candidate_span": {"binding": "ordered_selected_source_v1", "source_key": case["key"]}}
    resolved = resolve_issue_reader_occurrence(
        issue, {"source_page": 1, "markdown": current}, {"ordered_proof_stream": [proof]}, "\n" + current + "\n")
    span = resolved["page_reader_span"]
    assert current[span["character_start"]:span["character_end"]] == "ID6"


def test_structural_container_consumer_rejects_resealed_mutations(structural_route):
    from kb_creator.pipeline import source_choice_translation as choices
    from kb_creator.pipeline.source_choice_container_proof import (
        derive_container_proof, open_structural_projection_context)
    from kb_creator.pipeline.reader_occurrence_projection import (
        ReaderOccurrenceError, validate_linguistic_source_choice_stage05_row)

    case = structural_route
    result = prepare_review_draft_structural_successor(
        predecessor_input=case["input"], predecessor_authored=case["authored"],
        binding_root=case["root"], edits_path=case["edits_path"], output_dir=case["root"] / "structural-input")
    context = open_structural_projection_context(input_path=Path(result["input"]["path"]), binding_root=case["root"])
    audit = json.loads((case["authored"] / "review-draft-stage05-audit.json").read_text(encoding="utf-8"))
    predecessor_proof = next(row for row in audit["pages"][0]["ordered_proof_stream"]
                             if row["kind"] == "linguistic_source_choice_container_v1")
    record = predecessor_proof["ledger"]
    path = Path(record["path"])
    ledger = json.loads(path.read_text(encoding="utf-8"))
    verified = choices.verify_ledger_v2(path)
    key = (case["key"]["view"], case["key"]["raw_index"])
    row = derive_container_proof(ledger_record=record, ledger=ledger, verified=verified,
                                 page=1, key=key, current_markdown="- " + case["before"],
                                 structural_context=context)
    for field in ("current_page_sha256", "lexical_page_sha256"):
        altered = deepcopy(row)
        altered["structural_projection"][field] = "0" * 64
        altered["row_sha256"] = sha256_bytes(canonical_bytes({k: v for k, v in altered.items() if k != "row_sha256"}))
        with pytest.raises(ReaderOccurrenceError):
            validate_linguistic_source_choice_stage05_row(altered, key)
    altered = deepcopy(row)
    altered["structural_projection"]["current_witness_spans"][0]["span"]["character_start"] += 1
    altered["row_sha256"] = sha256_bytes(canonical_bytes({k: v for k, v in altered.items() if k != "row_sha256"}))
    with pytest.raises(ReaderOccurrenceError):
        validate_linguistic_source_choice_stage05_row(altered, key)
    with pytest.raises(ValueError, match="current page differs"):
        derive_container_proof(ledger_record=record, ledger=ledger, verified=verified,
                               page=1, key=key, current_markdown="- " + case["before"] + "!",
                               structural_context=context)
    packet_path = case["run"] / "outputs/04-visual-merge-bundle/merge_packets/pages/page-001.json"
    original_packet = packet_path.read_bytes()
    packet = json.loads(original_packet)
    source_block = next(block for block in packet["views"][key[0]]["blocks"]
                        if block["raw_index"] == key[1])
    source_block["text"] += "!"
    _write(packet_path, packet)
    with pytest.raises(ReaderOccurrenceError):
        validate_linguistic_source_choice_stage05_row(row, key)
    packet_path.write_bytes(original_packet)
    # A byte change in the bound edit authority invalidates even the original,
    # otherwise self-consistent and resealed Stage05 row.
    case["edits_path"].write_bytes(case["edits_path"].read_bytes() + b" ")
    with pytest.raises(ReaderOccurrenceError):
        validate_linguistic_source_choice_stage05_row(row, key)


def test_synthetic_non_list_successor_preserves_lexical_page(structural_route):
    from kb_creator.scripts import author_reviewed_semantic_decisions as author

    case = structural_route
    sidecar = case["edits_path"].parent / "marker-dispositions.json"
    marker = json.loads(sidecar.read_text(encoding="utf-8"))
    marker["dispositions"][0]["disposition"] = "non_list"
    _write(sidecar, marker)
    edits = case["edits"]
    edits["source_marker_dispositions"] = {"path": sidecar.name, **file_identity(sidecar)}
    edits["structural_post_patches"] = []
    edits["page_units"] = []
    _write(case["edits_path"], edits)
    output = case["root"] / "non-list-input"
    result = prepare_review_draft_structural_successor(
        predecessor_input=case["input"], predecessor_authored=case["authored"],
        binding_root=case["root"], edits_path=case["edits_path"], output_dir=output)
    assert result["affected_pages"] == []
    assert (output / "draft-pages/page-001.json").read_bytes() == (
        case["input"].parent / "draft-pages/page-001.json").read_bytes()
    authored = case["root"] / "non-list-authored"
    author.author_drafts(case["run"], output / "draft-pages", authored,
                         sorted((output / "author-specs").glob("spec-*.json")), mode="review_draft",
                         draft_input=Path(result["input"]["path"]), binding_root=case["root"])
    decision = json.loads((authored / "pages/page-001.json").read_text(encoding="utf-8"))
    predecessor = json.loads((case["authored"] / "pages/page-001.json").read_text(encoding="utf-8"))
    assert decision["markdown"] == predecessor["markdown"] == case["before"]
    assert decision["semantic_structure"]["units"] == predecessor["semantic_structure"]["units"]
    assert decision["linguistic_source_choice_corrections"] == predecessor["linguistic_source_choice_corrections"]


@pytest.mark.parametrize("mutation", ["patch_hash", "retained_hash", "missing_patch", "non_list_patch"])
def test_structural_preflight_rejects_stale_or_incomplete_source(structural_route, mutation):
    case = structural_route
    edits = case["edits"]
    if mutation == "patch_hash":
        edits["structural_post_patches"][0]["patches"][0]["source_occurrences"][0]["source_text_sha256"] = "0" * 64
    elif mutation == "retained_hash":
        edits["retained_owner_assertions"] = [{"source_page": 1, **case["key"], "source_text_sha256": "0" * 64,
            "owner_id": "composite", "representation": "unordered_list", "visual_group_id": "one"}]
        edits["structural_post_patches"] = []
        edits["page_units"] = []
    elif mutation == "missing_patch":
        edits["structural_post_patches"] = []
        edits["page_units"] = []
    else:
        sidecar = case["edits_path"].parent / "marker-dispositions.json"
        marker = json.loads(sidecar.read_text(encoding="utf-8"))
        marker["dispositions"][0]["disposition"] = "non_list"
        _write(sidecar, marker)
        edits["source_marker_dispositions"] = {"path": sidecar.name, **file_identity(sidecar)}
    _write(case["edits_path"], edits)
    output = case["root"] / "rejected-input"
    with pytest.raises(ValueError):
        prepare_review_draft_structural_successor(
            predecessor_input=case["input"], predecessor_authored=case["authored"],
            binding_root=case["root"], edits_path=case["edits_path"], output_dir=output)
    assert not output.exists()


def test_structural_post_patch_runs_after_v2_replacement(monkeypatch):
    from kb_creator.scripts import author_reviewed_semantic_decisions as author
    from kb_creator.pipeline import reader_occurrence_projection as projection

    def replace(markdown, replacements):
        assert markdown == "H old text"
        return "H final text", []

    monkeypatch.setattr(projection, "apply_bound_reader_replacements", replace)
    monkeypatch.setattr(author, "_apply_review_rules", lambda markdown, *_: markdown)
    decision = {"markdown": "H old text", "linguistic_source_choice_corrections": [{
        "page_reader_span": {"start_byte": 0, "end_byte": 1}, "reader_preimage": "old", "reader_replacement": "final",
    }]}
    row = {"patches": [], "rules": {}, "post_patches": [], "structural_post_patches": [{"before": "H final text", "after": "- final text", "count": 1}], "units": []}
    assert author._render_reviewed_markdown(decision, {}, row, 155)[0] == "- final text"


def test_structural_post_patch_is_exact_and_cannot_erase_unreviewed_marker(monkeypatch):
    from kb_creator.scripts import author_reviewed_semantic_decisions as author
    monkeypatch.setattr(author, "_apply_review_rules", lambda markdown, *_: markdown)
    decision = {"markdown": "H one\nU two"}
    row = {"patches": [], "rules": {}, "post_patches": [], "structural_post_patches": [{"before": "H one", "after": "- one", "count": 1}], "units": []}
    assert author._render_reviewed_markdown(decision, {}, row, 1)[0] == "- one\nU two"
    row["structural_post_patches"][0]["count"] = 2
    with pytest.raises(ValueError, match="patch matches"):
        author._render_reviewed_markdown(decision, {}, row, 1)
