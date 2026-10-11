from __future__ import annotations

import copy
import json
from pathlib import Path

from kb_creator.scripts.materialize_mineru_ai_merge import _validated_v2_title_role


FIXTURES = Path(__file__).parent / "fixtures" / "grouped_titles"


def _actual(page: int):
    fixture = json.loads((FIXTURES / f"page-{page:03}.json").read_text(encoding="utf-8"))
    return fixture["decision"], fixture["packet"]


def _assert_group(decision: dict, packet: dict, expected: bool) -> None:
    unit = decision["semantic_structure"]["units"][0]
    for source in unit["source_blocks"]:
        block = next(block for block in packet["views"][source["view"]]["blocks"] if block["raw_index"] == source["raw_index"])
        assert _validated_v2_title_role(decision, packet, block["text"], (source["view"], source["raw_index"]), set()) is expected


def test_actual_pages_63_and_97_allow_only_complete_ordered_heading_groups():
    for page in (63, 97):
        decision, packet = _actual(page)
        _assert_group(decision, packet, True)


def test_grouped_heading_rejects_reorder_omission_duplicate_stale_and_partial_fragment():
    decision, packet = _actual(63)
    for mutation in ("reorder", "omission", "duplicate", "stale", "partial"):
        broken = copy.deepcopy(decision)
        unit = broken["semantic_structure"]["units"][0]
        if mutation == "reorder":
            unit["source_blocks"][0], unit["source_blocks"][1] = unit["source_blocks"][1], unit["source_blocks"][0]
        elif mutation == "omission":
            unit["source_blocks"] = unit["source_blocks"][:-1]
        elif mutation == "duplicate":
            unit["source_blocks"][1] = dict(unit["source_blocks"][0])
        elif mutation == "stale":
            unit["source_fragments"][0]["source_sha256"] = "0" * 64
        else:
            unit["source_fragments"][0]["end"] -= 1
        _assert_group(broken, packet, False)


def test_grouped_heading_rejects_wrong_owner_and_lexical_change():
    decision, packet = _actual(97)
    wrong_owner = copy.deepcopy(decision)
    wrong_owner["semantic_structure"]["units"].append(copy.deepcopy(wrong_owner["semantic_structure"]["units"][0]))
    _assert_group(wrong_owner, packet, False)
    lexical = copy.deepcopy(decision)
    lexical["markdown"] = lexical["markdown"].replace("WAITING TO BE BORN", "WAITING TO BE GONE")
    _assert_group(lexical, packet, False)
