import json

from kb_creator.scripts.complete_selected_title_roles import complete_title_spec


def _write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value), encoding="utf-8")


def _block(raw_index, text, *, kind="text", bbox=None):
    return {"raw_index": raw_index, "text": text, "type": kind,
            "bbox": bbox or [10, 20, 100, 40],
            "semantic_evidence": {"v2_title": True}}


def test_completion_uses_source_key_order_and_keeps_packet_headers_as_labels(tmp_path):
    drafts, packets = tmp_path / "drafts", tmp_path / "packets"
    decision = {"markdown": "Same\nHeader\nSame", "overlay_preference": "txt",
                "selected_blocks": [{"view": "txt", "raw_index": value, "purpose": "text"}
                                    for value in (1, 2, 3)]}
    packet = {"views": {"txt": {"blocks": [
        _block(1, "Same"), _block(2, "Header", kind="header"), _block(3, "Same"),
    ]}}}
    _write(drafts / "page-001.json", decision); _write(packets / "page-001.json", packet)
    spec = {"semantic_structure_profile": "reviewed_role_outline_and_partitions_v2",
            "pages": [{"source_page": 1, "units": []}]}

    successor, report = complete_title_spec(spec, drafts, packets)

    units = successor["pages"][0]["units"]
    assert [(unit["kind"], unit["raw_indices"]) for unit in units] == [
        ("heading", [1]), ("label", [2]), ("heading", [3]),
    ]
    assert report["generated_heading_count"] == 2
    assert report["generated_label_count"] == 1
    # The repeated reader text is addressed by a unique multiline selector,
    # rather than a global Same -> ## Same replacement.
    assert len(successor["pages"][0]["post_patches"]) == 2
    assert spec["pages"][0]["units"] == []


def test_completion_reports_unproved_source_reader_drift_without_creating_a_role(tmp_path):
    drafts, packets = tmp_path / "drafts", tmp_path / "packets"
    _write(drafts / "page-001.json", {"markdown": "Correct title", "overlay_preference": "txt",
        "selected_blocks": [{"view": "txt", "raw_index": 1, "purpose": "text"}]})
    _write(packets / "page-001.json", {"views": {"txt": {"blocks": [_block(1, "Noisy title")]}}})
    spec = {"semantic_structure_profile": "reviewed_role_outline_and_partitions_v2",
            "pages": [{"source_page": 1, "units": []}]}

    successor, report = complete_title_spec(spec, drafts, packets)

    assert successor["pages"][0]["units"] == []
    assert report["unresolved_title_count"] == 1
    assert report["unresolved_titles"][0]["raw_index"] == 1
