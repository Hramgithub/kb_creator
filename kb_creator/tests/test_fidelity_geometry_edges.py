import json
from pathlib import Path

import pytest

from kb_creator.scripts.audit_mineru_ai_merge_fidelity import (
    _make_unit, _public_unit, audit_v3_content,
)
from kb_creator.tests.test_audit_mineru_ai_merge_fidelity import (
    _running_header_case, _subspan_case, _v3_allowlist, _v3_geometry, v2_decision,
)


@pytest.mark.parametrize("overlap,neighbor,passed", [
    (4, "neighbor", True),
    (8, "neighbor", True),
    (9, "neighbor", False),
    (4, "beta neighbor", False),
    (0, "beta neighbor", True),
])
def test_subspan_line_edge_overlap_keeps_one_text_owner(overlap, neighbor, passed):
    packet = _subspan_case()
    packet["views"]["original_pipeline_txt"]["blocks"].append({
        "raw_index": 1, "source_page": 1, "type": "text",
        "bbox": [150, 180 - overlap, 250, 260], "text": neighbor,
    })
    decision = v2_decision("alpha beta gamma " + neighbor, [
        ("original_pipeline_txt", 0), ("original_pipeline_txt", 1),
    ])
    report = audit_v3_content({1: packet}, {1: decision}, allowlist=_v3_allowlist(),
                              geometry=_v3_geometry(), visual_inventory={})
    assert report["passed"] is passed


@pytest.mark.parametrize("bottom,passed", [(105, True), (120, True), (121, False)])
def test_reviewed_running_header_below_six_percent_with_body_title(bottom, passed):
    packets, decisions, exclusions, inventory, geometry = _running_header_case()
    for page, packet in packets.items():
        for view in packet["views"].values():
            view["blocks"][0]["text"] = "DISSOCIATION details"
        decisions[page]["markdown"] = "DISSOCIATION details"
        header = packet["views"]["raster_pipeline_ocr"]["blocks"][1]
        header["bbox"] = [400, bottom - 30, 650, bottom]
        exclusions[page - 1]["unit"] = _public_unit(_make_unit(page, "raster_pipeline_ocr", header))
    report = audit_v3_content(packets, decisions, allowlist=_v3_allowlist(exclusions=exclusions),
                              geometry=geometry, visual_inventory=inventory)
    assert report["passed"] is passed
    import jsonschema
    contract = Path(__file__).resolve().parents[1] / "contracts/ai_merge_fidelity_audit.v3.schema.json"
    policy_schema = json.loads(contract.read_text(encoding="utf-8"))["properties"]["policy"]
    jsonschema.validate(report["policy"], policy_schema)


def test_running_headers_can_mirror_on_facing_pages():
    packets, decisions, exclusions, inventory, geometry = _running_header_case()
    for page, packet in packets.items():
        header = packet["views"]["raster_pipeline_ocr"]["blocks"][1]
        header["bbox"] = [350, 70, 500, 100] if page == 1 else [500, 70, 650, 100]
        exclusions[page - 1]["unit"] = _public_unit(_make_unit(page, "raster_pipeline_ocr", header))
    report = audit_v3_content(packets, decisions, allowlist=_v3_allowlist(exclusions=exclusions),
                              geometry=geometry, visual_inventory=inventory)
    assert report["passed"]
