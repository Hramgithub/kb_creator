"""Fail-closed tests for reviewed source-choice answer rebinding."""
from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest

from kb_creator.pipeline import source_choice_rebinding as subject
from kb_creator.pipeline import source_choice_translation as choices
from kb_creator.pipeline.identity import file_identity, sha256_bytes
from kb_creator.pipeline.identity import canonical_bytes


def _write(path: Path, value: object) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False), encoding="utf-8")
    return path


def _alternative(name: str, text: str, *, locator: int = 1) -> dict:
    return {"alternative_id": name, "raw_text": text, "raw_text_sha256": sha256_bytes(text.encode()),
            "reader_text": text, "reader_text_sha256": sha256_bytes(text.encode()),
            "source_locator": {"view": "txt", "raw_index": locator}, "selectable": True,
            "nonselectable_reason": None, "reader_adapter": {"policy": "identity_v1"},
            "evidence": [{"path": f"old/{name}.json", "bytes": 12, "sha256": "A" * 64}]}


def _choice(issue_id: str = "issue-1") -> dict:
    return {"issue_id": issue_id, "source_pdf_sha256": "B" * 64, "source_page": 4,
            "issue_kind": choices.PENDING_KIND, "source_selector": {"diagnostic": {"code": "x"}},
            "r0_source_preimage": {"source_excerpt_sha256": "C" * 64},
            "reader_anchor": {"kind": "source", "selected_source_key": {"view": "txt", "raw_index": 1}},
            "reader_projection": {"reader_text": "first", "reader_text_sha256": sha256_bytes(b"first")},
            "raw_reader_replay": {"base_policy": "display_text_v1", "presentation_policy": None,
                                  "anchor_alternative_id": "first", "selected_row_proof": {"source_locator": {"view": "txt", "raw_index": 1}}},
            "provisional_alternative_id": "first", "provisional_alternative_ids": ["first"],
            "alternatives": [_alternative("first", "first"), _alternative("second", "second", locator=2)]}


def _queue(path: Path, rows: list[dict]) -> Path:
    return _write(path, {"schema": choices.QUEUE_SCHEMA_V2, "choices": rows})


def _submission(path: Path, queue: Path, rows: list[dict]) -> Path:
    return _write(path, {"schema": choices.SUBMISSION_SCHEMA_V2, "state": "submitted",
                         "queue": {"path": str(queue.resolve()), **file_identity(queue)}, "choices": rows})


def _answer(issue_id: str = "issue-1") -> dict:
    return {"issue_id": issue_id, "disposition": "selected_alternative", "alternative_id": "second",
            "reason": "Reviewed exact reading.", "label": None}


@pytest.fixture
def queues(tmp_path, monkeypatch):
    old = _queue(tmp_path / "old.json", [_choice()])
    new_row = copy.deepcopy(_choice())
    proof_row = {"kind": "selected", "unit": {"view_id": "txt", "raw_index": 1,
                 "original_text_sha256": sha256_bytes(b"first")}, "markdown_span": [0, 5]}
    def bind(queue, audit_name):
        evidence_root = tmp_path / queue.stem / "final-evidence"; audit = _write(evidence_root / "review-draft-stage05-audit.json", {"pages": [{"source_page": 4, "ordered_proof_stream": [proof_row]}]})
        evidence = _write(evidence_root / "review-draft-evidence.json", {"authored": {"stage05_audit": {"path": audit.name, **file_identity(audit)}}})
        value = json.loads(queue.read_text(encoding="utf-8")); replay = value["choices"][0]["raw_reader_replay"]
        replay["stage05_audit"] = {"path": audit.name, **file_identity(audit)}
        replay["selected_row_proof"] = {"stream_index": 0, "source_locator": {"view": "txt", "raw_index": 1},
                                         "raw_text_sha256": sha256_bytes(b"first"), "row_sha256": sha256_bytes(canonical_bytes(proof_row))}
        value["final_evidence"] = {"path": str(evidence.resolve()), **file_identity(evidence)}
        _write(queue, value)
    bind(old, "old-audit.json")
    bind(_queue(tmp_path / "new.json", [new_row]), "new-audit.json")
    # The public validator is deliberately replaced only for compact synthetic queues.
    monkeypatch.setattr(choices, "verify_queue_v2", lambda path: {"state": "verified", "queue": str(path)})
    return old, tmp_path / "new.json"


def test_reuses_exact_reviewed_answer_when_only_evidence_path_relocates(tmp_path, queues):
    old, new = queues
    value = json.loads(new.read_text(encoding="utf-8")); value["choices"][0]["alternatives"][0]["evidence"][0]["path"] = "new/relocated.json"; _write(new, value)
    answer = _submission(tmp_path / "old-answer.json", old, [_answer()])
    result = subject.rebind_source_choice_submissions(old, new, [answer], tmp_path / "out")
    partial = json.loads(Path(result["submission"]).read_text(encoding="utf-8"))
    template = json.loads((tmp_path / "out" / "SOURCE_CHOICE_REBINDING_TEMPLATE.v2.json").read_text(encoding="utf-8"))
    audit = json.loads(Path(result["audit"]).read_text(encoding="utf-8"))
    assert result["accepted"] is False and partial["choices"] == [_answer()] and template["choices"] == []
    assert audit["rows"][0]["state"] == "reused" and audit["pending"] == 0


@pytest.mark.parametrize("change", ["raw", "reader", "projection", "alternative", "locator", "pdf", "adapter"])
def test_changed_semantic_source_or_reader_identity_stays_pending(tmp_path, queues, change):
    old, new = queues
    value = json.loads(new.read_text(encoding="utf-8")); row = value["choices"][0]
    if change == "raw": row["alternatives"][1]["raw_text"] = "changed"
    elif change == "reader": row["alternatives"][1]["reader_text"] = "changed"
    elif change == "projection": row["reader_projection"]["reader_text"] = "changed"
    elif change == "alternative": row["alternatives"].pop()
    elif change == "locator": row["alternatives"][1]["source_locator"]["raw_index"] = 9
    elif change == "pdf": row["source_pdf_sha256"] = "D" * 64
    else: row["alternatives"][1]["reader_adapter"] = {"policy": "changed"}
    _write(new, value)
    answer = _submission(tmp_path / "answer.json", old, [_answer()])
    result = subject.rebind_source_choice_submissions(old, new, [answer], tmp_path / "out")
    assert result["reused"] == 0 and result["pending"] == 1
    assert json.loads(Path(result["submission"]).read_text(encoding="utf-8"))["choices"] == []


def test_partial_and_absent_sets_remain_explicitly_pending(tmp_path, queues):
    old, new = queues
    old_value = json.loads(old.read_text(encoding="utf-8")); old_value["choices"].append(_choice("issue-2")); _write(old, old_value)
    new_value = json.loads(new.read_text(encoding="utf-8")); new_value["choices"].append(_choice("issue-2")); new_value["choices"].append(_choice("issue-3")); _write(new, new_value)
    answer = _submission(tmp_path / "answer.json", old, [_answer()])
    result = subject.rebind_source_choice_submissions(old, new, [answer], tmp_path / "out")
    audit = json.loads(Path(result["audit"]).read_text(encoding="utf-8"))
    assert [(row["issue_id"], row["state"], row["reason"]) for row in audit["rows"]] == [
        ("issue-1", "reused", "exact_semantic_identity"), ("issue-2", "pending", "absent_old_answer"),
        ("issue-3", "absent", "absent_old_issue")]
    template = json.loads((tmp_path / "out" / "SOURCE_CHOICE_REBINDING_TEMPLATE.v2.json").read_text(encoding="utf-8"))
    assert result["pending"] == 2
    assert [row["issue_id"] for row in template["choices"]] == ["issue-2", "issue-3"]


def test_rejects_duplicate_foreign_and_mutated_submissions_without_output(tmp_path, queues):
    old, new = queues
    answer = _submission(tmp_path / "answer.json", old, [_answer()])
    duplicate = _submission(tmp_path / "duplicate.json", old, [_answer()])
    with pytest.raises(subject.SourceChoiceRebindingError, match="duplicate"):
        subject.rebind_source_choice_submissions(old, new, [answer, duplicate], tmp_path / "duplicate-out")
    foreign = json.loads(answer.read_text(encoding="utf-8")); foreign["queue"]["sha256"] = "0" * 64; _write(answer, foreign)
    with pytest.raises(subject.SourceChoiceRebindingError, match="foreign"):
        subject.rebind_source_choice_submissions(old, new, [answer], tmp_path / "foreign-out")
    assert not (tmp_path / "duplicate-out").exists() and not (tmp_path / "foreign-out").exists()


def test_rechecks_input_identity_after_two_verifications_and_rejects_drift_without_writing(tmp_path, queues, monkeypatch):
    old, new = queues
    answer = _submission(tmp_path / "answer.json", old, [_answer()])
    calls = 0
    def verify(path):
        nonlocal calls
        calls += 1
        if calls == 2:
            new.write_text(new.read_text(encoding="utf-8") + " ", encoding="utf-8")
        return {"state": "verified"}
    monkeypatch.setattr(choices, "verify_queue_v2", verify)
    with pytest.raises(subject.SourceChoiceRebindingError, match="changed during verification"):
        subject.rebind_source_choice_submissions(old, new, [answer], tmp_path / "out")
    assert calls == 2 and not (tmp_path / "out").exists()


def test_rechecks_sealed_stage05_authority_identity_before_writing(tmp_path, queues, monkeypatch):
    old, new = queues; answer = _submission(tmp_path / "answer.json", old, [_answer()])
    original, changed = subject._same_rebound_proof, False
    def mutate_after_proof(*args):
        nonlocal changed
        result = original(*args)
        if not changed:
            audit = _audit_path(new); audit.write_text(audit.read_text(encoding="utf-8") + " ", encoding="utf-8"); changed = True
        return result
    monkeypatch.setattr(subject, "_same_rebound_proof", mutate_after_proof)
    with pytest.raises(subject.SourceChoiceRebindingError, match="input changed during verification"):
        subject.rebind_source_choice_submissions(old, new, [answer], tmp_path / "out")
    assert changed and not (tmp_path / "out").exists()


def test_rejects_existing_or_overlapping_output_and_preserves_inputs(tmp_path, queues):
    old, new = queues
    answer = _submission(tmp_path / "answer.json", old, [_answer()])
    before = {path: path.read_bytes() for path in (old, new, answer)}
    with pytest.raises(subject.SourceChoiceRebindingError):
        subject.rebind_source_choice_submissions(old, new, [answer], old.parent)
    assert before == {path: path.read_bytes() for path in before}


def test_replay_transport_can_move_but_normal_replay_authority_cannot(tmp_path, queues):
    old, new = queues
    value = json.loads(new.read_text(encoding="utf-8")); replay = value["choices"][0]["raw_reader_replay"]
    replay.update({"schema": "kb_creator.raw_reader_replay.v1", "anchor_source_locator": {"view": "txt", "raw_index": 1},
                   "anchor_raw_text_sha256": sha256_bytes(b"first"), "r0_reader_span": {"character_start": 20, "character_end": 25, "text_sha256": sha256_bytes(b"first"), "decision_markdown_sha256": "D" * 64},
                   "decision": {"path": "new/decision.json", "bytes": 4, "sha256": "E" * 64},
                   "stage05_audit": {"path": "new/stage05.json", "bytes": 5, "sha256": "F" * 64}})
    _write(new, value)
    old_value = json.loads(old.read_text(encoding="utf-8")); old_value["choices"][0]["raw_reader_replay"] = copy.deepcopy(replay); _write(old, old_value)
    # These verified transport fields may move without changing the source reading.
    value = json.loads(new.read_text(encoding="utf-8")); replay = value["choices"][0]["raw_reader_replay"]
    replay["decision"] = {"path": "other/decision.json", "bytes": 99, "sha256": "1" * 64}
    replay["stage05_audit"] = {"path": "other/stage05.json", "bytes": 88, "sha256": "2" * 64}
    replay["r0_reader_span"]["character_start"] = 1; replay["r0_reader_span"]["decision_markdown_sha256"] = "3" * 64
    replay["selected_row_proof"]["stream_index"] = 17; _write(new, value)
    answer = _submission(tmp_path / "answer.json", old, [_answer()])
    # N134 reopens the sealed Stage05 proof; a relocated record needs a valid
    # identity, so this unbound transport mutation is rejected.
    with pytest.raises(subject.SourceChoiceRebindingError, match="malformed"):
        subject.rebind_source_choice_submissions(old, new, [answer], tmp_path / "transport-out")
    # A selected source hash is semantic replay authority and must remain pending.
    value["choices"][0]["raw_reader_replay"]["anchor_raw_text_sha256"] = "4" * 64; _write(new, value)
    assert subject.rebind_source_choice_submissions(old, new, [answer], tmp_path / "semantic-out")["reused"] == 0


def test_composite_raw_source_slice_drift_stays_pending(tmp_path, queues):
    old, new = queues
    composite = {"schema": "kb_creator.raw_reader_replay.v2", "anchor_mode": "composite_source_slice_v1",
                 "base_policy": "identity_v1", "anchor_source_locator": {"view": "txt", "raw_index": 1},
                 "anchor_container_sha256": sha256_bytes(b"first"), "semantic_unit_id": "unit-1",
                 "semantic_unit_markdown_sha256": "A" * 64, "source_fragment": {"view": "txt", "raw_index": 1, "start": 0, "end": 5, "source_sha256": sha256_bytes(b"first")},
                 "raw_source_slice": {"start": 0, "end": 5, "raw_text_sha256": sha256_bytes(b"first")},
                 "r0_reader_span": {"character_start": 0, "character_end": 5, "text_sha256": sha256_bytes(b"first")},
                 "normalized_source_slice": [0, 5], "diagnostic_baseline_alternative_id": "first",
                 "decision": {"path": "old/decision.json", "bytes": 1, "sha256": "B" * 64},
                 "stage05_audit": {"path": "old/stage05.json", "bytes": 1, "sha256": "C" * 64},
                 "selected_row_proof": {"stream_index": 1, "source_locator": {"view": "txt", "raw_index": 1}, "raw_text_sha256": sha256_bytes(b"first"), "row_sha256": "D" * 64}}
    for path in (old, new):
        value = json.loads(path.read_text(encoding="utf-8")); value["choices"][0]["raw_reader_replay"] = copy.deepcopy(composite); _write(path, value)
    value = json.loads(new.read_text(encoding="utf-8")); value["choices"][0]["raw_reader_replay"]["raw_source_slice"]["start"] = 1; _write(new, value)
    answer = _submission(tmp_path / "answer.json", old, [_answer()])
    assert subject.rebind_source_choice_submissions(old, new, [answer], tmp_path / "out")["reused"] == 0


def test_rejects_output_inside_review_master_parent(tmp_path, queues):
    old, new = queues
    master = tmp_path / "master" / "MASTER_EN.md"; master.parent.mkdir(); master.write_text("source", encoding="utf-8")
    for path in (old, new):
        value = json.loads(path.read_text(encoding="utf-8")); value["review_master"] = {"path": str(master)}; _write(path, value)
    answer = _submission(tmp_path / "answer.json", old, [_answer()])
    with pytest.raises(choices.SourceChoiceError, match="overlaps"):
        subject.rebind_source_choice_submissions(old, new, [answer], master.parent / "rebind")
    assert not (master.parent / "rebind").exists()


def _refresh_audit_record(queue: Path) -> None:
    value = json.loads(queue.read_text(encoding="utf-8")); replay = value["choices"][0]["raw_reader_replay"]
    evidence = Path(value["final_evidence"]["path"]); audit = evidence.parent / replay["stage05_audit"]["path"]
    row = json.loads(audit.read_text(encoding="utf-8"))["pages"][0]["ordered_proof_stream"][0]
    replay["stage05_audit"] = {"path": audit.name, **file_identity(audit)}
    replay["selected_row_proof"]["row_sha256"] = sha256_bytes(canonical_bytes(row)); _write(queue, value)
    evidence_value = json.loads(evidence.read_text(encoding="utf-8")); evidence_value["authored"]["stage05_audit"] = replay["stage05_audit"]
    _write(evidence, evidence_value); value["final_evidence"] = {"path": str(evidence.resolve()), **file_identity(evidence)}; _write(queue, value)


def _audit_path(queue: Path) -> Path:
    value = json.loads(queue.read_text(encoding="utf-8")); replay = value["choices"][0]["raw_reader_replay"]
    return Path(value["final_evidence"]["path"]).parent / replay["stage05_audit"]["path"]


def test_stage05_audit_is_loaded_once_for_multiple_pages(tmp_path, queues, monkeypatch):
    old, _ = queues; value = json.loads(old.read_text(encoding="utf-8")); replay = value["choices"][0]["raw_reader_replay"]
    evidence = Path(value["final_evidence"]["path"]); audit = evidence.parent / replay["stage05_audit"]["path"]
    data = json.loads(audit.read_text(encoding="utf-8")); second = copy.deepcopy(data["pages"][0]["ordered_proof_stream"][0])
    second["unit"]["raw_index"] = 2; second["markdown_span"] = [10, 15]
    data["pages"].append({"source_page": 5, "ordered_proof_stream": [second]}); _write(audit, data)
    record = {"path": audit.name, **file_identity(audit)}; replay["stage05_audit"] = record
    evidence_value = json.loads(evidence.read_text(encoding="utf-8")); evidence_value["authored"]["stage05_audit"] = record; _write(evidence, evidence_value)
    value["final_evidence"] = {"path": str(evidence.resolve()), **file_identity(evidence)}; _write(old, value)
    second_replay = copy.deepcopy(replay); second_replay["selected_row_proof"] = {
        "stream_index": 0, "source_locator": {"view": "txt", "raw_index": 2},
        "raw_text_sha256": sha256_bytes(b"first"), "row_sha256": sha256_bytes(canonical_bytes(second)),
    }
    reads, original = [], subject._read
    def counted(path):
        if Path(path).resolve() == audit.resolve(): reads.append(path)
        return original(path)
    monkeypatch.setattr(subject, "_read", counted)
    authority = subject._stage05_authority(json.loads(old.read_text(encoding="utf-8"))); cache = {}
    subject._proof_row(replay, 4, authority, cache); subject._proof_row(second_replay, 5, authority, cache)
    assert len(reads) == 1


def test_sealed_proof_coordinate_only_drift_reuses(tmp_path, queues):
    old, new = queues; audit = _audit_path(new)
    data = json.loads(audit.read_text(encoding="utf-8")); data["pages"][0]["ordered_proof_stream"][0]["markdown_span"] = [19, 24]; _write(audit, data); _refresh_audit_record(new)
    answer = _submission(tmp_path / "answer.json", old, [_answer()])
    assert subject.rebind_source_choice_submissions(old, new, [answer], tmp_path / "out")["reused"] == 1


@pytest.mark.parametrize("field,mutate", [
    ("kind", lambda r: r.__setitem__("kind", "other")),
    ("raw", lambda r: r["unit"].__setitem__("original_text_sha256", "0" * 64)),
    ("unknown", lambda r: r.__setitem__("future_semantic", True)),
    ("malformedspan", lambda r: r.__setitem__("markdown_span", [5])),
])
def test_sealed_proof_semantic_row_drift_stays_pending(tmp_path, queues, field, mutate):
    old, new = queues; audit = _audit_path(new)
    data = json.loads(audit.read_text(encoding="utf-8")); mutate(data["pages"][0]["ordered_proof_stream"][0]); _write(audit, data); _refresh_audit_record(new)
    answer = _submission(tmp_path / "answer.json", old, [_answer()])
    if field in {"kind", "malformedspan"}:
        with pytest.raises(subject.SourceChoiceRebindingError, match="row differs"):
            subject.rebind_source_choice_submissions(old, new, [answer], tmp_path / "out")
    else:
        assert subject.rebind_source_choice_submissions(old, new, [answer], tmp_path / "out")["pending"] == 1


def test_sealed_proof_locator_or_audit_identity_drift_rejects(tmp_path, queues):
    old, new = queues; value = json.loads(new.read_text(encoding="utf-8")); value["choices"][0]["raw_reader_replay"]["selected_row_proof"]["stream_index"] = 1; _write(new, value)
    answer = _submission(tmp_path / "answer.json", old, [_answer()])
    with pytest.raises(subject.SourceChoiceRebindingError, match="locator"):
        subject.rebind_source_choice_submissions(old, new, [answer], tmp_path / "out")
