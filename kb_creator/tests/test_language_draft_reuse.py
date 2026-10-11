from __future__ import annotations

import json
from pathlib import Path

import pytest

from kb_creator.pipeline import five_step_language as language
from kb_creator.pipeline import language_continuation as continuation
from kb_creator.pipeline.identity import deterministic_inventory
from kb_creator.pipeline.language_draft_reuse import prepare_reused_draft
from kb_creator.tests.test_language_continuation import predecessor, _draft, _read, _write


@pytest.fixture
def reuse_inputs(predecessor, tmp_path):
    run, glossary = predecessor
    prepared = continuation.prepare_continuation(run, glossary, tmp_path / "old-input")
    drafted = continuation.submit_continuation(tmp_path / "old-input", _draft(prepared, tmp_path / "draft.json"), tmp_path / "old-draft")
    proof = _read(Path(drafted["template_path"]))
    for row in proof["units"]:
        row["disposition"] = "checked_unchanged"
    _write(tmp_path / "proof.json", proof)
    continuation.submit_continuation(tmp_path / "old-draft", tmp_path / "proof.json", tmp_path / "old-final")
    continuation.prepare_continuation(run, glossary, tmp_path / "new-input")
    return tmp_path / "old-final/result", tmp_path / "new-input"


def test_reuse_preserves_text_but_requires_new_review(reuse_inputs, tmp_path):
    prior, target = reuse_inputs
    before = deterministic_inventory(prior)
    result = prepare_reused_draft(prior, target, tmp_path / "reuse")
    assert result["review_transferred"] is False
    assert result["new_proofread_required"] is True
    drafted = continuation.submit_continuation(target, tmp_path / "reuse/draft.submission.json", tmp_path / "new-draft")
    template = _read(Path(drafted["template_path"]))
    assert all(row["disposition"] == "pending" for row in template["units"])
    old = _read(prior / "evidence/proofread.submission.json")
    assert [row["final_ru_text"] for row in template["units"]] == [row["final_ru_text"] for row in old["units"]]
    assert deterministic_inventory(prior) == before
    with pytest.raises(ValueError, match="pending"):
        continuation.submit_continuation(tmp_path / "new-draft", Path(drafted["template_path"]), tmp_path / "bad-final")


def test_v3_reuse_rederives_verified_heading_context(reuse_inputs, tmp_path):
    prior, target = reuse_inputs
    task_path = Path(continuation.verify_continuation(target)["task_path"])
    task = _read(task_path)
    assert task["schema"] == "kb_creator.five_step_language_draft_task.v3"
    assert language._verified_unit_context(task, language._source(task, "master_en"))
    result = prepare_reused_draft(prior, target, tmp_path / "reuse")
    assert result["state"] == "draft_ready_for_submission"


def test_v3_reuse_rejects_tampered_unit_context(reuse_inputs, tmp_path, monkeypatch):
    prior, target = reuse_inputs
    verified = continuation.verify_continuation(target)
    task_path = Path(verified["task_path"])
    task = _read(task_path)
    task["source_unit_context"] = []
    task = language._seal(task["schema"], {key: value for key, value in task.items() if key not in {"schema", "task_sha256"}}, "task_sha256")
    _write(task_path, task)
    monkeypatch.setattr(continuation, "verify_continuation", lambda _: verified)
    with pytest.raises(language.FiveStepLanguageError, match="context"):
        prepare_reused_draft(prior, target, tmp_path / "reuse")


@pytest.mark.parametrize("name", ["MASTER_RU.md", "evidence/proofread.submission.json", "evidence/MASTER_EN.md"])
def test_rejects_changed_predecessor(reuse_inputs, tmp_path, name):
    prior, target = reuse_inputs
    (prior / name).write_text("tampered", encoding="utf-8")
    with pytest.raises(ValueError):
        prepare_reused_draft(prior, target, tmp_path / "reuse")
    assert not (tmp_path / "reuse").exists()


@pytest.mark.parametrize("field", ["units", "master_en", "source_spans"])
def test_rejects_semantically_different_source_even_when_task_verified(reuse_inputs, tmp_path, monkeypatch, field):
    prior, target = reuse_inputs
    # Isolate the reuse boundary: a separately valid new task may have changed source.
    verified = continuation.verify_continuation(target)
    task_path = Path(verified["task_path"])
    task = _read(task_path)
    if field == "units":
        task[field][0]["part_index"] = 99
    else:
        task[field]["sha256"] = "A" * 64
    _write(task_path, task)
    monkeypatch.setattr(continuation, "verify_continuation", lambda _: verified)
    with pytest.raises(ValueError, match="requires"):
        prepare_reused_draft(prior, target, tmp_path / "reuse")


def test_new_glossary_is_enforced(reuse_inputs, tmp_path):
    prior, target = reuse_inputs
    state = continuation.verify_continuation(target)
    run = Path(state["inputs"]["run_state"]["path"]).parent
    glossary = tmp_path / "glossaries/new.json"
    _write(glossary, {"terms": [{"source": "Page", "target": "Страница", "bad": ["Page"]}]})
    continuation.prepare_continuation(run, glossary, tmp_path / "changed-glossary")
    with pytest.raises(ValueError, match="mechanical QA"):
        prepare_reused_draft(prior, tmp_path / "changed-glossary", tmp_path / "reuse")


def test_cannot_overwrite_or_nest_output(reuse_inputs, tmp_path):
    prior, target = reuse_inputs
    for output in (prior, prior / "reuse", target / "reuse", tmp_path):
        with pytest.raises(ValueError, match="outside"):
            prepare_reused_draft(prior, target, output)
