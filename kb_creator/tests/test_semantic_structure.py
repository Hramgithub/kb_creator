import hashlib
import json
from pathlib import Path

import pytest

from kb_creator.pipeline.semantic_structure import (
    _validate_v2_role_contract,
    apply_reviewed_text_corrections,
    SemanticStructureError,
    reviewed_block_text_correction_candidates,
    reviewed_block_text_corrections,
    collect_reference_image_proof_keys,
    _syntax_errors,
    validate_canonical_blank_separators,
    validate_semantic_structure,
    validate_selected_title_coverage,
)


def _span(lines, start, end):
    return {"start_line": start, "end_line": end, "sha256": hashlib.sha256("\n".join(lines[start - 1:end]).encode()).hexdigest().upper()}


def _fixture(*, placement="reference_only"):
    lines = ["## Record", "> Note", ">", "> - one", "> - two", "", "| STR | CON |", "| --- | --- |", "| 50 | 60 |"]
    markdown = "\n".join(lines)
    visual = {"path": "outputs/04-visual-merge-bundle/visual/original_pipeline_txt/pages/page-001.png", "bytes": 1, "sha256": "A" * 64}
    packet = {"views": {"original_pipeline_txt": {"blocks": [
        {"raw_index": 0, "assets": []}, {"raw_index": 1, "assets": ["images/stats.png"]},
    ]}}}
    unit = lambda identity, kind, representation, source, start, end, **extra: {
        "id": identity, "kind": kind, "representation": representation, "source_blocks": [{"view": "original_pipeline_txt", "raw_index": source}], "markdown_span": _span(lines, start, end), "container_parent": None, "semantic_parent": "record" if identity != "record" else None, "continuation_of": None, "heading_level": 2 if kind == "heading" else None, "item_count": 2 if kind == "list" else None, **extra,
    }
    decision = {"markdown": markdown, "selected_blocks": [{"view": "original_pipeline_txt", "raw_index": 0, "purpose": "text"}, {"view": "original_pipeline_txt", "raw_index": 1, "purpose": "structure"}], "assets": [{"view": "original_pipeline_txt", "source_path": "images/stats.png", "logical_name": "stats.png", "placement": placement}], "semantic_structure": {"schema": "kb_creator.page_semantic_structure.v1", "review": {"state": "complete", "visual": visual}, "units": [unit("record", "heading", "atx_heading", 0, 1, 1), unit("note", "handout", "blockquote", 0, 2, 5), unit("stats", "statblock", "table", 1, 7, 9)]}}
    return {1: decision}, {1: packet}, {visual["path"]: {"bytes": 1, "sha256": "A" * 64}}


def test_reference_only_asset_permits_semantic_table_without_duplicate_image():
    decisions, packets, visuals = _fixture()
    report = validate_semantic_structure(decisions, packets, visuals, required_pages=[1])
    assert report["pages"][0]["validated_unit_count"] == 3


def test_selected_title_coverage_requires_one_complete_source_partition():
    key = ("txt", 7)
    decision = {"selected_blocks": [{"view": "txt", "raw_index": 7, "purpose": "text"}]}
    blocks = {key: {"text": "Exact title", "semantic_evidence": {"v2_title": True}}}
    unit = {"kind": "heading", "representation": "atx_heading", "source_fragments": [
        {"view": "txt", "raw_index": 7, "start": 0, "end": 11},
    ]}
    validate_selected_title_coverage(1, decision, blocks, [unit])
    unit["source_fragments"][0]["end"] = 10
    with pytest.raises(SemanticStructureError, match="title_coverage_fragment_partition"):
        validate_selected_title_coverage(1, decision, blocks, [unit])
    with pytest.raises(SemanticStructureError, match="title_coverage_missing"):
        validate_selected_title_coverage(1, decision, blocks, [])


def test_final_validator_accepts_only_a_verified_ordinary_prose_correction():
    source, reader = "The girl's coat is blue.", "The girl’s coat is blue."
    lines = ["# Heading", "", reader]
    visual = {"path": "outputs/04-visual-merge-bundle/visual/original_pipeline_txt/pages/page-001.png", "bytes": 1, "sha256": "A" * 64}
    decision = {
        "markdown": "\n".join(lines),
        "selected_blocks": [
            {"view": "original_pipeline_txt", "raw_index": 0, "purpose": "structure"},
            {"view": "original_pipeline_txt", "raw_index": 1, "purpose": "text"},
        ],
        "reviewed_block_corrections": [{
            "view": "original_pipeline_txt", "raw_index": 1, "before": "girl's", "after": "girl’s",
            "reason": "reviewed source", "original_text_sha256": hashlib.sha256(source.encode()).hexdigest().upper(),
        }],
        "reviewed_prose_bindings_v1": [{
            "view": "original_pipeline_txt", "raw_index": 1,
            "original_text_sha256": hashlib.sha256(source.encode()).hexdigest().upper(),
            "markdown_span": _span(lines, 3, 3),
        }],
        "assets": [],
        "semantic_structure": {"schema": "kb_creator.page_semantic_structure.v1", "review": {"state": "complete", "visual": visual}, "units": [{
            "id": "heading", "kind": "heading", "representation": "atx_heading",
            "source_blocks": [{"view": "original_pipeline_txt", "raw_index": 0}],
            "markdown_span": _span(lines, 1, 1), "container_parent": None,
            "semantic_parent": None, "continuation_of": None, "heading_level": 1, "item_count": None,
        }]},
    }
    packet = {"views": {"original_pipeline_txt": {"blocks": [
        {"raw_index": 0, "text": "Heading", "assets": []},
        {"raw_index": 1, "text": source, "assets": []},
    ]}}}
    assert validate_semantic_structure({1: decision}, {1: packet}, {visual["path"]: {"bytes": 1, "sha256": "A" * 64}}, required_pages=[1])["pages"][0]["validated_unit_count"] == 1
    del decision["reviewed_prose_bindings_v1"]
    with pytest.raises(SemanticStructureError, match="semantic unit"):
        validate_semantic_structure({1: decision}, {1: packet}, {visual["path"]: {"bytes": 1, "sha256": "A" * 64}}, required_pages=[1])


def test_inline_asset_requires_placeholder_inside_declared_span():
    decisions, packets, visuals = _fixture(placement="inline")
    with pytest.raises(SemanticStructureError, match="inline semantic asset"):
        validate_semantic_structure(decisions, packets, visuals, required_pages=[1])


def test_flattened_handout_fails_even_when_text_is_present():
    decisions, packets, visuals = _fixture()
    decisions[1]["markdown"] = decisions[1]["markdown"].replace("> Note", "Note")
    with pytest.raises(SemanticStructureError, match="markdown span"):
        validate_semantic_structure(decisions, packets, visuals, required_pages=[1])


def test_source_citation_and_explicit_nested_list_are_closed():
    decisions, packets, visuals = _fixture()
    lines = decisions[1]["markdown"].split("\n")
    note = decisions[1]["semantic_structure"]["units"][1]
    nested = {"id": "note-list", "kind": "list", "representation": "unordered_list", "source_blocks": [{"view": "original_pipeline_txt", "raw_index": 0}], "markdown_span": _span(lines, 4, 5), "container_parent": "note", "semantic_parent": "record", "continuation_of": None, "heading_level": None, "item_count": 2}
    decisions[1]["semantic_structure"]["units"].insert(2, nested)
    assert validate_semantic_structure(decisions, packets, visuals, required_pages=[1])["pages"][0]["validated_unit_count"] == 4
    nested["source_blocks"] = [{"view": "original_pipeline_txt", "raw_index": 99}]
    with pytest.raises(SemanticStructureError, match="source block"):
        validate_semantic_structure(decisions, packets, visuals, required_pages=[1])


def test_ordered_source_text_allows_prefix_repeated_in_later_block():
    visual = {"path": "outputs/04-visual-merge-bundle/visual/original_pipeline_txt/pages/page-001.png", "bytes": 1, "sha256": "A" * 64}
    lines = ["> Dad", "> Daddy will help"]
    decision = {
        "markdown": "\n".join(lines),
        "selected_blocks": [
            {"view": "original_pipeline_txt", "raw_index": 0, "purpose": "text"},
            {"view": "original_pipeline_txt", "raw_index": 1, "purpose": "text"},
        ],
        "assets": [],
        "semantic_structure": {
            "schema": "kb_creator.page_semantic_structure.v1",
            "review": {"state": "complete", "visual": visual},
            "units": [{
                "id": "letter", "kind": "handout", "representation": "blockquote",
                "source_blocks": [
                    {"view": "original_pipeline_txt", "raw_index": 0},
                    {"view": "original_pipeline_txt", "raw_index": 1},
                ],
                "markdown_span": _span(lines, 1, 2), "container_parent": None,
                "semantic_parent": None, "continuation_of": None,
                "heading_level": None, "item_count": None,
            }],
        },
    }
    packet = {"views": {"original_pipeline_txt": {"blocks": [
        {"raw_index": 0, "text": "Dad", "assets": []},
        {"raw_index": 1, "text": "Daddy will help", "assets": []},
    ]}}}
    report = validate_semantic_structure(
        {1: decision}, {1: packet}, {visual["path"]: {"bytes": 1, "sha256": "A" * 64}},
        required_pages=[1],
    )
    assert report["pages"][0]["validated_unit_count"] == 1


def test_reviewed_exact_text_correction_binds_source_evidence_to_markdown():
    visual = {"path": "outputs/04-visual-merge-bundle/visual/original_pipeline_txt/pages/page-001.png", "bytes": 1, "sha256": "A" * 64}
    lines = ["> Don't stop"]
    source = {"view": "original_pipeline_txt", "raw_index": 0}
    decision = {
        "markdown": lines[0], "selected_blocks": [{**source, "purpose": "text"}], "assets": [],
        "review": {"visual_reviewed": True, "notes": "text correction: Dou't -> Don't; reason: full-resolution source visual confirms the apostrophe"},
        "semantic_structure": {"schema": "kb_creator.page_semantic_structure.v1", "review": {"state": "complete", "visual": visual}, "units": [{
            "id": "letter", "kind": "handout", "representation": "blockquote", "source_blocks": [source],
            "markdown_span": _span(lines, 1, 1), "container_parent": None, "semantic_parent": None,
            "continuation_of": None, "heading_level": None, "item_count": None,
        }]},
    }
    packet = {"views": {"original_pipeline_txt": {"blocks": [{"raw_index": 0, "text": "Dou't stop", "assets": []}]}}}
    report = validate_semantic_structure({1: decision}, {1: packet}, {visual["path"]: {"bytes": 1, "sha256": "A" * 64}}, required_pages=[1])
    assert report["pages"][0]["validated_unit_count"] == 1


def test_reviewed_block_correction_is_scoped_to_named_repeated_source_block():
    text = "Gear: Any the player and Keeper seems fit."
    blocks = {
        ("original_pipeline_txt", 0): {"text": text},
        ("original_pipeline_txt", 1): {"text": text},
    }
    decision = {"selected_blocks": [
        {"view": "original_pipeline_txt", "raw_index": 0, "purpose": "text"},
        {"view": "original_pipeline_txt", "raw_index": 1, "purpose": "text"},
    ], "reviewed_block_corrections": [{
        "view": "original_pipeline_txt", "raw_index": 0,
        "before": "seems fit", "after": "sees fit", "reason": "source render",
        "original_text_sha256": hashlib.sha256(text.encode()).hexdigest().upper(),
    }]}
    markdown = "> Gear: Any the player and Keeper sees fit."
    corrections = reviewed_block_text_corrections(
        decision, blocks, set(blocks), markdown, 1,
        semantic_units=[{
            "source_blocks": [{"view": "original_pipeline_txt", "raw_index": 0}],
            "markdown_span": _span(markdown.split("\n"), 1, 1),
        }],
    )
    assert apply_reviewed_text_corrections(text, ("original_pipeline_txt", 0), [], corrections).endswith("sees fit.")
    assert apply_reviewed_text_corrections(text, ("original_pipeline_txt", 1), [], corrections).endswith("seems fit.")


@pytest.mark.parametrize(
    "row, error",
    [
        ({"view": "wrong", "raw_index": 0}, "not selected"),
        ({"view": "original_pipeline_txt", "raw_index": 9}, "not selected"),
        ({"view": "original_pipeline_txt", "raw_index": 0, "original_text_sha256": "0" * 64}, "evidence"),
        ({"view": "original_pipeline_txt", "raw_index": 0, "before": "absent"}, "exactly once"),
        ({"view": "original_pipeline_txt", "raw_index": 0, "after": ""}, "evidence"),
    ],
)
def test_reviewed_block_correction_rejects_wrong_identity_hash_and_text(row, error):
    text = "Gear: seems fit"
    complete = {
        "view": "original_pipeline_txt", "raw_index": 0,
        "before": "seems fit", "after": "sees fit", "reason": "source render",
        "original_text_sha256": hashlib.sha256(text.encode()).hexdigest().upper(),
    }
    complete.update(row)
    with pytest.raises(SemanticStructureError, match=error):
        reviewed_block_text_corrections(
            {"selected_blocks": [{"view": "original_pipeline_txt", "raw_index": 0, "purpose": "text"}], "reviewed_block_corrections": [complete]},
            {("original_pipeline_txt", 0): {"text": text}},
            {("original_pipeline_txt", 0)}, "> Gear: sees fit", 1,
        )


def test_reviewed_block_correction_rejects_duplicate_or_overlapping_rows():
    text = "Angelo's .38 Revolver (27/11), damage 1D10."
    row = {
        "view": "original_pipeline_txt", "raw_index": 0,
        "before": "(27/11)", "after": "Revolver (27/11)", "reason": "source label",
        "original_text_sha256": hashlib.sha256(text.encode()).hexdigest().upper(),
    }
    with pytest.raises(SemanticStructureError, match="overlapping or duplicate"):
        reviewed_block_text_corrections(
            {"selected_blocks": [{"view": "original_pipeline_txt", "raw_index": 0, "purpose": "text"}], "reviewed_block_corrections": [row, row.copy()]},
            {("original_pipeline_txt", 0): {"text": text}},
            {("original_pipeline_txt", 0)}, "Revolver (27/11)", 1,
            semantic_units=[{
                "source_blocks": [{"view": "original_pipeline_txt", "raw_index": 0}],
                "markdown_span": _span(["Revolver (27/11)"], 1, 1),
            }],
        )
    overlapping = [
        {**row, "before": "Revolver", "after": "Pistol"},
        {**row, "before": "Revolver (27/11)", "after": "Pistol (27/11)"},
    ]
    with pytest.raises(SemanticStructureError, match="overlapping or duplicate"):
        reviewed_block_text_corrections(
            {"selected_blocks": [{"view": "original_pipeline_txt", "raw_index": 0, "purpose": "text"}], "reviewed_block_corrections": overlapping},
            {("original_pipeline_txt", 0): {"text": text}},
            {("original_pipeline_txt", 0)}, "Pistol (27/11)", 1,
            semantic_units=[{
                "source_blocks": [{"view": "original_pipeline_txt", "raw_index": 0}],
                "markdown_span": _span(["Pistol (27/11)"], 1, 1),
            }],
        )


def test_semantic_validator_does_not_leak_block_correction_to_peer_block():
    visual = {"path": "outputs/04-visual-merge-bundle/visual/original_pipeline_txt/pages/page-001.png", "bytes": 1, "sha256": "A" * 64}
    text = "Gear: seems fit"
    lines = ["> Gear: sees fit", "> Gear: sees fit"]
    refs = [{"view": "original_pipeline_txt", "raw_index": index} for index in (0, 1)]
    units = [{
        "id": f"gear-{index}", "kind": "handout", "representation": "blockquote",
        "source_blocks": [refs[index]], "markdown_span": _span(lines, index + 1, index + 1),
        "container_parent": None, "semantic_parent": None, "continuation_of": None,
        "heading_level": None, "item_count": None,
    } for index in (0, 1)]
    decision = {
        "markdown": "\n".join(lines),
        "selected_blocks": [{**ref, "purpose": "text"} for ref in refs], "assets": [],
        "reviewed_block_corrections": [{
            "view": "original_pipeline_txt", "raw_index": 0, "before": "seems fit",
            "after": "sees fit", "reason": "source render",
            "original_text_sha256": hashlib.sha256(text.encode()).hexdigest().upper(),
        }],
        "semantic_structure": {"schema": "kb_creator.page_semantic_structure.v1", "review": {"state": "complete", "visual": visual}, "units": units},
    }
    packet = {"views": {"original_pipeline_txt": {"blocks": [
        {"raw_index": 0, "text": text, "assets": []},
        {"raw_index": 1, "text": text, "assets": []},
    ]}}}
    with pytest.raises(SemanticStructureError, match="text source is absent"):
        validate_semantic_structure({1: decision}, {1: packet}, {visual["path"]: {"bytes": 1, "sha256": "A" * 64}}, required_pages=[1])


def _projected_block_correction_fixture(markdown, corrected_text, *, kind, representation):
    lines = markdown.split("\n")
    visual = {"path": "outputs/04-visual-merge-bundle/visual/original_pipeline_txt/pages/page-001.png", "bytes": 1, "sha256": "A" * 64}
    source = {"view": "original_pipeline_txt", "raw_index": 4}
    unit = {
        "id": "corrected", "kind": kind, "representation": representation,
        "source_blocks": [source], "markdown_span": _span(lines, 1, 1),
        "container_parent": None, "semantic_parent": None, "continuation_of": None,
        "heading_level": 1 if kind == "heading" else None,
        "item_count": 1 if kind == "list" else None,
    }
    decision = {
        "markdown": markdown, "selected_blocks": [{**source, "purpose": "text"}], "assets": [],
        "reviewed_block_corrections": [{
            **source, "before": "Bad source", "after": corrected_text,
            "reason": "reviewed source evidence",
            "original_text_sha256": hashlib.sha256(b"Bad source").hexdigest().upper(),
        }],
        "semantic_structure": {"schema": "kb_creator.page_semantic_structure.v1", "review": {"state": "complete", "visual": visual}, "units": [unit]},
    }
    packet = {"views": {"original_pipeline_txt": {"blocks": [{"raw_index": 4, "text": "Bad source", "assets": []}]}}}
    return {1: decision}, {1: packet}, {visual["path"]: {"bytes": 1, "sha256": "A" * 64}}


@pytest.mark.parametrize(
    "markdown,corrected_text,kind,representation",
    [
        ("# **Corrected** heading", "Corrected heading", "heading", "atx_heading"),
        ("- Corrected *list*", "Corrected list", "list", "unordered_list"),
        ("> Corrected **quote**", "Corrected quote", "handout", "blockquote"),
    ],
)
def test_block_correction_uses_one_bound_visible_unit_for_presentation_markers(
    markdown, corrected_text, kind, representation,
):
    decisions, packets, visuals = _projected_block_correction_fixture(
        markdown, corrected_text, kind=kind, representation=representation,
    )
    assert validate_semantic_structure(decisions, packets, visuals, required_pages=[1])["pages"][0]["validated_unit_count"] == 1


def test_block_correction_accepts_source_bullet_for_bound_unordered_list():
    decisions, packets, visuals = _projected_block_correction_fixture(
        "- The only other witness saw the train.",
        "• The only other witness saw the train.",
        kind="list", representation="unordered_list",
    )
    assert validate_semantic_structure(decisions, packets, visuals, required_pages=[1])["pages"][0]["validated_unit_count"] == 1


def test_block_correction_requires_reader_visible_text_even_when_raw_markdown_contains_it():
    hidden, packets, visuals = _projected_block_correction_fixture(
        "# Read [public label](HiddenCorrected) now.", "HiddenCorrected",
        kind="heading", representation="atx_heading",
    )
    with pytest.raises(SemanticStructureError, match="bound visible span"):
        validate_semantic_structure(hidden, packets, visuals, required_pages=[1])

    visible, packets, visuals = _projected_block_correction_fixture(
        "# Read [VisibleCorrected](https://example.test) now.", "VisibleCorrected",
        kind="heading", representation="atx_heading",
    )
    assert validate_semantic_structure(visible, packets, visuals, required_pages=[1])["pages"][0]["validated_unit_count"] == 1


def test_block_correction_uses_source_interval_to_bind_one_v2_fragment_unit():
    text = "Title\nBad source"
    key = ("original_pipeline_txt", 4)
    markdown = "# Title\nVisibleCorrected"

    def fragment(start, end):
        value = text[start:end]
        return {
            "view": key[0], "raw_index": key[1],
            "source_sha256": hashlib.sha256(text.encode()).hexdigest().upper(),
            "normalized_sha256": hashlib.sha256(
                "".join(char for char in value.casefold() if char.isalnum()).encode()
            ).hexdigest().upper(),
            "start": start, "end": end,
            "fragment_sha256": hashlib.sha256(value.encode()).hexdigest().upper(),
        }

    decision = {
        "selected_blocks": [{"view": key[0], "raw_index": key[1], "purpose": "text"}],
        "reviewed_block_corrections": [{
            "view": key[0], "raw_index": key[1], "before": "Bad source",
            "after": "VisibleCorrected", "reason": "reviewed source evidence",
            "original_text_sha256": hashlib.sha256(text.encode()).hexdigest().upper(),
        }],
    }
    units = [
        {"source_blocks": [{"view": key[0], "raw_index": key[1]}], "source_fragments": [fragment(0, 6)], "markdown_span": _span(markdown.split("\n"), 1, 1)},
        {"source_blocks": [{"view": key[0], "raw_index": key[1]}], "source_fragments": [fragment(6, len(text))], "markdown_span": _span(markdown.split("\n"), 2, 2)},
    ]
    corrections = reviewed_block_text_corrections(
        decision, {key: {"text": text}}, {key}, markdown, 1, semantic_units=units,
    )
    assert corrections[key] == [("Bad source", "VisibleCorrected")]


def test_block_correction_without_semantic_units_fails_closed():
    text = "Bad source"
    key = ("original_pipeline_txt", 4)
    decision = {
        "selected_blocks": [{"view": key[0], "raw_index": key[1], "purpose": "text"}],
        "reviewed_block_corrections": [{
            "view": key[0], "raw_index": key[1], "before": text, "after": "VisibleCorrected",
            "reason": "reviewed source evidence",
            "original_text_sha256": hashlib.sha256(text.encode()).hexdigest().upper(),
        }],
    }
    with pytest.raises(SemanticStructureError, match="requires a semantic unit binding"):
        reviewed_block_text_corrections(decision, {key: {"text": text}}, {key}, "# VisibleCorrected", 1)
    assert reviewed_block_text_correction_candidates(decision, {key: {"text": text}}, {key}, 1)[key] == [(text, "VisibleCorrected")]


@pytest.mark.parametrize(
    "markdown,corrected_text,kind,representation",
    [
        ("> The only other witness saw the train.", "• The only other witness saw the train.", "handout", "blockquote"),
        ("- The only other witness saw the train.", "intro • The only other witness saw the train.", "list", "unordered_list"),
        ("- The only other witness saw the train.", "• The only other witness saw the train!", "list", "unordered_list"),
    ],
)
def test_block_correction_rejects_unproven_or_inexact_source_bullet_equivalence(
    markdown, corrected_text, kind, representation,
):
    decisions, packets, visuals = _projected_block_correction_fixture(
        markdown, corrected_text, kind=kind, representation=representation,
    )
    with pytest.raises(SemanticStructureError, match="bound visible span"):
        validate_semantic_structure(decisions, packets, visuals, required_pages=[1])


def test_projected_block_correction_rejects_unrelated_ambiguous_or_stale_unit_binding():
    decisions, packets, visuals = _projected_block_correction_fixture(
        "ignored\n> Corrected **quote**", "Corrected quote", kind="handout", representation="blockquote",
    )
    unit = decisions[1]["semantic_structure"]["units"][0]
    unit["markdown_span"] = _span(decisions[1]["markdown"].split("\n"), 1, 1)
    with pytest.raises(SemanticStructureError, match="bound visible span"):
        validate_semantic_structure(decisions, packets, visuals, required_pages=[1])

    decisions, packets, visuals = _projected_block_correction_fixture(
        "> Corrected **quote**", "Corrected quote", kind="handout", representation="blockquote",
    )
    duplicate = {**decisions[1]["semantic_structure"]["units"][0], "id": "duplicate"}
    decisions[1]["semantic_structure"]["units"].append(duplicate)
    with pytest.raises(SemanticStructureError, match="exactly one semantic unit"):
        validate_semantic_structure(decisions, packets, visuals, required_pages=[1])

    decisions, packets, visuals = _projected_block_correction_fixture(
        "> Corrected **quote**", "Corrected quote", kind="handout", representation="blockquote",
    )
    decisions[1]["semantic_structure"]["units"][0]["markdown_span"]["sha256"] = "0" * 64
    with pytest.raises(SemanticStructureError, match="correction unit has invalid markdown span"):
        validate_semantic_structure(decisions, packets, visuals, required_pages=[1])


def test_unreviewed_or_stale_text_correction_fails_closed():
    visual = {"path": "outputs/04-visual-merge-bundle/visual/original_pipeline_txt/pages/page-001.png", "bytes": 1, "sha256": "A" * 64}
    lines = ["> Don't stop"]
    source = {"view": "original_pipeline_txt", "raw_index": 0}
    decision = {
        "markdown": lines[0], "selected_blocks": [{**source, "purpose": "text"}], "assets": [],
        "semantic_structure": {"schema": "kb_creator.page_semantic_structure.v1", "review": {"state": "complete", "visual": visual}, "units": [{
            "id": "letter", "kind": "handout", "representation": "blockquote", "source_blocks": [source],
            "markdown_span": _span(lines, 1, 1), "container_parent": None, "semantic_parent": None,
            "continuation_of": None, "heading_level": None, "item_count": None,
        }]},
    }
    packet = {"views": {"original_pipeline_txt": {"blocks": [{"raw_index": 0, "text": "Dou't stop", "assets": []}]}}}
    decisions, packets = {1: decision}, {1: packet}
    visuals = {visual["path"]: {"bytes": 1, "sha256": "A" * 64}}
    with pytest.raises(SemanticStructureError, match="text source is absent"):
        validate_semantic_structure(decisions, packets, visuals, required_pages=[1])
    decision["review"] = {
        "visual_reviewed": True,
        "notes": "text correction: Missing -> Present; reason: deliberately stale fixture",
    }
    with pytest.raises(SemanticStructureError, match="source must occur exactly once"):
        validate_semantic_structure(decisions, packets, visuals, required_pages=[1])


def test_nested_blockquote_heading_may_share_container_first_line():
    visual = {"path": "outputs/04-visual-merge-bundle/visual/original_pipeline_txt/pages/page-001.png", "bytes": 1, "sha256": "A" * 64}
    lines = ["> # Card title", ">", "> Body"]
    source = {"view": "original_pipeline_txt", "raw_index": 0}
    parent = {
        "id": "card", "kind": "handout", "representation": "blockquote", "source_blocks": [source],
        "markdown_span": _span(lines, 1, 3), "container_parent": None, "semantic_parent": None,
        "continuation_of": None, "heading_level": None, "item_count": None,
    }
    child = {
        "id": "card-title", "kind": "heading", "representation": "atx_heading", "source_blocks": [source],
        "markdown_span": _span(lines, 1, 1), "container_parent": "card", "semantic_parent": None,
        "continuation_of": None, "heading_level": 1, "item_count": None,
    }
    decision = {
        "markdown": "\n".join(lines), "selected_blocks": [{**source, "purpose": "structure"}], "assets": [],
        "semantic_structure": {"schema": "kb_creator.page_semantic_structure.v1", "review": {"state": "complete", "visual": visual}, "units": [parent, child]},
    }
    packet = {"views": {"original_pipeline_txt": {"blocks": [{"raw_index": 0, "text": "Card title", "assets": []}]}}}
    report = validate_semantic_structure({1: decision}, {1: packet}, {visual["path"]: {"bytes": 1, "sha256": "A" * 64}}, required_pages=[1])
    assert report["pages"][0]["validated_unit_count"] == 2


def _line_group_fixture(markdown="STR 40 CON 45  \nLuck 65  \nHP 11"):
    visual = {"path": "outputs/04-visual-merge-bundle/visual/original_pipeline_txt/pages/page-001.png", "bytes": 1, "sha256": "A" * 64}
    lines = markdown.split("\n")
    sources = [
        {"view": "original_pipeline_txt", "raw_index": 2},
        {"view": "original_pipeline_txt", "raw_index": 1},
        {"view": "original_pipeline_txt", "raw_index": 3},
    ]
    decision = {
        "markdown": markdown,
        "selected_blocks": [{**source, "purpose": "structure"} for source in sources],
        "assets": [],
        "semantic_structure": {
            "schema": "kb_creator.page_semantic_structure.v1",
            "review": {"state": "complete", "visual": visual},
            "units": [{
                "id": "character-fields", "kind": "line_group", "representation": "hard_break_lines",
                "source_blocks": sources, "markdown_span": _span(lines, 1, len(lines)),
                "container_parent": None, "semantic_parent": None, "continuation_of": None,
                "heading_level": None, "item_count": None,
            }],
        },
    }
    packet = {"views": {"original_pipeline_txt": {"blocks": [
        {"raw_index": 1, "text": "Luck 65", "assets": []},
        {"raw_index": 2, "text": "STR 40 CON 45", "assets": []},
        {"raw_index": 3, "text": "HP 11", "assets": []},
    ]}}}
    return {1: decision}, {1: packet}, {visual["path"]: {"bytes": 1, "sha256": "A" * 64}}


def test_hard_break_line_group_binds_reviewed_source_order_and_topology():
    decisions, packets, visuals = _line_group_fixture()
    report = validate_semantic_structure(decisions, packets, visuals, required_pages=[1])
    assert report["pages"][0]["units"][0]["representation"] == "hard_break_lines"


@pytest.mark.parametrize(
    "markdown,error",
    [
        ("STR 40 CON 45\nLuck 65  \nHP 11", "missing a Markdown hard break"),
        ("STR 40 CON 45  \n\nLuck 65  \nHP 11", "source/reader line count mismatch"),
        ("Luck 65  \nSTR 40 CON 45  \nHP 11", "text source is absent|source order or line mapping mismatch"),
        ("STR 40 CON 45  \nLuck 65  \nHP 11  ", "final line must not carry"),
    ],
)
def test_hard_break_line_group_rejects_spacing_and_order_mutations(markdown, error):
    decisions, packets, visuals = _line_group_fixture(markdown)
    with pytest.raises(SemanticStructureError, match=error):
        validate_semantic_structure(decisions, packets, visuals, required_pages=[1])


def test_hard_break_line_group_supports_multiple_lines_from_one_source_block():
    decisions, packets, visuals = _line_group_fixture("STR 40 CON 45  \nLuck 65  \nHP 11")
    source = {"view": "original_pipeline_txt", "raw_index": 9}
    decisions[1]["selected_blocks"] = [{**source, "purpose": "structure"}]
    unit = decisions[1]["semantic_structure"]["units"][0]
    unit["source_blocks"] = [source]
    packets[1]["views"]["original_pipeline_txt"]["blocks"] = [{
        "raw_index": 9, "text": "STR 40 CON 45   \nLuck 65   \nHP 11", "assets": [],
    }]
    assert validate_semantic_structure(decisions, packets, visuals, required_pages=[1])["pages"][0]["validated_unit_count"] == 1


def _title_conflict_fixture(*, source="THE ENLIGHTENEDWEBSITE", reader="THE ENLIGHTENED WEBSITE", notes=None):
    visual = {"path": "outputs/04-visual-merge-bundle/visual/original_pipeline_txt/pages/page-001.png", "bytes": 1, "sha256": "A" * 64}
    lines = [f"## {reader}"]
    source_ref = {"view": "original_pipeline_txt", "raw_index": 7}
    if notes is None:
        notes = (
            f"text correction: {source} -> {reader}; reason: reviewed visual\n"
            f"title evidence confirmation: original_pipeline_txt:7 -> {reader}; reason: reviewed visual"
        )
    decision = {
        "markdown": lines[0], "selected_blocks": [{**source_ref, "purpose": "structure"}], "assets": [],
        "review": {"visual_reviewed": True, "notes": notes},
        "semantic_structure": {"schema": "kb_creator.page_semantic_structure.v1", "review": {"state": "complete", "visual": visual}, "units": [{
            "id": "title", "kind": "heading", "representation": "atx_heading", "source_blocks": [source_ref],
            "markdown_span": _span(lines, 1, 1), "container_parent": None, "semantic_parent": None,
            "continuation_of": None, "heading_level": 2, "item_count": None,
        }]},
    }
    packet = {"views": {"original_pipeline_txt": {"blocks": [{
        "raw_index": 7, "text": source, "assets": [], "semantic_evidence": {
            "v2_title": True, "markdown_heading": True, "middle_title": False,
        },
    }]}}}
    return {1: decision}, {1: packet}, {visual["path"]: {"bytes": 1, "sha256": "A" * 64}}


def test_title_evidence_confirmation_binds_changed_reader_heading_and_seals_report():
    decisions, packets, visuals = _title_conflict_fixture()
    report = validate_semantic_structure(decisions, packets, visuals, required_pages=[1])
    confirmations = report["pages"][0]["title_evidence_confirmations"]
    assert confirmations == [{
        "view": "original_pipeline_txt", "raw_index": 7,
        "source_sha256": hashlib.sha256(b"THE ENLIGHTENEDWEBSITE").hexdigest().upper(),
        "reader_sha256": hashlib.sha256(b"THE ENLIGHTENED WEBSITE").hexdigest().upper(), "changed": True,
    }]


@pytest.mark.parametrize(
    "notes,error",
    [
        ("", "title_evidence_confirmation_required"),
        ("title evidence confirmation: original_pipeline_txt:7 -> THE ENLIGHTENED WEBSITE; reason: reviewed visual", "title_text_correction_required"),
        ("text correction: THE ENLIGHTENEDWEBSITE -> THE ENLIGHTENED WEBSITE; reason: reviewed visual\ntitle evidence confirmation: original_pipeline_txt:7 -> OTHER; reason: reviewed visual", "title_reader_heading_mismatch"),
        ("text correction: THE ENLIGHTENEDWEBSITE -> THE ENLIGHTENED WEBSITE; reason: reviewed visual\ntitle evidence confirmation: original_pipeline_txt:8 -> THE ENLIGHTENED WEBSITE; reason: reviewed visual", "title_evidence_confirmation_stale"),
    ],
)
def test_title_evidence_confirmation_fails_closed(notes, error):
    decisions, packets, visuals = _title_conflict_fixture(notes=notes)
    with pytest.raises(SemanticStructureError, match=error):
        validate_semantic_structure(decisions, packets, visuals, required_pages=[1])


def test_unchanged_title_conflict_confirmation_and_blank_separator_contract():
    decisions, packets, visuals = _title_conflict_fixture(
        source="APPENDIX C - PREGENERATED PLAYER-CHARACTERS",
        reader="APPENDIX C - PREGENERATED PLAYER-CHARACTERS",
        notes="title evidence confirmation: original_pipeline_txt:7 -> APPENDIX C - PREGENERATED PLAYER-CHARACTERS; reason: visual wrap only",
    )
    report = validate_semantic_structure(decisions, packets, visuals, required_pages=[1])
    assert report["pages"][0]["title_evidence_confirmations"][0]["changed"] is False
    assert validate_canonical_blank_separators("alpha\n\n>\n\nbeta", 1) == 0
    with pytest.raises(SemanticStructureError, match="redundant_root_blank_separator"):
        validate_canonical_blank_separators("alpha\n\n\nbeta", 1)


def _v2_stats_fixture():
    source = "Name\nSTR 50"
    lines = ["## Name", "STR 50"]
    visual = {"path": "outputs/04-visual-merge-bundle/visual/original_pipeline_txt/pages/page-001.png", "bytes": 1, "sha256": "A" * 64}
    ref = {"view": "original_pipeline_txt", "raw_index": 0}
    def fragment(start, end):
        value = source[start:end]
        return {**ref, "source_sha256": hashlib.sha256(source.encode()).hexdigest().upper(), "normalized_sha256": hashlib.sha256("".join(c for c in value.casefold() if c.isalnum()).encode()).hexdigest().upper(), "start": start, "end": end, "fragment_sha256": hashlib.sha256(value.encode()).hexdigest().upper()}
    def unit(identity, kind, start, end, parent=None, fragments=None):
        return {"id": identity, "kind": kind, "representation": "atx_heading" if kind == "heading" else "semantic_span", "source_blocks": [ref], "source_fragments": fragments or [], "markdown_span": _span(lines, start, end), "container_parent": parent, "semantic_parent": None, "continuation_of": None, "heading_level": 2 if kind == "heading" else None, "item_count": None}
    title = unit("title", "heading", 1, 1, "stats", [fragment(0, 4)])
    stats = unit("stats", "statblock", 1, 2, None, [fragment(4, len(source))])
    decision = {"semantic_role": "character_statistics", "markdown": "\n".join(lines), "selected_blocks": [{**ref, "purpose": "structure"}], "assets": [], "semantic_structure": {"schema": "kb_creator.page_semantic_structure.v2", "profile": "reviewed_role_outline_and_partitions_v2", "role_contract": {"role": "character_statistics", "group_id": "appendix-a", "statblock_ids": ["stats"], "title_heading_ids": ["title"]}, "review": {"state": "complete", "visual": visual}, "units": [stats, title]}}
    packet = {"views": {"original_pipeline_txt": {"blocks": [{"raw_index": 0, "text": source, "assets": []}]}}}
    return {1: decision}, {1: packet}, {visual["path"]: {"bytes": 1, "sha256": "A" * 64}}


def test_v2_statblock_title_partition_is_exact_and_v1_remains_compatible():
    decisions, packets, visuals = _v2_stats_fixture()
    assert validate_semantic_structure(decisions, packets, visuals, required_pages=[1])["profile"] == "reviewed_role_outline_and_partitions_v2"
    decisions[1]["semantic_structure"]["units"][0]["source_fragments"][0]["end"] -= 1
    with pytest.raises(SemanticStructureError, match="stale|partition"):
        validate_semantic_structure(decisions, packets, visuals, required_pages=[1])
    legacy, legacy_packets, legacy_visuals = _fixture()
    assert validate_semantic_structure(legacy, legacy_packets, legacy_visuals, required_pages=[1])["profile"] == "visually_reviewed_semantic_containers_v1"


def _v2_line_group_fixture():
    source = "The wind returns\nThe bell answers\nThe wind returns"
    lines = ["The wind returns  ", "The bell answers  ", "The wind returns"]
    visual = {"path": "outputs/04-visual-merge-bundle/visual/original_pipeline_txt/pages/page-045.png", "bytes": 1, "sha256": "A" * 64}
    ref = {"view": "original_pipeline_txt", "raw_index": 45}

    def fragment(start, end):
        value = source[start:end]
        return {
            **ref,
            "source_sha256": hashlib.sha256(source.encode()).hexdigest().upper(),
            "normalized_sha256": hashlib.sha256(
                "".join(char for char in value.casefold() if char.isalnum()).encode()
            ).hexdigest().upper(),
            "start": start,
            "end": end,
            "fragment_sha256": hashlib.sha256(value.encode()).hexdigest().upper(),
        }

    first = len("The wind returns\n")
    second = first + len("The bell answers\n")
    unit = {
        "id": "refrain", "kind": "line_group", "representation": "hard_break_lines",
        "source_blocks": [ref], "source_fragments": [fragment(0, first), fragment(first, second), fragment(second, len(source))],
        "markdown_span": _span(lines, 1, 3), "container_parent": None, "semantic_parent": None,
        "continuation_of": None, "heading_level": None, "item_count": None,
    }
    decision = {
        "semantic_role": "body", "markdown": "\n".join(lines),
        "selected_blocks": [{**ref, "purpose": "text"}], "assets": [],
        "semantic_structure": {
            "schema": "kb_creator.page_semantic_structure.v2",
            "profile": "reviewed_role_outline_and_partitions_v2",
            "role_contract": {"role": "body", "group_id": "handout-h"},
            "review": {"state": "complete", "visual": visual}, "units": [unit],
        },
    }
    packet = {"views": {"original_pipeline_txt": {"blocks": [{"raw_index": 45, "text": source, "assets": []}]}}}
    return {45: decision}, {45: packet}, {visual["path"]: {"bytes": 1, "sha256": "A" * 64}}


def test_v2_line_group_uses_full_fragmented_refrain_including_repeated_lines():
    decisions, packets, visuals = _v2_line_group_fixture()
    report = validate_semantic_structure(decisions, packets, visuals, required_pages=[45])
    assert report["pages"][0]["validated_unit_count"] == 1


@pytest.mark.parametrize(
    "mutation,error",
    [
        ("count", "line-group source/reader line count mismatch"),
        ("order", "line-group source order or line mapping mismatch"),
        ("boundary", "line-group source fragment cuts a physical line"),
    ],
)
def test_v2_line_group_rejects_count_order_and_fragment_boundary_mutations(mutation, error):
    decisions, packets, visuals = _v2_line_group_fixture()
    decision = decisions[45]
    unit = decision["semantic_structure"]["units"][0]
    if mutation == "count":
        lines = decision["markdown"].splitlines()[:2]
        decision["markdown"] = "\n".join(lines)
        unit["markdown_span"] = _span(lines, 1, 2)
    elif mutation == "order":
        lines = ["The bell answers  ", "The wind returns  ", "The wind returns"]
        decision["markdown"] = "\n".join(lines)
        unit["markdown_span"] = _span(lines, 1, 3)
    else:
        fragment = unit["source_fragments"][1]
        source = packets[45]["views"]["original_pipeline_txt"]["blocks"][0]["text"]
        fragment["start"] += 1
        value = source[fragment["start"]:fragment["end"]]
        fragment["fragment_sha256"] = hashlib.sha256(value.encode()).hexdigest().upper()
        fragment["normalized_sha256"] = hashlib.sha256(
            "".join(char for char in value.casefold() if char.isalnum()).encode()
        ).hexdigest().upper()
    with pytest.raises(SemanticStructureError, match=error):
        validate_semantic_structure(decisions, packets, visuals, required_pages=[45])


def _v2_refrain_correction_fixture():
    decisions, packets, visuals = _v2_line_group_fixture()
    source = "The refrain returns\nThe bell answers\nThe refrain returns\nThe final bell"
    lines = [
        "The refrain returns  ", "The refrain returns  ",
        "The refrain returns  ", "The final bell",
    ]
    key = ("original_pipeline_txt", 45)
    unit = decisions[45]["semantic_structure"]["units"][0]
    unit["markdown_span"] = _span(lines, 1, 4)
    fragments = []
    start = 0
    for physical_line in source.splitlines(keepends=True):
        end = start + len(physical_line)
        value = source[start:end]
        fragments.append({
            "view": key[0], "raw_index": key[1],
            "source_sha256": hashlib.sha256(source.encode()).hexdigest().upper(),
            "normalized_sha256": hashlib.sha256(
                "".join(char for char in value.casefold() if char.isalnum()).encode()
            ).hexdigest().upper(),
            "start": start, "end": end,
            "fragment_sha256": hashlib.sha256(value.encode()).hexdigest().upper(),
        })
        start = end
    unit["source_fragments"] = fragments
    decisions[45]["markdown"] = "\n".join(lines)
    decisions[45]["reviewed_block_corrections"] = [{
        "view": key[0], "raw_index": key[1],
        "before": "The bell answers", "after": "The refrain returns",
        "reason": "reviewed verse source",
        "original_text_sha256": hashlib.sha256(source.encode()).hexdigest().upper(),
    }]
    packets[45]["views"][key[0]]["blocks"][0]["text"] = source
    return decisions, packets, visuals


def test_v2_line_group_correction_binds_repeated_refrain_to_exact_physical_line():
    decisions, packets, visuals = _v2_refrain_correction_fixture()
    assert validate_semantic_structure(
        decisions, packets, visuals, required_pages=[45],
    )["pages"][0]["validated_unit_count"] == 1


def test_v2_line_group_correction_rejects_repeated_refrain_at_wrong_occurrence():
    decisions, packets, visuals = _v2_refrain_correction_fixture()
    lines = [
        "The refrain returns  ", "The bell answers  ",
        "The refrain returns  ", "The final bell",
    ]
    decisions[45]["markdown"] = "\n".join(lines)
    decisions[45]["semantic_structure"]["units"][0]["markdown_span"] = _span(lines, 1, 4)
    with pytest.raises(SemanticStructureError, match="bound visible line"):
        validate_semantic_structure(decisions, packets, visuals, required_pages=[45])


def test_v2_line_group_correction_rejects_hidden_link_and_invalid_fragment():
    decisions, packets, visuals = _v2_refrain_correction_fixture()
    lines = [
        "The refrain returns  ", "[public](The refrain returns)  ",
        "The refrain returns  ", "The final bell",
    ]
    decisions[45]["markdown"] = "\n".join(lines)
    decisions[45]["semantic_structure"]["units"][0]["markdown_span"] = _span(lines, 1, 4)
    with pytest.raises(SemanticStructureError, match="bound visible line"):
        validate_semantic_structure(decisions, packets, visuals, required_pages=[45])

    decisions, packets, visuals = _v2_refrain_correction_fixture()
    fragment = decisions[45]["semantic_structure"]["units"][0]["source_fragments"][1]
    fragment["start"] += 1
    value = packets[45]["views"]["original_pipeline_txt"]["blocks"][0]["text"][fragment["start"]:fragment["end"]]
    fragment["fragment_sha256"] = hashlib.sha256(value.encode()).hexdigest().upper()
    fragment["normalized_sha256"] = hashlib.sha256(
        "".join(char for char in value.casefold() if char.isalnum()).encode()
    ).hexdigest().upper()
    with pytest.raises(SemanticStructureError, match="fragment cuts a physical line"):
        validate_semantic_structure(decisions, packets, visuals, required_pages=[45])


def test_v2_line_group_correction_keeps_full_group_order_validation():
    decisions, packets, visuals = _v2_refrain_correction_fixture()
    lines = [
        "The refrain returns  ", "The refrain returns  ",
        "The final bell  ", "The refrain returns",
    ]
    decisions[45]["markdown"] = "\n".join(lines)
    decisions[45]["semantic_structure"]["units"][0]["markdown_span"] = _span(lines, 1, 4)
    with pytest.raises(SemanticStructureError, match="line-group source order or line mapping mismatch"):
        validate_semantic_structure(decisions, packets, visuals, required_pages=[45])


def test_v2_selected_asset_anchor_allows_distinct_image_assertion_units_with_one_inline_placeholder():
    lines = ["## Printed label one", "## Printed label two", "", "![Handout]({{asset:handout.png}})"]
    visual = {"path": "outputs/04-visual-merge-bundle/visual/original_pipeline_txt/pages/page-001.png", "bytes": 1, "sha256": "A" * 64}
    asset_ref = {"view": "original_pipeline_txt", "raw_index": 7}
    asset_block = {"source_page": 1, "view_id": "original_pipeline_txt", "raw_index": 7, "block_type": "image", "bbox": [100, 100, 900, 900], "source_path": "images/handout.png"}
    def unit(identity, line, assertion_id):
        return {"id": identity, "kind": "heading", "representation": "atx_heading", "source_blocks": [asset_ref], "source_fragments": [], "markdown_span": _span(lines, line, line), "container_parent": None, "semantic_parent": None, "continuation_of": None, "heading_level": 2, "item_count": None, "visual_assertion_ids": [assertion_id]}
    decision = {"semantic_role": "body", "markdown": "\n".join(lines), "selected_blocks": [{**asset_ref, "purpose": "asset"}], "assets": [{"view": "original_pipeline_txt", "source_path": "images/handout.png", "logical_name": "handout.png", "placement": "inline"}], "semantic_structure": {"schema": "kb_creator.page_semantic_structure.v2", "profile": "reviewed_role_outline_and_partitions_v2", "role_contract": {"role": "body", "group_id": "handout"}, "review": {"state": "complete", "visual": visual}, "units": [unit("label-one", 1, "a-one"), unit("label-two", 2, "a-two")]}}
    def assertion(text, start):
        return {"source_page": 1, "text": text, "placement": {"relation": "within_selected_asset_region", "asset_block": asset_block, "logical_name": "handout.png", "markdown_span": {"start": start, "end": start + len("".join(char for char in text.casefold() if char.isalnum()))}}}
    assertions = {"a-one": assertion("Printed label one", 0), "a-two": assertion("Printed label two", len("printedlabelone"))}
    packet = {"views": {"original_pipeline_txt": {"blocks": [{"raw_index": 7, "type": "image", "text": "", "assets": ["images/handout.png"]}]}}}
    report = validate_semantic_structure({1: decision}, {1: packet}, {visual["path"]: {"bytes": 1, "sha256": "A" * 64}}, required_pages=[1], visual_assertions=assertions)
    assert report["pages"][0]["validated_unit_count"] == 2
    assertions["a-two"]["placement"]["asset_block"]["raw_index"] = 8
    with pytest.raises(SemanticStructureError, match="inline semantic asset"):
        validate_semantic_structure({1: decision}, {1: packet}, {visual["path"]: {"bytes": 1, "sha256": "A" * 64}}, required_pages=[1], visual_assertions=assertions)


def _v2_populated_asset_text_fixture():
    lines = ["| Visible ledger |", "| --- |", "| 42 |", "![Ledger]({{asset:ledger.png}})"]
    markdown = "\n".join(lines)
    visual = {"path": "outputs/04-visual-merge-bundle/visual/original_pipeline_txt/pages/page-042.png", "bytes": 1, "sha256": "A" * 64}
    asset_ref = {"view": "original_pipeline_txt", "raw_index": 718}
    asset_block = {"source_page": 42, "view_id": "original_pipeline_txt", "raw_index": 718, "block_type": "table", "bbox": [100, 100, 900, 700], "source_path": "images/ledger.png"}
    unit = {"id": "ledger", "kind": "statblock", "representation": "table", "source_blocks": [asset_ref], "source_fragments": [], "markdown_span": _span(lines, 1, 4), "container_parent": None, "semantic_parent": None, "continuation_of": None, "heading_level": None, "item_count": None, "visual_assertion_ids": ["ledger-visible-text"]}
    decision = {"semantic_role": "body", "markdown": markdown, "selected_blocks": [{**asset_ref, "purpose": "asset"}], "assets": [{"view": "original_pipeline_txt", "source_path": "images/ledger.png", "logical_name": "ledger.png", "placement": "inline"}], "semantic_structure": {"schema": "kb_creator.page_semantic_structure.v2", "profile": "reviewed_role_outline_and_partitions_v2", "role_contract": {"role": "body", "group_id": "ledger"}, "review": {"state": "complete", "visual": visual}, "units": [unit]}}
    assertion = {"source_page": 42, "text": "Visible ledger 42", "placement": {"relation": "within_selected_asset_region", "asset_block": asset_block, "logical_name": "ledger.png", "markdown_span": {"start": 0, "end": len("visibleledger42")}}}
    packet = {"views": {"original_pipeline_txt": {"blocks": [{"raw_index": 718, "type": "table", "text": "Vlsible ldg er", "assets": ["images/ledger.png"]}]}}}
    return {42: decision}, {42: packet}, {visual["path"]: {"bytes": 1, "sha256": "A" * 64}}, {"ledger-visible-text": assertion}


def test_v2_populated_asset_ocr_can_be_replaced_by_full_image_assertion():
    decisions, packets, visuals, assertions = _v2_populated_asset_text_fixture()
    report = validate_semantic_structure(decisions, packets, visuals, required_pages=[42], visual_assertions=assertions)
    assert report["pages"][0]["validated_unit_count"] == 1


@pytest.mark.parametrize("mutation", ["missing", "mismatched"])
def test_v2_populated_asset_ocr_requires_matching_image_assertion(mutation):
    decisions, packets, visuals, assertions = _v2_populated_asset_text_fixture()
    if mutation == "missing":
        assertions = {}
    else:
        assertions["ledger-visible-text"]["placement"]["asset_block"]["raw_index"] = 719
    with pytest.raises(SemanticStructureError):
        validate_semantic_structure(decisions, packets, visuals, required_pages=[42], visual_assertions=assertions)


def test_reference_image_proof_key_requires_exact_asset_identity():
    decision = {"source_page": 45, "review": {"visual_reviewed": True}, "selected_blocks": [{"view": "original_pipeline_txt", "raw_index": 811, "purpose": "asset"}], "assets": [{"view": "original_pipeline_txt", "source_path": "images/p045-raw811.png", "logical_name": "p045-raw811", "placement": "reference_only"}], "markdown": "| skill | value |", "semantic_structure": {"profile": "reviewed_role_outline_and_partitions_v2", "units": [{"id": "parent", "kind": "statblock", "representation": "table", "markdown_span": {"start_line": 1, "end_line": 1}, "source_blocks": [{"view": "original_pipeline_txt", "raw_index": 800}]}, {"id": "child", "kind": "statblock", "representation": "semantic_span", "source_fragments": [], "visual_assertion_ids": ["proof"], "container_parent": "parent", "markdown_span": {"start_line": 1, "end_line": 1}, "source_blocks": [{"view": "original_pipeline_txt", "raw_index": 811}]}]}}
    packet = {"views": {"original_pipeline_txt": {"blocks": [{"raw_index": 811, "assets": ["images/p045-raw811.png"]}]}}}
    assertion = {"source_page": 45, "text": "skill", "placement": {"relation": "within_selected_asset_region", "logical_name": "p045-raw811", "asset_block": {"source_page": 45, "view_id": "original_pipeline_txt", "raw_index": 811, "source_path": "images/p045-raw811.png"}}}
    assert collect_reference_image_proof_keys({45: decision}, {45: packet}, {"proof": assertion}) == {(45, "original_pipeline_txt", 811, "p045-raw811", "child")}
    assertion["placement"]["asset_block"]["source_path"] = "images/other.png"
    assert not collect_reference_image_proof_keys({45: decision}, {45: packet}, {"proof": assertion})


def test_v2_statblock_is_plain_markdown_and_rejects_quote_transport():
    decisions, packets, visuals = _v2_stats_fixture()
    report = validate_semantic_structure(decisions, packets, visuals, required_pages=[1])
    assert report["pages"][0]["units"][0]["representation"] == "semantic_span"
    assert not any(line.startswith(">") for line in decisions[1]["markdown"].splitlines())

    decisions[1]["semantic_structure"]["units"][0]["representation"] = "blockquote"
    with pytest.raises(SemanticStructureError, match="invalid kind/representation"):
        validate_semantic_structure(decisions, packets, visuals, required_pages=[1])


@pytest.mark.parametrize("reader", ["Long Island", "**Long Island**"])
def test_v2_label_semantic_span_accepts_one_plain_or_bold_bound_line(reader):
    source = "Long Island"
    lines = [reader]
    visual = {"path": "outputs/04-visual-merge-bundle/visual/original_pipeline_txt/pages/page-001.png", "bytes": 1, "sha256": "A" * 64}
    ref = {"view": "original_pipeline_txt", "raw_index": 0}
    fragment = {**ref, "source_sha256": hashlib.sha256(source.encode()).hexdigest().upper(), "normalized_sha256": hashlib.sha256("longisland".encode()).hexdigest().upper(), "start": 0, "end": len(source), "fragment_sha256": hashlib.sha256(source.encode()).hexdigest().upper()}
    unit = {"id": "location-label", "kind": "label", "representation": "semantic_span", "source_blocks": [ref], "source_fragments": [fragment], "markdown_span": _span(lines, 1, 1), "container_parent": None, "semantic_parent": None, "continuation_of": None, "heading_level": None, "item_count": None}
    decision = {"semantic_role": "body", "markdown": reader, "selected_blocks": [{**ref, "purpose": "text"}], "assets": [], "semantic_structure": {"schema": "kb_creator.page_semantic_structure.v2", "profile": "reviewed_role_outline_and_partitions_v2", "role_contract": {"role": "body", "group_id": "locations"}, "review": {"state": "complete", "visual": visual}, "units": [unit]}}
    packet = {"views": {"original_pipeline_txt": {"blocks": [{"raw_index": 0, "text": source, "assets": []}]}}}
    assert validate_semantic_structure({1: decision}, {1: packet}, {visual["path"]: {"bytes": 1, "sha256": "A" * 64}}, required_pages=[1])["pages"][0]["validated_unit_count"] == 1


@pytest.mark.parametrize("reader", ["Long Island\nnext", "# Long Island", "- Long Island", "> Long Island"])
def test_v2_label_semantic_span_rejects_multiline_or_markdown_prefix(reader):
    decisions, packets, visuals = _v2_stats_fixture()
    decision = decisions[1]
    decision["markdown"] = reader
    unit = decision["semantic_structure"]["units"][1]
    unit["kind"] = "label"
    unit["representation"] = "semantic_span"
    unit["source_fragments"] = []
    unit["markdown_span"] = _span(reader.split("\n"), 1, len(reader.split("\n")))
    unit["source_blocks"] = [{"view": "original_pipeline_txt", "raw_index": 0}]
    with pytest.raises(SemanticStructureError):
        validate_semantic_structure(decisions, packets, visuals, required_pages=[1])

    decisions, packets, visuals = _v2_stats_fixture()
    decisions[1]["markdown"] = "> ## Name\nSTR 50"
    decisions[1]["semantic_structure"]["units"][0]["markdown_span"] = _span(
        decisions[1]["markdown"].split("\n"), 1, 2
    )
    decisions[1]["semantic_structure"]["units"][1]["markdown_span"] = _span(
        decisions[1]["markdown"].split("\n"), 1, 1
    )
    with pytest.raises(SemanticStructureError, match="quote syntax"):
        validate_semantic_structure(decisions, packets, visuals, required_pages=[1])


def _v2_paragraph_fixture():
    first = "Either the police at the dock when the injured diver is periodically at the beach"
    corrected_first = "Either the police at the dock when the injured diver is"
    second = " brought ashore, the Coast Guard can identify Solomon."
    reader = corrected_first + second
    lines = [reader]
    visual = {"path": "outputs/04-visual-merge-bundle/visual/original_pipeline_txt/pages/page-077.png", "bytes": 1, "sha256": "A" * 64}

    def fragment(raw_index, source):
        return {
            "view": "original_pipeline_txt", "raw_index": raw_index,
            "source_sha256": hashlib.sha256(source.encode()).hexdigest().upper(),
            "normalized_sha256": hashlib.sha256("".join(char for char in source.casefold() if char.isalnum()).encode()).hexdigest().upper(),
            "start": 0, "end": len(source), "fragment_sha256": hashlib.sha256(source.encode()).hexdigest().upper(),
        }

    refs = [{"view": "original_pipeline_txt", "raw_index": raw} for raw in (1519, 1512)]
    unit = {
        "id": "police-continuation", "kind": "paragraph", "representation": "semantic_span",
        "source_blocks": refs, "source_fragments": [fragment(1519, first), fragment(1512, second)],
        "markdown_span": _span(lines, 1, 1), "container_parent": None, "semantic_parent": None,
        "continuation_of": None, "heading_level": None, "item_count": None,
    }
    decision = {
        "semantic_role": "body", "markdown": reader,
        "selected_blocks": [{**ref, "purpose": "text"} for ref in refs], "assets": [],
        "reviewed_block_corrections": [{
            "view": "original_pipeline_txt", "raw_index": 1519,
            "before": "is periodically at the beach", "after": "is", "reason": "reviewed page split",
            "original_text_sha256": hashlib.sha256(first.encode()).hexdigest().upper(),
        }],
        "semantic_structure": {
            "schema": "kb_creator.page_semantic_structure.v2", "profile": "reviewed_role_outline_and_partitions_v2",
            "role_contract": {"role": "body", "group_id": "page-077"},
            "review": {"state": "complete", "visual": visual}, "units": [unit],
        },
    }
    packet = {"views": {"original_pipeline_txt": {"blocks": [
        {"raw_index": 1519, "text": first, "assets": []},
        {"raw_index": 1512, "text": second, "assets": []},
    ]}}}
    return {77: decision}, {77: packet}, {visual["path"]: {"bytes": 1, "sha256": "A" * 64}}


def test_v2_paragraph_semantic_span_joins_corrected_source_fragments():
    decisions, packets, visuals = _v2_paragraph_fixture()
    assert validate_semantic_structure(decisions, packets, visuals, required_pages=[77])["pages"][0]["validated_unit_count"] == 1


@pytest.mark.parametrize("reader", [
    "first line\nsecond line", "# Heading", "- item", "1. item", "> quote", "| cell |", "```code", "<div>text</div>",
])
def test_v2_paragraph_semantic_span_rejects_structured_or_multiline_markdown(reader):
    lines = reader.split("\n")
    assert _syntax_errors(
        {"kind": "paragraph", "representation": "semantic_span"}, lines, 1, len(lines),
    ) == (["semantic paragraph span must contain exactly one nonblank line"] if len(lines) > 1
          else ["semantic paragraph span must be plain Markdown prose"])


@pytest.mark.parametrize("mutation", ["gap", "overlap", "reorder"])
def test_v2_paragraph_semantic_span_rejects_fragment_loss_overlap_or_reorder(mutation):
    decisions, packets, visuals = _v2_paragraph_fixture()
    unit = decisions[77]["semantic_structure"]["units"][0]
    if mutation == "reorder":
        unit["source_fragments"].reverse()
    else:
        fragment = unit["source_fragments"][0]
        source = packets[77]["views"]["original_pipeline_txt"]["blocks"][0]["text"]
        fragment["end"] -= 1 if mutation == "gap" else -1
        value = source[fragment["start"]:fragment["end"]]
        fragment["fragment_sha256"] = hashlib.sha256(value.encode()).hexdigest().upper()
        fragment["normalized_sha256"] = hashlib.sha256("".join(char for char in value.casefold() if char.isalnum()).encode()).hexdigest().upper()
    with pytest.raises(SemanticStructureError):
        validate_semantic_structure(decisions, packets, visuals, required_pages=[77])


def test_v2_paragraph_semantic_span_rejects_reader_without_corrected_fragments():
    decisions, packets, visuals = _v2_paragraph_fixture()
    first = packets[77]["views"]["original_pipeline_txt"]["blocks"][0]["text"]
    second = packets[77]["views"]["original_pipeline_txt"]["blocks"][1]["text"]
    reader = first + second
    decisions[77]["markdown"] = reader
    decisions[77]["semantic_structure"]["units"][0]["markdown_span"] = _span([reader], 1, 1)
    with pytest.raises(SemanticStructureError, match="source_fragment_reader_loss"):
        validate_semantic_structure(decisions, packets, visuals, required_pages=[77])


def test_v2_fragment_reader_comparison_consumes_reviewed_ocr_correction():
    decisions, packets, visuals = _v2_stats_fixture()
    source = "Narne\nSTR 50"
    packets[1]["views"]["original_pipeline_txt"]["blocks"][0]["text"] = source
    decisions[1]["review"] = {
        "state": "complete",
        "visual": decisions[1]["semantic_structure"]["review"]["visual"],
        "notes": "text correction: Narne -> Name; reason: visual review confirms Name",
    }

    def rebind(fragment: dict, start: int, end: int) -> None:
        value = source[start:end]
        fragment.update({
            "source_sha256": hashlib.sha256(source.encode()).hexdigest().upper(),
            "normalized_sha256": hashlib.sha256(
                "".join(char for char in value.casefold() if char.isalnum()).encode()
            ).hexdigest().upper(),
            "start": start,
            "end": end,
            "fragment_sha256": hashlib.sha256(value.encode()).hexdigest().upper(),
        })

    stats, title = decisions[1]["semantic_structure"]["units"]
    rebind(title["source_fragments"][0], 0, 5)
    rebind(stats["source_fragments"][0], 5, len(source))
    assert validate_semantic_structure(
        decisions, packets, visuals, required_pages=[1]
    )["profile"] == "reviewed_role_outline_and_partitions_v2"


def test_v2_statblock_requires_one_first_title_and_complete_partition():
    decisions, packets, visuals = _v2_stats_fixture()
    decisions[1]["semantic_structure"]["role_contract"]["title_heading_ids"] = []
    with pytest.raises(SemanticStructureError, match="contract_invalid"):
        validate_semantic_structure(decisions, packets, visuals, required_pages=[1])
    decisions, packets, visuals = _v2_stats_fixture()
    decisions[1]["semantic_structure"]["units"][1]["markdown_span"] = _span(decisions[1]["markdown"].split("\n"), 2, 2)
    with pytest.raises(SemanticStructureError, match="ATX heading level mismatch"):
        validate_semantic_structure(decisions, packets, visuals, required_pages=[1])


def _v2_pregenerated_fixture(second_page=2):
    decisions, packets, visuals = {}, {}, {}
    for page, values, root in [(1, ["Appendix", "Hero One", "Background", "What You Know"], "root"), (second_page, ["Hero Two", "Background", "What You Know"], None)]:
        lines = ["# Appendix", "## Hero One", "### Background", "### What You Know"] if root else ["## Hero Two", "### Background", "### What You Know"]
        refs = [{"view": "original_pipeline_txt", "raw_index": index} for index in range(len(values))]
        visual = {"path": f"outputs/04-visual-merge-bundle/visual/original_pipeline_txt/pages/page-{page:03d}.png", "bytes": 1, "sha256": "A" * 64}
        def item(index, level, parent=None):
            text = values[index]; ref = refs[index]
            fragment = {**ref, "source_sha256": hashlib.sha256(text.encode()).hexdigest().upper(), "normalized_sha256": hashlib.sha256("".join(c for c in text.casefold() if c.isalnum()).encode()).hexdigest().upper(), "start": 0, "end": len(text), "fragment_sha256": hashlib.sha256(text.encode()).hexdigest().upper()}
            return {"id": ("root" if root and index == 0 else f"record-{page}" if index == (1 if root else 0) else f"leaf-{page}-{index}"), "kind": "heading", "representation": "atx_heading", "source_blocks": [ref], "source_fragments": [fragment], "markdown_span": _span(lines, index + 1, index + 1), "container_parent": None, "semantic_parent": parent, "continuation_of": None, "heading_level": level, "item_count": None}
        units = []
        if root:
            units.append(item(0, 1)); units.append(item(1, 2, "root")); units.extend([item(2, 3, f"record-{page}"), item(3, 3, f"record-{page}")])
        else:
            units.append(item(0, 2)); units.extend([item(1, 3, f"record-{page}"), item(2, 3, f"record-{page}")])
        contract = {"role": "pregenerated_characters", "group_id": "appendix-c", "root_heading_id": root, "record_heading_id": f"record-{page}", "leaf_heading_ids": [unit["id"] for unit in units if unit["heading_level"] == 3]}
        decisions[page] = {"semantic_role": "pregenerated_characters", "markdown": "\n".join(lines), "selected_blocks": [{**ref, "purpose": "structure"} for ref in refs], "assets": [], "semantic_structure": {"schema": "kb_creator.page_semantic_structure.v2", "profile": "reviewed_role_outline_and_partitions_v2", "role_contract": contract, "review": {"state": "complete", "visual": visual}, "units": units}}
        packets[page] = {"views": {"original_pipeline_txt": {"blocks": [{"raw_index": index, "text": text, "assets": []} for index, text in enumerate(values)]}}}
        visuals[visual["path"]] = {"bytes": 1, "sha256": "A" * 64}
    return decisions, packets, visuals


def test_v2_pregenerated_outline_requires_parent_order_and_contiguous_pages():
    decisions, packets, visuals = _v2_pregenerated_fixture()
    assert validate_semantic_structure(decisions, packets, visuals, required_pages=[1, 2])["profile"] == "reviewed_role_outline_and_partitions_v2"
    decisions[2]["semantic_structure"]["units"][1]["semantic_parent"] = None
    with pytest.raises(SemanticStructureError, match="pregenerated_parent_invalid"):
        validate_semantic_structure(decisions, packets, visuals, required_pages=[1, 2])
    decisions, packets, visuals = _v2_pregenerated_fixture(second_page=3)
    with pytest.raises(SemanticStructureError, match="noncontiguous"):
        validate_semantic_structure(decisions, packets, visuals, required_pages=[1, 3])


def test_v2_plural_pregenerated_records_allow_empty_leaves_and_require_ordered_coverage():
    decisions, packets, visuals = _v2_pregenerated_fixture()
    page = decisions[1]
    lines = ["# Appendix", "## Hero One", "## Hero Two"]
    page["markdown"] = "\n".join(lines)
    units = page["semantic_structure"]["units"]
    root, first = units[:2]
    root["markdown_span"] = _span(lines, 1, 1)
    first["markdown_span"] = _span(lines, 2, 2)
    second_ref = {"view": "original_pipeline_txt", "raw_index": 2}
    source = "Hero Two"
    packets[1]["views"]["original_pipeline_txt"]["blocks"][2]["text"] = source
    fragment = {**second_ref, "source_sha256": hashlib.sha256(source.encode()).hexdigest().upper(), "normalized_sha256": hashlib.sha256("herotwo".encode()).hexdigest().upper(), "start": 0, "end": len(source), "fragment_sha256": hashlib.sha256(source.encode()).hexdigest().upper()}
    second = {**first, "id": "record-1b", "source_blocks": [second_ref], "source_fragments": [fragment], "markdown_span": _span(lines, 3, 3), "semantic_parent": "root"}
    page["selected_blocks"] = [row for row in page["selected_blocks"] if row["raw_index"] in {0, 1, 2}]
    page["semantic_structure"]["units"] = [root, first, second]
    page["semantic_structure"]["role_contract"] = {"role": "pregenerated_characters", "group_id": "appendix-c", "root_heading_id": "root", "record_heading_ids": ["record-1", "record-1b"], "leaf_heading_ids": []}
    assert validate_semantic_structure(decisions, packets, visuals, required_pages=[1])["profile"] == "reviewed_role_outline_and_partitions_v2"
    page["semantic_structure"]["role_contract"]["record_heading_ids"].reverse()
    with pytest.raises(SemanticStructureError, match="record_coverage_or_order"):
        validate_semantic_structure(decisions, packets, visuals, required_pages=[1])


def test_v2_plural_pregenerated_requires_global_root_and_schema_profile_parity():
    decisions, packets, visuals = _v2_pregenerated_fixture()
    decisions[2]["semantic_structure"]["role_contract"].pop("record_heading_id")
    decisions[2]["semantic_structure"]["role_contract"]["record_heading_ids"] = ["record-2"]
    decisions[2]["semantic_structure"]["units"][0]["semantic_parent"] = "root"
    assert validate_semantic_structure(decisions, packets, visuals, required_pages=[1, 2])["profile"] == "reviewed_role_outline_and_partitions_v2"
    decisions[2]["semantic_structure"]["units"][0]["semantic_parent"] = None
    with pytest.raises(SemanticStructureError, match="global_parent_invalid"):
        validate_semantic_structure(decisions, packets, visuals, required_pages=[1, 2])
    schema_path = Path(__file__).parents[1] / "contracts" / "reconstruction_decision_set.v2.schema.json"
    profiles = set(json.loads(schema_path.read_text(encoding="utf-8"))["properties"]["semantic_structure_profile"]["enum"])
    assert profiles == {"visually_reviewed_semantic_containers_v1", "reviewed_role_outline_and_partitions_v2"}


def test_v2_plural_pregenerated_uses_effective_markdown_and_first_reader_heading():
    decisions, packets, visuals = _v2_pregenerated_fixture()
    page = decisions[2]
    contract = page["semantic_structure"]["role_contract"]
    contract.pop("record_heading_id")
    contract["record_heading_ids"] = ["record-2"]
    page["semantic_structure"]["units"][0]["semantic_parent"] = "root"
    raw_lines = ["{{asset:portrait}}", "## Hero Two", "", "### Background", "### What You Know"]
    effective_lines = ["{{asset:portrait}}", "## Hero Two", "### Background", "### What You Know"]
    page["markdown"] = "\n".join(raw_lines)
    page["block_boundaries"] = [{"style": "compact", "heading_line": "## Hero Two", "first_body_line": "### Background"}]
    for index, unit in enumerate(page["semantic_structure"]["units"]):
        unit["markdown_span"] = _span(effective_lines, index + 2, index + 2)
    assert validate_semantic_structure(decisions, packets, visuals, required_pages=[1, 2])["profile"] == "reviewed_role_outline_and_partitions_v2"


def test_v2_plural_pregenerated_rejects_coverage_and_leaf_mutations_before_replay():
    decisions, packets, visuals = _v2_pregenerated_fixture()
    page = decisions[2]
    contract = page["semantic_structure"]["role_contract"]
    contract.pop("record_heading_id")
    contract["record_heading_ids"] = ["record-2"]
    page["semantic_structure"]["units"][0]["semantic_parent"] = "root"
    contract["leaf_heading_ids"] = []
    with pytest.raises(SemanticStructureError, match="leaf_coverage_or_order"):
        validate_semantic_structure(decisions, packets, visuals, required_pages=[1, 2])
    contract["leaf_heading_ids"] = ["leaf-2-1", "leaf-2-2"]
    page["semantic_structure"]["units"][1]["semantic_parent"] = None
    with pytest.raises(SemanticStructureError, match="pregenerated_parent_invalid"):
        validate_semantic_structure(decisions, packets, visuals, required_pages=[1, 2])
    page["semantic_structure"]["units"][1]["semantic_parent"] = "record-2"
    contract["record_heading_ids"] = ["record-2", "record-2"]
    with pytest.raises(SemanticStructureError, match="pregenerated_outline_invalid"):
        validate_semantic_structure(decisions, packets, visuals, required_pages=[1, 2])


def test_v2_legacy_pregenerated_later_record_keeps_null_parent_contract():
    decisions, packets, visuals = _v2_pregenerated_fixture()
    assert decisions[2]["semantic_structure"]["units"][0]["semantic_parent"] is None
    assert validate_semantic_structure(decisions, packets, visuals, required_pages=[1, 2])["profile"] == "reviewed_role_outline_and_partitions_v2"


def test_v2_plural_pregenerated_rejects_missing_and_extra_record_coverage():
    units = [
        {"id": "root", "kind": "heading", "representation": "atx_heading", "heading_level": 1, "markdown_span": {"start_line": 1}, "semantic_parent": None},
        {"id": "record-a", "kind": "heading", "representation": "atx_heading", "heading_level": 2, "markdown_span": {"start_line": 2}, "semantic_parent": "root"},
        {"id": "record-b", "kind": "heading", "representation": "atx_heading", "heading_level": 2, "markdown_span": {"start_line": 3}, "semantic_parent": "root"},
    ]
    base = {"semantic_role": "pregenerated_characters", "markdown": "# Root\n## A\n## B", "semantic_structure": {"role_contract": {"role": "pregenerated_characters", "group_id": "g", "root_heading_id": "root", "record_heading_ids": ["record-a"], "leaf_heading_ids": []}}}
    with pytest.raises(SemanticStructureError, match="record_coverage_or_order"):
        _validate_v2_role_contract(1, base, units)
    base["semantic_structure"]["role_contract"]["record_heading_ids"] = ["record-a", "record-b", "root"]
    with pytest.raises(SemanticStructureError, match="pregenerated_outline_invalid"):
        _validate_v2_role_contract(1, base, units)
