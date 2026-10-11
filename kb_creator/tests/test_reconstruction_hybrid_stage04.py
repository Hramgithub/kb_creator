"""Focused transaction tests for the mixed replay/executed Stage 04 executor."""
from __future__ import annotations

from pathlib import Path

import pytest

from kb_creator.pipeline import reconstruction
from kb_creator.pipeline import reconstruction_hybrid_stage04 as stage04
from kb_creator.pipeline.identity import file_identity


def _run(tmp_path: Path) -> dict:
    script = Path(__file__).parents[1] / "scripts/build_mineru_visual_merge_bundle.py"
    source = tmp_path / "source.pdf"
    contract = tmp_path / "contract.json"
    source.write_bytes(b"source")
    contract.write_text("{}", encoding="utf-8")
    return {
        "local": {"run_root": str(tmp_path), "source_path": str(source), "contract_path": str(contract)},
        "source": {"path_hint": "source.pdf", **file_identity(source)},
        "contract": {"path_hint": "contract.json", **file_identity(contract)},
        "portable_identity_sha256": "A" * 64,
        "options": {"fixture": True}, "toolchain": [{"name": "injected_adapters", "version": "test"}],
        "implementation": {"files": [{"path": "kb_creator/scripts/build_mineru_visual_merge_bundle.py", **file_identity(script)}], "inventory_sha256": "B" * 64},
    }


def test_stage04_publishes_a_direct_v1_manifest_and_validates_it(tmp_path, monkeypatch):
    run = _run(tmp_path)
    upstream = [{"stage_id": "01-prepare-inputs", "manifest_sha256": "1" * 64}]
    monkeypatch.setattr(stage04, "_validate_live_bindings", lambda *_: None)
    monkeypatch.setattr(stage04, "_validate_output", lambda *_: None)

    def build(output: Path) -> dict:
        output.mkdir()
        (output / "bundle.txt").write_text("fresh", encoding="utf-8")
        return {"adapter": "fresh"}

    receipt = stage04.invoke_stage04(tmp_path, run, upstream, reconstruction.StageAdapter("visual_merge_bundle", build))

    assert receipt["stage_id"] == "04-visual-merge-bundle"
    assert stage04.validate_stage04(tmp_path, run, upstream) == receipt
    assert (tmp_path / "outputs/04-visual-merge-bundle/bundle.txt").read_text(encoding="utf-8") == "fresh"


def test_stage04_retains_owned_failure_without_a_stage_manifest(tmp_path, monkeypatch):
    run = _run(tmp_path)
    monkeypatch.setattr(stage04, "_validate_live_bindings", lambda *_: None)

    def fail(output: Path) -> dict:
        output.mkdir()
        (output / "diagnostic.txt").write_text("failed", encoding="utf-8")
        raise ValueError("adapter failed")

    with pytest.raises(stage04.HybridStage04Error, match="adapter failed"):
        stage04.invoke_stage04(tmp_path, run, [], reconstruction.StageAdapter("visual_merge_bundle", fail))

    assert (tmp_path / "failures/04-visual-merge-bundle/diagnostic.txt").is_file()
    assert (tmp_path / "failures/04-visual-merge-bundle/stage-failure.json").is_file()
    assert not (tmp_path / "stages/04-visual-merge-bundle/stage.json").exists()


def test_stage04_records_a_failure_when_live_preflight_rejects_the_attempt(tmp_path, monkeypatch):
    run = _run(tmp_path)
    monkeypatch.setattr(stage04, "_validate_live_bindings", lambda *_: (_ for _ in ()).throw(stage04.HybridStage04Error("stale binding")))

    with pytest.raises(stage04.HybridStage04Error, match="stale binding"):
        stage04.invoke_stage04(tmp_path, run, [], reconstruction.StageAdapter("visual_merge_bundle", lambda _: {}))

    receipt = tmp_path / "failures/04-visual-merge-bundle/stage-failure.json"
    assert receipt.is_file()
    assert "stale binding" in receipt.read_text(encoding="utf-8")


def test_manifest_write_failure_quarantines_published_payload(tmp_path, monkeypatch):
    run = _run(tmp_path)
    monkeypatch.setattr(stage04, '_validate_live_bindings', lambda *_: None)
    monkeypatch.setattr(stage04, '_validate_output', lambda *_: None)
    monkeypatch.setattr(reconstruction, '_write_stage', lambda *_: (_ for _ in ()).throw(OSError('manifest write failed')))
    def build(output):
        output.mkdir()
        (output / 'payload.txt').write_text('fresh output')
        return {}
    with pytest.raises(stage04.HybridStage04Error, match='manifest write failed'):
        stage04.invoke_stage04(tmp_path, run, [], reconstruction.StageAdapter('visual_merge_bundle', build))
    assert (tmp_path / 'failures/04-visual-merge-bundle/payload.txt').read_text() == 'fresh output'
    assert not (tmp_path / 'outputs/04-visual-merge-bundle').exists()
