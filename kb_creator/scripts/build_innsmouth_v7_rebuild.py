from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_MANIFEST = ROOT / "kb_creator/inputs/innsmouth_v6_freeze_manifest.json"
DEFAULT_REPORT_DIR = ROOT / "kb_creator/reports/innsmouth_v7_rebuild"
DEFAULT_CONFIG = ROOT / "kb_creator/working/the_innsmouth_terror.v7_rebuild.package.json"


def now_utc() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat()


def rel(path: Path) -> str:
    try:
        return path.resolve().relative_to(ROOT.resolve()).as_posix()
    except ValueError:
        return path.as_posix()


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


def run_command(command: list[str], *, env: dict[str, str] | None = None) -> dict[str, Any]:
    started = now_utc()
    completed = subprocess.run(
        command,
        cwd=ROOT,
        env=env,
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


def replace_text(value: Any, replacements: dict[str, str]) -> Any:
    if isinstance(value, str):
        for old, new in replacements.items():
            value = value.replace(old, new)
        return value
    if isinstance(value, list):
        return [replace_text(item, replacements) for item in value]
    if isinstance(value, dict):
        return {key: replace_text(item, replacements) for key, item in value.items()}
    return value


def load_baseline_config(manifest: dict[str, Any]) -> dict[str, Any]:
    config_path = ROOT / manifest["artifacts"]["config"]
    return read_json(config_path)


def make_v7_config(manifest: dict[str, Any], report_dir: Path) -> tuple[dict[str, Any], dict[str, str]]:
    config = load_baseline_config(manifest)
    replacements = {
        "The_Innsmouth_Terror_Full_RU_v6.html": "The_Innsmouth_Terror_Full_RU_v7_rebuild.html",
        "The_Innsmouth_Terror_Full_RU_v6_two_column.pdf": "The_Innsmouth_Terror_Full_RU_v7_rebuild_two_column.pdf",
        "production_html_report_v6.json": "production_html_report_v7_rebuild.json",
        "html_v6_statblock_projection_report.json": "html_v7_rebuild_statblock_projection_report.json",
        "production_pdf_report_v6_two_column.json": "production_pdf_report_v7_rebuild_two_column.json",
        "pdf_print_qa_two_column.json": "pdf_print_qa_v7_rebuild_two_column.json",
        "positive_content_audit.v1.json": "positive_content_audit_v7_rebuild.json",
        "positive_content_audit.v1.md": "positive_content_audit_v7_rebuild.md",
        "coc_mechanics_audit.v1.json": "coc_mechanics_audit_v7_rebuild.json",
        "coc_mechanics_audit.v1.md": "coc_mechanics_audit_v7_rebuild.md",
        "art_layout_qa.json": "art_layout_qa_v7_rebuild.json",
        "semantic_chain_audit.v1.json": "semantic_chain_audit_v7_rebuild.json",
        "semantic_chain_audit.v1.md": "semantic_chain_audit_v7_rebuild.md",
        "frontmatter_manifest.json": "frontmatter_manifest_v7_rebuild.json",
    }
    config = replace_text(config, replacements)
    config["project_key"] = "The_Innsmouth_Terror_v7_rebuild"
    config["workbench_qa_root"] = "."
    config["rebuild_proof"] = {
        "mode": "kb_creator_v7_rebuild",
        "baseline_manifest": rel(DEFAULT_MANIFEST),
        "baseline_commit": manifest.get("baseline_commit"),
        "generated_at_utc": now_utc(),
    }
    # Put newly generated reports beside the v7 config while keeping source and
    # accepted content inputs pointed at the frozen v6 artifacts.
    for section_name in (
        "production_html",
        "production_pdf",
        "positive_content_audit",
        "coc_mechanics_audit",
        "semantic_chain_audit",
        "frontmatter",
        "production_art_layout",
    ):
        section = config.get(section_name)
        if isinstance(section, dict) and isinstance(section.get("report"), str):
            section["report"] = Path(section["report"]).name
    config.setdefault("production_art_layout", {})["report"] = "art_layout_qa_v7_rebuild.json"
    config["production_art_layout"]["art_manifest"] = str(
        ROOT / "CoC/Working/Scenarios/The_Innsmouth_Terror/project/QA/Recovery_v6/art_manifest.json"
    )
    config["production_art_layout"][
        "integration_manifest"
    ] = str(ROOT / "CoC/Working/Scenarios/The_Innsmouth_Terror/project/QA/Recovery_v6/art_html_integration_manifest.json")
    config.setdefault("art_integration", {})["placement_manifest"] = str(
        ROOT / "CoC/Working/Scenarios/The_Innsmouth_Terror/project/QA/Recovery_v6/art_manifest.json"
    )
    config.setdefault("production_html", {})["report"] = "production_html_report_v7_rebuild.json"
    config.setdefault("production_pdf", {}).setdefault("variants", {}).setdefault("two_column", {})[
        "report"
    ] = "production_pdf_report_v7_rebuild_two_column.json"
    config["production_pdf"]["report"] = "production_pdf_report_v7_rebuild.json"
    config["positive_content_audit"]["report"] = "positive_content_audit_v7_rebuild.json"
    config["positive_content_audit"]["markdown_report"] = "positive_content_audit_v7_rebuild.md"
    config["coc_mechanics_audit"]["report"] = "coc_mechanics_audit_v7_rebuild.json"
    config["coc_mechanics_audit"]["markdown_report"] = "coc_mechanics_audit_v7_rebuild.md"
    config["semantic_chain_audit"]["report"] = "semantic_chain_audit_v7_rebuild.json"
    config["semantic_chain_audit"]["markdown_report"] = "semantic_chain_audit_v7_rebuild.md"
    config["frontmatter"]["report"] = "frontmatter_manifest_v7_rebuild.json"
    config["production_pdf"]["temp_root"] = str(args_config_temp_root(config, report_dir))
    config["pdf_print_qa"] = {
        "report": "pdf_print_qa_v7_rebuild.json",
        "variant_reports": {"two_column": "pdf_print_qa_v7_rebuild_two_column.json"},
    }
    return config, replacements


def args_config_temp_root(config: dict[str, Any], report_dir: Path) -> Path:
    """Keep dry-run PDF render scratch files inside the rebuild workspace."""
    configured_html = str(config.get("production_html", {}).get("output_html", ""))
    if "kb_creator/working/innsmouth_full_dry_run" in configured_html.replace("\\", "/"):
        return ROOT / "kb_creator/working/innsmouth_full_dry_run/Production_PDF_Temp_v7_rebuild"
    return report_dir / "Production_PDF_Temp_v7_rebuild"


def normalize_html(text: str) -> str:
    text = re.sub(r"generated_at_utc[^,\n<]+", "generated_at_utc", text)
    text = re.sub(r"v7_rebuild", "vX", text)
    text = re.sub(r"v6", "vX", text)
    return re.sub(r"\s+", " ", text).strip()


def text_from_html(text: str) -> str:
    text = re.sub(r"<script\b[\s\S]*?</script>", " ", text, flags=re.I)
    text = re.sub(r"<style\b[\s\S]*?</style>", " ", text, flags=re.I)
    text = re.sub(r"<[^>]+>", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def normalize_reader_text(text: str) -> str:
    for marker in (
        "The_Innsmouth_Terror_recovery_v6_cleaned",
        "The_Innsmouth_Terror_v7_rebuild",
    ):
        text = text.replace(marker, "PROJECT_KEY")
    return re.sub(r"\s+", " ", text).strip()


def compare_html(baseline_path: Path, rebuild_path: Path) -> dict[str, Any]:
    baseline = baseline_path.read_text(encoding="utf-8")
    rebuild = rebuild_path.read_text(encoding="utf-8")
    baseline_text = text_from_html(baseline)
    rebuild_text = text_from_html(rebuild)
    baseline_reader_text = normalize_reader_text(baseline_text)
    rebuild_reader_text = normalize_reader_text(rebuild_text)
    return {
        "baseline": rel(baseline_path),
        "rebuild": rel(rebuild_path),
        "byte_identical": baseline == rebuild,
        "normalized_html_identical": normalize_html(baseline) == normalize_html(rebuild),
        "visible_text_identical": baseline_text == rebuild_text,
        "reader_visible_text_identical": baseline_reader_text == rebuild_reader_text,
        "baseline_sha256": sha256_file(baseline_path),
        "rebuild_sha256": sha256_file(rebuild_path),
        "baseline_visible_text_sha256": hashlib.sha256(baseline_text.encode("utf-8")).hexdigest(),
        "rebuild_visible_text_sha256": hashlib.sha256(rebuild_text.encode("utf-8")).hexdigest(),
        "baseline_reader_visible_text_sha256": hashlib.sha256(baseline_reader_text.encode("utf-8")).hexdigest(),
        "rebuild_reader_visible_text_sha256": hashlib.sha256(rebuild_reader_text.encode("utf-8")).hexdigest(),
        "baseline_img_count": len(re.findall(r"<img\b", baseline, flags=re.I)),
        "rebuild_img_count": len(re.findall(r"<img\b", rebuild, flags=re.I)),
        "baseline_table_count": len(re.findall(r"<table\b", baseline, flags=re.I)),
        "rebuild_table_count": len(re.findall(r"<table\b", rebuild, flags=re.I)),
        "baseline_statblock_count": len(re.findall(r'class="[^"]*\bstatblock-card\b', baseline)),
        "rebuild_statblock_count": len(re.findall(r'class="[^"]*\bstatblock-card\b', rebuild)),
    }


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


def status_of(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {"path": rel(path), "exists": False, "status": "missing"}
    data = read_json(path)
    return {
        "path": rel(path),
        "exists": True,
        "status": data.get("status"),
        "findings": len(data.get("findings", [])) if isinstance(data.get("findings"), list) else data.get("findings"),
        "warnings": len(data.get("warnings", [])) if isinstance(data.get("warnings"), list) else data.get("warnings"),
        "sha256": sha256_file(path),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--report-dir", type=Path, default=DEFAULT_REPORT_DIR)
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--skip-pdf", action="store_true")
    args = parser.parse_args()

    manifest = read_json(args.manifest)
    report_dir = args.report_dir
    report_dir.mkdir(parents=True, exist_ok=True)
    args.config.parent.mkdir(parents=True, exist_ok=True)

    config, _ = make_v7_config(manifest, report_dir)
    write_json(args.config, config)

    html_path = ROOT / config["production_html"]["output_html"]
    pdf_path = ROOT / config["production_pdf"]["variants"]["two_column"]["output_pdf"]
    qa_root = args.config.parent

    commands: list[dict[str, Any]] = []
    base = [sys.executable, "translator/translator.py"]
    commands.append(run_command([*base, "build-production-html", "--config", rel(args.config), "--force"]))

    stat_env = os.environ.copy()
    stat_env["INNSMOUTH_HTML"] = str(html_path)
    stat_env["INNSMOUTH_QA"] = str(qa_root)
    stat_env["INNSMOUTH_STATBLOCK_REPORT"] = str(qa_root / "html_v7_rebuild_statblock_projection_report.json")
    commands.append(
        run_command(
            [sys.executable, "CoC/Working/Scenarios/The_Innsmouth_Terror/project/scripts/apply_statblock_projection_to_html_v3.py"],
            env=stat_env,
        )
    )

    for stage in ("positive-content-audit", "coc-mechanics-audit", "art-layout-qa"):
        commands.append(run_command([*base, stage, "--config", rel(args.config), "--check-only"]))

    if not args.skip_pdf:
        commands.append(
            run_command([*base, "build-production-pdf", "--config", rel(args.config), "--variant", "two_column"])
        )
        commands.append(run_command([*base, "pdf-print-qa", "--config", rel(args.config), "--variant", "two_column", "--check-only"]))

    baseline_html = ROOT / manifest["artifacts"]["html"]
    baseline_pdf = ROOT / manifest["artifacts"]["pdf_two_column"]
    report_paths = {
        "production_html": qa_root / "production_html_report_v7_rebuild.json",
        "statblock_projection": qa_root / "html_v7_rebuild_statblock_projection_report.json",
        "positive_content": qa_root / "positive_content_audit_v7_rebuild.json",
        "coc_mechanics": qa_root / "coc_mechanics_audit_v7_rebuild.json",
        "art_layout": qa_root / "art_layout_qa_v7_rebuild.json",
        "production_pdf": qa_root / "production_pdf_report_v7_rebuild_two_column.json",
        "pdf_print": qa_root / "pdf_print_qa_v7_rebuild_two_column.json",
    }
    qa_statuses = {name: status_of(path) for name, path in report_paths.items()}
    html_comparison = compare_html(baseline_html, html_path) if html_path.exists() else {"error": "missing_v7_html"}
    pdf_comparison = {
        "baseline": rel(baseline_pdf),
        "rebuild": rel(pdf_path),
        "byte_identical": baseline_pdf.exists() and pdf_path.exists() and sha256_file(baseline_pdf) == sha256_file(pdf_path),
        "baseline_sha256": sha256_file(baseline_pdf) if baseline_pdf.exists() else None,
        "rebuild_sha256": sha256_file(pdf_path) if pdf_path.exists() else None,
    }
    blocker_findings: list[dict[str, Any]] = []
    for command in commands:
        if command["returncode"] != 0:
            blocker_findings.append({"code": "command_failed", "command": command["command"], "returncode": command["returncode"]})
    for name, status in qa_statuses.items():
        if status.get("exists") is False:
            blocker_findings.append({"code": "missing_qa_report", "name": name, "path": status.get("path")})
        elif status.get("status") not in {"pass", "ok"}:
            blocker_findings.append({"code": "qa_not_pass", "name": name, "status": status.get("status")})
    if not html_comparison.get("reader_visible_text_identical"):
        blocker_findings.append({"code": "html_visible_text_differs"})
    if html_comparison.get("baseline_img_count") != html_comparison.get("rebuild_img_count"):
        blocker_findings.append({"code": "html_image_count_differs"})
    if html_comparison.get("baseline_table_count") != html_comparison.get("rebuild_table_count"):
        blocker_findings.append({"code": "html_table_count_differs"})
    if html_comparison.get("baseline_statblock_count") != html_comparison.get("rebuild_statblock_count"):
        blocker_findings.append({"code": "html_statblock_count_differs"})

    report = {
        "schema": "kb_creator_innsmouth_v7_rebuild_report.v1",
        "generated_at_utc": now_utc(),
        "status": "pass" if not blocker_findings else "blocked",
        "baseline_manifest": rel(args.manifest),
        "baseline_commit": manifest.get("baseline_commit"),
        "config": file_record(args.config),
        "artifacts": {
            "html": file_record(html_path),
            "pdf_two_column": file_record(pdf_path),
        },
        "qa_statuses": qa_statuses,
        "comparisons": {
            "html": html_comparison,
            "pdf": pdf_comparison,
        },
        "commands": commands,
        "findings": blocker_findings,
    }
    report_path = report_dir / "rebuild_report.json"
    write_json(report_path, report)
    print(
        f"status={report['status']} html={rel(html_path)} pdf={rel(pdf_path)} "
        f"findings={len(blocker_findings)} report={rel(report_path)}"
    )
    return 0 if report["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
