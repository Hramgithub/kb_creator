from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from kb_creator.pdf_raw import step5_non_live_contracts as contracts
from kb_creator.pdf_raw.step5_non_live_identity_adapter import run_non_live_identity_capture
from kb_creator.pdf_raw.step5_non_live_policy import SyntheticCapabilityBroker
from kb_creator.tests import _step5_non_live_fixture_leaves as fixtures


def _broker():
    return SyntheticCapabilityBroker(**fixtures.broker_bundle())


def test_identity_two_column_positive():
    payload = contracts.validate_identity_capture(run_non_live_identity_capture(fixtures.invocation("identity_capture"), _broker()))
    assert payload["source_virtual_name"] == fixtures.SOURCE_TWO_COLUMN_NAME


def test_identity_nested_form_positive():
    bundle = fixtures.broker_bundle()
    bundle["controls"][fixtures.SELECTION_CONTROL_NAME] = fixtures.selection_control(fixtures.SOURCE_NESTED_FORM_NAME)
    broker = SyntheticCapabilityBroker(**bundle)
    payload = contracts.validate_identity_capture(run_non_live_identity_capture(fixtures.invocation("identity_capture", fixtures.SOURCE_NESTED_FORM_NAME), broker))
    assert payload["page_ref"] == [12, 0]


def test_identity_control_content_binding_before_source():
    broker = _broker()
    invocation = json.loads(fixtures.invocation("identity_capture"))
    invocation["control_record_content_sha256"] = "0" * 64
    raw = contracts.seal_closed(invocation, contracts._INVOCATION_KEYS)
    failure = json.loads(run_non_live_identity_capture(raw, broker))
    assert failure["error_code"] == "control_record_content_sha256_invalid"
    assert [event["capability"] for event in broker.audit_payload()["events"][:2]] == ["control_read_exact", "queue_read_exact"]


def test_identity_prerequisite_and_queue_before_source():
    broker = _broker()
    run_non_live_identity_capture(fixtures.invocation("identity_capture"), broker)
    caps = [event["capability"] for event in broker.audit_payload()["events"]]
    assert caps[:2] == ["control_read_exact", "queue_read_exact"]


def test_identity_source_byte_drift_target_first():
    bundle = fixtures.broker_bundle()
    source = bundle["sources"][fixtures.SOURCE_TWO_COLUMN_NAME]
    source["bytes"] = source["bytes"] + b"x"
    broker = SyntheticCapabilityBroker(**bundle)
    payload = contracts.validate_identity_capture(run_non_live_identity_capture(fixtures.invocation("identity_capture"), broker))
    assert payload["source_byte_length"] == len(source["bytes"])


def test_identity_metadata_drift_target_first():
    bundle = fixtures.broker_bundle()
    source = bundle["sources"][fixtures.SOURCE_TWO_COLUMN_NAME]
    source["metadata"] = dict(source["metadata"])
    source["metadata"]["profile"] = "synthetic-fixture-v2-drift"
    broker = SyntheticCapabilityBroker(**bundle)
    payload = contracts.validate_identity_capture(run_non_live_identity_capture(fixtures.invocation("identity_capture"), broker))
    assert payload["synthetic_metadata_before"]["profile"] == "synthetic-fixture-v2-drift"


def test_identity_structural_drift_target_first():
    bundle = fixtures.broker_bundle()
    source = bundle["sources"][fixtures.SOURCE_TWO_COLUMN_NAME]
    source["page_identity"] = dict(source["page_identity"])
    source["page_identity"]["page_ref"] = [21, 0]
    broker = SyntheticCapabilityBroker(**bundle)
    payload = contracts.validate_identity_capture(run_non_live_identity_capture(fixtures.invocation("identity_capture"), broker))
    assert payload["page_ref"] == [21, 0]


def test_identity_exactly_two_reads_and_zero_downstream_calls():
    broker = _broker()
    run_non_live_identity_capture(fixtures.invocation("identity_capture"), broker)
    caps = [event["capability"] for event in broker.audit_payload()["events"]]
    assert caps.count("source_read_exact") == 2
    assert "proof_stage_a" not in caps


def test_identity_invalid_phase_fails_before_broker_access():
    broker = _broker()
    invocation = json.loads(fixtures.invocation("identity_capture"))
    invocation["phase"] = "page_preflight"
    raw = contracts.canonical_json(invocation)
    try:
        run_non_live_identity_capture(raw, broker)
    except ValueError:
        pass
    assert broker.audit_payload()["event_count"] == 0


def test_identity_invalid_selection_schema_returns_closed_failure():
    bundle = fixtures.broker_bundle()
    control = json.loads(fixtures.selection_control())
    control["schema"] = "bad"
    bundle["controls"][fixtures.SELECTION_CONTROL_NAME] = contracts.seal_closed(control, contracts._SELECTION_KEYS)
    broker = SyntheticCapabilityBroker(**bundle)
    failure = json.loads(run_non_live_identity_capture(fixtures.invocation("identity_capture"), broker))
    assert failure["terminal_state"] == "synthetic_identity_capture_rejected"


def test_identity_policy_digest_mismatch_returns_failure():
    bundle = fixtures.broker_bundle()
    broker = SyntheticCapabilityBroker(**bundle)
    invocation = json.loads(fixtures.invocation("identity_capture"))
    invocation["synthetic_policy_sha256"] = "0" * 64
    raw = contracts.seal_closed(invocation, contracts._INVOCATION_KEYS)
    try:
        run_non_live_identity_capture(raw, broker)
    except ValueError as exc:
        assert str(exc) == "synthetic_policy_sha256_invalid"


def test_identity_failure_propagates_prerequisite_digest_when_available():
    bundle = fixtures.broker_bundle()
    control = json.loads(fixtures.selection_control())
    control["selected_item_row_sha256"] = "0" * 64
    bundle["controls"][fixtures.SELECTION_CONTROL_NAME] = contracts.seal_closed(control, contracts._SELECTION_KEYS)
    broker = SyntheticCapabilityBroker(**bundle)
    failure = json.loads(run_non_live_identity_capture(fixtures.invocation("identity_capture"), broker))
    assert failure["prerequisite_qa_sha256"] == fixtures.prerequisite()["content_sha256"]
