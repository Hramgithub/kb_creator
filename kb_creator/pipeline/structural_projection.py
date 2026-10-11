"""Exact, source-position-preserving projection after lexical R1 replay."""
from __future__ import annotations

from typing import Any, Callable, Mapping

from .identity import sha256_bytes


def _sha(text: str) -> str:
    return sha256_bytes(text.encode("utf-8"))


def _patch_projection(before: str, after: str, patch: Mapping[str, Any]) -> list[int | None]:
    """Map each result character to one character in the exact patch preimage."""
    interval_map = patch.get("interval_map")
    if interval_map is None:
        if after == "- " + before:
            return [None, None, *range(len(before))]
        if len(before) >= 2 and before[0] in "HUT" and before[1] == " " and after == "-" + before[1:]:
            return [None, *range(1, len(before))]
        raise ValueError("structural patch is not a conserved list-marker operation")
    if not isinstance(interval_map, dict) or set(interval_map) != {"segments", "removed_intervals"}:
        raise ValueError("structural interval map has an invalid shape")
    segments, removed = interval_map["segments"], interval_map["removed_intervals"]
    if not isinstance(segments, list) or not segments or not isinstance(removed, list):
        raise ValueError("structural interval map is incomplete")
    used: set[int] = set()
    result: list[str] = []
    origins: list[int | None] = []
    patch_order = [(item["view"], item["raw_index"]) for item in patch["source_occurrences"]]
    for segment in segments:
        if not isinstance(segment, dict) or segment.get("kind") not in {"copy", "literal"}:
            raise ValueError("structural interval segment is malformed")
        if segment["kind"] == "copy":
            if set(segment) != {"kind", "start", "end", "sha256", "source_occurrences"}:
                raise ValueError("structural copied interval is malformed")
            start, end = segment["start"], segment["end"]
            keys = segment["source_occurrences"]
            key_order = [(key.get("view"), key.get("raw_index")) for key in keys] if isinstance(keys, list) and all(isinstance(key, dict) for key in keys) else []
            if (type(start) is not int or type(end) is not int or not 0 <= start < end <= len(before)
                    or not isinstance(keys, list) or not keys
                    or any(not isinstance(key, dict) or set(key) != {"view", "raw_index"}
                           or (key["view"], key["raw_index"]) not in patch_order for key in keys)
                    or len(set(key_order)) != len(key_order)
                    or key_order != sorted(key_order, key=patch_order.index)
                    or segment["sha256"] != _sha(before[start:end])
                    or any(index in used for index in range(start, end))):
                raise ValueError("structural copied interval is stale, foreign, or repeated")
            used.update(range(start, end))
            result.append(before[start:end]); origins.extend(range(start, end))
        else:
            if set(segment) != {"kind", "text", "sha256"} or segment["text"] not in {"-", "- "} or segment["sha256"] != _sha(segment["text"]):
                raise ValueError("structural literal is not a reviewed list marker")
            result.append(segment["text"]); origins.extend([None] * len(segment["text"]))
    removed_positions: set[int] = set()
    for item in removed:
        if not isinstance(item, dict) or set(item) != {"start", "end", "sha256", "reason", "source_occurrence"}:
            raise ValueError("structural removed interval is malformed")
        start, end = item["start"], item["end"]
        source_key = item["source_occurrence"]
        if not isinstance(source_key, dict) or set(source_key) != {"view", "raw_index"}:
            raise ValueError("structural ornament has no qualified source occurrence")
        qualified_key = (source_key["view"], source_key["raw_index"])
        bound_copy = any(segment.get("kind") == "copy"
                         and source_key in segment.get("source_occurrences", [])
                         and segment["start"] == end
                         for segment in segments if isinstance(segment, dict))
        earlier_copy = any(segment.get("kind") == "copy"
                           and source_key in segment.get("source_occurrences", [])
                           and segment["start"] < start
                           for segment in segments if isinstance(segment, dict))
        if (type(start) is not int or type(end) is not int or not 0 <= start < end <= len(before)
                or item["reason"] != "reviewed_ornament" or before[start:end] not in {"H", "U", "T"}
                or (start != 0 and before[start - 1] != "\n") or end >= len(before) or before[end] != " "
                or qualified_key not in patch_order or not bound_copy or earlier_copy
                or item["sha256"] != _sha(before[start:end])
                or any(index in used or index in removed_positions for index in range(start, end))):
            raise ValueError("structural ornament deletion is stale or repeated")
        removed_positions.update(range(start, end))
    if used | removed_positions != set(range(len(before))) or "".join(result) != after:
        raise ValueError("structural interval map does not conserve the exact preimage")
    return origins


def project_structural_page(lexical_page: str, patches: list[Mapping[str, Any]]) -> tuple[str, list[int | None]]:
    """Apply ordered reviewed operations, retaining every surviving R1 position."""
    if not isinstance(lexical_page, str) or not isinstance(patches, list):
        raise ValueError("structural page projection input is malformed")
    current = lexical_page
    origins: list[int | None] = list(range(len(current)))
    for patch in patches:
        if not isinstance(patch, Mapping) or patch.get("count") != 1:
            raise ValueError("structural patch count is invalid")
        before, after = patch.get("before"), patch.get("after")
        if (not isinstance(before, str) or not before or not isinstance(after, str)
                or patch.get("before_sha256") != _sha(before) or patch.get("after_sha256") != _sha(after)):
            raise ValueError("structural patch text identity is stale")
        if current.count(before) != 1:
            raise ValueError("structural patch preimage is absent or ambiguous")
        start = current.index(before); end = start + len(before)
        local = _patch_projection(before, after, patch)
        replacement_origins = [origins[start + index] if index is not None else None for index in local]
        current = current[:start] + after + current[end:]
        origins = origins[:start] + replacement_origins + origins[end:]
    return current, origins


def validate_ornament_source(patch: Mapping[str, Any], page: int,
                             list_candidates: set[tuple[int, str, int]],
                             source_text: Callable[[int, str, int], str],
                             current_page: str) -> None:
    """Bind deletion to the full classified source occurrence's page position."""
    before, after = patch["before"], patch["after"]
    if current_page.count(before) != 1:
        raise ValueError("structural ornament patch preimage is absent or ambiguous")
    patch_start = current_page.index(before)

    def leading_position(identity: tuple[int, str, int], ornament: str, offset: int) -> bool:
        if identity not in list_candidates:
            return False
        raw = source_text(*identity)
        if (not raw.startswith(ornament + " ") or current_page.find(raw) < 0
                or current_page.find(raw) != current_page.rfind(raw)):
            return False
        return current_page.index(raw) == patch_start + offset

    interval_map = patch.get("interval_map")
    if interval_map is None:
        if len(before) < 2 or before[0] not in "HUT" or after != "-" + before[1:]:
            return
        eligible = [(page, item["view"], item["raw_index"]) for item in patch["source_occurrences"]
                    if leading_position((page, item["view"], item["raw_index"]), before[0], 0)]
        if len(eligible) != 1:
            raise ValueError("structural ornament lacks one exact leading source position")
        return
    for removed in interval_map["removed_intervals"]:
        key = removed["source_occurrence"]
        identity = (page, key["view"], key["raw_index"])
        ornament = before[removed["start"]:removed["end"]]
        if not leading_position(identity, ornament, removed["start"]):
            raise ValueError("structural ornament is not at the classified source occurrence's leading position")


def project_interval(current: str, origins: list[int | None], start: int, end: int, *,
                     allow_ornament_deletion: bool = False) -> dict[str, Any]:
    """Project one immutable lexical interval; reject loss or fragmentation."""
    if type(start) is not int or type(end) is not int or not 0 <= start < end:
        raise ValueError("lexical interval is malformed")
    positions = [index for index, origin in enumerate(origins) if origin is not None and start <= origin < end]
    source_positions = [origins[index] for index in positions]
    if (not positions or positions != list(range(positions[0], positions[-1] + 1))
            or source_positions != sorted(set(source_positions))
            or (not allow_ornament_deletion and source_positions != list(range(start, end)))
            or (allow_ornament_deletion and len(source_positions) < end - start - 1)):
        raise ValueError("structural projection removes or fragments a lexical interval")
    low, high = positions[0], positions[-1] + 1
    return {"character_start": low, "character_end": high, "text_sha256": _sha(current[low:high])}


def _definition_lines(lines: list[str], definition: Mapping[str, Any]) -> tuple[int, int]:
    """Resolve the two selector forms accepted by the reviewed author."""
    if "start_line" in definition or "end_line" in definition:
        start, end = definition.get("start_line"), definition.get("end_line")
        if type(start) is not int or type(end) is not int or not 1 <= start <= end <= len(lines):
            raise ValueError("retained owner line selector is invalid")
        return start, end
    start_text, end_text = definition.get("start"), definition.get("end")
    if not isinstance(start_text, str) or (end_text is not None and not isinstance(end_text, str)):
        raise ValueError("retained owner text selector is invalid")
    starts = [index for index, line in enumerate(lines) if start_text in line]
    if len(starts) != 1:
        raise ValueError("retained owner text selector is ambiguous")
    first = starts[0]
    if end_text is None:
        return first + 1, first + 1
    ends = [index for index in range(first, len(lines)) if end_text in lines[index]]
    if len(ends) != 1:
        raise ValueError("retained owner text selector is ambiguous")
    return first + 1, ends[0] + 1


def _line_interval(lines: list[str], start: int, end: int) -> tuple[int, int]:
    low = sum(len(line) + 1 for line in lines[:start - 1])
    return low, low + len("\n".join(lines[start - 1:end]))


def retained_assertion_key(assertion: Any) -> tuple[int, str, int]:
    """Check the same closed retained-assertion domain at both seal boundaries."""
    required = {"source_page", "view", "raw_index", "source_text_sha256",
                "owner_id", "representation", "visual_group_id"}
    if (not isinstance(assertion, dict) or set(assertion) != required
            or type(assertion["source_page"]) is not int or assertion["source_page"] < 1
            or not isinstance(assertion["view"], str)
            or assertion["view"] not in {"original_pipeline_txt", "original_pipeline_ocr", "raster_pipeline_ocr"}
            or type(assertion["raw_index"]) is not int or assertion["raw_index"] < 0
            or not isinstance(assertion["source_text_sha256"], str)
            or len(assertion["source_text_sha256"]) != 64
            or any(character not in "0123456789abcdefABCDEF" for character in assertion["source_text_sha256"])
            or not isinstance(assertion["owner_id"], str) or not assertion["owner_id"]
            or assertion["representation"] != "unordered_list"
            or not isinstance(assertion["visual_group_id"], str) or not assertion["visual_group_id"]):
        raise ValueError("retained owner assertion is malformed")
    return assertion["source_page"], assertion["view"], assertion["raw_index"]


def validate_retained_owner_projection(*, assertion: Mapping[str, Any], owner: Mapping[str, Any],
        predecessor_definition: Mapping[str, Any], successor_definition: Mapping[str, Any],
        predecessor_markdown: str, effective_markdown: str, default_view: str | None = None,
        patches: list[Mapping[str, Any]]) -> None:
    """Prove that a retained owner's exact authored span selects its projected origins."""
    old, new = predecessor_definition, successor_definition
    if not isinstance(old, Mapping) or not isinstance(new, Mapping):
        raise ValueError("retained owner definition is malformed")
    def without_lines(value: Mapping[str, Any]) -> dict[str, Any]:
        return {key: item for key, item in value.items()
                if key not in {"start_line", "end_line"}}
    if without_lines(old) != without_lines(new):
        raise ValueError("retained owner unit is missing or changed")
    if (("start_line" in old) != ("start_line" in new)
            or ("end_line" in old) != ("end_line" in new)):
        raise ValueError("retained owner selector conversion is unsupported")
    if not isinstance(predecessor_markdown, str) or effective_markdown != predecessor_markdown:
        raise ValueError("retained owner effective/stored Markdown coordinates differ")
    span = owner.get("markdown_span")
    lines = predecessor_markdown.split("\n")
    if (not isinstance(span, Mapping) or set(span) != {"start_line", "end_line", "sha256"}
            or type(span["start_line"]) is not int or type(span["end_line"]) is not int
            or not 1 <= span["start_line"] <= span["end_line"] <= len(lines)):
        raise ValueError("retained owner authored span is invalid")
    old_bounds = _definition_lines(lines, old)
    if old_bounds != (span["start_line"], span["end_line"]):
        raise ValueError("retained owner authored span differs from predecessor selector")
    old_low, old_high = _line_interval(lines, *old_bounds)
    old_text = predecessor_markdown[old_low:old_high]
    if span["sha256"] != _sha(old_text):
        raise ValueError("retained owner authored span hash is stale")
    authored_sources = owner.get("source_blocks")
    if not isinstance(authored_sources, list) or not authored_sources or not isinstance(authored_sources[0], Mapping):
        raise ValueError("retained owner authored sources are malformed")
    default_view = default_view or authored_sources[0].get("view")
    raw_indices = old.get("raw_indices")
    if not isinstance(raw_indices, list) or not raw_indices or any(type(index) is not int for index in raw_indices):
        raise ValueError("retained owner definition sources are malformed")
    expected_sources = [{"view": old.get("view") or default_view,
                         "raw_index": index} for index in raw_indices]
    if "source_fragments" in old and "visual_assertion_ids" not in old:
        selectors = old["source_fragments"]
        actual_fragments = owner.get("source_fragments")
        if (not isinstance(selectors, list) or not isinstance(actual_fragments, list)
                or [{"view": item.get("view", default_view), "raw_index": item.get("raw_index"),
                     "start": item.get("start"), "end": item.get("end")}
                    for item in selectors if isinstance(item, Mapping)] !=
                    [{key: fragment.get(key) for key in ("view", "raw_index", "start", "end")}
                     for fragment in actual_fragments if isinstance(fragment, Mapping)]
                or any(not isinstance(item, Mapping) for item in selectors + actual_fragments)):
            raise ValueError("retained owner source fragments differ from authored owner")
    if (owner.get("id") != assertion.get("owner_id") or old.get("id") != owner.get("id")
            or old.get("kind") != owner.get("kind") or old.get("representation") != owner.get("representation")
            or expected_sources != authored_sources
            or {"view": assertion.get("view"), "raw_index": assertion.get("raw_index")}
            not in expected_sources
            or any(old.get(field) != owner.get(field) for field in
                   ("container_parent", "semantic_parent", "continuation_of", "heading_level", "item_count"))
            or ("visual_assertion_ids" in old and old["visual_assertion_ids"] != owner.get("visual_assertion_ids"))):
        raise ValueError("retained owner definition differs from authored owner")
    current, origins = project_structural_page(predecessor_markdown, patches)
    mapped = project_interval(current, origins, old_low, old_high)
    low, high = mapped["character_start"], mapped["character_end"]
    if current[low:high].encode("utf-8") != old_text.encode("utf-8"):
        raise ValueError("retained owner projected bytes changed")
    new_lines = current.split("\n")
    if _line_interval(new_lines, *_definition_lines(new_lines, new)) != (low, high):
        raise ValueError("retained owner selector differs from projected interval")
