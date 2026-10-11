import inspect
import json

import pytest

from kb_creator.pdf_raw import page_proof
from kb_creator.pdf_raw.errors import RawPdfError
from kb_creator.tests import _page_proof_fixture_leaves as leaves


_PRIVATE_TOPOLOGY_DIGEST = "4d3683f15ae64b4d03e51211755f2b3580e112e35bce4bf8c69efa29645dd3b4"
_FLOW_ERROR = "page_proof_flow_invalid"
_ADJACENCY_ERROR = "page_proof_adjacency_invalid"
_PRECEDENCE_MATRIX = (
    (False, False, False, False, "included", "included"),
    (False, False, False, True, "excluded", "running_marginal"),
    (False, False, True, False, "excluded", "occlusion"),
    (False, False, True, True, "excluded", "occlusion"),
    (False, True, False, False, "excluded", "text_layer_disagreement"),
    (False, True, False, True, "excluded", "text_layer_disagreement"),
    (False, True, True, False, "excluded", "text_layer_disagreement"),
    (False, True, True, True, "excluded", "text_layer_disagreement"),
    (True, False, False, False, "excluded", "visual_only"),
    (True, False, False, True, "excluded", "visual_only"),
    (True, False, True, False, "excluded", "visual_only"),
    (True, False, True, True, "excluded", "visual_only"),
    (True, True, False, False, "excluded", "visual_only"),
    (True, True, False, True, "excluded", "visual_only"),
    (True, True, True, False, "excluded", "visual_only"),
    (True, True, True, True, "excluded", "visual_only"),
)


def _canonical_json(value: object) -> bytes:
    return json.dumps(value, ensure_ascii=True, sort_keys=True, separators=(",", ":")).encode("utf-8")


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
                independent_visual_crosscheck_byte_length=leaves.TWO_COLUMN_LENGTHS[3],
                independent_visual_crosscheck_sha256=leaves.TWO_COLUMN_SHA256[3],
                pre_visual_binding_sha256="cdb993a29ef0b05229a9a9c5dfd65dd30977df9c3ec1c295a88a94b5ea1f9c1d",
        binding_sha256="0c45fd6b6440482b377fbcd3c6797701e622250dc0fdd496d18dbef81cd48838",
                expected_candidate_sha256="9bc92192ee0e03282585b83d6902b9367b1960b897c20da0c0c7240725c73e21",
                expected_reviewed_ledger_sha256="91ceaadb97a611699e648ca865be60951709f09b1c5cf555ceb1f3c94cf427c0",
            ),
            leaves.WITNESS_TWO_COLUMN_V1,
            leaves.RENDER_PNG_TWO_COLUMN_V1,
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
                independent_visual_crosscheck_byte_length=leaves.NESTED_FORM_LENGTHS[3],
                independent_visual_crosscheck_sha256=leaves.NESTED_FORM_SHA256[3],
                pre_visual_binding_sha256="388f7cc61345dbbcb516a4090e0d35cabb308f37137bf9b6b86c691fbf6c122c",
        binding_sha256="249d56182c4710e6392740703ed86d388b714498d1bbc9c60e403de0caf0fbf2",
                expected_candidate_sha256="c91d828ac9d5225df07efa76d0f854717ae67c5fb193d427f1992ab51631e929",
                expected_reviewed_ledger_sha256="a3382a5a0c432967419b6266156d1b132e22ef7f44ecc8ea8043b75da7d93d7b",
            ),
            leaves.WITNESS_NESTED_FORM_V1,
            leaves.RENDER_PNG_NESTED_FORM_V1,
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
                independent_visual_crosscheck_byte_length=leaves.VISUAL_ONLY_LENGTHS[3],
                independent_visual_crosscheck_sha256=leaves.VISUAL_ONLY_SHA256[3],
                pre_visual_binding_sha256="7f9327e3dba8c5ad888efa3423115e779b0bb0502438e7ddd9c02cd2c43dbea2",
        binding_sha256="4d9c98331427c55f788ee2fc532365434054e6d300236120fc11946c7894aecd",
                expected_candidate_sha256="98f9ccd0bf6d8c02a977472fcad6ac9feed628fd6a2943464307b9f4860d744a",
                expected_reviewed_ledger_sha256="696cac67d638d93b51d4d475e34205cf5b4f432fcc517c21bdab6c51a9e8ccd3",
            ),
            leaves.WITNESS_VISUAL_ONLY_V1,
            leaves.RENDER_PNG_VISUAL_ONLY_V1,
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


def _normalized_mechanics(case_index: int) -> dict[str, object]:
    row, witness_raw, render_raw = _case_rows()[case_index]
    return page_proof._normalize_fixture_witness_render_components(
        _authority_for(row, witness_raw),
        witness_raw,
        render_raw,
        row,
    )


def _stub_mechanics(atom_count: int) -> dict[str, object]:
    return {
        "atom_geometry_rows": tuple({"atom_row_id": f"a{index}"} for index in range(atom_count)),
        "visual_components": tuple({"component_id": f"c{index}"} for index in range(atom_count)),
    }


def _block(block_id: str, ordinal: int, atom_row_id: str, component_id: str, fragment_ids: list[str], column_index: int, *, running_marginal: bool = False, occluded: bool = False, text_layer_disagreement: bool = False, visual_only: bool = False) -> dict[str, object]:
    return {
        "block_id": block_id,
        "block_ordinal": ordinal,
        "atom_row_ids": [atom_row_id],
        "component_ids": [component_id],
        "fragment_ids": fragment_ids,
        "column_index": column_index,
        "flow_flags": {
            "running_marginal": running_marginal,
            "occluded": occluded,
            "text_layer_disagreement": text_layer_disagreement,
            "visual_only": visual_only,
        },
    }


@pytest.mark.parametrize(
    ("visual_only", "text_layer_disagreement", "occluded", "running_marginal", "expected_disposition", "expected_reason"),
    _PRECEDENCE_MATRIX,
)
def test_reading_flow_disposition_precedence_has_explicit_16_of_16_literal_matrix(
    visual_only: bool,
    text_layer_disagreement: bool,
    occluded: bool,
    running_marginal: bool,
    expected_disposition: str,
    expected_reason: str,
):
    flags = {
        "running_marginal": running_marginal,
        "occluded": occluded,
        "text_layer_disagreement": text_layer_disagreement,
        "visual_only": visual_only,
    }
    assert page_proof._derive_reading_flow_disposition(flags) == (expected_disposition, expected_reason)


def test_oracle_baseline_is_literal_and_non_circular():
    source = inspect.getsource(inspect.getmodule(test_oracle_baseline_is_literal_and_non_circular))
    assert "".join(("def ", "_adjacency_from_included")) not in source
    assert "".join(("for index in range", "(len(included)")) not in source
    assert len(_PRECEDENCE_MATRIX) == 16
    assert _PRECEDENCE_MATRIX[0] == (False, False, False, False, "included", "included")
    assert _PRECEDENCE_MATRIX[-1] == (True, True, True, True, "excluded", "visual_only")


def test_partition_substitution_and_repair_fail_closed():
    normalized = _stub_mechanics(4)
    valid = {
        "blocks": [
            _block("b0", 0, "a0", "c0", ["f0"], 1),
            _block("b1", 1, "a1", "c1", ["f1"], 1, running_marginal=True),
            _block("b2", 2, "a2", "c2", ["f2"], 1),
            _block("b3", 3, "a3", "c3", ["f3"], 2, visual_only=True),
        ],
        "included_block_ids": ["b0", "b2"],
        "excluded_block_ids": ["b1", "b3"],
        "adjacency_rows": [
            {
                "source_fragment_id": "f0",
                "target_fragment_id": "f2",
                "boundary_kind": "within_column",
                "source_block_id": "b0",
                "target_block_id": "b2",
            }
        ],
    }
    normalized_flow = page_proof._normalize_fixture_block_flow_adjacency(normalized, valid)
    assert normalized_flow["included_block_ids"] == ("b0", "b2")
    assert normalized_flow["excluded_block_ids"] == ("b1", "b3")
    broken = dict(valid)
    broken["included_block_ids"] = ["b1", "b2"]
    with pytest.raises(RawPdfError, match=f"^{_FLOW_ERROR}$"):
        page_proof._normalize_fixture_block_flow_adjacency(normalized, broken)
    assert page_proof._normalize_fixture_block_flow_adjacency(normalized, valid)["pre_visual_evidence_core_sha256"] == normalized_flow["pre_visual_evidence_core_sha256"]


def test_excluded_fragment_is_not_admitted_to_fragment_or_boundary_universe():
    normalized = _stub_mechanics(3)
    valid = {
        "blocks": [
            _block("b0", 0, "a0", "c0", ["f0"], 0),
            _block("b1", 1, "a1", "c1", ["fx"], 0, occluded=True),
            _block("b2", 2, "a2", "c2", ["f2"], 1),
        ],
        "included_block_ids": ["b0", "b2"],
        "excluded_block_ids": ["b1"],
        "adjacency_rows": [
            {
                "source_fragment_id": "f0",
                "target_fragment_id": "f2",
                "boundary_kind": "cross_column",
                "source_block_id": "b0",
                "target_block_id": "b2",
            }
        ],
    }
    normalized_flow = page_proof._normalize_fixture_block_flow_adjacency(normalized, valid)
    assert [row["fragment_id"] for row in normalized_flow["fragment_universe"]] == ["f0", "f2"]
    assert all("fx" not in row.values() for row in normalized_flow["adjacency_universe"])


def test_shuffled_missing_extra_and_nonadjacent_edges_fail_closed_then_repair_from_literal_baseline():
    normalized = _stub_mechanics(4)
    valid = {
        "blocks": [
            _block("b0", 0, "a0", "c0", ["f0"], 0),
            _block("b1", 1, "a1", "c1", ["f1"], 0),
            _block("b2", 2, "a2", "c2", ["f2"], 1),
            _block("b3", 3, "a3", "c3", ["f3"], 1),
        ],
        "included_block_ids": ["b0", "b1", "b2", "b3"],
        "excluded_block_ids": [],
        "adjacency_rows": [
            {
                "source_fragment_id": "f0",
                "target_fragment_id": "f1",
                "boundary_kind": "within_column",
                "source_block_id": "b0",
                "target_block_id": "b1",
            },
            {
                "source_fragment_id": "f1",
                "target_fragment_id": "f2",
                "boundary_kind": "cross_column",
                "source_block_id": "b1",
                "target_block_id": "b2",
            },
            {
                "source_fragment_id": "f2",
                "target_fragment_id": "f3",
                "boundary_kind": "within_column",
                "source_block_id": "b2",
                "target_block_id": "b3",
            },
        ],
    }
    assert page_proof._normalize_fixture_block_flow_adjacency(normalized, valid)
    shuffled = dict(valid)
    shuffled["adjacency_rows"] = list(reversed(valid["adjacency_rows"]))
    with pytest.raises(RawPdfError, match=f"^{_ADJACENCY_ERROR}$"):
        page_proof._normalize_fixture_block_flow_adjacency(normalized, shuffled)
    missing = dict(valid)
    missing["adjacency_rows"] = valid["adjacency_rows"][:-1]
    with pytest.raises(RawPdfError, match=f"^{_ADJACENCY_ERROR}$"):
        page_proof._normalize_fixture_block_flow_adjacency(normalized, missing)
    extra = dict(valid)
    extra["adjacency_rows"] = valid["adjacency_rows"] + [valid["adjacency_rows"][-1]]
    with pytest.raises(RawPdfError, match=f"^{_ADJACENCY_ERROR}$"):
        page_proof._normalize_fixture_block_flow_adjacency(normalized, extra)
    nonadjacent = dict(valid)
    nonadjacent["adjacency_rows"] = list(valid["adjacency_rows"])
    nonadjacent["adjacency_rows"][0] = dict(nonadjacent["adjacency_rows"][0])
    nonadjacent["adjacency_rows"][0]["target_fragment_id"] = "f2"
    with pytest.raises(RawPdfError, match=f"^{_ADJACENCY_ERROR}$"):
        page_proof._normalize_fixture_block_flow_adjacency(normalized, nonadjacent)
    repaired = page_proof._normalize_fixture_block_flow_adjacency(normalized, valid)
    assert repaired["adjacency_universe"] == tuple(valid["adjacency_rows"])


def test_running_marginal_occlusion_disagreement_visual_only_and_cross_column_positives_with_literal_oracles_and_no_xy_sort():
    two_column = _normalized_mechanics(0)
    two_blocks = []
    for index, (atom_row, component) in enumerate(zip(two_column["atom_geometry_rows"], two_column["visual_components"])):
        two_blocks.append(
            _block(
                f"b{index}",
                index,
                atom_row["atom_row_id"],
                component["component_id"],
                [f"f{index}"],
                1 if index < len(two_column["atom_geometry_rows"]) // 2 else 0,
            )
        )
    two_literal = {
        "blocks": two_blocks,
        "included_block_ids": [block["block_id"] for block in two_blocks],
        "excluded_block_ids": [],
        "adjacency_rows": [
            {
                "source_fragment_id": "f0",
                "target_fragment_id": "f1",
                "boundary_kind": "cross_column",
                "source_block_id": "b0",
                "target_block_id": "b1",
            },
        ],
    }
    two_normalized = page_proof._normalize_fixture_block_flow_adjacency(two_column, two_literal)
    assert two_normalized["paint_order_atom_row_ids"] == tuple(row["atom_row_id"] for row in two_column["atom_geometry_rows"])
    assert two_normalized["adjacency_universe"] == tuple(two_literal["adjacency_rows"])
    assert [row["fragment_id"] for row in two_normalized["fragment_universe"]] == ["f0", "f1"]

    reason_mechanics = _stub_mechanics(4)
    reason_literal = {
        "blocks": [
            _block("b0", 0, "a0", "c0", ["n0"], 0),
            _block("b1", 1, "a1", "c1", ["n1"], 0, running_marginal=True),
            _block("b2", 2, "a2", "c2", ["n2"], 0, occluded=True),
            _block("b3", 3, "a3", "c3", ["n3"], 0, text_layer_disagreement=True),
        ],
        "included_block_ids": ["b0"],
        "excluded_block_ids": ["b1", "b2", "b3"],
        "adjacency_rows": [],
    }
    reason_flow = page_proof._normalize_fixture_block_flow_adjacency(reason_mechanics, reason_literal)
    assert [block["reading_flow_reason"] for block in reason_flow["blocks"]] == [
        "included",
        "running_marginal",
        "occlusion",
        "text_layer_disagreement",
    ]
    assert [row["fragment_id"] for row in reason_flow["fragment_universe"]] == ["n0"]

    visual_only = _normalized_mechanics(2)
    visual_block = _block(
        "b0",
        0,
        visual_only["atom_geometry_rows"][0]["atom_row_id"],
        visual_only["visual_components"][0]["component_id"],
        ["v0"],
        0,
        visual_only=True,
    )
    visual_literal = {
        "blocks": [visual_block],
        "included_block_ids": [],
        "excluded_block_ids": ["b0"],
        "adjacency_rows": [],
    }
    visual_flow = page_proof._normalize_fixture_block_flow_adjacency(visual_only, visual_literal)
    assert visual_flow["included_block_ids"] == ()
    assert visual_flow["excluded_block_ids"] == ("b0",)
    assert visual_flow["fragment_universe"] == ()
