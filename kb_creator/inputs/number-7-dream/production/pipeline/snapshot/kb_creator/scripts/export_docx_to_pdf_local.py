#!/usr/bin/env python3
"""Fail-closed local LibreOffice DOCX-to-PDF export with sealed tool evidence."""

from __future__ import annotations

import argparse
import configparser
import hashlib
import json
import os
import shutil
import stat
import subprocess
import tempfile
import time
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[2]
TOOLS_ROOT = REPO_ROOT / ".tools"
RUNTIME_ROOT = TOOLS_ROOT / "runtime" / "kb_creator" / "docx_pdf"


class LocalExportError(ValueError):
    pass


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def _identity(path: Path) -> dict[str, Any]:
    return {"path": str(path.resolve(strict=True)), "bytes": path.stat().st_size, "sha256": _sha(path)}


def _is_reparse(path: Path) -> bool:
    attributes = getattr(path.lstat(), "st_file_attributes", 0)
    return path.is_symlink() or bool(attributes & getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0))


def _contained(path: Path, root: Path, suffix: str, *, must_exist: bool) -> Path:
    root = root.resolve(strict=True)
    path = path.resolve(strict=must_exist)
    try:
        path.relative_to(root)
    except ValueError as error:
        raise LocalExportError("path escapes assigned stage root") from error
    if path.suffix.lower() != suffix:
        raise LocalExportError(f"path must use {suffix}")
    cursor = path if must_exist else path.parent
    while cursor != root:
        if _is_reparse(cursor):
            raise LocalExportError("path contains reparse content")
        cursor = cursor.parent
    if must_exist:
        if not path.is_file() or _is_reparse(path):
            raise LocalExportError("input must be a regular file")
    elif path.exists():
        raise LocalExportError("output must be absent")
    return path


def _libreoffice(path: Path) -> Path:
    executable = path.resolve(strict=True)
    try:
        executable.relative_to(TOOLS_ROOT.resolve(strict=True))
    except ValueError as error:
        raise LocalExportError("LibreOffice must resolve below repository .tools") from error
    if executable.name.lower() not in {"soffice", "soffice.exe", "soffice.com", "libreoffice", "libreoffice.exe"}:
        raise LocalExportError("unexpected LibreOffice executable name")
    if not executable.is_file() or _is_reparse(executable):
        raise LocalExportError("LibreOffice executable must be a regular file")
    return executable


def _libreoffice_version(executable: Path) -> str:
    version_file = executable.parent / "version.ini"
    if not version_file.is_file() or _is_reparse(version_file):
        raise LocalExportError("LibreOffice version.ini is missing")
    parser = configparser.ConfigParser(interpolation=None)
    parser.read(version_file, encoding="utf-8")
    build_id = parser.get("Version", "buildid", fallback="").strip()
    if not build_id:
        raise LocalExportError("LibreOffice version.ini lacks buildid")
    release = executable.parent.parent.name.strip()
    if not release:
        raise LocalExportError("LibreOffice release directory is invalid")
    return f"{release};buildid={build_id}"


def _runtime_root() -> Path:
    tools = TOOLS_ROOT.resolve(strict=True)
    target = RUNTIME_ROOT.absolute()
    try:
        target.relative_to(tools)
    except ValueError as error:
        raise LocalExportError("LibreOffice runtime root must be below repository .tools") from error
    cursor = target
    missing: list[Path] = []
    while not cursor.exists():
        missing.append(cursor)
        cursor = cursor.parent
    while cursor != tools:
        if _is_reparse(cursor):
            raise LocalExportError("LibreOffice runtime root contains reparse content")
        cursor = cursor.parent
    if _is_reparse(tools):
        raise LocalExportError("repository .tools cannot be reparse content")
    for path in reversed(missing):
        path.mkdir()
    resolved = target.resolve(strict=True)
    if resolved != target or _is_reparse(resolved) or not resolved.is_dir():
        raise LocalExportError("LibreOffice runtime root is not a regular directory")
    return resolved


def export_docx(
    docx: Path,
    pdf: Path,
    stage_root: Path,
    libreoffice: Path,
    *,
    evidence_output: Path | None = None,
    transient: bool = False,
    timeout_seconds: int = 180,
) -> dict[str, Any]:
    if transient == (evidence_output is not None):
        raise LocalExportError("transient export forbids evidence; final export requires it")
    stage_root = stage_root.resolve(strict=True)
    docx = _contained(docx, stage_root, ".docx", must_exist=True)
    pdf = _contained(pdf, stage_root, ".pdf", must_exist=False)
    evidence = None if evidence_output is None else _contained(evidence_output, stage_root, ".json", must_exist=False)
    executable = _libreoffice(libreoffice)
    version = _libreoffice_version(executable)

    workspace = Path(tempfile.mkdtemp(prefix="lo-", dir=_runtime_root()))
    profile = workspace / "profile"
    converted = workspace / "converted"
    profile.mkdir(); converted.mkdir()
    started = time.monotonic()
    try:
        process = subprocess.run(
            [
                str(executable), "--headless", "--nologo", "--nodefault", "--nofirststartwizard",
                f"-env:UserInstallation={profile.resolve().as_uri()}",
                "--convert-to", "pdf:writer_pdf_Export", "--outdir", str(converted), str(docx),
            ],
            capture_output=True, text=True, timeout=timeout_seconds, check=False,
        )
        generated = converted / f"{docx.stem}.pdf"
        deadline = time.monotonic() + timeout_seconds
        previous_size = -1
        stable_polls = 0
        while time.monotonic() < deadline:
            if generated.is_file():
                size = generated.stat().st_size
                stable_polls = stable_polls + 1 if size > 0 and size == previous_size else 0
                previous_size = size
                if stable_polls >= 1:
                    break
            time.sleep(0.2)
        candidates = [item for item in converted.glob("*.pdf") if item.is_file()]
        if process.returncode != 0 or candidates != [generated] or generated.stat().st_size < 1 or stable_polls < 1:
            detail = (process.stderr or process.stdout)[-500:]
            raise LocalExportError(f"LibreOffice export failed or produced a non-exact output set: {detail}")
        os.replace(generated, pdf)
    except Exception:
        if pdf.exists():
            pdf.unlink()
        raise
    finally:
        shutil.rmtree(workspace, ignore_errors=True)
    if workspace.exists():
        if pdf.exists():
            pdf.unlink()
        raise LocalExportError("LibreOffice export workspace cleanup failed")

    result = {
        "schema": "kb_creator.local_libreoffice_docx_pdf_export.v1",
        "status": "pass",
        "input": _identity(docx),
        "output": _identity(pdf),
        "engine": {**_identity(executable), "name": "libreoffice", "version": version},
        "export": {
            "filter": "writer_pdf_Export", "headless": True, "all_pages": True,
            "fresh_export": True, "document_input_role": "accepted_docx" if not transient else "docx_candidate",
        },
        "cleanup": {"profile_absent": True, "conversion_workspace_absent": True, "temporary_output_absent": True, "status": "pass"},
        "elapsed_ms": int((time.monotonic() - started) * 1000),
    }
    if evidence is not None:
        temp = evidence.with_suffix(evidence.suffix + ".tmp")
        temp.write_text(json.dumps(result, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n", encoding="utf-8", newline="\n")
        os.replace(temp, evidence)
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--docx", required=True, type=Path)
    parser.add_argument("--pdf", required=True, type=Path)
    parser.add_argument("--stage-root", required=True, type=Path)
    parser.add_argument("--libreoffice", required=True, type=Path)
    parser.add_argument("--evidence-output", type=Path)
    parser.add_argument("--transient", action="store_true")
    parser.add_argument("--timeout-seconds", type=int, default=180)
    args = parser.parse_args()
    try:
        result = export_docx(
            args.docx, args.pdf, args.stage_root, args.libreoffice,
            evidence_output=args.evidence_output, transient=args.transient, timeout_seconds=args.timeout_seconds,
        )
    except Exception as error:
        print(json.dumps({"status": "fail", "error": f"{type(error).__name__}: {error}"}, ensure_ascii=False), file=__import__("sys").stderr)
        return 2
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
