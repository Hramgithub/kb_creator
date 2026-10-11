"""Exact mixed-page authority and legacy compatibility, without OCR dependencies."""
import copy
import json
from pathlib import Path

import pytest
from jsonschema import validate
from reportlab.pdfgen import canvas

from kb_creator.pipeline import reconstruction as recon
from kb_creator.pipeline import reconstruction_promotion as promotion
from kb_creator.pipeline import mineru_cpu_first as cpu
from kb_creator.pipeline import five_step_intake as intake
from kb_creator.pipeline.identity import file_identity
from kb_creator.scripts.prepare_mineru_three_view_inputs import prepare_inputs, SOURCE_DISPLAYED_MEDIABOX_POLICY
from kb_creator.tests.test_mineru_cpu_packet_b import _runtime_fixture

SCHEMAS = Path(__file__).parents[1] / "contracts"
SIZES = [(602.56, 782.72), (603, 783), (600.96, 781.92)]


def mixed_source(tmp_path):
    source = tmp_path / "mixed.pdf"
    document = canvas.Canvas(str(source), invariant=1)
    for number, size in enumerate(SIZES, 1):
        document.setPageSize(size)
        document.drawString(15, 40, f"Page {number}")
        document.showPage()
    document.save()
    return source


def contract_for(source, tmp_path):
    root = tmp_path / "intake"
    intake.prepare_intake(source, root)
    submission = json.loads((root / "intake-submission.template.json").read_text())
    submission["contract"]["scenario"] = {"id": "mixed-pages", "title": "Mixed pages"}
    submission["contract"]["reconstruction"]["strategies"] = ["reading_order"]
    submission["contract"]["page_roles"] = [{"role": "body", "first_page": 1, "last_page": 3, "content_mode": "text", "traits": [], "strategies": ["reading_order"]}]
    path = tmp_path / "submission.json"
    path.write_text(json.dumps(submission))
    contract = intake._validate_submission(root, path)
    target = tmp_path / "contract.json"
    target.write_text(json.dumps(contract))
    return target, contract


def schema(name):
    return json.loads((SCHEMAS / (name + ".schema.json")).read_text())


def test_mixed_intake_runspec_stage01_identity_and_source_mutation(tmp_path):
    source = mixed_source(tmp_path)
    path, contract = contract_for(source, tmp_path)
    validate(contract, schema("scenario_reconstruction_contract.v2"))
    assert contract["contract_revision"] == 2
    runtime, _, _ = _runtime_fixture(tmp_path / "runtime")
    run = recon.build_run_spec(path, source, tmp_path / "run", "mixed", runtime=runtime)
    validate(run, schema("run_spec.v3"))
    assert run["schema"] == cpu.RUN_SCHEMA_V3
    prepared = tmp_path / "stage" / "prepared"
    manifest = prepare_inputs(source, prepared, file_identity(source)["sha256"], "1-3", 72, "source", raster_only=True, geometry_policy=SOURCE_DISPLAYED_MEDIABOX_POLICY)
    validate(manifest, schema("mineru_three_view_inputs.v3"))
    assert "page_size_points" not in manifest["render"]
    assert [r["raster_pdf_page_size_points"] for r in manifest["render"]["page_geometry"]] == [list(size) for size in SIZES]
    cpu.validate_stage_output(run, "prepare_inputs", prepared.parent)
    identity = promotion._source_identity(run, contract)
    validate(identity, schema("reconstruction_source_identity.v2"))
    promotion._validate_source_identity(identity, "mixed-pages")
    assert identity["source"]["page_geometry"] == contract["source"]["page_geometry"]
    changed = copy.deepcopy(run)
    changed["source"]["page_geometry"][1]["media_box_coordinates"][2] += 1
    with pytest.raises(cpu.CpuFirstContractError, match="page 2"):
        cpu.validate_stage_output(changed, "prepare_inputs", prepared.parent)
    source.write_bytes(source.read_bytes() + b"\n%changed")
    with pytest.raises(cpu.CpuFirstContractError, match="identity"):
        cpu.validate_stage_output(run, "prepare_inputs", prepared.parent)


@pytest.mark.parametrize("mutation", ["missing", "duplicate", "reordered", "nan", "extent", "crop", "rotation", "unit", "bool_page", "bool_rotation"])
def test_mixed_authority_rejects_invalid_page_rows(tmp_path, mutation):
    rows = recon._source_pdf_geometry(mixed_source(tmp_path))["page_geometry"]
    if mutation == "missing": rows.pop()
    elif mutation == "duplicate": rows[1] = copy.deepcopy(rows[0])
    elif mutation == "reordered": rows.reverse()
    elif mutation == "nan": rows[1]["media_box_coordinates"][2] = float("nan")
    elif mutation == "extent": rows[1]["media_box_coordinates"][2] = -1
    elif mutation == "crop": rows[1]["crop_box_coordinates"][2] = 999
    elif mutation == "rotation": rows[1]["rotation_degrees"] = 45
    elif mutation == "unit": rows[1]["user_unit"] = 2
    elif mutation == "bool_page": rows[0]["source_page"] = True
    else: rows[0]["rotation_degrees"] = False
    with pytest.raises(recon.ControlPlaneError): recon._validate_page_geometry(rows, 3)


def test_mixed_source_rejects_uniform_contract_and_legacy_runtime(tmp_path):
    source = mixed_source(tmp_path)
    path, contract = contract_for(source, tmp_path)
    with pytest.raises(recon.ControlPlaneError, match="CPU-first"):
        recon.build_run_spec(path, source, tmp_path / "unsupported", "legacy")
    contract["schema"] = recon.CONTRACT_SCHEMA
    contract["contract_revision"] = 1
    contract["source"].pop("page_geometry")
    contract["source"].update(media_box_points=list(SIZES[0]), rotation_degrees=0)
    path.write_text(json.dumps(contract))
    with pytest.raises(recon.ControlPlaneError, match="geometry"):
        recon.preflight(path, source, tmp_path / "bad")


def test_uniform_source_keeps_scalar_legacy_authority(tmp_path):
    source = tmp_path / "uniform.pdf"
    document = canvas.Canvas(str(source), pagesize=(500, 700), invariant=1)
    for _ in range(3): document.showPage()
    document.save()
    assert recon._source_pdf_geometry(source) == {"page_count": 3, "media_box_points": [500, 700], "rotation_degrees": 0}


def test_mixed_source_page_render_preserves_each_page_and_rejects_stale_hashes(tmp_path):
    import math
    from kb_creator.tests.test_source_page_render import _renderer
    from kb_creator.pipeline.source_page_render import render_source_pdf_page
    renderer = _renderer()
    source = mixed_source(tmp_path)
    authority = file_identity(source)["sha256"]
    renderer_sha = file_identity(renderer)["sha256"]
    for page, size in enumerate(SIZES, 1):
        output = tmp_path / f"page-{page}.png"
        row = render_source_pdf_page(source, page, renderer, 72, output, expected_source_sha256=authority, expected_renderer_sha256=renderer_sha)
        assert row["pixels"] == [math.ceil(value) for value in size]
        assert row["sha256"] == file_identity(output)["sha256"]
        for source_hash, renderer_hash in (("0" * 64, renderer_sha), (authority, "0" * 64)):
            rejected = tmp_path / f"rejected-{page}.png"
            with pytest.raises(ValueError, match="authority mismatch"):
                render_source_pdf_page(source, page, renderer, 72, rejected, expected_source_sha256=source_hash, expected_renderer_sha256=renderer_hash)
            assert not rejected.exists()
    assert file_identity(source)["sha256"] == authority


@pytest.mark.parametrize("contract_revision", [2, 3])
def test_mixed_cpu_prefix_passes_production_fidelity_audit(tmp_path, monkeypatch, contract_revision):
    from kb_creator.tests import test_mineru_cpu_packet_b as fixtures
    source = tmp_path / "six-pages.pdf"
    document = canvas.Canvas(str(source), invariant=1)
    sizes = SIZES * 2
    for number, size in enumerate(sizes, 1):
        document.setPageSize(size)
        document.drawString(15, 40, f"Page {number}")
        document.showPage()
    document.save()
    contract_path = fixtures._write_contract(tmp_path, source)
    contract = json.loads(contract_path.read_text(encoding="utf-8"))
    contract["schema"] = recon.CONTRACT_SCHEMA_V3 if contract_revision == 3 else recon.CONTRACT_SCHEMA_V2
    contract["contract_revision"] = contract_revision
    if contract_revision == 3:
        contract["scope"]["required_entities"] = {"handout_label_sets": [
            {"scope_id": "synthetic", "labels": [
                {"label": "A", "occurrences": [{"source_page": 2, "section": "body"}]}
            ]}
        ]}
    contract["source"].pop("media_box_points")
    contract["source"].pop("rotation_degrees")
    contract["source"]["page_geometry"] = recon._source_pdf_geometry(source)["page_geometry"]
    contract_path.write_text(json.dumps(contract), encoding="utf-8")
    original_writer = fixtures._write_view_artifacts
    def matching_layout(root, pages=6):
        original_writer(root, pages)
        layout = canvas.Canvas(str(root / "document_layout.pdf"), invariant=1)
        for page, size in enumerate(sizes, 1):
            layout.setPageSize(size)
            layout.drawString(10, 680, f"layout {page}")
            layout.showPage()
        layout.save()
        for suffix in ("origin", "span"):
            (root / f"document_{suffix}.pdf").write_bytes(source.read_bytes())
    monkeypatch.setattr(fixtures, "_write_view_artifacts", matching_layout)
    runtime, _, _ = fixtures._runtime_fixture(tmp_path / "runtime")
    run_root = tmp_path / "run"
    adapters = fixtures._run_adapters(run_root)
    original_bundle = adapters["visual_merge_bundle"]
    def complete_bundle(output):
        result = original_bundle.invoke(output)
        manifest = json.loads((output / "visual/visual_manifest.json").read_text())
        evidence = output / "evidence/execution.json"
        evidence.parent.mkdir(exist_ok=True)
        evidence.write_text(json.dumps({**manifest["execution"], "output_inventory": manifest["files"]}), encoding="utf-8")
        return result
    adapters["visual_merge_bundle"] = recon.StageAdapter("visual_merge_bundle", complete_bundle)
    result = recon.run_engine(contract_path, source, run_root, "mixed-audit", adapters, runtime)
    assert result["exit_code"] == 10, result
    expected_schema = cpu.RUN_SCHEMA_V4 if contract_revision == 3 else cpu.RUN_SCHEMA_V3
    assert recon.load_run(run_root)["schema"] == expected_schema
    submission = tmp_path / "submission"
    fixtures._write_complete_v2_audit_submission(run_root, submission)
    assert fixtures._call_production_v2_audit(run_root, submission)["passed"] is True
    from kb_creator.pipeline import reconstruction_replay as replay
    destination = tmp_path / "replayed"
    replayed = replay.replay_run_engine(contract_path, source, run_root, destination, "mixed-replayed", "04", runtime)
    assert replayed["state"] == "needs_review"
    replay.validate_replayed_prefix(destination)
    assert recon.load_run(destination)["schema"] == expected_schema
    assert recon.load_run(destination)["source"]["page_geometry"] == contract["source"]["page_geometry"]
    assert not (destination / "outputs/05-fidelity-audit").exists()
