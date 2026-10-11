"""Complete-page provenance for reader coverage choices."""

import pytest

from kb_creator.pipeline.identity import sha256_bytes
from kb_creator.pipeline.reader_text_coverage_binding import (
    ReaderTextCoverageBindingError, _indexed_visible_reader, _visible_reader,
)
from kb_creator.pipeline.source_choice_coverage_successor import (
    SourceChoiceCoverageSuccessorError, project_claims,
)


@pytest.mark.parametrize("page,start,end,expected", [
    ("## Alpha", 3, 8, (0, 5, "Alpha")),
    ("Prior\n\n## Alpha", 10, 15, (6, 11, "Alpha")),
    ("Prior\n\n- Alpha", 9, 14, (6, 11, "Alpha")),
    ("Prior\n\n1. Alpha", 10, 15, (6, 11, "Alpha")),
    ("Prior\n\n> Alpha", 9, 14, (6, 11, "Alpha")),
    ("**Alpha**", 2, 7, (0, 5, "Alpha")),
    ("`Alpha`", 1, 6, (0, 5, "Alpha")),
    ("[Alpha](dest)", 1, 6, (0, 5, "Alpha")),
    ("Alpha\n\n## Alpha", 10, 15, (6, 11, "Alpha")),
    ("Before\n\n![alt](path)\n\n## Alpha", 25, 30, (7, 12, "Alpha")),
])
def test_accepted_complete_page_vectors(page, start, end, expected):
    projected = _indexed_visible_reader(page)
    assert projected.visible == _visible_reader(page)
    assert projected.raw_interval(start, end) == expected


def test_mixed_syntax_literal_code_punctuation_and_unicode_origins():
    page = "Прежде [label](hidden) and `a*b_c`!\n\n> ## **Финал**"
    indexed = _indexed_visible_reader(page)
    assert indexed.normalized == "Прежде label and a*b_c! Финал"
    for target in ("label", "a*b_c", "Финал"):
        start = page.index(target)
        a, b, value = indexed.raw_interval(start, start + len(target))
        assert indexed.normalized[a:b] == value == target
    assert page.index("Финал") != len(page[:page.index("Финал")].encode("utf-8"))
    with pytest.raises(ReaderTextCoverageBindingError, match="no contiguous"):
        indexed.raw_interval(page.index("hidden"), page.index("hidden") + len("hidden"))


def test_collapsed_whitespace_requires_complete_ownership():
    page = "Alpha  \n  Beta"
    indexed = _indexed_visible_reader(page)
    assert indexed.normalized == "Alpha Beta"
    with pytest.raises(ReaderTextCoverageBindingError, match="partially owns"):
        indexed.raw_interval(5, 6)
    assert indexed.raw_interval(0, 5) == (0, 5, "Alpha")


def test_hidden_link_destination_does_not_move_later_occurrence_identity():
    page = "[Alpha](hidden-destination) Alpha"
    indexed = _indexed_visible_reader(page)
    assert indexed.normalized == "Alpha Alpha"
    first = page.index("Alpha")
    second = page.rindex("Alpha")
    assert indexed.raw_interval(first, first + 5) == (0, 5, "Alpha")
    assert indexed.raw_interval(second, second + 5) == (6, 11, "Alpha")


@pytest.mark.parametrize("page", ["##", "- ", "1. ", "`open", "[x](open", "<b>x</b>"])
def test_malformed_complete_pages_remain_rejected(page):
    with pytest.raises(ReaderTextCoverageBindingError):
        _indexed_visible_reader(page)


def _sha(text):
    return sha256_bytes(text.encode("utf-8"))


def _claim(page, word):
    visible = _indexed_visible_reader(page).normalized
    start = visible.index(word)
    key = {"source_page": 1, "view_id": "ocr", "raw_index": 1}
    return {"status": "validated", "claim": {
        "claim_id": "claim-1", "reader_page": 1,
        "source_unit": key, "canonical_unit": key,
        "proof": {"normalized_span": [start, start + len(word)],
                  "expected_normalized_sha256": _sha(word)},
    }}


def _choice(page, old, new, issue):
    start = page.index(old)
    return {"disposition": "selected_alternative", "issue_id": issue,
            "r0_reader_span": {"character_start": start, "character_end": start + len(old),
                               "text_sha256": _sha(old)},
            "intended_reader_successor": {"text": new}}


def test_heading_edit_shifts_claim_and_preserves_its_text_proof():
    page = "## Old\n\nKeep"
    claim = _claim(page, "Keep")
    choice = _choice(page, "Old", "Longer", "heading")
    rows = project_claims([claim], [choice], {"heading": {"source_page": 1}},
                          {1: {"markdown": page}})
    assert len(rows) == 1
    assert rows[0]["mode"] == "shifted"
    assert rows[0]["r0_normalized_span"] == [4, 8]
    assert rows[0]["r1_normalized_span"] == [7, 11]
    assert rows[0]["r0_normalized_sha256"] == rows[0]["r1_normalized_sha256"] == _sha("Keep")


def test_edit_after_claim_does_not_shift_it_and_two_edits_conserve_page():
    page = "Anchor\n\n## Old\n\nKeep"
    claim = _claim(page, "Anchor")
    choices = [_choice(page, "Old", "Longer", "heading"),
               _choice(page, "Keep", "Kept", "ending")]
    queue = {issue: {"source_page": 1} for issue in ("heading", "ending")}
    assert project_claims([claim], choices, queue, {1: {"markdown": page}}) == []


def test_partial_claim_overlap_remains_rejected():
    page = "## Old\n\nKeep"
    claim = _claim(page, "Keep")
    choice = _choice(page, "Kee", "New", "partial")
    with pytest.raises(SourceChoiceCoverageSuccessorError, match="partially overlaps"):
        project_claims([claim], [choice], {"partial": {"source_page": 1}},
                       {1: {"markdown": page}})
