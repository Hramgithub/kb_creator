"""Public Stage05 invocation ownership, equality and full closing verification."""
from __future__ import annotations

from collections import Counter
import json
from pathlib import Path

import pytest

from kb_creator.pipeline import source_choice_successor as adapter
from kb_creator.pipeline import source_choice_translation as choices
from kb_creator.pipeline.identity import file_identity, sha256_bytes
from kb_creator.scripts import audit_mineru_ai_merge_fidelity as audit
from kb_creator.tests.test_audit_mineru_ai_merge_fidelity import (
    _v3_allowlist, _v3_geometry, v2_decision, v2_packet,
)


def _sha(text):
    return sha256_bytes(text.encode())


@pytest.fixture
def repeated_choices(tmp_path, monkeypatch):
    """Four pages, four corrections/page, two shared ledger authorities."""
    master = tmp_path / "MASTER_EN.md"
    master.write_text("valid", encoding="utf-8")
    packets, decisions, paths = {}, {}, []
    ledgers = [{"source_choices": [], "ledger_sha256": name} for name in ("a", "b")]
    queues = [{"choices": []}, {"choices": []}]
    for page in range(1, 5):
        texts = [f"Page {page} stable block {index}" for index in range(4)]
        packets[page] = v2_packet(texts, page=page)
        decision = v2_decision("\n\n".join(texts), [("original_pipeline_txt", i) for i in range(4)], page=page)
        decisions[page] = decision
        corrections = decision["linguistic_source_choice_corrections"] = []
        for index, text in enumerate(texts):
            issue, alt = f"p{page}-i{index}", f"alt-{page}-{index}"
            locator = {"view": "original_pipeline_txt", "raw_index": index, "field": "text"}
            anchor = {"selected_source_key": {"view": locator["view"], "raw_index": index}}
            span = {"start": 0, "text_sha256": _sha(text)}
            queues[index % 2]["choices"].append({
                "issue_id": issue, "source_page": page, "reader_projection": {"reader_text": text},
                "alternatives": [{"alternative_id": alt, "source_locator": locator,
                                  "raw_text": text, "raw_text_sha256": _sha(text)}],
            })
            ledgers[index % 2]["source_choices"].append({
                "issue_id": issue, "alternative_id": alt, "disposition": "selected_alternative",
                "reader_anchor": anchor, "r0_reader_span": span,
                "chosen_raw_alternative": {"text_sha256": _sha(text), "source_locator": locator},
                "intended_reader_successor": {"text": text, "text_sha256": _sha(text)},
                "raw_reader_replay": {"anchor_source_locator": locator, "r0_preimage_sha256": _sha(text)},
            })
            corrections.append({"authority": adapter.AUTHORITY, "issue_id": issue, "alternative_id": alt,
                "view": locator["view"], "raw_index": index, "raw_text_sha256": _sha(text),
                "selected_raw_text_sha256": _sha(text), "page_reader_span": span, "reader_anchor": anchor,
                "reader_preimage": text, "reader_replacement": text})
    for index, name in enumerate(("a", "b")):
        root = tmp_path / name
        root.mkdir()
        queue = root / "SOURCE_CHOICE_QUEUE.v2.json"
        queue.write_text(json.dumps(queues[index]), encoding="utf-8")
        (root / "SOURCE_CHOICE_SUBMISSION.v2.json").write_text("{}", encoding="utf-8")
        ledger = root / "SOURCE_CHOICE_LEDGER.v2.json"
        ledgers[index]["queue"] = {"path": str(queue.resolve()), **file_identity(queue)}
        ledger.write_text(json.dumps(ledgers[index]), encoding="utf-8")
        paths.append(ledger.resolve())
    for decision in decisions.values():
        for index, row in enumerate(decision["linguistic_source_choice_corrections"]):
            row["ledger"] = {"path": str(paths[index % 2]), **file_identity(paths[index % 2])}
    calls = []

    def verify(path):
        path = Path(path).resolve()
        calls.append(path)
        if master.read_text(encoding="utf-8") != "valid":
            raise choices.SourceChoiceError("bound master drift")
        value = json.loads(path.read_text(encoding="utf-8"))
        return {"ledger": str(path), "submission": str(path.parent / "SOURCE_CHOICE_SUBMISSION.v2.json"),
                "queue": value["queue"]["path"], "ledger_sha256": value["ledger_sha256"],
                "choices": len(value["source_choices"])}

    monkeypatch.setattr(choices, "verify_ledger_v2", verify)
    monkeypatch.setattr(adapter, "verify_ledger_v2", verify)
    geometry = {"observed_geometry": [row for page in packets for row in _v3_geometry(page)["observed_geometry"]]}
    return {"args": (packets, decisions), "kwargs": {"allowlist": _v3_allowlist(), "geometry": geometry,
            "visual_inventory": {}}, "calls": calls, "paths": paths, "master": master}


def _old_public(case):
    # The former public wrapper used these same consumers without contexts.
    with choices._author_ledger_snapshot_scope(None), adapter.ledger_validation_scope():
        return audit._audit_v3_content(*case["args"], **case["kwargs"], _structural_context=None)


def _run(case):
    return audit.audit_v3_content(*case["args"], **case["kwargs"])


def test_repeated_pages_two_ledgers_exact_old_result_and_counts(repeated_choices, monkeypatch):
    case = repeated_choices
    expected = _old_public(case)
    assert expected["passed"], expected["errors"]
    # 16 per correction, 8 per page/ledger, and 2 adapter-scope opens.
    assert Counter(case["calls"]) == Counter({path: 13 for path in case["paths"]})
    case["calls"].clear()
    opened, closed = [], []
    real_open, real_close = choices.open_verified_ledger_v2_snapshot, choices.reverify_ledger_v2_snapshot

    def traced_open(path):
        opened.append(Path(path).resolve())
        return real_open(path)

    def traced_close(snapshot):
        closed.append(snapshot.ledger_path)
        return real_close(snapshot)

    monkeypatch.setattr(choices, "open_verified_ledger_v2_snapshot", traced_open)
    monkeypatch.setattr(choices, "reverify_ledger_v2_snapshot", traced_close)
    actual = _run(case)
    assert actual == expected
    assert json.dumps(actual) == json.dumps(expected)  # Exact order and serializable values.
    assert opened == closed == case["paths"]
    assert case["calls"] == case["paths"] * 2


@pytest.mark.parametrize("filename", ["SOURCE_CHOICE_LEDGER.v2.json", "SOURCE_CHOICE_SUBMISSION.v2.json",
                                       "SOURCE_CHOICE_QUEUE.v2.json", "MASTER_EN.md"])
def test_closing_check_rejects_mutation(repeated_choices, monkeypatch, filename):
    case = repeated_choices
    real_audit = audit._audit_v3_content

    def mutate(*args, **kwargs):
        result = real_audit(*args, **kwargs)
        path = case["master"] if filename == "MASTER_EN.md" else case["paths"][0].parent / filename
        path.write_bytes(path.read_bytes() + b" ")
        return result

    monkeypatch.setattr(audit, "_audit_v3_content", mutate)
    with pytest.raises(choices.SourceChoiceError, match="changed since snapshot|bound master drift"):
        _run(case)
    assert case["calls"] == case["paths"] + [case["paths"][0]]
    assert choices._current_author_ledger_snapshot(case["paths"][0]) is None
    assert adapter._LEDGER_SCOPE.get() is None


@pytest.mark.parametrize("field", ["ledger", "issue_id", "alternative_id", "page_reader_span", "reader_anchor",
                                   "selected_raw_text_sha256", "reader_preimage", "reader_replacement", "raw_text_sha256"])
def test_conflicting_row_identity_still_fails(repeated_choices, field):
    case = repeated_choices
    row = case["args"][1][1]["linguistic_source_choice_corrections"][0]
    if field == "ledger":
        row[field] = {**row[field], "sha256": "0" * 64}
    elif field in {"page_reader_span", "reader_anchor"}:
        row[field] = {}
    else:
        row[field] = "wrong"
    with pytest.raises(ValueError):
        _run(case)


def test_foreign_owner_closed_context_and_sequential_freshness(repeated_choices, monkeypatch):
    case = repeated_choices
    captured = []
    real_audit = audit._audit_v3_content

    def capture(*args, **kwargs):
        contexts, owner = kwargs["_ledger_contexts"], kwargs["_ledger_owner"]
        captured.append((contexts, owner))
        with pytest.raises(ValueError, match="another or closed public audit"):
            contexts.snapshot_v2(object(), case["paths"][0])
        return real_audit(*args, **kwargs)

    monkeypatch.setattr(audit, "_audit_v3_content", capture)
    result = _run(case)
    assert _run(case) == result
    assert captured[0][0] is not captured[1][0]
    assert case["calls"] == case["paths"] * 4
    for contexts, owner in captured:
        with pytest.raises(ValueError, match="closed public audit"):
            contexts.audit_values_v2(owner, case["paths"][0])
    case["master"].write_text("drift")
    with pytest.raises(ValueError, match="bound master drift"):
        _run(case)


@pytest.mark.parametrize("inner_fails", [False, True])
def test_nested_and_error_scopes_restore_outer_and_ignore_author(repeated_choices, monkeypatch, inner_fails):
    case = repeated_choices
    real_audit = audit._audit_v3_content
    captured, depth = [], []

    def nested(*args, **kwargs):
        contexts, owner = kwargs["_ledger_contexts"], kwargs["_ledger_owner"]
        captured.append((contexts, owner))
        snapshot = choices._current_author_ledger_snapshot(case["paths"][0])
        assert snapshot is contexts.snapshot_v2(owner, case["paths"][0])
        if depth:
            assert contexts is not captured[0][0]
            if inner_fails:
                raise RuntimeError("inner failure")
            return real_audit(*args, **kwargs)
        depth.append(True)
        try:
            if inner_fails:
                with pytest.raises(RuntimeError, match="inner failure"):
                    _run(case)
            else:
                assert _run(case)["passed"]
        finally:
            depth.pop()
        assert choices._current_author_ledger_snapshot(case["paths"][0]) is snapshot
        return real_audit(*args, **kwargs)

    monkeypatch.setattr(audit, "_audit_v3_content", nested)
    caller_marker = object()
    with choices._author_ledger_snapshot_scope(lambda path: caller_marker), adapter.ledger_validation_scope():
        caller_scope = adapter._LEDGER_SCOPE.get()
        assert _run(case)["passed"]
        assert choices._current_author_ledger_snapshot(case["paths"][0]) is caller_marker
        assert adapter._LEDGER_SCOPE.get() is caller_scope
    assert Counter(case["calls"]) == Counter({case["paths"][0]: 3 if inner_fails else 4,
                                             case["paths"][1]: 2 if inner_fails else 4})
    for contexts, owner in captured:
        with pytest.raises(ValueError, match="closed public audit"):
            contexts.snapshot_v2(owner, case["paths"][0])


def test_outer_error_restores_caller_and_discards_snapshots(repeated_choices, monkeypatch):
    case = repeated_choices
    saved = []

    def fail(*args, **kwargs):
        contexts, owner = kwargs["_ledger_contexts"], kwargs["_ledger_owner"]
        saved.append((contexts, owner))
        contexts.snapshot_v2(owner, case["paths"][0])
        raise RuntimeError("original failure")

    monkeypatch.setattr(audit, "_audit_v3_content", fail)
    marker = object()
    with choices._author_ledger_snapshot_scope(lambda path: marker):
        with pytest.raises(RuntimeError, match="original failure"):
            _run(case)
        assert choices._current_author_ledger_snapshot(case["paths"][0]) is marker
    assert case["calls"] == [case["paths"][0]]
    assert saved[0][0]._snapshots == {}


@pytest.mark.parametrize("dependency", ["MASTER_EN.md", "MANIFEST.json"])
def test_real_closing_verifier_reopens_bound_master_dependencies(tmp_path, monkeypatch, dependency):
    """Mutate a real compact R0 binding after the public R1 audit completes."""
    from kb_creator.tests import test_source_choice_v2_integration as integration

    real_close = audit._PublicAuditLedgerContexts.reverify_before_return
    mutated = []

    def drift_at_close(contexts, owner):
        if contexts._snapshots and not mutated:
            snapshot = next(iter(contexts._snapshots.values()))
            master = Path(snapshot.queue_value["review_master"]["path"])
            path = master.parent / dependency
            path.write_bytes(path.read_bytes() + b"\n")
            mutated.append(path)
        return real_close(contexts, owner)

    monkeypatch.setattr(audit._PublicAuditLedgerContexts, "reverify_before_return", drift_at_close)
    with pytest.raises(ValueError, match="drift|differs|mismatch|changed"):
        integration.test_real_v2_r1_chain_reaches_verified_master_and_language_readiness(
            tmp_path, monkeypatch, "provisional", False)
    assert len(mutated) == 1
    assert mutated[0].name == dependency
    assert choices._current_author_ledger_snapshot(mutated[0]) is None
    assert adapter._LEDGER_SCOPE.get() is None
