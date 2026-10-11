import json

import pytest

from kb_creator.pipeline import source_choice_coverage_successor as subject
from kb_creator.pipeline.identity import canonical_bytes, file_identity, sha256_bytes


def _sha(text):
    return sha256_bytes(text.encode())


def _fixture(tmp_path, monkeypatch):
    from pathlib import Path
    from kb_creator.tests.test_source_choice_composite_integration import _prepare_composite_queue, _submission
    from kb_creator.pipeline import source_choice_translation as choices
    from kb_creator.scripts.author_reviewed_semantic_decisions import _recompute_composer_coverage
    built, queue_path, row, alternative = _prepare_composite_queue(tmp_path, monkeypatch)
    result = choices.record_decisions_v2(queue_path,
        _submission(queue_path, row["issue_id"], alternative["alternative_id"], tmp_path / "submission.json"),
        tmp_path / "ledger")
    predecessor = built["r0_input"]
    claims = _recompute_composer_coverage(json.loads(predecessor.read_text(encoding="utf-8")),
                                         tmp_path, built["run"], built["draft_pages"])
    assert len(claims) == 1
    return predecessor, Path(result["ledger"]), claims[0]


def test_exact_composite_claim_gets_sealed_disposition_from_real_r0_authority(tmp_path, monkeypatch):
    predecessor, ledger, claim = _fixture(tmp_path, monkeypatch)
    value = subject.make_dispositions(predecessor_input=predecessor, ledger_path=ledger, claims=[claim])
    assert len(value["dispositions"]) == 1
    row = value["dispositions"][0]
    assert row["claim_id"] == claim["claim"]["claim_id"]
    assert row["r0_normalized_span"] == row["r1_normalized_span"] == [18, 21]
    assert row["r0_normalized_sha256"] == _sha("1D6")
    assert row["r1_normalized_sha256"] == _sha("ID6")
    assert subject.validate_dispositions(value, predecessor_input=predecessor, ledger_path=ledger,
                                         claims=[claim])[row["claim_id"]] == row


@pytest.mark.parametrize("attack", ["stale_predecessor", "anchor", "interval", "chosen", "missing", "duplicate", "cross_issue"])
def test_disposition_rejects_stale_or_substituted_authority(tmp_path, monkeypatch, attack):
    predecessor, ledger, claim = _fixture(tmp_path, monkeypatch)
    value = subject.make_dispositions(predecessor_input=predecessor, ledger_path=ledger, claims=[claim])
    if attack == "stale_predecessor":
        predecessor.write_text("changed", encoding="utf-8")
    elif attack == "missing":
        value["dispositions"] = []
    elif attack == "duplicate":
        value["dispositions"].append(dict(value["dispositions"][0]))
    elif attack == "cross_issue":
        value["dispositions"][0]["issue_id"] = "issue-2"
    elif attack == "anchor":
        value["dispositions"][0]["raw_reader_replay"]["anchor_container_sha256"] = _sha("other")
    elif attack == "interval":
        value["dispositions"][0]["r1_normalized_span"][1] = 22
    else:
        value["dispositions"][0]["chosen_raw_alternative"]["source_locator"]["raw_index"] = 9
    value["disposition_sha256"] = sha256_bytes(canonical_bytes({k: v for k, v in value.items() if k != "disposition_sha256"}))
    with pytest.raises(ValueError):
        subject.validate_dispositions(value, predecessor_input=predecessor, ledger_path=ledger, claims=[claim])


@pytest.mark.parametrize("attack", [None, "predecessor_input", "ledger", "queue"])
def test_author_requires_disposition_authorities_to_match_its_r1_input(tmp_path, monkeypatch, attack):
    from kb_creator.scripts.author_reviewed_semantic_decisions import _composer_coverage_successor_dispositions
    bindings, value = {}, {}
    names = {"predecessor_input": "source_choice_predecessor", "ledger": "source_choice_ledger", "queue": "source_choice_queue"}
    for field, name in names.items():
        path = tmp_path / f"{field}.json"
        path.write_text("{}", encoding="utf-8")
        record = file_identity(path)
        value[field] = {"path": str(path), **record}
        bindings[name] = {"path": path.name, **record}
    if attack:
        other = tmp_path / "unrelated-copy.json"
        other.write_text("{}", encoding="utf-8")
        bindings[names[attack]]["path"] = other.name
    disposition = tmp_path / "disposition.json"
    disposition.write_text(json.dumps(value), encoding="utf-8")
    bindings["source_choice_coverage_dispositions"] = {"path": disposition.name, **file_identity(disposition)}
    calls = []
    monkeypatch.setattr(subject, "validate_dispositions", lambda *args, **kwargs: calls.append(True) or {})
    if attack:
        with pytest.raises(ValueError, match="differs from successor"):
            _composer_coverage_successor_dispositions({"bindings": bindings}, tmp_path, [])
        assert calls == []
    else:
        assert _composer_coverage_successor_dispositions({"bindings": bindings}, tmp_path, []) == {}
        assert calls == [True]
