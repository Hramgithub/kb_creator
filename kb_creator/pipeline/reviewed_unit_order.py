"""Order semantic declarations by exact reader spans without editing content."""
from __future__ import annotations

import copy
from typing import Any


def order_semantic_units(markdown: str, units: list[dict[str, Any]], *, page: int) -> list[dict[str, Any]]:
    """Keep all selectors/relations unchanged, stable-sort by verified start line.

    Equal starts preserve their declared parent/child order. Ambiguous or stale
    selectors raise through the existing author resolver; no fuzzy matching.
    """
    from kb_creator.scripts.author_reviewed_semantic_decisions import _definition_span

    if not isinstance(markdown, str) or not isinstance(units, list):
        raise ValueError("Markdown and semantic unit list are required")
    identifiers = [unit.get("id") for unit in units if isinstance(unit, dict)]
    if len(identifiers) != len(units) or any(not isinstance(value, str) or not value for value in identifiers) or len(set(identifiers)) != len(identifiers):
        raise ValueError("semantic units require unique IDs")
    lines = markdown.split("\n")
    positioned = [(_definition_span(lines, unit, page)[0], unit) for unit in units]
    return [copy.deepcopy(unit) for _, unit in sorted(positioned, key=lambda pair: pair[0])]


def expose_nested_table_units(markdown: str, page_spec: dict[str, Any], tables: list[dict[str, Any]]) -> dict[str, Any]:
    """Give already-present exact tables their own disjoint source selectors.

    ``tables`` contains source-bound view/raw_index/rows from verified metadata.
    This only changes declarations, never Markdown, source cells, or review flags.
    The table evidence verifier must subsequently check the source bindings.
    """
    from kb_creator.pipeline.reviewed_table_evidence import _markdown_rows
    from kb_creator.scripts.author_reviewed_semantic_decisions import _definition_span

    result = copy.deepcopy(page_spec)
    page = result["source_page"]
    lines = markdown.split("\n")
    for table in tables:
        view, raw, rows = table["view"], table["raw_index"], table["rows"]
        owners = [unit for unit in result["units"] if unit.get("view") == view and raw in unit.get("raw_indices", [])]
        if len(owners) != 1:
            raise ValueError("table must have one unambiguous source owner")
        parent = owners[0]
        if parent.get("representation") == "table":
            continue
        if parent.get("kind") != "statblock" or len(parent["raw_indices"]) < 2 or "source_fragments" in parent:
            raise ValueError("nested table requires a disjoint whole-block statblock owner")
        first, last = _definition_span(lines, parent, page)
        matches = []
        for start in range(first, last + 1):
            if not lines[start - 1].startswith("|") or start > first and lines[start - 2].startswith("|"):
                continue
            end = start
            while end < last and lines[end].startswith("|"):
                end += 1
            try:
                rendered = _markdown_rows(markdown, {"start_line": start, "end_line": end})
            except ValueError:
                continue
            if rendered == rows or rendered == [[""] * len(rows[0]), *rows]:
                matches.append((start, end))
        if len(matches) != 1:
            raise ValueError("source table has no unique exact Markdown match inside its owner")
        start, end = matches[0]
        parent["raw_indices"].remove(raw)
        result["units"].append({
            "id": f"{parent['id']}-table-{raw}", "kind": "statblock", "representation": "table",
            "view": view, "raw_indices": [raw], "start_line": start, "end_line": end,
            "container_parent": parent["id"], "semantic_parent": parent.get("semantic_parent"),
            "continuation_of": None, "heading_level": None, "item_count": None,
        })
    result["units"] = order_semantic_units(markdown, result["units"], page=page)
    return result
