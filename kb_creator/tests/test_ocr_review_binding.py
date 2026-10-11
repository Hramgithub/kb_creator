from __future__ import annotations

import json
from pathlib import Path

import pytest

from kb_creator.pipeline.ocr_review_binding import bind_ocr_reviews, VIEW
from kb_creator.pipeline.identity import file_identity, deterministic_inventory
from kb_creator.pipeline.mechanical_reconstruction import VIEWS


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False), encoding="utf-8")


@pytest.fixture
def inputs(tmp_path):
    run = tmp_path / "run"
    stage = run / "outputs/04-visual-merge-bundle"
    metadata = run / "outputs/02-mineru-three-view/views" / VIEW / "source_content_list.json"
    write(run / "run.json", {"source": {"sha256": "A" * 64, "page_count": 1}})
    write(metadata, [{"text": "WESTERNUNION", "page_idx": 0}])
    write(stage / "visual/visual_manifest.json", {"files": []})
    packet = {"schema": "kb_creator.mineru_merge_packet.v1", "source_page": 1,
              "views": {name: {"blocks": [{"raw_index": 0, "text": "WESTERNUNION"}]} for name in VIEWS}}
    write(stage / "merge_packets/pages/page-001.json", packet)
    renders = tmp_path / "renders"
    renders.mkdir()
    (renders / "page-01.jpg").write_bytes(b"source-render")
    visual_sha = file_identity(renders / "page-01.jpg")["sha256"]
    review = tmp_path / "review"
    report = {"schema": "kb_creator.preliminary_ocr_visual_review.v1", "view": VIEW,
              "metadata_sha256": file_identity(metadata)["sha256"], "pages": [{"source_page": 1,
                  "visual_sha256": visual_sha, "ordered_raw_indices": [0], "unresolved": [],
                  "ocr_corrections": [{"raw_index": 0, "before": "WESTERNUNION", "after": "WESTERN UNION", "reason": "Visible word boundary"}]}]}
    write(review / "report.json", report)
    coverage = {"source_sha256": "A" * 64, "metadata_sha256": file_identity(metadata)["sha256"],
                "page_count": 1, "exact_full_block_corrections": 1, "pages": [{"source_page": 1,
                    "report": "report.json", "report_sha256": file_identity(review / "report.json")["sha256"], "visual_sha256": visual_sha}]}
    write(review / "coverage.json", coverage)
    write(review / "source-review.json", {"schema": "kb_creator.source_review_coverage.v1", "source": {"sha256": "A" * 64, "pages": 1}, "pages": [{"page": 1, "render": "page-01.jpg", "sha256": visual_sha}]})
    return run, review / "coverage.json", review / "source-review.json", renders, metadata


def call(inputs, output):
    return bind_ocr_reviews(*inputs, output, authority_validator=lambda _: None)


def test_binds_full_block_and_preserves_inputs_deterministically(inputs, tmp_path):
    before = deterministic_inventory(inputs[0])
    first = call(inputs, tmp_path / "first")
    second = call(inputs, tmp_path / "second")
    assert first == second
    assert first["reconstruction_accepted"] is False
    row = first["corrections"][0]
    assert (row["source_page"], row["view"], row["raw_index"], row["before"], row["after"]) == (1, VIEW, 0, "WESTERNUNION", "WESTERN UNION")
    assert (tmp_path / "first/reports/report.json").read_bytes() == (inputs[1].parent / "report.json").read_bytes()
    assert deterministic_inventory(inputs[0]) == before


def test_explicit_furniture_outside_prose_order_remains_evidence(inputs, tmp_path):
    run, coverage, _, _, _ = inputs
    packet_path = run / "outputs/04-visual-merge-bundle/merge_packets/pages/page-001.json"
    packet = json.loads(packet_path.read_text())
    packet["views"][VIEW]["blocks"].append({"raw_index": 1, "text": "", "type": "image"})
    write(packet_path, packet)
    report_path = coverage.parent / "report.json"
    report = json.loads(report_path.read_text())
    report["pages"][0]["source_furniture"] = [{"raw_index": 1, "reason": "source-reviewed border"}]
    write(report_path, report)
    cov = json.loads(coverage.read_text())
    cov["pages"][0]["report_sha256"] = file_identity(report_path)["sha256"]
    write(coverage, cov)
    bound = call(inputs, tmp_path / "bound")
    assert bound["pages"][0]["reviewed_dispositions"]["source_furniture"][0]["raw_index"] == 1
    assert len(bound["corrections"]) == 1


def test_nested_reports_cannot_collide_in_evidence_bundle(inputs, tmp_path):
    run, coverage, source_review, _, _ = inputs
    state = json.loads((run / "run.json").read_text())
    state["source"]["page_count"] = 2
    write(run / "run.json", state)
    pages = run / "outputs/04-visual-merge-bundle/merge_packets/pages"
    packet = json.loads((pages / "page-001.json").read_text())
    packet["source_page"] = 2
    for view in packet["views"].values():
        view["blocks"] = [{"raw_index": 1, "text": ""}]
    write(pages / "page-002.json", packet)
    report = json.loads((coverage.parent / "report.json").read_text())
    report["pages"][0].update(source_page=2, ordered_raw_indices=[1], ocr_corrections=[])
    nested = coverage.parent / "nested/report.json"
    write(nested, report)
    cov = json.loads(coverage.read_text())
    cov["page_count"] = 2
    cov["pages"].append({**cov["pages"][0], "source_page": 2, "report": "nested/report.json", "report_sha256": file_identity(nested)["sha256"]})
    write(coverage, cov)
    visual = json.loads(source_review.read_text())
    visual["source"]["pages"] = 2
    visual["pages"].append({**visual["pages"][0], "page": 2})
    write(source_review, visual)
    with pytest.raises(ValueError, match="filenames collide"):
        call(inputs, tmp_path / "bound")


def test_unmentioned_block_is_explicitly_unreviewed_not_silently_accepted(inputs, tmp_path):
    run = inputs[0]
    packet_path = run / "outputs/04-visual-merge-bundle/merge_packets/pages/page-001.json"
    packet = json.loads(packet_path.read_text())
    packet["views"][VIEW]["blocks"].append({"raw_index": 1, "text": "", "type": "image"})
    write(packet_path, packet)
    bound = call(inputs, tmp_path / "bound")
    assert bound["pages"][0]["unreviewed_raw_indices"] == [1]
    assert [row["raw_index"] for row in bound["corrections"]] == [0]
    assert bound["reconstruction_accepted"] is False


@pytest.mark.parametrize("case", ["stale_report", "stale_render", "stale_metadata", "missing_page", "duplicate_page", "before", "duplicate_correction", "control", "foreign_source", "missing_block", "traversal"])
def test_rejects_unbound_or_ambiguous_review(inputs, tmp_path, case):
    run, cov_path, src_path, renders, metadata = inputs
    report_path = cov_path.parent / "report.json"
    cov = json.loads(cov_path.read_text())
    report = json.loads(report_path.read_text())
    if case == "stale_render":
        (renders / "page-01.jpg").write_bytes(b"changed")
    elif case == "stale_metadata":
        write(metadata, [{"text": "changed", "page_idx": 0}])
    elif case in {"missing_page", "duplicate_page"}:
        cov["pages"] = [] if case == "missing_page" else cov["pages"] * 2
    elif case == "foreign_source":
        cov["source_sha256"] = "B" * 64
    elif case == "traversal":
        cov["pages"][0]["report"] = "../../outside.json"
    else:
        correction = report["pages"][0]["ocr_corrections"][0]
        if case in {"stale_report", "before"}:
            correction["before"] = "not the packet text"
        elif case == "duplicate_correction":
            report["pages"][0]["ocr_corrections"] *= 2
        elif case == "control":
            correction["after"] = "bad\x01text"
        elif case == "missing_block":
            report["pages"][0]["ordered_raw_indices"] = []
        write(report_path, report)
        if case != "stale_report":
            cov["pages"][0]["report_sha256"] = file_identity(report_path)["sha256"]
    write(cov_path, cov)
    with pytest.raises((ValueError, FileNotFoundError)):
        call(inputs, tmp_path / "bound")
    assert not (tmp_path / "bound").exists()
