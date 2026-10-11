"""Fail-closed raw interval operations for composite source-choice replay.

Offsets are sealed evidence.  This module intentionally has no substring
search helpers: callers must derive coordinates from their semantic authority.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from .identity import sha256_bytes


class SourceChoiceSliceError(ValueError):
    """A sealed source interval cannot safely be replayed."""


@dataclass(frozen=True)
class SourceSlice:
    start: int
    end: int
    before_sha256: str
    after: str


def slice_record(text: str, start: int, end: int) -> dict[str, object]:
    """Return exact interval evidence without discovering it from text."""
    if not isinstance(text, str) or type(start) is not int or type(end) is not int or not 0 <= start < end <= len(text):
        raise SourceChoiceSliceError("source slice coordinates are invalid")
    value = text[start:end]
    return {"raw_character_start": start, "raw_character_end": end,
            "raw_text_sha256": sha256_bytes(value.encode("utf-8"))}


def apply_sealed_slices(container: str, slices: Iterable[SourceSlice], *, container_sha256: str) -> str:
    """Apply disjoint intervals right-to-left after proving each predecessor."""
    if not isinstance(container, str) or sha256_bytes(container.encode("utf-8")) != container_sha256:
        raise SourceChoiceSliceError("selected source container identity drift")
    ordered = sorted(slices, key=lambda item: (item.start, item.end))
    previous = 0
    for item in ordered:
        if (type(item.start) is not int or type(item.end) is not int or not 0 <= item.start < item.end <= len(container)
                or not isinstance(item.before_sha256, str) or not isinstance(item.after, str)):
            raise SourceChoiceSliceError("source slice is malformed")
        if item.start < previous:
            raise SourceChoiceSliceError("source slices overlap")
        if sha256_bytes(container[item.start:item.end].encode("utf-8")) != item.before_sha256:
            raise SourceChoiceSliceError("source slice predecessor drift")
        previous = item.end
    result = container
    for item in reversed(ordered):
        result = result[:item.start] + item.after + result[item.end:]
    return result
