from __future__ import annotations

from kb_creator.pdf_raw import step5_non_live_contracts as contracts
from kb_creator.pdf_raw.step5_non_live_policy import build_policy

SOURCE_TWO_COLUMN_NAME = contracts.SOURCE_TWO_COLUMN
SOURCE_NESTED_FORM_NAME = contracts.SOURCE_NESTED_FORM
QUEUE_NAME = contracts.QUEUE_NAME
SELECTION_CONTROL_NAME = contracts.SELECTION_CONTROL_NAME
AUTHORIZATION_CONTROL_NAME = contracts.AUTHORIZATION_CONTROL_NAME
SOURCE_BYTES = {
    SOURCE_TWO_COLUMN_NAME: b"%PDF-synthetic-step5-two-column%",
    SOURCE_NESTED_FORM_NAME: b"%PDF-synthetic-step5-nested-form%",
}


def source_metadata(name: str) -> dict:
    return {
        "content_sha256": contracts.sha256_hex(SOURCE_BYTES[name]),
        "profile": "synthetic-fixture-v2",
        "source_name": name,
    }


def source_identity(name: str) -> dict:
    page_ref = [11, 0] if name == SOURCE_TWO_COLUMN_NAME else [12, 0]
    route = [[1, 0], [page_ref[0], page_ref[1]]]
    return contracts.sealed_dict(
        {
            "content_sha256": "0" * 64,
            "crop_box_pdf": ["0", "0", "600", "800"],
            "media_box_pdf": ["0", "0", "600", "800"],
            "page_count": 1,
            "page_identity_sha256": contracts.sha256_hex(contracts.canonical_json({"name": name, "page_ref": page_ref})),
            "page_ref": page_ref,
            "page_tree_route": route,
            "rotation_degrees": 0,
            "schema": contracts.SOURCE_IDENTITY_SCHEMA,
            "selected_page_index": 0,
            "source_virtual_name": name,
        },
        contracts._SOURCE_IDENTITY_KEYS,
    )


def runtime_identity() -> dict:
    return contracts.sealed_dict(
        {
            "content_sha256": "0" * 64,
            "implementation_manifest_sha256": "2c8dd274f50ea4515fa4f8f96665ae4df4cbf7ced26d7dba77fb0904264f08ef",
            "runtime_manifest_sha256": "89374af63f4905d5db4647e53992d1c1ac4037f628077705ebd7ebdb566c24b8",
            "schema": contracts.RUNTIME_IDENTITY_SCHEMA,
        },
        contracts._RUNTIME_IDENTITY_KEYS,
    )


def _env_hash() -> str:
    return contracts.sha256_hex(contracts.canonical_json(list(contracts.EXPECTED_ENV_ALLOWLIST)))


def command_record(command_id: str, expected_result: dict, actual_result: dict, output_parser_binding: str) -> dict:
    argv = [
        "D:\\NRI\\.tools\\python-3.13.14\\python.exe",
        "-I",
        "-B",
        "-m",
        "pytest",
        "--disable-plugin-autoload",
        "-q",
        "-p",
        "no:cacheprovider",
        command_id,
    ]
    return contracts.sealed_dict(
        {
            "actual_result": actual_result,
            "command_id": command_id,
            "completed_at": "2026-08-11T10:00:01Z",
            "content_sha256": "0" * 64,
            "cwd": "D:\\NRI",
            "environment_allowlist_sha256": _env_hash(),
            "exact_argv": argv,
            "exit_code": 0,
            "expected_result": expected_result,
            "implementation_manifest_sha256": "2c8dd274f50ea4515fa4f8f96665ae4df4cbf7ced26d7dba77fb0904264f08ef",
            "output_parser_binding": output_parser_binding,
            "started_at": "2026-08-11T10:00:00Z",
            "stderr_byte_length": 0,
            "stderr_sha256": contracts.sha256_hex(b""),
            "stdout_byte_length": 1,
            "stdout_sha256": contracts.sha256_hex(b"x"),
            "terminal_state": "accepted",
        },
        contracts._COMMAND_RECORD_KEYS,
    )


def prerequisite() -> dict:
    spec1 = "kb_creator/docs/plans/20260809-innsmouth-page-level-consumer-proof/handoffs/sol_page_proof_step5_non_live_adapter_implementation_spec_20260811.md"
    spec2 = "kb_creator/docs/plans/20260809-innsmouth-page-level-consumer-proof/handoffs/terra_page_proof_step5_non_live_adapter_p1_architecture_rereview_20260811.md"
    spec3 = "kb_creator/docs/plans/20260809-innsmouth-page-level-consumer-proof/handoffs/terra_page_proof_step5_non_live_adapter_p1_remediation_architecture_review_20260812.md"
    commands = [
        command_record("page_proof_py_compile", {"compiled": 11}, {"compiled": 11}, "literal.py_compile"),
        command_record("page_proof_collect_159", {"collected": 159}, {"collected": 159}, "literal.collect"),
        command_record("page_proof_execute_159", {"passed": 159}, {"passed": 159}, "literal.execute"),
        command_record("stage_a_topology_execute_15", {"passed": 15}, {"passed": 15}, "literal.execute"),
        command_record("stage_a_aggregate_execute_386_plus_1_skip", {"passed": 386, "skipped": 1}, {"passed": 386, "skipped": 1}, "literal.execute"),
        command_record("inactive_root_public_poison_target", {"passed": 1}, {"passed": 1}, "literal.execute"),
    ]
    receipts = [
        receipt_binding("sol", "architecture", spec1, 147, "321414e19ce6f227210448dfd200a09af96e434d312942551a844e9ec5ed214d"),
        receipt_binding("terra", "architecture", spec2, 150, "4f0dcaef70a7362c7fe56a02f826d25d65fadf9e3425142834a965c2d82e0c01"),
        receipt_binding("terra", "architecture", spec3, 162, "4b196c54046317eb5949424baed884ab45b0a52a9d88b99d80505f99ea179802"),
    ]
    return contracts.sealed_dict(
        {
            "aggregate_result": {
                "inactive_root_public_poison_target": {"failed": 0, "passed": 1, "skipped": 0},
                "page_proof_collect_159": {"collected": 159, "failed": 0, "skipped": 0},
                "page_proof_execute_159": {"failed": 0, "passed": 159, "skipped": 0},
                "stage_a_aggregate_execute_386_plus_1_skip": {"failed": 0, "passed": 386, "skipped": 1},
                "stage_a_topology_execute_15": {"failed": 0, "passed": 15, "skipped": 0},
            },
            "command_records": commands,
            "content_sha256": "0" * 64,
            "cwd": "D:\\NRI",
            "environment_allowlist": list(contracts.EXPECTED_ENV_ALLOWLIST),
            "goal_id": contracts.EXPECTED_GOAL_ID,
            "implementation_manifest_sha256": "2c8dd274f50ea4515fa4f8f96665ae4df4cbf7ced26d7dba77fb0904264f08ef",
            "receipt_bindings": receipts,
            "run_id": "retry-20260812-fixture-run",
            "runtime_identity": runtime_identity(),
            "schema": contracts.PREREQUISITE_SCHEMA,
            "step_id": contracts.EXPECTED_STEP_ID,
            "terminal_state": "accepted_fixture_only_prerequisite_qa",
        },
        contracts._PREREQUISITE_KEYS,
    )


def receipt_binding(role: str, review_kind: str, repo_relative_path: str, byte_length: int, sha: str) -> dict:
    return contracts.sealed_dict(
        {
            "byte_length": byte_length,
            "content_sha256": "0" * 64,
            "decision": "accepted",
            "repo_relative_path": repo_relative_path,
            "review_kind": review_kind,
            "role": role,
            "sha256": sha,
        },
        contracts._RECEIPT_BINDING_KEYS,
    )


def queue_rows():
    return [
        queue_row(0, "item-001", "unresolved", "block_order_only_hypothesis", 10),
        queue_row(1, "item-002", "closed", "block_order_only_hypothesis", 11),
        queue_row(2, "item-003", "unresolved", "other_hypothesis", 12),
    ]


def queue_row(queue_order: int, item_id: str, status: str, hypothesis: str, ordinal: int) -> dict:
    payload = {
        "artifact_repo_relative_path_literal": f"kb_creator/tests/fixtures/{item_id}.json",
        "content_sha256": "0" * 64,
        "hypothesis_literal": hypothesis,
        "item_id": item_id,
        "item_id_utf8_hex": item_id.encode("utf-8").hex(),
        "item_row_sha256": "0" * 64,
        "metadata_source_row_ordinal": ordinal,
        "queue_order": queue_order,
        "selected_page_index": 0,
        "status_literal": status,
    }
    unsigned = dict(payload)
    unsigned.pop("content_sha256")
    unsigned.pop("item_row_sha256")
    row_sha = contracts.sha256_hex(contracts.canonical_json(unsigned))
    payload["item_row_sha256"] = row_sha
    return contracts.sealed_dict(payload, contracts._QUEUE_ROW_KEYS)


def eligibility_filter() -> dict:
    return contracts.sealed_dict(
        {
            "allowed_hypotheses": ["block_order_only_hypothesis", "paragraph_boundary_only_hypothesis"],
            "content_sha256": "0" * 64,
            "duplicate_item_policy": "reject_snapshot",
            "page_index_minimum": 0,
            "required_status": "unresolved",
            "unknown_field_policy": "reject_row",
        },
        contracts._ELIGIBILITY_FILTER_KEYS,
    )


def eligibility_results(rows: list[dict]) -> list[dict]:
    results = []
    for row in rows:
        reasons = []
        if row["status_literal"] != "unresolved":
            reasons.append("status_mismatch")
        if row["hypothesis_literal"] not in {"block_order_only_hypothesis", "paragraph_boundary_only_hypothesis"}:
            reasons.append("hypothesis_mismatch")
        results.append(
            contracts.sealed_dict(
                {
                    "content_sha256": "0" * 64,
                    "eligible": not reasons,
                    "item_id": row["item_id"],
                    "reasons": reasons,
                },
                contracts._ELIGIBILITY_RESULT_KEYS,
            )
        )
    return results


def queue_binding(queue_raw: bytes) -> dict:
    return contracts.sealed_dict(
        {
            "content_sha256": "0" * 64,
            "logical_content_sha256": contracts.sha256_hex(queue_raw),
            "raw_byte_length": len(queue_raw),
            "raw_file_sha256": contracts.sha256_hex(queue_raw),
            "schema": "kb_creator.pdf_raw.Step5SyntheticQueueAuthorityBinding.v1",
            "virtual_name": QUEUE_NAME,
        },
        contracts._QUEUE_BINDING_KEYS,
    )


def queue_authority_raw() -> bytes:
    payload = {
        "queue_name": QUEUE_NAME,
        "row_ids": ["item-001", "item-002", "item-003"],
        "schema": "kb_creator.pdf_raw.Step5SyntheticQueueAuthorityFile.v1",
    }
    return contracts.canonical_json(payload)


def queue_proof() -> dict:
    rows = queue_rows()
    results = eligibility_results(rows)
    eligible_rows = [row for row, result in zip(rows, results) if result["eligible"]]
    proof = {
        "content_sha256": "0" * 64,
        "eligibility_filter": eligibility_filter(),
        "eligibility_result_sha256": contracts.sha256_hex(contracts.canonical_json(results)),
        "eligibility_results": results,
        "ordered_eligible_preimage": eligible_rows,
        "ordering_preimage_sha256": contracts.sha256_hex(contracts.canonical_json(eligible_rows)),
        "ordering_rule": ["queue_order", "selected_page_index", "item_id_utf8_hex", "metadata_source_row_ordinal"],
        "queue_authority_binding": None,
        "queue_snapshot_sha256": contracts.sha256_hex(contracts.canonical_json(rows)),
        "schema": contracts.QUEUE_SCHEMA,
        "selected_candidate_preimage": eligible_rows[0],
        "selection_replay_result": contracts.sealed_dict(
            {
                "content_sha256": "0" * 64,
                "replay_terminal": "first_eligible_selected_no_live_read",
                "selected_array_index": 0,
                "selected_item_id": eligible_rows[0]["item_id"],
            },
            contracts._SELECTION_REPLAY_KEYS,
        ),
        "snapshot_record_count": len(rows),
        "snapshot_row_hash_inventory": [row["item_row_sha256"] for row in rows],
        "snapshot_rows": rows,
    }
    raw = queue_authority_raw()
    bound = dict(proof)
    bound["queue_authority_binding"] = queue_binding(raw)
    return contracts.sealed_dict(bound, contracts._QUEUE_KEYS)


def selection_control(source_name: str = SOURCE_TWO_COLUMN_NAME) -> bytes:
    queue = queue_proof()
    payload = {
        "content_sha256": "0" * 64,
        "control_kind": "selection",
        "control_record_virtual_name": SELECTION_CONTROL_NAME,
        "exact_argv": ["D:\\NRI\\.tools\\python-3.13.14\\python.exe", "-I", "-B", "step5-non-live", "identity_capture", SELECTION_CONTROL_NAME, source_name, "0"],
        "execution_profile": contracts.EXPECTED_EXECUTION_PROFILE,
        "phase": "identity_capture",
        "prerequisite_qa": prerequisite(),
        "prerequisite_qa_sha256": prerequisite()["content_sha256"],
        "queue_selection_proof": queue,
        "schema": contracts.SELECTION_SCHEMA,
        "selected_item_row_sha256": queue["selected_candidate_preimage"]["item_row_sha256"],
        "selected_page_index": 0,
        "source_virtual_name": source_name,
    }
    return contracts.seal_closed(payload, contracts._SELECTION_KEYS)


def authorization_control(source_name: str = SOURCE_TWO_COLUMN_NAME) -> bytes:
    selection = contracts._load_canonical_json(selection_control(source_name))
    queue = selection["queue_selection_proof"]
    payload = {
        "authorization_scope": "selected_page_preflight",
        "content_sha256": "0" * 64,
        "control_kind": "authorization",
        "control_record_virtual_name": AUTHORIZATION_CONTROL_NAME,
        "exact_argv": ["D:\\NRI\\.tools\\python-3.13.14\\python.exe", "-I", "-B", "step5-non-live", "page_preflight", AUTHORIZATION_CONTROL_NAME, source_name, "0"],
        "execution_profile": contracts.EXPECTED_EXECUTION_PROFILE,
        "phase": "page_preflight",
        "prerequisite_qa": prerequisite(),
        "prerequisite_qa_sha256": prerequisite()["content_sha256"],
        "queue_selection_proof": queue,
        "schema": contracts.AUTHORIZATION_SCHEMA,
        "selected_item_row_sha256": queue["selected_candidate_preimage"]["item_row_sha256"],
        "selected_page_index": 0,
        "selection_sha256": selection["content_sha256"],
        "source_identity_sha256": source_identity(source_name)["content_sha256"],
        "source_virtual_name": source_name,
    }
    return contracts.seal_closed(payload, contracts._AUTHORIZATION_KEYS)


def invocation(phase: str, source_name: str = SOURCE_TWO_COLUMN_NAME) -> bytes:
    control_raw = selection_control(source_name) if phase == "identity_capture" else authorization_control(source_name)
    control = contracts._load_canonical_json(control_raw)
    payload = {
        "content_sha256": "0" * 64,
        "control_record_byte_length": len(control_raw),
        "control_record_content_sha256": control["content_sha256"],
        "control_record_file_sha256": contracts.sha256_hex(control_raw),
        "control_record_virtual_name": SELECTION_CONTROL_NAME if phase == "identity_capture" else AUTHORIZATION_CONTROL_NAME,
        "exact_argv": [
            "D:\\NRI\\.tools\\python-3.13.14\\python.exe",
            "-I",
            "-B",
            "step5-non-live",
            phase,
            SELECTION_CONTROL_NAME if phase == "identity_capture" else AUTHORIZATION_CONTROL_NAME,
            source_name,
            "0",
        ],
        "execution_profile": contracts.EXPECTED_EXECUTION_PROFILE,
        "expected_output_schema": contracts.IDENTITY_SCHEMA if phase == "identity_capture" else contracts.EVIDENCE_SCHEMA,
        "goal_id": contracts.EXPECTED_GOAL_ID,
        "phase": phase,
        "run_id": "retry-20260812-fixture-run",
        "schema": contracts.INVOCATION_SCHEMA,
        "selected_page_index": 0,
        "source_virtual_name": source_name,
        "step_id": contracts.EXPECTED_STEP_ID,
        "synthetic_policy": build_policy(),
        "synthetic_policy_sha256": build_policy()["content_sha256"],
    }
    return contracts.seal_closed(payload, contracts._INVOCATION_KEYS)


def broker_bundle():
    return {
        "controls": {
            SELECTION_CONTROL_NAME: selection_control(SOURCE_TWO_COLUMN_NAME),
            AUTHORIZATION_CONTROL_NAME: authorization_control(SOURCE_TWO_COLUMN_NAME),
        },
        "queues": {QUEUE_NAME: queue_authority_raw()},
        "sources": {
            SOURCE_TWO_COLUMN_NAME: {
                "bytes": SOURCE_BYTES[SOURCE_TWO_COLUMN_NAME],
                "metadata": source_metadata(SOURCE_TWO_COLUMN_NAME),
                "page_identity": source_identity(SOURCE_TWO_COLUMN_NAME),
            },
            SOURCE_NESTED_FORM_NAME: {
                "bytes": SOURCE_BYTES[SOURCE_NESTED_FORM_NAME],
                "metadata": source_metadata(SOURCE_NESTED_FORM_NAME),
                "page_identity": source_identity(SOURCE_NESTED_FORM_NAME),
            },
        },
        "public_root_poison": contracts.INACTIVE_PUBLIC_ROOT_TERMINAL,
    }


class ProofProtocol:
    def runtime_identity(self):
        return runtime_identity()

    def run_stage_a(self, selected_page_index: int, source_identity_binding: dict) -> dict:
        return contracts.sealed_dict(
            {
                "content_sha256": "0" * 64,
                "inventory_sha256": contracts.sha256_hex(b"stage-a-inventory"),
                "ordered_row_hash_inventory": [contracts.sha256_hex(b"row-1"), contracts.sha256_hex(b"row-2")],
                "row_count": 2,
                "schema": contracts.STAGE_A_SCHEMA,
                "selected_page_index": selected_page_index,
                "source_identity_sha256": source_identity_binding["content_sha256"],
                "terminal_state": "synthetic_stage_a_authority_only",
            },
            contracts._STAGE_A_KEYS,
        )

    def run_page_proof(self, stage_a_authority: dict, source_identity_binding: dict) -> dict:
        evidence_sha = contracts.sha256_hex(b"page-proof-evidence")
        return contracts.sealed_dict(
            {
                "block_count": 2,
                "block_inventory": [{"block_id": "b1", "ordinal": 0}, {"block_id": "b2", "ordinal": 1}],
                "boundary_count": 1,
                "boundary_decisions": [{"boundary_id": "bd1", "decision": "keep"}],
                "candidate_core_sha256": contracts.sha256_hex(b"candidate-core"),
                "conservation": {
                    "complete_adjacency": True,
                    "complete_order_permutation": True,
                    "complete_visual_binding": True,
                    "stage_a_row_conservation": True,
                    "block_conservation": True,
                    "fragment_conservation": True,
                },
                "content_sha256": "0" * 64,
                "evidence_core_sha256": evidence_sha,
                "fragment_count": 2,
                "fragment_inventory": [{"fragment_id": "f1", "ordinal": 0}, {"fragment_id": "f2", "ordinal": 1}],
                "reading_order_permutation": [0, 1],
                "replay": {"mismatch_count": 0, "replay_sha256": evidence_sha, "terminal_state": "exact_replay_satisfied"},
                "schema": contracts.PAGE_PROOF_SCHEMA,
                "selected_page_index": 0,
                "source_identity_sha256": source_identity_binding["content_sha256"],
                "stable_reason_codes": ["ok"],
                "stage_a_authority_sha256": stage_a_authority["content_sha256"],
                "terminal_state": "synthetic_page_proof_only",
                "visual_crosscheck_sha256": contracts.sha256_hex(b"visual-crosscheck"),
            },
            contracts._PROOF_KEYS,
        )

    def run_visual_witness(self, page_proof_core: dict, source_identity_binding: dict) -> dict:
        return contracts.sealed_dict(
            {
                "block_inventory_sha256": contracts.sha256_hex(contracts.canonical_json(page_proof_core["block_inventory"])),
                "boundary_inventory_sha256": contracts.sha256_hex(contracts.canonical_json(page_proof_core["boundary_decisions"])),
                "content_sha256": "0" * 64,
                "page_proof_content_sha256": page_proof_core["content_sha256"],
                "persisted": False,
                "schema": contracts.VISUAL_WITNESS_SCHEMA,
                "selected_page_index": 0,
                "source_identity_sha256": source_identity_binding["content_sha256"],
                "terminal_state": "synthetic_visual_witness_only",
                "witness_sha256": contracts.sha256_hex(b"visual-witness"),
            },
            contracts._VISUAL_KEYS,
        )
