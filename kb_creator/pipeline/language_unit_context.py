"""Deterministic source-only context for formal language units.

The index is intentionally derived from MASTER_EN every time it is consumed.
It is evidence, never translator input.
"""
from __future__ import annotations

import hashlib
import re
from typing import Any

from kb_creator.scripts import scenario_master_ru as legacy
from kb_creator.scripts.prepare_translation_batches import expand_units_for_translation


def _sha(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest().upper()


def _kind(text: str) -> str:
    lines = [line for line in text.splitlines() if line.strip()]
    if lines and all(line.lstrip().startswith("|") for line in lines):
        return "table"
    if len(lines) == 1 and lines[0].startswith("<!-- source-page-"):
        return "page_marker"
    if len(lines) == 1 and lines[0].lstrip().startswith("#"):
        return "heading"
    return "block"


_SOURCE_PAGE = re.compile(r"<!--\s*source-page-(?:-\d+-)?(?P<page>\d{3})\s*-->")


def _source_page(text: str) -> int | None:
    """Read the declared source page from both legacy and current markers."""
    match = _SOURCE_PAGE.fullmatch(text.strip())
    return int(match.group("page")) if match else None


def derive(master_text: str, max_batch_chars: int) -> list[dict[str, Any]]:
    """Return an ordered compact index aligned to public expanded units."""
    base = legacy._source_units(master_text)
    expanded = expand_units_for_translation(base, max_batch_chars)
    page = None
    blocks: list[dict[str, Any]] = []
    for index, row in enumerate(base):
        text = row["source_text"]
        marker_page = _source_page(text)
        if marker_page is not None:
            page = marker_page
        blocks.append({"index": index, "page": page, "text": text, "hash": _sha(text), "kind": _kind(text)})
    result: list[dict[str, Any]] = []
    cursor = 0
    offset = 0
    for row in expanded:
        source = row["source_text"]
        while cursor < len(blocks) and (start := blocks[cursor]["text"].find(source, offset)) < 0:
            cursor += 1
            offset = 0
        if cursor >= len(blocks):
            raise ValueError("expanded unit cannot be located in source blocks")
        block = blocks[cursor]
        previous = next((candidate for candidate in reversed(blocks[:cursor]) if candidate["page"] == block["page"] and candidate["kind"] != "page_marker"), None)
        result.append({
            "unit_id": row["unit_id"], "source_hash": row["source_hash"],
            "parent_block_index": block["index"], "parent_block_sha256": block["hash"],
            "source_start": start, "source_end": start + len(source), "page": block["page"],
            "parent_kind": block["kind"],
            "predecessor": None if previous is None else {
                "block_index": previous["index"], "sha256": previous["hash"], "kind": previous["kind"], "text": previous["text"],
            },
        })
        offset = start + len(source)
    if [row["unit_id"] for row in result] != [row["unit_id"] for row in expanded]:
        raise ValueError("context unit order mismatch")
    return result


def context_by_unit(master_text: str, max_batch_chars: int, expected: object) -> dict[str, dict[str, Any]]:
    actual = derive(master_text, max_batch_chars)
    if actual != expected:
        raise ValueError("source unit context is missing, stale, or tampered")
    return {row["unit_id"]: row for row in actual}
