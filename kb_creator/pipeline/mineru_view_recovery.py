"""Import one sealed successful MinerU view into a fresh Stage 02 staging area."""
from __future__ import annotations

import json
import os
import copy
import io
import zipfile
from pathlib import Path, PurePosixPath
from typing import Any, Mapping

from . import mineru_cpu_first
from .identity import (
    assert_existing_path_components_are_not_reparse,
    canonical_bytes,
    deterministic_inventory,
    file_identity,
    is_reparse_point,
    sha256_bytes,
)


SCHEMA = "kb_creator.mineru_verified_view_import.v1"
WRAPPER_COMPATIBILITY_SCHEMA = "kb_creator.mineru_view_wrapper_compatibility.v1"
SOURCE_PROFILE_COMPATIBILITY_SCHEMA = "kb_creator.mineru_source_profile_compatibility.v1"
ALLOWED_SOURCE_PROFILE_PATHS = (
    "backend/pipeline/pipeline_analyze.py",
    "utils/pdf_image_tools.py",
)


class ViewRecoveryError(ValueError):
    """A historical succeeded view cannot be safely imported."""


def _descriptor(view_id: str) -> dict[str, Any]:
    matches = [row for row in mineru_cpu_first.VIEW_PLAN if row["view_id"] == view_id]
    if len(matches) != 1:
        raise ViewRecoveryError("unknown view id")
    return dict(matches[0])


def _seal(value: Mapping[str, Any], key: str) -> dict[str, Any]:
    result = dict(value)
    result[key] = sha256_bytes(canonical_bytes(result))
    return result


def _validate_wrapper_compatibility(
    origin_run: Mapping[str, Any], fresh_run: Mapping[str, Any], view_id: str,
    record: Mapping[str, Any] | None,
) -> dict[str, Any] | None:
    origin = origin_run["common_tools"]["wrapper"]
    fresh = fresh_run["common_tools"]["wrapper"]
    if origin == fresh:
        if record is not None:
            raise ViewRecoveryError("wrapper compatibility is unnecessary")
        return None
    if not isinstance(record, Mapping) or set(record) != {
        "schema", "view_id", "origin_wrapper", "fresh_wrapper", "rationale", "compatibility_sha256",
    }:
        raise ViewRecoveryError("wrapper compatibility record missing or malformed")
    unsigned = {key: value for key, value in record.items() if key != "compatibility_sha256"}
    if (
        record["schema"] != WRAPPER_COMPATIBILITY_SCHEMA
        or record["view_id"] != view_id
        or record["origin_wrapper"] != origin
        or record["fresh_wrapper"] != fresh
        or not isinstance(record["rationale"], str)
        or not record["rationale"].strip()
        or record["compatibility_sha256"] != sha256_bytes(canonical_bytes(unsigned))
    ):
        raise ViewRecoveryError("wrapper compatibility record is not sealed for these runs")
    return dict(record)


def _validate_equivalence(
    origin_run: Mapping[str, Any], fresh_run: Mapping[str, Any], descriptor: Mapping[str, Any],
    source_profile_compatibility: Mapping[str, Any] | None = None,
) -> dict[str, Any] | None:
    try:
        origin_source = origin_run["source"]
        fresh_source = fresh_run["source"]
        if (
            {key: origin_source.get(key) for key in ("bytes", "sha256", "page_count")}
            != {key: fresh_source.get(key) for key in ("bytes", "sha256", "page_count")}
            or origin_run["scope"]["ordered_pages"] != fresh_run["scope"]["ordered_pages"]
        ):
            raise ViewRecoveryError("source or page scope differs")
        if origin_run["options"]["ocr_language"] != fresh_run["options"]["ocr_language"]:
            raise ViewRecoveryError("OCR language differs")
        if source_profile_compatibility is not None:
            _validate_cross_profile_semantics(origin_run, fresh_run, descriptor)
            return _validate_source_profile_compatibility(
                origin_run, fresh_run, descriptor, source_profile_compatibility,
            )
        if origin_run["capability_snapshot"] != fresh_run["capability_snapshot"]:
            raise ViewRecoveryError("provider capability differs")
        provider_id = descriptor["provider_id"]
        if origin_run["provider_profiles"].get(provider_id) != fresh_run["provider_profiles"].get(provider_id):
            raise ViewRecoveryError("provider profile or model identity differs")
        for name, identity in origin_run["common_tools"].items():
            if name != "wrapper" and fresh_run["common_tools"].get(name) != identity:
                raise ViewRecoveryError("runtime identity differs")
    except KeyError as error:
        raise ViewRecoveryError(f"run lacks recovery binding: {error}") from error
    return None


def _validate_cross_profile_semantics(
    origin_run: Mapping[str, Any], fresh_run: Mapping[str, Any], descriptor: Mapping[str, Any],
) -> None:
    """Keep only receipt/source-inventory churn outside the reviewed transport pair."""
    provider_id = descriptor["provider_id"]
    if origin_run["source"] != fresh_run["source"] or origin_run["scope"] != fresh_run["scope"]:
        raise ViewRecoveryError("source, geometry, or page scope differs")
    if origin_run["options"] != fresh_run["options"] or origin_run["view_plan"] != fresh_run["view_plan"]:
        raise ViewRecoveryError("OCR execution semantics differ")
    origin_provider = next(row for row in origin_run["capability_snapshot"]["providers"] if row["provider_id"] == provider_id)
    fresh_provider = next(row for row in fresh_run["capability_snapshot"]["providers"] if row["provider_id"] == provider_id)
    if {key: value for key, value in origin_provider.items() if key != "verification_receipt"} != {key: value for key, value in fresh_provider.items() if key != "verification_receipt"}:
        raise ViewRecoveryError("provider device or profile semantics differ")
    semantic_profile_keys = ("python", "lock", "installed_distributions", "model_manifest")
    origin_profile = origin_run["provider_profiles"][provider_id]
    fresh_profile = fresh_run["provider_profiles"][provider_id]
    if origin_profile["source"].get("version") != fresh_profile["source"].get("version"):
        raise ViewRecoveryError("MinerU source version differs")
    if any(origin_profile.get(key) != fresh_profile.get(key) for key in semantic_profile_keys):
        raise ViewRecoveryError("provider model, lock, config, or launcher semantics differ")
    if not _equivalent_profile_config(origin_run, fresh_run, provider_id):
        raise ViewRecoveryError("provider config semantics differ")
    if not _equivalent_launcher(origin_run, fresh_run, provider_id):
        raise ViewRecoveryError("provider launcher semantics differ")
    for name, identity in origin_run["common_tools"].items():
        if name != "wrapper" and fresh_run["common_tools"].get(name) != identity:
            raise ViewRecoveryError("common runtime tool semantics differ")


def _profile_file(run: Mapping[str, Any], provider_id: str, name: str) -> Path:
    try:
        return Path(str(run["local"]["profile_paths"][provider_id][name])).resolve(strict=True)
    except (KeyError, OSError) as error:
        raise ViewRecoveryError(f"profile {name} path is unavailable") from error


def _normal_path(value: str, run: Mapping[str, Any]) -> str:
    candidate = Path(value)
    if not candidate.is_absolute(): return value
    try: resolved = candidate.resolve(strict=False)
    except OSError as error: raise ViewRecoveryError("config path cannot be resolved") from error
    for key in ("mineru_source_root", "mineru_root"):
        root = Path(str(run["local"][key])).resolve()
        if resolved.is_relative_to(root): return f"<{key}>/{resolved.relative_to(root).as_posix()}"
    raise ViewRecoveryError("config references an external path")


def _normalized_config(run: Mapping[str, Any], provider_id: str) -> object:
    path = _profile_file(run, provider_id, "config")
    if mineru_cpu_first._identity_lower(path) != run["provider_profiles"][provider_id]["config"]:
        raise ViewRecoveryError("config identity does not match verified profile")
    try: value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error: raise ViewRecoveryError("config is not valid JSON") from error
    def walk(item: Any) -> Any:
        if isinstance(item, dict): return {key: walk(value) for key, value in item.items()}
        if isinstance(item, list): return [walk(value) for value in item]
        return _normal_path(item, run) if isinstance(item, str) else item
    return walk(value)


def _equivalent_profile_config(origin: Mapping[str, Any], fresh: Mapping[str, Any], provider_id: str) -> bool:
    return _normalized_config(origin, provider_id) == _normalized_config(fresh, provider_id)


def _equivalent_launcher(origin: Mapping[str, Any], fresh: Mapping[str, Any], provider_id: str) -> bool:
    if origin["provider_profiles"][provider_id]["mineru"] == fresh["provider_profiles"][provider_id]["mineru"]:
        return True
    first, second = (_profile_file(run, provider_id, "mineru") for run in (origin, fresh))
    for path, run in ((first, origin), (second, fresh)):
        if mineru_cpu_first._identity_lower(path) != run["provider_profiles"][provider_id]["mineru"]:
            raise ViewRecoveryError("launcher identity does not match verified profile")
    def semantic_body(run: Mapping[str, Any], body: bytes) -> tuple[bytes, bytes]:
        marker = body.rfind(b"#!")
        if marker < 0: raise ViewRecoveryError("launcher lacks distlib shebang")
        end = body.find(b"\n", marker)
        expected = b"#!" + str(_profile_file(run, provider_id, "python")).encode("utf-8")
        if end < 0 or body[marker:end] != expected: raise ViewRecoveryError("launcher shebang is not bound to profile Python")
        archive = body[end + 1:]
        try:
            with zipfile.ZipFile(io.BytesIO(archive)) as bundle:
                if bundle.namelist() != ["__main__.py"]: raise ViewRecoveryError("launcher distlib archive is unexpected")
                return body[:marker], bundle.read("__main__.py")
        except zipfile.BadZipFile as error: raise ViewRecoveryError("launcher distlib archive is invalid") from error
    return semantic_body(origin, first.read_bytes()) == semantic_body(fresh, second.read_bytes())


def source_profile_compatibility_record(
    origin_run: Mapping[str, Any], fresh_run: Mapping[str, Any], view_id: str,
    changed_sources: Mapping[str, Mapping[str, Mapping[str, Any]]],
) -> dict[str, Any]:
    """Seal the sole reviewed source-profile difference for one imported view."""
    descriptor = _descriptor(view_id)
    if set(changed_sources) != set(ALLOWED_SOURCE_PROFILE_PATHS):
        raise ViewRecoveryError("source profile changed-source set is not approved")
    for path in ALLOWED_SOURCE_PROFILE_PATHS:
        row = changed_sources[path]
        if set(row) != {"origin", "fresh"} or any(
            not isinstance(row[name], Mapping) or set(row[name]) != {"bytes", "sha256"}
            for name in ("origin", "fresh")
        ):
            raise ViewRecoveryError("source profile changed-source identity is malformed")
        if row["origin"] == row["fresh"]:
            raise ViewRecoveryError("source profile approved file did not change")
    provider_id = descriptor["provider_id"]
    value: dict[str, Any] = {
        "schema": SOURCE_PROFILE_COMPATIBILITY_SCHEMA,
        "view_id": view_id,
        "origin": {
            "run_identity_sha256": origin_run["portable_identity_sha256"],
            "source": copy.deepcopy(origin_run["source"]), "scope": copy.deepcopy(origin_run["scope"]),
            "options": copy.deepcopy(origin_run["options"]), "capability_snapshot": copy.deepcopy(origin_run["capability_snapshot"]),
            "provider": copy.deepcopy(next(row for row in origin_run["capability_snapshot"]["providers"] if row["provider_id"] == provider_id)),
            "provider_profile": copy.deepcopy(origin_run["provider_profiles"][provider_id]),
            "common_tools": copy.deepcopy(origin_run["common_tools"]), "view_descriptor": descriptor,
        },
        "fresh": {
            "run_identity_sha256": fresh_run["portable_identity_sha256"],
            "source": copy.deepcopy(fresh_run["source"]), "scope": copy.deepcopy(fresh_run["scope"]),
            "options": copy.deepcopy(fresh_run["options"]), "capability_snapshot": copy.deepcopy(fresh_run["capability_snapshot"]),
            "provider": copy.deepcopy(next(row for row in fresh_run["capability_snapshot"]["providers"] if row["provider_id"] == provider_id)),
            "provider_profile": copy.deepcopy(fresh_run["provider_profiles"][provider_id]),
            "common_tools": copy.deepcopy(fresh_run["common_tools"]), "view_descriptor": descriptor,
        },
        "changed_sources": {path: {name: dict(value) for name, value in changed_sources[path].items()} for path in ALLOWED_SOURCE_PROFILE_PATHS},
    }
    return _seal(value, "compatibility_sha256")


def source_profile_compatibility_from_runs(
    origin_run: Mapping[str, Any], fresh_run: Mapping[str, Any], view_id: str,
) -> dict[str, Any]:
    """Inventory both sealed profile sources and allow exactly the reviewed transport pair."""
    try:
        source_roots = [Path(str(run["local"]["mineru_source_root"])).resolve() / "src" for run in (origin_run, fresh_run)]
        for source_root, run in zip(source_roots, (origin_run, fresh_run)):
            sealed_source = run["provider_profiles"]["pipeline_cpu"]["source"]
            if mineru_cpu_first._source_inventory(source_root) != {
                key: sealed_source.get(key) for key in ("file_count", "sha256")
            }:
                raise ViewRecoveryError("sealed profile source inventory mismatch")
        roots = [source_root / "mineru" for source_root in source_roots]
        inventories = []
        for root in roots:
            if not root.is_dir():
                raise ViewRecoveryError("source profile package root is unavailable")
            inventories.append({path.relative_to(root).as_posix(): file_identity(path) for path in root.rglob("*") if path.is_file() and "__pycache__" not in path.parts and path.suffix not in {".pyc", ".pyo"}})
        changed = {path for path in set(inventories[0]) | set(inventories[1]) if inventories[0].get(path) != inventories[1].get(path)}
        if changed != set(ALLOWED_SOURCE_PROFILE_PATHS):
            raise ViewRecoveryError("source profile contains an unapproved source change")
        return source_profile_compatibility_record(origin_run, fresh_run, view_id, {
            path: {"origin": inventories[0][path], "fresh": inventories[1][path]}
            for path in ALLOWED_SOURCE_PROFILE_PATHS
        })
    except (KeyError, OSError) as error:
        raise ViewRecoveryError("source profile inventory failed") from error


def _validate_source_profile_compatibility(
    origin_run: Mapping[str, Any], fresh_run: Mapping[str, Any], descriptor: Mapping[str, Any], record: Mapping[str, Any],
) -> dict[str, Any]:
    required = {"schema", "view_id", "origin", "fresh", "changed_sources", "compatibility_sha256"}
    if set(record) != required or record.get("schema") != SOURCE_PROFILE_COMPATIBILITY_SCHEMA:
        raise ViewRecoveryError("source profile compatibility record missing or malformed")
    unsigned = {key: value for key, value in record.items() if key != "compatibility_sha256"}
    if record.get("compatibility_sha256") != sha256_bytes(canonical_bytes(unsigned)):
        raise ViewRecoveryError("source profile compatibility record is not sealed")
    expected = source_profile_compatibility_from_runs(origin_run, fresh_run, descriptor["view_id"])
    if dict(record) != expected:
        raise ViewRecoveryError("source profile compatibility record is not bound to these runs")
    return dict(record)


def _safe_copy_tree(origin: Path, destination: Path, expected_inventory: list[dict[str, Any]]) -> None:
    try:
        assert_existing_path_components_are_not_reparse(origin)
        assert_existing_path_components_are_not_reparse(destination)
    except ValueError as error:
        raise ViewRecoveryError("artifact copy path crosses a reparse point") from error
    if destination.exists():
        raise ViewRecoveryError("fresh view destination already exists")
    if origin.is_symlink() or is_reparse_point(origin) or not origin.is_dir():
        raise ViewRecoveryError("origin artifact root is unsafe")
    for item in origin.rglob("*"):
        relative = item.relative_to(origin)
        pure = PurePosixPath(relative.as_posix())
        if item.is_symlink() or is_reparse_point(item) or not pure.parts or any(part in {"", ".", ".."} for part in pure.parts):
            raise ViewRecoveryError("origin artifact tree is unsafe")
        if item.is_file() and getattr(item.stat(), "st_nlink", 1) != 1:
            raise ViewRecoveryError("origin artifact is hardlinked")
    observed = deterministic_inventory(origin)
    if observed != expected_inventory:
        raise ViewRecoveryError("origin artifact inventory mismatch")
    destination.mkdir(parents=True)
    try:
        assert_existing_path_components_are_not_reparse(destination)
    except ValueError as error:
        raise ViewRecoveryError("fresh artifact destination crosses a reparse point") from error
    for row in observed:
        source = origin / row["path"]
        target = destination / row["path"]
        target.parent.mkdir(parents=True, exist_ok=True)
        try:
            assert_existing_path_components_are_not_reparse(target.parent)
        except ValueError as error:
            raise ViewRecoveryError("fresh artifact destination crosses a reparse point") from error
        with source.open("rb") as inp, target.open("xb") as out:
            while chunk := inp.read(1024 * 1024):
                out.write(chunk)
            out.flush()
            os.fsync(out.fileno())
        if file_identity(target) != {"bytes": row["bytes"], "sha256": row["sha256"]}:
            raise ViewRecoveryError("copied artifact identity mismatch")
    if deterministic_inventory(destination) != observed:
        raise ViewRecoveryError("copied artifact inventory mismatch")


def _copy_origin_receipt(origin_receipt_path: Path, fresh_view: Path) -> dict[str, Any]:
    evidence = fresh_view / "evidence" / "origin-view.json"
    try:
        assert_existing_path_components_are_not_reparse(origin_receipt_path)
        assert_existing_path_components_are_not_reparse(evidence)
        raw = origin_receipt_path.read_bytes()
        evidence.parent.mkdir(parents=True, exist_ok=True)
        assert_existing_path_components_are_not_reparse(evidence.parent)
        with evidence.open("xb") as stream:
            stream.write(raw)
            stream.flush()
            os.fsync(stream.fileno())
    except (OSError, ValueError) as error:
        raise ViewRecoveryError("origin receipt evidence copy failed") from error
    if evidence.read_bytes() != raw:
        raise ViewRecoveryError("origin receipt evidence copy mismatch")
    return {"path_hint": evidence.relative_to(fresh_view.parent.parent).as_posix(), **file_identity(evidence)}


def import_verified_succeeded_view(
    origin_run: Mapping[str, Any], origin_stage_root: Path,
    fresh_run: Mapping[str, Any], fresh_stage_root: Path, view_id: str,
    *, wrapper_compatibility: Mapping[str, Any] | None = None,
    source_profile_compatibility: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Validate and copy a historical succeeded view, then bind a fresh receipt.

    Callers must load and seal-validate both run records before this boundary:
    `reconstruction.load_run` for each run, plus their own fresh-run/root binding
    checks.  This adapter validates only the supplied Stage02 view authority and
    its cross-run identities; it does not authorize a run for execution.
    """
    descriptor = _descriptor(view_id)
    profile_compatibility = _validate_equivalence(origin_run, fresh_run, descriptor, source_profile_compatibility)
    compatibility = _validate_wrapper_compatibility(origin_run, fresh_run, view_id, wrapper_compatibility)
    origin_receipt_path = origin_stage_root / "views" / view_id / "view.json"
    try:
        origin_receipt = mineru_cpu_first.validate_view_receipt(
            origin_run, descriptor, origin_receipt_path, origin_stage_root,
        )
    except (OSError, ValueError, json.JSONDecodeError, mineru_cpu_first.CpuFirstContractError) as error:
        raise ViewRecoveryError(f"origin succeeded view is invalid: {error}") from error
    if origin_receipt["state"] != "succeeded":
        raise ViewRecoveryError("only a succeeded view can be imported")
    _, origin_input = mineru_cpu_first.view_input_identity(origin_run, descriptor)
    _, fresh_input = mineru_cpu_first.view_input_identity(fresh_run, descriptor)
    if origin_receipt["input"] != origin_input or origin_input != fresh_input:
        raise ViewRecoveryError("view input identity differs")
    origin_artifacts = origin_stage_root / "views" / view_id / "artifacts"
    fresh_view = fresh_stage_root / "views" / view_id
    artifacts = fresh_view / "artifacts"
    _safe_copy_tree(origin_artifacts, artifacts, origin_receipt["output_inventory"])
    origin_evidence = _copy_origin_receipt(origin_receipt_path, fresh_view)
    diagnostics = {
        "mode": "imported_verified_success_view",
        "origin": {
            "run_identity_sha256": origin_run["portable_identity_sha256"],
            "receipt": {"path_hint": f"views/{view_id}/view.json", **file_identity(origin_receipt_path), "receipt_sha256": origin_receipt["receipt_sha256"]},
            "receipt_evidence": {**origin_evidence, "receipt_sha256": origin_receipt["receipt_sha256"]},
            "artifact_inventory_sha256": sha256_bytes(canonical_bytes(origin_receipt["output_inventory"])),
        },
        "wrapper_compatibility": compatibility,
        "source_profile_compatibility": profile_compatibility,
    }
    fresh_receipt = mineru_cpu_first.write_succeeded_view(
        fresh_run, descriptor, fresh_input, artifacts, fresh_view / "view.json", diagnostics,
    )
    try:
        mineru_cpu_first.validate_view_receipt(fresh_run, descriptor, fresh_view / "view.json", fresh_stage_root)
    except (OSError, ValueError, json.JSONDecodeError, mineru_cpu_first.CpuFirstContractError) as error:
        raise ViewRecoveryError(f"fresh imported view is invalid: {error}") from error
    return _seal({
        "schema": SCHEMA,
        "view_id": view_id,
        "state": "imported",
        "fresh_receipt_sha256": fresh_receipt["receipt_sha256"],
        "origin_receipt_sha256": origin_receipt["receipt_sha256"],
        "wrapper_compatibility": compatibility,
        "source_profile_compatibility": profile_compatibility,
    }, "import_sha256")
