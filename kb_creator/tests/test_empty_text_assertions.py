from copy import deepcopy
import hashlib
import json
from pathlib import Path

import pytest

from kb_creator.pipeline.empty_text_assertions import RELATION, author_assertion, select_empty_sources, validate
from kb_creator.pipeline.semantic_structure import SCHEMA_V2, validate_semantic_structure
from kb_creator.scripts.audit_mineru_ai_merge_fidelity import _normalized, audit_v3_content
from kb_creator.tests.test_audit_mineru_ai_merge_fidelity import _v3_geometry, _v3_allowlist


def fixture(kind="heading"):
    text = "Restored source heading?" if kind == "heading" else "Clipped source handout li"
    line = ("## " if kind == "heading" else "> " if kind == "handout" else "") + text
    visual_path = "outputs/04-visual-merge-bundle/visual/original_pipeline_txt/pages/page-001.png"
    inventory = {visual_path: {"bytes": 7, "sha256": "A"*64}}
    packet = {"source_page": 1, "views": {view: {"blocks": [
        {"raw_index": 0, "source_page": 1, "type": "text", "text": "", "bbox": [100,100,800,200], "assets": []},
        {"raw_index": 1, "source_page": 1, "type": "text", "text": "Unchanged body.", "bbox": [100,250,800,500], "assets": []},
    ]} for view in ("original_pipeline_txt", "original_pipeline_ocr", "raster_pipeline_ocr")}}
    unit = {"id": "empty-heading", "kind": kind,
            "representation": "atx_heading" if kind == "heading" else "blockquote" if kind == "handout" else "semantic_span",
            "source_blocks": [{"view": "original_pipeline_txt", "raw_index": 0}],
            "source_fragments": [], "visual_assertion_ids": ["source-visible"],
            "markdown_span": {"start_line": 1, "end_line": 1, "sha256": hashlib.sha256(line.encode()).hexdigest().upper()},
            "container_parent": None, "semantic_parent": None, "continuation_of": None,
            "heading_level": 2 if kind == "heading" else None, "item_count": None}
    decision = {"source_page": 1, "semantic_role": "body", "markdown": line+"\n\nUnchanged body.", "assets": [],
                "review": {"visual_reviewed": True},
                "selected_blocks": [{"view": "original_pipeline_txt", "raw_index": 1, "purpose": "text"}],
                "semantic_structure": {"schema": SCHEMA_V2, "profile": "reviewed_role_outline_and_partitions_v2",
                                       "role_contract": {"role": "body", "group_id": "fixture"},
                                       "review": {"state": "complete", "visual": {"path": visual_path, **inventory[visual_path]}}, "units": [unit]}}
    select_empty_sources(decision, packet, [{"view": "original_pipeline_txt", "raw_index": 0}], 1)
    selector = {"assertion_id": "source-visible", "source_page": 1, "text": text, "bbox": [100,100,800,200],
                "relation": RELATION, "empty_source": {"view_id": "original_pipeline_txt", "raw_index": 0},
                "rationale": "Printed region inspected; all OCR views empty."}
    assertion = author_assertion(selector, packet, decision, inventory)
    return packet, decision, inventory, assertion


@pytest.mark.parametrize("kind", ["heading", "handout", "paragraph"])
def test_empty_region_preserves_raw_and_passes_fidelity_and_semantics(kind):
    packet, decision, inventory, assertion = fixture(kind)
    before = deepcopy(packet)
    report = audit_v3_content({1: packet}, {1: decision}, geometry=_v3_geometry(), visual_inventory=inventory,
                              allowlist=_v3_allowlist(assertions=[assertion]))
    assert report["passed"], report
    assert packet == before
    semantic = validate_semantic_structure({1: decision}, {1: packet}, inventory,
                                           visual_assertions={assertion["assertion_id"]: assertion})
    assert semantic["pages"][0]["validated_unit_count"] == 1


@pytest.mark.parametrize("attack", ["nonempty", "null", "bbox", "source_sha", "wrong_page_visual", "wrong_view_visual", "span", "punctuation", "hidden_link", "owner", "purpose", "duplicate_owner"])
def test_empty_region_assertions_reject_stale_or_false_proof(attack):
    packet, decision, inventory, assertion = fixture()
    if attack in {"nonempty", "null"}:
        packet["views"]["original_pipeline_txt"]["blocks"][0]["text"] = "Actual source" if attack == "nonempty" else None
    elif attack == "bbox":
        assertion["source_region"]["bbox"] = [1,2,3,4]
    elif attack == "source_sha":
        assertion["placement"]["source_block"]["original_text_sha256"] = "B"*64
    elif attack.startswith("wrong_"):
        assertion["visual"]["path"] = assertion["visual"]["path"].replace("001", "002") if attack == "wrong_page_visual" else assertion["visual"]["path"].replace("original_pipeline_txt", "raster_pipeline_ocr")
    elif attack == "span":
        assertion["placement"]["markdown_span"]["start"] += 1
    elif attack == "punctuation":
        decision["markdown"] = decision["markdown"].replace("heading?", "heading!")
    elif attack == "hidden_link":
        decision["markdown"] = "## [public](Restored source heading?)\n\nUnchanged body."
    elif attack == "owner":
        decision["semantic_structure"]["units"][0]["visual_assertion_ids"] = ["someone-else"]
    elif attack == "purpose":
        decision["selected_blocks"][-1]["purpose"] = "asset"
    else:
        decision["semantic_structure"]["units"].append(deepcopy(decision["semantic_structure"]["units"][0]))
    with pytest.raises(ValueError):
        validate(assertion, packet, decision, _normalized(decision["markdown"]))


def test_missing_assertion_does_not_accept_empty_semantic_owner():
    packet, decision, inventory, assertion = fixture()
    with pytest.raises(ValueError):
        validate_semantic_structure({1: decision}, {1: packet}, inventory, visual_assertions={})
    with pytest.raises(ValueError, match="duplicate"):
        select_empty_sources(decision, packet, [{"view": "original_pipeline_txt", "raw_index": 0}], 1)


def test_empty_text_assertion_closed_json_schema():
    from jsonschema import Draft202012Validator
    _, _, _, assertion = fixture()
    schema = json.loads((Path(__file__).parents[1] / "contracts/ai_merge_fidelity_reviewed_allowlist.v3.schema.json").read_text(encoding="utf-8"))
    validator = Draft202012Validator({"$ref": "#/$defs/assertion", "$defs": schema["$defs"]})
    validator.validate(assertion)
    bad = deepcopy(assertion)
    bad["placement"]["source_block"]["original_text_sha256"] = "B"*64
    assert list(validator.iter_errors(bad))
    bad = deepcopy(assertion)
    bad["placement"]["invented_raw_text"] = "Transcribed heading"
    assert list(validator.iter_errors(bad))
