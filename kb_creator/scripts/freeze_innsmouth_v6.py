from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


BASELINE_COMMIT = "0470919f83e2d536ecae78010096e1f768bc0626"
PROJECT_KEY = "the_innsmouth_terror"
FREEZE_STATE = "baseline_frozen"

FROZEN_FILES = [
    "CoC/Working/Scenarios/The_Innsmouth_Terror/project/QA/Recovery_v6/the_innsmouth_terror.recovery_v6_cleaned.package.json",
    "CoC/Output/Scenarios/The_Innsmouth_Terror/For_Keeper/KeeperBook_v6.md",
    "CoC/Output/Scenarios/The_Innsmouth_Terror/The_Innsmouth_Terror_Full_RU_v6.html",
    "CoC/Output/Scenarios/The_Innsmouth_Terror/Pdf/The_Innsmouth_Terror_Full_RU_v6_two_column.pdf",
    "CoC/Working/Scenarios/The_Innsmouth_Terror/project/QA/Recovery_v6/frontmatter_manifest.json",
    "CoC/Working/Scenarios/The_Innsmouth_Terror/project/QA/Recovery_v6/production_html_report_v6.json",
    "CoC/Working/Scenarios/The_Innsmouth_Terror/project/QA/Recovery_v6/html_v6_statblock_projection_report.json",
    "CoC/Working/Scenarios/The_Innsmouth_Terror/project/QA/Recovery_v6/positive_content_audit.v1.json",
    "CoC/Working/Scenarios/The_Innsmouth_Terror/project/QA/Recovery_v6/coc_mechanics_audit.v1.json",
    "CoC/Working/Scenarios/The_Innsmouth_Terror/project/QA/Recovery_v6/art_layout_qa.json",
    "CoC/Working/Scenarios/The_Innsmouth_Terror/project/QA/Recovery_v6/page_structure_audit.v1.json",
    "CoC/Working/Scenarios/The_Innsmouth_Terror/project/QA/Recovery_v6/semantic_chain_audit.v1.json",
    "CoC/Working/Scenarios/The_Innsmouth_Terror/project/QA/Recovery_v6/production_pdf_report_v6_two_column.json",
    "CoC/Working/Scenarios/The_Innsmouth_Terror/project/QA/Recovery_v6/pdf_print_qa_two_column.json",
    "CoC/Working/Scenarios/The_Innsmouth_Terror/project/scripts/apply_statblock_projection_to_html_v3.py",
    "translator/translator.py",
    "translator/positive_content_audit.py",
    "translator/docs/architecture/production_frontmatter_standard.md",
]

KB_ROOT = Path("CoC/Output/Scenarios/The_Innsmouth_Terror/Knowledge_Base_v6")
HTML_PATH = Path("CoC/Output/Scenarios/The_Innsmouth_Terror/The_Innsmouth_Terror_Full_RU_v6.html")

QA_REPORT_STATUS_PATHS = {
    "production_html": "CoC/Working/Scenarios/The_Innsmouth_Terror/project/QA/Recovery_v6/production_html_report_v6.json",
    "statblock_projection": "CoC/Working/Scenarios/The_Innsmouth_Terror/project/QA/Recovery_v6/html_v6_statblock_projection_report.json",
    "positive_content": "CoC/Working/Scenarios/The_Innsmouth_Terror/project/QA/Recovery_v6/positive_content_audit.v1.json",
    "coc_mechanics": "CoC/Working/Scenarios/The_Innsmouth_Terror/project/QA/Recovery_v6/coc_mechanics_audit.v1.json",
    "art_layout": "CoC/Working/Scenarios/The_Innsmouth_Terror/project/QA/Recovery_v6/art_layout_qa.json",
    "page_structure": "CoC/Working/Scenarios/The_Innsmouth_Terror/project/QA/Recovery_v6/page_structure_audit.v1.json",
    "semantic_chain": "CoC/Working/Scenarios/The_Innsmouth_Terror/project/QA/Recovery_v6/semantic_chain_audit.v1.json",
    "production_pdf": "CoC/Working/Scenarios/The_Innsmouth_Terror/project/QA/Recovery_v6/production_pdf_report_v6_two_column.json",
    "pdf_print": "CoC/Working/Scenarios/The_Innsmouth_Terror/project/QA/Recovery_v6/pdf_print_qa_two_column.json",
}

VERIFY_COMMAND = [
    "python",
    "kb_creator/scripts/check_innsmouth_v6_freeze.py",
    "--manifest",
    "kb_creator/inputs/innsmouth_v6_freeze_manifest.json",
    "--report",
    "kb_creator/reports/innsmouth_v6_reproducibility_report.json",
]


def repo_root() -> Path:
    output = subprocess.check_output(["git", "rev-parse", "--show-toplevel"], text=True).strip()
    return Path(output)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def file_record(root: Path, rel_path: str) -> dict[str, Any]:
    path = root / rel_path
    if not path.exists():
        raise FileNotFoundError(rel_path)
    return {
        "path": rel_path.replace("\\", "/"),
        "sha256": sha256_file(path),
        "size_bytes": path.stat().st_size,
        "hash_mode": "binary_sha256",
    }


def read_json(root: Path, rel_path: str) -> dict[str, Any]:
    with (root / rel_path).open("r", encoding="utf-8") as handle:
        return json.load(handle)


def collect_kb_files(root: Path) -> list[str]:
    kb_dir = root / KB_ROOT
    return [
        str(path.relative_to(root)).replace("\\", "/")
        for path in sorted(kb_dir.glob("*.md"))
    ]


def collect_html_image_files(root: Path) -> list[str]:
    html_path = root / HTML_PATH
    html_text = html_path.read_text(encoding="utf-8")
    image_paths: list[str] = []
    for match in re.finditer(r'<img\b[^>]*\bsrc=["\']([^"\']+)["\']', html_text, re.I):
        src = match.group(1).strip()
        if not src or re.match(r"^[a-z]+:", src, re.I):
            continue
        path = (html_path.parent / src.replace("/", "\\")).resolve()
        try:
            rel_path = str(path.relative_to(root)).replace("\\", "/")
        except ValueError:
            continue
        image_paths.append(rel_path)
    return sorted(dict.fromkeys(image_paths))


def collect_qa_status(root: Path) -> dict[str, dict[str, Any]]:
    statuses: dict[str, dict[str, Any]] = {}
    for name, rel_path in QA_REPORT_STATUS_PATHS.items():
        data = read_json(root, rel_path)
        statuses[name] = {
            "path": rel_path,
            "sha256": sha256_file(root / rel_path),
            "status": data.get("status"),
            "action": data.get("action"),
            "findings": (data.get("counts") or {}).get("findings", len(data.get("findings", []))),
            "warnings": (data.get("counts") or {}).get("warnings", len(data.get("warnings", []))),
        }
    return statuses


def build_manifest(root: Path) -> dict[str, Any]:
    frozen_paths = list(dict.fromkeys(FROZEN_FILES + collect_kb_files(root) + collect_html_image_files(root)))
    records = [file_record(root, rel_path) for rel_path in frozen_paths]
    return {
        "schema": "kb_creator_innsmouth_v6_freeze_manifest.v1",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "freeze_state": FREEZE_STATE,
        "production_approved": False,
        "project_key": PROJECT_KEY,
        "scenario": "The Innsmouth Terror",
        "baseline_commit": BASELINE_COMMIT,
        "path_mode": "repo_relative",
        "verification": {
            "working_directory": ".",
            "command": VERIFY_COMMAND,
            "checker": "kb_creator/scripts/check_innsmouth_v6_freeze.py",
            "report": "kb_creator/reports/innsmouth_v6_reproducibility_report.json",
            "scope": "content-hash and QA-status verification of frozen tracked baseline",
        },
        "invalidation_rule": (
            "Any mutation of listed source/config/script/QA/output files or required images "
            "invalidates this manifest and any review based on it."
        ),
        "intentional_exclusions": [
            "CoC/Working/Scenarios/The_Innsmouth_Terror/project/QA/Recovery_v6/release_qa_report.json",
            "CoC/Working/Scenarios/The_Innsmouth_Terror/project/QA/Recovery_v6/Pipeline_Cache/",
            "CoC/Working/Scenarios/The_Innsmouth_Terror/project/QA/Recovery_v6/Production_PDF_Temp/",
            "CoC/Working/Scenarios/The_Innsmouth_Terror/project/QA/Recovery_v2/",
            "CoC/Working/Scenarios/The_Innsmouth_Terror/project/QA/Recovery_v5/",
            "CoC/Output/Scenarios/The_Innsmouth_Terror/The_Innsmouth_Terror_Full_RU_v2.html",
            "CoC/Output/Scenarios/The_Innsmouth_Terror/The_Innsmouth_Terror_Full_RU_v5.html",
            "raw agent transcripts",
            "browser profiles and scratch renders",
        ],
        "artifacts": {
            "config": "CoC/Working/Scenarios/The_Innsmouth_Terror/project/QA/Recovery_v6/the_innsmouth_terror.recovery_v6_cleaned.package.json",
            "keeper_book": "CoC/Output/Scenarios/The_Innsmouth_Terror/For_Keeper/KeeperBook_v6.md",
            "knowledge_base_root": str(KB_ROOT).replace("\\", "/"),
            "html": "CoC/Output/Scenarios/The_Innsmouth_Terror/The_Innsmouth_Terror_Full_RU_v6.html",
            "pdf_two_column": "CoC/Output/Scenarios/The_Innsmouth_Terror/Pdf/The_Innsmouth_Terror_Full_RU_v6_two_column.pdf",
        },
        "qa_statuses": collect_qa_status(root),
        "files": records,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output",
        default="kb_creator/inputs/innsmouth_v6_freeze_manifest.json",
        help="Repo-relative output manifest path.",
    )
    args = parser.parse_args()
    root = repo_root()
    manifest = build_manifest(root)
    output = root / args.output
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"status=pass files={len(manifest['files'])} output={args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
