import ast
import base64
import copy
from dataclasses import replace
import json

import pytest

from kb_creator.pdf_raw import raw_authority_projection as stage_a
from kb_creator.pdf_raw import raw_interpreter_authority as legacy_authority
from kb_creator.pdf_raw.errors import RawPdfError
from kb_creator.pdf_raw.raw_authority_projection import (
    project_stage_a_raw_authority,
    replay_stage_a_raw_authority,
)


_GROUPS = (
    ("objects", "object"),
    ("streams", "stream"),
    ("tokens", "token"),
    ("frames", "frame"),
    ("resolutions", "resolution"),
    ("invocations", "invocation"),
    ("atoms", "atom"),
    ("glyphs", "glyph"),
)
_GROUP_PLURALS = tuple(plural for plural, _ in _GROUPS)
_GROUP_KIND = {plural: kind for plural, kind in _GROUPS}


def _canonical_artifact(authority):
    return stage_a.json.loads(authority.canonical_bytes().decode("utf-8"))


def _token_rows(artifact, stream_id):
    return [token for token in artifact["tokens"] if token["stream_id"] == stream_id]


def _span_dict(pdf_bytes, start, end):
    return {"span": [start, end], "sha256": stage_a._sha(pdf_bytes[start:end])}


def _fixture_pdf(artifact):
    fixture_id = artifact["fixture"]["id"]
    row = next(row for row in stage_a._FIXTURES if row.fixture_id.decode("ascii") == fixture_id)
    return row.pdf


def _set_stream_tokens(artifact, *, sync_nested_tokens=True):
    for stream in artifact["streams"]:
        tokens = _token_rows(artifact, stream["stream_id"])
        stream["token_count"] = len(tokens)
        if sync_nested_tokens:
            stream["tokens"] = [copy.deepcopy(token) for token in tokens]


def _reseal(artifact, *, sync_nested_tokens=True):
    _set_stream_tokens(artifact, sync_nested_tokens=sync_nested_tokens)
    for plural, kind in _GROUPS:
        for ordinal, row in enumerate(artifact[plural]):
            row["ordinal"] = ordinal
            unsigned = {key: value for key, value in row.items() if key not in {"row_id", "row_sha256"}}
            row["row_id"] = stage_a._sha(
                (f"stage-a.row-id.v1\0{kind}\0").encode("ascii") + stage_a._canonical(unsigned)
            )
            row["row_sha256"] = stage_a._sha(
                (f"stage-a.row.v1\0{kind}\0").encode("ascii")
                + stage_a._canonical({**unsigned, "row_id": row["row_id"]})
            )
    counts = {f"{plural[:-1]}_count": len(artifact[plural]) for plural in _GROUP_PLURALS}
    inventory = {
        "counts": counts,
        **{f"{plural}_row_sha256": [row["row_sha256"] for row in artifact[plural]] for plural in _GROUP_PLURALS},
    }
    artifact["counts"] = counts
    artifact["inventory_sha256"] = stage_a._sha(stage_a._canonical(inventory))
    artifact["content_sha256"] = stage_a._sha(
        stage_a._canonical({key: value for key, value in artifact.items() if key != "content_sha256"})
    )
    return stage_a._canonical(artifact)


def _assert_no_open_or_extract(monkeypatch):
    opens = []
    extracts = []

    def fake_open(*args, **kwargs):
        opens.append((args, kwargs))
        raise AssertionError("RawPdfDocument.open must not be called for malformed replay")

    def fake_extract(*args, **kwargs):
        extracts.append((args, kwargs))
        raise AssertionError("extract_raw_pdf_page_atoms must not be called for malformed replay")

    monkeypatch.setattr(stage_a.RawPdfDocument, "open", fake_open)
    monkeypatch.setattr(stage_a, "extract_raw_pdf_page_atoms", fake_extract)
    return opens, extracts


def _assert_surrogate_semantic_rejection(row, artifact_raw):
    """Prove malformed structure is rejected without relying on final pins."""
    parsed = json.loads(artifact_raw.decode("utf-8"))
    surrogate = replace(
        row,
        expected_inventory_sha256=parsed["inventory_sha256"],
        expected_content_sha256=parsed["content_sha256"],
    )
    with pytest.raises(RawPdfError, match="^raw_interpreter_authority_blocked$"):
        stage_a._validate_artifact(parsed, surrogate, replay=True)


def _assert_surrogate_first_failure_is_target_violation(row, artifact_raw, repair):
    """Prove the surrogate fails only until the intended target violation is repaired."""
    parsed = json.loads(artifact_raw.decode("utf-8"))
    blocked_surrogate = replace(
        row,
        expected_inventory_sha256=parsed["inventory_sha256"],
        expected_content_sha256=parsed["content_sha256"],
    )
    with pytest.raises(RawPdfError, match="^raw_interpreter_authority_blocked$"):
        stage_a._validate_artifact(parsed, blocked_surrogate, replay=True)
    repair(parsed)
    repaired_raw = _reseal(parsed)
    repaired = json.loads(repaired_raw.decode("utf-8"))
    repaired_surrogate = replace(
        row,
        expected_inventory_sha256=repaired["inventory_sha256"],
        expected_content_sha256=repaired["content_sha256"],
    )
    assert stage_a._validate_artifact(repaired, repaired_surrogate, replay=True) == repaired


def _source_row():
    return [
        (row, _canonical_artifact(project_stage_a_raw_authority(row.fixture_id, row.pdf, row.profile, row.selector)))
        for row in stage_a._FIXTURES
    ]


def _json_rewrite(artifact_raw, edit):
    parsed = json.loads(artifact_raw.decode("utf-8"))
    edit(parsed)
    return stage_a._canonical(parsed)


def _mutated_payload_bytes(stream, artifact):
    pdf = _fixture_pdf(artifact)
    start, end = stream["encoded_payload_span"]["span"]
    payload = pdf[start:end]
    mutated = payload[:-1] + (b"X" if payload[-1:] != b"X" else b"Y")
    return mutated


def _rebuild_root_only(parsed):
    counts = {f"{plural[:-1]}_count": len(parsed[plural]) for plural in _GROUP_PLURALS}
    inventory = {
        "counts": counts,
        **{f"{plural}_row_sha256": [row["row_sha256"] for row in parsed[plural]] for plural in _GROUP_PLURALS},
    }
    parsed["counts"] = counts
    parsed["inventory_sha256"] = stage_a._sha(stage_a._canonical(inventory))
    parsed["content_sha256"] = stage_a._sha(
        stage_a._canonical({key: value for key, value in parsed.items() if key != "content_sha256"})
    )
    return stage_a._canonical(parsed)


def _append_exact_sealed_clone(artifact_raw, plural):
    parsed = json.loads(artifact_raw.decode("utf-8"))
    parsed[plural].append(copy.deepcopy(parsed[plural][0]))
    return _rebuild_root_only(parsed)


def _first_token_id(artifact, ordinal):
    token = next(token for token in artifact["tokens"] if token["token_ordinal"] == ordinal)
    return [token["stream_id"], token["token_ordinal"]]


def _add_child_frame(artifact, suffix):
    root = artifact["frames"][0]
    child = copy.deepcopy(root)
    child["frame_id"] = f"{root['frame_id']}-{suffix}"
    child["parent_frame_id"] = root["frame_id"]
    artifact["frames"].append(child)
    return child


def _build_invocation_row(artifact, suffix, target_frame_id, token_ordinal):
    root_frame = artifact["frames"][0]["frame_id"]
    return {
        "kind": "invocation",
        "ordinal": len(artifact["invocations"]),
        "invocation_id": f"invoke-{suffix}",
        "parent_frame_id": root_frame,
        "target_frame_id": target_frame_id,
        "token_id": _first_token_id(artifact, token_ordinal),
        "row_id": "0" * 64,
        "row_sha256": "0" * 64,
    }


def _add_invocation_topology(artifact, *, suffix="a", token_ordinal=4):
    child = _add_child_frame(artifact, f"child-{suffix}")
    invocation = _build_invocation_row(artifact, suffix, child["frame_id"], token_ordinal)
    artifact["invocations"].append(invocation)
    return child, invocation


def _ensure_second_stream_row(artifact):
    clone = copy.deepcopy(artifact["streams"][0])
    object_span = next(
        item["physical_span"]
        for item in artifact["objects"]
        if item["ref"] == [8, 0]
    )
    start = object_span["span"][0]
    clone["stream_id"] = "8:0"
    clone["owner_ref"] = [8, 0]
    clone["physical_object_span"] = copy.deepcopy(object_span)
    clone["stream_keyword_span"] = _span_dict(_fixture_pdf(artifact), start, start + 6)
    clone["opening_eol_span"] = _span_dict(_fixture_pdf(artifact), start + 6, start + 7)
    clone["encoded_payload_span"] = _span_dict(_fixture_pdf(artifact), start + 7, start + 8)
    clone["encoded_payload_sha256"] = clone["encoded_payload_span"]["sha256"]
    clone["endstream_keyword_span"] = _span_dict(_fixture_pdf(artifact), start + 8, start + 17)
    clone["closing_eol_span"] = None
    clone["post_payload_mode"] = "none"
    clone["decoder_chain"] = ["identity"]
    clone["decoded_length"] = 1
    clone["decoded_sha256"] = clone["encoded_payload_sha256"]
    clone["root_contents_ordinal"] = 1
    clone["token_count"] = 0
    clone["tokens"] = []
    artifact["streams"].append(clone)
    return clone


def _ensure_second_frame_row(artifact):
    return _add_child_frame(artifact, "synthetic")


def _ensure_second_resolution_row(artifact):
    clone = copy.deepcopy(artifact["resolutions"][0])
    clone["resolution_id"] = clone["resolution_id"] + "-synthetic"
    clone["token_id"] = _first_token_id(artifact, 5)
    artifact["resolutions"].append(clone)
    artifact["atoms"][0]["resource_resolution_ids"] = [
        artifact["resolutions"][0]["resolution_id"],
        clone["resolution_id"],
    ]
    return clone


def _ensure_second_atom_row(artifact):
    clone = copy.deepcopy(artifact["atoms"][0])
    clone["atom_id"] = clone["atom_id"] + "-synthetic"
    clone["operator_evidence"]["operator_token_id"] = _first_token_id(artifact, 8)
    clone["operator_evidence"]["operand_token_ids"] = [_first_token_id(artifact, 7)]
    clone["glyph_ids"] = []
    artifact["atoms"].append(clone)
    return clone


def _ensure_second_glyph_row(artifact):
    clone = copy.deepcopy(artifact["glyphs"][0])
    clone["glyph_id"] = clone["glyph_id"] + "-synthetic"
    clone["code_index"] = 0
    artifact["glyphs"].append(clone)
    artifact["atoms"][0]["glyph_ids"] = [artifact["glyphs"][0]["glyph_id"], clone["glyph_id"]]
    return clone


def _repair_second_stream_count_violation(parsed):
    parsed["streams"].pop()


def _repair_second_stream_swap_count_violation(parsed):
    parsed["streams"][0], parsed["streams"][1] = parsed["streams"][1], parsed["streams"][0]
    parsed["streams"].pop()


def _repair_second_atom_count_violation(parsed):
    parsed["atoms"].pop()


def _repair_second_atom_swap_count_violation(parsed):
    parsed["atoms"][0], parsed["atoms"][1] = parsed["atoms"][1], parsed["atoms"][0]
    parsed["atoms"].pop()


def _repair_second_glyph_count_violation(parsed):
    parsed["glyphs"].pop()
    parsed["atoms"][0]["glyph_ids"] = [parsed["glyphs"][0]["glyph_id"]]


def _repair_second_glyph_swap_count_violation(parsed):
    parsed["glyphs"][0], parsed["glyphs"][1] = parsed["glyphs"][1], parsed["glyphs"][0]
    parsed["glyphs"].pop()
    parsed["atoms"][0]["glyph_ids"] = [parsed["glyphs"][0]["glyph_id"]]


def _synthesize_one_row_group(artifact, plural):
    if plural == "streams":
        return _ensure_second_stream_row(artifact)
    if plural == "frames":
        return _ensure_second_frame_row(artifact)
    if plural == "resolutions":
        return _ensure_second_resolution_row(artifact)
    if plural == "atoms":
        return _ensure_second_atom_row(artifact)
    if plural == "glyphs":
        return _ensure_second_glyph_row(artifact)
    raise AssertionError(f"unsupported one-row synthetic group: {plural}")


def _set_group_duplicate_semantic_id(artifact, plural, semantic_key):
    if plural == "invocations":
        _, first = _add_invocation_topology(artifact, suffix="dup-a", token_ordinal=4)
        _, second = _add_invocation_topology(artifact, suffix="dup-b", token_ordinal=6)
        second[semantic_key] = first[semantic_key]
        return
    if plural in {"streams", "frames", "resolutions", "atoms", "glyphs"}:
        _synthesize_one_row_group(artifact, plural)
    elif len(artifact[plural]) < 2:
        artifact[plural].append(copy.deepcopy(artifact[plural][0]))
    artifact[plural][-1][semantic_key] = artifact[plural][0][semantic_key]


def _swap_group_rows(artifact, plural):
    if plural == "invocations":
        _add_invocation_topology(artifact, suffix="swap-a", token_ordinal=4)
        _add_invocation_topology(artifact, suffix="swap-b", token_ordinal=6)
    elif plural in {"streams", "frames", "resolutions", "atoms", "glyphs"}:
        _synthesize_one_row_group(artifact, plural)
    elif len(artifact[plural]) < 2:
        artifact[plural].append(copy.deepcopy(artifact[plural][0]))
    artifact[plural][0], artifact[plural][1] = artifact[plural][1], artifact[plural][0]


def _insert_group_clone(artifact, plural, extra_mutate=None):
    if plural == "invocations":
        _, clone = _add_invocation_topology(artifact, suffix="insert", token_ordinal=4)
    elif plural in {"streams", "frames", "resolutions", "atoms", "glyphs"}:
        clone = _synthesize_one_row_group(artifact, plural)
    else:
        clone = copy.deepcopy(artifact[plural][-1])
        artifact[plural].append(clone)
    if extra_mutate is not None:
        extra_mutate(clone)


def _drop_group_last(artifact, plural):
    if plural == "invocations":
        _add_invocation_topology(artifact, suffix="remove", token_ordinal=4)
    artifact[plural].pop()


def _case_root_binding_fixture_id(artifact):
    other = next(
        row.fixture_id.decode("ascii")
        for row in stage_a._FIXTURES
        if row.fixture_id.decode("ascii") != artifact["fixture"]["id"]
    )
    artifact["fixture"]["id"] = other


def _case_root_binding_profile_hash(artifact):
    artifact["profile"]["raw_sha256"] = "0" * 64


def _case_root_binding_schema(artifact):
    artifact["schema"] = "kb_creator.pdf_raw.RawAtomProvenanceAuthority.v999"


def _case_root_binding_terminal(artifact):
    artifact["terminal_state"] = "consumer_ready"


def _case_root_binding_unknown_root_key(artifact):
    artifact["unexpected_root_key"] = {}


def _case_root_binding_missing_root_key(artifact):
    del artifact["selector"]


def _case_root_binding_wrong_inventory_pin(artifact):
    return lambda artifact_raw: _json_rewrite(artifact_raw, lambda parsed: parsed.__setitem__("inventory_sha256", "f" * 64))


def _case_root_binding_wrong_content_pin(artifact):
    return lambda artifact_raw: _json_rewrite(artifact_raw, lambda parsed: parsed.__setitem__("content_sha256", "e" * 64))


def _case_trailer_root_ref_existing_object(artifact):
    artifact["trailer_root"]["ref"] = [2, 0]


def _case_trailer_dictionary_shifted_span(artifact):
    pdf = _fixture_pdf(artifact)
    artifact["trailer_root"]["dictionary"] = _span_dict(pdf, 0, 8)


def _case_trailer_root_entry_shifted_span(artifact):
    pdf = _fixture_pdf(artifact)
    artifact["trailer_root"]["root_entry"] = _span_dict(pdf, 57, 64)


def _case_trailer_root_value_shifted_span(artifact):
    pdf = _fixture_pdf(artifact)
    artifact["trailer_root"]["root_value"] = _span_dict(pdf, 113, 118)


def _case_trailer_broken_nesting(artifact):
    entry = artifact["trailer_root"]["root_entry"]["span"]
    artifact["trailer_root"]["root_value"]["span"] = [entry[1] - 1, entry[1]]
    pdf = _fixture_pdf(artifact)
    start, end = artifact["trailer_root"]["root_value"]["span"]
    artifact["trailer_root"]["root_value"]["sha256"] = stage_a._sha(pdf[start:end])


def _case_page_index_changed(artifact):
    artifact["page"]["page_index"] = 1


def _case_page_ref_changed(artifact):
    artifact["page"]["page_ref"] = [2, 0]


def _case_page_route_reordered(artifact):
    artifact["page"]["page_tree_route"] = [[3, 0], [2, 0]]


def _case_page_route_duplicated(artifact):
    artifact["page"]["page_tree_route"] = [[2, 0], [2, 0]]


def _case_page_route_detached(artifact):
    artifact["page"]["page_tree_route"] = [[2, 0], [8, 0]]


def _case_universal_unknown_key(artifact, plural):
    if plural == "invocations":
        _add_invocation_topology(artifact, suffix="unknown", token_ordinal=4)
        return lambda artifact_raw: _json_rewrite(
            artifact_raw,
            lambda parsed, p=plural: parsed[p][0].__setitem__("unexpected_key", "x"),
        )
    artifact[plural][0]["unexpected_key"] = "x"


def _case_universal_missing_key(artifact, plural):
    if plural == "invocations":
        _add_invocation_topology(artifact, suffix="missing", token_ordinal=4)
        return lambda artifact_raw: _json_rewrite(artifact_raw, lambda parsed, p=plural: parsed[p][0].pop("row_sha256"))
    return lambda artifact_raw: _json_rewrite(artifact_raw, lambda parsed, p=plural: parsed[p][0].pop("row_sha256"))


def _case_universal_wrong_kind(artifact, plural):
    if plural == "invocations":
        _add_invocation_topology(artifact, suffix="wrong-kind", token_ordinal=4)
        return lambda artifact_raw: _json_rewrite(
            artifact_raw,
            lambda parsed, p=plural: parsed[p][0].__setitem__("kind", "wrong-kind"),
        )
    artifact[plural][0]["kind"] = "wrong-kind"


def _case_universal_wrong_type(artifact, plural):
    if plural == "invocations":
        _add_invocation_topology(artifact, suffix="wrong-type", token_ordinal=4)
        return lambda artifact_raw: _json_rewrite(artifact_raw, lambda parsed, p=plural: parsed[p][0].__setitem__("ordinal", "0"))
    return lambda artifact_raw: _json_rewrite(artifact_raw, lambda parsed, p=plural: parsed[p][0].__setitem__("ordinal", "0"))


def _case_universal_duplicate_row_id(artifact, plural):
    if plural == "invocations":
        _add_invocation_topology(artifact, suffix="dup-row", token_ordinal=4)
        return lambda artifact_raw, p=plural: _append_exact_sealed_clone(artifact_raw, p)
    if plural in {"streams", "frames", "resolutions", "atoms", "glyphs"}:
        return lambda artifact_raw, p=plural: _append_exact_sealed_clone(artifact_raw, p)
    if len(artifact[plural]) < 2:
        artifact[plural].append(copy.deepcopy(artifact[plural][0]))
    return lambda artifact_raw: _json_rewrite(artifact_raw, lambda parsed, p=plural: parsed[p][1].__setitem__("row_id", parsed[p][0]["row_id"]))


def _case_universal_row_swap(artifact, plural):
    return _swap_group_rows(artifact, plural)


def _case_universal_row_insert(artifact, plural):
    return _insert_group_clone(artifact, plural)


def _case_universal_row_remove(artifact, plural):
    return _drop_group_last(artifact, plural)


def _case_object_duplicate_ref(artifact):
    artifact["objects"][1]["ref"] = artifact["objects"][0]["ref"]


def _case_object_shifted_span(artifact):
    pdf = _fixture_pdf(artifact)
    artifact["objects"][1]["physical_span"] = _span_dict(pdf, 0, 8)


def _case_object_overlap(artifact):
    left = artifact["objects"][0]["physical_span"]["span"]
    artifact["objects"][1]["physical_span"]["span"] = [left[1] - 4, left[1] + 12]
    pdf = _fixture_pdf(artifact)
    start, end = artifact["objects"][1]["physical_span"]["span"]
    artifact["objects"][1]["physical_span"]["sha256"] = stage_a._sha(pdf[start:end])


def _case_object_order_swap(artifact):
    _swap_group_rows(artifact, "objects")


def _case_stream_owner_wrong_object(artifact):
    artifact["streams"][0]["owner_ref"] = [8, 0]


def _case_stream_id_detached(artifact):
    artifact["streams"][0]["stream_id"] = "8:0"


def _case_stream_physical_object_detached(artifact):
    pdf = _fixture_pdf(artifact)
    artifact["streams"][0]["physical_object_span"] = _span_dict(pdf, 0, 8)


def _case_stream_keyword_shifted(artifact):
    pdf = _fixture_pdf(artifact)
    artifact["streams"][0]["stream_keyword_span"] = _span_dict(pdf, 0, 6)


def _case_stream_opening_eol_shifted(artifact):
    pdf = _fixture_pdf(artifact)
    artifact["streams"][0]["opening_eol_span"] = _span_dict(pdf, 6, 7)


def _case_stream_payload_shifted(artifact):
    pdf = _fixture_pdf(artifact)
    artifact["streams"][0]["encoded_payload_span"] = _span_dict(pdf, 7, 10)
    artifact["streams"][0]["encoded_payload_sha256"] = artifact["streams"][0]["encoded_payload_span"]["sha256"]


def _case_stream_endstream_shifted(artifact):
    pdf = _fixture_pdf(artifact)
    artifact["streams"][0]["endstream_keyword_span"] = _span_dict(pdf, 10, 19)


def _case_stream_closing_eol_shifted_if_present(artifact):
    if artifact["streams"][0]["closing_eol_span"] is None:
        raise AssertionError("collection must select the FlateDecode fixture")
    pdf = _fixture_pdf(artifact)
    artifact["streams"][0]["closing_eol_span"] = _span_dict(pdf, 0, 1)


def _case_stream_adjacency_broken(artifact):
    start, end = artifact["streams"][0]["opening_eol_span"]["span"]
    artifact["streams"][0]["opening_eol_span"]["span"] = [start + 1, end + 1]
    pdf = _fixture_pdf(artifact)
    artifact["streams"][0]["opening_eol_span"]["sha256"] = stage_a._sha(pdf[start + 1 : end + 1])


def _case_stream_post_payload_mode_mismatch(artifact):
    stream = artifact["streams"][0]
    if stream["closing_eol_span"] is None:
        stream["post_payload_mode"] = "single_eol_lf"
    else:
        stream["post_payload_mode"] = "none"


def _case_stream_decoder_chain_substitution(artifact):
    artifact["streams"][0]["decoder_chain"] = ["identity", "FlateDecode"]


def _case_stream_encoded_payload_digest_changed(artifact):
    stream = artifact["streams"][0]
    stream["encoded_payload_sha256"] = stage_a._sha(_mutated_payload_bytes(stream, artifact))


def _case_stream_decoded_claim_changed(artifact):
    stream = artifact["streams"][0]
    stream["decoded_length"] += 1
    stream["decoded_sha256"] = "a" * 64
    for token in _token_rows(artifact, stream["stream_id"]):
        token["decoded_sha256"] = stream["decoded_sha256"]
    if stream["tokens"]:
        for token in stream["tokens"]:
            token["decoded_sha256"] = stream["decoded_sha256"]


def _case_stream_root_contents_order_changed(artifact):
    artifact["streams"][0]["root_contents_ordinal"] = 1


def _case_stream_nested_global_divergence(artifact):
    stream = artifact["streams"][0]
    stream["tokens"] = list(reversed(copy.deepcopy(stream["tokens"])))


def _case_token_foreign_stream(artifact):
    artifact["tokens"][0]["stream_id"] = "foreign-stream"


def _case_token_duplicate_ordinal(artifact):
    artifact["tokens"][1]["token_ordinal"] = artifact["tokens"][0]["token_ordinal"]


def _case_token_decoded_overlap(artifact):
    artifact["tokens"][1]["decoded_span"] = artifact["tokens"][0]["decoded_span"]


def _case_token_decoded_gap_reversal(artifact):
    artifact["tokens"][0]["decoded_span"] = [2, 4]
    artifact["tokens"][1]["decoded_span"] = [0, 2]


def _case_token_decoded_out_of_range(artifact):
    artifact["tokens"][0]["decoded_span"] = [0, artifact["streams"][0]["decoded_length"] + 1]


def _case_token_decoded_zero_length(artifact):
    start = artifact["tokens"][0]["decoded_span"][0]
    artifact["tokens"][0]["decoded_span"] = [start, start]


def _case_token_raw_b64_changed(artifact):
    artifact["tokens"][0]["raw_b64"] = base64.b64encode(b"XX").decode("ascii")


def _case_token_decoded_hash_changed(artifact):
    artifact["tokens"][0]["decoded_sha256"] = "b" * 64


def _case_token_identity_physical_offset_shifted(artifact):
    stream = artifact["streams"][0]
    if stream["decoder_chain"] != ["identity"]:
        raise AssertionError("collection must select the identity fixture")
    pdf = _fixture_pdf(artifact)
    artifact["tokens"][0]["physical_span"] = _span_dict(pdf, 0, 1)
    artifact["tokens"][0]["physical_sha256"] = artifact["tokens"][0]["physical_span"]["sha256"]


def _case_token_physical_mixed_null(artifact):
    if artifact["streams"][0]["decoder_chain"] == ["identity"]:
        artifact["tokens"][0]["physical_span"] = None
    else:
        artifact["tokens"][0]["physical_sha256"] = "d" * 64


def _case_token_flate_physical_injected(artifact):
    stream = artifact["streams"][0]
    if stream["decoder_chain"] != ["FlateDecode"]:
        raise AssertionError("collection must select the FlateDecode fixture")
    pdf = _fixture_pdf(artifact)
    artifact["tokens"][0]["physical_span"] = _span_dict(pdf, 0, 1)
    artifact["tokens"][0]["physical_sha256"] = artifact["tokens"][0]["physical_span"]["sha256"]


def _case_token_identity_physical_duplicate(artifact):
    stream = artifact["streams"][0]
    if stream["decoder_chain"] != ["identity"]:
        raise AssertionError("collection must select the identity fixture")
    artifact["tokens"][1]["physical_span"] = copy.deepcopy(artifact["tokens"][0]["physical_span"])
    artifact["tokens"][1]["physical_sha256"] = artifact["tokens"][0]["physical_sha256"]


def _case_token_global_order_swap(artifact):
    artifact["tokens"][0], artifact["tokens"][1] = artifact["tokens"][1], artifact["tokens"][0]
    artifact["tokens"][0]["token_ordinal"] = 0
    artifact["tokens"][1]["token_ordinal"] = 1


def _case_frame_owner_non_stream_object(artifact):
    artifact["frames"][0]["owner_ref"] = [1, 0]


def _case_frame_decoded_hash_detached(artifact):
    artifact["frames"][0]["decoded_stream_sha256"] = "c" * 64


def _case_frame_root_parent_self(artifact):
    artifact["frames"][0]["parent_frame_id"] = artifact["frames"][0]["frame_id"]


def _case_frame_second_root_inserted(artifact):
    _insert_group_clone(
        artifact,
        "frames",
        extra_mutate=lambda row: row.update(
            {"frame_id": row["frame_id"] + "-clone", "parent_frame_id": None}
        ),
    )


def _case_frame_orphan_child_inserted(artifact):
    _insert_group_clone(
        artifact,
        "frames",
        extra_mutate=lambda row: row.update(
            {"frame_id": row["frame_id"] + "-orphan", "parent_frame_id": "missing-parent"}
        ),
    )


def _case_frame_child_before_parent(artifact):
    root = artifact["frames"][0]
    child = copy.deepcopy(root)
    child["frame_id"] = root["frame_id"] + "-child"
    child["parent_frame_id"] = root["frame_id"]
    artifact["frames"].insert(0, child)


def _case_resolution_foreign_frame(artifact):
    artifact["resolutions"][0]["frame_id"] = "foreign-frame"


def _case_resolution_missing_token(artifact):
    artifact["resolutions"][0]["token_id"] = ["5:0", 999]


def _case_resolution_wrong_existing_token(artifact):
    artifact["resolutions"][0]["token_id"] = ["5:0", 0]


def _case_resolution_non_font_target(artifact):
    artifact["resolutions"][0]["target_ref"] = [5, 0]


def _case_resolution_invalid_resource_b64(artifact):
    artifact["resolutions"][0]["resource_name_b64"] = "@@@"


def _case_resolution_invalid_char_range(artifact):
    artifact["resolutions"][0]["first_char"] = 200
    artifact["resolutions"][0]["last_char"] = 100


def _case_resolution_widths_span_outside_font(artifact):
    pdf = _fixture_pdf(artifact)
    artifact["resolutions"][0]["widths_span"] = _span_dict(pdf, 0, 8)


def _case_resolution_duplicate_id(artifact):
    _insert_group_clone(artifact, "resolutions")


def _case_resolution_orphan_inserted(artifact):
    _insert_group_clone(
        artifact,
        "resolutions",
        extra_mutate=lambda row: row.update({"resolution_id": row["resolution_id"] + "-orphan"}),
    )
    artifact["atoms"][0]["resource_resolution_ids"] = [artifact["resolutions"][0]["resolution_id"]]


def _case_resolution_order_reversed(artifact):
    clone = copy.deepcopy(artifact["resolutions"][0])
    clone["resolution_id"] = clone["resolution_id"] + "-later"
    artifact["resolutions"].append(clone)
    artifact["atoms"][0]["resource_resolution_ids"] = [
        artifact["resolutions"][1]["resolution_id"],
        artifact["resolutions"][0]["resolution_id"],
    ]


def _case_invocation_self_cycle_inserted(artifact):
    root_frame = artifact["frames"][0]["frame_id"]
    artifact["invocations"].append(
        {
            "kind": "invocation",
            "ordinal": 0,
            "invocation_id": "invoke-self",
            "parent_frame_id": root_frame,
            "target_frame_id": root_frame,
            "token_id": ["5:0", 4],
            "row_id": "0" * 64,
            "row_sha256": "0" * 64,
        }
    )


def _case_invocation_foreign_parent(artifact):
    root_frame = artifact["frames"][0]["frame_id"]
    child = copy.deepcopy(artifact["frames"][0])
    child["frame_id"] = root_frame + "-child"
    child["parent_frame_id"] = root_frame
    artifact["frames"].append(child)
    artifact["invocations"].append(
        {
            "kind": "invocation",
            "ordinal": 0,
            "invocation_id": "invoke-foreign-parent",
            "parent_frame_id": "foreign-parent",
            "target_frame_id": child["frame_id"],
            "token_id": ["5:0", 4],
            "row_id": "0" * 64,
            "row_sha256": "0" * 64,
        }
    )


def _case_invocation_target_parent_disagreement(artifact):
    root_frame = artifact["frames"][0]["frame_id"]
    child = copy.deepcopy(artifact["frames"][0])
    child["frame_id"] = root_frame + "-child"
    child["parent_frame_id"] = root_frame
    artifact["frames"].append(child)
    artifact["invocations"].append(
        {
            "kind": "invocation",
            "ordinal": 0,
            "invocation_id": "invoke-parent-disagree",
            "parent_frame_id": child["frame_id"],
            "target_frame_id": child["frame_id"],
            "token_id": ["5:0", 4],
            "row_id": "0" * 64,
            "row_sha256": "0" * 64,
        }
    )


def _case_invocation_root_target(artifact):
    root_frame = artifact["frames"][0]["frame_id"]
    artifact["invocations"].append(
        {
            "kind": "invocation",
            "ordinal": 0,
            "invocation_id": "invoke-root",
            "parent_frame_id": root_frame,
            "target_frame_id": root_frame,
            "token_id": ["5:0", 4],
            "row_id": "0" * 64,
            "row_sha256": "0" * 64,
        }
    )


def _case_invocation_duplicate_incoming_edge(artifact):
    root_frame = artifact["frames"][0]["frame_id"]
    child = copy.deepcopy(artifact["frames"][0])
    child["frame_id"] = root_frame + "-child"
    child["parent_frame_id"] = root_frame
    artifact["frames"].append(child)
    artifact["invocations"].extend(
        [
            {
                "kind": "invocation",
                "ordinal": 0,
                "invocation_id": "invoke-a",
                "parent_frame_id": root_frame,
                "target_frame_id": child["frame_id"],
                "token_id": ["5:0", 4],
                "row_id": "0" * 64,
                "row_sha256": "0" * 64,
            },
            {
                "kind": "invocation",
                "ordinal": 1,
                "invocation_id": "invoke-b",
                "parent_frame_id": root_frame,
                "target_frame_id": child["frame_id"],
                "token_id": ["5:0", 4],
                "row_id": "0" * 64,
                "row_sha256": "0" * 64,
            },
        ]
    )


def _case_invocation_order_reversal(artifact):
    root_frame = artifact["frames"][0]["frame_id"]
    child_a = copy.deepcopy(artifact["frames"][0])
    child_a["frame_id"] = root_frame + "-child-a"
    child_a["parent_frame_id"] = root_frame
    child_b = copy.deepcopy(artifact["frames"][0])
    child_b["frame_id"] = root_frame + "-child-b"
    child_b["parent_frame_id"] = root_frame
    artifact["frames"].extend([child_a, child_b])
    artifact["invocations"].extend(
        [
            {
                "kind": "invocation",
                "ordinal": 0,
                "invocation_id": "invoke-b",
                "parent_frame_id": root_frame,
                "target_frame_id": child_b["frame_id"],
                "token_id": ["5:0", 6],
                "row_id": "0" * 64,
                "row_sha256": "0" * 64,
            },
            {
                "kind": "invocation",
                "ordinal": 1,
                "invocation_id": "invoke-a",
                "parent_frame_id": root_frame,
                "target_frame_id": child_a["frame_id"],
                "token_id": ["5:0", 4],
                "row_id": "0" * 64,
                "row_sha256": "0" * 64,
            },
        ]
    )


def _case_atom_foreign_frame(artifact):
    artifact["atoms"][0]["frame_id"] = "foreign-frame"


def _case_atom_operator_missing_key(artifact):
    del artifact["atoms"][0]["operator_evidence"]["operator_physical_sha256"]


def _case_atom_operator_extra_key(artifact):
    artifact["atoms"][0]["operator_evidence"]["unexpected"] = True


def _case_atom_operator_wrong_stream(artifact):
    artifact["atoms"][0]["operator_evidence"]["operator_token_id"] = ["foreign-stream", 4]


def _case_atom_operand_after_operator(artifact):
    artifact["atoms"][0]["operator_evidence"]["operand_token_ids"] = [["5:0", 5]]


def _case_atom_operator_span_detached(artifact):
    artifact["atoms"][0]["operator_evidence"]["operator_decoded_span"] = [0, 2]


def _case_atom_unsupported_operator_kind(artifact):
    artifact["atoms"][0]["operator_kind"] = "Do"


def _case_atom_foreign_resolution(artifact):
    artifact["atoms"][0]["resource_resolution_ids"] = ["foreign-resolution"]


def _case_atom_duplicate_resolution(artifact):
    resolution_id = artifact["resolutions"][0]["resolution_id"]
    artifact["atoms"][0]["resource_resolution_ids"] = [resolution_id, resolution_id]


def _case_atom_foreign_glyph(artifact):
    artifact["atoms"][0]["glyph_ids"] = ["foreign-glyph"]


def _case_atom_reordered_glyphs(artifact):
    clone = copy.deepcopy(artifact["glyphs"][0])
    clone["glyph_id"] = clone["glyph_id"] + "-clone"
    clone["code_index"] = 1
    artifact["glyphs"].append(clone)
    artifact["atoms"][0]["glyph_ids"] = [clone["glyph_id"], artifact["glyphs"][0]["glyph_id"]]


def _case_atom_truthy_stage_a_field(artifact):
    artifact["atoms"][0]["geometry"] = {"x": 1}


def _case_atom_order_reversal(artifact):
    clone = copy.deepcopy(artifact["atoms"][0])
    clone["atom_id"] = clone["atom_id"] + "-later"
    clone["operator_evidence"]["operator_token_id"] = ["5:0", 5]
    clone["operator_evidence"]["operand_token_ids"] = [["5:0", 4]]
    clone["glyph_ids"] = []
    artifact["atoms"].insert(0, clone)


def _case_glyph_foreign_atom(artifact):
    artifact["glyphs"][0]["atom_id"] = "foreign-atom"


def _case_glyph_resolution_not_owned(artifact):
    artifact["glyphs"][0]["font_resolution_id"] = "foreign-resolution"


def _case_glyph_foreign_font_ref(artifact):
    artifact["glyphs"][0]["font_ref"] = [5, 0]


def _case_glyph_code_token_not_operand(artifact):
    artifact["glyphs"][0]["code_token_id"] = ["5:0", 4]


def _case_glyph_duplicate_code_index(artifact):
    clone = copy.deepcopy(artifact["glyphs"][0])
    clone["glyph_id"] = clone["glyph_id"] + "-dup"
    artifact["glyphs"].append(clone)


def _case_glyph_reversed_code_index(artifact):
    clone = copy.deepcopy(artifact["glyphs"][0])
    clone["glyph_id"] = clone["glyph_id"] + "-later"
    clone["code_index"] = 1
    artifact["glyphs"].insert(0, clone)


def _case_glyph_invalid_code_b64(artifact):
    artifact["glyphs"][0]["code_b64"] = "@@@"


def _case_glyph_invalid_scalar_b64(artifact):
    artifact["glyphs"][0]["scalar_utf8_b64"] = "@@@"


def _case_glyph_scalar_mismatch(artifact):
    artifact["glyphs"][0]["unicode_scalar"] = 66


def _case_glyph_width_mismatch(artifact):
    artifact["glyphs"][0]["width"] = "501"


def _case_glyph_font_span_outside_containment(artifact):
    pdf = _fixture_pdf(artifact)
    artifact["glyphs"][0]["font_dictionary_span"] = _span_dict(pdf, 0, 8)


def _case_glyph_width_span_outside_containment(artifact):
    pdf = _fixture_pdf(artifact)
    artifact["glyphs"][0]["width_entry_span"] = _span_dict(pdf, 0, 8)


def _case_glyph_orphan_inserted(artifact):
    clone = copy.deepcopy(artifact["glyphs"][0])
    clone["glyph_id"] = clone["glyph_id"] + "-orphan"
    clone["atom_id"] = artifact["atoms"][0]["atom_id"]
    artifact["glyphs"].append(clone)
    artifact["atoms"][0]["glyph_ids"] = [artifact["glyphs"][0]["glyph_id"]]


def _case_stream_synthetic_row_insert(artifact):
    _ensure_second_stream_row(artifact)


def _case_frame_synthetic_row_insert(artifact):
    _ensure_second_frame_row(artifact)


def _case_resolution_synthetic_row_insert(artifact):
    _ensure_second_resolution_row(artifact)


def _case_glyph_synthetic_row_insert(artifact):
    _ensure_second_glyph_row(artifact)


def _case_aggregate_count_changed(artifact):
    return lambda artifact_raw: _json_rewrite(
        artifact_raw,
        lambda parsed: parsed["counts"].__setitem__("token_count", parsed["counts"]["token_count"] + 1),
    )


def _case_aggregate_group_hash_list_reordered(artifact):
    def _edit(parsed):
        if len(parsed["tokens"]) < 2:
            raise AssertionError("sealed Stage A fixtures require two token rows")
        inventory = {
            "counts": parsed["counts"],
            **{
                f"{plural}_row_sha256": (
                    list(reversed([row["row_sha256"] for row in parsed["tokens"]]))
                    if plural == "tokens"
                    else [row["row_sha256"] for row in parsed[plural]]
                )
                for plural in _GROUP_PLURALS
            },
        }
        parsed["inventory_sha256"] = stage_a._sha(stage_a._canonical(inventory))

    return lambda artifact_raw: _json_rewrite(artifact_raw, _edit)


def _case_aggregate_resealed_wrong_order(artifact):
    artifact["tokens"][0], artifact["tokens"][1] = artifact["tokens"][1], artifact["tokens"][0]


def _case_noncanonical_json_bytes(artifact):
    return json.dumps(artifact, ensure_ascii=False, sort_keys=True, indent=2).encode("utf-8")


def _case_legacy_registry_mutated_pdf_leaf(monkeypatch):
    row = stage_a._FIXTURES[0]
    corrupt = stage_a._FixtureRow(
        row.fixture_id,
        row.pdf + b"x",
        row.profile,
        row.selector,
        row.fixture_id_length,
        row.pdf_length,
        row.profile_length,
        row.selector_length,
        row.fixture_id_sha256,
        row.pdf_sha256,
        row.profile_sha256,
        row.selector_sha256,
        row.binding_sha256,
        row.expected_inventory_sha256,
        row.expected_content_sha256,
    )
    monkeypatch.setattr(stage_a, "_FIXTURES", (corrupt, stage_a._FIXTURES[1]))


_UNIVERSAL_GROUP_CASES = []
for plural, kind in _GROUPS:
    semantic_key = {
        "objects": None,
        "streams": "stream_id",
        "tokens": None,
        "frames": "frame_id",
        "resolutions": "resolution_id",
        "invocations": "invocation_id",
        "atoms": "atom_id",
        "glyphs": "glyph_id",
    }[plural]
    _UNIVERSAL_GROUP_CASES.extend(
        [
            (f"universal.{plural}.unknown_key", lambda artifact, p=plural: _case_universal_unknown_key(artifact, p)),
            (f"universal.{plural}.missing_key", lambda artifact, p=plural: _case_universal_missing_key(artifact, p)),
            (f"universal.{plural}.wrong_kind", lambda artifact, p=plural: _case_universal_wrong_kind(artifact, p)),
            (f"universal.{plural}.wrong_type", lambda artifact, p=plural: _case_universal_wrong_type(artifact, p)),
            (f"universal.{plural}.duplicate_row_id", lambda artifact, p=plural: _case_universal_duplicate_row_id(artifact, p)),
            (f"universal.{plural}.row_swap", lambda artifact, p=plural: _case_universal_row_swap(artifact, p)),
            (f"universal.{plural}.row_insert", lambda artifact, p=plural: _case_universal_row_insert(artifact, p)),
            (f"universal.{plural}.row_remove", lambda artifact, p=plural: _case_universal_row_remove(artifact, p)),
        ]
    )
    if semantic_key is not None:
        _UNIVERSAL_GROUP_CASES.append(
            (
                f"universal.{plural}.duplicate_semantic_id",
                lambda artifact, p=plural, key=semantic_key: _set_group_duplicate_semantic_id(artifact, p, key),
            )
        )


_MATRIX_CASES = [
    ("root.fixture_id", _case_root_binding_fixture_id),
    ("root.profile_hash", _case_root_binding_profile_hash),
    ("root.schema", _case_root_binding_schema),
    ("root.terminal_state", _case_root_binding_terminal),
    ("root.unknown_root_key", _case_root_binding_unknown_root_key),
    ("root.missing_root_key", _case_root_binding_missing_root_key),
    ("root.inventory_pin", _case_root_binding_wrong_inventory_pin),
    ("root.content_pin", _case_root_binding_wrong_content_pin),
    ("trailer.root_ref_existing_object", _case_trailer_root_ref_existing_object),
    ("trailer.dictionary_shifted_span", _case_trailer_dictionary_shifted_span),
    ("trailer.root_entry_shifted_span", _case_trailer_root_entry_shifted_span),
    ("trailer.root_value_shifted_span", _case_trailer_root_value_shifted_span),
    ("trailer.broken_nesting", _case_trailer_broken_nesting),
    ("page.index_changed", _case_page_index_changed),
    ("page.ref_changed", _case_page_ref_changed),
    ("page.route_reordered", _case_page_route_reordered),
    ("page.route_duplicated", _case_page_route_duplicated),
    ("page.route_detached", _case_page_route_detached),
    *_UNIVERSAL_GROUP_CASES,
    ("object.duplicate_ref", _case_object_duplicate_ref),
    ("object.shifted_span", _case_object_shifted_span),
    ("object.overlap", _case_object_overlap),
    ("object.order_swap", _case_object_order_swap),
    ("stream.owner_wrong_object", _case_stream_owner_wrong_object),
    ("stream.id_detached", _case_stream_id_detached),
    ("stream.physical_object_detached", _case_stream_physical_object_detached),
    ("stream.keyword_shifted", _case_stream_keyword_shifted),
    ("stream.opening_eol_shifted", _case_stream_opening_eol_shifted),
    ("stream.payload_shifted", _case_stream_payload_shifted),
    ("stream.endstream_shifted", _case_stream_endstream_shifted),
    ("stream.closing_eol_shifted_if_present", _case_stream_closing_eol_shifted_if_present),
    ("stream.adjacency_broken", _case_stream_adjacency_broken),
    ("stream.post_payload_mode_mismatch", _case_stream_post_payload_mode_mismatch),
    ("stream.decoder_chain_substitution", _case_stream_decoder_chain_substitution),
    ("stream.encoded_payload_digest_changed", _case_stream_encoded_payload_digest_changed),
    ("stream.decoded_claim_changed", _case_stream_decoded_claim_changed),
    ("stream.root_contents_order_changed", _case_stream_root_contents_order_changed),
    ("stream.nested_global_divergence", _case_stream_nested_global_divergence),
    ("token.foreign_stream", _case_token_foreign_stream),
    ("token.duplicate_ordinal", _case_token_duplicate_ordinal),
    ("token.decoded_overlap", _case_token_decoded_overlap),
    ("token.decoded_gap_reversal", _case_token_decoded_gap_reversal),
    ("token.decoded_out_of_range", _case_token_decoded_out_of_range),
    ("token.decoded_zero_length", _case_token_decoded_zero_length),
    ("token.raw_b64_changed", _case_token_raw_b64_changed),
    ("token.decoded_hash_changed", _case_token_decoded_hash_changed),
    ("token.identity_physical_offset_shifted", _case_token_identity_physical_offset_shifted),
    ("token.physical_mixed_null", _case_token_physical_mixed_null),
    ("token.flate_physical_injected", _case_token_flate_physical_injected),
    ("token.identity_physical_duplicate", _case_token_identity_physical_duplicate),
    ("token.global_order_swap", _case_token_global_order_swap),
    ("frame.owner_non_stream_object", _case_frame_owner_non_stream_object),
    ("frame.decoded_hash_detached", _case_frame_decoded_hash_detached),
    ("frame.root_parent_self", _case_frame_root_parent_self),
    ("frame.second_root_inserted", _case_frame_second_root_inserted),
    ("frame.orphan_child_inserted", _case_frame_orphan_child_inserted),
    ("frame.child_before_parent", _case_frame_child_before_parent),
    ("resolution.foreign_frame", _case_resolution_foreign_frame),
    ("resolution.missing_token", _case_resolution_missing_token),
    ("resolution.wrong_existing_token", _case_resolution_wrong_existing_token),
    ("resolution.non_font_target", _case_resolution_non_font_target),
    ("resolution.invalid_resource_b64", _case_resolution_invalid_resource_b64),
    ("resolution.invalid_char_range", _case_resolution_invalid_char_range),
    ("resolution.widths_span_outside_font", _case_resolution_widths_span_outside_font),
    ("resolution.duplicate_id", _case_resolution_duplicate_id),
    ("resolution.orphan_inserted", _case_resolution_orphan_inserted),
    ("resolution.order_reversed", _case_resolution_order_reversed),
    ("invocation.self_cycle_inserted", _case_invocation_self_cycle_inserted),
    ("invocation.foreign_parent", _case_invocation_foreign_parent),
    ("invocation.target_parent_disagreement", _case_invocation_target_parent_disagreement),
    ("invocation.root_target", _case_invocation_root_target),
    ("invocation.duplicate_incoming_edge", _case_invocation_duplicate_incoming_edge),
    ("invocation.order_reversal", _case_invocation_order_reversal),
    ("atom.foreign_frame", _case_atom_foreign_frame),
    ("atom.operator_missing_key", _case_atom_operator_missing_key),
    ("atom.operator_extra_key", _case_atom_operator_extra_key),
    ("atom.operator_wrong_stream", _case_atom_operator_wrong_stream),
    ("atom.operand_after_operator", _case_atom_operand_after_operator),
    ("atom.operator_span_detached", _case_atom_operator_span_detached),
    ("atom.unsupported_operator_kind", _case_atom_unsupported_operator_kind),
    ("atom.foreign_resolution", _case_atom_foreign_resolution),
    ("atom.duplicate_resolution", _case_atom_duplicate_resolution),
    ("atom.foreign_glyph", _case_atom_foreign_glyph),
    ("atom.reordered_glyphs", _case_atom_reordered_glyphs),
    ("atom.truthy_stage_a_field", _case_atom_truthy_stage_a_field),
    ("atom.order_reversal", _case_atom_order_reversal),
    ("glyph.foreign_atom", _case_glyph_foreign_atom),
    ("glyph.resolution_not_owned", _case_glyph_resolution_not_owned),
    ("glyph.foreign_font_ref", _case_glyph_foreign_font_ref),
    ("glyph.code_token_not_operand", _case_glyph_code_token_not_operand),
    ("glyph.duplicate_code_index", _case_glyph_duplicate_code_index),
    ("glyph.reversed_code_index", _case_glyph_reversed_code_index),
    ("glyph.invalid_code_b64", _case_glyph_invalid_code_b64),
    ("glyph.invalid_scalar_b64", _case_glyph_invalid_scalar_b64),
    ("glyph.scalar_mismatch", _case_glyph_scalar_mismatch),
    ("glyph.width_mismatch", _case_glyph_width_mismatch),
    ("glyph.font_span_outside_containment", _case_glyph_font_span_outside_containment),
    ("glyph.width_span_outside_containment", _case_glyph_width_span_outside_containment),
    ("glyph.orphan_inserted", _case_glyph_orphan_inserted),
    ("stream.synthetic_row_insert", _case_stream_synthetic_row_insert),
    ("frame.synthetic_row_insert", _case_frame_synthetic_row_insert),
    ("resolution.synthetic_row_insert", _case_resolution_synthetic_row_insert),
    ("glyph.synthetic_row_insert", _case_glyph_synthetic_row_insert),
    ("aggregate.count_changed", _case_aggregate_count_changed),
    ("aggregate.group_hash_list_reordered", _case_aggregate_group_hash_list_reordered),
    ("aggregate.resealed_wrong_order", _case_aggregate_resealed_wrong_order),
    ("aggregate.noncanonical_json", _case_noncanonical_json_bytes),
]


@pytest.mark.parametrize("leaf", ("fixture_id", "pdf", "profile", "selector"))
def test_every_unpinned_input_leaf_fails_before_open_or_extract(monkeypatch, leaf):
    row = stage_a._FIXTURES[0]
    opens, extracts = _assert_no_open_or_extract(monkeypatch)
    supplied = {
        "fixture_id": row.fixture_id,
        "pdf": row.pdf,
        "profile": row.profile,
        "selector": row.selector,
    }
    supplied[leaf] += b"x"
    with pytest.raises(RawPdfError, match="^raw_interpreter_fixture_admission_forbidden$"):
        project_stage_a_raw_authority(**{f"{key}_raw": value for key, value in supplied.items()})
    assert opens == extracts == []


def test_registry_corruption_fails_before_admission_open_or_extract(monkeypatch):
    row = stage_a._FIXTURES[0]
    corrupt = stage_a._FixtureRow(
        row.fixture_id,
        row.pdf + b"x",
        row.profile,
        row.selector,
        row.fixture_id_length,
        row.pdf_length,
        row.profile_length,
        row.selector_length,
        row.fixture_id_sha256,
        row.pdf_sha256,
        row.profile_sha256,
        row.selector_sha256,
        row.binding_sha256,
        row.expected_inventory_sha256,
        row.expected_content_sha256,
    )
    monkeypatch.setattr(stage_a, "_FIXTURES", (corrupt, stage_a._FIXTURES[1]))
    opens, extracts = _assert_no_open_or_extract(monkeypatch)
    with pytest.raises(RawPdfError, match="^raw_interpreter_fixture_registry_invalid$"):
        project_stage_a_raw_authority(row.fixture_id, row.pdf, row.profile, row.selector)
    assert opens == extracts == []


def test_literal_registry_pair_rejects_reversal_in_both_authorities(monkeypatch):
    monkeypatch.setattr(stage_a, "_FIXTURES", tuple(reversed(stage_a._FIXTURES)))
    with pytest.raises(RawPdfError, match="^raw_interpreter_fixture_registry_invalid$"):
        stage_a._registry_check()
    monkeypatch.setattr(legacy_authority, "_ALLOWLIST_ROWS", tuple(reversed(legacy_authority._ALLOWLIST_ROWS)))
    with pytest.raises(RawPdfError, match="^raw_interpreter_fixture_registry_invalid$"):
        legacy_authority._registry()


def test_literal_registry_pair_rejects_fully_rehashed_cross_pair_in_both_authorities(monkeypatch):
    stage_rows = list(stage_a._FIXTURES)
    stage_cross = stage_a._FixtureRow(
        stage_rows[0].fixture_id,
        stage_rows[1].pdf,
        stage_rows[0].profile,
        stage_rows[0].selector,
        len(stage_rows[0].fixture_id),
        len(stage_rows[1].pdf),
        len(stage_rows[0].profile),
        len(stage_rows[0].selector),
        stage_a._sha(stage_rows[0].fixture_id),
        stage_a._sha(stage_rows[1].pdf),
        stage_a._sha(stage_rows[0].profile),
        stage_a._sha(stage_rows[0].selector),
        stage_a._binding(stage_rows[0].fixture_id, stage_rows[1].pdf, stage_rows[0].profile, stage_rows[0].selector),
        stage_rows[1].expected_inventory_sha256,
        stage_rows[1].expected_content_sha256,
    )
    monkeypatch.setattr(stage_a, "_FIXTURES", (stage_cross, stage_rows[1]))
    with pytest.raises(RawPdfError, match="^raw_interpreter_fixture_registry_invalid$"):
        stage_a._registry_check()

    legacy_rows = list(legacy_authority._ALLOWLIST_ROWS)
    legacy_cross = legacy_authority._FixtureRow(
        legacy_rows[0].fixture_id_raw,
        legacy_rows[1].pdf_raw,
        legacy_rows[0].profile_raw,
        legacy_rows[0].selector_raw,
        len(legacy_rows[0].fixture_id_raw),
        len(legacy_rows[1].pdf_raw),
        len(legacy_rows[0].profile_raw),
        len(legacy_rows[0].selector_raw),
        legacy_authority._sha(legacy_rows[0].fixture_id_raw),
        legacy_authority._sha(legacy_rows[1].pdf_raw),
        legacy_authority._sha(legacy_rows[0].profile_raw),
        legacy_authority._sha(legacy_rows[0].selector_raw),
        legacy_authority._bind_hash(
            legacy_rows[0].fixture_id_raw,
            legacy_rows[1].pdf_raw,
            legacy_rows[0].profile_raw,
            legacy_rows[0].selector_raw,
        ),
    )
    monkeypatch.setattr(legacy_authority, "_ALLOWLIST_ROWS", (legacy_cross, legacy_rows[1]))
    with pytest.raises(RawPdfError, match="^raw_interpreter_fixture_registry_invalid$"):
        legacy_authority._registry()


def test_non_bytes_ingress_is_rejected_before_admission(monkeypatch):
    row = stage_a._FIXTURES[0]
    opens, extracts = _assert_no_open_or_extract(monkeypatch)
    with pytest.raises(RawPdfError, match="^raw_interpreter_authority_ingress_forbidden$"):
        project_stage_a_raw_authority("fixture", row.pdf, row.profile, row.selector)
    assert opens == extracts == []


_IDENTITY_OFFSET_SKIP_REASON = "identity physical-offset evidence is not defined for the FlateDecode fixture; the identity fixture pair executes this case"

_TARGET_FIRST_FAILURE_REPAIRS = {
    "stream.synthetic_row_insert": _repair_second_stream_count_violation,
    "glyph.synthetic_row_insert": _repair_second_glyph_count_violation,
    "universal.streams.row_insert": _repair_second_stream_count_violation,
    "universal.streams.row_swap": _repair_second_stream_swap_count_violation,
    "universal.atoms.row_insert": _repair_second_atom_count_violation,
    "universal.atoms.row_swap": _repair_second_atom_swap_count_violation,
    "universal.glyphs.row_insert": _repair_second_glyph_count_violation,
    "universal.glyphs.row_swap": _repair_second_glyph_swap_count_violation,
}


def _collected_matrix():
    pairs, ids = [], []
    for case_name, mutate in _MATRIX_CASES:
        fixture_indexes = (0, 1)
        if case_name in {"stream.closing_eol_shifted_if_present", "token.flate_physical_injected"}:
            fixture_indexes = (1,)
        if case_name in {"token.identity_physical_duplicate"}:
            fixture_indexes = (0,)
        for index in fixture_indexes:
            fixture_id = stage_a._FIXTURES[index].fixture_id.decode("ascii")
            value = (case_name, mutate, index)
            if case_name == "token.identity_physical_offset_shifted" and index == 1:
                value = pytest.param(*value, marks=pytest.mark.skip(reason=_IDENTITY_OFFSET_SKIP_REASON))
            pairs.append(value)
            ids.append(f"{case_name}[{fixture_id}]")
    return pairs, ids


_COLLECTED_MATRIX, _COLLECTED_MATRIX_IDS = _collected_matrix()


def test_matrix_collection_shape_and_single_skip_contract():
    assert len(_MATRIX_CASES) == 176
    assert len(_COLLECTED_MATRIX) == 349
    skip_params = [
        param
        for param in _COLLECTED_MATRIX
        if any(getattr(mark, "name", "") == "skip" for mark in getattr(param, "marks", ()))
    ]
    assert len(skip_params) == 1


@pytest.mark.parametrize("case_name,mutate,row_index", _COLLECTED_MATRIX, ids=_COLLECTED_MATRIX_IDS)
def test_fully_rehashed_adversarial_matrix_blocks_before_open_or_extract(monkeypatch, case_name, mutate, row_index):
    row, source = _source_row()[row_index]
    opens, extracts = _assert_no_open_or_extract(monkeypatch)
    artifact = copy.deepcopy(source)
    result = mutate(artifact)
    if case_name != "stream.nested_global_divergence":
        artifact_raw = _reseal(artifact)
    else:
        artifact_raw = _reseal(artifact, sync_nested_tokens=False)
    if callable(result):
        artifact_raw = result(artifact_raw)
    elif result is not None:
        artifact_raw = result
    if case_name.startswith("universal.") or case_name in {
        "token.decoded_zero_length",
        "stream.closing_eol_shifted_if_present",
        "token.flate_physical_injected",
        "token.identity_physical_offset_shifted",
        "token.identity_physical_duplicate",
        "stream.synthetic_row_insert",
        "frame.synthetic_row_insert",
        "resolution.synthetic_row_insert",
        "glyph.synthetic_row_insert",
    }:
        _assert_surrogate_semantic_rejection(row, artifact_raw)
    repair = _TARGET_FIRST_FAILURE_REPAIRS.get(case_name)
    if repair is not None:
        _assert_surrogate_first_failure_is_target_violation(row, artifact_raw, repair)
    with pytest.raises(RawPdfError, match="^raw_interpreter_authority_blocked$"):
        replay_stage_a_raw_authority(row.fixture_id, row.pdf, row.profile, row.selector, artifact_raw)
    assert opens == extracts == []


def test_every_present_physical_span_rejects_zero_length_before_open_or_extract(monkeypatch):
    """Exercise every fixture-present physical span family with fresh seals."""
    sources = _source_row()
    opens, extracts = _assert_no_open_or_extract(monkeypatch)
    span_keys = {
        "objects": ("physical_span",),
        "streams": ("physical_object_span", "stream_keyword_span", "opening_eol_span", "encoded_payload_span", "endstream_keyword_span", "closing_eol_span"),
        "tokens": ("physical_span",),
        "resolutions": ("widths_span",),
        "glyphs": ("font_dictionary_span", "width_entry_span"),
    }
    for row, source in sources:
        for trailer_key in ("dictionary", "root_entry", "root_value"):
            artifact = copy.deepcopy(source)
            start = artifact["trailer_root"][trailer_key]["span"][0]
            artifact["trailer_root"][trailer_key] = _span_dict(row.pdf, start, start)
            raw = _reseal(artifact)
            _assert_surrogate_semantic_rejection(row, raw)
            with pytest.raises(RawPdfError, match="^raw_interpreter_authority_blocked$"):
                replay_stage_a_raw_authority(row.fixture_id, row.pdf, row.profile, row.selector, raw)
        for plural, keys in span_keys.items():
            for index, key in ((i, key) for i in range(len(source[plural])) for key in keys if source[plural][i].get(key) is not None):
                artifact = copy.deepcopy(source)
                start = artifact[plural][index][key]["span"][0]
                artifact[plural][index][key] = _span_dict(row.pdf, start, start)
                raw = _reseal(artifact)
                _assert_surrogate_semantic_rejection(row, raw)
                with pytest.raises(RawPdfError, match="^raw_interpreter_authority_blocked$"):
                    replay_stage_a_raw_authority(row.fixture_id, row.pdf, row.profile, row.selector, raw)
    assert opens == extracts == []


def test_legacy_registry_mutation_fails_before_open_or_extract(monkeypatch):
    _case_legacy_registry_mutated_pdf_leaf(monkeypatch)
    row = stage_a._FIXTURES[1]
    opens, extracts = _assert_no_open_or_extract(monkeypatch)
    with pytest.raises(RawPdfError, match="^raw_interpreter_fixture_registry_invalid$"):
        replay_stage_a_raw_authority(
            row.fixture_id,
            row.pdf,
            row.profile,
            row.selector,
            project_stage_a_raw_authority(row.fixture_id, row.pdf, row.profile, row.selector).canonical_bytes(),
        )
    assert opens == extracts == []


def test_stage_a_module_cannot_import_live_or_consumer_paths():
    source = stage_a.__file__
    raw = open(source, "r", encoding="utf-8").read()
    tree = ast.parse(raw, filename=source)
    forbidden_text = (
        "innsmouth",
        "keeperbook",
        "markdown",
        "html",
        "pdfplumber",
        "pypdf",
        "fitz",
    )
    assert all(token not in raw.lower() for token in forbidden_text)
    imports = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imports.extend(alias.name for alias in node.names)
        if isinstance(node, ast.ImportFrom) and node.module is not None:
            imports.append(node.module)
    assert "kb_creator.pdf_raw.source_reconstruction" not in imports


def test_reseal_helper_emits_canonical_json_and_not_stale_seals():
    row = stage_a._FIXTURES[0]
    artifact = _canonical_artifact(project_stage_a_raw_authority(row.fixture_id, row.pdf, row.profile, row.selector))
    artifact["atoms"][0]["geometry"] = "changed"
    sealed = _reseal(artifact)
    parsed = json.loads(sealed)
    fresh = _canonical_artifact(project_stage_a_raw_authority(row.fixture_id, row.pdf, row.profile, row.selector))
    assert sealed == stage_a._canonical(parsed)
    assert parsed["atoms"][0]["row_sha256"] != fresh["atoms"][0]["row_sha256"]
