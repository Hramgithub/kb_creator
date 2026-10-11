"""Real compact R0/queue coverage for a composite source-choice anchor."""
from __future__ import annotations

import importlib.util
import json
import shutil
import sys
import pytest
from copy import deepcopy
from pathlib import Path
from types import SimpleNamespace

from kb_creator.pipeline import language_continuation as continuation
from kb_creator.pipeline import reconstruction_replay as replay
from kb_creator.pipeline import reconstruction_replay_resume as resume
from kb_creator.pipeline import source_choice_translation as choices
from kb_creator.pipeline.five_step_intake import build_review_master_en, verify_master_en
from kb_creator.pipeline.identity import file_identity, sha256_bytes
from kb_creator.pipeline.manifests import sealed
from kb_creator.pipeline.mechanical_reconstruction import compile_mechanical_draft
from kb_creator.pipeline.review_draft_preparation import prepare_review_draft_author_inputs
from kb_creator.pipeline.review_draft_materialization import verify_final_review_draft
from kb_creator.pipeline.source_choice_successor_preparation import prepare_source_choice_successor
from kb_creator.scripts import author_reviewed_semantic_decisions as author
from kb_creator.scripts import materialize_mineru_ai_merge as materializer


VIEWS = ("original_pipeline_txt", "original_pipeline_ocr", "raster_pipeline_ocr")
BASELINE = "1D6"
ALTERNATE = "ID6"
PREFIX = "Composite prefix: "
SUFFIX = " :composite suffix"
CONTAINER = PREFIX + BASELINE + SUFFIX
SECOND_BASELINE = "2D8"
SECOND_ALTERNATE = "I\nD8"
MIDDLE = "; middle punctuation: "
RETAINED = " [retained source question]"
MULTICHOICE_CONTAINER = PREFIX + BASELINE + MIDDLE + SECOND_BASELINE + RETAINED + SUFFIX


def _write(path: Path, value: object) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return path


def _reconstruction_fixture(tmp_path: Path):
    fixture_path = Path(__file__).with_name("test_reconstruction_replay_resume.py")
    spec = importlib.util.spec_from_file_location("composite_replay_fixture", fixture_path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module._fixture(tmp_path)[0]


def _coverage_factory(tmp_path: Path, run: Path, source: Path, packet_path: Path,
                      txt_raws: list[int], raster_raw: int | list[int], *, multichoice: bool = False,
                      whole_block_correction: bool = False, retained_strong: bool = False) -> dict[str, str]:
    canonical_key = {"source_page": 1, "view_id": "raster_pipeline_ocr", "raw_index": raster_raw}
    claim_rows = []
    baseline_rows = [BASELINE] + ([SECOND_BASELINE] if multichoice else [])
    if whole_block_correction:
        baseline_rows = ["Bad first paragraph.", "Bad second paragraph."]
    if retained_strong:
        baseline_rows = ["Seed.", "Bad second paragraph."]
    spans = [
        [len(PREFIX), len(PREFIX) + len(BASELINE)],
        [len(PREFIX) + len(BASELINE) + len(MIDDLE),
         len(PREFIX) + len(BASELINE) + len(MIDDLE) + len(SECOND_BASELINE)],
    ]
    if whole_block_correction:
        spans = [[0, len(text)] for text in baseline_rows]
    for index, (txt_raw, baseline, span) in enumerate(zip(txt_raws, baseline_rows, spans)):
        if whole_block_correction:
            canonical_key = {"source_page": 1, "view_id": "raster_pipeline_ocr", "raw_index": raster_raw[index]}
        source_key = {"source_page": 1, "view_id": "original_pipeline_txt", "raw_index": txt_raw}
        fact_id = f"txt-tail-transcription-{index + 1}"
        claim_rows.append({
            "claim_id": f"txt-tail-in-raster-container-{index + 1}",
            "proof_mode": "continuation_subspan",
            "source_key": source_key,
            "canonical_key": canonical_key,
            "reader_page": 1,
            "reader_span": span,
            "semantic_container": "complete_selected_block",
            "validated_fact_id": fact_id,
        })
    selectors = _write(tmp_path / "coverage-selectors.json", {
        "schema": "kb_creator.reader_text_coverage_selectors.v1",
        "claims": claim_rows,
    })
    visual = run / "outputs/04-visual-merge-bundle/visual/original_pipeline_txt/pages/page-001.png"
    source_record = {"path": str(source.resolve()), **file_identity(source)}
    visual_record = {"path": str(visual.resolve()), **file_identity(visual)}
    packet_record = {"path": str(packet_path.resolve()), **file_identity(packet_path)}
    fact_rows = []
    for index, (claim, baseline) in enumerate(zip(claim_rows, baseline_rows), start=1):
        reviewed = _write(tmp_path / f"transcription-review-{index}.json", {
            "schema": "kb_creator.reviewed_source_transcription.v1",
            "approval": "source_image_bound_exact_transcription",
            "reviewer": "composite integration fixture",
            "source_key": claim["source_key"],
            "canonical_key": claim["canonical_key"],
            "source_pdf": source_record,
            "source_visual": visual_record,
            "packet": packet_record,
            "exact_text": baseline,
            "scope": "one diagnostic tail inside one selected raster container",
        })
        fact_rows.append({
            "schema": "kb_creator.source_transcription_fact.v1",
            "fact_id": claim["validated_fact_id"],
            "source_key": claim["source_key"],
            "canonical_key": claim["canonical_key"],
            "source_visual": visual_record,
            "evidence_kind": "source_render_exact_transcription",
            "evidence": {"path": reviewed.name, **file_identity(reviewed)},
            "exact_text": baseline,
            "approval": "source_image_bound_exact_transcription",
        })
    evidence = _write(tmp_path / "coverage-evidence.json", {
        "schema": "kb_creator.reader_text_coverage_evidence.v1",
        "facts": fact_rows,
    })
    return {"factory_id": "composite-tail", "selectors_path": str(selectors),
            "evidence_path": str(evidence)}


def _build_r0(tmp_path: Path, monkeypatch, *, multichoice: bool = False,
              whole_block_correction: bool = False, corrected_alias: bool = False,
              wrapped_source: bool = False, label_partition: bool = False,
              empty_region: bool = False, empty_region_kind: str = "heading",
              quoted_dialogue: bool = False, prose_role: bool = False,
              retained_strong: bool = False, source_marker_binding: bool = False,
              lexical_unowned_second: bool = False,
              owner_successor_fixture: bool = False) -> dict[str, Path | dict]:
    assert not lexical_unowned_second or whole_block_correction
    assert not owner_successor_fixture or (quoted_dialogue and lexical_unowned_second)
    assert not corrected_alias or whole_block_correction
    assert not prose_role or (whole_block_correction and not corrected_alias)
    assert not wrapped_source or (whole_block_correction and not corrected_alias)
    assert not label_partition or (whole_block_correction and not corrected_alias and not wrapped_source)
    assert not empty_region or (whole_block_correction and not corrected_alias and not wrapped_source and not label_partition)
    assert empty_region_kind in {"heading", "handout"}
    assert not quoted_dialogue or (whole_block_correction and not any((corrected_alias, wrapped_source, label_partition, empty_region)))
    assert not retained_strong or (whole_block_correction and not any((corrected_alias, wrapped_source, label_partition, empty_region, quoted_dialogue, prose_role)))
    dialogue_text = "TS: And then what?\n\nES: The officer never returned."
    dialogue_markdown = "> TS: And then what?\n>\n> ES: The officer never returned."
    empty_reader = ("## " if empty_region_kind == "heading" else "> ") + "Source-only heading?"
    corrected_view = "raster_pipeline_ocr" if corrected_alias else "original_pipeline_txt"
    authorities = _reconstruction_fixture(tmp_path)
    run = authorities.run_root
    run_json = json.loads((run / "run.json").read_text(encoding="utf-8"))
    source = Path(run_json["local"]["source_path"])
    run_json["source"] = {"path_hint": source.name, **file_identity(source)}
    _write(run / "run.json", run_json)
    _write(run / "outputs/01-prepare-inputs/prepared/sample_pages.json", {"pages": []})
    _write(run / "replay/completion.json", {"state": "fixture"})

    visual_manifest_path = run / "outputs/04-visual-merge-bundle/visual/visual_manifest.json"
    visual_manifest = json.loads(visual_manifest_path.read_text(encoding="utf-8"))
    visual_manifest.pop("manifest_sha256")
    for view in VIEWS:
        image = run / f"outputs/04-visual-merge-bundle/visual/{view}/pages/page-001.png"
        image.parent.mkdir(parents=True, exist_ok=True)
        image.write_bytes(("composite fixture " + view).encode("utf-8"))
        visual_manifest["files"].append({"path": f"visual/{view}/pages/page-001.png", **file_identity(image)})
    _write(visual_manifest_path, sealed("kb_creator.mineru_visual_merge_bundle.v3",
                                       visual_manifest, digest_key="manifest_sha256"))

    packet_path = run / "outputs/04-visual-merge-bundle/merge_packets/pages/page-001.json"
    packet = json.loads(packet_path.read_text(encoding="utf-8"))
    packet["schema"] = "kb_creator.mineru_merge_packet.v1"
    texts = dict(zip(VIEWS, (BASELINE, ALTERNATE, "")))
    if whole_block_correction:
        assert not multichoice
        texts = dict(zip(VIEWS, ("Bad first paragraph.", "Alternate first paragraph.", "Bad first paragraph.")))
        if wrapped_source:
            texts["original_pipeline_txt"] = "ood first para  \ngraph."
            texts["raster_pipeline_ocr"] = texts["original_pipeline_txt"]
        if label_partition:
            texts["original_pipeline_txt"] = "SE A MONSTER SUMMONING COVER-UP MART IN ’S BEACH"
            texts["raster_pipeline_ocr"] = texts["original_pipeline_txt"]
        if retained_strong:
            texts = dict(zip(VIEWS, ("Seed.", "Seed", "Seed.")))
    secondary_texts = dict(zip(VIEWS, (SECOND_BASELINE, SECOND_ALTERNATE, "")))
    if whole_block_correction:
        secondary_texts = dict(zip(VIEWS, ("Bad second paragraph.", "Alternate second paragraph.", "Bad second paragraph.")))
    two_blocks = multichoice or whole_block_correction
    raws: dict[str, int | list[int]] = {}
    for view in VIEWS:
        block = packet["views"][view]["blocks"][0]
        block["text"] = texts[view]
        raw_indices = [block["raw_index"]]
        if two_blocks:
            secondary = dict(block)
            secondary["raw_index"] = max(
                row["raw_index"] for item in packet["views"].values() for row in item["blocks"]
            ) + 1
            secondary["text"] = secondary_texts[view]
            if prose_role:
                secondary["semantic_evidence"] = {**secondary.get("semantic_evidence", {}), "markdown_heading": True}
            packet["views"][view]["blocks"].append(secondary)
            raw_indices.append(secondary["raw_index"])
        raws[view] = raw_indices if two_blocks else raw_indices[0]
    raster_container = dict(packet["views"]["raster_pipeline_ocr"]["blocks"][0])
    raster_container["raw_index"] = max(
        row["raw_index"] for item in packet["views"].values() for row in item["blocks"]
    ) + 1
    raster_container["text"] = MULTICHOICE_CONTAINER if multichoice else CONTAINER
    if not whole_block_correction:
        packet["views"]["raster_pipeline_ocr"]["blocks"].append(raster_container)
    raws["selected_raster_container"] = raster_container["raw_index"]
    packet["pairwise"] = {
        f"{left}__vs__{right}": {
            "bbox_matches": [
                {"left_raw_index": raws[left][index] if two_blocks else raws[left],
                 "right_raw_index": raws[right][index] if two_blocks else raws[right], "bbox_iou": 1.0}
                for index in range(2 if two_blocks else 1)
            ],
            "left_unmatched": [], "right_unmatched": [],
        }
        for left, right in ((VIEWS[0], VIEWS[1]), (VIEWS[0], VIEWS[2]), (VIEWS[1], VIEWS[2]))
    }
    empty_raws = {}
    if empty_region:
        for view in VIEWS:
            raw = max(b["raw_index"] for v in packet["views"].values() for b in v["blocks"]) + 1
            empty_raws[view] = raw
            packet["views"][view]["blocks"].append({"raw_index": raw, "source_page": 1, "type": "text", "text": "", "bbox": [100, 10, 800, 50], "assets": []})
            if prose_role:
                packet["views"][view]["blocks"][-1]["semantic_evidence"] = {"text_level": 2}
        for pair, data in packet["pairwise"].items():
            left, right = pair.split("__vs__")
            data["bbox_matches"].append({"left_raw_index": empty_raws[left], "right_raw_index": empty_raws[right], "bbox_iou": 1.0})
    _write(packet_path, packet)

    comparison_path = run / "outputs/03-compare-views/comparison.json"
    comparison = json.loads(comparison_path.read_text(encoding="utf-8"))
    comparison.pop("comparison_sha256")
    for view in VIEWS:
        comparison["views"][view]["blocks"][0]["text"] = texts[view]
        if two_blocks:
            comparison["views"][view]["blocks"].append(dict(packet["views"][view]["blocks"][1]))
        if empty_region:
            comparison["views"][view]["blocks"].append(dict(packet["views"][view]["blocks"][-1]))
    if multichoice:
        comparison["pairwise"].setdefault("original_pipeline_txt__vs__raster_pipeline_ocr", {})["semantic_conflicts"] = [{
            "kind": "image_heading_overlap",
            "left_raw_index": raws["original_pipeline_txt"][0],
            "right_raw_index": raws["selected_raster_container"],
        }]
    _write(comparison_path, sealed("kb_creator.mineru_multi_view_comparison.v3",
                                   comparison, digest_key="comparison_sha256"))
    queue_path = run / "review/review_queue.json"
    queue = json.loads(queue_path.read_text(encoding="utf-8"))
    queue.pop("queue_sha256")
    queue["items"][0]["merge_packet"] = {"path": "merge_packets/pages/page-001.json",
                                             **file_identity(packet_path)}
    queue["comparison"] = {"path": "outputs/03-compare-views/comparison.json",
                           **file_identity(comparison_path)}
    _write(queue_path, sealed("kb_creator.review_queue.v2", queue, digest_key="queue_sha256"))
    queue = json.loads(queue_path.read_text(encoding="utf-8"))

    monkeypatch.setattr(replay, "validate_replayed_prefix", lambda _root: authorities)
    monkeypatch.setattr(replay, "validate_replay_artifacts_for_consumption", lambda _root: None)
    monkeypatch.setattr(resume, "validate_replay_review_queue", lambda _root: SimpleNamespace(
        run_root=run, queue=queue, queue_path=queue_path, comparison_path=comparison_path))

    mechanical = tmp_path / "mechanical"
    compile_mechanical_draft(run, mechanical, authority_validator=lambda _root: authorities)
    mechanical_manifest = json.loads((mechanical / "mechanical_draft.json").read_text(encoding="utf-8"))
    assert any(row["code"] == "three_view_content_mismatch"
               for row in mechanical_manifest["diagnostics"])

    reviewed = tmp_path / "reviewed-pages"
    _write(reviewed / "page-001.json", {
        "schema": "kb_creator.mineru_ai_page_decision.v1",
        "source_page": 1,
        "semantic_role": "body",
        "overlay_preference": "raster_pipeline_ocr",
        "selected_blocks": ([{"view": corrected_view, "raw_index": raw, "purpose": "text"}
                             for raw in raws[corrected_view]] if whole_block_correction else
                            [{"view": "raster_pipeline_ocr", "raw_index": raws["selected_raster_container"], "purpose": "text"}]),
        "markdown": texts["original_pipeline_txt"] + "\n\nBad second paragraph." if whole_block_correction else (MULTICHOICE_CONTAINER if multichoice else CONTAINER),
        "assets": [], "unresolved": [],
        "review": {"visual_reviewed": False, "notes": "composite R0 fixture"},
    })
    config = _write(tmp_path / "config.json", {
        "schema": "kb_creator.review_draft_preparation_config.v1", "forced_selections": []})
    semantic = _write(tmp_path / "semantic-spec.json", {
        "semantic_structure_profile": "reviewed_role_outline_and_partitions_v2",
        "pages": [{
            "source_page": 1,
            "role_contract": {"role": "body", "group_id": "composite-fixture"},
            "units": [{"id": "composite", "kind": "statblock", "representation": "semantic_span",
                       "view": "raster_pipeline_ocr", "raw_indices": [raws["raster_pipeline_ocr"] if whole_block_correction else raws["selected_raster_container"]],
                       "start": "Good whole paragraph." if whole_block_correction else (MULTICHOICE_CONTAINER if multichoice else CONTAINER),
                       "end": "Good whole paragraph." if whole_block_correction else (MULTICHOICE_CONTAINER if multichoice else CONTAINER)}],
        }],
        "ocr_equivalence_classes": [],
    })
    txt_raws = raws["original_pipeline_txt"] if two_blocks else [raws["original_pipeline_txt"]]
    factories = [_coverage_factory(
        tmp_path, run, source, packet_path, txt_raws,
        raws["raster_pipeline_ocr"] if whole_block_correction else raws["selected_raster_container"],
        multichoice=multichoice, whole_block_correction=whole_block_correction,
        retained_strong=retained_strong)]
    if whole_block_correction:
        # Direct selected TXT paragraphs have no cross-view coverage aliases.
        if not corrected_alias:
            _write(Path(factories[0]["selectors_path"]), {
                "schema": "kb_creator.reader_text_coverage_selectors.v1", "claims": []})
            _write(Path(factories[0]["evidence_path"]), {
                "schema": "kb_creator.reader_text_coverage_evidence.v1", "facts": []})
        semantic_data = json.loads(semantic.read_text(encoding="utf-8"))
        page_spec = semantic_data["pages"][0]
        page_spec["units"] = []
        page_spec["reviewed_block_corrections"] = [
            {"view": corrected_view, "raw_index": raw, "before": "Bad", "after": "Good", "reason": "synthetic whole paragraph correction"}
            for raw in raws[corrected_view]]
        page_spec["reviewed_prose_bindings_v1"] = [
            {"view": corrected_view, "raw_index": raw, "markdown_span": {"start_line": line, "end_line": line}}
            for raw, line in zip(raws[corrected_view], (1, 3))]
        page_spec["post_patches"] = [
            {"before": "Bad " + suffix, "after": "Good " + suffix, "count": 1}
            for suffix in ("first paragraph.", "second paragraph.")]
        if lexical_unowned_second:
            # R0 has an ordinary unchanged second paragraph. R1's ledger alone
            # changes it, so no R0 semantic or explicit prose owner is inherited.
            page_spec["reviewed_block_corrections"] = page_spec["reviewed_block_corrections"][:1]
            page_spec["reviewed_prose_bindings_v1"] = page_spec["reviewed_prose_bindings_v1"][:1]
            page_spec["post_patches"] = page_spec["post_patches"][:1]
        if retained_strong:
            corrected = "Seed. Retained continuation INT."
            marked = "Seed. Retained continuation **INT**."
            page_spec["reviewed_block_corrections"][0].update(
                before=texts[corrected_view], after=corrected,
                reason="synthetic sealed retained continuation")
            page_spec["post_patches"][0].update(before=texts[corrected_view], after=marked)
        if wrapped_source:
            page_spec["reviewed_block_corrections"][0].update(
                before=texts["original_pipeline_txt"], after="Good first paragraph.")
            page_spec["reviewed_prose_bindings_v1"][0]["source_layout"] = "soft_wrapped_paragraph_v1"
            page_spec["post_patches"][0].update(
                before=texts["original_pipeline_txt"], after="Good first paragraph.")
        if label_partition:
            raw = raws[corrected_view][0]
            source = texts[corrected_view]
            labels = ("SEA MONSTER", "SUMMONING", "COVER-UP", "MARTIN’S BEACH")
            starts = [source.index(value) for value in ("SE A MONSTER", "SUMMONING", "COVER-UP", "MART IN ’S BEACH")]
            page_spec["reviewed_block_corrections"] = [
                {"view": corrected_view, "raw_index": raw, "before": before, "after": after,
                 "reason": "synthetic source-confirmed cover label spacing"}
                for before, after in (("SE A MONSTER", labels[0]), ("MART IN ’S BEACH", labels[3]))
            ] + page_spec["reviewed_block_corrections"][1:]
            page_spec["reviewed_prose_bindings_v1"] = [page_spec["reviewed_prose_bindings_v1"][1]]
            page_spec["reviewed_prose_bindings_v1"][0]["markdown_span"] = {"start_line": 9, "end_line": 9}
            page_spec["post_patches"][0] = {"before": source, "after": "\n\n".join(labels), "count": 1}
            page_spec["units"] = [
                {"id": f"cover-label-{index}", "kind": "label", "representation": "semantic_span",
                 "view": corrected_view, "raw_indices": [raw], "start_line": 1 + index * 2,
                 "end_line": 1 + index * 2,
                 "source_fragments": [{"view": corrected_view, "raw_index": raw, "start": start, "end": end}]}
                for index, (start, end) in enumerate(zip(starts, starts[1:] + [len(source)]))
            ]
        if empty_region:
            raw = empty_raws["original_pipeline_txt"]
            page_spec["empty_source_selections"] = [{"view": "original_pipeline_txt", "raw_index": raw}]
            page_spec["post_patches"].append({"before": "Good first paragraph.", "after": empty_reader+"\n\nGood first paragraph.", "count": 1})
            for binding in page_spec["reviewed_prose_bindings_v1"]:
                binding["markdown_span"]["start_line"] += 2
                binding["markdown_span"]["end_line"] += 2
            page_spec["units"] = [{"id": "empty-region-heading", "kind": empty_region_kind, "representation": "atx_heading" if empty_region_kind == "heading" else "blockquote",
                                   "view": "original_pipeline_txt", "raw_indices": [raw], "start_line": 1, "end_line": 1,
                                   "heading_level": 2 if empty_region_kind == "heading" else None, "visual_assertion_ids": ["source-empty-heading"]}]
            semantic_data["visual_text_assertions"] = [{"assertion_id": "source-empty-heading", "source_page": 1,
                "text": "Source-only heading?", "bbox": [100,10,800,50], "relation": "within_selected_empty_text_region",
                "empty_source": {"view_id": "original_pipeline_txt", "raw_index": raw}, "rationale": "Synthetic source-only heading fixture."}]
        if quoted_dialogue:
            raw = raws[corrected_view][0]
            page_spec["reviewed_block_corrections"][0] = {
                "view": corrected_view, "raw_index": raw,
                "before": texts[corrected_view], "after": dialogue_text,
                "reason": "Synthetic source interview with two separate speaker paragraphs."}
            page_spec["post_patches"][0] = {
                "before": texts[corrected_view], "after": dialogue_markdown, "count": 1}
            page_spec["reviewed_prose_bindings_v1"] = [
                {"view": corrected_view, "raw_index": raws[corrected_view][1],
                 "markdown_span": {"start_line": 5, "end_line": 5}}]
            page_spec["units"] = [{
                "id": "source-interview", "kind": "handout", "representation": "blockquote",
                "view": corrected_view, "raw_indices": [raw], "start_line": 1, "end_line": 3}]
            if owner_successor_fixture:
                page_spec["reviewed_prose_bindings_v1"] = []
        if prose_role:
            binding = page_spec["reviewed_prose_bindings_v1"][-1]
            page_spec["reviewed_prose_roles_v1"] = [{
                "role": "ordinary_prose", "view": corrected_view,
                "raw_index": raws[corrected_view][1],
                "markdown_span": dict(binding["markdown_span"]),
                "visual_reviewed": True, "rationale": "Synthetic body paragraph misclassified as title.",
            }]
        _write(semantic, semantic_data)
    if source_marker_binding:
        if not whole_block_correction:
            raise ValueError("source-marker fixture requires a selected whole-block source")
        visual = run / "outputs/04-visual-merge-bundle/visual/original_pipeline_txt/pages/page-001.png"
        source_text = texts[corrected_view]
        marker_row = {
            "source_page": 1, "view": corrected_view, "raw_index": raws[corrected_view][0],
            "reader_preimage_sha256": sha256_bytes(source_text.encode("utf-8")).upper(),
            "visual": {"path": "outputs/04-visual-merge-bundle/visual/original_pipeline_txt/pages/page-001.png", **file_identity(visual)},
        }
        marker = _write(tmp_path / "marker-dispositions.json", {
            "schema": "kb_creator.source_marker_dispositions.v1", "candidates": [marker_row],
            "dispositions": [{**marker_row, "disposition": "non_list", "rationale": "Synthetic reviewed prose is not a list."}],
        })
        semantic_data = json.loads(semantic.read_text(encoding="utf-8"))
        semantic_data["source_marker_dispositions"] = {"path": marker.name, **file_identity(marker)}
        _write(semantic, semantic_data)
    composed = prepare_review_draft_author_inputs(
        mechanical_dir=mechanical, config_path=config, semantic_spec_paths=[semantic],
        output_dir=tmp_path / "composed", binding_root=tmp_path,
        reviewed_draft_pages=reviewed, coverage_factories=factories)
    review_input = json.loads(Path(composed["draft_input"]["path"]).read_text(encoding="utf-8"))
    issue = review_input["source_issues"]["issues"][0]
    if not whole_block_correction:
        assert issue["candidate_span"] == {"semantic_unit_id": "composite", "source_page": 1}

    archive = {
        "schema": "kb_creator.review_draft_archive_consumption.v1", "state": "read_only_consumption",
        "source_run_root": str(run), "target_run_root": str(run),
        "source_sha256": run_json["source"]["sha256"],
        "source": {"bridge_sha256": authorities.bridge_sha256},
        "target": {"bridge_sha256": authorities.bridge_sha256},
        "checked_paths": {
            "stage_02_root": str(run / "outputs/02-mineru-three-view"),
            "comparison": str(comparison_path),
            "merge_packets": str(packet_path.parent.parent),
            "visual_manifest": str(visual_manifest_path),
            "geometry_plan": str(run / "outputs/04-visual-merge-bundle/visual/geometry_plan.json"),
            "review_queue": str(queue_path),
        },
    }
    from kb_creator.pipeline import review_draft as review_draft_module
    from kb_creator.pipeline import review_draft_materialization as materialization_route
    monkeypatch.setattr(review_draft_module, "build_archive_consumption_context", lambda **_unused: archive)
    monkeypatch.setattr(materialization_route, "build_archive_consumption_context", lambda **_unused: archive)

    from kb_creator.pipeline.review_draft_preparation import compose_structural_role_issue_successor
    preview = tmp_path / "structural-preview"
    baseline = tmp_path / "structural-baseline"
    _write(baseline / "decision_set.json", {"reviewed_allowlist": {"path": "reviewed_allowlist.v3.json"}})
    _write(baseline / "reviewed_allowlist.v3.json", {
        "schema": "kb_creator.ai_merge_fidelity_reviewed_allowlist.v3", "authority": {},
        "substitutions": [], "source_text_exclusions": [], "visual_text_assertions": [],
        "ocr_equivalence_classes": []})
    _write(baseline / "pages/page-001.json", json.loads(
        (Path(composed["draft_pages"]) / "page-001.json").read_text(encoding="utf-8")))
    author.author(run, baseline, preview, [Path(path) for path in composed["spec_paths"]])
    structural_input = tmp_path / "structural-input.json"
    structural = compose_structural_role_issue_successor(
        input_path=Path(composed["draft_input"]["path"]), binding_root=tmp_path, run_root=run,
        authored_preview_root=preview, destination=structural_input)
    # The source-choice question is lexical and must survive this structural
    # successor unchanged; it is not itself a structural-role question.
    assert structural["structural_issue_count"] == (1 if multichoice else 0)
    lexical = [row for row in review_input["source_issues"]["issues"]
               if row["kind"] == "translation_source_choice_pending"]
    assert structural["preserved_lexical_issue_count"] == len(lexical)
    successor_issues = json.loads(structural_input.read_text(encoding="utf-8"))["source_issues"]["issues"]
    assert all(row in successor_issues for row in lexical)
    r0_input = Path(structural["input"]["path"])
    authored = tmp_path / "r0-authored"
    author.author_drafts(run, Path(composed["draft_pages"]), authored,
                         [Path(path) for path in composed["spec_paths"]], mode="review_draft",
                         draft_input=r0_input, binding_root=tmp_path)
    evidence = authored / "review-draft-evidence.json"
    descriptor = verify_final_review_draft(
        run_root=run, authored_root=authored, input_path=r0_input,
        evidence_path=evidence, binding_root=tmp_path)
    materialized = tmp_path / "r0-materialized"
    materializer.materialize(Path(descriptor["bundle_root"]), Path(descriptor["raw_root"]),
                             Path(descriptor["decisions_root"]), materialized,
                             review_draft_authority=descriptor, review_draft_binding_root=tmp_path)
    master = tmp_path / "r0-master"
    build_review_master_en(materialized, evidence, master, binding_root=tmp_path)
    assert verify_master_en(master, binding_root=tmp_path)["state"] == "verified_review_draft"
    expected_container = ("Good first paragraph.\n\nGood second paragraph." if whole_block_correction
                          else (MULTICHOICE_CONTAINER if multichoice else CONTAINER))
    if label_partition:
        expected_container = "SEA MONSTER\n\nSUMMONING\n\nCOVER-UP\n\nMARTIN’S BEACH\n\nGood second paragraph."
    if empty_region:
        expected_container = empty_reader + "\n\n" + expected_container
    if quoted_dialogue:
        expected_container = dialogue_markdown + "\n\nGood second paragraph."
    if retained_strong:
        expected_container = "Seed. Retained continuation **INT**.\n\nGood second paragraph."
    if lexical_unowned_second:
        expected_container = ((dialogue_markdown if quoted_dialogue else "Good first paragraph.")
                              + "\n\nBad second paragraph.")
    assert (master / "MASTER_EN.md").read_text(encoding="utf-8").endswith(expected_container + "\n")
    return {"run": run, "mechanical": mechanical, "master": master,
            "r0_input": r0_input,
            "draft_pages": Path(composed["draft_pages"]),
            "spec_paths": [Path(path) for path in composed["spec_paths"]],
            "raws": raws}


@pytest.mark.parametrize("choose_alternative", [False, True])
def test_real_corrected_interview_keeps_speaker_paragraphs_through_verified_queue(tmp_path, monkeypatch, choose_alternative):
    built = _build_r0(tmp_path, monkeypatch, whole_block_correction=True, quoted_dialogue=True)
    queue = Path(choices.prepare_v2(built["master"], built["mechanical"], tmp_path / "dialogue-queue", binding_root=tmp_path)["queue"])
    assert choices.verify_queue_v2(queue)["choices"] == 2
    master = (built["master"] / "MASTER_EN.md").read_text(encoding="utf-8")
    assert "> TS: And then what?\n>\n> ES: The officer never returned." in master
    assert "TS: And then what? ES:" not in master
    rows = json.loads(queue.read_text(encoding="utf-8"))["choices"]
    selected = []
    for row in rows:
        alternative = next(a for a in row["alternatives"] if a["alternative_id"] == row["provisional_alternative_id"])
        if choose_alternative and alternative["raw_text"] == "Bad first paragraph.":
            alternative = next(a for a in row["alternatives"] if a["raw_text"] == "Alternate first paragraph.")
            assert alternative["reader_text"] == "> Alternate first paragraph."
        selected.append((row["issue_id"], alternative["alternative_id"]))
    ledger = Path(choices.record_decisions_v2(queue, _submission_choices(queue, selected, tmp_path / "submission.json"), tmp_path / "ledger")["ledger"])
    r1 = prepare_source_choice_successor(input_path=built["r0_input"], binding_root=tmp_path,
        ledger_path=ledger, draft_pages=built["draft_pages"], spec_paths=built["spec_paths"], output_dir=tmp_path / "r1-input")
    authored = tmp_path / "r1-authored"
    author.author_drafts(built["run"], Path(r1["draft_pages"]), authored,
        [Path(p) for p in r1["spec_paths"]], mode="review_draft", draft_input=Path(r1["input"]["path"]), binding_root=tmp_path)
    evidence = authored / "review-draft-evidence.json"
    descriptor = verify_final_review_draft(run_root=built["run"], authored_root=authored,
        input_path=Path(r1["input"]["path"]), evidence_path=evidence, binding_root=tmp_path)
    materializer.materialize(Path(descriptor["bundle_root"]), Path(descriptor["raw_root"]), Path(descriptor["decisions_root"]),
        tmp_path / "r1-materialized", review_draft_authority=descriptor, review_draft_binding_root=tmp_path)
    build_review_master_en(tmp_path / "r1-materialized", evidence, tmp_path / "r1-master", binding_root=tmp_path)
    final = (tmp_path / "r1-master/MASTER_EN.md").read_text(encoding="utf-8")
    expected = master.replace("> TS: And then what?\n>\n> ES: The officer never returned.", "> Alternate first paragraph.") if choose_alternative else master
    assert final == expected


@pytest.mark.parametrize("kind", ["heading", "handout"])
def test_real_empty_region_heading_reaches_master_and_verified_queue(tmp_path, monkeypatch, kind):
    built = _build_r0(tmp_path, monkeypatch, whole_block_correction=True, empty_region=True, empty_region_kind=kind)
    result = choices.prepare_v2(built["master"], built["mechanical"], tmp_path / "source-choices", binding_root=tmp_path)
    assert choices.verify_queue_v2(Path(result["queue"]))["choices"] == 2
    assert "Source-only heading?" in (built["master"] / "MASTER_EN.md").read_text(encoding="utf-8")


def _submission(queue_path: Path, issue_id: str, alternative_id: str, path: Path) -> Path:
    return _write(path, {
        "schema": choices.SUBMISSION_SCHEMA_V2,
        "state": "submitted",
        "queue": {"path": str(queue_path.resolve()), **file_identity(queue_path)},
        "choices": [{"issue_id": issue_id, "disposition": "selected_alternative",
                     "alternative_id": alternative_id,
                     "reason": "Select the differing authenticated OCR witness.", "label": None}],
    })


def _submission_choices(queue_path: Path, selected: list[tuple[str, str]], path: Path) -> Path:
    return _write(path, {
        "schema": choices.SUBMISSION_SCHEMA_V2,
        "state": "submitted",
        "queue": {"path": str(queue_path.resolve()), **file_identity(queue_path)},
        "choices": [{"issue_id": issue_id, "disposition": "selected_alternative",
                     "alternative_id": alternative_id,
                     "reason": "Select the authenticated OCR witness for this disjoint slice.",
                     "label": None}
                    for issue_id, alternative_id in selected],
    })


def _prepare_composite_queue(tmp_path: Path, monkeypatch, *, multichoice: bool = False):
    renderer = shutil.which("pdftoppm")
    assert renderer is not None
    monkeypatch.setenv("KB_CREATOR_PDFTOPPM", renderer)
    built = _build_r0(tmp_path, monkeypatch, multichoice=multichoice)

    queue_root = tmp_path / "queue-v2"
    prepared = choices.prepare_v2(built["master"], built["mechanical"], queue_root,
                                  binding_root=tmp_path)
    queue_path = Path(prepared["queue"])
    queue = json.loads(queue_path.read_text(encoding="utf-8"))
    assert len(queue["choices"]) == (2 if multichoice else 1)
    choice = queue["choices"][0]
    replay_record = choice["raw_reader_replay"]
    assert replay_record["anchor_mode"] == "composite_source_slice_v1"
    assert replay_record["anchor_source_locator"] == {
        "view": "raster_pipeline_ocr", "raw_index": built["raws"]["selected_raster_container"], "field": "text"}
    assert replay_record["raw_source_slice"]["raw_character_start"] == len(PREFIX)
    assert replay_record["raw_source_slice"]["raw_character_end"] == len(PREFIX) + len(BASELINE)
    baseline = next(row for row in choice["alternatives"]
                    if row["alternative_id"] == replay_record["diagnostic_baseline_alternative_id"])
    alternate = next(row for row in choice["alternatives"]
                     if row["selectable"] and row["raw_text"] == ALTERNATE)
    assert baseline["source_locator"]["view"] == "original_pipeline_txt"
    assert baseline["raw_text"] == BASELINE
    assert alternate["source_locator"]["view"] == "original_pipeline_ocr"
    return built, queue_path, choice, alternate


def test_real_composite_r0_and_queue_keep_raster_provenance_separate_from_txt_baseline(tmp_path, monkeypatch):
    """The public queue derives a slice while R0 keeps the raster container."""
    _prepare_composite_queue(tmp_path, monkeypatch)


@pytest.mark.parametrize("corrected_alias", [False, True])
def test_real_whole_block_corrected_r0_reaches_v2_queue(tmp_path, monkeypatch, corrected_alias):
    renderer = shutil.which("pdftoppm"); assert renderer is not None
    monkeypatch.setenv("KB_CREATOR_PDFTOPPM", renderer)
    built = _build_r0(tmp_path, monkeypatch, whole_block_correction=True, corrected_alias=corrected_alias)
    queue = Path(choices.prepare_v2(built["master"], built["mechanical"], tmp_path / "whole-queue", binding_root=tmp_path)["queue"])
    assert choices.verify_queue_v2(queue)["choices"] == 2
    rows = json.loads(queue.read_text(encoding="utf-8"))["choices"]
    selected_view = "raster_pipeline_ocr" if corrected_alias else "original_pipeline_txt"
    assert {row["raw_reader_replay"]["anchor_source_locator"]["raw_index"] for row in rows} == set(built["raws"][selected_view])
    for row in rows:
        assert row["raw_reader_replay"]["base_policy"] == "reviewed_block_correction_v1"
        selected = next(a for a in row["alternatives"] if a["alternative_id"] == row["provisional_alternative_id"])
        assert selected["raw_text"].startswith("Bad ")
        assert selected["reader_text"].startswith("Good ")
        assert all(alternative["reader_text"] == alternative["raw_text"]
                   for alternative in row["alternatives"] if alternative is not selected)
    if corrected_alias:
        audit = json.loads((tmp_path / "r0-authored/review-draft-stage05-audit.json").read_text(encoding="utf-8"))
        aliases = [row["detail"] for row in audit["pages"][0]["units"]
                   if row["disposition"] == "included_covered_by_reader"]
        assert len(aliases) == 2
        original = "Bad first paragraph. Bad second paragraph."
        current = "Good first paragraph. Good second paragraph."
        for alias, raw, corrected in zip(aliases,
                ["Bad first paragraph.", "Bad second paragraph."],
                ["Good first paragraph.", "Good second paragraph."]):
            before_span = [original.index(raw), original.index(raw) + len(raw)]
            after_span = [current.index(corrected), current.index(corrected) + len(corrected)]
            assert alias["normalized_span"] == before_span
            assert alias["current_reader_normalized_span"] == after_span
            proof = alias["reviewed_correction_disposition"]
            assert proof["predecessor_normalized_span"] == before_span
            assert proof["reader_normalized_span"] == after_span
            assert proof["reader_normalized_sha256"] == sha256_bytes(corrected.encode())


def test_retained_corrected_reader_runs_through_v2_successor_route(tmp_path, monkeypatch):
    """A sealed expanded correction keeps its exact marked R0 reader in R1."""
    renderer = shutil.which("pdftoppm"); assert renderer is not None
    monkeypatch.setenv("KB_CREATOR_PDFTOPPM", renderer)
    built = _build_r0(tmp_path, monkeypatch, whole_block_correction=True, retained_strong=True)
    queue_path = Path(choices.prepare_v2(built["master"], built["mechanical"], tmp_path / "retained-queue",
                                         binding_root=tmp_path)["queue"])
    queue = json.loads(queue_path.read_text(encoding="utf-8"))
    retained = next(row for row in queue["choices"]
                    if row["reader_projection"]["reader_text"] == "Seed. Retained continuation **INT**.")
    selected = next(row for row in retained["alternatives"]
                    if row["alternative_id"] == retained["provisional_alternative_id"])
    assert selected["reader_adapter"]["policy"] == "reviewed_corrected_reader_retention_v1"
    assert [row["selectable"] for row in retained["alternatives"]].count(True) == 1
    assert all(row.get("nonselectable_reason") == "requires_separate_reviewed_source_correction"
               for row in retained["alternatives"] if row is not selected)
    blocked = next(row for row in retained["alternatives"] if row is not selected)
    selected_rows = [(row["issue_id"], row["provisional_alternative_id"])
                     for row in queue["choices"]]
    rejected_rows = [(issue_id, blocked["alternative_id"] if issue_id == retained["issue_id"] else alternative_id)
                     for issue_id, alternative_id in selected_rows]
    with pytest.raises(choices.SourceChoiceError, match="unknown or empty"):
        choices.record_decisions_v2(
            queue_path, _submission_choices(queue_path, rejected_rows, tmp_path / "blocked-submission.json"),
            tmp_path / "blocked-ledger")
    ledger = Path(choices.record_decisions_v2(
        queue_path, _submission_choices(queue_path, selected_rows, tmp_path / "retained-submission.json"),
        tmp_path / "retained-ledger")["ledger"])
    choices.verify_ledger_v2(ledger)
    r1 = prepare_source_choice_successor(
        input_path=built["r0_input"], binding_root=tmp_path, ledger_path=ledger,
        draft_pages=built["draft_pages"], spec_paths=built["spec_paths"], output_dir=tmp_path / "retained-r1")
    r1_input = Path(r1["input"]["path"])
    assert not [row for row in json.loads(r1_input.read_text(encoding="utf-8"))["source_issues"]["issues"]
                if row["issue_id"] == retained["issue_id"]]
    authored = tmp_path / "retained-authored"
    author.author_drafts(built["run"], Path(r1["draft_pages"]), authored,
                         [Path(path) for path in r1["spec_paths"]], mode="review_draft",
                         draft_input=r1_input, binding_root=tmp_path)
    descriptor = verify_final_review_draft(run_root=built["run"], authored_root=authored, input_path=r1_input,
                                           evidence_path=authored / "review-draft-evidence.json", binding_root=tmp_path)
    r0_text = (built["master"] / "MASTER_EN.md").read_text(encoding="utf-8")
    assert "Seed. Retained continuation **INT**." in r0_text
    decision = json.loads((Path(descriptor["decisions_root"]) / "page-001.json").read_text(encoding="utf-8"))
    assert decision["markdown"] == "Seed. Retained continuation **INT**.\n\nGood second paragraph."
    stream = json.loads((authored / "review-draft-stage05-audit.json").read_text(encoding="utf-8"))["pages"][0]["ordered_proof_stream"]
    assert any(row["kind"] == "linguistic_source_choice_v1" and row["r1_text"] == "Seed. Retained continuation **INT**."
               for row in stream)


def test_real_unowned_lexical_paragraph_preflights_and_authors(tmp_path, monkeypatch):
    """A sealed R1 choice changes prose outside all R0 semantic/prose owners."""
    renderer = shutil.which("pdftoppm")
    assert renderer is not None
    monkeypatch.setenv("KB_CREATOR_PDFTOPPM", renderer)
    built = _build_r0(tmp_path, monkeypatch, whole_block_correction=True,
                      lexical_unowned_second=True)
    queue_path = Path(choices.prepare_v2(built["master"], built["mechanical"],
                                         tmp_path / "lexical-queue", binding_root=tmp_path)["queue"])
    queue = json.loads(queue_path.read_text(encoding="utf-8"))
    second = next(row for row in queue["choices"]
                  if row["reader_projection"]["reader_text"] == "Bad second paragraph.")
    changed = next(row for row in second["alternatives"]
                   if row["selectable"] and row["reader_text"] == "Alternate second paragraph.")
    selections = [(row["issue_id"], changed["alternative_id"] if row is second
                   else row["provisional_alternative_id"]) for row in queue["choices"]]
    ledger = Path(choices.record_decisions_v2(queue_path,
        _submission_choices(queue_path, selections, tmp_path / "lexical-submission.json"),
        tmp_path / "lexical-ledger")["ledger"])
    choices.verify_ledger_v2(ledger)
    r1 = prepare_source_choice_successor(input_path=built["r0_input"], binding_root=tmp_path,
        ledger_path=ledger, draft_pages=built["draft_pages"], spec_paths=built["spec_paths"],
        output_dir=tmp_path / "lexical-r1")
    specs = [Path(path) for path in r1["spec_paths"]]
    row = json.loads(specs[0].read_text(encoding="utf-8"))["pages"][0]
    key = (row["linguistic_source_choice_corrections"][-1]["view"],
           row["linguistic_source_choice_corrections"][-1]["raw_index"])
    assert not any(key[1] in unit["raw_indices"] for unit in row["units"])
    assert not any((binding["view"], binding["raw_index"]) == key
                   for binding in row.get("reviewed_prose_bindings_v1", []))
    r1_input = Path(r1["input"]["path"])
    preflight = author.validate_spec(built["run"], None, specs,
        draft_pages=Path(r1["draft_pages"]), draft_input=r1_input, binding_root=tmp_path)
    assert preflight["correction_coverage"]["unbound_keys"] == 0
    copied_drafts = tmp_path / "unbound-draft-copy"
    shutil.copytree(Path(r1["draft_pages"]), copied_drafts)
    with pytest.raises(ValueError, match="differs from bound input path"):
        author.validate_spec(built["run"], None, specs, draft_pages=copied_drafts,
                             draft_input=r1_input, binding_root=tmp_path)
    authored = tmp_path / "lexical-authored"
    author.author_drafts(built["run"], Path(r1["draft_pages"]), authored, specs,
                         mode="review_draft", draft_input=r1_input, binding_root=tmp_path)
    descriptor = verify_final_review_draft(run_root=built["run"], authored_root=authored,
        input_path=r1_input, evidence_path=authored / "review-draft-evidence.json", binding_root=tmp_path)
    decision = json.loads((Path(descriptor["decisions_root"]) / "page-001.json").read_text(encoding="utf-8"))
    assert decision["markdown"].endswith("Alternate second paragraph.")
    assert {(binding["view"], binding["raw_index"]) for binding in decision["reviewed_prose_bindings_v1"]} >= {key}


@pytest.mark.parametrize("mutation", ["packet", "queue", "decision_and_sidecar", "evidence_seal"])
def test_real_corrected_master_reopens_sealed_authorities(tmp_path, monkeypatch, mutation):
    from kb_creator.pipeline.reader_occurrence_projection import (
        ReaderOccurrenceError, _correction_packet_blocks,
    )

    renderer = shutil.which("pdftoppm"); assert renderer is not None
    monkeypatch.setenv("KB_CREATOR_PDFTOPPM", renderer)
    built = _build_r0(tmp_path, monkeypatch, whole_block_correction=True)
    master = built["master"]
    material_path = master / "REVIEW_DRAFT_MATERIALIZATION.v1.json"
    material = json.loads(material_path.read_text(encoding="utf-8"))
    evidence_path = Path(material["authority"]["final_evidence"]["path"])
    evidence = json.loads(evidence_path.read_text(encoding="utf-8"))
    audit = json.loads((evidence_path.parent / evidence["authored"]["stage05_audit"]["path"]).read_text(encoding="utf-8"))
    decision_path = master / "evidence/review/page-001.json"
    queue_path = Path(material["authority"]["review_queue"]["path"])
    if mutation == "packet":
        queue = json.loads(queue_path.read_text(encoding="utf-8"))
        packet = queue_path.parent.parent / "outputs/04-visual-merge-bundle" / queue["items"][0]["merge_packet"]["path"]
        packet.write_bytes(packet.read_bytes() + b" ")
    elif mutation == "queue":
        queue_path.write_bytes(queue_path.read_bytes() + b" ")
    elif mutation == "decision_and_sidecar":
        # Updating an unsigned materialization sidecar cannot substitute an
        # authored decision sealed by the final evidence's decision set.
        decision_path.write_bytes(decision_path.read_bytes() + b" ")
        material["pages"][0]["decision_sha256"] = file_identity(decision_path)["sha256"]
        _write(material_path, material)
    else:
        evidence["evidence_sha256"] = "0" * 64
    with pytest.raises(ReaderOccurrenceError, match="packet authority is invalid"):
        _correction_packet_blocks(master, evidence_path, evidence, audit, 1, decision_path)


def test_real_corrected_label_partition_reaches_verified_queue(tmp_path, monkeypatch):
    built = _build_r0(tmp_path, monkeypatch, whole_block_correction=True, label_partition=True)
    queue = Path(choices.prepare_v2(built["master"], built["mechanical"], tmp_path / "labels-queue", binding_root=tmp_path)["queue"])
    assert choices.verify_queue_v2(queue)["choices"] == 2
    rows = json.loads(queue.read_text(encoding="utf-8"))["choices"]
    label = next(row for row in rows if row["reader_projection"]["reader_text"].startswith("SEA MONSTER"))
    assert label["reader_projection"]["reader_text"] == "SEA MONSTER\n\nSUMMONING\n\nCOVER-UP\n\nMARTIN’S BEACH"
    selected = next(a for a in label["alternatives"] if a["alternative_id"] == label["provisional_alternative_id"])
    assert selected["raw_text"] == "SE A MONSTER SUMMONING COVER-UP MART IN ’S BEACH"
    assert selected["reader_text"] == label["reader_projection"]["reader_text"]
    assert all(a["reader_text"] == a["raw_text"] for a in label["alternatives"] if a is not selected)


def test_real_wrapped_initial_and_interior_correction_reaches_verified_queue(tmp_path, monkeypatch):
    renderer = shutil.which("pdftoppm"); assert renderer is not None
    monkeypatch.setenv("KB_CREATOR_PDFTOPPM", renderer)
    built = _build_r0(tmp_path, monkeypatch, whole_block_correction=True, wrapped_source=True)
    queue = Path(choices.prepare_v2(built["master"], built["mechanical"], tmp_path / "wrapped-queue", binding_root=tmp_path)["queue"])
    assert choices.verify_queue_v2(queue)["choices"] == 2
    rows = json.loads(queue.read_text(encoding="utf-8"))["choices"]
    first = next(row for row in rows if row["reader_projection"]["reader_text"] == "Good first paragraph.")
    selected = next(a for a in first["alternatives"] if a["alternative_id"] == first["provisional_alternative_id"])
    assert selected["raw_text"] == "ood first para  \ngraph."
    assert selected["reader_text"] == "Good first paragraph."
    assert first["raw_reader_replay"]["base_policy"] == "reviewed_block_correction_v1"


def test_real_multichoice_queue_keeps_two_disjoint_raster_slices(tmp_path, monkeypatch):
    """Two natural coverage claims remain diagnostic slices of one raster owner."""
    built, queue_path, first, first_alternate = _prepare_composite_queue(
        tmp_path, monkeypatch, multichoice=True)
    queue = json.loads(queue_path.read_text(encoding="utf-8"))
    assert len(queue["choices"]) == 2
    choices_by_start = sorted(queue["choices"], key=lambda row:
                              row["raw_reader_replay"]["raw_source_slice"]["raw_character_start"])
    assert [row["raw_reader_replay"]["raw_source_slice"]["raw_character_start"]
            for row in choices_by_start] == [len(PREFIX), len(PREFIX) + len(BASELINE) + len(MIDDLE)]
    assert all(row["raw_reader_replay"]["anchor_source_locator"] == {
        "view": "raster_pipeline_ocr", "raw_index": built["raws"]["selected_raster_container"], "field": "text"}
        for row in choices_by_start)


def test_real_multichoice_r1_route_preserves_one_full_punctuated_container(tmp_path, monkeypatch):
    """Two ledger choices replay as one complete raster container."""
    built, queue_path, _first, _first_alternate = _prepare_composite_queue(
        tmp_path, monkeypatch, multichoice=True)
    queue = json.loads(queue_path.read_text(encoding="utf-8"))
    ordered = sorted(queue["choices"], key=lambda row:
                     row["raw_reader_replay"]["raw_source_slice"]["raw_character_start"])
    alternatives = [next(row for row in choice["alternatives"]
                         if row["selectable"] and row["raw_text"] == expected)
                    for choice, expected in zip(ordered, (ALTERNATE, SECOND_ALTERNATE))]
    selected = [(choice["issue_id"], alternative["alternative_id"])
                for choice, alternative in zip(ordered, alternatives)]
    ledger = Path(choices.record_decisions_v2(
        queue_path, _submission_choices(queue_path, selected, tmp_path / "multichoice-submission.json"),
        tmp_path / "ledger-v2")["ledger"])
    choices.verify_ledger_v2(ledger)
    r1 = prepare_source_choice_successor(
        input_path=built["r0_input"], binding_root=tmp_path, ledger_path=ledger,
        draft_pages=built["draft_pages"], spec_paths=built["spec_paths"],
        output_dir=tmp_path / "r1-input")
    r1_input = Path(r1["input"]["path"])
    assert r1["resolved_choice_count"] == 2
    retained_issues = json.loads(r1_input.read_text(encoding="utf-8"))["source_issues"]["issues"]
    assert len(retained_issues) == 1
    retained_issue = retained_issues[0]
    assert retained_issue["kind"] == "source_structure_role_pending"
    assert retained_issue["source_excerpt_en"] == MULTICHOICE_CONTAINER
    authored = tmp_path / "r1-authored"
    author.author_drafts(built["run"], Path(r1["draft_pages"]), authored,
                         [Path(path) for path in r1["spec_paths"]], mode="review_draft",
                         draft_input=r1_input, binding_root=tmp_path)
    evidence = authored / "review-draft-evidence.json"
    descriptor = verify_final_review_draft(run_root=built["run"], authored_root=authored,
                                            input_path=r1_input, evidence_path=evidence,
                                            binding_root=tmp_path)
    audit = json.loads((authored / "review-draft-stage05-audit.json").read_text(encoding="utf-8"))
    proof = next(row for row in audit["pages"][0]["ordered_proof_stream"]
                 if row["kind"] == "linguistic_source_choice_container_v1")
    expected = PREFIX + ALTERNATE + MIDDLE + SECOND_ALTERNATE + RETAINED + SUFFIX
    assert proof["r1_container"]["text"] == expected
    assert proof["markdown_span"] == proof["r1_container"]["normalized_page_span"]
    assert len(proof["diagnostic_witnesses"]) == 2
    assert [row["issue_id"] for row in proof["diagnostic_witnesses"]] == [row["issue_id"] for row in ordered]
    # Submission order is a separate public contract. Proof derivation must not
    # depend on the order of the already authenticated correction records.
    decision = json.loads((Path(descriptor["decisions_root"]) / "page-001.json").read_text(encoding="utf-8"))
    reversed_decision = deepcopy(decision)
    reversed_decision["linguistic_source_choice_corrections"].reverse()
    mappings = [({"kind": "selected", "unit": row["unit"], "markdown_span": row["markdown_span"]}
                 if row["kind"] == "linguistic_source_choice_container_v1" else row)
                for row in audit["pages"][0]["ordered_proof_stream"]]
    from kb_creator.scripts.audit_mineru_ai_merge_fidelity import _linguistic_source_choice_proofs
    assert _linguistic_source_choice_proofs(1, reversed_decision, mappings) == audit["pages"][0]["ordered_proof_stream"]
    materialized = tmp_path / "r1-materialized"
    materializer.materialize(Path(descriptor["bundle_root"]), Path(descriptor["raw_root"]),
                             Path(descriptor["decisions_root"]), materialized,
                             review_draft_authority=descriptor, review_draft_binding_root=tmp_path)
    master = tmp_path / "r1-master"
    build_review_master_en(materialized, evidence, master, binding_root=tmp_path)
    master_text = (master / "MASTER_EN.md").read_text(encoding="utf-8")
    predecessor_text = (built["master"] / "MASTER_EN.md").read_text(encoding="utf-8")
    assert predecessor_text.endswith(MULTICHOICE_CONTAINER + "\n")
    assert master_text == predecessor_text[:-(len(MULTICHOICE_CONTAINER) + 1)] + expected + "\n"
    assert PREFIX in master_text and MIDDLE in master_text and RETAINED in master_text and SUFFIX in master_text
    assert BASELINE not in master_text and SECOND_BASELINE not in master_text
    bindings = json.loads((master / "ISSUE_EN_BINDINGS.v2.json").read_text(encoding="utf-8"))["bindings"]
    assert len(bindings) == 1
    assert bindings[0]["issue_id"] == retained_issue["issue_id"]
    assert bindings[0]["reader_projection"]["reader_text"] == expected
    glossary = _write(tmp_path / "glossary/terms.json", {"terms": [{"source": "Keeper", "target": "Хранитель"}]})
    assert continuation.prepare_continuation(master, glossary, tmp_path / "language",
                                             review_binding_root=tmp_path)["phase"] == "documentary_draft"


def test_real_multichoice_public_submission_rejects_reversed_queue_order(tmp_path, monkeypatch):
    """The v2 public ledger deliberately keeps its queue order as sealed authority."""
    _built, queue_path, _first, _first_alternate = _prepare_composite_queue(
        tmp_path, monkeypatch, multichoice=True)
    queue = json.loads(queue_path.read_text(encoding="utf-8"))
    selected = []
    for choice, expected in zip(queue["choices"], (ALTERNATE, SECOND_ALTERNATE)):
        alternate = next(row for row in choice["alternatives"]
                         if row["selectable"] and row["raw_text"] == expected)
        selected.append((choice["issue_id"], alternate["alternative_id"]))
    with pytest.raises(choices.SourceChoiceError, match="out of order"):
        choices.record_decisions_v2(
            queue_path, _submission_choices(queue_path, list(reversed(selected)),
                                              tmp_path / "reversed-submission.json"),
            tmp_path / "reversed-ledger")


@pytest.mark.parametrize("replacement", ["ID6", "ID6 extended", "ID6\nextra line"])
def test_real_composite_r1_route_preserves_container_surroundings(tmp_path, monkeypatch, replacement):
    """Run through language readiness once the interval-aware consumer is complete."""
    monkeypatch.setattr(sys.modules[__name__], "ALTERNATE", replacement)
    built, queue_path, choice, alternate = _prepare_composite_queue(tmp_path, monkeypatch)

    ledger_root = tmp_path / "ledger-v2"
    result = choices.record_decisions_v2(
        queue_path, _submission(queue_path, choice["issue_id"], alternate["alternative_id"],
                                tmp_path / "submission.json"), ledger_root)
    ledger = Path(result["ledger"])
    choices.verify_ledger_v2(ledger)
    r1 = prepare_source_choice_successor(
        input_path=built["r0_input"], binding_root=tmp_path, ledger_path=ledger,
        draft_pages=built["draft_pages"], spec_paths=built["spec_paths"],
        output_dir=tmp_path / "r1-input")
    r1_input = Path(r1["input"]["path"])
    authored = tmp_path / "r1-authored"
    author.author_drafts(built["run"], Path(r1["draft_pages"]), authored,
                         [Path(path) for path in r1["spec_paths"]], mode="review_draft",
                         draft_input=r1_input, binding_root=tmp_path)
    evidence = authored / "review-draft-evidence.json"
    descriptor = verify_final_review_draft(run_root=built["run"], authored_root=authored,
                                            input_path=r1_input, evidence_path=evidence,
                                            binding_root=tmp_path)
    evidence_payload = json.loads(evidence.read_text(encoding="utf-8"))
    audit_path = authored / evidence_payload["authored"]["stage05_audit"]["path"]
    stream = json.loads(audit_path.read_text(encoding="utf-8"))["pages"][0]["ordered_proof_stream"]
    proof = next(row for row in stream if row["kind"] == "linguistic_source_choice_container_v1")
    assert proof["r1_container"]["text"] == PREFIX + replacement + SUFFIX
    assert len(proof["diagnostic_witnesses"]) == 1
    assert proof["markdown_span"] == proof["r1_container"]["normalized_page_span"]
    materialized = tmp_path / "r1-materialized"
    materializer.materialize(Path(descriptor["bundle_root"]), Path(descriptor["raw_root"]),
                             Path(descriptor["decisions_root"]), materialized,
                             review_draft_authority=descriptor, review_draft_binding_root=tmp_path)
    master = tmp_path / "r1-master"
    build_review_master_en(materialized, evidence, master, binding_root=tmp_path)
    text = (master / "MASTER_EN.md").read_text(encoding="utf-8")
    assert text.endswith(PREFIX + ALTERNATE + SUFFIX + "\n")
    assert PREFIX in text and SUFFIX in text and BASELINE not in text

    glossary = _write(tmp_path / "glossary/terms.json", {
        "terms": [{"source": "Keeper", "target": "Хранитель"}]})
    ready = continuation.prepare_continuation(master, glossary, tmp_path / "language",
                                              review_binding_root=tmp_path)
    assert ready["phase"] == "documentary_draft"
