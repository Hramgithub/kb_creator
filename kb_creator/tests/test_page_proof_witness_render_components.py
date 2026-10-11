import binascii
import json

import pytest

from kb_creator.pdf_raw import page_proof
from kb_creator.pdf_raw.errors import RawPdfError
from kb_creator.tests import _page_proof_fixture_leaves as leaves


_PRIVATE_TOPOLOGY_DIGEST = "4d3683f15ae64b4d03e51211755f2b3580e112e35bce4bf8c69efa29645dd3b4"
_WITNESS_SCHEMA_ERROR = "page_proof_witness_schema_invalid"
_RENDER_ERROR = "page_proof_render_invalid"
_GEOMETRY_ERROR = "page_proof_geometry_invalid"


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
            0,
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
            1,
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
            2,
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


def _mutate_witness(raw: bytes, mutator) -> bytes:
    value = json.loads(raw.decode("utf-8"))
    mutator(value)
    return _canonical_json(value)


def _mutate_render(raw: bytes, index: int, value: int) -> bytes:
    data = bytearray(raw)
    data[index] = value
    return bytes(data)


def _reseal_witness_for_render(raw: bytes, render_raw: bytes) -> bytes:
    value = json.loads(raw.decode("utf-8"))
    value["render_identity"]["render_png_byte_length"] = len(render_raw)
    value["render_identity"]["render_png_sha256"] = page_proof._sha256(render_raw)
    value["content_sha256"] = page_proof._sha256(_canonical_json({key: item for key, item in value.items() if key != "content_sha256"}))
    return _canonical_json(value)


def _u32(raw: bytes, offset: int) -> int:
    return int.from_bytes(raw[offset:offset + 4], "big")


def _replace_idat_data(raw: bytes, new_idat: bytes) -> bytes:
    offset = 8
    output = bytearray(raw[:8])
    replaced = False
    while offset < len(raw):
        length = _u32(raw, offset)
        chunk_type = raw[offset + 4:offset + 8]
        data_start = offset + 8
        data_end = data_start + length
        crc_end = data_end + 4
        chunk_data = new_idat if chunk_type == b"IDAT" and not replaced else raw[data_start:data_end]
        if chunk_type == b"IDAT":
            replaced = True
        output.extend(len(chunk_data).to_bytes(4, "big"))
        output.extend(chunk_type)
        output.extend(chunk_data)
        output.extend((binascii.crc32(chunk_type + chunk_data) & 0xFFFFFFFF).to_bytes(4, "big"))
        offset = crc_end
    return bytes(output)


def _append_after_iend(raw: bytes, suffix: bytes) -> bytes:
    return raw + suffix


def test_positive_literal_witness_and_render_leaves_have_independent_metadata_and_normalize():
    for row, witness_raw, render_raw, metadata_index in _case_rows():
        witness_length, render_length, crosscheck_length = leaves.RENDER_MECHANICS_V1_LENGTHS[metadata_index]
        witness_sha, render_sha, crosscheck_sha = leaves.RENDER_MECHANICS_V1_SHA256[metadata_index]
        assert len(witness_raw) == witness_length
        assert page_proof._sha256(witness_raw) == witness_sha
        assert len(render_raw) == render_length
        assert page_proof._sha256(render_raw) == render_sha
        assert row.independent_visual_crosscheck_byte_length == crosscheck_length
        assert row.independent_visual_crosscheck_sha256 == crosscheck_sha
        normalized = page_proof._normalize_fixture_witness_render_components(
            _authority_for(row, witness_raw),
            witness_raw,
            render_raw,
            row,
        )
        assert normalized["render_identity"]["render_png_sha256"] == render_sha
        assert len(normalized["visual_components"]) == len(normalized["atom_geometry_rows"])


def test_malformed_png_signature_chunk_filter_and_dimensions_fail_closed():
    row, witness_raw, render_raw, _ = _case_rows()[0]
    authority = _authority_for(row, witness_raw)
    bad_signature = _mutate_render(render_raw, 1, ord("A"))
    bad_chunk = _mutate_render(render_raw, 12, ord("J"))
    bad_filter = _mutate_render(render_raw, 50, 5)
    with pytest.raises(RawPdfError, match=f"^{_RENDER_ERROR}$"):
        page_proof._normalize_fixture_witness_render_components(authority, _reseal_witness_for_render(witness_raw, bad_signature), bad_signature, row)
    with pytest.raises(RawPdfError, match=f"^{_RENDER_ERROR}$"):
        page_proof._normalize_fixture_witness_render_components(authority, _reseal_witness_for_render(witness_raw, bad_chunk), bad_chunk, row)
    with pytest.raises(RawPdfError, match=f"^{_RENDER_ERROR}$"):
        page_proof._normalize_fixture_witness_render_components(authority, _reseal_witness_for_render(witness_raw, bad_filter), bad_filter, row)
    bad_witness = _mutate_witness(witness_raw, lambda value: value["render_identity"].__setitem__("png_width", 99))
    with pytest.raises(RawPdfError, match=f"^{_RENDER_ERROR}$"):
        page_proof._normalize_fixture_witness_render_components(authority, bad_witness, render_raw, row)
    assert page_proof._normalize_fixture_witness_render_components(authority, witness_raw, render_raw, row)


def test_affine_decimal_and_bbox_target_only_failures_repair_positive():
    row, witness_raw, render_raw, _ = _case_rows()[0]
    authority = _authority_for(row, witness_raw)
    bad_decimal = _mutate_witness(witness_raw, lambda value: value["render_identity"]["pdf_to_px_affine"].__setitem__(0, "1.0"))
    with pytest.raises(RawPdfError, match=f"^{_WITNESS_SCHEMA_ERROR}$"):
        page_proof._normalize_fixture_witness_render_components(authority, bad_decimal, render_raw, row)
    assert page_proof._parse_canonical_decimal("0.5", _WITNESS_SCHEMA_ERROR) == (1, 2)
    assert page_proof._parse_canonical_decimal("-1.25", _WITNESS_SCHEMA_ERROR) == (-5, 4)
    with pytest.raises(RawPdfError, match=f"^{_WITNESS_SCHEMA_ERROR}$"):
        page_proof._parse_canonical_decimal("01.5", _WITNESS_SCHEMA_ERROR)
    with pytest.raises(RawPdfError, match=f"^{_WITNESS_SCHEMA_ERROR}$"):
        page_proof._parse_canonical_decimal("1.0", _WITNESS_SCHEMA_ERROR)
    bad_bbox = _mutate_witness(witness_raw, lambda value: value["atom_geometry_rows"][0].__setitem__("bbox_px", [0, 0, 0, 3]))
    with pytest.raises(RawPdfError, match=f"^{_GEOMETRY_ERROR}$"):
        page_proof._normalize_fixture_witness_render_components(authority, bad_bbox, render_raw, row)
    bad_projection = _mutate_witness(witness_raw, lambda value: value["atom_geometry_rows"][0]["bbox_pdf"].__setitem__(2, "2"))
    with pytest.raises(RawPdfError, match=f"^{_GEOMETRY_ERROR}$"):
        page_proof._normalize_fixture_witness_render_components(authority, bad_projection, render_raw, row)
    assert page_proof._normalize_fixture_witness_render_components(authority, witness_raw, render_raw, row)


def test_mask_pixel_component_order_and_ownership_failures_repair_positive():
    row, witness_raw, render_raw, _ = _case_rows()[1]
    authority = _authority_for(row, witness_raw)
    bad_mask = _mutate_witness(witness_raw, lambda value: value["visual_components"][0].__setitem__("mask_rle_b64", "AQE="))
    with pytest.raises(RawPdfError, match=f"^{_RENDER_ERROR}$"):
        page_proof._normalize_fixture_witness_render_components(authority, bad_mask, render_raw, row)
    bad_pixel_count = _mutate_witness(witness_raw, lambda value: value["visual_components"][0].__setitem__("pixel_count", 5))
    with pytest.raises(RawPdfError, match=f"^{_RENDER_ERROR}$"):
        page_proof._normalize_fixture_witness_render_components(authority, bad_pixel_count, render_raw, row)
    bad_order = _mutate_witness(witness_raw, lambda value: value["visual_components"].reverse())
    with pytest.raises(RawPdfError, match=f"^{_RENDER_ERROR}$"):
        page_proof._normalize_fixture_witness_render_components(authority, bad_order, render_raw, row)
    bad_owner = _mutate_witness(witness_raw, lambda value: value["atom_geometry_rows"][1].__setitem__("component_ids", [value["atom_geometry_rows"][0]["component_ids"][0]]))
    with pytest.raises(RawPdfError, match=f"^{_GEOMETRY_ERROR}$"):
        page_proof._normalize_fixture_witness_render_components(authority, bad_owner, render_raw, row)
    assert page_proof._normalize_fixture_witness_render_components(authority, witness_raw, render_raw, row)


def test_png_and_zlib_terminal_trailing_bytes_fail_closed_and_repair():
    row, witness_raw, render_raw, _ = _case_rows()[0]
    authority = _authority_for(row, witness_raw)
    trailing_png = _append_after_iend(render_raw, b"\x00")
    with pytest.raises(RawPdfError, match=f"^{_RENDER_ERROR}$"):
        page_proof._normalize_fixture_witness_render_components(
            authority,
            _reseal_witness_for_render(witness_raw, trailing_png),
            trailing_png,
            row,
        )
    idat_length = _u32(render_raw, 33)
    idat_start = 41
    idat_end = idat_start + idat_length
    trailing_zlib = _replace_idat_data(render_raw, render_raw[idat_start:idat_end] + b"\x00")
    with pytest.raises(RawPdfError, match=f"^{_RENDER_ERROR}$"):
        page_proof._normalize_fixture_witness_render_components(
            authority,
            _reseal_witness_for_render(witness_raw, trailing_zlib),
            trailing_zlib,
            row,
        )
    assert page_proof._normalize_fixture_witness_render_components(authority, witness_raw, render_raw, row)


def test_missing_and_malformed_geometry_rows_fail_closed_and_repair():
    row, witness_raw, render_raw, _ = _case_rows()[2]
    authority = _authority_for(row, witness_raw)
    missing_row = _mutate_witness(witness_raw, lambda value: value.__setitem__("atom_geometry_rows", []))
    with pytest.raises(RawPdfError, match=f"^{_GEOMETRY_ERROR}$"):
        page_proof._normalize_fixture_witness_render_components(authority, missing_row, render_raw, row)
    malformed_status = _mutate_witness(witness_raw, lambda value: value["atom_geometry_rows"][0].__setitem__("geometry_status", "missing"))
    with pytest.raises(RawPdfError, match=f"^{_GEOMETRY_ERROR}$"):
        page_proof._normalize_fixture_witness_render_components(authority, malformed_status, render_raw, row)
    wrong_atom_binding = _mutate_witness(witness_raw, lambda value: value["atom_geometry_rows"][0].__setitem__("atom_row_id", "other"))
    with pytest.raises(RawPdfError, match=f"^{_GEOMETRY_ERROR}$"):
        page_proof._normalize_fixture_witness_render_components(authority, wrong_atom_binding, render_raw, row)
    assert page_proof._normalize_fixture_witness_render_components(authority, witness_raw, render_raw, row)
