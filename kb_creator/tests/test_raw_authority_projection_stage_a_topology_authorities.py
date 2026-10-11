"""Focused synthetic two-column raw-paint authority checks; no page proof."""
import copy
import json
import hashlib
from dataclasses import replace

import pytest

from kb_creator.pdf_raw import raw_authority_projection as stage_a
from kb_creator.pdf_raw.errors import RawPdfError
from kb_creator.pdf_raw.raw_authority_projection import (
    project_stage_a_raw_authority,
    replay_stage_a_raw_authority,
)


def _row():
    return stage_a._FIXTURES[2]


def _artifact():
    row = _row()
    return json.loads(project_stage_a_raw_authority(row.fixture_id, row.pdf, row.profile, row.selector).canonical_bytes())


def _nested_row():
    return stage_a._FIXTURES[3]


def _nested_artifact():
    row = _nested_row()
    return json.loads(project_stage_a_raw_authority(row.fixture_id, row.pdf, row.profile, row.selector).canonical_bytes())


def _reseal_nested_artifact(artifact, *, refresh_glyph_atom_ids=True):
    """Keep every artifact seal valid while one topology fact is adversarial."""
    old_atom_ids = [atom["atom_id"] for atom in artifact["atoms"]]
    for group, kind in (("frames", "frame"), ("invocations", "invocation"), ("atoms", "atom")):
        for ordinal, item in enumerate(artifact[group]):
            item["ordinal"] = ordinal
            stage_a._seal_row(kind, item)
    if refresh_glyph_atom_ids:
        atom_ids = {old: item["atom_id"] for old, item in zip(old_atom_ids, artifact["atoms"])}
        for glyph in artifact["glyphs"]:
            glyph["atom_id"] = atom_ids.get(glyph["atom_id"], glyph["atom_id"])
    for ordinal, glyph in enumerate(artifact["glyphs"]):
        glyph["ordinal"] = ordinal
        stage_a._seal_row("glyph", glyph)
    counts = {f"{name[:-1]}_count": len(artifact[name]) for name in ("objects", "streams", "tokens", "frames", "resolutions", "invocations", "atoms", "glyphs")}
    inventory = {"counts": counts, **{f"{name}_row_sha256": [item["row_sha256"] for item in artifact[name]] for name in ("objects", "streams", "tokens", "frames", "resolutions", "invocations", "atoms", "glyphs")}}
    artifact["counts"] = counts
    artifact["inventory_sha256"] = stage_a._sha(stage_a._canonical(inventory))
    artifact["content_sha256"] = stage_a._sha(stage_a._canonical({key: value for key, value in artifact.items() if key != "content_sha256"}))
    return artifact


def _private_expected_row_for_artifact(row, artifact):
    return replace(
        row,
        expected_inventory_sha256=artifact["inventory_sha256"],
        expected_content_sha256=artifact["content_sha256"],
    )


def test_nested_form_adapter_normalizes_existing_bytes_only_form_records_without_ctm():
    assert len(stage_a._PDF_NESTED_FORM) == 1463
    assert hashlib.sha256(stage_a._PDF_NESTED_FORM).hexdigest() == "1e6b3313c74fb3275e0a6413cbc5d5733b79cd0642a08069686e47d3cddbee1d"
    replay = stage_a.extract_raw_pdf_page_atoms(
        stage_a._PDF_NESTED_FORM,
        {"page_object_ref": [3, 0], "page_tree_route": [[2, 0], [3, 0]]},
        dict(stage_a._PAGE_PROFILE),
    )
    row = stage_a._FixtureRow(
        b"stage-a.positive-nested-form.v1", b"", b"", b"", 0, 0, 0, 0,
        "", "", "", "", "", topology_id="stage_a_positive_nested_form.v1",
    )
    normalized = stage_a._adapt_nested_form_replay(row, replay)
    assert [stream["root_contents_ordinal"] for stream in normalized["streams"]] == [0, None, None]
    assert [atom["operator_kind"] for atom in normalized["atoms"]] == ["text_show", "form_do", "text_show", "form_do", "text_show", "text_show", "text_show"]
    assert [atom["glyph_ids"] for atom in normalized["atoms"] if atom["operator_kind"] == "form_do"] == [[], []]
    assert [invocation["token_id"] for invocation in normalized["invocations"]] == [["5:0", 8], ["7:0", 8]]
    assert all("effective_ctm" not in item for item in (*normalized["atoms"], *normalized["invocations"]))
    assert [resolution["widths_span"] is None for resolution in normalized["resolutions"]] == [False, True, False, True, False]


def test_nested_form_replays_literal_raw_invocation_authority_without_ctm():
    row = _nested_row()
    authority = project_stage_a_raw_authority(row.fixture_id, row.pdf, row.profile, row.selector)
    replay = replay_stage_a_raw_authority(row.fixture_id, row.pdf, row.profile, row.selector, authority.canonical_bytes())
    artifact = json.loads(authority.canonical_bytes())
    assertion = json.loads(row.positive_topology_assertion_raw)
    assert replay.canonical_bytes() == authority.canonical_bytes()
    assert artifact["inventory_sha256"] == row.expected_inventory_sha256
    assert artifact["content_sha256"] == row.expected_content_sha256
    assert stage_a._nested_form_assertion(artifact, row) == row.positive_topology_assertion_raw
    assert [base64_decode(item["code_b64"]) for item in artifact["glyphs"]] == [b"P", b"C", b"N", b"D", b"Q"]
    assert assertion["facts"]["continuity_constraints"]["depth_first_paint_order_required"] is True
    assert assertion["facts"]["stage_a_claim_boundary"] == {"geometry": "not_proved_stage_a", "visibility": "not_proved_stage_a", "semantic_blocks": "not_proved_stage_a", "reading_order": "not_proved_stage_a"}
    assert all("effective_ctm" not in item for item in (*artifact["atoms"], *artifact["invocations"]))


@pytest.mark.parametrize("target", ("frame_parent", "invocation_target", "paint_order", "glyph_owner"))
def test_nested_form_target_only_raw_invocation_validator_rejects(target):
    artifact = copy.deepcopy(_nested_artifact())
    if target == "frame_parent":
        artifact["frames"][2]["parent_frame_id"] = "page-3-0-0"
    elif target == "invocation_target":
        artifact["invocations"][1]["target_frame_id"] = "page-3-0-0"
    elif target == "paint_order":
        artifact["atoms"][4]["frame_id"] = "form-7-0-1"
    else:
        artifact["glyphs"][2]["atom_id"] = artifact["atoms"][5]["atom_id"]
    _reseal_nested_artifact(artifact, refresh_glyph_atom_ids=target != "glyph_owner")
    surrogate = _private_expected_row_for_artifact(_nested_row(), artifact)
    with pytest.raises(RawPdfError, match="^raw_interpreter_authority_blocked$"):
        stage_a._validate_artifact(artifact, surrogate, replay=True)
    assert stage_a._validate_artifact(_nested_artifact(), _nested_row(), replay=True) == _nested_artifact()


def test_two_column_replays_literal_raw_paint_authority_only():
    row = _row()
    authority = project_stage_a_raw_authority(row.fixture_id, row.pdf, row.profile, row.selector)
    replay = replay_stage_a_raw_authority(row.fixture_id, row.pdf, row.profile, row.selector, authority.canonical_bytes())
    artifact = json.loads(authority.canonical_bytes())
    assertion = json.loads(row.positive_topology_assertion_raw)
    assert replay.canonical_bytes() == authority.canonical_bytes()
    assert artifact["inventory_sha256"] == row.expected_inventory_sha256
    assert artifact["content_sha256"] == row.expected_content_sha256
    assert len(row.positive_topology_assertion_raw) == row.positive_topology_assertion_length
    assert stage_a._sha(row.positive_topology_assertion_raw) == row.positive_topology_assertion_sha256
    assert assertion["positive_topology_assertion_sha256"] == row.positive_topology_facts_sha256
    assert assertion["content_sha256"] == row.positive_topology_content_sha256
    assert stage_a._two_column_assertion(artifact, row) == row.positive_topology_assertion_raw
    assert [base64_decode(item["code_b64"]) for item in artifact["glyphs"]] == [b"A", b"B", b"C", b"D"]
    assert assertion["facts"]["cross_slot_transition"]["from_atom_ordinal"] == 1
    assert assertion["facts"]["cross_slot_transition"]["to_atom_ordinal"] == 2
    assert assertion["facts"]["stage_a_claim_boundary"] == {"geometry": "not_proved_stage_a", "visibility": "not_proved_stage_a", "semantic_blocks": "not_proved_stage_a", "reading_order": "not_proved_stage_a"}
    assert all(atom[key] == "unavailable_stage_a" for atom in artifact["atoms"] for key in ("geometry", "visibility", "semantic_role"))


def base64_decode(value):
    import base64
    return base64.b64decode(value)


@pytest.mark.parametrize("target", ("left", "right", "reversed", "endpoint", "membership"))
def test_two_column_target_only_raw_paint_validator_rejects(target):
    artifact = copy.deepcopy(_artifact())
    if target == "left":
        artifact["atoms"] = artifact["atoms"][1:]
    elif target == "right":
        artifact["atoms"] = artifact["atoms"][:3]
    elif target == "reversed":
        artifact["streams"] = list(reversed(artifact["streams"]))
    elif target == "endpoint":
        artifact["glyphs"][1]["code_b64"] = artifact["glyphs"][0]["code_b64"]
    else:
        artifact["glyphs"][3]["atom_id"] = artifact["glyphs"][2]["atom_id"]
    with pytest.raises(RawPdfError, match="^raw_interpreter_authority_blocked$"):
        stage_a._validate_two_column_rows(artifact, code="raw_interpreter_authority_blocked")


def _private_resealed_different_assertion(row):
    """Change only the expected assertion authority, not the valid artifact."""
    assertion = json.loads(row.positive_topology_assertion_raw)
    assertion["facts"]["cross_slot_transition"]["minimum_text_atoms_per_slot"] = 3
    assertion["positive_topology_assertion_sha256"] = stage_a._sha(
        b"stage-a.positive-topology-facts.v1\0" + stage_a._canonical(assertion["facts"])
    )
    assertion["content_sha256"] = stage_a._sha(
        stage_a._canonical({key: value for key, value in assertion.items() if key != "content_sha256"})
    )
    raw = stage_a._canonical(assertion)
    return replace(
        row,
        positive_topology_assertion_raw=raw,
        positive_topology_assertion_sha256=stage_a._sha(raw),
        positive_topology_assertion_length=len(raw),
        positive_topology_facts_sha256=assertion["positive_topology_assertion_sha256"],
        positive_topology_content_sha256=assertion["content_sha256"],
    )


def _private_resealed_different_nested_assertion(row):
    assertion = json.loads(row.positive_topology_assertion_raw)
    assertion["facts"]["continuity_constraints"]["outer_descendant_interval"] = [2, 4]
    assertion["positive_topology_assertion_sha256"] = stage_a._sha(
        b"stage-a.positive-topology-facts.v1\0" + stage_a._canonical(assertion["facts"])
    )
    assertion["content_sha256"] = stage_a._sha(
        stage_a._canonical({key: value for key, value in assertion.items() if key != "content_sha256"})
    )
    raw = stage_a._canonical(assertion)
    return replace(
        row,
        positive_topology_assertion_raw=raw,
        positive_topology_assertion_sha256=stage_a._sha(raw),
        positive_topology_assertion_length=len(raw),
        positive_topology_facts_sha256=assertion["positive_topology_assertion_sha256"],
        positive_topology_content_sha256=assertion["content_sha256"],
    )


def test_nested_form_replay_rejects_private_fully_resealed_assertion_then_original_repair_passes():
    row = _nested_row()
    artifact = _nested_artifact()
    surrogate = _private_resealed_different_nested_assertion(row)
    with pytest.raises(RawPdfError, match="^raw_interpreter_authority_blocked$"):
        stage_a._validate_artifact(artifact, surrogate, replay=True)
    assert stage_a._validate_artifact(artifact, row, replay=True) == artifact


def test_two_column_replay_rejects_private_fully_resealed_assertion_then_original_repair_passes():
    row = _row()
    artifact = _artifact()
    surrogate = _private_resealed_different_assertion(row)
    # Ordinary raw provenance and every artifact seal are valid first. Only the
    # private assertion differs; restoring the accepted row is the target-only
    # repair and must pass the same full replay validation path.
    with pytest.raises(RawPdfError, match="^raw_interpreter_authority_blocked$"):
        stage_a._validate_artifact(artifact, surrogate, replay=True)
    assert stage_a._validate_artifact(artifact, row, replay=True) == artifact


def test_two_column_assertion_has_closed_non_geometric_boundary_and_registry_cross_pair_fails_pre_open(monkeypatch):
    row = _row()
    artifact = _artifact()
    assertion = json.loads(stage_a._two_column_assertion(artifact, row))
    assertion["facts"]["stage_a_claim_boundary"]["reading_order"] = "accepted"
    assert assertion["facts"]["stage_a_claim_boundary"] != json.loads(stage_a._two_column_assertion(artifact, row))["facts"]["stage_a_claim_boundary"]
    cross = stage_a._FixtureRow(
        row.fixture_id, stage_a._FIXTURES[0].pdf, row.profile, row.selector,
        row.fixture_id_length, stage_a._FIXTURES[0].pdf_length, row.profile_length, row.selector_length,
        row.fixture_id_sha256, stage_a._FIXTURES[0].pdf_sha256, row.profile_sha256, row.selector_sha256,
        stage_a._binding(row.fixture_id, stage_a._FIXTURES[0].pdf, row.profile, row.selector),
        row.expected_inventory_sha256, row.expected_content_sha256, row.topology_id, row.positive_topology_assertion_raw, row.positive_topology_assertion_sha256,
    )
    monkeypatch.setattr(stage_a, "_FIXTURES", (*stage_a._FIXTURES[:2], cross))
    monkeypatch.setattr(stage_a.RawPdfDocument, "open", lambda *_a, **_k: (_ for _ in ()).throw(AssertionError("must not open")))
    with pytest.raises(RawPdfError, match="^raw_interpreter_fixture_registry_invalid$"):
        project_stage_a_raw_authority(row.fixture_id, row.pdf, row.profile, row.selector)
