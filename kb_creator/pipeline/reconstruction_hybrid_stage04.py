"""Fresh Stage 04 execution over a replayed CPU-first Stage 01--03 prefix.

This module deliberately sits outside the Stage 01--03 producer closure.  It
uses the normal Stage 04 adapter and manifest writer, but validates the
replayed v2 view-set/v3 comparison authority before publishing its output.
"""
from __future__ import annotations

import copy
import json
import shutil
from pathlib import Path
from typing import Any, Mapping, Sequence

from kb_creator.pipeline import process as pipeline_process
from kb_creator.pipeline import reconstruction
from kb_creator.pipeline.identity import canonical_bytes, deterministic_inventory, file_identity, sha256_bytes
from kb_creator.pipeline.manifests import is_sha256
from kb_creator.scripts import build_mineru_visual_merge_bundle as bundle


class HybridStage04Error(reconstruction.ControlPlaneError):
    """The mixed replay/executed Stage 04 authority is invalid."""


_NAME = "visual_merge_bundle"
_ORDINAL = 4


def _paths(run_root: Path) -> tuple[Path, Path, Path]:
    return (
        run_root / "outputs/01-prepare-inputs/prepared/sample_pages.json",
        run_root / "outputs/02-mineru-three-view/view-set.json",
        run_root / "outputs/03-compare-views/comparison.json",
    )


def _inputs(run: dict[str, Any]) -> list[dict[str, Any]]:
    return reconstruction._base_stage_inputs(_NAME, run)


def _validate_live_bindings(run_root: Path, run: dict[str, Any]) -> None:
    """Validate replay-owned implementation identity plus native runtime bindings."""
    # Import lazily to avoid a reconstruction_replay -> this module import
    # cycle.  The fresh run intentionally has a larger implementation
    # inventory than the native producer validator expects.
    from kb_creator.pipeline import reconstruction_replay as replay

    if run.get("implementation") != replay._replay_inventory():
        raise HybridStage04Error("stale replay implementation binding")
    native = copy.deepcopy(run)
    native["implementation"] = reconstruction.implementation_inventory(
        reconstruction._repo_root(), reconstruction._implementation_paths(),
    )
    reconstruction._validate_live_run_bindings(run_root, native)


def _validate_archived_bindings(run_root: Path, run: dict[str, Any]) -> None:
    """Check the immutable inputs of a sealed Stage 04 without executable freshness."""
    try:
        loaded = reconstruction.load_run(run_root)
        if loaded != run:
            raise HybridStage04Error("archived run record mismatch")
        if Path(str(run["local"]["run_root"])).resolve() != run_root.resolve():
            raise HybridStage04Error("archived run root binding mismatch")
        contract, contract_sha = reconstruction.load_contract(Path(str(run["local"]["contract_path"])))
        if contract_sha != run["contract"]["sha256"] or contract.get("contract_revision") != run["contract"].get("contract_revision"):
            raise HybridStage04Error("archived contract binding mismatch")
        source = Path(str(run["local"]["source_path"]))
        if file_identity(source) != {"bytes": run["source"]["bytes"], "sha256": run["source"]["sha256"]}:
            raise HybridStage04Error("archived source binding mismatch")
        implementation = run.get("implementation", {})
        files = implementation.get("files") if isinstance(implementation, dict) else None
        if not isinstance(files, list) or implementation.get("inventory_sha256") != sha256_bytes(canonical_bytes(files)):
            raise HybridStage04Error("archived implementation inventory mismatch")
        # These identities are sealed in run.json.  Reading an archive must not
        # require that the executable or provider installation still exists.
        for key in ("capability_snapshot", "provider_profiles", "common_tools"):
            if not isinstance(run.get(key), dict):
                raise HybridStage04Error(f"archived {key} binding missing")
    except HybridStage04Error:
        raise
    except (KeyError, OSError, ValueError, json.JSONDecodeError, reconstruction.ControlPlaneError) as error:
        raise HybridStage04Error(f"archived binding validation failed: {error}") from error


def _validate_output(run_root: Path, run: dict[str, Any], output: Path, *, archived: bool = False) -> None:
    prepared, view_set, comparison = _paths(run_root)
    source = Path(str(run["local"]["source_path"]))
    if not all(path.is_file() for path in (prepared, view_set, comparison, source)):
        raise HybridStage04Error("hybrid Stage 04 lacks sealed replay inputs")
    try:
        expected_inputs, comparison_data = bundle._load_inputs(
            view_set, bundle.sha256_file(view_set), source, run["source"]["sha256"],
            comparison, bundle.sha256_file(comparison), view_set.parent,
            int(run["options"]["review_dpi"]), prepared, bundle.sha256_file(prepared),
        )
        contract_path = Path(str(run["local"]["contract_path"])).resolve()
        expected_inputs["reconstruction_contract"] = {
            "path": str(contract_path), "sha256": bundle.sha256_file(contract_path),
        }
        # The v3 branch validates typed relative references, their containment,
        # source/preparation hashes, fresh identity and view coverage.  Keep the
        # check explicit: this executor must never route through the legacy CPU
        # validator, which only understands source producer wrappers.
        if comparison_data.get("schema") != "kb_creator.mineru_multi_view_comparison.v3":
            raise HybridStage04Error("hybrid Stage 04 requires replay comparison v3")
        if comparison_data.get("run_identity_sha256") != run["portable_identity_sha256"]:
            raise HybridStage04Error("hybrid comparison run identity mismatch")
        manifest_path = output / "visual/visual_manifest.json"
        if not manifest_path.is_file():
            raise HybridStage04Error("hybrid Stage 04 lacks visual manifest")
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        bundle.validate_v2_bundle(output, manifest, expected_inputs=expected_inputs)
        plan = json.loads((output / "visual/geometry_plan.json").read_text(encoding="utf-8"))
        if (
            plan.get("run_identity_sha256") != run["portable_identity_sha256"]
            or plan.get("policy") != run["options"]["geometry_policy"]
            or plan.get("review_dpi") != run["options"]["review_dpi"]
            or plan.get("rounding_rule") != run["options"]["geometry_rounding_rule"]
            or plan.get("tolerances") != {
                "dimension_points": run["options"]["geometry_dimension_tolerance_points"],
                "relative_aspect_ratio": run["options"]["geometry_relative_aspect_tolerance"],
                "pixels": run["options"]["geometry_pixel_tolerance"],
            }
            or plan.get("renderer", {}).get("argv_recipe") != run["options"]["geometry_renderer_recipe"]
            or plan.get("succeeded_views") != comparison_data.get("succeeded_views")
            or plan.get("preparation_manifest") != {
                "path_hint": "outputs/01-prepare-inputs/prepared/sample_pages.json", **file_identity(prepared),
            }
        ):
            raise HybridStage04Error("hybrid Stage 04 geometry authority mismatch")
        renderer_sha256 = run["common_tools"]["pdftoppm"]["sha256"] if archived else file_identity(Path(str(run["local"]["common_paths"]["pdftoppm"]))) ["sha256"]
        if str(plan.get("renderer", {}).get("sha256", "")).upper() != str(renderer_sha256).upper():
            raise HybridStage04Error("hybrid Stage 04 renderer identity mismatch")
        layouts = {
            view: bundle.find_layout_pdf(view_set.parent, view, cpu_first=True)
            for view in comparison_data["succeeded_views"]
        }
        recomputed = bundle.build_geometry_plan(
            prepared_manifest=json.loads(prepared.read_text(encoding="utf-8")),
            prepared_identity={"path_hint": "outputs/01-prepare-inputs/prepared/sample_pages.json", **file_identity(prepared)},
            layouts=layouts, views=tuple(comparison_data["succeeded_views"]),
            dpi=run["options"]["review_dpi"], renderer=plan["renderer"],
            run_identity_sha256=run["portable_identity_sha256"],
            source_identity={"path_hint": source.name, **file_identity(source)},
            comparison_identity={"path_hint": "outputs/03-compare-views/comparison.json", **file_identity(comparison)},
            view_set_identity={"path_hint": "outputs/02-mineru-three-view/view-set.json", **file_identity(view_set), "receipt_sha256": json.loads(view_set.read_text(encoding="utf-8"))["receipt_sha256"]},
        )
        observed_base = {key: value for key, value in plan.items() if key not in {"rendered_pages", "plan_sha256"}}
        recomputed_base = {key: value for key, value in recomputed.items() if key not in {"rendered_pages", "plan_sha256"}}
        if observed_base != recomputed_base:
            raise HybridStage04Error("hybrid Stage 04 geometry plan is stale")
        if [row.get("source_page") for row in plan.get("targets", [])] != list(run["scope"]["ordered_pages"]):
            raise HybridStage04Error("hybrid Stage 04 geometry page coverage mismatch")
        contract = json.loads(contract_path.read_text(encoding="utf-8"))
        roles = tuple((row["first_page"], row["last_page"], row["role"]) for row in contract["page_roles"])
        expected_pages = list(run["scope"]["ordered_pages"])
        packet_dir = output / "merge_packets/pages"
        expected_packet_names = {
            f"page-{page:03d}.{suffix}" for page in expected_pages for suffix in ("json", "md")
        }
        if not packet_dir.is_dir() or {path.name for path in packet_dir.iterdir() if path.is_file()} != expected_packet_names:
            raise HybridStage04Error("hybrid Stage 04 packet coverage mismatch")
        for page in expected_pages:
            packet_path = output / "merge_packets/pages" / f"page-{page:03d}.json"
            packet = json.loads(packet_path.read_text(encoding="utf-8"))
            expected_views = {
                view_id: bundle._page_view(comparison_data["views"][view_id], page)
                for view_id in comparison_data["succeeded_views"]
            }
            expected = {
                "schema": "kb_creator.mineru_merge_packet.v1",
                "source_page": page,
                "semantic_role": bundle.role_for_page(page, roles),
                "views": expected_views,
                "pairwise": bundle._packet_pairwise(comparison_data["pairwise"], comparison_data["views"], page),
                "review_signals": bundle.review_signals(expected_views, bundle.CPU_TRIPTYCH),
            }
            if packet != expected:
                raise HybridStage04Error(f"hybrid Stage 04 merge packet mismatch: {page}")
    except HybridStage04Error:
        raise
    except (KeyError, OSError, ValueError, json.JSONDecodeError) as error:
        raise HybridStage04Error(f"hybrid Stage 04 output validation failed: {error}") from error


def invoke_stage04(
    run_root: Path, run: dict[str, Any], upstream: Sequence[dict[str, str]],
    adapter: reconstruction.StageAdapter,
) -> dict[str, str]:
    """Invoke Stage 04 once in an owned transaction and retain failure evidence."""
    if adapter.name != _NAME:
        raise HybridStage04Error("wrong adapter for hybrid Stage 04")
    output = reconstruction._stage_output_path(run_root, _ORDINAL, _NAME)
    stage_id = reconstruction._stage_id(_ORDINAL, _NAME)
    staging = run_root / "local/staging" / stage_id
    failure = run_root / "failures" / stage_id
    if output.exists() or staging.exists() or failure.exists():
        raise HybridStage04Error(f"hybrid Stage 04 attempt path already exists: {stage_id}")
    output.parent.mkdir(parents=True, exist_ok=True)
    staging.parent.mkdir(parents=True, exist_ok=True)
    started_at = reconstruction._utc_now()
    try:
        _validate_live_bindings(run_root, run)
        diagnostics = dict(adapter.invoke(staging))
        _validate_output(run_root, run, staging)
        deterministic_inventory(staging)
        staging.replace(output)
        manifest = reconstruction._write_stage(
            run_root, _ORDINAL, _NAME, run, list(upstream), output,
            diagnostics, started_at, _inputs(run),
        )
    except Exception as error:
        # A manifest write may fail after output publication.  Quarantine the
        # actual output in that case, retaining its diagnostics and payload.
        failed = output if output.exists() else staging
        failed.mkdir(parents=True, exist_ok=True)
        if isinstance(error, pipeline_process.ProcessFailure):
            receipt = reconstruction.sealed(
                "kb_creator.stage_failure.v1",
                {
                    "stage_id": stage_id, "stage_name": _NAME,
                    "run_identity_sha256": run["portable_identity_sha256"],
                    "failure_kind": "child_process_nonzero", "profile": None,
                    "argv": list(error.argv), "environment": error.environment,
                    "exit_code": error.returncode, "stdout": error.stdout,
                    "stderr": error.stderr, "stdout_truncated": error.stdout_truncated,
                    "stderr_truncated": error.stderr_truncated,
                }, digest_key="failure_sha256",
            )
            reconstruction._write_json(failed / "stage-failure.json", receipt)
        elif not (failed / "stage-failure.json").exists():
            reconstruction._write_json(failed / "stage-failure.json", {
                "schema": "kb_creator.hybrid_stage04_failure.v1",
                "stage_id": stage_id, "stage_name": _NAME,
                "run_identity_sha256": run.get("portable_identity_sha256"),
                "failure_kind": "validation_or_adapter_failure", "message": str(error),
            })
        if failed.exists():
            failure.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(failed), str(failure))
        manifest_parent = reconstruction._stage_manifest_path(run_root, _ORDINAL, _NAME).parent
        if manifest_parent.exists():
            shutil.rmtree(manifest_parent)
        raise HybridStage04Error(f"hybrid Stage 04 failed: {error}") from error
    return {"stage_id": manifest["reproducible"]["stage_id"], "manifest_sha256": manifest["reproducible_sha256"]}


def _validate_stage04(
    run_root: Path, run: dict[str, Any], upstream: Sequence[dict[str, str]],
    *, archived: bool,
) -> dict[str, str]:
    """Validate the complete v1 direct Stage 04 manifest and replay-aware output."""
    path = reconstruction._stage_manifest_path(run_root, _ORDINAL, _NAME)
    data = reconstruction._read(path)
    reconstruction._require_exact_keys(data, {"schema", "reproducible", "execution", "reproducible_sha256"}, "hybrid Stage 04 manifest")
    reproducible = data.get("reproducible")
    execution = data.get("execution")
    if data.get("schema") != reconstruction.STAGE_SCHEMA or not isinstance(reproducible, dict) or not isinstance(execution, dict):
        raise HybridStage04Error("hybrid Stage 04 manifest shape mismatch")
    expected_keys = {"stage_id", "stage_name", "stage_version", "state", "run_identity_sha256", "upstream", "inputs", "options", "adapter", "tools", "implementation_inventory_sha256", "outputs", "evidence", "cache_key"}
    reconstruction._require_exact_keys(reproducible, expected_keys, "hybrid Stage 04 reproducible record")
    reconstruction._require_exact_keys(execution, {"started_at_utc", "completed_at_utc", "exit_code", "structured_diagnostics"}, "hybrid Stage 04 execution")
    adapter = {"logical_name": _NAME, "script_sha256": reconstruction._implementation_record(run, reconstruction.STAGE_SCRIPTS[_NAME])["sha256"], "argv_shape_version": 1}
    expected_cache = sha256_bytes(canonical_bytes({"stage_id": reconstruction._stage_id(_ORDINAL, _NAME), "stage_version": 1, "run_identity_sha256": run["portable_identity_sha256"], "upstream": list(upstream), "inputs": _inputs(run), "options": run["options"], "adapter": adapter, "tools": run["toolchain"], "implementation_inventory_sha256": run["implementation"]["inventory_sha256"]}))
    if (
        not is_sha256(data.get("reproducible_sha256"))
        or sha256_bytes(canonical_bytes(reproducible)) != data["reproducible_sha256"]
        or reproducible.get("stage_id") != reconstruction._stage_id(_ORDINAL, _NAME)
        or reproducible.get("stage_name") != _NAME or reproducible.get("stage_version") != 1
        or reproducible.get("state") != "succeeded" or reproducible.get("run_identity_sha256") != run["portable_identity_sha256"]
        or reproducible.get("upstream") != list(upstream) or reproducible.get("inputs") != _inputs(run)
        or reproducible.get("options") != run["options"] or reproducible.get("adapter") != adapter
        or reproducible.get("tools") != run["toolchain"] or reproducible.get("implementation_inventory_sha256") != run["implementation"]["inventory_sha256"]
        or reproducible.get("cache_key") != expected_cache or execution.get("exit_code") != 0
        or not isinstance(execution.get("structured_diagnostics"), dict)
    ):
        raise HybridStage04Error("hybrid Stage 04 manifest authority mismatch")
    output = reconstruction._stage_output_path(run_root, _ORDINAL, _NAME)
    outputs = reproducible.get("outputs")
    if not isinstance(outputs, dict):
        raise HybridStage04Error("hybrid Stage 04 output inventory missing")
    reconstruction._require_exact_keys(outputs, {"root_hint", "files", "inventory_sha256"}, "hybrid Stage 04 output inventory")
    observed = deterministic_inventory(output)
    if (
        outputs.get("root_hint") != output.relative_to(run_root).as_posix()
        or outputs.get("files") != observed
        or outputs.get("inventory_sha256") != sha256_bytes(canonical_bytes(observed))
    ):
        raise HybridStage04Error("hybrid Stage 04 output inventory mismatch")
    if archived:
        _validate_output(run_root, run, output, archived=True)
    else:
        _validate_output(run_root, run, output)
    return {"stage_id": reconstruction._stage_id(_ORDINAL, _NAME), "manifest_sha256": data["reproducible_sha256"]}


def validate_stage04_current(
    run_root: Path, run: dict[str, Any], upstream: Sequence[dict[str, str]],
) -> dict[str, str]:
    """Validate Stage 04 for current execution or resume authority."""
    _validate_live_bindings(run_root, run)
    return _validate_stage04(run_root, run, upstream, archived=False)


def validate_stage04_artifacts(
    run_root: Path, run: dict[str, Any], upstream: Sequence[dict[str, str]],
) -> dict[str, str]:
    """Validate a sealed historical Stage 04 for read-only consumption."""
    _validate_archived_bindings(run_root, run)
    return _validate_stage04(run_root, run, upstream, archived=True)


def validate_stage04(
    run_root: Path, run: dict[str, Any], upstream: Sequence[dict[str, str]],
) -> dict[str, str]:
    """Compatibility alias retaining the strict current-authority behavior."""
    return validate_stage04_current(run_root, run, upstream)
