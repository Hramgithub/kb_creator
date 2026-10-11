"""Independent PDF-page graphic-domain contracts for guarded DOCX readers.

This module validates reviewed source evidence. It does not infer semantic
absence from an extractor's empty resource list or from a downstream master.
"""

from __future__ import annotations

import json
import hashlib
import io
import os
import re
import shutil
import tempfile
from pathlib import Path
from typing import Any

from .identity import assert_existing_path_components_are_not_reparse, file_identity
from .manifests import sealed, validate_seal


INVENTORY_SCHEMA = "kb_creator.source_graphics_inventory.v1"
REVIEW_SCHEMA = "kb_creator.source_graphics_review.v1"
SHA = re.compile(r"^[0-9A-F]{64}$")
PAINT_KINDS = {"raster", "inline_image", "vector_group", "shading", "pattern",
               "composite_candidate", "mask_dependency", "uninvoked_resource"}
GRAPHIC_CATEGORIES = {"opening_art", "body_scene", "portrait", "map", "handout",
                      "cover", "ornament", "composite"}


class SourceGraphicsError(ValueError):
    pass


def _page_facts(page: Any) -> tuple[dict[str, Any], str, str]:
    box = page.mediabox
    width, height = float(box.width), float(box.height)
    rotation = int(page.get("/Rotate", 0)) % 360
    if width <= 0 or height <= 0 or rotation not in {0, 90, 180, 270}:
        raise SourceGraphicsError("source page has unsupported geometry")
    geometry = {"width_pt": width, "height_pt": height, "rotation": rotation,
                "coordinate_space": "pdf_mediabox_top_left"}
    content = page.get_contents()
    content_data = content.get_data() if content is not None else b""
    resources = page.get("/Resources")
    resource_bytes = io.BytesIO()
    if resources is not None:
        resources.get_object().write_to_stream(resource_bytes)
    return (geometry, hashlib.sha256(content_data).hexdigest().upper(),
            hashlib.sha256(resource_bytes.getvalue()).hexdigest().upper())


def build_inventory(source_pdf: Path, renderer: Path, output_root: Path, *, dpi: int = 200) -> Path:
    """Render every physical page; leave paint discovery explicitly incomplete.

    This producer does not infer graphic absence. Its page PNGs are candidates
    for full-resolution human review, and manual region evidence is mandatory.
    """
    from pypdf import PdfReader, __version__ as pypdf_version
    from .source_page_render import RECIPE, render_source_pdf_page

    source_pdf = source_pdf.resolve(strict=True)
    renderer = renderer.resolve(strict=True)
    output_root = output_root.resolve()
    if (source_pdf.suffix.lower() != ".pdf" or not source_pdf.is_file() or not renderer.is_file()
            or type(dpi) is not int or dpi < 200 or output_root.exists()
            or not output_root.parent.is_dir()):
        raise SourceGraphicsError("source, renderer, DPI, or absent output root is invalid")
    assert_existing_path_components_are_not_reparse(source_pdf)
    assert_existing_path_components_are_not_reparse(renderer)
    reader = PdfReader(str(source_pdf))
    if len(reader.pages) < 1:
        raise SourceGraphicsError("source PDF has no physical pages")
    source_record = {"path": str(source_pdf), **file_identity(source_pdf),
                     "page_count": len(reader.pages)}
    renderer_record = {"path": str(renderer), **file_identity(renderer)}
    stage = Path(tempfile.mkdtemp(prefix=".graphics-", dir=output_root.parent))
    try:
        pages = []
        for number, page in enumerate(reader.pages, 1):
            geometry, content_sha, resource_sha = _page_facts(page)
            name = f"page-{number:04}.png"
            png = stage / name
            render = render_source_pdf_page(source_pdf, number, renderer, dpi, png,
                                            expected_source_sha256=source_record["sha256"],
                                            expected_renderer_sha256=renderer_record["sha256"])
            pages.append({"page": number, "geometry": geometry,
                          "content_sha256": content_sha, "resource_sha256": resource_sha,
                          "render": {"path": name, **file_identity(png), "dpi": dpi,
                                     "pixels": render["pixels"], "source_page": number},
                          "discovery": {"status": "incomplete", "diagnostic_ids": [],
                                        "limits": ["paint operators and nested/inline/vector/composite semantics require manual page review"]}})
        value = sealed(INVENTORY_SCHEMA, {
            "source_pdf": source_record,
            "producer": {"implementation_sha256": file_identity(Path(__file__))["sha256"],
                         "tool_versions": {"pdftoppm": renderer_record, "pypdf": pypdf_version},
                         "render_profile": RECIPE},
            "pages": pages, "paint_occurrences": [],
        }, digest_key="inventory_sha256")
        (stage / "SOURCE_GRAPHICS_INVENTORY.json").write_text(
            json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        os.replace(stage, output_root)
        return output_root / "SOURCE_GRAPHICS_INVENTORY.json"
    except Exception:
        shutil.rmtree(stage, ignore_errors=True)
        raise


def validate_produced_inventory(path: Path, *, source_pdf: Path | None = None) -> dict[str, Any]:
    """Recompute all source-page facts and PNGs, independent of stored rows."""
    from pypdf import PdfReader, __version__ as pypdf_version
    from .source_page_render import RECIPE, render_source_pdf_page

    value = validate_inventory(path, source_pdf=source_pdf)
    producer = value["producer"]
    tools = producer["tool_versions"]
    if (producer["implementation_sha256"] != file_identity(Path(__file__))["sha256"]
            or producer["render_profile"] != RECIPE or set(tools) != {"pdftoppm", "pypdf"}
            or tools["pypdf"] != pypdf_version):
        raise SourceGraphicsError("source inventory producer implementation changed")
    renderer = _exact_renderer(tools["pdftoppm"])
    pdf = Path(value["source_pdf"]["path"])
    reader = PdfReader(str(pdf))
    with tempfile.TemporaryDirectory(prefix="kb-graphics-replay-") as directory:
        for number, (page, row) in enumerate(zip(reader.pages, value["pages"], strict=True), 1):
            geometry, content_sha, resource_sha = _page_facts(page)
            if (row["geometry"] != geometry or row["content_sha256"] != content_sha
                    or row["resource_sha256"] != resource_sha):
                raise SourceGraphicsError("source PDF page facts differ from inventory")
            png = Path(directory) / f"page-{number:04}.png"
            render = render_source_pdf_page(pdf, number, renderer, row["render"]["dpi"], png,
                                            expected_source_sha256=value["source_pdf"]["sha256"],
                                            expected_renderer_sha256=tools["pdftoppm"]["sha256"])
            if (render["sha256"] != row["render"]["sha256"] or
                    render["pixels"] != row["render"]["pixels"]):
                raise SourceGraphicsError("source page PNG differs from reproducible PDF render")
    return value


def _exact_renderer(record: Any) -> Path:
    row = _object(record, {"path", "bytes", "sha256"}, "renderer")
    path = Path(str(row["path"]))
    if not path.is_absolute() or not path.is_file() or path.is_symlink():
        raise SourceGraphicsError("renderer is missing")
    assert_existing_path_components_are_not_reparse(path)
    if file_identity(path) != {"bytes": row["bytes"], "sha256": row["sha256"]}:
        raise SourceGraphicsError("renderer identity changed")
    return path


def _object(value: Any, keys: set[str], label: str) -> dict[str, Any]:
    if not isinstance(value, dict) or set(value) != keys:
        raise SourceGraphicsError(f"{label} has unknown or missing fields")
    return value


def _digest(value: Any, label: str) -> str:
    if not isinstance(value, str) or not SHA.fullmatch(value):
        raise SourceGraphicsError(f"{label} must be uppercase SHA-256")
    return value


def _read(path: Path, schema: str, seal_key: str) -> dict[str, Any]:
    assert_existing_path_components_are_not_reparse(path)
    if not path.is_file() or path.is_symlink():
        raise SourceGraphicsError(f"missing regular {schema} document")
    try:
        value = json.loads(path.read_text(encoding="utf-8-sig"))
        if not isinstance(value, dict):
            raise SourceGraphicsError("sealed document must be an object")
        validate_seal(value, seal_key)
    except (OSError, ValueError, TypeError) as error:
        raise SourceGraphicsError(f"invalid {schema}: {error}") from error
    if value.get("schema") != schema:
        raise SourceGraphicsError(f"unsupported {schema} version")
    return value


def _bound_file(root: Path, record: Any, label: str) -> Path:
    row = _object(record, {"path", "bytes", "sha256"}, label)
    relative = row["path"]
    if not isinstance(relative, str) or not relative or Path(relative).is_absolute() or ".." in Path(relative).parts:
        raise SourceGraphicsError(f"unsafe {label} path")
    path = (root / relative).resolve()
    if not path.is_relative_to(root.resolve()) or not path.is_file() or path.is_symlink():
        raise SourceGraphicsError(f"missing or escaping {label}")
    assert_existing_path_components_are_not_reparse(path)
    if file_identity(path) != {"bytes": row["bytes"], "sha256": _digest(row["sha256"], label)}:
        raise SourceGraphicsError(f"{label} identity mismatch")
    return path


def _source(record: Any, expected_source: Path | None) -> tuple[Path, int]:
    row = _object(record, {"path", "bytes", "sha256", "page_count"}, "source PDF")
    path = Path(str(row["path"]))
    if not path.is_absolute() or not path.is_file() or path.is_symlink():
        raise SourceGraphicsError("source PDF must be an existing absolute regular file")
    assert_existing_path_components_are_not_reparse(path)
    if expected_source is not None and path.resolve() != expected_source.resolve(strict=True):
        raise SourceGraphicsError("source PDF authority mismatch")
    if file_identity(path) != {"bytes": row["bytes"], "sha256": _digest(row["sha256"], "source PDF")}:
        raise SourceGraphicsError("source PDF identity mismatch")
    from pypdf import PdfReader

    try:
        count = len(PdfReader(str(path)).pages)
    except Exception as error:
        raise SourceGraphicsError("source PDF cannot be parsed") from error
    if type(row["page_count"]) is not int or count < 1 or row["page_count"] != count:
        raise SourceGraphicsError("source PDF physical page domain mismatch")
    return path, count


def _bbox(value: Any, label: str) -> None:
    if (not isinstance(value, list) or len(value) != 4 or
            any(type(item) not in {int, float} for item in value) or
            value[0] >= value[2] or value[1] >= value[3]):
        raise SourceGraphicsError(f"invalid {label} region")


def validate_inventory(path: Path, *, source_pdf: Path | None = None) -> dict[str, Any]:
    """Reopen the immutable source and every full-page PNG; no empty-domain shortcut."""
    value = _read(path, INVENTORY_SCHEMA, "inventory_sha256")
    _object(value, {"schema", "source_pdf", "producer", "pages", "paint_occurrences",
                    "inventory_sha256"}, "source graphics inventory")
    _, count = _source(value["source_pdf"], source_pdf)
    producer = _object(value["producer"], {"implementation_sha256", "tool_versions", "render_profile"}, "producer")
    _digest(producer["implementation_sha256"], "producer implementation")
    if not isinstance(producer["tool_versions"], dict) or not isinstance(producer["render_profile"], str) or not producer["render_profile"]:
        raise SourceGraphicsError("producer identity is incomplete")
    pages = value["pages"]
    if not isinstance(pages, list) or len(pages) != count:
        raise SourceGraphicsError("inventory must enumerate every physical PDF page")
    for number, row in enumerate(pages, 1):
        _object(row, {"page", "geometry", "content_sha256", "resource_sha256", "render", "discovery"}, "page inventory")
        if row["page"] != number:
            raise SourceGraphicsError("inventory page order/domain mismatch")
        geometry = _object(row["geometry"], {"width_pt", "height_pt", "rotation", "coordinate_space"}, "page geometry")
        if (any(type(geometry[key]) not in {int, float} or geometry[key] <= 0 for key in ("width_pt", "height_pt"))
                or geometry["rotation"] not in {0, 90, 180, 270} or geometry["coordinate_space"] != "pdf_mediabox_top_left"):
            raise SourceGraphicsError("page geometry is invalid")
        _digest(row["content_sha256"], "page content")
        _digest(row["resource_sha256"], "page resources")
        render = _object(row["render"], {"path", "bytes", "sha256", "dpi", "pixels", "source_page"}, "page render")
        if render["source_page"] != number or type(render["dpi"]) is not int or render["dpi"] < 200:
            raise SourceGraphicsError("full-page source render is missing sufficient resolution")
        image_path = _bound_file(path.parent, {key: render[key] for key in ("path", "bytes", "sha256")}, "page render")
        if image_path.suffix.lower() != ".png":
            raise SourceGraphicsError("source review requires a PNG full-page render")
        from PIL import Image

        with Image.open(image_path) as image:
            if image.format != "PNG" or list(image.size) != render["pixels"]:
                raise SourceGraphicsError("page render dimensions differ from reviewed evidence")
            image.verify()
        discovery = _object(row["discovery"], {"status", "diagnostic_ids", "limits"}, "page discovery")
        if discovery["status"] != "incomplete" or not isinstance(discovery["limits"], list) or not discovery["limits"]:
            raise SourceGraphicsError("raw paint discovery cannot claim exhaustive closure in v1")
        if not isinstance(discovery["diagnostic_ids"], list):
            raise SourceGraphicsError("page discovery diagnostics are malformed")
    occurrences = value["paint_occurrences"]
    if not isinstance(occurrences, list):
        raise SourceGraphicsError("paint occurrences must be a list")
    ids: set[str] = set()
    for row in occurrences:
        _object(row, {"occurrence_id", "page", "kind", "operator_path", "invocation_ordinal",
                      "resource_path", "stream_sha256", "bbox", "discovery_limit"}, "paint occurrence")
        oid = row["occurrence_id"]
        if (not isinstance(oid, str) or not oid or oid in ids or type(row["page"]) is not int
                or not 1 <= row["page"] <= count or row["kind"] not in PAINT_KINDS
                or not isinstance(row["operator_path"], str) or type(row["invocation_ordinal"]) is not int
                or row["invocation_ordinal"] < 0):
            raise SourceGraphicsError("paint occurrence identity/topology is invalid")
        ids.add(oid)
        if row["stream_sha256"] is not None:
            _digest(row["stream_sha256"], "paint stream")
        if row["bbox"] is not None:
            _bbox(row["bbox"], "paint occurrence")
    return value


def validate_review(path: Path, inventory_path: Path, *, source_pdf: Path | None = None) -> dict[str, Any]:
    """Require a reviewed all-page semantic domain and exact per-graphic decisions."""
    inventory = validate_produced_inventory(inventory_path, source_pdf=source_pdf)
    value = _read(path, REVIEW_SCHEMA, "review_sha256")
    _object(value, {"schema", "inventory", "source_pdf", "reviewer", "page_reviews",
                    "graphics", "technical_occurrences", "state", "review_sha256"}, "source graphics review")
    expected_inventory = {"path": str(inventory_path.resolve()), **file_identity(inventory_path)}
    if value["inventory"] != expected_inventory or value["source_pdf"] != inventory["source_pdf"]:
        raise SourceGraphicsError("review has stale inventory or source authority")
    reviewer = _object(value["reviewer"], {"role", "reference", "time_utc"}, "reviewer")
    if any(not isinstance(reviewer[key], str) or not reviewer[key].strip() for key in reviewer):
        raise SourceGraphicsError("review authority is incomplete")
    page_reviews = value["page_reviews"]
    if not isinstance(page_reviews, list) or len(page_reviews) != len(inventory["pages"]):
        raise SourceGraphicsError("every physical page needs source visual review")
    by_page: dict[int, set[str]] = {}
    for number, row in enumerate(page_reviews, 1):
        _object(row, {"page", "render_sha256", "status", "graphic_ids", "residual_issues",
                      "manual_page_coverage"}, "page review")
        if row["page"] != number or row["render_sha256"] != inventory["pages"][number - 1]["render"]["sha256"]:
            raise SourceGraphicsError("page review is missing or bound to a stale render")
        coverage = _object(row["manual_page_coverage"], {"view_sha256", "reviewed", "regions",
                                                         "remaining_limits", "reviewer_reference"}, "manual page coverage")
        if (coverage["view_sha256"] != row["render_sha256"] or coverage["reviewed"] is not True
                or not isinstance(coverage["regions"], list) or not isinstance(coverage["remaining_limits"], str)
                or not isinstance(coverage["reviewer_reference"], str) or not coverage["reviewer_reference"].strip()):
            raise SourceGraphicsError("incomplete discovery requires exact manual page coverage")
        if row["status"] not in {"reviewed_graphics", "reviewed_no_meaningful_graphics"} or row["residual_issues"]:
            raise SourceGraphicsError("source page review is pending or unresolved")
        ids = row["graphic_ids"]
        if (not isinstance(ids, list) or any(not isinstance(oid, str) or not oid for oid in ids)
                or len(ids) != len(set(ids)) or bool(ids) != (row["status"] == "reviewed_graphics")):
            raise SourceGraphicsError("page graphic domain/status mismatch")
        by_page[number] = set(ids)
        region_ids: set[str] = set()
        for region in coverage["regions"]:
            _object(region, {"region_id", "bbox", "graphic_id"}, "manual region")
            _bbox(region["bbox"], "manual")
            if region["region_id"] in region_ids:
                raise SourceGraphicsError("duplicate manual region")
            region_ids.add(region["region_id"])
            if region["graphic_id"] is not None and region["graphic_id"] not in by_page[number]:
                raise SourceGraphicsError("manual region has unknown page graphic")
    graphics = value["graphics"]
    if not isinstance(graphics, list) or {row.get("graphic_id") for row in graphics if isinstance(row, dict)} != set().union(*by_page.values()) or len(graphics) != sum(map(len, by_page.values())):
        raise SourceGraphicsError("review graphic IDs do not close the page domain")
    occurrence_pages = {row["occurrence_id"]: row["page"] for row in inventory["paint_occurrences"]
                        if row["kind"] != "uninvoked_resource"}
    occurrence_ids = set(occurrence_pages)
    bound_occurrences: set[str] = set()
    for row in graphics:
        _object(row, {"graphic_id", "page", "category", "owner", "source_region", "occurrence_ids",
                      "manual_region_id", "disposition", "rationale", "decision_reference", "selected"}, "graphic decision")
        if (type(row["page"]) is not int or row["page"] not in by_page
                or row["graphic_id"] not in by_page[row["page"]] or row["category"] not in GRAPHIC_CATEGORIES
                or row["disposition"] not in {"include", "equivalent_replacement", "exclude"}
                or not isinstance(row["owner"], str) or not row["owner"].strip()
                or any(not isinstance(row[key], str) or not row[key].strip() for key in ("rationale", "decision_reference"))):
            raise SourceGraphicsError("graphic decision is unresolved or lacks owner/authority")
        _bbox(row["source_region"], "graphic")
        if row["manual_region_id"] is not None:
            regions = page_reviews[row["page"] - 1]["manual_page_coverage"]["regions"]
            if not any(region["region_id"] == row["manual_region_id"] and region["graphic_id"] == row["graphic_id"] for region in regions):
                raise SourceGraphicsError("graphic manual region is unbound")
        if not row["occurrence_ids"] and row["manual_region_id"] is None:
            raise SourceGraphicsError("graphic lacks source occurrence or reviewed manual region")
        for oid in row["occurrence_ids"]:
            if oid not in occurrence_ids or oid in bound_occurrences or occurrence_pages[oid] != row["page"]:
                raise SourceGraphicsError("paint occurrence is unknown or reused")
            bound_occurrences.add(oid)
        if row["disposition"] == "exclude":
            if row["selected"] is not None:
                raise SourceGraphicsError("excluded graphic cannot select reader bytes")
        else:
            _bound_file(path.parent, row["selected"], "selected graphic")
    technical = value["technical_occurrences"]
    if not isinstance(technical, list):
        raise SourceGraphicsError("technical occurrence decisions are malformed")
    for row in technical:
        _object(row, {"occurrence_id", "parent_graphic_id", "reason", "decision_reference"}, "technical occurrence")
        if (row["occurrence_id"] not in occurrence_ids or row["occurrence_id"] in bound_occurrences
                or row["parent_graphic_id"] not in {g["graphic_id"] for g in graphics}
                or occurrence_pages[row["occurrence_id"]] != next(g["page"] for g in graphics if g["graphic_id"] == row["parent_graphic_id"])
                or not row["reason"] or not row["decision_reference"]):
            raise SourceGraphicsError("technical paint occurrence lacks reviewed parent")
        bound_occurrences.add(row["occurrence_id"])
    if bound_occurrences != occurrence_ids or value["state"] != "closed":
        raise SourceGraphicsError("paint/page source domain is not closed")
    return value
