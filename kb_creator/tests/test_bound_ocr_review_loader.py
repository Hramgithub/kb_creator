from __future__ import annotations

import json
import shutil
from pathlib import Path

import pytest

from kb_creator.pipeline.bound_ocr_review_loader import load_bound_ocr_reviews
from kb_creator.pipeline.identity import file_identity
from kb_creator.pipeline.mechanical_reconstruction import _canonical, _sha
from kb_creator.tests.test_ocr_review_binding import call, inputs


def _bound(inputs, tmp_path):
    result = call(inputs, tmp_path / "bound")
    ledger = tmp_path / "bound" / "bound-corrections.json"
    return ledger, result


def _reseal(path: Path):
    value = json.loads(path.read_text(encoding="utf-8"))
    value.pop("ledger_sha256", None)
    value["ledger_sha256"] = _sha(_canonical(value))
    path.write_text(json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + "\n", encoding="utf-8")


def _load(inputs, ledger):
    return load_bound_ocr_reviews(inputs[0], ledger, authority_validator=lambda _: None)


def test_valid_one_row_ledger_loads(inputs, tmp_path):
    ledger, bound = _bound(inputs, tmp_path)
    value, mapping = _load(inputs, ledger)
    assert value["schema"] == "kb_creator.bound_ocr_review.v1"
    assert len(mapping) == 1
    assert mapping[(1, "original_pipeline_ocr", 0)]["after"] == "WESTERN UNION"
    assert bound["ledger_sha256"] == json.loads(ledger.read_text())["ledger_sha256"]


def test_source_bound_v2_report_loads_without_flat_field_assumptions(inputs, tmp_path):
    report_path = inputs[1].parent / "report.json"
    report = json.loads(report_path.read_text())
    report["schema"] = "kb_creator.preliminary_ocr_visual_review.v2"
    report["ocr_view"] = {"name": report.pop("view"), "source_content_list_sha256": report.pop("metadata_sha256")}
    report_path.write_text(json.dumps(report), encoding="utf-8")
    coverage = json.loads(inputs[1].read_text())
    coverage["pages"][0]["report_sha256"] = file_identity(report_path)["sha256"]
    inputs[1].write_text(json.dumps(coverage), encoding="utf-8")
    ledger, _ = _bound(inputs, tmp_path)
    assert len(_load(inputs, ledger)[1]) == 1


def test_changed_correction_and_resealed_ledger_does_not_replace_report(inputs, tmp_path):
    ledger, value = _bound(inputs, tmp_path)
    value["corrections"][0]["after"] = "invented"
    value["corrections"][0]["after_sha256"] = _sha(b"invented")
    ledger.write_text(json.dumps(value), encoding="utf-8")
    _reseal(ledger)
    with pytest.raises(ValueError, match="differs from reviewed report"):
        _load(inputs, ledger)


@pytest.mark.parametrize("case", [
    "mutated_report_resealed", "missing_correction_resealed", "wrong_selector_resealed",
    "corrupt_render_resealed", "corrupt_report", "duplicate_correction_resealed",
    "stale_metadata", "stale_packet", "evidence_path_escape",
])
def test_loader_rejects_tampered_or_stale_bound_evidence(inputs, tmp_path, case):
    ledger, _ = _bound(inputs, tmp_path)
    value = json.loads(ledger.read_text(encoding="utf-8"))
    report = ledger.parent / "reports" / "report.json"
    render = Path(value["corrections"][0]["source_render"]["path"])
    if case == "mutated_report_resealed":
        report.write_text(report.read_text(encoding="utf-8") + "\n", encoding="utf-8")
        value["evidence"]["reports/report.json"] = file_identity(report)
    elif case == "missing_correction_resealed":
        value["corrections"] = []
    elif case == "wrong_selector_resealed":
        value["corrections"][0]["raw_index"] = 99
    elif case == "corrupt_render_resealed":
        render.write_bytes(render.read_bytes() + b"tamper")
        value["corrections"][0]["source_render"] = {"path": str(render), **file_identity(render)}
    elif case == "corrupt_report":
        report.write_text("{broken", encoding="utf-8")
    elif case == "duplicate_correction_resealed":
        value["corrections"].append(dict(value["corrections"][0]))
    elif case == "stale_metadata":
        metadata = inputs[4]
        metadata.write_text(json.dumps([{"text": "changed", "page_idx": 0}]), encoding="utf-8")
    elif case == "stale_packet":
        packet = inputs[0] / "outputs/04-visual-merge-bundle/merge_packets/pages/page-001.json"
        data = json.loads(packet.read_text(encoding="utf-8"))
        data["views"]["original_pipeline_ocr"]["blocks"][0]["text"] = "changed"
        packet.write_text(json.dumps(data), encoding="utf-8")
    elif case == "evidence_path_escape":
        value["evidence"]["reports/report.json"] = {"bytes": 1, "sha256": "0" * 64}
    if case.endswith("resealed") or case in {"mutated_report_resealed", "corrupt_render_resealed"}:
        ledger.write_text(json.dumps(value), encoding="utf-8")
        _reseal(ledger)
    else:
        ledger.write_text(json.dumps(value), encoding="utf-8")
    with pytest.raises((ValueError, FileNotFoundError, json.JSONDecodeError)):
        _load(inputs, ledger)
