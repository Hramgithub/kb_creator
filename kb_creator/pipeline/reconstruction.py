from __future__ import annotations

import json
import math
import os
import re
import shutil
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Mapping, Sequence

from . import process as pipeline_process
from . import mineru_cpu_first
from .handout_ledger import page_section
from .identity import (
    assert_existing_path_components_are_not_reparse,
    canonical_bytes,
    deterministic_inventory,
    file_identity,
    implementation_inventory,
    is_reparse_point,
    sha256_bytes,
    sha256_file,
)
from .manifests import is_sha256, sealed, validate_seal


TARGET = "reconstructed_en"
PROFILE = "mineru_three_view_v1"
CONTRACT_SCHEMA = "kb_creator.scenario_reconstruction_contract.v1"
CONTRACT_SCHEMA_V2 = "kb_creator.scenario_reconstruction_contract.v2"
CONTRACT_SCHEMA_V3 = "kb_creator.scenario_reconstruction_contract.v3"
RUN_SCHEMA = "kb_creator.run_spec.v1"
QUEUE_SCHEMA = "kb_creator.review_queue.v1"
DECISION_SET_SCHEMA = "kb_creator.reconstruction_decision_set.v1"
DECISION_SET_V2_SCHEMA = "kb_creator.reconstruction_decision_set.v2"
VALIDATED_SUBMISSION_SCHEMA = "kb_creator.validated_reconstruction_submission.v1"
STAGE_SCHEMA = "kb_creator.stage_manifest.v1"
CAPABILITY_SCHEMA = "nri.mineru_cuda_capability.v1"
SKIP_SCHEMA = "kb_creator.run_skip.v1"
RUN_STAGES = (
    "prepare_inputs",
    "mineru_three_view",
    "compare_views",
    "visual_merge_bundle",
)
RESUME_STAGES = ("fidelity_audit", "materialize_candidate")
ALL_STAGES = RUN_STAGES + RESUME_STAGES
STAGE_SCRIPTS = {
    "prepare_inputs": "kb_creator/scripts/prepare_mineru_three_view_inputs.py",
    "mineru_three_view": "kb_creator/scripts/run_mineru_three_view.ps1",
    "compare_views": "kb_creator/scripts/compare_mineru_three_views.py",
    "visual_merge_bundle": "kb_creator/scripts/build_mineru_visual_merge_bundle.py",
    "fidelity_audit": "kb_creator/scripts/audit_mineru_ai_merge_fidelity.py",
    "materialize_candidate": "kb_creator/scripts/materialize_mineru_ai_merge.py",
}
SAFE_RUN_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$")


class ControlPlaneError(ValueError):
    pass


@dataclass(frozen=True)
class StageAdapter:
    """Test-injectable boundary around one existing command-line adapter."""

    name: str
    invoke: Callable[[Path], Mapping[str, object]]


@dataclass(frozen=True)
class RuntimeOptions:
    mineru_root: Path
    pdftoppm: Path
    powershell: Path
    python: Path = Path(sys.executable)
    raster_dpi: int = 200
    review_dpi: int = 110
    provider_capabilities: Path | None = None
    mineru_source_root: Path | None = None
    ocr_language: str | None = None


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _read(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise ControlPlaneError(f"invalid JSON: {path}") from error
    if not isinstance(value, dict):
        raise ControlPlaneError("JSON root must be an object")
    return value


def _write_json(path: Path, value: object) -> None:
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def _require_exact_keys(
    value: Mapping[str, Any],
    expected: set[str],
    label: str,
) -> None:
    if set(value) != expected:
        raise ControlPlaneError(f"{label} has unexpected or missing fields")


def _validate_page_geometry(rows: object, page_count: int) -> list[dict[str, Any]]:
    if not isinstance(rows, list) or len(rows) != page_count:
        raise ControlPlaneError("source page geometry must cover every page")
    checked: list[dict[str, Any]] = []
    for expected_page, row in enumerate(rows, 1):
        if not isinstance(row, dict) or set(row) != {"source_page", "media_box_coordinates", "crop_box_coordinates", "rotation_degrees", "user_unit"}:
            raise ControlPlaneError("invalid source page geometry row")
        if type(row["source_page"]) is not int or row["source_page"] != expected_page or type(row["rotation_degrees"]) is not int or row["rotation_degrees"] not in (0, 90, 180, 270) or isinstance(row["user_unit"], bool) or row["user_unit"] != 1.0:
            raise ControlPlaneError("invalid source page geometry authority")
        for key in ("media_box_coordinates", "crop_box_coordinates"):
            box = row[key]
            if not isinstance(box, list) or len(box) != 4 or any(not isinstance(item, (int, float)) or isinstance(item, bool) or not math.isfinite(item) for item in box) or box[2] <= box[0] or box[3] <= box[1]:
                raise ControlPlaneError("invalid source page box")
        media, crop = row["media_box_coordinates"], row["crop_box_coordinates"]
        if crop[0] < media[0] or crop[1] < media[1] or crop[2] > media[2] or crop[3] > media[3]:
            raise ControlPlaneError("CropBox escapes MediaBox")
        checked.append(row)
    return checked


def validate_contract(value: dict[str, Any]) -> dict[str, Any]:
    _require_exact_keys(
        value,
        {
            "schema",
            "contract_revision",
            "scenario",
            "source",
            "scope",
            "page_roles",
            "reconstruction",
            "acceptance",
        },
        "reconstruction contract",
    )
    revision = value.get("contract_revision")
    if type(revision) is not int or (value.get("schema"), revision) not in {(CONTRACT_SCHEMA, 1), (CONTRACT_SCHEMA_V2, 2), (CONTRACT_SCHEMA_V3, 3)}:
        raise ControlPlaneError("unsupported reconstruction contract")
    scenario = value.get("scenario")
    if not isinstance(scenario, dict):
        raise ControlPlaneError("invalid scenario")
    _require_exact_keys(scenario, {"id", "title"}, "scenario")
    if not isinstance(scenario["id"], str) or not re.fullmatch(
        r"[a-z0-9]+(?:-[a-z0-9]+)*", scenario["id"]
    ):
        raise ControlPlaneError("invalid scenario id")
    if not isinstance(scenario["title"], str) or not scenario["title"].strip():
        raise ControlPlaneError("invalid scenario title")

    source = value.get("source")
    if not isinstance(source, dict):
        raise ControlPlaneError("invalid source identity")
    scalar_source_keys = {"sha256", "byte_count", "page_count", "media_box_points", "rotation_degrees"}
    geometry_source_keys = {"sha256", "byte_count", "page_count", "page_geometry"}
    expected_source_keys = scalar_source_keys if revision == 1 else geometry_source_keys if revision == 2 else None
    if revision == 3 and set(source) != scalar_source_keys and set(source) != geometry_source_keys:
        raise ControlPlaneError("v3 source must use exactly one geometry authority")
    if expected_source_keys is not None:
        _require_exact_keys(source, expected_source_keys, "source identity")
    if not is_sha256(source["sha256"]):
        raise ControlPlaneError("invalid source hash")
    if type(source["byte_count"]) is not int or source["byte_count"] < 1:
        raise ControlPlaneError("invalid source byte count")
    if type(source["page_count"]) is not int or source["page_count"] < 1:
        raise ControlPlaneError("invalid source page count")
    if "media_box_points" in source:
        geometry = source["media_box_points"]
        if not isinstance(geometry, list) or len(geometry) != 2 or any(not isinstance(item, (int, float)) or isinstance(item, bool) or not math.isfinite(item) or item <= 0 for item in geometry):
            raise ControlPlaneError("invalid source MediaBox")
        if type(source["rotation_degrees"]) is not int or source["rotation_degrees"] not in (0, 90, 180, 270):
            raise ControlPlaneError("invalid source rotation")
    else:
        _validate_page_geometry(source["page_geometry"], source["page_count"])

    scope = value.get("scope")
    if not isinstance(scope, dict):
        raise ControlPlaneError("invalid scope")
    _require_exact_keys(
        scope,
        {"mode", "first_page", "last_page", "required_entities"},
        "scope",
    )
    entities = scope["required_entities"]
    if not isinstance(entities, dict):
        raise ControlPlaneError("invalid required entities")
    _require_exact_keys(entities, {"numbered_player_handouts"} if revision < 3 else {"handout_label_sets"}, "required entities")
    if revision == 3:
        sets = entities["handout_label_sets"]
        if not isinstance(sets, list) or not sets:
            raise ControlPlaneError("handout label sets are required")
        seen_scopes, seen_occurrences = set(), set()
        previous_scope = None
        for group in sets:
            if not isinstance(group, dict) or set(group) != {"scope_id", "labels"} or not isinstance(group["scope_id"], str) or not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", group["scope_id"]) or group["scope_id"] in seen_scopes or not isinstance(group["labels"], list) or not group["labels"]:
                raise ControlPlaneError("invalid handout label set")
            if previous_scope is not None and group["scope_id"] <= previous_scope:
                raise ControlPlaneError("handout label sets must be deterministically ordered")
            seen_scopes.add(group["scope_id"])
            previous_scope = group["scope_id"]
            previous_label = None
            for item in group["labels"]:
                if not isinstance(item, dict) or set(item) != {"label", "occurrences"} or not isinstance(item["label"], str) or not re.fullmatch(r"(?:[A-Z]|[1-9]\d*)", item["label"]) or not isinstance(item["occurrences"], list) or not item["occurrences"]:
                    raise ControlPlaneError("invalid handout label authority")
                key = (group["scope_id"], item["label"])
                if previous_label is not None and item["label"] <= previous_label:
                    raise ControlPlaneError("handout labels must be deterministically ordered")
                previous_label = item["label"]
                previous_occurrence = None
                for occurrence in item["occurrences"]:
                    if not isinstance(occurrence, dict) or set(occurrence) != {"source_page", "section"} or type(occurrence["source_page"]) is not int or not 1 <= occurrence["source_page"] <= source["page_count"] or occurrence["section"] not in {"body", "appendix"}:
                        raise ControlPlaneError("invalid handout occurrence")
                    row = (*key, occurrence["source_page"])
                    if row in seen_occurrences: raise ControlPlaneError("duplicate handout occurrence")
                    order = (occurrence["source_page"], occurrence["section"])
                    if previous_occurrence is not None and order <= previous_occurrence:
                        raise ControlPlaneError("handout occurrences must be deterministically ordered")
                    previous_occurrence = order
                    seen_occurrences.add(row)
    if (
        scope["mode"] != "all_source_pages"
        or scope["first_page"] != 1
        or scope["last_page"] != source["page_count"]
        or (revision < 3 and not isinstance(entities["numbered_player_handouts"], int))
        or (revision < 3 and (isinstance(entities["numbered_player_handouts"], bool) or entities["numbered_player_handouts"] < 0))
    ):
        raise ControlPlaneError("scope must exactly cover the source")

    roles = value.get("page_roles")
    if not isinstance(roles, list) or not roles:
        raise ControlPlaneError("page roles are required")
    expected_page = 1
    allowed_modes = {"text", "mixed", "visual", "unknown"}
    allowed_strategies = {
        "embedded_text",
        "reading_order",
        "ocr_region",
        "visual_preserve",
    }
    for row in roles:
        if not isinstance(row, dict):
            raise ControlPlaneError("invalid page role")
        _require_exact_keys(
            row,
            {
                "role",
                "first_page",
                "last_page",
                "content_mode",
                "traits",
                "strategies",
            },
            "page role",
        )
        if (
            not isinstance(row["role"], str)
            or not row["role"]
            or row["first_page"] != expected_page
            or not isinstance(row["last_page"], int)
            or row["last_page"] < expected_page
            or row["content_mode"] not in allowed_modes
            or not isinstance(row["traits"], list)
            or any(not isinstance(item, str) for item in row["traits"])
            or len(row["traits"]) != len(set(row["traits"]))
            or not isinstance(row["strategies"], list)
            or not row["strategies"]
            or len(row["strategies"]) != len(set(row["strategies"]))
            or not set(row["strategies"]).issubset(allowed_strategies)
        ):
            raise ControlPlaneError("invalid or non-contiguous page role")
        expected_page = row["last_page"] + 1
    if expected_page != source["page_count"] + 1:
        raise ControlPlaneError("page roles do not cover the source")
    if revision == 3:
        for group in entities["handout_label_sets"]:
            for label in group["labels"]:
                for occurrence in label["occurrences"]:
                    try:
                        actual_section = page_section(value, occurrence["source_page"])
                    except ValueError as error:
                        raise ControlPlaneError(str(error)) from error
                    if occurrence["section"] != actual_section:
                        raise ControlPlaneError("handout occurrence section disagrees with source page role")

    reconstruction = value.get("reconstruction")
    if not isinstance(reconstruction, dict):
        raise ControlPlaneError("invalid reconstruction policy")
    _require_exact_keys(
        reconstruction,
        {"strategies", "required_review"},
        "reconstruction",
    )
    if (
        reconstruction["required_review"] is not True
        or not isinstance(reconstruction["strategies"], list)
        or not reconstruction["strategies"]
        or len(reconstruction["strategies"]) != len(set(reconstruction["strategies"]))
        or not set(reconstruction["strategies"]).issubset(allowed_strategies)
    ):
        raise ControlPlaneError("invalid reconstruction policy")
    acceptance = value.get("acceptance")
    if not isinstance(acceptance, dict):
        raise ControlPlaneError("invalid reconstruction acceptance")
    _require_exact_keys(acceptance, {"approval_authority"}, "acceptance")
    if acceptance["approval_authority"] != "configured_reconstruction_review":
        raise ControlPlaneError("invalid reconstruction approval authority")
    return value


def load_contract(path: Path) -> tuple[dict[str, Any], str]:
    data = validate_contract(_read(path))
    return data, sha256_bytes(canonical_bytes(data))


def _safe_new_root(path: Path) -> None:
    if path.exists():
        raise ControlPlaneError("run root must be absent")
    parent = path.parent
    if not parent.is_dir():
        raise ControlPlaneError("run root parent must exist")
    try:
        assert_existing_path_components_are_not_reparse(parent)
    except ValueError as error:
        raise ControlPlaneError(str(error)) from error


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _implementation_paths() -> list[Path]:
    repo = _repo_root()
    return [
        repo / "kb_creator" / "__main__.py",
        repo / "kb_creator" / "pipeline" / "identity.py",
        repo / "kb_creator" / "pipeline" / "process.py",
        repo / "kb_creator" / "pipeline" / "windows_process_tree.py",
        repo / "kb_creator" / "pipeline" / "manifests.py",
        repo / "kb_creator" / "pipeline" / "reconstruction.py",
        repo / "kb_creator" / "pipeline" / "mineru_cpu_first.py",
        repo / "kb_creator" / "pipeline" / "mineru_view_recovery.py",
        repo / "kb_creator" / "pipeline" / "mineru_view_recovery_plan.py",
        repo / "kb_creator" / "pipeline" / "reconstruction_promotion.py",
        repo / "kb_creator" / "pipeline" / "handout_ledger.py",
        repo / "kb_creator" / "contracts" / "reconstruction_upstream_inventory.v1.schema.json",
        repo / "kb_creator" / "contracts" / "reconstruction_upstream_manifest.v1.schema.json",
        repo / "kb_creator" / "contracts" / "reconstruction_source_identity.v1.schema.json",
        repo / "kb_creator" / "contracts" / "reconstruction_source_identity.v2.schema.json",
        repo / "kb_creator" / "contracts" / "reconstruction_source_identity.v3.schema.json",
        repo / "kb_creator" / "contracts" / "scenario_reconstruction_contract.v2.schema.json",
        repo / "kb_creator" / "contracts" / "scenario_reconstruction_contract.v3.schema.json",
        repo / "kb_creator" / "contracts" / "run_spec.v3.schema.json",
        repo / "kb_creator" / "contracts" / "run_spec.v4.schema.json",
        repo / "kb_creator" / "contracts" / "mineru_three_view_inputs.v3.schema.json",
        repo / "kb_creator" / "contracts" / "artifact_acceptance.v1.schema.json",
        repo / "kb_creator" / "contracts" / "run_spec.v2.schema.json",
        repo / "kb_creator" / "contracts" / "mineru_view_execution.v1.schema.json",
        repo / "kb_creator" / "contracts" / "mineru_view_set.v1.schema.json",
        repo / "kb_creator" / "contracts" / "mineru_multi_view_comparison.v2.schema.json",
        repo / "kb_creator" / "contracts" / "mineru_three_view_inputs.v2.schema.json",
        repo / "kb_creator" / "contracts" / "mineru_geometry_plan.v1.schema.json",
        repo / "kb_creator" / "contracts" / "mineru_visual_merge_bundle.v2.schema.json",
        repo / "kb_creator" / "contracts" / "mineru_geometry_failure.v1.schema.json",
        repo / "kb_creator" / "contracts" / "ai_merge_fidelity_audit.v2.schema.json",
        repo / "kb_creator" / "contracts" / "ai_merge_fidelity_reviewed_allowlist.v2.schema.json",
        repo / "kb_creator" / "scripts" / "prepare_mineru_three_view_inputs.py",
        repo / "kb_creator" / "scripts" / "run_mineru_three_view.ps1",
        repo / "kb_creator" / "scripts" / "compare_mineru_three_views.py",
        repo / "kb_creator" / "scripts" / "build_mineru_visual_merge_bundle.py",
        repo / "kb_creator" / "scripts" / "audit_mineru_ai_merge_fidelity.py",
        repo / "kb_creator" / "scripts" / "materialize_mineru_ai_merge.py",
        repo / "MinerU" / "scripts" / "probe-capability.ps1",
    ]


def _runtime_capability(runtime: RuntimeOptions | None) -> dict[str, Any]:
    if runtime is None:
        return {
            "schema": CAPABILITY_SCHEMA,
            "state": "injected",
            "reason_code": "injected_adapters",
            "receipt": None,
        }
    receipt_path = (runtime.mineru_root / "capability.json").resolve()
    if not receipt_path.is_file():
        raise ControlPlaneError(
            f"MinerU CUDA capability receipt is missing: {receipt_path}"
        )
    receipt = _read(receipt_path)
    _require_exact_keys(
        receipt,
        {
            "schema",
            "capability",
            "state",
            "reason_code",
            "checked_at_utc",
            "probe",
        },
        "MinerU CUDA capability receipt",
    )
    state = receipt.get("state")
    reason_code = receipt.get("reason_code")
    if (
        receipt.get("schema") != CAPABILITY_SCHEMA
        or receipt.get("capability") != "mineru_cuda"
        or state not in {"available", "unavailable"}
        or not isinstance(reason_code, str)
        or not reason_code
        or not isinstance(receipt.get("checked_at_utc"), str)
        or not isinstance(receipt.get("probe"), dict)
    ):
        raise ControlPlaneError("invalid MinerU CUDA capability receipt")
    return {
        "schema": CAPABILITY_SCHEMA,
        "state": state,
        "reason_code": reason_code,
        "receipt": {
            "path_hint": receipt_path.name,
            **file_identity(receipt_path),
        },
    }


def _runtime_toolchain(
    runtime: RuntimeOptions | None,
    capability: Mapping[str, Any] | None = None,
) -> tuple[list[dict[str, Any]], dict[str, str]]:
    if runtime is None:
        return ([{"name": "injected_adapters", "version": "test"}], {})
    capability = capability or _runtime_capability(runtime)
    if capability.get("state") == "unavailable":
        return [], {}
    if capability.get("state") != "available":
        raise ControlPlaneError("invalid runtime capability state")
    paths = {
        "python": runtime.python.resolve(),
        "powershell": runtime.powershell.resolve(),
        "pdftoppm": runtime.pdftoppm.resolve(),
        "mineru": (
            runtime.mineru_root / ".venv" / "Scripts" / "mineru.exe"
        ).resolve(),
        "mineru_initialize": (
            _repo_root() / "MinerU" / "scripts" / "initialize.ps1"
        ).resolve(),
    }
    records = []
    for name, path in paths.items():
        if not path.is_file():
            raise ControlPlaneError(f"required tool is missing: {name}: {path}")
        records.append({"name": name, "path_hint": path.name, **file_identity(path)})
    return records, {name: str(path) for name, path in paths.items()}


def _source_pdf_geometry(source_path: Path) -> dict[str, Any]:
    try:
        from pypdf import PdfReader
    except ImportError as error:  # pragma: no cover - host dependency boundary
        raise ControlPlaneError("pypdf is required for source preflight") from error
    try:
        reader = PdfReader(str(source_path))
    except Exception as error:
        raise ControlPlaneError("source is not a readable PDF") from error
    if not reader.pages:
        raise ControlPlaneError("source PDF has no pages")
    rows = []
    for number, page in enumerate(reader.pages, 1):
        media, crop = page.mediabox, page.cropbox
        raw_rotation = float(page.get("/Rotate", 0))
        if not math.isfinite(raw_rotation) or not raw_rotation.is_integer():
            raise ControlPlaneError("source rotation must be an integer right angle")
        row = {"source_page": number,
               "media_box_coordinates": [float(media.left), float(media.bottom), float(media.right), float(media.top)],
               "crop_box_coordinates": [float(crop.left), float(crop.bottom), float(crop.right), float(crop.top)],
               "rotation_degrees": int(raw_rotation) % 360,
               "user_unit": float(page.get("/UserUnit", 1))}
        rows.append(row)
    _validate_page_geometry(rows, len(reader.pages))
    uniform = all({key: value for key, value in row.items() if key != "source_page"} == {key: value for key, value in rows[0].items() if key != "source_page"} for row in rows[1:])
    if uniform:
        first = rows[0]
        return {"page_count": len(rows), "media_box_points": [first["media_box_coordinates"][2] - first["media_box_coordinates"][0], first["media_box_coordinates"][3] - first["media_box_coordinates"][1]], "rotation_degrees": first["rotation_degrees"]}
    return {"page_count": len(rows), "page_geometry": rows}


def preflight(
    contract_path: Path,
    source_path: Path,
    run_root: Path,
    target: str = TARGET,
    runtime: RuntimeOptions | None = None,
) -> dict[str, Any]:
    if target != TARGET:
        raise ControlPlaneError("unsupported target")
    contract, contract_sha = load_contract(contract_path)
    if not source_path.is_file():
        raise ControlPlaneError("source is not a file")
    observed = file_identity(source_path)
    source = contract["source"]
    if observed != {"bytes": source["byte_count"], "sha256": source["sha256"]}:
        raise ControlPlaneError("source identity mismatch")
    geometry = _source_pdf_geometry(source_path)
    expected_geometry = {"page_count": source["page_count"]}
    if "media_box_points" in source:
        expected_geometry.update(media_box_points=[float(item) for item in source["media_box_points"]], rotation_degrees=source["rotation_degrees"])
    else:
        expected_geometry["page_geometry"] = source["page_geometry"]
    if geometry != expected_geometry:
        raise ControlPlaneError("source page geometry does not match contract")
    _safe_new_root(run_root)
    cpu_first_values = (
        runtime.provider_capabilities if runtime is not None else None,
        runtime.mineru_source_root if runtime is not None else None,
        runtime.ocr_language if runtime is not None else None,
    )
    if any(value is not None for value in cpu_first_values) and not all(
        value is not None for value in cpu_first_values
    ):
        raise ControlPlaneError(
            "CPU-first dispatch requires provider capabilities, MinerU source root, and explicit ocr_language together"
        )
    if runtime is not None and all(value is not None for value in cpu_first_values):
        if runtime.ocr_language not in mineru_cpu_first.OCR_LANGUAGES:
            raise ControlPlaneError("CPU-first RunSpec requires an explicit closed ocr_language")
        try:
            snapshot, _ = mineru_cpu_first.build_runtime_snapshot(runtime)
        except mineru_cpu_first.CpuFirstContractError as error:
            raise ControlPlaneError(str(error)) from error
        return {
            "schema": "kb_creator.preflight.v2",
            "state": "ready",
            "target": TARGET,
            "contract_sha256": contract_sha,
            "source": observed,
            "source_geometry": geometry,
            **snapshot,
        }
    capability = _runtime_capability(runtime)
    toolchain, _ = _runtime_toolchain(runtime, capability)
    return {
        "schema": "kb_creator.preflight.v1",
        "state": (
            "ready" if capability["state"] != "unavailable" else "skipped"
        ),
        "target": TARGET,
        "contract_sha256": contract_sha,
        "source": observed,
        "source_geometry": geometry,
        "capability": capability,
        "toolchain": toolchain,
    }


def build_run_spec(
    contract_path: Path,
    source_path: Path,
    run_root: Path,
    run_id: str,
    runtime: RuntimeOptions | None = None,
) -> dict[str, Any]:
    if not SAFE_RUN_ID.fullmatch(run_id):
        raise ControlPlaneError("invalid run id")
    ready = preflight(contract_path, source_path, run_root, runtime=runtime)
    contract, contract_sha = load_contract(contract_path)
    implementation = implementation_inventory(_repo_root(), _implementation_paths())
    if contract["contract_revision"] >= 2 and ready["schema"] != "kb_creator.preflight.v2":
        raise ControlPlaneError("contract revision requires the CPU-first profile")
    if ready["schema"] == "kb_creator.preflight.v2":
        if runtime is None:
            raise ControlPlaneError("CPU-first runtime is missing")
        second_snapshot, local_runtime = mineru_cpu_first.build_runtime_snapshot(runtime)
        if second_snapshot != {
            "capability_snapshot": ready["capability_snapshot"],
            "provider_profiles": ready["provider_profiles"],
            "common_tools": ready["common_tools"],
        }:
            raise ControlPlaneError("CPU-first runtime evidence changed during preflight")
        portable: dict[str, Any] = {
            "schema": (
                mineru_cpu_first.RUN_SCHEMA_V4
                if contract["contract_revision"] == 3
                else mineru_cpu_first.RUN_SCHEMA_V3
                if contract["contract_revision"] == 2
                else mineru_cpu_first.RUN_SCHEMA
            ),
            "run_id": run_id,
            "target": TARGET,
            "profile": mineru_cpu_first.PROFILE,
            "contract": {
                "path_hint": contract_path.name,
                "bytes": len(canonical_bytes(contract)),
                "sha256": contract_sha,
                "contract_revision": contract["contract_revision"],
            },
            "source": {
                "path_hint": source_path.name,
                **ready["source"],
                "page_count": contract["source"]["page_count"],
                **({"page_geometry": contract["source"]["page_geometry"]} if "page_geometry" in contract["source"] else {"media_box_points": contract["source"]["media_box_points"], "rotation_degrees": contract["source"]["rotation_degrees"]}),
            },
            "scope": {"ordered_pages": list(range(1, contract["source"]["page_count"] + 1))},
            "options": {
                "raster_dpi": runtime.raster_dpi,
                "review_dpi": runtime.review_dpi,
                "ocr_language": runtime.ocr_language,
                "source_box": "MediaBox",
                "geometry_policy": "source_displayed_mediabox_v1",
                "geometry_dimension_tolerance_points": "0.001",
                "geometry_relative_aspect_tolerance": "0.000005",
                "geometry_pixel_tolerance": 0,
                "geometry_rounding_rule": "ceil(points*dpi/72)",
                "geometry_renderer_recipe": "pdftoppm-mediabox-png-v1",
                "cache_mode": "run_local_verified",
                "processing_window_size": 1,
                "api_max_concurrent_requests": 1,
            },
            "execution_boundary": {
                "mode": "current_station_local_only",
                "remote_endpoints_allowed": False,
                "external_services_allowed": False,
                "user_executable_allowed": False,
            },
            "view_plan": list(mineru_cpu_first.VIEW_PLAN),
            "capability_snapshot": ready["capability_snapshot"],
            "provider_profiles": ready["provider_profiles"],
            "common_tools": ready["common_tools"],
            "toolchain": [
                {"name": name, **identity}
                for name, identity in sorted(ready["common_tools"].items())
            ],
            "implementation": implementation,
        }
        portable["portable_identity_sha256"] = sha256_bytes(canonical_bytes(portable))
        return {
            **portable,
            "local": {
                "contract_path": str(contract_path.resolve()),
                "source_path": str(source_path.resolve()),
                "run_root": str(run_root.resolve()),
                "mineru_root": str(runtime.mineru_root.resolve()),
                **local_runtime,
            },
        }
    _, executable_paths = _runtime_toolchain(runtime, ready["capability"])
    portable: dict[str, Any] = {
        "schema": RUN_SCHEMA,
        "run_id": run_id,
        "target": TARGET,
        "profile": PROFILE,
        "contract": {
            "path_hint": contract_path.name,
            "bytes": len(canonical_bytes(contract)),
            "sha256": contract_sha,
            "contract_revision": 1,
        },
        "source": {
            "path_hint": source_path.name,
            **ready["source"],
            "page_count": contract["source"]["page_count"],
            "media_box_points": contract["source"]["media_box_points"],
            "rotation_degrees": contract["source"]["rotation_degrees"],
        },
        "scope": {
            "ordered_pages": list(range(1, contract["source"]["page_count"] + 1))
        },
        "options": {
            "raster_dpi": runtime.raster_dpi if runtime else 200,
            "review_dpi": runtime.review_dpi if runtime else 110,
            "mineru_profiles": ["hybrid_high", "pipeline_ocr", "hybrid_high"],
            "source_box": "MediaBox",
            "cache_mode": "run_local_verified",
        },
        "capability": ready["capability"],
        "toolchain": ready["toolchain"],
        "implementation": implementation,
    }
    portable["portable_identity_sha256"] = sha256_bytes(canonical_bytes(portable))
    return {
        **portable,
        "local": {
            "contract_path": str(contract_path.resolve()),
            "source_path": str(source_path.resolve()),
            "run_root": str(run_root.resolve()),
            "mineru_root": str(runtime.mineru_root.resolve()) if runtime else None,
            "executable_paths": executable_paths,
        },
    }


def write_run(
    contract_path: Path,
    source_path: Path,
    run_root: Path,
    run_id: str,
    runtime: RuntimeOptions | None = None,
) -> dict[str, Any]:
    spec = build_run_spec(contract_path, source_path, run_root, run_id, runtime)
    run_root.mkdir(parents=False)
    _write_json(run_root / "run.json", spec)
    return spec


def _portable_run_fields(run: Mapping[str, Any]) -> dict[str, Any]:
    return {
        key: value
        for key, value in run.items()
        if key not in {"local", "portable_identity_sha256"}
    }


def load_run(run_root: Path) -> dict[str, Any]:
    data = _read(run_root / "run.json")
    if data.get("schema") in mineru_cpu_first.RUN_SCHEMAS:
        expected_v2 = {
            "schema",
            "run_id",
            "target",
            "profile",
            "contract",
            "source",
            "scope",
            "options",
            "execution_boundary",
            "view_plan",
            "capability_snapshot",
            "provider_profiles",
            "common_tools",
            "toolchain",
            "implementation",
            "portable_identity_sha256",
            "local",
        }
        _require_exact_keys(data, expected_v2, "CPU-first run spec")
        revision = (
            3 if data["schema"] == mineru_cpu_first.RUN_SCHEMA_V4
            else 2 if data["schema"] == mineru_cpu_first.RUN_SCHEMA_V3
            else 1
        )
        if data.get("contract", {}).get("contract_revision") != revision:
            raise ControlPlaneError("run schema and contract revision mismatch")
        source = data["source"]
        keys = {"path_hint", "bytes", "sha256", "page_count"} | ({"page_geometry"} if "page_geometry" in source else {"media_box_points", "rotation_degrees"})
        _require_exact_keys(source, keys, "CPU-first source")
        if "page_geometry" in source:
            _validate_page_geometry(source["page_geometry"], source["page_count"])
        if data["scope"].get("ordered_pages") != list(range(1, source["page_count"] + 1)):
            raise ControlPlaneError("run source page coverage mismatch")
        try:
            mineru_cpu_first.validate_view_plan(data["view_plan"])
        except mineru_cpu_first.CpuFirstContractError as error:
            raise ControlPlaneError(str(error)) from error
        if data.get("profile") != mineru_cpu_first.PROFILE or data.get("target") != TARGET:
            raise ControlPlaneError("invalid CPU-first run spec")
        if data.get("options") != {
            "raster_dpi": data.get("options", {}).get("raster_dpi"),
            "review_dpi": data.get("options", {}).get("review_dpi"),
            "ocr_language": data.get("options", {}).get("ocr_language"),
            "source_box": "MediaBox",
            "geometry_policy": "source_displayed_mediabox_v1",
            "geometry_dimension_tolerance_points": "0.001",
            "geometry_relative_aspect_tolerance": "0.000005",
            "geometry_pixel_tolerance": 0,
            "geometry_rounding_rule": "ceil(points*dpi/72)",
            "geometry_renderer_recipe": "pdftoppm-mediabox-png-v1",
            "cache_mode": "run_local_verified",
            "processing_window_size": 1,
            "api_max_concurrent_requests": 1,
        }:
            raise ControlPlaneError("invalid CPU-first geometry/execution options")
        boundary = data.get("execution_boundary")
        if boundary != {
            "mode": "current_station_local_only",
            "remote_endpoints_allowed": False,
            "external_services_allowed": False,
            "user_executable_allowed": False,
        }:
            raise ControlPlaneError("invalid CPU-first execution boundary")
        if sha256_bytes(canonical_bytes(_portable_run_fields(data))) != data["portable_identity_sha256"]:
            raise ControlPlaneError("run spec identity mismatch")
        return data
    expected = {
        "schema",
        "run_id",
        "target",
        "profile",
        "contract",
        "source",
        "scope",
        "options",
        "capability",
        "toolchain",
        "implementation",
        "portable_identity_sha256",
        "local",
    }
    _require_exact_keys(data, expected, "run spec")
    if (
        data["schema"] != RUN_SCHEMA
        or data["target"] != TARGET
        or data["profile"] != PROFILE
    ):
        raise ControlPlaneError("invalid run spec")
    if (
        sha256_bytes(canonical_bytes(_portable_run_fields(data)))
        != data["portable_identity_sha256"]
    ):
        raise ControlPlaneError("run spec identity mismatch")
    return data


def _validate_live_cpu_first_bindings(
    run_root: Path,
    run: dict[str, Any],
) -> tuple[Path, Path, dict[str, Any]]:
    local = run.get("local")
    if not isinstance(local, dict):
        raise ControlPlaneError("invalid CPU-first local bindings")
    _require_exact_keys(
        local,
        {
            "contract_path",
            "source_path",
            "run_root",
            "mineru_root",
            "provider_capabilities_path",
            "mineru_source_root",
            "profile_paths",
            "common_paths",
        },
        "CPU-first local bindings",
    )
    try:
        actual_root = run_root.resolve()
        assert_existing_path_components_are_not_reparse(actual_root)
    except (OSError, ValueError) as error:
        raise ControlPlaneError(str(error)) from error
    if Path(str(local["run_root"])).resolve() != actual_root:
        raise ControlPlaneError("local run root binding mismatch")
    contract_path = Path(str(local["contract_path"]))
    source_path = Path(str(local["source_path"]))
    contract, contract_sha = load_contract(contract_path)
    if contract_sha != run["contract"]["sha256"]:
        raise ControlPlaneError("stale contract")
    if file_identity(source_path) != {"bytes": run["source"]["bytes"], "sha256": run["source"]["sha256"]}:
        raise ControlPlaneError("stale source")
    if implementation_inventory(_repo_root(), _implementation_paths()) != run["implementation"]:
        raise ControlPlaneError("stale implementation")
    capability = run.get("capability_snapshot")
    if not isinstance(capability, dict) or capability.get("provider_receipt", {}).get("providers") != capability.get("providers") or capability.get("provider_receipt", {}).get("receipt_sha256") != capability.get("receipt_sha256"):
        raise ControlPlaneError("invalid frozen provider capability snapshot")
    try:
        mineru_cpu_first._lower_seal(capability["provider_receipt"], "receipt_sha256", sorted_keys=False)
        mineru_cpu_first.validate_view_plan(run["view_plan"])
        source_root = Path(str(local["mineru_source_root"])).resolve()
        mineru_root = Path(str(local["mineru_root"])).resolve()
        current_profiles: dict[str, Any] = {}
        expected_local_profiles: dict[str, Any] = {}
        for provider in capability["providers"]:
            if provider["state"] != "ready":
                continue
            snapshot, paths = mineru_cpu_first._validate_profile(provider, mineru_root, source_root)
            current_profiles[provider["provider_id"]] = snapshot
            expected_local_profiles[provider["provider_id"]] = paths
        if current_profiles != run["provider_profiles"] or expected_local_profiles != local["profile_paths"]:
            raise ControlPlaneError("stale CPU-first provider profile binding")
        common_paths = {name: Path(path).resolve() for name, path in local["common_paths"].items()}
        current_common = {name: mineru_cpu_first._identity_lower(path) for name, path in common_paths.items()}
        if current_common != run["common_tools"]:
            raise ControlPlaneError("stale CPU-first common tool binding")
    except (KeyError, OSError, json.JSONDecodeError, mineru_cpu_first.CpuFirstContractError) as error:
        raise ControlPlaneError(str(error)) from error
    return contract_path, source_path, contract


def _validate_live_run_bindings(
    run_root: Path,
    run: dict[str, Any],
) -> tuple[Path, Path, dict[str, Any]]:
    if run.get("schema") in mineru_cpu_first.RUN_SCHEMAS:
        return _validate_live_cpu_first_bindings(run_root, run)
    local = run["local"]
    if not isinstance(local, dict):
        raise ControlPlaneError("invalid local run bindings")
    _require_exact_keys(
        local,
        {
            "contract_path",
            "source_path",
            "run_root",
            "mineru_root",
            "executable_paths",
        },
        "local run bindings",
    )
    try:
        bound_run_root = Path(str(local["run_root"])).resolve()
        actual_run_root = run_root.resolve()
        assert_existing_path_components_are_not_reparse(actual_run_root)
    except (OSError, ValueError) as error:
        raise ControlPlaneError(str(error)) from error
    if bound_run_root != actual_run_root:
        raise ControlPlaneError("local run root binding mismatch")
    contract_path = Path(str(local.get("contract_path", "")))
    source_path = Path(str(local.get("source_path", "")))
    contract, contract_sha = load_contract(contract_path)
    if contract_sha != run["contract"]["sha256"]:
        raise ControlPlaneError("stale contract")
    if file_identity(source_path) != {
        "bytes": run["source"]["bytes"],
        "sha256": run["source"]["sha256"],
    }:
        raise ControlPlaneError("stale source")
    current_implementation = implementation_inventory(
        _repo_root(), _implementation_paths()
    )
    if current_implementation != run["implementation"]:
        raise ControlPlaneError("stale implementation")
    executable_paths = local["executable_paths"]
    if not isinstance(executable_paths, dict):
        raise ControlPlaneError("invalid executable path bindings")
    toolchain = run.get("toolchain")
    expected_capability = run.get("capability")
    if not isinstance(expected_capability, dict):
        raise ControlPlaneError("invalid run capability binding")
    if expected_capability.get("state") == "injected":
        current_capability = _runtime_capability(None)
    else:
        mineru_root_value = local.get("mineru_root")
        if not isinstance(mineru_root_value, str) or not mineru_root_value:
            raise ControlPlaneError("missing MinerU root binding")
        current_capability = _runtime_capability(
            RuntimeOptions(
                mineru_root=Path(mineru_root_value),
                pdftoppm=Path("unused"),
                powershell=Path("unused"),
                python=Path("unused"),
            )
        )
    if current_capability != expected_capability:
        raise ControlPlaneError("stale MinerU CUDA capability binding")
    if toolchain == [{"name": "injected_adapters", "version": "test"}]:
        if executable_paths or local["mineru_root"] is not None:
            raise ControlPlaneError("invalid injected-adapter bindings")
        return contract_path, source_path, contract
    if expected_capability.get("state") == "unavailable":
        if toolchain != [] or executable_paths != {}:
            raise ControlPlaneError("invalid skipped-run tool bindings")
        return contract_path, source_path, contract
    if not isinstance(toolchain, list) or not toolchain:
        raise ControlPlaneError("invalid toolchain inventory")
    expected_names: set[str] = set()
    for record in toolchain:
        if not isinstance(record, dict):
            raise ControlPlaneError("invalid toolchain record")
        _require_exact_keys(
            record,
            {"name", "path_hint", "bytes", "sha256"},
            "toolchain record",
        )
        name = record["name"]
        if not isinstance(name, str) or name in expected_names:
            raise ControlPlaneError("duplicate or invalid toolchain name")
        expected_names.add(name)
        bound = executable_paths.get(name)
        if not isinstance(bound, str) or not bound:
            raise ControlPlaneError(f"missing executable binding: {name}")
        tool_path = Path(bound)
        if (
            not tool_path.is_file()
            or tool_path.name != record["path_hint"]
            or file_identity(tool_path)
            != {"bytes": record["bytes"], "sha256": record["sha256"]}
        ):
            raise ControlPlaneError(f"stale tool binding: {name}")
    if set(executable_paths) != expected_names:
        raise ControlPlaneError("unexpected executable binding")
    mineru_root_value = local["mineru_root"]
    if not isinstance(mineru_root_value, str) or not mineru_root_value:
        raise ControlPlaneError("missing MinerU root binding")
    mineru_root = Path(mineru_root_value).resolve()
    expected_mineru = (mineru_root / ".venv" / "Scripts" / "mineru.exe").resolve()
    expected_initialize = (
        _repo_root() / "MinerU" / "scripts" / "initialize.ps1"
    ).resolve()
    if (
        Path(executable_paths.get("mineru", "")).resolve() != expected_mineru
        or Path(executable_paths.get("mineru_initialize", "")).resolve()
        != expected_initialize
    ):
        raise ControlPlaneError("MinerU root binding mismatch")
    return contract_path, source_path, contract


def _stage_id(ordinal: int, name: str) -> str:
    return f"{ordinal:02d}-{name.replace('_', '-')}"


def _stage_manifest_path(
    run_root: Path,
    ordinal: int,
    name: str,
) -> Path:
    return run_root / "stages" / _stage_id(ordinal, name) / "stage.json"


def _stage_output_path(
    run_root: Path,
    ordinal: int,
    name: str,
) -> Path:
    return run_root / "outputs" / _stage_id(ordinal, name)


def _implementation_record(run: dict[str, Any], path: str) -> dict[str, Any]:
    for record in run["implementation"]["files"]:
        if record["path"] == path:
            return record
    raise ControlPlaneError(f"implementation inventory lacks {path}")


def _base_stage_inputs(name: str, run: dict[str, Any]) -> list[dict[str, Any]]:
    contract = {
        "kind": "scenario_reconstruction_contract",
        "path_hint": run["contract"]["path_hint"],
        "bytes": run["contract"]["bytes"],
        "sha256": run["contract"]["sha256"],
    }
    source = {
        "kind": "source_pdf",
        "path_hint": run["source"]["path_hint"],
        "bytes": run["source"]["bytes"],
        "sha256": run["source"]["sha256"],
    }
    if name == "prepare_inputs":
        return [contract, source]
    if name == "mineru_three_view":
        return [source]
    if name == "visual_merge_bundle":
        result = [contract, source]
        if run.get("schema") in mineru_cpu_first.RUN_SCHEMAS:
            prepared = Path(str(run["local"]["run_root"])) / "outputs" / "01-prepare-inputs" / "prepared" / "sample_pages.json"
            if not prepared.is_file():
                raise ControlPlaneError("Stage 04 lacks the directly bound Stage 01 preparation manifest")
            result.append({"kind": "mineru_preparation_manifest", "path_hint": "outputs/01-prepare-inputs/prepared/sample_pages.json", **file_identity(prepared)})
        return result
    return []


def _write_stage(
    run_root: Path,
    ordinal: int,
    name: str,
    run: dict[str, Any],
    upstream: Sequence[dict[str, str]],
    output: Path,
    diagnostics: Mapping[str, object],
    started_at: str,
    inputs: Sequence[dict[str, Any]],
) -> dict[str, Any]:
    try:
        files = deterministic_inventory(output)
    except ValueError as error:
        raise ControlPlaneError(str(error)) from error
    adapter = {
        "logical_name": name,
        "script_sha256": _implementation_record(
            run,
            STAGE_SCRIPTS[name],
        )["sha256"],
        "argv_shape_version": 1,
    }
    cache_key = sha256_bytes(
        canonical_bytes(
            {
                "stage_id": _stage_id(ordinal, name),
                "stage_version": 1,
                "run_identity_sha256": run["portable_identity_sha256"],
                "upstream": list(upstream),
                "inputs": list(inputs),
                "options": run["options"],
                "adapter": adapter,
                "tools": run["toolchain"],
                "implementation_inventory_sha256": run["implementation"][
                    "inventory_sha256"
                ],
            }
        )
    )
    reproducible = {
        "stage_id": _stage_id(ordinal, name),
        "stage_name": name,
        "stage_version": 1,
        "state": "succeeded",
        "run_identity_sha256": run["portable_identity_sha256"],
        "upstream": list(upstream),
        "inputs": list(inputs),
        "options": run["options"],
        "adapter": adapter,
        "tools": run["toolchain"],
        "implementation_inventory_sha256": run["implementation"][
            "inventory_sha256"
        ],
        "outputs": {
            "root_hint": output.relative_to(run_root).as_posix(),
            "files": files,
            "inventory_sha256": sha256_bytes(canonical_bytes(files)),
        },
        "evidence": [],
        "cache_key": cache_key,
    }
    manifest = {
        "schema": STAGE_SCHEMA,
        "reproducible": reproducible,
        "execution": {
            "started_at_utc": started_at,
            "completed_at_utc": _utc_now(),
            "exit_code": 0,
            "structured_diagnostics": dict(diagnostics),
        },
        "reproducible_sha256": sha256_bytes(canonical_bytes(reproducible)),
    }
    destination = _stage_manifest_path(run_root, ordinal, name)
    destination.parent.mkdir(parents=True, exist_ok=False)
    _write_json(destination, manifest)
    return manifest


def _validate_stage(
    run_root: Path,
    ordinal: int,
    name: str,
    run: dict[str, Any],
    expected_upstream: Sequence[dict[str, str]],
    expected_inputs: Sequence[dict[str, Any]],
) -> tuple[dict[str, Any], dict[str, str]]:
    path = _stage_manifest_path(run_root, ordinal, name)
    data = _read(path)
    _require_exact_keys(
        data,
        {"schema", "reproducible", "execution", "reproducible_sha256"},
        "stage manifest",
    )
    if data["schema"] != STAGE_SCHEMA:
        raise ControlPlaneError("invalid stage manifest schema")
    reproducible = data.get("reproducible")
    if not isinstance(reproducible, dict):
        raise ControlPlaneError("invalid reproducible stage record")
    expected_reproducible_keys = {
        "stage_id",
        "stage_name",
        "stage_version",
        "state",
        "run_identity_sha256",
        "upstream",
        "inputs",
        "options",
        "adapter",
        "tools",
        "implementation_inventory_sha256",
        "outputs",
        "evidence",
        "cache_key",
    }
    _require_exact_keys(
        reproducible,
        expected_reproducible_keys,
        "reproducible stage record",
    )
    if (
        not is_sha256(data["reproducible_sha256"])
        or sha256_bytes(canonical_bytes(reproducible))
        != data["reproducible_sha256"]
    ):
        raise ControlPlaneError("reproducible_sha256 mismatch")
    execution = data.get("execution")
    if not isinstance(execution, dict):
        raise ControlPlaneError("invalid stage execution record")
    _require_exact_keys(
        execution,
        {
            "started_at_utc",
            "completed_at_utc",
            "exit_code",
            "structured_diagnostics",
        },
        "stage execution record",
    )
    if execution["exit_code"] != 0 or not isinstance(
        execution["structured_diagnostics"], dict
    ):
        raise ControlPlaneError("invalid stage execution result")
    expected_adapter = {
        "logical_name": name,
        "script_sha256": _implementation_record(
            run,
            STAGE_SCRIPTS[name],
        )["sha256"],
        "argv_shape_version": 1,
    }
    expected_cache_key = sha256_bytes(
        canonical_bytes(
            {
                "stage_id": _stage_id(ordinal, name),
                "stage_version": 1,
                "run_identity_sha256": run["portable_identity_sha256"],
                "upstream": list(expected_upstream),
                "inputs": list(expected_inputs),
                "options": run["options"],
                "adapter": expected_adapter,
                "tools": run["toolchain"],
                "implementation_inventory_sha256": run["implementation"][
                    "inventory_sha256"
                ],
            }
        )
    )
    if (
        reproducible.get("stage_id") != _stage_id(ordinal, name)
        or reproducible.get("stage_name") != name
        or reproducible.get("stage_version") != 1
        or reproducible.get("state") != "succeeded"
        or reproducible.get("run_identity_sha256")
        != run["portable_identity_sha256"]
        or reproducible.get("upstream") != list(expected_upstream)
        or reproducible.get("inputs") != list(expected_inputs)
        or reproducible.get("options") != run["options"]
        or reproducible.get("adapter") != expected_adapter
        or reproducible.get("tools") != run["toolchain"]
        or reproducible.get("implementation_inventory_sha256")
        != run["implementation"]["inventory_sha256"]
        or reproducible.get("cache_key") != expected_cache_key
    ):
        raise ControlPlaneError("stage manifest identity mismatch")
    outputs = reproducible.get("outputs")
    if not isinstance(outputs, dict):
        raise ControlPlaneError("stage manifest lacks outputs")
    _require_exact_keys(
        outputs,
        {"root_hint", "files", "inventory_sha256"},
        "stage output inventory",
    )
    output_root = _stage_output_path(run_root, ordinal, name)
    if outputs.get("root_hint") != output_root.relative_to(run_root).as_posix():
        raise ControlPlaneError("stage output root mismatch")
    try:
        assert_existing_path_components_are_not_reparse(output_root)
        observed = deterministic_inventory(output_root)
    except ValueError as error:
        raise ControlPlaneError(str(error)) from error
    if (
        observed != outputs.get("files")
        or sha256_bytes(canonical_bytes(observed))
        != outputs.get("inventory_sha256")
    ):
        raise ControlPlaneError("stage output inventory mismatch")
    if run.get("schema") in mineru_cpu_first.RUN_SCHEMAS:
        try:
            mineru_cpu_first.validate_stage_output(run, name, output_root)
        except (KeyError, OSError, json.JSONDecodeError, mineru_cpu_first.CpuFirstContractError) as error:
            raise ControlPlaneError(str(error)) from error
    receipt = {
        "stage_id": _stage_id(ordinal, name),
        "manifest_sha256": data["reproducible_sha256"],
    }
    return data, receipt


def _validate_stage_prefix(
    run_root: Path,
    run: dict[str, Any],
    names: Sequence[str],
    inputs_by_stage: Mapping[str, Sequence[dict[str, Any]]] | None = None,
) -> list[dict[str, str]]:
    stages_root = run_root / "stages"
    expected_dirs = {
        _stage_id(index, name) for index, name in enumerate(names, 1)
    }
    observed_dirs = (
        {path.name for path in stages_root.iterdir() if path.is_dir()}
        if stages_root.is_dir()
        else set()
    )
    if observed_dirs != expected_dirs:
        raise ControlPlaneError("stage manifest set is incomplete or contains extras")
    upstream: list[dict[str, str]] = []
    for ordinal, name in enumerate(names, 1):
        expected_inputs = (
            list(inputs_by_stage[name])
            if inputs_by_stage and name in inputs_by_stage
            else _base_stage_inputs(name, run)
        )
        _, receipt = _validate_stage(
            run_root,
            ordinal,
            name,
            run,
            upstream,
            expected_inputs,
        )
        upstream.append(receipt)
    return upstream


def make_queue(
    run_spec: dict[str, Any],
    contract: dict[str, Any],
    bundle_root: Path,
    comparison: Path,
    prepared_manifest: Path,
) -> dict[str, Any]:
    prepared = _read(prepared_manifest)
    render = prepared.get("render")
    page_geometry = render.get("page_geometry", []) if isinstance(render, dict) else []
    geometry_difference_pages = {
        row.get("source_page")
        for row in page_geometry
        if isinstance(row, dict)
        and row.get("media_box_coordinates")
        != row.get("crop_box_coordinates")
    }
    rows = []
    for role in contract["page_roles"]:
        for page in range(role["first_page"], role["last_page"] + 1):
            packet = (
                bundle_root
                / "merge_packets"
                / "pages"
                / f"page-{page:03d}.json"
            )
            if not packet.is_file():
                raise ControlPlaneError(
                    f"missing merge packet for source page {page}"
                )
            packet_data = _read(packet)
            if packet_data.get("source_page") != page:
                raise ControlPlaneError("merge packet page identity mismatch")
            rows.append(
                {
                    "id": f"page-{page:03d}",
                    "source_page": page,
                    "contract_role": role["role"],
                    "contract_traits": role["traits"],
                    "contract_strategies": role["strategies"],
                    "merge_packet": {
                        "path": packet.relative_to(bundle_root).as_posix(),
                        **file_identity(packet),
                    },
                    "issue_kinds": _review_issue_kinds(
                        role,
                        packet_data,
                        page in geometry_difference_pages,
                    ),
                    "required_decision_file": f"pages/page-{page:03d}.json",
                    "state": "open",
                }
            )
    return sealed(
        QUEUE_SCHEMA,
        {
            "run_identity_sha256": run_spec["portable_identity_sha256"],
            "contract_sha256": run_spec["contract"]["sha256"],
            "source_sha256": run_spec["source"]["sha256"],
            "comparison": {
                "path": "outputs/03-compare-views/comparison.json",
                **file_identity(comparison),
            },
            "required_decision_schema": "kb_creator.mineru_ai_page_decision.v1",
            "items": rows,
        },
        digest_key="queue_sha256",
    )


def _review_issue_kinds(
    role: Mapping[str, Any],
    packet: Mapping[str, Any],
    geometry_box_difference: bool,
) -> list[str]:
    issues = ["page_fidelity"]
    strategies = set(role.get("strategies", []))
    traits = set(role.get("traits", []))
    for strategy in ("reading_order", "visual_preserve", "ocr_region"):
        if strategy in strategies:
            issues.append(strategy)
    if "statblock" in traits:
        issues.append("structured_statblock")
    if "table_heavy" in traits:
        issues.append("structured_table")
    if "form_like" in traits:
        issues.append("form_like")
    if geometry_box_difference:
        issues.append("geometry_box_difference")
    signals = packet.get("review_signals")
    if isinstance(signals, dict):
        if (
            signals.get("normalized_text_similarity", 1) < 1
            or signals.get("text_length_divergence", 0) > 0
            or signals.get("block_type_divergence", 0) > 0
        ):
            issues.append("semantic_conflict")
        if (
            signals.get("asset_count_divergence", 0) > 0
            or signals.get("missing_overlay_box_candidates", 0) > 0
        ):
            issues.append("asset_ambiguity")
    return issues


def validate_queue(
    path: Path,
    run: dict[str, Any],
) -> dict[str, Any]:
    queue = _read(path)
    _require_exact_keys(
        queue,
        {
            "schema",
            "run_identity_sha256",
            "contract_sha256",
            "source_sha256",
            "comparison",
            "required_decision_schema",
            "items",
            "queue_sha256",
        },
        "review queue",
    )
    if queue["schema"] != QUEUE_SCHEMA:
        raise ControlPlaneError("invalid review queue")
    try:
        validate_seal(queue, "queue_sha256")
    except ValueError as error:
        raise ControlPlaneError(str(error)) from error
    if (
        queue["run_identity_sha256"] != run["portable_identity_sha256"]
        or queue["contract_sha256"] != run["contract"]["sha256"]
        or queue["source_sha256"] != run["source"]["sha256"]
    ):
        raise ControlPlaneError("review queue identity mismatch")
    comparison = queue["comparison"]
    _require_exact_keys(
        comparison,
        {"path", "bytes", "sha256"},
        "review queue comparison",
    )
    comparison_relative = "outputs/03-compare-views/comparison.json"
    if comparison.get("path") != comparison_relative:
        raise ControlPlaneError("review queue comparison path mismatch")
    run_root = Path(str(run["local"]["run_root"]))
    comparison_path = run_root / comparison_relative
    try:
        assert_existing_path_components_are_not_reparse(comparison_path)
    except ValueError as error:
        raise ControlPlaneError(str(error)) from error
    if not comparison_path.is_file() or file_identity(comparison_path) != {
        "bytes": comparison.get("bytes"),
        "sha256": comparison.get("sha256"),
    }:
        raise ControlPlaneError("review queue comparison identity mismatch")
    items = queue["items"]
    expected_pages = run["scope"]["ordered_pages"]
    if (
        not isinstance(items, list)
        or [item.get("source_page") for item in items] != expected_pages
    ):
        raise ControlPlaneError("review queue page coverage mismatch")
    return queue


def validate_decision_set(
    path: Path,
    queue: dict[str, Any],
    decisions_root: Path,
) -> dict[str, Any]:
    data = _read(path)
    legacy_required = {
        "schema",
        "review_queue_sha256",
        "contract_sha256",
        "source_sha256",
        "decisions",
        "reviewed_allowlist",
        "submission_state",
    }
    schema = data.get("schema")
    required = legacy_required if schema == DECISION_SET_SCHEMA else legacy_required | {"semantic_structure_profile"}
    _require_exact_keys(data, required, "decision set")
    if schema not in {DECISION_SET_SCHEMA, DECISION_SET_V2_SCHEMA} or data["submission_state"] != "submitted_for_validation":
        raise ControlPlaneError("invalid decision set")
    if schema == DECISION_SET_V2_SCHEMA and data["semantic_structure_profile"] not in {"visually_reviewed_semantic_containers_v1", "reviewed_role_outline_and_partitions_v2"}:
        raise ControlPlaneError("invalid semantic structure profile")
    if (
        data["review_queue_sha256"] != queue["queue_sha256"]
        or data["contract_sha256"] != queue["contract_sha256"]
        or data["source_sha256"] != queue["source_sha256"]
    ):
        raise ControlPlaneError("stale decision set")
    if data["reviewed_allowlist"] is not None:
        allowlist = data["reviewed_allowlist"]
        if not isinstance(allowlist, dict):
            raise ControlPlaneError("invalid reviewed allowlist")
        _require_exact_keys(
            allowlist,
            {"path", "bytes", "sha256"},
            "reviewed allowlist",
        )
        relative = Path(str(allowlist["path"]))
        allowlist_path = decisions_root / relative
        if (
            relative.is_absolute()
            or ".." in relative.parts
            or ":" in str(allowlist["path"])
            or "\\" in str(allowlist["path"])
            or relative.as_posix() != str(allowlist["path"])
            or not allowlist_path.is_file()
            or file_identity(allowlist_path)
            != {"bytes": allowlist["bytes"], "sha256": allowlist["sha256"]}
        ):
            raise ControlPlaneError("reviewed allowlist identity mismatch")
    decisions = data["decisions"]
    if not isinstance(decisions, list):
        raise ControlPlaneError("invalid decision inventory")
    expected = {item["source_page"] for item in queue["items"]}
    seen: set[int] = set()
    for row in decisions:
        if not isinstance(row, dict):
            raise ControlPlaneError("invalid decision record")
        _require_exact_keys(
            row,
            {"source_page", "path", "bytes", "sha256"},
            "decision record",
        )
        page = row["source_page"]
        relative = Path(str(row["path"]))
        if (
            page in seen
            or page not in expected
            or relative.is_absolute()
            or ".." in relative.parts
            or relative.as_posix() != f"pages/page-{page:03d}.json"
        ):
            raise ControlPlaneError("unsafe or duplicate decision inventory")
        decision_file = decisions_root / relative
        if not decision_file.is_file() or file_identity(decision_file) != {
            "bytes": row["bytes"],
            "sha256": row["sha256"],
        }:
            raise ControlPlaneError("decision identity mismatch")
        decision = _read(decision_file)
        if (
            decision.get("schema") != queue["required_decision_schema"]
            or decision.get("source_page") != page
            or decision.get("unresolved") != []
            or decision.get("review", {}).get("visual_reviewed") is not True
        ):
            raise ControlPlaneError("decision is not closed")
        if schema == DECISION_SET_V2_SCHEMA:
            structure = decision.get("semantic_structure")
            expected_schema = "kb_creator.page_semantic_structure.v2" if data["semantic_structure_profile"] == "reviewed_role_outline_and_partitions_v2" else "kb_creator.page_semantic_structure.v1"
            if not isinstance(structure, dict) or structure.get("schema") != expected_schema:
                raise ControlPlaneError("v2 decision lacks semantic structure")
        elif "semantic_structure" in decision:
            raise ControlPlaneError("legacy decision set cannot mix structural profile")
        seen.add(page)
    if seen != expected:
        raise ControlPlaneError("decision coverage mismatch")
    return data


def validate_review_draft_decision_set(
    path: Path, queue: dict[str, Any], decisions_root: Path, evidence_path: Path,
) -> dict[str, Any]:
    """Validate a sealed review-draft decision set without production promotion.

    This intentionally does not call :func:`validate_decision_set`: that
    validator proves closed visual review and remains the production boundary.
    The separate route requires final Stage05 evidence and retains literal page
    flags for downstream reporting.
    """
    from kb_creator.pipeline.review_draft import ReviewDraftError, validate_review_draft_evidence
    try:
        evidence = validate_review_draft_evidence(_read(evidence_path))
    except (OSError, ValueError, ReviewDraftError) as error:
        raise ControlPlaneError(f"invalid review-draft evidence: {error}") from error
    decision_identity = evidence["authored"].get("decision_set")
    if decision_identity != {"path": path.name, **file_identity(path)}:
        raise ControlPlaneError("review-draft evidence does not bind the decision set")
    audit_identity = evidence["authored"].get("stage05_audit")
    if not isinstance(audit_identity, dict) or set(audit_identity) != {"path", "bytes", "sha256"}:
        raise ControlPlaneError("review-draft evidence lacks Stage05 audit identity")
    audit_path = evidence_path.parent / audit_identity["path"]
    if not audit_path.is_file() or file_identity(audit_path) != {"bytes": audit_identity["bytes"], "sha256": audit_identity["sha256"]}:
        raise ControlPlaneError("review-draft Stage05 audit identity changed")
    if _read(audit_path) != evidence["audit"]:
        raise ControlPlaneError("review-draft Stage05 audit content differs from sealed evidence")
    data = _read(path)
    decisions = data.get("decisions") if isinstance(data, dict) else None
    expected = {item["source_page"] for item in queue["items"]}
    if not isinstance(decisions, list) or len(decisions) != len(expected):
        raise ControlPlaneError("review-draft decision inventory is incomplete")
    seen: set[int] = set()
    literal_false: set[int] = set()
    for row in decisions:
        if not isinstance(row, dict) or set(row) != {"source_page", "path", "bytes", "sha256"}:
            raise ControlPlaneError("review-draft decision record is malformed")
        page = row["source_page"]
        relative = Path(str(row["path"]))
        if type(page) is not int or page in seen or page not in expected or relative.as_posix() != f"pages/page-{page:03d}.json" or relative.is_absolute() or ".." in relative.parts:
            raise ControlPlaneError("review-draft decision record is unsafe")
        decision_path = decisions_root / relative
        if not decision_path.is_file() or file_identity(decision_path) != {"bytes": row["bytes"], "sha256": row["sha256"]}:
            raise ControlPlaneError("review-draft decision identity mismatch")
        decision = _read(decision_path)
        if decision.get("source_page") != page or decision.get("unresolved") != [] or decision.get("review", {}).get("visual_reviewed") not in {True, False}:
            raise ControlPlaneError("review-draft decision is not a closed reader draft")
        if decision["review"]["visual_reviewed"] is False:
            literal_false.add(page)
        seen.add(page)
    if seen != expected or literal_false != set(evidence["visual_reviewed_false_pages"]):
        raise ControlPlaneError("review-draft page domain or literal visual flags mismatch")
    return data


def _decision_inputs(
    decision_set_path: Path,
    decision_set: dict[str, Any],
    *,
    run: Mapping[str, Any] | None = None,
    queue: Mapping[str, Any] | None = None,
) -> list[dict[str, Any]]:
    records = [
        {
            "kind": "reconstruction_decision_set",
            "path_hint": decision_set_path.name,
            **file_identity(decision_set_path),
        }
    ]
    records.extend(
        {
            "kind": "page_decision",
            "path_hint": row["path"],
            "bytes": row["bytes"],
            "sha256": row["sha256"],
        }
        for row in decision_set["decisions"]
    )
    allowlist = decision_set.get("reviewed_allowlist")
    if allowlist:
        records.append(
            {
                "kind": "reviewed_allowlist",
                "path_hint": allowlist["path"],
                "bytes": allowlist["bytes"],
                "sha256": allowlist["sha256"],
            }
        )
    if run is not None and run.get("schema") in mineru_cpu_first.RUN_SCHEMAS:
        if queue is None:
            raise ControlPlaneError("v2 decision inputs require review queue")
        run_root = Path(str(run["local"]["run_root"]))
        queue_path = run_root / "review" / "review_queue.json"
        comparison_path = run_root / str(queue["comparison"]["path"])
        records.extend(
            [
                {"kind": "review_queue", "path_hint": "review/review_queue.json", **file_identity(queue_path)},
                {"kind": "multi_view_comparison", "path_hint": queue["comparison"]["path"], **file_identity(comparison_path)},
                {"kind": "fidelity_policy", "path_hint": "kb_creator/contracts/ai_merge_fidelity_audit.v2.schema.json", **file_identity(_repo_root() / "kb_creator" / "contracts" / "ai_merge_fidelity_audit.v2.schema.json")},
            ]
        )
    return records


def _validate_submission_snapshot(
    snapshot_root: Path,
    run: Mapping[str, Any],
    queue: Mapping[str, Any],
) -> tuple[dict[str, Any], dict[str, Any]]:
    try:
        assert_existing_path_components_are_not_reparse(snapshot_root)
        if any(path.is_symlink() or is_reparse_point(path) for path in snapshot_root.rglob("*")):
            raise ValueError("validated submission contains a reparse point")
        inventory = _read(snapshot_root / "submission_inventory.json")
    except (OSError, ValueError) as error:
        raise ControlPlaneError("invalid validated submission snapshot") from error
    _require_exact_keys(
        inventory,
        {
            "schema",
            "run_identity_sha256",
            "review_queue_sha256",
            "contract_sha256",
            "source_sha256",
            "decision_set",
            "decisions",
            "reviewed_allowlist",
            "files",
            "inventory_sha256",
        },
        "validated submission inventory",
    )
    try:
        validate_seal(inventory, "inventory_sha256")
    except ValueError as error:
        raise ControlPlaneError("invalid validated submission seal") from error
    if (
        inventory.get("schema") != VALIDATED_SUBMISSION_SCHEMA
        or inventory.get("run_identity_sha256") != run["portable_identity_sha256"]
        or inventory.get("review_queue_sha256") != queue["queue_sha256"]
        or inventory.get("contract_sha256") != run["contract"]["sha256"]
        or inventory.get("source_sha256") != run["source"]["sha256"]
    ):
        raise ControlPlaneError("stale validated submission snapshot")
    files = inventory.get("files")
    if not isinstance(files, list) or files != deterministic_inventory(snapshot_root):
        # The inventory cannot list itself because its seal would be recursive.
        observed = [
            row for row in deterministic_inventory(snapshot_root)
            if row["path"] != "submission_inventory.json"
        ]
        if files != observed:
            raise ControlPlaneError("validated submission file inventory mismatch")
    decision_set_record = inventory.get("decision_set")
    if not isinstance(decision_set_record, dict):
        raise ControlPlaneError("invalid validated decision-set identity")
    decision_path = snapshot_root / "decision_set.json"
    if decision_set_record != {"path": "decision_set.json", **file_identity(decision_path)}:
        raise ControlPlaneError("validated decision-set identity mismatch")
    decisions = validate_decision_set(decision_path, dict(queue), snapshot_root)
    expected_records = [
        {"source_page": row["source_page"], "path": row["path"], "bytes": row["bytes"], "sha256": row["sha256"]}
        for row in decisions["decisions"]
    ]
    if inventory.get("decisions") != expected_records:
        raise ControlPlaneError("validated decision domain mismatch")
    allowlist = decisions.get("reviewed_allowlist")
    expected_allowlist = None
    if allowlist:
        path = snapshot_root / "reviewed_allowlist.json"
        expected_allowlist = {"path": "reviewed_allowlist.json", **file_identity(path)}
    if inventory.get("reviewed_allowlist") != expected_allowlist:
        raise ControlPlaneError("validated allowlist identity mismatch")
    return inventory, decisions


def _materialize_submission_snapshot(
    run_root: Path,
    run: Mapping[str, Any],
    queue: Mapping[str, Any],
    decision_set_path: Path,
    decisions: Mapping[str, Any],
    decisions_root: Path,
) -> tuple[Path, dict[str, Any]]:
    review_root = run_root / "review"
    destination = review_root / "validated-submission-v1"
    staging = review_root / ".validated-submission-v1.staging"
    if destination.exists():
        _, snapshot = _validate_submission_snapshot(destination, run, queue)
        supplied_set = _read(decision_set_path)
        supplied_allowlist = decisions.get("reviewed_allowlist")
        if supplied_allowlist:
            supplied_set["reviewed_allowlist"] = {
                "path": "reviewed_allowlist.json",
                **file_identity(decisions_root / str(supplied_allowlist["path"])),
            }
        if supplied_set != _read(destination / "decision_set.json"):
            raise ControlPlaneError("stale or conflicting validated submission snapshot")
        for row in decisions["decisions"]:
            if file_identity(decisions_root / str(row["path"])) != file_identity(destination / str(row["path"])):
                raise ControlPlaneError("stale or conflicting validated submission snapshot")
        if supplied_allowlist and file_identity(decisions_root / str(supplied_allowlist["path"])) != file_identity(destination / "reviewed_allowlist.json"):
            raise ControlPlaneError("stale or conflicting validated submission snapshot")
        return destination, snapshot
    if staging.exists():
        raise ControlPlaneError("validated submission staging residue exists")
    try:
        staging.mkdir(parents=False)
        copied_decisions: list[dict[str, Any]] = []
        (staging / "pages").mkdir()
        shutil.copyfile(decision_set_path, staging / "decision_set.json")
        for row in decisions["decisions"]:
            source = decisions_root / str(row["path"])
            target = staging / str(row["path"])
            shutil.copyfile(source, target)
            copied_decisions.append(
                {"source_page": row["source_page"], "path": row["path"], **file_identity(target)}
            )
        copied_allowlist = None
        allowlist = decisions.get("reviewed_allowlist")
        if allowlist:
            source = decisions_root / str(allowlist["path"])
            target = staging / "reviewed_allowlist.json"
            shutil.copyfile(source, target)
            copied_allowlist = {"path": "reviewed_allowlist.json", **file_identity(target)}
            snapshot_set = _read(staging / "decision_set.json")
            snapshot_set["reviewed_allowlist"] = copied_allowlist
            _write_json(staging / "decision_set.json", snapshot_set)
        snapshot_set = _read(staging / "decision_set.json")
        decision_record = {"path": "decision_set.json", **file_identity(staging / "decision_set.json")}
        files = deterministic_inventory(staging)
        inventory = sealed(
            VALIDATED_SUBMISSION_SCHEMA,
            {
                "run_identity_sha256": run["portable_identity_sha256"],
                "review_queue_sha256": queue["queue_sha256"],
                "contract_sha256": run["contract"]["sha256"],
                "source_sha256": run["source"]["sha256"],
                "decision_set": decision_record,
                "decisions": copied_decisions,
                "reviewed_allowlist": copied_allowlist,
                "files": files,
            },
            digest_key="inventory_sha256",
        )
        _write_json(staging / "submission_inventory.json", inventory)
        _validate_submission_snapshot(staging, run, queue)
        if destination.exists():
            raise ControlPlaneError("validated submission path already exists")
        os.rename(staging, destination)
    except Exception:
        if staging.exists():
            shutil.rmtree(staging)
        raise
    _, snapshot = _validate_submission_snapshot(destination, run, queue)
    return destination, snapshot


def _invoke_stage(
    run_root: Path,
    ordinal: int,
    name: str,
    run: dict[str, Any],
    upstream: list[dict[str, str]],
    adapter: StageAdapter,
    external_inputs: Sequence[dict[str, Any]] = (),
) -> dict[str, str]:
    if adapter.name != name:
        raise ControlPlaneError(f"wrong adapter for stage {name}")
    _validate_live_run_bindings(run_root, run)
    output = _stage_output_path(run_root, ordinal, name)
    if output.exists():
        raise ControlPlaneError(f"stage output already exists: {output}")
    output.parent.mkdir(parents=True, exist_ok=True)
    stage_id = _stage_id(ordinal, name)
    staging = run_root / "local" / "staging" / stage_id
    failure = run_root / "failures" / stage_id
    if staging.exists() or failure.exists():
        raise ControlPlaneError(f"stage attempt path already exists: {stage_id}")
    staging.parent.mkdir(parents=True, exist_ok=True)
    inputs = [*_base_stage_inputs(name, run), *external_inputs]
    started_at = _utc_now()
    try:
        diagnostics = dict(adapter.invoke(staging))
        if run.get("schema") in mineru_cpu_first.RUN_SCHEMAS:
            mineru_cpu_first.validate_stage_output(run, name, staging)
        deterministic_inventory(staging)
        staging.replace(output)
        manifest = _write_stage(
            run_root,
            ordinal,
            name,
            run,
            upstream,
            output,
            diagnostics,
            started_at,
            inputs,
        )
    except Exception as error:
        if (
            run.get("schema") in mineru_cpu_first.RUN_SCHEMAS
            and isinstance(error, pipeline_process.ProcessFailure)
        ):
            staging.mkdir(parents=True, exist_ok=True)
            argv = list(error.argv)
            profile = None
            if "-Profile" in argv:
                profile_index = argv.index("-Profile") + 1
                if profile_index < len(argv):
                    profile = argv[profile_index]
            process_failure = sealed(
                "kb_creator.stage_failure.v1",
                {
                    "stage_id": stage_id,
                    "stage_name": name,
                    "run_identity_sha256": run["portable_identity_sha256"],
                    "failure_kind": "child_process_nonzero",
                    "profile": profile,
                    "argv": argv,
                    "environment": error.environment,
                    "exit_code": error.returncode,
                    "stdout": error.stdout,
                    "stderr": error.stderr,
                    "stdout_truncated": error.stdout_truncated,
                    "stderr_truncated": error.stderr_truncated,
                },
                digest_key="failure_sha256",
            )
            _write_json(staging / "stage-failure.json", process_failure)
        failed_output = staging if staging.exists() else output
        if failed_output.exists():
            failure.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(failed_output), str(failure))
        manifest_parent = _stage_manifest_path(
            run_root,
            ordinal,
            name,
        ).parent
        if manifest_parent.exists():
            shutil.rmtree(manifest_parent)
        raise ControlPlaneError(f"stage {name} failed: {error}") from error
    return {
        "stage_id": manifest["reproducible"]["stage_id"],
        "manifest_sha256": manifest["reproducible_sha256"],
    }


def _skip_stages(reason_code: str) -> list[dict[str, Any]]:
    stages: list[dict[str, Any]] = []
    for ordinal, name in enumerate(ALL_STAGES, 1):
        if name == "mineru_three_view":
            stage_reason = reason_code
            blocked_by = ["capability:mineru_cuda"]
        elif ordinal < 2:
            stage_reason = "run_prerequisite_unavailable"
            blocked_by = ["capability:mineru_cuda"]
        else:
            previous = ALL_STAGES[ordinal - 2]
            stage_reason = "dependency_skipped"
            blocked_by = [_stage_id(ordinal - 1, previous)]
        stages.append(
            {
                "stage_id": _stage_id(ordinal, name),
                "stage_name": name,
                "state": "skipped",
                "reason_code": stage_reason,
                "blocked_by": blocked_by,
            }
        )
    return stages


def _write_skipped_run(run_root: Path, run: dict[str, Any]) -> dict[str, Any]:
    capability = run["capability"]
    skip = sealed(
        SKIP_SCHEMA,
        {
            "state": "skipped",
            "run_identity_sha256": run["portable_identity_sha256"],
            "capability": capability,
            "stages": _skip_stages(capability["reason_code"]),
        },
        digest_key="skip_sha256",
    )
    destination = run_root / "skip.json"
    _write_json(destination, skip)
    return {
        "schema": "kb_creator.run_result.v1",
        "state": "skipped",
        "exit_code": 0,
        "run_identity_sha256": run["portable_identity_sha256"],
        "reason_code": capability["reason_code"],
        "skip_evidence": str(destination),
    }


def _validate_skip(run_root: Path, run: dict[str, Any]) -> dict[str, Any]:
    path = run_root / "skip.json"
    data = _read(path)
    _require_exact_keys(
        data,
        {
            "schema",
            "state",
            "run_identity_sha256",
            "capability",
            "stages",
            "skip_sha256",
        },
        "run skip evidence",
    )
    if data.get("schema") != SKIP_SCHEMA or data.get("state") != "skipped":
        raise ControlPlaneError("invalid run skip evidence")
    try:
        validate_seal(data, "skip_sha256")
    except ValueError as error:
        raise ControlPlaneError(str(error)) from error
    if (
        data.get("run_identity_sha256") != run["portable_identity_sha256"]
        or data.get("capability") != run["capability"]
        or data.get("stages")
        != _skip_stages(run["capability"]["reason_code"])
    ):
        raise ControlPlaneError("run skip evidence identity mismatch")
    for forbidden in ("stages", "outputs", "review"):
        if (run_root / forbidden).exists():
            raise ControlPlaneError(
                f"skipped run contains forbidden {forbidden} artifacts"
            )
    return data


def run_engine(
    contract_path: Path,
    source_path: Path,
    run_root: Path,
    run_id: str,
    adapters: Mapping[str, StageAdapter] | None = None,
    runtime: RuntimeOptions | None = None,
    recovery_plan: dict[str, Any] | None = None,
) -> dict[str, Any]:
    run = write_run(contract_path, source_path, run_root, run_id, runtime)
    if recovery_plan is not None:
        from .mineru_view_recovery_plan import RecoveryPlanError, validate_fresh_target
        try:
            validate_fresh_target(recovery_plan, run)
        except RecoveryPlanError as error:
            raise ControlPlaneError(str(error)) from error
    if run["schema"] == RUN_SCHEMA and run["capability"]["state"] == "unavailable":
        return _write_skipped_run(run_root, run)
    if adapters is None:
        adapters = production_run_adapters(run, contract_path, source_path, recovery_plan=recovery_plan)
    if set(adapters) != set(RUN_STAGES):
        raise ControlPlaneError("fixed run graph adapters are incomplete")
    _validate_live_run_bindings(run_root, run)
    upstream: list[dict[str, str]] = []
    for ordinal, name in enumerate(RUN_STAGES, 1):
        upstream.append(
            _invoke_stage(
                run_root,
                ordinal,
                name,
                run,
                upstream,
                adapters[name],
            )
        )
    _, _, contract = _validate_live_run_bindings(run_root, run)
    bundle = _stage_output_path(run_root, 4, "visual_merge_bundle")
    comparison = (
        _stage_output_path(run_root, 3, "compare_views") / "comparison.json"
    )
    queue = make_queue(
        run,
        contract,
        bundle,
        comparison,
        _stage_output_path(run_root, 1, "prepare_inputs")
        / "prepared"
        / "sample_pages.json",
    )
    review = run_root / "review"
    review.mkdir()
    _write_json(review / "review_queue.json", queue)
    _write_json(
        review / "decision_set.template.json",
        {
            "schema": DECISION_SET_SCHEMA,
            "review_queue_sha256": queue["queue_sha256"],
            "contract_sha256": queue["contract_sha256"],
            "source_sha256": queue["source_sha256"],
            "decisions": [],
            "reviewed_allowlist": None,
            "submission_state": "draft",
        },
    )
    return {
        "schema": "kb_creator.run_result.v1",
        "state": "needs_review",
        "exit_code": 10,
        "run_identity_sha256": run["portable_identity_sha256"],
        "review_queue": str(review / "review_queue.json"),
    }


def resume_engine(
    run_root: Path,
    decision_set: Path,
    decisions_root: Path,
    adapters: Mapping[str, StageAdapter] | None = None,
) -> dict[str, Any]:
    run = load_run(run_root)
    _validate_live_run_bindings(run_root, run)
    if run["schema"] == RUN_SCHEMA and run["capability"]["state"] == "unavailable":
        _validate_skip(run_root, run)
        raise ControlPlaneError(
            "run was skipped because MinerU CUDA capability is unavailable; "
            "start a new run after capability changes"
        )
    upstream = _validate_stage_prefix(run_root, run, RUN_STAGES)
    queue = validate_queue(run_root / "review" / "review_queue.json", run)
    decisions = validate_decision_set(decision_set, queue, decisions_root)
    snapshot_root, decisions = _materialize_submission_snapshot(
        run_root, run, queue, decision_set, decisions, decisions_root
    )
    decision_set = snapshot_root / "decision_set.json"
    decisions_root = snapshot_root
    decision_inputs = _decision_inputs(decision_set, decisions, run=run, queue=queue)
    if adapters is None:
        adapters = production_resume_adapters(
            run, decisions, decisions_root, queue=queue
        )
    if set(adapters) != set(RESUME_STAGES):
        raise ControlPlaneError("fixed resume graph adapters are incomplete")
    inputs_by_stage: dict[str, list[dict[str, Any]]] = {"fidelity_audit": decision_inputs}
    for ordinal, name in enumerate(RESUME_STAGES, len(RUN_STAGES) + 1):
        stage_inputs = decision_inputs
        if name == "materialize_candidate" and run.get("schema") in mineru_cpu_first.RUN_SCHEMAS:
            audit_path = _stage_output_path(run_root, 5, "fidelity_audit") / "audit.json"
            if not audit_path.is_file():
                raise ControlPlaneError("v2 materialization requires the passed Stage05 audit")
            stage_inputs = decision_inputs + [{"kind": "fidelity_audit", "path_hint": "outputs/05-fidelity-audit/audit.json", **file_identity(audit_path)}]
            inputs_by_stage[name] = stage_inputs
        upstream.append(
            _invoke_stage(
                run_root,
                ordinal,
                name,
                run,
                upstream,
                adapters[name],
                stage_inputs,
            )
        )
    _validate_stage_prefix(
        run_root,
        run,
        ALL_STAGES,
        inputs_by_stage if run.get("schema") in mineru_cpu_first.RUN_SCHEMAS else {"fidelity_audit": decision_inputs, "materialize_candidate": decision_inputs},
    )
    return {
        "schema": "kb_creator.resume_result.v1",
        "state": "candidate_ready_for_reconstruction_qa",
        "exit_code": 0,
        "run_identity_sha256": run["portable_identity_sha256"],
        "candidate_root": str(
            _stage_output_path(run_root, 6, "materialize_candidate")
            / "candidate"
        ),
    }


def _python_argv(run: dict[str, Any], script_name: str) -> list[str]:
    if run.get("schema") in mineru_cpu_first.RUN_SCHEMAS:
        python_path = run["local"]["profile_paths"]["pipeline_cpu"]["python"]
    else:
        python_path = run["local"]["executable_paths"].get("python")
    if not python_path:
        raise ControlPlaneError("run lacks a Python executable binding")
    return [
        python_path,
        "-B",
        str(_repo_root() / "kb_creator" / "scripts" / script_name),
    ]


def production_cpu_first_run_adapters(
    run: dict[str, Any],
    contract_path: Path,
    source_path: Path,
    *, recovery_plan: Mapping[str, Any] | None = None,
) -> dict[str, StageAdapter]:
    local = run["local"]
    powershell = local["common_paths"]["powershell"]
    pdftoppm = local["common_paths"]["pdftoppm"]
    run_root = Path(local["run_root"])
    pages = f"1-{run['source']['page_count']}"
    prepare_root = _stage_output_path(run_root, 1, "prepare_inputs") / "prepared"
    mineru_output = _stage_output_path(run_root, 2, "mineru_three_view")
    comparison_root = _stage_output_path(run_root, 3, "compare_views")

    def prepare(output: Path) -> Mapping[str, object]:
        output.mkdir(parents=True, exist_ok=False)
        argv = _python_argv(run, "prepare_mineru_three_view_inputs.py") + [
            "--source", str(source_path),
            "--output-dir", str(output / "prepared"),
            "--source-sha256", run["source"]["sha256"],
            "--pages", pages,
            "--dpi", str(run["options"]["raster_dpi"]),
            "--basename", "source",
            "--raster-only",
            "--geometry-policy", run["options"]["geometry_policy"],
        ]
        diagnostics = pipeline_process.run(argv, cwd=_repo_root())
        _write_json(output / "command.json", diagnostics)
        return diagnostics

    def mineru(output: Path) -> Mapping[str, object]:
        output.mkdir(parents=True, exist_ok=False)
        commands = []
        profile_names = {
            "original_pipeline_txt": "pipeline_txt",
            "original_pipeline_ocr": "pipeline_ocr",
            "raster_pipeline_ocr": "pipeline_ocr",
            "original_hybrid_high": "hybrid_high",
            "original_vlm": "vlm_local",
        }
        providers = {row["provider_id"]: row for row in run["capability_snapshot"]["providers"]}
        imported: set[str] = set()
        if recovery_plan:
            from .mineru_view_recovery import import_verified_succeeded_view
            origin_run = recovery_plan["origin_run"]
            origin_stage = Path(str(recovery_plan["origin_stage_root"]))
            compatibility = recovery_plan.get("wrapper_compatibility", {})
            source_profile = recovery_plan.get("source_profile_compatibility", {})
            for view_id in recovery_plan["views"]:
                import_verified_succeeded_view(
                    origin_run, origin_stage, run, output, view_id,
                    wrapper_compatibility=compatibility.get(view_id),
                    source_profile_compatibility=source_profile.get(view_id),
                )
                imported.add(view_id)
        for descriptor in run["view_plan"]:
            if descriptor["view_id"] in imported:
                continue
            input_path, input_identity = mineru_cpu_first.view_input_identity(run, descriptor)
            receipt_path = output / "views" / descriptor["view_id"] / "view.json"
            provider = providers[descriptor["provider_id"]]
            if provider["state"] == "unavailable":
                mineru_cpu_first.write_skipped_view(run, descriptor, input_identity, receipt_path)
                continue
            view_dir = receipt_path.parent
            view_dir.mkdir(parents=True, exist_ok=False)
            artifact_root = view_dir / "artifacts"
            argv = [
                powershell,
                "-NoProfile",
                "-File",
                local["common_paths"]["wrapper"],
                "-Profile",
                profile_names[descriptor["view_id"]],
                "-InputPath",
                str(input_path),
                "-OutputPath",
                str(artifact_root),
                "-ToolRoot",
                local["mineru_root"],
                "-SourceRoot",
                local["mineru_source_root"],
                "-RuntimeRoot",
                str(view_dir / "runtime"),
                "-OcrLanguage",
                run["options"]["ocr_language"],
                "-StartPage",
                "0",
                "-EndPage",
                str(run["source"]["page_count"] - 1),
            ]
            outer_environment = {
                key: os.environ[key]
                for key in ("SystemRoot", "WINDIR", "ComSpec", "PATHEXT")
                if key in os.environ
            }
            diagnostics = pipeline_process.run(
                argv,
                cwd=_repo_root(),
                env_updates=outer_environment,
                inherit_environment=False,
            )
            commands.append(diagnostics)
            mineru_cpu_first.write_succeeded_view(
                run,
                descriptor,
                input_identity,
                artifact_root,
                receipt_path,
                diagnostics,
            )
        mineru_cpu_first.write_view_set(run, output)
        return {"commands": commands, "imported_views": sorted(imported), "view_set": "view-set.json"}

    def compare(output: Path) -> Mapping[str, object]:
        argv = _python_argv(run, "compare_mineru_three_views.py") + [
            "--manifest", str(prepare_root / "sample_pages.json"),
            "--view-set-manifest", str(mineru_output / "view-set.json"),
            "--output-dir", str(output),
        ]
        diagnostics = pipeline_process.run(argv, cwd=_repo_root())
        _write_json(output / "command.json", diagnostics)
        return diagnostics

    def visual_bundle(output: Path) -> Mapping[str, object]:
        view_set = mineru_output / "view-set.json"
        comparison = comparison_root / "comparison.json"
        argv = _python_argv(run, "build_mineru_visual_merge_bundle.py") + [
            "--raw-root", str(mineru_output),
            "--output-root", str(output),
            "--raw-receipt", str(view_set),
            "--raw-receipt-sha256", sha256_file(view_set),
            "--source", str(source_path),
            "--source-sha256", run["source"]["sha256"],
            "--comparison", str(comparison),
            "--comparison-sha256", sha256_file(comparison),
            "--prepared-manifest", str(prepare_root / "sample_pages.json"),
            "--prepared-manifest-sha256", sha256_file(prepare_root / "sample_pages.json"),
            "--pdftoppm", pdftoppm,
            "--dpi", str(run["options"]["review_dpi"]),
            "--reconstruction-contract", str(contract_path),
        ]
        diagnostics = pipeline_process.run(argv, cwd=_repo_root())
        _write_json(output / "command.json", diagnostics)
        return diagnostics

    return {
        "prepare_inputs": StageAdapter("prepare_inputs", prepare),
        "mineru_three_view": StageAdapter("mineru_three_view", mineru),
        "compare_views": StageAdapter("compare_views", compare),
        "visual_merge_bundle": StageAdapter("visual_merge_bundle", visual_bundle),
    }


def production_run_adapters(
    run: dict[str, Any],
    contract_path: Path,
    source_path: Path,
    *, recovery_plan: Mapping[str, Any] | None = None,
) -> dict[str, StageAdapter]:
    if run.get("schema") in mineru_cpu_first.RUN_SCHEMAS:
        return production_cpu_first_run_adapters(run, contract_path, source_path, recovery_plan=recovery_plan)
    local = run["local"]
    executable_paths = local.get("executable_paths", {})
    powershell = executable_paths.get("powershell")
    pdftoppm = executable_paths.get("pdftoppm")
    mineru_root = local.get("mineru_root")
    if not powershell or not pdftoppm or not mineru_root:
        raise ControlPlaneError("run lacks production tool bindings")
    run_root = Path(local["run_root"])
    pages = f"1-{run['source']['page_count']}"
    prepare_root = (
        _stage_output_path(run_root, 1, "prepare_inputs") / "prepared"
    )
    mineru_output = _stage_output_path(run_root, 2, "mineru_three_view")
    comparison_root = _stage_output_path(run_root, 3, "compare_views")

    def prepare(output: Path) -> Mapping[str, object]:
        output.mkdir(parents=True, exist_ok=False)
        argv = _python_argv(run, "prepare_mineru_three_view_inputs.py") + [
            "--source",
            str(source_path),
            "--output-dir",
            str(output / "prepared"),
            "--source-sha256",
            run["source"]["sha256"],
            "--pages",
            pages,
            "--dpi",
            str(run["options"]["raster_dpi"]),
            "--basename",
            "source",
            "--raster-only",
        ]
        diagnostics = pipeline_process.run(argv, cwd=_repo_root())
        _write_json(output / "command.json", diagnostics)
        return diagnostics

    def mineru(output: Path) -> Mapping[str, object]:
        output.mkdir(parents=True, exist_ok=False)
        commands = []
        raster_pdf = prepare_root / "source_raster.pdf"
        views = (
            ("original_hybrid", "hybrid_high", source_path),
            ("original_pipeline_ocr", "pipeline_ocr", source_path),
            ("raster_hybrid", "hybrid_high", raster_pdf),
        )
        for name, profile, input_path in views:
            argv = [
                powershell,
                "-NoProfile",
                "-File",
                str(
                    _repo_root()
                    / "kb_creator"
                    / "scripts"
                    / "run_mineru_three_view.ps1"
                ),
                "-Profile",
                profile,
                "-InputPath",
                str(input_path),
                "-OutputPath",
                str(output / "runs" / name),
                "-MinerURoot",
                mineru_root,
            ]
            commands.append(pipeline_process.run(argv, cwd=_repo_root()))
        if file_identity(source_path) != {
            "bytes": run["source"]["bytes"],
            "sha256": run["source"]["sha256"],
        }:
            raise ControlPlaneError("source changed during MinerU execution")
        _write_json(
            output / "raw_receipt.json",
            {
                "schema": "kb_creator.mineru_three_view_receipt.v1",
                "commands": commands,
            },
        )
        return {"commands": commands}

    def compare(output: Path) -> Mapping[str, object]:
        argv = _python_argv(run, "compare_mineru_three_views.py") + [
            "--manifest",
            str(prepare_root / "sample_pages.json"),
            "--original-hybrid",
            str(mineru_output / "runs" / "original_hybrid"),
            "--original-pipeline-ocr",
            str(mineru_output / "runs" / "original_pipeline_ocr"),
            "--raster-hybrid",
            str(mineru_output / "runs" / "raster_hybrid"),
            "--output-dir",
            str(output),
        ]
        diagnostics = pipeline_process.run(argv, cwd=_repo_root())
        _write_json(output / "command.json", diagnostics)
        return diagnostics

    def visual_bundle(output: Path) -> Mapping[str, object]:
        raw_receipt = mineru_output / "raw_receipt.json"
        comparison = comparison_root / "comparison.json"
        argv = _python_argv(run, "build_mineru_visual_merge_bundle.py") + [
            "--raw-root",
            str(mineru_output),
            "--output-root",
            str(output),
            "--raw-receipt",
            str(raw_receipt),
            "--raw-receipt-sha256",
            sha256_file(raw_receipt),
            "--source",
            str(source_path),
            "--source-sha256",
            run["source"]["sha256"],
            "--comparison",
            str(comparison),
            "--comparison-sha256",
            sha256_file(comparison),
            "--pdftoppm",
            pdftoppm,
            "--dpi",
            str(run["options"]["review_dpi"]),
            "--reconstruction-contract",
            str(contract_path),
        ]
        diagnostics = pipeline_process.run(argv, cwd=_repo_root())
        _write_json(output / "command.json", diagnostics)
        return diagnostics

    return {
        "prepare_inputs": StageAdapter("prepare_inputs", prepare),
        "mineru_three_view": StageAdapter("mineru_three_view", mineru),
        "compare_views": StageAdapter("compare_views", compare),
        "visual_merge_bundle": StageAdapter(
            "visual_merge_bundle",
            visual_bundle,
        ),
    }


def production_resume_adapters(
    run: dict[str, Any],
    decision_set: dict[str, Any],
    decisions_root: Path,
    *,
    queue: dict[str, Any] | None = None,
) -> dict[str, StageAdapter]:
    run_root = Path(run["local"]["run_root"])
    bundle_root = _stage_output_path(run_root, 4, "visual_merge_bundle")
    raw_root = _stage_output_path(run_root, 2, "mineru_three_view")
    comparison_path: Path | None = None
    comparison_sha256: str | None = None
    if run.get("schema") in mineru_cpu_first.RUN_SCHEMAS:
        if queue is None:
            raise ControlPlaneError("v2 resume adapters require the validated review queue")
        current_queue = validate_queue(
            run_root / "review" / "review_queue.json", run
        )
        if queue != current_queue:
            raise ControlPlaneError("v2 review queue argument is stale or unvalidated")
        record = queue.get("comparison")
        if (
            not isinstance(record, dict)
            or set(record) != {"path", "bytes", "sha256"}
            or record.get("path") != "outputs/03-compare-views/comparison.json"
        ):
            raise ControlPlaneError("v2 review queue lacks fixed comparison authority")
        comparison_path = run_root / record["path"]
        try:
            assert_existing_path_components_are_not_reparse(comparison_path)
        except ValueError as error:
            raise ControlPlaneError(str(error)) from error
        if not comparison_path.is_file() or file_identity(comparison_path) != {
            "bytes": record.get("bytes"),
            "sha256": record.get("sha256"),
        }:
            raise ControlPlaneError("v2 comparison authority changed")
        comparison_sha256 = str(record["sha256"])

    def fidelity(output: Path) -> Mapping[str, object]:
        output.mkdir(parents=True, exist_ok=False)
        argv = _python_argv(run, "audit_mineru_ai_merge_fidelity.py") + [
            "--mode", "v2" if run.get("schema") in mineru_cpu_first.RUN_SCHEMAS else "legacy-v1",
            "--decisions-root",
            str(decisions_root / "pages"),
            "--merge-packets-root",
            str(bundle_root / "merge_packets"),
            "--output",
            str(output / "audit.json"),
        ]
        if comparison_path is not None and comparison_sha256 is not None:
            queue_path = run_root / "review" / "review_queue.json"
            decision_set_path = decisions_root / "decision_set.json"
            argv += [
                "--review-queue", str(queue_path),
                "--review-queue-sha256", sha256_file(queue_path),
                "--comparison", str(comparison_path),
                "--comparison-sha256", comparison_sha256,
                "--decision-set", str(decision_set_path),
                "--decision-set-sha256", sha256_file(decision_set_path),
            ]
        allowlist = decision_set.get("reviewed_allowlist")
        if allowlist:
            allowlist_path = decisions_root / str(allowlist["path"])
            if not allowlist_path.is_file() or file_identity(allowlist_path) != {
                "bytes": allowlist["bytes"],
                "sha256": allowlist["sha256"],
            }:
                raise ControlPlaneError("reviewed allowlist identity mismatch")
            argv += ["--reviewed-allowlist", str(allowlist_path)]
        diagnostics = pipeline_process.run(argv, cwd=_repo_root())
        report = _read(output / "audit.json")
        if report.get("passed") is not True:
            raise ControlPlaneError("fidelity audit did not pass")
        _write_json(output / "command.json", diagnostics)
        return diagnostics

    def materialize(output: Path) -> Mapping[str, object]:
        output.mkdir(parents=True, exist_ok=False)
        argv = _python_argv(run, "materialize_mineru_ai_merge.py") + [
            "--bundle-root",
            str(bundle_root),
            "--raw-root",
            str(raw_root),
            "--decisions-root",
            str(decisions_root / "pages"),
            "--output-root",
            str(output / "candidate"),
        ]
        if comparison_path is not None and comparison_sha256 is not None:
            audit_path = _stage_output_path(run_root, 5, "fidelity_audit") / "audit.json"
            argv += [
                "--comparison",
                str(comparison_path),
                "--comparison-sha256",
                comparison_sha256,
                "--fidelity-audit", str(audit_path),
                "--fidelity-audit-sha256", sha256_file(audit_path),
            ]
        diagnostics = pipeline_process.run(argv, cwd=_repo_root())
        if not (output / "candidate").is_dir():
            raise ControlPlaneError("materializer did not create a candidate")
        _write_json(output / "command.json", diagnostics)
        return diagnostics

    return {
        "fidelity_audit": StageAdapter("fidelity_audit", fidelity),
        "materialize_candidate": StageAdapter(
            "materialize_candidate",
            materialize,
        ),
    }
