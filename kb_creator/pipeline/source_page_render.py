"""Deterministic, source-bound PDF page rendering for reviewed facsimiles.

This module intentionally knows no scenario paths.  Callers must supply all
authorities and persist the returned identity in their own sealed records.
"""
from __future__ import annotations

import hashlib
import math
import os
import re
import shutil
import subprocess
import tempfile
from contextlib import contextmanager
from contextvars import ContextVar
from dataclasses import dataclass
from pathlib import Path
from typing import Any


RECIPE = "pdftoppm-mediabox-single-page-png-v1"
ORIGIN = "source_pdf_page_render_v1"
IMAGE_PLACEHOLDER = re.compile(r"!\[([^\]\r\n]+)\]\(\{\{asset:([^{}]+)\}\}\)")
SHA256 = re.compile(r"^[0-9A-Fa-f]{64}$")


@dataclass(frozen=True)
class _RenderEntry:
    path: Path
    pixels: tuple[int, int]
    byte_count: int
    sha256: str


@dataclass
class _RenderScope:
    root: Path
    entries: dict[tuple[Any, ...], _RenderEntry]


_ACTIVE_RENDER_SCOPE: ContextVar[_RenderScope | None] = ContextVar("source_page_render_scope", default=None)


@contextmanager
def _reuse_rendered_pages():
    """Keep only fresh PNG binaries within one synchronous authority traversal."""
    with tempfile.TemporaryDirectory(prefix="kb-source-render-") as directory:
        token = _ACTIVE_RENDER_SCOPE.set(_RenderScope(Path(directory), {}))
        try:
            yield
        finally:
            _ACTIVE_RENDER_SCOPE.reset(token)


def _sha256(value: Any, label: str) -> str:
    if not isinstance(value, str) or not SHA256.fullmatch(value):
        raise ValueError(f"{label} must be a SHA-256 hex digest")
    return value.upper()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def _page_geometry(source: Path, page: int) -> tuple[float, float, int]:
    from pypdf import PdfReader

    reader = PdfReader(str(source))
    if page < 1 or page > len(reader.pages):
        raise ValueError("source_page is outside the PDF page domain")
    pdf_page = reader.pages[page - 1]
    box = pdf_page.mediabox
    width, height = float(box.width), float(box.height)
    rotation = int(pdf_page.get("/Rotate", 0)) % 360
    if width <= 0 or height <= 0 or rotation not in {0, 90, 180, 270}:
        raise ValueError("source page has unsupported MediaBox or rotation")
    return width, height, rotation


def _png_facts(path: Path, expected_pixels: list[int]) -> _RenderEntry:
    if not path.is_file() or path.stat().st_size <= 0:
        raise ValueError("pdftoppm source-page render failed")
    from PIL import Image
    with Image.open(path) as image:
        if image.format != "PNG":
            raise ValueError("pdftoppm did not produce a PNG")
        pixels = (image.width, image.height)
        image.verify()
    if list(pixels) != expected_pixels:
        raise ValueError("source-page render pixels do not match MediaBox geometry")
    return _RenderEntry(path, pixels, path.stat().st_size, sha256_file(path))


def _copy_verified_render(entry: _RenderEntry, output: Path, expected_pixels: list[int]) -> None:
    try:
        current = _png_facts(entry.path, expected_pixels)
    except (OSError, ValueError) as error:
        raise ValueError("private source-page render payload changed") from error
    if current != entry:
        raise ValueError("private source-page render payload changed")
    temporary: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(prefix=".source-render-", suffix=".png", dir=output.parent, delete=False) as stream:
            temporary = Path(stream.name)
        shutil.copyfile(entry.path, temporary)
        copied = _png_facts(temporary, expected_pixels)
        if (copied.pixels, copied.byte_count, copied.sha256) != (entry.pixels, entry.byte_count, entry.sha256):
            raise ValueError("source-page render copy changed")
        os.replace(temporary, output)
        temporary = None
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


def render_source_pdf_page(
    source: Path,
    source_page: int,
    renderer: Path,
    dpi: int,
    output: Path,
    *,
    expected_source_sha256: str,
    expected_renderer_sha256: str,
) -> dict[str, Any]:
    """Render exactly one full MediaBox page and return sealed binary facts.

    The caller must compare this result with a reviewed decision.  A preview
    remains scratch until a later gate binds the returned identity.
    """
    if type(source_page) is not int or source_page < 1 or type(dpi) is not int or dpi <= 0:
        raise ValueError("source_page and dpi must be positive integers")
    expected_source_sha256 = _sha256(expected_source_sha256, "source SHA-256")
    expected_renderer_sha256 = _sha256(expected_renderer_sha256, "renderer SHA-256")
    if not source.is_file() or not renderer.is_file():
        raise ValueError("source PDF or pdftoppm renderer is missing")
    if sha256_file(source) != expected_source_sha256 or sha256_file(renderer) != expected_renderer_sha256:
        raise ValueError("source or renderer SHA-256 authority mismatch")
    width, height, rotation = _page_geometry(source, source_page)
    output.parent.mkdir(parents=True, exist_ok=True)
    if output.suffix.lower() != ".png":
        raise ValueError("source page render output must be a PNG")
    expected = [math.ceil(width * dpi / 72), math.ceil(height * dpi / 72)]
    if rotation in {90, 270}:
        expected.reverse()
    scope = _ACTIVE_RENDER_SCOPE.get()
    key = ((str(source.resolve()), expected_source_sha256, source_page,
            str(renderer.resolve()), expected_renderer_sha256, dpi, RECIPE, width, height, rotation)
           if scope is not None else None)
    if scope is not None and key in scope.entries:
        if sha256_file(source) != expected_source_sha256 or sha256_file(renderer) != expected_renderer_sha256:
            raise ValueError("source or renderer SHA-256 authority changed before reuse")
        entry = scope.entries[key]
        _copy_verified_render(entry, output, expected)
    else:
        rendered = scope.root / f"render-{len(scope.entries):06d}.png" if scope is not None else output
        stem = rendered.with_suffix("")
        command = [str(renderer), "-f", str(source_page), "-l", str(source_page), "-singlefile", "-r", str(dpi), "-png", str(source), str(stem)]
        completed = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
        if completed.returncode != 0:
            raise ValueError("pdftoppm source-page render failed")
        entry = _png_facts(rendered, expected)
        if scope is not None:
            if sha256_file(source) != expected_source_sha256 or sha256_file(renderer) != expected_renderer_sha256:
                raise ValueError("source or renderer SHA-256 authority changed during render")
            _copy_verified_render(entry, output, expected)
            scope.entries[key] = entry
    return {"recipe": RECIPE, "dpi": dpi, "renderer_sha256": expected_renderer_sha256, "pixels": list(entry.pixels), "bytes": entry.byte_count, "sha256": entry.sha256, "source_sha256": expected_source_sha256, "source_page": source_page, "rotation": rotation}


def validate_source_page_render_row(
    row: Any,
    *,
    decision_page: int,
    expected_source_sha256: str,
    expected_renderer_sha256: str,
    markdown: str,
    page_visual_reviewed: bool,
) -> dict[str, Any]:
    """Validate the graphic review independently of the page text review.

    The asset has its own source/page/renderer identity and visual decision.
    Retaining it must not promote an unfinished reconstruction to reviewed text.
    Strict authoring still requires reviewed pages at its own ingress gate.
    """
    expected = {"origin", "source_page", "source_sha256", "logical_name", "placement", "render", "source_visual_review"}
    if not isinstance(row, dict) or set(row) != expected or row["origin"] != ORIGIN:
        raise ValueError("source-page render row has an unsupported shape")
    render = row["render"]
    review = row["source_visual_review"]
    expected_source_sha256 = _sha256(expected_source_sha256, "source SHA-256")
    expected_renderer_sha256 = _sha256(expected_renderer_sha256, "renderer SHA-256")
    if (row["source_page"] != decision_page or _sha256(row["source_sha256"], "row source SHA-256") != expected_source_sha256
            or row["placement"] != "full_page" or not isinstance(row["logical_name"], str)
            or not row["logical_name"].endswith(".png") or "/" in row["logical_name"] or "\\" in row["logical_name"]):
        raise ValueError("source-page render row does not bind the reviewed source page")
    if not isinstance(render, dict) or set(render) != {"recipe", "dpi", "renderer_sha256", "pixels", "bytes", "sha256"}:
        raise ValueError("source-page render facts have an unsupported shape")
    if (render["recipe"] != RECIPE or type(render["dpi"]) is not int or render["dpi"] <= 0
            or _sha256(render["renderer_sha256"], "row renderer SHA-256") != expected_renderer_sha256
            or not isinstance(render["pixels"], list) or len(render["pixels"]) != 2
            or any(type(value) is not int or value <= 0 for value in render["pixels"])
            or type(render["bytes"]) is not int or render["bytes"] <= 0
            or not isinstance(render["sha256"], str) or not SHA256.fullmatch(render["sha256"])):
        raise ValueError("source-page render facts are invalid")
    if (not isinstance(review, dict) or set(review) != {"visual_reviewed", "rationale"}
            or review["visual_reviewed"] is not True or not isinstance(review["rationale"], str)
            or not review["rationale"].strip() or type(page_visual_reviewed) is not bool):
        raise ValueError("source-page render lacks closed visual review")
    placeholder = "{{asset:" + row["logical_name"] + "}}"
    matches = [match for match in IMAGE_PLACEHOLDER.finditer(markdown) if match.group(2) == row["logical_name"]]
    if len(matches) != 1 or markdown.count(placeholder) != 1:
        raise ValueError("source-page render needs an exact nonempty Markdown image placeholder")
    return row


def replay_source_render_context(run_root: Path, geometry: dict[str, Any]) -> dict[str, Any]:
    """Extract only the already sealed local source and Stage04 renderer facts."""
    import json
    run = json.loads((run_root / "run.json").read_text(encoding="utf-8"))
    source = Path(str(run.get("local", {}).get("source_path", "")))
    renderer = Path(str(run.get("local", {}).get("common_paths", {}).get("pdftoppm", "")))
    source_id = run.get("source", {})
    renderer_id = geometry.get("renderer", {}) if isinstance(geometry, dict) else {}
    source_sha = _sha256(source_id.get("sha256") if isinstance(source_id, dict) else None, "run source SHA-256")
    renderer_sha = _sha256(renderer_id.get("sha256") if isinstance(renderer_id, dict) else None, "geometry renderer SHA-256")
    if (not source.is_file() or not renderer.is_file() or not isinstance(source_id, dict)
            or not isinstance(renderer_id, dict)
            or sha256_file(source) != source_sha or sha256_file(renderer) != renderer_sha):
        raise ValueError("fresh replay source or Stage04 renderer authority mismatch")
    return {"source": source, "renderer": renderer, "source_sha256": source_sha, "renderer_sha256": renderer_sha}
