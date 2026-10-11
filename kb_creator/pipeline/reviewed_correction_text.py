"""Exact reader-visible Markdown evidence for reviewed text corrections.

This is deliberately a narrow adapter for already-reviewed semantic-unit spans.
It does not normalize Unicode, whitespace, case, punctuation, or numbers.
"""

from __future__ import annotations

from collections.abc import Mapping
from hashlib import sha256
import re
from typing import Any


class VisibleCorrectionError(ValueError):
    """Raised when a correction has no one exact visible-text occurrence."""


class UnsupportedMarkdownError(VisibleCorrectionError):
    """Raised for span syntax whose reader-visible projection is not contracted."""


_ATX_HEADING = re.compile(r" {0,3}#{1,6}(?:[ \t]+|$)")
_BLOCK_QUOTE = re.compile(r" {0,3}> ?")
_UNORDERED_LIST = re.compile(r" {0,3}[-+*][ \t]+")
_ORDERED_LIST = re.compile(r" {0,3}\d{1,9}[.)][ \t]+")
_HTML_TAG = re.compile(r"</?[A-Za-z][^>]*>")


def _line_range(markdown: str, markdown_span: Mapping[str, Any]) -> tuple[list[str], int, int]:
    if not isinstance(markdown, str):
        raise VisibleCorrectionError("markdown must be a string")
    if not isinstance(markdown_span, Mapping):
        raise VisibleCorrectionError("markdown_span must be a mapping")
    start = markdown_span.get("start_line")
    end = markdown_span.get("end_line")
    if type(start) is not int or type(end) is not int or start < 1 or end < start:
        raise VisibleCorrectionError("markdown_span must have positive ordered line bounds")
    lines = markdown.splitlines()
    if end > len(lines):
        raise VisibleCorrectionError("markdown_span exceeds Markdown line count")
    return lines[start - 1:end], start, end


def _project_block_line(line: str) -> str:
    """Project one unambiguous CommonMark-like block prefix.

    The correction helper is an evidence guard, not a general Markdown parser.
    It accepts one quote container followed by one heading or list marker.  It
    never repeatedly strips markers: content beginning with another block-like
    marker is ambiguous without a full parser and is rejected instead.
    """
    return _project_block_line_indexed(line)[0]


def _project_block_line_indexed(line: str) -> tuple[str, list[int]]:
    """Return the existing block projection with source character positions."""
    origin = 0
    quote = _BLOCK_QUOTE.match(line)
    if quote:
        origin += quote.end()
        line = line[quote.end():]
        if _BLOCK_QUOTE.match(line):
            raise UnsupportedMarkdownError("nested block quote is outside the visible-text contract")

    for pattern in (_ATX_HEADING, _UNORDERED_LIST, _ORDERED_LIST):
        match = pattern.match(line)
        if match:
            if pattern is _UNORDERED_LIST and line.lstrip().startswith("*"):
                raise UnsupportedMarkdownError("asterisk list syntax differs between reader parsers")
            content = line[match.end():]
            # A heading owns the rest of its line.  A list-looking heading title
            # therefore remains text, while a list item's second marker would
            # require nested-list parsing to classify correctly.
            if pattern is not _ATX_HEADING and any(
                nested.match(content)
                for nested in (_BLOCK_QUOTE, _ATX_HEADING, _UNORDERED_LIST, _ORDERED_LIST)
            ):
                raise UnsupportedMarkdownError("nested block syntax is outside the visible-text contract")
            origin += match.end()
            return content, list(range(origin, origin + len(content)))
    return line, list(range(origin, origin + len(line)))


def _delimiter_can_open(text: str, index: int, width: int) -> bool:
    following = index + width
    return (
        following < len(text)
        and not text[following].isspace()
        and (index == 0 or not text[index - 1].isalnum())
    )


def _delimiter_can_close(text: str, index: int, width: int) -> bool:
    following = index + width
    return (
        index > 0
        and not text[index - 1].isspace()
        and (following == len(text) or not text[following].isalnum())
    )


def _matching_emphasis_delimiter(text: str, index: int, delimiter: str) -> int | None:
    search = index + len(delimiter)
    while True:
        close = text.find(delimiter, search)
        if close < 0:
            return None
        if _delimiter_can_close(text, close, len(delimiter)):
            return close
        search = close + 1


def _inline_visible_text(text: str) -> str:
    """Project a conservative subset of inline Markdown into visible text.

    Inline code retains its content (including literal ``*``/``_`` markers), while
    Markdown delimiters and link destinations are not reader-visible.  Ambiguous
    or malformed constructs remain literal rather than being normalized away.
    """
    return _inline_visible_text_indexed(text)[0]


def _inline_visible_text_indexed(text: str, source_positions: list[int] | None = None) -> tuple[str, list[int]]:
    """Project inline syntax and retain each visible character's raw origin."""
    if source_positions is None:
        source_positions = list(range(len(text)))
    output: list[str] = []
    origins: list[int] = []
    index = 0
    while index < len(text):
        char = text[index]
        if char == "`":
            width = 1
            while index + width < len(text) and text[index + width] == "`":
                width += 1
            fence = "`" * width
            close = text.find(fence, index + width)
            if close < 0:
                raise UnsupportedMarkdownError("unclosed inline code span")
            output.append(text[index + width:close])
            origins.extend(source_positions[index + width:close])
            index = close + width
            continue
        if char == "[":
            label_end = text.find("](", index + 1)
            if label_end >= 0:
                label = text[index + 1:label_end]
                destination = text[label_end + 2:]
                destination_end = destination.find(")")
                if destination_end < 0:
                    raise UnsupportedMarkdownError("unclosed inline link destination")
                if "[" in label or "(" in destination[:destination_end]:
                    raise UnsupportedMarkdownError("nested inline link syntax is outside the visible-text contract")
                projected, positions = _inline_visible_text_indexed(label, source_positions[index + 1:label_end])
                output.append(projected)
                origins.extend(positions)
                index = label_end + 2 + destination_end + 1
                continue
        if char == "!" and index + 1 < len(text) and text[index + 1] == "[":
            raise UnsupportedMarkdownError("image syntax is outside the visible-text contract")
        if char in "*_":
            width = 1
            while index + width < len(text) and text[index + width] == char and width < 3:
                width += 1
            delimiter = char * width
            close = _matching_emphasis_delimiter(text, index, delimiter)
            if (
                close is not None
                and _delimiter_can_open(text, index, width)
            ):
                projected, positions = _inline_visible_text_indexed(
                    text[index + width:close], source_positions[index + width:close]
                )
                output.append(projected)
                origins.extend(positions)
                index = close + width
                continue
        output.append(char)
        origins.append(source_positions[index])
        index += 1
    return "".join(output), origins


def _visible_segments(markdown: str, markdown_span: Mapping[str, Any]) -> list[tuple[str, int, int]]:
    lines, first_line, _ = _line_range(markdown, markdown_span)
    segments: list[tuple[str, int, int]] = []
    current: list[str] = []
    segment_start = first_line
    for offset, source_line in enumerate(lines):
        line_number = first_line + offset
        if source_line.startswith(("```", "~~~")):
            raise UnsupportedMarkdownError("fenced code blocks are outside the visible-text contract")
        if _HTML_TAG.search(source_line):
            raise UnsupportedMarkdownError("HTML is outside the visible-text contract")
        if not source_line.strip():
            if current:
                segments.append(("\n".join(current), segment_start, line_number - 1))
                current = []
            segment_start = line_number + 1
            continue
        if not current:
            segment_start = line_number
        current.append(_inline_visible_text(_project_block_line(source_line)))
    if current:
        segments.append(("\n".join(current), segment_start, first_line + len(lines) - 1))
    return segments


def _occurrences(text: str, needle: str) -> list[int]:
    result: list[int] = []
    start = 0
    while True:
        found = text.find(needle, start)
        if found < 0:
            return result
        result.append(found)
        start = found + 1


def verify_visible_correction(
    markdown: str, corrected_text: str, markdown_span: Mapping[str, Any],
) -> dict[str, Any]:
    """Require one exact corrected-text occurrence in one reviewed unit span.

    The caller must supply the unit's reviewed ``markdown_span``.  This prevents
    a correction from being satisfied by a duplicate on an unrelated page block.
    A match may cross adjacent nonblank lines in that unit, but never a blank
    line, which keeps separately rendered blocks from being concatenated.
    """
    if not isinstance(corrected_text, str) or not corrected_text:
        raise VisibleCorrectionError("corrected_text must be a nonempty string")
    matches: list[tuple[int, int, int]] = []
    for visible_text, start_line, end_line in _visible_segments(markdown, markdown_span):
        for offset in _occurrences(visible_text, corrected_text):
            matches.append((start_line, end_line, offset))
    if not matches:
        raise VisibleCorrectionError("corrected text is absent from the reviewed visible span")
    if len(matches) != 1:
        raise VisibleCorrectionError("corrected text is ambiguous in the reviewed visible span")
    start_line, end_line, offset = matches[0]
    return {
        "corrected_text_sha256": sha256(corrected_text.encode("utf-8")).hexdigest().upper(),
        "match_offset": offset,
        "span_start_line": start_line,
        "span_end_line": end_line,
    }
