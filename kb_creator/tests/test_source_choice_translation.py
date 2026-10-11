from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path

import pytest

from kb_creator.pipeline import source_choice_translation as sc
from kb_creator.pipeline.identity import file_identity
from kb_creator.pipeline.manifests import sealed
from kb_creator.pipeline.mechanical_reconstruction import compile_mechanical_draft, verify_mechanical_draft
from kb_creator.pipeline.five_step_intake import build_review_master_en, verify_master_en
from kb_creator.tests.test_mechanical_reconstruction import VIEWS, _block, _packet, _stage04, _verified
from kb_creator.tests.test_review_draft_materialization import _materialized_review_route
from kb_creator.tests import test_review_draft_materialization as review_fixture


def _issue(text: str = "Old reading", *, code: str = "semantic_conflict", source_keys: list[dict] | None = None, source_pdf_sha256: str = "A" * 64) -> dict:
    return {"issue_id": "choice-001", "kind": sc.PENDING_KIND, "reason": "two source readings",
            "source_pdf_sha256": source_pdf_sha256, "source_page": 1,
            "source_selector": {"mechanical_diagnostic": {"code": code, "source_keys": source_keys or [{"view": view, "raw_index": 1} for view in VIEWS]}},
            "source_excerpt_en": text, "source_excerpt_sha256": hashlib.sha256(text.encode()).hexdigest().upper(),
            "evidence": [], "candidate_span": {"line": 1}, "state": "open"}


def _master(tmp_path: Path, issue: dict | None, source_identity: dict) -> Path:
    root = tmp_path / "r0"; root.mkdir(parents=True)
    text = "<!-- source-page-001 -->\nOld reading\n"
    master = root / "MASTER_EN.md"; master.write_text(text, encoding="utf-8")
    evidence = tmp_path / "evidence.json"; evidence.write_text(json.dumps({"source_issues": {"issues": [] if issue is None else [issue]}}), encoding="utf-8")
    rows = []
    if issue:
        start = text.index("Old reading")
        rows = [{"issue_id": issue["issue_id"], "source_page": 1, "source_selector": issue["source_selector"], "character_start": start, "character_end": start + 11, "byte_start": start, "byte_end": start + 11, "text_sha256": hashlib.sha256(b"Old reading").hexdigest().upper()}]
    bindings = sealed("kb_creator.issue_en_bindings.v1", {"master_en": {"path": "MASTER_EN.md", **file_identity(master)}, "final_evidence": {"path": str(evidence), **file_identity(evidence)}, "bindings": rows}, digest_key="bindings_sha256")
    (root / "ISSUE_EN_BINDINGS.v1.json").write_text(json.dumps(bindings), encoding="utf-8")
    provenance = root / "MASTER_EN.provenance.json"
    provenance.write_text(json.dumps({"source": source_identity}), encoding="utf-8")
    (root / "MANIFEST.json").write_text(json.dumps({"final_evidence": {"path": str(evidence), **file_identity(evidence)}, "master_en": {"path": "MASTER_EN.md", **file_identity(master)}, "provenance": {"path": "MASTER_EN.provenance.json", **file_identity(provenance)}}), encoding="utf-8")
    return root


def _candidate(tmp_path: Path) -> Path:
    blocks = {VIEWS[0]: [_block(1, "Old reading")], VIEWS[1]: [_block(1, "New reading")], VIEWS[2]: [_block(1, "New reading")]}
    run = _stage04(tmp_path / "run", {1: _packet(1, blocks)})
    comparison = json.loads((run / "outputs/03-compare-views/comparison.json").read_text())
    for pair in comparison["pairwise"].values(): pair["semantic_conflicts"] = [{"left_raw_index": 1, "right_raw_index": 1}]
    (run / "outputs/03-compare-views/comparison.json").write_text(json.dumps(comparison), encoding="utf-8")
    candidate = tmp_path / "candidate"; compile_mechanical_draft(run, candidate, authority_validator=_verified)
    return candidate


def _candidate_for_text(tmp_path: Path, old: str, new: str, *, source_bytes: bytes = b"synthetic source") -> Path:
    blocks = {VIEWS[0]: [_block(1, old)], VIEWS[1]: [_block(1, new)], VIEWS[2]: [_block(1, new)]}
    run = _stage04(tmp_path / "mechanical-run", {1: _packet(1, blocks)})
    # Explicit tiny Stage04 authority injection: the compiler fixture consumes
    # this exact source identity without a book reconstruction run.
    source = run / "source.pdf"; source.write_bytes(source_bytes)
    run_json = json.loads((run / "run.json").read_text())
    run_json["source"] = {"path_hint": "source.pdf", "bytes": len(source_bytes), "sha256": hashlib.sha256(source_bytes).hexdigest().upper()}
    (run / "run.json").write_text(json.dumps(run_json), encoding="utf-8")
    comparison = json.loads((run / "outputs/03-compare-views/comparison.json").read_text())
    for pair in comparison["pairwise"].values(): pair["semantic_conflicts"] = [{"left_raw_index": 1, "right_raw_index": 1}]
    (run / "outputs/03-compare-views/comparison.json").write_text(json.dumps(comparison), encoding="utf-8")
    candidate = tmp_path / "mechanical-candidate"; compile_mechanical_draft(run, candidate, authority_validator=_verified)
    return candidate


def _candidate_for_readings(tmp_path: Path, readings: tuple[str, str, str], *, force_hold: bool = False) -> Path:
    blocks = {view: [_block(1, text)] for view, text in zip(VIEWS, readings)}
    if force_hold:
        blocks[VIEWS[0]][0]["semantic_evidence"]["text_level"] = 1
    run = _stage04(tmp_path / "mechanical-run", {1: _packet(1, blocks)})
    comparison = json.loads((run / "outputs/03-compare-views/comparison.json").read_text())
    for pair in comparison["pairwise"].values(): pair["semantic_conflicts"] = [{"left_raw_index": 1, "right_raw_index": 1}]
    (run / "outputs/03-compare-views/comparison.json").write_text(json.dumps(comparison), encoding="utf-8")
    candidate = tmp_path / "mechanical-candidate"; compile_mechanical_draft(run, candidate, authority_validator=_verified)
    return candidate


def _fixture_pdf_bytes(tmp_path: Path, monkeypatch) -> bytes:
    seed = tmp_path / "source-seed"; seed.mkdir()
    _materialized_review_route(seed, monkeypatch, [])
    return (seed / "source.pdf").read_bytes()


def _actual_master(tmp_path: Path, monkeypatch, issues: list[dict], *, source_bytes: bytes | None = None) -> Path:
    route_root = tmp_path / "route"; route_root.mkdir(parents=True)
    if source_bytes is not None:
        monkeypatch.setattr(review_fixture, "_pdf", lambda path: path.write_bytes(source_bytes))
    materialized, evidence = _materialized_review_route(route_root, monkeypatch, issues)
    master = tmp_path / "r0"; build_review_master_en(materialized, evidence, master, binding_root=route_root)
    assert verify_master_en(master, binding_root=route_root)["state"] == "verified_review_draft"
    return master


def _actual_pending_route(tmp_path: Path, monkeypatch) -> tuple[Path, Path]:
    from kb_creator.tests.test_review_draft_preparation import (
        test_production_composer_binds_actual_pending_alternative_before_authoring,
    )
    test_production_composer_binds_actual_pending_alternative_before_authoring(
        monkeypatch, tmp_path, False, False)
    # The producer fixture ends with a configuration-drift negative. Restore
    # the original authority before the independent queue/ledger assertions.
    (tmp_path / "config.json").write_text(json.dumps({
        "schema": "kb_creator.review_draft_preparation_config.v1", "forced_selections": [],
    }), encoding="utf-8")
    return tmp_path / "master", tmp_path / "mechanical"


def _candidate_source(candidate: Path) -> dict:
    return json.loads((candidate / "mechanical_draft.json").read_text())["authorities"]["source"]


def _submission(queue_root: Path, rows: list[dict], path: Path) -> Path:
    queue_path = queue_root / "SOURCE_CHOICE_QUEUE.v1.json"
    value = {"schema": sc.SUBMISSION_SCHEMA, "state": "submitted", "queue": {"path": str(queue_path.resolve()), **file_identity(queue_path)}, "choices": rows}
    path.write_text(json.dumps(value), encoding="utf-8")
    return path


@pytest.fixture
def source_choice_route(tmp_path, monkeypatch):
    # The producer is the real compiler format.  The test-only Stage04 boundary
    # is explicit; no JSON adapter or invented source-choice candidate exists.
    candidate = _candidate(tmp_path)
    diagnostic = json.loads((candidate / "mechanical_draft.json").read_text())["diagnostics"][0]
    master = _master(tmp_path, _issue(code=diagnostic["code"], source_keys=diagnostic["source_keys"], source_pdf_sha256=_candidate_source(candidate)["sha256"]), _candidate_source(candidate))
    monkeypatch.setattr(sc, "verify_master_en", lambda root: {"state": "verified_review_draft"})
    monkeypatch.setattr(sc, "verify_mechanical_draft", lambda path: verify_mechanical_draft(path, authority_validator=_verified))
    return master, candidate


def test_prepare_verify_and_record_consume_mechanical_diagnostic(source_choice_route, tmp_path):
    master, candidate = source_choice_route
    result = sc.prepare(master, candidate, tmp_path / "queue")
    assert result["choices"] == 1
    queue = json.loads((tmp_path / "queue/SOURCE_CHOICE_QUEUE.v1.json").read_text())
    assert [row["text"] for row in queue["choices"][0]["alternatives"]] == ["Old reading", "New reading", "New reading"]
    assert queue["choices"][0]["source_pdf_sha256"] == _candidate_source(candidate)["sha256"]
    assert queue["choices"][0]["alternatives"][0]["evidence"]["source"]["sha256"] == _candidate_source(candidate)["sha256"]
    assert Path(result["submission_template"]).is_file()
    assert sc.verify_queue(tmp_path / "queue")["state"] == "verified"
    chosen = queue["choices"][0]["alternatives"][1]["alternative_id"]
    submission = _submission(tmp_path / "queue", [{"issue_id": "choice-001", "disposition": "selected_alternative", "alternative_id": chosen, "reason": "exact source reading"}], tmp_path / "submission.json")
    output = sc.record_decisions(tmp_path / "queue", submission, tmp_path / "ledger")
    ledger = json.loads(Path(output["ledger"]).read_text())
    assert ledger["source_choices"][0]["intended_successor_replacement"]["text_sha256"] == hashlib.sha256(b"New reading").hexdigest().upper()


def test_v2_queue_keeps_raw_witness_distinct_from_display_reader(monkeypatch, tmp_path):
    """A v2 queue derives reader witnesses from the sealed occurrence policy."""
    candidate = _candidate(tmp_path)
    diagnostic = json.loads((candidate / "mechanical_draft.json").read_text())["diagnostics"][0]
    master = _master(tmp_path, _issue(code=diagnostic["code"], source_keys=diagnostic["source_keys"],
                                      source_pdf_sha256=_candidate_source(candidate)["sha256"]), _candidate_source(candidate))
    text = (master / "MASTER_EN.md").read_text(encoding="utf-8"); start = text.index("Old reading")
    evidence = tmp_path / "evidence.json"
    decision_path = master / "evidence/review/page-001.json"; decision_path.parent.mkdir(parents=True)
    decision_path.write_text(json.dumps({"markdown": "Old reading", "semantic_structure": {"units": []},
        "selected_blocks": [{"view": VIEWS[0], "raw_index": 1, "purpose": "text"}]}), encoding="utf-8")
    audit_path = tmp_path / "audit.json"
    audit_path.write_text(json.dumps({"pages": [{"source_page": 1, "ordered_proof_stream": [{
        "kind": "selected", "unit": {"source_page": 1, "view_id": VIEWS[0], "raw_index": 1,
            "block_type": "text", "original_text_sha256": hashlib.sha256(b"Old reading").hexdigest().upper(),
            "normalized_text_sha256": hashlib.sha256(b"Oldreading").hexdigest().upper(),
            "normalized_character_count": 10}, "markdown_span": [0, 10]}]}]}), encoding="utf-8")
    evidence_value = json.loads(evidence.read_text(encoding="utf-8"))
    evidence_value["authored"] = {"stage05_audit": {"path": "audit.json", **file_identity(audit_path)}}
    evidence.write_text(json.dumps(evidence_value), encoding="utf-8")
    manifest_path = master / "MANIFEST.json"
    manifest_value = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest_value["final_evidence"] = {"path": str(evidence), **file_identity(evidence)}
    manifest_path.write_text(json.dumps(manifest_value), encoding="utf-8")
    binding = {"issue_id": "choice-001", "source_page": 1,
        "source_selector": _issue(code=diagnostic["code"], source_keys=diagnostic["source_keys"])["source_selector"],
        "source_occurrence": {"source_excerpt": "Old reading", "source_excerpt_sha256": hashlib.sha256(b"Old reading").hexdigest().upper(), "candidate_span": {}, "source_locator": _issue(code=diagnostic["code"], source_keys=diagnostic["source_keys"])["source_selector"]},
        "reader_anchor": {"kind": "ordered_selected_source_v1", "selected_source_key": {"view": VIEWS[0], "raw_index": 1}},
        "page_reader_span": {"character_start": 0, "character_end": 11, "byte_start": 0, "byte_end": 11, "text_sha256": hashlib.sha256(b"Old reading").hexdigest().upper(), "decision_markdown_sha256": hashlib.sha256(b"Old reading").hexdigest().upper()},
        "master_reader_span": {"character_start": start, "character_end": start + 11, "byte_start": len(text[:start].encode()), "byte_end": len(text[:start + 11].encode()), "text_sha256": hashlib.sha256(b"Old reading").hexdigest().upper(), "master_en_sha256": hashlib.sha256(text.encode()).hexdigest().upper()},
        "reader_projection": {"policy": "identity_v1", "reader_text": "Old reading", "reader_text_sha256": hashlib.sha256(b"Old reading").hexdigest().upper()},
        "decision": {"path": "evidence/review/page-001.json", **file_identity(decision_path)}, "stage05_audit": {"path": "audit.json", **file_identity(audit_path)}}
    v2 = sealed("kb_creator.issue_en_bindings.v2", {"master_en": {"path": "MASTER_EN.md", **file_identity(master / "MASTER_EN.md")},
        "final_evidence": {"path": str(evidence), **file_identity(evidence)}, "bindings": [binding]}, digest_key="bindings_sha256")
    (master / "ISSUE_EN_BINDINGS.v2.json").write_text(json.dumps(v2), encoding="utf-8")
    monkeypatch.setattr(sc, "verify_master_en", lambda _root, **_kwargs: {"state": "verified_review_draft"})
    monkeypatch.setattr(sc, "verify_mechanical_draft", lambda path: verify_mechanical_draft(path, authority_validator=_verified))
    result = sc.prepare_v2(master, candidate, tmp_path / "queue-v2")
    queue = json.loads(Path(result["queue"]).read_text()); choice = queue["choices"][0]
    assert choice["alternatives"][0]["raw_text"] == "Old reading"
    assert choice["alternatives"][0]["reader_text"] == "Old reading"
    submission = tmp_path / "submission-v2.json"
    submission.write_text(json.dumps({"schema": sc.SUBMISSION_SCHEMA_V2, "state": "submitted",
        "queue": {"path": str(Path(result["queue"]).resolve()), **file_identity(Path(result["queue"]))},
        "choices": [{"issue_id": "choice-001", "disposition": "selected_alternative",
                     "alternative_id": choice["alternatives"][1]["alternative_id"], "reason": "selected raw witness"}]}), encoding="utf-8")
    recorded = sc.record_decisions_v2(Path(result["queue"]), submission, tmp_path / "ledger-v2")
    assert sc.verify_ledger_v2(Path(recorded["ledger"]))["choices"] == 1


def test_actual_review_master_producer_prepares_verifies_and_records(tmp_path, monkeypatch):
    """Use the tracked Stage05/06/materializer/MASTER_EN route without stubbing master verification."""
    master, candidate = _actual_pending_route(tmp_path, monkeypatch)
    queue_root = tmp_path / "actual-queue"
    prepared = sc.prepare_v2(master, candidate, queue_root, binding_root=tmp_path)
    queue_path = Path(prepared["queue"])
    queue = json.loads(queue_path.read_text(encoding="utf-8"))
    choice = queue["choices"][0]
    selected = next(row["alternative_id"] for row in choice["alternatives"]
                    if row["selectable"] and row["alternative_id"] != choice["provisional_alternative_id"])
    assert sc.verify_queue_v2(queue_root)["state"] == "verified"
    submission = tmp_path / "actual-submission.json"
    submission.write_text(json.dumps({"schema": sc.SUBMISSION_SCHEMA_V2, "state": "submitted",
        "queue": {"path": str(queue_path.resolve()), **file_identity(queue_path)},
        "choices": [{"issue_id": choice["issue_id"], "disposition": "selected_alternative",
                     "alternative_id": selected, "reason": "exact reviewed source block"}]}), encoding="utf-8")
    result = sc.record_decisions_v2(queue_root, submission, tmp_path / "actual-ledger")
    assert Path(result["ledger"]).is_file()
    assert sc.verify_ledger_v2(tmp_path / "actual-ledger")["choices"] == 1


def test_actual_review_master_zero_choice_and_blocked_source(tmp_path, monkeypatch):
    source_bytes = _fixture_pdf_bytes(tmp_path, monkeypatch)
    candidate = _candidate_for_text(tmp_path, "Source", "New Source", source_bytes=source_bytes)
    monkeypatch.setattr(sc, "verify_mechanical_draft", lambda path: verify_mechanical_draft(path, authority_validator=_verified))
    zero_master = _actual_master(tmp_path / "zero", monkeypatch, [], source_bytes=source_bytes)
    assert sc.prepare_v2(zero_master, candidate, tmp_path / "zero-queue", binding_root=tmp_path / "zero/route")["choices"] == 0
    blocked = _issue("Source", source_pdf_sha256=_candidate_source(candidate)["sha256"])
    blocked["kind"] = "source_material_blocked"
    blocked["source_selector"] = {"view": VIEWS[0], "raw_index": 1}
    blocked_master = _actual_master(tmp_path / "blocked", monkeypatch, [blocked], source_bytes=source_bytes)
    with pytest.raises(sc.SourceChoiceError, match="source material is blocked"):
        sc.prepare_v2(blocked_master, candidate, tmp_path / "blocked-queue", binding_root=tmp_path / "blocked/route")


def test_equal_witnesses_and_empty_readings_are_not_ambiguous_replacements(tmp_path, monkeypatch):
    candidate = _candidate_for_readings(tmp_path, ("", "Old reading", "New reading"))
    diagnostic = json.loads((candidate / "mechanical_draft.json").read_text())["diagnostics"][0]
    source = _candidate_source(candidate)
    master = _master(tmp_path, _issue(code=diagnostic["code"], source_keys=diagnostic["source_keys"], source_pdf_sha256=source["sha256"]), source)
    monkeypatch.setattr(sc, "verify_master_en", lambda root: {"state": "verified_review_draft"})
    monkeypatch.setattr(sc, "verify_mechanical_draft", lambda path: verify_mechanical_draft(path, authority_validator=_verified))
    queue_root = tmp_path / "queue"; sc.prepare(master, candidate, queue_root)
    choice = json.loads((queue_root / "SOURCE_CHOICE_QUEUE.v1.json").read_text())["choices"][0]
    assert choice["alternatives"][0]["selectable"] is False
    assert len(choice["provisional_alternative_ids"]) == 1
    assert choice["provisional_alternative_id"] == choice["provisional_alternative_ids"][0]


def test_single_or_absent_supported_reading_cannot_be_pending_choice(tmp_path, monkeypatch):
    for index, (readings, message) in enumerate([(("", "A", "A"), "only one supported reading"), (("", "", ""), "no supported reading")]):
        candidate = _candidate_for_readings(tmp_path / f"case-{index}", readings, force_hold=True)
        report = json.loads((candidate / "mechanical_draft.json").read_text())
        diagnostic, source = report["diagnostics"][0], _candidate_source(candidate)
        master = _master(tmp_path / (message + "-master"), _issue(code=diagnostic["code"], source_keys=diagnostic["source_keys"], source_pdf_sha256=source["sha256"]), source)
        monkeypatch.setattr(sc, "verify_master_en", lambda root: {"state": "verified_review_draft"})
        monkeypatch.setattr(sc, "verify_mechanical_draft", lambda path: verify_mechanical_draft(path, authority_validator=_verified))
        with pytest.raises(sc.SourceChoiceError, match=message): sc.prepare(master, candidate, tmp_path / (message + "-queue"))


@pytest.mark.parametrize("mutation", ["candidate", "packet", "source_issue", "fabricated", "missing", "overlap"])
def test_verify_queue_rederives_complete_authority(source_choice_route, tmp_path, mutation):
    master, candidate = source_choice_route; queue_root = tmp_path / "queue"; sc.prepare(master, candidate, queue_root)
    queue_path = queue_root / "SOURCE_CHOICE_QUEUE.v1.json"
    if mutation == "candidate":
        (candidate / "pages/page-001.json").write_text("{}", encoding="utf-8")
    elif mutation == "packet":
        report = json.loads((candidate / "mechanical_draft.json").read_text())
        packet = Path(report["run_root"]) / "outputs/04-visual-merge-bundle/merge_packets/pages/page-001.json"; packet.write_text("{}", encoding="utf-8")
    elif mutation == "source_issue":
        evidence = json.loads((master / "MANIFEST.json").read_text())["final_evidence"]["path"]
        Path(evidence).write_text("{}", encoding="utf-8")
    else:
        value = json.loads(queue_path.read_text())
        if mutation == "fabricated": value["choices"][0]["alternatives"][1]["text"] = "Fabricated"
        elif mutation == "missing": value["choices"] = []
        else: value["choices"].append(copy.deepcopy(value["choices"][0]))
        value = sealed(sc.QUEUE_SCHEMA, {key: row for key, row in value.items() if key not in {"schema", "queue_sha256"}}, digest_key="queue_sha256")
        queue_path.write_text(json.dumps(value), encoding="utf-8")
    with pytest.raises(sc.SourceChoiceError): sc.verify_queue(queue_root)


def test_rejects_incomplete_submission_and_output_overlap(source_choice_route, tmp_path):
    master, candidate = source_choice_route
    with pytest.raises(sc.SourceChoiceError): sc.prepare(master, candidate, candidate)
    sc.prepare(master, candidate, tmp_path / "queue")
    with pytest.raises(sc.SourceChoiceError): sc.record_decisions(tmp_path / "queue", [], tmp_path / "ledger")


def test_retained_semantic_and_immutable_outputs(source_choice_route, tmp_path):
    master, candidate = source_choice_route; queue_root = tmp_path / "queue"; sc.prepare(master, candidate, queue_root)
    queue = json.loads((queue_root / "SOURCE_CHOICE_QUEUE.v1.json").read_text())
    provisional = queue["choices"][0]["provisional_alternative_id"]
    rows = [{"issue_id": "choice-001", "disposition": "unresolved_semantic", "alternative_id": provisional, "reason": "meaning remains open", "label": "Проверить смысл"}]
    submission = _submission(queue_root, rows, tmp_path / "retained-submission.json")
    before = submission.read_bytes()
    sc.record_decisions(queue_root, submission, tmp_path / "ledger")
    assert submission.read_bytes() == before
    ledger = json.loads((tmp_path / "ledger/SOURCE_CHOICE_LEDGER.v1.json").read_text())
    assert ledger["source_choices"][0]["intended_successor_replacement"]["resulting_issue_state"] == "retained"
    changed_rows = [dict(rows[0], reason="a changed submission")]
    changed_submission = _submission(queue_root, changed_rows, tmp_path / "changed-submission.json")
    with pytest.raises(sc.SourceChoiceError):
        sc.record_decisions(queue_root, changed_submission, tmp_path / "ledger")


def test_rejects_cross_book_candidate_and_binds_source_identity(tmp_path, monkeypatch):
    master, candidate_a = _actual_pending_route(tmp_path, monkeypatch)
    candidate_b = _candidate_for_text(tmp_path / "b", "Source", "New Source", source_bytes=b"book b")
    assert _candidate_source(candidate_a)["sha256"] != _candidate_source(candidate_b)["sha256"]
    monkeypatch.setattr(sc, "verify_mechanical_draft", lambda path: verify_mechanical_draft(path, authority_validator=_verified))
    with pytest.raises(sc.SourceChoiceError, match="source identity does not match"):
        sc.prepare_v2(master, candidate_b, tmp_path / "wrong-source-queue", binding_root=tmp_path)
    assert not (tmp_path / "wrong-source-queue").exists()


def test_rejects_stale_queue_bound_submission_even_when_choices_match(source_choice_route, tmp_path):
    master, candidate = source_choice_route
    queue_a, queue_b = tmp_path / "queue-a", tmp_path / "queue-b"
    sc.prepare(master, candidate, queue_a)
    diagnostic = json.loads((candidate / "mechanical_draft.json").read_text())["diagnostics"][0]
    other_master = _master(tmp_path / "other", _issue(code=diagnostic["code"], source_keys=diagnostic["source_keys"], source_pdf_sha256=_candidate_source(candidate)["sha256"]), _candidate_source(candidate))
    sc.prepare(other_master, candidate, queue_b)
    choice = json.loads((queue_a / "SOURCE_CHOICE_QUEUE.v1.json").read_text())["choices"][0]
    submission = _submission(queue_a, [{"issue_id": choice["issue_id"], "disposition": "selected_alternative", "alternative_id": choice["alternatives"][1]["alternative_id"], "reason": "same visible reading"}], tmp_path / "stale-submission.json")
    with pytest.raises(sc.SourceChoiceError, match="different queue"):
        sc.record_decisions(queue_b, submission, tmp_path / "ledger")


@pytest.mark.parametrize("mutation", [None, "replacement", "future_r1", "submission", "candidate"])
def test_ledger_consumption_rederives_decisions_and_source_authority(source_choice_route, tmp_path, mutation):
    master, candidate = source_choice_route
    queue_root, ledger_root = tmp_path / "queue", tmp_path / "ledger"
    sc.prepare(master, candidate, queue_root)
    choice = json.loads((queue_root / "SOURCE_CHOICE_QUEUE.v1.json").read_text())["choices"][0]
    rows = [{"issue_id": choice["issue_id"], "disposition": "selected_alternative",
             "alternative_id": choice["alternatives"][1]["alternative_id"], "reason": "exact source reading"}]
    submission = _submission(queue_root, rows, tmp_path / "submission.json")
    sc.record_decisions(queue_root, submission, ledger_root)
    ledger_path = ledger_root / "SOURCE_CHOICE_LEDGER.v1.json"
    if mutation in {"replacement", "future_r1"}:
        value = json.loads(ledger_path.read_text())
        if mutation == "replacement":
            value["source_choices"][0]["intended_successor_replacement"]["result_sha256"] = "0" * 64
        else:
            value["intended_successor"]["r1_identity"] = {"sha256": "0" * 64}
        value = sealed(sc.LEDGER_SCHEMA, {k: v for k, v in value.items() if k not in {"schema", "ledger_sha256"}}, digest_key="ledger_sha256")
        ledger_path.write_text(json.dumps(value), encoding="utf-8")
    elif mutation == "submission":
        path = ledger_root / "SOURCE_CHOICE_SUBMISSION.v1.json"
        value = json.loads(path.read_text())
        value["choices"][0]["alternative_id"] = choice["alternatives"][0]["alternative_id"]
        value = sealed(sc.SUBMISSION_SCHEMA, {k: v for k, v in value.items() if k not in {"schema", "submission_sha256"}}, digest_key="submission_sha256")
        path.write_text(json.dumps(value), encoding="utf-8")
    elif mutation == "candidate":
        (candidate / "pages/page-001.json").write_text("{}", encoding="utf-8")
    before = ledger_path.read_bytes()
    if mutation:
        with pytest.raises(sc.SourceChoiceError):
            sc.verify_ledger(ledger_root)
    else:
        assert sc.verify_ledger(ledger_root)["state"] == "verified"
    assert ledger_path.read_bytes() == before
