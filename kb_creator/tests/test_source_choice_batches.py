from __future__ import annotations

import json
from pathlib import Path

import pytest

from kb_creator.pipeline import source_choice_batches as batches
from kb_creator.pipeline import source_choice_translation as choices


def _write(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False), encoding="utf-8")
    return path


def _queue(tmp_path, monkeypatch):
    rows = []
    for number in range(3):
        raw = f"Heading {number}\nA phrase — with  spaces."
        alternatives = [{"alternative_id": f"{number}-{v}", "raw_text": text,
                         "reader_text": text.replace("  ", " "), "selectable": True,
                         "source_locator": {"view": v, "raw_index": number}}
                        for v, text in [("txt", raw), ("ocr", raw.replace("phrase", "paragraph"))]]
        rows.append({"issue_id": f"issue-{number}", "source_page": number + 1,
                     "provisional_alternative_id": f"{number}-txt", "alternatives": alternatives})
    path = _write(tmp_path / "queue.json", {"schema": choices.QUEUE_SCHEMA_V2,
                  "review_master": {"path": str(tmp_path / "master/MASTER_EN.md")},
                  "candidate": {"path": str(tmp_path / "mechanical")}, "choices": rows})
    # These tests isolate export/collection; the public queue validator remains
    # the production authority and is tested by the R1 integration fixture.
    calls = []
    monkeypatch.setattr(choices, "verify_queue_v2", lambda p: calls.append(p))
    return path, rows, calls


def _answers(path, queue, ids):
    return _write(path, {"schema": choices.SUBMISSION_SCHEMA_V2, "state": "submitted",
                         "queue": batches._identity(queue), "choices": [
                             {"issue_id": key, "disposition": "selected_alternative",
                              "alternative_id": key.replace("issue-", "") + "-txt",
                              "reason": "Checked source wording.", "label": None} for key in ids]})


def test_batches_cover_once_keep_evidence_and_reconstruct_exact_diffs(tmp_path, monkeypatch):
    queue, rows, calls = _queue(tmp_path, monkeypatch)
    original = queue.read_bytes()
    result = batches.prepare_batches(queue, tmp_path / "batches", max_choices=2)
    assert calls == [queue]
    assert (result["choices"], result["batches"]) == (3, 2)
    manifest = batches._read(Path(result["manifest"]))
    assert [i for group in manifest["batches"] for i in group["issue_ids"]] == [x["issue_id"] for x in rows]
    actual = []
    for group in manifest["batches"]:
        task = batches._read(Path(group["task"]["path"]))
        view = batches._read(Path(group["review"]["path"]))
        template = batches._read(Path(group["template"]["path"]))
        assert all(x["disposition"] is None and x["alternative_id"] is None for x in template["choices"])
        actual.extend(task["choices"])
        for full, compact in zip(task["choices"], view["choices"]):
            for alt, delta in zip(full["alternatives"], compact["alternatives"]):
                for field in ("raw", "reader"):
                    restored = compact[f"baseline_{field}_text"]
                    for change in reversed(delta[f"{field}_changes"]):
                        start, end = change["start"], change["end"]
                        assert restored[start:end] == change["before"]
                        restored = restored[:start] + change["after"] + restored[end:]
                    assert restored == alt[f"{field}_text"]
    assert actual == rows and queue.read_bytes() == original


def test_long_choice_not_truncated_and_old_output_not_overwritten(tmp_path, monkeypatch):
    queue, _, _ = _queue(tmp_path, monkeypatch)
    result = batches.prepare_batches(queue, tmp_path / "out", max_review_chars=1)
    assert result["batches"] == 3
    before = Path(result["manifest"]).read_bytes()
    with pytest.raises(choices.SourceChoiceError):
        batches.prepare_batches(queue, tmp_path / "out")
    assert Path(result["manifest"]).read_bytes() == before


def test_collected_answers_restore_queue_order_and_use_public_recorder(tmp_path, monkeypatch):
    queue, _, _ = _queue(tmp_path, monkeypatch)
    last = _answers(tmp_path / "last.json", queue, ["issue-2"])
    first = _answers(tmp_path / "first.json", queue, ["issue-1", "issue-0"])
    calls = []
    def record(q, submission, output):
        value = batches._read(submission)
        calls.append((q, value, output))
        return {"state": "verified"}
    monkeypatch.setattr(choices, "record_decisions_v2", record)
    assert batches.collect_submissions(queue, [last, first], tmp_path / "collected")["state"] == "verified"
    assert len(calls) == 1 and calls[0][0] == queue
    assert [x["issue_id"] for x in calls[0][1]["choices"]] == ["issue-0", "issue-1", "issue-2"]


@pytest.mark.parametrize("ids", [["issue-0"], ["issue-0", "issue-0", "issue-2"], ["issue-0", "issue-1", "unknown"]])
def test_collection_rejects_missing_duplicate_unknown_before_writing(tmp_path, monkeypatch, ids):
    queue, _, _ = _queue(tmp_path, monkeypatch)
    answers = _answers(tmp_path / "answers.json", queue, ids)
    with pytest.raises(choices.SourceChoiceError):
        batches.collect_submissions(queue, [answers], tmp_path / "out")
    assert not (tmp_path / "out").exists()


def test_collection_rejects_queue_drift(tmp_path, monkeypatch):
    queue, _, _ = _queue(tmp_path, monkeypatch)
    answers = _answers(tmp_path / "answers.json", queue, ["issue-0", "issue-1", "issue-2"])
    queue.write_text(queue.read_text(encoding="utf-8") + " ", encoding="utf-8")
    with pytest.raises(choices.SourceChoiceError, match="exact queue"):
        batches.collect_submissions(queue, [answers], tmp_path / "out")
    assert not (tmp_path / "out").exists()


def test_prepare_propagates_authority_failure_without_output(tmp_path, monkeypatch):
    queue, _, _ = _queue(tmp_path, monkeypatch)
    def fail(path):
        raise choices.SourceChoiceError("stale source")
    monkeypatch.setattr(choices, "verify_queue_v2", fail)
    with pytest.raises(choices.SourceChoiceError, match="stale source"):
        batches.prepare_batches(queue, tmp_path / "out")
    assert not (tmp_path / "out").exists()


@pytest.mark.parametrize("inside", ["master", "mechanical"])
def test_no_batch_files_written_under_source_authorities(tmp_path, monkeypatch, inside):
    queue, _, _ = _queue(tmp_path, monkeypatch)
    with pytest.raises(choices.SourceChoiceError, match="overlaps"):
        batches.prepare_batches(queue, tmp_path / inside / "out")
    assert not (tmp_path / inside).exists()
