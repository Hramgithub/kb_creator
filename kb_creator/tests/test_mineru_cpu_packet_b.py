from __future__ import annotations

import hashlib
import ctypes
from ctypes import wintypes
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import time

import pytest
from jsonschema import validate
from reportlab.pdfgen import canvas

from kb_creator.pipeline import mineru_cpu_first
from kb_creator.pipeline import process as pipeline_process
from kb_creator.pipeline import windows_process_tree
from kb_creator.pipeline.identity import canonical_bytes, deterministic_inventory, file_identity, sha256_bytes
from kb_creator.pipeline.manifests import validate_seal
from kb_creator.pipeline.reconstruction import (
    ControlPlaneError,
    RuntimeOptions,
    StageAdapter,
    RESUME_STAGES,
    RUN_STAGES,
    preflight,
    production_resume_adapters,
    resume_engine,
    run_engine,
)
from kb_creator.scripts.materialize_mineru_ai_merge import materialize
from kb_creator.scripts.audit_mineru_ai_merge_fidelity import audit_v2, write_output as write_audit_output
from kb_creator.scripts.compare_mineru_three_views import compare_view_set
from kb_creator.scripts.build_mineru_visual_merge_bundle import (
    _attach_render_evidence,
    _identity,
    _seal,
    GeometryContractError,
    _write_geometry_failure,
    build_contact_sheets,
    build_geometry_plan,
    build_optional_companions,
    build_packets,
    build_triptychs,
    inventory as visual_inventory,
)
from kb_creator.scripts.prepare_mineru_three_view_inputs import (
    SOURCE_DISPLAYED_MEDIABOX_POLICY,
    prepare_inputs,
)


REPO = Path(__file__).resolve().parents[2]
CONTRACTS = REPO / "kb_creator" / "contracts"


def _lower_identity(path: Path) -> dict[str, object]:
    identity = file_identity(path)
    return {"bytes": identity["bytes"], "sha256": identity["sha256"].lower()}


def _seal_lower(payload: dict[str, object], *, sort_keys: bool = True) -> dict[str, object]:
    encoded = json.dumps(
        payload,
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=sort_keys,
    ).encode("utf-8")
    return {**payload, "receipt_sha256": hashlib.sha256(encoded).hexdigest()}


def _write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _make_source(path: Path, pages: int = 6) -> None:
    document = canvas.Canvas(str(path), pagesize=(500, 700), invariant=1)
    for page in range(1, pages + 1):
        document.drawString(40, 650, f"Synthetic source page {page}")
        document.showPage()
    document.save()


def _write_contract(root: Path, source: Path) -> Path:
    source_identity = file_identity(source)
    contract = {
        "schema": "kb_creator.scenario_reconstruction_contract.v1",
        "contract_revision": 1,
        "scenario": {"id": "synthetic-cpu-first", "title": "Synthetic CPU first"},
        "source": {
            "sha256": source_identity["sha256"],
            "byte_count": source_identity["bytes"],
            "page_count": 6,
            "media_box_points": [500, 700],
            "rotation_degrees": 0,
        },
        "scope": {
            "mode": "all_source_pages",
            "first_page": 1,
            "last_page": 6,
            "required_entities": {"numbered_player_handouts": 0},
        },
        "page_roles": [
            {"role": "cover", "first_page": 1, "last_page": 1, "content_mode": "visual", "traits": [], "strategies": ["visual_preserve"]},
            {"role": "scenario_body", "first_page": 2, "last_page": 4, "content_mode": "text", "traits": ["two_column"], "strategies": ["reading_order"]},
            {"role": "visual_ocr", "first_page": 5, "last_page": 5, "content_mode": "mixed", "traits": [], "strategies": ["visual_preserve", "ocr_region"]},
            {"role": "rules", "first_page": 6, "last_page": 6, "content_mode": "text", "traits": ["statblock"], "strategies": ["reading_order"]},
        ],
        "reconstruction": {
            "strategies": ["reading_order", "visual_preserve", "ocr_region"],
            "required_review": True,
        },
        "acceptance": {"approval_authority": "configured_reconstruction_review"},
    }
    path = root / "contract.json"
    _write_json(path, contract)
    return path


def _write_profile(source_root: Path, mineru_root: Path, provider_id: str) -> dict[str, object]:
    cpu = provider_id == "pipeline_cpu"
    local_profile = "pipeline-cpu-v1" if cpu else "windows-cu128-v1"
    profile = "mineru-pipeline-cpu-windows-v1" if cpu else "mineru-local-windows-cu128-v1"
    profile_root = mineru_root / "profiles" / local_profile
    python = profile_root / ".venv" / "Scripts" / "python.exe"
    mineru = profile_root / ".venv" / "Scripts" / "mineru.exe"
    config = mineru_root / "runtime" / local_profile / "mineru.json"
    lock = source_root / ("requirements.windows-cpu-pipeline.lock.txt" if cpu else "requirements.windows-cu128-provider.lock.txt")
    for path, body in ((python, b"fixture-python"), (mineru, b"fixture-mineru"), (config, b"{}"), (lock, b"mineru==3.4.4\n")):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(body)

    rows = []
    required = 40 if cpu else 55
    for index in range(required):
        family = "pipeline" if index < 40 else "vlm"
        path = source_root / "models" / family / f"model-{index:03d}.bin"
        path.parent.mkdir(parents=True, exist_ok=True)
        if not path.exists():
            path.write_bytes(f"model-{index}".encode("ascii"))
        rows.append({"path": path.relative_to(source_root).as_posix(), **_lower_identity(path)})

    install = _seal_lower(
        {
            "schema": "nri.mineru_profile_installation.v1",
            "profile": profile,
            "source": mineru_cpu_first._source_inventory(source_root / "src"),
            "python": {
                "executable_bytes": python.stat().st_size,
                "executable_sha256": _lower_identity(python)["sha256"],
            },
            "installed_distributions": {"mineru": "3.4.4"},
        }
    )
    install_path = profile_root / "install-receipt.json"
    _write_json(install_path, install)
    verify = _seal_lower(
        {
            "schema": "nri.mineru_profile_verification.v1",
            "profile": profile,
            "state": "ready",
            "install_receipt": {
                **_lower_identity(install_path),
                "receipt_sha256": install["receipt_sha256"],
            },
            "config": _lower_identity(config),
            "lock": {**_lower_identity(lock), "entries": 1},
            "model_manifest": {"required_rows": required, "rows": rows},
        }
    )
    verify_path = profile_root / "verify-receipt.json"
    _write_json(verify_path, verify)
    return {
        "provider_id": provider_id,
        "required": cpu,
        "state": "ready",
        "reason_code": "verified_cpu_profile" if cpu else "verified_cuda_profile",
        "profile": profile,
        "verification_receipt": {
            "path_hint": f"profiles/{local_profile}/verify-receipt.json",
            **_lower_identity(verify_path),
        },
    }


def _runtime_fixture(root: Path, *, gpu_ready: bool = False) -> tuple[RuntimeOptions, Path, Path]:
    source_root = root / "MinerU"
    source_file = source_root / "src" / "mineru_fixture.py"
    source_file.parent.mkdir(parents=True)
    source_file.write_text("VERSION = '3.4.4'\n", encoding="utf-8")
    mineru_root = root / ".tools" / "MinerU"
    cpu = _write_profile(source_root, mineru_root, "pipeline_cpu")
    providers = [cpu]
    if gpu_ready:
        cuda = _write_profile(source_root, mineru_root, "hybrid_cuda")
        providers.extend(
            [
                cuda,
                {**cuda, "provider_id": "vlm_cuda"},
            ]
        )
    else:
        providers.extend(
            [
                {"provider_id": "hybrid_cuda", "required": False, "state": "unavailable", "reason_code": "nvidia_device_not_detected", "profile": "mineru-local-windows-cu128-v1", "verification_receipt": None},
                {"provider_id": "vlm_cuda", "required": False, "state": "unavailable", "reason_code": "nvidia_device_not_detected", "profile": "mineru-local-windows-cu128-v1", "verification_receipt": None},
            ]
        )
    capability = _seal_lower(
        {
            "schema": "nri.mineru_provider_capabilities.v1",
            "checked_at_utc": "2026-09-14T00:00:00Z",
            "execution_boundary": "current_station_local_only",
            "providers": providers,
        },
        sort_keys=False,
    )
    capability_path = mineru_root / "capabilities" / "providers.json"
    _write_json(capability_path, capability)
    powershell = root / "tools" / "pwsh.exe"
    pdftoppm = root / "tools" / "pdftoppm.exe"
    powershell.parent.mkdir(parents=True)
    powershell.write_bytes(b"fixture-powershell")
    pdftoppm.write_bytes(b"fixture-pdftoppm")
    python = mineru_root / "profiles" / "pipeline-cpu-v1" / ".venv" / "Scripts" / "python.exe"
    return (
        RuntimeOptions(
            mineru_root=mineru_root,
            pdftoppm=pdftoppm,
            powershell=powershell,
            python=python,
            provider_capabilities=capability_path,
            mineru_source_root=source_root,
            ocr_language="en",
        ),
        source_root,
        capability_path,
    )


def _write_view_artifacts(root: Path, pages: int = 6) -> None:
    root.mkdir(parents=True)
    rows = [
        {"page_idx": index, "type": "text", "bbox": [10, 10, 490, 60], "text": f"Page {index + 1}"}
        for index in range(pages)
    ]
    _write_json(root / "document_content_list.json", rows)
    _write_json(root / "document_content_list_v2.json", [[] for _ in range(pages)])
    _write_json(root / "document_middle.json", {"pdf_info": [[] for _ in range(pages)]})
    (root / "document.md").write_text("\n".join(f"Page {page}" for page in range(1, pages + 1)) + "\n", encoding="utf-8")
    layout = canvas.Canvas(str(root / "document_layout.pdf"), pagesize=(500, 700), invariant=1)
    for page in range(1, pages + 1):
        layout.drawString(10, 680, f"layout {page}")
        layout.showPage()
    layout.save()


def _run_adapters(run_root: Path) -> dict[str, StageAdapter]:
    def current_run() -> dict[str, object]:
        return json.loads((run_root / "run.json").read_text(encoding="utf-8"))

    def prepare(output: Path) -> dict[str, object]:
        run = current_run()
        prepare_inputs(
            Path(run["local"]["source_path"]), output / "prepared",
            run["source"]["sha256"], "1-6", run["options"]["raster_dpi"],
            "source", raster_only=True, geometry_policy=SOURCE_DISPLAYED_MEDIABOX_POLICY,
        )
        return {"fixture": "prepare", "source_box": "MediaBox", "text_layer": False}

    def execute_views(output: Path) -> dict[str, object]:
        run = current_run()
        output.mkdir(parents=True)
        providers = {row["provider_id"]: row for row in run["capability_snapshot"]["providers"]}
        for descriptor in run["view_plan"]:
            _, input_identity = mineru_cpu_first.view_input_identity(run, descriptor)
            receipt = output / "views" / descriptor["view_id"] / "view.json"
            if providers[descriptor["provider_id"]]["state"] == "unavailable":
                mineru_cpu_first.write_skipped_view(run, descriptor, input_identity, receipt)
            else:
                receipt.parent.mkdir(parents=True)
                artifacts = receipt.parent / "artifacts"
                _write_view_artifacts(artifacts)
                mineru_cpu_first.write_succeeded_view(
                    run,
                    descriptor,
                    input_identity,
                    artifacts,
                    receipt,
                    {"fixture": "local", "exit_code": 0},
                )
        mineru_cpu_first.write_view_set(run, output)
        return {"fixture": "view-set"}

    def compare(output: Path) -> dict[str, object]:
        result = compare_view_set(
            run_root / "outputs" / "01-prepare-inputs" / "prepared" / "sample_pages.json",
            run_root / "outputs" / "02-mineru-three-view" / "view-set.json",
            output,
        )
        return {"fixture": "comparison", "status": result["status"]}

    def bundle(output: Path) -> dict[str, object]:
        run = current_run()
        view_set_path = run_root / "outputs" / "02-mineru-three-view" / "view-set.json"
        comparison_path = run_root / "outputs" / "03-compare-views" / "comparison.json"
        prepared_path = run_root / "outputs" / "01-prepare-inputs" / "prepared" / "sample_pages.json"
        view_set = json.loads(view_set_path.read_text(encoding="utf-8"))
        comparison = json.loads(comparison_path.read_text(encoding="utf-8"))
        roles = ((1, 1, "cover"), (2, 4, "scenario_body"), (5, 5, "visual_ocr"), (6, 6, "rules"))
        views = tuple(view_set["succeeded_views"])
        layouts = {
            view: run_root / "outputs" / "02-mineru-three-view" / "views" / view / "artifacts" / "document_layout.pdf"
            for view in views
        }
        renderer_path = Path(run["local"]["common_paths"]["pdftoppm"])
        renderer = {**_identity(renderer_path), "version": "fixture-pdftoppm 1", "argv_recipe": "pdftoppm-mediabox-png-v1"}
        plan = build_geometry_plan(
            prepared_manifest=json.loads(prepared_path.read_text(encoding="utf-8")),
            prepared_identity=_identity(prepared_path, path_hint="outputs/01-prepare-inputs/prepared/sample_pages.json"),
            layouts=layouts, views=views, dpi=run["options"]["review_dpi"], renderer=renderer,
            run_identity_sha256=run["portable_identity_sha256"],
            source_identity=_identity(Path(run["local"]["source_path"]), path_hint=run["source"]["path_hint"]),
            comparison_identity=_identity(comparison_path, path_hint="outputs/03-compare-views/comparison.json"),
            view_set_identity={**_identity(view_set_path, path_hint="outputs/02-mineru-three-view/view-set.json"), "receipt_sha256": view_set["receipt_sha256"]},
        )
        rendered = {view: [] for view in views}
        targets = {row["source_page"]: row["target_pixels"] for row in plan["targets"]}
        from PIL import Image
        for view in views:
            pages_root = output / "visual" / view / "pages"
            pages_root.mkdir(parents=True, exist_ok=True)
            for page in range(1, 7):
                path = pages_root / f"page-{page:03d}.png"
                Image.new("RGB", tuple(targets[page]), "white").save(path)
                rendered[view].append(path)
        plan = _attach_render_evidence(plan, rendered, output)
        plan_path = output / "visual" / "geometry_plan.json"
        _write_json(plan_path, plan)
        triptychs = build_triptychs(rendered, output / "visual" / "triptychs", mineru_cpu_first.REQUIRED_VIEWS)
        contacts = build_contact_sheets(triptychs, output / "visual" / "contact_sheets")
        companions = build_optional_companions(rendered, output / "visual" / "companions", views[3:])
        build_packets(
            comparison,
            output / "merge_packets",
            6,
            roles,
            tuple(view_set["succeeded_views"]),
            mineru_cpu_first.REQUIRED_VIEWS,
        )
        packet_files = sorted((output / "merge_packets").rglob("*"))
        files = [path for pages in rendered.values() for path in pages] + triptychs + contacts + companions + [path for path in packet_files if path.is_file()] + [plan_path]
        inputs = {
            "raw_receipt": {"path": str(view_set_path.resolve()), "sha256": hashlib.sha256(view_set_path.read_bytes()).hexdigest().upper()},
            "source": {"path": str(Path(run["local"]["source_path"]).resolve()), "sha256": hashlib.sha256(Path(run["local"]["source_path"]).read_bytes()).hexdigest().upper()},
            "comparison": {"path": str(comparison_path.resolve()), "sha256": hashlib.sha256(comparison_path.read_bytes()).hexdigest().upper()},
            "raw_root": str((run_root / "outputs" / "02-mineru-three-view").resolve()),
            "dpi": run["options"]["review_dpi"],
            "preparation_manifest": {"path": str(prepared_path.resolve()), "sha256": hashlib.sha256(prepared_path.read_bytes()).hexdigest().upper()},
            "reconstruction_contract": {"path": str(Path(run["local"]["contract_path"]).resolve()), "sha256": hashlib.sha256(Path(run["local"]["contract_path"]).read_bytes()).hexdigest().upper()},
        }
        manifest = _seal({
            "schema": "kb_creator.mineru_visual_merge_bundle.v2",
            "inputs": inputs,
            "layouts": {view: {"path": str(path), "sha256": hashlib.sha256(path.read_bytes()).hexdigest().upper()} for view, path in layouts.items()},
            "execution": {"commands": [[str(renderer_path), "-r", str(run["options"]["review_dpi"]), "-png", "-f", "1", "-l", "6", str(layouts[view]), str(output / "visual" / view / "pages" / "_render")] for view in views], "pdftoppm_version": "fixture-pdftoppm 1"},
            "counts": {"rendered_pages": 6 * len(views), "triptychs": 6, "contact_sheets": 2, "merge_packets": 6, "optional_companions": 6 * max(0, len(views) - 3)},
            "inventory_scope": "all generated files except the three explicitly listed adapter/self-referential records",
            "inventory_exclusions": ["visual/visual_manifest.json", "evidence/execution.json", "command.json"],
            "files": visual_inventory(output, files),
            "geometry_plan": {"path": "visual/geometry_plan.json", "bytes": plan_path.stat().st_size, "sha256": hashlib.sha256(plan_path.read_bytes()).hexdigest().upper(), "plan_sha256": plan["plan_sha256"]},
        }, "manifest_sha256")
        _write_json(output / "visual" / "visual_manifest.json", manifest)
        return {"fixture": "visual-bundle", "run": run["portable_identity_sha256"]}

    return {
        "prepare_inputs": StageAdapter("prepare_inputs", prepare),
        "mineru_three_view": StageAdapter("mineru_three_view", execute_views),
        "compare_views": StageAdapter("compare_views", compare),
        "visual_merge_bundle": StageAdapter("visual_merge_bundle", bundle),
    }


def _resume_adapters() -> dict[str, StageAdapter]:
    def audit(output: Path) -> dict[str, object]:
        output.mkdir(parents=True)
        _write_json(output / "audit.json", {"passed": True, "provider_neutral": True})
        return {"fixture": "audit"}

    def materialize(output: Path) -> dict[str, object]:
        candidate = output / "candidate"
        candidate.mkdir(parents=True)
        (candidate / "RECONSTRUCTION.md").write_text("synthetic candidate only\n", encoding="utf-8")
        return {"fixture": "materialize"}

    return {
        "fidelity_audit": StageAdapter("fidelity_audit", audit),
        "materialize_candidate": StageAdapter("materialize_candidate", materialize),
    }


def _close_decisions(run_root: Path, destination: Path) -> tuple[Path, Path]:
    queue = json.loads((run_root / "review" / "review_queue.json").read_text(encoding="utf-8"))
    records = []
    for page in range(1, 7):
        relative = f"pages/page-{page:03d}.json"
        path = destination / relative
        _write_json(
            path,
            {
                "schema": "kb_creator.mineru_ai_page_decision.v1",
                "source_page": page,
                "unresolved": [],
                "review": {"visual_reviewed": True},
            },
        )
        records.append({"source_page": page, "path": relative, **file_identity(path)})
    decision_set = destination / "DecisionSet.json"
    _write_json(
        decision_set,
        {
            "schema": "kb_creator.reconstruction_decision_set.v1",
            "review_queue_sha256": queue["queue_sha256"],
            "contract_sha256": queue["contract_sha256"],
            "source_sha256": queue["source_sha256"],
            "decisions": records,
            "reviewed_allowlist": None,
            "submission_state": "submitted_for_validation",
        },
    )
    return decision_set, destination


def _write_materializer_decisions(run_root: Path, destination: Path) -> Path:
    for page in range(1, 7):
        packet = json.loads(
            (
                run_root
                / "outputs"
                / "04-visual-merge-bundle"
                / "merge_packets"
                / "pages"
                / f"page-{page:03d}.json"
            ).read_text(encoding="utf-8")
        )
        _write_json(
            destination / f"page-{page:03d}.json",
            {
                "schema": "kb_creator.mineru_ai_page_decision.v1",
                "source_page": page,
                "semantic_role": packet["semantic_role"],
                "overlay_preference": next(iter(packet["views"])),
                "selected_blocks": [],
                "markdown": f"Synthetic page {page}.",
                "assets": [],
                "unresolved": [],
                "review": {
                    "visual_reviewed": True,
                    "notes": "Synthetic fixture review only.",
                },
            },
        )
    return destination


def _write_complete_v2_audit_submission(run_root: Path, destination: Path) -> tuple[Path, dict[str, object]]:
    queue = json.loads((run_root / "review" / "review_queue.json").read_text(encoding="utf-8"))
    pages = destination / "pages"
    records = []
    for page in range(1, 7):
        packet = json.loads((run_root / "outputs" / "04-visual-merge-bundle" / "merge_packets" / "pages" / f"page-{page:03d}.json").read_text(encoding="utf-8"))
        block = packet["views"]["original_pipeline_txt"]["blocks"][0]
        path = pages / f"page-{page:03d}.json"
        _write_json(path, {
            "schema": "kb_creator.mineru_ai_page_decision.v1", "source_page": page,
            "semantic_role": packet["semantic_role"], "overlay_preference": "original_pipeline_txt",
            "selected_blocks": [{"view": "original_pipeline_txt", "raw_index": block["raw_index"], "purpose": "text"}],
            "markdown": block["text"], "assets": [], "unresolved": [],
            "review": {"visual_reviewed": True, "notes": "Complete synthetic source unit."},
        })
        records.append({"source_page": page, "path": f"pages/page-{page:03d}.json", **file_identity(path)})
    decision_set = {"schema": "kb_creator.reconstruction_decision_set.v1", "review_queue_sha256": queue["queue_sha256"], "contract_sha256": queue["contract_sha256"], "source_sha256": queue["source_sha256"], "decisions": records, "reviewed_allowlist": None, "submission_state": "submitted_for_validation"}
    _write_json(destination / "decision_set.json", decision_set)
    return destination / "decision_set.json", decision_set


def _full_fixture(tmp_path: Path, *, gpu_ready: bool = False):
    source = tmp_path / "source.pdf"
    _make_source(source)
    contract = _write_contract(tmp_path, source)
    runtime, source_root, capability = _runtime_fixture(tmp_path, gpu_ready=gpu_ready)
    run_root = tmp_path / "run"
    return source, contract, runtime, source_root, capability, run_root


def _reseal_stage_output(run_root: Path, ordinal: int, name: str) -> None:
    output = run_root / "outputs" / f"{ordinal:02d}-{name.replace('_', '-')}"
    manifest_path = run_root / "stages" / f"{ordinal:02d}-{name.replace('_', '-')}" / "stage.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    files = deterministic_inventory(output)
    manifest["reproducible"]["outputs"]["files"] = files
    manifest["reproducible"]["outputs"]["inventory_sha256"] = sha256_bytes(canonical_bytes(files))
    manifest["reproducible_sha256"] = sha256_bytes(canonical_bytes(manifest["reproducible"]))
    _write_json(manifest_path, manifest)


def test_cpu_first_absent_gpu_e2e_stops_for_review_then_resumes(tmp_path):
    source, contract, runtime, source_root, capability, run_root = _full_fixture(tmp_path)
    result = run_engine(contract, source, run_root, "cpu-first", _run_adapters(run_root), runtime)
    assert result["state"] == "needs_review" and result["exit_code"] == 10
    run = json.loads((run_root / "run.json").read_text(encoding="utf-8"))
    assert run["schema"] == "kb_creator.run_spec.v2"
    assert run["profile"] == "mineru_cpu_first_three_view_v1"
    assert run["options"]["ocr_language"] == "en"
    assert {key: run["options"][key] for key in (
        "geometry_policy", "geometry_dimension_tolerance_points",
        "geometry_relative_aspect_tolerance", "geometry_pixel_tolerance",
        "geometry_rounding_rule", "geometry_renderer_recipe",
    )} == {
        "geometry_policy": "source_displayed_mediabox_v1",
        "geometry_dimension_tolerance_points": "0.001",
        "geometry_relative_aspect_tolerance": "0.000005",
        "geometry_pixel_tolerance": 0,
        "geometry_rounding_rule": "ceil(points*dpi/72)",
        "geometry_renderer_recipe": "pdftoppm-mediabox-png-v1",
    }
    assert run["view_plan"] == list(mineru_cpu_first.VIEW_PLAN)
    validate(run, json.loads((CONTRACTS / "run_spec.v2.schema.json").read_text(encoding="utf-8")))
    view_set = json.loads((run_root / "outputs" / "02-mineru-three-view" / "view-set.json").read_text(encoding="utf-8"))
    assert view_set["succeeded_views"] == list(mineru_cpu_first.REQUIRED_VIEWS)
    assert [row["state"] for row in view_set["views"]] == ["succeeded"] * 3 + ["skipped"] * 2
    validate(view_set, json.loads((CONTRACTS / "mineru_view_set.v1.schema.json").read_text(encoding="utf-8")))
    for row in view_set["views"][3:]:
        view_root = run_root / "outputs" / "02-mineru-three-view" / "views" / row["view_id"]
        assert [path.name for path in view_root.iterdir()] == ["view.json"]
        validate(
            json.loads((view_root / "view.json").read_text(encoding="utf-8")),
            json.loads((CONTRACTS / "mineru_view_execution.v1.schema.json").read_text(encoding="utf-8")),
        )
    comparison = json.loads((run_root / "outputs" / "03-compare-views" / "comparison.json").read_text(encoding="utf-8"))
    assert comparison["status"] == "pass_for_review"
    validate(comparison, json.loads((CONTRACTS / "mineru_multi_view_comparison.v2.schema.json").read_text(encoding="utf-8")))
    assert len(comparison["pairwise"]) == 3
    assert comparison["skipped_views"] and "parity" not in json.dumps(comparison).lower()
    queue = json.loads((run_root / "review" / "review_queue.json").read_text(encoding="utf-8"))
    assert [row["source_page"] for row in queue["items"]] == list(range(1, 7))
    assert "visual_preserve" in queue["items"][0]["issue_kinds"]
    assert "ocr_region" in queue["items"][4]["issue_kinds"]
    assert "structured_statblock" in queue["items"][5]["issue_kinds"]

    # A newly changed optional-provider probe cannot alter this sealed view set.
    live = json.loads(capability.read_text(encoding="utf-8"))
    live["providers"][1] = _write_profile(source_root, runtime.mineru_root, "hybrid_cuda")
    live = _seal_lower({key: value for key, value in live.items() if key != "receipt_sha256"}, sort_keys=False)
    _write_json(capability, live)
    decision_set, decisions_root = _close_decisions(run_root, tmp_path / "decisions")
    resumed = resume_engine(run_root, decision_set, decisions_root, _resume_adapters())
    assert resumed["state"] == "candidate_ready_for_reconstruction_qa"
    assert resumed["exit_code"] == 0
    assert len(list((run_root / "stages").glob("*/stage.json"))) == len(RUN_STAGES + RESUME_STAGES)


def _call_production_v2_audit(run_root: Path, submission: Path):
    queue_path = run_root / "review" / "review_queue.json"
    comparison_path = run_root / "outputs" / "03-compare-views" / "comparison.json"
    decision_set_path = submission / "decision_set.json"
    return audit_v2(
        submission / "pages",
        run_root / "outputs" / "04-visual-merge-bundle" / "merge_packets",
        queue_path, file_identity(queue_path)["sha256"],
        comparison_path, file_identity(comparison_path)["sha256"],
        decision_set_path, file_identity(decision_set_path)["sha256"],
    )


def test_audit_v2_accepts_canonical_pass_for_review_authority(tmp_path):
    source, contract, runtime, _, _, run_root = _full_fixture(tmp_path)
    assert run_engine(contract, source, run_root, "audit-v2-positive", _run_adapters(run_root), runtime)["exit_code"] == 10
    comparison = json.loads((run_root / "outputs/03-compare-views/comparison.json").read_text(encoding="utf-8"))
    assert comparison["schema"] == "kb_creator.mineru_multi_view_comparison.v2"
    assert comparison["status"] == "pass_for_review" and comparison["failures"] == []
    submission = tmp_path / "validated-submission"
    _write_complete_v2_audit_submission(run_root, submission)
    report = _call_production_v2_audit(run_root, submission)
    assert report["passed"] is True
    validate(report, json.loads((CONTRACTS / "ai_merge_fidelity_audit.v2.schema.json").read_text(encoding="utf-8")))


@pytest.mark.parametrize(
    ("schema", "status", "failures"),
    [
        ("kb_creator.mineru_multi_view_comparison.v2", "pass", []),
        ("kb_creator.mineru_multi_view_comparison.v2", "fail", []),
        ("kb_creator.mineru_multi_view_comparison.v2", "PASS_FOR_REVIEW", []),
        ("kb_creator.mineru_multi_view_comparison.v2", "succeeded", []),
        ("kb_creator.mineru_multi_view_comparison.v2", None, []),
        ("kb_creator.mineru_multi_view_comparison.v2", "pass_for_review", [{"reason": "synthetic failure"}]),
        ("kb_creator.mineru_three_view_comparison.v1", "pass_for_review", []),
        (None, "pass_for_review", []),
    ],
)
def test_audit_v2_rejects_noncanonical_schema_status_or_failures(tmp_path, schema, status, failures):
    source, contract, runtime, _, _, run_root = _full_fixture(tmp_path)
    assert run_engine(contract, source, run_root, "audit-v2-negative", _run_adapters(run_root), runtime)["exit_code"] == 10
    comparison_path = run_root / "outputs/03-compare-views/comparison.json"
    comparison = json.loads(comparison_path.read_text(encoding="utf-8"))
    if schema is None:
        comparison.pop("schema")
    else:
        comparison["schema"] = schema
    if status is None:
        comparison.pop("status")
    else:
        comparison["status"] = status
    comparison["failures"] = failures
    _write_json(comparison_path, comparison)
    _reseal_stage_output(run_root, 3, "compare_views")
    queue_path = run_root / "review/review_queue.json"
    queue = json.loads(queue_path.read_text(encoding="utf-8"))
    queue["comparison"] = {"path": "outputs/03-compare-views/comparison.json", **file_identity(comparison_path)}
    queue["queue_sha256"] = sha256_bytes(canonical_bytes({key: value for key, value in queue.items() if key != "queue_sha256"}))
    _write_json(queue_path, queue)
    submission = tmp_path / "validated-submission"
    _write_complete_v2_audit_submission(run_root, submission)
    with pytest.raises((ControlPlaneError, ValueError)):
        _call_production_v2_audit(run_root, submission)
    assert not (run_root / "outputs/05-fidelity-audit").exists()


def test_production_stage05_adapter_reaches_v2_content_ledger(tmp_path, monkeypatch):
    source, contract, runtime, _, _, run_root = _full_fixture(tmp_path)
    assert run_engine(contract, source, run_root, "audit-v2-adapter", _run_adapters(run_root), runtime)["exit_code"] == 10
    submission = tmp_path / "validated-submission"
    decision_set_path, decision_set = _write_complete_v2_audit_submission(run_root, submission)
    run = json.loads((run_root / "run.json").read_text(encoding="utf-8"))
    queue = json.loads((run_root / "review/review_queue.json").read_text(encoding="utf-8"))
    captured = []
    def execute_audit(argv, *, cwd=None, env_updates=None):
        captured.append(list(argv))
        def value(flag): return Path(argv[argv.index(flag) + 1])
        report = audit_v2(value("--decisions-root"), value("--merge-packets-root"), value("--review-queue"), argv[argv.index("--review-queue-sha256") + 1], value("--comparison"), argv[argv.index("--comparison-sha256") + 1], value("--decision-set"), argv[argv.index("--decision-set-sha256") + 1])
        write_audit_output(value("--output"), report)
        return {"exit_code": 0, "synthetic": "production-audit-dispatch"}
    monkeypatch.setattr(pipeline_process, "run", execute_audit)
    output = tmp_path / "stage05"
    production_resume_adapters(run, decision_set, submission, queue=queue)["fidelity_audit"].invoke(output)
    report = json.loads((output / "audit.json").read_text(encoding="utf-8"))
    assert report["passed"] is True
    assert captured[0][captured[0].index("--mode") + 1] == "v2"


def test_v2_materializer_uses_only_sealed_stage03_authority(tmp_path, monkeypatch):
    source, contract, runtime, _, _, run_root = _full_fixture(tmp_path)
    result = run_engine(
        contract,
        source,
        run_root,
        "materializer-authority",
        _run_adapters(run_root),
        runtime,
    )
    assert result["exit_code"] == 10
    run = json.loads((run_root / "run.json").read_text(encoding="utf-8"))
    queue_path = run_root / "review" / "review_queue.json"
    queue = json.loads(queue_path.read_text(encoding="utf-8"))
    comparison = run_root / "outputs" / "03-compare-views" / "comparison.json"
    raw_root = run_root / "outputs" / "02-mineru-three-view"
    bundle_root = run_root / "outputs" / "04-visual-merge-bundle"
    authored_decisions = _write_materializer_decisions(run_root, tmp_path / "merge-decisions")
    snapshot = run_root / "review" / "validated-submission-v1"
    decisions = snapshot / "pages"
    decisions.mkdir(parents=True)
    for source_decision in authored_decisions.glob("*.json"):
        shutil.copyfile(source_decision, decisions / source_decision.name)
    _write_json(snapshot / "decision_set.json", {"synthetic": "materializer authority fixture"})
    assert not (raw_root / "comparison" / "comparison.json").exists()
    audit_path = run_root / "outputs" / "05-fidelity-audit" / "audit.json"
    audit_path.parent.mkdir()
    page_rows = [{"source_page": page, "required_character_count": 1, "covered_character_count": 1, "completeness": 1.0, "selected_recall": 1.0, "selected_precision": 1.0, "ordered_span_mappings": [], "units": [], "substitutions": [], "visual_assertions": [], "unaccounted_unit_count": 0, "errors": [], "passed": True} for page in run["scope"]["ordered_pages"]]
    _write_json(audit_path, {
        "schema": "kb_creator.ai-merge-fidelity-audit/v2",
        "authorities": {
            "run": {"portable_identity_sha256": run["portable_identity_sha256"], "source_sha256": run["source"]["sha256"], "contract_sha256": run["contract"]["sha256"]},
            "review_queue": {"path_hint": "review/review_queue.json", **file_identity(queue_path), "queue_sha256": queue["queue_sha256"]},
            "comparison": {"path_hint": "outputs/03-compare-views/comparison.json", **file_identity(comparison)},
            "decision_set": {"path_hint": "validated-submission/decision_set.json", **file_identity(snapshot / "decision_set.json")},
            "reviewed_allowlist": None,
            "packets": [{"source_page": item["source_page"], "path_hint": f"outputs/04-visual-merge-bundle/merge_packets/pages/page-{item['source_page']:03d}.json", **file_identity(bundle_root / "merge_packets" / "pages" / f"page-{item['source_page']:03d}.json")} for item in queue["items"]],
        },
        "policy": {"source_completeness_threshold": 1.0, "selected_recall_threshold": 0.95, "required_views": ["original_pipeline_txt", "original_pipeline_ocr", "raster_pipeline_ocr"], "normalization": "unicode_nfkc_casefold_alphanumeric_stream_v1", "low_text_exemption": False},
        "pages": page_rows,
        "boundaries": [],
        "errors": [],
        "passed": True,
    })
    audit_args = {"fidelity_audit": audit_path, "fidelity_audit_sha256": file_identity(audit_path)["sha256"]}

    candidate = tmp_path / "candidate"
    outcome = materialize(
        bundle_root,
        raw_root,
        decisions,
        candidate,
        comparison=comparison,
        comparison_sha256=queue["comparison"]["sha256"],
        **audit_args,
    )
    assert outcome["status"] == "candidate_ready_for_reconstruction_qa"
    provenance = json.loads(
        (candidate / "MERGE_PROVENANCE.json").read_text(encoding="utf-8")
    )
    assert provenance["raw_comparison"] == str(comparison.resolve())
    assert provenance["fidelity_audit"]["sha256"] == audit_args["fidelity_audit_sha256"]

    attacks = [
        ({}, "missing-both"),
        ({"comparison": comparison}, "missing-sha"),
        ({"comparison_sha256": queue["comparison"]["sha256"]}, "missing-path"),
        (
            {
                "comparison": comparison,
                "comparison_sha256": "0" * 64,
            },
            "wrong-sha",
        ),
        (
            {
                "comparison": tmp_path / "outside.json",
                "comparison_sha256": queue["comparison"]["sha256"],
            },
            "outside-path",
        ),
    ]
    for kwargs, name in attacks:
        output = tmp_path / f"rejected-{name}"
        with pytest.raises(ValueError):
            materialize(bundle_root, raw_root, decisions, output, **kwargs)
        assert not output.exists()

    original_queue = queue_path.read_bytes()
    changed = json.loads(original_queue.decode("utf-8"))
    changed["comparison"]["path"] = "outputs/02-mineru-three-view/comparison.json"
    changed["queue_sha256"] = sha256_bytes(
        canonical_bytes({key: value for key, value in changed.items() if key != "queue_sha256"})
    )
    _write_json(queue_path, changed)
    with pytest.raises(ValueError):
        materialize(
            bundle_root,
            raw_root,
            decisions,
            tmp_path / "rejected-queue-graph",
            comparison=comparison,
            comparison_sha256=queue["comparison"]["sha256"],
        )
    assert not (tmp_path / "rejected-queue-graph").exists()
    queue_path.write_bytes(original_queue)

    changed = json.loads(original_queue.decode("utf-8"))
    changed["comparison"]["bytes"] += 1
    changed["queue_sha256"] = sha256_bytes(
        canonical_bytes({key: value for key, value in changed.items() if key != "queue_sha256"})
    )
    _write_json(queue_path, changed)
    with pytest.raises(ValueError):
        materialize(
            bundle_root,
            raw_root,
            decisions,
            tmp_path / "rejected-queue-bytes",
            comparison=comparison,
            comparison_sha256=queue["comparison"]["sha256"],
        )
    assert not (tmp_path / "rejected-queue-bytes").exists()
    queue_path.write_bytes(original_queue)

    visual_path = bundle_root / "visual" / "visual_manifest.json"
    stage4_path = run_root / "stages" / "04-visual-merge-bundle" / "stage.json"
    original_visual = visual_path.read_bytes()
    original_stage4 = stage4_path.read_bytes()
    visual = json.loads(original_visual.decode("utf-8"))
    visual["inputs"]["comparison"]["sha256"] = "F" * 64
    visual["manifest_sha256"] = sha256_bytes(
        canonical_bytes(
            {key: value for key, value in visual.items() if key != "manifest_sha256"}
        )
    )
    _write_json(visual_path, visual)
    _reseal_stage_output(run_root, 4, "visual_merge_bundle")
    with pytest.raises(ValueError):
        materialize(
            bundle_root,
            raw_root,
            decisions,
            tmp_path / "rejected-visual-graph",
            comparison=comparison,
            comparison_sha256=queue["comparison"]["sha256"],
        )
    assert not (tmp_path / "rejected-visual-graph").exists()
    visual_path.write_bytes(original_visual)
    stage4_path.write_bytes(original_stage4)

    captured: list[list[str]] = []

    def fake_run(argv, *, cwd=None, env_updates=None):
        captured.append(list(argv))
        target = Path(argv[argv.index("--output-root") + 1])
        target.mkdir(parents=True)
        return {"argv": list(argv), "exit_code": 0}

    monkeypatch.setattr(pipeline_process, "run", fake_run)
    with pytest.raises(ControlPlaneError, match="validated review queue"):
        production_resume_adapters(
            run,
            {"reviewed_allowlist": None},
            snapshot,
        )
    adapters = production_resume_adapters(
        run,
        {"reviewed_allowlist": None},
        snapshot,
        queue=queue,
    )
    adapters["materialize_candidate"].invoke(tmp_path / "adapter-output")
    argv = captured[-1]
    assert argv.count("--comparison") == 1
    assert argv.count("--comparison-sha256") == 1
    assert argv.count("--fidelity-audit") == 1
    assert argv.count("--fidelity-audit-sha256") == 1
    assert argv[argv.index("--comparison") + 1] == str(comparison)
    assert argv[argv.index("--comparison-sha256") + 1] == queue["comparison"]["sha256"]
    assert argv[argv.index("--fidelity-audit") + 1] == str(audit_path)
    assert argv[argv.index("--fidelity-audit-sha256") + 1] == file_identity(audit_path)["sha256"]


def test_gpu_ready_enriches_but_does_not_replace_cpu_triptych(tmp_path):
    source, contract, runtime, _, _, run_root = _full_fixture(tmp_path, gpu_ready=True)
    result = run_engine(contract, source, run_root, "gpu-enriched", _run_adapters(run_root), runtime)
    assert result["exit_code"] == 10
    view_set = json.loads((run_root / "outputs" / "02-mineru-three-view" / "view-set.json").read_text(encoding="utf-8"))
    assert view_set["succeeded_views"] == [row["view_id"] for row in mineru_cpu_first.VIEW_PLAN]
    comparison = json.loads((run_root / "outputs" / "03-compare-views" / "comparison.json").read_text(encoding="utf-8"))
    assert len(comparison["pairwise"]) == 10
    packet = json.loads((run_root / "outputs" / "04-visual-merge-bundle" / "merge_packets" / "pages" / "page-001.json").read_text(encoding="utf-8"))
    assert list(packet["views"])[:3] == list(mineru_cpu_first.REQUIRED_VIEWS)
    assert list(packet["views"])[3:] == ["original_hybrid_high", "original_vlm"]


def test_required_cpu_unavailable_blocks_before_run_root_creation(tmp_path):
    source, contract, runtime, _, capability, run_root = _full_fixture(tmp_path)
    value = json.loads(capability.read_text(encoding="utf-8"))
    value["providers"][0].update(state="invalid", reason_code="cpu_profile_not_verified", verification_receipt=None)
    value = _seal_lower({key: item for key, item in value.items() if key != "receipt_sha256"}, sort_keys=False)
    _write_json(capability, value)
    with pytest.raises(ControlPlaneError, match="required pipeline_cpu provider is not ready"):
        preflight(contract, source, run_root, runtime=runtime)
    assert not run_root.exists()


def test_cpu_first_dispatch_rejects_partial_runtime_arguments_without_writes(tmp_path):
    source, contract, runtime, _, _, run_root = _full_fixture(tmp_path)
    partial = RuntimeOptions(
        mineru_root=runtime.mineru_root,
        pdftoppm=runtime.pdftoppm,
        powershell=runtime.powershell,
        python=runtime.python,
        provider_capabilities=runtime.provider_capabilities,
    )
    with pytest.raises(ControlPlaneError, match="requires provider capabilities"):
        preflight(contract, source, run_root, runtime=partial)
    assert not run_root.exists()


@pytest.mark.parametrize("kind", ["source", "model", "config", "lock", "tool"])
def test_cpu_first_identity_drift_fails_closed_before_resume_outputs(tmp_path, kind):
    source, contract, runtime, source_root, _, run_root = _full_fixture(tmp_path)
    run_engine(contract, source, run_root, f"drift-{kind}", _run_adapters(run_root), runtime)
    decision_set, decisions_root = _close_decisions(run_root, tmp_path / "decisions")
    if kind == "source":
        source.write_bytes(source.read_bytes() + b"changed")
    elif kind == "model":
        next((source_root / "models" / "pipeline").glob("*.bin")).write_bytes(b"changed")
    elif kind == "config":
        (runtime.mineru_root / "runtime" / "pipeline-cpu-v1" / "mineru.json").write_bytes(b"changed")
    elif kind == "lock":
        (source_root / "requirements.windows-cpu-pipeline.lock.txt").write_bytes(b"changed")
    else:
        runtime.pdftoppm.write_bytes(b"changed")
    with pytest.raises(ControlPlaneError, match="stale|mismatch"):
        resume_engine(run_root, decision_set, decisions_root, _resume_adapters())
    assert not (run_root / "outputs" / "05-fidelity-audit").exists()


def test_view_artifact_or_page_drift_and_required_skip_are_rejected(tmp_path):
    source, contract, runtime, _, _, run_root = _full_fixture(tmp_path)
    run_engine(contract, source, run_root, "view-drift", _run_adapters(run_root), runtime)
    run = json.loads((run_root / "run.json").read_text(encoding="utf-8"))
    required = run["view_plan"][0]
    _, input_identity = mineru_cpu_first.view_input_identity(run, required)
    with pytest.raises(mineru_cpu_first.CpuFirstContractError, match="only an unavailable optional"):
        mineru_cpu_first.write_skipped_view(run, required, input_identity, tmp_path / "forbidden" / "view.json")
    layout = run_root / "outputs" / "02-mineru-three-view" / "views" / required["view_id"] / "artifacts" / "document_layout.pdf"
    layout.write_bytes(b"changed")
    decision_set, decisions_root = _close_decisions(run_root, tmp_path / "decisions")
    with pytest.raises(ControlPlaneError, match="output inventory"):
        resume_engine(run_root, decision_set, decisions_root, _resume_adapters())


@pytest.mark.parametrize("stage", ["comparison", "packet"])
def test_resealed_semantic_output_attack_is_rejected_on_resume(tmp_path, stage):
    source, contract, runtime, _, _, run_root = _full_fixture(tmp_path)
    run_engine(contract, source, run_root, f"semantic-{stage}", _run_adapters(run_root), runtime)
    decision_set, decisions_root = _close_decisions(run_root, tmp_path / "decisions")
    if stage == "comparison":
        path = run_root / "outputs" / "03-compare-views" / "comparison.json"
        value = json.loads(path.read_text(encoding="utf-8"))
        value["pairwise"].pop(next(iter(value["pairwise"])))
        _write_json(path, value)
        _reseal_stage_output(run_root, 3, "compare_views")
        expected = "comparison identity/view set mismatch"
    else:
        path = run_root / "outputs" / "04-visual-merge-bundle" / "merge_packets" / "pages" / "page-001.json"
        value = json.loads(path.read_text(encoding="utf-8"))
        value["decision"] = {"selected": "automatic"}
        _write_json(path, value)
        _reseal_stage_output(run_root, 4, "visual_merge_bundle")
        expected = "merge packet has unexpected or missing fields"
    with pytest.raises(ControlPlaneError, match=expected):
        resume_engine(run_root, decision_set, decisions_root, _resume_adapters())
    assert not (run_root / "outputs" / "05-fidelity-audit").exists()


def test_cpu_first_schemas_and_cli_wiring_are_additive_and_closed():
    for name in (
        "run_spec.v2.schema.json",
        "mineru_view_execution.v1.schema.json",
        "mineru_view_set.v1.schema.json",
        "mineru_multi_view_comparison.v2.schema.json",
    ):
        schema = json.loads((CONTRACTS / name).read_text(encoding="utf-8"))
        assert schema["$schema"].endswith("2020-12/schema")
        assert schema["additionalProperties"] is False
    run_schema = json.loads((CONTRACTS / "run_spec.v2.schema.json").read_text(encoding="utf-8"))
    assert run_schema["properties"]["profile"]["const"] == "mineru_cpu_first_three_view_v1"
    assert run_schema["properties"]["execution_boundary"]["const"]["remote_endpoints_allowed"] is False
    assert "auto" not in json.dumps(run_schema).lower()
    source = (REPO / "kb_creator" / "pipeline" / "reconstruction.py").read_text(encoding="utf-8")
    wrapper = (REPO / "kb_creator" / "scripts" / "run_mineru_three_view.ps1").read_text(encoding="utf-8")
    cli = (REPO / "kb_creator" / "__main__.py").read_text(encoding="utf-8")
    production = "\n".join((source, wrapper, cli)).lower()
    assert "dissociation" not in production
    assert "bogdan" not in production
    assert "http-client" not in production
    assert "--provider-capabilities" in cli and "--ocr-language" in cli
    helper = (REPO / "kb_creator" / "pipeline" / "windows_process_tree.py").read_text(encoding="utf-8")
    assert 'environment = $allowedEnvironment' in wrapper
    assert "RedirectStandardOutput" not in wrapper and "ReadToEndAsync" not in wrapper
    assert "PROC_THREAD_ATTRIBUTE_HANDLE_LIST" in helper
    assert "AssignProcessToJobObject" in helper and "TerminateJobObject" in helper
    assert "shell=True" not in helper and "os.system" not in helper
    assert "Stop-Process" not in wrapper and "taskkill" not in wrapper.lower()
    assert "-ActiveTimeoutSeconds 21600" in wrapper and "cleanup_timeout_seconds = 30" in wrapper
    assert 'repo / "kb_creator" / "pipeline" / "windows_process_tree.py"' in source
    assert '"pipeline", "--method", $(if ($Profile -eq "pipeline_txt") { "txt" } else { "ocr" })' in wrapper
    assert '$arguments += @("vlm-engine")' in wrapper
    assert '$arguments += @("vlm-engine", "--method"' not in wrapper
    for forbidden in ("HTTP_PROXY", "HTTPS_PROXY", "ALL_PROXY", "PYTHONPATH", "API_URL", "SERVER_URL"):
        assert f"{forbidden} =" not in wrapper.split("function Invoke-MinerUClosedProcess", 1)[0]


def test_wrapper_dispatch_rejects_cpu_first_only_profiles_in_legacy_mode(tmp_path):
    pwsh = shutil.which("pwsh.exe") or shutil.which("pwsh")
    if pwsh is None:
        pytest.skip("PowerShell 7 is unavailable")
    wrapper = REPO / "kb_creator" / "scripts" / "run_mineru_three_view.ps1"
    common = [
        pwsh,
        "-NoProfile",
        "-File",
        str(wrapper),
        "-InputPath",
        str(tmp_path / "missing.pdf"),
        "-OutputPath",
        str(tmp_path / "output"),
        "-MinerURoot",
        str(tmp_path / "missing-mineru"),
    ]
    for profile in ("pipeline_txt", "vlm_local"):
        result = subprocess.run(
            [*common, "-Profile", profile],
            check=False,
            capture_output=True,
            text=True,
        )
        diagnostic = result.stdout + result.stderr
        assert result.returncode != 0
        assert "requires CPU-first -ToolRoot execution" in diagnostic
    for profile in ("hybrid_high", "pipeline_ocr"):
        result = subprocess.run(
            [*common, "-Profile", profile],
            check=False,
            capture_output=True,
            text=True,
        )
        diagnostic = result.stdout + result.stderr
        assert result.returncode != 0
        assert "requires CPU-first -ToolRoot execution" not in diagnostic


def test_closed_environment_resolves_path_home_inside_runtime(tmp_path):
    runtime = tmp_path / "runtime" / "pipeline-cpu-v1"
    home = runtime / "home"
    roaming = home / "AppData" / "Roaming"
    local = home / "AppData" / "Local"
    for path in (home, roaming, local):
        path.mkdir(parents=True, exist_ok=True)
    environment = {
        key: os.environ[key]
        for key in ("SystemRoot", "WINDIR", "ComSpec", "PATHEXT")
        if key in os.environ
    }
    environment.update(
        {
            "HOME": str(home),
            "USERPROFILE": str(home),
            "APPDATA": str(roaming),
            "LOCALAPPDATA": str(local),
        }
    )
    code = (
        "import json, os; from pathlib import Path; "
        "print(json.dumps({'home': str(Path.home()), 'keys': {k: os.environ.get(k) "
        "for k in ('HOME','USERPROFILE','APPDATA','LOCALAPPDATA','HTTP_PROXY','PYTHONPATH')}}))"
    )
    result = pipeline_process.run(
        [sys.executable, "-c", code],
        env_updates=environment,
        inherit_environment=False,
    )
    observed = json.loads(str(result["stdout"]))
    assert Path(observed["home"]).resolve() == home.resolve()
    assert observed["keys"] == {
        "HOME": str(home),
        "USERPROFILE": str(home),
        "APPDATA": str(roaming),
        "LOCALAPPDATA": str(local),
        "HTTP_PROXY": None,
        "PYTHONPATH": None,
    }


def test_process_failure_preserves_bounded_sanitized_stdout_and_stderr():
    code = "import sys; print('head\\x00' + 'O'*20000); print('err\\x01' + 'E'*20000, file=sys.stderr); raise SystemExit(7)"
    with pytest.raises(pipeline_process.ProcessFailure) as raised:
        pipeline_process.run(
            [sys.executable, "-c", code],
            env_updates={key: os.environ[key] for key in ("SystemRoot", "WINDIR") if key in os.environ},
            inherit_environment=False,
        )
    failure = raised.value
    assert failure.returncode == 7
    assert failure.stdout.startswith("head?") and failure.stderr.startswith("err?")
    assert failure.stdout.endswith("...[truncated]") and failure.stderr.endswith("...[truncated]")
    assert failure.stdout_truncated is True and failure.stderr_truncated is True
    assert "\x00" not in failure.stdout and "\x01" not in failure.stderr


def _pid_is_active(pid: int) -> bool:
    synchronize = 0x00100000
    wait_timeout = 258
    kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
    kernel32.OpenProcess.argtypes = (ctypes.c_uint32, ctypes.c_int, ctypes.c_uint32)
    kernel32.OpenProcess.restype = ctypes.c_void_p
    kernel32.WaitForSingleObject.argtypes = (ctypes.c_void_p, ctypes.c_uint32)
    kernel32.WaitForSingleObject.restype = ctypes.c_uint32
    kernel32.CloseHandle.argtypes = (ctypes.c_void_p,)
    handle = kernel32.OpenProcess(synchronize, False, pid)
    if not handle:
        return False
    try:
        return kernel32.WaitForSingleObject(handle, 0) == wait_timeout
    finally:
        kernel32.CloseHandle(handle)


def _run_tree_helper(
    tmp_path: Path,
    script_text: str,
    arguments: list[str],
    *,
    active_timeout: float = 10,
    cleanup_timeout: float = 3,
) -> tuple[subprocess.CompletedProcess[str], dict[str, object], Path, Path, float]:
    if os.name != "nt":
        pytest.skip("Windows process-tree helper is Windows-only")
    runtime = tmp_path / "runtime"
    runtime.mkdir(parents=True, exist_ok=True)
    script = tmp_path / "hostile & child [literal].py"
    script.write_text(script_text, encoding="utf-8")
    stdout_path = runtime / "stdout.log"
    stderr_path = runtime / "stderr.log"
    spec_path = runtime / "spec.json"
    result_path = runtime / "result.json"
    child_environment = {
        key: os.environ[key]
        for key in ("SystemRoot", "WINDIR", "ComSpec", "PATHEXT")
        if key in os.environ
    }
    child_environment.update(
        {
            "PATH": str(Path(sys.executable).parent),
            "HOME": str(runtime / "home"),
            "USERPROFILE": str(runtime / "home"),
            "TEMP": str(runtime / "tmp"),
            "TMP": str(runtime / "tmp"),
            "PYTHONUTF8": "1",
            "PYTHONIOENCODING": "utf-8:backslashreplace",
        }
    )
    (runtime / "home").mkdir()
    (runtime / "tmp").mkdir()
    _write_json(
        spec_path,
        {
            "schema": "kb_creator.windows_process_tree_spec.v1",
            "executable": str(Path(sys.executable).resolve()),
            "arguments": ["-B", str(script), *arguments],
            "working_directory": str(tmp_path.resolve()),
            "environment": child_environment,
            "stdout_path": str(stdout_path.resolve()),
            "stderr_path": str(stderr_path.resolve()),
            "active_timeout_seconds": active_timeout,
            "cleanup_timeout_seconds": cleanup_timeout,
        },
    )
    helper = REPO / "kb_creator" / "pipeline" / "windows_process_tree.py"
    started = time.monotonic()
    completed = subprocess.run(
        [
            sys.executable,
            "-B",
            str(helper),
            "--spec",
            str(spec_path),
            "--result",
            str(result_path),
            "--runtime-root",
            str(runtime),
        ],
        check=False,
        capture_output=True,
        text=True,
        timeout=15,
    )
    elapsed = time.monotonic() - started
    result = json.loads(result_path.read_text(encoding="utf-8"))
    return completed, result, stdout_path, stderr_path, elapsed


def test_windows_tree_runner_closes_inherited_file_handles_and_only_kills_owned_tree(tmp_path):
    artifact = tmp_path / "artifact & literal.txt"
    grandchild_pid = tmp_path / "grandchild.pid"
    sentinel = subprocess.Popen(
        [sys.executable, "-c", "import time; time.sleep(60)"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    try:
        completed, result, stdout_path, _, elapsed = _run_tree_helper(
            tmp_path,
            """
import pathlib, subprocess, sys
artifact, pid_path = map(pathlib.Path, sys.argv[1:3])
literal = sys.argv[3]
child = subprocess.Popen([sys.executable, '-c', "import sys,time; print('grandchild-held'); sys.stdout.flush(); time.sleep(60)"])
pid_path.write_text(str(child.pid), encoding='ascii')
artifact.write_text(literal, encoding='utf-8')
print('root-finished', flush=True)
""",
            [str(artifact), str(grandchild_pid), "literal;&|%$()"],
        )
        assert completed.returncode == 0 and completed.stderr == ""
        assert elapsed < 10
        assert result["state"] == "completed" and result["exit_code"] == 0
        assert result["cleanup_completed"] is True
        assert artifact.read_text(encoding="utf-8") == "literal;&|%$()"
        output = stdout_path.read_text(encoding="utf-8")
        assert "root-finished" in output
        assert not _pid_is_active(int(grandchild_pid.read_text(encoding="ascii")))
        assert sentinel.poll() is None
    finally:
        sentinel.terminate()
        sentinel.wait(timeout=5)


@pytest.mark.parametrize("_attempt", range(3))
def test_windows_tree_runner_active_timeout_is_distinct_from_cleanup(tmp_path, _attempt):
    owned_pid = tmp_path / "timed-out.pid"
    sentinel = subprocess.Popen(
        [sys.executable, "-c", "import time; time.sleep(60)"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    try:
        completed, result, stdout_path, _, _ = _run_tree_helper(
            tmp_path,
            "import os,pathlib,sys,time; pathlib.Path(sys.argv[1]).write_text(str(os.getpid()), encoding='ascii'); print('before-timeout', flush=True); time.sleep(60)\n",
            [str(owned_pid)],
            active_timeout=2,
        )
        assert completed.returncode == 0
        assert result == {
            "schema": "kb_creator.windows_process_tree_result.v2",
            "state": "active_timeout",
            "exit_code": 124,
            "timed_out": True,
            "cleanup_completed": True,
            "helper_error": None,
        }
        assert "before-timeout" in stdout_path.read_text(encoding="utf-8")
        assert not _pid_is_active(int(owned_pid.read_text(encoding="ascii")))
        assert sentinel.poll() is None
    finally:
        sentinel.terminate()
        sentinel.wait(timeout=5)


def test_windows_tree_runner_preserves_nonzero_large_output_without_shell_parsing(tmp_path):
    literal = "literal;&|<>%$()[]{}"
    completed, result, stdout_path, stderr_path, _ = _run_tree_helper(
        tmp_path,
        "import sys; print(sys.argv[1]); print('O'*20000); print('E'*20000, file=sys.stderr); raise SystemExit(7)\n",
        [literal],
    )
    assert completed.returncode == 0
    assert result["state"] == "completed" and result["exit_code"] == 7
    assert result["cleanup_completed"] is True
    assert stdout_path.read_text(encoding="utf-8").startswith(literal + "\n")
    assert len(stdout_path.read_bytes()) > 20_000 and len(stderr_path.read_bytes()) > 20_000


def test_windows_tree_runner_refuses_log_path_escape_without_starting_child(tmp_path):
    if os.name != "nt":
        pytest.skip("Windows process-tree helper is Windows-only")
    runtime = tmp_path / "runtime"
    runtime.mkdir()
    marker = tmp_path / "started.txt"
    script = tmp_path / "child.py"
    script.write_text(f"from pathlib import Path; Path({str(marker)!r}).write_text('bad')\n", encoding="utf-8")
    spec = runtime / "spec.json"
    result = runtime / "result.json"
    escaped_log = tmp_path / "escaped.log"
    _write_json(
        spec,
        {
            "schema": "kb_creator.windows_process_tree_spec.v1",
            "executable": str(Path(sys.executable).resolve()),
            "arguments": ["-B", str(script)],
            "working_directory": str(tmp_path.resolve()),
            "environment": {"PATH": str(Path(sys.executable).parent)},
            "stdout_path": str(escaped_log),
            "stderr_path": str(runtime / "stderr.log"),
            "active_timeout_seconds": 2,
            "cleanup_timeout_seconds": 1,
        },
    )
    completed = subprocess.run(
        [
            sys.executable, "-B", str(REPO / "kb_creator" / "pipeline" / "windows_process_tree.py"),
            "--spec", str(spec), "--result", str(result), "--runtime-root", str(runtime),
        ],
        check=False,
        capture_output=True,
        text=True,
    )
    assert completed.returncode == 125 and completed.stdout == "" and completed.stderr == ""
    evidence = json.loads(result.read_text(encoding="utf-8"))
    assert evidence["state"] == "helper_error"
    assert "contained by runtime root" in evidence["helper_error"]
    assert not marker.exists() and not escaped_log.exists()


def test_windows_kernel32_abi_is_complete_exact_and_dynamically_bound():
    if os.name != "nt":
        pytest.skip("Windows process-tree helper is Windows-only")
    source = (REPO / "kb_creator" / "pipeline" / "windows_process_tree.py").read_text(encoding="utf-8")
    used = set(re.findall(r"kernel32\.([A-Za-z0-9_]+)\(", source))
    assert used == set(windows_process_tree.KERNEL32_ABI)
    assert windows_process_tree.KERNEL32_ABI["AssignProcessToJobObject"] == (
        (wintypes.HANDLE, wintypes.HANDLE),
        wintypes.BOOL,
    )
    kernel32 = windows_process_tree._load_kernel32()
    for name, (argtypes, restype) in windows_process_tree.KERNEL32_ABI.items():
        function = getattr(kernel32, name)
        assert tuple(function.argtypes) == tuple(argtypes), name
        assert function.restype is restype, name
    assert ctypes.sizeof(wintypes.HANDLE) == ctypes.sizeof(ctypes.c_void_p)
    assert ctypes.sizeof(wintypes.BOOL) == 4


def test_windows_kernel32_loader_fails_closed_on_unsupported_platform(monkeypatch):
    monkeypatch.setattr(windows_process_tree.os, "name", "posix")
    with pytest.raises(windows_process_tree.RunnerError, match="requires Windows"):
        windows_process_tree._load_kernel32()


def _compile_fake_mineru(pwsh: str, source: Path, destination: Path) -> None:
    source.write_text(
        r'''using System;
using System.Linq;
using System.IO;
using System.Text;
public static class FakeMinerU {
  static string BuildLog(string prefix, char fill, string sentinel) {
    var value = new StringBuilder(prefix);
    while ((value.Length % 8192) != 8191) value.Append(fill);
    value.Append("\x1b[31mCSI_SPLIT");
    while ((value.Length % 8192) != 8191) value.Append(fill);
    value.Append("\x1b]8;;https://bad\x07OSC_SPLIT");
    value.Append(new string(fill, 70000));
    value.Append(sentinel);
    return value.ToString();
  }
  public static int Main(string[] args) {
    if (args.Length > 0 && args[0].EndsWith("profile_receipt.py", StringComparison.OrdinalIgnoreCase)) return 0;
    bool failProbes = File.Exists(Path.Combine(Environment.CurrentDirectory, "fail-probes.flag"));
    if (args.SequenceEqual(new[] { "--version" })) { if (failProbes) { Console.Error.Write("version probe failed"); return 11; } Console.WriteLine("mineru 3.4.4"); return 0; }
    if (args.SequenceEqual(new[] { "--help" })) { if (failProbes) { Console.Error.Write("help probe failed"); return 12; } Console.WriteLine("--path --output --backend --method --lang --effort --formula --table --start --end"); return 0; }
    string[] required = { "HOME", "USERPROFILE", "APPDATA", "LOCALAPPDATA", "TEMP", "TMP", "HF_HOME", "MODELSCOPE_CACHE" };
    if (required.Any(name => String.IsNullOrEmpty(Environment.GetEnvironmentVariable(name)))) return 91;
    if (Environment.GetEnvironmentVariable("MINERU_TASK_RESULT_TIMEOUT_SECONDS") != "18000") return 94;
    string[] forbidden = { "HTTP_PROXY", "HTTPS_PROXY", "ALL_PROXY", "PYTHONPATH", "API_URL", "SERVER_URL" };
    if (forbidden.Any(name => !String.IsNullOrEmpty(Environment.GetEnvironmentVariable(name)))) return 92;
    string home = Environment.GetEnvironmentVariable("HOME");
    if (home != Environment.GetEnvironmentVariable("USERPROFILE") ||
        !Environment.GetEnvironmentVariable("APPDATA").StartsWith(home, StringComparison.OrdinalIgnoreCase) ||
        !Environment.GetEnvironmentVariable("LOCALAPPDATA").StartsWith(home, StringComparison.OrdinalIgnoreCase)) return 93;
    int pathIndex = Array.IndexOf(args, "--path");
    if (pathIndex >= 0 && args[pathIndex + 1].IndexOf("fail", StringComparison.OrdinalIgnoreCase) >= 0) {
      Console.Out.Write(BuildLog("\x1b[31mhead\0", 'O', " Привет STDOUT_TERMINAL\x1b[0m"));
      Console.Error.Write(BuildLog("\x1b[31merr\x01", 'E', " Привет STDERR_TERMINAL\x1b[0m"));
      return 7;
    }
    return 0;
  }
}''',
        encoding="utf-8",
    )
    windows_root = Path(os.environ.get("WINDIR", ""))
    compilers = (
        windows_root / "Microsoft.NET" / "Framework64" / "v4.0.30319" / "csc.exe",
        windows_root / "Microsoft.NET" / "Framework" / "v4.0.30319" / "csc.exe",
    )
    compiler = next((path for path in compilers if path.is_file()), None)
    if compiler is None:
        pytest.skip("Windows C# compiler is unavailable for the executable harness")
    subprocess.run(
        [str(compiler), "/nologo", f"/out:{destination}", str(source)],
        check=True,
        capture_output=True,
        text=True,
    )


def _compile_python_forwarder(source: Path, destination: Path) -> None:
    python_literal = str(Path(sys.executable).resolve()).replace("\\", "\\\\").replace('"', '\\"')
    source.write_text(
        r'''using System;
using System.Diagnostics;
using System.Linq;
using System.Text;
public static class PythonForwarder {
  static string Quote(string value) {
    if (value.Length > 0 && value.All(c => !Char.IsWhiteSpace(c) && c != '"')) return value;
    var result = new StringBuilder("\"");
    int slashes = 0;
    foreach (char c in value) {
      if (c == '\\') { slashes++; continue; }
      if (c == '"') { result.Append('\\', slashes * 2 + 1); result.Append(c); slashes = 0; continue; }
      result.Append('\\', slashes); slashes = 0; result.Append(c);
    }
    result.Append('\\', slashes * 2); result.Append('"');
    return result.ToString();
  }
  public static int Main(string[] args) {
    var start = new ProcessStartInfo("''' + python_literal + r'''", String.Join(" ", args.Select(Quote)));
    start.UseShellExecute = false;
    var process = Process.Start(start);
    process.WaitForExit();
    return process.ExitCode;
  }
}''',
        encoding="utf-8",
    )
    windows_root = Path(os.environ.get("WINDIR", ""))
    compilers = (
        windows_root / "Microsoft.NET" / "Framework64" / "v4.0.30319" / "csc.exe",
        windows_root / "Microsoft.NET" / "Framework" / "v4.0.30319" / "csc.exe",
    )
    compiler = next((path for path in compilers if path.is_file()), None)
    if compiler is None:
        pytest.skip("Windows C# compiler is unavailable for the executable harness")
    subprocess.run(
        [str(compiler), "/nologo", f"/out:{destination}", str(source)],
        check=True,
        capture_output=True,
        text=True,
    )


def _wrapper_fixture(tmp_path: Path) -> tuple[str, Path, Path]:
    pwsh = shutil.which("pwsh.exe") or shutil.which("pwsh")
    if pwsh is None:
        pytest.skip("PowerShell 7 is unavailable")
    fixture = tmp_path / "fixture"
    wrapper = fixture / "kb_creator" / "scripts" / "run_mineru_three_view.ps1"
    common = fixture / "MinerU" / "scripts" / "profile-common.ps1"
    wrapper.parent.mkdir(parents=True)
    common.parent.mkdir(parents=True)
    shutil.copy2(REPO / "kb_creator" / "scripts" / wrapper.name, wrapper)
    process_helper = fixture / "kb_creator" / "pipeline" / "windows_process_tree.py"
    process_helper.parent.mkdir(parents=True)
    shutil.copy2(REPO / "kb_creator" / "pipeline" / process_helper.name, process_helper)
    shutil.copy2(REPO / "MinerU" / "scripts" / common.name, common)
    (common.parent / "profile_receipt.py").write_text("# fake helper input\n", encoding="utf-8")
    _write_json(fixture / "MinerU" / "models" / "manifest.json", {})
    tool_root = fixture / ".tools" / "MinerU"
    definition = tool_root / "profiles" / "pipeline-cpu-v1"
    executable = tmp_path / "fake-mineru.exe"
    _compile_fake_mineru(pwsh, tmp_path / "fake-mineru.cs", executable)
    scripts = definition / ".venv" / "Scripts"
    scripts.mkdir(parents=True)
    _compile_python_forwarder(tmp_path / "python-forwarder.cs", scripts / "python.exe")
    shutil.copy2(executable, scripts / "mineru.exe")
    _write_json(tool_root / "runtime" / "pipeline-cpu-v1" / "mineru.json", {})
    _write_json(definition / "verify-receipt.json", {})
    return pwsh, wrapper, tool_root


def test_wrapper_uses_runtime_home_and_retains_bounded_failure_evidence(tmp_path):
    pwsh, wrapper, tool_root = _wrapper_fixture(tmp_path)
    success_input = tmp_path / "source.pdf"
    failure_input = tmp_path / "fail-source.pdf"
    success_input.write_bytes(b"pdf")
    failure_input.write_bytes(b"pdf")
    hostile = os.environ.copy()
    hostile.update(
        {
            "HOME": str(tmp_path / "hostile-home"),
            "USERPROFILE": str(tmp_path / "hostile-profile"),
            "APPDATA": str(tmp_path / "hostile-appdata"),
            "LOCALAPPDATA": str(tmp_path / "hostile-localappdata"),
            "HTTP_PROXY": "http://hostile.invalid",
            "HTTPS_PROXY": "http://hostile.invalid",
            "ALL_PROXY": "http://hostile.invalid",
            "PYTHONPATH": str(tmp_path / "hostile-python"),
            "API_URL": "https://hostile.invalid",
            "SERVER_URL": "https://hostile.invalid",
            "MINERU_TASK_RESULT_TIMEOUT_SECONDS": "7",
        }
    )
    success_output = tmp_path / "success-output"
    base = [
        pwsh, "-NoProfile", "-File", str(wrapper), "-Profile", "pipeline_txt",
        "-ToolRoot", str(tool_root), "-OcrLanguage", "en", "-StartPage", "0", "-EndPage", "0",
    ]
    completed = subprocess.run(
        [*base, "-InputPath", str(success_input), "-OutputPath", str(success_output)],
        check=True,
        capture_output=True,
        text=True,
        env=hostile,
    )
    result = json.loads(completed.stdout)
    environment = result["environment"]
    runtime = (tool_root / "runtime" / "pipeline-cpu-v1").resolve()
    for key in (
        "HOME", "USERPROFILE", "APPDATA", "LOCALAPPDATA", "TEMP", "TMP",
        "HF_HOME", "HUGGINGFACE_HUB_CACHE", "HF_XET_CACHE", "MODELSCOPE_CACHE",
        "PYTHONUSERBASE", "XDG_CACHE_HOME", "MINERU_TOOLS_CONFIG_JSON",
    ):
        assert Path(environment[key]).resolve().is_relative_to(runtime)
    assert environment["HOME"] == environment["USERPROFILE"]
    assert environment["PYTHONNOUSERSITE"] == "1"
    assert environment["MINERU_TASK_RESULT_TIMEOUT_SECONDS"] == "18000"
    assert not (set(environment) & {"HTTP_PROXY", "HTTPS_PROXY", "ALL_PROXY", "PYTHONPATH", "API_URL", "SERVER_URL"})
    assert not (success_output / "failure.json").exists()

    failure_output = tmp_path / "failure-output"
    failed = subprocess.run(
        [*base, "-InputPath", str(failure_input), "-OutputPath", str(failure_output)],
        check=False,
        capture_output=True,
        text=True,
        env=hostile,
    )
    assert failed.returncode != 0
    evidence = json.loads((failure_output / "failure.json").read_text(encoding="utf-8"))
    unsigned = {key: value for key, value in evidence.items() if key != "failure_sha256"}
    assert evidence["failure_sha256"] == hashlib.sha256(
        json.dumps(unsigned, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    ).hexdigest().upper()
    assert evidence["schema"] == "kb_creator.mineru_closed_invocation_failure.v3"
    assert evidence["phase"] == "execute" and evidence["exit_code"] == 7
    assert evidence["stdout"].startswith("head?") and evidence["stderr"].startswith("err?")
    assert "...[middle omitted]" in evidence["stdout"] and "...[middle omitted]" in evidence["stderr"]
    assert evidence["stdout"].endswith("STDOUT_TERMINAL") and evidence["stderr"].endswith("STDERR_TERMINAL")
    assert evidence["stdout_truncated"] is True and evidence["stderr_truncated"] is True
    assert len(evidence["stdout"]) <= 16_384 and len(evidence["stderr"]) <= 16_384
    assert evidence["stdout_total_bytes"] > 65_000 and evidence["stderr_total_bytes"] > 65_000
    for stream, sentinel in (("stdout", "STDOUT_TERMINAL"), ("stderr", "STDERR_TERMINAL")):
        identity = evidence["full_logs"][stream]
        log_path = failure_output / identity["path"]
        log_bytes = log_path.read_bytes()
        assert len(log_bytes) == identity["bytes"] == evidence[f"{stream}_total_bytes"]
        assert hashlib.sha256(log_bytes).hexdigest().upper() == identity["sha256"]
        assert sentinel in log_path.read_text(encoding="utf-8")
        assert "Привет" in log_path.read_text(encoding="utf-8")
        assert "\x00" not in log_path.read_text(encoding="utf-8")
        assert "\x01" not in log_path.read_text(encoding="utf-8")
        assert "\x1b" not in log_path.read_text(encoding="utf-8")
        assert "[31m" not in log_path.read_text(encoding="utf-8")
        assert "8;;https://bad" not in log_path.read_text(encoding="utf-8")
        assert identity["inline_truncated"] is True
    assert evidence["runner"] == {
        "state": "completed",
        "timed_out": False,
        "cleanup_completed": True,
    }
    assert list((tool_root / "runtime" / "pipeline-cpu-v1" / "invocations").iterdir()) == []


def test_wrapper_seals_version_failure_with_unique_logs_when_help_also_fails(tmp_path):
    pwsh, wrapper, tool_root = _wrapper_fixture(tmp_path)
    (wrapper.parents[2] / "fail-probes.flag").write_text("both probes fail\n", encoding="utf-8")
    source = tmp_path / "source.pdf"
    source.write_bytes(b"pdf")
    output = tmp_path / "failure-output"
    completed = subprocess.run(
        [
            pwsh, "-NoProfile", "-File", str(wrapper), "-Profile", "pipeline_txt",
            "-ToolRoot", str(tool_root), "-OcrLanguage", "en", "-StartPage", "0", "-EndPage", "0",
            "-InputPath", str(source), "-OutputPath", str(output),
        ], check=False, capture_output=True, text=True,
    )
    assert completed.returncode != 0
    evidence = json.loads((output / "failure.json").read_text(encoding="utf-8"))
    assert evidence["phase"] == "version" and evidence["exit_code"] == 11
    identities = [evidence["full_logs"][stream] for stream in ("stdout", "stderr")]
    assert all((output / identity["path"]).is_file() for identity in identities)
    assert len({identity["path"] for identity in identities}) == 2
    artifact_names = {path.name for path in (output / "artifacts").glob("failure-*-full.log")}
    assert len(artifact_names) == 4
    assert all("failure-stdout-full.log" != name and "failure-stderr-full.log" != name for name in artifact_names)


def test_v2_process_failure_is_sealed_and_retained_by_quarantine(tmp_path):
    source, contract, runtime, _, _, run_root = _full_fixture(tmp_path)
    adapters = _run_adapters(run_root)

    def fail_view(output: Path) -> dict[str, object]:
        nested = output / "views" / "original_pipeline_txt" / "artifacts"
        nested.mkdir(parents=True)
        _write_json(nested / "failure.json", {"schema": "fixture.wrapper.failure.v1"})
        raise pipeline_process.ProcessFailure(
            ["pwsh.exe", "-Profile", "pipeline_txt"],
            7,
            "bounded stdout",
            "bounded stderr",
            environment={"SystemRoot": "C:\\Windows"},
        )

    adapters["mineru_three_view"] = StageAdapter("mineru_three_view", fail_view)
    with pytest.raises(ControlPlaneError, match="command failed with exit code 7"):
        run_engine(contract, source, run_root, "failure-evidence", adapters, runtime)
    failure_root = run_root / "failures" / "02-mineru-three-view"
    assert (failure_root / "views" / "original_pipeline_txt" / "artifacts" / "failure.json").is_file()
    stage_failure = json.loads((failure_root / "stage-failure.json").read_text(encoding="utf-8"))
    validate_seal(stage_failure, "failure_sha256")
    assert stage_failure["failure_kind"] == "child_process_nonzero"
    assert stage_failure["profile"] == "pipeline_txt"
    assert stage_failure["stdout"] == "bounded stdout"
    assert stage_failure["stderr"] == "bounded stderr"
    assert not (run_root / "outputs" / "02-mineru-three-view").exists()
    assert not (run_root / "stages" / "02-mineru-three-view" / "stage.json").exists()


def test_stage04_geometry_failure_receipt_is_retained_beside_stage_failure(tmp_path):
    source, contract, runtime, _, _, run_root = _full_fixture(tmp_path)
    adapters = _run_adapters(run_root)

    def fail_geometry(output: Path) -> dict[str, object]:
        error = GeometryContractError(
            "synthetic geometry drift",
            matrix=[{"view_id": "raster_pipeline_ocr", "source_page": 1}],
            mismatch={"kind": "displayed_dimension", "view_id": "raster_pipeline_ocr", "source_page": 1},
        )
        _write_geometry_failure(
            output,
            error=error,
            identities={"fixture": "sealed-inputs"},
            renderer={"sha256": file_identity(runtime.pdftoppm)["sha256"]},
            views=mineru_cpu_first.REQUIRED_VIEWS,
            dpi=110,
        )
        raise pipeline_process.ProcessFailure(
            ["python", "build_mineru_visual_merge_bundle.py"], 1,
            "", "layout geometry differs from Stage 01 authority",
        )

    adapters["visual_merge_bundle"] = StageAdapter("visual_merge_bundle", fail_geometry)
    with pytest.raises(ControlPlaneError, match="command failed with exit code 1"):
        run_engine(contract, source, run_root, "geometry-failure", adapters, runtime)
    failure_root = run_root / "failures" / "04-visual-merge-bundle"
    assert {path.name for path in failure_root.iterdir()} == {"geometry-failure.json", "stage-failure.json"}
    geometry = json.loads((failure_root / "geometry-failure.json").read_text(encoding="utf-8"))
    validate_seal(geometry, "failure_sha256")
    assert geometry["outputs_created"] == [] and geometry["first_mismatch"]["kind"] == "displayed_dimension"
