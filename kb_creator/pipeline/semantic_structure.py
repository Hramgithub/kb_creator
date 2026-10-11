"""Closed, visual-review-bound semantic Markdown structure validation.

This module is deliberately independent of scenario vocabulary.  It is used by
both replay Stage 05 and Stage 06 so that a candidate cannot be materialized
with Markdown whose reviewed container topology differs from the audited form.
"""
from __future__ import annotations

import hashlib
import re
import unicodedata
from typing import Any, Mapping

from kb_creator.pipeline.reviewed_correction_text import (
    VisibleCorrectionError,
    verify_visible_correction,
)

PROFILE = "visually_reviewed_semantic_containers_v1"
SCHEMA = "kb_creator.page_semantic_structure.v1"
PROFILE_V2 = "reviewed_role_outline_and_partitions_v2"
SCHEMA_V2 = "kb_creator.page_semantic_structure.v2"
KIND_REPRESENTATIONS = {
    "blockquote": {"blockquote"}, "callout": {"blockquote"},
    "handout": {"blockquote"}, "list": {"unordered_list", "ordered_list"},
    "statblock": {"blockquote", "table"}, "heading": {"atx_heading"},
    "line_group": {"hard_break_lines"},
}
_SOURCE_UNORDERED_LIST_MARKER = re.compile(r"^[*+\-•‣⁃◦▪▫][ \t]+")
V2_KIND_REPRESENTATIONS = {
    **KIND_REPRESENTATIONS,
    # A v2 statblock is not a quotation.  `semantic_span` means that its exact
    # plain-Markdown boundary is carried only by the sealed sidecar.  Tables
    # remain self-delimiting Markdown.  Historical v1 blockquote statblocks
    # stay readable but cannot be authored as new v2 decisions.
    "statblock": {"semantic_span", "table"},
    "label": {"semantic_span"},
    # Ordinary prose can bind one reviewed source span when reconstruction
    # joins corrected source fragments.  It remains deliberately narrower
    # than a general Markdown container.
    "paragraph": {"semantic_span"},
}
_ID = re.compile(r"^[A-Za-z][A-Za-z0-9._-]*$")
_ATX = re.compile(r"^(#{1,6})[ \t]+\S.*$")
_UL = re.compile(r"^[*-][ \t]+\S")
_OL = re.compile(r"^\d+[.)][ \t]+\S")
_INLINE_TAG = re.compile(r"</?(?:sup|sub)>", re.IGNORECASE)
_TEXT_CORRECTION = re.compile(
    r"^text correction: (?P<before>.+?) -> (?P<after>.+?); reason: (?P<reason>.+)$"
)
_TITLE_EVIDENCE_CONFIRMATION = re.compile(
    r"^title evidence confirmation: (?P<view>[A-Za-z0-9_.-]+):(?P<raw_index>\d+) -> (?P<reader>.+?); reason: (?P<reason>.+)$"
)
TITLE_EVIDENCE_KEYS = (
    "text_level", "v2_title", "middle_title", "markdown_heading", "model_title",
)


class SemanticStructureError(ValueError):
    pass


def apply_block_boundaries(markdown: str, boundaries: Any) -> str:
    """Apply the pre-existing, intentionally narrow compact-boundary transform."""
    if boundaries is None:
        return markdown
    if not isinstance(boundaries, list) or not boundaries:
        raise SemanticStructureError("block_boundaries must be a nonempty list when present")
    lines = markdown.split("\n")
    selectors: set[tuple[str, str]] = set(); removals: list[int] = []
    for row in boundaries:
        if not isinstance(row, dict) or set(row) != {"style", "heading_line", "first_body_line"}:
            raise SemanticStructureError("block boundary must have exact keys")
        heading, first = row["heading_line"], row["first_body_line"]
        if row["style"] != "compact":
            raise SemanticStructureError("unsupported block boundary style")
        if not isinstance(heading, str) or not _ATX.fullmatch(heading):
            raise SemanticStructureError("compact block boundary heading_line must be one exact ATX heading")
        if not isinstance(first, str) or not first.strip() or "\n" in first:
            raise SemanticStructureError("compact block boundary first_body_line must be one exact nonempty line")
        if (heading, first) in selectors:
            raise SemanticStructureError("duplicate compact block boundary selector")
        if lines.count(heading) != 1:
            raise SemanticStructureError("compact block boundary heading_line must match exactly once")
        selectors.add((heading, first))
        hits = [index for index in range(len(lines) - 2) if lines[index] == heading and lines[index + 1] == "" and lines[index + 2] == first]
        if len(hits) != 1:
            raise SemanticStructureError("compact block boundary must match exactly one heading, one empty separator, and its first body line")
        removals.append(hits[0] + 1)
    if len(set(removals)) != len(removals):
        raise SemanticStructureError("compact block boundaries overlap")
    for index in sorted(removals, reverse=True):
        del lines[index]
    return "\n".join(lines)


def _span_hash(lines: list[str], start: int, end: int) -> str:
    return hashlib.sha256("\n".join(lines[start - 1:end]).encode("utf-8")).hexdigest().upper()


def _normalized(value: str) -> str:
    return "".join(char for char in unicodedata.normalize("NFKC", _INLINE_TAG.sub("", value)).casefold() if char.isalnum())


def extract_atx_heading_label(span_text: str, heading_level: int) -> str:
    """Return the one display label in a reviewed ATX heading container.

    A source-less positional proof may cover a title and its byline.  Consumers
    must use this label, never the complete proof span, for outline and TOC
    text.
    """
    matches = [line for line in span_text.split("\n") if _ATX.fullmatch(line)]
    if len(matches) != 1 or len(_ATX.fullmatch(matches[0]).group(1)) != heading_level:
        raise SemanticStructureError("ATX heading level mismatch")
    return re.sub(r"[ \t]+#*[ \t]*$", "", _ATX.fullmatch(matches[0]).group(0).split(None, 1)[1])


def _profile(decision: Mapping[str, Any], page: int) -> str:
    """Return the explicitly selected semantic profile; never upgrade v1."""
    structure = decision.get("semantic_structure")
    if not isinstance(structure, Mapping):
        raise SemanticStructureError(f"page {page}: missing semantic_structure")
    if structure.get("schema") == SCHEMA:
        if set(structure) != {"schema", "review", "units"}:
            raise SemanticStructureError(f"page {page}: missing or invalid semantic_structure")
        return PROFILE
    if structure.get("schema") == SCHEMA_V2:
        if set(structure) != {"schema", "profile", "role_contract", "review", "units"} or structure.get("profile") != PROFILE_V2:
            raise SemanticStructureError(f"page {page}: invalid v2 semantic_structure")
        return PROFILE_V2
    raise SemanticStructureError(f"page {page}: missing or invalid semantic_structure")


def _fragment_text(block: Mapping[str, Any], fragment: Mapping[str, Any], page: int) -> str:
    """Bind an author-reviewed byte range, rather than guessing a title split."""
    expected = {"view", "raw_index", "source_sha256", "normalized_sha256", "start", "end", "fragment_sha256"}
    if set(fragment) != expected or type(fragment.get("raw_index")) is not int or type(fragment.get("start")) is not int or type(fragment.get("end")) is not int:
        raise SemanticStructureError(f"source_fragment_invalid: page {page}")
    text = block.get("text")
    if not isinstance(text, str) or not 0 <= fragment["start"] < fragment["end"] <= len(text):
        raise SemanticStructureError(f"source_fragment_out_of_range: page {page}")
    if fragment["source_sha256"] != hashlib.sha256(text.encode("utf-8")).hexdigest().upper():
        raise SemanticStructureError(f"source_fragment_stale: page {page}")
    value = text[fragment["start"]:fragment["end"]]
    if (
        fragment["fragment_sha256"] != hashlib.sha256(value.encode("utf-8")).hexdigest().upper()
        or fragment["normalized_sha256"] != hashlib.sha256(_normalized(value).encode("utf-8")).hexdigest().upper()
    ):
        raise SemanticStructureError(f"source_fragment_stale: page {page}")
    return value


def _validate_v2_fragments(
    page: int, units: list[dict[str, Any]], packet_blocks: Mapping[tuple[str, int], Mapping[str, Any]],
    lines: list[str], selected: set[tuple[str, int]],
    text_corrections: list[tuple[str, str]], block_corrections: Mapping[tuple[str, int], list[tuple[str, str]]],
) -> None:
    """Require exact, lossless reviewed partitions when a source block is split."""
    by_source: dict[tuple[str, int], list[tuple[int, int, str]]] = {}
    for unit in units:
        fragments = unit.get("source_fragments")
        if not isinstance(fragments, list):
            raise SemanticStructureError(f"source_fragments_required: page {page}")
        if not fragments and not unit.get("visual_assertion_ids"):
            raise SemanticStructureError(f"source_fragments_empty_without_visual_proof: page {page}")
        span = unit["markdown_span"]
        reader = _normalized("\n".join(lines[span["start_line"] - 1:span["end_line"]]))
        prefix = _normalized("\n".join(lines[:span["start_line"] - 1]))
        fragment_reader = ""
        for fragment in fragments:
            if not isinstance(fragment, dict):
                raise SemanticStructureError(f"source_fragment_invalid: page {page}")
            key = (fragment.get("view"), fragment.get("raw_index"))
            if key not in selected or key not in packet_blocks:
                raise SemanticStructureError(f"source_fragment_unselected: page {page}")
            text = _fragment_text(packet_blocks[key], fragment, page)
            # Fragment offsets and hashes bind the immutable extracted bytes.
            # Reader comparison consumes the same exact visually reviewed
            # correction ledger as whole-source-block validation; otherwise a
            # valid partition containing an accepted OCR repair can never
            # match its reviewed Markdown.
            text = apply_reviewed_text_corrections(text, key, text_corrections, block_corrections)
            fragment_reader += _normalized(text)
            by_source.setdefault(key, []).append((fragment["start"], fragment["end"], unit["id"]))
        if fragment_reader and fragment_reader not in reader:
            raise SemanticStructureError(
                f"source_fragment_reader_loss: page {page}: unit {unit['id']}"
            )
    for key, intervals in by_source.items():
        intervals.sort()
        text = packet_blocks[key].get("text")
        if not isinstance(text, str) or intervals[0][0] != 0 or intervals[-1][1] != len(text):
            raise SemanticStructureError(f"source_partition_loss: page {page}")
        previous = 0
        for start, end, _ in intervals:
            if start != previous:
                raise SemanticStructureError(f"source_partition_overlap_or_loss: page {page}")
            previous = end


def _v2_line_group_source_lines(
    page: int, unit: Mapping[str, Any], source_keys: list[tuple[str, int]],
    packet_blocks: Mapping[tuple[str, int], Mapping[str, Any]],
    text_corrections: list[tuple[str, str]],
    block_corrections: Mapping[tuple[str, int], list[tuple[str, str]]],
) -> list[str]:
    """Read v2 line groups from their exact physical source fragments.

    A v2 fragment may partition a source block between semantic units.  For a
    hard-break group, every selected fragment must start and end at a physical
    line boundary; concatenating a partial source line would conceal a bad
    reviewed partition or alter the line-count evidence.
    """
    fragments = unit["source_fragments"]
    source_rank = {key: index for index, key in enumerate(source_keys)}
    prior_rank = -1
    prior_end: dict[tuple[str, int], int] = {}
    result: list[str] = []
    for fragment in fragments:
        if not isinstance(fragment, Mapping):
            raise SemanticStructureError(f"source_fragment_invalid: page {page}")
        key = (fragment.get("view"), fragment.get("raw_index"))
        if key not in source_rank or key not in packet_blocks:
            raise SemanticStructureError(f"line-group source fragment is unbound: page {page}")
        raw_value = _fragment_text(packet_blocks[key], fragment, page)
        rank = source_rank[key]
        if rank < prior_rank or fragment["start"] < prior_end.get(key, -1):
            raise SemanticStructureError(f"line-group source fragment order mismatch: page {page}")
        prior_rank = rank
        prior_end[key] = fragment["end"]
        source = packet_blocks[key].get("text")
        if not isinstance(source, str):
            raise SemanticStructureError(f"page {page}: line-group source block has no text")
        start, end = fragment["start"], fragment["end"]
        if (start > 0 and source[start - 1] != "\n") or (end < len(source) and source[end - 1] != "\n"):
            raise SemanticStructureError(f"line-group source fragment cuts a physical line: page {page}")
        value = apply_reviewed_text_corrections(
            raw_value, key, text_corrections, block_corrections,
        )
        lines = [_INLINE_TAG.sub("", line).rstrip(" \t") for line in value.splitlines()]
        if not lines or any(not line.strip() for line in lines):
            raise SemanticStructureError(f"page {page}: line-group source contains an empty line")
        result.extend(lines)
    if not result:
        raise SemanticStructureError(f"page {page}: line-group source fragments are empty")
    return result


def _validate_v2_visual_assertions(
    page: int, units: list[dict[str, Any]], lines: list[str], assertions: Mapping[str, Mapping[str, Any]],
    *, packet: Mapping[str, Any] | None = None, decision: Mapping[str, Any] | None = None,
) -> None:
    """Bind image-only reader wording to sealed assertion spans, never to OCR text."""
    claimed: set[str] = set()
    for unit in units:
        ids = unit.get("visual_assertion_ids", [])
        if not isinstance(ids, list) or len(ids) != len(set(ids)) or any(not isinstance(value, str) or not value for value in ids):
            raise SemanticStructureError(f"visual_assertion_ids_invalid: page {page}")
        if not ids:
            continue
        span = unit["markdown_span"]
        from kb_creator.scripts.audit_mineru_ai_merge_fidelity import ASSET, IMAGE
        reader_text = "\n".join(lines[span["start_line"] - 1:span["end_line"]])
        prefix_text = "\n".join(lines[:span["start_line"] - 1])
        reader = _normalized(ASSET.sub("", IMAGE.sub("", reader_text)))
        prefix = _normalized(ASSET.sub("", IMAGE.sub("", prefix_text)))
        intervals: list[tuple[int, int]] = []
        for identity in ids:
            row = assertions.get(identity)
            if row is None or row.get("source_page") != page or identity in claimed:
                raise SemanticStructureError(f"visual_assertion_unbound_or_reused: page {page}")
            placement = row.get("placement")
            from .empty_text_assertions import RELATION as EMPTY_TEXT_RELATION
            if not isinstance(placement, Mapping):
                raise SemanticStructureError(f"visual_assertion_wrong_variant: page {page}")
            positional = placement.get("relation") in {"before_anchor", "after_anchor", "column_before_anchor", "column_after_anchor"}
            if placement.get("relation") not in {"within_selected_asset_region", EMPTY_TEXT_RELATION} and not positional:
                raise SemanticStructureError(f"visual_assertion_wrong_variant: page {page}")
            if positional:
                if (unit["kind"], unit["representation"], unit["source_blocks"], unit["source_fragments"], len(ids)) != ("heading", "atx_heading", [], [], 1):
                    raise SemanticStructureError(f"source_less_positional_heading_invalid: page {page}")
                proof_span = placement.get("markdown_span")
                if not isinstance(proof_span, Mapping):
                    raise SemanticStructureError(f"positional_assertion_context_missing: page {page}")
                start, end = proof_span.get("start"), proof_span.get("end")
                if type(start) is not int or type(end) is not int or start != 0 or end != len(reader) or reader != _normalized(row.get("text", "")):
                    raise SemanticStructureError(f"source_less_positional_heading_coverage: page {page}")
                anchor = placement.get("anchor_unit")
                if not isinstance(anchor, Mapping):
                    raise SemanticStructureError(f"source_less_positional_heading_anchor: page {page}")
                anchor_key = {"view": anchor.get("view_id"), "raw_index": anchor.get("raw_index")}
                if not any(other is not unit and anchor_key in other.get("source_blocks", []) for other in units):
                    raise SemanticStructureError(f"source_less_positional_heading_anchor_owner: page {page}")
                extract_atx_heading_label(reader_text, unit["heading_level"])
                claimed.add(identity)
                intervals.append((0, len(reader)))
                continue
            if placement.get("relation") == EMPTY_TEXT_RELATION:
                from .empty_text_assertions import validate as validate_empty_assertion
                if packet is None or decision is None:
                    raise SemanticStructureError(f"empty_text_assertion_context_missing: page {page}")
                try:
                    validate_empty_assertion(row, packet, decision, _normalized(ASSET.sub("", IMAGE.sub("", "\n".join(lines)))))
                except ValueError as exc:
                    raise SemanticStructureError(f"empty_text_assertion_invalid: page {page}: {exc}") from exc
                block = placement["source_block"]
                if unit["source_blocks"] != [{"view": block["view_id"], "raw_index": block["raw_index"]}]:
                    raise SemanticStructureError(f"empty_text_assertion_wrong_owner: page {page}")
            proof_span = placement.get("markdown_span")
            if not isinstance(proof_span, Mapping):
                raise SemanticStructureError(f"visual_assertion_span_invalid: page {page}")
            start, end = proof_span.get("start"), proof_span.get("end")
            local_start, local_end = start - len(prefix), end - len(prefix)
            if type(start) is not int or type(end) is not int or not (0 <= local_start < local_end <= len(reader)) or reader[local_start:local_end] != _normalized(row.get("text", "")):
                raise SemanticStructureError(f"visual_assertion_span_invalid: page {page}")
            if any(local_start < old_end and local_end > old_start for old_start, old_end in intervals):
                raise SemanticStructureError(f"visual_assertion_span_overlap: page {page}")
            intervals.append((local_start, local_end)); claimed.add(identity)
        if not unit["source_fragments"]:
            intervals.sort()
            if intervals[0][0] != 0 or intervals[-1][1] != len(reader) or any(left[1] != right[0] for left, right in zip(intervals, intervals[1:])):
                raise SemanticStructureError(f"visual_assertion_coverage_gap: page {page}")


def _v2_unit_binds_selected_asset(
    page: int, unit: Mapping[str, Any], key: tuple[str, int], logical_name: str,
    assertions: Mapping[str, Mapping[str, Any]] | None,
) -> bool:
    """Return whether this image-only unit is bound to its exact selected asset."""
    if assertions is None:
        return False
    identities = unit.get("visual_assertion_ids")
    if not isinstance(identities, list):
        return False
    for identity in identities:
        row = assertions.get(identity)
        placement = row.get("placement") if isinstance(row, Mapping) else None
        asset_block = placement.get("asset_block") if isinstance(placement, Mapping) else None
        if (
            isinstance(asset_block, Mapping)
            and row.get("source_page") == page
            and placement.get("relation") == "within_selected_asset_region"
            and placement.get("logical_name") == logical_name
            and asset_block.get("source_page") == page
            and asset_block.get("view_id") == key[0]
            and asset_block.get("raw_index") == key[1]
        ):
            return True
    return False


def collect_reference_image_proof_keys(
    decisions: Mapping[int, Mapping[str, Any]],
    packets: Mapping[int, Mapping[str, Any]],
    visual_assertions: Mapping[str, Mapping[str, Any]],
) -> set[tuple[int, str, int, str, str]]:
    """Return proof keys only for fully validated reference-only image children.

    Callers must invoke this after ``validate_semantic_structure`` succeeds on
    the same decisions, packets, and assertions.  The returned keys are bound
    to the complete decision identity used by Stage06 conflict resolution.
    """
    trusted: set[tuple[int, str, int, str, str]] = set()
    for page, decision in decisions.items():
        structure = decision.get("semantic_structure")
        if not isinstance(structure, Mapping) or structure.get("profile") != PROFILE_V2:
            continue
        if decision.get("review", {}).get("visual_reviewed") is not True:
            continue
        packet = packets.get(page, {})
        views = packet.get("views", {}) if isinstance(packet, Mapping) else {}
        selected = {
            (row.get("view"), row.get("raw_index")): row
            for row in decision.get("selected_blocks", [])
            if isinstance(row, Mapping)
        }
        units = structure.get("units")
        if not isinstance(units, list):
            continue
        by_id = {unit.get("id"): unit for unit in units if isinstance(unit, Mapping)}
        for unit in units:
            if not isinstance(unit, Mapping) or unit.get("kind") != "statblock" or unit.get("source_fragments") != []:
                continue
            ids = unit.get("visual_assertion_ids")
            sources = unit.get("source_blocks")
            parent = by_id.get(unit.get("container_parent"))
            if not isinstance(ids, list) or not ids or len(sources or []) != 1 or not isinstance(parent, Mapping):
                continue
            if parent.get("kind") != "statblock" or parent.get("representation") not in {"semantic_span", "table"}:
                continue
            child_span = unit.get("markdown_span", {})
            parent_span = parent.get("markdown_span", {})
            if not (parent_span.get("start_line", 0) <= child_span.get("start_line", 0) <= child_span.get("end_line", 0) <= parent_span.get("end_line", 0)):
                continue
            source = sources[0]
            key = (source.get("view"), source.get("raw_index"))
            selected_row = selected.get(key)
            if not isinstance(selected_row, Mapping) or selected_row.get("purpose") != "asset":
                continue
            blocks = views.get(key[0], {}).get("blocks", []) if isinstance(views.get(key[0]), Mapping) else []
            packet_blocks = [block for block in blocks if isinstance(block, Mapping) and block.get("raw_index") == key[1]]
            assets = [asset for asset in decision.get("assets", []) if isinstance(asset, Mapping) and asset.get("view") == key[0] and asset.get("placement") == "reference_only" and len(packet_blocks) == 1 and asset.get("source_path") in packet_blocks[0].get("assets", [])]
            if len(packet_blocks) != 1 or len(assets) != 1:
                continue
            asset = assets[0]
            lines = str(decision.get("markdown", "")).split("\n")
            start, end = child_span.get("start_line"), child_span.get("end_line")
            if type(start) is not int or type(end) is not int or "{{asset:" + str(asset.get("logical_name")) + "}}" in "\n".join(lines[start - 1:end]):
                continue
            valid = True
            for assertion_id in ids:
                row = visual_assertions.get(assertion_id)
                placement = row.get("placement") if isinstance(row, Mapping) else None
                block = placement.get("asset_block") if isinstance(placement, Mapping) else None
                if not isinstance(row, Mapping) or row.get("source_page") != page or not isinstance(placement, Mapping) or placement.get("relation") != "within_selected_asset_region" or placement.get("logical_name") != asset.get("logical_name") or not isinstance(block, Mapping) or block.get("source_page") != page or block.get("view_id") != key[0] or block.get("raw_index") != key[1] or block.get("source_path") not in packet_blocks[0].get("assets", []):
                    valid = False
                    break
            if valid:
                trusted.add((page, key[0], key[1], str(asset.get("logical_name")), str(unit.get("id"))))
    return trusted


def collect_split_structure_proof_keys(
    decisions: Mapping[int, Mapping[str, Any]],
    packets: Mapping[int, Mapping[str, Any]],
) -> set[tuple[int, str, int]]:
    """Return keys for audited v2 structure selections split across units.

    Callers must invoke :func:`validate_semantic_structure` successfully on
    the same decisions and packets first. This helper reports only a shape
    Stage06 cannot infer from a legacy decision: every bound unit has an exact
    fragment, and the group contains both a heading and reader content.
    """
    trusted: set[tuple[int, str, int]] = set()
    for page, decision in decisions.items():
        structure = decision.get("semantic_structure")
        if (
            not isinstance(structure, Mapping)
            or structure.get("schema") != SCHEMA_V2
            or structure.get("profile") != PROFILE_V2
            or decision.get("review", {}).get("visual_reviewed") is not True
        ):
            continue
        packet = packets.get(page, {})
        views = packet.get("views", {}) if isinstance(packet, Mapping) else {}
        units = structure.get("units")
        if not isinstance(units, list):
            continue
        for selected in decision.get("selected_blocks", []):
            if not isinstance(selected, Mapping) or selected.get("purpose") != "structure":
                continue
            view, raw_index = selected.get("view"), selected.get("raw_index")
            if not isinstance(view, str) or type(raw_index) is not int:
                continue
            blocks = views.get(view, {}).get("blocks", []) if isinstance(views.get(view), Mapping) else []
            if len([block for block in blocks if isinstance(block, Mapping) and block.get("raw_index") == raw_index]) != 1:
                continue
            key = (view, raw_index)
            bound = [
                unit for unit in units
                if isinstance(unit, Mapping)
                and any(
                    isinstance(source, Mapping)
                    and (source.get("view"), source.get("raw_index")) == key
                    for source in unit.get("source_blocks", [])
                )
            ]
            if len(bound) < 2:
                continue
            if any(
                not isinstance(unit.get("source_fragments"), list)
                or not any(
                    isinstance(fragment, Mapping)
                    and (fragment.get("view"), fragment.get("raw_index")) == key
                    for fragment in unit["source_fragments"]
                )
                for unit in bound
            ):
                continue
            if not any(unit.get("representation") == "atx_heading" for unit in bound):
                continue
            if not any(unit.get("representation") in {"blockquote", "semantic_span", "table"} for unit in bound):
                continue
            trusted.add((page, view, raw_index))
    return trusted


def _validate_v2_role_contract(page: int, decision: Mapping[str, Any], units: list[dict[str, Any]]) -> None:
    contract = decision["semantic_structure"].get("role_contract")
    if not isinstance(contract, Mapping) or not isinstance(contract.get("role"), str):
        raise SemanticStructureError(f"role_contract_invalid: page {page}")
    if contract["role"] != decision.get("semantic_role") or not isinstance(contract.get("group_id"), str) or not contract["group_id"]:
        raise SemanticStructureError(f"role_contract_invalid: page {page}")
    by_id = {unit["id"]: unit for unit in units}
    role = contract["role"]
    if role == "character_statistics":
        if set(contract) != {"role", "group_id", "statblock_ids", "title_heading_ids"}:
            raise SemanticStructureError(f"role_contract_invalid: page {page}")
        stat_ids, title_ids = contract["statblock_ids"], contract["title_heading_ids"]
        if not isinstance(stat_ids, list) or not isinstance(title_ids, list) or not stat_ids or len(stat_ids) != len(title_ids) or len(set(stat_ids)) != len(stat_ids) or len(set(title_ids)) != len(title_ids):
            raise SemanticStructureError(f"statblock_title_contract_invalid: page {page}")
        top_level = {unit["id"] for unit in units if unit["kind"] == "statblock" and unit["container_parent"] is None}
        if set(stat_ids) != top_level:
            raise SemanticStructureError(f"statblock_title_coverage: page {page}")
        for stat_id, title_id in zip(stat_ids, title_ids):
            stat, title = by_id.get(stat_id), by_id.get(title_id)
            if not isinstance(stat, Mapping) or not isinstance(title, Mapping) or title.get("kind") != "heading" or title.get("container_parent") != stat_id or title.get("markdown_span", {}).get("start_line") != stat.get("markdown_span", {}).get("start_line"):
                raise SemanticStructureError(f"statblock_title_required: page {page}")
    elif role == "pregenerated_characters":
        legacy_keys = {"role", "group_id", "root_heading_id", "record_heading_id", "leaf_heading_ids"}
        plural_keys = {"role", "group_id", "root_heading_id", "record_heading_ids", "leaf_heading_ids"}
        keys = set(contract)
        if keys != legacy_keys and keys != plural_keys:
            raise SemanticStructureError(f"role_contract_invalid: page {page}")
        plural = keys == plural_keys
        record_ids = contract["record_heading_ids"] if plural else [contract["record_heading_id"]]
        leaves = contract["leaf_heading_ids"]
        root = contract["root_heading_id"]
        if (
            not isinstance(record_ids, list) or not record_ids
            or not all(isinstance(identity, str) for identity in record_ids)
            or len(set(record_ids)) != len(record_ids)
            or not isinstance(leaves, list)
            or not all(isinstance(identity, str) for identity in leaves)
            or len(set(leaves)) != len(leaves)
            or (not plural and not leaves)
        ):
            raise SemanticStructureError(f"pregenerated_outline_invalid: page {page}")
        records = [by_id.get(identity) for identity in record_ids]
        if any(
            not isinstance(record, Mapping)
            or record.get("kind") != "heading"
            or record.get("representation") != "atx_heading"
            or record.get("heading_level") != 2
            for record in records
        ):
            raise SemanticStructureError(f"pregenerated_outline_invalid: page {page}")
        if root is not None:
            root_unit = by_id.get(root)
            if not isinstance(root_unit, Mapping) or root_unit.get("kind") != "heading" or root_unit.get("heading_level") != 1 or (not plural and root_unit.get("markdown_span", {}).get("start_line") != 1):
                raise SemanticStructureError(f"pregenerated_root_invalid: page {page}")
        if not plural and root is None and records[0].get("markdown_span", {}).get("start_line") != 1:
            raise SemanticStructureError(f"pregenerated_record_order_invalid: page {page}")
        if root is not None and any(record.get("semantic_parent") != root for record in records):
            raise SemanticStructureError(f"pregenerated_parent_invalid: page {page}")
        if plural:
            parsed = []
            effective_markdown = apply_block_boundaries(
                str(decision.get("markdown", "")), decision.get("block_boundaries")
            )
            for line_number, line in enumerate(effective_markdown.split("\n"), 1):
                match = _ATX.match(line)
                if match is None:
                    continue
                matches = [
                    unit for unit in units
                    if unit.get("kind") == "heading"
                    and unit.get("representation") == "atx_heading"
                    and unit.get("markdown_span", {}).get("start_line") == line_number
                ]
                if len(matches) != 1:
                    raise SemanticStructureError(f"pregenerated_heading_coverage: page {page}")
                parsed.append((line_number, len(match.group(1)), matches[0]["id"]))
            if not parsed or (root is not None and parsed[0][2] != root) or (
                root is None and parsed[0][2] != record_ids[0]
            ):
                raise SemanticStructureError(f"pregenerated_first_heading_invalid: page {page}")
            if len(parsed) != len({identity for _, _, identity in parsed}):
                raise SemanticStructureError(f"pregenerated_heading_coverage: page {page}")
            parsed_h2 = [identity for _, level, identity in parsed if level == 2]
            parsed_h3 = [identity for _, level, identity in parsed if level == 3]
            if record_ids != parsed_h2:
                raise SemanticStructureError(f"pregenerated_record_coverage_or_order: page {page}")
            if leaves != parsed_h3:
                raise SemanticStructureError(f"pregenerated_leaf_coverage_or_order: page {page}")
            if root is not None and [identity for _, level, identity in parsed if level == 1] != [root]:
                raise SemanticStructureError(f"pregenerated_root_coverage: page {page}")
            if root is None and any(level == 1 for _, level, _ in parsed):
                raise SemanticStructureError(f"pregenerated_root_coverage: page {page}")
        for leaf_id in leaves:
            leaf = by_id.get(leaf_id)
            if not isinstance(leaf, Mapping) or leaf.get("kind") != "heading" or leaf.get("representation") != "atx_heading" or leaf.get("heading_level") != 3:
                raise SemanticStructureError(f"pregenerated_parent_invalid: page {page}")
            prior = [record for record in records if record["markdown_span"]["start_line"] < leaf["markdown_span"]["start_line"]]
            if not prior or leaf.get("semantic_parent") != prior[-1]["id"]:
                raise SemanticStructureError(f"pregenerated_parent_invalid: page {page}")
    else:
        if set(contract) != {"role", "group_id"}:
            raise SemanticStructureError(f"role_contract_invalid: page {page}")


def _packet_block_keys(packet: Mapping[str, Any]) -> set[tuple[str, int]]:
    result: set[tuple[str, int]] = set()
    for view, value in packet.get("views", {}).items():
        for block in value.get("blocks", []):
            if isinstance(block, dict) and type(block.get("raw_index")) is int:
                result.add((view, block["raw_index"]))
    return result


def _selected_keys(decision: Mapping[str, Any]) -> set[tuple[str, int]]:
    return {(row.get("view"), row.get("raw_index")) for row in decision.get("selected_blocks", []) if isinstance(row, dict)}


def selected_title_keys(
    decision: Mapping[str, Any], packet_blocks: Mapping[tuple[str, int], Mapping[str, Any]],
) -> set[tuple[str, int]]:
    """Return the closed, reader-text title domain for a V2 page.

    Stage05 and Stage06 must ask the same question.  Asset-only and structure
    selections deliberately do not enter this title domain.
    """
    selected = {
        (row.get("view"), row.get("raw_index"))
        for row in decision.get("selected_blocks", [])
        if isinstance(row, Mapping) and row.get("purpose") == "text"
    }
    return {
        key for key in selected
        if isinstance(packet_blocks.get(key, {}).get("semantic_evidence"), Mapping)
        and any(packet_blocks[key]["semantic_evidence"].get(name) for name in TITLE_EVIDENCE_KEYS)
    }


def validate_selected_title_coverage(
    page: int, decision: Mapping[str, Any], packet_blocks: Mapping[tuple[str, int], Mapping[str, Any]],
    units: list[dict[str, Any]], *, reviewed_prose_role_keys: set[tuple[str, int]] | None = None,
) -> None:
    """Require one source-bound V2 title disposition for every selected title.

    A title may be an outline heading, a source header label, or one of the
    established reviewed containers.  The fragment partition remains the
    source identity: text equality elsewhere on the page is never evidence.
    """
    selected_titles = selected_title_keys(decision, packet_blocks)
    allowed = {
        ("heading", "atx_heading"), ("label", "semantic_span"),
        ("callout", "blockquote"), ("blockquote", "blockquote"),
        ("handout", "blockquote"), ("statblock", "semantic_span"),
    }
    for key in sorted(selected_titles):
        if key in (reviewed_prose_role_keys or set()):
            if any(any(isinstance(source, Mapping) and (source.get("view"), source.get("raw_index")) == key
                       for source in unit.get("source_blocks", [])) for unit in units):
                raise SemanticStructureError(f"title_coverage_role_semantic_overlap: page {page}: {key[0]}:{key[1]}")
            continue
        source = packet_blocks[key].get("text")
        if not isinstance(source, str) or not source:
            raise SemanticStructureError(f"title_coverage_source_invalid: page {page}")
        matching = []
        for unit in units:
            if (unit.get("kind"), unit.get("representation")) not in allowed:
                continue
            fragments = [fragment for fragment in unit.get("source_fragments", [])
                         if isinstance(fragment, Mapping)
                         and (fragment.get("view"), fragment.get("raw_index")) == key]
            if fragments:
                matching.append((unit, fragments))
        if not matching:
            raise SemanticStructureError(f"title_coverage_missing: page {page}: {key[0]}:{key[1]}")
        fragments = [fragment for _, rows in matching for fragment in rows]
        fragments.sort(key=lambda row: (row["start"], row["end"]))
        if (
            fragments[0].get("start") != 0 or fragments[-1].get("end") != len(source)
            or any(left["end"] != right["start"] for left, right in zip(fragments, fragments[1:]))
        ):
            raise SemanticStructureError(f"title_coverage_fragment_partition: page {page}: {key[0]}:{key[1]}")


def _packet_blocks(packet: Mapping[str, Any]) -> dict[tuple[str, int], Mapping[str, Any]]:
    result: dict[tuple[str, int], Mapping[str, Any]] = {}
    for view, value in packet.get("views", {}).items():
        for block in value.get("blocks", []):
            if isinstance(block, dict) and type(block.get("raw_index")) is int:
                result[(view, block["raw_index"])] = block
    return result


def reviewed_text_corrections(
    decision: Mapping[str, Any], packet_blocks: Mapping[tuple[str, int], Mapping[str, Any]],
    selected: set[tuple[str, int]], markdown: str, page: int,
) -> list[tuple[str, str]]:
    """Return exact source-to-reader corrections authorized by visual review.

    Corrections live in the existing reviewer evidence notes so they cannot be
    introduced by an unreviewed materialization transform.  Each source form
    must occur exactly once in the selected page evidence and each replacement
    must already be visible in the reviewed Markdown.
    """
    review = decision.get("review")
    notes = review.get("notes", "") if isinstance(review, Mapping) else ""
    if not isinstance(notes, str):
        raise SemanticStructureError(f"page {page}: invalid review notes")
    corrections: list[tuple[str, str]] = []
    for line in notes.splitlines():
        if not line.startswith("text correction:"):
            continue
        match = _TEXT_CORRECTION.fullmatch(line.strip())
        if not match:
            raise SemanticStructureError(f"page {page}: malformed reviewed text correction")
        before, after, reason = match.group("before", "after", "reason")
        if before == after or not before.strip() or not after.strip() or not reason.strip():
            raise SemanticStructureError(f"page {page}: invalid reviewed text correction")
        if (before, after) in corrections:
            raise SemanticStructureError(f"page {page}: duplicate reviewed text correction")
        source_occurrences = sum(
            str(packet_blocks[key].get("text", "")).count(before)
            for key in selected if key in packet_blocks
        )
        if source_occurrences != 1:
            raise SemanticStructureError(
                f"page {page}: reviewed text correction source must occur exactly once in selected evidence"
            )
        if after not in markdown:
            raise SemanticStructureError(f"page {page}: reviewed text correction is absent from Markdown")
        corrections.append((before, after))
    return corrections


def reviewed_block_text_correction_candidates(
    decision: Mapping[str, Any], packet_blocks: Mapping[tuple[str, int], Mapping[str, Any]],
    selected: set[tuple[str, int]], page: int,
) -> dict[tuple[str, int], list[tuple[str, str]]]:
    """Return source-authorized corrections without reader-acceptance claims.

    Staged authoring may need these exact source candidates before it can build
    final Markdown spans.  This function checks only immutable source evidence;
    :func:`reviewed_block_text_corrections` remains the required visible-proof
    gate for completed decisions.
    """
    rows = decision.get("reviewed_block_corrections", [])
    if rows is None:
        return {}
    if not isinstance(rows, list):
        raise SemanticStructureError(f"page {page}: reviewed block corrections must be a list")
    result: dict[tuple[str, int], list[tuple[str, str]]] = {}
    intervals: dict[tuple[str, int], list[tuple[int, int]]] = {}
    text_selected = {
        (row.get("view"), row.get("raw_index"))
        for row in decision.get("selected_blocks", [])
        if isinstance(row, Mapping) and row.get("purpose") != "asset"
    }
    expected = {"view", "raw_index", "before", "after", "reason", "original_text_sha256"}
    for row in rows:
        if not isinstance(row, Mapping) or set(row) != expected:
            raise SemanticStructureError(f"page {page}: invalid reviewed block correction")
        view, raw_index = row["view"], row["raw_index"]
        key = (view, raw_index)
        if not isinstance(view, str) or type(raw_index) is not int or key not in selected or key not in text_selected:
            raise SemanticStructureError(f"page {page}: reviewed block correction is not selected")
        block = packet_blocks.get(key)
        text = block.get("text") if isinstance(block, Mapping) else None
        before, after, reason = row["before"], row["after"], row["reason"]
        if (
            not isinstance(text, str) or not text
            or not isinstance(before, str) or not before
            or not isinstance(after, str) or not after
            or before == after or not isinstance(reason, str) or not reason.strip()
            or row["original_text_sha256"] != hashlib.sha256(text.encode("utf-8")).hexdigest().upper()
        ):
            raise SemanticStructureError(f"page {page}: invalid reviewed block correction evidence")
        if text.count(before) != 1:
            raise SemanticStructureError(f"page {page}: reviewed block correction source must occur exactly once in its named block")
        start = text.index(before); interval = (start, start + len(before))
        if any(not (interval[1] <= other[0] or other[1] <= interval[0]) for other in intervals.setdefault(key, [])):
            raise SemanticStructureError(f"page {page}: overlapping or duplicate reviewed block correction")
        intervals[key].append(interval)
        result.setdefault(key, []).append((before, after))
    # Linguistic choices use a distinct sealed-ledger adapter.  They are never
    # interpreted as visual-review notes or legacy reviewed corrections.
    try:
        from kb_creator.pipeline.source_choice_successor import linguistic_choice_corrections
        overrides: set[tuple[str, int]] = set()
        linguistic = linguistic_choice_corrections(decision, packet_blocks, selected, page,
                                                  full_source_overrides=overrides)
    except ValueError as error:
        raise SemanticStructureError(str(error)) from error
    for key, corrections in linguistic.items():
        if key in overrides:
            if len(corrections) != 1 or corrections[0][0] != packet_blocks[key].get("text"):
                raise SemanticStructureError(f"page {page}: whole-source override is ambiguous")
            result[key] = []
            intervals[key] = []
        occupied = intervals.setdefault(key, [])
        text = packet_blocks[key].get("text")
        for before, after in corrections:
            if not isinstance(text, str) or text.count(before) != 1:
                raise SemanticStructureError(f"page {page}: linguistic source choice is not exact")
            interval = (text.index(before), text.index(before) + len(before))
            if any(not (interval[1] <= other[0] or other[1] <= interval[0]) for other in occupied):
                raise SemanticStructureError(f"page {page}: overlapping linguistic source choice")
            occupied.append(interval)
            result.setdefault(key, []).append((before, after))
    return result


def reviewed_block_text_corrections(
    decision: Mapping[str, Any], packet_blocks: Mapping[tuple[str, int], Mapping[str, Any]],
    selected: set[tuple[str, int]], markdown: str, page: int,
    *, semantic_units: list[Mapping[str, Any]] | None = None,
) -> dict[tuple[str, int], list[tuple[str, str]]]:
    """Return source-authorized corrections proved in bound visible spans."""
    if semantic_units is None:
        structure = decision.get("semantic_structure")
        candidate_units = structure.get("units") if isinstance(structure, Mapping) else None
        if isinstance(candidate_units, list):
            semantic_units = candidate_units
    candidates = reviewed_block_text_correction_candidates(
        decision, packet_blocks, selected, page,
    )
    # A changed ledger-bound source choice is revalidated by its own exact
    # anchor, chosen raw locator, preimage and successor checks.  It carries no
    # visual acceptance claim, so exclude only those pairs from the separate
    # visual-review span proof; retain them below for source-fragment replay.
    from kb_creator.pipeline.source_choice_successor import linguistic_choice_corrections
    linguistic = linguistic_choice_corrections(decision, packet_blocks, selected, page)
    visual_candidates = {
        key: [pair for pair in rows if pair not in linguistic.get(key, [])]
        for key, rows in candidates.items()
    }
    visual_candidates = {key: rows for key, rows in visual_candidates.items() if rows}
    if visual_candidates and semantic_units is None and "reviewed_prose_bindings_v1" not in decision:
        raise SemanticStructureError(
            f"page {page}: reviewed block correction requires a semantic unit binding"
        )
    # Ordinary prose is deliberately not a semantic presentation kind.  When
    # explicitly present, the closed paragraph contract owns its selected keys;
    # all remaining corrections retain the legacy semantic-unit proof route.
    prose_keys = verified_reviewed_prose_binding_keys(
        decision, packet_blocks, selected, markdown, page,
        semantic_units=semantic_units, correction_candidates=candidates,
    )
    if visual_candidates and semantic_units is None and set(visual_candidates) - prose_keys:
        raise SemanticStructureError(
            f"page {page}: reviewed block correction requires a semantic unit binding"
        )
    for key, corrections in visual_candidates.items():
        if key in prose_keys:
            continue
        block = packet_blocks[key]
        text = block.get("text")
        if not isinstance(text, str):  # source validator already enforces this
            raise SemanticStructureError(f"page {page}: invalid reviewed block correction evidence")
        for before, after in corrections:
            start = text.index(before)
            _verify_projected_block_correction(
                page, markdown, key, after, semantic_units,
                source_text=text, source_interval=(start, start + len(before)),
                source_before=before, packet_blocks=packet_blocks,
            )
    return candidates


def verified_reviewed_prose_binding_keys(
    decision: Mapping[str, Any], packet_blocks: Mapping[tuple[str, int], Mapping[str, Any]],
    selected: set[tuple[str, int]], markdown: str, page: int,
    *, semantic_units: list[Mapping[str, Any]] | None,
    correction_candidates: Mapping[tuple[str, int], list[tuple[str, str]]] | None = None,
) -> set[tuple[str, int]]:
    """Return only paragraph keys proven by the closed prose verifier."""
    if "reviewed_prose_bindings_v1" not in decision:
        return set()
    from kb_creator.pipeline.reviewed_prose_binding import (
        ReviewedProseBindingError, verify_reviewed_prose_bindings,
    )
    try:
        return set(verify_reviewed_prose_bindings(
            decision, packet_blocks, selected, markdown, page,
            semantic_units=semantic_units, correction_candidates=correction_candidates,
        ))
    except ReviewedProseBindingError as exc:
        raise SemanticStructureError(str(exc)) from exc


def verified_reviewed_prose_role_keys(
    decision: Mapping[str, Any], packet_blocks: Mapping[tuple[str, int], Mapping[str, Any]],
    selected: set[tuple[str, int]], markdown: str, page: int, *, semantic_units: list[Mapping[str, Any]] | None,
    visual_inventory: Mapping[str, Mapping[str, Any]],
) -> tuple[set[tuple[str, int]], dict[tuple[str, int], dict[str, Any]]]:
    if "reviewed_prose_roles_v1" not in decision:
        return set(), {}
    from kb_creator.pipeline.reviewed_prose_binding import ReviewedProseBindingError, verify_reviewed_prose_roles
    try:
        proofs = verify_reviewed_prose_roles(decision, packet_blocks, selected, markdown, page,
                                             semantic_units=semantic_units, visual_inventory=visual_inventory)
        return set(proofs), proofs
    except ReviewedProseBindingError as exc:
        raise SemanticStructureError(str(exc)) from exc


def _verify_projected_block_correction(
    page: int, markdown: str, key: tuple[str, int], corrected_text: str,
    semantic_units: list[Mapping[str, Any]], *, source_text: str | None = None,
    source_interval: tuple[int, int] | None = None, source_before: str | None = None,
    packet_blocks: Mapping[tuple[str, int], Mapping[str, Any]] | None = None,
) -> None:
    """Bind a nonliteral correction to one sealed reader-visible unit span."""
    matches = []
    for unit in semantic_units:
        if not isinstance(unit, Mapping):
            continue
        sources = unit.get("source_blocks")
        if isinstance(sources, list) and any(
            isinstance(source, Mapping)
            and source.get("view") == key[0]
            and source.get("raw_index") == key[1]
            for source in sources
        ):
            matches.append(unit)
    if len(matches) > 1 and source_text is not None and source_interval is not None:
        interval_matches = []
        for unit in matches:
            fragments = unit.get("source_fragments")
            if not isinstance(fragments, list):
                continue
            contains_interval = False
            for fragment in fragments:
                if not isinstance(fragment, Mapping):
                    continue
                if (fragment.get("view"), fragment.get("raw_index")) != key:
                    continue
                _fragment_text({"text": source_text}, fragment, page)
                if fragment["start"] <= source_interval[0] and source_interval[1] <= fragment["end"]:
                    contains_interval = True
                    break
            if contains_interval:
                interval_matches.append(unit)
        matches = interval_matches
    if len(matches) != 1:
        raise SemanticStructureError(
            f"page {page}: reviewed block correction must bind exactly one semantic unit"
        )
    span = matches[0].get("markdown_span")
    lines = markdown.split("\n")
    if (
        not isinstance(span, Mapping)
        or set(span) != {"start_line", "end_line", "sha256"}
        or type(span.get("start_line")) is not int
        or type(span.get("end_line")) is not int
        or not 1 <= span["start_line"] <= span["end_line"] <= len(lines)
        or span.get("sha256") != _span_hash(lines, span["start_line"], span["end_line"])
    ):
        raise SemanticStructureError(f"page {page}: correction unit has invalid markdown span")

    unit = matches[0]
    if unit.get("kind") == "line_group" and unit.get("representation") == "hard_break_lines":
        if (
            source_text is None or source_interval is None or source_before is None
            or packet_blocks is None
        ):
            raise SemanticStructureError(
                f"page {page}: line-group correction requires source interval evidence"
            )
        _verify_line_group_correction_line(
            page, markdown, unit, key, source_text, source_interval, source_before,
            corrected_text, packet_blocks,
        )
        return

    direct_error: VisibleCorrectionError
    try:
        verify_visible_correction(markdown, corrected_text, span)
        return
    except VisibleCorrectionError as exc:
        direct_error = exc

    # The author materializer may expand a punctuation correction to a complete
    # OCR list item.  A source bullet glyph is structural evidence, whereas the
    # reader-visible span projects its Markdown list marker away.  Treat that
    # one marker as equivalent only after the immutable source key has resolved
    # to this sealed unordered-list unit; all following content stays exact.
    source_marker = _SOURCE_UNORDERED_LIST_MARKER.match(corrected_text)
    if (
        unit.get("kind") == "list"
        and unit.get("representation") == "unordered_list"
        and source_marker is not None
    ):
        try:
            verify_visible_correction(markdown, corrected_text[source_marker.end():], span)
            return
        except VisibleCorrectionError as exc:
            direct_error = exc
    raise SemanticStructureError(
        f"page {page}: reviewed block correction is absent from its bound visible span"
    ) from direct_error


def _verify_line_group_correction_line(
    page: int, markdown: str, unit: Mapping[str, Any], key: tuple[str, int],
    source_text: str, source_interval: tuple[int, int], source_before: str,
    corrected_text: str, packet_blocks: Mapping[tuple[str, int], Mapping[str, Any]],
) -> None:
    """Prove a line-group correction at its sealed physical reader line.

    A refrain can legitimately repeat inside a hard-break group.  Its source
    interval therefore selects the physical source line, whose ordinal selects
    one physical reader line.  This does not relax the ordinary unit-wide
    ambiguity rule used by prose and other semantic representations.
    """
    fragments = unit.get("source_fragments")
    source_blocks = unit.get("source_blocks")
    if not isinstance(fragments, list) or not fragments or not isinstance(source_blocks, list):
        raise SemanticStructureError(f"page {page}: line-group correction lacks sealed source fragments")
    source_keys: list[tuple[str, int]] = []
    for source in source_blocks:
        if not isinstance(source, Mapping):
            raise SemanticStructureError(f"page {page}: line-group correction has invalid source block")
        source_key = (source.get("view"), source.get("raw_index"))
        if not isinstance(source_key[0], str) or type(source_key[1]) is not int or source_key in source_keys:
            raise SemanticStructureError(f"page {page}: line-group correction has invalid source block")
        source_keys.append(source_key)
    source_rank = {source_key: index for index, source_key in enumerate(source_keys)}
    prior_rank = -1
    prior_end: dict[tuple[str, int], int] = {}
    physical_lines: list[tuple[tuple[str, int], int, int, str]] = []
    for fragment in fragments:
        if not isinstance(fragment, Mapping):
            raise SemanticStructureError(f"page {page}: line-group correction has invalid source fragment")
        fragment_key = (fragment.get("view"), fragment.get("raw_index"))
        if fragment_key not in source_rank or fragment_key not in packet_blocks:
            raise SemanticStructureError(f"page {page}: line-group correction fragment is unbound")
        fragment_source = packet_blocks[fragment_key].get("text")
        if not isinstance(fragment_source, str):
            raise SemanticStructureError(f"page {page}: line-group correction source block has no text")
        value = _fragment_text(packet_blocks[fragment_key], fragment, page)
        start, end = fragment["start"], fragment["end"]
        rank = source_rank[fragment_key]
        if rank < prior_rank or start < prior_end.get(fragment_key, -1):
            raise SemanticStructureError(f"page {page}: line-group correction fragment order mismatch")
        if (start > 0 and fragment_source[start - 1] != "\n") or (
            end < len(fragment_source) and fragment_source[end - 1] != "\n"
        ):
            raise SemanticStructureError(f"page {page}: line-group correction fragment cuts a physical line")
        prior_rank = rank
        prior_end[fragment_key] = end
        cursor = start
        for raw_line in value.splitlines(keepends=True):
            line_end = cursor + len(raw_line.rstrip("\r\n"))
            physical_lines.append((fragment_key, cursor, line_end, raw_line.rstrip("\r\n")))
            cursor += len(raw_line)
    matches = [
        (index, line) for index, line in enumerate(physical_lines)
        if line[0] == key and line[1] <= source_interval[0] and source_interval[1] <= line[2]
    ]
    if len(matches) != 1:
        raise SemanticStructureError(f"page {page}: line-group correction interval has no unique physical line")
    line_index, (_, line_start, _, source_line) = matches[0]
    relative_start = source_interval[0] - line_start
    if source_line[relative_start:relative_start + len(source_before)] != source_before:
        raise SemanticStructureError(f"page {page}: line-group correction interval is stale")
    span = unit["markdown_span"]
    target_line = span["start_line"] + line_index
    lines = markdown.split("\n")
    if target_line > span["end_line"] or target_line > len(lines):
        raise SemanticStructureError(f"page {page}: line-group correction reader line is unbound")
    target_span = {
        "start_line": target_line,
        "end_line": target_line,
        "sha256": _span_hash(lines, target_line, target_line),
    }
    try:
        verify_visible_correction(markdown, corrected_text, target_span)
    except VisibleCorrectionError as exc:
        raise SemanticStructureError(
            f"page {page}: reviewed line-group correction is absent from its bound visible line"
        ) from exc


def apply_reviewed_text_corrections(
    text: str, key: tuple[str, int], corrections: list[tuple[str, str]],
    block_corrections: Mapping[tuple[str, int], list[tuple[str, str]]],
) -> str:
    """Apply legacy page-wide corrections and then only this block's corrections."""
    for before, after in corrections:
        text = text.replace(before, after)
    for before, after in block_corrections.get(key, []):
        text = text.replace(before, after)
    return text


def _atx_heading_occurrences(markdown: str, text: str) -> int:
    """Count exact reader headings, including headings nested in a quote."""
    pattern = re.compile(
        rf"(?m)^(?:> )?#{{1,6}}[ \t]+{re.escape(text)}[ \t]*#*[ \t]*$"
    )
    return len(pattern.findall(markdown))


def reviewed_title_evidence_confirmations(
    decision: Mapping[str, Any], packet_blocks: Mapping[tuple[str, int], Mapping[str, Any]],
    markdown: str, page: int, *, semantic_units: list[Mapping[str, Any]] | None = None,
) -> dict[tuple[str, int], str]:
    """Validate explicit resolutions for title-view disagreement.

    A selected structural block can be a heading in the selected/Markdown
    views while its middle view says it is not.  This is visual-review work,
    never an invitation to infer a word split.  A reviewer must bind the
    exact source key to the exact reader heading in the notes ledger.
    """
    selected = _selected_keys(decision)
    candidates = {
        key: block for key, block in packet_blocks.items()
        if key in selected
        and next((row.get("purpose") for row in decision.get("selected_blocks", [])
                  if isinstance(row, Mapping) and (row.get("view"), row.get("raw_index")) == key), None) == "structure"
        and isinstance(block.get("semantic_evidence"), Mapping)
        and block["semantic_evidence"].get("v2_title") is True
        and block["semantic_evidence"].get("markdown_heading") is True
        and block["semantic_evidence"].get("middle_title") is False
    }
    review = decision.get("review")
    notes = review.get("notes", "") if isinstance(review, Mapping) else ""
    if not isinstance(notes, str):
        raise SemanticStructureError(f"title_evidence_confirmation_invalid: page {page}: invalid review notes")
    confirmations: dict[tuple[str, int], str] = {}
    for raw_line in notes.splitlines():
        line = raw_line.strip()
        if not line.startswith("title evidence confirmation:"):
            continue
        match = _TITLE_EVIDENCE_CONFIRMATION.fullmatch(line)
        if not match:
            raise SemanticStructureError(f"title_evidence_confirmation_invalid: page {page}: malformed title evidence confirmation")
        key = (match.group("view"), int(match.group("raw_index")))
        reader, reason = match.group("reader"), match.group("reason")
        if not reader.strip() or not reason.strip() or key in confirmations:
            raise SemanticStructureError(f"title_evidence_confirmation_invalid: page {page}: invalid or duplicate title evidence confirmation")
        if key not in candidates:
            raise SemanticStructureError(f"title_evidence_confirmation_stale: page {page}: confirmation does not bind a current title conflict")
        if _atx_heading_occurrences(markdown, reader) != 1:
            raise SemanticStructureError(f"title_reader_heading_mismatch: page {page}: reader heading must occur exactly once")
        confirmations[key] = reader
    if candidates and (not isinstance(review, Mapping) or review.get("visual_reviewed") is not True):
        raise SemanticStructureError(f"title_evidence_confirmation_invalid: page {page}: title conflict requires visual review")
    missing = set(candidates) - set(confirmations)
    if missing:
        raise SemanticStructureError(f"title_evidence_confirmation_required: page {page}: missing title evidence confirmation")
    corrections = reviewed_text_corrections(decision, packet_blocks, selected, markdown, page)
    block_corrections = reviewed_block_text_corrections(
        decision, packet_blocks, selected, markdown, page, semantic_units=semantic_units,
    )
    for key, reader in confirmations.items():
        source = candidates[key].get("text")
        if not isinstance(source, str) or not source.strip():
            raise SemanticStructureError(f"title_evidence_confirmation_invalid: page {page}: title source text is invalid")
        corrected = apply_reviewed_text_corrections(
            source, key, corrections, block_corrections,
        )
        if corrected != reader:
            raise SemanticStructureError(f"title_text_correction_required: page {page}: changed title requires reviewed text correction")
    return confirmations


def validate_canonical_blank_separators(markdown: str, page: int) -> int:
    """Reject undeclared multi-blank root-level separators in reviewed Markdown."""
    lines = markdown.split("\n")
    runs: list[tuple[int, int]] = []
    index = 0
    while index < len(lines):
        if lines[index] != "":
            index += 1
            continue
        start = index
        while index < len(lines) and lines[index] == "":
            index += 1
        length = index - start
        if start > 0 and index < len(lines) and length > 1:
            runs.append((start + 1, length))
    if runs:
        start, length = runs[0]
        raise SemanticStructureError(
            f"redundant_root_blank_separator: page {page}: start line {start}, run length {length}"
        )
    return 0


def _syntax_errors(unit: Mapping[str, Any], lines: list[str], start: int, end: int) -> list[str]:
    kind, representation = unit["kind"], unit["representation"]
    body = lines[start - 1:end]
    # A list nested in a reviewed blockquote retains the quote marker on every
    # physical Markdown line; validate its list syntax after that container
    # prefix is removed.
    list_body = [line[2:] if line.startswith("> ") else ("" if line == ">" else line) for line in body]
    errors: list[str] = []
    if representation == "blockquote" and any(not line.startswith(">") for line in body):
        errors.append("blockquote span has an unquoted line")
    if representation == "semantic_span":
        if kind not in {"statblock", "label", "paragraph"}:
            errors.append("semantic span is reserved for statblocks, labels, and paragraphs")
        elif kind == "label":
            if len(body) != 1 or not body[0].strip():
                errors.append("semantic label span must contain exactly one nonblank line")
            elif re.match(r"^\s*(?:#{1,6}\s|[-*+]\s|>\s|\d+[.)]\s)", body[0]):
                errors.append("semantic label span cannot use heading, list, or quote syntax")
        elif kind == "paragraph":
            if len(body) != 1 or not body[0].strip():
                errors.append("semantic paragraph span must contain exactly one nonblank line")
            elif (
                re.match(r"^\s*(?:#{1,6}\s|[-*+]\s|>\s|\d+[.)]\s|`{3,}|<[/!A-Za-z])", body[0])
                or "|" in body[0]
                or "`" in body[0]
            ):
                errors.append("semantic paragraph span must be plain Markdown prose")
        elif not body or not body[0].strip() or not body[-1].strip():
            errors.append("semantic statblock span must have nonblank boundaries")
        elif any(line.lstrip().startswith(">") for line in body):
            errors.append("semantic statblock span contains quote syntax")
    if representation == "unordered_list":
        count = sum(bool(_UL.match(line)) for line in list_body)
        if count != unit["item_count"] or any(line and not _UL.match(line) and not line.startswith("  ") for line in list_body):
            errors.append("unordered list syntax or item_count mismatch")
    if representation == "ordered_list":
        count = sum(bool(_OL.match(line)) for line in list_body)
        if count != unit["item_count"] or any(line and not _OL.match(line) and not line.startswith("   ") for line in list_body):
            errors.append("ordered list syntax or item_count mismatch")
    if representation == "table":
        if len(body) < 2 or "|" not in body[0] or not re.fullmatch(r"[| :\-]+", body[1]):
            errors.append("table span lacks Markdown header/delimiter pair")
    if representation == "atx_heading":
        # A heading may be the first semantic child of a reviewed blockquote,
        # where CommonMark prefixes the ATX marker with `> `.
        heading_body = [line[2:] if line.startswith("> ") else line for line in body]
        headings = [line for line in heading_body if _ATX.match(line)]
        if len(headings) != 1 or len(_ATX.match(headings[0]).group(1)) != unit["heading_level"]:
            errors.append("ATX heading level mismatch")
    if representation == "hard_break_lines":
        if len(body) < 2 or any(not line.strip() for line in body):
            errors.append("hard-break line group must contain at least two nonblank lines")
        elif any(not re.search(r" {2,}$", line) for line in body[:-1]):
            errors.append("hard-break line group is missing a Markdown hard break")
        elif re.search(r" {2,}$", body[-1]):
            errors.append("hard-break line group final line must not carry a hard break")
    return errors


def validate_semantic_structure(
    decisions: Mapping[int, Mapping[str, Any]], packets: Mapping[int, Mapping[str, Any]],
    visual_inventory: Mapping[str, Mapping[str, Any]], *, required_pages: list[int] | None = None,
    visual_assertions: Mapping[str, Mapping[str, Any]] | None = None,
) -> dict[str, Any]:
    """Return a deterministic report or raise on an invalid reviewed contract."""
    pages = required_pages or sorted(decisions)
    profiles = {_profile(decisions[page], page) for page in pages}
    if len(profiles) != 1:
        raise SemanticStructureError("semantic_profile_mismatch")
    profile = profiles.pop()
    reports: list[dict[str, Any]] = []; ids: dict[str, tuple[int, dict[str, Any]]] = {}
    previous_end: dict[int, list[tuple[int, int, str]]] = {}
    for page in pages:
        decision = decisions.get(page); packet = packets.get(page)
        if not isinstance(decision, Mapping) or not isinstance(packet, Mapping):
            raise SemanticStructureError(f"page {page}: missing decision or packet")
        structure = decision.get("semantic_structure")
        if not isinstance(structure, dict):
            raise SemanticStructureError(f"page {page}: missing or invalid semantic_structure")
        review = structure["review"]
        if not isinstance(review, dict) or set(review) != {"state", "visual"} or review["state"] != "complete":
            raise SemanticStructureError(f"page {page}: semantic review is not complete")
        visual = review["visual"]
        if not isinstance(visual, dict) or set(visual) != {"path", "bytes", "sha256"} or visual.get("bytes", 0) <= 0 or visual_inventory.get(visual["path"]) != {"bytes": visual["bytes"], "sha256": visual["sha256"]}:
            raise SemanticStructureError(f"page {page}: reviewed visual identity mismatch")
        if f"page-{page:03d}" not in str(visual["path"]):
            raise SemanticStructureError(f"page {page}: reviewed visual is for another page")
        units = structure["units"]
        if not isinstance(units, list):
            raise SemanticStructureError(f"page {page}: units must be a list")
        markdown = apply_block_boundaries(str(decision.get("markdown", "")), decision.get("block_boundaries"))
        lines = markdown.split("\n")
        spans: list[tuple[int, int, str]] = []; rows = []; last_start = 0; role_proofs: dict[tuple[str, int], dict[str, Any]] = {}
        packet_blocks, packets_keys, selected = _packet_blocks(packet), _packet_block_keys(packet), _selected_keys(decision)
        selected_purposes = {(row.get("view"), row.get("raw_index")): row.get("purpose") for row in decision.get("selected_blocks", []) if isinstance(row, Mapping)}
        text_corrections = reviewed_text_corrections(decision, packet_blocks, selected, markdown, page)
        block_corrections = reviewed_block_text_corrections(
            decision, packet_blocks, selected, markdown, page, semantic_units=units,
        )
        verified_prose_keys = verified_reviewed_prose_binding_keys(
            decision, packet_blocks, selected, markdown, page,
            semantic_units=units, correction_candidates=block_corrections,
        )
        title_confirmations = reviewed_title_evidence_confirmations(
            decision, packet_blocks, markdown, page, semantic_units=units,
        )
        redundant_blank_runs = validate_canonical_blank_separators(markdown, page)
        bound_block_correction_keys = set(verified_prose_keys)
        for unit in units:
            expected = {"id", "kind", "representation", "source_blocks", "markdown_span", "container_parent", "semantic_parent", "continuation_of", "heading_level", "item_count"}
            if profile == PROFILE_V2:
                expected |= {"source_fragments"}
                if "visual_assertion_ids" in unit:
                    expected |= {"visual_assertion_ids"}
            if not isinstance(unit, dict) or set(unit) != expected or not isinstance(unit["id"], str) or not _ID.fullmatch(unit["id"]):
                raise SemanticStructureError(f"page {page}: invalid semantic unit")
            representations = V2_KIND_REPRESENTATIONS if profile == PROFILE_V2 else KIND_REPRESENTATIONS
            if unit["id"] in ids or unit["kind"] not in representations or unit["representation"] not in representations[unit["kind"]]:
                raise SemanticStructureError(f"page {page}: duplicate id or invalid kind/representation")
            span = unit["markdown_span"]
            if not isinstance(span, dict) or set(span) != {"start_line", "end_line", "sha256"} or type(span["start_line"]) is not int or type(span["end_line"]) is not int or not 1 <= span["start_line"] <= span["end_line"] <= len(lines) or span["sha256"] != _span_hash(lines, span["start_line"], span["end_line"]):
                raise SemanticStructureError(f"page {page}: invalid semantic markdown span")
            if unit["kind"] == "heading":
                if type(unit["heading_level"]) is not int or not 1 <= unit["heading_level"] <= 6:
                    raise SemanticStructureError(f"page {page}: invalid heading level")
            elif unit["heading_level"] is not None:
                raise SemanticStructureError(f"page {page}: non-heading has heading_level")
            if unit["kind"] == "list":
                if type(unit["item_count"]) is not int or unit["item_count"] < 1:
                    raise SemanticStructureError(f"page {page}: invalid list item_count")
            elif unit["item_count"] is not None:
                raise SemanticStructureError(f"page {page}: non-list has item_count")
            source_blocks = unit["source_blocks"]
            source_less_positional = (
                profile == PROFILE_V2 and unit["kind"] == "heading"
                and unit["representation"] == "atx_heading" and source_blocks == []
                and unit.get("source_fragments") == [] and isinstance(unit.get("visual_assertion_ids"), list)
                and len(unit["visual_assertion_ids"]) == 1
            )
            if not isinstance(source_blocks, list) or (not source_blocks and not source_less_positional):
                raise SemanticStructureError(f"page {page}: source_blocks required")
            if source_less_positional:
                assertion_id = unit["visual_assertion_ids"][0]
                assertion = visual_assertions.get(assertion_id) if visual_assertions is not None else None
                relation = assertion.get("placement", {}).get("relation") if isinstance(assertion, Mapping) else None
                if relation not in {"before_anchor", "after_anchor", "column_before_anchor", "column_after_anchor"}:
                    raise SemanticStructureError(f"source_less_positional_heading_wrong_proof: page {page}")
            source_keys = []
            for source in source_blocks:
                if not isinstance(source, dict) or set(source) != {"view", "raw_index"} or type(source["raw_index"]) is not int:
                    raise SemanticStructureError(f"page {page}: invalid source block")
                key = (source["view"], source["raw_index"])
                if key not in packets_keys or key not in selected or key in source_keys:
                    raise SemanticStructureError(f"page {page}: source block absent or unselected")
                source_keys.append(key)
            if profile == PROFILE_V2 and unit.get("source_fragments") == [] and any(selected_purposes.get(key) != "asset" for key in source_keys):
                from .empty_text_assertions import RELATION as EMPTY_TEXT_RELATION, validate as validate_empty_assertion
                assertion_ids = unit.get("visual_assertion_ids", [])
                assertion = visual_assertions.get(assertion_ids[0]) if visual_assertions is not None and len(assertion_ids) == 1 else None
                if not isinstance(assertion, Mapping) or assertion.get("placement", {}).get("relation") != EMPTY_TEXT_RELATION:
                    raise SemanticStructureError(f"empty source_fragments require selected asset or empty-text proof: page {page}")
                from kb_creator.scripts.audit_mineru_ai_merge_fidelity import ASSET, IMAGE
                try:
                    validate_empty_assertion(assertion, packet, decision, _normalized(ASSET.sub("", IMAGE.sub("", markdown))))
                except ValueError as exc:
                    raise SemanticStructureError(f"invalid empty-text semantic proof: page {page}: {exc}") from exc
            # An image-backed source block has exactly two closed choices: it
            # is reader-visible through its declared inline asset placeholder,
            # or its raster is retained as evidence only while a reviewed
            # semantic representation (for example a statblock table) carries
            # the reader text.  The latter must be explicit `reference_only`.
            span_text = "\n".join(lines[span["start_line"] - 1:span["end_line"]])
            span_normalized = _normalized(span_text); text_cursor = 0
            line_group_source = (
                _v2_line_group_source_lines(
                    page, unit, source_keys, packet_blocks, text_corrections, block_corrections,
                )
                if profile == PROFILE_V2 and unit["kind"] == "line_group" else []
            )
            for key in source_keys:
                # reviewed_block_text_corrections has already proved every
                # correction against its unique bound visible span.  Repeating
                # a raw-Markdown containment shortcut here could reintroduce
                # hidden syntax as evidence, so this unit loop only records
                # the bound source key.
                if key in block_corrections:
                    bound_block_correction_keys.add(key)
                block_text = packet_blocks[key].get("text")
                if profile == PROFILE_V2 and any(
                    fragment.get("view") == key[0] and fragment.get("raw_index") == key[1]
                    for fragment in unit["source_fragments"] if isinstance(fragment, Mapping)
                ):
                    # v2 validates this source through its exact partition below;
                    # requiring the whole mixed block in each child span would
                    # forbid the reviewed split it is designed to represent.
                    continue
                if isinstance(block_text, str):
                    block_text = apply_reviewed_text_corrections(
                        block_text, key, text_corrections, block_corrections,
                    )
                if profile != PROFILE_V2 and unit["kind"] == "line_group":
                    if not isinstance(block_text, str) or not block_text:
                        raise SemanticStructureError(f"page {page}: line-group source block has no text")
                    source_lines = [
                        _INLINE_TAG.sub("", line).rstrip(" \t")
                        for line in block_text.splitlines()
                    ]
                    if not source_lines or any(not line.strip() for line in source_lines):
                        raise SemanticStructureError(f"page {page}: line-group source contains an empty line")
                    line_group_source.extend(source_lines)
                normalized_block = _normalized(block_text) if isinstance(block_text, str) else ""
                asset_text_proof = False
                if profile == PROFILE_V2 and unit.get("source_fragments") == []:
                    asset_text_proof = any(
                        isinstance(asset, Mapping)
                        and asset.get("view") == key[0]
                        and asset.get("source_path") in packet_blocks[key].get("assets", [])
                        and (
                            asset.get("placement") != "reference_only"
                            or (
                                unit.get("kind") == "statblock"
                                and unit.get("source_fragments") == []
                                and isinstance(unit.get("visual_assertion_ids"), list)
                                and bool(unit.get("visual_assertion_ids"))
                            )
                        )
                        and _v2_unit_binds_selected_asset(
                            page, unit, key, asset.get("logical_name"), visual_assertions,
                        )
                        for asset in decision.get("assets", [])
                    )
                # Asset-only source evidence may legitimately be retained as
                # reference_only while semantic Markdown replaces the raster.
                if not normalized_block:
                    continue
                if asset_text_proof:
                    continue
                occurrence = span_normalized.find(normalized_block, text_cursor)
                if occurrence < 0:
                    raise SemanticStructureError(f"page {page}: text source is absent from declared span")
                # Source blocks are an ordered reviewed sequence. Repeated
                # words or prefix forms in later blocks (for example `Dad`
                # followed by `Daddy`) are valid; the monotonic cursor, not
                # global substring uniqueness, binds each occurrence.
                text_cursor = occurrence + len(normalized_block)
            if unit["kind"] == "line_group":
                reader_lines = [line.rstrip(" \t") for line in lines[span["start_line"] - 1:span["end_line"]]]
                if len(line_group_source) < 2 or len(reader_lines) != len(line_group_source):
                    raise SemanticStructureError(f"page {page}: line-group source/reader line count mismatch")
                if [_normalized(line) for line in reader_lines] != [_normalized(line) for line in line_group_source]:
                    raise SemanticStructureError(f"page {page}: line-group source order or line mapping mismatch")
            assets = decision.get("assets", [])
            for key in source_keys:
                block_assets = packet_blocks[key].get("assets", [])
                if not block_assets:
                    continue
                matches = [asset for asset in assets if isinstance(asset, dict) and asset.get("view") == key[0] and asset.get("source_path") in block_assets]
                if not matches:
                    raise SemanticStructureError(f"page {page}: asset-backed source block lacks decision asset")
                for asset in matches:
                    placement, logical = asset.get("placement"), asset.get("logical_name")
                    if placement == "reference_only":
                        continue
                    placeholder = f"{{{{asset:{logical}}}}}" if isinstance(logical, str) else ""
                    assertion_bound = profile == PROFILE_V2 and _v2_unit_binds_selected_asset(
                        page, unit, key, logical, visual_assertions,
                    )
                    if assertion_bound and markdown.count(placeholder) == 1:
                        continue
                    if not placeholder or placeholder not in span_text:
                        raise SemanticStructureError(f"page {page}: inline semantic asset lacks span placeholder")
            errors = _syntax_errors(unit, lines, span["start_line"], span["end_line"])
            if errors:
                raise SemanticStructureError(f"page {page}: {errors[0]}")
            if span["start_line"] < last_start:
                raise SemanticStructureError(f"page {page}: semantic units are not declared in Markdown order")
            last_start = span["start_line"]
            ids[unit["id"]] = (page, unit); spans.append((span["start_line"], span["end_line"], unit["id"]))
            rows.append({"id": unit["id"], "kind": unit["kind"], "representation": unit["representation"], "markdown_span_sha256": span["sha256"]})
        if profile == PROFILE_V2:
            _validate_v2_fragments(
                page, units, packet_blocks, lines, selected, text_corrections, block_corrections,
            )
            role_keys, role_proofs = verified_reviewed_prose_role_keys(
                decision, packet_blocks, selected, decision["markdown"], page,
                semantic_units=units, visual_inventory=visual_inventory,
            )
            validate_selected_title_coverage(page, decision, packet_blocks, units,
                                             reviewed_prose_role_keys=role_keys)
            if visual_assertions is not None:
                _validate_v2_visual_assertions(page, units, lines, visual_assertions, packet=packet, decision=decision)
            _validate_v2_role_contract(page, decision, units)
        unbound_block_corrections = set(block_corrections) - bound_block_correction_keys
        if unbound_block_corrections:
            raise SemanticStructureError(f"page {page}: reviewed block correction has no bound reader span")
        for start, end, identity in spans:
            for other_start, other_end, other_id in spans:
                if identity == other_id or end < other_start or other_end < start:
                    continue
                # Any overlap must later be proved by explicit containment parent.
                pass
        previous_end[page] = spans
        confirmation_rows = []
        for key, reader in sorted(title_confirmations.items()):
            source = str(packet_blocks[key].get("text", ""))
            confirmation_rows.append({
                "view": key[0], "raw_index": key[1],
                "source_sha256": hashlib.sha256(source.encode("utf-8")).hexdigest().upper(),
                "reader_sha256": hashlib.sha256(reader.encode("utf-8")).hexdigest().upper(),
                "changed": source != reader,
            })
        reports.append({"source_page": page, "review": review, "declared_unit_count": len(rows), "validated_unit_count": len(rows), "title_evidence_confirmations": confirmation_rows, "reviewed_prose_roles": [role_proofs[key] for key in sorted(role_proofs)], "redundant_root_blank_separator_runs": redundant_blank_runs, "units": rows})
    for page, decision in ((page, decisions[page]) for page in pages):
        for unit in decision["semantic_structure"]["units"]:
            start, end = unit["markdown_span"]["start_line"], unit["markdown_span"]["end_line"]
            for relation in ("container_parent", "semantic_parent", "continuation_of"):
                value = unit[relation]
                if value is None:
                    continue
                if not isinstance(value, str) or value not in ids:
                    raise SemanticStructureError(f"page {page}: unresolved {relation}")
                other_page, parent = ids[value]
                if relation == "container_parent":
                    parent_start = parent["markdown_span"]["start_line"]
                    parent_end = parent["markdown_span"]["end_line"]
                    contained = parent_start <= start and end <= parent_end and (parent_start, parent_end) != (start, end)
                    if other_page != page or not contained:
                        raise SemanticStructureError(f"page {page}: invalid container containment")
                elif relation == "semantic_parent":
                    if parent["kind"] != "heading" or (other_page == page and parent["markdown_span"]["start_line"] >= start) or (unit["kind"] == "heading" and unit["heading_level"] != parent["heading_level"] + 1):
                        raise SemanticStructureError(f"page {page}: invalid semantic parent")
                elif parent["kind"] != unit["kind"] or parent["representation"] != unit["representation"] or other_page > page or (other_page == page and parent["markdown_span"]["end_line"] >= start):
                    raise SemanticStructureError(f"page {page}: invalid continuation")
        units = decision["semantic_structure"]["units"]
        for index, left in enumerate(units):
            left_span = left["markdown_span"]
            for right in units[index + 1:]:
                right_span = right["markdown_span"]
                if left_span["end_line"] < right_span["start_line"] or right_span["end_line"] < left_span["start_line"]:
                    continue
                left_contains = left_span["start_line"] <= right_span["start_line"] and right_span["end_line"] <= left_span["end_line"] and left_span != right_span
                right_contains = right_span["start_line"] <= left_span["start_line"] and left_span["end_line"] <= right_span["end_line"] and left_span != right_span
                if left_contains and right["container_parent"] == left["id"]:
                    continue
                if right_contains and left["container_parent"] == right["id"]:
                    continue
                raise SemanticStructureError(f"page {page}: crossing or implicit overlapping semantic spans")
    for identity in ids:
        seen: set[str] = set(); cursor = identity
        while cursor is not None:
            if cursor in seen:
                raise SemanticStructureError("semantic relation cycle")
            seen.add(cursor)
            _, unit = ids[cursor]
            parents = [value for value in (unit["container_parent"], unit["semantic_parent"], unit["continuation_of"]) if value is not None]
            # Each relation graph is a directed parent graph; a node can have
            # several relation kinds, so inspect all reachable edges.
            pending = parents[:]
            while pending:
                parent_id = pending.pop()
                if parent_id == identity:
                    raise SemanticStructureError("semantic relation cycle")
                _, parent_unit = ids[parent_id]
                pending.extend(value for value in (parent_unit["container_parent"], parent_unit["semantic_parent"], parent_unit["continuation_of"]) if value is not None)
            cursor = unit["continuation_of"]
    if profile == PROFILE_V2:
        grouped: dict[str, list[tuple[int, Mapping[str, Any]]]] = {}
        for page in pages:
            contract = decisions[page]["semantic_structure"]["role_contract"]
            if contract["role"] == "pregenerated_characters":
                grouped.setdefault(contract["group_id"], []).append((page, contract))
        for group_id, members in grouped.items():
            numbers = [page for page, _ in members]
            if numbers != list(range(numbers[0], numbers[-1] + 1)):
                raise SemanticStructureError(f"pregenerated_pages_noncontiguous: {group_id}")
            if sum(item[1]["root_heading_id"] is not None for item in members) > 1:
                raise SemanticStructureError(f"pregenerated_root_duplicate: {group_id}")
            if members[0][1]["root_heading_id"] is None:
                raise SemanticStructureError(f"pregenerated_root_missing: {group_id}")
            if any(contract["root_heading_id"] is not None for _, contract in members[1:]):
                raise SemanticStructureError(f"pregenerated_root_position: {group_id}")
            root_id = members[0][1]["root_heading_id"]
            root_page, root = ids[root_id]
            if root_page != members[0][0] or root.get("heading_level") != 1:
                raise SemanticStructureError(f"pregenerated_root_invalid: {group_id}")
            for page, contract in members:
                if "record_heading_ids" not in contract:
                    continue
                record_ids = contract["record_heading_ids"]
                for record_id in record_ids:
                    record_page, record = ids[record_id]
                    if record_page != page or record.get("semantic_parent") != root_id:
                        raise SemanticStructureError(f"pregenerated_global_parent_invalid: {group_id}")
    return {"schema": "kb_creator.reconstruction_semantic_structure.v1", "profile": profile, "pages": reports, "structure_sha256": hashlib.sha256(__import__("json").dumps(reports, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()).hexdigest().upper()}
