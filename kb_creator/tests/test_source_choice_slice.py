import json

import pytest

from kb_creator.pipeline.identity import file_identity, sha256_bytes
from kb_creator.pipeline.semantic_structure import _normalized
from kb_creator.pipeline.source_choice_slice import SourceChoiceSliceError, SourceSlice, apply_sealed_slices, slice_record
from kb_creator.pipeline import source_choice_translation as translation


def _hash(value: str) -> str:
    return sha256_bytes(value.encode("utf-8"))


def test_sealed_slices_apply_right_to_left_and_preserve_surroundings():
    container = "prefix 1D6 middle 1D6 suffix"
    first = slice_record(container, 7, 10)
    second = slice_record(container, 18, 21)
    result = apply_sealed_slices(container, [
        SourceSlice(first["raw_character_start"], first["raw_character_end"], first["raw_text_sha256"], "ID6-long"),
        SourceSlice(second["raw_character_start"], second["raw_character_end"], second["raw_text_sha256"], "ID6"),
    ], container_sha256=_hash(container))
    assert result == "prefix ID6-long middle ID6 suffix"


def test_sealed_slices_reject_overlap_and_stale_predecessor():
    container = "abcDEFghi"
    evidence = slice_record(container, 3, 6)
    item = SourceSlice(3, 6, evidence["raw_text_sha256"], "XYZ")
    try:
        apply_sealed_slices(container, [item, SourceSlice(5, 8, _hash("Fgh"), "Q")], container_sha256=_hash(container))
    except SourceChoiceSliceError as error:
        assert "overlap" in str(error)
    else:
        raise AssertionError("overlapping intervals were accepted")
    try:
        apply_sealed_slices("abcXXXghi", [item], container_sha256=_hash("abcXXXghi"))
    except SourceChoiceSliceError as error:
        assert "predecessor drift" in str(error)
    else:
        raise AssertionError("stale interval was accepted")


def _composite_fixture(tmp_path):
    container = "prefix 1D6 repeated 1D6 tail"
    # The reader span names the second occurrence.  A search-based route could
    # silently choose the first; the semantic-unit coordinate selects index 19.
    markdown = "header\n" + container
    decision = {
        "markdown": markdown,
        "selected_blocks": [{"purpose": "text", "view": "raster", "raw_index": 7}],
        "semantic_structure": {"units": [{"id": "unit", "source_blocks": [{"view": "raster", "raw_index": 7}], "markdown_span": {
            "start_line": 2, "end_line": 2, "sha256": _hash(container)},
            "source_fragments": [{"view": "raster", "raw_index": 7, "start": 0,
                "end": len(container), "source_sha256": _hash(container), "fragment_sha256": _hash(container),
                "normalized_sha256": _hash(_normalized(container))}]}]},
    }
    path = tmp_path / "page-001.json"; path.write_text(json.dumps(decision), encoding="utf-8")
    second = container.rfind("1D6")
    binding = {"source_page": 1, "reader_anchor": {"semantic_unit_id": "unit"},
        "reader_projection": {"reader_text": "1D6"},
        "page_reader_span": {"character_start": len("header\n") + second,
            "character_end": len("header\n") + second + 3, "text_sha256": _hash("1D6")},
        "decision": {"path": path.name, **file_identity(path)},
        "stage05_audit": {"path": "unused", "bytes": 1, "sha256": "x"}}
    alternatives = [
        {"alternative_id": "txt", "selectable": True, "raw_text": "1D6", "raw_text_sha256": _hash("1D6")},
        {"alternative_id": "ocr", "selectable": True, "raw_text": "ID6", "raw_text_sha256": _hash("ID6")},
    ]
    row = {"kind": "selected", "markdown_span": [len(_normalized("header\n")), len(_normalized(markdown))],
        "unit": {"view_id": "raster", "raw_index": 7,
        "original_text_sha256": _hash(container)}}
    return container, second, binding, alternatives, row


def test_composite_replay_uses_unit_coordinates_not_repeated_substring_search(tmp_path):
    """A larger selected container may replay a diagnostic tail only by offsets."""
    container, second, binding, alternatives, row = _composite_fixture(tmp_path)
    replay = translation._composite_source_slice_replay(tmp_path, binding, alternatives,
        stage05_pages={1: {"ordered_proof_stream": [row]}}, key={"view": "raster", "raw_index": 7},
        anchor_container={"text": container, "source_locator": {"view": "raster", "raw_index": 7, "field": "text"}})
    assert replay["raw_source_slice"] == {"raw_character_start": second, "raw_character_end": second + 3,
        "raw_text_sha256": _hash("1D6")}
    assert replay["diagnostic_baseline_alternative_id"] == "txt"
    assert alternatives[1]["reader_text"] == "ID6"
    assert replay["normalized_source_slice"] == [len(_normalized("header\n" + container[:second])),
                                                len(_normalized("header\n" + container[:second + 3]))]


@pytest.mark.parametrize("bad_span", [None, [6], [6, 7, 8], [False, 6], [0, 23], [7, 29], [6, 28]])
def test_composite_replay_rejects_forged_normalized_container_range(tmp_path, bad_span):
    container, _, binding, alternatives, row = _composite_fixture(tmp_path)
    row["markdown_span"] = bad_span
    with pytest.raises(translation.SourceChoiceError, match="normalized container range"):
        translation._composite_source_slice_replay(tmp_path, binding, alternatives,
            stage05_pages={1: {"ordered_proof_stream": [row]}}, key={"view": "raster", "raw_index": 7},
            anchor_container={"text": container, "source_locator": {"view": "raster", "raw_index": 7, "field": "text"}})


def test_composite_replay_rejects_stale_normalized_fragment_hash(tmp_path):
    container, _, binding, alternatives, row = _composite_fixture(tmp_path)
    path = tmp_path / binding["decision"]["path"]
    decision = json.loads(path.read_text(encoding="utf-8"))
    decision["semantic_structure"]["units"][0]["source_fragments"][0]["normalized_sha256"] = _hash("stale")
    path.write_text(json.dumps(decision), encoding="utf-8")
    binding["decision"] = {"path": path.name, **file_identity(path)}
    with pytest.raises(translation.SourceChoiceError, match="fragment-to-unit"):
        translation._composite_source_slice_replay(tmp_path, binding, alternatives,
            stage05_pages={1: {"ordered_proof_stream": [row]}}, key={"view": "raster", "raw_index": 7},
            anchor_container={"text": container, "source_locator": {"view": "raster", "raw_index": 7, "field": "text"}})


@pytest.mark.parametrize("fault", [None, "block_digest", "packet_drift", "duplicate_block"])
def test_composite_container_uses_real_sealed_packet_block_shape(tmp_path, fault):
    packet = tmp_path / "outputs/04-visual-merge-bundle/merge_packets/pages/page-001.json"
    packet.parent.mkdir(parents=True)
    block = {"raw_index": 7, "text": "prefix 1D6 tail", "type": "text"}
    if fault == "block_digest":
        block["text_sha256"] = _hash("wrong")
    blocks = [block, dict(block)] if fault == "duplicate_block" else [block]
    value = {"views": {"raster": {"blocks": blocks}}}
    packet.write_text(json.dumps(value), encoding="utf-8")
    report = {"run_root": str(tmp_path), "pages": [{"source_page": 1,
        "packet": {"path": packet.name, **file_identity(packet)}}]}
    if fault == "packet_drift":
        packet.write_text(json.dumps({"views": {}}), encoding="utf-8")
    if fault:
        with pytest.raises(translation.SourceChoiceError):
            translation._packet_source_block(report, {"source_page": 1}, {"view": "raster", "raw_index": 7})
    else:
        result = translation._packet_source_block(report, {"source_page": 1}, {"view": "raster", "raw_index": 7})
        assert result["text"] == block["text"]
        assert result["packet"]["sha256"] == file_identity(packet)["sha256"]
