"""Move semantic unit selectors through sealed page edits without text search."""
from __future__ import annotations

from copy import deepcopy
from typing import Any, Iterable, Mapping

from .identity import sha256_bytes
from .source_choice_slice import SourceSlice, apply_sealed_slices


class SourceChoiceSelectorError(ValueError):
    """A successor selector cannot be derived from its predecessor unit."""


def rebind_prose_selectors(page_spec: Mapping[str, Any], r0_markdown: str,
                           authored_bindings: Iterable[Mapping[str, Any]], slices: Iterable[SourceSlice],
                           *, markdown_sha256: str) -> dict[str, Any]:
    """Move paragraph bindings using their sealed coordinates, including following prose."""
    output = deepcopy(dict(page_spec))
    selectors = output.get("reviewed_prose_bindings_v1", [])
    if not isinstance(selectors, list):
        raise SourceChoiceSelectorError("prose selectors are malformed")
    by_key = {}
    for row in authored_bindings:
        key = (row.get("view"), row.get("raw_index"))
        if not isinstance(key[0], str) or type(key[1]) is not int or key in by_key:
            raise SourceChoiceSelectorError("predecessor prose key is malformed or duplicated")
        by_key[key] = row
    definitions, units, seen = [], [], set()
    for i, selector in enumerate(selectors):
        key = (selector.get("view"), selector.get("raw_index"))
        if key in seen or key not in by_key:
            raise SourceChoiceSelectorError("prose selector has no unique predecessor")
        seen.add(key)
        old = by_key[key]
        if selector.get("source_layout") != old.get("source_layout"):
            raise SourceChoiceSelectorError("prose source layout differs from predecessor")
        span = selector.get("markdown_span", {})
        if not isinstance(span, Mapping) or set(span) != {"start_line", "end_line"}:
            raise SourceChoiceSelectorError("prose line selector is malformed")
        name = f"prose-{i}"
        definitions.append({"id": name, **span})
        units.append({"id": name, "markdown_span": old.get("markdown_span")})
    rebound = rebind_unit_selectors({"units": definitions}, r0_markdown, units, slices,
                                    markdown_sha256=markdown_sha256)
    for selector, unit in zip(selectors, rebound["units"]):
        selector["markdown_span"] = {k: unit[k] for k in ("start_line", "end_line")}
    return output


def rebind_prose_role_selectors(page_spec: Mapping[str, Any], r0_markdown: str,
                                authored_roles: Iterable[Mapping[str, Any]], slices: Iterable[SourceSlice], *, markdown_sha256: str) -> dict[str, Any]:
    """Rebind ordinary-prose role selectors by sealed predecessor coordinates."""
    output = deepcopy(dict(page_spec)); selectors = output.get("reviewed_prose_roles_v1", [])
    if not isinstance(selectors, list):
        raise SourceChoiceSelectorError("prose role selectors are malformed")
    old = {(row.get("view"), row.get("raw_index")): row for row in authored_roles}
    definitions = []; units = []; seen = set()
    for index, selector in enumerate(selectors):
        key = (selector.get("view"), selector.get("raw_index")); span = selector.get("markdown_span")
        if key in seen or key not in old or not isinstance(span, Mapping) or set(span) != {"start_line", "end_line"}:
            raise SourceChoiceSelectorError("prose role selector has no unique predecessor")
        seen.add(key); name = f"prose-role-{index}"
        definitions.append({"id": name, **span}); units.append({"id": name, "markdown_span": old[key].get("markdown_span")})
    rebound = rebind_unit_selectors({"units": definitions}, r0_markdown, units, slices, markdown_sha256=markdown_sha256)
    for selector, unit in zip(selectors, rebound["units"]):
        selector["markdown_span"] = {key: unit[key] for key in ("start_line", "end_line")}
    return output


def rebind_unit_selectors(
    page_spec: Mapping[str, Any], r0_markdown: str,
    authored_units: Iterable[Mapping[str, Any]], slices: Iterable[SourceSlice],
    *, markdown_sha256: str,
) -> dict[str, Any]:
    """Project verified R0 spec units through a complete set of page replacements.

    The caller owns reopening the sealed predecessor spec and decision. Unit
    identity, line-span hashes, page identity and replacement preimages are
    checked here. Textual selectors are replaced with exact line selectors;
    their old strings are never used to rediscover an occurrence.
    """
    edits = list(slices)
    successor = apply_sealed_slices(r0_markdown, edits, container_sha256=markdown_sha256)
    # A reviewed retention can cover several semantic units without changing
    # their boundaries. Validate its seal/overlap above, then project only edits.
    edits = [edit for edit in edits if r0_markdown[edit.start:edit.end] != edit.after]
    definitions = page_spec.get("units", [])
    if not isinstance(definitions, list):
        raise SourceChoiceSelectorError("semantic spec units are malformed")
    by_id: dict[str, Mapping[str, Any]] = {}
    for unit in authored_units:
        name = unit.get("id") if isinstance(unit, Mapping) else None
        if not isinstance(name, str) or not name or name in by_id:
            raise SourceChoiceSelectorError("predecessor unit identity is missing or duplicated")
        by_id[name] = unit
    lines = r0_markdown.split("\n")
    line_offsets = [0]
    for line in lines:
        line_offsets.append(line_offsets[-1] + len(line) + 1)
    output = deepcopy(dict(page_spec))
    seen: set[str] = set()
    for definition in output.get("units", []):
        name = definition.get("id") if isinstance(definition, dict) else None
        if not isinstance(name, str) or name in seen or name not in by_id:
            raise SourceChoiceSelectorError("spec unit has no unique predecessor unit")
        seen.add(name)
        span = by_id[name].get("markdown_span")
        if not isinstance(span, Mapping):
            raise SourceChoiceSelectorError("predecessor unit has no line span")
        first, last = span.get("start_line"), span.get("end_line")
        if (type(first) is not int or type(last) is not int
                or not 1 <= first <= last <= len(lines)):
            raise SourceChoiceSelectorError("predecessor unit line span is malformed")
        start, end = line_offsets[first - 1], line_offsets[last] - 1
        if sha256_bytes(r0_markdown[start:end].encode()) != span.get("sha256"):
            raise SourceChoiceSelectorError("predecessor unit line span identity drift")
        if ("start_line" in definition or "end_line" in definition) and (
                definition.get("start_line") != first or definition.get("end_line") != last):
            raise SourceChoiceSelectorError("spec line selector differs from predecessor unit")
        for edit in edits:
            if edit.start < start < edit.end or edit.start < end < edit.end:
                raise SourceChoiceSelectorError("replacement crosses a semantic unit boundary")
        new_start = start + sum(len(edit.after) - (edit.end - edit.start) for edit in edits if edit.end <= start)
        new_end = end + sum(len(edit.after) - (edit.end - edit.start) for edit in edits if edit.end <= end)
        if (new_start > 0 and successor[new_start - 1] != "\n") or (
                new_end < len(successor) and successor[new_end] != "\n"):
            raise SourceChoiceSelectorError("replacement merges a semantic unit with an adjacent line")
        definition.pop("start", None)
        definition.pop("end", None)
        definition["start_line"] = successor[:new_start].count("\n") + 1
        definition["end_line"] = successor[:new_end].count("\n") + 1
    return output
