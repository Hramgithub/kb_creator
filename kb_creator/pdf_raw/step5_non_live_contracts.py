from __future__ import annotations

import hashlib
import json
import re

SOURCE_TWO_COLUMN = "fixture://step5/source/one-page-two-column.v1"
SOURCE_NESTED_FORM = "fixture://step5/source/one-page-nested-form.v1"
QUEUE_NAME = "fixture://step5/queue/unresolved-items.v1"
SELECTION_CONTROL_NAME = "fixture://step5/control/selection.v1"
AUTHORIZATION_CONTROL_NAME = "fixture://step5/control/authorization.v1"
VIRTUAL_REGISTRY = (
    SOURCE_TWO_COLUMN,
    SOURCE_NESTED_FORM,
    QUEUE_NAME,
    SELECTION_CONTROL_NAME,
    AUTHORIZATION_CONTROL_NAME,
)
SOURCE_NAMES = (SOURCE_TWO_COLUMN, SOURCE_NESTED_FORM)
ALLOWED_IMPORT_ROOTS = (
    "__future__",
    "hashlib",
    "json",
    "re",
    "kb_creator.pdf_raw.step5_non_live_contracts",
    "kb_creator.pdf_raw.step5_non_live_policy",
)
POLICY_SCHEMA = "kb_creator.pdf_raw.SyntheticCapabilityPolicy.v1"
AUDIT_EVENT_SCHEMA = "kb_creator.pdf_raw.SyntheticCapabilityAuditEvent.v1"
AUDIT_SCHEMA = "kb_creator.pdf_raw.SyntheticCapabilityAudit.v1"
PREREQUISITE_SCHEMA = "kb_creator.pdf_raw.LivePagePreflightPrerequisiteQA.v1"
QUEUE_SCHEMA = "kb_creator.pdf_raw.LivePagePreflightSelectionQueue.v1"
SELECTION_SCHEMA = "kb_creator.pdf_raw.Step5SyntheticSelection.v1"
AUTHORIZATION_SCHEMA = "kb_creator.pdf_raw.Step5SyntheticAuthorization.v1"
INVOCATION_SCHEMA = "kb_creator.pdf_raw.Step5NonLiveInvocation.v1"
IDENTITY_SCHEMA = "kb_creator.pdf_raw.NonLiveSourceIdentityCapture.v1"
EVIDENCE_SCHEMA = "kb_creator.pdf_raw.NonLivePagePreflightEvidencePackage.v1"
FAILURE_SCHEMA = "kb_creator.pdf_raw.NonLivePagePreflightFailure.v1"
STAGE_A_SCHEMA = "kb_creator.pdf_raw.Step5SyntheticStageAAuthority.v1"
PAGE_PROOF_SCHEMA = "kb_creator.pdf_raw.Step5SyntheticPageProofCore.v1"
VISUAL_WITNESS_SCHEMA = "kb_creator.pdf_raw.Step5SyntheticVisualWitnessIdentity.v1"
RUNTIME_IDENTITY_SCHEMA = "kb_creator.pdf_raw.Step5SyntheticRuntimeIdentity.v1"
SOURCE_IDENTITY_SCHEMA = "kb_creator.pdf_raw.Step5SyntheticSourceIdentity.v1"
EXPECTED_EXECUTION_PROFILE = "synthetic_fixture_only_no_live_authority"
EXPECTED_GOAL_ID = "20260809-innsmouth-page-level-consumer-proof"
EXPECTED_STEP_ID = "5-adapter-non-live-implementation"
EXPECTED_ENV_ALLOWLIST = ("PYTHONHASHSEED=0", "PYTHONDONTWRITEBYTECODE=1")
_IDENTIFIER_CONTRACT = {
    "run_id": frozenset({"retry-20260812-fixture-run"}),
    "item_id": frozenset({"item-001", "item-002", "item-003"}),
    "selected_item_id": frozenset({"item-001", "item-002", "item-003"}),
    "block_id": frozenset({"b1", "b2"}),
    "fragment_id": frozenset({"f1", "f2"}),
    "boundary_id": frozenset({"bd1"}),
}
_IDENTIFIER_ERRORS = {
    "run_id": "run_id_invalid",
    "item_id": "item_id_invalid",
    "selected_item_id": "item_id_invalid",
    "block_id": "block_id_invalid",
    "fragment_id": "fragment_id_invalid",
    "boundary_id": "boundary_id_invalid",
}
DENY_TERMINAL_STATE = "synthetic_policy_denied"
POISON_TERMINAL_STATE = "synthetic_policy_poisoned"
INACTIVE_PUBLIC_ROOT_TERMINAL = "page_proof_stage_a_fixture_coverage_incomplete"
_SHA256 = re.compile(r"^[0-9a-f]{64}$")

_INVOCATION_KEYS = (
    "content_sha256",
    "control_record_byte_length",
    "control_record_content_sha256",
    "control_record_file_sha256",
    "control_record_virtual_name",
    "exact_argv",
    "execution_profile",
    "expected_output_schema",
    "goal_id",
    "phase",
    "run_id",
    "schema",
    "selected_page_index",
    "source_virtual_name",
    "step_id",
    "synthetic_policy",
    "synthetic_policy_sha256",
)
_POLICY_KEYS = (
    "adapter_capabilities",
    "content_sha256",
    "controller_capabilities",
    "deny_terminal_state",
    "execution_profile",
    "registry",
    "schema",
)
_AUDIT_EVENT_KEYS = (
    "capability",
    "content_sha256",
    "decision",
    "matched_policy_entry",
    "normalized_name",
    "ordinal",
    "requested_access",
    "schema",
    "subject",
)
_AUDIT_KEYS = (
    "content_sha256",
    "denied_capabilities",
    "event_count",
    "event_sha256_inventory",
    "events",
    "policy_complete",
    "schema",
)
_COMMAND_RECORD_KEYS = (
    "actual_result",
    "command_id",
    "completed_at",
    "content_sha256",
    "cwd",
    "environment_allowlist_sha256",
    "exact_argv",
    "exit_code",
    "expected_result",
    "implementation_manifest_sha256",
    "output_parser_binding",
    "started_at",
    "stderr_byte_length",
    "stderr_sha256",
    "stdout_byte_length",
    "stdout_sha256",
    "terminal_state",
)
_RECEIPT_BINDING_KEYS = (
    "byte_length",
    "content_sha256",
    "decision",
    "repo_relative_path",
    "review_kind",
    "role",
    "sha256",
)
_PREREQUISITE_KEYS = (
    "aggregate_result",
    "command_records",
    "content_sha256",
    "cwd",
    "environment_allowlist",
    "implementation_manifest_sha256",
    "receipt_bindings",
    "run_id",
    "runtime_identity",
    "schema",
    "step_id",
    "terminal_state",
    "goal_id",
)
_QUEUE_BINDING_KEYS = (
    "content_sha256",
    "logical_content_sha256",
    "raw_byte_length",
    "raw_file_sha256",
    "schema",
    "virtual_name",
)
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
_ELIGIBILITY_FILTER_KEYS = (
    "allowed_hypotheses",
    "content_sha256",
    "duplicate_item_policy",
    "page_index_minimum",
    "required_status",
    "unknown_field_policy",
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
_SELECTION_KEYS = (
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
    "source_virtual_name",
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
_IDENTITY_KEYS = (
    "adapter_implementation_binding",
    "content_sha256",
    "decision",
    "eligibility_result_sha256",
    "execution_profile",
    "goal_id",
    "media_box_pdf",
    "crop_box_pdf",
    "ordering_preimage_sha256",
    "page_count",
    "page_identity_sha256",
    "page_ref",
    "page_tree_route",
    "policy_audit_sha256",
    "prerequisite_qa_sha256",
    "queue_snapshot_sha256",
    "rotation_degrees",
    "run_id",
    "selected_item_row_sha256",
    "selected_page_index",
    "selection_sha256",
    "source_byte_length",
    "source_sha256",
    "source_virtual_name",
    "step_id",
    "synthetic_metadata_after",
    "synthetic_metadata_before",
    "synthetic_policy_sha256",
    "schema",
    "terminal_state",
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
_FAILURE_KEYS = (
    "content_sha256",
    "decision",
    "error_code",
    "execution_profile",
    "goal_id",
    "phase",
    "prerequisite_qa_sha256",
    "run_id",
    "schema",
    "step_id",
    "terminal_state",
)
_RUNTIME_IDENTITY_KEYS = (
    "content_sha256",
    "implementation_manifest_sha256",
    "runtime_manifest_sha256",
    "schema",
)
_SOURCE_IDENTITY_KEYS = (
    "content_sha256",
    "crop_box_pdf",
    "media_box_pdf",
    "page_count",
    "page_identity_sha256",
    "page_ref",
    "page_tree_route",
    "rotation_degrees",
    "schema",
    "selected_page_index",
    "source_virtual_name",
)
_STAGE_A_KEYS = (
    "content_sha256",
    "inventory_sha256",
    "ordered_row_hash_inventory",
    "row_count",
    "schema",
    "selected_page_index",
    "source_identity_sha256",
    "terminal_state",
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
_EXPECTED_BLOCK_PROJECTION = (("b1", 0), ("b2", 1))
_EXPECTED_FRAGMENT_PROJECTION = (("f1", 0), ("f2", 1))
_EXPECTED_BOUNDARY_PROJECTION = (("bd1", "keep"),)


def sha256_hex(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def canonical_json(value: object) -> bytes:
    return json.dumps(value, ensure_ascii=True, sort_keys=True, separators=(",", ":")).encode("utf-8")


def _reject_duplicate_pairs(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate_key_forbidden")
        result[key] = value
    return result


def _validate_scalar(value):
    if value is None or value is True or value is False or isinstance(value, (int, str)):
        return
    if isinstance(value, float):
        raise ValueError("float_forbidden")
    if isinstance(value, list):
        for item in value:
            _validate_scalar(item)
        return
    if isinstance(value, dict):
        for inner in value.values():
            _validate_scalar(inner)
        return
    raise ValueError("type_forbidden")


def _load_canonical_json(raw: bytes) -> dict:
    if not isinstance(raw, bytes):
        raise ValueError("bytes_required")
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise ValueError("utf8_invalid") from exc
    if text.startswith("\ufeff"):
        raise ValueError("utf8_invalid")
    try:
        value = json.loads(text, object_pairs_hook=_reject_duplicate_pairs)
    except json.JSONDecodeError as exc:
        raise ValueError("json_invalid") from exc
    _validate_scalar(value)
    if not isinstance(value, dict):
        raise ValueError("root_object_required")
    if canonical_json(value) != raw:
        raise ValueError("canonical_bytes_invalid")
    return value


def _ensure_keys(value: dict, keys: tuple[str, ...]) -> None:
    if len(value) != len(keys) or tuple(sorted(value.keys())) != tuple(sorted(keys)):
        raise ValueError("closed_schema_invalid")


def seal_closed(value: dict, keys: tuple[str, ...]) -> bytes:
    _ensure_keys(value, keys)
    unsigned = dict(value)
    unsigned.pop("content_sha256", None)
    unsigned["content_sha256"] = sha256_hex(canonical_json(unsigned))
    _ensure_keys(unsigned, keys)
    return canonical_json(unsigned)


def sealed_dict(value: dict, keys: tuple[str, ...]) -> dict:
    return _load_canonical_json(seal_closed(value, keys))


def _validate_sha(value: str, code: str) -> None:
    if not isinstance(value, str) or not _SHA256.fullmatch(value):
        raise ValueError(code)


def _validate_name(name: str, allowed: tuple[str, ...], code: str) -> None:
    if name not in allowed:
        raise ValueError(code)


def _validate_page_index(value) -> None:
    if not isinstance(value, int) or value != 0:
        raise ValueError("selected_page_index_invalid")


def _expected_command_rows() -> tuple[tuple[str, dict, str], ...]:
    return (
        ("page_proof_py_compile", {"compiled": 11}, "literal.py_compile"),
        ("page_proof_collect_159", {"collected": 159}, "literal.collect"),
        ("page_proof_execute_159", {"passed": 159}, "literal.execute"),
        ("stage_a_topology_execute_15", {"passed": 15}, "literal.execute"),
        ("stage_a_aggregate_execute_386_plus_1_skip", {"passed": 386, "skipped": 1}, "literal.execute"),
        ("inactive_root_public_poison_target", {"passed": 1}, "literal.execute"),
    )


EXPECTED_RECEIPT_BINDINGS = (
    {
        "role": "sol",
        "review_kind": "architecture",
        "repo_relative_path": "kb_creator/docs/plans/20260809-innsmouth-page-level-consumer-proof/handoffs/sol_page_proof_step5_non_live_adapter_implementation_spec_20260811.md",
        "byte_length": 147,
        "sha256": "321414e19ce6f227210448dfd200a09af96e434d312942551a844e9ec5ed214d",
    },
    {
        "role": "terra",
        "review_kind": "architecture",
        "repo_relative_path": "kb_creator/docs/plans/20260809-innsmouth-page-level-consumer-proof/handoffs/terra_page_proof_step5_non_live_adapter_p1_architecture_rereview_20260811.md",
        "byte_length": 150,
        "sha256": "4f0dcaef70a7362c7fe56a02f826d25d65fadf9e3425142834a965c2d82e0c01",
    },
    {
        "role": "terra",
        "review_kind": "architecture",
        "repo_relative_path": "kb_creator/docs/plans/20260809-innsmouth-page-level-consumer-proof/handoffs/terra_page_proof_step5_non_live_adapter_p1_remediation_architecture_review_20260812.md",
        "byte_length": 162,
        "sha256": "4b196c54046317eb5949424baed884ab45b0a52a9d88b99d80505f99ea179802",
    },
)


def _validate_exact_argv(value, expected_phase: str, control_name: str, source_name: str) -> None:
    expected = ["D:\\NRI\\.tools\\python-3.13.14\\python.exe", "-I", "-B", "step5-non-live", expected_phase, control_name, source_name, "0"]
    if value != expected:
        raise ValueError("exact_argv_invalid")


def build_policy_dict() -> dict:
    return sealed_dict(
        {
            "adapter_capabilities": [
                "control_read_exact",
                "queue_read_exact",
                "source_read_exact",
                "source_metadata_exact",
                "source_identity_exact",
                "inactive_public_root_assert",
                "proof_stage_a",
                "proof_page_proof",
                "proof_visual_witness",
            ],
            "content_sha256": "0" * 64,
            "controller_capabilities": ["output_create_new"],
            "deny_terminal_state": DENY_TERMINAL_STATE,
            "execution_profile": EXPECTED_EXECUTION_PROFILE,
            "registry": list(VIRTUAL_REGISTRY),
            "schema": POLICY_SCHEMA,
        },
        _POLICY_KEYS,
    )


def validate_policy(policy: dict) -> dict:
    _ensure_keys(policy, _POLICY_KEYS)
    if seal_closed(dict(policy), _POLICY_KEYS) != canonical_json(policy):
        raise ValueError("synthetic_policy_invalid")
    if policy["schema"] != POLICY_SCHEMA or policy["execution_profile"] != EXPECTED_EXECUTION_PROFILE:
        raise ValueError("synthetic_policy_invalid")
    if tuple(policy["registry"]) != VIRTUAL_REGISTRY:
        raise ValueError("synthetic_policy_invalid")
    return policy


def validate_invocation(raw: bytes, expected_phase: str) -> dict:
    value = _load_canonical_json(raw)
    _ensure_keys(value, _INVOCATION_KEYS)
    if value["schema"] != INVOCATION_SCHEMA:
        raise ValueError("invocation_schema_invalid")
    if value["execution_profile"] != EXPECTED_EXECUTION_PROFILE:
        raise ValueError("invocation_profile_invalid")
    if value["goal_id"] != EXPECTED_GOAL_ID or value["step_id"] != EXPECTED_STEP_ID:
        raise ValueError("invocation_goal_invalid")
    if value["phase"] != expected_phase:
        raise ValueError("invocation_phase_invalid")
    expected_control = SELECTION_CONTROL_NAME if expected_phase == "identity_capture" else AUTHORIZATION_CONTROL_NAME
    expected_output = IDENTITY_SCHEMA if expected_phase == "identity_capture" else EVIDENCE_SCHEMA
    if value["control_record_virtual_name"] != expected_control:
        raise ValueError("control_record_virtual_name_invalid")
    _validate_name(value["source_virtual_name"], SOURCE_NAMES, "source_virtual_name_invalid")
    _validate_page_index(value["selected_page_index"])
    _validate_exact_argv(value["exact_argv"], expected_phase, expected_control, value["source_virtual_name"])
    if value["expected_output_schema"] != expected_output:
        raise ValueError("expected_output_schema_invalid")
    validate_policy(value["synthetic_policy"])
    if value["synthetic_policy_sha256"] != value["synthetic_policy"]["content_sha256"]:
        raise ValueError("synthetic_policy_sha256_invalid")
    if not isinstance(value["control_record_byte_length"], int) or value["control_record_byte_length"] < 1:
        raise ValueError("control_record_length_invalid")
    _validate_sha(value["control_record_file_sha256"], "control_record_file_sha256_invalid")
    _validate_sha(value["control_record_content_sha256"], "control_record_content_sha256_invalid")
    if seal_closed(dict(value), _INVOCATION_KEYS) != raw:
        raise ValueError("invocation_seal_invalid")
    return value


def _validate_runtime_identity(value: dict) -> None:
    _ensure_keys(value, _RUNTIME_IDENTITY_KEYS)
    if value["schema"] != RUNTIME_IDENTITY_SCHEMA:
        raise ValueError("runtime_identity_invalid")
    _validate_sha(value["implementation_manifest_sha256"], "runtime_identity_invalid")
    _validate_sha(value["runtime_manifest_sha256"], "runtime_identity_invalid")
    if seal_closed(dict(value), _RUNTIME_IDENTITY_KEYS) != canonical_json(value):
        raise ValueError("runtime_identity_invalid")


def validate_source_identity(value: dict) -> dict:
    try:
        _ensure_keys(value, _SOURCE_IDENTITY_KEYS)
    except ValueError as exc:
        raise ValueError("source_identity_schema_invalid") from exc
    if value["schema"] != SOURCE_IDENTITY_SCHEMA:
        raise ValueError("source_identity_schema_invalid")
    _validate_name(value["source_virtual_name"], SOURCE_NAMES, "source_identity_schema_invalid")
    _validate_page_index(value["selected_page_index"])
    if value["page_count"] != 1 or value["rotation_degrees"] != 0:
        raise ValueError("source_identity_schema_invalid")
    if value["page_ref"] not in ([11, 0], [12, 0]):
        raise ValueError("source_identity_schema_invalid")
    if value["page_tree_route"] != [[1, 0], value["page_ref"]]:
        raise ValueError("source_identity_schema_invalid")
    for box_name in ("media_box_pdf", "crop_box_pdf"):
        box = value[box_name]
        if box != ["0", "0", "600", "800"]:
            raise ValueError("source_identity_schema_invalid")
    expected_sha = sha256_hex(canonical_json({"name": value["source_virtual_name"], "page_ref": value["page_ref"]}))
    if value["page_identity_sha256"] != expected_sha:
        raise ValueError("source_identity_schema_invalid")
    if seal_closed(dict(value), _SOURCE_IDENTITY_KEYS) != canonical_json(value):
        raise ValueError("source_identity_schema_invalid")
    return value


def _validate_command_record(value: dict, command_id: str) -> None:
    _ensure_keys(value, _COMMAND_RECORD_KEYS)
    if value["command_id"] != command_id:
        raise ValueError("prerequisite_command_invalid")
    if value["cwd"] != "D:\\NRI":
        raise ValueError("prerequisite_command_invalid")
    _validate_sha(value["environment_allowlist_sha256"], "prerequisite_command_invalid")
    _validate_sha(value["implementation_manifest_sha256"], "prerequisite_command_invalid")
    _validate_sha(value["stdout_sha256"], "prerequisite_command_invalid")
    _validate_sha(value["stderr_sha256"], "prerequisite_command_invalid")
    if not isinstance(value["exit_code"], int):
        raise ValueError("prerequisite_command_invalid")
    if not isinstance(value["stdout_byte_length"], int) or not isinstance(value["stderr_byte_length"], int):
        raise ValueError("prerequisite_command_invalid")
    if value["exact_argv"][:3] != ["D:\\NRI\\.tools\\python-3.13.14\\python.exe", "-I", "-B"]:
        raise ValueError("prerequisite_command_invalid")
    if value["actual_result"] != value["expected_result"]:
        raise ValueError("prerequisite_actual_result_invalid")
    if seal_closed(dict(value), _COMMAND_RECORD_KEYS) != canonical_json(value):
        raise ValueError("prerequisite_command_invalid")


def _validate_receipt_binding(value: dict) -> None:
    _ensure_keys(value, _RECEIPT_BINDING_KEYS)
    if value["role"] not in {"sol", "terra"}:
        raise ValueError("receipt_binding_invalid")
    if value["review_kind"] != "architecture":
        raise ValueError("receipt_binding_invalid")
    if value["decision"] != "accepted":
        raise ValueError("receipt_binding_invalid")
    if not isinstance(value["byte_length"], int) or value["byte_length"] < 1:
        raise ValueError("receipt_binding_invalid")
    _validate_sha(value["sha256"], "receipt_binding_invalid")
    if seal_closed(dict(value), _RECEIPT_BINDING_KEYS) != canonical_json(value):
        raise ValueError("receipt_binding_invalid")


def validate_prerequisite(value: dict) -> dict:
    _ensure_keys(value, _PREREQUISITE_KEYS)
    if value["schema"] != PREREQUISITE_SCHEMA:
        raise ValueError("prerequisite_schema_invalid")
    if value["goal_id"] != EXPECTED_GOAL_ID or value["step_id"] != EXPECTED_STEP_ID:
        raise ValueError("prerequisite_schema_invalid")
    if value["cwd"] != "D:\\NRI" or tuple(value["environment_allowlist"]) != EXPECTED_ENV_ALLOWLIST:
        raise ValueError("prerequisite_environment_invalid")
    _validate_sha(value["implementation_manifest_sha256"], "prerequisite_manifest_invalid")
    _validate_runtime_identity(value["runtime_identity"])
    command_specs = _expected_command_rows()
    if len(value["command_records"]) != 6:
        raise ValueError("prerequisite_command_count_invalid")
    for record, (command_id, expected_result, parser_binding) in zip(value["command_records"], command_specs):
        _validate_command_record(record, command_id)
        if record["expected_result"] != expected_result or record["output_parser_binding"] != parser_binding:
            raise ValueError("prerequisite_command_invalid")
        if record["exit_code"] != 0 or record["terminal_state"] != "accepted":
            raise ValueError("prerequisite_command_invalid")
        if record["stdout_byte_length"] < 0 or record["stderr_byte_length"] < 0:
            raise ValueError("prerequisite_command_invalid")
        if record["stdout_sha256"] != sha256_hex(b"x") or record["stderr_sha256"] != sha256_hex(b""):
            raise ValueError("prerequisite_command_invalid")
    if len(value["receipt_bindings"]) != 3:
        raise ValueError("receipt_binding_invalid")
    for binding, expected in zip(value["receipt_bindings"], EXPECTED_RECEIPT_BINDINGS):
        _validate_receipt_binding(binding)
        for key, expected_value in expected.items():
            if binding[key] != expected_value:
                raise ValueError("receipt_binding_invalid")
    if len({binding["sha256"] for binding in value["receipt_bindings"]}) != 3:
        raise ValueError("receipt_binding_invalid")
    if value["aggregate_result"] != {
        "inactive_root_public_poison_target": {"failed": 0, "passed": 1, "skipped": 0},
        "page_proof_collect_159": {"collected": 159, "failed": 0, "skipped": 0},
        "page_proof_execute_159": {"failed": 0, "passed": 159, "skipped": 0},
        "stage_a_aggregate_execute_386_plus_1_skip": {"failed": 0, "passed": 386, "skipped": 1},
        "stage_a_topology_execute_15": {"failed": 0, "passed": 15, "skipped": 0},
    }:
        raise ValueError("prerequisite_aggregate_invalid")
    if value["terminal_state"] != "accepted_fixture_only_prerequisite_qa":
        raise ValueError("prerequisite_terminal_invalid")
    if seal_closed(dict(value), _PREREQUISITE_KEYS) != canonical_json(value):
        raise ValueError("prerequisite_seal_invalid")
    return value


def _validate_queue_binding(value: dict) -> None:
    _ensure_keys(value, _QUEUE_BINDING_KEYS)
    if value["schema"] != "kb_creator.pdf_raw.Step5SyntheticQueueAuthorityBinding.v1":
        raise ValueError("queue_binding_invalid")
    if value["virtual_name"] != QUEUE_NAME:
        raise ValueError("queue_binding_invalid")
    _validate_sha(value["raw_file_sha256"], "queue_binding_invalid")
    _validate_sha(value["logical_content_sha256"], "queue_binding_invalid")
    if seal_closed(dict(value), _QUEUE_BINDING_KEYS) != canonical_json(value):
        raise ValueError("queue_binding_invalid")


def _validate_queue_row(value: dict) -> None:
    _ensure_keys(value, _QUEUE_ROW_KEYS)
    _validate_leaf(value["item_id"], "item_id")
    if value["status_literal"] not in {"unresolved", "closed"}:
        raise ValueError("queue_row_invalid")
    if value["hypothesis_literal"] not in {"block_order_only_hypothesis", "paragraph_boundary_only_hypothesis", "other_hypothesis"}:
        raise ValueError("queue_row_invalid")
    if not isinstance(value["queue_order"], int) or not isinstance(value["metadata_source_row_ordinal"], int):
        raise ValueError("queue_row_invalid")
    _validate_page_index(value["selected_page_index"])
    _validate_sha(value["item_row_sha256"], "queue_row_invalid")
    if value["item_id_utf8_hex"] != value["item_id"].encode("utf-8").hex():
        raise ValueError("queue_row_invalid")
    row_preimage = {key: value[key] for key in _QUEUE_ROW_KEYS if key not in {"content_sha256", "item_row_sha256"}}
    if value["item_row_sha256"] != sha256_hex(canonical_json(row_preimage)):
        raise ValueError("queue_row_preimage_invalid")
    if value["artifact_repo_relative_path_literal"].startswith(("Output\\", "build\\", "public\\", "release\\")):
        raise ValueError("queue_row_invalid")
    if seal_closed(dict(value), _QUEUE_ROW_KEYS) != canonical_json(value):
        raise ValueError("queue_row_invalid")


def _validate_eligibility_filter(value: dict) -> None:
    _ensure_keys(value, _ELIGIBILITY_FILTER_KEYS)
    if value["required_status"] != "unresolved":
        raise ValueError("queue_filter_invalid")
    if tuple(value["allowed_hypotheses"]) != ("block_order_only_hypothesis", "paragraph_boundary_only_hypothesis"):
        raise ValueError("queue_filter_invalid")
    if value["page_index_minimum"] != 0 or value["duplicate_item_policy"] != "reject_snapshot" or value["unknown_field_policy"] != "reject_row":
        raise ValueError("queue_filter_invalid")
    if seal_closed(dict(value), _ELIGIBILITY_FILTER_KEYS) != canonical_json(value):
        raise ValueError("queue_filter_invalid")


def _validate_eligibility_result(value: dict) -> None:
    _ensure_keys(value, _ELIGIBILITY_RESULT_KEYS)
    if not isinstance(value["eligible"], bool) or not isinstance(value["reasons"], list):
        raise ValueError("queue_result_invalid")
    if seal_closed(dict(value), _ELIGIBILITY_RESULT_KEYS) != canonical_json(value):
        raise ValueError("queue_result_invalid")


def _expected_queue_authority_raw(rows: list[dict]) -> bytes:
    return canonical_json(
        {
            "queue_name": QUEUE_NAME,
            "row_ids": [row["item_id"] for row in rows],
            "schema": "kb_creator.pdf_raw.Step5SyntheticQueueAuthorityFile.v1",
        }
    )


def _validate_selection_replay(value: dict) -> None:
    _ensure_keys(value, _SELECTION_REPLAY_KEYS)
    _validate_leaf(value["selected_item_id"], "selected_item_id")
    if value["selected_array_index"] != 0 or value["replay_terminal"] != "first_eligible_selected_no_live_read":
        raise ValueError("queue_replay_invalid")
    if seal_closed(dict(value), _SELECTION_REPLAY_KEYS) != canonical_json(value):
        raise ValueError("queue_replay_invalid")


def validate_queue(value: dict) -> dict:
    _ensure_keys(value, _QUEUE_KEYS)
    if value["schema"] != QUEUE_SCHEMA:
        raise ValueError("queue_schema_invalid")
    _validate_queue_binding(value["queue_authority_binding"])
    if value["snapshot_record_count"] != len(value["snapshot_rows"]):
        raise ValueError("queue_snapshot_count_invalid")
    if len(value["snapshot_row_hash_inventory"]) != len(value["snapshot_rows"]):
        raise ValueError("queue_snapshot_inventory_invalid")
    ids = []
    ordinals = []
    for row, row_hash in zip(value["snapshot_rows"], value["snapshot_row_hash_inventory"]):
        _validate_queue_row(row)
        ids.append(row["item_id"])
        ordinals.append(row["metadata_source_row_ordinal"])
        if row_hash != row["item_row_sha256"]:
            raise ValueError("queue_snapshot_inventory_invalid")
    if len(ids) != len(set(ids)) or len(ordinals) != len(set(ordinals)):
        raise ValueError("queue_snapshot_inventory_invalid")
    _validate_eligibility_filter(value["eligibility_filter"])
    if len(value["eligibility_results"]) != len(value["snapshot_rows"]):
        raise ValueError("queue_result_invalid")
    expected_results = []
    for row, result in zip(value["snapshot_rows"], value["eligibility_results"]):
        _validate_eligibility_result(result)
        reasons = []
        if row["status_literal"] != value["eligibility_filter"]["required_status"]:
            reasons.append("status_mismatch")
        if row["hypothesis_literal"] not in set(value["eligibility_filter"]["allowed_hypotheses"]):
            reasons.append("hypothesis_mismatch")
        expected = sealed_dict(
            {
                "content_sha256": "0" * 64,
                "eligible": not reasons,
                "item_id": row["item_id"],
                "reasons": reasons,
            },
            _ELIGIBILITY_RESULT_KEYS,
        )
        expected_results.append(expected)
        if result != expected:
            raise ValueError("queue_result_invalid")
    if tuple(value["ordering_rule"]) != ("queue_order", "selected_page_index", "item_id_utf8_hex", "metadata_source_row_ordinal"):
        raise ValueError("queue_ordering_invalid")
    if not value["ordered_eligible_preimage"]:
        raise ValueError("queue_selection_invalid")
    expected_ordered = [row for row, result in zip(value["snapshot_rows"], expected_results) if result["eligible"]]
    expected_ordered.sort(key=lambda row: (row["queue_order"], row["selected_page_index"], row["item_id_utf8_hex"], row["metadata_source_row_ordinal"]))
    if value["ordered_eligible_preimage"] != expected_ordered:
        raise ValueError("queue_ordering_invalid")
    expected_raw = _expected_queue_authority_raw(value["snapshot_rows"])
    if value["queue_authority_binding"]["raw_byte_length"] != len(expected_raw):
        raise ValueError("queue_binding_invalid")
    if value["queue_authority_binding"]["raw_file_sha256"] != sha256_hex(expected_raw):
        raise ValueError("queue_binding_invalid")
    if value["queue_authority_binding"]["logical_content_sha256"] != sha256_hex(expected_raw):
        raise ValueError("queue_binding_invalid")
    if value["queue_snapshot_sha256"] != sha256_hex(canonical_json(value["snapshot_rows"])):
        raise ValueError("queue_hash_invalid")
    if value["eligibility_result_sha256"] != sha256_hex(canonical_json(expected_results)):
        raise ValueError("queue_hash_invalid")
    if value["ordering_preimage_sha256"] != sha256_hex(canonical_json(expected_ordered)):
        raise ValueError("queue_hash_invalid")
    _validate_selection_replay(value["selection_replay_result"])
    if value["selected_candidate_preimage"] != value["ordered_eligible_preimage"][0]:
        raise ValueError("queue_selection_invalid")
    for key in ("queue_snapshot_sha256", "eligibility_result_sha256", "ordering_preimage_sha256"):
        _validate_sha(value[key], "queue_hash_invalid")
    if seal_closed(dict(value), _QUEUE_KEYS) != canonical_json(value):
        raise ValueError("queue_seal_invalid")
    return value


def validate_selection_control(raw: bytes, invocation: dict, queue_raw: bytes) -> dict:
    value = _load_canonical_json(raw)
    _ensure_keys(value, _SELECTION_KEYS)
    if value["schema"] != SELECTION_SCHEMA or value["control_kind"] != "selection" or value["phase"] != "identity_capture":
        raise ValueError("selection_schema_invalid")
    if value["execution_profile"] != invocation["execution_profile"]:
        raise ValueError("selection_profile_invalid")
    if value["control_record_virtual_name"] != SELECTION_CONTROL_NAME or value["source_virtual_name"] != invocation["source_virtual_name"]:
        raise ValueError("selection_binding_invalid")
    _validate_page_index(value["selected_page_index"])
    _validate_exact_argv(value["exact_argv"], "identity_capture", SELECTION_CONTROL_NAME, value["source_virtual_name"])
    prerequisite = validate_prerequisite(value["prerequisite_qa"])
    queue = validate_queue(value["queue_selection_proof"])
    if value["prerequisite_qa_sha256"] != prerequisite["content_sha256"]:
        raise ValueError("prerequisite_qa_sha256_invalid")
    if value["selected_item_row_sha256"] != queue["selected_candidate_preimage"]["item_row_sha256"]:
        raise ValueError("selected_item_row_sha256_invalid")
    if queue_raw != _expected_queue_authority_raw(queue["snapshot_rows"]):
        raise ValueError("queue_authority_binding_invalid")
    if queue["queue_authority_binding"]["raw_file_sha256"] != sha256_hex(queue_raw):
        raise ValueError("queue_authority_binding_invalid")
    if value["selected_page_index"] != queue["selected_candidate_preimage"]["selected_page_index"]:
        raise ValueError("selection_page_invalid")
    if seal_closed(dict(value), _SELECTION_KEYS) != raw:
        raise ValueError("selection_seal_invalid")
    return value


def validate_authorization_control(raw: bytes, invocation: dict, queue_raw: bytes) -> dict:
    value = _load_canonical_json(raw)
    _ensure_keys(value, _AUTHORIZATION_KEYS)
    if value["schema"] != AUTHORIZATION_SCHEMA or value["control_kind"] != "authorization" or value["phase"] != "page_preflight":
        raise ValueError("authorization_schema_invalid")
    if value["authorization_scope"] != "selected_page_preflight":
        raise ValueError("authorization_scope_invalid")
    if value["execution_profile"] != invocation["execution_profile"]:
        raise ValueError("authorization_profile_invalid")
    if value["control_record_virtual_name"] != AUTHORIZATION_CONTROL_NAME or value["source_virtual_name"] != invocation["source_virtual_name"]:
        raise ValueError("authorization_binding_invalid")
    _validate_page_index(value["selected_page_index"])
    _validate_exact_argv(value["exact_argv"], "page_preflight", AUTHORIZATION_CONTROL_NAME, value["source_virtual_name"])
    prerequisite = validate_prerequisite(value["prerequisite_qa"])
    queue = validate_queue(value["queue_selection_proof"])
    if value["prerequisite_qa_sha256"] != prerequisite["content_sha256"]:
        raise ValueError("prerequisite_qa_sha256_invalid")
    if value["selected_item_row_sha256"] != queue["selected_candidate_preimage"]["item_row_sha256"]:
        raise ValueError("selected_item_row_sha256_invalid")
    _validate_sha(value["selection_sha256"], "selection_sha256_invalid")
    _validate_sha(value["source_identity_sha256"], "source_identity_sha256_invalid")
    if queue_raw != _expected_queue_authority_raw(queue["snapshot_rows"]):
        raise ValueError("queue_authority_binding_invalid")
    if queue["queue_authority_binding"]["raw_file_sha256"] != sha256_hex(queue_raw):
        raise ValueError("queue_authority_binding_invalid")
    if seal_closed(dict(value), _AUTHORIZATION_KEYS) != raw:
        raise ValueError("authorization_seal_invalid")
    return value


def validate_identity_capture(raw: bytes) -> dict:
    value = _load_canonical_json(raw)
    _ensure_keys(value, _IDENTITY_KEYS)
    if value["schema"] != IDENTITY_SCHEMA or value["execution_profile"] != EXPECTED_EXECUTION_PROFILE:
        raise ValueError("identity_schema_invalid")
    if value["goal_id"] != EXPECTED_GOAL_ID or value["step_id"] != EXPECTED_STEP_ID:
        raise ValueError("identity_binding_invalid")
    if value["terminal_state"] != "synthetic_source_identity_only_no_live_authority":
        raise ValueError("identity_terminal_invalid")
    if value["decision"] != {"live_authority": False, "repair_admission": "none", "review_required": True, "source_use": "forbidden"}:
        raise ValueError("identity_decision_invalid")
    for key in (
        "selection_sha256",
        "prerequisite_qa_sha256",
        "queue_snapshot_sha256",
        "eligibility_result_sha256",
        "ordering_preimage_sha256",
        "selected_item_row_sha256",
        "source_sha256",
        "page_identity_sha256",
        "adapter_implementation_binding",
        "synthetic_policy_sha256",
        "policy_audit_sha256",
    ):
        _validate_sha(value[key], "identity_hash_invalid")
    _validate_name(value["source_virtual_name"], SOURCE_NAMES, "source_virtual_name_invalid")
    if seal_closed(dict(value), _IDENTITY_KEYS) != raw:
        raise ValueError("identity_seal_invalid")
    return value


def _validate_stage_a(value: dict, source_identity_sha256: str) -> None:
    _ensure_keys(value, _STAGE_A_KEYS)
    if value["schema"] != STAGE_A_SCHEMA or value["terminal_state"] != "synthetic_stage_a_authority_only":
        raise ValueError("stage_a_invalid")
    if value["selected_page_index"] != 0 or value["source_identity_sha256"] != source_identity_sha256:
        raise ValueError("stage_a_invalid")
    if value["row_count"] != len(value["ordered_row_hash_inventory"]) or value["row_count"] < 1:
        raise ValueError("stage_a_invalid")
    for item in value["ordered_row_hash_inventory"]:
        _validate_sha(item, "stage_a_invalid")
    _validate_sha(value["inventory_sha256"], "stage_a_invalid")
    if seal_closed(dict(value), _STAGE_A_KEYS) != canonical_json(value):
        raise ValueError("stage_a_invalid")


def _validate_page_proof(value: dict, source_identity_sha256: str, stage_a_sha256: str) -> None:
    _ensure_keys(value, _PROOF_KEYS)
    if not isinstance(value["block_inventory"], list):
        raise ValueError("page_proof_invalid")
    if not isinstance(value["fragment_inventory"], list):
        raise ValueError("page_proof_invalid")
    if not isinstance(value["boundary_decisions"], list):
        raise ValueError("page_proof_invalid")

    block_projection = []
    for block in value["block_inventory"]:
        if not isinstance(block, dict) or tuple(sorted(block.keys())) != ("block_id", "ordinal"):
            raise ValueError("page_proof_invalid")
        _validate_leaf(block["block_id"], "block_id")
        if not isinstance(block["ordinal"], int):
            raise ValueError("page_proof_invalid")
        block_projection.append((block["block_id"], block["ordinal"]))

    fragment_projection = []
    for fragment in value["fragment_inventory"]:
        if not isinstance(fragment, dict) or tuple(sorted(fragment.keys())) != ("fragment_id", "ordinal"):
            raise ValueError("page_proof_invalid")
        _validate_leaf(fragment["fragment_id"], "fragment_id")
        if not isinstance(fragment["ordinal"], int):
            raise ValueError("page_proof_invalid")
        fragment_projection.append((fragment["fragment_id"], fragment["ordinal"]))

    boundary_projection = []
    for boundary in value["boundary_decisions"]:
        if not isinstance(boundary, dict) or tuple(sorted(boundary.keys())) != ("boundary_id", "decision"):
            raise ValueError("page_proof_invalid")
        _validate_leaf(boundary["boundary_id"], "boundary_id")
        if not isinstance(boundary["decision"], str):
            raise ValueError("page_proof_invalid")
        boundary_projection.append((boundary["boundary_id"], boundary["decision"]))

    if tuple(block_projection) != _EXPECTED_BLOCK_PROJECTION:
        raise ValueError("page_proof_invalid")
    if tuple(fragment_projection) != _EXPECTED_FRAGMENT_PROJECTION:
        raise ValueError("page_proof_invalid")
    if tuple(boundary_projection) != _EXPECTED_BOUNDARY_PROJECTION:
        raise ValueError("page_proof_invalid")
    if value["schema"] != PAGE_PROOF_SCHEMA or value["terminal_state"] != "synthetic_page_proof_only":
        raise ValueError("page_proof_invalid")
    if value["selected_page_index"] != 0 or value["source_identity_sha256"] != source_identity_sha256 or value["stage_a_authority_sha256"] != stage_a_sha256:
        raise ValueError("page_proof_invalid")
    for key in ("candidate_core_sha256", "evidence_core_sha256", "visual_crosscheck_sha256"):
        _validate_sha(value[key], "page_proof_invalid")
    if value["block_count"] != len(value["block_inventory"]) or value["fragment_count"] != len(value["fragment_inventory"]) or value["boundary_count"] != len(value["boundary_decisions"]):
        raise ValueError("page_proof_invalid")
    if value["conservation"] != {
        "complete_adjacency": True,
        "complete_order_permutation": True,
        "complete_visual_binding": True,
        "stage_a_row_conservation": True,
        "block_conservation": True,
        "fragment_conservation": True,
    }:
        raise ValueError("page_proof_invalid")
    if value["replay"] != {"mismatch_count": 0, "replay_sha256": value["evidence_core_sha256"], "terminal_state": "exact_replay_satisfied"}:
        raise ValueError("page_proof_invalid")
    if seal_closed(dict(value), _PROOF_KEYS) != canonical_json(value):
        raise ValueError("page_proof_invalid")


def _validate_visual_witness(value: dict, source_identity_sha256: str, page_proof: dict) -> None:
    _ensure_keys(value, _VISUAL_KEYS)
    if value["schema"] != VISUAL_WITNESS_SCHEMA or value["terminal_state"] != "synthetic_visual_witness_only":
        raise ValueError("visual_witness_invalid")
    expected_block_hash = sha256_hex(canonical_json(page_proof["block_inventory"]))
    expected_boundary_hash = sha256_hex(canonical_json(page_proof["boundary_decisions"]))
    if (
        value["selected_page_index"] != 0
        or value["source_identity_sha256"] != source_identity_sha256
        or value["page_proof_content_sha256"] != page_proof["content_sha256"]
        or value["block_inventory_sha256"] != expected_block_hash
        or value["boundary_inventory_sha256"] != expected_boundary_hash
    ):
        raise ValueError("visual_witness_invalid")
    if value["persisted"] is not False:
        raise ValueError("visual_witness_invalid")
    for key in ("block_inventory_sha256", "boundary_inventory_sha256", "witness_sha256"):
        _validate_sha(value[key], "visual_witness_invalid")
    if seal_closed(dict(value), _VISUAL_KEYS) != canonical_json(value):
        raise ValueError("visual_witness_invalid")


def validate_audit(value: dict) -> dict:
    _ensure_keys(value, _AUDIT_KEYS)
    if value["schema"] != AUDIT_SCHEMA:
        raise ValueError("policy_audit_invalid")
    if value["event_count"] != len(value["events"]) or len(value["event_sha256_inventory"]) != len(value["events"]) or value["policy_complete"] is not True:
        raise ValueError("policy_audit_invalid")
    denied = []
    poison = False
    for ordinal, (event, event_sha) in enumerate(zip(value["events"], value["event_sha256_inventory"]), start=1):
        _ensure_keys(event, _AUDIT_EVENT_KEYS)
        if event["schema"] != AUDIT_EVENT_SCHEMA or event["ordinal"] != ordinal:
            raise ValueError("policy_audit_invalid")
        if event["decision"] not in {"allow", "deny", "deny_run_poisoned"} or event["subject"] not in {"adapter", "controller"}:
            raise ValueError("policy_audit_invalid")
        if seal_closed(dict(event), _AUDIT_EVENT_KEYS) != canonical_json(event):
            raise ValueError("policy_audit_invalid")
        if event_sha != event["content_sha256"]:
            raise ValueError("policy_audit_invalid")
        expected_decision, expected_match = _policy_replay_decision(
            event["subject"],
            event["capability"],
            event["normalized_name"],
            event["requested_access"],
            poison,
        )
        if event["decision"] != expected_decision or event["matched_policy_entry"] != expected_match:
            raise ValueError("policy_audit_invalid")
        if expected_decision == "deny":
            poison = True
        if event["decision"] != "allow":
            denied.append(event["capability"])
    if value["denied_capabilities"] != denied:
        raise ValueError("policy_audit_invalid")
    if seal_closed(dict(value), _AUDIT_KEYS) != canonical_json(value):
        raise ValueError("policy_audit_invalid")
    return value


def _policy_replay_decision(subject: str, capability: str, normalized_name: str, requested_access: str, poisoned: bool) -> tuple[str, str]:
    if poisoned:
        return "deny_run_poisoned", "deny:poisoned"
    allow_rows = {
        ("adapter", "control_read_exact", SELECTION_CONTROL_NAME, "read_bytes"): "adapter:control_read_exact",
        ("adapter", "control_read_exact", AUTHORIZATION_CONTROL_NAME, "read_bytes"): "adapter:control_read_exact",
        ("adapter", "queue_read_exact", QUEUE_NAME, "read_bytes"): "adapter:queue_read_exact",
        ("adapter", "source_read_exact", SOURCE_TWO_COLUMN, "read_bytes"): "adapter:source_read_exact",
        ("adapter", "source_read_exact", SOURCE_NESTED_FORM, "read_bytes"): "adapter:source_read_exact",
        ("adapter", "source_metadata_exact", SOURCE_TWO_COLUMN, "read_metadata"): "adapter:source_metadata_exact",
        ("adapter", "source_metadata_exact", SOURCE_NESTED_FORM, "read_metadata"): "adapter:source_metadata_exact",
        ("adapter", "source_identity_exact", SOURCE_TWO_COLUMN, "read_identity"): "adapter:source_identity_exact",
        ("adapter", "source_identity_exact", SOURCE_NESTED_FORM, "read_identity"): "adapter:source_identity_exact",
        ("adapter", "inactive_public_root_assert", "page-proof-public-root", "assert_inactive"): "adapter:inactive_public_root_assert",
        ("adapter", "proof_stage_a", "synthetic-stage-a", "call"): "adapter:proof_stage_a",
        ("adapter", "proof_page_proof", "synthetic-page-proof", "call"): "adapter:proof_page_proof",
        ("adapter", "proof_visual_witness", "synthetic-visual-witness", "call"): "adapter:proof_visual_witness",
        ("controller", "output_create_new", "synthetic-output", "create_new"): "controller:output_create_new",
    }
    match_id = allow_rows.get((subject, capability, normalized_name, requested_access))
    if match_id is None:
        return "deny", "deny:default"
    return "allow", match_id


def _validate_leaf(value, field_name: str | None = None) -> None:
    if isinstance(value, dict):
        for key, inner in value.items():
            _validate_leaf(inner, key)
        return
    if isinstance(value, list):
        for inner in value:
            _validate_leaf(inner, field_name)
        return
    if isinstance(value, bool) or isinstance(value, int) or value is None:
        return
    if not isinstance(value, str):
        raise ValueError("source_identity_schema_invalid")
    if field_name and field_name.endswith("_sha256"):
        _validate_sha(value, "source_identity_schema_invalid")
        return
    if field_name in {"event_sha256_inventory", "ordered_row_hash_inventory", "snapshot_row_hash_inventory"}:
        _validate_sha(value, "source_identity_schema_invalid")
        return
    if field_name in {"goal_id", "step_id"}:
        return
    if field_name in _IDENTIFIER_CONTRACT:
        if value not in _IDENTIFIER_CONTRACT[field_name]:
            raise ValueError(_IDENTIFIER_ERRORS[field_name])
        return
    if field_name == "capability" and value in {
        "control_read_exact",
        "queue_read_exact",
        "source_read_exact",
        "source_metadata_exact",
        "source_identity_exact",
        "inactive_public_root_assert",
        "proof_stage_a",
        "proof_page_proof",
        "proof_visual_witness",
        "output_create_new",
    }:
        return
    if value in {
        EXPECTED_EXECUTION_PROFILE,
        EVIDENCE_SCHEMA,
        STAGE_A_SCHEMA,
        PAGE_PROOF_SCHEMA,
        VISUAL_WITNESS_SCHEMA,
        AUDIT_SCHEMA,
        AUDIT_EVENT_SCHEMA,
        RUNTIME_IDENTITY_SCHEMA,
        SOURCE_IDENTITY_SCHEMA,
        "synthetic_preflight_evidence_only_no_live_authority",
        "synthetic_stage_a_authority_only",
        "synthetic_page_proof_only",
        "synthetic_visual_witness_only",
        "exact_replay_satisfied",
        "keep",
        "ok",
        "allow",
        "deny",
        "deny_run_poisoned",
        "adapter",
        "controller",
        "read_bytes",
        "read_metadata",
        "read_identity",
        "assert_inactive",
        "call",
        "create_new",
        SELECTION_CONTROL_NAME,
        AUTHORIZATION_CONTROL_NAME,
        QUEUE_NAME,
        SOURCE_TWO_COLUMN,
        SOURCE_NESTED_FORM,
        "page-proof-public-root",
        "synthetic-stage-a",
        "synthetic-page-proof",
        "synthetic-visual-witness",
        "synthetic-output",
        "adapter:control_read_exact",
        "adapter:queue_read_exact",
        "adapter:source_read_exact",
        "adapter:source_metadata_exact",
        "adapter:source_identity_exact",
        "adapter:inactive_public_root_assert",
        "adapter:proof_stage_a",
        "adapter:proof_page_proof",
        "adapter:proof_visual_witness",
        "controller:output_create_new",
        "deny:default",
        "deny:poisoned",
        "first_eligible_selected_no_live_read",
        "synthetic_selected_page_preflight_only",
        "forbidden",
        "none",
        "block_order_only_hypothesis",
        "paragraph_boundary_only_hypothesis",
        "other_hypothesis",
        "unresolved",
        "closed",
        "status_mismatch",
        "hypothesis_mismatch",
    }:
        return
    if value.isdigit():
        return
    raise ValueError("source_identity_schema_invalid")


def validate_preflight_evidence(raw: bytes) -> dict:
    value = _load_canonical_json(raw)
    _ensure_keys(value, _EVIDENCE_KEYS)
    if value["schema"] != EVIDENCE_SCHEMA or value["execution_profile"] != EXPECTED_EXECUTION_PROFILE:
        raise ValueError("evidence_schema_invalid")
    if value["goal_id"] != EXPECTED_GOAL_ID or value["step_id"] != EXPECTED_STEP_ID:
        raise ValueError("evidence_binding_invalid")
    if value["terminal_state"] != "synthetic_preflight_evidence_only_no_live_authority":
        raise ValueError("evidence_terminal_invalid")
    if value["decision"] != {
        "live_authority": False,
        "production_activation": False,
        "repair_admission": "none",
        "review_required": True,
        "scope": "synthetic_selected_page_preflight_only",
        "source_use": "forbidden",
    }:
        raise ValueError("evidence_decision_invalid")
    for key in (
        "selection_sha256",
        "source_identity_sha256",
        "authorization_sha256",
        "prerequisite_qa_sha256",
        "queue_snapshot_sha256",
        "eligibility_result_sha256",
        "ordering_preimage_sha256",
        "implementation_manifest_sha256",
        "synthetic_policy_sha256",
    ):
        _validate_sha(value[key], "evidence_hash_invalid")
    _validate_runtime_identity(value["runtime_identity"])
    validate_source_identity(value["source_identity_before"])
    validate_source_identity(value["source_identity_after"])
    if value["source_identity_sha256"] != value["source_identity_before"]["content_sha256"]:
        raise ValueError("source_identity_schema_invalid")
    if value["source_identity_after"]["content_sha256"] != value["source_identity_before"]["content_sha256"]:
        raise ValueError("source_identity_schema_invalid")
    _validate_stage_a(value["stage_a_authority"], value["source_identity_sha256"])
    _validate_page_proof(value["page_proof"], value["source_identity_sha256"], value["stage_a_authority"]["content_sha256"])
    _validate_visual_witness(value["synthetic_visual_witness_identity"], value["source_identity_sha256"], value["page_proof"])
    validate_audit(value["policy_audit"])
    if value["source_identity_before"] != value["source_identity_after"]:
        raise ValueError("source_post_read_drift")
    _validate_leaf(value)
    if seal_closed(dict(value), _EVIDENCE_KEYS) != raw:
        raise ValueError("evidence_seal_invalid")
    return value


def validate_failure(raw: bytes, invocation: dict) -> dict:
    value = _load_canonical_json(raw)
    _ensure_keys(value, _FAILURE_KEYS)
    if value["schema"] != FAILURE_SCHEMA or value["execution_profile"] != EXPECTED_EXECUTION_PROFILE:
        raise ValueError("failure_schema_invalid")
    if value["goal_id"] != invocation["goal_id"] or value["step_id"] != invocation["step_id"] or value["run_id"] != invocation["run_id"] or value["phase"] != invocation["phase"]:
        raise ValueError("failure_binding_invalid")
    if value["decision"] != {"live_authority": False, "review_required": True}:
        raise ValueError("failure_decision_invalid")
    if value["terminal_state"] not in {"synthetic_identity_capture_rejected", "synthetic_page_preflight_rejected"}:
        raise ValueError("failure_terminal_invalid")
    if value["error_code"] not in {
        "authorization_scope_invalid",
        "control_record_content_sha256_invalid",
        "control_record_file_sha256_invalid",
        "control_record_length_invalid",
        "exact_argv_invalid",
        "invocation_phase_invalid",
        "invocation_schema_invalid",
        "page_proof_invalid",
        "preflight_rejected_render_contract_unresolved",
        "queue_authority_binding_invalid",
        "selection_schema_invalid",
        "source_post_read_drift",
        "stage_a_invalid",
        "synthetic_policy_denied",
        "synthetic_policy_poisoned",
        "visual_witness_invalid",
    }:
        raise ValueError("failure_error_code_invalid")
    if invocation["phase"] == "identity_capture" and value["prerequisite_qa_sha256"] not in {"0" * 64, invocation["control_record_content_sha256"]}:
        raise ValueError("failure_prerequisite_invalid")
    if seal_closed(dict(value), _FAILURE_KEYS) != raw:
        raise ValueError("failure_seal_invalid")
    return value


def make_failure(invocation: dict, error_code: str, terminal_state: str, prerequisite_qa_sha256: str = "0" * 64) -> bytes:
    return seal_closed(
        {
            "content_sha256": "0" * 64,
            "decision": {"live_authority": False, "review_required": True},
            "error_code": error_code,
            "execution_profile": EXPECTED_EXECUTION_PROFILE,
            "goal_id": invocation["goal_id"],
            "phase": invocation["phase"],
            "prerequisite_qa_sha256": prerequisite_qa_sha256,
            "run_id": invocation["run_id"],
            "schema": FAILURE_SCHEMA,
            "step_id": invocation["step_id"],
            "terminal_state": terminal_state,
        },
        _FAILURE_KEYS,
    )
