from __future__ import annotations

import hashlib
import json
import math
from itertools import combinations
from pathlib import Path, PurePosixPath
from typing import Any, Mapping, Sequence

from .identity import canonical_bytes, deterministic_inventory, file_identity, sha256_bytes


RUN_SCHEMA = "kb_creator.run_spec.v2"
RUN_SCHEMA_V3 = "kb_creator.run_spec.v3"
RUN_SCHEMA_V4 = "kb_creator.run_spec.v4"
RUN_SCHEMAS = frozenset({RUN_SCHEMA, RUN_SCHEMA_V3, RUN_SCHEMA_V4})
PROFILE = "mineru_cpu_first_three_view_v1"
VIEW_SCHEMA = "kb_creator.mineru_view_execution.v1"
VIEW_SET_SCHEMA = "kb_creator.mineru_view_set.v1"
COMPARISON_SCHEMA = "kb_creator.mineru_multi_view_comparison.v2"
OCR_LANGUAGES = frozenset(
    {
        "en",
        "ch",
        "chinese_cht",
        "korean",
        "japan",
        "latin",
        "arabic",
        "east_slavic",
        "cyrillic",
        "devanagari",
        "ta",
        "te",
        "ka",
        "th",
        "el",
    }
)
OPTIONAL_UNAVAILABLE_REASONS = frozenset(
    {
        "nvidia_device_not_detected",
        "nvidia_driver_or_nvidia_smi_missing",
        "nvidia_smi_query_failed",
        "unsupported_local_gpu",
    }
)
VIEW_PLAN: tuple[dict[str, Any], ...] = (
    {
        "view_id": "original_pipeline_txt",
        "required": True,
        "provider_id": "pipeline_cpu",
        "input_kind": "original",
        "backend": "pipeline",
        "method": "txt",
        "effort": None,
        "formula": True,
        "table": True,
    },
    {
        "view_id": "original_pipeline_ocr",
        "required": True,
        "provider_id": "pipeline_cpu",
        "input_kind": "original",
        "backend": "pipeline",
        "method": "ocr",
        "effort": None,
        "formula": True,
        "table": True,
    },
    {
        "view_id": "raster_pipeline_ocr",
        "required": True,
        "provider_id": "pipeline_cpu",
        "input_kind": "raster",
        "backend": "pipeline",
        "method": "ocr",
        "effort": None,
        "formula": True,
        "table": True,
    },
    {
        "view_id": "original_hybrid_high",
        "required": False,
        "provider_id": "hybrid_cuda",
        "input_kind": "original",
        "backend": "hybrid-engine",
        "method": "txt",
        "effort": "high",
        "formula": True,
        "table": True,
    },
    {
        "view_id": "original_vlm",
        "required": False,
        "provider_id": "vlm_cuda",
        "input_kind": "original",
        "backend": "vlm-engine",
        "method": None,
        "effort": None,
        "formula": True,
        "table": True,
    },
)
REQUIRED_VIEWS = tuple(row["view_id"] for row in VIEW_PLAN if row["required"])


class CpuFirstContractError(ValueError):
    pass


def _exact(value: object, keys: set[str], label: str) -> dict[str, Any]:
    if not isinstance(value, dict) or set(value) != keys:
        raise CpuFirstContractError(f"{label} has unexpected or missing fields")
    return value


def _safe_relative(value: object, label: str) -> Path:
    if not isinstance(value, str) or not value or "\\" in value or ":" in value:
        raise CpuFirstContractError(f"unsafe {label}")
    relative = PurePosixPath(value)
    if relative.is_absolute() or ".." in relative.parts or relative.as_posix() != value:
        raise CpuFirstContractError(f"unsafe {label}")
    return Path(*relative.parts)


def _identity_lower(path: Path) -> dict[str, Any]:
    identity = file_identity(path)
    return {"bytes": identity["bytes"], "sha256": identity["sha256"].lower()}


def _lower_seal(value: Mapping[str, Any], key: str, *, sorted_keys: bool) -> None:
    expected = value.get(key)
    if not isinstance(expected, str) or len(expected) != 64:
        raise CpuFirstContractError(f"invalid {key}")
    unsigned = {name: item for name, item in value.items() if name != key}
    encoded = json.dumps(
        unsigned,
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=sorted_keys,
    ).encode("utf-8")
    if hashlib.sha256(encoded).hexdigest() != expected:
        raise CpuFirstContractError(f"{key} mismatch")


def _source_inventory(source: Path) -> dict[str, Any]:
    rows = []
    for path in sorted(source.rglob("*"), key=lambda item: item.as_posix()):
        if not path.is_file() or "__pycache__" in path.parts or path.suffix in {".pyc", ".pyo"}:
            continue
        identity = _identity_lower(path)
        rows.append({"path": path.relative_to(source).as_posix(), **identity})
    encoded = json.dumps(rows, ensure_ascii=False, separators=(",", ":"), sort_keys=True).encode("utf-8")
    return {"file_count": len(rows), "sha256": hashlib.sha256(encoded).hexdigest()}


def validate_view_plan(value: object) -> list[dict[str, Any]]:
    if value != list(VIEW_PLAN):
        raise CpuFirstContractError("view plan is not the exact ordered CPU-first plan")
    serialized = json.dumps(value, sort_keys=True).lower()
    if "auto" in serialized or "http" in serialized or "url" in serialized or "executable" in serialized:
        raise CpuFirstContractError("view plan contains a forbidden selector or endpoint")
    return list(value)


def _profile_paths(provider_id: str, mineru_root: Path, source_root: Path) -> dict[str, Path]:
    cpu = provider_id == "pipeline_cpu"
    profile_id = "pipeline-cpu-v1" if cpu else "windows-cu128-v1"
    return {
        "python": mineru_root / "profiles" / profile_id / ".venv" / "Scripts" / "python.exe",
        "mineru": mineru_root / "profiles" / profile_id / ".venv" / "Scripts" / "mineru.exe",
        "verify_receipt": mineru_root / "profiles" / profile_id / "verify-receipt.json",
        "install_receipt": mineru_root / "profiles" / profile_id / "install-receipt.json",
        "config": mineru_root / "runtime" / profile_id / "mineru.json",
        "lock": source_root / ("requirements.windows-cpu-pipeline.lock.txt" if cpu else "requirements.windows-cu128-provider.lock.txt"),
    }


def _validate_profile(provider: Mapping[str, Any], mineru_root: Path, source_root: Path) -> tuple[dict[str, Any], dict[str, str]]:
    provider_id = str(provider["provider_id"])
    paths = _profile_paths(provider_id, mineru_root, source_root)
    receipt_record = provider.get("verification_receipt")
    if not isinstance(receipt_record, dict):
        raise CpuFirstContractError(f"ready provider lacks verification receipt: {provider_id}")
    expected_hint = f"profiles/{'pipeline-cpu-v1' if provider_id == 'pipeline_cpu' else 'windows-cu128-v1'}/verify-receipt.json"
    if receipt_record.get("path_hint") != expected_hint:
        raise CpuFirstContractError(f"provider verification path mismatch: {provider_id}")
    verify_path = paths["verify_receipt"]
    if not verify_path.is_file() or _identity_lower(verify_path) != {
        "bytes": receipt_record.get("bytes"),
        "sha256": receipt_record.get("sha256"),
    }:
        raise CpuFirstContractError(f"provider verification receipt identity mismatch: {provider_id}")
    verify = json.loads(verify_path.read_text(encoding="utf-8"))
    _lower_seal(verify, "receipt_sha256", sorted_keys=True)
    expected_profile = "mineru-pipeline-cpu-windows-v1" if provider_id == "pipeline_cpu" else "mineru-local-windows-cu128-v1"
    if verify.get("schema") != "nri.mineru_profile_verification.v1" or verify.get("profile") != expected_profile or verify.get("state") != "ready":
        raise CpuFirstContractError(f"provider verification receipt is not ready: {provider_id}")
    install_path = paths["install_receipt"]
    if not install_path.is_file():
        raise CpuFirstContractError(f"provider install receipt missing: {provider_id}")
    install = json.loads(install_path.read_text(encoding="utf-8"))
    _lower_seal(install, "receipt_sha256", sorted_keys=True)
    linked = verify.get("install_receipt")
    if not isinstance(linked, dict) or _identity_lower(install_path) != {"bytes": linked.get("bytes"), "sha256": linked.get("sha256")} or install.get("receipt_sha256") != linked.get("receipt_sha256"):
        raise CpuFirstContractError(f"provider install receipt linkage mismatch: {provider_id}")
    if install.get("profile") != expected_profile or not isinstance(install.get("installed_distributions"), dict):
        raise CpuFirstContractError(f"provider install inventory is invalid: {provider_id}")
    for key in ("python", "mineru", "config", "lock"):
        if not paths[key].is_file():
            raise CpuFirstContractError(f"provider input missing: {provider_id}:{key}")
    python_expected = install.get("python", {})
    if _identity_lower(paths["python"]) != {
        "bytes": python_expected.get("executable_bytes"),
        "sha256": python_expected.get("executable_sha256"),
    }:
        raise CpuFirstContractError(f"provider Python identity mismatch: {provider_id}")
    for key in ("config", "lock"):
        expected = verify.get(key)
        observed = _identity_lower(paths[key])
        if not isinstance(expected, dict) or observed != {"bytes": expected.get("bytes"), "sha256": expected.get("sha256")}:
            raise CpuFirstContractError(f"provider {key} identity mismatch: {provider_id}")
    source = source_root / "src"
    source_expected = install.get("source")
    if not source.is_dir() or not isinstance(source_expected, dict) or _source_inventory(source) != {
        "file_count": source_expected.get("file_count"),
        "sha256": source_expected.get("sha256"),
    }:
        raise CpuFirstContractError(f"provider source identity mismatch: {provider_id}")
    model = verify.get("model_manifest")
    rows = model.get("rows") if isinstance(model, dict) else None
    expected_count = 40 if provider_id == "pipeline_cpu" else 55
    if not isinstance(rows, list) or len(rows) != expected_count or model.get("required_rows") != expected_count:
        raise CpuFirstContractError(f"provider model evidence incomplete: {provider_id}")
    for row in rows:
        if not isinstance(row, dict) or set(row) != {"path", "bytes", "sha256"}:
            raise CpuFirstContractError(f"provider model row malformed: {provider_id}")
        model_path = source_root / _safe_relative(row["path"], "model path")
        if not model_path.is_file() or _identity_lower(model_path) != {"bytes": row["bytes"], "sha256": row["sha256"]}:
            raise CpuFirstContractError(f"provider model identity mismatch: {row.get('path')}")
    snapshot = {
        "provider": dict(provider),
        "verification_receipt": {**_identity_lower(verify_path), "receipt_sha256": verify["receipt_sha256"]},
        "install_receipt": {**_identity_lower(install_path), "receipt_sha256": install["receipt_sha256"]},
        "python": _identity_lower(paths["python"]),
        "mineru": _identity_lower(paths["mineru"]),
        "config": _identity_lower(paths["config"]),
        "lock": {**_identity_lower(paths["lock"]), "entries": verify["lock"]["entries"]},
        "installed_distributions": dict(sorted(install["installed_distributions"].items())),
        "source": install["source"],
        "model_manifest": model,
    }
    local = {name: str(path.resolve()) for name, path in paths.items()}
    return snapshot, local


def build_runtime_snapshot(runtime: object) -> tuple[dict[str, Any], dict[str, Any]]:
    capability_path = getattr(runtime, "provider_capabilities", None)
    source_root = getattr(runtime, "mineru_source_root", None)
    if capability_path is None or source_root is None:
        raise CpuFirstContractError("CPU-first runtime requires provider capabilities and MinerU source root")
    capability_path = Path(capability_path).resolve()
    mineru_root = Path(getattr(runtime, "mineru_root")).resolve()
    source_root = Path(source_root).resolve()
    if capability_path != (mineru_root / "capabilities" / "providers.json").resolve() or not capability_path.is_file():
        raise CpuFirstContractError("provider capability path is not the fixed local receipt")
    capability = json.loads(capability_path.read_text(encoding="utf-8"))
    _exact(capability, {"schema", "checked_at_utc", "execution_boundary", "providers", "receipt_sha256"}, "provider capability receipt")
    _lower_seal(capability, "receipt_sha256", sorted_keys=False)
    providers = capability.get("providers")
    if capability.get("schema") != "nri.mineru_provider_capabilities.v1" or capability.get("execution_boundary") != "current_station_local_only" or not isinstance(capability.get("checked_at_utc"), str) or not capability["checked_at_utc"] or not isinstance(providers, list) or [row.get("provider_id") for row in providers if isinstance(row, dict)] != ["pipeline_cpu", "hybrid_cuda", "vlm_cuda"]:
        raise CpuFirstContractError("provider capability snapshot is invalid or reordered")
    profiles: dict[str, Any] = {}
    local_profiles: dict[str, Any] = {}
    for index, provider in enumerate(providers):
        _exact(
            provider,
            {"provider_id", "required", "state", "reason_code", "profile", "verification_receipt"},
            "provider capability row",
        )
        expected_required = index == 0
        if not isinstance(provider, dict) or provider.get("required") is not expected_required:
            raise CpuFirstContractError("provider requirement flag mismatch")
        expected_profile = "mineru-pipeline-cpu-windows-v1" if index == 0 else "mineru-local-windows-cu128-v1"
        if provider.get("profile") != expected_profile:
            raise CpuFirstContractError("provider profile mismatch")
        state = provider.get("state")
        if index == 0:
            if state != "ready" or provider.get("reason_code") != "verified_cpu_profile":
                raise CpuFirstContractError("required pipeline_cpu provider is not ready")
        elif state == "invalid":
            raise CpuFirstContractError(f"optional provider is invalid: {provider.get('provider_id')}")
        elif state == "unavailable":
            if provider.get("reason_code") not in OPTIONAL_UNAVAILABLE_REASONS or provider.get("verification_receipt") is not None:
                raise CpuFirstContractError("optional provider has unsupported unavailable evidence")
            continue
        elif state != "ready" or provider.get("reason_code") != "verified_cuda_profile":
            raise CpuFirstContractError("optional provider state is invalid")
        receipt = provider.get("verification_receipt")
        if not isinstance(receipt, dict) or set(receipt) != {"path_hint", "bytes", "sha256"}:
            raise CpuFirstContractError("ready provider verification identity is malformed")
        snapshot, local = _validate_profile(provider, mineru_root, source_root)
        profiles[provider["provider_id"]] = snapshot
        local_profiles[provider["provider_id"]] = local
    common_paths = {
        "powershell": Path(getattr(runtime, "powershell")).resolve(),
        "pdftoppm": Path(getattr(runtime, "pdftoppm")).resolve(),
        "wrapper": (Path(__file__).resolve().parents[1] / "scripts" / "run_mineru_three_view.ps1").resolve(),
        "preparer": (Path(__file__).resolve().parents[1] / "scripts" / "prepare_mineru_three_view_inputs.py").resolve(),
        "profile_common": (Path(__file__).resolve().parents[2] / "MinerU" / "scripts" / "profile-common.ps1").resolve(),
        "profile_receipt": (Path(__file__).resolve().parents[2] / "MinerU" / "scripts" / "profile_receipt.py").resolve(),
    }
    for name, path in common_paths.items():
        if not path.is_file():
            raise CpuFirstContractError(f"CPU-first common tool missing: {name}")
    cpu_python = Path(local_profiles["pipeline_cpu"]["python"])
    if Path(getattr(runtime, "python")).resolve() != cpu_python:
        raise CpuFirstContractError("Stage 01 Python must be the verified CPU profile Python")
    portable = {
        "capability_snapshot": {
            "path_hint": "capabilities/providers.json",
            **_identity_lower(capability_path),
            "receipt_sha256": capability["receipt_sha256"],
            "providers": providers,
            "provider_receipt": capability,
        },
        "provider_profiles": profiles,
        "common_tools": {name: _identity_lower(path) for name, path in common_paths.items()},
    }
    local = {
        "provider_capabilities_path": str(capability_path),
        "mineru_source_root": str(source_root),
        "profile_paths": local_profiles,
        "common_paths": {name: str(path) for name, path in common_paths.items()},
    }
    return portable, local


def view_cache_key(run: Mapping[str, Any], descriptor: Mapping[str, Any], input_identity: Mapping[str, Any]) -> str:
    profile = run["provider_profiles"].get(descriptor["provider_id"])
    return sha256_bytes(
        canonical_bytes(
            {
                "run_identity_sha256": run["portable_identity_sha256"],
                "descriptor": descriptor,
                "input": input_identity,
                "capability_snapshot": run["capability_snapshot"],
                "provider_profile": profile,
                "argv_shape_version": 1,
                "wrapper": run["common_tools"]["wrapper"],
            }
        )
    )


def view_input_identity(run: Mapping[str, Any], descriptor: Mapping[str, Any]) -> tuple[Path, dict[str, Any]]:
    if descriptor["input_kind"] == "original":
        path = Path(run["local"]["source_path"])
        return path, {
            "kind": "original",
            "path_hint": run["source"]["path_hint"],
            "bytes": run["source"]["bytes"],
            "sha256": run["source"]["sha256"],
            "source_sha256": run["source"]["sha256"],
        }
    prepared_root = Path(run["local"]["run_root"]) / "outputs" / "01-prepare-inputs" / "prepared"
    manifest_path = prepared_root / "sample_pages.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    record = manifest.get("outputs", {}).get("raster_pdf")
    if not isinstance(record, dict):
        raise CpuFirstContractError("Stage 01 lacks raster output identity")
    path = prepared_root / str(record.get("name", ""))
    if not path.is_file() or {"name": path.name, **file_identity(path)} != record:
        raise CpuFirstContractError("Stage 01 raster identity mismatch")
    return path, {
        "kind": "raster",
        "path_hint": "outputs/01-prepare-inputs/prepared/" + path.name,
        **file_identity(path),
        "source_sha256": run["source"]["sha256"],
        "preparation_manifest": {"path_hint": "outputs/01-prepare-inputs/prepared/sample_pages.json", **file_identity(manifest_path)},
    }


def write_skipped_view(run: Mapping[str, Any], descriptor: Mapping[str, Any], input_identity: Mapping[str, Any], destination: Path) -> dict[str, Any]:
    provider = next(row for row in run["capability_snapshot"]["providers"] if row["provider_id"] == descriptor["provider_id"])
    if descriptor["required"] or provider["state"] != "unavailable" or provider["reason_code"] not in OPTIONAL_UNAVAILABLE_REASONS:
        raise CpuFirstContractError("only an unavailable optional provider can create a skipped view")
    payload = {
        "schema": VIEW_SCHEMA,
        "view_id": descriptor["view_id"],
        "required": False,
        "provider_id": descriptor["provider_id"],
        "run_identity_sha256": run["portable_identity_sha256"],
        "input": dict(input_identity),
        "execution_profile": {**dict(descriptor), "ocr_language": run["options"]["ocr_language"], "argv_shape_version": 1},
        "capability_snapshot": {key: run["capability_snapshot"][key] for key in ("bytes", "sha256", "receipt_sha256")},
        "provider_verification": None,
        "profile_identity": None,
        "state": "skipped",
        "reason_code": provider["reason_code"],
        "artifact_root": None,
        "output_inventory": [],
        "page_coverage": None,
        "exit_code": 0,
        "diagnostics": {"invoked": False},
        "blocked_by": {"provider_id": provider["provider_id"], "capability_receipt_sha256": run["capability_snapshot"]["receipt_sha256"]},
        "cache_key": view_cache_key(run, descriptor, input_identity),
    }
    payload["receipt_sha256"] = sha256_bytes(canonical_bytes(payload))
    destination.parent.mkdir(parents=True, exist_ok=False)
    destination.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return payload


def write_succeeded_view(
    run: Mapping[str, Any],
    descriptor: Mapping[str, Any],
    input_identity: Mapping[str, Any],
    artifact_root: Path,
    destination: Path,
    diagnostics: Mapping[str, Any],
) -> dict[str, Any]:
    provider = next(row for row in run["capability_snapshot"]["providers"] if row["provider_id"] == descriptor["provider_id"])
    if provider["state"] != "ready":
        raise CpuFirstContractError("only a ready provider can create a succeeded view")
    inventory = deterministic_inventory(artifact_root)
    content_rows = [row for row in inventory if row["path"].endswith("_content_list.json")]
    if len(content_rows) != 1:
        raise CpuFirstContractError("view requires exactly one content-list artifact")
    content = json.loads((artifact_root / content_rows[0]["path"]).read_text(encoding="utf-8"))
    indices = sorted({row.get("page_idx") for row in content if isinstance(row, dict) and isinstance(row.get("page_idx"), int)}) if isinstance(content, list) else []
    expected_indices = list(range(len(run["scope"]["ordered_pages"])))
    if indices != expected_indices:
        raise CpuFirstContractError("view content-list page coverage mismatch")
    profile = run["provider_profiles"][descriptor["provider_id"]]
    payload = {
        "schema": VIEW_SCHEMA,
        "view_id": descriptor["view_id"],
        "required": descriptor["required"],
        "provider_id": descriptor["provider_id"],
        "run_identity_sha256": run["portable_identity_sha256"],
        "input": dict(input_identity),
        "execution_profile": {**dict(descriptor), "ocr_language": run["options"]["ocr_language"], "argv_shape_version": 1},
        "capability_snapshot": {key: run["capability_snapshot"][key] for key in ("bytes", "sha256", "receipt_sha256")},
        "provider_verification": profile["verification_receipt"],
        "profile_identity": profile,
        "state": "succeeded",
        "reason_code": None,
        "artifact_root": f"views/{descriptor['view_id']}/artifacts",
        "output_inventory": inventory,
        "page_coverage": list(run["scope"]["ordered_pages"]),
        "exit_code": 0,
        "diagnostics": dict(diagnostics),
        "blocked_by": None,
        "cache_key": view_cache_key(run, descriptor, input_identity),
    }
    payload["receipt_sha256"] = sha256_bytes(canonical_bytes(payload))
    destination.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return payload


def _validate_upper_seal(value: Mapping[str, Any], key: str) -> None:
    expected = value.get(key)
    unsigned = {name: item for name, item in value.items() if name != key}
    if expected != sha256_bytes(canonical_bytes(unsigned)):
        raise CpuFirstContractError(f"{key} mismatch")


def validate_view_receipt(run: Mapping[str, Any], descriptor: Mapping[str, Any], path: Path, stage_root: Path) -> dict[str, Any]:
    receipt = json.loads(path.read_text(encoding="utf-8"))
    _exact(receipt, {"schema", "view_id", "required", "provider_id", "run_identity_sha256", "input", "execution_profile", "capability_snapshot", "provider_verification", "profile_identity", "state", "reason_code", "artifact_root", "output_inventory", "page_coverage", "exit_code", "diagnostics", "blocked_by", "cache_key", "receipt_sha256"}, "view receipt")
    _validate_upper_seal(receipt, "receipt_sha256")
    if receipt["schema"] != VIEW_SCHEMA or receipt["view_id"] != descriptor["view_id"] or receipt["required"] is not descriptor["required"] or receipt["provider_id"] != descriptor["provider_id"] or receipt["run_identity_sha256"] != run["portable_identity_sha256"]:
        raise CpuFirstContractError("view receipt identity mismatch")
    _, expected_input = view_input_identity(run, descriptor)
    if receipt["input"] != expected_input:
        raise CpuFirstContractError("view input lineage mismatch")
    expected_profile = {**dict(descriptor), "ocr_language": run["options"]["ocr_language"], "argv_shape_version": 1}
    if receipt["execution_profile"] != expected_profile or receipt["cache_key"] != view_cache_key(run, descriptor, receipt["input"]):
        raise CpuFirstContractError("view execution profile/cache mismatch")
    capability_identity = {key: run["capability_snapshot"][key] for key in ("bytes", "sha256", "receipt_sha256")}
    if receipt["capability_snapshot"] != capability_identity:
        raise CpuFirstContractError("view capability snapshot mismatch")
    provider = next(row for row in run["capability_snapshot"]["providers"] if row["provider_id"] == descriptor["provider_id"])
    view_dir = path.parent
    if receipt["state"] == "skipped":
        if descriptor["required"] or provider["state"] != "unavailable" or receipt["reason_code"] != provider["reason_code"] or receipt["provider_verification"] is not None or receipt["profile_identity"] is not None or receipt["artifact_root"] is not None or receipt["output_inventory"] != [] or receipt["page_coverage"] is not None or receipt["exit_code"] != 0 or receipt["diagnostics"] != {"invoked": False} or receipt["blocked_by"] != {"provider_id": provider["provider_id"], "capability_receipt_sha256": run["capability_snapshot"]["receipt_sha256"]}:
            raise CpuFirstContractError("invalid skipped view evidence")
        if any(item.name != "view.json" for item in view_dir.iterdir()):
            raise CpuFirstContractError("skipped view contains output artifacts")
        return receipt
    if receipt["state"] != "succeeded" or provider["state"] != "ready" or receipt["reason_code"] is not None or receipt["exit_code"] != 0 or receipt["blocked_by"] is not None:
        raise CpuFirstContractError("invalid succeeded view evidence")
    expected_profile_identity = run["provider_profiles"][descriptor["provider_id"]]
    if receipt["profile_identity"] != expected_profile_identity or receipt["provider_verification"] != expected_profile_identity["verification_receipt"]:
        raise CpuFirstContractError("view provider profile identity mismatch")
    expected_hint = f"views/{descriptor['view_id']}/artifacts"
    if receipt["artifact_root"] != expected_hint:
        raise CpuFirstContractError("view artifact root mismatch")
    artifact_root = stage_root / _safe_relative(expected_hint, "view artifact root")
    observed = deterministic_inventory(artifact_root)
    if receipt["output_inventory"] != observed:
        raise CpuFirstContractError("view output inventory mismatch")
    for suffix in ("_content_list.json", "_content_list_v2.json", "_middle.json", ".md", "_layout.pdf"):
        if sum(row["path"].endswith(suffix) for row in observed) != 1:
            raise CpuFirstContractError(f"view requires exactly one {suffix} artifact")
    content_row = next(row for row in observed if row["path"].endswith("_content_list.json"))
    content = json.loads((artifact_root / content_row["path"]).read_text(encoding="utf-8"))
    actual_indices = sorted(
        {
            row.get("page_idx")
            for row in content
            if isinstance(row, dict)
            and isinstance(row.get("page_idx"), int)
            and not isinstance(row.get("page_idx"), bool)
        }
    ) if isinstance(content, list) else []
    if actual_indices != list(range(len(run["scope"]["ordered_pages"]))):
        raise CpuFirstContractError("view content-list page coverage mismatch")
    if receipt["page_coverage"] != run["scope"]["ordered_pages"]:
        raise CpuFirstContractError("view page coverage mismatch")
    return receipt


def validate_view_set(run: Mapping[str, Any], stage_root: Path) -> dict[str, Any]:
    path = stage_root / "view-set.json"
    value = json.loads(path.read_text(encoding="utf-8"))
    _exact(value, {"schema", "run_identity_sha256", "ordered_view_plan", "required_succeeded", "succeeded_views", "views", "receipt_sha256"}, "view set")
    _validate_upper_seal(value, "receipt_sha256")
    validate_view_plan(value["ordered_view_plan"])
    if value["schema"] != VIEW_SET_SCHEMA or value["run_identity_sha256"] != run["portable_identity_sha256"] or value["required_succeeded"] != list(REQUIRED_VIEWS) or not isinstance(value["views"], list) or len(value["views"]) != len(VIEW_PLAN):
        raise CpuFirstContractError("view set identity or required set mismatch")
    succeeded = []
    for descriptor, record in zip(VIEW_PLAN, value["views"]):
        if not isinstance(record, dict) or set(record) != {"view_id", "state", "receipt"} or record["view_id"] != descriptor["view_id"]:
            raise CpuFirstContractError("view set row mismatch")
        receipt_path = stage_root / _safe_relative(record["receipt"]["path"], "view receipt path")
        expected_path = stage_root / "views" / descriptor["view_id"] / "view.json"
        if receipt_path != expected_path or not receipt_path.is_file():
            raise CpuFirstContractError("view receipt path mismatch")
        receipt = validate_view_receipt(run, descriptor, receipt_path, stage_root)
        expected_record = {"path": receipt_path.relative_to(stage_root).as_posix(), **file_identity(receipt_path), "receipt_sha256": receipt["receipt_sha256"]}
        if record["state"] != receipt["state"] or record["receipt"] != expected_record:
            raise CpuFirstContractError("view-set receipt identity mismatch")
        if receipt["state"] == "succeeded":
            succeeded.append(descriptor["view_id"])
    if value["succeeded_views"] != succeeded or succeeded[:3] != list(REQUIRED_VIEWS):
        raise CpuFirstContractError("view set succeeded order mismatch")
    return value


def write_view_set(run: Mapping[str, Any], stage_root: Path) -> dict[str, Any]:
    records = []
    succeeded = []
    for descriptor in VIEW_PLAN:
        path = stage_root / "views" / descriptor["view_id"] / "view.json"
        receipt = validate_view_receipt(run, descriptor, path, stage_root)
        records.append({"view_id": descriptor["view_id"], "state": receipt["state"], "receipt": {"path": path.relative_to(stage_root).as_posix(), **file_identity(path), "receipt_sha256": receipt["receipt_sha256"]}})
        if receipt["state"] == "succeeded":
            succeeded.append(descriptor["view_id"])
    payload = {"schema": VIEW_SET_SCHEMA, "run_identity_sha256": run["portable_identity_sha256"], "ordered_view_plan": list(VIEW_PLAN), "required_succeeded": list(REQUIRED_VIEWS), "succeeded_views": succeeded, "views": records}
    payload["receipt_sha256"] = sha256_bytes(canonical_bytes(payload))
    (stage_root / "view-set.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return validate_view_set(run, stage_root)


def validate_comparison(run: Mapping[str, Any], output: Path) -> dict[str, Any]:
    from kb_creator.scripts.compare_mineru_three_views import diff_blocks, inspect_view

    comparison_path = output / "comparison.json"
    value = json.loads(comparison_path.read_text(encoding="utf-8"))
    _exact(
        value,
        {
            "schema", "status", "run_identity_sha256", "manifest", "view_set",
            "required_views", "succeeded_views", "skipped_views", "views",
            "pairwise", "failures",
        },
        "multi-view comparison",
    )
    run_root = Path(str(run["local"]["run_root"]))
    prepared_path = run_root / "outputs" / "01-prepare-inputs" / "prepared" / "sample_pages.json"
    view_set_path = run_root / "outputs" / "02-mineru-three-view" / "view-set.json"
    view_set = validate_view_set(run, view_set_path.parent)
    expected_manifest = {"path": str(prepared_path), **file_identity(prepared_path)}
    expected_view_set = {
        "path": str(view_set_path),
        **file_identity(view_set_path),
        "receipt_sha256": view_set["receipt_sha256"],
    }
    succeeded = view_set["succeeded_views"]
    skipped = []
    for row in view_set["views"]:
        if row["state"] == "skipped":
            receipt_path = view_set_path.parent / _safe_relative(row["receipt"]["path"], "view receipt path")
            receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
            skipped.append({"view_id": row["view_id"], "reason_code": receipt["reason_code"], "receipt": row["receipt"]})
    expected_pairs = [f"{left}__vs__{right}" for left, right in combinations(succeeded, 2)]
    if (
        value["schema"] != COMPARISON_SCHEMA
        or value["status"] != "pass_for_review"
        or value["run_identity_sha256"] != run["portable_identity_sha256"]
        or value["manifest"] != expected_manifest
        or value["view_set"] != expected_view_set
        or value["required_views"] != list(REQUIRED_VIEWS)
        or value["succeeded_views"] != succeeded
        or value["skipped_views"] != skipped
        or not isinstance(value["views"], dict)
        or list(value["views"]) != succeeded
        or not isinstance(value["pairwise"], dict)
        or list(value["pairwise"]) != expected_pairs
        or value["failures"] != []
    ):
        raise CpuFirstContractError("Stage 03 comparison identity/view set mismatch")
    expected_indices = list(range(len(run["scope"]["ordered_pages"])))
    prepared = json.loads(prepared_path.read_text(encoding="utf-8"))
    source_pages = {
        row["sample_page"]: row["source_page"]
        for row in prepared["ordered_pages"]
    }
    observed_views: dict[str, Any] = {}
    for view_id in succeeded:
        view = value["views"][view_id]
        coverage = view.get("coverage") if isinstance(view, dict) else None
        artifacts = view.get("artifacts") if isinstance(view, dict) else None
        if (
            not isinstance(coverage, dict)
            or coverage.get("expected_page_idx") != expected_indices
            or coverage.get("actual_page_idx") != expected_indices
            or coverage.get("missing_page_idx") != []
            or coverage.get("extra_page_idx") != []
            or not isinstance(artifacts, dict)
            or not isinstance(artifacts.get("layout_pdf"), str)
            or not artifacts["layout_pdf"]
        ):
            raise CpuFirstContractError("Stage 03 comparison coverage/layout mismatch")
        receipt_row = next(row for row in view_set["views"] if row["view_id"] == view_id)
        receipt_path = view_set_path.parent / _safe_relative(receipt_row["receipt"]["path"], "view receipt path")
        receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
        artifact_root = view_set_path.parent / _safe_relative(receipt["artifact_root"], "view artifact root")
        observed_views[view_id] = inspect_view(artifact_root, source_pages)
        if view != observed_views[view_id]:
            raise CpuFirstContractError("Stage 03 comparison view evidence is stale")
    expected_pairwise = {
        f"{left}__vs__{right}": diff_blocks(observed_views[left]["blocks"], observed_views[right]["blocks"])
        for left, right in combinations(succeeded, 2)
    }
    if value["pairwise"] != expected_pairwise:
        raise CpuFirstContractError("Stage 03 pairwise evidence is stale")
    return value


def validate_stage_output(run: Mapping[str, Any], name: str, output: Path) -> None:
    if name == "prepare_inputs":
        from kb_creator.scripts.prepare_mineru_three_view_inputs import _verify_raster_pdf

        manifest_path = output / "prepared" / "sample_pages.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        mapping = manifest.get("ordered_pages")
        render = manifest.get("render")
        raster = manifest.get("outputs", {}).get("raster_pdf")
        expected_mapping = [{"sample_page": page, "source_page": page} for page in run["scope"]["ordered_pages"]]
        raster_path = output / "prepared" / str(raster.get("name", "")) if isinstance(raster, dict) else Path()
        mixed = "page_geometry" in run["source"]
        expected_displayed = list(run["source"].get("media_box_points", []))
        if not mixed and run["source"]["rotation_degrees"] in (90, 270):
            expected_displayed.reverse()
        geometry = render.get("page_geometry", []) if isinstance(render, dict) else []
        expected_schema = "kb_creator.mineru_three_view_inputs.v3" if mixed else "kb_creator.mineru_three_view_inputs.v2"
        if manifest.get("schema") != expected_schema or manifest.get("mode") != "raster_only" or mapping != expected_mapping or not isinstance(render, dict) or render.get("source_box") != "MediaBox" or render.get("geometry_policy") != run["options"]["geometry_policy"] or render.get("raster_has_text_layer") is not False or len(geometry) != len(expected_mapping) or (not mixed and any(row.get("displayed_page_size_points") != expected_displayed or row.get("raster_pdf_page_size_points") != expected_displayed for row in geometry)) or any(row.get("raster_pdf_rotation_degrees") != 0 or row.get("raster_pdf_user_unit") != 1.0 or row.get("source_user_unit") != 1.0 for row in geometry) or manifest.get("source", {}).get("bytes") != run["source"]["bytes"] or manifest.get("source", {}).get("sha256") != run["source"]["sha256"] or not raster_path.is_file() or {"name": raster_path.name, **file_identity(raster_path)} != raster:
            raise CpuFirstContractError("Stage 01 preparation lineage/MediaBox contract failed")
        try:
            from pypdf import PdfReader
            source_path = Path(str(run["local"]["source_path"]))
            if file_identity(source_path) != {key: run["source"][key] for key in ("bytes", "sha256")}:
                raise CpuFirstContractError("Stage 01 source identity changed")
            source_reader = PdfReader(str(source_path))
            if mixed:
                from .reconstruction import _validate_page_geometry
                _validate_page_geometry(run["source"]["page_geometry"], run["source"]["page_count"])
                if "page_size_points" in render or "rotation_degrees" in render:
                    raise CpuFirstContractError("mixed source has a scalar geometry authority")
            for record, mapping_row in zip(geometry, expected_mapping):
                source_page = source_reader.pages[mapping_row["source_page"] - 1]
                media = [float(source_page.mediabox.left), float(source_page.mediabox.bottom), float(source_page.mediabox.right), float(source_page.mediabox.top)]
                crop = [float(source_page.cropbox.left), float(source_page.cropbox.bottom), float(source_page.cropbox.right), float(source_page.cropbox.top)]
                raw = [float(source_page.mediabox.width), float(source_page.mediabox.height)]
                rotation = int(source_page.get("/Rotate", 0)) % 360
                displayed = raw if rotation in (0, 180) else list(reversed(raw))
                expected_pixels = [math.ceil(value * render["dpi"] / 72.0) for value in displayed]
                if mixed:
                    observed = {"source_page": mapping_row["source_page"], "media_box_coordinates": media, "crop_box_coordinates": crop, "rotation_degrees": rotation, "user_unit": float(source_page.get("/UserUnit", 1))}
                    if run["source"]["page_geometry"][mapping_row["source_page"] - 1] != observed:
                        raise CpuFirstContractError(f"Stage 01 source geometry authority mismatch: page {mapping_row['source_page']}")
                if (
                    record.get("source_page") != mapping_row["source_page"]
                    or record.get("media_box_coordinates") != media
                    or record.get("crop_box_coordinates") != crop
                    or record.get("source_rotation_degrees") != rotation
                    or record.get("source_user_unit") != float(source_page.get("/UserUnit", 1))
                    or record.get("raster_pdf_page_size_points") != displayed
                    or record.get("displayed_page_size_points") != displayed
                    or record.get("raster_pixel_dimensions") != expected_pixels
                ):
                    raise CpuFirstContractError("Stage 01 source geometry evidence is stale")
            if _verify_raster_pdf(raster_path, geometry, PdfReader) != manifest.get("raster_pdf_verification"):
                raise CpuFirstContractError("Stage 01 raster PDF verification evidence is stale")
        except CpuFirstContractError:
            raise
        except (OSError, ValueError) as error:
            raise CpuFirstContractError("Stage 01 raster PDF verification failed") from error
    elif name == "mineru_three_view":
        validate_view_set(run, output)
    elif name == "compare_views":
        validate_comparison(run, output)
    elif name == "visual_merge_bundle":
        from kb_creator.scripts.build_mineru_visual_merge_bundle import (
            _packet_pairwise,
            _page_view,
            build_geometry_plan,
            find_layout_pdf,
            review_signals,
            role_for_page,
            validate_v2_bundle,
        )

        run_root = Path(str(run["local"]["run_root"]))
        view_set = validate_view_set(run, run_root / "outputs" / "02-mineru-three-view")
        comparison = validate_comparison(run, run_root / "outputs" / "03-compare-views")
        manifest_path = output / "visual" / "visual_manifest.json"
        if not manifest_path.is_file():
            raise CpuFirstContractError("Stage 04 lacks the v2 visual manifest")
        visual_manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        geometry_path = output / "visual" / "geometry_plan.json"
        geometry = json.loads(geometry_path.read_text(encoding="utf-8"))
        prepared_path = run_root / "outputs" / "01-prepare-inputs" / "prepared" / "sample_pages.json"
        pdftoppm = Path(str(run["local"]["common_paths"]["pdftoppm"]))
        if (
            geometry.get("run_identity_sha256") != run["portable_identity_sha256"]
            or geometry.get("policy") != run["options"]["geometry_policy"]
            or geometry.get("review_dpi") != run["options"]["review_dpi"]
            or geometry.get("rounding_rule") != run["options"]["geometry_rounding_rule"]
            or geometry.get("tolerances") != {
                "dimension_points": run["options"]["geometry_dimension_tolerance_points"],
                "relative_aspect_ratio": run["options"]["geometry_relative_aspect_tolerance"],
                "pixels": run["options"]["geometry_pixel_tolerance"],
            }
            or geometry.get("renderer", {}).get("argv_recipe") != run["options"]["geometry_renderer_recipe"]
            or geometry.get("succeeded_views") != view_set["succeeded_views"]
            or geometry.get("preparation_manifest") != {"path_hint": "outputs/01-prepare-inputs/prepared/sample_pages.json", **file_identity(prepared_path)}
            or geometry.get("renderer", {}).get("sha256") != file_identity(pdftoppm)["sha256"]
        ):
            raise CpuFirstContractError("Stage 04 visual geometry identity graph mismatch")
        try:
            views = tuple(view_set["succeeded_views"])
            layouts = {view: find_layout_pdf(run_root / "outputs" / "02-mineru-three-view", view, cpu_first=True) for view in views}
            recomputed = build_geometry_plan(
                prepared_manifest=json.loads(prepared_path.read_text(encoding="utf-8")),
                prepared_identity={"path_hint": "outputs/01-prepare-inputs/prepared/sample_pages.json", **file_identity(prepared_path)},
                layouts=layouts,
                views=views,
                dpi=run["options"]["review_dpi"],
                renderer=geometry["renderer"],
                run_identity_sha256=run["portable_identity_sha256"],
                source_identity={"path_hint": run["source"]["path_hint"], **file_identity(Path(str(run["local"]["source_path"])))},
                comparison_identity={"path_hint": "outputs/03-compare-views/comparison.json", **file_identity(run_root / "outputs" / "03-compare-views" / "comparison.json")},
                view_set_identity={"path_hint": "outputs/02-mineru-three-view/view-set.json", **file_identity(run_root / "outputs" / "02-mineru-three-view" / "view-set.json"), "receipt_sha256": view_set["receipt_sha256"]},
            )
            observed_base = {key: value for key, value in geometry.items() if key not in {"rendered_pages", "plan_sha256"}}
            recomputed_base = {key: value for key, value in recomputed.items() if key not in {"rendered_pages", "plan_sha256"}}
            if recomputed_base != observed_base:
                raise CpuFirstContractError("Stage 04 visual geometry plan is stale")
        except (OSError, ValueError, KeyError) as error:
            raise CpuFirstContractError("Stage 04 visual geometry preflight cannot be reproduced") from error
        expected_pairs = list(comparison["pairwise"])
        contract = json.loads(Path(str(run["local"]["contract_path"])).read_text(encoding="utf-8"))
        roles = tuple((row["first_page"], row["last_page"], row["role"]) for row in contract["page_roles"])
        for page in run["scope"]["ordered_pages"]:
            packet = output / "merge_packets" / "pages" / f"page-{page:03d}.json"
            if not packet.is_file():
                raise CpuFirstContractError(f"Stage 04 lacks open page packet {page}")
            data = json.loads(packet.read_text(encoding="utf-8"))
            _exact(data, {"schema", "source_page", "semantic_role", "views", "pairwise", "review_signals"}, "merge packet")
            expected_views = {
                view_id: _page_view(comparison["views"][view_id], page)
                for view_id in view_set["succeeded_views"]
            }
            expected = {
                "schema": "kb_creator.mineru_merge_packet.v1",
                "source_page": page,
                "semantic_role": role_for_page(page, roles),
                "views": expected_views,
                "pairwise": _packet_pairwise(comparison["pairwise"], comparison["views"], page),
                "review_signals": review_signals(expected_views, REQUIRED_VIEWS),
            }
            if data != expected or list(data["pairwise"]) != expected_pairs:
                raise CpuFirstContractError("Stage 04 CPU triptych/view order mismatch")
        try:
            validate_v2_bundle(output, visual_manifest)
        except (OSError, ValueError, KeyError) as error:
            raise CpuFirstContractError("Stage 04 visual geometry evidence failed") from error
