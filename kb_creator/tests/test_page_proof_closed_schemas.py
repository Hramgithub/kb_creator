import copy
from dataclasses import replace
import json
import pickle

import pytest

from kb_creator.pdf_raw import page_proof
from kb_creator.pdf_raw.errors import RawPdfError
from kb_creator.tests import _page_proof_fixture_leaves as leaves


_COVERAGE_ERROR = "page_proof_stage_a_fixture_coverage_incomplete"
_REGISTRY_ERROR = "page_proof_fixture_registry_invalid"
_INGRESS_ERROR = "page_proof_public_ingress_invalid"
_ADMISSION_ERROR = "page_proof_fixture_admission_missing"
_AUTHORITY_ERROR = "page_proof_stage_a_authority_invalid"
_CANDIDATE_SCHEMA_ERROR = "page_proof_candidate_schema_invalid"
_REVIEW_SCHEMA_ERROR = "page_proof_review_schema_invalid"
_EXPECTED_LEDGER_SCHEMA_ERROR = "page_proof_expected_ledger_schema_invalid"
_BOUNDARY_ERROR = "page_proof_public_boundary_incomplete"
_PRIVATE_TOPOLOGY_DIGEST = "4d3683f15ae64b4d03e51211755f2b3580e112e35bce4bf8c69efa29645dd3b4"


def _canonical_json(value: object) -> bytes:
    return json.dumps(value, ensure_ascii=True, sort_keys=True, separators=(",", ":")).encode("utf-8")


def _entry(**values):
    draft = page_proof._RequiredStageATopologyEntry(entry_sha256="0" * 64, **values)
    return replace(draft, entry_sha256=page_proof._entry_sha256(draft))


def _private_valid_inventory():
    rows = (
        _entry(
            topology_id="stage_a_positive_two_column.v1",
            stage_a_fixture_id="stage-a.positive-two-column.v1",
            stage_a_authority_schema="kb_creator.pdf_raw.RawAtomProvenanceAuthority.v1",
            stage_a_authority_content_sha256="890a9cef3ce995e7cb7881c035baa3e1e5a4c782f1827847b640c93fb28eafef",
            stage_a_authority_inventory_sha256="3173d033fcf6228687388f020f0e5e6e7e9c1ce2a373bc1b2bca49823ab951c0",
            stage_a_fixture_binding_sha256="c41ec7ae9eea7d5fc2f654eb825bf1bb1af954d00c754fd6140f134985af8880",
            positive_topology_assertion_sha256="e681b6ffbed2705283b915039e1d7a6ac145f4988765fd772a68eb63803831c8",
            independent_stage_a_review_kind="fixture_topology_acceptance",
            independent_stage_a_review_decision="accept",
            independent_stage_a_review_content_sha256="74ddca65755dbde190b57a5e82368895644ac6b605873913c20a32f2786d6526",
            reviewed_authority_content_sha256="890a9cef3ce995e7cb7881c035baa3e1e5a4c782f1827847b640c93fb28eafef",
        ),
        _entry(
            topology_id="stage_a_positive_nested_form.v1",
            stage_a_fixture_id="stage-a.positive-nested-form.v1",
            stage_a_authority_schema="kb_creator.pdf_raw.RawAtomProvenanceAuthority.v1",
            stage_a_authority_content_sha256="8726e5d36b7acba9d96eacdcd62a57da00d7f4cfdd4df79cd6c63106d2e353e7",
            stage_a_authority_inventory_sha256="f296a28a72e509f47fe294217492cc463375c30144f8deab57fd7b4c85678b21",
            stage_a_fixture_binding_sha256="9b0f9f382e7926e3447072fa9340c38dd93531302e4294a14d8436eeacdf1d0a",
            positive_topology_assertion_sha256="a82adc738fd89394e80a607df46f7775a1967f874267f3b0289e7e64829d3d0f",
            independent_stage_a_review_kind="fixture_topology_acceptance",
            independent_stage_a_review_decision="accept",
            independent_stage_a_review_content_sha256="136489ff1892bb27b8425806a1972809d03ce5e5e22f42b6a9f1bdfeca1cc503",
            reviewed_authority_content_sha256="8726e5d36b7acba9d96eacdcd62a57da00d7f4cfdd4df79cd6c63106d2e353e7",
        ),
    )
    draft = page_proof._RequiredStageATopologyInventory(
        schema="PageProofRequiredStageATopologyInventory.v1",
        required_topology_ids=("stage_a_positive_two_column.v1", "stage_a_positive_nested_form.v1"),
        entries=rows,
        entry_count=2,
        inventory_sha256="0" * 64,
        content_sha256="0" * 64,
    )
    sealed = replace(draft, inventory_sha256=page_proof._inventory_sha256(draft.required_topology_ids, rows))
    sealed = replace(sealed, content_sha256=page_proof._inventory_content_sha256(sealed))
    return sealed, page_proof._inventory_primitives(sealed)


def _private_fixture_rows():
    return (
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


def _private_expected(rows):
    return tuple(page_proof._fixture_admission_primitives(row) for row in rows)


def _review_candidate_raw(binding_sha256: str) -> bytes:
    payload = {
        "schema": "kb_creator.pdf_raw.PageBlockEvidenceCandidateV1",
        "fixture_binding_sha256": binding_sha256,
        "required_topology_inventory_content_sha256": _PRIVATE_TOPOLOGY_DIGEST,
    }
    payload["content_sha256"] = page_proof._sha256(_canonical_json(payload))
    return _canonical_json(payload)


def _review_attestation_raw(binding_sha256: str, decision: str = "accept") -> bytes:
    payload = {
        "schema": "kb_creator.pdf_raw.ReviewedPageBlockEvidenceV1",
        "fixture_binding_sha256": binding_sha256,
        "required_topology_inventory_content_sha256": _PRIVATE_TOPOLOGY_DIGEST,
        "decision": decision,
    }
    payload["content_sha256"] = page_proof._sha256(_canonical_json(payload))
    return _canonical_json(payload)


def _registry_rows_for_review():
    rows = list(_private_fixture_rows())
    candidate_raw = _review_candidate_raw(rows[0].binding_sha256)
    rows[0] = replace(rows[0], expected_candidate_sha256=page_proof._sha256(candidate_raw))
    return tuple(rows), candidate_raw


class _AuthoritySubclass(page_proof.RawAtomProvenanceAuthorityV1):
    pass


def _fake_authority_instance(authority_type):
    return object.__new__(authority_type)


@pytest.fixture
def _active_topology(monkeypatch):
    inventory, expected = _private_valid_inventory()
    monkeypatch.setattr(page_proof, "_PRODUCTION_REQUIRED_STAGE_A_TOPOLOGY_INVENTORY", inventory)
    monkeypatch.setattr(page_proof, "_PRODUCTION_EXPECTED_TOPOLOGY_PRIMITIVES", expected)
    return inventory, expected


def _activate_fixture_registry(monkeypatch, rows):
    monkeypatch.setattr(page_proof, "_PRODUCTION_FIXTURE_ADMISSION", rows)
    monkeypatch.setattr(page_proof, "_PRODUCTION_EXPECTED_FIXTURE_ADMISSION_PRIMITIVES", _private_expected(rows))


def test_fixture_admission_projection_excludes_expected_output_hashes():
    projection = page_proof._fixture_admission_projection(_private_fixture_rows()[0])
    assert "expected_candidate_sha256" not in projection
    assert "expected_reviewed_ledger_sha256" not in projection
    assert projection["binding_sha256"] == _private_fixture_rows()[0].binding_sha256


def test_candidate_wrapper_rejects_unknown_missing_duplicate_mistyped_and_noncanonical_json():
    valid = _review_candidate_raw(_private_fixture_rows()[0].binding_sha256)
    candidate = page_proof._candidate_wrapper_from_raw(valid)
    assert type(candidate) is page_proof._PageBlockEvidenceCandidateWrapper
    with pytest.raises(RawPdfError, match=f"^{_CANDIDATE_SCHEMA_ERROR}$"):
        page_proof._candidate_wrapper_from_raw(b'{"schema":"kb_creator.pdf_raw.PageBlockEvidenceCandidateV1","schema":"kb_creator.pdf_raw.PageBlockEvidenceCandidateV1"}')
    with pytest.raises(RawPdfError, match=f"^{_CANDIDATE_SCHEMA_ERROR}$"):
        page_proof._candidate_wrapper_from_raw(_canonical_json({
            "schema": "kb_creator.pdf_raw.PageBlockEvidenceCandidateV1",
            "pre_visual_binding_sha256": _private_fixture_rows()[0].binding_sha256,
            "content_sha256": "0" * 64,
        }))
    with pytest.raises(RawPdfError, match=f"^{_CANDIDATE_SCHEMA_ERROR}$"):
        page_proof._candidate_wrapper_from_raw(_canonical_json({
            "schema": "kb_creator.pdf_raw.PageBlockEvidenceCandidateV1",
            "pre_visual_binding_sha256": _private_fixture_rows()[0].binding_sha256,
            "required_topology_inventory_content_sha256": _PRIVATE_TOPOLOGY_DIGEST,
            "content_sha256": candidate.content_sha256,
            "extra": "x",
        }))
    with pytest.raises(RawPdfError, match=f"^{_CANDIDATE_SCHEMA_ERROR}$"):
        page_proof._candidate_wrapper_from_raw(_canonical_json({
            "schema": "kb_creator.pdf_raw.PageBlockEvidenceCandidateV1",
            "pre_visual_binding_sha256": 1,
            "required_topology_inventory_content_sha256": _PRIVATE_TOPOLOGY_DIGEST,
            "content_sha256": candidate.content_sha256,
        }))
    with pytest.raises(RawPdfError, match=f"^{_CANDIDATE_SCHEMA_ERROR}$"):
        page_proof._candidate_wrapper_from_raw(b'{"required_topology_inventory_content_sha256":"' + _PRIVATE_TOPOLOGY_DIGEST.encode("ascii") + b'","schema":"kb_creator.pdf_raw.PageBlockEvidenceCandidateV1","pre_visual_binding_sha256":"' + _private_fixture_rows()[0].binding_sha256.encode("ascii") + b'","content_sha256":"' + candidate.content_sha256.encode("ascii") + b'"}')


def test_review_wrapper_rejects_unknown_missing_duplicate_mistyped_enum_and_noncanonical_json():
    valid = _review_attestation_raw(_private_fixture_rows()[0].binding_sha256)
    review = page_proof._review_wrapper_from_raw(valid)
    assert type(review) is page_proof._ReviewedPageBlockEvidenceWrapper
    with pytest.raises(RawPdfError, match=f"^{_REVIEW_SCHEMA_ERROR}$"):
        page_proof._review_wrapper_from_raw(b'{"schema":"kb_creator.pdf_raw.ReviewedPageBlockEvidenceV1","schema":"kb_creator.pdf_raw.ReviewedPageBlockEvidenceV1"}')
    with pytest.raises(RawPdfError, match=f"^{_REVIEW_SCHEMA_ERROR}$"):
        page_proof._review_wrapper_from_raw(_canonical_json({
            "schema": "kb_creator.pdf_raw.ReviewedPageBlockEvidenceV1",
            "pre_visual_binding_sha256": _private_fixture_rows()[0].binding_sha256,
            "required_topology_inventory_content_sha256": _PRIVATE_TOPOLOGY_DIGEST,
            "content_sha256": "0" * 64,
        }))
    with pytest.raises(RawPdfError, match=f"^{_REVIEW_SCHEMA_ERROR}$"):
        page_proof._review_wrapper_from_raw(_canonical_json({
            "schema": "kb_creator.pdf_raw.ReviewedPageBlockEvidenceV1",
            "pre_visual_binding_sha256": _private_fixture_rows()[0].binding_sha256,
            "required_topology_inventory_content_sha256": _PRIVATE_TOPOLOGY_DIGEST,
            "decision": "maybe",
            "content_sha256": review.content_sha256,
        }))
    with pytest.raises(RawPdfError, match=f"^{_REVIEW_SCHEMA_ERROR}$"):
        page_proof._review_wrapper_from_raw(b'{"required_topology_inventory_content_sha256":"' + _PRIVATE_TOPOLOGY_DIGEST.encode("ascii") + b'","schema":"kb_creator.pdf_raw.ReviewedPageBlockEvidenceV1","pre_visual_binding_sha256":"' + _private_fixture_rows()[0].binding_sha256.encode("ascii") + b'","decision":"accept","content_sha256":"' + review.content_sha256.encode("ascii") + b'"}')


def test_wrapper_capability_immutability_copy_and_pickle_containment():
    candidate = page_proof._candidate_wrapper_from_raw(_review_candidate_raw(_private_fixture_rows()[0].binding_sha256))
    review = page_proof._review_wrapper_from_raw(_review_attestation_raw(_private_fixture_rows()[0].binding_sha256))
    with pytest.raises(TypeError):
        page_proof._PageBlockEvidenceCandidateWrapper(object(), b"{}", {})
    with pytest.raises(TypeError):
        page_proof._ReviewedPageBlockEvidenceWrapper(object(), b"{}", {})
    with pytest.raises(AttributeError):
        candidate._content_sha256 = "0" * 64  # type: ignore[attr-defined]
    with pytest.raises(AttributeError):
        review._decision = "reject"  # type: ignore[attr-defined]
    with pytest.raises(TypeError):
        copy.copy(candidate)
    with pytest.raises(TypeError):
        copy.deepcopy(candidate)
    with pytest.raises(TypeError):
        pickle.dumps(candidate)
    with pytest.raises(TypeError):
        copy.copy(review)
    with pytest.raises(TypeError):
        copy.deepcopy(review)
    with pytest.raises(TypeError):
        pickle.dumps(review)


def test_exact_authority_type_gate_rejects_subclass_type_confusion():
    with pytest.raises(RawPdfError, match=f"^{_AUTHORITY_ERROR}$"):
        page_proof._require_authority_type(object())
    with pytest.raises(RawPdfError, match=f"^{_AUTHORITY_ERROR}$"):
        page_proof._require_authority_type(_fake_authority_instance(_AuthoritySubclass))


def test_public_routes_remain_coverage_first_while_topology_is_incomplete():
    with pytest.raises(RawPdfError, match=f"^{_COVERAGE_ERROR}$"):
        page_proof.derive_fixture_page_block_ledger_v1(object(), object(), object(), object())
    with pytest.raises(RawPdfError, match=f"^{_COVERAGE_ERROR}$"):
        page_proof.review_fixture_page_block_ledger_v1(object(), object(), object())
    with pytest.raises(RawPdfError, match=f"^{_COVERAGE_ERROR}$"):
        page_proof.replay_fixture_page_block_ledger_v1(object(), object(), object(), object(), object(), object())


def test_public_precedence_with_complete_topology_but_inactive_registry(_active_topology):
    with pytest.raises(RawPdfError, match=f"^{_REGISTRY_ERROR}$"):
        page_proof.derive_fixture_page_block_ledger_v1(object(), b"x", b"y", b"z")


def test_derive_and_replay_ingress_and_authority_precedence(monkeypatch, _active_topology):
    _activate_fixture_registry(monkeypatch, _private_fixture_rows())
    with pytest.raises(RawPdfError, match=f"^{_INGRESS_ERROR}$"):
        page_proof.derive_fixture_page_block_ledger_v1(object(), bytearray(leaves.TWO_COLUMN[1]), leaves.TWO_COLUMN[2], leaves.TWO_COLUMN[3])  # type: ignore[arg-type]
    with pytest.raises(RawPdfError, match=f"^{_AUTHORITY_ERROR}$"):
        page_proof.derive_fixture_page_block_ledger_v1(object(), leaves.TWO_COLUMN[1], leaves.TWO_COLUMN[2], leaves.TWO_COLUMN[3])
    with pytest.raises(RawPdfError, match=f"^{_AUTHORITY_ERROR}$"):
        page_proof.replay_fixture_page_block_ledger_v1(object(), leaves.TWO_COLUMN[1], leaves.TWO_COLUMN[2], leaves.TWO_COLUMN[3], _review_attestation_raw(_private_fixture_rows()[0].binding_sha256), b"expected")


def test_review_and_replay_schema_precedence_and_boundary_stop(monkeypatch, _active_topology):
    rows, candidate_raw = _registry_rows_for_review()
    _activate_fixture_registry(monkeypatch, rows)
    valid_review = _review_attestation_raw(rows[0].binding_sha256)
    with pytest.raises(RawPdfError, match=f"^{_ADMISSION_ERROR}$"):
        page_proof.review_fixture_page_block_ledger_v1(b'{"schema":"kb_creator.pdf_raw.PageBlockEvidenceCandidateV1","schema":"kb_creator.pdf_raw.PageBlockEvidenceCandidateV1"}', leaves.TWO_COLUMN[3], b"{}")
    with pytest.raises(RawPdfError, match=f"^{_REVIEW_SCHEMA_ERROR}$"):
        page_proof.review_fixture_page_block_ledger_v1(candidate_raw, leaves.TWO_COLUMN[3], b'{"schema":"kb_creator.pdf_raw.ReviewedPageBlockEvidenceV1","schema":"kb_creator.pdf_raw.ReviewedPageBlockEvidenceV1"}')
    with pytest.raises(RawPdfError, match=f"^{_BOUNDARY_ERROR}$"):
        page_proof.review_fixture_page_block_ledger_v1(candidate_raw, leaves.TWO_COLUMN[3], valid_review)
    authority = _fake_authority_instance(page_proof.RawAtomProvenanceAuthorityV1)
    with pytest.raises(RawPdfError, match=f"^{_REVIEW_SCHEMA_ERROR}$"):
        page_proof.replay_fixture_page_block_ledger_v1(authority, leaves.TWO_COLUMN[1], leaves.TWO_COLUMN[2], leaves.TWO_COLUMN[3], b'{"schema":"kb_creator.pdf_raw.ReviewedPageBlockEvidenceV1","schema":"kb_creator.pdf_raw.ReviewedPageBlockEvidenceV1"}', b"expected")
    with pytest.raises(RawPdfError, match=f"^{_EXPECTED_LEDGER_SCHEMA_ERROR}$"):
        page_proof.replay_fixture_page_block_ledger_v1(authority, leaves.TWO_COLUMN[1], leaves.TWO_COLUMN[2], leaves.TWO_COLUMN[3], valid_review, bytearray(b"expected"))  # type: ignore[arg-type]
