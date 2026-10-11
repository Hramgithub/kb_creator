"""Exact presentation replay for one corrected source block in a quote unit."""
from __future__ import annotations

from collections.abc import Mapping

from .identity import sha256_bytes
from .reviewed_correction_text import verify_visible_correction
from .semantic_structure import _fragment_text, apply_reviewed_text_corrections


def quote_text(text: str) -> str:
    """Keep every payload byte and paragraph boundary inside one quote."""
    if not isinstance(text, str) or not text or "\r" in text:
        raise ValueError("quoted payload requires nonempty LF text")
    result = "\n".join("> " + line if line else ">" for line in text.split("\n"))
    verify_visible_correction(result, text, {"start_line": 1, "end_line": len(result.split("\n"))})
    return result


def project_corrected_quote(decision: Mapping, packet_blocks: Mapping,
                            key: tuple[str, int], corrections: Mapping, page: int):
    """Return a sealed whole quote only for complete, exclusive source ownership.

    Other shapes retain their existing projection. Once a multiline quote owns
    this source, malformed ownership or reader drift is an error, never fallback.
    """
    units = decision.get("semantic_structure", {}).get("units", [])
    source_key = {"view": key[0], "raw_index": key[1]}
    owners = [u for u in units if source_key in u.get("source_blocks", [])]
    quoted = [u for u in owners if u.get("representation") == "blockquote"
              and u.get("markdown_span", {}).get("start_line") != u.get("markdown_span", {}).get("end_line")]
    if not quoted:
        return None
    if len(owners) != 1 or len(quoted) != 1:
        raise ValueError("corrected quote requires one source owner")
    unit = quoted[0]
    if (unit.get("kind") not in {"handout", "blockquote", "callout"}
            or unit.get("source_blocks") != [source_key]
            or unit.get("container_parent") is not None):
        raise ValueError("corrected quote has unsupported or composite ownership")
    source = packet_blocks[key]["text"]
    fragments = unit.get("source_fragments")
    if (not isinstance(fragments, list) or len(fragments) != 1
            or (fragments[0].get("view"), fragments[0].get("raw_index")) != key
            or fragments[0].get("start") != 0 or fragments[0].get("end") != len(source)
            or _fragment_text(packet_blocks[key], fragments[0], page) != source):
        raise ValueError("corrected quote requires one complete source fragment")
    pairs = corrections.get(key)
    if not pairs:
        raise ValueError("corrected quote lacks source corrections")
    corrected = apply_reviewed_text_corrections(source, key, [], {key: sorted(pairs, key=lambda p: source.index(p[0]))})
    expected = quote_text(corrected)
    lines = decision["markdown"].split("\n")
    span = unit.get("markdown_span", {})
    first, last = span.get("start_line"), span.get("end_line")
    if type(first) is not int or type(last) is not int or not 1 <= first < last <= len(lines):
        raise ValueError("corrected quote line bounds are invalid")
    reader = "\n".join(lines[first - 1:last])
    if reader != expected or span.get("sha256") != sha256_bytes(reader.encode()):
        raise ValueError("corrected quote reader differs from exact source presentation")
    for other in units:
        if other is unit:
            continue
        other_span = other.get("markdown_span", {})
        lo, hi = other_span.get("start_line"), other_span.get("end_line")
        if type(lo) is int and type(hi) is int and max(lo, first) <= min(hi, last):
            raise ValueError("corrected quote overlaps another semantic owner")
    return reader, {"policy": "reviewed_quote_container_v1", "semantic_unit_id": unit["id"],
                    "source_sha256": sha256_bytes(source.encode()),
                    "payload_sha256": sha256_bytes(corrected.encode()),
                    "reader_sha256": sha256_bytes(reader.encode()),
                    "source_fragment": fragments[0], "markdown_span": span}
