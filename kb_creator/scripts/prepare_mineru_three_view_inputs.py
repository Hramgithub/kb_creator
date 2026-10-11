"""Prepare deterministic vector and image-only PDF views for MinerU comparison."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import shutil
import sys
import tempfile
from io import BytesIO
from pathlib import Path
from typing import Any


LETTER = (612.0, 792.0)  # retained only as the historic default test geometry
SOURCE_DISPLAYED_MEDIABOX_POLICY = "source_displayed_mediabox_v1"
LEGACY_PIXEL_GRID_POLICY = "legacy_pixel_grid_v1"


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def file_record(path: Path) -> dict[str, Any]:
    return {"name": path.name, "bytes": path.stat().st_size, "sha256": sha256_file(path)}


def parse_pages(value: str, page_count: int) -> list[int]:
    pages: list[int] = []
    for item in value.split(","):
        item = item.strip()
        if not item:
            continue
        if "-" in item:
            first_text, last_text = item.split("-", 1)
            first, last = int(first_text), int(last_text)
            if last < first:
                raise ValueError(f"descending page range: {item}")
            pages.extend(range(first, last + 1))
        else:
            pages.append(int(item))
    if not pages or len(pages) != len(set(pages)):
        raise ValueError("pages must be nonempty and unique")
    if any(page < 1 or page > page_count for page in pages):
        raise ValueError(f"pages must be inside 1..{page_count}")
    return pages


def _pdf_dependencies() -> tuple[Any, Any, Any, Any]:
    try:
        import fitz  # PyMuPDF
        from pypdf import PdfReader, PdfWriter
        from reportlab.lib.utils import ImageReader
        from reportlab.pdfgen import canvas
    except ImportError as exc:  # pragma: no cover - dependency error is host-specific
        raise RuntimeError("requires PyMuPDF, pypdf and reportlab") from exc
    return fitz, PdfReader, PdfWriter, (ImageReader, canvas)


def _assert_empty_or_matching_resume(output_dir: Path, *, resume: bool, expected: dict[str, Any], raster_only: bool) -> None:
    if not output_dir.exists():
        return
    contents = list(output_dir.iterdir())
    if not contents:
        return
    manifest = output_dir / "sample_pages.json"
    if not resume or not manifest.is_file():
        raise FileExistsError(f"refusing non-empty output directory: {output_dir}")
    observed = json.loads(manifest.read_text(encoding="utf-8"))
    if observed.get("mode") != expected["mode"]:
        raise ValueError("resume outputs do not match the selected preparation mode")
    for key in ("source", "ordered_pages", "render"):
        if observed.get(key) != expected[key]:
            raise ValueError("resume manifest does not prove the same owned input run")
    expected_output_keys = {"raster_pdf"} if raster_only else {"vector_pdf", "raster_pdf"}
    if set(observed.get("outputs", {})) != expected_output_keys:
        raise ValueError("resume outputs do not match the selected preparation mode")
    for key in sorted(expected_output_keys):
        record = observed.get("outputs", {}).get(key)
        if not isinstance(record, dict):
            raise ValueError("resume manifest lacks an output record")
        path = output_dir / record.get("name", "")
        if not path.is_file() or file_record(path) != record:
            raise ValueError("resume output identity does not match manifest")


def _write_vector(source: Path, pages: list[int], destination: Path, PdfReader: Any, PdfWriter: Any) -> None:
    reader = PdfReader(str(source))
    writer = PdfWriter()
    for source_page in pages:
        writer.add_page(reader.pages[source_page - 1])
    writer.add_metadata({"/Creator": "kb_creator MinerU three-view input preparer", "/Producer": "pypdf"})
    with destination.open("wb") as stream:
        writer.write(stream)


def _write_raster(
    source: Path,
    pages: list[int],
    destination: Path,
    dpi: int,
    fitz: Any,
    ImageReader: Any,
    canvas: Any,
    expected_pixels: list[list[int]],
    displayed_sizes: list[list[float]],
    geometry_policy: str,
) -> None:
    document = fitz.open(source)
    try:
        result = canvas.Canvas(str(destination), pagesize=LETTER, pageCompression=1, invariant=1)
        result.setCreator("kb_creator MinerU three-view input preparer")
        result.setTitle("Image-only MinerU input")
        scale = dpi / 72.0
        for index, source_page in enumerate(pages):
            page = document.load_page(source_page - 1)
            # PyMuPDF otherwise renders the CropBox.  Reconstruction authority is
            # the full MediaBox; changing the in-memory crop never writes source.
            original_crop = page.cropbox
            try:
                try:
                    page.set_cropbox(page.mediabox)
                except ValueError:
                    if geometry_policy != SOURCE_DISPLAYED_MEDIABOX_POLICY:
                        raise
                    # PyMuPDF rejects an otherwise valid full-page CropBox for
                    # some non-zero-origin MediaBoxes. Resetting the MediaBox
                    # on the in-memory page removes subordinate page boxes and
                    # leaves the source file untouched.
                    page.set_mediabox(page.mediabox)
                pixmap = page.get_pixmap(matrix=fitz.Matrix(scale, scale), alpha=False)
            finally:
                try:
                    page.set_cropbox(original_crop)
                except ValueError:
                    pass
            png = pixmap.tobytes("png")
            if [pixmap.width, pixmap.height] != expected_pixels[index]:
                raise ValueError(
                    "raster dimensions do not match transformed full MediaBox"
                )
            # drawImage is the only page content: no text operators/text layer are emitted.
            if geometry_policy == SOURCE_DISPLAYED_MEDIABOX_POLICY:
                # The samples are embedded unchanged.  Their physical extent is
                # the source-displayed MediaBox, never the rounded sample grid.
                width, height = displayed_sizes[index]
            else:
                width, height = pixmap.width * 72.0 / dpi, pixmap.height * 72.0 / dpi
            result.setPageSize((width, height))
            result.drawImage(ImageReader(BytesIO(png)), 0, 0, width=width, height=height)
            result.showPage()
        result.save()
    finally:
        document.close()


def _verify_raster_pdf(
    path: Path,
    page_geometry: list[dict[str, Any]],
    PdfReader: Any,
) -> list[dict[str, Any]]:
    """Re-open the derivative and prove its canvas and image-only topology."""
    reader = PdfReader(str(path))
    if len(reader.pages) != len(page_geometry):
        raise ValueError("raster PDF page count mismatch")
    verified: list[dict[str, Any]] = []
    for index, (page, expected) in enumerate(zip(reader.pages, page_geometry), start=1):
        media = [float(page.mediabox.left), float(page.mediabox.bottom), float(page.mediabox.right), float(page.mediabox.top)]
        crop = [float(page.cropbox.left), float(page.cropbox.bottom), float(page.cropbox.right), float(page.cropbox.top)]
        width, height = float(page.mediabox.width), float(page.mediabox.height)
        raw_rotation = float(page.get("/Rotate", 0))
        if not math.isfinite(raw_rotation) or not raw_rotation.is_integer():
            raise ValueError("source rotation must be an integer right angle")
        rotation = int(raw_rotation) % 360
        user_unit = float(page.get("/UserUnit", 1))
        resources = page.get("/Resources") or {}
        xobjects = resources.get("/XObject") or {}
        images = []
        for name, reference in xobjects.items():
            obj = reference.get_object()
            if obj.get("/Subtype") == "/Image":
                images.append({"name": str(name), "pixel_dimensions": [int(obj["/Width"]), int(obj["/Height"])]})
        target = expected["raster_pdf_page_size_points"]
        if (
            rotation != 0
            or user_unit != 1.0
            or crop != media
            or [width, height] != target
            or len(images) != 1
            or images[0]["pixel_dimensions"] != expected["raster_pixel_dimensions"]
            or page.extract_text().strip()
        ):
            raise ValueError(f"raster PDF page {index} failed exact image-only geometry verification")
        verified.append({
            "sample_page": index,
            "media_box_coordinates": media,
            "crop_box_coordinates": crop,
            "displayed_page_size_points": [width, height],
            "rotation_degrees": rotation,
            "user_unit": user_unit,
            "image_count": 1,
            "image_pixel_dimensions": images[0]["pixel_dimensions"],
            "has_text_layer": False,
        })
    return verified


def prepare_inputs(source: Path, output_dir: Path, expected_sha256: str, pages_text: str, dpi: int, basename: str, *, resume: bool = False, raster_only: bool = False, geometry_policy: str = LEGACY_PIXEL_GRID_POLICY) -> dict[str, Any]:
    if not source.is_file():
        raise FileNotFoundError(source)
    if dpi <= 0:
        raise ValueError("dpi must be positive")
    if not basename or any(character in basename for character in "\\/:*?\"<>|"):
        raise ValueError("basename must be a safe filename stem")
    if geometry_policy not in {LEGACY_PIXEL_GRID_POLICY, SOURCE_DISPLAYED_MEDIABOX_POLICY}:
        raise ValueError("unsupported raster geometry policy")
    fitz, PdfReader, PdfWriter, reportlab = _pdf_dependencies()
    ImageReader, canvas = reportlab
    source_record = file_record(source)
    if source_record["sha256"] != expected_sha256.upper():
        raise ValueError("source SHA-256 mismatch")
    reader = PdfReader(str(source))
    page_count = len(reader.pages)
    pages = parse_pages(pages_text, page_count)
    geometry = None
    page_geometry = []
    for source_page in pages:
        page = reader.pages[source_page - 1]
        box = page.mediabox
        crop = page.cropbox
        coordinates = tuple(float(value) for value in (box.left, box.bottom, box.right, box.top))
        crop_coordinates = tuple(float(value) for value in (crop.left, crop.bottom, crop.right, crop.top))
        dimensions = (coordinates[2] - coordinates[0], coordinates[3] - coordinates[1])
        raw_rotation = float(page.get("/Rotate", 0))
        if not math.isfinite(raw_rotation) or not raw_rotation.is_integer():
            raise ValueError("source rotation must be an integer right angle")
        rotation = int(raw_rotation) % 360
        user_unit = float(page.get("/UserUnit", 1))
        if geometry_policy == SOURCE_DISPLAYED_MEDIABOX_POLICY:
            if not all(math.isfinite(value) for value in (*coordinates, *crop_coordinates, *dimensions, user_unit)) or any(value <= 0 for value in dimensions):
                raise ValueError("source MediaBox geometry must be finite and positive")
            if rotation not in (0, 90, 180, 270):
                raise ValueError("source rotation must be a right angle")
            if user_unit != 1.0:
                raise ValueError("source_displayed_mediabox_v1 requires UserUnit 1")
        if crop_coordinates[2] <= crop_coordinates[0] or crop_coordinates[3] <= crop_coordinates[1] or crop_coordinates[0] < coordinates[0] or crop_coordinates[1] < coordinates[1] or crop_coordinates[2] > coordinates[2] or crop_coordinates[3] > coordinates[3]:
            raise ValueError("source CropBox is invalid or escapes MediaBox")
        observed = (dimensions, rotation)
        if geometry is None:
            geometry = observed
        displayed = dimensions if rotation in (0, 180) else (dimensions[1], dimensions[0])
        page_record = {
            "source_page": source_page,
            "media_box_coordinates": list(coordinates),
            "crop_box_coordinates": list(crop_coordinates),
            "displayed_page_size_points": list(displayed),
            "raster_pixel_dimensions": [
                math.ceil(displayed[0] * dpi / 72.0),
                math.ceil(displayed[1] * dpi / 72.0),
            ],
        }
        if geometry_policy == SOURCE_DISPLAYED_MEDIABOX_POLICY:
            page_record.update({
                "source_rotation_degrees": rotation,
                "source_user_unit": user_unit,
                "raster_pdf_page_size_points": list(displayed),
                "raster_pdf_rotation_degrees": 0,
                "raster_pdf_user_unit": 1.0,
            })
        page_geometry.append(page_record)
    authority_keys = ("media_box_coordinates", "crop_box_coordinates", "source_rotation_degrees", "source_user_unit")
    mixed_geometry = any(tuple(row.get(key) for key in authority_keys) != tuple(page_geometry[0].get(key) for key in authority_keys) for row in page_geometry[1:])
    if mixed_geometry and geometry_policy != SOURCE_DISPLAYED_MEDIABOX_POLICY:
        raise ValueError("mixed geometry requires source_displayed_mediabox_v1")
    expected = {
        "mode": "raster_only" if raster_only else "vector_and_raster",
        "source": {**source_record, "page_count": page_count, "path_name": source.name},
        "ordered_pages": [{"sample_page": index, "source_page": page} for index, page in enumerate(pages, start=1)],
        "render": {
            "dpi": dpi,
            "source_box": "MediaBox",
            "raster_has_text_layer": False,
            "page_geometry": page_geometry,
        },
    }
    if not mixed_geometry:
        expected["render"].update(page_size_points=list(geometry[0]), rotation_degrees=geometry[1])
    if geometry_policy == SOURCE_DISPLAYED_MEDIABOX_POLICY:
        expected["render"] = {"geometry_policy": geometry_policy, **expected["render"]}
    _assert_empty_or_matching_resume(output_dir, resume=resume, expected=expected, raster_only=raster_only)
    if output_dir.exists() and any(output_dir.iterdir()):
        return json.loads((output_dir / "sample_pages.json").read_text(encoding="utf-8"))
    output_dir.parent.mkdir(parents=True, exist_ok=True)
    stage = Path(tempfile.mkdtemp(prefix=f".{output_dir.name}.stage-", dir=output_dir.parent))
    try:
        raster = stage / f"{basename}_raster.pdf"
        outputs = {"raster_pdf": raster}
        if not raster_only:
            vector = stage / f"{basename}_vector.pdf"
            _write_vector(source, pages, vector, PdfReader, PdfWriter)
            outputs = {"vector_pdf": vector, **outputs}
        _write_raster(
            source,
            pages,
            raster,
            dpi,
            fitz,
            ImageReader,
            canvas,
            [row["raster_pixel_dimensions"] for row in page_geometry],
            [row["displayed_page_size_points"] for row in page_geometry],
            geometry_policy,
        )
        verification = _verify_raster_pdf(raster, page_geometry, PdfReader) if geometry_policy == SOURCE_DISPLAYED_MEDIABOX_POLICY else None
        manifest = {
            "schema": "kb_creator.mineru_three_view_inputs.v3" if geometry_policy == SOURCE_DISPLAYED_MEDIABOX_POLICY and mixed_geometry else "kb_creator.mineru_three_view_inputs.v2" if geometry_policy == SOURCE_DISPLAYED_MEDIABOX_POLICY else "kb_creator.mineru_three_view_inputs.v1",
            **expected,
            "outputs": {key: file_record(path) for key, path in outputs.items()},
            **({"raster_pdf_verification": verification} if geometry_policy == SOURCE_DISPLAYED_MEDIABOX_POLICY else {}),
            "tool_versions": {
                "python": sys.version.split()[0],
                "pypdf": getattr(__import__("pypdf"), "__version__", "unknown"),
                "pymupdf": getattr(fitz, "__version__", getattr(fitz, "VersionBind", "unknown")),
                "reportlab": getattr(__import__("reportlab"), "Version", "unknown"),
            },
        }
        (stage / "sample_pages.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        if output_dir.exists():
            output_dir.rmdir()
        os.replace(stage, output_dir)
        return manifest
    except Exception:
        shutil.rmtree(stage, ignore_errors=True)
        raise


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", required=True, type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument("--source-sha256", required=True)
    parser.add_argument("--pages", required=True, help="one-based pages, for example 5,12,53 or 1-10")
    parser.add_argument("--dpi", type=int, default=200)
    parser.add_argument("--basename", default="sample")
    parser.add_argument("--resume", action="store_true")
    parser.add_argument("--raster-only", action="store_true", help="write only the image-only PDF; original MinerU views use the retained source directly")
    parser.add_argument("--geometry-policy", choices=(LEGACY_PIXEL_GRID_POLICY, SOURCE_DISPLAYED_MEDIABOX_POLICY), default=LEGACY_PIXEL_GRID_POLICY)
    args = parser.parse_args()
    manifest = prepare_inputs(args.source.resolve(), args.output_dir.resolve(), args.source_sha256, args.pages, args.dpi, args.basename, resume=args.resume, raster_only=args.raster_only, geometry_policy=args.geometry_policy)
    print(json.dumps({"status": "ok", "manifest": str(args.output_dir / "sample_pages.json"), "outputs": manifest["outputs"]}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
