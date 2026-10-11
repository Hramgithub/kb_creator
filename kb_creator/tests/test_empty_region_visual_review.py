import json

import pytest
from pypdf import PdfWriter

from kb_creator.scripts.build_empty_region_visual_review import pixel_box, validate_rows
from kb_creator.scripts.probe_empty_region_coverage import excerpt_matches, probe


def fixture(tmp_path):
    source = tmp_path / "source.pdf"
    writer = PdfWriter()
    writer.add_blank_page(width=612, height=792)
    writer.write(str(source))
    key = {"view": "original_pipeline_txt", "raw_index": 5}
    bbox = [100, 200, 300, 400]
    report = {"rows": [{"source_page": 1, "source_key": key,
                        "witnesses": [{"source_key": key, "text": "", "bbox": bbox}]}]}
    packet = {"source_page": 1, "views": {key["view"]: {"blocks": [{"raw_index": 5, "text": "", "bbox": bbox}]}}}
    (tmp_path / "page-001.json").write_text(json.dumps(packet), encoding="utf-8")
    return report, source, packet


def test_exact_region_and_padding():
    assert pixel_box([100, 200, 300, 400], (1224, 1584)) == (122, 316, 368, 634)
    assert pixel_box([0, 0, 1000, 1000], (1224, 1584), 15) == (0, 0, 1224, 1584)


def test_excerpt_coordinates_and_repeated_witnesses():
    text = "Build: 1  \nMove: 8\n\nBuild: 1 Move: 8"
    matches = excerpt_matches("Build: 1 Move: 8", text)
    assert len(matches) == 2
    assert matches[0] == {"start_char": 0, "end_char": 18, "text": "Build: 1  \nMove: 8"}
    assert excerpt_matches("Build: 2 Move: 8", text) == []
    assert excerpt_matches("build: 1 Move: 8", text) == []
    assert excerpt_matches("Build 1 Move: 8", text) == []
    with pytest.raises(ValueError):
        excerpt_matches("  ", text)


@pytest.mark.parametrize("box", [[0, 0, 0, 10], [-1, 0, 20, 30], [0, 0, 1001, 30], [0, 0, float('nan'), 10], [True, 0, 10, 20]])
def test_invalid_geometry_rejected(box):
    with pytest.raises(ValueError):
        pixel_box(box, (100, 100))


def test_packet_bound_observation(tmp_path):
    report, source, _ = fixture(tmp_path)
    rows, authorities = validate_rows(report, tmp_path, source)
    assert len(rows) == len(authorities) == 1
    assert rows[0]["bbox"] == [100, 200, 300, 400]


@pytest.mark.parametrize("change", ["nonempty", "bbox", "duplicate", "page", "crop", "rotation"])
def test_stale_or_unsupported_observation_rejected(tmp_path, change):
    report, source, packet = fixture(tmp_path)
    if change == "nonempty":
        packet["views"]["original_pipeline_txt"]["blocks"][0]["text"] = "visible"
    elif change == "bbox":
        report["rows"][0]["witnesses"][0]["bbox"] = [1, 2, 3, 4]
    elif change == "duplicate":
        report["rows"] *= 2
    elif change == "page":
        packet["source_page"] = 2
    else:
        writer = PdfWriter()
        page = writer.add_blank_page(width=612, height=792)
        if change == "crop":
            page.cropbox.upper_right = (500, 700)
        else:
            page.rotate(90)
        writer.write(str(source))
    (tmp_path / "page-001.json").write_text(json.dumps(packet), encoding="utf-8")
    with pytest.raises(ValueError):
        validate_rows(report, tmp_path, source)


def test_probe_does_not_reuse_distant_occurrence(tmp_path):
    drafts, packets = tmp_path / "drafts", tmp_path / "packets"
    drafts.mkdir()
    packets.mkdir()
    manifest = tmp_path / "manifest.json"
    triage = tmp_path / "triage.json"
    manifest.write_text(json.dumps({"rows": [{"region_id": 1, "source_page": 1, "source_key": {"view": "original_pipeline_txt", "raw_index": 1}}]}))
    triage.write_text(json.dumps({"rows": [{"region_id": 1, "excerpts": ["Separate occurrence"]}]}))
    (drafts / "page-003.json").write_text(json.dumps({"markdown": "Separate occurrence"}))
    result = probe(manifest, triage, drafts, packets, tmp_path / "probe.json")
    assert result["rows"][0]["probes"][0]["matches"] == []
    assert result["rows"][0]["all_excerpts_have_reader_candidate"] is False
    (drafts / "page-002.json").write_text(json.dumps({"markdown": "Separate occurrence"}))
    result = probe(manifest, triage, drafts, packets, tmp_path / "probe2.json")
    assert result["rows"][0]["all_excerpts_have_reader_candidate"] is True
    assert result["rows"][0]["probes"][0]["matches"][0]["source_page"] == 2
    with pytest.raises(FileExistsError):
        probe(manifest, triage, drafts, packets, tmp_path / "probe2.json")
    triage.write_text(json.dumps({"rows": [{"region_id": 2, "excerpts": ["Separate occurrence"]}]}))
    with pytest.raises(ValueError, match="every region"):
        probe(manifest, triage, drafts, packets, tmp_path / "probe3.json")
