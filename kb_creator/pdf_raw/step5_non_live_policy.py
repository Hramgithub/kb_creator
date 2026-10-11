from __future__ import annotations

from . import step5_non_live_contracts as contracts


def build_policy() -> dict:
    return contracts.build_policy_dict()


class SyntheticCapabilityBroker:
    def __init__(self, *, controls: dict[str, bytes], queues: dict[str, bytes], sources: dict[str, dict], public_root_poison: str):
        self.policy = build_policy()
        self._validate_bundle(controls, queues, sources, public_root_poison)
        self.controls = {key: bytes(value) for key, value in controls.items()}
        self.queues = {key: bytes(value) for key, value in queues.items()}
        self.sources = {key: {"bytes": bytes(value["bytes"]), "metadata": value["metadata"], "page_identity": value["page_identity"]} for key, value in sources.items()}
        self.public_root_poison = public_root_poison
        self.output_sink: bytes | None = None
        self.poisoned = False
        self._audit_events: list[dict] = []
        self._ordinal = 0

    def _validate_bundle(self, controls, queues, sources, public_root_poison) -> None:
        if tuple(sorted(controls.keys())) != tuple(sorted((contracts.SELECTION_CONTROL_NAME, contracts.AUTHORIZATION_CONTROL_NAME))):
            raise ValueError("synthetic_policy_invalid")
        if tuple(sorted(queues.keys())) != tuple(sorted((contracts.QUEUE_NAME,))):
            raise ValueError("synthetic_policy_invalid")
        if tuple(sorted(sources.keys())) != tuple(sorted(contracts.SOURCE_NAMES)):
            raise ValueError("synthetic_policy_invalid")
        if public_root_poison != contracts.INACTIVE_PUBLIC_ROOT_TERMINAL:
            raise ValueError("synthetic_policy_invalid")

    def _entry(self, subject: str, capability: str, normalized_name: str, requested_access: str, decision: str, matched_policy_entry: str) -> dict:
        self._ordinal += 1
        return contracts.sealed_dict(
            {
                "capability": capability,
                "content_sha256": "0" * 64,
                "decision": decision,
                "matched_policy_entry": matched_policy_entry,
                "normalized_name": normalized_name,
                "ordinal": self._ordinal,
                "requested_access": requested_access,
                "schema": contracts.AUDIT_EVENT_SCHEMA,
                "subject": subject,
            },
            contracts._AUDIT_EVENT_KEYS,
        )

    def _append_event(self, subject: str, capability: str, normalized_name: str, requested_access: str, decision: str) -> None:
        if decision == "deny":
            match_id = "deny:default"
        elif decision == "deny_run_poisoned":
            match_id = "deny:poisoned"
        else:
            match_id = f"{subject}:{capability}"
        event = self._entry(subject, capability, normalized_name, requested_access, decision, match_id)
        self._audit_events.append(event)

    def _check_poison(self, subject: str, capability: str, normalized_name: str, requested_access: str) -> None:
        if self.poisoned:
            self._append_event(subject, capability, normalized_name, requested_access, "deny_run_poisoned")
            raise ValueError("synthetic_policy_poisoned")

    def _deny(self, subject: str, capability: str, normalized_name: str, requested_access: str) -> None:
        self.poisoned = True
        self._append_event(subject, capability, normalized_name, requested_access, "deny")
        raise ValueError("synthetic_policy_denied")

    def _allow(self, subject: str, capability: str, normalized_name: str, requested_access: str) -> None:
        self._append_event(subject, capability, normalized_name, requested_access, "allow")

    def read_control(self, subject: str, name: str) -> bytes:
        self._check_poison(subject, "control_read_exact", name, "read_bytes")
        if subject != "adapter" or name not in self.controls:
            self._deny(subject, "control_read_exact", name, "read_bytes")
        self._allow(subject, "control_read_exact", name, "read_bytes")
        return self.controls[name]

    def read_queue(self, subject: str, name: str) -> bytes:
        self._check_poison(subject, "queue_read_exact", name, "read_bytes")
        if subject != "adapter" or name not in self.queues:
            self._deny(subject, "queue_read_exact", name, "read_bytes")
        self._allow(subject, "queue_read_exact", name, "read_bytes")
        return self.queues[name]

    def read_source(self, subject: str, name: str) -> bytes:
        self._check_poison(subject, "source_read_exact", name, "read_bytes")
        if subject != "adapter" or name not in self.sources:
            self._deny(subject, "source_read_exact", name, "read_bytes")
        self._allow(subject, "source_read_exact", name, "read_bytes")
        return self.sources[name]["bytes"]

    def source_metadata(self, subject: str, name: str) -> dict:
        self._check_poison(subject, "source_metadata_exact", name, "read_metadata")
        if subject != "adapter" or name not in self.sources:
            self._deny(subject, "source_metadata_exact", name, "read_metadata")
        self._allow(subject, "source_metadata_exact", name, "read_metadata")
        return self.sources[name]["metadata"]

    def structural_identity(self, subject: str, name: str, page_index: int) -> dict:
        self._check_poison(subject, "source_identity_exact", name, "read_identity")
        if subject != "adapter" or name not in self.sources or page_index != 0:
            self._deny(subject, "source_identity_exact", name, "read_identity")
        self._allow(subject, "source_identity_exact", name, "read_identity")
        return self.sources[name]["page_identity"]

    def assert_public_root_inactive(self, subject: str) -> str:
        self._check_poison(subject, "inactive_public_root_assert", "page-proof-public-root", "assert_inactive")
        if subject != "adapter":
            self._deny(subject, "inactive_public_root_assert", "page-proof-public-root", "assert_inactive")
        self._allow(subject, "inactive_public_root_assert", "page-proof-public-root", "assert_inactive")
        return self.public_root_poison

    def run_stage_a(self, subject: str, provider, selected_page_index: int, source_identity_binding: dict) -> dict:
        self._check_poison(subject, "proof_stage_a", "synthetic-stage-a", "call")
        if subject != "adapter" or provider is None or not callable(provider):
            self._deny(subject, "proof_stage_a", "synthetic-stage-a", "call")
        self._allow(subject, "proof_stage_a", "synthetic-stage-a", "call")
        return provider(selected_page_index, source_identity_binding)

    def run_page_proof(self, subject: str, provider, stage_a_authority: dict, source_identity_binding: dict) -> dict:
        self._check_poison(subject, "proof_page_proof", "synthetic-page-proof", "call")
        if subject != "adapter" or provider is None or not callable(provider):
            self._deny(subject, "proof_page_proof", "synthetic-page-proof", "call")
        self._allow(subject, "proof_page_proof", "synthetic-page-proof", "call")
        return provider(stage_a_authority, source_identity_binding)

    def run_visual_witness(self, subject: str, provider, page_proof_core: dict, source_identity_binding: dict) -> dict:
        self._check_poison(subject, "proof_visual_witness", "synthetic-visual-witness", "call")
        if subject != "adapter" or provider is None or not callable(provider):
            self._deny(subject, "proof_visual_witness", "synthetic-visual-witness", "call")
        self._allow(subject, "proof_visual_witness", "synthetic-visual-witness", "call")
        return provider(page_proof_core, source_identity_binding)

    def write_output(self, subject: str, raw: bytes) -> None:
        self._check_poison(subject, "output_create_new", "synthetic-output", "create_new")
        if subject != "controller" or self.output_sink is not None:
            self._deny(subject, "output_create_new", "synthetic-output", "create_new")
        self._allow(subject, "output_create_new", "synthetic-output", "create_new")
        self.output_sink = bytes(raw)

    def policy_sha256(self) -> str:
        return self.policy["content_sha256"]

    def audit_payload(self) -> dict:
        denied = [event["capability"] for event in self._audit_events if event["decision"] != "allow"]
        return contracts.sealed_dict(
            {
                "content_sha256": "0" * 64,
                "denied_capabilities": denied,
                "event_count": len(self._audit_events),
                "event_sha256_inventory": [event["content_sha256"] for event in self._audit_events],
                "events": self._audit_events,
                "policy_complete": True,
                "schema": contracts.AUDIT_SCHEMA,
            },
            contracts._AUDIT_KEYS,
        )

    def audit_sha256(self) -> str:
        payload = self.audit_payload()
        return payload["content_sha256"]
