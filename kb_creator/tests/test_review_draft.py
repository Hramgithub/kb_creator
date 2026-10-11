from __future__ import annotations

import copy

import pytest

from kb_creator.pipeline.identity import canonical_bytes, sha256_bytes
from kb_creator.pipeline.review_draft import (
    FINAL_SCHEMA,
    INPUT_SCHEMA,
    ISSUES_SCHEMA,
    ReviewDraftError,
    finalize_review_draft_evidence,
    prepare_review_draft_input,
    validate_review_draft_evidence,
    validate_review_draft_input,
)


def _identity(name: str) -> dict:
    return {"path": name, "bytes": 1, "sha256": "A" * 64}


def _input(*, issue: bool = False) -> dict:
    issues = []
    if issue:
        issues = [{
            "issue_id": "source-p003-printed-wording", "kind": "source_wording",
            "reason": "printed wording needs an editorial decision", "source_pdf_sha256": "B" * 64,
            "source_page": 3, "source_selector": {"view": "original_pipeline_txt", "raw_index": 7},
            "source_excerpt_en": "printed wording", "source_excerpt_sha256": "C" * 64,
            "evidence": [_identity("packets/page-003.json")],
            "candidate_span": {"start": 10, "end": 25, "sha256": "D" * 64}, "state": "open",
        }]
    value = {
        "schema": INPUT_SCHEMA,
        "bindings": {"candidate": _identity("candidate/manifest.json"), "queue": _identity("review/queue.json")},
        "source_issues": {"schema": ISSUES_SCHEMA, "issues": issues},
        "unresolved_dispositions": [{
            "source_page": 1, "predecessor_unresolved": "Stage05 audit pending",
            "category": "administrative_pending", "outcome": "audit_pending", "evidence": [_identity("proposal.json")],
            "predecessor": _identity("old/page-001.json"), "current": _identity("new/page-001.json"),
        }],
    }
    value["input_sha256"] = sha256_bytes(canonical_bytes(value))
    return value


def test_prepared_input_is_acyclic_and_preserves_open_source_issue():
    value = _input(issue=True)
    record = validate_review_draft_input(value)
    prepared = prepare_review_draft_input(value)
    assert record.sha256 == value["input_sha256"]
    assert prepared == {
        "schema": "kb_creator.review_draft_preflight.v1", "state": "prepared_for_audit",
        "input_sha256": value["input_sha256"], "open_issue_ids": ["source-p003-printed-wording"],
        "audit_pending_count": 1,
    }


@pytest.mark.parametrize("mutation", ["future_binding", "premature_close", "invented_ru_id", "seal"])
def test_input_rejects_circular_or_premature_authority(mutation):
    value = _input(issue=True)
    if mutation == "future_binding":
        value["bindings"]["stage05_audit"] = _identity("audit.json")
    elif mutation == "premature_close":
        value["unresolved_dispositions"][0]["outcome"] = "closed"
    elif mutation == "invented_ru_id":
        value["source_issues"]["issues"][0]["ru_unit_id"] = "invented"
    else:
        value["input_sha256"] = "0" * 64
    if mutation != "seal":
        value["input_sha256"] = sha256_bytes(canonical_bytes({key: item for key, item in value.items() if key != "input_sha256"}))
    with pytest.raises(ReviewDraftError):
        validate_review_draft_input(value)


def test_final_evidence_only_closes_named_audit_pending_entries_and_keeps_false_flags():
    value = _input()
    final = finalize_review_draft_evidence(
        value,
        authored={"decision_set": _identity("decision_set.json")},
        audit={"passed": True, "errors": []},
        visual_reviewed_false_pages=[40, 3],
    )
    assert final["schema"] == FINAL_SCHEMA
    assert final["unresolved_dispositions"][0]["outcome"] == "closed_after_audit"
    assert final["visual_reviewed_false_pages"] == [3, 40]
    changed = copy.deepcopy(final); changed["audit"]["passed"] = False
    with pytest.raises(ReviewDraftError, match="seal"):
        validate_review_draft_evidence(changed)


def test_open_machine_hold_cannot_enter_cold_authoring():
    value = _input()
    value["unresolved_dispositions"][0].update(category="machine_blocker", outcome="blocked")
    value["input_sha256"] = sha256_bytes(canonical_bytes({key: item for key, item in value.items() if key != "input_sha256"}))
    with pytest.raises(ReviewDraftError, match="holds"):
        prepare_review_draft_input(value)


def test_input_rejects_missing_disposition_evidence():
    value = _input(); value["unresolved_dispositions"][0]["evidence"] = []
    value["input_sha256"] = sha256_bytes(canonical_bytes({key: item for key, item in value.items() if key != "input_sha256"}))
    with pytest.raises(ReviewDraftError, match="outcome"):
        validate_review_draft_input(value)
