#!/usr/bin/env python3
"""Apply fully accepted scenario-neutral ArtView v3 decisions to a new projection."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import tempfile
from pathlib import Path
from typing import Any

from kb_creator.scripts import scenario_artview


class ArtViewApplyError(ValueError):
    pass


def _canonical(value: object) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def _read(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(value, dict):
        raise ArtViewApplyError(f"JSON object required: {path}")
    return value


def _write(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + "\n", encoding="utf-8", newline="\n")


def _identity(path: Path, root: Path) -> dict[str, Any]:
    return {"path": path.resolve().relative_to(root.resolve()).as_posix(), "bytes": path.stat().st_size, "sha256": _sha(path)}


def _resolve(root: Path, record: object, label: str) -> Path:
    if not isinstance(record, dict) or set(record) != {"path", "bytes", "sha256"}:
        raise ArtViewApplyError(f"{label} closed identity mismatch")
    relative = scenario_artview.safe_relative(str(record["path"])); path = (root / Path(relative)).resolve()
    try:
        path.relative_to(root.resolve())
    except ValueError as error:
        raise ArtViewApplyError(f"{label} escapes authority root") from error
    if not path.is_file() or path.is_symlink() or path.stat().st_size != record["bytes"] or _sha(path) != record["sha256"]:
        raise ArtViewApplyError(f"{label} identity mismatch")
    return path


def _seal(schema: str, payload: dict[str, Any], key: str) -> dict[str, Any]:
    value = {"schema": schema, **payload}; value[key] = hashlib.sha256(_canonical(value)).hexdigest().upper(); return value


def _validate_seal(value: dict[str, Any], key: str, label: str) -> None:
    digest = value.get(key); unsigned = {name: item for name, item in value.items() if name != key}
    if not isinstance(digest, str) or not re.fullmatch(r"[0-9A-F]{64}", digest) or hashlib.sha256(_canonical(unsigned)).hexdigest().upper() != digest:
        raise ArtViewApplyError(f"{label} seal mismatch")


def apply(profile_path: Path, decisions_path: Path, artview_acceptance_path: Path, output_root: Path, authority_root: Path, candidate_manifest_path: Path | None = None) -> dict[str, Any]:
    raw_output_root = output_root
    profile_path = profile_path.resolve(); decisions_path = decisions_path.resolve(); artview_acceptance_path = artview_acceptance_path.resolve(); authority_root = authority_root.resolve()
    try:
        output_root = scenario_artview._v3_output_root(authority_root, raw_output_root, "ArtView application output", must_exist=False)
    except (ValueError, FileExistsError) as error:
        raise ArtViewApplyError(str(error)) from error
    profile_probe = _read(profile_path)
    validator = scenario_artview.validate_v4_decisions if profile_probe.get("schema") == scenario_artview.PROFILE_SCHEMA_V4 else scenario_artview.validate_v3_decisions
    validation = validator(profile_path, decisions_path, True, candidate_manifest_path, authority_root if candidate_manifest_path is not None else None)
    if validation["status"] != "pass":
        raise ArtViewApplyError(f"ArtView decisions are not accepted and closed: {validation['findings']}")
    profile = profile_probe
    try:
        if candidate_manifest_path is None:
            candidate_root = scenario_artview._v3_output_root(profile_path.parent, f"{profile['output_root']}/candidate", "ArtView v3 candidate", must_exist=True)
            manifest_path = candidate_root / "candidate_manifest.json"
        else:
            manifest_path = scenario_artview._v3_explicit_candidate_manifest(authority_root, candidate_manifest_path)
            candidate_root = manifest_path.parent
    except ValueError as error:
        raise ArtViewApplyError(str(error)) from error
    manifest = _read(manifest_path); decisions = _read(decisions_path)
    acceptance = _read(artview_acceptance_path); _validate_seal(acceptance, "receipt_sha256", "ArtView acceptance")
    if set(acceptance) != {"schema", "scenario_id", "artifact_kind", "candidate", "producer_stage", "evidence", "decision", "decision_at_utc", "user_decision_reference", "recorder_role", "receipt_sha256"} or acceptance["schema"] != "kb_creator.artifact_acceptance.v1" or acceptance["scenario_id"] != profile["scenario_id"] or acceptance["artifact_kind"] != "artview" or acceptance["decision"] != "accepted" or acceptance["recorder_role"] != "main_orchestrator":
        raise ArtViewApplyError("invalid ArtView acceptance")
    if acceptance["candidate"] != _identity(manifest_path, authority_root):
        raise ArtViewApplyError("ArtView acceptance does not bind candidate manifest")
    _resolve(authority_root, acceptance["producer_stage"], "ArtView producer stage")
    decision_identity = _identity(decisions_path, authority_root)
    if not isinstance(acceptance["evidence"], list) or acceptance["evidence"].count(decision_identity) != 1:
        raise ArtViewApplyError("ArtView acceptance does not bind exact decisions")
    for index, record in enumerate(acceptance["evidence"]):
        _resolve(authority_root, record, f"ArtView evidence {index}")
    rows = {row["asset_id"]: row for row in manifest["rows"]}; stage = Path(tempfile.mkdtemp(prefix=f".{output_root.name}.staging.", dir=output_root.parent))
    try:
        projection_rows = []; asset_records = []
        for decision in decisions["decisions"]:
            row = rows[decision["asset_id"]]; choice = decision["binary"]["choice"]; selected = None
            if choice == "keep_current": selected = row["current"]
            elif choice == "use_candidate": selected = next(candidate["binary"] for candidate in row["alternatives"] if candidate["candidate_id"] == decision["binary"]["candidate_id"])
            output_path = None
            if selected is not None:
                source = _resolve(candidate_root, {key: selected[key] for key in ("path", "bytes", "sha256")}, f"selected asset {decision['asset_id']}")
                suffix = source.suffix.lower(); output_path = f"assets/{decision['asset_id']}{suffix}"; target = stage / output_path; target.parent.mkdir(parents=True, exist_ok=True); shutil.copyfile(source, target); asset_records.append(_identity(target, stage))
            projection_rows.append({"asset_id": decision["asset_id"], "anchor": row["anchor"], "status": "excluded" if selected is None else "included", "source_choice": choice, "candidate_id": decision["binary"]["candidate_id"], "output_path": output_path, "presentation": decision["presentation"], **({"review_id": row["review_id"], "placement_id": row["placement_id"], "semantic_role": row["semantic_role"], "placement_target": row["placement_target"], "source_page": row["source_page"], "required": row["required"]} if profile.get("schema") == scenario_artview.PROFILE_SCHEMA_V4 else {})})
        projection = _seal("kb_creator.scenario_artview_reader_projection.v3", {"scenario_id": profile["scenario_id"], "rows": projection_rows}, "projection_sha256"); _write(stage / "reader_projection.json", projection)
        effective = _seal("kb_creator.scenario_artview_effective_visual_config.v3", {"scenario_id": profile["scenario_id"], "decision_bindings": decisions["bindings"], "rows": [{"asset_id": row["asset_id"], "output_path": row["output_path"], "presentation": row["presentation"], **({key: row[key] for key in ("review_id", "placement_id", "semantic_role", "placement_target", "source_page", "required")} if "placement_id" in row else {})} for row in projection_rows if row["status"] == "included"]}, "config_sha256"); _write(stage / "effective_visual_config.json", effective)
        inventory_sha = hashlib.sha256("".join(f"{row['path']}\t{row['bytes']}\t{row['sha256']}\n" for row in sorted(asset_records, key=lambda item: item["path"])).encode("utf-8")).hexdigest().upper()
        applied = _seal("kb_creator.scenario_artview_application.v3", {"scenario_id": profile["scenario_id"], "inputs": {"profile": _identity(profile_path, authority_root), "candidate_manifest": _identity(manifest_path, authority_root), "decisions": decision_identity, "artview_acceptance": _identity(artview_acceptance_path, authority_root)}, "reader_projection": _identity(stage / "reader_projection.json", stage), "effective_visual_config": _identity(stage / "effective_visual_config.json", stage), "assets": sorted(asset_records, key=lambda item: item["path"]), "assets_inventory_sha256": inventory_sha, "counts": {"reviewed": len(projection_rows), "included": sum(row["status"] == "included" for row in projection_rows), "excluded": sum(row["status"] == "excluded" for row in projection_rows)}}, "application_sha256"); _write(stage / "ARTVIEW_APPLIED.json", applied)
        inventory_rows = []
        for path in sorted((item for item in stage.rglob("*") if item.is_file() and item.name != "INVENTORY.json"), key=lambda item: item.relative_to(stage).as_posix()):
            inventory_rows.append(_identity(path, stage))
        _write(stage / "INVENTORY.json", {"schema": "kb_creator.candidate_inventory.v1", "files": inventory_rows, "sha256": hashlib.sha256("".join(f"{row['path']}\t{row['bytes']}\t{row['sha256']}\n" for row in inventory_rows).encode("utf-8")).hexdigest().upper()})
        os.replace(stage, output_root)
        return {"status": "ready_for_html_candidate", "scenario_id": profile["scenario_id"], "application_sha256": applied["application_sha256"], "effective_config_sha256": effective["config_sha256"], "counts": applied["counts"]}
    except Exception:
        shutil.rmtree(stage, ignore_errors=True)
        raise


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__); parser.add_argument("--profile", type=Path, required=True); parser.add_argument("--decisions", type=Path, required=True); parser.add_argument("--artview-acceptance", type=Path, required=True); parser.add_argument("--output-root", type=Path, required=True); parser.add_argument("--authority-root", type=Path, required=True); parser.add_argument("--candidate-manifest", type=Path); args = parser.parse_args()
    try: result = apply(args.profile, args.decisions, args.artview_acceptance, args.output_root, args.authority_root, args.candidate_manifest)
    except Exception as error: print(json.dumps({"status": "fail", "error": f"{type(error).__name__}: {error}"}, ensure_ascii=False), file=__import__("sys").stderr); return 2
    print(json.dumps(result, ensure_ascii=False, sort_keys=True)); return 0


if __name__ == "__main__":
    raise SystemExit(main())
