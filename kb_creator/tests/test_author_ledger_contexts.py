"""Focused invocation and immutable-snapshot checks for V2 author selectors."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from kb_creator.pipeline import source_choice_translation as choices
from kb_creator.pipeline.identity import file_identity
from kb_creator.scripts import author_reviewed_semantic_decisions as author
from kb_creator.tests.test_review_draft_structural_successor import structural_route


def _ledger(tmp_path: Path, name: str, issue: str) -> Path:
    root = tmp_path / name
    root.mkdir()
    queue = root / "SOURCE_CHOICE_QUEUE.v2.json"
    queue.write_text(json.dumps({"choices": [{"issue_id": issue, "reader_projection": {"reader_text": "before"}}]}), encoding="utf-8")
    submission = root / "SOURCE_CHOICE_SUBMISSION.v2.json"
    submission.write_text("{}", encoding="utf-8")
    ledger = root / "SOURCE_CHOICE_LEDGER.v2.json"
    ledger.write_text(json.dumps({
        "ledger_sha256": name,
        "queue": {"path": str(queue.resolve()), **file_identity(queue)},
        "source_choices": [{"issue_id": issue, "alternative_id": "alt", "reader_anchor": {
            "selected_source_key": {"view": "v", "raw_index": 1}}, "r0_reader_span": {"start": 0},
            "intended_reader_successor": {"text": "after"},
            "chosen_raw_alternative": {"text_sha256": "ABC"}}],
    }), encoding="utf-8")
    return ledger


def _fake_verifier(monkeypatch: pytest.MonkeyPatch, *, deep_authority: Path | None = None) -> list[Path]:
    calls: list[Path] = []

    def verify(path: Path) -> dict:
        path = Path(path).resolve()
        calls.append(path)
        if deep_authority is not None and deep_authority.read_text() != "valid":
            raise choices.SourceChoiceError("deep authority drift")
        value = json.loads(path.read_text(encoding="utf-8"))
        return {"ledger": str(path), "submission": str(path.parent / "SOURCE_CHOICE_SUBMISSION.v2.json"),
                "queue": value["queue"]["path"], "ledger_sha256": value["ledger_sha256"],
                "choices": len(value["source_choices"])}

    monkeypatch.setattr(choices, "verify_ledger_v2", verify)
    return calls


def _select(ledger: Path, issue: str, contexts: author._AuthorLedgerContexts, owner: object) -> dict:
    decision = {"selected_blocks": [{"view": "v", "raw_index": 1, "purpose": "text"}]}
    packet = {"views": {"v": {"blocks": [{"raw_index": 1, "text": "source"}]}}}
    selector = {"ledger": str(ledger), "issue_id": issue, "alternative_id": "alt", "view": "v", "raw_index": 1}
    author._materialize_linguistic_source_choice_corrections(decision, packet, [selector], 1, contexts, owner)
    return decision


def test_many_selectors_have_two_checks_and_unchanged_json(tmp_path, monkeypatch):
    ledger = _ledger(tmp_path, "a", "issue-a")
    calls = _fake_verifier(monkeypatch)
    owner = object()
    contexts = author._AuthorLedgerContexts(owner)
    first = _select(ledger, "issue-a", contexts, owner)
    for _ in range(24):
        assert _select(ledger, "issue-a", contexts, owner) == first
    contexts.reverify_before_publish(owner)
    assert calls == [ledger.resolve(), ledger.resolve()]
    assert first["linguistic_source_choice_corrections"] == [{
        "authority": "linguistic_source_choice", "ledger": {"path": str(ledger.resolve()), **file_identity(ledger)},
        "issue_id": "issue-a", "alternative_id": "alt", "view": "v", "raw_index": 1,
        "raw_text_sha256": author.digest(b"source"), "page_reader_span": {"start": 0},
        "reader_anchor": {"selected_source_key": {"view": "v", "raw_index": 1}},
        "reader_preimage": "before", "reader_replacement": "after", "selected_raw_text_sha256": "ABC",
    }]
    json.dumps(first)


def test_two_ledgers_and_owner_isolation(tmp_path, monkeypatch):
    a = _ledger(tmp_path, "a", "issue-a")
    b = _ledger(tmp_path, "b", "issue-b")
    calls = _fake_verifier(monkeypatch)
    owner = object()
    contexts = author._AuthorLedgerContexts(owner)
    _select(a, "issue-a", contexts, owner)
    _select(b, "issue-b", contexts, owner)
    with pytest.raises(ValueError, match="differs from ledger"):
        _select(b, "issue-a", contexts, owner)
    with pytest.raises(ValueError, match="another author invocation"):
        contexts.lookup_v2(object(), a, "issue-a")
    contexts.reverify_before_publish(owner)
    assert calls == [a.resolve(), b.resolve(), a.resolve(), b.resolve()]
    fresh = author._AuthorLedgerContexts(object())
    assert fresh._snapshots == {}


@pytest.mark.parametrize("filename", ["SOURCE_CHOICE_LEDGER.v2.json", "SOURCE_CHOICE_SUBMISSION.v2.json", "SOURCE_CHOICE_QUEUE.v2.json"])
def test_direct_drift_fails_prepublish(tmp_path, monkeypatch, filename):
    ledger = _ledger(tmp_path, "a", "issue-a")
    _fake_verifier(monkeypatch)
    owner = object()
    contexts = author._AuthorLedgerContexts(owner)
    _select(ledger, "issue-a", contexts, owner)
    with (ledger.parent / filename).open("ab") as stream:
        stream.write(b" ")
    with pytest.raises(choices.SourceChoiceError, match="changed since snapshot"):
        contexts.reverify_before_publish(owner)


def test_deep_drift_fails_and_snapshot_is_read_only(tmp_path, monkeypatch):
    ledger = _ledger(tmp_path, "a", "issue-a")
    deep = tmp_path / "deep-authority"
    deep.write_text("valid")
    calls = _fake_verifier(monkeypatch, deep_authority=deep)
    snapshot = choices.open_verified_ledger_v2_snapshot(ledger)
    with pytest.raises(TypeError):
        snapshot.ledger_by_issue["issue-a"]["reader_anchor"]["selected_source_key"]["view"] = "tampered"
    deep.write_text("changed")
    with pytest.raises(choices.SourceChoiceError, match="deep authority drift"):
        choices.reverify_ledger_v2_snapshot(snapshot)
    assert calls == [ledger.resolve(), ledger.resolve()]


def test_author_prepublish_failure_removes_stage_and_destination(tmp_path, monkeypatch):
    ledger = _ledger(tmp_path, "a", "issue-a")
    deep = tmp_path / "deep-authority"
    deep.write_text("valid")
    calls = _fake_verifier(monkeypatch, deep_authority=deep)
    destination = tmp_path / "authored"

    def staged_author(_run, _baseline, stage, _specs, *, preview_root, ledger_contexts, owner):
        stage.mkdir()
        (stage / "decision_set.json").write_text("{}")
        ledger_contexts.lookup_v2(owner, ledger, "issue-a")
        deep.write_text("changed")
        return {"decisions": []}

    monkeypatch.setattr(author, "_author_with_ledger_contexts", staged_author)
    with pytest.raises(choices.SourceChoiceError, match="deep authority drift"):
        author.author(tmp_path, tmp_path, destination, [])
    assert not destination.exists()
    assert not (tmp_path / ".authored.author-staging").exists()
    assert calls == [ledger.resolve(), ledger.resolve()]


def test_selector_rejection_and_v1_does_not_open_context(tmp_path, monkeypatch):
    ledger = _ledger(tmp_path, "a", "issue-a")
    calls = _fake_verifier(monkeypatch)
    owner = object()
    contexts = author._AuthorLedgerContexts(owner)
    decision = {"selected_blocks": [{"view": "v", "raw_index": 1, "purpose": "text"}]}
    packet = {"views": {"v": {"blocks": [{"raw_index": 1, "text": "source"}]}}}
    base = {"ledger": str(ledger), "issue_id": "issue-a", "alternative_id": "alt", "view": "v", "raw_index": 1}
    for change in ({"issue_id": "wrong"}, {"alternative_id": "wrong"}, {"view": "wrong"}, {"raw_index": 2}):
        with pytest.raises(ValueError):
            author._materialize_linguistic_source_choice_corrections(decision, packet, [{**base, **change}], 1, contexts, owner)
    v1 = {**base, "before": "source", "after": "replacement"}
    author._materialize_linguistic_source_choice_corrections(decision, packet, [v1], 1, contexts, owner)
    assert decision["linguistic_source_choice_corrections"][0]["before"] == "source"
    assert calls == [ledger.resolve()]


@pytest.mark.parametrize("reserved", ["_ledger_contexts", "_ledger_owner", "_structural_context"])
def test_public_audit_rejects_private_author_context(monkeypatch, reserved):
    from kb_creator.scripts import audit_mineru_ai_merge_fidelity as audit

    reached = []
    monkeypatch.setattr(audit, "_audit_v3_content", lambda *args, **kwargs: reached.append(kwargs))
    with choices._author_ledger_snapshot_scope(lambda path: object()):
        with pytest.raises(TypeError, match="private to the author audit entrypoint"):
            audit.audit_v3_content(**{reserved: object()})
    assert reached == []


@pytest.mark.parametrize("paths", [
    {"structural_input_path": Path("input.json")},
    {"structural_binding_root": Path("root")},
    {"structural_input_path": None, "structural_binding_root": Path("root")},
])
def test_public_audit_requires_complete_structural_paths(monkeypatch, paths):
    from kb_creator.scripts import audit_mineru_ai_merge_fidelity as audit

    reached = []
    monkeypatch.setattr(audit, "_audit_v3_content", lambda *args, **kwargs: reached.append(kwargs))
    with pytest.raises(TypeError, match="structural audit"):
        audit.audit_v3_content(**paths)
    assert reached == []


def test_actual_author_drafts_uses_two_full_checks(tmp_path, monkeypatch):
    """Run the existing compact R1 chain and count only its author invocation."""
    from kb_creator.pipeline import source_choice_successor
    from kb_creator.tests import test_source_choice_v2_integration as integration

    real_author_drafts = author.author_drafts
    real_verify = choices.verify_ledger_v2
    observed: list[Path] = []

    def wrapped_author_drafts(*args, **kwargs):
        if "r1-input" not in str(kwargs.get("draft_input")):
            return real_author_drafts(*args, **kwargs)
        def traced(path):
            observed.append(Path(path).resolve())
            return real_verify(path)

        with monkeypatch.context() as scoped:
            scoped.setattr(choices, "verify_ledger_v2", traced)
            scoped.setattr(source_choice_successor, "verify_ledger_v2", traced)
            result = real_author_drafts(*args, **kwargs)
        assert observed == [observed[0], observed[0]]
        return result

    monkeypatch.setattr(author, "author_drafts", wrapped_author_drafts)
    integration.test_real_v2_r1_chain_reaches_verified_master_and_language_readiness(
        tmp_path, monkeypatch, "provisional", False)


def test_actual_author_drafts_deep_drift_cleans_stage(tmp_path, monkeypatch):
    """A Stage04 authority change after Stage05 aborts before cold publication."""
    from kb_creator.pipeline import source_choice_successor
    from kb_creator.tests import test_source_choice_v2_integration as integration

    real_author_drafts = author.author_drafts
    real_reverify = author._AuthorLedgerContexts.reverify_before_publish
    real_verify = choices.verify_ledger_v2
    observed: list[Path] = []
    attempted = []

    def wrapped_author_drafts(*args, **kwargs):
        if "r1-input" not in str(kwargs.get("draft_input")):
            return real_author_drafts(*args, **kwargs)
        run_root, _, destination = args[:3]
        attempted.append(Path(destination))

        def traced(path):
            observed.append(Path(path).resolve())
            return real_verify(path)

        def drift_before_reverify(contexts, owner):
            if contexts._snapshots:
                packet = Path(run_root) / "outputs/04-visual-merge-bundle/merge_packets/pages/page-001.json"
                packet.write_bytes(packet.read_bytes() + b"\n")
            return real_reverify(contexts, owner)

        with monkeypatch.context() as scoped:
            scoped.setattr(choices, "verify_ledger_v2", traced)
            scoped.setattr(source_choice_successor, "verify_ledger_v2", traced)
            scoped.setattr(author._AuthorLedgerContexts, "reverify_before_publish", drift_before_reverify)
            return real_author_drafts(*args, **kwargs)

    monkeypatch.setattr(author, "author_drafts", wrapped_author_drafts)
    with pytest.raises(ValueError):
        integration.test_real_v2_r1_chain_reaches_verified_master_and_language_readiness(
            tmp_path, monkeypatch, "provisional", False)
    assert len(attempted) == 1
    destination = attempted[0]
    assert not destination.exists()
    assert not (destination.parent / f".{destination.name}.cold-start-staging").exists()
    assert len(observed) == 2


def test_structural_authority_drift_cleans_author_stage(structural_route, monkeypatch):
    import inspect
    from kb_creator.pipeline import source_choice_container_proof as proof
    from kb_creator.pipeline.review_draft_preparation import prepare_review_draft_structural_successor

    case = structural_route
    output = case["root"] / "structural-input"
    prepared = prepare_review_draft_structural_successor(
        predecessor_input=case["input"], predecessor_authored=case["authored"],
        binding_root=case["root"], edits_path=case["edits_path"], output_dir=output)
    destination = case["root"] / "structural-authored"
    real_open = proof.open_structural_projection_context
    opens = []
    mutated = []

    def drift_before_final_open(*, input_path, binding_root):
        opens.append(Path(input_path))
        caller = inspect.currentframe().f_back
        if (caller.f_code.co_name == "_author_drafts_with_ledger_contexts"
                and caller.f_locals.get("structural_context") is not None and not mutated):
            with case["edits_path"].open("ab") as stream:
                stream.write(b"\n")
            mutated.append(True)
        return real_open(input_path=input_path, binding_root=binding_root)

    monkeypatch.setattr(proof, "open_structural_projection_context", drift_before_final_open)
    with pytest.raises(ValueError):
        author.author_drafts(case["run"], output / "draft-pages", destination,
            sorted((output / "author-specs").glob("spec-*.json")), mode="review_draft",
            draft_input=Path(prepared["input"]["path"]), binding_root=case["root"])
    assert mutated == [True]
    assert len(opens) >= 2
    assert not destination.exists()
    assert not (destination.parent / f".{destination.name}.cold-start-staging").exists()


def test_structural_author_replays_standalone_audit(structural_route):
    from kb_creator.pipeline.review_draft_materialization import verify_final_review_draft
    from kb_creator.tests.test_review_draft_structural_successor import (
        test_synthetic_api_to_author_preserves_source_choice,
    )

    case = structural_route
    test_synthetic_api_to_author_preserves_source_choice(case)
    authored = case["root"] / "structural-authored"
    result = verify_final_review_draft(
        run_root=case["run"], authored_root=authored,
        input_path=case["root"] / "structural-input" / case["input"].name,
        evidence_path=authored / "review-draft-evidence.json", binding_root=case["root"])
    assert result["state"] == "verified_review_draft_candidate"
