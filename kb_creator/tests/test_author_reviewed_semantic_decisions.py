import json
from pathlib import Path

import pytest

from kb_creator.scripts.author_reviewed_semantic_decisions import (
    _append_review_notes,
    _apply_selected_before,
    _canonicalize_blank_separators,
    _canonicalize_line_groups,
    _load_spec_fragments,
    _materialize_reviewed_block_corrections,
    _materialize_reviewed_prose_bindings,
    _remove_review_notes,
    _source_fragments,
    _reject_overlapping_selected_asset_assertions,
    _unit_definitions,
    validate_spec,
)


def _asset_assertion(assertion_id, bbox, *, page=1, raw_index=7, source_path="images/map.png"):
    return {
        "assertion_id": assertion_id, "source_page": page, "relation": "within_selected_asset_region",
        "bbox": bbox,
        "asset": {"view_id": "original_pipeline_txt", "raw_index": raw_index,
                  "logical_name": "map.png", "source_path": source_path},
    }


def test_preflight_rejects_only_overlapping_regions_for_one_selected_asset():
    with pytest.raises(ValueError, match="overlapping selected asset regions second and first"):
        _reject_overlapping_selected_asset_assertions([
            _asset_assertion("first", [10, 10, 30, 30]),
            _asset_assertion("second", [20, 20, 40, 40]),
        ])


def test_preflight_allows_touching_and_isolates_distinct_selected_assets_and_pages():
    _reject_overlapping_selected_asset_assertions([
        _asset_assertion("left", [10, 10, 20, 30]),
        _asset_assertion("right", [20, 10, 30, 30]),
        _asset_assertion("other-asset", [15, 15, 25, 25], raw_index=8),
        _asset_assertion("other-page", [15, 15, 25, 25], page=2),
        _asset_assertion("other-file", [15, 15, 25, 25], source_path="images/other.png"),
    ])


def _write(path, value):
    path.write_text(json.dumps(value), encoding="utf-8")
    return path


def test_disjoint_spec_fragments_merge_in_page_order(tmp_path):
    second = _write(tmp_path / "second.json", {
        "pages": [{"source_page": 2}],
        "visual_text_assertions": [{"assertion_id": "b"}],
    })
    first = _write(tmp_path / "first.json", {
        "pages": [{"source_page": 1}],
        "visual_text_assertions": [{"assertion_id": "a"}],
    })
    merged = _load_spec_fragments([second, first])
    assert [row["source_page"] for row in merged["pages"]] == [1, 2]
    assert [row["assertion_id"] for row in merged["visual_text_assertions"]] == ["b", "a"]


@pytest.mark.parametrize(
    "left,right,error",
    [
        ({"pages": [{"source_page": 1}]}, {"pages": [{"source_page": 1}]}, "source_page"),
        (
            {"visual_text_assertions": [{"assertion_id": "same"}]},
            {"visual_text_assertions": [{"assertion_id": "same"}]},
            "assertion_id",
        ),
    ],
)
def test_spec_fragment_merge_rejects_duplicate_authority(tmp_path, left, right, error):
    paths = [_write(tmp_path / "left.json", left), _write(tmp_path / "right.json", right)]
    with pytest.raises(ValueError, match=error):
        _load_spec_fragments(paths)


def test_review_notes_append_preserves_history_and_requires_visual_review():
    decision = {"review": {"visual_reviewed": True, "notes": "original evidence"}}
    _append_review_notes(decision, ["title override: Numbe; reason: adjacent cover fragments were visually reconstructed"], 1)
    assert decision["review"]["notes"].splitlines() == [
        "original evidence",
        "title override: Numbe; reason: adjacent cover fragments were visually reconstructed",
    ]
    with pytest.raises(ValueError, match="visually reviewed"):
        _append_review_notes({"review": {"visual_reviewed": False, "notes": ""}}, ["evidence"], 1)


def test_review_notes_remove_is_exact_and_preserves_other_history():
    decision = {"review": {"visual_reviewed": True, "notes": "keep\nsuperseded\nkeep two"}}
    _remove_review_notes(decision, ["superseded"], 10)
    assert decision["review"]["notes"] == "keep\nkeep two"
    with pytest.raises(ValueError, match="exactly once"):
        _remove_review_notes(decision, ["missing"], 10)


def _line_group_inputs(markdown):
    decision = {
        "overlay_preference": "original_pipeline_txt",
        "markdown": markdown,
        "selected_blocks": [
            {"view": "original_pipeline_txt", "raw_index": 1, "purpose": "structure"},
            {"view": "original_pipeline_txt", "raw_index": 2, "purpose": "structure"},
            {"view": "original_pipeline_txt", "raw_index": 3, "purpose": "structure"},
        ],
        "review": {"visual_reviewed": True, "notes": "reviewed"},
    }
    packet = {"views": {"original_pipeline_txt": {"blocks": [
        {"raw_index": 1, "text": "Luck: 85"},
        {"raw_index": 2, "text": "STR: 60 CON: 35"},
        {"raw_index": 3, "text": "HP: 8"},
    ]}}}
    definition = {
        "id": "fields", "kind": "line_group", "representation": "hard_break_lines",
        "raw_indices": [2, 1, 3], "start": "STR: 60", "end": "HP: 8",
    }
    return decision, packet, definition


def test_line_group_authoring_compacts_and_reorders_from_reviewed_raw_mapping():
    decision, packet, definition = _line_group_inputs("Luck: 85\n\nSTR: 60 CON: 35\n\nHP: 8")
    rendered = _canonicalize_line_groups(decision["markdown"], decision, packet, [definition], 23)
    assert rendered == "STR: 60 CON: 35  \nLuck: 85  \nHP: 8"
    assert _canonicalize_line_groups(rendered, decision, packet, [definition], 23) == rendered


def test_line_group_authoring_rejects_unrelated_content_and_ambiguous_members():
    decision, packet, definition = _line_group_inputs("Luck: 85\n\nSTR: 60 CON: 35\nNOTE\nHP: 8")
    with pytest.raises(ValueError, match="line-group"):
        _canonicalize_line_groups(decision["markdown"], decision, packet, [definition], 23)
    decision["markdown"] = "Luck: 85\nLuck: 85\nSTR: 60 CON: 35\nHP: 8"
    with pytest.raises(ValueError, match="line-group"):
        _canonicalize_line_groups(decision["markdown"], decision, packet, [definition], 23)


def test_line_group_authoring_uses_source_candidates_before_final_semantic_spans():
    text = "Refrain old\nRefrain"
    decision = {
        "overlay_preference": "original_pipeline_txt",
        "markdown": "Refrain new\nRefrain",
        "selected_blocks": [{"view": "original_pipeline_txt", "raw_index": 4, "purpose": "text"}],
        "reviewed_block_corrections": [{
            "view": "original_pipeline_txt", "raw_index": 4,
            "before": "Refrain old", "after": "Refrain new", "reason": "reviewed source correction",
            "original_text_sha256": __import__("hashlib").sha256(text.encode()).hexdigest().upper(),
        }],
    }
    packet = {"views": {"original_pipeline_txt": {"blocks": [{"raw_index": 4, "text": text}]}}}
    definition = {
        "id": "refrain", "kind": "line_group", "representation": "hard_break_lines",
        "raw_indices": [4], "start": "Refrain new", "end": "Refrain",
    }
    assert _canonicalize_line_groups(decision["markdown"], decision, packet, [definition], 45) == "Refrain new  \nRefrain"


def test_selected_before_is_shared_exact_and_fail_closed():
    decision, _, _ = _line_group_inputs("")
    _apply_selected_before(decision, [{"raw_index": 2, "before_raw_index": 1}], 23)
    assert [row["raw_index"] for row in decision["selected_blocks"]] == [2, 1, 3]
    with pytest.raises(ValueError, match="exact keys"):
        _apply_selected_before(decision, [{"raw_index": 1}], 23)


def test_selected_before_qualifies_reused_indices_by_extraction_view():
    selected = [{"view": "txt", "raw_index": 7}, {"view": "txt", "raw_index": 9},
                {"view": "raster", "raw_index": 7}]
    decision = {"selected_blocks": selected, "markdown": "unchanged reader"}
    with pytest.raises(ValueError, match="not unique"):
        _apply_selected_before(decision, [{"raw_index": 7, "before_raw_index": 9}], 152)
    move = {"view": "raster", "raw_index": 7, "before_view": "txt", "before_raw_index": 9}
    _apply_selected_before(decision, [move], 152)
    assert [(x["view"], x["raw_index"]) for x in selected] == [("txt", 7), ("raster", 7), ("txt", 9)]
    assert decision["markdown"] == "unchanged reader"
    _apply_selected_before(decision, [move], 152)
    assert [(x["view"], x["raw_index"]) for x in selected] == [("txt", 7), ("raster", 7), ("txt", 9)]
    for bad in ({**move, "view": "absent"}, {**move, "before_view": "absent"}):
        with pytest.raises(ValueError, match="not unique"):
            _apply_selected_before(decision, [bad], 152)
    with pytest.raises(ValueError, match="exact keys"):
        _apply_selected_before(decision, [{"view": "raster", "raw_index": 7, "before_raw_index": 9}], 152)


def test_author_materializes_block_correction_with_immutable_source_hash():
    text = "Angelo's .38 (27/11)\nDamage: 1D10"
    decision = {"selected_blocks": [{"view": "original_pipeline_txt", "raw_index": 7, "purpose": "text"}]}
    packet = {"views": {"original_pipeline_txt": {"blocks": [{"raw_index": 7, "text": text}]}}}
    selector = [{
        "view": "original_pipeline_txt", "raw_index": 7,
        "before": "(27/11)", "after": "Revolver (27/11)", "reason": "source label",
    }]
    _materialize_reviewed_block_corrections(decision, packet, selector, 46)
    assert decision["reviewed_block_corrections"] == [{
        **selector[0], "original_text_sha256": __import__("hashlib").sha256(text.encode()).hexdigest().upper(),
    }]


def test_author_block_correction_rejects_unselected_or_nonexistent_source_block():
    decision = {"selected_blocks": [{"view": "original_pipeline_txt", "raw_index": 7, "purpose": "text"}]}
    packet = {"views": {"original_pipeline_txt": {"blocks": [{"raw_index": 7, "text": "Gear: seems fit"}]}}}
    selector = [{"view": "original_pipeline_txt", "raw_index": 8, "before": "seems", "after": "sees", "reason": "source"}]
    with pytest.raises(ValueError, match="selected text block"):
        _materialize_reviewed_block_corrections(decision, packet, selector, 46)
    decision["selected_blocks"].append({"view": "original_pipeline_txt", "raw_index": 8, "purpose": "asset"})
    packet["views"]["original_pipeline_txt"]["blocks"].append({"raw_index": 8, "text": "Gear: seems fit"})
    with pytest.raises(ValueError, match="selected text block"):
        _materialize_reviewed_block_corrections(decision, packet, selector, 46)


def test_author_derives_prose_selector_hashes_from_packet_and_final_markdown():
    source = "The girl's coat is blue."
    reader = "The girl’s coat is blue."
    decision = {"selected_blocks": [{"view": "original_pipeline_ocr", "raw_index": 268, "purpose": "text"}]}
    packet = {"views": {"original_pipeline_ocr": {"blocks": [{"raw_index": 268, "text": source}]}}}
    _materialize_reviewed_prose_bindings(decision, packet, [{
        "view": "original_pipeline_ocr", "raw_index": 268,
        "markdown_span": {"start_line": 3, "end_line": 3},
    }], "# Heading\n\n" + reader, 16)
    binding = decision["reviewed_prose_bindings_v1"][0]
    assert binding["original_text_sha256"] == __import__("hashlib").sha256(source.encode()).hexdigest().upper()
    assert binding["markdown_span"]["sha256"] == __import__("hashlib").sha256(reader.encode()).hexdigest().upper()
    with pytest.raises(ValueError, match="invalid or unselected"):
        _materialize_reviewed_prose_bindings(decision, packet, [{"view": "original_pipeline_ocr", "raw_index": 999, "markdown_span": {"start_line": 3, "end_line": 3}}], "# Heading\n\n" + reader, 16)


def test_validate_spec_honors_explicit_unit_view_for_raw_index(monkeypatch, tmp_path: Path):
    from kb_creator.scripts import author_reviewed_semantic_decisions as author
    run, baseline = tmp_path / "run", tmp_path / "baseline"
    (run / "outputs/04-visual-merge-bundle/merge_packets/pages").mkdir(parents=True)
    (baseline / "pages").mkdir(parents=True)
    visual_path = "outputs/04-visual-merge-bundle/visual/original_pipeline_txt/pages/page-001.png"
    monkeypatch.setattr(author, "_visual_inventory", lambda _: {visual_path: {"bytes": 1, "sha256": "A" * 64}})
    _write(baseline / "pages/page-001.json", {
        "source_page": 1, "overlay_preference": "original_pipeline_txt",
        "selected_blocks": [{"view": "original_pipeline_ocr", "raw_index": 100, "purpose": "text"}],
        "markdown": "> OCR canonical", "assets": [],
        "review": {"visual_reviewed": True, "notes": "reviewed"},
    })
    _write(run / "outputs/04-visual-merge-bundle/merge_packets/pages/page-001.json", {
        "source_page": 1, "views": {
            "original_pipeline_txt": {"blocks": [{"raw_index": 0, "text": "wrong overlay text", "assets": []}]},
            "original_pipeline_ocr": {"blocks": [{"raw_index": 100, "text": "OCR canonical", "assets": []}]},
        },
    })
    spec = _write(tmp_path / "spec.json", {"pages": [{"source_page": 1, "units": [{
        "id": "ocr", "kind": "handout", "representation": "blockquote",
        "view": "original_pipeline_ocr", "raw_indices": [100],
        "start": "> OCR canonical", "end": "> OCR canonical",
    }]}]})
    assert validate_spec(run, baseline, [spec])["page_count"] == 1


def test_validate_spec_applies_asset_placements_before_semantic_validation(monkeypatch, tmp_path: Path):
    from kb_creator.pipeline.semantic_structure import SemanticStructureError
    from kb_creator.scripts import author_reviewed_semantic_decisions as author
    run, baseline = tmp_path / "run", tmp_path / "baseline"
    (run / "outputs/04-visual-merge-bundle/merge_packets/pages").mkdir(parents=True)
    (run / "review").mkdir()
    (baseline / "pages").mkdir(parents=True)
    visual_path = "outputs/04-visual-merge-bundle/visual/original_pipeline_txt/pages/page-001.png"
    monkeypatch.setattr(author, "_visual_inventory", lambda _: {visual_path: {"bytes": 1, "sha256": "A" * 64}})
    _write(baseline / "pages/page-001.json", {
        "source_page": 1, "overlay_preference": "original_pipeline_txt",
        "selected_blocks": [{"view": "original_pipeline_txt", "raw_index": 1, "purpose": "asset"}],
        "markdown": "> Map legend", "assets": [{
            "view": "original_pipeline_txt", "source_path": "images/map.png",
            "logical_name": "map.png", "placement": "reference_only",
        }], "review": {"visual_reviewed": True, "notes": "reviewed"},
    })
    _write(run / "outputs/04-visual-merge-bundle/merge_packets/pages/page-001.json", {
        "source_page": 1, "views": {"original_pipeline_txt": {"blocks": [{
            "raw_index": 1, "type": "image", "text": "", "assets": ["images/map.png"],
        }]}},
    })
    _write(run / "run.json", {"schema": "kb_creator.run_spec.v4", "portable_identity_sha256": "A" * 64,
        "source": {"path_hint": "source.pdf", "bytes": 1, "sha256": "B" * 64}})
    _write(run / "review/review_queue.json", {"queue_sha256": "Q" * 64})
    spec = _write(tmp_path / "spec.json", {"pages": [{"source_page": 1, "asset_placements": {"map.png": "map"}, "units": [{
        "id": "map", "kind": "handout", "representation": "blockquote", "raw_indices": [1],
        "start": "> Map legend", "end": "> Map legend",
    }]}]})

    with pytest.raises(SemanticStructureError, match="inline semantic asset lacks span placeholder"):
        validate_spec(run, baseline, [spec])

    baseline_page = json.loads((baseline / "pages/page-001.json").read_text(encoding="utf-8"))
    baseline_page["markdown"] = "> Map legend {{asset:map.png}}"
    _write(baseline / "pages/page-001.json", baseline_page)
    spec_page = json.loads(spec.read_text(encoding="utf-8"))
    spec_page["pages"][0]["units"][0].update({
        "start": "> Map legend {{asset:map.png}}", "end": "> Map legend {{asset:map.png}}",
    })
    _write(spec, spec_page)
    candidate = tmp_path / "candidate"
    assert validate_spec(run, baseline, [spec], candidate_output=candidate)["page_count"] == 1
    assert json.loads((candidate / "pages/page-001.json").read_text(encoding="utf-8"))["assets"][0]["placement"] == "map"


def test_asset_placement_selectors_reject_unknown_and_malformed_values():
    from kb_creator.scripts.author_reviewed_semantic_decisions import _apply_asset_placements
    decision = {"assets": [{"logical_name": "map.png", "placement": "reference_only"}]}
    with pytest.raises(ValueError, match="selector is invalid"):
        _apply_asset_placements(decision, {"missing.png": "map"}, 1)
    with pytest.raises(ValueError, match="value is invalid"):
        _apply_asset_placements(decision, {"map.png": ""}, 1)


def test_validate_spec_can_materialize_only_validated_candidate_preserving_review_state(monkeypatch, tmp_path: Path):
    from kb_creator.scripts import author_reviewed_semantic_decisions as author
    run, baseline = tmp_path / "run", tmp_path / "baseline"
    (run / "outputs/04-visual-merge-bundle/merge_packets/pages").mkdir(parents=True)
    (run / "review").mkdir()
    (baseline / "pages").mkdir(parents=True)
    visual_path = "outputs/04-visual-merge-bundle/visual/original_pipeline_txt/pages/page-001.png"
    monkeypatch.setattr(author, "_visual_inventory", lambda _: {visual_path: {"bytes": 1, "sha256": "A" * 64}})
    review = {"visual_reviewed": True, "notes": "reviewed evidence"}
    unresolved = [{"kind": "pending", "detail": "coverage remains open"}]
    _write(run / "run.json", {"schema": "kb_creator.run_spec.v4", "portable_identity_sha256": "A" * 64, "source": {"path_hint": "source.pdf", "bytes": 1, "sha256": "B" * 64}})
    _write(run / "review/review_queue.json", {"queue_sha256": "Q" * 64})
    _write(baseline / "pages/page-001.json", {
        "source_page": 1, "overlay_preference": "original_pipeline_txt",
        "selected_blocks": [{"view": "original_pipeline_txt", "raw_index": 0, "purpose": "text"}],
        "markdown": "> Corrected reader text", "assets": [], "unresolved": unresolved, "review": review,
    })
    _write(run / "outputs/04-visual-merge-bundle/merge_packets/pages/page-001.json", {"source_page": 1, "views": {
        "original_pipeline_txt": {"blocks": [{"raw_index": 0, "text": "Corrected reader text", "assets": []}]},
    }})
    spec = _write(tmp_path / "spec.json", {"pages": [{"source_page": 1, "units": [{
        "id": "body", "kind": "handout", "representation": "blockquote", "raw_indices": [0],
        "start": "> Corrected reader text", "end": "> Corrected reader text",
    }]}]})
    candidate = tmp_path / "candidate"
    result = validate_spec(run, baseline, [spec], candidate_output=candidate)
    manifest = json.loads((candidate / "candidate_manifest.json").read_text(encoding="utf-8"))
    page = json.loads((candidate / "pages/page-001.json").read_text(encoding="utf-8"))
    assert result["candidate_output"]["path"] == str(candidate)
    assert manifest["state"] == "validated_candidate_only" and manifest["acceptance"] == "pending"
    assert manifest["inputs"]["source"] == {"sha256": "B" * 64, "bytes": 1, "path_hint": "source.pdf"}
    assert manifest["inputs"]["run"]["path"].endswith("run.json")
    assert manifest["inputs"]["baseline"]["path"] == str(baseline)
    assert page["review"] == review and page["unresolved"] == unresolved
    assert not (candidate / "decision_set.json").exists() and not (candidate / "reviewed_allowlist.v3.json").exists()
    with pytest.raises(ValueError, match="already exists"):
        validate_spec(run, baseline, [spec], candidate_output=candidate)


def test_candidate_publish_failure_keeps_staging_manifest_incomplete(monkeypatch, tmp_path: Path):
    from kb_creator.scripts import author_reviewed_semantic_decisions as author
    run, baseline = tmp_path / "run", tmp_path / "baseline"
    (run / "outputs/04-visual-merge-bundle/merge_packets/pages").mkdir(parents=True)
    (run / "review").mkdir(); (baseline / "pages").mkdir(parents=True)
    visual_path = "outputs/04-visual-merge-bundle/visual/original_pipeline_txt/pages/page-001.png"
    monkeypatch.setattr(author, "_visual_inventory", lambda _: {visual_path: {"bytes": 1, "sha256": "A" * 64}})
    _write(run / "run.json", {"schema": "kb_creator.run_spec.v4", "portable_identity_sha256": "A" * 64, "source": {"path_hint": "source.pdf", "bytes": 1, "sha256": "B" * 64}})
    _write(run / "review/review_queue.json", {"queue_sha256": "Q" * 64})
    _write(baseline / "pages/page-001.json", {"source_page": 1, "overlay_preference": "original_pipeline_txt", "selected_blocks": [{"view": "original_pipeline_txt", "raw_index": 0, "purpose": "text"}], "markdown": "> reader", "assets": [], "review": {"visual_reviewed": True, "notes": "reviewed"}})
    _write(run / "outputs/04-visual-merge-bundle/merge_packets/pages/page-001.json", {"source_page": 1, "views": {"original_pipeline_txt": {"blocks": [{"raw_index": 0, "text": "reader", "assets": []}]}}})
    spec = _write(tmp_path / "spec.json", {"pages": [{"source_page": 1, "units": [{"id": "body", "kind": "handout", "representation": "blockquote", "raw_indices": [0], "start": "> reader", "end": "> reader"}]}]})
    candidate = tmp_path / "candidate"
    monkeypatch.setattr(Path, "replace", lambda self, target: (_ for _ in ()).throw(OSError("simulated rename failure")))
    with pytest.raises(OSError, match="simulated rename failure"):
        validate_spec(run, baseline, [spec], candidate_output=candidate)
    staging = tmp_path / ".candidate.candidate-staging/candidate_manifest.json"
    assert not candidate.exists() and json.loads(staging.read_text(encoding="utf-8"))["state"] == "incomplete_candidate_output"


@pytest.mark.parametrize("run", [
    {"schema": "kb_creator.run_spec.v4", "source": {"path_hint": "source.pdf", "bytes": 1}},
    {"schema": "kb_creator.run_spec.v4", "source": {"path_hint": "source.pdf", "bytes": 1, "sha256": "B" * 64}, "source_sha256": "B" * 64},
    {"schema": "unsupported", "source": {"path_hint": "source.pdf", "bytes": 1, "sha256": "B" * 64}},
])
def test_candidate_source_identity_rejects_missing_or_contradictory_envelopes(run):
    from kb_creator.scripts.author_reviewed_semantic_decisions import _candidate_source_identity
    with pytest.raises(ValueError, match="candidate output"):
        _candidate_source_identity(run)


def test_validate_spec_invalid_proof_creates_no_candidate_output(monkeypatch, tmp_path: Path):
    from kb_creator.scripts import author_reviewed_semantic_decisions as author
    run, baseline = tmp_path / "run", tmp_path / "baseline"
    (run / "outputs/04-visual-merge-bundle/merge_packets/pages").mkdir(parents=True)
    (baseline / "pages").mkdir(parents=True)
    visual_path = "outputs/04-visual-merge-bundle/visual/original_pipeline_txt/pages/page-001.png"
    monkeypatch.setattr(author, "_visual_inventory", lambda _: {visual_path: {"bytes": 1, "sha256": "A" * 64}})
    _write(baseline / "pages/page-001.json", {"source_page": 1, "overlay_preference": "original_pipeline_txt", "selected_blocks": [{"view": "original_pipeline_txt", "raw_index": 0, "purpose": "text"}], "markdown": "> reader", "assets": [], "review": {"visual_reviewed": True, "notes": "reviewed"}})
    _write(run / "outputs/04-visual-merge-bundle/merge_packets/pages/page-001.json", {"source_page": 1, "views": {"original_pipeline_txt": {"blocks": [{"raw_index": 0, "text": "reader", "assets": []}]}}})
    spec = _write(tmp_path / "bad.json", {"pages": [{"source_page": 1, "units": [{"id": "body", "kind": "handout", "representation": "blockquote", "raw_indices": [0], "start": "> missing", "end": "> missing"}]}]})
    candidate = tmp_path / "candidate"
    with pytest.raises(ValueError, match="start selector"):
        validate_spec(run, baseline, [spec], candidate_output=candidate)
    assert not candidate.exists() and not (tmp_path / ".candidate.candidate-staging").exists()


def test_validate_only_cli_forwards_optional_candidate_output_and_rejects_other_modes(monkeypatch, tmp_path: Path):
    from kb_creator.scripts import author_reviewed_semantic_decisions as author
    candidate = tmp_path / "candidate"
    captured = {}
    monkeypatch.setattr(author, "validate_spec", lambda run, baseline, specs, *, candidate_output=None: captured.update({"run": run, "baseline": baseline, "specs": specs, "candidate": candidate_output}) or {"page_count": 1})
    monkeypatch.setattr("sys.argv", ["author", "--run", "run", "--baseline", "baseline", "--spec", "one", "--validate-only", "--candidate-output", str(candidate)])
    assert author.main() == 0 and captured["candidate"] == candidate
    monkeypatch.setattr("sys.argv", ["author", "--run", "run", "--baseline", "baseline", "--spec", "one", "--candidate-output", str(candidate), "--output", "output"])
    with pytest.raises(SystemExit):
        author.main()


def test_blank_separator_authoring_replaces_only_exact_reviewed_runs():
    markdown = "Stanwick\n\n\n\n\n\nElsie\n\n\n\n\n\nRegular\n\n\n\nHeavy"
    declarations = [
        {"before_line": "Stanwick", "after_line": "Elsie", "expected_blank_lines": 5},
        {"before_line": "Elsie", "after_line": "Regular", "expected_blank_lines": 5},
        {"before_line": "Regular", "after_line": "Heavy", "expected_blank_lines": 3},
    ]
    assert _canonicalize_blank_separators(markdown, declarations, 18) == "Stanwick\n\nElsie\n\nRegular\n\nHeavy"


@pytest.mark.parametrize(
    "declarations,error",
    [
        ([{"before_line": "Stanwick", "after_line": "Elsie", "expected_blank_lines": 4}], "blank_separator_selector_mismatch"),
        ([{"before_line": "Stanwick", "after_line": "Elsie", "expected_blank_lines": 5}, {"before_line": "Stanwick", "after_line": "Elsie", "expected_blank_lines": 5}], "blank_separator_declaration_invalid"),
        ([{"before_line": "Stanwick", "after_line": "Elsie", "expected_blank_lines": 5, "extra": 1}], "blank_separator_declaration_invalid"),
    ],
)
def test_blank_separator_authoring_is_exact_and_fail_closed(declarations, error):
    markdown = "Stanwick\n\n\n\n\n\nElsie"
    with pytest.raises(ValueError, match=error):
        _canonicalize_blank_separators(markdown, declarations, 18)


def test_v2_authoring_auto_partitions_unshared_sources_and_rejects_shared_implicit_split():
    packet = {"views": {"original_pipeline_txt": {"blocks": [{"raw_index": 7, "text": "Name"}]}}}
    definition = {"raw_indices": [7]}
    rows = _source_fragments(packet, definition, "original_pipeline_txt", 1, set())
    assert rows[0]["start"] == 0 and rows[0]["end"] == 4
    with pytest.raises(ValueError, match="shared"):
        _source_fragments(packet, definition, "original_pipeline_txt", 1, {("original_pipeline_txt", 7)})


def test_v2_authoring_inherited_units_are_closed_and_mutually_exclusive():
    baseline = {"semantic_structure": {"units": [{"id": "text", "kind": "heading", "representation": "atx_heading", "source_blocks": [{"view": "original_pipeline_txt", "raw_index": 1}], "markdown_span": {"start_line": 1, "end_line": 1}, "container_parent": None, "semantic_parent": None, "continuation_of": None, "heading_level": 1, "item_count": None}]}}
    inherited = _unit_definitions({"inherit_units_from_baseline": True}, baseline, 1)
    assert inherited[0]["raw_indices"] == [1]
    assert inherited[0]["source_fragments"] == []
    with pytest.raises(ValueError, match="mutually exclusive"):
        _unit_definitions({"inherit_units_from_baseline": True, "units": []}, baseline, 1)


def test_v2_authoring_inherits_only_reviewed_fragment_selectors_for_rehashing():
    baseline = {"semantic_structure": {"units": [{"id": "split", "kind": "heading", "representation": "atx_heading", "source_blocks": [{"view": "original_pipeline_txt", "raw_index": 7}], "source_fragments": [{"view": "original_pipeline_txt", "raw_index": 7, "source_sha256": "OLD", "normalized_sha256": "OLD", "start": 0, "end": 4, "fragment_sha256": "OLD"}], "markdown_span": {"start_line": 1, "end_line": 1}, "container_parent": None, "semantic_parent": None, "continuation_of": None, "heading_level": 1, "item_count": None}]}}
    inherited = _unit_definitions({"inherit_units_from_baseline": True}, baseline, 1)
    assert inherited[0]["source_fragments"] == [
        {"view": "original_pipeline_txt", "raw_index": 7, "start": 0, "end": 4}
    ]


def test_cold_drafts_require_exact_closed_reviewed_queue(tmp_path: Path):
    from kb_creator.scripts.author_reviewed_semantic_decisions import _load_cold_drafts
    queue = {"items": [{"source_page": 1, "contract_role": "body"}]}
    drafts = tmp_path / "drafts"; drafts.mkdir()
    page = {"schema": "kb_creator.mineru_ai_page_decision.v1", "source_page": 1, "semantic_role": "body", "overlay_preference": "original_pipeline_txt", "selected_blocks": [], "markdown": "", "assets": [], "unresolved": [], "review": {"visual_reviewed": True, "notes": "reviewed"}}
    (drafts / "page-001.json").write_text(json.dumps(page), encoding="utf-8")
    assert _load_cold_drafts(drafts, queue)[1]["semantic_role"] == "body"
    page["review"]["visual_reviewed"] = False
    (drafts / "page-001.json").write_text(json.dumps(page), encoding="utf-8")
    with pytest.raises(ValueError, match="closed visual review"):
        _load_cold_drafts(drafts, queue)


def test_cold_drafts_reject_extra_page(tmp_path: Path):
    from kb_creator.scripts.author_reviewed_semantic_decisions import _load_cold_drafts
    queue = {"items": [{"source_page": 1, "contract_role": "body"}]}
    drafts = tmp_path / "drafts"; drafts.mkdir()
    for page in (1, 2):
        (drafts / f"page-{page:03d}.json").write_text(json.dumps({"schema": "kb_creator.mineru_ai_page_decision.v1", "source_page": page, "semantic_role": "body", "overlay_preference": "original_pipeline_txt", "selected_blocks": [], "markdown": "", "assets": [], "unresolved": [], "review": {"visual_reviewed": True, "notes": "reviewed"}}), encoding="utf-8")
    with pytest.raises(ValueError, match="mismatches replay queue"):
        _load_cold_drafts(drafts, queue)



def test_cold_start_full_route_base_ocr(monkeypatch, tmp_path: Path):
    import importlib.util
    from types import SimpleNamespace
    from kb_creator.pipeline.identity import file_identity
    from kb_creator.pipeline.manifests import sealed
    from kb_creator.pipeline import reconstruction_replay as replay, reconstruction_replay_resume as resume
    from kb_creator.scripts import author_reviewed_semantic_decisions as author
    source = Path(__file__).with_name("test_reconstruction_replay_resume.py")
    module_spec = importlib.util.spec_from_file_location("cold_start_resume_fixture", source)
    fixture = importlib.util.module_from_spec(module_spec); assert module_spec.loader is not None; module_spec.loader.exec_module(fixture)
    authorities, _, _ = fixture._fixture(tmp_path)
    run = authorities.run_root
    original = run / "outputs/04-visual-merge-bundle/visual/original_pipeline_txt/pages/page-001.png"; original.parent.mkdir(parents=True); original.write_bytes(b"source")
    triptych = run / "outputs/04-visual-merge-bundle/visual/triptychs/page-001.png"
    manifest = sealed("kb_creator.mineru_visual_merge_bundle.v3", {"files": [{"path": "visual/triptychs/page-001.png", **file_identity(triptych)}, {"path": "visual/original_pipeline_txt/pages/page-001.png", **file_identity(original)}]}, digest_key="manifest_sha256")
    (run / "outputs/04-visual-merge-bundle/visual/visual_manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
    packet_path = run / "outputs/04-visual-merge-bundle/merge_packets/pages/page-001.json"; packet = json.loads(packet_path.read_text(encoding="utf-8")); packet["views"]["original_pipeline_ocr"]["blocks"][0]["text"] = "Unrelated corrupt text"; packet_path.write_text(json.dumps(packet), encoding="utf-8")
    queue = json.loads((run / "review/review_queue.json").read_text(encoding="utf-8"))
    monkeypatch.setattr(replay, "validate_replayed_prefix", lambda value: authorities)
    monkeypatch.setattr(resume, "validate_replay_review_queue", lambda value: SimpleNamespace(queue=queue))
    drafts = tmp_path / "drafts"; drafts.mkdir(); (drafts / "page-001.json").write_text(json.dumps({"schema": "kb_creator.mineru_ai_page_decision.v1", "source_page": 1, "semantic_role": "body", "overlay_preference": "original_pipeline_txt", "selected_blocks": [{"view": "original_pipeline_txt", "raw_index": 0, "purpose": "text"}], "markdown": "# Stable heading", "assets": [], "unresolved": [], "review": {"visual_reviewed": True, "notes": "reviewed"}}), encoding="utf-8")
    spec = tmp_path / "spec.json"; spec.write_text(json.dumps({"semantic_structure_profile": "visually_reviewed_semantic_containers_v1", "pages": [{"source_page": 1, "units": [{"id": "heading", "kind": "heading", "representation": "atx_heading", "raw_indices": [0], "start": "# Stable heading", "end": "# Stable heading", "heading_level": 1}]}], "ocr_equivalence_classes": [{"class_id": "ocr-1", "source_page": 1, "canonical": {"view_id": "original_pipeline_txt", "raw_index": 0}, "alternates": [{"view_id": "original_pipeline_ocr", "raw_index": 1}], "rationale": "visual proof resolves OCR corruption", "visual_verdict": "canonical_proof_complete_for_region_alternates_are_ocr_corruption", "equivalence_policy": "reviewed_visual_full_unit_v1", "supporting_assertion_ids": []}]}), encoding="utf-8")
    output = tmp_path / "output"; author.author_drafts(run, drafts, output, [spec])
    allowlist = json.loads((output / "reviewed_allowlist.v3.json").read_text(encoding="utf-8"))
    assert allowlist["ocr_equivalence_classes"][0]["class_id"] == "ocr-1"

    downgraded = tmp_path / "downgraded-drafts"; downgraded.mkdir()
    (downgraded / "page-001.json").write_text(json.dumps({"schema": "kb_creator.mineru_ai_page_decision.v1", "source_page": 1, "semantic_role": "body", "overlay_preference": "original_pipeline_txt", "selected_blocks": [{"view": "original_pipeline_txt", "raw_index": 0, "purpose": "text"}], "markdown": "> Stable heading", "assets": [], "unresolved": [], "review": {"visual_reviewed": True, "notes": "reviewed"}}), encoding="utf-8")
    downgraded_spec = tmp_path / "downgraded-spec.json"
    downgraded_spec.write_text(json.dumps({"semantic_structure_profile": "visually_reviewed_semantic_containers_v1", "pages": [{"source_page": 1, "units": [{"id": "heading", "kind": "handout", "representation": "blockquote", "raw_indices": [0], "start": "> Stable heading", "end": "> Stable heading"}]}], "ocr_equivalence_classes": [{"class_id": "ocr-1", "source_page": 1, "canonical": {"view_id": "original_pipeline_txt", "raw_index": 0}, "alternates": [{"view_id": "original_pipeline_ocr", "raw_index": 1}], "rationale": "visual proof resolves OCR corruption", "visual_verdict": "canonical_proof_complete_for_region_alternates_are_ocr_corruption", "equivalence_policy": "reviewed_visual_full_unit_v1", "supporting_assertion_ids": []}]}), encoding="utf-8")
    from kb_creator.scripts import materialize_mineru_ai_merge as materialize
    monkeypatch.setattr(materialize, "_is_title", lambda block: True)
    with pytest.raises(ValueError, match=r"page-001\.json: .*silently downgraded"):
        author.author_drafts(run, downgraded, tmp_path / "downgraded-output", [downgraded_spec])
    assert not (tmp_path / "downgraded-output").exists()
    diagnostic = tmp_path / "downgraded-output.failed-decision-validation.json"
    saved = json.loads(diagnostic.read_text(encoding="utf-8"))
    assert saved["state"] == "failed_unpublished" and saved["accepted"] is False
    assert saved["stage05_audit"]["passed"] is True
    assert saved["stage06_validation"]["checked_pages"] == [1]
    assert saved["stage06_validation"]["passed"] is False
    assert saved["candidate_pages"][0]["decision"]["markdown"] == "> Stable heading"
    original_diagnostic = diagnostic.read_bytes()
    with pytest.raises(ValueError, match="diagnostic already exists"):
        author.author_drafts(run, downgraded, tmp_path / "downgraded-output", [downgraded_spec])
    assert diagnostic.read_bytes() == original_diagnostic
    assert not (tmp_path / "downgraded-output").exists()


def test_stage06_collects_each_page_failure_without_leaking_failed_asset_names(monkeypatch, tmp_path):
    from kb_creator.scripts import author_reviewed_semantic_decisions as author
    from kb_creator.scripts import materialize_mineru_ai_merge as materializer
    visited = []
    def validate(decision, packet, comparison, raw, names, *args):
        page = decision["source_page"]
        visited.append(page)
        if page == 1:
            names.add("failed-page-name")
            raise ValueError("bad title")
        assert "failed-page-name" not in names
        if page == 2:
            names.add("valid-page-name")
        if page == 3:
            assert "valid-page-name" in names
            raise ValueError("bad asset")
    monkeypatch.setattr(materializer, "_validate_decision", validate)
    result = author._validate_authored_pages({n: {"source_page": n} for n in (3, 1, 2)},
        {n: {} for n in (1, 2, 3)}, {}, tmp_path, None, tmp_path, set(), set())
    assert visited == result["checked_pages"] == [1, 2, 3]
    assert result["passed_pages"] == [2]
    assert [row["source_page"] for row in result["failures"]] == [1, 3]
    assert result["passed"] is False




def test_cold_ocr_rejects_stale_assertion_and_wrong_members(monkeypatch):
    from kb_creator.scripts import author_reviewed_semantic_decisions as author
    unit = lambda run, page, view, raw: {"source_page": page, "view_id": view, "raw_index": raw, "block_type": "text", "bbox": [0, 0, 1, 1], "original_text_sha256": "A" * 64, "normalized_text_sha256": "B" * 64, "normalized_character_count": 1}
    monkeypatch.setattr(author, "_packet_unit", unit)
    visuals = {"outputs/04-visual-merge-bundle/visual/original_pipeline_txt/pages/page-001.png": {"bytes": 1, "sha256": "C" * 64}}
    reviewed = {"class_id": "x", "source_page": 1, "canonical": {"view_id": "original_pipeline_txt", "raw_index": 0}, "alternates": [{"view_id": "original_pipeline_ocr", "raw_index": 1}], "rationale": "review", "visual_verdict": "canonical_proof_complete_for_region_alternates_are_ocr_corruption", "equivalence_policy": "reviewed_visual_full_unit_v1", "supporting_assertion_ids": ["stale"]}
    with pytest.raises(ValueError, match="stale assertion"):
        author._cold_ocr_classes(Path("run"), [reviewed], visuals, {1: {"selected_blocks": [], "markdown": ""}}, {})
    wrong = {"class_id": "bad", "source_page": 1, "canonical": {"view_id": "original_pipeline_ocr", "raw_index": 0}, "alternates": [{"view_id": "raster_pipeline_ocr", "raw_index": 2}], "rationale": "wrong"}
    with pytest.raises(ValueError, match="members or visual"):
        author._cold_ocr_classes(Path("run"), [wrong], visuals, {}, {})


def test_cold_ocr_allows_any_required_cpu_view_only_for_new_reviewed_policy(monkeypatch, tmp_path: Path):
    from kb_creator.scripts import author_reviewed_semantic_decisions as author
    unit = lambda run, page, view, raw: {"source_page": page, "view_id": view, "raw_index": raw, "block_type": "text", "bbox": [0, 0, 1, 1], "original_text_sha256": "A" * 64, "normalized_text_sha256": "B" * 64, "normalized_character_count": 1}
    monkeypatch.setattr(author, "_packet_unit", unit)
    visuals = {"outputs/04-visual-merge-bundle/visual/original_pipeline_txt/pages/page-001.png": {"bytes": 1, "sha256": "C" * 64}}
    selector = {"class_id": "raster", "source_page": 1, "canonical": {"view_id": "raster_pipeline_ocr", "raw_index": 2}, "alternates": [{"view_id": "original_pipeline_txt", "raw_index": 0}], "rationale": "review", "visual_verdict": "canonical_proof_complete_for_region_alternates_are_ocr_corruption", "equivalence_policy": "reviewed_visual_full_unit_any_cpu_view_v1", "supporting_assertion_ids": []}
    packet = {"views": {view: {"blocks": [{"raw_index": raw, "text": "full canonical"}]} for view, raw in (("original_pipeline_txt", 0), ("original_pipeline_ocr", 1), ("raster_pipeline_ocr", 2))}}
    run = tmp_path / "run"; packet_path = run / "outputs/04-visual-merge-bundle/merge_packets/pages/page-001.json"; packet_path.parent.mkdir(parents=True); packet_path.write_text(json.dumps(packet), encoding="utf-8")
    decisions = {1: {"selected_blocks": [{"view": "raster_pipeline_ocr", "raw_index": 2}], "markdown": "full canonical"}}
    rows = author._cold_ocr_classes(run, [selector], visuals, decisions, {})
    assert rows[0]["canonical_unit"]["view_id"] == "raster_pipeline_ocr"
    selector["equivalence_policy"] = "reviewed_visual_full_unit_v1"
    with pytest.raises(ValueError, match="policy, verdict"):
        author._cold_ocr_classes(run, [selector], visuals, decisions, {})
