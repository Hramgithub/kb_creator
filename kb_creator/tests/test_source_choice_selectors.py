from copy import deepcopy

import pytest

from kb_creator.pipeline.identity import sha256_bytes
from kb_creator.pipeline.source_choice_selectors import SourceChoiceSelectorError, rebind_unit_selectors, rebind_prose_selectors, rebind_prose_role_selectors
from kb_creator.pipeline.source_choice_slice import SourceSlice, SourceChoiceSliceError


def _sha(text):
    return sha256_bytes(text.encode())


def _unit(name, first, last, text):
    return {"id": name, "markdown_span": {"start_line": first, "end_line": last, "sha256": _sha(text)}}


def test_equal_lines_are_rebound_by_authored_coordinates_and_multiple_edits():
    markdown = "heading\n1D6\nmiddle\n1D6\nsuffix"
    units = [_unit("first", 2, 2, "1D6"), _unit("second", 4, 4, "1D6"), _unit("last", 5, 5, "suffix")]
    spec = {"units": [{"id": name, "start": text, "end": text} for name, text in
                      [("first", "1D6"), ("second", "1D6"), ("last", "suffix")]]}
    original = deepcopy(spec)
    edits = [SourceSlice(19, 22, _sha("1D6"), "ID6\nextra"), SourceSlice(8, 11, _sha("1D6"), "2D6\nmore\nlines")]
    result = rebind_unit_selectors(spec, markdown, units, edits, markdown_sha256=_sha(markdown))
    assert [(u["start_line"], u["end_line"]) for u in result["units"]] == [(2, 4), (6, 7), (8, 8)]
    assert all("start" not in u and "end" not in u for u in result["units"])
    assert spec == original


def test_replacement_inside_unit_updates_its_end_and_following_units():
    markdown = "prefix 1D6 tail\nlast"
    units = [_unit("block", 1, 1, "prefix 1D6 tail"), _unit("last", 2, 2, "last")]
    spec = {"units": [{"id": "block", "start_line": 1, "end_line": 1},
                      {"id": "last", "start_line": 2, "end_line": 2}]}
    result = rebind_unit_selectors(spec, markdown, units,
        [SourceSlice(7, 10, _sha("1D6"), "ID6\nextra")], markdown_sha256=_sha(markdown))
    assert [(u["start_line"], u["end_line"]) for u in result["units"]] == [(1, 2), (3, 3)]


def test_verified_retention_can_cross_multiple_units_while_real_edit_moves_them():
    markdown = "heading\n\nENTROPY\n\nSORCERY\n\ntail"
    retained = "ENTROPY\n\nSORCERY"
    start = markdown.index(retained)
    units = [_unit("first", 3, 3, "ENTROPY"), _unit("second", 5, 5, "SORCERY")]
    spec = {"units": [{"id": "first", "start_line": 3, "end_line": 3},
                      {"id": "second", "start_line": 5, "end_line": 5}]}
    edits = [SourceSlice(start,start+len(retained),_sha(retained),retained),
             SourceSlice(0,7,_sha("heading"),"heading\nextra")]
    result = rebind_unit_selectors(spec,markdown,units,edits,markdown_sha256=_sha(markdown))
    assert [(u["start_line"],u["end_line"]) for u in result["units"]] == [(4,4),(6,6)]


@pytest.mark.parametrize("fault", ["retention_hash","page_hash","overlap","unit_hash","real_crossing"])
def test_retention_still_requires_all_evidence_and_rejects_real_crossing(fault):
    markdown = "abc\ndef\nghi"
    units = [_unit("unit",2,2,"def")]
    spec = {"units": [{"id":"unit","start_line":2,"end_line":2}]}
    retained = markdown[2:9]
    edits = [SourceSlice(2,9,_sha(retained),retained)]
    page_hash = _sha(markdown)
    if fault == "retention_hash": edits = [SourceSlice(2,9,_sha("wrong"),retained)]
    elif fault == "page_hash": page_hash = _sha("wrong")
    elif fault == "overlap": edits.append(SourceSlice(4,7,_sha("def"),"def"))
    elif fault == "unit_hash": units[0]["markdown_span"]["sha256"] = _sha("wrong")
    elif fault == "real_crossing": edits = [SourceSlice(2,9,_sha(retained),retained.upper())]
    with pytest.raises((SourceChoiceSelectorError, SourceChoiceSliceError)):
        rebind_unit_selectors(spec,markdown,units,edits,markdown_sha256=page_hash)


def _prose_fixture():
    markdown = "> A\n>\n> B\n\ntail"
    selector = {"view": "original_pipeline_txt", "raw_index": 4,
                "markdown_span": {"start_line": 5, "end_line": 5}}
    authored = {**deepcopy(selector), "original_text_sha256": _sha("tail"),
                "markdown_span": {**selector["markdown_span"], "sha256": _sha("tail")}}
    edit = SourceSlice(0, 9, _sha("> A\n>\n> B"), "> C")
    return markdown, {"reviewed_prose_bindings_v1": [selector]}, [authored], [edit]


def test_prose_after_shortened_quote_moves_by_sealed_coordinates():
    markdown, spec, bindings, edits = _prose_fixture()
    original = deepcopy(spec)
    result = rebind_prose_selectors(spec, markdown, bindings, edits, markdown_sha256=_sha(markdown))
    assert result["reviewed_prose_bindings_v1"][0]["markdown_span"] == {"start_line": 3, "end_line": 3}
    assert spec == original


def test_prose_role_selectors_rebind_after_and_reject_inside_bound_span_edits():
    markdown = "heading\n\nordinary prose\n\ntail"
    selector = {"role": "ordinary_prose", "view": "original_pipeline_txt", "raw_index": 9,
                "markdown_span": {"start_line": 5, "end_line": 5}, "visual_reviewed": True, "rationale": "reviewed"}
    authored = [{"view": "original_pipeline_txt", "raw_index": 9,
                 "markdown_span": {"start_line": 5, "end_line": 5, "sha256": _sha("tail")}}]
    spec = {"reviewed_prose_roles_v1": [selector]}
    shifted = rebind_prose_role_selectors(spec, markdown, authored,
        [SourceSlice(0, 7, _sha("heading"), "heading\nextra")], markdown_sha256=_sha(markdown))
    assert shifted["reviewed_prose_roles_v1"][0]["markdown_span"] == {"start_line": 6, "end_line": 6}
    with pytest.raises((SourceChoiceSelectorError, SourceChoiceSliceError)):
        rebind_prose_role_selectors(spec, markdown, authored,
            [SourceSlice(9, 22, _sha("ordinary prose"), "changed")], markdown_sha256=_sha(markdown))


@pytest.mark.parametrize("fault", ["missing", "duplicate_key", "duplicate_selector", "layout", "span_hash", "selector_line", "boundary"])
def test_prose_rebinding_rejects_stale_or_ambiguous_bindings(fault):
    markdown, spec, bindings, edits = _prose_fixture()
    if fault == "missing": bindings.clear()
    elif fault == "duplicate_key": bindings.append(deepcopy(bindings[0]))
    elif fault == "duplicate_selector": spec["reviewed_prose_bindings_v1"].append(deepcopy(spec["reviewed_prose_bindings_v1"][0]))
    elif fault == "layout": bindings[0]["source_layout"] = "soft_wrapped_paragraph_v1"
    elif fault == "span_hash": bindings[0]["markdown_span"]["sha256"] = _sha("wrong")
    elif fault == "selector_line": spec["reviewed_prose_bindings_v1"][0]["markdown_span"]["start_line"] = 4
    elif fault == "boundary": edits = [SourceSlice(8, 12, _sha(markdown[8:12]), "x")]
    with pytest.raises((SourceChoiceSelectorError, SourceChoiceSliceError)):
        rebind_prose_selectors(spec, markdown, bindings, edits, markdown_sha256=_sha(markdown))


@pytest.mark.parametrize("fault", ["unit_hash", "unit_duplicate", "page_hash", "cross_boundary", "line_merge", "numeric_selector"])
def test_selector_rebinding_rejects_stale_or_unplaceable_evidence(fault):
    markdown = "abc\ndef\nghi"
    unit = _unit("unit", 2, 2, "def")
    units = [unit]
    spec = {"units": [{"id": "unit", "start": "def"}]}
    digest = _sha(markdown)
    edits = [SourceSlice(4, 7, _sha("def"), "DEF")]
    if fault == "unit_hash": unit["markdown_span"]["sha256"] = _sha("wrong")
    if fault == "unit_duplicate": units.append(deepcopy(unit))
    if fault == "page_hash": digest = _sha("wrong")
    if fault == "cross_boundary": edits = [SourceSlice(2, 5, _sha("c\nd"), "x")]
    if fault == "line_merge": edits = [SourceSlice(3, 4, _sha("\n"), " ")]
    if fault == "numeric_selector": spec["units"][0].update(start_line=1, end_line=1)
    with pytest.raises((SourceChoiceSelectorError, SourceChoiceSliceError)):
        rebind_unit_selectors(spec, markdown, units, edits, markdown_sha256=digest)
