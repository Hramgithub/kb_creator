import json
import os
import hashlib
import copy
import subprocess
import sys
from dataclasses import replace
from pathlib import Path

import pytest

from kb_creator.pipeline.mechanical_reconstruction import compile_mechanical_draft, verify_mechanical_draft, _validate_candidate_page, _validate_generated_draft
from kb_creator.pipeline.mechanical_reconstruction import _validate_selection, _sha
from kb_creator.pipeline import reconstruction, reconstruction_replay as replay
from kb_creator.tests.test_mineru_cpu_packet_b import _full_fixture, _run_adapters
from kb_creator.tests import test_mineru_cpu_packet_b as fixtures
from kb_creator.scripts import build_mineru_visual_merge_bundle as bundle


VIEWS = ("original_pipeline_txt", "original_pipeline_ocr", "raster_pipeline_ocr")

def _quote_selection_fixture():
    texts = ("A's \"book\"", "A’s “book”", "A’s \"book\"")
    alternatives = {}
    for view, text in zip(VIEWS, texts):
        alternatives[(view, 1)] = {"text": text, "text_sha256": _sha(text.encode())}
    entry = {"chosen_view": VIEWS[0], "raw_index": 1, "disposition": "emitted", "correction": None,
             "text_selection": {"rule": "three_view_typographic_quote_equivalent", "output_sha256": _sha(texts[0].encode()),
                                 "view_status": {VIEWS[0]: "selected", VIEWS[1]: "equivalent", VIEWS[2]: "equivalent"}}}
    return entry, alternatives

def test_v3_quote_selection_rederives_witness_and_v2_rejects_new_rule():
    entry, alternatives = _quote_selection_fixture()
    _validate_selection(entry, 1, alternatives, schema="kb_creator.mechanical_draft.v3")
    for mutate in (
        lambda value: value["text_selection"].update({"rule": "three_view_exact"}),
        lambda value: value["text_selection"]["view_status"].update({VIEWS[1]: "corroborating"}),
        lambda value: value["text_selection"].update({"output_sha256": "0" * 64}),
        lambda value: value.update({"chosen_view": VIEWS[1]}),
    ):
        changed = copy.deepcopy(entry); mutate(changed)
        with pytest.raises(ValueError):
            _validate_selection(changed, 1, alternatives, schema="kb_creator.mechanical_draft.v3")
    with pytest.raises(ValueError):
        _validate_selection(entry, 1, alternatives, schema="kb_creator.mechanical_draft.v2")

def test_v4_title_selection_rederives_witness_and_old_versions_reject_it():
    texts = ("Chapter Two", "chapter two", "CHAPTER TWO")
    alternatives = {(view, 1): {"text": text, "text_sha256": _sha(text.encode()), "semantic_evidence": {"markdown_heading": True}}
                   for view, text in zip(VIEWS, texts)}
    entry = {"chosen_view": VIEWS[0], "raw_index": 1, "disposition": "emitted", "correction": None,
             "text_selection": {"rule": "three_view_title_ascii_case_equivalent.v1", "output_sha256": _sha(texts[0].encode()),
                                 "view_status": {VIEWS[0]: "selected", VIEWS[1]: "equivalent", VIEWS[2]: "equivalent"}}}
    _validate_selection(entry, 1, alternatives, schema="kb_creator.mechanical_draft.v4")
    with pytest.raises(ValueError):
        _validate_selection(entry, 1, alternatives, schema="kb_creator.mechanical_draft.v3")

@pytest.mark.parametrize("rule, texts", [
    ("three_view_title_ascii_case_equivalent.v1", ("Chapter Two", "chapter two", "CHAPTER TWO")),
    ("three_view_title_letter_spacing_equivalent.v1", ("SECRETS", "S E C R E T S", "SECRETS")),
])
def test_v4_validator_rejects_forged_body_title_witnesses(rule, texts):
    entry, alternatives = _quote_selection_fixture()
    alternatives = {(view, 1): {"text": text, "text_sha256": _sha(text.encode()), "semantic_evidence": {}}
                    for view, text in zip(VIEWS, texts)}
    entry["text_selection"] = {"rule": rule, "output_sha256": _sha(texts[0].encode()),
                                "view_status": {view: "selected" if index == 0 else "corroborating" if text == texts[0] else "equivalent"
                                                for index, (view, text) in enumerate(zip(VIEWS, texts))}}
    with pytest.raises(ValueError, match="title equivalence"):
        _validate_selection(entry, 1, alternatives, schema="kb_creator.mechanical_draft.v4")


def _block(raw, text="body", kind="text", *, assets=None, table_body="", level=None):
    return {"raw_index": raw, "type": kind, "text": text, "bbox": [0, raw, 100, raw + 1], "assets": assets or [], "table_body": table_body, "semantic_evidence": {"text_level": level}}


def _packet(page, blocks_by_view):
    return {"schema": "kb_creator.mineru_merge_packet.v1", "source_page": page, "semantic_role": "body", "views": {view: {"blocks": blocks_by_view[view]} for view in VIEWS}}


def _stage04(root: Path, packets):
    stage = root / "outputs/04-visual-merge-bundle"; pages = stage / "merge_packets/pages"; pages.mkdir(parents=True)
    (stage / "visual").mkdir(); (stage / "visual/visual_manifest.json").write_text(json.dumps({"files": []}), encoding="utf-8")
    source = root / "source.pdf"; source.write_bytes(b"synthetic source")
    (root / "outputs/01-prepare-inputs/prepared").mkdir(parents=True)
    (root / "outputs/01-prepare-inputs/prepared/sample_pages.json").write_text("{}", encoding="utf-8")
    (root / "outputs/03-compare-views").mkdir(parents=True)
    pairs = {}
    for left, right in ((VIEWS[0], VIEWS[1]), (VIEWS[0], VIEWS[2]), (VIEWS[1], VIEWS[2])):
        pairs[f"{left}__vs__{right}"] = {"bbox_matches": [], "left_unmatched": [], "right_unmatched": [], "semantic_conflicts": []}
    (root / "outputs/03-compare-views/comparison.json").write_text(json.dumps({"pairwise": pairs}), encoding="utf-8")
    (root / "run.json").write_text(json.dumps({"source": {"path_hint": "source.pdf", "bytes": source.stat().st_size, "sha256": hashlib.sha256(source.read_bytes()).hexdigest().upper()}}), encoding="utf-8")
    for page, value in packets.items():
        value = copy.deepcopy(value)
        value["pairwise"] = {}
        for left, right in ((VIEWS[0], VIEWS[1]), (VIEWS[0], VIEWS[2]), (VIEWS[1], VIEWS[2])):
            left_raw = {block["raw_index"] for block in value["views"][left]["blocks"]}
            right_raw = {block["raw_index"] for block in value["views"][right]["blocks"]}
            value["pairwise"][f"{left}__vs__{right}"] = {"bbox_matches": [{"left_raw_index": raw, "right_raw_index": raw, "bbox_iou": 1.0} for raw in sorted(left_raw & right_raw)], "left_unmatched": [], "right_unmatched": []}
        (pages / f"page-{page:03d}.json").write_text(json.dumps(value), encoding="utf-8")
    return root


def _verified(_: Path):
    return object()


def test_compiler_is_deterministic_and_keeps_candidate_unreviewed(tmp_path):
    blocks = {view: [_block(7, "Exact body", assets=["images/map.png"], level=2)] for view in VIEWS}
    root = _stage04(tmp_path / "run", {1: _packet(1, blocks)})
    first = compile_mechanical_draft(root, tmp_path / "first", authority_validator=_verified)
    second = compile_mechanical_draft(root, tmp_path / "second", authority_validator=_verified)
    assert first["manifest_sha256"] == second["manifest_sha256"]
    assert first["review_flags"] == {"visual_reviewed": False, "accepted": False}
    page = json.loads((tmp_path / "first/pages/page-001.json").read_text(encoding="utf-8"))
    assert page["markdown"].startswith("## Exact body\n![mechanical asset]({{asset:")
    assert page["entries"][0]["source_keys"] == [{"view": view, "raw_index": 7} for view in VIEWS]
    assert page["entries"][0]["assets_emitted"][0]["source_path"] == "images/map.png"
    assert not (tmp_path / "first/decision_set.json").exists()


def test_mismatch_is_retained_as_typed_hold_without_dropping_table_evidence(tmp_path):
    good = _block(1, "", "table", assets=["tables/a.png"], table_body="<table><tr><th>A</th></tr><tr><td>1</td></tr></table>")
    changed = dict(good); changed["text"] = "different"
    blocks = {VIEWS[0]: [good], VIEWS[1]: [changed], VIEWS[2]: [good]}
    root = _stage04(tmp_path / "run", {1: _packet(1, blocks)})
    report = compile_mechanical_draft(root, tmp_path / "out", authority_validator=_verified)
    page = json.loads((tmp_path / "out/pages/page-001.json").read_text(encoding="utf-8"))
    assert report["unresolved_hold_count"] == 1
    assert report["diagnostics"][0]["code"] == "three_view_content_mismatch"
    assert [row["disposition"] for row in page["entries"]] == ["hold"]
    assert page["entries"][0]["assets"] == ["tables/a.png"]
    assert page["entries"][0]["table_body_sha256"]


def test_table_requires_real_header_and_data_row_and_keeps_hold(tmp_path):
    block = _block(2, "", "table", assets=["tables/a.png"], table_body="<table><tr><td>orphan</td></tr></table>")
    root = _stage04(tmp_path / "run", {1: _packet(1, {view: [block] for view in VIEWS})})
    report = compile_mechanical_draft(root, tmp_path / "out", authority_validator=_verified)
    page = json.loads((tmp_path / "out/pages/page-001.json").read_text(encoding="utf-8"))
    assert report["diagnostics"][0]["code"] == "table_evidence_missing"
    assert page["entries"][0]["disposition"] == "hold"


def test_emitted_table_has_exact_table_body_mapping_and_closed_schema(tmp_path):
    body = "<table><tr><th>A</th></tr><tr><td>1</td></tr></table>"
    block = _block(4, "", "table", assets=["tables/a.png"], table_body=body)
    root = _stage04(tmp_path / "run", {1: _packet(1, {view: [block] for view in VIEWS})})
    report = compile_mechanical_draft(root, tmp_path / "out", authority_validator=_verified)
    page = json.loads((tmp_path / "out/pages/page-001.json").read_text(encoding="utf-8"))
    mapping = page["entries"][0]["unit"]["source_offsets"]
    assert all(row["field"] == "table_body" and row["end"] == len(body) for row in mapping)
    assert all(row["source_sha256"] == hashlib.sha256(body.encode()).hexdigest().upper() for row in mapping)
    from jsonschema import Draft202012Validator, ValidationError
    schema = json.loads((Path(__file__).resolve().parents[1] / "contracts/mechanical_draft.v5.schema.json").read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(report)
    tampered = dict(report); tampered["authorities"] = dict(report["authorities"]); tampered["authorities"].pop("comparison")
    with pytest.raises(ValidationError): Draft202012Validator(schema).validate(tampered)


def test_standard_library_validation_matches_schema_negative_boundaries(tmp_path):
    block = _block(5, "body", assets=["images/a.png"])
    root = _stage04(tmp_path / "run", {1: _packet(1, {view: [block] for view in VIEWS})})
    report = compile_mechanical_draft(root, tmp_path / "out", authority_validator=_verified)
    page = json.loads((tmp_path / "out/pages/page-001.json").read_text(encoding="utf-8"))
    from jsonschema import Draft202012Validator, ValidationError
    schema = json.loads((Path(__file__).resolve().parents[1] / "contracts/mechanical_draft.v5.schema.json").read_text(encoding="utf-8"))
    page_schema = {"$ref": "#/$defs/page_candidate", "$defs": schema["$defs"]}
    page_mutations = [
        lambda value: value["entries"][0].update({"unexpected": 1}),
        lambda value: value["entries"][0].pop("source_keys"),
        lambda value: value["entries"][0]["alternatives"][0].pop("blocks"),
        lambda value: value["entries"][0]["source_keys"][0].update({"raw_index": True}),
        lambda value: value["entries"][0]["reader_span"].update({"start_line": 0}),
        lambda value: value["entries"][0]["unit"]["source_offsets"][0].update({"source_sha256": "bad"}),
    ]
    for mutate in page_mutations:
        malformed = copy.deepcopy(page); mutate(malformed)
        with pytest.raises(ValidationError): Draft202012Validator(page_schema).validate(malformed)
        with pytest.raises(ValueError): _validate_candidate_page(malformed)
    report_mutations = [
        lambda value: value["authorities"]["source"].update({"bytes": True}),
        lambda value: value["authorities"].update({"validator_route": "replay", "replay": {"bridge": {"path": "replay/bridge.json", "bytes": 1, "sha256": "bad"}, "completion": value["authorities"]["run"]}}),
        lambda value: value["diagnostics"].append({"code": "bad", "page": True, "source_keys": [], "alternatives": [], "expected": "x", "observed": "x", "next_action": "x"}),
        lambda value: value["pages"][0]["packet"].update({"bytes": True}),
    ]
    for mutate in report_mutations:
        malformed = copy.deepcopy(report); mutate(malformed)
        with pytest.raises(ValidationError): Draft202012Validator(schema).validate(malformed)
        with pytest.raises(ValueError): _validate_generated_draft(malformed, tmp_path / "out")


@pytest.mark.parametrize(
    ("name", "kind", "text", "assets", "table_body", "level", "disposition", "unit_kind"),
    [
        ("text", "text", "body", [], "", None, "emitted", "paragraph"),
        ("title", "text", "Title", [], "", 2, "emitted", "paragraph"),
        ("table", "table", "", [], "<table><tr><th>A</th></tr><tr><td>1</td></tr></table>", None, "emitted", "table"),
        ("image_only", "image", "", ["images/a.png"], "", None, "emitted", "asset"),
        ("text_and_image", "text", "body", ["images/a.png"], "", None, "emitted", "paragraph"),
        ("empty_furniture", "footer", "", [], "", None, "excluded_empty", None),
    ],
)
def test_supported_block_modes_materialize_schema_valid_boundary_candidates(tmp_path, name, kind, text, assets, table_body, level, disposition, unit_kind):
    block = _block(8, text, kind, assets=assets, table_body=table_body, level=level)
    root = _stage04(tmp_path / name, {1: _packet(1, {view: [block] for view in VIEWS})})
    report = compile_mechanical_draft(root, tmp_path / f"{name}-candidate", authority_validator=_verified)
    page = json.loads((tmp_path / f"{name}-candidate/pages/page-001.json").read_text(encoding="utf-8"))
    entry = page["entries"][0]
    assert entry["disposition"] == disposition
    if unit_kind is None:
        assert "unit" not in entry
    else:
        assert entry["unit"]["kind"] == unit_kind
        if unit_kind == "asset":
            assert entry["unit"]["source_offsets"] == []
            assert len(entry["unit"]["asset_bindings"]) == len(VIEWS)
        else:
            assert len(entry["unit"]["source_offsets"]) == len(VIEWS)
    assert report["review_flags"] == {"visual_reviewed": False, "accepted": False}


def test_hash_keyed_reviewed_correction_is_exact_and_fail_closed(tmp_path):
    block = _block(3, "before")
    root = _stage04(tmp_path / "run", {1: _packet(1, {view: [block] for view in VIEWS})})
    from kb_creator.pipeline.mechanical_reconstruction import _sha
    correction = {"source_sha256": _sha(b"before"), "before": "before", "after": "after", "reason": "reviewed source evidence"}
    report = compile_mechanical_draft(root, tmp_path / "out", reviewed_corrections={correction["source_sha256"]: correction}, authority_validator=_verified)
    page = json.loads((tmp_path / "out/pages/page-001.json").read_text(encoding="utf-8"))
    assert page["entries"][0]["reader_text"] == "after"
    bad = dict(correction); bad["source_sha256"] = "0" * 64
    with pytest.raises(ValueError, match="not exact"):
        compile_mechanical_draft(root, tmp_path / "bad", reviewed_corrections={_sha(b"before"): bad}, authority_validator=_verified)


def test_rejects_unverified_stage04_before_output_creation(tmp_path):
    root = tmp_path / "run"; root.mkdir()
    with pytest.raises(ValueError, match="incomplete"):
        compile_mechanical_draft(root, tmp_path / "out", authority_validator=_verified)
    assert not (tmp_path / "out").exists()


def test_keeps_ocr_only_block_and_reading_order_difference_as_holds(tmp_path):
    a, b = _block(1, "A"), _block(2, "B")
    ocr_only = _block(3, "OCR only")
    root = _stage04(tmp_path / "run", {1: _packet(1, {VIEWS[0]: [a, b], VIEWS[1]: [b, a, ocr_only], VIEWS[2]: [a, b]})})
    report = compile_mechanical_draft(root, tmp_path / "out", authority_validator=_verified)
    page = json.loads((tmp_path / "out/pages/page-001.json").read_text(encoding="utf-8"))
    assert len(page["entries"]) == 3
    assert any(row["raw_index"] == 3 for row in page["entries"])
    assert report["unresolved_hold_count"] == 3


def test_closed_shifted_bbox_triangle_emits_and_local_inversion_holds_only_endpoints(tmp_path):
    first, second, third = _block(1, "first"), _block(2, "second"), _block(3, "third")
    shifted = copy.deepcopy(first); shifted["bbox"] = [1, 1, 101, 2]
    root = _stage04(tmp_path / "shift", {1: _packet(1, {VIEWS[0]: [first], VIEWS[1]: [first], VIEWS[2]: [shifted]})})
    report = compile_mechanical_draft(root, tmp_path / "shift-out", authority_validator=_verified)
    assert report["unresolved_hold_count"] == 0
    assert json.loads((tmp_path / "shift-out/pages/page-001.json").read_text())["entries"][0]["disposition"] == "emitted"
    blocks = {VIEWS[0]: [first, second, third], VIEWS[1]: [second, first, third], VIEWS[2]: [second, first, third]}
    root = _stage04(tmp_path / "inversion", {1: _packet(1, blocks)})
    report = compile_mechanical_draft(root, tmp_path / "inversion-out", authority_validator=_verified)
    page = json.loads((tmp_path / "inversion-out/pages/page-001.json").read_text())
    assert [row["disposition"] for row in page["entries"]].count("emitted") == 1
    assert {row["code"] for row in report["diagnostics"]} == {"reading_order_conflict"}


def test_ambiguous_packet_edge_is_rejected_before_candidate_output(tmp_path):
    block = _block(1, "body")
    root = _stage04(tmp_path / "run", {1: _packet(1, {view: [block] for view in VIEWS})})
    packet = root / "outputs/04-visual-merge-bundle/merge_packets/pages/page-001.json"
    value = json.loads(packet.read_text()); value["pairwise"][f"{VIEWS[0]}__vs__{VIEWS[1]}"]["bbox_matches"].append({"left_raw_index": 1, "right_raw_index": 1, "bbox_iou": 1.0})
    packet.write_text(json.dumps(value), encoding="utf-8")
    with pytest.raises(ValueError, match="ambiguous bbox edge"):
        compile_mechanical_draft(root, tmp_path / "out", authority_validator=_verified)
    assert not (tmp_path / "out").exists()


def test_advisory_pairwise_semantic_conflict_is_projected_and_unknown_unmatched_key_fails_closed(tmp_path):
    block = _block(1, "body")
    root = _stage04(tmp_path / "conflict", {1: _packet(1, {view: [block] for view in VIEWS})})
    packet = root / "outputs/04-visual-merge-bundle/merge_packets/pages/page-001.json"
    value = json.loads(packet.read_text()); pair = value["pairwise"][f"{VIEWS[0]}__vs__{VIEWS[1]}"]
    pair["semantic_conflicts"] = [{"left_raw_index": 1, "right_raw_index": 1}]
    value["views"][VIEWS[0]]["blocks"][0]["semantic_evidence"]["markdown_heading"] = True
    packet.write_text(json.dumps(value), encoding="utf-8")
    report = compile_mechanical_draft(root, tmp_path / "conflict-out", authority_validator=_verified)
    assert report["schema"] == "kb_creator.mechanical_draft.v5"
    assert report["diagnostics"] == []
    root2 = _stage04(tmp_path / "unknown", {1: _packet(1, {view: [block] for view in VIEWS})})
    packet2 = root2 / "outputs/04-visual-merge-bundle/merge_packets/pages/page-001.json"; value = json.loads(packet2.read_text())
    value["pairwise"][f"{VIEWS[0]}__vs__{VIEWS[1]}"]["left_unmatched"] = [{"raw_index": 99}]; packet2.write_text(json.dumps(value), encoding="utf-8")
    with pytest.raises(ValueError, match="unknown source key"):
        compile_mechanical_draft(root2, tmp_path / "unknown-out", authority_validator=_verified)


def test_title_metadata_disagreement_and_drive_asset_are_rejected_or_held(tmp_path):
    first = _block(1, "Maybe title", level=2); second = _block(1, "Maybe title", level=None)
    root = _stage04(tmp_path / "run", {1: _packet(1, {VIEWS[0]: [first], VIEWS[1]: [second], VIEWS[2]: [first]})})
    report = compile_mechanical_draft(root, tmp_path / "out", authority_validator=_verified)
    assert report["unresolved_hold_count"] == 1
    bad = _block(2, "body", assets=["C:/escape.png"])
    root2 = _stage04(tmp_path / "run2", {1: _packet(1, {view: [bad] for view in VIEWS})})
    with pytest.raises(ValueError, match="relative POSIX"):
        compile_mechanical_draft(root2, tmp_path / "bad", authority_validator=_verified)


@pytest.mark.parametrize("mutate", [
    lambda blocks: blocks[VIEWS[2]].__setitem__("type", "header"),
    lambda blocks: blocks[VIEWS[2]].__setitem__("assets", ["images/other.png"]),
    lambda blocks: blocks[VIEWS[2]].__setitem__("table_body", "<table>other</table>"),
    lambda blocks: blocks[VIEWS[2]]["semantic_evidence"].__setitem__("text_level", 1),
])
def test_output_relevant_semantic_projection_keeps_emitted_structure_exact(tmp_path, mutate):
    blocks = {view: _block(1, "body", assets=["images/a.png"]) for view in VIEWS}
    for view in VIEWS:
        blocks[view]["semantic_evidence"]["markdown_heading"] = view == VIEWS[0]
    mutate(blocks)
    root = _stage04(tmp_path / "run", {1: _packet(1, {view: [blocks[view]] for view in VIEWS})})
    report = compile_mechanical_draft(root, tmp_path / "out", authority_validator=_verified)
    assert report["unresolved_hold_count"] == 1


def test_advisory_projection_exposes_text_mismatch_as_text_hold(tmp_path):
    blocks = {view: _block(1, text, level=2) for view, text in zip(VIEWS, ("one", "two", "three"))}
    blocks[VIEWS[0]]["semantic_evidence"]["markdown_heading"] = True
    root = _stage04(tmp_path / "run", {1: _packet(1, {view: [blocks[view]] for view in VIEWS})})
    report = compile_mechanical_draft(root, tmp_path / "out", authority_validator=_verified)
    assert report["diagnostics"][0]["code"] == "three_view_content_mismatch"


def test_public_verifier_reopens_authority_and_rejects_source_packet_or_page_drift(tmp_path):
    block = _block(1, "body")
    root = _stage04(tmp_path / "run", {1: _packet(1, {view: [block] for view in VIEWS})})
    source = root / "source.pdf"
    def checked_authority(run_root):
        run = json.loads((run_root / "run.json").read_text(encoding="utf-8"))
        assert hashlib.sha256(source.read_bytes()).hexdigest().upper() == run["source"]["sha256"]
    output = tmp_path / "out"
    report = compile_mechanical_draft(root, output, authority_validator=checked_authority)
    assert verify_mechanical_draft(output, authority_validator=checked_authority)["manifest_sha256"] == report["manifest_sha256"]
    source.write_bytes(b"changed source")
    with pytest.raises(AssertionError):
        verify_mechanical_draft(output, authority_validator=checked_authority)
    source.write_bytes(b"synthetic source")
    packet = root / "outputs/04-visual-merge-bundle/merge_packets/pages/page-001.json"
    packet.write_text(packet.read_text(encoding="utf-8") + " ", encoding="utf-8")
    with pytest.raises(ValueError, match="packet binding mismatch"):
        verify_mechanical_draft(output, authority_validator=checked_authority)
    packet.write_text(packet.read_text(encoding="utf-8").rstrip(), encoding="utf-8")
    candidate_page = output / "pages/page-001.json"
    candidate_page.write_text(candidate_page.read_text(encoding="utf-8") + " ", encoding="utf-8")
    with pytest.raises(ValueError, match="candidate page identity mismatch"):
        verify_mechanical_draft(output, authority_validator=checked_authority)


def _reseal_candidate_manifest(candidate_dir, mutate):
    manifest_path = candidate_dir / "mechanical_draft.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    mutate(manifest)
    for page in manifest["pages"]:
        candidate_path = candidate_dir / page["candidate"]["path"]
        page["candidate"] = {"path": page["candidate"]["path"], **{"bytes": candidate_path.stat().st_size, "sha256": _sha(candidate_path.read_bytes())}}
    manifest["manifest_sha256"] = _sha(json.dumps({key: value for key, value in manifest.items() if key != "manifest_sha256"}, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8"))
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, sort_keys=True, indent=2) + "\n", encoding="utf-8")


def test_public_verifier_rejects_resealed_forged_packet_alternative(tmp_path):
    block = _block(1, "source text")
    root = _stage04(tmp_path / "run", {1: _packet(1, {view: [block] for view in VIEWS})})
    output = tmp_path / "out"
    compile_mechanical_draft(root, output, authority_validator=_verified)
    candidate_path = output / "pages/page-001.json"
    candidate = json.loads(candidate_path.read_text(encoding="utf-8"))
    forged = "FORGED TEXT"
    for alternative in candidate["entries"][0]["alternatives"]:
        alternative["blocks"][0]["text"] = forged
        alternative["blocks"][0]["text_sha256"] = _sha(forged.encode())
    candidate["entries"][0]["source_text_sha256"] = _sha(forged.encode())
    candidate["entries"][0]["reader_text"] = forged
    candidate["entries"][0]["reader_span"] = {"start_line": 1, "end_line": 1, "sha256": _sha(forged.encode())}
    candidate["entries"][0]["unit"]["reader_span"] = dict(candidate["entries"][0]["reader_span"])
    for offset in candidate["entries"][0]["unit"]["source_offsets"]:
        offset.update({"source_sha256": _sha(forged.encode()), "start": 0, "end": len(forged)})
    candidate["entries"][0]["text_selection"]["output_sha256"] = _sha(forged.encode())
    candidate["markdown"] = forged
    candidate_path.write_text(json.dumps(candidate, ensure_ascii=False, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    _reseal_candidate_manifest(output, lambda _: None)
    with pytest.raises(ValueError, match="candidate content does not match authoritative packet"):
        verify_mechanical_draft(output, authority_validator=_verified)


def test_public_verifier_rejects_resealed_forged_diagnostic(tmp_path):
    blocks = {view: [_block(1, "one" if view == VIEWS[0] else "two")] for view in VIEWS}
    root = _stage04(tmp_path / "run", {1: _packet(1, blocks)})
    output = tmp_path / "out"
    compile_mechanical_draft(root, output, authority_validator=_verified)
    def forge(manifest):
        manifest["diagnostics"][0]["next_action"] = "forged diagnostic"
    _reseal_candidate_manifest(output, forge)
    with pytest.raises(ValueError, match="candidate diagnostics do not match authoritative packet"):
        verify_mechanical_draft(output, authority_validator=_verified)


@pytest.mark.parametrize("schema,ruleset", [
    ("kb_creator.mechanical_draft.v2", "mechanical-reconstruction.v2"),
    ("kb_creator.mechanical_draft.v3", "mechanical-reconstruction.v3"),
    ("kb_creator.mechanical_draft.v4", "mechanical-reconstruction.v4"),
])
def test_public_verifier_binds_historical_packet_evidence_without_newer_projection(tmp_path, schema, ruleset):
    block = _block(1, "source text")
    root = _stage04(tmp_path / "run", {1: _packet(1, {view: [block] for view in VIEWS})})
    output = tmp_path / "out"
    compile_mechanical_draft(root, output, authority_validator=_verified)
    def historic(manifest):
        manifest["schema"] = schema
        manifest["ruleset_version"] = ruleset
    _reseal_candidate_manifest(output, historic)
    assert verify_mechanical_draft(output, authority_validator=_verified)["schema"] == schema


@pytest.mark.parametrize("schema,ruleset,blocks,correction", [
    ("kb_creator.mechanical_draft.v2", "mechanical-reconstruction.v2",
     {view: [_block(1, "plain body")] for view in VIEWS}, None),
    ("kb_creator.mechanical_draft.v3", "mechanical-reconstruction.v3",
     {view: [_block(1, "A's \"book\"")] for view in VIEWS}, None),
    ("kb_creator.mechanical_draft.v4", "mechanical-reconstruction.v4",
     {view: [_block(1, "Chapter Two", level=2, assets=["images/map.png"])] for view in VIEWS}, None),
    ("kb_creator.mechanical_draft.v4", "mechanical-reconstruction.v4",
     {view: [_block(1, "", "table", table_body="<table><tr><th>A</th></tr><tr><td>one</td></tr></table>")] for view in VIEWS}, None),
    ("kb_creator.mechanical_draft.v4", "mechanical-reconstruction.v4",
     {view: [_block(1, "before")] for view in VIEWS},
     {"source_sha256": _sha(b"before"), "before": "before", "after": "after", "reason": "reviewed source evidence"}),
])
def test_historical_rendered_output_recipes_remain_valid(tmp_path, schema, ruleset, blocks, correction):
    root = _stage04(tmp_path / "run", {1: _packet(1, blocks)})
    output = tmp_path / "out"
    corrections = None if correction is None else {correction["source_sha256"]: correction}
    compile_mechanical_draft(root, output, reviewed_corrections=corrections, authority_validator=_verified)
    _reseal_candidate_manifest(output, lambda manifest: manifest.update({"schema": schema, "ruleset_version": ruleset}))
    assert verify_mechanical_draft(output, authority_validator=_verified, reviewed_corrections=corrections)["schema"] == schema


def test_historical_verifier_rejects_resealed_forged_reader_output(tmp_path):
    block = _block(1, "source text")
    root = _stage04(tmp_path / "run", {1: _packet(1, {view: [block] for view in VIEWS})})
    output = tmp_path / "out"
    compile_mechanical_draft(root, output, authority_validator=_verified)
    candidate_path = output / "pages/page-001.json"
    candidate = json.loads(candidate_path.read_text(encoding="utf-8"))
    forged = "FORGED OUTPUT"
    candidate["entries"][0]["reader_text"] = forged
    candidate["entries"][0]["reader_span"] = {"start_line": 1, "end_line": 1, "sha256": _sha(forged.encode())}
    candidate["entries"][0]["unit"]["reader_span"] = dict(candidate["entries"][0]["reader_span"])
    candidate["markdown"] = forged
    candidate_path.write_text(json.dumps(candidate, ensure_ascii=False, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    _reseal_candidate_manifest(output, lambda manifest: manifest.update({"schema": "kb_creator.mechanical_draft.v4", "ruleset_version": "mechanical-reconstruction.v4"}))
    with pytest.raises(ValueError, match="legacy rendered output does not match authoritative packet"):
        verify_mechanical_draft(output, authority_validator=_verified)


def test_historical_verifier_rejects_excluded_content_and_forged_asset_marker(tmp_path):
    block = _block(1, "body", assets=["images/map.png"])
    root = _stage04(tmp_path / "run", {1: _packet(1, {view: [block] for view in VIEWS})})
    output = tmp_path / "out"
    compile_mechanical_draft(root, output, authority_validator=_verified)
    candidate_path = output / "pages/page-001.json"
    candidate = json.loads(candidate_path.read_text(encoding="utf-8"))
    candidate["entries"][0]["assets_emitted"][0]["logical_name"] = "forged.png"
    candidate_path.write_text(json.dumps(candidate, ensure_ascii=False, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    _reseal_candidate_manifest(output, lambda manifest: manifest.update({"schema": "kb_creator.mechanical_draft.v4", "ruleset_version": "mechanical-reconstruction.v4"}))
    with pytest.raises(ValueError, match="legacy rendered output does not match authoritative packet"):
        verify_mechanical_draft(output, authority_validator=_verified)


def test_historical_excluded_empty_allows_null_correction_but_rejects_nonnull_correction(tmp_path):
    block = _block(1, "", "footer")
    root = _stage04(tmp_path / "run", {1: _packet(1, {view: [block] for view in VIEWS})})
    output = tmp_path / "out"
    compile_mechanical_draft(root, output, authority_validator=_verified)
    candidate_path = output / "pages/page-001.json"
    candidate = json.loads(candidate_path.read_text(encoding="utf-8"))
    candidate["entries"][0]["correction"] = None  # Historical v4 shape in the frozen Fear candidate.
    candidate_path.write_text(json.dumps(candidate, ensure_ascii=False, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    _reseal_candidate_manifest(output, lambda manifest: manifest.update({"schema": "kb_creator.mechanical_draft.v4", "ruleset_version": "mechanical-reconstruction.v4"}))
    assert verify_mechanical_draft(output, authority_validator=_verified)["schema"] == "kb_creator.mechanical_draft.v4"
    candidate = json.loads(candidate_path.read_text(encoding="utf-8"))
    candidate["entries"][0]["correction"] = {"source_sha256": _sha(b""), "before": "x", "after": "y", "reason": "forged"}
    candidate_path.write_text(json.dumps(candidate, ensure_ascii=False, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    _reseal_candidate_manifest(output, lambda _: None)
    with pytest.raises(ValueError):
        verify_mechanical_draft(output, authority_validator=_verified)


def test_historical_output_allows_selected_source_offset_recipe_only(tmp_path):
    block = _block(1, "source text")
    root = _stage04(tmp_path / "run", {1: _packet(1, {view: [block] for view in VIEWS})})
    output = tmp_path / "out"
    compile_mechanical_draft(root, output, authority_validator=_verified)
    candidate_path = output / "pages/page-001.json"
    candidate = json.loads(candidate_path.read_text(encoding="utf-8"))
    unit = candidate["entries"][0]["unit"]
    unit["source_offsets"] = [unit["source_offsets"][0]]
    candidate_path.write_text(json.dumps(candidate, ensure_ascii=False, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    _reseal_candidate_manifest(output, lambda manifest: manifest.update({"schema": "kb_creator.mechanical_draft.v4", "ruleset_version": "mechanical-reconstruction.v4"}))
    assert verify_mechanical_draft(output, authority_validator=_verified)["schema"] == "kb_creator.mechanical_draft.v4"


def test_public_verifier_requires_external_legacy_correction_authority(tmp_path):
    block = _block(1, "before")
    root = _stage04(tmp_path / "run", {1: _packet(1, {view: [block] for view in VIEWS})})
    correction = {"source_sha256": _sha(b"before"), "before": "before", "after": "after", "reason": "reviewed source evidence"}
    output = tmp_path / "out"
    compile_mechanical_draft(root, output, reviewed_corrections={correction["source_sha256"]: correction}, authority_validator=_verified)
    assert verify_mechanical_draft(output, authority_validator=_verified, reviewed_corrections={correction["source_sha256"]: correction})["manifest_sha256"]
    with pytest.raises(ValueError, match="legacy correction requires supplied authority"):
        verify_mechanical_draft(output, authority_validator=_verified)
    candidate_path = output / "pages/page-001.json"
    candidate = json.loads(candidate_path.read_text(encoding="utf-8"))
    candidate["entries"][0]["correction"]["after"] = "forged"
    candidate["entries"][0]["reader_text"] = "forged"
    candidate["entries"][0]["reader_span"] = {"start_line": 1, "end_line": 1, "sha256": _sha(b"forged")}
    candidate["entries"][0]["unit"]["reader_span"] = dict(candidate["entries"][0]["reader_span"])
    candidate["entries"][0]["text_selection"]["output_sha256"] = _sha(b"forged")
    candidate["markdown"] = "forged"
    candidate_path.write_text(json.dumps(candidate, ensure_ascii=False, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    _reseal_candidate_manifest(output, lambda _: None)
    with pytest.raises(ValueError, match="legacy correction does not match supplied authority"):
        verify_mechanical_draft(output, authority_validator=_verified, reviewed_corrections={correction["source_sha256"]: correction})


def test_reader_spans_follow_blank_separator_and_complex_table_is_held(tmp_path):
    a, b = _block(1, "first"), _block(2, "second")
    root = _stage04(tmp_path / "run", {1: _packet(1, {view: [a, b] for view in VIEWS})})
    compile_mechanical_draft(root, tmp_path / "out", authority_validator=_verified)
    page = json.loads((tmp_path / "out/pages/page-001.json").read_text(encoding="utf-8"))
    assert [row["reader_span"]["start_line"] for row in page["entries"]] == [1, 3]
    complex_table = _block(3, "", "table", table_body="<table><tr><th colspan='2'>A</th></tr><tr><td>1</td><td>2</td></tr></table>")
    root2 = _stage04(tmp_path / "run2", {1: _packet(1, {view: [complex_table] for view in VIEWS})})
    report = compile_mechanical_draft(root2, tmp_path / "complex", authority_validator=_verified)
    assert report["diagnostics"][0]["code"] == "table_evidence_missing"
    br_table = _block(4, "", "table", table_body="<table><tr><th>A</th></tr><tr><td>one<br>two</td></tr></table>")
    root3 = _stage04(tmp_path / "run3", {1: _packet(1, {view: [br_table] for view in VIEWS})})
    report = compile_mechanical_draft(root3, tmp_path / "break", authority_validator=_verified)
    assert report["diagnostics"][0]["code"] == "table_evidence_missing"


def test_duplicate_text_emits_as_separate_components_when_recorded_edges_are_unique(tmp_path):
    duplicate = [_block(1, "same"), _block(2, "same")]
    duplicate[1]["bbox"] = duplicate[0]["bbox"]
    root = _stage04(tmp_path / "run", {1: _packet(1, {view: duplicate for view in VIEWS})})
    report = compile_mechanical_draft(root, tmp_path / "candidate", authority_validator=_verified)
    page = json.loads((tmp_path / "candidate/pages/page-001.json").read_text(encoding="utf-8"))
    assert report["diagnostics"] == []
    assert [item["disposition"] for item in page["entries"]] == ["emitted", "emitted"]
    assert [{item["raw_index"] for item in row["source_keys"]} for row in page["entries"]] == [{1}, {2}]


def test_default_validator_native_and_replay_e2e_fixtures(tmp_path, monkeypatch):
    original_writer = fixtures._write_view_artifacts
    def complete_artifacts(root, pages=6):
        original_writer(root, pages)
        for suffix in ("origin", "span"):
            (root / f"document_{suffix}.pdf").write_bytes((root / "document_layout.pdf").read_bytes())
    monkeypatch.setattr(fixtures, "_write_view_artifacts", complete_artifacts)
    source, contract, runtime, _, _, native = _full_fixture(tmp_path)
    renderer = os.environ.get("KB_CREATOR_PDFTOPPM")
    if renderer: runtime = replace(runtime, pdftoppm=Path(renderer))
    adapters = _run_adapters(native); native_bundle = adapters["visual_merge_bundle"]
    def complete_bundle(output):
        result = native_bundle.invoke(output); manifest = json.loads((output / "visual/visual_manifest.json").read_text())
        (output / "evidence").mkdir(exist_ok=True); (output / "evidence/execution.json").write_text(json.dumps({**manifest["execution"], "output_inventory": manifest["files"]}))
        return result
    adapters["visual_merge_bundle"] = reconstruction.StageAdapter("visual_merge_bundle", complete_bundle)
    reconstruction.run_engine(contract, source, native, "native", runtime=runtime, adapters=adapters)
    native_report = compile_mechanical_draft(native, tmp_path / "native-candidate")
    assert native_report["review_flags"]["accepted"] is False
    assert native_report["authorities"]["validator_route"] == "native"
    assert native_report["authorities"]["replay"] is None
    assert native_report["authorities"]["source"]["sha256"]
    clean_environment = dict(os.environ)
    clean_environment.pop("PYTHONPATH", None)
    cli = subprocess.run(
        [sys.executable, "-B", "-m", "kb_creator.scripts.prepare_mineru_mechanical_draft", "--run-root", str(native), "--output", str(tmp_path / "native-cli-candidate")],
        cwd=Path(__file__).resolve().parents[2], env=clean_environment, capture_output=True, text=True,
    )
    assert cli.returncode == 0, cli.stderr
    assert json.loads(cli.stdout)["state"] == "mechanical_candidate_requires_review"
    def replay_adapters(run, *_):
        root = Path(run["local"]["run_root"]); stage = _run_adapters(root)["visual_merge_bundle"]
        def build(output):
            if not renderer: return stage.invoke(output)
            raw = root / "outputs/02-mineru-three-view"
            return bundle.build_bundle(raw_root=raw, output_root=output, raw_receipt=raw / "view-set.json", raw_receipt_sha256=bundle.sha256_file(raw / "view-set.json"), source=source, source_sha256=bundle.sha256_file(source), comparison=root / "outputs/03-compare-views/comparison.json", comparison_sha256=bundle.sha256_file(root / "outputs/03-compare-views/comparison.json"), pdftoppm=renderer, dpi=run["options"]["review_dpi"], expected_pages=6, reconstruction_contract=contract, prepared_manifest=root / "outputs/01-prepare-inputs/prepared/sample_pages.json", prepared_manifest_sha256=bundle.sha256_file(root / "outputs/01-prepare-inputs/prepared/sample_pages.json"))
        return {"visual_merge_bundle": reconstruction.StageAdapter("visual_merge_bundle", build)}
    monkeypatch.setattr(reconstruction, "production_run_adapters", replay_adapters)
    replay_root = tmp_path / "replay"
    replay.replay_run_engine(contract, source, native, replay_root, "replay", "03", runtime)
    replay_report = compile_mechanical_draft(replay_root, tmp_path / "replay-candidate")
    assert replay_report["review_flags"]["visual_reviewed"] is False
    assert replay_report["authorities"]["validator_route"] == "replay"
    assert replay_report["authorities"]["replay"]["bridge"]["sha256"]
    assert replay_report["authorities"]["replay"]["completion"]["sha256"]
