import copy

import pytest

from kb_creator.pipeline.reviewed_unit_order import expose_nested_table_units, order_semantic_units


def test_reorders_only_declarations_and_preserves_relations_and_source_selectors():
    units = [
        {"id": "later", "start": "Later", "end": "Later", "raw_indices": [4]},
        {"id": "parent", "start_line": 1, "end_line": 3, "raw_indices": [1, 2]},
        {"id": "child", "start_line": 1, "end_line": 1, "raw_indices": [1], "container_parent": "parent"},
    ]
    original = copy.deepcopy(units)
    result = order_semantic_units("First\n\nLater", units, page=1)
    assert [unit["id"] for unit in result] == ["parent", "child", "later"]
    assert {u["id"]: u for u in result} == {u["id"]: u for u in original}
    assert units == original
    assert order_semantic_units("First\n\nLater", result, page=1) == result


@pytest.mark.parametrize("markdown,units", [
    ("Same\nSame", [{"id": "a", "start": "Same"}]),
    ("Present", [{"id": "a", "start": "Missing"}]),
    ("Present", [{"id": "a", "start_line": 2, "end_line": 2}]),
    ("Present", [{"id": "a", "start": "Present"}, {"id": "a", "start": "Present"}]),
])
def test_ambiguous_stale_or_duplicate_units_fail(markdown, units):
    with pytest.raises(ValueError):
        order_semantic_units(markdown, units, page=1)


def test_nested_table_gets_disjoint_child_without_changing_cells_or_parent_span():
    markdown = "# Guard\n\n| STR | HP |\n| --- | --- |\n| 12 | 9 |\n\nMove 8"
    spec = {"source_page": 1, "units": [{"id": "stats", "kind": "statblock", "representation": "semantic_span", "view": "original_pipeline_ocr", "raw_indices": [2, 3], "start_line": 1, "end_line": 7, "semantic_parent": None}]}
    original = copy.deepcopy(spec)
    result = expose_nested_table_units(markdown, spec, [{"view": "original_pipeline_ocr", "raw_index": 2, "rows": [["STR", "HP"], ["12", "9"]]}])
    parent, child = result["units"]
    assert parent["raw_indices"] == [3] and parent["start_line"] == 1 and parent["end_line"] == 7
    assert child["raw_indices"] == [2] and child["container_parent"] == "stats"
    assert (child["start_line"], child["end_line"]) == (3, 5)
    assert spec == original
    with pytest.raises(ValueError, match="no unique exact"):
        expose_nested_table_units(markdown, spec, [{"view": "original_pipeline_ocr", "raw_index": 2, "rows": [["STR", "HP"], ["99", "9"]]}])
