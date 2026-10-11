"""Synthetic sealed v1 publication archive for read-only verifier tests only.

This writes inert historical fixture bytes directly. It never calls a retired
production writer, adapter, rendering engine, or acceptance command.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from kb_creator.pipeline.identity import canonical_bytes, deterministic_inventory, file_identity, sha256_bytes
from kb_creator.pipeline.manifests import sealed
from kb_creator.pipeline.publication import (
    ACCEPTANCE_SCHEMA,
    ACCEPTANCE_STAGE,
    ADAPTER_NAMES,
    MANDATORY_PACKAGE_ROLES,
    PACKAGE_SCHEMA,
    REQUIRED_AUTHORITIES,
    STAGE_SCHEMA,
    STAGES,
    _stage_id,
    verify_production_package,
)
from kb_creator.scripts.verify_production_package import verify_package


def _write(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(canonical_bytes(value) + b"\n")


def _record(path: Path, root: Path) -> dict[str, Any]:
    return {"path": path.relative_to(root).as_posix(), **file_identity(path)}


def build_historical_publication_archive(root: Path) -> Path:
    """Create a minimal, internally sealed archive; caller must verify it."""
    root.mkdir()
    roles = {role: f"roles/{role}.bin" for role in MANDATORY_PACKAGE_ROLES}
    for kind in ("master_en", "master_ru", "artview", "html", "docx", "pdf"):
        roles[f"{kind}_acceptance"] = f"acceptance/{kind}.json"
    roles.update({
        "master_en": "MASTER_EN.md", "master_ru": "MASTER_RU.md",
        "artview_candidate_manifest": "artview/CANDIDATE.json",
        "artview_decisions": "acceptance/artview.decisions.json",
        "html": "document.html", "docx": "document.docx", "pdf": "document.pdf",
        "effective_config": "config/effective.json",
    })
    assert set(roles) == MANDATORY_PACKAGE_ROLES
    assert len(set(roles.values())) == len(roles)
    for role, relative in roles.items():
        if role.endswith("_acceptance") or role == "artview_decisions":
            continue
        path = root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(f"historical fixture {role}\n".encode("utf-8"))
    (root / roles["html"]).write_text("<html><body><p>TEST ARCHIVE</p></body></html>\n", encoding="utf-8")
    config_paths = [root / "configs" / f"{name}.json" for name in
                    ("publication-contract", "source", "language", "artview", "docx")]
    for path in config_paths:
        _write(path, {"fixture": path.stem})
    snapshot_paths = [root / "pipeline" / "schema.json", root / "pipeline" / "verify.py"]
    for path in snapshot_paths:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(f"TEST ARCHIVE {path.name}\n", encoding="utf-8")
    upstream_paths = {name: root / "upstream" / f"{name}.json" for name in
                      ("reconstruction_inventory", "reconstruction_acceptance", "source_identity")}
    for path in upstream_paths.values():
        _write(path, {"fixture": path.stem})
    decisions = sealed("kb_creator.scenario_artview_decisions.v3", {
        "scenario_id": "archive", "state": "accepted",
        "bindings": {name: "A" * 64 for name in (
            "candidate_manifest_sha256", "candidate_files_inventory_sha256", "profile_sha256",
            "master_ru_sha256", "master_ru_acceptance_sha256", "master_ru_asset_manifest_sha256",
            "reconstruction_inventory_sha256")},
        "decisions": [{"asset_id": "synthetic-art", "binary": {"choice": "keep_current", "candidate_id": None},
                       "presentation": {"width_percent": 50, "alignment": "left", "wrap_text": False,
                                        "wrap_tables": False}, "reviewed": True, "notes": "fixture"}],
        "review": {"state": "closed", "reviewed_count": 1, "unresolved_asset_ids": []},
    }, digest_key="decisions_sha256")
    _write(root / roles["artview_decisions"], decisions)
    submission = root / "authorities/master_ru_submission.json"
    _write(submission, {"fixture": True})

    stage_paths: list[Path] = []
    stage_records: list[dict[str, Any]] = []
    upstream: list[dict[str, str]] = []
    acceptances: dict[str, Path] = {}
    producer_role = {"master_en": "master_en", "master_ru": "master_ru",
                     "artview": "artview_candidate_manifest", "html": "html",
                     "docx": "docx", "pdf": "pdf"}
    producer_index = {kind: STAGES.index(stage) for kind, stage in ACCEPTANCE_STAGE.items()}
    common_inputs = [
        {"kind": "publication_contract", "file": _record(config_paths[0], root)},
        {"kind": "accepted_reconstruction", "file": _record(upstream_paths["reconstruction_acceptance"], root)},
    ]
    for index, stage in enumerate(STAGES[:8]):
        inputs = [dict(row) for row in common_inputs]
        for kind in REQUIRED_AUTHORITIES[stage]:
            if kind.endswith("_acceptance"):
                source = acceptances[kind.removesuffix("_acceptance")]
            elif kind == "artview_decisions":
                source = root / roles["artview_decisions"]
            elif kind == "master_ru_submission":
                source = submission
            else:
                raise AssertionError(f"unhandled archive authority: {kind}")
            inputs.append({"kind": kind, "file": _record(source, root)})
        output_role = {0: "master_en", 1: None, 2: "master_ru", 3: "artview_candidate_manifest",
                       4: None, 5: "html", 6: "docx", 7: "pdf"}[index]
        output_file = (root / roles[output_role]) if output_role else submission
        output_files = [_record(output_file, root)]
        reproducible = {
            "stage_id": _stage_id(index), "stage_name": stage, "stage_version": 1,
            "state": "succeeded", "run_identity_sha256": "3" * 64,
            "upstream": list(upstream), "inputs": inputs,
            "adapter": {"logical_name": ADAPTER_NAMES[stage], "version": 1,
                        "script": _record(snapshot_paths[1], root)},
            "effective_config": _record(root / roles["effective_config"], root),
            "tools": [{"name": "injected_publication_adapters", "version": "test", "scope": "injected_test"}],
            "implementation_inventory_sha256": sha256_bytes(canonical_bytes([_record(p, root) for p in snapshot_paths])),
            "outputs": {"root": ".", "files": output_files,
                        "inventory_sha256": sha256_bytes(canonical_bytes(output_files))},
            "evidence": {"root": ".", "files": [],
                         "inventory_sha256": sha256_bytes(canonical_bytes([]))},
        }
        reproducible["cache_key"] = sha256_bytes(canonical_bytes(reproducible))
        stage_value = {"schema": STAGE_SCHEMA, "reproducible": reproducible,
                       "execution": {"started_at_utc": "2026-01-01T00:00:00Z",
                                     "finished_at_utc": "2026-01-01T00:00:01Z", "exit_code": 0,
                                     "structured_diagnostics": {"fixture": "TEST ARCHIVE; no execution"}}}
        stage_value["reproducible_sha256"] = sha256_bytes(canonical_bytes(
            {"schema": STAGE_SCHEMA, "reproducible": reproducible}))
        stage_path = root / "stages" / f"{_stage_id(index)}.json"
        _write(stage_path, stage_value)
        stage_paths.append(stage_path)
        stage_records.append(_record(stage_path, root))
        upstream.append({"stage_id": _stage_id(index), "manifest_sha256": stage_value["reproducible_sha256"]})
        for kind, producer in producer_index.items():
            if producer != index:
                continue
            candidate = root / roles[producer_role[kind]]
            evidence = [_record(root / roles["artview_decisions"], root)] if kind == "artview" else [_record(candidate, root)]
            receipt = sealed(ACCEPTANCE_SCHEMA, {
                "scenario_id": "archive", "artifact_kind": kind, "candidate": _record(candidate, root),
                "producer_stage": _record(stage_path, root), "evidence": evidence,
                "decision": "accepted", "decision_at_utc": "2026-01-01T00:00:00Z",
                "user_decision_reference": "synthetic historical fixture", "recorder_role": "main_orchestrator",
            }, digest_key="receipt_sha256")
            receipt_path = root / roles[f"{kind}_acceptance"]
            _write(receipt_path, receipt)
            acceptances[kind] = receipt_path
    manifest = sealed(PACKAGE_SCHEMA, {
        "scenario_id": "archive", "package_state": "candidate_for_release_review",
        "release_state": "not_reviewed", "publication_run_identity_sha256": "3" * 64,
        "roles": [{"role": role, "path": path} for role, path in sorted(roles.items())],
        "inventory": deterministic_inventory(root),
        "stage_manifests": stage_records,
        "acceptance_receipts": [_record(acceptances[kind], root) for kind in
                                ("master_en", "master_ru", "artview", "html", "docx", "pdf")],
        "config_inventory": [_record(p, root) for p in config_paths],
        "pipeline_snapshot": [_record(p, root) for p in snapshot_paths],
        "upstream": {name: _record(path, root) for name, path in upstream_paths.items()},
    }, digest_key="manifest_sha256")
    _write(root / "PRODUCTION_MANIFEST.json", manifest)
    before = deterministic_inventory(root)
    local = verify_production_package(root)
    offline = verify_package(root)
    assert local["pdf_count"] == offline["pdf_count"] == 1
    assert local["release_state"] == offline["release_state"] == "not_reviewed"
    assert deterministic_inventory(root) == before
    return root
