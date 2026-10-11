from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from kb_creator.pdf_raw import step5_non_live_contracts as contracts
from kb_creator.tests import _step5_non_live_fixture_leaves as fixtures


def _selection_invocation():
    return contracts.validate_invocation(fixtures.invocation("identity_capture"), "identity_capture")


def _authorization_invocation():
    return contracts.validate_invocation(fixtures.invocation("page_preflight"), "page_preflight")


def test_closed_virtual_name_registry():
    assert contracts.VIRTUAL_REGISTRY == (
        fixtures.SOURCE_TWO_COLUMN_NAME,
        fixtures.SOURCE_NESTED_FORM_NAME,
        fixtures.QUEUE_NAME,
        fixtures.SELECTION_CONTROL_NAME,
        fixtures.AUTHORIZATION_CONTROL_NAME,
    )


def test_control_file_and_content_bindings_target_first():
    control_raw = fixtures.selection_control()
    invocation = json.loads(fixtures.invocation("identity_capture"))
    invocation["control_record_content_sha256"] = "0" * 64
    raw = contracts.canonical_json(invocation)
    with pytest.raises(ValueError, match="invocation_seal_invalid"):
        contracts.validate_invocation(raw, "identity_capture")
    valid = contracts.validate_selection_control(control_raw, _selection_invocation(), fixtures.queue_authority_raw())
    assert valid["content_sha256"] != contracts.sha256_hex(control_raw)


def test_prerequisite_six_command_baseline_replays():
    prerequisite = fixtures.prerequisite()
    assert [row["command_id"] for row in prerequisite["command_records"]] == [
        "page_proof_py_compile",
        "page_proof_collect_159",
        "page_proof_execute_159",
        "stage_a_topology_execute_15",
        "stage_a_aggregate_execute_386_plus_1_skip",
        "inactive_root_public_poison_target",
    ]
    assert contracts.validate_prerequisite(prerequisite)["content_sha256"] == prerequisite["content_sha256"]


def test_prerequisite_actual_result_correspondence_target_first_resealed():
    prerequisite = json.loads(contracts.canonical_json(fixtures.prerequisite()))
    prerequisite["command_records"][0]["actual_result"] = {"compiled": 999}
    prerequisite["command_records"][0] = contracts.sealed_dict(prerequisite["command_records"][0], contracts._COMMAND_RECORD_KEYS)
    prerequisite = contracts.sealed_dict(prerequisite, contracts._PREREQUISITE_KEYS)
    with pytest.raises(ValueError, match="prerequisite_actual_result_invalid"):
        contracts.validate_prerequisite(prerequisite)


@pytest.mark.parametrize(
    ("mutation", "field"),
    [
        ("command_omitted", ("command_records", 0)),
        ("command_duplicated", ("command_records", 1)),
        ("command_reordered", ("command_records", 2)),
        ("argv_drift", ("command_records", 3, "exact_argv")),
        ("missing_isolated_or_no_bytecode", ("command_records", 4, "exact_argv")),
        ("cache_enabled", ("command_records", 5, "exact_argv")),
        ("cwd_runtime_manifest_drift", ("cwd",)),
        ("count_or_skip_drift", ("aggregate_result", "stage_a_aggregate_execute_386_plus_1_skip", "skipped")),
        ("target_node_or_claim_drift", ("aggregate_result", "inactive_root_public_poison_target", "passed")),
        ("stdout_stderr_or_parser_drift", ("command_records", 0, "stdout_byte_length")),
    ],
)
def test_prerequisite_target_first_reseal(mutation, field):
    prerequisite = json.loads(contracts.canonical_json(fixtures.prerequisite()))
    if mutation == "command_omitted":
        prerequisite["command_records"].pop(0)
    elif mutation == "command_duplicated":
        prerequisite["command_records"].append(prerequisite["command_records"][0])
    elif mutation == "command_reordered":
        prerequisite["command_records"][0], prerequisite["command_records"][1] = prerequisite["command_records"][1], prerequisite["command_records"][0]
    elif mutation in {"argv_drift", "missing_isolated_or_no_bytecode", "cache_enabled"}:
        prerequisite[field[0]][field[1]][field[2]][1] = "-X"
    elif mutation == "cwd_runtime_manifest_drift":
        prerequisite["cwd"] = "D:\\OTHER"
    elif mutation == "count_or_skip_drift":
        prerequisite["aggregate_result"]["stage_a_aggregate_execute_386_plus_1_skip"]["skipped"] = 0
    elif mutation == "target_node_or_claim_drift":
        prerequisite["aggregate_result"]["inactive_root_public_poison_target"]["passed"] = 0
    else:
        prerequisite["command_records"][0]["stdout_byte_length"] = 7
    prerequisite = contracts.sealed_dict(prerequisite, contracts._PREREQUISITE_KEYS)
    with pytest.raises(ValueError):
        contracts.validate_prerequisite(prerequisite)


def test_prerequisite_selection_authorization_byte_equivalence():
    selection = contracts._load_canonical_json(fixtures.selection_control())
    authorization = contracts._load_canonical_json(fixtures.authorization_control())
    assert selection["prerequisite_qa"] == authorization["prerequisite_qa"]
    assert selection["prerequisite_qa_sha256"] == authorization["prerequisite_qa_sha256"]


def test_queue_complete_four_key_element_zero_replay():
    queue = fixtures.queue_proof()
    assert queue["selected_candidate_preimage"] == queue["ordered_eligible_preimage"][0]
    assert queue["selection_replay_result"]["selected_array_index"] == 0
    assert contracts.validate_queue(queue)["content_sha256"] == queue["content_sha256"]


@pytest.mark.parametrize(
    "mutation",
    [
        "row_hash_or_inventory",
        "earlier_row_omitted",
        "duplicate_item_or_ordinal",
        "utf8_or_unicode_normalization",
        "status_hypothesis_or_page",
        "forbidden_artifact",
        "reason_vector",
        "ordering_or_dropped_eligible",
        "nonzero_selected_index",
        "authority_drift_refresh_or_reselection",
    ],
)
def test_queue_target_first_reseal(mutation):
    queue = json.loads(contracts.canonical_json(fixtures.queue_proof()))
    if mutation == "row_hash_or_inventory":
        queue["snapshot_rows"][0]["item_row_sha256"] = "0" * 64
        queue["snapshot_rows"][0] = contracts.sealed_dict(queue["snapshot_rows"][0], contracts._QUEUE_ROW_KEYS)
        queue["snapshot_row_hash_inventory"][0] = "0" * 64
    elif mutation == "earlier_row_omitted":
        queue["snapshot_rows"].pop(0)
    elif mutation == "duplicate_item_or_ordinal":
        queue["snapshot_rows"][1]["item_id"] = queue["snapshot_rows"][0]["item_id"]
    elif mutation == "utf8_or_unicode_normalization":
        queue["snapshot_rows"][0]["item_id_utf8_hex"] = "zz"
    elif mutation == "status_hypothesis_or_page":
        queue["snapshot_rows"][0]["selected_page_index"] = 1
    elif mutation == "forbidden_artifact":
        queue["snapshot_rows"][0]["artifact_repo_relative_path_literal"] = "Output\\forbidden.json"
    elif mutation == "reason_vector":
        queue["eligibility_results"][0]["reasons"] = ["mutated"]
    elif mutation == "ordering_or_dropped_eligible":
        queue["ordered_eligible_preimage"] = []
    elif mutation == "nonzero_selected_index":
        queue["selection_replay_result"]["selected_array_index"] = 1
    else:
        queue["queue_authority_binding"]["virtual_name"] = "fixture://step5/queue/other.v1"
    queue = contracts.sealed_dict(queue, contracts._QUEUE_KEYS)
    with pytest.raises(ValueError):
        contracts.validate_queue(queue)


def test_contract_selection_requires_literal_control_name():
    invocation = json.loads(fixtures.invocation("identity_capture"))
    invocation["control_record_virtual_name"] = "fixture://step5/control/other.v1"
    raw = contracts.canonical_json(invocation)
    with pytest.raises(ValueError, match="control_record_virtual_name_invalid"):
        contracts.validate_invocation(raw, "identity_capture")


def test_contract_authorization_requires_literal_scope():
    control = json.loads(fixtures.authorization_control())
    control["authorization_scope"] = "other"
    raw = contracts.seal_closed(control, contracts._AUTHORIZATION_KEYS)
    with pytest.raises(ValueError, match="authorization_scope_invalid"):
        contracts.validate_authorization_control(raw, _authorization_invocation(), fixtures.queue_authority_raw())


def test_contract_source_name_must_be_exact_literal():
    invocation = json.loads(fixtures.invocation("identity_capture"))
    invocation["source_virtual_name"] = "fixture://step5/source/selected-page.v1"
    raw = contracts.canonical_json(invocation)
    with pytest.raises(ValueError, match="source_virtual_name_invalid"):
        contracts.validate_invocation(raw, "identity_capture")


def test_contract_selection_page_and_selected_row_cross_bind():
    control = json.loads(fixtures.selection_control())
    control["selected_item_row_sha256"] = "0" * 64
    raw = contracts.seal_closed(control, contracts._SELECTION_KEYS)
    with pytest.raises(ValueError, match="selected_item_row_sha256_invalid"):
        contracts.validate_selection_control(raw, _selection_invocation(), fixtures.queue_authority_raw())


def test_contract_authorization_selection_sha_must_be_hash():
    control = json.loads(fixtures.authorization_control())
    control["selection_sha256"] = "not-a-sha"
    raw = contracts.seal_closed(control, contracts._AUTHORIZATION_KEYS)
    with pytest.raises(ValueError, match="selection_sha256_invalid"):
        contracts.validate_authorization_control(raw, _authorization_invocation(), fixtures.queue_authority_raw())


def test_contract_policy_digest_must_match_embedded_policy():
    invocation = json.loads(fixtures.invocation("identity_capture"))
    invocation["synthetic_policy_sha256"] = "0" * 64
    raw = contracts.seal_closed(invocation, contracts._INVOCATION_KEYS)
    with pytest.raises(ValueError, match="synthetic_policy_sha256_invalid"):
        contracts.validate_invocation(raw, "identity_capture")


def test_contract_expected_output_schema_is_phase_exact():
    invocation = json.loads(fixtures.invocation("identity_capture"))
    invocation["expected_output_schema"] = contracts.EVIDENCE_SCHEMA
    raw = contracts.seal_closed(invocation, contracts._INVOCATION_KEYS)
    with pytest.raises(ValueError, match="expected_output_schema_invalid"):
        contracts.validate_invocation(raw, "identity_capture")


def test_contract_failure_validator_accepts_closed_failure():
    invocation = _selection_invocation()
    raw = contracts.make_failure(invocation, "selection_schema_invalid", "synthetic_identity_capture_rejected")
    failure = contracts.validate_failure(raw, invocation)
    assert failure["terminal_state"] == "synthetic_identity_capture_rejected"


def test_contract_failure_validator_rejects_unknown_error_code():
    invocation = _selection_invocation()
    failure = json.loads(contracts.make_failure(invocation, "selection_schema_invalid", "synthetic_identity_capture_rejected"))
    failure["error_code"] = "surprise"
    raw = contracts.seal_closed(failure, contracts._FAILURE_KEYS)
    with pytest.raises(ValueError, match="failure_error_code_invalid"):
        contracts.validate_failure(raw, invocation)
