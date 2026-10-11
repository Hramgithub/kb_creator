from dataclasses import replace
import hashlib
import json

from kb_creator.pdf_raw import page_proof
from kb_creator.tests import _page_proof_fixture_leaves as leaves


_PRIVATE_TOPOLOGY_DIGEST = "4d3683f15ae64b4d03e51211755f2b3580e112e35bce4bf8c69efa29645dd3b4"

_PRIVATE_FIXTURE_ADMISSIONS = (
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
)

_PRIVATE_EXPECTED_FIXTURE_ADMISSION_PRIMITIVES = ((b'page-proof.positive-two-column.v1', 33, 'e40137c0f1597d0a7b4aac30969a521e40c28d8019f02be2c10e21593dc127c9', 'stage-a.positive-two-column.v1', '890a9cef3ce995e7cb7881c035baa3e1e5a4c782f1827847b640c93fb28eafef', '4d3683f15ae64b4d03e51211755f2b3580e112e35bce4bf8c69efa29645dd3b4', 119, '10ed1f66fb1f4022051d3c3b0deca071fabe5c3f10a6673872655ed49d4d91a3', 'cdb993a29ef0b05229a9a9c5dfd65dd30977df9c3ec1c295a88a94b5ea1f9c1d', 3050, 'd08e02060ccb8a602a445cc14f0e71fd16fbcf1616d826463e00c64f46948295', 2501, '2c358a6feb63859fa2f4c10346bd64e26da13f1e6d64f7cce5a868f881cab2c5', '0c45fd6b6440482b377fbcd3c6797701e622250dc0fdd496d18dbef81cd48838', '9bc92192ee0e03282585b83d6902b9367b1960b897c20da0c0c7240725c73e21', '91ceaadb97a611699e648ca865be60951709f09b1c5cf555ceb1f3c94cf427c0'), (b'page-proof.positive-nested-form.v1', 34, 'a3b7a43716c68188aade57ef01da907d582b63fb4d478cb6fe01f6c0bbfdf558', 'stage-a.positive-nested-form.v1', '8726e5d36b7acba9d96eacdcd62a57da00d7f4cfdd4df79cd6c63106d2e353e7', '4d3683f15ae64b4d03e51211755f2b3580e112e35bce4bf8c69efa29645dd3b4', 107, '416dfa33e7cb1b999ecb7fb3919d49b7482e5c2a1d459f1351e7c3ebf2b75303', '388f7cc61345dbbcb516a4090e0d35cabb308f37137bf9b6b86c691fbf6c122c', 2927, 'c488c0491139d27e696b5ab4ea4205b5ada0a9f577e3c3a23231868469eb85c3', 2084, '887aba071a09620cdc4789a5635ba57661eff0eec0792ad50db66af3a2d4f0d3', '249d56182c4710e6392740703ed86d388b714498d1bbc9c60e403de0caf0fbf2', 'c91d828ac9d5225df07efa76d0f854717ae67c5fb193d427f1992ab51631e929', 'a3382a5a0c432967419b6266156d1b132e22ef7f44ecc8ea8043b75da7d93d7b'), (b'page-proof.positive-visual-only.v1', 34, '0de3f42cefdd92ad05303f3cc39043f98a990468c220ed3c1ebd01867d2ea998', 'stage-a.identity-single-use.v1', 'e10859438e4ccef9ea6fdff9c8e3c923e71f39c4ae1b2c6a420d4319a1c468ed', '4d3683f15ae64b4d03e51211755f2b3580e112e35bce4bf8c69efa29645dd3b4', 86, '78e18a99eddb04e0123fb8aaafa4996f3cfa2acea02214841c68882c88932a33', '7f9327e3dba8c5ad888efa3423115e779b0bb0502438e7ddd9c02cd2c43dbea2', 2125, '68d22df7ade83daa01348bcd25dc90ec69a9f0efe73b9f6f0bb0b9cfe379fb2e', 1461, '1e47e656240499dcc6d2c1e25a64691fe99c02d9801b6f52b2f8cc80993f1c76', '4d9c98331427c55f788ee2fc532365434054e6d300236120fc11946c7894aecd', '98f9ccd0bf6d8c02a977472fcad6ac9feed628fd6a2943464307b9f4860d744a', '696cac67d638d93b51d4d475e34205cf5b4f432fcc517c21bdab6c51a9e8ccd3'))


def _sha256(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def _oracle_pre_visual_binding_sha256(row: page_proof._FixtureAdmission) -> str:
    payload = {
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
    return _sha256(b"page-proof.fixture-pre-visual-binding.v1\0" + json.dumps(payload, ensure_ascii=True, sort_keys=True, separators=(",", ":")).encode())


def _oracle_final_admission_binding_sha256(row: page_proof._FixtureAdmission) -> str:
    payload = {
        "fixture_id": row.fixture_id.decode("ascii"), "fixture_id_byte_length": row.fixture_id_byte_length,
        "fixture_id_sha256": row.fixture_id_sha256, "stage_a_fixture_id": row.stage_a_fixture_id,
        "stage_a_authority_content_sha256": row.stage_a_authority_content_sha256,
        "required_topology_inventory_content_sha256": row.required_topology_inventory_content_sha256,
        "render_png_byte_length": row.render_png_byte_length, "render_png_sha256": row.render_png_sha256,
        "witness_schema": "kb_creator.pdf_raw.PageProofWitnessV3",
        "visual_crosscheck_schema": "kb_creator.pdf_raw.IndependentPageVisualCrossCheckV2",
        "pre_visual_binding_sha256": row.pre_visual_binding_sha256,
        "witness_byte_length": row.witness_byte_length, "witness_sha256": row.witness_sha256,
        "independent_visual_crosscheck_byte_length": row.independent_visual_crosscheck_byte_length,
        "independent_visual_crosscheck_sha256": row.independent_visual_crosscheck_sha256,
    }
    return _sha256(b"page-proof.fixture-admission.v2\0" + json.dumps(payload, ensure_ascii=True, sort_keys=True, separators=(",", ":")).encode())


def _canonical_rows() -> tuple[page_proof._FixtureAdmission, ...]:
    return _PRIVATE_FIXTURE_ADMISSIONS


def _canonical_expected() -> tuple[tuple[object, ...], ...]:
    return _PRIVATE_EXPECTED_FIXTURE_ADMISSION_PRIMITIVES


def _canonical_row(index: int) -> page_proof._FixtureAdmission:
    return _canonical_rows()[index]


def _registry_is_valid(
    rows: tuple[page_proof._FixtureAdmission, ...],
    expected_primitives: tuple[tuple[object, ...], ...],
    digest: str = _PRIVATE_TOPOLOGY_DIGEST,
) -> bool:
    return page_proof._fixture_admission_registry_is_valid(rows, expected_primitives, digest)


def _row_with_binding(row: page_proof._FixtureAdmission) -> page_proof._FixtureAdmission:
    rebound = replace(row, binding_sha256="0" * 64)
    return replace(rebound, binding_sha256=page_proof._fixture_admission_binding_sha256(rebound))


def _recompute_row(
    row: page_proof._FixtureAdmission,
    *,
    fixture_id: bytes | None = None,
    stage_a_fixture_id: str | None = None,
    stage_a_authority_content_sha256: str | None = None,
    required_topology_inventory_content_sha256: str | None = None,
    witness_pair: tuple[int, str] | None = None,
    render_pair: tuple[int, str] | None = None,
    crosscheck_pair: tuple[int, str] | None = None,
    expected_candidate_sha256: str | None = None,
    expected_reviewed_ledger_sha256: str | None = None,
) -> page_proof._FixtureAdmission:
    updated = row
    if fixture_id is not None:
        updated = replace(
            updated,
            fixture_id=fixture_id,
            fixture_id_byte_length=len(fixture_id),
            fixture_id_sha256=_sha256(fixture_id),
        )
    if stage_a_fixture_id is not None:
        updated = replace(updated, stage_a_fixture_id=stage_a_fixture_id)
    if stage_a_authority_content_sha256 is not None:
        updated = replace(updated, stage_a_authority_content_sha256=stage_a_authority_content_sha256)
    if required_topology_inventory_content_sha256 is not None:
        updated = replace(updated, required_topology_inventory_content_sha256=required_topology_inventory_content_sha256)
    if witness_pair is not None:
        updated = replace(updated, witness_byte_length=witness_pair[0], witness_sha256=witness_pair[1])
    if render_pair is not None:
        updated = replace(updated, render_png_byte_length=render_pair[0], render_png_sha256=render_pair[1])
    if crosscheck_pair is not None:
        updated = replace(
            updated,
            independent_visual_crosscheck_byte_length=crosscheck_pair[0],
            independent_visual_crosscheck_sha256=crosscheck_pair[1],
        )
    if expected_candidate_sha256 is not None:
        updated = replace(updated, expected_candidate_sha256=expected_candidate_sha256)
    if expected_reviewed_ledger_sha256 is not None:
        updated = replace(updated, expected_reviewed_ledger_sha256=expected_reviewed_ledger_sha256)
    updated = replace(updated, pre_visual_binding_sha256="0" * 64)
    updated = replace(updated, pre_visual_binding_sha256=page_proof._fixture_pre_visual_binding_sha256(updated))
    return _row_with_binding(updated)


def _replace_row(
    rows: tuple[page_proof._FixtureAdmission, ...],
    index: int,
    row: page_proof._FixtureAdmission,
) -> tuple[page_proof._FixtureAdmission, ...]:
    updated = list(rows)
    updated[index] = row
    return tuple(updated)


def _mutate_expected_child(
    expected_primitives: tuple[tuple[object, ...], ...],
    index: int,
    child: tuple[object, ...],
) -> tuple[tuple[object, ...], ...]:
    updated = list(expected_primitives)
    updated[index] = child
    return tuple(updated)


def _assert_canonical_registry_still_valid() -> None:
    assert all(page_proof._fixture_admission_is_valid(row) for row in _canonical_rows())
    assert _registry_is_valid(_canonical_rows(), _canonical_expected())


def _alternate_fixture_id() -> bytes:
    return b"page-proof.positive-two-column.x1"


def _alternate_expected_hash() -> str:
    return "f" * 64


def _mutate_semantic_row(target: str) -> tuple[page_proof._FixtureAdmission, bool]:
    base = _canonical_row(0)
    other = _canonical_row(1)
    visual = _canonical_row(2)
    if target == "fixture identity":
        return _recompute_row(base, fixture_id=_alternate_fixture_id()), True
    if target == "fixture length":
        return _recompute_row(base, fixture_id=b"page-proof.positive-two-column.x2"), True
    if target == "Stage A fixture":
        return _recompute_row(base, stage_a_fixture_id=other.stage_a_fixture_id), True
    if target == "Stage A content":
        return _recompute_row(base, stage_a_authority_content_sha256=other.stage_a_authority_content_sha256), True
    if target == "topology digest":
        return _recompute_row(base, required_topology_inventory_content_sha256="1" * 64), True
    if target == "witness leaf":
        return _recompute_row(base, witness_pair=(other.witness_byte_length, other.witness_sha256)), True
    if target == "render leaf":
        return _recompute_row(base, render_pair=(other.render_png_byte_length, other.render_png_sha256)), True
    if target == "visual cross-check leaf":
        return _recompute_row(
            base,
            crosscheck_pair=(
                other.independent_visual_crosscheck_byte_length,
                other.independent_visual_crosscheck_sha256,
            ),
        ), True
    if target == "complete cross-pair":
        return _recompute_row(
            base,
            witness_pair=(visual.witness_byte_length, visual.witness_sha256),
            render_pair=(visual.render_png_byte_length, visual.render_png_sha256),
            crosscheck_pair=(
                visual.independent_visual_crosscheck_byte_length,
                visual.independent_visual_crosscheck_sha256,
            ),
        ), True
    if target == "expected candidate":
        return _recompute_row(base, expected_candidate_sha256=_alternate_expected_hash()), True
    if target == "expected reviewed":
        return _recompute_row(base, expected_reviewed_ledger_sha256=_alternate_expected_hash()), True
    if target == "binding seal":
        return replace(base, binding_sha256=_alternate_expected_hash()), False
    raise AssertionError(target)


def test_private_literal_fixture_rows_and_expected_tuple_are_closed_and_valid():
    assert page_proof._PRODUCTION_FIXTURE_ADMISSION == ()
    assert page_proof._PRODUCTION_EXPECTED_FIXTURE_ADMISSION_PRIMITIVES == ()
    assert type(_canonical_expected()) is tuple
    assert all(type(child) is tuple for child in _canonical_expected())
    assert tuple(page_proof._fixture_admission_primitives(row) for row in _canonical_rows()) == _canonical_expected()
    for row in _canonical_rows():
        assert row.pre_visual_binding_sha256 == _oracle_pre_visual_binding_sha256(row)
        assert row.binding_sha256 == _oracle_final_admission_binding_sha256(row)
        assert row.pre_visual_binding_sha256 == page_proof._fixture_pre_visual_binding_sha256(row)
        assert row.binding_sha256 == page_proof._fixture_admission_binding_sha256(row)
        assert page_proof._fixture_admission_row_matches_derive_leaves(
            row,
            (leaves.TWO_COLUMN, leaves.NESTED_FORM, leaves.VISUAL_ONLY)[_canonical_rows().index(row)][1],
            (leaves.TWO_COLUMN, leaves.NESTED_FORM, leaves.VISUAL_ONLY)[_canonical_rows().index(row)][2],
            (leaves.TWO_COLUMN, leaves.NESTED_FORM, leaves.VISUAL_ONLY)[_canonical_rows().index(row)][3],
        )
    for row, child in zip(_canonical_rows(), _canonical_expected()):
        assert row is not child
    _assert_canonical_registry_still_valid()


def test_fixture_admission_schema_negatives_fail_closed():
    base = _canonical_row(0)
    invalid_rows = (
        replace(base, fixture_id="not-bytes"),
        replace(base, fixture_id=b"\xff"),
        replace(base, fixture_id_byte_length=0),
        replace(base, fixture_id_byte_length=-1),
        replace(base, fixture_id_byte_length=True),
        replace(base, witness_byte_length=0),
        replace(base, witness_byte_length=-1),
        replace(base, witness_byte_length=True),
        replace(base, render_png_byte_length=0),
        replace(base, independent_visual_crosscheck_byte_length=0),
        replace(base, fixture_id_sha256="A" * 64),
        replace(base, witness_sha256="a" * 63),
        replace(base, render_png_sha256="g" * 64),
        replace(base, independent_visual_crosscheck_sha256="A" * 64),
        replace(base, binding_sha256="A" * 64),
        replace(base, expected_candidate_sha256="A" * 64),
        replace(base, expected_reviewed_ledger_sha256="A" * 64),
        replace(base, fixture_id_sha256="0" * 64),
        replace(base, binding_sha256="0" * 64),
    )
    for row in invalid_rows:
        assert not page_proof._fixture_admission_is_valid(row)
    _assert_canonical_registry_still_valid()


def test_resealed_target_only_semantic_negatives_fail_registry_and_repair_positive():
    targets = (
        "fixture identity",
        "fixture length",
        "Stage A fixture",
        "Stage A content",
        "topology digest",
        "witness leaf",
        "render leaf",
        "visual cross-check leaf",
        "complete cross-pair",
        "expected candidate",
        "expected reviewed",
        "binding seal",
    )
    for target in targets:
        mutated_row, row_should_stay_valid = _mutate_semantic_row(target)
        mutated_rows = _replace_row(_canonical_rows(), 0, mutated_row)
        if row_should_stay_valid:
            assert page_proof._fixture_admission_is_valid(mutated_row)
        else:
            assert not page_proof._fixture_admission_is_valid(mutated_row)
        assert not _registry_is_valid(mutated_rows, _canonical_expected())
        repaired_rows = _replace_row(_canonical_rows(), 0, _canonical_row(0))
        assert page_proof._fixture_admission_is_valid(repaired_rows[0])
        assert _registry_is_valid(repaired_rows, _canonical_expected())
        _assert_canonical_registry_still_valid()


def test_duplicate_reorder_missing_and_extra_rows_fail_registry_and_repair():
    duplicate_rows = (_canonical_row(0), _canonical_row(0), _canonical_row(2))
    reorder_rows = (_canonical_row(1), _canonical_row(0), _canonical_row(2))
    missing_rows = (_canonical_row(0), _canonical_row(1))
    extra_rows = _canonical_rows() + (_canonical_row(0),)
    for rows in (duplicate_rows, reorder_rows, missing_rows, extra_rows):
        assert not _registry_is_valid(rows, _canonical_expected())
        _assert_canonical_registry_still_valid()


def test_expected_tuple_independence_and_shape_attacks_fail_registry():
    altered_child = (
        _canonical_expected()[0][0],
        _canonical_expected()[0][1],
        _canonical_expected()[0][2],
        _canonical_expected()[0][3],
        _canonical_expected()[0][4],
        _canonical_expected()[0][5],
        _canonical_expected()[0][6],
        _canonical_expected()[0][7],
        _canonical_expected()[0][8],
        _canonical_expected()[0][9],
        _canonical_expected()[0][10],
        _canonical_expected()[0][11],
        _canonical_expected()[0][12],
        _alternate_expected_hash(),
        _canonical_expected()[0][14],
    )
    assert not _registry_is_valid(_canonical_rows(), _mutate_expected_child(_canonical_expected(), 0, altered_child))
    assert not _registry_is_valid(_canonical_rows(), (_canonical_expected()[1], _canonical_expected()[0], _canonical_expected()[2]))
    assert not _registry_is_valid(_canonical_rows(), [child for child in _canonical_expected()])  # type: ignore[arg-type]
    assert not _registry_is_valid(_canonical_rows(), (_canonical_expected()[0], ("short",), _canonical_expected()[2]))
    _assert_canonical_registry_still_valid()


def test_topology_digest_argument_checks_fail_closed():
    assert not _registry_is_valid(_canonical_rows(), _canonical_expected(), "A" * 64)
    assert not _registry_is_valid(_canonical_rows(), _canonical_expected(), "a" * 63)
    assert not _registry_is_valid(_canonical_rows(), _canonical_expected(), 1)  # type: ignore[arg-type]
    _assert_canonical_registry_still_valid()
