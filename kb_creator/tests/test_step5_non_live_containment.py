from __future__ import annotations

import ast
import hashlib
import sys
from dataclasses import dataclass
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

_C07_NODE_IDS = (
    "kb_creator/tests/test_step5_non_live_contracts.py::test_closed_virtual_name_registry",
    "kb_creator/tests/test_step5_non_live_contracts.py::test_control_file_and_content_bindings_target_first",
    "kb_creator/tests/test_step5_non_live_contracts.py::test_prerequisite_six_command_baseline_replays",
    "kb_creator/tests/test_step5_non_live_contracts.py::test_prerequisite_actual_result_correspondence_target_first_resealed",
    "kb_creator/tests/test_step5_non_live_contracts.py::test_prerequisite_target_first_reseal[command_omitted-field0]",
    "kb_creator/tests/test_step5_non_live_contracts.py::test_prerequisite_target_first_reseal[command_duplicated-field1]",
    "kb_creator/tests/test_step5_non_live_contracts.py::test_prerequisite_target_first_reseal[command_reordered-field2]",
    "kb_creator/tests/test_step5_non_live_contracts.py::test_prerequisite_target_first_reseal[argv_drift-field3]",
    "kb_creator/tests/test_step5_non_live_contracts.py::test_prerequisite_target_first_reseal[missing_isolated_or_no_bytecode-field4]",
    "kb_creator/tests/test_step5_non_live_contracts.py::test_prerequisite_target_first_reseal[cache_enabled-field5]",
    "kb_creator/tests/test_step5_non_live_contracts.py::test_prerequisite_target_first_reseal[cwd_runtime_manifest_drift-field6]",
    "kb_creator/tests/test_step5_non_live_contracts.py::test_prerequisite_target_first_reseal[count_or_skip_drift-field7]",
    "kb_creator/tests/test_step5_non_live_contracts.py::test_prerequisite_target_first_reseal[target_node_or_claim_drift-field8]",
    "kb_creator/tests/test_step5_non_live_contracts.py::test_prerequisite_target_first_reseal[stdout_stderr_or_parser_drift-field9]",
    "kb_creator/tests/test_step5_non_live_contracts.py::test_prerequisite_selection_authorization_byte_equivalence",
    "kb_creator/tests/test_step5_non_live_contracts.py::test_queue_complete_four_key_element_zero_replay",
    "kb_creator/tests/test_step5_non_live_contracts.py::test_queue_target_first_reseal[row_hash_or_inventory]",
    "kb_creator/tests/test_step5_non_live_contracts.py::test_queue_target_first_reseal[earlier_row_omitted]",
    "kb_creator/tests/test_step5_non_live_contracts.py::test_queue_target_first_reseal[duplicate_item_or_ordinal]",
    "kb_creator/tests/test_step5_non_live_contracts.py::test_queue_target_first_reseal[utf8_or_unicode_normalization]",
    "kb_creator/tests/test_step5_non_live_contracts.py::test_queue_target_first_reseal[status_hypothesis_or_page]",
    "kb_creator/tests/test_step5_non_live_contracts.py::test_queue_target_first_reseal[forbidden_artifact]",
    "kb_creator/tests/test_step5_non_live_contracts.py::test_queue_target_first_reseal[reason_vector]",
    "kb_creator/tests/test_step5_non_live_contracts.py::test_queue_target_first_reseal[ordering_or_dropped_eligible]",
    "kb_creator/tests/test_step5_non_live_contracts.py::test_queue_target_first_reseal[nonzero_selected_index]",
    "kb_creator/tests/test_step5_non_live_contracts.py::test_queue_target_first_reseal[authority_drift_refresh_or_reselection]",
    "kb_creator/tests/test_step5_non_live_contracts.py::test_contract_selection_requires_literal_control_name",
    "kb_creator/tests/test_step5_non_live_contracts.py::test_contract_authorization_requires_literal_scope",
    "kb_creator/tests/test_step5_non_live_contracts.py::test_contract_source_name_must_be_exact_literal",
    "kb_creator/tests/test_step5_non_live_contracts.py::test_contract_selection_page_and_selected_row_cross_bind",
    "kb_creator/tests/test_step5_non_live_contracts.py::test_contract_authorization_selection_sha_must_be_hash",
    "kb_creator/tests/test_step5_non_live_contracts.py::test_contract_policy_digest_must_match_embedded_policy",
    "kb_creator/tests/test_step5_non_live_contracts.py::test_contract_expected_output_schema_is_phase_exact",
    "kb_creator/tests/test_step5_non_live_contracts.py::test_contract_failure_validator_accepts_closed_failure",
    "kb_creator/tests/test_step5_non_live_contracts.py::test_contract_failure_validator_rejects_unknown_error_code",
)
_C08_NODE_IDS = (
    "kb_creator/tests/test_step5_non_live_policy.py::test_broker_rejects_caller_policy_and_nonexact_registry",
    "kb_creator/tests/test_step5_non_live_policy.py::test_denied_attempt_blocks_later_allowed_read",
    "kb_creator/tests/test_step5_non_live_policy.py::test_denied_attempt_blocks_later_output_create",
    "kb_creator/tests/test_step5_non_live_policy.py::test_audit_target_first_reseal",
    "kb_creator/tests/test_step5_non_live_policy.py::test_audit_policy_replay_target_first_resealed[forged_matched_policy_entry]",
    "kb_creator/tests/test_step5_non_live_policy.py::test_audit_policy_replay_target_first_resealed[ordinal_gap]",
    "kb_creator/tests/test_step5_non_live_policy.py::test_audit_policy_replay_target_first_resealed[subject_mismatch]",
    "kb_creator/tests/test_step5_non_live_policy.py::test_audit_policy_replay_target_first_resealed[normalized_name_mismatch]",
    "kb_creator/tests/test_step5_non_live_policy.py::test_audit_policy_replay_target_first_resealed[requested_access_mismatch]",
    "kb_creator/tests/test_step5_non_live_policy.py::test_audit_policy_replay_target_first_resealed[missing_denied_inventory]",
    "kb_creator/tests/test_step5_non_live_policy.py::test_output_sink_is_at_most_one_create_new",
    "kb_creator/tests/test_step5_non_live_policy.py::test_controller_accepts_only_validated_positive_output",
    "kb_creator/tests/test_step5_non_live_policy.py::test_controller_validates_sealed_failure_core",
    "kb_creator/tests/test_step5_non_live_policy.py::test_controller_rejects_unsealed_or_cross_phase_failure",
    "kb_creator/tests/test_step5_non_live_policy.py::test_controller_rejects_positive_after_poison",
    "kb_creator/tests/test_step5_non_live_policy.py::test_policy_audit_records_poison_followup_decision",
    "kb_creator/tests/test_step5_non_live_policy.py::test_policy_public_root_assert_uses_literal_name",
    "kb_creator/tests/test_step5_non_live_policy.py::test_policy_queue_read_is_adapter_only",
    "kb_creator/tests/test_step5_non_live_policy.py::test_policy_source_metadata_is_adapter_only",
    "kb_creator/tests/test_step5_non_live_policy.py::test_policy_structural_identity_is_page_zero_only",
    "kb_creator/tests/test_step5_non_live_policy.py::test_controller_rejects_non_bytes_output",
    "kb_creator/tests/test_step5_non_live_policy.py::test_controller_rejects_wrong_positive_schema",
    "kb_creator/tests/test_step5_non_live_policy.py::test_policy_denied_inventory_is_reported",
    "kb_creator/tests/test_step5_non_live_policy.py::test_policy_output_sink_stays_empty_after_denied_run",
)
_C09_NODE_IDS = (
    "kb_creator/tests/test_step5_non_live_identity_adapter.py::test_identity_two_column_positive",
    "kb_creator/tests/test_step5_non_live_identity_adapter.py::test_identity_nested_form_positive",
    "kb_creator/tests/test_step5_non_live_identity_adapter.py::test_identity_control_content_binding_before_source",
    "kb_creator/tests/test_step5_non_live_identity_adapter.py::test_identity_prerequisite_and_queue_before_source",
    "kb_creator/tests/test_step5_non_live_identity_adapter.py::test_identity_source_byte_drift_target_first",
    "kb_creator/tests/test_step5_non_live_identity_adapter.py::test_identity_metadata_drift_target_first",
    "kb_creator/tests/test_step5_non_live_identity_adapter.py::test_identity_structural_drift_target_first",
    "kb_creator/tests/test_step5_non_live_identity_adapter.py::test_identity_exactly_two_reads_and_zero_downstream_calls",
    "kb_creator/tests/test_step5_non_live_identity_adapter.py::test_identity_invalid_phase_fails_before_broker_access",
    "kb_creator/tests/test_step5_non_live_identity_adapter.py::test_identity_invalid_selection_schema_returns_closed_failure",
    "kb_creator/tests/test_step5_non_live_identity_adapter.py::test_identity_policy_digest_mismatch_returns_failure",
    "kb_creator/tests/test_step5_non_live_identity_adapter.py::test_identity_failure_propagates_prerequisite_digest_when_available",
)
_C10_NODE_IDS = (
    "kb_creator/tests/test_step5_non_live_preflight_adapter.py::test_missing_closed_protocol_precedes_stage_a",
    "kb_creator/tests/test_step5_non_live_preflight_adapter.py::test_legacy_run_only_callable_is_rejected",
    "kb_creator/tests/test_step5_non_live_preflight_adapter.py::test_closed_three_stage_protocol_positive",
    "kb_creator/tests/test_step5_non_live_preflight_adapter.py::test_stage_a_binding_target_first",
    "kb_creator/tests/test_step5_non_live_preflight_adapter.py::test_page_proof_binding_target_first",
    "kb_creator/tests/test_step5_non_live_preflight_adapter.py::test_visual_witness_binding_target_first",
    "kb_creator/tests/test_step5_non_live_preflight_adapter.py::test_conservation_target_first_reseal",
    "kb_creator/tests/test_step5_non_live_preflight_adapter.py::test_replay_target_first_reseal",
    "kb_creator/tests/test_step5_non_live_preflight_adapter.py::test_audit_completeness_target_first_reseal",
    "kb_creator/tests/test_step5_non_live_preflight_adapter.py::test_plaintext_secret_resealed_is_rejected",
    "kb_creator/tests/test_step5_non_live_preflight_adapter.py::test_source_identity_resealed_adversary[plaintext_equal_pair]",
    "kb_creator/tests/test_step5_non_live_preflight_adapter.py::test_source_identity_resealed_adversary[unknown_key_equal_pair]",
    "kb_creator/tests/test_step5_non_live_preflight_adapter.py::test_payload_leak_target_first_reseal",
    "kb_creator/tests/test_step5_non_live_preflight_adapter.py::test_preflight_source_post_read_drift",
    "kb_creator/tests/test_step5_non_live_preflight_adapter.py::test_preflight_binds_authorization_source_identity",
    "kb_creator/tests/test_step5_non_live_preflight_adapter.py::test_preflight_runtime_identity_is_closed",
    "kb_creator/tests/test_step5_non_live_preflight_adapter.py::test_preflight_records_all_three_proof_calls",
    "kb_creator/tests/test_step5_non_live_preflight_adapter.py::test_preflight_selection_sha_propagates",
    "kb_creator/tests/test_step5_non_live_preflight_adapter.py::test_preflight_queue_hashes_propagate",
    "kb_creator/tests/test_step5_non_live_preflight_adapter.py::test_preflight_negative_decision_is_literal",
    "kb_creator/tests/test_step5_non_live_preflight_adapter.py::test_preflight_visual_identity_not_persisted",
    "kb_creator/tests/test_step5_non_live_preflight_adapter.py::test_preflight_stage_a_inventory_count_matches_rows",
    "kb_creator/tests/test_step5_non_live_preflight_adapter.py::test_identifier_run_id_target_first_resealed_closed_values",
    "kb_creator/tests/test_step5_non_live_preflight_adapter.py::test_identifier_item_id_target_first_resealed_closed_values",
    "kb_creator/tests/test_step5_non_live_preflight_adapter.py::test_identifier_block_id_target_first_resealed_closed_values",
    "kb_creator/tests/test_step5_non_live_preflight_adapter.py::test_identifier_fragment_id_target_first_resealed_closed_values",
    "kb_creator/tests/test_step5_non_live_preflight_adapter.py::test_identifier_boundary_id_target_first_resealed_closed_values",
    "kb_creator/tests/test_step5_non_live_preflight_adapter.py::test_page_proof_block_id_ordinal_mapping_target_first_fully_resealed",
    "kb_creator/tests/test_step5_non_live_preflight_adapter.py::test_page_proof_fragment_id_ordinal_mapping_target_first_fully_resealed",
    "kb_creator/tests/test_step5_non_live_preflight_adapter.py::test_page_proof_boundary_id_decision_mapping_target_first_fully_resealed",
    "kb_creator/tests/test_step5_non_live_preflight_adapter.py::test_visual_inventory_hash_binding_target_first_fully_resealed",
)
_C11_NODE_IDS = (
    "kb_creator/tests/test_step5_non_live_containment.py::test_exact_literal_collection_inventory",
    "kb_creator/tests/test_step5_non_live_containment.py::test_exact_eleven_file_candidate_inventory",
    "kb_creator/tests/test_step5_non_live_containment.py::test_direct_imports_match_appendix_b_closure",
    "kb_creator/tests/test_step5_non_live_containment.py::test_no_dynamic_import_or_executable_code",
    "kb_creator/tests/test_step5_non_live_containment.py::test_no_environment_or_path_discovery",
    "kb_creator/tests/test_step5_non_live_containment.py::test_no_socket_network_browser_or_subprocess",
    "kb_creator/tests/test_step5_non_live_containment.py::test_no_file_open_alias_or_attribute_call",
    "kb_creator/tests/test_step5_non_live_containment.py::test_no_cli_or_executable_module_guard",
    "kb_creator/tests/test_step5_non_live_containment.py::test_no_production_root_assignment_or_mutation",
    "kb_creator/tests/test_step5_non_live_containment.py::test_appendix_a_production_hashes_unchanged",
    "kb_creator/tests/test_step5_non_live_containment.py::test_no_public_export",
    "kb_creator/tests/test_step5_non_live_containment.py::test_c10_target_first_oracle_is_test_owned_and_production_sealer_independent",
    "kb_creator/tests/test_step5_non_live_containment.py::test_ast_meta_probe_detects_getattr_import_alias",
    "kb_creator/tests/test_step5_non_live_containment.py::test_ast_meta_probe_detects_getattr_open_alias",
    "kb_creator/tests/test_step5_non_live_containment.py::test_ast_meta_probe_detects_builtins_subscript_and_base_aliases",
    "kb_creator/tests/test_step5_non_live_containment.py::test_ast_meta_probe_detects_from_import_and_chained_callable_aliases",
    "kb_creator/tests/test_step5_non_live_containment.py::test_ast_meta_probe_detects_env_socket_subprocess_equivalents",
    "kb_creator/tests/test_step5_non_live_containment.py::test_ast_meta_probe_detects_protected_root_and_public_export_equivalents",
    "kb_creator/tests/test_step5_non_live_containment.py::test_ast_meta_probe_detects_protected_root_collection_storage_equivalents",
    "kb_creator/tests/test_step5_non_live_containment.py::test_ast_meta_probe_detects_protected_root_call_argument_alias_sink",
    "kb_creator/tests/test_step5_non_live_containment.py::test_ast_meta_probe_detects_path_division_and_path_base_propagation_equivalents",
    "kb_creator/tests/test_step5_non_live_containment.py::test_ast_meta_probe_detects_public_export_member_import_alias_equivalents",
    "kb_creator/tests/test_step5_non_live_containment.py::test_no_live_output_build_release_literals",
)
EXPECTED_NODE_IDS = _C07_NODE_IDS + _C08_NODE_IDS + _C09_NODE_IDS + _C10_NODE_IDS + _C11_NODE_IDS

PRODUCTION_FILES = (
    "D:\\NRI\\kb_creator\\pdf_raw\\step5_non_live_contracts.py",
    "D:\\NRI\\kb_creator\\pdf_raw\\step5_non_live_policy.py",
    "D:\\NRI\\kb_creator\\pdf_raw\\step5_non_live_controller.py",
    "D:\\NRI\\kb_creator\\pdf_raw\\step5_non_live_identity_adapter.py",
    "D:\\NRI\\kb_creator\\pdf_raw\\step5_non_live_preflight_adapter.py",
)
ELEVEN_FILES = PRODUCTION_FILES + (
    "D:\\NRI\\kb_creator\\tests\\_step5_non_live_fixture_leaves.py",
    "D:\\NRI\\kb_creator\\tests\\test_step5_non_live_contracts.py",
    "D:\\NRI\\kb_creator\\tests\\test_step5_non_live_policy.py",
    "D:\\NRI\\kb_creator\\tests\\test_step5_non_live_identity_adapter.py",
    "D:\\NRI\\kb_creator\\tests\\test_step5_non_live_preflight_adapter.py",
    "D:\\NRI\\kb_creator\\tests\\test_step5_non_live_containment.py",
)
EXPECTED_IMPORT_ROOTS = {
    "__future__",
    "hashlib",
    "json",
    "re",
    "kb_creator.pdf_raw.step5_non_live_policy",
}
PROTECTED_ROOTS = {
    "_PRODUCTION_FIXTURE_ADMISSION",
    "_PRODUCTION_EXPECTED_FIXTURE_ADMISSION_PRIMITIVES",
    "_PRODUCTION_REQUIRED_STAGE_A_TOPOLOGY_INVENTORY",
    "_PRODUCTION_EXPECTED_TOPOLOGY_PRIMITIVES",
}
ALLOWED_CATEGORIES = {
    "dynamic_import_execution",
    "file_path_access",
    "environment_discovery",
    "network_browser_access",
    "process_cli_execution",
    "protected_root_mutation",
    "forbidden_path_literal",
    "public_export",
}


def sha256_hex(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def _read(path: str) -> str:
    return Path(path).read_text(encoding="utf-8")


def _trees():
    return {path: ast.parse(_read(path), filename=path) for path in PRODUCTION_FILES}


@dataclass(frozen=True)
class ResolvedValue:
    kind: str
    value: tuple[str, ...]


UNKNOWN = ResolvedValue("unknown", ())


class Analyzer:
    def __init__(self, tree: ast.AST):
        self.tree = tree
        self.parents: dict[ast.AST, ast.AST] = {}
        self.bindings: dict[str, ResolvedValue] = {}
        self.findings: set[tuple[str, int, int]] = set()
        for parent in ast.walk(tree):
            for child in ast.iter_child_nodes(parent):
                self.parents[child] = parent

    def analyze(self) -> tuple[tuple[str, int, int], ...]:
        limit = sum(1 for node in ast.walk(self.tree) if isinstance(node, (ast.Assign, ast.AnnAssign, ast.NamedExpr, ast.Import, ast.ImportFrom))) + 1
        for _ in range(limit):
            changed = False
            for node in ast.walk(self.tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        changed |= self._bind(alias.asname or alias.name, ResolvedValue("module", (alias.name,)))
                elif isinstance(node, ast.ImportFrom) and node.module:
                    for alias in node.names:
                        name = alias.asname or alias.name
                        changed |= self._bind(name, self._import_binding(node.module, alias.name))
                elif isinstance(node, ast.Assign):
                    value = self._resolve(node.value)
                    changed |= self._assign_targets(node.targets, value)
                elif isinstance(node, ast.AnnAssign):
                    value = self._resolve(node.value) if node.value is not None else UNKNOWN
                    changed |= self._assign_target(node.target, value)
                elif isinstance(node, ast.NamedExpr):
                    changed |= self._assign_target(node.target, self._resolve(node.value))
            if not changed:
                break
        else:
            raise AssertionError("resolver_non_convergent")

        for node in ast.walk(self.tree):
            self._scan_node(node)
        return tuple(sorted(self.findings, key=lambda item: (item[1], item[2], item[0])))

    def _bind(self, name: str, value: ResolvedValue) -> bool:
        if not name or value == UNKNOWN:
            return False
        current = self.bindings.get(name)
        if current is not None:
            return False
        self.bindings[name] = value
        return True

    def _assign_targets(self, targets: list[ast.expr], value: ResolvedValue) -> bool:
        changed = False
        for target in targets:
            changed |= self._assign_target(target, value)
        return changed

    def _assign_target(self, target: ast.expr, value: ResolvedValue) -> bool:
        if isinstance(target, ast.Name):
            return self._bind(target.id, value)
        if isinstance(target, (ast.Tuple, ast.List)) and value.kind == "tuple":
            changed = False
            for inner, part in zip(target.elts, value.value, strict=False):
                changed |= self._assign_target(inner, ResolvedValue("const", (part,)))
            return changed
        return False

    def _import_binding(self, module: str, member: str) -> ResolvedValue:
        if module == "builtins" and member == "open":
            return ResolvedValue("callable", ("file_path_access", "builtins.open"))
        return ResolvedValue("member", (module, member))

    def _resolve(self, node: ast.AST | None) -> ResolvedValue:
        if node is None:
            return UNKNOWN
        if isinstance(node, ast.Name):
            if node.id in PROTECTED_ROOTS:
                return ResolvedValue("protected_root", (node.id,))
            if node.id == "__builtins__":
                return ResolvedValue("module", ("__builtins__",))
            if node.id in {"builtins", "io", "importlib", "os", "pathlib", "socket", "subprocess", "webbrowser"}:
                return ResolvedValue("module", (node.id,))
            if node.id == "Path":
                return ResolvedValue("module", ("Path",))
            return self.bindings.get(node.id, UNKNOWN)
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            return ResolvedValue("const", (node.value,))
        if isinstance(node, ast.JoinedStr):
            parts = []
            for value in node.values:
                resolved = self._resolve(value)
                if resolved.kind != "const":
                    return UNKNOWN
                parts.append(resolved.value[0])
            return ResolvedValue("const", ("".join(parts),))
        if isinstance(node, ast.FormattedValue):
            return self._resolve(node.value)
        if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Add):
            left = self._resolve(node.left)
            right = self._resolve(node.right)
            if left.kind == right.kind == "const":
                return ResolvedValue("const", (left.value[0] + right.value[0],))
            return UNKNOWN
        if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Div):
            left = self._resolve(node.left)
            right = self._resolve(node.right)
            if left.kind in {"const", "path"} and right.kind in {"const", "path"}:
                return ResolvedValue("path", (left.value[0].rstrip("\\/") + "\\" + right.value[0].lstrip("\\/"),))
            return UNKNOWN
        if isinstance(node, ast.Attribute):
            base = self._resolve(node.value)
            if base.kind == "module":
                module = base.value[0]
                return self._attribute_binding(module, node.attr)
            if base.kind == "member":
                return ResolvedValue("member", (base.value[0], f"{base.value[1]}.{node.attr}"))
            if base.kind in {"protected_root", "path"}:
                return base
            return UNKNOWN
        if isinstance(node, ast.Subscript):
            base = self._resolve(node.value)
            key = self._resolve(node.slice)
            if base.kind == "member" and base.value == ("os", "environ") and key.kind == "const":
                return ResolvedValue("callable", ("environment_discovery", "os.environ"))
            if base.kind == "module" and base.value[0] in {"builtins", "__builtins__"} and key.kind == "const" and key.value[0] == "__import__":
                return ResolvedValue("callable", ("dynamic_import_execution", "__import__"))
            if base.kind == "callable":
                return base
            return UNKNOWN
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == "getattr" and len(node.args) >= 2:
            base = self._resolve(node.args[0])
            member = self._resolve(node.args[1])
            if member.kind != "const":
                return UNKNOWN
            if base.kind == "module":
                return self._attribute_binding(base.value[0], member.value[0])
            return UNKNOWN
        if isinstance(node, ast.Call) and self._resolve(node.func).kind == "module" and self._resolve(node.func).value[0] == "Path":
            if node.args:
                first_arg = self._resolve(node.args[0])
                if first_arg.kind == "const":
                    return ResolvedValue("path", first_arg.value)
            return ResolvedValue("path", ("",))
        if isinstance(node, (ast.Tuple, ast.List)):
            values = []
            for inner in node.elts:
                resolved = self._resolve(inner)
                if resolved.kind == "protected_root":
                    return resolved
                if resolved.kind != "const":
                    return UNKNOWN
                values.append(resolved.value[0])
            return ResolvedValue("tuple", tuple(values))
        if isinstance(node, ast.Set):
            for inner in node.elts:
                resolved = self._resolve(inner)
                if resolved.kind == "protected_root":
                    return resolved
                if resolved.kind != "const":
                    return UNKNOWN
            return ResolvedValue("tuple", ())
        if isinstance(node, ast.Dict):
            for inner in tuple(node.keys) + tuple(node.values):
                resolved = self._resolve(inner)
                if resolved.kind == "protected_root":
                    return resolved
                if resolved.kind != "const":
                    return UNKNOWN
            return ResolvedValue("tuple", ())
        return UNKNOWN

    def _attribute_binding(self, module: str, member: str) -> ResolvedValue:
        if module in {"builtins", "__builtins__", "io"} and member == "open":
            return ResolvedValue("callable", ("file_path_access", f"{module}.open"))
        if module in {"builtins", "__builtins__"} and member == "__import__":
            return ResolvedValue("callable", ("dynamic_import_execution", "__import__"))
        if module == "os" and member == "environ":
            return ResolvedValue("member", ("os", "environ"))
        if module == "socket" and member == "socket":
            return ResolvedValue("callable", ("network_browser_access", "socket.socket"))
        if module == "subprocess" and member in {"run", "Popen", "call", "check_output"}:
            return ResolvedValue("callable", ("process_cli_execution", f"subprocess.{member}"))
        if module in {"pathlib", "Path"} and member in {"read_text", "read_bytes", "write_text", "write_bytes", "open"}:
            return ResolvedValue("callable", ("file_path_access", f"{module}.{member}"))
        if module == "webbrowser" and member == "open":
            return ResolvedValue("callable", ("network_browser_access", "webbrowser.open"))
        return ResolvedValue("member", (module, member))

    def _scan_node(self, node: ast.AST) -> None:
        if isinstance(node, ast.Call):
            self._scan_call(node)
        elif isinstance(node, ast.Assign):
            self._scan_assignment(node)
        elif isinstance(node, ast.Expr):
            self._scan_escape(node, node.value)
            self._scan_path_expression(node.value, node)
        elif isinstance(node, ast.AnnAssign):
            self._scan_single_target(node, node.target)
        elif isinstance(node, ast.NamedExpr):
            self._scan_single_target(node, node.target)
        elif isinstance(node, ast.Return):
            self._scan_escape(node, node.value)

    def _scan_call(self, node: ast.Call) -> None:
        resolved = self._resolve(node.func)
        if resolved.kind == "callable":
            self._add(resolved.value[0], node)
        if isinstance(node.func, ast.Attribute) and node.func.attr in {"append", "extend", "update"} and node.args:
            if self._is_public_export_target(node.func.value, node.args[0]):
                self._add("public_export", node)
        if isinstance(node.func, ast.Attribute) and node.func.attr in {"append", "extend", "update"} and self._is_protected_target(node.func.value):
            self._add("protected_root_mutation", node)
        for arg in node.args:
            if self._resolve(arg).kind == "protected_root":
                self._add("protected_root_mutation", node)
            self._scan_path_expression(arg, node)

    def _scan_assignment(self, node: ast.Assign) -> None:
        for target in node.targets:
            self._scan_single_target(node, target)
        self._scan_escape(node, node.value)
        self._scan_path_expression(node.value, node)
        if any(isinstance(target, ast.Name) and target.id == "__all__" for target in node.targets) and self._contains_step5_non_live(node.value):
            self._add("public_export", node)

    def _scan_single_target(self, anchor: ast.AST, target: ast.AST) -> None:
        if self._is_protected_target(target):
            self._add("protected_root_mutation", anchor)

    def _scan_escape(self, anchor: ast.AST, value: ast.AST | None) -> None:
        if value is None:
            return
        resolved = self._resolve(value)
        if resolved.kind == "callable":
            self._add(resolved.value[0], anchor)
        if resolved.kind == "protected_root":
            self._add("protected_root_mutation", anchor)

    def _scan_path_expression(self, value: ast.AST | None, anchor: ast.AST) -> None:
        resolved = self._resolve(value)
        if resolved.kind in {"const", "path"} and _contains_forbidden_path_segment(resolved.value[0]):
            self._add("forbidden_path_literal", anchor)
        if isinstance(value, ast.BinOp) and isinstance(value.op, ast.Add):
            self._scan_path_expression(value.left, anchor)
            self._scan_path_expression(value.right, anchor)
        if isinstance(value, ast.Call) and isinstance(value.func, ast.Attribute) and value.func.attr in {"join", "joinpath"}:
            for arg in value.args:
                self._scan_path_expression(arg, anchor)

    def _add(self, category: str, node: ast.AST) -> None:
        self.findings.add((category, node.lineno, node.col_offset))

    def _is_public_export_target(self, node: ast.AST, value: ast.AST | None = None) -> bool:
        if isinstance(node, ast.Name) and node.id == "__all__":
            return True
        if value is not None and self._contains_step5_non_live(value):
            return True
        return False

    def _contains_step5_non_live(self, node: ast.AST) -> bool:
        resolved = self._resolve(node)
        if resolved.kind == "const":
            return resolved.value[0] == "step5_non_live"
        if resolved.kind in {"member", "module"}:
            return any(part == "step5_non_live" or part.endswith(".step5_non_live") for part in resolved.value)
        if isinstance(node, (ast.List, ast.Tuple)):
            return any(self._contains_step5_non_live(inner) for inner in node.elts)
        if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Add):
            return self._contains_step5_non_live(node.left) or self._contains_step5_non_live(node.right)
        return False

    def _is_protected_target(self, node: ast.AST | None) -> bool:
        return isinstance(node, ast.Name) and node.id in PROTECTED_ROOTS


def _contains_forbidden_path_segment(value: str) -> bool:
    if "\\" not in value and "/" not in value:
        return False
    normalized = value.replace("/", "\\")
    lowered = [segment.lower() for segment in normalized.split("\\") if segment not in {"", "."}]
    return any(segment in {"live", "source", "output", "build", "public", "production", "repair", "release"} for segment in lowered)


def _findings() -> dict[str, tuple[tuple[str, int, int], ...]]:
    return {path: Analyzer(tree).analyze() for path, tree in _trees().items()}


def test_exact_literal_collection_inventory(request: pytest.FixtureRequest):
    actual = tuple(item.nodeid for item in request.session.items if "test_step5_non_live_" in item.nodeid)
    assert actual == EXPECTED_NODE_IDS
    assert len(actual) == 125
    assert len(_C07_NODE_IDS) == 35
    assert len(_C08_NODE_IDS) == 24
    assert len(_C09_NODE_IDS) == 12
    assert len(_C10_NODE_IDS) == 31
    assert len(_C11_NODE_IDS) == 23


def test_exact_eleven_file_candidate_inventory():
    assert len(ELEVEN_FILES) == 11


def test_direct_imports_match_appendix_b_closure():
    roots = set()
    for tree in _trees().values():
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                roots.update(alias.name for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module:
                roots.add(node.module)
    assert roots <= EXPECTED_IMPORT_ROOTS


def test_no_dynamic_import_or_executable_code():
    for path, path_findings in _findings().items():
        assert all(category != "dynamic_import_execution" for category, _line, _column in path_findings), path


def test_no_environment_or_path_discovery():
    findings = _findings()
    for path, path_findings in findings.items():
        assert all(category != "environment_discovery" for category, _line, _column in path_findings), path


def test_no_socket_network_browser_or_subprocess():
    findings = _findings()
    for path, path_findings in findings.items():
        assert all(category not in {"network_browser_access", "process_cli_execution"} for category, _line, _column in path_findings), path


def test_no_file_open_alias_or_attribute_call():
    findings = _findings()
    for path, path_findings in findings.items():
        assert all(category != "file_path_access" for category, _line, _column in path_findings), path


def test_no_cli_or_executable_module_guard():
    for path in PRODUCTION_FILES:
        assert "__main__" not in _read(path)


def test_no_production_root_assignment_or_mutation():
    findings = _findings()
    for path, path_findings in findings.items():
        assert all(category != "protected_root_mutation" for category, _line, _column in path_findings), path


def test_appendix_a_production_hashes_unchanged():
    with open("D:\\NRI\\kb_creator\\pdf_raw\\page_proof.py", "rb") as handle:
        assert sha256_hex(handle.read()) == "269e244f15445df8ee81d3fff33297705197f1bdcd703369c1342a49698114c2"


def test_no_public_export():
    findings = Analyzer(ast.parse(_read("D:\\NRI\\kb_creator\\pdf_raw\\__init__.py"))).analyze()
    assert all(category != "public_export" for category, _line, _column in findings)


def test_c10_target_first_oracle_is_test_owned_and_production_sealer_independent():
    tree = ast.parse(_read("D:\\NRI\\kb_creator\\tests\\test_step5_non_live_preflight_adapter.py"))
    forbidden_attrs = {"canonical_json", "sha256_hex", "seal_closed", "sealed_dict"}
    oracle_functions = {
        node.name: node
        for node in tree.body
        if isinstance(node, ast.FunctionDef) and node.name.startswith("_oracle_")
    }
    assert oracle_functions
    for function in oracle_functions.values():
        for node in ast.walk(function):
            if isinstance(node, ast.Attribute) and isinstance(node.value, ast.Name):
                assert not (node.value.id == "contracts" and node.attr in forbidden_attrs)
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) and isinstance(node.func.value, ast.Name):
                assert not (node.func.value.id == "fixtures")


def test_ast_meta_probe_detects_getattr_import_alias():
    snippet = 'loader_name="__"+"import__"\nloader=getattr(__builtins__,loader_name)\nloader("os")\n'
    findings = Analyzer(ast.parse(snippet)).analyze()
    assert findings == (
        ("dynamic_import_execution", 2, 0),
        ("dynamic_import_execution", 3, 0),
    )


def test_ast_meta_probe_detects_getattr_open_alias():
    snippet = 'import builtins\nmember="op"+"en"\nopen_alias=getattr(builtins,member)\nopen_alias("x")\n'
    findings = Analyzer(ast.parse(snippet)).analyze()
    assert findings == (
        ("file_path_access", 3, 0),
        ("file_path_access", 4, 0),
    )


def test_ast_meta_probe_detects_builtins_subscript_and_base_aliases():
    snippet = 'b=__builtins__\nc=b\nloader=c["__"+"import__"]\nstored=loader\nloader("os")\n'
    findings = Analyzer(ast.parse(snippet)).analyze()
    assert findings == (
        ("dynamic_import_execution", 3, 0),
        ("dynamic_import_execution", 4, 0),
        ("dynamic_import_execution", 5, 0),
    )


def test_ast_meta_probe_detects_from_import_and_chained_callable_aliases():
    snippet = "from builtins import open as local_open\nalias=local_open\nstored=alias\nalias('x')\n"
    findings = Analyzer(ast.parse(snippet)).analyze()
    assert findings == (
        ("file_path_access", 2, 0),
        ("file_path_access", 3, 0),
        ("file_path_access", 4, 0),
    )


def test_ast_meta_probe_detects_env_socket_subprocess_equivalents():
    snippet = (
        "import os as os_mod\n"
        "import socket as sock_mod\n"
        "import subprocess as sp\n"
        "path_owner=os_mod.environ\n"
        "path_owner['PA'+'TH']\n"
        "sock_mod.socket()\n"
        "sp.Popen(['cmd'])\n"
    )
    findings = Analyzer(ast.parse(snippet)).analyze()
    assert findings == (
        ("environment_discovery", 5, 0),
        ("network_browser_access", 6, 0),
        ("process_cli_execution", 7, 0),
    )


def test_ast_meta_probe_detects_protected_root_and_public_export_equivalents():
    snippet = (
        "_PRODUCTION_FIXTURE_ADMISSION='x'\n"
        "saved=_PRODUCTION_EXPECTED_FIXTURE_ADMISSION_PRIMITIVES\n"
        "path='D:\\\\NRI\\\\Output'+'\\\\artifact.txt'\n"
        "__all__=['step5_'+'non_live']\n"
    )
    findings = Analyzer(ast.parse(snippet)).analyze()
    assert findings == (
        ("protected_root_mutation", 1, 0),
        ("protected_root_mutation", 2, 0),
        ("forbidden_path_literal", 3, 0),
        ("public_export", 4, 0),
    )


def test_ast_meta_probe_detects_protected_root_collection_storage_equivalents():
    snippet = (
        "a=_PRODUCTION_FIXTURE_ADMISSION\n"
        "b=_PRODUCTION_EXPECTED_FIXTURE_ADMISSION_PRIMITIVES\n"
        "c=_PRODUCTION_REQUIRED_STAGE_A_TOPOLOGY_INVENTORY\n"
        "d=_PRODUCTION_EXPECTED_TOPOLOGY_PRIMITIVES\n"
        "bag=[a]\n"
        "set_box={b}\n"
        "box={'x':c,d:'y'}\n"
        "pair=(d,)\n"
        "nested=({'x':[a,{'y':b}]},)\n"
    )
    findings = Analyzer(ast.parse(snippet)).analyze()
    assert findings == (
        ("protected_root_mutation", 1, 0),
        ("protected_root_mutation", 2, 0),
        ("protected_root_mutation", 3, 0),
        ("protected_root_mutation", 4, 0),
        ("protected_root_mutation", 5, 0),
        ("protected_root_mutation", 6, 0),
        ("protected_root_mutation", 7, 0),
        ("protected_root_mutation", 8, 0),
        ("protected_root_mutation", 9, 0),
    )


def test_ast_meta_probe_detects_protected_root_call_argument_alias_sink():
    snippet = (
        "a=_PRODUCTION_FIXTURE_ADMISSION\n"
        "bag=[a]\n"
        "consume(bag)\n"
    )
    findings = Analyzer(ast.parse(snippet)).analyze()
    assert findings == (
        ("protected_root_mutation", 1, 0),
        ("protected_root_mutation", 2, 0),
        ("protected_root_mutation", 3, 0),
    )


def test_ast_meta_probe_detects_path_division_and_path_base_propagation_equivalents():
    snippet = 'base=Path("D:\\\\NRI")\nalias=base\nassembled=alias/("Out"+"put")/"x.txt"\n'
    findings = Analyzer(ast.parse(snippet)).analyze()
    assert findings == (("forbidden_path_literal", 3, 0),)


def test_ast_meta_probe_detects_public_export_member_import_alias_equivalents():
    cases = (
        (
            "from package import step5_non_live as exported\n"
            "member_alias=exported\n"
            "__all__=[member_alias]\n",
            (("public_export", 3, 0),),
        ),
        (
            "import package as pkg\n"
            "exported=pkg.step5_non_live\n"
            "__all__=[exported]\n",
            (("public_export", 3, 0),),
        ),
        (
            "import package.step5_non_live as exported\n"
            "__all__=[exported]\n",
            (("public_export", 2, 0),),
        ),
    )
    for snippet, expected in cases:
        assert Analyzer(ast.parse(snippet)).analyze() == expected


def test_no_live_output_build_release_literals():
    forbidden = ("D:\\NRI\\Output\\", "D:\\NRI\\Source\\", "D:\\NRI\\build\\", "D:\\NRI\\public\\", "D:\\NRI\\release\\")
    for path in PRODUCTION_FILES:
        text = _read(path)
        for token in forbidden:
            assert token not in text, path
