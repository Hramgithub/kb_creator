import json
from pathlib import Path

import pytest

from kb_creator.pipeline.text_segmentation import (
    ALLOWLIST_FIELD,
    TextSegmentationError,
    allowlist_v3_keys,
    derive_claim,
    text_segmentation_claims,
    validate_claim,
)


def normalize(text: str) -> str:
    return "".join(char for char in text.casefold() if char.isalnum())


def unit(page, view, index, text, bbox):
    normalized = normalize(text)
    return {"source_page": page, "view_id": view, "raw_index": index, "block_type": "text", "bbox": bbox, "original_text_sha256": "A" * 64, "normalized_text_sha256": "B" * 64, "normalized_character_count": len(normalized), "_text": text}


def fixture():
    selected = unit(1, "original_pipeline_txt", 10, "Alpha beta", [0, 0, 900, 100])
    alternate_a = unit(1, "raster_pipeline_ocr", 20, "Alpha", [0, 0, 450, 100])
    alternate_b = unit(1, "raster_pipeline_ocr", 21, "betx", [450, 0, 900, 100])
    refs = {tuple(row[key] for key in ("source_page", "view_id", "raw_index")): row for row in (selected, alternate_a, alternate_b)}
    reader = normalize("Alpha beta")
    mapping = {(1, "original_pipeline_txt", 10): {"unit": {key: value for key, value in selected.items() if not key.startswith("_")}, "markdown_span": [0, len(reader)]}}
    visual = {"path": "outputs/04-visual-merge-bundle/visual/original_pipeline_txt/pages/page-001.png", "bytes": 1, "sha256": "C" * 64}
    selector = {"claim_id": "generic-split", "source_page": 1, "selected": [{"view_id": "original_pipeline_txt", "raw_index": 10}], "alternates": [{"view_id": "raster_pipeline_ocr", "raw_index": 20}, {"view_id": "raster_pipeline_ocr", "raw_index": 21}], "layout_relation": "figure_wrap", "alternate_token_corrections": [{"unit": {"view_id": "raster_pipeline_ocr", "raw_index": 21}, "from_token": "betx", "to_token": "beta", "source_region": {"view_id": "raster_pipeline_ocr", "coordinate_space": "mineru_page_1000_top_left_v1", "bbox": [450, 0, 900, 100]}, "visual_verdict": "replacement_visible_in_source", "rationale": "source visibly has beta"}], "visual_verdict": "selected_sequence_matches_source_and_alternate_segmentation", "rationale": "figure interrupts one reader sentence"}
    return refs, mapping, reader, visual, selector


def metrics(left, right):
    return {"iou": 0.5, "smaller_box_coverage": 1.0}


def test_legacy_allowlist_remains_closed_and_claim_field_is_optional():
    base = {"schema": "x", "authority": {}, "substitutions": [], "source_text_exclusions": [], "visual_text_assertions": [], "ocr_equivalence_classes": []}
    assert text_segmentation_claims(base) == []
    assert allowlist_v3_keys({**base, ALLOWLIST_FIELD: []})
    with pytest.raises(TextSegmentationError):
        allowlist_v3_keys({**base, "unknown": []})


def test_derives_and_replays_closed_split_claim_with_reviewed_token_repair():
    refs, mappings, reader, visual, selector = fixture()
    claim = derive_claim(selector, references=refs, selected_mappings=mappings, reader_text=reader, source_visual=visual, normalize=normalize)
    assert claim["proof"]["normalized_span"] == [0, len(reader)]
    assert claim["proof"]["alternate_partition_end_offsets"] == [5, len(reader)]
    assert validate_claim(claim, references=refs, selected_mappings=mappings, reader_text=reader, visual_inventory={visual["path"]: {"bytes": 1, "sha256": "C" * 64}}, normalize=normalize, spatial_metrics=metrics, automatic_disposition=lambda row: None) == claim


def test_token_correction_source_region_accepts_contained_bbox():
    refs, mappings, reader, visual, selector = fixture()
    selector["alternate_token_corrections"][0]["source_region"]["bbox"] = [500, 10, 800, 90]
    claim = derive_claim(selector, references=refs, selected_mappings=mappings, reader_text=reader, source_visual=visual, normalize=normalize)
    assert claim["alternate_token_corrections"][0]["source_region"]["bbox"] == [500, 10, 800, 90]


@pytest.mark.parametrize(
    "region",
    [
        {"view_id": "original_pipeline_txt", "coordinate_space": "mineru_page_1000_top_left_v1", "bbox": [450, 0, 900, 100]},
        {"view_id": "raster_pipeline_ocr", "coordinate_space": "wrong_space", "bbox": [450, 0, 900, 100]},
        {"view_id": "raster_pipeline_ocr", "coordinate_space": "mineru_page_1000_top_left_v1", "bbox": [900, 0, 901, 100]},
        {"view_id": "raster_pipeline_ocr", "coordinate_space": "mineru_page_1000_top_left_v1", "bbox": [450, 100, 400, 90]},
        {"view_id": "raster_pipeline_ocr", "coordinate_space": "mineru_page_1000_top_left_v1", "bbox": [450, 0, float("nan"), 100]},
    ],
)
def test_token_correction_source_region_rejects_wrong_or_invalid_proof(region):
    refs, mappings, reader, visual, selector = fixture()
    selector["alternate_token_corrections"][0]["source_region"] = region
    with pytest.raises(TextSegmentationError, match="source region"):
        derive_claim(selector, references=refs, selected_mappings=mappings, reader_text=reader, source_visual=visual, normalize=normalize)


@pytest.mark.parametrize("mutation", ["missing_alternate", "reordered", "stale_visual", "ambiguous_token", "same_region_zero_overlap", "competing_selected", "all_automatic"])
def test_segmentation_claims_fail_closed(mutation):
    refs, mappings, reader, visual, selector = fixture()
    if mutation == "missing_alternate":
        selector["alternates"].pop()
    if mutation == "reordered":
        selector["alternates"].reverse()
    if mutation == "ambiguous_token":
        refs[(1, "raster_pipeline_ocr", 21)]["_text"] = "betx betx"
    claim = derive_claim(selector, references=refs, selected_mappings=mappings, reader_text=reader, source_visual=visual, normalize=normalize) if mutation not in {"missing_alternate", "reordered", "ambiguous_token"} else None
    if mutation in {"missing_alternate", "reordered", "ambiguous_token"}:
        with pytest.raises(TextSegmentationError):
            derive_claim(selector, references=refs, selected_mappings=mappings, reader_text=reader, source_visual=visual, normalize=normalize)
        return
    if mutation == "stale_visual":
        inventory = {visual["path"]: {"bytes": 1, "sha256": "D" * 64}}
        geometry = metrics
        automatic = lambda row: None
    elif mutation == "same_region_zero_overlap":
        claim["layout_relation"] = "same_region"
        inventory = {visual["path"]: {"bytes": 1, "sha256": "C" * 64}}
        geometry = lambda left, right: {"iou": 0.0, "smaller_box_coverage": 1.0}
        automatic = lambda row: None
    elif mutation == "competing_selected":
        extra = unit(1, "original_pipeline_txt", 11, "other", [0, 0, 900, 100])
        refs[(1, "original_pipeline_txt", 11)] = extra
        mappings[(1, "original_pipeline_txt", 11)] = {"unit": {key: value for key, value in extra.items() if not key.startswith("_")}, "markdown_span": [0, 1]}
        inventory = {visual["path"]: {"bytes": 1, "sha256": "C" * 64}}
        geometry = metrics
        automatic = lambda row: None
    else:
        inventory = {visual["path"]: {"bytes": 1, "sha256": "C" * 64}}
        geometry = metrics
        automatic = lambda row: "included_equivalent_exact"
    with pytest.raises(TextSegmentationError):
        validate_claim(claim, references=refs, selected_mappings=mappings, reader_text=reader, visual_inventory=inventory, normalize=normalize, spatial_metrics=geometry, automatic_disposition=automatic)


def test_real_p2ax2_packet_units_are_available_without_book_data_mutation():
    root = Path(__file__).parents[1] / "working/cursed-idol/r01/upstream/cursed-idol/reconstruction/reconstruction-001/outputs/04-visual-merge-bundle/merge_packets/pages"
    expected = [
        (20, "original_pipeline_txt", (278,), "raster_pipeline_ocr", (278, 279, 280)),
        (24, "original_pipeline_txt", (397,), "raster_pipeline_ocr", (402, 404)),
        (30, "original_pipeline_txt", (511, 512), "raster_pipeline_ocr", (518,)),
        (30, "original_pipeline_txt", (525, 526), "raster_pipeline_ocr", (531, 532)),
    ]
    for page, selected_view, selected_indices, alternate_view, alternate_indices in expected:
        packet = json.loads((root / f"page-{page:03d}.json").read_text(encoding="utf-8"))
        blocks = {view: {block["raw_index"] for block in data["blocks"]} for view, data in packet["views"].items()}
        assert set(selected_indices) <= blocks[selected_view]
        assert set(alternate_indices) <= blocks[alternate_view]


@pytest.mark.parametrize("requires_claim", [False, True])
def test_public_v3_audit_replays_a_derived_claim_before_automatic_dispositions(requires_claim):
    from kb_creator.scripts.audit_mineru_ai_merge_fidelity import _make_unit, _normalized, _v3_page_context, audit_v3_content
    packet = {"source_page": 1, "views": {}}
    blocks = {
        "original_pipeline_txt": [{"raw_index": 0, "source_page": 1, "type": "text", "bbox": [0, 0, 900, 100], "text": "Alpha beta"}],
        "original_pipeline_ocr": [],
        "raster_pipeline_ocr": [
            {"raw_index": 20, "source_page": 1, "type": "text", "bbox": [0, 0, 450, 100], "text": "Alpha"},
            {"raw_index": 21, "source_page": 1, "type": "text", "bbox": [450, 0, 900, 100], "text": "beta"},
        ],
    }
    packet["views"] = {view: {"blocks": rows} for view, rows in blocks.items()}
    if requires_claim:
        packet["views"]["raster_pipeline_ocr"]["blocks"][1]["bbox"] = [450, 200, 900, 300]
    decision = {"source_page": 1, "markdown": "Alpha beta", "selected_blocks": [{"view": "original_pipeline_txt", "raw_index": 0, "purpose": "text"}], "assets": []}
    geometry = {"observed_geometry": [{"view_id": view, "source_page": 1, "media_box_coordinates": ["0", "0", "595", "841"], "crop_box_coordinates": ["0", "0", "595", "841"], "rotation_degrees": 0, "user_unit": "1", "effective_displayed_size_points": ["595", "841"]} for view in blocks]}
    errors = []
    context = _v3_page_context(1, packet, decision, geometry, errors)
    assert not errors
    refs = {(1, view, index): value for (view, index), value in context["references"].items()}
    mappings = {(1, row["unit"]["view_id"], row["unit"]["raw_index"]): row for row in context["mappings"]}
    visual = {"path": "outputs/04-visual-merge-bundle/visual/original_pipeline_txt/pages/page-001.png", "bytes": 1, "sha256": "C" * 64}
    selector = {"claim_id": "audit-split", "source_page": 1, "selected": [{"view_id": "original_pipeline_txt", "raw_index": 0}], "alternates": [{"view_id": "raster_pipeline_ocr", "raw_index": 20}, {"view_id": "raster_pipeline_ocr", "raw_index": 21}], "layout_relation": "figure_wrap", "alternate_token_corrections": [], "visual_verdict": "selected_sequence_matches_source_and_alternate_segmentation", "rationale": "reviewed figure wrap"}
    claim = derive_claim(selector, references=refs, selected_mappings=mappings, reader_text=context["rendered"], source_visual=visual, normalize=_normalized)
    allowlist = {"schema": "kb_creator.ai_merge_fidelity_reviewed_allowlist.v3", "authority": {}, "substitutions": [], "source_text_exclusions": [], "visual_text_assertions": [], "ocr_equivalence_classes": [], "text_segmentation_claims": [claim]}
    if not requires_claim:
        with pytest.raises(ValueError, match="no otherwise-unaccounted alternate"):
            audit_v3_content({1: packet}, {1: decision}, allowlist=allowlist, geometry=geometry, visual_inventory={visual["path"]: {"bytes": 1, "sha256": "C" * 64}})
        return
    report = audit_v3_content({1: packet}, {1: decision}, allowlist=allowlist, geometry=geometry, visual_inventory={visual["path"]: {"bytes": 1, "sha256": "C" * 64}})
    assert report["passed"]
    assert [row["disposition"] for row in report["pages"][0]["units"]] == ["included_selected", "included_reviewed_segmentation", "included_reviewed_segmentation"]


def test_p2ax3_real_p038_full_unit_corrections_are_exact_and_hash_bound():
    selected_a = unit(38, "original_pipeline_ocr", 657, "An Exclusive Premiere Engagemenu FRIDAY.MARCH12.1937- Evelusive viewing to follow.", [0, 0, 900, 100])
    selected_b = unit(38, "original_pipeline_ocr", 658, "Event starts at 6pm sharp in the evening. Exclusive viewing to follow.", [0, 100, 900, 200])
    alternate_a = unit(38, "raster_pipeline_ocr", 665, "An Exclusive Premiere Engagement An Exclusive Premiere", [0, 0, 900, 100])
    alternate_b = unit(38, "raster_pipeline_ocr", 666, "，1937- FRIDAY.MARCH12. Event starts at 6pm sharp in the evening. Exclusive viewing to follow. in the evening. Exclusive viewing to follow.", [0, 100, 900, 200])
    rows = (selected_a, selected_b, alternate_a, alternate_b)
    refs = {tuple(row[key] for key in ("source_page", "view_id", "raw_index")): row for row in rows}
    reader = normalize("An Exclusive Premiere Engagement — FRIDAY, MARCH 12, 1937 — Event starts at 6pm sharp in the evening. Exclusive viewing to follow.")
    mappings = {(38, "original_pipeline_ocr", 657): {"unit": {key: value for key, value in selected_a.items() if not key.startswith("_")}, "markdown_span": [0, 46]}, (38, "original_pipeline_ocr", 658): {"unit": {key: value for key, value in selected_b.items() if not key.startswith("_")}, "markdown_span": [46, 103]}}
    visual = {"path": "outputs/04-visual-merge-bundle/visual/original_pipeline_txt/pages/page-038.png", "bytes": 1, "sha256": "C" * 64}
    selector = {"claim_id": "p038-invitation-title-date-event", "source_page": 38, "selected": [{"view_id": "original_pipeline_ocr", "raw_index": 657}, {"view_id": "original_pipeline_ocr", "raw_index": 658}], "alternates": [{"view_id": "raster_pipeline_ocr", "raw_index": 665}, {"view_id": "raster_pipeline_ocr", "raw_index": 666}], "layout_relation": "same_region", "alternate_token_corrections": [], "alternate_full_unit_corrections": [{"unit": {"view_id": "raster_pipeline_ocr", "raw_index": 665}, "before": alternate_a["_text"], "after": "An Exclusive Premiere Engagement", "visual_verdict": "corrected_full_unit_visible_in_source", "rationale": "duplicate title prefix"}, {"unit": {"view_id": "raster_pipeline_ocr", "raw_index": 666}, "before": alternate_b["_text"], "after": "— FRIDAY, MARCH 12, 1937 — Event starts at 6pm sharp in the evening. Exclusive viewing to follow.", "visual_verdict": "corrected_full_unit_visible_in_source", "rationale": "scrambled date and duplicate event tail"}], "visual_verdict": "selected_sequence_matches_source_and_alternate_segmentation", "rationale": "one printed handout region"}
    claim = derive_claim(selector, references=refs, selected_mappings=mappings, reader_text=reader, source_visual=visual, normalize=normalize)
    assert claim["proof"] == {"normalized_span": [0, 103], "expected_normalized_sha256": "05ACCEB0BBEA7F2F643729DDE64439741C97A91858ACBFCD334B129CDC8F4F9D", "alternate_partition_end_offsets": [29, 103]}
    assert validate_claim(claim, references=refs, selected_mappings=mappings, reader_text=reader, visual_inventory={visual["path"]: {"bytes": 1, "sha256": "C" * 64}}, normalize=normalize, spatial_metrics=metrics, automatic_disposition=lambda row: None) == claim


def test_author_public_replay_stage06_and_promotion_close_split_full_unit_claim(monkeypatch, tmp_path):
    """Only Stage01-04 prefix validation is mocked; public author/replay/promotion run."""
    import hashlib
    import importlib.util
    from kb_creator.pipeline import reconstruction_promotion as promotion
    from kb_creator.pipeline import reconstruction_replay as replay
    from kb_creator.pipeline import reconstruction_replay_resume as resume
    from kb_creator.pipeline.identity import deterministic_inventory, file_identity
    from kb_creator.pipeline.manifests import sealed
    from kb_creator.scripts import author_reviewed_semantic_decisions as author

    source = Path(__file__).with_name("test_reconstruction_replay_resume.py")
    module_spec = importlib.util.spec_from_file_location("segmentation_resume_fixture", source)
    fixture = importlib.util.module_from_spec(module_spec); assert module_spec.loader is not None; module_spec.loader.exec_module(fixture)
    authorities, _, _ = fixture._fixture(tmp_path); run = authorities.run_root
    import shutil
    from reportlab.pdfgen.canvas import Canvas
    renderer = Path(shutil.which("pdftoppm")); assert renderer.is_file()
    source_pdf = tmp_path / "source.pdf"; canvas = Canvas(str(source_pdf)); canvas.drawString(72, 720, "segmentation"); canvas.save()
    def file_sha(path): return hashlib.sha256(path.read_bytes()).hexdigest().upper()
    run_data = json.loads((run / "run.json").read_text(encoding="utf-8")); run_data["source"]["sha256"] = file_sha(source_pdf); run_data["local"] = {"source_path": str(source_pdf), "common_paths": {"pdftoppm": str(renderer)}}; (run / "run.json").write_text(json.dumps(run_data), encoding="utf-8")
    geometry_path = run / "outputs/04-visual-merge-bundle/visual/geometry_plan.json"; geometry = json.loads(geometry_path.read_text(encoding="utf-8")); geometry.pop("plan_sha256"); geometry["renderer"] = {"sha256": file_sha(renderer)}; geometry = sealed("kb_creator.mineru_geometry_plan.v2", geometry, digest_key="plan_sha256"); geometry_path.write_text(json.dumps(geometry), encoding="utf-8")
    packet_path = run / "outputs/04-visual-merge-bundle/merge_packets/pages/page-001.json"
    packet = json.loads(packet_path.read_text(encoding="utf-8"))
    selected = {"raw_index": 0, "source_page": 1, "type": "text", "bbox": [0, 0, 900, 100], "text": "Alpha beta"}
    first = {"raw_index": 20, "source_page": 1, "type": "text", "bbox": [0, 0, 450, 100], "text": "Alpha"}
    second = {"raw_index": 21, "source_page": 1, "type": "text", "bbox": [450, 0, 900, 100], "text": "beta beta"}
    packet["views"]["original_pipeline_txt"]["blocks"] = [selected]
    packet["views"]["original_pipeline_ocr"]["blocks"] = []
    packet["views"]["raster_pipeline_ocr"]["blocks"] = [first, second]
    packet_path.write_text(json.dumps(packet), encoding="utf-8")
    comparison_path = run / "outputs/03-compare-views/comparison.json"
    comparison = json.loads(comparison_path.read_text(encoding="utf-8")); comparison.pop("comparison_sha256")
    comparison["views"]["original_pipeline_txt"]["blocks"] = [selected]
    comparison["views"]["original_pipeline_ocr"]["blocks"] = []
    comparison["views"]["raster_pipeline_ocr"]["blocks"] = [first, second]
    comparison = sealed("kb_creator.mineru_multi_view_comparison.v3", comparison, digest_key="comparison_sha256")
    comparison_path.write_text(json.dumps(comparison), encoding="utf-8")
    visual_file = run / "outputs/04-visual-merge-bundle/visual/original_pipeline_txt/pages/page-001.png"
    visual_file.parent.mkdir(parents=True); visual_file.write_bytes(b"segmentation source visual")
    manifest_path = run / "outputs/04-visual-merge-bundle/visual/visual_manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8")); manifest.pop("manifest_sha256")
    manifest["files"].append({"path": "visual/original_pipeline_txt/pages/page-001.png", **file_identity(visual_file)})
    manifest = sealed("kb_creator.mineru_visual_merge_bundle.v3", manifest, digest_key="manifest_sha256")
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
    queue_path = run / "review/review_queue.json"
    queue = json.loads(queue_path.read_text(encoding="utf-8")); queue.pop("queue_sha256")
    queue["source_sha256"] = file_sha(source_pdf)
    queue["comparison"] = {"path": "outputs/03-compare-views/comparison.json", **file_identity(comparison_path)}
    queue["items"][0]["merge_packet"] = {"path": "merge_packets/pages/page-001.json", **file_identity(packet_path)}
    queue = sealed("kb_creator.review_queue.v2", queue, digest_key="queue_sha256"); queue_path.write_text(json.dumps(queue), encoding="utf-8")
    monkeypatch.setattr(replay, "validate_replayed_prefix", lambda _root: authorities)
    monkeypatch.setattr(resume, "validate_replayed_prefix", lambda _root: authorities)
    drafts = tmp_path / "drafts"; drafts.mkdir()
    (drafts / "page-001.json").write_text(json.dumps({"schema": "kb_creator.mineru_ai_page_decision.v1", "source_page": 1, "semantic_role": "body", "overlay_preference": "original_pipeline_txt", "selected_blocks": [{"view": "original_pipeline_txt", "raw_index": 0, "purpose": "text"}], "markdown": "# Alpha beta", "assets": [], "unresolved": [], "review": {"visual_reviewed": True, "notes": "reviewed segmentation"}}), encoding="utf-8")
    spec = tmp_path / "spec.json"
    spec.write_text(json.dumps({"semantic_structure_profile": "reviewed_role_outline_and_partitions_v2", "pages": [{"source_page": 1, "role_contract": {"role": "body", "group_id": "segmentation"}, "units": [{"id": "heading", "kind": "heading", "representation": "atx_heading", "raw_indices": [0], "start": "# Alpha beta", "end": "# Alpha beta", "heading_level": 1}]}], "text_segmentation_claims": [{"claim_id": "synthetic-split-full-unit", "source_page": 1, "selected": [{"view_id": "original_pipeline_txt", "raw_index": 0}], "alternates": [{"view_id": "raster_pipeline_ocr", "raw_index": 20}, {"view_id": "raster_pipeline_ocr", "raw_index": 21}], "layout_relation": "same_region", "alternate_token_corrections": [], "alternate_full_unit_corrections": [{"unit": {"view_id": "raster_pipeline_ocr", "raw_index": 21}, "before": "beta beta", "after": "beta", "visual_verdict": "corrected_full_unit_visible_in_source", "rationale": "source contains one beta"}], "visual_verdict": "selected_sequence_matches_source_and_alternate_segmentation", "rationale": "one split source line"}]}), encoding="utf-8")
    authored = tmp_path / "authored"; author.author_drafts(run, drafts, authored, [spec])
    assert resume.replay_resume_engine(run, authored / "decision_set.json", authored)["state"] == "candidate_ready_for_reconstruction_qa"
    audit = json.loads((run / "outputs/05-fidelity-audit/audit.json").read_text(encoding="utf-8")); assert audit["passed"] is True
    assert [row["disposition"] for row in audit["pages"][0]["units"]] == ["included_selected", "included_reviewed_segmentation", "included_reviewed_segmentation"]
    submission = resume.load_replay_submission(authorities); decision_set = json.loads((submission.root / "decision_set.json").read_text(encoding="utf-8")); run_data = json.loads((run / "run.json").read_text(encoding="utf-8"))
    promotion._validate_candidate(run, {"source": {"page_count": 1}, "page_roles": [{"first_page": 1, "last_page": 1, "role": "body"}], "scope": {"required_entities": {"numbered_player_handouts": 0}}}, submission.root, decision_set, run=run_data, fidelity_path=run / "outputs/05-fidelity-audit/audit.json", fidelity=audit, candidate_root=run / "outputs/06-materialize-candidate", replay_bridge_sha256=authorities.bridge_sha256, replay_submission=submission.receipt, stage6_files=deterministic_inventory(run / "outputs/06-materialize-candidate"))
