"""Scaffold incomplete reviewed decision drafts from Stage04 packet files.

This tool preserves canonical-view evidence for human review. It does not
create semantic units, allowlists, decision sets, seals, or acceptance facts.
Schema checks validate only packet shape and identity fields; they do not prove
that the input is sealed, closed, replay-authorized, or accepted.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
from pathlib import Path, PurePosixPath
from typing import Any


DECISION_SCHEMA = "kb_creator.mineru_ai_page_decision.v1"
PACKET_SCHEMA = "kb_creator.mineru_merge_packet.v1"
CANONICAL_VIEWS = {
    "original_pipeline_txt",
    "original_pipeline_ocr",
    "raster_pipeline_ocr",
}
_PAGE_NAME = re.compile(r"page-(\d{3,})\.json$")
_SAFE_NAME = re.compile(r"[^A-Za-z0-9._-]+")


def _sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest().upper()


def _write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + "\n", encoding="utf-8")


def _safe_asset_path(value: Any) -> str:
    if not isinstance(value, str) or not value or "\\" in value:
        raise ValueError("asset path must be a nonempty relative POSIX path")
    path = PurePosixPath(value)
    if path.is_absolute() or any(part in {"", ".", ".."} for part in path.parts) or re.match(r"^[A-Za-z]:", value):
        raise ValueError("asset path escapes its canonical packet")
    return value


def _logical_asset_name(page: int, raw_index: int, source_path: str) -> str:
    suffix = Path(PurePosixPath(source_path).name).suffix
    stem = PurePosixPath(source_path).stem
    stem = _SAFE_NAME.sub("-", stem).strip(".-") or "asset"
    digest = hashlib.sha256(source_path.encode("utf-8")).hexdigest()[:12]
    return f"p{page:03d}-r{raw_index:05d}-{stem}-{digest}{suffix}"


def _heading_text(text: str, evidence: Any) -> str:
    level = evidence.get("text_level") if isinstance(evidence, dict) else None
    return f"{'#' * level} {text}" if type(level) is int and 1 <= level <= 6 else text


def _load_packets(packets_dir: Path, canonical_view: str) -> list[tuple[int, Path, bytes, dict[str, Any]]]:
    if canonical_view not in CANONICAL_VIEWS:
        raise ValueError("canonical view is unsupported")
    if not packets_dir.is_dir():
        raise ValueError("packets directory is missing")
    rows: list[tuple[int, Path, bytes, dict[str, Any]]] = []
    seen_pages: set[int] = set()
    for path in sorted(packets_dir.iterdir()):
        if not path.is_file() or path.suffix != ".json":
            continue
        match = _PAGE_NAME.fullmatch(path.name)
        if match is None:
            raise ValueError("packets directory contains a non-page JSON file")
        page = int(match.group(1))
        if page in seen_pages:
            raise ValueError("duplicate source page packet")
        raw = path.read_bytes()
        try:
            packet = json.loads(raw)
        except json.JSONDecodeError as error:
            raise ValueError(f"invalid packet JSON: {path.name}") from error
        if (
            not isinstance(packet, dict)
            or packet.get("schema") != PACKET_SCHEMA
            or packet.get("source_page") != page
            or not isinstance(packet.get("semantic_role"), str)
        ):
            raise ValueError(f"packet identity is invalid: {path.name}")
        views = packet.get("views")
        if not isinstance(views, dict) or canonical_view not in views or not isinstance(views[canonical_view], dict):
            raise ValueError(f"packet lacks canonical view: {path.name}")
        if not isinstance(views[canonical_view].get("blocks"), list):
            raise ValueError(f"canonical view blocks are invalid: {path.name}")
        rows.append((page, path, raw, packet)); seen_pages.add(page)
    if not rows:
        raise ValueError("packets directory has no page packets")
    pages = [page for page, _, _, _ in rows]
    if pages != list(range(1, len(pages) + 1)):
        raise ValueError("source page packet sequence is missing or noncontiguous")
    return rows


def _draft_for_packet(
    page: int, packet: dict[str, Any], canonical_view: str,
) -> tuple[dict[str, Any], dict[str, Any]]:
    blocks = packet["views"][canonical_view]["blocks"]
    selected_blocks: list[dict[str, Any]] = []
    assets: list[dict[str, Any]] = []
    markdown_parts: list[str] = []
    unresolved = ["manual review required: scaffold has no semantic, visual, or acceptance determination"]
    inventory_blocks: list[dict[str, Any]] = []
    raw_indexes: set[int] = set()
    logical_names: set[str] = set()
    for position, block in enumerate(blocks):
        if (
            not isinstance(block, dict)
            or type(block.get("raw_index")) is not int
            or block["raw_index"] < 0
            or block["raw_index"] in raw_indexes
        ):
            raise ValueError(f"page {page}: canonical block identity is invalid")
        raw_index = block["raw_index"]; raw_indexes.add(raw_index)
        if "source_page" in block and block["source_page"] != page:
            raise ValueError(f"page {page}: canonical block source page mismatches packet")
        block_type = block.get("type")
        if not isinstance(block_type, str) or not block_type:
            raise ValueError(f"page {page}: canonical block type is invalid")
        text = block.get("text")
        if text is not None and not isinstance(text, str):
            raise ValueError(f"page {page}: canonical block text is invalid")
        text = text or ""
        source_assets = block.get("assets", [])
        if not isinstance(source_assets, list):
            raise ValueError(f"page {page}: canonical block assets are invalid")
        safe_paths = [_safe_asset_path(value) for value in source_assets]
        if len(set(safe_paths)) != len(safe_paths):
            raise ValueError(f"page {page}: canonical block repeats an asset path")
        emitted_assets: list[str] = []
        selected = bool(text or safe_paths)
        if selected:
            purpose = "text" if text else "asset"
            selected_blocks.append({"view": canonical_view, "raw_index": raw_index, "purpose": purpose})
        if text:
            markdown_parts.append(_heading_text(text, block.get("semantic_evidence")))
        for source_path in safe_paths:
            logical_name = _logical_asset_name(page, raw_index, source_path)
            if logical_name in logical_names:
                raise ValueError(f"page {page}: generated asset logical name collides")
            logical_names.add(logical_name); emitted_assets.append(logical_name)
            placement = "reference_only" if text else "inline"
            assets.append({
                "view": canonical_view,
                "source_path": source_path,
                "logical_name": logical_name,
                "placement": placement,
            })
            if placement == "inline":
                markdown_parts.append(f"![review-draft asset page {page} raw {raw_index}]({{{{asset:{logical_name}}}}})")
        issues: list[str] = []
        if block_type not in {"text", "image", "table", "title", "header", "footer", "page_number"}:
            issues.append(f"unknown canonical block type {block_type!r}")
        if not text and not safe_paths:
            issues.append("empty canonical block")
        if issues:
            unresolved.extend(f"manual review required: raw {raw_index}: {issue}" for issue in issues)
        inventory_blocks.append({
            "position": position,
            "raw_index": raw_index,
            "type": block_type,
            "has_text": bool(text),
            "text_sha256": _sha256_bytes(text.encode("utf-8")) if text else None,
            "text_characters": len(text),
            "source_assets": safe_paths,
            "selected": selected,
            "emitted_assets": emitted_assets,
            "unresolved": issues,
        })
    decision = {
        "schema": DECISION_SCHEMA,
        "source_page": page,
        "semantic_role": packet["semantic_role"],
        "overlay_preference": canonical_view,
        "selected_blocks": selected_blocks,
        "markdown": "\n\n".join(markdown_parts),
        "assets": assets,
        "unresolved": unresolved,
        "review": {"visual_reviewed": False, "notes": "review-draft scaffold; manual review required"},
    }
    return decision, {"block_count": len(blocks), "blocks": inventory_blocks}


def prepare_review_drafts(packets_dir: Path, canonical_view: str, output_dir: Path) -> dict[str, Any]:
    """Create a deterministic, incomplete human-review draft set from packets."""
    packets_dir = packets_dir.resolve()
    output_dir = output_dir.resolve()
    if output_dir.exists():
        raise FileExistsError("output directory already exists")
    rows = _load_packets(packets_dir, canonical_view)
    stage = output_dir.parent / f".{output_dir.name}.review-draft-staging"
    if stage.exists():
        raise FileExistsError("owned review-draft staging directory already exists")
    try:
        pages_dir = stage / "pages"
        report_pages = []
        for page, packet_path, packet_bytes, packet in rows:
            decision, inventory = _draft_for_packet(page, packet, canonical_view)
            _write_json(pages_dir / f"page-{page:03d}.json", decision)
            report_pages.append({
                "source_page": page,
                "semantic_role": packet["semantic_role"],
                "source_packet": {
                    "path": packet_path.name,
                    "sha256": _sha256_bytes(packet_bytes),
                    "bytes": len(packet_bytes),
                },
                "canonical_view": canonical_view,
                **inventory,
            })
        report = {
            "schema": "kb_creator.mineru_review_draft_scaffold.v1",
            "state": "drafts_require_manual_review",
            "authority_state": "unverified_evidence_only",
            "authority_note": "packet schema and byte identity do not prove sealed, closed, replay-authorized, or accepted authority",
            "canonical_view": canonical_view,
            "page_count": len(report_pages),
            "pages": report_pages,
        }
        _write_json(stage / "scaffold_inventory.json", report)
        stage.replace(output_dir)
        return report
    finally:
        if stage.exists():
            shutil.rmtree(stage)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--packets", type=Path, required=True)
    parser.add_argument("--canonical-view", choices=sorted(CANONICAL_VIEWS), required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(argv)
    report = prepare_review_drafts(args.packets, args.canonical_view, args.output)
    print(json.dumps({"state": report["state"], "page_count": report["page_count"], "output": str(args.output)}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
