import hashlib
import json
import os
import shutil
from pathlib import Path

import pytest

from kb_creator.pipeline.review_draft_materialization import (
    ReviewDraftMaterializationError,
    SCHEMA,
    verify_descriptor,
)
from kb_creator.pipeline.identity import deterministic_inventory, file_identity
from kb_creator.pipeline.five_step_intake import (
    FiveStepIntakeError,
    ISSUE_EN_BINDINGS_SCHEMA,
    REVIEW_MASTER_MANIFEST_SCHEMA,
    _inventory_value,
    _issue_en_bindings,
    _source_spans,
    build_review_master_en,
    verify_master_en,
)
from kb_creator.pipeline.manifests import sealed
from kb_creator.pipeline.source_page_render import (
    ORIGIN,
    RECIPE,
    render_source_pdf_page,
)
from kb_creator.scripts.audit_mineru_ai_merge_fidelity import audit_v3_content
from kb_creator.scripts.materialize_mineru_ai_merge import _validate_decision


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def _renderer() -> Path:
    value = shutil.which("pdftoppm")
    if not value:
        pytest.skip("pdftoppm is unavailable")
    return Path(value)


def _pdf(path: Path) -> None:
    from reportlab.pdfgen.canvas import Canvas
    canvas = Canvas(str(path), pagesize=(72, 144))
    canvas.drawString(10, 120, "reviewed source")
    canvas.showPage()
    canvas.save()


def test_real_stage05_and_stage06_source_render_proof_are_bound(tmp_path):
    """Run the production audit and materializer validator; no stubbed proof."""
    renderer = _renderer()
    source = tmp_path / "source.pdf"
    _pdf(source)
    preview = tmp_path / "review.png"
    facts = render_source_pdf_page(source, 1, renderer, 144, preview,
        expected_source_sha256=_sha(source), expected_renderer_sha256=_sha(renderer))
    render = {key: facts[key] for key in ("recipe", "dpi", "renderer_sha256", "pixels", "bytes", "sha256")}
    asset = {
        "origin": ORIGIN, "source_page": 1, "source_sha256": _sha(source),
        "logical_name": "page.png", "placement": "full_page", "render": render,
        "source_visual_review": {"visual_reviewed": True, "rationale": "reviewed source raster"},
    }
    decision = {
        "schema": "kb_creator.mineru_ai_page_decision.v1", "source_page": 1,
        "semantic_role": "reader", "overlay_preference": "original_pipeline_txt",
        "selected_blocks": [], "markdown": "![Source]({{asset:page.png}})",
        "assets": [asset], "unresolved": [], "review": {"visual_reviewed": True, "notes": "reviewed"},
    }
    views = {name: {"blocks": []} for name in (
        "original_pipeline_txt", "original_pipeline_ocr", "raster_pipeline_ocr")}
    packets = {1: {"source_page": 1, "semantic_role": "reader", "views": views}}
    context = {"source": source, "renderer": renderer, "source_sha256": _sha(source),
               "renderer_sha256": _sha(renderer)}
    allowlist = {"schema": "kb_creator.ai_merge_fidelity_reviewed_allowlist.v3",
                 "authority": {}, "substitutions": [], "source_text_exclusions": [],
                 "visual_text_assertions": [], "ocr_equivalence_classes": []}
    audit = audit_v3_content(packets, {1: decision}, allowlist=allowlist, geometry={},
                             visual_inventory={}, source_render_context=context)
    assert audit["passed"] is True
    context["proofs"] = {1: audit["pages"][0]["source_page_renders"]}
    _, assets, _ = _validate_decision(decision, packets[1], {"views": {}}, tmp_path / "raw",
                                      set(), context, tmp_path / "stage06")
    assert assets[0]["sha256"] == facts["sha256"]
    context["proofs"] = {1: []}
    with pytest.raises(ValueError, match="Stage05 proof"):
        _validate_decision(decision, packets[1], {"views": {}}, tmp_path / "raw",
                           set(), context, tmp_path / "stage06-mismatch")


def test_descriptor_rejects_resealed_source_identity_drift(tmp_path):
    roots = [tmp_path / name for name in ("bundle", "raw", "decisions")]
    for root in roots:
        root.mkdir()
    paths = {}
    for name in ("input", "evidence", "audit", "source", "renderer", "comparison", "queue"):
        path = tmp_path / f"{name}.bin"
        path.write_bytes(name.encode())
        paths[name] = {"path": str(path), "bytes": path.stat().st_size, "sha256": _sha(path)}
    value = {
        "schema": SCHEMA, "state": "verified_review_draft_candidate",
        "bundle_root": str(roots[0]), "raw_root": str(roots[1]), "decisions_root": str(roots[2]),
        "input": paths["input"], "final_evidence": paths["evidence"], "audit": paths["audit"],
        "source": paths["source"], "renderer": paths["renderer"], "comparison": paths["comparison"],
        "review_queue": paths["queue"], "pages": [{"source_page": 1}], "assets": [],
        "reference_proof_keys": [], "split_structure_proof_keys": [],
    }
    assert verify_descriptor(value)["state"] == "verified_review_draft_candidate"
    Path(paths["source"]["path"]).write_bytes(b"changed")
    with pytest.raises(ReviewDraftMaterializationError, match="source identity drift"):
        verify_descriptor(value)


def _write(path: Path, value) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding="utf-8")
    return path


def _review_route_fixture(tmp_path, monkeypatch, source_issues=None, *, asset_first=False):
    """Archive validation is stubbed at its boundary; Stage05/06 stay real."""
    from types import SimpleNamespace
    from kb_creator.pipeline.identity import canonical_bytes, file_identity, sha256_bytes
    from kb_creator.pipeline.review_draft import finalize_review_draft_evidence
    from kb_creator.pipeline import review_draft_materialization as route
    from kb_creator.pipeline import reconstruction_replay_resume as resume
    from kb_creator.scripts.audit_mineru_ai_merge_fidelity import audit_v3_content
    from kb_creator.scripts import materialize_mineru_ai_merge as materializer

    run, authored = tmp_path / "run", tmp_path / "authored"
    renderer = _renderer(); source = tmp_path / "source.pdf"; _pdf(source)
    run_json = _write(run / "run.json", {"local": {"source_path": str(source), "common_paths": {"pdftoppm": str(renderer)}}, "source": {"sha256": _sha(source)}})
    geometry = _write(run / "outputs/04-visual-merge-bundle/visual/geometry_plan.json", {"renderer": {"sha256": _sha(renderer)}})
    _write(run / "outputs/04-visual-merge-bundle/visual/visual_manifest.json", {})
    preview = tmp_path / "preview.png"
    facts = render_source_pdf_page(source, 1, renderer, 144, preview, expected_source_sha256=_sha(source), expected_renderer_sha256=_sha(renderer))
    render = {key: facts[key] for key in ("recipe", "dpi", "renderer_sha256", "pixels", "bytes", "sha256")}
    asset = {"origin": ORIGIN, "source_page": 1, "source_sha256": _sha(source), "logical_name": "page.png", "placement": "full_page", "render": render, "source_visual_review": {"visual_reviewed": True, "rationale": "fixture"}}
    decision = {"schema": "kb_creator.mineru_ai_page_decision.v1", "source_page": 1, "semantic_role": "reader", "overlay_preference": "original_pipeline_txt", "selected_blocks": [], "markdown": "![Source]({{asset:page.png}})", "assets": [asset], "unresolved": [], "review": {"visual_reviewed": True, "notes": "fixture"}}
    packet = {"source_page": 1, "semantic_role": "reader", "views": {name: {"blocks": []} for name in ("original_pipeline_txt", "original_pipeline_ocr", "raster_pipeline_ocr")}}
    if source_issues:
        # A question must name a selected OCR occurrence, not coincidental image alt text.
        source_issues = json.loads(json.dumps(source_issues))
        text = source_issues[0]["source_excerpt_en"]
        key = {"view": "original_pipeline_txt", "raw_index": 1}
        packet["views"]["original_pipeline_txt"]["blocks"] = [
            {"raw_index": 1, "source_page": 1, "type": "text", "text": text, "bbox": [100, 100, 900, 200], "assets": []}]
        _write(geometry, {"renderer": {"sha256": _sha(renderer)}, "observed_geometry": [
            {"view_id": "original_pipeline_txt", "source_page": 1,
             "media_box_coordinates": [0, 0, 72, 144], "crop_box_coordinates": [0, 0, 72, 144],
             "rotation_degrees": 0, "user_unit": 1, "effective_displayed_size_points": [72, 144]}]})
        decision["selected_blocks"] = [{**key, "purpose": "text"}]
        decision["markdown"] = (decision["markdown"] + "\n\n" + text if asset_first
                                else text + "\n\n" + decision["markdown"])
        for issue in source_issues:
            issue["candidate_span"] = {"binding": "ordered_selected_source_v1", "source_key": key, "source_page": 1}
    packet_path = _write(run / "outputs/04-visual-merge-bundle/merge_packets/pages/page-001.json", packet)
    _write(run / "outputs/04-visual-merge-bundle/merge_packets/merge_index.json", {"by_source_page": [{"source_page": 1, "semantic_role": "reader", "priority_score": 1, "packet": "pages/page-001.json"}]})
    comparison = _write(run / "outputs/03-compare-views/comparison.json", {"views": {}})
    raw = run / "outputs/02-mineru-three-view"; raw.mkdir(parents=True)
    queue = _write(run / "review/review_queue.json", {"items": [{"source_page": 1, "merge_packet": {"path": "merge_packets/pages/page-001.json", **file_identity(packet_path)}}]})
    page = _write(authored / "pages/page-001.json", decision)
    allowlist = _write(authored / "reviewed_allowlist.v3.json", {"schema": "kb_creator.ai_merge_fidelity_reviewed_allowlist.v3", "authority": {}, "substitutions": [], "source_text_exclusions": [], "visual_text_assertions": [], "ocr_equivalence_classes": []})
    context = {"source": source, "renderer": renderer, "source_sha256": _sha(source), "renderer_sha256": _sha(renderer)}
    audit_value = audit_v3_content({1: packet}, {1: decision}, allowlist=json.loads(allowlist.read_text()), geometry=json.loads(geometry.read_text()), visual_inventory={}, source_render_context=context)
    audit = _write(authored / "review-draft-stage05-audit.json", audit_value)
    decision_set = _write(authored / "decision_set.json", {"decisions": [{"source_page": 1, "path": "pages/page-001.json", **file_identity(page)}]})
    binding_paths = {}
    for name in ("candidate_manifest", "prepared_staging", "input_00", "source_dispositions"):
        binding_paths[name] = _write(tmp_path / (name + ".json"), {"name": name})
    bindings = {name: {"path": path.relative_to(tmp_path).as_posix(), **file_identity(path)} for name, path in binding_paths.items()}
    input_value = {"schema": "kb_creator.review_draft_input.v1", "bindings": bindings, "source_issues": {"schema": "kb_creator.review_draft_source_issues.v1", "issues": source_issues or []}, "unresolved_dispositions": []}
    input_value["input_sha256"] = sha256_bytes(canonical_bytes(input_value))
    input_path = _write(tmp_path / "review-input.json", input_value)
    evidence_value = finalize_review_draft_evidence(input_value, authored={"decision_set": {"path": "decision_set.json", **file_identity(decision_set)}, "reviewed_allowlist": {"path": "reviewed_allowlist.v3.json", **file_identity(allowlist)}, "stage05_audit": {"path": "review-draft-stage05-audit.json", **file_identity(audit)}}, audit=audit_value, visual_reviewed_false_pages=[])
    evidence = _write(authored / "review-draft-evidence.json", evidence_value)
    archive = {"target": {"bridge_sha256": "A" * 64}, "checked_paths": {"stage_02_root": str(raw), "comparison": str(comparison), "merge_packets": str(packet_path.parent.parent), "visual_manifest": str(run / "outputs/04-visual-merge-bundle/visual/visual_manifest.json"), "geometry_plan": str(geometry), "review_queue": str(queue)}}
    monkeypatch.setattr(route, "build_archive_consumption_context", lambda **unused: archive)
    monkeypatch.setattr(resume, "validate_replay_review_queue", lambda unused: SimpleNamespace(queue=json.loads(queue.read_text()), queue_path=queue))
    return route, materializer, run, authored, input_path, evidence, decision_set, audit, binding_paths


def test_review_route_verifies_then_materializes_real_stage05_stage06(tmp_path, monkeypatch):
    route, materializer, run, authored, input_path, evidence, *_ = _review_route_fixture(tmp_path, monkeypatch)
    descriptor = route.verify_final_review_draft(run_root=run, authored_root=authored, input_path=input_path, evidence_path=evidence)
    output = tmp_path / "materialized"
    result = materializer.materialize(Path(descriptor["bundle_root"]), Path(descriptor["raw_root"]), Path(descriptor["decisions_root"]), output, review_draft_authority=descriptor)
    assert result["status"] == "verified_review_draft_candidate"
    assert (output / "REVIEW_DRAFT_MATERIALIZATION.v1.json").is_file()


def test_materializer_verifies_once_per_operation_and_rechecks_later_call(tmp_path, monkeypatch):
    route, materializer, run, authored, input_path, evidence, _, audit, _ = _review_route_fixture(tmp_path, monkeypatch)
    original = route.verify_final_review_draft
    descriptor = original(run_root=run, authored_root=authored, input_path=input_path, evidence_path=evidence)
    calls = []

    def counted(**kwargs):
        calls.append(kwargs)
        return original(**kwargs)

    monkeypatch.setattr(route, "verify_final_review_draft", counted)
    for index in range(2):
        materializer.materialize(Path(descriptor["bundle_root"]), Path(descriptor["raw_root"]),
                                 Path(descriptor["decisions_root"]), tmp_path / f"result-{index}",
                                 review_draft_authority=descriptor)
        assert len(calls) == index + 1
    audit.write_text("{}", encoding="utf-8")
    with pytest.raises(ValueError):
        materializer.materialize(Path(descriptor["bundle_root"]), Path(descriptor["raw_root"]),
                                 Path(descriptor["decisions_root"]), tmp_path / "changed-authority",
                                 review_draft_authority=descriptor)
    # Descriptor identity validation rejects drift before another full audit.
    assert len(calls) == 2
    assert not (tmp_path / "changed-authority").exists()


def test_review_route_rejects_half_recorded_final_candidate_coverage_bridge(tmp_path, monkeypatch):
    """A coverage-aware author cannot degrade to the legacy no-coverage route."""
    from kb_creator.pipeline.review_draft import finalize_review_draft_evidence

    route, _, run, authored, input_path, _, decision_set, audit, _ = _review_route_fixture(tmp_path, monkeypatch)
    candidate = _write(authored / "candidate-manifest.json", {"placeholder": True})
    allowlist = authored / "reviewed_allowlist.v3.json"
    evidence = _write(tmp_path / "coverage-bridge-evidence.json", finalize_review_draft_evidence(
        json.loads(input_path.read_text(encoding="utf-8")),
        authored={
            "decision_set": {"path": "decision_set.json", **file_identity(decision_set)},
            "reviewed_allowlist": {"path": "reviewed_allowlist.v3.json", **file_identity(allowlist)},
            "stage05_audit": {"path": "review-draft-stage05-audit.json", **file_identity(audit)},
            "final_candidate": {"path": "candidate-manifest.json", **file_identity(candidate)},
        },
        audit=json.loads(audit.read_text(encoding="utf-8")), visual_reviewed_false_pages=[],
    ))
    with pytest.raises(ReviewDraftMaterializationError, match="coverage bridge is incomplete"):
        route.verify_final_review_draft(run_root=run, authored_root=authored,
                                        input_path=input_path, evidence_path=evidence)


def test_review_route_rederives_final_candidate_coverage_before_real_stage05_audit(tmp_path, monkeypatch):
    """A sealed bridge must contribute a live source-to-reader claim to Stage05."""
    from kb_creator.pipeline.identity import canonical_bytes, sha256_bytes
    from kb_creator.pipeline.review_draft import finalize_review_draft_evidence
    from kb_creator.pipeline.reviewed_draft_staging import recompute_coverage_factories
    from kb_creator.scripts import author_reviewed_semantic_decisions as author

    route, _, run, authored, _, _, _, _, bindings = _review_route_fixture(tmp_path, monkeypatch)
    source = Path(json.loads((run / "run.json").read_text(encoding="utf-8"))["local"]["source_path"])
    renderer = _renderer()
    run_value = json.loads((run / "run.json").read_text(encoding="utf-8"))
    run_value.update({"schema": "kb_creator.run_spec.v2", "source": {
        "sha256": _sha(source), "bytes": source.stat().st_size, "path_hint": "source.pdf",
    }})
    _write(run / "run.json", run_value)

    packet = {"source_page": 1, "semantic_role": "reader", "views": {
        "original_pipeline_txt": {"blocks": [{"raw_index": 1, "type": "text", "text": "Source text continuation", "bbox": [10, 10, 900, 100]}]},
        "original_pipeline_ocr": {"blocks": [{"raw_index": 2, "type": "text", "text": "continuation", "bbox": [10, 110, 500, 180]}]},
        "raster_pipeline_ocr": {"blocks": []},
    }}
    packet_path = _write(run / "outputs/04-visual-merge-bundle/merge_packets/pages/page-001.json", packet)
    for view in ("original_pipeline_txt", "original_pipeline_ocr"):
        image = run / "outputs/04-visual-merge-bundle/visual" / view / "pages/page-001.png"
        image.parent.mkdir(parents=True, exist_ok=True); image.write_bytes(b"coverage visual " + view.encode())
    visual_manifest = {
        "views": [{"path": "visual/original_pipeline_txt/pages/page-001.png"},
                  {"path": "visual/original_pipeline_ocr/pages/page-001.png"}],
    }
    _write(run / "outputs/04-visual-merge-bundle/visual/visual_manifest.json", visual_manifest)
    geometry = {"renderer": {"sha256": _sha(renderer)}, "observed_geometry": [
        {"view_id": view, "source_page": 1, "media_box_coordinates": [0, 0, 72, 144],
         "crop_box_coordinates": [0, 0, 72, 144], "rotation_degrees": 0,
         "user_unit": 1, "effective_displayed_size_points": [72, 144]}
        for view in ("original_pipeline_txt", "original_pipeline_ocr", "raster_pipeline_ocr")
    ]}
    _write(run / "outputs/04-visual-merge-bundle/visual/geometry_plan.json", geometry)
    decision = {"schema": "kb_creator.mineru_ai_page_decision.v1", "source_page": 1,
        "semantic_role": "reader", "overlay_preference": "original_pipeline_txt",
        "selected_blocks": [{"view": "original_pipeline_txt", "raw_index": 1, "purpose": "text"}],
        "markdown": "Source text continuation", "assets": [], "unresolved": [],
        "review": {"visual_reviewed": True, "notes": "coverage fixture"}}
    page = _write(authored / "pages/page-001.json", decision)
    decision_set = _write(authored / "decision_set.json", {"decisions": [
        {"source_page": 1, "path": "pages/page-001.json", **file_identity(page)}]})

    selectors = _write(tmp_path / "coverage-selectors.json", {"schema": "kb_creator.reader_text_coverage_selectors.v1", "claims": [{
        "claim_id": "continuation-001", "proof_mode": "continuation_subspan",
        "source_key": {"source_page": 1, "view_id": "original_pipeline_ocr", "raw_index": 2},
        "canonical_key": {"source_page": 1, "view_id": "original_pipeline_txt", "raw_index": 1},
        "reader_page": 1, "reader_span": [12, 24], "semantic_container": "complete_selected_block",
        "validated_fact_id": "transcription-001",
    }]})
    source_record = {"path": str(source.resolve()), **file_identity(source)}
    ocr_visual = run / "outputs/04-visual-merge-bundle/visual/original_pipeline_ocr/pages/page-001.png"
    packet_record = {"path": str(packet_path.resolve()), **file_identity(packet_path)}
    transcription = _write(tmp_path / "transcription-review.json", {
        "schema": "kb_creator.reviewed_source_transcription.v1", "approval": "source_image_bound_exact_transcription",
        "reviewer": "fixture", "source_key": {"source_page": 1, "view_id": "original_pipeline_ocr", "raw_index": 2},
        "canonical_key": {"source_page": 1, "view_id": "original_pipeline_txt", "raw_index": 1},
        "source_pdf": source_record, "source_visual": {"path": str(ocr_visual.resolve()), **file_identity(ocr_visual)},
        "packet": packet_record, "exact_text": "continuation", "scope": "fixture",
    })
    coverage_evidence = _write(tmp_path / "coverage-evidence.json", {"schema": "kb_creator.reader_text_coverage_evidence.v1", "facts": [{
        "schema": "kb_creator.source_transcription_fact.v1", "fact_id": "transcription-001",
        "source_key": {"source_page": 1, "view_id": "original_pipeline_ocr", "raw_index": 2},
        "canonical_key": {"source_page": 1, "view_id": "original_pipeline_txt", "raw_index": 1},
        "source_visual": {"path": str(ocr_visual.resolve()), **file_identity(ocr_visual)},
        "evidence_kind": "source_render_exact_transcription",
        "evidence": {"path": "transcription-review.json", **file_identity(transcription)},
        "exact_text": "continuation", "approval": "source_image_bound_exact_transcription",
    }]})

    baseline = tmp_path / "baseline"; baseline_page = _write(baseline / "pages/page-001.json", decision)
    spec = _write(tmp_path / "coverage-spec.json", {"pages": [{"source_page": 1}]})
    candidate = tmp_path / "final-candidate"; candidate_page = _write(candidate / "pages/page-001.json", decision)
    manifest = {"schema": "kb_creator.validated_draft_candidate.v1", "state": "validated_candidate_only",
        "scope": "candidate_only", "acceptance": "pending", "validation": {}, "inputs": {
            "source": run_value["source"], "run": {"path": str((run / "run.json").resolve()), **file_identity(run / "run.json")},
            "review_queue": {"path": "review/review_queue.json", **file_identity(run / "review/review_queue.json")},
            "baseline": {"path": str(baseline.resolve()), "pages": [{"path": "pages/page-001.json", **file_identity(baseline_page)}]},
            "specs": [{"path": str(spec.resolve()), **file_identity(spec)}],
            "code": {"path": str(Path(author.__file__).resolve()), **file_identity(Path(author.__file__))},
        }, "pages": [{"source_page": 1, "path": "pages/page-001.json", **file_identity(candidate_page)}]}
    candidate_manifest = _write(candidate / "candidate_manifest.json", manifest)
    bindings["candidate_manifest"] = _write(tmp_path / "candidate_manifest.json", {"placeholder": True})
    bindings["ledger"] = _write(tmp_path / "ledger.json", {"placeholder": True})
    review_bindings = {
        "candidate_manifest": {"path": "candidate_manifest.json", **file_identity(bindings["candidate_manifest"])},
        "ledger": {"path": "ledger.json", **file_identity(bindings["ledger"])},
        "source_dispositions": {"path": "source_dispositions.json", **file_identity(bindings["source_dispositions"])},
        "reviewed_candidate_manifest": {"path": "final-candidate/candidate_manifest.json", **file_identity(candidate_manifest)},
        "input_00": {"path": "coverage-spec.json", **file_identity(spec)},
    }
    review_input = {"schema": "kb_creator.review_draft_input.v1", "bindings": review_bindings,
                    "source_issues": {"schema": "kb_creator.review_draft_source_issues.v1", "issues": []},
                    "unresolved_dispositions": []}
    review_input["input_sha256"] = sha256_bytes(canonical_bytes(review_input))
    # The sealed bindings are rooted at tmp_path while the input itself is in a
    # separate directory.  A consumer must derive the root from the bridge,
    # never guess input_path.parent.
    input_path = _write(tmp_path / "input-records/coverage-review-input.json", review_input)

    def replay(_run, _baseline, _specs, *, candidate_output):
        generated = Path(candidate_output)
        _write(generated / "pages/page-001.json", decision)
        _write(generated / "candidate_manifest.json", {"pages": [{"source_page": 1, "path": "pages/page-001.json"}], "validation": {}})
        return {}
    monkeypatch.setattr(author, "validate_spec", replay)
    coverage = recompute_coverage_factories(run_root=run, source_pdf=source, drafts_root=candidate, factories=[{
        "factory_id": "continuation", "selectors_path": str(selectors), "evidence_path": str(coverage_evidence)}])
    assert len(coverage["claims"]) == 1
    source_run = tmp_path / "archived-source"; source_run.mkdir()
    checked_paths = {
        "stage_02_root": str(run / "outputs/02-mineru-three-view"),
        "comparison": str(run / "outputs/03-compare-views/comparison.json"),
        "merge_packets": str(run / "outputs/04-visual-merge-bundle/merge_packets"),
        "visual_manifest": str(run / "outputs/04-visual-merge-bundle/visual/visual_manifest.json"),
        "geometry_plan": str(run / "outputs/04-visual-merge-bundle/visual/geometry_plan.json"),
        "review_queue": str(run / "review/review_queue.json"),
    }
    archive_authority = {"schema": "kb_creator.review_draft_archive_consumption.v1", "state": "read_only_consumption",
        "source_run_root": str(source_run.resolve()), "target_run_root": str(run.resolve()), "source_sha256": "A" * 64,
        "source": {"run_identity_sha256": "B" * 64, "bridge_sha256": "C" * 64, "producer_freshness": {"state": "stale"}},
        "target": {"run_identity_sha256": "D" * 64, "bridge_sha256": "E" * 64, "producer_freshness": {"state": "stale"}},
        "checked_paths": checked_paths}
    monkeypatch.setattr(route, "build_archive_consumption_context", lambda **unused: archive_authority)
    staging = _write(authored / "prepared-staging.json", sealed("kb_creator.reviewed_draft_staging.v3", {"state": "prepared_for_audit",
        "bindings": {"finalized_candidate_manifest": {"path": str(candidate_manifest.resolve()), **file_identity(candidate_manifest)}},
        "evidence": {"review_draft_preflight": {"input_sha256": review_input["input_sha256"]},
            "authority": {"archive_authority": archive_authority},
            "coverage_factories": coverage}}, digest_key="manifest_sha256"))
    allowlist = json.loads((authored / "reviewed_allowlist.v3.json").read_text(encoding="utf-8"))
    audit = audit_v3_content({1: packet}, {1: decision}, allowlist=allowlist, geometry=geometry,
        visual_inventory={}, source_render_context={"source": source, "renderer": renderer,
        "source_sha256": _sha(source), "renderer_sha256": _sha(renderer)},
        reader_coverage_claims=[row["claim"] for row in coverage["claims"]])
    assert audit["passed"] is True and audit["reader_coverage_claim_count"] == 1
    audit_path = _write(authored / "review-draft-stage05-audit.json", audit)
    candidate_link = authored / "final-candidate"
    shutil.copytree(candidate, candidate_link)
    manifest_path = candidate_link / "candidate_manifest.json"
    evidence = _write(tmp_path / "coverage-review-evidence.json", finalize_review_draft_evidence(review_input, authored={
        "decision_set": {"path": "decision_set.json", **file_identity(decision_set)},
        "reviewed_allowlist": {"path": "reviewed_allowlist.v3.json", **file_identity(authored / "reviewed_allowlist.v3.json")},
        "stage05_audit": {"path": "review-draft-stage05-audit.json", **file_identity(audit_path)},
        "final_candidate": {"path": "final-candidate/candidate_manifest.json", **file_identity(manifest_path)},
        "prepared_staging": {"path": "prepared-staging.json", **file_identity(staging)},
    }, audit=audit, visual_reviewed_false_pages=[]))
    descriptor = route.verify_final_review_draft(run_root=run, authored_root=authored,
                                                  input_path=input_path, evidence_path=evidence)
    assert descriptor["state"] == "verified_review_draft_candidate"
    selectors.write_text(selectors.read_text(encoding="utf-8") + "\n", encoding="utf-8")
    with pytest.raises(ReviewDraftMaterializationError, match="coverage bridge cannot be rederived"):
        route.verify_final_review_draft(run_root=run, authored_root=authored,
                                        input_path=input_path, evidence_path=evidence)


def test_final_candidate_bridge_requires_real_producer_ledger_binding(tmp_path, monkeypatch):
    """Bridge authority supplies staging; sealed producer input supplies its ledger."""
    from kb_creator.pipeline import review_draft_materialization as route

    route, _, run, authored, input_path, evidence, *_ = _review_route_fixture(tmp_path, monkeypatch)
    value = json.loads(input_path.read_text(encoding="utf-8"))
    value["bindings"]["reviewed_candidate_manifest"] = value["bindings"]["candidate_manifest"]
    from kb_creator.pipeline.identity import canonical_bytes, sha256_bytes
    value["input_sha256"] = sha256_bytes(canonical_bytes(
        {key: item for key, item in value.items() if key != "input_sha256"}))
    input_path.write_text(json.dumps(value), encoding="utf-8")
    bridge = authored / "final-candidate"
    bridge.mkdir(); candidate = bridge / "candidate_manifest.json"; candidate.write_text("{}", encoding="utf-8")
    staging = authored / "prepared-staging"; staging.mkdir(); staging_manifest = staging / "staging-manifest.json"
    staging_manifest.write_text(json.dumps({"bindings": {"finalized_candidate_manifest": {
        "path": str(candidate.resolve()), **file_identity(candidate)}}}), encoding="utf-8")
    evidence_value = json.loads(evidence.read_text(encoding="utf-8"))
    evidence_value["input_sha256"] = value["input_sha256"]
    evidence_value["authored"].update({
        "final_candidate": {"path": "final-candidate/candidate_manifest.json", **file_identity(candidate)},
        "prepared_staging": {"path": "prepared-staging/staging-manifest.json", **file_identity(staging_manifest)},
    })
    evidence_value["evidence_sha256"] = sha256_bytes(canonical_bytes(
        {key: item for key, item in evidence_value.items() if key != "evidence_sha256"}))
    evidence.write_text(json.dumps(evidence_value), encoding="utf-8")
    with pytest.raises(ReviewDraftMaterializationError, match="lacks ledger binding"):
        route.verify_final_review_draft(run_root=run, authored_root=authored,
                                        input_path=input_path, evidence_path=evidence)


@pytest.mark.parametrize("mutation, message", [
    ("corrupt_seal", "manifest_sha256 mismatch"),
    ("target", "do not select the supplied target"),
    ("source", "do not select the supplied target"),
    ("candidate", "not bound to this final candidate"),
])
def test_final_candidate_archive_bridge_rejects_seal_lineage_and_bound_dependency_drift(tmp_path, monkeypatch, mutation, message):
    from types import SimpleNamespace
    from kb_creator.pipeline import review_draft_materialization as route
    from kb_creator.pipeline.identity import canonical_bytes, sha256_bytes

    run, source, other = tmp_path / "run07", tmp_path / "run04", tmp_path / "other"
    for path in (run, source, other): path.mkdir()
    candidate = _write(tmp_path / "candidate_manifest.json", {"candidate": True})
    archive = {"schema": "kb_creator.review_draft_archive_consumption.v1", "state": "read_only_consumption",
        "source_run_root": str(source.resolve()), "target_run_root": str(run.resolve()), "source_sha256": "A" * 64,
        "source": {"run_identity_sha256": "B" * 64, "bridge_sha256": "C" * 64, "producer_freshness": {"state": "stale"}},
        "target": {"run_identity_sha256": "D" * 64, "bridge_sha256": "E" * 64, "producer_freshness": {"state": "stale"}},
        "checked_paths": {key: str(run / key) for key in ("stage_02_root", "comparison", "merge_packets", "visual_manifest", "geometry_plan", "review_queue")}}
    # Match reviewed_draft_staging.stage_reviewed_drafts exactly: its v3
    # manifest is sealed after the producer has assembled the report, and the
    # seal field itself is then appended.  Do not use a fixture-only shape here.
    staging_value = {"schema": "kb_creator.reviewed_draft_staging.v3", "state": "prepared_for_audit",
        "bindings": {"finalized_candidate_manifest": {"path": str(candidate.resolve()), **file_identity(candidate)}},
        "evidence": {"review_draft_preflight": {"input_sha256": "F" * 64},
                     "authority": {"archive_authority": archive}}}
    staging_value["manifest_sha256"] = sha256_bytes(canonical_bytes(staging_value))
    if mutation == "corrupt_seal":
        staging_value["evidence"]["authority"]["archive_authority"]["source_sha256"] = "0" * 64
    elif mutation == "target":
        staging_value["evidence"]["authority"]["archive_authority"]["target_run_root"] = str(other.resolve())
        staging_value["manifest_sha256"] = sha256_bytes(canonical_bytes({key: value for key, value in staging_value.items() if key != "manifest_sha256"}))
    elif mutation == "source":
        staging_value["evidence"]["authority"]["archive_authority"]["source_run_root"] = str(run.resolve())
        staging_value["manifest_sha256"] = sha256_bytes(canonical_bytes({key: value for key, value in staging_value.items() if key != "manifest_sha256"}))
    staging = _write(tmp_path / "staging-manifest.json", staging_value)
    if mutation == "candidate":
        _write(candidate, {"candidate": False})
    authored = lambda name: {"final_candidate": candidate, "prepared_staging": staging}[name]
    with pytest.raises(ReviewDraftMaterializationError, match=message):
        route._archive_context_for_final_candidate(run_root=run,
            review_input=SimpleNamespace(sha256="F" * 64), authored=authored)


def test_authored_relative_path_rejects_symlink_escape(tmp_path):
    from kb_creator.pipeline import review_draft_materialization as route

    root, outside = tmp_path / "root", tmp_path / "outside"
    root.mkdir(); outside.mkdir()
    target = outside / "payload.json"; target.write_text("{}", encoding="utf-8")
    link = root / "escape.json"
    try:
        os.symlink(target, link)
    except OSError as error:
        pytest.skip(f"symlink creation unavailable: {error}")
    with pytest.raises(ReviewDraftMaterializationError, match="escapes its binding root"):
        route._resolved_under(root, "escape.json", "test")


@pytest.mark.parametrize("mutation", ["decision", "audit", "input"])
def test_review_route_rejects_changed_resealed_authority_before_output(tmp_path, monkeypatch, mutation):
    route, materializer, run, authored, input_path, evidence, decision_set, audit, bindings = _review_route_fixture(tmp_path, monkeypatch)
    if mutation == "decision":
        _write(authored / "pages/page-001.json", {"changed": True})
    elif mutation == "audit":
        _write(audit, {"passed": True, "errors": []})
    else:
        _write(bindings["input_00"], {"changed": True})
    with pytest.raises((ValueError, ReviewDraftMaterializationError)):
        route.verify_final_review_draft(run_root=run, authored_root=authored, input_path=input_path, evidence_path=evidence)
    assert not (tmp_path / "materialized").exists()


def test_materializer_recomputes_and_rejects_caller_descriptor_after_audit_drift(tmp_path, monkeypatch):
    route, materializer, run, authored, input_path, evidence, _, audit, _ = _review_route_fixture(tmp_path, monkeypatch)
    descriptor = route.verify_final_review_draft(run_root=run, authored_root=authored, input_path=input_path, evidence_path=evidence)
    # The descriptor still has valid caller-visible file hashes.  The actual
    # bound audit changes afterwards; materialize must rerun verification.
    _write(audit, {"passed": True, "errors": []})
    output = tmp_path / "forged-output"
    with pytest.raises((ValueError, ReviewDraftMaterializationError)):
        materializer.materialize(Path(descriptor["bundle_root"]), Path(descriptor["raw_root"]), Path(descriptor["decisions_root"]), output, review_draft_authority=descriptor)
    assert not output.exists()


def _materialized_review_route(tmp_path, monkeypatch, source_issues=None, *, asset_first=False):
    route, materializer, run, authored, input_path, evidence, *_ = _review_route_fixture(tmp_path, monkeypatch, source_issues, asset_first=asset_first)
    descriptor = route.verify_final_review_draft(run_root=run, authored_root=authored, input_path=input_path, evidence_path=evidence)
    materialized = tmp_path / "materialized"
    materializer.materialize(Path(descriptor["bundle_root"]), Path(descriptor["raw_root"]), Path(descriptor["decisions_root"]), materialized, review_draft_authority=descriptor)
    return materialized, evidence


def test_build_and_verify_review_master_zero_open_issues(tmp_path, monkeypatch):
    materialized, evidence = _materialized_review_route(tmp_path, monkeypatch)
    result = build_review_master_en(materialized, evidence, tmp_path / "master")
    assert result["state"] == "verified_review_draft"
    bindings = json.loads((tmp_path / "master/ISSUE_EN_BINDINGS.v2.json").read_text(encoding="utf-8"))
    assert bindings["bindings"] == []
    assert (tmp_path / "master/MASTER_EN.md").read_bytes() == (materialized / "RECONSTRUCTED_EN.md").read_bytes()


def test_public_review_master_reopener_renders_once_per_call_with_real_consumers(tmp_path, monkeypatch):
    from kb_creator.pipeline import source_page_render as renderer_module

    materialized, evidence = _materialized_review_route(tmp_path, monkeypatch)
    master = tmp_path / "master"
    build_review_master_en(materialized, evidence, master)
    before = deterministic_inventory(master)
    real_run = renderer_module.subprocess.run
    launches = []

    def counted(*args, **kwargs):
        launches.append(args[0])
        return real_run(*args, **kwargs)

    monkeypatch.setattr(renderer_module.subprocess, "run", counted)
    first = verify_master_en(master)
    assert first["state"] == "verified_review_draft" and len(launches) == 1
    second = verify_master_en(master)
    assert second == first and len(launches) == 2
    assert deterministic_inventory(master) == before
    # The fixture supplies a sealed Stage01-04 prefix. This public reopener
    # still executes the real audit, decision checks and materializer.
    copied = master / "REVIEW_DRAFT_MATERIALIZATION.v1.json"
    original = copied.read_bytes()
    copied.write_bytes(original + b" ")
    with pytest.raises(FiveStepIntakeError):
        verify_master_en(master)
    assert len(launches) == 2


@pytest.mark.parametrize("asset_first", [False, True])
def test_build_and_verify_review_master_projects_open_issue_to_unique_visible_span(tmp_path, monkeypatch, asset_first):
    source = tmp_path / "source.pdf"
    # The fixture includes a selected text block and separately rendered source asset.
    issue = {"issue_id": "source-001", "kind": "editorial", "reason": "keep visible", "source_pdf_sha256": "placeholder",
             "source_page": 1, "source_selector": {"block": 1}, "source_excerpt_en": "Source",
             "source_excerpt_sha256": hashlib.sha256(b"Source").hexdigest().upper(), "evidence": [], "candidate_span": {"line": 1}, "state": "open"}
    materialized, evidence = _materialized_review_route(tmp_path, monkeypatch, [issue], asset_first=asset_first)
    result = build_review_master_en(materialized, evidence, tmp_path / "master")
    assert result["state"] == "verified_review_draft"
    bindings = json.loads((tmp_path / "master/ISSUE_EN_BINDINGS.v2.json").read_text(encoding="utf-8"))["bindings"]
    assert bindings[0]["issue_id"] == "source-001"
    span = bindings[0]["master_reader_span"]
    assert span["character_end"] > span["character_start"]
    master_text = (tmp_path / "master/MASTER_EN.md").read_text(encoding="utf-8")
    assert master_text[span["character_start"]:span["character_end"]] == "Source"
    assert verify_master_en(tmp_path / "master")["state"] == "verified_review_draft"


@pytest.mark.parametrize("target", ["page", "asset", "issue", "literal"])
def test_review_master_verifier_rejects_material_drift(tmp_path, monkeypatch, target):
    issue = {"issue_id": "source-001", "kind": "editorial", "reason": "keep visible", "source_pdf_sha256": "placeholder",
             "source_page": 1, "source_selector": {"block": 1}, "source_excerpt_en": "Source",
             "source_excerpt_sha256": hashlib.sha256(b"Source").hexdigest().upper(), "evidence": [], "candidate_span": {"line": 1}, "state": "open"}
    materialized, evidence = _materialized_review_route(tmp_path, monkeypatch, [issue])
    master = tmp_path / "master"; build_review_master_en(materialized, evidence, master)
    if target == "page":
        (master / "MASTER_EN.md").write_text("broken", encoding="utf-8")
    elif target == "asset":
        asset = next((master / "assets").iterdir()); asset.write_bytes(b"broken")
    elif target == "issue":
        value = json.loads((master / "ISSUE_EN_BINDINGS.v2.json").read_text(encoding="utf-8")); value["bindings"][0]["master_reader_span"]["character_start"] += 1
        (master / "ISSUE_EN_BINDINGS.v2.json").write_text(json.dumps(value), encoding="utf-8")
    else:
        value = json.loads((master / "REVIEW_DRAFT_MATERIALIZATION.v1.json").read_text(encoding="utf-8")); value["acceptance"] = "accepted"
        (master / "REVIEW_DRAFT_MATERIALIZATION.v1.json").write_text(json.dumps(value), encoding="utf-8")
    with pytest.raises(FiveStepIntakeError):
        verify_master_en(master)


def test_review_master_builder_rejects_forged_alt_text_without_source_issue(tmp_path, monkeypatch):
    """A clean issue list never authorizes changed visible source prose."""
    materialized, evidence = _materialized_review_route(tmp_path, monkeypatch)
    reconstructed = materialized / "RECONSTRUCTED_EN.md"
    reconstructed.write_text(reconstructed.read_text(encoding="utf-8").replace("Source", "Forged"), encoding="utf-8")
    with pytest.raises(FiveStepIntakeError, match="fresh authority projection"):
        build_review_master_en(materialized, evidence, tmp_path / "master")
    assert not (tmp_path / "master").exists()


@pytest.mark.parametrize("target", ["page", "asset", "sidecar"])
def test_review_master_builder_rejects_coherent_materialization_projection_drift(tmp_path, monkeypatch, target):
    materialized, evidence = _materialized_review_route(tmp_path, monkeypatch)
    if target == "page":
        path = materialized / "pages/page-001.md"
        path.write_text(path.read_text(encoding="utf-8") + "\nforged", encoding="utf-8")
    elif target == "asset":
        next((materialized / "assets").iterdir()).write_bytes(b"forged asset")
    else:
        path = materialized / "MERGE_PROVENANCE.json"
        value = json.loads(path.read_text(encoding="utf-8")); value["forged"] = True
        _write(path, value)
    with pytest.raises(FiveStepIntakeError, match="fresh authority projection"):
        build_review_master_en(materialized, evidence, tmp_path / "master")
    assert not (tmp_path / "master").exists()


def test_review_master_verifier_rejects_resealed_forged_master_against_projection(tmp_path, monkeypatch):
    materialized, evidence = _materialized_review_route(tmp_path, monkeypatch)
    master = tmp_path / "master"; build_review_master_en(materialized, evidence, master)
    for path in (master / "MASTER_EN.md", master / "evidence/reconstruction/RECONSTRUCTED_EN.md"):
        path.write_text(path.read_text(encoding="utf-8").replace("Source", "Forged"), encoding="utf-8")
    pages = [1]
    decisions = sorted((master / "evidence/review").glob("*.json"))
    _write(master / "EN_SOURCE_SPANS.json", _source_spans(master / "MASTER_EN.md", decisions, master))
    _write(master / "ISSUE_EN_BINDINGS.v1.json", _issue_en_bindings(master / "MASTER_EN.md", [], pages, evidence))
    manifest = json.loads((master / "MANIFEST.json").read_text(encoding="utf-8"))
    (master / "INVENTORY.json").unlink()
    (master / "MANIFEST.json").unlink()
    _write(master / "INVENTORY.json", _inventory_value(master))
    manifest.pop("manifest_sha256")
    manifest["master_en"] = {"path": "MASTER_EN.md", **file_identity(master / "MASTER_EN.md")}
    manifest["inventory"] = {"path": "INVENTORY.json", **file_identity(master / "INVENTORY.json")}
    _write(master / "MANIFEST.json", sealed(REVIEW_MASTER_MANIFEST_SCHEMA, manifest, digest_key="manifest_sha256"))
    with pytest.raises(FiveStepIntakeError, match="fresh authority projection"):
        verify_master_en(master)
