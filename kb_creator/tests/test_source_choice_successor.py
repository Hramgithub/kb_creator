from __future__ import annotations

import json
from pathlib import Path

import pytest

from kb_creator.pipeline.identity import file_identity, sha256_bytes
from kb_creator.pipeline import source_choice_successor as successor


def _authority(tmp_path: Path, monkeypatch, **change):
    ledger_path, queue_path = tmp_path / "SOURCE_CHOICE_LEDGER.v1.json", tmp_path / "SOURCE_CHOICE_QUEUE.v1.json"
    before, after = "R0 reading", "R1 reading"
    queue = {"choices": [{"issue_id": "choice-001", "source_page": 1, "alternatives": [
        {"alternative_id": "alt-r1", "text": after},
    ]}]}
    ledger = {"queue": {"path": str(queue_path.resolve())}, "source_choices": [{
        "issue_id": "choice-001", "alternative_id": "alt-r1",
        "predecessor_span": {"text_sha256": sha256_bytes(before.encode())},
        "intended_successor_replacement": {"text_sha256": sha256_bytes(after.encode())},
    }]}
    queue_path.write_text(json.dumps(queue), encoding="utf-8")
    ledger_path.write_text(json.dumps(ledger), encoding="utf-8")
    monkeypatch.setattr(successor, "verify_ledger", lambda path: {"state": "verified"})
    row = {"authority": successor.AUTHORITY, "ledger": {"path": str(ledger_path.resolve()), **file_identity(ledger_path)},
           "issue_id": "choice-001", "alternative_id": "alt-r1", "view": "original_pipeline_txt", "raw_index": 1,
           "before": before, "after": after, "original_text_sha256": sha256_bytes(before.encode())}
    row.update(change)
    return row


def test_linguistic_choice_requires_exact_sealed_ledger_binding(tmp_path, monkeypatch):
    row = _authority(tmp_path, monkeypatch)
    result = successor.linguistic_choice_corrections(
        {"linguistic_source_choice_corrections": [row]},
        {("original_pipeline_txt", 1): {"text": "R0 reading"}},
        {("original_pipeline_txt", 1)}, 1,
    )
    assert result == {("original_pipeline_txt", 1): [("R0 reading", "R1 reading")]}


@pytest.mark.parametrize("change", [
    {"authority": "visual_reviewed_correction"},
    {"after": "free text"},
    {"alternative_id": "invented"},
    {"issue_id": "missing"},
])
def test_linguistic_choice_rejects_forged_or_free_text(tmp_path, monkeypatch, change):
    row = _authority(tmp_path, monkeypatch, **change)
    with pytest.raises(successor.SourceChoiceSuccessorError):
        successor.linguistic_choice_corrections(
            {"linguistic_source_choice_corrections": [row]},
            {("original_pipeline_txt", 1): {"text": "R0 reading"}},
            {("original_pipeline_txt", 1)}, 1,
        )


def test_linguistic_choice_rechecks_ledger_each_public_call(tmp_path, monkeypatch):
    row = _authority(tmp_path, monkeypatch)
    calls = []
    monkeypatch.setattr(successor, "verify_ledger", lambda path: calls.append(Path(path)) or {"state": "verified"})
    for _ in range(2):
        successor.linguistic_choice_corrections({"linguistic_source_choice_corrections": [row]},
            {("original_pipeline_txt", 1): {"text": "R0 reading"}}, {("original_pipeline_txt", 1)}, 1)
    assert len(calls) == 2
