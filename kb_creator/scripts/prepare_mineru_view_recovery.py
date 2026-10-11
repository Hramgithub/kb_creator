"""Prepare a sealed MinerU view recovery plan from an inspected origin run."""

from __future__ import annotations

import argparse
import json
import os
import sys
import tempfile
from pathlib import Path
from typing import Any, Mapping, Sequence

from kb_creator.pipeline.identity import canonical_bytes, file_identity, sha256_bytes
from kb_creator.pipeline.mineru_view_recovery_plan import SCHEMA, SOURCE_PROFILE_PLAN_SCHEMA, load_plan
from kb_creator.pipeline import mineru_cpu_first, reconstruction, mineru_view_recovery


def _origin_stage(root: Path, stage: str) -> Path:
    if stage not in {"outputs", "failures"}:
        raise ValueError("origin stage must be outputs or failures")
    return root / stage / "02-mineru-three-view"


def _selected_receipts(
    run: Mapping[str, Any], stage_root: Path, views: Sequence[str]
) -> dict[str, dict[str, Any]]:
    descriptors = {row["view_id"]: row for row in mineru_cpu_first.VIEW_PLAN}
    receipts: dict[str, dict[str, Any]] = {}
    for view_id in views:
        if view_id not in descriptors:
            raise ValueError(f"invalid view: {view_id}")
        receipt = stage_root / "views" / view_id / "view.json"
        try:
            value = mineru_cpu_first.validate_view_receipt(
                run, descriptors[view_id], receipt, stage_root
            )
        except Exception as error:
            raise ValueError(f"selected view receipt is invalid: {view_id}") from error
        if value.get("state") != "succeeded":
            raise ValueError(f"selected view did not succeed: {view_id}")
        receipts[view_id] = {
            "path": f"views/{view_id}/view.json",
            **file_identity(receipt),
            "receipt_sha256": value["receipt_sha256"],
        }
    return receipts


def prepare_plan(
    *,
    origin_run: Path,
    origin_stage: str,
    source: Path,
    views: Sequence[str],
    output: Path,
    fresh_run: Path | None = None,
    fresh_preflight: Mapping[str, Any] | None = None,
    wrapper_compatibility: Mapping[str, Any] | None = None,
    source_profile_compatibility: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Build, seal, validate, and atomically publish one previously absent plan."""
    origin = origin_run.resolve(strict=True)
    source_path = source.resolve(strict=True)
    destination = output.resolve()
    if destination.exists():
        raise FileExistsError(f"refusing existing output: {destination}")
    if not views or len(views) != len(set(views)):
        raise ValueError("views must be nonempty and unique")
    if wrapper_compatibility is None:
        wrapper_records: dict[str, Any] = {}
    elif isinstance(wrapper_compatibility, dict):
        wrapper_records = wrapper_compatibility
    else:
        raise ValueError("wrapper compatibility must be a JSON object")
    stage_root = _origin_stage(origin, origin_stage).resolve(strict=True)
    run = reconstruction.load_run(origin)
    fresh = None
    fresh_root = None
    if fresh_run is not None and fresh_preflight is not None:
        raise ValueError("choose either fresh run or fresh preflight")
    if fresh_run is not None:
        fresh_root = fresh_run.resolve(strict=True)
        fresh = reconstruction.load_run(fresh_root)
        reconstruction._validate_live_run_bindings(fresh_root, fresh)
    elif fresh_preflight is not None:
        fresh = dict(fresh_preflight)
        from kb_creator.pipeline.mineru_view_recovery_plan import fresh_target
        if not fresh.get("local") or not fresh_target(fresh).get("portable_identity_sha256"):
            raise ValueError("fresh preflight is malformed")
    source_identity = file_identity(source_path)
    if {key: run["source"].get(key) for key in ("bytes", "sha256")} != source_identity:
        raise ValueError("source does not match origin run")
    receipts = _selected_receipts(run, stage_root, views)
    source_records = source_profile_compatibility or ({
        view_id: mineru_view_recovery.source_profile_compatibility_from_runs(run, fresh, view_id)
        for view_id in views
    } if fresh is not None else {})
    if fresh is not None and set(source_records) != set(views):
        raise ValueError("source profile compatibility must cover every selected view")
    for view_id in views if fresh is not None else ():
        mineru_view_recovery._validate_source_profile_compatibility(
            run, fresh, next(row for row in mineru_cpu_first.VIEW_PLAN if row["view_id"] == view_id), source_records[view_id]
        )
    unsigned: dict[str, Any] = {
        "schema": SOURCE_PROFILE_PLAN_SCHEMA if fresh is not None else SCHEMA,
        "origin_run_root": str(origin),
        "origin_run": {"path": "run.json", **file_identity(origin / "run.json")},
        "origin_stage_root": str(stage_root),
        "source": source_identity,
        "views": list(views),
        "origin_receipts": receipts,
        "wrapper_compatibility": wrapper_records,
    }
    if fresh is not None:
        from kb_creator.pipeline.mineru_view_recovery_plan import fresh_target
        unsigned.update(fresh_target=fresh_target(fresh),source_profile_compatibility=source_records)
    plan = {**unsigned, "plan_sha256": sha256_bytes(canonical_bytes(unsigned))}
    destination.parent.mkdir(parents=True, exist_ok=True)
    temporary_handle = tempfile.NamedTemporaryFile(
        mode="w", encoding="utf-8", suffix=".tmp", prefix=f".{destination.name}.",
        dir=destination.parent, delete=False,
    )
    temporary = Path(temporary_handle.name)
    try:
        temporary_handle.write(json.dumps(plan, ensure_ascii=False, indent=2) + "\n")
        temporary_handle.close()
        load_plan(temporary, source_path)
        # A hard link is the portable same-filesystem no-replace publication primitive.
        # os.replace would overwrite a destination created while validation was running.
        os.link(temporary, destination)
        temporary.unlink()
    except Exception:
        if not temporary_handle.closed:
            temporary_handle.close()
        temporary.unlink(missing_ok=True)
        raise
    return plan


def _compatibility(path: Path | None, label: str) -> dict[str, Any]:
    if path is None:
        return {}
    value = json.loads(path.resolve(strict=True).read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{label} JSON must be an object")
    return value


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--origin-run", required=True, type=Path)
    parser.add_argument("--origin-stage", required=True, choices=("outputs", "failures"))
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--fresh-run", type=Path)
    group.add_argument("--fresh-preflight", type=Path)
    parser.add_argument("--source", required=True, type=Path)
    parser.add_argument("--view", action="append", required=True)
    parser.add_argument("--wrapper-compatibility", type=Path)
    parser.add_argument("--source-profile-compatibility", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args(argv)
    try:
        plan = prepare_plan(
            origin_run=args.origin_run,
            origin_stage=args.origin_stage,
            fresh_run=args.fresh_run,
            fresh_preflight=(json.loads(args.fresh_preflight.read_text(encoding="utf-8")) if args.fresh_preflight else None),
            source=args.source,
            views=args.view,
            output=args.output,
            wrapper_compatibility=_compatibility(args.wrapper_compatibility, "wrapper compatibility"),
            source_profile_compatibility=_compatibility(args.source_profile_compatibility, "source profile compatibility"),
        )
    except Exception as error:
        print(f"prepare_mineru_view_recovery: {error}", file=sys.stderr)
        return 2
    print(json.dumps({"status": "ok", "output": str(args.output.resolve()), "plan_sha256": plan["plan_sha256"]}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
