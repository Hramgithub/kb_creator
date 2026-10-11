"""Preflight or promote an explicitly user-accepted Innsmouth MASTER_EN package."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import shutil
import sys
from typing import Any

SCRIPTS_DIR = Path(__file__).resolve().parent
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))
import build_innsmouth_master_en as master


ROOT_FILES = {"MASTER_EN.md", "MASTER_EN.qa.json"}
HEX_SHA256 = re.compile(r"^[0-9a-fA-F]{64}$")
WINDOWS_ABSOLUTE_PATH = re.compile(rb"(?:[A-Za-z]:(?:\\\\|/)|\\\\\\\\)")
EXPECTED_SOURCE_RECONSTRUCTED_EN = {
    "markdown": {
        "path": "RECONSTRUCTED_EN.md",
        "byte_count": master.RECONSTRUCTED_EN_BYTES,
        "sha256": master.RECONSTRUCTED_EN_SHA256,
    },
    "qa": {
        "path": "RECONSTRUCTED_EN.qa.json",
        "byte_count": master.RECONSTRUCTED_EN_QA_BYTES,
        "sha256": master.RECONSTRUCTED_EN_QA_SHA256,
    },
    "asset_inventory": {
        "asset_count": 136,
        "inventory_sha256": master.reconstructed.FINAL_ASSET_INVENTORY_SHA256,
    },
}


def sha256(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest().upper()


def canonical_json(value: Any) -> bytes:
    return (
        json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        + "\n"
    ).encode("utf-8")


def _expected_hash(value: str, label: str) -> str:
    if not HEX_SHA256.fullmatch(value):
        raise ValueError(f"{label} must be one explicit SHA-256")
    return value.upper()


def verify_source_reconstructed_identity(value: object) -> dict[str, Any]:
    if value != EXPECTED_SOURCE_RECONSTRUCTED_EN:
        raise ValueError("MASTER_EN QA canonical Stage B provenance mismatch")
    return value


def inspect_candidate(
    root: Path,
    expected_master_sha256: str,
    expected_qa_sha256: str,
    *,
    allowed_root_files: set[str] = ROOT_FILES,
    expected_file_count: int = len(master.RETAINED_ASSETS) + 2,
) -> dict[str, Any]:
    expected_master_sha256 = _expected_hash(expected_master_sha256, "MASTER_EN hash")
    expected_qa_sha256 = _expected_hash(expected_qa_sha256, "MASTER_EN QA hash")
    if not root.is_dir():
        raise ValueError(f"missing MASTER_EN candidate directory: {root}")
    root_files = {path.name for path in root.iterdir() if path.is_file()}
    root_directories = {path.name for path in root.iterdir() if path.is_dir()}
    if root_files != allowed_root_files:
        raise ValueError(f"unexpected MASTER_EN candidate root files: {sorted(root_files)}")
    if root_directories != {"assets"}:
        raise ValueError(
            f"unexpected MASTER_EN candidate root directories: {sorted(root_directories)}"
        )
    assets_dir = root / "assets"
    files = sorted(path for path in root.rglob("*") if path.is_file())
    if (
        len(files) != expected_file_count
        or len(list(assets_dir.glob("*"))) != len(master.RETAINED_ASSETS)
    ):
        raise ValueError("MASTER_EN candidate package inventory mismatch")

    markdown_raw = (root / "MASTER_EN.md").read_bytes()
    qa_raw = (root / "MASTER_EN.qa.json").read_bytes()
    if sha256(markdown_raw) != expected_master_sha256:
        raise ValueError("MASTER_EN candidate identity mismatch")
    if sha256(qa_raw) != expected_qa_sha256:
        raise ValueError("MASTER_EN QA identity mismatch")
    if WINDOWS_ABSOLUTE_PATH.search(qa_raw):
        raise ValueError("MASTER_EN QA contains a device-specific absolute path")

    markdown = markdown_raw.decode("utf-8")
    counts = master.validate_master_en(markdown)
    qa = json.loads(qa_raw)
    if qa.get("state") != "MASTER_EN_READER_PACKAGE_READY":
        raise ValueError("MASTER_EN QA state mismatch")
    input_identity = verify_source_reconstructed_identity(qa.get("input", {}))

    inventory = master.retained_asset_inventory(assets_dir)
    if qa.get("asset_inventory", {}).get("inventory_sha256") != inventory["inventory_sha256"]:
        raise ValueError("MASTER_EN QA asset inventory mismatch")
    return {
        "state": "MASTER_EN_CANDIDATE_PREFLIGHT_OK",
        "markdown": {
            "path": "MASTER_EN.md",
            "byte_count": len(markdown_raw),
            "sha256": sha256(markdown_raw),
        },
        "qa": {
            "path": "MASTER_EN.qa.json",
            "byte_count": len(qa_raw),
            "sha256": sha256(qa_raw),
        },
        "source_reconstructed_en": input_identity,
        "asset_inventory": inventory,
        "counts": counts,
    }


def acceptance_manifest(report: dict[str, Any], accepted_on: str) -> bytes:
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", accepted_on):
        raise ValueError("accepted-on must use YYYY-MM-DD")
    return canonical_json(
        {
            "schema": "InnsmouthAcceptedMasterEn.v1",
            "state": "ACCEPTED_MASTER_EN_REPO_INPUT",
            "accepted_on": accepted_on,
            "acceptance_authority": "explicit_user_promotion_in_main_chat",
            "source_reconstructed_en": report["source_reconstructed_en"],
            "package": {
                "markdown": report["markdown"],
                "qa": report["qa"],
                "asset_count": report["asset_inventory"]["asset_count"],
                "asset_inventory_sha256": report["asset_inventory"]["inventory_sha256"],
                "counts": report["counts"],
            },
            "rules": {
                "manual_file_copy_forbidden": True,
                "historical_ru_or_en_bridge_forbidden": True,
                "generated_html_or_pdf_manual_edit_forbidden": True,
            },
        }
    )


def verify_promoted(root: Path) -> dict[str, Any]:
    manifest_path = root / "MASTER_EN.acceptance.json"
    if not manifest_path.is_file():
        raise ValueError("missing MASTER_EN acceptance manifest")
    manifest = json.loads(manifest_path.read_bytes())
    if manifest.get("state") != "ACCEPTED_MASTER_EN_REPO_INPUT":
        raise ValueError("MASTER_EN acceptance state mismatch")
    package = manifest.get("package", {})
    report = inspect_candidate(
        root,
        package.get("markdown", {}).get("sha256", ""),
        package.get("qa", {}).get("sha256", ""),
        allowed_root_files=ROOT_FILES | {"MASTER_EN.acceptance.json"},
        expected_file_count=len(master.RETAINED_ASSETS) + 3,
    )
    if package.get("asset_inventory_sha256") != report["asset_inventory"]["inventory_sha256"]:
        raise ValueError("accepted MASTER_EN inventory mismatch")
    if package.get("counts") != report["counts"]:
        raise ValueError("accepted MASTER_EN structural counts mismatch")
    return {**report, "state": "ACCEPTED_MASTER_EN_REPO_INPUT_VERIFIED"}


def promote(
    candidate: Path,
    target: Path,
    expected_master_sha256: str,
    expected_qa_sha256: str,
    accepted_on: str,
) -> dict[str, Any]:
    if target.exists():
        raise ValueError(f"refusing to overwrite accepted MASTER_EN target: {target}")
    stage = target.with_name(target.name + ".stage")
    if stage.exists():
        raise ValueError(f"MASTER_EN promotion stage already exists: {stage}")
    report = inspect_candidate(candidate, expected_master_sha256, expected_qa_sha256)
    manifest = acceptance_manifest(report, accepted_on)
    stage.mkdir(parents=True)
    try:
        shutil.copyfile(candidate / "MASTER_EN.md", stage / "MASTER_EN.md")
        shutil.copyfile(candidate / "MASTER_EN.qa.json", stage / "MASTER_EN.qa.json")
        shutil.copytree(candidate / "assets", stage / "assets")
        (stage / "MASTER_EN.acceptance.json").write_bytes(manifest)
        stage.rename(target)
    except Exception:
        if stage.exists():
            shutil.rmtree(stage)
        raise
    return verify_promoted(target)


def main() -> None:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--preflight", action="store_true")
    mode.add_argument("--promote", action="store_true")
    mode.add_argument("--verify", action="store_true")
    parser.add_argument("--candidate", type=Path)
    parser.add_argument("--target", type=Path)
    parser.add_argument("--expected-master-sha256")
    parser.add_argument("--expected-qa-sha256")
    parser.add_argument("--accepted-on")
    args = parser.parse_args()

    if args.verify:
        if args.target is None:
            raise SystemExit("--target is required with --verify")
        result = verify_promoted(args.target)
        print(json.dumps(result, ensure_ascii=False, sort_keys=True))
        print("INNSMOUTH_ACCEPTED_MASTER_EN_REPO_INPUT_OK")
        return
    required = (
        args.candidate,
        args.expected_master_sha256,
        args.expected_qa_sha256,
    )
    if any(value is None for value in required):
        raise SystemExit(
            "--candidate, --expected-master-sha256 and --expected-qa-sha256 are required"
        )
    if args.preflight:
        result = inspect_candidate(
            args.candidate, args.expected_master_sha256, args.expected_qa_sha256
        )
        print(json.dumps(result, ensure_ascii=False, sort_keys=True))
        print("INNSMOUTH_MASTER_EN_PROMOTION_PREFLIGHT_OK")
        return
    if args.target is None or args.accepted_on is None:
        raise SystemExit("--target and --accepted-on are required with --promote")
    result = promote(
        args.candidate,
        args.target,
        args.expected_master_sha256,
        args.expected_qa_sha256,
        args.accepted_on,
    )
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    print("INNSMOUTH_MASTER_EN_PROMOTED")


if __name__ == "__main__":
    main()
