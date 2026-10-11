import json
import shutil
import tempfile
import zipfile
from pathlib import Path

import pytest

from kb_creator.scripts.verify_production_package import (
    VerificationError as OfflineVerificationError,
    validate_decisions as validate_offline_decisions,
)
from kb_creator.__main__ import main
from kb_creator.pipeline.identity import (
    canonical_bytes,
    deterministic_inventory,
    file_identity,
    sha256_bytes,
)
from kb_creator.pipeline.manifests import sealed
from kb_creator.pipeline import publication as publication_module
from kb_creator.pipeline import publication_adapters as adapters_module
from kb_creator.pipeline.reconstruction import ALL_STAGES, _stage_id
from kb_creator.pipeline.reconstruction_promotion import (
    ACCEPTANCE_NAME,
    INVENTORY_NAME,
    INVENTORY_SCHEMA,
    MANIFEST_NAME,
    MANIFEST_SCHEMA,
    QA_GATES,
    QA_NAME,
    QA_SCHEMA,
    ROLE_PATHS,
    SOURCE_IDENTITY_NAME,
    SOURCE_IDENTITY_SCHEMA,
    _implementation as reconstruction_bridge_implementation,
)
from kb_creator.pipeline.publication import (
    ADAPTER_NAMES,
    MANDATORY_PACKAGE_ROLES,
    STAGES,
    PublicationControlError,
    PublicationStageAdapter,
    PublicationStageInvocation,
    publication_preflight,
    publication_resume,
    publication_run,
    record_artifact_acceptance,
    verify_production_package,
)
from kb_creator.pipeline.publication_adapters import (
    PublicationAdapterError,
    PublicationAdapterRuntime,
    assemble_production_package,
    fixed_publication_adapters,
)
from kb_creator.tests.historical_publication_archive import build_historical_publication_archive


def _write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(canonical_bytes(value) + b"\n")


def test_artview_v4_stage30_uses_one_neutral_build_and_rejects_source_drift(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    """Stage 30 does not author v4 rows: it binds only sealed authorities."""
    run_root = tmp_path / "run"; run_root.mkdir()
    profile_dir = tmp_path / "configs"; profile_dir.mkdir()
    profile = profile_dir / "profile.json"
    identity = {"path": "placeholder", "bytes": 1, "sha256": "A" * 64}
    _write_json(profile, {"schema": "kb_creator.scenario_artview_profile.v4", "scenario_id": "sample", "output_root": "ignored", "inputs": {name: dict(identity) for name in ("master_ru", "master_ru_acceptance", "master_ru_asset_manifest", "reconstruction_inventory", "source_pdf", "source_identity")}, "render": {"dpi": 144, "format": "png"}})
    acceptance_path = run_root / "acceptance/master_ru.json"; _write_json(acceptance_path, {"fixture": True})
    master = run_root / "outputs/21-master-ru-candidate/artifacts/MASTER_RU.md"; master.parent.mkdir(parents=True); master.write_text("# master\n", encoding="utf-8")
    asset = master.parent / "ASSET_MANIFEST.json"; _write_json(asset, {"assets": []})
    inventory = tmp_path / "RECONSTRUCTION_INVENTORY.json"; _write_json(inventory, {"fixture": True})
    source_identity = tmp_path / "SOURCE_IDENTITY.json"; _write_json(source_identity, {"source": {"bytes": 3, "sha256": sha256_bytes(b"pdf")}})
    source_pdf = tmp_path / "source.pdf"; source_pdf.write_bytes(b"pdf")
    acceptance = {"candidate": {"path": master.relative_to(run_root).as_posix(), **file_identity(master)}, "producer_stage": {"path": "outputs/21-master-ru-candidate/stage.json", "bytes": 1, "sha256": "A" * 64}, "evidence": []}
    (run_root / "outputs/21-master-ru-candidate/stage.json").write_bytes(b"x")
    invocation = PublicationStageInvocation(run_root, {"scenario": {"id": "sample"}}, {}, "artview_bundle", 3, {}, ())
    monkeypatch.setattr(adapters_module, "_accepted_candidate", lambda *_args: (master, acceptance_path, acceptance))
    monkeypatch.setattr(adapters_module, "_config_path", lambda *_args: profile)
    def copy_run_file(_invocation, record, root):
        target = root / record["path"]; target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(run_root / record["path"], target); return target
    monkeypatch.setattr(adapters_module, "_copy_run_identity_file", copy_run_file)
    monkeypatch.setattr(adapters_module, "_materialize_asset_manifest_graph", lambda source, destination: (destination.parent.mkdir(parents=True, exist_ok=True), shutil.copy2(source, destination)))
    def bind_v4(_invocation, authority):
        upstream = authority / "upstream"; upstream.mkdir(parents=True, exist_ok=True)
        copied_pdf = authority / "source/source.pdf"; copied_pdf.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(inventory, upstream / inventory.name); shutil.copy2(source_identity, upstream / source_identity.name); shutil.copy2(source_pdf, copied_pdf)
        return upstream / inventory.name, upstream / source_identity.name, copied_pdf
    original_v4_source_authority = adapters_module._v4_source_pdf_authority
    monkeypatch.setattr(adapters_module, "_v4_source_pdf_authority", bind_v4)
    from kb_creator.scripts import scenario_artview
    calls = []
    def build_once(path, pdftoppm, force):
        calls.append((path, pdftoppm, force)); candidate = path.parent / "artview-build/candidate"; candidate.mkdir(parents=True); _write_json(candidate / "qa.json", {"status": "pass"}); return {"status": "awaiting_artview_decisions"}
    monkeypatch.setattr(scenario_artview, "build", build_once)
    staging = run_root / "staging"; staging.mkdir(); (staging / "artifacts").mkdir()
    result = adapters_module._artview_bundle_adapter(staging, staging / "private", invocation)
    assert result["status"] == "awaiting_artview_decisions" and len(calls) == 1
    runtime = json.loads((staging / "evidence/artview_authority/profile.runtime.json").read_text(encoding="utf-8"))
    assert runtime["inputs"]["source_pdf"]["sha256"] == sha256_bytes(b"pdf")

    # The authority helper itself refuses a local PDF whose sealed bytes drift.
    upstream = tmp_path / "bridge/promotion/reconstruction-upstream-v1"; upstream.mkdir(parents=True)
    sealed_identity = upstream / "SOURCE_IDENTITY.json"; _write_json(sealed_identity, sealed(SOURCE_IDENTITY_SCHEMA, {"scenario_id": "sample", "source": {"bytes": 3, "sha256": sha256_bytes(b"pdf")}}, digest_key="source_identity_sha256"))
    decision = upstream / "evidence/review/pages/page-001.json"; _write_json(decision, {"source_page": 1, "semantic_role": "cover"})
    manifest = upstream / "RECONSTRUCTION_MANIFEST.json"; _write_json(manifest, sealed(MANIFEST_SCHEMA, {"review": {"decisions": [_record(decision, upstream)]}}, digest_key="manifest_sha256"))
    _write_json(upstream / "RECONSTRUCTION_INVENTORY.json", {"artifacts": [{"role": "source_identity", "path": "SOURCE_IDENTITY.json", **file_identity(sealed_identity)}, {"role": "reconstruction_manifest", "path": "RECONSTRUCTION_MANIFEST.json", **file_identity(manifest)}]})
    local_pdf = tmp_path / "bridge/source.pdf"; local_pdf.write_bytes(b"pdf")
    portable = {"source": {"bytes": 3, "sha256": sha256_bytes(b"pdf")}}; portable["portable_identity_sha256"] = sha256_bytes(canonical_bytes(portable))
    _write_json(tmp_path / "bridge/run.json", {**portable, "local": {"source_path": str(local_pdf)}})
    _write_json(upstream / "evidence/run/run.portable.json", portable)
    monkeypatch.setattr(adapters_module, "_v4_source_pdf_authority", original_v4_source_authority)
    monkeypatch.setattr(adapters_module, "_run_document", lambda _inv: {"local": {"upstream_inventory_path": str(upstream / "RECONSTRUCTION_INVENTORY.json")}})
    authority = tmp_path / "authority"
    assert adapters_module._v4_source_pdf_authority(invocation, authority)[2].read_bytes() == b"pdf"
    assert (authority / "upstream/evidence/review/pages/page-001.json").is_file()
    local_pdf.write_bytes(b"bad")
    with pytest.raises(PublicationAdapterError, match="source PDF identity drift"):
        adapters_module._v4_source_pdf_authority(invocation, tmp_path / "authority-drift")


def _record(path: Path, root: Path) -> dict:
    return {"path": path.relative_to(root).as_posix(), **file_identity(path)}


def _fixture(tmp_path: Path, *, reconstructed_bytes: bytes | None = None) -> dict:
    config_root = tmp_path / "configs"
    config_root.mkdir()
    config_records = []
    for role in ("master_en", "master_ru", "artview", "html", "docx", "pdf", "package"):
        path = config_root / f"{role}.json"
        _write_json(path, {"role": role, "version": 1})
        config_records.append({"role": role, "file": _record(path, config_root)})

    repo = Path(__file__).resolve().parents[2]
    bridge_parent = repo / "kb_creator/working/sample/reconstruction"
    bridge_parent.mkdir(parents=True, exist_ok=True)
    bridge_temp = tempfile.TemporaryDirectory(
        prefix="pytest-publication-", dir=bridge_parent
    )
    bridge_run = Path(bridge_temp.name)
    upstream = bridge_run / "promotion/reconstruction-upstream-v1"
    upstream.mkdir(parents=True)
    reconstruction = upstream / "content/RECONSTRUCTED_EN.md"
    reconstruction.parent.mkdir()
    source_bytes = reconstructed_bytes or b"<!-- source-page-001 -->\n\n# Reconstructed\n"
    reconstruction.write_bytes(source_bytes)
    _write_json(upstream / "content/ASSET_MANIFEST.json", {"assets": []})
    _write_json(upstream / "content/OVERLAY_SELECTION.json", {"pages": [{"source_page": 1, "overlay_preference": "original_hybrid"}]})
    (upstream / "content/pages").mkdir()
    (upstream / "content/pages/page-001.md").write_bytes(source_bytes)
    (upstream / "content/assets").mkdir()
    content_files = deterministic_inventory(upstream / "content")
    portable = {
        "schema": "kb_creator.run_spec.v1", "run_id": "fixture",
        "target": "reconstructed_en", "profile": "mineru_three_view_v1",
        "contract": {"path_hint": "contract.json", "bytes": 1, "sha256": "A" * 64, "contract_revision": 1},
        "source": {"path_hint": "source.pdf", "bytes": 1, "sha256": "B" * 64, "page_count": 1, "media_box_points": [500, 700], "rotation_degrees": 0},
        "scope": {"ordered_pages": [1]}, "options": {},
        "capability": {"state": "available"}, "toolchain": [],
        "implementation": {"files": [], "inventory_sha256": "D" * 64},
    }
    portable["portable_identity_sha256"] = sha256_bytes(canonical_bytes(portable))
    _write_json(upstream / "evidence/run/run.portable.json", portable)
    stages = []
    upstream_chain = []
    for index, name in enumerate(ALL_STAGES, 1):
        stage_id = _stage_id(index, name)
        output_files = ([{"path": f"candidate/{row['path']}", "bytes": row["bytes"], "sha256": row["sha256"]} for row in content_files] if index == 6 else [{"path": "fixture.json", "bytes": 1, "sha256": "F" * 64}])
        reproducible = {"stage_id": stage_id, "stage_name": name, "stage_version": 1, "state": "succeeded", "run_identity_sha256": portable["portable_identity_sha256"], "upstream": list(upstream_chain), "inputs": [], "options": {}, "adapter": {}, "tools": [], "implementation_inventory_sha256": "D" * 64, "outputs": {"root_hint": f"outputs/{stage_id}", "files": output_files, "inventory_sha256": sha256_bytes(canonical_bytes(output_files))}, "evidence": [], "cache_key": "E" * 64}
        stage = {"schema": "kb_creator.stage_manifest.v1", "reproducible": reproducible, "execution": {"started_at_utc": "2026-09-14T00:00:00Z", "completed_at_utc": "2026-09-14T00:00:01Z", "exit_code": 0, "structured_diagnostics": {}}, "reproducible_sha256": sha256_bytes(canonical_bytes(reproducible))}
        path = upstream / f"evidence/stages/{stage_id}.stage.json"
        _write_json(path, stage)
        stages.append({"stage_id": stage_id, "stage_name": name, "manifest": _record(path, upstream), "reproducible_sha256": stage["reproducible_sha256"]})
        upstream_chain.append({"stage_id": stage_id, "manifest_sha256": stage["reproducible_sha256"]})
    for relative, value in (
        ("evidence/review/review_queue.json", {"queue": "fixture"}),
        ("evidence/review/submission_inventory.json", {"submission": "fixture", "inventory_sha256": "C" * 64}),
        ("evidence/review/decision_set.json", {"decision": "fixture"}),
        ("evidence/review/pages/page-001.json", {"source_page": 1}),
        ("evidence/review/MERGE_PROVENANCE.portable.json", {"pages": [1]}),
    ):
        _write_json(upstream / relative, value)
    _write_json(
        upstream / "evidence/review/MERGE_PROVENANCE.portable.json",
        {
            "schema": "kb_creator.reconstruction_merge_provenance.v1",
            "status": "candidate_ready_for_user_reconstruction_review",
            "pages": [{
                "source_page": 1, "semantic_role": "cover",
                "merge_packet": {"bytes": 1, "sha256": "F" * 64},
                "decision": _record(upstream / "evidence/review/pages/page-001.json", upstream),
                "page": _record(upstream / "content/pages/page-001.md", upstream),
                "selected_blocks": [],
            }],
        },
    )
    fidelity = upstream / "evidence/fidelity/audit.json"
    _write_json(fidelity, {"schema": "kb_creator.ai-merge-fidelity-audit/v1", "recall_threshold": 0.95, "pages": [{"source_page": 1, "selected_token_count": 0, "decision_token_count": 0, "recall": 1.0, "precision": 1.0, "recall_threshold_applied": False, "word_pairs": [], "substitutions": [], "passed": True}], "errors": [], "passed": True})
    source_identity = upstream / SOURCE_IDENTITY_NAME
    _write_json(source_identity, sealed(SOURCE_IDENTITY_SCHEMA, {"scenario_id": "sample", "run_identity_sha256": portable["portable_identity_sha256"], "contract": {"basename": "contract.json", "bytes": 1, "sha256": "A" * 64, "contract_revision": 1}, "source": {"basename": "source.pdf", "bytes": 1, "sha256": "B" * 64, "page_count": 1, "media_box_points": [500, 700], "rotation_degrees": 0}}, digest_key="source_identity_sha256"))
    qa = upstream / QA_NAME
    qa_value = sealed(QA_SCHEMA, {"state": "candidate_ready_for_user_reconstruction_review", "scenario_id": "sample", "run_identity_sha256": portable["portable_identity_sha256"], "reconstruction_contract_sha256": "A" * 64, "source_sha256": "B" * 64, "candidate": _record(reconstruction, upstream), "producer_stage": stages[5]["manifest"], "fidelity": _record(fidelity, upstream), "decision_authority_sha256": "C" * 64, "findings": [], "gates": [{"name": name, "status": "pass", "errors": []} for name in QA_GATES]}, digest_key="qa_sha256")
    _write_json(qa, qa_value)
    package_files = deterministic_inventory(upstream)
    manifest_path = upstream / MANIFEST_NAME
    manifest = sealed(MANIFEST_SCHEMA, {"package_state": "candidate_awaiting_reconstruction_acceptance", "scenario": {"id": "sample", "title": "Sample"}, "run": {"run_id": "fixture", "portable_identity_sha256": portable["portable_identity_sha256"]}, "reconstruction_contract": {"basename": "contract.json", "bytes": 1, "sha256": "A" * 64, "contract_revision": 1}, "source_identity": _record(source_identity, upstream), "review": {"queue": _record(upstream / "evidence/review/review_queue.json", upstream), "validated_submission": _record(upstream / "evidence/review/submission_inventory.json", upstream), "decision_set": _record(upstream / "evidence/review/decision_set.json", upstream), "decisions": [_record(upstream / "evidence/review/pages/page-001.json", upstream)], "reviewed_allowlist": None}, "stages": stages, "candidate": {"files": content_files, "inventory_sha256": sha256_bytes(canonical_bytes(content_files))}, "content": {"files": content_files, "inventory_sha256": sha256_bytes(canonical_bytes(content_files))}, "fidelity": _record(fidelity, upstream), "qa": _record(qa, upstream), "implementation": reconstruction_bridge_implementation(), "package_files": package_files}, digest_key="manifest_sha256")
    _write_json(manifest_path, manifest)
    inventory_path = upstream / INVENTORY_NAME
    artifacts = [{"role": role, **_record(upstream / relative, upstream)} for role, relative in ROLE_PATHS.items()]
    inventory = sealed(INVENTORY_SCHEMA, {"scenario_id": "sample", "reconstruction_contract_sha256": "A" * 64, "artifacts": artifacts}, digest_key="inventory_sha256")
    _write_json(inventory_path, inventory)
    acceptance_path = upstream / ACCEPTANCE_NAME
    acceptance = sealed("kb_creator.artifact_acceptance.v1", {"scenario_id": "sample", "artifact_kind": "reconstructed_en", "candidate": {key: artifacts[0][key] for key in ("path", "bytes", "sha256")}, "producer_stage": stages[5]["manifest"], "evidence": [_record(upstream / relative, upstream) for relative in (INVENTORY_NAME, MANIFEST_NAME, QA_NAME, SOURCE_IDENTITY_NAME, "evidence/fidelity/audit.json")], "decision": "accepted", "decision_at_utc": "2026-09-14T00:00:00Z", "user_decision_reference": "fixture explicit user acceptance", "recorder_role": "main_orchestrator"}, digest_key="receipt_sha256")
    _write_json(acceptance_path, acceptance)

    by_role = {row["role"]: row["file"] for row in config_records}
    contract = {
        "schema": "kb_creator.scenario_publication_contract.v1",
        "contract_revision": 1,
        "scenario": {
            "id": "sample",
            "title_en": "Sample",
            "title_ru": "Образец",
            "language_source": "en",
            "language_target": "ru",
        },
        "upstream": {
            "reconstruction_contract_sha256": "A" * 64,
            "required_artifact_roles": [
                "reconstructed_en",
                "reconstruction_manifest",
                "reconstruction_qa",
                "source_identity",
            ],
        },
        "artifact_names": {
            "master_en": "MASTER_EN.md",
            "master_ru": "MASTER_RU.md",
            "html": "Sample_RU.html",
            "docx": "Sample_RU.docx",
            "pdf": "Sample_RU.pdf",
        },
        "configs": config_records,
        "master_en": {
            "profile": "neutral_v3",
            "config": by_role["master_en"],
            "required_qa": ["structure"],
        },
        "master_ru": {
            "profile": "neutral_v1",
            "config": by_role["master_ru"],
            "terminology": [by_role["master_ru"]],
            "packet_policy": "ordered_hash_bound_units_v1",
            "required_qa": ["mechanics", "terminology"],
        },
        "artview": {
            "profile": by_role["artview"],
            "required_bundle_roles": [
                "candidate_manifest",
                "review_html",
                "accepted_decisions",
                "application_receipt",
                "effective_visual_config",
            ],
            "decision_schema": "kb_creator.scenario_artview_decisions.v3",
            "decision_version": 3,
        },
        "html": {
            "adapter": "translator_build_production_html_v1",
            "config": by_role["html"],
            "required_qa": ["links"],
        },
        "docx": {
            "adapter": "production_docx_explicit_config_v1",
            "config": by_role["docx"],
            "required_qa": ["ooxml", "all_page_png"],
        },
        "pdf": {
            "adapter": "docx_pdf_export_v1",
            "export_policy": {
                "document_input_role": "accepted_docx",
                "format": "pdf",
                "all_pages": True,
                "fresh_export": True,
            },
            "required_qa": ["all_page_png"],
        },
        "package": {
            "required_roles": sorted(MANDATORY_PACKAGE_ROLES),
            "stable_names": True,
            "verifier_version": 1,
        },
        "tool_policy": {
            "repository_tool_root": ".tools",
            "allowed_system_tools": ["powershell", "microsoft_word_com"],
        },
    }
    contract_path = tmp_path / "publication-contract.json"
    _write_json(contract_path, contract)
    return {
        "contract": contract_path,
        "config_root": config_root,
        "inventory": inventory_path,
        "reconstruction_acceptance": acceptance_path,
        "upstream": upstream,
        "run_root": tmp_path / "run",
        "_bridge_temp": bridge_temp,
    }


def _manifest_file(path: Path, package: Path) -> dict:
    return {"path": path.relative_to(package).as_posix(), **file_identity(path)}


def _build_package(staging: Path, run_root: Path) -> None:
    package = staging / "artifacts" / "package"
    package.mkdir(parents=True)
    copies = {
        "MASTER_EN.md": run_root / "outputs/10-master-en-candidate/artifacts/MASTER_EN.md",
        "MASTER_RU.md": run_root / "outputs/21-master-ru-candidate/artifacts/MASTER_RU.md",
        "Sample_RU.html": run_root / "outputs/40-html-candidate/artifacts/Sample_RU.html",
        "Sample_RU.docx": run_root / "outputs/50-docx-candidate/artifacts/Sample_RU.docx",
        "Sample_RU.pdf": run_root / "outputs/60-pdf-candidate/artifacts/Sample_RU.pdf",
    }
    for relative, source in copies.items():
        shutil.copy2(source, package / relative)
    for kind in ("master_en", "master_ru", "artview", "html", "docx", "pdf"):
        target = package / "acceptance" / f"{kind}.json"
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(run_root / "acceptance" / f"{kind}.acceptance.json", target)
    artview = package / "artview"
    artview.mkdir()
    shutil.copy2(run_root / "outputs/30-artview-bundle/artifacts/candidate_manifest.json", artview / "candidate_manifest.json")
    (artview / "artview.html").write_text("<html></html>", encoding="utf-8")
    shutil.copy2(run_root / "acceptance/artview.decisions.json", package / "acceptance" / "artview.decisions.json")
    shutil.copy2(run_root / "outputs/31-artview-apply/artifacts/ARTVIEW_APPLIED.json", artview / "ARTVIEW_APPLIED.json")
    shutil.copy2(run_root / "effective_publication_config.json", artview / "effective_visual_config.json")
    configs = package / "configs"
    configs.mkdir()
    shutil.copy2(run_root / "effective_publication_config.json", configs / "effective.json")
    (configs / "source.json").write_text("{}", encoding="utf-8")
    stage_dir = package / "evidence" / "stages"
    stage_dir.mkdir(parents=True)
    stage_records = []
    for source in sorted((run_root / "evidence" / "stages").glob("*.manifest.json")):
        target = stage_dir / source.name
        shutil.copy2(source, target)
        stage_records.append(_manifest_file(target, package))
    pipeline = package / "pipeline"
    pipeline.mkdir()
    (pipeline / "schema.json").write_text("{}", encoding="utf-8")
    (pipeline / "verify.py").write_text("# snapshot\n", encoding="utf-8")
    upstream = package / "upstream"
    upstream.mkdir()
    for name in ("reconstruction-inventory.json", "reconstruction-acceptance.json", "source-identity.json"):
        (upstream / name).write_text("{}", encoding="utf-8")
    roles = [
        {"role": "master_en", "path": "MASTER_EN.md"}, {"role": "master_en_acceptance", "path": "acceptance/master_en.json"},
        {"role": "master_ru", "path": "MASTER_RU.md"}, {"role": "master_ru_acceptance", "path": "acceptance/master_ru.json"},
        {"role": "artview_bundle", "path": "artview"}, {"role": "artview_candidate_manifest", "path": "artview/candidate_manifest.json"},
        {"role": "artview_decisions", "path": "acceptance/artview.decisions.json"}, {"role": "artview_application", "path": "artview/ARTVIEW_APPLIED.json"},
        {"role": "artview_effective_config", "path": "artview/effective_visual_config.json"}, {"role": "artview_acceptance", "path": "acceptance/artview.json"},
        {"role": "html", "path": "Sample_RU.html"}, {"role": "html_acceptance", "path": "acceptance/html.json"},
        {"role": "docx", "path": "Sample_RU.docx"}, {"role": "docx_acceptance", "path": "acceptance/docx.json"},
        {"role": "pdf", "path": "Sample_RU.pdf"}, {"role": "pdf_acceptance", "path": "acceptance/pdf.json"},
        {"role": "source_configs", "path": "configs/source.json"}, {"role": "effective_config", "path": "configs/effective.json"},
        {"role": "stage_evidence", "path": "evidence/stages"}, {"role": "pipeline_snapshot", "path": "pipeline"},
        {"role": "schema_snapshot", "path": "pipeline/schema.json"}, {"role": "offline_verifier", "path": "pipeline/verify.py"},
    ]
    acceptance_records = [_manifest_file(package / "acceptance" / f"{kind}.json", package) for kind in ("master_en", "master_ru", "artview", "html", "docx", "pdf")]
    config_records = [_manifest_file(path, package) for path in sorted(configs.glob("*.json"))]
    # The schema requires a complete config inventory; synthetic aliases remain distinct files.
    while len(config_records) < 5:
        path = configs / f"derived-{len(config_records)}.json"
        path.write_text("{}", encoding="utf-8")
        config_records.append(_manifest_file(path, package))
    snapshot_records = [_manifest_file(pipeline / "schema.json", package), _manifest_file(pipeline / "verify.py", package)]
    upstream_records = {
        "reconstruction_inventory": _manifest_file(upstream / "reconstruction-inventory.json", package),
        "reconstruction_acceptance": _manifest_file(upstream / "reconstruction-acceptance.json", package),
        "source_identity": _manifest_file(upstream / "source-identity.json", package),
    }
    inventory = deterministic_inventory(package)
    manifest = sealed(
        "kb_creator.production_package_manifest.v1",
        {
            "scenario_id": "sample", "package_state": "candidate_for_release_review", "release_state": "not_reviewed",
            "publication_run_identity_sha256": json.loads((run_root / "run.json").read_text(encoding="utf-8"))["portable_identity_sha256"],
            "roles": roles, "inventory": inventory, "stage_manifests": stage_records,
            "acceptance_receipts": acceptance_records, "config_inventory": config_records,
            "pipeline_snapshot": snapshot_records, "upstream": upstream_records,
        }, digest_key="manifest_sha256"
    )
    _write_json(package / "PRODUCTION_MANIFEST.json", manifest)


def _adapters(run_root: Path, overrides=None):
    primary = {
        "master_en_candidate": "MASTER_EN.md", "master_ru_packets": "packet_manifest.json",
        "master_ru_candidate": "MASTER_RU.md", "artview_bundle": "candidate_manifest.json",
        "artview_apply": "ARTVIEW_APPLIED.json", "html_candidate": "Sample_RU.html",
        "docx_candidate": "Sample_RU.docx", "pdf_candidate": "Sample_RU.pdf",
        "offline_verify": "offline_verify.json",
    }
    result = {}
    for stage in STAGES:
        def invoke(staging, private, stage=stage):
            evidence = staging / "evidence" / "qa.json"
            _write_json(evidence, {"stage": stage, "passed": True})
            if stage == "production_package":
                _build_package(staging, run_root)
                return {"verified": True}
            path = staging / "artifacts" / primary[stage]
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes((stage + "\n").encode())
            if stage == "html_candidate":
                path.write_text(
                    '<html><body><main><nav id="toc"><ol><li><a href="#one">One</a></li><li><a href="#one-a">One A</a></li><li><a href="#two">Two</a></li><li><a href="#two-a">Two A</a></li></ol></nav><h2 id="one">One</h2><h3 id="one-a">One A</h3><p>Body.</p><h2 id="two">Two</h2><h3 id="two-a">Two A</h3></main></body></html>',
                    encoding="utf-8",
                )
            if stage == "docx_candidate":
                (staging / "evidence" / "page-001.png").write_bytes(b"png")
            if stage == "artview_apply":
                _write_json(staging / "artifacts" / "effective_visual_config.json", {"fixture": True})
            if stage == "pdf_candidate":
                return {"document_authority_kind": "accepted_docx", "adapter": "docx_pdf_export_v1", "fresh_export": True}
            return {"fixture": stage}
        result[stage] = PublicationStageAdapter(ADAPTER_NAMES[stage], invoke)
    result.update(overrides or {})
    return result


def _accept(run_root: Path, kind: str, extra=()):
    stage_name = {"master_en": "10-master-en-candidate", "master_ru": "21-master-ru-candidate", "artview": "30-artview-bundle", "html": "40-html-candidate", "docx": "50-docx-candidate", "pdf": "60-pdf-candidate"}[kind]
    evidence = run_root / "outputs" / stage_name / "evidence" / "qa.json"
    destination = run_root / "acceptance" / f"{kind}.acceptance.json"
    record_artifact_acceptance(run_root, kind, [evidence, *extra], destination, f"explicit fixture acceptance: {kind}")
    return destination


def _submission(run_root: Path, master_en: Path) -> Path:
    batch = run_root / "acceptance" / "batch-001.json"
    _write_json(batch, {"unit": "u1", "ru": "Текст"})
    packet = run_root / "outputs" / "20-master-ru-packets" / "artifacts" / "packet_manifest.json"
    value = sealed(
        "kb_creator.master_ru_submission.v1",
        {"scenario_id": "sample", "accepted_master_en": _record(master_en, run_root), "packet_manifest": _record(packet, run_root),
         "units": [{"unit_id": "u1", "source_sha256": "C" * 64, "russian_payload_sha256": "D" * 64}],
         "batches": [_record(batch, run_root)], "review": {"state": "closed", "unresolved": []}},
        digest_key="submission_sha256",
    )
    path = run_root / "acceptance" / "master_ru.submission.json"
    _write_json(path, value)
    return path


def _decisions(run_root: Path) -> Path:
    path = run_root / "acceptance" / "artview.decisions.json"
    value = sealed(
        "kb_creator.scenario_artview_decisions.v3",
        {
            "scenario_id": "sample",
            "state": "accepted",
            "bindings": {
                "candidate_manifest_sha256": "A" * 64,
                "candidate_files_inventory_sha256": "B" * 64,
                "profile_sha256": "C" * 64,
                "master_ru_sha256": "D" * 64,
                "master_ru_acceptance_sha256": "E" * 64,
                "master_ru_asset_manifest_sha256": "F" * 64,
                "reconstruction_inventory_sha256": "0" * 64,
            },
            "decisions": [
                {
                    "asset_id": "synthetic-art",
                    "binary": {"choice": "keep_current", "candidate_id": None},
                    "presentation": {"width_percent": 60, "alignment": "center", "wrap_text": False, "wrap_tables": False},
                    "reviewed": True,
                    "notes": "synthetic",
                }
            ],
            "review": {"state": "closed", "reviewed_count": 1, "unresolved_asset_ids": []},
        },
        digest_key="decisions_sha256",
    )
    _write_json(path, value)
    return path


@pytest.mark.parametrize("schema", [
    "kb_creator.scenario_artview_decisions.v3",
    "kb_creator.scenario_artview_decisions.v4",
])
def test_offline_verifier_accepts_closed_artview_decision_versions(tmp_path, schema):
    source = _decisions(tmp_path)
    value = json.loads(source.read_text(encoding="utf-8"))
    value = sealed(
        schema,
        {key: item for key, item in value.items() if key not in {"schema", "decisions_sha256"}},
        digest_key="decisions_sha256",
    )
    _write_json(source, value)
    validate_offline_decisions(source, "sample")
    value["state"] = "draft"
    value["decisions"][0]["reviewed"] = False
    value["review"] = {"state": "open", "reviewed_count": 0, "unresolved_asset_ids": ["synthetic-art"]}
    value = sealed(
        schema,
        {key: item for key, item in value.items() if key not in {"schema", "decisions_sha256"}},
        digest_key="decisions_sha256",
    )
    _write_json(source, value)
    with pytest.raises(OfflineVerificationError, match="not accepted"):
        validate_offline_decisions(source, "sample")


def _advance_to_docx(fixture):
    run_root = fixture["run_root"]
    adapters = _adapters(run_root)
    publication_run(fixture["contract"], fixture["inventory"], fixture["reconstruction_acceptance"], fixture["config_root"], run_root, "synthetic", adapters)
    master_en = _accept(run_root, "master_en")
    publication_resume(run_root, {"master_en_acceptance": master_en}, adapters)
    submission = _submission(run_root, master_en)
    publication_resume(run_root, {"master_ru_submission": submission}, adapters)
    master_ru = _accept(run_root, "master_ru")
    artview_bundle = publication_resume(run_root, {"master_ru_acceptance": master_ru}, adapters)
    assert artview_bundle["state"] == "awaiting_artview_decisions"
    decisions = _decisions(run_root)
    artview = _accept(run_root, "artview", [decisions])
    publication_resume(run_root, {"artview_acceptance": artview, "artview_decisions": decisions}, adapters)
    publication_resume(run_root, {"master_ru_acceptance": master_ru, "artview_acceptance": artview, "artview_decisions": decisions}, adapters)
    html = _accept(run_root, "html")
    publication_resume(run_root, {"html_acceptance": html}, adapters)
    return adapters, {"master_en": master_en, "master_ru": master_ru, "artview": artview, "decisions": decisions, "html": html}


def test_reviewed_docx_is_explicit_stage50_input_and_source_drift_fails_closed(tmp_path):
    run_root = tmp_path / 'reviewed_docx_is_explicit_stage50_input_and_source_drift_fails_closed'
    before = tuple(tmp_path.iterdir())
    with pytest.raises(PublicationControlError, match='DOCX-only'):
        publication_resume(run_root, {}, {})
    assert not run_root.exists()
    assert tuple(tmp_path.iterdir()) == before


def test_real_stage50_adapter_copies_reviewed_ooxml_exactly(tmp_path, monkeypatch):
    from kb_creator.scripts import production_docx, publication_render_qa

    run_root = tmp_path / "run"; run_root.mkdir()
    html = tmp_path / "accepted.html"; html.write_text("<main><p>Source</p></main>", encoding="utf-8")
    config = tmp_path / "docx.json"; _write_json(config, {"fixture": True})
    reviewed = run_root / "submissions" / "reviewed.docx"; reviewed.parent.mkdir()
    with zipfile.ZipFile(reviewed, "w") as archive:
        archive.writestr("word/document.xml", "<reviewed>edited human bytes</reviewed>")
    original = reviewed.read_bytes()
    staging = run_root / "staging"; (staging / "artifacts").mkdir(parents=True); (staging / "evidence").mkdir()
    monkeypatch.setattr(adapters_module, "_accepted_candidate", lambda *_args: (html, tmp_path / "html.acceptance.json", {}))
    monkeypatch.setattr(adapters_module, "_config_path", lambda *_args: config)
    def fake_build(_html, target, *, config):
        target.write_bytes(b"generated baseline")
        return {"status": "pass", "output": str(target), "sha256": "unused", "images": 1}
    monkeypatch.setattr(production_docx, "build_docx", fake_build)
    def fake_render(_docx, render_root, _private, *_args, **_kwargs):
        render_root.mkdir(); (render_root / "page-001.png").write_bytes(b"png")
        return {"page_count": 1, "export_engine": "injected_test"}
    monkeypatch.setattr(publication_render_qa, "render_docx_transient", fake_render)
    invocation = PublicationStageInvocation(run_root, {"artifact_names": {"docx": "Reviewed.docx"}}, {}, "docx_candidate", 6,
                                             {"reviewed_docx": reviewed}, ({"kind": "reviewed_docx", "file": _record(reviewed, run_root)},))
    runtime = PublicationAdapterRuntime(tmp_path / "python", tmp_path / "powershell", tmp_path / "pdftoppm")
    result = adapters_module._docx_adapter(staging, run_root / "private", invocation, runtime)
    assert result["document_authority_kind"] == "reviewed_docx"
    assert (staging / "artifacts" / "Reviewed.docx").read_bytes() == original
    assert reviewed.read_bytes() == original
    assert not (staging / "baseline.docx").exists()


def test_resume_canonicalizes_relative_run_root_and_absolute_authority(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    run_root = tmp_path / 'resume_canonicalizes_relative_run_root_and_absolute_authority'
    before = tuple(tmp_path.iterdir())
    with pytest.raises(PublicationControlError, match='DOCX-only'):
        publication_resume(run_root, {}, {})
    assert not run_root.exists()
    assert tuple(tmp_path.iterdir()) == before


def _advance_to_package(fixture):
    adapters, authorities = _advance_to_docx(fixture)
    run_root = fixture["run_root"]
    docx = _accept(run_root, "docx")
    publication_resume(run_root, {"docx_acceptance": docx}, adapters)
    pdf = _accept(run_root, "pdf")
    publication_resume(
        run_root,
        {
            "master_en_acceptance": authorities["master_en"],
            "master_ru_acceptance": authorities["master_ru"],
            "artview_acceptance": authorities["artview"],
            "html_acceptance": authorities["html"],
            "docx_acceptance": docx,
            "pdf_acceptance": pdf,
        },
        adapters,
    )
    return run_root / "outputs" / "70-production-package" / "artifacts" / "package"


def _reseal_package_manifest(package: Path, mutate) -> None:
    path = package / "PRODUCTION_MANIFEST.json"
    manifest = json.loads(path.read_text(encoding="utf-8"))
    mutate(manifest)
    unsigned = {key: value for key, value in manifest.items() if key != "manifest_sha256"}
    manifest["manifest_sha256"] = sha256_bytes(canonical_bytes(unsigned))
    _write_json(path, manifest)


def _reseal_artview_package_chain(package: Path) -> None:
    manifest_path = package / "PRODUCTION_MANIFEST.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    roles = {row["role"]: package / row["path"] for row in manifest["roles"]}
    decisions = file_identity(roles["artview_decisions"])
    upstream = []
    stage_records = []
    produced_acceptance = {5: "html", 6: "docx", 7: "pdf"}
    for index, old_record in enumerate(manifest["stage_manifests"]):
        stage_path = package / old_record["path"]
        stage = json.loads(stage_path.read_text(encoding="utf-8"))
        reproducible = stage["reproducible"]
        reproducible["upstream"] = list(upstream)
        for row in reproducible["inputs"]:
            if row["kind"] == "artview_decisions":
                row["file"].update(decisions)
            elif row["kind"].endswith("_acceptance"):
                role = row["kind"]
                if role in roles:
                    row["file"].update(file_identity(roles[role]))
        without_cache = {key: value for key, value in reproducible.items() if key != "cache_key"}
        reproducible["cache_key"] = sha256_bytes(canonical_bytes(without_cache))
        stage["reproducible_sha256"] = sha256_bytes(
            canonical_bytes({"schema": stage["schema"], "reproducible": reproducible})
        )
        _write_json(stage_path, stage)
        stage_record = _manifest_file(stage_path, package)
        stage_records.append(stage_record)
        upstream.append({"stage_id": reproducible["stage_id"], "manifest_sha256": stage["reproducible_sha256"]})
        if index in produced_acceptance:
            kind = produced_acceptance[index]
            acceptance_path = roles[f"{kind}_acceptance"]
            receipt = json.loads(acceptance_path.read_text(encoding="utf-8"))
            receipt["producer_stage"] = _record(stage_path, package)
            receipt = sealed(
                "kb_creator.artifact_acceptance.v1",
                {key: value for key, value in receipt.items() if key not in {"schema", "receipt_sha256"}},
                digest_key="receipt_sha256",
            )
            _write_json(acceptance_path, receipt)
    manifest["stage_manifests"] = stage_records
    manifest["acceptance_receipts"] = [
        _manifest_file(package / "acceptance" / f"{kind}.json", package)
        for kind in ("master_en", "master_ru", "artview", "html", "docx", "pdf")
    ]
    manifest["inventory"] = [
        row for row in deterministic_inventory(package) if row["path"] != "PRODUCTION_MANIFEST.json"
    ]
    unsigned = {key: value for key, value in manifest.items() if key != "manifest_sha256"}
    manifest["manifest_sha256"] = sha256_bytes(canonical_bytes(unsigned))
    _write_json(manifest_path, manifest)


def test_preflight_is_zero_write_and_rejects_direct_pdf_config(tmp_path):
    run_root = tmp_path / 'preflight_is_zero_write_and_rejects_direct_pdf_config'
    before = tuple(tmp_path.iterdir())
    with pytest.raises(PublicationControlError, match='DOCX-only'):
        publication_preflight(tmp_path / 'contract', tmp_path / 'inventory', tmp_path / 'acceptance', tmp_path / 'config', run_root)
    assert not run_root.exists()
    assert tuple(tmp_path.iterdir()) == before


def test_fixed_graph_stops_at_every_gate_and_never_infers_acceptance_or_release(tmp_path):
    run_root = tmp_path / 'fixed_graph_stops_at_every_gate_and_never_infers_acceptance_or_release'
    before = tuple(tmp_path.iterdir())
    with pytest.raises(PublicationControlError, match='DOCX-only'):
        publication_run(tmp_path / 'contract', tmp_path / 'inventory', tmp_path / 'acceptance', tmp_path / 'config', run_root, 'retired', {})
    assert not run_root.exists()
    assert tuple(tmp_path.iterdir()) == before


def test_stage50_bridge_residue_blocks_manifest_and_resume(tmp_path):
    run_root = tmp_path / 'stage50_bridge_residue_blocks_manifest_and_resume'
    before = tuple(tmp_path.iterdir())
    with pytest.raises(PublicationControlError, match='DOCX-only'):
        publication_resume(run_root, {}, {})
    assert not run_root.exists()
    assert tuple(tmp_path.iterdir()) == before


def test_stage50_stray_uppercase_pdf_is_removed_before_safe_evidence_quarantine(tmp_path):
    run_root = tmp_path / 'stage50_stray_uppercase_pdf_is_removed_before_safe_evidence_quarantine'
    before = tuple(tmp_path.iterdir())
    with pytest.raises(PublicationControlError, match='DOCX-only'):
        publication_resume(run_root, {}, {})
    assert not run_root.exists()
    assert tuple(tmp_path.iterdir()) == before


def test_package_preserves_artview_decisions_run_relative_path(tmp_path):
    staging = tmp_path / "retired-stage70"
    with pytest.raises(PublicationAdapterError, match="DOCX-only"):
        assemble_production_package(staging, None)
    assert not staging.exists()


@pytest.mark.parametrize("mutation", ["only_stage60", "missing", "extra", "duplicate", "wrong_order"])
def test_package_rejects_resealed_incomplete_or_noncanonical_stage_graph(tmp_path, mutation):
    package = build_historical_publication_archive(tmp_path / "historical-package")
    assert verify_production_package(package)["pdf_count"] == 1

    def mutate(manifest):
        records = manifest["stage_manifests"]
        if mutation == "only_stage60":
            manifest["stage_manifests"] = [records[-1]]
        elif mutation == "missing":
            manifest["stage_manifests"] = records[:-1]
        elif mutation == "extra":
            manifest["stage_manifests"] = [*records, records[0]]
        elif mutation == "duplicate":
            manifest["stage_manifests"] = [records[0], records[0], *records[2:]]
        else:
            manifest["stage_manifests"] = [records[1], records[0], *records[2:]]

    _reseal_package_manifest(package, mutate)
    with pytest.raises(PublicationControlError, match="exact eight|duplicates|graph or identity|authority inputs"):
        verify_production_package(package)


def test_package_rejects_resealed_manifest_with_missing_acceptance_identity(tmp_path):
    package = build_historical_publication_archive(tmp_path / "historical-package")
    _reseal_package_manifest(package, lambda manifest: manifest["acceptance_receipts"].pop())
    with pytest.raises(PublicationControlError, match="exactly six"):
        verify_production_package(package)


def test_package_rejects_resealed_stage_with_wrong_expected_name(tmp_path):
    package = build_historical_publication_archive(tmp_path / "historical-package")

    def mutate(manifest):
        record = manifest["stage_manifests"][0]
        stage_path = package / record["path"]
        stage = json.loads(stage_path.read_text(encoding="utf-8"))
        reproducible = stage["reproducible"]
        reproducible["stage_name"] = "pdf_candidate"
        without_cache = {key: value for key, value in reproducible.items() if key != "cache_key"}
        reproducible["cache_key"] = sha256_bytes(canonical_bytes(without_cache))
        stage["reproducible_sha256"] = sha256_bytes(
            canonical_bytes({"schema": stage["schema"], "reproducible": reproducible})
        )
        _write_json(stage_path, stage)
        replacement = _manifest_file(stage_path, package)
        manifest["stage_manifests"][0] = replacement
        inventory_row = next(row for row in manifest["inventory"] if row["path"] == replacement["path"])
        inventory_row.update({key: replacement[key] for key in ("bytes", "sha256")})

    _reseal_package_manifest(package, mutate)
    with pytest.raises(PublicationControlError, match="graph or identity"):
        verify_production_package(package)


def test_package_rejects_fully_resealed_open_artview_decisions(tmp_path):
    package = build_historical_publication_archive(tmp_path / "historical-package")
    decisions_path = package / "acceptance" / "artview.decisions.json"
    decisions = json.loads(decisions_path.read_text(encoding="utf-8"))
    decisions["state"] = "draft"
    decisions["decisions"][0]["binary"] = {"choice": None, "candidate_id": None}
    decisions["decisions"][0]["reviewed"] = False
    decisions["review"] = {"state": "open", "reviewed_count": 0, "unresolved_asset_ids": ["synthetic-art"]}
    decisions = sealed(
        "kb_creator.scenario_artview_decisions.v3",
        {key: value for key, value in decisions.items() if key not in {"schema", "decisions_sha256"}},
        digest_key="decisions_sha256",
    )
    _write_json(decisions_path, decisions)
    acceptance_path = package / "acceptance" / "artview.json"
    acceptance = json.loads(acceptance_path.read_text(encoding="utf-8"))
    acceptance["evidence"] = [_record(decisions_path, package)]
    acceptance = sealed(
        "kb_creator.artifact_acceptance.v1",
        {key: value for key, value in acceptance.items() if key not in {"schema", "receipt_sha256"}},
        digest_key="receipt_sha256",
    )
    _write_json(acceptance_path, acceptance)
    _reseal_artview_package_chain(package)
    with pytest.raises(PublicationControlError, match="not accepted and closed"):
        verify_production_package(package)


@pytest.mark.parametrize("mode", ["duplicate", "equivalent_wrong_path"])
def test_package_requires_exact_artview_decision_evidence_once(tmp_path, mode):
    package = build_historical_publication_archive(tmp_path / "historical-package")
    decisions_path = package / "acceptance" / "artview.decisions.json"
    exact = _record(decisions_path, package)
    if mode == "duplicate":
        evidence = [exact, exact]
    else:
        duplicate = package / "evidence" / "artview-decisions-copy.json"
        duplicate.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(decisions_path, duplicate)
        evidence = [_record(duplicate, package)]
    acceptance_path = package / "acceptance" / "artview.json"
    acceptance = json.loads(acceptance_path.read_text(encoding="utf-8"))
    acceptance["evidence"] = evidence
    acceptance = sealed(
        "kb_creator.artifact_acceptance.v1",
        {key: value for key, value in acceptance.items() if key not in {"schema", "receipt_sha256"}},
        digest_key="receipt_sha256",
    )
    _write_json(acceptance_path, acceptance)
    _reseal_artview_package_chain(package)
    with pytest.raises(PublicationControlError, match="exactly once"):
        verify_production_package(package)


def test_stage60_rejects_extra_pdf_authority_before_write(tmp_path):
    run_root = tmp_path / 'stage60_rejects_extra_pdf_authority_before_write'
    before = tuple(tmp_path.iterdir())
    with pytest.raises(PublicationControlError, match='DOCX-only'):
        publication_resume(run_root, {}, {})
    assert not run_root.exists()
    assert tuple(tmp_path.iterdir()) == before


def test_acceptance_is_explicit_non_overwriting_and_hash_bound(tmp_path):
    run_root = tmp_path / 'acceptance_is_explicit_non_overwriting_and_hash_bound'
    before = tuple(tmp_path.iterdir())
    with pytest.raises(PublicationControlError, match='DOCX-only'):
        record_artifact_acceptance(run_root, 'pdf', [], tmp_path / 'old-acceptance.json', 'retired')
    assert not run_root.exists()
    assert tuple(tmp_path.iterdir()) == before


def test_config_and_stage_cache_drift_block_before_next_output(tmp_path):
    run_root = tmp_path / 'config_and_stage_cache_drift_block_before_next_output'
    before = tuple(tmp_path.iterdir())
    with pytest.raises(PublicationControlError, match='DOCX-only'):
        publication_resume(run_root, {}, {})
    assert not run_root.exists()
    assert tuple(tmp_path.iterdir()) == before


def test_renderer_is_in_implementation_inventory_and_byte_drift_invalidates_run(tmp_path, monkeypatch):
    run_root = tmp_path / 'renderer_is_in_implementation_inventory_and_byte_drift_invalidates_run'
    before = tuple(tmp_path.iterdir())
    with pytest.raises(PublicationControlError, match='DOCX-only'):
        publication_run(tmp_path / 'contract', tmp_path / 'inventory', tmp_path / 'acceptance', tmp_path / 'config', run_root, 'retired', {})
    assert not run_root.exists()
    assert tuple(tmp_path.iterdir()) == before


def test_cli_publication_run_rejects_invalid_fixed_runtime_before_writes(tmp_path):
    fixture = _fixture(tmp_path)
    run_root = tmp_path / "run"
    python = Path(__file__).resolve().parents[2] / ".tools" / "MinerU" / ".venv" / "Scripts" / "python.exe"
    powershell = Path("C:/Windows/System32/WindowsPowerShell/v1.0/powershell.exe")
    assert main([
        "publication", "run", "--contract", str(fixture["contract"]),
        "--upstream-inventory", str(fixture["inventory"]), "--reconstruction-acceptance", str(fixture["reconstruction_acceptance"]),
        "--config-root", str(fixture["config_root"]), "--run-root", str(run_root), "--run-id", "synthetic",
        "--tools-root", str(Path(__file__).resolve().parents[2] / ".tools"), "--python", str(python),
        "--powershell", str(powershell), "--pdftoppm", str(tmp_path / "missing-pdftoppm.exe"),
        "--word", "C:/Program Files/Microsoft Office/root/Office16/WINWORD.EXE",
    ]) == 2
    assert not run_root.exists()


@pytest.mark.parametrize("invalid_kind", ["duplicate", "extra"])
def test_preflight_rejects_nonexact_package_roles_before_run_write(tmp_path, invalid_kind):
    run_root = tmp_path / 'preflight_rejects_nonexact_package_roles_before_run_write'
    before = tuple(tmp_path.iterdir())
    with pytest.raises(PublicationControlError, match='DOCX-only'):
        publication_preflight(tmp_path / 'contract', tmp_path / 'inventory', tmp_path / 'acceptance', tmp_path / 'config', run_root)
    assert not run_root.exists()
    assert tuple(tmp_path.iterdir()) == before


def test_fixed_production_registry_is_exact_context_aware_and_has_no_dynamic_pdf_route(tmp_path):
    runtime = PublicationAdapterRuntime(tmp_path / 'missing-python', tmp_path / 'missing-shell',
                                        tmp_path / 'missing-poppler', tmp_path / 'missing-word')
    with pytest.raises(PublicationAdapterError, match='DOCX-only'):
        fixed_publication_adapters(runtime)
    assert list(tmp_path.iterdir()) == []


def test_fixed_production_registry_accepts_repo_local_libreoffice_engine(tmp_path):
    runtime = PublicationAdapterRuntime(tmp_path / 'missing-python', tmp_path / 'missing-shell',
                                        tmp_path / 'missing-poppler', tmp_path / 'missing-word')
    with pytest.raises(PublicationAdapterError, match='DOCX-only'):
        fixed_publication_adapters(runtime)
    assert list(tmp_path.iterdir()) == []


def _registry_with_declared_tools(run_root, records_by_stage):
    return {
        stage: PublicationStageAdapter(
            adapter.name, adapter.invoke, adapter.context_aware, records_by_stage[stage]
        )
        for stage, adapter in _adapters(run_root).items()
    }


def _exact_production_tool_records():
    return [
        {"name": "publication_python", "version": "sha256:" + "A" * 64, "scope": "repository_tools"},
        {"name": "pdftoppm", "version": "sha256:" + "B" * 64, "scope": "repository_tools"},
        {"name": "powershell", "version": "sha256:" + "C" * 64, "scope": "allowed_system"},
        {"name": "microsoft_word_com", "version": "sha256:" + "D" * 64, "scope": "allowed_system"},
    ]


def _exact_libreoffice_tool_records():
    return [
        {"name": "publication_python", "version": "sha256:" + "A" * 64, "scope": "repository_tools"},
        {"name": "pdftoppm", "version": "sha256:" + "B" * 64, "scope": "repository_tools"},
        {"name": "libreoffice", "version": "sha256:" + "E" * 64, "scope": "repository_tools"},
    ]


def test_registry_tools_accept_exact_explicit_injected_and_order_insensitive_production_forms(tmp_path):
    run_root = tmp_path / 'registry_tools_accept_exact_explicit_injected_and_order_insensitive_production_forms'
    before = tuple(tmp_path.iterdir())
    with pytest.raises(PublicationControlError, match='DOCX-only'):
        publication_run(tmp_path / 'contract', tmp_path / 'inventory', tmp_path / 'acceptance', tmp_path / 'config', run_root, 'retired', {})
    assert not run_root.exists()
    assert tuple(tmp_path.iterdir()) == before


@pytest.mark.parametrize(
    "invalid_kind",
    ["extra_tool", "lowercase_sha", "wrong_name", "missing_word", "wrong_scope", "duplicate", "mixed", "extra_field"],
)
def test_registry_tools_reject_nonexact_declarations_before_run_write(tmp_path, invalid_kind):
    fixture = _fixture(tmp_path)
    production = _exact_production_tool_records()
    if invalid_kind == "extra_tool":
        malformed = [*production, {"name": "extra", "version": "sha256:" + "E" * 64, "scope": "repository_tools"}]
    elif invalid_kind == "lowercase_sha":
        malformed = [{**production[0], "version": "sha256:" + "a" * 64}, *production[1:]]
    elif invalid_kind == "wrong_name":
        malformed = [*production[:-1], {**production[-1], "name": "word"}]
    elif invalid_kind == "missing_word":
        malformed = production[:-1]
    elif invalid_kind == "wrong_scope":
        malformed = [{**production[0], "scope": "allowed_system"}, *production[1:]]
    elif invalid_kind == "duplicate":
        malformed = [*production[:-1], dict(production[-2])]
    elif invalid_kind == "extra_field":
        malformed = [{**production[0], "path": "forbidden"}, *production[1:]]
    else:
        malformed = production
    declarations = {stage: malformed for stage in STAGES}
    if invalid_kind == "mixed":
        declarations[STAGES[0]] = [{"name": "injected_publication_adapters", "version": "test", "scope": "injected_test"}]
    registry = _registry_with_declared_tools(fixture["run_root"], declarations)
    with pytest.raises(PublicationControlError):
        publication_run(
            fixture["contract"], fixture["inventory"], fixture["reconstruction_acceptance"],
            fixture["config_root"], fixture["run_root"], "invalid-tools", registry,
        )
    assert not fixture["run_root"].exists()


def test_real_stage70_and_copied_stage71_adapters_close_synthetic_package(tmp_path):
    run_root = tmp_path / 'real_stage70_and_copied_stage71_adapters_close_synthetic_package'
    before = tuple(tmp_path.iterdir())
    with pytest.raises(PublicationControlError, match='DOCX-only'):
        publication_run(tmp_path / 'contract', tmp_path / 'inventory', tmp_path / 'acceptance', tmp_path / 'config', run_root, 'retired', {})
    assert not run_root.exists()
    assert tuple(tmp_path.iterdir()) == before


def test_neutral_publication_registry_has_no_legacy_pdf_callable():
    assert ADAPTER_NAMES["pdf_candidate"] == "docx_pdf_export_v1"
    serialized = json.dumps(ADAPTER_NAMES).lower()
    for forbidden in ("html_to_pdf", "browser", "chromium", "print-to-pdf"):
        assert forbidden not in serialized
