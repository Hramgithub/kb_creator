from __future__ import annotations

import json
from pathlib import Path

import pytest

from kb_creator.pipeline import pending_source_choices as pending
from kb_creator.pipeline.identity import canonical_bytes, file_identity, sha256_bytes
from kb_creator.pipeline.mechanical_reconstruction import compile_mechanical_draft, verify_mechanical_draft
from kb_creator.tests.test_mechanical_reconstruction import VIEWS, _block, _packet, _stage04, _verified


def _write(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value), encoding="utf-8")


def _fixture(tmp_path: Path, monkeypatch) -> tuple[dict, Path, Path, set[tuple[int, str, int]]]:
    blocks = {
        VIEWS[0]: [_block(1, "Visible NPC")],
        VIEWS[1]: [_block(1, "Different NPC")],
        VIEWS[2]: [_block(1, "Visible NPC")],
    }
    run = _stage04(tmp_path / "run", {1: _packet(1, blocks)})
    candidate = tmp_path / "candidate"
    report = compile_mechanical_draft(run, candidate, authority_validator=_verified)
    diagnostic = next(row for row in report["diagnostics"] if row["code"] == "three_view_content_mismatch")
    manifest = candidate / "mechanical_draft.json"
    issue = {
        "issue_id": "source-choice-p001-three-view-001", "kind": "translation_source_choice_pending",
        "reason": "fixture divergent source views", "source_page": 1,
        "source_pdf_sha256": report["authorities"]["source"]["sha256"],
        "source_excerpt_en": "Visible NPC", "source_excerpt_sha256": sha256_bytes(b"Visible NPC"),
        "evidence": [{"mechanical_diagnostic_index": report["diagnostics"].index(diagnostic)}],
        "candidate_span": {"character_start": 0, "character_end": 11,
                           "text_sha256": sha256_bytes(b"Visible NPC")}, "state": "open",
        "source_selector": {"mechanical_diagnostic": {"code": diagnostic["code"], "source_keys": diagnostic["source_keys"]}},
    }
    review = {
        "schema": "kb_creator.review_draft_input.v1",
        "bindings": {"candidate_manifest": {"path": "candidate/mechanical_draft.json", **file_identity(manifest)}},
        "source_issues": {"schema": "kb_creator.review_draft_source_issues.v1", "issues": [issue]},
        "unresolved_dispositions": [],
    }
    review["input_sha256"] = sha256_bytes(canonical_bytes(review))
    input_path = tmp_path / "review-draft-input.json"; _write(input_path, review)
    monkeypatch.setattr(pending, "verify_mechanical_draft", lambda path: verify_mechanical_draft(path, authority_validator=_verified))
    selected = {(1, VIEWS[0], 1)}
    return review, input_path, run, selected


def test_derives_only_unselected_verified_pending_alternative(tmp_path, monkeypatch):
    review, input_path, run, selected = _fixture(tmp_path, monkeypatch)
    assert pending.derive_pending_source_keys(review_input=review, input_path=input_path, binding_root=tmp_path,
                                              run_root=run, selected_keys=selected) == {(1, VIEWS[1], 1), (1, VIEWS[2], 1)}


def test_coverage_owner_anchors_pending_diagnostic_without_becoming_pending(tmp_path, monkeypatch):
    review, input_path, run, _ = _fixture(tmp_path, monkeypatch)
    owner = {(1, VIEWS[0], 1)}
    assert pending.derive_pending_source_keys(
        review_input=review, input_path=input_path, binding_root=tmp_path, run_root=run,
        selected_keys=set(), coverage_owner_keys=owner,
    ) == {(1, VIEWS[1], 1), (1, VIEWS[2], 1)}


@pytest.mark.parametrize("attack", ("foreign_pdf", "unselected", "resealed_candidate", "stale_packet"))
def test_rejects_forged_or_unbound_pending_authority(tmp_path, monkeypatch, attack):
    review, input_path, run, selected = _fixture(tmp_path, monkeypatch)
    if attack == "foreign_pdf":
        review["source_issues"]["issues"][0]["source_pdf_sha256"] = "0" * 64
    elif attack == "unselected":
        selected = {(1, "foreign", 1)}
    elif attack == "resealed_candidate":
        manifest = tmp_path / "candidate/mechanical_draft.json"
        value = json.loads(manifest.read_text(encoding="utf-8")); value["review_flags"]["accepted"] = True
        _write(manifest, value)
    else:
        packet = run / "outputs/04-visual-merge-bundle/merge_packets/pages/page-001.json"
        packet.write_text("{}", encoding="utf-8")
    if attack != "stale_packet":
        review["input_sha256"] = sha256_bytes(canonical_bytes({key: value for key, value in review.items() if key != "input_sha256"}))
        _write(input_path, review)
    with pytest.raises(pending.PendingSourceChoiceError):
        pending.derive_pending_source_keys(review_input=review, input_path=input_path, binding_root=tmp_path,
                                           run_root=run, selected_keys=selected)
