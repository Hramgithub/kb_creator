import hashlib
import json
from pathlib import Path

import pytest
from reportlab.pdfgen import canvas

from kb_creator.__main__ import main
from kb_creator.pipeline import reconstruction as reconstruction_module
from kb_creator.pipeline.identity import canonical_bytes, file_identity, sha256_bytes
from kb_creator.pipeline.reconstruction import (
    ControlPlaneError,
    RESUME_STAGES,
    RUN_STAGES,
    RuntimeOptions,
    StageAdapter,
    _review_issue_kinds,
    preflight,
    production_resume_adapters,
    resume_engine,
    run_engine,
    write_run,
)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def make_source(path: Path, pages: int = 2) -> None:
    document = canvas.Canvas(str(path), pagesize=(500, 700), invariant=1)
    for page in range(1, pages + 1):
        document.drawString(50, 650, f"Source page {page}")
        document.showPage()
    document.save()


def contract(source: Path) -> dict:
    return {
        "schema": "kb_creator.scenario_reconstruction_contract.v1",
        "contract_revision": 1,
        "scenario": {"id": "sample", "title": "Sample"},
        "source": {
            "sha256": sha(source),
            "byte_count": source.stat().st_size,
            "page_count": 2,
            "media_box_points": [500, 700],
            "rotation_degrees": 0,
        },
        "scope": {
            "mode": "all_source_pages",
            "first_page": 1,
            "last_page": 2,
            "required_entities": {"numbered_player_handouts": 0},
        },
        "page_roles": [
            {
                "role": "cover",
                "first_page": 1,
                "last_page": 1,
                "content_mode": "visual",
                "traits": [],
                "strategies": ["visual_preserve"],
            },
            {
                "role": "scenario_body",
                "first_page": 2,
                "last_page": 2,
                "content_mode": "text",
                "traits": [],
                "strategies": ["reading_order"],
            },
        ],
        "reconstruction": {
            "strategies": ["reading_order", "visual_preserve"],
            "required_review": True,
        },
        "acceptance": {
            "approval_authority": "configured_reconstruction_review"
        },
    }


def write_contract(tmp_path: Path, source: Path) -> Path:
    path = tmp_path / "contract.json"
    path.write_text(json.dumps(contract(source)), encoding="utf-8")
    return path


def unavailable_runtime(tmp_path: Path) -> RuntimeOptions:
    mineru_root = tmp_path / ".tools" / "MinerU"
    mineru_root.mkdir(parents=True)
    (mineru_root / "capability.json").write_text(
        json.dumps(
            {
                "schema": "nri.mineru_cuda_capability.v1",
                "capability": "mineru_cuda",
                "state": "unavailable",
                "reason_code": "nvidia_device_not_detected",
                "checked_at_utc": "2026-09-14T00:00:00Z",
                "probe": {
                    "platform": "Win32NT",
                    "nvidia_device_detected": False,
                    "video_controllers": ["Generic display adapter"],
                    "nvidia_smi_path": None,
                    "devices": [],
                },
            }
        ),
        encoding="utf-8",
    )
    return RuntimeOptions(
        mineru_root=mineru_root,
        pdftoppm=tmp_path / "missing-pdftoppm.exe",
        powershell=tmp_path / "missing-pwsh.exe",
        python=tmp_path / "missing-python.exe",
    )


def run_adapters() -> dict[str, StageAdapter]:
    def prepare(output: Path) -> dict:
        prepared = output / "prepared"
        prepared.mkdir(parents=True)
        (prepared / "sample_pages.json").write_text("{}", encoding="utf-8")
        return {"fixture": "prepare"}

    def mineru(output: Path) -> dict:
        for view in ("original_hybrid", "original_pipeline_ocr", "raster_hybrid"):
            root = output / "runs" / view
            root.mkdir(parents=True)
            (root / "layout.pdf").write_bytes(b"fixture")
        (output / "raw_receipt.json").write_text("{}", encoding="utf-8")
        return {"fixture": "mineru"}

    def compare(output: Path) -> dict:
        output.mkdir(parents=True)
        (output / "comparison.json").write_text(
            json.dumps({"status": "pass"}),
            encoding="utf-8",
        )
        return {"fixture": "compare"}

    def bundle(output: Path) -> dict:
        pages = output / "merge_packets" / "pages"
        pages.mkdir(parents=True)
        for page in (1, 2):
            (pages / f"page-{page:03d}.json").write_text(
                json.dumps({"source_page": page}),
                encoding="utf-8",
            )
        return {"fixture": "bundle"}

    return {
        "prepare_inputs": StageAdapter("prepare_inputs", prepare),
        "mineru_three_view": StageAdapter("mineru_three_view", mineru),
        "compare_views": StageAdapter("compare_views", compare),
        "visual_merge_bundle": StageAdapter("visual_merge_bundle", bundle),
    }


def resume_adapters() -> dict[str, StageAdapter]:
    def audit(output: Path) -> dict:
        output.mkdir(parents=True)
        (output / "audit.json").write_text(
            json.dumps({"passed": True}),
            encoding="utf-8",
        )
        return {"fixture": "audit"}

    def materialize(output: Path) -> dict:
        candidate = output / "candidate"
        candidate.mkdir(parents=True)
        (candidate / "RECONSTRUCTION.md").write_text(
            "candidate only\n",
            encoding="utf-8",
        )
        return {"fixture": "materialize"}

    return {
        "fidelity_audit": StageAdapter("fidelity_audit", audit),
        "materialize_candidate": StageAdapter(
            "materialize_candidate",
            materialize,
        ),
    }


def close_decisions(run_root: Path, destination: Path) -> tuple[Path, Path]:
    queue = json.loads(
        (run_root / "review" / "review_queue.json").read_text(encoding="utf-8")
    )
    pages = destination / "pages"
    pages.mkdir(parents=True)
    records = []
    for page in (1, 2):
        relative = f"pages/page-{page:03d}.json"
        path = destination / relative
        path.write_text(
            json.dumps(
                {
                    "schema": "kb_creator.mineru_ai_page_decision.v1",
                    "source_page": page,
                    "unresolved": [],
                    "review": {"visual_reviewed": True},
                }
            ),
            encoding="utf-8",
        )
        records.append(
            {"source_page": page, "path": relative, **file_identity(path)}
        )
    decision_set = destination / "DecisionSet.json"
    decision_set.write_text(
        json.dumps(
            {
                "schema": "kb_creator.reconstruction_decision_set.v1",
                "review_queue_sha256": queue["queue_sha256"],
                "contract_sha256": queue["contract_sha256"],
                "source_sha256": queue["source_sha256"],
                "decisions": records,
                "reviewed_allowlist": None,
                "submission_state": "submitted_for_validation",
            }
        ),
        encoding="utf-8",
    )
    return decision_set, destination


def test_preflight_is_non_mutating_and_downstream_targets_do_not_write(tmp_path):
    source = tmp_path / "source.pdf"
    make_source(source)
    path = write_contract(tmp_path, source)
    root = tmp_path / "run"
    assert preflight(path, source, root)["state"] == "ready"
    assert not root.exists()
    for target in (
        "master_en",
        "master_ru",
        "artview",
        "html",
        "docx",
        "pdf",
        "production",
        "html-to-pdf",
    ):
        with pytest.raises(ControlPlaneError, match="unsupported target"):
            preflight(path, source, root, target)
        assert not root.exists()


def test_no_cuda_preflight_is_non_mutating_explicit_skip(tmp_path):
    source = tmp_path / "source.pdf"
    make_source(source)
    contract_path = write_contract(tmp_path, source)
    run_root = tmp_path / "run"
    result = preflight(
        contract_path,
        source,
        run_root,
        runtime=unavailable_runtime(tmp_path),
    )
    assert result["state"] == "skipped"
    assert result["capability"]["state"] == "unavailable"
    assert result["toolchain"] == []
    assert not run_root.exists()


def test_no_cuda_run_writes_only_identity_bound_skip_evidence(tmp_path):
    source = tmp_path / "source.pdf"
    make_source(source)
    contract_path = write_contract(tmp_path, source)
    run_root = tmp_path / "run"
    called = False

    def forbidden_adapter(_output: Path) -> dict:
        nonlocal called
        called = True
        raise AssertionError("a skipped run must not invoke stage adapters")

    adapters = {
        name: StageAdapter(name, forbidden_adapter) for name in RUN_STAGES
    }
    result = run_engine(
        contract_path,
        source,
        run_root,
        "no-cuda",
        adapters=adapters,
        runtime=unavailable_runtime(tmp_path),
    )
    assert result["state"] == "skipped"
    assert result["exit_code"] == 0
    assert called is False
    assert {path.name for path in run_root.iterdir()} == {"run.json", "skip.json"}
    skip = json.loads((run_root / "skip.json").read_text(encoding="utf-8"))
    assert skip["run_identity_sha256"] == json.loads(
        (run_root / "run.json").read_text(encoding="utf-8")
    )["portable_identity_sha256"]
    assert [row["state"] for row in skip["stages"]] == ["skipped"] * 6
    assert skip["stages"][1]["reason_code"] == "nvidia_device_not_detected"
    assert all(
        row["reason_code"] == "dependency_skipped"
        for row in skip["stages"][2:]
    )
    serialized = json.dumps({"result": result, "skip": skip}).lower()
    assert "candidate_ready" not in serialized
    assert "needs_review" not in serialized
    assert "succeeded" not in serialized


def test_no_cuda_skipped_run_cannot_resume_or_survive_capability_drift(tmp_path):
    source = tmp_path / "source.pdf"
    make_source(source)
    contract_path = write_contract(tmp_path, source)
    runtime = unavailable_runtime(tmp_path)
    run_root = tmp_path / "run"
    run_engine(contract_path, source, run_root, "no-cuda", runtime=runtime)
    with pytest.raises(ControlPlaneError, match="run was skipped"):
        resume_engine(run_root, tmp_path / "decisions.json", tmp_path)

    capability_path = runtime.mineru_root / "capability.json"
    capability = json.loads(capability_path.read_text(encoding="utf-8"))
    capability["checked_at_utc"] = "2026-09-14T01:00:00Z"
    capability_path.write_text(json.dumps(capability), encoding="utf-8")
    with pytest.raises(ControlPlaneError, match="stale MinerU CUDA capability"):
        resume_engine(run_root, tmp_path / "decisions.json", tmp_path)


def test_cli_rejects_downstream_target_before_writing(tmp_path):
    root = tmp_path / "run"
    result = main(
        [
            "run",
            "--contract",
            str(tmp_path / "missing-contract.json"),
            "--source",
            str(tmp_path / "missing-source.pdf"),
            "--run-root",
            str(root),
            "--run-id",
            "test",
            "--target",
            "pdf",
            "--mineru-root",
            str(tmp_path / "mineru"),
            "--pdftoppm",
            str(tmp_path / "pdftoppm.exe"),
            "--powershell",
            str(tmp_path / "pwsh.exe"),
        ]
    )
    assert result == 2
    assert not root.exists()


def test_run_seals_identity_and_rejects_existing_root(tmp_path):
    source = tmp_path / "source.pdf"
    make_source(source)
    path = write_contract(tmp_path, source)
    root = tmp_path / "run"
    result = write_run(path, source, root, "safe-run")
    assert (root / "run.json").is_file()
    assert result["target"] == "reconstructed_en"
    with pytest.raises(ControlPlaneError, match="must be absent"):
        write_run(path, source, root, "safe-run")


def test_synthetic_fixed_graph_run_resume_has_six_verified_stages(tmp_path):
    source = tmp_path / "source.pdf"
    make_source(source)
    contract_path = write_contract(tmp_path, source)
    run_root = tmp_path / "run"
    run_result = run_engine(
        contract_path,
        source,
        run_root,
        "synthetic",
        adapters=run_adapters(),
    )
    assert run_result["state"] == "needs_review"
    assert run_result["exit_code"] == 10
    assert len(list((run_root / "stages").glob("*/stage.json"))) == 4
    decision_set, decisions_root = close_decisions(
        run_root,
        tmp_path / "decisions",
    )
    resume_result = resume_engine(
        run_root,
        decision_set,
        decisions_root,
        adapters=resume_adapters(),
    )
    assert resume_result["state"] == "candidate_ready_for_reconstruction_qa"
    assert "accept" not in json.dumps(resume_result).lower()
    manifests = sorted((run_root / "stages").glob("*/stage.json"))
    assert len(manifests) == 6
    assert [path.parent.name for path in manifests] == [
        f"{index:02d}-{name.replace('_', '-')}"
        for index, name in enumerate(RUN_STAGES + RESUME_STAGES, 1)
    ]
    for path in manifests:
        manifest = json.loads(path.read_text(encoding="utf-8"))
        assert manifest["schema"] == "kb_creator.stage_manifest.v1"
        assert manifest["reproducible"]["state"] == "succeeded"
        assert manifest["reproducible"]["outputs"]["files"]
        assert manifest["reproducible_sha256"] == sha256_bytes(
            canonical_bytes(manifest["reproducible"])
        )
    for ordinal in (5, 6):
        manifest = json.loads(manifests[ordinal - 1].read_text(encoding="utf-8"))
        assert [row["kind"] for row in manifest["reproducible"]["inputs"]] == [
            "reconstruction_decision_set",
            "page_decision",
            "page_decision",
        ]


def test_resume_rejects_stale_stage_output_before_new_writes(tmp_path):
    source = tmp_path / "source.pdf"
    make_source(source)
    contract_path = write_contract(tmp_path, source)
    run_root = tmp_path / "run"
    run_engine(
        contract_path,
        source,
        run_root,
        "synthetic",
        adapters=run_adapters(),
    )
    decision_set, decisions_root = close_decisions(
        run_root,
        tmp_path / "decisions",
    )
    stale = (
        run_root
        / "outputs"
        / "01-prepare-inputs"
        / "prepared"
        / "sample_pages.json"
    )
    stale.write_text('{"changed":true}', encoding="utf-8")
    with pytest.raises(ControlPlaneError, match="output inventory"):
        resume_engine(
            run_root,
            decision_set,
            decisions_root,
            adapters=resume_adapters(),
        )
    assert not (run_root / "outputs" / "05-fidelity-audit").exists()


def test_resume_rejects_stale_queue_and_open_decision(tmp_path):
    source = tmp_path / "source.pdf"
    make_source(source)
    contract_path = write_contract(tmp_path, source)
    run_root = tmp_path / "run"
    run_engine(
        contract_path,
        source,
        run_root,
        "synthetic",
        adapters=run_adapters(),
    )
    decision_set, decisions_root = close_decisions(
        run_root,
        tmp_path / "decisions",
    )
    first = decisions_root / "pages" / "page-001.json"
    decision = json.loads(first.read_text(encoding="utf-8"))
    decision["unresolved"] = ["column-order"]
    first.write_text(json.dumps(decision), encoding="utf-8")
    with pytest.raises(ControlPlaneError, match="identity mismatch"):
        resume_engine(
            run_root,
            decision_set,
            decisions_root,
            adapters=resume_adapters(),
        )

    queue_path = run_root / "review" / "review_queue.json"
    queue = json.loads(queue_path.read_text(encoding="utf-8"))
    queue["items"][0]["state"] = "decided"
    queue_path.write_text(json.dumps(queue), encoding="utf-8")
    with pytest.raises(ControlPlaneError, match="queue_sha256 mismatch"):
        resume_engine(
            run_root,
            decision_set,
            decisions_root,
            adapters=resume_adapters(),
        )


def test_resume_rejects_tampered_local_run_root_before_new_writes(tmp_path):
    source = tmp_path / "source.pdf"
    make_source(source)
    contract_path = write_contract(tmp_path, source)
    run_root = tmp_path / "run"
    run_engine(
        contract_path,
        source,
        run_root,
        "synthetic",
        adapters=run_adapters(),
    )
    decision_set, decisions_root = close_decisions(
        run_root,
        tmp_path / "decisions",
    )
    run_path = run_root / "run.json"
    run = json.loads(run_path.read_text(encoding="utf-8"))
    run["local"]["run_root"] = str(tmp_path / "elsewhere")
    run_path.write_text(json.dumps(run), encoding="utf-8")
    with pytest.raises(ControlPlaneError, match="run root binding mismatch"):
        resume_engine(
            run_root,
            decision_set,
            decisions_root,
            adapters=resume_adapters(),
        )
    assert not (run_root / "outputs" / "05-fidelity-audit").exists()


def test_stage_output_root_escape_is_rejected_even_when_resealed(tmp_path):
    source = tmp_path / "source.pdf"
    make_source(source)
    contract_path = write_contract(tmp_path, source)
    run_root = tmp_path / "run"
    run_engine(
        contract_path,
        source,
        run_root,
        "synthetic",
        adapters=run_adapters(),
    )
    decision_set, decisions_root = close_decisions(
        run_root,
        tmp_path / "decisions",
    )
    manifest_path = run_root / "stages" / "01-prepare-inputs" / "stage.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["reproducible"]["outputs"]["root_hint"] = "../../outside"
    manifest["reproducible_sha256"] = sha256_bytes(
        canonical_bytes(manifest["reproducible"])
    )
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
    with pytest.raises(ControlPlaneError, match="output root mismatch"):
        resume_engine(
            run_root,
            decision_set,
            decisions_root,
            adapters=resume_adapters(),
        )
    assert not (run_root / "outputs" / "05-fidelity-audit").exists()


def test_failed_stage_is_quarantined_without_passing_output(tmp_path):
    source = tmp_path / "source.pdf"
    make_source(source)
    contract_path = write_contract(tmp_path, source)
    run_root = tmp_path / "run"

    def fail_after_partial_write(output: Path) -> dict:
        output.mkdir(parents=True)
        (output / "partial.txt").write_text("partial", encoding="utf-8")
        raise RuntimeError("fixture failure")

    adapters = run_adapters()
    adapters["prepare_inputs"] = StageAdapter(
        "prepare_inputs",
        fail_after_partial_write,
    )
    with pytest.raises(ControlPlaneError, match="fixture failure"):
        run_engine(
            contract_path,
            source,
            run_root,
            "synthetic",
            adapters=adapters,
        )
    assert not (run_root / "outputs" / "01-prepare-inputs").exists()
    assert (
        run_root / "failures" / "01-prepare-inputs" / "partial.txt"
    ).is_file()
    assert not (run_root / "stages" / "01-prepare-inputs" / "stage.json").exists()


def test_tool_drift_between_stages_stops_before_next_output(tmp_path):
    source = tmp_path / "source.pdf"
    make_source(source)
    contract_path = write_contract(tmp_path, source)
    tools_root = tmp_path / "tools"
    python = tools_root / "python.exe"
    powershell = tools_root / "pwsh.exe"
    pdftoppm = tools_root / "pdftoppm.exe"
    mineru_root = tools_root / "mineru"
    mineru = mineru_root / ".venv" / "Scripts" / "mineru.exe"
    initialize = mineru_root / "scripts" / "initialize.ps1"
    for path in (python, powershell, pdftoppm, mineru, initialize):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(path.name.encode("ascii"))
    (mineru_root / "capability.json").write_text(
        json.dumps(
            {
                "schema": "nri.mineru_cuda_capability.v1",
                "capability": "mineru_cuda",
                "state": "available",
                "reason_code": "nvidia_smi_cuda_candidate",
                "checked_at_utc": "2026-09-14T00:00:00Z",
                "probe": {
                    "platform": "Win32NT",
                    "nvidia_device_detected": True,
                    "video_controllers": ["NVIDIA fixture"],
                    "nvidia_smi_path": "nvidia-smi.exe",
                    "devices": ["NVIDIA fixture, 999.0"],
                },
            }
        ),
        encoding="utf-8",
    )
    runtime = RuntimeOptions(
        mineru_root=mineru_root,
        pdftoppm=pdftoppm,
        powershell=powershell,
        python=python,
    )
    adapters = run_adapters()
    original_prepare = adapters["prepare_inputs"].invoke

    def mutate_tool(output: Path) -> dict:
        result = dict(original_prepare(output))
        python.write_bytes(b"changed")
        return result

    adapters["prepare_inputs"] = StageAdapter("prepare_inputs", mutate_tool)
    run_root = tmp_path / "run"
    with pytest.raises(ControlPlaneError, match="stale tool binding: python"):
        run_engine(
            contract_path,
            source,
            run_root,
            "synthetic",
            adapters=adapters,
            runtime=runtime,
        )
    assert (run_root / "outputs" / "01-prepare-inputs").is_dir()
    assert not (run_root / "outputs" / "02-mineru-three-view").exists()


def test_new_control_plane_schemas_are_valid_json():
    contracts = Path(__file__).resolve().parents[1] / "contracts"
    for name in (
        "scenario_reconstruction_contract.v1.schema.json",
        "run_spec.v1.schema.json",
        "stage_manifest.v1.schema.json",
        "review_queue.v1.schema.json",
        "reconstruction_decision_set.v1.schema.json",
        "run_skip.v1.schema.json",
    ):
        schema = json.loads((contracts / name).read_text(encoding="utf-8"))
        assert schema["$schema"].endswith("2020-12/schema")
        assert schema["additionalProperties"] is False


def test_review_issue_kinds_are_derived_without_scenario_constants():
    role = {
        "strategies": ["reading_order", "visual_preserve", "ocr_region"],
        "traits": ["statblock", "table_heavy", "form_like"],
    }
    packet = {
        "review_signals": {
            "normalized_text_similarity": 0.8,
            "text_length_divergence": 0.1,
            "block_type_divergence": 1,
            "asset_count_divergence": 2,
            "missing_overlay_box_candidates": 1,
        }
    }
    assert _review_issue_kinds(role, packet, True) == [
        "page_fidelity",
        "reading_order",
        "visual_preserve",
        "ocr_region",
        "structured_statblock",
        "structured_table",
        "form_like",
        "geometry_box_difference",
        "semantic_conflict",
        "asset_ambiguity",
    ]


def test_production_fidelity_adapter_uses_merge_index_root(tmp_path, monkeypatch):
    run_root = tmp_path / "run"
    output = tmp_path / "audit-output"
    captured: list[list[str]] = []

    def fake_run(argv, *, cwd=None, env_updates=None):
        captured.append(list(argv))
        audit_path = Path(argv[argv.index("--output") + 1])
        audit_path.write_text(json.dumps({"passed": True}), encoding="utf-8")
        return {"argv": list(argv), "exit_code": 0}

    monkeypatch.setattr(reconstruction_module.pipeline_process, "run", fake_run)
    adapters = production_resume_adapters(
        {
            "local": {
                "run_root": str(run_root),
                "executable_paths": {"python": "python.exe"},
            }
        },
        {"reviewed_allowlist": None},
        tmp_path / "decisions",
    )
    adapters["fidelity_audit"].invoke(output)
    argv = captured[0]
    assert argv[argv.index("--mode") + 1] == "legacy-v1"
    packets_root = Path(argv[argv.index("--merge-packets-root") + 1])
    assert packets_root == (
        run_root
        / "outputs"
        / "04-visual-merge-bundle"
        / "merge_packets"
    )
    assert packets_root.name != "pages"
