#!/usr/bin/env python3
"""Offline standard-library verifier for a frozen neutral publication package."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import stat
import sys
from html.parser import HTMLParser
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit


MANIFEST = "PRODUCTION_MANIFEST.json"
PACKAGE_SCHEMA = "kb_creator.production_package_manifest.v1"
STAGE_SCHEMA = "kb_creator.publication_stage_manifest.v1"
ACCEPTANCE_SCHEMA = "kb_creator.artifact_acceptance.v1"
DECISIONS_SCHEMAS = {
    "kb_creator.scenario_artview_decisions.v3",
    "kb_creator.scenario_artview_decisions.v4",
}
STAGES = (
    ("10-master-en-candidate", "master_en_candidate", "master_en_projection_v3"),
    ("20-master-ru-packets", "master_ru_packets", "master_ru_packets_v1"),
    ("21-master-ru-candidate", "master_ru_candidate", "master_ru_assembly_v1"),
    ("30-artview-bundle", "artview_bundle", "scenario_artview_v3"),
    ("31-artview-apply", "artview_apply", "scenario_artview_apply_v1"),
    ("40-html-candidate", "html_candidate", "translator_build_production_html_v1"),
    ("50-docx-candidate", "docx_candidate", "production_docx_reviewed_authority_v2"),
    ("60-pdf-candidate", "pdf_candidate", "docx_pdf_export_v1"),
)
ACCEPTANCE_KINDS = ("master_en", "master_ru", "artview", "html", "docx", "pdf")
MANDATORY_ROLES = {
    "master_en", "master_en_acceptance", "master_ru", "master_ru_acceptance",
    "artview_bundle", "artview_candidate_manifest", "artview_decisions",
    "artview_application", "artview_effective_config", "artview_acceptance",
    "html", "html_acceptance", "docx", "docx_acceptance", "pdf",
    "pdf_acceptance", "source_configs", "effective_config", "stage_evidence",
    "pipeline_snapshot", "schema_snapshot", "offline_verifier",
}


class VerificationError(ValueError):
    pass


class _Refs(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.values: list[str] = []

    def handle_starttag(self, _tag: str, attrs: list[tuple[str, str | None]]) -> None:
        for key, value in attrs:
            if key.lower() in {"src", "href"} and value:
                self.values.append(value)


def canonical(value: object) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


def sha(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def identity(path: Path, root: Path) -> dict[str, Any]:
    return {"path": path.relative_to(root).as_posix(), "bytes": path.stat().st_size, "sha256": sha(path)}


def exact(value: object, keys: set[str], label: str) -> dict[str, Any]:
    if not isinstance(value, dict) or set(value) != keys:
        raise VerificationError(f"{label} closed shape mismatch")
    return value


def read_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8-sig"))
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        raise VerificationError(f"cannot read JSON {path.name}: {error}") from error
    if not isinstance(value, dict):
        raise VerificationError(f"JSON object required: {path.name}")
    return value


def validate_seal(value: dict[str, Any], key: str, label: str) -> None:
    digest = value.get(key)
    if not isinstance(digest, str) or not re.fullmatch(r"[0-9A-F]{64}", digest):
        raise VerificationError(f"{label} seal missing")
    if hashlib.sha256(canonical({name: item for name, item in value.items() if name != key})).hexdigest().upper() != digest:
        raise VerificationError(f"{label} seal mismatch")


def is_reparse(path: Path) -> bool:
    try:
        metadata = os.lstat(path)
    except OSError:
        return False
    return stat.S_ISLNK(metadata.st_mode) or bool(getattr(metadata, "st_file_attributes", 0) & getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0x400))


def safe_relative(value: object, label: str) -> Path:
    if not isinstance(value, str) or not value or "\\" in value or ":" in value:
        raise VerificationError(f"unsafe {label} path")
    path = Path(value)
    if path.is_absolute() or any(part in {"", ".", ".."} for part in path.parts):
        raise VerificationError(f"unsafe {label} path")
    return path


def resolve(root: Path, record: object, label: str) -> Path:
    row = exact(record, {"path", "bytes", "sha256"}, label)
    relative = safe_relative(row["path"], label)
    path = root / relative
    current = path
    while True:
        if is_reparse(current):
            raise VerificationError(f"{label} contains reparse content")
        if current == root:
            break
        current = current.parent
    if not path.is_file() or isinstance(row["bytes"], bool) or not isinstance(row["bytes"], int) or row["bytes"] < 1 or path.stat().st_size != row["bytes"] or not re.fullmatch(r"[0-9A-F]{64}", str(row["sha256"])) or sha(path) != row["sha256"]:
        raise VerificationError(f"{label} identity mismatch")
    return path


def inventory(root: Path) -> list[dict[str, Any]]:
    rows = []
    # Match the production inventory builder exactly.  pathlib's native ordering
    # is part of that v1 contract (not a case-sensitive POSIX re-sort).
    for path in sorted(root.rglob("*")):
        if is_reparse(path):
            raise VerificationError("package contains reparse content")
        if path.is_file() and path.name != MANIFEST:
            rows.append(identity(path, root))
    return rows


def validate_html_local_references(html_path: Path, package_root: Path) -> int:
    parser = _Refs()
    parser.feed(html_path.read_text(encoding="utf-8"))
    count = 0
    for value in parser.values:
        parts = urlsplit(value)
        if parts.scheme or parts.netloc or value.startswith(("#", "data:")) or not parts.path:
            continue
        relative = safe_relative(parts.path, f"HTML local reference {value}")
        path = html_path.parent / relative
        cursor = path
        while True:
            if not cursor.exists() or is_reparse(cursor):
                raise VerificationError(f"HTML local reference is missing or unsafe: {value}")
            if cursor == package_root:
                break
            if package_root not in cursor.parents:
                raise VerificationError(f"HTML local reference escapes package: {value}")
            cursor = cursor.parent
        if not path.is_file():
            raise VerificationError(f"HTML local reference is not a file: {value}")
        count += 1
    return count


def validate_decisions(path: Path, scenario_id: str) -> None:
    value = read_json(path)
    exact(value, {"schema", "scenario_id", "state", "bindings", "decisions", "review", "decisions_sha256"}, "ArtView decisions")
    validate_seal(value, "decisions_sha256", "ArtView decisions")
    if value["schema"] not in DECISIONS_SCHEMAS or value["scenario_id"] != scenario_id or value["state"] != "accepted":
        raise VerificationError("ArtView decisions are not accepted")
    rows = value["decisions"]
    if not isinstance(rows, list) or not rows:
        raise VerificationError("ArtView decisions are empty")
    ids = []
    for row in rows:
        exact(row, {"asset_id", "binary", "presentation", "reviewed", "notes"}, "ArtView decision row")
        if not isinstance(row["asset_id"], str) or not row["asset_id"] or row["asset_id"] in ids or row["reviewed"] is not True or row["binary"].get("choice") not in {"keep_current", "use_candidate", "exclude"}:
            raise VerificationError("ArtView decision row is incomplete")
        ids.append(row["asset_id"])
    if value["review"] != {"state": "closed", "reviewed_count": len(rows), "unresolved_asset_ids": []}:
        raise VerificationError("ArtView review is not closed")


def verify_package(package_root: Path) -> dict[str, Any]:
    package_root = package_root.resolve(strict=True)
    if not package_root.is_dir() or is_reparse(package_root):
        raise VerificationError("package root must be a regular directory")
    manifest_path = package_root / MANIFEST
    manifest = read_json(manifest_path)
    exact(manifest, {"schema", "scenario_id", "package_state", "release_state", "publication_run_identity_sha256", "roles", "inventory", "stage_manifests", "acceptance_receipts", "config_inventory", "pipeline_snapshot", "upstream", "manifest_sha256"}, "production manifest")
    validate_seal(manifest, "manifest_sha256", "production manifest")
    if manifest["schema"] != PACKAGE_SCHEMA or manifest["package_state"] != "candidate_for_release_review" or manifest["release_state"] != "not_reviewed":
        raise VerificationError("package cannot claim acceptance or release")
    observed = inventory(package_root)
    if manifest["inventory"] != observed:
        raise VerificationError("package inventory mismatch")
    pdfs = [row for row in observed if row["path"].lower().endswith(".pdf")]
    if len(pdfs) != 1:
        raise VerificationError("package must contain exactly one PDF")
    roles = manifest["roles"]
    if not isinstance(roles, list):
        raise VerificationError("package roles must be a list")
    names = []
    paths = []
    role_map: dict[str, Path] = {}
    for row in roles:
        exact(row, {"role", "path"}, "package role")
        relative = safe_relative(row["path"], f"role {row['role']}")
        path = package_root / relative
        if not path.exists() or is_reparse(path):
            raise VerificationError(f"package role missing: {row['role']}")
        names.append(row["role"]); paths.append(row["path"]); role_map[row["role"]] = path
    if len(names) != len(set(names)) or len(paths) != len(set(paths)) or not MANDATORY_ROLES.issubset(names):
        raise VerificationError("package roles are incomplete or duplicated")
    if identity(role_map["pdf"], package_root) != pdfs[0]:
        raise VerificationError("sole package PDF role mismatch")
    html_local_reference_count = validate_html_local_references(role_map["html"], package_root)
    validate_decisions(role_map["artview_decisions"], manifest["scenario_id"])
    stage_records = manifest["stage_manifests"]
    if not isinstance(stage_records, list) or len(stage_records) != len(STAGES) or len({canonical(row) for row in stage_records}) != len(STAGES):
        raise VerificationError("package requires exact eight stage manifests")
    stages = []
    upstream = []
    continuity: tuple[bytes, bytes, bytes, object, bytes] | None = None
    for index, (stage_id, stage_name, adapter_name) in enumerate(STAGES):
        stage_path = resolve(package_root, stage_records[index], f"stage {stage_id}")
        stage = read_json(stage_path)
        exact(stage, {"schema", "reproducible", "execution", "reproducible_sha256"}, "stage manifest")
        reproducible = exact(stage["reproducible"], {"stage_id", "stage_name", "stage_version", "state", "run_identity_sha256", "upstream", "inputs", "adapter", "effective_config", "tools", "implementation_inventory_sha256", "outputs", "evidence", "cache_key"}, "stage reproducible")
        if stage["schema"] != STAGE_SCHEMA or stage["reproducible_sha256"] != hashlib.sha256(canonical({"schema": STAGE_SCHEMA, "reproducible": reproducible})).hexdigest().upper():
            raise VerificationError("stage seal mismatch")
        without_cache = {key: item for key, item in reproducible.items() if key != "cache_key"}
        expected_inputs = {
            "publication_contract", "accepted_reconstruction",
            *(
                (), ("master_en_acceptance",), ("master_ru_submission",),
                ("master_ru_acceptance",), ("artview_acceptance", "artview_decisions"),
                ("master_ru_acceptance", "artview_acceptance", "artview_decisions"),
                ("html_acceptance",), ("docx_acceptance",),
            )[index],
        }
        inputs = reproducible["inputs"]
        if index == 6 and isinstance(inputs, list) and any(row.get("kind") == "reviewed_docx" for row in inputs if isinstance(row, dict)):
            expected_inputs.add("reviewed_docx")
        if not isinstance(inputs, list) or len(inputs) != len(expected_inputs) or {row.get("kind") for row in inputs if isinstance(row, dict)} != expected_inputs:
            raise VerificationError("stage authority input set mismatch")
        for row in inputs:
            exact(row, {"kind", "file"}, "stage input")
            exact(row["file"], {"path", "bytes", "sha256"}, "stage input identity")
        adapter = exact(reproducible["adapter"], {"logical_name", "version", "script"}, "stage adapter")
        exact(adapter["script"], {"path", "bytes", "sha256"}, "stage adapter script")
        exact(reproducible["effective_config"], {"path", "bytes", "sha256"}, "stage effective config")
        if reproducible["stage_id"] != stage_id or reproducible["stage_name"] != stage_name or reproducible["stage_version"] != 1 or reproducible["state"] != "succeeded" or reproducible["run_identity_sha256"] != manifest["publication_run_identity_sha256"] or reproducible["upstream"] != upstream or adapter["logical_name"] != adapter_name or adapter["version"] != 1 or reproducible["cache_key"] != hashlib.sha256(canonical(without_cache)).hexdigest().upper():
            raise VerificationError("stage graph or adapter mismatch")
        observed_continuity = (
            canonical(adapter["script"]), canonical(reproducible["effective_config"]),
            canonical(reproducible["tools"]), reproducible["implementation_inventory_sha256"],
            canonical([row["file"] for row in inputs if row["kind"] in {"publication_contract", "accepted_reconstruction"}]),
        )
        if continuity is None:
            continuity = observed_continuity
        elif continuity != observed_continuity:
            raise VerificationError("stage config, tool, implementation, or source continuity mismatch")
        stages.append(stage)
        upstream.append({"stage_id": stage_id, "manifest_sha256": stage["reproducible_sha256"]})
    reviewed_inputs = [row["file"] for row in stages[6]["reproducible"]["inputs"] if row["kind"] == "reviewed_docx"]
    reviewed_role = role_map.get("reviewed_docx_submission")
    if reviewed_inputs:
        if reviewed_role is None or {key: identity(reviewed_role, package_root)[key] for key in ("bytes", "sha256")} != {key: reviewed_inputs[0][key] for key in ("bytes", "sha256")}:
            raise VerificationError("reviewed DOCX submission identity mismatch")
    elif reviewed_role is not None:
        raise VerificationError("unbound reviewed DOCX submission")
    effective_identity = identity(role_map["effective_config"], package_root)
    if {key: stages[0]["reproducible"]["effective_config"].get(key) for key in ("bytes", "sha256")} != {key: effective_identity[key] for key in ("bytes", "sha256")}:
        raise VerificationError("packaged effective config authority mismatch")
    for group in ("acceptance_receipts", "config_inventory", "pipeline_snapshot"):
        records = manifest[group]
        if not isinstance(records, list) or len({canonical(row) for row in records}) != len(records):
            raise VerificationError(f"{group} contains duplicates")
        for index, record in enumerate(records):
            resolve(package_root, record, f"{group} {index}")
    upstream_records = exact(manifest["upstream"], {"reconstruction_inventory", "reconstruction_acceptance", "source_identity"}, "package upstream")
    for name, record in upstream_records.items():
        resolve(package_root, record, f"upstream {name}")
    acceptance_records = manifest["acceptance_receipts"]
    if not isinstance(acceptance_records, list) or len(acceptance_records) != 6 or len({canonical(row) for row in acceptance_records}) != 6:
        raise VerificationError("package requires exact six acceptance receipts")
    candidates = {"master_en": "master_en", "master_ru": "master_ru", "artview": "artview_candidate_manifest", "html": "html", "docx": "docx", "pdf": "pdf"}
    acceptances = {}
    producer_indexes = {"master_en": 0, "master_ru": 2, "artview": 3, "html": 5, "docx": 6, "pdf": 7}
    for kind in ACCEPTANCE_KINDS:
        receipt_path = role_map[f"{kind}_acceptance"]
        receipt_identity = identity(receipt_path, package_root)
        if acceptance_records.count(receipt_identity) != 1:
            raise VerificationError(f"{kind} acceptance role mismatch")
        receipt = read_json(receipt_path)
        exact(receipt, {"schema", "scenario_id", "artifact_kind", "candidate", "producer_stage", "evidence", "decision", "decision_at_utc", "user_decision_reference", "recorder_role", "receipt_sha256"}, f"{kind} acceptance")
        validate_seal(receipt, "receipt_sha256", f"{kind} acceptance")
        producer = stage_records[producer_indexes[kind]]
        if receipt["schema"] != ACCEPTANCE_SCHEMA or receipt["scenario_id"] != manifest["scenario_id"] or receipt["artifact_kind"] != kind or receipt["decision"] != "accepted" or receipt["recorder_role"] != "main_orchestrator" or not str(receipt["user_decision_reference"]).strip() or {key: receipt["candidate"].get(key) for key in ("bytes", "sha256")} != {key: identity(role_map[candidates[kind]], package_root)[key] for key in ("bytes", "sha256")} or {key: receipt["producer_stage"].get(key) for key in ("bytes", "sha256")} != {key: producer[key] for key in ("bytes", "sha256")}:
            raise VerificationError(f"{kind} acceptance authority mismatch")
        acceptances[kind] = receipt
    decisions_identity = identity(role_map["artview_decisions"], package_root)
    if acceptances["artview"]["evidence"].count(decisions_identity) != 1:
        raise VerificationError("ArtView acceptance lacks exact packaged decisions")
    for index, stage in enumerate(stages):
        for row in stage["reproducible"]["inputs"]:
            kind = str(row.get("kind", ""))
            if kind.endswith("_acceptance") and kind.removesuffix("_acceptance") in acceptances:
                role_identity = identity(role_map[kind], package_root)
                if {key: row["file"].get(key) for key in ("bytes", "sha256")} != {key: role_identity[key] for key in ("bytes", "sha256")}:
                    raise VerificationError(f"Stage {index} has stale {kind}")
    stage60 = stages[-1]["reproducible"]
    document_inputs = [row for row in stage60["inputs"] if row.get("kind") == "docx_acceptance"]
    if len(document_inputs) != 1 or stage60["adapter"].get("logical_name") != "docx_pdf_export_v1" or any(row.get("kind") in {"html_acceptance", "source_html", "pdf", "stage50_pdf", "stage50_png"} for row in stage60["inputs"]):
        raise VerificationError("Stage 60 lacks exact accepted-DOCX lineage")
    if {key: document_inputs[0]["file"].get(key) for key in ("bytes", "sha256")} != {key: identity(role_map["docx_acceptance"], package_root)[key] for key in ("bytes", "sha256")}:
        raise VerificationError("Stage 60 DOCX acceptance mismatch")
    stage60_pdfs = [row for row in stage60["outputs"].get("files", []) if str(row.get("path", "")).lower().endswith(".pdf")]
    if len(stage60_pdfs) != 1 or {key: stage60_pdfs[0].get(key) for key in ("bytes", "sha256")} != {key: pdfs[0][key] for key in ("bytes", "sha256")}:
        raise VerificationError("Stage 60 PDF identity mismatch")
    return {"schema": "kb_creator.production_package_verification.v1", "state": "candidate_for_release_review", "release_state": "not_reviewed", "manifest_sha256": manifest["manifest_sha256"], "pdf_count": 1, "html_local_reference_count": html_local_reference_count}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--package-root", required=True, type=Path)
    args = parser.parse_args()
    try:
        result = verify_package(args.package_root)
    except Exception as error:
        print(json.dumps({"state": "blocked", "error": f"{type(error).__name__}: {error}"}, ensure_ascii=False, sort_keys=True), file=sys.stderr)
        return 2
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
