import hashlib
import copy
import json
from pathlib import Path

import pytest


from kb_creator.pipeline import semantic_structure as module
from kb_creator.scripts import author_reviewed_semantic_decisions as author


def _span(lines, start, end):
    return {"start_line": start, "end_line": end, "sha256": hashlib.sha256("\n".join(lines[start - 1:end]).encode()).hexdigest().upper()}


def _fixture():
    lines = ["# Phlebotomy", "", "by Jeffrey Moeller", "", "## Themes"]
    visual = {"path": "outputs/04-visual-merge-bundle/visual/original_pipeline_txt/pages/page-147.png", "bytes": 1, "sha256": "A" * 64}
    title = {"id": "title", "kind": "heading", "representation": "atx_heading", "source_blocks": [], "source_fragments": [], "visual_assertion_ids": ["proof"], "markdown_span": _span(lines, 1, 3), "container_parent": None, "semantic_parent": None, "continuation_of": None, "heading_level": 1, "item_count": None}
    footer = {"id": "footer", "kind": "heading", "representation": "atx_heading", "source_blocks": [{"view": "original_pipeline_txt", "raw_index": 2903}], "source_fragments": [{"view": "original_pipeline_txt", "raw_index": 2903, "source_sha256": hashlib.sha256(b"Themes").hexdigest().upper(), "normalized_sha256": hashlib.sha256(b"themes").hexdigest().upper(), "start": 0, "end": 6, "fragment_sha256": hashlib.sha256(b"Themes").hexdigest().upper()}], "markdown_span": _span(lines, 5, 5), "container_parent": None, "semantic_parent": None, "continuation_of": None, "heading_level": 2, "item_count": None}
    decision = {"semantic_role": "body", "markdown": "\n".join(lines), "selected_blocks": [{"view": "original_pipeline_txt", "raw_index": 2903, "purpose": "text"}], "assets": [], "semantic_structure": {"schema": module.SCHEMA_V2, "profile": module.PROFILE_V2, "role_contract": {"role": "body", "group_id": "fear"}, "review": {"state": "complete", "visual": visual}, "units": [title, footer]}}
    anchor = {"source_page": 147, "view_id": "original_pipeline_txt", "raw_index": 2903, "block_type": "text", "bbox": [100, 400, 900, 500]}
    assertion = {"source_page": 147, "text": "Phlebotomy\nby Jeffrey Moeller", "placement": {"relation": "before_anchor", "anchor_unit": anchor, "expected_pair_sha256": "B" * 64, "markdown_span": {"start": 0, "end": len("phlebotomybyjeffreymoeller")}}}
    packet = {"views": {"original_pipeline_txt": {"blocks": [{"raw_index": 2903, "text": "Themes", "assets": []}]}}}
    return decision, packet, visual, assertion


def test_positional_heading_keeps_byline_out_of_display_label():
    assert module.extract_atx_heading_label("# Phlebotomy\n\nby Jeffrey Moeller", 1) == "Phlebotomy"


def test_stage06_preserves_raw_assertions_for_legacy_consumers():
    from kb_creator.pipeline.review_draft_materialization import _stage06_proof_keys

    assertion = {"assertion_id": "legacy-proof", "source_page": 1, "text": "legacy"}
    stage06 = _stage06_proof_keys({1: {"source_page": 1}}, {1: {}},
                                  {"visual_text_assertions": [assertion]}, {}, {})
    assert stage06.reference_proof_keys == set()
    assert stage06.split_structure_proof_keys == set()
    assert stage06.visual_assertions == {"legacy-proof": assertion}


@pytest.mark.parametrize("failure", [None, "missing_geometry", "tampered_text"])
def test_stage06_forwards_bound_positional_context(monkeypatch, failure):
    from kb_creator.pipeline.review_draft_materialization import _stage06_proof_keys, ReviewDraftMaterializationError
    from kb_creator.scripts import audit_mineru_ai_merge_fidelity as audit
    decision, packet, visual, assertion = _fixture()
    assertion["assertion_id"] = "proof"
    assertion["placement"].pop("markdown_span")
    geometry = {"sealed_context": True}
    if failure == "missing_geometry": geometry = {}
    if failure == "tampered_text": assertion["text"] += " changed"
    def context(page, packet_arg, decision_arg, geometry_arg, errors):
        assert page == 147 and packet_arg is packet and decision_arg is decision
        if not geometry_arg.get("sealed_context"):
            errors.append("missing geometry")
        return {"rendered": "phlebotomybyjeffreymoellerthemes", "mappings": [
            {"unit": {"view_id": "original_pipeline_txt", "raw_index": 2903}, "markdown_span": [26, 32]}]}
    monkeypatch.setattr(audit, "_v3_page_context", context)
    args = ({147: decision}, {147: packet}, {"visual_text_assertions": [assertion]},
            {visual["path"]: {"bytes": 1, "sha256": "A" * 64}}, geometry)
    if failure:
        with pytest.raises(ReviewDraftMaterializationError, match="positional assertion context"):
            _stage06_proof_keys(*args)
    else:
        _stage06_proof_keys(*args)
    assert "markdown_span" not in assertion["placement"]


def test_authoring_adapter_materializes_ephemeral_positional_interval_without_mutating_allowlist(monkeypatch):
    from kb_creator.scripts import audit_mineru_ai_merge_fidelity as audit
    row = {"assertion_id": "proof", "source_page": 147, "text": "Phlebotomy\nby Jeffrey Moeller", "placement": {"relation": "before_anchor", "anchor_unit": {"view_id": "original_pipeline_txt", "raw_index": 2903}, "expected_pair_sha256": "B" * 64}}
    monkeypatch.setattr(audit, "_v3_page_context", lambda *args: {"rendered": "phlebotomybyjeffreymoellerthemes", "mappings": [{"unit": {"view_id": "original_pipeline_txt", "raw_index": 2903}, "markdown_span": [26, 32]}]})
    result = author.semantic_assertion_map({"proof": row}, {147: {}}, {147: {}}, {})
    assert result["proof"]["placement"]["markdown_span"] == {"start": 0, "end": 26}
    assert "markdown_span" not in row["placement"]


def test_source_less_positional_heading_requires_complete_combined_proof_span():
    decision, packet, visual, assertion = _fixture()
    assert module.validate_semantic_structure({147: decision}, {147: packet}, {visual["path"]: {"bytes": 1, "sha256": "A" * 64}}, required_pages=[147], visual_assertions={"proof": assertion})["pages"][0]["validated_unit_count"] == 2
    assertion["text"] = "Phlebotomy"
    with pytest.raises(module.SemanticStructureError, match="coverage"):
        module.validate_semantic_structure({147: decision}, {147: packet}, {visual["path"]: {"bytes": 1, "sha256": "A" * 64}}, required_pages=[147], visual_assertions={"proof": assertion})


def test_actual_page147_title_requires_reused_enriched_positional_context():
    """The sealed page147 title passes only with the derived Stage06 map."""
    from kb_creator.pipeline.review_draft_materialization import _stage06_proof_keys
    from kb_creator.scripts.author_reviewed_semantic_decisions import _visual_inventory
    from kb_creator.scripts.materialize_mineru_ai_merge import _validated_v2_title_role

    reviewed = Path("kb_creator/working/fears-sharp-little-needles/reviewed")
    run, authored = reviewed / "author-replay-n76-v01", reviewed / "r0-source-n150-authored-v01"
    decision = json.loads((authored / "pages/page-147.json").read_text(encoding="utf-8"))
    packet = json.loads((run / "outputs/04-visual-merge-bundle/merge_packets/pages/page-147.json").read_text(encoding="utf-8"))
    geometry = json.loads((run / "outputs/04-visual-merge-bundle/visual/geometry_plan.json").read_text(encoding="utf-8"))
    allowlist = json.loads((authored / "reviewed_allowlist.v3.json").read_text(encoding="utf-8"))
    allowlist["visual_text_assertions"] = [
        row for row in allowlist["visual_text_assertions"] if row.get("source_page") == 147
    ]
    stage06 = _stage06_proof_keys({147: decision}, {147: packet}, allowlist, _visual_inventory(run), geometry)
    selected = next(row for row in decision["selected_blocks"]
                    if (row["view"], row["raw_index"]) == ("original_pipeline_txt", 2903))
    source = next(row for row in packet["views"][selected["view"]]["blocks"]
                  if row["raw_index"] == selected["raw_index"])["text"]
    key = (selected["view"], selected["raw_index"])
    assert _validated_v2_title_role(decision, packet, source, key,
                                    stage06.split_structure_proof_keys, stage06.visual_assertions)
    raw_assertions = {row["assertion_id"]: row for row in allowlist["visual_text_assertions"]}
    assert not _validated_v2_title_role(decision, packet, source, key,
                                        stage06.split_structure_proof_keys, raw_assertions)
    stripped = copy.deepcopy(stage06.visual_assertions)
    positional = next(row for row in stripped.values()
                      if row.get("placement", {}).get("relation") == "before_anchor")
    positional["placement"].pop("markdown_span")
    assert not _validated_v2_title_role(decision, packet, source, key,
                                        stage06.split_structure_proof_keys, stripped)


@pytest.mark.parametrize("mutate", ["no-proof", "two-proofs", "ordinary", "asset"])
def test_source_less_shape_fails_closed(mutate):
    decision, packet, visual, assertion = _fixture()
    unit = decision["semantic_structure"]["units"][0]
    if mutate == "no-proof": unit.pop("visual_assertion_ids")
    elif mutate == "two-proofs": unit["visual_assertion_ids"] = ["proof", "other"]
    elif mutate == "ordinary": unit["kind"] = "handout"; unit["representation"] = "blockquote"; unit["heading_level"] = None
    else: assertion["placement"]["relation"] = "within_selected_asset_region"
    with pytest.raises(module.SemanticStructureError):
        module.validate_semantic_structure({147: decision}, {147: packet}, {visual["path"]: {"bytes": 1, "sha256": "A" * 64}}, required_pages=[147], visual_assertions={"proof": assertion, "other": assertion})
