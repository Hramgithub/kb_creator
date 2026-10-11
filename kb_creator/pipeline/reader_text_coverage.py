"""Closed, source-bound proof for text already represented in a reader.

This module is deliberately independent from authoring and staging.  Callers
provide packet units, file identities, selected canonical keys and reviewed
facts; this module derives a portable claim or returns a typed hold.  It never
turns an assertion, an OCR-empty block, or a boolean approval into evidence.
"""

from __future__ import annotations

import hashlib
import re
from collections.abc import Mapping, Sequence
from typing import Any


CLAIM_SCHEMA = "kb_creator.reader_text_coverage_claim.v1"
OCR_FACT_SCHEMA = "kb_creator.validated_ocr_class_fact.v1"
TRANSCRIPTION_FACT_SCHEMA = "kb_creator.source_transcription_fact.v1"
# Headers and titles remain reader text when a selected-unit mapping proves
# their reader interval; tables and visual assets are deliberately excluded.
TEXT_BLOCK_TYPES = frozenset({"text", "aside_text", "header", "title"})
PROOF_MODES = frozenset({"exact_full_unit", "reviewed_ocr_class", "continuation_subspan", "coincident_exact_alias"})
_SPACE = re.compile(r"\s+", re.UNICODE)


class ReaderTextCoverageError(ValueError):
    """A coverage claim is malformed, stale, or does not prove exact text."""


def normalized_text(value: str) -> str:
    """Fold visual line-wrap whitespace only; keep every other character exact."""
    if not isinstance(value, str):
        raise ReaderTextCoverageError("text must be a string")
    return _SPACE.sub(" ", value).strip()


def sha256(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest().upper()


def _identity(value: Any, label: str) -> dict[str, Any]:
    if not isinstance(value, Mapping) or set(value) != {"path", "bytes", "sha256"}:
        raise ReaderTextCoverageError(f"{label} identity has an invalid closed shape")
    path, size, digest = value["path"], value["bytes"], value["sha256"]
    if not isinstance(path, str) or not path or type(size) is not int or size < 0 or not isinstance(digest, str) or not re.fullmatch(r"[A-F0-9]{64}", digest):
        raise ReaderTextCoverageError(f"{label} identity is malformed")
    return dict(value)


def _key(value: Any, label: str) -> tuple[int, str, int]:
    if not isinstance(value, Mapping) or set(value) != {"source_page", "view_id", "raw_index"}:
        raise ReaderTextCoverageError(f"{label} key has an invalid closed shape")
    page, view, index = value["source_page"], value["view_id"], value["raw_index"]
    if type(page) is not int or page < 1 or not isinstance(view, str) or not view or type(index) is not int or index < 0:
        raise ReaderTextCoverageError(f"{label} key is malformed")
    return page, view, index


def _public_unit(unit: Mapping[str, Any]) -> dict[str, Any]:
    return {key: unit[key] for key in ("source_page", "view_id", "raw_index", "block_type", "text", "raw_text_sha256", "bbox")}


def _unit(unit: Any, label: str) -> dict[str, Any]:
    required = {"source_page", "view_id", "raw_index", "block_type", "text", "raw_text_sha256", "bbox"}
    if not isinstance(unit, Mapping) or set(unit) != required:
        raise ReaderTextCoverageError(f"{label} unit has an invalid closed shape")
    _key({key: unit[key] for key in ("source_page", "view_id", "raw_index")}, label)
    if unit["block_type"] not in TEXT_BLOCK_TYPES:
        raise ReaderTextCoverageError(f"{label} is an asset, table, or non-reader unit")
    if not isinstance(unit["text"], str) or not normalized_text(unit["text"]):
        raise ReaderTextCoverageError(f"{label} has no meaningful text")
    if unit["raw_text_sha256"] != sha256(unit["text"]):
        raise ReaderTextCoverageError(f"{label} raw text identity is stale")
    bbox = unit["bbox"]
    if not isinstance(bbox, list) or len(bbox) != 4 or any(type(item) not in {int, float} for item in bbox):
        raise ReaderTextCoverageError(f"{label} bbox is malformed")
    if not (bbox[0] < bbox[2] and bbox[1] < bbox[3]):
        raise ReaderTextCoverageError(f"{label} bbox is not positive")
    return dict(unit)


def _fact_for(
    fact_id: str | None, facts: Mapping[str, Any], *, schema: str, source_key: tuple[int, str, int],
    canonical_key: tuple[int, str, int], source_visual: Mapping[str, Any], mode: str,
) -> str | None:
    if not isinstance(fact_id, str) or not fact_id:
        return None
    fact = facts.get(fact_id)
    if fact is None:
        return None
    if not isinstance(fact, Mapping):
        raise ReaderTextCoverageError(f"{mode}: named validated fact is malformed")
    required = {"schema", "fact_id", "source_key", "canonical_key", "source_visual", "evidence_kind", "evidence", "exact_text"}
    if set(fact) != required or fact["schema"] != schema or fact["fact_id"] != fact_id:
        raise ReaderTextCoverageError(f"{mode}: validated fact has an invalid closed shape")
    if _key(fact["source_key"], "validated fact source") != source_key or _key(fact["canonical_key"], "validated fact canonical") != canonical_key:
        raise ReaderTextCoverageError(f"{mode}: validated fact is bound to different keys")
    if _identity(fact["source_visual"], "validated fact visual") != dict(source_visual):
        raise ReaderTextCoverageError(f"{mode}: validated fact visual identity is stale")
    expected_kinds = {"validated_ocr_class"} if schema == OCR_FACT_SCHEMA else {"source_render_exact_transcription", "source_bound_decoder"}
    if fact["evidence_kind"] not in expected_kinds:
        raise ReaderTextCoverageError(f"{mode}: validated fact has an unsupported evidence kind")
    _identity(fact["evidence"], "validated fact evidence")
    text = fact["exact_text"]
    if not isinstance(text, str) or not normalized_text(text):
        raise ReaderTextCoverageError(f"{mode}: validated fact has no exact text")
    return text


def _claim_selector(selector: Any) -> tuple[str, str, tuple[int, str, int], tuple[int, str, int], int, list[int], str, str | None, str | None]:
    required = {"claim_id", "proof_mode", "source_key", "canonical_key", "reader_page", "reader_span", "semantic_container", "validated_fact_id"}
    if not isinstance(selector, Mapping) or (set(selector) != required and set(selector) != required | {"alias_of_claim_id"}):
        raise ReaderTextCoverageError("coverage selector has an invalid closed shape")
    claim_id, mode = selector["claim_id"], selector["proof_mode"]
    if not isinstance(claim_id, str) or not claim_id or mode not in PROOF_MODES:
        raise ReaderTextCoverageError("coverage selector identity is malformed")
    source_key, canonical_key = _key(selector["source_key"], "source"), _key(selector["canonical_key"], "canonical")
    if source_key == canonical_key:
        raise ReaderTextCoverageError("selected canonical key cannot be the source key")
    reader_page, span, container, fact_id = selector["reader_page"], selector["reader_span"], selector["semantic_container"], selector["validated_fact_id"]
    if type(reader_page) is not int or reader_page < 1 or not isinstance(span, list) or len(span) != 2 or any(type(item) is not int for item in span) or span[0] < 0 or span[0] >= span[1] or not isinstance(container, str) or not container:
        raise ReaderTextCoverageError("coverage selector reader binding is malformed")
    if fact_id is not None and (not isinstance(fact_id, str) or not fact_id):
        raise ReaderTextCoverageError("coverage selector validated fact identity is malformed")
    alias_of = selector.get("alias_of_claim_id")
    if mode == "coincident_exact_alias":
        if not isinstance(alias_of, str) or not alias_of or alias_of == claim_id or fact_id is not None:
            raise ReaderTextCoverageError("coincident alias selector identity is malformed")
    elif alias_of is not None:
        raise ReaderTextCoverageError("only a coincident alias may name a primary claim")
    return claim_id, mode, source_key, canonical_key, reader_page, span, container, fact_id, alias_of


def _canonical_mapping(value: Any, *, reader_page: int, container: str, claim_span: list[int]) -> None:
    """Bind the claim interval to the selected canonical unit's reader mapping."""
    if not isinstance(value, Mapping) or set(value) != {"reader_page", "normalized_span", "semantic_container"}:
        raise ReaderTextCoverageError("canonical selected mapping has an invalid closed shape")
    mapped_page, mapped_span, mapped_container = value["reader_page"], value["normalized_span"], value["semantic_container"]
    if mapped_page != reader_page or mapped_container != container or not isinstance(mapped_span, list) or len(mapped_span) != 2 or any(type(item) is not int for item in mapped_span):
        raise ReaderTextCoverageError("canonical selected mapping is stale")
    if mapped_span[0] < 0 or mapped_span[0] >= mapped_span[1] or not (mapped_span[0] <= claim_span[0] and claim_span[1] <= mapped_span[1]):
        raise ReaderTextCoverageError("reader span is not bound to the canonical selected unit")


def assess_claim(
    selector: Mapping[str, Any], *, units: Mapping[tuple[int, str, int], Mapping[str, Any]],
    selected_keys: Sequence[tuple[int, str, int]], reader_pages: Mapping[int, Mapping[str, Any]],
    source_pdf: Mapping[str, Any], packet: Mapping[str, Any], source_visuals: Mapping[int, Mapping[str, Any]],
    reader_markdown: Mapping[int, Mapping[str, Any]], selected_mappings: Mapping[tuple[int, str, int], Mapping[str, Any]], validated_facts: Mapping[str, Any],
    excluded_keys: Sequence[tuple[int, str, int]] = (),
    primary_claims: Mapping[str, Mapping[str, Any]] | None = None,
) -> dict[str, Any]:
    """Return a validated closed claim, or a typed evidence hold for a missing fact."""
    claim_id, mode, source_key, canonical_key, reader_page, span, container, fact_id, alias_of = _claim_selector(selector)
    source = _unit(units.get(source_key), "source")
    canonical = _unit(units.get(canonical_key), "canonical")
    if canonical_key not in selected_keys:
        raise ReaderTextCoverageError("canonical key is not selected by the reader")
    if canonical_key[0] != reader_page:
        raise ReaderTextCoverageError("canonical key source page must equal reader page")
    if source_key in selected_keys:
        raise ReaderTextCoverageError("source key is already selected")
    if source_key in excluded_keys or canonical_key in excluded_keys:
        raise ReaderTextCoverageError("coverage claim collides with an excluded key")
    if reader_page not in {source_key[0], source_key[0] - 1}:
        raise ReaderTextCoverageError("reader page must be the source page or immediately preceding page")
    page = reader_pages.get(reader_page)
    if not isinstance(page, Mapping) or set(page) != {"markdown", "semantic_container"} or page["semantic_container"] != container or not isinstance(page["markdown"], str):
        raise ReaderTextCoverageError("reader page or semantic container is stale")
    reader = normalized_text(page["markdown"])
    if span[1] > len(reader):
        raise ReaderTextCoverageError("reader span is outside normalized Markdown")
    _canonical_mapping(selected_mappings.get(canonical_key), reader_page=reader_page, container=container, claim_span=span)
    source_visual = _identity(source_visuals.get(source_key[0]), "source visual")
    source_pdf_identity, packet_identity, markdown_identity = _identity(source_pdf, "source PDF"), _identity(packet, "packet"), _identity(reader_markdown.get(reader_page), "reader Markdown")
    if mode == "coincident_exact_alias":
        primary = (primary_claims or {}).get(alias_of)
        if not isinstance(primary, Mapping) or primary.get("proof_mode") == "coincident_exact_alias":
            raise ReaderTextCoverageError("coincident alias primary is missing or is an alias")
        required_primary = {"schema", "claim_id", "proof_mode", "source_pdf", "packet", "source_unit", "source_visual", "canonical_unit", "reader_markdown", "reader_page", "semantic_container", "proof"}
        if set(primary) != required_primary or primary.get("schema") != CLAIM_SCHEMA or primary.get("claim_id") != alias_of:
            raise ReaderTextCoverageError("coincident alias primary has an invalid closed shape")
        primary_source = _unit(primary["source_unit"], "coincident alias primary source")
        primary_canonical = _unit(primary["canonical_unit"], "coincident alias primary canonical")
        primary_proof = primary.get("proof")
        if (source_key == (primary_source["source_page"], primary_source["view_id"], primary_source["raw_index"])
                or source_key[0] != primary_source["source_page"]
                or normalized_text(source["text"]) != normalized_text(primary_source["text"])
                or source["raw_text_sha256"] != primary_source["raw_text_sha256"]
                or source["bbox"] != primary_source["bbox"]
                or _public_unit(canonical) != _public_unit(primary_canonical)
                or source_pdf_identity != primary["source_pdf"]
                or packet_identity != primary["packet"]
                or markdown_identity != primary["reader_markdown"]
                or reader_page != primary["reader_page"]
                or container != primary["semantic_container"]
                or not isinstance(primary_proof, Mapping)
                or primary_proof.get("normalized_span") != span
                or primary_proof.get("source_text_sha256") != sha256(normalized_text(primary_source["text"]))):
            raise ReaderTextCoverageError("coincident alias does not exactly match its primary claim")
        proof_text = source["text"]
    elif mode == "exact_full_unit":
        proof_text = source["text"]
        if normalized_text(canonical["text"]) != normalized_text(proof_text):
            raise ReaderTextCoverageError("exact full-unit canonical text differs from source")
        if canonical["bbox"] != source["bbox"]:
            raise ReaderTextCoverageError("exact full-unit canonical geometry differs from source")
    elif mode == "reviewed_ocr_class":
        proof_text = _fact_for(fact_id, validated_facts, schema=OCR_FACT_SCHEMA, source_key=source_key, canonical_key=canonical_key, source_visual=source_visual, mode=mode)
    else:
        proof_text = _fact_for(fact_id, validated_facts, schema=TRANSCRIPTION_FACT_SCHEMA, source_key=source_key, canonical_key=canonical_key, source_visual=source_visual, mode=mode)
    if proof_text is None:
        needed = "validated OCR-class fact" if mode == "reviewed_ocr_class" else "source-render exact transcription"
        return {"status": "deferred", "claim_id": claim_id, "reason_code": "missing_bound_evidence", "needed": needed, "source_key": dict(selector["source_key"])}
    proof_normalized = normalized_text(proof_text)
    reader_subspan = reader[span[0]:span[1]]
    if reader_subspan != proof_normalized:
        raise ReaderTextCoverageError("reader span does not exactly equal source proof text")
    first_occurrence = reader.find(proof_normalized)
    if first_occurrence < 0 or reader.find(proof_normalized, first_occurrence + 1) >= 0:
        raise ReaderTextCoverageError("reader proof text is ambiguous or duplicated")
    return {
        "status": "validated",
        "claim": {
            "schema": CLAIM_SCHEMA, "claim_id": claim_id, "proof_mode": mode,
            "source_pdf": source_pdf_identity, "packet": packet_identity,
            "source_unit": _public_unit(source), "source_visual": source_visual,
            "canonical_unit": _public_unit(canonical), "reader_markdown": markdown_identity,
            "reader_page": reader_page, "semantic_container": container,
            "proof": {"normalized_span": span, "expected_normalized_sha256": sha256(proof_normalized), "source_text_sha256": sha256(proof_normalized), "validated_fact_id": fact_id,
                      **({"alias_of_claim_id": alias_of} if mode == "coincident_exact_alias" else {})},
        },
    }


def validate_claims(claims: Sequence[Mapping[str, Any]]) -> None:
    """Enforce global one-source-key and non-overlapping reader-span ownership."""
    source_keys: set[tuple[int, str, int]] = set()
    claim_ids: set[str] = set()
    claims_by_id: dict[str, Mapping[str, Any]] = {}
    spans: dict[int, list[tuple[int, int, str, Mapping[str, Any]]]] = {}
    for item in claims:
        if not isinstance(item, Mapping) or set(item) != {"status", "claim"} or item.get("status") != "validated" or not isinstance(item.get("claim"), Mapping):
            raise ReaderTextCoverageError("coverage batch contains a deferred or malformed claim")
        claim = item["claim"]
        required = {"schema", "claim_id", "proof_mode", "source_pdf", "packet", "source_unit", "source_visual", "canonical_unit", "reader_markdown", "reader_page", "semantic_container", "proof"}
        if set(claim) != required or claim["schema"] != CLAIM_SCHEMA:
            raise ReaderTextCoverageError("coverage claim has an invalid closed shape")
        claim_id = claim["claim_id"]
        if not isinstance(claim_id, str) or not claim_id or claim_id in claim_ids:
            raise ReaderTextCoverageError("coverage claim_id is invalid or duplicated")
        claim_ids.add(claim_id)
        if claim.get("proof_mode") not in PROOF_MODES:
            raise ReaderTextCoverageError("coverage claim proof mode is invalid")
        claims_by_id[claim_id] = claim
        key = _key({name: claim["source_unit"][name] for name in ("source_page", "view_id", "raw_index")}, "claim source")
        if key in source_keys:
            raise ReaderTextCoverageError("source key has more than one coverage claim")
        source_keys.add(key)
        proof = claim["proof"]
        if not isinstance(proof, Mapping) or not isinstance(proof.get("normalized_span"), list) or len(proof["normalized_span"]) != 2:
            raise ReaderTextCoverageError("coverage claim proof is malformed")
        start, end = proof["normalized_span"]
        page = claim["reader_page"]
        for old_start, old_end, old_id, old_claim in spans.setdefault(page, []):
            if start < old_end and old_start < end:
                alias_of = proof.get("alias_of_claim_id")
                old_alias_of = old_claim["proof"].get("alias_of_claim_id")
                if not ((claim["proof_mode"] == "coincident_exact_alias" and alias_of == old_id)
                        or (old_claim["proof_mode"] == "coincident_exact_alias" and old_alias_of == claim["claim_id"])):
                    raise ReaderTextCoverageError(f"reader span overlaps claim {old_id}")
        spans[page].append((start, end, claim["claim_id"], claim))
    for claim in claims_by_id.values():
        proof = claim["proof"]
        alias_of = proof.get("alias_of_claim_id")
        if claim["proof_mode"] != "coincident_exact_alias":
            if alias_of is not None:
                raise ReaderTextCoverageError("only a coincident alias may overlap its primary")
            continue
        primary = claims_by_id.get(alias_of)
        if not isinstance(alias_of, str) or not isinstance(primary, Mapping) or primary.get("proof_mode") == "coincident_exact_alias":
            raise ReaderTextCoverageError("coincident alias primary is missing or is an alias")
        source = _unit(claim["source_unit"], "coincident alias source")
        primary_source = _unit(primary["source_unit"], "coincident alias primary source")
        canonical = _unit(claim["canonical_unit"], "coincident alias canonical")
        primary_canonical = _unit(primary["canonical_unit"], "coincident alias primary canonical")
        primary_proof = primary["proof"]
        if (source["source_page"] != primary_source["source_page"]
                or (source["source_page"], source["view_id"], source["raw_index"]) == (primary_source["source_page"], primary_source["view_id"], primary_source["raw_index"])
                or normalized_text(source["text"]) != normalized_text(primary_source["text"])
                or source["raw_text_sha256"] != primary_source["raw_text_sha256"]
                or source["bbox"] != primary_source["bbox"]
                or _public_unit(canonical) != _public_unit(primary_canonical)
                or claim["source_pdf"] != primary["source_pdf"]
                or claim["packet"] != primary["packet"]
                or claim["reader_markdown"] != primary["reader_markdown"]
                or claim["reader_page"] != primary["reader_page"]
                or claim["semantic_container"] != primary["semantic_container"]
                or proof["normalized_span"] != primary_proof.get("normalized_span")
                or proof.get("source_text_sha256") != sha256(normalized_text(source["text"]))
                or primary_proof.get("source_text_sha256") != sha256(normalized_text(primary_source["text"]))):
            raise ReaderTextCoverageError("coincident alias does not exactly match its primary claim")
