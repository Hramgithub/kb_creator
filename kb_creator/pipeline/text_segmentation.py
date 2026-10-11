"""Closed reviewed accounting for source-text split and merge claims.

This module deliberately has no Stage04 or filesystem dependency.  Authoring,
audit, replay, and promotion can use the same derivation and verification code
with their own packet, reader-proof, visual-inventory, and geometry adapters.
"""

from __future__ import annotations

import hashlib
import math
import re
from collections import Counter
from collections.abc import Callable, Iterable, Mapping
from typing import Any


ALLOWLIST_FIELD = "text_segmentation_claims"
V3_ALLOWLIST_KEYS = frozenset({
    "schema", "authority", "substitutions", "source_text_exclusions",
    "visual_text_assertions", "ocr_equivalence_classes",
})
LAYOUT_RELATIONS = frozenset({"same_region", "column_wrap", "figure_wrap"})
_TOKEN = re.compile(r"[^\W_]+", re.UNICODE)
SOURCE_REGION_COORDINATE_SPACE = "mineru_page_1000_top_left_v1"


class TextSegmentationError(ValueError):
    """A reviewed segmentation claim is malformed or no longer reproducible."""


def allowlist_v3_keys(value: Mapping[str, Any]) -> frozenset[str]:
    """Accept the legacy v3 top level or its one additive claim-field variant."""
    keys = frozenset(value)
    if keys not in {V3_ALLOWLIST_KEYS, V3_ALLOWLIST_KEYS | {ALLOWLIST_FIELD}}:
        raise TextSegmentationError("v3 allowlist: closed schema required")
    return keys


def text_segmentation_claims(value: Mapping[str, Any]) -> list[Any]:
    """Return claims while preserving byte-identical legacy allowlists."""
    allowlist_v3_keys(value)
    claims = value.get(ALLOWLIST_FIELD, [])
    if not isinstance(claims, list):
        raise TextSegmentationError("text segmentation claims must be an array")
    return claims


def sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest().upper()


def unit_ref(unit: Mapping[str, Any]) -> tuple[int, str, int]:
    page, view, index = unit.get("source_page"), unit.get("view_id"), unit.get("raw_index")
    if type(page) is not int or not isinstance(view, str) or type(index) is not int:
        raise TextSegmentationError("segmentation unit identity is malformed")
    return page, view, index


def public_unit(unit: Mapping[str, Any]) -> dict[str, Any]:
    return {key: value for key, value in unit.items() if not key.startswith("_")}


def _exact_unit(value: Any, references: Mapping[tuple[int, str, int], Mapping[str, Any]], label: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise TextSegmentationError(f"{label}: unit is malformed")
    found = references.get(unit_ref(value))
    if found is None or public_unit(found) != dict(value):
        raise TextSegmentationError(f"{label}: stale or unknown packet unit")
    return found


def _selector_ref(value: Any, page: int, label: str) -> tuple[str, int]:
    if not isinstance(value, Mapping) or set(value) != {"view_id", "raw_index"}:
        raise TextSegmentationError(f"{label}: selector reference is malformed")
    view, index = value["view_id"], value["raw_index"]
    if not isinstance(view, str) or type(index) is not int or index < 0:
        raise TextSegmentationError(f"{label}: selector reference is malformed")
    return view, index


def _validate_source_region(value: Any, unit: Mapping[str, Any]) -> None:
    if not isinstance(value, Mapping) or set(value) != {"view_id", "coordinate_space", "bbox"}:
        raise TextSegmentationError("alternate token correction source region has an invalid closed shape")
    if value["view_id"] != unit.get("view_id") or value["coordinate_space"] != SOURCE_REGION_COORDINATE_SPACE:
        raise TextSegmentationError("alternate token correction source region identity is stale")
    bbox = value["bbox"]
    unit_bbox = unit.get("bbox")
    if not isinstance(bbox, list) or len(bbox) != 4 or not isinstance(unit_bbox, list) or len(unit_bbox) != 4:
        raise TextSegmentationError("alternate token correction source region bbox is malformed")
    if any(isinstance(item, bool) or not isinstance(item, (int, float)) or not math.isfinite(item) for item in bbox + unit_bbox):
        raise TextSegmentationError("alternate token correction source region bbox is not finite")
    x1, y1, x2, y2 = bbox
    ux1, uy1, ux2, uy2 = unit_bbox
    if not (x1 < x2 and y1 < y2 and ux1 < ux2 and uy1 < uy2):
        raise TextSegmentationError("alternate token correction source region bbox is not positive")
    if not (ux1 <= x1 and uy1 <= y1 and x2 <= ux2 and y2 <= uy2):
        raise TextSegmentationError("alternate token correction source region is outside its unit")


def apply_token_corrections(
    raw_text: str,
    corrections: Iterable[Mapping[str, Any]],
    *,
    max_distance: int = 2,
) -> str:
    """Apply the narrow, reviewed OCR token repair permitted by P2AX2."""
    result = raw_text
    for correction in corrections:
        if not isinstance(correction, Mapping) or set(correction) != {
            "unit", "from_token", "to_token", "source_region", "visual_verdict", "rationale",
        }:
            raise TextSegmentationError("alternate token correction has an invalid closed shape")
        before, after = correction["from_token"], correction["to_token"]
        if not isinstance(before, str) or not isinstance(after, str) or not before or not after:
            raise TextSegmentationError("alternate token correction requires nonempty tokens")
        if not before.isalnum() or not after.isalnum() or _levenshtein(before.casefold(), after.casefold()) > max_distance:
            raise TextSegmentationError("alternate token correction exceeds reviewed OCR bounds")
        if correction["visual_verdict"] != "replacement_visible_in_source" or not isinstance(correction["rationale"], str) or not correction["rationale"].strip():
            raise TextSegmentationError("alternate token correction lacks reviewed visual evidence")
        matches = [match for match in _TOKEN.finditer(result) if match.group(0) == before]
        if len(matches) != 1:
            raise TextSegmentationError("alternate token correction must match exactly one whole token")
        match = matches[0]
        result = result[:match.start()] + after + result[match.end():]
    return result


def _levenshtein(left: str, right: str) -> int:
    row = list(range(len(right) + 1))
    for index, left_char in enumerate(left, 1):
        next_row = [index]
        for offset, right_char in enumerate(right, 1):
            next_row.append(min(next_row[-1] + 1, row[offset] + 1, row[offset - 1] + (left_char != right_char)))
        row = next_row
    return row[-1]


def derive_claim(
    selector: Mapping[str, Any], *, references: Mapping[tuple[int, str, int], Mapping[str, Any]],
    selected_mappings: Mapping[tuple[int, str, int], Mapping[str, Any]], reader_text: str,
    source_visual: Mapping[str, Any], normalize: Callable[[str], str],
) -> dict[str, Any]:
    """Expand a reviewed short selector into a hash-bound closed allowlist row."""
    required = {"claim_id", "source_page", "selected", "alternates", "layout_relation", "alternate_token_corrections", "visual_verdict", "rationale"}
    allowed = required | {"alternate_full_unit_corrections"}
    if not isinstance(selector, Mapping) or not required <= set(selector) or set(selector) - allowed:
        raise TextSegmentationError("segmentation selector has an invalid closed shape")
    claim_id, page = selector["claim_id"], selector["source_page"]
    if not isinstance(claim_id, str) or not claim_id or type(page) is not int or page < 1:
        raise TextSegmentationError("segmentation selector identity is malformed")
    if selector["layout_relation"] not in LAYOUT_RELATIONS or selector["visual_verdict"] != "selected_sequence_matches_source_and_alternate_segmentation" or not isinstance(selector["rationale"], str) or not selector["rationale"].strip():
        raise TextSegmentationError("segmentation selector lacks a reviewed layout verdict")
    if not isinstance(selector["selected"], list) or not selector["selected"] or not isinstance(selector["alternates"], list) or not selector["alternates"]:
        raise TextSegmentationError("segmentation selector requires selected and alternate units")
    selected_refs = [_selector_ref(row, page, "selected") for row in selector["selected"]]
    alternate_refs = [_selector_ref(row, page, "alternate") for row in selector["alternates"]]
    if len(set(selected_refs)) != len(selected_refs) or len(set(alternate_refs)) != len(alternate_refs) or set(selected_refs) & set(alternate_refs):
        raise TextSegmentationError("segmentation selector has duplicate or overlapping members")
    if len({view for view, _ in alternate_refs}) != 1 or alternate_refs != sorted(alternate_refs, key=lambda item: item[1]):
        raise TextSegmentationError("segmentation alternates must use one view in packet order")
    selected = [references.get((page, view, index)) for view, index in selected_refs]
    alternates = [references.get((page, view, index)) for view, index in alternate_refs]
    if any(unit is None for unit in selected + alternates):
        raise TextSegmentationError("segmentation selector names an unknown packet unit")
    if len(selected) == len(alternates) == 1:
        raise TextSegmentationError("segmentation requires a split or merged sequence")
    if any(unit.get("block_type") not in {"text", "aside_text"} for unit in selected + alternates):
        raise TextSegmentationError("segmentation requires reader text units")
    if any(unit_ref(unit) in selected_mappings for unit in alternates):
        raise TextSegmentationError("segmentation alternate is already selected")
    mappings = []
    for unit in selected:
        mapping = selected_mappings.get(unit_ref(unit))
        if not isinstance(mapping, Mapping) or mapping.get("unit") != public_unit(unit) or not isinstance(mapping.get("markdown_span"), list) or len(mapping["markdown_span"]) != 2:
            raise TextSegmentationError("selected segmentation unit is not mapped to reader proof")
        start, end = mapping["markdown_span"]
        if type(start) is not int or type(end) is not int or start < 0 or end <= start or end > len(reader_text):
            raise TextSegmentationError("selected segmentation proof span is malformed")
        mappings.append((start, end))
    if any(right[0] != left[1] for left, right in zip(mappings, mappings[1:])):
        raise TextSegmentationError("selected segmentation proof spans must be contiguous and gap-free")
    corrections = selector["alternate_token_corrections"]
    if not isinstance(corrections, list):
        raise TextSegmentationError("alternate token corrections must be an array")
    correction_by_ref: dict[tuple[int, str, int], list[Mapping[str, Any]]] = {unit_ref(unit): [] for unit in alternates}
    for correction in corrections:
        if not isinstance(correction, Mapping):
            raise TextSegmentationError("alternate token correction is malformed")
        short = correction.get("unit")
        if not isinstance(short, Mapping):
            raise TextSegmentationError("alternate correction unit is malformed")
        view, index = _selector_ref(short, page, "alternate correction")
        unit = references.get((page, view, index))
        if unit is None:
            raise TextSegmentationError("alternate correction names an unknown packet unit")
        key = unit_ref(unit)
        if key not in correction_by_ref:
            raise TextSegmentationError("alternate token correction targets a non-alternate unit")
        _validate_source_region(correction.get("source_region"), unit)
        correction_by_ref[key].append(correction)
    if any(len(rows) > 2 for rows in correction_by_ref.values()):
        raise TextSegmentationError("at most two alternate token corrections are allowed per unit")
    full_rows = selector.get("alternate_full_unit_corrections", [])
    if not isinstance(full_rows, list) or len(full_rows) > 2:
        raise TextSegmentationError("alternate full-unit corrections must contain at most two rows")
    full_by_ref: dict[tuple[int, str, int], Mapping[str, Any]] = {}
    for row in full_rows:
        if not isinstance(row, Mapping) or set(row) != {"unit", "before", "after", "visual_verdict", "rationale"}:
            raise TextSegmentationError("alternate full-unit correction has an invalid closed shape")
        view, index = _selector_ref(row["unit"], page, "alternate full-unit correction")
        unit = references.get((page, view, index))
        if unit is None or unit_ref(unit) not in correction_by_ref or unit_ref(unit) in full_by_ref:
            raise TextSegmentationError("alternate full-unit correction targets an invalid or duplicate alternate")
        before, after = row["before"], row["after"]
        if not isinstance(before, str) or not isinstance(after, str) or before != unit.get("_text") or not after.strip():
            raise TextSegmentationError("alternate full-unit correction has stale before text or empty after text")
        if row["visual_verdict"] != "corrected_full_unit_visible_in_source" or not isinstance(row["rationale"], str) or not row["rationale"].strip():
            raise TextSegmentationError("alternate full-unit correction lacks reviewed visual evidence")
        before_normalized, after_normalized = normalize(before), normalize(after)
        if len(after_normalized) > len(before_normalized) or Counter(after_normalized) - Counter(before_normalized):
            raise TextSegmentationError("alternate full-unit correction adds unsupported reader text")
        full_by_ref[unit_ref(unit)] = row
    if set(full_by_ref) & {key for key, rows in correction_by_ref.items() if rows}:
        raise TextSegmentationError("alternate cannot combine token and full-unit corrections")
    def corrected_text(unit: Mapping[str, Any]) -> str:
        full = full_by_ref.get(unit_ref(unit))
        return str(full["after"]) if full else apply_token_corrections(str(unit.get("_text", "")), correction_by_ref[unit_ref(unit)])
    corrected = "".join(normalize(corrected_text(unit)) for unit in alternates)
    start, end = mappings[0][0], mappings[-1][1]
    selected_text = reader_text[start:end]
    if selected_text != corrected:
        raise TextSegmentationError("selected and corrected alternate segmentation text differ")
    offsets, cursor = [], 0
    for unit in alternates:
        part = normalize(corrected_text(unit))
        cursor += len(part); offsets.append(cursor)
    if not isinstance(source_visual, Mapping) or set(source_visual) != {"path", "bytes", "sha256"}:
        raise TextSegmentationError("segmentation source visual identity is malformed")
    return {
        "claim_id": claim_id, "source_page": page, "selected": [public_unit(unit) for unit in selected],
        "alternates": [public_unit(unit) for unit in alternates], "layout_relation": selector["layout_relation"],
        "alternate_token_corrections": [{**dict(row), "unit": public_unit(references[(page, *_selector_ref(row["unit"], page, "alternate correction"))])} for row in corrections],
        **({"alternate_full_unit_corrections": [{"unit": public_unit(references[(page, *_selector_ref(row["unit"], page, "alternate full-unit correction"))]), "before": row["before"], "after": row["after"], "before_sha256": sha256(row["before"]), "after_sha256": sha256(row["after"]), "visual_verdict": row["visual_verdict"], "rationale": row["rationale"]} for row in full_rows]} if "alternate_full_unit_corrections" in selector else {}), "source_visual": dict(source_visual),
        "visual_verdict": selector["visual_verdict"], "rationale": selector["rationale"],
        "proof": {"normalized_span": [start, end], "expected_normalized_sha256": sha256(selected_text), "alternate_partition_end_offsets": offsets},
    }


def validate_claim(
    claim: Mapping[str, Any], *, references: Mapping[tuple[int, str, int], Mapping[str, Any]],
    selected_mappings: Mapping[tuple[int, str, int], Mapping[str, Any]], reader_text: str,
    visual_inventory: Mapping[str, Mapping[str, Any]], normalize: Callable[[str], str],
    spatial_metrics: Callable[[Mapping[str, Any], Mapping[str, Any]], Mapping[str, float]],
    protected_members: Iterable[tuple[int, str, int]] = (),
    automatic_disposition: Callable[[Mapping[str, Any]], Any] | None = None,
) -> dict[str, Any]:
    """Recompute a derived claim and enforce its ownership and geometry gates."""
    required = {"claim_id", "source_page", "selected", "alternates", "layout_relation", "alternate_token_corrections", "source_visual", "visual_verdict", "rationale", "proof"}
    allowed = required | {"alternate_full_unit_corrections"}
    if not isinstance(claim, Mapping) or not required <= set(claim) or set(claim) - allowed:
        raise TextSegmentationError("segmentation claim has an invalid closed shape")
    page = claim.get("source_page")
    if type(page) is not int:
        raise TextSegmentationError("segmentation claim page is malformed")
    selected = [_exact_unit(value, references, "selected claim") for value in claim["selected"]] if isinstance(claim["selected"], list) else []
    alternates = [_exact_unit(value, references, "alternate claim") for value in claim["alternates"]] if isinstance(claim["alternates"], list) else []
    if not selected or not alternates or len({unit_ref(unit) for unit in selected + alternates}) != len(selected) + len(alternates):
        raise TextSegmentationError("segmentation claim members are empty, duplicated, or overlapping")
    if any(unit_ref(unit)[0] != page for unit in selected + alternates):
        raise TextSegmentationError("segmentation claim crosses source pages")
    selector = {key: claim[key] for key in {"claim_id", "source_page", "layout_relation", "visual_verdict", "rationale"}}
    selector["alternate_token_corrections"] = [
        {**dict(row), "unit": {"view_id": row["unit"]["view_id"], "raw_index": row["unit"]["raw_index"]}}
        for row in claim["alternate_token_corrections"]
    ] if isinstance(claim["alternate_token_corrections"], list) else claim["alternate_token_corrections"]
    if "alternate_full_unit_corrections" in claim:
        selector["alternate_full_unit_corrections"] = [
            {"unit": {"view_id": row["unit"]["view_id"], "raw_index": row["unit"]["raw_index"]}, "before": row["before"], "after": row["after"], "visual_verdict": row["visual_verdict"], "rationale": row["rationale"]}
            for row in claim["alternate_full_unit_corrections"]
        ] if isinstance(claim["alternate_full_unit_corrections"], list) else claim["alternate_full_unit_corrections"]
    selector["selected"] = [{"view_id": unit["view_id"], "raw_index": unit["raw_index"]} for unit in selected]
    selector["alternates"] = [{"view_id": unit["view_id"], "raw_index": unit["raw_index"]} for unit in alternates]
    derived = derive_claim(selector, references=references, selected_mappings=selected_mappings, reader_text=reader_text, source_visual=claim["source_visual"], normalize=normalize)
    if derived != dict(claim):
        raise TextSegmentationError("segmentation claim derived facts are stale")
    visual = claim["source_visual"]
    expected_visual = f"outputs/04-visual-merge-bundle/visual/original_pipeline_txt/pages/page-{page:03d}.png"
    if visual.get("path") != expected_visual:
        raise TextSegmentationError("segmentation source visual must match the original page")
    if visual_inventory.get(visual["path"]) != {"bytes": visual["bytes"], "sha256": visual["sha256"]}:
        raise TextSegmentationError("segmentation claim source visual identity is stale")
    protected = set(protected_members)
    if any(unit_ref(unit) in protected for unit in alternates):
        raise TextSegmentationError("segmentation alternate collides with another reviewed disposition")
    if automatic_disposition is not None and not any(automatic_disposition(unit) is None for unit in alternates):
        raise TextSegmentationError("segmentation claim has no otherwise-unaccounted alternate")
    if automatic_disposition is not None:
        claim_start, claim_end = derived["proof"]["normalized_span"]
        for unit in alternates:
            automatic = automatic_disposition(unit)
            if automatic is None:
                continue
            span = automatic.get("markdown_span") or automatic.get("selected_mapping", {}).get("markdown_span")
            if not isinstance(span, list) or len(span) != 2 or not claim_start <= span[0] < span[1] <= claim_end:
                raise TextSegmentationError("automatic segmentation proof points outside the claim")
    if not any(
        float(spatial_metrics(candidate, alternate).get("smaller_box_coverage", 0.0)) >= 0.80
        for candidate in selected for alternate in alternates
    ):
        raise TextSegmentationError("segmentation sequence lacks required selected geometry coverage")
    for alternate in alternates:
        metrics = [(candidate, spatial_metrics(candidate, alternate)) for candidate in selected]
        if claim["layout_relation"] == "same_region" and not any(float(row.get("iou", 0.0)) > 0.0 for _, row in metrics):
            raise TextSegmentationError("same_region segmentation alternate has zero overlap")
        for candidate_ref, mapping in selected_mappings.items():
            if candidate_ref in {unit_ref(unit) for unit in selected}:
                continue
            candidate = references.get(candidate_ref)
            if candidate is not None and float(spatial_metrics(candidate, alternate).get("smaller_box_coverage", 0.0)) > 0.10:
                raise TextSegmentationError("segmentation alternate has competing selected reader box")
    return derived
