from copy import deepcopy

import pytest

from kb_creator.pipeline.reviewed_asset_retention import retain_reference_assets


def fixture():
    block = {"raw_index": 3, "type": "image", "text": "", "assets": ["images/a.png"]}
    packet = {"source_page": 1, "semantic_role": "body", "views": {
        view: {"blocks": [deepcopy(block)]}
        for view in ("original_pipeline_txt", "original_pipeline_ocr")}}
    draft = {"source_page": 1, "semantic_role": "body", "selected_blocks": [],
             "assets": [], "markdown": "The source text.",
             "review": {"visual_reviewed": False}, "unresolved": ["check text"]}
    return packet, draft


def test_retains_all_views_without_changing_content_or_approval():
    packet, draft = fixture()
    before = deepcopy(draft)
    result = retain_reference_assets(packet, draft)
    assert draft == before
    assert len(result["added_assets"]) == 2
    assert len({x["logical_name"] for x in result["added_assets"]}) == 2
    assert all(x["placement"] == "reference_only" for x in result["added_assets"])
    for key in ("markdown", "review", "unresolved"):
        assert result["decision"][key] == draft[key]
    assert retain_reference_assets(packet, result["decision"])["added_assets"] == []


def test_existing_inline_asset_and_selection_preserved():
    packet, draft = fixture()
    draft["selected_blocks"] = [{"view": "original_pipeline_txt", "raw_index": 3, "purpose": "asset"}]
    existing = {"view": "original_pipeline_txt", "source_path": "images/a.png",
                "logical_name": "reader-image.png", "placement": "inline"}
    draft["assets"] = [existing]
    result = retain_reference_assets(packet, draft)
    assert result["decision"]["assets"][0] == existing
    assert len(result["added_assets"]) == 1


@pytest.mark.parametrize("change", [{"text": "caption"}, {"type": "table"}, {"table_body": "<table>"}])
def test_never_turns_text_or_table_into_asset_only_selection(change):
    packet, draft = fixture()
    for view in packet["views"].values():
        view["blocks"][0].update(change)
    result = retain_reference_assets(packet, draft)
    assert result["decision"] == draft
    assert len(result["deferred_blocks"]) == 2


@pytest.mark.parametrize("path", ["../secret.png", "C:/secret.png", "/secret.png", "images\\a.png"])
def test_rejects_escaping_asset_path(path):
    packet, draft = fixture()
    packet["views"]["original_pipeline_txt"]["blocks"][0]["assets"] = [path]
    with pytest.raises(ValueError):
        retain_reference_assets(packet, draft)


def test_rejects_stale_selection_and_page_mismatch():
    packet, draft = fixture()
    draft["selected_blocks"] = [{"view": "original_pipeline_txt", "raw_index": 99, "purpose": "asset"}]
    with pytest.raises(ValueError, match="absent"):
        retain_reference_assets(packet, draft)
    draft["source_page"] = 2
    with pytest.raises(ValueError, match="identity"):
        retain_reference_assets(packet, draft)
