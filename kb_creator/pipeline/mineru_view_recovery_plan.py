"""Sealed caller input for importing verified views into a fresh Stage 02."""
from __future__ import annotations
import json
from pathlib import Path
from typing import Any
from .identity import canonical_bytes, file_identity, sha256_bytes
from . import reconstruction
from . import mineru_cpu_first

SCHEMA = "kb_creator.mineru_view_recovery_plan.v1"
SOURCE_PROFILE_PLAN_SCHEMA = "kb_creator.mineru_view_recovery_plan.v2"

class RecoveryPlanError(ValueError): pass

def fresh_target(run: dict[str, Any]) -> dict[str, Any]:
    return {key: run[key] for key in ("portable_identity_sha256", "source", "scope", "options", "capability_snapshot", "provider_profiles", "common_tools", "view_plan")}


def load_plan(path: Path, source: Path, fresh_preflight: dict[str, Any] | None = None) -> dict[str, Any]:
    try: data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error: raise RecoveryPlanError("invalid recovery plan") from error
    legacy={"schema","origin_run_root","origin_run","origin_stage_root","source","views","origin_receipts","wrapper_compatibility","plan_sha256"}
    required={"schema","origin_run_root","origin_run","origin_stage_root","fresh_target","source","views","origin_receipts","wrapper_compatibility","source_profile_compatibility","plan_sha256"}
    if not isinstance(data,dict) or (set(data)!=legacy if data.get("schema")==SCHEMA else set(data)!=required) or data.get("schema") not in {SCHEMA,SOURCE_PROFILE_PLAN_SCHEMA}: raise RecoveryPlanError("recovery plan shape")
    unsigned={k:v for k,v in data.items() if k!="plan_sha256"}
    if data["plan_sha256"]!=sha256_bytes(canonical_bytes(unsigned)): raise RecoveryPlanError("recovery plan seal")
    if data["source"] != {"bytes": file_identity(source)["bytes"], "sha256": file_identity(source)["sha256"]}: raise RecoveryPlanError("recovery plan source")
    if not isinstance(data["views"],list) or not data["views"] or len(data["views"])!=len(set(data["views"])) or any(v not in mineru_cpu_first.REQUIRED_VIEWS for v in data["views"]): raise RecoveryPlanError("recovery plan views")
    origin=Path(data["origin_run_root"]).resolve(strict=True); stage=Path(data["origin_stage_root"]).resolve(strict=True)
    if not stage.is_relative_to(origin) or stage.relative_to(origin).as_posix() not in {"outputs/02-mineru-three-view","failures/02-mineru-three-view"}: raise RecoveryPlanError("recovery plan origin stage")
    if data["origin_run"] != {"path":"run.json",**file_identity(origin/"run.json")}: raise RecoveryPlanError("recovery plan origin run identity")
    try: run=reconstruction.load_run(origin)
    except Exception as error: raise RecoveryPlanError("recovery plan origin run") from error
    if Path(str(run["local"]["run_root"])).resolve() != origin: raise RecoveryPlanError("recovery plan origin root binding")
    if data["schema"] == SCHEMA:
        fresh = None
    else:
      if not isinstance(data["fresh_target"], dict): raise RecoveryPlanError("recovery plan fresh target")
      if fresh_preflight is not None and data["fresh_target"] != fresh_target(fresh_preflight): raise RecoveryPlanError("recovery plan fresh preflight target")
    if not isinstance(data["origin_receipts"],dict) or set(data["origin_receipts"]) != set(data["views"]): raise RecoveryPlanError("recovery plan receipt set")
    if not isinstance(data["wrapper_compatibility"],dict) or not set(data["wrapper_compatibility"]).issubset(set(data["views"])): raise RecoveryPlanError("recovery plan wrapper compatibility")
    if data["schema"] != SCHEMA and (not isinstance(data["source_profile_compatibility"],dict) or set(data["source_profile_compatibility"]) != set(data["views"])): raise RecoveryPlanError("recovery plan source profile compatibility")
    for view_id in data["views"]:
        descriptor=next(row for row in mineru_cpu_first.VIEW_PLAN if row["view_id"]==view_id)
        receipt=stage/"views"/view_id/"view.json"
        try: value=mineru_cpu_first.validate_view_receipt(run,descriptor,receipt,stage)
        except Exception as error: raise RecoveryPlanError("recovery plan origin receipt") from error
        if value["state"]!="succeeded" or data["origin_receipts"][view_id] != {"path":f"views/{view_id}/view.json",**file_identity(receipt),"receipt_sha256":value["receipt_sha256"]}: raise RecoveryPlanError("recovery plan receipt identity")
    result={**data,"origin_run_root":str(origin),"origin_stage_root":str(stage),"origin_run":run}
    return result


def validate_fresh_target(plan: dict[str, Any], run: dict[str, Any]) -> None:
    if plan.get("schema") == SOURCE_PROFILE_PLAN_SCHEMA and plan.get("fresh_target") != fresh_target(run):
        raise RecoveryPlanError("recovery plan fresh target does not match created run")
