from __future__ import annotations

import hashlib
import importlib.util
import json
import os
from pathlib import Path

import pytest


def _sha(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest().upper()


def _resume_fixture():
    source = Path(__file__).with_name("test_reconstruction_replay_resume.py")
    spec = importlib.util.spec_from_file_location("after_anchor_resume_fixture", source)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


@pytest.mark.parametrize(
    "correct_title,relation,assertion_bbox",
    [
        (False, "after_anchor", [120, 200, 580, 240]),
        (True, "after_anchor", [120, 200, 580, 240]),
        (False, "column_after_anchor", [620, 100, 900, 700]),
        (False, "column_sideways_anchor", [620, 100, 900, 700]),
    ],
)
def test_after_anchor_author_replay_promotion_hashes_title_and_author(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path, correct_title: bool,
    relation: str, assertion_bbox: list[int],
):
    """Run the public author/replay/promotion route for an after-anchor proof."""
    from kb_creator.pipeline import reconstruction_promotion as promotion
    from kb_creator.pipeline import reconstruction_replay as replay
    from kb_creator.pipeline import reconstruction_replay_resume as resume
    from kb_creator.pipeline.identity import deterministic_inventory, file_identity
    from kb_creator.pipeline.manifests import sealed
    from kb_creator.scripts import author_reviewed_semantic_decisions as author

    fixture = _resume_fixture()
    authorities, _, _ = fixture._fixture(tmp_path)
    run = authorities.run_root
    from reportlab.pdfgen.canvas import Canvas
    source_pdf = tmp_path / "source.pdf"
    canvas = Canvas(str(source_pdf), pagesize=(612, 792))
    canvas.drawString(72, 720, "Synthetic after-anchor source")
    canvas.showPage()
    canvas.save()
    renderer = Path(os.environ.get("KB_CREATOR_PDFTOPPM", ""))
    assert renderer.is_file(), "KB_CREATOR_PDFTOPPM must point to pdftoppm for this route test"
    run_data = json.loads((run / "run.json").read_text(encoding="utf-8"))
    source_sha256 = _sha(source_pdf.read_bytes())
    renderer_sha256 = _sha(renderer.read_bytes())
    run_data["source"]["sha256"] = source_sha256
    run_data["local"] = {"source_path": str(source_pdf), "common_paths": {"pdftoppm": str(renderer)}}
    (run / "run.json").write_text(json.dumps(run_data), encoding="utf-8")
    geometry_path = run / "outputs/04-visual-merge-bundle/visual/geometry_plan.json"
    geometry = json.loads(geometry_path.read_text(encoding="utf-8"))
    geometry.pop("plan_sha256")
    geometry["renderer"] = {"sha256": renderer_sha256}
    geometry = sealed("kb_creator.mineru_geometry_plan.v2", geometry, digest_key="plan_sha256")
    geometry_path.write_text(json.dumps(geometry), encoding="utf-8")
    title = {"raw_index": 0, "source_page": 1, "type": "text", "bbox": [100, 100, 600, 180], "text": "Cursed Idol"}
    if correct_title:
        title["text"] = "Cur5ed Idol"
    ocr_a = {"raw_index": 20, "source_page": 1, "type": "text", "bbox": [100, 100, 600, 180], "text": "Curscd Id0l"}
    ocr_b = {"raw_index": 21, "source_page": 1, "type": "text", "bbox": [100, 100, 600, 180], "text": "Cursed IdoI"}
    packet_path = run / "outputs/04-visual-merge-bundle/merge_packets/pages/page-001.json"
    packet = json.loads(packet_path.read_text(encoding="utf-8"))
    packet["views"]["original_pipeline_txt"]["blocks"] = [title]
    packet["views"]["original_pipeline_ocr"]["blocks"] = [ocr_a]
    packet["views"]["raster_pipeline_ocr"]["blocks"] = [ocr_b]
    packet_path.write_text(json.dumps(packet), encoding="utf-8")

    comparison_path = run / "outputs/03-compare-views/comparison.json"
    comparison = json.loads(comparison_path.read_text(encoding="utf-8"))
    comparison.pop("comparison_sha256")
    comparison["views"]["original_pipeline_txt"]["blocks"] = [title]
    comparison["views"]["original_pipeline_ocr"]["blocks"] = [ocr_a]
    comparison["views"]["raster_pipeline_ocr"]["blocks"] = [ocr_b]
    comparison = sealed("kb_creator.mineru_multi_view_comparison.v3", comparison, digest_key="comparison_sha256")
    comparison_path.write_text(json.dumps(comparison), encoding="utf-8")

    visual = run / "outputs/04-visual-merge-bundle/visual/original_pipeline_txt/pages/page-001.png"
    visual.parent.mkdir(parents=True, exist_ok=True)
    visual.write_bytes(b"after-anchor source visual")
    manifest_path = run / "outputs/04-visual-merge-bundle/visual/visual_manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest.pop("manifest_sha256")
    manifest["files"].append({"path": "visual/original_pipeline_txt/pages/page-001.png", **file_identity(visual)})
    manifest = sealed("kb_creator.mineru_visual_merge_bundle.v3", manifest, digest_key="manifest_sha256")
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")

    queue_path = run / "review/review_queue.json"
    queue = json.loads(queue_path.read_text(encoding="utf-8"))
    queue.pop("queue_sha256")
    queue["source_sha256"] = source_sha256
    queue["comparison"] = {"path": "outputs/03-compare-views/comparison.json", **file_identity(comparison_path)}
    queue["items"][0]["merge_packet"] = {"path": "merge_packets/pages/page-001.json", **file_identity(packet_path)}
    queue = sealed("kb_creator.review_queue.v2", queue, digest_key="queue_sha256")
    queue_path.write_text(json.dumps(queue), encoding="utf-8")

    monkeypatch.setattr(replay, "validate_replayed_prefix", lambda _root: authorities)
    monkeypatch.setattr(resume, "validate_replayed_prefix", lambda _root: authorities)

    drafts = tmp_path / "drafts"
    drafts.mkdir()
    (drafts / "page-001.json").write_text(
        json.dumps({
            "schema": "kb_creator.mineru_ai_page_decision.v1",
            "source_page": 1,
            "semantic_role": "body",
            "overlay_preference": "original_pipeline_txt",
            "selected_blocks": [{"view": "original_pipeline_txt", "raw_index": 0, "purpose": "text"}],
            "markdown": "# Cursed Idol\n\nVisibleAuthor",
            "assets": [],
            "unresolved": [],
            "review": {"visual_reviewed": True, "notes": "after-anchor proof reviewed"},
        }),
        encoding="utf-8",
    )
    spec = tmp_path / "spec.json"
    spec.write_text(
        json.dumps({
            "semantic_structure_profile": "reviewed_role_outline_and_partitions_v2",
            "pages": [{
                "source_page": 1,
                "role_contract": {"role": "body", "group_id": "after-anchor"},
                "units": [
                    {"id": "title", "kind": "heading", "representation": "atx_heading", "raw_indices": [0], "start": "# Cursed Idol", "end": "# Cursed Idol", "heading_level": 1},
                ],
            }],
            "visual_text_assertions": [{
                "assertion_id": "visible-author",
                "source_page": 1,
                "text": "VisibleAuthor",
                "relation": relation,
                "bbox": assertion_bbox,
                "anchor": {"view_id": "original_pipeline_txt", "raw_index": 0},
                "rationale": "printed author line follows the title or begins the right column",
            }],
            "ocr_equivalence_classes": [{
                "class_id": "title-ocr",
                "source_page": 1,
                "canonical": {"view_id": "original_pipeline_txt", "raw_index": 0},
                "alternates": [
                    {"view_id": "original_pipeline_ocr", "raw_index": 20},
                    {"view_id": "raster_pipeline_ocr", "raw_index": 21},
                ],
                "rationale": "reviewed OCR variants preserve the printed title",
                "visual_verdict": "canonical_proof_complete_for_region_alternates_are_ocr_corruption",
                "equivalence_policy": "reviewed_visual_full_unit_v1",
                "supporting_assertion_ids": ["visible-author"],
            }],
        }),
        encoding="utf-8",
    )

    if correct_title:
        draft_path = drafts / "page-001.json"
        draft = json.loads(draft_path.read_text(encoding="utf-8"))
        draft["review"]["notes"] += "\ntext correction: Cur5ed -> Cursed; reason: printed source title."
        draft_path.write_text(json.dumps(draft), encoding="utf-8")
    baseline = tmp_path / "validation-baseline"
    (baseline / "pages").mkdir(parents=True)
    (baseline / "pages/page-001.json").write_bytes((drafts / "page-001.json").read_bytes())
    if relation == "column_sideways_anchor":
        with pytest.raises(ValueError, match="source assertion relation is invalid"):
            author.validate_spec(run, baseline, [spec])
        return
    assert author.validate_spec(run, baseline, [spec])["visual_assertion_count"] == 1
    authored = tmp_path / "authored"
    author.author_drafts(run, drafts, authored, [spec])
    result = resume.replay_resume_engine(run, authored / "decision_set.json", authored)
    assert result["state"] == "candidate_ready_for_reconstruction_qa"
    audit = json.loads((run / "outputs/05-fidelity-audit/audit.json").read_text(encoding="utf-8"))
    assert audit["passed"] is True
    allowlist = json.loads((authored / "reviewed_allowlist.v3.json").read_text(encoding="utf-8"))
    proof = allowlist["ocr_equivalence_classes"][0]["canonical_proof"]
    assert proof["supporting_assertion_ids"] == ["visible-author"]
    assert proof["expected_normalized_sha256"] == _sha(b"cursedidolvisibleauthor")

    submission = resume.load_replay_submission(authorities)
    decision_set = json.loads((submission.root / "decision_set.json").read_text(encoding="utf-8"))
    promotion._validate_candidate(
        run,
        {"source": {"page_count": 1}, "page_roles": [{"first_page": 1, "last_page": 1, "role": "body"}], "scope": {"required_entities": {"numbered_player_handouts": 0}}},
        submission.root,
        decision_set,
        run=run_data,
        fidelity_path=run / "outputs/05-fidelity-audit/audit.json",
        fidelity=audit,
        candidate_root=run / "outputs/06-materialize-candidate",
        replay_bridge_sha256=authorities.bridge_sha256,
        replay_submission=submission.receipt,
        stage6_files=deterministic_inventory(run / "outputs/06-materialize-candidate"),
    )
