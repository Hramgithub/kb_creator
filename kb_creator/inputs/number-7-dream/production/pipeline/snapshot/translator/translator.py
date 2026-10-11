#!/usr/bin/env python3
"""Generic translator package CLI.

The project-specific package config owns paths and policy. This script is the
upstream entrypoint for reusable package steps; legacy project copies
under Dune/Scripts are mirrors only.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import html as html_lib
import json
import math
import os
import platform
import re
import shutil
import shlex
import socket
import subprocess
import sys
import tempfile
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import unquote

from PIL import Image, ImageDraw, ImageFont

try:  # Support both package imports and ``python translator/translator.py``.
    from . import coc_mechanics_audit, contract_v2_audit, page_policy, page_structure_audit, pipeline_plan, pipeline_run, positive_content_audit, remediation_checkpoint_audit, semantic_chain_audit
    from .contract_v2_gates import compare_structural_fingerprints
    from .document_ir import document_from_manifest, structural_fingerprint, validate_document
    from .pipeline_state import JsonContentCache as ContentAddressedJsonCache
except ImportError:  # pragma: no cover - exercised by the standalone CLI.
    _TRANSLATOR_DIR = str(Path(__file__).resolve().parent)
    if _TRANSLATOR_DIR not in sys.path:
        sys.path.insert(0, _TRANSLATOR_DIR)
    import contract_v2_audit
    import page_policy
    import coc_mechanics_audit
    import page_structure_audit
    import positive_content_audit
    import remediation_checkpoint_audit
    import semantic_chain_audit
    import pipeline_plan
    import pipeline_run
    from contract_v2_gates import compare_structural_fingerprints
    from document_ir import document_from_manifest, structural_fingerprint, validate_document
    from pipeline_state import JsonContentCache as ContentAddressedJsonCache


REPO_ROOT = Path(os.environ.get("NRI_ROOT", Path(__file__).resolve().parents[1])).resolve()
DEFAULT_CONFIG = REPO_ROOT / "translator/config/wormsign.package.example.json"
DEFAULT_TOOL_PATHS = {
    "pdfinfo": ".tools/poppler/poppler-26.02.0/Library/bin/pdfinfo.exe",
    "pdftoppm": ".tools/poppler/poppler-26.02.0/Library/bin/pdftoppm.exe",
    "pdftotext": ".tools/poppler/poppler-26.02.0/Library/bin/pdftotext.exe",
    "tesseract": ".tools/tesseract/tesseract.exe",
}
COMMON_WINDOWS_TOOL_PATHS = {
    "tesseract": [
        "C:/Program Files/Tesseract-OCR/tesseract.exe",
        "C:/Program Files (x86)/Tesseract-OCR/tesseract.exe",
    ],
}
COMMON_EDGE_PATHS = [
    "C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe",
    "C:/Program Files/Microsoft/Edge/Application/msedge.exe",
]
IMG_PNG_SRC_RE = re.compile(r'(<img\b[^>]*\bsrc=["\'])([^"\']+?\.png)(["\'][^>]*>)', re.I)
CSS_PNG_URL_RE = re.compile(r"""(url\(["']?)([^"')]+?\.png)(["']?\))""", re.I)
IMG_REF_RE = re.compile(r"""(?:<img\b[^>]*\bsrc=|url\()["']?([^"') >]+)""", re.I)
TOC_RE = re.compile(r'(?P<toc><nav\b[^>]*\bid=["\']toc["\'][\s\S]*?</nav>)', re.I)
RAW_PAGE_RE = re.compile(r"^=== PAGE (?P<page>\d{2,3}) ===\s*$", re.M)
SOURCE_PAGE_RE = re.compile(r"^<!--\s*source-page-(?P<page>\d{3})\s*-->\s*$", re.M)
DEFAULT_PAGE_RENDER_DPI = 180
DEFAULT_TOC_POLICY = {
    "mode": "preserve_and_link",
    "source_title": "Содержание",
    "generated_fallback_title": "Оглавление",
    "source_page": None,
    "columns": 2,
    "root_heading_level": 1,
    "font_size": "9.5pt",
    "line_height": "1.18",
    "item_gap": "3px",
    "column_fill": "balance",
    "column_gap": "7mm",
    "source_link_map": "",
    "source_toc_stop_titles": [],
    "replace_source_toc_pages": True,
    "replace_manual_toc_sections": False,
    "manual_toc_titles": ["Содержание", "Оглавление"],
    "max_heading_level": 2,
    "exclude_statblock_headings": True,
    "exclude_page_types": ["cover", "credits", "source_toc", "quote_art", "full_art"],
    "exclude_titles": ["Содержание", "Оглавление"],
}
IMAGE_APPROVAL_ROLES = ["source_image", "map", "diagram", "floorplan", "handout", "npc", "atmospheric", "decoration", "reject"]
IMAGE_COPY_ROLES = {"source_image", "map", "diagram", "floorplan", "handout", "npc", "atmospheric"}
CONTENT_SIGNAL_ROLES = {"map", "diagram", "floorplan", "handout"}
STATBLOCK_PROFILE_TOKENS = {
    "coc": ["STR", "CON", "SIZ", "INT", "POW", "DEX", "APP", "EDU", "SAN", "HP", "MOV", "DB", "BUILD"],
    "dune": ["DRIVE", "DUTY", "FAITH", "JUSTICE", "POWER", "TRUTH", "BATTLE", "COMMUNICATE", "DISCIPLINE", "MOVE", "UNDERSTAND", "FOCUS", "DETERMINATION"],
    "generic": ["STR", "CON", "HP", "SKILL", "ATTACK", "ARMOR", "DRIVE", "ASSET", "TALENT", "SPECIAL"],
}
STATBLOCK_PROFILE_RULES = {
    "coc": {
        "label": "Call of Cthulhu",
        "target_shape": [
            "Separate each NPC/creature statblock from prose.",
            "Use one table for core characteristics.",
            "Use one table for derived stats.",
            "Use one action/parameter table for attacks, armor, skills, sanity loss, and special combat notes.",
        ],
        "fields": ["STR", "CON", "SIZ", "INT", "POW", "DEX", "APP", "EDU", "SAN", "HP", "MOV", "DB", "BUILD"],
    },
    "dune": {
        "label": "Dune: Adventures in the Imperium",
        "target_shape": [
            "Separate NPC/adversary or asset statblocks from prose.",
            "Keep drives, skills, focuses, talents, assets, traits, and conflict notes in structured tables or cards.",
            "Preserve ratings, quality, scale, trait names, and rules notes exactly until terminology QA.",
        ],
        "fields": ["DUTY", "FAITH", "JUSTICE", "POWER", "TRUTH", "BATTLE", "COMMUNICATE", "DISCIPLINE", "MOVE", "UNDERSTAND"],
    },
    "generic": {
        "label": "Generic RPG statblock",
        "target_shape": [
            "Separate statblocks/cards from prose.",
            "Keep ratings, rules terms, attacks, armor, skills, assets, traits, and special notes in structured Markdown.",
            "Mark uncertain values as `?` until checked against render/source PDF.",
        ],
        "fields": ["rating", "derived stat", "attack/action", "skill", "asset", "trait", "special note"],
    },
}
LETTER_RUN = r"[^\W\d_]"
HYPHENATED_LINE_BREAK_RE = re.compile(rf"({LETTER_RUN}{{2,}})-\s*\n\s*({LETTER_RUN}{{2,}})", re.U)
PAGE_SELECTOR_RE = re.compile(r"^(?P<start>\d+)(?:-(?P<end>\d+))?$")
_TOOL_IDENTITY_CACHE: dict[tuple[str, str], dict[str, str]] = {}


def parse_page_selectors(values: list[str] | None) -> list[str] | None:
    """Expand repeatable CLI page selectors into sorted semantic page ids."""

    if values is None:
        return None
    selected: set[int] = set()
    for value in values:
        match = PAGE_SELECTOR_RE.fullmatch(value.strip())
        if not match:
            raise ValueError(f"invalid_page_selector: {value!r}")
        start = int(match.group("start"))
        end = int(match.group("end") or start)
        if end < start:
            raise ValueError(f"descending_page_range: {value!r}")
        selected.update(range(start, end + 1))
    return [str(page).zfill(3) for page in sorted(selected)]


def select_policy_pages(
    config: dict[str, Any],
    *,
    stage: str,
    page_count: int,
    requested_pages: list[str] | None,
) -> dict[str, Any]:
    """Return a valid page-policy decision or fail before stage side effects."""

    selection = page_policy.select_pages(stage, page_count, config.get("page_map"), requested_pages)
    if selection["status"] != "ok":
        codes = ", ".join(str(error["code"]) for error in selection["errors"])
        raise ValueError(codes)
    return selection


def page_selection_report(
    selection: dict[str, Any],
    *,
    unavailable_pages: set[str] | None = None,
    extra_skipped: list[dict[str, str]] | None = None,
) -> dict[str, Any]:
    """Condense policy decisions into stable report evidence for physical stages."""

    unavailable = unavailable_pages or set()
    effective_pages = [page for page in selection["physical_selected_pages"] if page not in unavailable]
    skipped = [
        {"page": decision["id"], "reason": decision["reason"]}
        for decision in selection["decisions"]
        if not decision["selected"] and decision["reason"] != "not_requested"
    ]
    skipped.extend({"page": page, "reason": "page_render_missing"} for page in sorted(unavailable, key=int))
    skipped.extend(extra_skipped or [])
    skipped.sort(key=lambda item: (int(item["page"]), item["reason"]))
    return {
        "requested_pages": selection["requested_pages"],
        "effective_pages": effective_pages,
        "skipped_pages": skipped,
    }


def page_count_from_text_pages(pages: list[dict[str, Any]]) -> int:
    numbered_pages = [int(page["page"]) for page in pages if page.get("page") is not None]
    return max(numbered_pages, default=1)


def rendered_page_images(render_dir: Path) -> dict[int, Path]:
    images: dict[int, Path] = {}
    for image in render_dir.glob("page-*.png"):
        match = re.fullmatch(r"page-(\d+)", image.stem)
        if match:
            images[int(match.group(1))] = image
    return images


def read_json(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(data, dict) and data.get("project_key") and data.get("workbench_qa_root"):
        data["__config_path"] = str(path.resolve())
    return data


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def root_path(value: str) -> Path:
    value = value.replace("/", "\\")
    path = Path(value)
    return path.resolve() if path.is_absolute() else (REPO_ROOT / path).resolve()


def rel(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(REPO_ROOT)).replace("\\", "/")
    except ValueError:
        return str(path).replace("\\", "/")


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def postproduction_config(config: dict[str, Any]) -> dict[str, Any]:
    return config.get("postproduction", {})


def qa_root(config: dict[str, Any], config_path: Path | None = None) -> Path:
    pp = postproduction_config(config)
    value = pp.get("working_qa_root") or pp.get("qa_output_dir") or config.get("workbench_qa_root") or "translator/QA"
    path = Path(str(value).replace("/", "\\"))
    if path.is_absolute():
        return path.resolve()
    stored_config_path = config.get("__config_path")
    base = (
        config_path.resolve().parent
        if config_path is not None
        else Path(str(stored_config_path)).resolve().parent
        if stored_config_path
        else REPO_ROOT
    )
    return (base / path).resolve()


def processing_cache(config: dict[str, Any]) -> ContentAddressedJsonCache:
    """Keep deterministic processing data in the private workbench QA layer."""

    return ContentAddressedJsonCache(qa_root(config), relative_dir="Pipeline_Cache")


def cache_telemetry() -> dict[str, int]:
    return {"hits": 0, "misses": 0, "duration_ms": 0}


def cache_duration_ms(start_ns: int) -> int:
    return max(0, (time.monotonic_ns() - start_ns) // 1_000_000)


def executable_identity(tool: Path, *, version: str | None = None) -> dict[str, str]:
    """Return a path-free executable digest with a conservative version slot."""

    digest = sha256_file(tool) if tool.exists() else sha256_text(f"missing:{tool.name}")
    version = version or "unavailable"
    key = (tool.name.casefold(), f"{digest}:{version}")
    cached = _TOOL_IDENTITY_CACHE.get(key)
    if cached is not None:
        return cached
    # Binary content is the authoritative identity. Do not add a tool-version
    # subprocess to an OCR/PDF operation just to populate telemetry.
    identity = {"sha256": digest, "version": version}
    _TOOL_IDENTITY_CACHE[key] = identity
    return identity


def diagnostic_lines(lines: list[str], *, limit: int = 5) -> list[dict[str, Any]]:
    """Preserve diagnostic evidence without publishing text or local paths."""

    return [
        {"sha256": sha256_text(line), "chars": len(line)}
        for line in lines[:limit]
    ]


def cached_tesseract_result(
    cache: ContentAddressedJsonCache,
    telemetry: dict[str, int],
    *,
    image: Path,
    normalized_zone: dict[str, Any] | None,
    tess: Path,
    tess_identity: dict[str, str],
    language: str,
    psm: str,
    force: bool,
    encoding: str | None = None,
    input_sha256: str | None = None,
) -> dict[str, Any]:
    """Run one OCR unit or reuse a validated private cache value."""

    started = time.monotonic_ns()
    input_hashes = {"render_or_crop_sha256": input_sha256 or sha256_file(image)}
    options = {
        "language": language,
        "psm": psm,
        "normalized_zone": normalized_zone,
        "tesseract": tess_identity,
        "command": {"output": "stdout", "encoding": encoding or "default", "timeout_seconds": 120},
    }
    lookup = None if force else cache.get("tesseract_ocr", input_hashes, options)
    value = lookup.value if lookup and lookup.hit else None
    valid = (
        isinstance(value, dict)
        and isinstance(value.get("text"), str)
        and isinstance(value.get("returncode"), int)
        and not isinstance(value.get("returncode"), bool)
        and isinstance(value.get("stderr"), list)
        and all(isinstance(line, str) for line in value["stderr"])
    )
    if valid:
        telemetry["hits"] += 1
        telemetry["duration_ms"] += cache_duration_ms(started)
        return value

    telemetry["misses"] += 1
    run_kwargs: dict[str, Any] = {
        "cwd": REPO_ROOT,
        "capture_output": True,
        "text": True,
        "encoding": encoding or "utf-8",
        "errors": "replace",
        "timeout": 120,
        "check": False,
    }
    if encoding is not None:
        run_kwargs.update({"encoding": encoding})
    completed = subprocess.run(
        [str(tess), str(image), "stdout", "-l", language, "--psm", psm],
        **run_kwargs,
    )
    result = {
        "text": completed.stdout.strip(),
        "returncode": completed.returncode,
        "stderr": completed.stderr.strip().splitlines()[:5],
    }
    cache.put("tesseract_ocr", input_hashes, options, result)
    telemetry["duration_ms"] += cache_duration_ms(started)
    return result


def report_path(config: dict[str, Any], key: str, default_name: str) -> Path:
    pp = postproduction_config(config)
    value = pp.get(key, default_name)
    path = Path(str(value).replace("/", "\\"))
    return path.resolve() if path.is_absolute() else qa_root(config) / path


def intake_config(config: dict[str, Any]) -> dict[str, Any]:
    return config.get("intake", {})


def tooling_config(config: dict[str, Any]) -> dict[str, Any]:
    return config.get("tooling", {})


def intake_report_path(config: dict[str, Any], key: str, default_name: str) -> Path:
    intake = intake_config(config)
    value = intake.get(key, default_name)
    path = Path(str(value).replace("/", "\\"))
    return path.resolve() if path.is_absolute() else qa_root(config) / path


def config_path(config: dict[str, Any], key: str, *, required: bool = True) -> Path | None:
    value = config.get(key)
    if value is None:
        if required:
            raise KeyError(key)
        return None
    return root_path(str(value))


def resolve_command_path(config: dict[str, Any], key: str, default_relative: str) -> tuple[Path, str]:
    value = tooling_config(config).get(key)
    if value:
        path = root_path(str(value))
        return path, "config"
    default_path = root_path(default_relative)
    if default_path.exists():
        return default_path, "repo_default"
    found = shutil.which(key)
    if found:
        return Path(found).resolve(), "path"
    for candidate in COMMON_WINDOWS_TOOL_PATHS.get(key, []):
        path = Path(candidate)
        if path.exists():
            return path.resolve(), "common_windows"
    return default_path, "missing_default"


def command_path(config: dict[str, Any], key: str, default_relative: str) -> Path:
    return resolve_command_path(config, key, default_relative)[0]


def pdfinfo_path(config: dict[str, Any]) -> Path:
    return command_path(config, "pdfinfo", DEFAULT_TOOL_PATHS["pdfinfo"])


def pdftoppm_path(config: dict[str, Any]) -> Path:
    return command_path(config, "pdftoppm", DEFAULT_TOOL_PATHS["pdftoppm"])


def pdftotext_path(config: dict[str, Any]) -> Path:
    return command_path(config, "pdftotext", DEFAULT_TOOL_PATHS["pdftotext"])


def tesseract_path(config: dict[str, Any]) -> Path:
    return command_path(config, "tesseract", DEFAULT_TOOL_PATHS["tesseract"])


def import_check(module_name: str, package_label: str | None = None) -> dict[str, Any]:
    try:
        module = __import__(module_name)
        version = getattr(module, "__version__", None) or getattr(module, "VersionBind", None)
        return {"module": module_name, "package": package_label or module_name, "ok": True, "version": str(version) if version else None}
    except Exception as exc:  # pragma: no cover - error path is environment-specific.
        return {"module": module_name, "package": package_label or module_name, "ok": False, "error": str(exc)}


def command_check(path: Path, args: list[str] | None = None) -> dict[str, Any]:
    result: dict[str, Any] = {"path": rel(path), "exists": path.exists()}
    if not path.exists():
        return result
    try:
        completed = subprocess.run(
            [str(path), *(args or ["-v"])],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            timeout=20,
            check=False,
        )
        result.update(
            {
                "ok": completed.returncode == 0,
                "returncode": completed.returncode,
                "stdout": completed.stdout.strip().splitlines()[:3],
                "stderr": completed.stderr.strip().splitlines()[:3],
            }
        )
    except Exception as exc:  # pragma: no cover - error path is environment-specific.
        result.update({"ok": False, "error": str(exc)})
    return result


def command_check_for(config: dict[str, Any], key: str, args: list[str] | None = None) -> dict[str, Any]:
    path, source = resolve_command_path(config, key, DEFAULT_TOOL_PATHS[key])
    result = command_check(path, args)
    result["resolution"] = source
    configured = tooling_config(config).get(key)
    if configured:
        result["configured_path"] = str(configured)
    return result


def station_profile(config_path: Path) -> dict[str, Any]:
    commands = {}
    for name in ("codex", "git", "node", "python", "py", "gh", "dotnet"):
        found = shutil.which(name)
        commands[name] = {"path": found, "available": bool(found)}
    return {
        "schema": "translator_station_profile.v1",
        "computer": os.environ.get("COMPUTERNAME") or socket.gethostname(),
        "userprofile": os.environ.get("USERPROFILE"),
        "localappdata": os.environ.get("LOCALAPPDATA"),
        "platform": platform.platform(),
        "repo_root": str(REPO_ROOT),
        "config": rel(config_path),
        "python_executable": sys.executable,
        "path_commands": commands,
        "nri_root_env": os.environ.get("NRI_ROOT"),
    }


def configured_pdf_engine_command(config: dict[str, Any]) -> list[str]:
    command = config.get("production_pdf", {}).get("engine_command")
    if isinstance(command, list):
        return [str(part) for part in command]
    if isinstance(command, str):
        try:
            return shlex.split(command, posix=os.name != "nt")
        except ValueError:
            return [command]
    return []


def resolve_edge_path(config: dict[str, Any]) -> tuple[Path | None, str]:
    command = configured_pdf_engine_command(config)
    if command:
        configured = Path(command[0])
        if configured.exists():
            return configured.resolve(), "production_pdf.engine_command"
    for name in ("msedge", "msedge.exe", "microsoft-edge"):
        found = shutil.which(name)
        if found:
            return Path(found).resolve(), "path"
    for candidate in COMMON_EDGE_PATHS:
        path = Path(candidate)
        if path.exists():
            return path.resolve(), "common_windows"
    return None, "missing"


def edge_pdf_engine_check(config: dict[str, Any]) -> dict[str, Any]:
    edge_path, resolution = resolve_edge_path(config)
    configured = configured_pdf_engine_command(config)
    warnings: list[dict[str, Any]] = []
    recommended_command: list[str] | None = None
    version: dict[str, Any] | None = None
    if edge_path:
        version = command_check(edge_path, ["--version"])
        recommended_command = [
            str(edge_path),
            "--headless=new",
            "--disable-gpu",
            "--no-sandbox",
            "--no-first-run",
            "--no-pdf-header-footer",
            "--user-data-dir={temp_dir}",
            "--print-to-pdf={output_pdf}",
            "{source_html_uri}",
        ]
    if configured:
        if "--headless" in configured and "--headless=new" not in configured:
            warnings.append(
                {
                    "code": "legacy_edge_headless_flag",
                    "message": "This station requires --headless=new for reliable Edge print-to-pdf output.",
                }
            )
        if os.name == "nt" and "--no-sandbox" not in configured:
            warnings.append(
                {
                    "code": "missing_edge_no_sandbox_flag",
                    "message": "The verified Edge print-to-pdf command on this station includes --no-sandbox.",
                }
            )
        if "--no-pdf-header-footer" not in configured:
            warnings.append(
                {
                    "code": "missing_edge_no_pdf_header_footer_flag",
                    "message": "Production PDF printing must disable browser header/footer metadata.",
                }
            )
    return {
        "schema": "translator_html_pdf_engine_check.v1",
        "engine": "microsoft_edge",
        "path": str(edge_path) if edge_path else None,
        "exists": bool(edge_path),
        "resolution": resolution,
        "version": version,
        "configured_command": configured or None,
        "recommended_command": recommended_command,
        "station_notes": [
            "On this Windows station, legacy --headless returned 0 without creating a PDF during Edge print-to-pdf.",
            "Use --headless=new, --no-sandbox, and --no-pdf-header-footer for production_pdf.engine_command.",
        ],
        "warnings": warnings,
    }


def required_config_keys() -> list[str]:
    return ["schema", "project_key", "source_pdf", "package_root", "workbench_root"]


def package_title(config: dict[str, Any]) -> str:
    return str(
        config.get("title_ru")
        or config.get("title_en")
        or config.get("scenario_title_ru")
        or config.get("scenario_title_en")
        or config.get("project_key")
        or "Translator package"
    )


def package_config_path(project_key: str) -> Path:
    return REPO_ROOT / "translator" / "config" / f"{project_key}.package.json"


def default_package_roots(project_family: str, project_key: str) -> tuple[str, str, str]:
    family_root = project_family if project_family else "Generic"
    if family_root.lower() == "generic":
        return (
            f"Output/Translator/{project_key}",
            f"Output/Translator/{project_key}",
            f"Working/Translator/{project_key}",
        )
    return (
        f"{family_root}/Output/Scenarios/{project_key}",
        f"{family_root}/Output/Scenarios/{project_key}",
        f"{family_root}/Working/Scenarios/{project_key}",
    )


def build_initial_package_config(
    *,
    source_pdf: Path,
    project_key: str,
    project_family: str,
    project_type: str,
    title_en: str | None,
    title_ru: str | None,
    package_root_value: str | None,
    public_package_root_value: str | None,
    workbench_root_value: str | None,
    qa_root_value: str | None,
) -> dict[str, Any]:
    default_public, default_package, default_workbench = default_package_roots(project_family, project_key)
    package_root_value = package_root_value or default_package
    public_package_root_value = public_package_root_value or default_public
    workbench_root_value = workbench_root_value or default_workbench
    qa_root_value = qa_root_value or f"{workbench_root_value}/project/QA"
    source_prefix = f"{workbench_root_value}/Formatted/{project_key}"
    output_prefix = f"{public_package_root_value}/{project_key}"
    source_exists = source_pdf.exists()
    source_identity: dict[str, Any] = {
        "source_pdf_original_external": str(source_pdf),
        "source_pdf_is_external": not source_pdf.is_relative_to(REPO_ROOT),
    }
    if source_exists:
        source_identity.update(
            {
                "source_pdf_bytes": source_pdf.stat().st_size,
                "source_pdf_sha256": sha256_file(source_pdf).upper(),
            }
        )
    return {
        "schema": "translator_package_config.v1",
        "nri_root": ".",
        "project_key": project_key,
        "project_family": project_family,
        "project_type": project_type,
        "title_en": title_en or project_key.replace("_", " ").title(),
        "title_ru": title_ru or "",
        "source_pdf": str(source_pdf),
        **source_identity,
        "public_package_root": public_package_root_value,
        "package_root": package_root_value,
        "workbench_root": workbench_root_value,
        "workbench_qa_root": qa_root_value,
        "tooling": dict(DEFAULT_TOOL_PATHS),
        "intake": {
            "env_check_report": "translator_env_check.json",
            "config_validation_report": "translator_config_validation.json",
            "pdf_info_report": "source_pdf_info.json",
            "pdf_hash_report": "source_pdf_hash.json",
            "page_render_report": "page_render_report.json",
            "text_extraction_report": "text_extraction_report.json",
            "ocr_report": "ocr_report.json",
            "source_text_qa_report": "source_text_qa_report.json",
            "source_text_normalization_report": "source_text_normalization_report.json",
            "image_extraction_report": "image_extraction_report.json",
            "image_inventory": "image_inventory.json",
            "image_classification": "image_classification.json",
            "image_classification_review": "image_classification_review.md",
            "image_contact_sheet": "image_contact_sheet.png",
            "image_contact_sheet_report": "image_contact_sheet_report.json",
            "image_role_approval": "image_role_approval.json",
            "image_role_approval_review": "image_role_approval_review.md",
            "apply_image_approval_report": "apply_image_approval_report.json",
            "page_renders": f"{workbench_root_value}/Images/Page_Renders",
            "embedded_images": f"{workbench_root_value}/Images/PDF_Extracted_All",
            "page_render_dpi": DEFAULT_PAGE_RENDER_DPI,
            "raw_text": f"{source_prefix}_Source_Text_Raw_EN_v1.txt",
            "ocr_text": f"{source_prefix}_Source_Text_OCR_EN_v1.md",
            "ocr_language": "eng",
            "ocr_psm": 6,
            "normalized_text": f"{source_prefix}_Source_Text_Normalized_EN_v1.md",
        },
        "contact_sheet": {
            "columns": 4,
            "thumb_width": 260,
            "thumb_height": 190,
            "label_height": 122,
            "margin": 24,
            "gap": 18,
        },
        "normalize_source_text": {"join_hyphenated_lines": False},
        "normalize_headings": {
            "source_markdown": f"{public_package_root_value}/For_Keeper/KeeperBook_v1.md",
            "report": "heading_normalization_report.json",
            "required_gates": ["keeper_full_accepted"],
            "rules": {
                "trim_heading_whitespace": True,
                "collapse_repeated_spaces": True,
                "fix_markdown_heading_spacing": True,
                "strip_closing_hashes": True,
                "max_heading_level": 6,
                "remove_titles": [],
                "remove_patterns": [],
                "title_replacements": [],
                "level_overrides": [],
            },
        },
        "source_reconstruction": {
            "source_markdown": f"{source_prefix}_Source_Text_Normalized_EN_v1.md",
            "task_packet_json": "source_reconstruction_tasks.json",
            "task_packet_md": "source_reconstruction_tasks.md",
        },
        "column_ocr_reconstruction": {
            "candidate_markdown": f"{workbench_root_value}/Translation_Work/Column_OCR_Reconstruction/{project_key}_Column_OCR_Candidate_EN.md",
            "page_chunk_dir": f"{workbench_root_value}/Translation_Work/Column_OCR_Reconstruction/Source_Pages",
            "crop_dir": f"{qa_root_value}/Column_OCR",
            "report": "column_ocr_reconstruction_report.json",
            "language": "eng",
            "psm": 6,
            "zones": [
                {"name": "left", "box": [0.05, 0.06, 0.50, 0.92]},
                {"name": "right", "box": [0.50, 0.06, 0.95, 0.92]},
            ],
            "source_art_strategy": "insert_anchor_then_ocr",
            "skip_ocr_roles": [],
            "auto_detect_columns": False,
        },
        "statblock_reconstruction": {
            "source_markdown": f"{source_prefix}_Source_Text_Normalized_EN_v1.md",
            "qa_report": "source_text_qa_report.json",
            "report": "statblock_reconstruction_report.json",
            "task_packet_md": "statblock_reconstruction_tasks.md",
            "profile": project_family.lower(),
        },
        "statblock_edition_conversion": {
            "enabled": False,
            "source_edition": "7e",
            "target_edition": "7e",
            "report": "statblock_edition_conversion_report.json",
            "markdowns": [
                {
                    "label": "keeper_markdown",
                    "path": f"{public_package_root_value}/For_Keeper/KeeperBook_v1.md",
                }
            ],
        },
        "review_html": {
            "source_markdown": f"{source_prefix}_Source_Text_Normalized_EN_v1.md",
            "output_html": f"{workbench_root_value}/project/Review_HTML/{project_key}_Source_Normalized_Review.html",
            "report": "review_html_report.json",
        },
        "production_html": {
            "source_markdown": f"{public_package_root_value}/For_Keeper/KeeperBook_v1.md",
            "output_html": f"{output_prefix}_Full_RU_v1.html",
            "report": "production_html_report.json",
            "toc_policy": {**DEFAULT_TOC_POLICY},
            "trial_source_markdown": f"{source_prefix}_Source_Text_Normalized_EN_v1.md",
            "trial_output_html": f"{workbench_root_value}/project/Review_HTML/{project_key}_Production_Trial.html",
            "required_gates": [
                "keeper_full_accepted",
                "term_gate_passed",
                "layout_anchors_accepted",
                "production_art_integrated",
            ],
        },
        "term_gate": {
            "registry": "",
            "source_markdown": f"{source_prefix}_Source_Text_Full_EN_v1.md",
            "output_markdown": f"{public_package_root_value}/For_Keeper/KeeperBook_v1.md",
            "report": "term_gate_report.json",
            "required_gates": ["source_full_ru_accepted"],
        },
        "layout_anchors": {
            "source_markdown": f"{public_package_root_value}/For_Keeper/KeeperBook_v1.md",
            "report": "layout_anchors_report.json",
            "required_gates": ["keeper_full_accepted"],
            "required_patterns": [],
        },
        "production_pdf": {
            "source_html": f"{output_prefix}_Full_RU_v1.html",
            "output_pdf": f"{public_package_root_value}/Pdf/{project_key}_Full_RU_v1.pdf",
            "report": "production_pdf_report.json",
            "required_gates": ["production_html_built"],
            "engine_command": None,
        },
        "translation": {
            "source_markdown": f"{source_prefix}_Source_Text_Full_EN_v1.md",
            "tasks_json": "translation_tasks.json",
            "tasks_jsonl": "translation_tasks.jsonl",
            "tasks_md": "translation_tasks.md",
            "prompt_pack_dir": "Localization_Prompts",
            "prompt_pack_report": "localization_prompt_pack_report.json",
            "localization_qa_report": "localization_qa_report.json",
            "report": "translation_preparation_report.json",
            "required_gates": ["source_reconstruction_accepted"],
            "max_unit_chars": 3500,
            "provider": "codex",
            "source_lang": "en",
            "target_lang": "ru",
        },
        "art_integration": {
            "report": "art_integration_report.json",
            "source_html": f"{output_prefix}_Full_RU_v1.html",
            "preserve_page_art_report": "preserve_page_art_report.json",
            "preserved_page_art": [],
            "required_gates": ["review_html_built"],
            "require_no_pending_image_approval": True,
            "require_applied_images": True,
            "require_source_html": False,
        },
        "production_art_layout": {
            "art_manifest": "art_manifest.json",
            "integration_manifest": "art_html_integration_manifest.json",
            "report": "art_layout_qa.json",
            "require_manifest": False,
            "require_break_policy": True,
            "require_text_contamination_policy": True,
            "autoscale_steps": [100, 90, 80, 70],
            "allowed_placements": [
                "replace_visual_page",
                "credits_background_page",
                "scenario_opening_float_right",
                "page_art_after_heading",
                "page_art_after_quote",
                "flow_art_before_first_paragraph",
                "compact_sheet_art_after_table",
            ],
        },
        "approval_ledger": {
            "report": "approval_ledger.json",
            "qa_report": "approval_ledger_qa.json",
            "production_approval_must_be_explicit": True,
        },
        "release_manifest": {
            "report": "release_manifest.json",
            "require_existing": [],
        },
        "pdf_print_qa": {
            "report": "pdf_print_qa.json",
            "render_dir": "PDF_Smoke_Renders",
            "require_header_footer_disabled": True,
            "require_current_html_hash": True,
            "min_text_chars": 1000,
            "page_size": "A4",
        },
        "release_qa": {
            "html": f"{output_prefix}_Full_RU_v1.html",
            "pdf": f"{public_package_root_value}/Pdf/{project_key}_Full_RU_v1.pdf",
            "report": "release_qa_report.json",
            "required_gates": [
                "production_html_built",
                "term_gate_passed",
                "layout_anchors_accepted",
                "production_art_integrated",
                "coverage_gate_passed",
            ],
            "require_pdf": False,
        },
        "coverage_gate": {
            "source_markdown": f"{source_prefix}_Source_Text_Full_EN_v1.md",
            "ru_markdown": f"{source_prefix}_Source_Text_Full_RU_v1.md",
            "keeper_markdown": f"{public_package_root_value}/For_Keeper/KeeperBook_v1.md",
            "html": f"{output_prefix}_Full_RU_v1.html",
            "pdf": f"{public_package_root_value}/Pdf/{project_key}_Full_RU_v1.pdf",
            "report": "coverage_gate_report.json",
            "required_gates": [
                "source_reconstruction_accepted",
                "source_full_ru_accepted",
                "keeper_full_accepted",
                "production_html_built",
            ],
            "require_pdf": False,
            "min_token_coverage": 0.98,
            "min_heading_ratio": 0.95,
            "min_pdf_heading_ratio": 0.80,
            "min_pdf_heading_hits": 6,
        },
        "production_outputs": {
            "source_full_ru": f"{source_prefix}_Source_Text_Full_RU_v1.md",
            "keeper_markdown": f"{public_package_root_value}/For_Keeper/KeeperBook_v1.md",
            "html": f"{output_prefix}_Full_RU_v1.html",
            "pdf": f"{public_package_root_value}/Pdf/{project_key}_Full_RU_v1.pdf",
            "images": f"{public_package_root_value}/Images",
            "knowledge_base": f"{public_package_root_value}/Knowledge_Base",
        },
        "scenario_gates": {
            "source_pdf_intake": False,
            "source_text_raw_extracted": False,
            "source_text_normalized": False,
            "source_reconstruction_prepared": False,
            "source_reconstruction_accepted": False,
            "source_full_ru_accepted": False,
            "keeper_full_accepted": False,
            "term_gate_passed": False,
            "layout_anchors_accepted": False,
            "review_html_built": False,
            "production_html_built": False,
            "production_art_integrated": False,
            "coverage_gate_passed": False,
            "production_pdf_built": False,
            "production_approved": False,
        },
    }


def init_package(
    *,
    source_pdf: Path,
    project_key: str,
    project_family: str,
    project_type: str,
    title_en: str | None,
    title_ru: str | None,
    config_out: Path | None,
    package_root_value: str | None,
    public_package_root_value: str | None,
    workbench_root_value: str | None,
    qa_root_value: str | None,
    force: bool = False,
    create_dirs: bool = True,
) -> dict[str, Any]:
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_-]*", project_key):
        raise ValueError("project_key must contain only ASCII letters, digits, underscore, or hyphen, and start with a letter/digit")
    source_pdf = source_pdf.resolve()
    config_out = (config_out or package_config_path(project_key)).resolve()
    if config_out.exists() and not force:
        raise FileExistsError(config_out)
    config = build_initial_package_config(
        source_pdf=source_pdf,
        project_key=project_key,
        project_family=project_family,
        project_type=project_type,
        title_en=title_en,
        title_ru=title_ru,
        package_root_value=package_root_value,
        public_package_root_value=public_package_root_value,
        workbench_root_value=workbench_root_value,
        qa_root_value=qa_root_value,
    )
    config_out.parent.mkdir(parents=True, exist_ok=True)
    write_json(config_out, config)
    created_dirs: list[str] = []
    if create_dirs:
        for key in ("package_root", "public_package_root", "workbench_root", "workbench_qa_root"):
            path = root_path(str(config[key]))
            path.mkdir(parents=True, exist_ok=True)
            created_dirs.append(rel(path))
        for value in (
            intake_config(config)["page_renders"],
            intake_config(config)["embedded_images"],
            Path(str(intake_config(config)["raw_text"])).parent.as_posix(),
            Path(str(review_html_config(config)["output_html"])).parent.as_posix(),
        ):
            path = root_path(str(value))
            path.mkdir(parents=True, exist_ok=True)
            created_dirs.append(rel(path))
    result = {
        "schema": "translator_init_package.v1",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "status": "pass",
        "config": rel(config_out),
        "source_pdf": str(source_pdf),
        "source_exists": source_pdf.exists(),
        "source_pdf_bytes": source_pdf.stat().st_size if source_pdf.exists() else None,
        "source_pdf_sha256": sha256_file(source_pdf).upper() if source_pdf.exists() else None,
        "project_key": project_key,
        "created_dirs": sorted(set(created_dirs)),
        "next_commands": [
            f"translator/translator.py validate-config --config {rel(config_out)}",
            f"translator/translator.py env-check --config {rel(config_out)}",
            f"translator/translator.py intake --config {rel(config_out)}",
            f"translator/translator.py render-pages --config {rel(config_out)}",
            f"translator/translator.py extract-text --config {rel(config_out)}",
            f"translator/translator.py source-text-qa --config {rel(config_out)}",
        ],
    }
    write_json(intake_report_path(config, "init_package_report", "init_package_report.json"), result)
    return result


def validate_config_data(config: dict[str, Any], *, strict_release: bool = False) -> dict[str, Any]:
    missing = [key for key in required_config_keys() if not config.get(key)]
    paths: dict[str, Any] = {}
    for key in ["source_pdf", "package_root", "workbench_root", "public_package_root"]:
        if config.get(key):
            path = root_path(str(config[key]))
            paths[key] = {"path": rel(path), "exists": path.exists()}
    output_paths: dict[str, Any] = {}
    for key, value in config.get("production_outputs", {}).items():
        path = root_path(str(value))
        output_paths[key] = {"path": rel(path), "exists": path.exists()}
    findings: list[dict[str, Any]] = []
    warnings: list[dict[str, Any]] = []
    if strict_release:
        local_temp_patterns = [
            r"[/\\]AppData[/\\]Local[/\\]Temp[/\\]",
            r"[/\\]Temp[/\\]codex-clipboard",
            r"^%TEMP%[/\\]",
        ]
        path_fields: list[tuple[str, Any]] = [
            ("source_pdf", config.get("source_pdf")),
            ("source_pdf_original_external", config.get("source_pdf_original_external")),
        ]
        landing = production_html_config(config).get("landing_asset")
        if isinstance(landing, dict):
            path_fields.extend(
                [
                    ("production_html.landing_asset.source", landing.get("source")),
                    ("production_html.landing_asset.working_master", landing.get("working_master")),
                    ("production_html.landing_asset.src", landing.get("src")),
                ]
            )
        for label, value in path_fields:
            if not value:
                continue
            text = str(value)
            if any(re.search(pattern, text, re.I) for pattern in local_temp_patterns):
                findings.append({"code": "strict_release_temp_path", "field": label, "path": text})
            path = root_path(text)
            if not path.exists():
                findings.append({"code": "strict_release_missing_path", "field": label, "path": rel(path)})
        pdf_cfg = production_pdf_config(config)
        engine = pdf_cfg.get("engine_command")
        station_profiles = config.get("station_profiles") or pdf_cfg.get("station_profiles")
        if engine and not station_profiles:
            engine_parts = engine if isinstance(engine, list) else [engine]
            if any(Path(str(part)).is_absolute() for part in engine_parts[:1]):
                warnings.append(
                    {
                        "code": "strict_release_absolute_pdf_engine_without_station_profile",
                        "field": "production_pdf.engine_command",
                    }
                )
    return {
        "missing_required_keys": missing,
        "paths": paths,
        "production_outputs": output_paths,
        "findings": findings,
        "warnings": warnings,
        "strict_release": strict_release,
        "status": "pass" if not missing and paths.get("source_pdf", {}).get("exists") and not findings else "fail",
    }


def validate_config(config_path: Path, *, strict_release: bool = False) -> dict[str, Any]:
    config = read_json(config_path)
    report = (
        intake_report_path(config, "strict_config_validation_report", "translator_config_validation_strict_release.json")
        if strict_release
        else intake_report_path(config, "config_validation_report", "translator_config_validation.json")
    )
    result = {
        "schema": "translator_config_validation.v1",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "config": rel(config_path),
        **validate_config_data(config, strict_release=strict_release),
    }
    write_json(report, result)
    return result


def env_check(config_path: Path) -> dict[str, Any]:
    config = read_json(config_path)
    imports = [
        import_check("fitz", "PyMuPDF"),
        import_check("pdfplumber"),
        import_check("pypdf"),
        import_check("PIL", "Pillow"),
    ]
    commands = {
        "pdfinfo": command_check_for(config, "pdfinfo", ["-v"]),
        "pdftoppm": command_check_for(config, "pdftoppm", ["-v"]),
        "pdftotext": command_check_for(config, "pdftotext", ["-v"]),
        "tesseract": command_check_for(config, "tesseract", ["--version"]),
    }
    findings = []
    for item in imports:
        if not item.get("ok"):
            findings.append({"code": "missing_python_module", "message": item["package"]})
    for name, item in commands.items():
        if not item.get("exists"):
            findings.append({"code": "missing_tool", "message": name})
    html_pdf_engine = edge_pdf_engine_check(config)
    result = {
        "schema": "translator_environment_check.v1",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "config": rel(config_path),
        "station": station_profile(config_path),
        "python": {"executable": sys.executable, "version": sys.version},
        "imports": imports,
        "commands": commands,
        "html_pdf_engine": html_pdf_engine,
        "status": "pass" if not findings else "fail",
        "findings": findings,
        "warnings": html_pdf_engine.get("warnings", []),
    }
    write_json(intake_report_path(config, "env_check_report", "translator_env_check.json"), result)
    return result


def pdf_metadata(pdf_path: Path) -> dict[str, Any]:
    import fitz  # PyMuPDF

    with fitz.open(pdf_path) as doc:
        pages = []
        for index, page in enumerate(doc, start=1):
            rect = page.rect
            pages.append({"page": index, "width_pt": round(rect.width, 3), "height_pt": round(rect.height, 3)})
        return {
            "path": rel(pdf_path),
            "pages": len(doc),
            "is_encrypted": doc.is_encrypted,
            "metadata": dict(doc.metadata or {}),
            "page_sizes": pages,
        }


def intake_pdf(config_path: Path) -> dict[str, Any]:
    config = read_json(config_path)
    source = root_path(str(config["source_pdf"]))
    if not source.exists():
        raise FileNotFoundError(source)
    metadata = pdf_metadata(source)
    digest = sha256_file(source)
    result = {
        "schema": "translator_pdf_intake.v1",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "config": rel(config_path),
        "source_pdf": metadata,
        "file_size_bytes": source.stat().st_size,
        "sha256": digest.upper(),
    }
    write_json(intake_report_path(config, "pdf_info_report", "source_pdf_info.json"), result)
    write_json(
        intake_report_path(config, "pdf_hash_report", "source_pdf_hash.json"),
        {
            "schema": "translator_pdf_hash.v1",
            "generated_at_utc": result["generated_at_utc"],
            "source_pdf": rel(source),
            "file_size_bytes": source.stat().st_size,
            "sha256": digest.upper(),
        },
    )
    return result


def render_pages(
    config_path: Path, *, force: bool = False, requested_pages: list[str] | None = None
) -> dict[str, Any]:
    import fitz  # PyMuPDF

    config = read_json(config_path)
    source = root_path(str(config["source_pdf"]))
    render_dir = root_path(intake_config(config).get("page_renders", f"{config['workbench_root']}/Images/Page_Renders"))
    dpi = int(intake_config(config).get("page_render_dpi", DEFAULT_PAGE_RENDER_DPI))
    written: list[str] = []
    existing: list[str] = []
    scale = dpi / 72.0
    matrix = fitz.Matrix(scale, scale)
    with fitz.open(source) as doc:
        page_count = len(doc)
        selection = select_policy_pages(
            config, stage="render", page_count=page_count, requested_pages=requested_pages
        )
        selection_report = page_selection_report(selection)
        render_dir.mkdir(parents=True, exist_ok=True)
        for page_id in selection_report["effective_pages"]:
            index = int(page_id)
            target = render_dir / f"page-{index:02d}.png"
            if target.exists() and not force:
                existing.append(rel(target))
                continue
            page = doc.load_page(index - 1)
            pix = page.get_pixmap(matrix=matrix, alpha=False)
            pix.save(target)
            written.append(rel(target))
    result = {
        "schema": "translator_page_render.v1",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "config": rel(config_path),
        "source_pdf": rel(source),
        "render_dir": rel(render_dir),
        "dpi": dpi,
        "page_count": page_count,
        "written": written,
        "existing": existing,
        "page_selection": selection_report,
        "status": "pass" if len(written) + len(existing) == len(selection_report["effective_pages"]) else "fail",
    }
    write_json(intake_report_path(config, "page_render_report", "page_render_report.json"), result)
    return result


def extract_text(config_path: Path, *, force: bool = False) -> dict[str, Any]:
    import pdfplumber

    config = read_json(config_path)
    source = root_path(str(config["source_pdf"]))
    target = root_path(intake_config(config).get("raw_text", f"{config['workbench_root']}/Formatted/Source_Text_Raw_EN_v1.txt"))
    target_existed = target.exists()
    target.parent.mkdir(parents=True, exist_ok=True)
    existed = target.exists()
    pages: list[dict[str, Any]] = []
    chunks: list[str] = []
    if existed and not force:
        text = target.read_text(encoding="utf-8")
        result = {
            "schema": "translator_text_extraction.v1",
            "generated_at_utc": datetime.now(timezone.utc).isoformat(),
            "config": rel(config_path),
            "source_pdf": rel(source),
            "raw_text": rel(target),
            "status": "pass",
            "action": "kept_existing",
            "chars": len(text),
            "sha256": sha256_text(text),
        }
        write_json(intake_report_path(config, "text_extraction_report", "text_extraction_report.json"), result)
        return result
    with pdfplumber.open(source) as pdf:
        for index, page in enumerate(pdf.pages, start=1):
            page_text = page.extract_text(layout=True) or ""
            pages.append({"page": index, "chars": len(page_text)})
            chunks.append(f"\n\n<!-- source-page-{index:03d} -->\n\n{page_text.strip()}\n")
    text = "".join(chunks).strip() + "\n"
    target.write_text(text, encoding="utf-8", newline="\n")
    result = {
        "schema": "translator_text_extraction.v1",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "config": rel(config_path),
        "source_pdf": rel(source),
        "raw_text": rel(target),
        "status": "pass",
        "action": "rewritten" if existed else "created",
        "pages": pages,
        "chars": len(text),
        "sha256": sha256_text(text),
    }
    write_json(intake_report_path(config, "text_extraction_report", "text_extraction_report.json"), result)
    return result


def ocr_pages(
    config_path: Path,
    *,
    force: bool = False,
    promote: bool = False,
    requested_pages: list[str] | None = None,
) -> dict[str, Any]:
    config = read_json(config_path)
    intake = intake_config(config)
    render_dir = root_path(intake.get("page_renders", f"{config['workbench_root']}/Images/Page_Renders"))
    if not render_dir.exists():
        raise FileNotFoundError(f"Run render-pages first: {render_dir}")
    images_by_page = rendered_page_images(render_dir)
    if not images_by_page:
        raise FileNotFoundError(f"No page renders found in {render_dir}")
    page_count = max(images_by_page)
    selection = select_policy_pages(
        config, stage="ocr", page_count=page_count, requested_pages=requested_pages
    )
    unavailable = {
        page_id for page_id in selection["physical_selected_pages"] if int(page_id) not in images_by_page
    }
    selection_report = page_selection_report(selection, unavailable_pages=unavailable)
    images = [(int(page_id), images_by_page[int(page_id)]) for page_id in selection_report["effective_pages"]]
    lang = str(intake.get("ocr_language", "eng"))
    psm = str(intake.get("ocr_psm", 6))
    target = root_path(intake.get("ocr_text", f"{config['workbench_root']}/Formatted/{config['project_key']}_Source_Text_OCR_EN_v1.md"))
    raw_target = root_path(intake.get("raw_text", f"{config['workbench_root']}/Formatted/Source_Text_Raw_EN_v1.txt"))
    report = intake_report_path(config, "ocr_report", "ocr_report.json")
    if target.exists() and not force:
        text = target.read_text(encoding="utf-8")
        result = {
            "schema": "translator_page_ocr.v1",
            "generated_at_utc": datetime.now(timezone.utc).isoformat(),
            "config": rel(config_path),
            "render_dir": rel(render_dir),
            "ocr_text": rel(target),
            "status": "pass",
            "action": "kept_existing",
            "promoted_to_raw_text": False,
            "counts": {"pages": len(images), "chars": len(text), "findings": 0},
            "sha256": sha256_text(text),
            "findings": [],
            "page_selection": selection_report,
            "cache": cache_telemetry(),
        }
        if promote:
            raw_target.parent.mkdir(parents=True, exist_ok=True)
            raw_target.write_text(text, encoding="utf-8", newline="\n")
            result["promoted_to_raw_text"] = True
            result["raw_text"] = rel(raw_target)
        write_json(report, result)
        return result
    tess = tesseract_path(config)
    if not tess.exists():
        raise FileNotFoundError(tess)
    cache = processing_cache(config)
    telemetry = cache_telemetry()
    tess_identity = executable_identity(tess, version=str(tooling_config(config).get("tesseract_version") or "unavailable"))
    target.parent.mkdir(parents=True, exist_ok=True)
    chunks: list[str] = []
    pages: list[dict[str, Any]] = []
    findings: list[dict[str, Any]] = []
    for page, image in images:
        ocr = cached_tesseract_result(
            cache,
            telemetry,
            image=image,
            normalized_zone=None,
            tess=tess,
            tess_identity=tess_identity,
            language=lang,
            psm=psm,
            force=force,
        )
        page_text = str(ocr["text"])
        if ocr["returncode"] != 0:
            findings.append(
                {
                    "page": page,
                    "code": "tesseract_failed",
                    "returncode": ocr["returncode"],
                    "stderr": diagnostic_lines(ocr["stderr"]),
                }
            )
        if len(page_text) < 50:
            findings.append({"page": page, "code": "very_short_ocr_page", "chars": len(page_text)})
        chunks.append(f"\n\n<!-- source-page-{page:03d} -->\n\n{page_text}\n")
        pages.append(
            {
                "page": page,
                "image": rel(image),
                "chars": len(page_text),
                "returncode": ocr["returncode"],
                "stderr": diagnostic_lines(ocr["stderr"], limit=3),
            }
        )
    text = "".join(chunks).strip() + "\n"
    target.write_text(text, encoding="utf-8", newline="\n")
    promoted = False
    if promote:
        raw_target.parent.mkdir(parents=True, exist_ok=True)
        raw_target.write_text(text, encoding="utf-8", newline="\n")
        promoted = True
    result = {
        "schema": "translator_page_ocr.v1",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "config": rel(config_path),
        "render_dir": rel(render_dir),
        "tesseract": rel(tess),
        "language": lang,
        "psm": int(psm),
        "ocr_text": rel(target),
        "raw_text": rel(raw_target) if promoted else None,
        "status": "needs_review" if findings else "pass",
        "action": "rewritten" if force else "created",
        "promoted_to_raw_text": promoted,
        "counts": {
            "pages": len(pages),
            "chars": len(text),
            "min_page_chars": min((item["chars"] for item in pages), default=0),
            "max_page_chars": max((item["chars"] for item in pages), default=0),
            "findings": len(findings),
        },
        "sha256": sha256_text(text),
        "pages": pages,
        "findings": findings,
        "page_selection": selection_report,
        "cache": telemetry,
    }
    write_json(report, result)
    return result


def column_ocr_config(config: dict[str, Any]) -> dict[str, Any]:
    defaults = {
        "candidate_markdown": f"{config['workbench_root']}/Translation_Work/Column_OCR_Reconstruction/{config['project_key']}_Column_OCR_Candidate_EN.md",
        "page_chunk_dir": f"{config['workbench_root']}/Translation_Work/Column_OCR_Reconstruction/Source_Pages",
        "crop_dir": f"{config.get('workbench_qa_root', config['workbench_root'] + '/project/QA')}/Column_OCR",
        "report": "column_ocr_reconstruction_report.json",
        "language": intake_config(config).get("ocr_language", "eng"),
        "psm": intake_config(config).get("ocr_psm", 6),
        "zones": [
            {"name": "left", "box": [0.05, 0.06, 0.50, 0.92]},
            {"name": "right", "box": [0.50, 0.06, 0.95, 0.92]},
        ],
        "source_art_strategy": "insert_anchor_then_ocr",
        "skip_ocr_roles": [],
        "auto_detect_columns": False,
    }
    merged = dict(defaults)
    merged.update(config.get("column_ocr_reconstruction", {}))
    return merged


def column_ocr_report_path(config: dict[str, Any]) -> Path:
    value = column_ocr_config(config).get("report", "column_ocr_reconstruction_report.json")
    path = Path(str(value).replace("/", "\\"))
    return path.resolve() if path.is_absolute() else qa_root(config) / path


def column_ocr_candidate_path(config: dict[str, Any]) -> Path:
    return root_path(str(column_ocr_config(config)["candidate_markdown"]))


def column_ocr_chunk_dir(config: dict[str, Any]) -> Path:
    return root_path(str(column_ocr_config(config)["page_chunk_dir"]))


def column_ocr_crop_dir(config: dict[str, Any]) -> Path:
    return root_path(str(column_ocr_config(config)["crop_dir"]))


def crop_box_pixels(box: list[Any], width: int, height: int) -> tuple[int, int, int, int]:
    if len(box) != 4:
        raise ValueError("Column OCR crop box must contain four values.")
    values = [float(item) for item in box]
    if all(0 <= item <= 1 for item in values):
        left, top, right, bottom = values
        pixels = (round(left * width), round(top * height), round(right * width), round(bottom * height))
    else:
        pixels = tuple(round(item) for item in values)
    left, top, right, bottom = pixels
    left = max(0, min(left, width - 1))
    top = max(0, min(top, height - 1))
    right = max(left + 1, min(right, width))
    bottom = max(top + 1, min(bottom, height))
    return left, top, right, bottom


def auto_detect_column_zones(source_image: Image.Image) -> list[dict[str, Any]]:
    gray = source_image.convert("L")
    width, height = gray.size
    histogram_x = [0] * width
    threshold = 245
    for y in range(height):
        for x, value in enumerate(gray.crop((0, y, width, y + 1)).getdata()):
            if value < threshold:
                histogram_x[x] += 1
    active_x = [index for index, count in enumerate(histogram_x) if count > max(3, height // 200)]
    if not active_x:
        return [
            {"name": "left", "box": [0.05, 0.06, 0.50, 0.92], "auto_detected": True},
            {"name": "right", "box": [0.50, 0.06, 0.95, 0.92], "auto_detected": True},
        ]
    left = max(0, min(active_x) - round(width * 0.02))
    right = min(width, max(active_x) + round(width * 0.02))
    mid_start = max(left + 1, round(width * 0.35))
    mid_end = min(right - 1, round(width * 0.65))
    if mid_end <= mid_start:
        split = (left + right) // 2
    else:
        split = min(range(mid_start, mid_end), key=lambda idx: histogram_x[idx])
    top = round(height * 0.06)
    bottom = round(height * 0.92)
    return [
        {"name": "left", "box": [left, top, split, bottom], "auto_detected": True},
        {"name": "right", "box": [split, top, right, bottom], "auto_detected": True},
    ]


def source_art_role_dir(role: str) -> str:
    role = role.casefold()
    if role in {"map", "floorplan"}:
        return "Maps"
    if role == "diagram":
        return "Diagrams"
    if role == "handout":
        return "Handouts"
    if role == "npc":
        return "NPC"
    if role == "atmospheric":
        return "Atmospheric"
    return "Source_Images"


def column_ocr_art_anchors(config: dict[str, Any], target_markdown: Path) -> dict[int, list[dict[str, Any]]]:
    public_root = root_path(str(config.get("public_package_root") or config.get("package_root") or ""))
    anchors: dict[int, list[dict[str, Any]]] = {}
    for item in art_integration_config(config).get("preserved_page_art", []):
        try:
            page = int(item.get("page"))
        except (TypeError, ValueError):
            continue
        role = str(item.get("role") or "source_image")
        target_filename = str(item.get("target_filename") or f"page-{page:03d}-{role}.png")
        role_dir = source_art_role_dir(role)
        target_path = public_root / "Images" / role_dir / target_filename
        target_exists = target_path.exists()
        try:
            ref = target_path.resolve().relative_to(target_markdown.parent.resolve()).as_posix()
        except ValueError:
            ref = os.path.relpath(target_path.resolve(), target_markdown.parent.resolve()).replace("\\", "/")
        anchors.setdefault(page, []).append(
            {
                "role": role,
                "target_path": rel(target_path),
                "target_exists": target_exists,
                "markdown": f"![Preserved source {role}](%s)" % ref,
                "review_notes": item.get("review_notes"),
                "skip_ocr": bool(item.get("skip_ocr", False)),
            }
        )
    return anchors


def dehyphenate_simple_ocr(text: str) -> str:
    return HYPHENATED_LINE_BREAK_RE.sub(r"\1\2", text)


def reconstruct_column_ocr(
    config_path: Path,
    *,
    apply: bool = False,
    force: bool = False,
    requested_pages: list[str] | None = None,
) -> dict[str, Any]:
    config = read_json(config_path)
    cfg = column_ocr_config(config)
    render_dir = page_render_dir(config)
    if not render_dir.exists():
        raise FileNotFoundError(f"Run render-pages first: {render_dir}")
    images_by_page = rendered_page_images(render_dir)
    if not images_by_page:
        raise FileNotFoundError(f"No page renders found in {render_dir}")
    page_count = max(images_by_page)
    selection = select_policy_pages(
        config, stage="column-ocr", page_count=page_count, requested_pages=requested_pages
    )
    unavailable = {
        page_id for page_id in selection["physical_selected_pages"] if int(page_id) not in images_by_page
    }
    selection_report = page_selection_report(selection, unavailable_pages=unavailable)
    policy_validation = page_policy.validate_page_map(page_count, config.get("page_map"))
    policy_pages = {page["id"]: page for page in policy_validation["pages"]}
    images = [(int(page_id), images_by_page[int(page_id)]) for page_id in selection_report["effective_pages"]]
    tess = tesseract_path(config)
    if not tess.exists():
        raise FileNotFoundError(tess)
    cache = processing_cache(config)
    telemetry = cache_telemetry()
    tess_identity = executable_identity(tess, version=str(tooling_config(config).get("tesseract_version") or "unavailable"))

    candidate = column_ocr_candidate_path(config)
    chunk_dir = column_ocr_chunk_dir(config)
    crop_dir = column_ocr_crop_dir(config)
    report = column_ocr_report_path(config)
    lang = str(cfg.get("language") or "eng")
    psm = str(cfg.get("psm") or 6)
    zones = list(cfg.get("zones") or [])
    auto_detect_columns = bool(cfg.get("auto_detect_columns", False))
    if not zones and not auto_detect_columns:
        raise ValueError("column_ocr_reconstruction.zones must contain at least one zone or auto_detect_columns=true.")
    if (candidate.exists() or chunk_dir.exists()) and not force and apply:
        raise FileExistsError("Column OCR candidate outputs already exist; rerun with --force to rewrite.")

    crop_dir.mkdir(parents=True, exist_ok=True)
    if apply:
        candidate.parent.mkdir(parents=True, exist_ok=True)
        chunk_dir.mkdir(parents=True, exist_ok=True)
    anchors = column_ocr_art_anchors(config, candidate)
    findings: list[dict[str, Any]] = []
    page_records: list[dict[str, Any]] = []
    chunks: list[str] = []
    selected_page_numbers = {page for page, _image in images}
    for page, page_anchors in anchors.items():
        if page not in selected_page_numbers:
            continue
        for anchor in page_anchors:
            if not anchor.get("target_exists"):
                findings.append(
                    {
                        "page": page,
                        "code": "missing_source_art_anchor",
                        "target_path": anchor.get("target_path"),
                        "message": "Run preserve-page-art or adjust art_integration.preserved_page_art before accepting this candidate.",
                    }
                )

    for page, image in images:
        page_parts: list[str] = [f"<!-- source-page-{page:03d} -->"]
        for anchor in anchors.get(page, []):
            page_parts.append(str(anchor["markdown"]))
        page_record: dict[str, Any] = {"page": page, "image": rel(image), "zones": [], "anchors": anchors.get(page, [])}
        page_anchors = anchors.get(page, [])
        skip_roles = {str(role).casefold() for role in cfg.get("skip_ocr_roles", [])}
        skip_page_ocr = bool(page_anchors) and any(
            bool(anchor.get("skip_ocr")) or str(anchor.get("role", "")).casefold() in skip_roles for anchor in page_anchors
        )
        with Image.open(image) as source_image:
            width, height = source_image.size
            page_record["image_size"] = {"width": width, "height": height}
            page_zones = policy_pages[f"{page:03d}"]["zones"] or zones or auto_detect_column_zones(source_image)
            if not policy_pages[f"{page:03d}"]["zones"] and not zones:
                page_record["auto_detected_columns"] = True
            if skip_page_ocr:
                page_record["ocr_skipped"] = True
                page_record["skip_reason"] = "source_art_anchor_skip_ocr"
                for zone_index, zone in enumerate(page_zones, start=1):
                    zone_name = str(zone.get("name") or f"zone{zone_index}")
                    try:
                        box = crop_box_pixels(list(zone["box"]), width, height)
                    except Exception as exc:
                        findings.append({"page": page, "zone": zone_name, "code": "invalid_crop_box", "message": str(exc)})
                        continue
                    crop = source_image.crop(box)
                    crop_path = crop_dir / f"page-{page:03d}-{zone_name}.png"
                    crop.save(crop_path)
                    page_record["zones"].append(
                        {
                            "name": zone_name,
                            "box": list(box),
                            "crop": rel(crop_path),
                            "chars": 0,
                            "returncode": None,
                            "ocr_skipped": True,
                        }
                    )
                page_text = "\n\n".join(part.strip() for part in page_parts if part.strip()).strip() + "\n"
                chunks.append(page_text)
                if apply:
                    chunk_path = chunk_dir / f"page_{page:03d}_source_en.md"
                    chunk_path.write_text(page_text, encoding="utf-8", newline="\n")
                    page_record["chunk"] = rel(chunk_path)
                page_record["chars"] = len(page_text)
                page_records.append(page_record)
                continue
            for zone_index, zone in enumerate(page_zones, start=1):
                zone_name = str(zone.get("name") or f"zone{zone_index}")
                try:
                    box = crop_box_pixels(list(zone["box"]), width, height)
                except Exception as exc:
                    findings.append({"page": page, "zone": zone_name, "code": "invalid_crop_box", "message": str(exc)})
                    continue
                crop = source_image.crop(box)
                crop_path = crop_dir / f"page-{page:03d}-{zone_name}.png"
                crop.save(crop_path)
                normalized_zone = {
                    "name": zone_name.strip().casefold(),
                    "box": list(box),
                }
                crop_sha256 = sha256_file(crop_path) if crop_path.exists() else sha256_file(image)
                ocr = cached_tesseract_result(
                    cache,
                    telemetry,
                    image=crop_path,
                    normalized_zone=normalized_zone,
                    tess=tess,
                    tess_identity=tess_identity,
                    language=lang,
                    psm=psm,
                    force=force,
                    encoding="utf-8",
                    input_sha256=crop_sha256,
                )
                zone_text = dehyphenate_simple_ocr(str(ocr["text"]))
                if ocr["returncode"] != 0:
                    findings.append(
                        {
                            "page": page,
                            "zone": zone_name,
                            "code": "tesseract_failed",
                            "returncode": ocr["returncode"],
                            "stderr": diagnostic_lines(ocr["stderr"]),
                        }
                    )
                if len(zone_text) < int(zone.get("min_chars", 20)):
                    findings.append({"page": page, "zone": zone_name, "code": "very_short_zone_ocr", "chars": len(zone_text)})
                page_record["zones"].append(
                    {
                        "name": zone_name,
                        "box": list(box),
                        "crop": rel(crop_path),
                        "chars": len(zone_text),
                        "returncode": ocr["returncode"],
                        "stderr": diagnostic_lines(ocr["stderr"], limit=3),
                    }
                )
                if zone_text:
                    page_parts.append(zone_text)
        page_text = "\n\n".join(part.strip() for part in page_parts if part.strip()).strip() + "\n"
        chunks.append(page_text)
        if apply:
            chunk_path = chunk_dir / f"page_{page:03d}_source_en.md"
            chunk_path.write_text(page_text, encoding="utf-8", newline="\n")
            page_record["chunk"] = rel(chunk_path)
        page_record["chars"] = len(page_text)
        page_records.append(page_record)

    text = "\n\n".join(chunk.strip() for chunk in chunks).strip() + "\n"
    if apply:
        candidate.write_text(text, encoding="utf-8", newline="\n")
    result = {
        "schema": "translator_column_ocr_reconstruction.v1",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "config": rel(config_path),
        "mode": "apply" if apply else "check_only",
        "status": "needs_review" if findings else "pass",
        "source": "page render column-aware OCR candidate",
        "render_dir": rel(render_dir),
        "crop_dir": rel(crop_dir),
        "candidate_markdown": rel(candidate),
        "page_chunk_dir": rel(chunk_dir),
        "language": lang,
        "psm": int(psm),
        "zones": zones if zones else "auto",
        "auto_detect_columns": auto_detect_columns,
        "source_art_strategy": str(cfg.get("source_art_strategy") or "insert_anchor_then_ocr"),
        "approval_state": {
            "candidate_only": True,
            "source_reconstruction_accepted": False,
            "requires_qa_assembly_pass": True,
        },
        "source_reconstruction_gate_changed": False,
        "counts": {
            "pages": len(page_records),
            "chars": len(text),
            "page_chunks_written": len(page_records) if apply else 0,
            "image_refs": len(re.findall(r"!\[[^\]]*\]\([^)]+\)", text)),
            "findings": len(findings),
        },
        "sha256": sha256_text(text),
        "pages": page_records,
        "findings": findings,
        "page_selection": selection_report,
        "cache": telemetry,
        "next_steps": [
            "Review and clean page chunks against page renders.",
            "Assemble Source_Text_Full_EN from accepted chunks.",
            "Only then set source_reconstruction_accepted=true if QA passes.",
        ],
    }
    write_json(report, result)
    return result


def split_raw_text_pages(text: str) -> list[dict[str, Any]]:
    matches = list(RAW_PAGE_RE.finditer(text))
    marker_type = "raw_page"
    if not matches:
        matches = list(SOURCE_PAGE_RE.finditer(text))
        marker_type = "source_page"
    if not matches:
        return [{"page": None, "marker_type": "none", "text": text}]
    pages: list[dict[str, Any]] = []
    for index, match in enumerate(matches):
        start = match.end()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        pages.append({"page": int(match.group("page")), "marker_type": marker_type, "text": text[start:end].strip()})
    return pages


def spaced_caps_line(line: str) -> bool:
    stripped = line.strip()
    if len(stripped) < 3:
        return False
    if stat_like_line(stripped):
        return False
    letters = [char for char in stripped if char.isalpha()]
    spaces = stripped.count(" ")
    return bool(letters) and spaces >= max(3, len(letters) // 2) and stripped.upper() == stripped


def stat_like_line(line: str) -> bool:
    tokens = re.findall(r"\b(?:STR|CON|SIZ|INT|POW|DEX|APP|EDU|SAN|HP|MOV|DB|BUILD)\b", line.upper())
    return len(tokens) >= 3 or ("HP" in tokens and len(tokens) >= 2)


def hyphenated_line_break_records(text: str, *, artifact: str, limit: int = 50) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    lines = text.splitlines()
    for index, line in enumerate(lines):
        left = line.strip()
        match = re.search(rf"({LETTER_RUN}{{2,}})-\s*$", left, re.U)
        if not match:
            continue
        for next_index in range(index + 1, min(len(lines), index + 8)):
            right = lines[next_index].strip()
            if not right:
                continue
            if right.startswith("<!--") or right.startswith("!["):
                continue
            if re.fullmatch(r"(?:source\s+)?page\s+\d{1,4}", right, re.I):
                continue
            right_match = re.match(rf"({LETTER_RUN}{{2,}})", right, re.U)
            if not right_match:
                continue
            records.append(
                {
                    "artifact": artifact,
                    "line": index + 1,
                    "next_line": next_index + 1,
                    "left": left[-120:],
                    "right": right[:120],
                    "candidate": f"{match.group(1)}-{right_match.group(1)}",
                }
            )
            break
        if len(records) >= limit:
            break
    return records


def source_text_qa(config_path: Path, *, requested_pages: list[str] | None = None) -> dict[str, Any]:
    config = read_json(config_path)
    raw_path = root_path(intake_config(config).get("raw_text", f"{config['workbench_root']}/Formatted/Source_Text_Raw_EN_v1.txt"))
    if not raw_path.exists():
        raise FileNotFoundError(raw_path)
    text = raw_path.read_text(encoding="utf-8")
    pages = split_raw_text_pages(text)
    selection = select_policy_pages(
        config,
        stage="extract-text",
        page_count=page_count_from_text_pages(pages),
        requested_pages=requested_pages,
    )
    selection_report = page_selection_report(selection)
    effective_numbers = {int(page_id) for page_id in selection_report["effective_pages"]}
    pages = [
        page
        for page in pages
        if page["page"] in effective_numbers or (page["page"] is None and 1 in effective_numbers)
    ]
    page_reports: list[dict[str, Any]] = []
    findings: list[dict[str, Any]] = []
    hyphen_breaks = HYPHENATED_LINE_BREAK_RE.findall(text)
    hyphen_break_records = hyphenated_line_break_records(
        text,
        artifact="raw_text",
        limit=int(intake_config(config).get("max_hyphenated_line_break_examples", 50)),
    )
    for page in pages:
        page_text = page["text"]
        lines = page_text.splitlines()
        nonempty = [line for line in lines if line.strip()]
        spaced_caps = [line.strip() for line in nonempty if spaced_caps_line(line)]
        stat_like = [line.strip() for line in nonempty if stat_like_line(line)]
        page_report = {
            "page": page["page"],
            "marker_type": page["marker_type"],
            "chars": len(page_text),
            "nonempty_lines": len(nonempty),
            "spaced_caps_lines": spaced_caps[:10],
            "stat_like_lines": stat_like[:10],
            "starts_with": page_text[:120].replace("\n", " "),
        }
        if len(page_text.strip()) < 50:
            findings.append({"page": page["page"], "code": "very_short_or_empty_page", "chars": len(page_text.strip())})
        if spaced_caps:
            findings.append({"page": page["page"], "code": "decorative_spaced_caps", "count": len(spaced_caps), "examples": spaced_caps[:3]})
        if stat_like:
            findings.append({"page": page["page"], "code": "stat_like_lines", "count": len(stat_like), "examples": stat_like[:3]})
        page_reports.append(page_report)
    if hyphen_breaks or hyphen_break_records:
        examples = ["-".join(item) for item in hyphen_breaks[:10]]
        examples.extend(item["candidate"] for item in hyphen_break_records[:10] if item["candidate"] not in examples)
        findings.append({"page": None, "code": "hyphenated_line_breaks", "count": max(len(hyphen_breaks), len(hyphen_break_records)), "examples": examples[:10]})
    result = {
        "schema": "translator_source_text_qa.v1",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "config": rel(config_path),
        "raw_text": rel(raw_path),
        "status": "needs_review" if findings else "pass",
        "counts": {
            "pages": len(page_reports),
            "chars": len(text),
            "findings": len(findings),
            "hyphenated_line_breaks": max(len(hyphen_breaks), len(hyphen_break_records)),
            "very_short_pages": sum(1 for item in findings if item["code"] == "very_short_or_empty_page"),
            "decorative_spaced_caps_pages": sum(1 for item in findings if item["code"] == "decorative_spaced_caps"),
            "stat_like_pages": sum(1 for item in findings if item["code"] == "stat_like_lines"),
        },
        "pages": page_reports,
        "findings": findings,
        "page_selection": selection_report,
    }
    write_json(intake_report_path(config, "source_text_qa_report", "source_text_qa_report.json"), result)
    return result


def source_page_marker(page: int | None) -> str:
    return f"<!-- source-page-{int(page):03d} -->" if page is not None else "<!-- source-page-unknown -->"


def slugify(text: str) -> str:
    mapping = {
        "а": "a", "б": "b", "в": "v", "г": "g", "д": "d", "е": "e", "ё": "e",
        "ж": "zh", "з": "z", "и": "i", "й": "i", "к": "k", "л": "l", "м": "m",
        "н": "n", "о": "o", "п": "p", "р": "r", "с": "s", "т": "t", "у": "u",
        "ф": "f", "х": "h", "ц": "ts", "ч": "ch", "ш": "sh", "щ": "sch",
        "ъ": "", "ы": "y", "ь": "", "э": "e", "ю": "yu", "я": "ya",
    }
    text = "".join(mapping.get(ch, ch) for ch in text.lower())
    return re.sub(r"[^a-z0-9]+", "-", text).strip("-") or "section"


def unique_slug(title: str, used: dict[str, int]) -> str:
    base = slugify(title)
    used[base] = used.get(base, 0) + 1
    return base if used[base] == 1 else f"{base}-{used[base]}"


def inline_markdown(text: str) -> str:
    text = re.sub(r"\s*<!--.*?-->\s*", " ", text, flags=re.DOTALL).strip()
    protected: dict[str, str] = {}

    def protect_escape(match: re.Match[str]) -> str:
        token = f"\x00NRI_ESC_{len(protected)}\x00"
        protected[token] = html_lib.escape(match.group(1))
        return token

    # CommonMark escapes must become literal punctuation before the bounded
    # emphasis parser runs.  Without this guard ``\*`` leaks a slash and may
    # open a false emphasis span across unrelated text.
    text = re.sub(r"\\([\\`*{}\[\]()#+\-.!_>])", protect_escape, text)
    escaped = html_lib.escape(text)
    escaped = re.sub(r"`([^`]+)`", r"<code>\1</code>", escaped)
    escaped = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", escaped)
    escaped = re.sub(r"\*([^*]+)\*", r"<em>\1</em>", escaped)
    escaped = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r'<a href="\2">\1</a>', escaped)
    for token, literal in protected.items():
        escaped = escaped.replace(token, literal)
    return escaped


def render_markdown_paragraph(lines: list[str]) -> str:
    """Render inline Markdown while preserving CommonMark hard line breaks."""

    rendered: list[str] = []
    for index, line in enumerate(lines):
        hard_break = line.endswith("  ")
        rendered.append(inline_markdown(line.rstrip() if hard_break else line.strip()))
        if index + 1 < len(lines):
            rendered.append("<br>\n" if hard_break else " ")
    return "".join(rendered)


STRUCTURAL_ANCHOR_RE = re.compile(r'<a id="([A-Za-z0-9_-]+)"></a>')
STRUCTURAL_TABLE_RE = re.compile(
    r'<table>(?:<tr>(?:(?:<td(?: colspan="[1-9][0-9]*")?>(?:[^<>]|<br>)*</td>)|'
    r'(?:<th colspan="[1-9][0-9]*">(?:[^<>]|<br>)*</th>))+</tr>)+</table>'
)


def render_structural_html(line: str) -> str | None:
    """Render only the source format's exact anchor and table vocabulary.

    Arbitrary raw HTML remains escaped by the normal paragraph path.  This
    narrow allowlist is sufficient for accepted reader masters, whose stable
    cross-reference anchors and compact tables are already validated by their
    package gate.
    """

    stripped = line.strip()
    if STRUCTURAL_ANCHOR_RE.fullmatch(stripped):
        return stripped
    if STRUCTURAL_TABLE_RE.fullmatch(stripped):
        return f'<div class="table-wrap raw-html-table">{stripped}</div>'
    return None


def split_leading_structural_anchors(line: str) -> tuple[str, str]:
    """Return strict leading anchors and the Markdown remainder.

    Reader masters sometimes place a stable anchor immediately before a
    run-in label on the same line.  Only the existing anchor vocabulary is
    admitted; attributes and arbitrary raw HTML remain on the escaped
    paragraph path.
    """

    remainder = line.strip()
    anchors: list[str] = []
    while True:
        match = STRUCTURAL_ANCHOR_RE.match(remainder)
        if not match:
            break
        anchors.append(match.group(0))
        remainder = remainder[match.end():].lstrip()
    return "".join(anchors), remainder


def markdown_table_class(lines: list[str]) -> str:
    if not lines:
        return ""
    header = [cell.strip().upper() for cell in lines[0].strip().strip("|").split("|")]
    header_set = set(header)
    if (
        {"СИЛ", "ВЫН", "ТЕЛ", "ИНТ", "МОЩ", "ЛВК", "НАР", "ОБР", "РАС", "ПЗ"}.issubset(header_set)
        or {"СИЛ", "ВЫН", "РАЗ", "ИНТ", "МОЩ", "ЛВК", "ВНЕШ", "ОБР", "РАС", "ПЗ"}.issubset(header_set)
    ):
        return " statblock-attributes-table"
    if {"БКУ", "КПМЛ", "СКО", "ПМ"}.issubset(header_set):
        return " statblock-derived-table"
    if {"ОРУЖИЕ / ДЕЙСТВИЕ", "ЗНАЧЕНИЕ"}.issubset(header_set) or {"ДЕЙСТВИЕ", "ЗНАЧЕНИЕ / УРОН"}.issubset(header_set):
        return " statblock-actions-table"
    if {"СТИМУЛ", "ЗНАЧЕНИЕ", "УБЕЖДЕНИЕ"}.issubset(header_set) or {"СТИМУЛ", "ЗНАЧ.", "УТВЕРЖДЕНИЕ"}.issubset(header_set):
        return " statblock-dune-drives-table"
    if {"НАВЫК", "ЗНАЧЕНИЕ", "СПЕЦИАЛИЗАЦИИ"}.issubset(header_set) or {"НАВЫК", "ЗНАЧ.", "ФОКУС"}.issubset(header_set):
        return " statblock-dune-skills-table"
    return ""


def html_class_token_count(html_text: str, token: str) -> int:
    count = 0
    for match in re.finditer(r'class=["\']([^"\']*)["\']', html_text, re.I):
        if token in match.group(1).split():
            count += 1
    return count


def render_markdown_table(lines: list[str]) -> str:
    rows: list[str] = []
    for index, line in enumerate(lines):
        if index == 1:
            continue
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        tag = "th" if index == 0 else "td"
        rows.append("<tr>" + "".join(f"<{tag}>{inline_markdown(cell)}</{tag}>" for cell in cells) + "</tr>")
    table_class = markdown_table_class(lines)
    class_attr = f' class="{table_class.strip()}"' if table_class else ""
    return f'<div class="table-wrap{table_class}"><table{class_attr}>\n' + "\n".join(rows) + "\n</table></div>"


def render_blockquote_lines(lines: list[str], source_path: Path, html_path: Path, *, statblock: bool = False, heading_offset: int = 1) -> str:
    out: list[str] = []
    i = 0
    while i < len(lines):
        stripped = lines[i].strip()
        if not stripped:
            i += 1
            continue
        image_html = render_markdown_image(stripped, source_path, html_path)
        if image_html:
            out.append(image_html)
            i += 1
            continue
        if stripped.startswith("|") and i + 1 < len(lines) and re.match(r"^\|\s*:?-{3,}", lines[i + 1].strip()):
            table_lines = [stripped, lines[i + 1].strip()]
            i += 2
            while i < len(lines) and lines[i].strip().startswith("|"):
                table_lines.append(lines[i].strip())
                i += 1
            out.append(render_markdown_table(table_lines))
            continue
        if stripped.startswith("#"):
            level = min(len(stripped) - len(stripped.lstrip("#")) + heading_offset, 6)
            title = stripped.lstrip("#").strip()
            out.append(f"<h{level}>{inline_markdown(title)}</h{level}>")
            i += 1
            continue
        if stripped.startswith("- "):
            items: list[str] = []
            while i < len(lines):
                if lines[i].strip().startswith("- "):
                    items.append(lines[i].strip()[2:].strip()); i += 1
                elif not lines[i].strip() and i + 1 < len(lines) and lines[i + 1].strip().startswith("- "):
                    i += 1
                else:
                    break
            out.append("<ul>\n" + "\n".join(f"<li>{inline_markdown(item)}</li>" for item in items) + "\n</ul>")
            continue
        if re.match(r"^\d+\.\s+", stripped):
            items = []
            while i < len(lines):
                if re.match(r"^\d+\.\s+", lines[i].strip()):
                    items.append(re.sub(r"^\d+\.\s+", "", lines[i].strip())); i += 1
                elif not lines[i].strip() and i + 1 < len(lines) and re.match(r"^\d+\.\s+", lines[i + 1].strip()):
                    i += 1
                else:
                    break
            out.append("<ol>\n" + "\n".join(f"<li>{inline_markdown(item)}</li>" for item in items) + "\n</ol>")
            continue
        paragraph = [lines[i].strip() if not lines[i].endswith("  ") else lines[i].lstrip()]
        i += 1
        while i < len(lines):
            nxt = lines[i].strip()
            if not nxt or nxt.startswith(("#", "|", "- ", "![", "<!--")) or re.match(r"^\d+\.\s+", nxt):
                break
            paragraph.append(lines[i].strip() if not lines[i].endswith("  ") else lines[i].lstrip())
            i += 1
        content = "<br>\n".join(inline_markdown(line.rstrip()) for line in paragraph) if statblock else render_markdown_paragraph(paragraph)
        out.append(f"<p>{content}</p>")
    return "\n".join(out)


def render_markdown_image(line: str, source_path: Path, html_path: Path) -> str | None:
    match = re.match(r"!\[([^\]]*)\]\(([^)]+)\)(?:\{([^}]*)\})?\s*$", line.strip())
    if not match:
        return None
    alt = match.group(1).strip()
    ref = match.group(2).strip()
    attr = (match.group(3) or "").strip()
    classes: list[str] = []
    if attr:
        for token in attr.split():
            if token.startswith("."):
                candidate = re.sub(r"[^A-Za-z0-9_-]", "", token[1:])
                if candidate:
                    classes.append(candidate)
    if "://" in ref or ref.startswith("data:"):
        src = ref
    else:
        candidate = (source_path.parent / ref.replace("/", "\\")).resolve()
        src = os.path.relpath(candidate, html_path.parent).replace("\\", "/") if candidate.exists() else ref
    class_attr = f' class="{" ".join(classes)}"' if classes else ""
    caption = f"<figcaption>{inline_markdown(alt)}</figcaption>" if alt else ""
    return f'<figure{class_attr}><img src="{html_lib.escape(src)}" alt="{html_lib.escape(alt)}">{caption}</figure>'


def render_keeper_art_block(
    line: str,
    source_path: Path,
    html_path: Path,
    art_classes: dict[str, str] | None = None,
) -> str | None:
    """Render the strictly generated art block used by canonical manifests."""
    match = re.fullmatch(
        r'<div class="keeper-art-block" data-placement-id="([A-Za-z0-9_-]+)" '
        r'data-anchor-id="([A-Za-z0-9_-]+)"(?P<attrs>[^>]*)>\s*'
        r'<img id="[A-Za-z0-9_-]+-image" src="((?:\.\./)?Images(?:_v\d+)?/[^"<>]+|(?:\.\./)?Images/Runtime_Assets/[^"<>]+)" '
        r'alt="([^"]*)">\s*</div>',
        line.strip(),
    )
    if not match:
        return None
    placement_id = match.group(1)
    anchor_id = match.group(2)
    extra_attrs = match.group("attrs") or ""
    ref = match.group(4)
    alt = match.group(5)
    # KeeperBook lives in For_Keeper while the managed runtime assets are
    # package-relative under Images. Do not enable arbitrary raw HTML here.
    candidate_base = source_path.parent if ref.startswith("../") else source_path.parent.parent
    candidate = (candidate_base / ref.replace("/", "\\")).resolve()
    src = os.path.relpath(candidate, html_path.parent).replace("\\", "/") if candidate.exists() else ref
    layout_class = (art_classes or {}).get(placement_id, "").strip()
    classes = " ".join(part for part in ("keeper-art-block", layout_class) if part)
    source_attrs = ""
    for name in ("data-source-page", "data-source-anchor-id", "data-source-anchor-kind", "data-source-anchor-method"):
        attr_match = re.search(rf'\s{name}="([^"]*)"', extra_attrs)
        if attr_match:
            source_attrs += f' {name}="{html_lib.escape(attr_match.group(1))}"'
    return (
        f'<figure class="{html_lib.escape(classes)}" data-placement-id="{html_lib.escape(placement_id)}" '
        f'data-anchor-id="{html_lib.escape(anchor_id)}"{source_attrs}><img src="{html_lib.escape(src)}" '
        f'alt="{html_lib.escape(alt)}"></figure>'
    )


def markdown_to_review_html(
    md: str,
    *,
    source_path: Path,
    html_path: Path,
    art_classes: dict[str, str] | None = None,
) -> tuple[str, list[dict[str, Any]], int]:
    lines = md.splitlines()
    out: list[str] = []
    toc: list[dict[str, Any]] = []
    used_slugs: dict[str, int] = {}
    pending_anchor_ids: list[str] = []
    page_count = 0
    current_page: str | None = None
    i = 0
    while i < len(lines):
        stripped = lines[i].strip()
        page_match = re.match(r"<!--\s*(?:source-page|pdf-page)-(\d{3})\s*-->", stripped)
        if page_match:
            pending_anchor_ids = []
            if current_page is not None:
                out.append("</section>")
            current_page = page_match.group(1)
            page_count += 1
            out.append(f"<!-- pdf-page-{current_page} -->")
            out.append(f'<section class="review-page" id="page-{current_page}" data-page="{current_page}">')
            out.append(f'<div class="page-marker">source page {current_page}</div>')
            i += 1
            continue
        if not stripped:
            i += 1
            continue
        semantic_start = re.fullmatch(r"<!--\s*semantic-span-start:\s*([A-Za-z0-9_-]+)\s*;\s*id:\s*([A-Za-z0-9_-]+)\s*-->", stripped)
        if semantic_start:
            kind, semantic_id = semantic_start.group(1).casefold(), semantic_start.group(2)
            if kind != "statblock":
                raise ValueError(f"unsupported semantic kind: {kind}")
            end_marker = f"<!-- semantic-span-end: {kind}; id: {semantic_id} -->"
            end_index = i + 1
            while end_index < len(lines) and lines[end_index].strip() != end_marker:
                if "semantic-span-" in lines[end_index]:
                    raise ValueError("semantic span markers overlap or mismatch")
                end_index += 1
            if end_index >= len(lines):
                raise ValueError("semantic span end marker is missing")
            inner = render_blockquote_lines(lines[i + 1:end_index], source_path, html_path, statblock=True, heading_offset=0)
            out.append(f'<section class="statblock-card" data-semantic-kind="statblock" data-semantic-id="{html_lib.escape(semantic_id)}">{inner}</section>')
            i = end_index + 1
            continue
        if re.fullmatch(r"<!--\s*semantic-span-end:.*-->", stripped):
            raise ValueError("semantic span end marker is unmatched")
        if stripped.startswith("<!--"):
            i += 1
            continue
        structural_html = render_structural_html(stripped)
        if structural_html:
            out.append(structural_html)
            anchor_ids = re.findall(r'\bid=["\']([^"\']+)["\']', structural_html, re.I)
            pending_anchor_ids = anchor_ids if anchor_ids else []
            i += 1
            continue
        leading_anchors, anchored_remainder = split_leading_structural_anchors(stripped)
        if leading_anchors and anchored_remainder:
            out.append(leading_anchors)
            pending_anchor_ids = re.findall(r'\bid=["\']([^"\']+)["\']', leading_anchors, re.I)
            stripped = anchored_remainder
        keeper_art_html = render_keeper_art_block(stripped, source_path, html_path, art_classes=art_classes)
        if keeper_art_html:
            out.append(keeper_art_html)
            i += 1
            continue
        image_html = render_markdown_image(stripped, source_path, html_path)
        if image_html:
            out.append(image_html)
            i += 1
            continue
        if stripped.startswith("|") and i + 1 < len(lines) and re.match(r"^\|\s*:?-{3,}", lines[i + 1].strip()):
            table_lines = [stripped, lines[i + 1].strip()]
            i += 2
            while i < len(lines) and lines[i].strip().startswith("|"):
                table_lines.append(lines[i].strip())
                i += 1
            out.append(render_markdown_table(table_lines))
            continue
        if stripped.startswith("#"):
            level = min(len(stripped) - len(stripped.lstrip("#")), 6)
            title = stripped[level:].strip()
            heading_id = unique_slug(title, used_slugs)
            out.append(f'<h{level} id="{heading_id}">{inline_markdown(title)}</h{level}>')
            if level <= 3:
                toc.append({
                    "level": level,
                    "title": title,
                    "href": heading_id,
                    "page": current_page,
                    "source_anchor_ids": list(pending_anchor_ids),
                })
            pending_anchor_ids = []
            i += 1
            continue
        if stripped.startswith(">"):
            quote_lines: list[str] = []
            while i < len(lines) and lines[i].lstrip().startswith(">"):
                raw_quote = lines[i].lstrip()[1:]
                quote_lines.append(raw_quote[1:] if raw_quote.startswith(" ") else raw_quote)
                i += 1
            if quote_lines:
                semantic_directive = re.fullmatch(r"<!--\s*semantic-kind:\s*([A-Za-z0-9_-]+)\s*-->", quote_lines[0])
                if semantic_directive:
                    raise ValueError("semantic kind must use paired neutral span markers")
            callout_class = "review-callout"
            if quote_lines:
                directive = re.fullmatch(r"<!--\s*callout-class:\s*([A-Za-z0-9_-]+)\s*-->", quote_lines[0])
                if directive:
                    callout_class = f"{callout_class} {directive.group(1)}"
                    quote_lines = quote_lines[1:]
            # Legacy callout transport remains intentionally separate from
            # governed semantic directives for backward-compatible packages.
            inner = render_blockquote_lines(quote_lines, source_path, html_path, statblock="statblock-card" in callout_class.split())
            out.append(f'<blockquote class="{callout_class}">{inner}</blockquote>')
            continue
        if stripped.startswith("- "):
            items: list[str] = []
            while i < len(lines) and lines[i].strip().startswith("- "):
                items.append(lines[i].strip()[2:].strip())
                i += 1
            out.append("<ul>\n" + "\n".join(f"<li>{inline_markdown(item)}</li>" for item in items) + "\n</ul>")
            continue
        ordered_item = re.match(r"^(\d+)\.\s+", stripped)
        if ordered_item:
            start = int(ordered_item.group(1))
            items: list[str] = []
            while i < len(lines) and re.match(r"^\d+\.\s+", lines[i].strip()):
                items.append(re.sub(r"^\d+\.\s+", "", lines[i].strip()))
                i += 1
            start_attr = f' start="{start}"' if start != 1 else ""
            out.append(f"<ol{start_attr}>\n" + "\n".join(f"<li>{inline_markdown(item)}</li>" for item in items) + "\n</ol>")
            continue

        # ``stripped`` may be the Markdown remainder after one or more leading
        # structural anchors were emitted above.  Re-reading ``lines[i]`` here
        # would escape and duplicate those anchors inside the paragraph.
        paragraph = [
            stripped
            if leading_anchors
            else (lines[i].strip() if not lines[i].endswith("  ") else lines[i].lstrip())
        ]
        i += 1
        while i < len(lines):
            nxt = lines[i].strip()
            if (
                not nxt
                or nxt.startswith(("#", ">", "|", "- ", "![", "<!--"))
                or render_structural_html(nxt) is not None
                or bool(split_leading_structural_anchors(nxt)[0])
                or re.match(r"^\d+\.\s+", nxt)
            ):
                break
            paragraph.append(lines[i].strip() if not lines[i].endswith("  ") else lines[i].lstrip())
            i += 1
        out.append(f"<p>{render_markdown_paragraph(paragraph)}</p>")
    if current_page is not None:
        out.append("</section>")
    return "\n".join(out), toc, page_count


def review_html_config(config: dict[str, Any]) -> dict[str, Any]:
    return config.get("review_html", {})


def review_source_markdown_path(config: dict[str, Any]) -> Path:
    review = review_html_config(config)
    if review.get("source_markdown"):
        return root_path(str(review["source_markdown"]))
    outputs = config.get("production_outputs", {})
    if outputs.get("keeper_markdown") and root_path(str(outputs["keeper_markdown"])).exists():
        return root_path(str(outputs["keeper_markdown"]))
    intake = intake_config(config)
    if intake.get("normalized_text"):
        return root_path(str(intake["normalized_text"]))
    if outputs.get("source_full_ru"):
        return root_path(str(outputs["source_full_ru"]))
    raise KeyError("review_html.source_markdown")


def review_html_path(config: dict[str, Any]) -> Path:
    review = review_html_config(config)
    if review.get("output_html"):
        return root_path(str(review["output_html"]))
    key = str(config.get("project_key", "package"))
    return qa_root(config) / "Review_HTML" / f"{key}_Review.html"


def review_html_report_path(config: dict[str, Any]) -> Path:
    review = review_html_config(config)
    value = review.get("report", "review_html_report.json")
    path = Path(str(value).replace("/", "\\"))
    return path.resolve() if path.is_absolute() else qa_root(config) / path


def build_review_toc(toc: list[dict[str, Any]]) -> str:
    if not toc:
        return ""
    lines = ['<nav id="toc" class="review-toc"><h1>Оглавление</h1><ol>']
    for item in toc:
        level = int(item["level"])
        title = html_lib.escape(str(item["title"]))
        href = html_lib.escape(str(item["href"]))
        page = item.get("page")
        page_suffix = f' <span class="toc-page">p.{html_lib.escape(str(page))}</span>' if page else ""
        lines.append(f'<li class="toc-level-{level}"><a href="#{href}">{title}</a>{page_suffix}</li>')
    lines.append("</ol></nav>")
    return "\n".join(lines)


def build_review_html_document(config: dict[str, Any], body: str, toc_html: str) -> str:
    title = package_title(config)
    lang = str(config.get("html_lang") or config.get("language_target") or "ru")
    css = """
body { margin: 0; background: #eee2ca; color: #25160f; font: 18px/1.5 Georgia, "Times New Roman", serif; }
main { max-width: 980px; margin: 0 auto; padding: 32px 28px 64px; background: #fffaf0; }
h1, h2, h3, h4, h5, h6 { color: #6b2d12; line-height: 1.16; margin: 1.15em 0 .35em; }
h1 { font-size: 2rem; border-bottom: 2px solid #9a4b24; padding-bottom: .15em; text-transform: uppercase; font-weight: 700; }
h2 { font-size: 1.45rem; border-bottom: 1px solid #c7a675; padding-bottom: .12em; text-transform: none; font-weight: 700; }
h3, h4, h5, h6 { font-size: 1.18rem; text-transform: none; font-weight: 400; }
a { color: #7a3214; }
.review-toc { padding: 16px 18px; margin: 0 0 28px; background: #f2e2c2; border: 1px solid #c7a675; }
.review-toc h1 { margin-top: 0; font-size: 1.35rem; }
.review-toc ol { columns: 2; padding-left: 24px; }
.review-toc li { break-inside: avoid; margin: 0 0 6px; }
.review-toc .toc-level-2 { margin-left: 1em; }
.review-toc .toc-level-3 { margin-left: 2em; font-size: .92em; }
.toc-page { color: #826a4c; font-size: .85em; }
.review-page { padding: 18px 0 34px; border-bottom: 1px solid #d7c59e; }
.page-marker { display: inline-block; margin: 0 0 12px; padding: 3px 8px; background: #8f3d19; color: #fff; border-radius: 3px; font: 700 13px/1.2 Arial, sans-serif; }
blockquote.review-callout { margin: 1.2em 0; padding: .8em 1em; border-left: 5px solid #8f3d19; background: #f0dfbd; }
.table-wrap { overflow-x: auto; margin: 1em 0; }
table { width: 100%; border-collapse: collapse; font-size: .92em; }
th, td { border: 1px solid #c7a675; padding: 6px 8px; vertical-align: top; }
th { background: #e8d4ad; text-align: left; }
figure { margin: 1.2em 0; text-align: center; }
figure img { max-width: 100%; height: auto; }
figcaption { color: #6f5b3c; font-size: .88em; margin-top: .35em; }
code { background: #f0e4cf; padding: 1px 4px; border-radius: 2px; }
@media print { body { background: #fff; } main { max-width: none; } .review-page { break-inside: avoid-page; } .review-toc { break-after: page; } }
"""
    return f"""<!doctype html>
<html lang="{html_lib.escape(lang)}">
<head>
  <meta charset="utf-8">
  <title>{html_lib.escape(title)} - Review HTML</title>
  <style>{css}</style>
</head>
<body>
<main>
{toc_html}
{body}
</main>
</body>
</html>
"""


def build_review_html(config_path: Path, *, force: bool = False) -> dict[str, Any]:
    config = read_json(config_path)
    source = review_source_markdown_path(config)
    target = review_html_path(config)
    report = review_html_report_path(config)
    if not source.exists():
        raise FileNotFoundError(source)
    target_existed = target.exists()
    if target.exists() and not force:
        html_text = target.read_text(encoding="utf-8")
        digest = sha256_text(html_text)
        counts: dict[str, Any] = {
            "html_bytes": len(html_text.encode("utf-8")),
            "headings": len(re.findall(r"<h[1-6]\b", html_text)),
            "source_pages": len(re.findall(r'class="review-page"', html_text)),
            "findings": 0,
        }
        if report.exists():
            previous = read_json(report)
            if previous.get("sha256") == digest and isinstance(previous.get("counts"), dict):
                counts.update(previous["counts"])
        result = {
            "schema": "translator_review_html.v1",
            "generated_at_utc": datetime.now(timezone.utc).isoformat(),
            "config": rel(config_path),
            "source_markdown": rel(source),
            "review_html": rel(target),
            "status": "pass",
            "action": "kept_existing",
            "counts": counts,
            "sha256": digest,
        }
        write_json(report, result)
        return result
    md = source.read_text(encoding="utf-8")
    target.parent.mkdir(parents=True, exist_ok=True)
    body, toc, source_pages = markdown_to_review_html(md, source_path=source, html_path=target)
    html_text = build_review_html_document(config, body, build_review_toc(toc))
    target.write_text(html_text, encoding="utf-8", newline="\n")
    refs = html_refs(html_text)
    resolved = [(ref, (target.parent / ref.replace("/", "\\")).resolve()) for ref in refs]
    missing = [ref for ref, path in resolved if not path.exists() and "://" not in ref and not ref.startswith("data:")]
    findings = [{"code": "missing_image_ref", "message": ref} for ref in missing]
    result = {
        "schema": "translator_review_html.v1",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "config": rel(config_path),
        "source_markdown": rel(source),
        "review_html": rel(target),
        "status": "needs_review" if not findings else "fail",
        "action": "rewritten" if target_existed else "created",
        "counts": {
            "html_bytes": len(html_text.encode("utf-8")),
            "headings": len(toc),
            "source_pages": source_pages,
            "image_refs": len(refs),
            "missing_image_refs": len(missing),
            "findings": len(findings),
        },
        "sha256": sha256_text(html_text),
        "findings": findings,
    }
    write_json(report, result)
    return result


def production_html_config(config: dict[str, Any]) -> dict[str, Any]:
    return config.get("production_html", {})


def resolved_frontmatter_policy(config: dict[str, Any]) -> dict[str, Any]:
    """Return the single frontmatter policy consumed by production rendering.

    Stage 40 may provide a pre-resolved ``frontmatter_policy``.  Older
    package configs keep their explicit fields, but are normalized here so
    source capture, page typing, ordering, manifest generation, and QA cannot
    make different missing-field decisions.
    """

    production = production_html_config(config)
    frontmatter = frontmatter_config(config)
    raw = config.get("frontmatter_policy")
    if not isinstance(raw, dict):
        raw = production.get("frontmatter_policy") if isinstance(production, dict) else None
    if not isinstance(raw, dict):
        raw = frontmatter.get("resolved_policy") if isinstance(frontmatter, dict) else None
    raw = raw if isinstance(raw, dict) else {}
    raw_page_map = raw.get("page_map")
    page_map = raw_page_map if isinstance(raw_page_map, dict) else config.get("page_map", {})
    raw_toc = raw.get("toc_policy")
    toc = raw_toc if isinstance(raw_toc, dict) else production.get("toc_policy", {})
    raw_credits = raw.get("credits_policy")
    credits = raw_credits if isinstance(raw_credits, dict) else production.get("credits_policy", {})
    return {
        "page_map": page_map if isinstance(page_map, dict) else {},
        "toc_policy": {**DEFAULT_TOC_POLICY, **(toc if isinstance(toc, dict) else {})},
        "credits_policy": credits if isinstance(credits, dict) else {},
        "frontmatter_order": raw.get("frontmatter_order") or raw.get("order") or [],
        "body_start_page": raw.get("body_start_page"),
        "expected_flow": raw.get("expected_flow") or raw.get("frontmatter_order") or raw.get("order") or [],
    }


def frontmatter_config(config: dict[str, Any]) -> dict[str, Any]:
    raw = config.get("frontmatter", {})
    return raw if isinstance(raw, dict) else {}


def page_map_config(config: dict[str, Any]) -> dict[str, dict[str, Any]]:
    raw = resolved_frontmatter_policy(config)["page_map"]
    if not isinstance(raw, dict):
        return {}
    result: dict[str, dict[str, Any]] = {}
    for key, value in raw.items():
        page = str(key).zfill(3)
        if isinstance(value, dict):
            result[page] = value
    return result


def page_type_for(config: dict[str, Any], page: str | None) -> str:
    if not page:
        return "body"
    return str(page_map_config(config).get(str(page).zfill(3), {}).get("type") or "body")


def frontmatter_cover_pages(config: dict[str, Any]) -> set[str]:
    pages = {
        page
        for page, meta in page_map_config(config).items()
        if str(meta.get("type") or "").strip().casefold().replace("_", "-") in {"cover", "title", "landing"}
    }
    cover = frontmatter_config(config).get("cover", {})
    if isinstance(cover, dict) and str(cover.get("page") or "").strip():
        pages.add(str(cover.get("page")).zfill(3))
    return pages


def frontmatter_cover_config(config: dict[str, Any]) -> dict[str, Any]:
    cover = frontmatter_config(config).get("cover", {})
    return cover if isinstance(cover, dict) else {}


def frontmatter_cover_background_underlay(config: dict[str, Any]) -> bool:
    return frontmatter_cover_config(config).get("background_underlay", True) is not False


def frontmatter_report_path(config: dict[str, Any]) -> Path:
    frontmatter = frontmatter_config(config)
    report = str(frontmatter.get("report") or "frontmatter_manifest.json")
    path = Path(report)
    return path.resolve() if path.is_absolute() else qa_root(config) / path


def promote_frontmatter_art_class(config: dict[str, Any], item: dict[str, Any], css_class: str) -> str:
    page = str(item.get("source_page") or item.get("page_id") or item.get("page") or "").zfill(3)
    if page not in frontmatter_cover_pages(config):
        return css_class
    parts = [part for part in css_class.split() if part not in {"art-inline", "art-full-width"}]
    for required in ("art-cover", "art-full-page"):
        if required not in parts:
            parts.append(required)
    return " ".join(parts)


def html_typography_config(config: dict[str, Any]) -> dict[str, str]:
    typography = production_html_config(config).get("typography", {})
    if not isinstance(typography, dict):
        typography = {}
    return {
        "body_font_family": str(
            typography.get("body_font_family")
            or 'Georgia, "Times New Roman", serif'
        ),
        "body_font_size": str(typography.get("body_font_size") or "12pt"),
        "body_line_height": str(typography.get("body_line_height") or "1.45"),
        "print_body_font_size": str(typography.get("print_body_font_size") or "9pt"),
        "print_body_line_height": str(typography.get("print_body_line_height") or "1.28"),
    }


def statblock_section_heading_ids(config: dict[str, Any]) -> list[str]:
    ids: list[str] = []
    policies: list[dict[str, Any]] = []
    html_policy = production_html_config(config).get("statblock_section_policy")
    if isinstance(html_policy, dict):
        policies.append(html_policy)
    for variant in production_pdf_config(config).get("variants", {}).values():
        if isinstance(variant, dict) and isinstance(variant.get("statblock_section_policy"), dict):
            policies.append(variant["statblock_section_policy"])
    for policy in policies:
        for value in policy.get("heading_ids", []):
            heading_id = str(value).strip()
            if heading_id and re.fullmatch(r"[A-Za-z0-9_-]+", heading_id) and heading_id not in ids:
                ids.append(heading_id)
    return ids


def production_html_report_path(config: dict[str, Any]) -> Path:
    value = production_html_config(config).get("report", "production_html_report.json")
    path = Path(str(value).replace("/", "\\"))
    return path.resolve() if path.is_absolute() else qa_root(config) / path


def production_html_source_path(config: dict[str, Any], *, trial: bool = False) -> Path:
    prod = production_html_config(config)
    if trial and prod.get("trial_source_markdown"):
        return root_path(str(prod["trial_source_markdown"]))
    if prod.get("source_markdown"):
        return root_path(str(prod["source_markdown"]))
    outputs = config.get("production_outputs", {})
    if outputs.get("keeper_markdown"):
        return root_path(str(outputs["keeper_markdown"]))
    raise KeyError("production_html.source_markdown")


def production_html_target_path(config: dict[str, Any], *, trial: bool = False) -> Path:
    prod = production_html_config(config)
    if trial and prod.get("trial_output_html"):
        return root_path(str(prod["trial_output_html"]))
    if prod.get("output_html"):
        return root_path(str(prod["output_html"]))
    outputs = config.get("production_outputs", {})
    if outputs.get("html"):
        return root_path(str(outputs["html"]))
    raise KeyError("production_outputs.html")


def production_required_gates(config: dict[str, Any]) -> list[str]:
    return list(production_html_config(config).get("required_gates", ["keeper_full_accepted", "term_gate_passed"]))


def production_entry_findings(config: dict[str, Any], source: Path) -> list[dict[str, Any]]:
    findings: list[dict[str, Any]] = []
    gates = config.get("scenario_gates") or config.get("production_gates") or {}
    for gate in production_required_gates(config):
        if gates.get(gate) is not True:
            findings.append({"code": "required_gate_not_true", "gate": gate, "message": f"Required gate is not true: {gate}"})
    if not source.exists():
        findings.append({"code": "missing_source_markdown", "path": rel(source), "message": "Production HTML source markdown does not exist."})
    prod = production_html_config(config)
    if prod.get("require_landing_decision", False):
        decision = prod.get("landing_decision")
        if not isinstance(decision, dict):
            findings.append({"code": "missing_landing_decision", "message": "Production requires a landing decision before HTML/PDF build."})
        else:
            status = str(decision.get("status") or "")
            if status not in {"accepted", "approved", "accepted_for_review"}:
                findings.append({"code": "landing_decision_not_accepted", "status": status})
            if not decision.get("content"):
                findings.append({"code": "landing_decision_missing_content", "message": "Specify what the production landing contains."})
        landing = prod.get("landing_asset")
        if not isinstance(landing, dict) or not landing.get("src"):
            findings.append({"code": "missing_required_landing_asset", "message": "Production requires a landing asset src."})
        else:
            landing_src = root_path(str(landing["src"]))
            if not landing_src.exists():
                findings.append({"code": "missing_required_landing_asset_file", "path": rel(landing_src)})
    for item in art_integration_config(config).get("preserved_page_art", []):
        role = str(item.get("role") or "source_image")
        if role not in IMAGE_COPY_ROLES:
            continue
        try:
            page = int(item.get("page"))
        except (TypeError, ValueError):
            findings.append({"code": "invalid_preserved_page_art_page", "item": item.get("target_filename")})
            continue
        target_filename = item.get("target_filename") or f"page-{page:03d}-{role}.png"
        try:
            target = target_dir_for_image_role(config, role) / safe_filename(str(target_filename))
        except ValueError as exc:
            findings.append({"code": "invalid_preserved_page_art_role", "role": role, "message": str(exc)})
            continue
        if not target.exists():
            findings.append(
                {
                    "code": "missing_required_preserved_page_art_file",
                    "page": f"{page:03d}",
                    "role": role,
                    "path": rel(target),
                    "message": "Run preserve-page-art --apply before production HTML rebuild.",
                }
            )
    return findings


def filter_production_toc(toc: list[dict[str, Any]], config: dict[str, Any]) -> list[dict[str, Any]]:
    policy = resolved_frontmatter_policy(config)["toc_policy"]
    max_level = int(policy.get("max_heading_level", 2))
    exclude_page_types = {str(item) for item in policy.get("exclude_page_types", ["cover", "credits", "source_toc", "quote_art", "full_art"])}
    exclude_titles = {"содержание", "оглавление"}
    exclude_titles.update(str(item).strip().lower() for item in policy.get("exclude_titles", []))
    callout_policy = callout_policy_config(config)
    if callout_policy.get("toc_exclude", True):
        for rule in callout_rules(callout_policy):
            exclude_titles.update(rule["labels"])
    exclude_heading_ids = {str(item).strip() for item in policy.get("exclude_heading_ids", []) if str(item).strip()}
    exclude_heading_id_prefixes = tuple(
        str(item).strip() for item in policy.get("exclude_heading_id_prefixes", []) if str(item).strip()
    )
    exclude_source_anchor_prefixes = tuple(
        str(item).strip() for item in policy.get("exclude_source_anchor_prefixes", []) if str(item).strip()
    )
    if bool(policy.get("exclude_statblock_headings", True)):
        exclude_heading_ids.update(statblock_section_heading_ids(config))
    level_overrides = heading_level_override_map(config)
    filtered: list[dict[str, Any]] = []
    for item in toc:
        href = str(item.get("href") or "")
        if href in exclude_heading_ids or any(href.startswith(prefix) for prefix in exclude_heading_id_prefixes):
            continue
        source_anchor_ids = [str(value) for value in item.get("source_anchor_ids", [])]
        if any(
            anchor_id.startswith(prefix)
            for anchor_id in source_anchor_ids
            for prefix in exclude_source_anchor_prefixes
        ):
            continue
        level = int(level_overrides.get(href, item.get("level", 99)))
        title = str(item.get("title") or "").strip()
        page = str(item.get("page") or "").zfill(3) if item.get("page") else None
        if level > max_level:
            continue
        if page and page_type_for(config, page) in exclude_page_types:
            continue
        if title.lower() in exclude_titles:
            continue
        filtered.append({**item, "level": level})
    return filtered


def normalized_toc_title(value: str) -> str:
    value = re.sub(r"\s*[.·…]{2,}\s*\d+\s*$", "", value).strip()
    return re.sub(r"\s+", " ", value).casefold()


def source_toc_heading_prefix_match(source_key: str, headings: dict[str, dict[str, Any]]) -> dict[str, Any] | None:
    """Resolve source TOC rows against headings that keep inline metadata."""
    if not source_key:
        return None
    for heading_key, item in headings.items():
        if heading_key == source_key:
            return item
        if heading_key.startswith(source_key + ",") or heading_key.startswith(source_key + " —"):
            return item
    return None


def source_toc_from_markdown(markdown: str, config: dict[str, Any]) -> dict[str, Any] | None:
    """Capture a typed source TOC before its page is replaced by production HTML."""

    policy = resolved_frontmatter_policy(config)["toc_policy"]
    source_pages = {page for page, meta in page_map_config(config).items() if str(meta.get("type") or "") == "source_toc"}
    titles = policy.get("manual_toc_titles", ["Contents", "Table of Contents", "Содержание", "Оглавление"])
    known_titles = {str(value).strip().casefold() for value in titles if str(value).strip()}
    stop_titles = {str(value).strip().casefold() for value in policy.get("source_toc_stop_titles", []) if str(value).strip()}
    declared_entries = policy.get("source_entries")
    if not isinstance(declared_entries, list):
        declared_entries = policy.get("entries")
    sections = re.finditer(
        r'<!--\s*(?:source-page|pdf-page)-(?P<page>\d{3})\s*-->\s*(?P<content>[\s\S]*?)(?=<!--\s*(?:source-page|pdf-page)-\d{3}\s*-->|\Z)',
        markdown,
        re.I,
    )
    for match in sections:
        page = match.group("page")
        if page in source_pages and isinstance(declared_entries, list):
            entries: list[dict[str, Any]] = []
            for index, item in enumerate(declared_entries, start=1):
                if isinstance(item, str):
                    title = item.strip()
                    level = 1
                elif isinstance(item, dict):
                    title = str(item.get("title") or item.get("source_text") or "").strip()
                    try:
                        level = max(1, int(item.get("display_level") or item.get("level") or 1))
                    except (TypeError, ValueError):
                        level = 1
                    href = str(item.get("href") or item.get("matched_heading_id") or item.get("target_id") or "").strip().lstrip("#")
                else:
                    continue
                if title:
                    entry = {"title": title, "level": level, "source_line": index, "source": "accepted_source_entries"}
                    if href:
                        entry["href"] = href
                    entries.append(entry)
            if entries:
                title = str(policy.get("source_title") or "Содержание").strip() or "Содержание"
                return {"page": page, "title": title, "entries": entries, "page_type_evidence": "source_toc_accepted_entries"}
        title: str | None = None
        entries: list[dict[str, Any]] = []
        for line_no, line in enumerate(match.group("content").splitlines(), start=1):
            heading = re.match(r"^\s*#{1,6}\s+(.+?)\s*$", line)
            if heading and title is None:
                title = heading.group(1).strip()
                continue
            if heading or not line.strip():
                continue
            indent = len(line) - len(line.lstrip(" "))
            text = re.sub(r"^(?:[-*+]\s+|\d+[.)]\s+)", "", line.strip())
            clean_title = re.sub(r"\s*(?:[.·…]{2,}|[—–-])\s*\d+\s*$", "", text).strip()
            if any(clean_title.casefold() == stop or clean_title.casefold().startswith(stop + " ") for stop in stop_titles):
                break
            if clean_title:
                level = 1 if policy.get("display_mode") == "flat" else max(1, indent // 2 + 1)
                entries.append({"title": clean_title, "level": level, "source_line": line_no})
        if title is not None:
            if page in source_pages or title.casefold() in known_titles:
                return {"page": page, "title": title, "entries": entries, "page_type_evidence": "source_toc"}
    return None


def source_toc_link_map(config: dict[str, Any]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    policy = resolved_frontmatter_policy(config)["toc_policy"]
    value = policy.get("source_link_map")
    if not value:
        return [], []
    path = root_path(str(value))
    if not path.exists():
        return [], [{"code": "source_toc_link_map_missing", "path": rel(path)}]
    try:
        data = read_json(path)
    except Exception as exc:
        return [], [{"code": "source_toc_link_map_unreadable", "path": rel(path), "message": str(exc)}]
    schema = str(data.get("schema") or "")
    artifact = str(data.get("artifact") or "")
    schema_ok = (
        schema.startswith("viral_toc_link_map")
        or schema.startswith("translator_source_toc_link_map")
        or artifact in {"viral_toc_link_map", "translator_source_toc_link_map"}
    )
    if not schema_ok or not isinstance(data.get("entries"), list):
        return [], [{"code": "source_toc_link_map_invalid_schema", "path": rel(path)}]
    return [item for item in data["entries"] if isinstance(item, dict)], []


def source_toc_with_internal_links(
    source_toc: dict[str, Any], toc: list[dict[str, Any]], config: dict[str, Any] | None = None
) -> dict[str, Any]:
    headings = {normalized_toc_title(str(item["title"])): item for item in toc}
    headings_by_id = {str(item.get("href") or ""): item for item in toc if str(item.get("href") or "")}
    heading_ids = set(headings_by_id)
    mapped_rows, findings = source_toc_link_map(config or {})
    mappings: dict[str, str] = {}
    for row in mapped_rows:
        source_title = str(row.get("source_title") or "").strip()
        target = str(row.get("matched_heading_id") or row.get("href") or "").strip().lstrip("#")
        status = str(row.get("status") or "").strip().casefold()
        key = normalized_toc_title(source_title)
        if status not in {"approved", "accepted", "link"} or not key or not target:
            findings.append({"code": "source_toc_link_map_invalid_entry", "entry": row})
            continue
        if key in mappings:
            findings.append({"code": "source_toc_link_map_duplicate_mapping", "source_title": source_title, "target": target})
            continue
        if target not in heading_ids:
            findings.append({"code": "source_toc_link_map_invalid_target", "source_title": source_title, "target": target})
            continue
        mappings[key] = target
    entries: list[dict[str, Any]] = []
    for entry in source_toc["entries"]:
        key = normalized_toc_title(str(entry["title"]))
        explicit_target = str(entry.get("href") or entry.get("matched_heading_id") or "").strip().lstrip("#")
        if explicit_target and explicit_target not in heading_ids:
            findings.append({"code": "source_toc_entry_invalid_target", "source_title": entry["title"], "target": explicit_target})
            explicit_target = ""
        mapped_target = mappings.get(key)
        exact_target = headings.get(key) or source_toc_heading_prefix_match(key, headings)
        href = explicit_target or mapped_target or (str(exact_target["href"]) if exact_target else None)
        # A preserved source TOC owns its presentation hierarchy.  The target
        # heading supplies only the link destination; borrowing its H1/H2/H3
        # level would silently restyle a flat printed contents page.
        level = entry.get("level")
        try:
            normalized_level = int(level)
        except (TypeError, ValueError):
            normalized_level = int(entry.get("level") or 1)
        entries.append({
            **entry,
            "level": normalized_level,
            "href": href,
            "link_status": "explicit" if explicit_target else "mapped" if mapped_target else "exact" if headings.get(key) else "prefix" if exact_target else "unresolved",
        })
    unresolved = [entry["title"] for entry in entries if entry["href"] is None]
    findings.extend({"code": "source_toc_link_unresolved", "source_title": title} for title in unresolved)
    return {**source_toc, "entries": entries, "link_map_findings": findings}


def build_production_toc(
    toc: list[dict[str, Any]], config: dict[str, Any], *, source_toc: dict[str, Any] | None = None
) -> str:
    source_toc = source_toc_with_internal_links(source_toc, toc, config) if source_toc else None
    toc = filter_production_toc(toc, config)
    toc_cfg = resolved_frontmatter_policy(config)["toc_policy"]
    bg = str(toc_cfg.get("background_image") or "").strip()
    columns_value = toc_cfg.get("columns", 2)
    columns = columns_value if isinstance(columns_value, int) and not isinstance(columns_value, bool) and 1 <= columns_value <= 4 else 2
    root_level_value = toc_cfg.get("root_heading_level", 1)
    root_level = root_level_value if isinstance(root_level_value, int) and not isinstance(root_level_value, bool) and 1 <= root_level_value <= 6 else 1
    styles = [f"--toc-columns: {columns}"]
    for field, css_var in (
        ("font_size", "--toc-font-size"),
        ("line_height", "--toc-line-height"),
        ("item_gap", "--toc-item-gap"),
        ("column_fill", "--toc-column-fill"),
        ("column_gap", "--toc-column-gap"),
    ):
        value = str(toc_cfg.get(field) or "").strip()
        if value:
            styles.append(f"{css_var}: {value}")
    if bg:
        bg_path = root_path(bg)
        html_path = production_html_target_path(config)
        bg_ref = os.path.relpath(bg_path, html_path.parent).replace("\\", "/") if bg_path.exists() else bg.replace("\\", "/")
        styles.append(f"background-image: url({html_lib.escape(bg_ref)})")
    style = f' style="{"; ".join(styles)};"'
    entries = source_toc["entries"] if source_toc else toc
    title = str(source_toc["title"]) if source_toc else "Оглавление"
    origin = "source" if source_toc else "generated"
    mode = str(toc_cfg.get("mode") or "generated").strip().casefold()
    display_layout = "flat" if source_toc and toc_cfg.get("display_mode") == "flat" else "source" if source_toc else "generated"
    if mode == "generated_hierarchical":
        if source_toc:
            raise ValueError("invalid hierarchical TOC: source TOC entries are not supported")
        top_level = toc_cfg.get("top_level_anchor_ids")
        parent_children = toc_cfg.get("parent_children", {})
        require_all = toc_cfg.get("require_all_heading_ids", False)
        if not isinstance(top_level, list) or not top_level:
            raise ValueError("invalid hierarchical TOC: top_level_anchor_ids must be a non-empty list")
        if not isinstance(parent_children, dict):
            raise ValueError("invalid hierarchical TOC: parent_children must be an object")
        if not isinstance(require_all, bool):
            raise ValueError("invalid hierarchical TOC: require_all_heading_ids must be boolean")
        anchor_pattern = re.compile(r"[A-Za-z][A-Za-z0-9_-]*")
        normalized_top = [str(value).strip() for value in top_level]
        if any(not anchor_pattern.fullmatch(value) for value in normalized_top):
            raise ValueError("invalid hierarchical TOC: malformed top-level anchor")
        if len(normalized_top) != len(set(normalized_top)):
            raise ValueError("invalid hierarchical TOC: duplicate top-level anchor")
        available: dict[str, dict[str, Any]] = {}
        for item in entries:
            href = str(item.get("href") or "").strip()
            if not href:
                raise ValueError("invalid hierarchical TOC: unresolved heading anchor")
            if href in available:
                raise ValueError(f"invalid hierarchical TOC: duplicate heading anchor {href}")
            available[href] = item
        assigned = set(normalized_top)
        normalized_children: dict[str, list[str]] = {}
        for raw_parent, raw_children in parent_children.items():
            parent = str(raw_parent).strip()
            if parent not in normalized_top:
                raise ValueError(f"invalid hierarchical TOC: parent anchor is not top-level: {parent}")
            if not isinstance(raw_children, list):
                raise ValueError(f"invalid hierarchical TOC: children for {parent} must be a list")
            children = [str(value).strip() for value in raw_children]
            if any(not anchor_pattern.fullmatch(value) for value in children):
                raise ValueError(f"invalid hierarchical TOC: malformed child anchor under {parent}")
            if len(children) != len(set(children)):
                raise ValueError(f"invalid hierarchical TOC: duplicate child anchor under {parent}")
            for child in children:
                if child in normalized_top:
                    raise ValueError(f"invalid hierarchical TOC: cyclic parent/child anchor {child}")
                if child in assigned:
                    raise ValueError(f"invalid hierarchical TOC: duplicate assigned anchor {child}")
                assigned.add(child)
            normalized_children[parent] = children
        unknown = sorted(assigned - set(available))
        if unknown:
            raise ValueError(f"invalid hierarchical TOC: unknown anchors: {', '.join(unknown)}")
        missing = sorted(set(available) - assigned)
        if require_all and missing:
            raise ValueError(f"invalid hierarchical TOC: missing anchors: {', '.join(missing)}")
        raw_font_size = str(toc_cfg.get("font_size") or "").strip()
        font_match = re.fullmatch(r"([1-9][0-9]*(?:\.[0-9]+)?)pt", raw_font_size, re.I) if raw_font_size else None
        if raw_font_size and font_match is None:
            raise ValueError("invalid hierarchical TOC: font_size must use positive pt units")
        docx_font_attr = f' data-toc-font-size-pt="{font_match.group(1)}"' if font_match else ""
        lines = [f'<nav id="toc" class="toc toc-hierarchical" data-toc-origin="{origin}" data-toc-columns="{columns}" data-toc-numbering="none" data-toc-layout="hierarchical"{docx_font_attr}{style}><div class="toc-frame"><h1>{html_lib.escape(title)}</h1><ul class="toc-root">']
        for parent in normalized_top:
            item = available[parent]
            parent_title = html_lib.escape(str(item["title"]))
            lines.append(f'<li class="toc-group toc-level-1" data-toc-anchor="{html_lib.escape(parent)}"><a href="#{html_lib.escape(parent)}">{parent_title}</a>')
            children = normalized_children.get(parent, [])
            if children:
                lines.append('<ul class="toc-children">')
                for child in children:
                    child_title = html_lib.escape(str(available[child]["title"]))
                    lines.append(f'<li class="toc-level-2"><a href="#{html_lib.escape(child)}">{child_title}</a></li>')
                lines.append('</ul>')
            lines.append('</li>')
        lines.append("</ul></div></nav>")
        return "\n".join(lines)
    if not entries:
        return f'<nav id="toc" class="toc" data-toc-origin="{origin}" data-toc-layout="{display_layout}" data-toc-columns="{columns}"{style}><div class="toc-frame"><h1>{html_lib.escape(title)}</h1><ol></ol></div></nav>'
    lines = [f'<nav id="toc" class="toc" data-toc-origin="{origin}" data-toc-layout="{display_layout}" data-toc-columns="{columns}"{style}><div class="toc-frame"><h1>{html_lib.escape(title)}</h1><ol>']
    for item in entries:
        level = max(1, int(item["level"]) - root_level + 1)
        title = html_lib.escape(str(item["title"]))
        href = item.get("href")
        if href:
            lines.append(f'<li class="toc-level-{level}"><a href="#{html_lib.escape(str(href))}">{title}</a></li>')
        else:
            lines.append(f'<li class="toc-level-{level}" data-unresolved="true">{title}</li>')
    lines.append("</ol></div></nav>")
    return "\n".join(lines)


def wrap_statblock_cards(body: str, config: dict[str, Any]) -> tuple[str, int]:
    configured_ids: list[str] = []
    html_policy = production_html_config(config).get("statblock_section_policy") or {}
    if isinstance(html_policy, dict):
        configured_ids.extend(str(value).strip() for value in html_policy.get("heading_ids", []) if str(value).strip())
    for variant in dict(production_pdf_config(config).get("variants", {})).values():
        if not isinstance(variant, dict):
            continue
        policy = variant.get("statblock_section_policy") or {}
        configured_ids.extend(str(value).strip() for value in policy.get("heading_ids", []) if str(value).strip())
    if not configured_ids:
        return body, 0

    transformed_ids: set[str] = set()

    def move_detached_heading_into_callout(match: re.Match[str]) -> str:
        heading = match.group("heading")
        heading_id = match.group("id")
        blockquote_open = match.group("blockquote_open")
        blockquote_body = match.group("blockquote_body")
        transformed_ids.add(heading_id)
        return f'<div class="statblock-card">{blockquote_open}{heading}\n{blockquote_body}</div>'

    configured_id_pattern = "|".join(re.escape(value) for value in sorted(set(configured_ids), key=len, reverse=True))
    body = re.sub(
        rf'(?P<heading><h[1-6]\b[^>]*\bid="(?P<id>{configured_id_pattern})"[^>]*>[\s\S]*?</h[1-6]>)\s*'
        rf'(?P<blockquote_open><blockquote\b[^>]*\bclass="[^"]*\breview-callout\b[^"]*"[^>]*>)'
        rf'(?P<blockquote_body>[\s\S]*?</blockquote>)',
        move_detached_heading_into_callout,
        body,
        flags=re.I,
    )
    configured_ids = [value for value in configured_ids if value not in transformed_ids]
    if not configured_ids:
        return body, len(transformed_ids)

    heading_re = re.compile(r'<h([1-6])\b[^>]*\bid="([^"]+)"[^>]*>', re.I)
    lines = body.splitlines()
    out: list[str] = []
    in_section = False
    in_card = False
    card_level: int | None = None
    wrapped = 0
    for line in lines:
        heading = heading_re.search(line)
        if heading:
            level = int(heading.group(1))
            heading_id = heading.group(2)
            if heading_id in configured_ids:
                if in_card:
                    out.append("</div>")
                    in_card = False
                in_section = True
                card_level = level
                out.append('<div class="statblock-card">')
                out.append(line)
                in_card = True
                wrapped += 1
                continue
            if in_section and card_level is not None and level <= card_level:
                if in_card:
                    out.append("</div>")
                    in_card = False
                in_section = False
                card_level = None
        if in_section and line.startswith("</section>"):
            if in_card:
                out.append("</div>")
                in_card = False
            in_section = False
            card_level = None
        out.append(line)
    if in_card:
        out.append("</div>")
    return "\n".join(out), wrapped


def wrap_page_type_statblock_callouts(body: str) -> tuple[str, int]:
    wrapped = 0

    def repl_section(match: re.Match[str]) -> str:
        nonlocal wrapped
        section = match.group(0)

        def repl_callout(callout_match: re.Match[str]) -> str:
            nonlocal wrapped
            callout = callout_match.group(0)
            if "statblock-card" in callout:
                return callout
            if not re.search(r'class="[^"]*\bstatblock-dune-', callout, re.I):
                return callout
            wrapped += 1
            return f'<div class="statblock-card">{callout}</div>'

        return re.sub(
            r'<blockquote\b[^>]*\bclass="[^"]*\breview-callout\b[^"]*"[^>]*>[\s\S]*?</blockquote>',
            repl_callout,
            section,
            flags=re.I,
        )

    body = re.sub(
        r'<section\b(?=[^>]*\bclass="[^"]*\bpage-type-statblock-card\b[^"]*")[^>]*>[\s\S]*?</section>',
        repl_section,
        body,
        flags=re.I,
    )
    return body, wrapped


def annotate_page_type_sections(body: str, config: dict[str, Any]) -> tuple[str, list[dict[str, Any]]]:
    annotations: list[dict[str, Any]] = []
    page_map = page_map_config(config)
    for page, meta in page_map.items():
        page_type = str(meta.get("type") or "").strip()
        page_type_class = page_type.replace("_", "-")
        background_image = str(meta.get("background_image") or "").strip()
        if not page_type and not background_image:
            continue
        pattern = re.compile(
            rf'(?P<open><section\b(?=[^>]*\bid=["\']page-{re.escape(page)}["\'])(?=[^>]*\bdata-page=["\']{re.escape(page)}["\'])[^>]*>)',
            re.I,
        )
        def repl(match: re.Match[str]) -> str:
            open_tag = match.group("open")
            class_match = re.search(r'class=["\']([^"\']*)["\']', open_tag, re.I)
            classes = class_match.group(1).split() if class_match else []
            if page_type_class:
                extra = f"page-type-{page_type_class}"
                if extra not in classes:
                    classes.append(extra)
            if class_match:
                open_tag = open_tag[: class_match.start(1)] + " ".join(classes) + open_tag[class_match.end(1) :]
            else:
                open_tag = open_tag[:-1] + f' class="{" ".join(classes)}">'
            if background_image:
                bg_path = root_path(background_image)
                html_path = production_html_target_path(config)
                bg_ref = os.path.relpath(bg_path, html_path.parent).replace("\\", "/") if bg_path.exists() else background_image.replace("\\", "/")
                if 'style="' in open_tag:
                    open_tag = re.sub(r'style="([^"]*)"', rf'style="\1; background-image: url({html_lib.escape(bg_ref)});"', open_tag, count=1)
                else:
                    open_tag = open_tag[:-1] + f' style="background-image: url({html_lib.escape(bg_ref)});">'
            return open_tag
        body, count = pattern.subn(repl, body, count=1)
        if count:
            annotations.append({"page": page, "type": page_type or None, "background_image": background_image or None, "annotated": True})
    return body, annotations


def remove_source_toc_sections(
    body: str, config: dict[str, Any], *, source_toc: dict[str, Any] | None = None
) -> tuple[str, list[dict[str, Any]]]:
    policy = production_html_config(config).get("toc_policy", {})
    if not isinstance(policy, dict):
        policy = {}
    if not bool(policy.get("replace_source_toc_pages", True)):
        return body, []
    removed: list[dict[str, Any]] = []
    source_pages = [page for page, meta in page_map_config(config).items() if str(meta.get("type") or "") == "source_toc"]
    if source_toc and str(source_toc.get("page") or "").zfill(3) not in source_pages:
        source_pages.append(str(source_toc["page"]).zfill(3))
    for page in source_pages:
        pattern = re.compile(
            rf'\n?<!--\s*pdf-page-{re.escape(page)}\s*-->\s*<section\b[^>]*\bid=["\']page-{re.escape(page)}["\'][\s\S]*?</section>\s*',
            re.I,
        )
        body, count = pattern.subn("\n", body, count=1)
        removed.append(
            {
                "page": page,
                "page_type": "source_toc",
                "source_page_evidence": page,
                "count": count,
                "mode": "preserved_as_production_toc",
            }
        )
    return body, removed


def remove_manual_toc_sections(body: str, config: dict[str, Any]) -> tuple[str, list[dict[str, Any]]]:
    policy = production_html_config(config).get("toc_policy", {})
    if not isinstance(policy, dict):
        policy = {}
    if not bool(policy.get("replace_manual_toc_sections", True)):
        return body, []

    removed: list[dict[str, Any]] = []
    titles = policy.get("manual_toc_titles", ["Содержание", "Оглавление"])
    normalized_titles = {str(title).strip().lower() for title in titles if str(title).strip()}
    if not normalized_titles:
        return body, []

    def repl(match: re.Match[str]) -> str:
        title_text = re.sub(r"<[^>]+>", "", match.group("title")).strip().lower()
        if title_text not in normalized_titles:
            return match.group(0)
        removed.append({"title": title_text, "mode": "replaced_by_generated_toc"})
        return "\n"

    body = re.sub(
        r'\n?(?P<heading><h[1-6]\b[^>]*>\s*(?P<title>Содержание|Оглавление)\s*</h[1-6]>)\s*'
        r'(?P<list><(?:ul|ol)\b[^>]*>[\s\S]*?</(?:ul|ol)>)\s*',
        repl,
        body,
        flags=re.I,
    )
    if not bool(policy.get("remove_manual_toc_mixed_blocks", False)):
        return body, removed

    title_pattern = "|".join(re.escape(title) for title in sorted(normalized_titles, key=len, reverse=True))

    def mixed_repl(match: re.Match[str]) -> str:
        section = match.group("section")
        title = re.search(rf'<h[1-6]\b[^>]*>\s*({title_pattern})\s*</h[1-6]>', section, re.I)
        if not title:
            return section
        page_match = re.search(r'\bid=["\']page-(\d{3})["\']', section, re.I)
        removed.append(
            {
                "title": title.group(1).strip().lower(),
                "page": page_match.group(1) if page_match else None,
                "mode": "mixed_blocks_replaced_by_generated_toc",
            }
        )
        return ""

    body = re.sub(
        r'(?P<section><section\b[^>]*>[^<]*(?:<[^>]+>[^<]*)*?[\s\S]*?</section>)',
        mixed_repl,
        body,
        flags=re.I,
    )
    return body, removed


def callout_policy_config(config: dict[str, Any]) -> dict[str, Any]:
    policy = production_html_config(config).get("callout_policy", config.get("callout_policy", {}))
    return policy if isinstance(policy, dict) else {}


def callout_rules(policy: dict[str, Any]) -> list[dict[str, Any]]:
    raw_rules = policy.get("rules")
    if not isinstance(raw_rules, list):
        raw_rules = [{"labels": policy.get("labels", []), "aliases": policy.get("aliases", [])}]
    rules: list[dict[str, Any]] = []
    for raw in raw_rules:
        if not isinstance(raw, dict):
            continue
        labels = raw.get("labels", raw.get("label", []))
        if isinstance(labels, str):
            labels = [labels]
        aliases = raw.get("aliases", [])
        if isinstance(aliases, str):
            aliases = [aliases]
        values = {str(value).strip().casefold() for value in [*labels, *aliases] if str(value).strip()}
        if values:
            rules.append(
                {
                    "labels": values,
                    "boundary": str(raw.get("boundary") or policy.get("boundary") or "next_heading_same_or_higher"),
                    "mode": str(raw.get("mode") or policy.get("mode") or "convert"),
                    "style_class": str(raw.get("style_class") or policy.get("style_class") or "").strip(),
                }
            )
    return rules


def transform_markdown_callouts(markdown: str, config: dict[str, Any]) -> tuple[str, dict[str, Any]]:
    """Convert explicitly configured note headings without widening their boundaries."""

    policy = callout_policy_config(config)
    rules = callout_rules(policy)
    result: dict[str, Any] = {"configured_rules": len(rules), "converted": [], "findings": []}
    if not rules:
        return markdown, result
    lines = markdown.splitlines()
    out: list[str] = []
    heading_re = re.compile(r"^(#{1,6})\s+(.+?)\s*$")
    page_re = re.compile(r"^<!--\s*(?:source-page|pdf-page)-\d{3}\b[^>]*-->$", re.I)
    index = 0
    while index < len(lines):
        heading = heading_re.match(lines[index].strip())
        if not heading:
            out.append(lines[index])
            index += 1
            continue
        title = heading.group(2).strip()
        level = len(heading.group(1))
        rule = next((item for item in rules if title.casefold() in item["labels"]), None)
        if rule is None:
            out.append(lines[index])
            index += 1
            continue
        boundary = rule["boundary"]
        if boundary not in {"next_heading", "next_heading_same_or_higher", "next_page"}:
            result["findings"].append({"code": "unsupported_callout_boundary", "title": title, "line": index + 1, "boundary": boundary})
            out.append(lines[index])
            index += 1
            continue
        end = index + 1
        while end < len(lines):
            candidate = lines[end].strip()
            next_heading = heading_re.match(candidate)
            is_boundary = (
                page_re.match(candidate)
                or (boundary == "next_heading" and next_heading is not None)
                or (boundary == "next_heading_same_or_higher" and next_heading is not None and len(next_heading.group(1)) <= level)
            )
            if is_boundary:
                break
            end += 1
        record = {"title": title, "line": index + 1, "boundary": boundary, "end_line": end}
        if rule["mode"] == "validate":
            record["validated"] = True
            result["converted"].append(record)
            out.extend(lines[index:end])
        else:
            class_directive = re.sub(r"[^A-Za-z0-9_-]", "", rule["style_class"])
            callout_lines = [f"**{title}**", *lines[index + 1 : end]]
            if class_directive:
                callout_lines.insert(0, f"<!-- callout-class: {class_directive} -->")
            out.extend(">" if not value else f"> {value}" for value in callout_lines)
            record["converted"] = True
            result["converted"].append(record)
        index = end
    return "\n".join(out) + ("\n" if markdown.endswith("\n") else ""), result


def ordered_list_continuity_report(markdown: str, config: dict[str, Any]) -> dict[str, Any]:
    """Describe list starts; rendering preserves them and never joins separate blocks."""

    blocks: list[dict[str, int]] = []
    lines = markdown.splitlines()
    index = 0
    while index < len(lines):
        match = re.match(r"^(\d+)\.\s+", lines[index].strip())
        if not match:
            index += 1
            continue
        start_line = index + 1
        start = int(match.group(1))
        end = start
        count = 0
        while index < len(lines):
            item = re.match(r"^(\d+)\.\s+", lines[index].strip())
            if not item:
                break
            end = int(item.group(1))
            count += 1
            index += 1
        blocks.append({"line": start_line, "start": start, "end": end, "items": count})
    policy = production_html_config(config).get("ordered_list_continuity_policy", config.get("ordered_list_continuity_policy", {}))
    if not isinstance(policy, dict):
        policy = {}
    declared = policy.get("known_continuations", [])
    findings: list[dict[str, Any]] = []
    if not isinstance(declared, list):
        findings.append({"code": "invalid_list_continuity_policy"})
        declared = []
    for item in declared:
        if not isinstance(item, dict):
            findings.append({"code": "invalid_declared_list_continuation"})
            continue
        expected_start = item.get("next_start", item.get("start"))
        if not isinstance(expected_start, int) or not any(block["start"] == expected_start for block in blocks):
            findings.append({"code": "declared_list_continuation_not_found", "continuation": item})
    return {"blocks": blocks, "declared_continuations": len(declared), "findings": findings}


def normalize_appendix_handout_headings(markdown: str, config: dict[str, Any]) -> tuple[str, dict[str, Any]]:
    """Promote standalone Appendix handout labels into normalized Markdown headings."""
    policy = production_html_config(config).get("handout_heading_policy", {})
    if not isinstance(policy, dict) or not policy.get("enabled", False):
        return markdown, {"enabled": False, "transformed": [], "findings": []}

    appendix_heading = str(policy.get("appendix_heading") or "").strip()
    target_level = max(2, min(6, int(policy.get("heading_level", 2))))
    if not appendix_heading:
        return markdown, {"enabled": True, "transformed": [], "findings": [{"code": "handout_heading_appendix_missing"}]}

    lines = markdown.splitlines()
    appendix_index = next(
        (index for index, line in enumerate(lines) if re.fullmatch(r"#{1,6}\s+" + re.escape(appendix_heading) + r"\s*", line.strip())),
        None,
    )
    if appendix_index is None:
        return markdown, {"enabled": True, "transformed": [], "findings": [{"code": "handout_heading_appendix_not_found", "heading": appendix_heading}]}

    marker_re = re.compile(r"^(?:#{1,6}\s+)?(?:Handout\s*#|Раздаточ(?:ный|ные)\s+материал(?:ы)?\s*№\s*)(\d+[A-Za-z]?)\s*$", re.I)
    heading_re = re.compile(r"^(#{1,6})\s+(.+?)\s*$")
    handout_token_re = re.compile(r"Handout\s*#(\d+[A-Za-z]?)", re.I)
    overrides = {
        str(item.get("number") or "").lower(): item
        for item in policy.get("title_overrides", [])
        if isinstance(item, dict) and str(item.get("number") or "").strip()
    }
    current_page = ""
    page_headings: list[tuple[int, int]] = []
    target_numbers: dict[int, list[str]] = {}
    marker_lines: set[int] = set()
    findings: list[dict[str, Any]] = []

    def append_number(target_index: int, number: str) -> None:
        values = target_numbers.setdefault(target_index, [])
        if number not in values:
            values.append(number)

    for index, line in enumerate(lines):
        page_match = SOURCE_PAGE_RE.match(line)
        if page_match:
            current_page = page_match.group("page")
            page_headings = []
            continue
        if index < appendix_index:
            continue
        heading_match = heading_re.match(line)
        marker_match = marker_re.match(line.strip())
        if heading_match and not marker_match:
            existing_numbers = handout_token_re.findall(heading_match.group(2))
            if existing_numbers:
                target_numbers[index] = list(dict.fromkeys(existing_numbers))
            page_headings.append((index, len(heading_match.group(1))))
            continue
        if not marker_match:
            continue
        number = marker_match.group(1)
        override = overrides.get(number.lower())
        preferred_headings = [heading_index for heading_index, level in page_headings if level <= 2]
        target_index = preferred_headings[-1] if preferred_headings else (page_headings[-1][0] if page_headings else None)
        created_heading = False
        if override and override.get("source_page") and str(override["source_page"]).zfill(3) != current_page:
            override = None
        if override and override.get("force_title"):
            title = str(override.get("title") or "").strip()
            if title:
                lines[index] = f"{'#' * target_level} {title}"
                target_index = index
                created_heading = True
        elif target_index is None and override:
            title = str(override.get("title") or "").strip()
            if title:
                lines[index] = f"{'#' * target_level} {title}"
                target_index = index
                created_heading = True
        if target_index is None:
            findings.append({"code": "handout_heading_target_missing", "number": number, "line": index + 1, "source_page": current_page})
            continue
        append_number(target_index, number)
        if not created_heading:
            marker_lines.add(index)

    transformed: list[dict[str, Any]] = []
    for index, numbers in sorted(target_numbers.items()):
        heading_match = heading_re.match(lines[index])
        if not heading_match:
            findings.append({"code": "handout_heading_target_not_heading", "line": index + 1, "numbers": numbers})
            continue
        title = re.sub(
            r"\s*(?:—|:)\s*Handout\s*#\d+[A-Za-z]?(?:\s*/\s*Handout\s*#\d+[A-Za-z]?)*\s*$",
            "",
            heading_match.group(2),
            flags=re.I,
        )
        title = handout_token_re.sub("", title)
        title = re.sub(r"\s*(?:—|:|/)\s*$", "", title).strip()
        if not title:
            findings.append({"code": "handout_heading_title_missing", "line": index + 1, "numbers": numbers})
            continue
        suffix = f" — Handout #{numbers[0]}" if len(numbers) == 1 else ": " + " / ".join(f"Handout #{number}" for number in numbers)
        lines[index] = f"{'#' * target_level} {title}{suffix}"
        transformed.append({"line": index + 1, "title": title, "numbers": numbers})

    for index in marker_lines:
        lines[index] = ""
    normalized = "\n".join(lines) + ("\n" if markdown.endswith("\n") else "")
    required_base_numbers = [str(value) for value in policy.get("required_base_numbers", [])]
    required_range = policy.get("required_base_range")
    if isinstance(required_range, list) and len(required_range) == 2:
        try:
            first, last = int(required_range[0]), int(required_range[1])
            required_base_numbers.extend(str(value) for value in range(first, last + 1))
        except (TypeError, ValueError):
            findings.append({"code": "handout_heading_required_range_invalid", "value": required_range})
    actual_base_numbers = {
        base_match.group(0)
        for item in transformed
        for number in item["numbers"]
        if (base_match := re.match(r"\d+", number))
    }
    missing = [number for number in required_base_numbers if number not in actual_base_numbers]
    if missing:
        findings.append({"code": "handout_heading_required_numbers_missing", "numbers": missing})
    return normalized, {
        "enabled": True,
        "appendix_heading": appendix_heading,
        "heading_level": target_level,
        "transformed": transformed,
        "marker_lines_removed": len(marker_lines),
        "findings": findings,
    }


KEEPER_ART_BLOCK_RE = re.compile(
    r'^(?P<prefix><div class="keeper-art-block" data-placement-id="(?P<placement_id>[A-Za-z0-9_-]+)" '
    r'data-anchor-id=")(?P<anchor_id>[A-Za-z0-9_-]+)(?P<suffix>"[^>]*>\s*'
    r'<img id="[A-Za-z0-9_-]+-image" src="(?P<src>(?:\.\./)?Images(?:_v\d+)?/[^"<>]+|(?:\.\./)?Images/Runtime_Assets/[^"<>]+)" '
    r'alt="[^"]*">\s*</div>)\s*$'
)


def reader_art_manifest_entries(config: dict[str, Any]) -> dict[str, dict[str, Any]]:
    """Read canonical reader-facing art entries keyed by placement id."""
    art = production_art_layout_config(config)
    value = str(art.get("source_anchor_manifest") or art.get("art_manifest") or "").strip()
    if not value:
        return {}
    path = Path(value.replace("/", "\\"))
    manifest_path = path.resolve() if path.is_absolute() else qa_root(config) / path
    if not manifest_path.exists():
        return {}
    manifest = read_json(manifest_path)
    return {
        str(item.get("placement_id") or "").strip(): item
        for item in manifest.get("placements", [])
        if isinstance(item, dict) and str(item.get("placement_id") or "").strip()
    }


def reader_art_layout_from_manifest(config: dict[str, Any]) -> tuple[dict[str, str], dict[str, str]]:
    """Read optional reader-facing layout and anchor data from the canonical art manifest."""
    classes: dict[str, str] = {}
    anchors: dict[str, str] = {}
    for placement_id, item in reader_art_manifest_entries(config).items():
        css_class = promote_frontmatter_art_class(config, item, str(item.get("css_class") or "").strip())
        if css_class:
            classes[placement_id] = css_class
        anchor_id = str(item.get("heading_id") or "").strip()
        if anchor_id:
            anchors[placement_id] = anchor_id
    return classes, anchors


def relocate_reader_art_blocks(markdown: str, config: dict[str, Any]) -> tuple[str, dict[str, Any]]:
    """Move generated art blocks to canonical semantic headings without rewriting source Markdown."""
    entries = reader_art_manifest_entries(config)
    _, target_anchors = reader_art_layout_from_manifest(config)
    preserve_existing = bool(production_art_layout_config(config).get("preserve_existing_reader_art_blocks", False))
    if not entries:
        return markdown, {"enabled": False, "relocated": [], "findings": []}

    lines = markdown.splitlines()
    used_slugs: dict[str, int] = {}
    heading_lines: dict[str, int] = {}
    page_marker_lines: dict[str, int] = {}
    for index, line in enumerate(lines):
        page_match = re.match(r"^<!--\s*source-page-(\d{3})\s*-->$", line.strip())
        if page_match:
            page_marker_lines[f"page-{page_match.group(1)}"] = index
        match = re.match(r"^(#{1,6})\s+(.+?)\s*$", line.strip())
        if match:
            heading_lines[unique_slug(match.group(2), used_slugs)] = index

    inserts: dict[int, list[str]] = {}
    removed_indexes: set[int] = set()
    relocated: list[dict[str, Any]] = []
    findings: list[dict[str, Any]] = []
    for index, line in enumerate(lines):
        match = KEEPER_ART_BLOCK_RE.match(line.strip())
        if not match:
            continue
        placement_id = match.group("placement_id")
        target_anchor = target_anchors.get(placement_id)
        if not target_anchor:
            continue
        if preserve_existing:
            relocated.append(
                {
                    "placement_id": placement_id,
                    "from_anchor": match.group("anchor_id"),
                    "to_anchor": target_anchor,
                    "moved": False,
                    "preserved_existing": True,
                }
            )
            continue
        target_index = heading_lines.get(target_anchor)
        if target_index is None:
            entry = entries.get(placement_id, {})
            if entry.get("require_reader_anchor") or entry.get("emit_reader_art_block"):
                findings.append({"code": "reader_art_anchor_not_found", "placement_id": placement_id, "heading_id": target_anchor})
            continue
        updated = f'{match.group("prefix")}{target_anchor}{match.group("suffix")}'
        removed_indexes.add(index)
        inserts.setdefault(target_index, []).append(updated)
        relocated.append(
            {
                "placement_id": placement_id,
                "from_anchor": match.group("anchor_id"),
                "to_anchor": target_anchor,
                "moved": index != target_index + 1 or match.group("anchor_id") != target_anchor,
            }
        )

    existing_ids = {
        match.group("placement_id")
        for line in lines
        if (match := KEEPER_ART_BLOCK_RE.match(line.strip()))
    }
    for placement_id, item in entries.items():
        if placement_id in existing_ids or not item.get("emit_reader_art_block"):
            continue
        target_anchor = target_anchors.get(placement_id)
        target_index = heading_lines.get(target_anchor or "")
        if target_index is None:
            target_index = page_marker_lines.get(target_anchor or "")
        runtime_src = str(item.get("runtime_src") or "").strip()
        runtime_filename = str(item.get("runtime_filename") or item.get("asset_id") or "").strip()
        if not runtime_src and runtime_filename:
            runtime_src = f"Images/Runtime_Assets/{runtime_filename}"
        if target_index is None or not runtime_src:
            findings.append(
                {
                    "code": "reader_art_addition_invalid",
                    "placement_id": placement_id,
                    "heading_id": target_anchor,
                    "runtime_filename": runtime_filename or None,
                    "runtime_src": runtime_src or None,
                }
            )
            continue
        inserts.setdefault(target_index, []).append(
            f'<div class="keeper-art-block" data-placement-id="{placement_id}" '
            f'data-anchor-id="{target_anchor}"> <img id="{placement_id}-image" '
            f'src="{runtime_src}" alt="{placement_id}"> </div>'
        )
        relocated.append(
            {
                "placement_id": placement_id,
                "from_anchor": None,
                "to_anchor": target_anchor,
                "moved": True,
                "added": True,
            }
        )

    if not removed_indexes and not inserts:
        return markdown, {"enabled": True, "relocated": relocated, "findings": findings}
    out: list[str] = []
    for index, line in enumerate(lines):
        if index not in removed_indexes:
            out.append(line)
        if index in inserts:
            out.extend(inserts[index])
    return "\n".join(out) + ("\n" if markdown.endswith("\n") else ""), {
        "enabled": True,
        "relocated": relocated,
        "findings": findings,
    }


def suppress_reader_metadata_markdown(markdown: str, config: dict[str, Any]) -> tuple[str, list[dict[str, Any]]]:
    """Remove package-declared service prose from reader-facing derivative artifacts only."""
    rules = production_html_config(config).get("reader_metadata_suppressions", [])
    if not isinstance(rules, list):
        return markdown, []
    current_page: str | None = None
    lines = markdown.splitlines()
    out: list[str] = []
    suppressed: list[dict[str, Any]] = []
    index = 0
    while index < len(lines):
        marker = re.match(r"<!--\s*source-page-(\d{3})\s*-->", lines[index].strip())
        if marker:
            current_page = marker.group(1)
        matched_rule = next(
            (
                rule for rule in rules
                if isinstance(rule, dict)
                and str(rule.get("source_page") or "").zfill(3) == str(current_page or "").zfill(3)
                and str(rule.get("starts_with") or "").strip()
                and lines[index].strip().startswith(str(rule["starts_with"]).strip())
            ),
            None,
        )
        if matched_rule is None:
            out.append(lines[index])
            index += 1
            continue
        start = index
        while index < len(lines) and lines[index].strip():
            index += 1
        suppressed.append(
            {
                "source_page": current_page,
                "starts_with": matched_rule["starts_with"],
                "lines": index - start,
            }
        )
    return "\n".join(out) + ("\n" if markdown.endswith("\n") else ""), suppressed


def normalized_markdown_output_path(config: dict[str, Any], *, trial: bool = False) -> Path | None:
    """Return the optional reader-facing Markdown emitted by production post-processing."""
    if trial:
        return None
    policy = production_html_config(config).get("handout_heading_policy", {})
    if not isinstance(policy, dict):
        return None
    value = str(policy.get("output_markdown") or "").strip()
    return root_path(value) if value else None


def remove_source_cover_sections(body: str, config: dict[str, Any]) -> tuple[str, list[dict[str, Any]]]:
    landing_asset = production_html_config(config).get("landing_asset", {})
    if not isinstance(landing_asset, dict) or not bool(landing_asset.get("suppress_source_cover_page", False)):
        return body, []
    removed: list[dict[str, Any]] = []
    for page, meta in page_map_config(config).items():
        if str(meta.get("type") or "") != "cover":
            continue
        pattern = re.compile(
            rf'\n?<!--\s*pdf-page-{re.escape(page)}\s*-->\s*<section\b[^>]*\bid=["\']page-{re.escape(page)}["\'][\s\S]*?</section>\s*',
            re.I,
        )
        body, count = pattern.subn("\n", body, count=1)
        removed.append({"page": page, "count": count, "mode": "replaced_by_landing_asset"})
    return body, removed


def remove_markdown_pages_by_type(text: str, config: dict[str, Any], page_types: set[str]) -> str:
    for page, meta in page_map_config(config).items():
        if str(meta.get("type") or "") not in page_types:
            continue
        pattern = re.compile(
            rf'\n?<!--\s*(?:source-page|pdf-page)-{re.escape(page)}\s*-->\s*[\s\S]*?(?=\n<!--\s*(?:source-page|pdf-page)-\d{{3}}\s*-->|$)',
            re.I,
        )
        text = pattern.sub("\n", text, count=1)
    return text


def heading_level_override_map(config: dict[str, Any]) -> dict[str, int]:
    overrides = production_html_config(config).get("heading_level_overrides", [])
    result: dict[str, int] = {}
    if not isinstance(overrides, list):
        return result
    for item in overrides:
        if not isinstance(item, dict):
            continue
        heading_id = str(item.get("id") or "").strip()
        if not heading_id:
            continue
        try:
            level = int(item.get("level"))
        except (TypeError, ValueError):
            continue
        result[heading_id] = max(1, min(6, level))
    return result


def apply_heading_level_overrides(body: str, config: dict[str, Any]) -> tuple[str, list[dict[str, Any]]]:
    overrides = heading_level_override_map(config)
    changed: list[dict[str, Any]] = []
    for heading_id, new_level in overrides.items():
        pattern = re.compile(
            rf'<h(?P<old>[1-6])\b(?P<attrs>[^>]*\bid=["\']{re.escape(heading_id)}["\'][^>]*)>(?P<inner>[\s\S]*?)</h(?P=old)>',
            re.I,
        )
        def repl(match: re.Match[str]) -> str:
            old_level = int(match.group("old"))
            if old_level != new_level:
                changed.append({"id": heading_id, "old_level": old_level, "new_level": new_level})
            return f'<h{new_level}{match.group("attrs")}>{match.group("inner")}</h{new_level}>'
        body = pattern.sub(repl, body, count=1)
    return body, changed


def table_rows_from_html(table_html: str) -> list[list[str]]:
    rows: list[list[str]] = []
    for row_html in re.findall(r"<tr>([\s\S]*?)</tr>", table_html, re.I):
        cells = re.findall(r"<t[hd][^>]*>([\s\S]*?)</t[hd]>", row_html, re.I)
        rows.append([cell.strip() for cell in cells])
    return rows


DEFAULT_CREDITS_LAYOUT_PROFILES = {
    "two_columns_10pt": {"columns": 2, "font_size": "10pt", "line_height": "1.15", "column_gap": "9mm"},
    "three_columns_8pt": {"columns": 3, "font_size": "8pt", "line_height": "1.1", "column_gap": "6mm"},
    "five_columns_5pt": {"columns": 5, "font_size": "5pt", "line_height": "1.04", "column_gap": "4mm"},
}


def credits_layout_profile(config: dict[str, Any]) -> tuple[str, dict[str, Any]]:
    """Resolve a bounded credits profile; compact layouts require explicit opt-in."""
    policy = production_html_config(config).get("credits_policy", {})
    policy = policy if isinstance(policy, dict) else {}
    profiles = dict(DEFAULT_CREDITS_LAYOUT_PROFILES)
    custom_profiles = policy.get("layout_profiles", {})
    if isinstance(custom_profiles, dict):
        for name, value in custom_profiles.items():
            if isinstance(value, dict):
                profiles[str(name)] = {**profiles.get(str(name), {}), **value}
    requested_name = str(policy.get("layout_profile") or "two_columns_10pt")
    name = requested_name if requested_name in profiles else "two_columns_10pt"
    profile = profiles[name]
    columns = profile.get("columns", 2)
    if not isinstance(columns, int) or isinstance(columns, bool) or not 1 <= columns <= 5:
        columns = 2
    font_size = str(profile.get("font_size") or "10pt")
    line_height = str(profile.get("line_height") or "1.15")
    column_gap = str(profile.get("column_gap") or "9mm")
    if not re.fullmatch(r"\d+(?:\.\d+)?(?:pt|px|em|rem|mm)", font_size):
        font_size = "10pt"
    if not re.fullmatch(r"\d+(?:\.\d+)?", line_height):
        line_height = "1.15"
    if not re.fullmatch(r"\d+(?:\.\d+)?(?:pt|px|em|rem|mm)", column_gap):
        column_gap = "9mm"
    return name, {"columns": columns, "font_size": font_size, "line_height": line_height, "column_gap": column_gap}


def transform_credits_sections(body: str, config: dict[str, Any]) -> tuple[str, list[dict[str, Any]]]:
    transformed: list[dict[str, Any]] = []
    credits_policy = resolved_frontmatter_policy(config)["credits_policy"]
    keep_preceding_heading = bool(credits_policy.get("keep_preceding_heading", False))
    force_page_boundary = credits_policy.get("force_page_boundary", True) is not False
    profile_name, profile = credits_layout_profile(config)
    heading_ids = [
        str(value).strip()
        for value in credits_policy.get("heading_ids", [])
        if str(value).strip()
    ]
    end_anchor_by_heading = credits_policy.get("end_anchor_by_heading", {})
    end_anchor_by_heading = end_anchor_by_heading if isinstance(end_anchor_by_heading, dict) else {}
    for heading_id in heading_ids:
        end_anchor = str(end_anchor_by_heading.get(heading_id) or "").strip()
        boundary = r"(?=<h[1-6]\b|\Z)"
        if end_anchor:
            boundary = (
                rf'(?=<a\b[^>]*\bid=["\']{re.escape(end_anchor)}["\'][^>]*></a>|'
                r'<h[1-6]\b|\Z)'
            )
        pattern = re.compile(
            rf'(?P<heading><h(?P<level>[1-6])\b[^>]*\bid=["\']{re.escape(heading_id)}["\'][^>]*>[\s\S]*?</h(?P=level)>)'
            rf'(?P<body>[\s\S]*?){boundary}',
            re.I,
        )
        match = pattern.search(body)
        if not match:
            transformed.append({"heading_id": heading_id, "count": 0, "reason": "missing_heading"})
            continue
        section_body = match.group("body")
        columns_class = "credits-columns"
        layout_mode = str(credits_policy.get("layout_mode") or "columns").strip()
        if layout_mode == "grid":
            paragraphs = re.findall(r'<p\b[^>]*>([\s\S]*?)</p>', section_body, re.I)
            remainder = re.sub(r'<p\b[^>]*>[\s\S]*?</p>', "", section_body, flags=re.I).strip()
            pair_count = int(credits_policy.get("role_name_pairs", 0))
            if remainder or pair_count < 0 or pair_count * 2 > len(paragraphs):
                transformed.append({"heading_id": heading_id, "count": 0, "reason": "credits_grid_contract_mismatch"})
                continue
            items = []
            for index in range(pair_count):
                role, names = paragraphs[index * 2 : index * 2 + 2]
                items.append(
                    '<div class="credit-item"><div class="credit-role">'
                    + role
                    + '</div><div class="credit-names">'
                    + names
                    + '</div></div>'
                )
            items.extend(
                '<div class="credit-item credit-note"><p>' + paragraph + '</p></div>'
                for paragraph in paragraphs[pair_count * 2 :]
            )
            section_body = "".join(items)
            columns_class += " credits-grid"
        style = (
            f'--credits-columns: {profile["columns"]}; '
            f'--credits-font-size: {profile["font_size"]}; '
            f'--credits-line-height: {profile["line_height"]}; '
            f'--credits-column-gap: {profile["column_gap"]};'
        )
        replacement = (
            '<section class="production-page page-type-credits credits-by-heading">'
            '<div class="credits-frame">'
            + match.group("heading")
            + f'<div class="{columns_class}" data-credits-profile="{html_lib.escape(profile_name)}" style="{style}">'
            + section_body
            + '</div></div></section><div class="credits-page-boundary" aria-hidden="true"></div>\n'
        )
        body = body[: match.start()] + replacement + body[match.end() :]
        transformed.append({
            "heading_id": heading_id,
            "count": 1,
            "mode": "heading_section_to_credit_columns",
            "profile": profile_name,
            "profile_values": profile,
            "layout_mode": layout_mode,
            "end_anchor": end_anchor or None,
        })
    for page, meta in page_map_config(config).items():
        if str(meta.get("type") or "") != "credits":
            continue
        pattern = re.compile(
            rf'(?P<section><section\b[^>]*\bid=["\']page-{re.escape(page)}["\'][\s\S]*?</section>)',
            re.I,
        )
        match = pattern.search(body)
        if not match:
            transformed.append({"page": page, "count": 0, "reason": "missing_section"})
            continue
        suppressed_heading = False
        if not keep_preceding_heading:
            prefix = body[: match.start("section")]
            heading_pattern = re.compile(
                rf'(?P<heading><h1\b[^>]*>[\s\S]*?</h1>\s*)(?P<marker><!--\s*(?:source-page|pdf-page)-{re.escape(page)}\s*-->\s*)$',
                re.I,
            )
            updated_prefix, suppressed_count = heading_pattern.subn(r"\g<marker>", prefix)
            if suppressed_count:
                body = updated_prefix + body[match.start("section") :]
                match = pattern.search(body)
                if not match:
                    transformed.append({"page": page, "count": 0, "reason": "section_missing_after_heading_suppression"})
                    continue
                suppressed_heading = True
        section = match.group("section")
        tables = re.findall(r'<div class="table-wrap[^"]*"><table[^>]*>([\s\S]*?)</table></div>', section, re.I)
        if not tables:
            page_modes = credits_policy.get("page_modes", {})
            page_mode = page_modes.get(page) if isinstance(page_modes, dict) else None
            prose_pages = {str(value).zfill(3) for value in credits_policy.get("prose_pages", [])}
            declared_pages = {str(value).zfill(3) for value in credits_policy.get("source_pages", [])}
            content_mode = str(page_mode or credits_policy.get("content_mode") or credits_policy.get("mode") or "").strip().casefold()
            if content_mode not in {"prose", "preserve_prose"} or (declared_pages and page not in declared_pages):
                if page in prose_pages:
                    pass
                else:
                    transformed.append({"page": page, "count": 0, "reason": "no_tables", "suppressed_preceding_heading": suppressed_heading})
                    continue
            open_match = re.match(r'(?P<open><section\b[^>]*>)(?P<inner>[\s\S]*)(?P<close></section>)', section, re.I)
            if not open_match:
                transformed.append({"page": page, "count": 0, "reason": "invalid_section", "suppressed_preceding_heading": suppressed_heading})
                continue
            inner = open_match.group("inner")
            if 'class="credits-frame"' not in inner:
                section = open_match.group("open") + '<div class="credits-frame"><div class="credits-prose">' + inner + '</div></div>' + open_match.group("close")
            boundary = '<div class="credits-page-boundary" aria-hidden="true"></div>' if force_page_boundary else ""
            body = body[: match.start("section")] + section + boundary + body[match.end("section") :]
            transformed.append({
                "page": page,
                "count": 1,
                "mode": "prose_credits_preserved",
                "suppressed_preceding_heading": suppressed_heading,
                "page_boundary": force_page_boundary,
            })
            continue
        def table_repl(table_match: re.Match[str]) -> str:
            rows = table_rows_from_html(table_match.group(1))
            items = []
            for row in rows[1:]:
                if len(row) < 2:
                    continue
                role = row[0]
                names = row[1]
                items.append(f'<div class="credit-item"><div class="credit-role">{role}</div><div class="credit-names">{names}</div></div>')
            style = (
                f'--credits-columns: {profile["columns"]}; '
                f'--credits-font-size: {profile["font_size"]}; '
                f'--credits-line-height: {profile["line_height"]}; '
                f'--credits-column-gap: {profile["column_gap"]};'
            )
            return f'<div class="credits-columns" data-credits-profile="{html_lib.escape(profile_name)}" style="{style}">' + "\n".join(items) + "</div>"
        new_section, count = re.subn(r'<div class="table-wrap[^"]*"><table[^>]*>([\s\S]*?)</table></div>', table_repl, section, flags=re.I)
        if count:
            open_match = re.match(r'(?P<open><section\b[^>]*>)(?P<inner>[\s\S]*)(?P<close></section>)', new_section, re.I)
            if open_match and 'class="credits-frame"' not in open_match.group("inner"):
                new_section = open_match.group("open") + '<div class="credits-frame">' + open_match.group("inner") + '</div>' + open_match.group("close")
            boundary = '<div class="credits-page-boundary" aria-hidden="true"></div>' if force_page_boundary else ""
            body = body[: match.start("section")] + new_section + boundary + body[match.end("section") :]
        transformed.append({
            "page": page,
            "count": count,
            "mode": "table_to_credit_columns",
            "profile": profile_name,
            "profile_values": profile,
            "suppressed_preceding_heading": suppressed_heading,
            "page_boundary": force_page_boundary,
        })
    return body, transformed


def merge_table_continuations(body: str, config: dict[str, Any]) -> tuple[str, list[dict[str, Any]]]:
    """Join explicitly declared source-page table continuations and renumber a numeric first column."""
    policies = production_html_config(config).get("table_continuations", [])
    if not isinstance(policies, list):
        return body, []
    reports: list[dict[str, Any]] = []
    for policy in policies:
        if not isinstance(policy, dict):
            continue
        heading_id = str(policy.get("heading_id") or "").strip()
        continuation_page = str(policy.get("continuation_page") or "").strip().zfill(3)
        if not heading_id or not continuation_page.isdigit():
            reports.append({"status": "invalid_policy", "heading_id": heading_id})
            continue
        first = re.search(
            rf'(?P<head><h[1-6]\b[^>]*\bid=["\']{re.escape(heading_id)}["\'][^>]*>[\s\S]*?</h[1-6]>[\s\S]*?)'
            r'(?P<table><div class="table-wrap[^>]*"><table[^>]*>(?P<rows>[\s\S]*?)</table></div>)',
            body,
            re.I,
        )
        continuation_section = re.search(
            rf'(?P<section><!--\s*(?:source-page|pdf-page)-{re.escape(continuation_page)}\s*-->\s*<section\b[^>]*\bid=["\']page-{re.escape(continuation_page)}["\'][^>]*>)(?P<body>[\s\S]*?)</section>',
            body,
            re.I,
        )
        if not first or not continuation_section:
            reports.append({"status": "missing_table", "heading_id": heading_id, "continuation_page": continuation_page})
            continue
        continuation_table = re.search(r'<div class="table-wrap[^>]*"><table[^>]*>(?P<rows>[\s\S]*?)</table></div>', continuation_section.group("body"), re.I)
        if continuation_table:
            continuation_rows = re.findall(r'<tr\b[^>]*>([\s\S]*?)</tr>', continuation_table.group("rows"), re.I)
            data_rows = [row for row in continuation_rows if not re.search(r'<th\b', row, re.I)]
            continuation_replacement = ""
        else:
            source_segment = re.search(
                rf'<!--\s*(?:source-page|pdf-page)-{re.escape(continuation_page)}\s*-->[\s\S]*?(?=<h[1-6]\b|</section>)',
                body,
                re.I,
            )
            pipe_rows = re.findall(
                r'<p>\|\s*(\d+)\s*\|\s*([^|]+?)\s*\|\s*(.*?)\s*\|</p>',
                source_segment.group(0) if source_segment else "",
                re.I | re.S,
            )
            data_rows = [f'<td>{number}</td><td>{title}</td><td>{text}</td>' for number, title, text in pipe_rows]
            continuation_replacement = ""
        if not data_rows:
            reports.append({"status": "missing_continuation_rows", "heading_id": heading_id, "continuation_page": continuation_page})
            continue
        merged_rows = first.group("rows") + "".join(f"<tr>{row}</tr>" for row in data_rows)
        if bool(policy.get("renumber_first_column", False)):
            counter = 0
            def renumber(match: re.Match[str]) -> str:
                nonlocal counter
                cells = re.findall(r'<td\b[^>]*>[\s\S]*?</td>', match.group(1), re.I)
                if not cells:
                    return match.group(0)
                counter += 1
                replacement = re.sub(r'(<td\b[^>]*>)[\s\S]*?(</td>)', rf'\g<1>{counter}\g<2>', cells[0], count=1, flags=re.I)
                return '<tr>' + match.group(1).replace(cells[0], replacement, 1) + '</tr>'
            merged_rows = re.sub(r'<tr\b[^>]*>([\s\S]*?)</tr>', renumber, merged_rows, flags=re.I)
        merged_table = re.sub(r'(?s)(<table[^>]*>).*?(</table>)', rf'\g<1>{merged_rows}\g<2>', first.group("table"), count=1)
        body = body[: first.start("table")] + merged_table + body[first.end("table") :]
        reports.append({"status": "merged", "heading_id": heading_id, "continuation_page": continuation_page, "rows_added": len(data_rows), "renumbered": bool(policy.get("renumber_first_column", False))})
        body = re.sub(
            rf'(?s)(<!--\s*(?:source-page|pdf-page)-{re.escape(continuation_page)}\s*-->\s*<section\b[^>]*\bid=["\']page-{re.escape(continuation_page)}["\'][^>]*>.*?)'
            r'(?:<div class="table-wrap[^>]*"><table[^>]*>[\s\S]*?</table></div>|(?:\s*<p>\|\s*\d+\s*\|[\s\S]*?\|</p>)+)',
            r'\1' + continuation_replacement,
            body,
            count=1,
            flags=re.I,
        )
    return body, reports


def transform_quote_art_sections(body: str, config: dict[str, Any]) -> tuple[str, list[dict[str, Any]]]:
    transformed: list[dict[str, Any]] = []
    for page, meta in page_map_config(config).items():
        if str(meta.get("type") or "") != "quote_art":
            continue
        pattern = re.compile(
            rf'(?P<section><section\b[^>]*\bid=["\']page-{re.escape(page)}["\'][\s\S]*?</section>)',
            re.I,
        )
        match = pattern.search(body)
        if not match:
            transformed.append({"page": page, "count": 0, "reason": "missing_section"})
            continue
        section = match.group("section")
        figure = re.search(r'<figure\b[^>]*>(?P<figure>[\s\S]*?<img\b[^>]*\bsrc="(?P<src>[^"]+)"[^>]*>[\s\S]*?)</figure>', section, re.I)
        if not figure:
            transformed.append({"page": page, "count": 0, "reason": "missing_art"})
            continue
        src = figure.group("src")
        section_no_figure = section[: figure.start()] + section[figure.end() :]
        open_tag = re.match(r"(<section\b[^>]*>)", section_no_figure, re.I)
        if not open_tag:
            transformed.append({"page": page, "count": 0, "reason": "section_open_tag_not_found"})
            continue
        open_html = open_tag.group(1)
        if 'style="' in open_html:
            open_html = re.sub(r'style="([^"]*)"', rf'style="\1; background-image: url({html_lib.escape(src)});"', open_html, count=1)
        else:
            open_html = open_html[:-1] + f' style="background-image: url({html_lib.escape(src)});">'
        new_section = open_html + section_no_figure[len(open_tag.group(1)) :]
        body = body[: match.start("section")] + new_section + body[match.end("section") :]
        transformed.append({"page": page, "count": 1, "mode": "art_as_section_background"})
    return body, transformed


def build_frontmatter_manifest(config: dict[str, Any], html_text: str, production_source_toc: dict[str, Any] | None) -> dict[str, Any]:
    """Record the reader-facing frontmatter contract used by publishing."""

    page_map = page_map_config(config)
    cover_cfg = frontmatter_cover_config(config)
    cover_pages = sorted(frontmatter_cover_pages(config))
    cover_page = cover_pages[0] if cover_pages else None
    cover_asset = None
    if cover_page:
        for placement_id, item in reader_art_manifest_entries(config).items():
            if str(item.get("source_page") or "").zfill(3) != cover_page:
                continue
            cover_asset = {
                "placement_id": placement_id,
                "asset_id": item.get("asset_id"),
                "runtime_filename": item.get("runtime_filename"),
                "runtime_src": item.get("runtime_src"),
                "source_page": cover_page,
                "role": item.get("production_role") or item.get("semantic_role"),
                "css_class": promote_frontmatter_art_class(config, item, str(item.get("css_class") or "")),
                "mode": "full_page_cover",
                "required": True,
            }
            break
    toc_policy = resolved_frontmatter_policy(config)["toc_policy"]
    credits_pages = [
        page
        for page, meta in page_map.items()
        if str(meta.get("type") or "").strip().casefold().replace("_", "-") == "credits"
    ]
    body_pages = [
        page
        for page, meta in page_map.items()
        if str(meta.get("type") or "").strip().casefold().replace("_", "-") not in {"cover", "title", "landing", "source-toc", "credits"}
    ]
    flow = []
    for match in re.finditer(
        r'<section\b[^>]*\bclass=["\'][^"\']*production-landing[^"\']*["\'][\s\S]*?</section>'
        r'|<nav\b[^>]*\bid=["\']toc["\'][\s\S]*?</nav>'
        r'|<section\b[^>]*\bdata-page=["\'](?P<page>\d{3})["\'][\s\S]*?</section>',
        html_text,
        re.I,
    ):
        chunk = match.group(0)
        if "production-landing" in chunk:
            flow.append("landing")
        elif re.search(r'<nav\b[^>]*\bid=["\']toc["\']', chunk, re.I):
            origin_match = re.search(r'data-toc-origin=["\']([^"\']+)["\']', chunk, re.I)
            flow.append(f"toc:{origin_match.group(1).strip().casefold() if origin_match else 'unknown'}")
        elif match.groupdict().get("page"):
            flow.append(f"page-{match.group('page')}")
        if len(flow) >= 8:
            break
    policy = resolved_frontmatter_policy(config)
    declared_body_start = policy.get("body_start_page")
    return {
        "schema": "translator_frontmatter_manifest.v1",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "cover": {
            "page": cover_page,
            "pages": cover_pages,
            "asset": cover_asset,
            "mode": cover_cfg.get("mode", "source_cover_full_page"),
            "fit": cover_cfg.get("fit", "contain"),
            "background_underlay": frontmatter_cover_background_underlay(config),
        },
        "toc": {
            "mode": toc_policy["mode"],
            "source_page": str(toc_policy.get("source_page")).zfill(3) if toc_policy.get("source_page") else None,
            "title": production_source_toc.get("title") if production_source_toc else toc_policy.get("generated_fallback_title", "Оглавление"),
            "origin": "source" if production_source_toc else "generated",
            "entries": len(production_source_toc.get("entries", [])) if production_source_toc else None,
            "source_link_map": toc_policy.get("source_link_map"),
        },
        "credits": {"pages": credits_pages},
        "body": {"starts_at": str(declared_body_start).zfill(3) if declared_body_start else (body_pages[0] if body_pages else None)},
        "flow": flow,
    }


def production_landing_html(config: dict[str, Any], html_path: Path) -> str:
    landing = production_html_config(config).get("landing_asset")
    if not isinstance(landing, dict) or not landing.get("src"):
        return ""
    source = root_path(str(landing["src"]))
    if not source.exists():
        return ""
    rel_src = os.path.relpath(source, html_path.parent).replace("\\", "/")
    title_en = str(landing.get("title_en") or config.get("title_en") or "").strip()
    title_ru = str(landing.get("title_ru") or config.get("title_ru") or "").strip()
    title_html = ""
    if landing.get("show_titles", True) and (title_en or title_ru):
        title_lines = []
        if title_en:
            title_lines.append(f'<div class="production-landing-title-en">{html_lib.escape(title_en)}</div>')
        if title_ru:
            title_lines.append(f'<div class="production-landing-title-ru">{html_lib.escape(title_ru)}</div>')
        title_html = '<div class="production-landing-title">' + "".join(title_lines) + "</div>\n"
    return (
        '<section class="production-landing" id="production-landing" data-production-role="landing" '
        f'style="background-image: url({html_lib.escape(rel_src)});">\n'
        f"{title_html}"
        "</section>\n"
    )


def build_production_html_document(config: dict[str, Any], body: str, toc_html: str) -> str:
    title = str(config.get("scenario_title_ru") or config.get("scenario_title_en") or config.get("project_key") or "Production HTML")
    print_columns = max(1, min(2, int(production_html_config(config).get("print_columns", 1))))
    normal_single_column_flow = (
        print_columns == 1
        and bool(production_html_config(config).get("avoid_single_column_fragmentation_context", False))
    )
    body_classes = f"print-columns-{print_columns}" + (
        " normal-single-column-flow" if normal_single_column_flow else ""
    )
    print_column_count = "auto" if normal_single_column_flow else str(print_columns)
    print_column_gap = "8mm" if print_columns > 1 else "0"
    landing_html = production_landing_html(config, production_html_target_path(config))
    typography = html_typography_config(config)
    cover_underlay_enabled = frontmatter_cover_background_underlay(config)
    cover_background_css = "#2b170d center/cover no-repeat" if cover_underlay_enabled else "transparent none"
    cover_text_color_css = "#f7ead2" if cover_underlay_enabled else "#6b2d12"
    cover_text_shadow_css = "0 2px 5px rgba(0,0,0,.85)" if cover_underlay_enabled else "none"
    cover_heading_border_css = "rgba(247,234,210,.6)" if cover_underlay_enabled else "rgba(107,45,18,.35)"
    statblock_section_font_css = ""
    full_page_heading_keep_css = ""
    body_art_table_flow_css = ""
    long_callout_page_flow_css = ""
    section_start_page_css = ""
    if production_html_config(config).get("allow_statblock_flow_beside_body_art", False):
        body_art_table_flow_css = """
  body.print-columns-1 .statblock-card {
    break-inside: auto !important;
    page-break-inside: auto !important;
  }
  body.print-columns-1 .statblock-card .table-wrap {
    break-inside: avoid !important;
    page-break-inside: avoid !important;
    overflow: auto !important;
  }
"""
    if production_html_config(config).get("keep_full_page_art_with_heading", False):
        full_page_heading_keep_css = """
  body.print-columns-1 .full-page-art-card {
    display: block;
    box-sizing: border-box;
    break-before: page;
    page-break-before: always;
    break-after: page;
    page-break-after: always;
    break-inside: avoid;
    page-break-inside: avoid;
  }
  body.print-columns-1 .full-page-art-card figure.art-full-page,
  body.print-columns-1 .full-page-art-card figure.art-handout-page,
  body.print-columns-1 .full-page-art-card figure.art-pregen-fullpage {
    break-before: auto;
    page-break-before: auto;
    break-after: auto;
    page-break-after: auto;
  }
  body.print-columns-1 .full-page-art-card + p,
  body.print-columns-1 .full-page-art-card + h1,
  body.print-columns-1 .full-page-art-card + h2,
  body.print-columns-1 .full-page-art-card + h3,
  body.print-columns-1 .full-page-art-card + h4,
  body.print-columns-1 .full-page-art-card + a + h1,
  body.print-columns-1 .full-page-art-card + a + h2,
  body.print-columns-1 .full-page-art-card + a + h3,
  body.print-columns-1 .full-page-art-card + a + h4,
  body.print-columns-1 .full-page-art-card + .full-page-art-card {
    break-before: page !important;
    page-break-before: always !important;
  }
  body.print-columns-1 h1:has(+ figure.art-full-page),
  body.print-columns-1 h2:has(+ figure.art-full-page),
  body.print-columns-1 h3:has(+ figure.art-full-page),
  body.print-columns-1 h4:has(+ figure.art-full-page),
  body.print-columns-1 h1:has(+ p + figure.art-full-page),
  body.print-columns-1 h2:has(+ p + figure.art-full-page),
  body.print-columns-1 h3:has(+ p + figure.art-full-page),
  body.print-columns-1 h4:has(+ p + figure.art-full-page) {
    break-before: page;
    page-break-before: always;
    break-after: avoid;
    page-break-after: avoid;
  }
  body.print-columns-1 h1:has(+ p + figure.art-full-page) + p,
  body.print-columns-1 h2:has(+ p + figure.art-full-page) + p,
  body.print-columns-1 h3:has(+ p + figure.art-full-page) + p,
  body.print-columns-1 h4:has(+ p + figure.art-full-page) + p {
    break-after: avoid;
    page-break-after: avoid;
  }
  body.print-columns-1 h1 + figure.art-full-page img,
  body.print-columns-1 h2 + figure.art-full-page img,
  body.print-columns-1 h3 + figure.art-full-page img,
  body.print-columns-1 h4 + figure.art-full-page img,
  body.print-columns-1 p + figure.art-full-page img {
    max-height: 242mm;
  }
  body.print-columns-1 .handout-art-card {
    min-height: 0 !important;
  }
  body.print-columns-1 .handout-art-card figure.art-handout-page img {
    max-height: 205mm;
  }
  body.print-columns-1 .pregen-art-card {
    min-height: 266mm;
  }
  body.print-columns-1 .pregen-art-card figure.art-pregen-fullpage img {
    max-height: 252mm;
  }
"""
    if production_html_config(config).get("allow_long_callout_page_breaks", False):
        long_callout_page_flow_css = """
  body.print-columns-1 blockquote.review-callout:not(.callout-keep-together):not([data-break-policy="keep_together"]) {
    break-inside: auto !important;
    page-break-inside: auto !important;
    box-decoration-break: clone;
    -webkit-box-decoration-break: clone;
  }
"""
    raw_section_start_ids = production_html_config(config).get("page_break_before_anchor_ids", [])
    if isinstance(raw_section_start_ids, list):
        section_start_ids = [
            str(value).strip()
            for value in raw_section_start_ids
            if re.fullmatch(r"[A-Za-z][A-Za-z0-9_-]*", str(value).strip())
        ]
        if section_start_ids:
            first_card_selectors = ",\n  ".join(
                f"body.print-columns-1 a#{anchor_id} + h2 + .full-page-art-card"
                for anchor_id in section_start_ids
            )
            first_card_selectors += ",\n  body.print-columns-1 .production-section-start + .full-page-art-card"
            section_start_page_css = f"""
  body.print-columns-1 .production-section-start {{
    display: block;
    margin: 0;
    padding: 0;
    break-before: page !important;
    page-break-before: always !important;
    break-after: avoid;
    page-break-after: avoid;
  }}
  body.print-columns-1 blockquote.review-callout:has(+ .production-section-start) {{
    margin-top: .75em;
    margin-bottom: 0;
    padding: .55em .8em;
    font-size: 9.25pt;
    line-height: 1.16;
    columns: 2;
    column-gap: 6mm;
    break-after: page !important;
    page-break-after: always !important;
  }}
  body.print-columns-1 blockquote.review-callout:has(+ .production-section-start) > p {{
    break-inside: avoid-column;
    page-break-inside: avoid;
  }}
  body.print-columns-1 blockquote.review-callout:has(+ .production-section-start) > p:nth-child(2n+3):nth-child(-n+19) {{
    break-after: avoid-column !important;
    page-break-after: avoid !important;
  }}
  body.normal-single-column-flow .full-page-art-card + p,
  body.normal-single-column-flow .full-page-art-card + h1,
  body.normal-single-column-flow .full-page-art-card + h2,
  body.normal-single-column-flow .full-page-art-card + h3,
  body.normal-single-column-flow .full-page-art-card + h4,
  body.normal-single-column-flow .full-page-art-card + a + h1,
  body.normal-single-column-flow .full-page-art-card + a + h2,
  body.normal-single-column-flow .full-page-art-card + a + h3,
  body.normal-single-column-flow .full-page-art-card + a + h4,
  body.normal-single-column-flow .full-page-art-card + .full-page-art-card {{
    break-before: auto !important;
    page-break-before: auto !important;
  }}
  body.normal-single-column-flow .full-page-art-card {{
    break-before: auto !important;
    page-break-before: auto !important;
    break-after: auto !important;
    page-break-after: auto !important;
    min-height: 266mm;
  }}
  {first_card_selectors} {{
    break-before: auto !important;
    page-break-before: auto !important;
    min-height: 0 !important;
  }}
  body.normal-single-column-flow .full-page-art-card h1,
  body.normal-single-column-flow .full-page-art-card h2,
  body.normal-single-column-flow .full-page-art-card h3,
  body.normal-single-column-flow .full-page-art-card h4,
  body.normal-single-column-flow .full-page-art-card + .production-section-start {{
    break-before: auto !important;
    page-break-before: auto !important;
  }}
  body.normal-single-column-flow .full-page-art-card h1 + figure.art-full-page img,
  body.normal-single-column-flow .full-page-art-card h2 + figure.art-full-page img,
  body.normal-single-column-flow .full-page-art-card h3 + figure.art-full-page img,
  body.normal-single-column-flow .full-page-art-card h4 + figure.art-full-page img {{
    max-height: 230mm;
  }}
  body.normal-single-column-flow .section-heading-bound-card > h2,
  body.normal-single-column-flow .section-heading-bound-card > h2 + a + h3 {{
    display: inline-block;
    margin: 0 0 1mm;
    padding: 0;
    border-bottom: 0;
    line-height: 1.05;
  }}
  body.print-columns-1 .section-heading-bound-card {{
    break-before: page !important;
    page-break-before: always !important;
  }}
  body.normal-single-column-flow .section-heading-bound-card > h2::after {{
    content: " — ";
    white-space: pre;
  }}
  body.normal-single-column-flow .section-heading-bound-card > figure.art-pregen-fullpage {{
    margin-top: 1mm;
  }}
"""
    statblock_heading_ids = statblock_section_heading_ids(config)
    if statblock_heading_ids:
        selectors = ",\n  ".join(f"#{heading_id}" for heading_id in statblock_heading_ids)
        statblock_section_font_css = f"""
  {selectors} {{
    font-size: 12pt;
  }}
"""
    css = """
@page { size: A4; margin: 14mm 13mm 16mm; }
body { margin: 0; background: #eee2ca; color: #25160f; font: __BODY_FONT_SIZE__/__BODY_LINE_HEIGHT__ __BODY_FONT_FAMILY__; font-variant-numeric: lining-nums; }
main { max-width: 940px; margin: 0 auto; padding: 32px 30px 64px; background: #fffaf0; }
h1, h2, h3, h4, h5, h6 { color: #6b2d12; line-height: 1.16; margin: 1.1em 0 .35em; break-after: avoid; page-break-after: avoid; }
h1, h2, h3, h4 { clear: both; }
h1 { font-size: 2rem; border-bottom: 2px solid #9a4b24; padding-bottom: .15em; text-transform: uppercase; font-weight: 700; }
h2 { font-size: 1.42rem; border-bottom: 1px solid #c7a675; padding-bottom: .12em; text-transform: none; font-weight: 700; }
h3, h4, h5, h6 { font-size: 1.16rem; text-transform: none; font-weight: 400; }
a { color: #7a3214; }
.toc { padding: 34px 40px 62px; margin: 0 0 30px; background: #f2e2c2 center/cover no-repeat; border: 0; break-after: page; page-break-after: always; box-sizing: border-box; min-height: 236mm; overflow: hidden; }
.toc-frame { background: rgba(255,250,240,.86); border: 3px solid rgba(96,75,49,.72); padding: 22px 30px; min-height: 210mm; box-sizing: border-box; box-shadow: 0 0 0 1px rgba(255,250,240,.7) inset; }
.toc h1 { margin: 0; padding: 0 0 5px; text-align: center; font-size: 1.45rem; letter-spacing: .08em; border-bottom: 1px solid rgba(96,75,49,.72); }
.toc ol, .toc ul.toc-root { columns: var(--toc-columns, 2); column-fill: var(--toc-column-fill, auto); column-gap: var(--toc-column-gap, normal); margin-top: 20px; padding-left: 24px; padding-top: 0; max-height: 190mm; overflow: hidden; font-size: var(--toc-font-size, inherit); line-height: var(--toc-line-height, inherit); }
.toc li { break-inside: avoid; margin: 0 0 var(--toc-item-gap, 6px); color: #4c2413; }
.toc a { text-decoration: none; }
.toc .toc-level-1 { margin-left: 0; font-weight: 700; text-transform: uppercase; letter-spacing: .01em; }
.toc[data-toc-layout="flat"] .toc-level-1 { font-weight: 500; text-transform: none; letter-spacing: normal; }
.toc .toc-level-2 { margin-left: .85em; font-weight: 500; text-transform: none; }
.toc .toc-level-3,
.toc .toc-level-4,
.toc .toc-level-5,
.toc .toc-level-6 { margin-left: 1.7em; font-size: .92em; font-weight: 400; text-transform: none; }
.toc-hierarchical ul { list-style: none; }
.toc-hierarchical ul.toc-root { padding-left: 0; }
.toc-hierarchical .toc-group { break-inside: avoid; page-break-inside: avoid; font-weight: 400; text-transform: none; }
.toc-hierarchical .toc-group > a { display: block; font-weight: 700; text-transform: none; }
.toc-hierarchical .toc-children { margin: .28em 0 0 1.2em; padding: 0; font-weight: 400; }
.toc-hierarchical .toc-children > li { margin: 0 0 var(--toc-item-gap, 6px); font-weight: 400; text-transform: none; }
.hard-page-break { display: block; height: 0; margin: 0; padding: 0; break-after: page; page-break-after: always; }
.production-landing {
  margin: 0 0 28px;
  padding: 0 0 18px;
  border-bottom: 1px solid #d7c59e;
  position: relative;
  background-repeat: no-repeat;
  background-position: center 56%;
  background-size: contain;
  min-height: 72vh;
  display: block;
}
.production-landing-title { position: absolute; top: 25%; left: 0; transform: translateY(-50%); width: 100%; margin: 0; text-align: center; color: #5c2610; text-shadow: 0 1px 0 #fffaf0, 0 -1px 0 #fffaf0, 1px 0 0 #fffaf0, -1px 0 0 #fffaf0; }
.production-landing-title-en { font-size: 2.1rem; line-height: 1.05; font-weight: 700; text-transform: uppercase; }
.production-landing-title-ru { margin-top: 5px; font-size: 1.38rem; line-height: 1.12; font-weight: 700; }
.production-landing-figure { display: none; margin: 0; text-align: center; }
.production-landing .art-cover { break-before: auto; break-after: auto; }
.production-landing-figure img { width: 100%; max-height: 250mm; object-fit: contain; }
.production-page { padding: 18px 0 34px; border-bottom: 1px solid #d7c59e; }
.production-page.page-type-cover { min-height: 236mm; background: __COVER_BACKGROUND__; padding: 0; box-sizing: border-box; break-after: page; page-break-after: always; position: relative; overflow: hidden; }
.production-page.page-type-cover h1,
.production-page.page-type-cover h2,
.production-page.page-type-cover p { position: relative; z-index: 1; margin-left: auto; margin-right: auto; max-width: 72%; text-align: center; color: __COVER_TEXT_COLOR__; font-family: Georgia, "Times New Roman", serif; text-shadow: __COVER_TEXT_SHADOW__; border-bottom-color: __COVER_HEADING_BORDER__; }
.production-page.page-type-cover h1:first-of-type { padding-top: 28mm; margin-top: 0; }
.production-page.page-type-cover h1 { font-size: 2.35rem; letter-spacing: .06em; }
.production-page.page-type-cover h2 { font-size: 1.35rem; }
.production-page.page-type-cover p { font-size: 1rem; font-weight: 700; letter-spacing: .04em; }
.production-page.page-type-cover figure,
.production-page.page-type-cover figure.keeper-art-block,
.production-page.page-type-cover figure.art-cover,
.production-page.page-type-cover figure.art-full-page { display: block; width: 100%; max-width: 100%; margin: 0 auto; text-align: center; break-before: auto; break-after: auto; }
.production-page.page-type-cover figure img { width: 100%; max-width: 100%; max-height: 250mm; object-fit: contain; }
.production-page.page-type-credits { padding: 34px 40px 62px; margin: 0; background: #f2e2c2 center/cover no-repeat; border: 0; box-sizing: border-box; min-height: 236mm; overflow: hidden; break-after: page; page-break-after: always; }
.production-page.page-type-credits .credits-frame { background: rgba(255,250,240,.86); border: 3px solid rgba(96,75,49,.72); padding: 22px 30px; min-height: 210mm; box-sizing: border-box; box-shadow: 0 0 0 1px rgba(255,250,240,.7) inset; }
.credits-page-boundary { display: block; height: 0; margin: 0; padding: 0; column-span: all; break-before: page; page-break-before: always; }
.production-page.page-type-credits h1 { text-align: center; border-bottom: 0; letter-spacing: .08em; margin: 0 0 .9em; }
.production-page.page-type-credits h2 { font-size: 1.08rem; margin: .65em 0 .35em; break-after: avoid; page-break-after: avoid; }
.production-page.page-type-credits .credits-columns { columns: var(--credits-columns, 2); column-gap: var(--credits-column-gap, 9mm); font-size: var(--credits-font-size, 10pt); line-height: var(--credits-line-height, 1.15); overflow-wrap: anywhere; }
.production-page.page-type-credits .credits-grid { columns: auto; display: grid; grid-template-columns: repeat(var(--credits-columns, 2), minmax(0, 1fr)); align-content: start; gap: var(--credits-column-gap, 9mm); height: auto; overflow: visible; }
.production-page.page-type-credits .credit-item { break-inside: avoid; margin: 0 0 .48em; text-align: center; }
.production-page.page-type-credits .credit-role { font-weight: 700; text-transform: uppercase; letter-spacing: .04em; border-bottom: 1px solid #8c775b; padding-bottom: 1px; margin-bottom: 1px; }
.production-page.page-type-credits .credit-names { font-weight: 600; }
.production-page.page-type-quote-art { min-height: 236mm; background: #2b170d center/cover no-repeat; color: #fff8e7; padding: 70mm 28mm 0; box-sizing: border-box; break-after: page; page-break-after: always; text-align: center; }
.production-page.page-type-quote-art h1,
.production-page.page-type-quote-art h2 { color: #fff8e7; border-color: rgba(255,248,231,.72); text-shadow: 0 2px 5px rgba(0,0,0,.85); }
.production-page.page-type-quote-art h1 { margin: 0 auto .7em; max-width: 72%; letter-spacing: .14em; }
.production-page.page-type-quote-art p { max-width: 62%; color: #fff8e7; background: transparent; padding: 0; margin: .25em auto; font-style: italic; text-shadow: 0 2px 5px rgba(0,0,0,.9); }
.page-marker { display: none; }
blockquote.review-callout { margin: 1.2em 0; padding: .8em 1em; border-left: 5px solid #8f3d19; background: #f0dfbd; }
.statblock-card { break-inside: avoid; page-break-inside: avoid; margin: .75em 0 1em; line-height: 1.12; }
.statblock-card h2, .statblock-card h3 { margin-top: 0; }
.statblock-card p { margin: .2em 0; }
.statblock-card p:last-child { margin-bottom: 0; }
.statblock-card table.has-index-column th:first-child,
.statblock-card table.has-index-column td:first-child { width: 2.2em; min-width: 2.2em; max-width: 2.2em; text-align: center; white-space: nowrap; }
.table-wrap { overflow-x: auto; margin: 1em 0; break-inside: avoid; page-break-inside: avoid; }
table { width: 100%; max-width: 100%; border-collapse: collapse; font-size: .9em; }
th, td { border: 1px solid #c7a675; padding: 6px 8px; vertical-align: top; }
th { background: #e8d4ad; text-align: left; }
figure { margin: 1.2em 0; text-align: center; break-inside: avoid; page-break-inside: avoid; }
figure img { max-width: 100%; height: auto; }
.art-inline { width: min(48%, 82mm); margin-left: auto; margin-right: auto; }
.art-inline img { max-width: 100%; }
figcaption { color: #6f5b3c; font-size: .88em; margin-top: .35em; }
.art-body-right { float: right; width: 25%; max-width: 320px; margin: .1em 0 .55em .85em; text-align: right; clear: right; }
.art-body-right img { width: 100%; max-height: 105mm; object-fit: contain; }
figure.art-body-right + h3,
figure.art-body-right + a + h3,
figure.art-body-right + h4,
figure.art-body-right + a + h4,
figure.art-float-right + h3,
figure.art-float-right + a + h3,
figure.art-float-right + h4,
figure.art-float-right + a + h4,
figure.art-scenario-right + h3,
figure.art-scenario-right + a + h3,
figure.art-scenario-right + h4,
figure.art-scenario-right + a + h4 { clear: none; }
.art-handout-page { width: 80%; max-width: 80%; margin: .4em auto; text-align: center; break-inside: avoid; page-break-inside: avoid; }
.art-handout-page img { width: 100%; max-height: 205mm; object-fit: contain; }
.artview-decision.artview-width-25 { width: 25%; }
.artview-decision.artview-width-80 { width: 80%; max-width: 80%; }
.artview-decision.artview-width-100 { width: 100%; max-width: 100%; }
.artview-decision.artview-align-center { float: none; clear: both; margin-left: auto; margin-right: auto; text-align: center; }
.artview-decision.artview-align-right.artview-wrap-text { float: right; clear: right; margin-left: .85em; margin-right: 0; text-align: right; }
.art-full-page, .art-cover, .art-pregen-fullpage { break-before: page; break-after: page; margin: 0; text-align: center; }
.art-full-page img, .art-cover img, .art-pregen-fullpage img { width: 100%; max-height: 250mm; object-fit: contain; }
.art-full-width { width: 100%; clear: both; }
.art-float-right, .art-scenario-right { float: right; width: min(48%, 82mm); margin: .15em 0 .65em 1em; text-align: right; }
.art-float-right.art-scale-30, .art-scenario-right.art-scale-30 { width: min(30%, 54mm); }
.art-scenario-compact, .art-flow-compact { width: min(44%, 76mm); }
.art-flow-half { width: min(50%, 86mm); }
.art-compact-sheet { width: min(38%, 64mm); }
.art-scale-50 img { max-width: 50%; }
.art-scale-100 img { max-width: 100%; }
.art-scale-90 img { max-width: 90%; }
.art-scale-80 img { max-width: 80%; }
.art-scale-70 img { max-width: 70%; }
.art-source-excluded-note, .art-technical-caption { display: none; }
code { background: #f0e4cf; padding: 1px 4px; border-radius: 2px; }
@media print {
  body { background: #fff; font-size: __PRINT_BODY_FONT_SIZE__; line-height: __PRINT_BODY_LINE_HEIGHT__; }
  main { max-width: none; padding: 0; background: #fff; column-count: __PRINT_COLUMNS__; column-gap: __PRINT_COLUMN_GAP__; }
  .production-landing {
    column-span: all;
    break-after: page;
    margin: 0;
    padding: 0;
    border-bottom: 0;
    position: relative;
    min-height: 267mm;
    display: block;
    background-repeat: no-repeat;
    background-position: center 56%;
    background-size: 100% auto;
  }
  .production-landing-title { top: 25%; margin-bottom: 0; }
  .production-landing-title-en { font-size: 28pt; }
  .production-landing-title-ru { font-size: 17pt; }
  .production-landing-figure { display: none; }
  .production-landing .art-cover { break-before: auto; break-after: auto; }
  .production-landing-figure img { width: 100%; max-height: 220mm; object-fit: contain; }
  .toc { column-span: all; break-after: page; page-break-after: always; min-height: 267mm; box-sizing: border-box; font-size: 12pt; padding: 16mm 18mm; }
  .toc-frame { min-height: 230mm; }
  .toc a { text-decoration: none; }
  .production-page { padding: 0 0 10px; border-bottom: 0; break-inside: auto; page-break-inside: auto; }
  .production-page.page-type-cover { column-span: all; min-height: 267mm; break-before: page; break-after: page; page-break-before: always; page-break-after: always; }
  .production-page.page-type-cover h1:first-of-type { padding-top: 34mm; }
  .production-page.page-type-cover h1 { font-size: 28pt; }
  .production-page.page-type-cover h2 { font-size: 17pt; }
  .production-page.page-type-cover p { font-size: 11pt; }
  .production-page.page-type-cover figure,
  .production-page.page-type-cover figure.keeper-art-block,
  .production-page.page-type-cover figure.art-cover,
  .production-page.page-type-cover figure.art-full-page {
    column-span: all !important;
    width: 100% !important;
    max-width: 100% !important;
    margin: 0 auto !important;
    break-before: auto !important;
    page-break-before: auto !important;
    break-after: auto !important;
    page-break-after: auto !important;
  }
  .production-page.page-type-cover figure img {
    width: 100% !important;
    max-width: 100% !important;
    max-height: 252mm !important;
    object-fit: contain !important;
  }
  .production-page.page-type-credits,
  .production-page.page-type-quote-art { column-span: all; min-height: 267mm; break-after: page; page-break-after: always; }
  .production-page.page-type-credits { padding: 16mm 18mm; background-repeat: no-repeat; background-position: center; background-size: cover; -webkit-print-color-adjust: exact; print-color-adjust: exact; }
  .production-page.page-type-credits .credits-frame { min-height: 230mm; padding: 10mm 11mm; background: rgba(255,250,240,.86); border: 2px solid rgba(96,75,49,.72); -webkit-print-color-adjust: exact; print-color-adjust: exact; }
  .credits-page-boundary { display: block; height: 0; margin: 0; padding: 0; column-span: all; break-before: page; page-break-before: always; }
  .production-page.page-type-credits h1 { margin: 0 0 4mm; font-size: 16pt; }
  .production-page.page-type-credits h2 { font-size: 16pt; margin: 0 0 4mm; text-align: center; }
  .production-page.page-type-credits .credits-columns { columns: var(--credits-columns, 2); column-fill: balance; column-gap: var(--credits-column-gap, 9mm); height: 194mm; font-size: var(--credits-font-size, 10pt); line-height: var(--credits-line-height, 1.15); overflow: hidden; overflow-wrap: anywhere; }
  .production-page.page-type-credits .credits-grid { columns: auto; display: grid; grid-template-columns: repeat(var(--credits-columns, 2), minmax(0, 1fr)); align-content: start; gap: var(--credits-column-gap, 9mm); height: auto; overflow: visible; }
  .production-page.page-type-credits .credit-item { margin-bottom: 1.4mm; }
  body.print-columns-1 .production-landing,
  body.print-columns-1 .toc,
  body.print-columns-1 .production-page.page-type-credits,
  body.print-columns-1 .production-page.page-type-quote-art,
  body.print-columns-1 .credits-page-boundary { column-span: none !important; }
  body.print-columns-1 .credits-page-boundary { display: none !important; break-before: auto; page-break-before: auto; }
  .production-page.page-type-quote-art p { max-width: 64%; font-size: 11pt; }
  body.print-columns-2 .production-page:not(.page-type-cover):not(.page-type-credits):not(.page-type-source-toc):not(.page-type-quote-art):not(.page-type-full-art):not(.page-type-statblock-card) { display: contents; }
  h1 { font-size: 1.35rem; }
  h2 { font-size: 1.08rem; }
  h3 { font-size: .98rem; }
  body.print-columns-2 h1 { column-span: all; }
  body.print-columns-2 h2,
  body.print-columns-2 h3,
  body.print-columns-2 h4,
  body.print-columns-2 h5,
  body.print-columns-2 h6 { column-span: none; }
  h1, h2, h3, h4, h5, h6 { margin: .75em 0 .25em; }
  p { margin: .38em 0; }
  ul, ol { margin: .38em 0 .38em 1.1em; padding-left: .8em; }
  figure, .table-wrap, blockquote.review-callout { break-inside: avoid; page-break-inside: avoid; }
__STATBLOCK_SECTION_FONT_CSS__
  .table-wrap { overflow: visible; }
  .statblock-card { font-size: 12pt; }
  .statblock-card { break-inside: avoid; page-break-inside: avoid; }
  .statblock-card .table-wrap { margin: .45em 0; overflow: visible; max-width: 100%; }
  .statblock-card table { table-layout: auto; width: 100%; max-width: 100%; font-size: .6em; }
  .statblock-card table.statblock-attributes-table { font-size: .56em; }
  .statblock-card table.statblock-derived-table { font-size: .58em; }
  .statblock-card table.statblock-actions-table { font-size: .6em; }
  .statblock-card table.statblock-dune-drives-table,
  .statblock-card table.statblock-dune-skills-table { font-size: .64em; }
  .statblock-card table.has-index-column th:first-child,
  .statblock-card table.has-index-column td:first-child { width: 1.8em; min-width: 1.8em; max-width: 1.8em; padding-left: 1px; padding-right: 1px; text-align: center; white-space: nowrap; }
  .statblock-card th,
  .statblock-card td { padding: 1px 2px; overflow-wrap: normal; word-break: normal; white-space: normal; }
  body.print-columns-2 blockquote.review-callout { column-span: all; columns: 2; column-gap: 8mm; break-inside: auto; page-break-inside: auto; }
  body.print-columns-2 blockquote.review-callout p { break-inside: auto; }
  figure { margin: .55em 0; }
  figure img { max-height: 120mm; object-fit: contain; }
  figure.art-inline { width: 25%; max-width: 42mm; margin-left: auto; margin-right: auto; }
  figure.art-inline img { width: 100%; max-height: 72mm; object-fit: contain; }
  figure.art-body-right { float: right; width: 25%; max-width: 42mm; margin: .1em 0 .45em .75em; clear: right; }
  figure.art-body-right img { width: 100%; max-height: 72mm; object-fit: contain; }
  figure.art-handout-page { float: none; width: 80%; max-width: 80%; margin: .4em auto; break-before: auto; page-break-before: auto; break-after: auto; page-break-after: auto; }
  figure.art-handout-page img { width: 100%; max-height: 205mm; object-fit: contain; }
  figure.artview-decision.artview-width-25 { width: 25%; max-width: 42mm; }
  figure.artview-decision.artview-width-80 { width: 80%; max-width: 80%; }
  figure.artview-decision.artview-width-100 { width: 100%; max-width: 100%; }
  figure.artview-decision.artview-align-center { float: none; clear: both; margin-left: auto; margin-right: auto; }
  figure.artview-decision.artview-align-right.artview-wrap-text { float: right; clear: right; margin-left: .75em; margin-right: 0; }
  body.print-columns-2 figure.art-full-width { column-span: all; width: 100%; clear: both; margin: .55em 0 .8em; break-inside: avoid; page-break-inside: avoid; }
  body.print-columns-2 figure.art-full-width img { width: 100%; max-height: 92mm; object-fit: contain; }
  .art-full-page, .art-cover, .art-pregen-fullpage { break-before: page; break-after: page; column-span: all; }
  body.print-columns-1 .art-full-page,
  body.print-columns-1 .art-cover,
  body.print-columns-1 .art-pregen-fullpage {
    break-before: auto; page-break-before: auto;
    break-after: auto; page-break-after: auto;
    column-span: none;
  }
  .art-full-page img, .art-cover img, .art-pregen-fullpage img { max-height: 252mm; }
  .art-float-right, .art-scenario-right { float: right; width: 46%; margin: .1em 0 .45em .75em; }
  .art-float-right.art-scale-30, .art-scenario-right.art-scale-30 { width: 30%; }
  .art-scenario-compact, .art-flow-compact { width: 42%; }
  .art-compact-sheet { width: 36%; }
  figcaption { font-size: .72em; }
  table { font-size: .68em; line-height: 1.16; }
  th, td { padding: 2px 3px; }
__BODY_ART_TABLE_FLOW_CSS__
__FULL_PAGE_HEADING_KEEP_CSS__
__LONG_CALLOUT_PAGE_FLOW_CSS__
__SECTION_START_PAGE_CSS__
}
""".replace("__PRINT_COLUMNS__", print_column_count).replace("__PRINT_COLUMN_GAP__", print_column_gap).replace("__STATBLOCK_SECTION_FONT_CSS__", statblock_section_font_css).replace("__BODY_ART_TABLE_FLOW_CSS__", body_art_table_flow_css).replace("__FULL_PAGE_HEADING_KEEP_CSS__", full_page_heading_keep_css).replace("__LONG_CALLOUT_PAGE_FLOW_CSS__", long_callout_page_flow_css).replace("__SECTION_START_PAGE_CSS__", section_start_page_css)
    css = (
        css.replace("__BODY_FONT_FAMILY__", typography["body_font_family"])
        .replace("__BODY_FONT_SIZE__", typography["body_font_size"])
        .replace("__BODY_LINE_HEIGHT__", typography["body_line_height"])
        .replace("__PRINT_BODY_FONT_SIZE__", typography["print_body_font_size"])
        .replace("__PRINT_BODY_LINE_HEIGHT__", typography["print_body_line_height"])
        .replace("__COVER_BACKGROUND__", cover_background_css)
        .replace("__COVER_TEXT_COLOR__", cover_text_color_css)
        .replace("__COVER_TEXT_SHADOW__", cover_text_shadow_css)
        .replace("__COVER_HEADING_BORDER__", cover_heading_border_css)
    )
    return f"""<!doctype html>
<html lang="ru">
<head>
  <meta charset="utf-8">
  <title>{html_lib.escape(title)}</title>
  <style>{css}</style>
</head>
<body class="{body_classes}">
<main>
{landing_html}
{toc_html}
{body}
</main>
</body>
</html>
"""


def suppress_section_navigation_lists(body: str, config: dict[str, Any]) -> tuple[str, list[str]]:
    """Remove configured micro-TOC lists after a section heading in downstream HTML."""
    raw_anchor_ids = production_html_config(config).get("suppress_section_navigation_after_anchor_ids", [])
    if not isinstance(raw_anchor_ids, list):
        return body, []
    anchor_ids = {
        str(value).strip()
        for value in raw_anchor_ids
        if re.fullmatch(r"[A-Za-z][A-Za-z0-9_-]*", str(value).strip())
    }
    if not anchor_ids:
        return body, []

    lines = body.splitlines()
    output: list[str] = []
    removed: list[str] = []
    index = 0
    while index < len(lines):
        line = lines[index]
        anchor_match = re.fullmatch(r'<a\b[^>]*\bid="([^"]+)"[^>]*></a>', line, re.I)
        if not anchor_match or anchor_match.group(1) not in anchor_ids:
            output.append(line)
            index += 1
            continue

        anchor_id = anchor_match.group(1)
        output.append(line)
        index += 1
        if index >= len(lines) or not re.match(r"^<h[1-6]\b", lines[index], re.I):
            continue
        output.append(lines[index])
        index += 1
        while index < len(lines) and re.match(r"^<figure\b[^>]*>.*</figure>$", lines[index], re.I):
            output.append(lines[index])
            index += 1
        if index >= len(lines) or not re.match(r"^<ul>\s*$", lines[index], re.I):
            continue
        while index < len(lines):
            closing = bool(re.match(r"^</ul>\s*$", lines[index], re.I))
            index += 1
            if closing:
                break
        removed.append(anchor_id)
    return "\n".join(output), removed


def wrap_section_page_starts(body: str, config: dict[str, Any]) -> tuple[str, list[str]]:
    """Wrap configured section anchors and headings in non-empty page-start blocks."""
    raw_anchor_ids = production_html_config(config).get("page_break_before_anchor_ids", [])
    if not isinstance(raw_anchor_ids, list):
        return body, []
    anchor_ids = {
        str(value).strip()
        for value in raw_anchor_ids
        if re.fullmatch(r"[A-Za-z][A-Za-z0-9_-]*", str(value).strip())
    }
    if not anchor_ids:
        return body, []

    lines = body.splitlines()
    output: list[str] = []
    inserted: list[str] = []
    index = 0
    while index < len(lines):
        line = lines[index]
        anchor_match = re.fullmatch(r'<a\b[^>]*\bid="([^"]+)"[^>]*></a>', line, re.I)
        if (
            anchor_match
            and anchor_match.group(1) in anchor_ids
            and index + 1 < len(lines)
            and re.match(r"^<h2\b", lines[index + 1], re.I)
            and (index == 0 or lines[index - 1] != '<section class="production-section-start">')
        ):
            output.extend([
                '<section class="production-section-start">',
                line,
                lines[index + 1],
                "</section>",
            ])
            inserted.append(anchor_match.group(1))
            index += 2
            continue
        output.append(line)
        index += 1
    return "\n".join(output), inserted


def bind_section_heading_into_first_card(body: str, config: dict[str, Any]) -> tuple[str, list[str]]:
    """Move configured group anchor/H2 into its immediately following full-page card."""
    raw_anchor_ids = production_html_config(config).get("bind_section_heading_into_first_card_anchor_ids", [])
    if not isinstance(raw_anchor_ids, list):
        return body, []
    anchor_ids = [
        str(value).strip()
        for value in raw_anchor_ids
        if re.fullmatch(r"[A-Za-z][A-Za-z0-9_-]*", str(value).strip())
    ]
    bound: list[str] = []
    for anchor_id in anchor_ids:
        pattern = re.compile(
            rf'(<a\b[^>]*\bid="{re.escape(anchor_id)}"[^>]*></a>\n'
            rf'<h2\b[^>]*>.*?</h2>)\n'
            rf'(<section\b[^>]*\bclass="[^"]*\bfull-page-art-card\b[^"]*"[^>]*>)',
            re.I,
        )
        def bind_match(match: re.Match[str]) -> str:
            card_open = match.group(2).replace(
                'class="', 'class="section-heading-bound-card ', 1
            )
            return f"{card_open}\n{match.group(1)}"

        body, count = pattern.subn(bind_match, body, count=1)
        if count:
            bound.append(anchor_id)
    return body, bound


def wrap_full_page_art_cards(body: str, config: dict[str, Any]) -> tuple[str, int]:
    """Wrap full-page figures, plus a nearby heading/caption, in atomic print cards."""
    if not production_html_config(config).get("keep_full_page_art_with_heading", False):
        return body, 0

    lines = body.splitlines()
    groups: list[tuple[int, int, str]] = []
    claimed: set[int] = set()
    for figure_index, line in enumerate(lines):
        figure_match = re.search(
            r'<figure\b[^>]*\bclass="[^"]*\b(art-full-page|art-handout-page|art-pregen-fullpage)\b', line, re.I
        )
        if not figure_match:
            continue
        art_class = figure_match.group(1).casefold()
        card_class = (
            " handout-art-card" if art_class == "art-handout-page"
            else " pregen-art-card" if art_class == "art-pregen-fullpage"
            else ""
        )
        start = figure_index
        cursor = figure_index - 1
        caption_count = 0
        while cursor >= 0 and caption_count < 3 and re.match(r"^<p\b", lines[cursor], re.I):
            start = cursor
            cursor -= 1
            caption_count += 1
        if cursor >= 0 and re.match(r"^<h[1-4]\b", lines[cursor], re.I):
            start = cursor
            if cursor > 0 and re.match(r'^<a\b[^>]*\bid="[^"]+"[^>]*></a>$', lines[cursor - 1], re.I):
                start = cursor - 1
        else:
            start = figure_index
            if figure_index > 0 and re.match(r'^<a\b[^>]*\bid="[^"]+"[^>]*></a>$', lines[figure_index - 1], re.I):
                start = figure_index - 1
        end = figure_index
        if card_class:
            cursor = figure_index + 1
            trailing_count = 0
            while cursor < len(lines) and trailing_count < 3 and re.match(r"^<p\b", lines[cursor], re.I):
                end = cursor
                cursor += 1
                trailing_count += 1
        if any(index in claimed for index in range(start, end + 1)):
            start = figure_index
        claimed.update(range(start, end + 1))
        groups.append((start, end, card_class))

    starts = {start: card_class for start, _, card_class in groups}
    ends = {end for _, end, _ in groups}
    output: list[str] = []
    for index, line in enumerate(lines):
        if index in starts:
            output.append(f'<section class="full-page-art-card{starts[index]}">')
        output.append(line)
        if index in ends:
            output.append("</section>")
    return "\n".join(output), len(groups)


def suppress_generic_figure_captions(body: str, config: dict[str, Any]) -> tuple[str, list[str]]:
    """Remove configured or generated technical labels, preserving authored captions."""
    production = production_html_config(config)
    raw_values = production.get("suppress_figure_captions", [])
    if not isinstance(raw_values, list):
        return body, []
    suppressed = {str(value).strip().casefold() for value in raw_values if str(value).strip()}
    raw_policy = production.get("figure_caption_policy", {})
    if not isinstance(raw_policy, dict) or set(raw_policy) - {"mode"}:
        raise ValueError("production_html.figure_caption_policy must be a closed object")
    caption_mode = str(raw_policy.get("mode", "all")).strip().casefold()
    if caption_mode not in {"all", "authored_only"}:
        raise ValueError("production_html.figure_caption_policy.mode is invalid")
    if not suppressed and caption_mode == "all":
        return body, []
    removed: list[str] = []

    def is_technical_caption(plain: str) -> bool:
        if caption_mode != "authored_only":
            return False
        return bool(
            re.fullmatch(
                r"(?:cover|source image from page\s+\d+|исходное изображение со страницы\s+\d+)",
                plain,
                re.I,
            )
        )

    def replace(match: re.Match[str]) -> str:
        plain = html_lib.unescape(re.sub(r"<[^>]+>", "", match.group(1))).strip()
        if plain.casefold() not in suppressed and not is_technical_caption(plain):
            return match.group(0)
        removed.append(plain)
        return ""

    return re.sub(r"<figcaption>(.*?)</figcaption>", replace, body, flags=re.I | re.S), removed


def preserved_page_art_figures(config: dict[str, Any], html_path: Path) -> list[dict[str, Any]]:
    figures: list[dict[str, Any]] = []
    for index, item in enumerate(art_integration_config(config).get("preserved_page_art", []), start=1):
        role = str(item.get("role") or "source_image")
        if role not in IMAGE_COPY_ROLES:
            continue
        try:
            page = int(item.get("page"))
        except (TypeError, ValueError):
            continue
        target_filename = item.get("target_filename") or f"page-{page:03d}-{role}.png"
        try:
            target = target_dir_for_image_role(config, role) / safe_filename(str(target_filename))
        except ValueError:
            continue
        rel_src = os.path.relpath(target, html_path.parent).replace("\\", "/")
        caption = str(item.get("caption") or item.get("review_notes") or f"Preserved source {role}, page {page:03d}")
        include_caption = bool(item.get("include_caption", False) and caption)
        caption_html = f"<figcaption>{html_lib.escape(caption)}</figcaption>" if include_caption else ""
        css_class = str(item.get("css_class") or "art-full-width")
        columnned = item.get("columnned", item.get("columned", True))
        columnned_value = "true" if bool(columnned) else "false"
        figures.append(
            {
                "page": f"{page:03d}",
                "target": target,
                "insert_after_heading_id": str(item.get("insert_after_heading_id") or ""),
                "insert_position": str(item.get("insert_position") or ""),
                "html": (
                    '<figure class="preserved-page-art {css_class}" data-source-page="{page}" data-role="{role}" data-columnned="{columnned}">'
                    '<img src="{src}" alt="{alt}">'
                    "{caption_html}"
                    "</figure>"
                ).format(
                    css_class=html_lib.escape(css_class),
                    page=f"{page:03d}",
                    role=html_lib.escape(role),
                    columnned=columnned_value,
                    src=html_lib.escape(rel_src),
                    alt=html_lib.escape(f"Preserved {role} from source page {page:03d}"),
                    caption_html=caption_html,
                ),
            }
        )
    return figures


def inject_preserved_page_art(body: str, config: dict[str, Any], html_path: Path) -> tuple[str, list[dict[str, Any]]]:
    figures = preserved_page_art_figures(config, html_path)
    if not figures:
        return body, []
    inserted: list[dict[str, Any]] = []
    for figure in figures:
        page = figure["page"]
        pattern = re.compile(
            rf'(<section class="[^"]*\b(?:review|production)-page\b[^"]*" id="page-{page}" data-page="{page}">[\s\S]*?)(</section>)',
            re.M,
        )
        match = pattern.search(body)
        src_match = re.search(r'<img\b[^>]*\bsrc="([^"]+)"', figure["html"], re.I)
        src = src_match.group(1) if src_match else ""
        if match and src and src in match.group(1):
            inserted.append(
                {
                    "page": page,
                    "target_path": rel(figure["target"]),
                    "inserted": False,
                    "reason": "already_referenced_in_page_section",
                }
            )
            continue
        insert_after_heading_id = str(figure.get("insert_after_heading_id") or "")
        insert_position = str(figure.get("insert_position") or "")
        if match and insert_position == "section_start":
            section_html = match.group(1)
            marker_re = re.compile(r'(<div\b[^>]*\bclass=["\']page-marker["\'][\s\S]*?</div>)', re.I)
            section_html, marker_count = marker_re.subn(rf"\1\n{figure['html']}", section_html, count=1)
            if marker_count == 1:
                body = body[: match.start(1)] + section_html + body[match.end(1):]
                count = 1
            else:
                body, count = pattern.subn(rf"\1\n{figure['html']}\n\2", body, count=1)
        elif match and insert_after_heading_id:
            section_html = match.group(1)
            heading_re = re.compile(
                rf'(<h[1-6]\b[^>]*\bid="{re.escape(insert_after_heading_id)}"[^>]*>[\s\S]*?</h[1-6]>)',
                re.I,
            )
            section_html, heading_count = heading_re.subn(rf"\1\n{figure['html']}", section_html, count=1)
            if heading_count == 1:
                body = body[: match.start(1)] + section_html + body[match.end(1):]
                count = 1
            else:
                body, count = pattern.subn(rf"\1\n{figure['html']}\n\2", body, count=1)
        else:
            body, count = pattern.subn(rf"\1\n{figure['html']}\n\2", body, count=1)
        inserted.append(
            {
                "page": page,
                "target_path": rel(figure["target"]),
                "inserted": count == 1,
                "insert_after_heading_id": insert_after_heading_id or None,
                "insert_position": insert_position or None,
            }
        )
    return body, inserted


def suppress_production_reader_noise(body: str, config: dict[str, Any]) -> tuple[str, list[dict[str, Any]]]:
    suppressed: list[dict[str, Any]] = []
    patterns = list(production_html_config(config).get("suppress_reader_noise_patterns", []))
    for pattern in patterns:
        needle = str(pattern)
        if not needle:
            continue
        block_re = re.compile(
            rf"\n?<p>(?:<em>)?\s*(?:{needle})\s*(?:</em>)?</p>\n?",
            re.I,
        )
        body, count = block_re.subn("\n", body)
        suppressed.append({"pattern": needle, "count": count})
    for heading_id in production_html_config(config).get("suppress_heading_ids", []):
        heading_id = str(heading_id).strip()
        if not heading_id:
            continue
        heading_re = re.compile(
            rf'\n?<h[1-6]\b[^>]*\bid=["\']{re.escape(heading_id)}["\'][^>]*>[\s\S]*?</h[1-6]>\n?',
            re.I,
        )
        body, count = heading_re.subn("\n", body)
        suppressed.append({"heading_id": heading_id, "count": count})
    return body, suppressed


def suppress_production_body_images(body: str, config: dict[str, Any]) -> tuple[str, list[dict[str, Any]]]:
    suppressed: list[dict[str, Any]] = []
    patterns = list(production_html_config(config).get("suppress_body_image_refs", []))
    if production_html_config(config).get("landing_asset"):
        patterns.extend(production_html_config(config).get("landing_asset", {}).get("replaces_body_image_refs", []))
    for pattern in patterns:
        needle = str(pattern)
        if not needle:
            continue
        figure_re = re.compile(rf"\n?<figure\b[^>]*>[\s\S]*?{re.escape(needle)}[\s\S]*?</figure>\n?", re.I)
        body, count = figure_re.subn("\n", body)
        suppressed.append({"pattern": needle, "count": count})
    return body, suppressed


def build_production_html(config_path: Path, *, force: bool = False, check_only: bool = False, trial: bool = False) -> dict[str, Any]:
    config = read_json(config_path)
    source = production_html_source_path(config, trial=trial)
    target = production_html_target_path(config, trial=trial)
    report = production_html_report_path(config)
    findings = production_entry_findings(config, source)
    gate_findings = list(findings)
    if findings and not trial:
        result = {
            "schema": "translator_production_html.v1",
            "generated_at_utc": datetime.now(timezone.utc).isoformat(),
            "config": rel(config_path),
            "source_markdown": rel(source),
            "production_html": rel(target),
            "status": "blocked",
            "action": "check_only" if check_only else "not_built",
            "mode": "production",
            "required_gates": production_required_gates(config),
            "counts": {"findings": len(findings)},
            "findings": findings,
        }
        write_json(report, result)
        return result
    if trial and not source.exists():
        result = {
            "schema": "translator_production_html.v1",
            "generated_at_utc": datetime.now(timezone.utc).isoformat(),
            "config": rel(config_path),
            "source_markdown": rel(source),
            "production_html": rel(target),
            "status": "blocked",
            "action": "trial_not_built",
            "mode": "trial",
            "required_gates": production_required_gates(config),
            "counts": {"findings": 1 + len(gate_findings)},
            "findings": [{"code": "missing_trial_source_markdown", "path": rel(source)}] + gate_findings,
        }
        write_json(report, result)
        return result
    if target.exists() and not force and not check_only:
        html_text = target.read_text(encoding="utf-8")
        result = {
            "schema": "translator_production_html.v1",
            "generated_at_utc": datetime.now(timezone.utc).isoformat(),
            "config": rel(config_path),
            "source_markdown": rel(source),
            "production_html": rel(target),
            "status": "trial_needs_review" if trial else "pass",
            "action": "trial_kept_existing" if trial else "kept_existing",
            "mode": "trial" if trial else "production",
            "required_gates": production_required_gates(config),
            "counts": {
                "html_bytes": len(html_text.encode("utf-8")),
                "headings": len(re.findall(r"<h[1-6]\b", html_text)),
                "source_pages": len(re.findall(r'class="production-page"', html_text)),
                "image_refs": len(html_refs(html_text)),
                "findings": 0,
            },
            "sha256": sha256_text(html_text),
        }
        write_json(report, result)
        return result
    md = source.read_text(encoding="utf-8")
    md, handout_heading_transform = normalize_appendix_handout_headings(md, config)
    md, reader_art_relocation = relocate_reader_art_blocks(md, config)
    md, suppressed_reader_metadata = suppress_reader_metadata_markdown(md, config)
    reader_art_classes, _ = reader_art_layout_from_manifest(config)
    normalized_markdown = normalized_markdown_output_path(config, trial=trial)
    frontmatter_policy = resolved_frontmatter_policy(config)
    toc_policy_for_source = frontmatter_policy["toc_policy"]
    toc_mode = str(toc_policy_for_source["mode"]).strip().casefold()
    source_toc = source_toc_from_markdown(md, config) if toc_mode in {"source", "preserve_source", "preserve_and_link"} else None
    md, callout_transform = transform_markdown_callouts(md, config)
    list_continuity = ordered_list_continuity_report(md, config)
    body, toc, source_pages = markdown_to_review_html(
        md,
        source_path=source,
        html_path=target,
        art_classes=reader_art_classes,
    )
    body = body.replace('class="review-page"', 'class="production-page"').replace(">source page ", ">page ")
    body, page_type_annotations = annotate_page_type_sections(body, config)
    body, removed_source_toc = remove_source_toc_sections(body, config, source_toc=source_toc)
    body, removed_manual_toc = remove_manual_toc_sections(body, config)
    body, removed_source_cover = remove_source_cover_sections(body, config)
    body, suppressed_reader_noise = suppress_production_reader_noise(body, config)
    body, suppressed_body_images = suppress_production_body_images(body, config)
    body, suppressed_figure_captions = suppress_generic_figure_captions(body, config)
    body, suppressed_section_navigation = suppress_section_navigation_lists(body, config)
    body, section_page_starts = wrap_section_page_starts(body, config)
    body, preserved_art = inject_preserved_page_art(body, config, target)
    body, transformed_credits = transform_credits_sections(body, config)
    body, table_continuations = merge_table_continuations(body, config)
    body, transformed_quote_art = transform_quote_art_sections(body, config)
    body, statblock_cards = wrap_statblock_cards(body, config)
    body, statblock_page_callouts = wrap_page_type_statblock_callouts(body)
    body, heading_level_overrides = apply_heading_level_overrides(body, config)
    body, full_page_art_cards = wrap_full_page_art_cards(body, config)
    body, section_headings_bound_into_first_card = bind_section_heading_into_first_card(body, config)
    production_source_toc = source_toc_with_internal_links(source_toc, toc, config) if source_toc else None
    toc_html = (
        ""
        if toc_policy_for_source["mode"] == "disabled"
        else build_production_toc(toc, config, source_toc=production_source_toc)
    )
    html_text = build_production_html_document(config, body, toc_html)
    # Count the final semantic class, not only heading-based cards introduced
    # by ``wrap_statblock_cards``. Typed statblock transport produces the same
    # neutral class and must be visible in production QA evidence.
    statblock_cards = html_class_token_count(html_text, "statblock-card")
    html_text, landing_toc_order_ok, landing_toc_order_action = place_landing_and_toc(config, html_text)
    frontmatter_manifest = build_frontmatter_manifest(config, html_text, production_source_toc)
    frontmatter_path = frontmatter_report_path(config)
    refs = html_refs(html_text)
    resolved = [(ref, (target.parent / ref.replace("/", "\\")).resolve()) for ref in refs]
    missing = [ref for ref, path in resolved if not path.exists() and "://" not in ref and not ref.startswith("data:")]
    findings = [{"code": "missing_image_ref", "message": ref} for ref in missing]
    semantic_findings: list[dict[str, Any]] = []
    toc_policy = toc_policy_for_source
    source_toc_pages = [page for page, meta in page_map_config(config).items() if str(meta.get("type") or "") == "source_toc"]
    if production_source_toc and production_source_toc["page"] not in source_toc_pages:
        source_toc_pages.append(production_source_toc["page"])
    source_cover_pages = [page for page, meta in page_map_config(config).items() if str(meta.get("type") or "") == "cover"]
    landing_asset = production_html_config(config).get("landing_asset", {})
    suppress_source_cover = isinstance(landing_asset, dict) and bool(landing_asset.get("suppress_source_cover_page", False))
    if suppress_source_cover:
        not_removed_cover = [item for item in removed_source_cover if item.get("count") != 1]
        if source_cover_pages and not_removed_cover:
            semantic_findings.append({"code": "source_cover_not_suppressed", "pages": [item["page"] for item in not_removed_cover]})
        visible_source_cover = [
            page for page in source_cover_pages
            if re.search(rf'id=["\']page-{re.escape(page)}["\']', html_text)
        ]
        if visible_source_cover:
            semantic_findings.append({"code": "duplicate_source_cover_page_visible", "pages": visible_source_cover})
    if toc_policy.get("replace_source_toc_pages", True):
        not_removed = [item for item in removed_source_toc if item.get("count") != 1]
        if source_toc_pages and not_removed:
            semantic_findings.append({"code": "source_toc_not_replaced", "pages": [item["page"] for item in not_removed]})
        visible_source_toc = [
            page for page in source_toc_pages
            if re.search(rf'id=["\']page-{re.escape(page)}["\']', html_text)
        ]
        if visible_source_toc:
            semantic_findings.append({"code": "duplicate_source_toc_page_visible", "pages": visible_source_toc})
        if toc_mode in {"source", "preserve_source", "preserve_and_link"} and source_toc_pages and source_toc is None:
            semantic_findings.append({"code": "source_toc_content_not_preserved", "pages": source_toc_pages})
        if production_source_toc and any(entry.get("href") is None for entry in production_source_toc["entries"]):
            semantic_findings.append(
                {
                    "code": "source_toc_entry_unresolved",
                    "entries": [entry["title"] for entry in production_source_toc["entries"] if entry.get("href") is None],
                }
            )
        if production_source_toc:
            semantic_findings.extend(production_source_toc.get("link_map_findings", []))
    if toc_policy["mode"] != "disabled" and not TOC_RE.search(html_text):
        semantic_findings.append({"code": "missing_generated_toc"})
    if toc_html.strip() and not landing_toc_order_ok:
        semantic_findings.append({"code": "landing_toc_order", "action": landing_toc_order_action})
    semantic_findings.extend(callout_transform["findings"])
    semantic_findings.extend(handout_heading_transform["findings"])
    semantic_findings.extend(reader_art_relocation["findings"])
    semantic_findings.extend(list_continuity["findings"])
    findings.extend(semantic_findings)
    all_findings = findings + ([{"code": "trial_bypassed_gate", **item} for item in gate_findings] if trial else [])
    status = "fail" if findings else ("trial_needs_review" if trial else "pass")
    action = "check_only" if check_only else (
        ("trial_rewritten" if target.exists() else "trial_created") if trial else ("rewritten" if target.exists() else "created")
    )
    if not check_only:
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(html_text, encoding="utf-8", newline="\n")
        write_json(frontmatter_path, frontmatter_manifest)
        if normalized_markdown:
            normalized_markdown.parent.mkdir(parents=True, exist_ok=True)
            normalized_markdown.write_text(md, encoding="utf-8", newline="\n")
    result = {
        "schema": "translator_production_html.v1",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "config": rel(config_path),
        "source_markdown": rel(source),
        "production_html": rel(target),
        "normalized_markdown": rel(normalized_markdown) if normalized_markdown else None,
        "status": status,
        "action": action,
        "mode": "trial" if trial else "production",
        "required_gates": production_required_gates(config),
        "counts": {
            "html_bytes": len(html_text.encode("utf-8")),
            "headings": len(toc),
            "source_pages": source_pages,
            "image_refs": len(refs),
            "missing_image_refs": len(missing),
            "preserved_page_art_refs": sum(1 for item in preserved_art if item["inserted"]),
            "statblock_cards": statblock_cards,
            "full_page_art_cards": full_page_art_cards,
            "statblock_page_callouts": statblock_page_callouts,
            "page_type_annotations": len(page_type_annotations),
            "removed_source_cover_pages": sum(item["count"] for item in removed_source_cover),
            "removed_source_toc_pages": sum(item["count"] for item in removed_source_toc),
            "removed_manual_toc_sections": len(removed_manual_toc),
            "source_toc_entries": len(production_source_toc["entries"]) if production_source_toc else 0,
            "converted_callouts": len(callout_transform["converted"]),
            "relocated_reader_art_blocks": sum(1 for item in reader_art_relocation["relocated"] if item["moved"]),
            "suppressed_reader_metadata": len(suppressed_reader_metadata),
            "normalized_handout_headings": len(handout_heading_transform["transformed"]),
            "normalized_markdown_bytes": len(md.encode("utf-8")) if normalized_markdown else 0,
            "ordered_list_blocks": len(list_continuity["blocks"]),
            "transformed_credit_tables": sum(item["count"] for item in transformed_credits),
            "transformed_quote_art_pages": sum(item["count"] for item in transformed_quote_art),
            "heading_level_overrides": len(heading_level_overrides),
            "suppressed_reader_noise_blocks": sum(item["count"] for item in suppressed_reader_noise),
            "suppressed_body_image_refs": sum(item["count"] for item in suppressed_body_images),
            "suppressed_figure_captions": len(suppressed_figure_captions),
            "suppressed_section_navigation_lists": len(suppressed_section_navigation),
            "section_page_starts": len(section_page_starts),
            "section_headings_bound_into_first_card": len(section_headings_bound_into_first_card),
            "findings": len(all_findings),
            "trial_bypassed_gates": len(gate_findings) if trial else 0,
        },
        "sha256": sha256_text(html_text),
        "preserved_page_art": preserved_art,
        "page_type_annotations": page_type_annotations,
        "removed_source_cover": removed_source_cover,
        "removed_source_toc": removed_source_toc,
        "source_toc": production_source_toc,
        "frontmatter_manifest": rel(frontmatter_path),
        "frontmatter": frontmatter_manifest,
        "removed_manual_toc": removed_manual_toc,
        "callout_transform": callout_transform,
        "handout_heading_transform": handout_heading_transform,
        "reader_art_relocation": reader_art_relocation,
        "suppressed_reader_metadata": suppressed_reader_metadata,
        "ordered_list_continuity": list_continuity,
        "transformed_credits": transformed_credits,
        "table_continuations": table_continuations,
        "transformed_quote_art": transformed_quote_art,
        "heading_level_overrides": heading_level_overrides,
        "suppressed_reader_noise": suppressed_reader_noise,
        "suppressed_body_images": suppressed_body_images,
        "suppressed_figure_captions": suppressed_figure_captions,
        "suppressed_section_navigation": suppressed_section_navigation,
        "section_page_starts": section_page_starts,
        "section_headings_bound_into_first_card": section_headings_bound_into_first_card,
        "landing_toc_order": {"ok": landing_toc_order_ok, "action": landing_toc_order_action},
        "findings": all_findings,
    }
    write_json(report, result)
    return result


def source_reconstruction_config(config: dict[str, Any]) -> dict[str, Any]:
    return config.get("source_reconstruction", {})


def source_reconstruction_source_path(config: dict[str, Any]) -> Path:
    sr = source_reconstruction_config(config)
    if sr.get("source_markdown"):
        return root_path(str(sr["source_markdown"]))
    intake = intake_config(config)
    if intake.get("normalized_text"):
        return root_path(str(intake["normalized_text"]))
    if intake.get("raw_text"):
        return root_path(str(intake["raw_text"]))
    raise KeyError("source_reconstruction.source_markdown")


def source_reconstruction_output_path(config: dict[str, Any], key: str, default_name: str) -> Path:
    sr = source_reconstruction_config(config)
    value = sr.get(key, default_name)
    path = Path(str(value).replace("/", "\\"))
    return path.resolve() if path.is_absolute() else qa_root(config) / path


def page_render_dir(config: dict[str, Any]) -> Path:
    return root_path(intake_config(config).get("page_renders", f"{config['workbench_root']}/Images/Page_Renders"))


def page_render_path(render_dir: Path, page: int | None) -> Path | None:
    if page is None:
        return None
    candidates = [
        render_dir / f"page-{page:02d}.png",
        render_dir / f"page-{page:03d}.png",
        render_dir / f"p{page:03d}.png",
    ]
    return next((candidate for candidate in candidates if candidate.exists()), candidates[0])


def compact_excerpt(text: str, limit: int = 700) -> str:
    compact = re.sub(r"\s+", " ", text).strip()
    return compact if len(compact) <= limit else compact[: limit - 1].rstrip() + "…"


def source_reconstruction_markdown(result: dict[str, Any]) -> str:
    lines = [
        f"# {result.get('title', 'Source Reconstruction')} - task packet",
        "",
        f"- Status: `{result['status']}`",
        f"- Source markdown: `{result['source_markdown']}`",
        f"- Page renders: `{result['page_render_dir']}`",
        f"- Pages: `{result['counts']['pages']}`",
        f"- Pages with render: `{result['counts']['pages_with_render']}`",
        f"- Pages missing render: `{result['counts']['pages_missing_render']}`",
        f"- Pages with QA findings: `{result['counts']['pages_with_qa_findings']}`",
        f"- Empty/image-only pages: `{result['counts']['empty_pages']}`",
        "",
        "## Purpose",
        "",
        "This packet prepares manual source reconstruction. It does not approve text order, translation, KeeperBook, HTML, or PDF.",
        "",
    ]
    global_findings = result.get("global_findings", [])
    if global_findings:
        lines.extend(["## Global Findings", ""])
        for item in global_findings:
            lines.append(f"- `{item.get('code')}`: {item.get('count', item.get('message', 'review'))}")
        lines.append("")
    lines.extend(
        [
            "## Page Tasks",
            "",
            "| Page | Status | Render | Chars | QA findings |",
            "|---:|---|---|---:|---:|",
        ]
    )
    for page in result["pages"]:
        render = page.get("render")
        render_text = f"`{render}`" if render else "missing"
        lines.append(
            f"| {page['page']} | `{page['status']}` | {render_text} | {page['chars']} | {len(page.get('findings', []))} |"
        )
    lines.append("")
    for page in result["pages"]:
        lines.extend(
            [
                f"## Page {int(page['page']):03d}",
                "",
                f"- Status: `{page['status']}`",
                f"- Render: `{page.get('render') or 'missing'}`",
                f"- Chars: `{page['chars']}`",
                f"- Nonempty lines: `{page.get('nonempty_lines', 0)}`",
                "",
            ]
        )
        if page.get("findings"):
            lines.extend(["### QA Findings", ""])
            for item in page["findings"]:
                examples = item.get("examples") or []
                extra = f" Examples: {'; '.join(str(example) for example in examples[:3])}" if examples else ""
                lines.append(f"- `{item.get('code')}`{extra}")
            lines.append("")
        lines.extend(["### Normalized Excerpt", "", page.get("excerpt", ""), ""])
    return "\n".join(lines).rstrip() + "\n"


def prepare_source_reconstruction(config_path: Path, *, force: bool = False) -> dict[str, Any]:
    config = read_json(config_path)
    source = source_reconstruction_source_path(config)
    packet_json = source_reconstruction_output_path(config, "task_packet_json", "source_reconstruction_tasks.json")
    packet_md = source_reconstruction_output_path(config, "task_packet_md", "source_reconstruction_tasks.md")
    if not source.exists():
        raise FileNotFoundError(source)
    if packet_json.exists() and packet_md.exists() and not force:
        result = read_json(packet_json)
        result["action"] = "kept_existing"
        write_json(packet_json, result)
        return result

    text = source.read_text(encoding="utf-8")
    pages = split_raw_text_pages(text)
    render_dir = page_render_dir(config)
    qa_path = intake_report_path(config, "source_text_qa_report", "source_text_qa_report.json")
    qa = read_json(qa_path) if qa_path.exists() else {"pages": [], "findings": []}
    qa_pages = {item.get("page"): item for item in qa.get("pages", [])}
    page_findings: dict[int | None, list[dict[str, Any]]] = {}
    global_findings: list[dict[str, Any]] = []
    for finding in qa.get("findings", []):
        page = finding.get("page")
        if page is None:
            global_findings.append(finding)
        else:
            page_findings.setdefault(int(page), []).append(finding)

    tasks: list[dict[str, Any]] = []
    for page in pages:
        page_num = page.get("page")
        page_text = str(page.get("text") or "")
        render = page_render_path(render_dir, page_num)
        render_exists = bool(render and render.exists())
        findings = page_findings.get(page_num, [])
        qa_page = qa_pages.get(page_num, {})
        if "<!-- empty-or-image-only-page -->" in page_text or len(page_text.strip()) < 50:
            status = "empty_or_image_only_needs_visual_check"
        elif findings:
            status = "needs_reconstruction_attention"
        else:
            status = "needs_reconstruction"
        tasks.append(
            {
                "page": page_num,
                "status": status,
                "render": rel(render) if render_exists and render else None,
                "render_exists": render_exists,
                "chars": len(page_text),
                "nonempty_lines": int(qa_page.get("nonempty_lines", len([line for line in page_text.splitlines() if line.strip()]))),
                "findings": findings,
                "excerpt": compact_excerpt(page_text),
            }
        )

    result = {
        "schema": "translator_source_reconstruction_tasks.v1",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "config": rel(config_path),
        "title": str(config.get("scenario_title_en") or config.get("project_key") or "Source Reconstruction"),
        "source_markdown": rel(source),
        "page_render_dir": rel(render_dir),
        "source_text_qa": rel(qa_path) if qa_path.exists() else None,
        "status": "needs_review",
        "action": "rewritten" if packet_json.exists() or packet_md.exists() else "created",
        "counts": {
            "pages": len(tasks),
            "pages_with_render": sum(1 for item in tasks if item["render_exists"]),
            "pages_missing_render": sum(1 for item in tasks if not item["render_exists"]),
            "pages_with_qa_findings": sum(1 for item in tasks if item["findings"]),
            "empty_pages": sum(1 for item in tasks if item["status"] == "empty_or_image_only_needs_visual_check"),
            "global_findings": len(global_findings),
        },
        "global_findings": global_findings,
        "pages": tasks,
        "outputs": {
            "task_packet_json": rel(packet_json),
            "task_packet_md": rel(packet_md),
        },
    }
    write_json(packet_json, result)
    packet_md.parent.mkdir(parents=True, exist_ok=True)
    packet_md.write_text(source_reconstruction_markdown(result), encoding="utf-8", newline="\n")
    return result


def statblock_reconstruction_config(config: dict[str, Any]) -> dict[str, Any]:
    return config.get("statblock_reconstruction", {})


def statblock_profile(config: dict[str, Any]) -> str:
    value = str(statblock_reconstruction_config(config).get("profile") or config.get("project_family") or "generic").lower()
    if value in {"coc", "call_of_cthulhu", "call-of-cthulhu"}:
        return "coc"
    if value in {"dune", "dune_ait", "dune_adventures"}:
        return "dune"
    return "generic"


def statblock_output_path(config: dict[str, Any], key: str, default_name: str) -> Path:
    cfg = statblock_reconstruction_config(config)
    value = cfg.get(key, default_name)
    path = Path(str(value).replace("/", "\\"))
    return path.resolve() if path.is_absolute() else qa_root(config) / path


def statblock_source_path(config: dict[str, Any]) -> Path:
    cfg = statblock_reconstruction_config(config)
    if cfg.get("source_markdown"):
        return root_path(str(cfg["source_markdown"]))
    return source_reconstruction_source_path(config)


def statblock_qa_report_path(config: dict[str, Any]) -> Path:
    cfg = statblock_reconstruction_config(config)
    value = cfg.get("qa_report") or intake_config(config).get("source_text_qa_report") or "source_text_qa_report.json"
    path = Path(str(value).replace("/", "\\"))
    return path.resolve() if path.is_absolute() else qa_root(config) / path


def statblock_like_line_for_profile(line: str, profile: str) -> bool:
    upper = line.upper()
    tokens = [
        token
        for token in STATBLOCK_PROFILE_TOKENS.get(profile, STATBLOCK_PROFILE_TOKENS["generic"])
        if re.search(rf"\b{re.escape(token)}\b", upper)
    ]
    if len(tokens) >= 3:
        return True
    if profile == "coc":
        return stat_like_line(line)
    if profile == "dune":
        return len(tokens) >= 2 and any(
            token in tokens
            for token in ("DUTY", "FAITH", "JUSTICE", "POWER", "TRUTH", "BATTLE", "COMMUNICATE", "DISCIPLINE", "MOVE", "UNDERSTAND")
        )
    return len(tokens) >= 2


def statblock_reconstruction_markdown(result: dict[str, Any]) -> str:
    profile_rules = result["profile_rules"]
    lines = [
        f"# {result.get('title', 'Statblock Reconstruction')} - QA packet",
        "",
        f"- Status: `{result['status']}`",
        f"- Profile: `{result['profile']}` ({profile_rules['label']})",
        f"- Source markdown: `{result['source_markdown']}`",
        f"- Source QA report: `{result.get('source_qa_report') or 'missing'}`",
        f"- Page renders: `{result['page_render_dir']}`",
        f"- Candidate pages: `{result['counts']['candidate_pages']}`",
        "",
        "## Universal Requirements",
        "",
        "- Treat statblocks, cards, and rules-heavy character records as structured data, not prose.",
        "- Rebuild the whole statblock/card from render or source PDF when OCR merges it with surrounding text.",
        "- Keep surrounding prose before/after the block as separate paragraphs.",
        "- Preserve ratings, dice notation, percentages, armor, skills, assets, traits, attacks, and special notes exactly until terminology QA.",
        "- Mark uncertain values as `?` and do not approve source reconstruction until they are visually resolved.",
        "",
        "## Profile Shape",
        "",
    ]
    for item in profile_rules["target_shape"]:
        lines.append(f"- {item}")
    lines.extend(["", "## Expected Fields", "", ", ".join(f"`{field}`" for field in profile_rules["fields"]), ""])
    if result["pages"]:
        lines.extend(["## Candidate Pages", "", "| Page | Render | QA findings | Matched lines | Status |", "|---:|---|---:|---:|---|"])
        for page in result["pages"]:
            lines.append(
                f"| {page['page']} | `{page.get('render') or 'missing'}` | {len(page.get('qa_findings', []))} | {len(page.get('matched_lines', []))} | `{page['status']}` |"
            )
        lines.append("")
        for page in result["pages"]:
            lines.extend(
                [
                    f"## Page {int(page['page']):03d}",
                    "",
                    f"- Status: `{page['status']}`",
                    f"- Render: `{page.get('render') or 'missing'}`",
                    "",
                ]
            )
            if page.get("qa_findings"):
                lines.extend(["### QA Findings", ""])
                for finding in page["qa_findings"]:
                    examples = finding.get("examples") or []
                    extra = f" Examples: {'; '.join(str(example) for example in examples[:3])}" if examples else ""
                    lines.append(f"- `{finding.get('code')}`{extra}")
                lines.append("")
            if page.get("matched_lines"):
                lines.extend(["### Matched Lines", ""])
                for matched in page["matched_lines"][:12]:
                    lines.append(f"- `{matched}`")
                lines.append("")
            lines.extend(
                [
                    "### Reconstruction Notes",
                    "",
                    "- [ ] Rebuild each block as a structured Markdown table/card.",
                    "- [ ] Separate prose from statblock/card content.",
                    "- [ ] Resolve `?` values against render/source PDF.",
                    "",
                ]
            )
    else:
        lines.extend(["## Candidate Pages", "", "No statblock-like pages were detected.", ""])
    return "\n".join(lines).rstrip() + "\n"


def prepare_statblock_reconstruction(
    config_path: Path, *, force: bool = False, requested_pages: list[str] | None = None
) -> dict[str, Any]:
    config = read_json(config_path)
    source = statblock_source_path(config)
    report = statblock_output_path(config, "report", "statblock_reconstruction_report.json")
    packet_md = statblock_output_path(config, "task_packet_md", "statblock_reconstruction_tasks.md")
    if not source.exists():
        raise FileNotFoundError(source)

    profile = statblock_profile(config)
    profile_rules = STATBLOCK_PROFILE_RULES.get(profile, STATBLOCK_PROFILE_RULES["generic"])
    markdown = source.read_text(encoding="utf-8")
    pages = split_raw_text_pages(markdown)
    selection = select_policy_pages(
        config,
        stage="reconstruction",
        page_count=page_count_from_text_pages(pages),
        requested_pages=requested_pages,
    )
    selection_report = page_selection_report(selection)
    declared_page_map = config.get("page_map") is not None
    policy_validation = page_policy.validate_page_map(
        page_count_from_text_pages(pages), config.get("page_map")
    )
    policy_pages = {page["id"]: page for page in policy_validation["pages"]}
    if declared_page_map:
        eligible_pages = [
            page_id
            for page_id in selection_report["effective_pages"]
            if policy_pages[page_id]["type"] == "statblock_card"
        ]
        selection_report["skipped_pages"].extend(
            {"page": page_id, "reason": "not_statblock_card"}
            for page_id in selection_report["effective_pages"]
            if page_id not in eligible_pages
        )
        selection_report["effective_pages"] = eligible_pages
        selection_report["skipped_pages"].sort(key=lambda item: (int(item["page"]), item["reason"]))
    if report.exists() and packet_md.exists() and not force and requested_pages is None:
        result = read_json(report)
        result["action"] = "kept_existing"
        result["page_selection"] = selection_report
        write_json(report, result)
        return result

    effective_numbers = {int(page_id) for page_id in selection_report["effective_pages"]}
    pages = [
        page
        for page in pages
        if page["page"] in effective_numbers or (page["page"] is None and 1 in effective_numbers)
    ]
    qa_path = statblock_qa_report_path(config)
    qa_by_page: dict[int | None, list[dict[str, Any]]] = {}
    if qa_path.exists():
        qa_report = read_json(qa_path)
        for finding in qa_report.get("findings", []):
            qa_by_page.setdefault(finding.get("page"), []).append(finding)
    render_dir = page_render_dir(config)
    candidate_pages: list[dict[str, Any]] = []
    for page in pages:
        page_num = page["page"]
        lines = [line.strip() for line in page["text"].splitlines() if line.strip()]
        matched = [line for line in lines if statblock_like_line_for_profile(line, profile)]
        qa_findings = [item for item in qa_by_page.get(page_num, []) if item.get("code") == "stat_like_lines"]
        if not matched and not qa_findings:
            continue
        render = page_render_path(render_dir, page_num)
        candidate_pages.append(
            {
                "page": page_num,
                "status": "needs_statblock_reconstruction",
                "render": rel(render) if render and render.exists() else None,
                "qa_findings": qa_findings,
                "matched_lines": matched[:20],
                "excerpt": compact_excerpt(page["text"], 900),
            }
        )
    result = {
        "schema": "translator_statblock_reconstruction.v1",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "config": rel(config_path),
        "title": str(config.get("title_en") or config.get("project_key") or "Statblock Reconstruction"),
        "profile": profile,
        "profile_rules": profile_rules,
        "source_markdown": rel(source),
        "source_qa_report": rel(qa_path) if qa_path.exists() else None,
        "page_render_dir": rel(render_dir),
        "status": "needs_review" if candidate_pages else "pass",
        "action": "rewritten" if report.exists() else "created",
        "counts": {
            "pages_scanned": len(pages),
            "candidate_pages": len(candidate_pages),
            "matched_lines": sum(len(page["matched_lines"]) for page in candidate_pages),
            "qa_statblock_pages": sum(1 for page in candidate_pages if page["qa_findings"]),
        },
        "pages": candidate_pages,
        "page_selection": selection_report,
    }
    write_json(report, result)
    packet_md.parent.mkdir(parents=True, exist_ok=True)
    packet_md.write_text(statblock_reconstruction_markdown(result), encoding="utf-8", newline="\n")
    return result


COC_6E_CORE_FIELDS = ("сил", "вын", "тел", "инт", "мощ", "лвк", "нар", "обр")


def statblock_edition_config(config: dict[str, Any]) -> dict[str, Any]:
    return config.get("statblock_edition_conversion", {})


def statblock_edition_report_path(config: dict[str, Any]) -> Path:
    cfg = statblock_edition_config(config)
    value = cfg.get("report", "statblock_edition_conversion_report.json")
    path = Path(str(value).replace("/", "\\"))
    return path.resolve() if path.is_absolute() else qa_root(config) / path


def statblock_edition_markdown_targets(config: dict[str, Any]) -> list[dict[str, Any]]:
    cfg = statblock_edition_config(config)
    configured = cfg.get("markdowns")
    targets: list[dict[str, Any]] = []
    if isinstance(configured, list):
        for index, item in enumerate(configured, start=1):
            if isinstance(item, dict):
                value = item.get("path")
                label = str(item.get("label") or f"markdown_{index}")
            else:
                value = item
                label = f"markdown_{index}"
            if value:
                targets.append({"label": label, "path": root_path(str(value))})
    if not targets:
        ph = production_html_config(config)
        if ph.get("source_markdown"):
            targets.append({"label": "production_html.source_markdown", "path": root_path(str(ph["source_markdown"]))})
    return targets


def markdown_table_cells(line: str) -> list[str]:
    stripped = line.strip()
    if not stripped.startswith("|") or not stripped.endswith("|"):
        return []
    return [cell.strip() for cell in stripped.strip("|").split("|")]


def markdown_table_separator(line: str) -> bool:
    cells = markdown_table_cells(line)
    return bool(cells) and all(re.fullmatch(r":?-{3,}:?", cell.strip()) for cell in cells)


def normalize_stat_field(value: str) -> str:
    value = re.sub(r"\s+", "", value).casefold()
    aliases = {
        "бку": "бку",
        "бку.": "бку",
        "db": "бку",
        "damagebonus": "бку",
        "комплекция": "комплекция",
        "build": "комплекция",
        "ско": "ско",
        "mov": "ско",
        "move": "ско",
        "пм": "пм",
        "mp": "пм",
        "атакзараунд": "атакзараунд",
        "attacksperround": "атакзараунд",
    }
    return aliases.get(value, value)


def simple_int_cell(value: str) -> int | None:
    value = value.strip()
    if re.fullmatch(r"\d+", value):
        return int(value)
    return None


def multi_int_cell(value: str) -> list[int] | None:
    value = value.strip()
    if not re.fullmatch(r"\d+(?:\s*/\s*\d+)+", value):
        single = simple_int_cell(value)
        return [single] if single is not None else None
    return [int(part.strip()) for part in value.split("/")]


def collapse_state_values(values: list[Any]) -> Any:
    if not values:
        return ""
    if all(value == values[0] for value in values):
        return values[0]
    return "/".join(str(value) for value in values)


def coc_build_damage_bonus(str_plus_siz: int) -> tuple[str, int]:
    if str_plus_siz <= 64:
        return "-2", -2
    if str_plus_siz <= 84:
        return "-1", -1
    if str_plus_siz <= 124:
        return "0", 0
    if str_plus_siz <= 164:
        return "+1D4", 1
    if str_plus_siz <= 204:
        return "+1D6", 2
    if str_plus_siz <= 284:
        return "+2D6", 3
    if str_plus_siz <= 364:
        return "+3D6", 4
    if str_plus_siz <= 444:
        return "+4D6", 5
    if str_plus_siz <= 524:
        return "+5D6", 6
    extra = math.ceil((str_plus_siz - 524) / 80)
    return f"+{5 + extra}D6", 6 + extra


def coc_human_mov(strength: int, dexterity: int, size: int) -> int:
    if dexterity < size and strength < size:
        return 7
    if dexterity > size and strength > size:
        return 9
    return 8


def nearest_previous_heading(lines: list[str], line_index: int) -> str | None:
    for index in range(line_index - 1, -1, -1):
        match = re.match(r"^(#{1,6})\s+(.+?)\s*$", lines[index])
        if match:
            return match.group(2).strip()
    return None


def coc_6e_conversion_for_table(headers: list[str], values: list[str]) -> tuple[dict[str, Any] | None, dict[str, Any] | None]:
    normalized_headers = [normalize_stat_field(item) for item in headers]
    index_by_field = {field: index for index, field in enumerate(normalized_headers)}
    if not all(field in index_by_field for field in COC_6E_CORE_FIELDS):
        return None, None
    parsed: dict[str, list[int]] = {}
    complex_values: dict[str, str] = {}
    for field in COC_6E_CORE_FIELDS:
        raw = values[index_by_field[field]] if index_by_field[field] < len(values) else ""
        value = multi_int_cell(raw)
        if value is None:
            complex_values[field] = raw
        else:
            parsed[field] = value
    if complex_values:
        return None, {"code": "complex_6e_characteristic_needs_manual_conversion", "values": complex_values}
    if not all(all(1 <= value <= 20 for value in parsed[field]) for field in COC_6E_CORE_FIELDS):
        return None, None
    state_count = max(len(parsed[field]) for field in COC_6E_CORE_FIELDS)
    incompatible_states = {
        field: parsed[field]
        for field in COC_6E_CORE_FIELDS
        if len(parsed[field]) not in {1, state_count}
    }
    if incompatible_states:
        return None, {"code": "incompatible_6e_multistate_characteristics", "values": incompatible_states}

    def state_value(field: str, state: int) -> int:
        values_for_field = parsed[field]
        return values_for_field[state] if len(values_for_field) > 1 else values_for_field[0]

    converted_core_states: dict[str, list[int]] = {
        field: [state_value(field, state) * 5 for state in range(state_count)]
        for field in COC_6E_CORE_FIELDS
    }
    damage_bonus_values: list[str] = []
    build_values: list[int] = []
    hp_values: list[int] = []
    mp_values: list[int] = []
    mov_values: list[int] = []
    for state in range(state_count):
        strength = converted_core_states["сил"][state]
        constitution = converted_core_states["вын"][state]
        size = converted_core_states["тел"][state]
        power = converted_core_states["мощ"][state]
        dexterity = converted_core_states["лвк"][state]
        damage_bonus, build = coc_build_damage_bonus(strength + size)
        damage_bonus_values.append(damage_bonus)
        build_values.append(build)
        hp_values.append((constitution + size) // 10)
        mp_values.append(power // 5)
        mov_values.append(coc_human_mov(strength, dexterity, size))

    converted_values = list(values)
    for field in COC_6E_CORE_FIELDS:
        converted_values[index_by_field[field]] = str(collapse_state_values(converted_core_states[field]))
    if "пз" in index_by_field and index_by_field["пз"] < len(converted_values):
        converted_values[index_by_field["пз"]] = str(collapse_state_values(hp_values))

    return (
        {
            "converted_values": converted_values,
            "derived": {
                "БКУ": collapse_state_values(damage_bonus_values),
                "Комплекция": collapse_state_values(build_values),
                "СКО": collapse_state_values(mov_values),
                "ПМ": collapse_state_values(mp_values),
                "Атак за раунд": "?" if state_count > 1 else 1,
            },
            "source_values": {field: collapse_state_values(parsed[field]) for field in COC_6E_CORE_FIELDS},
            "converted_core": {field: collapse_state_values(converted_core_states[field]) for field in COC_6E_CORE_FIELDS},
            "computed_hp": collapse_state_values(hp_values),
            "state_count": state_count,
        },
        None,
    )


def markdown_table_row(cells: list[str]) -> str:
    return "| " + " | ".join(cells) + " |"


def statblock_derived_table_lines(derived: dict[str, Any]) -> list[str]:
    headers = ["БКУ", "Комплекция", "СКО", "ПМ", "Атак за раунд"]
    return [
        markdown_table_row(headers),
        "|---|---:|---:|---:|---:|",
        markdown_table_row([str(derived[header]) for header in headers]),
    ]


def find_following_derived_table(lines: list[str], start_index: int) -> tuple[int, int] | None:
    index = start_index
    while index < len(lines) and not lines[index].strip():
        index += 1
    if index + 2 >= len(lines):
        return None
    headers = [normalize_stat_field(cell) for cell in markdown_table_cells(lines[index])]
    if not {"бку", "комплекция", "ско", "пм"}.issubset(set(headers)):
        return None
    if not markdown_table_separator(lines[index + 1]):
        return None
    end = index + 2
    while end + 1 < len(lines) and lines[end + 1].strip().startswith("|"):
        end += 1
    return index, end


def convert_coc_6e_markdown(text: str, *, apply: bool) -> tuple[str, list[dict[str, Any]], list[dict[str, Any]], int]:
    lines = text.splitlines()
    output = list(lines)
    offset = 0
    records: list[dict[str, Any]] = []
    findings: list[dict[str, Any]] = []
    conversions = 0
    index = 0
    while index + 2 < len(lines):
        headers = markdown_table_cells(lines[index])
        if not headers or not markdown_table_separator(lines[index + 1]):
            index += 1
            continue
        values = markdown_table_cells(lines[index + 2])
        conversion, finding = coc_6e_conversion_for_table(headers, values)
        if finding:
            finding.update(
                {
                    "line": index + 1,
                    "heading": nearest_previous_heading(lines, index),
                }
            )
            findings.append(finding)
            index += 3
            continue
        if not conversion:
            index += 1
            continue

        conversions += 1
        heading = nearest_previous_heading(lines, index)
        derived = conversion["derived"]
        record = {
            "heading": heading,
            "line": index + 1,
            "source_values": conversion["source_values"],
            "converted_core": conversion["converted_core"],
            "derived": derived,
            "computed_hp": conversion["computed_hp"],
        }
        records.append(record)
        if apply:
            out_index = index + offset
            output[out_index + 2] = markdown_table_row(conversion["converted_values"])
            replacement = [""] + statblock_derived_table_lines(derived)
            existing = find_following_derived_table(lines, index + 3)
            if existing:
                start, end = existing
                out_start = start + offset
                out_end = end + offset
                output[out_start : out_end + 1] = statblock_derived_table_lines(derived)
                offset += len(statblock_derived_table_lines(derived)) - (end - start + 1)
            else:
                insert_at = index + 3 + offset
                output[insert_at:insert_at] = replacement
                offset += len(replacement)
        index += 3
    trailing_newline = "\n" if text.endswith("\n") else ""
    return "\n".join(output) + trailing_newline, records, findings, conversions


def run_statblock_edition_gate(config_path: Path, *, apply: bool = False, check_only: bool = False) -> dict[str, Any]:
    config = read_json(config_path)
    cfg = statblock_edition_config(config)
    report = statblock_edition_report_path(config)
    source_edition = str(cfg.get("source_edition") or "7e").casefold()
    target_edition = str(cfg.get("target_edition") or "7e").casefold()
    enabled = bool(cfg.get("enabled", source_edition != target_edition))
    findings: list[dict[str, Any]] = []
    warnings: list[dict[str, Any]] = []
    artifacts: list[dict[str, Any]] = []

    if not enabled or source_edition not in {"6e", "6", "sixth", "sixth edition", "6ая", "6ая редакция"} or target_edition not in {"7e", "7", "seventh", "seventh edition", "7ая", "7ая редакция"}:
        result = {
            "schema": "translator_statblock_edition_conversion.v1",
            "generated_at_utc": datetime.now(timezone.utc).isoformat(),
            "config": rel(config_path),
            "status": "pass",
            "mode": "check_only" if check_only else ("apply" if apply else "dry_run"),
            "action": "disabled",
            "artifact_writes": {"qa_report": True, "production_markdown": False},
            "source_edition": source_edition,
            "target_edition": target_edition,
            "counts": {"artifacts": 0, "conversions": 0, "findings": 0, "warnings": 0},
            "findings": [],
            "warnings": [],
            "artifacts": [],
        }
        write_json(report, result)
        return result

    for target in statblock_edition_markdown_targets(config):
        label = str(target["label"])
        path = target["path"]
        if not path.exists():
            findings.append({"code": "missing_statblock_edition_markdown", "label": label, "path": rel(path)})
            artifacts.append({"label": label, "path": rel(path), "exists": False, "conversions": 0, "findings": 1})
            continue
        text = path.read_text(encoding="utf-8")
        converted_text, records, artifact_findings, conversions = convert_coc_6e_markdown(text, apply=apply)
        for finding in artifact_findings:
            findings.append({"artifact": label, "path": rel(path), **finding})
        changed = converted_text != text
        if apply and changed:
            path.write_text(converted_text, encoding="utf-8", newline="\n")
        artifacts.append(
            {
                "label": label,
                "path": rel(path),
                "exists": True,
                "changed": bool(apply and changed),
                "would_change": bool((not apply) and conversions),
                "conversions": conversions,
                "records": records,
                "findings": len(artifact_findings),
            }
        )

    total_conversions = sum(int(item.get("conversions", 0)) for item in artifacts)
    if total_conversions and not apply:
        warnings.append(
            {
                "code": "statblock_edition_conversion_pending",
                "message": "Run with --apply after review to rewrite configured reader Markdown before production.",
            }
        )
    if findings:
        status = "blocked"
    elif total_conversions and not apply:
        status = "needs_apply"
    else:
        status = "pass"
    result = {
        "schema": "translator_statblock_edition_conversion.v1",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "config": rel(config_path),
        "status": status,
        "mode": "check_only" if check_only else ("apply" if apply else "dry_run"),
        "action": "check_only" if check_only else ("applied" if apply else "dry_run"),
        "artifact_writes": {
            "qa_report": True,
            "production_markdown": bool(apply and any(item.get("changed") for item in artifacts)),
        },
        "source_edition": source_edition,
        "target_edition": target_edition,
        "counts": {
            "artifacts": len(artifacts),
            "conversions": total_conversions,
            "findings": len(findings),
            "warnings": len(warnings),
        },
        "artifacts": artifacts,
        "findings": findings,
        "warnings": warnings,
        "approval_state": {
            "statblock_edition_conversion_passed": status == "pass",
            "production_approved": False,
        },
    }
    write_json(report, result)
    return result


PDF_LIGATURE_MOJIBAKE_REPAIRS = {
    "昀툀": "ffl",
    "昀케": "ffi",
    "昀昀": "ff",
    "昀椀": "fi",
    "昀氀": "fl",
}


def repair_pdf_ligature_mojibake(text: str) -> tuple[str, dict[str, int]]:
    counts: dict[str, int] = {}
    repaired = text
    for bad, good in PDF_LIGATURE_MOJIBAKE_REPAIRS.items():
        count = repaired.count(bad)
        if count:
            counts[bad] = count
            repaired = repaired.replace(bad, good)
    return repaired, counts


def normalize_page_text(page_text: str, *, join_hyphenated_lines: bool = False) -> tuple[str, dict[str, Any]]:
    removed_lines: list[str] = []
    kept_lines: list[str] = []
    for line in page_text.splitlines():
        stripped = line.strip()
        if not stripped:
            kept_lines.append("")
            continue
        if spaced_caps_line(stripped):
            removed_lines.append(stripped)
            continue
        if re.fullmatch(r"\d{2,4}", stripped):
            removed_lines.append(stripped)
            continue
        kept_lines.append(line.rstrip())
    normalized = "\n".join(kept_lines).strip()
    dehyphenations = 0
    if join_hyphenated_lines:
        normalized, dehyphenations = HYPHENATED_LINE_BREAK_RE.subn(r"\1\2", normalized)
    normalized, ligature_mojibake_repairs = repair_pdf_ligature_mojibake(normalized)
    normalized = re.sub(r"\n{3,}", "\n\n", normalized).strip()
    return normalized, {
        "removed_lines": removed_lines,
        "removed_line_count": len(removed_lines),
        "dehyphenations": dehyphenations,
        "ligature_mojibake_repairs": ligature_mojibake_repairs,
        "chars": len(normalized),
    }


def normalize_source_text(config_path: Path, *, force: bool = False) -> dict[str, Any]:
    config = read_json(config_path)
    raw_path = root_path(intake_config(config).get("raw_text", f"{config['workbench_root']}/Formatted/Source_Text_Raw_EN_v1.txt"))
    target = root_path(
        intake_config(config).get(
            "normalized_text",
            f"{config['workbench_root']}/Formatted/Source_Text_Normalized_EN_v1.md",
        )
    )
    if not raw_path.exists():
        raise FileNotFoundError(raw_path)
    target_existed = target.exists()
    report_target = intake_report_path(config, "source_text_normalization_report", "source_text_normalization_report.json")
    if target.exists() and not force:
        text = target.read_text(encoding="utf-8")
        digest = sha256_text(text)
        page_count = len(SOURCE_PAGE_RE.findall(text))
        empty_pages = text.count("<!-- empty-or-image-only-page -->")
        counts: dict[str, Any] = {
            "pages": page_count,
            "chars": len(text),
            "removed_lines": None,
            "dehyphenations": None,
            "empty_pages": empty_pages,
            "join_hyphenated_lines": None,
        }
        if report_target.exists():
            previous = read_json(report_target)
            if previous.get("sha256") == digest and isinstance(previous.get("counts"), dict):
                counts.update(previous["counts"])
        result = {
            "schema": "translator_source_text_normalization.v1",
            "generated_at_utc": datetime.now(timezone.utc).isoformat(),
            "config": rel(config_path),
            "raw_text": rel(raw_path),
            "normalized_text": rel(target),
            "status": "pass",
            "action": "kept_existing",
            "counts": counts,
            "sha256": digest,
        }
        write_json(report_target, result)
        return result
    raw_text = raw_path.read_text(encoding="utf-8")
    pages = split_raw_text_pages(raw_text)
    normalize_cfg = config.get("normalize_source_text", {})
    join_hyphenated_lines = bool(normalize_cfg.get("join_hyphenated_lines", False))
    output_parts = [
        f"# {config.get('scenario_title_en', config.get('project_key', 'Source Text'))} - Normalized Source Draft",
        "",
        "<!-- generated-by: translator normalize-source-text -->",
        f"<!-- source: {rel(raw_path)} -->",
        "",
    ]
    page_reports: list[dict[str, Any]] = []
    for page in pages:
        normalized, page_report = normalize_page_text(page["text"], join_hyphenated_lines=join_hyphenated_lines)
        page_number = page["page"]
        output_parts.append(source_page_marker(page_number))
        output_parts.append("")
        if normalized:
            output_parts.append(normalized)
        else:
            output_parts.append("<!-- empty-or-image-only-page -->")
        output_parts.append("")
        page_report.update({"page": page_number, "marker_type": page["marker_type"]})
        page_reports.append(page_report)
    text = "\n".join(output_parts).strip() + "\n"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(text, encoding="utf-8", newline="\n")
    result = {
        "schema": "translator_source_text_normalization.v1",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "config": rel(config_path),
        "raw_text": rel(raw_path),
        "normalized_text": rel(target),
        "status": "needs_review",
        "action": "rewritten" if target_existed else "created",
        "counts": {
            "pages": len(page_reports),
            "chars": len(text),
            "removed_lines": sum(item["removed_line_count"] for item in page_reports),
            "dehyphenations": sum(item["dehyphenations"] for item in page_reports),
            "empty_pages": sum(1 for item in page_reports if item["chars"] == 0),
            "join_hyphenated_lines": join_hyphenated_lines,
        },
        "sha256": sha256_text(text),
        "pages": page_reports,
    }
    write_json(report_target, result)
    return result


def normalize_headings_config(config: dict[str, Any]) -> dict[str, Any]:
    return dict(config.get("normalize_headings") or {})


def normalize_headings_required_gates(config: dict[str, Any]) -> list[str]:
    return list(normalize_headings_config(config).get("required_gates", []))


def normalize_headings_apply_findings(config: dict[str, Any]) -> list[dict[str, Any]]:
    gates = gate_state(config)
    return [
        {"code": "required_gate_not_true", "gate": gate, "message": f"Required gate is not true: {gate}"}
        for gate in normalize_headings_required_gates(config)
        if gates.get(gate) is not True
    ]


def normalize_headings_report_path(config: dict[str, Any]) -> Path:
    return config_report_path(config, "normalize_headings", "heading_normalization_report.json")


def normalize_headings_source_path(config: dict[str, Any]) -> Path:
    cfg = normalize_headings_config(config)
    if cfg.get("source_markdown"):
        return root_path(str(cfg["source_markdown"]))
    outputs = config.get("production_outputs", {})
    if outputs.get("keeper_markdown"):
        return root_path(str(outputs["keeper_markdown"]))
    return production_html_source_path(config)


def normalize_heading_title(title: str, rules: dict[str, Any]) -> str:
    result = title.strip() if rules.get("trim_heading_whitespace", True) else title
    if rules.get("collapse_repeated_spaces", True):
        result = re.sub(r"\s+", " ", result)
    for item in rules.get("title_replacements", []):
        if not isinstance(item, dict):
            continue
        source = str(item.get("from") or "")
        target = str(item.get("to") or "")
        if not source:
            continue
        if item.get("regex"):
            result = re.sub(source, target, result)
        elif result == source:
            result = target
    return result


def remove_heading_title(title: str, rules: dict[str, Any]) -> bool:
    normalized = title.strip()
    if normalized in {str(item).strip() for item in rules.get("remove_titles", [])}:
        return True
    for pattern in rules.get("remove_patterns", []):
        if re.search(str(pattern), normalized):
            return True
    return False


def normalized_heading_level(title: str, current_level: int, rules: dict[str, Any]) -> int:
    level = current_level
    for item in rules.get("level_overrides", []):
        if not isinstance(item, dict):
            continue
        new_level = int(item.get("level", level))
        matched = False
        if item.get("regex"):
            matched = bool(re.search(str(item.get("match") or ""), title))
        else:
            matched = title == str(item.get("title") or item.get("match") or "").strip()
        if matched:
            level = new_level
    max_level = int(rules.get("max_heading_level", 6))
    return max(1, min(max_level, min(6, level)))


def normalize_markdown_heading_lines(text: str, rules: dict[str, Any]) -> tuple[str, list[dict[str, Any]], list[dict[str, Any]]]:
    changes: list[dict[str, Any]] = []
    findings: list[dict[str, Any]] = []
    output_lines: list[str] = []
    heading_re = re.compile(r"^(?P<hashes>#{1,6})(?P<space>\s*)(?P<title>.*?)(?P<trailing>\s+#+\s*)?$")
    for line_no, line in enumerate(text.splitlines(), start=1):
        match = heading_re.match(line)
        if not match:
            output_lines.append(line)
            continue
        raw_title = match.group("title")
        level = len(match.group("hashes"))
        if rules.get("strip_closing_hashes", True):
            raw_title = re.sub(r"\s+#+\s*$", "", raw_title)
        title = normalize_heading_title(raw_title, rules)
        if not title:
            findings.append({"code": "empty_heading_after_normalization", "line": line_no, "original": line})
            output_lines.append(line)
            continue
        if remove_heading_title(title, rules):
            changes.append({"line": line_no, "action": "removed", "from": line, "title": title})
            continue
        new_level = normalized_heading_level(title, level, rules)
        new_line = f"{'#' * new_level} {title}" if rules.get("fix_markdown_heading_spacing", True) else f"{'#' * new_level}{match.group('space')}{title}"
        if new_line != line:
            changes.append(
                {
                    "line": line_no,
                    "action": "rewritten",
                    "from": line,
                    "to": new_line,
                    "old_level": level,
                    "new_level": new_level,
                    "old_title": raw_title.strip(),
                    "new_title": title,
                }
            )
        output_lines.append(new_line)
    if rules.get("update_markdown_heading_links", True):
        replacements: list[tuple[str, str]] = []
        for item in rules.get("title_replacements", []):
            if not isinstance(item, dict) or item.get("regex"):
                continue
            source = str(item.get("from") or "").strip()
            target = str(item.get("to") or "").strip()
            if source and target and source != target:
                replacements.append((source, target))
        for index, line in enumerate(output_lines):
            new_line = line
            for source, target in replacements:
                new_line = new_line.replace(f"[{source}](#{slugify(source)})", f"[{target}](#{slugify(target)})")
            if new_line != line:
                output_lines[index] = new_line
                changes.append({"line": index + 1, "action": "markdown_link_rewritten", "from": line, "to": new_line})
    suffix = "\n" if text.endswith("\n") else ""
    return "\n".join(output_lines) + suffix, changes, findings


def normalize_headings(config_path: Path, *, apply: bool = False) -> dict[str, Any]:
    config = read_json(config_path)
    source = normalize_headings_source_path(config)
    report = normalize_headings_report_path(config)
    if not source.exists():
        raise FileNotFoundError(source)
    cfg = normalize_headings_config(config)
    rules = dict(cfg.get("rules") or {})
    text = source.read_text(encoding="utf-8")
    normalized, changes, findings = normalize_markdown_heading_lines(text, rules)
    gate_findings = normalize_headings_apply_findings(config) if apply else []
    findings.extend(gate_findings)
    action = "check_only"
    if apply and gate_findings:
        action = "not_applied"
    elif apply and normalized != text:
        source.write_text(normalized, encoding="utf-8", newline="\n")
        action = "rewritten"
    elif apply:
        action = "kept_existing"
    status = "blocked" if gate_findings else ("pass" if not findings else "needs_review")
    result = {
        "schema": "translator_heading_normalization.v1",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "config": rel(config_path),
        "source_markdown": rel(source),
        "report": rel(report),
        "status": status,
        "mode": "apply" if apply else "check_only",
        "action": action,
        "required_gates": normalize_headings_required_gates(config),
        "artifact_writes": {
            "qa_report": True,
            "production_markdown": bool(apply and not gate_findings and normalized != text),
        },
        "counts": {
            "headings_checked": len(re.findall(r"^#{1,6}\s*", text, re.M)),
            "changes": len(changes),
            "findings": len(findings),
        },
        "sha256_before": sha256_text(text),
        "sha256_after": sha256_text(normalized),
        "changes": changes,
        "findings": findings,
        "approval_state": {
            "heading_normalization_applied": bool(not findings and (apply or not changes)),
        },
    }
    write_json(report, result)
    return result


def extract_images(
    config_path: Path, *, force: bool = False, requested_pages: list[str] | None = None
) -> dict[str, Any]:
    import fitz  # PyMuPDF

    config = read_json(config_path)
    source = root_path(str(config["source_pdf"]))
    image_dir = root_path(intake_config(config).get("embedded_images", f"{config['workbench_root']}/Images/PDF_Extracted_All"))
    by_xref: dict[int, dict[str, Any]] = {}
    page_refs: list[dict[str, Any]] = []
    written: list[str] = []
    existing: list[str] = []

    with fitz.open(source) as doc:
        page_count = len(doc)
        selection = select_policy_pages(
            config, stage="render", page_count=page_count, requested_pages=requested_pages
        )
        selection_report = page_selection_report(selection)
        image_dir.mkdir(parents=True, exist_ok=True)
        for page_id in selection_report["effective_pages"]:
            page_index = int(page_id)
            page = doc.load_page(page_index - 1)
            for image_index, image_info in enumerate(page.get_images(full=True), start=1):
                xref = int(image_info[0])
                width = int(image_info[2])
                height = int(image_info[3])
                colorspace = image_info[5]
                page_ref = {
                    "page": page_index,
                    "page_image_index": image_index,
                    "xref": xref,
                    "width": width,
                    "height": height,
                    "colorspace": colorspace,
                }
                page_refs.append(page_ref)
                if xref in by_xref:
                    by_xref[xref]["page_refs"].append(page_ref)
                    continue
                extracted = doc.extract_image(xref)
                ext = str(extracted.get("ext") or "bin").lower()
                image_bytes = extracted["image"]
                digest = hashlib.sha256(image_bytes).hexdigest()
                target = image_dir / f"pdf_image_xref_{xref:05d}_{width}x{height}_{digest[:10]}.{ext}"
                if target.exists() and not force:
                    existing.append(rel(target))
                else:
                    target.write_bytes(image_bytes)
                    written.append(rel(target))
                by_xref[xref] = {
                    "xref": xref,
                    "path": rel(target),
                    "ext": ext,
                    "width": width,
                    "height": height,
                    "colorspace": colorspace,
                    "bytes": len(image_bytes),
                    "sha256": digest,
                    "page_refs": [page_ref],
                }
    images = sorted(by_xref.values(), key=lambda item: item["xref"])
    result = {
        "schema": "translator_embedded_image_extraction.v1",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "config": rel(config_path),
        "source_pdf": rel(source),
        "image_dir": rel(image_dir),
        "page_count": page_count,
        "page_selection": selection_report,
        "status": "pass",
        "counts": {
            "unique_images": len(images),
            "page_image_refs": len(page_refs),
            "written": len(written),
            "existing": len(existing),
        },
        "written": written,
        "existing": existing,
        "images": images,
    }
    write_json(intake_report_path(config, "image_extraction_report", "image_extraction_report.json"), result)
    write_json(intake_report_path(config, "image_inventory", "image_inventory.json"), result)
    return result


def image_inventory_path(config: dict[str, Any]) -> Path:
    return intake_report_path(config, "image_inventory", "image_inventory.json")


def image_visual_stats(path: Path) -> dict[str, Any]:
    with Image.open(path) as image:
        rgba = image.convert("RGBA")
        rgba.thumbnail((96, 96), Image.Resampling.LANCZOS)
        gray = rgba.convert("L")
        histogram = gray.histogram()
        width, height = gray.size
        gray_pixels = list(gray.get_flattened_data())
        alpha_pixels = list(rgba.getchannel("A").get_flattened_data())
    pixel_count = sum(histogram)
    if not pixel_count:
        return {"mean_luma": 0, "dark_ratio": 0, "light_ratio": 0, "foreground_ratio": 0, "center_foreground_ratio": 0, "alpha_coverage_ratio": 0}

    background_luma = max(range(256), key=histogram.__getitem__)
    foreground = [
        alpha >= 16 and abs(luma - background_luma) >= 20
        for luma, alpha in zip(gray_pixels, alpha_pixels)
    ]
    center_x0, center_x1 = width // 4, max(width // 4 + 1, width * 3 // 4)
    center_y0, center_y1 = height // 4, max(height // 4 + 1, height * 3 // 4)
    center_indices = [
        y * width + x
        for y in range(center_y0, min(center_y1, height))
        for x in range(center_x0, min(center_x1, width))
    ]
    foreground_count = sum(foreground)
    center_foreground_count = sum(foreground[index] for index in center_indices)
    return {
        "mean_luma": round(sum(value * count for value, count in enumerate(histogram)) / pixel_count, 2),
        "dark_ratio": round(sum(histogram[:17]) / pixel_count, 4),
        "light_ratio": round(sum(histogram[240:]) / pixel_count, 4),
        "background_luma": background_luma,
        "foreground_ratio": round(foreground_count / pixel_count, 4),
        "center_foreground_ratio": round(center_foreground_count / max(len(center_indices), 1), 4),
        "alpha_coverage_ratio": round(sum(alpha >= 16 for alpha in alpha_pixels) / pixel_count, 4),
    }


def empty_frame_or_mask_reason(stats: dict[str, Any]) -> str | None:
    """Identify technical layers that cannot carry map/handout content."""

    alpha_coverage = float(stats.get("alpha_coverage_ratio", 1.0))
    foreground = float(stats.get("foreground_ratio", 1.0))
    center_foreground = float(stats.get("center_foreground_ratio", 1.0))
    if alpha_coverage <= 0.12:
        return "sparse_transparency_mask"
    if foreground <= 0.15 and center_foreground <= 0.015:
        return "near_empty_frame_or_mask"
    return None


def classify_image_candidate(image: dict[str, Any], page_count: int) -> dict[str, Any]:
    width = int(image["width"])
    height = int(image["height"])
    pages = sorted({int(ref["page"]) for ref in image.get("page_refs", [])})
    page_use_count = len(pages)
    area = width * height
    aspect = max(width / max(height, 1), height / max(width, 1))
    source_path = root_path(image["path"])
    visual_stats = image_visual_stats(source_path) if source_path.exists() else {}
    reasons: list[str] = []
    suggested_role = "needs_review"
    decision_state = "needs_review"

    empty_layer_reason = empty_frame_or_mask_reason(visual_stats) if visual_stats else None
    if empty_layer_reason:
        suggested_role = "decoration"
        decision_state = "auto_suggested"
        reasons.append(empty_layer_reason)
    elif page_use_count >= max(3, page_count // 2):
        suggested_role = "decoration"
        decision_state = "auto_suggested"
        reasons.append("reused_on_many_pages")
    elif min(width, height) <= 16 and max(width, height) >= 1000:
        suggested_role = "decoration"
        decision_state = "auto_suggested"
        reasons.append("very_thin_rule_or_separator")
    elif aspect >= 8:
        suggested_role = "decoration"
        decision_state = "auto_suggested"
        reasons.append("extreme_aspect_ratio")
    elif area < 50_000:
        suggested_role = "decoration"
        decision_state = "auto_suggested"
        reasons.append("small_asset")
    elif visual_stats.get("dark_ratio", 0) >= 0.88:
        suggested_role = "decoration"
        decision_state = "auto_suggested"
        reasons.append("mostly_dark_frame_or_mask")
    elif page_use_count == 1 and area >= 750_000:
        suggested_role = "content_image_candidate"
        reasons.append("large_single_page_image")
    elif page_use_count == 1 and area >= 150_000:
        suggested_role = "spot_art_or_handout_candidate"
        reasons.append("medium_single_page_image")

    if not reasons:
        reasons.append("no_safe_auto_classification")

    return {
        "xref": image["xref"],
        "source_path": image["path"],
        "suggested_role": suggested_role,
        "decision_state": decision_state,
        "review_required": decision_state != "auto_suggested" or suggested_role != "decoration",
        "width": width,
        "height": height,
        "area": area,
        "ext": image["ext"],
        "bytes": image["bytes"],
        "sha256": image["sha256"],
        "visual_stats": visual_stats,
        "pages": pages,
        "page_use_count": page_use_count,
        "reasons": reasons,
        "target_role": None,
        "target_path": None,
        "review_notes": "",
    }


def image_classification_markdown(result: dict[str, Any]) -> str:
    lines = [
        "# Image Classification Review",
        "",
        f"Config: `{result['config']}`",
        f"Status: `{result['status']}`",
        "",
        "| XRef | Suggested role | State | Pages | Size | File | Reasons |",
        "|---|---|---|---|---|---|---|",
    ]
    for item in result["candidates"]:
        pages = ", ".join(str(page) for page in item["pages"])
        reasons = ", ".join(item["reasons"])
        lines.append(
            "| {xref} | {role} | {state} | {pages} | {width}x{height} | `{file}` | {reasons} |".format(
                xref=item["xref"],
                role=item["suggested_role"],
                state=item["decision_state"],
                pages=pages,
                width=item["width"],
                height=item["height"],
                file=Path(item["source_path"]).name,
                reasons=reasons,
            )
        )
    lines.extend(
        [
            "",
            "## Review Rules",
            "",
            "- `decoration`: repeated backgrounds, separators, borders, or layout fragments; do not move to public `Images` unless explicitly needed.",
            "- `content_image_candidate`: likely source image, handout, NPC, map, diagram, floorplan, or atmosphere candidate; inspect visually before assigning a target.",
            "- `spot_art_or_handout_candidate`: smaller content candidate; inspect visually before assigning a target.",
            "- Fill `target_role`, `target_path`, and `review_notes` in JSON or transfer approved items into the scenario image manifests.",
            "",
        ]
    )
    return "\n".join(lines)


def classify_images(config_path: Path) -> dict[str, Any]:
    config = read_json(config_path)
    inventory_path = image_inventory_path(config)
    if not inventory_path.exists():
        raise FileNotFoundError(f"Run extract-images first: {inventory_path}")
    inventory = read_json(inventory_path)
    page_count = int(inventory.get("page_count") or 0)
    candidates = [classify_image_candidate(image, page_count) for image in inventory.get("images", [])]
    counts: dict[str, int] = {}
    for item in candidates:
        counts[item["suggested_role"]] = counts.get(item["suggested_role"], 0) + 1
    result = {
        "schema": "translator_image_classification.v1",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "config": rel(config_path),
        "inventory": rel(inventory_path),
        "status": "needs_review" if any(item["review_required"] for item in candidates) else "pass",
        "counts": {
            "candidates": len(candidates),
            "review_required": sum(1 for item in candidates if item["review_required"]),
            "auto_suggested_decoration": sum(
                1 for item in candidates
                if item["decision_state"] == "auto_suggested" and item["suggested_role"] == "decoration"
            ),
            "by_suggested_role": counts,
        },
        "candidates": candidates,
    }
    json_path = intake_report_path(config, "image_classification", "image_classification.json")
    write_json(json_path, result)
    md_path = intake_report_path(config, "image_classification_review", "image_classification_review.md")
    md_path.parent.mkdir(parents=True, exist_ok=True)
    md_path.write_text(image_classification_markdown(result), encoding="utf-8", newline="\n")
    return result


def classification_path(config: dict[str, Any]) -> Path:
    return intake_report_path(config, "image_classification", "image_classification.json")


def contact_sheet_config(config: dict[str, Any]) -> dict[str, Any]:
    return config.get("contact_sheet", {})


def load_default_font(size: int) -> ImageFont.ImageFont:
    for font_name in ("arial.ttf", "segoeui.ttf", "DejaVuSans.ttf"):
        try:
            return ImageFont.truetype(font_name, size)
        except OSError:
            continue
    return ImageFont.load_default()


def draw_wrapped_text(draw: ImageDraw.ImageDraw, xy: tuple[int, int], text: str, font: ImageFont.ImageFont, fill: str, max_width: int, line_gap: int = 4) -> int:
    x, y = xy
    words = text.split()
    lines: list[str] = []
    current = ""
    for word in words:
        candidate = word if not current else f"{current} {word}"
        bbox = draw.textbbox((x, y), candidate, font=font)
        if bbox[2] - bbox[0] <= max_width or not current:
            current = candidate
        else:
            lines.append(current)
            current = word
    if current:
        lines.append(current)
    line_height = draw.textbbox((x, y), "Ag", font=font)[3] - draw.textbbox((x, y), "Ag", font=font)[1] + line_gap
    for line in lines:
        draw.text((x, y), line, font=font, fill=fill)
        y += line_height
    return y


def fit_image(image: Image.Image, box: tuple[int, int]) -> Image.Image:
    fitted = image.copy()
    fitted.thumbnail(box, Image.Resampling.LANCZOS)
    return fitted


def compact_pages(pages: list[int]) -> str:
    if not pages:
        return "-"
    ranges: list[str] = []
    start = prev = pages[0]
    for page in pages[1:]:
        if page == prev + 1:
            prev = page
            continue
        ranges.append(str(start) if start == prev else f"{start}-{prev}")
        start = prev = page
    ranges.append(str(start) if start == prev else f"{start}-{prev}")
    return ",".join(ranges)


def make_contact_sheet(config_path: Path) -> dict[str, Any]:
    config = read_json(config_path)
    class_path = classification_path(config)
    if not class_path.exists():
        raise FileNotFoundError(f"Run classify-images first: {class_path}")
    classification = read_json(class_path)
    sheet_cfg = contact_sheet_config(config)
    columns = int(sheet_cfg.get("columns", 4))
    thumb_w = int(sheet_cfg.get("thumb_width", 260))
    thumb_h = int(sheet_cfg.get("thumb_height", 190))
    label_h = int(sheet_cfg.get("label_height", 122))
    margin = int(sheet_cfg.get("margin", 24))
    gap = int(sheet_cfg.get("gap", 18))
    title_h = 72
    candidates = classification.get("candidates", [])
    rows = (len(candidates) + columns - 1) // columns
    cell_w = thumb_w + 24
    cell_h = thumb_h + label_h
    width = margin * 2 + columns * cell_w + (columns - 1) * gap
    height = margin * 2 + title_h + rows * cell_h + max(rows - 1, 0) * gap
    sheet = Image.new("RGB", (width, height), "#f8f1e6")
    draw = ImageDraw.Draw(sheet)
    title_font = load_default_font(22)
    label_font = load_default_font(14)
    small_font = load_default_font(12)
    draw.text((margin, margin), f"{config.get('scenario_title_en', config.get('project_key'))} - image contact sheet", font=title_font, fill="#20140f")
    draw.text((margin, margin + 34), f"{len(candidates)} candidates from {rel(class_path)}", font=small_font, fill="#5b5148")

    missing: list[str] = []
    for index, item in enumerate(candidates):
        row, col = divmod(index, columns)
        x = margin + col * (cell_w + gap)
        y = margin + title_h + row * (cell_h + gap)
        draw.rounded_rectangle((x, y, x + cell_w, y + cell_h), radius=8, outline="#b9aa96", fill="#fffaf1")
        image_path = root_path(item["source_path"])
        thumb_area = (x + 12, y + 12, x + 12 + thumb_w, y + 12 + thumb_h)
        if image_path.exists():
            with Image.open(image_path) as image:
                thumb = fit_image(image.convert("RGB"), (thumb_w, thumb_h))
            tx = thumb_area[0] + (thumb_w - thumb.width) // 2
            ty = thumb_area[1] + (thumb_h - thumb.height) // 2
            sheet.paste(thumb, (tx, ty))
        else:
            missing.append(item["source_path"])
            draw.rectangle(thumb_area, outline="#8a2d2d", fill="#ead4d4")
            draw.text((thumb_area[0] + 8, thumb_area[1] + 8), "missing image", font=label_font, fill="#8a2d2d")
        label_y = y + 12 + thumb_h + 10
        pages = compact_pages([int(page) for page in item.get("pages", [])])
        header = f"xref {item['xref']} | p.{pages} | {item['width']}x{item['height']}"
        draw.text((x + 12, label_y), header, font=label_font, fill="#20140f")
        label_y += 22
        role_color = "#8a2d2d" if item.get("review_required") else "#2f6337"
        draw_wrapped_text(draw, (x + 12, label_y), str(item["suggested_role"]), label_font, role_color, thumb_w)
        label_y += 38
        reasons = ", ".join(item.get("reasons", []))
        draw_wrapped_text(draw, (x + 12, label_y), reasons, small_font, "#5b5148", thumb_w)

    target = intake_report_path(config, "image_contact_sheet", "image_contact_sheet.png")
    target.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(target, format="PNG")
    result = {
        "schema": "translator_image_contact_sheet.v1",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "config": rel(config_path),
        "classification": rel(class_path),
        "contact_sheet": rel(target),
        "status": "pass" if not missing else "fail",
        "counts": {
            "candidates": len(candidates),
            "missing_images": len(missing),
            "columns": columns,
            "rows": rows,
        },
        "missing": missing,
    }
    write_json(intake_report_path(config, "image_contact_sheet_report", "image_contact_sheet_report.json"), result)
    return result


def image_approval_markdown(result: dict[str, Any]) -> str:
    lines = [
        "# Image Role Approval",
        "",
        f"Config: `{result['config']}`",
        f"Contact sheet: `{result['contact_sheet']}`",
        "",
        "Allowed roles: `source_image`, `handout`, `npc`, `atmospheric`, `decoration`, `reject`.",
        "",
        "| XRef | Pages | Suggested | Decision | Target filename | Source file | Notes |",
        "|---|---|---|---|---|---|---|",
    ]
    for item in result["items"]:
        pages = compact_pages([int(page) for page in item.get("pages", [])])
        source_name = Path(item["source_path"]).name
        lines.append(
            "| {xref} | {pages} | {suggested} | {decision} | `{target}` | `{source}` | {notes} |".format(
                xref=item["xref"],
                pages=pages,
                suggested=item["suggested_role"],
                decision=item["decision_state"],
                target=item["target_filename"] or "",
                source=source_name,
                notes=item["review_notes"] or "",
            )
        )
    lines.extend(
        [
            "",
            "## How To Approve",
            "",
            "1. Open the contact sheet and inspect each `pending` row.",
            "2. In JSON, set `decision_state` to `approved` or `rejected`.",
            "3. For `approved`, set `target_role` and `target_filename`.",
            "4. Keep source extraction files in `Working`; later apply/copy only approved runtime assets into public `Images/*`.",
            "",
        ]
    )
    return "\n".join(lines)


def prepare_image_approval(config_path: Path) -> dict[str, Any]:
    config = read_json(config_path)
    class_path = classification_path(config)
    if not class_path.exists():
        raise FileNotFoundError(f"Run classify-images first: {class_path}")
    classification = read_json(class_path)
    contact_sheet = intake_report_path(config, "image_contact_sheet", "image_contact_sheet.png")
    allowed_roles = IMAGE_APPROVAL_ROLES
    items: list[dict[str, Any]] = []
    for candidate in classification.get("candidates", []):
        if not candidate.get("review_required"):
            continue
        items.append(
            {
                "xref": candidate["xref"],
                "source_path": candidate["source_path"],
                "pages": candidate.get("pages", []),
                "suggested_role": candidate["suggested_role"],
                "decision_state": "pending",
                "allowed_roles": allowed_roles,
                "target_role": None,
                "target_filename": None,
                "target_path": None,
                "review_notes": "",
                "width": candidate["width"],
                "height": candidate["height"],
                "sha256": candidate["sha256"],
            }
        )
    result = {
        "schema": "translator_image_role_approval.v1",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "config": rel(config_path),
        "classification": rel(class_path),
        "contact_sheet": rel(contact_sheet),
        "status": "pending" if items else "pass",
        "allowed_roles": allowed_roles,
        "counts": {
            "pending": len(items),
            "approved": 0,
            "rejected": 0,
        },
        "items": items,
    }
    json_path = intake_report_path(config, "image_role_approval", "image_role_approval.json")
    write_json(json_path, result)
    md_path = intake_report_path(config, "image_role_approval_review", "image_role_approval_review.md")
    md_path.parent.mkdir(parents=True, exist_ok=True)
    md_path.write_text(image_approval_markdown(result), encoding="utf-8", newline="\n")
    return result


def image_role_approval_path(config: dict[str, Any]) -> Path:
    return intake_report_path(config, "image_role_approval", "image_role_approval.json")


def target_dir_for_image_role(config: dict[str, Any], role: str) -> Path:
    images_root = root_path(config["production_outputs"]["images"])
    mapping = {
        "source_image": images_root / "Source_Images",
        "map": images_root / "Maps",
        "diagram": images_root / "Diagrams",
        "floorplan": images_root / "Maps",
        "handout": images_root / "Handouts",
        "npc": images_root / "NPC",
        "atmospheric": images_root / "Atmospheric",
    }
    if role not in mapping:
        raise ValueError(f"Role {role!r} does not map to a public image directory")
    return mapping[role]


def safe_filename(value: str) -> str:
    name = Path(value).name
    if not name or name != value or any(sep in value for sep in ("/", "\\")):
        raise ValueError(f"Unsafe target filename: {value!r}")
    return name


def apply_image_approval(config_path: Path, *, apply: bool = False) -> dict[str, Any]:
    config = read_json(config_path)
    approval_path = image_role_approval_path(config)
    if not approval_path.exists():
        raise FileNotFoundError(f"Run prepare-image-approval first: {approval_path}")
    approval = read_json(approval_path)
    applied: list[dict[str, Any]] = []
    skipped: list[dict[str, Any]] = []
    findings: list[dict[str, Any]] = []
    allowed_roles = set(approval.get("allowed_roles", []))
    copy_roles = IMAGE_COPY_ROLES

    for item in approval.get("items", []):
        state = item.get("decision_state")
        if state == "pending":
            skipped.append({"xref": item.get("xref"), "reason": "pending"})
            continue
        if state == "rejected":
            skipped.append({"xref": item.get("xref"), "reason": "rejected"})
            continue
        if state != "approved":
            findings.append({"xref": item.get("xref"), "code": "invalid_decision_state", "value": state})
            continue
        role = item.get("target_role")
        if role not in allowed_roles:
            findings.append({"xref": item.get("xref"), "code": "invalid_target_role", "value": role})
            continue
        if role in {"decoration", "reject"}:
            skipped.append({"xref": item.get("xref"), "reason": role})
            continue
        if role not in copy_roles:
            findings.append({"xref": item.get("xref"), "code": "unmapped_target_role", "value": role})
            continue
        target_filename = item.get("target_filename")
        if not target_filename:
            findings.append({"xref": item.get("xref"), "code": "missing_target_filename"})
            continue
        try:
            filename = safe_filename(str(target_filename))
        except ValueError as exc:
            findings.append({"xref": item.get("xref"), "code": "unsafe_target_filename", "message": str(exc)})
            continue
        source = root_path(str(item["source_path"]))
        if not source.exists():
            findings.append({"xref": item.get("xref"), "code": "missing_source", "source_path": item["source_path"]})
            continue
        if role in CONTENT_SIGNAL_ROLES:
            visual_stats = image_visual_stats(source)
            empty_reason = empty_frame_or_mask_reason(visual_stats)
            if empty_reason:
                findings.append(
                    {
                        "xref": item.get("xref"),
                        "code": "empty_frame_or_mask_asset",
                        "target_role": role,
                        "reason": empty_reason,
                        "visual_stats": visual_stats,
                    }
                )
                continue
        target = target_dir_for_image_role(config, str(role)) / filename
        record = {
            "xref": item.get("xref"),
            "source_path": rel(source),
            "target_role": role,
            "target_path": rel(target),
            "source_sha256": sha256_file(source),
            "action": "would_copy" if not apply else "copied",
        }
        if apply:
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, target)
            record["target_sha256"] = sha256_file(target)
        applied.append(record)

    result = {
        "schema": "translator_apply_image_approval.v1",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "config": rel(config_path),
        "approval": rel(approval_path),
        "mode": "apply" if apply else "check_only",
        "status": "fail" if findings else ("pending" if any(item["reason"] == "pending" for item in skipped) else "pass"),
        "counts": {
            "applied_or_would_apply": len(applied),
            "skipped": len(skipped),
            "findings": len(findings),
        },
        "applied": applied,
        "skipped": skipped,
        "findings": findings,
    }
    write_json(intake_report_path(config, "apply_image_approval_report", "apply_image_approval_report.json"), result)
    return result


def art_integration_config(config: dict[str, Any]) -> dict[str, Any]:
    return config.get("art_integration", {})


def art_integration_report_path(config: dict[str, Any]) -> Path:
    art = art_integration_config(config)
    value = art.get("report", "art_integration_report.json")
    path = Path(str(value).replace("/", "\\"))
    return path.resolve() if path.is_absolute() else qa_root(config) / path


def art_placement_manifest_path(config: dict[str, Any]) -> Path | None:
    """Return the optional canonical visual-art placement manifest path."""

    value = art_integration_config(config).get("placement_manifest")
    if not value:
        return None
    path = Path(str(value).replace("/", "\\"))
    return path.resolve() if path.is_absolute() else qa_root(config) / path


def package_has_visual_art_contract(config: dict[str, Any]) -> bool:
    art = art_integration_config(config)
    return bool(art.get("placement_manifest") or art.get("preserved_page_art"))


def canonical_art_placement_findings(config: dict[str, Any]) -> list[dict[str, Any]]:
    """Validate selected visual placements before a release can use them."""

    manifest_path = art_placement_manifest_path(config)
    if manifest_path is None:
        if package_has_visual_art_contract(config):
            return [{"code": "missing_art_placement_manifest", "path": None}]
        return []
    if not manifest_path.exists():
        return [{"code": "missing_art_placement_manifest", "path": rel(manifest_path)}]
    try:
        manifest = read_json(manifest_path)
    except Exception as exc:
        return [{"code": "unreadable_art_placement_manifest", "path": rel(manifest_path), "message": str(exc)}]
    placements = manifest.get("placements")
    if not isinstance(placements, list) or not placements:
        return [{"code": "art_placement_manifest_empty", "path": rel(manifest_path)}]

    findings: list[dict[str, Any]] = []
    selected_states = {"approved", "accepted", "selected"}
    crop_required_roles = {"source_image", "map", "floorplan"}
    for index, item in enumerate(placements, start=1):
        if not isinstance(item, dict):
            findings.append({"code": "art_placement_not_object", "index": index})
            continue
        decision = str(item.get("decision_state") or "").casefold()
        if decision not in selected_states:
            continue
        missing = [
            field
            for field in ("asset_id", "runtime_filename", "semantic_role", "source_page", "heading_id", "insertion_rule")
            if not item.get(field)
        ]
        if missing:
            findings.append({"code": "selected_art_placement_missing_fields", "index": index, "asset_id": item.get("asset_id"), "fields": missing})
            continue
        source_kind = str(item.get("source_kind") or "")
        role = str(item.get("semantic_role") or "")
        if source_kind == "extracted_asset":
            if item.get("source_xref") is None:
                findings.append({"code": "selected_extracted_art_missing_source_xref", "index": index, "asset_id": item.get("asset_id")})
            if not item.get("source_asset_sha256"):
                findings.append({"code": "selected_extracted_art_missing_source_hash", "index": index, "asset_id": item.get("asset_id")})
            continue
        if item.get("allow_full_page_art") is True:
            if not item.get("full_page_review_reason"):
                findings.append({"code": "full_page_art_missing_review_reason", "index": index, "asset_id": item.get("asset_id")})
            if str(item.get("visual_review_status") or "") not in {"approved", "approved_clean", "approved_full_page"}:
                findings.append(
                    {
                        "code": "full_page_art_not_reviewed",
                        "index": index,
                        "asset_id": item.get("asset_id"),
                        "status": item.get("visual_review_status"),
                    }
                )
        elif role in crop_required_roles and not item.get("crop_box"):
            findings.append({"code": "selected_art_missing_crop_box", "index": index, "asset_id": item.get("asset_id"), "role": role})
        elif item.get("crop_box") is not None:
            crop_box = item.get("crop_box")
            try:
                crop = [int(value) for value in crop_box]
            except (TypeError, ValueError):
                crop = []
            if len(crop) != 4 or crop[0] >= crop[2] or crop[1] >= crop[3]:
                findings.append({"code": "selected_art_invalid_crop_box", "index": index, "asset_id": item.get("asset_id"), "crop_box": crop_box})
    return findings


def art_placement_draft_report_path(config: dict[str, Any]) -> Path:
    value = art_integration_config(config).get("placement_manifest_report", "art_placement_manifest_report.json")
    path = Path(str(value).replace("/", "\\"))
    return path.resolve() if path.is_absolute() else qa_root(config) / path


def build_art_placement_manifest(config_path: Path, *, check_only: bool = False) -> dict[str, Any]:
    """Draft one explicit placement layer from approvals and legacy visual rows."""

    config = read_json(config_path)
    art = art_integration_config(config)
    manifest_target = art_placement_manifest_path(config)
    report = art_placement_draft_report_path(config)
    approval_path = image_role_approval_path(config)
    legacy_value = art.get("legacy_page_manifest")
    legacy_path = (qa_root(config) / str(legacy_value).replace("/", "\\")) if legacy_value else None
    findings: list[dict[str, Any]] = []
    if manifest_target is None:
        findings.append({"code": "art_placement_manifest_not_configured"})
    if not approval_path.exists():
        findings.append({"code": "missing_image_role_approval", "path": rel(approval_path)})
    if art.get("require_legacy_page_manifest") and (legacy_path is None or not legacy_path.exists()):
        findings.append({"code": "missing_legacy_page_art_manifest", "path": rel(legacy_path) if legacy_path else None})

    approval = read_json(approval_path) if approval_path.exists() else {"items": []}
    legacy = read_json(legacy_path) if legacy_path and legacy_path.exists() else {"rows": []}
    keeper_value = config.get("production_outputs", {}).get("keeper_markdown")
    keeper_path = root_path(str(keeper_value)) if keeper_value else None
    headings_by_page: dict[str, str] = {}
    page_markers: set[str] = set()
    if keeper_path and keeper_path.exists():
        keeper_text = keeper_path.read_text(encoding="utf-8")
        page_markers = {match.group(1) for match in re.finditer(r"^<!--\s*source-page-(\d{3})\s*-->$", keeper_text, re.M)}
        _, headings, _ = markdown_to_review_html(keeper_text, source_path=keeper_path, html_path=keeper_path.with_suffix(".html"))
        for heading in headings:
            page = str(heading.get("page") or "").zfill(3)
            if page and heading.get("href"):
                headings_by_page.setdefault(page, str(heading["href"]))
    else:
        findings.append({"code": "missing_keeper_markdown_for_art_anchors", "path": rel(keeper_path) if keeper_path else None})

    placements: list[dict[str, Any]] = []
    selected_pages: set[str] = set()
    for item in approval.get("items", []):
        if not isinstance(item, dict) or item.get("decision_state") != "approved":
            continue
        pages = item.get("pages") or []
        if not pages:
            findings.append({"code": "approved_art_missing_page", "xref": item.get("xref")})
            continue
        page = str(pages[0]).zfill(3)
        role = str(item.get("target_role") or "source_image")
        if role in {"decoration", "reject"}:
            continue
        heading_id = headings_by_page.get(page)
        anchor_kind = "heading" if heading_id else "source_page_section"
        if not heading_id:
            if page != "001" and page not in page_markers:
                fallback_pages = [candidate for candidate in headings_by_page if candidate < page]
                if role == "handout" and fallback_pages:
                    fallback_page = max(fallback_pages)
                    heading_id = headings_by_page[fallback_page]
                    anchor_kind = "heading_nearest_previous_page"
                else:
                    findings.append({"code": "approved_art_missing_heading_anchor", "xref": item.get("xref"), "page": page})
                    heading_id = f"page-{page}"
            else:
                heading_id = f"page-{page}"
        emit_reader_art_block = role in IMAGE_COPY_ROLES
        runtime_src = None
        if emit_reader_art_block and item.get("target_filename"):
            try:
                runtime_target = target_dir_for_image_role(config, role) / safe_filename(str(item["target_filename"]))
                default_package_root = root_path(str(config["production_outputs"]["images"])).parent
                package_root = root_path(str(config.get("public_package_root") or default_package_root))
                runtime_src = os.path.relpath(runtime_target, package_root).replace("\\", "/")
            except ValueError:
                runtime_src = None
        insertion_rule = (
            "before_page_anchor"
            if page == "001"
            else "replace_visual_page"
            if role == "handout" and page in {"112", "113", "114", "115", "116", "117", "118", "119", "120", "121", "122"}
            else "after_heading"
        )
        is_frontmatter_cover_art = page in frontmatter_cover_pages(config)
        production_role = "cover" if is_frontmatter_cover_art else role
        css_class = (
            "art-cover art-full-page"
            if is_frontmatter_cover_art
            else "art-full-width"
            if role in {"map", "floorplan", "handout"}
            else "art-inline"
        )
        placements.append(
            {
                "placement_id": f"xref-{int(item.get('xref', 0)):05d}",
                "asset_id": f"xref-{int(item.get('xref', 0)):05d}",
                "runtime_filename": item.get("target_filename"),
                "runtime_src": runtime_src,
                "runtime_role": role,
                "semantic_role": role,
                "source_kind": "extracted_asset",
                "source_page": page,
                "source_xref": item.get("xref"),
                "source_asset_path": item.get("source_path"),
                "source_asset_sha256": item.get("sha256"),
                "heading_id": heading_id,
                "anchor_kind": anchor_kind,
                "insertion_rule": insertion_rule,
                "decision_state": "approved",
                "emit_reader_art_block": emit_reader_art_block,
                "css_class": css_class,
                "production_role": production_role,
                "placement": "full_page" if is_frontmatter_cover_art else "page_art_after_heading",
                "columnned": False if is_frontmatter_cover_art else None,
                "reviewer": "image_role_approval",
                "visual_review_status": "approved_for_review",
                "review_reason": item.get("review_notes") or "Approved extracted source asset.",
            }
        )
        selected_pages.add(page)

    for row in legacy.get("rows", []):
        if not isinstance(row, dict):
            continue
        page = str(row.get("page") or "").zfill(3)
        placements.append(
            {
                "asset_id": row.get("target_filename") or f"legacy-page-{page}",
                "runtime_filename": row.get("target_filename"),
                "runtime_role": row.get("role") or "source_image",
                "semantic_role": row.get("role") or "source_image",
                "source_kind": "page_render",
                "source_page": page,
                "source_render": row.get("source_path"),
                "source_xrefs": row.get("source_xrefs") or [],
                "heading_id": headings_by_page.get(page, f"page-{page}"),
                "anchor_kind": "heading" if page in headings_by_page else "source_page_section",
                "insertion_rule": row.get("insertion_position") or "after_heading",
                "decision_state": "auxiliary" if page in selected_pages else "pending_visual_review",
                "reviewer": "legacy_page_render_inventory",
                "visual_review_status": "pending_user_review",
                "review_reason": "Explicit fallback inventory row; it is not selected for production without a crop or reviewed full-page exception.",
            }
        )

    result = {
        "schema": "translator_art_placement_manifest.v1",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "config": rel(config_path),
        "status": "needs_review" if findings else "pass",
        "action": "check_only" if check_only else "drafted",
        "placements": placements,
        "counts": {
            "placements": len(placements),
            "approved_extracted": sum(1 for item in placements if item.get("source_kind") == "extracted_asset"),
            "legacy_page_render_rows": sum(1 for item in placements if item.get("source_kind") == "page_render"),
            "findings": len(findings),
        },
        "findings": findings,
    }
    write_json(report, result)
    if manifest_target is not None and not check_only:
        write_json(manifest_target, result)
    return result


def preserve_page_art_report_path(config: dict[str, Any]) -> Path:
    art = art_integration_config(config)
    value = art.get("preserve_page_art_report", "preserve_page_art_report.json")
    path = Path(str(value).replace("/", "\\"))
    return path.resolve() if path.is_absolute() else qa_root(config) / path


def preserve_page_art(config_path: Path, *, apply: bool = False) -> dict[str, Any]:
    config = read_json(config_path)
    art_items = list(art_integration_config(config).get("preserved_page_art", []))
    render_dir = page_render_dir(config)
    report = preserve_page_art_report_path(config)
    preserved: list[dict[str, Any]] = []
    findings: list[dict[str, Any]] = []
    for index, item in enumerate(art_items, start=1):
        role = str(item.get("role") or "source_image")
        if role not in IMAGE_COPY_ROLES:
            findings.append({"index": index, "code": "invalid_preserved_art_role", "role": role})
            continue
        page = item.get("page")
        try:
            page_num = int(page)
        except (TypeError, ValueError):
            findings.append({"index": index, "code": "invalid_page", "page": page})
            continue
        source = page_render_path(render_dir, page_num)
        if source is None or not source.exists():
            findings.append({"index": index, "code": "missing_page_render", "page": page_num, "path": rel(source) if source else ""})
            continue
        target_filename = item.get("target_filename") or f"page-{page_num:03d}-{role}.png"
        try:
            filename = safe_filename(str(target_filename))
        except ValueError as exc:
            findings.append({"index": index, "code": "unsafe_target_filename", "message": str(exc)})
            continue
        target = target_dir_for_image_role(config, role) / filename
        crop_box = item.get("crop_box")
        record = {
            "index": index,
            "page": page_num,
            "role": role,
            "source_path": rel(source),
            "target_path": rel(target),
            "crop_box": crop_box,
            "review_notes": item.get("review_notes", ""),
            "action": "would_preserve" if not apply else "preserved",
        }
        if apply:
            target.parent.mkdir(parents=True, exist_ok=True)
            if crop_box:
                try:
                    box = tuple(int(value) for value in crop_box)
                except (TypeError, ValueError):
                    findings.append({"index": index, "code": "invalid_crop_box", "crop_box": crop_box})
                    continue
                if len(box) != 4:
                    findings.append({"index": index, "code": "invalid_crop_box", "crop_box": crop_box})
                    continue
                with Image.open(source) as image:
                    image.crop(box).save(target)
            else:
                shutil.copy2(source, target)
            record["target_sha256"] = sha256_file(target)
        preserved.append(record)
    result = {
        "schema": "translator_preserve_page_art.v1",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "config": rel(config_path),
        "mode": "apply" if apply else "check_only",
        "status": "fail" if findings else "pass",
        "counts": {
            "configured": len(art_items),
            "preserved_or_would_preserve": len(preserved),
            "findings": len(findings),
        },
        "preserved": preserved,
        "findings": findings,
    }
    write_json(report, result)
    return result


def art_integration_required_gates(config: dict[str, Any]) -> list[str]:
    return list(art_integration_config(config).get("required_gates", ["review_html_built"]))


def art_source_html_path(config: dict[str, Any]) -> Path | None:
    art = art_integration_config(config)
    value = art.get("source_html")
    if value:
        return root_path(str(value))
    outputs = config.get("production_outputs", {})
    if outputs.get("html"):
        return root_path(str(outputs["html"]))
    production = config.get("production_html", {})
    if production.get("output_html"):
        return root_path(str(production["output_html"]))
    return None


def art_gate_findings(config: dict[str, Any]) -> list[dict[str, Any]]:
    findings: list[dict[str, Any]] = []
    gates = config.get("scenario_gates", {})
    for gate in art_integration_required_gates(config):
        if gates.get(gate) is not True:
            findings.append({"code": "gate_not_passed", "gate": gate, "value": gates.get(gate)})
    return findings


def prepare_art_integration(config_path: Path, *, check_only: bool = False) -> dict[str, Any]:
    config = read_json(config_path)
    art = art_integration_config(config)
    approval_path = image_role_approval_path(config)
    apply_report_path = intake_report_path(config, "apply_image_approval_report", "apply_image_approval_report.json")
    source_html = art_source_html_path(config)
    report = art_integration_report_path(config)
    findings = art_gate_findings(config)
    approval_counts = {"pending": 0, "approved": 0, "rejected": 0}
    copied_targets: list[str] = []
    missing_targets: list[str] = []

    if not approval_path.exists():
        findings.append({"code": "missing_image_role_approval", "path": rel(approval_path)})
        approval_items: list[dict[str, Any]] = []
    else:
        approval = read_json(approval_path)
        approval_items = list(approval.get("items", []))
        approval_counts = dict(approval.get("counts", approval_counts))
        pending = int(approval_counts.get("pending", 0))
        if art.get("require_no_pending_image_approval", True) and pending:
            findings.append({"code": "pending_image_approval", "count": pending, "path": rel(approval_path)})

    if not apply_report_path.exists():
        findings.append({"code": "missing_apply_image_approval_report", "path": rel(apply_report_path)})
    else:
        apply_report = read_json(apply_report_path)
        if apply_report.get("counts", {}).get("findings", 0):
            findings.append(
                {
                    "code": "apply_image_approval_findings",
                    "count": apply_report.get("counts", {}).get("findings", 0),
                    "path": rel(apply_report_path),
                }
            )

    for item in approval_items:
        if item.get("decision_state") != "approved":
            continue
        role = item.get("target_role")
        if role in {"decoration", "reject"}:
            continue
        target_path = item.get("target_path")
        if item.get("target_filename") and role:
            try:
                target = target_dir_for_image_role(config, str(role)) / safe_filename(str(item["target_filename"]))
            except ValueError:
                continue
        elif target_path:
            target = root_path(str(target_path))
        else:
            findings.append({"code": "approved_image_missing_target", "xref": item.get("xref")})
            continue
        if target.exists():
            copied_targets.append(rel(target))
        else:
            missing_targets.append(rel(target))

    if art.get("require_applied_images", True) and missing_targets:
        findings.append({"code": "approved_images_not_applied", "count": len(missing_targets), "targets": missing_targets[:20]})
    if source_html is not None and art.get("require_source_html", False) and not source_html.exists():
        findings.append({"code": "missing_art_source_html", "path": rel(source_html)})

    status = "blocked" if findings else "pass"
    result = {
        "schema": "translator_art_integration_preparation.v1",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "config": rel(config_path),
        "status": status,
        "action": "check_only" if check_only else "prepared",
        "required_gates": art_integration_required_gates(config),
        "approval": rel(approval_path),
        "apply_report": rel(apply_report_path),
        "source_html": rel(source_html) if source_html else None,
        "counts": {
            "approval_pending": int(approval_counts.get("pending", 0)),
            "approval_approved": int(approval_counts.get("approved", 0)),
            "approval_rejected": int(approval_counts.get("rejected", 0)),
            "copied_targets": len(copied_targets),
            "missing_targets": len(missing_targets),
            "findings": len(findings),
        },
        "copied_targets": copied_targets,
        "missing_targets": missing_targets,
        "findings": findings,
    }
    write_json(report, result)
    return result


def flatten_for_jpeg(image: Image.Image) -> Image.Image:
    if image.mode in {"RGBA", "LA"} or (image.mode == "P" and "transparency" in image.info):
        rgba = image.convert("RGBA")
        background = Image.new("RGBA", rgba.size, (255, 250, 240, 255))
        background.alpha_composite(rgba)
        return background.convert("RGB")
    return image.convert("RGB")


def optimized_name(source_path: Path, quality: int) -> str:
    digest = sha256_file(source_path)[:10]
    return f"{source_path.stem}_{digest}_q{quality}.jpg"


def same_file_content(src: Path, dst: Path) -> bool:
    return dst.exists() and src.stat().st_size == dst.stat().st_size and sha256_file(src) == sha256_file(dst)


def ensure_master_copy(source_path: Path, *, images_root: Path, working_master_root: Path) -> Path:
    target = working_master_root / source_path.resolve().relative_to(images_root.resolve())
    target.parent.mkdir(parents=True, exist_ok=True)
    if not same_file_content(source_path, target):
        shutil.copy2(source_path, target)
    return target


def optimize_png(
    source_path: Path,
    *,
    html_path: Path,
    images_root: Path,
    optimized_root: Path | None,
    working_master_root: Path,
    quality: int,
) -> dict[str, Any]:
    master_copy = ensure_master_copy(source_path, images_root=images_root, working_master_root=working_master_root)
    target_root = source_path.parent if optimized_root is None else optimized_root
    optimized_path = target_root / optimized_name(source_path, quality)
    optimized_path.parent.mkdir(parents=True, exist_ok=True)
    if not optimized_path.exists() or optimized_path.stat().st_mtime < source_path.stat().st_mtime:
        with Image.open(source_path) as image:
            flatten_for_jpeg(image).save(
                optimized_path,
                format="JPEG",
                quality=quality,
                optimize=True,
                progressive=True,
                subsampling=1,
            )
    return {
        "source_path": rel(source_path),
        "working_master_path": rel(master_copy),
        "optimized_path": rel(optimized_path),
        "html_src": os.path.relpath(optimized_path, html_path.parent).replace("\\", "/"),
        "source_bytes": source_path.stat().st_size,
        "optimized_bytes": optimized_path.stat().st_size,
        "source_sha256": sha256_file(source_path),
        "optimized_sha256": sha256_file(optimized_path),
        "format": "jpeg",
        "jpeg_quality": quality,
    }


def rewrite_png_refs(config: dict[str, Any], html_text: str, *, html_path: Path, images_root: Path) -> tuple[str, list[dict[str, Any]]]:
    pp = postproduction_config(config)
    quality = int(pp.get("image_quality", 80))
    optimized_dir_value = pp.get("optimized_image_dir", "source_dir")
    optimized_dir = str(optimized_dir_value or "").strip()
    if optimized_dir.lower() in {"", "source_dir", "role_dir", "same_dir"}:
        optimized_root = None
    else:
        optimized_root = (html_path.parent / optimized_dir.replace("/", "\\")).resolve()
    working_master_root = root_path(pp.get("working_master_images") or f"{config.get('workbench_root', 'translator')}/Images/production_source_png")
    conversions: list[dict[str, Any]] = []
    by_source: dict[Path, dict[str, Any]] = {}

    def replace(match: re.Match[str]) -> str:
        prefix, src, suffix = match.group(1), match.group(2), match.group(3)
        if "://" in src or src.startswith("data:"):
            return match.group(0)
        source_path = (html_path.parent / src.replace("/", "\\")).resolve()
        if not source_path.exists() or images_root.resolve() not in source_path.parents:
            return match.group(0)
        if source_path.suffix.lower() != ".png":
            return match.group(0)
        if source_path not in by_source:
            by_source[source_path] = optimize_png(
                source_path,
                html_path=html_path,
                images_root=images_root,
                optimized_root=optimized_root,
                working_master_root=working_master_root,
                quality=quality,
            )
            conversions.append(by_source[source_path])
        return prefix + by_source[source_path]["html_src"] + suffix

    html_text = IMG_PNG_SRC_RE.sub(replace, html_text)
    html_text = CSS_PNG_URL_RE.sub(replace, html_text)
    return html_text, conversions


def page_section_re(page: str) -> re.Pattern[str]:
    return re.compile(
        rf'(?P<page><!--\s*pdf-page-{re.escape(page)}\s*-->\s*<section\b[^>]*\bdata-page=["\']{re.escape(page)}["\'][\s\S]*?</section>)',
        re.I,
    )


def credits_before_toc(config: dict[str, Any]) -> bool:
    """Resolve credit placement from the closed frontmatter role order.

    Stage 40 supplies ``frontmatter_order`` as the authoritative ordering
    contract.  The historical ``frontmatter_position`` remains a fallback for
    standalone/legacy configs that have no resolved order.
    """
    policy = resolved_frontmatter_policy(config)
    order = policy.get("frontmatter_order")
    if isinstance(order, list) and order:
        roles = [str(role) for role in order]
        toc_role = "source_toc" if "source_toc" in roles else "toc" if "toc" in roles else None
        if "credits" in roles and toc_role is not None:
            return roles.index("credits") < roles.index(toc_role)
        return False
    return policy["credits_policy"].get("frontmatter_position") == "before_toc"


def place_landing_and_toc(config: dict[str, Any], html_text: str) -> tuple[str, bool, str]:
    pp = postproduction_config(config)
    if pp.get("toc_position", "after_landing") != "after_landing":
        return html_text, True, "toc_position_not_changed"
    if production_html_config(config).get("landing_asset"):
        landing = re.search(r'<section\b[^>]*\bclass=["\'][^"\']*production-landing[^"\']*["\'][\s\S]*?</section>', html_text, re.I)
        toc = TOC_RE.search(html_text)
        if not toc or not landing:
            return html_text, False, "missing_custom_landing_or_toc"
        if landing.start() < toc.start():
            ordered_html = html_text
            landing_action = "custom_landing_before_toc"
        else:
            landing_block = landing.group(0)
            without_landing = html_text[: landing.start()] + html_text[landing.end() :]
            toc_after = TOC_RE.search(without_landing)
            if not toc_after:
                return html_text, False, "toc_missing_after_custom_landing_removal"
            ordered_html = without_landing[: toc_after.start()] + landing_block + "\n" + toc_after.group("toc") + without_landing[toc_after.end() :]
            landing_action = "moved_custom_landing_before_toc"
        if not credits_before_toc(config):
            return ordered_html, True, landing_action
        credits = re.search(
            r'(?P<section><section\b[^>]*\bclass=["\'][^"\']*page-type-credits[^"\']*["\'][\s\S]*?</section>)'
            r'(?P<boundary>\s*<div\b[^>]*\bclass=["\'][^"\']*credits-page-boundary[^"\']*["\'][^>]*></div>)?',
            ordered_html,
            re.I,
        )
        if not credits:
            return ordered_html, False, "missing_credits_for_before_toc"
        toc = TOC_RE.search(ordered_html)
        if not toc:
            return ordered_html, False, "toc_missing_before_credits_placement"
        landing = re.search(r'<section\b[^>]*\bclass=["\'][^"\']*production-landing[^"\']*["\'][\s\S]*?</section>', ordered_html, re.I)
        if landing and landing.start() < credits.start() < toc.start():
            return ordered_html, True, landing_action + "+credits_before_toc"
        credits_block = credits.group(0)
        without_credits = ordered_html[: credits.start()] + ordered_html[credits.end() :]
        toc_after = TOC_RE.search(without_credits)
        if not toc_after:
            return ordered_html, False, "toc_missing_after_credits_removal"
        ordered_html = without_credits[: toc_after.start()] + credits_block + "\n" + toc_after.group("toc") + without_credits[toc_after.end() :]
        return ordered_html, True, landing_action + "+moved_credits_before_toc"
    landing_page = str(pp.get("landing_page", "001")).zfill(3)
    toc = TOC_RE.search(html_text)
    landing = page_section_re(landing_page).search(html_text)
    if not toc or not landing:
        return html_text, False, "missing_toc_or_landing"
    if landing.start() < toc.start():
        ordered_html = html_text
        landing_action = "already_landing_before_toc"
    else:
        landing_block = landing.group("page")
        toc_block = toc.group("toc")
        without_landing = html_text[: landing.start()] + html_text[landing.end() :]
        toc_after = TOC_RE.search(without_landing)
        if not toc_after:
            return html_text, False, "toc_missing_after_landing_removal"
        ordered_html = without_landing[: toc_after.start()] + landing_block + "\n" + toc_block + without_landing[toc_after.end() :]
        landing_action = "moved_landing_before_toc"
    if not credits_before_toc(config):
        return ordered_html, True, landing_action
    credits = re.search(
        r'(?P<section><section\b[^>]*\bclass=["\'][^"\']*page-type-credits[^"\']*["\'][\s\S]*?</section>)'
        r'(?P<boundary>\s*<div\b[^>]*\bclass=["\'][^"\']*credits-page-boundary[^"\']*["\'][^>]*></div>)?',
        ordered_html,
        re.I,
    )
    toc = TOC_RE.search(ordered_html)
    if not credits or not toc:
        return ordered_html, False, "missing_credits_or_toc_for_before_toc"
    if landing.start() < credits.start() < toc.start():
        return ordered_html, True, landing_action + "+credits_before_toc"
    credits_block = credits.group(0)
    without_credits = ordered_html[: credits.start()] + ordered_html[credits.end() :]
    toc_after = TOC_RE.search(without_credits)
    if not toc_after:
        return ordered_html, False, "toc_missing_after_credits_removal"
    ordered_html = without_credits[: toc_after.start()] + credits_block + "\n" + toc_after.group("toc") + without_credits[toc_after.end() :]
    return ordered_html, True, landing_action + "+moved_credits_before_toc"


def optimize_images(config_path: Path) -> dict[str, Any]:
    config = read_json(config_path)
    html_path = root_path(config["production_outputs"]["html"])
    images_root = root_path(config["production_outputs"]["images"])
    html_before = html_path.read_text(encoding="utf-8")
    html_text = html_before
    conversions: list[dict[str, Any]] = []
    if postproduction_config(config).get("optimize_runtime_png", True):
        html_text, conversions = rewrite_png_refs(config, html_text, html_path=html_path, images_root=images_root)
    html_text, order_ok, order_action = place_landing_and_toc(config, html_text)
    html_path.write_text(html_text, encoding="utf-8", newline="\n")
    result = {
        "schema": "translator_postproduction_image_optimization.v1",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "config": rel(config_path),
        "status": "pass" if order_ok else "blocked",
        "html": rel(html_path),
        "html_changed": html_before != html_text,
        "html_before_sha256": sha256_text(html_before),
        "html_after_sha256": sha256_text(html_text),
        "landing_toc_order": {"ok": order_ok, "action": order_action},
        "conversions": conversions,
        "counts": {
            "converted_png_refs": len(conversions),
            "source_bytes": sum(item["source_bytes"] for item in conversions),
            "optimized_bytes": sum(item["optimized_bytes"] for item in conversions),
        },
    }
    write_json(report_path(config, "optimization_report", "postproduction_image_optimization.json"), result)
    return result


def normalize_ref(value: str) -> str:
    value = unquote(value.strip().strip("'\""))
    return value.split("#", 1)[0] if "#" in value else value


def html_refs(html: str) -> list[str]:
    refs = []
    for match in IMG_REF_RE.finditer(html):
        ref = normalize_ref(match.group(1))
        if ref and not ref.startswith("data:") and "://" not in ref:
            refs.append(ref)
    return refs


def flow_re(config: dict[str, Any]) -> re.Pattern[str]:
    landing = str(postproduction_config(config).get("landing_page", "001")).zfill(3)
    return re.compile(
        rf'(<section\b[^>]*\bclass=["\'][^"\']*production-landing[^"\']*["\'][\s\S]*?</section>|<nav\b[^>]*\bid=["\']toc["\'][\s\S]*?</nav>|<!--\s*pdf-page-{landing}\s*-->\s*<section\b[^>]*\bdata-page=["\']{landing}["\'][\s\S]*?</section>|<section\b[^>]*\bdata-page=["\'][^"\']+["\'][\s\S]*?</section>)',
        re.I,
    )


def first_flow_items(config: dict[str, Any], html: str) -> list[str]:
    items: list[str] = []
    landing = str(postproduction_config(config).get("landing_page", "001")).zfill(3)
    for match in flow_re(config).finditer(html):
        chunk = match.group(1)
        if re.search(r'class=["\'][^"\']*production-landing', chunk, re.I):
            items.append("landing")
        elif "<nav" in chunk and re.search(r'id=["\']toc["\']', chunk):
            items.append("toc")
        elif f'data-page="{landing}"' in chunk or f"data-page='{landing}'" in chunk:
            items.append(f"page-{landing}")
        else:
            page = re.search(r'data-page=["\']([^"\']+)["\']', chunk)
            items.append(f"page-{page.group(1)}" if page else "section")
        if len(items) >= 5:
            break
    return items


def postproduction_qa(config_path: Path) -> dict[str, Any]:
    config = read_json(config_path)
    pp = postproduction_config(config)
    html_path = root_path(config["production_outputs"]["html"])
    images_root = root_path(config["production_outputs"]["images"])
    html = html_path.read_text(encoding="utf-8")
    refs = html_refs(html)
    resolved = [(ref, (html_path.parent / ref.replace("/", "\\")).resolve()) for ref in refs]
    missing = [ref for ref, path in resolved if not path.exists()]
    png_exceptions = set(pp.get("keep_png_runtime_exceptions", []))
    png_refs = [ref for ref, path in resolved if path.exists() and path.suffix.lower() == ".png" and ref not in png_exceptions]
    optimized_dir_value = pp.get("optimized_image_dir", "source_dir")
    optimized_dir = str(optimized_dir_value or "").strip().replace("/", "\\")
    if optimized_dir.lower() in {"", "source_dir", "role_dir", "same_dir"}:
        optimized_refs = [
            ref for ref, path in resolved
            if path.exists() and images_root in path.parents and path.suffix.lower() in {".jpg", ".jpeg"}
        ]
    else:
        optimized_refs = [
            ref for ref, path in resolved
            if path.exists() and optimized_dir in str(path) and path.suffix.lower() in {".jpg", ".jpeg"}
        ]
    outside_images = [ref for ref, path in resolved if path.exists() and images_root not in path.parents]
    first_items = first_flow_items(config, html)
    landing = str(pp.get("landing_page", "001")).zfill(3)
    findings: list[dict[str, str]] = []
    expected_flow = ["landing", "toc"] if production_html_config(config).get("landing_asset") else [f"page-{landing}", "toc"]
    if pp.get("toc_position", "after_landing") == "after_landing" and first_items[:2] != expected_flow:
        findings.append({"code": "landing_toc_order", "message": f"first flow items are {first_items[:5]}"})
    if missing:
        findings.append({"code": "missing_image_refs", "message": ", ".join(missing[:10])})
    if png_refs:
        findings.append({"code": "png_runtime_refs", "message": ", ".join(png_refs[:10])})
    if outside_images:
        findings.append({"code": "image_ref_outside_public_images", "message": ", ".join(outside_images[:10])})
    if pp.get("optimize_runtime_png", True) and refs and not optimized_refs:
        findings.append({"code": "no_optimized_refs", "message": "no optimized JPEG runtime refs found"})
    result = {
        "schema": "translator_public_postproduction_qa.v1",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "config": rel(config_path),
        "html": rel(html_path),
        "images_root": rel(images_root),
        "hashes": {"html_sha256": sha256_file(html_path)},
        "status": "pass" if not findings else "fail",
        "counts": {
            "image_refs": len(refs),
            "optimized_refs": len(optimized_refs),
            "png_runtime_refs": len(png_refs),
            "missing_image_refs": len(missing),
        },
        "first_flow_items": first_items,
        "findings": findings,
    }
    write_json(report_path(config, "qa_report", "public_postproduction_qa.json"), result)
    return result


def cleanup_runtime_images_report_path(config: dict[str, Any]) -> Path:
    pp = postproduction_config(config)
    return report_path(config, "runtime_cleanup_report", str(pp.get("runtime_cleanup_report", "runtime_image_cleanup_report.json")))


def cleanup_runtime_protected_assets(config: dict[str, Any]) -> dict[Path, list[str]]:
    protected: dict[Path, list[str]] = {}

    def protect(path: Path, reason: str) -> None:
        protected.setdefault(path.resolve(), []).append(reason)

    landing = production_html_config(config).get("landing_asset")
    if isinstance(landing, dict) and landing.get("src"):
        protect(root_path(str(landing["src"])), "configured_landing_asset")
    landing_decision = production_html_config(config).get("landing_decision")
    if isinstance(landing_decision, dict) and landing_decision.get("runtime_asset"):
        protect(root_path(str(landing_decision["runtime_asset"])), "configured_landing_runtime_asset")

    for item in art_integration_config(config).get("preserved_page_art", []):
        role = str(item.get("role") or "source_image")
        if role not in IMAGE_COPY_ROLES:
            continue
        try:
            page = int(item.get("page"))
            filename = item.get("target_filename") or f"page-{page:03d}-{role}.png"
            protect(target_dir_for_image_role(config, role) / safe_filename(str(filename)), "preserved_page_art")
        except (TypeError, ValueError):
            continue

    for item in production_art_layout_config(config).get("required_assets", []):
        if not isinstance(item, dict):
            continue
        filename = str(item.get("target_filename") or item.get("asset_id") or "").strip()
        role = str(item.get("role") or item.get("production_role") or "source_image")
        if not filename:
            continue
        try:
            protect(target_dir_for_image_role(config, role) / safe_filename(filename), "required_runtime_asset")
        except ValueError:
            continue

    for item in postproduction_config(config).get("required_runtime_assets", []):
        value = item.get("path") if isinstance(item, dict) else item
        if value:
            protect(root_path(str(value)), "configured_required_runtime_asset")
    return protected


def cleanup_runtime_images(config_path: Path, *, apply: bool = False) -> dict[str, Any]:
    config = read_json(config_path)
    pp = postproduction_config(config)
    html_path = root_path(config["production_outputs"]["html"])
    images_root = root_path(config["production_outputs"]["images"])
    html = html_path.read_text(encoding="utf-8")
    used_paths = {
        (html_path.parent / ref.replace("/", "\\")).resolve()
        for ref in html_refs(html)
        if "://" not in ref and not ref.startswith("data:")
    }
    configured_dirs = pp.get(
        "runtime_image_cleanup_dirs",
        [
            "Landing",
            "Maps",
            "Source_Images",
        ],
    )
    remove_empty_dirs = bool(pp.get("runtime_cleanup_remove_empty_dirs", True))
    images_root_resolved = images_root.resolve()
    scan_dirs = [images_root / str(item).replace("/", "\\") for item in configured_dirs]
    findings: list[dict[str, Any]] = []
    warnings: list[dict[str, Any]] = []
    skipped_dirs: list[str] = []
    protected_assets: list[dict[str, Any]] = []
    candidates: list[dict[str, Any]] = []
    candidate_paths: list[tuple[dict[str, Any], Path]] = []
    rejected_candidates: list[dict[str, Any]] = []
    rebuild_required_assets: list[dict[str, Any]] = []
    protected_paths = cleanup_runtime_protected_assets(config)
    landing = production_html_config(config).get("landing_asset")
    if isinstance(landing, dict) and landing.get("src"):
        landing_src = root_path(str(landing["src"]))
        if not landing_src.exists():
            rebuild_required_assets.append(
                {
                    "code": "missing_landing_runtime_asset",
                    "path": rel(landing_src),
                    "regenerate_with": "prepare landing asset before build-production-html",
                }
            )
    for item in art_integration_config(config).get("preserved_page_art", []):
        role = str(item.get("role") or "source_image")
        if role not in IMAGE_COPY_ROLES:
            continue
        try:
            page = int(item.get("page"))
            target_filename = item.get("target_filename") or f"page-{page:03d}-{role}.png"
            target = target_dir_for_image_role(config, role) / safe_filename(str(target_filename))
        except (TypeError, ValueError):
            continue
        if not target.exists():
            rebuild_required_assets.append(
                {
                    "code": "missing_preserved_page_art_runtime_asset",
                    "page": f"{page:03d}",
                    "role": role,
                    "path": rel(target),
                    "regenerate_with": "preserve-page-art --apply",
                }
            )
    if rebuild_required_assets:
        warnings.append(
            {
                "code": "production_html_rebuild_requires_asset_regeneration",
                "missing_required_assets": len(rebuild_required_assets),
            }
        )
    for directory in scan_dirs:
        if not directory.exists():
            skipped_dirs.append(rel(directory))
            continue
        directory_resolved = directory.resolve()
        if images_root_resolved not in {directory_resolved, *directory_resolved.parents}:
            findings.append({"code": "cleanup_dir_outside_images_root", "path": rel(directory)})
            continue
        for path in sorted(directory.iterdir()):
            if path.is_symlink():
                rejected_candidates.append({"path": rel(path), "code": "cleanup_symlink_candidate_rejected"})
                continue
            if not path.is_file():
                continue
            resolved_path = path.resolve()
            if images_root_resolved not in {resolved_path, *resolved_path.parents}:
                findings.append({"code": "cleanup_candidate_outside_images_root", "path": rel(path)})
                continue
            if resolved_path in used_paths:
                continue
            reasons = protected_paths.get(resolved_path)
            if reasons:
                protected_assets.append({"path": rel(path), "reasons": reasons})
                continue
            candidate = {
                "path": rel(path),
                "bytes": path.stat().st_size,
                "sha256": sha256_file(path),
            }
            candidates.append(candidate)
            candidate_paths.append((candidate, path))
    deleted: list[dict[str, Any]] = []
    deleted_dirs: list[str] = []
    if apply and not findings:
        for item, path in candidate_paths:
            resolved_path = path.resolve()
            if path.is_symlink():
                rejected_candidates.append({"path": rel(path), "code": "cleanup_symlink_candidate_rejected_before_delete"})
                continue
            if images_root_resolved not in {resolved_path, *resolved_path.parents}:
                findings.append({"code": "cleanup_candidate_outside_images_root_before_delete", "path": rel(path)})
                continue
            if path.exists() and path.is_file():
                path.unlink()
                deleted.append(item)
        if remove_empty_dirs:
            for directory in sorted(scan_dirs, key=lambda item: len(item.parts), reverse=True):
                if not directory.exists() or not directory.is_dir():
                    continue
                directory_resolved = directory.resolve()
                if images_root_resolved not in {directory_resolved, *directory_resolved.parents}:
                    continue
                try:
                    next(directory.iterdir())
                except StopIteration:
                    directory.rmdir()
                    deleted_dirs.append(rel(directory))
    result = {
        "schema": "translator_runtime_image_cleanup.v1",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "config": rel(config_path),
        "status": "blocked" if findings else "pass",
        "mode": "apply" if apply else "dry_run",
        "action": "apply" if apply else "dry_run",
        "artifact_writes": {"qa_report": True, "runtime_assets_deleted": bool(deleted)},
        "html": rel(html_path),
        "images_root": rel(images_root),
        "scan_dirs": [rel(path) for path in scan_dirs],
        "skipped_dirs": skipped_dirs,
        "counts": {
            "html_image_refs": len(used_paths),
            "unused_candidates": len(candidates),
            "protected_assets": len(protected_assets),
            "rejected_candidates": len(rejected_candidates),
            "deleted": len(deleted),
            "deleted_dirs": len(deleted_dirs),
            "skipped_dirs": len(skipped_dirs),
            "findings": len(findings),
            "warnings": len(warnings),
            "missing_required_runtime_assets": len(rebuild_required_assets),
        },
        "unused_candidates": candidates,
        "protected_assets": protected_assets,
        "rejected_candidates": rejected_candidates,
        "deleted": deleted,
        "deleted_dirs": deleted_dirs,
        "rebuildability": {
            "production_html_clean_rebuild_ready": not rebuild_required_assets,
            "missing_required_runtime_assets": rebuild_required_assets,
        },
        "findings": findings,
        "warnings": warnings,
    }
    write_json(cleanup_runtime_images_report_path(config), result)
    return result


def config_report_path(config: dict[str, Any], section: str, default_name: str, key: str = "report") -> Path:
    value = config.get(section, {}).get(key, default_name)
    path = Path(str(value).replace("/", "\\"))
    return path.resolve() if path.is_absolute() else qa_root(config) / path


def page_structure_audit_config(config: dict[str, Any]) -> dict[str, Any]:
    return config.get("page_structure_audit", {})


def page_structure_audit_report_path(config: dict[str, Any]) -> Path:
    return config_report_path(config, "page_structure_audit", "page_structure_audit.json")


def page_structure_audit_markdown_path(config: dict[str, Any]) -> Path | None:
    value = page_structure_audit_config(config).get("markdown_report")
    if not value:
        return None
    path = Path(str(value).replace("/", "\\"))
    return path.resolve() if path.is_absolute() else qa_root(config) / path


def page_structure_audit_input_path(config: dict[str, Any], key: str) -> Path:
    cfg = page_structure_audit_config(config)
    if not cfg.get(key):
        raise ValueError(f"page_structure_audit.{key} is required")
    return root_path(str(cfg[key]))


def run_page_structure_audit(config_path: Path, *, check_only: bool = False) -> dict[str, Any]:
    config = read_json(config_path)
    cfg = page_structure_audit_config(config)
    source_path = page_structure_audit_input_path(config, "source_markdown")
    candidate_path = page_structure_audit_input_path(config, "candidate_markdown")
    ledger_path = root_path(str(cfg["acceptance_ledger"])) if cfg.get("acceptance_ledger") else None
    ledger = read_json(ledger_path) if ledger_path and ledger_path.exists() else {"records": []}
    source_text = source_path.read_text(encoding="utf-8")
    candidate_text = candidate_path.read_text(encoding="utf-8")
    result = page_structure_audit.audit_texts(
        source_text,
        candidate_text,
        policy=cfg.get("policy") or {},
        source_label=rel(source_path),
        candidate_label=rel(candidate_path),
        source_sha256=page_structure_audit.sha256_file(source_path),
        candidate_sha256=page_structure_audit.sha256_file(candidate_path),
        ledger=ledger,
    )
    result["check_only"] = check_only
    result["acceptance_ledger_path"] = rel(ledger_path) if ledger_path else None
    report = page_structure_audit_report_path(config)
    markdown = page_structure_audit_markdown_path(config)
    page_structure_audit.write_audit(result, report, markdown)
    result["report"] = rel(report)
    result["markdown_report"] = rel(markdown) if markdown else None
    return result


def coc_mechanics_audit_config(config: dict[str, Any]) -> dict[str, Any]:
    return config.get("coc_mechanics_audit", {})


def coc_mechanics_audit_report_path(config: dict[str, Any]) -> Path:
    return config_report_path(config, "coc_mechanics_audit", "coc_mechanics_audit.json")


def coc_mechanics_audit_markdown_path(config: dict[str, Any]) -> Path | None:
    value = coc_mechanics_audit_config(config).get("markdown_report")
    if not value:
        return None
    path = Path(str(value).replace("/", "\\"))
    return path.resolve() if path.is_absolute() else qa_root(config) / path


def coc_mechanics_audit_input_path(config: dict[str, Any]) -> Path:
    cfg = coc_mechanics_audit_config(config)
    value = cfg.get("input") or cfg.get("html") or cfg.get("candidate")
    if not value:
        raise ValueError("coc_mechanics_audit.input is required")
    return root_path(str(value))


def run_coc_mechanics_audit(config_path: Path, *, check_only: bool = False) -> dict[str, Any]:
    config = read_json(config_path)
    cfg = coc_mechanics_audit_config(config)
    input_path = coc_mechanics_audit_input_path(config)
    text = input_path.read_text(encoding="utf-8")
    result = coc_mechanics_audit.audit_text(
        text,
        policy=cfg.get("policy") or {},
        input_label=rel(input_path),
        input_sha256=coc_mechanics_audit.sha256_file(input_path),
    )
    result["check_only"] = check_only
    report = coc_mechanics_audit_report_path(config)
    markdown = coc_mechanics_audit_markdown_path(config)
    coc_mechanics_audit.write_audit(result, report, markdown)
    result["report"] = rel(report)
    result["markdown_report"] = rel(markdown) if markdown else None
    return result


def positive_content_audit_config(config: dict[str, Any]) -> dict[str, Any]:
    return config.get("positive_content_audit", {})


def positive_content_audit_report_path(config: dict[str, Any]) -> Path:
    return config_report_path(config, "positive_content_audit", "positive_content_audit.json")


def positive_content_audit_markdown_path(config: dict[str, Any]) -> Path | None:
    value = positive_content_audit_config(config).get("markdown_report")
    if not value:
        return None
    path = Path(str(value).replace("/", "\\"))
    return path.resolve() if path.is_absolute() else qa_root(config) / path


def resolve_positive_content_path(value: str) -> Path:
    path = Path(str(value).replace("/", "\\"))
    return path.resolve() if path.is_absolute() else root_path(str(value))


def run_positive_content_audit(config_path: Path, *, check_only: bool = False) -> dict[str, Any]:
    config = read_json(config_path)
    cfg = positive_content_audit_config(config)
    audit_cfg: dict[str, Any] = {
        "expected": cfg.get("expected") or {},
    }
    if cfg.get("html"):
        audit_cfg["html"] = str(resolve_positive_content_path(str(cfg["html"])))
    if cfg.get("kb_root"):
        audit_cfg["kb_root"] = str(resolve_positive_content_path(str(cfg["kb_root"])))
    result = positive_content_audit.audit(audit_cfg)
    result["check_only"] = check_only
    report = positive_content_audit_report_path(config)
    markdown = positive_content_audit_markdown_path(config)
    positive_content_audit.write_audit(result, report, markdown)
    result["report"] = rel(report)
    result["markdown_report"] = rel(markdown) if markdown else None
    return result


def remediation_checkpoint_config(config: dict[str, Any]) -> dict[str, Any]:
    return config.get("remediation_checkpoint_audit", {})


def remediation_checkpoint_report_path(config: dict[str, Any]) -> Path:
    return config_report_path(config, "remediation_checkpoint_audit", "remediation_checkpoint_audit.json")


def remediation_checkpoint_markdown_path(config: dict[str, Any]) -> Path | None:
    value = remediation_checkpoint_config(config).get("markdown_report")
    if not value:
        return None
    path = Path(str(value).replace("/", "\\"))
    return path.resolve() if path.is_absolute() else qa_root(config) / path


def run_remediation_checkpoint_audit(config_path: Path, *, check_only: bool = False) -> dict[str, Any]:
    config = read_json(config_path)
    cfg = remediation_checkpoint_config(config)
    checkpoint = cfg.get("checkpoint")
    checkpoint_path = resolve_positive_content_path(str(checkpoint)) if checkpoint else qa_root(config) / "user_review_remediation_checkpoint.v1.json"
    result = remediation_checkpoint_audit.audit_checkpoint(checkpoint_path)
    result["check_only"] = check_only
    report = remediation_checkpoint_report_path(config)
    markdown = remediation_checkpoint_markdown_path(config)
    remediation_checkpoint_audit.write_audit(result, report, markdown)
    result["report"] = rel(report)
    result["markdown_report"] = rel(markdown) if markdown else None
    return result


def semantic_chain_audit_config(config: dict[str, Any]) -> dict[str, Any]:
    return config.get("semantic_chain_audit", {})


def semantic_chain_audit_report_path(config: dict[str, Any]) -> Path:
    return config_report_path(config, "semantic_chain_audit", "semantic_chain_audit.json")


def semantic_chain_audit_markdown_path(config: dict[str, Any]) -> Path | None:
    value = semantic_chain_audit_config(config).get("markdown_report")
    if not value:
        return None
    path = Path(str(value).replace("/", "\\"))
    return path.resolve() if path.is_absolute() else qa_root(config) / path


def resolve_semantic_chain_path(config: dict[str, Any], value: str, *, report: bool = False) -> Path:
    path = Path(str(value).replace("/", "\\"))
    if path.is_absolute():
        return path.resolve()
    return (qa_root(config) / path).resolve() if report else root_path(str(value))


def run_semantic_chain_audit(config_path: Path, *, check_only: bool = False) -> dict[str, Any]:
    config = read_json(config_path)
    cfg = semantic_chain_audit_config(config)
    audit_cfg = {
        "artifacts": {
            name: {**spec, "path": str(resolve_semantic_chain_path(config, str(spec["path"])))}
            for name, spec in (cfg.get("artifacts") or {}).items()
        },
        "reports": {
            name: {**spec, "path": str(resolve_semantic_chain_path(config, str(spec["path"]), report=True))}
            for name, spec in (cfg.get("reports") or {}).items()
        },
        "links": cfg.get("links") or [],
    }
    approval_cfg = dict(cfg.get("approval") or {})
    if approval_cfg:
        approval_cfg.update(production_approval_state(config))
        audit_cfg["approval"] = approval_cfg
    result = semantic_chain_audit.audit_chain(audit_cfg)
    result["check_only"] = check_only
    report = semantic_chain_audit_report_path(config)
    markdown = semantic_chain_audit_markdown_path(config)
    semantic_chain_audit.write_audit(result, report, markdown)
    result["report"] = rel(report)
    result["markdown_report"] = rel(markdown) if markdown else None
    return result


def gate_state(config: dict[str, Any]) -> dict[str, Any]:
    scenario_gates = dict(config.get("scenario_gates") or {})
    production_gates = dict(config.get("production_gates") or {})
    merged = dict(scenario_gates)
    for gate, production_value in production_gates.items():
        if gate in scenario_gates and scenario_gates[gate] != production_value:
            # A contradictory declaration must never satisfy a required gate.
            merged[gate] = False
        else:
            merged[gate] = production_value
    return merged


def explicit_production_approved(config: dict[str, Any]) -> bool:
    gates = gate_state(config)
    ledger_cfg = config.get("approval_ledger", {})
    explicit = bool(ledger_cfg.get("explicit_production_approval") or ledger_cfg.get("user_production_approval"))
    if ledger_cfg.get("production_approval_must_be_explicit", True):
        return gates.get("production_approved") is True and explicit
    return gates.get("production_approved") is True


def production_approval_state(config: dict[str, Any]) -> dict[str, Any]:
    gates = gate_state(config)
    ledger_cfg = config.get("approval_ledger", {})
    explicit = bool(ledger_cfg.get("explicit_production_approval") or ledger_cfg.get("user_production_approval"))
    return {
        "production_approved": explicit_production_approved(config),
        "production_gate": gates.get("production_approved") is True,
        "explicit_approval": explicit,
        "approval_source": ledger_cfg.get("approval_source") if explicit else None,
        "script_success_is_not_production_approval": True,
    }


def approval_ledger_report_path(config: dict[str, Any]) -> Path:
    return config_report_path(config, "approval_ledger", "approval_ledger.json")


def approval_ledger_qa_path(config: dict[str, Any]) -> Path:
    return config_report_path(config, "approval_ledger", "approval_ledger_qa.json", key="qa_report")


def run_approval_ledger(config_path: Path, *, check_only: bool = False) -> dict[str, Any]:
    config = read_json(config_path)
    ledger_cfg = config.get("approval_ledger", {})
    report = approval_ledger_report_path(config)
    qa_report = approval_ledger_qa_path(config)
    gates = gate_state(config)
    findings: list[dict[str, Any]] = []
    warnings: list[dict[str, Any]] = []
    production_approved = gates.get("production_approved") is True
    explicit = bool(ledger_cfg.get("explicit_production_approval") or ledger_cfg.get("user_production_approval"))
    if ledger_cfg.get("production_approval_must_be_explicit", True) and production_approved and not explicit:
        findings.append({"code": "production_approved_without_explicit_approval"})
    future_open = [
        key
        for key, value in gates.items()
        if key.endswith("_approved") and key != "production_approved" and value is True
    ]
    if future_open:
        warnings.append({"code": "non_terminal_approval_gates_true", "gates": future_open})
    ledger = {
        "schema": "translator_approval_ledger.v1",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "config": rel(config_path),
        "project_key": config.get("project_key"),
        "gates": gates,
        "production_gate_boundaries": {
            **production_approval_state(config),
            "production_approval_source": ledger_cfg.get("approval_source") if explicit else None,
        },
        "status": "blocked" if findings else "pass",
        "findings": findings,
        "warnings": warnings,
    }
    qa = {
        "schema": "translator_approval_ledger_qa.v1",
        "generated_at_utc": ledger["generated_at_utc"],
        "config": rel(config_path),
        "ledger": rel(report),
        "status": ledger["status"],
        "counts": {"gates": len(gates), "findings": len(findings), "warnings": len(warnings)},
        "findings": findings,
        "warnings": warnings,
    }
    if not check_only:
        write_json(report, ledger)
    write_json(qa_report, qa)
    return qa


def release_manifest_report_path(config: dict[str, Any]) -> Path:
    return config_report_path(config, "release_manifest", "release_manifest.json")


def optional_existing_path(value: Any) -> Path | None:
    if not value:
        return None
    return root_path(str(value))


def artifact_record(label: str, path: Path | None, *, required: bool = False) -> dict[str, Any]:
    record: dict[str, Any] = {"label": label, "path": rel(path) if path else None, "required": required, "exists": bool(path and path.exists())}
    if path and path.exists() and path.is_file():
        record.update({"bytes": path.stat().st_size, "sha256": sha256_file(path)})
    return record


def default_release_manifest_artifacts(config: dict[str, Any], config_path: Path) -> list[tuple[str, Path | None, bool]]:
    outputs = config.get("production_outputs", {})
    artifacts: list[tuple[str, Path | None, bool]] = [
        ("package_config", config_path, True),
        ("source_pdf", optional_existing_path(config.get("source_pdf")), True),
        ("source_full_ru", optional_existing_path(outputs.get("source_full_ru")), False),
        ("keeper_markdown", optional_existing_path(outputs.get("keeper_markdown")), False),
        ("production_html", optional_existing_path(outputs.get("html")), False),
        ("production_pdf", optional_existing_path(outputs.get("pdf")), False),
        ("production_html_report", production_html_report_path(config), False),
        ("coverage_gate_report", coverage_gate_report_path(config), False),
        ("critical_remediation_gate_report", critical_remediation_report_path(config), False),
        ("release_qa_report", release_qa_report_path(config), False),
        ("approval_ledger", approval_ledger_report_path(config), False),
        ("approval_ledger_qa", approval_ledger_qa_path(config), False),
        ("art_layout_qa", art_layout_qa_report_path(config), False),
        ("pdf_print_qa", pdf_print_qa_report_path(config), False),
    ]
    for item in config.get("release_manifest", {}).get("artifacts", []):
        if isinstance(item, dict):
            artifacts.append((str(item.get("label") or item.get("path")), optional_existing_path(item.get("path")), bool(item.get("required", False))))
    return artifacts


def build_release_manifest(config_path: Path, *, check_only: bool = False) -> dict[str, Any]:
    config = read_json(config_path)
    manifest_cfg = config.get("release_manifest", {})
    report = release_manifest_report_path(config)
    records = [artifact_record(label, path, required=required) for label, path, required in default_release_manifest_artifacts(config, config_path)]
    required_labels = set(str(item) for item in manifest_cfg.get("require_existing", []))
    findings: list[dict[str, Any]] = []
    warnings: list[dict[str, Any]] = []
    for record in records:
        required = bool(record["required"] or record["label"] in required_labels)
        record["required"] = required
        if required and not record["exists"]:
            findings.append({"code": "missing_required_release_artifact", "label": record["label"], "path": record["path"]})
        elif not record["exists"]:
            warnings.append({"code": "missing_optional_release_artifact", "label": record["label"], "path": record["path"]})
    result = {
        "schema": "translator_release_manifest.v1",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "config": rel(config_path),
        "status": "blocked" if findings else "pass",
        "action": "check_only" if check_only else "written",
        "artifacts": records,
        "counts": {
            "artifacts": len(records),
            "existing": sum(1 for item in records if item["exists"]),
            "findings": len(findings),
            "warnings": len(warnings),
        },
        "findings": findings,
        "warnings": warnings,
        "approval_state": production_approval_state(config),
    }
    if not check_only:
        write_json(report, result)
    else:
        write_json(report, result)
    return result


def production_art_layout_config(config: dict[str, Any]) -> dict[str, Any]:
    return config.get("production_art_layout", {})


def art_layout_qa_report_path(config: dict[str, Any]) -> Path:
    return config_report_path(config, "production_art_layout", "art_layout_qa.json")


def art_layout_manifest_path(config: dict[str, Any]) -> Path:
    art = production_art_layout_config(config)
    value = art.get("art_manifest", "art_manifest.json")
    path = Path(str(value).replace("/", "\\"))
    return path.resolve() if path.is_absolute() else qa_root(config) / path


def art_layout_integration_manifest_path(config: dict[str, Any]) -> Path:
    art = production_art_layout_config(config)
    value = art.get("integration_manifest", "art_html_integration_manifest.json")
    path = Path(str(value).replace("/", "\\"))
    return path.resolve() if path.is_absolute() else qa_root(config) / path


def preserved_art_as_placements(config: dict[str, Any]) -> list[dict[str, Any]]:
    placements: list[dict[str, Any]] = []
    for item in art_integration_config(config).get("preserved_page_art", []):
        page = str(item.get("page") or "").zfill(3)
        role = str(item.get("role") or "source_image")
        bbox = item.get("crop_box")
        placements.append(
            {
                "asset_id": item.get("target_filename") or f"page-{page}-{role}",
                "page_id": page,
                "asset_path": item.get("target_filename"),
                "placement": item.get("placement") or "page_art_after_heading",
                "css_class": item.get("css_class") or "art-full-width",
                "break_policy": item.get("break_policy") or "keep_with_page_text",
                "semantic_role": role,
                "source_kind": "page_render_crop" if bbox else "page_render_full_page",
                "asset_form": "runtime_image",
                "crop_kind": "clean_crop" if bbox else "full_page",
                "content_risk": item.get("content_risk") or "source_visual",
                "production_role": role,
                "decision_state": item.get("decision_state") or "accepted_for_review",
                "approval_label": item.get("approval_label") or "",
                "source_render": item.get("source_render") or f"page-{page}.png",
                "source_bbox_or_full_page": bbox or "full_page",
                "text_contamination_policy": item.get("text_contamination_policy") or "preserve_as_source_art",
                "visual_review_required": bool(item.get("visual_review_required", False)),
                "visual_review_status": item.get("visual_review_status") or "pending" if item.get("visual_review_required") else "not_required",
                "forbidden_source_text_regions": item.get("forbidden_source_text_regions") or [],
                "protected_blocks": item.get("protected_blocks") or [],
            }
        )
    return placements


def canonical_art_placements_as_layout(manifest: dict[str, Any], config: dict[str, Any] | None = None) -> list[dict[str, Any]]:
    """Adapt the canonical selection contract to the existing layout-QA shape."""

    placement_map = {
        "after_heading": "page_art_after_heading",
        "before_first_paragraph": "flow_art_before_first_paragraph",
        "replace_visual_page": "replace_visual_page",
        "before_page_anchor": "replace_visual_page",
    }
    result: list[dict[str, Any]] = []
    for item in manifest.get("placements", []):
        if not isinstance(item, dict) or str(item.get("decision_state") or "") not in {"approved", "accepted", "selected"}:
            continue
        source_kind = str(item.get("source_kind") or "")
        full_page = bool(item.get("allow_full_page_art"))
        css_class = promote_frontmatter_art_class(
            config or {},
            item,
            "art-full-width" if item.get("semantic_role") in {"map", "floorplan", "handout"} else str(item.get("css_class") or "art-inline"),
        )
        result.append(
            {
                "asset_id": item.get("runtime_filename") or item.get("asset_id"),
                "asset_path": item.get("runtime_filename"),
                "runtime_filename": item.get("runtime_filename"),
                "page_id": str(item.get("source_page") or "").zfill(3),
                "placement": placement_map.get(str(item.get("insertion_rule") or ""), "page_art_after_heading"),
                "css_class": css_class,
                "break_policy": "keep_with_page_text",
                "semantic_role": item.get("semantic_role"),
                "source_kind": source_kind,
                "source_xref": item.get("source_xref"),
                "source_asset_sha256": item.get("source_asset_sha256"),
                "asset_form": "runtime_image",
                "crop_kind": "full_page" if full_page else ("extracted_asset" if source_kind == "extracted_asset" else "clean_crop"),
                "content_risk": "source_visual",
                "production_role": item.get("semantic_role"),
                "decision_state": item.get("decision_state"),
                "source_render": item.get("source_render") or item.get("source_asset_path"),
                "source_bbox_or_full_page": "full_page" if full_page else item.get("crop_box") or "extracted_asset",
                "text_contamination_policy": "preserve_as_source_art",
                "visual_review_required": item.get("visual_review_status") not in {"approved", "not_required"},
                "visual_review_status": item.get("visual_review_status") or "pending",
                "target_heading_id": item.get("heading_id"),
            }
        )
    return result


def boxes_intersect(a: list[int] | tuple[int, int, int, int], b: list[int] | tuple[int, int, int, int]) -> bool:
    ax0, ay0, ax1, ay1 = [int(value) for value in a]
    bx0, by0, bx1, by1 = [int(value) for value in b]
    return ax0 < bx1 and ax1 > bx0 and ay0 < by1 and ay1 > by0


def html_has_image_ref_for_stem(image_refs: list[str], filename: str) -> bool:
    stem = Path(filename).stem
    return any(Path(normalize_ref(ref)).name.startswith(stem) for ref in image_refs)


def html_image_path_for_stem(html_path: Path, image_refs: list[str], filename: str) -> Path | None:
    stem = Path(filename).stem
    for ref in image_refs:
        normalized = normalize_ref(ref)
        if Path(normalized).name.startswith(stem):
            return (html_path.parent / normalized.replace("/", "\\")).resolve()
    return None


def art_layout_image_ref_findings(html_path: Path, image_refs: list[str]) -> list[dict[str, Any]]:
    findings: list[dict[str, Any]] = []
    for ref in image_refs:
        normalized = normalize_ref(ref)
        target = (html_path.parent / normalized.replace("/", "\\")).resolve()
        if not target.exists():
            findings.append({"code": "html_image_ref_missing_file", "src": ref, "path": rel(target)})
            continue
        try:
            with Image.open(target) as image:
                image_format = str(image.format or "").upper()
                width, height = image.size
                image.verify()
        except Exception as exc:
            findings.append({"code": "html_image_ref_not_decodable", "src": ref, "path": rel(target), "message": str(exc)})
            continue
        suffix = target.suffix.lower()
        expected_format = {
            ".png": "PNG",
            ".jpg": "JPEG",
            ".jpeg": "JPEG",
            ".webp": "WEBP",
            ".gif": "GIF",
        }.get(suffix)
        if expected_format and image_format != expected_format:
            findings.append(
                {
                    "code": "html_image_ref_extension_format_mismatch",
                    "src": ref,
                    "path": rel(target),
                    "extension": suffix,
                    "actual_format": image_format,
                    "expected_format": expected_format,
                }
            )
        if width <= 0 or height <= 0:
            findings.append({"code": "html_image_ref_empty_dimensions", "src": ref, "path": rel(target), "width": width, "height": height})
    return findings


def preserved_runtime_target(config: dict[str, Any], role: str, filename: str) -> Path:
    return target_dir_for_image_role(config, role) / safe_filename(filename)


def art_layout_required_asset_findings(
    config: dict[str, Any],
    *,
    html_path: Path,
    placements: list[dict[str, Any]],
    image_refs: list[str],
) -> list[dict[str, Any]]:
    art = production_art_layout_config(config)
    findings: list[dict[str, Any]] = []
    by_asset = {str(item.get("asset_id") or item.get("asset_path") or ""): item for item in placements}
    for item in art.get("required_assets", []):
        if not isinstance(item, dict):
            continue
        filename = str(item.get("target_filename") or item.get("asset_id") or "").strip()
        role = str(item.get("role") or item.get("production_role") or "source_image")
        if not filename:
            findings.append({"code": "required_art_asset_missing_filename", "item": item})
            continue
        placement = by_asset.get(filename)
        if placement is None:
            findings.append({"code": "missing_required_art_placement", "asset_id": filename, "page": item.get("page"), "role": role})
        elif isinstance(item.get("expected_crop_box"), list) and len(item.get("expected_crop_box")) == 4:
            expected = [int(value) for value in item["expected_crop_box"]]
            tolerance = int(item.get("crop_tolerance_px", art.get("default_crop_tolerance_px", 12)) or 0)
            bbox = placement.get("source_bbox_or_full_page")
            try:
                actual = [int(value) for value in bbox]
            except (TypeError, ValueError):
                findings.append({"code": "required_art_expected_crop_unavailable", "asset_id": filename, "expected_crop_box": expected, "actual_crop_box": bbox})
            else:
                deltas = [abs(actual[index] - expected[index]) for index in range(4)]
                if len(actual) != 4 or any(delta > tolerance for delta in deltas):
                    findings.append(
                        {
                            "code": "required_art_crop_box_mismatch",
                            "asset_id": filename,
                            "expected_crop_box": expected,
                            "actual_crop_box": actual,
                            "crop_tolerance_px": tolerance,
                            "deltas": deltas,
                        }
                    )
        html_ref_path = html_image_path_for_stem(html_path, image_refs, filename)
        if item.get("require_html_ref", True) and html_ref_path is None:
            findings.append({"code": "missing_required_art_html_ref", "asset_id": filename})
        if item.get("require_runtime_file", True):
            try:
                target = html_ref_path or preserved_runtime_target(config, role, filename)
            except ValueError as exc:
                findings.append({"code": "required_art_asset_bad_filename", "asset_id": filename, "message": str(exc)})
                continue
            if not target.exists():
                findings.append({"code": "missing_required_art_runtime_file", "asset_id": filename, "path": rel(target)})
                continue
            min_width = int(item.get("min_width", 0) or 0)
            min_height = int(item.get("min_height", 0) or 0)
            if min_width or min_height:
                with Image.open(target) as image:
                    width, height = image.size
                if width < min_width or height < min_height:
                    findings.append(
                        {
                            "code": "required_art_runtime_file_too_small",
                            "asset_id": filename,
                            "path": rel(target),
                            "width": width,
                            "height": height,
                            "min_width": min_width,
                            "min_height": min_height,
                        }
                    )
    return findings


def art_layout_approval_identity_findings(
    config: dict[str, Any],
    *,
    placements: list[dict[str, Any]],
    image_refs: list[str],
) -> list[dict[str, Any]]:
    """Bind approved extracted assets to canonical placements and HTML refs."""

    approval_path = image_role_approval_path(config)
    if not approval_path.exists():
        return []
    approval = read_json(approval_path)
    selected = [
        item
        for item in placements
        if isinstance(item, dict) and str(item.get("decision_state") or "").casefold() in {"approved", "accepted", "selected"}
    ]
    findings: list[dict[str, Any]] = []
    excluded_xrefs = {int(value) for value in art_integration_config(config).get("excluded_xrefs", [])}
    for approved in approval.get("items", []):
        if not isinstance(approved, dict) or approved.get("decision_state") != "approved":
            continue
        role = str(approved.get("target_role") or "")
        if role not in IMAGE_COPY_ROLES or approved.get("placement_required") is False:
            continue
        xref = approved.get("xref")
        if xref is not None and int(xref) in excluded_xrefs:
            continue
        filename = str(approved.get("target_filename") or "").strip()
        page = str(approved.get("pages", [""])[0] if approved.get("pages") else "").zfill(3)
        fallback = any(
            str(item.get("page_id") or item.get("source_page") or "").zfill(3) == page
            and str(item.get("source_kind") or "").startswith("page_render")
            for item in selected
        )
        matches = [
            placement
            for placement in selected
            if (xref is not None and str(placement.get("source_xref")) == str(xref))
            or (filename and str(placement.get("runtime_filename") or placement.get("asset_path") or "") == filename)
        ]
        if not matches:
            findings.append(
                {
                    "code": "orphaned_approved_art_with_page_render_fallback" if fallback else "approved_art_missing_placement",
                    "xref": xref,
                    "runtime_filename": filename,
                    "role": role,
                    "page": page,
                }
            )
            continue
        placement = matches[0]
        placement_filename = str(placement.get("runtime_filename") or placement.get("asset_path") or "")
        if filename and placement_filename != filename:
            findings.append(
                {
                    "code": "approved_art_runtime_identity_mismatch",
                    "xref": xref,
                    "approved_runtime_filename": filename,
                    "placement_runtime_filename": placement_filename,
                }
            )
        approved_hash = str(approved.get("sha256") or "")
        placement_hash = str(placement.get("source_asset_sha256") or "")
        if approved_hash and placement_hash != approved_hash:
            findings.append(
                {
                    "code": "approved_art_source_identity_mismatch",
                    "xref": xref,
                    "approved_sha256": approved_hash,
                    "placement_sha256": placement_hash or None,
                }
            )
        if filename and not html_has_image_ref_for_stem(image_refs, filename):
            findings.append(
                {
                    "code": "orphaned_approved_art_with_page_render_fallback" if fallback else "approved_art_missing_html_ref",
                    "xref": xref,
                    "runtime_filename": filename,
                    "page": page,
                }
            )
    return findings


def art_layout_crop_findings(config: dict[str, Any], placements: list[dict[str, Any]]) -> list[dict[str, Any]]:
    art = production_art_layout_config(config)
    findings: list[dict[str, Any]] = []
    min_by_role = {
        str(role): [int(values[0]), int(values[1])]
        for role, values in dict(art.get("min_crop_dimensions_by_role", {})).items()
        if isinstance(values, list) and len(values) >= 2
    }
    forbidden_regions = [item for item in art.get("forbidden_crop_regions", []) if isinstance(item, dict)]
    for placement in placements:
        asset_id = str(placement.get("asset_id") or placement.get("asset_path") or "unnamed_asset")
        role = str(placement.get("production_role") or placement.get("semantic_role") or "")
        bbox = placement.get("source_bbox_or_full_page")
        if not isinstance(bbox, list) or len(bbox) != 4:
            continue
        try:
            crop = [int(value) for value in bbox]
        except (TypeError, ValueError):
            findings.append({"code": "art_crop_box_not_numeric", "asset_id": asset_id, "crop_box": bbox})
            continue
        crop_width = crop[2] - crop[0]
        crop_height = crop[3] - crop[1]
        min_dims = min_by_role.get(role)
        if min_dims:
            min_width, min_height = min_dims
            if crop_width < min_width or crop_height < min_height:
                findings.append(
                    {
                        "code": "art_crop_dimensions_too_small",
                        "asset_id": asset_id,
                        "role": role,
                        "crop_width": crop_width,
                        "crop_height": crop_height,
                        "min_width": min_width,
                        "min_height": min_height,
                    }
                )
        page = str(placement.get("page_id") or "").zfill(3)
        for region in forbidden_regions:
            region_page = str(region.get("page") or "").zfill(3)
            if region_page and region_page != page:
                continue
            region_box = region.get("box")
            if not isinstance(region_box, list) or len(region_box) != 4:
                continue
            if boxes_intersect(crop, [int(value) for value in region_box]):
                findings.append(
                    {
                        "code": "art_crop_intersects_forbidden_region",
                        "asset_id": asset_id,
                        "page": page,
                        "region": region.get("name") or "forbidden_region",
                        "crop_box": crop,
                        "region_box": region_box,
                    }
                )
    return findings


def run_art_layout_qa(config_path: Path, *, check_only: bool = False) -> dict[str, Any]:
    config = read_json(config_path)
    art = production_art_layout_config(config)
    report = art_layout_qa_report_path(config)
    manifest_path = art_placement_manifest_path(config) or art_layout_manifest_path(config)
    integration_path = art_layout_integration_manifest_path(config)
    html_path = root_path(str(config.get("production_outputs", {}).get("html") or production_html_config(config).get("output_html")))
    findings: list[dict[str, Any]] = []
    warnings: list[dict[str, Any]] = []
    placements: list[dict[str, Any]] = []
    if manifest_path.exists():
        manifest = read_json(manifest_path)
        placements = (
            canonical_art_placements_as_layout(manifest, config)
            if manifest.get("schema") == "translator_art_placement_manifest.v1"
            else list(manifest.get("placements", []))
        )
        if manifest.get("status") not in {None, "pass", "warning"}:
            findings.append({"code": "art_manifest_not_pass", "status": manifest.get("status"), "path": rel(manifest_path)})
    elif art.get("require_manifest", False):
        findings.append({"code": "missing_art_manifest", "path": rel(manifest_path)})
    else:
        placements = preserved_art_as_placements(config)
        warnings.append({"code": "using_preserved_page_art_as_manifest_candidates", "count": len(placements)})
    if art.get("require_integration_manifest", False) and not integration_path.exists():
        findings.append({"code": "missing_art_integration_manifest", "path": rel(integration_path)})
    html_text = html_path.read_text(encoding="utf-8") if html_path.exists() else ""
    if not html_path.exists():
        findings.append({"code": "missing_production_html", "path": rel(html_path)})
    image_refs = html_refs(html_text)
    findings.extend(art_layout_image_ref_findings(html_path, image_refs) if html_path.exists() else [])
    if package_has_visual_art_contract(config):
        findings.extend(canonical_art_placement_findings(config))
    findings.extend(art_layout_required_asset_findings(config, html_path=html_path, placements=placements, image_refs=image_refs))
    findings.extend(art_layout_approval_identity_findings(config, placements=placements, image_refs=image_refs))
    findings.extend(art_layout_crop_findings(config, placements))
    allowed_placements = set(art.get("allowed_placements", []))
    required_fields = [
        "placement",
        "css_class",
        "break_policy",
        "semantic_role",
        "source_kind",
        "asset_form",
        "crop_kind",
        "production_role",
        "decision_state",
        "source_render",
        "source_bbox_or_full_page",
        "text_contamination_policy",
    ]
    placement_checks: list[dict[str, Any]] = []
    for placement in placements:
        asset_id = str(placement.get("asset_id") or placement.get("asset_path") or "unnamed_asset")
        missing = [
            field
            for field in required_fields
            if placement.get(field) is None or placement.get(field) == "" or placement.get(field) == []
        ]
        if missing:
            findings.append({"code": "art_placement_missing_required_fields", "asset_id": asset_id, "fields": missing})
        placement_name = str(placement.get("placement") or "")
        if allowed_placements and placement_name and placement_name not in allowed_placements:
            findings.append({"code": "art_placement_not_allowed", "asset_id": asset_id, "placement": placement_name})
        if art.get("require_break_policy", True) and not placement.get("break_policy"):
            findings.append({"code": "art_break_policy_missing", "asset_id": asset_id})
        if art.get("require_text_contamination_policy", True) and not placement.get("text_contamination_policy"):
            findings.append({"code": "art_text_contamination_policy_missing", "asset_id": asset_id})
        if str(placement.get("asset_path") or "").lower().endswith((".jp2", ".jpx")):
            findings.append({"code": "raw_jp2_in_production_art", "asset_id": asset_id})
        if placement.get("visual_review_required") and placement.get("visual_review_status") not in {"approved_clean", "approved_for_review", "approved_full_page"}:
            findings.append({"code": "art_visual_review_not_approved", "asset_id": asset_id, "status": placement.get("visual_review_status")})
        placement_checks.append({"asset_id": asset_id, "missing_fields": missing, "placement": placement_name, "css_class": placement.get("css_class")})
    visible_text = strip_html_tags(re.sub(r"<!--[\s\S]*?-->", " ", html_text))
    technical_hits = re.findall(r"(?:\.jp2|\.jpx|p\d{3}[_-]occ\d+|data-art-asset|source-render)", visible_text, re.I)
    if technical_hits:
        findings.append({"code": "technical_art_text_visible", "hits": sorted(set(technical_hits))[:20]})
    result = {
        "schema": "translator_art_layout_qa.v1",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "config": rel(config_path),
        "status": "blocked" if findings else "pass",
        "action": "check_only" if check_only else "checked",
        "html": rel(html_path),
        "hashes": {"html_sha256": sha256_file(html_path)} if html_path.exists() else {},
        "art_manifest": rel(manifest_path),
        "integration_manifest": rel(integration_path),
        "counts": {
            "placements": len(placements),
            "html_image_refs": len(image_refs),
            "findings": len(findings),
            "warnings": len(warnings),
        },
        "placement_checks": placement_checks,
        "findings": findings,
        "warnings": warnings,
        "approval_state": {"production_art_layout_passed": not findings, "production_approved": False},
    }
    write_json(report, result)
    return result


def pdf_print_qa_config(config: dict[str, Any]) -> dict[str, Any]:
    return config.get("pdf_print_qa", {})


def pdf_print_qa_report_path(config: dict[str, Any], variant: str | None = None) -> Path:
    qa_cfg = pdf_print_qa_config(config)
    if variant:
        reports = qa_cfg.get("variant_reports", {})
        if isinstance(reports, dict) and reports.get(variant):
            value = reports[variant]
        else:
            base = str(qa_cfg.get("report", "pdf_print_qa.json"))
            stem = Path(base).stem
            suffix = Path(base).suffix or ".json"
            value = f"{stem}_{variant}{suffix}"
        path = Path(str(value).replace("/", "\\"))
        return path.resolve() if path.is_absolute() else qa_root(config) / path
    return config_report_path(config, "pdf_print_qa", "pdf_print_qa.json")


def pdf_print_run_report_path(config: dict[str, Any], variant: str | None = None) -> Path:
    pdf_cfg = production_pdf_config(config)
    value = pdf_cfg.get("print_run_report")
    if not value:
        value = f"pdf_print_run_{variant}.json" if variant else "pdf_print_run.json"
    path = Path(str(value).replace("/", "\\"))
    return path.resolve() if path.is_absolute() else qa_root(config) / path


def production_pdf_temp_root(config: dict[str, Any]) -> Path:
    value = production_pdf_config(config).get("temp_root")
    if value:
        return root_path(str(value))
    workbench_root = config.get("workbench_root")
    if workbench_root:
        return root_path(str(workbench_root)) / "Temp" / "Production_PDF"
    project_key = safe_filename(str(config.get("project_key") or "package"))
    return Path(tempfile.gettempdir()).resolve() / "nri_translator_production_pdf" / project_key


def make_production_pdf_temp_dir(temp_root: Path) -> Path:
    for _ in range(20):
        temp_dir = temp_root / f"run_{uuid.uuid4().hex[:8]}"
        try:
            temp_dir.mkdir(parents=False, exist_ok=False)
            probe = temp_dir / ".write_probe"
            probe.write_text("ok", encoding="utf-8")
            probe.unlink()
            return temp_dir
        except FileExistsError:
            continue
        except OSError:
            try:
                if temp_dir.exists():
                    shutil.rmtree(temp_dir)
            except OSError:
                pass
            raise
    raise FileExistsError(f"Could not create a unique production PDF temp directory under {temp_root}")


def remove_production_pdf_temp_dir(
    temp_dir: Path,
    *,
    attempts: int = 120,
    retry_delay_seconds: float = 0.25,
) -> int:
    """Remove a browser profile after delayed Windows child-process shutdown."""
    if attempts < 1:
        raise ValueError("production PDF temp cleanup attempts must be positive")
    for attempt in range(1, attempts + 1):
        try:
            shutil.rmtree(temp_dir)
            return attempt
        except OSError:
            if not temp_dir.exists():
                return attempt
            if attempt == attempts:
                raise
            time.sleep(retry_delay_seconds)
    raise AssertionError("unreachable production PDF temp cleanup state")


def collect_pdf_page_metrics(pdf: Path) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    metrics: list[dict[str, Any]] = []
    warnings: list[dict[str, Any]] = []
    try:
        import fitz  # PyMuPDF

        with fitz.open(pdf) as doc:
            for index, page in enumerate(doc, start=1):
                text = page.get_text("text") or ""
                pix = page.get_pixmap(matrix=fitz.Matrix(0.35, 0.35), alpha=False)
                image = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
                gray = image.convert("L")
                bbox = gray.point(lambda value: 0 if value > 246 else 255).getbbox()
                total = pix.width * pix.height
                if bbox:
                    left, top, right, bottom = bbox
                    content_area = max(0, right - left) * max(0, bottom - top)
                    blank_bottom_ratio = max(0.0, (pix.height - bottom) / pix.height)
                else:
                    content_area = 0
                    blank_bottom_ratio = 1.0
                ink_ratio = content_area / total if total else 0.0
                text_chars = len(pdf_token_text(text))
                record = {
                    "page": index,
                    "text_chars": text_chars,
                    "ink_bbox_ratio": round(ink_ratio, 5),
                    "blank_bottom_ratio": round(blank_bottom_ratio, 5),
                }
                metrics.append(record)
    except Exception as exc:
        warnings.append({"code": "pdf_page_occupancy_metrics_failed", "message": str(exc)})
    return metrics, warnings


def valid_cached_pdf_processing(value: Any) -> bool:
    if not isinstance(value, dict) or not isinstance(value.get("text"), str):
        return False
    if value.get("error") is not None and not isinstance(value.get("error"), dict):
        return False
    if not isinstance(value.get("warnings"), list) or not all(isinstance(item, dict) for item in value["warnings"]):
        return False
    metrics = value.get("page_metrics")
    return isinstance(metrics, list) and all(
        isinstance(item, dict)
        and isinstance(item.get("page"), int)
        and isinstance(item.get("text_chars"), int)
        and isinstance(item.get("ink_bbox_ratio"), (int, float))
        and isinstance(item.get("blank_bottom_ratio"), (int, float))
        for item in metrics
    )


def cached_pdf_processing(
    config: dict[str, Any],
    pdf: Path,
    *,
    variant: str | None,
    telemetry: dict[str, int],
) -> dict[str, Any]:
    """Load one hash-bound PDF text/metrics record without caching a gate verdict."""

    started = time.monotonic_ns()
    tool = pdftotext_path(config)
    if not pdf.exists() or not tool.exists():
        telemetry["misses"] += 1
        telemetry["duration_ms"] += cache_duration_ms(started)
        return {
            "text": "",
            "error": {"code": "missing_pdftotext_or_pdf"},
            "warnings": [],
            "page_metrics": [],
        }
    input_hashes = {"pdf_sha256": sha256_file(pdf)}
    options = {
        "variant": variant,
        "pdftotext": executable_identity(tool, version=str(tooling_config(config).get("pdftotext_version") or "unavailable")),
        "command": ["-layout", "-enc", "UTF-8", "-"],
        "metrics": "pymupdf_0.35_grayscale_threshold_246_v1",
    }
    cache = processing_cache(config)
    lookup = cache.get("pdf_processing", input_hashes, options)
    if lookup.hit and valid_cached_pdf_processing(lookup.value):
        telemetry["hits"] += 1
        telemetry["duration_ms"] += cache_duration_ms(started)
        return lookup.value

    telemetry["misses"] += 1
    completed = subprocess.run(
        [str(tool), "-layout", "-enc", "UTF-8", str(pdf), "-"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=120,
        check=False,
    )
    error = None
    if completed.returncode != 0:
        error = {
            "code": "pdftotext_failed",
            "returncode": completed.returncode,
            "stderr": diagnostic_lines(completed.stderr.strip().splitlines()),
        }
    page_metrics, metric_warnings = collect_pdf_page_metrics(pdf)
    value = {
        "text": completed.stdout,
        "error": error,
        "warnings": metric_warnings,
        "page_metrics": page_metrics,
    }
    cache.put("pdf_processing", input_hashes, options, value)
    telemetry["duration_ms"] += cache_duration_ms(started)
    return value


def pdf_page_occupancy_metrics(
    config: dict[str, Any],
    cached_metrics: list[dict[str, Any]],
    *,
    variant: str | None = None,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    metrics: list[dict[str, Any]] = []
    findings: list[dict[str, Any]] = []
    warnings: list[dict[str, Any]] = []
    qa_cfg = pdf_print_qa_config(config).get("near_empty_page_policy", {})
    if not isinstance(qa_cfg, dict) or not qa_cfg.get("enabled", True):
        return metrics, findings, warnings
    min_ink_ratio = float(qa_cfg.get("min_ink_ratio", 0.012))
    min_text_chars = int(qa_cfg.get("min_text_chars", 80))
    max_blank_bottom_ratio = float(qa_cfg.get("max_blank_bottom_ratio", 0.58))
    fail_on_unexpected = bool(qa_cfg.get("fail_on_unexpected", False))
    for source_record in cached_metrics:
        record = dict(source_record)
        near_empty = record["ink_bbox_ratio"] < min_ink_ratio and record["text_chars"] < min_text_chars
        half_empty = record["blank_bottom_ratio"] > max_blank_bottom_ratio and record["text_chars"] >= min_text_chars
        record.update({"near_empty": near_empty, "half_empty": half_empty})
        metrics.append(record)
        if near_empty or half_empty:
            item = {
                "code": "near_empty_pdf_page" if near_empty else "half_empty_pdf_page",
                "variant": variant,
                **record,
            }
            if fail_on_unexpected:
                findings.append(item)
            else:
                warnings.append(item)
    return metrics, findings, warnings


def run_pdf_print_qa(config_path: Path, *, check_only: bool = False, variant: str | None = None) -> dict[str, Any]:
    config = read_json(config_path)
    qa_cfg = pdf_print_qa_config(config)
    html = production_pdf_html_path(config)
    pdf = production_pdf_target_path(config, variant)
    report = pdf_print_qa_report_path(config, variant)
    print_report = production_pdf_report_path(config, variant)
    findings: list[dict[str, Any]] = []
    warnings: list[dict[str, Any]] = []
    checks: dict[str, Any] = {}
    telemetry = cache_telemetry()
    page_metrics: list[dict[str, Any]] = []
    if not html.exists():
        findings.append({"code": "missing_html", "path": rel(html)})
    if not pdf.exists() or pdf.stat().st_size == 0:
        findings.append({"code": "missing_or_empty_pdf", "path": rel(pdf)})
        text = ""
        meta = None
    else:
        try:
            meta = pdf_metadata(pdf)
        except Exception as exc:
            meta = None
            findings.append({"code": "pdf_metadata_failed", "message": str(exc)})
        pdf_processing = cached_pdf_processing(config, pdf, variant=variant, telemetry=telemetry)
        text = str(pdf_processing["text"])
        if pdf_processing["error"]:
            warnings.append(pdf_processing["error"])
        warnings.extend(pdf_processing["warnings"])
        page_metrics, occupancy_findings, occupancy_warnings = pdf_page_occupancy_metrics(
            config, pdf_processing["page_metrics"], variant=variant
        )
        findings.extend(occupancy_findings)
        warnings.extend(occupancy_warnings)
    html_sha = sha256_file(html) if html.exists() else None
    html_text = html.read_text(encoding="utf-8") if html.exists() else ""
    pdf_sha = sha256_file(pdf) if pdf.exists() and pdf.stat().st_size > 0 else None
    print_run = read_json(print_report) if print_report.exists() else {}
    variant_cfg = print_run.get("variant_config", {}) if isinstance(print_run.get("variant_config", {}), dict) else {}
    command = print_run.get("engine_command") or []
    command_text = " ".join(str(part) for part in command)
    variant_html_text = ""
    variant_html_path: Path | None = None
    for part in command:
        value = str(part)
        if not value.lower().endswith(".html"):
            continue
        if value.startswith("file:///"):
            variant_html_path = Path(unquote(value[8:]))
        else:
            variant_html_path = Path(value)
        break
    if variant_html_path and variant_html_path.exists():
        try:
            variant_html_text = variant_html_path.read_text(encoding="utf-8")
        except Exception as exc:
            warnings.append({"code": "variant_html_unreadable", "path": rel(variant_html_path), "message": str(exc)})
    header_footer_disabled = "--no-pdf-header-footer" in command_text or print_run.get("print_policy", {}).get("header_footer") == "disabled"
    checks["header_footer_disabled"] = header_footer_disabled
    if qa_cfg.get("require_header_footer_disabled", True) and not header_footer_disabled:
        findings.append({"code": "pdf_header_footer_not_disabled", "print_report": rel(print_report)})
    checks["current_html_hash_recorded"] = bool(html_sha and print_run.get("source_html_sha256") == html_sha)
    if qa_cfg.get("require_current_html_hash", True) and print_report.exists() and not checks["current_html_hash_recorded"]:
        findings.append({"code": "pdf_not_recorded_against_current_html_hash", "print_report": rel(print_report)})
    if not print_report.exists():
        warnings.append({"code": "missing_production_pdf_report", "path": rel(print_report)})
    min_text_chars = int(qa_cfg.get("min_text_chars", 1000))
    checks["pdf_text_extract_nonempty"] = len(pdf_token_text(text)) >= min_text_chars
    if pdf.exists() and not checks["pdf_text_extract_nonempty"]:
        findings.append({"code": "pdf_text_extract_too_sparse", "chars": len(pdf_token_text(text)), "min_chars": min_text_chars})
    forbidden_visible = [item for item in ["file:///", ".html", "pdf-page-", "data-art-asset"] if item in text]
    checks["no_technical_text_visible"] = not forbidden_visible
    if forbidden_visible:
        findings.append({"code": "pdf_technical_text_visible", "hits": forbidden_visible})
    if variant_cfg.get("layout_mode") == "page_flow_columns":
        checks["page_flow_columns_layout_mode"] = True
        saved_variant_policy_checks = print_run.get("variant_html_policy_checks", {})
        if not isinstance(saved_variant_policy_checks, dict):
            saved_variant_policy_checks = {}
        if variant_html_text:
            broad_display_contents = bool(
                re.search(
                    r'body\.pdf-layout-page-flow-columns\s+\.production-page\s*\{[^}]*display:\s*contents\s*!important',
                    variant_html_text,
                    re.I,
                )
            )
            scoped_display_contents = bool(
                re.search(
                    r'body\.pdf-layout-page-flow-columns\s+\.production-page:not\([^}]*display:\s*contents\s*!important',
                    variant_html_text,
                    re.I,
                )
            )
            special_page_block_display = all(
                token in variant_html_text
                for token in [
                    ".production-page.page-type-credits",
                    ".production-page.page-type-source-toc",
                    ".production-page.page-type-quote-art",
                    "display: block !important",
                    "column-span: all !important",
                ]
            )
            checks["page_flow_columns_display_contents_scoped"] = scoped_display_contents and not broad_display_contents
            checks["page_flow_columns_special_pages_block_display"] = special_page_block_display
            checks["page_flow_columns_cover_full_page_art_css"] = bool(
                re.search(
                    r'body\.pdf-layout-page-flow-columns\s+\.production-page\.page-type-cover\s+figure[^{]*\{[^}]*column-span:\s*all\s*!important[^}]*width:\s*100%\s*!important',
                    variant_html_text,
                    re.I | re.S,
                )
                and re.search(
                    r'body\.pdf-layout-page-flow-columns\s+\.production-page\.page-type-cover\s+figure\s+img[^{]*\{[^}]*max-height:\s*252mm\s*!important',
                    variant_html_text,
                    re.I | re.S,
                )
            )
            if broad_display_contents or not scoped_display_contents:
                findings.append({"code": "page_flow_columns_unscoped_display_contents", "variant": variant})
            if not special_page_block_display:
                findings.append({"code": "page_flow_columns_special_pages_not_protected", "variant": variant})
            if not checks["page_flow_columns_cover_full_page_art_css"]:
                findings.append({"code": "page_flow_columns_cover_art_not_protected", "variant": variant})
        elif saved_variant_policy_checks:
            checks["page_flow_columns_display_contents_scoped"] = bool(
                saved_variant_policy_checks.get("display_contents_scoped")
            )
            checks["page_flow_columns_special_pages_block_display"] = bool(
                saved_variant_policy_checks.get("special_pages_block_display")
            )
            checks["page_flow_columns_cover_full_page_art_css"] = bool(
                saved_variant_policy_checks.get("cover_full_page_art_css")
            )
            if saved_variant_policy_checks.get("unscoped_display_contents") or not checks["page_flow_columns_display_contents_scoped"]:
                findings.append({"code": "page_flow_columns_unscoped_display_contents", "variant": variant})
            if not checks["page_flow_columns_special_pages_block_display"]:
                findings.append({"code": "page_flow_columns_special_pages_not_protected", "variant": variant})
            if not checks["page_flow_columns_cover_full_page_art_css"]:
                findings.append({"code": "page_flow_columns_cover_art_not_protected", "variant": variant})
        else:
            warnings.append({"code": "page_flow_columns_variant_html_policy_checks_missing", "variant": variant})
        checks["page_flow_columns_section_wrappers"] = variant_cfg.get("section_wrappers") == "display_contents"
        if not checks["page_flow_columns_section_wrappers"]:
            findings.append({"code": "page_flow_columns_section_wrappers_not_display_contents", "variant": variant})
        heading_policy = variant_cfg.get("heading_policy", {})
        checks["page_flow_columns_h1_span_all"] = heading_policy.get("h1") == "column_span_all"
        checks["page_flow_columns_h2_h6_inline"] = heading_policy.get("h2_h6") == "inline_column_flow"
        if not checks["page_flow_columns_h1_span_all"]:
            findings.append({"code": "page_flow_columns_h1_policy_not_span_all", "variant": variant})
        if not checks["page_flow_columns_h2_h6_inline"]:
            findings.append({"code": "page_flow_columns_h2_h6_policy_not_inline", "variant": variant})
        callout_policy = variant_cfg.get("callout_policy", {})
        checks["page_flow_columns_callouts_splittable"] = callout_policy.get("default") == "split_across_columns"
        if not checks["page_flow_columns_callouts_splittable"]:
            findings.append({"code": "page_flow_columns_callouts_not_splittable", "variant": variant})
        art_column_policy = variant_cfg.get("art_column_policy", {})
        checks["page_flow_columns_default_art_columnned"] = art_column_policy.get("default_columnned") is True
        if not checks["page_flow_columns_default_art_columnned"]:
            findings.append({"code": "page_flow_columns_default_art_not_columnned", "variant": variant})
        not_columnned_roles = {str(role) for role in art_column_policy.get("not_columnned_roles", [])}
        required_not_columnned = {"landing", "toc", "cover"}
        checks["page_flow_columns_non_columnned_art_roles"] = required_not_columnned.issubset(not_columnned_roles)
        if not checks["page_flow_columns_non_columnned_art_roles"]:
            findings.append(
                {
                    "code": "page_flow_columns_missing_non_columnned_art_roles",
                    "variant": variant,
                    "missing": sorted(required_not_columnned - not_columnned_roles),
                }
            )
        atomic_columnned_roles = {str(role) for role in art_column_policy.get("atomic_columnned_roles", [])}
        required_atomic_columnned = {"floorplan", "source_image"}
        checks["page_flow_columns_atomic_columnned_art_roles"] = required_atomic_columnned.issubset(atomic_columnned_roles)
        if not checks["page_flow_columns_atomic_columnned_art_roles"]:
            findings.append(
                {
                    "code": "page_flow_columns_missing_atomic_columnned_art_roles",
                    "variant": variant,
                    "missing": sorted(required_atomic_columnned - atomic_columnned_roles),
                }
            )
        statblock_policy = variant_cfg.get("statblock_section_policy", {})
        statblock_not_applicable = statblock_policy.get("not_applicable") is True
        statblock_heading_ids = [str(value).strip() for value in statblock_policy.get("heading_ids", []) if str(value).strip()]
        statblock_card_count = html_class_token_count(html_text, "statblock-card")
        statblock_inline = (
            statblock_policy.get("break_before") in {"none", "inline"}
            and not statblock_heading_ids
            and statblock_card_count > 0
        )
        checks["page_flow_columns_statblock_section_break"] = statblock_not_applicable or statblock_inline or (
            bool(statblock_heading_ids) and statblock_policy.get("break_before") == "page"
        )
        checks["page_flow_columns_statblock_inline"] = statblock_inline
        checks["page_flow_columns_statblock_section_break_not_applicable"] = statblock_not_applicable
        if not checks["page_flow_columns_statblock_section_break"]:
            findings.append({"code": "page_flow_columns_missing_statblock_section_break", "variant": variant})
        if statblock_heading_ids or statblock_inline:
            checks["page_flow_columns_statblock_cards"] = statblock_card_count
            if statblock_card_count <= 0:
                findings.append({"code": "page_flow_columns_missing_statblock_cards", "variant": variant})
    else:
        checks["page_flow_columns_layout_mode"] = False
    result = {
        "schema": "translator_pdf_print_qa.v1",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "config": rel(config_path),
        "status": "blocked" if findings else "pass",
        "action": "check_only" if check_only else "checked",
        "variant": variant,
        "inputs": {"html": rel(html), "pdf": rel(pdf), "production_pdf_report": rel(print_report)},
        "hashes": {"html_sha256": html_sha, "pdf_sha256": pdf_sha},
        "print_policy": {
            "route": "browser_edge_or_chromium_headless_print",
            "page_size": qa_cfg.get("page_size", "A4"),
            "background_graphics": True,
            "header_footer": "disabled" if header_footer_disabled else "unknown_or_enabled",
        },
        "counts": {
            "pdf_pages": meta.get("pages") if isinstance(meta, dict) else None,
            "pdf_text_chars": len(pdf_token_text(text)),
            "statblock_cards": checks.get("page_flow_columns_statblock_cards"),
            "near_empty_pages": sum(1 for item in page_metrics if item.get("near_empty")),
            "half_empty_pages": sum(1 for item in page_metrics if item.get("half_empty")),
            "findings": len(findings),
            "warnings": len(warnings),
        },
        "checks": checks,
        "page_occupancy": page_metrics,
        "findings": findings,
        "warnings": warnings,
        "cache": telemetry,
        "approval_state": {"production_pdf_built": not findings, "production_approved": False},
    }
    write_json(report, result)
    return result


def read_csv_rows(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def term_gate_config(config: dict[str, Any]) -> dict[str, Any]:
    return config.get("term_gate", {})


def term_gate_report_path(config: dict[str, Any]) -> Path:
    gate = term_gate_config(config)
    value = gate.get("report", "term_gate_report.json")
    path = Path(str(value).replace("/", "\\"))
    return path.resolve() if path.is_absolute() else qa_root(config) / path


def term_gate_source_path(config: dict[str, Any]) -> Path | None:
    gate = term_gate_config(config)
    value = gate.get("source_markdown")
    if value:
        return root_path(str(value))
    outputs = config.get("production_outputs", {})
    if outputs.get("source_full_ru"):
        return root_path(str(outputs["source_full_ru"]))
    return None


def term_gate_output_path(config: dict[str, Any]) -> Path | None:
    gate = term_gate_config(config)
    value = gate.get("output_markdown")
    if value:
        return root_path(str(value))
    outputs = config.get("production_outputs", {})
    if outputs.get("keeper_markdown"):
        return root_path(str(outputs["keeper_markdown"]))
    return None


def term_gate_registry_path(config: dict[str, Any]) -> Path | None:
    paths = term_gate_registry_paths(config)
    return paths[0] if paths else None


def term_gate_registry_paths(config: dict[str, Any]) -> list[Path]:
    """Return package registries while retaining the original single-registry key."""

    gate = term_gate_config(config)
    values: list[Any] = []
    if gate.get("registry"):
        values.append(gate["registry"])
    registries = gate.get("registries")
    if isinstance(registries, list):
        values.extend(registries)
    elif registries:
        values.append(registries)
    if not values and config.get("shared_terminology"):
        values.append(config["shared_terminology"])
    paths: list[Path] = []
    for value in values:
        path = root_path(str(value))
        if path not in paths:
            paths.append(path)
    return paths


def term_gate_required_gates(config: dict[str, Any]) -> list[str]:
    return list(term_gate_config(config).get("required_gates", ["source_full_ru_accepted"]))


def text_line_refs(text: str, needle: str, max_refs: int = 8, *, ignore_case: bool = True) -> list[int]:
    if not needle:
        return []
    flags = re.I if ignore_case else 0
    pattern = re.compile(rf"(?<![A-Za-zА-Яа-яЁё0-9]){re.escape(needle)}(?![A-Za-zА-Яа-яЁё0-9])", flags)
    refs: list[int] = []
    for line_no, line in enumerate(text.splitlines(), start=1):
        if pattern.search(line):
            refs.append(line_no)
            if len(refs) >= max_refs:
                break
    return refs


def bad_variant_line_refs(text: str, bad_variant: str) -> list[int]:
    has_letter = any(char.isalpha() for char in bad_variant)
    is_upper_acronym = has_letter and bad_variant.upper() == bad_variant
    return text_line_refs(text, bad_variant, ignore_case=not is_upper_acronym)


def split_term_values(value: str) -> list[str]:
    out: list[str] = []
    for part in re.split(r"\s*;\s*|\s*/\s*", value or ""):
        cleaned = part.strip()
        if cleaned and cleaned not in out:
            out.append(cleaned)
    return out


def accepted_registry_rows(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    accepted: list[dict[str, str]] = []
    for row in rows:
        status = str(row.get("status") or row.get("Status") or "").strip().casefold()
        if status and status != "accepted":
            continue
        source_term = str(row.get("source_term") or row.get("original_en") or row.get("term_key") or "").strip()
        accepted_ru = str(row.get("accepted_ru") or row.get("ru_decision") or row.get("RU") or "").strip()
        if source_term and accepted_ru:
            accepted.append(row)
    return accepted


def term_gate_exception_entries(gate: dict[str, Any]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """Load inline or JSON exception rows, keeping malformed evidence visible."""

    findings: list[dict[str, Any]] = []
    entries: list[dict[str, Any]] = []
    raw_values: list[Any] = [gate.get("exceptions"), gate.get("exception_allowlist")]
    for raw in raw_values:
        if raw is None:
            continue
        if isinstance(raw, str):
            path = root_path(raw)
            if not path.exists():
                findings.append({"code": "missing_term_exception_allowlist", "path": rel(path)})
                continue
            try:
                loaded = json.loads(path.read_text(encoding="utf-8"))
            except Exception as exc:
                findings.append({"code": "unreadable_term_exception_allowlist", "path": rel(path), "message": str(exc)})
                continue
            raw = loaded.get("exceptions", loaded) if isinstance(loaded, dict) else loaded
        if isinstance(raw, dict):
            raw = raw.get("exceptions", [])
        if not isinstance(raw, list):
            findings.append({"code": "invalid_term_exception_allowlist"})
            continue
        for entry in raw:
            if not isinstance(entry, dict) or not str(entry.get("term") or "").strip() or not str(entry.get("reason") or "").strip():
                findings.append({"code": "unreviewed_term_exception", "exception": entry})
                continue
            entries.append(entry)
    return entries, findings


def contextual_forbidden_mechanics(
    text: str, gate: dict[str, Any], exceptions: list[dict[str, Any]]
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """Find reader-output mechanics terms unless a reviewed contextual exception applies."""

    raw_terms = gate.get("forbidden_mechanics", [])
    if not isinstance(raw_terms, list):
        return [], [{"code": "invalid_forbidden_mechanics_config"}]
    findings: list[dict[str, Any]] = []
    checks: list[dict[str, Any]] = []
    for raw in raw_terms:
        spec = {"term": raw} if isinstance(raw, str) else raw
        if not isinstance(spec, dict) or not str(spec.get("term") or "").strip():
            findings.append({"code": "invalid_forbidden_mechanics_term", "term": raw})
            continue
        term = str(spec["term"]).strip()
        context_pattern = str(spec.get("context_regex") or "").strip()
        try:
            context_re = re.compile(context_pattern, re.I) if context_pattern else None
        except re.error as exc:
            findings.append({"code": "invalid_forbidden_mechanics_context", "term": term, "message": str(exc)})
            continue
        term_re = re.compile(rf"(?<![A-Za-zА-Яа-яЁё0-9]){re.escape(term)}(?![A-Za-zА-Яа-яЁё0-9])", re.I)
        hits: list[dict[str, Any]] = []
        for line_no, line in enumerate(text.splitlines(), start=1):
            if not term_re.search(line) or (context_re and not context_re.search(line)):
                continue
            allowed = next(
                (
                    exception
                    for exception in exceptions
                    if str(exception.get("term") or "").strip().casefold() in {"*", term.casefold()}
                    and (
                        not str(exception.get("context_regex") or exception.get("line_regex") or "").strip()
                        or re.search(str(exception.get("context_regex") or exception.get("line_regex")), line, re.I)
                    )
                ),
                None,
            )
            hit = {"line": line_no, "allowed": allowed is not None}
            if allowed is not None:
                hit["exception_reason"] = str(allowed["reason"])
            else:
                findings.append({"code": "forbidden_mechanics_term", "term": term, "line": line_no})
            hits.append(hit)
        checks.append({"term": term, "hits": hits, "unallowed_hits": sum(not hit["allowed"] for hit in hits)})
    return checks, findings


def run_term_gate(config_path: Path, *, check_only: bool = False) -> dict[str, Any]:
    config = read_json(config_path)
    report = term_gate_report_path(config)
    registries = term_gate_registry_paths(config)
    registry = registries[0] if registries else None
    source = term_gate_source_path(config)
    output = term_gate_output_path(config)
    findings: list[dict[str, Any]] = []
    gates = config.get("scenario_gates") or config.get("production_gates") or {}
    for gate in term_gate_required_gates(config):
        if gates.get(gate) is not True:
            findings.append({"code": "required_gate_not_true", "gate": gate, "value": gates.get(gate)})
    if not registries:
        findings.append({"code": "missing_term_registry_config"})
        rows: list[dict[str, str]] = []
    else:
        rows = []
        for registry_path in registries:
            if not registry_path.exists():
                findings.append({"code": "missing_term_registry", "path": rel(registry_path)})
                continue
            rows.extend(read_csv_rows(registry_path))
    if source is None or not source.exists():
        findings.append({"code": "missing_term_source_markdown", "path": rel(source) if source else None})
        source_text = ""
    else:
        source_text = source.read_text(encoding="utf-8")
    if output is None or not output.exists():
        findings.append({"code": "missing_term_output_markdown", "path": rel(output) if output else None})
        output_text = ""
    else:
        output_text = output.read_text(encoding="utf-8")

    checks: list[dict[str, Any]] = []
    accepted_rows = accepted_registry_rows(rows)
    for row in accepted_rows:
        source_term = str(row.get("source_term") or row.get("original_en") or row.get("term_key") or "").strip()
        accepted_ru = str(row.get("accepted_ru") or row.get("ru_decision") or row.get("RU") or "").strip()
        aliases = split_term_values(str(row.get("aliases") or row.get("short_form") or ""))
        bad_values = split_term_values(str(row.get("bad_ru") or row.get("bad_variants") or ""))
        source_refs = text_line_refs(source_text, source_term)
        if not source_refs:
            continue
        ru_refs = text_line_refs(output_text, accepted_ru)
        if not ru_refs:
            for alias in aliases:
                ru_refs = text_line_refs(output_text, alias)
                if ru_refs:
                    break
        bad_refs = {bad: refs for bad in bad_values if (refs := bad_variant_line_refs(output_text, bad))}
        status = "fail_bad_variant" if bad_refs else ("pass" if ru_refs else "missing_ru")
        if status != "pass":
            findings.append({"code": status, "source_term": source_term, "accepted_ru": accepted_ru, "source_refs": source_refs[:5]})
        checks.append(
            {
                "source_term": source_term,
                "accepted_ru": accepted_ru,
                "status": status,
                "source_line_refs": source_refs,
                "ru_line_refs": ru_refs,
                "bad_variant_refs": bad_refs,
            }
        )

    exception_entries, exception_findings = term_gate_exception_entries(term_gate_config(config))
    findings.extend(exception_findings)
    forbidden_checks, forbidden_findings = contextual_forbidden_mechanics(output_text, term_gate_config(config), exception_entries)
    findings.extend(forbidden_findings)

    result = {
        "schema": "translator_term_gate.v1",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "config": rel(config_path),
        "status": "blocked" if findings else "pass",
        "action": "check_only" if check_only else "checked",
        "required_gates": term_gate_required_gates(config),
        "registry": rel(registry) if registry else None,
        "registries": [rel(path) for path in registries],
        "source_markdown": rel(source) if source else None,
        "output_markdown": rel(output) if output else None,
        "counts": {
            "registry_rows": len(rows),
            "accepted_terms": len(accepted_rows),
            "checked_terms_present_in_source": len(checks),
            "forbidden_mechanics_terms": len(forbidden_checks),
            "forbidden_mechanics_hits": sum(len(item["hits"]) for item in forbidden_checks),
            "term_exception_allowlist_entries": len(exception_entries),
            "findings": len(findings),
        },
        "checks": checks,
        "forbidden_mechanics": forbidden_checks,
        "findings": findings,
    }
    write_json(report, result)
    return result


def layout_anchors_config(config: dict[str, Any]) -> dict[str, Any]:
    return config.get("layout_anchors", {})


def layout_anchors_report_path(config: dict[str, Any]) -> Path:
    anchors = layout_anchors_config(config)
    value = anchors.get("report", "layout_anchors_report.json")
    path = Path(str(value).replace("/", "\\"))
    return path.resolve() if path.is_absolute() else qa_root(config) / path


def run_layout_anchors(config_path: Path, *, check_only: bool = False) -> dict[str, Any]:
    config = read_json(config_path)
    anchors = layout_anchors_config(config)
    report = layout_anchors_report_path(config)
    source_value = anchors.get("source_markdown") or config.get("production_outputs", {}).get("keeper_markdown")
    source = root_path(str(source_value)) if source_value else None
    manifest_value = anchors.get("manifest")
    manifest = root_path(str(manifest_value)) if manifest_value else None
    findings: list[dict[str, Any]] = []
    gates = config.get("scenario_gates") or config.get("production_gates") or {}
    required_gates = list(anchors.get("required_gates", ["keeper_full_accepted"]))
    for gate in required_gates:
        if gates.get(gate) is not True:
            findings.append({"code": "required_gate_not_true", "gate": gate, "value": gates.get(gate)})
    if source is None or not source.exists():
        findings.append({"code": "missing_layout_source_markdown", "path": rel(source) if source else None})
        text = ""
    else:
        text = source.read_text(encoding="utf-8")
    if manifest is not None and not manifest.exists():
        findings.append({"code": "missing_layout_anchor_manifest", "path": rel(manifest)})

    pattern_checks: list[dict[str, Any]] = []
    for item in list(anchors.get("required_patterns", [])):
        name = str(item.get("name") or item.get("pattern") or "pattern")
        pattern = str(item.get("pattern") or "")
        flags = re.I if item.get("ignore_case", True) else 0
        found = bool(pattern and re.search(pattern, text, flags))
        pattern_checks.append({"name": name, "pattern": pattern, "found": found})
        if not found:
            findings.append({"code": "missing_required_layout_pattern", "name": name, "pattern": pattern})

    result = {
        "schema": "translator_layout_anchors.v1",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "config": rel(config_path),
        "status": "blocked" if findings else "pass",
        "action": "check_only" if check_only else "checked",
        "required_gates": required_gates,
        "source_markdown": rel(source) if source else None,
        "manifest": rel(manifest) if manifest else None,
        "counts": {
            "headings": len(re.findall(r"^#{1,6}\s+", text, re.M)),
            "tables": len(re.findall(r"^\|.+\|\s*$", text, re.M)),
            "images": len(re.findall(r"!\[[^\]]*\]\([^)]+\)|<img\b", text, re.I)),
            "page_markers": len(re.findall(r"pdf-page|source-page|=== PAGE", text, re.I)),
            "required_patterns": len(pattern_checks),
            "findings": len(findings),
        },
        "pattern_checks": pattern_checks,
        "findings": findings,
    }
    write_json(report, result)
    return result


def coverage_gate_config(config: dict[str, Any]) -> dict[str, Any]:
    return config.get("coverage_gate", {})


def contract_v2_config(config: dict[str, Any]) -> dict[str, Any]:
    return config.get("contract_v2", {})


def contract_v2_report_path(config: dict[str, Any]) -> Path:
    return config_report_path(config, "contract_v2", "source_block_coverage_report.json")


def contract_v2_manifest_path(config: dict[str, Any], key: str) -> Path | None:
    value = contract_v2_config(config).get(key)
    return root_path(str(value)) if value else None


def has_two_column_pages(config: dict[str, Any]) -> bool:
    return any(str(page.get("column_mode", "")).lower() == "two_column" for page in page_map_config(config).values())


def strict_reading_order_required(config: dict[str, Any]) -> bool:
    contract = contract_v2_config(config)
    return bool(
        contract.get("require_reading_order_gate")
        or contract.get("strict_reading_order")
        or has_two_column_pages(config)
    )


def load_source_block_document(path: Path) -> Any:
    return document_from_manifest(read_json(path))


def run_source_block_coverage_gate(config_path: Path, *, check_only: bool = False) -> dict[str, Any]:
    config = read_json(config_path)
    report = contract_v2_report_path(config)
    source_manifest = contract_v2_manifest_path(config, "source_block_manifest")
    candidate_manifest = contract_v2_manifest_path(config, "candidate_block_manifest")
    findings: list[dict[str, Any]] = []
    input_hashes: dict[str, str] = {"config": sha256_file(config_path)}
    source_document = None
    candidate_document = None
    source_validation = None
    candidate_validation = None
    coverage_gate = None
    strict_reading_order = strict_reading_order_required(config)
    source_schema = None
    candidate_schema = None

    if source_manifest is None:
        findings.append({"code": "missing_source_block_manifest_config"})
    elif not source_manifest.exists():
        findings.append({"code": "missing_source_block_manifest", "path": rel(source_manifest)})
    else:
        input_hashes["source_block_manifest"] = sha256_file(source_manifest)
        source_manifest_raw = read_json(source_manifest)
        source_schema = source_manifest_raw.get("schema")
        source_document = document_from_manifest(source_manifest_raw)
        source_validation = validate_document(source_document, strict_reading_order=strict_reading_order)
        for blocker in source_validation.blockers:
            findings.append({"code": "source_block_manifest_invalid", "detail": blocker})
        if strict_reading_order and source_schema != "translator.source_block_manifest.v2":
            findings.append(
                {
                    "code": "source_block_manifest_schema_not_v2",
                    "detail": f"expected translator.source_block_manifest.v2, actual {source_schema}",
                }
            )

    if candidate_manifest is None:
        findings.append({"code": "missing_candidate_block_manifest_config"})
    elif not candidate_manifest.exists():
        findings.append({"code": "missing_candidate_block_manifest", "path": rel(candidate_manifest)})
    else:
        input_hashes["candidate_block_manifest"] = sha256_file(candidate_manifest)
        candidate_manifest_raw = read_json(candidate_manifest)
        candidate_schema = candidate_manifest_raw.get("schema")
        candidate_document = document_from_manifest(candidate_manifest_raw)
        candidate_validation = validate_document(candidate_document, strict_reading_order=strict_reading_order)
        for blocker in candidate_validation.blockers:
            findings.append({"code": "candidate_block_manifest_invalid", "detail": blocker})
        if strict_reading_order and candidate_schema != "translator.candidate_block_manifest.v2":
            findings.append(
                {
                    "code": "candidate_block_manifest_schema_not_v2",
                    "detail": f"expected translator.candidate_block_manifest.v2, actual {candidate_schema}",
                }
            )

    if source_document is not None and candidate_document is not None:
        if strict_reading_order and input_hashes.get("source_block_manifest") == input_hashes.get("candidate_block_manifest"):
            findings.append(
                {
                    "code": "source_candidate_manifest_self_comparison",
                    "detail": "Strict reading-order gate requires independently generated source and candidate manifests.",
                }
            )
        coverage_gate = compare_structural_fingerprints(
            source_document,
            candidate_document,
            strict_reading_order=strict_reading_order,
        )
        for blocker in coverage_gate.blockers:
            findings.append({"code": "source_block_coverage_mismatch", "detail": blocker})

    result = {
        "schema": "translator_source_block_coverage_gate.v2",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "config": rel(config_path),
        "status": "blocked" if findings else "pass",
        "action": "check_only" if check_only else "checked",
        "strict_reading_order": strict_reading_order,
        "input_hashes": input_hashes,
        "source_block_manifest": rel(source_manifest) if source_manifest else None,
        "candidate_block_manifest": rel(candidate_manifest) if candidate_manifest else None,
        "manifest_schemas": {
            "source_block_manifest": source_schema,
            "candidate_block_manifest": candidate_schema,
        },
        "source_validation": {
            "status": source_validation.status,
            "blockers": list(source_validation.blockers),
            "fingerprint": structural_fingerprint(source_document).as_dict(),
        }
        if source_validation and source_document
        else None,
        "candidate_validation": {
            "status": candidate_validation.status,
            "blockers": list(candidate_validation.blockers),
            "fingerprint": structural_fingerprint(candidate_document).as_dict(),
        }
        if candidate_validation and candidate_document
        else None,
        "coverage_gate": {
            "status": coverage_gate.status,
            "blockers": list(coverage_gate.blockers),
        }
        if coverage_gate
        else None,
        "counts": {
            "findings": len(findings),
            "input_hashes": len(input_hashes),
        },
        "findings": findings,
    }
    write_json(report, result)
    return result


def critical_remediation_config(config: dict[str, Any]) -> dict[str, Any]:
    return config.get("critical_remediation_gate", {})


def critical_remediation_report_path(config: dict[str, Any]) -> Path:
    gate = critical_remediation_config(config)
    value = gate.get("report", "critical_remediation_gate_report.json")
    path = Path(str(value).replace("/", "\\"))
    return path.resolve() if path.is_absolute() else qa_root(config) / path


def coverage_gate_report_path(config: dict[str, Any]) -> Path:
    gate = coverage_gate_config(config)
    value = gate.get("report", "coverage_gate_report.json")
    path = Path(str(value).replace("/", "\\"))
    return path.resolve() if path.is_absolute() else qa_root(config) / path


def coverage_path(config: dict[str, Any], key: str, fallback: str | None = None) -> Path | None:
    gate = coverage_gate_config(config)
    outputs = config.get("production_outputs", {})
    value = gate.get(key) or outputs.get(key) or fallback
    return root_path(str(value)) if value else None


def markdown_headings(text: str) -> list[str]:
    return [match.group(2).strip() for match in re.finditer(r"^(#{1,6})\s+(.+?)\s*$", text, re.M)]


def markdown_page_markers(text: str) -> list[str]:
    return re.findall(r"source-page-(\d{1,4})|pdf-page-(\d{1,4})|<!--\s*page[: -]*(\d{1,4})(?:\s*[;|][^>]*)?\s*-->", text, re.I)


def normalize_marker_tuples(markers: list[tuple[str, ...]]) -> list[str]:
    result: list[str] = []
    for item in markers:
        value = next((part for part in item if part), "")
        if value:
            result.append(f"{int(value):03d}")
    return result


def markdown_image_refs(text: str) -> list[str]:
    return re.findall(r"!\[[^\]]*\]\([^)]+\)|<img\b[^>]*\bsrc=[\"'][^\"']+[\"'][^>]*>", text, re.I)


def dice_tokens(text: str) -> list[str]:
    return re.findall(r"\b\d*\s*[dD]\s*\d+(?:\s*[+-]\s*\d+)?\b", text)


def numeric_tokens(text: str) -> list[str]:
    return re.findall(r"(?<![\w.])\d+(?:[.,]\d+)?%?(?![\w.])", text)


def statblock_markers(text: str) -> list[str]:
    patterns = [
        (r"\b(?:STR|CON|SIZ|DEX|APP|INT|POW|EDU|HP|MP|SAN|DB|Build|Move)\b", 0),
        (r"\b(?:СИЛ|ВЫН|ТЕЛ|РАЗ|ЛОВ|ЛВК|НАР|ВНЕ|ИНТ|МОЩ|ОБР|РАС|ПЗ|ПМ|БкУ|ЗДР|МЗ|РАСС|Урон|Комплекция|Телосложение|Скорость|СКО)\b", re.I),
        (r"\b(?:Traits|Talents|Drives|Skills|Assets|Focuses|Statement)\b", 0),
        (r"\b(?:Черты|Таланты|Стимулы|Навыки|Активы|Специализации|Убеждение|Движение)\b", re.I),
    ]
    hits: list[str] = []
    for pattern, flags in patterns:
        hits.extend(re.findall(pattern, text, flags))
    return hits


def coverage_visible_text(text: str, *, kind: str) -> str:
    if kind == "html":
        text = re.sub(r"<script\b[\s\S]*?</script>", " ", text, flags=re.I)
        text = re.sub(r"<style\b[\s\S]*?</style>", " ", text, flags=re.I)
        text = strip_html_tags(text)
    else:
        text = re.sub(r"<!--[\s\S]*?-->", " ", text)
        text = re.sub(r"!\[[^\]]*\]\([^)]+\)", " ", text)
        # Placement ids, xrefs, and page attributes are traceability metadata,
        # not reader-facing numeric content for coverage comparisons.
        text = re.sub(r"<[^>]+>", " ", text)
    return text


def html_page_markers(text: str) -> list[str]:
    markers = re.findall(r'<section\b[^>]*\bclass=["\'][^"\']*production-page[^"\']*["\'][^>]*\bdata-page=["\'](\d{1,4})["\']', text, re.I)
    if not markers:
        markers = re.findall(r'<section\b[^>]*\bclass=["\'][^"\']*production-page[^"\']*["\'][^>]*\bid=["\']page-(\d{1,4})["\']', text, re.I)
    return [f"{int(item):03d}" for item in markers]


def pdf_token_text(text: str) -> str:
    raw_lines = [line.strip() for line in text.replace("\f", "\n").splitlines()]
    normalized_lines = [re.sub(r"\s+", " ", line).strip() for line in raw_lines]
    counts: dict[str, int] = {}
    for line in normalized_lines:
        if line:
            counts[line] = counts.get(line, 0) + 1
    kept: list[str] = []
    for raw, normalized in zip(raw_lines, normalized_lines):
        if not normalized:
            continue
        if re.search(r"\bfile:///.+\.html\b", normalized, re.I):
            continue
        if re.search(r"\bhttps?://.+\.html\b", normalized, re.I):
            continue
        if re.fullmatch(r"\d+\s*/\s*\d+", normalized):
            continue
        digit_chars = sum(1 for char in normalized if char.isdigit())
        digit_ratio = digit_chars / max(len(normalized), 1)
        repeated_footer_like = counts.get(normalized, 0) >= 3 and (len(normalized) <= 80 or digit_ratio >= 0.35)
        if repeated_footer_like:
            continue
        kept.append(raw)
    return "\n".join(kept)


def structural_features(text: str, *, kind: str) -> dict[str, Any]:
    headings = markdown_headings(text)
    token_text = coverage_visible_text(text, kind=kind)
    if kind == "html":
        headings = [strip_html_tags(item).strip() for item in re.findall(r"<h[1-6]\b[^>]*>(.*?)</h[1-6]>", text, re.I | re.S)]
        page_markers = html_page_markers(text)
        table_rows = re.findall(r"<tr\b|class=[\"'][^\"']*\bcredit-item\b", text, re.I)
        images = html_refs(text)
    else:
        page_markers = normalize_marker_tuples(markdown_page_markers(text))
        table_rows = [
            row
            for row in re.findall(r"^\|.+\|\s*$", text, re.M)
            if not re.fullmatch(r"\|\s*:?-{3,}:?\s*(?:\|\s*:?-{3,}:?\s*)+\|?", row.strip())
        ]
        images = markdown_image_refs(text)
    return {
        "chars": len(text),
        "page_markers": page_markers,
        "headings": headings,
        "tables": table_rows,
        "image_refs": images,
        "dice_tokens": dice_tokens(token_text),
        "numeric_tokens": numeric_tokens(token_text),
        "statblock_markers": statblock_markers(token_text),
    }


def strip_html_tags(value: str) -> str:
    return re.sub(r"<[^>]+>", " ", value)


def norm_text_for_presence(value: str) -> str:
    value = value.casefold()
    value = re.sub(r"[^\wа-яё]+", " ", value, flags=re.I)
    return re.sub(r"\s+", " ", value).strip()


def multiset_coverage(source_items: list[str], target_items: list[str]) -> dict[str, Any]:
    source_counts: dict[str, int] = {}
    target_counts: dict[str, int] = {}
    for item in source_items:
        key = re.sub(r"\s+", "", item.casefold())
        source_counts[key] = source_counts.get(key, 0) + 1
    for item in target_items:
        key = re.sub(r"\s+", "", item.casefold())
        target_counts[key] = target_counts.get(key, 0) + 1
    missing: list[dict[str, Any]] = []
    covered = 0
    total = sum(source_counts.values())
    for key, count in source_counts.items():
        target_count = target_counts.get(key, 0)
        covered += min(count, target_count)
        if target_count < count:
            missing.append({"token": key, "expected": count, "found": target_count})
    ratio = covered / total if total else 1.0
    return {"source": total, "target": sum(target_counts.values()), "covered": covered, "ratio": ratio, "missing": missing[:50]}


def source_pdf_info_report_path(config: dict[str, Any]) -> Path:
    return intake_report_path(config, "pdf_info_report", "source_pdf_info.json")


def load_source_pdf_metadata(config: dict[str, Any]) -> tuple[dict[str, Any] | None, list[dict[str, Any]]]:
    warnings: list[dict[str, Any]] = []
    report = source_pdf_info_report_path(config)
    if report.exists():
        try:
            data = read_json(report)
            source_pdf = data.get("source_pdf")
            if isinstance(source_pdf, dict) and source_pdf.get("pages"):
                return source_pdf, warnings
        except (json.JSONDecodeError, OSError) as exc:
            warnings.append({"code": "source_pdf_info_read_failed", "path": rel(report), "message": str(exc)})
    source_value = config.get("source_pdf")
    if not source_value:
        return None, warnings + [{"code": "missing_source_pdf_config"}]
    source = root_path(str(source_value))
    if not source.exists():
        return None, warnings + [{"code": "missing_source_pdf", "path": rel(source)}]
    try:
        return pdf_metadata(source), warnings
    except Exception as exc:  # pragma: no cover - defensive runtime report path
        return None, warnings + [{"code": "source_pdf_metadata_failed", "path": rel(source), "message": str(exc)}]


def critical_gate_path(config: dict[str, Any], key: str, fallback: str | None = None) -> Path | None:
    gate = critical_remediation_config(config)
    outputs = config.get("production_outputs", {})
    value = gate.get(key) or outputs.get(key) or fallback
    return root_path(str(value)) if value else None


def english_like_heading(value: str) -> bool:
    text = strip_html_tags(value).strip()
    if not text:
        return False
    latin = len(re.findall(r"[A-Za-z]", text))
    cyrillic = len(re.findall(r"[А-Яа-яЁё]", text))
    if latin < 3:
        return False
    if cyrillic:
        return latin > cyrillic * 2
    return True


def heading_records(text: str, *, kind: str, artifact: str) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    if kind == "html":
        for match in re.finditer(r"<h([1-6])\b[^>]*>(.*?)</h\1>", text, re.I | re.S):
            heading = strip_html_tags(match.group(2)).strip()
            if english_like_heading(heading):
                records.append({"artifact": artifact, "heading": heading[:160], "offset": match.start()})
    else:
        for match in re.finditer(r"^(#{1,6})\s+(.+?)\s*$", text, re.M):
            heading = match.group(2).strip()
            if english_like_heading(heading):
                records.append({"artifact": artifact, "heading": heading[:160], "line": text.count("\n", 0, match.start()) + 1})
    return records


def regex_for_literal_label(label: str) -> re.Pattern[str]:
    parts = re.split(r"\s+", label.strip())
    pattern = r"\s+".join(re.escape(part) for part in parts if part)
    return re.compile(pattern, re.I)


def markdown_heading_contains_label(text: str, label_re: re.Pattern[str]) -> bool:
    return any(label_re.search(match.group(2).strip()) for match in re.finditer(r"^(#{1,6})\s+(.+?)\s*$", text, re.M))


def markdown_callout_contains_label(text: str, label_re: re.Pattern[str]) -> bool:
    return any(label_re.search(line.strip().lstrip(">").strip()) for line in text.splitlines() if line.strip().startswith(">"))


def html_heading_contains_label(text: str, label_re: re.Pattern[str]) -> bool:
    for match in re.finditer(r"<h([1-6])\b[^>]*>(.*?)</h\1>", text, re.I | re.S):
        if label_re.search(strip_html_tags(match.group(2)).strip()):
            return True
    return False


def html_toc_contains_label(text: str, label_re: re.Pattern[str]) -> bool:
    toc = TOC_RE.search(text)
    return bool(toc and label_re.search(strip_html_tags(toc.group("toc")).strip()))


def html_callout_contains_label(text: str, label_re: re.Pattern[str]) -> bool:
    for match in re.finditer(r"<blockquote\b[^>]*\bclass=[\"'][^\"']*\breview-callout\b[^\"']*[\"'][^>]*>(.*?)</blockquote>", text, re.I | re.S):
        if label_re.search(strip_html_tags(match.group(1)).strip()):
            return True
    return False


def required_callout_records(
    required_callouts: list[dict[str, Any]],
    *,
    texts: dict[str, str],
    pdf_text: str,
) -> list[dict[str, Any]]:
    findings: list[dict[str, Any]] = []
    for item in required_callouts:
        label = str(item.get("label") or "").strip()
        if not label:
            continue
        label_re = regex_for_literal_label(label)
        artifacts = item.get("artifacts") or ["ru_markdown", "keeper_markdown", "html"]
        require_pdf_text = bool(item.get("require_pdf_text", True))

        for artifact in artifacts:
            text = texts.get(str(artifact), "")
            if not text:
                continue
            if artifact in {"ru_markdown", "keeper_markdown"}:
                if markdown_heading_contains_label(text, label_re):
                    findings.append({"code": "required_callout_rendered_as_heading", "artifact": artifact, "label": label})
                if not markdown_callout_contains_label(text, label_re):
                    findings.append({"code": "missing_required_markdown_callout", "artifact": artifact, "label": label})
            elif artifact == "html":
                if html_heading_contains_label(text, label_re):
                    findings.append({"code": "required_callout_rendered_as_html_heading", "artifact": artifact, "label": label})
                if html_toc_contains_label(text, label_re):
                    findings.append({"code": "required_callout_visible_in_toc", "artifact": artifact, "label": label})
                if not html_callout_contains_label(text, label_re):
                    findings.append({"code": "missing_required_html_callout", "artifact": artifact, "label": label})

        if require_pdf_text and not label_re.search(pdf_token_text(pdf_text)):
            findings.append({"code": "missing_required_pdf_callout_text", "artifact": "pdf_text", "label": label})
    return findings


def term_hit_records(text: str, terms: list[str], *, artifact: str, limit: int = 200) -> list[dict[str, Any]]:
    hits: list[dict[str, Any]] = []
    for term in terms:
        if not term:
            continue
        pattern = re.compile(rf"(?<![\wА-Яа-яЁё]){re.escape(term)}(?![\wА-Яа-яЁё])", re.I)
        for match in pattern.finditer(text):
            hits.append(
                {
                    "artifact": artifact,
                    "term": term,
                    "match": match.group(0),
                    "line": text.count("\n", 0, match.start()) + 1,
                }
            )
            if len(hits) >= limit:
                return hits
    return hits


def duplicate_refs(refs: list[str], allowed: set[str] | None = None) -> list[dict[str, Any]]:
    allowed = allowed or set()
    counts: dict[str, int] = {}
    for ref in refs:
        key = normalize_ref(ref).replace("\\", "/")
        counts[key] = counts.get(key, 0) + 1
    return [{"ref": ref, "count": count} for ref, count in sorted(counts.items()) if count > 1 and ref not in allowed]


def expected_page_markers(source_pages: int | None) -> set[str]:
    if not source_pages:
        return set()
    return {f"{page:03d}" for page in range(1, source_pages + 1)}


def run_critical_remediation_gate(config_path: Path, *, check_only: bool = False) -> dict[str, Any]:
    config = read_json(config_path)
    gate = critical_remediation_config(config)
    report = critical_remediation_report_path(config)
    outputs = config.get("production_outputs", {})
    ru = critical_gate_path(config, "ru_markdown", outputs.get("source_full_ru"))
    keeper = critical_gate_path(config, "keeper_markdown", outputs.get("keeper_markdown"))
    html = critical_gate_path(config, "html", outputs.get("html"))
    pdf = critical_gate_path(config, "pdf", outputs.get("pdf"))
    findings: list[dict[str, Any]] = []
    warnings: list[dict[str, Any]] = []
    telemetry = cache_telemetry()

    source_meta, source_warnings = load_source_pdf_metadata(config)
    warnings.extend(source_warnings)
    source_pages = int(source_meta.get("pages", 0)) if source_meta else None
    if not source_pages:
        findings.append({"code": "source_pdf_page_count_unavailable"})

    pdf_meta = None
    pdf_text = ""
    if pdf and pdf.exists():
        try:
            pdf_meta = pdf_metadata(pdf)
        except Exception as exc:  # pragma: no cover - defensive runtime report path
            findings.append({"code": "production_pdf_metadata_failed", "path": rel(pdf), "message": str(exc)})
        pdf_processing = cached_pdf_processing(config, pdf, variant=None, telemetry=telemetry)
        pdf_text = str(pdf_processing["text"])
        if pdf_processing["error"]:
            findings.append({"code": "production_pdf_text_extract_failed", **pdf_processing["error"]})
        elif len(pdf_token_text(pdf_text)) < int(gate.get("min_pdf_token_chars", 1000)):
            findings.append({"code": "production_pdf_text_too_short", "chars": len(pdf_token_text(pdf_text))})
    else:
        findings.append({"code": "missing_production_pdf", "path": rel(pdf) if pdf else None})

    pdf_pages = int(pdf_meta.get("pages", 0)) if pdf_meta else None
    pdf_mode = str(gate.get("pdf_mode", "reader-draft"))
    if source_pages and pdf_pages:
        ratio = round(pdf_pages / max(source_pages, 1), 3)
        max_reader_ratio = float(gate.get("max_reader_page_ratio", 2.0))
        if pdf_mode == "source-layout" and pdf_pages != source_pages:
            findings.append({"code": "source_layout_pdf_page_count_mismatch", "source_pages": source_pages, "pdf_pages": pdf_pages})
        elif pdf_mode == "reader-draft" and ratio > max_reader_ratio:
            findings.append({"code": "reader_pdf_page_ratio_too_high", "source_pages": source_pages, "pdf_pages": pdf_pages, "ratio": ratio, "max_ratio": max_reader_ratio})

    texts: dict[str, str] = {}
    for name, path, kind in [
        ("ru_markdown", ru, "markdown"),
        ("keeper_markdown", keeper, "markdown"),
        ("html", html, "html"),
    ]:
        if not path or not path.exists():
            findings.append({"code": f"missing_{name}", "path": rel(path) if path else None})
            texts[name] = ""
            continue
        texts[name] = path.read_text(encoding="utf-8", errors="replace")
        if gate.get("require_russian_headings", False):
            headings = heading_records(texts[name], kind=kind, artifact=name)
            for item in headings[: int(gate.get("max_heading_findings", 80))]:
                findings.append({"code": "english_reader_facing_heading", **item})

    required_pages = expected_page_markers(source_pages)
    html_required_pages = set(required_pages)
    toc_policy = production_html_config(config).get("toc_policy", {})
    if isinstance(toc_policy, dict) and toc_policy.get("replace_source_toc_pages", True):
        html_required_pages -= {
            page for page, meta in page_map_config(config).items()
            if str(meta.get("type") or "") == "source_toc"
        }
    for name, text, kind in [
        ("ru_markdown", texts.get("ru_markdown", ""), "markdown"),
        ("keeper_markdown", texts.get("keeper_markdown", ""), "markdown"),
        ("html", texts.get("html", ""), "html"),
    ]:
        markers = set(structural_features(text, kind=kind)["page_markers"])
        expected = html_required_pages if name == "html" else required_pages
        if gate.get("require_exact_page_markers", False) and expected and markers != expected:
            findings.append({"code": "source_page_marker_mismatch", "artifact": name, "missing": sorted(expected - markers), "extra": sorted(markers - expected)})

    blocker_terms = list(gate.get("blocker_english_terms") or [])
    for name, text in [
        ("ru_markdown", texts.get("ru_markdown", "")),
        ("keeper_markdown", texts.get("keeper_markdown", "")),
        ("html", coverage_visible_text(texts.get("html", ""), kind="html")),
        ("pdf_text", pdf_token_text(pdf_text)),
    ]:
        for hit in term_hit_records(text, blocker_terms, artifact=name, limit=int(gate.get("max_term_findings_per_artifact", 200))):
            findings.append({"code": "blocker_english_term", **hit})

    reader_noise_patterns = list(production_html_config(config).get("suppress_reader_noise_patterns", []))
    for name, text in [
        ("ru_markdown", texts.get("ru_markdown", "")),
        ("keeper_markdown", texts.get("keeper_markdown", "")),
        ("html", coverage_visible_text(texts.get("html", ""), kind="html")),
        ("pdf_text", pdf_token_text(pdf_text)),
    ]:
        for pattern in reader_noise_patterns:
            if not pattern:
                continue
            noise_re = re.compile(str(pattern), re.I)
            for match in noise_re.finditer(text):
                findings.append(
                    {
                        "code": "reader_visible_noise",
                        "artifact": name,
                        "pattern": str(pattern),
                        "match": match.group(0)[:160],
                        "line": text.count("\n", 0, match.start()) + 1,
                    }
                )
                if len([item for item in findings if item.get("code") == "reader_visible_noise" and item.get("artifact") == name]) >= int(gate.get("max_reader_noise_findings_per_artifact", 50)):
                    break

    if gate.get("block_hyphenated_line_breaks", True):
        for name, text in [
            ("ru_markdown", texts.get("ru_markdown", "")),
            ("keeper_markdown", texts.get("keeper_markdown", "")),
            ("html", coverage_visible_text(texts.get("html", ""), kind="html")),
        ]:
            for item in hyphenated_line_break_records(
                text,
                artifact=name,
                limit=int(gate.get("max_hyphenated_line_break_findings_per_artifact", 50)),
            ):
                findings.append({"code": "reader_hyphenated_line_break", **item})

    required_callouts = [item for item in gate.get("required_callouts", []) if isinstance(item, dict)]
    findings.extend(required_callout_records(required_callouts, texts=texts, pdf_text=pdf_text))

    if html and html.exists():
        refs = html_refs(texts.get("html", ""))
        allowed_duplicates = {str(item).replace("\\", "/") for item in gate.get("allowed_duplicate_image_refs", [])}
        for item in duplicate_refs(refs, allowed=allowed_duplicates):
            findings.append({"code": "duplicate_html_image_ref", **item})

    if gate.get("require_cropped_preserved_art", True):
        findings.extend(canonical_art_placement_findings(config))
        if art_placement_manifest_path(config) is None:
            for index, item in enumerate(art_integration_config(config).get("preserved_page_art", []), start=1):
                role = str(item.get("role") or "")
                if item.get("allow_full_page_art") is True:
                    continue
                if role in set(gate.get("crop_required_roles", ["map", "floorplan", "source_image"])) and not item.get("crop_box"):
                    findings.append(
                        {
                            "code": "preserved_art_missing_crop_box",
                            "index": index,
                            "page": item.get("page"),
                            "role": role,
                            "target_filename": item.get("target_filename"),
                        }
                    )

    result = {
        "schema": "translator_critical_remediation_gate.v1",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "config": rel(config_path),
        "status": "blocked" if findings else "pass",
        "action": "check_only" if check_only else "checked",
        "pdf_mode": pdf_mode,
        "paths": {
            "ru_markdown": rel(ru) if ru else None,
            "keeper_markdown": rel(keeper) if keeper else None,
            "html": rel(html) if html else None,
            "pdf": rel(pdf) if pdf else None,
            "art_placement_manifest": rel(art_placement_manifest_path(config)) if art_placement_manifest_path(config) else None,
        },
        "hashes": {"html_sha256": sha256_file(html) if html and html.exists() else None},
        "source_pdf": source_meta,
        "production_pdf": pdf_meta,
        "counts": {
            "source_pdf_pages": source_pages or 0,
            "production_pdf_pages": pdf_pages or 0,
            "findings": len(findings),
            "warnings": len(warnings),
            "pdf_text_chars": len(pdf_text),
            "required_callouts": len(required_callouts),
        },
        "findings": findings,
        "warnings": warnings,
        "cache": telemetry,
        "approval_state": {
            "critical_remediation_gate_passed": False,
            "production_approved": False,
        },
    }
    write_json(report, result)
    return result


def run_coverage_gate(config_path: Path, *, check_only: bool = False) -> dict[str, Any]:
    config = read_json(config_path)
    gate = coverage_gate_config(config)
    report = coverage_gate_report_path(config)
    outputs = config.get("production_outputs", {})
    source = coverage_path(config, "source_markdown")
    ru = coverage_path(config, "ru_markdown", outputs.get("source_full_ru"))
    keeper = coverage_path(config, "keeper_markdown", outputs.get("keeper_markdown"))
    html = coverage_path(config, "html", outputs.get("html"))
    pdf = coverage_path(config, "pdf", outputs.get("pdf"))
    gates = config.get("scenario_gates") or config.get("production_gates") or {}
    required_gates = list(gate.get("required_gates", []))
    min_token_coverage = float(gate.get("min_token_coverage", 0.98))
    min_heading_ratio = float(gate.get("min_heading_ratio", 0.95))
    min_pdf_heading_ratio = float(gate.get("min_pdf_heading_ratio", 0.80))
    min_pdf_heading_hits = int(gate.get("min_pdf_heading_hits", 6))
    findings: list[dict[str, Any]] = []
    warnings: list[dict[str, Any]] = []
    telemetry = cache_telemetry()

    for required in required_gates:
        if gates.get(required) is not True:
            findings.append({"code": "required_gate_not_true", "gate": required, "value": gates.get(required)})

    paths = {"source_markdown": source, "ru_markdown": ru, "keeper_markdown": keeper, "html": html}
    if gate.get("require_pdf", False):
        paths["pdf"] = pdf
    texts: dict[str, str] = {}
    for name, path in paths.items():
        if path is None or not path.exists():
            findings.append({"code": f"missing_{name}", "path": rel(path) if path else None})
            texts[name] = ""
        else:
            texts[name] = path.read_text(encoding="utf-8", errors="replace")

    pdf_text = ""
    pdf_error = None
    if pdf is not None and pdf.exists():
        pdf_processing = cached_pdf_processing(config, pdf, variant=None, telemetry=telemetry)
        pdf_text = str(pdf_processing["text"])
        pdf_error = pdf_processing["error"]
        if pdf_error:
            warnings.append(pdf_error)
    elif gate.get("require_pdf", False):
        findings.append({"code": "missing_pdf", "path": rel(pdf) if pdf else None})

    pdf_tokens_text = pdf_token_text(pdf_text)
    comparable_keeper_text = texts.get("keeper_markdown", "")
    toc_policy = production_html_config(config).get("toc_policy", {})
    excluded_keeper_page_types = {str(value) for value in gate.get("exclude_keeper_page_types", [])}
    if isinstance(toc_policy, dict) and toc_policy.get("replace_source_toc_pages", True):
        excluded_keeper_page_types.add("source_toc")
    landing_policy = production_html_config(config).get("landing", {})
    if isinstance(landing_policy, dict) and landing_policy.get("suppress_source_cover_page", False):
        excluded_keeper_page_types.add("cover")
    if excluded_keeper_page_types:
        comparable_keeper_text = remove_markdown_pages_by_type(comparable_keeper_text, config, excluded_keeper_page_types)
    declared_transforms = gate.get("declared_html_transforms", {})
    if not isinstance(declared_transforms, dict):
        declared_transforms = {}
    heading_transform_allowance = max(0, int(declared_transforms.get("headings_to_callouts", 0)))
    table_transform_allowance = max(0, int(declared_transforms.get("tables_to_credit_layouts", 0)))
    table_transform_allowance += max(0, int(declared_transforms.get("tables_to_continuation_merges", 0)))
    features = {
        "source_markdown": structural_features(texts.get("source_markdown", ""), kind="markdown"),
        "ru_markdown": structural_features(texts.get("ru_markdown", ""), kind="markdown"),
        "keeper_markdown": structural_features(texts.get("keeper_markdown", ""), kind="markdown"),
        "keeper_production_baseline": structural_features(comparable_keeper_text, kind="markdown"),
        "html": structural_features(texts.get("html", ""), kind="html"),
        "pdf_text": {
            "chars": len(pdf_text),
            "token_chars": len(pdf_tokens_text),
            "headings_checked": 0,
            "heading_hits": 0,
            "dice_tokens": dice_tokens(pdf_tokens_text),
            "numeric_tokens": numeric_tokens(pdf_tokens_text),
        },
    }

    ignored_text_pages = {
        str(page).zfill(3)
        for page, meta in page_map_config(config).items()
        if isinstance(meta, dict) and bool(meta.get("skip_ocr"))
    }
    source_pages = set(features["source_markdown"]["page_markers"])
    ru_pages = set(features["ru_markdown"]["page_markers"])
    keeper_pages = set(features["keeper_markdown"]["page_markers"])
    source_pages_cmp = source_pages - ignored_text_pages
    ru_pages_cmp = ru_pages - ignored_text_pages
    keeper_pages_cmp = keeper_pages - ignored_text_pages
    if source_pages_cmp and source_pages_cmp != ru_pages_cmp:
        findings.append({"code": "page_marker_mismatch_en_ru", "missing_in_ru": sorted(source_pages_cmp - ru_pages_cmp), "extra_in_ru": sorted(ru_pages_cmp - source_pages_cmp)})
    if ru_pages_cmp and ru_pages_cmp != keeper_pages_cmp:
        findings.append({"code": "page_marker_mismatch_ru_keeper", "missing_in_keeper": sorted(ru_pages_cmp - keeper_pages_cmp), "extra_in_keeper": sorted(keeper_pages_cmp - ru_pages_cmp)})
    html_pages = set(features["html"]["page_markers"])
    keeper_production_pages = set(features["keeper_production_baseline"]["page_markers"])
    if keeper_production_pages and keeper_production_pages != html_pages:
        findings.append({"code": "page_marker_mismatch_keeper_html", "missing_in_html": sorted(keeper_production_pages - html_pages), "extra_in_html": sorted(html_pages - keeper_production_pages)})
    if len(features["ru_markdown"]["headings"]) < len(features["source_markdown"]["headings"]) * min_heading_ratio:
        findings.append(
            {
                "code": "heading_count_regression_en_ru",
                "source": len(features["source_markdown"]["headings"]),
                "ru": len(features["ru_markdown"]["headings"]),
                "min_ratio": min_heading_ratio,
            }
        )
    expected_keeper_headings = max(0, len(features["keeper_production_baseline"]["headings"]) - heading_transform_allowance)
    if len(features["html"]["headings"]) < expected_keeper_headings * min_heading_ratio:
        findings.append(
            {
                "code": "heading_count_regression_keeper_html",
                "keeper": len(features["keeper_production_baseline"]["headings"]),
                "declared_heading_transforms": heading_transform_allowance,
                "expected_after_transforms": expected_keeper_headings,
                "html": len(features["html"]["headings"]),
                "min_ratio": min_heading_ratio,
            }
        )

    structural_pairs = [
        ("image_refs_en_ru", "source_markdown", "ru_markdown", "image_refs", 1.0),
        ("image_refs_keeper_html", "keeper_production_baseline", "html", "image_refs", 1.0),
        ("tables_en_ru", "source_markdown", "ru_markdown", "tables", 1.0),
        ("tables_keeper_html", "keeper_production_baseline", "html", "tables", 1.0),
        ("statblocks_en_ru", "source_markdown", "ru_markdown", "statblock_markers", min_heading_ratio),
        ("statblocks_keeper_html", "keeper_production_baseline", "html", "statblock_markers", min_heading_ratio),
    ]
    for code, source_name, target_name, field, min_ratio in structural_pairs:
        source_count = len(features[source_name][field])
        target_count = len(features[target_name][field])
        allowance = table_transform_allowance if code == "tables_keeper_html" else 0
        required = max(0, source_count - allowance) * min_ratio
        if target_count < required:
            findings.append(
                {
                    "code": "structural_count_regression",
                    "check": code,
                    "field": field,
                    "source": source_count,
                    "declared_transform_allowance": allowance,
                    "target": target_count,
                    "min_ratio": min_ratio,
                }
            )

    token_checks = {
        "dice_en_ru": multiset_coverage(features["source_markdown"]["dice_tokens"], features["ru_markdown"]["dice_tokens"]),
        "numbers_en_ru": multiset_coverage(features["source_markdown"]["numeric_tokens"], features["ru_markdown"]["numeric_tokens"]),
        "dice_keeper_html": multiset_coverage(features["keeper_production_baseline"]["dice_tokens"], features["html"]["dice_tokens"]),
        "numbers_keeper_html": multiset_coverage(features["keeper_production_baseline"]["numeric_tokens"], features["html"]["numeric_tokens"]),
    }
    if pdf_text or gate.get("require_pdf", False):
        token_checks["dice_keeper_pdf"] = multiset_coverage(features["keeper_production_baseline"]["dice_tokens"], features["pdf_text"]["dice_tokens"])
        token_checks["numbers_keeper_pdf"] = multiset_coverage(features["keeper_production_baseline"]["numeric_tokens"], features["pdf_text"]["numeric_tokens"])
    for name, check in token_checks.items():
        if check["ratio"] < min_token_coverage:
            findings.append({"code": "token_coverage_below_threshold", "check": name, "ratio": check["ratio"], "min_ratio": min_token_coverage, "missing": check["missing"][:20]})

    if pdf_text:
        pdf_norm = norm_text_for_presence(pdf_text)
        headings = [item for item in features["keeper_production_baseline"]["headings"] if len(norm_text_for_presence(item)) >= 4]
        checked = headings
        hits = sum(1 for heading in checked if norm_text_for_presence(heading) in pdf_norm)
        features["pdf_text"].update({"headings_checked": len(checked), "heading_hits": hits})
        required_hits = min(min_pdf_heading_hits, len(checked))
        required_ratio_hits = round(len(checked) * min_pdf_heading_ratio)
        required = min(len(checked), max(required_hits, required_ratio_hits))
        if checked and hits < required:
            findings.append(
                {
                    "code": "pdf_heading_coverage_failed",
                    "checked": len(checked),
                    "hits": hits,
                    "required_hits": required,
                    "min_ratio": min_pdf_heading_ratio,
                }
            )

    result = {
        "schema": "translator_coverage_gate.v1",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "config": rel(config_path),
        "status": "blocked" if findings else "pass",
        "action": "check_only" if check_only else "checked",
        "required_gates": required_gates,
        "paths": {name: rel(path) if path else None for name, path in {"source_markdown": source, "ru_markdown": ru, "keeper_markdown": keeper, "html": html, "pdf": pdf}.items()},
        "thresholds": {
            "min_token_coverage": min_token_coverage,
            "min_heading_ratio": min_heading_ratio,
            "min_pdf_heading_ratio": min_pdf_heading_ratio,
            "min_pdf_heading_hits": min_pdf_heading_hits,
        },
        "counts": {
            "findings": len(findings),
            "warnings": len(warnings),
            "source_pages": len(features["source_markdown"]["page_markers"]),
            "ru_pages": len(features["ru_markdown"]["page_markers"]),
            "source_headings": len(features["source_markdown"]["headings"]),
            "ru_headings": len(features["ru_markdown"]["headings"]),
            "keeper_headings": len(features["keeper_markdown"]["headings"]),
            "html_headings": len(features["html"]["headings"]),
            "pdf_text_chars": features["pdf_text"]["chars"],
            "pdf_heading_hits": features["pdf_text"]["heading_hits"],
            "pdf_headings_checked": features["pdf_text"]["headings_checked"],
        },
        "token_checks": token_checks,
        "features": {
            name: {
                "chars": data["chars"],
                "page_markers": len(data.get("page_markers", [])),
                "headings": len(data.get("headings", [])),
                "tables": len(data.get("tables", [])),
                "image_refs": len(data.get("image_refs", [])),
                "dice_tokens": len(data.get("dice_tokens", [])),
                "numeric_tokens": len(data.get("numeric_tokens", [])),
                "statblock_markers": len(data.get("statblock_markers", [])),
            }
            for name, data in features.items()
            if name != "pdf_text"
        },
        "pdf_text": features["pdf_text"],
        "findings": findings,
        "warnings": warnings,
        "cache": telemetry,
        "approval_state": {
            "coverage_gate_passed": not findings,
            "production_approved": False,
        },
    }
    write_json(report, result)
    return result


def release_qa_config(config: dict[str, Any]) -> dict[str, Any]:
    return config.get("release_qa", {})


def release_qa_report_path(config: dict[str, Any]) -> Path:
    release = release_qa_config(config)
    value = release.get("report", "release_qa_report.json")
    path = Path(str(value).replace("/", "\\"))
    return path.resolve() if path.is_absolute() else qa_root(config) / path


def release_report_dependency_paths(config: dict[str, Any], release: dict[str, Any]) -> dict[str, Path]:
    outputs = config.get("production_outputs", {})
    paths = {
        "approval_ledger": approval_ledger_report_path(config),
        "approval_ledger_qa": approval_ledger_qa_path(config),
        "release_manifest": release_manifest_report_path(config),
        "art_layout_qa": art_layout_qa_report_path(config),
        "pdf_print_qa": root_path(str(release["pdf_print_qa_report"])) if release.get("pdf_print_qa_report") else pdf_print_qa_report_path(config),
        "postproduction_qa": report_path(config, "qa_report", "public_postproduction_qa.json"),
        "image_optimization": report_path(config, "optimization_report", "postproduction_image_optimization.json"),
        "runtime_image_cleanup": cleanup_runtime_images_report_path(config),
        "production_html": production_html_report_path(config),
        "critical_remediation_gate": critical_remediation_report_path(config),
        "term_gate": term_gate_report_path(config),
    }
    configured = release.get("report_paths", {})
    if isinstance(configured, dict):
        for label, value in configured.items():
            if value:
                paths[str(label)] = root_path(str(value))
    return paths


def nested_report_value(data: Any, field: str) -> Any:
    value = data
    for part in field.split("."):
        if not isinstance(value, dict) or part not in value:
            return None
        value = value[part]
    return value


def report_minimum_satisfied(value: Any, expected: Any) -> bool:
    if isinstance(expected, dict):
        expected = expected.get("minimum", expected.get("min"))
    if isinstance(value, (list, dict, str)):
        value = len(value)
    return isinstance(value, (int, float)) and isinstance(expected, (int, float)) and value >= expected


def release_open_blockers(release: dict[str, Any]) -> tuple[Path | None, list[dict[str, Any]], list[dict[str, Any]]]:
    raw = release.get("open_blocker_ledger")
    if not raw:
        return None, [], []
    settings = raw if isinstance(raw, dict) else {"path": raw}
    if not settings.get("path"):
        return None, [], [{"code": "invalid_open_blocker_ledger_config"}]
    path = root_path(str(settings["path"]))
    if not path.exists():
        return path, [], [{"code": "missing_open_blocker_ledger", "path": rel(path)}]
    try:
        if path.suffix.lower() == ".json":
            data = read_json(path)
            candidates = data.get("open_blockers", data.get("blockers", [])) if isinstance(data, dict) else data
            if not isinstance(candidates, list):
                return path, [], [{"code": "invalid_open_blocker_ledger", "path": rel(path)}]
            blockers = [
                item if isinstance(item, dict) else {"value": item}
                for item in candidates
                if not isinstance(item, dict) or str(item.get("status", "open")).casefold() in {"open", "blocked", "todo"}
            ]
            return path, blockers, []
        blockers = [
            {"line": line_no, "text": line.strip()}
            for line_no, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1)
            if re.search(r"(?:-\s*\[\s*\]|\bstatus\s*:\s*(?:open|blocked|todo)\b)", line, re.I)
        ]
        return path, blockers, []
    except Exception as exc:
        return path, [], [{"code": "unreadable_open_blocker_ledger", "path": rel(path), "message": str(exc)}]


def production_html_semantic_qa(config: dict[str, Any], html_text: str) -> tuple[dict[str, Any], list[dict[str, Any]], list[dict[str, Any]]]:
    checks: dict[str, Any] = {}
    findings: list[dict[str, Any]] = []
    warnings: list[dict[str, Any]] = []
    page_map = page_map_config(config)
    landing_asset = production_html_config(config).get("landing_asset") or {}
    suppress_source_cover = isinstance(landing_asset, dict) and bool(landing_asset.get("suppress_source_cover_page", False))
    cover_results: list[dict[str, Any]] = []
    for page in sorted(frontmatter_cover_pages(config)):
        match = re.search(
            rf'(?P<section><section\b(?=[^>]*\bid=["\']page-{re.escape(page)}["\'])(?=[^>]*\bclass=["\'][^"\']*\bpage-type-cover\b)[^>]*>[\s\S]*?</section>)',
            html_text,
            re.I,
        )
        record = {
            "page": page,
            "section": bool(match),
            "figure": False,
            "background": False,
            "inline_figure": False,
            "full_page_class": False,
        }
        if not match:
            findings.append({"code": "frontmatter_cover_section_missing", "page": page})
            cover_results.append(record)
            continue
        section = match.group("section")
        record["background"] = "background-image:" in section
        figure_match = re.search(r'<figure\b(?P<attrs>[^>]*)>', section, re.I)
        record["figure"] = bool(figure_match)
        if figure_match:
            attrs = figure_match.group("attrs")
            class_match = re.search(r'class=["\']([^"\']*)["\']', attrs, re.I)
            classes = set((class_match.group(1) if class_match else "").split())
            record["inline_figure"] = "art-inline" in classes and not ({"art-cover", "art-full-page"} & classes)
            record["full_page_class"] = bool({"art-cover", "art-full-page"} & classes)
            if record["inline_figure"]:
                findings.append({"code": "frontmatter_cover_art_inline", "page": page, "classes": sorted(classes)})
            if not record["full_page_class"]:
                findings.append({"code": "frontmatter_cover_art_not_full_page", "page": page, "classes": sorted(classes)})
        if not record["figure"] and not record["background"]:
            findings.append({"code": "frontmatter_cover_art_missing", "page": page})
        cover_results.append(record)
    if cover_results:
        cover_css_ok = all(
            token in html_text
            for token in [
                ".production-page.page-type-cover figure",
                ".production-page.page-type-cover figure img",
                "max-height: 252mm",
            ]
        )
        checks["frontmatter_cover_pages"] = cover_results
        checks["frontmatter_cover_full_page_css"] = cover_css_ok
        if not cover_css_ok:
            findings.append({"code": "frontmatter_cover_full_page_css_missing"})

    if suppress_source_cover:
        source_cover_pages = [page for page, meta in page_map.items() if str(meta.get("type") or "") == "cover"]
        visible_source_cover_pages = [
            page
            for page in source_cover_pages
            if re.search(rf'<section\b[^>]*\bid=["\']page-{re.escape(page)}["\']', html_text, re.I)
        ]
        checks["source_cover_suppressed"] = not visible_source_cover_pages
        if visible_source_cover_pages:
            findings.append({"code": "source_cover_page_visible_after_suppression", "pages": visible_source_cover_pages})

    if "Оглавление" in html_text or "Содержание" in html_text:
        source_toc_pages = [page for page, meta in page_map.items() if str(meta.get("type") or "") == "source_toc"]
        rendered_toc_pages = len(re.findall(r'<nav\b[^>]*\bclass=["\'][^"\']*\btoc\b[^"\']*["\']', html_text, re.I))
        toc_cfg = production_html_config(config).get("toc_policy", {})
        toc_mode = str(toc_cfg.get("mode", "generated")) if isinstance(toc_cfg, dict) else "generated"
        generated_toc_expected = toc_mode != "disabled"
        if source_toc_pages:
            toc_count_ok = rendered_toc_pages == len(source_toc_pages)
        else:
            toc_count_ok = (rendered_toc_pages == 1) if generated_toc_expected else (rendered_toc_pages == 0)
        checks["toc_page_count_matches_source"] = {
            "source_toc_pages": len(source_toc_pages),
            "rendered_toc_pages": rendered_toc_pages,
            "generated_toc_expected": generated_toc_expected,
            "ok": toc_count_ok,
        }
        if source_toc_pages and rendered_toc_pages != len(source_toc_pages):
            findings.append(
                {
                    "code": "toc_page_count_mismatch",
                    "source_toc_pages": len(source_toc_pages),
                    "rendered_toc_pages": rendered_toc_pages,
                }
            )
        if not source_toc_pages and not toc_count_ok:
            findings.append(
                {
                    "code": "generated_toc_count_mismatch",
                    "expected": 1 if generated_toc_expected else 0,
                    "rendered_toc_pages": rendered_toc_pages,
                }
            )
        source_toc_title = None
        source_toc_match = re.search(r'<nav\b[^>]*\bdata-toc-origin=["\']source["\'][^>]*>[\s\S]*?<h1>(.*?)</h1>', html_text, re.I)
        if source_toc_match:
            source_toc_title = re.sub(r"<[^>]+>", "", source_toc_match.group(1)).strip()
        toc_title_ok = bool(source_toc_title) or bool(
            re.search(r'<nav\b[^>]*\bclass=["\'][^"\']*\btoc\b[^"\']*["\'][\s\S]*?<h1>Оглавление</h1>', html_text, re.I)
        )
        checks["production_toc_title_preserved_or_generated"] = {
            "ok": toc_title_ok,
            "source_title": source_toc_title,
        }
        if not toc_title_ok:
            findings.append({"code": "production_toc_title_missing"})
        if source_toc_title is None and re.search(r'<nav\b[^>]*\bclass=["\'][^"\']*\btoc\b[^"\']*["\'][\s\S]*?<h1>Содержание</h1>', html_text, re.I):
            findings.append({"code": "production_toc_uses_soderzhanie_title"})
        toc_spacing_ok = bool(
            re.search(r'\.toc ol\s*\{[^}]*margin-top:\s*(?:1[6-9]|[2-9]\d)px', html_text, re.I)
            or re.search(r'\.toc ol\s*\{[^}]*margin-top:\s*(?:1\.[2-9]|[2-9])em', html_text, re.I)
        )
        checks["production_toc_body_offset_after_rule"] = toc_spacing_ok
        if not toc_spacing_ok:
            warnings.append({"code": "production_toc_body_offset_not_detected"})
        toc_fit_ok = bool(
            re.search(r'\.toc\s*\{[^}]*min-height:\s*\d+(?:mm|px|vh)[^}]*overflow:\s*hidden', html_text, re.I | re.S)
            and re.search(r'\.toc\s*\{[^}]*break-after:\s*page', html_text, re.I | re.S)
        )
        checks["production_toc_fit_on_one_page_css"] = toc_fit_ok
        if not toc_fit_ok:
            findings.append({"code": "production_toc_fit_on_one_page_css_missing"})

    quote_pages = [page for page, meta in page_map.items() if str(meta.get("type") or "") == "quote_art"]
    quote_results: list[dict[str, Any]] = []
    for page in quote_pages:
        match = re.search(
            rf'(?P<section><section\b(?=[^>]*\bid=["\']page-{re.escape(page)}["\'])(?=[^>]*\bclass=["\'][^"\']*\bpage-type-quote-art\b)[^>]*>[\s\S]*?</section>)',
            html_text,
            re.I,
        )
        record = {"page": page, "section": bool(match), "background": False, "inline_figure": False}
        if not match:
            findings.append({"code": "quote_art_section_missing", "page": page})
            quote_results.append(record)
            continue
        section = match.group("section")
        record["background"] = "background-image:" in section
        record["inline_figure"] = "<figure" in section
        if not record["background"]:
            findings.append({"code": "quote_art_missing_background_image", "page": page})
        if record["inline_figure"]:
            findings.append({"code": "quote_art_kept_inline_figure", "page": page})
        quote_results.append(record)
    if quote_pages:
        quote_css_ok = all(
            token in html_text
            for token in [
                ".production-page.page-type-quote-art",
                "background: transparent",
                "text-shadow:",
            ]
        )
        checks["quote_art_css_full_page_overlay"] = quote_css_ok
        checks["quote_art_pages"] = quote_results
        if not quote_css_ok:
            findings.append({"code": "quote_art_overlay_css_missing"})

    if "art-full-width" in html_text:
        page_flow_variants = [
            variant
            for variant in dict(production_pdf_config(config).get("variants", {})).values()
            if isinstance(variant, dict) and variant.get("layout_mode") == "page_flow_columns"
        ]
        page_flow_keeps_art_in_columns = any(
            "art-full-width" not in [
                str(value)
                for value in ((variant.get("art_column_policy") or {}).get("not_columnned_classes") or [])
            ]
            for variant in page_flow_variants
        )
        full_width_css_ok = bool(
            re.search(r'body\.print-columns-2\s+figure\.art-full-width\s*\{[^}]*column-span:\s*all', html_text, re.I)
        )
        full_width_configured = any(
            "art-full-width" in [str(value) for value in ((variant.get("art_column_policy") or {}).get("not_columnned_classes") or [])]
            for variant in dict(production_pdf_config(config).get("variants", {})).values()
            if isinstance(variant, dict)
        )
        checks["art_full_width_page_flow_keeps_art_in_columns"] = page_flow_keeps_art_in_columns
        if not page_flow_keeps_art_in_columns:
            checks["art_full_width_escapes_print_columns"] = full_width_css_ok
            checks["art_full_width_not_columnned_class_configured"] = full_width_configured
            if not full_width_css_ok:
                findings.append({"code": "art_full_width_not_excluded_from_columns"})
            if not full_width_configured:
                findings.append({"code": "art_full_width_not_columnned_class_not_configured"})

    credits_pages = [page for page, meta in page_map.items() if str(meta.get("type") or "") == "credits"]
    credits_policy = production_html_config(config).get("credits_policy", {})
    require_credits_background_image = not isinstance(credits_policy, dict) or credits_policy.get("require_background_image", True)
    require_credits_page_boundary = not isinstance(credits_policy, dict) or credits_policy.get("force_page_boundary", True) is not False
    credits_results: list[dict[str, Any]] = []
    for page in credits_pages:
        match = re.search(
            rf'(?P<section><section\b(?=[^>]*\bid=["\']page-{re.escape(page)}["\'])(?=[^>]*\bclass=["\'][^"\']*\bpage-type-credits\b)[^>]*>[\s\S]*?</section>)',
            html_text,
            re.I,
        )
        record = {
            "page": page,
            "section": bool(match),
            "background": False,
            "frame": False,
            "columns": False,
            "preceding_h1": False,
            "page_boundary": False,
            "profile": None,
            "profile_matches_config": False,
        }
        if not match:
            findings.append({"code": "credits_section_missing", "page": page})
            credits_results.append(record)
            continue
        section = match.group("section")
        record["page_boundary"] = bool(re.match(r'\s*<div\b[^>]*\bclass=["\'][^"\']*\bcredits-page-boundary\b', html_text[match.end("section") :], re.I))
        prefix = html_text[: match.start("section")]
        record["preceding_h1"] = bool(re.search(
            rf'<h1\b[^>]*>[\s\S]*?</h1>\s*<!--\s*(?:source-page|pdf-page)-{re.escape(page)}\s*-->\s*$',
            prefix,
            re.I,
        ))
        record["background"] = "background-image:" in section
        record["frame"] = 'class="credits-frame"' in section
        record["columns"] = 'class="credits-columns"' in section
        profile_match = re.search(r'<div\b[^>]*\bclass="credits-columns"[^>]*\bdata-credits-profile="(?P<profile>[^"]+)"[^>]*\bstyle="(?P<style>[^"]*)"', section, re.I)
        expected_profile, expected_values = credits_layout_profile(config)
        if profile_match:
            record["profile"] = profile_match.group("profile")
            expected_style = [
                f'--credits-columns: {expected_values["columns"]}',
                f'--credits-font-size: {expected_values["font_size"]}',
                f'--credits-line-height: {expected_values["line_height"]}',
                f'--credits-column-gap: {expected_values["column_gap"]}',
            ]
            record["profile_matches_config"] = (
                profile_match.group("profile") == expected_profile
                and all(token in profile_match.group("style") for token in expected_style)
            )
        if require_credits_background_image and not record["background"]:
            findings.append({"code": "credits_missing_background_image", "page": page})
        if not record["frame"]:
            findings.append({"code": "credits_missing_frame", "page": page})
        if not record["columns"]:
            findings.append({"code": "credits_missing_columns", "page": page})
        if record["preceding_h1"] and not bool(credits_policy.get("keep_preceding_heading", False)):
            findings.append({"code": "credits_preceding_heading_outside_section", "page": page})
        if require_credits_page_boundary and not record["page_boundary"]:
            findings.append({"code": "credits_page_boundary_missing", "page": page})
        if not record["profile_matches_config"]:
            findings.append({"code": "credits_layout_profile_missing_or_mismatched", "page": page, "expected_profile": expected_profile})
        credits_results.append(record)
    if credits_pages:
        credits_css_ok = all(
            token in html_text
            for token in [
                ".production-page.page-type-credits .credits-frame",
                ".production-page.page-type-credits .credits-columns",
                "columns: var(--credits-columns, 2)",
                "font-size: var(--credits-font-size, 10pt)",
                "overflow-wrap: anywhere",
                "print-color-adjust: exact",
                ".credits-page-boundary",
                "break-before: page",
            ]
        )
        checks["credits_visual_page_layout"] = credits_results
        checks["credits_print_background_frame_css"] = credits_css_ok
        checks["credits_overflow_guard_css"] = credits_css_ok
        if not credits_css_ok:
            findings.append({"code": "credits_print_background_frame_css_missing"})

    heading_css_checks = {
        "h1_uppercase_bold": bool(re.search(r'h1\s*\{[^}]*text-transform:\s*uppercase[^}]*font-weight:\s*700', html_text, re.I | re.S)),
        "h2_sentence_case_bold": bool(re.search(r'h2\s*\{[^}]*text-transform:\s*none[^}]*font-weight:\s*700', html_text, re.I | re.S)),
        "h3_plus_sentence_case_regular": bool(re.search(r'h3,\s*h4,\s*h5,\s*h6\s*\{[^}]*text-transform:\s*none[^}]*font-weight:\s*400', html_text, re.I | re.S)),
    }
    checks["heading_typography_normalization"] = heading_css_checks
    for code, ok in heading_css_checks.items():
        if not ok:
            findings.append({"code": f"heading_typography_{code}_missing"})

    typography = html_typography_config(config)
    typography_checks = {
        "body_font_size": typography["body_font_size"] in html_text,
        "body_line_height": f"/{typography['body_line_height']}" in html_text or f"line-height: {typography['body_line_height']}" in html_text,
        "print_body_font_size": f"font-size: {typography['print_body_font_size']}" in html_text,
        "print_body_line_height": f"line-height: {typography['print_body_line_height']}" in html_text,
    }
    checks["configured_typography_present"] = typography_checks
    for code, ok in typography_checks.items():
        if not ok:
            findings.append({"code": f"configured_typography_{code}_missing"})

    rendered_statblock_cards = html_class_token_count(html_text, "statblock-card")
    checks["statblock_cards"] = rendered_statblock_cards
    statblock_heading_ids = statblock_section_heading_ids(config)
    statblock_results: list[dict[str, Any]] = []
    for heading_id in statblock_heading_ids:
        inside = bool(
            re.search(
                rf'<div\b[^>]*\bclass=["\'][^"\']*\bstatblock-card\b[^"\']*["\'][\s\S]*?<h[1-6]\b[^>]*\bid=["\']{re.escape(heading_id)}["\']',
                html_text,
                re.I,
            )
        )
        outside_before_card = bool(
            re.search(
                rf'<h[1-6]\b[^>]*\bid=["\']{re.escape(heading_id)}["\'][^>]*>[\s\S]*?</h[1-6]>\s*<div\b[^>]*\bclass=["\'][^"\']*\bstatblock-card\b',
                html_text,
                re.I,
            )
        )
        statblock_results.append({"heading_id": heading_id, "inside_card": inside, "outside_before_card": outside_before_card})
        if not inside:
            findings.append({"code": "statblock_heading_not_inside_card", "heading_id": heading_id})
        if outside_before_card and not inside:
            findings.append({"code": "statblock_heading_detached_before_card", "heading_id": heading_id})
    if statblock_heading_ids:
        css_ok = ".statblock-card h2, .statblock-card h3" in html_text
        checks["statblock_headings_inside_cards"] = statblock_results
        checks["statblock_h2_h3_css"] = css_ok
        if not css_ok:
            warnings.append({"code": "statblock_h2_h3_css_not_detected"})

    return checks, findings, warnings


def run_release_qa(config_path: Path, *, check_only: bool = False) -> dict[str, Any]:
    config = read_json(config_path)
    release = release_qa_config(config)
    report = release_qa_report_path(config)
    outputs = config.get("production_outputs", {})
    html = root_path(str(release.get("html") or outputs.get("html"))) if (release.get("html") or outputs.get("html")) else None
    pdf = root_path(str(release.get("pdf") or outputs.get("pdf"))) if (release.get("pdf") or outputs.get("pdf")) else None
    images_root = root_path(str(outputs["images"])) if outputs.get("images") else None
    findings: list[dict[str, Any]] = []
    warnings: list[dict[str, Any]] = []
    hashes: dict[str, Any] = {}
    semantic_checks: dict[str, Any] = {}
    gates = config.get("scenario_gates") or config.get("production_gates") or {}
    required_gates = list(release.get("required_gates", ["production_html_built"]))
    for gate in required_gates:
        if gates.get(gate) is not True:
            findings.append({"code": "required_gate_not_true", "gate": gate, "value": gates.get(gate)})
    selected_variant = production_pdf_config(config).get("selected_variant")
    selected_pdf: Path | None = production_pdf_target_path(config, str(selected_variant)) if selected_variant else None
    selected_pdf_report: Path | None = production_pdf_report_path(config, str(selected_variant)) if selected_variant else None
    selected_pdf_print_report: Path | None = pdf_print_qa_report_path(config, str(selected_variant)) if selected_variant else None
    release_pdf_print_report = release.get("pdf_print_qa_report")
    required_pdf_variants = [str(item) for item in release.get("required_pdf_variants", [])]
    report_dependency_paths = release_report_dependency_paths(config, release)
    report_dependencies: list[dict[str, Any]] = []
    report_data_by_label: dict[str, dict[str, Any]] = {}
    configured_required_reports = list(release.get("required_reports", []))
    if package_has_visual_art_contract(config) and "critical_remediation_gate" not in configured_required_reports:
        configured_required_reports.append("critical_remediation_gate")
    if release.get("require_nonempty_required_reports", False) and not configured_required_reports:
        findings.append({"code": "required_release_reports_empty"})
    for label in configured_required_reports:
        path = report_dependency_paths.get(str(label))
        if path is None:
            findings.append({"code": "unknown_required_release_report", "label": label})
            continue
        record: dict[str, Any] = {"label": str(label), "path": rel(path), "exists": path.exists(), "status": None}
        if not path.exists():
            findings.append({"code": "missing_required_release_report", "label": label, "path": rel(path)})
        else:
            try:
                data = read_json(path)
                report_data_by_label[str(label)] = data
                status = data.get("status")
                record["status"] = status
                if status not in {"pass", "warning"}:
                    findings.append({"code": "required_release_report_not_pass", "label": label, "path": rel(path), "status": status})
                if str(label) == "runtime_image_cleanup":
                    rebuildability = data.get("rebuildability", {})
                    if rebuildability.get("production_html_clean_rebuild_ready") is False:
                        warnings.append(
                            {
                                "code": "production_html_clean_rebuild_not_ready",
                                "label": label,
                                "path": rel(path),
                                "missing_required_runtime_assets": len(rebuildability.get("missing_required_runtime_assets", [])),
                            }
                        )
            except Exception as exc:
                findings.append({"code": "required_release_report_unreadable", "label": label, "path": rel(path), "message": str(exc)})
        report_dependencies.append(record)
    if html is None or not html.exists():
        findings.append({"code": "missing_release_html", "path": rel(html) if html else None})
        html_text = ""
    else:
        html_text = html.read_text(encoding="utf-8")
        hashes["html_sha256"] = sha256_file(html)
        if re.search(r"[A-Za-z]:\\|file:///", html_text):
            findings.append({"code": "absolute_local_path_in_html"})
        ids = set(re.findall(r'id=["\']([^"\']+)["\']', html_text))
        for href in re.findall(r'href=["\']#([^"\']+)["\']', html_text):
            if href not in ids:
                findings.append({"code": "missing_internal_link_target", "target": href})
        for src in html_refs(html_text):
            if "://" in src or src.startswith("data:"):
                continue
            target = (html.parent / src.replace("/", "\\")).resolve()
            if not target.exists():
                findings.append({"code": "missing_image_ref", "src": src})
            elif images_root is not None and images_root.exists() and images_root.resolve() not in {target, *target.parents}:
                warnings.append({"code": "image_outside_images_root", "src": src, "path": rel(target)})
        semantic_checks, semantic_findings, semantic_warnings = production_html_semantic_qa(config, html_text)
        findings.extend(semantic_findings)
        warnings.extend(semantic_warnings)
    if package_has_visual_art_contract(config):
        critical_report = report_data_by_label.get("critical_remediation_gate")
        critical_html_hash = nested_report_value(critical_report or {}, "hashes.html_sha256")
        if html is None or not html.exists() or not isinstance(critical_html_hash, str):
            findings.append({"code": "critical_remediation_evidence_unverifiable"})
        elif critical_html_hash != hashes.get("html_sha256"):
            findings.append({"code": "critical_remediation_not_current_html", "path": rel(html)})
    report_minima = release.get("required_report_minima", {})
    if report_minima and not isinstance(report_minima, dict):
        findings.append({"code": "invalid_required_report_minima"})
    elif isinstance(report_minima, dict):
        for label, minima in report_minima.items():
            data = report_data_by_label.get(str(label))
            if not isinstance(minima, dict):
                findings.append({"code": "invalid_required_report_minimum", "label": label})
                continue
            if data is None:
                findings.append({"code": "required_report_minimum_without_report", "label": label})
                continue
            for field, expected in minima.items():
                actual = nested_report_value(data, str(field))
                if not report_minimum_satisfied(actual, expected):
                    findings.append(
                        {
                            "code": "required_report_semantic_minimum_not_met",
                            "label": label,
                            "field": field,
                            "expected": expected,
                            "actual": actual,
                        }
                    )
    semantic_minima = release.get("semantic_minima", {})
    if semantic_minima and not isinstance(semantic_minima, dict):
        findings.append({"code": "invalid_release_semantic_minima"})
    elif isinstance(semantic_minima, dict):
        for field, expected in semantic_minima.items():
            actual = nested_report_value(semantic_checks, str(field))
            if not report_minimum_satisfied(actual, expected):
                findings.append({"code": "release_semantic_minimum_not_met", "field": field, "expected": expected, "actual": actual})
    freshness = release.get("evidence_freshness", [])
    if freshness and not isinstance(freshness, list):
        findings.append({"code": "invalid_evidence_freshness_config"})
    elif isinstance(freshness, list):
        for requirement in freshness:
            if not isinstance(requirement, dict):
                findings.append({"code": "invalid_evidence_freshness_requirement"})
                continue
            label = str(requirement.get("report") or "")
            field = str(requirement.get("field") or "sha256")
            evidence_path = root_path(str(requirement["path"])) if requirement.get("path") else None
            expected_hash = nested_report_value(report_data_by_label.get(label, {}), field)
            if evidence_path is None or not evidence_path.exists() or not isinstance(expected_hash, str):
                findings.append({"code": "stale_evidence_unverifiable", "report": label, "field": field})
            elif expected_hash != sha256_file(evidence_path):
                findings.append({"code": "stale_evidence_hash_mismatch", "report": label, "field": field, "path": rel(evidence_path)})
    blocker_path, open_blockers, blocker_findings = release_open_blockers(release)
    findings.extend(blocker_findings)
    blocker_config = release.get("open_blocker_ledger")
    if open_blockers and (not isinstance(blocker_config, dict) or blocker_config.get("fail_on_open", True)):
        findings.append({"code": "open_release_blockers", "path": rel(blocker_path) if blocker_path else None, "count": len(open_blockers)})
    if release.get("require_pdf", False) and (pdf is None or not pdf.exists()):
        findings.append({"code": "missing_release_pdf", "path": rel(pdf) if pdf else None})
    elif pdf is not None and not pdf.exists():
        warnings.append({"code": "pdf_not_built", "path": rel(pdf)})
    elif pdf is not None and pdf.exists():
        hashes["pdf_sha256"] = sha256_file(pdf)
    variant_dependencies: list[dict[str, Any]] = []
    for required_variant in required_pdf_variants:
        try:
            variant_pdf = production_pdf_target_path(config, required_variant)
            variant_pdf_report = production_pdf_report_path(config, required_variant)
            variant_pdf_print_report = pdf_print_qa_report_path(config, required_variant)
        except Exception as exc:
            findings.append({"code": "invalid_required_pdf_variant", "variant": required_variant, "message": str(exc)})
            continue
        record: dict[str, Any] = {
            "variant": required_variant,
            "pdf": rel(variant_pdf),
            "pdf_exists": variant_pdf.exists(),
            "build_report": rel(variant_pdf_report),
            "print_qa_report": rel(variant_pdf_print_report),
            "build_status": None,
            "print_qa_status": None,
        }
        if not variant_pdf.exists():
            findings.append({"code": "missing_required_variant_pdf", "variant": required_variant, "path": rel(variant_pdf)})
        else:
            hashes[f"{required_variant}_pdf_sha256"] = sha256_file(variant_pdf)
        for label, path in [("build", variant_pdf_report), ("print_qa", variant_pdf_print_report)]:
            if not path.exists():
                findings.append({"code": f"missing_required_variant_{label}_report", "variant": required_variant, "path": rel(path)})
                continue
            try:
                data = read_json(path)
                record[f"{label}_status"] = data.get("status")
                if data.get("status") not in {"pass", "warning"}:
                    findings.append({"code": f"required_variant_{label}_not_pass", "variant": required_variant, "status": data.get("status"), "path": rel(path)})
                if label == "print_qa":
                    if data.get("variant") != required_variant:
                        findings.append({"code": "required_variant_print_qa_variant_mismatch", "variant": required_variant, "actual": data.get("variant"), "path": rel(path)})
                    if variant_pdf.exists() and data.get("hashes", {}).get("pdf_sha256") != sha256_file(variant_pdf):
                        findings.append({"code": "required_variant_print_qa_pdf_hash_mismatch", "variant": required_variant, "path": rel(path)})
            except Exception as exc:
                findings.append({"code": f"required_variant_{label}_report_unreadable", "variant": required_variant, "path": rel(path), "message": str(exc)})
        variant_dependencies.append(record)
    if production_pdf_config(config).get("require_variant", False) and not required_pdf_variants:
        findings.append({"code": "required_pdf_variants_not_configured"})
    if production_pdf_config(config).get("require_variant", False) and release.get("require_pdf", False):
        findings.append({"code": "variant_only_release_must_not_require_main_pdf"})
    if selected_variant:
        selected_pdf_report_data: dict[str, Any] = {}
        selected_variant_promoted_to_canonical = False
        if selected_pdf_report is None or not selected_pdf_report.exists():
            findings.append(
                {
                    "code": "missing_selected_variant_pdf_report",
                    "variant": selected_variant,
                    "path": rel(selected_pdf_report) if selected_pdf_report else None,
                }
            )
        else:
            try:
                selected_pdf_report_data = read_json(selected_pdf_report)
                if html is not None and html.exists() and selected_pdf_report_data.get("source_html_sha256") != sha256_file(html):
                    findings.append(
                        {
                            "code": "selected_pdf_not_built_from_current_html",
                            "variant": selected_variant,
                            "report": rel(selected_pdf_report),
                        }
                    )
                if selected_pdf is not None and selected_pdf.exists() and selected_pdf_report_data.get("sha256") != sha256_file(selected_pdf):
                    findings.append(
                        {
                            "code": "selected_pdf_report_hash_mismatch",
                            "variant": selected_variant,
                            "report": rel(selected_pdf_report),
                        }
                    )
                if selected_pdf is not None and not selected_pdf.exists() and pdf is not None and pdf.exists():
                    selected_variant_promoted_to_canonical = selected_pdf_report_data.get("sha256") == sha256_file(pdf)
            except Exception as exc:
                findings.append({"code": "selected_pdf_report_unreadable", "variant": selected_variant, "message": str(exc)})
        if selected_pdf is None or not selected_pdf.exists():
            if selected_variant_promoted_to_canonical:
                warnings.append(
                    {
                        "code": "selected_variant_file_pruned_after_canonical_promotion",
                        "variant": selected_variant,
                        "selected_pdf": rel(selected_pdf) if selected_pdf else None,
                        "canonical_pdf": rel(pdf) if pdf else None,
                    }
                )
                if pdf is not None and pdf.exists():
                    hashes["selected_pdf_sha256"] = sha256_file(pdf)
            else:
                findings.append({"code": "missing_selected_variant_pdf", "variant": selected_variant, "path": rel(selected_pdf) if selected_pdf else None})
        else:
            hashes["selected_pdf_sha256"] = sha256_file(selected_pdf)
        if pdf is not None and selected_pdf is not None and pdf.exists() and selected_pdf.exists():
            if sha256_file(pdf) != sha256_file(selected_pdf):
                findings.append(
                    {
                        "code": "canonical_pdf_not_selected_variant",
                        "variant": selected_variant,
                        "canonical_pdf": rel(pdf),
                        "selected_pdf": rel(selected_pdf),
                    }
                )
        if selected_pdf_print_report is not None and selected_pdf_print_report.exists():
            try:
                pdf_print_data = read_json(selected_pdf_print_report)
                if pdf_print_data.get("variant") != selected_variant:
                    findings.append(
                        {
                            "code": "pdf_print_qa_variant_mismatch",
                            "expected": selected_variant,
                            "actual": pdf_print_data.get("variant"),
                            "report": rel(selected_pdf_print_report),
                        }
                    )
                report_hashes = pdf_print_data.get("hashes", {})
                if html is not None and html.exists() and report_hashes.get("html_sha256") != sha256_file(html):
                    findings.append({"code": "pdf_print_qa_not_current_html", "report": rel(selected_pdf_print_report)})
                selected_hash = sha256_file(selected_pdf) if selected_pdf is not None and selected_pdf.exists() else None
                canonical_hash = sha256_file(pdf) if pdf is not None and pdf.exists() else None
                expected_pdf_hash = selected_hash or (canonical_hash if selected_variant_promoted_to_canonical else None)
                if expected_pdf_hash and report_hashes.get("pdf_sha256") != expected_pdf_hash:
                    findings.append({"code": "pdf_print_qa_pdf_hash_mismatch", "report": rel(selected_pdf_print_report)})
            except Exception as exc:
                findings.append({"code": "pdf_print_qa_report_unreadable", "path": rel(selected_pdf_print_report), "message": str(exc)})

    result = {
        "schema": "translator_release_qa.v1",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "config": rel(config_path),
        "status": "blocked" if findings else "pass",
        "action": "check_only" if check_only else "checked",
        "required_gates": required_gates,
        "html": rel(html) if html else None,
        "pdf": rel(pdf) if pdf else None,
        "selected_variant": selected_variant,
        "selected_pdf": rel(selected_pdf) if selected_pdf else None,
        "hashes": hashes,
        "counts": {
            "image_refs": len(html_refs(html_text)),
            "required_reports": len(report_dependencies),
            "required_pdf_variants": len(variant_dependencies),
            "semantic_checks": len(semantic_checks),
            "open_blockers": len(open_blockers),
            "findings": len(findings),
            "warnings": len(warnings),
        },
        "semantic_checks": semantic_checks,
        "required_reports": report_dependencies,
        "required_pdf_variants": variant_dependencies,
        "open_blocker_ledger": {"path": rel(blocker_path) if blocker_path else None, "open": open_blockers},
        "findings": findings,
        "warnings": warnings,
        "approval_state": {
            "production_html_built": gates.get("production_html_built") is True,
            "production_pdf_built": gates.get("production_pdf_built") is True,
            "production_approved": gates.get("production_approved") is True,
        },
    }
    write_json(report, result)
    return result


def legacy_script_audit_config(config: dict[str, Any]) -> dict[str, Any]:
    return config.get("legacy_script_audit", {})


def legacy_script_audit_report_path(config: dict[str, Any]) -> Path:
    audit = legacy_script_audit_config(config)
    value = audit.get("report", "legacy_script_audit.json")
    path = Path(str(value).replace("/", "\\"))
    return path.resolve() if path.is_absolute() else qa_root(config) / path


def script_files_under(paths: list[str]) -> list[Path]:
    files: list[Path] = []
    for value in paths:
        root = root_path(value)
        if root.is_file():
            files.append(root)
            continue
        if not root.exists():
            continue
        for suffix in ("*.py", "*.ps1", "*.js"):
            files.extend(root.rglob(suffix))
    return sorted(set(files))


def audit_legacy_script(path: Path) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8", errors="replace")
    hardcoded_patterns = [
        r"Dune[/\\]Output[/\\]Scenarios[/\\]Wormsign",
        r"Output[/\\]Scenarios[/\\]Wormsign",
        r"Scenarios[/\\]Wormsign",
        r"project[/\\]Production",
    ]
    cli_args = len(re.findall(r"add_argument\(", text))
    config_mentions = len(re.findall(r"--config|package_config|package-config|read_json\(.*config|DEFAULT_CONFIG", text))
    env_root = "NRI_ROOT" in text
    hardcoded_hits = []
    for pattern in hardcoded_patterns:
        count = len(re.findall(pattern, text, re.I))
        if count:
            hardcoded_hits.append({"pattern": pattern, "count": count})
    if config_mentions and cli_args and not hardcoded_hits:
        migration_state = "config_driven"
    elif config_mentions and cli_args:
        migration_state = "partial_adapter"
    elif cli_args:
        migration_state = "cli_only"
    else:
        migration_state = "hardcoded_legacy"
    return {
        "path": rel(path),
        "bytes": path.stat().st_size,
        "migration_state": migration_state,
        "cli_arg_count": cli_args,
        "config_mentions": config_mentions,
        "uses_nri_root_env": env_root,
        "hardcoded_hits": hardcoded_hits,
    }


def run_legacy_script_audit(config_path: Path) -> dict[str, Any]:
    config = read_json(config_path)
    audit = legacy_script_audit_config(config)
    roots = list(audit.get("script_roots", ["translator/scripts/wormsign", "Dune/Scripts"]))
    report = legacy_script_audit_report_path(config)
    files = script_files_under(roots)
    items = [audit_legacy_script(path) for path in files]
    counts: dict[str, int] = {}
    for item in items:
        state = str(item["migration_state"])
        counts[state] = counts.get(state, 0) + 1
    hardcoded = [item for item in items if item["hardcoded_hits"]]
    no_env = [item for item in items if not item["uses_nri_root_env"] and item["path"].startswith("translator/scripts/wormsign/")]
    result = {
        "schema": "translator_legacy_script_audit.v1",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "config": rel(config_path),
        "status": "needs_migration" if hardcoded else "pass",
        "script_roots": roots,
        "counts": {
            "files": len(items),
            "hardcoded_path_files": len(hardcoded),
            "translator_wormsign_without_nri_root_env": len(no_env),
            "by_migration_state": dict(sorted(counts.items())),
        },
        "items": items,
        "next_migration_targets": [
            item for item in items
            if item["migration_state"] in {"hardcoded_legacy", "cli_only", "partial_adapter"}
        ][:40],
    }
    write_json(report, result)
    md_path = report.with_suffix(".md")
    lines = [
        "# Legacy Script Migration Audit",
        "",
        f"Generated: `{result['generated_at_utc']}`",
        f"Status: `{result['status']}`",
        "",
        "## Counts",
        "",
        f"- files: `{result['counts']['files']}`",
        f"- hardcoded path files: `{result['counts']['hardcoded_path_files']}`",
        f"- translator/wormsign files without `NRI_ROOT`: `{result['counts']['translator_wormsign_without_nri_root_env']}`",
        "",
        "## Migration States",
        "",
    ]
    for state, count in sorted(counts.items()):
        lines.append(f"- `{state}`: `{count}`")
    lines.extend(["", "## Next Migration Targets", ""])
    lines.extend(["| State | File | Hardcoded hits |", "|---|---|---:|"])
    for item in result["next_migration_targets"]:
        lines.append(f"| `{item['migration_state']}` | `{item['path']}` | {len(item['hardcoded_hits'])} |")
    md_path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")
    return result


def production_pdf_config(config: dict[str, Any]) -> dict[str, Any]:
    return config.get("production_pdf", {})


def production_pdf_variant_config(config: dict[str, Any], variant: str | None) -> dict[str, Any]:
    if not variant:
        return {}
    variants = production_pdf_config(config).get("variants", {})
    if not isinstance(variants, dict) or variant not in variants:
        raise KeyError(f"Unknown production PDF variant: {variant}")
    value = variants[variant]
    if not isinstance(value, dict):
        raise TypeError(f"production_pdf.variants.{variant} must be an object")
    return value


def production_pdf_report_path(config: dict[str, Any], variant: str | None = None) -> Path:
    variant_cfg = production_pdf_variant_config(config, variant)
    if variant_cfg.get("report"):
        value = variant_cfg["report"]
    elif variant:
        base = str(production_pdf_config(config).get("report", "production_pdf_report.json"))
        stem = Path(base).stem
        suffix = Path(base).suffix or ".json"
        value = f"{stem}_{variant}{suffix}"
    else:
        value = production_pdf_config(config).get("report", "production_pdf_report.json")
    path = Path(str(value).replace("/", "\\"))
    return path.resolve() if path.is_absolute() else qa_root(config) / path


def production_pdf_html_path(config: dict[str, Any]) -> Path:
    pdf_cfg = production_pdf_config(config)
    if pdf_cfg.get("source_html"):
        return root_path(str(pdf_cfg["source_html"]))
    return root_path(str(config["production_outputs"]["html"]))


def production_pdf_target_path(config: dict[str, Any], variant: str | None = None) -> Path:
    variant_cfg = production_pdf_variant_config(config, variant)
    if variant_cfg.get("output_pdf"):
        return root_path(str(variant_cfg["output_pdf"]))
    pdf_cfg = production_pdf_config(config)
    if pdf_cfg.get("output_pdf"):
        return root_path(str(pdf_cfg["output_pdf"]))
    return root_path(str(config["production_outputs"]["pdf"]))


def production_pdf_required_gates(config: dict[str, Any]) -> list[str]:
    return list(production_pdf_config(config).get("required_gates", ["production_html_built"]))


def production_pdf_entry_findings(config: dict[str, Any], html_path: Path, *, variant: str | None = None) -> list[dict[str, Any]]:
    findings: list[dict[str, Any]] = []
    if production_pdf_config(config).get("require_variant", False) and not variant:
        findings.append(
            {
                "code": "variant_required_for_production_pdf",
                "message": "This package publishes explicit one_column/two_column PDFs only; variantless main PDF build is disabled.",
            }
        )
    gates = config.get("scenario_gates") or config.get("production_gates") or {}
    for gate in production_pdf_required_gates(config):
        if gates.get(gate) is not True:
            findings.append({"code": "required_gate_not_true", "gate": gate, "message": f"Required gate is not true: {gate}"})
    if not html_path.exists():
        findings.append({"code": "missing_source_html", "path": rel(html_path), "message": "Production PDF source HTML does not exist."})
    if not production_pdf_config(config).get("engine_command"):
        findings.append({"code": "missing_pdf_engine", "message": "production_pdf.engine_command is not configured."})
    return findings


def page_flow_variant_html_policy_checks(html_text: str, variant_cfg: dict[str, Any]) -> dict[str, Any]:
    """Verify that only configured page-flow exceptions leave the columns."""
    broad_display_contents = bool(
        re.search(
            r'body\.pdf-layout-page-flow-columns\s+\.production-page\s*\{[^}]*display:\s*contents\s*!important',
            html_text,
            re.I,
        )
    )
    scoped_display_contents = bool(
        re.search(
            r'body\.pdf-layout-page-flow-columns\s+\.production-page:not\([^}]*display:\s*contents\s*!important',
            html_text,
            re.I,
        )
    )
    raw_types = variant_cfg.get("page_flow_exempt_page_types", ["cover"])
    page_types = [
        str(value).strip().replace("_", "-")
        for value in raw_types
        if str(value).strip()
    ] if isinstance(raw_types, list) else ["cover"]
    raw_pages = variant_cfg.get("page_flow_exempt_pages", [])
    page_ids = [
        str(value).strip().zfill(3)
        for value in raw_pages
        if str(value).strip().isdigit()
    ] if isinstance(raw_pages, list) else []
    expected_selectors = [
        f".production-page.page-type-{page_type}" for page_type in dict.fromkeys(page_types)
    ] + [
        f".production-page#page-{page}" for page in dict.fromkeys(page_ids)
    ]
    raw_full_width_sections = variant_cfg.get("full_width_sections", [])
    full_width_section_ids = [
        str(item.get("start_heading_id") or "").strip()
        for item in raw_full_width_sections
        if isinstance(item, dict) and str(item.get("start_heading_id") or "").strip()
    ] if isinstance(raw_full_width_sections, list) else []
    special_page_block_display = bool(expected_selectors) and all(
        selector in html_text for selector in expected_selectors
    ) and "display: block !important" in html_text and "column-span: all !important" in html_text
    cover_full_page_css = bool(
        re.search(
            r'body\.pdf-layout-page-flow-columns\s+\.production-page\.page-type-cover\s+figure[^{]*\{[^}]*column-span:\s*all\s*!important[^}]*width:\s*100%\s*!important',
            html_text,
            re.I | re.S,
        )
        and re.search(
            r'body\.pdf-layout-page-flow-columns\s+\.production-page\.page-type-cover\s+figure\s+img[^{]*\{[^}]*max-height:\s*252mm\s*!important',
            html_text,
            re.I | re.S,
        )
    )
    return {
        "display_contents_scoped": scoped_display_contents and not broad_display_contents,
        "unscoped_display_contents": broad_display_contents,
        "special_pages_block_display": special_page_block_display,
        "cover_full_page_art_css": cover_full_page_css,
        "full_width_sections_applied": all(
            f'data-full-width-section-start="{heading_id}"' in html_text
            for heading_id in full_width_section_ids
        ),
        "full_width_section_start_ids": full_width_section_ids,
        "full_width_tables_applied": all(
            f'data-pdf-full-width-table="{html_lib.escape(str(title), quote=True)}"' in html_text
            for title in variant_cfg.get("full_width_table_titles", [])
            if str(title).strip()
        ) if isinstance(variant_cfg.get("full_width_table_titles", []), list) else True,
    }


def apply_page_flow_full_width_sections(html_text: str, variant_cfg: dict[str, Any]) -> tuple[str, list[str]]:
    """Split configured heading-to-end sections into full-width PDF page flow."""
    raw_sections = variant_cfg.get("full_width_sections", [])
    if not isinstance(raw_sections, list):
        return html_text, []

    applied: list[str] = []
    for item in raw_sections:
        if not isinstance(item, dict):
            continue
        heading_id = str(item.get("start_heading_id") or "").strip()
        if not heading_id or heading_id in applied:
            continue
        heading_pattern = re.compile(
            rf'<h[1-6]\b[^>]*\bid="{re.escape(heading_id)}"[^>]*>',
            re.I,
        )
        heading_match = heading_pattern.search(html_text)
        if not heading_match:
            continue
        section_start = html_text.rfind("<section", 0, heading_match.start())
        if section_start < 0:
            continue
        page_open_end = html_text.find(">", section_start, heading_match.start())
        if page_open_end < 0:
            continue
        page_open_tag = html_text[section_start:page_open_end + 1]
        if "production-page" not in page_open_tag:
            continue

        # The start heading can share a source page with preceding body content.
        # Close that source wrapper and start an Appendix wrapper at the semantic boundary.
        title = str(item.get("title") or "").strip()
        title_html = (
            f'<h1 class="pdf-appendix-title">{html_lib.escape(title)}</h1>'
            if title else ""
        )
        appendix_open = (
            f'</section><section class="production-page page-type-appendix pdf-full-width-section" '
            f'data-full-width-section-start="{html_lib.escape(heading_id, quote=True)}">{title_html}'
        )
        html_text = html_text[:heading_match.start()] + appendix_open + html_text[heading_match.start():]
        applied.append(heading_id)
    return html_text, applied


def apply_page_flow_full_width_tables(html_text: str, variant_cfg: dict[str, Any]) -> tuple[str, list[str]]:
    """Mark configured large tables as full-width in the PDF-only variant HTML."""
    raw_titles = variant_cfg.get("full_width_table_titles", [])
    if not isinstance(raw_titles, list):
        return html_text, []
    titles = [str(title).strip() for title in raw_titles if str(title).strip()]
    applied: list[str] = []

    for title in titles:
        if title in applied:
            continue
        title_index = html_text.find(title)
        while title_index >= 0:
            paragraph_end = html_text.find("</p>", title_index)
            if paragraph_end < 0:
                break
            table_start = html_text.find('<div class="table-wrap', paragraph_end, paragraph_end + 1200)
            if table_start < 0:
                title_index = html_text.find(title, title_index + len(title))
                continue
            tag_end = html_text.find(">", table_start)
            if tag_end < 0:
                break
            tag = html_text[table_start:tag_end + 1]
            if "table-full-width" in tag:
                applied.append(title)
                break
            new_tag = tag.replace(
                'class="table-wrap',
                'class="table-wrap table-full-width',
                1,
            )
            if "data-pdf-full-width-table=" not in new_tag:
                new_tag = new_tag[:-1] + f' data-pdf-full-width-table="{html_lib.escape(title, quote=True)}">'
            html_text = html_text[:table_start] + new_tag + html_text[tag_end + 1:]
            applied.append(title)
            break
    return html_text, applied


def production_pdf_variant_html(html_path: Path, temp_dir: Path, variant: str, variant_cfg: dict[str, Any]) -> tuple[Path, dict[str, Any]]:
    html_text = html_path.read_text(encoding="utf-8")
    print_columns = max(1, min(2, int(variant_cfg.get("print_columns", 1))))
    normal_single_column_flow = (
        print_columns == 1
        and bool(variant_cfg.get("avoid_single_column_fragmentation_context", False))
    )
    print_column_count = "auto" if normal_single_column_flow else str(print_columns)
    column_gap = "8mm" if print_columns > 1 else "0"
    layout_mode = str(variant_cfg.get("layout_mode") or variant_cfg.get("column_scope") or "")
    page_flow = print_columns > 1 and layout_mode == "page_flow_columns"
    body_classes = f"print-columns-{print_columns}"
    if normal_single_column_flow:
        body_classes += " normal-single-column-flow"
    if page_flow:
        body_classes += " pdf-layout-page-flow-columns"
    html_text = re.sub(
        r'<body\b([^>]*)class="[^"]*"',
        rf'<body\1class="{body_classes}"',
        html_text,
        count=1,
        flags=re.I,
    )
    if 'class="print-columns-' not in html_text:
        html_text = re.sub(r"<body\b", f'<body class="{body_classes}"', html_text, count=1, flags=re.I)
    base_href = html_lib.escape(html_path.parent.resolve().as_uri().rstrip("/") + "/")
    base_tag = f'\n<base href="{base_href}">\n'
    page_flow_css = ""
    if page_flow:
        html_text, applied_full_width_sections = apply_page_flow_full_width_sections(html_text, variant_cfg)
        html_text, applied_full_width_tables = apply_page_flow_full_width_tables(html_text, variant_cfg)
        raw_exempt_types = variant_cfg.get("page_flow_exempt_page_types", ["cover"])
        exempt_page_types = [
            str(value).strip().replace("_", "-")
            for value in raw_exempt_types
            if str(value).strip()
        ] if isinstance(raw_exempt_types, list) else ["cover"]
        raw_exempt_pages = variant_cfg.get("page_flow_exempt_pages", [])
        exempt_pages = [
            str(value).strip().zfill(3)
            for value in raw_exempt_pages
            if str(value).strip().isdigit()
        ] if isinstance(raw_exempt_pages, list) else []
        exempt_selectors = [
            f"body.pdf-layout-page-flow-columns .production-page.page-type-{page_type}"
            for page_type in dict.fromkeys(exempt_page_types)
        ] + [
            f"body.pdf-layout-page-flow-columns .production-page#page-{page}"
            for page in dict.fromkeys(exempt_pages)
        ]
        exempt_selector_css = ",\n  ".join(exempt_selectors) or "body.pdf-layout-page-flow-columns .production-page.page-type-cover"
        art_column_policy = variant_cfg.get("art_column_policy") or {}
        default_art_columnned = art_column_policy.get("default_columnned") is not False
        not_columnned_roles = {str(role) for role in art_column_policy.get("not_columnned_roles", [])}

        def add_default_art_columnned(match: re.Match[str]) -> str:
            tag = match.group(0)
            if re.search(r"\bdata-columnned=", tag, re.I):
                return tag
            role_match = re.search(r'\bdata-role="([^"]+)"', tag, re.I)
            role = role_match.group(1) if role_match else ""
            columnned = default_art_columnned and role not in not_columnned_roles
            return tag[:-1] + f' data-columnned="{str(columnned).lower()}">'

        html_text = re.sub(
            r'<figure\b(?=[^>]*\bclass="[^"]*\bpreserved-page-art\b[^"]*")[^>]*>',
            add_default_art_columnned,
            html_text,
            flags=re.I,
        )
        statblock_policy = variant_cfg.get("statblock_section_policy") or {}
        statblock_heading_ids = [str(value).strip() for value in statblock_policy.get("heading_ids", []) if str(value).strip()]
        statblock_break_css = ""
        if statblock_heading_ids:
            statblock_selectors = ",\n  ".join(
                f"body.pdf-layout-page-flow-columns #{heading_id}" for heading_id in statblock_heading_ids
            )
            statblock_break_css = f"""
  {statblock_selectors} {{
    break-before: page !important;
    page-break-before: always !important;
    column-span: all !important;
    break-after: avoid;
    page-break-after: avoid;
  }}
"""
        heading_page_break_ids = [
            str(value).strip()
            for value in variant_cfg.get("heading_page_break_before_ids", [])
            if str(value).strip()
        ]
        heading_page_break_css = ""
        if heading_page_break_ids:
            heading_selectors = ",\n  ".join(
                f"body.pdf-layout-page-flow-columns #{heading_id}"
                for heading_id in heading_page_break_ids
            )
            heading_page_break_css = f"""
  {heading_selectors} {{
    break-before: page !important;
    page-break-before: always !important;
    break-after: avoid !important;
    page-break-after: avoid !important;
  }}
"""
        page_flow_css = """
  body.pdf-layout-page-flow-columns main {
    column-count: 2 !important;
    column-gap: __COLUMN_GAP__ !important;
    column-fill: auto;
  }
  body.pdf-layout-page-flow-columns .production-page:not(.page-type-cover):not(.page-type-credits):not(.page-type-source-toc):not(.page-type-quote-art) {
    display: contents !important;
    break-inside: auto !important;
    page-break-inside: auto !important;
  }
  __PAGE_FLOW_EXEMPT_SELECTORS__ {
    display: block !important;
    column-span: all !important;
    break-after: page;
    page-break-after: always;
  }
  body.pdf-layout-page-flow-columns .production-page.page-type-cover figure,
  body.pdf-layout-page-flow-columns .production-page.page-type-cover figure.keeper-art-block,
  body.pdf-layout-page-flow-columns .production-page.page-type-cover figure.art-cover,
  body.pdf-layout-page-flow-columns .production-page.page-type-cover figure.art-full-page {
    column-span: all !important;
    float: none !important;
    clear: both !important;
    display: block !important;
    width: 100% !important;
    max-width: 100% !important;
    margin: 0 auto !important;
    break-before: auto !important;
    page-break-before: auto !important;
    break-after: auto !important;
    page-break-after: auto !important;
  }
  body.pdf-layout-page-flow-columns .production-page.page-type-cover figure img,
  body.pdf-layout-page-flow-columns .production-page.page-type-cover figure.keeper-art-block img,
  body.pdf-layout-page-flow-columns .production-page.page-type-cover figure.art-cover img,
  body.pdf-layout-page-flow-columns .production-page.page-type-cover figure.art-full-page img {
    width: 100% !important;
    max-width: 100% !important;
    max-height: 252mm !important;
    object-fit: contain !important;
  }
  body.pdf-layout-page-flow-columns .pdf-full-width-section,
  body.pdf-layout-page-flow-columns .pdf-full-width-section ~ .production-page {
    display: block !important;
    column-span: all !important;
    column-count: 1 !important;
    break-after: page !important;
    page-break-after: always !important;
  }
  body.pdf-layout-page-flow-columns .pdf-full-width-section {
    break-before: page !important;
    page-break-before: always !important;
  }
  body.pdf-layout-page-flow-columns .pdf-full-width-section .pdf-appendix-title {
    column-span: all !important;
    margin: 0 0 6mm !important;
    text-align: center;
    letter-spacing: .08em;
  }
  body.pdf-layout-page-flow-columns .pdf-full-width-section figure:not(.art-float-right):not(.art-scenario-right),
  body.pdf-layout-page-flow-columns .pdf-full-width-section ~ .production-page figure:not(.art-float-right):not(.art-scenario-right) {
    column-span: all !important;
    float: none !important;
    width: 100% !important;
    max-width: 100% !important;
    margin-left: 0 !important;
    margin-right: 0 !important;
  }
  body.pdf-layout-page-flow-columns .pdf-full-width-section figure:not(.art-float-right):not(.art-scenario-right):not(.art-scale-50) img,
  body.pdf-layout-page-flow-columns .pdf-full-width-section ~ .production-page figure:not(.art-float-right):not(.art-scenario-right):not(.art-scale-50) img {
    width: 100% !important;
    max-width: 100% !important;
    max-height: 252mm !important;
    object-fit: contain;
  }
  body.pdf-layout-page-flow-columns .pdf-full-width-section figure.art-float-right,
  body.pdf-layout-page-flow-columns .pdf-full-width-section ~ .production-page figure.art-float-right {
    column-span: none !important;
    float: right !important;
    clear: none !important;
    width: min(30%, 54mm) !important;
    max-width: 30% !important;
    margin: .1em 0 .45em .75em !important;
  }
  body.pdf-layout-page-flow-columns .pdf-full-width-section figure.art-float-right img,
  body.pdf-layout-page-flow-columns .pdf-full-width-section ~ .production-page figure.art-float-right img {
    width: 100% !important;
    max-width: 100% !important;
    max-height: 105mm !important;
  }
  body.pdf-layout-page-flow-columns .pdf-full-width-section figure.art-scale-50 img,
  body.pdf-layout-page-flow-columns .pdf-full-width-section ~ .production-page figure.art-scale-50 img {
    width: 50% !important;
    max-width: 50% !important;
  }
  body.pdf-layout-page-flow-columns h1 {
    column-span: all;
    break-after: avoid;
    page-break-after: avoid;
  }
  body.pdf-layout-page-flow-columns h2,
  body.pdf-layout-page-flow-columns h3,
  body.pdf-layout-page-flow-columns h4,
  body.pdf-layout-page-flow-columns h5,
  body.pdf-layout-page-flow-columns h6 {
    column-span: none !important;
    break-after: avoid;
    page-break-after: avoid;
  }
  body.pdf-layout-page-flow-columns blockquote.review-callout {
    column-span: none !important;
    columns: auto !important;
    column-count: auto !important;
    break-inside: auto !important;
    page-break-inside: auto !important;
    box-decoration-break: clone;
    -webkit-box-decoration-break: clone;
  }
  body.pdf-layout-page-flow-columns blockquote.review-callout.callout-keep-together,
  body.pdf-layout-page-flow-columns blockquote.review-callout[data-break-policy="keep_together"] {
    break-inside: avoid !important;
    page-break-inside: avoid !important;
  }
  body.pdf-layout-page-flow-columns .statblock-card {
    break-inside: avoid !important;
    page-break-inside: avoid !important;
  }
  body.pdf-layout-page-flow-columns .table-wrap,
  body.pdf-layout-page-flow-columns table {
    break-inside: avoid;
    page-break-inside: avoid;
  }
  body.pdf-layout-page-flow-columns .table-wrap {
    overflow: visible !important;
    max-width: 100%;
  }
  body.pdf-layout-page-flow-columns .table-wrap.table-full-width {
    column-span: all !important;
    width: 100% !important;
    max-width: 100% !important;
    break-inside: avoid !important;
    page-break-inside: avoid !important;
  }
  body.pdf-layout-page-flow-columns .statblock-card table {
    table-layout: auto;
    width: 100%;
    max-width: 100%;
    font-size: .6em;
  }
  body.pdf-layout-page-flow-columns .statblock-card table.statblock-attributes-table {
    font-size: .56em;
  }
  body.pdf-layout-page-flow-columns .statblock-card table.statblock-derived-table {
    font-size: .58em;
  }
  body.pdf-layout-page-flow-columns .statblock-card table.statblock-actions-table {
    font-size: .6em;
  }
  body.pdf-layout-page-flow-columns .statblock-card table.has-index-column th:first-child,
  body.pdf-layout-page-flow-columns .statblock-card table.has-index-column td:first-child {
    width: 1.8em;
    min-width: 1.8em;
    max-width: 1.8em;
    padding-left: 1px;
    padding-right: 1px;
    text-align: center;
    white-space: nowrap;
  }
  body.pdf-layout-page-flow-columns .statblock-card th,
  body.pdf-layout-page-flow-columns .statblock-card td {
    padding: 1px 2px;
    overflow-wrap: normal;
    word-break: normal;
    white-space: normal;
  }
  body.pdf-layout-page-flow-columns figure {
    break-inside: avoid;
    page-break-inside: avoid;
  }
  body.pdf-layout-page-flow-columns figure.preserved-page-art {
    column-span: none !important;
    display: block;
    width: 100%;
    max-width: 100%;
    margin-left: 0;
    margin-right: 0;
    break-inside: avoid;
    page-break-inside: avoid;
  }
  body.pdf-layout-page-flow-columns figure.preserved-page-art img {
    max-width: 100%;
    max-height: 118mm;
    object-fit: contain;
  }
  body.pdf-layout-page-flow-columns figure.art-full-width,
  body.pdf-layout-page-flow-columns figure.art-full-page,
  body.pdf-layout-page-flow-columns figure.art-pregen-fullpage {
    column-span: none !important;
    float: none !important;
    clear: none !important;
    width: 100% !important;
    max-width: 100% !important;
    margin-left: 0 !important;
    margin-right: 0 !important;
    break-before: auto !important;
    page-break-before: auto !important;
    break-after: auto !important;
    page-break-after: auto !important;
  }
  body.pdf-layout-page-flow-columns figure.art-full-width img,
  body.pdf-layout-page-flow-columns figure.art-full-page img,
  body.pdf-layout-page-flow-columns figure.art-pregen-fullpage img {
    width: 100% !important;
    max-width: 100% !important;
    max-height: 118mm !important;
    object-fit: contain;
  }
  body.pdf-layout-page-flow-columns .production-landing,
  body.pdf-layout-page-flow-columns .production-toc,
  body.pdf-layout-page-flow-columns .toc,
  body.pdf-layout-page-flow-columns figure.preserved-page-art[data-columnned="false"],
  body.pdf-layout-page-flow-columns .art-cover {
    column-span: all !important;
    break-inside: avoid;
    page-break-inside: avoid;
  }
__STATBLOCK_BREAK_CSS__
__HEADING_PAGE_BREAK_CSS__
""".replace("__COLUMN_GAP__", column_gap).replace("__STATBLOCK_BREAK_CSS__", statblock_break_css).replace("__HEADING_PAGE_BREAK_CSS__", heading_page_break_css).replace("__PAGE_FLOW_EXEMPT_SELECTORS__", exempt_selector_css)
    variant_typography_css = ""
    print_body_font_size = str(variant_cfg.get("print_body_font_size") or "").strip()
    print_body_line_height = str(variant_cfg.get("print_body_line_height") or "").strip()
    statblock_card_font_size = str(variant_cfg.get("statblock_card_font_size") or "").strip()
    if print_body_font_size:
        variant_typography_css += f"  body {{ font-size: {print_body_font_size} !important; }}\n"
    if print_body_line_height:
        variant_typography_css += f"  body {{ line-height: {print_body_line_height} !important; }}\n"
    if statblock_card_font_size:
        variant_typography_css += f"  .statblock-card {{ font-size: {statblock_card_font_size} !important; }}\n"
        variant_typography_css += f"  .statblock-card h2, .statblock-card h3 {{ font-size: {statblock_card_font_size} !important; }}\n"
    override = (
        "\n<style id=\"translator-pdf-variant-css\">\n"
        "@media print {\n"
        f"{variant_typography_css}"
        f"  main {{ column-count: {print_column_count} !important; column-gap: {column_gap} !important; }}\n"
        f"{page_flow_css}"
        "}\n"
        "</style>\n"
    )
    if "</head>" in html_text:
        html_text = html_text.replace("</head>", base_tag + override + "</head>", 1)
    else:
        html_text = base_tag + override + html_text
    target = temp_dir / f"{html_path.stem}_{safe_filename(variant)}.html"
    target.write_text(html_text, encoding="utf-8", newline="\n")
    checks = page_flow_variant_html_policy_checks(html_text, variant_cfg) if page_flow else {}
    return target, checks


def production_pdf_render_command(
    engine_command: str | list[Any],
    *,
    source_html: Path,
    output_pdf: Path,
    temp_dir: Path,
    browser_executable: str | None = None,
) -> list[str]:
    placeholders = {
        "source_html": str(source_html),
        "source_html_uri": source_html.resolve().as_uri(),
        "output_pdf": str(output_pdf),
        "temp_dir": str(temp_dir),
        "browser_executable": browser_executable or "",
    }
    if isinstance(engine_command, list):
        return [str(part).format(**placeholders) for part in engine_command]
    if isinstance(engine_command, str):
        rendered = engine_command.format(**placeholders)
        return shlex.split(rendered, posix=os.name != "nt")
    raise TypeError("production_pdf.engine_command must be a string or list of strings")


def portable_process_output_lines(value: str, *, limit: int = 20) -> list[str]:
    """Keep captured tool diagnostics useful without leaking device-local repo paths."""
    repo_root = str(REPO_ROOT)
    return [
        re.sub(re.escape(repo_root), "<repo>", line, flags=re.I)
        for line in value.strip().splitlines()[:limit]
    ]


def production_pdf_command_result(
    config: dict[str, Any],
    config_path: Path,
    report: Path,
    html_path: Path,
    pdf_path: Path,
    command: list[str] | None,
    *,
    status: str,
    action: str,
    findings: list[dict[str, Any]],
    variant: str | None = None,
    completed: subprocess.CompletedProcess[str] | None = None,
    temp_dir: Path | None = None,
    temp_pdf_path: Path | None = None,
    render_html_path: Path | None = None,
    render_html_sha256: str | None = None,
    rendered_temp_pdf_bytes: int | None = None,
    temp_pdf_sha256: str | None = None,
    canonical_replaced: bool = False,
    previous_pdf_preserved: bool = False,
    variant_html_policy_checks: dict[str, Any] | None = None,
    temp_cleanup: dict[str, Any] | None = None,
) -> dict[str, Any]:
    counts: dict[str, Any] = {"findings": len(findings)}
    if pdf_path.exists():
        counts["pdf_bytes"] = pdf_path.stat().st_size
    html_sha256 = sha256_file(html_path) if html_path.exists() else None
    render_html_path = render_html_path or html_path
    if render_html_sha256 is None and render_html_path.exists():
        render_html_sha256 = sha256_file(render_html_path)
    canonical_pdf_sha256 = sha256_file(pdf_path) if pdf_path.exists() and pdf_path.stat().st_size > 0 else None
    if action == "check_only":
        mode = "check_only"
    elif action == "not_built":
        mode = "not_built"
    else:
        mode = "build"
    result: dict[str, Any] = {
        "schema": "translator_production_pdf.v1",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "config": rel(config_path),
        "source_html": rel(html_path),
        "source_html_sha256": html_sha256,
        "render_html": rel(render_html_path),
        "render_html_sha256": render_html_sha256,
        "production_pdf": rel(pdf_path),
        "variant": variant,
        "variant_config": production_pdf_variant_config(config, variant) if variant else {},
        "status": status,
        "action": action,
        "mode": mode,
        "artifact_writes": {"qa_report": True, "production_pdf": canonical_replaced},
        "canonical_replaced": canonical_replaced,
        "previous_pdf_preserved": previous_pdf_preserved,
        "required_gates": production_pdf_required_gates(config),
        "engine_command": production_pdf_config(config).get("engine_command"),
        "print_policy": {
            "route": "browser_edge_or_chromium_headless_print",
            "background_graphics": True,
            "header_footer": "disabled" if command and "--no-pdf-header-footer" in " ".join(command) else "unknown_or_enabled",
        },
        "variant_html_policy_checks": variant_html_policy_checks or {},
        "temp_dir": rel(temp_dir) if temp_dir else None,
        "temp_pdf": rel(temp_pdf_path) if temp_pdf_path else None,
        "temp_pdf_sha256": temp_pdf_sha256,
        "canonical_pdf_sha256": canonical_pdf_sha256,
        "temp_cleanup": temp_cleanup or {},
        "counts": counts,
        "findings": findings,
    }
    if completed is not None:
        result["engine_result"] = {
            "returncode": completed.returncode,
            "stdout": portable_process_output_lines(completed.stdout),
            "stderr": portable_process_output_lines(completed.stderr),
        }
    if canonical_pdf_sha256:
        result["sha256"] = canonical_pdf_sha256
    if rendered_temp_pdf_bytes is not None:
        result["rendered_temp_pdf_bytes"] = rendered_temp_pdf_bytes
    write_json(report, result)
    return result


def wait_for_stable_file(path: Path, *, timeout_seconds: float = 10.0, stable_seconds: float = 0.75) -> bool:
    deadline = time.monotonic() + timeout_seconds
    last_size: int | None = None
    stable_since: float | None = None
    while time.monotonic() < deadline:
        if not path.exists():
            last_size = None
            stable_since = None
            time.sleep(0.1)
            continue
        size = path.stat().st_size
        now = time.monotonic()
        if size > 0 and size == last_size:
            if stable_since is None:
                stable_since = now
            if now - stable_since >= stable_seconds:
                return True
        else:
            last_size = size
            stable_since = now if size > 0 else None
        time.sleep(0.1)
    return False


def build_production_pdf(config_path: Path, *, check_only: bool = False, variant: str | None = None) -> dict[str, Any]:
    config = read_json(config_path)
    html_path = production_pdf_html_path(config)
    variant_cfg = production_pdf_variant_config(config, variant)
    pdf_path = production_pdf_target_path(config, variant)
    report = production_pdf_report_path(config, variant)
    findings = production_pdf_entry_findings(config, html_path, variant=variant)
    engine = production_pdf_config(config).get("engine_command")
    browser_executable: str | None = None
    if "{browser_executable}" in json.dumps(engine, ensure_ascii=False):
        edge_path, _ = resolve_edge_path(config)
        if edge_path is None:
            findings.append({"code": "missing_pdf_browser", "message": "Edge/Chromium executable could not be resolved."})
        else:
            browser_executable = str(edge_path)
    command: list[str] | None = None
    if engine:
        try:
            command = production_pdf_render_command(
                engine,
                source_html=html_path,
                output_pdf=pdf_path,
                temp_dir=report.parent / "_production_pdf_temp",
                browser_executable=browser_executable,
            )
        except Exception as exc:
            findings.append({"code": "invalid_pdf_engine_command", "message": str(exc)})
    if findings or check_only:
        status = "blocked" if findings else "pass"
        return production_pdf_command_result(
            config,
            config_path,
            report,
            html_path,
            pdf_path,
            command,
            status=status,
            action="check_only" if check_only else "not_built",
            findings=findings,
            variant=variant,
        )

    if command is None:
        findings.append({"code": "missing_pdf_engine", "message": "production_pdf.engine_command is not configured."})
        return production_pdf_command_result(
            config,
            config_path,
            report,
            html_path,
            pdf_path,
            command,
            status="blocked",
            action="not_built",
            findings=findings,
            variant=variant,
        )

    timeout_seconds = int(production_pdf_config(config).get("engine_timeout_seconds", 120))
    pdf_path.parent.mkdir(parents=True, exist_ok=True)
    report.parent.mkdir(parents=True, exist_ok=True)
    previous_pdf_existed = pdf_path.exists()
    temp_root = production_pdf_temp_root(config)
    temp_root.mkdir(parents=True, exist_ok=True)
    temp_dir = make_production_pdf_temp_dir(temp_root)
    temp_pdf_path = pdf_path.parent / (
        f".{safe_filename(pdf_path.stem)}.tmp-{os.getpid()}-{int(time.time() * 1_000_000)}{pdf_path.suffix or '.pdf'}"
    )
    render_html_path = html_path
    render_html_sha256: str | None = None
    variant_html_policy_checks: dict[str, Any] = {}
    rendered_temp_pdf_bytes: int | None = None
    temp_pdf_sha256: str | None = None
    completed: subprocess.CompletedProcess[str] | None = None
    canonical_replaced = False
    failure_status = "fail"
    temp_cleanup: dict[str, Any] = {
        "render_temp_dir": {"path": rel(temp_dir), "removed": False},
        "staged_pdf": {"path": rel(temp_pdf_path), "removed": False},
    }
    try:
        if variant:
            render_html_path, variant_html_policy_checks = production_pdf_variant_html(html_path, temp_dir, variant, variant_cfg)
        render_html_sha256 = sha256_file(render_html_path)
        command = production_pdf_render_command(
            engine, source_html=render_html_path, output_pdf=temp_pdf_path, temp_dir=temp_dir,
            browser_executable=browser_executable,
        )
        completed = subprocess.run(
            command,
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            timeout=timeout_seconds,
            check=False,
        )
        output_timeout_seconds = float(production_pdf_config(config).get("temp_output_timeout_seconds", 60.0))
        output_stable_seconds = float(production_pdf_config(config).get("temp_output_stable_seconds", 0.75))
        stable = wait_for_stable_file(
            temp_pdf_path,
            timeout_seconds=output_timeout_seconds,
            stable_seconds=output_stable_seconds,
        )
        if completed.returncode != 0:
            findings.append({"code": "pdf_engine_failed", "returncode": completed.returncode})
        if not temp_pdf_path.exists():
            findings.append({"code": "missing_temp_output_pdf", "path": rel(temp_pdf_path), "message": "PDF engine completed but its temporary output was not created."})
        elif temp_pdf_path.stat().st_size == 0:
            findings.append({"code": "empty_temp_output_pdf", "path": rel(temp_pdf_path), "message": "PDF engine created an empty temporary output."})
        elif not stable:
            findings.append({"code": "unstable_temp_output_pdf", "path": rel(temp_pdf_path), "message": "PDF engine output did not become stable before replacement."})
        else:
            rendered_temp_pdf_bytes = temp_pdf_path.stat().st_size
            temp_pdf_sha256 = sha256_file(temp_pdf_path)

        if not findings:
            try:
                # Staging beside the canonical target keeps os.replace atomic on Windows.
                os.replace(temp_pdf_path, pdf_path)
                canonical_replaced = True
            except PermissionError as exc:
                failure_status = "blocked"
                findings.append({"code": "output_pdf_locked", "path": rel(pdf_path), "message": str(exc)})
            except OSError as exc:
                findings.append({"code": "output_pdf_replace_failed", "path": rel(pdf_path), "message": str(exc)})
    except FileNotFoundError as exc:
        failure_status = "blocked"
        findings.append({"code": "pdf_engine_not_found", "message": str(exc), "command": command})
    except subprocess.TimeoutExpired as exc:
        findings.append({"code": "pdf_engine_timeout", "timeout_seconds": timeout_seconds, "message": str(exc)})
    except Exception as exc:
        findings.append({"code": "pdf_engine_exception", "message": str(exc)})
    finally:
        if temp_pdf_path.exists():
            try:
                temp_pdf_path.unlink()
                temp_cleanup["staged_pdf"]["removed"] = True
            except OSError as exc:
                findings.append({"code": "temp_pdf_cleanup_failed", "path": rel(temp_pdf_path), "message": str(exc)})
                temp_cleanup["staged_pdf"]["error"] = str(exc)
        else:
            temp_cleanup["staged_pdf"]["removed"] = True
        try:
            cleanup_attempts = remove_production_pdf_temp_dir(temp_dir)
            temp_cleanup["render_temp_dir"]["removed"] = True
            temp_cleanup["render_temp_dir"]["attempts"] = cleanup_attempts
        except OSError as exc:
            findings.append({"code": "temp_render_dir_cleanup_failed", "path": rel(temp_dir), "message": str(exc)})
            temp_cleanup["render_temp_dir"]["error"] = str(exc)

    cleanup_failed = any(not item.get("removed") for item in temp_cleanup.values())
    status = "pass" if canonical_replaced and not cleanup_failed else failure_status
    action = "built" if canonical_replaced else "not_replaced"
    if canonical_replaced and cleanup_failed:
        action = "built_with_cleanup_failure"
    return production_pdf_command_result(
        config,
        config_path,
        report,
        html_path,
        pdf_path,
        command,
        status=status,
        action=action,
        findings=findings,
        variant=variant,
        completed=completed,
        temp_dir=temp_dir,
        temp_pdf_path=temp_pdf_path,
        render_html_path=render_html_path,
        render_html_sha256=render_html_sha256,
        rendered_temp_pdf_bytes=rendered_temp_pdf_bytes,
        temp_pdf_sha256=temp_pdf_sha256,
        canonical_replaced=canonical_replaced,
        previous_pdf_preserved=previous_pdf_existed and not canonical_replaced,
        variant_html_policy_checks=variant_html_policy_checks,
        temp_cleanup=temp_cleanup,
    )


def translation_config(config: dict[str, Any]) -> dict[str, Any]:
    return config.get("translation", {})


def translation_report_path(config: dict[str, Any]) -> Path:
    value = translation_config(config).get("report", "translation_preparation_report.json")
    path = Path(str(value).replace("/", "\\"))
    return path.resolve() if path.is_absolute() else qa_root(config) / path


def translation_payload_report_path(config: dict[str, Any]) -> Path:
    value = translation_config(config).get("payload_qa_report", "translation_payload_qa_report.json")
    path = Path(str(value).replace("/", "\\"))
    return path.resolve() if path.is_absolute() else qa_root(config) / path


def translation_output_path(config: dict[str, Any], key: str, default_name: str) -> Path:
    value = translation_config(config).get(key, default_name)
    path = Path(str(value).replace("/", "\\"))
    return path.resolve() if path.is_absolute() else qa_root(config) / path


def localization_prompt_pack_dir(config: dict[str, Any]) -> Path:
    value = translation_config(config).get("prompt_pack_dir", "Localization_Prompts")
    path = Path(str(value).replace("/", "\\"))
    return path.resolve() if path.is_absolute() else qa_root(config) / path


def prompt_pack_report_path(config: dict[str, Any]) -> Path:
    value = translation_config(config).get("prompt_pack_report", "localization_prompt_pack_report.json")
    path = Path(str(value).replace("/", "\\"))
    return path.resolve() if path.is_absolute() else qa_root(config) / path


def translation_source_path(config: dict[str, Any]) -> Path:
    tr = translation_config(config)
    if tr.get("source_markdown"):
        return root_path(str(tr["source_markdown"]))
    outputs = config.get("production_outputs", {})
    if outputs.get("source_full_ru"):
        return root_path(str(outputs["source_full_ru"]))
    raise KeyError("translation.source_markdown")


def localization_output_path(config: dict[str, Any]) -> Path:
    tr = translation_config(config)
    if tr.get("output_markdown"):
        return root_path(str(tr["output_markdown"]))
    term = config.get("term_gate", {})
    if term.get("output_markdown"):
        return root_path(str(term["output_markdown"]))
    outputs = config.get("production_outputs", {})
    if outputs.get("keeper_markdown"):
        return root_path(str(outputs["keeper_markdown"]))
    raise KeyError("translation.output_markdown")


def translation_required_gates(config: dict[str, Any]) -> list[str]:
    return list(translation_config(config).get("required_gates", ["source_full_ru_accepted"]))


def source_block_coverage_report_findings(config: dict[str, Any]) -> list[dict[str, Any]]:
    if not strict_reading_order_required(config):
        return []
    findings: list[dict[str, Any]] = []
    report = contract_v2_report_path(config)
    if not report.exists():
        return [
            {
                "code": "missing_source_block_coverage_report",
                "path": rel(report),
                "message": "Strict reading-order gate requires a passing source-block coverage report.",
            }
        ]
    data = read_json(report)
    if data.get("schema") != "translator_source_block_coverage_gate.v2":
        findings.append(
            {
                "code": "source_block_coverage_report_schema_not_v2",
                "path": rel(report),
                "message": "Strict reading-order gate requires v2 report schema.",
            }
        )
    if data.get("status") != "pass":
        findings.append(
            {
                "code": "source_block_coverage_gate_not_passed",
                "path": rel(report),
                "message": "Source-block coverage gate has not passed.",
            }
        )
    if data.get("strict_reading_order") is not True:
        findings.append(
            {
                "code": "source_block_coverage_not_strict",
                "path": rel(report),
                "message": "Report did not run in strict reading-order mode.",
            }
        )
    input_hashes = data.get("input_hashes") if isinstance(data.get("input_hashes"), dict) else {}
    source_manifest = contract_v2_manifest_path(config, "source_block_manifest")
    candidate_manifest = contract_v2_manifest_path(config, "candidate_block_manifest")
    for key, path in {
        "source_block_manifest": source_manifest,
        "candidate_block_manifest": candidate_manifest,
    }.items():
        if path and path.exists():
            expected = sha256_file(path)
            if input_hashes.get(key) != expected:
                findings.append(
                    {
                        "code": "source_block_coverage_report_stale",
                        "path": rel(report),
                        "message": f"{key} hash no longer matches the report.",
                    }
                )
        else:
            findings.append(
                {
                    "code": f"missing_{key}",
                    "path": rel(path) if path else None,
                    "message": f"{key} is required for strict reading-order gate.",
                }
            )
    return findings


def localization_prompt_pack(config_path: Path, *, force: bool = False) -> dict[str, Any]:
    config = read_json(config_path)
    out_dir = localization_prompt_pack_dir(config)
    report = prompt_pack_report_path(config)
    profile = statblock_profile(config)
    source = statblock_source_path(config)
    package_title = str(config.get("title_en") or config.get("project_key") or "Package")
    source_lang = str(translation_config(config).get("source_lang", "en"))
    target_lang = str(translation_config(config).get("target_lang", "ru"))
    files = {
        "00_contract": out_dir / "00_documentary_localization_contract.md",
        "01_ocr_cleanup": out_dir / "01_ocr_cleanup_prompt.md",
        "02_source_restoration": out_dir / "02_source_restoration_prompt.md",
        "03_localization": out_dir / "03_localization_prompt.md",
        "04_qa": out_dir / "04_localization_qa_checklist.md",
    }
    existing = [path for path in files.values() if path.exists()]
    if existing and not force:
        result = {
            "schema": "translator_localization_prompt_pack.v1",
            "generated_at_utc": datetime.now(timezone.utc).isoformat(),
            "config": rel(config_path),
            "status": "pass",
            "action": "kept_existing",
            "profile": profile,
            "prompt_pack_dir": rel(out_dir),
            "files": {key: rel(path) for key, path in files.items()},
        }
        write_json(report, result)
        return result

    out_dir.mkdir(parents=True, exist_ok=True)
    profile_rules = STATBLOCK_PROFILE_RULES.get(profile, STATBLOCK_PROFILE_RULES["generic"])
    common_header = (
        f"# {package_title}\n\n"
        f"- Config: `{rel(config_path)}`\n"
        f"- Profile: `{profile}` ({profile_rules['label']})\n"
        f"- Source language: `{source_lang}`\n"
        f"- Target language: `{target_lang}`\n"
        f"- Working source: `{rel(source)}`\n\n"
    )
    files["00_contract"].write_text(
        common_header
        + "## Documentary Localization Contract\n\n"
        + "- Preserve all numbers, ratings, dice notation, percentages, dates, page markers, table cells, statblocks, card fields, and rules references.\n"
        + "- Preserve source structure before style polish: headings, lists, tables, callouts, boxed text, cards/statblocks, captions, and image anchors.\n"
        + "- Do not summarize, adapt, omit, combine, or reorder source material unless a QA decision explicitly says so.\n"
        + "- If OCR evidence is ambiguous, mark the value as `?` or `<!-- REVIEW: ... -->`; do not invent missing mechanics.\n"
        + "- Service/OCR artifacts must be removed from reader text but kept in QA reports when they explain a decision.\n"
        + "- Translation starts only from accepted source reconstruction, not from raw OCR or a mixed review draft.\n",
        encoding="utf-8",
        newline="\n",
    )
    files["01_ocr_cleanup"].write_text(
        common_header
        + "## OCR Cleanup Prompt\n\n"
        + "Task: clean OCR noise while preserving source evidence.\n\n"
        + "Rules:\n"
        + "- Remove repeated running headers, page-number-only lines, OCR service captions, and obvious scanner artifacts.\n"
        + "- Preserve page markers and do not merge pages.\n"
        + "- Do not join hyphenated lines automatically on two-column pages unless the page render proves the word continues.\n"
        + "- Preserve numerals, dice expressions, percentages, ranges, stat abbreviations, and named mechanics exactly.\n"
        + "- Do not turn prose into tables; only restore a table when the source page shows structured/tabular data.\n"
        + "- Mark unresolved OCR fragments with `<!-- REVIEW: ... -->` instead of silently deleting them.\n",
        encoding="utf-8",
        newline="\n",
    )
    files["02_source_restoration"].write_text(
        common_header
        + "## Source Restoration Prompt\n\n"
        + "Task: rebuild source-faithful Markdown from OCR plus page render/PDF evidence.\n\n"
        + "Rules:\n"
        + "- Work page by page: compare OCR text to the page render before approving order or structure.\n"
        + "- Restore headings, lists, quotes, emphasis, tables, callouts, captions, and image anchors when visible.\n"
        + "- Keep cards/statblocks structurally separate from prose.\n"
        + "- For profile-specific statblocks/cards, use this target shape:\n"
        + "\n".join(f"  - {item}" for item in profile_rules["target_shape"])
        + "\n"
        + "- Preserve field labels/values relevant to the profile: "
        + ", ".join(f"`{field}`" for field in profile_rules["fields"])
        + ".\n"
        + "- Keep uncertain values as `?` until visually resolved; source reconstruction is not accepted while `?` remains in mechanics.\n",
        encoding="utf-8",
        newline="\n",
    )
    files["03_localization"].write_text(
        common_header
        + "## Localization Prompt\n\n"
        + "Task: translate accepted source Markdown into Russian documentary-quality text.\n\n"
        + "Rules:\n"
        + "- Translate meaning faithfully; do not abridge, retell, modernize, or add new lore.\n"
        + "- Preserve Markdown structure, page markers, table shape, image links, anchors, callouts, and statblock/card boundaries.\n"
        + "- Preserve all numbers, formulas, dice notation, percentages, damage, armor, HP, ratings, skills, assets, traits, and special rules.\n"
        + "- Apply the package glossary/terminology registry when present; otherwise leave uncertain terms marked for terminology QA.\n"
        + "- Keep original proper names when the project has no accepted RU form.\n"
        + "- Never translate from raw OCR when source reconstruction gates are false.\n",
        encoding="utf-8",
        newline="\n",
    )
    files["04_qa"].write_text(
        common_header
        + "## Localization QA Checklist\n\n"
        + "| Check | Requirement |\n"
        + "|---|---|\n"
        + "| Completeness | No source paragraph, table, statblock, card, caption, handout text, or appendix is omitted. |\n"
        + "| Numbers | All numbers, dates, dice, percentages, HP, armor, ratings, and damage values match source. |\n"
        + "| Structure | Headings, page markers, tables, lists, callouts, image anchors, and statblock/card boundaries are preserved. |\n"
        + "| OCR noise | Running headers, OCR artifacts, broken columns, stray symbols, and service captions do not leak into reader output. |\n"
        + "| Ambiguity | Unresolved source readings are marked with `?` or `<!-- REVIEW: ... -->`, not guessed. |\n"
        + "| Terminology | Accepted terms are used consistently; disputed terms are recorded in glossary/QA. |\n"
        + "| Derivatives | Keeper/KB/HTML/PDF are generated only after accepted source-first text. |\n",
        encoding="utf-8",
        newline="\n",
    )
    result = {
        "schema": "translator_localization_prompt_pack.v1",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "config": rel(config_path),
        "status": "pass",
        "action": "rewritten" if existing else "created",
        "profile": profile,
        "prompt_pack_dir": rel(out_dir),
        "files": {key: rel(path) for key, path in files.items()},
    }
    write_json(report, result)
    return result


def mechanics_tokens(text: str) -> list[str]:
    token_re = re.compile(
        r"\b\d+d\d+(?:[+-]\d+)?\b|\b\d+(?:\.\d+)?%?\b|\b(?:STR|CON|SIZ|INT|POW|DEX|APP|EDU|SAN|HP|MOV|DB|BUILD)\b",
        re.I,
    )
    return token_re.findall(text)


def localization_qa_report_path(config: dict[str, Any]) -> Path:
    value = translation_config(config).get("localization_qa_report", "localization_qa_report.json")
    path = Path(str(value).replace("/", "\\"))
    return path.resolve() if path.is_absolute() else qa_root(config) / path


def localization_qa(config_path: Path) -> dict[str, Any]:
    config = read_json(config_path)
    source = translation_source_path(config)
    output = localization_output_path(config)
    report = localization_qa_report_path(config)
    findings: list[dict[str, Any]] = []
    if not source.exists():
        findings.append({"code": "missing_source_markdown", "path": rel(source)})
    if not output.exists():
        findings.append({"code": "missing_output_markdown", "path": rel(output)})
    if findings:
        result = {
            "schema": "translator_localization_qa.v1",
            "generated_at_utc": datetime.now(timezone.utc).isoformat(),
            "config": rel(config_path),
            "source_markdown": rel(source),
            "output_markdown": rel(output),
            "status": "blocked",
            "counts": {"findings": len(findings)},
            "findings": findings,
        }
        write_json(report, result)
        return result

    source_text = source.read_text(encoding="utf-8")
    output_text = output.read_text(encoding="utf-8")
    source_pages = SOURCE_PAGE_RE.findall(source_text)
    output_pages = SOURCE_PAGE_RE.findall(output_text)
    if len(source_pages) != len(output_pages):
        findings.append({"code": "page_marker_count_mismatch", "source": len(source_pages), "output": len(output_pages)})
    if source_pages and output_pages and source_pages != output_pages:
        findings.append({"code": "page_marker_sequence_mismatch", "source_sample": source_pages[:10], "output_sample": output_pages[:10]})
    source_tokens = mechanics_tokens(source_text)
    output_tokens = mechanics_tokens(output_text)
    source_token_counts: dict[str, int] = {}
    output_token_counts: dict[str, int] = {}
    for token in source_tokens:
        source_token_counts[token.upper()] = source_token_counts.get(token.upper(), 0) + 1
    for token in output_tokens:
        output_token_counts[token.upper()] = output_token_counts.get(token.upper(), 0) + 1
    missing_tokens = [
        {"token": token, "source": count, "output": output_token_counts.get(token, 0)}
        for token, count in sorted(source_token_counts.items())
        if output_token_counts.get(token, 0) < count
    ]
    extra_tokens = [
        {"token": token, "source": source_token_counts.get(token, 0), "output": count}
        for token, count in sorted(output_token_counts.items())
        if count > source_token_counts.get(token, 0)
    ]
    if missing_tokens:
        findings.append({"code": "mechanics_tokens_missing_or_reduced", "count": len(missing_tokens), "examples": missing_tokens[:20]})
    if extra_tokens:
        findings.append({"code": "mechanics_tokens_added_or_increased", "count": len(extra_tokens), "examples": extra_tokens[:20]})
    review_markers = len(re.findall(r"<!--\s*REVIEW:|\?", output_text))
    if review_markers:
        findings.append({"code": "unresolved_review_or_uncertain_markers", "count": review_markers})
    service_noise = re.findall(r"\b(?:OCR|tesseract|pdf_image_xref|source render|page render)\b", output_text, flags=re.I)
    if service_noise:
        findings.append({"code": "possible_service_noise_in_output", "count": len(service_noise), "examples": service_noise[:10]})
    result = {
        "schema": "translator_localization_qa.v1",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "config": rel(config_path),
        "source_markdown": rel(source),
        "output_markdown": rel(output),
        "status": "pass" if not findings else "needs_review",
        "counts": {
            "source_page_markers": len(source_pages),
            "output_page_markers": len(output_pages),
            "source_mechanics_tokens": len(source_tokens),
            "output_mechanics_tokens": len(output_tokens),
            "findings": len(findings),
        },
        "findings": findings,
    }
    write_json(report, result)
    return result


def translation_entry_findings(config: dict[str, Any], source: Path) -> list[dict[str, Any]]:
    findings: list[dict[str, Any]] = []
    gates = config.get("scenario_gates") or config.get("production_gates") or {}
    for gate in translation_required_gates(config):
        if gates.get(gate) is not True:
            findings.append({"code": "required_gate_not_true", "gate": gate, "message": f"Required gate is not true: {gate}"})
    findings.extend(source_block_coverage_report_findings(config))
    if not source.exists():
        findings.append({"code": "missing_source_markdown", "path": rel(source), "message": "Translation source markdown does not exist."})
    else:
        findings.extend(translation_source_payload_findings(source))
    return findings


def translation_source_payload_findings(source: Path) -> list[dict[str, Any]]:
    """Catch OCR/source debris before it becomes a translation unit."""
    text = source.read_text(encoding="utf-8")
    suspicious_patterns = [
        (r"\(G YBER", "ocr_garbage_tail", "Probable OCR garbage tail in source text."),
        (r"Derr or \(i", "ocr_garbage_tail", "Probable OCR garbage tail in source text."),
        (r"^\s*4 _", "ocr_garbage_tail", "Probable OCR garbage-only line in source text."),
        (r"^\s*4\s+[\u2018']\s+sg\s+x\s*$", "ocr_garbage_tail", "Probable OCR garbage-only line in source text."),
        (r"^\s*-\s*rs\s*»", "ocr_garbage_tail", "Probable OCR garbage-only list item in source text."),
        (r"\bCON55_", "stat_value_ocr_damage", "Probable OCR damage in stat line."),
        (r"^-\s+—\s+Traits:", "list_marker_ocr_damage", "Duplicated list marker before Traits."),
        (r"\bQuechuah\b", "term_ocr_damage", "Likely OCR misspelling of Quechua in source text."),
        (r"\n\s*\.\s+leader of the Deep Ones", "line_join_ocr_damage", "Probable orphan punctuation from line/column reconstruction."),
    ]
    findings: list[dict[str, Any]] = []
    for pattern, code, message in suspicious_patterns:
        for match in re.finditer(pattern, text, flags=re.MULTILINE):
            page = source_page_for_offset(text, match.start())
            findings.append(
                {
                    "code": code,
                    "path": rel(source),
                    "page": page,
                    "match": match.group(0)[:80],
                    "message": message,
                }
            )
    return findings


def translation_payload_qa(config_path: Path, *, check_only: bool = False) -> dict[str, Any]:
    config = read_json(config_path)
    source = translation_source_path(config)
    report = translation_payload_report_path(config)
    findings: list[dict[str, Any]] = []
    source_sha256: str | None = None
    if not source.exists():
        findings.append({"code": "missing_source_markdown", "path": rel(source), "message": "Translation source markdown does not exist."})
    else:
        source_sha256 = sha256_file(source).upper()
        findings.extend(translation_source_payload_findings(source))
    result = {
        "schema": "translator_translation_payload_qa.v1",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "config": rel(config_path),
        "source_markdown": rel(source),
        "source_markdown_sha256": source_sha256,
        "status": "blocked" if findings else "pass",
        "action": "check_only" if check_only else "created",
        "counts": {"findings": len(findings)},
        "findings": findings,
        "report": rel(report),
    }
    write_json(report, result)
    return result


def source_page_for_offset(text: str, offset: int) -> int | None:
    page: int | None = None
    for match in re.finditer(r"<!--\s*source-page-(\d+)\s*-->", text):
        if match.start() > offset:
            break
        page = int(match.group(1))
    return page


def split_translation_units(markdown: str, *, max_chars: int = 3500) -> list[dict[str, Any]]:
    return split_translation_units_for_config({}, markdown, max_chars=max_chars)


def split_translation_block(block: str, *, max_chars: int) -> list[str]:
    stripped = block.strip()
    if len(stripped) <= max_chars:
        return [stripped] if stripped else []
    parts = [part.strip() for part in re.split(r"(?<=[.!?])\s+(?=[A-Z\"'(\u2018\u201c])", stripped) if part.strip()]
    if len(parts) <= 1:
        parts = [part.strip() for part in stripped.splitlines() if part.strip()]
    chunks: list[str] = []
    current: list[str] = []
    for part in parts:
        if len(part) > max_chars:
            if current:
                chunks.append(" ".join(current).strip())
                current = []
            for start in range(0, len(part), max_chars):
                chunks.append(part[start : start + max_chars].strip())
            continue
        pending = " ".join([*current, part]).strip()
        if current and len(pending) > max_chars:
            chunks.append(" ".join(current).strip())
            current = [part]
        else:
            current.append(part)
    if current:
        chunks.append(" ".join(current).strip())
    return [chunk for chunk in chunks if chunk]


def split_translation_units_for_config(config: dict[str, Any], markdown: str, *, max_chars: int = 3500) -> list[dict[str, Any]]:
    pages = split_raw_text_pages(markdown)
    if not pages:
        pages = [{"page": None, "text": markdown}]
    tr = translation_config(config)
    source_lang = str(tr.get("source_lang", config.get("language_source", "en")))
    target_lang = str(tr.get("target_lang", config.get("language_target", "ru")))
    units: list[dict[str, Any]] = []
    ordinal = 1
    for page in pages:
        page_num = page.get("page")
        chunks: list[str] = []
        current: list[str] = []
        for block in re.split(r"\n{2,}", str(page.get("text") or "")):
            stripped = block.strip()
            if not stripped or stripped.startswith("<!--"):
                continue
            for subblock in split_translation_block(stripped, max_chars=max_chars):
                pending = "\n\n".join([*current, subblock]).strip()
                if current and len(pending) > max_chars:
                    chunks.append("\n\n".join(current).strip())
                    current = [subblock]
                else:
                    current.append(subblock)
        if current:
            chunks.append("\n\n".join(current).strip())
        for chunk in chunks:
            if not chunk:
                continue
            unit_id = f"p{int(page_num):03d}_u{ordinal:04d}" if page_num is not None else f"u{ordinal:04d}"
            units.append(
                {
                    "unit_id": unit_id,
                    "page": page_num,
                    "status": "ready_for_translation",
                    "source_lang": source_lang,
                    "target_lang": target_lang,
                    "source_text": chunk,
                    target_lang: "",
                    "source_hash": sha256_text(chunk),
                }
            )
            ordinal += 1
    return units


def translation_tasks_markdown(result: dict[str, Any]) -> str:
    lines = [
        f"# {result.get('title', 'Translation')} - task packet",
        "",
        f"- Status: `{result['status']}`",
        f"- Source markdown: `{result['source_markdown']}`",
        f"- Units: `{result['counts'].get('units', 0)}`",
        f"- Findings: `{result['counts'].get('findings', 0)}`",
        "",
        "## Purpose",
        "",
        "This packet prepares translation units. It does not call an API, does not fill RU text, and does not approve KeeperBook or production.",
        "",
    ]
    if result.get("findings"):
        lines.extend(["## Findings", ""])
        for finding in result["findings"]:
            label = finding.get("gate") or finding.get("path") or finding.get("message", "")
            lines.append(f"- `{finding.get('code')}`: {label}")
        lines.append("")
    if result.get("units"):
        lines.extend(["## Units", "", "| Unit | Page | Chars | Status |", "|---|---:|---:|---|"])
        for unit in result["units"]:
            lines.append(f"| `{unit['unit_id']}` | {unit.get('page') or ''} | {len(unit.get('source_text', ''))} | `{unit['status']}` |")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def prepare_translation(config_path: Path, *, force: bool = False, check_only: bool = False) -> dict[str, Any]:
    config = read_json(config_path)
    source = translation_source_path(config)
    report = translation_report_path(config)
    tasks_json = translation_output_path(config, "tasks_json", "translation_tasks.json")
    tasks_jsonl = translation_output_path(config, "tasks_jsonl", "translation_tasks.jsonl")
    tasks_md = translation_output_path(config, "tasks_md", "translation_tasks.md")
    findings = translation_entry_findings(config, source)
    if findings:
        result = {
            "schema": "translator_translation_preparation.v1",
            "generated_at_utc": datetime.now(timezone.utc).isoformat(),
            "config": rel(config_path),
            "source_markdown": rel(source),
            "status": "blocked",
            "action": "check_only" if check_only else "not_prepared",
            "required_gates": translation_required_gates(config),
            "counts": {"units": 0, "findings": len(findings)},
            "findings": findings,
            "outputs": {"tasks_json": rel(tasks_json), "tasks_jsonl": rel(tasks_jsonl), "tasks_md": rel(tasks_md)},
        }
        write_json(report, result)
        tasks_md.parent.mkdir(parents=True, exist_ok=True)
        tasks_md.write_text(translation_tasks_markdown(result), encoding="utf-8", newline="\n")
        return result
    if tasks_json.exists() and tasks_md.exists() and not force and not check_only:
        result = read_json(tasks_json)
        result["action"] = "kept_existing"
        write_json(report, result)
        return result
    markdown = source.read_text(encoding="utf-8")
    max_chars = int(translation_config(config).get("max_unit_chars", 3500))
    units = split_translation_units_for_config(config, markdown, max_chars=max_chars)
    oversized = [
        {"code": "translation_unit_too_large", "unit_id": unit["unit_id"], "chars": len(unit["source_text"]), "max_chars": max_chars}
        for unit in units
        if len(unit["source_text"]) > max_chars
    ]
    status = "needs_review" if oversized else "pass"
    result = {
        "schema": "translator_translation_preparation.v1",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "config": rel(config_path),
        "title": str(config.get("scenario_title_en") or config.get("project_key") or "Translation"),
        "source_markdown": rel(source),
        "status": status,
        "action": "check_only" if check_only else ("rewritten" if tasks_json.exists() else "created"),
        "required_gates": translation_required_gates(config),
        "counts": {"units": len(units), "findings": len(oversized)},
        "units": units if not check_only else [],
        "findings": oversized,
        "outputs": {"tasks_json": rel(tasks_json), "tasks_jsonl": rel(tasks_jsonl), "tasks_md": rel(tasks_md)},
    }
    write_json(report, result)
    if not check_only:
        write_json(tasks_json, result)
        tasks_jsonl.parent.mkdir(parents=True, exist_ok=True)
        with tasks_jsonl.open("w", encoding="utf-8", newline="\n") as handle:
            for unit in units:
                handle.write(json.dumps(unit, ensure_ascii=False, sort_keys=True) + "\n")
        tasks_md.parent.mkdir(parents=True, exist_ok=True)
        tasks_md.write_text(translation_tasks_markdown(result), encoding="utf-8", newline="\n")
    return result


def command_exit_code(result: dict[str, Any], *, allow_blocked_exit_zero: bool) -> int:
    status = str(result.get("status") or "fail")
    if status in {"pass", "accepted", "ok", "success"}:
        return 0
    if status in {"fail", "error"}:
        return 1
    overridable_statuses = {
        "blocked",
        "needs_apply",
        "needs_migration",
        "needs_review",
        "pending",
        "trial_needs_review",
    }
    if allow_blocked_exit_zero and status in overridable_statuses:
        return 0
    return 1


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="translator")
    parser.add_argument(
        "--allow-blocked-exit-zero",
        action="store_true",
        help="Return exit code 0 for non-pass diagnostic results while preserving their reported status.",
    )
    sub = parser.add_subparsers(dest="command", required=True)
    init_cmd = sub.add_parser("init-package")
    init_cmd.add_argument("--source-pdf", type=Path, required=True)
    init_cmd.add_argument("--project-key", required=True)
    init_cmd.add_argument("--project-family", default="CoC")
    init_cmd.add_argument("--project-type", default="scenario")
    init_cmd.add_argument("--title-en")
    init_cmd.add_argument("--title-ru")
    init_cmd.add_argument("--config-out", type=Path)
    init_cmd.add_argument("--package-root")
    init_cmd.add_argument("--public-package-root")
    init_cmd.add_argument("--workbench-root")
    init_cmd.add_argument("--qa-root")
    init_cmd.add_argument("--force", action="store_true")
    init_cmd.add_argument("--no-create-dirs", action="store_true")
    init_cmd.add_argument("--allow-blocked-exit-zero", action="store_true", default=argparse.SUPPRESS)
    plan_cmd = sub.add_parser("plan", help="Create and freeze a non-executing pipeline plan in package QA.")
    plan_cmd.add_argument("--config", type=Path, required=True)
    plan_cmd.add_argument("--scope", type=Path, required=True)
    plan_cmd.add_argument(
        "--manifest",
        type=Path,
        default=REPO_ROOT / "translator/config/pipeline-stages.v1.json",
        help="Pipeline stage manifest (default: translator/config/pipeline-stages.v1.json).",
    )
    plan_cmd.add_argument("--allow-blocked-exit-zero", action="store_true", default=argparse.SUPPRESS)
    run_cmd = sub.add_parser("run", help="Execute exactly one frozen pipeline plan from package QA.")
    run_cmd.add_argument("--config", type=Path, required=True)
    run_cmd.add_argument("--plan-sha256", required=True)
    run_cmd.add_argument("--execute", action="store_true", help="Explicitly allow stage execution.")
    run_cmd.add_argument(
        "--plan-filename",
        default=pipeline_run.FROZEN_PLAN_FILENAME,
        help="Frozen plan filename beneath package QA only (default: pipeline_plan.json).",
    )
    run_cmd.add_argument("--allow-blocked-exit-zero", action="store_true", default=argparse.SUPPRESS)
    contract_v2_cmd = sub.add_parser(
        "contract-v2-audit",
        help="Run a read-only Contract V2 control-corpus audit.",
    )
    contract_v2_cmd.add_argument("--manifest", type=Path, required=True)
    contract_v2_cmd.add_argument("--root", type=Path, default=REPO_ROOT)
    contract_v2_cmd.add_argument("--output", type=Path)
    contract_v2_cmd.add_argument("--allow-blocked-exit-zero", action="store_true", default=argparse.SUPPRESS)
    for name in (
        "env-check",
        "validate-config",
        "intake",
        "render-pages",
        "extract-text",
        "ocr-pages",
        "reconstruct-column-ocr",
        "source-text-qa",
        "normalize-source-text",
        "normalize-headings",
        "prepare-source-reconstruction",
        "prepare-statblock-reconstruction",
        "statblock-edition-gate",
        "extract-images",
        "classify-images",
        "image-contact-sheet",
        "prepare-image-approval",
        "apply-image-approval",
        "preserve-page-art",
        "build-review-html",
        "build-production-html",
        "term-gate",
        "layout-anchors",
        "build-production-pdf",
        "prepare-localization-prompt-pack",
        "localization-qa",
        "prepare-translation",
        "translation-payload-qa",
        "build-art-placement-manifest",
        "prepare-art-integration",
        "approval-ledger",
        "build-release-manifest",
        "art-layout-qa",
        "pdf-print-qa",
        "source-block-coverage-gate",
        "page-structure-audit",
        "coc-mechanics-audit",
        "positive-content-audit",
        "remediation-checkpoint-audit",
        "semantic-chain-audit",
        "coverage-gate",
        "critical-remediation-gate",
        "release-qa",
        "legacy-script-audit",
        "optimize-images",
        "postproduction-qa",
        "cleanup-runtime-images",
    ):
        cmd = sub.add_parser(name)
        cmd.add_argument("--config", type=Path, required=True)
        cmd.add_argument("--allow-blocked-exit-zero", action="store_true", default=argparse.SUPPRESS)
        if name == "validate-config":
            cmd.add_argument("--strict-release", action="store_true")
        if name in {"render-pages", "extract-text", "ocr-pages", "reconstruct-column-ocr", "normalize-source-text", "prepare-source-reconstruction", "prepare-statblock-reconstruction", "extract-images", "build-review-html", "build-production-html", "prepare-localization-prompt-pack"}:
            cmd.add_argument("--force", action="store_true")
        if name == "normalize-headings":
            cmd.add_argument("--apply", action="store_true")
        if name == "ocr-pages":
            cmd.add_argument("--promote", action="store_true")
        if name in {
            "render-pages",
            "ocr-pages",
            "reconstruct-column-ocr",
            "source-text-qa",
            "prepare-statblock-reconstruction",
            "extract-images",
        }:
            cmd.add_argument("--pages", action="append", metavar="N|N-M")
        if name == "apply-image-approval":
            cmd.add_argument("--apply", action="store_true")
        if name == "preserve-page-art":
            cmd.add_argument("--apply", action="store_true")
        if name == "reconstruct-column-ocr":
            cmd.add_argument("--apply", action="store_true")
        if name == "build-production-html":
            cmd.add_argument("--check-only", action="store_true")
            cmd.add_argument("--trial", action="store_true")
        if name == "build-production-pdf":
            cmd.add_argument("--check-only", action="store_true")
            cmd.add_argument("--variant")
        if name in {"term-gate", "layout-anchors", "source-block-coverage-gate", "page-structure-audit", "coc-mechanics-audit", "positive-content-audit", "remediation-checkpoint-audit", "semantic-chain-audit", "coverage-gate", "critical-remediation-gate", "release-qa", "approval-ledger", "build-release-manifest", "art-layout-qa", "pdf-print-qa", "build-art-placement-manifest"}:
            cmd.add_argument("--check-only", action="store_true")
        if name == "statblock-edition-gate":
            statblock_mode = cmd.add_mutually_exclusive_group()
            statblock_mode.add_argument("--apply", action="store_true")
            statblock_mode.add_argument("--check-only", action="store_true")
        if name == "prepare-translation":
            cmd.add_argument("--force", action="store_true")
            cmd.add_argument("--check-only", action="store_true")
        if name == "translation-payload-qa":
            cmd.add_argument("--check-only", action="store_true")
        if name == "prepare-art-integration":
            cmd.add_argument("--check-only", action="store_true")
        if name == "pdf-print-qa":
            cmd.add_argument("--variant")
        if name == "cleanup-runtime-images":
            cmd.add_argument("--apply", action="store_true")
    args = parser.parse_args(argv)
    if hasattr(args, "pages"):
        try:
            args.requested_pages = parse_page_selectors(args.pages)
        except ValueError as exc:
            parser.error(str(exc))
    if args.command == "plan":
        try:
            config = read_json(args.config)
            plan = pipeline_plan.plan_from_paths(args.manifest, args.config, args.scope)
            frozen = pipeline_run.freeze_plan(plan, qa_root(config, args.config))
        except (OSError, ValueError, pipeline_plan.PipelinePlanError, pipeline_run.PipelineRunError) as exc:
            print(f"pipeline-plan: {exc}", file=sys.stderr)
            return 2
        blocked = sum(1 for stage in plan["included"] if stage.get("status") == "blocked")
        print(
            "status={status} sha256={sha256} stages={stages} blocked={blocked} json={path}".format(
                status=plan["status"],
                sha256=frozen["sha256"],
                stages=len(plan["included"]),
                blocked=blocked,
                path=frozen["path"],
            )
        )
        return command_exit_code(plan, allow_blocked_exit_zero=args.allow_blocked_exit_zero)
    if args.command == "run":
        if not args.execute:
            print("pipeline-run: run requires explicit --execute", file=sys.stderr)
            return 2
        try:
            config = read_json(args.config)
            result = pipeline_run.execute_frozen_plan(
                qa_root(config, args.config),
                args.config,
                args.plan_sha256,
                filename=args.plan_filename,
            )
        except (OSError, ValueError, pipeline_run.PipelineRunError) as exc:
            print(f"pipeline-run: {exc}", file=sys.stderr)
            return 2
        print(
            "status={status} sha256={sha256} stages={stages}".format(
                status=result["status"],
                sha256=result["plan_sha256"],
                stages=len(result["stages"]),
            )
        )
        return command_exit_code(result, allow_blocked_exit_zero=args.allow_blocked_exit_zero)
    if args.command == "contract-v2-audit":
        try:
            result = contract_v2_audit.audit_manifest(args.root.resolve(), args.manifest)
            if args.output:
                write_json(args.output, result)
        except (OSError, ValueError, json.JSONDecodeError) as exc:
            print(f"contract-v2-audit: {exc}", file=sys.stderr)
            return 2
        summary = result["summary"]
        status = "pass"
        if summary.get("blocked") or summary.get("unexpected_pass"):
            status = "blocked"
        result = {"status": status, **result}
        print(
            "status={status} total={total} pass={passed} expected_failure={expected_failure} blocked={blocked} unexpected_pass={unexpected}".format(
                status=status,
                total=summary["total"],
                passed=summary["pass"],
                expected_failure=summary["expected_failure"],
                blocked=summary["blocked"],
                unexpected=summary["unexpected_pass"],
            )
        )
        return command_exit_code(result, allow_blocked_exit_zero=args.allow_blocked_exit_zero)
    if args.command == "init-package":
        result = init_package(
            source_pdf=args.source_pdf,
            project_key=args.project_key,
            project_family=args.project_family,
            project_type=args.project_type,
            title_en=args.title_en,
            title_ru=args.title_ru,
            config_out=args.config_out,
            package_root_value=args.package_root,
            public_package_root_value=args.public_package_root,
            workbench_root_value=args.workbench_root,
            qa_root_value=args.qa_root,
            force=args.force,
            create_dirs=not args.no_create_dirs,
        )
        print(
            "status={status} config={config} source_exists={source} dirs={dirs}".format(
                status=result["status"],
                config=result["config"],
                source=str(result["source_exists"]).lower(),
                dirs=len(result["created_dirs"]),
            )
        )
        return command_exit_code(result, allow_blocked_exit_zero=args.allow_blocked_exit_zero)
    if args.command == "env-check":
        result = env_check(args.config)
        print(
            "status={status} imports={imports} tools={tools} findings={findings}".format(
                status=result["status"],
                imports=sum(1 for item in result["imports"] if item.get("ok")),
                tools=sum(1 for item in result["commands"].values() if item.get("exists")),
                findings=len(result["findings"]),
            )
        )
        return command_exit_code(result, allow_blocked_exit_zero=args.allow_blocked_exit_zero)
    if args.command == "validate-config":
        result = validate_config(args.config, strict_release=args.strict_release)
        print(
            "status={status} strict_release={strict} missing={missing} source_exists={source} findings={findings}".format(
                status=result["status"],
                strict=str(result.get("strict_release", False)).lower(),
                missing=",".join(result["missing_required_keys"]) or "-",
                source=str(result["paths"].get("source_pdf", {}).get("exists", False)).lower(),
                findings=len(result.get("findings", [])),
            )
        )
        return command_exit_code(result, allow_blocked_exit_zero=args.allow_blocked_exit_zero)
    if args.command == "intake":
        result = intake_pdf(args.config)
        print(
            "status=ok pages={pages} bytes={bytes} sha256={sha}".format(
                pages=result["source_pdf"]["pages"],
                bytes=result["file_size_bytes"],
                sha=result["sha256"][:12],
            )
        )
        return command_exit_code(result, allow_blocked_exit_zero=args.allow_blocked_exit_zero)
    if args.command == "render-pages":
        result = render_pages(args.config, force=args.force, requested_pages=args.requested_pages)
        print(
            "status={status} pages={pages} written={written} existing={existing} dpi={dpi}".format(
                status=result["status"],
                pages=result["page_count"],
                written=len(result["written"]),
                existing=len(result["existing"]),
                dpi=result["dpi"],
            )
        )
        return command_exit_code(result, allow_blocked_exit_zero=args.allow_blocked_exit_zero)
    if args.command == "extract-text":
        result = extract_text(args.config, force=args.force)
        print(
            "status={status} action={action} chars={chars} sha256={sha}".format(
                status=result["status"],
                action=result["action"],
                chars=result["chars"],
                sha=result["sha256"][:12],
            )
        )
        return command_exit_code(result, allow_blocked_exit_zero=args.allow_blocked_exit_zero)
    if args.command == "ocr-pages":
        result = ocr_pages(
            args.config, force=args.force, promote=args.promote, requested_pages=args.requested_pages
        )
        print(
            "status={status} action={action} pages={pages} chars={chars} findings={findings} promoted={promoted}".format(
                status=result["status"],
                action=result["action"],
                pages=result["counts"]["pages"],
                chars=result["counts"]["chars"],
                findings=result["counts"]["findings"],
                promoted=str(result.get("promoted_to_raw_text", False)).lower(),
            )
        )
        return command_exit_code(result, allow_blocked_exit_zero=args.allow_blocked_exit_zero)
    if args.command == "reconstruct-column-ocr":
        result = reconstruct_column_ocr(
            args.config, apply=args.apply, force=args.force, requested_pages=args.requested_pages
        )
        print(
            "status={status} mode={mode} pages={pages} chars={chars} chunks={chunks} findings={findings} gate_changed={gate}".format(
                status=result["status"],
                mode=result["mode"],
                pages=result["counts"]["pages"],
                chars=result["counts"]["chars"],
                chunks=result["counts"]["page_chunks_written"],
                findings=result["counts"]["findings"],
                gate=str(result.get("source_reconstruction_gate_changed", False)).lower(),
            )
        )
        return command_exit_code(result, allow_blocked_exit_zero=args.allow_blocked_exit_zero)
    if args.command == "source-text-qa":
        result = source_text_qa(args.config, requested_pages=args.requested_pages)
        print(
            "status={status} pages={pages} chars={chars} findings={findings} hyphen_breaks={hyphen}".format(
                status=result["status"],
                pages=result["counts"]["pages"],
                chars=result["counts"]["chars"],
                findings=result["counts"]["findings"],
                hyphen=result["counts"]["hyphenated_line_breaks"],
            )
        )
        return command_exit_code(result, allow_blocked_exit_zero=args.allow_blocked_exit_zero)
    if args.command == "normalize-source-text":
        result = normalize_source_text(args.config, force=args.force)
        counts = result.get("counts", {})
        print(
            "status={status} action={action} chars={chars} pages={pages} removed_lines={removed} dehyphenations={dehyphen}".format(
                status=result["status"],
                action=result["action"],
                chars=counts.get("chars", result.get("chars", 0)),
                pages=counts.get("pages", "-"),
                removed=counts.get("removed_lines", "-"),
                dehyphen=counts.get("dehyphenations", "-"),
            )
        )
        return command_exit_code(result, allow_blocked_exit_zero=args.allow_blocked_exit_zero)
    if args.command == "normalize-headings":
        result = normalize_headings(args.config, apply=args.apply)
        print(
            "status={status} action={action} mode={mode} headings={headings} changes={changes} findings={findings}".format(
                status=result["status"],
                action=result["action"],
                mode=result["mode"],
                headings=result["counts"].get("headings_checked", "-"),
                changes=result["counts"].get("changes", "-"),
                findings=result["counts"].get("findings", "-"),
            )
        )
        return command_exit_code(result, allow_blocked_exit_zero=args.allow_blocked_exit_zero)
    if args.command == "prepare-source-reconstruction":
        result = prepare_source_reconstruction(args.config, force=args.force)
        print(
            "status={status} action={action} pages={pages} with_render={with_render} qa_pages={qa_pages} empty={empty}".format(
                status=result["status"],
                action=result["action"],
                pages=result["counts"]["pages"],
                with_render=result["counts"]["pages_with_render"],
                qa_pages=result["counts"]["pages_with_qa_findings"],
                empty=result["counts"]["empty_pages"],
            )
        )
        return command_exit_code(result, allow_blocked_exit_zero=args.allow_blocked_exit_zero)
    if args.command == "prepare-statblock-reconstruction":
        result = prepare_statblock_reconstruction(
            args.config, force=args.force, requested_pages=args.requested_pages
        )
        print(
            "status={status} action={action} profile={profile} candidate_pages={pages} matched_lines={matched}".format(
                status=result["status"],
                action=result["action"],
                profile=result["profile"],
                pages=result["counts"]["candidate_pages"],
                matched=result["counts"]["matched_lines"],
            )
        )
        return command_exit_code(result, allow_blocked_exit_zero=args.allow_blocked_exit_zero)
    if args.command == "statblock-edition-gate":
        result = run_statblock_edition_gate(args.config, apply=args.apply, check_only=args.check_only)
        print(
            "status={status} action={action} source_edition={source} target_edition={target} artifacts={artifacts} conversions={conversions} findings={findings} warnings={warnings}".format(
                status=result["status"],
                action=result["action"],
                source=result.get("source_edition", "-"),
                target=result.get("target_edition", "-"),
                artifacts=result.get("counts", {}).get("artifacts", "-"),
                conversions=result.get("counts", {}).get("conversions", "-"),
                findings=result.get("counts", {}).get("findings", "-"),
                warnings=result.get("counts", {}).get("warnings", "-"),
            )
        )
        return command_exit_code(result, allow_blocked_exit_zero=args.allow_blocked_exit_zero)
    if args.command == "extract-images":
        result = extract_images(args.config, force=args.force, requested_pages=args.requested_pages)
        print(
            "status={status} unique={unique} refs={refs} written={written} existing={existing}".format(
                status=result["status"],
                unique=result["counts"]["unique_images"],
                refs=result["counts"]["page_image_refs"],
                written=result["counts"]["written"],
                existing=result["counts"]["existing"],
            )
        )
        return command_exit_code(result, allow_blocked_exit_zero=args.allow_blocked_exit_zero)
    if args.command == "classify-images":
        result = classify_images(args.config)
        print(
            "status={status} candidates={candidates} review_required={review} decoration={decoration}".format(
                status=result["status"],
                candidates=result["counts"]["candidates"],
                review=result["counts"]["review_required"],
                decoration=result["counts"]["auto_suggested_decoration"],
            )
        )
        return command_exit_code(result, allow_blocked_exit_zero=args.allow_blocked_exit_zero)
    if args.command == "image-contact-sheet":
        result = make_contact_sheet(args.config)
        print(
            "status={status} candidates={candidates} sheet={sheet} missing={missing}".format(
                status=result["status"],
                candidates=result["counts"]["candidates"],
                sheet=result["contact_sheet"],
                missing=result["counts"]["missing_images"],
            )
        )
        return command_exit_code(result, allow_blocked_exit_zero=args.allow_blocked_exit_zero)
    if args.command == "prepare-image-approval":
        result = prepare_image_approval(args.config)
        print(
            "status={status} pending={pending} contact_sheet={sheet}".format(
                status=result["status"],
                pending=result["counts"]["pending"],
                sheet=result["contact_sheet"],
            )
        )
        return command_exit_code(result, allow_blocked_exit_zero=args.allow_blocked_exit_zero)
    if args.command == "apply-image-approval":
        result = apply_image_approval(args.config, apply=args.apply)
        print(
            "status={status} mode={mode} applied={applied} skipped={skipped} findings={findings}".format(
                status=result["status"],
                mode=result["mode"],
                applied=result["counts"]["applied_or_would_apply"],
                skipped=result["counts"]["skipped"],
                findings=result["counts"]["findings"],
            )
        )
        return command_exit_code(result, allow_blocked_exit_zero=args.allow_blocked_exit_zero)
    if args.command == "preserve-page-art":
        result = preserve_page_art(args.config, apply=args.apply)
        print(
            "status={status} mode={mode} configured={configured} preserved={preserved} findings={findings}".format(
                status=result["status"],
                mode=result["mode"],
                configured=result["counts"]["configured"],
                preserved=result["counts"]["preserved_or_would_preserve"],
                findings=result["counts"]["findings"],
            )
        )
        return command_exit_code(result, allow_blocked_exit_zero=args.allow_blocked_exit_zero)
    if args.command == "build-review-html":
        result = build_review_html(args.config, force=args.force)
        print(
            "status={status} action={action} pages={pages} headings={headings} images={images} findings={findings}".format(
                status=result["status"],
                action=result["action"],
                pages=result["counts"].get("source_pages", "-"),
                headings=result["counts"].get("headings", "-"),
                images=result["counts"].get("image_refs", "-"),
                findings=result["counts"].get("findings", "-"),
            )
        )
        return command_exit_code(result, allow_blocked_exit_zero=args.allow_blocked_exit_zero)
    if args.command == "build-production-html":
        result = build_production_html(args.config, force=args.force, check_only=args.check_only, trial=args.trial)
        print(
            "status={status} action={action} mode={mode} pages={pages} headings={headings} images={images} findings={findings}".format(
                status=result["status"],
                action=result["action"],
                mode=result.get("mode", "production"),
                pages=result.get("counts", {}).get("source_pages", "-"),
                headings=result.get("counts", {}).get("headings", "-"),
                images=result.get("counts", {}).get("image_refs", "-"),
                findings=result.get("counts", {}).get("findings", "-"),
            )
        )
        return command_exit_code(result, allow_blocked_exit_zero=args.allow_blocked_exit_zero)
    if args.command == "term-gate":
        result = run_term_gate(args.config, check_only=args.check_only)
        print(
            "status={status} action={action} accepted={accepted} checked={checked} findings={findings}".format(
                status=result["status"],
                action=result["action"],
                accepted=result.get("counts", {}).get("accepted_terms", "-"),
                checked=result.get("counts", {}).get("checked_terms_present_in_source", "-"),
                findings=result.get("counts", {}).get("findings", "-"),
            )
        )
        return command_exit_code(result, allow_blocked_exit_zero=args.allow_blocked_exit_zero)
    if args.command == "layout-anchors":
        result = run_layout_anchors(args.config, check_only=args.check_only)
        print(
            "status={status} action={action} headings={headings} tables={tables} images={images} findings={findings}".format(
                status=result["status"],
                action=result["action"],
                headings=result.get("counts", {}).get("headings", "-"),
                tables=result.get("counts", {}).get("tables", "-"),
                images=result.get("counts", {}).get("images", "-"),
                findings=result.get("counts", {}).get("findings", "-"),
            )
        )
        return command_exit_code(result, allow_blocked_exit_zero=args.allow_blocked_exit_zero)
    if args.command == "source-block-coverage-gate":
        result = run_source_block_coverage_gate(args.config, check_only=args.check_only)
        print(
            "status={status} action={action} findings={findings} input_hashes={input_hashes}".format(
                status=result["status"],
                action=result["action"],
                findings=result.get("counts", {}).get("findings", "-"),
                input_hashes=result.get("counts", {}).get("input_hashes", "-"),
            )
        )
        return command_exit_code(result, allow_blocked_exit_zero=args.allow_blocked_exit_zero)
    if args.command == "page-structure-audit":
        result = run_page_structure_audit(args.config, check_only=args.check_only)
        print(
            "status={status} pages={pages} risk_pages={risk_pages} findings={findings} unaccepted={unaccepted} report={report}".format(
                status=result["status"],
                pages=result["pages"],
                risk_pages=result["risk_pages"],
                findings=len(result["findings"]),
                unaccepted=result["ledger"]["unaccepted_risk_count"],
                report=result["report"],
            )
        )
        return command_exit_code(result, allow_blocked_exit_zero=args.allow_blocked_exit_zero)
    if args.command == "coc-mechanics-audit":
        result = run_coc_mechanics_audit(args.config, check_only=args.check_only)
        print(
            "status={status} statblocks={statblocks} residue={residue} findings={findings} report={report}".format(
                status=result["status"],
                statblocks=result["counts"]["statblock_cards"],
                residue=result["counts"]["visible_english_mechanics_labels"],
                findings=result["counts"]["findings"],
                report=result["report"],
            )
        )
        return command_exit_code(result, allow_blocked_exit_zero=args.allow_blocked_exit_zero)
    if args.command == "positive-content-audit":
        result = run_positive_content_audit(args.config, check_only=args.check_only)
        print(
            "status={status} tables={tables} images={images} statblocks={statblocks} kb_files={kb_files} findings={findings} report={report}".format(
                status=result["status"],
                tables=result["counts"]["html_tables"],
                images=result["counts"]["html_images"],
                statblocks=result["counts"]["html_statblock_cards"],
                kb_files=result["counts"]["kb_files"],
                findings=len(result["findings"]),
                report=result["report"],
            )
        )
        return command_exit_code(result, allow_blocked_exit_zero=args.allow_blocked_exit_zero)
    if args.command == "remediation-checkpoint-audit":
        result = run_remediation_checkpoint_audit(args.config, check_only=args.check_only)
        print(
            "status={status} findings={findings} remediations={remediations} gates={gates} audit_findings={audit_findings} report={report}".format(
                status=result["status"],
                findings=result["counts"]["findings"],
                remediations=result["counts"]["remediations"],
                gates=result["counts"]["gates"],
                audit_findings=result["counts"]["audit_findings"],
                report=result["report"],
            )
        )
        return command_exit_code(result, allow_blocked_exit_zero=args.allow_blocked_exit_zero)
    if args.command == "semantic-chain-audit":
        result = run_semantic_chain_audit(args.config, check_only=args.check_only)
        print(
            "status={status} artifacts={artifacts} reports={reports} links={links} findings={findings} report={report}".format(
                status=result["status"],
                artifacts=result["counts"]["artifacts"],
                reports=result["counts"]["reports"],
                links=result["counts"]["links"],
                findings=result["counts"]["findings"],
                report=result["report"],
            )
        )
        return command_exit_code(result, allow_blocked_exit_zero=args.allow_blocked_exit_zero)
    if args.command == "coverage-gate":
        result = run_coverage_gate(args.config, check_only=args.check_only)
        print(
            "status={status} action={action} source_pages={source_pages} ru_pages={ru_pages} source_headings={source_headings} ru_headings={ru_headings} findings={findings} warnings={warnings}".format(
                status=result["status"],
                action=result["action"],
                source_pages=result.get("counts", {}).get("source_pages", "-"),
                ru_pages=result.get("counts", {}).get("ru_pages", "-"),
                source_headings=result.get("counts", {}).get("source_headings", "-"),
                ru_headings=result.get("counts", {}).get("ru_headings", "-"),
                findings=result.get("counts", {}).get("findings", "-"),
                warnings=result.get("counts", {}).get("warnings", "-"),
            )
        )
        return command_exit_code(result, allow_blocked_exit_zero=args.allow_blocked_exit_zero)
    if args.command == "critical-remediation-gate":
        result = run_critical_remediation_gate(args.config, check_only=args.check_only)
        print(
            "status={status} action={action} mode={mode} source_pages={source_pages} pdf_pages={pdf_pages} findings={findings} warnings={warnings}".format(
                status=result["status"],
                action=result["action"],
                mode=result.get("pdf_mode", "-"),
                source_pages=result.get("counts", {}).get("source_pdf_pages", "-"),
                pdf_pages=result.get("counts", {}).get("production_pdf_pages", "-"),
                findings=result.get("counts", {}).get("findings", "-"),
                warnings=result.get("counts", {}).get("warnings", "-"),
            )
        )
        return command_exit_code(result, allow_blocked_exit_zero=args.allow_blocked_exit_zero)
    if args.command == "build-production-pdf":
        result = build_production_pdf(args.config, check_only=args.check_only, variant=args.variant)
        print(
            "status={status} action={action} variant={variant} findings={findings}".format(
                status=result["status"],
                action=result["action"],
                variant=result.get("variant") or "-",
                findings=result.get("counts", {}).get("findings", "-"),
            )
        )
        return command_exit_code(result, allow_blocked_exit_zero=args.allow_blocked_exit_zero)
    if args.command == "prepare-localization-prompt-pack":
        result = localization_prompt_pack(args.config, force=args.force)
        print(
            "status={status} action={action} profile={profile} dir={directory} files={files}".format(
                status=result["status"],
                action=result["action"],
                profile=result["profile"],
                directory=result["prompt_pack_dir"],
                files=len(result["files"]),
            )
        )
        return command_exit_code(result, allow_blocked_exit_zero=args.allow_blocked_exit_zero)
    if args.command == "localization-qa":
        result = localization_qa(args.config)
        print(
            "status={status} source_pages={source_pages} output_pages={output_pages} findings={findings}".format(
                status=result["status"],
                source_pages=result.get("counts", {}).get("source_page_markers", "-"),
                output_pages=result.get("counts", {}).get("output_page_markers", "-"),
                findings=result.get("counts", {}).get("findings", "-"),
            )
        )
        return command_exit_code(result, allow_blocked_exit_zero=args.allow_blocked_exit_zero)
    if args.command == "prepare-translation":
        result = prepare_translation(args.config, force=args.force, check_only=args.check_only)
        print(
            "status={status} action={action} units={units} findings={findings}".format(
                status=result["status"],
                action=result["action"],
                units=result.get("counts", {}).get("units", "-"),
                findings=result.get("counts", {}).get("findings", "-"),
            )
        )
        return command_exit_code(result, allow_blocked_exit_zero=args.allow_blocked_exit_zero)
    if args.command == "translation-payload-qa":
        result = translation_payload_qa(args.config, check_only=args.check_only)
        print(
            "status={status} action={action} findings={findings} report={report}".format(
                status=result["status"],
                action=result["action"],
                findings=result.get("counts", {}).get("findings", "-"),
                report=result.get("report", "-"),
            )
        )
        return command_exit_code(result, allow_blocked_exit_zero=args.allow_blocked_exit_zero)
    if args.command == "prepare-art-integration":
        result = prepare_art_integration(args.config, check_only=args.check_only)
        print(
            "status={status} action={action} pending={pending} approved={approved} copied={copied} missing={missing} findings={findings}".format(
                status=result["status"],
                action=result["action"],
                pending=result.get("counts", {}).get("approval_pending", "-"),
                approved=result.get("counts", {}).get("approval_approved", "-"),
                copied=result.get("counts", {}).get("copied_targets", "-"),
                missing=result.get("counts", {}).get("missing_targets", "-"),
                findings=result.get("counts", {}).get("findings", "-"),
            )
        )
        return command_exit_code(result, allow_blocked_exit_zero=args.allow_blocked_exit_zero)
    if args.command == "build-art-placement-manifest":
        result = build_art_placement_manifest(args.config, check_only=args.check_only)
        print(
            "status={status} action={action} placements={placements} approved={approved} fallback={fallback} findings={findings}".format(
                status=result["status"],
                action=result["action"],
                placements=result["counts"]["placements"],
                approved=result["counts"]["approved_extracted"],
                fallback=result["counts"]["legacy_page_render_rows"],
                findings=result["counts"]["findings"],
            )
        )
        return command_exit_code(result, allow_blocked_exit_zero=args.allow_blocked_exit_zero)
    if args.command == "approval-ledger":
        result = run_approval_ledger(args.config, check_only=args.check_only)
        print(
            "status={status} action={action} gates={gates} findings={findings} warnings={warnings}".format(
                status=result["status"],
                action="check_only" if args.check_only else "checked",
                gates=result.get("counts", {}).get("gates", "-"),
                findings=result.get("counts", {}).get("findings", "-"),
                warnings=result.get("counts", {}).get("warnings", "-"),
            )
        )
        return command_exit_code(result, allow_blocked_exit_zero=args.allow_blocked_exit_zero)
    if args.command == "build-release-manifest":
        result = build_release_manifest(args.config, check_only=args.check_only)
        print(
            "status={status} action={action} artifacts={artifacts} existing={existing} findings={findings} warnings={warnings}".format(
                status=result["status"],
                action=result["action"],
                artifacts=result.get("counts", {}).get("artifacts", "-"),
                existing=result.get("counts", {}).get("existing", "-"),
                findings=result.get("counts", {}).get("findings", "-"),
                warnings=result.get("counts", {}).get("warnings", "-"),
            )
        )
        return command_exit_code(result, allow_blocked_exit_zero=args.allow_blocked_exit_zero)
    if args.command == "art-layout-qa":
        result = run_art_layout_qa(args.config, check_only=args.check_only)
        print(
            "status={status} action={action} placements={placements} image_refs={refs} findings={findings} warnings={warnings}".format(
                status=result["status"],
                action=result["action"],
                placements=result.get("counts", {}).get("placements", "-"),
                refs=result.get("counts", {}).get("html_image_refs", "-"),
                findings=result.get("counts", {}).get("findings", "-"),
                warnings=result.get("counts", {}).get("warnings", "-"),
            )
        )
        return command_exit_code(result, allow_blocked_exit_zero=args.allow_blocked_exit_zero)
    if args.command == "pdf-print-qa":
        result = run_pdf_print_qa(args.config, check_only=args.check_only, variant=args.variant)
        print(
            "status={status} action={action} variant={variant} pages={pages} text_chars={chars} findings={findings} warnings={warnings}".format(
                status=result["status"],
                action=result["action"],
                variant=result.get("variant") or "-",
                pages=result.get("counts", {}).get("pdf_pages", "-"),
                chars=result.get("counts", {}).get("pdf_text_chars", "-"),
                findings=result.get("counts", {}).get("findings", "-"),
                warnings=result.get("counts", {}).get("warnings", "-"),
            )
        )
        return command_exit_code(result, allow_blocked_exit_zero=args.allow_blocked_exit_zero)
    if args.command == "release-qa":
        result = run_release_qa(args.config, check_only=args.check_only)
        print(
            "status={status} action={action} image_refs={refs} findings={findings} warnings={warnings}".format(
                status=result["status"],
                action=result["action"],
                refs=result.get("counts", {}).get("image_refs", "-"),
                findings=result.get("counts", {}).get("findings", "-"),
                warnings=result.get("counts", {}).get("warnings", "-"),
            )
        )
        return command_exit_code(result, allow_blocked_exit_zero=args.allow_blocked_exit_zero)
    if args.command == "legacy-script-audit":
        result = run_legacy_script_audit(args.config)
        print(
            "status={status} files={files} hardcoded={hardcoded} no_env={no_env}".format(
                status=result["status"],
                files=result["counts"]["files"],
                hardcoded=result["counts"]["hardcoded_path_files"],
                no_env=result["counts"]["translator_wormsign_without_nri_root_env"],
            )
        )
        return command_exit_code(result, allow_blocked_exit_zero=args.allow_blocked_exit_zero)
    if args.command == "optimize-images":
        result = optimize_images(args.config)
        print(
            "status=ok converted={converted} html_changed={changed} order={order}".format(
                converted=result["counts"]["converted_png_refs"],
                changed=str(result["html_changed"]).lower(),
                order=result["landing_toc_order"]["action"],
            )
        )
        return command_exit_code(result, allow_blocked_exit_zero=args.allow_blocked_exit_zero)
    if args.command == "postproduction-qa":
        result = postproduction_qa(args.config)
        print(
            "status={status} first={first} image_refs={refs} optimized={opt} png_refs={png} findings={findings}".format(
                status=result["status"],
                first=",".join(result["first_flow_items"][:3]),
                refs=result["counts"]["image_refs"],
                opt=result["counts"]["optimized_refs"],
                png=result["counts"]["png_runtime_refs"],
                findings=len(result["findings"]),
            )
        )
        return command_exit_code(result, allow_blocked_exit_zero=args.allow_blocked_exit_zero)
    if args.command == "cleanup-runtime-images":
        result = cleanup_runtime_images(args.config, apply=args.apply)
        print(
            "status={status} action={action} refs={refs} unused={unused} deleted={deleted} findings={findings}".format(
                status=result["status"],
                action=result["action"],
                refs=result["counts"]["html_image_refs"],
                unused=result["counts"]["unused_candidates"],
                deleted=result["counts"]["deleted"] + result["counts"].get("deleted_dirs", 0),
                findings=result["counts"]["findings"],
            )
        )
        return command_exit_code(result, allow_blocked_exit_zero=args.allow_blocked_exit_zero)
    raise AssertionError(args.command)


if __name__ == "__main__":
    raise SystemExit(main())
