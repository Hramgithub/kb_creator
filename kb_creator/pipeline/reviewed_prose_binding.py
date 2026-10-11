"""Strict reader-paragraph evidence for reviewed ordinary-prose corrections.

This is intentionally separate from semantic presentation units.  It proves a
complete selected source paragraph against one complete, plain reader paragraph;
it does not classify the paragraph or authorize a correction on its own.
"""

from __future__ import annotations

from collections.abc import Mapping
from hashlib import sha256
import re
from typing import Any


class ReviewedProseBindingError(ValueError):
    """Raised when an ordinary-prose correction lacks a closed paragraph proof."""


_HASH = re.compile(r"^[0-9A-F]{64}$")
_BLOCK_PREFIX = re.compile(r" {0,3}(?:#{1,6}(?:[ \t]+|$)|>|[-+*][ \t]+|\d{1,9}[.)][ \t]+)")
_UNSUPPORTED_INLINE = re.compile(r"[`\[\]<>]|!\[")
_FENCE = re.compile(r"^ {0,3}(`{3,}|~{3,})")


def _digest(text: str) -> str:
    return sha256(text.encode("utf-8")).hexdigest().upper()


def _fail(page: int, message: str) -> None:
    raise ReviewedProseBindingError(f"page {page}: {message}")


def _single_plain_paragraph(text: Any, *, page: int, label: str) -> str:
    if not isinstance(text, str) or not text or "\n" in text or not text.strip():
        _fail(page, f"{label} must be one complete nonempty paragraph")
    if text != text.strip() or _BLOCK_PREFIX.match(text) or "|" in text or _UNSUPPORTED_INLINE.search(text):
        _fail(page, f"{label} is not supported plain prose")
    return text


def _source_paragraph(text: str, layout: str | None, *, page: int) -> str:
    if layout is None:
        return _single_plain_paragraph(text, page=page, label="selected source block")
    if layout != "soft_wrapped_paragraph_v1" or "\n" not in text:
        _fail(page, "source prose layout policy is invalid")
    lines = text.split("\n")
    if any(not line.strip() or line.startswith(("    ", "\t")) for line in lines):
        _fail(page, "wrapped source must contain one complete prose paragraph")
    for line in lines:
        _single_plain_paragraph(line.strip(), page=page, label="wrapped source line")
    # Validate shape only. Corrections must still replay against the original
    # bytes, including every newline; no implicit whitespace edit is authorized.
    return text


def _visible_prose_line(line: str, *, page: int, label: str) -> str:
    """Project one direct reader paragraph without accepting prose-in-code."""
    if not line or not line.strip() or line != line.strip() or _BLOCK_PREFIX.match(line) or "|" in line:
        _fail(page, f"{label} is not supported prose Markdown")
    if _UNSUPPORTED_INLINE.search(line):
        _fail(page, f"{label} is not supported prose Markdown")
    from kb_creator.pipeline.reviewed_correction_text import UnsupportedMarkdownError, _inline_visible_text
    try:
        visible = _inline_visible_text(line)
    except UnsupportedMarkdownError as exc:
        _fail(page, f"{label} has unsupported Markdown: {exc}")
    if not visible or visible != visible.strip():
        _fail(page, f"{label} has invalid visible text")
    return visible


def _span_lines(markdown: str, span: Mapping[str, Any], *, page: int) -> tuple[list[str], int, int]:
    if not isinstance(markdown, str) or not isinstance(span, Mapping) or set(span) != {"start_line", "end_line", "sha256"}:
        _fail(page, "prose binding has invalid markdown span")
    start, end, expected_hash = span.get("start_line"), span.get("end_line"), span.get("sha256")
    lines = markdown.splitlines()
    if type(start) is not int or type(end) is not int or not 1 <= start <= end <= len(lines) or not isinstance(expected_hash, str) or not _HASH.fullmatch(expected_hash):
        _fail(page, "prose binding has invalid markdown span")
    selected = lines[start - 1:end]
    if _digest("\n".join(selected)) != expected_hash:
        _fail(page, "prose binding markdown span hash is stale")
    if start > 1 and lines[start - 2].strip() or end < len(lines) and lines[end].strip():
        _fail(page, "prose binding span does not cover a whole paragraph")
    if len(selected) != 1:
        _fail(page, "prose binding span must contain exactly one plain paragraph line")
    return selected, start, end


def _corrected_source(text: str, corrections: list[tuple[str, str]], *, page: int) -> tuple[str, list[dict[str, int | str]]]:
    intervals: list[tuple[int, int, str, str]] = []
    for before, after in corrections:
        occurrences = [index for index in range(len(text)) if text.startswith(before, index)]
        if len(occurrences) != 1:
            _fail(page, "candidate correction no longer has one source occurrence")
        start = occurrences[0]
        intervals.append((start, start + len(before), before, after))
    intervals.sort()
    if any(right[0] < left[1] for left, right in zip(intervals, intervals[1:])):
        _fail(page, "candidate corrections overlap")
    chunks: list[str] = []
    cursor = 0
    proof_intervals: list[dict[str, int | str]] = []
    for start, end, before, after in intervals:
        chunks.extend((text[cursor:start], after))
        proof_intervals.append({"start": start, "end": end, "before_sha256": _digest(before), "after_sha256": _digest(after)})
        cursor = end
    chunks.append(text[cursor:])
    return "".join(chunks), proof_intervals


def _visible_page_paragraphs(markdown: str, *, page: int) -> list[tuple[str, int, int]]:
    """Return reader-visible paragraphs while retaining physical page context."""
    from kb_creator.pipeline.reviewed_correction_text import (
        UnsupportedMarkdownError,
        _HTML_TAG,
        _inline_visible_text,
        _project_block_line,
    )

    result: list[tuple[str, int, int]] = []
    current: list[str] = []
    current_start = 1
    fenced: str | None = None
    for number, line in enumerate([*markdown.splitlines(), ""], start=1):
        fence = _FENCE.match(line)
        if fenced is not None:
            if fence and fence.group(1)[0] == fenced[0] and len(fence.group(1)) >= len(fenced):
                fenced = None
            continue
        if fence:
            fenced = fence.group(1)
            continue
        if "<!--" in line or "-->" in line or _HTML_TAG.search(line):
            _fail(page, "HTML page context is outside the visible paragraph contract")
        if not line.strip():
            if current:
                result.append(("\n".join(current), current_start, number - 1))
                current = []
            continue
        if line.lstrip().startswith("!["):
            if current:
                result.append(("\n".join(current), current_start, number - 1))
                current = []
            continue
        if not current:
            current_start = number
        try:
            current.append(_inline_visible_text(_project_block_line(line)))
        except UnsupportedMarkdownError as exc:
            _fail(page, f"page context has unsupported Markdown: {exc}")
    if fenced is not None:
        _fail(page, "unclosed fenced code page context")
    return result


def _has_semantic_owner(key: tuple[str, int], semantic_units: Any) -> bool:
    if not isinstance(semantic_units, list):
        return False
    for unit in semantic_units:
        if not isinstance(unit, Mapping):
            continue
        sources = unit.get("source_blocks")
        if isinstance(sources, list) and any(
            isinstance(source, Mapping) and (source.get("view"), source.get("raw_index")) == key
            for source in sources
        ):
            return True
    return False


def verify_reviewed_prose_bindings(
    decision: Mapping[str, Any], packet_blocks: Mapping[tuple[str, int], Mapping[str, Any]],
    selected: set[tuple[str, int]], effective_markdown: str, page: int,
    *, semantic_units: list[Mapping[str, Any]] | None, correction_candidates: Mapping[tuple[str, int], list[tuple[str, str]]] | None = None,
) -> dict[tuple[str, int], dict[str, Any]]:
    """Return sealed proofs for explicit ordinary-prose bindings or raise.

    The existing candidate gate is deliberately called here, so callers cannot
    replace its six-field source authorization with a hand-built candidate map.
    """
    if not isinstance(decision, Mapping):
        _fail(page, "decision must be a mapping")
    rows = decision.get("reviewed_prose_bindings_v1", [])
    if rows is None:
        return {}
    if not isinstance(rows, list):
        _fail(page, "reviewed prose bindings must be a list")

    # Local import avoids an import-time cycle while preserving the established
    # candidate authority when this helper is later dispatched by that module.
    from kb_creator.pipeline.semantic_structure import reviewed_block_text_correction_candidates

    authoritative = reviewed_block_text_correction_candidates(decision, packet_blocks, selected, page)
    if correction_candidates is not None and correction_candidates != authoritative:
        _fail(page, "supplied correction candidates differ from existing candidate authority")

    expected = {"view", "raw_index", "original_text_sha256", "markdown_span"}
    proofs: dict[tuple[str, int], dict[str, Any]] = {}
    for row in rows:
        if not isinstance(row, Mapping) or set(row) not in (expected, expected | {"source_layout"}):
            _fail(page, "invalid reviewed prose binding")
        view, raw_index = row.get("view"), row.get("raw_index")
        key = (view, raw_index)
        if not isinstance(view, str) or type(raw_index) is not int or key in proofs or key not in selected:
            _fail(page, "reviewed prose binding is not uniquely selected")
        block = packet_blocks.get(key)
        source = block.get("text") if isinstance(block, Mapping) else None
        if not isinstance(row["original_text_sha256"], str) or not _HASH.fullmatch(row["original_text_sha256"]) or not isinstance(source, str) or _digest(source) != row["original_text_sha256"]:
            _fail(page, "reviewed prose binding source hash is stale")
        if "source_layout" in row and row["source_layout"] != "soft_wrapped_paragraph_v1":
            _fail(page, "source prose layout policy is invalid")
        source = _source_paragraph(source, row.get("source_layout"), page=page)
        corrections = authoritative.get(key)
        if not corrections:
            _fail(page, "reviewed prose binding has no existing authorized correction")
        if _has_semantic_owner(key, semantic_units):
            _fail(page, "reviewed prose binding overlaps semantic-unit ownership")
        corrected, intervals = _corrected_source(source, corrections, page=page)
        corrected = _single_plain_paragraph(corrected, page=page, label="corrected source paragraph")
        span_lines, start, end = _span_lines(effective_markdown, row["markdown_span"], page=page)
        visible_paragraphs = _visible_page_paragraphs(effective_markdown, page=page)
        selected_visible = [text for text, visible_start, visible_end in visible_paragraphs if (visible_start, visible_end) == (start, end)]
        if len(selected_visible) != 1:
            _fail(page, "reader span is not one visible paragraph in its full-page context")
        reader = _visible_prose_line(span_lines[0], page=page, label="reader paragraph")
        if selected_visible[0] != reader:
            _fail(page, "reader span has unsupported paragraph context")
        if reader != corrected:
            _fail(page, "reader paragraph differs from the complete corrected source paragraph")
        if sum(text == reader for text, _, _ in visible_paragraphs) != 1:
            _fail(page, "reader paragraph is not unique on the page")
        proofs[key] = {
            "source_key": {"view": view, "raw_index": raw_index},
            "source_text_sha256": _digest(source),
            "correction_intervals": intervals,
            "reader_span": {"start_line": start, "end_line": end, "sha256": row["markdown_span"]["sha256"]},
            "corrected_text_sha256": _digest(corrected),
            "visible_text_sha256": _digest(reader),
            **({"source_layout": row["source_layout"]} if "source_layout" in row else {}),
        }
    prose_keys = set(proofs)
    if prose_keys & set(authoritative) != prose_keys:
        _fail(page, "reviewed prose binding does not consume every listed prose correction")
    if any(key in prose_keys and _has_semantic_owner(key, semantic_units) for key in authoritative):
        _fail(page, "prose correction overlaps semantic-unit ownership")
    return proofs


def verify_reviewed_prose_roles(
    decision: Mapping[str, Any], packet_blocks: Mapping[tuple[str, int], Mapping[str, Any]],
    selected: set[tuple[str, int]], effective_markdown: str, page: int, *,
    semantic_units: list[Mapping[str, Any]] | None, visual_inventory: Mapping[str, Mapping[str, Any]],
) -> dict[tuple[str, int], dict[str, Any]]:
    """Verify the closed, source-reviewed ordinary-prose role ledger."""
    if "reviewed_prose_roles_v1" not in decision:
        return {}
    rows = decision["reviewed_prose_roles_v1"]
    if not isinstance(rows, list):
        _fail(page, "reviewed prose roles must be a list")
    # This verifier is public shared authority. Validate correction candidates
    # even when a role's reader text is unchanged, so a fabricated no-op cannot
    # be hidden beside an otherwise valid role outside the Stage05 caller.
    from kb_creator.pipeline.semantic_structure import reviewed_block_text_correction_candidates
    reviewed_block_text_correction_candidates(decision, packet_blocks, selected, page)
    expected = {"role", "view", "raw_index", "selection_purpose", "block_type", "source_bbox",
                "original_text_sha256", "title_evidence", "markdown_span", "visual", "rationale"}
    semantic_visual = decision.get("semantic_structure", {}).get("review", {}).get("visual") if isinstance(decision.get("semantic_structure"), Mapping) else None
    proofs: dict[tuple[str, int], dict[str, Any]] = {}
    title_keys = ("text_level", "v2_title", "middle_title", "markdown_heading", "model_title")
    selection_rows = decision.get("selected_blocks", [])
    for row in rows:
        if not isinstance(row, Mapping) or set(row) != expected:
            _fail(page, "invalid reviewed prose role")
        key = (row.get("view"), row.get("raw_index"))
        if row.get("role") != "ordinary_prose" or row.get("selection_purpose") != "text" or not isinstance(key[0], str) or type(key[1]) is not int or key in proofs:
            _fail(page, "reviewed prose role is invalid or duplicate")
        if sum(isinstance(item, Mapping) and (item.get("view"), item.get("raw_index")) == key and item.get("purpose") == "text" for item in selection_rows) != 1 or key not in selected:
            _fail(page, "reviewed prose role is not selected exactly once as text")
        block = packet_blocks.get(key); source = block.get("text") if isinstance(block, Mapping) else None
        evidence = block.get("semantic_evidence") if isinstance(block, Mapping) else None
        projected = {name: evidence.get(name) if isinstance(evidence, Mapping) else None for name in title_keys}
        if (not isinstance(block, Mapping) or block.get("type") != "text" or row.get("block_type") != "text"
                or not isinstance(source, str) or not source or row.get("source_bbox") != block.get("bbox")
                or row.get("original_text_sha256") != _digest(source) or row.get("title_evidence") != projected
                or not any(projected.values())):
            _fail(page, "reviewed prose role source identity or title evidence is stale")
        if _has_semantic_owner(key, semantic_units):
            _fail(page, "reviewed prose role overlaps semantic-unit ownership")
        if not isinstance(row.get("rationale"), str) or not row["rationale"].strip():
            _fail(page, "reviewed prose role rationale is empty")
        visual = row.get("visual")
        if not isinstance(visual, Mapping) or visual != semantic_visual or visual_inventory.get(visual.get("path")) != {"bytes": visual.get("bytes"), "sha256": visual.get("sha256")} or f"page-{page:03d}.png" not in str(visual.get("path")):
            _fail(page, "reviewed prose role visual identity is stale")
        span_lines, start, end = _span_lines(effective_markdown, row["markdown_span"], page=page)
        visible = _visible_page_paragraphs(effective_markdown, page=page)
        matching = [text for text, first, last in visible if (first, last) == (start, end)]
        reader = _visible_prose_line(span_lines[0], page=page, label="reader paragraph")
        if len(matching) != 1 or matching[0] != reader or sum(text == reader for text, _, _ in visible) != 1:
            _fail(page, "reviewed prose role reader paragraph is not one unique isolated paragraph")
        if reader != source:
            binding = verify_reviewed_prose_bindings(decision, packet_blocks, selected, effective_markdown, page, semantic_units=semantic_units).get(key)
            if binding is None or binding["reader_span"] != row["markdown_span"]:
                _fail(page, "reviewed prose role changed paragraph lacks matching correction binding")
        proofs[key] = {"role": "ordinary_prose", "source_key": {"view": key[0], "raw_index": key[1]},
                       "source_text_sha256": _digest(source), "reader_span": dict(row["markdown_span"]),
                       "visible_text_sha256": _digest(reader), "visual_sha256": visual["sha256"]}
    return proofs
