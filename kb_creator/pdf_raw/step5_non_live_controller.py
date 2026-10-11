from __future__ import annotations

from . import step5_non_live_contracts as contracts


def run_non_live_controller(invocation_raw: bytes, broker, run_non_live_fixture_phase):
    phase = _phase_from_invocation(invocation_raw)
    invocation = contracts.validate_invocation(invocation_raw, phase)
    output_raw = run_non_live_fixture_phase(invocation_raw, broker)
    if not isinstance(output_raw, bytes):
        raise ValueError("controller_output_invalid")
    payload = contracts._load_canonical_json(output_raw)
    schema = payload.get("schema")
    if schema == contracts.FAILURE_SCHEMA:
        contracts.validate_failure(output_raw, invocation)
        return output_raw
    if broker.poisoned:
        raise ValueError("synthetic_policy_poisoned")
    if schema != invocation["expected_output_schema"]:
        raise ValueError("controller_output_schema_invalid")
    if phase == "identity_capture":
        contracts.validate_identity_capture(output_raw)
    else:
        contracts.validate_preflight_evidence(output_raw)
    broker.write_output("controller", output_raw)
    return output_raw


def _phase_from_invocation(invocation_raw: bytes) -> str:
    loaded = contracts._load_canonical_json(invocation_raw)
    phase = loaded.get("phase")
    if phase not in ("identity_capture", "page_preflight"):
        raise ValueError("invocation_phase_invalid")
    return phase
