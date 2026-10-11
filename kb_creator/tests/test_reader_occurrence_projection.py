"""v2 source/reader occurrence bindings are exact and source-envelope bound."""
from __future__ import annotations

import pytest

from kb_creator.pipeline.identity import sha256_bytes
from kb_creator.pipeline.reader_occurrence_projection import (
    ReaderOccurrenceError,
    apply_bound_reader_replacements,
    project_raw_alternative_to_reader,
    resolve_issue_reader_occurrence,
)


def _sha(value: str) -> str:
    return sha256_bytes(value.encode("utf-8"))


def _issue(text: str, *, key: int = 1) -> dict:
    return {"issue_id": "issue", "source_page": 1, "source_excerpt_en": text,
            "source_excerpt_sha256": _sha(text),
            "source_selector": {"mechanical_diagnostic": {"source_keys": [{"view": "txt", "raw_index": key}]}},
            "candidate_span": {"binding": "ordered_selected_source_v1", "source_key": {"view": "txt", "raw_index": key}, "source_page": 1}}


def _decision(markdown: str) -> dict:
    return {"source_page": 1, "markdown": markdown,
            "selected_blocks": [{"view": "txt", "raw_index": 1}]}


def _audit(length: int) -> dict:
    return {"ordered_proof_stream": [{"kind": "selected", "unit": {"view_id": "txt", "raw_index": 1}, "markdown_span": [0, length]}]}


def test_identity_projection_uses_decision_relative_and_master_separate_spans():
    decision = _decision("Same defense")
    result = resolve_issue_reader_occurrence(_issue("Same defense"), decision, _audit(11), "\nSame defense\n")
    assert result["reader_projection"]["policy"] == "identity_v1"
    assert result["page_reader_span"]["character_start"] == 0
    assert result["page_reader_span"]["character_end"] == 12


def test_display_projection_deduplicates_identity_when_no_display_change():
    decision = _decision("Same defense")
    result = resolve_issue_reader_occurrence(_issue("Same defense"), decision, _audit(11), "\nSame defense\n")
    assert result["reader_projection"]["policy"] == "identity_v1"


def test_heading_display_projection_preserves_wrapper_outside_reader_slice():
    raw = "<sup>Researching</sup> <sub>Winoka</sub> <sub>Point</sub>"
    markdown = "## Researching Winoka Point"
    result = resolve_issue_reader_occurrence(_issue(raw), _decision(markdown), _audit(22), "\n" + markdown + "\n")
    assert result["reader_projection"]["policy"] == "display_text_v1"
    assert result["reader_projection"]["reader_text"] == "Researching Winoka Point"
    assert result["page_reader_span"]["character_start"] == 3


def test_stage05_normalized_proof_does_not_authorize_unrecorded_hardwrap():
    raw = "Christopher Smith"
    markdown = "Chri\nstopher Smith"
    with pytest.raises(ReaderOccurrenceError, match="source_material_blocked"):
        resolve_issue_reader_occurrence(_issue(raw), _decision(markdown), _audit(16), "\n" + markdown + "\n")


def test_normalized_match_outside_proven_stage05_anchor_fails_closed():
    raw = "Christopher Smith"
    with pytest.raises(ReaderOccurrenceError, match="source_material_blocked"):
        resolve_issue_reader_occurrence(_issue(raw), _decision("Other\nChristopher Smith"), _audit(5), "\nOther\nChristopher Smith\n")


@pytest.mark.parametrize("art", [
    "![SO RCE R Y]({{asset:map.png}})",
    "![SO RCE R Y](assets/map.png)",
    "{{asset:map.png}}",
])
@pytest.mark.parametrize("position", ["before", "after", "both"])
def test_ordered_reader_span_excludes_art_and_retains_materialized_offsets(art, position):
    from kb_creator.scripts.materialize_mineru_ai_merge import _substitute_assets
    raw = "SO RCE R Y"
    prefix = "Заголовок\n\n" + (art + "\n\n" if position in {"before", "both"} else "")
    suffix = "\n\n" + (art + "\n\n" if position in {"after", "both"} else "") + "Tail"
    markdown = prefix + raw + suffix
    audit = _audit(7)
    audit["ordered_proof_stream"][0]["markdown_span"] = [9, 16]
    assets = {"map.png": "assets/longer-materialized-map-name.png"}
    materialized = _substitute_assets(markdown, assets, "")
    result = resolve_issue_reader_occurrence(_issue(raw), _decision(markdown), audit,
                                            "\n" + materialized + "\n", asset_paths=assets)
    span = result["page_reader_span"]
    assert span["character_start"] == len(prefix)
    assert markdown[span["character_start"]:span["character_end"]] == raw
    target = result["materialized_page_reader_span"]
    assert ("\n" + materialized)[target["character_start"]:target["character_end"]] == raw


def test_art_alt_text_cannot_satisfy_missing_reader_occurrence():
    markdown = "![SO RCE R Y](assets/map.png)\n\nOTHER!!"
    with pytest.raises(ReaderOccurrenceError, match="source_material_blocked"):
        resolve_issue_reader_occurrence(_issue("SO RCE R Y"), _decision(markdown), _audit(5),
                                        "\n" + markdown + "\n")


def test_bound_replacements_use_exact_nonoverlapping_decision_spans():
    value, deltas = apply_bound_reader_replacements("one two three", [
        {"page_reader_span": {"character_start": 4, "character_end": 7}, "before": "two", "after": "second"},
        {"page_reader_span": {"character_start": 8, "character_end": 13}, "before": "three", "after": "third"},
    ])
    assert value == "one second third"
    assert len(deltas) == 2
    with pytest.raises(ReaderOccurrenceError, match="overlap"):
        apply_bound_reader_replacements("abcdef", [{"span": {"character_start": 1, "character_end": 3}, "before": "bc", "after": "x"}, {"span": {"character_start": 2, "character_end": 4}, "before": "cd", "after": "y"}])


def _corrected_occurrence(*, heading=False):
    from kb_creator.pipeline.semantic_structure import _normalized

    raw = "Bad threeword heading."
    corrected = "Good three-word heading."
    markdown = ("## " if heading else "") + corrected
    decision = _decision(markdown)
    decision["semantic_structure"] = {"units": [{
        "id": "title", "kind": "heading" if heading else "label",
        "representation": "semantic_span", "source_blocks": [{"view": "txt", "raw_index": 1}],
        "markdown_span": {"start_line": 1, "end_line": 1, "sha256": _sha(markdown)},
    }]}
    # Deliberately reverse source order: projection must not depend on row order.
    decision["reviewed_block_corrections"] = [
        {"view": "txt", "raw_index": 1, "before": before, "after": after,
         "original_text_sha256": _sha(raw), "reason": "source review"}
        for before, after in [("threeword", "three-word"), ("Bad", "Good")]]
    audit = _audit(len(_normalized(markdown)))
    audit["ordered_proof_stream"][0]["unit"]["original_text_sha256"] = _sha(raw)
    return _issue(raw), decision, audit, "\n" + markdown + "\n", {("txt", 1): {"text": raw}}


@pytest.mark.parametrize("heading", [False, True])
def test_reviewed_correction_projects_exact_complete_source_with_wrapper_outside(heading):
    issue, decision, audit, page, blocks = _corrected_occurrence(heading=heading)
    result = resolve_issue_reader_occurrence(issue, decision, audit, page, packet_blocks=blocks)
    assert result["reader_projection"]["policy"] == "reviewed_block_correction_v1"
    assert result["reader_projection"]["reader_text"] == "Good three-word heading."
    assert result["page_reader_span"]["character_start"] == (3 if heading else 0)
    assert issue["source_excerpt_en"] == "Bad threeword heading."


def test_reviewed_correction_projects_exact_complete_source_through_strong_markdown():
    issue, decision, audit, _page, blocks = _corrected_occurrence()
    decision["markdown"] = "- Good **three-word** heading."
    decision["semantic_structure"]["units"][0]["markdown_span"]["sha256"] = _sha(decision["markdown"])
    audit["ordered_proof_stream"][0]["markdown_span"] = [0, 20]
    result = resolve_issue_reader_occurrence(
        issue, decision, audit, "\n" + decision["markdown"] + "\n", packet_blocks=blocks)
    assert result["reader_projection"]["policy"] == "reviewed_block_correction_strong_display_v1"
    assert result["reader_projection"]["reader_text"] == "Good **three-word** heading."
    assert result["page_reader_span"]["character_start"] == 2


@pytest.mark.parametrize("markdown", [
    "- Good **threeword heading.",
    "- Good **three-word heading?",
    "- Good **three-word** heading.\n\nGood **three-word** heading.",
])
def test_reviewed_correction_strong_projection_rejects_unbalanced_drift_and_ambiguity(markdown):
    issue, decision, audit, _page, blocks = _corrected_occurrence()
    decision["markdown"] = markdown
    decision["semantic_structure"]["units"][0]["markdown_span"]["sha256"] = _sha(markdown)
    audit["ordered_proof_stream"][0]["markdown_span"] = [0, sum(char.isalnum() for char in markdown)]
    with pytest.raises(ReaderOccurrenceError):
        resolve_issue_reader_occurrence(issue, decision, audit, "\n" + markdown + "\n", packet_blocks=blocks)


@pytest.mark.parametrize("mutation", [
    "missing_packet", "changed_packet", "partial_excerpt", "stale_stage05",
    "stale_correction_hash", "stale_semantic_span", "wrong_source_key",
])
def test_reviewed_correction_occurrence_rejects_broken_source_proof(mutation):
    issue, decision, audit, page, blocks = _corrected_occurrence()
    if mutation == "missing_packet":
        blocks = None
    elif mutation == "changed_packet":
        blocks[("txt", 1)]["text"] += " extra"
    elif mutation == "partial_excerpt":
        issue["source_excerpt_en"] = "threeword"
        issue["source_excerpt_sha256"] = _sha("threeword")
    elif mutation == "stale_stage05":
        audit["ordered_proof_stream"][0]["unit"]["original_text_sha256"] = "0" * 64
    elif mutation == "stale_correction_hash":
        decision["reviewed_block_corrections"][0]["original_text_sha256"] = "0" * 64
    elif mutation == "stale_semantic_span":
        decision["semantic_structure"]["units"][0]["markdown_span"]["sha256"] = "0" * 64
    else:
        decision["semantic_structure"]["units"][0]["source_blocks"][0]["raw_index"] = 2
    with pytest.raises(ReaderOccurrenceError):
        resolve_issue_reader_occurrence(issue, decision, audit, page, packet_blocks=blocks)
