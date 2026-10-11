import json
from pathlib import Path

import pytest

from kb_creator.pipeline import mineru_view_recovery_plan as plans
from kb_creator.pipeline import reconstruction
import kb_creator.scripts.prepare_mineru_view_recovery as preparer
from kb_creator.scripts.prepare_mineru_view_recovery import prepare_plan
from kb_creator.tests.test_mineru_cpu_packet_b import _full_fixture, _run_adapters


def _origin(tmp_path: Path):
    source, contract, runtime, _, _, origin = _full_fixture(tmp_path)
    reconstruction.run_engine(contract, source, origin, "origin", _run_adapters(origin), runtime)
    return source, origin


def test_prepare_real_fixture_plan_load_roundtrip_and_exact_compatibility(tmp_path):
    source, origin = _origin(tmp_path)
    output = tmp_path / "recovery-plan.json"
    compatibility = {"original_pipeline_txt": {"reviewed": True, "reason": "fixture"}}
    plan = prepare_plan(
        origin_run=origin,
        origin_stage="outputs",
        source=source,
        views=["original_pipeline_txt"],
        output=output,
        wrapper_compatibility=compatibility,
    )
    loaded = plans.load_plan(output, source)
    assert loaded["views"] == ["original_pipeline_txt"]
    assert loaded["wrapper_compatibility"] == compatibility
    assert "original_pipeline_ocr" not in loaded["wrapper_compatibility"]
    assert plan["plan_sha256"] == loaded["plan_sha256"]


def test_existing_output_is_unchanged_and_rejected(tmp_path):
    source, origin = _origin(tmp_path)
    output = tmp_path / "existing.json"
    original = b"preserve this\n"
    output.write_bytes(original)
    with pytest.raises(FileExistsError):
        prepare_plan(
            origin_run=origin,
            origin_stage="outputs",
            source=source,
            views=["original_pipeline_txt"],
            output=output,
        )
    assert output.read_bytes() == original


def test_destination_created_during_validation_is_never_overwritten(tmp_path, monkeypatch):
    source, origin = _origin(tmp_path)
    output = tmp_path / "raced-plan.json"
    sentinel = b"created by another writer\n"
    real_load_plan = preparer.load_plan

    def racing_load_plan(path, source_path):
        value = real_load_plan(path, source_path)
        output.write_bytes(sentinel)
        return value

    monkeypatch.setattr(preparer, "load_plan", racing_load_plan)
    with pytest.raises(FileExistsError):
        prepare_plan(
            origin_run=origin,
            origin_stage="outputs",
            source=source,
            views=["original_pipeline_txt"],
            output=output,
        )
    assert output.read_bytes() == sentinel
    assert not list(tmp_path.glob(f".{output.name}.*.tmp"))


def test_source_mismatch_is_rejected_before_output(tmp_path):
    source, origin = _origin(tmp_path)
    mismatched = tmp_path / "other.pdf"
    mismatched.write_bytes(source.read_bytes() + b"changed")
    output = tmp_path / "recovery-plan.json"
    with pytest.raises(ValueError, match="source does not match origin run"):
        prepare_plan(
            origin_run=origin,
            origin_stage="outputs",
            source=mismatched,
            views=["original_pipeline_txt"],
            output=output,
        )
    assert not output.exists()


def test_failed_selected_receipt_and_invalid_view_are_rejected(tmp_path):
    source, origin = _origin(tmp_path)
    output = tmp_path / "recovery-plan.json"
    receipt = origin / "outputs/02-mineru-three-view/views/original_pipeline_txt/view.json"
    value = json.loads(receipt.read_text(encoding="utf-8"))
    value["state"] = "failed"
    receipt.write_text(json.dumps(value), encoding="utf-8")
    with pytest.raises(ValueError):
        prepare_plan(
            origin_run=origin,
            origin_stage="outputs",
            source=source,
            views=["original_pipeline_txt"],
            output=output,
        )
    with pytest.raises(ValueError):
        prepare_plan(
            origin_run=origin,
            origin_stage="outputs",
            source=source,
            views=["not-a-view"],
            output=tmp_path / "invalid-view.json",
        )
