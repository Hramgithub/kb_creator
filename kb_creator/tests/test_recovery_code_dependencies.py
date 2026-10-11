"""Recovery implementation changes invalidate a recorded execution checkpoint."""
from pathlib import Path

import pytest

from kb_creator.pipeline import five_step, reconstruction
from kb_creator.tests.test_five_step_runner import adapters


MODULES = ("mineru_view_recovery.py", "mineru_view_recovery_plan.py")
REAL_CODES = five_step._codes


@pytest.mark.parametrize("name", MODULES)
def test_recovery_module_is_recorded_and_drift_stops_resume(tmp_path, adapters, monkeypatch, name):
    monkeypatch.setattr(five_step, "_codes", REAL_CODES)
    relative = f"kb_creator/pipeline/{name}"
    root = Path(reconstruction.__file__).resolve().parents[2]
    assert root / relative in reconstruction._implementation_paths()
    assert relative in {row["path"] for row in five_step._codes(1)}
    source = tmp_path / "source.pdf"
    source.write_bytes(b"fixture")
    glossary = tmp_path / "terms.json"
    glossary.write_text('{"terms": []}', encoding="utf-8")
    run = tmp_path / "run"
    assert five_step.start(source, glossary, run)["state"] == "needs_agent_work"
    calls_before = list(adapters)
    original = five_step.file_identity

    def changed_identity(path):
        result = original(path)
        if Path(path).resolve() == (root / relative).resolve():
            result = {**result, "sha256": "0" * 64}
        return result

    monkeypatch.setattr(five_step, "file_identity", changed_identity)
    with pytest.raises(five_step.FiveStepError, match="implementation changed"):
        five_step.resume(run, submission=glossary)
    assert adapters == calls_before


@pytest.mark.parametrize("relative", [
    "kb_creator/scripts/author_reviewed_semantic_decisions.py",
    "kb_creator/pipeline/reviewed_line_group.py",
    "kb_creator/pipeline/reviewed_correction_text.py",
    "kb_creator/pipeline/reviewed_prose_binding.py",
])
def test_reviewed_author_dependency_drift_stops_before_resume(tmp_path, adapters, monkeypatch, relative):
    monkeypatch.setattr(five_step, "_codes", REAL_CODES)
    assert relative in {row["path"] for row in five_step._codes(1)}
    source = tmp_path / "source.pdf"
    source.write_bytes(b"fixture")
    glossary = tmp_path / "terms.json"
    glossary.write_text('{"terms": []}', encoding="utf-8")
    run = tmp_path / "run"
    assert five_step.start(source, glossary, run)["state"] == "needs_agent_work"
    calls_before = list(adapters)
    original = five_step.file_identity

    def changed_identity(path):
        result = original(path)
        if Path(path).resolve() == (five_step.ROOT / relative).resolve():
            return {**result, "sha256": "0" * 64}
        return result

    monkeypatch.setattr(five_step, "file_identity", changed_identity)
    with pytest.raises(five_step.FiveStepError, match="implementation changed"):
        five_step.resume(run, submission=glossary)
    assert adapters == calls_before


def test_visible_correction_is_in_downstream_and_promotion_inventories():
    from kb_creator.pipeline import reconstruction_promotion, reconstruction_replay_resume

    relative = "kb_creator/pipeline/reviewed_correction_text.py"
    assert relative in reconstruction_replay_resume.DOWNSTREAM_IMPLEMENTATION
    assert relative in {row["path"] for row in reconstruction_promotion._implementation()["files"]}
    for step in range(1, 6):
        assert relative in {row["path"] for row in REAL_CODES(step)}


def test_reviewed_prose_binding_is_in_downstream_and_promotion_inventories():
    from kb_creator.pipeline import reconstruction_promotion, reconstruction_replay_resume

    relative = "kb_creator/pipeline/reviewed_prose_binding.py"
    assert relative in reconstruction_replay_resume.DOWNSTREAM_IMPLEMENTATION
    assert relative in {row["path"] for row in reconstruction_promotion._implementation()["files"]}
    for step in range(1, 6):
        assert relative in {row["path"] for row in REAL_CODES(step)}
