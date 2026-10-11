from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest

from kb_creator.pipeline import mineru_view_recovery as recovery
from kb_creator.pipeline import mineru_cpu_first
from kb_creator.pipeline import reconstruction
from kb_creator.pipeline.identity import canonical_bytes, file_identity, sha256_bytes
from kb_creator.tests.test_mineru_cpu_packet_b import _full_fixture, _run_adapters


VIEW = "original_pipeline_txt"


def _run_pair(tmp_path: Path) -> tuple[dict, Path, dict, Path]:
    source, contract, runtime, _, _, origin_root = _full_fixture(tmp_path)
    reconstruction.run_engine(contract, source, origin_root, "origin", _run_adapters(origin_root), runtime)
    origin_run = json.loads((origin_root / "run.json").read_text(encoding="utf-8"))
    fresh_root = tmp_path / "fresh"
    fresh_run = reconstruction.write_run(contract, source, fresh_root, "fresh", runtime)
    return origin_run, origin_root / "outputs/02-mineru-three-view", fresh_run, tmp_path / "fresh-stage"


def _compatibility(origin: dict, fresh: dict) -> dict:
    value = {
        "schema": recovery.WRAPPER_COMPATIBILITY_SCHEMA,
        "view_id": VIEW,
        "origin_wrapper": origin["common_tools"]["wrapper"],
        "fresh_wrapper": fresh["common_tools"]["wrapper"],
        "rationale": "Reviewed diagnostic-only wrapper update.",
    }
    value["compatibility_sha256"] = sha256_bytes(canonical_bytes(value))
    return value


def _source_profile_compatibility(origin: dict, fresh: dict) -> dict:
    changed = {
        path: {
            "origin": {"bytes": 10, "sha256": "a" * 64},
            "fresh": {"bytes": 11, "sha256": "b" * 64},
        }
        for path in recovery.ALLOWED_SOURCE_PROFILE_PATHS
    }
    return recovery.source_profile_compatibility_record(origin, fresh, VIEW, changed)


def _reseal_run(run: dict) -> None:
    portable = {key: value for key, value in run.items() if key not in {"local", "portable_identity_sha256"}}
    run["portable_identity_sha256"] = sha256_bytes(canonical_bytes(portable))


def _real_source_pair(tmp_path: Path, origin: dict, fresh: dict, *, third_file: bool = False) -> None:
    for name, run in (("origin", origin), ("fresh", fresh)):
        root = tmp_path / f"{name}-source" / "src" / "mineru"
        for relative, body in (("backend/pipeline/pipeline_analyze.py", b"old"), ("utils/pdf_image_tools.py", b"old"), ("stable.py", b"stable")):
            path = root / relative; path.parent.mkdir(parents=True, exist_ok=True); path.write_bytes(body)
        if name == "fresh":
            (root / "backend/pipeline/pipeline_analyze.py").write_bytes(b"new")
            (root / "utils/pdf_image_tools.py").write_bytes(b"new")
            if third_file: (root / "third.py").write_bytes(b"third")
        run["local"]["mineru_source_root"] = str(root.parent.parent)
        run["provider_profiles"]["pipeline_cpu"]["source"] = {**mineru_cpu_first._source_inventory(root.parent), "version": "3.4.4"}


def _refresh_origin_txt_receipt(origin: dict, stage: Path) -> None:
    descriptor = recovery._descriptor(VIEW)
    _, input_identity = mineru_cpu_first.view_input_identity(origin, descriptor)
    view = stage / "views" / VIEW
    mineru_cpu_first.write_succeeded_view(origin, descriptor, input_identity, view / "artifacts", view / "view.json", {"fixture": "refreshed"})


def test_imports_verified_succeeded_view_with_new_fresh_receipt(tmp_path):
    origin, origin_stage, fresh, fresh_stage = _run_pair(tmp_path)

    result = recovery.import_verified_succeeded_view(origin, origin_stage, fresh, fresh_stage, VIEW)

    receipt = json.loads((fresh_stage / "views" / VIEW / "view.json").read_text(encoding="utf-8"))
    assert result["state"] == "imported"
    assert receipt["run_identity_sha256"] == fresh["portable_identity_sha256"]
    assert receipt["diagnostics"]["mode"] == "imported_verified_success_view"
    assert receipt["diagnostics"]["origin"]["run_identity_sha256"] == origin["portable_identity_sha256"]
    assert receipt["diagnostics"]["origin"]["receipt"]["receipt_sha256"] == result["origin_receipt_sha256"]
    evidence = fresh_stage / receipt["diagnostics"]["origin"]["receipt_evidence"]["path_hint"]
    assert evidence.read_bytes() == (origin_stage / "views" / VIEW / "view.json").read_bytes()
    assert not (fresh_stage / "views" / VIEW / "artifacts/evidence/origin-view.json").exists()
    assert file_identity(fresh_stage / "views" / VIEW / "artifacts/document_content_list.json") == file_identity(origin_stage / "views" / VIEW / "artifacts/document_content_list.json")


def test_wrapper_drift_requires_a_sealed_compatibility_record(tmp_path):
    origin, origin_stage, fresh, fresh_stage = _run_pair(tmp_path)
    fresh = copy.deepcopy(fresh)
    fresh["common_tools"]["wrapper"] = {"bytes": 99, "sha256": "f" * 64}
    _reseal_run(fresh)

    with pytest.raises(recovery.ViewRecoveryError, match="wrapper compatibility"):
        recovery.import_verified_succeeded_view(origin, origin_stage, fresh, fresh_stage, VIEW)

    result = recovery.import_verified_succeeded_view(
        origin, origin_stage, fresh, fresh_stage, VIEW,
        wrapper_compatibility=_compatibility(origin, fresh),
    )
    assert result["wrapper_compatibility"]["fresh_wrapper"] == fresh["common_tools"]["wrapper"]


def test_imports_only_with_sealed_exact_two_file_source_profile_compatibility(tmp_path):
    origin, origin_stage, fresh, fresh_stage = _run_pair(tmp_path)
    fresh = copy.deepcopy(fresh)
    origin = copy.deepcopy(origin)
    _real_source_pair(tmp_path, origin, fresh)
    fresh["capability_snapshot"]["receipt_sha256"] = "c" * 64
    _reseal_run(origin)
    _reseal_run(fresh)
    _refresh_origin_txt_receipt(origin, origin_stage)
    record = recovery.source_profile_compatibility_from_runs(origin, fresh, VIEW)

    result = recovery.import_verified_succeeded_view(
        origin, origin_stage, fresh, fresh_stage, VIEW,
        source_profile_compatibility=record,
    )
    assert result["source_profile_compatibility"]["compatibility_sha256"] == record["compatibility_sha256"]


def test_source_profile_inventory_ignores_cache_but_binds_sealed_source_summary(tmp_path):
    origin, _, fresh, _ = _run_pair(tmp_path)
    origin, fresh = copy.deepcopy(origin), copy.deepcopy(fresh)
    for name, run in (("origin", origin), ("fresh", fresh)):
        root = tmp_path / name / "src" / "mineru"
        for relative, body in (("backend/pipeline/pipeline_analyze.py", b"old"), ("utils/pdf_image_tools.py", b"old"), ("stable.py", b"stable")):
            path = root / relative; path.parent.mkdir(parents=True, exist_ok=True); path.write_bytes(body)
        if name == "fresh":
            (root / "backend/pipeline/pipeline_analyze.py").write_bytes(b"new")
            (root / "utils/pdf_image_tools.py").write_bytes(b"new")
            cache = root / "utils/__pycache__/pdf_image_tools.cpython-312.pyc"; cache.parent.mkdir(parents=True); cache.write_bytes(b"cache")
        run["local"]["mineru_source_root"] = str(root.parent.parent)
        run["provider_profiles"]["pipeline_cpu"]["source"] = {
            **mineru_cpu_first._source_inventory(root.parent), "version": "3.4.4"
        }
    record = recovery.source_profile_compatibility_from_runs(origin, fresh, VIEW)
    assert set(record["changed_sources"]) == set(recovery.ALLOWED_SOURCE_PROFILE_PATHS)


def test_consumer_rejects_live_third_source_file_despite_two_file_record(tmp_path):
    origin, origin_stage, fresh, fresh_stage = _run_pair(tmp_path)
    origin, fresh = copy.deepcopy(origin), copy.deepcopy(fresh)
    _real_source_pair(tmp_path, origin, fresh, third_file=True)
    roots = [Path(run["local"]["mineru_source_root"]) / "src" / "mineru" for run in (origin, fresh)]
    record = recovery.source_profile_compatibility_record(origin, fresh, VIEW, {
        path: {"origin": file_identity(roots[0] / path), "fresh": file_identity(roots[1] / path)}
        for path in recovery.ALLOWED_SOURCE_PROFILE_PATHS
    })
    with pytest.raises(recovery.ViewRecoveryError, match="unapproved source change"):
        recovery.import_verified_succeeded_view(origin, origin_stage, fresh, fresh_stage, VIEW, source_profile_compatibility=record)


@pytest.mark.parametrize("mutation", ("third_file", "model", "lock", "device", "page", "config"))
def test_source_profile_compatibility_rejects_unbound_change(tmp_path, mutation):
    origin, origin_stage, fresh, fresh_stage = _run_pair(tmp_path)
    fresh = copy.deepcopy(fresh)
    fresh["capability_snapshot"]["receipt_sha256"] = "c" * 64
    fresh["provider_profiles"]["pipeline_cpu"]["source"] = {**fresh["provider_profiles"]["pipeline_cpu"]["source"], "file_count": 2, "sha256": "d" * 64}
    _reseal_run(fresh)
    record = _source_profile_compatibility(origin, fresh)
    if mutation == "third_file":
        record["changed_sources"]["third.py"] = record["changed_sources"].pop(recovery.ALLOWED_SOURCE_PROFILE_PATHS[0])
    elif mutation == "model": record["fresh"]["provider_profile"]["model_manifest"]["required_rows"] = 0
    elif mutation == "lock": record["fresh"]["provider_profile"]["lock"]["sha256"] = "e" * 64
    elif mutation == "device": record["fresh"]["provider"]["profile"] = "other"
    elif mutation == "page": record["fresh"]["scope"]["ordered_pages"] = [1]
    else: record["fresh"]["provider_profile"]["config"]["sha256"] = "e" * 64
    record["compatibility_sha256"] = sha256_bytes(canonical_bytes({k: v for k, v in record.items() if k != "compatibility_sha256"}))
    with pytest.raises(recovery.ViewRecoveryError):
        recovery.import_verified_succeeded_view(origin, origin_stage, fresh, fresh_stage, VIEW, source_profile_compatibility=record)


@pytest.mark.parametrize("mutation", ("model", "lock", "device", "config", "launcher", "option", "geometry", "source_version"))
def test_source_profile_compatibility_rejects_actual_fresh_semantic_change(tmp_path, mutation):
    origin, origin_stage, fresh, fresh_stage = _run_pair(tmp_path)
    fresh = copy.deepcopy(fresh)
    fresh["capability_snapshot"]["receipt_sha256"] = "c" * 64
    fresh["provider_profiles"]["pipeline_cpu"]["source"] = {**fresh["provider_profiles"]["pipeline_cpu"]["source"], "file_count": 2, "sha256": "d" * 64}
    if mutation == "model": fresh["provider_profiles"]["pipeline_cpu"]["model_manifest"]["required_rows"] = 0
    elif mutation == "lock": fresh["provider_profiles"]["pipeline_cpu"]["lock"]["sha256"] = "e" * 64
    elif mutation == "device": fresh["capability_snapshot"]["providers"][0]["profile"] = "other"
    elif mutation == "config": fresh["provider_profiles"]["pipeline_cpu"]["config"]["sha256"] = "e" * 64
    elif mutation == "launcher": fresh["provider_profiles"]["pipeline_cpu"]["mineru"]["sha256"] = "e" * 64
    elif mutation == "option": fresh["options"]["raster_dpi"] = 300
    elif mutation == "source_version": fresh["provider_profiles"]["pipeline_cpu"]["source"]["version"] = "unexpected"
    else: fresh["source"]["media_box_points"] = [1, 1]
    _reseal_run(fresh)
    record = _source_profile_compatibility(origin, fresh)
    with pytest.raises(recovery.ViewRecoveryError):
        recovery.import_verified_succeeded_view(origin, origin_stage, fresh, fresh_stage, VIEW, source_profile_compatibility=record)


@pytest.mark.parametrize("mutation", ("artifact", "partial", "profile", "source"))
def test_rejects_tampered_or_non_equivalent_view_import(tmp_path, mutation):
    origin, origin_stage, fresh, fresh_stage = _run_pair(tmp_path)
    if mutation == "artifact":
        (origin_stage / "views" / VIEW / "artifacts/document.md").write_text("tampered", encoding="utf-8")
    elif mutation == "partial":
        (origin_stage / "views" / VIEW / "artifacts/document_layout.pdf").unlink()
    elif mutation == "profile":
        fresh["provider_profiles"]["pipeline_cpu"]["profile"] = "different-profile"
    else:
        fresh["source"] = {**fresh["source"], "sha256": "0" * 64}

    with pytest.raises(recovery.ViewRecoveryError):
        recovery.import_verified_succeeded_view(origin, origin_stage, fresh, fresh_stage, VIEW)


def test_rejects_reparse_origin_artifact_root(tmp_path, monkeypatch):
    origin, origin_stage, fresh, fresh_stage = _run_pair(tmp_path)
    origin_artifacts = origin_stage / "views" / VIEW / "artifacts"
    original = recovery.is_reparse_point
    monkeypatch.setattr(recovery, "is_reparse_point", lambda path: path == origin_artifacts or original(path))

    with pytest.raises(recovery.ViewRecoveryError, match="unsafe"):
        recovery.import_verified_succeeded_view(origin, origin_stage, fresh, fresh_stage, VIEW)


def test_rejects_reparse_path_component_before_copy(tmp_path, monkeypatch):
    origin, origin_stage, fresh, fresh_stage = _run_pair(tmp_path)
    original = recovery.assert_existing_path_components_are_not_reparse

    def reject_origin(path):
        if path == origin_stage / "views" / VIEW / "artifacts":
            raise ValueError("junction")
        return original(path)

    monkeypatch.setattr(recovery, "assert_existing_path_components_are_not_reparse", reject_origin)
    with pytest.raises(recovery.ViewRecoveryError, match="reparse"):
        recovery.import_verified_succeeded_view(origin, origin_stage, fresh, fresh_stage, VIEW)
