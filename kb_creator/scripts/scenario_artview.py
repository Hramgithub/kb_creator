#!/usr/bin/env python3
"""Build and validate a portable, hash-bound scenario art review bundle."""

from __future__ import annotations

import argparse
import copy
import hashlib
import io
import json
import math
import os
import platform
import re
import shutil
import stat
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

import PIL
from PIL import Image, ImageOps


REPO_ROOT = Path(__file__).resolve().parents[2]
CANDIDATE_SCHEMA = "kb_creator.scenario_artview_candidate.v2"
DECISION_SCHEMA = "kb_creator.scenario_artview_decisions.v2"
PROFILE_SCHEMA_V3 = "kb_creator.scenario_artview_profile.v3"
CANDIDATE_SCHEMA_V3 = "kb_creator.scenario_artview_candidate.v3"
DECISION_SCHEMA_V3 = "kb_creator.scenario_artview_decisions.v3"
PROFILE_SCHEMA_V4 = "kb_creator.scenario_artview_profile.v4"
CANDIDATE_SCHEMA_V4 = "kb_creator.scenario_artview_candidate.v4"
DECISION_SCHEMA_V4 = "kb_creator.scenario_artview_decisions.v4"
V3_SAFE_PATH_PATTERN = (
    r"^(?!\s)(?!.*\s$)(?!/)(?!.*//)(?!.*(?:^|/)\.\.?(?:/|$))"
    r"(?!.*[:\\\x00-\x1F])"
    r"(?!.*(?:^|/)(?:[cC][oO][nN]|[pP][rR][nN]|[aA][uU][xX]|[nN][uU][lL]|"
    r"[cC][oO][mM][1-9]|[lL][pP][tT][1-9])(?:\.|/|$))"
    r"(?!.*[ .](?:/|$))[^/]+(?:/[^/]+)*$"
)
V3_SAFE_PATH_RE = re.compile(V3_SAFE_PATH_PATTERN)
BINARY_DECISIONS = (
    "keep_current",
    "use_candidate",
    "exclude",
    "needs_manual_work",
    "reopen_masters",
)
PRESENTATION_ALIGNMENTS = ("left", "center", "right")


def read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"Expected JSON object: {path}")
    return value


def canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + "\n", encoding="utf-8", newline="\n")


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest().upper()


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest().upper()


def file_record(path: Path, repo_path: str | None = None) -> dict[str, Any]:
    return {
        "path": repo_path or path.name,
        "bytes": path.stat().st_size,
        "sha256": sha256_file(path),
    }


def repo_path(path: Path) -> str:
    return path.resolve().relative_to(REPO_ROOT).as_posix()


def resolve_repo(value: str) -> Path:
    path = Path(value.replace("/", os.sep))
    resolved = path.resolve() if path.is_absolute() else (REPO_ROOT / path).resolve()
    return resolved


def require_file(path: Path, label: str) -> None:
    if not path.is_file():
        raise FileNotFoundError(f"Missing {label}: {path}")


def safe_relative(value: str) -> str:
    normalized = value.replace("\\", "/")
    if not normalized or normalized.startswith(("/", "//")) or re.match(r"^[A-Za-z]:", normalized):
        raise ValueError(f"Absolute path is forbidden in bundle: {value}")
    if "://" in normalized or any(part == ".." for part in normalized.split("/")):
        raise ValueError(f"Unsafe bundle path: {value}")
    return normalized


def image_record(path: Path, relative: str) -> dict[str, Any]:
    with Image.open(path) as image:
        image.load()
        width, height = image.size
        mode = image.mode
        media = Image.MIME.get(image.format or "") or (
            "image/jpeg" if path.suffix.casefold() in {".jpg", ".jpeg"} else "image/png"
        )
    return {
        **file_record(path, safe_relative(relative)),
        "dimensions": {"width": width, "height": height},
        "media_type": media,
        "colorspace": mode,
    }


def copy_cached_image(
    previous_root: Path | None,
    candidate_root: Path,
    record: Any,
    expected_relative: str,
) -> dict[str, Any] | None:
    """Copy a prior deterministic render only after validating its recorded identity."""
    if previous_root is None or not isinstance(record, dict):
        return None
    relative = safe_relative(expected_relative)
    if record.get("path") != relative:
        return None
    source = previous_root / relative.replace("/", os.sep)
    if not source.is_file():
        return None
    if source.stat().st_size != int(record.get("bytes") or -1):
        return None
    if sha256_file(source) != str(record.get("sha256") or "").upper():
        return None
    target = candidate_root / relative.replace("/", os.sep)
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(source, target)
    copied = image_record(target, relative)
    for key in ("dimensions", "media_type", "colorspace"):
        if record.get(key) != copied.get(key):
            target.unlink(missing_ok=True)
            return None
    return copied


def inventory(root: Path) -> tuple[dict[str, Any], str]:
    rows: list[dict[str, Any]] = []
    lines: list[str] = []
    for path in sorted((p for p in root.rglob("*") if p.is_file()), key=lambda p: p.relative_to(root).as_posix()):
        rel = path.relative_to(root).as_posix()
        digest = sha256_file(path)
        size = path.stat().st_size
        rows.append({"path": rel, "bytes": size, "sha256": digest})
        lines.append(f"{rel}\t{size}\t{digest}\n")
    identity = sha256_bytes("".join(lines).encode("utf-8"))
    return {"algorithm": "sorted relative_path<TAB>bytes<TAB>UPPER_SHA256<LF>", "files": rows, "sha256": identity}, identity


def find_pdftoppm(explicit: str | None) -> Path:
    candidates: list[Path] = []
    if explicit:
        candidates.append(Path(explicit))
    found = shutil.which("pdftoppm")
    if found:
        candidates.append(Path(found))
    runtime_root = Path.home() / ".cache" / "codex-runtimes"
    candidates.extend(runtime_root.glob("**/native/poppler/Library/bin/pdftoppm.exe"))
    for candidate in candidates:
        if candidate.is_file():
            return candidate.resolve()
    raise FileNotFoundError("pdftoppm was not found; pass --pdftoppm")


def poppler_version(executable: Path) -> str:
    result = subprocess.run([str(executable), "-v"], capture_output=True, text=True, check=False)
    text = (result.stderr or result.stdout).strip().splitlines()
    return text[0] if text else "unknown"


def render_page(executable: Path, pdf: Path, page: int, dpi: int, fmt: str, temp_root: Path) -> Path:
    target = temp_root / f"page-{page:03d}-{dpi}dpi"
    args = [
        str(executable), "-f", str(page), "-l", str(page), "-singlefile", "-r", str(dpi),
        f"-{fmt}", str(pdf), str(target),
    ]
    result = subprocess.run(args, capture_output=True, text=True, check=False)
    suffix = ".jpg" if fmt == "jpeg" else ".png"
    output = target.with_suffix(suffix)
    if result.returncode or not output.is_file():
        raise RuntimeError(f"pdftoppm failed for page {page}: {result.stderr.strip()}")
    return output


def normalize_context(source: Path, target: Path) -> None:
    target.parent.mkdir(parents=True, exist_ok=True)
    with Image.open(source) as image:
        rgb = image.convert("RGB")
        rgb.save(target, "JPEG", quality=85, subsampling=1, optimize=False, progressive=False)


def normalize_png(source: Path, target: Path) -> None:
    target.parent.mkdir(parents=True, exist_ok=True)
    with Image.open(source) as image:
        image.save(target, "PNG", optimize=False)


def bbox_iou(left: list[float], right: list[float]) -> float:
    x0 = max(left[0], right[0])
    y0 = max(left[1], right[1])
    x1 = min(left[2], right[2])
    y1 = min(left[3], right[3])
    intersection = max(0.0, x1 - x0) * max(0.0, y1 - y0)
    left_area = max(0.0, left[2] - left[0]) * max(0.0, left[3] - left[1])
    right_area = max(0.0, right[2] - right[0]) * max(0.0, right[3] - right[1])
    union = left_area + right_area - intersection
    return intersection / union if union else 0.0


def overlap_ratio(left: list[float], right: list[float]) -> float:
    x0 = max(left[0], right[0])
    y0 = max(left[1], right[1])
    x1 = min(left[2], right[2])
    y1 = min(left[3], right[3])
    intersection = max(0.0, x1 - x0) * max(0.0, y1 - y0)
    area = max(0.0, left[2] - left[0]) * max(0.0, left[3] - left[1])
    return intersection / area if area else 0.0


def rect_area(rect: list[float]) -> float:
    return max(0.0, rect[2] - rect[0]) * max(0.0, rect[3] - rect[1])


def select_direct_occurrence(
    occurrences: list[dict[str, Any]],
    target: list[float],
    page_width: float,
    page_height: float,
) -> tuple[dict[str, Any] | None, str | None, float, list[float], list[str]]:
    """Select an exact image occurrence or a bounded container around the region.

    A tight container normally reflects harmless bbox drift. A wider container
    can be a genuinely fuller source artwork (for example a banner around a
    portrait), so it is allowed only below a strict page-coverage ceiling and is
    exposed with a stronger review warning. Page-sized backgrounds remain a
    separate candidate class and never pass this selector.
    """
    exact: list[tuple[dict[str, Any], float, list[float], float]] = []
    containers: list[tuple[dict[str, Any], float, list[float], float]] = []
    fuller: list[tuple[dict[str, Any], float, list[float], float]] = []
    target_area = rect_area(target)
    page_area = page_width * page_height
    for occurrence in occurrences:
        rect = [
            float(occurrence["x0"]),
            float(occurrence["top"]),
            float(occurrence["x1"]),
            float(occurrence["bottom"]),
        ]
        iou = bbox_iou(target, rect)
        normalized = [
            rect[0] * 1000 / page_width,
            rect[1] * 1000 / page_height,
            rect[2] * 1000 / page_width,
            rect[3] * 1000 / page_height,
        ]
        edge_delta = [abs(normalized[index] - target[index] * 1000 / (page_width if index % 2 == 0 else page_height)) for index in range(4)]
        area_ratio = rect_area(rect) / target_area if target_area else float("inf")
        if iou >= 0.90 and max(edge_delta) <= 10:
            exact.append((occurrence, iou, edge_delta, area_ratio))
        elif overlap_ratio(target, rect) >= 0.98:
            if 1.0 <= area_ratio <= 1.60:
                containers.append((occurrence, iou, edge_delta, area_ratio))
            elif 1.60 < area_ratio <= 2.25 and rect_area(rect) / page_area <= 0.75:
                fuller.append((occurrence, iou, edge_delta, area_ratio))
    if len(exact) == 1:
        occurrence, iou, edge_delta, _ = exact[0]
        return occurrence, "exact_region", iou, edge_delta, []
    if len(exact) > 1:
        return None, None, 0.0, [], ["direct_ambiguous_occurrence"]
    if containers:
        containers.sort(key=lambda item: (item[3], max(item[2]), -item[1]))
        if len(containers) > 1 and abs(containers[0][3] - containers[1][3]) < 0.02:
            return None, None, 0.0, [], ["direct_ambiguous_containing_occurrence"]
        occurrence, iou, edge_delta, _ = containers[0]
        return occurrence, "containing_region", iou, edge_delta, ["direct_containing_region_review_required"]
    fuller.sort(key=lambda item: (item[3], max(item[2]), -item[1]))
    if not fuller:
        return None, None, 0.0, [], ["direct_no_unique_occurrence"]
    if len(fuller) > 1 and abs(fuller[0][3] - fuller[1][3]) < 0.05:
        return None, None, 0.0, [], ["direct_ambiguous_fuller_occurrence"]
    occurrence, iou, edge_delta, _ = fuller[0]
    return occurrence, "containing_fuller_art", iou, edge_delta, ["direct_fuller_art_review_required"]


def pdf_value(value: Any) -> Any:
    if isinstance(value, (list, tuple)):
        return [pdf_value(item) for item in value]
    text = str(value)
    # pdfminer names stringify as /'Image', while pypdf uses /Image.
    return text.lstrip("/").strip("'\"")


def occurrence_rect(occurrence: dict[str, Any]) -> list[float]:
    return [
        float(occurrence["x0"]),
        float(occurrence["top"]),
        float(occurrence["x1"]),
        float(occurrence["bottom"]),
    ]


def rect_intersection(left: list[float], right: list[float]) -> list[float]:
    return [
        max(left[0], right[0]),
        max(left[1], right[1]),
        min(left[2], right[2]),
        min(left[3], right[3]),
    ]


def rect_union_area(rects: list[list[float]]) -> float:
    """Return the exact union area of a small set of axis-aligned rectangles."""
    usable = [rect for rect in rects if rect_area(rect) > 0]
    if not usable:
        return 0.0
    xs = sorted({value for rect in usable for value in (rect[0], rect[2])})
    total = 0.0
    for left, right in zip(xs, xs[1:]):
        if right <= left:
            continue
        intervals = sorted(
            (rect[1], rect[3])
            for rect in usable
            if rect[0] < right and rect[2] > left
        )
        if not intervals:
            continue
        covered = 0.0
        start, end = intervals[0]
        for next_start, next_end in intervals[1:]:
            if next_start <= end:
                end = max(end, next_end)
            else:
                covered += end - start
                start, end = next_start, next_end
        covered += end - start
        total += (right - left) * covered
    return total


def display_image_from_pdf_dct(decoded: Image.Image) -> tuple[Image.Image, str]:
    if decoded.mode == "CMYK":
        normalized = Image.merge("CMYK", [ImageOps.invert(channel) for channel in decoded.split()])
        return normalized.convert("RGB"), "Pillow invert PDF CMYK samples + convert RGB"
    if decoded.mode == "RGB":
        return decoded.copy(), "none; raw RGB samples"
    return decoded.convert("RGB"), f"Pillow convert {decoded.mode} to RGB"


def validate_dct_occurrence(
    occurrence: dict[str, Any],
    pypdf_reader: Any,
) -> tuple[dict[str, Any] | None, list[str]]:
    """Validate one PDF image stream and decode its optional soft mask."""
    stream = occurrence.get("stream")
    attrs = getattr(stream, "attrs", {}) or {}
    filters = pdf_value(attrs.get("Filter"))
    filters = filters if isinstance(filters, list) else [filters]
    failures: list[str] = []
    if pdf_value(attrs.get("Subtype")) != "Image":
        failures.append("direct_subtype_not_image")
    if filters != ["DCTDecode"]:
        failures.append("direct_unsupported_filter")
    if attrs.get("Mask") is not None:
        failures.append("direct_explicit_mask_unsupported")
    if occurrence.get("imagemask"):
        failures.append("direct_image_mask")
    source_size = tuple(occurrence.get("srcsize") or ())
    declared_size = (int(attrs.get("Width") or 0), int(attrs.get("Height") or 0))
    if source_size != declared_size:
        failures.append("direct_dimension_disagreement")
    bits = int(attrs.get("BitsPerComponent") or 0)
    if int(occurrence.get("bits") or 0) != bits:
        failures.append("direct_bits_disagreement")
    objid = int(getattr(stream, "objid", 0) or 0)
    resolved = None
    smask_ref = None
    try:
        from pypdf.generic import IndirectObject

        resolved = IndirectObject(objid, 0, pypdf_reader).get_object()
        if pdf_value(resolved.get("/Subtype")) != "Image":
            failures.append("direct_pypdf_subtype_disagreement")
        if int(resolved.get("/Width") or 0) != declared_size[0] or int(resolved.get("/Height") or 0) != declared_size[1]:
            failures.append("direct_pypdf_dimension_disagreement")
        if resolved.get("/Mask") is not None:
            failures.append("direct_pypdf_explicit_mask_unsupported")
        smask_ref = resolved.get("/SMask")
        if bool(attrs.get("SMask")) != bool(smask_ref):
            failures.append("direct_smask_reader_disagreement")
    except Exception as exc:
        failures.append(f"direct_pypdf_resolution_failed:{type(exc).__name__}")
    if failures:
        return None, failures
    raw = bytes(getattr(stream, "rawdata", b""))
    try:
        with Image.open(io.BytesIO(raw)) as image:
            image.load()
            decoded = image.copy()
    except Exception:
        return None, ["direct_raw_decode_failed"]
    if decoded.size != declared_size:
        return None, ["direct_emitted_dimension_disagreement"]
    warnings: list[str] = []
    smask = None
    if smask_ref is not None:
        try:
            smask_object = smask_ref.get_object()
            smask_id = int(getattr(smask_ref, "idnum", 0) or 0)
            smask_filters = pdf_value(smask_object.get("/Filter"))
            smask_filters = smask_filters if isinstance(smask_filters, list) else [smask_filters]
            if pdf_value(smask_object.get("/Subtype")) != "Image" or smask_filters != ["DCTDecode"]:
                return None, ["direct_smask_unsupported"]
            if pdf_value(smask_object.get("/ColorSpace")) != "DeviceGray" or int(smask_object.get("/BitsPerComponent") or 0) != 8:
                return None, ["direct_smask_format_unsupported"]
            # pypdf get_data() returns decoded grayscale samples.  For a DCT
            # source we intentionally preserve and decode the original JPEG
            # stream so the portable bundle contains auditable source bytes.
            smask_raw = bytes(getattr(smask_object, "_data", b""))
            with Image.open(io.BytesIO(smask_raw)) as image:
                image.load()
                smask_image = image.convert("L")
            width_delta = abs(smask_image.width - decoded.width)
            height_delta = abs(smask_image.height - decoded.height)
            if width_delta > 1 or height_delta > 1:
                return None, ["direct_smask_dimension_disagreement"]
            if width_delta or height_delta:
                warnings.append("direct_smask_resampled_one_pixel")
                smask_image = smask_image.resize(decoded.size, Image.Resampling.LANCZOS)
            smask = {
                "object_id": smask_id,
                "raw": smask_raw,
                "image": smask_image,
                "original_dimensions": {
                    "width": int(smask_object.get("/Width") or 0),
                    "height": int(smask_object.get("/Height") or 0),
                },
            }
            warnings.append("direct_soft_mask_composited_review_required")
        except Exception as exc:
            return None, [f"direct_smask_decode_failed:{type(exc).__name__}"]
    return {
        "occurrence": occurrence,
        "attrs": attrs,
        "resolved": resolved,
        "object_id": objid,
        "raw": raw,
        "decoded": decoded,
        "declared_size": declared_size,
        "bits": bits,
        "colorspace": pdf_value(attrs.get("ColorSpace")),
        "smask": smask,
    }, warnings


def write_source_dct(
    output_root: Path,
    relative: str,
    raw: bytes,
) -> dict[str, Any]:
    path = output_root / safe_relative(relative).replace("/", os.sep)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(raw)
    return image_record(path, relative)


def crop_occurrence_image(
    image: Image.Image,
    placed_rect: list[float],
    target_rect: list[float],
) -> tuple[Image.Image, list[int]]:
    intersection = rect_intersection(placed_rect, target_rect)
    if rect_area(intersection) <= 0:
        raise ValueError("Occurrence does not intersect target")
    width = placed_rect[2] - placed_rect[0]
    height = placed_rect[3] - placed_rect[1]
    crop_box = [
        max(0, math.floor((intersection[0] - placed_rect[0]) * image.width / width)),
        max(0, math.floor((intersection[1] - placed_rect[1]) * image.height / height)),
        min(image.width, math.ceil((intersection[2] - placed_rect[0]) * image.width / width)),
        min(image.height, math.ceil((intersection[3] - placed_rect[1]) * image.height / height)),
    ]
    return image.crop(tuple(crop_box)), crop_box


def recover_region(
    asset: dict[str, Any],
    reconstruction_by_sha: dict[str, list[dict[str, Any]]],
    comparison: dict[str, Any],
) -> tuple[dict[str, Any] | None, list[str]]:
    provenance = asset.get("provenance") or {}
    kind = provenance.get("kind")
    if kind == "visual_region":
        return {
            "bbox": [float(value) for value in provenance["bbox"]],
            "view": provenance.get("selected_view"),
            "raw_index": provenance.get("raw_index"),
            "source": "publication_config",
        }, []
    if kind != "markdown_image_reference":
        return None, ["region_not_applicable"]
    binary = asset.get("binary") or {}
    matches = reconstruction_by_sha.get(str(binary.get("sha256") or "").upper(), [])
    if len(matches) != 1:
        return None, [f"markdown_reference_manifest_matches_{len(matches)}"]
    joined = matches[0]
    view = joined.get("view")
    source_path = joined.get("source_path")
    blocks = [
        block
        for block in (comparison.get("views", {}).get(view, {}).get("blocks", []))
        if source_path in (block.get("assets") or [])
        and int(block.get("source_page") or 0) == int(asset["source_page"])
        and block.get("type") == "image"
    ]
    if len(blocks) != 1:
        return None, [f"markdown_reference_comparison_matches_{len(blocks)}"]
    block = blocks[0]
    return {
        "bbox": [float(value) for value in block["bbox"]],
        "view": view,
        "raw_index": block.get("raw_index"),
        "source_path": source_path,
        "source": "reconstruction_manifest_and_comparison",
    }, []


def region_is_valid(region: dict[str, Any] | None) -> bool:
    if not region:
        return False
    bbox = region.get("bbox")
    return (
        isinstance(bbox, list)
        and len(bbox) == 4
        and all(isinstance(value, (int, float)) and 0 <= value <= 1000 for value in bbox)
        and bbox[0] < bbox[2]
        and bbox[1] < bbox[3]
    )


def text_overlap(region: dict[str, Any], comparison: dict[str, Any], page: int) -> dict[str, Any]:
    blocks = comparison.get("views", {}).get(region.get("view"), {}).get("blocks", [])
    hits = []
    for block in blocks:
        if int(block.get("source_page") or 0) != page or block.get("type") == "image":
            continue
        bbox = block.get("bbox")
        if not isinstance(bbox, list) or len(bbox) != 4:
            continue
        ratio = overlap_ratio(region["bbox"], [float(value) for value in bbox])
        if ratio > 0.01:
            hits.append({"raw_index": block.get("raw_index"), "type": block.get("type"), "target_overlap_ratio": round(ratio, 6)})
    return {"likely_text_contamination": bool(hits), "intersections": hits[:25]}


def extract_direct_candidate(
    *,
    asset_id: str,
    page: Any,
    pypdf_reader: Any,
    region: dict[str, Any],
    output_root: Path,
) -> tuple[dict[str, Any] | None, list[str]]:
    width = float(page.width)
    height = float(page.height)
    target = [region["bbox"][0] * width / 1000, region["bbox"][1] * height / 1000,
              region["bbox"][2] * width / 1000, region["bbox"][3] * height / 1000]
    occurrence, match_mode, iou, edge_delta, selection_warnings = select_direct_occurrence(
        page.images, target, width, height
    )
    if occurrence is None:
        return None, selection_warnings
    validated, validation_warnings = validate_dct_occurrence(occurrence, pypdf_reader)
    if validated is None:
        return None, validation_warnings
    attrs = validated["attrs"]
    declared_size = validated["declared_size"]
    objid = validated["object_id"]
    raw = validated["raw"]
    decoded = validated["decoded"]
    smask = validated["smask"]
    colorspace = validated["colorspace"]
    variant = "native"
    if match_mode == "containing_fuller_art":
        variant = "fuller"
    if smask is not None:
        variant = "fuller_masked" if variant == "fuller" else "masked"
    extension = "png" if smask is not None else "jpg"
    relative = f"assets/direct/{asset_id}.{extension}"
    target_path = output_root / relative
    target_path.parent.mkdir(parents=True, exist_ok=True)
    source_components = []
    if decoded.mode == "RGB" and smask is None:
        target_path.write_bytes(raw)
        binary = image_record(target_path, relative)
        source_binary = binary
        emitted_transform = "none; raw RGB DCT stream is the selectable binary"
    else:
        source_relative = f"assets/direct/source/{asset_id}.jpg"
        source_binary = write_source_dct(output_root, source_relative, raw)
        output_image, emitted_transform = display_image_from_pdf_dct(decoded)
        if smask is not None:
            output_image = output_image.convert("RGBA")
            output_image.putalpha(smask["image"])
            output_image.save(target_path, "PNG", optimize=False)
            emitted_transform += "; apply PDF soft mask; PNG RGBA metadata-stripped"
            mask_relative = f"assets/direct/source/{asset_id}-smask-{smask['object_id']}.jpg"
            mask_binary = write_source_dct(output_root, mask_relative, smask["raw"])
            source_components = [
                {"role": "base", "object_id": objid, "binary": source_binary},
                {"role": "soft_mask", "object_id": smask["object_id"], "binary": mask_binary},
            ]
        else:
            output_image.save(target_path, "JPEG", quality=92, subsampling=0, optimize=False, progressive=False)
            emitted_transform += "; JPEG q92 subsampling0 nonprogressive metadata-stripped"
        binary = image_record(target_path, relative)
    if not source_components:
        source_components = [{"role": "base", "object_id": objid, "binary": source_binary}]
    placed_rect = occurrence_rect(occurrence)
    locator = {
        "physical_page": int(region.get("source_page") or 0),
        "object_id": objid,
        "resource_name": occurrence.get("name"),
        "match_mode": match_mode,
        "occurrence_bbox_points_top_left": [round(value, 6) for value in placed_rect],
        "iou": round(iou, 8),
        "normalized_edge_delta": [round(value, 6) for value in edge_delta],
    }
    recipe = {
        "kind": "raw_pdf_dct_stream",
        "extractor": "pdfplumber PDFStream.rawdata",
        "validator": "pypdf IndirectObject",
        "filter": "DCTDecode",
        "no_mineru_binary": True,
        "source_no_resampling": True,
        "source_no_reencode": True,
        "selectable_emitted_transform": emitted_transform,
    }
    candidate_seed = {
        "asset_id": asset_id,
        "kind": "direct_xobject",
        "source_locator": locator,
        "recipe_sha256": sha256_bytes(canonical_json(recipe).encode("utf-8")),
        "emitted_sha256": binary["sha256"],
    }
    return {
        "candidate_id": "candidate-" + sha256_bytes(canonical_json(candidate_seed).encode("utf-8"))[:24].lower(),
        "kind": "direct_xobject",
        "path": relative,
        "binary": binary,
        "source_binary": source_binary,
        "source_components": source_components,
        "variant": variant,
        "source_locator": locator,
        "recipe": recipe,
        "quality": {
            "source_bits": int(attrs.get("BitsPerComponent") or 0),
            "source_colorspace": colorspace,
            "raw_stream_preserved": True,
            "effective_dpi": {
                "x": round(declared_size[0] * 72 / max(0.001, placed_rect[2] - placed_rect[0]), 2),
                "y": round(declared_size[1] * 72 / max(0.001, placed_rect[3] - placed_rect[1]), 2),
            },
        },
    }, selection_warnings + validation_warnings


def extract_multi_object_candidate(
    *, asset_id: str, page: Any, pypdf_reader: Any, region: dict[str, Any], output_root: Path,
) -> tuple[dict[str, Any] | None, list[str]]:
    """Build a review-only artwork from several native PDF image objects."""
    width = float(page.width)
    height = float(page.height)
    target = [region["bbox"][0] * width / 1000, region["bbox"][1] * height / 1000,
              region["bbox"][2] * width / 1000, region["bbox"][3] * height / 1000]
    target_area = rect_area(target)
    page_area = width * height
    components = []
    rejected: list[str] = []
    for occurrence in page.images:
        rect = occurrence_rect(occurrence)
        intersection = rect_intersection(rect, target)
        coverage = rect_area(intersection) / target_area if target_area else 0.0
        if coverage < 0.10 or rect_area(rect) / page_area >= 0.25:
            continue
        validated, failures = validate_dct_occurrence(occurrence, pypdf_reader)
        if validated is None:
            rejected.extend(failures)
            continue
        components.append((occurrence, validated, intersection, coverage))
    if not 2 <= len(components) <= 6:
        return None, sorted(set(rejected))
    clipped = [component[2] for component in components]
    union_coverage = rect_union_area(clipped) / target_area if target_area else 0.0
    if union_coverage < 0.85:
        return None, ["direct_multi_object_coverage_insufficient"]
    scale = 200 / 72
    canvas_width = max(1, math.ceil((target[2] - target[0]) * scale))
    canvas_height = max(1, math.ceil((target[3] - target[1]) * scale))
    canvas = Image.new("RGBA", (canvas_width, canvas_height), (255, 255, 255, 0))
    source_components = []
    object_ids = []
    placements = []
    warnings = ["direct_multi_object_composite_review_required"]
    for index, (occurrence, validated, intersection, _) in enumerate(components, start=1):
        object_id = validated["object_id"]
        object_ids.append(object_id)
        placed_rect = occurrence_rect(occurrence)
        display, _ = display_image_from_pdf_dct(validated["decoded"])
        cropped, native_crop = crop_occurrence_image(display, placed_rect, target)
        mask_crop = None
        if validated["smask"] is not None:
            mask_crop, _ = crop_occurrence_image(validated["smask"]["image"], placed_rect, target)
            warnings.append("direct_soft_mask_composited_review_required")
        output_box = [
            max(0, math.floor((intersection[0] - target[0]) * scale)),
            max(0, math.floor((intersection[1] - target[1]) * scale)),
            min(canvas_width, math.ceil((intersection[2] - target[0]) * scale)),
            min(canvas_height, math.ceil((intersection[3] - target[1]) * scale)),
        ]
        target_size = (max(1, output_box[2] - output_box[0]), max(1, output_box[3] - output_box[1]))
        rendered = cropped.convert("RGBA").resize(target_size, Image.Resampling.LANCZOS)
        if mask_crop is not None:
            rendered.putalpha(mask_crop.resize(target_size, Image.Resampling.LANCZOS))
        canvas.alpha_composite(rendered, (output_box[0], output_box[1]))
        base_rel = f"assets/direct/source/{asset_id}-part-{index}-xref-{object_id}.jpg"
        base_binary = write_source_dct(output_root, base_rel, validated["raw"])
        source_components.append({"role": "base", "object_id": object_id, "binary": base_binary})
        if validated["smask"] is not None:
            mask = validated["smask"]
            mask_rel = f"assets/direct/source/{asset_id}-part-{index}-smask-{mask['object_id']}.jpg"
            source_components.append({"role": "soft_mask", "object_id": mask["object_id"], "binary": write_source_dct(output_root, mask_rel, mask["raw"])})
        placements.append({"object_id": object_id, "occurrence_bbox_points_top_left": [round(v, 6) for v in placed_rect], "native_crop_box": native_crop, "output_box": output_box})
    relative = f"assets/direct/composite/{asset_id}.png"
    path = output_root / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(path, "PNG", optimize=False)
    binary = image_record(path, relative)
    locator = {"physical_page": int(region.get("source_page") or 0), "object_ids": object_ids, "target_bbox_points_top_left": [round(v, 6) for v in target], "placements": placements, "union_target_coverage": round(union_coverage, 6)}
    recipe = {"kind": "native_pdf_xobject_composite", "no_mineru_binary": True, "dpi": 200, "background": "transparent", "source_streams_preserved": True}
    return {
        "candidate_id": make_candidate_id(asset_id, "direct_composite_parts", locator, recipe, binary["sha256"]),
        "kind": "direct_composite_parts", "path": relative, "binary": binary,
        "source_components": source_components, "source_locator": locator, "recipe": recipe,
        "quality": {"union_target_coverage": round(union_coverage, 6), "component_count": len(components), "resampled": True},
    }, sorted(set(warnings))


def extract_page_composite_candidate(
    *, asset_id: str, page: Any, pypdf_reader: Any, region: dict[str, Any], output_root: Path,
) -> tuple[dict[str, Any] | None, list[str]]:
    """Crop art from a native full-page composite object, preserving its raw stream."""
    width = float(page.width)
    height = float(page.height)
    target = [region["bbox"][0] * width / 1000, region["bbox"][1] * height / 1000,
              region["bbox"][2] * width / 1000, region["bbox"][3] * height / 1000]
    page_area = width * height
    candidates = []
    for occurrence in page.images:
        rect = occurrence_rect(occurrence)
        page_coverage = rect_area(rect) / page_area
        if overlap_ratio(target, rect) < 0.98 or not 0.80 <= page_coverage <= 1.10:
            continue
        validated, failures = validate_dct_occurrence(occurrence, pypdf_reader)
        if validated is not None and validated["colorspace"] != "DeviceGray":
            candidates.append((occurrence, validated, page_coverage))
    if len(candidates) != 1:
        return None, ["embedded_page_composite_not_unique"] if candidates else []
    occurrence, validated, page_coverage = candidates[0]
    placed_rect = occurrence_rect(occurrence)
    display, transform = display_image_from_pdf_dct(validated["decoded"])
    cropped, native_crop = crop_occurrence_image(display, placed_rect, target)
    relative = f"assets/direct/page_composite/{asset_id}.png"
    path = output_root / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    cropped.save(path, "PNG", optimize=False)
    binary = image_record(path, relative)
    object_id = validated["object_id"]
    source_rel = f"assets/direct/source/{asset_id}-page-composite-xref-{object_id}.jpg"
    source_binary = write_source_dct(output_root, source_rel, validated["raw"])
    locator = {"physical_page": int(region.get("source_page") or 0), "object_id": object_id, "occurrence_bbox_points_top_left": [round(v, 6) for v in placed_rect], "target_bbox_points_top_left": [round(v, 6) for v in target], "native_crop_box": native_crop, "page_coverage": round(page_coverage, 6)}
    recipe = {"kind": "crop_native_full_page_xobject", "no_mineru_binary": True, "source_stream_preserved": True, "display_transform": transform, "output": "PNG RGB metadata-stripped"}
    return {
        "candidate_id": make_candidate_id(asset_id, "embedded_page_composite_crop", locator, recipe, binary["sha256"]),
        "kind": "embedded_page_composite_crop", "path": relative, "binary": binary,
        "source_binary": source_binary,
        "source_components": [{"role": "page_composite", "object_id": object_id, "binary": source_binary}],
        "source_locator": locator, "recipe": recipe,
        "quality": {"page_coverage": round(page_coverage, 6), "raw_stream_preserved": True, "resampled": False},
    }, ["embedded_page_composite_review_required"]


def make_candidate_id(asset_id: str, kind: str, locator: dict[str, Any], recipe: dict[str, Any], digest: str) -> str:
    seed = {
        "asset_id": asset_id,
        "kind": kind,
        "source_locator": locator,
        "recipe_sha256": sha256_bytes(canonical_json(recipe).encode("utf-8")),
        "emitted_sha256": digest,
    }
    return "candidate-" + sha256_bytes(canonical_json(seed).encode("utf-8"))[:24].lower()


def extract_heading_labels(markdown: str) -> dict[str, str]:
    labels: dict[str, str] = {}
    lines = markdown.splitlines()
    for index, line in enumerate(lines):
        for match in re.finditer(r'<a id="([A-Za-z0-9_-]+)"></a>', line):
            remainder = line[match.end():].strip()
            label = re.sub(r"[*_`\[\]()]", "", remainder).strip()
            if not label:
                for following in lines[index + 1:index + 12]:
                    if following.lstrip().startswith("#"):
                        label = following.lstrip("#").strip()
                        break
            labels[match.group(1)] = label or match.group(1)
    return labels


def iter_row_binary_records(row: dict[str, Any]):
    """Yield every portable binary record referenced by one review row."""
    for key in ("current", "context"):
        record = row.get(key)
        if isinstance(record, dict) and record.get("path"):
            yield record
    for candidate in row.get("alternatives", []):
        for key in ("binary", "source_binary"):
            record = candidate.get(key)
            if isinstance(record, dict) and record.get("path"):
                yield record
        for component in candidate.get("source_components", []):
            record = component.get("binary")
            if isinstance(record, dict) and record.get("path"):
                yield record


def artview_group(anchor: str | None, provenance: dict[str, Any] | None) -> str:
    """Classify a review row for useful presets and filtering, not publication."""
    value = str(anchor or "")
    if value.startswith("viral-handout-"):
        return "handout"
    if value.startswith("viral-keeper-map"):
        return "keeper_map"
    if value.startswith("viral-pregen-"):
        return "pregen"
    if (provenance or {}).get("kind") == "reviewed_provisional_full_page":
        return "full_page"
    return "body"


def default_presentation(group: str) -> dict[str, Any]:
    """Return editable recommendations; they are not accepted until reviewed."""
    if group == "pregen":
        return {"width_percent": 100, "alignment": "center", "wrap_text": False, "wrap_tables": False}
    if group in {"handout", "keeper_map"}:
        return {"width_percent": 80, "alignment": "center", "wrap_text": False, "wrap_tables": False}
    if group == "full_page":
        return {"width_percent": 100, "alignment": "center", "wrap_text": False, "wrap_tables": False}
    return {"width_percent": 25, "alignment": "right", "wrap_text": True, "wrap_tables": False}


def production_asset_states(
    production_manifest: dict[str, Any] | None,
    asset_decisions: dict[str, Any] | None,
) -> dict[str, dict[str, Any]]:
    """Project the current package state onto the 94 traceable review slots."""
    states: dict[str, dict[str, Any]] = {}
    if production_manifest:
        for item in production_manifest.get("files", []):
            path = str(item.get("path") or "")
            match = re.fullmatch(r"assets/([0-9a-fA-F]{64})\.[A-Za-z0-9]+", path)
            if match:
                states["viral-accepted-" + match.group(1).lower()] = {
                    "status": "included",
                    "reason": "present_in_current_production",
                    "paths": [path],
                }
    decisions = asset_decisions or {}
    suppressed: list[tuple[str, str]] = []
    for filename in decisions.get("suppressed_redundant_text_facsimiles", []):
        suppressed.append((str(filename), "suppressed_redundant_text_facsimile"))
    duplicate = decisions.get("suppressed_duplicate_narrative_art")
    if duplicate:
        suppressed.append((str(duplicate), "suppressed_duplicate_narrative_art"))
    for filename, reason in suppressed:
        digest = Path(filename).stem.casefold()
        if re.fullmatch(r"[0-9a-f]{64}", digest):
            states["viral-accepted-" + digest] = {"status": "excluded", "reason": reason, "paths": []}
    return states


def decision_bindings(manifest: dict[str, Any], manifest_sha: str) -> dict[str, str]:
    sources = manifest.get("decision_contract", {}).get(
        "binding_sources",
        ["source_pdf", "master_en", "master_ru"],
    )
    result = {
        "candidate_manifest_sha256": manifest_sha.upper(),
        "candidate_files_inventory_sha256": str(manifest["candidate_files_inventory_sha256"]).upper(),
    }
    for key in sources:
        if key not in manifest.get("bindings", {}):
            raise ValueError(f"Missing decision binding source: {key}")
        result[f"{key}_sha256"] = str(manifest["bindings"][key]["sha256"]).upper()
    return result


def draft_decision_document(manifest: dict[str, Any], manifest_sha: str) -> dict[str, Any]:
    """Create a portable, fully bound but deliberately unreviewed decision file."""
    result = {
        "schema": DECISION_SCHEMA_V3 if manifest.get("schema") == CANDIDATE_SCHEMA_V3 else DECISION_SCHEMA,
        "scenario_id": manifest["scenario_id"],
        "state": "draft",
        "bindings": decision_bindings(manifest, manifest_sha),
        "decisions": [
            {
                "asset_id": row["asset_id"],
                "binary": {"choice": None, "candidate_id": None},
                "presentation": row["presentation_defaults"],
                "reviewed": False,
                "notes": "",
            }
            for row in manifest["rows"]
        ],
    }
    if result["schema"] == DECISION_SCHEMA_V3:
        result["review"] = {"state": "open", "reviewed_count": 0, "unresolved_asset_ids": [row["asset_id"] for row in manifest["rows"]]}
        result["decisions_sha256"] = sha256_bytes(canonical_json(result).encode("utf-8"))
    return result


def presentation_findings(value: Any, asset_id: str) -> list[dict[str, Any]]:
    findings: list[dict[str, Any]] = []
    if not isinstance(value, dict):
        return [{"code": "presentation_missing", "asset_id": asset_id}]
    width = value.get("width_percent")
    alignment = value.get("alignment")
    wrap_text = value.get("wrap_text")
    wrap_tables = value.get("wrap_tables")
    if isinstance(width, bool) or not isinstance(width, int) or not 10 <= width <= 100:
        findings.append({"code": "presentation_width_invalid", "asset_id": asset_id})
    if alignment not in PRESENTATION_ALIGNMENTS:
        findings.append({"code": "presentation_alignment_invalid", "asset_id": asset_id})
    if not isinstance(wrap_text, bool) or not isinstance(wrap_tables, bool):
        findings.append({"code": "presentation_wrap_invalid", "asset_id": asset_id})
    elif wrap_tables and not wrap_text:
        findings.append({"code": "table_wrap_requires_text_wrap", "asset_id": asset_id})
    if alignment == "center" and (wrap_text is True or wrap_tables is True):
        findings.append({"code": "center_alignment_cannot_wrap", "asset_id": asset_id})
    return findings


def html_bundle(manifest: dict[str, Any], manifest_sha: str) -> str:
    payload = canonical_json(manifest).replace("&", "\\u0026").replace("<", "\\u003c").replace(">", "\\u003e")
    expected_bindings = canonical_json(decision_bindings(manifest, manifest_sha))
    template = r'''<!doctype html>
<html lang="ru"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Viral — ArtView v2</title>
<style>
:root{--bg:#0f172a;--panel:#1e293b;--panel2:#111827;--muted:#94a3b8;--line:#334155;--accent:#8b5cf6;--accent2:#c4b5fd;--ok:#34d399;--warn:#fbbf24;--bad:#fb7185}
*{box-sizing:border-box} body{margin:0;background:var(--bg);color:#f8fafc;font:15px/1.45 system-ui,sans-serif}
header{position:sticky;top:0;z-index:10;background:#0f172aee;border-bottom:1px solid var(--line);padding:13px 20px;backdrop-filter:blur(8px)}
h1{font-size:22px;margin:0 0 4px}.sub,.meta{color:var(--muted)}.toolbar{display:flex;gap:9px;align-items:center;flex-wrap:wrap;margin-top:10px}
button,input,select,textarea{font:inherit}button{background:#4c1d95;color:white;border:1px solid #6d28d9;border-radius:7px;padding:7px 11px;cursor:pointer}button.secondary{background:#1f2937;border-color:#475569}button:disabled{opacity:.4;cursor:not-allowed}
select,input[type=search],input[type=number],textarea{background:#0b1220;color:white;border:1px solid #475569;border-radius:6px;padding:6px 8px}input[type=search]{min-width:260px}
main{padding:18px;max-width:1900px;margin:auto}.row{background:var(--panel);border:1px solid var(--line);border-radius:11px;padding:14px;margin:0 0 20px;scroll-margin-top:125px}.row.reviewed{border-color:#15803d}.row h2{margin:0 0 5px;font-size:19px}.row-head{display:flex;gap:12px;justify-content:space-between;align-items:flex-start}.badges{display:flex;gap:6px;flex-wrap:wrap}.badge{font-size:12px;padding:2px 7px;border:1px solid #64748b;border-radius:999px;color:#cbd5e1}.badge.included{border-color:#059669;color:#6ee7b7}.badge.excluded{border-color:#e11d48;color:#fda4af}
.candidates{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:10px;margin:12px 0}.candidate{display:block;background:var(--panel2);border:2px solid var(--line);border-radius:9px;padding:8px;min-width:0;color:inherit}.candidate.selectable{cursor:pointer}.candidate.selected{border-color:var(--accent);box-shadow:0 0 0 2px #8b5cf633}.candidate.unavailable{border-style:dashed;color:var(--muted)}.candidate h3{font-size:14px;margin:0 0 7px}.candidate img{display:block;width:100%;height:230px;object-fit:contain;background:#070d1a}.candidate input{margin-right:7px}.candidate-links{display:flex;gap:8px;flex-wrap:wrap}.facts{font:12px/1.4 ui-monospace,monospace;color:#cbd5e1;overflow-wrap:anywhere}.origin{font:12px/1.35 system-ui,sans-serif;color:#93c5fd;margin:5px 0}.context{position:relative;background:#070d1a}.context img{height:230px}.bbox{position:absolute;border:3px solid #ef4444;background:#ef444422;pointer-events:none}
.decision-grid{display:grid;grid-template-columns:minmax(320px,.8fr) minmax(460px,1.2fr);gap:12px;margin-top:12px}.controls,.preview-shell{background:var(--panel2);border:1px solid var(--line);border-radius:9px;padding:12px}.controls h3,.preview-shell h3{font-size:15px;margin:0 0 9px}.workflow{display:flex;gap:9px;flex-wrap:wrap;padding:8px;background:#0b1220;border-radius:7px}.layout-grid{display:grid;grid-template-columns:repeat(2,minmax(170px,1fr));gap:9px;margin-top:10px}.control{display:flex;gap:7px;align-items:center}.layout-grid .control:first-child{grid-column:1/-1}.control label{min-width:105px;color:#cbd5e1}.control input[type=range]{flex:1}.control input[type=number]{width:72px}.presets{display:flex;gap:7px;flex-wrap:wrap;margin-top:10px}.review-line{display:flex;gap:8px;align-items:center;margin-top:12px;padding:9px;border:1px solid #475569;border-radius:7px}.review-line.ready{border-color:#059669;background:#052e2422}
.preview{background:#fffaf0;color:#292524;border-radius:6px;padding:13px;min-height:330px;overflow:hidden;font:14px/1.38 Georgia,serif}.preview-art{display:block;height:auto;max-height:250px;object-fit:contain;margin:0 auto 10px}.preview-art.float-left{float:left;margin:0 12px 8px 0}.preview-art.float-right{float:right;margin:0 0 8px 12px}.preview.no-text-wrap .preview-copy{clear:both}.preview-table{border-collapse:collapse;margin-top:9px;width:100%;font-size:12px}.preview-table.clear-table{clear:both}.preview-table.wrap-table{width:auto;min-width:45%}.preview-table th,.preview-table td{border:1px solid #a8a29e;padding:4px 6px}.preview-empty{padding:65px 10px;text-align:center;color:#78716c;border:2px dashed #d6d3d1}
textarea{width:100%;margin-top:10px;min-height:58px}.warning{color:var(--warn)}.ok{color:var(--ok)}.error{color:var(--bad)}a{color:var(--accent2)}.hidden{display:none!important}#message{min-height:1.4em}.sr-only{position:absolute;opacity:0;pointer-events:none}.nowrap{white-space:nowrap}
@media(max-width:1350px){.candidates{grid-template-columns:repeat(2,minmax(0,1fr))}}@media(max-width:980px){.decision-grid{grid-template-columns:1fr}.layout-grid{grid-template-columns:1fr}header{position:static}.row{scroll-margin-top:10px}}@media(max-width:680px){.candidates{grid-template-columns:1fr}.candidate img,.context img{height:260px}}
</style></head><body>
<header><h1>Viral — ArtView v2</h1><div class="sub">94 логических слота: текущий файл, crop страницы, кандидат из PDF без MinerU и контекст. Бинарник и параметры представления выбираются отдельно; ничего не применяется к MASTER или production автоматически.</div>
<div class="toolbar">
<select id="filter"><option value="all">Все строки</option><option value="unreviewed">Не проверены</option><option value="unresolved">Нет финального бинарника</option><option value="direct">Есть кандидат из PDF</option><option value="derived">Есть crop страницы</option><option value="full">Есть полная страница</option><option value="production-excluded">Сейчас исключены</option><option value="body">Обычный body art</option><option value="handout">Раздатки</option><option value="keeper_map">Карты Хранителя</option><option value="pregen">Листы сыщиков</option><option value="warning">С предупреждениями</option></select>
<input id="search" type="search" placeholder="Поиск по заголовку, anchor или asset id">
<button id="exportDraft">Экспорт черновика</button><button id="exportAccepted" disabled>Экспорт принятого JSON</button><button id="importButton" class="secondary">Импорт JSON</button><input id="importFile" type="file" accept="application/json" hidden>
<span id="progress"></span><span id="message"></span></div></header>
<main id="rows"></main>
<script type="application/json" id="manifest">__MANIFEST__</script>
<script>
"use strict";
const manifest=JSON.parse(document.getElementById("manifest").textContent);
const manifestSha="__MANIFEST_SHA__";
const decisionSchema="__DECISION_SCHEMA__";
const expectedBindings=__EXPECTED_BINDINGS__;
const state={};
const storageKey="scenario-artview-v2:"+manifestSha;
const finalChoices=new Set(["keep_current","use_candidate","exclude"]);
const choiceLabels={keep_current:"текущий файл",use_candidate:"выбранный кандидат",exclude:"исключить",needs_manual_work:"нужна ручная работа",reopen_masters:"вернуться к MASTER"};
const directKinds=new Set(["direct_xobject","embedded_page_composite_crop","direct_composite_parts"]);
const kindLabels={direct_xobject:"Из PDF напрямую",embedded_page_composite_crop:"Crop из PDF-композита",direct_composite_parts:"Композиция PDF-объектов",derived_page_crop:"Crop из страницы",full_page_render:"Полная страница"};
const groupLabels={body:"body art",handout:"раздатка",keeper_map:"карта Хранителя",pregen:"лист сыщика",full_page:"полная страница"};
const productionLabels={included:"в текущем production",excluded:"сейчас исключён",unknown:"production-статус неизвестен",absent:"нет в текущем production"};
const el=(tag,cls,text)=>{const node=document.createElement(tag);if(cls)node.className=cls;if(text!==undefined)node.textContent=text;return node};
function clone(value){return JSON.parse(JSON.stringify(value))}
function defaultState(row){return {binary:{choice:null,candidate_id:null},presentation:clone(row.presentation_defaults),reviewed:false,notes:""}}
function normalizeState(row,value){const base=defaultState(row);if(!value||typeof value!=="object")return base;if(value.binary&&typeof value.binary==="object"){base.binary.choice=value.binary.choice||null;base.binary.candidate_id=value.binary.candidate_id||null}if(value.presentation&&typeof value.presentation==="object")Object.assign(base.presentation,value.presentation);base.reviewed=value.reviewed===true;base.notes=typeof value.notes==="string"?value.notes:"";return base}
function facts(item){if(!item)return "";const binary=item.binary||item,dimensions=binary.dimensions||{};return `${dimensions.width||"?"}×${dimensions.height||"?"} · ${binary.bytes||0} bytes · ${binary.colorspace||"?"} · ${(binary.sha256||"").slice(0,16)}…`}
function originFacts(item){if(!item)return "";const locator=item.source_locator||{},source=item.source_binary||{};if(item.kind==="direct_xobject"){const variant=item.variant==="fuller"?"полный исходный арт":item.variant==="masked"?"base + soft mask":item.variant==="fuller_masked"?"полный арт + soft mask":locator.match_mode||"exact_region";return `PDF XObject ${locator.object_id||"?"} · ${variant} · raw ${source.colorspace||"?"} → рабочий ${(item.binary||{}).colorspace||"?"} · без MinerU`}if(item.kind==="embedded_page_composite_crop")return `PDF XObject ${locator.object_id||"?"} · crop из встроенного композита страницы · без MinerU`;if(item.kind==="direct_composite_parts")return `PDF XObject ${JSON.stringify(locator.object_ids||[])} · композиция нативных объектов · без MinerU`;if(item.kind==="derived_page_crop")return "Рендер страницы PDF + crop по региону";if(item.kind==="full_page_render")return "Полный рендер страницы PDF";return ""}
function selectedItem(row,current){if(current.binary.choice==="keep_current")return row.current;if(current.binary.choice==="use_candidate")return row.alternatives.find(item=>item.candidate_id===current.binary.candidate_id)||null;return null}
function selectBinary(row,choice,candidateId){const current=state[row.asset_id];current.binary={choice,candidate_id:candidateId||null};current.reviewed=false;persist();updateRow(document.querySelector(`[data-asset="${row.asset_id}"]`),row)}
function choiceCard(row,title,item,choice,candidateId){const label=el("label","candidate selectable");label.dataset.choice=choice;label.dataset.candidate=candidateId||"";const input=el("input","sr-only");input.type="radio";input.name="binary-"+row.asset_id;input.addEventListener("change",()=>selectBinary(row,choice,candidateId));const heading=el("h3");heading.append(input,document.createTextNode(title));const image=el("img");image.loading="lazy";image.alt=title;image.src=item.path;const links=el("div","candidate-links"),link=el("a","",directKinds.has(item.kind)?"Открыть рабочий файл":"Открыть оригинал");link.href=item.path;link.target="_blank";link.addEventListener("click",event=>event.stopPropagation());links.append(link);const seen=new Set([item.path]);for(const component of item.source_components||[]){const binary=component.binary||{};if(!binary.path||seen.has(binary.path))continue;seen.add(binary.path);const sourceLink=el("a","",`Открыть raw ${component.role||"XObject"} ${component.object_id||""}`.trim());sourceLink.href=binary.path;sourceLink.target="_blank";sourceLink.addEventListener("click",event=>event.stopPropagation());links.append(sourceLink)}if(item.source_binary&&item.source_binary.path&&!seen.has(item.source_binary.path)){const sourceLink=el("a","","Открыть raw XObject");sourceLink.href=item.source_binary.path;sourceLink.target="_blank";sourceLink.addEventListener("click",event=>event.stopPropagation());links.append(sourceLink)}label.append(heading,image,links);const origin=originFacts(item);if(origin)label.append(el("div","origin",origin));label.append(el("div","facts",facts(item)));return label}
function missingCard(title,text){const card=el("section","candidate unavailable"),heading=el("h3","",title),empty=el("div","preview-empty",text);card.append(heading,empty);return card}
function contextCard(row){const card=el("section","candidate"),heading=el("h3","","Контекст исходной страницы"),wrap=el("div","context"),image=el("img");image.loading="lazy";image.alt="Контекст страницы";image.src=row.context.path;wrap.append(image);if(row.region&&row.region.bbox){const box=el("div","bbox"),bbox=row.region.bbox;box.style.left=bbox[0]/10+"%";box.style.top=bbox[1]/10+"%";box.style.width=(bbox[2]-bbox[0])/10+"%";box.style.height=(bbox[3]-bbox[1])/10+"%";wrap.append(box)}const link=el("a","","Открыть страницу");link.href=row.context.path;link.target="_blank";card.append(heading,wrap,link,el("div","facts",facts(row.context)));return card}
function radioChoice(row,choice){const label=el("label"),input=el("input");input.type="radio";input.name="binary-"+row.asset_id;input.value=choice;input.addEventListener("change",()=>selectBinary(row,choice,null));label.append(input,document.createTextNode(" "+choiceLabels[choice]));return label}
function preset(row,values){Object.assign(state[row.asset_id].presentation,values);state[row.asset_id].reviewed=false;persist();updateRow(document.querySelector(`[data-asset="${row.asset_id}"]`),row)}
function buildPreview(){const shell=el("section","preview-shell"),heading=el("h3","","Предварительный макет"),preview=el("div","preview"),image=el("img","preview-art"),empty=el("div","preview-empty","Сначала выберите бинарник или исключение"),copy=el("div","preview-copy");copy.innerHTML="<p><strong>Пример раздела.</strong> Этот текст показывает реальное соотношение иллюстрации и наборной полосы. Изменяйте размер, позицию и обтекание, чтобы увидеть предполагаемое поведение.</p><p>Второй абзац помогает оценить, не становится ли колонка рядом с изображением слишком узкой.</p>";const table=el("table","preview-table");table.innerHTML="<thead><tr><th>Параметр</th><th>Значение</th></tr></thead><tbody><tr><td>Проверка</td><td>50%</td></tr><tr><td>Урон</td><td>1D6</td></tr></tbody>";preview.append(image,empty,copy,table);shell.append(heading,preview);return shell}
function layoutControls(row){const current=state[row.asset_id],box=el("section","controls"),heading=el("h3","","Параметры представления"),grid=el("div","layout-grid");box.append(heading);const widthControl=el("div","control"),widthLabel=el("label","","Размер, %"),range=el("input");range.type="range";range.min="10";range.max="100";range.step="5";range.dataset.field="width-range";const number=el("input");number.type="number";number.min="10";number.max="100";number.step="1";number.dataset.field="width-number";for(const input of [range,number])input.addEventListener("input",()=>{const value=Math.max(10,Math.min(100,Number(input.value)||10));current.presentation.width_percent=Math.round(value);current.reviewed=false;persist();updateRow(document.querySelector(`[data-asset="${row.asset_id}"]`),row)});widthControl.append(widthLabel,range,number);const alignControl=el("div","control"),alignLabel=el("label","","Позиция"),align=el("select");align.dataset.field="alignment";for(const [value,text] of [["left","слева"],["center","по центру"],["right","справа"]]){const option=el("option","",text);option.value=value;align.append(option)}align.addEventListener("change",()=>{current.presentation.alignment=align.value;if(align.value==="center"){current.presentation.wrap_text=false;current.presentation.wrap_tables=false}current.reviewed=false;persist();updateRow(document.querySelector(`[data-asset="${row.asset_id}"]`),row)});alignControl.append(alignLabel,align);const textControl=el("div","control"),textWrap=el("input");textWrap.type="checkbox";textWrap.dataset.field="wrap-text";textWrap.addEventListener("change",()=>{current.presentation.wrap_text=textWrap.checked;if(!textWrap.checked)current.presentation.wrap_tables=false;current.reviewed=false;persist();updateRow(document.querySelector(`[data-asset="${row.asset_id}"]`),row)});textControl.append(textWrap,document.createTextNode("Обтекать обычным текстом"));const tableControl=el("div","control"),tableWrap=el("input");tableWrap.type="checkbox";tableWrap.dataset.field="wrap-tables";tableWrap.addEventListener("change",()=>{current.presentation.wrap_tables=tableWrap.checked;current.reviewed=false;persist();updateRow(document.querySelector(`[data-asset="${row.asset_id}"]`),row)});tableControl.append(tableWrap,document.createTextNode("Разрешить обтекание таблицами"));grid.append(widthControl,alignControl,textControl,tableControl);box.append(grid);const presets=el("div","presets");for(const [text,values] of [["Body: 25% справа",{width_percent:25,alignment:"right",wrap_text:true,wrap_tables:false}],["Body + таблицы",{width_percent:25,alignment:"right",wrap_text:true,wrap_tables:true}],["Раздатка: 80%",{width_percent:80,alignment:"center",wrap_text:false,wrap_tables:false}],["Полная страница",{width_percent:100,alignment:"center",wrap_text:false,wrap_tables:false}]]){const button=el("button","secondary",text);button.type="button";button.addEventListener("click",()=>preset(row,values));presets.append(button)}box.append(presets);const review=el("label","review-line"),reviewed=el("input");reviewed.type="checkbox";reviewed.dataset.field="reviewed";reviewed.addEventListener("change",()=>{current.reviewed=reviewed.checked;persist();updateRow(document.querySelector(`[data-asset="${row.asset_id}"]`),row)});review.append(reviewed,document.createTextNode("Я проверил бинарник и параметры этой строки"));box.append(review);return box}
function updateRow(card,row){if(!card)return;const current=state[row.asset_id],item=selectedItem(row,current),presentation=current.presentation;card.classList.toggle("reviewed",current.reviewed);card.querySelectorAll(".selectable").forEach(node=>{const selected=node.dataset.choice===current.binary.choice&&(node.dataset.choice!=="use_candidate"||node.dataset.candidate===current.binary.candidate_id);node.classList.toggle("selected",selected);const input=node.querySelector("input");if(input)input.checked=selected});card.querySelectorAll(".workflow input").forEach(input=>{input.checked=input.value===current.binary.choice});const range=card.querySelector('[data-field="width-range"]'),number=card.querySelector('[data-field="width-number"]'),align=card.querySelector('[data-field="alignment"]'),wrapText=card.querySelector('[data-field="wrap-text"]'),wrapTables=card.querySelector('[data-field="wrap-tables"]'),reviewed=card.querySelector('[data-field="reviewed"]');range.value=String(presentation.width_percent);number.value=String(presentation.width_percent);align.value=presentation.alignment;wrapText.checked=presentation.wrap_text;wrapTables.checked=presentation.wrap_tables;wrapText.disabled=presentation.alignment==="center";wrapTables.disabled=presentation.alignment==="center"||!presentation.wrap_text;reviewed.checked=current.reviewed;reviewed.parentElement.classList.toggle("ready",current.reviewed);const preview=card.querySelector(".preview"),image=card.querySelector(".preview-art"),empty=card.querySelector(".preview-empty"),table=card.querySelector(".preview-table");preview.classList.toggle("no-text-wrap",!presentation.wrap_text);preview.classList.toggle("wrap-tables",presentation.wrap_tables);table.classList.toggle("clear-table",!presentation.wrap_tables);table.classList.toggle("wrap-table",presentation.wrap_tables);image.className="preview-art";image.style.marginLeft="";image.style.marginRight="";if(item){image.src=item.path;image.alt=row.label||row.anchor;image.style.width=presentation.width_percent+"%";image.hidden=false;empty.hidden=true;if(presentation.wrap_text&&presentation.alignment!=="center")image.classList.add("float-"+presentation.alignment);else{image.style.marginLeft=presentation.alignment==="right"?"auto":"0";image.style.marginRight=presentation.alignment==="left"?"auto":"0";if(presentation.alignment==="center"){image.style.marginLeft="auto";image.style.marginRight="auto"}}}else{image.hidden=true;empty.hidden=false;empty.textContent=current.binary.choice==="exclude"?"Арт будет исключён из финального продукта":"Сначала выберите бинарник или рабочее решение"}updateProgress();applyFilter()}
function buildRow(row,index){state[row.asset_id]=normalizeState(row,state[row.asset_id]);const card=el("article","row");card.dataset.asset=row.asset_id;card.dataset.kinds=row.alternatives.map(item=>item.kind).join(" ");card.dataset.warning=(row.warnings||[]).length?"yes":"no";card.dataset.group=row.group;card.dataset.production=(row.production_state||{}).status||"unknown";card.dataset.search=`${row.label||""} ${row.anchor||""} ${row.asset_id}`.toLowerCase();const head=el("div","row-head"),titleWrap=el("div"),badges=el("div","badges");titleWrap.append(el("h2","",`${index+1}. ${row.label||row.anchor}`),el("div","meta",`${row.asset_id} · исходная страница ${row.source_page} · ${JSON.stringify(row.placement)}`));const production=(row.production_state||{}).status||"unknown";badges.append(el("span","badge "+production,productionLabels[production]||production),el("span","badge",groupLabels[row.group]||row.group));head.append(titleWrap,badges);card.append(head);const grid=el("div","candidates"),pageCandidate=row.alternatives.find(item=>item.kind==="derived_page_crop"||item.kind==="full_page_render"),directCandidate=row.alternatives.find(item=>directKinds.has(item.kind));grid.append(choiceCard(row,"Текущий файл",row.current,"keep_current",null));grid.append(pageCandidate?choiceCard(row,kindLabels[pageCandidate.kind],pageCandidate,"use_candidate",pageCandidate.candidate_id):missingCard("Crop из страницы","Для этой строки нет отдельного region-crop"));grid.append(directCandidate?choiceCard(row,kindLabels[directCandidate.kind],directCandidate,"use_candidate",directCandidate.candidate_id):missingCard("Из PDF напрямую","Подходящий PDF XObject не найден"));grid.append(contextCard(row));card.append(grid);if(row.warnings&&row.warnings.length)card.append(el("div","warning","Предупреждения: "+row.warnings.join(" · ")));const workflow=el("div","workflow");for(const choice of ["exclude","needs_manual_work","reopen_masters"])workflow.append(radioChoice(row,choice));card.append(workflow);const decisionGrid=el("div","decision-grid");decisionGrid.append(layoutControls(row),buildPreview());card.append(decisionGrid);const notes=el("textarea");notes.placeholder="Заметка к решению";notes.value=state[row.asset_id].notes;notes.addEventListener("input",()=>{state[row.asset_id].notes=notes.value;persist()});card.append(notes);updateRow(card,row);return card}
function persist(){localStorage.setItem(storageKey,JSON.stringify(state));updateProgress()}
function isAcceptedRow(row){const current=state[row.asset_id];return current.reviewed&&finalChoices.has(current.binary.choice)&&(current.binary.choice!=="use_candidate"||row.alternatives.some(item=>item.candidate_id===current.binary.candidate_id))}
function updateProgress(){const reviewed=manifest.rows.filter(row=>state[row.asset_id]&&state[row.asset_id].reviewed).length,accepted=manifest.rows.filter(isAcceptedRow).length;document.getElementById("progress").textContent=`Проверено: ${reviewed} / ${manifest.rows.length} · готово к принятию: ${accepted}`;document.getElementById("exportAccepted").disabled=accepted!==manifest.rows.length}
function decisionDocument(documentState){return {schema:decisionSchema,scenario_id:manifest.scenario_id,state:documentState,bindings:expectedBindings,decisions:manifest.rows.map(row=>{const current=state[row.asset_id]||defaultState(row);return {asset_id:row.asset_id,binary:clone(current.binary),presentation:clone(current.presentation),reviewed:current.reviewed,notes:current.notes||""}})}}
function validatePresentation(value){if(!value||!Number.isInteger(value.width_percent)||value.width_percent<10||value.width_percent>100)throw Error("Размер должен быть целым числом 10–100");if(!["left","center","right"].includes(value.alignment))throw Error("Неверная позиция");if(typeof value.wrap_text!=="boolean"||typeof value.wrap_tables!=="boolean")throw Error("Неверные флаги обтекания");if(value.wrap_tables&&!value.wrap_text)throw Error("Обтекание таблицами требует обтекания текстом");if(value.alignment==="center"&&(value.wrap_text||value.wrap_tables))throw Error("Центральный арт не может обтекаться")}
function validateImport(documentValue){if(!documentValue||documentValue.schema!==decisionSchema||documentValue.scenario_id!==manifest.scenario_id)throw Error("Неверная схема или scenario_id");if(!["draft","accepted"].includes(documentValue.state))throw Error("Неверное состояние документа");for(const key of Object.keys(expectedBindings))if(!documentValue.bindings||documentValue.bindings[key]!==expectedBindings[key])throw Error("Не совпадает binding: "+key);if(Object.keys(documentValue.bindings||{}).length!==Object.keys(expectedBindings).length)throw Error("Лишние bindings");if(!Array.isArray(documentValue.decisions)||documentValue.decisions.length!==manifest.rows.length)throw Error("Неверное число решений");const seen=new Set();for(const item of documentValue.decisions){const row=manifest.rows.find(value=>value.asset_id===item.asset_id);if(!row||seen.has(item.asset_id))throw Error("Неизвестный или повторный asset_id");seen.add(item.asset_id);const choice=item.binary&&item.binary.choice,candidateId=item.binary&&item.binary.candidate_id;if(choice!==null&&!row.allowed_binary_decisions.includes(choice))throw Error("Недопустимое решение для "+item.asset_id);if(choice==="use_candidate"&&!row.alternatives.some(value=>value.candidate_id===candidateId))throw Error("Неизвестный candidate_id");if(choice!=="use_candidate"&&candidateId!==null)throw Error("Лишний candidate_id");if(typeof item.reviewed!=="boolean")throw Error("Нет reviewed для "+item.asset_id);validatePresentation(item.presentation);if(documentValue.state==="accepted"&&(!item.reviewed||!finalChoices.has(choice)))throw Error("Accepted содержит незавершённую строку "+item.asset_id)}return true}
function exportJson(documentState){const documentValue=decisionDocument(documentState),blob=new Blob([JSON.stringify(documentValue,null,2)+"\n"],{type:"application/json"}),link=el("a");link.href=URL.createObjectURL(blob);link.download=`artview-decisions.${documentState}.json`;link.click();URL.revokeObjectURL(link.href)}
function applyFilter(){const filter=document.getElementById("filter").value,query=document.getElementById("search").value.trim().toLowerCase();document.querySelectorAll(".row").forEach(card=>{const row=manifest.rows.find(value=>value.asset_id===card.dataset.asset),current=state[row.asset_id],matches=filter==="all"||(filter==="unreviewed"&&!current.reviewed)||(filter==="unresolved"&&!finalChoices.has(current.binary.choice))||(filter==="direct"&&row.alternatives.some(item=>directKinds.has(item.kind)))||(filter==="derived"&&card.dataset.kinds.includes("derived_page_crop"))||(filter==="full"&&card.dataset.kinds.includes("full_page_render"))||(filter==="production-excluded"&&card.dataset.production==="excluded")||(filter===card.dataset.group)||(filter==="warning"&&card.dataset.warning==="yes");card.classList.toggle("hidden",!matches||(query&&!card.dataset.search.includes(query)))})}
function render(){const root=document.getElementById("rows");root.textContent="";manifest.rows.forEach((row,index)=>root.append(buildRow(row,index)));updateProgress();applyFilter()}
try{const saved=JSON.parse(localStorage.getItem(storageKey)||"{}");for(const row of manifest.rows)state[row.asset_id]=normalizeState(row,saved[row.asset_id])}catch(_error){for(const row of manifest.rows)state[row.asset_id]=defaultState(row)}
document.getElementById("exportDraft").onclick=()=>exportJson("draft");document.getElementById("exportAccepted").onclick=()=>exportJson("accepted");document.getElementById("importButton").onclick=()=>document.getElementById("importFile").click();document.getElementById("importFile").onchange=async event=>{try{const documentValue=JSON.parse(await event.target.files[0].text());validateImport(documentValue);for(const item of documentValue.decisions)state[item.asset_id]=normalizeState(manifest.rows.find(row=>row.asset_id===item.asset_id),item);localStorage.setItem(storageKey,JSON.stringify(state));document.getElementById("message").className="ok";document.getElementById("message").textContent="Импорт принят";render()}catch(error){document.getElementById("message").className="error";document.getElementById("message").textContent="Импорт отклонён: "+error.message}finally{event.target.value=""}};document.getElementById("filter").onchange=applyFilter;document.getElementById("search").oninput=applyFilter;render();
</script></body></html>'''
    return (
        template.replace("__MANIFEST__", payload)
        .replace("__MANIFEST_SHA__", manifest_sha.upper())
        .replace("__DECISION_SCHEMA__", DECISION_SCHEMA)
        .replace("__EXPECTED_BINDINGS__", expected_bindings)
    )


def _v3_exact(value: object, keys: set[str], label: str) -> dict[str, Any]:
    if not isinstance(value, dict) or set(value) != keys:
        raise ValueError(f"{label} closed schema mismatch")
    return value


def _v3_safe_path(value: object, label: str) -> str:
    if not isinstance(value, str) or V3_SAFE_PATH_RE.fullmatch(value) is None:
        raise ValueError(f"{label} must be a normalized portable relative path")
    return value


def _v3_resolve(profile_root: Path, record: object, label: str) -> Path:
    row = _v3_exact(record, {"path", "bytes", "sha256"}, label)
    relative_value = _v3_safe_path(row["path"], label)
    relative = Path(*relative_value.split("/"))
    authority = profile_root.resolve()
    lexical = authority / relative
    current = lexical
    while True:
        try:
            current.relative_to(authority)
        except ValueError as error:
            raise ValueError(f"{label} escapes profile authority root") from error
        if current.exists() and _v3_is_reparse(current):
            raise ValueError(f"{label} contains an existing reparse path")
        if current == authority:
            break
        current = current.parent
    path = lexical.resolve()
    try:
        path.relative_to(authority)
    except ValueError as error:
        raise ValueError(f"{label} escapes profile authority root") from error
    if not path.is_file() or path.is_symlink() or path.stat().st_size != row["bytes"] or sha256_file(path) != row["sha256"]:
        raise ValueError(f"{label} identity mismatch")
    return path


def _v3_is_reparse(path: Path) -> bool:
    try:
        metadata = os.lstat(path)
    except OSError:
        return False
    return stat.S_ISLNK(metadata.st_mode) or bool(
        getattr(metadata, "st_file_attributes", 0) & getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0x400)
    )


def _v3_output_root(authority_root: Path, value: os.PathLike[str] | str, label: str, *, must_exist: bool) -> Path:
    raw = _v3_safe_path(os.fspath(value), label)
    relative = Path(*raw.split("/"))
    authority = authority_root.resolve()
    lexical = authority / relative
    if not lexical.parent.is_dir():
        raise ValueError(f"{label} parent must already exist")
    current = lexical.parent
    chain: list[Path] = []
    while True:
        try:
            current.relative_to(authority)
        except ValueError as error:
            raise ValueError(f"{label} escapes authority root") from error
        chain.append(current)
        if current == authority:
            break
        current = current.parent
    if any(component.exists() and _v3_is_reparse(component) for component in chain):
        raise ValueError(f"{label} contains an existing reparse path")
    if _v3_is_reparse(lexical):
        raise ValueError(f"{label} is an existing reparse path")
    resolved = lexical.resolve()
    try:
        resolved.relative_to(authority)
    except ValueError as error:
        raise ValueError(f"{label} escapes authority root") from error
    if must_exist:
        if not resolved.is_dir() or _v3_is_reparse(resolved):
            raise ValueError(f"{label} must be an existing non-reparse directory")
    elif resolved.exists():
        raise FileExistsError(f"{label} must be absent")
    return resolved


def _v3_validate_seal(value: dict[str, Any], key: str, label: str) -> None:
    digest = value.get(key)
    if not isinstance(digest, str) or not re.fullmatch(r"[0-9A-F]{64}", digest):
        raise ValueError(f"{label} seal missing")
    unsigned = {name: item for name, item in value.items() if name != key}
    if sha256_bytes(canonical_json(unsigned).encode("utf-8")) != digest:
        raise ValueError(f"{label} seal mismatch")


def _v3_graph_index(profile_root: Path, paths: dict[str, Path]) -> dict[tuple[Path, int, str], list[dict[str, Any]]]:
    index: dict[tuple[Path, int, str], list[dict[str, Any]]] = {}
    sources = (
        ("master_ru_asset_manifest", paths["master_ru_asset_manifest"], "assets"),
        ("reconstruction_inventory", paths["reconstruction_inventory"], "artifacts"),
    )
    for source, document_path, collection in sources:
        document = read_json(document_path)
        rows = document.get(collection)
        if not isinstance(rows, list):
            raise ValueError(f"ArtView source graph {source} lacks {collection}")
        for position, row in enumerate(rows):
            if not isinstance(row, dict) or not {"path", "bytes", "sha256"}.issubset(row):
                raise ValueError(f"ArtView source graph {source} row {position} lacks exact identity")
            record = {key: row[key] for key in ("path", "bytes", "sha256")}
            resolved = _v3_resolve(document_path.parent, record, f"ArtView source graph {source} row {position}")
            role = row.get("role", row.get("kind"))
            if not isinstance(role, str) or not role:
                role = "asset" if source == "master_ru_asset_manifest" else "artifact"
            key = (resolved, int(record["bytes"]), str(record["sha256"]))
            index.setdefault(key, []).append({"source": source, "role": role, "identity": record})
    return index


def _v3_bound_image(
    profile_root: Path,
    record: object,
    label: str,
    graph_index: dict[tuple[Path, int, str], list[dict[str, Any]]],
) -> tuple[Path, list[dict[str, Any]]]:
    path = _v3_image(profile_root, record, label)
    row = record if isinstance(record, dict) else {}
    memberships = graph_index.get((path, int(row.get("bytes", -1)), str(row.get("sha256", ""))))
    if not memberships:
        raise ValueError(f"{label} is outside exact bound source graph")
    return path, memberships


def _v3_profile(profile_path: Path) -> tuple[dict[str, Any], dict[str, Path], dict[tuple[Path, int, str], list[dict[str, Any]]]]:
    profile = read_json(profile_path)
    _v3_exact(profile, {"schema", "scenario_id", "output_root", "inputs", "excluded_source_pages", "rows"}, "ArtView v3 profile")
    if profile["schema"] != PROFILE_SCHEMA_V3 or not re.fullmatch(r"[a-z0-9][a-z0-9._-]*", str(profile["scenario_id"])):
        raise ValueError("invalid ArtView v3 profile")
    inputs = _v3_exact(profile["inputs"], {"master_ru", "master_ru_acceptance", "master_ru_asset_manifest", "reconstruction_inventory"}, "ArtView v3 inputs")
    paths = {name: _v3_resolve(profile_path.parent, record, f"ArtView input {name}") for name, record in inputs.items()}
    acceptance = read_json(paths["master_ru_acceptance"])
    _v3_exact(
        acceptance,
        {"schema", "scenario_id", "artifact_kind", "candidate", "producer_stage", "evidence", "decision", "decision_at_utc", "user_decision_reference", "recorder_role", "receipt_sha256"},
        "MASTER_RU acceptance",
    )
    _v3_validate_seal(acceptance, "receipt_sha256", "MASTER_RU acceptance")
    if acceptance.get("schema") != "kb_creator.artifact_acceptance.v1" or acceptance.get("scenario_id") != profile["scenario_id"] or acceptance.get("artifact_kind") != "master_ru" or acceptance.get("decision") != "accepted" or acceptance.get("recorder_role") != "main_orchestrator" or not isinstance(acceptance.get("decision_at_utc"), str) or not acceptance["decision_at_utc"].strip() or not isinstance(acceptance.get("user_decision_reference"), str) or not acceptance["user_decision_reference"].strip():
        raise ValueError("ArtView v3 requires exact accepted MASTER_RU")
    if acceptance.get("candidate") != profile["inputs"]["master_ru"]:
        raise ValueError("MASTER_RU acceptance candidate mismatch")
    _v3_resolve(profile_path.parent, acceptance["producer_stage"], "MASTER_RU producer stage")
    evidence = acceptance["evidence"]
    if not isinstance(evidence, list) or not evidence:
        raise ValueError("MASTER_RU acceptance evidence must be nonempty")
    for position, record in enumerate(evidence):
        _v3_resolve(profile_path.parent, record, f"MASTER_RU acceptance evidence {position}")
    if len({canonical_json(record) for record in evidence}) != len(evidence):
        raise ValueError("MASTER_RU acceptance evidence must be unique")
    excluded = profile["excluded_source_pages"]
    if not isinstance(excluded, list) or len(excluded) != len(set(excluded)) or any(not isinstance(page, int) or isinstance(page, bool) or page < 1 for page in excluded):
        raise ValueError("invalid excluded source pages")
    rows = profile["rows"]
    if not isinstance(rows, list) or not rows:
        raise ValueError("ArtView v3 profile has no review rows")
    graph_index = _v3_graph_index(profile_path.parent, paths)
    asset_ids: set[str] = set(); candidate_ids: set[str] = set()
    for row in rows:
        _v3_exact(row, {"asset_id", "anchor", "label", "source_page", "group", "current", "context", "alternatives", "presentation_defaults"}, "ArtView v3 row")
        asset_id = row["asset_id"]
        if not isinstance(asset_id, str) or not re.fullmatch(r"[a-z0-9][a-z0-9._-]*", asset_id) or asset_id in asset_ids or row["source_page"] in excluded:
            raise ValueError("invalid or duplicate ArtView v3 asset row")
        asset_ids.add(asset_id)
        _v3_bound_image(profile_path.parent, row["current"], f"current image {asset_id}", graph_index)
        _v3_bound_image(profile_path.parent, row["context"], f"context image {asset_id}", graph_index)
        if not isinstance(row["alternatives"], list):
            raise ValueError("ArtView alternatives must be a list")
        for candidate in row["alternatives"]:
            _v3_exact(candidate, {"candidate_id", "kind", "binary"}, "ArtView v3 candidate")
            if not isinstance(candidate["candidate_id"], str) or not re.fullmatch(r"[a-z0-9][a-z0-9._-]*", candidate["candidate_id"]) or candidate["candidate_id"] in candidate_ids:
                raise ValueError("invalid or duplicate ArtView v3 candidate")
            candidate_ids.add(candidate["candidate_id"])
            _v3_bound_image(profile_path.parent, candidate["binary"], f"candidate image {candidate['candidate_id']}", graph_index)
        if not isinstance(row["presentation_defaults"], dict) or set(row["presentation_defaults"]) != {"width_percent", "alignment", "wrap_text", "wrap_tables"} or presentation_findings(row["presentation_defaults"], asset_id):
            raise ValueError("invalid ArtView v3 presentation defaults")
    return profile, paths, graph_index


def _v3_image(root: Path, record: object, label: str) -> Path:
    row = _v3_exact(record, {"path", "bytes", "sha256", "media_type", "dimensions"}, label)
    path = _v3_resolve(root, {key: row[key] for key in ("path", "bytes", "sha256")}, label)
    with Image.open(path) as image:
        image.load(); dimensions = {"width": image.width, "height": image.height}
        media_type = Image.MIME.get(image.format or "") or ("image/jpeg" if path.suffix.lower() in {".jpg", ".jpeg"} else "image/png")
    if row["dimensions"] != dimensions or row["media_type"] != media_type:
        raise ValueError(f"{label} media identity mismatch")
    return path


def _v3_review_html(manifest: dict[str, Any], manifest_sha: str) -> str:
    payload = canonical_json(manifest).replace("&", "\\u0026").replace("<", "\\u003c").replace(">", "\\u003e")
    bindings = canonical_json(decision_bindings(manifest, manifest_sha))
    template = r'''<!doctype html>
<html lang="ru"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>ArtView v3</title>
<style>
:root{--bg:#0f172a;--panel:#1e293b;--panel2:#111827;--muted:#94a3b8;--line:#475569;--accent:#8b5cf6;--ok:#34d399;--warn:#fbbf24;--bad:#fb7185}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:#f8fafc;font:15px/1.45 system-ui,sans-serif}header{position:sticky;top:0;z-index:10;padding:14px 20px;background:#0f172aee;border-bottom:1px solid var(--line);backdrop-filter:blur(8px)}
h1{font-size:22px;margin:0 0 4px}.sub,.meta{color:var(--muted)}.toolbar{display:flex;gap:9px;align-items:center;flex-wrap:wrap;margin-top:10px}button,input,select{font:inherit}button{padding:7px 11px;border:1px solid #6d28d9;border-radius:7px;background:#4c1d95;color:#fff;cursor:pointer}button.secondary{background:#1f2937;border-color:#64748b}button:disabled{opacity:.42;cursor:not-allowed}
main{max-width:1600px;margin:auto;padding:18px}.row{margin:0 0 20px;padding:14px;border:1px solid var(--line);border-radius:11px;background:var(--panel)}.row.reviewed{border-color:#15803d}.row h2{margin:0 0 4px;font-size:19px}.row-head{display:flex;justify-content:space-between;gap:12px}.status{color:var(--warn)}.row.reviewed .status{color:var(--ok)}code{overflow-wrap:anywhere;color:#cbd5e1}
.images{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:10px;margin:12px 0}.image-card{display:block;min-width:0;padding:9px;border:2px solid var(--line);border-radius:8px;background:var(--panel2)}.image-card.selectable{cursor:pointer;transition:border-color .15s,box-shadow .15s,transform .15s}.image-card.selectable:hover{border-color:#a78bfa;transform:translateY(-1px)}.image-card.selectable:focus-within{outline:2px solid #c4b5fd;outline-offset:2px}.image-card.selected,.image-card.selected:focus-within{border-color:var(--ok);outline-color:var(--ok);box-shadow:0 0 0 2px #34d39955}.image-card h3{margin:0 0 7px;font-size:14px}.image-card.selected h3{color:var(--ok)}.image-card img{display:block;width:100%;height:250px;object-fit:contain;background:#fff}.image-card .facts{margin-top:5px;color:var(--muted);font:12px/1.35 ui-monospace,monospace;overflow-wrap:anywhere}.sr-only{position:absolute;width:1px;height:1px;padding:0;margin:-1px;overflow:hidden;clip:rect(0,0,0,0);white-space:nowrap;border:0}
.decision-grid{display:block}.controls{padding:12px;border:1px solid var(--line);border-radius:8px;background:var(--panel2)}fieldset{margin:0;padding:10px;border:1px solid var(--line);border-radius:7px}legend{padding:0 5px;color:#ddd6fe}.presentation{display:grid;grid-template-columns:repeat(2,minmax(170px,1fr));gap:9px}.control{display:flex;gap:8px;align-items:center}.control input[type=number],.control select{max-width:110px;padding:5px;background:#0b1220;color:#fff;border:1px solid #64748b;border-radius:5px}.error{color:var(--bad)}
dialog{width:min(680px,calc(100vw - 32px));padding:0;border:1px solid var(--line);border-radius:11px;background:var(--panel);color:#f8fafc;box-shadow:0 24px 70px #000b}dialog::backdrop{background:#020617cc}.import-shell{padding:18px}.import-shell h2{margin:0 0 8px}.import-shell p{margin:6px 0;color:var(--muted)}.import-file{display:block;width:100%;margin:14px 0;padding:10px;border:1px solid var(--line);border-radius:7px;background:var(--panel2);color:#fff}.import-summary{min-height:72px;margin:12px 0;padding:10px;border:1px solid var(--line);border-radius:7px;background:#0b1220;white-space:pre-line}.import-summary.ok{border-color:#15803d;color:#bbf7d0}.import-summary.warning{border-color:#d97706;color:#fde68a}.import-summary.error{border-color:#be123c;color:#fecdd3}.dialog-actions{display:flex;justify-content:flex-end;gap:9px;margin-top:14px}
@media(max-width:1000px){header{position:static}.images{grid-template-columns:1fr 1fr}}@media(max-width:650px){.images,.presentation{grid-template-columns:1fr}}
</style></head><body>
<header><h1 id="title">ArtView v3</h1><div class="sub">Кликните по нужному варианту изображения: выбранная карточка будет обведена зелёным, а строка получит статус «Выбор сделан». При необходимости настройте параметры представления. Ничего не применяется автоматически.</div>
<div class="toolbar"><button id="exportDraft" class="secondary">Экспорт черновика</button><button id="exportAccepted" disabled>Экспорт принятого JSON</button><button id="importConfig" class="secondary">Импорт прошлого JSON</button><span id="progress"></span><span id="message" aria-live="polite"></span></div></header>
<main id="rows"></main>
<dialog id="importDialog" aria-labelledby="importTitle"><form method="dialog" class="import-shell"><h2 id="importTitle">Импорт прошлого конфига ArtView</h2><p>Точный JSON текущего кандидата восстанавливает выбор и отметки проверки. JSON от прежнего кандидата переносит только совместимые решения; отметки проверки сбрасываются и требуют нового клика по каждому выбранному варианту.</p><input id="importFile" class="import-file" type="file" accept=".json,application/json"><div id="importSummary" class="import-summary" aria-live="polite">Выберите экспортированный ArtView JSON.</div><div class="dialog-actions"><button id="cancelImport" type="button" class="secondary">Отмена</button><button id="applyImport" type="button" disabled>Применить импорт</button></div></form></dialog>
<script type="application/json" id="manifest">__MANIFEST__</script>
<script type="application/json" id="bindings">__BINDINGS__</script>
<script>
"use strict";
const manifest=JSON.parse(document.getElementById("manifest").textContent);
const expectedBindings=JSON.parse(document.getElementById("bindings").textContent);
const decisionSchema=manifest.decision_contract.schema;
const finalChoices=new Set(["keep_current","use_candidate","exclude"]);
const alignmentLabels={left:"Слева",center:"По центру",right:"Справа"};
const decisions=new Map(manifest.rows.map(row=>[row.asset_id,{asset_id:row.asset_id,binary:{choice:null,candidate_id:null},presentation:{...row.presentation_defaults},reviewed:false,notes:""}]));
const rowRefs=new Map();
const root=document.getElementById("rows"),acceptedButton=document.getElementById("exportAccepted"),progress=document.getElementById("progress"),message=document.getElementById("message"),importDialog=document.getElementById("importDialog"),importFile=document.getElementById("importFile"),importSummary=document.getElementById("importSummary"),applyImportButton=document.getElementById("applyImport");
let pendingImport=null;
document.title=manifest.scenario_id+" - ArtView v3";
document.getElementById("title").textContent=manifest.scenario_id+" - ArtView v3";
const el=(tag,cls,text)=>{const node=document.createElement(tag);if(cls)node.className=cls;if(text!==undefined)node.textContent=text;return node};
function imageCard(title,item,alt,selection=null){const card=el(selection?"label":"section","image-card"+(selection?" selectable":"")),heading=el("h3","",title),image=el("img");if(selection){const input=el("input","sr-only");input.type="radio";input.name="image-choice-"+selection.row.asset_id;input.dataset.choice=selection.choice;input.dataset.candidateId=selection.candidateId||"";input.setAttribute("aria-label",title);input.addEventListener("change",()=>selectImage(selection.row,selection.current,selection.choice,selection.candidateId));card.append(input)}image.loading="lazy";image.src=item.path;image.alt=alt;card.append(heading,image,el("div","facts",`${item.dimensions.width}x${item.dimensions.height} · ${item.bytes} bytes · ${item.sha256}`));return card}
function candidateMap(row){return new Map(row.alternatives.map(item=>[item.candidate_id,item]))}
function binaryIsFinal(row,current){if(!finalChoices.has(current.binary.choice))return false;if(current.binary.choice!=="use_candidate")return current.binary.candidate_id===null;return candidateMap(row).has(current.binary.candidate_id)}
function presentationIsValid(value){return Number.isInteger(value.width_percent)&&value.width_percent>=10&&value.width_percent<=100&&["left","center","right"].includes(value.alignment)&&typeof value.wrap_text==="boolean"&&typeof value.wrap_tables==="boolean"&&(!value.wrap_tables||value.wrap_text)&&(value.alignment!=="center"||(!value.wrap_text&&!value.wrap_tables))}
function unresolvedAssetIds(){return manifest.rows.filter(row=>{const current=decisions.get(row.asset_id);return !current.reviewed||!binaryIsFinal(row,current)||!presentationIsValid(current.presentation)}).map(row=>row.asset_id)}
function isAcceptedReady(){return unresolvedAssetIds().length===0}
function selectImage(row,current,choice,candidateId){if(!row.allowed_binary_decisions.includes(choice))return;current.binary={choice,candidate_id:candidateId};current.reviewed=true;refresh()}
function refresh(){let reviewedCount=0;for(const row of manifest.rows){const current=decisions.get(row.asset_id),refs=rowRefs.get(row.asset_id),ready=binaryIsFinal(row,current)&&presentationIsValid(current.presentation)&&current.reviewed;for(const input of refs.imageChoices){const selected=current.binary.choice===input.dataset.choice&&(current.binary.candidate_id||"")===input.dataset.candidateId;input.checked=selected;input.closest(".image-card").classList.toggle("selected",selected)}refs.article.classList.toggle("reviewed",ready);refs.status.textContent=ready?"Выбор сделан":"Выберите вариант";if(current.reviewed)reviewedCount++}acceptedButton.disabled=!isAcceptedReady();progress.textContent=`Выбрано ${reviewedCount}/${manifest.rows.length}`}
function renderRow(row){const current=decisions.get(row.asset_id),article=el("article","row"),head=el("div","row-head"),identity=el("div"),status=el("strong","status","Решение не финально");identity.append(el("h2","",row.label),el("code","",row.asset_id),el("div","meta",`Страница ${row.source_page}; группа ${row.group}`));head.append(identity,status);article.append(head);
const images=el("div","images");images.append(imageCard("Текущий файл",row.current,row.label,{row,current,choice:"keep_current",candidateId:null}),imageCard("Контекст",row.context,`Контекст страницы ${row.source_page}`));if(row.allowed_binary_decisions.includes("use_candidate")){for(const candidate of row.alternatives)images.append(imageCard(`Кандидат ${candidate.candidate_id} (${candidate.kind})`,candidate.binary,candidate.candidate_id,{row,current,choice:"use_candidate",candidateId:candidate.candidate_id}))}article.append(images);
const grid=el("div","decision-grid");
const presentationBox=el("section","controls"),presentationField=el("fieldset"),presentationLegend=el("legend","","Параметры представления"),presentation=el("div","presentation");presentationField.append(presentationLegend,presentation);
const widthLabel=el("label","control","Ширина, %"),width=el("input");width.type="number";width.min="10";width.max="100";width.step="1";width.value=String(current.presentation.width_percent);width.addEventListener("input",()=>{current.presentation.width_percent=Number(width.value);refresh()});widthLabel.append(width);presentation.append(widthLabel);
const wrapInputs={};const alignmentLabel=el("label","control","Выравнивание"),alignment=el("select");for(const value of ["left","center","right"]){const option=el("option","",alignmentLabels[value]);option.value=value;option.selected=current.presentation.alignment===value;alignment.append(option)}alignment.addEventListener("change",()=>{current.presentation.alignment=alignment.value;if(alignment.value==="center"&&(current.presentation.wrap_text||current.presentation.wrap_tables)){current.presentation.wrap_text=false;current.presentation.wrap_tables=false;wrapInputs.wrap_text.checked=false;wrapInputs.wrap_tables.checked=false;message.textContent="При выравнивании по центру обтекание отключено."}refresh()});alignmentLabel.append(alignment);presentation.append(alignmentLabel);
for(const [key,labelText] of [["wrap_text","Обтекать текстом"],["wrap_tables","Обтекать таблицами"]]){const label=el("label","control"),input=el("input");wrapInputs[key]=input;input.type="checkbox";input.checked=current.presentation[key];input.addEventListener("change",()=>{if(input.checked&&current.presentation.alignment==="center"){current.presentation.alignment="right";alignment.value="right";message.textContent="Для обтекания выравнивание автоматически изменено на «Справа»."}current.presentation[key]=input.checked;if(key==="wrap_tables"&&input.checked){current.presentation.wrap_text=true;wrapInputs.wrap_text.checked=true}if(key==="wrap_text"&&!input.checked){current.presentation.wrap_tables=false;wrapInputs.wrap_tables.checked=false}refresh()});label.append(input,document.createTextNode(labelText));presentation.append(label)}presentationBox.append(presentationField);
grid.append(presentationBox);article.append(grid);const imageChoices=Array.from(article.querySelectorAll('input[name^="image-choice-"]'));rowRefs.set(row.asset_id,{article,status,imageChoices});root.append(article)}
function canonicalJson(value){if(value===null||typeof value!=="object")return JSON.stringify(value);if(Array.isArray(value))return "["+value.map(canonicalJson).join(",")+"]";return "{"+Object.keys(value).sort().map(key=>JSON.stringify(key)+":"+canonicalJson(value[key])).join(",")+"}"}
async function sha256Hex(text){const bytes=new TextEncoder().encode(text),digest=await crypto.subtle.digest("SHA-256",bytes);return Array.from(new Uint8Array(digest),byte=>byte.toString(16).padStart(2,"0")).join("").toUpperCase()}
function buildDecisionDocument(accepted){const rows=manifest.rows.map(row=>{const current=decisions.get(row.asset_id);return {asset_id:row.asset_id,binary:{choice:current.binary.choice,candidate_id:current.binary.candidate_id},presentation:{width_percent:current.presentation.width_percent,alignment:current.presentation.alignment,wrap_text:current.presentation.wrap_text,wrap_tables:current.presentation.wrap_tables},reviewed:current.reviewed,notes:""}}),unresolved=unresolvedAssetIds();if(accepted&&unresolved.length)throw new Error("Accepted export requires a valid image selection for every row");return {schema:decisionSchema,scenario_id:manifest.scenario_id,state:accepted?"accepted":"draft",bindings:{...expectedBindings},decisions:rows,review:{state:accepted?"closed":"open",reviewed_count:rows.filter(row=>row.reviewed).length,unresolved_asset_ids:unresolved}}}
async function sealDocument(documentValue){return {...documentValue,decisions_sha256:await sha256Hex(canonicalJson(documentValue))}}
function hasExactKeys(value,keys){return value&&typeof value==="object"&&!Array.isArray(value)&&Object.keys(value).sort().join("\n")===[...keys].sort().join("\n")}
function importedRowState(row,item,preserveReviewed){if(!hasExactKeys(item,["asset_id","binary","presentation","reviewed","notes"]))throw new Error("Неверная структура решения "+row.asset_id);if(!hasExactKeys(item.binary,["choice","candidate_id"]))throw new Error("Неверная структура binary "+row.asset_id);if(!hasExactKeys(item.presentation,["width_percent","alignment","wrap_text","wrap_tables"]))throw new Error("Неверная структура presentation "+row.asset_id);const choice=item.binary.choice,candidateId=item.binary.candidate_id;if(choice!==null&&!row.allowed_binary_decisions.includes(choice))throw new Error("Недопустимое решение "+row.asset_id);if(choice==="use_candidate"&&!candidateMap(row).has(candidateId))throw new Error("Кандидат больше не существует: "+row.asset_id);if(choice!=="use_candidate"&&candidateId!==null)throw new Error("Лишний candidate_id: "+row.asset_id);if(typeof item.reviewed!=="boolean"||typeof item.notes!=="string")throw new Error("Неверные reviewed/notes: "+row.asset_id);if(!presentationIsValid(item.presentation))throw new Error("Неверные параметры представления: "+row.asset_id);return {asset_id:row.asset_id,binary:{choice,candidate_id:candidateId},presentation:{width_percent:item.presentation.width_percent,alignment:item.presentation.alignment,wrap_text:item.presentation.wrap_text,wrap_tables:item.presentation.wrap_tables},reviewed:preserveReviewed&&item.reviewed,notes:""}}
async function prepareImport(documentValue){if(!hasExactKeys(documentValue,["schema","scenario_id","state","bindings","decisions","review","decisions_sha256"]))throw new Error("Документ не соответствует закрытой схеме ArtView");if(documentValue.schema!==decisionSchema||documentValue.scenario_id!==manifest.scenario_id)throw new Error("Неверная схема или scenario_id");if(!["draft","accepted"].includes(documentValue.state)||!Array.isArray(documentValue.decisions))throw new Error("Неверное состояние или список решений");const unsigned={...documentValue};delete unsigned.decisions_sha256;if(typeof documentValue.decisions_sha256!=="string"||documentValue.decisions_sha256!==await sha256Hex(canonicalJson(unsigned)))throw new Error("Контрольная сумма JSON не совпадает");const exactBindings=canonicalJson(documentValue.bindings)===canonicalJson(expectedBindings),currentRows=new Map(manifest.rows.map(row=>[row.asset_id,row])),seen=new Set(),next=new Map(manifest.rows.map(row=>[row.asset_id,{asset_id:row.asset_id,binary:{choice:null,candidate_id:null},presentation:{...row.presentation_defaults},reviewed:false,notes:""}])),skipped=[];let imported=0;for(const item of documentValue.decisions){const assetId=item&&item.asset_id,row=currentRows.get(assetId);if(typeof assetId!=="string"||seen.has(assetId)){if(exactBindings)throw new Error("Неизвестный или повторный asset_id");skipped.push(String(assetId||"<empty>")+": повтор/неверный id");continue}seen.add(assetId);if(!row){if(exactBindings)throw new Error("Неизвестный asset_id: "+assetId);skipped.push(assetId+": строки больше нет");continue}try{const importedState=importedRowState(row,item,exactBindings);if(exactBindings&&documentValue.state==="accepted"&&(!importedState.reviewed||!binaryIsFinal(row,importedState)))throw new Error("Accepted содержит незавершённую строку "+assetId);next.set(assetId,importedState);imported++}catch(error){if(exactBindings)throw error;skipped.push(assetId+": "+error.message)}}for(const row of manifest.rows)if(!seen.has(row.asset_id))skipped.push(row.asset_id+": отсутствует в прошлом JSON");if(exactBindings&&(imported!==manifest.rows.length||documentValue.decisions.length!==manifest.rows.length))throw new Error("Точный импорт должен содержать все строки");if(!exactBindings&&imported===0)throw new Error("Нет совместимых решений для переноса");return {states:next,exactBindings,imported,skipped,sourceState:documentValue.state}}
function download(documentValue,state){const text=JSON.stringify(documentValue,null,2)+"\n",url=URL.createObjectURL(new Blob([text],{type:"application/json"})),link=document.createElement("a");link.href=url;link.download=`${manifest.scenario_id}.artview-decisions.${state}.json`;document.body.append(link);link.click();link.remove();setTimeout(()=>URL.revokeObjectURL(url),0);return link.download}
async function copyExportLocator(filename){if(!navigator.clipboard||typeof navigator.clipboard.writeText!=="function")return false;try{await navigator.clipboard.writeText(filename);return true}catch(_error){return false}}
async function exportDocument(accepted){message.textContent="";try{if(typeof crypto==="undefined"||!crypto.subtle)throw new Error("Web Crypto is unavailable; serve ArtView from localhost");const documentValue=await sealDocument(buildDecisionDocument(accepted)),filename=download(documentValue,accepted?"accepted":"draft"),copied=await copyExportLocator(filename),label=accepted?"Принятый JSON экспортирован":"Черновик экспортирован";message.textContent=copied?`${label}. Имя файла скопировано: ${filename}. Полный путь определяет браузер и не сообщает странице.`:`${label}: ${filename}. Полный путь определяет браузер; автоматическое копирование имени недоступно.`;message.className=""}catch(error){message.textContent=error.message;message.className="error"}}
function resetImportDialog(){pendingImport=null;importFile.value="";importSummary.textContent="Выберите экспортированный ArtView JSON.";importSummary.className="import-summary";applyImportButton.disabled=true}
document.getElementById("importConfig").addEventListener("click",()=>{resetImportDialog();if(typeof importDialog.showModal==="function")importDialog.showModal();else importDialog.setAttribute("open","")});
document.getElementById("cancelImport").addEventListener("click",()=>importDialog.close());
importFile.addEventListener("change",async()=>{pendingImport=null;applyImportButton.disabled=true;const file=importFile.files&&importFile.files[0];if(!file)return;importSummary.textContent="Проверка "+file.name+"…";importSummary.className="import-summary";try{if(typeof crypto==="undefined"||!crypto.subtle)throw new Error("Web Crypto is unavailable; serve ArtView from localhost");const documentValue=JSON.parse(await file.text()),prepared=await prepareImport(documentValue);pendingImport=prepared;applyImportButton.disabled=false;if(prepared.exactBindings){importSummary.textContent=`Точное совпадение кандидата. Будут восстановлены ${prepared.imported}/${manifest.rows.length} решений и их отметки проверки.`;importSummary.className="import-summary ok"}else{const details=prepared.skipped.length?`\nПропущено: ${prepared.skipped.length}. ${prepared.skipped.slice(0,5).join("; ")}${prepared.skipped.length>5?"; …":""}`:"";importSummary.textContent=`Конфиг от предыдущего кандидата. Переносится ${prepared.imported}/${manifest.rows.length} совместимых решений. Отметки проверки будут сброшены; подтвердите каждый выбор кликом.${details}`;importSummary.className="import-summary warning"}}catch(error){importSummary.textContent="Импорт отклонён: "+error.message;importSummary.className="import-summary error"}});
applyImportButton.addEventListener("click",()=>{if(!pendingImport)return;for(const [assetId,value] of pendingImport.states)decisions.set(assetId,value);const exact=pendingImport.exactBindings,count=pendingImport.imported;refresh();importDialog.close();message.className="";message.textContent=exact?`Импортировано ${count} точных решений.`:`Перенесено ${count} совместимых решений. Подтвердите каждый выбор кликом.`;pendingImport=null});
document.getElementById("exportDraft").addEventListener("click",()=>exportDocument(false));acceptedButton.addEventListener("click",()=>exportDocument(true));for(const row of manifest.rows)renderRow(row);refresh();window.artviewV3={manifest,expectedBindings,decisions,buildDecisionDocument,sealDocument,isAcceptedReady,prepareImport};
</script></body></html>'''
    return template.replace("__MANIFEST__", payload).replace("__BINDINGS__", bindings)


def build_v3(profile_path: Path, force: bool, output_root_arg: Path | None = None) -> dict[str, Any]:
    profile, input_paths, graph_index = _v3_profile(profile_path)
    if force:
        raise FileExistsError("ArtView v3 output must be absent; --force is compatibility-only for v2")
    target_root = _v3_output_root(profile_path.parent, output_root_arg if output_root_arg is not None else profile["output_root"], "ArtView v3 output", must_exist=False)
    stage = Path(tempfile.mkdtemp(prefix=target_root.name + ".tmp-", dir=target_root.parent)); candidate_root = stage / "candidate"
    try:
        rows = []
        for source_row in profile["rows"]:
            asset_id = source_row["asset_id"]; current_source, current_membership = _v3_bound_image(profile_path.parent, source_row["current"], f"current image {asset_id}", graph_index)
            current_rel = f"assets/current/{asset_id}{current_source.suffix.lower()}"; current_target = candidate_root / current_rel; current_target.parent.mkdir(parents=True, exist_ok=True); shutil.copyfile(current_source, current_target)
            context_source, context_membership = _v3_bound_image(profile_path.parent, source_row["context"], f"context image {asset_id}", graph_index)
            context_rel = f"context/{asset_id}{context_source.suffix.lower()}"; context_target = candidate_root / context_rel; context_target.parent.mkdir(parents=True, exist_ok=True); shutil.copyfile(context_source, context_target)
            alternatives = []
            for source_candidate in source_row["alternatives"]:
                candidate_id = source_candidate["candidate_id"]; binary_source, binary_membership = _v3_bound_image(profile_path.parent, source_candidate["binary"], f"candidate image {candidate_id}", graph_index)
                relative = f"assets/candidates/{candidate_id}{binary_source.suffix.lower()}"; target = candidate_root / relative; target.parent.mkdir(parents=True, exist_ok=True); shutil.copyfile(binary_source, target)
                alternatives.append({"candidate_id": candidate_id, "kind": source_candidate["kind"], "binary": {**image_record(target, relative), "source_graph_membership": binary_membership}})
            rows.append({"asset_id": asset_id, "anchor": source_row["anchor"], "label": source_row["label"], "source_page": source_row["source_page"], "group": source_row["group"], "current": {**image_record(current_target, current_rel), "source_graph_membership": current_membership}, "context": {**image_record(context_target, context_rel), "source_graph_membership": context_membership}, "alternatives": alternatives, "allowed_binary_decisions": ["keep_current", *(["use_candidate"] if alternatives else []), "exclude", "needs_manual_work", "reopen_masters"], "presentation_defaults": source_row["presentation_defaults"]})
        inventory_doc, inventory_sha = inventory(candidate_root)
        write_json(candidate_root / "candidate_files.inventory.json", {"schema": "kb_creator.scenario_artview_candidate_files.v1", **inventory_doc})
        bindings = {"profile": file_record(profile_path, profile_path.name), **{name: file_record(path, profile["inputs"][name]["path"]) for name, path in input_paths.items()}}
        manifest = {"schema": CANDIDATE_SCHEMA_V3, "scenario_id": profile["scenario_id"], "state": "candidate_needs_user_decisions", "bindings": bindings, "derived_expected": {"review_rows": len(rows), "alternative_binaries": sum(len(row["alternatives"]) for row in rows), "portable_binaries": sum(2 + len(row["alternatives"]) for row in rows), "source_pages": len({row["source_page"] for row in rows}), "excluded_source_pages": list(profile["excluded_source_pages"])}, "rows": rows, "candidate_files_inventory_sha256": inventory_sha, "decision_contract": {"schema": DECISION_SCHEMA_V3, "binding_sources": ["profile", "master_ru", "master_ru_acceptance", "master_ru_asset_manifest", "reconstruction_inventory"], "accepted_requires_all_reviewed": True}}
        manifest_path = candidate_root / "candidate_manifest.json"; write_json(manifest_path, manifest); manifest_sha = sha256_file(manifest_path)
        template = draft_decision_document(manifest, manifest_sha); write_json(candidate_root / "artview-decisions.template.json", template)
        (candidate_root / "artview.html").write_text(_v3_review_html(manifest, manifest_sha), encoding="utf-8", newline="\n")
        qa = {"schema": "kb_creator.scenario_artview_qa.v3", "status": "pass", "candidate_manifest_sha256": manifest_sha, "candidate_files_inventory_sha256": inventory_sha, "derived_expected": manifest["derived_expected"], "checks": {"input_bindings": True, "unique_rows": True, "all_binaries_bound": True, "excluded_pages_absent": True, "decision_template_closed": True}, "findings": []}; write_json(candidate_root / "qa.json", qa)
        bundle_rows = []
        for path in sorted((item for item in candidate_root.rglob("*") if item.is_file() and item.name != "bundle.inventory.json"), key=lambda item: item.relative_to(candidate_root).as_posix()):
            bundle_rows.append(file_record(path, path.relative_to(candidate_root).as_posix()))
        write_json(candidate_root / "bundle.inventory.json", {"schema": "kb_creator.scenario_artview_bundle_inventory.v3", "files": bundle_rows, "sha256": sha256_bytes("".join(f"{row['path']}\t{row['bytes']}\t{row['sha256']}\n" for row in bundle_rows).encode("utf-8"))})
        (stage / "README.md").write_text(f"# {profile['scenario_id']} ArtView v3\n\nState: `candidate_needs_user_decisions`. No decision is accepted automatically.\n", encoding="utf-8", newline="\n")
        os.replace(stage, target_root)
        return {"status": "awaiting_artview_decisions", "output_root": str(target_root), "manifest_sha256": manifest_sha, "inventory_sha256": inventory_sha, "counts": manifest["derived_expected"]}
    except Exception:
        shutil.rmtree(stage, ignore_errors=True)
        raise


def _v4_profile(profile_path: Path) -> tuple[dict[str, Any], dict[str, Path]]:
    """Read the discovery-only successor profile.

    Unlike v3, this profile deliberately has no ``rows`` field: reader-review
    units are derived from the immutable PDF on every invocation.
    """
    profile = read_json(profile_path)
    _v3_exact(profile, {"schema", "scenario_id", "output_root", "inputs", "render"}, "ArtView v4 profile")
    if profile["schema"] != PROFILE_SCHEMA_V4 or not re.fullmatch(r"[a-z0-9][a-z0-9._-]*", str(profile["scenario_id"])):
        raise ValueError("invalid ArtView v4 profile")
    inputs = _v3_exact(profile["inputs"], {"master_ru", "master_ru_acceptance", "master_ru_asset_manifest", "reconstruction_inventory", "source_pdf", "source_identity"}, "ArtView v4 inputs")
    paths = {name: _v3_resolve(profile_path.parent, value, f"ArtView v4 input {name}") for name, value in inputs.items()}
    source_identity = read_json(paths["source_identity"])
    # Source identity documents have evolved; the immutable bytes/hash and page
    # count are the authority needed by visual discovery.
    source = source_identity.get("source", source_identity)
    if not isinstance(source, dict) or source.get("bytes") != paths["source_pdf"].stat().st_size or str(source.get("sha256", "")).upper() != sha256_file(paths["source_pdf"]):
        raise ValueError("ArtView v4 source PDF does not match sealed source identity")
    render = _v3_exact(profile["render"], {"dpi", "format"}, "ArtView v4 render")
    if type(render["dpi"]) is not int or render["dpi"] < 72 or render["format"] not in {"png", "jpeg"}:
        raise ValueError("ArtView v4 render settings are invalid")
    return profile, paths


def _v4_reconstruction_roles(reconstruction_inventory: Path) -> dict[int, str]:
    """Derive source-page semantics from accepted reconstruction decisions.

    The discovery profile is intentionally unable to author this mapping.  A
    reconstruction inventory/manifest is the authority and its sibling
    `decisions/page-NNN.json` records supply the exact reviewed role.
    """
    root = reconstruction_inventory.parent
    inventory = read_json(reconstruction_inventory)
    artifacts = inventory.get("artifacts")
    if inventory.get("schema") != "kb_creator.reconstruction_upstream_inventory.v1" or not isinstance(artifacts, list):
        raise ValueError("ArtView v4 reconstruction inventory is not sealed upstream authority")
    manifests = [row for row in artifacts if isinstance(row, dict) and row.get("role") == "reconstruction_manifest"]
    if len(manifests) != 1:
        raise ValueError("ArtView v4 reconstruction inventory lacks one manifest")
    manifest_path = _v3_resolve(root, {key: manifests[0].get(key) for key in ("path", "bytes", "sha256")}, "ArtView v4 reconstruction manifest")
    manifest = read_json(manifest_path)
    review = manifest.get("review")
    decisions = review.get("decisions") if isinstance(review, dict) else None
    if manifest.get("schema") != "kb_creator.reconstruction_upstream_manifest.v1" or not isinstance(decisions, list) or not decisions:
        raise ValueError("ArtView v4 reconstruction manifest lacks reviewed page decisions")
    roles: dict[int, str] = {}
    for record in decisions:
        path = _v3_resolve(manifest_path.parent, record, "ArtView v4 reconstruction page decision")
        value = read_json(path)
        page = value.get("source_page"); role = value.get("semantic_role")
        if type(page) is not int or page < 1 or not isinstance(role, str) or not role or page in roles:
            raise ValueError("ArtView v4 reconstruction page decision is invalid")
        roles[page] = role
    return roles


def _v4_raw_inventory(pdf: Path) -> tuple[int, list[dict[str, Any]], dict[tuple[int, int], list[tuple[int, str]]]]:
    """Inventory every page XObject occurrence before any content filtering.

    Only masks and image masks receive an automatic technical disposition.  All
    other raster occurrences become components of a page review unit, so a
    decorative-value judgement can never silently remove source content.
    """
    from pypdf import PdfReader

    reader = PdfReader(str(pdf))
    smask_owners: dict[tuple[int, int], list[tuple[int, str, Any]]] = {}
    for page_no, page in enumerate(reader.pages, start=1):
        resources = page.get("/Resources", {})
        xobjects = resources.get("/XObject", {}) if resources else {}
        for _name, ref in xobjects.items():
            obj = ref.get_object()
            smask = obj.get("/SMask") if hasattr(obj, "get") else None
            if smask is not None:
                smask_owners.setdefault((int(getattr(smask, "idnum", 0) or 0), int(getattr(smask, "generation", 0) or 0)), []).append((page_no, str(_name), smask))
    rows: list[dict[str, Any]] = []
    for page_no, page in enumerate(reader.pages, start=1):
        resources = page.get("/Resources", {})
        xobjects = resources.get("/XObject", {}) if resources else {}
        for name, ref in xobjects.items():
            obj = ref.get_object()
            if str(obj.get("/Subtype", "")).lstrip("/") != "Image":
                continue
            object_id = int(getattr(ref, "idnum", 0) or 0); generation = int(getattr(ref, "generation", 0) or 0)
            technical = bool(obj.get("/ImageMask", False)) or (object_id, generation) in smask_owners
            raw = bytes(getattr(obj, "_data", b""))
            rows.append({
                "raw_id": f"page-{page_no:03d}-xref-{object_id}-gen-{generation}-resource-{str(name).lstrip('/').casefold()}", "source_page": page_no,
                "xobject_name": str(name), "object_id": object_id, "generation": generation,
                "width": int(obj.get("/Width", 0) or 0), "height": int(obj.get("/Height", 0) or 0),
                "colorspace": str(obj.get("/ColorSpace", "")).lstrip("/"), "bytes": len(raw),
                "sha256": sha256_bytes(raw), "disposition": "technical_pdf_mechanic" if technical else "component_of_visual_unit",
                "technical_reason": "image_mask" if bool(obj.get("/ImageMask", False)) else "soft_mask" if (object_id, generation) in smask_owners else None,
                "bound_component_of": None,
            })
    by_page_resource = {(row["source_page"], str(row["xobject_name"])): row["raw_id"] for row in rows}
    for row in rows:
        key = (row["object_id"], row["generation"])
        if row["technical_reason"] == "soft_mask":
            owners = smask_owners.get(key, [])
            row["bound_component_of"] = [by_page_resource[(page, name)] for page, name, _ref in owners if (page, name) in by_page_resource]
    # A soft mask is often not exposed as a page resource.  It is still a raw
    # PDF image and must appear in the technical ledger, bound to its base.
    known = {(row["object_id"], row["generation"]) for row in rows}
    for (object_id, generation), owners in smask_owners.items():
        if (object_id, generation) in known:
            continue
        page, name, reference = owners[0]; obj = reference.get_object(); raw = bytes(getattr(obj, "_data", b""))
        rows.append({"raw_id": f"page-{page:03d}-xref-{object_id}-gen-{generation}-soft-mask", "source_page": page, "xobject_name": "SMask", "object_id": object_id, "generation": generation, "width": int(obj.get("/Width", 0) or 0), "height": int(obj.get("/Height", 0) or 0), "colorspace": str(obj.get("/ColorSpace", "")).lstrip("/"), "bytes": len(raw), "sha256": sha256_bytes(raw), "disposition": "technical_pdf_mechanic", "technical_reason": "soft_mask", "bound_component_of": [by_page_resource[(owner_page, owner_name)] for owner_page, owner_name, _ref in owners if (owner_page, owner_name) in by_page_resource]})
    return len(reader.pages), rows, {key: [(page, name) for page, name, _ref in owners] for key, owners in smask_owners.items()}


def _v4_native_image(pdf: Path, raw: dict[str, Any]) -> Image.Image:
    """Decode one non-technical XObject into a portable image unit.

    A decode failure is deliberately fatal: an ordinary object may not vanish
    simply because its filter is inconvenient.
    """
    from pypdf import PdfReader
    reader = PdfReader(str(pdf)); page = reader.pages[int(raw["source_page"]) - 1]
    resource = "/" + str(raw["xobject_name"]).lstrip("/")
    # pypdf's ImageFile path handles FlateDecode and applies SMask alpha.  The
    # raw ledger above retains object/resource identity, so decoded pixels never
    # erase source provenance.
    try:
        image = page.images[resource].image
        image.load()
        return image.convert("RGBA") if image.mode == "RGBA" else image.convert("RGB")
    except Exception as error:
        raise ValueError(f"ArtView v4 cannot decode ordinary raw object {raw['raw_id']}") from error


def _v4_master_assets_by_page(master_ru: Path, asset_manifest: Path) -> dict[int, list[dict[str, Any]]]:
    """Return accepted MASTER_RU image references in marker/source order."""
    manifest = read_json(asset_manifest)
    if manifest.get("schema") != "kb_creator.master_ru_asset_manifest.v1" or not isinstance(manifest.get("assets"), list):
        raise ValueError("ArtView v4 MASTER_RU asset manifest is invalid")
    records: dict[str, dict[str, Any]] = {}
    for record in manifest["assets"]:
        path = _v3_resolve(master_ru.parent, record, "ArtView v4 MASTER_RU asset")
        records[str(record["path"])] = {**record, "absolute_path": path}
    current_page: int | None = None; pages: dict[int, list[dict[str, Any]]] = {}
    for line in master_ru.read_text(encoding="utf-8").splitlines():
        marker = re.fullmatch(r"<!--\s*(?:source-page|pdf-page)-(\d{3})\s*-->", line.strip(), re.I)
        if marker:
            current_page = int(marker.group(1)); continue
        match = re.match(r"!\[[^\]]*\]\(([^)\s]+)(?:\s+[^)]*)?\)", line.strip())
        if match:
            if current_page is None or match.group(1) not in records:
                raise ValueError("ArtView v4 MASTER_RU image reference lacks a page marker or manifest identity")
            pages.setdefault(current_page, []).append(records.pop(match.group(1)))
    if records:
        raise ValueError("ArtView v4 MASTER_RU asset manifest has unreferenced assets")
    return pages


def build_v4(profile_path: Path, pdftoppm_arg: str | None, force: bool, output_root_arg: Path | None = None) -> dict[str, Any]:
    profile, inputs = _v4_profile(profile_path)
    if force:
        raise FileExistsError("ArtView v4 output must be absent; discovery is one-shot")
    target_root = _v3_output_root(profile_path.parent, output_root_arg if output_root_arg is not None else profile["output_root"], "ArtView v4 output", must_exist=False)
    page_count, raw_objects, _masks = _v4_raw_inventory(inputs["source_pdf"])
    source_doc = read_json(inputs["source_identity"]); source = source_doc.get("source", source_doc)
    if source.get("page_count") not in (None, page_count):
        raise ValueError("ArtView v4 source PDF page count does not match sealed source identity")
    roles = _v4_reconstruction_roles(inputs["reconstruction_inventory"])
    if any(page > page_count for page in roles):
        raise ValueError("ArtView v4 reconstruction role escapes source PDF")
    cover_pages = [page for page, role in roles.items() if role == "cover"]
    if len(cover_pages) != 1:
        raise ValueError("ArtView v4 requires exactly one reconstruction cover role")
    cover_page = cover_pages[0]
    master_assets = _v4_master_assets_by_page(inputs["master_ru"], inputs["master_ru_asset_manifest"])
    if cover_page in master_assets:
        raise ValueError("ArtView v4 cover must be source-page owned, not a MASTER_RU markdown asset")
    executable = find_pdftoppm(pdftoppm_arg)
    stage = Path(tempfile.mkdtemp(prefix=target_root.name + ".tmp-", dir=target_root.parent)); candidate_root = stage / "candidate"
    try:
        rows: list[dict[str, Any]] = []
        with tempfile.TemporaryDirectory(prefix="artview-v4-render-") as temp_name:
            render_root = Path(temp_name)
            # The cover is a semantic composite: it absorbs all nontechnical
            # page-one components and is rendered once from the clean PDF page.
            for page in [cover_page]:
                asset_id = f"pdf-page-{page:03d}-cover"
                rendered = render_page(executable, inputs["source_pdf"], page, profile["render"]["dpi"], profile["render"]["format"], render_root)
                suffix = rendered.suffix.lower(); rel = f"assets/current/{asset_id}{suffix}"; target = candidate_root / rel; target.parent.mkdir(parents=True, exist_ok=True); shutil.copyfile(rendered, target)
                context_rel = f"context/{asset_id}{suffix}"; context_target = candidate_root / context_rel; context_target.parent.mkdir(parents=True, exist_ok=True); shutil.copyfile(rendered, context_target)
                components = [item["raw_id"] for item in raw_objects if item["source_page"] == page and item["disposition"] == "component_of_visual_unit"]
                rows.append({"asset_id": asset_id, "review_id": asset_id, "placement_id": f"source-cover-page-{page:03d}", "anchor": f"source-page-{page:03d}", "label": f"Source page {page:03d} cover", "source_page": page, "source_region": "full_page", "group": "cover", "semantic_role": "cover", "placement_target": "source_page_cover", "required": True, "provenance_kind": "clean_page_render", "component_raw_ids": components, "current": image_record(target, rel), "context": image_record(context_target, context_rel), "alternatives": [], "allowed_binary_decisions": ["keep_current"], "presentation_defaults": {"width_percent": 100, "alignment": "center", "wrap_text": False, "wrap_tables": False}})
            ordinary_by_page: dict[int, list[dict[str, Any]]] = {}
            for raw in raw_objects:
                if raw["disposition"] == "component_of_visual_unit" and raw["source_page"] != cover_page:
                    ordinary_by_page.setdefault(raw["source_page"], []).append(raw)
            for page in sorted(set(ordinary_by_page) | set(master_assets)):
                raw_rows = ordinary_by_page.get(page, []); master_rows = master_assets.get(page, [])
                if raw_rows and master_rows and len(raw_rows) != len(master_rows):
                    raise ValueError(f"ArtView v4 cannot unambiguously match PDF occurrences to MASTER_RU assets on page {page}")
                pairs: list[tuple[dict[str, Any] | None, dict[str, Any] | None]] = list(zip(raw_rows, master_rows)) if raw_rows and master_rows else [(raw, None) for raw in raw_rows] or [(None, asset) for asset in master_rows]
                for ordinal, (raw, master_asset) in enumerate(pairs, start=1):
                    rendered = render_page(executable, inputs["source_pdf"], page, profile["render"]["dpi"], profile["render"]["format"], render_root)
                    base_id = raw["raw_id"] if raw is not None else f"master-page-{page:03d}-asset-{ordinal:03d}"
                    context_rel = f"context/{base_id}{rendered.suffix.lower()}"; context_target = candidate_root / context_rel; context_target.parent.mkdir(parents=True, exist_ok=True); shutil.copyfile(rendered, context_target)
                    alternatives: list[dict[str, Any]] = []; provenance = "master_ru_asset" if master_asset is not None else "native_pdf_object"
                    if master_asset is not None:
                        source = master_asset["absolute_path"]; rel = f"assets/current/{base_id}{source.suffix.lower()}"; target = candidate_root / rel; target.parent.mkdir(parents=True, exist_ok=True); shutil.copyfile(source, target)
                        placement_target = "markdown_asset"; placement_id = f"master-page-{page:03d}-asset-{ordinal:03d}"; asset_id = base_id
                        if raw is not None:
                            native = _v4_native_image(inputs["source_pdf"], raw); alt_rel = f"assets/candidates/{base_id}-native.png"; alt_target = candidate_root / alt_rel; alt_target.parent.mkdir(parents=True, exist_ok=True); native.save(alt_target, "PNG", optimize=False)
                            alternatives = [{"candidate_id": f"{base_id}-native", "kind": "native_pdf_object", "binary": image_record(alt_target, alt_rel)}]
                    else:
                        assert raw is not None
                        native = _v4_native_image(inputs["source_pdf"], raw); rel = f"assets/current/{base_id}.png"; target = candidate_root / rel; target.parent.mkdir(parents=True, exist_ok=True); native.save(target, "PNG", optimize=False)
                        placement_target = "source_page_after"; placement_id = f"source-object-{page:03d}-{raw['object_id']}-{str(raw['xobject_name']).lstrip('/').casefold()}"; asset_id = base_id
                    role = roles.get(page, "source_visual")
                    rows.append({"asset_id": asset_id, "review_id": asset_id, "placement_id": placement_id, "anchor": f"source-page-{page:03d}", "label": f"Source page {page:03d} visual {ordinal}", "source_page": page, "source_region": "native_xobject" if raw is not None else "master_only", "group": role, "semantic_role": role, "placement_target": placement_target, "required": False, "provenance_kind": provenance, "component_raw_ids": [raw["raw_id"]] if raw is not None else [], "current": image_record(target, rel), "context": image_record(context_target, context_rel), "alternatives": alternatives, "allowed_binary_decisions": ["keep_current", *( ["use_candidate"] if alternatives else []), "exclude", "needs_manual_work", "reopen_masters"], "presentation_defaults": default_presentation("body")})
        inventory_doc, inventory_sha = inventory(candidate_root)
        write_json(candidate_root / "source_visual_inventory.json", {"schema": "kb_creator.source_visual_inventory.v1", "source_pdf": file_record(inputs["source_pdf"], profile["inputs"]["source_pdf"]["path"]), "page_count": page_count, "raw_objects": raw_objects, "visual_units": [{"review_id": row["review_id"], "source_page": row["source_page"], "component_raw_ids": row["component_raw_ids"], "derivation": row["provenance_kind"], "placement_id": row["placement_id"]} for row in rows]})
        write_json(candidate_root / "candidate_files.inventory.json", {"schema": "kb_creator.scenario_artview_candidate_files.v1", **inventory_doc})
        bindings = {"profile": file_record(profile_path, profile_path.name), **{name: file_record(path, profile["inputs"][name]["path"]) for name, path in inputs.items()}}
        manifest = {"schema": CANDIDATE_SCHEMA_V4, "scenario_id": profile["scenario_id"], "state": "candidate_needs_user_decisions", "bindings": bindings, "derived_expected": {"review_rows": len(rows), "raw_objects": len(raw_objects), "technical_raw_objects": sum(item["disposition"] == "technical_pdf_mechanic" for item in raw_objects), "source_pages": len({row["source_page"] for row in rows})}, "rows": rows, "candidate_files_inventory_sha256": inventory_sha, "decision_contract": {"schema": DECISION_SCHEMA_V4, "binding_sources": ["profile", "master_ru", "master_ru_acceptance", "master_ru_asset_manifest", "reconstruction_inventory", "source_pdf", "source_identity"], "accepted_requires_all_reviewed": True}}
        manifest_path = candidate_root / "candidate_manifest.json"; write_json(manifest_path, manifest); manifest_sha = sha256_file(manifest_path)
        template = {"schema": DECISION_SCHEMA_V4, "scenario_id": profile["scenario_id"], "state": "draft", "bindings": decision_bindings(manifest, manifest_sha), "decisions": [{"asset_id": row["asset_id"], "binary": {"choice": None, "candidate_id": None}, "presentation": row["presentation_defaults"], "reviewed": False, "notes": ""} for row in rows], "review": {"state": "open", "reviewed_count": 0, "unresolved_asset_ids": [row["asset_id"] for row in rows]}}
        template["decisions_sha256"] = sha256_bytes(canonical_json(template).encode("utf-8")); write_json(candidate_root / "artview-decisions.template.json", template)
        (candidate_root / "artview.html").write_text(_v3_review_html(manifest, manifest_sha).replace("ArtView v3", "ArtView v4"), encoding="utf-8", newline="\n")
        write_json(candidate_root / "qa.json", {"schema": "kb_creator.scenario_artview_qa.v4", "status": "pass", "candidate_manifest_sha256": manifest_sha, "checks": {"source_identity": True, "raw_object_disposition_closure": len(raw_objects) == sum(item["disposition"] in {"technical_pdf_mechanic", "component_of_visual_unit"} for item in raw_objects), "review_unit_closure": all(item["disposition"] == "technical_pdf_mechanic" or any(item["raw_id"] in row["component_raw_ids"] for row in rows) for item in raw_objects), "required_cover_present": any(row["semantic_role"] == "cover" and row["required"] for row in rows)}})
        os.replace(stage, target_root)
        return {"status": "awaiting_artview_decisions", "output_root": str(target_root), "manifest_sha256": manifest_sha, "inventory_sha256": inventory_sha, "counts": manifest["derived_expected"]}
    except Exception:
        shutil.rmtree(stage, ignore_errors=True); raise


def build(
    profile_path: Path,
    pdftoppm_arg: str | None,
    force: bool,
    output_root_arg: Path | None = None,
) -> dict[str, Any]:
    profile = read_json(profile_path)
    if profile.get("schema") == PROFILE_SCHEMA_V4:
        return build_v4(profile_path, pdftoppm_arg, force, output_root_arg)
    if profile.get("schema") == PROFILE_SCHEMA_V3:
        return build_v3(profile_path, force, output_root_arg)
    import pdfplumber
    import pypdf
    from pypdf import PdfReader

    scenario_id = str(profile["scenario_id"])
    inputs = {key: resolve_repo(value) for key, value in profile["inputs"].items()}
    for key, path in inputs.items():
        require_file(path, key)
    target_root = output_root_arg.resolve() if output_root_arg else resolve_repo(profile["output_root"])
    if target_root.exists() and not force:
        raise FileExistsError(f"Output exists; use --force: {target_root}")
    publication = read_json(inputs["publication_config"])
    acceptance = read_json(inputs["master_en_acceptance"])
    en_assets = read_json(inputs["master_en_asset_manifest"])
    ru_provenance = read_json(inputs["master_ru_provenance"])
    ru_qa = read_json(inputs["master_ru_qa"])
    reconstruction = read_json(inputs["reconstruction_asset_manifest"])
    comparison = read_json(inputs["comparison"])
    current_production_manifest = read_json(inputs["production_manifest"]) if "production_manifest" in inputs else None
    current_asset_decisions = read_json(inputs["production_asset_decisions"]) if "production_asset_decisions" in inputs else None
    source_identity = publication["document"]["source_pdf"]
    if sha256_file(inputs["source_pdf"]) != source_identity["sha256"].upper():
        raise ValueError("Source PDF hash does not match publication config")
    if sha256_file(inputs["master_en"]) != acceptance["master_en"]["sha256"].upper():
        raise ValueError("MASTER_EN hash does not match acceptance")
    if sha256_file(inputs["master_ru"]) != ru_provenance["master_ru"]["sha256"].upper():
        raise ValueError("MASTER_RU hash does not match provenance")
    if ru_qa.get("status") != "pass" or ru_qa.get("master_ru_sha256", "").upper() != sha256_file(inputs["master_ru"]):
        raise ValueError("MASTER_RU QA is not a matching pass")
    config_assets = publication["assets"]
    reader_assets = [row for row in config_assets if row.get("disposition") == "reader"]
    evidence_assets = [row for row in config_assets if row.get("disposition") == "evidence_only"]
    if len({row["asset_id"] for row in config_assets}) != len(config_assets):
        raise ValueError("Duplicate publication asset_id")
    en_asset_by_id = {row["asset_id"]: row for row in en_assets["assets"] if row.get("reader_value") is True}
    if set(en_asset_by_id) != {row["asset_id"] for row in reader_assets}:
        raise ValueError("EN asset manifest reader ids differ from publication config")
    reconstruction_by_sha: dict[str, list[dict[str, Any]]] = {}
    for row in reconstruction["assets"]:
        reconstruction_by_sha.setdefault(str(row.get("sha256") or "").upper(), []).append(row)
    labels = extract_heading_labels(inputs["master_ru"].read_text(encoding="utf-8"))
    current_production_states = production_asset_states(current_production_manifest, current_asset_decisions)
    executable = find_pdftoppm(pdftoppm_arg)
    previous_candidate_root: Path | None = None
    previous_rows_by_asset: dict[str, dict[str, Any]] = {}
    previous_context_by_page: dict[int, dict[str, Any]] = {}
    previous_manifest_path = target_root / "candidate" / "candidate_manifest.json"
    if force and previous_manifest_path.is_file():
        try:
            previous_manifest = read_json(previous_manifest_path)
            previous_source = previous_manifest.get("bindings", {}).get("source_pdf", {})
            if str(previous_source.get("sha256") or "").upper() == source_identity["sha256"].upper():
                previous_candidate_root = previous_manifest_path.parent
                previous_rows_by_asset = {
                    str(row["asset_id"]): row
                    for row in previous_manifest.get("rows", [])
                    if isinstance(row, dict) and row.get("asset_id")
                }
                for row in previous_rows_by_asset.values():
                    context = row.get("context")
                    page_value = row.get("source_page")
                    if isinstance(context, dict) and isinstance(page_value, int):
                        previous_context_by_page.setdefault(page_value, context)
        except (OSError, ValueError, KeyError, TypeError, json.JSONDecodeError):
            previous_candidate_root = None
            previous_rows_by_asset = {}
            previous_context_by_page = {}
    target_root.parent.mkdir(parents=True, exist_ok=True)
    stage = Path(tempfile.mkdtemp(prefix=target_root.name + ".tmp-", dir=target_root.parent))
    candidate_root = stage / "candidate"
    render_temp = stage / "_render_tmp"
    render_temp.mkdir(parents=True)
    context_cache: dict[int, dict[str, Any]] = {}
    high_cache: dict[int, Path] = {}
    rows: list[dict[str, Any]] = []
    try:
        with pdfplumber.open(inputs["source_pdf"]) as plumber, inputs["source_pdf"].open("rb") as handle:
            pdf_reader = PdfReader(handle)
            if len(plumber.pages) != len(pdf_reader.pages):
                raise ValueError("PDF reader page-count disagreement")
            for asset in reader_assets:
                asset_id = asset["asset_id"]
                page_number = int(asset["source_page"])
                page = plumber.pages[page_number - 1]
                rotation = int(getattr(page, "rotation", 0) or 0)
                if rotation != 0 or float(page.width) <= 0 or float(page.height) <= 0:
                    raise ValueError(f"unsupported_page_geometry:{page_number}")
                manifest_asset = en_asset_by_id[asset_id]
                current_source = inputs["master_ru"].parent / manifest_asset["output_path"].replace("/", os.sep)
                require_file(current_source, f"current asset {asset_id}")
                if sha256_file(current_source) != manifest_asset["sha256"].upper():
                    raise ValueError(f"Current asset hash mismatch: {asset_id}")
                current_rel = safe_relative(f"assets/current/{Path(manifest_asset['output_path']).name}")
                current_target = candidate_root / current_rel
                current_target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(current_source, current_target)
                current = image_record(current_target, current_rel)
                if page_number not in context_cache:
                    context_rel = f"context/page-{page_number:03d}.jpg"
                    context_path = candidate_root / context_rel
                    context_recipe = "pdftoppm 120dpi RGB white + Pillow JPEG q85 subsampling1 nonprogressive metadata-stripped"
                    cached_context = previous_context_by_page.get(page_number)
                    copied_context = None
                    if isinstance(cached_context, dict) and cached_context.get("recipe") == context_recipe:
                        copied_context = copy_cached_image(
                            previous_candidate_root, candidate_root, cached_context, context_rel
                        )
                    if copied_context is None:
                        rendered = render_page(executable, inputs["source_pdf"], page_number, 120, "jpeg", render_temp)
                        normalize_context(rendered, context_path)
                        copied_context = image_record(context_path, context_rel)
                    context_cache[page_number] = {
                        **copied_context,
                        "recipe": context_recipe,
                        "selectable": False,
                    }
                region, region_warnings = recover_region(asset, reconstruction_by_sha, comparison)
                if region:
                    region["source_page"] = page_number
                warnings = list(region_warnings)
                alternatives: list[dict[str, Any]] = []
                kind = (asset.get("provenance") or {}).get("kind")
                if kind == "reviewed_provisional_full_page":
                    if page_number not in high_cache:
                        high_cache[page_number] = render_page(executable, inputs["source_pdf"], page_number, 200, "png", render_temp)
                    full_rel = f"assets/full_page/{asset_id}.png"
                    full_path = candidate_root / full_rel
                    normalize_png(high_cache[page_number], full_path)
                    full_binary = image_record(full_path, full_rel)
                    if full_binary["sha256"] == current["sha256"]:
                        full_path.unlink()
                        warnings.append("full_page_render_byte_identical_to_current")
                    else:
                        locator = {"physical_page": page_number, "box": "MediaBox", "points": [0, 0, float(page.width), float(page.height)]}
                        recipe = {"tool": "pdftoppm", "dpi": 200, "format": "png", "color": "RGB", "background": "white", "metadata": "stripped"}
                        alternatives.append({
                            "candidate_id": make_candidate_id(asset_id, "full_page_render", locator, recipe, full_binary["sha256"]),
                            "kind": "full_page_render", "path": full_rel, "binary": full_binary,
                            "source_locator": locator, "recipe": recipe,
                            "quality": {"page_coverage": 1.0, "resampled": True},
                        })
                elif region_is_valid(region):
                    direct, direct_warnings = extract_direct_candidate(
                        asset_id=asset_id, page=page, pypdf_reader=pdf_reader, region=region, output_root=candidate_root
                    )
                    if direct:
                        alternatives.append(direct)
                        warnings.extend(direct_warnings)
                    else:
                        composite, composite_warnings = extract_multi_object_candidate(
                            asset_id=asset_id, page=page, pypdf_reader=pdf_reader,
                            region=region, output_root=candidate_root,
                        )
                        if composite is None:
                            composite, composite_warnings = extract_page_composite_candidate(
                                asset_id=asset_id, page=page, pypdf_reader=pdf_reader,
                                region=region, output_root=candidate_root,
                            )
                        if composite:
                            alternatives.append(composite)
                            # A more specific audited fallback supersedes the
                            # generic no-unique-direct warning.
                            warnings.extend(composite_warnings)
                        else:
                            warnings.extend(direct_warnings)
                            warnings.extend(composite_warnings)
                    # A page crop is a separate visual choice from a native PDF
                    # object. Always emit it so ArtView can compare both routes.
                    bbox = region["bbox"]
                    page_pixel_width = round(float(page.width) * 200 / 72)
                    page_pixel_height = round(float(page.height) * 200 / 72)
                    crop_box = (
                        max(0, math.floor(bbox[0] * page_pixel_width / 1000)),
                        max(0, math.floor(bbox[1] * page_pixel_height / 1000)),
                        min(page_pixel_width, math.ceil(bbox[2] * page_pixel_width / 1000)),
                        min(page_pixel_height, math.ceil(bbox[3] * page_pixel_height / 1000)),
                    )
                    derived_rel = f"assets/derived/{asset_id}.png"
                    derived_path = candidate_root / derived_rel
                    locator = {"physical_page": page_number, "normalized_bbox_top_left": bbox, "pixel_crop_box": list(crop_box)}
                    recipe = {"tool": "pdftoppm+Pillow", "dpi": 200, "format": "png", "rounding": "floor_left_top_ceil_right_bottom_clamped"}
                    previous_row = previous_rows_by_asset.get(asset_id, {})
                    previous_derived = next(
                        (
                            candidate for candidate in previous_row.get("alternatives", [])
                            if candidate.get("kind") == "derived_page_crop"
                            and candidate.get("source_locator") == locator
                            and candidate.get("recipe") == recipe
                        ),
                        None,
                    )
                    derived_binary = copy_cached_image(
                        previous_candidate_root,
                        candidate_root,
                        previous_derived.get("binary") if previous_derived else None,
                        derived_rel,
                    )
                    if derived_binary is None:
                        if page_number not in high_cache:
                            high_cache[page_number] = render_page(executable, inputs["source_pdf"], page_number, 200, "png", render_temp)
                        with Image.open(high_cache[page_number]) as page_image:
                            actual_width, actual_height = page_image.size
                            if (actual_width, actual_height) != (page_pixel_width, page_pixel_height):
                                raise ValueError(f"unexpected_render_dimensions:{page_number}")
                            derived_path.parent.mkdir(parents=True, exist_ok=True)
                            page_image.crop(crop_box).save(derived_path, "PNG", optimize=False)
                        derived_binary = image_record(derived_path, derived_rel)
                    alternatives.append({
                        "candidate_id": make_candidate_id(asset_id, "derived_page_crop", locator, recipe, derived_binary["sha256"]),
                        "kind": "derived_page_crop", "path": derived_rel, "binary": derived_binary,
                        "source_locator": locator, "recipe": recipe,
                        "quality": {"page_coverage": round((bbox[2]-bbox[0])*(bbox[3]-bbox[1])/1_000_000, 6), "resampled": True},
                    })
                else:
                    warnings.append("invalid_or_missing_region")
                if region_is_valid(region):
                    overlap = text_overlap(region, comparison, page_number)
                    if overlap["likely_text_contamination"]:
                        warnings.append("likely_text_contamination")
                else:
                    overlap = {"likely_text_contamination": "unknown", "intersections": []}
                group = artview_group(asset.get("anchor"), asset.get("provenance"))
                allowed = ["keep_current"]
                if alternatives:
                    allowed.append("use_candidate")
                allowed.extend(["exclude", "needs_manual_work", "reopen_masters"])
                rows.append({
                    "asset_id": asset_id,
                    "anchor": asset["anchor"],
                    "label": labels.get(asset["anchor"], asset["anchor"]),
                    "placement": asset["placement"],
                    "source_order": asset.get("source_order"),
                    "source_page": page_number,
                    "accepted_provenance": asset.get("provenance"),
                    "current": current,
                    "region": region,
                    "page_geometry": {"width_points": float(page.width), "height_points": float(page.height), "rotation": rotation},
                    "context": context_cache[page_number],
                    "alternatives": alternatives,
                    "allowed_binary_decisions": allowed,
                    "group": group,
                    "presentation_defaults": default_presentation(group),
                    "production_state": current_production_states.get(asset_id, {
                        "status": "absent" if current_production_manifest else "unknown",
                        "reason": "not_present_in_current_production" if current_production_manifest else "production_not_bound",
                        "paths": [],
                    }),
                    "warnings": sorted(set(warnings)),
                    "text_overlap_evidence": overlap,
                })
        # Inventory only portable binaries, excluding the manifest and HTML to avoid a self-hash cycle.
        payload_paths = []
        for directory in (candidate_root / "assets", candidate_root / "context"):
            if directory.exists():
                payload_paths.extend(path for path in directory.rglob("*") if path.is_file())
        inventory_rows = []
        inventory_lines = []
        for path in sorted(payload_paths, key=lambda item: item.relative_to(candidate_root).as_posix()):
            rel = path.relative_to(candidate_root).as_posix()
            digest = sha256_file(path)
            size = path.stat().st_size
            inventory_rows.append({"path": rel, "bytes": size, "sha256": digest})
            inventory_lines.append(f"{rel}\t{size}\t{digest}\n")
        inventory_sha = sha256_bytes("".join(inventory_lines).encode("utf-8"))
        inventory_doc = {"schema": "kb_creator.scenario_artview_candidate_files.v1", "algorithm": "sorted relative_path<TAB>bytes<TAB>UPPER_SHA256<LF>", "sha256": inventory_sha, "files": inventory_rows}
        write_json(candidate_root / "candidate_files.inventory.json", inventory_doc)
        bindings = {
            key: file_record(path, repo_path(path))
            for key, path in inputs.items()
        }
        direct_kinds = {"direct_xobject", "embedded_page_composite_crop", "direct_composite_parts"}
        summary = {
            "publication_assets": len(config_assets),
            "reader_rows": len(rows),
            "evidence_only_rows": len(evidence_assets),
            "region_rows": sum(1 for row in rows if region_is_valid(row["region"])),
            "full_page_rows": sum(1 for asset in reader_assets if (asset.get("provenance") or {}).get("kind") == "reviewed_provisional_full_page"),
            "direct_candidates": sum(1 for row in rows for candidate in row["alternatives"] if candidate["kind"] in direct_kinds),
            "direct_single_candidates": sum(1 for row in rows for candidate in row["alternatives"] if candidate["kind"] == "direct_xobject"),
            "embedded_page_composite_candidates": sum(1 for row in rows for candidate in row["alternatives"] if candidate["kind"] == "embedded_page_composite_crop"),
            "direct_composite_candidates": sum(1 for row in rows for candidate in row["alternatives"] if candidate["kind"] == "direct_composite_parts"),
            "derived_candidates": sum(1 for row in rows for candidate in row["alternatives"] if candidate["kind"] == "derived_page_crop"),
            "full_page_candidates": sum(1 for row in rows for candidate in row["alternatives"] if candidate["kind"] == "full_page_render"),
            "unique_context_pages": len(context_cache),
        }
        manifest = {
            "schema": CANDIDATE_SCHEMA,
            "scenario_id": scenario_id,
            "state": "candidate_needs_user_decisions",
            "bindings": bindings,
            "generator": {
                "script": file_record(Path(__file__), repo_path(Path(__file__))),
                "python": platform.python_version(),
                "pdfplumber": pdfplumber.__version__,
                "pypdf": pypdf.__version__,
                "pillow": PIL.__version__,
                "poppler": poppler_version(executable),
                "profile_sha256": sha256_file(profile_path),
            },
            "summary": summary,
            "skipped_source_pages": [
                {"page": int(row["page"]), "publication_disposition": row["publication_disposition"], "reason": row["reason"], "candidate_paths": []}
                for row in publication["source_disposition"] if row.get("publication_disposition") == "excluded_advertising"
            ],
            "rows": rows,
            "candidate_files_inventory_sha256": inventory_sha,
            "decision_contract": {
                "schema": DECISION_SCHEMA,
                "binary_vocabulary": list(BINARY_DECISIONS),
                "presentation": {
                    "width_percent": {"type": "integer", "minimum": 10, "maximum": 100},
                    "alignment": list(PRESENTATION_ALIGNMENTS),
                    "wrap_text": "boolean",
                    "wrap_tables": "boolean_requires_wrap_text",
                },
                "binding_sources": [
                    key for key in (
                        "source_pdf", "master_en", "master_ru", "production_master_en",
                        "production_master_ru", "production_manifest", "production_asset_decisions",
                    ) if key in bindings
                ],
                "accepted_requires_all_reviewed": True,
                "default": "recommended_presentation_but_unreviewed",
            },
        }
        manifest_path = candidate_root / "candidate_manifest.json"
        write_json(manifest_path, manifest)
        manifest_sha = sha256_file(manifest_path)
        decision_template = draft_decision_document(manifest, manifest_sha)
        decision_template_path = candidate_root / "artview-decisions.template.json"
        write_json(decision_template_path, decision_template)
        html = html_bundle(manifest, manifest_sha)
        (candidate_root / "artview.html").write_text(html, encoding="utf-8", newline="\n")
        findings = []
        expected_excluded = list(acceptance["candidate"]["excluded_source_pages"])
        actual_excluded = [row["page"] for row in manifest["skipped_source_pages"]]
        checks = {
            "reader_rows_94": len(rows) == int(acceptance["candidate"]["reader_assets"]),
            "reader_and_evidence_partition": len(reader_assets) + len(evidence_assets) == len(config_assets),
            "unique_asset_ids": len({row["asset_id"] for row in rows}) == len(rows),
            "current_asset_each_row": all((candidate_root / row["current"]["path"]).is_file() for row in rows),
            "all_referenced_binaries_exist_and_match": all(
                (candidate_root / safe_relative(record["path"])).is_file()
                and sha256_file(candidate_root / safe_relative(record["path"])) == record["sha256"]
                for row in rows for record in iter_row_binary_records(row)
            ),
            "region_rows_84": summary["region_rows"] == 84,
            "direct_like_candidate_each_region_row": (
                summary["direct_candidates"] == summary["region_rows"]
                and all(
                    any(candidate["kind"] in direct_kinds for candidate in row["alternatives"])
                    for row in rows if region_is_valid(row["region"])
                )
            ),
            "full_page_rows_10": summary["full_page_rows"] == 10,
            "excluded_pages_exact": actual_excluded == expected_excluded == [123, 124],
            "excluded_pages_have_no_files": not any(f"page-{page:03d}" in item["path"] for page in actual_excluded for item in inventory_rows),
            "all_bundle_paths_safe": all(safe_relative(item["path"]) for item in inventory_rows),
            "html_rows_embedded": html.count('className="row"') == 0 and 'manifest.rows.forEach' in html,
            "decision_export_import_present": "decisionDocument" in html and "validateImport" in html,
            "binary_and_presentation_are_independent": all(
                set(row["presentation_defaults"]) == {"width_percent", "alignment", "wrap_text", "wrap_tables"}
                and "keep_current" in row["allowed_binary_decisions"]
                and "exclude" in row["allowed_binary_decisions"]
                for row in rows
            ),
            "live_text_and_table_preview_present": "Предварительный макет" in html and "wrap_tables" in html,
            "production_state_projected": (
                current_production_manifest is None
                or sum(1 for row in rows if row["production_state"]["status"] == "excluded") == 6
            ),
            "accepted_export_requires_review": "exportAccepted" in html and "isAcceptedRow" in html,
            "decision_template_is_bound_and_unreviewed": (
                decision_template["bindings"] == decision_bindings(manifest, manifest_sha)
                and len(decision_template["decisions"]) == len(rows)
                and all(
                    item["binary"] == {"choice": None, "candidate_id": None}
                    and item["reviewed"] is False
                    for item in decision_template["decisions"]
                )
            ),
        }
        for name, passed in checks.items():
            if not passed:
                findings.append({"code": name})
        qa = {
            "schema": "kb_creator.scenario_artview_qa.v2",
            "status": "pass" if not findings else "fail",
            "candidate_manifest_sha256": manifest_sha,
            "candidate_files_inventory_sha256": inventory_sha,
            "decision_template": file_record(
                decision_template_path,
                decision_template_path.relative_to(candidate_root).as_posix(),
            ),
            "counts": summary,
            "checks": checks,
            "findings": findings,
        }
        write_json(candidate_root / "qa.json", qa)
        readme = f"""# {scenario_id} ArtView review checkpoint

        State: `candidate_needs_user_decisions`. This is an offline review bundle, not
        an accepted visual-asset package. Open `candidate/artview.html`. For every
        logical asset, choose the exact binary, set width/alignment/text wrap/table
        wrap, then mark the row reviewed. Exported JSON remains separate from MASTER
        and production until explicit user acceptance. Pages 123 and 124 are excluded
        advertising and have no review binaries. `candidate/artview-decisions.template.json`
        is a hash-bound, empty draft for CLI validation or recovery; the browser can
        export the same schema after each review session.

Rebuild from the repository root:

```powershell
python -B kb_creator/scripts/scenario_artview.py build --profile {repo_path(profile_path)} --force
```

Candidate manifest SHA-256: `{manifest_sha}`
Candidate file inventory SHA-256: `{inventory_sha}`
Decision template SHA-256: `{sha256_file(decision_template_path)}`
"""
        (stage / "README.md").write_text(readme, encoding="utf-8", newline="\n")
        if qa["status"] != "pass":
            raise ValueError(f"ArtView QA failed: {findings}")
        shutil.rmtree(render_temp)
        if target_root.exists():
            if not force:
                raise FileExistsError(target_root)
            shutil.rmtree(target_root)
        os.replace(stage, target_root)
        return {"status": "pass", "output_root": repo_path(target_root), "manifest_sha256": manifest_sha, "inventory_sha256": inventory_sha, "counts": summary}
    except Exception:
        shutil.rmtree(stage, ignore_errors=True)
        raise


def seal_v3_decisions(value: dict[str, Any]) -> dict[str, Any]:
    result = {name: item for name, item in value.items() if name != "decisions_sha256"}
    result["decisions_sha256"] = sha256_bytes(canonical_json(result).encode("utf-8"))
    return result


def _v3_explicit_candidate_manifest(authority_root: Path, value: Path) -> Path:
    authority = authority_root.resolve(strict=True)
    raw = os.fspath(value)
    relative = Path(value)
    if not raw or (isinstance(value, str) and "\\" in value) or ":" in raw or relative.is_absolute() or any(part in {"", ".", ".."} for part in relative.parts):
        raise ValueError("explicit candidate manifest must be safe authority-relative")
    path = (authority / relative).resolve(strict=True)
    try:
        path.relative_to(authority)
    except ValueError as error:
        raise ValueError("explicit candidate manifest escapes authority root") from error
    current = path
    while current != authority:
        if _v3_is_reparse(current):
            raise ValueError("explicit candidate manifest contains reparse content")
        current = current.parent
    if path.name != "candidate_manifest.json" or not path.is_file():
        raise ValueError("explicit candidate manifest must name candidate_manifest.json")
    return path


def _v3_authority_file(
    authority_root: Path,
    value: os.PathLike[str] | str,
    label: str,
    *,
    expected_name: str | None = None,
) -> Path:
    """Resolve an existing file through an explicit, non-reparse authority root."""
    supplied_authority = Path(authority_root)
    if _v3_is_reparse(supplied_authority):
        raise ValueError(f"{label} authority root must be an existing non-reparse directory")
    authority = supplied_authority.resolve(strict=True)
    if not authority.is_dir() or _v3_is_reparse(authority):
        raise ValueError(f"{label} authority root must be an existing non-reparse directory")
    raw = os.fspath(value)
    normalized = raw.replace("\\", "/")
    if V3_SAFE_PATH_RE.fullmatch(normalized) is None:
        raise ValueError(f"{label} must be safe authority-relative")
    relative = Path(*normalized.split("/"))
    lexical = authority / relative
    current = lexical
    while True:
        try:
            current.relative_to(authority)
        except ValueError as error:
            raise ValueError(f"{label} escapes authority root") from error
        if current.exists() and _v3_is_reparse(current):
            raise ValueError(f"{label} contains reparse content")
        if current == authority:
            break
        current = current.parent
    path = lexical.resolve(strict=True)
    try:
        path.relative_to(authority)
    except ValueError as error:
        raise ValueError(f"{label} escapes authority root") from error
    if not path.is_file() or path.is_symlink():
        raise ValueError(f"{label} must name an existing non-reparse file")
    if expected_name is not None and path.name != expected_name:
        raise ValueError(f"{label} must name {expected_name}")
    return path


def _v3_absent_authority_file(
    authority_root: Path,
    value: os.PathLike[str] | str,
    label: str,
) -> Path:
    """Resolve a not-yet-created file without permitting traversal or reparse parents."""
    supplied_authority = Path(authority_root)
    if _v3_is_reparse(supplied_authority):
        raise ValueError(f"{label} authority root must be an existing non-reparse directory")
    authority = supplied_authority.resolve(strict=True)
    if not authority.is_dir() or _v3_is_reparse(authority):
        raise ValueError(f"{label} authority root must be an existing non-reparse directory")
    raw = os.fspath(value)
    normalized = raw.replace("\\", "/")
    if V3_SAFE_PATH_RE.fullmatch(normalized) is None:
        raise ValueError(f"{label} must be safe authority-relative")
    relative = Path(*normalized.split("/"))
    lexical = authority / relative
    if not lexical.parent.is_dir():
        raise ValueError(f"{label} parent must already exist")
    current = lexical.parent
    while True:
        try:
            current.relative_to(authority)
        except ValueError as error:
            raise ValueError(f"{label} escapes authority root") from error
        if _v3_is_reparse(current):
            raise ValueError(f"{label} contains reparse content")
        if current == authority:
            break
        current = current.parent
    path = lexical.resolve()
    try:
        path.relative_to(authority)
    except ValueError as error:
        raise ValueError(f"{label} escapes authority root") from error
    if path.exists() or _v3_is_reparse(lexical):
        raise FileExistsError(f"{label} must be absent")
    return path


def _v3_candidate_context(
    profile_path: Path,
    candidate_manifest_path: Path | None = None,
    authority_root: Path | None = None,
) -> dict[str, Any]:
    """Validate and project one complete v3 candidate graph for decision use."""
    profile, input_paths, graph_index = _v3_profile(profile_path)
    if candidate_manifest_path is None:
        candidate_root = _v3_output_root(
            profile_path.parent,
            f"{profile['output_root']}/candidate",
            "ArtView v3 candidate",
            must_exist=True,
        )
        manifest_path = candidate_root / "candidate_manifest.json"
    else:
        if authority_root is None:
            raise ValueError("explicit candidate manifest requires authority root")
        manifest_path = _v3_explicit_candidate_manifest(authority_root, candidate_manifest_path)
        candidate_root = manifest_path.parent
    manifest = read_json(manifest_path)
    findings: list[dict[str, Any]] = []
    if (
        set(manifest)
        != {
            "schema",
            "scenario_id",
            "state",
            "bindings",
            "derived_expected",
            "rows",
            "candidate_files_inventory_sha256",
            "decision_contract",
        }
        or manifest.get("schema") != CANDIDATE_SCHEMA_V3
        or manifest.get("scenario_id") != profile["scenario_id"]
    ):
        findings.append({"code": "candidate_manifest_shape_or_scenario"})
    expected_manifest_bindings = {
        "profile": file_record(profile_path, profile_path.name),
        **{
            name: file_record(path, profile["inputs"][name]["path"])
            for name, path in input_paths.items()
        },
    }
    if manifest.get("bindings") != expected_manifest_bindings:
        findings.append({"code": "candidate_manifest_binding_mismatch"})
    expected_rows = []
    for source_row in profile["rows"]:
        asset_id = source_row["asset_id"]
        current_source, current_membership = _v3_bound_image(
            profile_path.parent,
            source_row["current"],
            f"current image {asset_id}",
            graph_index,
        )
        current_rel = f"assets/current/{asset_id}{current_source.suffix.lower()}"
        context_source, context_membership = _v3_bound_image(
            profile_path.parent,
            source_row["context"],
            f"context image {asset_id}",
            graph_index,
        )
        context_rel = f"context/{asset_id}{context_source.suffix.lower()}"
        alternatives = []
        for source_candidate in source_row["alternatives"]:
            binary_source, binary_membership = _v3_bound_image(
                profile_path.parent,
                source_candidate["binary"],
                f"candidate image {source_candidate['candidate_id']}",
                graph_index,
            )
            relative = (
                f"assets/candidates/{source_candidate['candidate_id']}"
                f"{binary_source.suffix.lower()}"
            )
            alternatives.append(
                {
                    "candidate_id": source_candidate["candidate_id"],
                    "kind": source_candidate["kind"],
                    "binary": {
                        **image_record(binary_source, relative),
                        "source_graph_membership": binary_membership,
                    },
                }
            )
        expected_rows.append(
            {
                "asset_id": asset_id,
                "anchor": source_row["anchor"],
                "label": source_row["label"],
                "source_page": source_row["source_page"],
                "group": source_row["group"],
                "current": {
                    **image_record(current_source, current_rel),
                    "source_graph_membership": current_membership,
                },
                "context": {
                    **image_record(context_source, context_rel),
                    "source_graph_membership": context_membership,
                },
                "alternatives": alternatives,
                "allowed_binary_decisions": [
                    "keep_current",
                    *(["use_candidate"] if alternatives else []),
                    "exclude",
                    "needs_manual_work",
                    "reopen_masters",
                ],
                "presentation_defaults": source_row["presentation_defaults"],
            }
        )
    expected_derived = {
        "review_rows": len(expected_rows),
        "alternative_binaries": sum(len(row["alternatives"]) for row in expected_rows),
        "portable_binaries": sum(2 + len(row["alternatives"]) for row in expected_rows),
        "source_pages": len({row["source_page"] for row in expected_rows}),
        "excluded_source_pages": list(profile["excluded_source_pages"]),
    }
    expected_policy = {
        "schema": DECISION_SCHEMA_V3,
        "binding_sources": [
            "profile",
            "master_ru",
            "master_ru_acceptance",
            "master_ru_asset_manifest",
            "reconstruction_inventory",
        ],
        "accepted_requires_all_reviewed": True,
    }
    if (
        manifest.get("rows") != expected_rows
        or manifest.get("derived_expected") != expected_derived
        or manifest.get("state") != "candidate_needs_user_decisions"
        or manifest.get("decision_contract") != expected_policy
    ):
        findings.append({"code": "candidate_manifest_projection_mismatch"})
    binary_rows = []
    binary_roots = {candidate_root / "assets", candidate_root / "context"}
    for path in sorted(
        (
            item
            for item in candidate_root.rglob("*")
            if item.is_file() and any(root in item.parents for root in binary_roots)
        ),
        key=lambda item: item.relative_to(candidate_root).as_posix(),
    ):
        binary_rows.append(file_record(path, path.relative_to(candidate_root).as_posix()))
    inventory_sha = sha256_bytes(
        "".join(
            f"{row['path']}\t{row['bytes']}\t{row['sha256']}\n" for row in binary_rows
        ).encode("utf-8")
    )
    inventory_doc = read_json(candidate_root / "candidate_files.inventory.json")
    if (
        inventory_doc
        != {
            "schema": "kb_creator.scenario_artview_candidate_files.v1",
            "algorithm": "sorted relative_path<TAB>bytes<TAB>UPPER_SHA256<LF>",
            "files": binary_rows,
            "sha256": inventory_sha,
        }
        or manifest.get("candidate_files_inventory_sha256") != inventory_sha
    ):
        findings.append({"code": "candidate_binary_inventory_mismatch"})
    return {
        "profile": profile,
        "manifest": manifest,
        "manifest_path": manifest_path,
        "candidate_root": candidate_root,
        "findings": findings,
    }


def validate_v3_decisions(profile_path: Path, decisions_path: Path, require_accepted: bool, candidate_manifest_path: Path | None = None, authority_root: Path | None = None) -> dict[str, Any]:
    candidate = _v3_candidate_context(profile_path, candidate_manifest_path, authority_root)
    profile = candidate["profile"]
    manifest = candidate["manifest"]
    manifest_path = candidate["manifest_path"]
    decisions = read_json(decisions_path)
    findings = list(candidate["findings"])
    expected_bindings = decision_bindings(manifest, sha256_file(manifest_path))
    if set(decisions) != {"schema", "scenario_id", "state", "bindings", "decisions", "review", "decisions_sha256"}:
        findings.append({"code": "decision_closed_schema_mismatch"})
    else:
        try: _v3_validate_seal(decisions, "decisions_sha256", "ArtView v3 decisions")
        except ValueError: findings.append({"code": "decision_seal_mismatch"})
    if decisions.get("schema") != DECISION_SCHEMA_V3 or decisions.get("scenario_id") != profile["scenario_id"]:
        findings.append({"code": "schema_or_scenario_mismatch"})
    if decisions.get("bindings") != expected_bindings:
        findings.append({"code": "binding_mismatch"})
    rows = manifest.get("rows") if isinstance(manifest.get("rows"), list) else []
    supplied = decisions.get("decisions") if isinstance(decisions.get("decisions"), list) else []
    if [item.get("asset_id") for item in supplied if isinstance(item, dict)] != [row.get("asset_id") for row in rows]:
        findings.append({"code": "decision_order_cardinality_or_duplicate"})
    row_map = {row.get("asset_id"): row for row in rows if isinstance(row, dict)}
    unresolved = []
    for item in supplied:
        if not isinstance(item, dict) or set(item) != {"asset_id", "binary", "presentation", "reviewed", "notes"}:
            findings.append({"code": "decision_row_closed_schema_mismatch"}); continue
        row = row_map.get(item["asset_id"]); binary = item.get("binary")
        if row is None or not isinstance(binary, dict) or set(binary) != {"choice", "candidate_id"}:
            findings.append({"code": "unknown_asset_or_binary_shape", "asset_id": item.get("asset_id")}); continue
        choice = binary["choice"]; candidate_id = binary["candidate_id"]
        if choice is not None and choice not in row["allowed_binary_decisions"]:
            findings.append({"code": "binary_decision_not_allowed", "asset_id": item["asset_id"]})
        candidate_ids = {candidate["candidate_id"] for candidate in row["alternatives"]}
        if choice == "use_candidate" and candidate_id not in candidate_ids:
            findings.append({"code": "candidate_selection_mismatch", "asset_id": item["asset_id"]})
        if choice != "use_candidate" and candidate_id is not None:
            findings.append({"code": "unexpected_candidate_selection", "asset_id": item["asset_id"]})
        if not isinstance(item.get("presentation"), dict) or set(item["presentation"]) != {"width_percent", "alignment", "wrap_text", "wrap_tables"}:
            findings.append({"code": "presentation_closed_schema_mismatch", "asset_id": item["asset_id"]})
        else:
            findings.extend(presentation_findings(item["presentation"], item["asset_id"]))
        if not isinstance(item.get("reviewed"), bool) or not item.get("reviewed") or choice not in {"keep_current", "use_candidate", "exclude"}:
            unresolved.append(item["asset_id"])
    review = decisions.get("review")
    if not isinstance(review, dict) or set(review) != {"state", "reviewed_count", "unresolved_asset_ids"}:
        findings.append({"code": "review_closed_schema_mismatch"})
    else:
        reviewed_count = sum(item.get("reviewed") is True for item in supplied if isinstance(item, dict))
        if review["reviewed_count"] != reviewed_count or review["unresolved_asset_ids"] != unresolved:
            findings.append({"code": "review_summary_mismatch"})
    if require_accepted and (decisions.get("state") != "accepted" or not isinstance(review, dict) or review.get("state") != "closed" or unresolved):
        findings.append({"code": "accepted_full_closure_required", "asset_ids": unresolved})
    return {"schema": "kb_creator.scenario_artview_decision_validation.v3", "status": "pass" if not findings else "fail", "decision_count": len(supplied), "reviewed_count": sum(item.get("reviewed") is True for item in supplied if isinstance(item, dict)), "findings": findings}


def validate_v4_decisions(profile_path: Path, decisions_path: Path, require_accepted: bool, candidate_manifest_path: Path | None = None, authority_root: Path | None = None) -> dict[str, Any]:
    """Validate v4 decisions, including non-excludable required placements."""
    profile, _inputs = _v4_profile(profile_path)
    if candidate_manifest_path is None:
        root = _v3_output_root(profile_path.parent, f"{profile['output_root']}/candidate", "ArtView v4 candidate", must_exist=True)
        manifest_path = root / "candidate_manifest.json"
    else:
        if authority_root is None:
            raise ValueError("ArtView v4 explicit candidate requires an authority root")
        manifest_path = _v3_explicit_candidate_manifest(authority_root, candidate_manifest_path)
        root = manifest_path.parent
    manifest = read_json(manifest_path); decisions = read_json(decisions_path)
    findings: list[dict[str, Any]] = []
    if manifest.get("schema") != CANDIDATE_SCHEMA_V4 or manifest.get("scenario_id") != profile["scenario_id"]:
        findings.append({"code": "candidate_schema_or_scenario_mismatch"})
    expected_bindings = decision_bindings(manifest, sha256_file(manifest_path))
    if set(decisions) != {"schema", "scenario_id", "state", "bindings", "decisions", "review", "decisions_sha256"}:
        findings.append({"code": "decision_closed_schema_mismatch"})
    else:
        try: _v3_validate_seal(decisions, "decisions_sha256", "ArtView v4 decisions")
        except ValueError: findings.append({"code": "decision_seal_mismatch"})
    if decisions.get("schema") != DECISION_SCHEMA_V4 or decisions.get("scenario_id") != profile["scenario_id"]:
        findings.append({"code": "schema_or_scenario_mismatch"})
    if decisions.get("bindings") != expected_bindings:
        findings.append({"code": "binding_mismatch"})
    rows = manifest.get("rows") if isinstance(manifest.get("rows"), list) else []
    supplied = decisions.get("decisions") if isinstance(decisions.get("decisions"), list) else []
    if [item.get("asset_id") for item in supplied if isinstance(item, dict)] != [row.get("asset_id") for row in rows]:
        findings.append({"code": "decision_order_cardinality_or_duplicate"})
    unresolved: list[str] = []
    for row, item in zip(rows, supplied):
        if not isinstance(item, dict) or set(item) != {"asset_id", "binary", "presentation", "reviewed", "notes"} or item.get("asset_id") != row.get("asset_id"):
            findings.append({"code": "decision_row_closed_schema_mismatch"}); continue
        binary = item.get("binary")
        if not isinstance(binary, dict) or set(binary) != {"choice", "candidate_id"}:
            findings.append({"code": "unknown_asset_or_binary_shape", "asset_id": item["asset_id"]}); unresolved.append(item["asset_id"]); continue
        choice = binary.get("choice")
        if choice is not None and choice not in row.get("allowed_binary_decisions", []):
            findings.append({"code": "binary_decision_not_allowed", "asset_id": item["asset_id"]})
        candidate_ids = {candidate.get("candidate_id") for candidate in row.get("alternatives", []) if isinstance(candidate, dict)}
        if choice == "use_candidate" and binary.get("candidate_id") not in candidate_ids:
            findings.append({"code": "candidate_selection_mismatch", "asset_id": item["asset_id"]})
        if choice != "use_candidate" and binary.get("candidate_id") is not None:
            findings.append({"code": "unexpected_candidate_selection", "asset_id": item["asset_id"]})
        findings.extend(presentation_findings(item.get("presentation"), item["asset_id"]))
        if row.get("required") and choice in {"exclude", "needs_manual_work", "reopen_masters", None}:
            findings.append({"code": "required_placement_not_included", "asset_id": item["asset_id"], "placement_id": row.get("placement_id")})
        if item.get("reviewed") is not True or choice not in {"keep_current", "use_candidate", "exclude"}:
            unresolved.append(item["asset_id"])
    review = decisions.get("review")
    if not isinstance(review, dict) or set(review) != {"state", "reviewed_count", "unresolved_asset_ids"} or review.get("reviewed_count") != sum(item.get("reviewed") is True for item in supplied if isinstance(item, dict)) or review.get("unresolved_asset_ids") != unresolved:
        findings.append({"code": "review_summary_mismatch"})
    if require_accepted and (decisions.get("state") != "accepted" or not isinstance(review, dict) or review.get("state") != "closed" or unresolved):
        findings.append({"code": "accepted_full_closure_required", "asset_ids": unresolved})
    return {"schema": "kb_creator.scenario_artview_decision_validation.v4", "status": "pass" if not findings else "fail", "decision_count": len(supplied), "reviewed_count": sum(item.get("reviewed") is True for item in supplied if isinstance(item, dict)), "findings": findings}


def _v3_selected_binary(row: dict[str, Any], decision: dict[str, Any]) -> dict[str, Any] | None:
    binary = decision["binary"]
    if binary["choice"] == "keep_current":
        return row["current"]
    if binary["choice"] == "use_candidate":
        matches = [
            candidate["binary"]
            for candidate in row["alternatives"]
            if candidate["candidate_id"] == binary["candidate_id"]
        ]
        if len(matches) != 1:
            raise ValueError(f"selected candidate is missing or ambiguous: {decision['asset_id']}")
        return matches[0]
    if binary["choice"] == "exclude":
        return None
    raise ValueError(f"accepted decision is not final: {decision['asset_id']}")


def rebind_v3_decisions(
    source_profile_path: Path,
    source_candidate_manifest_path: Path,
    source_authority_root: Path,
    accepted_decisions_path: Path,
    target_profile_path: Path,
    target_candidate_manifest_path: Path,
    target_authority_root: Path,
    destination_path: Path,
) -> dict[str, Any]:
    """Rebind accepted v3 decisions only across exact review-evidence equivalence."""
    source_profile = _v3_authority_file(
        source_authority_root, source_profile_path, "source profile"
    )
    source_decisions = _v3_authority_file(
        source_authority_root, accepted_decisions_path, "accepted source decisions"
    )
    _v3_authority_file(
        source_authority_root,
        source_candidate_manifest_path,
        "source candidate manifest",
        expected_name="candidate_manifest.json",
    )
    target_profile = _v3_authority_file(
        target_authority_root, target_profile_path, "target profile"
    )
    _v3_authority_file(
        target_authority_root,
        target_candidate_manifest_path,
        "target candidate manifest",
        expected_name="candidate_manifest.json",
    )
    destination = _v3_absent_authority_file(
        target_authority_root, destination_path, "rebound decisions destination"
    )

    source_validation = validate_v3_decisions(
        source_profile,
        source_decisions,
        True,
        source_candidate_manifest_path,
        source_authority_root,
    )
    if source_validation["status"] != "pass":
        codes = ", ".join(row["code"] for row in source_validation["findings"])
        raise ValueError(f"accepted source decisions failed strict validation: {codes}")
    source_candidate = _v3_candidate_context(
        source_profile, source_candidate_manifest_path, source_authority_root
    )
    target_candidate = _v3_candidate_context(
        target_profile, target_candidate_manifest_path, target_authority_root
    )
    if target_candidate["findings"]:
        codes = ", ".join(row["code"] for row in target_candidate["findings"])
        raise ValueError(f"target candidate graph failed strict validation: {codes}")

    source_manifest = source_candidate["manifest"]
    target_manifest = target_candidate["manifest"]
    if source_manifest["scenario_id"] != target_manifest["scenario_id"]:
        raise ValueError("source and target scenario_id differ")
    source_asset_ids = [row["asset_id"] for row in source_manifest["rows"]]
    target_asset_ids = [row["asset_id"] for row in target_manifest["rows"]]
    if source_asset_ids != target_asset_ids:
        raise ValueError("source and target row order or cardinality differs")
    if source_manifest["rows"] != target_manifest["rows"]:
        raise ValueError("source and target user-visible decision evidence differs")
    if source_manifest["decision_contract"] != target_manifest["decision_contract"]:
        raise ValueError("source and target decision contracts differ")
    if source_manifest["derived_expected"] != target_manifest["derived_expected"]:
        raise ValueError("source and target derived counts differ")
    if (
        source_manifest["candidate_files_inventory_sha256"]
        != target_manifest["candidate_files_inventory_sha256"]
    ):
        raise ValueError("source and target candidate binary inventories differ")

    accepted = read_json(source_decisions)
    target_rows = {row["asset_id"]: row for row in target_manifest["rows"]}
    source_rows = {row["asset_id"]: row for row in source_manifest["rows"]}
    transferred = copy.deepcopy(accepted["decisions"])
    for decision in transferred:
        asset_id = decision["asset_id"]
        source_binary = _v3_selected_binary(source_rows[asset_id], decision)
        target_binary = _v3_selected_binary(target_rows[asset_id], decision)
        if source_binary != target_binary:
            raise ValueError(f"selected target binary is not exact equivalent: {asset_id}")

    unresolved = [
        item["asset_id"]
        for item in transferred
        if item["reviewed"] is not True
        or item["binary"]["choice"] not in {"keep_current", "use_candidate", "exclude"}
    ]
    if unresolved:
        raise ValueError("strictly accepted source decisions became unresolved")
    rebound = seal_v3_decisions(
        {
            "schema": DECISION_SCHEMA_V3,
            "scenario_id": target_manifest["scenario_id"],
            "state": "accepted",
            "bindings": decision_bindings(
                target_manifest, sha256_file(target_candidate["manifest_path"])
            ),
            "decisions": transferred,
            "review": {
                "state": "closed",
                "reviewed_count": sum(item["reviewed"] is True for item in transferred),
                "unresolved_asset_ids": unresolved,
            },
        }
    )
    serialized = json.dumps(rebound, ensure_ascii=False, sort_keys=True, indent=2) + "\n"
    with destination.open("x", encoding="utf-8", newline="\n") as handle:
        handle.write(serialized)
    target_validation = validate_v3_decisions(
        target_profile,
        destination,
        True,
        target_candidate_manifest_path,
        target_authority_root,
    )
    if target_validation["status"] != "pass":
        destination.unlink(missing_ok=True)
        codes = ", ".join(row["code"] for row in target_validation["findings"])
        raise ValueError(f"rebound decisions failed target validation: {codes}")
    return {
        "schema": "kb_creator.scenario_artview_decision_rebind.v1",
        "status": "pass",
        "scenario_id": target_manifest["scenario_id"],
        "decision_count": len(transferred),
        "source_decisions_sha256": sha256_file(source_decisions),
        "target_decisions_sha256": sha256_file(destination),
        "destination": str(destination),
    }


def _v4_rebind_candidate_context(
    profile_path: Path,
    candidate_manifest_path: Path,
    authority_root: Path,
) -> dict[str, Any]:
    """Validate the sealed, user-visible v4 candidate graph for rebinding."""
    profile, input_paths = _v4_profile(profile_path)
    manifest_path = _v3_explicit_candidate_manifest(authority_root, candidate_manifest_path)
    candidate_root = manifest_path.parent
    manifest = read_json(manifest_path)
    findings: list[dict[str, Any]] = []
    expected_keys = {
        "schema", "scenario_id", "state", "bindings", "derived_expected",
        "rows", "candidate_files_inventory_sha256", "decision_contract",
    }
    expected_bindings = {
        "profile": file_record(profile_path, profile_path.name),
        **{
            name: file_record(path, profile["inputs"][name]["path"])
            for name, path in input_paths.items()
        },
    }
    expected_contract = {
        "schema": DECISION_SCHEMA_V4,
        "binding_sources": [
            "profile", "master_ru", "master_ru_acceptance",
            "master_ru_asset_manifest", "reconstruction_inventory",
            "source_pdf", "source_identity",
        ],
        "accepted_requires_all_reviewed": True,
    }
    if (
        set(manifest) != expected_keys
        or manifest.get("schema") != CANDIDATE_SCHEMA_V4
        or manifest.get("scenario_id") != profile["scenario_id"]
        or manifest.get("state") != "candidate_needs_user_decisions"
        or not isinstance(manifest.get("rows"), list)
        or not isinstance(manifest.get("derived_expected"), dict)
    ):
        findings.append({"code": "candidate_manifest_shape_or_scenario"})
    if manifest.get("bindings") != expected_bindings:
        findings.append({"code": "candidate_manifest_binding_mismatch"})
    if manifest.get("decision_contract") != expected_contract:
        findings.append({"code": "candidate_decision_contract_mismatch"})

    binary_roots = {candidate_root / "assets", candidate_root / "context"}
    binary_rows = [
        file_record(path, path.relative_to(candidate_root).as_posix())
        for path in sorted(
            (
                item for item in candidate_root.rglob("*")
                if item.is_file() and any(root in item.parents for root in binary_roots)
            ),
            key=lambda item: item.relative_to(candidate_root).as_posix(),
        )
    ]
    inventory_sha = sha256_bytes(
        "".join(
            f"{row['path']}\t{row['bytes']}\t{row['sha256']}\n"
            for row in binary_rows
        ).encode("utf-8")
    )
    inventory_path = candidate_root / "candidate_files.inventory.json"
    inventory_doc = read_json(inventory_path) if inventory_path.is_file() else None
    expected_inventory = {
        "schema": "kb_creator.scenario_artview_candidate_files.v1",
        "algorithm": "sorted relative_path<TAB>bytes<TAB>UPPER_SHA256<LF>",
        "files": binary_rows,
        "sha256": inventory_sha,
    }
    if (
        inventory_doc != expected_inventory
        or manifest.get("candidate_files_inventory_sha256") != inventory_sha
    ):
        findings.append({"code": "candidate_binary_inventory_mismatch"})
    return {
        "profile": profile,
        "manifest": manifest,
        "manifest_path": manifest_path,
        "findings": findings,
    }


def rebind_v4_decisions(
    source_profile_path: Path,
    source_candidate_manifest_path: Path,
    source_authority_root: Path,
    accepted_decisions_path: Path,
    target_profile_path: Path,
    target_candidate_manifest_path: Path,
    target_authority_root: Path,
    destination_path: Path,
) -> dict[str, Any]:
    """Rebind accepted v4 choices only across an exact PDF-derived graph."""
    source_profile = _v3_authority_file(source_authority_root, source_profile_path, "source profile")
    source_decisions = _v3_authority_file(source_authority_root, accepted_decisions_path, "accepted source decisions")
    _v3_authority_file(source_authority_root, source_candidate_manifest_path, "source candidate manifest", expected_name="candidate_manifest.json")
    target_profile = _v3_authority_file(target_authority_root, target_profile_path, "target profile")
    _v3_authority_file(target_authority_root, target_candidate_manifest_path, "target candidate manifest", expected_name="candidate_manifest.json")
    destination = _v3_absent_authority_file(target_authority_root, destination_path, "rebound decisions destination")

    source_validation = validate_v4_decisions(
        source_profile, source_decisions, True,
        source_candidate_manifest_path, source_authority_root,
    )
    if source_validation["status"] != "pass":
        codes = ", ".join(row["code"] for row in source_validation["findings"])
        raise ValueError(f"accepted source decisions failed strict validation: {codes}")
    source_candidate = _v4_rebind_candidate_context(
        source_profile, source_candidate_manifest_path, source_authority_root,
    )
    target_candidate = _v4_rebind_candidate_context(
        target_profile, target_candidate_manifest_path, target_authority_root,
    )
    for label, candidate in (("source", source_candidate), ("target", target_candidate)):
        if candidate["findings"]:
            codes = ", ".join(row["code"] for row in candidate["findings"])
            raise ValueError(f"{label} candidate graph failed strict validation: {codes}")

    source_manifest = source_candidate["manifest"]
    target_manifest = target_candidate["manifest"]
    if source_manifest["scenario_id"] != target_manifest["scenario_id"]:
        raise ValueError("source and target scenario_id differ")
    if source_manifest["rows"] != target_manifest["rows"]:
        raise ValueError("source and target user-visible decision evidence differs")
    if source_manifest["decision_contract"] != target_manifest["decision_contract"]:
        raise ValueError("source and target decision contracts differ")
    if source_manifest["derived_expected"] != target_manifest["derived_expected"]:
        raise ValueError("source and target derived counts differ")
    if source_manifest["candidate_files_inventory_sha256"] != target_manifest["candidate_files_inventory_sha256"]:
        raise ValueError("source and target candidate binary inventories differ")

    accepted = read_json(source_decisions)
    transferred = copy.deepcopy(accepted["decisions"])
    for source_row, target_row, decision in zip(
        source_manifest["rows"], target_manifest["rows"], transferred,
    ):
        if _v3_selected_binary(source_row, decision) != _v3_selected_binary(target_row, decision):
            raise ValueError(f"selected target binary is not exact equivalent: {decision['asset_id']}")
    rebound = seal_v3_decisions({
        "schema": DECISION_SCHEMA_V4,
        "scenario_id": target_manifest["scenario_id"],
        "state": "accepted",
        "bindings": decision_bindings(target_manifest, sha256_file(target_candidate["manifest_path"])),
        "decisions": transferred,
        "review": copy.deepcopy(accepted["review"]),
    })
    with destination.open("x", encoding="utf-8", newline="\n") as handle:
        handle.write(json.dumps(rebound, ensure_ascii=False, sort_keys=True, indent=2) + "\n")
    target_validation = validate_v4_decisions(
        target_profile, destination, True,
        target_candidate_manifest_path, target_authority_root,
    )
    if target_validation["status"] != "pass":
        destination.unlink(missing_ok=True)
        codes = ", ".join(row["code"] for row in target_validation["findings"])
        raise ValueError(f"rebound decisions failed target validation: {codes}")
    return {
        "schema": "kb_creator.scenario_artview_decision_rebind.v2",
        "status": "pass",
        "scenario_id": target_manifest["scenario_id"],
        "decision_count": len(transferred),
        "source_decisions_sha256": sha256_file(source_decisions),
        "target_decisions_sha256": sha256_file(destination),
        "destination": str(destination),
    }


def rebind_decisions(
    source_profile_path: Path,
    source_candidate_manifest_path: Path,
    source_authority_root: Path,
    accepted_decisions_path: Path,
    target_profile_path: Path,
    target_candidate_manifest_path: Path,
    target_authority_root: Path,
    destination_path: Path,
) -> dict[str, Any]:
    """Dispatch strict rebinding without weakening either schema version."""
    source_profile = read_json(_v3_authority_file(source_authority_root, source_profile_path, "source profile"))
    target_profile = read_json(_v3_authority_file(target_authority_root, target_profile_path, "target profile"))
    if source_profile.get("schema") != target_profile.get("schema"):
        raise ValueError("source and target ArtView profile schemas differ")
    if source_profile.get("schema") == PROFILE_SCHEMA_V4:
        return rebind_v4_decisions(
            source_profile_path, source_candidate_manifest_path, source_authority_root,
            accepted_decisions_path, target_profile_path, target_candidate_manifest_path,
            target_authority_root, destination_path,
        )
    if source_profile.get("schema") == PROFILE_SCHEMA_V3:
        return rebind_v3_decisions(
            source_profile_path, source_candidate_manifest_path, source_authority_root,
            accepted_decisions_path, target_profile_path, target_candidate_manifest_path,
            target_authority_root, destination_path,
        )
    raise ValueError("unsupported ArtView profile schema for decision rebind")


def validate_decisions(profile_path: Path, decisions_path: Path, require_accepted: bool, candidate_manifest_path: Path | None = None, authority_root: Path | None = None) -> dict[str, Any]:
    profile = read_json(profile_path)
    if profile.get("schema") == PROFILE_SCHEMA_V4:
        return validate_v4_decisions(profile_path, decisions_path, require_accepted, candidate_manifest_path, authority_root)
    if profile.get("schema") == PROFILE_SCHEMA_V3:
        return validate_v3_decisions(profile_path, decisions_path, require_accepted, candidate_manifest_path, authority_root)
    if candidate_manifest_path is not None or authority_root is not None:
        raise ValueError("explicit candidate manifest is supported only for ArtView v3")
    candidate_root = resolve_repo(profile["output_root"]) / "candidate"
    manifest_path = candidate_root / "candidate_manifest.json"
    manifest = read_json(manifest_path)
    decisions = read_json(decisions_path)
    findings: list[dict[str, Any]] = []
    if decisions.get("schema") != DECISION_SCHEMA or decisions.get("scenario_id") != manifest.get("scenario_id"):
        findings.append({"code": "schema_or_scenario_mismatch"})
    expected_bindings = decision_bindings(manifest, sha256_file(manifest_path))
    if decisions.get("bindings") != expected_bindings:
        findings.append({"code": "binding_mismatch"})
    rows = {row["asset_id"]: row for row in manifest["rows"]}
    supplied = decisions.get("decisions") if isinstance(decisions.get("decisions"), list) else []
    if len(supplied) != len(rows) or len({item.get("asset_id") for item in supplied}) != len(supplied):
        findings.append({"code": "decision_cardinality_or_duplicate"})
    for item in supplied:
        row = rows.get(item.get("asset_id"))
        if not row:
            findings.append({"code": "unknown_asset_id", "asset_id": item.get("asset_id")})
            continue
        binary = item.get("binary") if isinstance(item.get("binary"), dict) else {}
        choice = binary.get("choice")
        candidate_id = binary.get("candidate_id")
        if choice is not None and choice not in row["allowed_binary_decisions"]:
            findings.append({"code": "binary_decision_not_allowed", "asset_id": item["asset_id"], "choice": choice})
        alternative_ids = {candidate["candidate_id"] for candidate in row["alternatives"]}
        if choice == "use_candidate" and candidate_id not in alternative_ids:
            findings.append({"code": "candidate_selection_mismatch", "asset_id": item["asset_id"]})
        if choice != "use_candidate" and candidate_id is not None:
            findings.append({"code": "unexpected_candidate_selection", "asset_id": item["asset_id"]})
        findings.extend(presentation_findings(item.get("presentation"), item["asset_id"]))
        if not isinstance(item.get("reviewed"), bool):
            findings.append({"code": "reviewed_flag_missing", "asset_id": item["asset_id"]})
    if require_accepted:
        if decisions.get("state") != "accepted":
            findings.append({"code": "accepted_state_required"})
        unresolved = [
            item.get("asset_id")
            for item in supplied
            if not item.get("reviewed")
            or (item.get("binary") or {}).get("choice") not in {"keep_current", "use_candidate", "exclude"}
        ]
        if unresolved:
            findings.append({"code": "unresolved_accepted_decisions", "asset_ids": unresolved})
    result = {
        "schema": "kb_creator.scenario_artview_decision_validation.v2",
        "status": "pass" if not findings else "fail",
        "decision_count": len(supplied),
        "findings": findings,
    }
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    build_parser = sub.add_parser("build")
    build_parser.add_argument("--profile", type=Path, required=True)
    build_parser.add_argument("--pdftoppm")
    build_parser.add_argument("--output-root", type=Path)
    build_parser.add_argument("--force", action="store_true")
    validate_parser = sub.add_parser("validate-decisions")
    validate_parser.add_argument("--profile", type=Path, required=True)
    validate_parser.add_argument("--decisions", type=Path, required=True)
    validate_parser.add_argument("--require-accepted", action="store_true")
    validate_parser.add_argument("--candidate-manifest", type=Path)
    validate_parser.add_argument("--authority-root", type=Path)
    rebind_parser = sub.add_parser(
        "rebind-decisions",
        help="rebind accepted v3/v4 decisions to an exactly equivalent fresh candidate",
    )
    rebind_parser.add_argument("--source-authority-root", type=Path, required=True)
    rebind_parser.add_argument("--source-profile", type=Path, required=True)
    rebind_parser.add_argument("--source-candidate-manifest", type=Path, required=True)
    rebind_parser.add_argument("--accepted-decisions", type=Path, required=True)
    rebind_parser.add_argument("--target-authority-root", type=Path, required=True)
    rebind_parser.add_argument("--target-profile", type=Path, required=True)
    rebind_parser.add_argument("--target-candidate-manifest", type=Path, required=True)
    rebind_parser.add_argument("--destination", type=Path, required=True)
    args = parser.parse_args()
    try:
        if args.command == "build":
            result = build(
                args.profile.resolve(),
                args.pdftoppm,
                args.force,
                args.output_root,
            )
        elif args.command == "validate-decisions":
            result = validate_decisions(args.profile.resolve(), args.decisions.resolve(), args.require_accepted, args.candidate_manifest, args.authority_root)
        else:
            result = rebind_decisions(
                args.source_profile,
                args.source_candidate_manifest,
                args.source_authority_root,
                args.accepted_decisions,
                args.target_profile,
                args.target_candidate_manifest,
                args.target_authority_root,
                args.destination,
            )
        print(json.dumps(result, ensure_ascii=False, sort_keys=True, indent=2))
        if result["status"] == "awaiting_artview_decisions":
            return 10
        return 0 if result["status"] == "pass" else 2
    except Exception as exc:
        print(json.dumps({"status": "fail", "error": f"{type(exc).__name__}: {exc}"}, ensure_ascii=False, indent=2), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
