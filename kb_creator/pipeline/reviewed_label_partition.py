"""Replay a complete selected block into its explicitly reviewed label spans."""
from __future__ import annotations

from typing import Any, Mapping

from .identity import sha256_bytes
from .semantic_structure import _fragment_text, apply_reviewed_text_corrections


def project_label_partition(
    decision: Mapping[str, Any], packet_blocks: Mapping, key: tuple[str, int],
    corrections: Mapping, page: int,
) -> tuple[str, dict[str, Any]] | None:
    """Only boundary whitespace is presentation; every label payload stays exact."""
    units = decision.get("semantic_structure", {}).get("units", [])
    owners = [unit for unit in units if {"view": key[0], "raw_index": key[1]} in unit.get("source_blocks", [])]
    if len(owners) < 2:
        return None
    source = packet_blocks[key]["text"]
    markdown = decision["markdown"]
    lines = markdown.split("\n")
    parts = []
    for unit in owners:
        if ((unit.get("kind"), unit.get("representation")) != ("label", "semantic_span")
                or unit.get("source_blocks") != [{"view": key[0], "raw_index": key[1]}]
                or not isinstance(unit.get("source_fragments"), list) or len(unit["source_fragments"]) != 1):
            raise ValueError("label partition has mixed source ownership or unsupported unit")
        fragment = unit["source_fragments"][0]
        if (fragment.get("view"), fragment.get("raw_index")) != key:
            raise ValueError("label partition fragment belongs to another source")
        raw = _fragment_text(packet_blocks[key], fragment, page)
        corrected = apply_reviewed_text_corrections(raw, key, [], corrections).strip(" \t\r\n")
        span = unit.get("markdown_span", {})
        line = span.get("start_line")
        if type(line) is not int or span.get("end_line") != line or not 1 <= line <= len(lines):
            raise ValueError("label partition requires a single sealed line per label")
        body = lines[line - 1]
        if not corrected or body != corrected or span.get("sha256") != sha256_bytes(body.encode()):
            raise ValueError("label partition reader differs from its corrected fragment")
        start = sum(len(value) + 1 for value in lines[:line - 1])
        parts.append((fragment["start"], fragment["end"], start, start + len(body), unit))
    parts.sort(key=lambda part: part[0])
    if (parts[0][0] != 0 or parts[-1][1] != len(source)
            or len({part[4].get("id") for part in parts}) != len(parts)):
        raise ValueError("label partition is incomplete or has duplicate owners")
    for left, right in zip(parts, parts[1:]):
        if left[1] != right[0] or left[3] >= right[2] or markdown[left[3]:right[2]] != "\n\n":
            raise ValueError("label partition has gaps, overlaps, reversed units or foreign reader content")
    start, end = parts[0][2], parts[-1][3]
    owner_ids = {part[4]["id"] for part in parts}
    for unit in units:
        if unit.get("id") in owner_ids:
            continue
        span = unit.get("markdown_span", {})
        first, last = span.get("start_line"), span.get("end_line")
        if type(first) is int and type(last) is int:
            other_start = sum(len(value) + 1 for value in lines[:first - 1])
            other_end = sum(len(value) + 1 for value in lines[:last]) - 1
            if other_start < end and other_end > start:
                raise ValueError("label partition envelope has another semantic owner")
    result = markdown[start:end]
    return result, {"policy": "reviewed_label_partition_v1", "source_sha256": sha256_bytes(source.encode()),
                    "reader_sha256": sha256_bytes(result.encode()),
                    "page_character_span": {"start": start, "end": end},
                    "units": [{"id": part[4]["id"], "fragment": part[4]["source_fragments"][0],
                               "markdown_span": part[4]["markdown_span"]} for part in parts]}
