"""Normalize and compare three MinerU views without treating differences as errors."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from collections import Counter, defaultdict
from html.parser import HTMLParser
from itertools import combinations
from pathlib import Path
from pathlib import PureWindowsPath
from typing import Any


VIEWS = ("original_hybrid", "original_pipeline_ocr", "raster_hybrid")
CPU_REQUIRED_VIEWS = ("original_pipeline_txt", "original_pipeline_ocr", "raster_pipeline_ocr")
CPU_FIRST_VIEW_ORDER = CPU_REQUIRED_VIEWS + ("original_hybrid_high", "original_vlm")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def find_single(root: Path, suffix: str, *, required: bool) -> Path | None:
    matches = sorted(root.rglob(f"*{suffix}"))
    if not matches:
        if required:
            raise FileNotFoundError(f"{root}: missing {suffix}")
        return None
    if len(matches) != 1:
        raise ValueError(f"{root}: expected one {suffix}, found {len(matches)}")
    return matches[0]


def _text(row: dict[str, Any]) -> str:
    for key in ("text", "content"):
        value = row.get(key)
        if isinstance(value, str):
            return value
    return ""


def _bbox(row: dict[str, Any]) -> list[float] | None:
    value = row.get("bbox")
    if not isinstance(value, list) or len(value) != 4 or any(isinstance(item, bool) or not isinstance(item, (int, float)) for item in value):
        return None
    return [float(item) for item in value]


def _assets(row: dict[str, Any]) -> list[str]:
    values: list[str] = []
    for key in ("img_path", "image_path", "asset_path"):
        value = row.get(key)
        if isinstance(value, str):
            values.append(value)
    return values


def inventory_assets(content_root: Path, references: list[str]) -> list[dict[str, Any]]:
    resolved_root = content_root.resolve()
    inventory = []
    for reference in sorted(set(references)):
        windows_path = PureWindowsPath(reference)
        if (not reference or windows_path.is_absolute() or windows_path.drive or ".." in windows_path.parts):
            raise ValueError(f"unsafe MinerU asset reference: {reference!r}")
        candidate = (resolved_root.joinpath(*windows_path.parts)).resolve()
        try:
            candidate.relative_to(resolved_root)
        except ValueError as exc:
            raise ValueError(f"MinerU asset escapes content root: {reference!r}") from exc
        if not candidate.is_file():
            raise FileNotFoundError(f"referenced MinerU asset is missing: {reference}")
        inventory.append({"reference": reference, "bytes": candidate.stat().st_size, "sha256": sha256_file(candidate)})
    return inventory


def _flatten_text(value: Any) -> str:
    if isinstance(value, str):
        return value
    if isinstance(value, list):
        return " ".join(part for part in (_flatten_text(item) for item in value) if part)
    if isinstance(value, dict):
        return " ".join(
            part for part in (_flatten_text(item) for key, item in value.items() if key not in {"type", "sub_type", "bbox", "level", "index", "score", "angle"}) if part
        )
    return ""


def _title_evidence(value: Any) -> list[tuple[str, list[float] | None]]:
    """Return title records from MinerU v2/middle structures without guessing text."""
    found: list[tuple[str, list[float] | None]] = []
    if isinstance(value, dict):
        if value.get("type") == "title":
            content = value.get("content")
            text = ""
            if isinstance(content, dict):
                text = _flatten_text(content.get("title_content"))
            if not text:
                text = _flatten_text(value.get("lines"))
            if text.strip():
                found.append((text.strip(), _bbox(value)))
        for child in value.values():
            found.extend(_title_evidence(child))
    elif isinstance(value, list):
        for child in value:
            found.extend(_title_evidence(child))
    return found


def _is_unambiguous_title(text: str, bbox: list[float] | None, titles: list[tuple[str, list[float] | None]]) -> bool:
    candidates = {(candidate_text, tuple(candidate_bbox) if candidate_bbox is not None else None) for candidate_text, candidate_bbox in titles if candidate_text == text}
    # v1/v2 and middle may use different page coordinate spaces.  Exact text
    # appearing once on the same page is therefore the only portable alignment;
    # duplicated text remains deliberately unresolved.
    return len(candidates) == 1


class _TableCells(HTMLParser):
    def __init__(self) -> None:
        super().__init__(); self.cells: list[str] = []; self._parts: list[str] | None = None
    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag in {"td", "th"}: self._parts = []
    def handle_data(self, data: str) -> None:
        if self._parts is not None: self._parts.append(data)
    def handle_endtag(self, tag: str) -> None:
        if tag in {"td", "th"} and self._parts is not None:
            text = " ".join("".join(self._parts).split())
            if text: self.cells.append(text)
            self._parts = None


def _table_evidence(value: Any) -> list[tuple[list[float] | None, str]]:
    """Extract only explicit MinerU v2 table text; never infer a statblock."""
    found: list[tuple[list[float] | None, str]] = []
    if isinstance(value, dict):
        if value.get("type") == "table":
            content = value.get("content") if isinstance(value.get("content"), dict) else {}
            caption = _flatten_text(content.get("table_caption"))
            parser = _TableCells(); parser.feed(content.get("html", "") if isinstance(content.get("html", ""), str) else "")
            text = " ".join(part.strip() for part in [caption, *parser.cells] if part and part.strip())
            if text:
                found.append((_bbox(value), text))
        for child in value.values():
            found.extend(_table_evidence(child))
    elif isinstance(value, list):
        for child in value:
            found.extend(_table_evidence(child))
    return found


def _unique_table_text(bbox: list[float] | None, tables: list[tuple[list[float] | None, str]]) -> str | None:
    matches = [text for table_bbox, text in tables if _iou(bbox, table_bbox) == 1.0]
    return matches[0] if len(matches) == 1 else None


def normalize_content(rows: Any, source_pages: dict[int, int], *, v2: Any = None, middle: Any = None, markdown: str = "") -> list[dict[str, Any]]:
    if not isinstance(rows, list):
        raise ValueError("content list must be an array")
    v2_pages = v2 if isinstance(v2, list) else []
    middle_pages = middle.get("pdf_info", []) if isinstance(middle, dict) else []
    markdown_headings = Counter(match.group(2).strip() for match in re.finditer(r"^(#{1,6})\s+(.+?)\s*#*\s*$", markdown, re.MULTILINE))
    normalized = []
    for index, row in enumerate(rows):
        if not isinstance(row, dict) or not isinstance(row.get("page_idx"), int) or isinstance(row.get("page_idx"), bool):
            raise ValueError(f"content row {index} lacks an exact page_idx")
        page_idx = row["page_idx"]
        text = _text(row)
        v2_titles = _title_evidence(v2_pages[page_idx]) if 0 <= page_idx < len(v2_pages) else []
        v2_tables = _table_evidence(v2_pages[page_idx]) if 0 <= page_idx < len(v2_pages) else []
        middle_titles = _title_evidence(middle_pages[page_idx]) if 0 <= page_idx < len(middle_pages) else []
        table_text = _unique_table_text(_bbox(row), v2_tables) if row.get("type") == "table" else None
        normalized.append({
            "raw_index": index,
            "page_idx": page_idx,
            "source_page": source_pages.get(page_idx + 1),
            "type": row.get("type", "unknown") if isinstance(row.get("type", "unknown"), str) else "unknown",
            "bbox": _bbox(row),
            "text": table_text if table_text is not None else text,
            # Preserve, rather than collapse, the competing title signals.
            "semantic_evidence": {
                "text_level": row.get("text_level"),
                "v2_title": _is_unambiguous_title(text, _bbox(row), v2_titles),
                "middle_title": _is_unambiguous_title(text, _bbox(row), middle_titles),
                # Markdown has no reliable block coordinates.  Count only an exact,
                # document-unique heading as evidence; repeated text stays ambiguous.
                "markdown_heading": markdown_headings[text.strip()] == 1,
                "model_title": bool(row.get("is_title") or row.get("title_level")),
                **({"v2_table_text": True} if table_text is not None else {}),
            },
            "assets": _assets(row),
        })
    return normalized


def _iou(left: list[float] | None, right: list[float] | None) -> float | None:
    if left is None or right is None:
        return None
    x1, y1 = max(left[0], right[0]), max(left[1], right[1])
    x2, y2 = min(left[2], right[2]), min(left[3], right[3])
    overlap = max(0.0, x2 - x1) * max(0.0, y2 - y1)
    union = (left[2] - left[0]) * (left[3] - left[1]) + (right[2] - right[0]) * (right[3] - right[1]) - overlap
    return overlap / union if union > 0 else 0.0


def diff_blocks(left: list[dict[str, Any]], right: list[dict[str, Any]]) -> dict[str, Any]:
    unmatched_right = set(range(len(right)))
    matches = []
    for left_index, block in enumerate(left):
        candidates = []
        for right_index in unmatched_right:
            candidate = right[right_index]
            if block["source_page"] != candidate["source_page"] or block["type"] != candidate["type"]:
                continue
            score = _iou(block["bbox"], candidate["bbox"])
            if score is not None and score >= 0.5:
                candidates.append((score, right_index))
        if candidates:
            score, right_index = max(candidates)
            unmatched_right.remove(right_index)
            matches.append({"left_raw_index": block["raw_index"], "right_raw_index": right[right_index]["raw_index"], "bbox_iou": round(score, 4)})
    left_by_raw_index = {block["raw_index"]: block for block in left}
    right_by_raw_index = {block["raw_index"]: block for block in right}
    matched_left = {entry["left_raw_index"] for entry in matches}
    conflicts = []
    for match in matches:
        lhs, rhs = left_by_raw_index[match["left_raw_index"]], right_by_raw_index[match["right_raw_index"]]
        lhs_title = any(bool(value) for value in lhs["semantic_evidence"].values())
        rhs_title = any(bool(value) for value in rhs["semantic_evidence"].values())
        if lhs_title != rhs_title:
            conflicts.append({"kind": "title_to_text_downgrade", "left_raw_index": lhs["raw_index"], "right_raw_index": rhs["raw_index"], "bbox_iou": match["bbox_iou"], "resolution": None})
    for asset_side, asset_blocks, heading_side, heading_blocks in (
        ("left", left, "left", left),
        ("right", right, "right", right),
        ("left", left, "right", right),
        ("right", right, "left", left),
    ):
        for image in asset_blocks:
            if not image["assets"]:
                continue
            for title in heading_blocks:
                if (asset_blocks is heading_blocks and title is image) or image["source_page"] != title["source_page"] or not any(bool(value) for value in title["semantic_evidence"].values()):
                    continue
                score = _iou(image["bbox"], title["bbox"])
                if score is not None and score >= 0.8:
                    conflicts.append({"kind": "image_heading_overlap", "asset_side": asset_side, "heading_side": heading_side, "asset_raw_index": image["raw_index"], "heading_raw_index": title["raw_index"], "bbox_iou": round(score, 4), "resolution": None})
    return {
        "bbox_matches": matches,
        "left_unmatched": [block for block in left if block["raw_index"] not in matched_left],
        "right_unmatched": [right[index] for index in sorted(unmatched_right)],
        "semantic_conflicts": conflicts,
    }


def inspect_view(root: Path, source_pages: dict[int, int]) -> dict[str, Any]:
    v1 = find_single(root, "_content_list.json", required=True)
    v2 = find_single(root, "_content_list_v2.json", required=True)
    middle = find_single(root, "_middle.json", required=True)
    markdown = find_single(root, ".md", required=True)
    layout = find_single(root, "_layout.pdf", required=False)
    origin = find_single(root, "_origin.pdf", required=False)
    span = find_single(root, "_span.pdf", required=False)
    blocks = normalize_content(
        json.loads(v1.read_text(encoding="utf-8")), source_pages,
        v2=json.loads(v2.read_text(encoding="utf-8")),
        middle=json.loads(middle.read_text(encoding="utf-8")),
        markdown=markdown.read_text(encoding="utf-8"),
    )
    actual_indices = sorted({block["page_idx"] for block in blocks})
    expected_indices = list(range(len(source_pages)))
    asset_refs = [asset for block in blocks for asset in block["assets"]]
    return {
        "root": str(root),
        "artifacts": {
            "content_list": str(v1), "content_list_v2": str(v2), "middle_json": str(middle), "markdown": str(markdown),
            "layout_pdf": str(layout) if layout else None, "origin_pdf": str(origin) if origin else None,
            "span_pdf": str(span) if span else None,
        },
        "coverage": {"expected_page_idx": expected_indices, "actual_page_idx": actual_indices,
                     "missing_page_idx": sorted(set(expected_indices) - set(actual_indices)),
                     "extra_page_idx": sorted(set(actual_indices) - set(expected_indices))},
        "block_counts": dict(sorted(Counter(block["type"] for block in blocks).items())),
        "text_lengths": {str(page): sum(len(block["text"]) for block in blocks if block["page_idx"] == page) for page in expected_indices},
        "asset_references": asset_refs,
        "asset_inventory": inventory_assets(v1.parent, asset_refs),
        "blocks": blocks,
    }


def compare_views(manifest_path: Path, roots: dict[str, Path], output_dir: Path) -> dict[str, Any]:
    if output_dir.exists() and any(output_dir.iterdir()):
        raise FileExistsError(f"refusing non-empty comparison directory: {output_dir}")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    mapping = manifest.get("ordered_pages")
    if not isinstance(mapping, list) or not mapping:
        raise ValueError("manifest lacks ordered_pages")
    source_pages = {entry["sample_page"]: entry["source_page"] for entry in mapping if isinstance(entry, dict) and isinstance(entry.get("sample_page"), int) and isinstance(entry.get("source_page"), int)}
    if len(source_pages) != len(mapping) or sorted(source_pages) != list(range(1, len(mapping) + 1)):
        raise ValueError("manifest page mapping must be contiguous and exact")
    views = {name: inspect_view(roots[name], source_pages) for name in VIEWS}
    pairs = {}
    for left, right in (("original_hybrid", "original_pipeline_ocr"), ("original_hybrid", "raster_hybrid"), ("original_pipeline_ocr", "raster_hybrid")):
        pairs[f"{left}__vs__{right}"] = diff_blocks(views[left]["blocks"], views[right]["blocks"])
    failures = []
    for name, view in views.items():
        if view["coverage"]["missing_page_idx"] or view["coverage"]["extra_page_idx"]:
            failures.append(f"{name}: page coverage")
        if view["artifacts"]["layout_pdf"] is None:
            failures.append(f"{name}: missing layout PDF")
    result = {"schema": "kb_creator.mineru_three_view_comparison.v1", "status": "pass" if not failures else "fail", "failures": failures,
              "manifest": {"path": str(manifest_path), "sha256": sha256_file(manifest_path)}, "views": views, "pairwise": pairs}
    output_dir.mkdir(parents=True, exist_ok=False)
    (output_dir / "comparison.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    lines = ["# MinerU three-view comparison", "", f"Status: **{result['status'].upper()}**", "", "## View coverage", "", "| View | Missing page_idx | Extra page_idx | Layout PDF |", "|---|---|---|---|"]
    for name, view in views.items():
        coverage, artifacts = view["coverage"], view["artifacts"]
        lines.append(f"| {name} | {coverage['missing_page_idx']} | {coverage['extra_page_idx']} | {'yes' if artifacts['layout_pdf'] else 'no'} |")
    lines.extend(["", "## Pairwise block comparison", "", "| Pair | BBox matches | Left unmatched | Right unmatched |", "|---|---:|---:|---:|"])
    for name, diff in pairs.items():
        lines.append(f"| {name} | {len(diff['bbox_matches'])} | {len(diff['left_unmatched'])} | {len(diff['right_unmatched'])} |")
    if failures:
        lines.extend(["", "## Contract findings", "", *[f"- {failure}" for failure in failures]])
    (output_dir / "comparison.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    return result


def _canonical_sha(value: object) -> str:
    encoded = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest().upper()


def _sealed(value: dict[str, Any], key: str) -> None:
    expected = value.get(key)
    unsigned = {name: item for name, item in value.items() if name != key}
    if expected != _canonical_sha(unsigned):
        raise ValueError(f"{key} mismatch")


def _file_identity(path: Path) -> dict[str, Any]:
    return {"bytes": path.stat().st_size, "sha256": sha256_file(path)}


def compare_view_set(manifest_path: Path, view_set_path: Path, output_dir: Path) -> dict[str, Any]:
    if output_dir.exists() and any(output_dir.iterdir()):
        raise FileExistsError(f"refusing non-empty comparison directory: {output_dir}")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    mapping = manifest.get("ordered_pages")
    if not isinstance(mapping, list) or not mapping:
        raise ValueError("manifest lacks ordered_pages")
    source_pages = {
        entry["sample_page"]: entry["source_page"]
        for entry in mapping
        if isinstance(entry, dict)
        and isinstance(entry.get("sample_page"), int)
        and isinstance(entry.get("source_page"), int)
    }
    if len(source_pages) != len(mapping) or sorted(source_pages) != list(range(1, len(mapping) + 1)):
        raise ValueError("manifest page mapping must be contiguous and exact")
    view_set = json.loads(view_set_path.read_text(encoding="utf-8"))
    _sealed(view_set, "receipt_sha256")
    if (
        view_set.get("schema") != "kb_creator.mineru_view_set.v1"
        or view_set.get("required_succeeded") != list(CPU_REQUIRED_VIEWS)
        or [row.get("view_id") for row in view_set.get("views", [])] != list(CPU_FIRST_VIEW_ORDER)
    ):
        raise ValueError("view-set manifest is not the exact CPU-first view set")
    stage_root = view_set_path.parent.resolve()
    roots: dict[str, Path] = {}
    skipped = []
    succeeded = []
    for row in view_set["views"]:
        receipt_record = row.get("receipt")
        if not isinstance(receipt_record, dict):
            raise ValueError("view-set row lacks receipt identity")
        relative = receipt_record.get("path")
        if not isinstance(relative, str) or "\\" in relative or ":" in relative or ".." in Path(relative).parts:
            raise ValueError("unsafe view receipt path")
        receipt_path = (stage_root / relative).resolve()
        try:
            receipt_path.relative_to(stage_root)
        except ValueError as error:
            raise ValueError("view receipt escapes stage root") from error
        if not receipt_path.is_file() or {"path": relative, **_file_identity(receipt_path), "receipt_sha256": receipt_record.get("receipt_sha256")} != receipt_record:
            raise ValueError("view receipt identity mismatch")
        receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
        _sealed(receipt, "receipt_sha256")
        if receipt.get("view_id") != row["view_id"] or receipt.get("state") != row.get("state") or receipt.get("run_identity_sha256") != view_set.get("run_identity_sha256"):
            raise ValueError("view receipt is stale or misbound")
        if receipt["state"] == "skipped":
            if receipt.get("artifact_root") is not None or receipt.get("output_inventory") != [] or receipt.get("diagnostics") != {"invoked": False}:
                raise ValueError("skipped view contains output evidence")
            skipped.append({"view_id": row["view_id"], "reason_code": receipt.get("reason_code"), "receipt": receipt_record})
            continue
        artifact_hint = receipt.get("artifact_root")
        if artifact_hint != f"views/{row['view_id']}/artifacts":
            raise ValueError("succeeded view artifact root mismatch")
        root = (stage_root / artifact_hint).resolve()
        try:
            root.relative_to(stage_root)
        except ValueError as error:
            raise ValueError("view artifact root escapes stage root") from error
        observed = [
            {"path": path.relative_to(root).as_posix(), **_file_identity(path)}
            for path in sorted(root.rglob("*"))
            if path.is_file()
        ]
        if observed != receipt.get("output_inventory"):
            raise ValueError("view output inventory mismatch")
        roots[row["view_id"]] = root
        succeeded.append(row["view_id"])
    if succeeded != view_set.get("succeeded_views") or succeeded[:3] != list(CPU_REQUIRED_VIEWS):
        raise ValueError("view-set succeeded view order mismatch")
    views = {name: inspect_view(roots[name], source_pages) for name in succeeded}
    pairs = {
        f"{left}__vs__{right}": diff_blocks(views[left]["blocks"], views[right]["blocks"])
        for left, right in combinations(succeeded, 2)
    }
    failures = []
    for name, view in views.items():
        if view["coverage"]["missing_page_idx"] or view["coverage"]["extra_page_idx"]:
            failures.append(f"{name}: page coverage")
        if view["artifacts"]["layout_pdf"] is None:
            failures.append(f"{name}: missing layout PDF")
    result = {
        "schema": "kb_creator.mineru_multi_view_comparison.v2",
        "status": "pass_for_review" if not failures else "fail",
        "run_identity_sha256": view_set["run_identity_sha256"],
        "manifest": {"path": str(manifest_path), **_file_identity(manifest_path)},
        "view_set": {"path": str(view_set_path), **_file_identity(view_set_path), "receipt_sha256": view_set["receipt_sha256"]},
        "required_views": list(CPU_REQUIRED_VIEWS),
        "succeeded_views": succeeded,
        "skipped_views": skipped,
        "views": views,
        "pairwise": pairs,
        "failures": failures,
    }
    output_dir.mkdir(parents=True, exist_ok=False)
    (output_dir / "comparison.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (output_dir / "comparison.md").write_text(
        "# MinerU multi-view comparison\n\n"
        f"Status: **{result['status'].upper()}**\n\n"
        "This evidence is pass-for-review only; it is not GPU parity or reconstruction acceptance.\n",
        encoding="utf-8",
    )
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", required=True, type=Path)
    parser.add_argument("--view-set-manifest", type=Path)
    for view in VIEWS:
        parser.add_argument(f"--{view.replace('_', '-')}", type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    args = parser.parse_args()
    if args.view_set_manifest is not None:
        if any(getattr(args, view) is not None for view in VIEWS):
            parser.error("--view-set-manifest cannot be combined with legacy view roots")
        result = compare_view_set(args.manifest.resolve(), args.view_set_manifest.resolve(), args.output_dir.resolve())
        passed = result["status"] == "pass_for_review"
    else:
        roots = {view: getattr(args, view) for view in VIEWS}
        if any(path is None for path in roots.values()):
            parser.error("legacy mode requires all three legacy view roots")
        result = compare_views(args.manifest.resolve(), {name: path.resolve() for name, path in roots.items()}, args.output_dir.resolve())
        passed = result["status"] == "pass"
    print(json.dumps({"status": result["status"], "comparison": str(args.output_dir / "comparison.json"), "failures": result["failures"]}, ensure_ascii=False))
    return 0 if passed else 2


if __name__ == "__main__":
    raise SystemExit(main())
