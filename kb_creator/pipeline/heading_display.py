"""Narrow display projection for OCR word wrapping in headings."""
from __future__ import annotations

import re


_WORD = r"[^\W\d_]+"
_WRAPPED_WORDS = re.compile(
    rf"(?<!\S)<(?P<tag>sup|sub)>(?P<words>{_WORD}(?:[ \t]+{_WORD})*)</(?P=tag)>(?!\S)",
    re.IGNORECASE,
)


def flatten_word_wrapped_heading(text: str) -> str:
    """Flatten only complete alphabetic words under an explicit heading policy.

    Attached exponents, digits, attributes, nesting and mixed HTML remain
    unchanged. Source text and its hashes are never rewritten by this projection.
    """
    projected = _WRAPPED_WORDS.sub(lambda match: match["words"], text)
    return text if "<" in projected or ">" in projected else projected
