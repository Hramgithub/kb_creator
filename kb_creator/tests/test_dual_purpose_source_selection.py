import hashlib
import json
from pathlib import Path

import pytest

from kb_creator.scripts.materialize_mineru_ai_merge import _validate_decision


SHAPES = [
    (11, 155, "table", "Equipment Shed Patriarch Road 1 Barn Farmhouse Food Store Truck Parking Lot Apartment Building Trees Bushes 中 Trees Playground Arcanum 5 miles Corn Fields • Pumpkin Patch. • Flower Beds 000 0000 ODOC Corn Fields", "0ca05a1ddb17a2e023a24f2c7129e0726b3014a910adb7ac243a1cfd6f45c15f.jpg"),
    (160, 3147, "table", "Background Information Birth Name London Rose Sinclair (adopted at birth) Born September 27, 1989 Origin Hollywood, California United States Genres Pop, Dance Instruments Vocals, Piano Years Active 1992-present", "99630f06e712c726ce2af02a1680339be8803f2b64138aaf9514e26339ec9840.jpg"),
    (163, 3216, "image", "4", "0c9642bd315acb5c2b73c6336b6ff5c236f862aed1096fae4267758b0196fe95.jpg"),
    (178, 3560, "table", "Patriarch Road 3 Barn Farmhouse Equipment Shed 0 Pumpkin Patch Store 三 Parking Lot Flower Beds 00000 Food Apartment Truck Building Bushes Trees Trees Playground Arcanum 5 miles Corn Fields Corn Fields 0000 0000 Feet 20 40 60 80 100 The Agri-Farm", "9ff901bdfc7a43d38bcab39fdaa75f160c3872b0e38d756de36665dbff57628e.jpg"),
    (197, 3674, "table", "Birth Name London Rose Sinclair (adopted at birth) Born September 27, 1989 Origin Hollywood, California United States Genres Pop, Dance Instruments Vocals, Piano Years Active 1992-present", "d7d482e8309d90a524761b9138ef7bceefbf2be00e05fadbf55b38e7a6a38bcf.jpg"),
]
VIEW = "original_pipeline_txt"


def _fixture(tmp_path: Path, shape: tuple[int, int, str, str, str], *, purpose_order=("text", "asset")):
    page, raw_index, block_type, caption, filename = shape
    raw_root = tmp_path / "raw"
    artifacts = raw_root / "views" / VIEW / "artifacts"
    asset = artifacts / "images" / filename
    asset.parent.mkdir(parents=True)
    asset.write_bytes(b"sealed source asset")
    content_list = artifacts / "content-list.json"
    content_list.write_text("[]", encoding="utf-8")
    content_identity = {"bytes": content_list.stat().st_size, "sha256": hashlib.sha256(content_list.read_bytes()).hexdigest().upper()}
    block = {"raw_index": raw_index, "type": block_type, "text": caption, "assets": [f"images/{filename}"]}
    packet = {"source_page": page, "semantic_role": "body", "views": {VIEW: {"blocks": [block]}}}
    comparison = {"views": {VIEW: {"artifacts": {"content_list": {"base": "view_artifact_root", "view_id": VIEW, "path": "content-list.json", **content_identity}}}}}
    decision = {
        "schema": "kb_creator.mineru_ai_page_decision.v1", "source_page": page,
        "semantic_role": "body", "overlay_preference": VIEW,
        "selected_blocks": [{"view": VIEW, "raw_index": raw_index, "purpose": purpose} for purpose in purpose_order],
        "markdown": caption, "assets": [{"view": VIEW, "source_path": f"images/{filename}", "logical_name": f"p{page}.jpg", "placement": "reference_only"}],
        "unresolved": [], "review": {"visual_reviewed": False, "notes": ""},
    }
    return decision, packet, comparison, raw_root, asset, content_list


@pytest.mark.parametrize("shape", SHAPES)
@pytest.mark.parametrize("purpose_order", [("text", "asset"), ("asset", "text")])
def test_actual_dual_purpose_shapes_allow_reader_and_exact_binary(shape, purpose_order, tmp_path):
    decision, packet, comparison, raw_root, _, _ = _fixture(tmp_path, shape, purpose_order=purpose_order)
    blocks, assets, markdown = _validate_decision(decision, packet, comparison, raw_root, set())
    assert len(blocks) == 1 and blocks[0]["_selection_purpose"] == "text"
    assert len(assets) == 1 and markdown == shape[3]


@pytest.mark.parametrize("mutation", ["duplicate_text", "duplicate_asset", "text_structure", "three_purposes", "legacy_visual"])
def test_dual_purpose_rejects_incompatible_selection_groups(mutation, tmp_path):
    decision, packet, comparison, raw_root, _, _ = _fixture(tmp_path, SHAPES[0])
    row = {"view": VIEW, "raw_index": SHAPES[0][1]}
    if mutation == "duplicate_text":
        decision["selected_blocks"].append({**row, "purpose": "text"})
    elif mutation == "duplicate_asset":
        decision["selected_blocks"].append({**row, "purpose": "asset"})
    elif mutation == "text_structure":
        decision["selected_blocks"] = [{**row, "purpose": value} for value in ("text", "structure")]
    elif mutation == "three_purposes":
        decision["selected_blocks"].append({**row, "purpose": "structure"})
    else:
        decision["selected_blocks"].append({**row, "purpose": "visual"})
    with pytest.raises(ValueError):
        _validate_decision(decision, packet, comparison, raw_root, set())


def test_legacy_visual_only_selection_remains_isolated(tmp_path):
    decision, packet, comparison, raw_root, _, _ = _fixture(tmp_path, SHAPES[0])
    decision["selected_blocks"] = [{"view": VIEW, "raw_index": SHAPES[0][1], "purpose": "visual"}]
    decision["assets"] = []
    blocks, assets, _ = _validate_decision(decision, packet, comparison, raw_root, set())
    assert blocks[0]["_selection_purpose"] == "visual" and assets == []


@pytest.mark.parametrize("mutation", ["empty_caption", "changed_caption", "unproved_caption", "reader_without_asset"])
def test_image_reader_requires_exact_caption_and_asset_pair(mutation, tmp_path):
    decision, packet, comparison, raw_root, _, _ = _fixture(tmp_path, SHAPES[2])
    if mutation == "empty_caption":
        packet["views"][VIEW]["blocks"][0]["text"] = ""
    elif mutation == "changed_caption":
        decision["markdown"] = "5"
    elif mutation == "unproved_caption":
        decision["markdown"] = "4\n4"
    else:
        decision["selected_blocks"] = decision["selected_blocks"][:1]
    with pytest.raises(ValueError):
        _validate_decision(decision, packet, comparison, raw_root, set())


@pytest.mark.parametrize("mutation", ["missing_asset", "stale_content_list", "wrong_source_path", "missing_declaration"])
def test_dual_purpose_binary_identity_remains_fail_closed(mutation, tmp_path):
    decision, packet, comparison, raw_root, asset, content_list = _fixture(tmp_path, SHAPES[0])
    if mutation == "missing_asset":
        asset.unlink()
    elif mutation == "stale_content_list":
        content_list.write_text("[\"changed\"]", encoding="utf-8")
    elif mutation == "missing_declaration":
        decision["assets"] = []
    else:
        decision["assets"][0]["source_path"] = "images/other.jpg"
    with pytest.raises(ValueError):
        _validate_decision(decision, packet, comparison, raw_root, set())
