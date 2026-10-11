"""Focused closed-shape and MASTER_EN transport checks for structural issues."""
from __future__ import annotations

import pytest
import json
from types import SimpleNamespace

from kb_creator.pipeline.five_step_intake import _issue_en_bindings
from kb_creator.pipeline.identity import canonical_bytes, sha256_bytes
from kb_creator.pipeline.review_draft import ReviewDraftError, validate_review_draft_input


@pytest.mark.parametrize("missing_geometry", [False, True])
def test_preview_forwards_verified_geometry_to_semantic_proofs(tmp_path, monkeypatch, missing_geometry):
    from kb_creator.pipeline import review_draft, reconstruction_replay_resume as replay
    from kb_creator.pipeline import review_draft_materialization as materialization
    from kb_creator.pipeline import structural_role_issues as structural
    from kb_creator.scripts import author_reviewed_semantic_decisions as author

    packets = tmp_path / "packets"
    (packets / "pages").mkdir(parents=True)
    (packets / "pages/page-001.json").write_text('{"source_page":1}', encoding="utf-8")
    geometry = {"sealed_test_geometry": [1, 2, 3]}
    geometry_path = tmp_path / "geometry.json"
    if not missing_geometry:
        geometry_path.write_text(json.dumps(geometry), encoding="utf-8")
    comparison = tmp_path / "comparison.json"
    comparison.write_text('{}', encoding="utf-8")
    paths = dict(stage_02_root=tmp_path, comparison=comparison, merge_packets=packets,
                 visual_manifest=tmp_path / "visual.json", geometry_plan=geometry_path)
    monkeypatch.setattr(review_draft, "build_archive_consumption_context", lambda **kwargs: {
        "checked_paths": paths, "target": {"bridge_sha256": "A" * 64}})
    monkeypatch.setattr(replay, "validate_replay_review_queue", lambda authority: SimpleNamespace(queue={}))
    monkeypatch.setattr(replay, "_validate_allowlist", lambda *args: None)
    monkeypatch.setattr(structural, "read_preview_decisions", lambda *args: ({1: {}}, {}))
    monkeypatch.setattr(author, "_visual_inventory", lambda *args: {})
    received = []

    def proof_keys(decisions, packet_map, allowlist, inventory, geometry_context):
        from kb_creator.pipeline.review_draft_materialization import Stage06Proofs
        received.append(geometry_context)
        return Stage06Proofs({"reference"}, {"split"}, {"proof": {"placement": {"markdown_span": {"start": 0, "end": 1}}}})

    monkeypatch.setattr(materialization, "_stage06_proof_keys", proof_keys)
    if missing_geometry:
        with pytest.raises(FileNotFoundError):
            structural.load_structural_preview(tmp_path, tmp_path)
        assert received == []
    else:
        result = structural.load_structural_preview(tmp_path, tmp_path)
        assert received == [geometry]
        assert result["geometry"] is received[0]
        assert result["reference_proof_keys"] == {"reference"}
        assert "proof" in result["visual_assertions"]


def _issue(issue_id: str, *, raw: int = 7) -> dict:
    excerpt = "Exact role text"
    return {
        "issue_id": issue_id, "kind": "source_structure_role_pending",
        "reason": "role differs", "source_pdf_sha256": "A" * 64, "source_page": 1,
        "source_selector": {"comparison_structural_role_v1": {
            "selected_source_key": {"view": "original_pipeline_txt", "raw_index": raw},
            "provisional_selection_purpose": "text", "provisional_block_type": "text",
            "comparison_records": [{"pair_name": "original_pipeline_txt__vs__raster_pipeline_ocr",
                                    "semantic_conflict_index": 0, "record_sha256": "B" * 64}]}},
        "source_excerpt_en": excerpt, "source_excerpt_sha256": sha256_bytes(excerpt.encode()),
        "evidence": [], "candidate_span": {"binding": "ordered_selected_source_v1", "source_page": 1,
                                                "source_key": {"view": "original_pipeline_txt", "raw_index": raw}},
        "state": "open"}


@pytest.mark.parametrize("mutation", ("bad_index", "bad_key", "bad_span", "duplicate_record"))
def test_structural_issue_closed_selector_rejects_tampering(mutation):
    issue = _issue("structural")
    if mutation == "bad_index":
        issue["source_selector"]["comparison_structural_role_v1"]["comparison_records"][0]["semantic_conflict_index"] = -1
    elif mutation == "bad_key":
        issue["source_selector"]["comparison_structural_role_v1"]["selected_source_key"] = {"view": "x"}
    elif mutation == "bad_span":
        issue["candidate_span"]["source_key"]["raw_index"] = 8
    else:
        row = dict(issue["source_selector"]["comparison_structural_role_v1"]["comparison_records"][0])
        issue["source_selector"]["comparison_structural_role_v1"]["comparison_records"].append(row)
    value = {"schema": "kb_creator.review_draft_input.v1", "bindings": {"input": {"path": "input.json", "bytes": 1, "sha256": "C" * 64}},
             "source_issues": {"schema": "kb_creator.review_draft_source_issues.v1", "issues": [issue]}, "unresolved_dispositions": []}
    value["input_sha256"] = sha256_bytes(canonical_bytes(value))
    with pytest.raises(ReviewDraftError):
        validate_review_draft_input(value)


def test_issue_en_bindings_keeps_structural_and_lexical_colocation(tmp_path):
    master = tmp_path / "MASTER_EN.md"
    master.write_text("<!-- source-page-001 -->\n\nExact role text\n", encoding="utf-8")
    evidence = tmp_path / "final.json"; evidence.write_text("{}", encoding="utf-8")
    structural = _issue("structural")
    lexical = dict(structural); lexical["issue_id"] = "lexical"; lexical["kind"] = "translation_source_choice_pending"
    lexical["source_selector"] = {"mechanical_diagnostic": {"code": "three_view_content_mismatch",
                                  "source_keys": [{"view": "original_pipeline_txt", "raw_index": 7}]}}
    bindings = _issue_en_bindings(master, [structural, lexical], [1], evidence)["bindings"]
    assert [row["issue_id"] for row in bindings] == ["structural", "lexical"]
    assert (bindings[0]["character_start"], bindings[0]["character_end"]) == (
        bindings[1]["character_start"], bindings[1]["character_end"])
