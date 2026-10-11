"""Source-visible, page-scoped handout evidence for reconstruction contract v3."""
from __future__ import annotations

import re
from typing import Any, Mapping

CAPTION = re.compile(
    r"(?i)^(?:(?P<prefix>[a-z][a-z0-9 '\u2019-]*?)\s+)?handout\s+"
    r"(?:#\s*)?(?P<label>[A-Z]|[1-9]\d*)(?:\s*$|\s*(?:-|\u2013|\u2014|:)\s+\S.*)$"
)
HEADING = re.compile(r"^\s{0,3}#{1,6}\s+")


def visible_caption(value: str) -> tuple[str | None, str] | None:
    """Parse a complete caption; never interpret an inline reference or filename."""
    value = value.strip()
    while value.startswith(">"):
        value = value[1:].strip()
    value = HEADING.sub("", value).strip()
    emphasis = re.fullmatch(r"(\*\*|__|\*|_)(.+)\1", value)
    if emphasis:
        value = emphasis.group(2).strip()
    match = CAPTION.fullmatch(value)
    if match is None:
        return None
    prefix = (match.group("prefix") or "").strip()
    prefix = re.sub(r"(?i)(?:^|\s)(?:player|investigator(?:['\u2019]s)?)$", "", prefix).strip()
    scope = re.sub(r"[\s-]+", "-", prefix.casefold()) if prefix else None
    return scope, match.group("label").upper()


def declared_occurrences(contract: Mapping[str, Any]) -> set[tuple[str, str, int, str]]:
    return {(group["scope_id"], row["label"], occurrence["source_page"], occurrence["section"])
            for group in contract["scope"]["required_entities"]["handout_label_sets"]
            for row in group["labels"] for occurrence in row["occurrences"]}


def page_section(contract: Mapping[str, Any], page: int) -> str:
    roles = [row for row in contract["page_roles"] if row["first_page"] <= page <= row["last_page"]]
    if len(roles) != 1:
        raise ValueError(f"handout page role is ambiguous: page {page}")
    tokens = re.split(r"[\s_/-]+", roles[0]["role"].casefold())
    topology = set(tokens).intersection({"body", "appendix"})
    if len(topology) != 1:
        raise ValueError(f"handout page requires explicit body or appendix role: page {page}")
    return topology.pop()


def _caption_lines(page: int, decision: Mapping[str, Any]) -> dict[int, tuple[str | None, str]]:
    from .semantic_structure import apply_block_boundaries

    markdown = decision.get("markdown")
    if not isinstance(markdown, str):
        raise ValueError(f"handout decision has no Markdown: page {page}")
    lines = apply_block_boundaries(markdown, decision.get("block_boundaries")).splitlines()
    captions = {index: parsed for index, line in enumerate(lines, 1)
                if HEADING.match(line) and (parsed := visible_caption(line)) is not None}
    structure = decision.get("semantic_structure")
    if structure is None:
        return captions
    if not isinstance(structure, dict) or not isinstance(structure.get("units"), list):
        raise ValueError(f"handout structure is invalid: page {page}")
    semantic_lines: set[int] = set()
    for unit in structure["units"]:
        if not isinstance(unit, dict) or unit.get("kind") != "handout":
            continue
        span = unit.get("markdown_span")
        if (not isinstance(span, dict) or type(span.get("start_line")) is not int
                or type(span.get("end_line")) is not int
                or not 1 <= span["start_line"] <= span["end_line"] <= len(lines)):
            raise ValueError(f"handout span is invalid: page {page}")
        matches = {index: parsed for index in range(span["start_line"], span["end_line"] + 1)
                   if (parsed := visible_caption(lines[index - 1])) is not None}
        if len(matches) != 1:
            raise ValueError(f"handout unit requires one visible caption: page {page}, line {span['start_line']}")
        if semantic_lines.intersection(matches):
            raise ValueError(f"duplicate handout units share a caption: page {page}")
        semantic_lines.update(matches)
        # An ATX heading inside its semantic unit is the same observation.
        captions.update(matches)
    return captions


def observed_occurrences(contract: Mapping[str, Any], decisions: Mapping[int, Mapping[str, Any]]) -> set[tuple[str, str, int, str]]:
    """Consume already validated decisions; upstream seals and asset proofs remain required."""
    declared = declared_occurrences(contract)
    observed: set[tuple[str, str, int, str]] = set()
    for page, decision in decisions.items():
        captions = _caption_lines(page, decision)
        if not captions:
            continue
        section = page_section(contract, page)
        for line, (scoped, label) in captions.items():
            candidates = [row for row in declared if row[1:]==(label, page, section)
                          and (scoped is None or row[0] == scoped)]
            if len(candidates) != 1:
                raise ValueError(f"handout occurrence is ambiguous or foreign: page {page}, label {label}, line {line}")
            if candidates[0] in observed:
                raise ValueError(f"duplicate physical handout occurrence: page {page}, label {label}, line {line}")
            observed.add(candidates[0])
    return observed
