#!/usr/bin/env python3
"""Render publication candidates with repository Poppler and emit closed page QA."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Any, Callable

from PIL import Image
from pypdf import PdfReader


REPO_ROOT = Path(__file__).resolve().parents[2]
POPLER_ROOT = REPO_ROOT / ".tools" / "poppler"


class RenderQaError(ValueError):
    pass


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def _identity(path: Path, root: Path) -> dict[str, Any]:
    return {"path": path.relative_to(root).as_posix(), "bytes": path.stat().st_size, "sha256": _sha(path)}


def _write(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n", encoding="utf-8", newline="\n")


def _repository_poppler(executable: Path) -> Path:
    executable = executable.resolve(strict=True)
    try:
        executable.relative_to(POPLER_ROOT.resolve(strict=True))
    except ValueError as error:
        raise RenderQaError("pdftoppm must resolve below repository .tools/poppler") from error
    if executable.name.lower() not in {"pdftoppm", "pdftoppm.exe"}:
        raise RenderQaError("unexpected Poppler executable")
    return executable


def render_pdf_pages(
    source: Path,
    output_root: Path,
    pdftoppm: Path,
    *,
    dpi: int = 110,
    source_kind: str = "final_pdf",
    retain_source_identity: bool = True,
) -> dict[str, Any]:
    source = source.resolve(strict=True)
    if source.suffix.lower() != ".pdf" or not source.is_file() or source.is_symlink():
        raise RenderQaError("render source must be a regular PDF")
    if output_root.exists() or not output_root.parent.is_dir():
        raise RenderQaError("render output must be absent below an existing parent")
    executable = _repository_poppler(pdftoppm)
    if isinstance(dpi, bool) or not isinstance(dpi, int) or not 72 <= dpi <= 600:
        raise RenderQaError("render DPI must be an integer from 72 to 600")
    reader = PdfReader(str(source))
    page_count = len(reader.pages)
    if page_count < 1:
        raise RenderQaError("PDF has no pages")
    stage = Path(tempfile.mkdtemp(prefix=f".{output_root.name}.staging.", dir=output_root.parent))
    try:
        prefix = stage / "page"
        process = subprocess.run(
            [str(executable), "-png", "-r", str(dpi), str(source), str(prefix)],
            capture_output=True,
            text=True,
            timeout=180,
            check=False,
        )
        if process.returncode != 0:
            raise RenderQaError(f"Poppler render failed with exit {process.returncode}: {process.stderr[-500:]}")
        raw_pages = sorted(stage.glob("page-*.png"))
        if len(raw_pages) != page_count:
            raise RenderQaError(f"rendered page count mismatch: expected {page_count}, got {len(raw_pages)}")
        pages = []
        for index, raw in enumerate(raw_pages, 1):
            target = stage / f"page-{index:03d}.png"
            if raw != target:
                raw.replace(target)
            with Image.open(target) as image:
                image.load()
                gray = image.convert("L")
                histogram = gray.histogram()
                total = image.width * image.height
                occupied = sum(histogram[:245])
                occupancy = round(occupied / total, 8) if total else 0.0
                dimensions = {"width": image.width, "height": image.height}
            text_chars = len((reader.pages[index - 1].extract_text() or "").strip())
            near_blank = occupancy < 0.002 and text_chars < 5
            pages.append(
                {
                    "page": index,
                    "image": _identity(target, stage),
                    "dimensions": dimensions,
                    "text_chars": text_chars,
                    "occupancy": occupancy,
                    "near_blank": near_blank,
                    "orphan_signal": text_chars < 5 and occupancy < 0.01,
                }
            )
        inventory = {
            "schema": "kb_creator.publication_render_inventory.v1",
            "source_kind": source_kind,
            "source": _identity(source, source.parent) if retain_source_identity else None,
            "renderer": {"path": str(executable), "bytes": executable.stat().st_size, "sha256": _sha(executable)},
            "dpi": dpi,
            "page_count": page_count,
            "pages": pages,
            "signals": {
                "near_blank_pages": [row["page"] for row in pages if row["near_blank"]],
                "orphan_signal_pages": [row["page"] for row in pages if row["orphan_signal"]],
            },
        }
        _write(stage / "render_inventory.json", inventory)
        _write(
            stage / "review_index.json",
            {
                "schema": "kb_creator.publication_page_review_index.v1",
                "source_kind": source_kind,
                "page_count": page_count,
                "pages": [{"page": row["page"], "image": row["image"], "review_state": "pending_human_review"} for row in pages],
                "review_state": "pending_human_review",
            },
        )
        os.replace(stage, output_root)
        return {"status": "pass", "page_count": page_count, "render_inventory": _identity(output_root / "render_inventory.json", output_root), "review_state": "pending_human_review"}
    except Exception:
        shutil.rmtree(stage, ignore_errors=True)
        raise


def _word_transient_export(
    powershell: Path,
    exporter: Path,
    source_docx: Path,
    bridge: Path,
    stage_root: Path,
) -> None:
    process = subprocess.run(
        [str(powershell), "-NoProfile", "-File", str(exporter), "-Docx", str(source_docx), "-Pdf", str(bridge), "-StageRoot", str(stage_root), "-TransientBridge"],
        capture_output=True,
        text=True,
        timeout=180,
        check=False,
    )
    if process.returncode != 0:
        raise RenderQaError(f"transient Word bridge failed with exit {process.returncode}")


def _libreoffice_transient_export(
    python: Path,
    exporter: Path,
    libreoffice: Path,
    source_docx: Path,
    bridge: Path,
    private_root: Path,
    stage_root: Path,
) -> None:
    process = subprocess.run(
        [
            str(python), "-I", str(exporter),
            "--docx", str(source_docx), "--pdf", str(bridge),
            "--stage-root", str(stage_root),
            "--libreoffice", str(libreoffice), "--transient",
        ],
        capture_output=True,
        text=True,
        timeout=240,
        check=False,
    )
    if process.returncode != 0:
        raise RenderQaError(f"transient LibreOffice bridge failed with exit {process.returncode}: {process.stderr[-500:]}")


def render_docx_transient(
    source_docx: Path,
    output_root: Path,
    private_root: Path,
    exporter_script: Path,
    powershell: Path,
    pdftoppm: Path,
    *,
    dpi: int = 110,
    export: Callable[[Path, Path, Path], None] | None = None,
    python: Path | None = None,
    libreoffice: Path | None = None,
    local_exporter_script: Path | None = None,
    stage_root: Path | None = None,
) -> dict[str, Any]:
    source_docx = source_docx.resolve(strict=True)
    if source_docx.suffix.lower() != ".docx" or not source_docx.is_file() or source_docx.is_symlink():
        raise RenderQaError("transient render source must be a regular DOCX")
    if private_root.exists() or not private_root.parent.is_dir():
        raise RenderQaError("private bridge root must be absent below an existing parent")
    private_root.mkdir()
    bridge = private_root / "bridge.pdf"
    export_stage_root = (stage_root or private_root.parent).resolve(strict=True)
    cleanup_passed = False
    rendered: dict[str, Any] | None = None
    try:
        if export is not None:
            export(source_docx, bridge, private_root)
            engine = "injected_test"
        elif libreoffice is not None:
            if python is None or local_exporter_script is None:
                raise RenderQaError("LibreOffice transient render lacks explicit Python or exporter binding")
            _libreoffice_transient_export(
                python.resolve(strict=True), local_exporter_script.resolve(strict=True),
                libreoffice.resolve(strict=True), source_docx, bridge, private_root, export_stage_root,
            )
            engine = "libreoffice"
        else:
            _word_transient_export(
                powershell.resolve(strict=True),
                exporter_script.resolve(strict=True),
                source_docx,
                bridge,
                export_stage_root,
            )
            engine = "microsoft_word_com"
        if not bridge.is_file() or bridge.stat().st_size < 1:
            raise RenderQaError("transient Word bridge was not created")
        rendered = render_pdf_pages(bridge, output_root, pdftoppm, dpi=dpi, source_kind="docx_candidate", retain_source_identity=False)
    finally:
        try:
            if bridge.exists():
                bridge.unlink()
            shutil.rmtree(private_root)
            cleanup_passed = not bridge.exists() and not private_root.exists()
        finally:
            if not cleanup_passed:
                raise RenderQaError("transient bridge cleanup failed")
    if rendered is None:
        raise RenderQaError("transient render did not complete")
    return {**rendered, "transient_bridge_used": True, "transient_bridge_cleanup": "pass", "export_engine": engine}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    final = sub.add_parser("render-pdf")
    final.add_argument("--input", required=True, type=Path)
    final.add_argument("--output-root", required=True, type=Path)
    final.add_argument("--pdftoppm", required=True, type=Path)
    final.add_argument("--dpi", type=int, default=110)
    args = parser.parse_args()
    try:
        result = render_pdf_pages(args.input, args.output_root, args.pdftoppm, dpi=args.dpi)
    except Exception as error:
        print(json.dumps({"status": "fail", "error": f"{type(error).__name__}: {error}"}, ensure_ascii=False), file=__import__("sys").stderr)
        return 2
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
