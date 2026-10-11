"""Position lineage for reviewed structural edits after lexical source choices."""
from copy import deepcopy

import pytest

from kb_creator.pipeline.identity import sha256_bytes
from kb_creator.pipeline.structural_projection import (project_interval, project_structural_page,
    validate_retained_owner_projection)


def _sha(text):
    return sha256_bytes(text.encode("utf-8"))


def _patch(before, after, occurrences, interval_map=None):
    result = {"before": before, "before_sha256": _sha(before), "after": after,
              "after_sha256": _sha(after), "count": 1, "source_occurrences": occurrences}
    if interval_map is not None:
        result["interval_map"] = interval_map
    return result


def _copy(before, start, end, key):
    return {"kind": "copy", "start": start, "end": end, "sha256": _sha(before[start:end]),
            "source_occurrences": [key]}


def test_two_identical_containers_reorder_by_exact_source_interval():
    before = "AA\nAA\nend"
    after = "AA\nend\nAA"
    first = {"view": "original_pipeline_txt", "raw_index": 7}
    second = {"view": "raster_pipeline_ocr", "raw_index": 7}
    suffix = {"view": "original_pipeline_txt", "raw_index": 8}
    occurrences = [{**key, "source_text_sha256": _sha("AA" if key != suffix else "end")}
                   for key in (first, second, suffix)]
    patch = _patch(before, after, occurrences, {"segments": [
        _copy(before, 3, 5, second), _copy(before, 5, 6, second),
        _copy(before, 6, 9, suffix), _copy(before, 2, 3, first), _copy(before, 0, 2, first)],
        "removed_intervals": []})
    current, origins = project_structural_page(before, [patch])
    assert current == after
    assert project_interval(current, origins, 0, 2)["character_start"] == 7
    assert project_interval(current, origins, 3, 5)["character_start"] == 0
    assert first != second


def test_interval_segment_cannot_reverse_qualified_source_keys():
    before = "AA"
    first = {"view": "original_pipeline_txt", "raw_index": 7}
    second = {"view": "raster_pipeline_ocr", "raw_index": 7}
    patch = _patch(before, before, [{**first, "source_text_sha256": _sha(before)},
                                    {**second, "source_text_sha256": _sha(before)}], {
        "segments": [{**_copy(before, 0, 2, first), "source_occurrences": [second, first]}],
        "removed_intervals": []})
    with pytest.raises(ValueError, match="copied interval"):
        project_structural_page(before, [patch])


@pytest.mark.parametrize("change", ["missing", "duplicate", "overlap", "foreign", "stale", "copied"])
def test_reorder_rejects_invalid_interval_map(change):
    before = "AA\nBB"
    key = {"view": "original_pipeline_txt", "raw_index": 1}
    other = {"view": "raster_pipeline_ocr", "raw_index": 1}
    occurrence = {**key, "source_text_sha256": _sha(before)}
    segments = [_copy(before, 3, 5, key), _copy(before, 2, 3, key), _copy(before, 0, 2, key)]
    patch = _patch(before, "BB\nAA", [occurrence], {"segments": segments, "removed_intervals": []})
    if change == "missing": segments.pop()
    elif change == "duplicate": segments.append(deepcopy(segments[0]))
    elif change == "overlap": segments[1] = _copy(before, 2, 4, key)
    elif change == "foreign": segments[0]["source_occurrences"] = [other]
    elif change == "stale": segments[0]["sha256"] = "0" * 64
    else: segments[0] = _copy(before, 0, 2, key)
    with pytest.raises(ValueError):
        project_structural_page(before, [patch])


def test_marker_insertion_shifts_container_and_witness_without_changing_bytes():
    before = "lead\nID6"
    patch = _patch("lead", "- lead", [{"view": "original_pipeline_txt", "raw_index": 1,
                                       "source_text_sha256": _sha("lead")}])
    current, origins = project_structural_page(before, [patch])
    assert current == "- lead\nID6"
    assert project_interval(current, origins, 5, 8) == {
        "character_start": 7, "character_end": 10, "text_sha256": _sha("ID6")}


def test_exact_ornament_removal_preserves_suffix_and_rejects_witness_loss():
    before = "H listed"
    patch = _patch(before, "- listed", [{"view": "original_pipeline_txt", "raw_index": 1,
                                         "source_text_sha256": _sha(before)}])
    current, origins = project_structural_page(before, [patch])
    assert current == "- listed"
    assert project_interval(current, origins, 2, len(before))["text_sha256"] == _sha("listed")
    with pytest.raises(ValueError, match="removes or fragments"):
        project_interval(current, origins, 0, len(before))
    bad = deepcopy(patch); bad["after"] = "- changed"; bad["after_sha256"] = _sha(bad["after"])
    with pytest.raises(ValueError, match="conserved"):
        project_structural_page(before, [bad])


def test_reorder_without_interval_map_is_rejected():
    with pytest.raises(ValueError, match="conserved"):
        project_structural_page("one\ntwo", [_patch("one\ntwo", "two\none", [
            {"view": "original_pipeline_txt", "raw_index": 1, "source_text_sha256": _sha("one\ntwo")}])])


def _retained_reorder():
    line = "- Равный"
    before = f"{line}\n{line}\nend"
    after = f"{line}\nend\n{line}"
    first = {"view": "original_pipeline_txt", "raw_index": 7}
    second = {"view": "original_pipeline_txt", "raw_index": 8}
    end_key = {"view": "original_pipeline_txt", "raw_index": 9}
    first_end = len(line)
    second_start = first_end + 1
    second_end = second_start + first_end
    end_start = second_end + 1
    patch = _patch(before, after, [{**key, "source_text_sha256": _sha(line if key != end_key else "end")}
                                   for key in (first, second, end_key)], {"segments": [
        _copy(before, second_start, second_end, second),
        _copy(before, second_end, second_end + 1, second),
        _copy(before, end_start, len(before), end_key),
        _copy(before, first_end, first_end + 1, first),
        _copy(before, 0, first_end, first)], "removed_intervals": []})
    definition = {"id": "retained", "kind": "list", "representation": "unordered_list",
                  "view": first["view"], "raw_indices": [first["raw_index"]],
                  "start_line": 1, "end_line": 1, "item_count": 1}
    owner = {"id": "retained", "kind": "list", "representation": "unordered_list",
             "source_blocks": [first], "markdown_span": {"start_line": 1, "end_line": 1,
             "sha256": _sha(line)}, "item_count": 1}
    assertion = {"owner_id": "retained", **first}
    return before, patch, definition, owner, assertion


def test_retained_selector_tracks_exact_equal_text_occurrence():
    before, patch, definition, owner, assertion = _retained_reorder()
    successor = {**definition, "start_line": 3, "end_line": 3}
    validate_retained_owner_projection(assertion=assertion, owner=owner,
        predecessor_definition=definition, successor_definition=successor,
        predecessor_markdown=before, effective_markdown=before, patches=[patch])
    with pytest.raises(ValueError, match="selector differs from projected interval"):
        validate_retained_owner_projection(assertion=assertion, owner=owner,
            predecessor_definition=definition, successor_definition=definition,
            predecessor_markdown=before, effective_markdown=before, patches=[patch])


def test_retained_selector_ignores_wrong_copy_labels_for_equal_text():
    before, patch, definition, owner, assertion = _retained_reorder()
    segments = patch["interval_map"]["segments"]
    first, second = {"view": "original_pipeline_txt", "raw_index": 7}, {"view": "original_pipeline_txt", "raw_index": 8}
    segments[0]["source_occurrences"] = [first]
    segments[-1]["source_occurrences"] = [second]
    with pytest.raises(ValueError, match="selector differs from projected interval"):
        validate_retained_owner_projection(assertion=assertion, owner=owner,
            predecessor_definition=definition, successor_definition=definition,
            predecessor_markdown=before, effective_markdown=before, patches=[patch])


def test_multiline_utf8_retained_span_survives_two_ordered_patches():
    before = "αρχή\n- Список\n  продолжение"
    key = {"view": "original_pipeline_txt", "raw_index": 11}
    owner_text = "- Список\n  продолжение"
    definition = {"id": "retained", "kind": "list", "representation": "unordered_list",
                  "view": key["view"], "raw_indices": [key["raw_index"]],
                  "start_line": 2, "end_line": 3, "item_count": 1}
    owner = {"id": "retained", "kind": "list", "representation": "unordered_list",
             "source_blocks": [key], "markdown_span": {"start_line": 2, "end_line": 3,
             "sha256": _sha(owner_text)}, "item_count": 1}
    patches = [_patch("αρχή", "- αρχή", [{"view": key["view"], "raw_index": 10,
                 "source_text_sha256": _sha("αρχή")}]),
               _patch("Список", "Список", [{**key, "source_text_sha256": _sha("Список")}],
                      {"segments": [_copy("Список", 0, len("Список"), key)], "removed_intervals": []})]
    validate_retained_owner_projection(assertion={"owner_id": "retained", **key}, owner=owner,
        predecessor_definition=definition, successor_definition=definition,
        predecessor_markdown=before, effective_markdown=before, patches=patches)


def test_unchanged_unique_text_selector_still_requires_exact_origin():
    before = "lead\n- unique retained"
    key = {"view": "original_pipeline_txt", "raw_index": 11}
    definition = {"id": "retained", "kind": "list", "representation": "unordered_list",
                  "view": key["view"], "raw_indices": [key["raw_index"]],
                  "start": "unique retained", "item_count": 1}
    owner = {"id": "retained", "kind": "list", "representation": "unordered_list",
             "source_blocks": [key], "markdown_span": {"start_line": 2, "end_line": 2,
             "sha256": _sha("- unique retained")}, "item_count": 1}
    patch = _patch("lead", "- lead", [{"view": key["view"], "raw_index": 10,
                                        "source_text_sha256": _sha("lead")}])
    validate_retained_owner_projection(assertion={"owner_id": "retained", **key}, owner=owner,
        predecessor_definition=definition, successor_definition=definition,
        predecessor_markdown=before, effective_markdown=before, patches=[patch])
    with pytest.raises(ValueError, match="ambiguous"):
        validate_retained_owner_projection(assertion={"owner_id": "retained", **key}, owner=owner,
            predecessor_definition=definition, successor_definition=definition,
            predecessor_markdown=before + "\n- unique retained",
            effective_markdown=before + "\n- unique retained", patches=[])


@pytest.mark.parametrize("change", ["count", "sources", "parent", "presence", "span_hash",
                                    "old_selector", "effective", "text_conversion"])
def test_retained_selector_rejects_changed_authority(change):
    before, patch, definition, owner, assertion = _retained_reorder()
    successor = {**definition, "start_line": 3, "end_line": 3}
    if change == "count": successor["item_count"] = 2
    elif change == "sources": successor["raw_indices"] = [8]
    elif change == "parent": successor["container_parent"] = "other"
    elif change == "presence": successor["extra"] = None
    elif change == "span_hash": owner["markdown_span"]["sha256"] = "0" * 64
    elif change == "old_selector": definition["start_line"] = 2
    elif change == "effective": before = before + "\n"
    else: successor = {key: value for key, value in definition.items()
                       if key not in {"start_line", "end_line"}} | {"start": "Равный"}
    with pytest.raises(ValueError):
        validate_retained_owner_projection(assertion=assertion, owner=owner,
            predecessor_definition=definition, successor_definition=successor,
            predecessor_markdown=before, effective_markdown=before[:-1] if change == "effective" else before,
            patches=[patch])
