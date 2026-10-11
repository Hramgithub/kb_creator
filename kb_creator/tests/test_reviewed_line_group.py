from __future__ import annotations

import pytest

from kb_creator.pipeline.reviewed_line_group import canonicalize_reviewed_line_group
from kb_creator.scripts.author_reviewed_semantic_decisions import _canonicalize_line_groups


REFRAIN = [
    "The lord and master, who rules the cold,",
    "Keeps watch where the moon is pale,",
    "Calls the lost from the silent road,",
    "And follows the winter gale,",
    "Until the stars have all grown old,",
    "The lord and master, who rules the cold,",
    "Waits beyond the frozen gate,",
    "With a crown of silver and snow,",
    "For the hour that seals our fate,",
    "When the sleeping rivers flow.",
]


def test_refrain_sequence_is_canonicalized_as_one_complete_group():
    markdown = "\n\n".join(REFRAIN)
    rendered = canonicalize_reviewed_line_group(markdown, REFRAIN)
    assert rendered == "  \n".join(REFRAIN)
    assert canonicalize_reviewed_line_group(rendered, REFRAIN) == rendered


def test_old_reorder_case_is_canonicalized_to_expected_source_order():
    markdown = "Luck: 85\n\nSTR: 60 CON: 35\n\nHP: 8"
    assert canonicalize_reviewed_line_group(
        markdown, ["STR: 60 CON: 35", "Luck: 85", "HP: 8"],
    ) == "STR: 60 CON: 35  \nLuck: 85  \nHP: 8"


def test_repeated_whole_sequence_is_ambiguous():
    markdown = "\n".join(REFRAIN + [""] + REFRAIN)
    with pytest.raises(ValueError, match="absent or ambiguous"):
        canonicalize_reviewed_line_group(markdown, REFRAIN)


def test_explicit_span_rejects_stale_or_interleaved_content():
    markdown = "\n".join([REFRAIN[0], "intrusion", *REFRAIN[1:]])
    with pytest.raises(ValueError, match="span is stale or contains undeclared content"):
        canonicalize_reviewed_line_group(markdown, REFRAIN, reviewed_span=[1, 11])


def test_unique_group_rejects_missing_or_interleaved_or_extra_member_occurrences():
    with pytest.raises(ValueError, match="absent or ambiguous"):
        canonicalize_reviewed_line_group("one\nthree", ["one", "two", "three"])
    with pytest.raises(ValueError, match="absent or ambiguous"):
        canonicalize_reviewed_line_group("one\nintrusion\ntwo\nthree", ["one", "two", "three"])
    with pytest.raises(ValueError, match="extra undeclared occurrences"):
        canonicalize_reviewed_line_group("one\ntwo\none\nthree", ["one", "two", "three"])


def test_blank_separators_and_trailing_spaces_are_normalized_only_inside_group():
    markdown = "before  \nalpha  \n\n beta\t\n\n gamma  \nafter  "
    assert canonicalize_reviewed_line_group(markdown, ["alpha", " beta", " gamma"]) == (
        "before  \nalpha  \n beta  \n gamma\nafter  "
    )


def test_explicit_span_disambiguates_only_the_exact_complete_sequence():
    markdown = "\n".join(REFRAIN + [""] + REFRAIN)
    rendered = canonicalize_reviewed_line_group(markdown, REFRAIN, reviewed_span={"start_line": 12, "end_line": 21})
    assert rendered.splitlines()[11:21] == [
        line + ("  " if index < len(REFRAIN) - 1 else "")
        for index, line in enumerate(REFRAIN)
    ]


def test_span_reorders_only_its_exact_multiset_boundary():
    markdown = "before\nLuck: 85\n\nSTR: 60 CON: 35\n\nHP: 8\nafter"
    assert canonicalize_reviewed_line_group(
        markdown,
        ["STR: 60 CON: 35", "Luck: 85", "HP: 8"],
        reviewed_span={"start_line": 2, "end_line": 6},
    ) == "before\nSTR: 60 CON: 35  \nLuck: 85  \nHP: 8\nafter"
    with pytest.raises(ValueError, match="span must name start_line and end_line"):
        canonicalize_reviewed_line_group(
            markdown,
            ["STR: 60 CON: 35", "Luck: 85", "HP: 8"],
            reviewed_span={"start_line": 2, "end_line": 6, "sha256": "stale"},
        )


def test_author_integration_preserves_genuine_refrain_and_source_order():
    decision = {
        "overlay_preference": "view",
        "selected_blocks": [
            {"view": "view", "raw_index": index, "purpose": "structure"}
            for index in range(1, len(REFRAIN) + 1)
        ],
    }
    packet = {"views": {"view": {"blocks": [
        {"raw_index": index, "text": line}
        for index, line in enumerate(REFRAIN, start=1)
    ]}}}
    definition = {
        "kind": "line_group", "representation": "hard_break_lines",
        "raw_indices": list(range(1, len(REFRAIN) + 1)),
    }
    markdown = "\n".join(REFRAIN)
    assert _canonicalize_line_groups(markdown, decision, packet, [definition], 45) == "  \n".join(REFRAIN)

    assert canonicalize_reviewed_line_group(markdown, [row["text"] for row in packet["views"]["view"]["blocks"]]) == "  \n".join(REFRAIN)
