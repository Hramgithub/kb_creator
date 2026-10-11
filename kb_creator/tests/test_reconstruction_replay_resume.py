from __future__ import annotations

import copy
import json
import os
from pathlib import Path

import pytest
from reportlab.pdfgen import canvas

from kb_creator.pipeline.identity import file_identity
from kb_creator.pipeline.manifests import sealed
from kb_creator.pipeline.reconstruction_replay import FreshReplayAuthorities
from kb_creator.pipeline import reconstruction_replay as replay
from kb_creator.pipeline import reconstruction_replay_resume as resume


VIEWS = ["original_pipeline_txt", "original_pipeline_ocr", "raster_pipeline_ocr"]
SHA = "A" * 64


def _write(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _fixture(tmp_path: Path) -> tuple[FreshReplayAuthorities, Path, Path]:
    root = tmp_path / "fresh-replay-04"
    source_pdf = tmp_path / "synthetic-source.pdf"
    document = canvas.Canvas(str(source_pdf), pagesize=(612, 792), invariant=1)
    document.drawString(72, 720, "Synthetic replay source")
    document.showPage()
    document.save()
    renderer = Path(os.environ.get("KB_CREATOR_PDFTOPPM", ""))
    assert renderer.is_file(), "KB_CREATOR_PDFTOPPM must point to pdftoppm for replay fixtures"
    source_identity = file_identity(source_pdf)
    renderer_identity = file_identity(renderer)
    run = {
        "schema": "kb_creator.run_spec.v2",
        "portable_identity_sha256": SHA,
        "contract": {"sha256": "B" * 64},
        "source": {"sha256": source_identity["sha256"]},
        "scope": {"ordered_pages": [1]},
        "local": {
            "source_path": str(source_pdf),
            "common_paths": {"pdftoppm": str(renderer)},
        },
    }
    _write(root / "run.json", run)
    bridge = sealed("kb_creator.stage_replay_bridge.v1", {"run_identity_sha256": SHA}, digest_key="bridge_sha256")
    _write(root / "replay/bridge.json", bridge)
    raw_root = root / "outputs/02-mineru-three-view"
    raw_root.mkdir(parents=True)
    blocks: dict[str, dict] = {}
    view_records: dict[str, dict] = {}
    for index, view_id in enumerate(VIEWS):
        artifact = raw_root / "views" / view_id / "artifacts" / "content_list.json"
        _write(artifact, [])
        block = {"raw_index": index, "source_page": 1, "type": "text", "bbox": [100, 100, 900, 200], "text": "Stable heading", "semantic_evidence": {"text_level": None, "v2_title": False, "middle_title": False, "markdown_heading": False, "model_title": False}, "assets": []}
        blocks[view_id] = block
        view_records[view_id] = {"artifacts": {"content_list": {"base": "view_artifact_root", "view_id": view_id, "path": "content_list.json", **file_identity(artifact)}}, "blocks": [block]}
    comparison = sealed("kb_creator.mineru_multi_view_comparison.v3", {"status": "pass_for_review", "run_identity_sha256": SHA, "required_views": VIEWS, "succeeded_views": VIEWS, "skipped_views": [], "views": view_records, "pairwise": {}, "failures": []}, digest_key="comparison_sha256")
    comparison_path = root / "outputs/03-compare-views/comparison.json"
    _write(comparison_path, comparison)
    bundle = root / "outputs/04-visual-merge-bundle"
    packet = {"source_page": 1, "semantic_role": "body", "views": {view: {"blocks": [blocks[view]]} for view in VIEWS}}
    packet_path = bundle / "merge_packets/pages/page-001.json"
    _write(packet_path, packet)
    _write(bundle / "merge_packets/merge_index.json", {"by_source_page": [{"source_page": 1, "semantic_role": "body", "priority_score": 0, "packet": "pages/page-001.json"}], "by_priority": []})
    geometry = sealed("kb_creator.mineru_geometry_plan.v2", {"renderer": renderer_identity, "observed_geometry": [{"view_id": view, "source_page": 1, "media_box_coordinates": ["0", "0", "612", "792"], "crop_box_coordinates": ["0", "0", "612", "792"], "rotation_degrees": 0, "user_unit": "1", "effective_displayed_size_points": ["612", "792"]} for view in VIEWS]}, digest_key="plan_sha256")
    geometry_path = bundle / "visual/geometry_plan.json"
    _write(geometry_path, geometry)
    visual_page = bundle / "visual/triptychs/page-001.png"
    visual_page.parent.mkdir(parents=True, exist_ok=True)
    visual_page.write_bytes(b"synthetic visual")
    visual = sealed("kb_creator.mineru_visual_merge_bundle.v3", {"files": [{"path": "visual/triptychs/page-001.png", **file_identity(visual_page)}]}, digest_key="manifest_sha256")
    visual_path = bundle / "visual/visual_manifest.json"
    _write(visual_path, visual)
    queue = sealed("kb_creator.review_queue.v2", {
        "run_identity_sha256": SHA, "contract_sha256": "B" * 64, "source_sha256": source_identity["sha256"],
        "comparison": {"path": "outputs/03-compare-views/comparison.json", **file_identity(comparison_path)},
        "bridge": {"path": "replay/bridge.json", **file_identity(root / "replay/bridge.json"), "bridge_sha256": bridge["bridge_sha256"]},
        "required_decision_schema": "kb_creator.mineru_ai_page_decision.v1",
        "items": [{"id": "page-001", "source_page": 1, "contract_role": "body", "contract_traits": [], "contract_strategies": [], "merge_packet": {"path": "merge_packets/pages/page-001.json", **file_identity(packet_path)}, "issue_kinds": [], "required_decision_file": "pages/page-001.json", "state": "open"}],
    }, digest_key="queue_sha256")
    _write(root / "review/review_queue.json", queue)
    decisions = tmp_path / "decisions"
    decision = {"schema": "kb_creator.mineru_ai_page_decision.v1", "source_page": 1, "semantic_role": "body", "overlay_preference": VIEWS[0], "selected_blocks": [{"view": VIEWS[0], "raw_index": 0, "purpose": "text"}], "markdown": "Stable heading", "assets": [], "unresolved": [], "review": {"visual_reviewed": True, "notes": "synthetic review"}}
    decision_path = decisions / "pages/page-001.json"
    _write(decision_path, decision)
    allowlist = {"schema": resume.ALLOWLIST_SCHEMA, "authority": {"run_identity_sha256": SHA, "bridge_sha256": bridge["bridge_sha256"], "review_queue_sha256": queue["queue_sha256"], "comparison_sha256": comparison["comparison_sha256"], "geometry_plan_sha256": geometry["plan_sha256"], "visual_manifest_sha256": visual["manifest_sha256"]}, "substitutions": [], "source_text_exclusions": [], "visual_text_assertions": [], "ocr_equivalence_classes": []}
    allow_path = decisions / "reviewed_allowlist.json"
    _write(allow_path, allowlist)
    decision_set = {"schema": "kb_creator.reconstruction_decision_set.v1", "review_queue_sha256": queue["queue_sha256"], "contract_sha256": "B" * 64, "source_sha256": source_identity["sha256"], "decisions": [{"source_page": 1, "path": "pages/page-001.json", **file_identity(decision_path)}], "reviewed_allowlist": {"path": "reviewed_allowlist.json", **file_identity(allow_path)}, "submission_state": "submitted_for_validation"}
    decision_set_path = decisions / "decision_set.json"
    _write(decision_set_path, decision_set)
    authorities = FreshReplayAuthorities(root, raw_root, comparison_path, bundle / "merge_packets", visual_path, geometry_path, bridge["bridge_sha256"])
    return authorities, decision_set_path, decisions


def _patch_prefix(monkeypatch: pytest.MonkeyPatch, authorities: FreshReplayAuthorities) -> None:
    monkeypatch.setattr(resume, "validate_replayed_prefix", lambda root: authorities)
    monkeypatch.setattr(replay, "validate_replayed_prefix", lambda root: authorities)


def test_full_synthetic_replay04_submission_audit_materialize(monkeypatch: pytest.MonkeyPatch, tmp_path: Path):
    jsonschema = pytest.importorskip("jsonschema")
    authorities, decision_set, decisions = _fixture(tmp_path)
    _patch_prefix(monkeypatch, authorities)
    result = resume.replay_resume_engine(authorities.run_root, decision_set, decisions)
    assert result["state"] == "candidate_ready_for_reconstruction_qa"
    assert result["acceptance_inferred"] is False
    assert [row["stage_id"] for row in result["stages"]] == list(resume.STAGES)
    audit = json.loads((authorities.run_root / "outputs/05-fidelity-audit/audit.json").read_text(encoding="utf-8"))
    assert audit["schema"] == resume.AUDIT_SCHEMA and audit["passed"] is True and audit["errors"] == []
    provenance = json.loads((authorities.run_root / "outputs/06-materialize-candidate/MERGE_PROVENANCE.json").read_text(encoding="utf-8"))
    assert provenance["schema"] == resume.PROVENANCE_SCHEMA and provenance["acceptance_inferred"] is False
    contracts = Path(resume.__file__).parents[1] / "contracts"
    instances = [
        ("validated_reconstruction_submission.v2.schema.json", json.loads((authorities.run_root / "review/validated-submission-v2/submission_inventory.json").read_text(encoding="utf-8"))),
        ("replay_downstream_stage_manifest.v1.schema.json", json.loads((authorities.run_root / "stages/05-fidelity-audit/stage.json").read_text(encoding="utf-8"))),
        ("replay_downstream_stage_manifest.v1.schema.json", json.loads((authorities.run_root / "stages/06-materialize-candidate/stage.json").read_text(encoding="utf-8"))),
        ("ai_merge_fidelity_audit.v3.schema.json", audit),
        ("mineru_ai_merge_provenance.v3.schema.json", provenance),
        ("replay_resume_result.v1.schema.json", result),
    ]
    for schema_name, instance in instances:
        schema = json.loads((contracts / schema_name).read_text(encoding="utf-8"))
        jsonschema.Draft202012Validator.check_schema(schema)
        jsonschema.validate(instance, schema)
    assert not any("acceptance" in path.name.lower() for path in authorities.run_root.rglob("*"))


def test_v3_audit_schema_closes_source_page_render_proofs(tmp_path: Path):
    jsonschema = pytest.importorskip("jsonschema")
    schema = json.loads(
        (Path(resume.__file__).parents[1] / "contracts/ai_merge_fidelity_audit.v3.schema.json").read_text(encoding="utf-8")
    )
    authorities, decision_set, decisions = _fixture(tmp_path)
    monkeypatch = pytest.MonkeyPatch()
    try:
        _patch_prefix(monkeypatch, authorities)
        resume.replay_resume_engine(authorities.run_root, decision_set, decisions)
    finally:
        monkeypatch.undo()
    audit = json.loads((authorities.run_root / "outputs/05-fidelity-audit/audit.json").read_text(encoding="utf-8"))
    proof = {
        "origin": "source_pdf_page_render_v1",
        "logical_name": "page-001.png",
        "source_page": 1,
        "render": {
            "recipe": "pdftoppm-mediabox-single-page-png-v1",
            "dpi": 144,
            "renderer_sha256": "A" * 64,
            "pixels": [1224, 1584],
            "bytes": 1,
            "sha256": "B" * 64,
        },
    }
    audit["pages"][0]["source_page_renders"] = [proof]
    jsonschema.validate(audit, schema)
    malformed = copy.deepcopy(audit)
    malformed["pages"][0]["source_page_renders"][0]["render"]["pixels"] = [0, 1584]
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(malformed, schema)


@pytest.mark.parametrize("mutation", ["bridge", "queue", "decision", "allowlist"])
def test_stale_authority_identity_rejected_before_stage05(monkeypatch: pytest.MonkeyPatch, tmp_path: Path, mutation: str):
    authorities, decision_set, decisions = _fixture(tmp_path)
    _patch_prefix(monkeypatch, authorities)
    if mutation == "bridge":
        authorities = FreshReplayAuthorities(authorities.run_root, authorities.stage_02_root, authorities.comparison, authorities.merge_packets, authorities.visual_manifest, authorities.geometry_plan, "F" * 64)
        _patch_prefix(monkeypatch, authorities)
    elif mutation == "queue":
        (authorities.run_root / "review/review_queue.json").write_text("{}", encoding="utf-8")
    elif mutation == "decision":
        (decisions / "pages/page-001.json").write_text("{}", encoding="utf-8")
    else:
        value = json.loads((decisions / "reviewed_allowlist.json").read_text(encoding="utf-8")); value["authority"]["comparison_sha256"] = "F" * 64; _write(decisions / "reviewed_allowlist.json", value)
    with pytest.raises((resume.ReplayResumeError, KeyError)):
        resume.replay_resume_engine(authorities.run_root, decision_set, decisions)
    assert not (authorities.run_root / "outputs/05-fidelity-audit").exists()


def test_stage06_failure_is_atomic_and_never_accepts(monkeypatch: pytest.MonkeyPatch, tmp_path: Path):
    authorities, decision_set, decisions = _fixture(tmp_path)
    _patch_prefix(monkeypatch, authorities)
    submission = resume.materialize_replay_submission_snapshot(authorities, decision_set, decisions)
    adapters = resume.replay_downstream_adapters(authorities, submission)
    def fail(output: Path) -> dict:
        (output / "partial.txt").write_text("partial", encoding="utf-8")
        raise resume.ReplayResumeError("synthetic stage06 failure")
    adapters["materialize_candidate"] = fail
    with pytest.raises(resume.ReplayResumeError, match="stage06 failure"):
        resume.replay_resume_engine(authorities.run_root, decision_set, decisions, adapters=adapters)
    assert (authorities.run_root / "outputs/05-fidelity-audit/audit.json").is_file()
    assert not (authorities.run_root / "outputs/06-materialize-candidate").exists()
    assert not (authorities.run_root / "stages/06-materialize-candidate").exists()


def test_stage06_access_gate_runs_on_final_path_before_manifest(monkeypatch: pytest.MonkeyPatch, tmp_path: Path):
    authorities, decision_set, decisions = _fixture(tmp_path)
    _patch_prefix(monkeypatch, authorities)
    observed: list[Path] = []

    def normalize(path: Path) -> dict[str, object]:
        observed.append(path)
        assert path == authorities.run_root / "outputs/06-materialize-candidate"
        assert path.is_dir()
        assert ".stage-" not in path.name
        assert not (authorities.run_root / "stages/06-materialize-candidate").exists()
        return {"state": "normalized"}

    monkeypatch.setattr(resume, "normalize_publication_access_if_managed", normalize)
    result = resume.replay_resume_engine(authorities.run_root, decision_set, decisions)

    assert result["state"] == "candidate_ready_for_reconstruction_qa"
    assert observed == [authorities.run_root / "outputs/06-materialize-candidate"]


@pytest.mark.parametrize(
    ("access_result", "message"),
    [
        ({"state": "unknown"}, "did not complete"),
        ({"state": "skipped", "reason": "managed_windows_failure"}, "did not complete"),
    ],
)
def test_stage06_unexpected_access_state_fails_closed(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    access_result: dict[str, str],
    message: str,
):
    authorities, decision_set, decisions = _fixture(tmp_path)
    _patch_prefix(monkeypatch, authorities)
    monkeypatch.setattr(
        resume,
        "normalize_publication_access_if_managed",
        lambda path: access_result,
    )

    with pytest.raises(resume.ReplayResumeError, match=message):
        resume.replay_resume_engine(authorities.run_root, decision_set, decisions)

    assert (authorities.run_root / "outputs/05-fidelity-audit/audit.json").is_file()
    assert not (authorities.run_root / "outputs/06-materialize-candidate").exists()
    assert not (authorities.run_root / "stages/06-materialize-candidate").exists()
    quarantines = list((authorities.run_root / "failures").glob(".06-materialize-candidate-*"))
    assert len(quarantines) == 1
    assert (quarantines[0] / "output/RECONSTRUCTED_EN.md").is_file()


def test_stage06_access_exception_quarantines_only_fresh_stage(monkeypatch: pytest.MonkeyPatch, tmp_path: Path):
    authorities, decision_set, decisions = _fixture(tmp_path)
    _patch_prefix(monkeypatch, authorities)

    def fail(path: Path) -> dict[str, object]:
        assert path == authorities.run_root / "outputs/06-materialize-candidate"
        raise OSError("synthetic ACL failure")

    monkeypatch.setattr(resume, "normalize_publication_access_if_managed", fail)
    with pytest.raises(OSError, match="synthetic ACL failure"):
        resume.replay_resume_engine(authorities.run_root, decision_set, decisions)

    assert (authorities.run_root / "outputs/05-fidelity-audit/audit.json").is_file()
    assert not (authorities.run_root / "outputs/06-materialize-candidate").exists()
    assert not (authorities.run_root / "stages/06-materialize-candidate").exists()
    quarantines = list((authorities.run_root / "failures").glob(".06-materialize-candidate-*"))
    assert len(quarantines) == 1
    assert (quarantines[0] / "output/RECONSTRUCTED_EN.md").is_file()


def test_stage06_access_gate_rejects_candidate_byte_mutation(monkeypatch: pytest.MonkeyPatch, tmp_path: Path):
    authorities, decision_set, decisions = _fixture(tmp_path)
    _patch_prefix(monkeypatch, authorities)

    def mutate(path: Path) -> dict[str, object]:
        candidate = path / "RECONSTRUCTED_EN.md"
        candidate.write_text(candidate.read_text(encoding="utf-8") + "mutated\n", encoding="utf-8")
        return {"state": "normalized"}

    monkeypatch.setattr(resume, "normalize_publication_access_if_managed", mutate)
    with pytest.raises(resume.ReplayResumeError, match="changed artifact bytes"):
        resume.replay_resume_engine(authorities.run_root, decision_set, decisions)

    assert not (authorities.run_root / "outputs/06-materialize-candidate").exists()
    quarantines = list((authorities.run_root / "failures").glob(".06-materialize-candidate-*"))
    assert len(quarantines) == 1


def test_stage06_rerun_access_failure_preserves_existing_pair(monkeypatch: pytest.MonkeyPatch, tmp_path: Path):
    authorities, decision_set, decisions = _fixture(tmp_path)
    _patch_prefix(monkeypatch, authorities)
    monkeypatch.setattr(
        resume,
        "normalize_publication_access_if_managed",
        lambda path: {"state": "normalized"},
    )
    first = resume.replay_resume_engine(authorities.run_root, decision_set, decisions)
    output = authorities.run_root / "outputs/06-materialize-candidate"
    manifest = authorities.run_root / "stages/06-materialize-candidate/stage.json"
    output_identity = file_identity(output / "RECONSTRUCTED_EN.md")
    manifest_identity = file_identity(manifest)

    def fail(path: Path) -> dict[str, object]:
        assert path == output
        raise OSError("synthetic rerun ACL failure")

    monkeypatch.setattr(resume, "normalize_publication_access_if_managed", fail)
    with pytest.raises(OSError, match="synthetic rerun ACL failure"):
        resume.replay_resume_engine(authorities.run_root, decision_set, decisions)

    assert output.is_dir() and manifest.is_file()
    assert file_identity(output / "RECONSTRUCTED_EN.md") == output_identity
    assert file_identity(manifest) == manifest_identity
    assert first["stages"][1]["manifest_sha256"] == json.loads(manifest.read_text(encoding="utf-8"))["manifest_sha256"]


def test_stage06_access_normalizer_is_bound_into_producer_closure():
    assert "kb_creator/scripts/normalize_publication_access.py" in resume.DOWNSTREAM_IMPLEMENTATION


def test_downstream_and_promotion_inventories_bind_proof_helpers():
    from kb_creator.pipeline import reconstruction_promotion as promotion

    required = {
        "kb_creator/pipeline/reconstruction_asset_inventory.py",
        "kb_creator/pipeline/text_segmentation.py",
    }
    assert required <= set(resume.DOWNSTREAM_IMPLEMENTATION)
    assert required <= {row["path"] for row in promotion._implementation()["files"]}


def test_cli_resume_is_dedicated_and_has_no_runtime_or_acceptance_flags():
    from kb_creator.__main__ import _parser
    args = _parser().parse_args(["replay", "resume", "--run-root", "r", "--decisions", "d", "--decisions-root", "p"])
    assert args.replay_command == "resume"
    for name in ("mineru_root", "source", "acceptance", "trust", "force"):
        assert not hasattr(args, name)


def test_downstream_schemas_are_closed_and_parse():
    contracts = Path(resume.__file__).parents[1] / "contracts"
    for relative in resume.DOWNSTREAM_IMPLEMENTATION:
        if not relative.endswith(".schema.json"):
            continue
        schema = json.loads((Path(resume.__file__).parents[2] / relative).read_text(encoding="utf-8"))
        assert schema["$schema"].endswith("2020-12/schema")
        assert schema["type"] == "object" and schema["additionalProperties"] is False


def test_resume_module_never_calls_legacy_resume_or_acceptance():
    source = Path(resume.__file__).read_text(encoding="utf-8")
    for forbidden in ("reconstruction.resume_engine(", "_validate_stage_prefix(", "record_reconstruction_acceptance", "acceptance_inferred\": True"):
        assert forbidden not in source
