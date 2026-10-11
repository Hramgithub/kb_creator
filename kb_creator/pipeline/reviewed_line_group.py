"""Canonicalize reviewed physical line groups without losing intentional refrains."""

from __future__ import annotations

from collections import Counter
from collections.abc import Mapping, Sequence
from typing import Any


def canonicalize_reviewed_line_group(
    markdown: str,
    expected_lines: Sequence[str],
    *,
    reviewed_span: Sequence[int] | Mapping[str, Any] | None = None,
) -> str:
    """Replace one reviewed line sequence with Markdown hard breaks.

    Matching ignores blank separator lines and trailing horizontal whitespace.
    A group is one contiguous sequence whose nonblank lines have exactly the
    declared multiset, so its reviewed Markdown order may differ from the
    source order. Without a span, that sequence must be unique and declared
    members must occur no more often than declared. A one-based, inclusive
    ``reviewed_span`` (``[start_line, end_line]`` or a mapping with exactly
    ``start_line`` and ``end_line``) may select one exact group.
    """
    if not isinstance(markdown, str):
        raise ValueError("reviewed line-group markdown must be text")
    expected = _normalize_expected(expected_lines)
    lines = markdown.split("\n")
    span = _parse_span(reviewed_span, len(lines))

    if span is None:
        declared_counts = Counter(expected)
        actual_counts = Counter(_normalized(line) for line in lines if line.strip())
        extras = [line for line, count in actual_counts.items() if line in declared_counts and count > declared_counts[line]]
        candidates = _find_candidates(lines, Counter(expected), 0, len(lines))
        if len(candidates) > 1:
            raise ValueError("reviewed line-group is absent or ambiguous")
        if not candidates:
            if extras:
                raise ValueError("reviewed line-group contains extra undeclared occurrences")
            raise ValueError("reviewed line-group is absent or ambiguous")
        if extras:
            raise ValueError("reviewed line-group contains extra undeclared occurrences")
        start, end = candidates[0]
    else:
        start, end = span
        if not _matches_exact_span(lines, expected, start, end):
            raise ValueError("reviewed line-group span is stale or contains undeclared content")

    rendered = [line + ("  " if index < len(expected) - 1 else "") for index, line in enumerate(expected)]
    lines[start:end + 1] = rendered
    return "\n".join(lines)


def _normalize_expected(expected_lines: Sequence[str]) -> list[str]:
    if isinstance(expected_lines, (str, bytes)) or not isinstance(expected_lines, Sequence):
        raise ValueError("reviewed line-group expected_lines must be a sequence")
    expected = [_normalized(line) for line in expected_lines]
    if len(expected) < 2 or any(not line.strip() for line in expected):
        raise ValueError("reviewed line-group requires at least two nonblank lines")
    return expected


def _normalized(line: str) -> str:
    if not isinstance(line, str):
        raise ValueError("reviewed line-group lines must be text")
    return line.rstrip(" \t")


def _parse_span(
    reviewed_span: Sequence[int] | Mapping[str, Any] | None, line_count: int,
) -> tuple[int, int] | None:
    if reviewed_span is None:
        return None
    if isinstance(reviewed_span, Mapping):
        if set(reviewed_span) != {"start_line", "end_line"}:
            raise ValueError("reviewed line-group span must name start_line and end_line")
        start_line, end_line = reviewed_span["start_line"], reviewed_span["end_line"]
    elif not isinstance(reviewed_span, (str, bytes)) and isinstance(reviewed_span, Sequence) and len(reviewed_span) == 2:
        start_line, end_line = reviewed_span
    else:
        raise ValueError("reviewed line-group span must be a two-line range")
    if type(start_line) is not int or type(end_line) is not int or start_line < 1 or end_line < start_line or end_line > line_count:
        raise ValueError("reviewed line-group span is outside Markdown")
    return start_line - 1, end_line - 1


def _find_candidates(
    lines: list[str], expected_counts: Counter[str], start: int, stop: int,
) -> list[tuple[int, int]]:
    candidates: list[tuple[int, int]] = []
    for candidate_start in range(start, stop):
        if not lines[candidate_start].strip() or _normalized(lines[candidate_start]) not in expected_counts:
            continue
        position = candidate_start
        candidate_lines = [_normalized(lines[position])]
        for _ in range(sum(expected_counts.values()) - 1):
            position += 1
            while position < stop and not lines[position].strip():
                position += 1
            if position >= stop:
                break
            candidate_lines.append(_normalized(lines[position]))
        else:
            if Counter(candidate_lines) == expected_counts:
                candidates.append((candidate_start, position))
    return candidates


def _matches_exact_span(lines: list[str], expected: list[str], start: int, end: int) -> bool:
    candidates = _find_candidates(lines, Counter(expected), start, end + 1)
    return candidates == [(start, end)]
