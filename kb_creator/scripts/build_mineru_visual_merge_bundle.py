"""Build a visual review and neutral per-page merge bundle from three MinerU views."""

from __future__ import annotations

import argparse
from decimal import Decimal, InvalidOperation, ROUND_CEILING
import hashlib
import json
import ntpath
import os
import re
import shutil
import subprocess
import sys
import tempfile
from collections import Counter
from difflib import SequenceMatcher
from pathlib import Path, PureWindowsPath
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from kb_creator.pipeline.reconstruction import ControlPlaneError, validate_contract


VIEWS = ("original_hybrid", "original_pipeline_ocr", "raster_hybrid")
TRIPTYCH_LABELS = ("original_hybrid", "original_pipeline_ocr", "raster_hybrid")
CPU_TRIPTYCH = ("original_pipeline_txt", "original_pipeline_ocr", "raster_pipeline_ocr")
GEOMETRY_POLICY = "source_displayed_mediabox_v1"
DIMENSION_TOLERANCE_PT = Decimal("0.001")
ASPECT_TOLERANCE = Decimal("0.000005")
VIEW_INPUT_KIND = {
    "original_pipeline_txt": "original",
    "original_pipeline_ocr": "original",
    "raster_pipeline_ocr": "raster",
    "original_hybrid_high": "original",
    "original_vlm": "original",
}
ROLES = ((1, 5, "front_matter"), (6, 16, "introduction_investigator_material"), (17, 25, "one_night_in_perla"),
         (26, 68, "island_main_scenario"), (69, 103, "handouts"), (104, 110, "keeper_maps"),
         (111, 123, "pre_generated_investigators"), (124, 124, "back_cover"))


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def _seal(value: dict[str, Any], key: str) -> dict[str, Any]:
    unsigned = {name: item for name, item in value.items() if name != key}
    return {
        **unsigned,
        key: hashlib.sha256(
            json.dumps(unsigned, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
        ).hexdigest().upper(),
    }


class GeometryContractError(ValueError):
    def __init__(self, message: str, *, matrix: list[dict[str, Any]] | None = None, mismatch: dict[str, Any] | None = None):
        super().__init__(message)
        self.matrix = matrix or []
        self.mismatch = mismatch or {"kind": "geometry_contract", "detail": message}


def _decimal(value: object, label: str) -> Decimal:
    try:
        result = Decimal(str(value))
    except (InvalidOperation, ValueError) as exc:
        raise GeometryContractError(f"{label} must be decimal") from exc
    if not result.is_finite():
        raise GeometryContractError(f"{label} must be finite")
    return result


def _identity(path: Path, *, path_hint: str | None = None) -> dict[str, Any]:
    return {
        "path_hint": path_hint or path.name,
        "bytes": path.stat().st_size,
        "sha256": sha256_file(path),
    }


def _pdf_geometry(path: Path, source_pages: list[int], view_id: str) -> tuple[dict[str, Any], list[dict[str, Any]], dict[str, Any] | None]:
    try:
        from pypdf import PdfReader
    except ImportError as exc:  # pragma: no cover
        raise RuntimeError("requires pypdf") from exc
    reader = PdfReader(str(path))
    page_count_mismatch = None
    if len(reader.pages) != len(source_pages):
        page_count_mismatch = {"kind": "page_count", "view_id": view_id, "expected": len(source_pages), "actual": len(reader.pages)}
    rows: list[dict[str, Any]] = []
    for sample_page, page in enumerate(reader.pages, start=1):
        source_page = source_pages[sample_page - 1] if sample_page <= len(source_pages) else None
        media = [_decimal(value, "MediaBox") for value in (page.mediabox.left, page.mediabox.bottom, page.mediabox.right, page.mediabox.top)]
        crop = [_decimal(value, "CropBox") for value in (page.cropbox.left, page.cropbox.bottom, page.cropbox.right, page.cropbox.top)]
        width, height = media[2] - media[0], media[3] - media[1]
        rotation = int(page.get("/Rotate", 0)) % 360
        user_unit = _decimal(page.get("/UserUnit", 1), "UserUnit")
        effective = (width, height) if rotation in (0, 180) else (height, width)
        rows.append({
            "view_id": view_id,
            "sample_page": sample_page,
            "source_page": source_page,
            "media_box_coordinates": [str(value) for value in media],
            "crop_box_coordinates": [str(value) for value in crop],
            "rotation_degrees": rotation,
            "user_unit": str(user_unit),
            "effective_displayed_size_points": [str(value) for value in effective],
        })
    return _identity(path, path_hint=f"views/{view_id}/artifacts/{path.name}"), rows, page_count_mismatch


def _first_mismatch(
    matrix: list[dict[str, Any]],
    authority: list[dict[str, Any]],
    views: tuple[str, ...],
) -> dict[str, Any] | None:
    authority_by_page = {int(row["source_page"]): row for row in authority}
    order = {view: index for index, view in enumerate(views)}
    for row in sorted(matrix, key=lambda item: (int(item["source_page"]), order[item["view_id"]])):
        view, page = row["view_id"], int(row["source_page"])
        expected = authority_by_page.get(page)
        if expected is None:
            return {"kind": "source_page_order", "view_id": view, "source_page": page}
        rotation = row["rotation_degrees"]
        if rotation not in (0, 90, 180, 270):
            return {"kind": "rotation", "view_id": view, "source_page": page, "actual": rotation}
        try:
            user_unit = _decimal(row["user_unit"], "UserUnit")
            actual_width, actual_height = (_decimal(value, "displayed dimension") for value in row["effective_displayed_size_points"])
            expected_width, expected_height = (_decimal(value, "authoritative displayed dimension") for value in expected["displayed_page_size_points"])
        except (KeyError, TypeError, GeometryContractError):
            return {"kind": "invalid_numeric_geometry", "view_id": view, "source_page": page}
        if user_unit != Decimal("1"):
            return {"kind": "user_unit", "view_id": view, "source_page": page, "actual": row["user_unit"]}
        if VIEW_INPUT_KIND[view] == "raster" and rotation != 0:
            return {"kind": "raster_rotation", "view_id": view, "source_page": page, "actual": rotation}
        if actual_width <= 0 or actual_height <= 0:
            return {"kind": "nonpositive_dimension", "view_id": view, "source_page": page}
        if abs(actual_width - expected_width) > DIMENSION_TOLERANCE_PT or abs(actual_height - expected_height) > DIMENSION_TOLERANCE_PT:
            return {"kind": "displayed_dimension", "view_id": view, "source_page": page, "expected": [str(expected_width), str(expected_height)], "actual": [str(actual_width), str(actual_height)]}
        aspect_delta = abs((actual_width / actual_height) / (expected_width / expected_height) - Decimal("1"))
        if aspect_delta > ASPECT_TOLERANCE:
            return {"kind": "aspect_ratio", "view_id": view, "source_page": page, "delta": str(aspect_delta)}
    return None


def build_geometry_plan(
    *, prepared_manifest: dict[str, Any], prepared_identity: dict[str, Any], layouts: dict[str, Path],
    views: tuple[str, ...], dpi: int, renderer: dict[str, Any], run_identity_sha256: str,
    source_identity: dict[str, Any], comparison_identity: dict[str, Any], view_set_identity: dict[str, Any],
) -> dict[str, Any]:
    render = prepared_manifest.get("render")
    authority = render.get("page_geometry") if isinstance(render, dict) else None
    if (
        prepared_manifest.get("schema") not in {"kb_creator.mineru_three_view_inputs.v2", "kb_creator.mineru_three_view_inputs.v3"}
        or render.get("geometry_policy") != GEOMETRY_POLICY
        or render.get("source_box") != "MediaBox"
        or render.get("raster_has_text_layer") is not False
        or not isinstance(render.get("dpi"), int)
        or render["dpi"] <= 0
        or not isinstance(authority, list)
        or not authority
        or tuple(views[:3]) != CPU_TRIPTYCH
        or len(views) not in (3, 4, 5)
        or len(set(views)) != len(views)
        or any(view not in VIEW_INPUT_KIND for view in views)
    ):
        raise GeometryContractError("invalid CPU-first Stage 01 geometry authority or succeeded view plan")
    for row in authority:
        try:
            media = [_decimal(value, "source MediaBox") for value in row["media_box_coordinates"]]
            crop = [_decimal(value, "source CropBox") for value in row["crop_box_coordinates"]]
            raw = (media[2] - media[0], media[3] - media[1])
            rotation = row["source_rotation_degrees"]
            displayed = raw if rotation in (0, 180) else (raw[1], raw[0])
            recorded_displayed = tuple(_decimal(value, "displayed dimension") for value in row["displayed_page_size_points"])
            raster_canvas = tuple(_decimal(value, "raster PDF canvas") for value in row["raster_pdf_page_size_points"])
            pixels = [
                int((value * render["dpi"] / Decimal(72)).to_integral_value(rounding=ROUND_CEILING))
                for value in displayed
            ]
        except (IndexError, KeyError, TypeError, GeometryContractError) as exc:
            raise GeometryContractError("invalid Stage 01 authoritative page geometry") from exc
        if (
            len(media) != 4
            or len(crop) != 4
            or raw[0] <= 0
            or raw[1] <= 0
            or rotation not in (0, 90, 180, 270)
            or _decimal(row.get("source_user_unit"), "source UserUnit") != Decimal("1")
            or recorded_displayed != displayed
            or raster_canvas != displayed
            or row.get("raster_pdf_rotation_degrees") != 0
            or _decimal(row.get("raster_pdf_user_unit"), "raster UserUnit") != Decimal("1")
            or row.get("raster_pixel_dimensions") != pixels
        ):
            raise GeometryContractError("Stage 01 authoritative geometry is internally inconsistent")
    if prepared_manifest["schema"] == "kb_creator.mineru_three_view_inputs.v2" and any(row["displayed_page_size_points"] != authority[0]["displayed_page_size_points"] for row in authority[1:]):
        raise GeometryContractError("legacy Stage 01 authoritative displayed geometry is not uniform")
    source_pages = [int(row["source_page"]) for row in authority]
    ordered_pages = prepared_manifest.get("ordered_pages", [])
    if (
        source_pages != [row.get("source_page") for row in ordered_pages if isinstance(row, dict)]
        or [row.get("sample_page") for row in ordered_pages if isinstance(row, dict)] != list(range(1, len(source_pages) + 1))
        or len(source_pages) != len(set(source_pages))
    ):
        raise GeometryContractError("Stage 01 source page order mismatch")
    matrix: list[dict[str, Any]] = []
    layout_records: list[dict[str, Any]] = []
    page_count_mismatches: list[dict[str, Any]] = []
    for view in views:
        identity, rows, count_mismatch = _pdf_geometry(layouts[view], source_pages, view)
        layout_records.append({"view_id": view, "input_kind": VIEW_INPUT_KIND[view], "page_count": len(rows), "layout": identity})
        matrix.extend(rows)
        if count_mismatch is not None:
            page_count_mismatches.append(count_mismatch)
    if page_count_mismatches:
        raise GeometryContractError("layout page count mismatch", matrix=matrix, mismatch=page_count_mismatches[0])
    mismatch = _first_mismatch(matrix, authority, views)
    if mismatch is not None:
        raise GeometryContractError("layout geometry differs from Stage 01 authority", matrix=matrix, mismatch=mismatch)
    targets = []
    for row in authority:
        width, height = map(_decimal, row["displayed_page_size_points"], ("width", "height"))
        targets.append({
            "source_page": int(row["source_page"]),
            "displayed_size_points": [str(width), str(height)],
            "target_pixels": [
                int((width * dpi / Decimal(72)).to_integral_value(rounding=ROUND_CEILING)),
                int((height * dpi / Decimal(72)).to_integral_value(rounding=ROUND_CEILING)),
            ],
        })
    return {
        "schema": "kb_creator.mineru_geometry_plan.v1",
        "policy": GEOMETRY_POLICY,
        "run_identity_sha256": run_identity_sha256,
        "preparation_manifest": prepared_identity,
        "source": source_identity,
        "comparison": comparison_identity,
        "view_set": view_set_identity,
        "review_dpi": dpi,
        "rounding_rule": "ceil(points*dpi/72)",
        "tolerances": {"dimension_points": "0.001", "relative_aspect_ratio": "0.000005", "pixels": 0},
        "renderer": renderer,
        "succeeded_views": list(views),
        "layouts": layout_records,
        "observed_geometry": matrix,
        "targets": targets,
        "transforms": {"pad": False, "crop": False, "post_render_resize": False},
        "rendered_pages": [],
    }


def _write_geometry_failure(
    output_root: Path, *, error: GeometryContractError, identities: dict[str, Any], renderer: dict[str, Any], views: tuple[str, ...], dpi: int,
) -> None:
    if output_root.exists() and any(output_root.iterdir()):
        raise FileExistsError(f"refusing non-empty geometry failure root: {output_root}")
    output_root.mkdir(parents=True, exist_ok=True)
    receipt = _seal({
        "schema": "kb_creator.mineru_geometry_failure.v1",
        "policy": GEOMETRY_POLICY,
        "inputs": identities,
        "renderer": renderer,
        "review_dpi": dpi,
        "succeeded_views": list(views),
        "first_mismatch": error.mismatch,
        "observed_geometry": error.matrix,
        "outputs_created": [],
    }, "failure_sha256")
    temporary = output_root / ".geometry-failure.json.tmp"
    temporary.write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    os.replace(temporary, output_root / "geometry-failure.json")


def role_for_page(page: int, roles: tuple[tuple[int, int, str], ...] = ROLES) -> str:
    for first, last, role in roles:
        if first <= page <= last:
            return role
    raise ValueError(f"source page outside canonical role ranges: {page}")


def safe_relative(value: str) -> str:
    path = PureWindowsPath(value)
    if not value or value.startswith(("/", "\\")) or path.is_absolute() or path.drive or ".." in path.parts:
        raise ValueError(f"unsafe artifact reference: {value!r}")
    return path.as_posix()


def _require_hash(path: Path, expected: str, label: str) -> dict[str, str]:
    if not path.is_file():
        raise FileNotFoundError(f"missing {label}: {path}")
    actual = sha256_file(path)
    if actual != expected.upper():
        raise ValueError(f"{label} SHA-256 mismatch")
    return {"path": str(path.resolve()), "sha256": actual}


def _replay_ref(path: Path, reference: dict[str, Any], *, base: str, view_roots: dict[str, Path] | None = None) -> Path:
    """Resolve a replay v3 typed reference without accepting an operational path."""
    try:
        from kb_creator.pipeline import reconstruction_replay as replay
        root = path.parent.parent
        resolved = replay.resolve_reference(root, {key: value for key, value in reference.items() if key != "receipt_sha256"}, view_roots)
        if reference.get("base") != base or not resolved.is_file():
            raise ValueError("unexpected typed replay reference")
        return resolved
    except (ValueError, KeyError, OSError) as error:
        raise ValueError("invalid replay typed reference") from error


def _load_replayed_cpu_inputs(data: dict[str, Any], receipt: dict[str, Any], raw_root: Path, prepared_manifest: Path) -> None:
    """Validate replay v3/v2 wrappers and their fresh, typed reference graph."""
    try:
        from kb_creator.pipeline import reconstruction_replay as replay
        replay._validate_view_set_v2(receipt)
        replay._validate_comparison_v3(data)
    except (ValueError, KeyError) as error:
        raise ValueError("invalid sealed replay comparison or view set") from error
    if data["run_identity_sha256"] != receipt["run_identity_sha256"] or data["succeeded_views"] != receipt["succeeded_views"] or data["succeeded_views"][:3] != list(CPU_TRIPTYCH):
        raise ValueError("replay comparison/view set identity or triptych mismatch")
    view_roots = {row["view_id"]: raw_root / "views" / row["view_id"] / "artifacts" for row in receipt["views"] if row["state"] == "succeeded"}
    for row in receipt["views"]:
        view_path = raw_root / row["receipt"]["path"]
        if not view_path.is_file() or view_path.stat().st_size != row["receipt"]["bytes"] or sha256_file(view_path) != row["receipt"]["sha256"]:
            raise ValueError("replay view receipt identity mismatch")
        view = json.loads(view_path.read_text(encoding="utf-8"))
        try:
            replay._validate_view_v2(view)
        except (ValueError, KeyError) as error:
            raise ValueError("invalid sealed replay view receipt") from error
        if view["run_identity_sha256"] != data["run_identity_sha256"] or view["receipt_sha256"] != row["receipt"]["receipt_sha256"]:
            raise ValueError("replay view receipt fresh identity mismatch")
    prepared_ref = _replay_ref(raw_root, data["manifest"], base="stage_01_root", view_roots=view_roots)
    receipt_ref = _replay_ref(raw_root, data["view_set"], base="stage_02_root", view_roots=view_roots)
    if (
        prepared_ref.resolve() != prepared_manifest.resolve()
        or receipt_ref.resolve() != (raw_root / "view-set.json").resolve()
        or data["view_set"].get("receipt_sha256") != receipt["receipt_sha256"]
    ):
        raise ValueError("replay comparison references different preparation or view-set authority")
    expected_indices = list(range(len(json.loads(prepared_manifest.read_text(encoding="utf-8"))["ordered_pages"])))
    for view_id, row in data["views"].items():
        coverage = row["coverage"]
        if not isinstance(coverage, dict) or coverage.get("expected_page_idx") != expected_indices or coverage.get("actual_page_idx") != expected_indices or coverage.get("missing_page_idx") != [] or coverage.get("extra_page_idx") != []:
            raise ValueError("replay view page coverage mismatch")
        for reference in row["artifacts"].values():
            _replay_ref(raw_root, reference, base="view_artifact_root", view_roots=view_roots)


def _load_inputs(raw_receipt: Path, receipt_sha: str, source: Path, source_sha: str, comparison: Path, comparison_sha: str, raw_root: Path, dpi: int, prepared_manifest: Path | None = None, prepared_manifest_sha: str | None = None) -> tuple[dict[str, Any], dict[str, Any]]:
    if dpi <= 0:
        raise ValueError("dpi must be positive")
    identities = {
        "raw_receipt": _require_hash(raw_receipt, receipt_sha, "raw receipt"),
        "source": _require_hash(source, source_sha, "source PDF"),
        "comparison": _require_hash(comparison, comparison_sha, "comparison JSON"),
        "raw_root": str(raw_root.resolve()), "dpi": dpi,
    }
    data = json.loads(comparison.read_text(encoding="utf-8"))
    if data.get("schema") in {"kb_creator.mineru_multi_view_comparison.v2", "kb_creator.mineru_multi_view_comparison.v3"}:
        if prepared_manifest is None or prepared_manifest_sha is None:
            raise ValueError("CPU-first comparison requires an exact preparation manifest")
        identities["preparation_manifest"] = _require_hash(prepared_manifest, prepared_manifest_sha, "preparation manifest")
        receipt = json.loads(raw_receipt.read_text(encoding="utf-8"))
        expected_receipt_seal = receipt.get("receipt_sha256")
        unsigned_receipt = {key: value for key, value in receipt.items() if key != "receipt_sha256"}
        if data.get("schema") == "kb_creator.mineru_multi_view_comparison.v3":
            _load_replayed_cpu_inputs(data, receipt, raw_root, prepared_manifest)
        elif (
            receipt.get("schema") != "kb_creator.mineru_view_set.v1"
            or expected_receipt_seal != hashlib.sha256(
                json.dumps(unsigned_receipt, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
            ).hexdigest().upper()
            or data.get("run_identity_sha256") != receipt.get("run_identity_sha256")
            or data.get("succeeded_views") != receipt.get("succeeded_views")
            or data.get("view_set")
            != {
                "path": str(raw_receipt),
                "bytes": raw_receipt.stat().st_size,
                "sha256": sha256_file(raw_receipt),
                "receipt_sha256": expected_receipt_seal,
            }
            or data.get("manifest") != {
                "path": str(prepared_manifest),
                "bytes": prepared_manifest.stat().st_size,
                "sha256": sha256_file(prepared_manifest),
            }
        ):
            raise ValueError("comparison does not bind the exact sealed CPU-first view set")
        succeeded = data.get("succeeded_views")
        if data.get("status") != "pass_for_review" or not isinstance(succeeded, list) or succeeded[:3] != list(CPU_TRIPTYCH) or list(data.get("views", {})) != succeeded:
            raise ValueError("comparison must preserve the required CPU triptych")
    elif data.get("status") != "pass" or set(data.get("views", {})) != set(VIEWS):
        raise ValueError("comparison must be a passing three-view comparison")
    return identities, data


def _check_resume(output_root: Path, identities: dict[str, Any], resume: bool, expected_plan: dict[str, Any] | None = None) -> dict[str, Any] | None:
    if not output_root.exists() or not any(output_root.iterdir()):
        return None
    manifest_path = output_root / "visual" / "visual_manifest.json"
    if not resume or not manifest_path.is_file():
        raise FileExistsError(f"refusing non-empty output root: {output_root}")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if manifest.get("schema") == "kb_creator.mineru_visual_merge_bundle.v2":
        validate_v2_bundle(output_root, manifest, expected_inputs=identities, expected_plan=expected_plan)
        return manifest
    if manifest.get("inputs") != identities:
        raise ValueError("resume manifest does not prove the same owned bundle")
    for record in manifest.get("files", []):
        path = output_root / safe_relative(record.get("path", ""))
        if not path.is_file() or sha256_file(path) != record.get("sha256"):
            raise ValueError("resume visual inventory is incomplete or changed")
    required = output_root / "merge_packets" / "merge_index.json"
    if not required.is_file():
        raise ValueError("resume bundle lacks merge index")
    return manifest


def find_layout_pdf(raw_root: Path, view: str, *, cpu_first: bool = False) -> Path:
    root = raw_root / ("views" if cpu_first else "runs") / view
    if cpu_first:
        root = root / "artifacts"
    matches = sorted(root.rglob("*_layout.pdf"))
    if len(matches) != 1:
        raise ValueError(f"{view}: expected exactly one layout PDF, found {len(matches)}")
    return matches[0]


def poppler_path_argument(path: str | os.PathLike[str], *, platform: str | None = None) -> str:
    """Return an absolute path spelling that Poppler can pass to the OS."""
    selected_platform = os.name if platform is None else platform
    raw_path = os.fspath(path)
    if selected_platform != "nt":
        return str(Path(raw_path).resolve())
    if raw_path.startswith("\\\\?\\"):
        return raw_path
    if not ntpath.isabs(raw_path):
        raise ValueError(f"Poppler Windows path must be absolute: {raw_path}")
    absolute = ntpath.abspath(raw_path)
    if absolute.startswith("\\\\"):
        return "\\\\?\\UNC\\" + absolute[2:]
    return "\\\\?\\" + absolute


def _logical_poppler_path(path: str | os.PathLike[str], *, platform: str | None = None) -> str | None:
    selected_platform = os.name if platform is None else platform
    raw_path = os.fspath(path)
    if selected_platform != "nt":
        candidate = Path(raw_path)
        return str(candidate.resolve()) if candidate.is_absolute() else None
    if raw_path.startswith("\\\\?\\UNC\\"):
        raw_path = "\\\\" + raw_path[8:]
    elif raw_path.startswith("\\\\?\\"):
        raw_path = raw_path[4:]
    if not ntpath.isabs(raw_path):
        return None
    return ntpath.normcase(ntpath.normpath(raw_path))


def poppler_paths_equivalent(left: str | os.PathLike[str], right: str | os.PathLike[str], *, platform: str | None = None) -> bool:
    """Compare only absolute Poppler paths, accepting Windows extended spelling."""
    left_logical = _logical_poppler_path(left, platform=platform)
    right_logical = _logical_poppler_path(right, platform=platform)
    return left_logical is not None and left_logical == right_logical


def poppler_render_prefix_is_valid(path: str | os.PathLike[str], *, platform: str | None = None) -> bool:
    """Require an absolute Poppler output prefix whose logical basename is _render."""
    selected_platform = os.name if platform is None else platform
    logical_path = _logical_poppler_path(path, platform=selected_platform)
    if logical_path is None:
        return False
    path_module = ntpath if selected_platform == "nt" else os.path
    expected = path_module.join(path_module.dirname(logical_path), "_render")
    return poppler_paths_equivalent(path, expected, platform=selected_platform)


def _bounded_child_output(value: str | None, *, limit: int = 2000) -> str:
    text = (value or "").strip()
    if len(text) <= limit:
        return text
    return text[:limit] + "... [truncated]"


def ordered_rendered_pages(target: Path, expected_pages: int) -> list[Path]:
    numbered: dict[int, Path] = {}
    pattern = re.compile(r"^_render-(\d+)\.png$")
    for path in target.glob("_render-*.png"):
        match = pattern.fullmatch(path.name)
        if match is None:
            raise ValueError(f"unexpected Poppler rendered filename: {path.name}")
        page = int(match.group(1))
        if page in numbered:
            raise ValueError(f"duplicate Poppler rendered page suffix: {page}")
        numbered[page] = path
    expected = list(range(1, expected_pages + 1))
    if sorted(numbered) != expected:
        raise ValueError(f"rendered page suffixes are not exactly 1..{expected_pages}: {sorted(numbered)}")
    return [numbered[page] for page in expected]


def _validate_rendered_pngs(paths: list[Path]) -> None:
    """Reject unreadable or dimensionless Poppler output before it reaches the bundle."""
    Image, _, _ = _image_lib()
    for path in paths:
        with Image.open(path) as image:
            if image.format != "PNG" or image.width < 1 or image.height < 1:
                raise ValueError(f"invalid rendered PNG: {path.name}")
            image.verify()


def _render_inventory(target: Path) -> list[str]:
    if not target.is_dir():
        return []
    return sorted(path.name for path in target.iterdir())


def render_layouts(layouts: dict[str, Path], visual_root: Path, pdftoppm: str, dpi: int, expected_pages: int, views: tuple[str, ...] = VIEWS) -> tuple[dict[str, list[Path]], list[list[str]], str]:
    result: dict[str, list[Path]] = {}
    commands: list[list[str]] = []
    version = subprocess.run([pdftoppm, "-v"], check=True, capture_output=True, text=True)
    version_text = (version.stdout + version.stderr).strip()
    # Poppler 26.02 may return success without creating files when its output
    # prefix exceeds the Win32 path limit.  Its input remains the bound layout;
    # only the transient renderer output moves to an owned short scratch root.
    with tempfile.TemporaryDirectory(prefix="kb-render-") as scratch_root:
        scratch_root_path = Path(scratch_root)
        for view in views:
            target = visual_root / view / "pages"
            target.mkdir(parents=True, exist_ok=True)
            scratch_target = scratch_root_path / view
            scratch_target.mkdir()
            temporary_prefix = scratch_target / "_render"
            logical_input = layouts[view]
            command = [pdftoppm, "-r", str(dpi), "-png", "-f", "1", "-l", str(expected_pages), poppler_path_argument(logical_input), poppler_path_argument(temporary_prefix)]
            try:
                completed = subprocess.run(command, check=True, capture_output=True, text=True)
            except subprocess.CalledProcessError as error:
                raise RuntimeError(
                    f"Poppler render failed for view={view}; exit_code={error.returncode}; "
                    f"input_chars={len(str(logical_input))}; output_prefix_chars={len(str(temporary_prefix))}; "
                    f"output_inventory={_render_inventory(scratch_target)!r}; "
                    f"stderr={_bounded_child_output(error.stderr)!r}; stdout={_bounded_child_output(error.stdout)!r}"
                ) from error
            commands.append(command)
            try:
                rendered = ordered_rendered_pages(scratch_target, expected_pages)
                _validate_rendered_pngs(rendered)
            except ValueError as error:
                raise RuntimeError(
                    f"Poppler render produced invalid pages for view={view}; exit_code={completed.returncode}; "
                    f"input_chars={len(str(logical_input))}; output_prefix_chars={len(str(temporary_prefix))}; "
                    f"output_inventory={_render_inventory(scratch_target)!r}; "
                    f"stderr={_bounded_child_output(completed.stderr)!r}; stdout={_bounded_child_output(completed.stdout)!r}"
                ) from error
            pages = []
            for index, path in enumerate(rendered, start=1):
                destination = target / f"page-{index:03d}.png"
                shutil.copyfile(path, destination)
                if sha256_file(path) != sha256_file(destination):
                    raise RuntimeError(f"rendered PNG copy changed bytes for view={view}; page={index}")
                pages.append(destination)
            result[view] = pages
    return result, commands, version_text


def _image_lib() -> tuple[Any, Any, Any]:
    try:
        from PIL import Image, ImageDraw, ImageFont
    except ImportError as exc:  # pragma: no cover
        raise RuntimeError("requires Pillow") from exc
    return Image, ImageDraw, ImageFont


def build_triptychs(rendered: dict[str, list[Path]], destination: Path, views: tuple[str, ...] = VIEWS) -> list[Path]:
    Image, ImageDraw, ImageFont = _image_lib()
    destination.mkdir(parents=True, exist_ok=True)
    font = ImageFont.load_default()
    outputs = []
    for page in range(1, len(rendered[views[0]]) + 1):
        images = [Image.open(rendered[view][page - 1]).convert("RGB") for view in views]
        try:
            width, height = images[0].size
            if any(image.size != (width, height) for image in images):
                raise ValueError("rendered view dimensions differ")
            canvas = Image.new("RGB", (width * 3, height + 18), "white")
            draw = ImageDraw.Draw(canvas)
            for index, (view, image) in enumerate(zip(views, images)):
                canvas.paste(image, (index * width, 18))
                draw.text((index * width + 2, 2), view, fill="black", font=font)
            draw.text((width * 3 - 72, 2), f"page {page:03d}", fill="black", font=font)
            output = destination / f"page-{page:03d}.png"
            canvas.save(output)
            outputs.append(output)
        finally:
            for image in images:
                image.close()
    return outputs


def build_optional_companions(rendered: dict[str, list[Path]], destination: Path, views: tuple[str, ...]) -> list[Path]:
    """Add labeled optional panels without changing any rendered view pixels."""
    Image, ImageDraw, ImageFont = _image_lib()
    destination.mkdir(parents=True, exist_ok=True)
    font = ImageFont.load_default()
    outputs: list[Path] = []
    for view in views:
        view_root = destination / view
        view_root.mkdir(parents=True, exist_ok=True)
        for page, source in enumerate(rendered[view], start=1):
            with Image.open(source) as opened:
                image = opened.convert("RGB")
                canvas = Image.new("RGB", (image.width, image.height + 18), "white")
                canvas.paste(image, (0, 18))
                ImageDraw.Draw(canvas).text((2, 2), f"{view} page {page:03d}", fill="black", font=font)
                output = view_root / f"page-{page:03d}.png"
                canvas.save(output)
                outputs.append(output)
    return outputs


def _renderer_identity(pdftoppm: str) -> tuple[dict[str, Any], str]:
    executable = Path(pdftoppm).resolve()
    if not executable.is_file():
        raise FileNotFoundError(f"missing pdftoppm: {executable}")
    completed = subprocess.run([str(executable), "-v"], check=True, capture_output=True, text=True)
    version = (completed.stdout + completed.stderr).strip()
    if not version:
        raise ValueError("pdftoppm version is empty")
    return {**_identity(executable, path_hint=executable.name), "version": version, "argv_recipe": "pdftoppm-mediabox-png-v1"}, version


def _attach_render_evidence(plan: dict[str, Any], rendered: dict[str, list[Path]], root: Path) -> dict[str, Any]:
    Image, _, _ = _image_lib()
    targets = {row["source_page"]: row["target_pixels"] for row in plan["targets"]}
    source_pages = [row["source_page"] for row in plan["targets"]]
    records: list[dict[str, Any]] = []
    for view in plan["succeeded_views"]:
        pages = rendered[view]
        if len(pages) != len(source_pages):
            raise GeometryContractError("rendered page count mismatch")
        for source_page, path in zip(source_pages, pages):
            with Image.open(path) as image:
                dimensions, mode = list(image.size), image.mode
            if dimensions != targets[source_page]:
                raise GeometryContractError(
                    "rendered page dimensions differ from canonical target",
                    mismatch={"kind": "rendered_pixels", "view_id": view, "source_page": source_page, "expected": targets[source_page], "actual": dimensions},
                )
            if mode != "RGB":
                raise GeometryContractError(
                    "rendered PNG mode must be RGB",
                    mismatch={"kind": "png_mode", "view_id": view, "source_page": source_page, "expected": "RGB", "actual": mode},
                )
            records.append({"view_id": view, "source_page": source_page, "path": path.relative_to(root).as_posix(), "dimensions": dimensions, "mode": mode, "bytes": path.stat().st_size, "sha256": sha256_file(path)})
    return _seal({**plan, "rendered_pages": records}, "plan_sha256")


def validate_v2_bundle(output_root: Path, manifest: dict[str, Any], *, expected_inputs: dict[str, Any] | None = None, expected_plan: dict[str, Any] | None = None) -> None:
    if set(manifest) != {"schema", "inputs", "layouts", "execution", "counts", "inventory_scope", "inventory_exclusions", "files", "geometry_plan", "manifest_sha256"}:
        raise ValueError("v2 visual bundle shape mismatch")
    if manifest.get("schema") != "kb_creator.mineru_visual_merge_bundle.v2":
        raise ValueError("expected v2 visual bundle")
    if manifest.get("inventory_scope") != "all generated files except the three explicitly listed adapter/self-referential records" or manifest.get("inventory_exclusions") != ["visual/visual_manifest.json", "evidence/execution.json", "command.json"]:
        raise ValueError("visual bundle inventory scope mismatch")
    if _seal(manifest, "manifest_sha256")["manifest_sha256"] != manifest.get("manifest_sha256"):
        raise ValueError("visual bundle seal mismatch")
    if expected_inputs is not None and manifest.get("inputs") != expected_inputs:
        raise ValueError("visual bundle inputs changed")
    inputs = manifest.get("inputs")
    required_inputs = {"raw_receipt", "source", "comparison", "raw_root", "dpi", "preparation_manifest"}
    if not isinstance(inputs, dict) or not required_inputs.issubset(inputs) or set(inputs) - required_inputs not in (set(), {"reconstruction_contract"}):
        raise ValueError("visual bundle input shape mismatch")
    for name in required_inputs - {"raw_root", "dpi"} | ({"reconstruction_contract"} if "reconstruction_contract" in inputs else set()):
        if not isinstance(inputs[name], dict) or set(inputs[name]) != {"path", "sha256"}:
            raise ValueError("visual bundle input identity shape mismatch")
    if not isinstance(inputs["raw_root"], str) or not isinstance(inputs["dpi"], int) or inputs["dpi"] <= 0:
        raise ValueError("visual bundle local input shape mismatch")
    if not isinstance(manifest.get("geometry_plan"), dict) or set(manifest["geometry_plan"]) != {"path", "bytes", "sha256", "plan_sha256"}:
        raise ValueError("geometry plan record shape mismatch")
    plan_path = output_root / safe_relative(manifest.get("geometry_plan", {}).get("path", ""))
    record = manifest.get("geometry_plan")
    if not isinstance(record, dict) or not plan_path.is_file() or {"path": record.get("path"), **_identity(plan_path, path_hint=record.get("path"))} != {"path": record.get("path"), "path_hint": record.get("path"), "bytes": record.get("bytes"), "sha256": record.get("sha256")}:
        raise ValueError("geometry plan identity mismatch")
    plan = json.loads(plan_path.read_text(encoding="utf-8"))
    if set(plan) != {"schema", "policy", "run_identity_sha256", "preparation_manifest", "source", "comparison", "view_set", "review_dpi", "rounding_rule", "tolerances", "renderer", "succeeded_views", "layouts", "observed_geometry", "targets", "transforms", "rendered_pages", "plan_sha256"}:
        raise ValueError("geometry plan shape mismatch")
    if _seal(plan, "plan_sha256")["plan_sha256"] != plan.get("plan_sha256") or plan.get("plan_sha256") != record.get("plan_sha256"):
        raise ValueError("geometry plan seal mismatch")
    if expected_plan is not None:
        current_base = {key: value for key, value in plan.items() if key not in {"rendered_pages", "plan_sha256"}}
        expected_base = {key: value for key, value in expected_plan.items() if key not in {"rendered_pages", "plan_sha256"}}
        if current_base != expected_base:
            raise ValueError("geometry plan no longer matches current sealed inputs")
    if plan.get("transforms") != {"pad": False, "crop": False, "post_render_resize": False}:
        raise ValueError("geometry transform prohibition changed")
    for name in ("preparation_manifest", "source", "comparison"):
        if not isinstance(plan.get(name), dict) or set(plan[name]) != {"path_hint", "bytes", "sha256"}:
            raise ValueError("geometry input identity shape mismatch")
    if not isinstance(plan.get("view_set"), dict) or set(plan["view_set"]) != {"path_hint", "bytes", "sha256", "receipt_sha256"}:
        raise ValueError("geometry view-set identity shape mismatch")
    if not isinstance(plan.get("renderer"), dict) or set(plan["renderer"]) != {"path_hint", "bytes", "sha256", "version", "argv_recipe"}:
        raise ValueError("geometry renderer identity shape mismatch")
    views = plan.get("succeeded_views")
    targets = plan.get("targets")
    if (
        not isinstance(views, list)
        or views[:3] != list(CPU_TRIPTYCH)
        or len(views) not in (3, 4, 5)
        or len(set(views)) != len(views)
        or list(manifest.get("layouts", {})) != views
        or [row.get("view_id") for row in plan.get("layouts", [])] != views
        or not isinstance(targets, list)
        or not targets
        or any(not isinstance(row.get("source_page"), int) or row["source_page"] < 1 for row in targets)
        or len({row["source_page"] for row in targets}) != len(targets)
    ):
        raise ValueError("geometry plan view/page topology mismatch")
    execution = manifest.get("execution")
    commands = execution.get("commands") if isinstance(execution, dict) else None
    if not isinstance(commands, list) or len(commands) != len(views) or execution.get("pdftoppm_version") != plan.get("renderer", {}).get("version"):
        raise ValueError("render execution evidence mismatch")
    expected_pages = len(targets)
    layout_map = manifest["layouts"]
    if any(not isinstance(value, dict) or set(value) != {"path", "sha256"} for value in layout_map.values()):
        raise ValueError("visual layout identity shape mismatch")
    if any(not isinstance(row, dict) or set(row) != {"view_id", "input_kind", "page_count", "layout"} or not isinstance(row.get("layout"), dict) or set(row["layout"]) != {"path_hint", "bytes", "sha256"} for row in plan["layouts"]):
        raise ValueError("geometry layout record shape mismatch")
    for row in plan["layouts"]:
        public = layout_map[row["view_id"]]
        if row["layout"]["sha256"] != public["sha256"] or Path(row["layout"]["path_hint"]).name != Path(public["path"]).name:
            raise ValueError("geometry and visual layout identities differ")
    if any(not isinstance(row, dict) or set(row) != {"view_id", "sample_page", "source_page", "media_box_coordinates", "crop_box_coordinates", "rotation_degrees", "user_unit", "effective_displayed_size_points"} for row in plan.get("observed_geometry", [])):
        raise ValueError("observed geometry record shape mismatch")
    if any(not isinstance(row, dict) or set(row) != {"source_page", "displayed_size_points", "target_pixels"} for row in targets):
        raise ValueError("geometry target record shape mismatch")
    for view, command in zip(views, commands):
        expected_prefix = ["-r", str(plan["review_dpi"]), "-png", "-f", "1", "-l", str(expected_pages)]
        if (
            not isinstance(command, list)
            or command[1:8] != expected_prefix
            or len(command) != 10
            or not poppler_paths_equivalent(command[-2], layout_map[view]["path"])
            or not poppler_render_prefix_is_valid(command[-1])
        ):
            raise ValueError("render argv is not the exact MediaBox recipe")
    actual_files = []
    for item in manifest.get("files", []):
        if not isinstance(item, dict) or set(item) not in ({"path", "bytes", "sha256"}, {"path", "bytes", "sha256", "dimensions"}):
            raise ValueError("visual inventory record shape mismatch")
        path = output_root / safe_relative(item.get("path", ""))
        if not path.is_file() or _identity(path, path_hint=item["path"]) != {"path_hint": item["path"], "bytes": item.get("bytes"), "sha256": item.get("sha256")}:
            raise ValueError("visual bundle inventory changed")
        actual_files.append(item["path"])
    if len(actual_files) != len(set(actual_files)):
        raise ValueError("visual bundle inventory contains duplicates")
    exclusions = set(manifest.get("inventory_exclusions", []))
    observed_files = {
        path.relative_to(output_root).as_posix()
        for path in output_root.rglob("*")
        if path.is_file() and path.relative_to(output_root).as_posix() not in exclusions
    }
    if observed_files != set(actual_files):
        raise ValueError("visual bundle inventory is not complete")
    expected_paths = {"visual/geometry_plan.json", "merge_packets/merge_index.json", "merge_packets/merge_index.md"}
    for sample_page in range(1, expected_pages + 1):
        expected_paths.update({
            f"visual/triptychs/page-{sample_page:03d}.png",
            f"merge_packets/pages/page-{sample_page:03d}.json",
            f"merge_packets/pages/page-{sample_page:03d}.md",
        })
        for view in views:
            expected_paths.add(f"visual/{view}/pages/page-{sample_page:03d}.png")
        for view in views[3:]:
            expected_paths.add(f"visual/companions/{view}/page-{sample_page:03d}.png")
    for start in range(1, expected_pages + 1, 4):
        last = min(start + 3, expected_pages)
        expected_paths.add(f"visual/contact_sheets/pages-{start:03d}-{last:03d}.png")
    if set(actual_files) != expected_paths:
        raise ValueError("visual bundle file topology mismatch")
    rendered = plan.get("rendered_pages")
    expected_rendered = len(plan.get("targets", [])) * len(plan.get("succeeded_views", []))
    if not isinstance(rendered, list) or len(rendered) != expected_rendered:
        raise ValueError("geometry plan render evidence is incomplete")
    Image, _, _ = _image_lib()
    for row in rendered:
        if not isinstance(row, dict) or set(row) != {"view_id", "source_page", "path", "dimensions", "mode", "bytes", "sha256"}:
            raise ValueError("rendered PNG evidence shape mismatch")
        path = output_root / safe_relative(row["path"])
        if not path.is_file() or sha256_file(path) != row["sha256"] or path.stat().st_size != row["bytes"]:
            raise ValueError("rendered PNG identity changed")
        with Image.open(path) as image:
            if list(image.size) != row["dimensions"] or image.mode != row["mode"]:
                raise ValueError("rendered PNG geometry changed")
        target = next(item for item in targets if item["source_page"] == row["source_page"])
        if row["dimensions"] != target["target_pixels"] or row["mode"] != "RGB":
            raise ValueError("rendered PNG differs from canonical target")
    expected_render_order = [(view, row["source_page"]) for view in views for row in targets]
    if [(row.get("view_id"), row.get("source_page")) for row in rendered] != expected_render_order:
        raise ValueError("rendered PNG evidence order mismatch")
    counts = manifest.get("counts", {})
    if counts != {
        "rendered_pages": expected_pages * len(views),
        "triptychs": expected_pages,
        "contact_sheets": (expected_pages + 3) // 4,
        "merge_packets": expected_pages,
        "optional_companions": expected_pages * max(0, len(views) - 3),
    }:
        raise ValueError("visual bundle counts mismatch")


def build_contact_sheets(triptychs: list[Path], destination: Path) -> list[Path]:
    Image, ImageDraw, ImageFont = _image_lib()
    destination.mkdir(parents=True, exist_ok=True)
    font = ImageFont.load_default()
    outputs = []
    for start in range(0, len(triptychs), 4):
        images = [Image.open(path).convert("RGB") for path in triptychs[start:start + 4]]
        try:
            width, height = images[0].size
            canvas = Image.new("RGB", (width * 2, height * 2), "white")
            for offset, image in enumerate(images):
                canvas.paste(image, ((offset % 2) * width, (offset // 2) * height))
            output = destination / f"pages-{start + 1:03d}-{start + len(images):03d}.png"
            canvas.save(output)
            outputs.append(output)
        finally:
            for image in images:
                image.close()
    return outputs


def _page_view(view: dict[str, Any], page: int) -> dict[str, Any]:
    blocks = [block for block in view.get("blocks", []) if block.get("source_page") == page]
    assets = [asset for block in blocks for asset in block.get("assets", [])]
    return {"blocks": blocks, "type_counts": dict(sorted(Counter(block.get("type", "unknown") for block in blocks).items())),
            "text_length": sum(len(block.get("text", "")) for block in blocks), "asset_references": assets}


def _match_source_page(
    pair_name: str,
    row: dict[str, Any],
    all_views: dict[str, Any],
    *,
    source_page_indexes: dict[str, dict[Any, Any]] | None = None,
) -> int:
    try:
        left_view, right_view = pair_name.split("__vs__", 1)
        left_index, right_index = row["left_raw_index"], row["right_raw_index"]
    except (KeyError, ValueError) as exc:
        raise ValueError(f"malformed bbox match for {pair_name}") from exc
    indexes = {} if source_page_indexes is None else source_page_indexes
    for name in (left_view, right_view):
        if name not in indexes:
            indexes[name] = {
                block.get("raw_index"): block.get("source_page")
                for block in all_views[name].get("blocks", [])
            }
    left_page, right_page = indexes[left_view].get(left_index), indexes[right_view].get(right_index)
    if not isinstance(left_page, int) or left_page != right_page:
        raise ValueError(f"bbox match does not resolve to one source page for {pair_name}")
    return left_page


def _packet_pairwise(pairwise: dict[str, Any], all_views: dict[str, Any], page: int) -> dict[str, Any]:
    result = {}
    # Reuse indexes only within this projection; the next call reads fresh input.
    source_page_indexes: dict[str, dict[Any, Any]] = {}
    for key, diff in pairwise.items():
        result[key] = {
            "bbox_matches": [row for row in diff.get("bbox_matches", []) if _match_source_page(key, row, all_views, source_page_indexes=source_page_indexes) == page],
            "left_unmatched": [row for row in diff.get("left_unmatched", []) if row.get("source_page") == page],
            "right_unmatched": [row for row in diff.get("right_unmatched", []) if row.get("source_page") == page],
        }
    return result


def review_signals(views: dict[str, dict[str, Any]], baseline: tuple[str, ...] = VIEWS) -> dict[str, Any]:
    texts = ["\n".join(block.get("text", "") for block in views[name]["blocks"]) for name in baseline]
    lengths = [views[name]["text_length"] for name in baseline]
    counts = [views[name]["type_counts"] for name in baseline]
    assets = [len(views[name]["asset_references"]) for name in baseline]
    text_similarity = min(SequenceMatcher(a=texts[0], b=texts[index]).ratio() for index in (1, 2))
    length_divergence = (max(lengths) - min(lengths)) / max(max(lengths), 1)
    type_divergence = max(0 if counts[0] == count else 1 for count in counts[1:])
    asset_divergence = max(assets) - min(assets)
    missing_boxes = sum(1 for name in baseline for block in views[name]["blocks"] if block.get("bbox") is None)
    visual_first = all(length == 0 for length in lengths)
    priority = round((1 - text_similarity) * 4 + length_divergence * 3 + type_divergence * 2 + min(asset_divergence, 3) + min(missing_boxes, 3) + (2 if visual_first else 0), 4)
    return {"normalized_text_similarity": round(text_similarity, 4), "text_length_divergence": round(length_divergence, 4),
            "block_type_divergence": type_divergence, "asset_count_divergence": asset_divergence,
            "missing_overlay_box_candidates": missing_boxes, "visual_first": visual_first, "priority_score": priority}


def build_packets(comparison: dict[str, Any], destination: Path, expected_pages: int, roles: tuple[tuple[int, int, str], ...] = ROLES, views_order: tuple[str, ...] = VIEWS, baseline: tuple[str, ...] = VIEWS) -> tuple[list[dict[str, Any]], list[Path]]:
    pages_dir = destination / "pages"
    pages_dir.mkdir(parents=True, exist_ok=True)
    index, files = [], []
    for page in range(1, expected_pages + 1):
        views = {name: _page_view(comparison["views"][name], page) for name in views_order}
        packet = {"schema": "kb_creator.mineru_merge_packet.v1", "source_page": page, "semantic_role": role_for_page(page, roles),
                  "views": views, "pairwise": _packet_pairwise(comparison.get("pairwise", {}), comparison["views"], page), "review_signals": review_signals(views, baseline)}
        json_path, md_path = pages_dir / f"page-{page:03d}.json", pages_dir / f"page-{page:03d}.md"
        json_path.write_text(json.dumps(packet, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        md_path.write_text(f"# Merge packet page {page:03d}\n\nRole: `{packet['semantic_role']}`\n\nPriority score: `{packet['review_signals']['priority_score']}`\n\nThis packet preserves alternatives; it does not select final text.\n", encoding="utf-8")
        index.append({"source_page": page, "semantic_role": packet["semantic_role"], "priority_score": packet["review_signals"]["priority_score"], "packet": f"pages/{json_path.name}"})
        files.extend([json_path, md_path])
    index_path = destination / "merge_index.json"
    index_path.write_text(json.dumps({"by_source_page": index, "by_priority": sorted(index, key=lambda row: (-row["priority_score"], row["source_page"]))}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    markdown = ["# MinerU merge index", "", "## By source page", "", "| Page | Role | Priority |", "|---:|---|---:|"]
    markdown += [f"| {row['source_page']} | {row['semantic_role']} | {row['priority_score']} |" for row in index]
    (destination / "merge_index.md").write_text("\n".join(markdown) + "\n", encoding="utf-8")
    return index, files + [index_path, destination / "merge_index.md"]


def inventory(root: Path, files: list[Path]) -> list[dict[str, Any]]:
    Image, _, _ = _image_lib()
    records = []
    for path in sorted(files):
        record = {"path": path.relative_to(root).as_posix(), "bytes": path.stat().st_size, "sha256": sha256_file(path)}
        if path.suffix.lower() == ".png":
            with Image.open(path) as image:
                record["dimensions"] = list(image.size)
        records.append(record)
    return records


def _contract_roles(path: Path) -> tuple[int, tuple[tuple[int, int, str], ...]]:
    try:
        data = validate_contract(json.loads(path.read_text(encoding="utf-8")))
    except (json.JSONDecodeError, OSError, ControlPlaneError) as error:
        raise ValueError("invalid reconstruction contract") from error
    source, scope, rows = data.get("source"), data.get("scope"), data.get("page_roles")
    if not isinstance(source, dict) or not isinstance(scope, dict) or not isinstance(rows, list) or scope.get("first_page") != 1 or scope.get("last_page") != source.get("page_count"):
        raise ValueError("invalid reconstruction contract topology")
    roles = tuple((row["first_page"], row["last_page"], row["role"]) for row in rows)
    if not roles or roles[0][0] != 1 or roles[-1][1] != source["page_count"] or any(roles[i][1] + 1 != roles[i + 1][0] for i in range(len(roles)-1)):
        raise ValueError("contract roles must be gap-free")
    return source["page_count"], roles

def build_bundle(*, raw_root: Path, output_root: Path, raw_receipt: Path, raw_receipt_sha256: str, source: Path, source_sha256: str, comparison: Path, comparison_sha256: str, pdftoppm: str, dpi: int = 110, expected_pages: int = 124, resume: bool = False, reconstruction_contract: Path | None = None, prepared_manifest: Path | None = None, prepared_manifest_sha256: str | None = None) -> dict[str, Any]:
    if reconstruction_contract is not None:
        expected_pages, roles = _contract_roles(reconstruction_contract)
    else:
        roles = ROLES
    identities, comparison_data = _load_inputs(raw_receipt, raw_receipt_sha256, source, source_sha256, comparison, comparison_sha256, raw_root, dpi, prepared_manifest, prepared_manifest_sha256)
    cpu_first = comparison_data.get("schema") in {"kb_creator.mineru_multi_view_comparison.v2", "kb_creator.mineru_multi_view_comparison.v3"}
    views_order = tuple(comparison_data["succeeded_views"]) if cpu_first else VIEWS
    baseline = CPU_TRIPTYCH if cpu_first else VIEWS
    if reconstruction_contract is not None:
        identities["reconstruction_contract"] = {
            "path": str(reconstruction_contract.resolve()),
            "sha256": sha256_file(reconstruction_contract),
        }
    if not cpu_first:
        existing = _check_resume(output_root, identities, resume)
        if existing is not None:
            return existing
    layouts = {view: find_layout_pdf(raw_root, view, cpu_first=cpu_first) for view in views_order}
    renderer = None
    plan = None
    if cpu_first:
        assert prepared_manifest is not None
        renderer, version_text = _renderer_identity(pdftoppm)
        prepared_data = json.loads(prepared_manifest.read_text(encoding="utf-8"))
        prepared_identity = _identity(prepared_manifest, path_hint="outputs/01-prepare-inputs/prepared/sample_pages.json")
        try:
            plan = build_geometry_plan(
                prepared_manifest=prepared_data,
                prepared_identity=prepared_identity,
                layouts=layouts,
                views=views_order,
                dpi=dpi,
                renderer=renderer,
                run_identity_sha256=comparison_data["run_identity_sha256"],
                source_identity=_identity(source, path_hint=source.name),
                comparison_identity=_identity(comparison, path_hint="outputs/03-compare-views/comparison.json"),
                view_set_identity={**_identity(raw_receipt, path_hint="outputs/02-mineru-three-view/view-set.json"), "receipt_sha256": json.loads(raw_receipt.read_text(encoding="utf-8"))["receipt_sha256"]},
            )
        except GeometryContractError as error:
            _write_geometry_failure(output_root, error=error, identities=identities, renderer=renderer, views=views_order, dpi=dpi)
            raise
    if cpu_first:
        existing = _check_resume(output_root, identities, resume, expected_plan=plan)
        if existing is not None:
            return existing
    output_root.parent.mkdir(parents=True, exist_ok=True)
    stage = Path(tempfile.mkdtemp(prefix=f".{output_root.name}.stage-", dir=output_root.parent))
    try:
        rendered, commands, version_text = render_layouts(layouts, stage / "visual", pdftoppm, dpi, expected_pages, views_order)
        if cpu_first:
            assert plan is not None
            plan = _attach_render_evidence(plan, rendered, stage)
        triptychs = build_triptychs(rendered, stage / "visual" / "triptychs", baseline)
        companions = build_optional_companions(rendered, stage / "visual" / "companions", views_order[3:]) if cpu_first else []
        contacts = build_contact_sheets(triptychs, stage / "visual" / "contact_sheets")
        _, packet_files = build_packets(comparison_data, stage / "merge_packets", expected_pages, roles, views_order, baseline)
        visual_files = [path for view in views_order for path in rendered[view]] + triptychs + companions + contacts
        plan_file = None
        if cpu_first:
            plan_file = stage / "visual" / "geometry_plan.json"
            plan_file.write_text(json.dumps(plan, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        exclusions = ["visual/visual_manifest.json", "evidence/execution.json", "command.json"] if cpu_first else ["visual/visual_manifest.json", "evidence/execution.json"]
        manifest = {"schema": "kb_creator.mineru_visual_merge_bundle.v2" if cpu_first else "kb_creator.mineru_visual_merge_bundle.v1", "inputs": identities,
                    "layouts": {view: {"path": str(path), "sha256": sha256_file(path)} for view, path in layouts.items()}, "execution": {"commands": commands, "pdftoppm_version": version_text}, "counts": {"rendered_pages": sum(len(rendered[view]) for view in views_order), "triptychs": len(triptychs), "contact_sheets": len(contacts), "merge_packets": expected_pages}, "inventory_scope": "all generated files except the two self-referential records listed in inventory_exclusions", "inventory_exclusions": ["visual/visual_manifest.json", "evidence/execution.json"],
                    "files": inventory(stage, visual_files + packet_files + ([plan_file] if plan_file else []))}
        manifest["inventory_exclusions"] = exclusions
        if cpu_first:
            manifest["inventory_scope"] = "all generated files except the three explicitly listed adapter/self-referential records"
        if cpu_first:
            manifest["counts"]["optional_companions"] = len(companions)
            manifest["geometry_plan"] = {"path": "visual/geometry_plan.json", **_identity(plan_file, path_hint="visual/geometry_plan.json"), "plan_sha256": plan["plan_sha256"]}
            # _identity uses path_hint; the public record uses the existing path spelling.
            manifest["geometry_plan"].pop("path_hint")
            manifest = _seal(manifest, "manifest_sha256")
        manifest_path = stage / "visual" / "visual_manifest.json"
        manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        evidence = stage / "evidence"
        evidence.mkdir()
        (evidence / "execution.json").write_text(json.dumps({"commands": commands, "pdftoppm_version": version_text, "output_inventory": manifest["files"]}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        if output_root.exists():
            output_root.rmdir()
        stage.replace(output_root)
        return manifest
    except GeometryContractError as error:
        shutil.rmtree(stage, ignore_errors=True)
        if output_root.exists() and not any(output_root.iterdir()):
            output_root.rmdir()
        assert renderer is not None
        if not error.matrix and plan is not None:
            error.matrix = plan["observed_geometry"]
        _write_geometry_failure(output_root, error=error, identities=identities, renderer=renderer, views=views_order, dpi=dpi)
        raise
    except Exception:
        shutil.rmtree(stage, ignore_errors=True)
        raise


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--raw-root", required=True, type=Path); parser.add_argument("--output-root", required=True, type=Path)
    parser.add_argument("--raw-receipt", required=True, type=Path); parser.add_argument("--raw-receipt-sha256", required=True)
    parser.add_argument("--source", required=True, type=Path); parser.add_argument("--source-sha256", required=True)
    parser.add_argument("--comparison", required=True, type=Path); parser.add_argument("--comparison-sha256", required=True)
    parser.add_argument("--prepared-manifest", type=Path); parser.add_argument("--prepared-manifest-sha256")
    parser.add_argument("--pdftoppm", required=True); parser.add_argument("--dpi", type=int, default=110); parser.add_argument("--expected-pages", type=int, default=124); parser.add_argument("--reconstruction-contract", type=Path); parser.add_argument("--resume", action="store_true")
    args = parser.parse_args()
    result = build_bundle(raw_root=args.raw_root.resolve(), output_root=args.output_root.resolve(), raw_receipt=args.raw_receipt.resolve(), raw_receipt_sha256=args.raw_receipt_sha256, source=args.source.resolve(), source_sha256=args.source_sha256, comparison=args.comparison.resolve(), comparison_sha256=args.comparison_sha256, pdftoppm=args.pdftoppm, dpi=args.dpi, expected_pages=args.expected_pages, resume=args.resume, reconstruction_contract=args.reconstruction_contract.resolve() if args.reconstruction_contract else None, prepared_manifest=args.prepared_manifest.resolve() if args.prepared_manifest else None, prepared_manifest_sha256=args.prepared_manifest_sha256)
    print(json.dumps({"status": "ok", "counts": result["counts"]}, ensure_ascii=False)); return 0


if __name__ == "__main__":
    raise SystemExit(main())
