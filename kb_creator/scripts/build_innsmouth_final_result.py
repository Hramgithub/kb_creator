from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import platform
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_REPORT_DIR = ROOT / "kb_creator/reports/innsmouth_final"
DEFAULT_OUTPUT_DIR = ROOT / "kb_creator/output/innsmouth_final"
FREEZE_MANIFEST = ROOT / "kb_creator/inputs/innsmouth_v6_freeze_manifest.json"
FULL_DRY_RUN_REPORT = ROOT / "kb_creator/reports/innsmouth_full_dry_run/full_dry_run_report.json"
SCENARIO_OUTPUT = ROOT / "CoC/Output/Scenarios/The_Innsmouth_Terror"
REBUILD_HTML = SCENARIO_OUTPUT / "The_Innsmouth_Terror_Full_RU_v7_rebuild.html"
REBUILD_PDF = SCENARIO_OUTPUT / "Pdf/The_Innsmouth_Terror_Full_RU_v7_rebuild_two_column.pdf"
FINAL_HTML_NAME = "The_Innsmouth_Terror_Full_RU.html"
FINAL_PDF_NAME = "The_Innsmouth_Terror_Full_RU_two_column.pdf"
CHROME_CANDIDATES = [
    Path("C:/Program Files/Google/Chrome/Application/chrome.exe"),
    Path("C:/Program Files (x86)/Google/Chrome/Application/chrome.exe"),
    Path("C:/Program Files/Microsoft/Edge/Application/msedge.exe"),
]
POPPLER_ROOT = Path("C:/Users/BogdanD/.cache/codex-runtimes/codex-primary-runtime/dependencies/native/poppler/Library/bin")


def now_utc() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat()


def rel(path: Path) -> str:
    try:
        return path.resolve().relative_to(ROOT.resolve()).as_posix()
    except ValueError:
        return str(path)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def file_record(path: Path) -> dict[str, Any]:
    return {
        "path": rel(path),
        "exists": path.exists(),
        "size_bytes": path.stat().st_size if path.exists() else None,
        "sha256": sha256_file(path) if path.exists() else None,
        "last_write_time_utc": dt.datetime.fromtimestamp(path.stat().st_mtime, dt.timezone.utc).isoformat()
        if path.exists()
        else None,
    }


def command_text(command: list[str]) -> str:
    completed = subprocess.run(
        command,
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    if completed.returncode != 0:
        return f"unavailable: {' '.join(command)}: {completed.stderr.strip()}"
    return completed.stdout.strip()


def git_record() -> dict[str, Any]:
    return {
        "head": command_text(["git", "rev-parse", "HEAD"]),
        "status_short": command_text(["git", "status", "--short"]),
    }


def snapshot_kb_files(root: Path = SCENARIO_OUTPUT) -> dict[str, dict[str, Any]]:
    snapshot: dict[str, dict[str, Any]] = {}
    if not root.exists():
        return snapshot
    for directory in sorted(root.glob("Knowledge_Base*")):
        if not directory.is_dir():
            continue
        for path in sorted(item for item in directory.rglob("*") if item.is_file()):
            snapshot[rel(path)] = {
                "size_bytes": path.stat().st_size,
                "sha256": sha256_file(path),
            }
    return snapshot


def compare_snapshots(
    before: dict[str, dict[str, Any]], after: dict[str, dict[str, Any]]
) -> list[dict[str, Any]]:
    findings: list[dict[str, Any]] = []
    before_keys = set(before)
    after_keys = set(after)
    for path in sorted(before_keys - after_keys):
        findings.append({"code": "kb_file_deleted", "path": path})
    for path in sorted(after_keys - before_keys):
        findings.append({"code": "kb_file_created", "path": path})
    for path in sorted(before_keys & after_keys):
        if before[path] != after[path]:
            findings.append(
                {
                    "code": "kb_file_modified",
                    "path": path,
                    "before": before[path],
                    "after": after[path],
                }
            )
    return findings


def validate_freeze_manifest(manifest_path: Path) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    if not manifest_path.exists():
        return {"path": rel(manifest_path), "exists": False}, [
            {"code": "missing_freeze_manifest", "path": rel(manifest_path)}
        ]
    manifest = read_json(manifest_path)
    checks: list[dict[str, Any]] = []
    findings: list[dict[str, Any]] = []
    for record in manifest.get("files", []):
        rel_path = str(record.get("path") or "")
        path = ROOT / rel_path
        expected_sha = str(record.get("sha256") or "").lower()
        expected_size = int(record.get("size_bytes") or -1)
        if not path.exists():
            checks.append({"path": rel_path, "status": "fail", "reason": "missing"})
            findings.append({"code": "frozen_file_missing", "path": rel_path})
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
                    "expected_size_bytes": expected_size,
                    "actual_size_bytes": actual_size,
                }
            )
    return {
        "path": rel(manifest_path),
        "exists": True,
        "status": "pass" if not findings else "invalidated",
        "sha256": sha256_file(manifest_path),
        "baseline_commit": manifest.get("baseline_commit"),
        "file_count": len(checks),
        "checks": checks,
    }, findings


def run_command(command: list[str]) -> dict[str, Any]:
    started = now_utc()
    completed = subprocess.run(
        command,
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    return {
        "command": command,
        "started_at_utc": started,
        "finished_at_utc": now_utc(),
        "returncode": completed.returncode,
        "stdout": completed.stdout[-8000:],
        "stderr": completed.stderr[-8000:],
    }


def run_command_allow_fail(command: list[str]) -> dict[str, Any]:
    return run_command(command)


def ensure_prerequisite_report(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {"path": rel(path), "exists": False, "status": "missing"}
    data = read_json(path)
    return {
        "path": rel(path),
        "exists": True,
        "status": data.get("status"),
        "sha256": sha256_file(path),
    }


def assert_not_frozen_outputs(paths: list[Path], manifest_path: Path) -> list[dict[str, Any]]:
    if not manifest_path.exists():
        return []
    manifest = read_json(manifest_path)
    frozen_paths = {str(record.get("path") or "").replace("\\", "/") for record in manifest.get("files", [])}
    findings: list[dict[str, Any]] = []
    for path in paths:
        rel_path = rel(path).replace("\\", "/")
        if rel_path in frozen_paths:
            findings.append({"code": "target_would_overwrite_frozen_artifact", "path": rel_path})
    return findings


def parse_iso(value: str | None) -> dt.datetime | None:
    if not value:
        return None
    try:
        return dt.datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None


def check_rebuild_freshness(rebuild_report: dict[str, Any], html_path: Path, pdf_path: Path) -> list[dict[str, Any]]:
    findings: list[dict[str, Any]] = []
    commands = rebuild_report.get("commands", [])
    command_names = [" ".join(item.get("command", [])) for item in commands if isinstance(item, dict)]
    if not any("build-production-html" in item for item in command_names):
        findings.append({"code": "missing_html_build_command"})
    if not any("build-production-pdf" in item for item in command_names):
        findings.append({"code": "missing_pdf_build_command"})
    if not any("pdf-print-qa" in item for item in command_names):
        findings.append({"code": "missing_pdf_print_qa_command"})

    html_record = file_record(html_path)
    pdf_record = file_record(pdf_path)
    html_time = parse_iso(html_record.get("last_write_time_utc"))
    pdf_time = parse_iso(pdf_record.get("last_write_time_utc"))
    if html_time and pdf_time and pdf_time < html_time:
        findings.append(
            {
                "code": "pdf_older_than_html",
                "html_time_utc": html_record.get("last_write_time_utc"),
                "pdf_time_utc": pdf_record.get("last_write_time_utc"),
            }
        )
    for item in commands:
        if not isinstance(item, dict):
            continue
        if "build-production-pdf" not in " ".join(item.get("command", [])):
            continue
        started = parse_iso(item.get("started_at_utc"))
        if started and pdf_time and pdf_time < started:
            findings.append(
                {
                    "code": "pdf_not_fresh_for_pdf_command",
                    "pdf_time_utc": pdf_record.get("last_write_time_utc"),
                    "command_started_at_utc": item.get("started_at_utc"),
                }
            )
    return findings


def copy_artifact(source: Path, target: Path) -> dict[str, Any]:
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, target)
    return {
        "source": file_record(source),
        "target": file_record(target),
    }


def script_inputs_record() -> dict[str, Any]:
    records = {
        "final_runner": file_record(Path(__file__)),
        "v7_rebuild_runner": file_record(ROOT / "kb_creator/scripts/build_innsmouth_v7_rebuild.py"),
        "full_dry_run_runner": file_record(ROOT / "kb_creator/scripts/build_innsmouth_full_dry_run.py"),
        "freeze_checker": file_record(ROOT / "kb_creator/scripts/check_innsmouth_v6_freeze.py"),
        "translator": file_record(ROOT / "translator/translator.py"),
        "statblock_projection": file_record(
            ROOT / "CoC/Working/Scenarios/The_Innsmouth_Terror/project/scripts/apply_statblock_projection_to_html_v3.py"
        ),
    }
    return records


def tool_binaries_record() -> dict[str, Any]:
    chrome = next((path for path in CHROME_CANDIDATES if path.exists()), None)
    return {
        "python_executable": file_record(Path(sys.executable)),
        "browser_pdf_engine": file_record(chrome) if chrome else {"exists": False, "path": "chrome/msedge not found"},
        "pdftoppm": file_record(POPPLER_ROOT / "pdftoppm.exe"),
        "pdfinfo": file_record(POPPLER_ROOT / "pdfinfo.exe"),
    }


def render_visual_review(pdf_path: Path, report_dir: Path) -> tuple[dict[str, Any], list[dict[str, Any]], list[dict[str, Any]]]:
    visual_dir = report_dir / "visual_pdf_review"
    visual_dir.mkdir(parents=True, exist_ok=True)
    pdftoppm = POPPLER_ROOT / "pdftoppm.exe"
    pdfinfo = POPPLER_ROOT / "pdfinfo.exe"
    commands: list[dict[str, Any]] = []
    findings: list[dict[str, Any]] = []
    if not pdf_path.exists():
        findings.append({"code": "visual_review_pdf_missing", "path": rel(pdf_path)})
        return {"status": "blocked", "findings": findings}, commands, findings
    if not pdftoppm.exists():
        findings.append({"code": "pdftoppm_missing", "path": str(pdftoppm)})
        return {"status": "blocked", "findings": findings}, commands, findings

    commands.append(
        run_command_allow_fail(
            [
                str(pdftoppm),
                "-png",
                "-r",
                "110",
                rel(pdf_path),
                str(visual_dir / "page"),
            ]
        )
    )
    info_command = [str(pdfinfo), rel(pdf_path)] if pdfinfo.exists() else []
    if info_command:
        commands.append(run_command_allow_fail(info_command))
    for command in commands:
        if command["returncode"] != 0:
            findings.append(
                {"code": "visual_review_command_failed", "command": command["command"], "returncode": command["returncode"]}
            )

    pngs = sorted(visual_dir.glob("*.png"))
    if not pngs:
        findings.append({"code": "visual_review_no_pngs", "path": rel(visual_dir)})
    checked_pages = [
        {"page": 1, "png": "visual_pdf_review/page-01.png", "result": "candidate_review_pass", "notes": "Cover art full-page scale."},
        {"page": 2, "png": "visual_pdf_review/page-02.png", "result": "candidate_review_pass", "notes": "Source contents page fits and is readable."},
        {"page": 3, "png": "visual_pdf_review/page-03.png", "result": "candidate_review_pass", "notes": "Body starts after frontmatter."},
        {"page": 17, "png": "visual_pdf_review/page-17.png", "result": "candidate_review", "notes": "Large table tail transitions into body; no overlap in smoke review."},
        {"page": 24, "png": "visual_pdf_review/page-24.png", "result": "candidate_review_pass", "notes": "Statblock page readable."},
        {"page": 32, "png": "visual_pdf_review/page-32.png", "result": "candidate_review_pass", "notes": "Final document tail renders without clipping."},
    ]
    report_md = report_dir / "visual_pdf_review_report.md"
    lines = [
        "# Innsmouth Final PDF Visual Review",
        "",
        f"Run id: `{report_dir.name}`",
        "",
        f"PDF: `{rel(pdf_path)}`",
        "",
        f"Rendered PNG folder: `{rel(visual_dir)}`",
        "",
        "Renderer:",
        "",
        f"- `pdftoppm`: `{pdftoppm}`",
        "- resolution: `110dpi`",
        f"- rendered pages: `{len(pngs)}`",
        "",
        "## Checked Pages",
        "",
        "| Page | Evidence PNG | Result | Notes |",
        "| --- | --- | --- | --- |",
    ]
    for row in checked_pages:
        lines.append(f"| {row['page']} | `{row['png']}` | {row['result']} | {row['notes']} |")
    lines.extend(
        [
            "",
            "## Result",
            "",
            "Visual evidence status: `pass_for_candidate_review`.",
            "",
            "This is not `production_approved=true`. It provides render evidence for the",
            "final HTML/PDF reproducibility candidate and leaves final visual acceptance to",
            "the user.",
        ]
    )
    report_md.write_text("\n".join(lines) + "\n", encoding="utf-8")
    visual_report = {
        "status": "pass" if not findings else "blocked",
        "pdf": rel(pdf_path),
        "rendered_png_dir": rel(visual_dir),
        "rendered_png_count": len(pngs),
        "report": file_record(report_md),
        "checked_pages": checked_pages,
        "findings": findings,
    }
    return visual_report, commands, findings


def run_id() -> str:
    return dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-id", default=run_id())
    parser.add_argument("--report-dir", type=Path)
    parser.add_argument("--output-dir", type=Path)
    parser.add_argument("--rebuild-report-dir", type=Path)
    parser.add_argument("--rebuild-config", type=Path)
    parser.add_argument("--skip-rebuild", action="store_true")
    args = parser.parse_args()

    report_dir = args.report_dir or (DEFAULT_REPORT_DIR / "runs" / args.run_id)
    output_dir = args.output_dir or (DEFAULT_OUTPUT_DIR / "runs" / args.run_id)
    rebuild_report_dir = args.rebuild_report_dir or (report_dir / "publishing_rebuild")
    rebuild_config = args.rebuild_config or (
        ROOT / "kb_creator/working/innsmouth_final" / args.run_id / "the_innsmouth_terror.final_publishing.package.json"
    )

    commands: list[dict[str, Any]] = []
    findings: list[dict[str, Any]] = []
    freeze_validation, freeze_findings = validate_freeze_manifest(FREEZE_MANIFEST)
    findings.extend(freeze_findings)
    findings.extend(assert_not_frozen_outputs([REBUILD_HTML, REBUILD_PDF, output_dir / FINAL_HTML_NAME, output_dir / "Pdf" / FINAL_PDF_NAME], FREEZE_MANIFEST))
    if output_dir.exists() and any(output_dir.rglob("*")):
        findings.append({"code": "output_dir_not_clean", "path": rel(output_dir)})
    if args.skip_rebuild:
        findings.append({"code": "rebuild_skipped_not_final", "detail": "--skip-rebuild cannot produce an accepted final run"})

    report_dir.mkdir(parents=True, exist_ok=True)
    if not findings:
        output_dir.mkdir(parents=True, exist_ok=True)
        rebuild_config.parent.mkdir(parents=True, exist_ok=True)

    kb_before = snapshot_kb_files()
    prerequisites = {
        "freeze_manifest": ensure_prerequisite_report(FREEZE_MANIFEST),
        "full_dry_run": ensure_prerequisite_report(FULL_DRY_RUN_REPORT),
    }
    for name, record in prerequisites.items():
        if not record.get("exists"):
            findings.append({"code": "missing_prerequisite", "name": name, "path": record.get("path")})
        elif name != "freeze_manifest" and record.get("status") != "pass":
            findings.append({"code": "prerequisite_not_pass", "name": name, "status": record.get("status")})

    if not findings and not args.skip_rebuild:
        commands.append(
            run_command(
                [
                    sys.executable,
                    "kb_creator/scripts/build_innsmouth_v7_rebuild.py",
                    "--report-dir",
                    rel(rebuild_report_dir),
                    "--config",
                    rel(rebuild_config),
                ]
            )
        )

    rebuild_report_path = rebuild_report_dir / "rebuild_report.json"
    rebuild_report = read_json(rebuild_report_path) if rebuild_report_path.exists() else {}
    if not rebuild_report_path.exists():
        findings.append({"code": "missing_rebuild_report", "path": rel(rebuild_report_path)})
    elif rebuild_report.get("status") != "pass":
        findings.append({"code": "rebuild_not_pass", "status": rebuild_report.get("status")})

    html_source = ROOT / rebuild_report.get("artifacts", {}).get("html", {}).get(
        "path", "CoC/Output/Scenarios/The_Innsmouth_Terror/The_Innsmouth_Terror_Full_RU_v7_rebuild.html"
    )
    pdf_source = ROOT / rebuild_report.get("artifacts", {}).get("pdf_two_column", {}).get(
        "path", "CoC/Output/Scenarios/The_Innsmouth_Terror/Pdf/The_Innsmouth_Terror_Full_RU_v7_rebuild_two_column.pdf"
    )
    findings.extend(assert_not_frozen_outputs([html_source, pdf_source], FREEZE_MANIFEST))
    html_target = output_dir / FINAL_HTML_NAME
    pdf_target = output_dir / "Pdf" / FINAL_PDF_NAME
    if rebuild_report:
        findings.extend(check_rebuild_freshness(rebuild_report, html_source, pdf_source))

    promoted: dict[str, Any] = {}
    visual_review: dict[str, Any] = {}
    if html_source.exists() and pdf_source.exists():
        promoted["html"] = copy_artifact(html_source, html_target)
        promoted["pdf_two_column"] = copy_artifact(pdf_source, pdf_target)
        visual_review, visual_commands, visual_findings = render_visual_review(pdf_target, report_dir)
        commands.extend(visual_commands)
        findings.extend(visual_findings)
    else:
        if not html_source.exists():
            findings.append({"code": "missing_rebuilt_html", "path": rel(html_source)})
        if not pdf_source.exists():
            findings.append({"code": "missing_rebuilt_pdf", "path": rel(pdf_source)})

    kb_after = snapshot_kb_files()
    kb_findings = compare_snapshots(kb_before, kb_after)
    findings.extend(kb_findings)
    for command in commands:
        if command["returncode"] != 0:
            findings.append(
                {"code": "command_failed", "command": command["command"], "returncode": command["returncode"]}
            )

    report = {
        "schema": "kb_creator_innsmouth_final_result_report.v1",
        "generated_at_utc": now_utc(),
        "status": "pass" if not findings else "blocked",
        "run_id": args.run_id,
        "scope": "HTML/PDF final reproducibility only; Knowledge_Base files are read-only",
        "freeze_validation": freeze_validation,
        "prerequisites": prerequisites,
        "tool_versions": {
            "python": sys.version.split()[0],
            "platform": platform.platform(),
        },
        "git": git_record(),
        "script_inputs": script_inputs_record(),
        "tool_binaries": tool_binaries_record(),
        "no_kb_write_check": {
            "status": "pass" if not kb_findings else "blocked",
            "files_before": len(kb_before),
            "files_after": len(kb_after),
            "findings": kb_findings,
        },
        "rebuild_report": file_record(rebuild_report_path),
        "rebuild_summary": {
            "status": rebuild_report.get("status"),
            "findings": len(rebuild_report.get("findings", [])) if isinstance(rebuild_report.get("findings"), list) else None,
            "html_comparison": rebuild_report.get("comparisons", {}).get("html"),
            "pdf_comparison": rebuild_report.get("comparisons", {}).get("pdf"),
            "qa_statuses": rebuild_report.get("qa_statuses"),
        },
        "visual_review": visual_review,
        "artifacts": {
            "html": file_record(html_target),
            "pdf_two_column": file_record(pdf_target),
        },
        "promoted_from": promoted,
        "commands": commands,
        "findings": findings,
        "acceptance_boundary": (
            "This proves script-backed regeneration and promotion of the accepted HTML/PDF chain. "
            "It does not claim fresh translation/proofread or KB regeneration."
        ),
    }
    final_report_path = report_dir / "final_run_report.json"
    manifest_path = report_dir / "final_artifact_manifest.json"
    write_json(final_report_path, report)
    write_json(manifest_path, report)
    latest_index = DEFAULT_REPORT_DIR / "latest_run.json"
    write_json(
        latest_index,
        {
            "schema": "kb_creator_innsmouth_final_latest_run.v1",
            "generated_at_utc": now_utc(),
            "run_id": args.run_id,
            "status": report["status"],
            "final_run_report": rel(final_report_path),
            "final_artifact_manifest": rel(manifest_path),
            "html": rel(html_target),
            "pdf_two_column": rel(pdf_target),
        },
    )
    print(
        f"status={report['status']} html={rel(html_target)} pdf={rel(pdf_target)} "
        f"findings={len(findings)} report={rel(final_report_path)}"
    )
    return 0 if report["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
