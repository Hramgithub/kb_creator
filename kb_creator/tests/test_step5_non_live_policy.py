from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from kb_creator.pdf_raw.step5_non_live_controller import run_non_live_controller
from kb_creator.pdf_raw import step5_non_live_contracts as contracts
from kb_creator.pdf_raw.step5_non_live_identity_adapter import run_non_live_identity_capture
from kb_creator.pdf_raw.step5_non_live_policy import SyntheticCapabilityBroker, build_policy
from kb_creator.tests import _step5_non_live_fixture_leaves as fixtures


def _broker():
    return SyntheticCapabilityBroker(**fixtures.broker_bundle())


def test_broker_rejects_caller_policy_and_nonexact_registry():
    assert build_policy()["registry"][0] == fixtures.SOURCE_TWO_COLUMN_NAME
    bundle = fixtures.broker_bundle()
    bundle["controls"]["fixture://step5/control/extra.v1"] = bundle["controls"][fixtures.SELECTION_CONTROL_NAME]
    with pytest.raises(ValueError, match="synthetic_policy_invalid"):
        SyntheticCapabilityBroker(**bundle)


def test_denied_attempt_blocks_later_allowed_read():
    broker = _broker()
    with pytest.raises(ValueError, match="synthetic_policy_denied"):
        broker.read_source("controller", fixtures.SOURCE_TWO_COLUMN_NAME)
    with pytest.raises(ValueError, match="synthetic_policy_poisoned"):
        broker.read_control("adapter", fixtures.SELECTION_CONTROL_NAME)


def test_denied_attempt_blocks_later_output_create():
    broker = _broker()
    with pytest.raises(ValueError, match="synthetic_policy_denied"):
        broker.write_output("adapter", b"bad")
    with pytest.raises(ValueError, match="synthetic_policy_poisoned"):
        broker.write_output("controller", b"good")


def test_audit_target_first_reseal():
    broker = _broker()
    broker.read_control("adapter", fixtures.SELECTION_CONTROL_NAME)
    audit = broker.audit_payload()
    assert audit["event_count"] == 1
    assert audit["events"][0]["matched_policy_entry"] == "adapter:control_read_exact"


@pytest.mark.parametrize(
    "mutation",
    [
        "forged_matched_policy_entry",
        "ordinal_gap",
        "subject_mismatch",
        "normalized_name_mismatch",
        "requested_access_mismatch",
        "missing_denied_inventory",
    ],
)
def test_audit_policy_replay_target_first_resealed(mutation):
    broker = _broker()
    broker.read_control("adapter", fixtures.SELECTION_CONTROL_NAME)
    with pytest.raises(ValueError):
        broker.read_source("controller", fixtures.SOURCE_TWO_COLUMN_NAME)
    audit = json.loads(contracts.canonical_json(broker.audit_payload()))
    if mutation == "forged_matched_policy_entry":
        audit["events"][0]["matched_policy_entry"] = "forged-policy-match"
        audit["events"][0] = contracts.sealed_dict(audit["events"][0], contracts._AUDIT_EVENT_KEYS)
        audit["event_sha256_inventory"][0] = audit["events"][0]["content_sha256"]
    elif mutation == "ordinal_gap":
        audit["events"][1]["ordinal"] = 3
        audit["events"][1] = contracts.sealed_dict(audit["events"][1], contracts._AUDIT_EVENT_KEYS)
        audit["event_sha256_inventory"][1] = audit["events"][1]["content_sha256"]
    elif mutation == "subject_mismatch":
        audit["events"][0]["subject"] = "controller"
        audit["events"][0] = contracts.sealed_dict(audit["events"][0], contracts._AUDIT_EVENT_KEYS)
        audit["event_sha256_inventory"][0] = audit["events"][0]["content_sha256"]
    elif mutation == "normalized_name_mismatch":
        audit["events"][0]["normalized_name"] = "fixture://step5/control/other.v1"
        audit["events"][0] = contracts.sealed_dict(audit["events"][0], contracts._AUDIT_EVENT_KEYS)
        audit["event_sha256_inventory"][0] = audit["events"][0]["content_sha256"]
    elif mutation == "requested_access_mismatch":
        audit["events"][0]["requested_access"] = "read_metadata"
        audit["events"][0] = contracts.sealed_dict(audit["events"][0], contracts._AUDIT_EVENT_KEYS)
        audit["event_sha256_inventory"][0] = audit["events"][0]["content_sha256"]
    else:
        audit["denied_capabilities"] = []
    audit = contracts.sealed_dict(audit, contracts._AUDIT_KEYS)
    with pytest.raises(ValueError, match="policy_audit_invalid"):
        contracts.validate_audit(audit)


def test_output_sink_is_at_most_one_create_new():
    broker = _broker()
    broker.write_output("controller", b"one")
    with pytest.raises(ValueError, match="synthetic_policy_denied"):
        broker.write_output("controller", b"two")


def test_controller_accepts_only_validated_positive_output():
    broker = _broker()
    raw = run_non_live_controller(fixtures.invocation("identity_capture"), broker, run_non_live_identity_capture)
    assert raw == broker.output_sink


def test_controller_validates_sealed_failure_core():
    broker = _broker()

    def failing_adapter(invocation_raw, inner_broker):
        invocation = json.loads(invocation_raw)
        return json.dumps({"schema": "kb_creator.pdf_raw.NonLivePagePreflightFailure.v1", "phase": invocation["phase"]}).encode("utf-8")

    with pytest.raises(ValueError, match="canonical_bytes_invalid|closed_schema_invalid|failure_schema_invalid"):
        run_non_live_controller(fixtures.invocation("identity_capture"), broker, failing_adapter)


def test_controller_rejects_unsealed_or_cross_phase_failure():
    broker = _broker()

    def failing_adapter(invocation_raw, inner_broker):
        invocation = json.loads(invocation_raw)
        failure = json.loads(run_non_live_identity_capture(invocation_raw, inner_broker))
        failure["phase"] = "page_preflight"
        return json.dumps(failure, sort_keys=True, separators=(",", ":")).encode("utf-8")

    with pytest.raises(ValueError, match="failure_binding_invalid|canonical_bytes_invalid|closed_schema_invalid"):
        run_non_live_controller(fixtures.invocation("identity_capture"), broker, failing_adapter)


def test_controller_rejects_positive_after_poison():
    broker = _broker()
    with pytest.raises(ValueError):
        broker.read_source("controller", fixtures.SOURCE_TWO_COLUMN_NAME)
    raw = run_non_live_controller(fixtures.invocation("identity_capture"), broker, run_non_live_identity_capture)
    assert json.loads(raw)["error_code"] == "synthetic_policy_poisoned"
    assert broker.output_sink is None


def test_policy_audit_records_poison_followup_decision():
    broker = _broker()
    with pytest.raises(ValueError):
        broker.read_source("controller", fixtures.SOURCE_TWO_COLUMN_NAME)
    with pytest.raises(ValueError):
        broker.read_control("adapter", fixtures.SELECTION_CONTROL_NAME)
    audit = broker.audit_payload()
    assert audit["events"][-1]["decision"] == "deny_run_poisoned"


def test_policy_public_root_assert_uses_literal_name():
    broker = _broker()
    assert broker.assert_public_root_inactive("adapter") == "page_proof_stage_a_fixture_coverage_incomplete"


def test_policy_queue_read_is_adapter_only():
    broker = _broker()
    assert broker.read_queue("adapter", fixtures.QUEUE_NAME)
    with pytest.raises(ValueError):
        broker.read_queue("controller", fixtures.QUEUE_NAME)


def test_policy_source_metadata_is_adapter_only():
    broker = _broker()
    assert broker.source_metadata("adapter", fixtures.SOURCE_TWO_COLUMN_NAME)["source_name"] == fixtures.SOURCE_TWO_COLUMN_NAME


def test_policy_structural_identity_is_page_zero_only():
    broker = _broker()
    with pytest.raises(ValueError):
        broker.structural_identity("adapter", fixtures.SOURCE_TWO_COLUMN_NAME, 1)


def test_controller_rejects_non_bytes_output():
    broker = _broker()
    with pytest.raises(ValueError, match="controller_output_invalid"):
        run_non_live_controller(fixtures.invocation("identity_capture"), broker, lambda *_: "bad")


def test_controller_rejects_wrong_positive_schema():
    broker = _broker()
    with pytest.raises(ValueError, match="controller_output_schema_invalid"):
        run_non_live_controller(fixtures.invocation("identity_capture"), broker, lambda *_: fixtures.authorization_control())


def test_policy_denied_inventory_is_reported():
    broker = _broker()
    with pytest.raises(ValueError):
        broker.read_source("controller", fixtures.SOURCE_TWO_COLUMN_NAME)
    assert broker.audit_payload()["denied_capabilities"] == ["source_read_exact"]


def test_policy_output_sink_stays_empty_after_denied_run():
    broker = _broker()
    with pytest.raises(ValueError):
        broker.read_source("controller", fixtures.SOURCE_TWO_COLUMN_NAME)
    assert broker.output_sink is None
