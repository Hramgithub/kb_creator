"""Claim projection tests; public authority closure uses the real R1 fixture."""
from copy import deepcopy

import pytest

from kb_creator.pipeline import source_choice_coverage_successor as subject
from kb_creator.pipeline.identity import sha256_bytes


def _sha(text):
    return sha256_bytes(text.encode())


def _fixture(replacement="ID6 longer", *, two=False):
    text = "prefix 1D6 middle 1D6 tail"
    anchor = {"view": "raster", "raw_index": 7, "field": "text"}
    choices, queue = [], {}
    for number, (start, end) in enumerate([(7, 10), (18, 21)] if two else [(7, 10)]):
        issue = f"issue-{number}"; source_raw = number + 1
        row = {"issue_id": issue, "disposition": "selected_alternative",
               "r0_reader_span": {"character_start": start, "character_end": end, "text_sha256": _sha(text[start:end])},
               "raw_reader_replay": {"anchor_mode": "composite_source_slice_v1", "anchor_source_locator": anchor,
                   "anchor_container_sha256": _sha(text),
                   "raw_source_slice": {"raw_character_start": start, "raw_character_end": end, "raw_text_sha256": _sha("1D6")}},
               "chosen_raw_alternative": {"source_locator": {"view": "ocr", "raw_index": source_raw, "field": "text"},
                                          "text_sha256": _sha(replacement)},
               "intended_reader_successor": {"text": replacement, "text_sha256": _sha(replacement)}}
        choices.append(row)
        queue[issue] = {"source_page": 1, "source_selector": {"mechanical_diagnostic": {"source_keys": [
            {"view": "txt", "raw_index": source_raw}, {"view": "ocr", "raw_index": source_raw}]}}}
    claims = []
    for name, raw, start, end in [("prefix", 0, 0, 6), ("first", 1, 7, 10), ("second", 2, 18, 21), ("tail", 3, 22, 26)]:
        claims.append({"status": "validated", "claim": {"claim_id": name, "reader_page": 1,
            "source_unit": {"source_page": 1, "view_id": "txt", "raw_index": raw},
            "canonical_unit": {"source_page": 1, "view_id": "raster", "raw_index": 7, "raw_text_sha256": _sha(text)},
            "proof": {"normalized_span": [start, end], "expected_normalized_sha256": _sha(text[start:end])}}})
    return claims, choices, queue, {1: {"markdown": text}}


def test_length_change_preserves_other_claims_on_the_same_container():
    claims, choices, queue, decisions = _fixture()
    original = deepcopy(claims)
    result = subject.project_claims(claims, choices, queue, decisions)
    assert [r["claim_id"] for r in result] == ["first", "second", "tail"]
    assert [r["mode"] for r in result] == ["replaced", "shifted", "shifted"]
    assert [r["r1_normalized_span"] for r in result] == [[7, 17], [25, 28], [29, 33]]
    assert result[1]["r1_normalized_sha256"] == _sha("1D6")
    assert claims == original


def test_choices_on_pages_without_coverage_do_not_enter_coverage_renderer():
    claims, choices, queue, decisions = _fixture()
    expected = subject.project_claims(claims, choices, queue, decisions)
    unrelated = deepcopy(choices[0]); unrelated["issue_id"] = "html-page"
    choices.append(unrelated)
    queue["html-page"] = {"source_page": 2}
    # This syntax is deliberately outside the coverage renderer's contract;
    # it belongs to another pipeline route and has no coverage claim here.
    decisions[2] = {"markdown": "<table>unrelated</table>"}
    assert subject.project_claims(claims, choices, queue, decisions) == expected


@pytest.mark.parametrize("replacement", ["ID6", "ID6\nextra", "ID6   extra"])
def test_two_equal_slices_keep_separate_proofs_and_fold_whitespace(replacement):
    claims, choices, queue, decisions = _fixture(replacement, two=True)
    result = subject.project_claims(claims, choices, queue, decisions)
    first, second = [r for r in result if r["mode"] == "replaced"]
    assert (first["issue_id"], second["issue_id"]) == ("issue-0", "issue-1")
    assert first["r1_normalized_sha256"] == second["r1_normalized_sha256"] == _sha(" ".join(replacement.split()))
    assert first["r1_normalized_span"][1] < second["r1_normalized_span"][0]


@pytest.mark.parametrize("fault", ["source_key", "container_hash", "preimage", "span", "partial_overlap", "duplicate", "selector_instead_of_claim"])
def test_projection_rejects_substituted_claim_identity_or_interval(fault):
    claims, choices, queue, decisions = _fixture()
    first = claims[1]["claim"]
    if fault == "source_key": first["source_unit"]["raw_index"] = 99
    elif fault == "container_hash": first["canonical_unit"]["raw_text_sha256"] = _sha("other")
    elif fault == "preimage": first["proof"]["expected_normalized_sha256"] = _sha("other")
    elif fault == "span": first["proof"]["normalized_span"] = [8, 11]
    elif fault == "partial_overlap":
        first["proof"] = {"normalized_span": [7, 13], "expected_normalized_sha256": _sha("1D6 mi")}
    elif fault == "duplicate": claims.append(deepcopy(claims[1]))
    else: claims[1] = {"claim_id": "first", "source_key": first["source_unit"]}
    with pytest.raises(subject.SourceChoiceCoverageSuccessorError):
        subject.project_claims(claims, choices, queue, decisions)
