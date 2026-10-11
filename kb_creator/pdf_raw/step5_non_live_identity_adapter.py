from __future__ import annotations

from . import step5_non_live_contracts as contracts

IMPLEMENTATION_BINDING_SHA256 = "5d52f6943ddf55c3808e51f3f8d7d5e557f47ac942969fe7913d51467f6d1e44"


def run_non_live_identity_capture(invocation_raw: bytes, broker) -> bytes:
    invocation = contracts.validate_invocation(invocation_raw, "identity_capture")
    prerequisite_sha = "0" * 64
    try:
        control_raw = broker.read_control("adapter", invocation["control_record_virtual_name"])
        prerequisite_sha = _prerequisite_digest(control_raw)
        if len(control_raw) != invocation["control_record_byte_length"]:
            raise ValueError("control_record_length_invalid")
        if contracts.sha256_hex(control_raw) != invocation["control_record_file_sha256"]:
            raise ValueError("control_record_file_sha256_invalid")
        queue_raw = broker.read_queue("adapter", contracts.QUEUE_NAME)
        selection = contracts.validate_selection_control(control_raw, invocation, queue_raw)
        prerequisite_sha = selection["prerequisite_qa_sha256"]
        if selection["content_sha256"] != invocation["control_record_content_sha256"]:
            raise ValueError("control_record_content_sha256_invalid")
        if invocation["synthetic_policy_sha256"] != broker.policy_sha256():
            raise ValueError("synthetic_policy_denied")
        source_before = broker.read_source("adapter", invocation["source_virtual_name"])
        metadata_before = broker.source_metadata("adapter", invocation["source_virtual_name"])
        identity = broker.structural_identity("adapter", invocation["source_virtual_name"], invocation["selected_page_index"])
        source_after = broker.read_source("adapter", invocation["source_virtual_name"])
        metadata_after = broker.source_metadata("adapter", invocation["source_virtual_name"])
        if source_before != source_after or metadata_before != metadata_after:
            raise ValueError("source_post_read_drift")
        queue = selection["queue_selection_proof"]
        return contracts.seal_closed(
            {
                "adapter_implementation_binding": IMPLEMENTATION_BINDING_SHA256,
                "content_sha256": "0" * 64,
                "decision": {"live_authority": False, "repair_admission": "none", "review_required": True, "source_use": "forbidden"},
                "eligibility_result_sha256": queue["eligibility_result_sha256"],
                "execution_profile": invocation["execution_profile"],
                "goal_id": invocation["goal_id"],
                "crop_box_pdf": identity["crop_box_pdf"],
                "media_box_pdf": identity["media_box_pdf"],
                "ordering_preimage_sha256": queue["ordering_preimage_sha256"],
                "page_count": identity["page_count"],
                "page_identity_sha256": identity["page_identity_sha256"],
                "page_ref": identity["page_ref"],
                "page_tree_route": identity["page_tree_route"],
                "policy_audit_sha256": broker.audit_sha256(),
                "prerequisite_qa_sha256": prerequisite_sha,
                "queue_snapshot_sha256": queue["queue_snapshot_sha256"],
                "rotation_degrees": identity["rotation_degrees"],
                "run_id": invocation["run_id"],
                "selected_item_row_sha256": selection["selected_item_row_sha256"],
                "selected_page_index": invocation["selected_page_index"],
                "selection_sha256": selection["content_sha256"],
                "source_byte_length": len(source_before),
                "source_sha256": contracts.sha256_hex(source_before),
                "source_virtual_name": invocation["source_virtual_name"],
                "step_id": invocation["step_id"],
                "synthetic_metadata_after": metadata_after,
                "synthetic_metadata_before": metadata_before,
                "synthetic_policy_sha256": invocation["synthetic_policy_sha256"],
                "schema": contracts.IDENTITY_SCHEMA,
                "terminal_state": "synthetic_source_identity_only_no_live_authority",
            },
            contracts._IDENTITY_KEYS,
        )
    except ValueError as exc:
        return contracts.make_failure(invocation, str(exc), "synthetic_identity_capture_rejected", prerequisite_sha)


def _prerequisite_digest(control_raw: bytes) -> str:
    try:
        payload = contracts._load_canonical_json(control_raw)
    except ValueError:
        return "0" * 64
    if isinstance(payload.get("prerequisite_qa_sha256"), str):
        return payload["prerequisite_qa_sha256"]
    prerequisite = payload.get("prerequisite_qa")
    if isinstance(prerequisite, dict) and isinstance(prerequisite.get("content_sha256"), str):
        return prerequisite["content_sha256"]
    return "0" * 64
