import ast
from dataclasses import replace
import hashlib
import inspect
import json
from pathlib import Path

import pytest

from kb_creator.pdf_raw import page_proof
from kb_creator.pdf_raw.errors import RawPdfError
from kb_creator.tests import _page_proof_fixture_leaves as leaves


_VISUAL_TEST_PATH = Path(r"D:\NRI\kb_creator\tests\test_page_proof_visual_crosscheck.py")
_TOPOLOGY = "4d3683f15ae64b4d03e51211755f2b3580e112e35bce4bf8c69efa29645dd3b4"
_INVENTORY = "3d707193bfe883dbe510e1ccdc169ac21e28c7b3a8fda697446a126fae7cdfd6"
_SURROGATE = "d0891ce46fc9cb3aeee366cf78610996b3e2a34e94d85c47e9d212599a438ac6"
_COVERAGE_ERROR = "page_proof_stage_a_fixture_coverage_incomplete"
_ADMISSION_ERROR = "page_proof_fixture_admission_missing"
_VISUAL_ERROR = "page_proof_visual_crosscheck_invalid"

_ENTRY_TWO_COLUMN = {
    "topology_id": "stage_a_positive_two_column.v1",
    "stage_a_fixture_id": "stage-a.positive-two-column.v1",
    "stage_a_authority_schema": "kb_creator.pdf_raw.RawAtomProvenanceAuthority.v1",
    "stage_a_authority_content_sha256": "890a9cef3ce995e7cb7881c035baa3e1e5a4c782f1827847b640c93fb28eafef",
    "stage_a_authority_inventory_sha256": "3173d033fcf6228687388f020f0e5e6e7e9c1ce2a373bc1b2bca49823ab951c0",
    "stage_a_fixture_binding_sha256": "c41ec7ae9eea7d5fc2f654eb825bf1bb1af954d00c754fd6140f134985af8880",
    "positive_topology_assertion_sha256": "e681b6ffbed2705283b915039e1d7a6ac145f4988765fd772a68eb63803831c8",
    "independent_stage_a_review_kind": "fixture_topology_acceptance",
    "independent_stage_a_review_decision": "accept",
    "independent_stage_a_review_content_sha256": "74ddca65755dbde190b57a5e82368895644ac6b605873913c20a32f2786d6526",
    "reviewed_authority_content_sha256": "890a9cef3ce995e7cb7881c035baa3e1e5a4c782f1827847b640c93fb28eafef",
    "entry_sha256": "31a05f30ebd7919f27191f2986c679c32c6fb739724a5364bdaef1d3b8b04673",
}
_ENTRY_NESTED_FORM = {
    "topology_id": "stage_a_positive_nested_form.v1",
    "stage_a_fixture_id": "stage-a.positive-nested-form.v1",
    "stage_a_authority_schema": "kb_creator.pdf_raw.RawAtomProvenanceAuthority.v1",
    "stage_a_authority_content_sha256": "8726e5d36b7acba9d96eacdcd62a57da00d7f4cfdd4df79cd6c63106d2e353e7",
    "stage_a_authority_inventory_sha256": "f296a28a72e509f47fe294217492cc463375c30144f8deab57fd7b4c85678b21",
    "stage_a_fixture_binding_sha256": "9b0f9f382e7926e3447072fa9340c38dd93531302e4294a14d8436eeacdf1d0a",
    "positive_topology_assertion_sha256": "a82adc738fd89394e80a607df46f7775a1967f874267f3b0289e7e64829d3d0f",
    "independent_stage_a_review_kind": "fixture_topology_acceptance",
    "independent_stage_a_review_decision": "accept",
    "independent_stage_a_review_content_sha256": "136489ff1892bb27b8425806a1972809d03ce5e5e22f42b6a9f1bdfeca1cc503",
    "reviewed_authority_content_sha256": "8726e5d36b7acba9d96eacdcd62a57da00d7f4cfdd4df79cd6c63106d2e353e7",
    "entry_sha256": "e7693b62761befda746fb405e1f6f5c89bca6ad91fea877110cd1e4a9d0844f6",
}
_ROOT = {
    "schema": "PageProofRequiredStageATopologyInventory.v1",
    "required_topology_ids": ("stage_a_positive_two_column.v1", "stage_a_positive_nested_form.v1"),
    "entries": (_ENTRY_TWO_COLUMN, _ENTRY_NESTED_FORM),
    "entry_count": 2,
    "inventory_sha256": _INVENTORY,
    "content_sha256": _TOPOLOGY,
}
_EXPECTED_INVENTORY_PRIMITIVES = (
    "PageProofRequiredStageATopologyInventory.v1",
    ("stage_a_positive_two_column.v1", "stage_a_positive_nested_form.v1"),
    (
        (
            "stage_a_positive_two_column.v1",
            "stage-a.positive-two-column.v1",
            "kb_creator.pdf_raw.RawAtomProvenanceAuthority.v1",
            "890a9cef3ce995e7cb7881c035baa3e1e5a4c782f1827847b640c93fb28eafef",
            "3173d033fcf6228687388f020f0e5e6e7e9c1ce2a373bc1b2bca49823ab951c0",
            "c41ec7ae9eea7d5fc2f654eb825bf1bb1af954d00c754fd6140f134985af8880",
            "e681b6ffbed2705283b915039e1d7a6ac145f4988765fd772a68eb63803831c8",
            "fixture_topology_acceptance",
            "accept",
            "74ddca65755dbde190b57a5e82368895644ac6b605873913c20a32f2786d6526",
            "890a9cef3ce995e7cb7881c035baa3e1e5a4c782f1827847b640c93fb28eafef",
            "31a05f30ebd7919f27191f2986c679c32c6fb739724a5364bdaef1d3b8b04673",
        ),
        (
            "stage_a_positive_nested_form.v1",
            "stage-a.positive-nested-form.v1",
            "kb_creator.pdf_raw.RawAtomProvenanceAuthority.v1",
            "8726e5d36b7acba9d96eacdcd62a57da00d7f4cfdd4df79cd6c63106d2e353e7",
            "f296a28a72e509f47fe294217492cc463375c30144f8deab57fd7b4c85678b21",
            "9b0f9f382e7926e3447072fa9340c38dd93531302e4294a14d8436eeacdf1d0a",
            "a82adc738fd89394e80a607df46f7775a1967f874267f3b0289e7e64829d3d0f",
            "fixture_topology_acceptance",
            "accept",
            "136489ff1892bb27b8425806a1972809d03ce5e5e22f42b6a9f1bdfeca1cc503",
            "8726e5d36b7acba9d96eacdcd62a57da00d7f4cfdd4df79cd6c63106d2e353e7",
            "e7693b62761befda746fb405e1f6f5c89bca6ad91fea877110cd1e4a9d0844f6",
        ),
    ),
    2,
    _INVENTORY,
    _TOPOLOGY,
)
_CASES = (
    {
        "name": "two-column",
        "leaf": leaves.TWO_COLUMN,
        "stage_id": "stage-a.positive-two-column.v1",
        "authority": "890a9cef3ce995e7cb7881c035baa3e1e5a4c782f1827847b640c93fb28eafef",
        "p": "cdb993a29ef0b05229a9a9c5dfd65dd30977df9c3ec1c295a88a94b5ea1f9c1d",
        "w": "172ae571a4da210c0f8cdd5faf4e82bbf1fe9e718448a89369ce38250d9a6594",
        "w_len": 3050,
        "w_raw": "d08e02060ccb8a602a445cc14f0e71fd16fbcf1616d826463e00c64f46948295",
        "v": "d38f51bba2b575528a32b572084b12ba2be33060e972ad7138a70eee9d580f73",
        "v_len": 2501,
        "v_raw": "2c358a6feb63859fa2f4c10346bd64e26da13f1e6d64f7cce5a868f881cab2c5",
        "f": "0c45fd6b6440482b377fbcd3c6797701e622250dc0fdd496d18dbef81cd48838",
        "candidate": "9bc92192ee0e03282585b83d6902b9367b1960b897c20da0c0c7240725c73e21",
        "reviewed": "91ceaadb97a611699e648ca865be60951709f09b1c5cf555ceb1f3c94cf427c0",
        "included": ("b0", "b1"),
        "excluded": (),
        "fragments": ("f0", "f1"),
        "adjacency": (("f0", "f1", "cross_column"),),
    },
    {
        "name": "nested-form",
        "leaf": leaves.NESTED_FORM,
        "stage_id": "stage-a.positive-nested-form.v1",
        "authority": "8726e5d36b7acba9d96eacdcd62a57da00d7f4cfdd4df79cd6c63106d2e353e7",
        "p": "388f7cc61345dbbcb516a4090e0d35cabb308f37137bf9b6b86c691fbf6c122c",
        "w": "aa95cc4c1ec640b9644e4febfb3e1d6f729be64b4544849ae5a9ffd4fd2c63e0",
        "w_len": 2927,
        "w_raw": "c488c0491139d27e696b5ab4ea4205b5ada0a9f577e3c3a23231868469eb85c3",
        "v": "f332b60fd1107f66ccff5e497a071f8438be9dc4d5e1e6c22734b9abbb6dbc97",
        "v_len": 2084,
        "v_raw": "887aba071a09620cdc4789a5635ba57661eff0eec0792ad50db66af3a2d4f0d3",
        "f": "249d56182c4710e6392740703ed86d388b714498d1bbc9c60e403de0caf0fbf2",
        "candidate": "c91d828ac9d5225df07efa76d0f854717ae67c5fb193d427f1992ab51631e929",
        "reviewed": "a3382a5a0c432967419b6266156d1b132e22ef7f44ecc8ea8043b75da7d93d7b",
        "included": ("b0",),
        "excluded": ("b1",),
        "fragments": ("n0",),
        "adjacency": (),
    },
    {
        "name": "visual-only",
        "leaf": leaves.VISUAL_ONLY,
        "stage_id": "stage-a.identity-single-use.v1",
        "authority": "e10859438e4ccef9ea6fdff9c8e3c923e71f39c4ae1b2c6a420d4319a1c468ed",
        "p": "7f9327e3dba8c5ad888efa3423115e779b0bb0502438e7ddd9c02cd2c43dbea2",
        "w": "0d9b5d5faf83844591daaf8b2b471c2c03564653e47769b45ea0abef0167fb39",
        "w_len": 2125,
        "w_raw": "68d22df7ade83daa01348bcd25dc90ec69a9f0efe73b9f6f0bb0b9cfe379fb2e",
        "v": "7995e65505d53305ff53811e0221b64496d93bf8b8a29a753d9683d0c1ac2f1f",
        "v_len": 1461,
        "v_raw": "1e47e656240499dcc6d2c1e25a64691fe99c02d9801b6f52b2f8cc80993f1c76",
        "f": "4d9c98331427c55f788ee2fc532365434054e6d300236120fc11946c7894aecd",
        "candidate": "98f9ccd0bf6d8c02a977472fcad6ac9feed628fd6a2943464307b9f4860d744a",
        "reviewed": "696cac67d638d93b51d4d475e34205cf5b4f432fcc517c21bdab6c51a9e8ccd3",
        "included": (),
        "excluded": ("b0",),
        "fragments": (),
        "adjacency": (),
    },
)
_TWO_BOUNDARY = {
    "p": "cdb993a29ef0b05229a9a9c5dfd65dd30977df9c3ec1c295a88a94b5ea1f9c1d",
    "w": "7d014e1cdb5ce542936a91b28615cc86f508208ec3a190dba84a990dd145e86d",
    "w_len": 3186,
    "w_raw": "e468e847f15c602d80808b572332978da2cd87eaa0009d766ae484ada80d1677",
    "v": "9083762bc843dacf0937f809809a8c82a4eed96326a7eb2dfab9870bb8d4aef0",
    "v_len": 2928,
    "v_raw": "761fc6aca16af4972d31081f4ad620f7f369c0c984c972f411ce196e4a95a2f4",
    "f": "afd101e900a5242cf0c7867102272997e719ea3f183c5e096d0e5c1c826c522e",
    "fragments": ("f0", "f1", "f2"),
    "adjacency": (("f0", "f1", "within_block"), ("f1", "f2", "cross_column")),
}
_EXPECTED_TARGET_NAMES = (
    "test_visual_crosscheck_root_pre_visual_binding_target_only_repair",
    "test_visual_crosscheck_root_topology_target_only_repair",
    "test_visual_crosscheck_root_pre_visual_core_target_only_repair",
    "test_visual_crosscheck_reviewer_identity_target_only_repair",
    "test_visual_crosscheck_reviewer_scope_target_only_repair",
    "test_visual_crosscheck_reviewer_independence_target_only_repair",
    "test_visual_crosscheck_root_content_seal_target_only_repair",
    "test_visual_crosscheck_boundary_missing_final_row_target_only_repair",
    "test_visual_crosscheck_boundary_duplicate_final_row_target_only_repair",
    "test_visual_crosscheck_boundary_reordered_rows_target_only_repair",
    "test_visual_crosscheck_boundary_aggregate_f0_f2_target_only_repair",
    "test_visual_crosscheck_boundary_source_fragment_target_only_repair",
    "test_visual_crosscheck_boundary_target_fragment_target_only_repair",
    "test_visual_crosscheck_boundary_kind_target_only_repair",
    "test_visual_crosscheck_boundary_source_block_target_only_repair",
    "test_visual_crosscheck_boundary_target_block_target_only_repair",
    "test_visual_crosscheck_boundary_source_column_target_only_repair",
    "test_visual_crosscheck_boundary_target_column_target_only_repair",
    "test_visual_crosscheck_boundary_bbox_target_only_repair",
    "test_visual_crosscheck_boundary_nonconfirm_target_only_repair",
    "test_visual_crosscheck_boundary_wrong_reason_target_only_repair",
    "test_visual_crosscheck_boundary_stale_decision_sha_target_only_repair",
    "test_visual_crosscheck_block_missing_final_row_target_only_repair",
    "test_visual_crosscheck_block_duplicate_final_row_target_only_repair",
    "test_visual_crosscheck_block_reordered_rows_target_only_repair",
    "test_visual_crosscheck_block_id_target_only_repair",
    "test_visual_crosscheck_block_ordinal_target_only_repair",
    "test_visual_crosscheck_block_disposition_target_only_repair",
    "test_visual_crosscheck_block_reason_target_only_repair",
    "test_visual_crosscheck_block_column_target_only_repair",
    "test_visual_crosscheck_block_bbox_target_only_repair",
    "test_visual_crosscheck_block_pixel_count_target_only_repair",
    "test_visual_crosscheck_block_component_evidence_target_only_repair",
    "test_visual_crosscheck_transcription_empty_bytes_target_only_repair",
    "test_visual_crosscheck_transcription_changed_bytes_old_hash_target_only_repair",
    "test_visual_crosscheck_transcription_wrong_hash_target_only_repair",
    "test_visual_crosscheck_block_nonconfirm_target_only_repair",
    "test_visual_crosscheck_block_wrong_reason_target_only_repair",
    "test_visual_crosscheck_block_stale_decision_sha_target_only_repair",
    "test_visual_crosscheck_inventory_block_digest_value_target_only_repair",
    "test_visual_crosscheck_inventory_block_digest_order_target_only_repair",
    "test_visual_crosscheck_inventory_boundary_digest_value_target_only_repair",
    "test_visual_crosscheck_inventory_boundary_digest_order_target_only_repair",
    "test_visual_crosscheck_inventory_block_count_target_only_repair",
    "test_visual_crosscheck_inventory_boundary_count_target_only_repair",
    "test_visual_crosscheck_inventory_stale_sha_target_only_repair",
)
_EXPECTED_POSITIVE_FIXTURE_NAMES = (
    "positive_two_column_normalized_case",
    "positive_nested_form_normalized_case",
    "positive_visual_only_normalized_case",
    "positive_two_boundary_normalized_case",
)
_EXPECTED_OUTER_NAMES = (
    "test_visual_crosscheck_outer_changed_v_with_unchanged_valid_row_rejected",
    "test_visual_crosscheck_outer_changed_row_v_metadata_without_recomputed_f_rejected",
)
_ADMISSION_PRIMITIVES = (
    (b"page-proof.positive-two-column.v1", 33, "e40137c0f1597d0a7b4aac30969a521e40c28d8019f02be2c10e21593dc127c9", "stage-a.positive-two-column.v1", "890a9cef3ce995e7cb7881c035baa3e1e5a4c782f1827847b640c93fb28eafef", _TOPOLOGY, 119, "10ed1f66fb1f4022051d3c3b0deca071fabe5c3f10a6673872655ed49d4d91a3", "cdb993a29ef0b05229a9a9c5dfd65dd30977df9c3ec1c295a88a94b5ea1f9c1d", 3050, "d08e02060ccb8a602a445cc14f0e71fd16fbcf1616d826463e00c64f46948295", 2501, "2c358a6feb63859fa2f4c10346bd64e26da13f1e6d64f7cce5a868f881cab2c5", "0c45fd6b6440482b377fbcd3c6797701e622250dc0fdd496d18dbef81cd48838", "9bc92192ee0e03282585b83d6902b9367b1960b897c20da0c0c7240725c73e21", "91ceaadb97a611699e648ca865be60951709f09b1c5cf555ceb1f3c94cf427c0"),
    (b"page-proof.positive-nested-form.v1", 34, "a3b7a43716c68188aade57ef01da907d582b63fb4d478cb6fe01f6c0bbfdf558", "stage-a.positive-nested-form.v1", "8726e5d36b7acba9d96eacdcd62a57da00d7f4cfdd4df79cd6c63106d2e353e7", _TOPOLOGY, 107, "416dfa33e7cb1b999ecb7fb3919d49b7482e5c2a1d459f1351e7c3ebf2b75303", "388f7cc61345dbbcb516a4090e0d35cabb308f37137bf9b6b86c691fbf6c122c", 2927, "c488c0491139d27e696b5ab4ea4205b5ada0a9f577e3c3a23231868469eb85c3", 2084, "887aba071a09620cdc4789a5635ba57661eff0eec0792ad50db66af3a2d4f0d3", "249d56182c4710e6392740703ed86d388b714498d1bbc9c60e403de0caf0fbf2", "c91d828ac9d5225df07efa76d0f854717ae67c5fb193d427f1992ab51631e929", "a3382a5a0c432967419b6266156d1b132e22ef7f44ecc8ea8043b75da7d93d7b"),
    (b"page-proof.positive-visual-only.v1", 34, "0de3f42cefdd92ad05303f3cc39043f98a990468c220ed3c1ebd01867d2ea998", "stage-a.identity-single-use.v1", "e10859438e4ccef9ea6fdff9c8e3c923e71f39c4ae1b2c6a420d4319a1c468ed", _TOPOLOGY, 86, "78e18a99eddb04e0123fb8aaafa4996f3cfa2acea02214841c68882c88932a33", "7f9327e3dba8c5ad888efa3423115e779b0bb0502438e7ddd9c02cd2c43dbea2", 2125, "68d22df7ade83daa01348bcd25dc90ec69a9f0efe73b9f6f0bb0b9cfe379fb2e", 1461, "1e47e656240499dcc6d2c1e25a64691fe99c02d9801b6f52b2f8cc80993f1c76", "4d9c98331427c55f788ee2fc532365434054e6d300236120fc11946c7894aecd", "98f9ccd0bf6d8c02a977472fcad6ac9feed628fd6a2943464307b9f4860d744a", "696cac67d638d93b51d4d475e34205cf5b4f432fcc517c21bdab6c51a9e8ccd3"),
)


class _Poison:
    def __getattribute__(self, name: str) -> object:
        raise AssertionError(f"caller argument accessed: {name}")

    def __bytes__(self) -> bytes:
        raise AssertionError("caller argument decoded")

    def __iter__(self) -> object:
        raise AssertionError("caller argument iterated")


def _sha256(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def _canonical_json(value: object) -> bytes:
    return json.dumps(value, ensure_ascii=True, sort_keys=True, separators=(",", ":")).encode("utf-8")


def _entry_from(value: dict[str, str]) -> page_proof._RequiredStageATopologyEntry:
    return page_proof._RequiredStageATopologyEntry(**value)


def _entry_payload(value: dict[str, str]) -> dict[str, str]:
    return {key: value[key] for key in value if key != "entry_sha256"}


def _entry_sha256(value: dict[str, str]) -> str:
    return _sha256(b"page-proof.required-stage-a-topology-entry.v1\0" + _canonical_json(_entry_payload(value)))


def _inventory_sha256(entries: tuple[dict[str, str], ...] = (_ENTRY_TWO_COLUMN, _ENTRY_NESTED_FORM)) -> str:
    payload = {
        "entry_count": len(entries),
        "ordered_entry_sha256": [entry["entry_sha256"] for entry in entries],
        "required_topology_ids": [entry["topology_id"] for entry in entries],
    }
    return _sha256(b"page-proof.required-stage-a-topology-inventory.v1\0" + _canonical_json(payload))


def _content_sha256(root: dict[str, object] = _ROOT) -> str:
    payload = {
        "entries": list(root["entries"]),
        "entry_count": root["entry_count"],
        "inventory_sha256": root["inventory_sha256"],
        "required_topology_ids": list(root["required_topology_ids"]),
        "schema": root["schema"],
    }
    return _sha256(_canonical_json(payload))


def _inventory(
    entries: tuple[dict[str, str], ...] = (_ENTRY_TWO_COLUMN, _ENTRY_NESTED_FORM),
) -> page_proof._RequiredStageATopologyInventory:
    return page_proof._RequiredStageATopologyInventory(
        schema="PageProofRequiredStageATopologyInventory.v1",
        required_topology_ids=tuple(entry["topology_id"] for entry in entries),
        entries=tuple(_entry_from(entry) for entry in entries),
        entry_count=len(entries),
        inventory_sha256=_inventory_sha256(entries),
        content_sha256=_content_sha256({
            "schema": "PageProofRequiredStageATopologyInventory.v1",
            "required_topology_ids": tuple(entry["topology_id"] for entry in entries),
            "entries": entries,
            "entry_count": len(entries),
            "inventory_sha256": _inventory_sha256(entries),
        }),
    )


def _expected_inventory_primitives() -> tuple[object, ...]:
    return _EXPECTED_INVENTORY_PRIMITIVES


def _row(case: dict[str, object], witness_raw: bytes | None = None, crosscheck_raw: bytes | None = None) -> page_proof._FixtureAdmission:
    leaf = case["leaf"]
    assert type(leaf) is tuple
    witness = leaf[1] if witness_raw is None else witness_raw
    crosscheck = leaf[3] if crosscheck_raw is None else crosscheck_raw
    return page_proof._FixtureAdmission(
        fixture_id=leaf[0],
        fixture_id_byte_length=len(leaf[0]),
        fixture_id_sha256=_sha256(leaf[0]),
        stage_a_fixture_id=case["stage_id"],
        stage_a_authority_content_sha256=case["authority"],
        required_topology_inventory_content_sha256=_TOPOLOGY,
        render_png_byte_length=len(leaf[2]),
        render_png_sha256=_sha256(leaf[2]),
        pre_visual_binding_sha256=case["p"],
        witness_byte_length=len(witness),
        witness_sha256=_sha256(witness),
        independent_visual_crosscheck_byte_length=len(crosscheck),
        independent_visual_crosscheck_sha256=_sha256(crosscheck),
        binding_sha256=case["f"] if witness_raw is None and crosscheck_raw is None else "0" * 64,
        expected_candidate_sha256=case["candidate"],
        expected_reviewed_ledger_sha256=case["reviewed"],
    )


def _two_boundary_row(crosscheck_raw: bytes | None = None) -> page_proof._FixtureAdmission:
    raw = leaves.INDEPENDENT_VISUAL_CROSSCHECK_TWO_BOUNDARY_V1 if crosscheck_raw is None else crosscheck_raw
    return page_proof._FixtureAdmission(
        fixture_id=leaves.TWO_COLUMN[0],
        fixture_id_byte_length=33,
        fixture_id_sha256=leaves.TWO_BOUNDARY_V1_SHA256[0],
        stage_a_fixture_id="stage-a.positive-two-column.v1",
        stage_a_authority_content_sha256="890a9cef3ce995e7cb7881c035baa3e1e5a4c782f1827847b640c93fb28eafef",
        required_topology_inventory_content_sha256=_TOPOLOGY,
        render_png_byte_length=119,
        render_png_sha256=leaves.TWO_BOUNDARY_V1_SHA256[2],
        pre_visual_binding_sha256=_TWO_BOUNDARY["p"],
        witness_byte_length=3186,
        witness_sha256=leaves.TWO_BOUNDARY_V1_SHA256[1],
        independent_visual_crosscheck_byte_length=len(raw),
        independent_visual_crosscheck_sha256=_sha256(raw),
        binding_sha256=_TWO_BOUNDARY["f"] if crosscheck_raw is None else "0" * 64,
        expected_candidate_sha256=_CASES[0]["candidate"],
        expected_reviewed_ledger_sha256=_CASES[0]["reviewed"],
    )


def _pre_visual_payload(row: page_proof._FixtureAdmission) -> dict[str, object]:
    return {
        "fixture_id": row.fixture_id.decode("ascii"),
        "fixture_id_byte_length": row.fixture_id_byte_length,
        "fixture_id_sha256": row.fixture_id_sha256,
        "stage_a_fixture_id": row.stage_a_fixture_id,
        "stage_a_authority_content_sha256": row.stage_a_authority_content_sha256,
        "required_topology_inventory_content_sha256": row.required_topology_inventory_content_sha256,
        "render_png_byte_length": row.render_png_byte_length,
        "render_png_sha256": row.render_png_sha256,
        "witness_schema": "kb_creator.pdf_raw.PageProofWitnessV3",
        "visual_crosscheck_schema": "kb_creator.pdf_raw.IndependentPageVisualCrossCheckV2",
    }


def _p(row: page_proof._FixtureAdmission) -> str:
    return _sha256(b"page-proof.fixture-pre-visual-binding.v1\0" + _canonical_json(_pre_visual_payload(row)))


def _f(row: page_proof._FixtureAdmission) -> str:
    payload = _pre_visual_payload(row)
    payload.update({
        "pre_visual_binding_sha256": row.pre_visual_binding_sha256,
        "witness_byte_length": row.witness_byte_length,
        "witness_sha256": row.witness_sha256,
        "independent_visual_crosscheck_byte_length": row.independent_visual_crosscheck_byte_length,
        "independent_visual_crosscheck_sha256": row.independent_visual_crosscheck_sha256,
    })
    return _sha256(b"page-proof.fixture-admission.v2\0" + _canonical_json(payload))


def _admission_rows() -> tuple[page_proof._FixtureAdmission, ...]:
    return tuple(_row(case) for case in _CASES)


def _admission_primitives() -> tuple[tuple[object, ...], ...]:
    return _ADMISSION_PRIMITIVES


def _authority(case: dict[str, object], witness_raw: bytes) -> page_proof.RawAtomProvenanceAuthorityV1:
    witness = json.loads(witness_raw.decode("utf-8"))
    raw = _canonical_json({
        "schema": "kb_creator.pdf_raw.RawAtomProvenanceAuthority.v1",
        "fixture": {"id": case["stage_id"]},
        "terminal_state": "fixture_only_authority",
        "content_sha256": case["authority"],
        "atoms": [{"atom_ordinal": row["atom_ordinal"], "atom_row_id": row["atom_row_id"]} for row in witness["atom_geometry_rows"]],
    })
    value = object.__new__(page_proof.RawAtomProvenanceAuthorityV1)
    object.__setattr__(value, "_raw", raw)
    object.__setattr__(value, "_fixture_id", case["stage_id"])
    object.__setattr__(value, "_content_sha256", case["authority"])
    object.__setattr__(value, "_terminal_state", "fixture_only_authority")
    object.__setattr__(value, "_sealed", True)
    return value


def _compose(case: dict[str, object]) -> dict[str, object]:
    leaf = case["leaf"]
    assert type(leaf) is tuple
    return page_proof._normalize_fixture_page_proof_composition(
        _authority(case, leaf[1]),
        leaf[1],
        leaf[2],
        leaf[3],
        _row(case),
    )


def _two_boundary_mechanics_and_flow() -> tuple[dict[str, object], dict[str, object]]:
    row = _two_boundary_row()
    mechanics = page_proof._normalize_fixture_witness_render_components(
        _authority(_CASES[0], leaves.WITNESS_TWO_BOUNDARY_V1),
        leaves.WITNESS_TWO_BOUNDARY_V1,
        leaves.RENDER_PNG_TWO_COLUMN_V1,
        row,
    )
    flow = page_proof._normalize_fixture_block_flow_adjacency(mechanics, mechanics["flow_input"])
    return mechanics, flow


def _reseal_json(value: dict[str, object]) -> bytes:
    value["content_sha256"] = _sha256(_canonical_json({key: item for key, item in value.items() if key != "content_sha256"}))
    return _canonical_json(value)


def _reseal_row(row: page_proof._FixtureAdmission) -> page_proof._FixtureAdmission:
    draft = replace(row, pre_visual_binding_sha256="0" * 64, binding_sha256="0" * 64)
    draft = replace(draft, pre_visual_binding_sha256=_p(draft))
    return replace(draft, binding_sha256=_f(draft))


def _poison_public_calls() -> None:
    poison = _Poison()
    calls = (
        (page_proof.derive_fixture_page_block_ledger_v1, (poison, poison, poison, poison)),
        (page_proof.review_fixture_page_block_ledger_v1, (poison, poison, poison)),
        (page_proof.replay_fixture_page_block_ledger_v1, (poison, poison, poison, poison, poison, poison)),
    )
    for operation, arguments in calls:
        with pytest.raises(RawPdfError, match=f"^{_COVERAGE_ERROR}$") as info:
            operation(*arguments)
        assert info.value.code == _COVERAGE_ERROR


def _all_visual_calls() -> list[ast.Call]:
    tree = ast.parse(_VISUAL_TEST_PATH.read_text(encoding="utf-8"))
    return [
        node for node in ast.walk(tree)
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Attribute)
        and isinstance(node.func.value, ast.Name)
        and node.func.value.id == "page_proof"
        and node.func.attr == "_normalize_fixture_visual_crosscheck"
    ]


def _visual_tree() -> ast.Module:
    return ast.parse(_VISUAL_TEST_PATH.read_text(encoding="utf-8"))


def _stmt_has_visual_call(stmt: ast.stmt) -> bool:
    return any(
        isinstance(node, ast.Call)
        and isinstance(node.func, ast.Attribute)
        and isinstance(node.func.value, ast.Name)
        and node.func.value.id == "page_proof"
        and node.func.attr == "_normalize_fixture_visual_crosscheck"
        for node in ast.walk(stmt)
    )


def _stmt_is_pre_normalizer_contract(stmt: ast.stmt) -> bool:
    return (
        isinstance(stmt, ast.Expr)
        and isinstance(stmt.value, ast.Call)
        and isinstance(stmt.value.func, ast.Name)
        and stmt.value.func.id == "_assert_pre_normalizer_contract"
    )


def _contract_predicate_map(stmt: ast.stmt) -> ast.Dict:
    assert _stmt_is_pre_normalizer_contract(stmt)
    call = stmt.value
    assert isinstance(call, ast.Call)
    assert {keyword.arg for keyword in call.keywords} == {
        "row",
        "witness_raw",
        "render_png_raw",
        "crosscheck_raw",
        "mechanics",
        "flow",
        "expected_predicates",
    }
    predicates = next(keyword.value for keyword in call.keywords if keyword.arg == "expected_predicates")
    assert isinstance(predicates, ast.Dict)
    assert len(predicates.keys) == 15
    assert all(isinstance(key, ast.Constant) and isinstance(key.value, str) for key in predicates.keys)
    assert all(isinstance(value, ast.Constant) and isinstance(value.value, bool) for value in predicates.values)
    return predicates


def test_authoritative_child_identities_materialize_exact_private_inventory_literals():
    assert _entry_sha256(_ENTRY_TWO_COLUMN) == _ENTRY_TWO_COLUMN["entry_sha256"]
    assert _entry_sha256(_ENTRY_NESTED_FORM) == _ENTRY_NESTED_FORM["entry_sha256"]
    assert _inventory_sha256() == _INVENTORY
    assert _content_sha256() == _TOPOLOGY
    inventory = _inventory()
    assert page_proof._inventory_is_complete(inventory, _expected_inventory_primitives()) == _TOPOLOGY
    assert page_proof._inventory_primitives(inventory) == _expected_inventory_primitives()


def test_private_inventory_expected_tuple_is_independent_and_complete():
    inventory_payload = {
        "entry_count": 2,
        "ordered_entry_sha256": [_ENTRY_TWO_COLUMN["entry_sha256"], _ENTRY_NESTED_FORM["entry_sha256"]],
        "required_topology_ids": ["stage_a_positive_two_column.v1", "stage_a_positive_nested_form.v1"],
    }
    assert _sha256(b"page-proof.required-stage-a-topology-inventory.v1\0" + _canonical_json(inventory_payload)) == _INVENTORY
    root_payload = {
        "entries": [_ENTRY_TWO_COLUMN, _ENTRY_NESTED_FORM],
        "entry_count": 2,
        "inventory_sha256": _INVENTORY,
        "required_topology_ids": ["stage_a_positive_two_column.v1", "stage_a_positive_nested_form.v1"],
        "schema": "PageProofRequiredStageATopologyInventory.v1",
    }
    assert _sha256(_canonical_json(root_payload)) == _TOPOLOGY
    assert "content_sha256" not in root_payload


def test_child_identity_missing_duplicate_swapped_and_wrong_source_hash_fail_closed():
    variants = (
        (_ENTRY_TWO_COLUMN,),
        (_ENTRY_TWO_COLUMN, _ENTRY_TWO_COLUMN),
        (_ENTRY_NESTED_FORM, _ENTRY_TWO_COLUMN),
        (_ENTRY_TWO_COLUMN | {"independent_stage_a_review_content_sha256": _ENTRY_NESTED_FORM["independent_stage_a_review_content_sha256"]}, _ENTRY_NESTED_FORM),
        (_ENTRY_TWO_COLUMN | {"reviewed_authority_content_sha256": _ENTRY_NESTED_FORM["reviewed_authority_content_sha256"]}, _ENTRY_NESTED_FORM),
    )
    for entries in variants:
        inventory = _inventory(entries)
        assert page_proof._inventory_is_complete(inventory, _expected_inventory_primitives()) is None
    assert page_proof._inventory_is_complete(_inventory(), _expected_inventory_primitives()) == _TOPOLOGY


def test_surrogate_and_non_child_hash_substitutes_never_complete():
    aggregate_hash = "b34b8342623b6b0ffe5e03d5c253c6f73be8ac54c82ef54d89d61ae8f7edbdad"
    variants = (
        _ENTRY_TWO_COLUMN | {"independent_stage_a_review_content_sha256": _SURROGATE},
        _ENTRY_TWO_COLUMN | {"independent_stage_a_review_content_sha256": aggregate_hash},
        _ENTRY_TWO_COLUMN | {"independent_stage_a_review_content_sha256": "f" * 64},
    )
    for first in variants:
        inventory = _inventory((first, _ENTRY_NESTED_FORM))
        assert page_proof._inventory_is_complete(inventory, _expected_inventory_primitives()) is None
    assert _SURROGATE not in b"".join(raw for case in _CASES for raw in case["leaf"]).decode("utf-8", errors="ignore")


def test_all_three_resealed_admission_rows_bind_exact_authoritative_inventory():
    rows = _admission_rows()
    assert all(page_proof._fixture_admission_is_valid(row) for row in rows)
    assert page_proof._fixture_admission_registry_is_valid(rows, _admission_primitives(), _TOPOLOGY)
    for case, row in zip(_CASES, rows):
        assert row.required_topology_inventory_content_sha256 == _TOPOLOGY
        assert row.pre_visual_binding_sha256 == case["p"] == _p(row)
        assert row.binding_sha256 == case["f"] == _f(row)
        assert row.witness_byte_length == case["w_len"]
        assert row.witness_sha256 == case["w_raw"]
        assert row.independent_visual_crosscheck_byte_length == case["v_len"]
        assert row.independent_visual_crosscheck_sha256 == case["v_raw"]


def test_all_three_resealed_compositions_preserve_literal_semantic_projection():
    for case in _CASES:
        result = _compose(case)
        assert result["flow"]["included_block_ids"] == case["included"]
        assert result["flow"]["excluded_block_ids"] == case["excluded"]
        assert tuple(row["fragment_id"] for row in result["flow"]["fragment_universe"]) == case["fragments"]
        assert tuple((row["source_fragment_id"], row["target_fragment_id"], row["boundary_kind"]) for row in result["flow"]["adjacency_universe"]) == case["adjacency"]
        assert result["visual_crosscheck"]["content_sha256"] == json.loads(case["leaf"][3])["content_sha256"]


def test_two_boundary_visual_evidence_reseals_without_semantic_drift():
    row = _two_boundary_row()
    assert row.pre_visual_binding_sha256 == _TWO_BOUNDARY["p"] == _p(row)
    assert row.binding_sha256 == _TWO_BOUNDARY["f"] == _f(row)
    assert row.witness_byte_length == _TWO_BOUNDARY["w_len"]
    assert row.witness_sha256 == _TWO_BOUNDARY["w_raw"]
    assert row.independent_visual_crosscheck_byte_length == _TWO_BOUNDARY["v_len"]
    assert row.independent_visual_crosscheck_sha256 == _TWO_BOUNDARY["v_raw"]
    mechanics, flow = _two_boundary_mechanics_and_flow()
    normalized = page_proof._normalize_fixture_visual_crosscheck(
        mechanics,
        flow,
        leaves.INDEPENDENT_VISUAL_CROSSCHECK_TWO_BOUNDARY_V1,
        row,
    )
    assert tuple(fragment["fragment_id"] for fragment in flow["fragment_universe"]) == _TWO_BOUNDARY["fragments"]
    assert tuple((edge["source_fragment_id"], edge["target_fragment_id"], edge["boundary_kind"]) for edge in flow["adjacency_universe"]) == _TWO_BOUNDARY["adjacency"]
    assert normalized["content_sha256"] == json.loads(leaves.INDEPENDENT_VISUAL_CROSSCHECK_TWO_BOUNDARY_V1)["content_sha256"]


def test_stale_p_w_v_f_each_fail_at_the_named_layer_and_inverse_repair_recovers():
    case = _CASES[0]
    leaf = case["leaf"]
    stale_p = replace(_row(case), pre_visual_binding_sha256="0" * 64)
    stale_w = _row(case, witness_raw=leaf[1] + b" ")
    stale_v = _row(case, crosscheck_raw=leaf[3] + b" ")
    stale_f = replace(_row(case), binding_sha256="0" * 64)
    for row in (stale_p, stale_w, stale_v, stale_f):
        with pytest.raises(RawPdfError, match=f"^{_ADMISSION_ERROR}$"):
            page_proof._normalize_fixture_page_proof_composition(_authority(case, leaf[1]), leaf[1], leaf[2], leaf[3], row)
    assert _compose(case)["flow"]["included_block_ids"] == ("b0", "b1")
    visual_value = json.loads(leaves.INDEPENDENT_VISUAL_CROSSCHECK_TWO_BOUNDARY_V1.decode("utf-8"))
    visual_value["pre_visual_evidence_core_sha256"] = "0" * 64
    bad_visual = _reseal_json(visual_value)
    bad_row = replace(_two_boundary_row(bad_visual), pre_visual_binding_sha256=_TWO_BOUNDARY["p"])
    bad_row = replace(bad_row, binding_sha256=_f(bad_row))
    mechanics, flow = _two_boundary_mechanics_and_flow()
    with pytest.raises(RawPdfError, match=f"^{_VISUAL_ERROR}$"):
        page_proof._normalize_fixture_visual_crosscheck(
            mechanics,
            flow,
            bad_visual,
            bad_row,
        )
    repaired = page_proof._normalize_fixture_visual_crosscheck(
        mechanics,
        flow,
        leaves.INDEPENDENT_VISUAL_CROSSCHECK_TWO_BOUNDARY_V1,
        _two_boundary_row(),
    )
    assert repaired["content_sha256"] == json.loads(leaves.INDEPENDENT_VISUAL_CROSSCHECK_TWO_BOUNDARY_V1)["content_sha256"]


def test_mixed_old_new_and_cross_pair_rows_fail_closed():
    rows = _admission_rows()
    old_digest_row = _reseal_row(replace(rows[0], required_topology_inventory_content_sha256=_SURROGATE))
    cross_pair = _reseal_row(replace(
        rows[0],
        witness_byte_length=rows[1].witness_byte_length,
        witness_sha256=rows[1].witness_sha256,
    ))
    assert not page_proof._fixture_admission_registry_is_valid((old_digest_row, rows[1], rows[2]), _admission_primitives(), _TOPOLOGY)
    assert not page_proof._fixture_admission_registry_is_valid((cross_pair, rows[1], rows[2]), _admission_primitives(), _TOPOLOGY)
    assert page_proof._fixture_admission_registry_is_valid(rows, _admission_primitives(), _TOPOLOGY)


def test_expected_output_hashes_remain_unconsumed_and_unreachable():
    source = ast.parse(inspect.getsource(page_proof))
    candidate_names = [
        node.attr for node in ast.walk(source)
        if isinstance(node, ast.Attribute) and node.attr in {"expected_candidate_sha256", "expected_reviewed_ledger_sha256"}
    ]
    assert candidate_names.count("expected_candidate_sha256") >= 1
    assert candidate_names.count("expected_reviewed_ledger_sha256") >= 1
    rows = _admission_rows()
    for row in rows:
        changed = _reseal_row(replace(row, expected_candidate_sha256="f" * 64))
        assert page_proof._fixture_admission_is_valid(changed)
    _poison_public_calls()


def test_production_roots_remain_inactive_and_public_poison_is_coverage_first():
    inventory = page_proof._PRODUCTION_REQUIRED_STAGE_A_TOPOLOGY_INVENTORY
    assert inventory.entries == ()
    assert inventory.entry_count == 0
    assert page_proof._PRODUCTION_EXPECTED_TOPOLOGY_PRIMITIVES[2] == ()
    assert page_proof._PRODUCTION_EXPECTED_TOPOLOGY_PRIMITIVES[3] == 0
    assert page_proof._PRODUCTION_FIXTURE_ADMISSION == ()
    assert page_proof._PRODUCTION_EXPECTED_FIXTURE_ADMISSION_PRIMITIVES == ()
    _poison_public_calls()


def test_static_containment_reproves_4b6_through_4b9():
    visual_source = _visual_tree()
    visual_calls = _all_visual_calls()
    functions = {node.name: node for node in visual_source.body if isinstance(node, ast.FunctionDef)}
    actual_target_tests = tuple(
        node.name for node in visual_source.body
        if isinstance(node, ast.FunctionDef)
        and node.name.startswith("test_visual_crosscheck_")
        and node.name.endswith("_target_only_repair")
    )
    assert len(visual_calls) == 98
    assert actual_target_tests == _EXPECTED_TARGET_NAMES
    assert set(functions) >= set(_EXPECTED_TARGET_NAMES) | set(_EXPECTED_POSITIVE_FIXTURE_NAMES) | set(_EXPECTED_OUTER_NAMES)
    pre_normalizer_exprs = [
        node for node in ast.walk(visual_source)
        if isinstance(node, ast.Expr) and _stmt_is_pre_normalizer_contract(node)
    ]
    assert len(pre_normalizer_exprs) == 96

    for name in _EXPECTED_POSITIVE_FIXTURE_NAMES:
        visual_stmt_indexes = [index for index, stmt in enumerate(functions[name].body) if _stmt_has_visual_call(stmt)]
        assert len(visual_stmt_indexes) == 1
        assert visual_stmt_indexes[0] > 0
        _contract_predicate_map(functions[name].body[visual_stmt_indexes[0] - 1])

    for name in _EXPECTED_TARGET_NAMES:
        visual_stmt_indexes = [index for index, stmt in enumerate(functions[name].body) if _stmt_has_visual_call(stmt)]
        assert len(visual_stmt_indexes) == 2
        for index in visual_stmt_indexes:
            assert index > 0
            _contract_predicate_map(functions[name].body[index - 1])

    for name in _EXPECTED_OUTER_NAMES:
        visual_stmt_indexes = [index for index, stmt in enumerate(functions[name].body) if _stmt_has_visual_call(stmt)]
        contract_stmt_indexes = [index for index, stmt in enumerate(functions[name].body) if _stmt_is_pre_normalizer_contract(stmt)]
        assert len(visual_stmt_indexes) == 1
        assert contract_stmt_indexes == []

    covered_call_count = (
        sum(len([stmt for stmt in functions[name].body if _stmt_has_visual_call(stmt)]) for name in _EXPECTED_POSITIVE_FIXTURE_NAMES)
        + sum(len([stmt for stmt in functions[name].body if _stmt_has_visual_call(stmt)]) for name in _EXPECTED_TARGET_NAMES)
        + sum(len([stmt for stmt in functions[name].body if _stmt_has_visual_call(stmt)]) for name in _EXPECTED_OUTER_NAMES)
    )
    assert covered_call_count == 98
    composition_tree = ast.parse(inspect.getsource(page_proof._normalize_fixture_page_proof_composition))
    composition_calls = [
        node.func.id for node in ast.walk(composition_tree)
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
    ]
    assert composition_calls.count("_normalize_fixture_witness_render_components") == 1
    assert composition_calls.count("_normalize_fixture_block_flow_adjacency") == 1
    assert composition_calls.count("_normalize_fixture_visual_crosscheck") == 1
    this_tree = ast.parse(inspect.getsource(test_static_containment_reproves_4b6_through_4b9))
    prohibited = {"open", "__import__", "eval", "exec", "compile", "subprocess", "importlib"}
    assert not any(isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id in prohibited for node in ast.walk(this_tree))
