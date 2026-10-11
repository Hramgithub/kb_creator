from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from kb_creator.pdf_raw import step5_non_live_contracts as contracts
from kb_creator.pdf_raw.step5_non_live_policy import SyntheticCapabilityBroker
from kb_creator.pdf_raw.step5_non_live_preflight_adapter import run_non_live_page_preflight
from kb_creator.tests import _step5_non_live_fixture_leaves as fixtures

_QUEUE_ROW_KEYS = (
    "artifact_repo_relative_path_literal",
    "content_sha256",
    "hypothesis_literal",
    "item_id",
    "item_id_utf8_hex",
    "item_row_sha256",
    "metadata_source_row_ordinal",
    "queue_order",
    "selected_page_index",
    "status_literal",
)
_ELIGIBILITY_RESULT_KEYS = (
    "content_sha256",
    "eligible",
    "item_id",
    "reasons",
)
_SELECTION_REPLAY_KEYS = (
    "content_sha256",
    "replay_terminal",
    "selected_array_index",
    "selected_item_id",
)
_QUEUE_BINDING_KEYS = (
    "content_sha256",
    "logical_content_sha256",
    "raw_byte_length",
    "raw_file_sha256",
    "schema",
    "virtual_name",
)
_QUEUE_KEYS = (
    "content_sha256",
    "eligibility_filter",
    "eligibility_result_sha256",
    "eligibility_results",
    "ordered_eligible_preimage",
    "ordering_preimage_sha256",
    "ordering_rule",
    "queue_authority_binding",
    "queue_snapshot_sha256",
    "schema",
    "selected_candidate_preimage",
    "selection_replay_result",
    "snapshot_record_count",
    "snapshot_row_hash_inventory",
    "snapshot_rows",
)
_AUTHORIZATION_KEYS = (
    "authorization_scope",
    "content_sha256",
    "control_kind",
    "control_record_virtual_name",
    "exact_argv",
    "execution_profile",
    "phase",
    "prerequisite_qa",
    "prerequisite_qa_sha256",
    "queue_selection_proof",
    "schema",
    "selected_item_row_sha256",
    "selected_page_index",
    "selection_sha256",
    "source_identity_sha256",
    "source_virtual_name",
)
_PROOF_KEYS = (
    "block_count",
    "block_inventory",
    "boundary_count",
    "boundary_decisions",
    "candidate_core_sha256",
    "conservation",
    "content_sha256",
    "evidence_core_sha256",
    "fragment_count",
    "fragment_inventory",
    "reading_order_permutation",
    "replay",
    "schema",
    "selected_page_index",
    "source_identity_sha256",
    "stable_reason_codes",
    "stage_a_authority_sha256",
    "terminal_state",
    "visual_crosscheck_sha256",
)
_VISUAL_KEYS = (
    "block_inventory_sha256",
    "boundary_inventory_sha256",
    "content_sha256",
    "page_proof_content_sha256",
    "persisted",
    "schema",
    "selected_page_index",
    "source_identity_sha256",
    "terminal_state",
    "witness_sha256",
)
_EVIDENCE_KEYS = (
    "authorization_sha256",
    "content_sha256",
    "decision",
    "eligibility_result_sha256",
    "execution_profile",
    "goal_id",
    "implementation_manifest_sha256",
    "ordering_preimage_sha256",
    "page_proof",
    "policy_audit",
    "prerequisite_qa_sha256",
    "queue_snapshot_sha256",
    "run_id",
    "runtime_identity",
    "selection_sha256",
    "source_identity_after",
    "source_identity_before",
    "source_identity_sha256",
    "stage_a_authority",
    "step_id",
    "synthetic_policy_sha256",
    "synthetic_visual_witness_identity",
    "schema",
    "terminal_state",
)

_IDENTIFIER_BAD_VALUES = (
    "arbitrary plaintext payload",
    "this identifier contains ordinary prose",
    "U0VDUkVUX1BBWUxPQUQ=",
    "D:\\NRI\\Output\\secret.txt",
)


def _broker():
    return SyntheticCapabilityBroker(**fixtures.broker_bundle())


def _oracle_canonical_json(value: object) -> bytes:
    return json.dumps(value, ensure_ascii=True, sort_keys=True, separators=(",", ":")).encode("utf-8")


def _oracle_sha256_hex(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def _oracle_seal_closed(value: dict, keys: tuple[str, ...]) -> bytes:
    if tuple(sorted(value.keys())) != tuple(sorted(keys)):
        raise AssertionError(("oracle_closed_schema_invalid", tuple(sorted(value.keys())), keys))
    unsigned = dict(value)
    unsigned.pop("content_sha256", None)
    unsigned["content_sha256"] = _oracle_sha256_hex(_oracle_canonical_json(unsigned))
    if tuple(sorted(unsigned.keys())) != tuple(sorted(keys)):
        raise AssertionError(("oracle_closed_schema_invalid", tuple(sorted(unsigned.keys())), keys))
    return _oracle_canonical_json(unsigned)


def _oracle_row_item_sha(row: dict) -> str:
    unsigned = dict(row)
    unsigned.pop("content_sha256", None)
    unsigned.pop("item_row_sha256", None)
    return _oracle_sha256_hex(_oracle_canonical_json(unsigned))


def _oracle_reseal_queue_row(row: dict) -> dict:
    updated = dict(row)
    updated["item_row_sha256"] = _oracle_row_item_sha(updated)
    return json.loads(_oracle_seal_closed(updated, _QUEUE_ROW_KEYS))


def _oracle_reseal_eligibility_result(result: dict) -> dict:
    return json.loads(_oracle_seal_closed(dict(result), _ELIGIBILITY_RESULT_KEYS))


def _oracle_reseal_selection_replay(result: dict) -> dict:
    return json.loads(_oracle_seal_closed(dict(result), _SELECTION_REPLAY_KEYS))


def _oracle_queue_authority_raw(snapshot_rows: list[dict]) -> bytes:
    return _oracle_canonical_json(
        {
            "queue_name": fixtures.QUEUE_NAME,
            "row_ids": [row["item_id"] for row in snapshot_rows],
            "schema": "kb_creator.pdf_raw.Step5SyntheticQueueAuthorityFile.v1",
        }
    )


def _oracle_reseal_queue_binding(queue_raw: bytes) -> dict:
    return json.loads(
        _oracle_seal_closed(
            {
                "content_sha256": "0" * 64,
                "logical_content_sha256": _oracle_sha256_hex(queue_raw),
                "raw_byte_length": len(queue_raw),
                "raw_file_sha256": _oracle_sha256_hex(queue_raw),
                "schema": "kb_creator.pdf_raw.Step5SyntheticQueueAuthorityBinding.v1",
                "virtual_name": fixtures.QUEUE_NAME,
            },
            _QUEUE_BINDING_KEYS,
        )
    )


def _oracle_reseal_queue_graph(control: dict) -> tuple[dict, bytes]:
    queue = json.loads(_oracle_canonical_json(control["queue_selection_proof"]))
    queue["snapshot_rows"] = [_oracle_reseal_queue_row(row) for row in queue["snapshot_rows"]]
    queue["snapshot_row_hash_inventory"] = [row["item_row_sha256"] for row in queue["snapshot_rows"]]
    queue["snapshot_record_count"] = len(queue["snapshot_rows"])
    queue["eligibility_results"] = [_oracle_reseal_eligibility_result(result) for result in queue["eligibility_results"]]
    eligible_rows = [row for row, result in zip(queue["snapshot_rows"], queue["eligibility_results"]) if result["eligible"]]
    queue["ordered_eligible_preimage"] = eligible_rows
    queue["selected_candidate_preimage"] = eligible_rows[0]
    queue["selection_replay_result"]["selected_item_id"] = eligible_rows[0]["item_id"]
    queue["selection_replay_result"] = _oracle_reseal_selection_replay(queue["selection_replay_result"])
    queue_raw = _oracle_queue_authority_raw(queue["snapshot_rows"])
    queue["queue_authority_binding"] = _oracle_reseal_queue_binding(queue_raw)
    queue["queue_snapshot_sha256"] = _oracle_sha256_hex(_oracle_canonical_json(queue["snapshot_rows"]))
    queue["eligibility_result_sha256"] = _oracle_sha256_hex(_oracle_canonical_json(queue["eligibility_results"]))
    queue["ordering_preimage_sha256"] = _oracle_sha256_hex(_oracle_canonical_json(queue["ordered_eligible_preimage"]))
    control["queue_selection_proof"] = json.loads(_oracle_seal_closed(queue, _QUEUE_KEYS))
    control["selected_item_row_sha256"] = control["queue_selection_proof"]["selected_candidate_preimage"]["item_row_sha256"]
    return control, queue_raw


def _oracle_reseal_authorization(control: dict) -> tuple[bytes, bytes]:
    updated = json.loads(_oracle_canonical_json(control))
    updated, queue_raw = _oracle_reseal_queue_graph(updated)
    return _oracle_seal_closed(updated, _AUTHORIZATION_KEYS), queue_raw


def _oracle_reseal_page_proof_graph(payload: dict) -> bytes:
    proof = json.loads(_oracle_canonical_json(payload["page_proof"]))
    payload["page_proof"] = json.loads(_oracle_seal_closed(proof, _PROOF_KEYS))
    visual = json.loads(_oracle_canonical_json(payload["synthetic_visual_witness_identity"]))
    visual["block_inventory_sha256"] = _oracle_sha256_hex(_oracle_canonical_json(payload["page_proof"]["block_inventory"]))
    visual["boundary_inventory_sha256"] = _oracle_sha256_hex(_oracle_canonical_json(payload["page_proof"]["boundary_decisions"]))
    visual["page_proof_content_sha256"] = payload["page_proof"]["content_sha256"]
    payload["synthetic_visual_witness_identity"] = json.loads(_oracle_seal_closed(visual, _VISUAL_KEYS))
    return _oracle_seal_closed(payload, _EVIDENCE_KEYS)


def _baseline_preflight_bytes() -> bytes:
    return run_non_live_page_preflight(fixtures.invocation("page_preflight"), _broker(), fixtures.ProofProtocol())


def _baseline_authorization_bytes() -> bytes:
    return fixtures.authorization_control()


def _assert_repaired_bytes(match_bytes: bytes, repaired_bytes: bytes) -> None:
    assert repaired_bytes == match_bytes


def test_missing_closed_protocol_precedes_stage_a():
    failure = json.loads(run_non_live_page_preflight(fixtures.invocation("page_preflight"), _broker(), None))
    assert failure["error_code"] == "preflight_rejected_render_contract_unresolved"


def test_legacy_run_only_callable_is_rejected():
    class Legacy:
        def run(self, *_args):
            return {}

    failure = json.loads(run_non_live_page_preflight(fixtures.invocation("page_preflight"), _broker(), Legacy()))
    assert failure["error_code"] == "preflight_rejected_render_contract_unresolved"


def test_closed_three_stage_protocol_positive():
    payload = contracts.validate_preflight_evidence(run_non_live_page_preflight(fixtures.invocation("page_preflight"), _broker(), fixtures.ProofProtocol()))
    assert payload["terminal_state"] == "synthetic_preflight_evidence_only_no_live_authority"


def test_stage_a_binding_target_first():
    class Bad(fixtures.ProofProtocol):
        def run_stage_a(self, selected_page_index, source_identity_binding):
            stage_a = super().run_stage_a(selected_page_index, source_identity_binding)
            stage_a["source_identity_sha256"] = "0" * 64
            return contracts.sealed_dict(stage_a, contracts._STAGE_A_KEYS)

    failure = json.loads(run_non_live_page_preflight(fixtures.invocation("page_preflight"), _broker(), Bad()))
    assert failure["error_code"] == "stage_a_invalid"


def test_page_proof_binding_target_first():
    class Bad(fixtures.ProofProtocol):
        def run_page_proof(self, stage_a_authority, source_identity_binding):
            proof = super().run_page_proof(stage_a_authority, source_identity_binding)
            proof["stage_a_authority_sha256"] = "0" * 64
            return contracts.sealed_dict(proof, contracts._PROOF_KEYS)

    failure = json.loads(run_non_live_page_preflight(fixtures.invocation("page_preflight"), _broker(), Bad()))
    assert failure["error_code"] == "page_proof_invalid"


def test_visual_witness_binding_target_first():
    class Bad(fixtures.ProofProtocol):
        def run_visual_witness(self, page_proof_core, source_identity_binding):
            visual = super().run_visual_witness(page_proof_core, source_identity_binding)
            visual["page_proof_content_sha256"] = "0" * 64
            return contracts.sealed_dict(visual, contracts._VISUAL_KEYS)

    failure = json.loads(run_non_live_page_preflight(fixtures.invocation("page_preflight"), _broker(), Bad()))
    assert failure["error_code"] == "visual_witness_invalid"


def test_conservation_target_first_reseal():
    class Bad(fixtures.ProofProtocol):
        def run_page_proof(self, stage_a_authority, source_identity_binding):
            proof = super().run_page_proof(stage_a_authority, source_identity_binding)
            proof["conservation"]["complete_visual_binding"] = False
            return contracts.sealed_dict(proof, contracts._PROOF_KEYS)

    failure = json.loads(run_non_live_page_preflight(fixtures.invocation("page_preflight"), _broker(), Bad()))
    assert failure["error_code"] == "page_proof_invalid"


def test_replay_target_first_reseal():
    class Bad(fixtures.ProofProtocol):
        def run_page_proof(self, stage_a_authority, source_identity_binding):
            proof = super().run_page_proof(stage_a_authority, source_identity_binding)
            proof["replay"]["mismatch_count"] = 1
            return contracts.sealed_dict(proof, contracts._PROOF_KEYS)

    failure = json.loads(run_non_live_page_preflight(fixtures.invocation("page_preflight"), _broker(), Bad()))
    assert failure["error_code"] == "page_proof_invalid"


def test_audit_completeness_target_first_reseal():
    broker = _broker()
    payload = contracts.validate_preflight_evidence(run_non_live_page_preflight(fixtures.invocation("page_preflight"), broker, fixtures.ProofProtocol()))
    assert payload["policy_audit"]["event_count"] == 12


def test_plaintext_secret_resealed_is_rejected():
    class Bad(fixtures.ProofProtocol):
        def run_visual_witness(self, page_proof_core, source_identity_binding):
            visual = super().run_visual_witness(page_proof_core, source_identity_binding)
            visual["secret"] = "secret"
            return contracts.sealed_dict(visual, tuple(list(contracts._VISUAL_KEYS) + ["secret"]))

    failure = json.loads(run_non_live_page_preflight(fixtures.invocation("page_preflight"), _broker(), Bad()))
    assert failure["error_code"] == "closed_schema_invalid"


@pytest.mark.parametrize(
    "mutation",
    [
        "plaintext_equal_pair",
        "unknown_key_equal_pair",
    ],
)
def test_source_identity_resealed_adversary(mutation):
    payload = json.loads(_baseline_preflight_bytes())
    if mutation == "plaintext_equal_pair":
        payload["source_identity_before"] = {"secret": "plaintext"}
        payload["source_identity_after"] = {"secret": "plaintext"}
    else:
        source_identity = json.loads(contracts.canonical_json(payload["source_identity_before"]))
        source_identity["unexpected"] = "plaintext"
        keys = tuple(sorted((*contracts._SOURCE_IDENTITY_KEYS, "unexpected")))
        payload["source_identity_before"] = contracts.sealed_dict(source_identity, keys)
        payload["source_identity_after"] = contracts.sealed_dict(source_identity, keys)
    payload = contracts.seal_closed(payload, contracts._EVIDENCE_KEYS)
    with pytest.raises(ValueError, match="source_identity_schema_invalid"):
        contracts.validate_preflight_evidence(payload)


def test_payload_leak_target_first_reseal():
    class Bad(fixtures.ProofProtocol):
        def run_stage_a(self, selected_page_index, source_identity_binding):
            stage_a = super().run_stage_a(selected_page_index, source_identity_binding)
            stage_a["ordered_row_hash_inventory"] = ["%PDF-leak"]
            return contracts.sealed_dict(stage_a, contracts._STAGE_A_KEYS)

    failure = json.loads(run_non_live_page_preflight(fixtures.invocation("page_preflight"), _broker(), Bad()))
    assert failure["error_code"] == "stage_a_invalid"


def test_preflight_source_post_read_drift():
    class DriftBroker(SyntheticCapabilityBroker):
        def __init__(self):
            super().__init__(**fixtures.broker_bundle())
            self._drift = False

        def read_source(self, subject, name):
            value = super().read_source(subject, name)
            if not self._drift:
                self.sources[name]["bytes"] = value + b"x"
                self._drift = True
            return value

    failure = json.loads(run_non_live_page_preflight(fixtures.invocation("page_preflight"), DriftBroker(), fixtures.ProofProtocol()))
    assert failure["error_code"] == "source_post_read_drift"


def test_preflight_binds_authorization_source_identity():
    bundle = fixtures.broker_bundle()
    control = json.loads(fixtures.authorization_control())
    control["source_identity_sha256"] = "0" * 64
    control_raw = contracts.seal_closed(control, contracts._AUTHORIZATION_KEYS)
    bundle["controls"][fixtures.AUTHORIZATION_CONTROL_NAME] = control_raw
    invocation = json.loads(fixtures.invocation("page_preflight"))
    invocation["control_record_byte_length"] = len(control_raw)
    invocation["control_record_file_sha256"] = contracts.sha256_hex(control_raw)
    invocation["control_record_content_sha256"] = contracts._load_canonical_json(control_raw)["content_sha256"]
    invocation_raw = contracts.seal_closed(invocation, contracts._INVOCATION_KEYS)
    failure = json.loads(run_non_live_page_preflight(invocation_raw, SyntheticCapabilityBroker(**bundle), fixtures.ProofProtocol()))
    assert failure["error_code"] == "source_identity_sha256_invalid"


def test_preflight_runtime_identity_is_closed():
    payload = contracts.validate_preflight_evidence(_baseline_preflight_bytes())
    assert payload["runtime_identity"]["schema"] == contracts.RUNTIME_IDENTITY_SCHEMA


def test_preflight_records_all_three_proof_calls():
    broker = _broker()
    run_non_live_page_preflight(fixtures.invocation("page_preflight"), broker, fixtures.ProofProtocol())
    caps = [event["capability"] for event in broker.audit_payload()["events"]]
    assert caps[6:9] == ["proof_stage_a", "proof_page_proof", "proof_visual_witness"]


def test_preflight_selection_sha_propagates():
    payload = contracts.validate_preflight_evidence(_baseline_preflight_bytes())
    assert payload["selection_sha256"] == contracts._load_canonical_json(fixtures.authorization_control())["selection_sha256"]


def test_preflight_queue_hashes_propagate():
    payload = contracts.validate_preflight_evidence(_baseline_preflight_bytes())
    queue = contracts._load_canonical_json(fixtures.authorization_control())["queue_selection_proof"]
    assert payload["queue_snapshot_sha256"] == queue["queue_snapshot_sha256"]


def test_preflight_negative_decision_is_literal():
    payload = contracts.validate_preflight_evidence(_baseline_preflight_bytes())
    assert payload["decision"]["live_authority"] is False


def test_preflight_visual_identity_not_persisted():
    payload = contracts.validate_preflight_evidence(_baseline_preflight_bytes())
    assert payload["synthetic_visual_witness_identity"]["persisted"] is False


def test_preflight_stage_a_inventory_count_matches_rows():
    payload = contracts.validate_preflight_evidence(_baseline_preflight_bytes())
    assert payload["stage_a_authority"]["row_count"] == 2


def test_identifier_run_id_target_first_resealed_closed_values():
    baseline_raw = _baseline_preflight_bytes()
    baseline = json.loads(baseline_raw)
    for invalid_value in _IDENTIFIER_BAD_VALUES:
        payload = json.loads(_oracle_canonical_json(baseline))
        payload["run_id"] = invalid_value
        mutated_raw = _oracle_seal_closed(payload, _EVIDENCE_KEYS)
        with pytest.raises(ValueError, match="run_id_invalid"):
            contracts.validate_preflight_evidence(mutated_raw)
        repaired = json.loads(_oracle_canonical_json(payload))
        repaired["run_id"] = baseline["run_id"]
        repaired_raw = _oracle_seal_closed(repaired, _EVIDENCE_KEYS)
        _assert_repaired_bytes(baseline_raw, repaired_raw)
        assert contracts.validate_preflight_evidence(repaired_raw)["run_id"] == baseline["run_id"]


def test_identifier_item_id_target_first_resealed_closed_values():
    baseline_raw = _baseline_authorization_bytes()
    baseline = json.loads(baseline_raw)
    invocation = json.loads(fixtures.invocation("page_preflight"))
    for invalid_value in _IDENTIFIER_BAD_VALUES:
        control = json.loads(_oracle_canonical_json(baseline))
        row = control["queue_selection_proof"]["snapshot_rows"][0]
        row["item_id"] = invalid_value
        row["item_id_utf8_hex"] = invalid_value.encode("utf-8").hex()
        result = control["queue_selection_proof"]["eligibility_results"][0]
        result["item_id"] = invalid_value
        selected = control["queue_selection_proof"]["selected_candidate_preimage"]
        selected["item_id"] = invalid_value
        selected["item_id_utf8_hex"] = invalid_value.encode("utf-8").hex()
        control["queue_selection_proof"]["ordered_eligible_preimage"][0]["item_id"] = invalid_value
        control["queue_selection_proof"]["ordered_eligible_preimage"][0]["item_id_utf8_hex"] = invalid_value.encode("utf-8").hex()
        control["queue_selection_proof"]["selection_replay_result"]["selected_item_id"] = invalid_value
        mutated_raw, queue_raw = _oracle_reseal_authorization(control)
        with pytest.raises(ValueError, match="item_id_invalid"):
            contracts.validate_authorization_control(mutated_raw, invocation, queue_raw)
        repaired_raw, repaired_queue_raw = _oracle_reseal_authorization(json.loads(_oracle_canonical_json(baseline)))
        _assert_repaired_bytes(baseline_raw, repaired_raw)
        assert contracts.validate_authorization_control(repaired_raw, invocation, repaired_queue_raw)["selected_item_row_sha256"] == baseline["selected_item_row_sha256"]


def test_identifier_block_id_target_first_resealed_closed_values():
    baseline_raw = _baseline_preflight_bytes()
    baseline = json.loads(baseline_raw)
    for invalid_value in _IDENTIFIER_BAD_VALUES:
        payload = json.loads(_oracle_canonical_json(baseline))
        payload["page_proof"]["block_inventory"][0]["block_id"] = invalid_value
        mutated_raw = _oracle_reseal_page_proof_graph(payload)
        with pytest.raises(ValueError, match="block_id_invalid"):
            contracts.validate_preflight_evidence(mutated_raw)
        repaired_raw = _oracle_reseal_page_proof_graph(json.loads(_oracle_canonical_json(baseline)))
        _assert_repaired_bytes(baseline_raw, repaired_raw)
        assert contracts.validate_preflight_evidence(repaired_raw)["page_proof"]["block_inventory"][0]["block_id"] == "b1"


def test_identifier_fragment_id_target_first_resealed_closed_values():
    baseline_raw = _baseline_preflight_bytes()
    baseline = json.loads(baseline_raw)
    for invalid_value in _IDENTIFIER_BAD_VALUES:
        payload = json.loads(_oracle_canonical_json(baseline))
        payload["page_proof"]["fragment_inventory"][0]["fragment_id"] = invalid_value
        mutated_raw = _oracle_reseal_page_proof_graph(payload)
        with pytest.raises(ValueError, match="fragment_id_invalid"):
            contracts.validate_preflight_evidence(mutated_raw)
        repaired_raw = _oracle_reseal_page_proof_graph(json.loads(_oracle_canonical_json(baseline)))
        _assert_repaired_bytes(baseline_raw, repaired_raw)
        assert contracts.validate_preflight_evidence(repaired_raw)["page_proof"]["fragment_inventory"][0]["fragment_id"] == "f1"


def test_identifier_boundary_id_target_first_resealed_closed_values():
    baseline_raw = _baseline_preflight_bytes()
    baseline = json.loads(baseline_raw)
    for invalid_value in _IDENTIFIER_BAD_VALUES:
        payload = json.loads(_oracle_canonical_json(baseline))
        payload["page_proof"]["boundary_decisions"][0]["boundary_id"] = invalid_value
        mutated_raw = _oracle_reseal_page_proof_graph(payload)
        with pytest.raises(ValueError, match="boundary_id_invalid"):
            contracts.validate_preflight_evidence(mutated_raw)
        repaired_raw = _oracle_reseal_page_proof_graph(json.loads(_oracle_canonical_json(baseline)))
        _assert_repaired_bytes(baseline_raw, repaired_raw)
        assert contracts.validate_preflight_evidence(repaired_raw)["page_proof"]["boundary_decisions"][0]["boundary_id"] == "bd1"


def test_page_proof_block_id_ordinal_mapping_target_first_fully_resealed():
    baseline_raw = _baseline_preflight_bytes()
    baseline = json.loads(baseline_raw)
    payload = json.loads(_oracle_canonical_json(baseline))
    payload["page_proof"]["block_inventory"] = [{"block_id": "b2", "ordinal": 0}, {"block_id": "b1", "ordinal": 1}]
    mutated_raw = _oracle_reseal_page_proof_graph(payload)
    with pytest.raises(ValueError, match="page_proof_invalid"):
        contracts.validate_preflight_evidence(mutated_raw)
    payload["page_proof"]["block_inventory"] = json.loads(_oracle_canonical_json(baseline["page_proof"]["block_inventory"]))
    repaired_raw = _oracle_reseal_page_proof_graph(payload)
    _assert_repaired_bytes(baseline_raw, repaired_raw)
    repaired = contracts.validate_preflight_evidence(repaired_raw)
    assert tuple((row["block_id"], row["ordinal"]) for row in repaired["page_proof"]["block_inventory"]) == (("b1", 0), ("b2", 1))


def test_page_proof_fragment_id_ordinal_mapping_target_first_fully_resealed():
    baseline_raw = _baseline_preflight_bytes()
    baseline = json.loads(baseline_raw)
    payload = json.loads(_oracle_canonical_json(baseline))
    payload["page_proof"]["fragment_inventory"] = [{"fragment_id": "f2", "ordinal": 0}, {"fragment_id": "f1", "ordinal": 1}]
    mutated_raw = _oracle_reseal_page_proof_graph(payload)
    with pytest.raises(ValueError, match="page_proof_invalid"):
        contracts.validate_preflight_evidence(mutated_raw)
    payload["page_proof"]["fragment_inventory"] = json.loads(_oracle_canonical_json(baseline["page_proof"]["fragment_inventory"]))
    repaired_raw = _oracle_reseal_page_proof_graph(payload)
    _assert_repaired_bytes(baseline_raw, repaired_raw)
    repaired = contracts.validate_preflight_evidence(repaired_raw)
    assert tuple((row["fragment_id"], row["ordinal"]) for row in repaired["page_proof"]["fragment_inventory"]) == (("f1", 0), ("f2", 1))


def test_page_proof_boundary_id_decision_mapping_target_first_fully_resealed():
    baseline_raw = _baseline_preflight_bytes()
    baseline = json.loads(baseline_raw)
    payload = json.loads(_oracle_canonical_json(baseline))
    payload["page_proof"]["boundary_decisions"] = [{"boundary_id": "bd1", "decision": "forbidden"}]
    mutated_raw = _oracle_reseal_page_proof_graph(payload)
    with pytest.raises(ValueError, match="page_proof_invalid"):
        contracts.validate_preflight_evidence(mutated_raw)
    payload["page_proof"]["boundary_decisions"] = json.loads(_oracle_canonical_json(baseline["page_proof"]["boundary_decisions"]))
    repaired_raw = _oracle_reseal_page_proof_graph(payload)
    _assert_repaired_bytes(baseline_raw, repaired_raw)
    repaired = contracts.validate_preflight_evidence(repaired_raw)
    assert tuple((row["boundary_id"], row["decision"]) for row in repaired["page_proof"]["boundary_decisions"]) == (("bd1", "keep"),)


def test_visual_inventory_hash_binding_target_first_fully_resealed():
    baseline_raw = _baseline_preflight_bytes()
    baseline = json.loads(baseline_raw)
    reversed_blocks = [{"block_id": "b2", "ordinal": 0}, {"block_id": "b1", "ordinal": 1}]
    for field_name, replacement in (
        ("block_inventory_sha256", _oracle_sha256_hex(_oracle_canonical_json(reversed_blocks))),
        ("boundary_inventory_sha256", _oracle_sha256_hex(_oracle_canonical_json([{"boundary_id": "bd1", "decision": "forbidden"}]))),
    ):
        payload = json.loads(_oracle_canonical_json(baseline))
        payload["synthetic_visual_witness_identity"][field_name] = replacement
        visual = payload["synthetic_visual_witness_identity"]
        payload["synthetic_visual_witness_identity"] = json.loads(_oracle_seal_closed(visual, _VISUAL_KEYS))
        mutated_raw = _oracle_seal_closed(payload, _EVIDENCE_KEYS)
        with pytest.raises(ValueError, match="visual_witness_invalid"):
            contracts.validate_preflight_evidence(mutated_raw)
        repaired_payload = json.loads(_oracle_canonical_json(payload))
        repaired_payload["synthetic_visual_witness_identity"][field_name] = baseline["synthetic_visual_witness_identity"][field_name]
        repaired_raw = _oracle_reseal_page_proof_graph(repaired_payload)
        _assert_repaired_bytes(baseline_raw, repaired_raw)
        repaired = contracts.validate_preflight_evidence(repaired_raw)
        assert repaired["synthetic_visual_witness_identity"][field_name] == baseline["synthetic_visual_witness_identity"][field_name]
