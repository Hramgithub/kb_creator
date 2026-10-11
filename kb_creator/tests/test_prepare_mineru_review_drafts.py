import json
from pathlib import Path

import pytest

from kb_creator.scripts.prepare_mineru_review_drafts import prepare_review_drafts


VIEW = "original_pipeline_txt"


def _packet(page, blocks, role="body"):
    return {
        "schema": "kb_creator.mineru_merge_packet.v1",
        "source_page": page,
        "semantic_role": role,
        "views": {VIEW: {"blocks": blocks}},
    }


def _block(raw_index, block_type, text="", assets=None, level=None):
    return {
        "raw_index": raw_index,
        "source_page": 1,
        "type": block_type,
        "text": text,
        "assets": [] if assets is None else assets,
        "semantic_evidence": {"text_level": level},
    }


def _write_packet(root: Path, page: int, packet: dict):
    root.mkdir(parents=True, exist_ok=True)
    (root / f"page-{page:03d}.json").write_text(json.dumps(packet), encoding="utf-8")


def test_scaffold_preserves_complete_canonical_text_assets_and_inventory(tmp_path):
    packets = tmp_path / "packets"
    blocks = [
        _block(1, "header", "HEADER TEXT", level=2),
        _block(2, "table", "TABLE BODY", ["images/table.png"]),
        _block(3, "image", "", ["images/map.png"]),
        _block(4, "footer", "FOOTER TEXT"),
        _block(5, "page_number", "7"),
        _block(6, "mystery", ""),
    ]
    _write_packet(packets, 1, _packet(1, blocks))
    output = tmp_path / "output"
    report = prepare_review_drafts(packets, VIEW, output)
    decision = json.loads((output / "pages/page-001.json").read_text(encoding="utf-8"))
    assert decision["review"] == {"visual_reviewed": False, "notes": "review-draft scaffold; manual review required"}
    assert decision["unresolved"] and all("manual review required" in row for row in decision["unresolved"])
    assert [row["raw_index"] for row in decision["selected_blocks"]] == [1, 2, 3, 4, 5]
    assert "## HEADER TEXT" in decision["markdown"]
    for exact in ("TABLE BODY", "FOOTER TEXT", "7"):
        assert exact in decision["markdown"]
    table_asset, image_asset = decision["assets"]
    assert table_asset["placement"] == "reference_only"
    assert image_asset["placement"] == "inline"
    assert f"{{{{asset:{image_asset['logical_name']}}}}}" in decision["markdown"]
    inventory = report["pages"][0]
    assert inventory["block_count"] == len(blocks)
    assert [row["raw_index"] for row in inventory["blocks"]] == [1, 2, 3, 4, 5, 6]
    assert inventory["blocks"][5]["unresolved"] == ["unknown canonical block type 'mystery'", "empty canonical block"]
    assert not (output / "decision_set.json").exists()
    assert not (output / "reviewed_allowlist.json").exists()
    assert report["state"] == "drafts_require_manual_review"
    assert report["authority_state"] == "unverified_evidence_only"


def test_scaffold_is_deterministic_and_binds_source_packet_identity(tmp_path):
    packets = tmp_path / "packets"
    _write_packet(packets, 1, _packet(1, [_block(1, "text", "Exact body")]))
    first, second = tmp_path / "first", tmp_path / "second"
    prepare_review_drafts(packets, VIEW, first)
    prepare_review_drafts(packets, VIEW, second)
    assert (first / "pages/page-001.json").read_bytes() == (second / "pages/page-001.json").read_bytes()
    assert (first / "scaffold_inventory.json").read_bytes() == (second / "scaffold_inventory.json").read_bytes()
    inventory = json.loads((first / "scaffold_inventory.json").read_text(encoding="utf-8"))
    assert inventory["pages"][0]["source_packet"]["path"] == "page-001.json"
    assert inventory["pages"][0]["source_packet"]["sha256"]


@pytest.mark.parametrize(
    "mutator, message",
    [
        (lambda root: _write_packet(root, 2, _packet(2, [_block(1, "text", "gap")])), "noncontiguous"),
        (lambda root: _write_packet(root, 1, _packet(1, [_block(1, "text", "bad", ["../escape.png"])])), "escapes"),
        (lambda root: _write_packet(root, 1, _packet(1, [_block(1, "text", "bad", ["images/a.png", "images/a.png"])])), "repeats"),
    ],
)
def test_scaffold_rejects_invalid_packet_input_fail_closed(tmp_path, mutator, message):
    packets = tmp_path / "packets"; mutator(packets)
    output = tmp_path / "output"
    with pytest.raises(ValueError, match=message):
        prepare_review_drafts(packets, VIEW, output)
    assert not output.exists()


def test_scaffold_rejects_invalid_view_and_output_collision(tmp_path):
    packets = tmp_path / "packets"
    _write_packet(packets, 1, _packet(1, [_block(1, "text", "body")]))
    with pytest.raises(ValueError, match="unsupported"):
        prepare_review_drafts(packets, "unknown_view", tmp_path / "invalid-view")
    output = tmp_path / "output"; output.mkdir()
    with pytest.raises(FileExistsError, match="already exists"):
        prepare_review_drafts(packets, VIEW, output)
    assert list(output.iterdir()) == []


@pytest.mark.parametrize(
    "mutate, message",
    [
        (lambda packet: packet.__setitem__("schema", "kb_creator.mineru_visual_merge_packet.v1"), "packet identity"),
        (lambda packet: packet["views"][VIEW]["blocks"][0].__setitem__("raw_index", -1), "block identity"),
        (lambda packet: packet["views"][VIEW]["blocks"][0].__setitem__("source_page", 2), "source page mismatches"),
    ],
)
def test_scaffold_rejects_wrong_real_schema_negative_raw_index_and_block_page_mismatch(tmp_path, mutate, message):
    packets = tmp_path / "packets"
    packet = _packet(1, [_block(1, "text", "body")])
    mutate(packet)
    _write_packet(packets, 1, packet)
    with pytest.raises(ValueError, match=message):
        prepare_review_drafts(packets, VIEW, tmp_path / "output")
