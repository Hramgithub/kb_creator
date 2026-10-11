import dataclasses
import base64
import hashlib
import json
import ast
import inspect

import pytest

from kb_creator.pdf_raw import page_proof
from kb_creator.pdf_raw.errors import RawPdfError
from kb_creator.tests import _page_proof_fixture_leaves as leaves


_PRIVATE_TOPOLOGY_DIGEST = "4d3683f15ae64b4d03e51211755f2b3580e112e35bce4bf8c69efa29645dd3b4"
_VISUAL_CROSSCHECK_ERROR = "page_proof_visual_crosscheck_invalid"


def _canonical_json(value: object) -> bytes:
    return json.dumps(value, ensure_ascii=True, sort_keys=True, separators=(",", ":")).encode("utf-8")


def _sha256(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def _oracle_final_admission_binding_sha256(row: page_proof._FixtureAdmission) -> str:
    payload = {
        "fixture_id": row.fixture_id.decode("ascii"), "fixture_id_byte_length": row.fixture_id_byte_length,
        "fixture_id_sha256": row.fixture_id_sha256, "stage_a_fixture_id": row.stage_a_fixture_id,
        "stage_a_authority_content_sha256": row.stage_a_authority_content_sha256,
        "required_topology_inventory_content_sha256": row.required_topology_inventory_content_sha256,
        "render_png_byte_length": row.render_png_byte_length, "render_png_sha256": row.render_png_sha256,
        "witness_schema": "kb_creator.pdf_raw.PageProofWitnessV3", "visual_crosscheck_schema": "kb_creator.pdf_raw.IndependentPageVisualCrossCheckV2",
        "pre_visual_binding_sha256": row.pre_visual_binding_sha256, "witness_byte_length": row.witness_byte_length,
        "witness_sha256": row.witness_sha256, "independent_visual_crosscheck_byte_length": row.independent_visual_crosscheck_byte_length,
        "independent_visual_crosscheck_sha256": row.independent_visual_crosscheck_sha256,
    }
    return _sha256(b"page-proof.fixture-admission.v2\0" + _canonical_json(payload))


def _oracle_pre_visual_binding_sha256(row: page_proof._FixtureAdmission) -> str:
    payload = {
        "fixture_id": row.fixture_id.decode("ascii"), "fixture_id_byte_length": row.fixture_id_byte_length,
        "fixture_id_sha256": row.fixture_id_sha256, "stage_a_fixture_id": row.stage_a_fixture_id,
        "stage_a_authority_content_sha256": row.stage_a_authority_content_sha256,
        "required_topology_inventory_content_sha256": row.required_topology_inventory_content_sha256,
        "render_png_byte_length": row.render_png_byte_length, "render_png_sha256": row.render_png_sha256,
        "witness_schema": "kb_creator.pdf_raw.PageProofWitnessV3",
        "visual_crosscheck_schema": "kb_creator.pdf_raw.IndependentPageVisualCrossCheckV2",
    }
    return _sha256(b"page-proof.fixture-pre-visual-binding.v1\0" + _canonical_json(payload))


def _b64(raw: bytes) -> str:
    return base64.b64encode(raw).decode("ascii")


def _case_rows():
    return (
        (
            page_proof._FixtureAdmission(
                fixture_id=leaves.TWO_COLUMN[0],
                fixture_id_byte_length=leaves.TWO_COLUMN_LENGTHS[0],
                fixture_id_sha256=leaves.TWO_COLUMN_SHA256[0],
                stage_a_fixture_id="stage-a.positive-two-column.v1",
                stage_a_authority_content_sha256="890a9cef3ce995e7cb7881c035baa3e1e5a4c782f1827847b640c93fb28eafef",
                required_topology_inventory_content_sha256=_PRIVATE_TOPOLOGY_DIGEST,
                witness_byte_length=leaves.TWO_COLUMN_LENGTHS[1],
                witness_sha256=leaves.TWO_COLUMN_SHA256[1],
                render_png_byte_length=leaves.TWO_COLUMN_LENGTHS[2],
                render_png_sha256=leaves.TWO_COLUMN_SHA256[2],
                independent_visual_crosscheck_byte_length=leaves.INDEPENDENT_VISUAL_CROSSCHECK_LENGTHS[0],
                independent_visual_crosscheck_sha256=leaves.INDEPENDENT_VISUAL_CROSSCHECK_SHA256[0],
                pre_visual_binding_sha256="cdb993a29ef0b05229a9a9c5dfd65dd30977df9c3ec1c295a88a94b5ea1f9c1d",
        binding_sha256="0c45fd6b6440482b377fbcd3c6797701e622250dc0fdd496d18dbef81cd48838",
                expected_candidate_sha256="9bc92192ee0e03282585b83d6902b9367b1960b897c20da0c0c7240725c73e21",
                expected_reviewed_ledger_sha256="91ceaadb97a611699e648ca865be60951709f09b1c5cf555ceb1f3c94cf427c0",
            ),
            leaves.WITNESS_TWO_COLUMN_V1,
            leaves.RENDER_PNG_TWO_COLUMN_V1,
            leaves.INDEPENDENT_VISUAL_CROSSCHECK_TWO_COLUMN_V1,
            {
                "blocks": [
                    {
                        "block_id": "b0",
                        "block_ordinal": 0,
                        "atom_row_ids": ["atom-0"],
                        "component_ids": ["f35948e50a49215aabc5e3f390a63876930fde2cf014486ed16ca4d305c679d5"],
                        "fragment_ids": ["f0"],
                        "column_index": 1,
                        "flow_flags": {
                            "running_marginal": False,
                            "occluded": False,
                            "text_layer_disagreement": False,
                            "visual_only": False,
                        },
                    },
                    {
                        "block_id": "b1",
                        "block_ordinal": 1,
                        "atom_row_ids": ["atom-1"],
                        "component_ids": ["037e747de4a6f894a091d68d007142c0dd8e1da1f33ba41527f9b48ea8a7795d"],
                        "fragment_ids": ["f1"],
                        "column_index": 0,
                        "flow_flags": {
                            "running_marginal": False,
                            "occluded": False,
                            "text_layer_disagreement": False,
                            "visual_only": False,
                        },
                    },
                ],
                "included_block_ids": ["b0", "b1"],
                "excluded_block_ids": [],
                "adjacency_rows": [
                    {
                        "source_fragment_id": "f0",
                        "target_fragment_id": "f1",
                        "boundary_kind": "cross_column",
                        "source_block_id": "b0",
                        "target_block_id": "b1",
                    }
                ],
            },
            {
                "content_sha256": "d38f51bba2b575528a32b572084b12ba2be33060e972ad7138a70eee9d580f73",
                "block_ids": ["b0", "b1"],
                "block_reasons": ["included", "included"],
                "transcriptions": [b"LEFT", b"RIGHT"],
                "boundary_pairs": [("f0", "f1", "cross_column")],
                "pre_visual_evidence_core_sha256": "3e53b5eaf8f8aa2630e831f12ae9606abba85e2db1d64eea974ff9da258903b6",
            },
        ),
        (
            page_proof._FixtureAdmission(
                fixture_id=leaves.NESTED_FORM[0],
                fixture_id_byte_length=leaves.NESTED_FORM_LENGTHS[0],
                fixture_id_sha256=leaves.NESTED_FORM_SHA256[0],
                stage_a_fixture_id="stage-a.positive-nested-form.v1",
                stage_a_authority_content_sha256="8726e5d36b7acba9d96eacdcd62a57da00d7f4cfdd4df79cd6c63106d2e353e7",
                required_topology_inventory_content_sha256=_PRIVATE_TOPOLOGY_DIGEST,
                witness_byte_length=leaves.NESTED_FORM_LENGTHS[1],
                witness_sha256=leaves.NESTED_FORM_SHA256[1],
                render_png_byte_length=leaves.NESTED_FORM_LENGTHS[2],
                render_png_sha256=leaves.NESTED_FORM_SHA256[2],
                independent_visual_crosscheck_byte_length=leaves.INDEPENDENT_VISUAL_CROSSCHECK_LENGTHS[1],
                independent_visual_crosscheck_sha256=leaves.INDEPENDENT_VISUAL_CROSSCHECK_SHA256[1],
                pre_visual_binding_sha256="388f7cc61345dbbcb516a4090e0d35cabb308f37137bf9b6b86c691fbf6c122c",
        binding_sha256="249d56182c4710e6392740703ed86d388b714498d1bbc9c60e403de0caf0fbf2",
                expected_candidate_sha256="c91d828ac9d5225df07efa76d0f854717ae67c5fb193d427f1992ab51631e929",
                expected_reviewed_ledger_sha256="a3382a5a0c432967419b6266156d1b132e22ef7f44ecc8ea8043b75da7d93d7b",
            ),
            leaves.WITNESS_NESTED_FORM_V1,
            leaves.RENDER_PNG_NESTED_FORM_V1,
            leaves.INDEPENDENT_VISUAL_CROSSCHECK_NESTED_FORM_V1,
            {
                "blocks": [
                    {
                        "block_id": "b0",
                        "block_ordinal": 0,
                        "atom_row_ids": ["atom-0"],
                        "component_ids": ["6301561cbbb1713825a5791b8c2b7372828f66428a0751c76e98ea8f2ade6cb9"],
                        "fragment_ids": ["n0"],
                        "column_index": 0,
                        "flow_flags": {
                            "running_marginal": False,
                            "occluded": False,
                            "text_layer_disagreement": False,
                            "visual_only": False,
                        },
                    },
                    {
                        "block_id": "b1",
                        "block_ordinal": 1,
                        "atom_row_ids": ["atom-1"],
                        "component_ids": ["0cf5151e4d5c9ec50252a5949e7dded0f358d2694d08761f165778ec821e8357"],
                        "fragment_ids": ["n1"],
                        "column_index": 0,
                        "flow_flags": {
                            "running_marginal": True,
                            "occluded": False,
                            "text_layer_disagreement": False,
                            "visual_only": False,
                        },
                    },
                ],
                "included_block_ids": ["b0"],
                "excluded_block_ids": ["b1"],
                "adjacency_rows": [],
            },
            {
                "content_sha256": "f332b60fd1107f66ccff5e497a071f8438be9dc4d5e1e6c22734b9abbb6dbc97",
                "block_ids": ["b0", "b1"],
                "block_reasons": ["included", "running_marginal"],
                "transcriptions": [b"FORM", b"MARGIN"],
                "boundary_pairs": [],
                "pre_visual_evidence_core_sha256": "997a208c30acc7bc9c2c91031096bf656734c2f2529c4818951853f305a17bb5",
            },
        ),
        (
            page_proof._FixtureAdmission(
                fixture_id=leaves.VISUAL_ONLY[0],
                fixture_id_byte_length=leaves.VISUAL_ONLY_LENGTHS[0],
                fixture_id_sha256=leaves.VISUAL_ONLY_SHA256[0],
                stage_a_fixture_id="stage-a.identity-single-use.v1",
                stage_a_authority_content_sha256="e10859438e4ccef9ea6fdff9c8e3c923e71f39c4ae1b2c6a420d4319a1c468ed",
                required_topology_inventory_content_sha256=_PRIVATE_TOPOLOGY_DIGEST,
                witness_byte_length=leaves.VISUAL_ONLY_LENGTHS[1],
                witness_sha256=leaves.VISUAL_ONLY_SHA256[1],
                render_png_byte_length=leaves.VISUAL_ONLY_LENGTHS[2],
                render_png_sha256=leaves.VISUAL_ONLY_SHA256[2],
                independent_visual_crosscheck_byte_length=leaves.INDEPENDENT_VISUAL_CROSSCHECK_LENGTHS[2],
                independent_visual_crosscheck_sha256=leaves.INDEPENDENT_VISUAL_CROSSCHECK_SHA256[2],
                pre_visual_binding_sha256="7f9327e3dba8c5ad888efa3423115e779b0bb0502438e7ddd9c02cd2c43dbea2",
        binding_sha256="4d9c98331427c55f788ee2fc532365434054e6d300236120fc11946c7894aecd",
                expected_candidate_sha256="98f9ccd0bf6d8c02a977472fcad6ac9feed628fd6a2943464307b9f4860d744a",
                expected_reviewed_ledger_sha256="696cac67d638d93b51d4d475e34205cf5b4f432fcc517c21bdab6c51a9e8ccd3",
            ),
            leaves.WITNESS_VISUAL_ONLY_V1,
            leaves.RENDER_PNG_VISUAL_ONLY_V1,
            leaves.INDEPENDENT_VISUAL_CROSSCHECK_VISUAL_ONLY_V1,
            {
                "blocks": [
                    {
                        "block_id": "b0",
                        "block_ordinal": 0,
                        "atom_row_ids": ["atom-0"],
                        "component_ids": ["7d6f2fa25b2be7b9918ffd01feb4fc06b68c9945dc881804b2c578465a1360a2"],
                        "fragment_ids": ["v0"],
                        "column_index": 0,
                        "flow_flags": {
                            "running_marginal": False,
                            "occluded": False,
                            "text_layer_disagreement": False,
                            "visual_only": True,
                        },
                    }
                ],
                "included_block_ids": [],
                "excluded_block_ids": ["b0"],
                "adjacency_rows": [],
            },
            {
                "content_sha256": "7995e65505d53305ff53811e0221b64496d93bf8b8a29a753d9683d0c1ac2f1f",
                "block_ids": ["b0"],
                "block_reasons": ["visual_only"],
                "transcriptions": [b"IMAGE"],
                "boundary_pairs": [],
                "pre_visual_evidence_core_sha256": "f7ee0ef14756eccdf2bdcfd9df727a800a118834f6c373f2892a4b394888ab65",
            },
        ),
    )


def _authority_for(row: page_proof._FixtureAdmission, witness_raw: bytes) -> page_proof.RawAtomProvenanceAuthorityV1:
    witness = json.loads(witness_raw.decode("utf-8"))
    atoms = [{"atom_ordinal": item["atom_ordinal"], "atom_row_id": item["atom_row_id"]} for item in witness["atom_geometry_rows"]]
    raw = _canonical_json({
        "schema": "kb_creator.pdf_raw.RawAtomProvenanceAuthority.v1",
        "fixture": {"id": row.stage_a_fixture_id},
        "terminal_state": "fixture_only_authority",
        "content_sha256": row.stage_a_authority_content_sha256,
        "atoms": atoms,
    })
    authority = object.__new__(page_proof.RawAtomProvenanceAuthorityV1)
    object.__setattr__(authority, "_raw", raw)
    object.__setattr__(authority, "_fixture_id", row.stage_a_fixture_id)
    object.__setattr__(authority, "_content_sha256", row.stage_a_authority_content_sha256)
    object.__setattr__(authority, "_terminal_state", "fixture_only_authority")
    object.__setattr__(authority, "_sealed", True)
    return authority


def _normalized_case(case_index: int) -> tuple[page_proof._FixtureAdmission, dict[str, object], dict[str, object], bytes, dict[str, object]]:
    row, witness_raw, render_raw, crosscheck_raw, flow_input, expected = _case_rows()[case_index]
    mechanics = page_proof._normalize_fixture_witness_render_components(
        _authority_for(row, witness_raw),
        witness_raw,
        render_raw,
        row,
    )
    flow = page_proof._normalize_fixture_block_flow_adjacency(mechanics, flow_input)
    return row, mechanics, flow, crosscheck_raw, expected


def _block_payload(value: dict[str, object]) -> dict[str, object]:
    return {
        "block_id": value["block_id"],
        "block_ordinal": value["block_ordinal"],
        "reading_flow_disposition": value["reading_flow_disposition"],
        "reading_flow_reason": value["reading_flow_reason"],
        "column_index": value["column_index"],
        "bbox_px": value["bbox_px"],
        "pixel_count": value["pixel_count"],
        "component_evidence_sha256": value["component_evidence_sha256"],
        "transcription_bytes_b64": value["transcription_bytes_b64"],
        "transcription_sha256": value["transcription_sha256"],
        "witness_decision": value["witness_decision"],
        "decision_reason": value["decision_reason"],
    }


def _block_sha(value: dict[str, object]) -> str:
    return _sha256(b"page-proof.visual-crosscheck-block-decision.v1\0" + _canonical_json(_block_payload(value)))


def _boundary_payload(value: dict[str, object]) -> dict[str, object]:
    return {
        "source_fragment_id": value["source_fragment_id"],
        "target_fragment_id": value["target_fragment_id"],
        "boundary_kind": value["boundary_kind"],
        "source_block_id": value["source_block_id"],
        "target_block_id": value["target_block_id"],
        "source_column_index": value["source_column_index"],
        "target_column_index": value["target_column_index"],
        "boundary_bbox_px": value["boundary_bbox_px"],
        "decision": value["decision"],
        "decision_reason": value["decision_reason"],
    }


def _boundary_sha(value: dict[str, object]) -> str:
    return _sha256(b"page-proof.visual-crosscheck-boundary-decision.v1\0" + _canonical_json(_boundary_payload(value)))


def _inventory_sha(block_hashes: tuple[str, ...], boundary_hashes: tuple[str, ...]) -> str:
    return _sha256(b"page-proof.visual-crosscheck-decision-inventory.v1\0" + _canonical_json({
        "block_decision_sha256s": list(block_hashes),
        "boundary_decision_sha256s": list(boundary_hashes),
        "confirmed_block_count": len(block_hashes),
        "confirmed_boundary_count": len(boundary_hashes),
    }))


def _parse_crosscheck(raw: bytes) -> dict[str, object]:
    return json.loads(raw.decode("utf-8"))


def _seal_crosscheck(value: dict[str, object], *, keep_block_digest_index: int | None = None, keep_boundary_digest_index: int | None = None, keep_inventory_digest: bool = False, keep_content_sha: bool = False) -> bytes:
    block_hashes = []
    for index, row in enumerate(value["block_checks"]):
        if index != keep_block_digest_index:
            row["decision_sha256"] = _block_sha(row)
        block_hashes.append(row["decision_sha256"])
    boundary_hashes = []
    for index, row in enumerate(value["boundary_checks"]):
        if index != keep_boundary_digest_index:
            row["decision_sha256"] = _boundary_sha(row)
        boundary_hashes.append(row["decision_sha256"])
    inventory = value["decision_inventory"]
    inventory["block_decision_sha256s"] = list(block_hashes)
    inventory["boundary_decision_sha256s"] = list(boundary_hashes)
    inventory["confirmed_block_count"] = len(block_hashes)
    inventory["confirmed_boundary_count"] = len(boundary_hashes)
    if not keep_inventory_digest:
        inventory["inventory_sha256"] = _inventory_sha(tuple(block_hashes), tuple(boundary_hashes))
    if not keep_content_sha:
        value["content_sha256"] = _sha256(_canonical_json({key: item for key, item in value.items() if key != "content_sha256"}))
    return _canonical_json(value)


def _reseal_admission_row_for_crosscheck(row: page_proof._FixtureAdmission, crosscheck_raw: bytes) -> page_proof._FixtureAdmission:
    updated = dataclasses.replace(row, independent_visual_crosscheck_byte_length=len(crosscheck_raw), independent_visual_crosscheck_sha256=_sha256(crosscheck_raw), binding_sha256="0" * 64)
    return dataclasses.replace(updated, binding_sha256=_oracle_final_admission_binding_sha256(updated))


_PREDICATE_KEYS = (
    "fixture_pre_visual_binding_is_valid",
    "fixture_admission_is_valid",
    "fixture_admission_row_matches_derive_leaves",
    "visual_crosscheck_leaf_matches_admission",
    "visual_crosscheck_root_binding_matches",
    "visual_crosscheck_root_context_matches",
    "visual_crosscheck_reviewer_matches_contract",
    "visual_crosscheck_cardinality_matches",
    "visual_crosscheck_block_region_matches",
    "visual_crosscheck_block_transcription_matches",
    "visual_crosscheck_block_decision_matches",
    "visual_crosscheck_boundary_region_matches",
    "visual_crosscheck_boundary_decision_matches",
    "visual_crosscheck_inventory_matches",
    "visual_crosscheck_content_seal_matches",
)


def _assert_pre_normalizer_contract(*, row: page_proof._FixtureAdmission, witness_raw: bytes, render_png_raw: bytes, crosscheck_raw: bytes, mechanics: dict[str, object], flow: dict[str, object], expected_predicates: dict[str, bool]) -> None:
    assert tuple(expected_predicates) == _PREDICATE_KEYS
    assert row.pre_visual_binding_sha256 == _oracle_pre_visual_binding_sha256(row)
    assert row.binding_sha256 == _oracle_final_admission_binding_sha256(row)
    assert (row.witness_byte_length, row.witness_sha256) == (len(witness_raw), _sha256(witness_raw))
    assert (row.render_png_byte_length, row.render_png_sha256) == (len(render_png_raw), _sha256(render_png_raw))
    root = _parse_crosscheck(crosscheck_raw)
    assert crosscheck_raw == _canonical_json(root)
    assert set(root) == set(page_proof._VISUAL_CROSSCHECK_ROOT_KEYS)
    blocks, adjacency = flow["blocks"], flow["adjacency_universe"]
    components = {item["component_id"]: item for item in mechanics["visual_components"]}
    block_rows, boundary_rows = root["block_checks"], root["boundary_checks"]
    block_regions, block_transcriptions, block_decisions = [], [], []
    for index, (actual, expected) in enumerate(zip(block_rows, blocks)):
        component_rows = tuple(components[item] for item in expected["component_ids"])
        block_regions.append(page_proof._visual_crosscheck_block_region_matches(actual, expected, index, component_rows))
        block_transcriptions.append(page_proof._visual_crosscheck_block_transcription_matches(actual))
        block_decisions.append(page_proof._visual_crosscheck_block_decision_matches(actual))
    lookup = {item["block_id"]: item for item in blocks}
    boundary_regions, boundary_decisions = [], []
    for actual, expected in zip(boundary_rows, adjacency):
        source, target = lookup[expected["source_block_id"]], lookup[expected["target_block_id"]]
        source_components = tuple(components[item] for item in source["component_ids"])
        target_components = tuple(components[item] for item in target["component_ids"])
        boundary_regions.append(page_proof._visual_crosscheck_boundary_region_matches(actual, expected, source, target, source_components, target_components))
        boundary_decisions.append(page_proof._visual_crosscheck_boundary_decision_matches(actual))
    block_hashes = tuple(item["decision_sha256"] for item in block_rows)
    boundary_hashes = tuple(item["decision_sha256"] for item in boundary_rows)
    assert {
        "fixture_pre_visual_binding_is_valid": page_proof._fixture_pre_visual_binding_is_valid(row),
        "fixture_admission_is_valid": page_proof._fixture_admission_is_valid(row),
        "fixture_admission_row_matches_derive_leaves": page_proof._fixture_admission_row_matches_derive_leaves(row, witness_raw, render_png_raw, crosscheck_raw),
        "visual_crosscheck_leaf_matches_admission": page_proof._visual_crosscheck_leaf_matches_admission(crosscheck_raw, row),
        "visual_crosscheck_root_binding_matches": page_proof._visual_crosscheck_root_binding_matches(root, row),
        "visual_crosscheck_root_context_matches": page_proof._visual_crosscheck_root_context_matches(root, row, flow["pre_visual_evidence_core_sha256"]),
        "visual_crosscheck_reviewer_matches_contract": page_proof._visual_crosscheck_reviewer_matches_contract(root),
        "visual_crosscheck_cardinality_matches": page_proof._visual_crosscheck_cardinality_matches(block_rows, boundary_rows, blocks, adjacency),
        "visual_crosscheck_block_region_matches": all(block_regions),
        "visual_crosscheck_block_transcription_matches": all(block_transcriptions),
        "visual_crosscheck_block_decision_matches": all(block_decisions),
        "visual_crosscheck_boundary_region_matches": all(boundary_regions),
        "visual_crosscheck_boundary_decision_matches": all(boundary_decisions),
        "visual_crosscheck_inventory_matches": page_proof._visual_crosscheck_inventory_matches(root["decision_inventory"], block_hashes, boundary_hashes),
        "visual_crosscheck_content_seal_matches": page_proof._visual_crosscheck_content_seal_matches(root),
    } == expected_predicates


def _two_boundary_case():
    row = page_proof._FixtureAdmission(fixture_id=leaves.TWO_COLUMN[0], fixture_id_byte_length=33, fixture_id_sha256=leaves.TWO_BOUNDARY_V1_SHA256[0], stage_a_fixture_id="stage-a.positive-two-column.v1", stage_a_authority_content_sha256="890a9cef3ce995e7cb7881c035baa3e1e5a4c782f1827847b640c93fb28eafef", required_topology_inventory_content_sha256=_PRIVATE_TOPOLOGY_DIGEST, render_png_byte_length=119, render_png_sha256=leaves.TWO_BOUNDARY_V1_SHA256[2], pre_visual_binding_sha256=leaves.TWO_BOUNDARY_PRE_VISUAL_BINDING_SHA256, witness_byte_length=3186, witness_sha256=leaves.TWO_BOUNDARY_V1_SHA256[1], independent_visual_crosscheck_byte_length=2928, independent_visual_crosscheck_sha256=leaves.TWO_BOUNDARY_V1_SHA256[3], binding_sha256=leaves.TWO_BOUNDARY_FINAL_BINDING_SHA256, expected_candidate_sha256="9bc92192ee0e03282585b83d6902b9367b1960b897c20da0c0c7240725c73e21", expected_reviewed_ledger_sha256="91ceaadb97a611699e648ca865be60951709f09b1c5cf555ceb1f3c94cf427c0")
    witness_raw, render_raw, crosscheck_raw = leaves.WITNESS_TWO_BOUNDARY_V1, leaves.RENDER_PNG_TWO_COLUMN_V1, leaves.INDEPENDENT_VISUAL_CROSSCHECK_TWO_BOUNDARY_V1
    flow_input = {"blocks": [{"block_id": "b0", "block_ordinal": 0, "atom_row_ids": ["atom-0"], "component_ids": ["f35948e50a49215aabc5e3f390a63876930fde2cf014486ed16ca4d305c679d5"], "fragment_ids": ["f0", "f1"], "column_index": 1, "flow_flags": {"running_marginal": False, "occluded": False, "text_layer_disagreement": False, "visual_only": False}}, {"block_id": "b1", "block_ordinal": 1, "atom_row_ids": ["atom-1"], "component_ids": ["037e747de4a6f894a091d68d007142c0dd8e1da1f33ba41527f9b48ea8a7795d"], "fragment_ids": ["f2"], "column_index": 0, "flow_flags": {"running_marginal": False, "occluded": False, "text_layer_disagreement": False, "visual_only": False}}], "included_block_ids": ["b0", "b1"], "excluded_block_ids": [], "adjacency_rows": [{"source_fragment_id": "f0", "target_fragment_id": "f1", "boundary_kind": "within_block", "source_block_id": "b0", "target_block_id": "b0"}, {"source_fragment_id": "f1", "target_fragment_id": "f2", "boundary_kind": "cross_column", "source_block_id": "b0", "target_block_id": "b1"}]}
    mechanics = page_proof._normalize_fixture_witness_render_components(_authority_for(row, witness_raw), witness_raw, render_raw, row)
    flow = page_proof._normalize_fixture_block_flow_adjacency(mechanics, flow_input)
    return row, witness_raw, render_raw, crosscheck_raw, mechanics, flow



@pytest.fixture(scope="module")
def positive_two_column_normalized_case():
    row, mechanics, flow, raw, expected = _normalized_case(0)
    _assert_pre_normalizer_contract(row=row, witness_raw=leaves.WITNESS_TWO_COLUMN_V1, render_png_raw=leaves.RENDER_PNG_TWO_COLUMN_V1, crosscheck_raw=raw, mechanics=mechanics, flow=flow, expected_predicates={
            "fixture_pre_visual_binding_is_valid": True,
            "fixture_admission_is_valid": True,
            "fixture_admission_row_matches_derive_leaves": True,
            "visual_crosscheck_leaf_matches_admission": True,
            "visual_crosscheck_root_binding_matches": True,
            "visual_crosscheck_root_context_matches": True,
            "visual_crosscheck_reviewer_matches_contract": True,
            "visual_crosscheck_cardinality_matches": True,
            "visual_crosscheck_block_region_matches": True,
            "visual_crosscheck_block_transcription_matches": True,
            "visual_crosscheck_block_decision_matches": True,
            "visual_crosscheck_boundary_region_matches": True,
            "visual_crosscheck_boundary_decision_matches": True,
            "visual_crosscheck_inventory_matches": True,
            "visual_crosscheck_content_seal_matches": True,
        })
    normalized = page_proof._normalize_fixture_visual_crosscheck(mechanics, flow, raw, row)
    assert normalized["content_sha256"] == expected["content_sha256"]
    return row, mechanics, flow, raw, normalized


@pytest.fixture(scope="module")
def positive_nested_form_normalized_case():
    row, mechanics, flow, raw, expected = _normalized_case(1)
    _assert_pre_normalizer_contract(row=row, witness_raw=leaves.WITNESS_NESTED_FORM_V1, render_png_raw=leaves.RENDER_PNG_NESTED_FORM_V1, crosscheck_raw=raw, mechanics=mechanics, flow=flow, expected_predicates={
            "fixture_pre_visual_binding_is_valid": True,
            "fixture_admission_is_valid": True,
            "fixture_admission_row_matches_derive_leaves": True,
            "visual_crosscheck_leaf_matches_admission": True,
            "visual_crosscheck_root_binding_matches": True,
            "visual_crosscheck_root_context_matches": True,
            "visual_crosscheck_reviewer_matches_contract": True,
            "visual_crosscheck_cardinality_matches": True,
            "visual_crosscheck_block_region_matches": True,
            "visual_crosscheck_block_transcription_matches": True,
            "visual_crosscheck_block_decision_matches": True,
            "visual_crosscheck_boundary_region_matches": True,
            "visual_crosscheck_boundary_decision_matches": True,
            "visual_crosscheck_inventory_matches": True,
            "visual_crosscheck_content_seal_matches": True,
        })
    normalized = page_proof._normalize_fixture_visual_crosscheck(mechanics, flow, raw, row)
    assert normalized["content_sha256"] == expected["content_sha256"]
    return row, mechanics, flow, raw, normalized


@pytest.fixture(scope="module")
def positive_visual_only_normalized_case():
    row, mechanics, flow, raw, expected = _normalized_case(2)
    _assert_pre_normalizer_contract(row=row, witness_raw=leaves.WITNESS_VISUAL_ONLY_V1, render_png_raw=leaves.RENDER_PNG_VISUAL_ONLY_V1, crosscheck_raw=raw, mechanics=mechanics, flow=flow, expected_predicates={
            "fixture_pre_visual_binding_is_valid": True,
            "fixture_admission_is_valid": True,
            "fixture_admission_row_matches_derive_leaves": True,
            "visual_crosscheck_leaf_matches_admission": True,
            "visual_crosscheck_root_binding_matches": True,
            "visual_crosscheck_root_context_matches": True,
            "visual_crosscheck_reviewer_matches_contract": True,
            "visual_crosscheck_cardinality_matches": True,
            "visual_crosscheck_block_region_matches": True,
            "visual_crosscheck_block_transcription_matches": True,
            "visual_crosscheck_block_decision_matches": True,
            "visual_crosscheck_boundary_region_matches": True,
            "visual_crosscheck_boundary_decision_matches": True,
            "visual_crosscheck_inventory_matches": True,
            "visual_crosscheck_content_seal_matches": True,
        })
    normalized = page_proof._normalize_fixture_visual_crosscheck(mechanics, flow, raw, row)
    assert normalized["content_sha256"] == expected["content_sha256"]
    return row, mechanics, flow, raw, normalized


@pytest.fixture(scope="module")
def positive_two_boundary_normalized_case():
    row, witness_raw, render_png_raw, raw, mechanics, flow = _two_boundary_case()
    assert (len(row.fixture_id), row.witness_byte_length, row.render_png_byte_length, row.independent_visual_crosscheck_byte_length) == leaves.TWO_BOUNDARY_V1_LENGTHS
    assert (row.fixture_id_sha256, row.witness_sha256, row.render_png_sha256, row.independent_visual_crosscheck_sha256) == leaves.TWO_BOUNDARY_V1_SHA256
    assert row.pre_visual_binding_sha256 == leaves.TWO_BOUNDARY_PRE_VISUAL_BINDING_SHA256
    assert row.binding_sha256 == leaves.TWO_BOUNDARY_FINAL_BINDING_SHA256
    assert _oracle_pre_visual_binding_sha256(row) == leaves.TWO_BOUNDARY_PRE_VISUAL_BINDING_SHA256
    assert _oracle_final_admission_binding_sha256(row) == leaves.TWO_BOUNDARY_FINAL_BINDING_SHA256
    assert _parse_crosscheck(raw)["pre_visual_evidence_core_sha256"] == leaves.TWO_BOUNDARY_EXPECTED_PRE_VISUAL_CORE_SHA256
    _assert_pre_normalizer_contract(row=row, witness_raw=witness_raw, render_png_raw=render_png_raw, crosscheck_raw=raw, mechanics=mechanics, flow=flow, expected_predicates={
            "fixture_pre_visual_binding_is_valid": True,
            "fixture_admission_is_valid": True,
            "fixture_admission_row_matches_derive_leaves": True,
            "visual_crosscheck_leaf_matches_admission": True,
            "visual_crosscheck_root_binding_matches": True,
            "visual_crosscheck_root_context_matches": True,
            "visual_crosscheck_reviewer_matches_contract": True,
            "visual_crosscheck_cardinality_matches": True,
            "visual_crosscheck_block_region_matches": True,
            "visual_crosscheck_block_transcription_matches": True,
            "visual_crosscheck_block_decision_matches": True,
            "visual_crosscheck_boundary_region_matches": True,
            "visual_crosscheck_boundary_decision_matches": True,
            "visual_crosscheck_inventory_matches": True,
            "visual_crosscheck_content_seal_matches": True,
        })
    normalized = page_proof._normalize_fixture_visual_crosscheck(mechanics, flow, raw, row)
    return row, witness_raw, render_png_raw, raw, mechanics, flow, normalized


def test_positive_literal_crosscheck_fixtures_execute(positive_two_column_normalized_case, positive_nested_form_normalized_case, positive_visual_only_normalized_case, positive_two_boundary_normalized_case):
    assert all(case[-1]["content_sha256"] for case in (positive_two_column_normalized_case, positive_nested_form_normalized_case, positive_visual_only_normalized_case, positive_two_boundary_normalized_case))


def test_visual_crosscheck_root_pre_visual_binding_target_only_repair(positive_two_boundary_normalized_case):
    baseline_row, witness_raw, render_png_raw, baseline_raw, mechanics, flow, baseline_normalized = positive_two_boundary_normalized_case
    value = _parse_crosscheck(leaves.INDEPENDENT_VISUAL_CROSSCHECK_TWO_BOUNDARY_V1)
    value["pre_visual_binding_sha256"] = "0" * 64
    mutated_raw = _seal_crosscheck(value)
    mutated_row = _reseal_admission_row_for_crosscheck(baseline_row, mutated_raw)
    _assert_pre_normalizer_contract(row=mutated_row, witness_raw=witness_raw, render_png_raw=render_png_raw, crosscheck_raw=mutated_raw, mechanics=mechanics, flow=flow, expected_predicates={
            "fixture_pre_visual_binding_is_valid": True,
            "fixture_admission_is_valid": True,
            "fixture_admission_row_matches_derive_leaves": True,
            "visual_crosscheck_leaf_matches_admission": True,
            "visual_crosscheck_root_binding_matches": False,
            "visual_crosscheck_root_context_matches": True,
            "visual_crosscheck_reviewer_matches_contract": True,
            "visual_crosscheck_cardinality_matches": True,
            "visual_crosscheck_block_region_matches": True,
            "visual_crosscheck_block_transcription_matches": True,
            "visual_crosscheck_block_decision_matches": True,
            "visual_crosscheck_boundary_region_matches": True,
            "visual_crosscheck_boundary_decision_matches": True,
            "visual_crosscheck_inventory_matches": True,
            "visual_crosscheck_content_seal_matches": True,
        })
    with pytest.raises(RawPdfError, match="^page_proof_visual_crosscheck_invalid$"):
        page_proof._normalize_fixture_visual_crosscheck(mechanics, flow, mutated_raw, mutated_row)
    value["pre_visual_binding_sha256"] = baseline_row.pre_visual_binding_sha256
    repaired_raw = _seal_crosscheck(value)
    repaired_row = _reseal_admission_row_for_crosscheck(baseline_row, repaired_raw)
    assert repaired_raw == baseline_raw
    _assert_pre_normalizer_contract(row=repaired_row, witness_raw=witness_raw, render_png_raw=render_png_raw, crosscheck_raw=repaired_raw, mechanics=mechanics, flow=flow, expected_predicates={
            "fixture_pre_visual_binding_is_valid": True,
            "fixture_admission_is_valid": True,
            "fixture_admission_row_matches_derive_leaves": True,
            "visual_crosscheck_leaf_matches_admission": True,
            "visual_crosscheck_root_binding_matches": True,
            "visual_crosscheck_root_context_matches": True,
            "visual_crosscheck_reviewer_matches_contract": True,
            "visual_crosscheck_cardinality_matches": True,
            "visual_crosscheck_block_region_matches": True,
            "visual_crosscheck_block_transcription_matches": True,
            "visual_crosscheck_block_decision_matches": True,
            "visual_crosscheck_boundary_region_matches": True,
            "visual_crosscheck_boundary_decision_matches": True,
            "visual_crosscheck_inventory_matches": True,
            "visual_crosscheck_content_seal_matches": True,
        })
    repaired_normalized = page_proof._normalize_fixture_visual_crosscheck(mechanics, flow, repaired_raw, repaired_row)
    assert _canonical_json(repaired_normalized) == _canonical_json(baseline_normalized)


def test_visual_crosscheck_root_topology_target_only_repair(positive_two_boundary_normalized_case):
    baseline_row, witness_raw, render_png_raw, baseline_raw, mechanics, flow, baseline_normalized = positive_two_boundary_normalized_case
    value = _parse_crosscheck(leaves.INDEPENDENT_VISUAL_CROSSCHECK_TWO_BOUNDARY_V1)
    value["required_topology_inventory_content_sha256"] = "0" * 64
    mutated_raw = _seal_crosscheck(value)
    mutated_row = _reseal_admission_row_for_crosscheck(baseline_row, mutated_raw)
    _assert_pre_normalizer_contract(row=mutated_row, witness_raw=witness_raw, render_png_raw=render_png_raw, crosscheck_raw=mutated_raw, mechanics=mechanics, flow=flow, expected_predicates={
            "fixture_pre_visual_binding_is_valid": True,
            "fixture_admission_is_valid": True,
            "fixture_admission_row_matches_derive_leaves": True,
            "visual_crosscheck_leaf_matches_admission": True,
            "visual_crosscheck_root_binding_matches": True,
            "visual_crosscheck_root_context_matches": False,
            "visual_crosscheck_reviewer_matches_contract": True,
            "visual_crosscheck_cardinality_matches": True,
            "visual_crosscheck_block_region_matches": True,
            "visual_crosscheck_block_transcription_matches": True,
            "visual_crosscheck_block_decision_matches": True,
            "visual_crosscheck_boundary_region_matches": True,
            "visual_crosscheck_boundary_decision_matches": True,
            "visual_crosscheck_inventory_matches": True,
            "visual_crosscheck_content_seal_matches": True,
        })
    with pytest.raises(RawPdfError, match="^page_proof_visual_crosscheck_invalid$"):
        page_proof._normalize_fixture_visual_crosscheck(mechanics, flow, mutated_raw, mutated_row)
    value["required_topology_inventory_content_sha256"] = baseline_row.required_topology_inventory_content_sha256
    repaired_raw = _seal_crosscheck(value)
    repaired_row = _reseal_admission_row_for_crosscheck(baseline_row, repaired_raw)
    assert repaired_raw == baseline_raw
    _assert_pre_normalizer_contract(row=repaired_row, witness_raw=witness_raw, render_png_raw=render_png_raw, crosscheck_raw=repaired_raw, mechanics=mechanics, flow=flow, expected_predicates={
            "fixture_pre_visual_binding_is_valid": True,
            "fixture_admission_is_valid": True,
            "fixture_admission_row_matches_derive_leaves": True,
            "visual_crosscheck_leaf_matches_admission": True,
            "visual_crosscheck_root_binding_matches": True,
            "visual_crosscheck_root_context_matches": True,
            "visual_crosscheck_reviewer_matches_contract": True,
            "visual_crosscheck_cardinality_matches": True,
            "visual_crosscheck_block_region_matches": True,
            "visual_crosscheck_block_transcription_matches": True,
            "visual_crosscheck_block_decision_matches": True,
            "visual_crosscheck_boundary_region_matches": True,
            "visual_crosscheck_boundary_decision_matches": True,
            "visual_crosscheck_inventory_matches": True,
            "visual_crosscheck_content_seal_matches": True,
        })
    repaired_normalized = page_proof._normalize_fixture_visual_crosscheck(mechanics, flow, repaired_raw, repaired_row)
    assert _canonical_json(repaired_normalized) == _canonical_json(baseline_normalized)


def test_visual_crosscheck_root_pre_visual_core_target_only_repair(positive_two_boundary_normalized_case):
    baseline_row, witness_raw, render_png_raw, baseline_raw, mechanics, flow, baseline_normalized = positive_two_boundary_normalized_case
    value = _parse_crosscheck(leaves.INDEPENDENT_VISUAL_CROSSCHECK_TWO_BOUNDARY_V1)
    value["pre_visual_evidence_core_sha256"] = "0" * 64
    mutated_raw = _seal_crosscheck(value)
    mutated_row = _reseal_admission_row_for_crosscheck(baseline_row, mutated_raw)
    _assert_pre_normalizer_contract(row=mutated_row, witness_raw=witness_raw, render_png_raw=render_png_raw, crosscheck_raw=mutated_raw, mechanics=mechanics, flow=flow, expected_predicates={
            "fixture_pre_visual_binding_is_valid": True,
            "fixture_admission_is_valid": True,
            "fixture_admission_row_matches_derive_leaves": True,
            "visual_crosscheck_leaf_matches_admission": True,
            "visual_crosscheck_root_binding_matches": True,
            "visual_crosscheck_root_context_matches": False,
            "visual_crosscheck_reviewer_matches_contract": True,
            "visual_crosscheck_cardinality_matches": True,
            "visual_crosscheck_block_region_matches": True,
            "visual_crosscheck_block_transcription_matches": True,
            "visual_crosscheck_block_decision_matches": True,
            "visual_crosscheck_boundary_region_matches": True,
            "visual_crosscheck_boundary_decision_matches": True,
            "visual_crosscheck_inventory_matches": True,
            "visual_crosscheck_content_seal_matches": True,
        })
    with pytest.raises(RawPdfError, match="^page_proof_visual_crosscheck_invalid$"):
        page_proof._normalize_fixture_visual_crosscheck(mechanics, flow, mutated_raw, mutated_row)
    value["pre_visual_evidence_core_sha256"] = leaves.TWO_BOUNDARY_EXPECTED_PRE_VISUAL_CORE_SHA256
    repaired_raw = _seal_crosscheck(value)
    repaired_row = _reseal_admission_row_for_crosscheck(baseline_row, repaired_raw)
    assert repaired_raw == baseline_raw
    _assert_pre_normalizer_contract(row=repaired_row, witness_raw=witness_raw, render_png_raw=render_png_raw, crosscheck_raw=repaired_raw, mechanics=mechanics, flow=flow, expected_predicates={
            "fixture_pre_visual_binding_is_valid": True,
            "fixture_admission_is_valid": True,
            "fixture_admission_row_matches_derive_leaves": True,
            "visual_crosscheck_leaf_matches_admission": True,
            "visual_crosscheck_root_binding_matches": True,
            "visual_crosscheck_root_context_matches": True,
            "visual_crosscheck_reviewer_matches_contract": True,
            "visual_crosscheck_cardinality_matches": True,
            "visual_crosscheck_block_region_matches": True,
            "visual_crosscheck_block_transcription_matches": True,
            "visual_crosscheck_block_decision_matches": True,
            "visual_crosscheck_boundary_region_matches": True,
            "visual_crosscheck_boundary_decision_matches": True,
            "visual_crosscheck_inventory_matches": True,
            "visual_crosscheck_content_seal_matches": True,
        })
    repaired_normalized = page_proof._normalize_fixture_visual_crosscheck(mechanics, flow, repaired_raw, repaired_row)
    assert _canonical_json(repaired_normalized) == _canonical_json(baseline_normalized)


def test_visual_crosscheck_reviewer_identity_target_only_repair(positive_two_boundary_normalized_case):
    baseline_row, witness_raw, render_png_raw, baseline_raw, mechanics, flow, baseline_normalized = positive_two_boundary_normalized_case
    value = _parse_crosscheck(leaves.INDEPENDENT_VISUAL_CROSSCHECK_TWO_BOUNDARY_V1)
    value["reviewer_identity"] = ""
    mutated_raw = _seal_crosscheck(value)
    mutated_row = _reseal_admission_row_for_crosscheck(baseline_row, mutated_raw)
    _assert_pre_normalizer_contract(row=mutated_row, witness_raw=witness_raw, render_png_raw=render_png_raw, crosscheck_raw=mutated_raw, mechanics=mechanics, flow=flow, expected_predicates={
            "fixture_pre_visual_binding_is_valid": True,
            "fixture_admission_is_valid": True,
            "fixture_admission_row_matches_derive_leaves": True,
            "visual_crosscheck_leaf_matches_admission": True,
            "visual_crosscheck_root_binding_matches": True,
            "visual_crosscheck_root_context_matches": True,
            "visual_crosscheck_reviewer_matches_contract": False,
            "visual_crosscheck_cardinality_matches": True,
            "visual_crosscheck_block_region_matches": True,
            "visual_crosscheck_block_transcription_matches": True,
            "visual_crosscheck_block_decision_matches": True,
            "visual_crosscheck_boundary_region_matches": True,
            "visual_crosscheck_boundary_decision_matches": True,
            "visual_crosscheck_inventory_matches": True,
            "visual_crosscheck_content_seal_matches": True,
        })
    with pytest.raises(RawPdfError, match="^page_proof_visual_crosscheck_invalid$"):
        page_proof._normalize_fixture_visual_crosscheck(mechanics, flow, mutated_raw, mutated_row)
    value["reviewer_identity"] = "fixture-reviewer-v1"
    repaired_raw = _seal_crosscheck(value)
    repaired_row = _reseal_admission_row_for_crosscheck(baseline_row, repaired_raw)
    assert repaired_raw == baseline_raw
    _assert_pre_normalizer_contract(row=repaired_row, witness_raw=witness_raw, render_png_raw=render_png_raw, crosscheck_raw=repaired_raw, mechanics=mechanics, flow=flow, expected_predicates={
            "fixture_pre_visual_binding_is_valid": True,
            "fixture_admission_is_valid": True,
            "fixture_admission_row_matches_derive_leaves": True,
            "visual_crosscheck_leaf_matches_admission": True,
            "visual_crosscheck_root_binding_matches": True,
            "visual_crosscheck_root_context_matches": True,
            "visual_crosscheck_reviewer_matches_contract": True,
            "visual_crosscheck_cardinality_matches": True,
            "visual_crosscheck_block_region_matches": True,
            "visual_crosscheck_block_transcription_matches": True,
            "visual_crosscheck_block_decision_matches": True,
            "visual_crosscheck_boundary_region_matches": True,
            "visual_crosscheck_boundary_decision_matches": True,
            "visual_crosscheck_inventory_matches": True,
            "visual_crosscheck_content_seal_matches": True,
        })
    repaired_normalized = page_proof._normalize_fixture_visual_crosscheck(mechanics, flow, repaired_raw, repaired_row)
    assert _canonical_json(repaired_normalized) == _canonical_json(baseline_normalized)


def test_visual_crosscheck_reviewer_scope_target_only_repair(positive_two_boundary_normalized_case):
    baseline_row, witness_raw, render_png_raw, baseline_raw, mechanics, flow, baseline_normalized = positive_two_boundary_normalized_case
    value = _parse_crosscheck(leaves.INDEPENDENT_VISUAL_CROSSCHECK_TWO_BOUNDARY_V1)
    value["reviewer_scope"] = "page_only"
    mutated_raw = _seal_crosscheck(value)
    mutated_row = _reseal_admission_row_for_crosscheck(baseline_row, mutated_raw)
    _assert_pre_normalizer_contract(row=mutated_row, witness_raw=witness_raw, render_png_raw=render_png_raw, crosscheck_raw=mutated_raw, mechanics=mechanics, flow=flow, expected_predicates={
            "fixture_pre_visual_binding_is_valid": True,
            "fixture_admission_is_valid": True,
            "fixture_admission_row_matches_derive_leaves": True,
            "visual_crosscheck_leaf_matches_admission": True,
            "visual_crosscheck_root_binding_matches": True,
            "visual_crosscheck_root_context_matches": True,
            "visual_crosscheck_reviewer_matches_contract": False,
            "visual_crosscheck_cardinality_matches": True,
            "visual_crosscheck_block_region_matches": True,
            "visual_crosscheck_block_transcription_matches": True,
            "visual_crosscheck_block_decision_matches": True,
            "visual_crosscheck_boundary_region_matches": True,
            "visual_crosscheck_boundary_decision_matches": True,
            "visual_crosscheck_inventory_matches": True,
            "visual_crosscheck_content_seal_matches": True,
        })
    with pytest.raises(RawPdfError, match="^page_proof_visual_crosscheck_invalid$"):
        page_proof._normalize_fixture_visual_crosscheck(mechanics, flow, mutated_raw, mutated_row)
    value["reviewer_scope"] = "page_block_and_boundary"
    repaired_raw = _seal_crosscheck(value)
    repaired_row = _reseal_admission_row_for_crosscheck(baseline_row, repaired_raw)
    assert repaired_raw == baseline_raw
    _assert_pre_normalizer_contract(row=repaired_row, witness_raw=witness_raw, render_png_raw=render_png_raw, crosscheck_raw=repaired_raw, mechanics=mechanics, flow=flow, expected_predicates={
            "fixture_pre_visual_binding_is_valid": True,
            "fixture_admission_is_valid": True,
            "fixture_admission_row_matches_derive_leaves": True,
            "visual_crosscheck_leaf_matches_admission": True,
            "visual_crosscheck_root_binding_matches": True,
            "visual_crosscheck_root_context_matches": True,
            "visual_crosscheck_reviewer_matches_contract": True,
            "visual_crosscheck_cardinality_matches": True,
            "visual_crosscheck_block_region_matches": True,
            "visual_crosscheck_block_transcription_matches": True,
            "visual_crosscheck_block_decision_matches": True,
            "visual_crosscheck_boundary_region_matches": True,
            "visual_crosscheck_boundary_decision_matches": True,
            "visual_crosscheck_inventory_matches": True,
            "visual_crosscheck_content_seal_matches": True,
        })
    repaired_normalized = page_proof._normalize_fixture_visual_crosscheck(mechanics, flow, repaired_raw, repaired_row)
    assert _canonical_json(repaired_normalized) == _canonical_json(baseline_normalized)


def test_visual_crosscheck_reviewer_independence_target_only_repair(positive_two_boundary_normalized_case):
    baseline_row, witness_raw, render_png_raw, baseline_raw, mechanics, flow, baseline_normalized = positive_two_boundary_normalized_case
    value = _parse_crosscheck(leaves.INDEPENDENT_VISUAL_CROSSCHECK_TWO_BOUNDARY_V1)
    value["reviewer_independence"] = "dependent"
    mutated_raw = _seal_crosscheck(value)
    mutated_row = _reseal_admission_row_for_crosscheck(baseline_row, mutated_raw)
    _assert_pre_normalizer_contract(row=mutated_row, witness_raw=witness_raw, render_png_raw=render_png_raw, crosscheck_raw=mutated_raw, mechanics=mechanics, flow=flow, expected_predicates={
            "fixture_pre_visual_binding_is_valid": True,
            "fixture_admission_is_valid": True,
            "fixture_admission_row_matches_derive_leaves": True,
            "visual_crosscheck_leaf_matches_admission": True,
            "visual_crosscheck_root_binding_matches": True,
            "visual_crosscheck_root_context_matches": True,
            "visual_crosscheck_reviewer_matches_contract": False,
            "visual_crosscheck_cardinality_matches": True,
            "visual_crosscheck_block_region_matches": True,
            "visual_crosscheck_block_transcription_matches": True,
            "visual_crosscheck_block_decision_matches": True,
            "visual_crosscheck_boundary_region_matches": True,
            "visual_crosscheck_boundary_decision_matches": True,
            "visual_crosscheck_inventory_matches": True,
            "visual_crosscheck_content_seal_matches": True,
        })
    with pytest.raises(RawPdfError, match="^page_proof_visual_crosscheck_invalid$"):
        page_proof._normalize_fixture_visual_crosscheck(mechanics, flow, mutated_raw, mutated_row)
    value["reviewer_independence"] = "independent"
    repaired_raw = _seal_crosscheck(value)
    repaired_row = _reseal_admission_row_for_crosscheck(baseline_row, repaired_raw)
    assert repaired_raw == baseline_raw
    _assert_pre_normalizer_contract(row=repaired_row, witness_raw=witness_raw, render_png_raw=render_png_raw, crosscheck_raw=repaired_raw, mechanics=mechanics, flow=flow, expected_predicates={
            "fixture_pre_visual_binding_is_valid": True,
            "fixture_admission_is_valid": True,
            "fixture_admission_row_matches_derive_leaves": True,
            "visual_crosscheck_leaf_matches_admission": True,
            "visual_crosscheck_root_binding_matches": True,
            "visual_crosscheck_root_context_matches": True,
            "visual_crosscheck_reviewer_matches_contract": True,
            "visual_crosscheck_cardinality_matches": True,
            "visual_crosscheck_block_region_matches": True,
            "visual_crosscheck_block_transcription_matches": True,
            "visual_crosscheck_block_decision_matches": True,
            "visual_crosscheck_boundary_region_matches": True,
            "visual_crosscheck_boundary_decision_matches": True,
            "visual_crosscheck_inventory_matches": True,
            "visual_crosscheck_content_seal_matches": True,
        })
    repaired_normalized = page_proof._normalize_fixture_visual_crosscheck(mechanics, flow, repaired_raw, repaired_row)
    assert _canonical_json(repaired_normalized) == _canonical_json(baseline_normalized)


def test_visual_crosscheck_root_content_seal_target_only_repair(positive_two_boundary_normalized_case):
    baseline_row, witness_raw, render_png_raw, baseline_raw, mechanics, flow, baseline_normalized = positive_two_boundary_normalized_case
    value = _parse_crosscheck(leaves.INDEPENDENT_VISUAL_CROSSCHECK_TWO_BOUNDARY_V1)
    original_content_sha256 = value["content_sha256"]
    value["content_sha256"] = "0" * 64
    mutated_raw = _canonical_json(value)
    mutated_row = _reseal_admission_row_for_crosscheck(baseline_row, mutated_raw)
    _assert_pre_normalizer_contract(row=mutated_row, witness_raw=witness_raw, render_png_raw=render_png_raw, crosscheck_raw=mutated_raw, mechanics=mechanics, flow=flow, expected_predicates={
            "fixture_pre_visual_binding_is_valid": True,
            "fixture_admission_is_valid": True,
            "fixture_admission_row_matches_derive_leaves": True,
            "visual_crosscheck_leaf_matches_admission": True,
            "visual_crosscheck_root_binding_matches": True,
            "visual_crosscheck_root_context_matches": True,
            "visual_crosscheck_reviewer_matches_contract": True,
            "visual_crosscheck_cardinality_matches": True,
            "visual_crosscheck_block_region_matches": True,
            "visual_crosscheck_block_transcription_matches": True,
            "visual_crosscheck_block_decision_matches": True,
            "visual_crosscheck_boundary_region_matches": True,
            "visual_crosscheck_boundary_decision_matches": True,
            "visual_crosscheck_inventory_matches": True,
            "visual_crosscheck_content_seal_matches": False,
        })
    with pytest.raises(RawPdfError, match="^page_proof_visual_crosscheck_invalid$"):
        page_proof._normalize_fixture_visual_crosscheck(mechanics, flow, mutated_raw, mutated_row)
    value["content_sha256"] = original_content_sha256
    repaired_raw = _canonical_json(value)
    repaired_row = _reseal_admission_row_for_crosscheck(baseline_row, repaired_raw)
    assert repaired_raw == baseline_raw
    _assert_pre_normalizer_contract(row=repaired_row, witness_raw=witness_raw, render_png_raw=render_png_raw, crosscheck_raw=repaired_raw, mechanics=mechanics, flow=flow, expected_predicates={
            "fixture_pre_visual_binding_is_valid": True,
            "fixture_admission_is_valid": True,
            "fixture_admission_row_matches_derive_leaves": True,
            "visual_crosscheck_leaf_matches_admission": True,
            "visual_crosscheck_root_binding_matches": True,
            "visual_crosscheck_root_context_matches": True,
            "visual_crosscheck_reviewer_matches_contract": True,
            "visual_crosscheck_cardinality_matches": True,
            "visual_crosscheck_block_region_matches": True,
            "visual_crosscheck_block_transcription_matches": True,
            "visual_crosscheck_block_decision_matches": True,
            "visual_crosscheck_boundary_region_matches": True,
            "visual_crosscheck_boundary_decision_matches": True,
            "visual_crosscheck_inventory_matches": True,
            "visual_crosscheck_content_seal_matches": True,
        })
    repaired_normalized = page_proof._normalize_fixture_visual_crosscheck(mechanics, flow, repaired_raw, repaired_row)
    assert _canonical_json(repaired_normalized) == _canonical_json(baseline_normalized)


def test_visual_crosscheck_boundary_missing_final_row_target_only_repair(positive_two_boundary_normalized_case):
    baseline_row, witness_raw, render_png_raw, baseline_raw, mechanics, flow, baseline_normalized = positive_two_boundary_normalized_case
    value = _parse_crosscheck(leaves.INDEPENDENT_VISUAL_CROSSCHECK_TWO_BOUNDARY_V1)
    literal_final_row = _parse_crosscheck(leaves.INDEPENDENT_VISUAL_CROSSCHECK_TWO_BOUNDARY_V1)["boundary_checks"][1]
    value["boundary_checks"].pop(1)
    mutated_raw = _seal_crosscheck(value)
    mutated_row = _reseal_admission_row_for_crosscheck(baseline_row, mutated_raw)
    _assert_pre_normalizer_contract(row=mutated_row, witness_raw=witness_raw, render_png_raw=render_png_raw, crosscheck_raw=mutated_raw, mechanics=mechanics, flow=flow, expected_predicates={
            "fixture_pre_visual_binding_is_valid": True,
            "fixture_admission_is_valid": True,
            "fixture_admission_row_matches_derive_leaves": True,
            "visual_crosscheck_leaf_matches_admission": True,
            "visual_crosscheck_root_binding_matches": True,
            "visual_crosscheck_root_context_matches": True,
            "visual_crosscheck_reviewer_matches_contract": True,
            "visual_crosscheck_cardinality_matches": False,
            "visual_crosscheck_block_region_matches": True,
            "visual_crosscheck_block_transcription_matches": True,
            "visual_crosscheck_block_decision_matches": True,
            "visual_crosscheck_boundary_region_matches": True,
            "visual_crosscheck_boundary_decision_matches": True,
            "visual_crosscheck_inventory_matches": True,
            "visual_crosscheck_content_seal_matches": True,
        })
    with pytest.raises(RawPdfError, match="^page_proof_visual_crosscheck_invalid$"):
        page_proof._normalize_fixture_visual_crosscheck(mechanics, flow, mutated_raw, mutated_row)
    value["boundary_checks"].insert(1, literal_final_row)
    repaired_raw = _seal_crosscheck(value)
    repaired_row = _reseal_admission_row_for_crosscheck(baseline_row, repaired_raw)
    assert repaired_raw == baseline_raw
    _assert_pre_normalizer_contract(row=repaired_row, witness_raw=witness_raw, render_png_raw=render_png_raw, crosscheck_raw=repaired_raw, mechanics=mechanics, flow=flow, expected_predicates={
            "fixture_pre_visual_binding_is_valid": True,
            "fixture_admission_is_valid": True,
            "fixture_admission_row_matches_derive_leaves": True,
            "visual_crosscheck_leaf_matches_admission": True,
            "visual_crosscheck_root_binding_matches": True,
            "visual_crosscheck_root_context_matches": True,
            "visual_crosscheck_reviewer_matches_contract": True,
            "visual_crosscheck_cardinality_matches": True,
            "visual_crosscheck_block_region_matches": True,
            "visual_crosscheck_block_transcription_matches": True,
            "visual_crosscheck_block_decision_matches": True,
            "visual_crosscheck_boundary_region_matches": True,
            "visual_crosscheck_boundary_decision_matches": True,
            "visual_crosscheck_inventory_matches": True,
            "visual_crosscheck_content_seal_matches": True,
        })
    repaired_normalized = page_proof._normalize_fixture_visual_crosscheck(mechanics, flow, repaired_raw, repaired_row)
    assert _canonical_json(repaired_normalized) == _canonical_json(baseline_normalized)


def test_visual_crosscheck_boundary_duplicate_final_row_target_only_repair(positive_two_boundary_normalized_case):
    baseline_row, witness_raw, render_png_raw, baseline_raw, mechanics, flow, baseline_normalized = positive_two_boundary_normalized_case
    value = _parse_crosscheck(leaves.INDEPENDENT_VISUAL_CROSSCHECK_TWO_BOUNDARY_V1)
    literal_final_row = _parse_crosscheck(leaves.INDEPENDENT_VISUAL_CROSSCHECK_TWO_BOUNDARY_V1)["boundary_checks"][1]
    value["boundary_checks"].append(literal_final_row)
    mutated_raw = _seal_crosscheck(value)
    mutated_row = _reseal_admission_row_for_crosscheck(baseline_row, mutated_raw)
    _assert_pre_normalizer_contract(row=mutated_row, witness_raw=witness_raw, render_png_raw=render_png_raw, crosscheck_raw=mutated_raw, mechanics=mechanics, flow=flow, expected_predicates={
            "fixture_pre_visual_binding_is_valid": True,
            "fixture_admission_is_valid": True,
            "fixture_admission_row_matches_derive_leaves": True,
            "visual_crosscheck_leaf_matches_admission": True,
            "visual_crosscheck_root_binding_matches": True,
            "visual_crosscheck_root_context_matches": True,
            "visual_crosscheck_reviewer_matches_contract": True,
            "visual_crosscheck_cardinality_matches": False,
            "visual_crosscheck_block_region_matches": True,
            "visual_crosscheck_block_transcription_matches": True,
            "visual_crosscheck_block_decision_matches": True,
            "visual_crosscheck_boundary_region_matches": True,
            "visual_crosscheck_boundary_decision_matches": True,
            "visual_crosscheck_inventory_matches": True,
            "visual_crosscheck_content_seal_matches": True,
        })
    with pytest.raises(RawPdfError, match="^page_proof_visual_crosscheck_invalid$"):
        page_proof._normalize_fixture_visual_crosscheck(mechanics, flow, mutated_raw, mutated_row)
    value["boundary_checks"].pop()
    repaired_raw = _seal_crosscheck(value)
    repaired_row = _reseal_admission_row_for_crosscheck(baseline_row, repaired_raw)
    assert repaired_raw == baseline_raw
    _assert_pre_normalizer_contract(row=repaired_row, witness_raw=witness_raw, render_png_raw=render_png_raw, crosscheck_raw=repaired_raw, mechanics=mechanics, flow=flow, expected_predicates={
            "fixture_pre_visual_binding_is_valid": True,
            "fixture_admission_is_valid": True,
            "fixture_admission_row_matches_derive_leaves": True,
            "visual_crosscheck_leaf_matches_admission": True,
            "visual_crosscheck_root_binding_matches": True,
            "visual_crosscheck_root_context_matches": True,
            "visual_crosscheck_reviewer_matches_contract": True,
            "visual_crosscheck_cardinality_matches": True,
            "visual_crosscheck_block_region_matches": True,
            "visual_crosscheck_block_transcription_matches": True,
            "visual_crosscheck_block_decision_matches": True,
            "visual_crosscheck_boundary_region_matches": True,
            "visual_crosscheck_boundary_decision_matches": True,
            "visual_crosscheck_inventory_matches": True,
            "visual_crosscheck_content_seal_matches": True,
        })
    repaired_normalized = page_proof._normalize_fixture_visual_crosscheck(mechanics, flow, repaired_raw, repaired_row)
    assert _canonical_json(repaired_normalized) == _canonical_json(baseline_normalized)


def test_visual_crosscheck_boundary_reordered_rows_target_only_repair(positive_two_boundary_normalized_case):
    baseline_row, witness_raw, render_png_raw, baseline_raw, mechanics, flow, baseline_normalized = positive_two_boundary_normalized_case
    value = _parse_crosscheck(leaves.INDEPENDENT_VISUAL_CROSSCHECK_TWO_BOUNDARY_V1)
    value["boundary_checks"][0], value["boundary_checks"][1] = value["boundary_checks"][1], value["boundary_checks"][0]
    mutated_raw = _seal_crosscheck(value)
    mutated_row = _reseal_admission_row_for_crosscheck(baseline_row, mutated_raw)
    _assert_pre_normalizer_contract(row=mutated_row, witness_raw=witness_raw, render_png_raw=render_png_raw, crosscheck_raw=mutated_raw, mechanics=mechanics, flow=flow, expected_predicates={
            "fixture_pre_visual_binding_is_valid": True,
            "fixture_admission_is_valid": True,
            "fixture_admission_row_matches_derive_leaves": True,
            "visual_crosscheck_leaf_matches_admission": True,
            "visual_crosscheck_root_binding_matches": True,
            "visual_crosscheck_root_context_matches": True,
            "visual_crosscheck_reviewer_matches_contract": True,
            "visual_crosscheck_cardinality_matches": True,
            "visual_crosscheck_block_region_matches": True,
            "visual_crosscheck_block_transcription_matches": True,
            "visual_crosscheck_block_decision_matches": True,
            "visual_crosscheck_boundary_region_matches": False,
            "visual_crosscheck_boundary_decision_matches": True,
            "visual_crosscheck_inventory_matches": True,
            "visual_crosscheck_content_seal_matches": True,
        })
    with pytest.raises(RawPdfError, match="^page_proof_visual_crosscheck_invalid$"):
        page_proof._normalize_fixture_visual_crosscheck(mechanics, flow, mutated_raw, mutated_row)
    value["boundary_checks"][0], value["boundary_checks"][1] = value["boundary_checks"][1], value["boundary_checks"][0]
    repaired_raw = _seal_crosscheck(value)
    repaired_row = _reseal_admission_row_for_crosscheck(baseline_row, repaired_raw)
    assert repaired_raw == baseline_raw
    _assert_pre_normalizer_contract(row=repaired_row, witness_raw=witness_raw, render_png_raw=render_png_raw, crosscheck_raw=repaired_raw, mechanics=mechanics, flow=flow, expected_predicates={
            "fixture_pre_visual_binding_is_valid": True,
            "fixture_admission_is_valid": True,
            "fixture_admission_row_matches_derive_leaves": True,
            "visual_crosscheck_leaf_matches_admission": True,
            "visual_crosscheck_root_binding_matches": True,
            "visual_crosscheck_root_context_matches": True,
            "visual_crosscheck_reviewer_matches_contract": True,
            "visual_crosscheck_cardinality_matches": True,
            "visual_crosscheck_block_region_matches": True,
            "visual_crosscheck_block_transcription_matches": True,
            "visual_crosscheck_block_decision_matches": True,
            "visual_crosscheck_boundary_region_matches": True,
            "visual_crosscheck_boundary_decision_matches": True,
            "visual_crosscheck_inventory_matches": True,
            "visual_crosscheck_content_seal_matches": True,
        })
    repaired_normalized = page_proof._normalize_fixture_visual_crosscheck(mechanics, flow, repaired_raw, repaired_row)
    assert _canonical_json(repaired_normalized) == _canonical_json(baseline_normalized)


def test_visual_crosscheck_boundary_aggregate_f0_f2_target_only_repair(positive_two_boundary_normalized_case):
    baseline_row, witness_raw, render_png_raw, baseline_raw, mechanics, flow, baseline_normalized = positive_two_boundary_normalized_case
    value = _parse_crosscheck(leaves.INDEPENDENT_VISUAL_CROSSCHECK_TWO_BOUNDARY_V1)
    value["boundary_checks"][0]["target_fragment_id"] = "f2"
    value["boundary_checks"][0]["boundary_kind"] = "cross_column"
    value["boundary_checks"][0]["target_block_id"] = "b1"
    value["boundary_checks"][0]["target_column_index"] = 0
    value["boundary_checks"][0]["boundary_bbox_px"] = [0, 0, 4, 3]
    value["boundary_checks"][1]["source_fragment_id"] = "f0"
    mutated_raw = _seal_crosscheck(value)
    mutated_row = _reseal_admission_row_for_crosscheck(baseline_row, mutated_raw)
    _assert_pre_normalizer_contract(row=mutated_row, witness_raw=witness_raw, render_png_raw=render_png_raw, crosscheck_raw=mutated_raw, mechanics=mechanics, flow=flow, expected_predicates={
            "fixture_pre_visual_binding_is_valid": True,
            "fixture_admission_is_valid": True,
            "fixture_admission_row_matches_derive_leaves": True,
            "visual_crosscheck_leaf_matches_admission": True,
            "visual_crosscheck_root_binding_matches": True,
            "visual_crosscheck_root_context_matches": True,
            "visual_crosscheck_reviewer_matches_contract": True,
            "visual_crosscheck_cardinality_matches": True,
            "visual_crosscheck_block_region_matches": True,
            "visual_crosscheck_block_transcription_matches": True,
            "visual_crosscheck_block_decision_matches": True,
            "visual_crosscheck_boundary_region_matches": False,
            "visual_crosscheck_boundary_decision_matches": True,
            "visual_crosscheck_inventory_matches": True,
            "visual_crosscheck_content_seal_matches": True,
        })
    with pytest.raises(RawPdfError, match="^page_proof_visual_crosscheck_invalid$"):
        page_proof._normalize_fixture_visual_crosscheck(mechanics, flow, mutated_raw, mutated_row)
    value["boundary_checks"][0]["target_fragment_id"] = "f1"
    value["boundary_checks"][0]["boundary_kind"] = "within_block"
    value["boundary_checks"][0]["target_block_id"] = "b0"
    value["boundary_checks"][0]["target_column_index"] = 1
    value["boundary_checks"][0]["boundary_bbox_px"] = [0, 0, 1, 3]
    value["boundary_checks"][1]["source_fragment_id"] = "f1"
    repaired_raw = _seal_crosscheck(value)
    repaired_row = _reseal_admission_row_for_crosscheck(baseline_row, repaired_raw)
    assert repaired_raw == baseline_raw
    _assert_pre_normalizer_contract(row=repaired_row, witness_raw=witness_raw, render_png_raw=render_png_raw, crosscheck_raw=repaired_raw, mechanics=mechanics, flow=flow, expected_predicates={
            "fixture_pre_visual_binding_is_valid": True,
            "fixture_admission_is_valid": True,
            "fixture_admission_row_matches_derive_leaves": True,
            "visual_crosscheck_leaf_matches_admission": True,
            "visual_crosscheck_root_binding_matches": True,
            "visual_crosscheck_root_context_matches": True,
            "visual_crosscheck_reviewer_matches_contract": True,
            "visual_crosscheck_cardinality_matches": True,
            "visual_crosscheck_block_region_matches": True,
            "visual_crosscheck_block_transcription_matches": True,
            "visual_crosscheck_block_decision_matches": True,
            "visual_crosscheck_boundary_region_matches": True,
            "visual_crosscheck_boundary_decision_matches": True,
            "visual_crosscheck_inventory_matches": True,
            "visual_crosscheck_content_seal_matches": True,
        })
    repaired_normalized = page_proof._normalize_fixture_visual_crosscheck(mechanics, flow, repaired_raw, repaired_row)
    assert _canonical_json(repaired_normalized) == _canonical_json(baseline_normalized)


def test_visual_crosscheck_boundary_source_fragment_target_only_repair(positive_two_boundary_normalized_case):
    baseline_row, witness_raw, render_png_raw, baseline_raw, mechanics, flow, baseline_normalized = positive_two_boundary_normalized_case
    value = _parse_crosscheck(leaves.INDEPENDENT_VISUAL_CROSSCHECK_TWO_BOUNDARY_V1)
    value["boundary_checks"][0]["source_fragment_id"] = "bad"
    mutated_raw = _seal_crosscheck(value)
    mutated_row = _reseal_admission_row_for_crosscheck(baseline_row, mutated_raw)
    _assert_pre_normalizer_contract(row=mutated_row, witness_raw=witness_raw, render_png_raw=render_png_raw, crosscheck_raw=mutated_raw, mechanics=mechanics, flow=flow, expected_predicates={
            "fixture_pre_visual_binding_is_valid": True,
            "fixture_admission_is_valid": True,
            "fixture_admission_row_matches_derive_leaves": True,
            "visual_crosscheck_leaf_matches_admission": True,
            "visual_crosscheck_root_binding_matches": True,
            "visual_crosscheck_root_context_matches": True,
            "visual_crosscheck_reviewer_matches_contract": True,
            "visual_crosscheck_cardinality_matches": True,
            "visual_crosscheck_block_region_matches": True,
            "visual_crosscheck_block_transcription_matches": True,
            "visual_crosscheck_block_decision_matches": True,
            "visual_crosscheck_boundary_region_matches": False,
            "visual_crosscheck_boundary_decision_matches": True,
            "visual_crosscheck_inventory_matches": True,
            "visual_crosscheck_content_seal_matches": True,
        })
    with pytest.raises(RawPdfError, match="^page_proof_visual_crosscheck_invalid$"):
        page_proof._normalize_fixture_visual_crosscheck(mechanics, flow, mutated_raw, mutated_row)
    value["boundary_checks"][0]["source_fragment_id"] = "f0"
    repaired_raw = _seal_crosscheck(value)
    repaired_row = _reseal_admission_row_for_crosscheck(baseline_row, repaired_raw)
    assert repaired_raw == baseline_raw
    _assert_pre_normalizer_contract(row=repaired_row, witness_raw=witness_raw, render_png_raw=render_png_raw, crosscheck_raw=repaired_raw, mechanics=mechanics, flow=flow, expected_predicates={
            "fixture_pre_visual_binding_is_valid": True,
            "fixture_admission_is_valid": True,
            "fixture_admission_row_matches_derive_leaves": True,
            "visual_crosscheck_leaf_matches_admission": True,
            "visual_crosscheck_root_binding_matches": True,
            "visual_crosscheck_root_context_matches": True,
            "visual_crosscheck_reviewer_matches_contract": True,
            "visual_crosscheck_cardinality_matches": True,
            "visual_crosscheck_block_region_matches": True,
            "visual_crosscheck_block_transcription_matches": True,
            "visual_crosscheck_block_decision_matches": True,
            "visual_crosscheck_boundary_region_matches": True,
            "visual_crosscheck_boundary_decision_matches": True,
            "visual_crosscheck_inventory_matches": True,
            "visual_crosscheck_content_seal_matches": True,
        })
    repaired_normalized = page_proof._normalize_fixture_visual_crosscheck(mechanics, flow, repaired_raw, repaired_row)
    assert _canonical_json(repaired_normalized) == _canonical_json(baseline_normalized)


def test_visual_crosscheck_boundary_target_fragment_target_only_repair(positive_two_boundary_normalized_case):
    baseline_row, witness_raw, render_png_raw, baseline_raw, mechanics, flow, baseline_normalized = positive_two_boundary_normalized_case
    value = _parse_crosscheck(leaves.INDEPENDENT_VISUAL_CROSSCHECK_TWO_BOUNDARY_V1)
    value["boundary_checks"][0]["target_fragment_id"] = "bad"
    mutated_raw = _seal_crosscheck(value)
    mutated_row = _reseal_admission_row_for_crosscheck(baseline_row, mutated_raw)
    _assert_pre_normalizer_contract(row=mutated_row, witness_raw=witness_raw, render_png_raw=render_png_raw, crosscheck_raw=mutated_raw, mechanics=mechanics, flow=flow, expected_predicates={
            "fixture_pre_visual_binding_is_valid": True,
            "fixture_admission_is_valid": True,
            "fixture_admission_row_matches_derive_leaves": True,
            "visual_crosscheck_leaf_matches_admission": True,
            "visual_crosscheck_root_binding_matches": True,
            "visual_crosscheck_root_context_matches": True,
            "visual_crosscheck_reviewer_matches_contract": True,
            "visual_crosscheck_cardinality_matches": True,
            "visual_crosscheck_block_region_matches": True,
            "visual_crosscheck_block_transcription_matches": True,
            "visual_crosscheck_block_decision_matches": True,
            "visual_crosscheck_boundary_region_matches": False,
            "visual_crosscheck_boundary_decision_matches": True,
            "visual_crosscheck_inventory_matches": True,
            "visual_crosscheck_content_seal_matches": True,
        })
    with pytest.raises(RawPdfError, match="^page_proof_visual_crosscheck_invalid$"):
        page_proof._normalize_fixture_visual_crosscheck(mechanics, flow, mutated_raw, mutated_row)
    value["boundary_checks"][0]["target_fragment_id"] = "f1"
    repaired_raw = _seal_crosscheck(value)
    repaired_row = _reseal_admission_row_for_crosscheck(baseline_row, repaired_raw)
    assert repaired_raw == baseline_raw
    _assert_pre_normalizer_contract(row=repaired_row, witness_raw=witness_raw, render_png_raw=render_png_raw, crosscheck_raw=repaired_raw, mechanics=mechanics, flow=flow, expected_predicates={
            "fixture_pre_visual_binding_is_valid": True,
            "fixture_admission_is_valid": True,
            "fixture_admission_row_matches_derive_leaves": True,
            "visual_crosscheck_leaf_matches_admission": True,
            "visual_crosscheck_root_binding_matches": True,
            "visual_crosscheck_root_context_matches": True,
            "visual_crosscheck_reviewer_matches_contract": True,
            "visual_crosscheck_cardinality_matches": True,
            "visual_crosscheck_block_region_matches": True,
            "visual_crosscheck_block_transcription_matches": True,
            "visual_crosscheck_block_decision_matches": True,
            "visual_crosscheck_boundary_region_matches": True,
            "visual_crosscheck_boundary_decision_matches": True,
            "visual_crosscheck_inventory_matches": True,
            "visual_crosscheck_content_seal_matches": True,
        })
    repaired_normalized = page_proof._normalize_fixture_visual_crosscheck(mechanics, flow, repaired_raw, repaired_row)
    assert _canonical_json(repaired_normalized) == _canonical_json(baseline_normalized)


def test_visual_crosscheck_boundary_kind_target_only_repair(positive_two_boundary_normalized_case):
    baseline_row, witness_raw, render_png_raw, baseline_raw, mechanics, flow, baseline_normalized = positive_two_boundary_normalized_case
    value = _parse_crosscheck(leaves.INDEPENDENT_VISUAL_CROSSCHECK_TWO_BOUNDARY_V1)
    value["boundary_checks"][0]["boundary_kind"] = "cross_column"
    mutated_raw = _seal_crosscheck(value)
    mutated_row = _reseal_admission_row_for_crosscheck(baseline_row, mutated_raw)
    _assert_pre_normalizer_contract(row=mutated_row, witness_raw=witness_raw, render_png_raw=render_png_raw, crosscheck_raw=mutated_raw, mechanics=mechanics, flow=flow, expected_predicates={
            "fixture_pre_visual_binding_is_valid": True,
            "fixture_admission_is_valid": True,
            "fixture_admission_row_matches_derive_leaves": True,
            "visual_crosscheck_leaf_matches_admission": True,
            "visual_crosscheck_root_binding_matches": True,
            "visual_crosscheck_root_context_matches": True,
            "visual_crosscheck_reviewer_matches_contract": True,
            "visual_crosscheck_cardinality_matches": True,
            "visual_crosscheck_block_region_matches": True,
            "visual_crosscheck_block_transcription_matches": True,
            "visual_crosscheck_block_decision_matches": True,
            "visual_crosscheck_boundary_region_matches": False,
            "visual_crosscheck_boundary_decision_matches": True,
            "visual_crosscheck_inventory_matches": True,
            "visual_crosscheck_content_seal_matches": True,
        })
    with pytest.raises(RawPdfError, match="^page_proof_visual_crosscheck_invalid$"):
        page_proof._normalize_fixture_visual_crosscheck(mechanics, flow, mutated_raw, mutated_row)
    value["boundary_checks"][0]["boundary_kind"] = "within_block"
    repaired_raw = _seal_crosscheck(value)
    repaired_row = _reseal_admission_row_for_crosscheck(baseline_row, repaired_raw)
    assert repaired_raw == baseline_raw
    _assert_pre_normalizer_contract(row=repaired_row, witness_raw=witness_raw, render_png_raw=render_png_raw, crosscheck_raw=repaired_raw, mechanics=mechanics, flow=flow, expected_predicates={
            "fixture_pre_visual_binding_is_valid": True,
            "fixture_admission_is_valid": True,
            "fixture_admission_row_matches_derive_leaves": True,
            "visual_crosscheck_leaf_matches_admission": True,
            "visual_crosscheck_root_binding_matches": True,
            "visual_crosscheck_root_context_matches": True,
            "visual_crosscheck_reviewer_matches_contract": True,
            "visual_crosscheck_cardinality_matches": True,
            "visual_crosscheck_block_region_matches": True,
            "visual_crosscheck_block_transcription_matches": True,
            "visual_crosscheck_block_decision_matches": True,
            "visual_crosscheck_boundary_region_matches": True,
            "visual_crosscheck_boundary_decision_matches": True,
            "visual_crosscheck_inventory_matches": True,
            "visual_crosscheck_content_seal_matches": True,
        })
    repaired_normalized = page_proof._normalize_fixture_visual_crosscheck(mechanics, flow, repaired_raw, repaired_row)
    assert _canonical_json(repaired_normalized) == _canonical_json(baseline_normalized)


def test_visual_crosscheck_boundary_source_block_target_only_repair(positive_two_boundary_normalized_case):
    baseline_row, witness_raw, render_png_raw, baseline_raw, mechanics, flow, baseline_normalized = positive_two_boundary_normalized_case
    value = _parse_crosscheck(leaves.INDEPENDENT_VISUAL_CROSSCHECK_TWO_BOUNDARY_V1)
    value["boundary_checks"][0]["source_block_id"] = "b1"
    mutated_raw = _seal_crosscheck(value)
    mutated_row = _reseal_admission_row_for_crosscheck(baseline_row, mutated_raw)
    _assert_pre_normalizer_contract(row=mutated_row, witness_raw=witness_raw, render_png_raw=render_png_raw, crosscheck_raw=mutated_raw, mechanics=mechanics, flow=flow, expected_predicates={
            "fixture_pre_visual_binding_is_valid": True,
            "fixture_admission_is_valid": True,
            "fixture_admission_row_matches_derive_leaves": True,
            "visual_crosscheck_leaf_matches_admission": True,
            "visual_crosscheck_root_binding_matches": True,
            "visual_crosscheck_root_context_matches": True,
            "visual_crosscheck_reviewer_matches_contract": True,
            "visual_crosscheck_cardinality_matches": True,
            "visual_crosscheck_block_region_matches": True,
            "visual_crosscheck_block_transcription_matches": True,
            "visual_crosscheck_block_decision_matches": True,
            "visual_crosscheck_boundary_region_matches": False,
            "visual_crosscheck_boundary_decision_matches": True,
            "visual_crosscheck_inventory_matches": True,
            "visual_crosscheck_content_seal_matches": True,
        })
    with pytest.raises(RawPdfError, match="^page_proof_visual_crosscheck_invalid$"):
        page_proof._normalize_fixture_visual_crosscheck(mechanics, flow, mutated_raw, mutated_row)
    value["boundary_checks"][0]["source_block_id"] = "b0"
    repaired_raw = _seal_crosscheck(value)
    repaired_row = _reseal_admission_row_for_crosscheck(baseline_row, repaired_raw)
    assert repaired_raw == baseline_raw
    _assert_pre_normalizer_contract(row=repaired_row, witness_raw=witness_raw, render_png_raw=render_png_raw, crosscheck_raw=repaired_raw, mechanics=mechanics, flow=flow, expected_predicates={
            "fixture_pre_visual_binding_is_valid": True,
            "fixture_admission_is_valid": True,
            "fixture_admission_row_matches_derive_leaves": True,
            "visual_crosscheck_leaf_matches_admission": True,
            "visual_crosscheck_root_binding_matches": True,
            "visual_crosscheck_root_context_matches": True,
            "visual_crosscheck_reviewer_matches_contract": True,
            "visual_crosscheck_cardinality_matches": True,
            "visual_crosscheck_block_region_matches": True,
            "visual_crosscheck_block_transcription_matches": True,
            "visual_crosscheck_block_decision_matches": True,
            "visual_crosscheck_boundary_region_matches": True,
            "visual_crosscheck_boundary_decision_matches": True,
            "visual_crosscheck_inventory_matches": True,
            "visual_crosscheck_content_seal_matches": True,
        })
    repaired_normalized = page_proof._normalize_fixture_visual_crosscheck(mechanics, flow, repaired_raw, repaired_row)
    assert _canonical_json(repaired_normalized) == _canonical_json(baseline_normalized)


def test_visual_crosscheck_boundary_target_block_target_only_repair(positive_two_boundary_normalized_case):
    baseline_row, witness_raw, render_png_raw, baseline_raw, mechanics, flow, baseline_normalized = positive_two_boundary_normalized_case
    value = _parse_crosscheck(leaves.INDEPENDENT_VISUAL_CROSSCHECK_TWO_BOUNDARY_V1)
    value["boundary_checks"][0]["target_block_id"] = "b1"
    mutated_raw = _seal_crosscheck(value)
    mutated_row = _reseal_admission_row_for_crosscheck(baseline_row, mutated_raw)
    _assert_pre_normalizer_contract(row=mutated_row, witness_raw=witness_raw, render_png_raw=render_png_raw, crosscheck_raw=mutated_raw, mechanics=mechanics, flow=flow, expected_predicates={
            "fixture_pre_visual_binding_is_valid": True,
            "fixture_admission_is_valid": True,
            "fixture_admission_row_matches_derive_leaves": True,
            "visual_crosscheck_leaf_matches_admission": True,
            "visual_crosscheck_root_binding_matches": True,
            "visual_crosscheck_root_context_matches": True,
            "visual_crosscheck_reviewer_matches_contract": True,
            "visual_crosscheck_cardinality_matches": True,
            "visual_crosscheck_block_region_matches": True,
            "visual_crosscheck_block_transcription_matches": True,
            "visual_crosscheck_block_decision_matches": True,
            "visual_crosscheck_boundary_region_matches": False,
            "visual_crosscheck_boundary_decision_matches": True,
            "visual_crosscheck_inventory_matches": True,
            "visual_crosscheck_content_seal_matches": True,
        })
    with pytest.raises(RawPdfError, match="^page_proof_visual_crosscheck_invalid$"):
        page_proof._normalize_fixture_visual_crosscheck(mechanics, flow, mutated_raw, mutated_row)
    value["boundary_checks"][0]["target_block_id"] = "b0"
    repaired_raw = _seal_crosscheck(value)
    repaired_row = _reseal_admission_row_for_crosscheck(baseline_row, repaired_raw)
    assert repaired_raw == baseline_raw
    _assert_pre_normalizer_contract(row=repaired_row, witness_raw=witness_raw, render_png_raw=render_png_raw, crosscheck_raw=repaired_raw, mechanics=mechanics, flow=flow, expected_predicates={
            "fixture_pre_visual_binding_is_valid": True,
            "fixture_admission_is_valid": True,
            "fixture_admission_row_matches_derive_leaves": True,
            "visual_crosscheck_leaf_matches_admission": True,
            "visual_crosscheck_root_binding_matches": True,
            "visual_crosscheck_root_context_matches": True,
            "visual_crosscheck_reviewer_matches_contract": True,
            "visual_crosscheck_cardinality_matches": True,
            "visual_crosscheck_block_region_matches": True,
            "visual_crosscheck_block_transcription_matches": True,
            "visual_crosscheck_block_decision_matches": True,
            "visual_crosscheck_boundary_region_matches": True,
            "visual_crosscheck_boundary_decision_matches": True,
            "visual_crosscheck_inventory_matches": True,
            "visual_crosscheck_content_seal_matches": True,
        })
    repaired_normalized = page_proof._normalize_fixture_visual_crosscheck(mechanics, flow, repaired_raw, repaired_row)
    assert _canonical_json(repaired_normalized) == _canonical_json(baseline_normalized)


def test_visual_crosscheck_boundary_source_column_target_only_repair(positive_two_boundary_normalized_case):
    baseline_row, witness_raw, render_png_raw, baseline_raw, mechanics, flow, baseline_normalized = positive_two_boundary_normalized_case
    value = _parse_crosscheck(leaves.INDEPENDENT_VISUAL_CROSSCHECK_TWO_BOUNDARY_V1)
    value["boundary_checks"][0]["source_column_index"] = 0
    mutated_raw = _seal_crosscheck(value)
    mutated_row = _reseal_admission_row_for_crosscheck(baseline_row, mutated_raw)
    _assert_pre_normalizer_contract(row=mutated_row, witness_raw=witness_raw, render_png_raw=render_png_raw, crosscheck_raw=mutated_raw, mechanics=mechanics, flow=flow, expected_predicates={
            "fixture_pre_visual_binding_is_valid": True,
            "fixture_admission_is_valid": True,
            "fixture_admission_row_matches_derive_leaves": True,
            "visual_crosscheck_leaf_matches_admission": True,
            "visual_crosscheck_root_binding_matches": True,
            "visual_crosscheck_root_context_matches": True,
            "visual_crosscheck_reviewer_matches_contract": True,
            "visual_crosscheck_cardinality_matches": True,
            "visual_crosscheck_block_region_matches": True,
            "visual_crosscheck_block_transcription_matches": True,
            "visual_crosscheck_block_decision_matches": True,
            "visual_crosscheck_boundary_region_matches": False,
            "visual_crosscheck_boundary_decision_matches": True,
            "visual_crosscheck_inventory_matches": True,
            "visual_crosscheck_content_seal_matches": True,
        })
    with pytest.raises(RawPdfError, match="^page_proof_visual_crosscheck_invalid$"):
        page_proof._normalize_fixture_visual_crosscheck(mechanics, flow, mutated_raw, mutated_row)
    value["boundary_checks"][0]["source_column_index"] = 1
    repaired_raw = _seal_crosscheck(value)
    repaired_row = _reseal_admission_row_for_crosscheck(baseline_row, repaired_raw)
    assert repaired_raw == baseline_raw
    _assert_pre_normalizer_contract(row=repaired_row, witness_raw=witness_raw, render_png_raw=render_png_raw, crosscheck_raw=repaired_raw, mechanics=mechanics, flow=flow, expected_predicates={
            "fixture_pre_visual_binding_is_valid": True,
            "fixture_admission_is_valid": True,
            "fixture_admission_row_matches_derive_leaves": True,
            "visual_crosscheck_leaf_matches_admission": True,
            "visual_crosscheck_root_binding_matches": True,
            "visual_crosscheck_root_context_matches": True,
            "visual_crosscheck_reviewer_matches_contract": True,
            "visual_crosscheck_cardinality_matches": True,
            "visual_crosscheck_block_region_matches": True,
            "visual_crosscheck_block_transcription_matches": True,
            "visual_crosscheck_block_decision_matches": True,
            "visual_crosscheck_boundary_region_matches": True,
            "visual_crosscheck_boundary_decision_matches": True,
            "visual_crosscheck_inventory_matches": True,
            "visual_crosscheck_content_seal_matches": True,
        })
    repaired_normalized = page_proof._normalize_fixture_visual_crosscheck(mechanics, flow, repaired_raw, repaired_row)
    assert _canonical_json(repaired_normalized) == _canonical_json(baseline_normalized)


def test_visual_crosscheck_boundary_target_column_target_only_repair(positive_two_boundary_normalized_case):
    baseline_row, witness_raw, render_png_raw, baseline_raw, mechanics, flow, baseline_normalized = positive_two_boundary_normalized_case
    value = _parse_crosscheck(leaves.INDEPENDENT_VISUAL_CROSSCHECK_TWO_BOUNDARY_V1)
    value["boundary_checks"][0]["target_column_index"] = 0
    mutated_raw = _seal_crosscheck(value)
    mutated_row = _reseal_admission_row_for_crosscheck(baseline_row, mutated_raw)
    _assert_pre_normalizer_contract(row=mutated_row, witness_raw=witness_raw, render_png_raw=render_png_raw, crosscheck_raw=mutated_raw, mechanics=mechanics, flow=flow, expected_predicates={
            "fixture_pre_visual_binding_is_valid": True,
            "fixture_admission_is_valid": True,
            "fixture_admission_row_matches_derive_leaves": True,
            "visual_crosscheck_leaf_matches_admission": True,
            "visual_crosscheck_root_binding_matches": True,
            "visual_crosscheck_root_context_matches": True,
            "visual_crosscheck_reviewer_matches_contract": True,
            "visual_crosscheck_cardinality_matches": True,
            "visual_crosscheck_block_region_matches": True,
            "visual_crosscheck_block_transcription_matches": True,
            "visual_crosscheck_block_decision_matches": True,
            "visual_crosscheck_boundary_region_matches": False,
            "visual_crosscheck_boundary_decision_matches": True,
            "visual_crosscheck_inventory_matches": True,
            "visual_crosscheck_content_seal_matches": True,
        })
    with pytest.raises(RawPdfError, match="^page_proof_visual_crosscheck_invalid$"):
        page_proof._normalize_fixture_visual_crosscheck(mechanics, flow, mutated_raw, mutated_row)
    value["boundary_checks"][0]["target_column_index"] = 1
    repaired_raw = _seal_crosscheck(value)
    repaired_row = _reseal_admission_row_for_crosscheck(baseline_row, repaired_raw)
    assert repaired_raw == baseline_raw
    _assert_pre_normalizer_contract(row=repaired_row, witness_raw=witness_raw, render_png_raw=render_png_raw, crosscheck_raw=repaired_raw, mechanics=mechanics, flow=flow, expected_predicates={
            "fixture_pre_visual_binding_is_valid": True,
            "fixture_admission_is_valid": True,
            "fixture_admission_row_matches_derive_leaves": True,
            "visual_crosscheck_leaf_matches_admission": True,
            "visual_crosscheck_root_binding_matches": True,
            "visual_crosscheck_root_context_matches": True,
            "visual_crosscheck_reviewer_matches_contract": True,
            "visual_crosscheck_cardinality_matches": True,
            "visual_crosscheck_block_region_matches": True,
            "visual_crosscheck_block_transcription_matches": True,
            "visual_crosscheck_block_decision_matches": True,
            "visual_crosscheck_boundary_region_matches": True,
            "visual_crosscheck_boundary_decision_matches": True,
            "visual_crosscheck_inventory_matches": True,
            "visual_crosscheck_content_seal_matches": True,
        })
    repaired_normalized = page_proof._normalize_fixture_visual_crosscheck(mechanics, flow, repaired_raw, repaired_row)
    assert _canonical_json(repaired_normalized) == _canonical_json(baseline_normalized)


def test_visual_crosscheck_boundary_bbox_target_only_repair(positive_two_boundary_normalized_case):
    baseline_row, witness_raw, render_png_raw, baseline_raw, mechanics, flow, baseline_normalized = positive_two_boundary_normalized_case
    value = _parse_crosscheck(leaves.INDEPENDENT_VISUAL_CROSSCHECK_TWO_BOUNDARY_V1)
    value["boundary_checks"][0]["boundary_bbox_px"] = [0, 0, 4, 3]
    mutated_raw = _seal_crosscheck(value)
    mutated_row = _reseal_admission_row_for_crosscheck(baseline_row, mutated_raw)
    _assert_pre_normalizer_contract(row=mutated_row, witness_raw=witness_raw, render_png_raw=render_png_raw, crosscheck_raw=mutated_raw, mechanics=mechanics, flow=flow, expected_predicates={
            "fixture_pre_visual_binding_is_valid": True,
            "fixture_admission_is_valid": True,
            "fixture_admission_row_matches_derive_leaves": True,
            "visual_crosscheck_leaf_matches_admission": True,
            "visual_crosscheck_root_binding_matches": True,
            "visual_crosscheck_root_context_matches": True,
            "visual_crosscheck_reviewer_matches_contract": True,
            "visual_crosscheck_cardinality_matches": True,
            "visual_crosscheck_block_region_matches": True,
            "visual_crosscheck_block_transcription_matches": True,
            "visual_crosscheck_block_decision_matches": True,
            "visual_crosscheck_boundary_region_matches": False,
            "visual_crosscheck_boundary_decision_matches": True,
            "visual_crosscheck_inventory_matches": True,
            "visual_crosscheck_content_seal_matches": True,
        })
    with pytest.raises(RawPdfError, match="^page_proof_visual_crosscheck_invalid$"):
        page_proof._normalize_fixture_visual_crosscheck(mechanics, flow, mutated_raw, mutated_row)
    value["boundary_checks"][0]["boundary_bbox_px"] = [0, 0, 1, 3]
    repaired_raw = _seal_crosscheck(value)
    repaired_row = _reseal_admission_row_for_crosscheck(baseline_row, repaired_raw)
    assert repaired_raw == baseline_raw
    _assert_pre_normalizer_contract(row=repaired_row, witness_raw=witness_raw, render_png_raw=render_png_raw, crosscheck_raw=repaired_raw, mechanics=mechanics, flow=flow, expected_predicates={
            "fixture_pre_visual_binding_is_valid": True,
            "fixture_admission_is_valid": True,
            "fixture_admission_row_matches_derive_leaves": True,
            "visual_crosscheck_leaf_matches_admission": True,
            "visual_crosscheck_root_binding_matches": True,
            "visual_crosscheck_root_context_matches": True,
            "visual_crosscheck_reviewer_matches_contract": True,
            "visual_crosscheck_cardinality_matches": True,
            "visual_crosscheck_block_region_matches": True,
            "visual_crosscheck_block_transcription_matches": True,
            "visual_crosscheck_block_decision_matches": True,
            "visual_crosscheck_boundary_region_matches": True,
            "visual_crosscheck_boundary_decision_matches": True,
            "visual_crosscheck_inventory_matches": True,
            "visual_crosscheck_content_seal_matches": True,
        })
    repaired_normalized = page_proof._normalize_fixture_visual_crosscheck(mechanics, flow, repaired_raw, repaired_row)
    assert _canonical_json(repaired_normalized) == _canonical_json(baseline_normalized)


def test_visual_crosscheck_boundary_nonconfirm_target_only_repair(positive_two_boundary_normalized_case):
    baseline_row, witness_raw, render_png_raw, baseline_raw, mechanics, flow, baseline_normalized = positive_two_boundary_normalized_case
    value = _parse_crosscheck(leaves.INDEPENDENT_VISUAL_CROSSCHECK_TWO_BOUNDARY_V1)
    value["boundary_checks"][0]["decision"] = "reject"
    mutated_raw = _seal_crosscheck(value)
    mutated_row = _reseal_admission_row_for_crosscheck(baseline_row, mutated_raw)
    _assert_pre_normalizer_contract(row=mutated_row, witness_raw=witness_raw, render_png_raw=render_png_raw, crosscheck_raw=mutated_raw, mechanics=mechanics, flow=flow, expected_predicates={
            "fixture_pre_visual_binding_is_valid": True,
            "fixture_admission_is_valid": True,
            "fixture_admission_row_matches_derive_leaves": True,
            "visual_crosscheck_leaf_matches_admission": True,
            "visual_crosscheck_root_binding_matches": True,
            "visual_crosscheck_root_context_matches": True,
            "visual_crosscheck_reviewer_matches_contract": True,
            "visual_crosscheck_cardinality_matches": True,
            "visual_crosscheck_block_region_matches": True,
            "visual_crosscheck_block_transcription_matches": True,
            "visual_crosscheck_block_decision_matches": True,
            "visual_crosscheck_boundary_region_matches": True,
            "visual_crosscheck_boundary_decision_matches": False,
            "visual_crosscheck_inventory_matches": True,
            "visual_crosscheck_content_seal_matches": True,
        })
    with pytest.raises(RawPdfError, match="^page_proof_visual_crosscheck_invalid$"):
        page_proof._normalize_fixture_visual_crosscheck(mechanics, flow, mutated_raw, mutated_row)
    value["boundary_checks"][0]["decision"] = "confirm"
    repaired_raw = _seal_crosscheck(value)
    repaired_row = _reseal_admission_row_for_crosscheck(baseline_row, repaired_raw)
    assert repaired_raw == baseline_raw
    _assert_pre_normalizer_contract(row=repaired_row, witness_raw=witness_raw, render_png_raw=render_png_raw, crosscheck_raw=repaired_raw, mechanics=mechanics, flow=flow, expected_predicates={
            "fixture_pre_visual_binding_is_valid": True,
            "fixture_admission_is_valid": True,
            "fixture_admission_row_matches_derive_leaves": True,
            "visual_crosscheck_leaf_matches_admission": True,
            "visual_crosscheck_root_binding_matches": True,
            "visual_crosscheck_root_context_matches": True,
            "visual_crosscheck_reviewer_matches_contract": True,
            "visual_crosscheck_cardinality_matches": True,
            "visual_crosscheck_block_region_matches": True,
            "visual_crosscheck_block_transcription_matches": True,
            "visual_crosscheck_block_decision_matches": True,
            "visual_crosscheck_boundary_region_matches": True,
            "visual_crosscheck_boundary_decision_matches": True,
            "visual_crosscheck_inventory_matches": True,
            "visual_crosscheck_content_seal_matches": True,
        })
    repaired_normalized = page_proof._normalize_fixture_visual_crosscheck(mechanics, flow, repaired_raw, repaired_row)
    assert _canonical_json(repaired_normalized) == _canonical_json(baseline_normalized)


def test_visual_crosscheck_boundary_wrong_reason_target_only_repair(positive_two_boundary_normalized_case):
    baseline_row, witness_raw, render_png_raw, baseline_raw, mechanics, flow, baseline_normalized = positive_two_boundary_normalized_case
    value = _parse_crosscheck(leaves.INDEPENDENT_VISUAL_CROSSCHECK_TWO_BOUNDARY_V1)
    value["boundary_checks"][0]["decision_reason"] = "other"
    mutated_raw = _seal_crosscheck(value)
    mutated_row = _reseal_admission_row_for_crosscheck(baseline_row, mutated_raw)
    _assert_pre_normalizer_contract(row=mutated_row, witness_raw=witness_raw, render_png_raw=render_png_raw, crosscheck_raw=mutated_raw, mechanics=mechanics, flow=flow, expected_predicates={
            "fixture_pre_visual_binding_is_valid": True,
            "fixture_admission_is_valid": True,
            "fixture_admission_row_matches_derive_leaves": True,
            "visual_crosscheck_leaf_matches_admission": True,
            "visual_crosscheck_root_binding_matches": True,
            "visual_crosscheck_root_context_matches": True,
            "visual_crosscheck_reviewer_matches_contract": True,
            "visual_crosscheck_cardinality_matches": True,
            "visual_crosscheck_block_region_matches": True,
            "visual_crosscheck_block_transcription_matches": True,
            "visual_crosscheck_block_decision_matches": True,
            "visual_crosscheck_boundary_region_matches": True,
            "visual_crosscheck_boundary_decision_matches": False,
            "visual_crosscheck_inventory_matches": True,
            "visual_crosscheck_content_seal_matches": True,
        })
    with pytest.raises(RawPdfError, match="^page_proof_visual_crosscheck_invalid$"):
        page_proof._normalize_fixture_visual_crosscheck(mechanics, flow, mutated_raw, mutated_row)
    value["boundary_checks"][0]["decision_reason"] = "matches_expected_boundary"
    repaired_raw = _seal_crosscheck(value)
    repaired_row = _reseal_admission_row_for_crosscheck(baseline_row, repaired_raw)
    assert repaired_raw == baseline_raw
    _assert_pre_normalizer_contract(row=repaired_row, witness_raw=witness_raw, render_png_raw=render_png_raw, crosscheck_raw=repaired_raw, mechanics=mechanics, flow=flow, expected_predicates={
            "fixture_pre_visual_binding_is_valid": True,
            "fixture_admission_is_valid": True,
            "fixture_admission_row_matches_derive_leaves": True,
            "visual_crosscheck_leaf_matches_admission": True,
            "visual_crosscheck_root_binding_matches": True,
            "visual_crosscheck_root_context_matches": True,
            "visual_crosscheck_reviewer_matches_contract": True,
            "visual_crosscheck_cardinality_matches": True,
            "visual_crosscheck_block_region_matches": True,
            "visual_crosscheck_block_transcription_matches": True,
            "visual_crosscheck_block_decision_matches": True,
            "visual_crosscheck_boundary_region_matches": True,
            "visual_crosscheck_boundary_decision_matches": True,
            "visual_crosscheck_inventory_matches": True,
            "visual_crosscheck_content_seal_matches": True,
        })
    repaired_normalized = page_proof._normalize_fixture_visual_crosscheck(mechanics, flow, repaired_raw, repaired_row)
    assert _canonical_json(repaired_normalized) == _canonical_json(baseline_normalized)


def test_visual_crosscheck_boundary_stale_decision_sha_target_only_repair(positive_two_boundary_normalized_case):
    baseline_row, witness_raw, render_png_raw, baseline_raw, mechanics, flow, baseline_normalized = positive_two_boundary_normalized_case
    value = _parse_crosscheck(leaves.INDEPENDENT_VISUAL_CROSSCHECK_TWO_BOUNDARY_V1)
    literal_decision_sha = value["boundary_checks"][0]["decision_sha256"]
    value["boundary_checks"][0]["decision_sha256"] = "0" * 64
    mutated_raw = _seal_crosscheck(value, keep_boundary_digest_index=0)
    mutated_row = _reseal_admission_row_for_crosscheck(baseline_row, mutated_raw)
    _assert_pre_normalizer_contract(row=mutated_row, witness_raw=witness_raw, render_png_raw=render_png_raw, crosscheck_raw=mutated_raw, mechanics=mechanics, flow=flow, expected_predicates={
            "fixture_pre_visual_binding_is_valid": True,
            "fixture_admission_is_valid": True,
            "fixture_admission_row_matches_derive_leaves": True,
            "visual_crosscheck_leaf_matches_admission": True,
            "visual_crosscheck_root_binding_matches": True,
            "visual_crosscheck_root_context_matches": True,
            "visual_crosscheck_reviewer_matches_contract": True,
            "visual_crosscheck_cardinality_matches": True,
            "visual_crosscheck_block_region_matches": True,
            "visual_crosscheck_block_transcription_matches": True,
            "visual_crosscheck_block_decision_matches": True,
            "visual_crosscheck_boundary_region_matches": True,
            "visual_crosscheck_boundary_decision_matches": False,
            "visual_crosscheck_inventory_matches": True,
            "visual_crosscheck_content_seal_matches": True,
        })
    with pytest.raises(RawPdfError, match="^page_proof_visual_crosscheck_invalid$"):
        page_proof._normalize_fixture_visual_crosscheck(mechanics, flow, mutated_raw, mutated_row)
    value["boundary_checks"][0]["decision_sha256"] = literal_decision_sha
    repaired_raw = _seal_crosscheck(value)
    repaired_row = _reseal_admission_row_for_crosscheck(baseline_row, repaired_raw)
    assert repaired_raw == baseline_raw
    _assert_pre_normalizer_contract(row=repaired_row, witness_raw=witness_raw, render_png_raw=render_png_raw, crosscheck_raw=repaired_raw, mechanics=mechanics, flow=flow, expected_predicates={
            "fixture_pre_visual_binding_is_valid": True,
            "fixture_admission_is_valid": True,
            "fixture_admission_row_matches_derive_leaves": True,
            "visual_crosscheck_leaf_matches_admission": True,
            "visual_crosscheck_root_binding_matches": True,
            "visual_crosscheck_root_context_matches": True,
            "visual_crosscheck_reviewer_matches_contract": True,
            "visual_crosscheck_cardinality_matches": True,
            "visual_crosscheck_block_region_matches": True,
            "visual_crosscheck_block_transcription_matches": True,
            "visual_crosscheck_block_decision_matches": True,
            "visual_crosscheck_boundary_region_matches": True,
            "visual_crosscheck_boundary_decision_matches": True,
            "visual_crosscheck_inventory_matches": True,
            "visual_crosscheck_content_seal_matches": True,
        })
    repaired_normalized = page_proof._normalize_fixture_visual_crosscheck(mechanics, flow, repaired_raw, repaired_row)
    assert _canonical_json(repaired_normalized) == _canonical_json(baseline_normalized)


def test_visual_crosscheck_block_missing_final_row_target_only_repair(positive_two_boundary_normalized_case):
    baseline_row, witness_raw, render_png_raw, baseline_raw, mechanics, flow, baseline_normalized = positive_two_boundary_normalized_case
    value = _parse_crosscheck(leaves.INDEPENDENT_VISUAL_CROSSCHECK_TWO_BOUNDARY_V1)
    value["block_checks"].pop(1)
    mutated_raw = _seal_crosscheck(value)
    mutated_row = _reseal_admission_row_for_crosscheck(baseline_row, mutated_raw)
    _assert_pre_normalizer_contract(row=mutated_row, witness_raw=witness_raw, render_png_raw=render_png_raw, crosscheck_raw=mutated_raw, mechanics=mechanics, flow=flow, expected_predicates={
            "fixture_pre_visual_binding_is_valid": True,
            "fixture_admission_is_valid": True,
            "fixture_admission_row_matches_derive_leaves": True,
            "visual_crosscheck_leaf_matches_admission": True,
            "visual_crosscheck_root_binding_matches": True,
            "visual_crosscheck_root_context_matches": True,
            "visual_crosscheck_reviewer_matches_contract": True,
            "visual_crosscheck_cardinality_matches": False,
            "visual_crosscheck_block_region_matches": True,
            "visual_crosscheck_block_transcription_matches": True,
            "visual_crosscheck_block_decision_matches": True,
            "visual_crosscheck_boundary_region_matches": True,
            "visual_crosscheck_boundary_decision_matches": True,
            "visual_crosscheck_inventory_matches": True,
            "visual_crosscheck_content_seal_matches": True,
        })
    with pytest.raises(RawPdfError, match="^page_proof_visual_crosscheck_invalid$"):
        page_proof._normalize_fixture_visual_crosscheck(mechanics, flow, mutated_raw, mutated_row)
    value["block_checks"].insert(1, _parse_crosscheck(leaves.INDEPENDENT_VISUAL_CROSSCHECK_TWO_BOUNDARY_V1)["block_checks"][1])
    repaired_raw = _seal_crosscheck(value)
    repaired_row = _reseal_admission_row_for_crosscheck(baseline_row, repaired_raw)
    assert repaired_raw == baseline_raw
    _assert_pre_normalizer_contract(row=repaired_row, witness_raw=witness_raw, render_png_raw=render_png_raw, crosscheck_raw=repaired_raw, mechanics=mechanics, flow=flow, expected_predicates={
            "fixture_pre_visual_binding_is_valid": True,
            "fixture_admission_is_valid": True,
            "fixture_admission_row_matches_derive_leaves": True,
            "visual_crosscheck_leaf_matches_admission": True,
            "visual_crosscheck_root_binding_matches": True,
            "visual_crosscheck_root_context_matches": True,
            "visual_crosscheck_reviewer_matches_contract": True,
            "visual_crosscheck_cardinality_matches": True,
            "visual_crosscheck_block_region_matches": True,
            "visual_crosscheck_block_transcription_matches": True,
            "visual_crosscheck_block_decision_matches": True,
            "visual_crosscheck_boundary_region_matches": True,
            "visual_crosscheck_boundary_decision_matches": True,
            "visual_crosscheck_inventory_matches": True,
            "visual_crosscheck_content_seal_matches": True,
        })
    repaired_normalized = page_proof._normalize_fixture_visual_crosscheck(mechanics, flow, repaired_raw, repaired_row)
    assert _canonical_json(repaired_normalized) == _canonical_json(baseline_normalized)


def test_visual_crosscheck_block_duplicate_final_row_target_only_repair(positive_two_boundary_normalized_case):
    baseline_row, witness_raw, render_png_raw, baseline_raw, mechanics, flow, baseline_normalized = positive_two_boundary_normalized_case
    value = _parse_crosscheck(leaves.INDEPENDENT_VISUAL_CROSSCHECK_TWO_BOUNDARY_V1)
    value["block_checks"].append(_parse_crosscheck(leaves.INDEPENDENT_VISUAL_CROSSCHECK_TWO_BOUNDARY_V1)["block_checks"][1])
    mutated_raw = _seal_crosscheck(value)
    mutated_row = _reseal_admission_row_for_crosscheck(baseline_row, mutated_raw)
    _assert_pre_normalizer_contract(row=mutated_row, witness_raw=witness_raw, render_png_raw=render_png_raw, crosscheck_raw=mutated_raw, mechanics=mechanics, flow=flow, expected_predicates={
            "fixture_pre_visual_binding_is_valid": True,
            "fixture_admission_is_valid": True,
            "fixture_admission_row_matches_derive_leaves": True,
            "visual_crosscheck_leaf_matches_admission": True,
            "visual_crosscheck_root_binding_matches": True,
            "visual_crosscheck_root_context_matches": True,
            "visual_crosscheck_reviewer_matches_contract": True,
            "visual_crosscheck_cardinality_matches": False,
            "visual_crosscheck_block_region_matches": True,
            "visual_crosscheck_block_transcription_matches": True,
            "visual_crosscheck_block_decision_matches": True,
            "visual_crosscheck_boundary_region_matches": True,
            "visual_crosscheck_boundary_decision_matches": True,
            "visual_crosscheck_inventory_matches": True,
            "visual_crosscheck_content_seal_matches": True,
        })
    with pytest.raises(RawPdfError, match="^page_proof_visual_crosscheck_invalid$"):
        page_proof._normalize_fixture_visual_crosscheck(mechanics, flow, mutated_raw, mutated_row)
    value["block_checks"].pop()
    repaired_raw = _seal_crosscheck(value)
    repaired_row = _reseal_admission_row_for_crosscheck(baseline_row, repaired_raw)
    assert repaired_raw == baseline_raw
    _assert_pre_normalizer_contract(row=repaired_row, witness_raw=witness_raw, render_png_raw=render_png_raw, crosscheck_raw=repaired_raw, mechanics=mechanics, flow=flow, expected_predicates={
            "fixture_pre_visual_binding_is_valid": True,
            "fixture_admission_is_valid": True,
            "fixture_admission_row_matches_derive_leaves": True,
            "visual_crosscheck_leaf_matches_admission": True,
            "visual_crosscheck_root_binding_matches": True,
            "visual_crosscheck_root_context_matches": True,
            "visual_crosscheck_reviewer_matches_contract": True,
            "visual_crosscheck_cardinality_matches": True,
            "visual_crosscheck_block_region_matches": True,
            "visual_crosscheck_block_transcription_matches": True,
            "visual_crosscheck_block_decision_matches": True,
            "visual_crosscheck_boundary_region_matches": True,
            "visual_crosscheck_boundary_decision_matches": True,
            "visual_crosscheck_inventory_matches": True,
            "visual_crosscheck_content_seal_matches": True,
        })
    repaired_normalized = page_proof._normalize_fixture_visual_crosscheck(mechanics, flow, repaired_raw, repaired_row)
    assert _canonical_json(repaired_normalized) == _canonical_json(baseline_normalized)


def test_visual_crosscheck_block_reordered_rows_target_only_repair(positive_two_boundary_normalized_case):
    baseline_row, witness_raw, render_png_raw, baseline_raw, mechanics, flow, baseline_normalized = positive_two_boundary_normalized_case
    value = _parse_crosscheck(leaves.INDEPENDENT_VISUAL_CROSSCHECK_TWO_BOUNDARY_V1)
    value["block_checks"][0], value["block_checks"][1] = value["block_checks"][1], value["block_checks"][0]
    mutated_raw = _seal_crosscheck(value)
    mutated_row = _reseal_admission_row_for_crosscheck(baseline_row, mutated_raw)
    _assert_pre_normalizer_contract(row=mutated_row, witness_raw=witness_raw, render_png_raw=render_png_raw, crosscheck_raw=mutated_raw, mechanics=mechanics, flow=flow, expected_predicates={
            "fixture_pre_visual_binding_is_valid": True,
            "fixture_admission_is_valid": True,
            "fixture_admission_row_matches_derive_leaves": True,
            "visual_crosscheck_leaf_matches_admission": True,
            "visual_crosscheck_root_binding_matches": True,
            "visual_crosscheck_root_context_matches": True,
            "visual_crosscheck_reviewer_matches_contract": True,
            "visual_crosscheck_cardinality_matches": True,
            "visual_crosscheck_block_region_matches": False,
            "visual_crosscheck_block_transcription_matches": True,
            "visual_crosscheck_block_decision_matches": True,
            "visual_crosscheck_boundary_region_matches": True,
            "visual_crosscheck_boundary_decision_matches": True,
            "visual_crosscheck_inventory_matches": True,
            "visual_crosscheck_content_seal_matches": True,
        })
    with pytest.raises(RawPdfError, match="^page_proof_visual_crosscheck_invalid$"):
        page_proof._normalize_fixture_visual_crosscheck(mechanics, flow, mutated_raw, mutated_row)
    value["block_checks"][0], value["block_checks"][1] = value["block_checks"][1], value["block_checks"][0]
    repaired_raw = _seal_crosscheck(value)
    repaired_row = _reseal_admission_row_for_crosscheck(baseline_row, repaired_raw)
    assert repaired_raw == baseline_raw
    _assert_pre_normalizer_contract(row=repaired_row, witness_raw=witness_raw, render_png_raw=render_png_raw, crosscheck_raw=repaired_raw, mechanics=mechanics, flow=flow, expected_predicates={
            "fixture_pre_visual_binding_is_valid": True,
            "fixture_admission_is_valid": True,
            "fixture_admission_row_matches_derive_leaves": True,
            "visual_crosscheck_leaf_matches_admission": True,
            "visual_crosscheck_root_binding_matches": True,
            "visual_crosscheck_root_context_matches": True,
            "visual_crosscheck_reviewer_matches_contract": True,
            "visual_crosscheck_cardinality_matches": True,
            "visual_crosscheck_block_region_matches": True,
            "visual_crosscheck_block_transcription_matches": True,
            "visual_crosscheck_block_decision_matches": True,
            "visual_crosscheck_boundary_region_matches": True,
            "visual_crosscheck_boundary_decision_matches": True,
            "visual_crosscheck_inventory_matches": True,
            "visual_crosscheck_content_seal_matches": True,
        })
    repaired_normalized = page_proof._normalize_fixture_visual_crosscheck(mechanics, flow, repaired_raw, repaired_row)
    assert _canonical_json(repaired_normalized) == _canonical_json(baseline_normalized)


def test_visual_crosscheck_block_id_target_only_repair(positive_two_boundary_normalized_case):
    baseline_row, witness_raw, render_png_raw, baseline_raw, mechanics, flow, baseline_normalized = positive_two_boundary_normalized_case
    value = _parse_crosscheck(leaves.INDEPENDENT_VISUAL_CROSSCHECK_TWO_BOUNDARY_V1)
    value["block_checks"][0]["block_id"] = "bad"
    mutated_raw = _seal_crosscheck(value)
    mutated_row = _reseal_admission_row_for_crosscheck(baseline_row, mutated_raw)
    _assert_pre_normalizer_contract(row=mutated_row, witness_raw=witness_raw, render_png_raw=render_png_raw, crosscheck_raw=mutated_raw, mechanics=mechanics, flow=flow, expected_predicates={
            "fixture_pre_visual_binding_is_valid": True,
            "fixture_admission_is_valid": True,
            "fixture_admission_row_matches_derive_leaves": True,
            "visual_crosscheck_leaf_matches_admission": True,
            "visual_crosscheck_root_binding_matches": True,
            "visual_crosscheck_root_context_matches": True,
            "visual_crosscheck_reviewer_matches_contract": True,
            "visual_crosscheck_cardinality_matches": True,
            "visual_crosscheck_block_region_matches": False,
            "visual_crosscheck_block_transcription_matches": True,
            "visual_crosscheck_block_decision_matches": True,
            "visual_crosscheck_boundary_region_matches": True,
            "visual_crosscheck_boundary_decision_matches": True,
            "visual_crosscheck_inventory_matches": True,
            "visual_crosscheck_content_seal_matches": True,
        })
    with pytest.raises(RawPdfError, match="^page_proof_visual_crosscheck_invalid$"):
        page_proof._normalize_fixture_visual_crosscheck(mechanics, flow, mutated_raw, mutated_row)
    value["block_checks"][0]["block_id"] = "b0"
    repaired_raw = _seal_crosscheck(value)
    repaired_row = _reseal_admission_row_for_crosscheck(baseline_row, repaired_raw)
    assert repaired_raw == baseline_raw
    _assert_pre_normalizer_contract(row=repaired_row, witness_raw=witness_raw, render_png_raw=render_png_raw, crosscheck_raw=repaired_raw, mechanics=mechanics, flow=flow, expected_predicates={
            "fixture_pre_visual_binding_is_valid": True,
            "fixture_admission_is_valid": True,
            "fixture_admission_row_matches_derive_leaves": True,
            "visual_crosscheck_leaf_matches_admission": True,
            "visual_crosscheck_root_binding_matches": True,
            "visual_crosscheck_root_context_matches": True,
            "visual_crosscheck_reviewer_matches_contract": True,
            "visual_crosscheck_cardinality_matches": True,
            "visual_crosscheck_block_region_matches": True,
            "visual_crosscheck_block_transcription_matches": True,
            "visual_crosscheck_block_decision_matches": True,
            "visual_crosscheck_boundary_region_matches": True,
            "visual_crosscheck_boundary_decision_matches": True,
            "visual_crosscheck_inventory_matches": True,
            "visual_crosscheck_content_seal_matches": True,
        })
    repaired_normalized = page_proof._normalize_fixture_visual_crosscheck(mechanics, flow, repaired_raw, repaired_row)
    assert _canonical_json(repaired_normalized) == _canonical_json(baseline_normalized)


def test_visual_crosscheck_block_ordinal_target_only_repair(positive_two_boundary_normalized_case):
    baseline_row, witness_raw, render_png_raw, baseline_raw, mechanics, flow, baseline_normalized = positive_two_boundary_normalized_case
    value = _parse_crosscheck(leaves.INDEPENDENT_VISUAL_CROSSCHECK_TWO_BOUNDARY_V1)
    value["block_checks"][0]["block_ordinal"] = 1
    mutated_raw = _seal_crosscheck(value)
    mutated_row = _reseal_admission_row_for_crosscheck(baseline_row, mutated_raw)
    _assert_pre_normalizer_contract(row=mutated_row, witness_raw=witness_raw, render_png_raw=render_png_raw, crosscheck_raw=mutated_raw, mechanics=mechanics, flow=flow, expected_predicates={
            "fixture_pre_visual_binding_is_valid": True,
            "fixture_admission_is_valid": True,
            "fixture_admission_row_matches_derive_leaves": True,
            "visual_crosscheck_leaf_matches_admission": True,
            "visual_crosscheck_root_binding_matches": True,
            "visual_crosscheck_root_context_matches": True,
            "visual_crosscheck_reviewer_matches_contract": True,
            "visual_crosscheck_cardinality_matches": True,
            "visual_crosscheck_block_region_matches": False,
            "visual_crosscheck_block_transcription_matches": True,
            "visual_crosscheck_block_decision_matches": True,
            "visual_crosscheck_boundary_region_matches": True,
            "visual_crosscheck_boundary_decision_matches": True,
            "visual_crosscheck_inventory_matches": True,
            "visual_crosscheck_content_seal_matches": True,
        })
    with pytest.raises(RawPdfError, match="^page_proof_visual_crosscheck_invalid$"):
        page_proof._normalize_fixture_visual_crosscheck(mechanics, flow, mutated_raw, mutated_row)
    value["block_checks"][0]["block_ordinal"] = 0
    repaired_raw = _seal_crosscheck(value)
    repaired_row = _reseal_admission_row_for_crosscheck(baseline_row, repaired_raw)
    assert repaired_raw == baseline_raw
    _assert_pre_normalizer_contract(row=repaired_row, witness_raw=witness_raw, render_png_raw=render_png_raw, crosscheck_raw=repaired_raw, mechanics=mechanics, flow=flow, expected_predicates={
            "fixture_pre_visual_binding_is_valid": True,
            "fixture_admission_is_valid": True,
            "fixture_admission_row_matches_derive_leaves": True,
            "visual_crosscheck_leaf_matches_admission": True,
            "visual_crosscheck_root_binding_matches": True,
            "visual_crosscheck_root_context_matches": True,
            "visual_crosscheck_reviewer_matches_contract": True,
            "visual_crosscheck_cardinality_matches": True,
            "visual_crosscheck_block_region_matches": True,
            "visual_crosscheck_block_transcription_matches": True,
            "visual_crosscheck_block_decision_matches": True,
            "visual_crosscheck_boundary_region_matches": True,
            "visual_crosscheck_boundary_decision_matches": True,
            "visual_crosscheck_inventory_matches": True,
            "visual_crosscheck_content_seal_matches": True,
        })
    repaired_normalized = page_proof._normalize_fixture_visual_crosscheck(mechanics, flow, repaired_raw, repaired_row)
    assert _canonical_json(repaired_normalized) == _canonical_json(baseline_normalized)


def test_visual_crosscheck_block_disposition_target_only_repair(positive_two_boundary_normalized_case):
    baseline_row, witness_raw, render_png_raw, baseline_raw, mechanics, flow, baseline_normalized = positive_two_boundary_normalized_case
    value = _parse_crosscheck(leaves.INDEPENDENT_VISUAL_CROSSCHECK_TWO_BOUNDARY_V1)
    value["block_checks"][0]["reading_flow_disposition"] = "excluded"
    mutated_raw = _seal_crosscheck(value)
    mutated_row = _reseal_admission_row_for_crosscheck(baseline_row, mutated_raw)
    _assert_pre_normalizer_contract(row=mutated_row, witness_raw=witness_raw, render_png_raw=render_png_raw, crosscheck_raw=mutated_raw, mechanics=mechanics, flow=flow, expected_predicates={
            "fixture_pre_visual_binding_is_valid": True,
            "fixture_admission_is_valid": True,
            "fixture_admission_row_matches_derive_leaves": True,
            "visual_crosscheck_leaf_matches_admission": True,
            "visual_crosscheck_root_binding_matches": True,
            "visual_crosscheck_root_context_matches": True,
            "visual_crosscheck_reviewer_matches_contract": True,
            "visual_crosscheck_cardinality_matches": True,
            "visual_crosscheck_block_region_matches": False,
            "visual_crosscheck_block_transcription_matches": True,
            "visual_crosscheck_block_decision_matches": True,
            "visual_crosscheck_boundary_region_matches": True,
            "visual_crosscheck_boundary_decision_matches": True,
            "visual_crosscheck_inventory_matches": True,
            "visual_crosscheck_content_seal_matches": True,
        })
    with pytest.raises(RawPdfError, match="^page_proof_visual_crosscheck_invalid$"):
        page_proof._normalize_fixture_visual_crosscheck(mechanics, flow, mutated_raw, mutated_row)
    value["block_checks"][0]["reading_flow_disposition"] = "included"
    repaired_raw = _seal_crosscheck(value)
    repaired_row = _reseal_admission_row_for_crosscheck(baseline_row, repaired_raw)
    assert repaired_raw == baseline_raw
    _assert_pre_normalizer_contract(row=repaired_row, witness_raw=witness_raw, render_png_raw=render_png_raw, crosscheck_raw=repaired_raw, mechanics=mechanics, flow=flow, expected_predicates={
            "fixture_pre_visual_binding_is_valid": True,
            "fixture_admission_is_valid": True,
            "fixture_admission_row_matches_derive_leaves": True,
            "visual_crosscheck_leaf_matches_admission": True,
            "visual_crosscheck_root_binding_matches": True,
            "visual_crosscheck_root_context_matches": True,
            "visual_crosscheck_reviewer_matches_contract": True,
            "visual_crosscheck_cardinality_matches": True,
            "visual_crosscheck_block_region_matches": True,
            "visual_crosscheck_block_transcription_matches": True,
            "visual_crosscheck_block_decision_matches": True,
            "visual_crosscheck_boundary_region_matches": True,
            "visual_crosscheck_boundary_decision_matches": True,
            "visual_crosscheck_inventory_matches": True,
            "visual_crosscheck_content_seal_matches": True,
        })
    repaired_normalized = page_proof._normalize_fixture_visual_crosscheck(mechanics, flow, repaired_raw, repaired_row)
    assert _canonical_json(repaired_normalized) == _canonical_json(baseline_normalized)


def test_visual_crosscheck_block_reason_target_only_repair(positive_two_boundary_normalized_case):
    baseline_row, witness_raw, render_png_raw, baseline_raw, mechanics, flow, baseline_normalized = positive_two_boundary_normalized_case
    value = _parse_crosscheck(leaves.INDEPENDENT_VISUAL_CROSSCHECK_TWO_BOUNDARY_V1)
    value["block_checks"][0]["reading_flow_reason"] = "visual_only"
    mutated_raw = _seal_crosscheck(value)
    mutated_row = _reseal_admission_row_for_crosscheck(baseline_row, mutated_raw)
    _assert_pre_normalizer_contract(row=mutated_row, witness_raw=witness_raw, render_png_raw=render_png_raw, crosscheck_raw=mutated_raw, mechanics=mechanics, flow=flow, expected_predicates={
            "fixture_pre_visual_binding_is_valid": True,
            "fixture_admission_is_valid": True,
            "fixture_admission_row_matches_derive_leaves": True,
            "visual_crosscheck_leaf_matches_admission": True,
            "visual_crosscheck_root_binding_matches": True,
            "visual_crosscheck_root_context_matches": True,
            "visual_crosscheck_reviewer_matches_contract": True,
            "visual_crosscheck_cardinality_matches": True,
            "visual_crosscheck_block_region_matches": False,
            "visual_crosscheck_block_transcription_matches": True,
            "visual_crosscheck_block_decision_matches": True,
            "visual_crosscheck_boundary_region_matches": True,
            "visual_crosscheck_boundary_decision_matches": True,
            "visual_crosscheck_inventory_matches": True,
            "visual_crosscheck_content_seal_matches": True,
        })
    with pytest.raises(RawPdfError, match="^page_proof_visual_crosscheck_invalid$"):
        page_proof._normalize_fixture_visual_crosscheck(mechanics, flow, mutated_raw, mutated_row)
    value["block_checks"][0]["reading_flow_reason"] = "included"
    repaired_raw = _seal_crosscheck(value)
    repaired_row = _reseal_admission_row_for_crosscheck(baseline_row, repaired_raw)
    assert repaired_raw == baseline_raw
    _assert_pre_normalizer_contract(row=repaired_row, witness_raw=witness_raw, render_png_raw=render_png_raw, crosscheck_raw=repaired_raw, mechanics=mechanics, flow=flow, expected_predicates={
            "fixture_pre_visual_binding_is_valid": True,
            "fixture_admission_is_valid": True,
            "fixture_admission_row_matches_derive_leaves": True,
            "visual_crosscheck_leaf_matches_admission": True,
            "visual_crosscheck_root_binding_matches": True,
            "visual_crosscheck_root_context_matches": True,
            "visual_crosscheck_reviewer_matches_contract": True,
            "visual_crosscheck_cardinality_matches": True,
            "visual_crosscheck_block_region_matches": True,
            "visual_crosscheck_block_transcription_matches": True,
            "visual_crosscheck_block_decision_matches": True,
            "visual_crosscheck_boundary_region_matches": True,
            "visual_crosscheck_boundary_decision_matches": True,
            "visual_crosscheck_inventory_matches": True,
            "visual_crosscheck_content_seal_matches": True,
        })
    repaired_normalized = page_proof._normalize_fixture_visual_crosscheck(mechanics, flow, repaired_raw, repaired_row)
    assert _canonical_json(repaired_normalized) == _canonical_json(baseline_normalized)


def test_visual_crosscheck_block_column_target_only_repair(positive_two_boundary_normalized_case):
    baseline_row, witness_raw, render_png_raw, baseline_raw, mechanics, flow, baseline_normalized = positive_two_boundary_normalized_case
    value = _parse_crosscheck(leaves.INDEPENDENT_VISUAL_CROSSCHECK_TWO_BOUNDARY_V1)
    value["block_checks"][0]["column_index"] = 0
    mutated_raw = _seal_crosscheck(value)
    mutated_row = _reseal_admission_row_for_crosscheck(baseline_row, mutated_raw)
    _assert_pre_normalizer_contract(row=mutated_row, witness_raw=witness_raw, render_png_raw=render_png_raw, crosscheck_raw=mutated_raw, mechanics=mechanics, flow=flow, expected_predicates={
            "fixture_pre_visual_binding_is_valid": True,
            "fixture_admission_is_valid": True,
            "fixture_admission_row_matches_derive_leaves": True,
            "visual_crosscheck_leaf_matches_admission": True,
            "visual_crosscheck_root_binding_matches": True,
            "visual_crosscheck_root_context_matches": True,
            "visual_crosscheck_reviewer_matches_contract": True,
            "visual_crosscheck_cardinality_matches": True,
            "visual_crosscheck_block_region_matches": False,
            "visual_crosscheck_block_transcription_matches": True,
            "visual_crosscheck_block_decision_matches": True,
            "visual_crosscheck_boundary_region_matches": True,
            "visual_crosscheck_boundary_decision_matches": True,
            "visual_crosscheck_inventory_matches": True,
            "visual_crosscheck_content_seal_matches": True,
        })
    with pytest.raises(RawPdfError, match="^page_proof_visual_crosscheck_invalid$"):
        page_proof._normalize_fixture_visual_crosscheck(mechanics, flow, mutated_raw, mutated_row)
    value["block_checks"][0]["column_index"] = 1
    repaired_raw = _seal_crosscheck(value)
    repaired_row = _reseal_admission_row_for_crosscheck(baseline_row, repaired_raw)
    assert repaired_raw == baseline_raw
    _assert_pre_normalizer_contract(row=repaired_row, witness_raw=witness_raw, render_png_raw=render_png_raw, crosscheck_raw=repaired_raw, mechanics=mechanics, flow=flow, expected_predicates={
            "fixture_pre_visual_binding_is_valid": True,
            "fixture_admission_is_valid": True,
            "fixture_admission_row_matches_derive_leaves": True,
            "visual_crosscheck_leaf_matches_admission": True,
            "visual_crosscheck_root_binding_matches": True,
            "visual_crosscheck_root_context_matches": True,
            "visual_crosscheck_reviewer_matches_contract": True,
            "visual_crosscheck_cardinality_matches": True,
            "visual_crosscheck_block_region_matches": True,
            "visual_crosscheck_block_transcription_matches": True,
            "visual_crosscheck_block_decision_matches": True,
            "visual_crosscheck_boundary_region_matches": True,
            "visual_crosscheck_boundary_decision_matches": True,
            "visual_crosscheck_inventory_matches": True,
            "visual_crosscheck_content_seal_matches": True,
        })
    repaired_normalized = page_proof._normalize_fixture_visual_crosscheck(mechanics, flow, repaired_raw, repaired_row)
    assert _canonical_json(repaired_normalized) == _canonical_json(baseline_normalized)


def test_visual_crosscheck_block_bbox_target_only_repair(positive_two_boundary_normalized_case):
    baseline_row, witness_raw, render_png_raw, baseline_raw, mechanics, flow, baseline_normalized = positive_two_boundary_normalized_case
    value = _parse_crosscheck(leaves.INDEPENDENT_VISUAL_CROSSCHECK_TWO_BOUNDARY_V1)
    value["block_checks"][0]["bbox_px"] = [0, 0, 4, 3]
    mutated_raw = _seal_crosscheck(value)
    mutated_row = _reseal_admission_row_for_crosscheck(baseline_row, mutated_raw)
    _assert_pre_normalizer_contract(row=mutated_row, witness_raw=witness_raw, render_png_raw=render_png_raw, crosscheck_raw=mutated_raw, mechanics=mechanics, flow=flow, expected_predicates={
            "fixture_pre_visual_binding_is_valid": True,
            "fixture_admission_is_valid": True,
            "fixture_admission_row_matches_derive_leaves": True,
            "visual_crosscheck_leaf_matches_admission": True,
            "visual_crosscheck_root_binding_matches": True,
            "visual_crosscheck_root_context_matches": True,
            "visual_crosscheck_reviewer_matches_contract": True,
            "visual_crosscheck_cardinality_matches": True,
            "visual_crosscheck_block_region_matches": False,
            "visual_crosscheck_block_transcription_matches": True,
            "visual_crosscheck_block_decision_matches": True,
            "visual_crosscheck_boundary_region_matches": True,
            "visual_crosscheck_boundary_decision_matches": True,
            "visual_crosscheck_inventory_matches": True,
            "visual_crosscheck_content_seal_matches": True,
        })
    with pytest.raises(RawPdfError, match="^page_proof_visual_crosscheck_invalid$"):
        page_proof._normalize_fixture_visual_crosscheck(mechanics, flow, mutated_raw, mutated_row)
    value["block_checks"][0]["bbox_px"] = [0, 0, 1, 3]
    repaired_raw = _seal_crosscheck(value)
    repaired_row = _reseal_admission_row_for_crosscheck(baseline_row, repaired_raw)
    assert repaired_raw == baseline_raw
    _assert_pre_normalizer_contract(row=repaired_row, witness_raw=witness_raw, render_png_raw=render_png_raw, crosscheck_raw=repaired_raw, mechanics=mechanics, flow=flow, expected_predicates={
            "fixture_pre_visual_binding_is_valid": True,
            "fixture_admission_is_valid": True,
            "fixture_admission_row_matches_derive_leaves": True,
            "visual_crosscheck_leaf_matches_admission": True,
            "visual_crosscheck_root_binding_matches": True,
            "visual_crosscheck_root_context_matches": True,
            "visual_crosscheck_reviewer_matches_contract": True,
            "visual_crosscheck_cardinality_matches": True,
            "visual_crosscheck_block_region_matches": True,
            "visual_crosscheck_block_transcription_matches": True,
            "visual_crosscheck_block_decision_matches": True,
            "visual_crosscheck_boundary_region_matches": True,
            "visual_crosscheck_boundary_decision_matches": True,
            "visual_crosscheck_inventory_matches": True,
            "visual_crosscheck_content_seal_matches": True,
        })
    repaired_normalized = page_proof._normalize_fixture_visual_crosscheck(mechanics, flow, repaired_raw, repaired_row)
    assert _canonical_json(repaired_normalized) == _canonical_json(baseline_normalized)


def test_visual_crosscheck_block_pixel_count_target_only_repair(positive_two_boundary_normalized_case):
    baseline_row, witness_raw, render_png_raw, baseline_raw, mechanics, flow, baseline_normalized = positive_two_boundary_normalized_case
    value = _parse_crosscheck(leaves.INDEPENDENT_VISUAL_CROSSCHECK_TWO_BOUNDARY_V1)
    value["block_checks"][0]["pixel_count"] = 4
    mutated_raw = _seal_crosscheck(value)
    mutated_row = _reseal_admission_row_for_crosscheck(baseline_row, mutated_raw)
    _assert_pre_normalizer_contract(row=mutated_row, witness_raw=witness_raw, render_png_raw=render_png_raw, crosscheck_raw=mutated_raw, mechanics=mechanics, flow=flow, expected_predicates={
            "fixture_pre_visual_binding_is_valid": True,
            "fixture_admission_is_valid": True,
            "fixture_admission_row_matches_derive_leaves": True,
            "visual_crosscheck_leaf_matches_admission": True,
            "visual_crosscheck_root_binding_matches": True,
            "visual_crosscheck_root_context_matches": True,
            "visual_crosscheck_reviewer_matches_contract": True,
            "visual_crosscheck_cardinality_matches": True,
            "visual_crosscheck_block_region_matches": False,
            "visual_crosscheck_block_transcription_matches": True,
            "visual_crosscheck_block_decision_matches": True,
            "visual_crosscheck_boundary_region_matches": True,
            "visual_crosscheck_boundary_decision_matches": True,
            "visual_crosscheck_inventory_matches": True,
            "visual_crosscheck_content_seal_matches": True,
        })
    with pytest.raises(RawPdfError, match="^page_proof_visual_crosscheck_invalid$"):
        page_proof._normalize_fixture_visual_crosscheck(mechanics, flow, mutated_raw, mutated_row)
    value["block_checks"][0]["pixel_count"] = 3
    repaired_raw = _seal_crosscheck(value)
    repaired_row = _reseal_admission_row_for_crosscheck(baseline_row, repaired_raw)
    assert repaired_raw == baseline_raw
    _assert_pre_normalizer_contract(row=repaired_row, witness_raw=witness_raw, render_png_raw=render_png_raw, crosscheck_raw=repaired_raw, mechanics=mechanics, flow=flow, expected_predicates={
            "fixture_pre_visual_binding_is_valid": True,
            "fixture_admission_is_valid": True,
            "fixture_admission_row_matches_derive_leaves": True,
            "visual_crosscheck_leaf_matches_admission": True,
            "visual_crosscheck_root_binding_matches": True,
            "visual_crosscheck_root_context_matches": True,
            "visual_crosscheck_reviewer_matches_contract": True,
            "visual_crosscheck_cardinality_matches": True,
            "visual_crosscheck_block_region_matches": True,
            "visual_crosscheck_block_transcription_matches": True,
            "visual_crosscheck_block_decision_matches": True,
            "visual_crosscheck_boundary_region_matches": True,
            "visual_crosscheck_boundary_decision_matches": True,
            "visual_crosscheck_inventory_matches": True,
            "visual_crosscheck_content_seal_matches": True,
        })
    repaired_normalized = page_proof._normalize_fixture_visual_crosscheck(mechanics, flow, repaired_raw, repaired_row)
    assert _canonical_json(repaired_normalized) == _canonical_json(baseline_normalized)


def test_visual_crosscheck_block_component_evidence_target_only_repair(positive_two_boundary_normalized_case):
    baseline_row, witness_raw, render_png_raw, baseline_raw, mechanics, flow, baseline_normalized = positive_two_boundary_normalized_case
    value = _parse_crosscheck(leaves.INDEPENDENT_VISUAL_CROSSCHECK_TWO_BOUNDARY_V1)
    value["block_checks"][0]["component_evidence_sha256"] = "0" * 64
    mutated_raw = _seal_crosscheck(value)
    mutated_row = _reseal_admission_row_for_crosscheck(baseline_row, mutated_raw)
    _assert_pre_normalizer_contract(row=mutated_row, witness_raw=witness_raw, render_png_raw=render_png_raw, crosscheck_raw=mutated_raw, mechanics=mechanics, flow=flow, expected_predicates={
            "fixture_pre_visual_binding_is_valid": True,
            "fixture_admission_is_valid": True,
            "fixture_admission_row_matches_derive_leaves": True,
            "visual_crosscheck_leaf_matches_admission": True,
            "visual_crosscheck_root_binding_matches": True,
            "visual_crosscheck_root_context_matches": True,
            "visual_crosscheck_reviewer_matches_contract": True,
            "visual_crosscheck_cardinality_matches": True,
            "visual_crosscheck_block_region_matches": False,
            "visual_crosscheck_block_transcription_matches": True,
            "visual_crosscheck_block_decision_matches": True,
            "visual_crosscheck_boundary_region_matches": True,
            "visual_crosscheck_boundary_decision_matches": True,
            "visual_crosscheck_inventory_matches": True,
            "visual_crosscheck_content_seal_matches": True,
        })
    with pytest.raises(RawPdfError, match="^page_proof_visual_crosscheck_invalid$"):
        page_proof._normalize_fixture_visual_crosscheck(mechanics, flow, mutated_raw, mutated_row)
    value["block_checks"][0]["component_evidence_sha256"] = "85eb75c6260349d970e966e88ecbd71ea15c547e9d7dba4e29ac53b5e8a3aa58"
    repaired_raw = _seal_crosscheck(value)
    repaired_row = _reseal_admission_row_for_crosscheck(baseline_row, repaired_raw)
    assert repaired_raw == baseline_raw
    _assert_pre_normalizer_contract(row=repaired_row, witness_raw=witness_raw, render_png_raw=render_png_raw, crosscheck_raw=repaired_raw, mechanics=mechanics, flow=flow, expected_predicates={
            "fixture_pre_visual_binding_is_valid": True,
            "fixture_admission_is_valid": True,
            "fixture_admission_row_matches_derive_leaves": True,
            "visual_crosscheck_leaf_matches_admission": True,
            "visual_crosscheck_root_binding_matches": True,
            "visual_crosscheck_root_context_matches": True,
            "visual_crosscheck_reviewer_matches_contract": True,
            "visual_crosscheck_cardinality_matches": True,
            "visual_crosscheck_block_region_matches": True,
            "visual_crosscheck_block_transcription_matches": True,
            "visual_crosscheck_block_decision_matches": True,
            "visual_crosscheck_boundary_region_matches": True,
            "visual_crosscheck_boundary_decision_matches": True,
            "visual_crosscheck_inventory_matches": True,
            "visual_crosscheck_content_seal_matches": True,
        })
    repaired_normalized = page_proof._normalize_fixture_visual_crosscheck(mechanics, flow, repaired_raw, repaired_row)
    assert _canonical_json(repaired_normalized) == _canonical_json(baseline_normalized)


def test_visual_crosscheck_transcription_empty_bytes_target_only_repair(positive_two_boundary_normalized_case):
    baseline_row, witness_raw, render_png_raw, baseline_raw, mechanics, flow, baseline_normalized = positive_two_boundary_normalized_case
    value = _parse_crosscheck(leaves.INDEPENDENT_VISUAL_CROSSCHECK_TWO_BOUNDARY_V1)
    value["block_checks"][0]["transcription_bytes_b64"] = _b64(b"")
    mutated_raw = _seal_crosscheck(value)
    mutated_row = _reseal_admission_row_for_crosscheck(baseline_row, mutated_raw)
    _assert_pre_normalizer_contract(row=mutated_row, witness_raw=witness_raw, render_png_raw=render_png_raw, crosscheck_raw=mutated_raw, mechanics=mechanics, flow=flow, expected_predicates={
            "fixture_pre_visual_binding_is_valid": True,
            "fixture_admission_is_valid": True,
            "fixture_admission_row_matches_derive_leaves": True,
            "visual_crosscheck_leaf_matches_admission": True,
            "visual_crosscheck_root_binding_matches": True,
            "visual_crosscheck_root_context_matches": True,
            "visual_crosscheck_reviewer_matches_contract": True,
            "visual_crosscheck_cardinality_matches": True,
            "visual_crosscheck_block_region_matches": True,
            "visual_crosscheck_block_transcription_matches": False,
            "visual_crosscheck_block_decision_matches": True,
            "visual_crosscheck_boundary_region_matches": True,
            "visual_crosscheck_boundary_decision_matches": True,
            "visual_crosscheck_inventory_matches": True,
            "visual_crosscheck_content_seal_matches": True,
        })
    with pytest.raises(RawPdfError, match="^page_proof_visual_crosscheck_invalid$"):
        page_proof._normalize_fixture_visual_crosscheck(mechanics, flow, mutated_raw, mutated_row)
    value["block_checks"][0]["transcription_bytes_b64"] = "TEVGVA=="
    repaired_raw = _seal_crosscheck(value)
    repaired_row = _reseal_admission_row_for_crosscheck(baseline_row, repaired_raw)
    assert repaired_raw == baseline_raw
    _assert_pre_normalizer_contract(row=repaired_row, witness_raw=witness_raw, render_png_raw=render_png_raw, crosscheck_raw=repaired_raw, mechanics=mechanics, flow=flow, expected_predicates={
            "fixture_pre_visual_binding_is_valid": True,
            "fixture_admission_is_valid": True,
            "fixture_admission_row_matches_derive_leaves": True,
            "visual_crosscheck_leaf_matches_admission": True,
            "visual_crosscheck_root_binding_matches": True,
            "visual_crosscheck_root_context_matches": True,
            "visual_crosscheck_reviewer_matches_contract": True,
            "visual_crosscheck_cardinality_matches": True,
            "visual_crosscheck_block_region_matches": True,
            "visual_crosscheck_block_transcription_matches": True,
            "visual_crosscheck_block_decision_matches": True,
            "visual_crosscheck_boundary_region_matches": True,
            "visual_crosscheck_boundary_decision_matches": True,
            "visual_crosscheck_inventory_matches": True,
            "visual_crosscheck_content_seal_matches": True,
        })
    repaired_normalized = page_proof._normalize_fixture_visual_crosscheck(mechanics, flow, repaired_raw, repaired_row)
    assert _canonical_json(repaired_normalized) == _canonical_json(baseline_normalized)


def test_visual_crosscheck_transcription_changed_bytes_old_hash_target_only_repair(positive_two_boundary_normalized_case):
    baseline_row, witness_raw, render_png_raw, baseline_raw, mechanics, flow, baseline_normalized = positive_two_boundary_normalized_case
    value = _parse_crosscheck(leaves.INDEPENDENT_VISUAL_CROSSCHECK_TWO_BOUNDARY_V1)
    value["block_checks"][0]["transcription_bytes_b64"] = _b64(b"CHANGED")
    mutated_raw = _seal_crosscheck(value)
    mutated_row = _reseal_admission_row_for_crosscheck(baseline_row, mutated_raw)
    _assert_pre_normalizer_contract(row=mutated_row, witness_raw=witness_raw, render_png_raw=render_png_raw, crosscheck_raw=mutated_raw, mechanics=mechanics, flow=flow, expected_predicates={
            "fixture_pre_visual_binding_is_valid": True,
            "fixture_admission_is_valid": True,
            "fixture_admission_row_matches_derive_leaves": True,
            "visual_crosscheck_leaf_matches_admission": True,
            "visual_crosscheck_root_binding_matches": True,
            "visual_crosscheck_root_context_matches": True,
            "visual_crosscheck_reviewer_matches_contract": True,
            "visual_crosscheck_cardinality_matches": True,
            "visual_crosscheck_block_region_matches": True,
            "visual_crosscheck_block_transcription_matches": False,
            "visual_crosscheck_block_decision_matches": True,
            "visual_crosscheck_boundary_region_matches": True,
            "visual_crosscheck_boundary_decision_matches": True,
            "visual_crosscheck_inventory_matches": True,
            "visual_crosscheck_content_seal_matches": True,
        })
    with pytest.raises(RawPdfError, match="^page_proof_visual_crosscheck_invalid$"):
        page_proof._normalize_fixture_visual_crosscheck(mechanics, flow, mutated_raw, mutated_row)
    value["block_checks"][0]["transcription_bytes_b64"] = "TEVGVA=="
    repaired_raw = _seal_crosscheck(value)
    repaired_row = _reseal_admission_row_for_crosscheck(baseline_row, repaired_raw)
    assert repaired_raw == baseline_raw
    _assert_pre_normalizer_contract(row=repaired_row, witness_raw=witness_raw, render_png_raw=render_png_raw, crosscheck_raw=repaired_raw, mechanics=mechanics, flow=flow, expected_predicates={
            "fixture_pre_visual_binding_is_valid": True,
            "fixture_admission_is_valid": True,
            "fixture_admission_row_matches_derive_leaves": True,
            "visual_crosscheck_leaf_matches_admission": True,
            "visual_crosscheck_root_binding_matches": True,
            "visual_crosscheck_root_context_matches": True,
            "visual_crosscheck_reviewer_matches_contract": True,
            "visual_crosscheck_cardinality_matches": True,
            "visual_crosscheck_block_region_matches": True,
            "visual_crosscheck_block_transcription_matches": True,
            "visual_crosscheck_block_decision_matches": True,
            "visual_crosscheck_boundary_region_matches": True,
            "visual_crosscheck_boundary_decision_matches": True,
            "visual_crosscheck_inventory_matches": True,
            "visual_crosscheck_content_seal_matches": True,
        })
    repaired_normalized = page_proof._normalize_fixture_visual_crosscheck(mechanics, flow, repaired_raw, repaired_row)
    assert _canonical_json(repaired_normalized) == _canonical_json(baseline_normalized)


def test_visual_crosscheck_transcription_wrong_hash_target_only_repair(positive_two_boundary_normalized_case):
    baseline_row, witness_raw, render_png_raw, baseline_raw, mechanics, flow, baseline_normalized = positive_two_boundary_normalized_case
    value = _parse_crosscheck(leaves.INDEPENDENT_VISUAL_CROSSCHECK_TWO_BOUNDARY_V1)
    value["block_checks"][0]["transcription_sha256"] = "0" * 64
    mutated_raw = _seal_crosscheck(value)
    mutated_row = _reseal_admission_row_for_crosscheck(baseline_row, mutated_raw)
    _assert_pre_normalizer_contract(row=mutated_row, witness_raw=witness_raw, render_png_raw=render_png_raw, crosscheck_raw=mutated_raw, mechanics=mechanics, flow=flow, expected_predicates={
            "fixture_pre_visual_binding_is_valid": True,
            "fixture_admission_is_valid": True,
            "fixture_admission_row_matches_derive_leaves": True,
            "visual_crosscheck_leaf_matches_admission": True,
            "visual_crosscheck_root_binding_matches": True,
            "visual_crosscheck_root_context_matches": True,
            "visual_crosscheck_reviewer_matches_contract": True,
            "visual_crosscheck_cardinality_matches": True,
            "visual_crosscheck_block_region_matches": True,
            "visual_crosscheck_block_transcription_matches": False,
            "visual_crosscheck_block_decision_matches": True,
            "visual_crosscheck_boundary_region_matches": True,
            "visual_crosscheck_boundary_decision_matches": True,
            "visual_crosscheck_inventory_matches": True,
            "visual_crosscheck_content_seal_matches": True,
        })
    with pytest.raises(RawPdfError, match="^page_proof_visual_crosscheck_invalid$"):
        page_proof._normalize_fixture_visual_crosscheck(mechanics, flow, mutated_raw, mutated_row)
    value["block_checks"][0]["transcription_sha256"] = "2cba9d25c1eaf7f3ef0e86b1562165b1d66e950ff5155de71b68049916145faf"
    repaired_raw = _seal_crosscheck(value)
    repaired_row = _reseal_admission_row_for_crosscheck(baseline_row, repaired_raw)
    assert repaired_raw == baseline_raw
    _assert_pre_normalizer_contract(row=repaired_row, witness_raw=witness_raw, render_png_raw=render_png_raw, crosscheck_raw=repaired_raw, mechanics=mechanics, flow=flow, expected_predicates={
            "fixture_pre_visual_binding_is_valid": True,
            "fixture_admission_is_valid": True,
            "fixture_admission_row_matches_derive_leaves": True,
            "visual_crosscheck_leaf_matches_admission": True,
            "visual_crosscheck_root_binding_matches": True,
            "visual_crosscheck_root_context_matches": True,
            "visual_crosscheck_reviewer_matches_contract": True,
            "visual_crosscheck_cardinality_matches": True,
            "visual_crosscheck_block_region_matches": True,
            "visual_crosscheck_block_transcription_matches": True,
            "visual_crosscheck_block_decision_matches": True,
            "visual_crosscheck_boundary_region_matches": True,
            "visual_crosscheck_boundary_decision_matches": True,
            "visual_crosscheck_inventory_matches": True,
            "visual_crosscheck_content_seal_matches": True,
        })
    repaired_normalized = page_proof._normalize_fixture_visual_crosscheck(mechanics, flow, repaired_raw, repaired_row)
    assert _canonical_json(repaired_normalized) == _canonical_json(baseline_normalized)


def test_visual_crosscheck_block_nonconfirm_target_only_repair(positive_two_boundary_normalized_case):
    baseline_row, witness_raw, render_png_raw, baseline_raw, mechanics, flow, baseline_normalized = positive_two_boundary_normalized_case
    value = _parse_crosscheck(leaves.INDEPENDENT_VISUAL_CROSSCHECK_TWO_BOUNDARY_V1)
    value["block_checks"][0]["witness_decision"] = "reject"
    mutated_raw = _seal_crosscheck(value)
    mutated_row = _reseal_admission_row_for_crosscheck(baseline_row, mutated_raw)
    _assert_pre_normalizer_contract(row=mutated_row, witness_raw=witness_raw, render_png_raw=render_png_raw, crosscheck_raw=mutated_raw, mechanics=mechanics, flow=flow, expected_predicates={
            "fixture_pre_visual_binding_is_valid": True,
            "fixture_admission_is_valid": True,
            "fixture_admission_row_matches_derive_leaves": True,
            "visual_crosscheck_leaf_matches_admission": True,
            "visual_crosscheck_root_binding_matches": True,
            "visual_crosscheck_root_context_matches": True,
            "visual_crosscheck_reviewer_matches_contract": True,
            "visual_crosscheck_cardinality_matches": True,
            "visual_crosscheck_block_region_matches": True,
            "visual_crosscheck_block_transcription_matches": True,
            "visual_crosscheck_block_decision_matches": False,
            "visual_crosscheck_boundary_region_matches": True,
            "visual_crosscheck_boundary_decision_matches": True,
            "visual_crosscheck_inventory_matches": True,
            "visual_crosscheck_content_seal_matches": True,
        })
    with pytest.raises(RawPdfError, match="^page_proof_visual_crosscheck_invalid$"):
        page_proof._normalize_fixture_visual_crosscheck(mechanics, flow, mutated_raw, mutated_row)
    value["block_checks"][0]["witness_decision"] = "confirm"
    repaired_raw = _seal_crosscheck(value)
    repaired_row = _reseal_admission_row_for_crosscheck(baseline_row, repaired_raw)
    assert repaired_raw == baseline_raw
    _assert_pre_normalizer_contract(row=repaired_row, witness_raw=witness_raw, render_png_raw=render_png_raw, crosscheck_raw=repaired_raw, mechanics=mechanics, flow=flow, expected_predicates={
            "fixture_pre_visual_binding_is_valid": True,
            "fixture_admission_is_valid": True,
            "fixture_admission_row_matches_derive_leaves": True,
            "visual_crosscheck_leaf_matches_admission": True,
            "visual_crosscheck_root_binding_matches": True,
            "visual_crosscheck_root_context_matches": True,
            "visual_crosscheck_reviewer_matches_contract": True,
            "visual_crosscheck_cardinality_matches": True,
            "visual_crosscheck_block_region_matches": True,
            "visual_crosscheck_block_transcription_matches": True,
            "visual_crosscheck_block_decision_matches": True,
            "visual_crosscheck_boundary_region_matches": True,
            "visual_crosscheck_boundary_decision_matches": True,
            "visual_crosscheck_inventory_matches": True,
            "visual_crosscheck_content_seal_matches": True,
        })
    repaired_normalized = page_proof._normalize_fixture_visual_crosscheck(mechanics, flow, repaired_raw, repaired_row)
    assert _canonical_json(repaired_normalized) == _canonical_json(baseline_normalized)


def test_visual_crosscheck_block_wrong_reason_target_only_repair(positive_two_boundary_normalized_case):
    baseline_row, witness_raw, render_png_raw, baseline_raw, mechanics, flow, baseline_normalized = positive_two_boundary_normalized_case
    value = _parse_crosscheck(leaves.INDEPENDENT_VISUAL_CROSSCHECK_TWO_BOUNDARY_V1)
    value["block_checks"][0]["decision_reason"] = "other"
    mutated_raw = _seal_crosscheck(value)
    mutated_row = _reseal_admission_row_for_crosscheck(baseline_row, mutated_raw)
    _assert_pre_normalizer_contract(row=mutated_row, witness_raw=witness_raw, render_png_raw=render_png_raw, crosscheck_raw=mutated_raw, mechanics=mechanics, flow=flow, expected_predicates={
            "fixture_pre_visual_binding_is_valid": True,
            "fixture_admission_is_valid": True,
            "fixture_admission_row_matches_derive_leaves": True,
            "visual_crosscheck_leaf_matches_admission": True,
            "visual_crosscheck_root_binding_matches": True,
            "visual_crosscheck_root_context_matches": True,
            "visual_crosscheck_reviewer_matches_contract": True,
            "visual_crosscheck_cardinality_matches": True,
            "visual_crosscheck_block_region_matches": True,
            "visual_crosscheck_block_transcription_matches": True,
            "visual_crosscheck_block_decision_matches": False,
            "visual_crosscheck_boundary_region_matches": True,
            "visual_crosscheck_boundary_decision_matches": True,
            "visual_crosscheck_inventory_matches": True,
            "visual_crosscheck_content_seal_matches": True,
        })
    with pytest.raises(RawPdfError, match="^page_proof_visual_crosscheck_invalid$"):
        page_proof._normalize_fixture_visual_crosscheck(mechanics, flow, mutated_raw, mutated_row)
    value["block_checks"][0]["decision_reason"] = "matches_replayed_region_components"
    repaired_raw = _seal_crosscheck(value)
    repaired_row = _reseal_admission_row_for_crosscheck(baseline_row, repaired_raw)
    assert repaired_raw == baseline_raw
    _assert_pre_normalizer_contract(row=repaired_row, witness_raw=witness_raw, render_png_raw=render_png_raw, crosscheck_raw=repaired_raw, mechanics=mechanics, flow=flow, expected_predicates={
            "fixture_pre_visual_binding_is_valid": True,
            "fixture_admission_is_valid": True,
            "fixture_admission_row_matches_derive_leaves": True,
            "visual_crosscheck_leaf_matches_admission": True,
            "visual_crosscheck_root_binding_matches": True,
            "visual_crosscheck_root_context_matches": True,
            "visual_crosscheck_reviewer_matches_contract": True,
            "visual_crosscheck_cardinality_matches": True,
            "visual_crosscheck_block_region_matches": True,
            "visual_crosscheck_block_transcription_matches": True,
            "visual_crosscheck_block_decision_matches": True,
            "visual_crosscheck_boundary_region_matches": True,
            "visual_crosscheck_boundary_decision_matches": True,
            "visual_crosscheck_inventory_matches": True,
            "visual_crosscheck_content_seal_matches": True,
        })
    repaired_normalized = page_proof._normalize_fixture_visual_crosscheck(mechanics, flow, repaired_raw, repaired_row)
    assert _canonical_json(repaired_normalized) == _canonical_json(baseline_normalized)


def test_visual_crosscheck_block_stale_decision_sha_target_only_repair(positive_two_boundary_normalized_case):
    baseline_row, witness_raw, render_png_raw, baseline_raw, mechanics, flow, baseline_normalized = positive_two_boundary_normalized_case
    value = _parse_crosscheck(leaves.INDEPENDENT_VISUAL_CROSSCHECK_TWO_BOUNDARY_V1)
    literal_decision_sha = value["block_checks"][0]["decision_sha256"]
    value["block_checks"][0]["decision_sha256"] = "0" * 64
    mutated_raw = _seal_crosscheck(value, keep_block_digest_index=0)
    mutated_row = _reseal_admission_row_for_crosscheck(baseline_row, mutated_raw)
    _assert_pre_normalizer_contract(row=mutated_row, witness_raw=witness_raw, render_png_raw=render_png_raw, crosscheck_raw=mutated_raw, mechanics=mechanics, flow=flow, expected_predicates={
            "fixture_pre_visual_binding_is_valid": True,
            "fixture_admission_is_valid": True,
            "fixture_admission_row_matches_derive_leaves": True,
            "visual_crosscheck_leaf_matches_admission": True,
            "visual_crosscheck_root_binding_matches": True,
            "visual_crosscheck_root_context_matches": True,
            "visual_crosscheck_reviewer_matches_contract": True,
            "visual_crosscheck_cardinality_matches": True,
            "visual_crosscheck_block_region_matches": True,
            "visual_crosscheck_block_transcription_matches": True,
            "visual_crosscheck_block_decision_matches": False,
            "visual_crosscheck_boundary_region_matches": True,
            "visual_crosscheck_boundary_decision_matches": True,
            "visual_crosscheck_inventory_matches": True,
            "visual_crosscheck_content_seal_matches": True,
        })
    with pytest.raises(RawPdfError, match="^page_proof_visual_crosscheck_invalid$"):
        page_proof._normalize_fixture_visual_crosscheck(mechanics, flow, mutated_raw, mutated_row)
    value["block_checks"][0]["decision_sha256"] = literal_decision_sha
    repaired_raw = _seal_crosscheck(value)
    repaired_row = _reseal_admission_row_for_crosscheck(baseline_row, repaired_raw)
    assert repaired_raw == baseline_raw
    _assert_pre_normalizer_contract(row=repaired_row, witness_raw=witness_raw, render_png_raw=render_png_raw, crosscheck_raw=repaired_raw, mechanics=mechanics, flow=flow, expected_predicates={
            "fixture_pre_visual_binding_is_valid": True,
            "fixture_admission_is_valid": True,
            "fixture_admission_row_matches_derive_leaves": True,
            "visual_crosscheck_leaf_matches_admission": True,
            "visual_crosscheck_root_binding_matches": True,
            "visual_crosscheck_root_context_matches": True,
            "visual_crosscheck_reviewer_matches_contract": True,
            "visual_crosscheck_cardinality_matches": True,
            "visual_crosscheck_block_region_matches": True,
            "visual_crosscheck_block_transcription_matches": True,
            "visual_crosscheck_block_decision_matches": True,
            "visual_crosscheck_boundary_region_matches": True,
            "visual_crosscheck_boundary_decision_matches": True,
            "visual_crosscheck_inventory_matches": True,
            "visual_crosscheck_content_seal_matches": True,
        })
    repaired_normalized = page_proof._normalize_fixture_visual_crosscheck(mechanics, flow, repaired_raw, repaired_row)
    assert _canonical_json(repaired_normalized) == _canonical_json(baseline_normalized)


def test_visual_crosscheck_inventory_block_digest_value_target_only_repair(positive_two_boundary_normalized_case):
    baseline_row, witness_raw, render_png_raw, baseline_raw, mechanics, flow, baseline_normalized = positive_two_boundary_normalized_case
    value = _parse_crosscheck(leaves.INDEPENDENT_VISUAL_CROSSCHECK_TWO_BOUNDARY_V1)
    value["decision_inventory"]["block_decision_sha256s"][0] = "0" * 64
    value["content_sha256"] = _sha256(_canonical_json({key: item for key, item in value.items() if key != "content_sha256"}))
    mutated_raw = _canonical_json(value)
    mutated_row = _reseal_admission_row_for_crosscheck(baseline_row, mutated_raw)
    _assert_pre_normalizer_contract(row=mutated_row, witness_raw=witness_raw, render_png_raw=render_png_raw, crosscheck_raw=mutated_raw, mechanics=mechanics, flow=flow, expected_predicates={
            "fixture_pre_visual_binding_is_valid": True,
            "fixture_admission_is_valid": True,
            "fixture_admission_row_matches_derive_leaves": True,
            "visual_crosscheck_leaf_matches_admission": True,
            "visual_crosscheck_root_binding_matches": True,
            "visual_crosscheck_root_context_matches": True,
            "visual_crosscheck_reviewer_matches_contract": True,
            "visual_crosscheck_cardinality_matches": True,
            "visual_crosscheck_block_region_matches": True,
            "visual_crosscheck_block_transcription_matches": True,
            "visual_crosscheck_block_decision_matches": True,
            "visual_crosscheck_boundary_region_matches": True,
            "visual_crosscheck_boundary_decision_matches": True,
            "visual_crosscheck_inventory_matches": False,
            "visual_crosscheck_content_seal_matches": True,
        })
    with pytest.raises(RawPdfError, match="^page_proof_visual_crosscheck_invalid$"):
        page_proof._normalize_fixture_visual_crosscheck(mechanics, flow, mutated_raw, mutated_row)
    value["decision_inventory"]["block_decision_sha256s"][0] = value["block_checks"][0]["decision_sha256"]
    value["content_sha256"] = _sha256(_canonical_json({key: item for key, item in value.items() if key != "content_sha256"}))
    repaired_raw = _canonical_json(value)
    repaired_row = _reseal_admission_row_for_crosscheck(baseline_row, repaired_raw)
    assert repaired_raw == baseline_raw
    _assert_pre_normalizer_contract(row=repaired_row, witness_raw=witness_raw, render_png_raw=render_png_raw, crosscheck_raw=repaired_raw, mechanics=mechanics, flow=flow, expected_predicates={
            "fixture_pre_visual_binding_is_valid": True,
            "fixture_admission_is_valid": True,
            "fixture_admission_row_matches_derive_leaves": True,
            "visual_crosscheck_leaf_matches_admission": True,
            "visual_crosscheck_root_binding_matches": True,
            "visual_crosscheck_root_context_matches": True,
            "visual_crosscheck_reviewer_matches_contract": True,
            "visual_crosscheck_cardinality_matches": True,
            "visual_crosscheck_block_region_matches": True,
            "visual_crosscheck_block_transcription_matches": True,
            "visual_crosscheck_block_decision_matches": True,
            "visual_crosscheck_boundary_region_matches": True,
            "visual_crosscheck_boundary_decision_matches": True,
            "visual_crosscheck_inventory_matches": True,
            "visual_crosscheck_content_seal_matches": True,
        })
    repaired_normalized = page_proof._normalize_fixture_visual_crosscheck(mechanics, flow, repaired_raw, repaired_row)
    assert _canonical_json(repaired_normalized) == _canonical_json(baseline_normalized)


def test_visual_crosscheck_inventory_block_digest_order_target_only_repair(positive_two_boundary_normalized_case):
    baseline_row, witness_raw, render_png_raw, baseline_raw, mechanics, flow, baseline_normalized = positive_two_boundary_normalized_case
    value = _parse_crosscheck(leaves.INDEPENDENT_VISUAL_CROSSCHECK_TWO_BOUNDARY_V1)
    value["decision_inventory"]["block_decision_sha256s"][0], value["decision_inventory"]["block_decision_sha256s"][1] = value["decision_inventory"]["block_decision_sha256s"][1], value["decision_inventory"]["block_decision_sha256s"][0]
    value["content_sha256"] = _sha256(_canonical_json({key: item for key, item in value.items() if key != "content_sha256"}))
    mutated_raw = _canonical_json(value)
    mutated_row = _reseal_admission_row_for_crosscheck(baseline_row, mutated_raw)
    _assert_pre_normalizer_contract(row=mutated_row, witness_raw=witness_raw, render_png_raw=render_png_raw, crosscheck_raw=mutated_raw, mechanics=mechanics, flow=flow, expected_predicates={
            "fixture_pre_visual_binding_is_valid": True,
            "fixture_admission_is_valid": True,
            "fixture_admission_row_matches_derive_leaves": True,
            "visual_crosscheck_leaf_matches_admission": True,
            "visual_crosscheck_root_binding_matches": True,
            "visual_crosscheck_root_context_matches": True,
            "visual_crosscheck_reviewer_matches_contract": True,
            "visual_crosscheck_cardinality_matches": True,
            "visual_crosscheck_block_region_matches": True,
            "visual_crosscheck_block_transcription_matches": True,
            "visual_crosscheck_block_decision_matches": True,
            "visual_crosscheck_boundary_region_matches": True,
            "visual_crosscheck_boundary_decision_matches": True,
            "visual_crosscheck_inventory_matches": False,
            "visual_crosscheck_content_seal_matches": True,
        })
    with pytest.raises(RawPdfError, match="^page_proof_visual_crosscheck_invalid$"):
        page_proof._normalize_fixture_visual_crosscheck(mechanics, flow, mutated_raw, mutated_row)
    value["decision_inventory"]["block_decision_sha256s"][0], value["decision_inventory"]["block_decision_sha256s"][1] = value["decision_inventory"]["block_decision_sha256s"][1], value["decision_inventory"]["block_decision_sha256s"][0]
    value["content_sha256"] = _sha256(_canonical_json({key: item for key, item in value.items() if key != "content_sha256"}))
    repaired_raw = _canonical_json(value)
    repaired_row = _reseal_admission_row_for_crosscheck(baseline_row, repaired_raw)
    assert repaired_raw == baseline_raw
    _assert_pre_normalizer_contract(row=repaired_row, witness_raw=witness_raw, render_png_raw=render_png_raw, crosscheck_raw=repaired_raw, mechanics=mechanics, flow=flow, expected_predicates={
            "fixture_pre_visual_binding_is_valid": True,
            "fixture_admission_is_valid": True,
            "fixture_admission_row_matches_derive_leaves": True,
            "visual_crosscheck_leaf_matches_admission": True,
            "visual_crosscheck_root_binding_matches": True,
            "visual_crosscheck_root_context_matches": True,
            "visual_crosscheck_reviewer_matches_contract": True,
            "visual_crosscheck_cardinality_matches": True,
            "visual_crosscheck_block_region_matches": True,
            "visual_crosscheck_block_transcription_matches": True,
            "visual_crosscheck_block_decision_matches": True,
            "visual_crosscheck_boundary_region_matches": True,
            "visual_crosscheck_boundary_decision_matches": True,
            "visual_crosscheck_inventory_matches": True,
            "visual_crosscheck_content_seal_matches": True,
        })
    repaired_normalized = page_proof._normalize_fixture_visual_crosscheck(mechanics, flow, repaired_raw, repaired_row)
    assert _canonical_json(repaired_normalized) == _canonical_json(baseline_normalized)


def test_visual_crosscheck_inventory_boundary_digest_value_target_only_repair(positive_two_boundary_normalized_case):
    baseline_row, witness_raw, render_png_raw, baseline_raw, mechanics, flow, baseline_normalized = positive_two_boundary_normalized_case
    value = _parse_crosscheck(leaves.INDEPENDENT_VISUAL_CROSSCHECK_TWO_BOUNDARY_V1)
    value["decision_inventory"]["boundary_decision_sha256s"][0] = "0" * 64
    value["content_sha256"] = _sha256(_canonical_json({key: item for key, item in value.items() if key != "content_sha256"}))
    mutated_raw = _canonical_json(value)
    mutated_row = _reseal_admission_row_for_crosscheck(baseline_row, mutated_raw)
    _assert_pre_normalizer_contract(row=mutated_row, witness_raw=witness_raw, render_png_raw=render_png_raw, crosscheck_raw=mutated_raw, mechanics=mechanics, flow=flow, expected_predicates={
            "fixture_pre_visual_binding_is_valid": True,
            "fixture_admission_is_valid": True,
            "fixture_admission_row_matches_derive_leaves": True,
            "visual_crosscheck_leaf_matches_admission": True,
            "visual_crosscheck_root_binding_matches": True,
            "visual_crosscheck_root_context_matches": True,
            "visual_crosscheck_reviewer_matches_contract": True,
            "visual_crosscheck_cardinality_matches": True,
            "visual_crosscheck_block_region_matches": True,
            "visual_crosscheck_block_transcription_matches": True,
            "visual_crosscheck_block_decision_matches": True,
            "visual_crosscheck_boundary_region_matches": True,
            "visual_crosscheck_boundary_decision_matches": True,
            "visual_crosscheck_inventory_matches": False,
            "visual_crosscheck_content_seal_matches": True,
        })
    with pytest.raises(RawPdfError, match="^page_proof_visual_crosscheck_invalid$"):
        page_proof._normalize_fixture_visual_crosscheck(mechanics, flow, mutated_raw, mutated_row)
    value["decision_inventory"]["boundary_decision_sha256s"][0] = value["boundary_checks"][0]["decision_sha256"]
    value["content_sha256"] = _sha256(_canonical_json({key: item for key, item in value.items() if key != "content_sha256"}))
    repaired_raw = _canonical_json(value)
    repaired_row = _reseal_admission_row_for_crosscheck(baseline_row, repaired_raw)
    assert repaired_raw == baseline_raw
    _assert_pre_normalizer_contract(row=repaired_row, witness_raw=witness_raw, render_png_raw=render_png_raw, crosscheck_raw=repaired_raw, mechanics=mechanics, flow=flow, expected_predicates={
            "fixture_pre_visual_binding_is_valid": True,
            "fixture_admission_is_valid": True,
            "fixture_admission_row_matches_derive_leaves": True,
            "visual_crosscheck_leaf_matches_admission": True,
            "visual_crosscheck_root_binding_matches": True,
            "visual_crosscheck_root_context_matches": True,
            "visual_crosscheck_reviewer_matches_contract": True,
            "visual_crosscheck_cardinality_matches": True,
            "visual_crosscheck_block_region_matches": True,
            "visual_crosscheck_block_transcription_matches": True,
            "visual_crosscheck_block_decision_matches": True,
            "visual_crosscheck_boundary_region_matches": True,
            "visual_crosscheck_boundary_decision_matches": True,
            "visual_crosscheck_inventory_matches": True,
            "visual_crosscheck_content_seal_matches": True,
        })
    repaired_normalized = page_proof._normalize_fixture_visual_crosscheck(mechanics, flow, repaired_raw, repaired_row)
    assert _canonical_json(repaired_normalized) == _canonical_json(baseline_normalized)


def test_visual_crosscheck_inventory_boundary_digest_order_target_only_repair(positive_two_boundary_normalized_case):
    baseline_row, witness_raw, render_png_raw, baseline_raw, mechanics, flow, baseline_normalized = positive_two_boundary_normalized_case
    value = _parse_crosscheck(leaves.INDEPENDENT_VISUAL_CROSSCHECK_TWO_BOUNDARY_V1)
    value["decision_inventory"]["boundary_decision_sha256s"][0], value["decision_inventory"]["boundary_decision_sha256s"][1] = value["decision_inventory"]["boundary_decision_sha256s"][1], value["decision_inventory"]["boundary_decision_sha256s"][0]
    value["content_sha256"] = _sha256(_canonical_json({key: item for key, item in value.items() if key != "content_sha256"}))
    mutated_raw = _canonical_json(value)
    mutated_row = _reseal_admission_row_for_crosscheck(baseline_row, mutated_raw)
    _assert_pre_normalizer_contract(row=mutated_row, witness_raw=witness_raw, render_png_raw=render_png_raw, crosscheck_raw=mutated_raw, mechanics=mechanics, flow=flow, expected_predicates={
            "fixture_pre_visual_binding_is_valid": True,
            "fixture_admission_is_valid": True,
            "fixture_admission_row_matches_derive_leaves": True,
            "visual_crosscheck_leaf_matches_admission": True,
            "visual_crosscheck_root_binding_matches": True,
            "visual_crosscheck_root_context_matches": True,
            "visual_crosscheck_reviewer_matches_contract": True,
            "visual_crosscheck_cardinality_matches": True,
            "visual_crosscheck_block_region_matches": True,
            "visual_crosscheck_block_transcription_matches": True,
            "visual_crosscheck_block_decision_matches": True,
            "visual_crosscheck_boundary_region_matches": True,
            "visual_crosscheck_boundary_decision_matches": True,
            "visual_crosscheck_inventory_matches": False,
            "visual_crosscheck_content_seal_matches": True,
        })
    with pytest.raises(RawPdfError, match="^page_proof_visual_crosscheck_invalid$"):
        page_proof._normalize_fixture_visual_crosscheck(mechanics, flow, mutated_raw, mutated_row)
    value["decision_inventory"]["boundary_decision_sha256s"][0], value["decision_inventory"]["boundary_decision_sha256s"][1] = value["decision_inventory"]["boundary_decision_sha256s"][1], value["decision_inventory"]["boundary_decision_sha256s"][0]
    value["content_sha256"] = _sha256(_canonical_json({key: item for key, item in value.items() if key != "content_sha256"}))
    repaired_raw = _canonical_json(value)
    repaired_row = _reseal_admission_row_for_crosscheck(baseline_row, repaired_raw)
    assert repaired_raw == baseline_raw
    _assert_pre_normalizer_contract(row=repaired_row, witness_raw=witness_raw, render_png_raw=render_png_raw, crosscheck_raw=repaired_raw, mechanics=mechanics, flow=flow, expected_predicates={
            "fixture_pre_visual_binding_is_valid": True,
            "fixture_admission_is_valid": True,
            "fixture_admission_row_matches_derive_leaves": True,
            "visual_crosscheck_leaf_matches_admission": True,
            "visual_crosscheck_root_binding_matches": True,
            "visual_crosscheck_root_context_matches": True,
            "visual_crosscheck_reviewer_matches_contract": True,
            "visual_crosscheck_cardinality_matches": True,
            "visual_crosscheck_block_region_matches": True,
            "visual_crosscheck_block_transcription_matches": True,
            "visual_crosscheck_block_decision_matches": True,
            "visual_crosscheck_boundary_region_matches": True,
            "visual_crosscheck_boundary_decision_matches": True,
            "visual_crosscheck_inventory_matches": True,
            "visual_crosscheck_content_seal_matches": True,
        })
    repaired_normalized = page_proof._normalize_fixture_visual_crosscheck(mechanics, flow, repaired_raw, repaired_row)
    assert _canonical_json(repaired_normalized) == _canonical_json(baseline_normalized)


def test_visual_crosscheck_inventory_block_count_target_only_repair(positive_two_boundary_normalized_case):
    baseline_row, witness_raw, render_png_raw, baseline_raw, mechanics, flow, baseline_normalized = positive_two_boundary_normalized_case
    value = _parse_crosscheck(leaves.INDEPENDENT_VISUAL_CROSSCHECK_TWO_BOUNDARY_V1)
    value["decision_inventory"]["confirmed_block_count"] = 3
    value["content_sha256"] = _sha256(_canonical_json({key: item for key, item in value.items() if key != "content_sha256"}))
    mutated_raw = _canonical_json(value)
    mutated_row = _reseal_admission_row_for_crosscheck(baseline_row, mutated_raw)
    _assert_pre_normalizer_contract(row=mutated_row, witness_raw=witness_raw, render_png_raw=render_png_raw, crosscheck_raw=mutated_raw, mechanics=mechanics, flow=flow, expected_predicates={
            "fixture_pre_visual_binding_is_valid": True,
            "fixture_admission_is_valid": True,
            "fixture_admission_row_matches_derive_leaves": True,
            "visual_crosscheck_leaf_matches_admission": True,
            "visual_crosscheck_root_binding_matches": True,
            "visual_crosscheck_root_context_matches": True,
            "visual_crosscheck_reviewer_matches_contract": True,
            "visual_crosscheck_cardinality_matches": True,
            "visual_crosscheck_block_region_matches": True,
            "visual_crosscheck_block_transcription_matches": True,
            "visual_crosscheck_block_decision_matches": True,
            "visual_crosscheck_boundary_region_matches": True,
            "visual_crosscheck_boundary_decision_matches": True,
            "visual_crosscheck_inventory_matches": False,
            "visual_crosscheck_content_seal_matches": True,
        })
    with pytest.raises(RawPdfError, match="^page_proof_visual_crosscheck_invalid$"):
        page_proof._normalize_fixture_visual_crosscheck(mechanics, flow, mutated_raw, mutated_row)
    value["decision_inventory"]["confirmed_block_count"] = len(value["block_checks"])
    value["content_sha256"] = _sha256(_canonical_json({key: item for key, item in value.items() if key != "content_sha256"}))
    repaired_raw = _canonical_json(value)
    repaired_row = _reseal_admission_row_for_crosscheck(baseline_row, repaired_raw)
    assert repaired_raw == baseline_raw
    _assert_pre_normalizer_contract(row=repaired_row, witness_raw=witness_raw, render_png_raw=render_png_raw, crosscheck_raw=repaired_raw, mechanics=mechanics, flow=flow, expected_predicates={
            "fixture_pre_visual_binding_is_valid": True,
            "fixture_admission_is_valid": True,
            "fixture_admission_row_matches_derive_leaves": True,
            "visual_crosscheck_leaf_matches_admission": True,
            "visual_crosscheck_root_binding_matches": True,
            "visual_crosscheck_root_context_matches": True,
            "visual_crosscheck_reviewer_matches_contract": True,
            "visual_crosscheck_cardinality_matches": True,
            "visual_crosscheck_block_region_matches": True,
            "visual_crosscheck_block_transcription_matches": True,
            "visual_crosscheck_block_decision_matches": True,
            "visual_crosscheck_boundary_region_matches": True,
            "visual_crosscheck_boundary_decision_matches": True,
            "visual_crosscheck_inventory_matches": True,
            "visual_crosscheck_content_seal_matches": True,
        })
    repaired_normalized = page_proof._normalize_fixture_visual_crosscheck(mechanics, flow, repaired_raw, repaired_row)
    assert _canonical_json(repaired_normalized) == _canonical_json(baseline_normalized)


def test_visual_crosscheck_inventory_boundary_count_target_only_repair(positive_two_boundary_normalized_case):
    baseline_row, witness_raw, render_png_raw, baseline_raw, mechanics, flow, baseline_normalized = positive_two_boundary_normalized_case
    value = _parse_crosscheck(leaves.INDEPENDENT_VISUAL_CROSSCHECK_TWO_BOUNDARY_V1)
    value["decision_inventory"]["confirmed_boundary_count"] = 3
    value["content_sha256"] = _sha256(_canonical_json({key: item for key, item in value.items() if key != "content_sha256"}))
    mutated_raw = _canonical_json(value)
    mutated_row = _reseal_admission_row_for_crosscheck(baseline_row, mutated_raw)
    _assert_pre_normalizer_contract(row=mutated_row, witness_raw=witness_raw, render_png_raw=render_png_raw, crosscheck_raw=mutated_raw, mechanics=mechanics, flow=flow, expected_predicates={
            "fixture_pre_visual_binding_is_valid": True,
            "fixture_admission_is_valid": True,
            "fixture_admission_row_matches_derive_leaves": True,
            "visual_crosscheck_leaf_matches_admission": True,
            "visual_crosscheck_root_binding_matches": True,
            "visual_crosscheck_root_context_matches": True,
            "visual_crosscheck_reviewer_matches_contract": True,
            "visual_crosscheck_cardinality_matches": True,
            "visual_crosscheck_block_region_matches": True,
            "visual_crosscheck_block_transcription_matches": True,
            "visual_crosscheck_block_decision_matches": True,
            "visual_crosscheck_boundary_region_matches": True,
            "visual_crosscheck_boundary_decision_matches": True,
            "visual_crosscheck_inventory_matches": False,
            "visual_crosscheck_content_seal_matches": True,
        })
    with pytest.raises(RawPdfError, match="^page_proof_visual_crosscheck_invalid$"):
        page_proof._normalize_fixture_visual_crosscheck(mechanics, flow, mutated_raw, mutated_row)
    value["decision_inventory"]["confirmed_boundary_count"] = len(value["boundary_checks"])
    value["content_sha256"] = _sha256(_canonical_json({key: item for key, item in value.items() if key != "content_sha256"}))
    repaired_raw = _canonical_json(value)
    repaired_row = _reseal_admission_row_for_crosscheck(baseline_row, repaired_raw)
    assert repaired_raw == baseline_raw
    _assert_pre_normalizer_contract(row=repaired_row, witness_raw=witness_raw, render_png_raw=render_png_raw, crosscheck_raw=repaired_raw, mechanics=mechanics, flow=flow, expected_predicates={
            "fixture_pre_visual_binding_is_valid": True,
            "fixture_admission_is_valid": True,
            "fixture_admission_row_matches_derive_leaves": True,
            "visual_crosscheck_leaf_matches_admission": True,
            "visual_crosscheck_root_binding_matches": True,
            "visual_crosscheck_root_context_matches": True,
            "visual_crosscheck_reviewer_matches_contract": True,
            "visual_crosscheck_cardinality_matches": True,
            "visual_crosscheck_block_region_matches": True,
            "visual_crosscheck_block_transcription_matches": True,
            "visual_crosscheck_block_decision_matches": True,
            "visual_crosscheck_boundary_region_matches": True,
            "visual_crosscheck_boundary_decision_matches": True,
            "visual_crosscheck_inventory_matches": True,
            "visual_crosscheck_content_seal_matches": True,
        })
    repaired_normalized = page_proof._normalize_fixture_visual_crosscheck(mechanics, flow, repaired_raw, repaired_row)
    assert _canonical_json(repaired_normalized) == _canonical_json(baseline_normalized)


def test_visual_crosscheck_inventory_stale_sha_target_only_repair(positive_two_boundary_normalized_case):
    baseline_row, witness_raw, render_png_raw, baseline_raw, mechanics, flow, baseline_normalized = positive_two_boundary_normalized_case
    value = _parse_crosscheck(leaves.INDEPENDENT_VISUAL_CROSSCHECK_TWO_BOUNDARY_V1)
    value["decision_inventory"]["inventory_sha256"] = "0" * 64
    value["content_sha256"] = _sha256(_canonical_json({key: item for key, item in value.items() if key != "content_sha256"}))
    mutated_raw = _canonical_json(value)
    mutated_row = _reseal_admission_row_for_crosscheck(baseline_row, mutated_raw)
    _assert_pre_normalizer_contract(row=mutated_row, witness_raw=witness_raw, render_png_raw=render_png_raw, crosscheck_raw=mutated_raw, mechanics=mechanics, flow=flow, expected_predicates={
            "fixture_pre_visual_binding_is_valid": True,
            "fixture_admission_is_valid": True,
            "fixture_admission_row_matches_derive_leaves": True,
            "visual_crosscheck_leaf_matches_admission": True,
            "visual_crosscheck_root_binding_matches": True,
            "visual_crosscheck_root_context_matches": True,
            "visual_crosscheck_reviewer_matches_contract": True,
            "visual_crosscheck_cardinality_matches": True,
            "visual_crosscheck_block_region_matches": True,
            "visual_crosscheck_block_transcription_matches": True,
            "visual_crosscheck_block_decision_matches": True,
            "visual_crosscheck_boundary_region_matches": True,
            "visual_crosscheck_boundary_decision_matches": True,
            "visual_crosscheck_inventory_matches": False,
            "visual_crosscheck_content_seal_matches": True,
        })
    with pytest.raises(RawPdfError, match="^page_proof_visual_crosscheck_invalid$"):
        page_proof._normalize_fixture_visual_crosscheck(mechanics, flow, mutated_raw, mutated_row)
    value["decision_inventory"]["inventory_sha256"] = _inventory_sha(tuple(value["decision_inventory"]["block_decision_sha256s"]), tuple(value["decision_inventory"]["boundary_decision_sha256s"]))
    value["content_sha256"] = _sha256(_canonical_json({key: item for key, item in value.items() if key != "content_sha256"}))
    repaired_raw = _canonical_json(value)
    repaired_row = _reseal_admission_row_for_crosscheck(baseline_row, repaired_raw)
    assert repaired_raw == baseline_raw
    _assert_pre_normalizer_contract(row=repaired_row, witness_raw=witness_raw, render_png_raw=render_png_raw, crosscheck_raw=repaired_raw, mechanics=mechanics, flow=flow, expected_predicates={
            "fixture_pre_visual_binding_is_valid": True,
            "fixture_admission_is_valid": True,
            "fixture_admission_row_matches_derive_leaves": True,
            "visual_crosscheck_leaf_matches_admission": True,
            "visual_crosscheck_root_binding_matches": True,
            "visual_crosscheck_root_context_matches": True,
            "visual_crosscheck_reviewer_matches_contract": True,
            "visual_crosscheck_cardinality_matches": True,
            "visual_crosscheck_block_region_matches": True,
            "visual_crosscheck_block_transcription_matches": True,
            "visual_crosscheck_block_decision_matches": True,
            "visual_crosscheck_boundary_region_matches": True,
            "visual_crosscheck_boundary_decision_matches": True,
            "visual_crosscheck_inventory_matches": True,
            "visual_crosscheck_content_seal_matches": True,
        })
    repaired_normalized = page_proof._normalize_fixture_visual_crosscheck(mechanics, flow, repaired_raw, repaired_row)
    assert _canonical_json(repaired_normalized) == _canonical_json(baseline_normalized)


def test_visual_crosscheck_outer_changed_v_with_unchanged_valid_row_rejected():
    row, _, _, raw, mechanics, flow = _two_boundary_case()
    changed_raw = raw + b" "
    assert not page_proof._visual_crosscheck_leaf_matches_admission(changed_raw, row)
    with pytest.raises(RawPdfError, match="^page_proof_visual_crosscheck_invalid$"):
        page_proof._normalize_fixture_visual_crosscheck(mechanics, flow, changed_raw, row)


def test_visual_crosscheck_outer_changed_row_v_metadata_without_recomputed_f_rejected():
    row, _, _, raw, mechanics, flow = _two_boundary_case()
    stale_row = dataclasses.replace(row, independent_visual_crosscheck_byte_length=row.independent_visual_crosscheck_byte_length + 1)
    assert not page_proof._fixture_admission_is_valid(stale_row)
    with pytest.raises(RawPdfError, match="^page_proof_visual_crosscheck_invalid$"):
        page_proof._normalize_fixture_visual_crosscheck(mechanics, flow, raw, stale_row)


def test_two_boundary_leaf_assignments_are_direct_literals():
    assert leaves.TWO_BOUNDARY_V1_LENGTHS == (33, 3186, 119, 2928)
    assert leaves.TWO_BOUNDARY_PRE_VISUAL_BINDING_SHA256 == "cdb993a29ef0b05229a9a9c5dfd65dd30977df9c3ec1c295a88a94b5ea1f9c1d"
    assert leaves.TWO_BOUNDARY_FINAL_BINDING_SHA256 == "afd101e900a5242cf0c7867102272997e719ea3f183c5e096d0e5c1c826c522e"


def test_visual_crosscheck_normalizer_call_layout_is_literal_and_complete():
    tree = ast.parse(inspect.getsource(inspect.getmodule(test_visual_crosscheck_normalizer_call_layout_is_literal_and_complete)))
    parents = {child: parent for parent in ast.walk(tree) for child in ast.iter_child_nodes(parent)}
    expected_counts = {
        "positive_two_column_normalized_case": 1,
        "positive_nested_form_normalized_case": 1,
        "positive_visual_only_normalized_case": 1,
        "positive_two_boundary_normalized_case": 1,
        "test_visual_crosscheck_root_pre_visual_binding_target_only_repair": 2,
        "test_visual_crosscheck_root_topology_target_only_repair": 2,
        "test_visual_crosscheck_root_pre_visual_core_target_only_repair": 2,
        "test_visual_crosscheck_reviewer_identity_target_only_repair": 2,
        "test_visual_crosscheck_reviewer_scope_target_only_repair": 2,
        "test_visual_crosscheck_reviewer_independence_target_only_repair": 2,
        "test_visual_crosscheck_root_content_seal_target_only_repair": 2,
        "test_visual_crosscheck_boundary_missing_final_row_target_only_repair": 2,
        "test_visual_crosscheck_boundary_duplicate_final_row_target_only_repair": 2,
        "test_visual_crosscheck_boundary_reordered_rows_target_only_repair": 2,
        "test_visual_crosscheck_boundary_aggregate_f0_f2_target_only_repair": 2,
        "test_visual_crosscheck_boundary_source_fragment_target_only_repair": 2,
        "test_visual_crosscheck_boundary_target_fragment_target_only_repair": 2,
        "test_visual_crosscheck_boundary_kind_target_only_repair": 2,
        "test_visual_crosscheck_boundary_source_block_target_only_repair": 2,
        "test_visual_crosscheck_boundary_target_block_target_only_repair": 2,
        "test_visual_crosscheck_boundary_source_column_target_only_repair": 2,
        "test_visual_crosscheck_boundary_target_column_target_only_repair": 2,
        "test_visual_crosscheck_boundary_bbox_target_only_repair": 2,
        "test_visual_crosscheck_boundary_nonconfirm_target_only_repair": 2,
        "test_visual_crosscheck_boundary_wrong_reason_target_only_repair": 2,
        "test_visual_crosscheck_boundary_stale_decision_sha_target_only_repair": 2,
        "test_visual_crosscheck_block_missing_final_row_target_only_repair": 2,
        "test_visual_crosscheck_block_duplicate_final_row_target_only_repair": 2,
        "test_visual_crosscheck_block_reordered_rows_target_only_repair": 2,
        "test_visual_crosscheck_block_id_target_only_repair": 2,
        "test_visual_crosscheck_block_ordinal_target_only_repair": 2,
        "test_visual_crosscheck_block_disposition_target_only_repair": 2,
        "test_visual_crosscheck_block_reason_target_only_repair": 2,
        "test_visual_crosscheck_block_column_target_only_repair": 2,
        "test_visual_crosscheck_block_bbox_target_only_repair": 2,
        "test_visual_crosscheck_block_pixel_count_target_only_repair": 2,
        "test_visual_crosscheck_block_component_evidence_target_only_repair": 2,
        "test_visual_crosscheck_transcription_empty_bytes_target_only_repair": 2,
        "test_visual_crosscheck_transcription_changed_bytes_old_hash_target_only_repair": 2,
        "test_visual_crosscheck_transcription_wrong_hash_target_only_repair": 2,
        "test_visual_crosscheck_block_nonconfirm_target_only_repair": 2,
        "test_visual_crosscheck_block_wrong_reason_target_only_repair": 2,
        "test_visual_crosscheck_block_stale_decision_sha_target_only_repair": 2,
        "test_visual_crosscheck_inventory_block_digest_value_target_only_repair": 2,
        "test_visual_crosscheck_inventory_block_digest_order_target_only_repair": 2,
        "test_visual_crosscheck_inventory_boundary_digest_value_target_only_repair": 2,
        "test_visual_crosscheck_inventory_boundary_digest_order_target_only_repair": 2,
        "test_visual_crosscheck_inventory_block_count_target_only_repair": 2,
        "test_visual_crosscheck_inventory_boundary_count_target_only_repair": 2,
        "test_visual_crosscheck_inventory_stale_sha_target_only_repair": 2,
        "test_visual_crosscheck_outer_changed_v_with_unchanged_valid_row_rejected": 1,
        "test_visual_crosscheck_outer_changed_row_v_metadata_without_recomputed_f_rejected": 1,
    }
    expected_false_keys = {
        "test_visual_crosscheck_root_pre_visual_binding_target_only_repair": "visual_crosscheck_root_binding_matches",
        "test_visual_crosscheck_root_topology_target_only_repair": "visual_crosscheck_root_context_matches",
        "test_visual_crosscheck_root_pre_visual_core_target_only_repair": "visual_crosscheck_root_context_matches",
        "test_visual_crosscheck_reviewer_identity_target_only_repair": "visual_crosscheck_reviewer_matches_contract",
        "test_visual_crosscheck_reviewer_scope_target_only_repair": "visual_crosscheck_reviewer_matches_contract",
        "test_visual_crosscheck_reviewer_independence_target_only_repair": "visual_crosscheck_reviewer_matches_contract",
        "test_visual_crosscheck_root_content_seal_target_only_repair": "visual_crosscheck_content_seal_matches",
        "test_visual_crosscheck_boundary_missing_final_row_target_only_repair": "visual_crosscheck_cardinality_matches",
        "test_visual_crosscheck_boundary_duplicate_final_row_target_only_repair": "visual_crosscheck_cardinality_matches",
        "test_visual_crosscheck_boundary_reordered_rows_target_only_repair": "visual_crosscheck_boundary_region_matches",
        "test_visual_crosscheck_boundary_aggregate_f0_f2_target_only_repair": "visual_crosscheck_boundary_region_matches",
        "test_visual_crosscheck_boundary_source_fragment_target_only_repair": "visual_crosscheck_boundary_region_matches",
        "test_visual_crosscheck_boundary_target_fragment_target_only_repair": "visual_crosscheck_boundary_region_matches",
        "test_visual_crosscheck_boundary_kind_target_only_repair": "visual_crosscheck_boundary_region_matches",
        "test_visual_crosscheck_boundary_source_block_target_only_repair": "visual_crosscheck_boundary_region_matches",
        "test_visual_crosscheck_boundary_target_block_target_only_repair": "visual_crosscheck_boundary_region_matches",
        "test_visual_crosscheck_boundary_source_column_target_only_repair": "visual_crosscheck_boundary_region_matches",
        "test_visual_crosscheck_boundary_target_column_target_only_repair": "visual_crosscheck_boundary_region_matches",
        "test_visual_crosscheck_boundary_bbox_target_only_repair": "visual_crosscheck_boundary_region_matches",
        "test_visual_crosscheck_boundary_nonconfirm_target_only_repair": "visual_crosscheck_boundary_decision_matches",
        "test_visual_crosscheck_boundary_wrong_reason_target_only_repair": "visual_crosscheck_boundary_decision_matches",
        "test_visual_crosscheck_boundary_stale_decision_sha_target_only_repair": "visual_crosscheck_boundary_decision_matches",
        "test_visual_crosscheck_block_missing_final_row_target_only_repair": "visual_crosscheck_cardinality_matches",
        "test_visual_crosscheck_block_duplicate_final_row_target_only_repair": "visual_crosscheck_cardinality_matches",
        "test_visual_crosscheck_block_reordered_rows_target_only_repair": "visual_crosscheck_block_region_matches",
        "test_visual_crosscheck_block_id_target_only_repair": "visual_crosscheck_block_region_matches",
        "test_visual_crosscheck_block_ordinal_target_only_repair": "visual_crosscheck_block_region_matches",
        "test_visual_crosscheck_block_disposition_target_only_repair": "visual_crosscheck_block_region_matches",
        "test_visual_crosscheck_block_reason_target_only_repair": "visual_crosscheck_block_region_matches",
        "test_visual_crosscheck_block_column_target_only_repair": "visual_crosscheck_block_region_matches",
        "test_visual_crosscheck_block_bbox_target_only_repair": "visual_crosscheck_block_region_matches",
        "test_visual_crosscheck_block_pixel_count_target_only_repair": "visual_crosscheck_block_region_matches",
        "test_visual_crosscheck_block_component_evidence_target_only_repair": "visual_crosscheck_block_region_matches",
        "test_visual_crosscheck_transcription_empty_bytes_target_only_repair": "visual_crosscheck_block_transcription_matches",
        "test_visual_crosscheck_transcription_changed_bytes_old_hash_target_only_repair": "visual_crosscheck_block_transcription_matches",
        "test_visual_crosscheck_transcription_wrong_hash_target_only_repair": "visual_crosscheck_block_transcription_matches",
        "test_visual_crosscheck_block_nonconfirm_target_only_repair": "visual_crosscheck_block_decision_matches",
        "test_visual_crosscheck_block_wrong_reason_target_only_repair": "visual_crosscheck_block_decision_matches",
        "test_visual_crosscheck_block_stale_decision_sha_target_only_repair": "visual_crosscheck_block_decision_matches",
        "test_visual_crosscheck_inventory_block_digest_value_target_only_repair": "visual_crosscheck_inventory_matches",
        "test_visual_crosscheck_inventory_block_digest_order_target_only_repair": "visual_crosscheck_inventory_matches",
        "test_visual_crosscheck_inventory_boundary_digest_value_target_only_repair": "visual_crosscheck_inventory_matches",
        "test_visual_crosscheck_inventory_boundary_digest_order_target_only_repair": "visual_crosscheck_inventory_matches",
        "test_visual_crosscheck_inventory_block_count_target_only_repair": "visual_crosscheck_inventory_matches",
        "test_visual_crosscheck_inventory_boundary_count_target_only_repair": "visual_crosscheck_inventory_matches",
        "test_visual_crosscheck_inventory_stale_sha_target_only_repair": "visual_crosscheck_inventory_matches",
    }
    calls = [node for node in ast.walk(tree) if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) and isinstance(node.func.value, ast.Name) and node.func.value.id == "page_proof" and node.func.attr == "_normalize_fixture_visual_crosscheck"]
    assert len(calls) == 98
    functions = {node.name: node for node in tree.body if isinstance(node, ast.FunctionDef)}
    counts = {name: 0 for name in expected_counts}
    for call in calls:
        function = call
        while not isinstance(function, ast.FunctionDef):
            function = parents[function]
        assert function.name in counts
        counts[function.name] += 1
    assert counts == expected_counts
    for name, count in expected_counts.items():
        statements = functions[name].body
        positions = [(index, next(node for node in ast.walk(statement) if node in calls)) for index, statement in enumerate(statements) if any(node in calls for node in ast.walk(statement))]
        if name.startswith("test_visual_crosscheck_outer"):
            assert len(positions) == 1
            continue
        assert len(positions) == count
        vectors = []
        for index, call in positions:
            assert index > 0 and isinstance(statements[index - 1], ast.Expr)
            guard = statements[index - 1].value
            assert isinstance(guard, ast.Call) and isinstance(guard.func, ast.Name) and guard.func.id == "_assert_pre_normalizer_contract"
            words = {word.arg: word.value for word in guard.keywords}
            assert [ast.dump(item, include_attributes=False) for item in call.args] == [ast.dump(words[key], include_attributes=False) for key in ("mechanics", "flow", "crosscheck_raw", "row")]
            literal = words["expected_predicates"]
            assert isinstance(literal, ast.Dict) and len(literal.keys) == 15
            assert [key.value for key in literal.keys] == list(_PREDICATE_KEYS)
            assert all(type(value.value) is bool for value in literal.values)
            vectors.append(next((key.value for key, value in zip(literal.keys, literal.values) if value.value is False), None))
        assert vectors == ([None] if name.startswith("positive_") else [expected_false_keys[name], None])
    assert len([node for node in ast.walk(tree) if isinstance(node, ast.Expr) and isinstance(node.value, ast.Call) and isinstance(node.value.func, ast.Name) and node.value.func.id == "_assert_pre_normalizer_contract"]) == 96


def test_binding_helper_ast_containment_and_closed_roots_exclude_final_binding():
    tree = ast.parse(inspect.getsource(page_proof))
    helper_names = ("_fixture_pre_visual_binding_payload", "_fixture_pre_visual_binding_sha256", "_fixture_pre_visual_binding_is_valid", "_fixture_admission_payload", "_fixture_admission_binding_sha256", "_fixture_admission_is_valid")
    functions = {node.name: node for node in tree.body if isinstance(node, ast.FunctionDef)}
    selected = {name: functions[name] for name in helper_names}
    assert tuple(selected) == helper_names
    edges = {
        "_fixture_pre_visual_binding_payload": set(),
        "_fixture_pre_visual_binding_sha256": {"_fixture_pre_visual_binding_payload"},
        "_fixture_pre_visual_binding_is_valid": {"_fixture_pre_visual_binding_sha256"},
        "_fixture_admission_payload": {"_fixture_pre_visual_binding_payload"},
        "_fixture_admission_binding_sha256": {"_fixture_admission_payload"},
        "_fixture_admission_is_valid": {"_fixture_pre_visual_binding_is_valid", "_fixture_admission_binding_sha256"},
    }
    name_calls = {
        "_fixture_pre_visual_binding_payload": set(),
        "_fixture_pre_visual_binding_sha256": {"_sha256", "_canonical_json", "_fixture_pre_visual_binding_payload"},
        "_fixture_pre_visual_binding_is_valid": {"type", "bool", "_fixture_pre_visual_binding_sha256"},
        "_fixture_admission_payload": {"_fixture_pre_visual_binding_payload"},
        "_fixture_admission_binding_sha256": {"_sha256", "_canonical_json", "_fixture_admission_payload"},
        "_fixture_admission_is_valid": {"type", "len", "all", "_sha256", "_fixture_pre_visual_binding_is_valid", "_fixture_admission_binding_sha256"},
    }
    attribute_calls = {
        "_fixture_pre_visual_binding_payload": {"row.fixture_id.decode"},
        "_fixture_pre_visual_binding_sha256": set(),
        "_fixture_pre_visual_binding_is_valid": {"_HEX.fullmatch"},
        "_fixture_admission_payload": {"value.update"},
        "_fixture_admission_binding_sha256": set(),
        "_fixture_admission_is_valid": {"row.fixture_id.decode", "_HEX.fullmatch"},
    }
    private_names = {
        "_fixture_pre_visual_binding_payload": {"_WITNESS_SCHEMA", "_VISUAL_CROSSCHECK_SCHEMA"},
        "_fixture_pre_visual_binding_sha256": {"_sha256", "_canonical_json", "_fixture_pre_visual_binding_payload"},
        "_fixture_pre_visual_binding_is_valid": {"_FixtureAdmission", "_HEX", "_fixture_pre_visual_binding_sha256"},
        "_fixture_admission_payload": {"_fixture_pre_visual_binding_payload"},
        "_fixture_admission_binding_sha256": {"_sha256", "_canonical_json", "_fixture_admission_payload"},
        "_fixture_admission_is_valid": {"_FixtureAdmission", "_HEX", "_sha256", "_fixture_pre_visual_binding_is_valid", "_fixture_admission_binding_sha256"},
    }

    def attribute_name(attribute: ast.Attribute) -> str:
        parts, value = [attribute.attr], attribute.value
        while isinstance(value, ast.Attribute):
            parts.append(value.attr)
            value = value.value
        assert isinstance(value, ast.Name)
        return ".".join([value.id, *reversed(parts)])

    direct_fields = {}
    for name, function in selected.items():
        body = ast.Module(body=function.body, type_ignores=[])
        actual_name_calls = {node.func.id for node in ast.walk(function) if isinstance(node, ast.Call) and isinstance(node.func, ast.Name)}
        actual_attribute_calls = {attribute_name(node.func) for node in ast.walk(function) if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)}
        actual_private_names = {node.id for node in ast.walk(body) if isinstance(node, ast.Name) and node.id.startswith("_")}
        assert actual_name_calls == name_calls[name]
        assert actual_attribute_calls == attribute_calls[name]
        assert actual_private_names == private_names[name]
        assert actual_name_calls & set(helper_names) == edges[name]
        direct_fields[name] = {node.attr for node in ast.walk(function) if isinstance(node, ast.Attribute) and isinstance(node.value, ast.Name) and node.value.id == "row"}

    p_fields = {"fixture_id", "fixture_id_byte_length", "fixture_id_sha256", "stage_a_fixture_id", "stage_a_authority_content_sha256", "required_topology_inventory_content_sha256", "render_png_byte_length", "render_png_sha256"}
    f_fields = {"pre_visual_binding_sha256", "witness_byte_length", "witness_sha256", "independent_visual_crosscheck_byte_length", "independent_visual_crosscheck_sha256"}
    payload_edges = {"_fixture_pre_visual_binding_payload": set(), "_fixture_admission_payload": {"_fixture_pre_visual_binding_payload"}}

    def closure(root: str) -> set[str]:
        pending, result = [root], set()
        while pending:
            name = pending.pop()
            if name not in result:
                result.add(name)
                pending.extend(payload_edges[name])
        return result

    assert set().union(*(direct_fields[name] for name in closure("_fixture_pre_visual_binding_payload"))) == p_fields
    assert set().union(*(direct_fields[name] for name in closure("_fixture_admission_payload"))) == p_fields | f_fields
    row, _, _, _, _, _ = _two_boundary_case()
    assert set(page_proof._fixture_pre_visual_binding_payload(row)) == {"fixture_id", "fixture_id_byte_length", "fixture_id_sha256", "stage_a_fixture_id", "stage_a_authority_content_sha256", "required_topology_inventory_content_sha256", "render_png_byte_length", "render_png_sha256", "witness_schema", "visual_crosscheck_schema"}
    assert set(page_proof._fixture_admission_payload(row)) == {"fixture_id", "fixture_id_byte_length", "fixture_id_sha256", "stage_a_fixture_id", "stage_a_authority_content_sha256", "required_topology_inventory_content_sha256", "render_png_byte_length", "render_png_sha256", "witness_schema", "visual_crosscheck_schema", "pre_visual_binding_sha256", "witness_byte_length", "witness_sha256", "independent_visual_crosscheck_byte_length", "independent_visual_crosscheck_sha256"}
    assert {node.value for node in ast.walk(selected["_fixture_pre_visual_binding_sha256"]) if isinstance(node, ast.Constant) and isinstance(node.value, bytes)} == {b"page-proof.fixture-pre-visual-binding.v1\0"}
    assert {node.value for node in ast.walk(selected["_fixture_admission_binding_sha256"]) if isinstance(node, ast.Constant) and isinstance(node.value, bytes)} == {b"page-proof.fixture-admission.v2\0"}

    payload_hash_helpers = ("_fixture_pre_visual_binding_payload", "_fixture_pre_visual_binding_sha256", "_fixture_admission_payload", "_fixture_admission_binding_sha256")
    prohibited_nodes = (ast.For, ast.AsyncFor, ast.While, ast.ListComp, ast.SetComp, ast.DictComp, ast.GeneratorExp, ast.Lambda, ast.Starred, ast.Import, ast.ImportFrom)
    prohibited_names = {"getattr", "setattr", "vars", "dir", "globals", "locals", "eval", "exec", "__import__", "importlib", "open", "Path", "pathlib", "os", "environ", "_normalize_fixture_visual_crosscheck", "_PRODUCTION_FIXTURE_ADMISSION", "_EXPECTED_PAGE_PROOF_FIXTURE_IDS", "_visual_crosscheck_block_region_matches", "_visual_crosscheck_block_transcription_matches", "_visual_crosscheck_block_decision_matches", "_visual_crosscheck_boundary_region_matches", "_visual_crosscheck_boundary_decision_matches", "_visual_crosscheck_inventory_matches", "_visual_crosscheck_content_seal_matches"}
    for name in payload_hash_helpers:
        function = selected[name]
        assert not any(isinstance(node, prohibited_nodes) for node in ast.walk(function))
        assert not any(isinstance(node, ast.Dict) and any(key is None for key in node.keys) for node in ast.walk(function))
        assert not any(isinstance(node, ast.keyword) and node.arg is None for node in ast.walk(function))
        assert not any(isinstance(node, ast.Name) and node.id in prohibited_names for node in ast.walk(function))
        assert not any(isinstance(node, ast.Attribute) and node.attr in {"__dict__", "asdict", "keys", "values", "items", "get"} for node in ast.walk(function))
        assert not any(isinstance(node, ast.Subscript) and isinstance(node.value, ast.Name) and node.value.id == "row" for node in ast.walk(function))
        for call in (node for node in ast.walk(function) if isinstance(node, ast.Call)):
            if any(isinstance(arg, ast.Name) and arg.id == "row" for arg in call.args):
                assert isinstance(call.func, ast.Name)
                assert (name, call.func.id) in {("_fixture_pre_visual_binding_sha256", "_fixture_pre_visual_binding_payload"), ("_fixture_admission_payload", "_fixture_pre_visual_binding_payload"), ("_fixture_admission_binding_sha256", "_fixture_admission_payload")}

    assert "binding_sha256" not in page_proof._WITNESS_ROOT_KEYS
    assert "binding_sha256" not in page_proof._VISUAL_CROSSCHECK_ROOT_KEYS
    assert "pre_visual_binding_sha256" in page_proof._WITNESS_ROOT_KEYS
    assert "pre_visual_binding_sha256" in page_proof._VISUAL_CROSSCHECK_ROOT_KEYS
