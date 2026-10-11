from __future__ import annotations

import copy
import hashlib
import json
import shutil
from pathlib import Path

from PIL import Image
from pypdf import PdfWriter
import pytest

from kb_creator.pipeline.identity import canonical_bytes, file_identity, sha256_bytes
from kb_creator.pipeline.manifests import sealed
from kb_creator.pipeline.publication import PublicationControlError, PublicationStageAdapter, publication_resume, publication_run, record_artifact_acceptance
from kb_creator.pipeline.publication_adapters import (
    PublicationAdapterError,
    PublicationAdapterRuntime,
    _copy_terminology_authorities,
    _materialize_asset_manifest_graph,
    fixed_publication_adapters,
)
from kb_creator.__main__ import main
from kb_creator.scripts import scenario_artview, scenario_master_ru, verify_scenario_master_ru
from kb_creator.scripts.verify_production_package import VerificationError, verify_package
from kb_creator.tests.test_publication_control_plane import _fixture, _write_json
from kb_creator.tests.test_publication_docx_adapter import _config as docx_config


def _identity(path: Path, root: Path) -> dict:
    return {"path": path.relative_to(root).as_posix(), **file_identity(path)}


def _configure(fixture: dict) -> None:
    root = fixture["config_root"]
    image = root / "art.png"; Image.new("RGB", (16, 12), (20, 40, 60)).save(image)
    image_record = {**_identity(image, root), "media_type": "image/png", "dimensions": {"width": 16, "height": 12}}
    graph = root / "artview_graph.json"
    _write_json(graph, {"schema": "synthetic.graph.v1", "artifacts": [
        {"role": "page_context", **_identity(image, root)},
        {"role": "reconstruction_candidate", **_identity(image, root)},
    ]})
    placeholder = _identity(image, root)
    values = {
        "master_en": {
            "schema": "kb_creator.master_en_publication.v3", "scenario_id": "sample", "inputs": {},
            "projection": {"output_name": "MASTER_EN.md", "excluded_source_pages": [], "page_marker_policy": "source_page_comment_v1", "anchor_policy": "preserve_v1", "asset_policy": "copy_markdown_references_v1"},
            "required_qa": ["structure"],
        },
        "master_ru": {"schema": "kb_creator.master_ru_adapter.v1", "max_batch_chars": 3000},
        "artview": {
            "schema": "kb_creator.scenario_artview_profile.v3", "scenario_id": "sample", "output_root": "unused-template-output",
            "inputs": {"master_ru": placeholder, "master_ru_acceptance": placeholder, "master_ru_asset_manifest": placeholder, "reconstruction_inventory": _identity(graph, root)},
            "excluded_source_pages": [],
            "rows": [{
                "asset_id": "map", "anchor": "synthetic", "label": "Карта", "source_page": 1, "group": "maps",
                "current": image_record, "context": image_record,
                "alternatives": [{"candidate_id": "map-alt", "kind": "reconstruction_candidate", "binary": image_record}],
                "presentation_defaults": {"width_percent": 60, "alignment": "center", "wrap_text": False, "wrap_tables": False},
            }],
        },
        "html": {"production_html": {"typography": {"body_font_size": "10pt"}}},
        "docx": docx_config(),
        "pdf": {"schema": "kb_creator.pdf_adapter.v1"},
        "package": {"schema": "kb_creator.package_adapter.v1"},
    }
    records = {}
    for role, value in values.items():
        path = root / f"{role}.json"; _write_json(path, value); records[role] = _identity(path, root)
    terms_csv = root / "shared-terms.csv"
    terms_csv.write_text(
        "source_term,accepted_ru,aliases,bad_ru,domain,status,source_scope,decision_rule,notes\n"
        "Keeper,Хранитель,Хранителя,Ведущий,role,accepted,book,rule,synthetic\n",
        encoding="utf-8",
    )
    terms_md = root / "shared-skills.md"
    terms_md.write_text(
        "| English | Принятый русский термин | Примечание |\n"
        "|---|---|---|\n"
        "| Track | Чтение следов | Не извлекать варианты из примечания. |\n",
        encoding="utf-8",
    )
    terminology_records = [_identity(terms_csv, root), _identity(terms_md, root)]
    fixture["terminology_sources"] = [terms_csv, terms_md]
    contract = json.loads(fixture["contract"].read_text(encoding="utf-8"))
    for row in contract["configs"]: row["file"] = records[row["role"]]
    contract["master_en"]["config"] = records["master_en"]
    contract["master_ru"]["config"] = records["master_ru"]
    contract["master_ru"]["terminology"] = terminology_records
    contract["master_ru"]["required_qa"] = [
        "accepted_master_en_identity",
        "ordered_unit_identity",
        "markdown_structure_preservation",
        "mechanics_preservation",
        "terminology_authority",
        "asset_identity",
        "independent_translation_qa",
    ]
    contract["artview"]["profile"] = records["artview"]
    contract["html"]["config"] = records["html"]
    contract["docx"]["config"] = records["docx"]
    _write_json(fixture["contract"], contract)


def _pdf(path: Path) -> None:
    writer = PdfWriter(); writer.add_blank_page(width=300, height=400)
    with path.open("wb") as stream: writer.write(stream)


def _submission(run_root: Path, master_en_acceptance: Path) -> Path:
    packet = run_root / "outputs" / "20-master-ru-packets" / "artifacts"
    manifest = json.loads((packet / "packet_manifest.json").read_text(encoding="utf-8"))
    batch_root = run_root / "submissions" / "master_ru" / "batches"
    batch_root.mkdir(parents=True)
    for row in manifest["batches"]:
        source = json.loads((packet / row["input"]["path"]).read_text(encoding="utf-8")); translated = copy.deepcopy(source)
        for unit in translated["units"]:
            unit["ru_text"] = unit["source_text"].replace("Reconstructed", "Реконструкция")
        _write_json(batch_root / Path(row["output_path"]).name, translated)
    target = run_root / "submissions" / "master_ru" / "master_ru.submission.json"
    scenario_master_ru.author_submission(packet, batch_root, target, run_root)
    return target


def _accept(run_root: Path, kind: str, evidence: list[Path]) -> Path:
    target = run_root / "acceptance" / f"{kind}.acceptance.json"
    record_artifact_acceptance(run_root, kind, evidence, target, f"explicit synthetic E2E acceptance: {kind}")
    return target


def test_package_terminology_copy_rejects_duplicate_identity_and_drift_before_writes(tmp_path: Path) -> None:
    config_root = tmp_path / "config"; config_root.mkdir()
    authority = config_root / "terms.csv"; authority.write_text("authority\n", encoding="utf-8")
    record = _identity(authority, config_root)
    duplicate_target = tmp_path / "duplicate-target"
    with pytest.raises(PublicationAdapterError, match="duplicate package terminology"):
        _copy_terminology_authorities([record, record], config_root, duplicate_target)
    assert not duplicate_target.exists()

    drifted = dict(record); drifted["sha256"] = "0" * 64
    drift_target = tmp_path / "drift-target"
    with pytest.raises(PublicationAdapterError, match="identity drift"):
        _copy_terminology_authorities([drifted], config_root, drift_target)
    assert not drift_target.exists()


def test_artview_asset_graph_materializes_only_exact_manifest_assets(tmp_path: Path) -> None:
    source = tmp_path / "source"
    asset = source / "assets" / "nested" / "map.png"
    asset.parent.mkdir(parents=True)
    Image.new("RGB", (16, 12), (20, 40, 60)).save(asset)
    unreferenced = source / "assets" / "stale.png"
    Image.new("RGB", (4, 4), (80, 90, 100)).save(unreferenced)
    manifest = source / "ASSET_MANIFEST.json"
    _write_json(manifest, {
        "schema": "kb_creator.master_ru_asset_manifest.v1",
        "scenario_id": "sample",
        "assets": [{"path": "assets/nested/map.png", **file_identity(asset)}],
        "summary": {"total": 1},
    })

    copied_manifest = tmp_path / "authority" / "outputs/21-master-ru-candidate/artifacts/ASSET_MANIFEST.json"
    _materialize_asset_manifest_graph(manifest, copied_manifest)

    copied_asset = copied_manifest.parent / "assets/nested/map.png"
    assert copied_manifest.read_bytes() == manifest.read_bytes()
    assert file_identity(copied_asset) == file_identity(asset)
    assert not (copied_manifest.parent / "assets/stale.png").exists()


@pytest.mark.parametrize("failure", ["stale", "missing_asset", "missing_identity"])
def test_artview_asset_graph_rejects_stale_or_missing_identity_before_materialization(tmp_path: Path, failure: str) -> None:
    source = tmp_path / "source"
    asset = source / "assets" / "map.png"
    asset.parent.mkdir(parents=True)
    Image.new("RGB", (16, 12), (20, 40, 60)).save(asset)
    record = {"path": "assets/map.png", **file_identity(asset)}
    if failure == "stale":
        record["sha256"] = "0" * 64
    elif failure == "missing_asset":
        asset.unlink()
    else:
        del record["sha256"]
    manifest = source / "ASSET_MANIFEST.json"
    _write_json(manifest, {
        "schema": "kb_creator.master_ru_asset_manifest.v1",
        "scenario_id": "sample",
        "assets": [record],
        "summary": {"total": 1},
    })
    copied_manifest = tmp_path / "authority" / "ASSET_MANIFEST.json"

    with pytest.raises(PublicationAdapterError, match="identity drift|asset is missing|lacks exact identity"):
        _materialize_asset_manifest_graph(manifest, copied_manifest)
    assert not copied_manifest.exists()
    assert not (copied_manifest.parent / "assets/map.png").exists()


def test_fixed_real_registry_route_is_retired_before_run_root(tmp_path: Path) -> None:
    run = tmp_path / "legacy-run"
    invoked = []
    registry = {"master_en_candidate": PublicationStageAdapter("old", lambda *_a, **_k: invoked.append(True))}
    with pytest.raises(PublicationControlError, match="DOCX-only"):
        publication_run(tmp_path / "contract", tmp_path / "inventory", tmp_path / "acceptance",
                        tmp_path / "config", run, "old", registry)
    assert not run.exists()
    assert not invoked


def test_stage21_legacy_resume_is_retired_before_evidence_read(tmp_path: Path) -> None:
    run = tmp_path / "legacy-run"
    with pytest.raises(PublicationControlError, match="DOCX-only"):
        publication_resume(run, {"master_en_acceptance": tmp_path / "missing"}, {})
    assert not run.exists()


def test_public_cli_run_is_retired_before_adapter_construction(tmp_path: Path, monkeypatch, capsys) -> None:
    monkeypatch.chdir(tmp_path)
    args = ["publication", "run", "--contract", "missing", "--upstream-inventory", "missing",
            "--reconstruction-acceptance", "missing", "--config-root", "missing",
            "--run-root", "legacy-run", "--tools-root", "missing", "--python", "missing",
            "--powershell", "missing", "--pdftoppm", "missing", "--word", "missing",
            "--run-id", "old"]
    assert main(args) == 2
    error = json.loads(capsys.readouterr().err)
    assert error["state"] == "blocked" and "DOCX-only" in error["error"]
    assert not (tmp_path / "legacy-run").exists()


def test_access_normalization_callback_is_not_reached_by_retired_route(tmp_path: Path, monkeypatch) -> None:
    run = tmp_path / "legacy-run"
    called = []
    monkeypatch.setattr("kb_creator.pipeline.publication.normalize_publication_access_if_managed",
                        lambda *_a, **_k: called.append(True))
    with pytest.raises(PublicationControlError, match="DOCX-only"):
        publication_run(tmp_path / "contract", tmp_path / "inventory", tmp_path / "acceptance",
                        tmp_path / "config", run, "old", {})
    assert not run.exists() and not called


def test_stage10_verifier_is_not_reached_by_retired_route(tmp_path: Path, monkeypatch) -> None:
    run = tmp_path / "legacy-run"
    called = []
    monkeypatch.setattr("kb_creator.pipeline.publication.validate_reconstruction_package",
                        lambda *_a, **_k: called.append(True))
    with pytest.raises(PublicationControlError, match="DOCX-only"):
        publication_run(tmp_path / "contract", tmp_path / "inventory", tmp_path / "acceptance",
                        tmp_path / "config", run, "old", {})
    assert not run.exists() and not called


def test_crlf_source_bytes_remain_unchanged_when_old_writer_is_rejected(tmp_path: Path) -> None:
    source = tmp_path / "MASTER_EN.md"
    source.write_bytes(b"line one\r\nline two\r\n")
    before = source.read_bytes()
    with pytest.raises(PublicationControlError, match="DOCX-only"):
        publication_run(source, tmp_path / "inventory", tmp_path / "acceptance",
                        tmp_path / "config", tmp_path / "legacy-run", "old", {})
    assert source.read_bytes() == before
    assert not (tmp_path / "legacy-run").exists()
