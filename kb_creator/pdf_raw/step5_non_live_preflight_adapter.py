from __future__ import annotations

from . import step5_non_live_contracts as contracts

IMPLEMENTATION_MANIFEST_SHA256 = "2c8dd274f50ea4515fa4f8f96665ae4df4cbf7ced26d7dba77fb0904264f08ef"


def run_non_live_page_preflight(invocation_raw: bytes, broker, proof_protocol) -> bytes:
    invocation = contracts.validate_invocation(invocation_raw, "page_preflight")
    prerequisite_sha = "0" * 64
    try:
        stage_a_runner, page_proof_runner, visual_runner = _protocol_functions(proof_protocol)
        control_raw = broker.read_control("adapter", invocation["control_record_virtual_name"])
        if len(control_raw) != invocation["control_record_byte_length"]:
            raise ValueError("control_record_length_invalid")
        if contracts.sha256_hex(control_raw) != invocation["control_record_file_sha256"]:
            raise ValueError("control_record_file_sha256_invalid")
        queue_raw = broker.read_queue("adapter", contracts.QUEUE_NAME)
        authorization = contracts.validate_authorization_control(control_raw, invocation, queue_raw)
        prerequisite_sha = authorization["prerequisite_qa_sha256"]
        if authorization["content_sha256"] != invocation["control_record_content_sha256"]:
            raise ValueError("control_record_content_sha256_invalid")
        if invocation["synthetic_policy_sha256"] != broker.policy_sha256():
            raise ValueError("synthetic_policy_denied")
        source_before = broker.read_source("adapter", invocation["source_virtual_name"])
        metadata_before = broker.source_metadata("adapter", invocation["source_virtual_name"])
        identity_before = broker.structural_identity("adapter", invocation["source_virtual_name"], invocation["selected_page_index"])
        if identity_before["content_sha256"] != authorization["source_identity_sha256"]:
            raise ValueError("source_identity_sha256_invalid")
        if broker.assert_public_root_inactive("adapter") != contracts.INACTIVE_PUBLIC_ROOT_TERMINAL:
            raise ValueError("preflight_rejected_render_contract_unresolved")
        stage_a = broker.run_stage_a("adapter", stage_a_runner, invocation["selected_page_index"], identity_before)
        page_proof = broker.run_page_proof("adapter", page_proof_runner, stage_a, identity_before)
        visual = broker.run_visual_witness("adapter", visual_runner, page_proof, identity_before)
        runtime_identity = proof_protocol.runtime_identity()
        source_after = broker.read_source("adapter", invocation["source_virtual_name"])
        metadata_after = broker.source_metadata("adapter", invocation["source_virtual_name"])
        identity_after = broker.structural_identity("adapter", invocation["source_virtual_name"], invocation["selected_page_index"])
        if source_before != source_after or metadata_before != metadata_after or identity_before != identity_after:
            raise ValueError("source_post_read_drift")
        queue = authorization["queue_selection_proof"]
        payload = contracts.seal_closed(
            {
                "authorization_sha256": authorization["content_sha256"],
                "content_sha256": "0" * 64,
                "decision": {
                    "live_authority": False,
                    "production_activation": False,
                    "repair_admission": "none",
                    "review_required": True,
                    "scope": "synthetic_selected_page_preflight_only",
                    "source_use": "forbidden",
                },
                "eligibility_result_sha256": queue["eligibility_result_sha256"],
                "execution_profile": invocation["execution_profile"],
                "goal_id": invocation["goal_id"],
                "implementation_manifest_sha256": IMPLEMENTATION_MANIFEST_SHA256,
                "ordering_preimage_sha256": queue["ordering_preimage_sha256"],
                "page_proof": page_proof,
                "policy_audit": broker.audit_payload(),
                "prerequisite_qa_sha256": prerequisite_sha,
                "queue_snapshot_sha256": queue["queue_snapshot_sha256"],
                "run_id": invocation["run_id"],
                "runtime_identity": runtime_identity,
                "selection_sha256": authorization["selection_sha256"],
                "source_identity_after": identity_after,
                "source_identity_before": identity_before,
                "source_identity_sha256": authorization["source_identity_sha256"],
                "stage_a_authority": stage_a,
                "step_id": invocation["step_id"],
                "synthetic_policy_sha256": invocation["synthetic_policy_sha256"],
                "synthetic_visual_witness_identity": visual,
                "schema": contracts.EVIDENCE_SCHEMA,
                "terminal_state": "synthetic_preflight_evidence_only_no_live_authority",
            },
            contracts._EVIDENCE_KEYS,
        )
        contracts.validate_preflight_evidence(payload)
        return payload
    except ValueError as exc:
        return contracts.make_failure(invocation, str(exc), "synthetic_page_preflight_rejected", prerequisite_sha)


def _protocol_functions(proof_protocol):
    required = ("run_stage_a", "run_page_proof", "run_visual_witness", "runtime_identity")
    if proof_protocol is None or any(not hasattr(proof_protocol, name) or not callable(getattr(proof_protocol, name)) for name in required):
        raise ValueError("preflight_rejected_render_contract_unresolved")
    if hasattr(proof_protocol, "run"):
        raise ValueError("preflight_rejected_render_contract_unresolved")
    return (
        getattr(proof_protocol, "run_stage_a"),
        getattr(proof_protocol, "run_page_proof"),
        getattr(proof_protocol, "run_visual_witness"),
    )
