from __future__ import annotations

import copy
import json
import os
import re
import shutil
import stat
import tempfile
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath
from typing import Any, Iterable, Mapping, Sequence

from . import mineru_cpu_first, reconstruction
from .identity import (
    assert_existing_path_components_are_not_reparse,
    canonical_bytes,
    deterministic_inventory,
    file_identity,
    implementation_inventory,
    is_reparse_point,
    sha256_bytes,
)
from .manifests import is_sha256, sealed, validate_seal


REGISTRY_SCHEMA = "kb_creator.reconstruction_stage_dependency_registry.v1"
INTAKE_SCHEMA = "kb_creator.stage_replay_intake.v1"
REBASE_SCHEMA = "kb_creator.stage_rebase_receipt.v1"
BRIDGE_SCHEMA = "kb_creator.stage_replay_bridge.v1"
STAGE_SCHEMA = "kb_creator.stage_manifest.v2"
COMMAND_SCHEMA = "kb_creator.replay_command.v1"
VIEW_SCHEMA = "kb_creator.mineru_view_execution.v2"
VIEW_SET_SCHEMA = "kb_creator.mineru_view_set.v2"
COMPARISON_SCHEMA = "kb_creator.mineru_multi_view_comparison.v3"
GEOMETRY_SCHEMA = "kb_creator.mineru_geometry_plan.v2"
VISUAL_SCHEMA = "kb_creator.mineru_visual_merge_bundle.v3"
VISUAL_EXECUTION_SCHEMA = "kb_creator.visual_replay_execution.v1"
TRANSFORM_PREFLIGHT_SCHEMA = "kb_creator.replay_transform_preflight.v1"
QUEUE_SCHEMA = "kb_creator.review_queue.v2"
HYBRID_COMPLETION_SCHEMA = "kb_creator.replay_hybrid_completion.v1"
ARCHIVED_SOURCE_PROVENANCE_SCHEMA = "kb_creator.archived_source_artifact_import.v1"

STAGE_IDS = (
    "01-prepare-inputs",
    "02-mineru-three-view",
    "03-compare-views",
    "04-visual-merge-bundle",
)
STAGE_NAMES = (
    "prepare_inputs",
    "mineru_three_view",
    "compare_views",
    "visual_merge_bundle",
)
STAGE_OUTPUTS = tuple(zip(STAGE_IDS, STAGE_NAMES, strict=True))
THROUGH_ALIASES = {
    "01": 1,
    "01-prepare-inputs": 1,
    "02": 2,
    "02-mineru-three-view": 2,
    "03": 3,
    "03-compare-views": 3,
    "04": 4,
    "04-visual-merge-bundle": 4,
}
REPLAY_IMPLEMENTATION_PATHS = (
    "kb_creator/pipeline/reconstruction_replay.py",
    "kb_creator/pipeline/reconstruction_hybrid_stage04.py",
    "kb_creator/pipeline/reconstruction_asset_inventory.py",
    "kb_creator/pipeline/text_segmentation.py",
    "kb_creator/contracts/reconstruction_stage_dependency_registry.v1.json",
    "kb_creator/contracts/stage_dependency_registry.v1.schema.json",
    "kb_creator/contracts/stage_replay_intake.v1.schema.json",
    "kb_creator/contracts/stage_rebase_receipt.v1.schema.json",
    "kb_creator/contracts/stage_replay_bridge.v1.schema.json",
    "kb_creator/contracts/stage_manifest.v2.schema.json",
    "kb_creator/contracts/replay_command.v1.schema.json",
    "kb_creator/contracts/mineru_view_execution.v2.schema.json",
    "kb_creator/contracts/mineru_view_set.v2.schema.json",
    "kb_creator/contracts/mineru_multi_view_comparison.v3.schema.json",
    "kb_creator/contracts/mineru_geometry_plan.v2.schema.json",
    "kb_creator/contracts/mineru_visual_merge_bundle.v3.schema.json",
    "kb_creator/contracts/visual_replay_execution.v1.schema.json",
    "kb_creator/contracts/replay_transform_preflight.v1.schema.json",
    "kb_creator/contracts/replay_hybrid_completion.v1.schema.json",
    "kb_creator/contracts/review_queue.v2.schema.json",
)
RUN07_BOUND_WRAPPER_FIXTURE = (
    "outputs/01-prepare-inputs/command.json",
    "outputs/02-mineru-three-view/view-set.json",
    "outputs/02-mineru-three-view/views/original_hybrid_high/view.json",
    "outputs/02-mineru-three-view/views/original_pipeline_ocr/view.json",
    "outputs/02-mineru-three-view/views/original_pipeline_txt/view.json",
    "outputs/02-mineru-three-view/views/original_vlm/view.json",
    "outputs/02-mineru-three-view/views/raster_pipeline_ocr/view.json",
    "outputs/03-compare-views/command.json",
    "outputs/03-compare-views/comparison.json",
    "outputs/04-visual-merge-bundle/command.json",
    "outputs/04-visual-merge-bundle/evidence/execution.json",
    "outputs/04-visual-merge-bundle/visual/geometry_plan.json",
    "outputs/04-visual-merge-bundle/visual/visual_manifest.json",
)

_DRIVE = re.compile(r"^[A-Za-z]:[\\/]")
_UNC = re.compile(r"^(?:\\\\|//)")
_DEVICE = re.compile(r"^(?:\\\\[?.]\\|//[?.]/)")
_RESERVED = {
    "CON", "PRN", "AUX", "NUL", "CLOCK$",
    *(f"COM{i}" for i in range(1, 10)),
    *(f"LPT{i}" for i in range(1, 10)),
}
_WRAPPER_SUFFIXES = {
    "01-prepare-inputs": {"command.json": "command"},
    "03-compare-views": {
        "command.json": "command",
        "comparison.json": "comparison",
    },
    "04-visual-merge-bundle": {
        "command.json": "command",
        "evidence/execution.json": "visual_execution",
        "visual/geometry_plan.json": "geometry",
        "visual/visual_manifest.json": "visual_manifest",
    },
}

JSON_PAYLOAD_ROUTES = (
    ("prepared_manifest", "01-prepare-inputs", r"prepared/sample_pages\.json", "object"),
    ("mineru_content_list", "02-mineru-three-view", r"views/[A-Za-z0-9_.-]+/artifacts/(?:[^/]+/)*[^/]+_content_list\.json", "array"),
    ("mineru_content_list_v2", "02-mineru-three-view", r"views/[A-Za-z0-9_.-]+/artifacts/(?:[^/]+/)*[^/]+_content_list_v2\.json", "array"),
    ("mineru_middle", "02-mineru-three-view", r"views/[A-Za-z0-9_.-]+/artifacts/(?:[^/]+/)*[^/]+_middle\.json", "object"),
    ("mineru_model", "02-mineru-three-view", r"views/[A-Za-z0-9_.-]+/artifacts/(?:[^/]+/)*[^/]+_model\.json", "array"),
    ("merge_index", "04-visual-merge-bundle", r"merge_packets/merge_index\.json", "object"),
    ("merge_packet", "04-visual-merge-bundle", r"merge_packets/pages/page-[0-9]{3}\.json", "object"),
)


class ReplayError(ValueError):
    def __init__(self, reason_code: str, detail: str = "") -> None:
        self.reason_code = reason_code
        self.detail = detail
        super().__init__(reason_code if not detail else f"{reason_code}: {detail}")


@dataclass(frozen=True)
class FreshReplayAuthorities:
    run_root: Path
    stage_02_root: Path | None
    comparison: Path | None
    merge_packets: Path | None
    visual_manifest: Path | None
    geometry_plan: Path | None
    bridge_sha256: str


@dataclass(frozen=True)
class ArchivedReplayArtifacts:
    """Read-only authority for sealed historical Stage 04 artifacts."""
    run_root: Path
    stage04_root: Path
    run_identity_sha256: str
    source_sha256: str
    bridge_sha256: str
    producer_freshness: dict[str, Any]


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as error:
        raise ReplayError("invalid_json", str(path)) from error
    if not isinstance(value, dict):
        raise ReplayError("invalid_json_shape", str(path))
    return value


def _write_json_new(path: Path, value: Mapping[str, Any]) -> None:
    raw = json.dumps(value, ensure_ascii=False, indent=2).encode("utf-8") + b"\n"
    _write_new(path, raw)


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _seal(schema: str, value: Mapping[str, Any], key: str) -> dict[str, Any]:
    return sealed(schema, dict(value), digest_key=key)


def _require_keys(value: Mapping[str, Any], expected: set[str], label: str) -> None:
    if set(value) != expected:
        raise ReplayError("shape_mismatch", label)


def _validate_relative(value: str, *, allow_empty: bool = False) -> PurePosixPath:
    if not isinstance(value, str) or (not value and not allow_empty):
        raise ReplayError("unsafe_relative_path", repr(value))
    if "\\" in value or ":" in value or _DRIVE.match(value) or _UNC.match(value) or _DEVICE.match(value):
        raise ReplayError("unsafe_relative_path", value)
    path = PurePosixPath(value)
    if path.is_absolute() or any(part in {"", ".", ".."} for part in path.parts):
        raise ReplayError("unsafe_relative_path", value)
    for part in path.parts:
        if part[-1:] in {" ", "."} or part.split(".", 1)[0].upper() in _RESERVED:
            raise ReplayError("unsafe_windows_alias", value)
    return path


def _trusted_origin_path(root: Path, relative: str) -> str:
    """Build an expected origin string without interpreting the origin value."""
    parts = _validate_relative(relative).parts
    return str(root.joinpath(*parts))


def _assert_tree_safe(root: Path) -> None:
    assert_existing_path_components_are_not_reparse(root)
    seen: set[str] = set()
    for path in sorted(root.rglob("*")):
        if is_reparse_point(path) or path.is_symlink():
            raise ReplayError("reparse_point", str(path))
        relative = path.relative_to(root).as_posix()
        _validate_relative(relative)
        folded = relative.casefold()
        if folded in seen:
            raise ReplayError("windows_case_collision", relative)
        seen.add(folded)
        if path.is_file():
            info = path.stat()
            if getattr(info, "st_nlink", 1) != 1:
                raise ReplayError("hardlink_source", relative)


def _assert_roots(source: Path, destination: Path) -> None:
    source = source.resolve()
    destination = destination.absolute()
    if destination.exists():
        raise ReplayError("destination_exists", str(destination))
    if not destination.parent.is_dir():
        raise ReplayError("destination_parent_missing", str(destination.parent))
    assert_existing_path_components_are_not_reparse(destination.parent)
    assert_existing_path_components_are_not_reparse(source)
    if source == destination or source in destination.parents or destination in source.parents:
        raise ReplayError("nested_or_self_replay")


def _write_new(path: Path, raw: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if is_reparse_point(path.parent):
        raise ReplayError("reparse_point", str(path.parent))
    try:
        with path.open("xb") as stream:
            stream.write(raw)
            stream.flush()
            os.fsync(stream.fileno())
    except FileExistsError as error:
        raise ReplayError("destination_collision", str(path)) from error
    if path.read_bytes() != raw:
        raise ReplayError("copy_reopen_mismatch", str(path))


def _copy_physical(source: Path, destination: Path) -> dict[str, Any]:
    if source.is_symlink() or is_reparse_point(source) or not source.is_file():
        raise ReplayError("unsafe_source_file", str(source))
    if getattr(source.stat(), "st_nlink", 1) != 1:
        raise ReplayError("hardlink_source", str(source))
    with source.open("rb") as inp:
        raw = inp.read()
    _write_new(destination, raw)
    try:
        if os.path.samefile(source, destination):
            raise ReplayError("copy_not_physically_distinct", str(destination))
    except OSError as error:
        raise ReplayError("copy_identity_unavailable", str(destination)) from error
    return file_identity(destination)


def _cleanup_owned(staging: Path, operation_id: str, final_root: Path) -> None:
    marker = staging / ".replay-owner.json"
    if not marker.is_file():
        raise ReplayError("staging_owner_marker_missing")
    value = _json(marker)
    if value != {"operation_id": operation_id, "final_root": str(final_root.absolute())}:
        raise ReplayError("staging_owner_marker_mismatch")
    shutil.rmtree(staging)


def load_registry() -> dict[str, Any]:
    path = _repo_root() / "kb_creator" / "contracts" / "reconstruction_stage_dependency_registry.v1.json"
    value = _json(path)
    _require_keys(value, {"schema", "registry_version", "supported_run_schemas", "supported_source_stage_schemas", "fixed_graph", "stages", "closed_selectors", "registry_sha256"}, "registry")
    if value["schema"] != REGISTRY_SCHEMA or value["registry_version"] != 1 or value["fixed_graph"] != list(STAGE_IDS):
        raise ReplayError("registry_version_mismatch")
    try:
        validate_seal(value, "registry_sha256")
    except ValueError as error:
        raise ReplayError("registry_seal_mismatch") from error
    stages = value.get("stages")
    if not isinstance(stages, list) or [row.get("stage_id") for row in stages] != list(STAGE_IDS):
        raise ReplayError("registry_graph_mismatch")
    for ordinal, row in enumerate(stages):
        expected_keys = {"stage_id", "stage_name", "direct_upstream", "run_field_selectors", "implementation_paths", "tool_selectors", "provider_selectors", "output_validator", "argv_recipe"}
        if not isinstance(row, dict):
            raise ReplayError("registry_stage_shape")
        _require_keys(row, expected_keys, "registry stage")
        if row["stage_name"] != STAGE_NAMES[ordinal] or row["direct_upstream"] != list(STAGE_IDS[:ordinal]):
            raise ReplayError("registry_dependency_mismatch", row["stage_id"])
        paths = row["implementation_paths"]
        if not isinstance(paths, list) or len(paths) != len(set(paths)) or any("*" in path or "?" in path for path in paths):
            raise ReplayError("registry_path_domain_mismatch", row["stage_id"])
        for path in paths:
            _validate_relative(path)
    return value


def _through_count(value: str) -> int:
    try:
        return THROUGH_ALIASES[value]
    except KeyError as error:
        raise ReplayError("invalid_replay_prefix", value) from error


def _source_stage_path(run_root: Path, stage_id: str) -> Path:
    return run_root / "stages" / stage_id / "stage.json"


def _source_output_path(run_root: Path, stage_id: str) -> Path:
    return run_root / "outputs" / stage_id


def _current_row(relative: str) -> dict[str, Any]:
    path = _repo_root() / relative
    if not path.is_file() or path.is_symlink() or is_reparse_point(path):
        raise ReplayError("closure_member_missing_or_unsafe", relative)
    return {"path": relative, **file_identity(path)}


def _closure_for(run: Mapping[str, Any], row: Mapping[str, Any], *, archived_source: bool = False) -> dict[str, Any]:
    """Bind a source producer separately from the code transforming its bytes.

    Normal replay deliberately keeps the old equality rule.  An explicitly
    archived import may use stale producer bytes only for saved 01--03
    artifacts; it still records and seals the current transformer closure.
    """
    inventory = run.get("implementation", {}).get("files")
    if not isinstance(inventory, list):
        raise ReplayError("source_implementation_inventory_missing")
    by_path: dict[str, dict[str, Any]] = {}
    for item in inventory:
        if not isinstance(item, dict) or set(item) != {"path", "bytes", "sha256"} or item.get("path") in by_path:
            raise ReplayError("source_implementation_inventory_ambiguous")
        by_path[item["path"]] = item
    source_rows, current_rows = [], []
    for relative in row["implementation_paths"]:
        source = by_path.get(relative)
        if source is None:
            raise ReplayError("legacy_closure_member_missing", relative)
        current = _current_row(relative)
        if source != current and not archived_source:
            raise ReplayError("producer_closure_changed", relative)
        if source != current and archived_source and relative.endswith("reconstruction_stage_dependency_registry.v1.json"):
            raise ReplayError("historical_registry_changed", relative)
        source_rows.append(source)
        current_rows.append(current)
    digest = sha256_bytes(canonical_bytes(source_rows))
    return {
        "source": source_rows,
        "current": current_rows,
        "producer_closure_sha256": digest,
        "current_transformer_closure_sha256": sha256_bytes(canonical_bytes(current_rows)),
    }


def _portable_equivalence(source: Mapping[str, Any], fresh: Mapping[str, Any], selectors: Iterable[str]) -> list[dict[str, Any]]:
    rows = []
    for key in selectors:
        left, right = copy.deepcopy(source.get(key)), copy.deepcopy(fresh.get(key))
        if key in {"contract", "source"}:
            if isinstance(left, dict):
                left.pop("path_hint", None)
            if isinstance(right, dict):
                right.pop("path_hint", None)
        if left != right:
            raise ReplayError("portable_authority_mismatch", key)
        rows.append({"selector": key, "sha256": sha256_bytes(canonical_bytes(left))})
    return rows


def _runtime_matches(source_run: Mapping[str, Any], runtime: reconstruction.RuntimeOptions) -> None:
    try:
        snapshot, _ = mineru_cpu_first.build_runtime_snapshot(runtime)
    except (OSError, KeyError, mineru_cpu_first.CpuFirstContractError) as error:
        raise ReplayError("runtime_snapshot_invalid", str(error)) from error
    expected = {key: source_run[key] for key in ("capability_snapshot", "provider_profiles", "common_tools")}
    if snapshot != expected:
        raise ReplayError("runtime_authority_mismatch")


def _replay_inventory() -> dict[str, Any]:
    paths = [*reconstruction._implementation_paths(), *(_repo_root() / item for item in REPLAY_IMPLEMENTATION_PATHS)]
    return implementation_inventory(_repo_root(), paths)


def _build_fresh_run(contract_path: Path, source_path: Path, run_root: Path, run_id: str, runtime: reconstruction.RuntimeOptions) -> dict[str, Any]:
    run = reconstruction.build_run_spec(contract_path, source_path, run_root, run_id, runtime)
    run["implementation"] = _replay_inventory()
    portable = {key: value for key, value in run.items() if key not in {"local", "portable_identity_sha256"}}
    run["portable_identity_sha256"] = sha256_bytes(canonical_bytes(portable))
    return run


def _verify_replay_source(contract_path: Path, source_path: Path, source_run_root: Path, through_stage: str, runtime: reconstruction.RuntimeOptions, *, fresh_run: Mapping[str, Any] | None = None, archived_source: bool = False) -> dict[str, Any]:
    count = _through_count(through_stage)
    if count not in {3, 4}:
        raise ReplayError("partial_prefix_not_runnable", through_stage)
    source_run_root = source_run_root.resolve()
    _assert_tree_safe(source_run_root)
    try:
        source_run = reconstruction.load_run(source_run_root)
    except (OSError, KeyError, reconstruction.ControlPlaneError) as error:
        raise ReplayError("source_run_invalid", str(error)) from error
    if source_run.get("schema") not in mineru_cpu_first.RUN_SCHEMAS:
        raise ReplayError("unsupported_source_run_schema")
    contract, contract_sha = reconstruction.load_contract(contract_path)
    if source_run["contract"] != {"path_hint": source_run["contract"]["path_hint"], "bytes": len(canonical_bytes(contract)), "sha256": contract_sha, "contract_revision": contract["contract_revision"]}:
        raise ReplayError("contract_identity_mismatch")
    if file_identity(source_path) != {"bytes": source_run["source"]["bytes"], "sha256": source_run["source"]["sha256"]}:
        raise ReplayError("source_identity_mismatch")
    if not archived_source:
        _runtime_matches(source_run, runtime)
    try:
        # The source can retain an unselected Stage04 success/failure.  Validate
        # only the requested contiguous producer prefix; the suffix has no authority.
        observed = {path.name for path in (source_run_root / "stages").iterdir() if path.is_dir()}
        selected = set(STAGE_IDS[:count])
        if not selected <= observed or observed - selected - {STAGE_IDS[3]}:
            raise reconstruction.ControlPlaneError("selected stage prefix is incomplete or ambiguous")
        manifests, upstream = [], []
        for ordinal, name in enumerate(reconstruction.RUN_STAGES[:count], 1):
            _stage, receipt = reconstruction._validate_stage(
                source_run_root, ordinal, name, source_run, upstream,
                reconstruction._base_stage_inputs(name, source_run),
            )
            manifests.append(receipt); upstream.append(receipt)
    except (OSError, KeyError, reconstruction.ControlPlaneError) as error:
        raise ReplayError("source_stage_prefix_invalid", str(error)) from error
    registry = load_registry()
    new_authority = fresh_run or source_run
    selectors = []
    stages = []
    upstream_outputs: list[str] = []
    for ordinal, registry_row in enumerate(registry["stages"][:count]):
        closure = _closure_for(source_run, registry_row, archived_source=archived_source)
        for selector in registry_row["run_field_selectors"]:
            if selector not in selectors:
                selectors.append(selector)
        equivalence = _portable_equivalence(source_run, new_authority, registry_row["run_field_selectors"])
        manifest_path = _source_stage_path(source_run_root, registry_row["stage_id"])
        manifest = _json(manifest_path)
        outputs = manifest["reproducible"]["outputs"]
        stage_key = sha256_bytes(canonical_bytes({
            "stage_id": registry_row["stage_id"],
            "stage_version": 2,
            "argv_recipe": registry_row["argv_recipe"],
            "portable_equivalence": equivalence,
            "producer_closure_sha256": closure["producer_closure_sha256"],
            "current_transformer_closure_sha256": closure["current_transformer_closure_sha256"],
            "tools": {key: source_run.get(key) for key in registry_row["tool_selectors"]},
            "providers": {key: source_run.get(key) for key in registry_row["provider_selectors"]},
            "upstream_output_inventory_sha256": list(upstream_outputs),
            "inputs": manifest["reproducible"]["inputs"],
        }))
        upstream_outputs.append(outputs["inventory_sha256"])
        stages.append({
            "stage_id": registry_row["stage_id"],
            "source_manifest": {"path": f"stages/{registry_row['stage_id']}/stage.json", **file_identity(manifest_path), "reproducible_sha256": manifests[ordinal]["manifest_sha256"]},
            "source_output": copy.deepcopy(outputs),
            "producer_closure": closure,
            "portable_equivalence": equivalence,
            "stage_eligibility_key": stage_key,
        })
    return _seal("kb_creator.replay_eligibility.v1", {
        "state": "eligible",
        "source_mode": "archived_source_artifact_import" if archived_source else "strict_replay",
        "source_run_id": source_run["run_id"],
        "source_run_identity_sha256": source_run["portable_identity_sha256"],
        "source_run_json": {"bytes": (source_run_root / "run.json").stat().st_size, "sha256": file_identity(source_run_root / "run.json")["sha256"]},
        "requested_prefix": list(STAGE_IDS[:count]),
        "registry": {**file_identity(_repo_root() / "kb_creator/contracts/reconstruction_stage_dependency_registry.v1.json"), "registry_sha256": registry["registry_sha256"]},
        "stages": stages,
        "acceptance_inferred": False,
        "decisions_replayed": False,
        "stages_05_06_replayed": False,
    }, "eligibility_sha256")


def verify_replay_source(contract_path: Path, source_path: Path, source_run_root: Path, through_stage: str, runtime: reconstruction.RuntimeOptions, *, fresh_run: Mapping[str, Any] | None = None) -> dict[str, Any]:
    """Strict replay eligibility: historical producers must equal current code."""
    return _verify_replay_source(
        contract_path, source_path, source_run_root, through_stage, runtime,
        fresh_run=fresh_run,
    )


def verify_archived_replay_source(contract_path: Path, source_path: Path, source_run_root: Path, through_stage: str, runtime: reconstruction.RuntimeOptions, *, fresh_run: Mapping[str, Any] | None = None) -> dict[str, Any]:
    """Preflight immutable native 01--03 artifacts for an explicit archived import.

    This never authorizes re-execution of the historical OCR producer.
    """
    if _through_count(through_stage) != 3:
        raise ReplayError("archived_source_requires_through03", through_stage)
    return _verify_replay_source(
        contract_path, source_path, source_run_root, through_stage, runtime,
        fresh_run=fresh_run, archived_source=True,
    )


def _contains_poison(value: Any, source_identity: str) -> bool:
    if isinstance(value, str):
        return source_identity in value or bool(_DRIVE.match(value) or _UNC.match(value) or _DEVICE.match(value))
    if isinstance(value, list):
        return any(_contains_poison(item, source_identity) for item in value)
    if isinstance(value, dict):
        return any(_contains_poison(item, source_identity) for item in value.values())
    return False


def _payload_string_is_poison(value: str, source_identity: str, *, reader_text: bool = False) -> bool:
    text = value.strip()
    if source_identity in value:
        return True
    # Typed MinerU reader text is a literal, never a filesystem target.  It may
    # contain CON, quoted paths, or a broken embedded-font slash.  Actual path
    # fields and unknown metadata still pass through the strict checks below.
    if reader_text:
        return False
    if _DRIVE.match(text) or _UNC.match(text) or _DEVICE.match(text) or text.startswith("/"):
        return True
    parts = [part for part in re.split(r"[\\/]", text) if part]
    if ".." in parts:
        return True
    return any(part.split(".", 1)[0].upper() in _RESERVED for part in parts)


def _payload_contains_poison(value: Any, source_identity: str) -> bool:
    if isinstance(value, str):
        return _payload_string_is_poison(value, source_identity)
    if isinstance(value, list):
        return any(_payload_contains_poison(item, source_identity) for item in value)
    if isinstance(value, dict):
        return any(
            _payload_string_is_poison(str(key), source_identity)
            or (
                _payload_string_is_poison(item, source_identity, reader_text=True)
                if isinstance(item, str) and (
                    key in {"text", "content"} and value.get("type") == "text"
                    or key == "text" and value.get("label") == "ocr_text"
                )
                else _payload_contains_poison(item, source_identity)
            )
            for key, item in value.items()
        )
    return False


def _json_payload_route(stage_id: str, relative: str) -> tuple[str, str]:
    matches = [
        (class_id, shape)
        for class_id, route_stage, pattern, shape in JSON_PAYLOAD_ROUTES
        if stage_id == route_stage and re.fullmatch(pattern, relative)
    ]
    if len(matches) != 1:
        raise ReplayError("unknown_json_payload_route", f"{stage_id}:{relative}")
    return matches[0]


def _read_json_payload(path: Path, stage_id: str, relative: str) -> Any:
    class_id, shape = _json_payload_route(stage_id, relative)
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as error:
        raise ReplayError("invalid_json", relative) from error
    expected = list if shape == "array" else dict
    if not isinstance(value, expected):
        raise ReplayError("invalid_json_payload_shape", f"{class_id}:{relative}")
    return value


def _operational_authority_projection(value: Any) -> Any:
    if isinstance(value, list):
        return [_operational_authority_projection(item) for item in value]
    if not isinstance(value, dict):
        return value
    return {
        key: _operational_authority_projection(item)
        for key, item in value.items()
        if not key.startswith("origin")
    }


def _typed_ref(base: str, path: str, identity: Mapping[str, Any], *, view_id: str | None = None) -> dict[str, Any]:
    _validate_relative(path)
    if base not in {"run_root", "stage_01_root", "stage_02_root", "stage_03_root", "stage_04_root", "view_artifact_root"}:
        raise ReplayError("unknown_reference_base", base)
    result: dict[str, Any] = {"base": base, "path": path, "bytes": identity["bytes"], "sha256": identity["sha256"]}
    if base == "view_artifact_root":
        if not view_id:
            raise ReplayError("view_reference_lacks_scope")
        result["view_id"] = view_id
    elif view_id is not None:
        raise ReplayError("unexpected_view_scope")
    return result


def resolve_reference(run_root: Path, reference: Mapping[str, Any], view_roots: Mapping[str, Path] | None = None) -> Path:
    allowed = {"base", "path", "bytes", "sha256"}
    if reference.get("base") == "view_artifact_root":
        allowed.add("view_id")
    _require_keys(reference, allowed, "typed reference")
    relative = _validate_relative(reference["path"])
    bases = {
        "run_root": run_root,
        "stage_01_root": run_root / "outputs/01-prepare-inputs",
        "stage_02_root": run_root / "outputs/02-mineru-three-view",
        "stage_03_root": run_root / "outputs/03-compare-views",
        "stage_04_root": run_root / "outputs/04-visual-merge-bundle",
    }
    base_name = reference["base"]
    if base_name == "view_artifact_root":
        view_id = reference["view_id"]
        if not isinstance(view_roots, Mapping) or view_id not in view_roots:
            raise ReplayError("unknown_view_artifact_root", str(view_id))
        base = view_roots[view_id]
    else:
        try:
            base = bases[base_name]
        except KeyError as error:
            raise ReplayError("unknown_reference_base", str(base_name)) from error
    candidate = base.joinpath(*relative.parts)
    try:
        candidate.resolve().relative_to(base.resolve())
        assert_existing_path_components_are_not_reparse(candidate)
    except (OSError, ValueError) as error:
        raise ReplayError("reference_escape", str(candidate)) from error
    if not candidate.is_file() or file_identity(candidate) != {"bytes": reference["bytes"], "sha256": reference["sha256"]}:
        raise ReplayError("reference_identity_mismatch", str(candidate))
    return candidate


def _semantic_view(source: Mapping[str, Any]) -> dict[str, Any]:
    keys = ("view_id", "required", "provider_id", "input", "execution_profile", "capability_snapshot", "provider_verification", "profile_identity", "state", "reason_code", "output_inventory", "page_coverage", "exit_code", "blocked_by")
    return {key: copy.deepcopy(source[key]) for key in keys}


def _rebase_view(source: Mapping[str, Any], fresh_identity: str, origin: Mapping[str, Any]) -> dict[str, Any]:
    expected = {"schema", "view_id", "required", "provider_id", "run_identity_sha256", "input", "execution_profile", "capability_snapshot", "provider_verification", "profile_identity", "state", "reason_code", "artifact_root", "output_inventory", "page_coverage", "exit_code", "diagnostics", "blocked_by", "cache_key", "receipt_sha256"}
    _require_keys(source, expected, "view execution v1")
    try:
        validate_seal(dict(source), "receipt_sha256")
    except ValueError as error:
        raise ReplayError("source_view_seal_mismatch") from error
    semantic = _semantic_view(source)
    projection = sha256_bytes(canonical_bytes(semantic))
    artifact_ref = None
    if source["state"] == "succeeded":
        if source["artifact_root"] != f"views/{source['view_id']}/artifacts":
            raise ReplayError("view_artifact_root_mismatch", source["view_id"])
        artifact_ref = {"base": "view_artifact_root", "view_id": source["view_id"], "path": "artifacts"}
    elif source["state"] != "skipped" or source["artifact_root"] is not None:
        raise ReplayError("unsupported_view_state", str(source["state"]))
    body = {
        **semantic,
        "run_identity_sha256": fresh_identity,
        "artifact_root": artifact_ref,
        "execution": {"mode": "replayed", "producer_invoked": False, "origin_execution": dict(origin)},
        "origin": dict(origin),
        "semantic_projection_sha256": projection,
    }
    body["cache_key"] = sha256_bytes(canonical_bytes({"run_identity_sha256": fresh_identity, "semantic_projection_sha256": projection, "artifact_root": artifact_ref}))
    return _seal(VIEW_SCHEMA, body, "receipt_sha256")


def _rebase_view_set(source: Mapping[str, Any], fresh_identity: str, fresh_views: Mapping[str, Mapping[str, Any]], output_root: Path, origin: Mapping[str, Any]) -> dict[str, Any]:
    _require_keys(source, {"schema", "run_identity_sha256", "ordered_view_plan", "required_succeeded", "succeeded_views", "views", "receipt_sha256"}, "view set v1")
    try:
        validate_seal(dict(source), "receipt_sha256")
    except ValueError as error:
        raise ReplayError("source_view_set_seal_mismatch") from error
    rows = []
    for row in source["views"]:
        _require_keys(row, {"view_id", "state", "receipt"}, "view set row")
        view_id = row["view_id"]
        fresh = fresh_views.get(view_id)
        if fresh is None or fresh["state"] != row["state"]:
            raise ReplayError("view_set_membership_mismatch", view_id)
        path = output_root / "views" / view_id / "view.json"
        rows.append({"view_id": view_id, "state": row["state"], "receipt": {"path": f"views/{view_id}/view.json", **file_identity(path), "receipt_sha256": fresh["receipt_sha256"]}})
    semantic = {"ordered_view_plan": source["ordered_view_plan"], "required_succeeded": source["required_succeeded"], "succeeded_views": source["succeeded_views"], "states": [{"view_id": row["view_id"], "state": row["state"]} for row in source["views"]]}
    return _seal(VIEW_SET_SCHEMA, {
        "run_identity_sha256": fresh_identity,
        "ordered_view_plan": copy.deepcopy(source["ordered_view_plan"]),
        "required_succeeded": copy.deepcopy(source["required_succeeded"]),
        "succeeded_views": copy.deepcopy(source["succeeded_views"]),
        "views": rows,
        "origin": dict(origin),
        "semantic_projection_sha256": sha256_bytes(canonical_bytes(semantic)),
    }, "receipt_sha256")


_COMPARISON_ARTIFACT_SUFFIXES = {
    "content_list": "_content_list.json",
    "content_list_v2": "_content_list_v2.json",
    "middle_json": "_middle.json",
    "markdown": ".md",
    "layout_pdf": "_layout.pdf",
    "origin_pdf": "_origin.pdf",
    "span_pdf": "_span.pdf",
}


def _view_artifact_map(view: Mapping[str, Any]) -> dict[str, dict[str, Any]]:
    inventory = view.get("output_inventory")
    if not isinstance(inventory, list):
        raise ReplayError("view_inventory_shape")
    selected: dict[str, dict[str, Any]] = {}
    for role, suffix in _COMPARISON_ARTIFACT_SUFFIXES.items():
        matches = [row for row in inventory if isinstance(row, dict) and set(row) == {"path", "bytes", "sha256"} and str(row["path"]).endswith(suffix)]
        if len(matches) != 1:
            raise ReplayError("comparison_artifact_role_mismatch", f"{view.get('view_id')}:{role}")
        relative = str(matches[0]["path"])
        _validate_relative(relative)
        selected[role] = {"path": relative, "bytes": matches[0]["bytes"], "sha256": matches[0]["sha256"]}
    if len({row["path"] for row in selected.values()}) != len(selected):
        raise ReplayError("comparison_artifact_role_collision", str(view.get("view_id")))
    return selected


def _validate_block(value: Mapping[str, Any], label: str) -> None:
    _require_keys(value, {"raw_index", "page_idx", "source_page", "type", "bbox", "text", "semantic_evidence", "assets"}, label)
    evidence = value["semantic_evidence"]
    if not isinstance(evidence, dict):
        raise ReplayError("shape_mismatch", f"{label} semantic_evidence")
    base_evidence = {"text_level", "v2_title", "middle_title", "markdown_heading", "model_title"}
    # Stage 03 may attach this one closed, positive-only fact when an exact
    # same-page v2 table match supplied the block text. Replay preserves that
    # evidence without opening the record to arbitrary semantic metadata.
    if set(evidence) not in (base_evidence, base_evidence | {"v2_table_text"}):
        raise ReplayError("shape_mismatch", f"{label} semantic_evidence")
    if "v2_table_text" in evidence and evidence["v2_table_text"] is not True:
        raise ReplayError("shape_mismatch", f"{label} semantic_evidence")
    if not isinstance(value["assets"], list) or any(not isinstance(item, str) for item in value["assets"]):
        raise ReplayError("shape_mismatch", f"{label} assets")


def _validate_pairwise(value: Mapping[str, Any]) -> None:
    for pair_id, row in value.items():
        if not isinstance(pair_id, str) or not isinstance(row, dict):
            raise ReplayError("comparison_pairwise_shape")
        _require_keys(row, {"bbox_matches", "left_unmatched", "right_unmatched", "semantic_conflicts"}, "comparison pair")
        for match in row["bbox_matches"]:
            _require_keys(match, {"left_raw_index", "right_raw_index", "bbox_iou"}, "bbox match")
        for side in ("left_unmatched", "right_unmatched"):
            for block in row[side]:
                _validate_block(block, "unmatched block")
        for conflict in row["semantic_conflicts"]:
            if not isinstance(conflict, dict):
                raise ReplayError("shape_mismatch", "semantic conflict")
            if conflict.get("kind") == "title_to_text_downgrade":
                expected = {"kind", "left_raw_index", "right_raw_index", "bbox_iou", "resolution"}
            elif conflict.get("kind") == "image_heading_overlap":
                expected = {"kind", "asset_side", "heading_side", "asset_raw_index", "heading_raw_index", "bbox_iou", "resolution"}
            else:
                raise ReplayError("shape_mismatch", "semantic conflict")
            _require_keys(conflict, expected, "semantic conflict")


def _comparison_projection(value: Mapping[str, Any], artifact_maps: Mapping[str, Mapping[str, Mapping[str, Any]]] | None = None) -> dict[str, Any]:
    views = {}
    for view_id, row in value["views"].items():
        source_artifacts = artifact_maps[view_id] if artifact_maps is not None else row["artifacts"]
        artifacts = {role: {key: item[key] for key in ("bytes", "sha256")} for role, item in source_artifacts.items()}
        views[view_id] = {key: copy.deepcopy(row[key]) for key in ("coverage", "block_counts", "text_lengths", "asset_references", "asset_inventory", "blocks")} | {"artifacts": artifacts}
    skipped = [{"view_id": row["view_id"], "reason_code": row["reason_code"]} for row in value["skipped_views"]]
    return {key: copy.deepcopy(value[key]) for key in ("status", "required_views", "succeeded_views", "pairwise", "failures")} | {"skipped_views": skipped, "views": views}


def _rebase_comparison(
    source: Mapping[str, Any], fresh_identity: str, prepared: Path,
    view_set: Path, stage2: Path, source_stage2: Path,
    origin: Mapping[str, Any], *, artifact_stage2: Path | None = None,
) -> dict[str, Any]:
    _require_keys(source, {"schema", "status", "run_identity_sha256", "manifest", "view_set", "required_views", "succeeded_views", "skipped_views", "views", "pairwise", "failures"}, "comparison v2")
    if source["schema"] != "kb_creator.mineru_multi_view_comparison.v2":
        raise ReplayError("comparison_schema_downgrade")
    if not isinstance(source["views"], dict) or set(source["views"]) != set(source["succeeded_views"]):
        raise ReplayError("comparison_view_domain_mismatch")
    fresh_view_set = _json(view_set)
    fresh_receipts = {row["view_id"]: _json(stage2 / row["receipt"]["path"]) for row in fresh_view_set["views"]}
    artifact_maps: dict[str, dict[str, dict[str, Any]]] = {}
    views: dict[str, Any] = {}
    for view_id, source_row in source["views"].items():
        if not isinstance(source_row, dict):
            raise ReplayError("comparison_view_shape", view_id)
        _require_keys(source_row, {"root", "artifacts", "coverage", "block_counts", "text_lengths", "asset_references", "asset_inventory", "blocks"}, "comparison view")
        fresh_view = fresh_receipts.get(view_id)
        if fresh_view is None or fresh_view.get("state") != "succeeded":
            raise ReplayError("comparison_view_receipt_missing", view_id)
        artifact_map = _view_artifact_map(fresh_view)
        artifact_maps[view_id] = artifact_map
        expected_old_root = _trusted_origin_path(
            source_stage2, f"views/{view_id}/artifacts"
        )
        if source_row["root"] != expected_old_root:
            raise ReplayError("origin_comparison_root_mismatch", view_id)
        if not isinstance(source_row["artifacts"], dict) or set(source_row["artifacts"]) != set(_COMPARISON_ARTIFACT_SUFFIXES):
            raise ReplayError("comparison_artifact_domain_mismatch", view_id)
        artifacts: dict[str, Any] = {}
        for role, identity in artifact_map.items():
            expected_old_path = _trusted_origin_path(
                source_stage2, f"views/{view_id}/artifacts/{identity['path']}"
            )
            if source_row["artifacts"][role] != expected_old_path:
                raise ReplayError("origin_comparison_path_mismatch", f"{view_id}:{role}")
            payload_root = artifact_stage2 or stage2
            fresh_path = payload_root.joinpath(
                "views", view_id, "artifacts", *_validate_relative(identity["path"]).parts
            )
            if file_identity(fresh_path) != {"bytes": identity["bytes"], "sha256": identity["sha256"]}:
                raise ReplayError("comparison_artifact_identity_mismatch", f"{view_id}:{role}")
            artifacts[role] = _typed_ref("view_artifact_root", identity["path"], identity, view_id=view_id)
        for block in source_row["blocks"]:
            _validate_block(block, "comparison block")
        views[view_id] = {key: copy.deepcopy(source_row[key]) for key in ("coverage", "block_counts", "text_lengths", "asset_references", "asset_inventory", "blocks")} | {
            "root": {"base": "view_artifact_root", "view_id": view_id, "path": "artifacts"},
            "artifacts": artifacts,
        }
    _validate_pairwise(source["pairwise"])
    skipped = []
    for row in source["skipped_views"]:
        _require_keys(row, {"view_id", "reason_code", "receipt"}, "skipped comparison view")
        view_id = row["view_id"]
        fresh = fresh_receipts.get(view_id)
        if fresh is None or fresh.get("state") != "skipped" or fresh.get("reason_code") != row["reason_code"]:
            raise ReplayError("comparison_skipped_view_mismatch", view_id)
        receipt_path = stage2 / "views" / view_id / "view.json"
        expected_source_receipt = source_stage2 / "views" / view_id / "view.json"
        if row["receipt"] != {"path": f"views/{view_id}/view.json", **file_identity(expected_source_receipt), "receipt_sha256": _json(expected_source_receipt)["receipt_sha256"]}:
            raise ReplayError("origin_skipped_receipt_mismatch", view_id)
        skipped.append({"view_id": view_id, "reason_code": row["reason_code"], "receipt": {**_typed_ref("stage_02_root", f"views/{view_id}/view.json", file_identity(receipt_path)), "receipt_sha256": fresh["receipt_sha256"]}})
    projection_source = _comparison_projection(source, artifact_maps)
    body = {
        "status": source["status"],
        "run_identity_sha256": fresh_identity,
        "manifest": _typed_ref("stage_01_root", "prepared/sample_pages.json", file_identity(prepared)),
        "view_set": {**_typed_ref("stage_02_root", "view-set.json", file_identity(view_set)), "receipt_sha256": _json(view_set)["receipt_sha256"]},
        "required_views": copy.deepcopy(source["required_views"]),
        "succeeded_views": copy.deepcopy(source["succeeded_views"]),
        "skipped_views": skipped,
        "views": views,
        "pairwise": copy.deepcopy(source["pairwise"]),
        "failures": copy.deepcopy(source["failures"]),
        "origin": dict(origin),
        "semantic_projection_sha256": sha256_bytes(canonical_bytes(projection_source)),
    }
    fresh = _seal(COMPARISON_SCHEMA, body, "comparison_sha256")
    if _comparison_projection(fresh) != projection_source:
        raise ReplayError("comparison_projection_mismatch")
    _validate_comparison_v3(fresh)
    return fresh


def _portable_projection(value: Any, source_identity: str) -> Any:
    if isinstance(value, list):
        return [_portable_projection(item, source_identity) for item in value]
    if not isinstance(value, dict):
        if isinstance(value, str) and (_DRIVE.match(value) or _UNC.match(value) or _DEVICE.match(value) or source_identity in value):
            return {"opaque_authority_string_sha256": sha256_bytes(value.encode("utf-8"))}
        return copy.deepcopy(value)
    result = {}
    for key, item in value.items():
        if key in {"schema", "run_identity_sha256", "plan_sha256", "manifest_sha256"}:
            continue
        result[key] = _portable_projection(item, source_identity)
    return result


def _validate_comparison_v3(value: Mapping[str, Any]) -> None:
    _require_keys(value, {"schema", "status", "run_identity_sha256", "manifest", "view_set", "required_views", "succeeded_views", "skipped_views", "views", "pairwise", "failures", "origin", "semantic_projection_sha256", "comparison_sha256"}, "comparison v3")
    if value["schema"] != COMPARISON_SCHEMA or value["status"] != "pass_for_review" or value["failures"] != []:
        raise ReplayError("comparison_v3_contract_mismatch")
    _require_keys(value["view_set"], {"base", "path", "bytes", "sha256", "receipt_sha256"}, "comparison view set ref")
    for row in value["skipped_views"]:
        _require_keys(row, {"view_id", "reason_code", "receipt"}, "comparison skipped view")
        _require_keys(row["receipt"], {"base", "path", "bytes", "sha256", "receipt_sha256"}, "comparison skipped receipt")
    if set(value["views"]) != set(value["succeeded_views"]):
        raise ReplayError("comparison_view_domain_mismatch")
    for view_id, row in value["views"].items():
        _require_keys(row, {"root", "artifacts", "coverage", "block_counts", "text_lengths", "asset_references", "asset_inventory", "blocks"}, "comparison view")
        if row["root"] != {"base": "view_artifact_root", "view_id": view_id, "path": "artifacts"}:
            raise ReplayError("comparison_view_root_mismatch", view_id)
        if set(row["artifacts"]) != set(_COMPARISON_ARTIFACT_SUFFIXES):
            raise ReplayError("comparison_artifact_domain_mismatch", view_id)
        for ref in row["artifacts"].values():
            _require_keys(ref, {"base", "view_id", "path", "bytes", "sha256"}, "comparison artifact ref")
            if ref["base"] != "view_artifact_root" or ref["view_id"] != view_id:
                raise ReplayError("comparison_artifact_scope_mismatch", view_id)
        for block in row["blocks"]:
            _validate_block(block, "comparison block")
    _validate_pairwise(value["pairwise"])
    try:
        validate_seal(dict(value), "comparison_sha256")
    except ValueError as error:
        raise ReplayError("comparison_v3_seal_mismatch") from error
    if sha256_bytes(canonical_bytes(_comparison_projection(value))) != value["semantic_projection_sha256"]:
        raise ReplayError("comparison_projection_mismatch")


def _identity_only(value: Mapping[str, Any]) -> dict[str, Any]:
    return {"bytes": value["bytes"], "sha256": value["sha256"]}


def _geometry_projection(value: Mapping[str, Any]) -> dict[str, Any]:
    layouts = []
    for row in value["layouts"]:
        layouts.append({
            "view_id": row["view_id"],
            "input_kind": row["input_kind"],
            "page_count": row["page_count"],
            "layout": _identity_only(row["layout"]),
        })
    renderer = copy.deepcopy(value["renderer"])
    renderer.pop("path_hint", None)
    return {
        "policy": copy.deepcopy(value["policy"]),
        "source": _identity_only(value["source"]),
        "review_dpi": value["review_dpi"],
        "rounding_rule": value["rounding_rule"],
        "tolerances": copy.deepcopy(value["tolerances"]),
        "renderer": renderer,
        "succeeded_views": copy.deepcopy(value["succeeded_views"]),
        "layouts": layouts,
        "observed_geometry": copy.deepcopy(value["observed_geometry"]),
        "targets": copy.deepcopy(value["targets"]),
        "transforms": copy.deepcopy(value["transforms"]),
        "rendered_pages": copy.deepcopy(value["rendered_pages"]),
    }


def _rebase_geometry(
    source: Mapping[str, Any], fresh_identity: str, fresh_run: Mapping[str, Any],
    prepared: Path, comparison: Path, view_set: Path, stage2: Path,
    source_stage1: Path, source_stage2: Path, source_stage3: Path,
    destination: Path, origin: Mapping[str, Any],
    *, artifact_stage2: Path | None = None, rendered_stage4: Path | None = None,
) -> dict[str, Any]:
    expected = {"schema", "policy", "run_identity_sha256", "preparation_manifest", "source", "comparison", "view_set", "review_dpi", "rounding_rule", "tolerances", "renderer", "succeeded_views", "layouts", "observed_geometry", "targets", "transforms", "rendered_pages", "plan_sha256"}
    _require_keys(source, expected, "geometry v1")
    if source["schema"] != "kb_creator.mineru_geometry_plan.v1":
        raise ReplayError("geometry_schema_downgrade")
    try:
        validate_seal(dict(source), "plan_sha256")
    except ValueError as error:
        raise ReplayError("source_geometry_seal_mismatch") from error
    source_prepared = source_stage1 / "prepared/sample_pages.json"
    source_comparison = source_stage3 / "comparison.json"
    source_view_set = source_stage2 / "view-set.json"
    if source["preparation_manifest"] != {"path_hint": "outputs/01-prepare-inputs/prepared/sample_pages.json", **file_identity(source_prepared)}:
        raise ReplayError("origin_geometry_preparation_mismatch")
    if source["comparison"] != {"path_hint": "outputs/03-compare-views/comparison.json", **file_identity(source_comparison)}:
        raise ReplayError("origin_geometry_comparison_mismatch")
    source_vs = _json(source_view_set)
    if source["view_set"] != {"path_hint": "outputs/02-mineru-three-view/view-set.json", **file_identity(source_view_set), "receipt_sha256": source_vs["receipt_sha256"]}:
        raise ReplayError("origin_geometry_view_set_mismatch")
    fresh_vs = _json(view_set)
    fresh_comparison = _json(comparison)
    fresh_views = {row["view_id"]: _json(stage2 / row["receipt"]["path"]) for row in fresh_vs["views"]}
    layouts = []
    for row in source["layouts"]:
        _require_keys(row, {"view_id", "input_kind", "page_count", "layout"}, "geometry layout")
        view_id = row["view_id"]
        artifacts = _view_artifact_map(fresh_views.get(view_id, {}))
        layout = artifacts["layout_pdf"]
        layout_root = artifact_stage2 or stage2
        layout_path = layout_root.joinpath(
            "views", view_id, "artifacts", *_validate_relative(layout["path"]).parts
        )
        if file_identity(layout_path) != {
            "bytes": layout["bytes"], "sha256": layout["sha256"]
        }:
            raise ReplayError("geometry_layout_identity_mismatch", view_id)
        expected_hint = (
            f"views/{view_id}/artifacts/"
            f"{_validate_relative(layout['path']).name}"
        )
        if row["layout"] != {"path_hint": expected_hint, "bytes": layout["bytes"], "sha256": layout["sha256"]}:
            raise ReplayError("origin_geometry_layout_mismatch", view_id)
        layouts.append({"view_id": view_id, "input_kind": row["input_kind"], "page_count": row["page_count"], "layout": _typed_ref("view_artifact_root", layout["path"], layout, view_id=view_id)})
    rendered = copy.deepcopy(source["rendered_pages"])
    for row in rendered:
        _require_keys(row, {"view_id", "source_page", "path", "dimensions", "mode", "bytes", "sha256"}, "geometry rendered page")
        _validate_relative(row["path"])
        render_root = rendered_stage4 or destination
        path = render_root.joinpath(*_validate_relative(row["path"]).parts)
        if file_identity(path) != {"bytes": row["bytes"], "sha256": row["sha256"]}:
            raise ReplayError("geometry_rendered_page_mismatch", row["path"])
    renderer = copy.deepcopy(source["renderer"])
    _require_keys(renderer, {"path_hint", "bytes", "sha256", "version", "argv_recipe"}, "geometry renderer")
    renderer.pop("path_hint")
    body = {
        "policy": source["policy"], "run_identity_sha256": fresh_identity,
        "preparation_manifest": _typed_ref("stage_01_root", "prepared/sample_pages.json", file_identity(prepared)),
        "source": {"path_hint": Path(str(fresh_run["source"]["path_hint"])).name, "bytes": source["source"]["bytes"], "sha256": source["source"]["sha256"]},
        "comparison": {**_typed_ref("stage_03_root", "comparison.json", file_identity(comparison)), "comparison_sha256": fresh_comparison["comparison_sha256"]},
        "view_set": {**_typed_ref("stage_02_root", "view-set.json", file_identity(view_set)), "receipt_sha256": fresh_vs["receipt_sha256"]},
        "review_dpi": source["review_dpi"], "rounding_rule": source["rounding_rule"], "tolerances": copy.deepcopy(source["tolerances"]),
        "renderer": renderer, "succeeded_views": copy.deepcopy(source["succeeded_views"]), "layouts": layouts,
        "observed_geometry": copy.deepcopy(source["observed_geometry"]), "targets": copy.deepcopy(source["targets"]),
        "transforms": copy.deepcopy(source["transforms"]), "rendered_pages": rendered,
        "origin": dict(origin), "execution": {"mode": "replayed", "producer_invoked": False},
    }
    source_projection = _geometry_projection(source)
    body["semantic_projection_sha256"] = sha256_bytes(canonical_bytes(source_projection))
    fresh = _seal(GEOMETRY_SCHEMA, body, "plan_sha256")
    if _geometry_projection(fresh) != source_projection:
        raise ReplayError("geometry_projection_mismatch")
    _validate_geometry_v2(fresh)
    return fresh


def _validate_geometry_v2(value: Mapping[str, Any]) -> None:
    expected = {"schema", "policy", "run_identity_sha256", "preparation_manifest", "source", "comparison", "view_set", "review_dpi", "rounding_rule", "tolerances", "renderer", "succeeded_views", "layouts", "observed_geometry", "targets", "transforms", "rendered_pages", "origin", "execution", "semantic_projection_sha256", "plan_sha256"}
    _require_keys(value, expected, "geometry v2")
    if value["schema"] != GEOMETRY_SCHEMA:
        raise ReplayError("geometry_v2_schema_mismatch")
    _require_keys(value["preparation_manifest"], {"base", "path", "bytes", "sha256"}, "geometry preparation ref")
    _require_keys(value["comparison"], {"base", "path", "bytes", "sha256", "comparison_sha256"}, "geometry comparison ref")
    _require_keys(value["view_set"], {"base", "path", "bytes", "sha256", "receipt_sha256"}, "geometry view set ref")
    _require_keys(value["source"], {"path_hint", "bytes", "sha256"}, "geometry source identity")
    _require_keys(value["renderer"], {"bytes", "sha256", "version", "argv_recipe"}, "geometry renderer")
    for row in value["layouts"]:
        _require_keys(row, {"view_id", "input_kind", "page_count", "layout"}, "geometry layout")
        _require_keys(row["layout"], {"base", "view_id", "path", "bytes", "sha256"}, "geometry layout ref")
        if row["layout"]["view_id"] != row["view_id"]:
            raise ReplayError("geometry_layout_scope_mismatch")
    for row in value["rendered_pages"]:
        _require_keys(row, {"view_id", "source_page", "path", "dimensions", "mode", "bytes", "sha256"}, "geometry rendered page")
        _validate_relative(row["path"])
    _require_keys(value["execution"], {"mode", "producer_invoked"}, "geometry execution")
    if value["execution"] != {"mode": "replayed", "producer_invoked": False}:
        raise ReplayError("geometry_execution_mismatch")
    try:
        validate_seal(dict(value), "plan_sha256")
    except ValueError as error:
        raise ReplayError("geometry_v2_seal_mismatch") from error
    if sha256_bytes(canonical_bytes(_geometry_projection(value))) != value["semantic_projection_sha256"]:
        raise ReplayError("geometry_projection_mismatch")


def _visual_projection(
    value: Mapping[str, Any], *, canonical_contract_sha256: str | None = None,
) -> dict[str, Any]:
    return {
        "source_sha256": value["inputs"]["source"]["sha256"],
        "contract_sha256": canonical_contract_sha256 or value["inputs"]["reconstruction_contract"]["sha256"],
        "dpi": value["inputs"]["dpi"],
        "layouts": {key: {"sha256": row["sha256"]} for key, row in value["layouts"].items()},
        "counts": copy.deepcopy(value["counts"]), "inventory_scope": value["inventory_scope"],
        "inventory_exclusions": copy.deepcopy(value["inventory_exclusions"]),
        "files": [{"path": row["path"], "bytes": row["bytes"], "sha256": row["sha256"]} for row in value["files"] if row["path"] != "visual/geometry_plan.json"],
    }


def _rebase_visual_execution(source: Mapping[str, Any], fresh_identity: str, destination: Path, origin: Mapping[str, Any], renderer: Mapping[str, Any]) -> dict[str, Any]:
    _require_keys(source, {"commands", "pdftoppm_version", "output_inventory"}, "visual execution v1")
    copied = []
    for row in source["output_inventory"]:
        keys = set(row) if isinstance(row, dict) else set()
        if keys not in ({"path", "bytes", "sha256"}, {"path", "bytes", "sha256", "dimensions"}):
            raise ReplayError("shape_mismatch", "visual execution inventory")
        if "dimensions" in row and (
            not isinstance(row["dimensions"], list)
            or len(row["dimensions"]) != 2
            or any(not isinstance(item, int) or item < 1 for item in row["dimensions"])
        ):
            raise ReplayError("shape_mismatch", "visual execution dimensions")
        _validate_relative(row["path"])
        if not row["path"].lower().endswith(".png"):
            continue
        target = destination / row["path"]
        if file_identity(target) != {"bytes": row["bytes"], "sha256": row["sha256"]}:
            raise ReplayError("visual_render_inventory_mismatch", row["path"])
        copied.append({key: row[key] for key in ("path", "bytes", "sha256")})
    projection = {"renderer": copy.deepcopy(renderer), "copied_render_inventory": copied}
    return _seal(VISUAL_EXECUTION_SCHEMA, {
        "run_identity_sha256": fresh_identity, "origin": dict(origin),
        "renderer": copy.deepcopy(renderer), "copied_render_inventory": copied,
        "execution": {"mode": "replayed", "producer_invoked": False},
        "semantic_projection_sha256": sha256_bytes(canonical_bytes(projection)),
    }, "execution_sha256")


def _rebase_visual(
    source: Mapping[str, Any], fresh_identity: str,
    fresh_run: Mapping[str, Any], prepared: Path, comparison: Path,
    view_set: Path, geometry: Path, stage2: Path, source_stage1: Path,
    source_stage2: Path, source_stage3: Path, destination: Path,
    origin: Mapping[str, Any], *, artifact_stage2: Path | None = None,
    payload_stage4: Path | None = None, source_stage4: Path | None = None,
) -> dict[str, Any]:
    _require_keys(source, {"schema", "inputs", "layouts", "execution", "counts", "inventory_scope", "inventory_exclusions", "files", "geometry_plan", "manifest_sha256"}, "visual manifest v2")
    if source["schema"] != "kb_creator.mineru_visual_merge_bundle.v2":
        raise ReplayError("visual_schema_downgrade")
    try:
        validate_seal(dict(source), "manifest_sha256")
    except ValueError as error:
        raise ReplayError("source_visual_seal_mismatch") from error
    inputs = source["inputs"]
    _require_keys(inputs, {"raw_receipt", "source", "comparison", "raw_root", "dpi", "preparation_manifest", "reconstruction_contract"}, "visual inputs")
    expected_paths = {
        "raw_receipt": _trusted_origin_path(source_stage2, "view-set.json"),
        "comparison": _trusted_origin_path(source_stage3, "comparison.json"),
        "preparation_manifest": _trusted_origin_path(
            source_stage1, "prepared/sample_pages.json"
        ),
    }
    for key, expected in expected_paths.items():
        if inputs[key]["path"] != expected:
            raise ReplayError("origin_visual_path_mismatch", key)
    if inputs["raw_root"] != str(source_stage2):
        raise ReplayError("origin_visual_path_mismatch", "raw_root")
    if inputs["source"].get("sha256") != fresh_run["source"]["sha256"]:
        raise ReplayError("origin_visual_source_mismatch")
    contract_path = Path(str(fresh_run.get("local", {}).get("contract_path", ""))).resolve()
    if not contract_path.is_file() or inputs["reconstruction_contract"].get("sha256") != file_identity(contract_path)["sha256"]:
        raise ReplayError("origin_visual_contract_mismatch")
    old_stage4 = source_stage4 or payload_stage4
    if old_stage4 is None:
        raise ReplayError("origin_visual_stage4_missing")
    source_execution = _json(old_stage4 / "evidence/execution.json")
    if source["execution"] != {
        "commands": source_execution["commands"],
        "pdftoppm_version": source_execution["pdftoppm_version"],
    } or source["files"] != source_execution["output_inventory"]:
        raise ReplayError("origin_visual_execution_mismatch")
    source_geometry_path = old_stage4 / "visual/geometry_plan.json"
    source_geometry = _json(source_geometry_path)
    if source["geometry_plan"] != {
        "path": "visual/geometry_plan.json", **file_identity(source_geometry_path),
        "plan_sha256": source_geometry["plan_sha256"],
    }:
        raise ReplayError("origin_visual_geometry_mismatch")
    fresh_vs, fresh_cmp, fresh_geometry = _json(view_set), _json(comparison), _json(geometry)
    fresh_views = {row["view_id"]: _json(stage2 / row["receipt"]["path"]) for row in fresh_vs["views"]}
    layouts = {}
    for view_id, old in source["layouts"].items():
        _require_keys(old, {"path", "sha256"}, "visual layout")
        artifact = _view_artifact_map(fresh_views.get(view_id, {}))["layout_pdf"]
        expected = _trusted_origin_path(
            source_stage2, f"views/{view_id}/artifacts/{artifact['path']}"
        )
        if old != {"path": expected, "sha256": artifact["sha256"]}:
            raise ReplayError("origin_visual_layout_mismatch", view_id)
        artifact_root = artifact_stage2 or stage2
        layout_path = artifact_root.joinpath(
            "views", view_id, "artifacts", *_validate_relative(artifact["path"]).parts
        )
        if file_identity(layout_path) != {
            "bytes": artifact["bytes"], "sha256": artifact["sha256"]
        }:
            raise ReplayError("visual_layout_identity_mismatch", view_id)
        layouts[view_id] = _typed_ref("view_artifact_root", artifact["path"], artifact, view_id=view_id)
    files = []
    for row in source["files"]:
        keys = set(row) if isinstance(row, dict) else set()
        if keys not in ({"path", "bytes", "sha256"}, {"path", "bytes", "sha256", "dimensions"}):
            raise ReplayError("shape_mismatch", "visual file")
        if "dimensions" in row and (
            not isinstance(row["dimensions"], list)
            or len(row["dimensions"]) != 2
            or any(not isinstance(item, int) or item < 1 for item in row["dimensions"])
        ):
            raise ReplayError("shape_mismatch", "visual file dimensions")
        _validate_relative(row["path"])
        payload_root = payload_stage4 or destination
        target = payload_root.joinpath(*_validate_relative(row["path"]).parts)
        identity = file_identity(geometry) if row["path"] == "visual/geometry_plan.json" else file_identity(target)
        if row["path"] != "visual/geometry_plan.json" and identity != {"bytes": row["bytes"], "sha256": row["sha256"]}:
            raise ReplayError("visual_payload_identity_mismatch", row["path"])
        files.append({"path": row["path"], **identity})
    body = {
        "run_identity_sha256": fresh_identity,
        "inputs": {
            "view_set": {**_typed_ref("stage_02_root", "view-set.json", file_identity(view_set)), "receipt_sha256": fresh_vs["receipt_sha256"]},
            "source": {"path_hint": Path(str(fresh_run["source"]["path_hint"])).name, "bytes": fresh_run["source"]["bytes"], "sha256": fresh_run["source"]["sha256"]},
            "comparison": {**_typed_ref("stage_03_root", "comparison.json", file_identity(comparison)), "comparison_sha256": fresh_cmp["comparison_sha256"]},
            "stage_02_root": {"base": "stage_02_root"}, "dpi": inputs["dpi"],
            "preparation_manifest": _typed_ref("stage_01_root", "prepared/sample_pages.json", file_identity(prepared)),
            "reconstruction_contract": {"bytes": fresh_run["contract"]["bytes"], "sha256": fresh_run["contract"]["sha256"], "contract_revision": fresh_run["contract"]["contract_revision"]},
        },
        "layouts": layouts,
        "execution": {"mode": "replayed", "producer_invoked": False, "renderer": copy.deepcopy(fresh_geometry["renderer"])},
        "counts": copy.deepcopy(source["counts"]), "inventory_scope": source["inventory_scope"], "inventory_exclusions": copy.deepcopy(source["inventory_exclusions"]),
        "files": files,
        "geometry_plan": {**_typed_ref("stage_04_root", "visual/geometry_plan.json", file_identity(geometry)), "plan_sha256": fresh_geometry["plan_sha256"]},
        "origin": dict(origin),
    }
    canonical_contract_sha256 = fresh_run["contract"]["sha256"]
    source_projection = _visual_projection(
        source, canonical_contract_sha256=canonical_contract_sha256
    )
    body["semantic_projection_sha256"] = sha256_bytes(canonical_bytes(source_projection))
    fresh = _seal(VISUAL_SCHEMA, body, "manifest_sha256")
    if _visual_projection(
        fresh, canonical_contract_sha256=canonical_contract_sha256
    ) != source_projection:
        raise ReplayError("visual_projection_mismatch")
    _validate_visual_v3(fresh)
    return fresh


def _validate_visual_v3(value: Mapping[str, Any]) -> None:
    _require_keys(value, {"schema", "run_identity_sha256", "inputs", "layouts", "execution", "counts", "inventory_scope", "inventory_exclusions", "files", "geometry_plan", "origin", "semantic_projection_sha256", "manifest_sha256"}, "visual v3")
    if value["schema"] != VISUAL_SCHEMA:
        raise ReplayError("visual_v3_schema_mismatch")
    _require_keys(value["inputs"], {"view_set", "source", "comparison", "stage_02_root", "dpi", "preparation_manifest", "reconstruction_contract"}, "visual v3 inputs")
    _require_keys(value["inputs"]["stage_02_root"], {"base"}, "visual stage2 root")
    if value["inputs"]["stage_02_root"] != {"base": "stage_02_root"}:
        raise ReplayError("visual_stage2_root_mismatch")
    for view_id, ref in value["layouts"].items():
        _require_keys(ref, {"base", "view_id", "path", "bytes", "sha256"}, "visual layout ref")
        if ref["base"] != "view_artifact_root" or ref["view_id"] != view_id:
            raise ReplayError("visual_layout_scope_mismatch", view_id)
    _require_keys(value["execution"], {"mode", "producer_invoked", "renderer"}, "visual execution")
    if value["execution"]["mode"] != "replayed" or value["execution"]["producer_invoked"] is not False:
        raise ReplayError("visual_execution_mismatch")
    for row in value["files"]:
        _require_keys(row, {"path", "bytes", "sha256"}, "visual inventory")
        _validate_relative(row["path"])
    _require_keys(value["geometry_plan"], {"base", "path", "bytes", "sha256", "plan_sha256"}, "visual geometry ref")
    try:
        validate_seal(dict(value), "manifest_sha256")
    except ValueError as error:
        raise ReplayError("visual_v3_seal_mismatch") from error
    if sha256_bytes(canonical_bytes(_visual_projection(value))) != value["semantic_projection_sha256"]:
        raise ReplayError("visual_projection_mismatch")


def _validate_view_v2(value: Mapping[str, Any]) -> None:
    expected = {
        "schema", "view_id", "required", "provider_id", "input",
        "execution_profile", "capability_snapshot", "provider_verification",
        "profile_identity", "state", "reason_code", "output_inventory",
        "page_coverage", "exit_code", "blocked_by", "run_identity_sha256",
        "artifact_root", "execution", "origin", "semantic_projection_sha256",
        "cache_key", "receipt_sha256",
    }
    _require_keys(value, expected, "view execution v2")
    if value["schema"] != VIEW_SCHEMA or value["state"] not in {"succeeded", "skipped"}:
        raise ReplayError("view_v2_contract_mismatch")
    _require_keys(value["execution"], {"mode", "producer_invoked", "origin_execution"}, "view execution")
    if value["execution"]["mode"] != "replayed" or value["execution"]["producer_invoked"] is not False:
        raise ReplayError("view_execution_mismatch")
    if value["state"] == "succeeded":
        if value["artifact_root"] != {"base": "view_artifact_root", "view_id": value["view_id"], "path": "artifacts"}:
            raise ReplayError("view_artifact_root_mismatch", str(value["view_id"]))
    elif value["artifact_root"] is not None:
        raise ReplayError("view_artifact_root_mismatch", str(value["view_id"]))
    try:
        validate_seal(dict(value), "receipt_sha256")
    except ValueError as error:
        raise ReplayError("view_v2_seal_mismatch") from error
    if sha256_bytes(canonical_bytes(_semantic_view(value))) != value["semantic_projection_sha256"]:
        raise ReplayError("view_projection_mismatch")


def _validate_view_set_v2(value: Mapping[str, Any]) -> None:
    _require_keys(value, {
        "schema", "run_identity_sha256", "ordered_view_plan",
        "required_succeeded", "succeeded_views", "views", "origin",
        "semantic_projection_sha256", "receipt_sha256",
    }, "view set v2")
    if value["schema"] != VIEW_SET_SCHEMA or not isinstance(value["views"], list):
        raise ReplayError("view_set_v2_contract_mismatch")
    for row in value["views"]:
        _require_keys(row, {"view_id", "state", "receipt"}, "view set row")
        _require_keys(row["receipt"], {"path", "bytes", "sha256", "receipt_sha256"}, "view set receipt")
        _validate_relative(row["receipt"]["path"])
    try:
        validate_seal(dict(value), "receipt_sha256")
    except ValueError as error:
        raise ReplayError("view_set_v2_seal_mismatch") from error
    semantic = {
        "ordered_view_plan": value["ordered_view_plan"],
        "required_succeeded": value["required_succeeded"],
        "succeeded_views": value["succeeded_views"],
        "states": [
            {"view_id": row["view_id"], "state": row["state"]}
            for row in value["views"]
        ],
    }
    if sha256_bytes(canonical_bytes(semantic)) != value["semantic_projection_sha256"]:
        raise ReplayError("view_set_projection_mismatch")


def _validate_command_v1(value: Mapping[str, Any], stage_id: str) -> None:
    _require_keys(value, {
        "schema", "stage_id", "run_identity_sha256", "producer_invoked",
        "inputs", "output", "origin_command", "transformer", "command_sha256",
    }, "replay command")
    if (
        value["schema"] != COMMAND_SCHEMA or value["stage_id"] != stage_id
        or value["producer_invoked"] is not False or value["inputs"] != []
        or value["output"] != {"base": f"stage_{stage_id[:2]}_root", "path": "command.json"}
        or value["transformer"] != "replay_command_v1"
    ):
        raise ReplayError("replay_command_contract_mismatch", stage_id)
    try:
        validate_seal(dict(value), "command_sha256")
    except ValueError as error:
        raise ReplayError("replay_command_seal_mismatch", stage_id) from error


def _validate_visual_execution_v1(value: Mapping[str, Any]) -> None:
    _require_keys(value, {
        "schema", "run_identity_sha256", "origin", "renderer",
        "copied_render_inventory", "execution", "semantic_projection_sha256",
        "execution_sha256",
    }, "visual replay execution")
    if value["schema"] != VISUAL_EXECUTION_SCHEMA or value["execution"] != {"mode": "replayed", "producer_invoked": False}:
        raise ReplayError("visual_execution_contract_mismatch")
    for row in value["copied_render_inventory"]:
        _require_keys(row, {"path", "bytes", "sha256"}, "visual render inventory")
        _validate_relative(row["path"])
    try:
        validate_seal(dict(value), "execution_sha256")
    except ValueError as error:
        raise ReplayError("visual_execution_seal_mismatch") from error


def _validate_transformed_wrapper(kind: str, stage_id: str, value: Mapping[str, Any]) -> tuple[str, str]:
    validators = {
        "command": (_validate_command_v1, "command_sha256"),
        "view": (_validate_view_v2, "receipt_sha256"),
        "view_set": (_validate_view_set_v2, "receipt_sha256"),
        "comparison": (_validate_comparison_v3, "comparison_sha256"),
        "geometry": (_validate_geometry_v2, "plan_sha256"),
        "visual_manifest": (_validate_visual_v3, "manifest_sha256"),
        "visual_execution": (_validate_visual_execution_v1, "execution_sha256"),
    }
    try:
        validator, seal_key = validators[kind]
    except KeyError as error:
        raise ReplayError("unknown_transformer", kind) from error
    if kind == "command":
        validator(value, stage_id)  # type: ignore[misc]
    else:
        validator(value)  # type: ignore[misc]
    return str(value["schema"]), seal_key


def _replay_command(stage_id: str, fresh_identity: str, origin: Mapping[str, Any]) -> dict[str, Any]:
    return _seal(COMMAND_SCHEMA, {
        "stage_id": stage_id,
        "run_identity_sha256": fresh_identity,
        "producer_invoked": False,
        "inputs": [],
        "output": {"base": f"stage_{stage_id[:2]}_root", "path": "command.json"},
        "origin_command": dict(origin),
        "transformer": "replay_command_v1",
    }, "command_sha256")


def _classify(stage_id: str, relative: str) -> str:
    if stage_id == "02-mineru-three-view":
        if relative == "command.json":
            return "command"
        if relative == "view-set.json":
            return "view_set"
        if re.fullmatch(r"views/[A-Za-z0-9_.-]+/view\.json", relative):
            return "view"
        if re.fullmatch(r"views/[A-Za-z0-9_.-]+/evidence/origin-view\.json", relative):
            return "recovered_view_evidence"
        if re.fullmatch(r"views/[A-Za-z0-9_.-]+/artifacts/.+", relative):
            return "payload"
        raise ReplayError("unregistered_stage_artifact", f"{stage_id}:{relative}")
    wrapper = _WRAPPER_SUFFIXES.get(stage_id, {}).get(relative)
    if wrapper:
        return wrapper
    if stage_id == "01-prepare-inputs" and relative in {"prepared/source_raster.pdf", "prepared/sample_pages.json"}:
        return "payload"
    if stage_id == "03-compare-views" and relative == "comparison.md":
        return "payload"
    if stage_id == "04-visual-merge-bundle" and any(
        re.fullmatch(pattern, relative)
        for pattern in (
            r"merge_packets/merge_index\.(?:json|md)",
            r"merge_packets/pages/page-[0-9]{3}\.(?:json|md)",
            r"visual/contact_sheets/pages-[0-9]{3}-[0-9]{3}\.png",
            r"visual/[A-Za-z0-9_.-]+/pages/page-[0-9]{3}\.png",
            r"visual/triptychs/page-[0-9]{3}\.png",
        )
    ):
        return "payload"
    raise ReplayError("unregistered_stage_artifact", f"{stage_id}:{relative}")


def _scan_payload(path: Path, stage_id: str, relative: str, source_identity: str) -> None:
    suffix = path.suffix.lower()
    if suffix == ".json":
        value = _read_json_payload(path, stage_id, relative)
        if _payload_contains_poison(value, source_identity):
            raise ReplayError("path_or_identity_poison_in_payload", relative)
    elif suffix in {".md", ".txt", ".csv"}:
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError as error:
            raise ReplayError("invalid_text_payload", relative) from error
        if source_identity in text or any(_DRIVE.match(line.strip()) or _UNC.match(line.strip()) or _DEVICE.match(line.strip()) for line in text.splitlines()):
            raise ReplayError("path_or_identity_poison_in_payload", relative)
    elif suffix not in {".pdf", ".png", ".jpg", ".jpeg"}:
        raise ReplayError("unknown_payload_scan_route", relative)


def _validate_recovered_view_evidence(
    evidence_path: Path, source_view_path: Path, view_id: str,
) -> None:
    """Allow a historical receipt only when the adjacent recovered view seals it."""
    relative = f"views/{view_id}/evidence/origin-view.json"
    source_view = _json(source_view_path)
    _rebase_view(source_view, "0" * 64, {"path": "recovery-evidence"})
    diagnostics = source_view.get("diagnostics")
    origin = diagnostics.get("origin") if isinstance(diagnostics, Mapping) else None
    if not isinstance(origin, Mapping):
        raise ReplayError("recovered_view_evidence_missing_origin", relative)
    receipt = origin.get("receipt")
    receipt_evidence = origin.get("receipt_evidence")
    if not isinstance(receipt, Mapping) or not isinstance(receipt_evidence, Mapping):
        raise ReplayError("recovered_view_evidence_missing_binding", relative)
    identity = file_identity(evidence_path)
    expected_receipt = {"path_hint": f"views/{view_id}/view.json", **identity}
    expected_evidence = {"path_hint": relative, **identity}
    for record, expected in ((receipt, expected_receipt), (receipt_evidence, expected_evidence)):
        if {key: record.get(key) for key in expected} != expected:
            raise ReplayError("recovered_view_evidence_identity_mismatch", relative)
    evidence = _json(evidence_path)
    _rebase_view(evidence, "0" * 64, {"path": "recovery-evidence"})
    if (
        evidence["view_id"] != view_id
        or evidence["receipt_sha256"] != receipt.get("receipt_sha256")
        or evidence["run_identity_sha256"] != origin.get("run_identity_sha256")
    ):
        raise ReplayError("recovered_view_evidence_receipt_mismatch", relative)


def _origin_record(source_root: Path, path: Path, source_run: Mapping[str, Any], stage_id: str) -> dict[str, Any]:
    return {
        "path": path.relative_to(source_root).as_posix(),
        **file_identity(path),
        "source_run_id": source_run["run_id"],
        "source_run_identity_sha256": source_run["portable_identity_sha256"],
        "source_stage_id": stage_id,
    }


def _rebase_stage(stage_id: str, source_root: Path, staging: Path, source_run: Mapping[str, Any], fresh_run: Mapping[str, Any], stage_evidence: Mapping[str, Any], intake_sha: str, upstream: Sequence[Mapping[str, Any]], *, archived_source: bool = False) -> dict[str, Any]:
    source_output = _source_output_path(source_root, stage_id)
    destination = staging / "outputs" / stage_id
    destination.mkdir(parents=True, exist_ok=False)
    source_rows = stage_evidence["source_output"]["files"]
    if deterministic_inventory(source_output) != source_rows:
        raise ReplayError("source_output_inventory_changed", stage_id)
    copied, wrappers, origins = [], [], []
    deferred: list[tuple[str, str, Path, Path, dict[str, Any]]] = []
    for row in source_rows:
        relative = row["path"]
        _validate_relative(relative)
        source_path = source_output / relative
        if file_identity(source_path) != {"bytes": row["bytes"], "sha256": row["sha256"]}:
            raise ReplayError("source_output_row_mismatch", relative)
        kind = _classify(stage_id, relative)
        target = destination / relative
        if kind == "payload":
            _scan_payload(source_path, stage_id, relative, source_run["portable_identity_sha256"])
            identity = _copy_physical(source_path, target)
            copied.append({"source": row, "destination": {"path": relative, **identity}})
        elif kind == "recovered_view_evidence":
            view_id = relative.split("/", 2)[1]
            _validate_recovered_view_evidence(
                source_path, source_output / "views" / view_id / "view.json", view_id,
            )
            identity = _copy_physical(source_path, target)
            copied.append({"source": row, "destination": {"path": relative, **identity}})
        else:
            origin_path = staging / "replay" / "origin" / "wrappers" / stage_id / relative
            origin_identity = _copy_physical(source_path, origin_path)
            origin = _origin_record(source_root, source_path, source_run, stage_id)
            origins.append({"path": origin_path.relative_to(staging).as_posix(), **origin_identity})
            deferred.append((relative, kind, source_path, target, origin))
    fresh_views: dict[str, dict[str, Any]] = {}
    for relative, kind, source_path, target, origin in deferred:
        if kind != "view":
            continue
        fresh = _rebase_view(_json(source_path), fresh_run["portable_identity_sha256"], origin)
        _write_json_new(target, fresh)
        fresh_views[fresh["view_id"]] = fresh
        wrappers.append({"source": next(row for row in source_rows if row["path"] == relative), "origin": next(row for row in origins if row["path"].endswith("/" + relative)), "fresh": {"path": relative, **file_identity(target)}, "transformer": "mineru_view_execution_v1_to_v2", "source_projection_sha256": fresh["semantic_projection_sha256"], "fresh_projection_sha256": fresh["semantic_projection_sha256"]})
    for relative, kind, source_path, target, origin in deferred:
        if kind == "view":
            continue
        source = _json(source_path)
        if kind == "command":
            fresh = _replay_command(stage_id, fresh_run["portable_identity_sha256"], origin)
            projection = None
        elif kind == "view_set":
            fresh = _rebase_view_set(source, fresh_run["portable_identity_sha256"], fresh_views, destination, origin)
            projection = fresh["semantic_projection_sha256"]
        elif kind == "comparison":
            fresh = _rebase_comparison(
                source, fresh_run["portable_identity_sha256"],
                staging / "outputs/01-prepare-inputs/prepared/sample_pages.json",
                staging / "outputs/02-mineru-three-view/view-set.json",
                staging / "outputs/02-mineru-three-view",
                source_root / "outputs/02-mineru-three-view", origin,
            )
            projection = fresh["semantic_projection_sha256"]
        elif kind == "geometry":
            fresh = _rebase_geometry(
                source, fresh_run["portable_identity_sha256"], fresh_run,
                staging / "outputs/01-prepare-inputs/prepared/sample_pages.json",
                staging / "outputs/03-compare-views/comparison.json",
                staging / "outputs/02-mineru-three-view/view-set.json",
                staging / "outputs/02-mineru-three-view",
                source_root / "outputs/01-prepare-inputs",
                source_root / "outputs/02-mineru-three-view",
                source_root / "outputs/03-compare-views",
                destination, origin,
            )
            projection = fresh["semantic_projection_sha256"]
        elif kind == "visual_manifest":
            fresh = _rebase_visual(
                source, fresh_run["portable_identity_sha256"], fresh_run,
                staging / "outputs/01-prepare-inputs/prepared/sample_pages.json",
                staging / "outputs/03-compare-views/comparison.json",
                staging / "outputs/02-mineru-three-view/view-set.json",
                destination / "visual/geometry_plan.json",
                staging / "outputs/02-mineru-three-view",
                source_root / "outputs/01-prepare-inputs",
                source_root / "outputs/02-mineru-three-view",
                source_root / "outputs/03-compare-views",
                destination, origin,
                source_stage4=source_root / "outputs/04-visual-merge-bundle",
            )
            projection = fresh["semantic_projection_sha256"]
        elif kind == "visual_execution":
            source_geometry = _json(source_root / "outputs/04-visual-merge-bundle/visual/geometry_plan.json")
            renderer = copy.deepcopy(source_geometry["renderer"])
            renderer.pop("path_hint", None)
            fresh = _rebase_visual_execution(source, fresh_run["portable_identity_sha256"], destination, origin, renderer)
            projection = fresh["semantic_projection_sha256"]
        else:
            raise ReplayError("unknown_transformer", kind)
        _write_json_new(target, fresh)
        source_projection = projection
        wrappers.append({"source": next(row for row in source_rows if row["path"] == relative), "origin": next(row for row in origins if row["path"].endswith("/" + relative)), "fresh": {"path": relative, **file_identity(target)}, "transformer": f"{kind}_typed_rebase_v1", "source_projection_sha256": source_projection, "fresh_projection_sha256": source_projection})
    operational = deterministic_inventory(destination)
    source_paths = {row["path"] for row in source_rows}
    mapped = [row["source"]["path"] for row in copied] + [row["source"]["path"] for row in wrappers]
    if len(mapped) != len(set(mapped)) or set(mapped) != source_paths:
        raise ReplayError("conservation_mapping_mismatch", stage_id)
    receipt = _seal(REBASE_SCHEMA, {
        "stage_id": stage_id,
        "run_identity_sha256": fresh_run["portable_identity_sha256"],
        "intake_sha256": intake_sha,
        "source_run_identity_sha256": source_run["portable_identity_sha256"],
        "source_manifest": stage_evidence["source_manifest"],
        "source_output_inventory_sha256": stage_evidence["source_output"]["inventory_sha256"],
        "copied_payloads": copied,
        "rebased_wrappers": wrappers,
        "origin_inventory": origins,
        "operational_inventory": operational,
        "operational_inventory_sha256": sha256_bytes(canonical_bytes(operational)),
        "producer_invoked": False,
        "semantic_content_changed": False,
        "acceptance_inferred": False,
    }, "rebase_sha256")
    rebase_path = staging / "stages" / stage_id / "rebase.json"
    _write_json_new(rebase_path, receipt)
    current_transformer_rows = stage_evidence["producer_closure"]["current"]
    current_transformer_sha = stage_evidence["producer_closure"].get(
        "current_transformer_closure_sha256",
        sha256_bytes(canonical_bytes(current_transformer_rows)),
    )
    transformer_closure = {
        "registry_sha256": load_registry()["registry_sha256"],
        "files": current_transformer_rows,
        "producer_closure_sha256": current_transformer_sha,
        "recipe": load_registry()["stages"][STAGE_IDS.index(stage_id)]["argv_recipe"],
    }
    if archived_source:
        # `files` above are the current rebase transformer, never a claim about
        # who created the archived OCR payload.  The latter stays immutable in
        # this versioned provenance record.
        transformer_closure["archived_source_provenance"] = {
            "schema": ARCHIVED_SOURCE_PROVENANCE_SCHEMA,
            "recorded_source_producer": {
                "files": stage_evidence["producer_closure"]["source"],
                "producer_closure_sha256": stage_evidence["producer_closure"]["producer_closure_sha256"],
            },
            "current_transformer": {
                "files": current_transformer_rows,
                "producer_closure_sha256": current_transformer_sha,
            },
        }
    stage_manifest = _seal(STAGE_SCHEMA, {
        "reproducible": {
            "stage_id": stage_id,
            "stage_name": STAGE_NAMES[STAGE_IDS.index(stage_id)],
            "stage_version": 2,
            "state": "succeeded",
            "run_identity_sha256": fresh_run["portable_identity_sha256"],
            "upstream": [dict(item) for item in upstream],
            "inputs": copy.deepcopy(_json(_source_stage_path(source_root, stage_id))["reproducible"]["inputs"]),
            "options": copy.deepcopy(fresh_run["options"]),
            "verification_implementation": {"inventory_sha256": fresh_run["implementation"]["inventory_sha256"]},
            "producer_closure": transformer_closure,
            "outputs": {"root_hint": f"outputs/{stage_id}", "files": operational, "inventory_sha256": sha256_bytes(canonical_bytes(operational))},
            "stage_eligibility_key": stage_evidence["stage_eligibility_key"],
            "rebase": {"path": f"stages/{stage_id}/rebase.json", **file_identity(rebase_path), "rebase_sha256": receipt["rebase_sha256"]},
        },
        "execution": {"mode": "replayed", "producer_invoked": False, "completed_at_utc": _utc_now(), "replay_provenance": {"source_run_id": source_run["run_id"], "source_run_identity_sha256": source_run["portable_identity_sha256"], "source_manifest": stage_evidence["source_manifest"], "source_output_inventory_sha256": stage_evidence["source_output"]["inventory_sha256"], "eligibility_key": stage_evidence["stage_eligibility_key"]}},
    }, "reproducible_sha256")
    manifest_path = staging / "stages" / stage_id / "stage.json"
    _write_json_new(manifest_path, stage_manifest)
    return {"stage_id": stage_id, "manifest_sha256": stage_manifest["reproducible_sha256"], "rebase_sha256": receipt["rebase_sha256"], "output_inventory_sha256": receipt["operational_inventory_sha256"]}


def verify_replay_transform(
    contract_path: Path, source_path: Path, source_run_root: Path,
    through_stage: str, runtime: reconstruction.RuntimeOptions, *, archived_source: bool = False,
) -> dict[str, Any]:
    """Deeply validate every wrapper transform without copying payloads or publishing."""
    count = _through_count(through_stage)
    if count not in {3, 4}:
        raise ReplayError("partial_prefix_not_runnable", through_stage)
    source_run_root = source_run_root.resolve()
    preflight_run_root = Path(tempfile.gettempdir()) / "kb-creator-replay-transform-preflight-never-published"
    fresh_run = _build_fresh_run(
        contract_path, source_path, preflight_run_root,
        "replay-transform-preflight", runtime,
    )
    eligibility = (
        verify_archived_replay_source(
            contract_path, source_path, source_run_root, through_stage, runtime,
            fresh_run=fresh_run,
        ) if archived_source else verify_replay_source(
            contract_path, source_path, source_run_root, through_stage, runtime,
            fresh_run=fresh_run,
        )
    )
    source_run = reconstruction.load_run(source_run_root)
    coverage: list[dict[str, Any]] = []
    payloads_scanned = 0

    with tempfile.TemporaryDirectory(prefix="kb-replay-transform-preflight-") as raw_scratch:
        scratch = Path(raw_scratch)

        def source_wrappers(stage_id: str) -> dict[str, list[tuple[str, str, Path, dict[str, Any]]]]:
            nonlocal payloads_scanned
            stage = next(row for row in eligibility["stages"] if row["stage_id"] == stage_id)
            source_output = _source_output_path(source_run_root, stage_id)
            if deterministic_inventory(source_output) != stage["source_output"]["files"]:
                raise ReplayError("source_output_inventory_changed", stage_id)
            result: dict[str, list[tuple[str, str, Path, dict[str, Any]]]] = {}
            for row in stage["source_output"]["files"]:
                relative = row["path"]
                path = source_output.joinpath(*_validate_relative(relative).parts)
                if file_identity(path) != {"bytes": row["bytes"], "sha256": row["sha256"]}:
                    raise ReplayError("source_output_row_mismatch", relative)
                kind = _classify(stage_id, relative)
                if kind == "payload":
                    _scan_payload(path, stage_id, relative, source_run["portable_identity_sha256"])
                    payloads_scanned += 1
                    continue
                if kind == "recovered_view_evidence":
                    view_id = relative.split("/", 2)[1]
                    _validate_recovered_view_evidence(
                        path, source_output / "views" / view_id / "view.json", view_id,
                    )
                    continue
                result.setdefault(kind, []).append((relative, kind, path, _origin_record(source_run_root, path, source_run, stage_id)))
            return result

        def only(items: Mapping[str, list[tuple[str, str, Path, dict[str, Any]]]], kind: str) -> tuple[str, str, Path, dict[str, Any]]:
            rows = items.get(kind, [])
            if len(rows) != 1:
                raise ReplayError("transform_preflight_wrapper_cardinality", f"{kind}:{len(rows)}")
            return rows[0]

        def emit(stage_id: str, row: tuple[str, str, Path, dict[str, Any]], value: Mapping[str, Any]) -> None:
            relative, kind, source_wrapper, _ = row
            schema, seal_key = _validate_transformed_wrapper(kind, stage_id, value)
            operational = _operational_authority_projection(value)
            if _contains_poison(operational, source_run["portable_identity_sha256"]):
                raise ReplayError("stale_operational_authority", relative)
            target = scratch.joinpath("outputs", stage_id, *_validate_relative(relative).parts)
            _write_json_new(target, value)
            coverage.append({
                "stage_id": stage_id,
                "source_path": relative,
                "kind": kind,
                "source": file_identity(source_wrapper),
                "output_schema": schema,
                "output": file_identity(target),
                "seal_key": seal_key,
                "seal_sha256": value[seal_key],
            })

        stage1 = source_wrappers(STAGE_IDS[0])
        row = only(stage1, "command")
        emit(STAGE_IDS[0], row, _replay_command(STAGE_IDS[0], fresh_run["portable_identity_sha256"], row[3]))

        stage2 = source_wrappers(STAGE_IDS[1])
        fresh_views: dict[str, dict[str, Any]] = {}
        for row in stage2.get("view", []):
            fresh = _rebase_view(_json(row[2]), fresh_run["portable_identity_sha256"], row[3])
            emit(STAGE_IDS[1], row, fresh)
            fresh_views[fresh["view_id"]] = fresh
        row = only(stage2, "view_set")
        stage2_scratch = scratch / "outputs" / STAGE_IDS[1]
        fresh_view_set = _rebase_view_set(
            _json(row[2]), fresh_run["portable_identity_sha256"],
            fresh_views, stage2_scratch, row[3],
        )
        emit(STAGE_IDS[1], row, fresh_view_set)

        stage3 = source_wrappers(STAGE_IDS[2])
        row = only(stage3, "comparison")
        comparison = _rebase_comparison(
            _json(row[2]), fresh_run["portable_identity_sha256"],
            _source_output_path(source_run_root, STAGE_IDS[0]) / "prepared/sample_pages.json",
            stage2_scratch / "view-set.json", stage2_scratch,
            _source_output_path(source_run_root, STAGE_IDS[1]), row[3],
            artifact_stage2=_source_output_path(source_run_root, STAGE_IDS[1]),
        )
        emit(STAGE_IDS[2], row, comparison)
        comparison_path = scratch / "outputs" / STAGE_IDS[2] / "comparison.json"
        row = only(stage3, "command")
        emit(STAGE_IDS[2], row, _replay_command(STAGE_IDS[2], fresh_run["portable_identity_sha256"], row[3]))

        if count == 3:
            return _seal("kb_creator.replay_transform_preflight.v2", {
                "state": "pass", "source_run_id": source_run["run_id"],
                "source_run_identity_sha256": source_run["portable_identity_sha256"],
                "fresh_preflight_identity_sha256": fresh_run["portable_identity_sha256"],
                "eligibility_sha256": eligibility["eligibility_sha256"],
                "requested_prefix": list(STAGE_IDS[:3]), "wrapper_count": len(coverage),
                "payload_count_scanned": payloads_scanned, "wrappers": coverage,
                "payloads_copied": False, "target_created": False, "published": False,
                "acceptance_inferred": False,
            }, "preflight_sha256")

        stage4 = source_wrappers(STAGE_IDS[3])
        stage4_source = _source_output_path(source_run_root, STAGE_IDS[3])
        row = only(stage4, "geometry")
        geometry = _rebase_geometry(
            _json(row[2]), fresh_run["portable_identity_sha256"], fresh_run,
            _source_output_path(source_run_root, STAGE_IDS[0]) / "prepared/sample_pages.json",
            comparison_path, stage2_scratch / "view-set.json", stage2_scratch,
            _source_output_path(source_run_root, STAGE_IDS[0]),
            _source_output_path(source_run_root, STAGE_IDS[1]),
            _source_output_path(source_run_root, STAGE_IDS[2]),
            stage4_source, row[3],
            artifact_stage2=_source_output_path(source_run_root, STAGE_IDS[1]),
            rendered_stage4=stage4_source,
        )
        emit(STAGE_IDS[3], row, geometry)
        geometry_path = scratch / "outputs" / STAGE_IDS[3] / "visual/geometry_plan.json"

        row = only(stage4, "visual_execution")
        source_geometry = _json(_source_output_path(source_run_root, STAGE_IDS[3]) / "visual/geometry_plan.json")
        renderer = copy.deepcopy(source_geometry["renderer"])
        renderer.pop("path_hint", None)
        execution = _rebase_visual_execution(
            _json(row[2]), fresh_run["portable_identity_sha256"],
            stage4_source, row[3], renderer,
        )
        emit(STAGE_IDS[3], row, execution)

        row = only(stage4, "visual_manifest")
        visual = _rebase_visual(
            _json(row[2]), fresh_run["portable_identity_sha256"], fresh_run,
            _source_output_path(source_run_root, STAGE_IDS[0]) / "prepared/sample_pages.json",
            comparison_path, stage2_scratch / "view-set.json", geometry_path,
            stage2_scratch,
            _source_output_path(source_run_root, STAGE_IDS[0]),
            _source_output_path(source_run_root, STAGE_IDS[1]),
            _source_output_path(source_run_root, STAGE_IDS[2]),
            stage4_source, row[3],
            artifact_stage2=_source_output_path(source_run_root, STAGE_IDS[1]),
            payload_stage4=stage4_source,
            source_stage4=stage4_source,
        )
        emit(STAGE_IDS[3], row, visual)
        row = only(stage4, "command")
        emit(STAGE_IDS[3], row, _replay_command(STAGE_IDS[3], fresh_run["portable_identity_sha256"], row[3]))

        expected_wrappers = sum(
            1
            for stage in eligibility["stages"]
            for source_row in stage["source_output"]["files"]
            if _classify(stage["stage_id"], source_row["path"]) != "payload"
        )
        if len(coverage) != expected_wrappers or len({(row["stage_id"], row["source_path"]) for row in coverage}) != len(coverage):
            raise ReplayError("transform_preflight_coverage_mismatch")

    return _seal(TRANSFORM_PREFLIGHT_SCHEMA, {
        "state": "pass",
        "source_run_id": source_run["run_id"],
        "source_run_identity_sha256": source_run["portable_identity_sha256"],
        "fresh_preflight_identity_sha256": fresh_run["portable_identity_sha256"],
        "eligibility_sha256": eligibility["eligibility_sha256"],
        "requested_prefix": list(STAGE_IDS),
        "wrapper_count": len(coverage),
        "payload_count_scanned": payloads_scanned,
        "wrappers": coverage,
        "payloads_copied": False,
        "target_created": False,
        "published": False,
        "acceptance_inferred": False,
    }, "preflight_sha256")


def verify_archived_replay_transform(
    contract_path: Path, source_path: Path, source_run_root: Path,
    runtime: reconstruction.RuntimeOptions,
) -> dict[str, Any]:
    """Read-only typed-wrapper preflight for an archived native 01--03 import."""
    return verify_replay_transform(
        contract_path, source_path, source_run_root, "03-compare-views", runtime,
        archived_source=True,
    )


def _write_review(source_root: Path, staging: Path, fresh_run: Mapping[str, Any], bridge: Mapping[str, Any]) -> None:
    source_queue = _json(source_root / "review/review_queue.json")
    comparison = staging / "outputs/03-compare-views/comparison.json"
    items = copy.deepcopy(source_queue["items"])
    queue = _seal(QUEUE_SCHEMA, {
        "run_identity_sha256": fresh_run["portable_identity_sha256"],
        "contract_sha256": fresh_run["contract"]["sha256"],
        "source_sha256": fresh_run["source"]["sha256"],
        "comparison": {"path": "outputs/03-compare-views/comparison.json", **file_identity(comparison)},
        "bridge": {"path": "replay/bridge.json", **file_identity(staging / "replay/bridge.json"), "bridge_sha256": bridge["bridge_sha256"]},
        "required_decision_schema": source_queue["required_decision_schema"],
        "items": items,
    }, "queue_sha256")
    review = staging / "review"
    _write_json_new(review / "review_queue.json", queue)
    _write_json_new(review / "decision_set.template.json", {
        "schema": reconstruction.DECISION_SET_SCHEMA,
        "review_queue_sha256": queue["queue_sha256"],
        "contract_sha256": fresh_run["contract"]["sha256"],
        "source_sha256": fresh_run["source"]["sha256"],
        "decisions": [],
        "reviewed_allowlist": None,
        "submission_state": "draft",
    })


def _write_hybrid_review(staging: Path, fresh_run: Mapping[str, Any], bridge: Mapping[str, Any], contract: Mapping[str, Any]) -> None:
    """Create a queue from the freshly executed Stage04, never a source queue."""
    bundle = staging / "outputs/04-visual-merge-bundle"
    comparison = staging / "outputs/03-compare-views/comparison.json"
    prepared = staging / "outputs/01-prepare-inputs/prepared/sample_pages.json"
    direct = reconstruction.make_queue(dict(fresh_run), dict(contract), bundle, comparison, prepared)
    body = {key: value for key, value in direct.items() if key not in {"schema", "queue_sha256"}}
    body["bridge"] = {"path": "replay/bridge.json", **file_identity(staging / "replay/bridge.json"), "bridge_sha256": bridge["bridge_sha256"]}
    queue = _seal(QUEUE_SCHEMA, body, "queue_sha256")
    review = staging / "review"
    _write_json_new(review / "review_queue.json", queue)
    _write_json_new(review / "decision_set.template.json", {
        "schema": reconstruction.DECISION_SET_SCHEMA, "review_queue_sha256": queue["queue_sha256"],
        "contract_sha256": fresh_run["contract"]["sha256"], "source_sha256": fresh_run["source"]["sha256"],
        "decisions": [], "reviewed_allowlist": None, "submission_state": "draft",
    })


def replay_run_engine(contract_path: Path, source_path: Path, source_run_root: Path, new_run_root: Path, new_run_id: str, through_stage: str, runtime: reconstruction.RuntimeOptions, *, archived_source: bool = False) -> dict[str, Any]:
    count = _through_count(through_stage)
    if count not in {3, 4}:
        raise ReplayError("partial_prefix_execution_not_implemented", "only the reviewed 01-03 hybrid route is runnable")
    source_run_root = source_run_root.resolve()
    _assert_roots(source_run_root, new_run_root)
    fresh_run = _build_fresh_run(contract_path, source_path, new_run_root, new_run_id, runtime)
    eligibility = (
        verify_archived_replay_source(contract_path, source_path, source_run_root, through_stage, runtime, fresh_run=fresh_run)
        if archived_source else verify_replay_source(contract_path, source_path, source_run_root, through_stage, runtime, fresh_run=fresh_run)
    )
    source_run = reconstruction.load_run(source_run_root)
    if fresh_run["portable_identity_sha256"] == source_run["portable_identity_sha256"]:
        raise ReplayError("replay_of_self")
    operation_id = uuid.uuid4().hex
    staging = new_run_root.parent / f".{new_run_root.name}.replay-{operation_id}"
    if staging.exists():
        raise ReplayError("staging_collision")
    staging.mkdir()
    _write_json_new(staging / ".replay-owner.json", {"operation_id": operation_id, "final_root": str(new_run_root.absolute())})
    try:
        fresh_run["local"]["run_root"] = str(new_run_root.resolve())
        _write_json_new(staging / "run.json", fresh_run)
        source_manifest_inventory = []
        for stage_id in STAGE_IDS[:count]:
            source_stage = _source_stage_path(source_run_root, stage_id)
            target = staging / "replay/origin/stages" / stage_id / "stage.json"
            _copy_physical(source_stage, target)
            source_manifest_inventory.append({"stage_id": stage_id, "path": target.relative_to(staging).as_posix(), **file_identity(target)})
        intake = _seal(INTAKE_SCHEMA, {
            "run_id": fresh_run["run_id"],
            "run_identity_sha256": fresh_run["portable_identity_sha256"],
            "source_run": {
                "run_id": source_run["run_id"], "portable_identity_sha256": source_run["portable_identity_sha256"],
                "run_json": eligibility["source_run_json"],
                **({"provenance_schema": ARCHIVED_SOURCE_PROVENANCE_SCHEMA,
                    "import_mode": "archived_source_artifact_import"} if archived_source else {}),
            },
            "requested_prefix": eligibility["requested_prefix"],
            "registry": eligibility["registry"],
            "source_stage_manifests": source_manifest_inventory,
            "eligibility_sha256": eligibility["eligibility_sha256"],
            "ancestry": [source_run["portable_identity_sha256"]],
            "acceptance_inferred": False,
            "decisions_replayed": False,
            "stages_05_06_replayed": False,
        }, "intake_sha256")
        _write_json_new(staging / "replay/intake.json", intake)
        stage_receipts = []
        for stage in eligibility["stages"]:
            receipt = _rebase_stage(stage["stage_id"], source_run_root, staging, source_run, fresh_run, stage, intake["intake_sha256"], stage_receipts, archived_source=archived_source)
            stage_receipts.append(receipt)
        bridge = _seal(BRIDGE_SCHEMA, {
            "run_identity_sha256": fresh_run["portable_identity_sha256"],
            "intake": {"path": "replay/intake.json", **file_identity(staging / "replay/intake.json"), "intake_sha256": intake["intake_sha256"]},
            "stages": stage_receipts,
            "operational_stale_authority_count": 0,
            "acceptance_inferred": False,
            "decisions_replayed": False,
            "stages_05_06_replayed": False,
        }, "bridge_sha256")
        _write_json_new(staging / "replay/bridge.json", bridge)
        if count == 3:
            # Publish the verified incomplete prefix before executing Stage04.
            # Its native visual evidence records real absolute paths, which must
            # remain stable.  Consumers reject this prefix until completion.
            _validate_replayed_prefix_graph(staging, "03-compare-views")
            if new_run_root.exists():
                raise ReplayError("destination_raced")
            (staging / ".replay-owner.json").unlink()
            staging.rename(new_run_root)
            contract, _contract_sha = reconstruction.load_contract(contract_path)
            execution_run = copy.deepcopy(fresh_run)
            execution_run["local"]["run_root"] = str(new_run_root.resolve())
            adapters = reconstruction.production_run_adapters(execution_run, contract_path, source_path)
            from .reconstruction_hybrid_stage04 import invoke_stage04
            stage04 = invoke_stage04(new_run_root, execution_run, stage_receipts, adapters["visual_merge_bundle"])
            stage04_path = new_run_root / "stages/04-visual-merge-bundle/stage.json"
            completion = _seal(HYBRID_COMPLETION_SCHEMA, {
                "run_identity_sha256": fresh_run["portable_identity_sha256"],
                "bridge": {"path": "replay/bridge.json", **file_identity(new_run_root / "replay/bridge.json"), "bridge_sha256": bridge["bridge_sha256"]},
                "replayed_stages": stage_receipts,
                "executed_stage": {"stage_id": stage04["stage_id"], "execution": {"mode": "executed", "producer_invoked": True}, "manifest": {"path": "stages/04-visual-merge-bundle/stage.json", **file_identity(stage04_path), "reproducible_sha256": stage04["manifest_sha256"]}},
                "acceptance_inferred": False,
            }, "completion_sha256")
            _write_json_new(new_run_root / "replay/completion.json", completion)
            validate_replayed_prefix(new_run_root)
            _write_hybrid_review(new_run_root, fresh_run, bridge, contract)
            result = {"schema": "kb_creator.replay_result.v1", "state": "needs_review", "exit_code": 10, "run_root": str(new_run_root), "run_identity_sha256": fresh_run["portable_identity_sha256"], "bridge_sha256": bridge["bridge_sha256"], "acceptance_inferred": False}
            _write_json_new(new_run_root / "result.json", result)
            return result
        else:
            _write_review(source_run_root, staging, fresh_run, bridge)
        _write_json_new(staging / "result.json", {"schema": "kb_creator.replay_result.v1", "state": "needs_review", "exit_code": 10, "run_identity_sha256": fresh_run["portable_identity_sha256"], "bridge_sha256": bridge["bridge_sha256"], "acceptance_inferred": False})
        (staging / ".replay-owner.json").unlink()
        validate_replayed_prefix(staging, expected_through="03-compare-views" if count == 3 else "04-visual-merge-bundle", allow_staging=True)
        if new_run_root.exists():
            raise ReplayError("destination_raced")
        staging.rename(new_run_root)
        try:
            validate_replayed_prefix(new_run_root, expected_through="03-compare-views" if count == 3 else "04-visual-merge-bundle")
        except Exception:
            quarantine = new_run_root.parent / f".{new_run_root.name}.replay-quarantine-{operation_id}"
            if quarantine.exists():
                raise ReplayError("post_publish_quarantine_collision")
            new_run_root.rename(quarantine)
            raise
    except Exception:
        if staging.exists():
            if (staging / "failures/04-visual-merge-bundle").is_dir():
                # Keep failed execution evidence in its owned quarantine.  The
                # requested destination remains absent and cannot claim review.
                quarantine = new_run_root.parent / f".{new_run_root.name}.replay-failed-{operation_id}"
                if quarantine.exists():
                    raise ReplayError("failure_quarantine_collision")
                staging.rename(quarantine)
                raise
            marker = staging / ".replay-owner.json"
            if not marker.exists():
                _write_json_new(marker, {"operation_id": operation_id, "final_root": str(new_run_root.absolute())})
            _cleanup_owned(staging, operation_id, new_run_root)
        raise
    return {"schema": "kb_creator.replay_result.v1", "state": "needs_review", "exit_code": 10, "run_root": str(new_run_root), "run_identity_sha256": fresh_run["portable_identity_sha256"], "bridge_sha256": bridge["bridge_sha256"], "acceptance_inferred": False}


def replay_archived_run_engine(contract_path: Path, source_path: Path, source_run_root: Path, new_run_root: Path, new_run_id: str, runtime: reconstruction.RuntimeOptions) -> dict[str, Any]:
    """Import sealed native 01--03 artifacts and execute only the fresh Stage04."""
    return replay_run_engine(
        contract_path, source_path, source_run_root, new_run_root, new_run_id,
        "03-compare-views", runtime, archived_source=True,
    )


def validate_hybrid_completion(
    completion: Mapping[str, Any], run_identity: str, bridge_identity: Mapping[str, Any],
    upstream: Sequence[Mapping[str, Any]], stage_identity: Mapping[str, Any], stage_receipt: Mapping[str, Any],
) -> None:
    """Validate the same closed completion edge in live runs and portable packages."""
    try:
        validate_seal(completion, "completion_sha256")
    except (ValueError, TypeError) as error:
        raise ReplayError("hybrid_completion_seal_mismatch") from error
    expected = {
        "schema": HYBRID_COMPLETION_SCHEMA,
        "run_identity_sha256": run_identity,
        "bridge": {"path": "replay/bridge.json", **bridge_identity},
        "replayed_stages": list(upstream),
        "executed_stage": {
            "stage_id": STAGE_IDS[3],
            "execution": {"mode": "executed", "producer_invoked": True},
            "manifest": {"path": "stages/04-visual-merge-bundle/stage.json", **stage_identity, "reproducible_sha256": stage_receipt["manifest_sha256"]},
        },
        "acceptance_inferred": False,
    }
    if (
        stage_receipt.get("stage_id") != STAGE_IDS[3]
        or [row.get("stage_id") for row in upstream] != list(STAGE_IDS[:3])
        or {key: value for key, value in completion.items() if key != "completion_sha256"} != expected
    ):
        raise ReplayError("hybrid_completion_authority_mismatch")


def _archived_closure_freshness(closure: Mapping[str, Any]) -> dict[str, Any]:
    """Report current producer drift without making it an artifact decision."""
    changed: list[str] = []
    unknown: list[str] = []
    for row in closure["files"]:
        try:
            if _current_row(row["path"]) != row:
                changed.append(row["path"])
        except (KeyError, ReplayError):
            unknown.append(str(row.get("path", "")))
    state = "unknown" if unknown else "stale" if changed else "fresh"
    return {"state": state, "changed_paths": changed, "unknown_paths": unknown}


def _validate_archived_closure(run: Mapping[str, Any], closure: Mapping[str, Any], stage_id: str) -> dict[str, Any]:
    files = closure.get("files")
    if not isinstance(files, list) or not files:
        raise ReplayError("archived_producer_closure_invalid", stage_id)
    inventory = run.get("implementation")
    inventory_files = inventory.get("files") if isinstance(inventory, dict) else None
    if not isinstance(inventory_files, list) or inventory.get("inventory_sha256") != sha256_bytes(canonical_bytes(inventory_files)):
        raise ReplayError("archived_implementation_inventory_mismatch", stage_id)
    rows: dict[str, dict[str, Any]] = {}
    for row in inventory_files:
        if not isinstance(row, dict) or set(row) != {"path", "bytes", "sha256"} or not isinstance(row.get("path"), str) or row["path"] in rows:
            raise ReplayError("archived_implementation_inventory_invalid", stage_id)
        _validate_relative(row["path"])
        rows[row["path"]] = row
    closure_paths: set[str] = set()
    for row in files:
        if not isinstance(row, dict) or set(row) != {"path", "bytes", "sha256"} or not isinstance(row.get("path"), str):
            raise ReplayError("archived_producer_closure_invalid", stage_id)
        _validate_relative(row["path"])
        if row["path"] in closure_paths or rows.get(row["path"]) != row:
            raise ReplayError("archived_producer_closure_mismatch", stage_id)
        closure_paths.add(row["path"])
    if closure.get("producer_closure_sha256") != sha256_bytes(canonical_bytes(files)):
        raise ReplayError("archived_producer_closure_digest_mismatch", stage_id)
    return _archived_closure_freshness(closure)


def _validate_archived_source_provenance(closure: Mapping[str, Any], source_manifest: Mapping[str, Any], stage_id: str) -> None:
    """Verify the two identities in an archived import without conflating them."""
    value = closure.get("archived_source_provenance")
    if not isinstance(value, dict) or set(value) != {"schema", "recorded_source_producer", "current_transformer"}:
        raise ReplayError("archived_source_provenance_invalid", stage_id)
    if value["schema"] != ARCHIVED_SOURCE_PROVENANCE_SCHEMA:
        raise ReplayError("archived_source_provenance_schema", stage_id)
    for label in ("recorded_source_producer", "current_transformer"):
        row = value[label]
        if not isinstance(row, dict) or set(row) != {"files", "producer_closure_sha256"} or not isinstance(row["files"], list):
            raise ReplayError("archived_source_provenance_invalid", stage_id)
        if row["producer_closure_sha256"] != sha256_bytes(canonical_bytes(row["files"])):
            raise ReplayError("archived_source_provenance_digest", stage_id)
    current = value["current_transformer"]
    if current["files"] != closure.get("files") or current["producer_closure_sha256"] != closure.get("producer_closure_sha256"):
        raise ReplayError("archived_transformer_closure_mismatch", stage_id)
    original = source_manifest.get("reproducible", {}).get("producer_closure", {})
    original_files = original.get("files") if isinstance(original, dict) else None
    if isinstance(original_files, list) and original_files != value["recorded_source_producer"]["files"]:
        raise ReplayError("archived_source_producer_mismatch", stage_id)


def _validate_replayed_prefix_graph(run_root: Path, expected_through: str, *, archived: bool = False) -> tuple[dict, dict, list, list[dict[str, Any]]]:
    """Check only the selected replay graph; never grant a consumer authority."""
    count = _through_count(expected_through)
    run_root = run_root.absolute()
    if not run_root.is_dir():
        raise ReplayError("replay_run_missing")
    _assert_tree_safe(run_root)
    try:
        run = reconstruction.load_run(run_root) if archived else _json(run_root / "run.json")
    except (OSError, KeyError, reconstruction.ControlPlaneError) as error:
        raise ReplayError("archived_run_invalid", str(error)) from error
    portable = {key: value for key, value in run.items() if key not in {"local", "portable_identity_sha256"}}
    if sha256_bytes(canonical_bytes(portable)) != run.get("portable_identity_sha256"):
        raise ReplayError("fresh_run_identity_mismatch")
    intake = _json(run_root / "replay/intake.json")
    bridge = _json(run_root / "replay/bridge.json")
    try:
        validate_seal(intake, "intake_sha256")
        validate_seal(bridge, "bridge_sha256")
    except ValueError as error:
        raise ReplayError("replay_graph_seal_mismatch") from error
    if intake.get("run_identity_sha256") != run["portable_identity_sha256"] or bridge.get("run_identity_sha256") != run["portable_identity_sha256"]:
        raise ReplayError("fresh_identity_injection")
    ancestry = intake.get("ancestry")
    if not isinstance(ancestry, list) or len(ancestry) != len(set(ancestry)) or run["portable_identity_sha256"] in ancestry:
        raise ReplayError("replay_ancestry_cycle")
    if intake.get("requested_prefix") != list(STAGE_IDS[:count]) or [row.get("stage_id") for row in bridge.get("stages", [])] != list(STAGE_IDS[:count]):
        raise ReplayError("replay_prefix_mismatch")
    if any(intake.get(key) is not False or bridge.get(key) is not False for key in ("acceptance_inferred", "decisions_replayed", "stages_05_06_replayed")):
        raise ReplayError("forbidden_replay_claim")
    if bridge.get("operational_stale_authority_count") != 0:
        raise ReplayError("stale_operational_authority")
    current_registry = load_registry()
    if intake.get("registry", {}).get("registry_sha256") != current_registry["registry_sha256"]:
        raise ReplayError("historical_registry_snapshot_required" if archived else "registry_drift")
    upstream = []
    freshness = []
    for ordinal, stage_id in enumerate(STAGE_IDS[:count]):
        rebase_path = run_root / "stages" / stage_id / "rebase.json"
        stage_path = run_root / "stages" / stage_id / "stage.json"
        rebase, stage = _json(rebase_path), _json(stage_path)
        try:
            validate_seal(rebase, "rebase_sha256")
            validate_seal(stage, "reproducible_sha256")
        except ValueError as error:
            raise ReplayError("stage_replay_seal_mismatch", stage_id) from error
        if rebase.get("run_identity_sha256") != run["portable_identity_sha256"] or stage.get("reproducible", {}).get("run_identity_sha256") != run["portable_identity_sha256"]:
            raise ReplayError("old_identity_in_operational_stage", stage_id)
        execution = stage.get("execution")
        if not isinstance(execution, dict) or execution.get("mode") != "replayed" or execution.get("producer_invoked") is not False or any(key in execution for key in ("argv", "environment", "stdout", "stderr")):
            raise ReplayError("fake_replay_execution", stage_id)
        output_root = run_root / "outputs" / stage_id
        observed = deterministic_inventory(output_root)
        if observed != rebase.get("operational_inventory") or sha256_bytes(canonical_bytes(observed)) != rebase.get("operational_inventory_sha256"):
            raise ReplayError("operational_inventory_mismatch", stage_id)
        if stage_id == "03-compare-views":
            comparison_value = _json(output_root / "comparison.json")
            _validate_comparison_v3(comparison_value)
            view_roots = {view_id: run_root / "outputs/02-mineru-three-view/views" / view_id / "artifacts" for view_id in comparison_value["succeeded_views"]}
            resolve_reference(run_root, comparison_value["manifest"], view_roots)
            view_set_ref = {key: comparison_value["view_set"][key] for key in ("base", "path", "bytes", "sha256")}
            view_set_path = resolve_reference(run_root, view_set_ref, view_roots)
            if _json(view_set_path)["receipt_sha256"] != comparison_value["view_set"]["receipt_sha256"]:
                raise ReplayError("comparison_view_set_seal_mismatch")
            for view_id, view in comparison_value["views"].items():
                for ref in view["artifacts"].values():
                    resolve_reference(run_root, ref, view_roots)
            for skipped in comparison_value["skipped_views"]:
                receipt_ref = {key: skipped["receipt"][key] for key in ("base", "path", "bytes", "sha256")}
                receipt_path = resolve_reference(run_root, receipt_ref, view_roots)
                if _json(receipt_path)["receipt_sha256"] != skipped["receipt"]["receipt_sha256"]:
                    raise ReplayError("comparison_skipped_receipt_seal_mismatch")
        elif stage_id == "04-visual-merge-bundle":
            geometry_value = _json(output_root / "visual/geometry_plan.json")
            visual_value = _json(output_root / "visual/visual_manifest.json")
            execution_value = _json(output_root / "evidence/execution.json")
            _validate_geometry_v2(geometry_value)
            _validate_visual_v3(visual_value)
            _require_keys(execution_value, {"schema", "run_identity_sha256", "origin", "renderer", "copied_render_inventory", "execution", "semantic_projection_sha256", "execution_sha256"}, "visual replay execution")
            try:
                validate_seal(execution_value, "execution_sha256")
            except ValueError as error:
                raise ReplayError("visual_execution_seal_mismatch") from error
            if execution_value["run_identity_sha256"] != run["portable_identity_sha256"] or execution_value["execution"] != {"mode": "replayed", "producer_invoked": False}:
                raise ReplayError("visual_execution_authority_mismatch")
            view_roots = {row["view_id"]: run_root / "outputs/02-mineru-three-view/views" / row["view_id"] / "artifacts" for row in geometry_value["layouts"]}
            for ref in (geometry_value["preparation_manifest"],):
                resolve_reference(run_root, ref, view_roots)
            for wrapped in (geometry_value["comparison"], geometry_value["view_set"], visual_value["inputs"]["comparison"], visual_value["inputs"]["view_set"], visual_value["geometry_plan"]):
                resolve_reference(run_root, {key: wrapped[key] for key in ("base", "path", "bytes", "sha256")}, view_roots)
            for row in geometry_value["layouts"]:
                resolve_reference(run_root, row["layout"], view_roots)
            for ref in visual_value["layouts"].values():
                resolve_reference(run_root, ref, view_roots)
        source_identity = intake["source_run"]["portable_identity_sha256"]
        for artifact in output_root.rglob("*.json"):
            relative = artifact.relative_to(output_root).as_posix()
            kind = _classify(stage_id, relative)
            if kind == "payload":
                operational = _read_json_payload(artifact, stage_id, relative)
                poisoned = _payload_contains_poison(operational, source_identity)
            elif kind == "recovered_view_evidence":
                view_id = relative.split("/", 2)[1]
                _validate_recovered_view_evidence(
                    artifact,
                    run_root / "replay/origin/wrappers" / stage_id / "views" / view_id / "view.json",
                    view_id,
                )
                poisoned = False
            else:
                operational = _operational_authority_projection(_json(artifact))
                poisoned = _contains_poison(operational, source_identity)
            if poisoned:
                raise ReplayError("stale_operational_authority", artifact.relative_to(run_root).as_posix())
        mapped = [row["source"]["path"] for row in rebase.get("copied_payloads", [])] + [row["source"]["path"] for row in rebase.get("rebased_wrappers", [])]
        source_manifest = _json(run_root / "replay/origin/stages" / stage_id / "stage.json")
        archived_manifest = next((row for row in intake.get("source_stage_manifests", []) if row.get("stage_id") == stage_id), None)
        expected_manifest = {"stage_id": stage_id, "path": f"replay/origin/stages/{stage_id}/stage.json", **file_identity(run_root / "replay/origin/stages" / stage_id / "stage.json")}
        if archived_manifest != expected_manifest or rebase.get("source_manifest") != {"path": f"stages/{stage_id}/stage.json", **file_identity(run_root / "replay/origin/stages" / stage_id / "stage.json"), "reproducible_sha256": source_manifest.get("reproducible_sha256")}:
            raise ReplayError("archived_origin_manifest_mismatch", stage_id)
        source_paths = [row["path"] for row in source_manifest["reproducible"]["outputs"]["files"]]
        if len(mapped) != len(set(mapped)) or sorted(mapped) != sorted(source_paths):
            raise ReplayError("conservation_mapping_mismatch", stage_id)
        for row in rebase.get("rebased_wrappers", []):
            if row.get("source_projection_sha256") != row.get("fresh_projection_sha256"):
                raise ReplayError("semantic_projection_mismatch", row.get("fresh", {}).get("path", ""))
            origin_path = run_root / row["origin"]["path"]
            if not origin_path.is_file() or file_identity(origin_path) != {"bytes": row["origin"]["bytes"], "sha256": row["origin"]["sha256"]}:
                raise ReplayError("origin_vault_identity_mismatch")
        closure = stage["reproducible"]["producer_closure"]
        source_import = intake.get("source_run", {}).get("import_mode") == "archived_source_artifact_import"
        if source_import:
            _validate_archived_source_provenance(closure, source_manifest, stage_id)
        if archived:
            freshness.append({"stage_id": stage_id, **_validate_archived_closure(run, closure, stage_id)})
        else:
            current_rows = [_current_row(item["path"]) for item in closure["files"]]
            if current_rows != closure["files"] or sha256_bytes(canonical_bytes(current_rows)) != closure["producer_closure_sha256"]:
                raise ReplayError("producer_closure_changed", stage_id)
        bridge_row = bridge["stages"][ordinal]
        if bridge_row != {"stage_id": stage_id, "manifest_sha256": stage["reproducible_sha256"], "rebase_sha256": rebase["rebase_sha256"], "output_inventory_sha256": rebase["operational_inventory_sha256"]}:
            raise ReplayError("bridge_stage_mismatch", stage_id)
        upstream.append(bridge_row)
    return run, bridge, upstream, freshness


def validate_replayed_prefix(run_root: Path, expected_through: str | None = None, *, allow_staging: bool = False) -> FreshReplayAuthorities:
    if expected_through is None:
        expected_through = "03-compare-views" if (run_root / "replay/completion.json").is_file() else "04-visual-merge-bundle"
    count = _through_count(expected_through)
    run_root = run_root.absolute()
    run, bridge, upstream, _ = _validate_replayed_prefix_graph(run_root, expected_through)
    if count == 3:
        completion_path = run_root / "replay/completion.json"
        completion = _json(completion_path)
        try:
            validate_seal(completion, "completion_sha256")
        except ValueError as error:
            raise ReplayError("hybrid_completion_seal_mismatch") from error
        expected_completion = {
            "schema": HYBRID_COMPLETION_SCHEMA,
            "run_identity_sha256": run["portable_identity_sha256"],
            "bridge": {"path": "replay/bridge.json", **file_identity(run_root / "replay/bridge.json"), "bridge_sha256": bridge["bridge_sha256"]},
            "replayed_stages": upstream,
            "acceptance_inferred": False,
        }
        if any(completion.get(key) != value for key, value in expected_completion.items()):
            raise ReplayError("hybrid_completion_authority_mismatch")
        try:
            from .reconstruction_hybrid_stage04 import validate_stage04
            execution_run = copy.deepcopy(run)
            execution_run["local"]["run_root"] = str(run_root.resolve())
            stage04 = validate_stage04(run_root, execution_run, upstream)
        except (OSError, KeyError, reconstruction.ControlPlaneError) as error:
            raise ReplayError("hybrid_stage04_invalid", str(error)) from error
        validate_hybrid_completion(
            completion, run["portable_identity_sha256"],
            {**file_identity(run_root / "replay/bridge.json"), "bridge_sha256": bridge["bridge_sha256"]},
            upstream, file_identity(run_root / "stages/04-visual-merge-bundle/stage.json"), stage04,
        )
    if not allow_staging:
        local_root = Path(str(run.get("local", {}).get("run_root", ""))).absolute()
        if local_root != run_root:
            raise ReplayError("fresh_run_root_binding_mismatch")
    return FreshReplayAuthorities(
        run_root=run_root,
        stage_02_root=run_root / "outputs/02-mineru-three-view" if count >= 2 else None,
        comparison=run_root / "outputs/03-compare-views/comparison.json" if count >= 3 else None,
        merge_packets=run_root / "outputs/04-visual-merge-bundle/merge_packets" if count == 4 or count == 3 and (run_root / "replay/completion.json").is_file() else None,
        visual_manifest=run_root / "outputs/04-visual-merge-bundle/visual/visual_manifest.json" if count == 4 or count == 3 and (run_root / "replay/completion.json").is_file() else None,
        geometry_plan=run_root / "outputs/04-visual-merge-bundle/visual/geometry_plan.json" if count == 4 or count == 3 and (run_root / "replay/completion.json").is_file() else None,
        bridge_sha256=bridge["bridge_sha256"],
    )


def validate_replay_authorities(run_root: Path, *, allow_staging: bool = False) -> FreshReplayAuthorities:
    """Dispatch only explicit replay topologies; a bare 03 bridge is invalid."""
    root = Path(run_root)
    return validate_replayed_prefix(
        root,
        expected_through="03-compare-views" if (root / "replay/completion.json").is_file() else "04-visual-merge-bundle",
        allow_staging=allow_staging,
    )


def validate_replay_artifacts_for_consumption(run_root: Path) -> ArchivedReplayArtifacts:
    """Grant read-only authority to a sealed replay-hybrid Stage 04 archive.

    This intentionally proves recorded closures against the sealed run inventory,
    while exposing live producer drift as reporting only.  It is never suitable
    for resume or re-execution.
    """
    root = Path(run_root).absolute()
    run, bridge, upstream, freshness_rows = _validate_replayed_prefix_graph(
        root, "03-compare-views", archived=True,
    )
    completion = _json(root / "replay/completion.json")
    try:
        validate_seal(completion, "completion_sha256")
    except ValueError as error:
        raise ReplayError("hybrid_completion_seal_mismatch") from error
    expected_completion = {
        "schema": HYBRID_COMPLETION_SCHEMA,
        "run_identity_sha256": run["portable_identity_sha256"],
        "bridge": {"path": "replay/bridge.json", **file_identity(root / "replay/bridge.json"), "bridge_sha256": bridge["bridge_sha256"]},
        "replayed_stages": upstream,
        "acceptance_inferred": False,
    }
    if any(completion.get(key) != value for key, value in expected_completion.items()):
        raise ReplayError("hybrid_completion_authority_mismatch")
    try:
        from .reconstruction_hybrid_stage04 import validate_stage04_artifacts
        stage04 = validate_stage04_artifacts(root, run, upstream)
    except (OSError, KeyError, reconstruction.ControlPlaneError) as error:
        raise ReplayError("hybrid_stage04_invalid", str(error)) from error
    validate_hybrid_completion(
        completion, run["portable_identity_sha256"],
        {**file_identity(root / "replay/bridge.json"), "bridge_sha256": bridge["bridge_sha256"]},
        upstream, file_identity(root / "stages/04-visual-merge-bundle/stage.json"), stage04,
    )
    changed_paths = [
        {"stage_id": row["stage_id"], "path": path}
        for row in freshness_rows for path in row["changed_paths"]
    ]
    unknown_paths = [
        {"stage_id": row["stage_id"], "path": path}
        for row in freshness_rows for path in row["unknown_paths"]
    ]
    state = "unknown" if unknown_paths else "stale" if changed_paths else "fresh"
    return ArchivedReplayArtifacts(
        run_root=root,
        stage04_root=root / "outputs/04-visual-merge-bundle",
        run_identity_sha256=run["portable_identity_sha256"],
        source_sha256=run["source"]["sha256"],
        bridge_sha256=bridge["bridge_sha256"],
        producer_freshness={"state": state, "changed_paths": changed_paths, "unknown_paths": unknown_paths},
    )
