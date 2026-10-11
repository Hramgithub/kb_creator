import ast
from dataclasses import replace
import hashlib
import inspect
import json

import pytest

from kb_creator.pdf_raw import page_proof
from kb_creator.pdf_raw.errors import RawPdfError
from kb_creator.tests import _page_proof_fixture_leaves as leaves


_TOPOLOGY = "4d3683f15ae64b4d03e51211755f2b3580e112e35bce4bf8c69efa29645dd3b4"
_CASES = (
    (leaves.TWO_COLUMN, "stage-a.positive-two-column.v1", "890a9cef3ce995e7cb7881c035baa3e1e5a4c782f1827847b640c93fb28eafef", "cdb993a29ef0b05229a9a9c5dfd65dd30977df9c3ec1c295a88a94b5ea1f9c1d", "0c45fd6b6440482b377fbcd3c6797701e622250dc0fdd496d18dbef81cd48838", ("atom-0", "atom-1"), ("b0", "b1"), (), ("f0", "f1")),
    (leaves.NESTED_FORM, "stage-a.positive-nested-form.v1", "8726e5d36b7acba9d96eacdcd62a57da00d7f4cfdd4df79cd6c63106d2e353e7", "388f7cc61345dbbcb516a4090e0d35cabb308f37137bf9b6b86c691fbf6c122c", "249d56182c4710e6392740703ed86d388b714498d1bbc9c60e403de0caf0fbf2", ("atom-0", "atom-1"), ("b0",), ("b1",), ("n0",)),
    (leaves.VISUAL_ONLY, "stage-a.identity-single-use.v1", "e10859438e4ccef9ea6fdff9c8e3c923e71f39c4ae1b2c6a420d4319a1c468ed", "7f9327e3dba8c5ad888efa3423115e779b0bb0502438e7ddd9c02cd2c43dbea2", "4d9c98331427c55f788ee2fc532365434054e6d300236120fc11946c7894aecd", ("atom-0",), (), ("b0",), ()),
)


def _sha256(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def _canonical_json(value: object) -> bytes:
    return json.dumps(value, ensure_ascii=True, sort_keys=True, separators=(",", ":")).encode("utf-8")


def _row(index: int, witness_raw: bytes | None = None, crosscheck_raw: bytes | None = None) -> page_proof._FixtureAdmission:
    leaf, stage_id, authority_sha, binding, final, _, _, _, _ = _CASES[index]
    witness = leaf[1] if witness_raw is None else witness_raw
    crosscheck = leaf[3] if crosscheck_raw is None else crosscheck_raw
    return page_proof._FixtureAdmission(
        fixture_id=leaf[0],
        fixture_id_byte_length=len(leaf[0]),
        fixture_id_sha256=_sha256(leaf[0]),
        stage_a_fixture_id=stage_id,
        stage_a_authority_content_sha256=authority_sha,
        required_topology_inventory_content_sha256=_TOPOLOGY,
        render_png_byte_length=len(leaf[2]),
        render_png_sha256=_sha256(leaf[2]),
        pre_visual_binding_sha256=binding,
        witness_byte_length=len(witness),
        witness_sha256=_sha256(witness),
        independent_visual_crosscheck_byte_length=len(crosscheck),
        independent_visual_crosscheck_sha256=_sha256(crosscheck),
        binding_sha256=final if witness_raw is None and crosscheck_raw is None else "0" * 64,
        expected_candidate_sha256="9bc92192ee0e03282585b83d6902b9367b1960b897c20da0c0c7240725c73e21",
        expected_reviewed_ledger_sha256="91ceaadb97a611699e648ca865be60951709f09b1c5cf555ceb1f3c94cf427c0",
    )


def _reseal_row(index: int, witness_raw: bytes, crosscheck_raw: bytes) -> page_proof._FixtureAdmission:
    draft = _row(index, witness_raw, crosscheck_raw)
    return replace(draft, binding_sha256=page_proof._fixture_admission_binding_sha256(draft))


def _authority(index: int, witness_raw: bytes) -> page_proof.RawAtomProvenanceAuthorityV1:
    _, stage_id, authority_sha, _, _, _, _, _, _ = _CASES[index]
    witness = json.loads(witness_raw.decode("utf-8"))
    raw = _canonical_json({
        "schema": "kb_creator.pdf_raw.RawAtomProvenanceAuthority.v1",
        "fixture": {"id": stage_id},
        "terminal_state": "fixture_only_authority",
        "content_sha256": authority_sha,
        "atoms": [{"atom_ordinal": row["atom_ordinal"], "atom_row_id": row["atom_row_id"]} for row in witness["atom_geometry_rows"]],
    })
    value = object.__new__(page_proof.RawAtomProvenanceAuthorityV1)
    object.__setattr__(value, "_raw", raw)
    object.__setattr__(value, "_fixture_id", stage_id)
    object.__setattr__(value, "_content_sha256", authority_sha)
    object.__setattr__(value, "_terminal_state", "fixture_only_authority")
    object.__setattr__(value, "_sealed", True)
    return value


def _reseal_witness(value: dict[str, object]) -> bytes:
    value["content_sha256"] = _sha256(_canonical_json({key: item for key, item in value.items() if key != "content_sha256"}))
    return _canonical_json(value)


def _compose(index: int, witness_raw: bytes | None = None, crosscheck_raw: bytes | None = None) -> dict[str, object]:
    leaf = _CASES[index][0]
    witness = leaf[1] if witness_raw is None else witness_raw
    crosscheck = leaf[3] if crosscheck_raw is None else crosscheck_raw
    row = _row(index) if witness_raw is None and crosscheck_raw is None else _reseal_row(index, witness, crosscheck)
    return page_proof._normalize_fixture_page_proof_composition(
        _authority(index, witness), witness, leaf[2], crosscheck, row,
    )


@pytest.mark.parametrize("index", range(3))
def test_canonical_literal_leaves_compose_to_the_independent_mechanics_flow_and_visual_primitives(index: int):
    _, _, _, binding, final, atom_ids, included, excluded, fragments = _CASES[index]
    result = _compose(index)
    assert _row(index).pre_visual_binding_sha256 == binding
    assert _row(index).binding_sha256 == final
    assert tuple(row["atom_row_id"] for row in result["mechanics"]["atom_geometry_rows"]) == atom_ids
    assert result["flow"]["included_block_ids"] == included
    assert result["flow"]["excluded_block_ids"] == excluded
    assert tuple(row["fragment_id"] for row in result["flow"]["fragment_universe"]) == fragments
    assert result["visual_crosscheck"]["content_sha256"] == json.loads(_CASES[index][0][3])["content_sha256"]


@pytest.mark.parametrize("mutation", ("schema", "missing", "unknown", "mistyped", "noncanonical"))
def test_witness_v3_flow_root_negatives_fail_before_composition_and_literal_repair_recovers(mutation: str):
    witness = json.loads(leaves.TWO_COLUMN[1])
    if mutation == "schema":
        witness["schema"] = "kb_creator.pdf_raw.PageProofWitnessV2"
    elif mutation == "missing":
        witness.pop("flow_input")
    elif mutation == "unknown":
        witness["flow_input"]["extra"] = 1
    elif mutation == "mistyped":
        witness["flow_input"] = []
    else:
        raw = leaves.TWO_COLUMN[1] + b" "
        with pytest.raises(RawPdfError, match="^page_proof_witness_schema_invalid$"):
            _compose(0, raw)
        assert _compose(0)["flow"]["included_block_ids"] == ("b0", "b1")
        return
    raw = _reseal_witness(witness)
    with pytest.raises(RawPdfError, match="^page_proof_(witness_schema_invalid|flow_invalid)$"):
        _compose(0, raw)
    assert _compose(0)["flow"]["included_block_ids"] == ("b0", "b1")


@pytest.mark.parametrize("target", ("duplicate", "missing", "reordered", "partition", "adjacency"))
def test_flow_ownership_partition_and_adjacency_negatives_are_witness_bound_and_repairable(target: str):
    witness = json.loads(leaves.TWO_COLUMN[1])
    flow = witness["flow_input"]
    if target == "duplicate":
        flow["blocks"][1]["atom_row_ids"] = ["atom-0"]
    elif target == "missing":
        flow["blocks"][1]["component_ids"] = []
    elif target == "reordered":
        flow["blocks"] = list(reversed(flow["blocks"]))
    elif target == "partition":
        flow["included_block_ids"] = ["b1", "b0"]
    else:
        flow["adjacency_rows"] = []
    with pytest.raises(RawPdfError, match="^page_proof_(flow_invalid|adjacency_invalid)$"):
        _compose(0, _reseal_witness(witness))
    assert _compose(0)["flow"]["adjacency_universe"][0]["boundary_kind"] == "cross_column"


def test_fully_resealed_flow_mutation_reaches_visual_crosscheck_and_rejects_its_stale_pre_visual_core():
    witness = json.loads(leaves.TWO_COLUMN[1])
    witness["flow_input"]["blocks"][0]["column_index"] = 0
    witness["flow_input"]["adjacency_rows"][0]["boundary_kind"] = "within_column"
    with pytest.raises(RawPdfError, match="^page_proof_visual_crosscheck_invalid$"):
        _compose(0, _reseal_witness(witness))
    assert _compose(0)["visual_crosscheck"]["content_sha256"] == json.loads(leaves.TWO_COLUMN[3])["content_sha256"]


@pytest.mark.parametrize("leaf_index", (1, 2, 3))
def test_cross_pairing_between_admitted_rows_is_rejected_before_any_composition(leaf_index: int):
    first, second = _CASES[0][0], _CASES[1][0]
    values = [first[1], first[2], first[3]]
    values[leaf_index - 1] = second[leaf_index]
    with pytest.raises(RawPdfError, match="^page_proof_fixture_admission_missing$"):
        page_proof._normalize_fixture_page_proof_composition(
            _authority(0, first[1]), values[0], values[1], values[2], _row(0),
        )


def test_composition_has_no_separate_or_pre_normalized_flow_entrance_and_no_geometry_or_visual_fallback():
    signature = inspect.signature(page_proof._normalize_fixture_page_proof_composition)
    assert tuple(signature.parameters) == (
        "validated_stage_a_authority", "witness_raw", "render_png_raw", "independent_visual_crosscheck_raw", "admission_row",
    )
    with pytest.raises(TypeError):
        page_proof._normalize_fixture_page_proof_composition(_authority(0, leaves.TWO_COLUMN[1]), leaves.TWO_COLUMN[1], leaves.TWO_COLUMN[2], leaves.TWO_COLUMN[3], _row(0), {})
    tree = ast.parse(inspect.getsource(page_proof._normalize_fixture_page_proof_composition))
    calls = [node.func.id for node in ast.walk(tree) if isinstance(node, ast.Call) and isinstance(node.func, ast.Name)]
    assert calls.count("_normalize_fixture_witness_render_components") == 1
    assert calls.count("_normalize_fixture_block_flow_adjacency") == 1
    assert calls.count("_normalize_fixture_visual_crosscheck") == 1
    helper = ast.parse(inspect.getsource(leaves))
    assert not any(isinstance(node, (ast.Import, ast.ImportFrom, ast.Call, ast.ListComp, ast.DictComp, ast.SetComp)) for node in ast.walk(helper))
