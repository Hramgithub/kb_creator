from __future__ import annotations

import argparse
import copy
import datetime as dt
import hashlib
import importlib.util
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
SCENARIO_ROOT = ROOT / "CoC/Working/Scenarios/The_Innsmouth_Terror"
SOURCE_BUILDER = SCENARIO_ROOT / "project/scripts/build_pymupdf_source_candidate.py"
READING_ORDER = SCENARIO_ROOT / "project/scripts/build_recovery_v6_reading_order_evidence.py"
SOURCE_CLEANUP = SCENARIO_ROOT / "project/scripts/build_recovery_v6_cleaned_source_candidate.py"
PUBLISHING_REBUILD = ROOT / "kb_creator/scripts/build_innsmouth_v7_rebuild.py"
BASELINE_CONFIG = SCENARIO_ROOT / "project/QA/Recovery_v6/the_innsmouth_terror.recovery_v6_cleaned.package.json"
SOURCE_PDF = Path(
    r"D:\яндекс\Yandex.Disk\НРИ\1_Зов Ктулху\english\7th Edition Call of Cthulhu\Adventures\1923_The Innsmouth Terror\The Innsmouth terror.pdf"
)
ACCEPTED_V6_EN = SCENARIO_ROOT / "Formatted/The_Innsmouth_Terror_Source_Text_Full_EN_v6_cleaned.md"
ACCEPTED_V2_EN = SCENARIO_ROOT / "Formatted/The_Innsmouth_Terror_Source_Text_Full_EN_v2.md"
ACCEPTED_V6_RAW_EN = SCENARIO_ROOT / "Formatted/The_Innsmouth_Terror_Source_Text_Full_EN_v6.md"
DEFAULT_REPORT_DIR = ROOT / "kb_creator/reports/innsmouth_full_dry_run"
DEFAULT_VERSION = "kb_full_dry_run_v1"
DEFAULT_CLEAN_VERSION = "kb_full_dry_run_cleaned_v1"
DEFAULT_ACCEPTED_CLEAN_VERSION = "kb_full_dry_run_accepted_cleaned_v1"
EXPECTED_SOURCE_SHA256 = "CFD72DD3B8702C07750DCBB9F721A704793D6D474167B288922E6F7EBEEA561F"
EXPECTED_SOURCE_BYTES = 71396612


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


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def normalize_source_text(text: str) -> str:
    text = re.sub(r"^# The Innsmouth Terror - Full EN Source Candidate .*$", "# SOURCE TITLE", text, flags=re.M)
    text = re.sub(r"<!-- generated-by:[^>]+-->", "<!-- generated-by -->", text)
    text = re.sub(r"<!-- source-method:[^>]+-->", "<!-- source-method -->", text)
    return re.sub(r"\s+", " ", text).strip()


def page_markers(text: str) -> list[str]:
    return re.findall(r"<!--\s*source-page-(\d{3})\s*-->", text)


def command_record(command: list[str]) -> dict[str, Any]:
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


def cleanup_command_record(raw_source: Path, clean_source: Path, report_dir: Path) -> dict[str, Any]:
    started = now_utc()
    stdout = ""
    stderr = ""
    returncode = 0
    try:
        sys.path.insert(0, str(SOURCE_CLEANUP.parent))
        spec = importlib.util.spec_from_file_location("innsmouth_source_cleanup_backend", SOURCE_CLEANUP)
        if spec is None or spec.loader is None:
            raise RuntimeError(f"cannot load cleanup backend: {SOURCE_CLEANUP}")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        module.RAW_FULL_EN = raw_source
        module.REFERENCE_FULL_EN_V2 = ACCEPTED_V2_EN
        module.CLEAN_FULL_EN = clean_source
        module.QA_V6 = report_dir
        module.CLEAN_PAGES_DIR = report_dir / "Cleaned_Source_Pages_v1"
        module.CLEAN_SOURCE_MANIFEST = report_dir / "source_block_manifest.cleaned.v2.json"
        module.CLEAN_CANDIDATE_MANIFEST = report_dir / "candidate_block_manifest.cleaned.v2.json"
        module.CLEAN_CONFIG = report_dir / "the_innsmouth_terror.full_dry_run_cleaned.package.json"
        module.CLEAN_REPORT_JSON = report_dir / "source_cleanup_report.v1.json"
        module.CLEAN_REPORT_MD = report_dir / "source_cleanup_report.v1.md"
        module.main()
        stdout = f"status=created output={rel(clean_source)} report={rel(module.CLEAN_REPORT_JSON)}\n"
    except Exception as exc:  # pragma: no cover - recorded as dry-run evidence.
        returncode = 1
        stderr = f"{type(exc).__name__}: {exc}"
    finally:
        try:
            sys.path.remove(str(SOURCE_CLEANUP.parent))
        except ValueError:
            pass
    return {
        "command": [
            sys.executable,
            rel(SOURCE_CLEANUP),
            "--kb-creator-wrapper",
            "--raw-source",
            rel(raw_source),
            "--clean-source",
            rel(clean_source),
            "--report-dir",
            rel(report_dir),
        ],
        "started_at_utc": started,
        "finished_at_utc": now_utc(),
        "returncode": returncode,
        "stdout": stdout[-8000:],
        "stderr": stderr[-8000:],
    }


def accepted_cleaned_delta_command_record(clean_source: Path, accepted_clean_source: Path, report_dir: Path) -> dict[str, Any]:
    started = now_utc()
    stdout = ""
    stderr = ""
    returncode = 0
    replacements = [
        {
            "code": "restore_evening_second_day",
            "old": "Evening of the\nThe Epic finale begins filming.",
            "new": "Evening of the 2nd day\nThe Epic finale begins filming.",
        },
        {
            "code": "remove_page_007_ocr_noise",
            "old": "\n(G YBER’ NO L7H)\nDerr or (i 2 Wis ty ee\n\n<!-- source-page-008 -->",
            "new": "\n\n<!-- source-page-008 -->",
        },
        {
            "code": "join_bazzledon_leader_line",
            "old": "broken. At night his dreams are wracked by Mother Hydra, the\n\n. leader of the Deep Ones.",
            "new": "broken. At night his dreams are wracked by Mother Hydra, the\nleader of the Deep Ones.",
        },
        {
            "code": "remove_page_008_ocr_noise",
            "old": "\n\n4 _ ” \"\n\n- rs »\n\nGenevieve ‘Ginny’ Dubois",
            "new": "\n\nGenevieve ‘Ginny’ Dubois",
        },
        {
            "code": "restore_playing_the_hero_reference",
            "old": "Epic Finale (page 25) atop the cliff face, for the Playing the\n\n— ot 0 }\n\n<!-- source-page-029 -->",
            "new": "Epic Finale (page 25) atop the cliff face, for the Playing the\nHero (page 27) outcome.\n\n<!-- source-page-029 -->",
        },
        {
            "code": "repair_patty_statline_spacing",
            "old": "STR50 CON55_ SIZ65 DEX 75 INT70",
            "new": "STR50 CON55 SIZ65 DEX 75 INT70",
        },
        {
            "code": "repair_patty_traits_bullet",
            "old": "- — Traits: direct and forceful.",
            "new": "- Traits: direct and forceful.",
        },
        {
            "code": "remove_page_037_ocr_noise",
            "old": "\nFor a further scenario featuring Patty, see Secret Santa by TA\nNewman.\n4 ‘ sg x\n\n<!-- source-page-038 -->",
            "new": "\nFor a further scenario featuring Patty, see Secret Santa by TA\nNewman.\n\n<!-- source-page-038 -->",
        },
        {
            "code": "repair_quechua",
            "old": "Language (Quechuah)",
            "new": "Language (Quechua)",
        },
    ]
    applied: list[dict[str, Any]] = []
    try:
        text = clean_source.read_text(encoding="utf-8")
        before_sha = hashlib.sha256(text.encode("utf-8")).hexdigest()
        for item in replacements:
            count = text.count(item["old"])
            if count != 1:
                raise RuntimeError(f"{item['code']} expected 1 match, found {count}")
            text = text.replace(item["old"], item["new"], 1)
            applied.append({"code": item["code"], "count": count})
        accepted_clean_source.parent.mkdir(parents=True, exist_ok=True)
        accepted_clean_source.write_text(text, encoding="utf-8", newline="\n")
        after_sha = hashlib.sha256(text.encode("utf-8")).hexdigest()
        report = {
            "schema": "kb_creator.accepted_cleaned_delta.v1",
            "generated_at_utc": now_utc(),
            "status": "pass",
            "input": rel(clean_source),
            "output": rel(accepted_clean_source),
            "input_sha256": before_sha,
            "output_sha256": after_sha,
            "applied": applied,
        }
        write_json(report_dir / "accepted_cleaned_delta_report.json", report)
        stdout = f"status=pass output={rel(accepted_clean_source)} replacements={len(applied)}\n"
    except Exception as exc:  # pragma: no cover - recorded as dry-run evidence.
        returncode = 1
        stderr = f"{type(exc).__name__}: {exc}"
        write_json(
            report_dir / "accepted_cleaned_delta_report.json",
            {
                "schema": "kb_creator.accepted_cleaned_delta.v1",
                "generated_at_utc": now_utc(),
                "status": "blocked",
                "input": rel(clean_source),
                "output": rel(accepted_clean_source),
                "applied": applied,
                "error": stderr,
            },
        )
    return {
        "command": [
            sys.executable,
            rel(Path(__file__)),
            "--accepted-cleaned-delta",
            "--clean-source",
            rel(clean_source),
            "--accepted-clean-source",
            rel(accepted_clean_source),
            "--report-dir",
            rel(report_dir),
        ],
        "started_at_utc": started,
        "finished_at_utc": now_utc(),
        "returncode": returncode,
        "stdout": stdout[-8000:],
        "stderr": stderr[-8000:],
    }


def compare_source(candidate: Path, accepted: Path) -> dict[str, Any]:
    if not candidate.exists() or not accepted.exists():
        return {
            "candidate": rel(candidate),
            "accepted": rel(accepted),
            "exists": False,
            "identical": False,
        }
    candidate_text = read_text(candidate)
    accepted_text = read_text(accepted)
    candidate_norm = normalize_source_text(candidate_text)
    accepted_norm = normalize_source_text(accepted_text)
    return {
        "candidate": rel(candidate),
        "accepted": rel(accepted),
        "exists": True,
        "byte_identical": sha256_file(candidate) == sha256_file(accepted),
        "normalized_source_identical": candidate_norm == accepted_norm,
        "candidate_sha256": sha256_file(candidate),
        "accepted_sha256": sha256_file(accepted),
        "candidate_normalized_sha256": hashlib.sha256(candidate_norm.encode("utf-8")).hexdigest(),
        "accepted_normalized_sha256": hashlib.sha256(accepted_norm.encode("utf-8")).hexdigest(),
        "candidate_chars": len(candidate_text),
        "accepted_chars": len(accepted_text),
        "candidate_pages": page_markers(candidate_text),
        "accepted_pages": page_markers(accepted_text),
        "candidate_page_count": len(page_markers(candidate_text)),
        "accepted_page_count": len(page_markers(accepted_text)),
    }


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def make_column_ocr_config(config_path: Path, report_dir: Path) -> dict[str, Any]:
    config = copy.deepcopy(read_json(BASELINE_CONFIG))
    working = ROOT / "kb_creator/working/innsmouth_full_dry_run"
    qa = working / "qa"
    config["project_key"] = "The_Innsmouth_Terror_kb_full_dry_run"
    config["workbench_qa_root"] = rel(qa)
    config["source_pdf"] = str(SOURCE_PDF)
    config["source_pdf_original_external"] = str(SOURCE_PDF)
    config["source_pdf_working"] = str(SOURCE_PDF)
    intake = config.setdefault("intake", {})
    intake["page_renders"] = rel(working / "Images/Page_Renders")
    intake["embedded_images"] = rel(working / "Images/PDF_Extracted_All")
    intake["raw_text"] = rel(working / "Formatted/The_Innsmouth_Terror_Source_Text_Raw_EN_kb_full_dry_run.txt")
    intake["ocr_text"] = rel(working / "Formatted/The_Innsmouth_Terror_Source_Text_OCR_EN_kb_full_dry_run.md")
    intake["normalized_text"] = rel(working / "Formatted/The_Innsmouth_Terror_Source_Text_Normalized_EN_kb_full_dry_run.md")
    column = config.setdefault("column_ocr_reconstruction", {})
    column["candidate_markdown"] = rel(
        working / "Translation_Work/Column_OCR_Reconstruction/The_Innsmouth_Terror_Column_OCR_Candidate_EN_kb_full_dry_run.md"
    )
    column["page_chunk_dir"] = rel(working / "Translation_Work/Column_OCR_Reconstruction/Source_Pages")
    column["crop_dir"] = rel(working / "QA/Column_OCR")
    column["report"] = "column_ocr_reconstruction_report.json"
    config["dry_run_proof"] = {
        "mode": "kb_creator_full_dry_run",
        "generated_at_utc": now_utc(),
        "baseline_config": rel(BASELINE_CONFIG),
    }
    write_json(config_path, config)
    return config


def reading_order_command_record(column_candidate: Path, column_report: Path, raw_source: Path, report_dir: Path) -> dict[str, Any]:
    started = now_utc()
    stdout = ""
    stderr = ""
    returncode = 0
    try:
        sys.path.insert(0, str(READING_ORDER.parent))
        spec = importlib.util.spec_from_file_location("innsmouth_reading_order_backend", READING_ORDER)
        if spec is None or spec.loader is None:
            raise RuntimeError(f"cannot load reading-order backend: {READING_ORDER}")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        module.QA_V6 = report_dir
        module.COLUMN_REPORT = column_report
        module.COLUMN_CANDIDATE = column_candidate
        module.OLD_FULL_EN = ACCEPTED_V2_EN
        module.FULL_EN_V6 = raw_source
        module.VISUAL_ONLY = {"001", "045", "046"}
        module.CONFIG_V6 = report_dir / "the_innsmouth_terror.full_dry_run_raw_v6.package.json"
        module.SOURCE_MANIFEST = report_dir / "source_block_manifest.v2.json"
        module.CANDIDATE_MANIFEST = report_dir / "candidate_block_manifest.v2.json"
        module.OLD_CANDIDATE_MANIFEST = report_dir / "old_full_en_candidate_block_manifest.v2.json"
        module.REPORT = report_dir / "reading_order_evidence_build.v1.json"
        module.main()
        stdout = f"status=created output={rel(raw_source)} report={rel(module.REPORT)}\n"
    except Exception as exc:  # pragma: no cover - recorded as dry-run evidence.
        returncode = 1
        stderr = f"{type(exc).__name__}: {exc}"
    finally:
        try:
            sys.path.remove(str(READING_ORDER.parent))
        except ValueError:
            pass
    return {
        "command": [
            sys.executable,
            rel(READING_ORDER),
            "--kb-creator-wrapper",
            "--column-candidate",
            rel(column_candidate),
            "--column-report",
            rel(column_report),
            "--raw-source",
            rel(raw_source),
            "--report-dir",
            rel(report_dir),
        ],
        "started_at_utc": started,
        "finished_at_utc": now_utc(),
        "returncode": returncode,
        "stdout": stdout[-8000:],
        "stderr": stderr[-8000:],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--version", default=DEFAULT_VERSION)
    parser.add_argument("--clean-version", default=DEFAULT_CLEAN_VERSION)
    parser.add_argument("--report-dir", type=Path, default=DEFAULT_REPORT_DIR)
    parser.add_argument("--skip-column-ocr", action="store_true")
    parser.add_argument("--skip-pymupdf", action="store_true")
    parser.add_argument("--skip-cleanup", action="store_true")
    parser.add_argument("--skip-accepted-cleaned-delta", action="store_true")
    parser.add_argument("--skip-publishing", action="store_true")
    args = parser.parse_args()

    report_dir = args.report_dir
    report_dir.mkdir(parents=True, exist_ok=True)
    working = ROOT / "kb_creator/working/innsmouth_full_dry_run"
    qa_dir = working / "qa"
    config_path = working / "the_innsmouth_terror.full_dry_run.package.json"
    qa_root = "project/QA/kb_creator_full_dry_run"
    pymupdf_candidate = SCENARIO_ROOT / "Formatted" / f"The_Innsmouth_Terror_Source_Text_Full_EN_{args.version}.md"
    raw_v6_candidate = working / "The_Innsmouth_Terror_Source_Text_Full_EN_kb_full_dry_run_raw_v6.md"
    cleaned_candidate = ROOT / "kb_creator/working/innsmouth_full_dry_run" / (
        f"The_Innsmouth_Terror_Source_Text_Full_EN_{args.clean_version}.md"
    )
    accepted_cleaned_candidate = ROOT / "kb_creator/working/innsmouth_full_dry_run" / (
        f"The_Innsmouth_Terror_Source_Text_Full_EN_{DEFAULT_ACCEPTED_CLEAN_VERSION}.md"
    )
    builder_report = SCENARIO_ROOT / qa_root / f"source_full_en_candidate_report_{args.version}.json"

    findings: list[dict[str, Any]] = []
    commands: list[dict[str, Any]] = []

    source_record = file_record(SOURCE_PDF)
    if not source_record["exists"]:
        findings.append({"code": "missing_source_pdf", "path": str(SOURCE_PDF)})
    else:
        if source_record["size_bytes"] != EXPECTED_SOURCE_BYTES:
            findings.append(
                {
                    "code": "source_pdf_size_mismatch",
                    "expected": EXPECTED_SOURCE_BYTES,
                    "actual": source_record["size_bytes"],
                }
            )
        if str(source_record["sha256"]).upper() != EXPECTED_SOURCE_SHA256:
            findings.append(
                {
                    "code": "source_pdf_hash_mismatch",
                    "expected": EXPECTED_SOURCE_SHA256,
                    "actual": str(source_record["sha256"]).upper(),
                }
            )

    config = make_column_ocr_config(config_path, report_dir)
    column_candidate = ROOT / config["column_ocr_reconstruction"]["candidate_markdown"]
    column_report = working / config["column_ocr_reconstruction"].get("report", "column_ocr_reconstruction_report.json")

    if not findings and not args.skip_column_ocr:
        base = [sys.executable, "translator/translator.py"]
        commands.append(command_record([*base, "render-pages", "--config", rel(config_path), "--force"]))
        commands.append(command_record([*base, "reconstruct-column-ocr", "--config", rel(config_path), "--force", "--apply"]))

    if not findings:
        commands.append(reading_order_command_record(column_candidate, column_report, raw_v6_candidate, report_dir / "reading_order"))

    if not findings and not args.skip_pymupdf:
        commands.append(
            command_record(
                [
                    sys.executable,
                    rel(SOURCE_BUILDER),
                    "--version",
                    args.version,
                    "--qa-root",
                    qa_root,
                ]
            )
        )

    cleanup_attempted = False
    if not findings and not args.skip_cleanup:
        cleanup_attempted = True
        cleanup_input = raw_v6_candidate if raw_v6_candidate.exists() else pymupdf_candidate
        commands.append(cleanup_command_record(cleanup_input, cleaned_candidate, report_dir / "source_cleanup"))

    accepted_cleaned_delta_attempted = False
    if not findings and not args.skip_accepted_cleaned_delta and cleaned_candidate.exists():
        accepted_cleaned_delta_attempted = True
        commands.append(
            accepted_cleaned_delta_command_record(
                cleaned_candidate,
                accepted_cleaned_candidate,
                report_dir / "accepted_cleaned_delta",
            )
        )

    publishing_attempted = False
    publishing_report_path = report_dir / "publishing_rebuild/rebuild_report.json"
    publishing_config_path = working / "the_innsmouth_terror.full_dry_run_publishing.package.json"
    if not findings and not args.skip_publishing:
        raw_precheck = compare_source(raw_v6_candidate, ACCEPTED_V6_RAW_EN)
        accepted_cleaned_precheck = compare_source(accepted_cleaned_candidate, ACCEPTED_V6_EN)
        if raw_precheck.get("normalized_source_identical") and accepted_cleaned_precheck.get(
            "normalized_source_identical"
        ):
            publishing_attempted = True
            commands.append(
                command_record(
                    [
                        sys.executable,
                        rel(PUBLISHING_REBUILD),
                        "--report-dir",
                        rel(publishing_report_path.parent),
                        "--config",
                        rel(publishing_config_path),
                    ]
                )
            )

    pymupdf_vs_v6 = compare_source(pymupdf_candidate, ACCEPTED_V6_EN)
    pymupdf_vs_v2 = compare_source(pymupdf_candidate, ACCEPTED_V2_EN)
    raw_v6_vs_accepted_raw = compare_source(raw_v6_candidate, ACCEPTED_V6_RAW_EN)
    raw_v6_vs_accepted_cleaned = compare_source(raw_v6_candidate, ACCEPTED_V6_EN)
    cleanup_vs_v6 = compare_source(cleaned_candidate, ACCEPTED_V6_EN)
    accepted_cleaned_vs_v6 = compare_source(accepted_cleaned_candidate, ACCEPTED_V6_EN)
    for command in commands:
        if command["returncode"] != 0:
            findings.append({"code": "command_failed", "command": command["command"], "returncode": command["returncode"]})

    raw_source_gate_passed = bool(raw_v6_vs_accepted_raw.get("normalized_source_identical"))
    cleaned_source_gate_passed = bool(accepted_cleaned_vs_v6.get("normalized_source_identical"))
    source_gate_passed = raw_source_gate_passed and cleaned_source_gate_passed
    if not raw_source_gate_passed:
        findings.append(
            {
                "code": "fresh_raw_source_differs_from_accepted_raw_v6",
                "detail": "Publishing is blocked until PDF/render/OCR/reading-order reconstruction reproduces accepted raw v6.",
            }
        )
    elif not cleaned_source_gate_passed:
        findings.append(
            {
                "code": "accepted_cleaned_source_has_unreproduced_post_cleanup_edits",
                "detail": "Raw v6 source is reproduced, but current deterministic cleanup output differs from accepted v6 cleaned text.",
            }
        )

    report = {
        "schema": "kb_creator_innsmouth_full_dry_run_report.v1",
        "generated_at_utc": now_utc(),
        "status": "pass" if not findings else "blocked",
        "scope": "source-pdf-to-source-candidate; publishing blocked unless source equals accepted v6",
        "source_pdf": source_record,
        "config": file_record(config_path),
        "pymupdf_candidate": file_record(pymupdf_candidate),
        "column_candidate": file_record(column_candidate),
        "raw_v6_candidate": file_record(raw_v6_candidate),
        "cleaned_candidate": file_record(cleaned_candidate),
        "accepted_cleaned_candidate": file_record(accepted_cleaned_candidate),
        "builder_report": file_record(builder_report),
        "cleanup_attempted": cleanup_attempted,
        "cleanup_report": file_record(report_dir / "source_cleanup/source_cleanup_report.v1.json"),
        "accepted_cleaned_delta_attempted": accepted_cleaned_delta_attempted,
        "accepted_cleaned_delta_report": file_record(
            report_dir / "accepted_cleaned_delta/accepted_cleaned_delta_report.json"
        ),
        "publishing_attempted": publishing_attempted,
        "publishing_report": file_record(publishing_report_path),
        "accepted_v6_en": file_record(ACCEPTED_V6_EN),
        "accepted_v6_raw_en": file_record(ACCEPTED_V6_RAW_EN),
        "accepted_v2_en": file_record(ACCEPTED_V2_EN),
        "comparisons": {
            "pymupdf_source_vs_accepted_v6": pymupdf_vs_v6,
            "pymupdf_source_vs_accepted_v2": pymupdf_vs_v2,
            "raw_v6_source_vs_accepted_raw_v6": raw_v6_vs_accepted_raw,
            "raw_v6_source_vs_accepted_v6_cleaned": raw_v6_vs_accepted_cleaned,
            "deterministic_cleanup_source_vs_accepted_v6": cleanup_vs_v6,
            "accepted_cleaned_source_vs_accepted_v6": accepted_cleaned_vs_v6,
        },
        "commands": commands,
        "findings": findings,
        "next_action": "Continue to translation/proofread/publishing dry-run boundary analysis."
        if source_gate_passed and not findings
        else "Recover or encode post-cleanup source edits before continuing to translation/publishing."
        if raw_source_gate_passed
        else "Fix PDF/render/OCR/reading-order reconstruction before continuing to cleanup/publishing."
        if findings
        else "Continue to translation/proofread/publishing dry-run.",
    }
    report_path = report_dir / "full_dry_run_report.json"
    write_json(report_path, report)
    print(f"status={report['status']} source={rel(cleaned_candidate)} findings={len(findings)} report={rel(report_path)}")
    return 0 if report["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
