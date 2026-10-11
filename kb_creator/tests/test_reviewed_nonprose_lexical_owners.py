from __future__ import annotations

import hashlib
import json
from pathlib import Path
import unittest

from kb_creator.pipeline.semantic_structure import (
    SemanticStructureError,
    validate_semantic_structure,
)


REPO = Path(__file__).resolve().parents[2]
SPEC_PATH = (REPO / "kb_creator/working/fears-sharp-little-needles/reviewed/source-shapes-n247-v01/spec.json")
INVENTORY_PATH = (REPO / "kb_creator/docs/plans/20260920-night-three-books/handoffs/N242-lexical-shapes-inventory-v01.json")
VISUAL_SHA = "A" * 64


def _digest(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest().upper()


def _normalized_digest(value: str) -> str:
    normalized = "".join(char for char in value.casefold() if char.isalnum())
    return _digest(normalized)


def _shape_case(row: dict, *, page: int | None = None, raw_index: int | None = None):
    page = row["page"] if page is None else page
    key_view, row_raw = row["key"]
    raw_index = row_raw if raw_index is None else raw_index
    source = row["source"]
    corrected = row["successor"]
    lines = corrected.splitlines()
    reader_lines = [line + ("  " if index < len(lines) - 1 else "")
                    for index, line in enumerate(lines)]
    start_line = row["proposed_definition"]["start_line"]
    markdown = "\n".join([""] * (start_line - 1) + reader_lines)
    source_sha = _digest(source)
    visual_path = f"outputs/04-visual-merge-bundle/visual/{key_view}/pages/page-{page:03}.png"
    fragment = {
        "view": key_view,
        "raw_index": raw_index,
        "source_sha256": source_sha,
        "normalized_sha256": _normalized_digest(source),
        "start": 0,
        "end": len(source),
        "fragment_sha256": source_sha,
    }
    kind = row["proposed_definition"]["kind"]
    unit = {
        "id": row["proposed_definition"]["id"],
        "kind": kind,
        "representation": row["proposed_definition"]["representation"],
        "source_blocks": [{"view": key_view, "raw_index": raw_index}],
        "source_fragments": [fragment],
        "markdown_span": {
            "start_line": row["proposed_definition"]["start_line"],
            "end_line": row["proposed_definition"]["end_line"],
            "sha256": _digest("\n".join(reader_lines)),
        },
        "container_parent": None,
        "semantic_parent": None,
        "continuation_of": None,
        "heading_level": None,
        "item_count": None,
    }
    decision = {
        "semantic_role": "body",
        "markdown": markdown,
        "selected_blocks": [{"view": key_view, "raw_index": raw_index, "purpose": "text"}],
        "assets": [],
        "semantic_structure": {
            "schema": "kb_creator.page_semantic_structure.v2",
            "profile": "reviewed_role_outline_and_partitions_v2",
            "role_contract": {"role": "body", "group_id": f"n247-p{page}"},
            "review": {"state": "complete", "visual": {
                "path": visual_path, "bytes": 1, "sha256": VISUAL_SHA,
            }},
            "units": [unit],
        },
        "reviewed_block_corrections": [
            {
                "view": key_view,
                "raw_index": raw_index,
                "before": before,
                "after": after,
                "reason": "N247 source-shape correction projection fixture",
                "original_text_sha256": source_sha,
            }
            for before, after in zip(source.splitlines(), corrected.splitlines(), strict=True)
            if before != after
        ],
    }
    packet = {"views": {key_view: {"blocks": [{
        "raw_index": raw_index, "text": source, "assets": [],
    }]}}}
    visual_inventory = {visual_path: {"bytes": 1, "sha256": VISUAL_SHA}}
    return page, decision, packet, visual_inventory


def _validate(case):
    page, decision, packet, visuals = case
    return validate_semantic_structure(
        {page: decision}, {page: packet}, visuals, required_pages=[page],
    )


class ReviewedNonproseLexicalOwnerTests(unittest.TestCase):
    def test_n247_spec_is_an_exact_seven_owner_successor(self):
        spec = json.loads(SPEC_PATH.read_text(encoding="utf-8"))
        base = json.loads((SPEC_PATH.parent.parent / "source077-authoring-n160-v01/spec.json").read_text(encoding="utf-8"))
        inventory = json.loads(INVENTORY_PATH.read_text(encoding="utf-8"))
        additions = {row["page"]: row["proposed_definition"] for row in inventory["rows"]}
        self.assertEqual(len(additions), 7)
        self.assertEqual(len(spec["pages"]), 200)
        self.assertEqual({key: value for key, value in spec.items() if key != "pages"}, {
            key: value for key, value in base.items() if key != "pages"
        })
        for current, original in zip(spec["pages"], base["pages"], strict=True):
            expected = original.get("units", []) + ([additions[current["source_page"]]] if current["source_page"] in additions else [])
            self.assertEqual(current["source_page"], original["source_page"])
            self.assertEqual({key: value for key, value in current.items() if key != "units"}, {
                key: value for key, value in original.items() if key != "units"
            })
            self.assertEqual(current.get("units", []), expected)
        all_ids = [unit["id"] for page in spec["pages"] for unit in page.get("units", [])]
        self.assertEqual(len(all_ids), len(set(all_ids)))
        self.assertEqual(sum(unit["kind"] == "line_group" for unit in additions.values()), 6)
        self.assertEqual(sum(unit["kind"] == "label" for unit in additions.values()), 1)


    def test_corrected_multiline_owners_reach_semantic_consumer(self):
        inventory = json.loads(INVENTORY_PATH.read_text(encoding="utf-8"))
        for row in inventory["rows"]:
            if row["proposed_definition"]["kind"] != "line_group":
                continue
            with self.subTest(page=row["page"]):
                case = _shape_case(row)
                result = _validate(case)
                self.assertEqual(result["pages"][0]["validated_unit_count"], 1)
                lines = case[1]["markdown"].splitlines()
                start = row["proposed_definition"]["start_line"]
                end = row["proposed_definition"]["end_line"]
                self.assertEqual(len(lines[start - 1:end]), end - start + 1)


    def test_six_line_category_and_author_credit_owner_preserves_all_lines(self):
        inventory = json.loads(INVENTORY_PATH.read_text(encoding="utf-8"))
        row = next(row for row in inventory["rows"] if row["page"] == 135)
        case = _shape_case(row)
        self.assertEqual(_validate(case)["pages"][0]["validated_unit_count"], 1)
        self.assertEqual([line.rstrip() for line in case[1]["markdown"].splitlines()[2:8]], [
            "MYTHOS INFECTION", "STALKING", "MURDER",
            "MENTAL DOMINATION by adam", "gauntlett & brian m.", "sammons",
        ])


    def test_multiline_owner_rejects_loss_reorder_and_duplicate(self):
        inventory = json.loads(INVENTORY_PATH.read_text(encoding="utf-8"))
        row = next(row for row in inventory["rows"] if row["page"] == 135)
        case = _shape_case(row)
        page, decision, packet, visuals = case
        lines = decision["markdown"].splitlines()
        for mutation in ("drop", "reorder", "duplicate"):
            with self.subTest(mutation=mutation):
                page, decision, packet, visuals = _shape_case(row)
                lines = decision["markdown"].splitlines()
                group_start = row["proposed_definition"]["start_line"] - 1
                group_end = row["proposed_definition"]["end_line"]
                if mutation == "drop":
                    del lines[group_end - 1]
                elif mutation == "reorder":
                    lines[group_start], lines[group_start + 1] = lines[group_start + 1], lines[group_start]
                else:
                    lines[group_start + 1] = lines[group_start]
                decision["markdown"] = "\n".join(lines)
                decision["semantic_structure"]["units"][0]["markdown_span"]["end_line"] = group_end - (mutation == "drop")
                decision["semantic_structure"]["units"][0]["markdown_span"]["sha256"] = _digest(decision["markdown"])
                with self.assertRaisesRegex(SemanticStructureError, "page 135:"):
                    _validate((page, decision, packet, visuals))


    def test_literal_hide_label_is_visible_and_rejects_wrong_source_binding(self):
        inventory = json.loads(INVENTORY_PATH.read_text(encoding="utf-8"))
        row = next(row for row in inventory["rows"] if row["page"] == 160)
        case = _shape_case(row)
        self.assertEqual(_validate(case)["pages"][0]["validated_unit_count"], 1)
        self.assertIn("[hide]", case[1]["markdown"])
        page, decision, packet, visuals = case
        decision["semantic_structure"]["units"][0]["source_blocks"][0]["raw_index"] += 1
        with self.assertRaisesRegex(SemanticStructureError, "page 160:"):
            _validate(case)


    def test_identical_handout_headings_bind_separately_by_page_and_key(self):
        inventory = json.loads(INVENTORY_PATH.read_text(encoding="utf-8"))
        rows = [row for row in inventory["rows"] if row["page"] in {162, 196}]
        cases = [_shape_case(row) for row in rows]
        decisions = {case[0]: case[1] for case in cases}
        packets = {case[0]: case[2] for case in cases}
        visuals = {key: value for case in cases for key, value in case[3].items()}
        report = validate_semantic_structure(decisions, packets, visuals, required_pages=[162, 196])
        self.assertEqual([row["source_page"] for row in report["pages"]], [162, 196])
        self.assertEqual([decision["semantic_structure"]["units"][0]["source_blocks"] for decision in decisions.values()], [
            [{"view": "original_pipeline_txt", "raw_index": 3191}],
            [{"view": "original_pipeline_txt", "raw_index": 3649}],
        ])
