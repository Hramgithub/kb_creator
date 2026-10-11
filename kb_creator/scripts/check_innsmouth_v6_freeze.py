from __future__ import annotations

import argparse
import hashlib
import json
import platform
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REQUIRED_QA_STATUSES = {
    "production_html": "pass",
    "statblock_projection": "pass",
    "positive_content": "pass",
    "coc_mechanics": "pass",
    "art_layout": "pass",
    "page_structure": "pass",
    "semantic_chain": "pass",
    "production_pdf": "pass",
    "pdf_print": "pass",
}

STALE_EXCLUDED_PATHS = {
    "CoC/Working/Scenarios/The_Innsmouth_Terror/project/QA/Recovery_v6/release_qa_report.json",
}


def repo_root() -> Path:
    output = subprocess.check_output(["git", "rev-parse", "--show-toplevel"], text=True).strip()
    return Path(output)


def git_head(root: Path) -> str:
    return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=root, text=True).strip()


def git_is_ancestor(root: Path, ancestor: str, descendant: str) -> bool:
    if not ancestor or not descendant:
        return False
    result = subprocess.run(
        ["git", "merge-base", "--is-ancestor", ancestor, descendant],
        cwd=root,
        text=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    return result.returncode == 0


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def check_files(root: Path, manifest: dict[str, Any]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    checks: list[dict[str, Any]] = []
    findings: list[dict[str, Any]] = []
    for record in manifest.get("files", []):
        rel_path = str(record.get("path") or "")
        expected_sha = str(record.get("sha256") or "").lower()
        expected_size = int(record.get("size_bytes") or -1)
        path = root / rel_path
        if not path.exists():
            findings.append({"code": "frozen_file_missing", "path": rel_path})
            checks.append({"path": rel_path, "status": "fail", "reason": "missing"})
            continue
        actual_sha = sha256_file(path)
        actual_size = path.stat().st_size
        status = "pass" if actual_sha == expected_sha and actual_size == expected_size else "fail"
        checks.append(
            {
                "path": rel_path,
                "status": status,
                "expected_sha256": expected_sha,
                "actual_sha256": actual_sha,
                "expected_size_bytes": expected_size,
                "actual_size_bytes": actual_size,
            }
        )
        if status != "pass":
            findings.append(
                {
                    "code": "frozen_file_hash_mismatch",
                    "path": rel_path,
                    "expected_sha256": expected_sha,
                    "actual_sha256": actual_sha,
                }
            )
    return checks, findings


def check_qa_statuses(manifest: dict[str, Any]) -> list[dict[str, Any]]:
    findings: list[dict[str, Any]] = []
    statuses = manifest.get("qa_statuses", {})
    for name, expected in REQUIRED_QA_STATUSES.items():
        row = statuses.get(name)
        if not isinstance(row, dict):
            findings.append({"code": "required_qa_status_missing", "qa": name})
            continue
        if row.get("status") != expected:
            findings.append({"code": "required_qa_status_not_pass", "qa": name, "status": row.get("status")})
        if name in {"positive_content", "coc_mechanics", "art_layout", "semantic_chain", "production_pdf", "pdf_print"}:
            if int(row.get("findings") or 0) != 0:
                findings.append({"code": "required_qa_has_findings", "qa": name, "findings": row.get("findings")})
    return findings


def check_exclusions(root: Path) -> list[dict[str, Any]]:
    findings: list[dict[str, Any]] = []
    for rel_path in STALE_EXCLUDED_PATHS:
        if (root / rel_path).exists():
            findings.append(
                {
                    "code": "stale_excluded_file_present",
                    "path": rel_path,
                    "severity": "warning",
                    "message": "Do not commit or cite this stale report as v6 freeze evidence.",
                }
            )
    return findings


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", required=True)
    parser.add_argument("--report", required=True)
    args = parser.parse_args()

    root = repo_root()
    manifest_path = root / args.manifest
    report_path = root / args.report
    manifest = load_json(manifest_path)
    file_checks, file_findings = check_files(root, manifest)
    qa_findings = check_qa_statuses(manifest)
    exclusion_findings = check_exclusions(root)
    blocker_findings = file_findings + qa_findings
    warnings = exclusion_findings

    current_head = git_head(root)
    baseline_commit = str(manifest.get("baseline_commit") or "")
    baseline_is_ancestor = git_is_ancestor(root, baseline_commit, current_head)
    status = "pass" if not blocker_findings else "fail"
    report = {
        "schema": "kb_creator_innsmouth_v6_reproducibility_report.v1",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "status": status,
        "mode": "dry_run_content_verification",
        "manifest": args.manifest,
        "manifest_sha256": sha256_file(manifest_path),
        "baseline_commit": baseline_commit,
        "current_head": current_head,
        "current_head_matches_baseline": current_head == baseline_commit,
        "baseline_is_ancestor_of_current_head": baseline_is_ancestor,
        "production_approved": manifest.get("production_approved"),
        "freeze_state": manifest.get("freeze_state"),
        "tool_versions": {
            "python": sys.version.split()[0],
            "platform": platform.platform(),
            "checker": "kb_creator/scripts/check_innsmouth_v6_freeze.py",
        },
        "counts": {
            "files": len(file_checks),
            "file_findings": len(file_findings),
            "qa_findings": len(qa_findings),
            "warnings": len(warnings),
        },
        "file_checks": file_checks,
        "qa_statuses": manifest.get("qa_statuses", {}),
        "findings": blocker_findings,
        "warnings": warnings,
        "cache_use": "none_declared",
        "result_note": (
            "This dry run verifies frozen baseline content hashes and QA-status evidence. "
            "It does not approve production release and does not rebuild OCR/translation."
        ),
    }
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(
        f"status={status} files={len(file_checks)} findings={len(blocker_findings)} "
        f"warnings={len(warnings)} report={args.report}"
    )
    return 0 if status == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
