"""Complete V2 title roles from selected source keys without text guessing.

The helper produces a successor spec.  It never changes an input spec, draft,
or packet and it keeps every generated role provisional by leaving review state
and unresolved transport untouched.
"""
from __future__ import annotations

import argparse
import copy
import json
import re
from collections import defaultdict
from pathlib import Path
from typing import Any

from kb_creator.pipeline.semantic_structure import TITLE_EVIDENCE_KEYS


_ATX = re.compile(r"^(#{1,6})[ \t]+(.*?)[ \t]*#*[ \t]*$")


def _title(block: dict[str, Any]) -> bool:
    evidence = block.get("semantic_evidence")
    return isinstance(evidence, dict) and any(evidence.get(name) for name in TITLE_EVIDENCE_KEYS)


def _line_text(line: str) -> str:
    match = _ATX.fullmatch(line)
    return match.group(2) if match else line


def _unique_context(lines: list[str], index: int) -> tuple[str, str]:
    """Return a smallest exact multiline selector for one physical line."""
    for radius in range(len(lines)):
        start, end = max(0, index - radius), min(len(lines), index + radius + 1)
        before = "\n".join(lines[start:end])
        if "\n".join(lines).count(before) == 1:
            relative = index - start
            patched = lines[start:end].copy()
            patched[relative] = "## " + patched[relative]
            return before, "\n".join(patched)
    raise ValueError("reader line has no unique page context")


def _selected_titles(decision: dict[str, Any], packet: dict[str, Any]) -> list[tuple[tuple[str, int], dict[str, Any]]]:
    blocks = {
        (view, block.get("raw_index")): block
        for view, value in packet.get("views", {}).items() if isinstance(value, dict)
        for block in value.get("blocks", []) if isinstance(block, dict)
    }
    result = []
    for row in decision.get("selected_blocks", []):
        if not isinstance(row, dict) or row.get("purpose") != "text":
            continue
        key = (row.get("view"), row.get("raw_index"))
        block = blocks.get(key)
        if isinstance(key[0], str) and type(key[1]) is int and isinstance(block, dict) and _title(block):
            result.append((key, block))
    return result


def _mapped_reader_lines(
    page: int, decision: dict[str, Any], packet: dict[str, Any], geometry: dict[str, Any] | None,
) -> dict[tuple[str, int], int]:
    """Use Stage05's monotonic source-key mapping when a raw title repeats.

    The audit mapping is source-key specific and already handles OCR text that
    differs from another selected view.  It is the only fallback for repeated
    reader lines; no fuzzy text comparison is introduced here.
    """
    if geometry is None:
        return {}
    from kb_creator.scripts.audit_mineru_ai_merge_fidelity import _normalized, _v3_page_context
    errors: list[str] = []
    context = _v3_page_context(page, packet, decision, geometry, errors)
    if errors:
        return {}
    line_ranges, cursor = [], 0
    for index, line in enumerate(decision["markdown"].split("\n")):
        width = len(_normalized(line))
        line_ranges.append((cursor, cursor + width, index))
        cursor += width
    result = {}
    for mapping in context["mappings"]:
        unit, span = mapping["unit"], mapping["markdown_span"]
        key = (unit["view_id"], unit["raw_index"])
        matches = [line for start, end, line in line_ranges if start <= span[0] and span[1] <= end]
        if len(matches) == 1:
            result[key] = matches[0]
    return result


def _running_header_keys(packets: dict[int, dict[str, Any]], decisions: dict[int, dict[str, Any]]) -> set[tuple[int, str, int]]:
    """Recognize only repeated titles in the same narrow top/bottom geometry band."""
    rows: dict[str, list[tuple[int, str, int, str]]] = defaultdict(list)
    for page, packet in packets.items():
        for (view, raw_index), block in _selected_titles(decisions[page], packet):
            text, bbox = block.get("text"), block.get("bbox")
            if not isinstance(text, str) or not isinstance(bbox, list) or len(bbox) != 4:
                continue
            if not all(isinstance(value, (int, float)) for value in bbox):
                continue
            band = "top" if bbox[1] <= 110 else "bottom" if bbox[1] >= 650 else "middle"
            rows[text].append((page, view, raw_index, band))
    return {
        (page, view, raw_index)
        for values in rows.values() if len({page for page, _, _, _ in values}) >= 3
        and len({band for _, _, _, band in values}) == 1
        and values[0][3] in {"top", "bottom"}
        for page, view, raw_index, _ in values
    }


def complete_title_spec(
    spec: dict[str, Any], drafts_root: Path, packets_root: Path, *, geometry: dict[str, Any] | None = None,
) -> tuple[dict[str, Any], dict[str, int]]:
    """Return an immutable-spec successor with complete selected V2 title roles."""
    if spec.get("semantic_structure_profile") != "reviewed_role_outline_and_partitions_v2":
        raise ValueError("title completion requires the V2 semantic profile")
    result = copy.deepcopy(spec)
    original_units = {
        (page.get("source_page"), unit.get("id")): copy.deepcopy(unit)
        for page in spec.get("pages", []) if isinstance(page, dict)
        for unit in page.get("units", []) if isinstance(unit, dict) and isinstance(unit.get("id"), str)
    }
    rows = {row.get("source_page"): row for row in result.get("pages", []) if isinstance(row, dict)}
    if not rows or len(rows) != len(result.get("pages", [])):
        raise ValueError("spec pages must have unique source_page values")
    decisions, packets = {}, {}
    for page in rows:
        decision_path = drafts_root / f"page-{page:03d}.json"
        packet_path = packets_root / f"page-{page:03d}.json"
        if not decision_path.is_file() or not packet_path.is_file():
            raise ValueError(f"page {page}: draft or packet is absent")
        decisions[page] = json.loads(decision_path.read_text(encoding="utf-8"))
        packets[page] = json.loads(packet_path.read_text(encoding="utf-8"))
    running_headers = _running_header_keys(packets, decisions)
    counts: dict[str, Any] = {"selected_title_count": 0, "preserved_unit_count": 0,
                              "generated_heading_count": 0, "generated_label_count": 0,
                              "unresolved_title_count": 0, "unresolved_titles": []}
    for page, row in sorted(rows.items()):
        decision, packet = decisions[page], packets[page]
        lines = decision.get("markdown", "").split("\n")
        if not isinstance(decision.get("markdown"), str):
            raise ValueError(f"page {page}: draft markdown is invalid")
        units = row.get("units")
        if not isinstance(units, list):
            raise ValueError(f"page {page}: spec units are invalid")
        existing = {
            (unit.get("view", decision.get("overlay_preference")), raw_index)
            for unit in units if isinstance(unit, dict)
            for raw_index in unit.get("raw_indices", [])
        }
        generated = 0
        patches = list(row.get("post_patches", []))
        mapped_lines = _mapped_reader_lines(page, decision, packet, geometry)
        for key, block in _selected_titles(decision, packet):
            counts["selected_title_count"] += 1
            if key in existing:
                counts["preserved_unit_count"] += 1
                continue
            text = block.get("text")
            if not isinstance(text, str) or not text:
                raise ValueError(f"page {page}: selected title has no source text")
            candidates = [index for index, line in enumerate(lines) if _line_text(line) == text]
            siblings = [other for other, sibling in _selected_titles(decision, packet) if sibling.get("text") == text]
            ordinal = siblings.index(key)
            if len(candidates) != len(siblings):
                # A selected alternate can disagree with the reader bytes at
                # the same geometry.  It needs an existing reviewed correction
                # or source-choice proof; making it a heading here would forge
                # that proof.  Leave it for the existing issue transport.
                line_index = mapped_lines.get(key)
                if line_index is None or _line_text(lines[line_index]) != text:
                    counts["unresolved_title_count"] += 1
                    counts["unresolved_titles"].append({
                        "source_page": page, "view": key[0], "raw_index": key[1],
                        "source_text": text, "reader_occurrence_count": len(candidates),
                        "same_source_text_selected_count": len(siblings),
                    })
                    continue
            else:
                line_index = candidates[ordinal]
            block_type = block.get("type")
            running = (page, key[0], key[1]) in running_headers
            kind, representation = ("label", "semantic_span") if block_type == "header" or running else ("heading", "atx_heading")
            if representation == "atx_heading" and _ATX.fullmatch(lines[line_index]) is None:
                before, after = _unique_context(lines, line_index)
                patches.append({"before": before, "after": after, "count": 1})
                lines[line_index] = "## " + lines[line_index]
            generated += 1
            unit_id = f"n81-p{page:03d}-title-{generated:03d}"
            units.append({
                "id": unit_id, "kind": kind, "representation": representation,
                "view": key[0], "raw_indices": [key[1]],
                "start_line": line_index + 1, "end_line": line_index + 1,
                "heading_level": 2 if kind == "heading" else None,
                "item_count": None, "container_parent": None,
                "semantic_parent": None, "continuation_of": None,
            })
            counts[f"generated_{kind}_count"] += 1
        units.sort(key=lambda unit: (unit.get("start_line", 0), unit["id"]))
        if patches:
            row["post_patches"] = patches
    preserved = {
        (page, unit.get("id")): unit
        for page, row in rows.items() for unit in row.get("units", [])
        if isinstance(unit, dict) and isinstance(unit.get("id"), str)
    }
    if any(preserved.get(key) != unit for key, unit in original_units.items()):
        raise ValueError("title completion changed an existing semantic unit")
    counts["existing_unit_count"] = len(original_units)
    counts["preserved_existing_unit_count"] = len(original_units)
    return result, counts


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--spec", required=True, type=Path)
    parser.add_argument("--draft-pages", required=True, type=Path)
    parser.add_argument("--packets", required=True, type=Path)
    parser.add_argument("--geometry", type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--report", required=True, type=Path)
    args = parser.parse_args()
    if args.output.exists() or args.report.exists():
        raise FileExistsError("title completion outputs must be absent")
    spec = json.loads(args.spec.read_text(encoding="utf-8"))
    geometry = json.loads(args.geometry.read_text(encoding="utf-8")) if args.geometry else None
    successor, counts = complete_title_spec(spec, args.draft_pages, args.packets, geometry=geometry)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(successor, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps({"schema": "kb_creator.selected_title_completion.v1", **counts}, indent=2) + "\n", encoding="utf-8", newline="\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
