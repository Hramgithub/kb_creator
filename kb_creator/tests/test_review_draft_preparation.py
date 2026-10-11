import json
import importlib.util
from pathlib import Path

import pytest

from kb_creator.pipeline.review_draft_preparation import (
    _bind_issue_occurrences,
    _choice_issues,
    _selected_reader_text,
    prepare_review_draft_author_inputs,
    prepare_review_draft_inputs,
    validate_review_draft_author_input,
)


def _write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value), encoding="utf-8")


def _packet(run, blocks):
    views = {view: {"blocks": blocks} for view in ("original_pipeline_txt", "original_pipeline_ocr", "raster_pipeline_ocr")}
    _write(run / "outputs/04-visual-merge-bundle/merge_packets/pages/page-001.json", {"views": views})


@pytest.mark.parametrize("view_count,alternate", [(3, ""), (2, ""), (3, "visible alternate")])
def test_excluded_empty_region_keeps_geometry_and_does_not_claim_source_blank(tmp_path, view_count, alternate):
    mechanical, run = tmp_path / "mechanical", tmp_path / "run"
    views = ["original_pipeline_txt", "original_pipeline_ocr", "raster_pipeline_ocr"]
    blocks = [{"raw_index": 10, "text": "", "assets": [], "type": "text", "bbox": [643, 137, 813, 517]},
              {"raw_index": 11, "text": alternate, "assets": [], "type": "text", "bbox": [643, 137, 813, 517]}]
    _packet(run, blocks)
    _write(mechanical / "mechanical_draft.json", {"page_count": 1, "pages": [{"source_page": 1}],
           "manifest_sha256": "A" * 64, "run_root": str(run), "diagnostics": [],
           "authorities": {"source": {"sha256": "B" * 64}}})
    alternatives = [{"view": view, "blocks": [{"raw_index": 11 if index == 2 else 10,
                                              "text": alternate if index == 2 else ""}]}
                    for index, view in enumerate(views[:view_count])]
    _write(mechanical / "pages/page-001.json", {"semantic_role": "handout", "entries": [
        {"ordinal": 0, "chosen_view": views[0], "raw_index": 10, "disposition": "excluded_empty", "alternatives": alternatives}]})
    config = tmp_path / "config.json"
    _write(config, {"schema": "kb_creator.review_draft_preparation_config.v1", "forced_selections": []})
    result = prepare_review_draft_inputs(mechanical_dir=mechanical, config_path=config, output_dir=tmp_path / "out")
    if alternate:
        assert result["excluded_empty_sources"] == []
        assert result["all_three_views_empty_count"] == 0
        assert result["provisional_source_count"] == 1
        page = json.loads((tmp_path / "out/draft-pages/page-001.json").read_text())
        assert page["markdown"] == alternate
        return
    observation = result["excluded_empty_sources"][0]
    assert observation["source_content_verification"] == "unverified_from_empty_ocr"
    assert observation["all_three_views_empty"] is (view_count == 3 and not alternate)
    assert result["all_three_views_empty_count"] == int(view_count == 3 and not alternate)
    assert observation["alternate_text_available"] is bool(alternate)
    assert len(observation["witnesses"]) == view_count
    assert all(row["bbox"] == [643, 137, 813, 517] and row["block_type"] == "text" for row in observation["witnesses"])
    assert result["source_issues"]["issues"] == []  # Equal empty readings are not a lexical disagreement.
    page = json.loads((tmp_path / "out/draft-pages/page-001.json").read_text())
    assert page["markdown"] == alternate


def test_preparation_preserves_emitted_text_forces_source_only_line_and_reports_other_holds(tmp_path):
    mechanical = tmp_path / "mechanical"
    run = tmp_path / "run"
    manifest = {"page_count": 1, "pages": [{"source_page": 1}], "manifest_sha256": "A" * 64, "run_root": str(run),
                "authorities": {"source": {"sha256": "B" * 64}}, "diagnostics": []}
    page = {"source_page": 1, "semantic_role": "body", "entries": [
        {"ordinal": 0, "chosen_view": "original_pipeline_txt", "raw_index": 10, "disposition": "emitted", "reader_text": "Body"},
        {"ordinal": 1, "chosen_view": "raster_pipeline_ocr", "raw_index": 11, "disposition": "hold"},
        {"ordinal": 2, "chosen_view": "original_pipeline_txt", "raw_index": 12, "disposition": "hold"},
    ]}
    _packet(run, [{"raw_index": 10, "text": "Body", "assets": []}, {"raw_index": 11, "text": "STR 110", "assets": []}, {"raw_index": 12, "text": "", "assets": []}])
    _write(mechanical / "mechanical_draft.json", manifest); _write(mechanical / "pages/page-001.json", page)
    config = {"schema": "kb_creator.review_draft_preparation_config.v1", "forced_selections": [{
        "source_page": 1, "source_key": {"view": "raster_pipeline_ocr", "raw_index": 11},
        "expected_text_sha256": "789ABA06B1942A0EBA02DCC75B0E8FE5E7E4C0B08808474ABB6B387528A06613", "purpose": "structure", "after_ordinal": 1}]}
    config_path = tmp_path / "config.json"; _write(config_path, config)
    report = prepare_review_draft_inputs(mechanical_dir=mechanical, config_path=config_path, output_dir=tmp_path / "out")
    draft = json.loads((tmp_path / "out/draft-pages/page-001.json").read_text())
    assert report["unrenderable_source_count"] == 1
    assert draft["markdown"] == "Body\n\nSTR 110"
    assert {tuple(sorted(row.items())) for row in draft["selected_blocks"]} >= {
        (("purpose", "structure"), ("raw_index", 11), ("view", "raster_pipeline_ocr"))
    }
    assert draft["review"]["visual_reviewed"] is False


def test_preparation_projects_only_visible_reading_order_issue_with_narrow_selector(tmp_path):
    mechanical = tmp_path / "mechanical"
    diagnostic = {"page": 1, "code": "reading_order_conflict", "source_keys": [
        {"view": "original_pipeline_txt", "raw_index": 10}, {"view": "raster_pipeline_ocr", "raw_index": 11}],
        "alternatives": [{"blocks": [{"text": "Visible text"}]}, {"blocks": [{"text": "Different text"}]}]}
    run = tmp_path / "run"
    _packet(run, [{"raw_index": 10, "text": "Visible text", "assets": []}, {"raw_index": 11, "text": "Different text", "assets": []}])
    _write(mechanical / "mechanical_draft.json", {"page_count": 1, "pages": [{"source_page": 1}], "manifest_sha256": "A" * 64, "run_root": str(run),
        "authorities": {"source": {"sha256": "B" * 64}}, "diagnostics": [diagnostic]})
    _write(mechanical / "pages/page-001.json", {"semantic_role": "body", "entries": [{"ordinal": 0, "chosen_view": "original_pipeline_txt", "raw_index": 10, "disposition": "emitted", "reader_text": "Visible text"}]})
    config = tmp_path / "config.json"; _write(config, {"schema": "kb_creator.review_draft_preparation_config.v1", "forced_selections": []})
    result = prepare_review_draft_inputs(mechanical_dir=mechanical, config_path=config, output_dir=tmp_path / "out")
    issue = result["source_issues"]["issues"][0]
    assert issue["source_page"] == 1
    assert issue["source_selector"] == {"mechanical_diagnostic": {"code": "reading_order_conflict", "source_keys": diagnostic["source_keys"]}}
    assert issue["candidate_span"]["character_start"] == 0


def test_preparation_uses_same_entry_nonempty_alternative_for_empty_choice(tmp_path):
    mechanical = tmp_path / "mechanical"; run = tmp_path / "run"
    blocks = [{"raw_index": 10, "text": "", "assets": []}, {"raw_index": 11, "text": "STR 110", "assets": []}]
    _packet(run, blocks)
    _write(mechanical / "mechanical_draft.json", {"page_count": 1, "pages": [{"source_page": 1}],
        "manifest_sha256": "A" * 64, "run_root": str(run), "authorities": {"source": {"sha256": "B" * 64}}, "diagnostics": []})
    _write(mechanical / "pages/page-001.json", {"semantic_role": "body", "entries": [{"ordinal": 0,
        "chosen_view": "original_pipeline_txt", "raw_index": 10, "disposition": "hold",
        "alternatives": [{"view": "original_pipeline_txt", "blocks": [{"raw_index": 10, "text": ""}]},
                         {"view": "raster_pipeline_ocr", "blocks": [{"raw_index": 11, "text": "STR 110"}]}]}]})
    config = tmp_path / "config.json"; _write(config, {"schema": "kb_creator.review_draft_preparation_config.v1", "forced_selections": []})
    result = prepare_review_draft_inputs(mechanical_dir=mechanical, config_path=config, output_dir=tmp_path / "out")
    page = json.loads((tmp_path / "out/draft-pages/page-001.json").read_text())
    assert page["markdown"] == "STR 110"
    assert page["selected_blocks"] == [{"view": "raster_pipeline_ocr", "raw_index": 11, "purpose": "text"}]
    provisional = result["provisional_sources"]
    assert provisional[0]["provisional_source_key"] == {"view": "raster_pipeline_ocr", "raw_index": 11}
    assert provisional[0]["text_choice_open"] is False


def test_equal_diagnostic_readings_stay_in_structural_accounting(tmp_path):
    mechanical = tmp_path / "mechanical"; run = tmp_path / "run"; _packet(run, [{"raw_index": 10, "text": "Same", "assets": []}])
    diagnostic = {"page": 1, "code": "reading_order_conflict", "source_keys": [{"view": "original_pipeline_txt", "raw_index": 10}],
                  "alternatives": [{"blocks": [{"text": "Same"}]}, {"blocks": [{"text": "Same"}]}]}
    _write(mechanical / "mechanical_draft.json", {"page_count": 1, "pages": [{"source_page": 1}], "manifest_sha256": "A" * 64,
        "run_root": str(run), "authorities": {"source": {"sha256": "B" * 64}}, "diagnostics": [diagnostic]})
    _write(mechanical / "pages/page-001.json", {"semantic_role": "body", "entries": [{"ordinal": 0, "chosen_view": "original_pipeline_txt", "raw_index": 10, "disposition": "emitted", "reader_text": "Same"}]})
    config = tmp_path / "config.json"; _write(config, {"schema": "kb_creator.review_draft_preparation_config.v1", "forced_selections": []})
    result = prepare_review_draft_inputs(mechanical_dir=mechanical, config_path=config, output_dir=tmp_path / "out")
    assert result["source_issues"]["issues"] == []
    assert result["pending_issues"] == [{"diagnostic_index": 0, "source_page": 1, "code": "reading_order_conflict", "reason": "structural_only_equal_readings"}]


@pytest.mark.parametrize("code", ["semantic_conflict", "asset_difference"])
def test_preparation_projects_added_diagnostic_only_from_selected_reader_owner(tmp_path, code):
    mechanical = tmp_path / "mechanical"; run = tmp_path / "run"
    _packet(run, [{"raw_index": 10, "text": "Selected reading", "assets": []},
                  {"raw_index": 11, "text": "Alternate reading", "assets": []}])
    diagnostic = {"page": 1, "code": code, "source_keys": [
        {"view": "original_pipeline_txt", "raw_index": 10},
        {"view": "original_pipeline_ocr", "raw_index": 11}],
        "alternatives": [{"blocks": [{"text": "Selected reading"}]},
                         {"blocks": [{"text": "Alternate reading"}]}]}
    _write(mechanical / "mechanical_draft.json", {"page_count": 1, "pages": [{"source_page": 1}],
        "manifest_sha256": "A" * 64, "run_root": str(run), "authorities": {"source": {"sha256": "B" * 64}},
        "diagnostics": [diagnostic]})
    _write(mechanical / "pages/page-001.json", {"semantic_role": "body", "entries": [{"ordinal": 0,
        "chosen_view": "original_pipeline_txt", "raw_index": 10, "disposition": "emitted",
        "reader_text": "Selected reading"}]})
    config = tmp_path / "config.json"; _write(config, {"schema": "kb_creator.review_draft_preparation_config.v1", "forced_selections": []})
    result = prepare_review_draft_inputs(mechanical_dir=mechanical, config_path=config, output_dir=tmp_path / "out")
    issue = result["source_issues"]["issues"]
    assert len(issue) == 1
    assert issue[0]["source_selector"]["mechanical_diagnostic"] == {"code": code, "source_keys": diagnostic["source_keys"]}
    assert issue[0]["source_excerpt_en"] == "Selected reading"


def test_added_diagnostics_reject_equal_asset_only_missing_and_ambiguous_owners():
    def diagnostic(code, texts):
        return {"page": 1, "code": code, "source_keys": [
            {"view": "original_pipeline_txt", "raw_index": 10},
            {"view": "original_pipeline_ocr", "raw_index": 11}],
            "alternatives": [{"blocks": [{"text": text}]} for text in texts]}
    manifest = {"authorities": {"source": {"sha256": "A" * 64}}}
    cases = [
        (diagnostic("semantic_conflict", ["Equal", "Equal"]), "Equal", {("original_pipeline_txt", 10): "Equal"}),
        (diagnostic("asset_difference", ["One", "Two"]), "One", {}),
        (diagnostic("semantic_conflict", ["One", "Two"]), "Missing", {("original_pipeline_txt", 10): "One"}),
        (diagnostic("asset_difference", ["One", "Two"]), "One\n\nTwo", {
            ("original_pipeline_txt", 10): "One", ("original_pipeline_ocr", 11): "Two"}),
    ]
    for row, markdown, owners in cases:
        issues, pending = _choice_issues({**manifest, "diagnostics": [row]}, {1: markdown},
                                         selected_reader_text={1: owners})
        assert issues == []
        assert pending == []


def test_selected_reader_map_deduplicates_same_key_text_and_asset(tmp_path):
    run = tmp_path / "run"
    _packet(run, [{"raw_index": 10, "text": "Caption", "assets": []}])
    draft = tmp_path / "draft-pages/page-001.json"
    _write(draft, {"source_page": 1, "markdown": "Caption", "selected_blocks": [
        {"view": "original_pipeline_txt", "raw_index": 10, "purpose": "text"},
        {"view": "original_pipeline_txt", "raw_index": 10, "purpose": "asset"},
    ]})
    readers = _selected_reader_text({"run_root": str(run)}, [draft])
    assert readers == {1: {("original_pipeline_txt", 10): "Caption"}}


@pytest.mark.parametrize("relative_output,structural_route", [(False, False), (True, False), (False, True)])
def test_production_composer_binds_actual_pending_alternative_before_authoring(monkeypatch, tmp_path, relative_output, structural_route):
    """The producer binds divergent source input without inventing an audit deferral."""
    from types import SimpleNamespace
    from kb_creator.pipeline.identity import canonical_bytes, file_identity, sha256_bytes
    from kb_creator.pipeline import reconstruction_replay as replay, reconstruction_replay_resume as resume
    from kb_creator.pipeline.mechanical_reconstruction import compile_mechanical_draft
    from kb_creator.scripts import author_reviewed_semantic_decisions as author
    fixture_path = Path(__file__).with_name("test_reconstruction_replay_resume.py")
    fixture_spec = importlib.util.spec_from_file_location("n72_composer_fixture", fixture_path)
    fixture = importlib.util.module_from_spec(fixture_spec); assert fixture_spec.loader is not None; fixture_spec.loader.exec_module(fixture)
    authorities, _, _ = fixture._fixture(tmp_path)
    run = authorities.run_root
    run_json = json.loads((run / "run.json").read_text(encoding="utf-8"))
    source_path = Path(run_json["local"]["source_path"])
    run_json["source"] = {"path_hint": source_path.name, **file_identity(source_path)}
    _write(run / "run.json", run_json)
    _write(run / "outputs/01-prepare-inputs/prepared/sample_pages.json", {"pages": []})
    _write(run / "replay/completion.json", {"state": "fixture"})
    original = run / "outputs/04-visual-merge-bundle/visual/original_pipeline_txt/pages/page-001.png"
    original.parent.mkdir(parents=True); original.write_bytes(b"synthetic source visual")
    visual_manifest = run / "outputs/04-visual-merge-bundle/visual/visual_manifest.json"
    visual = json.loads(visual_manifest.read_text(encoding="utf-8")); visual.pop("manifest_sha256")
    visual["files"].append({"path": "visual/original_pipeline_txt/pages/page-001.png", **file_identity(original)})
    from kb_creator.pipeline.manifests import sealed
    _write(visual_manifest, sealed("kb_creator.mineru_visual_merge_bundle.v3", visual, digest_key="manifest_sha256"))
    queue = json.loads((run / "review/review_queue.json").read_text(encoding="utf-8"))
    monkeypatch.setattr(replay, "validate_replayed_prefix", lambda _: authorities)
    monkeypatch.setattr(replay, "validate_replay_artifacts_for_consumption", lambda _: None)
    monkeypatch.setattr(resume, "validate_replay_review_queue", lambda _: SimpleNamespace(
        run_root=run, queue=queue, queue_path=run / "review/review_queue.json",
        comparison_path=run / "outputs/03-compare-views/comparison.json"))
    packet = json.loads((run / "outputs/04-visual-merge-bundle/merge_packets/pages/page-001.json").read_text(encoding="utf-8"))
    packet["schema"] = "kb_creator.mineru_merge_packet.v1"
    source = packet["views"]["original_pipeline_txt"]["blocks"][0]
    source["text"] = "# Stable heading"
    packet["views"]["original_pipeline_ocr"]["blocks"][0]["text"] = "Alternative heading"
    packet["pairwise"] = {
        f"{left}__vs__{right}": {"bbox_matches": [{"left_raw_index": packet["views"][left]["blocks"][0]["raw_index"],
                                                       "right_raw_index": packet["views"][right]["blocks"][0]["raw_index"], "bbox_iou": 1.0}],
                                 "left_unmatched": [], "right_unmatched": []}
        for left, right in (("original_pipeline_txt", "original_pipeline_ocr"),
                            ("original_pipeline_txt", "raster_pipeline_ocr"),
                            ("original_pipeline_ocr", "raster_pipeline_ocr"))
    }
    packet_path = run / "outputs/04-visual-merge-bundle/merge_packets/pages/page-001.json"
    _write(packet_path, packet)
    queue.pop("queue_sha256")
    queue["items"][0]["merge_packet"] = {"path": "merge_packets/pages/page-001.json", **file_identity(packet_path)}
    _write(run / "review/review_queue.json", sealed("kb_creator.review_queue.v2", queue, digest_key="queue_sha256"))
    queue = json.loads((run / "review/review_queue.json").read_text(encoding="utf-8"))
    comparison_path = run / "outputs/03-compare-views/comparison.json"
    comparison = json.loads(comparison_path.read_text(encoding="utf-8")); comparison.pop("comparison_sha256")
    comparison["views"]["original_pipeline_txt"]["blocks"][0].update({"text": source["text"]})
    if structural_route:
        comparison["pairwise"]["original_pipeline_txt__vs__original_pipeline_ocr"] = {"semantic_conflicts": [
            {"kind": "image_heading_overlap", "left_raw_index": source["raw_index"], "right_raw_index": 1},
        ]}
    _write(comparison_path, sealed("kb_creator.mineru_multi_view_comparison.v3", comparison, digest_key="comparison_sha256"))
    queue.pop("queue_sha256")
    queue["comparison"] = {"path": "outputs/03-compare-views/comparison.json", **file_identity(comparison_path)}
    _write(run / "review/review_queue.json", sealed("kb_creator.review_queue.v2", queue, digest_key="queue_sha256"))
    queue = json.loads((run / "review/review_queue.json").read_text(encoding="utf-8"))
    mechanical = tmp_path / "mechanical"
    compiled = compile_mechanical_draft(run, mechanical, authority_validator=lambda *_args, **_kwargs: authorities)
    assert compiled["diagnostics"], compiled
    config = tmp_path / "config.json"; _write(config, {"schema": "kb_creator.review_draft_preparation_config.v1", "forced_selections": []})
    spec = tmp_path / "semantic-spec.json"; _write(spec, {
        "semantic_structure_profile": "reviewed_role_outline_and_partitions_v2",
        "pages": [{"source_page": 1, "role_contract": {"role": "body", "group_id": "synthetic-composer"},
                   "units": [{"id": "heading", "kind": "heading", "representation": "atx_heading",
                              "raw_indices": [source["raw_index"]], "start": source["text"], "end": source["text"],
                              "heading_level": 1},
                             ]}], "ocr_equivalence_classes": []})
    monkeypatch.chdir(tmp_path)
    composed = prepare_review_draft_author_inputs(mechanical_dir=mechanical, config_path=config,
        semantic_spec_paths=[spec], output_dir=Path("composed") if relative_output else tmp_path / "composed", binding_root=tmp_path)
    assert composed["preparation"]["pending_issues"] == []
    input_path = Path(composed["draft_input"]["path"])
    draft_pages = Path(composed["draft_pages"])
    review_input = json.loads(input_path.read_text(encoding="utf-8"))
    assert review_input["source_issues"]["issues"][0]["candidate_span"] == {"semantic_unit_id": "heading", "source_page": 1}
    assert json.loads((draft_pages / "page-001.json").read_text())["review"]["visual_reviewed"] is False
    archive = {"schema": "kb_creator.review_draft_archive_consumption.v1", "state": "read_only_consumption",
        "source_run_root": str(run), "target_run_root": str(run), "source_sha256": run_json["source"]["sha256"],
        "source": {"bridge_sha256": authorities.bridge_sha256}, "target": {"bridge_sha256": authorities.bridge_sha256}, "checked_paths": {
        "stage_02_root": str(run / "outputs/02-mineru-three-view"), "comparison": str(comparison_path),
        "merge_packets": str(run / "outputs/04-visual-merge-bundle/merge_packets"),
        "visual_manifest": str(visual_manifest), "geometry_plan": str(run / "outputs/04-visual-merge-bundle/visual/geometry_plan.json"),
        "review_queue": str(run / "review/review_queue.json"),
    }}
    from kb_creator.pipeline import review_draft as review_draft_module
    monkeypatch.setattr(review_draft_module, "build_archive_consumption_context", lambda **_unused: archive)
    if structural_route:
        from kb_creator.pipeline.review_draft_preparation import compose_structural_role_issue_successor
        preview = tmp_path / "structural-preview"
        baseline = tmp_path / "structural-baseline"
        _write(baseline / "decision_set.json", {"reviewed_allowlist": {"path": "reviewed_allowlist.v3.json"}})
        _write(baseline / "reviewed_allowlist.v3.json", {
            "schema": "kb_creator.ai_merge_fidelity_reviewed_allowlist.v3", "authority": {},
            "substitutions": [], "source_text_exclusions": [], "visual_text_assertions": [], "ocr_equivalence_classes": []})
        _write(baseline / "pages/page-001.json", json.loads((draft_pages / "page-001.json").read_text()))
        author.author(run, baseline, preview, [Path(path) for path in composed["spec_paths"]])
        successor = tmp_path / "structural-input.json"
        result = compose_structural_role_issue_successor(input_path=input_path, binding_root=tmp_path,
            run_root=run, authored_preview_root=preview, destination=successor)
        assert result["structural_issue_count"] == 1
        assert result["preserved_lexical_issue_count"] == 1
        input_path = successor
    authored = tmp_path / "authored"
    author.author_drafts(run, draft_pages, authored, [Path(path) for path in composed["spec_paths"]],
                         mode="review_draft", draft_input=input_path, binding_root=tmp_path)
    assert json.loads((authored / "review-draft-stage05-audit.json").read_text(encoding="utf-8"))["passed"] is True
    if structural_route:
        import copy
        from kb_creator.pipeline.structural_role_issues import derive_structural_role_conflict_proofs
        current_decisions = {1: json.loads((authored / "pages/page-001.json").read_text(encoding="utf-8"))}
        current_audit = json.loads((authored / "review-draft-stage05-audit.json").read_text(encoding="utf-8"))
        proof_args = dict(review_input=json.loads(input_path.read_text(encoding="utf-8")),
            input_path=input_path, binding_root=tmp_path, run_root=run, decisions=current_decisions,
            packets={1: json.loads(packet_path.read_text(encoding="utf-8"))},
            comparison=json.loads(comparison_path.read_text(encoding="utf-8")), stage05_pages=current_audit["pages"])
        assert len(derive_structural_role_conflict_proofs(**proof_args)) == 1
        for damage in ("comparison", "packet", "audit_mapping", "record_index", "duplicate_owner", "purpose"):
            altered = copy.deepcopy(proof_args)
            if damage == "comparison": altered["comparison"]["pairwise"] = {}
            elif damage == "packet": altered["packets"][1]["views"]["original_pipeline_txt"]["blocks"][0]["text"] = "Forged"
            elif damage == "audit_mapping":
                row = next(row for row in altered["stage05_pages"][0]["ordered_proof_stream"] if row["kind"] == "selected")
                row["markdown_span"][0] += 1
            else:
                issue = next(row for row in altered["review_input"]["source_issues"]["issues"] if row["kind"] == "source_structure_role_pending")
                selector = issue["source_selector"]["comparison_structural_role_v1"]
                if damage == "record_index": selector["comparison_records"][0]["semantic_conflict_index"] += 1
                elif damage == "purpose": selector["provisional_selection_purpose"] = "asset"
                else:
                    duplicate = copy.deepcopy(issue); duplicate["issue_id"] += "-duplicate"
                    altered["review_input"]["source_issues"]["issues"].append(duplicate)
                altered["review_input"].pop("input_sha256")
                altered["review_input"]["input_sha256"] = sha256_bytes(canonical_bytes(altered["review_input"]))
                altered["input_path"] = tmp_path / (damage + ".json")
                _write(altered["input_path"], altered["review_input"])
            with pytest.raises(ValueError):
                derive_structural_role_conflict_proofs(**altered)
    from kb_creator.pipeline import review_draft_materialization as route
    from kb_creator.scripts import materialize_mineru_ai_merge as materializer
    from kb_creator.pipeline.five_step_intake import FiveStepIntakeError, build_review_master_en, verify_master_en
    monkeypatch.setattr(route, "build_archive_consumption_context", lambda **_unused: archive)
    descriptor = route.verify_final_review_draft(run_root=run, authored_root=authored, input_path=input_path,
                                                  evidence_path=authored / "review-draft-evidence.json", binding_root=tmp_path)
    if structural_route:
        assert len(descriptor["structural_role_proofs"]) == 1
    materialized = tmp_path / "materialized"
    materializer.materialize(Path(descriptor["bundle_root"]), Path(descriptor["raw_root"]),
                             Path(descriptor["decisions_root"]), materialized, review_draft_authority=descriptor,
                             review_draft_binding_root=tmp_path)
    master = tmp_path / "master"
    wrong_root = tmp_path / "wrong-root"; wrong_root.mkdir()
    with pytest.raises(FiveStepIntakeError):
        build_review_master_en(materialized, authored / "review-draft-evidence.json", tmp_path / "wrong-master",
                               binding_root=wrong_root)
    build_review_master_en(materialized, authored / "review-draft-evidence.json", master, binding_root=tmp_path)
    assert verify_master_en(master, binding_root=tmp_path)["state"] == "verified_review_draft"
    if structural_route:
        bindings = json.loads((master / "ISSUE_EN_BINDINGS.v2.json").read_text(encoding="utf-8"))["bindings"]
        assert len(bindings) == 2 and len({row["issue_id"] for row in bindings}) == 2
        # Lexical evidence includes the source heading marker; the structural
        # excerpt may omit it. Both exact spans overlap the same selected heading.
        assert max(row["master_reader_span"]["character_start"] for row in bindings) < min(row["master_reader_span"]["character_end"] for row in bindings)
        master_text = (master / "MASTER_EN.md").read_text(encoding="utf-8")
        for row in bindings:
            span = row["master_reader_span"]
            assert master_text[span["character_start"]:span["character_end"]] == row["reader_projection"]["reader_text"]
    assert validate_review_draft_author_input(input_path=input_path, binding_root=tmp_path)["open_source_issue_count"] == (2 if structural_route else 1)
    config.write_text("{}", encoding="utf-8")
    with pytest.raises(ValueError, match="composer_config"):
        validate_review_draft_author_input(input_path=input_path, binding_root=tmp_path)
    missing_spec = tmp_path / "missing-semantic-spec.json"
    _write(missing_spec, {"semantic_structure_profile": "reviewed_role_outline_and_partitions_v2", "pages": [], "ocr_equivalence_classes": []})
    restored_config = tmp_path / "config-restored.json"
    _write(restored_config, {"schema": "kb_creator.review_draft_preparation_config.v1", "forced_selections": []})
    with pytest.raises(ValueError, match="semantic spec page domain"):
        prepare_review_draft_author_inputs(mechanical_dir=mechanical, config_path=restored_config,
            semantic_spec_paths=[missing_spec], output_dir=tmp_path / "missing-composed", binding_root=tmp_path)


def test_repeated_visible_text_issue_binds_by_source_occurrence_not_substring():
    manifest = {"authorities": {"source": {"sha256": "A" * 64}}, "diagnostics": [{
        "page": 1, "code": "ocr_text_disagreement", "source_keys": [
            {"view": "original_pipeline_txt", "raw_index": 22},
            {"view": "original_pipeline_ocr", "raw_index": 22},
        ], "alternatives": [{"blocks": [{"text": "NPC"}]}, {"blocks": [{"text": "NPC wording"}]}],
    }]}
    issues, pending = _choice_issues(manifest, {1: "NPC\n\nNPC"})
    assert pending == [] and len(issues) == 1
    bound = _bind_issue_occurrences(issues, {
        (1, "original_pipeline_txt", 22): ["npc-two"],
        (1, "original_pipeline_ocr", 22): ["npc-two"],
    })
    assert bound[0]["candidate_span"] == {"semantic_unit_id": "npc-two", "source_page": 1}


def test_pending_issue_follows_coverage_owner_to_unique_canonical_semantic_unit():
    issue = {"issue_id": "attacks", "source_page": 152,
             "source_selector": {"mechanical_diagnostic": {"source_keys": [
                 {"view": "original_pipeline_txt", "raw_index": 2974},
                 {"view": "original_pipeline_ocr", "raw_index": 2974},
             ]}}}
    bound = _bind_issue_occurrences([issue], {
        (152, "raster_pipeline_ocr", 2978): ["statblock-attacks"],
    }, coverage_source_to_canonical={
        (152, "original_pipeline_txt", 2974): (152, "raster_pipeline_ocr", 2978),
    })
    assert bound[0]["candidate_span"] == {"semantic_unit_id": "statblock-attacks", "source_page": 152}
    with pytest.raises(ValueError, match="missing semantic occurrence"):
        _bind_issue_occurrences([issue], {}, coverage_source_to_canonical={
            (152, "original_pipeline_txt", 2974): (152, "raster_pipeline_ocr", 2978),
        })


def test_pending_ordinary_prose_carries_one_exact_selected_source_key_without_semantic_unit():
    issue = {"issue_id": "ordinary", "source_page": 108,
             "source_selector": {"mechanical_diagnostic": {"source_keys": [
                 {"view": "original_pipeline_txt", "raw_index": 44},
                 {"view": "original_pipeline_ocr", "raw_index": 44},
             ]}}}
    bound = _bind_issue_occurrences([issue], {}, selected_source_keys={
        108: {("original_pipeline_txt", 44)},
    })
    assert bound[0]["candidate_span"] == {
        "source_key": {"view": "original_pipeline_txt", "raw_index": 44},
        "source_page": 108, "binding": "ordered_selected_source_v1",
    }
    with pytest.raises(ValueError, match="missing semantic occurrence"):
        _bind_issue_occurrences([issue], {}, selected_source_keys={
            108: {("original_pipeline_txt", 44), ("original_pipeline_ocr", 44)},
        })
