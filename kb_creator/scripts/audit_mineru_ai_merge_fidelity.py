"""Fail-closed, stdlib-only audit of AI merge decisions against merge packets."""
from __future__ import annotations

import argparse
import collections
from decimal import Decimal, InvalidOperation
import difflib
import hashlib
import json
import os
import re
import stat
import sys
import tempfile
import unicodedata
from pathlib import Path
from typing import Any

from kb_creator.pipeline.source_page_render import render_source_pdf_page, validate_source_page_render_row


TOKEN = re.compile(r"[^\W_]+", re.UNICODE)
IMAGE = re.compile(r"!\[[^\]]*\]\([^)]*\)")
ASSET = re.compile(r"\{\{asset:[^}]+\}\}")
INLINE_SUP_SUB = re.compile(r"</?(?:sup|sub)>", re.IGNORECASE)
# A lexical-empty unit is retained only when its source bytes are limited to
# OCR/control noise and empty inline super/subscript markup.  This is narrower
# than the normalization function: punctuation, digits, equations, and any
# text enclosed by markup remain auditable source content.
EMPTY_NORMALIZATION_MARKUP = re.compile(r"</?(?:sup|sub)>", re.IGNORECASE)
EMPTY_NORMALIZATION_RESIDUE = re.compile(r"[\s\x00-\x1f\x7f\u00ad\u200b\u200c\u200d\ufeff\-\u2010-\u2015]*\Z")
PAGE = re.compile(r"^page-(\d{3})$")
V2_SCHEMA = "kb_creator.ai-merge-fidelity-audit/v2"
V2_ALLOWLIST_SCHEMA = "kb_creator.ai_merge_fidelity_reviewed_allowlist.v2"
V2_RUN_SCHEMA = "kb_creator.run_spec.v2"
REQUIRED_CPU_VIEWS = ["original_pipeline_txt", "original_pipeline_ocr", "raster_pipeline_ocr"]
V2_POLICY = {"source_completeness_threshold": 1.0, "selected_recall_threshold": 0.95, "required_views": REQUIRED_CPU_VIEWS, "normalization": "unicode_nfkc_casefold_alphanumeric_stream_v1", "low_text_exemption": False}
V3_SCHEMA = "kb_creator.ai-merge-fidelity-audit/v3"
V4_SCHEMA = "kb_creator.ai-merge-fidelity-audit/v4"
V3_ALLOWLIST_SCHEMA = "kb_creator.ai_merge_fidelity_reviewed_allowlist.v3"
V3_POLICY = {
    **V2_POLICY,
    "visual_assertion_policy": "position_first_interleaved_v1",
    "ocr_equivalence_policy": "same_page_geometry_lexical_v1",
    "ocr_min_iou": 0.50,
    "ocr_max_center_distance": 0.035,
    "ocr_max_token_levenshtein": 1,
    "ocr_max_string_levenshtein": 2,
    "ocr_min_similarity": 0.92,
    "canonical_geometry_policy": "source_displayed_mediabox_affine_v1",
    "whole_unit_equivalence_policy": "exact_unique_cross_view_geometry_v2",
    "subspan_equivalence_policy": "exact_unique_selected_context_geometry_v2",
    "subspan_min_smaller_box_coverage": 0.80,
    "subspan_max_other_box_overlap": 0.10,
    "running_furniture_policy": "reviewed_multi_page_top_margin_v2",
    "running_furniture_max_y": 0.12,
    "running_furniture_allow_mirrored_parity": True,
    "running_furniture_min_iou": 0.80,
    "running_furniture_max_center_distance": 0.01,
    "running_furniture_max_levenshtein": 1,
    "running_furniture_min_similarity": 0.92,
}
FILE_ATTRIBUTE_REPARSE_POINT = 0x400


def _json(path: Path, label: str) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise ValueError(f"{label}: invalid JSON") from error


def _tokens(text: str, markdown: bool = False) -> list[str]:
    if markdown:
        text = ASSET.sub(" ", IMAGE.sub(" ", text))
        text = re.sub(r"[`*_#>[\](){}]", " ", text)
    return TOKEN.findall(text.casefold())


def _multiset_metrics(selected: list[str], decision: list[str]) -> tuple[float, float]:
    selected_counts, decision_counts = collections.Counter(selected), collections.Counter(decision)
    common = sum((selected_counts & decision_counts).values())
    return (common / len(selected) if selected else 1.0, common / len(decision) if decision else 1.0)


def _aligned_word_pairs(selected: list[str], rendered: list[str]) -> list[dict[str, str]]:
    """Return only local, equal-count replacements; insertions cannot cascade."""
    pairs: list[dict[str, str]] = []
    matcher = difflib.SequenceMatcher(a=selected, b=rendered, autojunk=False)
    for opcode, left_start, left_end, right_start, right_end in matcher.get_opcodes():
        left_size, right_size = left_end - left_start, right_end - right_start
        if opcode != "replace" or left_size != right_size or left_size > 25:
            continue
        for left, right in zip(selected[left_start:left_end], rendered[right_start:right_end]):
            if left == right or len(left) != len(right):
                continue
            chars = difflib.SequenceMatcher(a=left, b=right, autojunk=False)
            changed_left, changed_right = [], []
            for char_opcode, a0, a1, b0, b1 in chars.get_opcodes():
                if char_opcode != "equal":
                    changed_left.append(left[a0:a1]); changed_right.append(right[b0:b1])
            source, replacement = "".join(changed_left), "".join(changed_right)
            if 1 <= len(source) <= 3 and 1 <= len(replacement) <= 3:
                pairs.append({"from_word": left, "to_word": right, "from": source, "to": replacement})
    return pairs


def _packet_index(root: Path) -> dict[int, Path]:
    index = _json(root / "merge_index.json", "merge index")
    rows = index.get("by_source_page") if isinstance(index, dict) else None
    if not isinstance(rows, list):
        raise ValueError("merge index: by_source_page missing")
    result: dict[int, Path] = {}
    for row in rows:
        if not isinstance(row, dict) or not isinstance(row.get("source_page"), int) or not isinstance(row.get("packet"), str):
            raise ValueError("merge index: invalid row")
        page = row["source_page"]
        if page in result or Path(row["packet"]).is_absolute():
            raise ValueError("merge index: duplicate page or unsafe packet path")
        packet = (root / row["packet"]).resolve()
        try: packet.relative_to(root.resolve())
        except ValueError as error: raise ValueError("merge index: packet path escapes root") from error
        if not packet.is_file(): raise ValueError(f"merge index: missing packet for page {page}")
        result[page] = packet
    if not result or set(result) != set(range(1, max(result) + 1)):
        raise ValueError("merge index: page domain must be contiguous from 1")
    return result


def _decision_index(root: Path, pages: set[int]) -> dict[int, Path]:
    result: dict[int, Path] = {}
    for path in root.glob("*.json"):
        match = PAGE.match(path.stem)
        if not match: raise ValueError(f"decisions: unexpected filename {path.name}")
        page = int(match.group(1))
        if page in result: raise ValueError(f"decisions: duplicate page {page}")
        result[page] = path
    if set(result) != pages: raise ValueError("decisions: page domain does not match merge packets")
    return result


def _allowlist(path: Path | None) -> dict[tuple[int, str, str], dict[str, Any]]:
    if path is None: return {}
    data = _json(path, "allowlist")
    rows = data.get("allowlist") if isinstance(data, dict) and set(data) == {"allowlist"} else None
    if not isinstance(rows, list): raise ValueError("allowlist: closed allowlist array required")
    result = {}
    for row in rows:
        if not isinstance(row, dict) or set(row) != {"source_page", "pattern", "max_count", "evidence"}:
            raise ValueError("allowlist: closed row required")
        pattern = row["pattern"]
        if not isinstance(row["source_page"], int) or not isinstance(pattern, dict) or set(pattern) != {"from", "to"} or not all(isinstance(pattern[key], str) and 1 <= len(pattern[key]) <= 3 for key in pattern) or not isinstance(row["max_count"], int) or row["max_count"] < 3 or not isinstance(row["evidence"], str) or not row["evidence"].strip():
            raise ValueError("allowlist: invalid row")
        key = (row["source_page"], pattern["from"].casefold(), pattern["to"].casefold())
        if key in result: raise ValueError("allowlist: duplicate row")
        result[key] = row
    return result


def _selected_tokens(packet: dict[str, Any], decision: dict[str, Any], page: int) -> list[str]:
    if packet.get("source_page") != page or not isinstance(packet.get("views"), dict): raise ValueError(f"page {page}: malformed packet")
    selected = decision.get("selected_blocks")
    if not isinstance(selected, list): raise ValueError(f"page {page}: selected_blocks missing")
    tokens, used = [], set()
    for row in selected:
        if not isinstance(row, dict) or not isinstance(row.get("view"), str) or not isinstance(row.get("raw_index"), int): raise ValueError(f"page {page}: malformed selected reference")
        key = (row["view"], row["raw_index"])
        if key in used: raise ValueError(f"page {page}: duplicate selected reference")
        used.add(key)
        view = packet["views"].get(row["view"])
        blocks = view.get("blocks") if isinstance(view, dict) else None
        matches = [block for block in blocks or [] if isinstance(block, dict) and block.get("raw_index") == row["raw_index"] and block.get("source_page") == page]
        if len(matches) != 1: raise ValueError(f"page {page}: selected reference absent from packet")
        block = matches[0]
        if block.get("type") not in {"image", "page_number"}:
            if not isinstance(block.get("text", ""), str): raise ValueError(f"page {page}: selected block text malformed")
            tokens.extend(_tokens(block.get("text", "")))
    return tokens


def audit(decisions_root: Path, packets_root: Path, allowlist_path: Path | None = None, recall_threshold: float = 0.95) -> dict[str, Any]:
    if not 0 <= recall_threshold <= 1: raise ValueError("recall threshold must be 0..1")
    packets = _packet_index(packets_root); decisions = _decision_index(decisions_root, set(packets)); allowlist = _allowlist(allowlist_path)
    errors, pages, used_allowlist = [], [], set()
    for page in sorted(packets):
        decision = _json(decisions[page], f"page {page} decision")
        if not isinstance(decision, dict) or decision.get("source_page") != page or not isinstance(decision.get("markdown"), str): raise ValueError(f"page {page}: malformed decision")
        selected = _selected_tokens(_json(packets[page], f"page {page} packet"), decision, page)
        rendered = _tokens(decision["markdown"], markdown=True)
        recall, precision = _multiset_metrics(selected, rendered)
        word_pairs = _aligned_word_pairs(selected, rendered)
        patterns = collections.Counter((row["from"], row["to"]) for row in word_pairs)
        pattern_rows = []
        for (left, right), count in sorted(patterns.items()):
            row = {"from": left, "to": right, "count": count}; key = (page, left, right)
            if count >= 3:
                allowed = allowlist.get(key)
                if allowed is None or allowed["max_count"] != count:
                    errors.append(f"page {page}: repeated substitution {left}->{right} count {count}")
                else:
                    used_allowlist.add(key); row["allowlisted"] = True
            pattern_rows.append(row)
        recall_failed = len(selected) >= 20 and recall < recall_threshold
        if recall_failed: errors.append(f"page {page}: recall {recall:.6f} below {recall_threshold:.6f}")
        pages.append({"source_page": page, "selected_token_count": len(selected), "decision_token_count": len(rendered), "recall": recall, "precision": precision, "recall_threshold_applied": len(selected) >= 20, "word_pairs": word_pairs, "substitutions": pattern_rows, "passed": not recall_failed and not any(error.startswith(f"page {page}: repeated") for error in errors)})
    unused = set(allowlist) - used_allowlist
    if unused: errors.append("allowlist: unused or overbroad rows " + canonical_keys(unused))
    return {"schema": "kb_creator.ai-merge-fidelity-audit/v1", "recall_threshold": recall_threshold, "pages": pages, "errors": errors, "passed": not errors}


def canonical_keys(keys: set[tuple[int, str, str]]) -> str:
    return json.dumps([{"source_page": page, "from": left, "to": right} for page, left, right in sorted(keys)], ensure_ascii=False, separators=(",", ":"))


def _sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest().upper()


def _identity(path: Path) -> dict[str, Any]:
    raw = path.read_bytes()
    return {"bytes": len(raw), "sha256": _sha(raw)}


def _normalized(text: str) -> str:
    value = INLINE_SUP_SUB.sub("", text)
    value = unicodedata.normalize("NFKC", value).casefold().replace("\u00ad", "")
    return "".join(character for character in value if character.isalnum())


def _is_reparse(path: Path) -> bool:
    info = os.lstat(path)
    attributes = getattr(info, "st_file_attributes", None)
    if os.name == "nt" and attributes is None:
        raise ValueError("Windows reparse-point inspection is unavailable")
    return stat.S_ISLNK(info.st_mode) or bool(attributes is not None and attributes & FILE_ATTRIBUTE_REPARSE_POINT)


def _assert_no_reparse(path: Path, *, tree: bool = False) -> None:
    cursor, existing = path.absolute(), []
    while True:
        if cursor.exists() or cursor.is_symlink(): existing.append(cursor)
        if cursor.parent == cursor: break
        cursor = cursor.parent
    if any(_is_reparse(item) for item in reversed(existing)):
        raise ValueError("authority path crosses a reparse point")
    if tree:
        if not path.is_dir(): raise ValueError(f"authority directory is missing: {path}")
        for root, directories, files in os.walk(path, followlinks=False):
            if any(_is_reparse(Path(root) / name) for name in directories + files):
                raise ValueError("authority tree contains a reparse point")


def _checked_identity(path: Path, expected_sha256: str, label: str) -> dict[str, Any]:
    if not re.fullmatch(r"[0-9A-Fa-f]{64}", expected_sha256 or ""):
        raise ValueError(f"{label}: invalid SHA-256")
    _assert_no_reparse(path)
    if not path.is_file(): raise ValueError(f"{label}: missing file")
    identity = _identity(path)
    if identity["sha256"] != expected_sha256.upper(): raise ValueError(f"{label}: SHA-256 mismatch")
    return identity


def _make_unit(page: int, view: str, block: dict[str, Any]) -> dict[str, Any]:
    text, bbox = block.get("text"), block.get("bbox")
    if not isinstance(text, str) or not text.strip(): raise ValueError(f"page {page}: malformed textual block")
    if bbox is not None and (not isinstance(bbox, list) or len(bbox) != 4 or any(type(item) not in {int, float} for item in bbox)):
        raise ValueError(f"page {page}: malformed block bbox")
    normalized = _normalized(text)
    normalization_empty_artifact = False
    if not normalized:
        table_body, assets = block.get("table_body", []), block.get("assets", [])
        if (
            block.get("type") not in {"page_number", "header", "footer"}
            or not isinstance(table_body, list) or table_body
            or not isinstance(assets, list) or assets
            or not EMPTY_NORMALIZATION_RESIDUE.fullmatch(EMPTY_NORMALIZATION_MARKUP.sub("", text))
        ):
            raise ValueError(f"page {page}: empty normalized textual block is not a safe OCR artifact")
        normalization_empty_artifact = True
    return {"source_page": page, "view_id": view, "raw_index": block["raw_index"], "block_type": block.get("type"), "bbox": bbox, "original_text_sha256": _sha(text.encode()), "normalized_text_sha256": _sha(normalized.encode()), "normalized_character_count": len(normalized), "_text": text, "_normalized": normalized, "_normalization_empty_artifact": normalization_empty_artifact}


def _public_unit(unit: dict[str, Any]) -> dict[str, Any]:
    return {key: value for key, value in unit.items() if not key.startswith("_")}


def _unit_key(unit: dict[str, Any]) -> tuple[Any, ...]:
    return (unit["source_page"], unit["view_id"], unit["raw_index"], unit["original_text_sha256"], unit["normalized_text_sha256"])


def _v2_allowlist(path: Path | None, expected: dict[str, str]) -> tuple[dict[str, Any], dict[str, Any] | None]:
    empty = {"substitutions": [], "source_text_exclusions": [], "visual_text_assertions": []}
    if path is None: return empty, None
    _assert_no_reparse(path)
    data = _json(path, "v2 allowlist")
    keys = {"schema", "authority", *empty}
    if not isinstance(data, dict) or set(data) != keys or data.get("schema") != V2_ALLOWLIST_SCHEMA: raise ValueError("v2 allowlist: closed schema required")
    if not isinstance(data.get("authority"), dict) or set(data["authority"]) != set(expected) or data["authority"] != expected: raise ValueError("v2 allowlist: stale authority")
    if any(not isinstance(data[key], list) for key in empty): raise ValueError("v2 allowlist: arrays required")
    return data, {"path_hint": path.name, **_identity(path), "schema": V2_ALLOWLIST_SCHEMA}


def audit_v2_content(packets: dict[int, dict[str, Any]], decisions: dict[int, dict[str, Any]], *, allowlist: dict[str, Any] | None = None, authorities: dict[str, Any] | None = None) -> dict[str, Any]:
    """Pure v2 ledger. Production callers use audit_v2 for authority validation."""
    allowlist = allowlist or {"substitutions": [], "source_text_exclusions": [], "visual_text_assertions": []}
    errors, pages, boundaries = [], [], []
    used_exclusions, used_assertions, used_substitutions = set(), set(), set()
    substitutions = allowlist.get("substitutions", [])
    for row in substitutions:
        if not isinstance(row, dict) or set(row) != {"source_page", "pattern", "max_count", "evidence"}: raise ValueError("v2 allowlist: invalid closed substitution row")
    previous_last = None
    for page in sorted(packets):
        packet, decision = packets[page], decisions.get(page)
        if not isinstance(decision, dict) or decision.get("source_page") != page or not isinstance(decision.get("markdown"), str): raise ValueError(f"page {page}: malformed decision")
        views = packet.get("views") if isinstance(packet, dict) else None
        if packet.get("source_page") != page or not isinstance(views, dict) or list(views)[:3] != REQUIRED_CPU_VIEWS: raise ValueError(f"page {page}: exact required CPU view domain is missing or reordered")
        units, references = [], {}
        for view_id in REQUIRED_CPU_VIEWS:
            blocks = views[view_id].get("blocks") if isinstance(views[view_id], dict) else None
            if not isinstance(blocks, list): raise ValueError(f"page {page}: malformed required view")
            for block in blocks:
                if not isinstance(block, dict) or type(block.get("raw_index")) is not int: raise ValueError(f"page {page}: malformed block")
                if block.get("type") == "image" or not isinstance(block.get("text"), str) or not block["text"].strip(): continue
                unit = _make_unit(page, view_id, block); key = (view_id, block["raw_index"])
                if key in references: raise ValueError(f"page {page}: duplicate raw block reference")
                units.append(unit); references[key] = unit
        selected, selected_keys = [], set()
        if not isinstance(decision.get("selected_blocks"), list): raise ValueError(f"page {page}: selected_blocks missing")
        for row in decision["selected_blocks"]:
            if not isinstance(row, dict) or not isinstance(row.get("view"), str) or type(row.get("raw_index")) is not int: raise ValueError(f"page {page}: malformed selected reference")
            unit = references.get((row["view"], row["raw_index"]))
            if unit is None:
                matches = [block for block in views.get(row.get("view"), {}).get("blocks", []) if block.get("raw_index") == row.get("raw_index")]
                if len(matches) == 1 and matches[0].get("type") == "image": continue
                raise ValueError(f"page {page}: selected text reference absent")
            if unit.get("_normalization_empty_artifact"):
                raise ValueError(f"page {page}: selected textual block has empty lexical normalization")
            if _unit_key(unit) in selected_keys: raise ValueError(f"page {page}: duplicate selected text unit")
            selected.append(unit); selected_keys.add(_unit_key(unit))
        rendered = _normalized(ASSET.sub("", IMAGE.sub("", decision["markdown"])))
        cursor, mappings = 0, []
        for unit in selected:
            start = rendered.find(unit["_normalized"], cursor)
            if start < 0:
                errors.append(f"page {page}: selected unit {unit['view_id']}:{unit['raw_index']} has no monotonic full Markdown span")
                continue
            end = start + len(unit["_normalized"]); cursor = end
            mappings.append({"unit": _public_unit(unit), "markdown_span": [start, end]})
        anchors = [unit["_normalized"] for unit in selected]
        joined_anchors = "".join(anchors)
        dispositions, unaccounted = [], 0
        for unit in units:
            matches = []
            for index, row in enumerate(allowlist.get("source_text_exclusions", [])):
                if not isinstance(row, dict) or set(row) != {"unit", "classification", "rationale", "visual", "logical_asset"}: raise ValueError("v2 allowlist: invalid closed exclusion row")
                if row.get("unit") == _public_unit(unit): matches.append((index, row))
            selected_unit = _unit_key(unit) in selected_keys
            full_covered = any(unit["_normalized"] in anchor for anchor in anchors) or unit["_normalized"] in joined_anchors
            if unit.get("_normalization_empty_artifact"):
                if matches:
                    raise ValueError("v2 allowlist: normalization-empty OCR artifact must not use a source exclusion")
                dispositions.append({"unit": _public_unit(unit), "disposition": "excluded_normalization_empty_artifact"})
                continue
            if selected_unit and matches: errors.append(f"page {page}: selected unit is also excluded {unit['view_id']}:{unit['raw_index']}")
            if len(matches) > 1: errors.append(f"page {page}: unit has duplicate exclusions {unit['view_id']}:{unit['raw_index']}")
            if selected_unit: disposition = "included_selected"
            elif full_covered: disposition = "included_equivalent"
            elif matches:
                index, row = matches[0]
                if row["classification"] not in {"visual_only", "advertisement", "decorative", "non_reader", "ocr_artifact"} or not isinstance(row["rationale"], str) or not row["rationale"].strip(): raise ValueError("v2 allowlist: invalid exclusion classification or rationale")
                if not isinstance(row["visual"], dict) or set(row["visual"]) != {"path", "bytes", "sha256"}: raise ValueError("v2 allowlist: exclusion lacks exact visual identity")
                if row["classification"] == "visual_only" and not isinstance(row["logical_asset"], str): errors.append(f"page {page}: visual_only exclusion lacks logical asset")
                if row["classification"] != "visual_only" and row["logical_asset"] is not None: errors.append(f"page {page}: non-visual exclusion has logical asset")
                if row["classification"] == "ocr_artifact" and unit["view_id"] == "raster_pipeline_ocr": errors.append(f"page {page}: raster evidence cannot be excluded as OCR artifact")
                used_exclusions.add(index); disposition = "excluded_reviewed"
            else:
                disposition = "unaccounted"; unaccounted += 1
                errors.append(f"page {page}: unaccounted full source unit {unit['view_id']}:{unit['raw_index']}")
            dispositions.append({"unit": _public_unit(unit), "disposition": disposition})
        assertions = []
        for index, row in enumerate(allowlist.get("visual_text_assertions", [])):
            if not isinstance(row, dict) or set(row) != {"source_page", "text", "original_text_sha256", "normalized_text_sha256", "bbox", "rationale", "visual"}: raise ValueError("v2 allowlist: invalid closed visual assertion")
            if row["source_page"] != page: continue
            normalized = _normalized(row["text"]) if isinstance(row["text"], str) else ""
            if not normalized or row["original_text_sha256"] != _sha(row["text"].encode()) or row["normalized_text_sha256"] != _sha(normalized.encode()): raise ValueError("v2 allowlist: visual assertion text identity mismatch")
            if any(unit["_normalized"] == normalized for unit in units): errors.append(f"page {page}: visual assertion duplicates extracted text")
            elif normalized not in rendered: errors.append(f"page {page}: visual assertion is absent from Markdown")
            else: used_assertions.add(index)
            assertions.append(row)
        authoritative_stream = joined_anchors + "".join(_normalized(row["text"]) for row in assertions)
        if rendered != authoritative_stream:
            errors.append(f"page {page}: Markdown contains omitted, reordered, or unproven reader text")
        selected_tokens = list("".join(unit["_normalized"] for unit in selected))
        rendered_tokens = list(rendered)
        recall, precision = _multiset_metrics(selected_tokens, rendered_tokens)
        if recall < 0.95: errors.append(f"page {page}: selected recall {recall:.6f} below 0.950000")
        word_pairs = _aligned_word_pairs([token for unit in selected for token in _tokens(unit["_text"])], _tokens(decision["markdown"], markdown=True))
        patterns = collections.Counter((row["from"], row["to"]) for row in word_pairs)
        substitution_rows = []
        for (left, right), count in sorted(patterns.items()):
            record = {"from": left, "to": right, "count": count, "allowlisted": False}
            if count >= 3:
                matches = [(index, row) for index, row in enumerate(substitutions) if row.get("source_page") == page and row.get("pattern") == {"from": left, "to": right} and row.get("max_count") == count and isinstance(row.get("evidence"), str) and row["evidence"].strip()]
                if len(matches) != 1: errors.append(f"page {page}: repeated substitution {left}->{right} count {count}")
                else: used_substitutions.add(matches[0][0]); record["allowlisted"] = True
            substitution_rows.append(record)
        required_chars = sum(unit["normalized_character_count"] for unit in units)
        covered_chars = sum(unit["normalized_character_count"] for unit, row in zip(units, dispositions) if row["disposition"] != "unaccounted")
        completeness = covered_chars / required_chars if required_chars else 1.0
        page_errors = [item for item in errors if item.startswith(f"page {page}:")]
        pages.append({"source_page": page, "required_character_count": required_chars, "covered_character_count": covered_chars, "completeness": completeness, "selected_recall": recall, "selected_precision": precision, "ordered_span_mappings": mappings, "units": dispositions, "substitutions": substitution_rows, "visual_assertions": assertions, "unaccounted_unit_count": unaccounted, "errors": page_errors, "passed": not page_errors and completeness == 1.0})
        reader_units = [unit for unit, row in zip(units, dispositions) if row["disposition"] in {"included_selected", "included_equivalent"}]
        if previous_last is not None and reader_units:
            left_page, left = previous_last; right = reader_units[0]
            hyphenated = left["_text"].rstrip().endswith("-") and right["_text"].lstrip()[:1].islower()
            boundaries.append({"left_page": left_page, "right_page": page, "kind": "hyphenated_continuation" if hyphenated else "page_boundary", "left_unit": _public_unit(left), "right_unit": _public_unit(right), "both_sides_covered": True})
        if reader_units: previous_last = (page, reader_units[-1])
    unused_exclusions = sorted(set(range(len(allowlist.get("source_text_exclusions", [])))) - used_exclusions)
    unused_assertions = sorted(set(range(len(allowlist.get("visual_text_assertions", [])))) - used_assertions)
    unused_substitutions = sorted(set(range(len(substitutions))) - used_substitutions)
    if unused_substitutions: errors.append(f"v2 allowlist: unused substitutions {unused_substitutions}")
    if unused_exclusions: errors.append(f"v2 allowlist: unused source_text_exclusions {unused_exclusions}")
    if unused_assertions: errors.append(f"v2 allowlist: unused visual_text_assertions {unused_assertions}")
    return {"schema": V2_SCHEMA, "authorities": authorities or {}, "policy": V2_POLICY, "pages": pages, "boundaries": boundaries, "errors": errors, "passed": not errors and all(row["passed"] for row in pages)}


def _levenshtein(left: str, right: str) -> int:
    previous = list(range(len(right) + 1))
    for index, left_char in enumerate(left, 1):
        current = [index]
        for offset, right_char in enumerate(right, 1):
            current.append(min(current[-1] + 1, previous[offset] + 1, previous[offset - 1] + (left_char != right_char)))
        previous = current
    return previous[-1]


def _decimal(value: Any, label: str) -> Decimal:
    if isinstance(value, bool) or not isinstance(value, (str, int, float, Decimal)):
        raise ValueError(f"v3 geometry: {label} must be numeric")
    try:
        result = Decimal(str(value))
    except (InvalidOperation, ValueError) as error:
        raise ValueError(f"v3 geometry: {label} must be numeric") from error
    if not result.is_finite():
        raise ValueError(f"v3 geometry: {label} must be finite")
    return result


def _geometry_box(value: Any, label: str) -> tuple[Decimal, Decimal, Decimal, Decimal]:
    if not isinstance(value, list) or len(value) != 4:
        raise ValueError(f"v3 geometry: {label} must contain four coordinates")
    result = tuple(_decimal(item, label) for item in value)
    if result[0] >= result[2] or result[1] >= result[3]:
        raise ValueError(f"v3 geometry: {label} is reversed or empty")
    return result  # type: ignore[return-value]


def _geometry_row(unit: dict[str, Any], geometry: dict[str, Any]) -> dict[str, Any]:
    rows = geometry.get("observed_geometry") if isinstance(geometry, dict) else None
    if not isinstance(rows, list):
        raise ValueError("v3 geometry: observed geometry is missing")
    matches = [row for row in rows if isinstance(row, dict) and row.get("view_id") == unit["view_id"] and row.get("source_page") == unit["source_page"]]
    if len(matches) != 1:
        raise ValueError("v3 geometry: exact view/page transform is missing or ambiguous")
    return matches[0]


def _fraction_bbox(unit: dict[str, Any], geometry: dict[str, Any]) -> list[float]:
    """Map a crop-local MinerU bbox into the displayed source MediaBox frame."""
    bbox = _geometry_box(unit.get("bbox"), "MinerU bbox")
    if any(item < 0 or item > 1000 for item in bbox):
        raise ValueError("v3 geometry: bbox escapes MinerU page space")
    row = _geometry_row(unit, geometry)
    media = _geometry_box(row.get("media_box_coordinates"), "MediaBox")
    crop = _geometry_box(row.get("crop_box_coordinates"), "CropBox")
    if crop[0] < media[0] or crop[1] < media[1] or crop[2] > media[2] or crop[3] > media[3]:
        raise ValueError("v3 geometry: CropBox escapes MediaBox")
    rotation = row.get("rotation_degrees")
    if isinstance(rotation, bool) or not isinstance(rotation, int) or rotation not in {0, 90, 180, 270}:
        raise ValueError("v3 geometry: unsupported rotation")
    user_unit = _decimal(row.get("user_unit"), "UserUnit")
    if user_unit <= 0:
        raise ValueError("v3 geometry: UserUnit must be positive")
    effective = row.get("effective_displayed_size_points")
    if not isinstance(effective, list) or len(effective) != 2:
        raise ValueError("v3 geometry: displayed source authority is missing")

    media_width = (media[2] - media[0]) * user_unit
    media_height = (media[3] - media[1]) * user_unit
    displayed = (media_width, media_height) if rotation in {0, 180} else (media_height, media_width)
    observed = (_decimal(effective[0], "displayed width"), _decimal(effective[1], "displayed height"))
    if observed != displayed:
        raise ValueError("v3 geometry: effective displayed size disagrees with MediaBox, rotation, or UserUnit")

    crop_width, crop_height = crop[2] - crop[0], crop[3] - crop[1]
    corners: list[tuple[Decimal, Decimal]] = []
    for local_x in (bbox[0], bbox[2]):
        for local_y in (bbox[1], bbox[3]):
            pdf_x = crop[0] + local_x * crop_width / Decimal(1000)
            pdf_y = crop[3] - local_y * crop_height / Decimal(1000)
            x = (pdf_x - media[0]) * user_unit
            y = (pdf_y - media[1]) * user_unit
            if rotation == 0:
                displayed_x, displayed_y = x, media_height - y
            elif rotation == 90:
                displayed_x, displayed_y = y, x
            elif rotation == 180:
                displayed_x, displayed_y = media_width - x, y
            else:
                displayed_x, displayed_y = media_height - y, media_width - x
            corners.append((displayed_x / displayed[0], displayed_y / displayed[1]))
    result_decimals = [
        min(point[0] for point in corners), min(point[1] for point in corners),
        max(point[0] for point in corners), max(point[1] for point in corners),
    ]
    if not (0 <= result_decimals[0] < result_decimals[2] <= 1 and 0 <= result_decimals[1] < result_decimals[3] <= 1):
        raise ValueError("v3 geometry: transformed bbox escapes displayed MediaBox")
    return [float(item) for item in result_decimals]


def _spatial_metrics(left: dict[str, Any], right: dict[str, Any], geometry: dict[str, Any]) -> dict[str, float]:
    a, b = _fraction_bbox(left, geometry), _fraction_bbox(right, geometry)
    return _box_spatial_metrics(a, b)


def _box_spatial_metrics(a: list[float], b: list[float]) -> dict[str, float]:
    width = max(0.0, min(a[2], b[2]) - max(a[0], b[0])); height = max(0.0, min(a[3], b[3]) - max(a[1], b[1]))
    intersection = width * height
    union = (a[2] - a[0]) * (a[3] - a[1]) + (b[2] - b[0]) * (b[3] - b[1]) - intersection
    iou = intersection / union if union else 0.0
    ax, ay = (a[0] + a[2]) / 2, (a[1] + a[3]) / 2
    bx, by = (b[0] + b[2]) / 2, (b[1] + b[3]) / 2
    smaller = min((a[2] - a[0]) * (a[3] - a[1]), (b[2] - b[0]) * (b[3] - b[1]))
    return {
        "iou": round(iou, 12),
        "center_distance": round(((ax - bx) ** 2 + (ay - by) ** 2) ** 0.5 / (2 ** 0.5), 12),
        "smaller_box_coverage": round(intersection / smaller if smaller else 0.0, 12),
    }


def _exact_unit(value: Any, references: dict[tuple[str, int], dict[str, Any]], page: int, label: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ValueError(f"v3 {label}: exact unit object required")
    unit = references.get((value.get("view_id"), value.get("raw_index")))
    if unit is None:
        raise ValueError(f"v3 {label}: stale or absent unit (missing view={value.get('view_id')!r} raw_index={value.get('raw_index')!r})")
    if unit["source_page"] != page:
        raise ValueError(f"v3 {label}: stale or absent unit (page mismatch expected={page} actual={unit['source_page']})")
    public = _public_unit(unit)
    if value != public:
        category = "shape" if set(value) != set(public) else "identity"
        raise ValueError(f"v3 {label}: stale or absent unit ({category} mismatch view={value.get('view_id')!r} raw_index={value.get('raw_index')!r})")
    return unit


def _visual_evidence(value: Any, inventory: dict[str, dict[str, Any]], label: str) -> None:
    if not isinstance(value, dict) or set(value) != {"path", "bytes", "sha256"}:
        raise ValueError(f"v3 {label}: exact visual identity required")
    path = value.get("path")
    if not isinstance(path, str) or not path.startswith("outputs/04-visual-merge-bundle/visual/") or "\\" in path or ":" in path or ".." in Path(path).parts:
        raise ValueError(f"v3 {label}: unsafe visual path")
    if inventory.get(path) != {"bytes": value["bytes"], "sha256": value["sha256"]}:
        raise ValueError(f"v3 {label}: visual identity mismatch")


def _selected_asset_evidence(value: Any, inventory: dict[str, dict[str, Any]], label: str) -> None:
    """Verify a selected binary from sealed Stage02 (or legacy Stage04)."""
    if not isinstance(value, dict) or set(value) != {"path", "bytes", "sha256"}:
        raise ValueError(f"v3 {label}: exact asset identity required")
    path = value.get("path")
    valid = isinstance(path, str) and "\\" not in path and ":" not in path and ".." not in Path(path).parts
    valid = valid and (path.startswith("outputs/02-mineru-three-view/views/") or path.startswith("outputs/04-visual-merge-bundle/visual/"))
    if not valid:
        raise ValueError(f"v3 {label}: unsafe selected asset path")
    if inventory.get(path) != {"bytes": value["bytes"], "sha256": value["sha256"]}:
        raise ValueError(f"v3 {label}: selected asset identity mismatch")


def _v3_assertions(
    page: int, rows: list[Any], units: list[dict[str, Any]], references: dict[tuple[str, int], dict[str, Any]],
    selected_keys: set[tuple[Any, ...]], mappings_by_key: dict[tuple[Any, ...], dict[str, Any]], rendered: str,
    geometry: dict[str, Any], visual_inventory: dict[str, dict[str, Any]], errors: list[str], used: set[int],
    packet: dict[str, Any], decision: dict[str, Any],
) -> list[dict[str, Any]]:
    proofs, seen = [], set()
    for index, row in enumerate(rows):
        if not isinstance(row, dict) or set(row) != {"assertion_id", "source_page", "text", "original_text_sha256", "normalized_text_sha256", "source_region", "placement", "visual", "visual_verdict", "rationale"}:
            raise ValueError("v3 allowlist: invalid closed visual assertion")
        if row["source_page"] != page:
            continue
        normalized = _normalized(row["text"]) if isinstance(row["text"], str) else ""
        if not normalized or row["original_text_sha256"] != _sha(row["text"].encode()) or row["normalized_text_sha256"] != _sha(normalized.encode()):
            raise ValueError("v3 assertion: text identity mismatch")
        region = row["source_region"]
        if not isinstance(region, dict) or set(region) != {"view_id", "coordinate_space", "bbox"} or region["coordinate_space"] != "mineru_page_1000_top_left_v1":
            raise ValueError("v3 assertion: source region shape mismatch")
        placement = row["placement"]
        if not isinstance(placement, dict):
            raise ValueError("v3 assertion: placement shape mismatch")
        from kb_creator.pipeline.empty_text_assertions import RELATION as EMPTY_TEXT_RELATION, validate as validate_empty_assertion
        if placement.get("relation") == EMPTY_TEXT_RELATION:
            start, end = validate_empty_assertion(row, packet, decision, rendered)
            source_block = placement["source_block"]
            claim = (source_block["view_id"], source_block["raw_index"], EMPTY_TEXT_RELATION)
            if claim in seen:
                raise ValueError("v3 assertion: duplicate empty source region claim")
            seen.add(claim)
            _fraction_bbox(source_block, geometry)
            _visual_evidence(row["visual"], visual_inventory, "empty-text assertion")
            if any(unit["_normalized"] == normalized for unit in units):
                errors.append(f"page {page}: visual assertion duplicates extracted text")
            used.add(index)
            proofs.append({"assertion_id": row["assertion_id"], "source_block": copy_json(source_block),
                           "relation": EMPTY_TEXT_RELATION, "markdown_span": [start, end], "visual": copy_json(row["visual"])})
            continue
        if placement.get("relation") == "within_selected_asset_region":
            if set(placement) != {"relation", "asset_block", "logical_name", "asset", "markdown_span"}:
                raise ValueError("v3 assertion: asset placement shape mismatch")
            asset_block = placement["asset_block"]
            expected_asset_block = {"source_page", "view_id", "raw_index", "block_type", "bbox", "source_path"}
            if not isinstance(asset_block, dict) or set(asset_block) != expected_asset_block or asset_block.get("source_page") != page or asset_block.get("block_type") not in {"image", "table"}:
                raise ValueError("v3 assertion: asset block shape mismatch")
            blocks = packet.get("views", {}).get(asset_block.get("view_id"), {}).get("blocks", [])
            matches = [block for block in blocks if isinstance(block, dict) and block.get("raw_index") == asset_block.get("raw_index")]
            if len(matches) != 1 or matches[0].get("type") != asset_block["block_type"] or matches[0].get("bbox") != asset_block["bbox"] or matches[0].get("assets") != [asset_block["source_path"]]:
                raise ValueError("v3 assertion: asset block is stale or ambiguous")
            selected = [row for row in decision.get("selected_blocks", []) if isinstance(row, dict) and row.get("view") == asset_block["view_id"] and row.get("raw_index") == asset_block["raw_index"] and row.get("purpose") == "asset"]
            assets = [row for row in decision.get("assets", []) if isinstance(row, dict) and row.get("view") == asset_block["view_id"] and row.get("source_path") == asset_block["source_path"] and row.get("logical_name") == placement.get("logical_name")]
            if len(selected) != 1 or len(assets) != 1:
                raise ValueError("v3 assertion: selected asset binding mismatch")
            from kb_creator.pipeline.reconstruction_asset_inventory import exact_selected_asset_path
            expected_asset_path = exact_selected_asset_path(visual_inventory, asset_block["view_id"], asset_block["source_path"])
            expected_asset = {"path": expected_asset_path, **visual_inventory.get(expected_asset_path, {})}
            if placement["asset"] != expected_asset:
                raise ValueError("v3 assertion: selected asset binary identity mismatch")
            _selected_asset_evidence(placement["asset"], visual_inventory, "assertion asset")
            assertion_box, block_box = _fraction_bbox({"source_page": page, "view_id": region["view_id"], "bbox": region["bbox"]}, geometry), _fraction_bbox(asset_block, geometry)
            if region["view_id"] != asset_block["view_id"] or not (block_box[0] < assertion_box[0] < assertion_box[2] < block_box[2] and block_box[1] < assertion_box[1] < assertion_box[3] < block_box[3]):
                errors.append(f"page {page}: visual assertion is outside selected asset region {row['assertion_id']}")
            reader_span = placement["markdown_span"]
            if not isinstance(reader_span, dict) or set(reader_span) != {"start", "end", "sha256"} or type(reader_span.get("start")) is not int or type(reader_span.get("end")) is not int:
                raise ValueError("v3 assertion: asset reader span shape mismatch")
            start, end = reader_span["start"], reader_span["end"]
            if not (0 <= start < end <= len(rendered)) or rendered[start:end] != normalized or reader_span["sha256"] != _sha(normalized.encode()):
                errors.append(f"page {page}: asset assertion reader span mismatch {row['assertion_id']}")
            if rendered.count(normalized) != 1:
                errors.append(f"page {page}: asset assertion normalized text is absent or ambiguous {row['assertion_id']}")
            duplicate = (asset_block["view_id"], asset_block["raw_index"], tuple(region["bbox"]), normalized)
            if duplicate in seen:
                raise ValueError("v3 assertion: duplicate asset region/text claim")
            seen.add(duplicate)
            for proof in proofs:
                other = proof.get("asset_block") if isinstance(proof, dict) else None
                if other != asset_block:
                    continue
                other_row = next((candidate for candidate in rows if isinstance(candidate, dict) and candidate.get("assertion_id") == proof.get("assertion_id")), None)
                other_box = other_row.get("source_region", {}).get("bbox") if isinstance(other_row, dict) else None
                if isinstance(other_box, list) and not (region["bbox"][2] <= other_box[0] or other_box[2] <= region["bbox"][0] or region["bbox"][3] <= other_box[1] or other_box[3] <= region["bbox"][1]):
                    errors.append(f"page {page}: overlapping selected asset regions {row['assertion_id']}")
            _visual_evidence(row["visual"], visual_inventory, "assertion")
            if row["visual_verdict"] != "source_text_visible_at_region" or not isinstance(row["rationale"], str) or not row["rationale"].strip():
                raise ValueError("v3 assertion: verdict or rationale mismatch")
            if any(unit["_normalized"] == normalized for unit in units):
                errors.append(f"page {page}: visual assertion duplicates extracted text")
            used.add(index)
            proofs.append({"assertion_id": row["assertion_id"], "asset_block": copy_json(asset_block), "logical_name": placement["logical_name"], "relation": placement["relation"], "markdown_span": [start, end], "visual": copy_json(row["visual"]), "asset": copy_json(placement["asset"])})
            continue
        if set(placement) != {"relation", "anchor_unit", "expected_pair_sha256"} or placement["relation"] not in {"before_anchor", "after_anchor", "column_before_anchor", "column_after_anchor", "anchor_prefix"}:
            raise ValueError("v3 assertion: placement shape mismatch")
        anchor = _exact_unit(placement["anchor_unit"], references, page, "assertion anchor")
        anchor_key = _unit_key(anchor)
        pair = (anchor_key, placement["relation"])
        if pair in seen:
            raise ValueError("v3 assertion: duplicate anchor/relation")
        seen.add(pair)
        if anchor["view_id"] not in REQUIRED_CPU_VIEWS or anchor_key not in selected_keys or anchor_key not in mappings_by_key:
            raise ValueError("v3 assertion: anchor is not one selected required-view unit")
        if region["view_id"] != anchor["view_id"]:
            raise ValueError("v3 assertion: coordinate view differs from anchor")
        assertion_unit = {**anchor, "bbox": region["bbox"]}
        assertion_box, anchor_box = _fraction_bbox(assertion_unit, geometry), _fraction_bbox(anchor, geometry)
        if placement["relation"] == "before_anchor":
            predicate = min(assertion_box[2], anchor_box[2]) > max(assertion_box[0], anchor_box[0]) and assertion_box[3] <= anchor_box[1]
        elif placement["relation"] == "after_anchor":
            predicate = min(assertion_box[2], anchor_box[2]) > max(assertion_box[0], anchor_box[0]) and assertion_box[1] >= anchor_box[3]
        elif placement["relation"] == "column_before_anchor":
            # A source column can end far below an anchor in the next column.
            # The only permitted wrap is strict left-to-right column order;
            # Markdown adjacency below remains independently enforced.
            predicate = assertion_box[2] <= anchor_box[0]
        elif placement["relation"] == "column_after_anchor":
            # A source column can begin far above an anchor in the previous column.
            # The only permitted wrap is strict left-to-right column order;
            # Markdown adjacency below remains independently enforced.
            predicate = assertion_box[0] >= anchor_box[2]
        else:
            predicate = min(assertion_box[3], anchor_box[3]) > max(assertion_box[1], anchor_box[1]) and (assertion_box[0] + assertion_box[2]) / 2 <= anchor_box[0] + (anchor_box[2] - anchor_box[0]) * 0.25
        if not predicate:
            errors.append(f"page {page}: visual assertion geometry predicate failed {row['assertion_id']}")
        expected_pair = _sha(((anchor["_normalized"] + normalized) if placement["relation"] in {"after_anchor", "column_after_anchor"} else (normalized + anchor["_normalized"])).encode())
        if placement["expected_pair_sha256"] != expected_pair:
            raise ValueError("v3 assertion: expected pair identity mismatch")
        anchor_span = mappings_by_key[anchor_key]["markdown_span"]
        anchor_start = anchor_span[0]
        start, end = (anchor_span[1], anchor_span[1] + len(normalized)) if placement["relation"] in {"after_anchor", "column_after_anchor"} else (anchor_start - len(normalized), anchor_start)
        if start < 0 or rendered[start:end] != normalized:
            errors.append(f"page {page}: positional visual assertion is not adjacent before anchor {row['assertion_id']}")
        _visual_evidence(row["visual"], visual_inventory, "assertion")
        if row["visual_verdict"] != "source_text_visible_at_region" or not isinstance(row["rationale"], str) or not row["rationale"].strip():
            raise ValueError("v3 assertion: verdict or rationale mismatch")
        # Repeated labels in distinct stat blocks are separate source occurrences.
        # An exact anchor/reader span already binds this insertion; reject an
        # extracted copy only when it also occupies the claimed source region.
        for unit in units:
            if unit["_normalized"] != normalized:
                continue
            extracted_box = _fraction_bbox(unit, geometry)
            if (min(assertion_box[2], extracted_box[2]) > max(assertion_box[0], extracted_box[0])
                    and min(assertion_box[3], extracted_box[3]) > max(assertion_box[1], extracted_box[1])):
                errors.append(f"page {page}: visual assertion duplicates extracted text")
                break
        used.add(index)
        proofs.append({"assertion_id": row["assertion_id"], "anchor_unit": _public_unit(anchor), "relation": placement["relation"], "markdown_span": [start, end], "visual": copy_json(row["visual"])})
    return proofs


def copy_json(value: Any) -> Any:
    return json.loads(json.dumps(value, ensure_ascii=False))


def _v3_page_context(page: int, packet: dict[str, Any], decision: dict[str, Any], geometry: dict[str, Any], errors: list[str], *, scoped_references: set[tuple[str, int]] | None = None) -> dict[str, Any]:
    views = packet.get("views") if isinstance(packet, dict) else None
    if not isinstance(decision, dict) or decision.get("source_page") != page or not isinstance(decision.get("markdown"), str):
        raise ValueError(f"page {page}: malformed decision")
    if packet.get("source_page") != page or not isinstance(views, dict) or list(views)[:3] != REQUIRED_CPU_VIEWS:
        raise ValueError(f"page {page}: exact required CPU view domain is missing or reordered")
    rows = decision.get("selected_blocks")
    if not isinstance(rows, list):
        raise ValueError(f"page {page}: selected_blocks missing")
    # MinerU image blocks can carry extracted captions. Only an explicit reader
    # selection puts that text in the lexical stream; selecting the asset alone
    # retains the existing binary-only semantics.
    image_reader_keys = {
        (row.get("view"), row.get("raw_index")) for row in rows
        if isinstance(row, dict) and isinstance(row.get("view"), str)
        and type(row.get("raw_index")) is int
        and row.get("purpose") in {"text", "structure"}
        and (scoped_references is None or (row["view"], row["raw_index"]) in scoped_references)
    }
    units, references = [], {}
    for view_id in REQUIRED_CPU_VIEWS:
        blocks = views[view_id].get("blocks") if isinstance(views[view_id], dict) else None
        if not isinstance(blocks, list):
            raise ValueError(f"page {page}: malformed required view")
        for block in blocks:
            if not isinstance(block, dict) or type(block.get("raw_index")) is not int:
                raise ValueError(f"page {page}: malformed block")
            if (block.get("type") == "image" and (view_id, block["raw_index"]) not in image_reader_keys) or not isinstance(block.get("text"), str) or not block["text"].strip():
                continue
            unit = _make_unit(page, view_id, block)
            _fraction_bbox(unit, geometry)
            key = (view_id, block["raw_index"])
            if key in references:
                raise ValueError(f"page {page}: duplicate raw block reference")
            units.append(unit); references[key] = unit
    selected, selected_keys = [], set()
    for row in rows:
        if not isinstance(row, dict) or not isinstance(row.get("view"), str) or type(row.get("raw_index")) is not int:
            raise ValueError(f"page {page}: malformed selected reference")
        if scoped_references is not None and (row["view"], row["raw_index"]) not in scoped_references:
            continue
        unit = references.get((row["view"], row["raw_index"]))
        if unit is None:
            from kb_creator.pipeline.empty_text_assertions import descriptor as empty_descriptor, owner as empty_owner
            if empty_owner(decision, row["view"], row["raw_index"]) is not None:
                empty_descriptor(packet, page, row["view"], row["raw_index"])
                # No lexical source unit is invented. The later assertion and
                # semantic gates must prove the visible text for this owner.
                continue
            matches = [block for block in views.get(row.get("view"), {}).get("blocks", []) if block.get("raw_index") == row.get("raw_index")]
            if len(matches) == 1 and (
                matches[0].get("type") == "image" or (
                    not str(matches[0].get("text") or "").strip()
                    and isinstance(matches[0].get("assets"), list)
                    and bool(matches[0]["assets"])
                )
            ):
                continue
            raise ValueError(f"page {page}: selected text reference absent")
        if unit.get("_normalization_empty_artifact"):
            raise ValueError(f"page {page}: selected textual block has empty lexical normalization")
        # An asset-purpose selection proves the binary reference for the
        # materializer; it does not claim that newly exposed table/OCR text is
        # also rendered as reader Markdown. Such text must be dispositioned by
        # an explicit visual-only exclusion, while semantic replacements use
        # purpose=structure and remain in the lexical proof stream.
        if row.get("purpose") == "asset":
            continue
        if _unit_key(unit) in selected_keys:
            raise ValueError(f"page {page}: duplicate selected text unit")
        selected.append(unit); selected_keys.add(_unit_key(unit))
    # A visually reviewed exact OCR correction changes only the reader-facing
    # form used for Markdown span binding.  The source unit identity and OCR
    # equivalence metrics remain bound to the immutable extracted bytes.
    from kb_creator.pipeline.semantic_structure import (
        apply_reviewed_text_corrections,
        reviewed_block_text_corrections,
        reviewed_text_corrections,
    )
    packet_blocks = {
        (view_id, block["raw_index"]): block
        for view_id in REQUIRED_CPU_VIEWS
        for block in views[view_id]["blocks"]
        if isinstance(block, dict) and type(block.get("raw_index")) is int
    }
    selected_refs = {(unit["view_id"], unit["raw_index"]) for unit in selected}
    corrections = reviewed_text_corrections(
        decision, packet_blocks, selected_refs, decision["markdown"], page,
    )
    block_corrections = reviewed_block_text_corrections(
        decision, packet_blocks, selected_refs, decision["markdown"], page,
    )
    rendered = _normalized(ASSET.sub("", IMAGE.sub("", decision["markdown"])))
    cursor, mappings, mappings_by_key = 0, [], {}
    reviewed_reader_projections = {}
    for unit in selected:
        rendered_source = apply_reviewed_text_corrections(
            unit["_text"], (unit["view_id"], unit["raw_index"]), corrections, block_corrections,
        )
        if decision.get("reviewed_block_corrections"):
            reviewed_reader_projections[_unit_key(unit)] = rendered_source
        rendered_normalized = _normalized(rendered_source)
        start = rendered.find(rendered_normalized, cursor)
        if start < 0:
            errors.append(f"page {page}: selected unit {unit['view_id']}:{unit['raw_index']} has no monotonic full Markdown span")
            continue
        end = start + len(rendered_normalized); cursor = end
        mapping = {"kind": "selected", "unit": _public_unit(unit), "markdown_span": [start, end]}
        mappings.append(mapping); mappings_by_key[_unit_key(unit)] = mapping
    return {
        "packet": packet, "decision": decision, "units": units, "references": references,
        "selected": selected, "selected_keys": selected_keys, "rendered": rendered,
        "mappings": mappings, "mappings_by_key": mappings_by_key,
        "reviewed_reader_projections": reviewed_reader_projections,
    }


def _exact_equivalent(unit: dict[str, Any], context: dict[str, Any], geometry: dict[str, Any]) -> dict[str, Any] | None:
    textual = [candidate for candidate in context["selected"] if candidate["view_id"] != unit["view_id"] and candidate["_normalized"] == unit["_normalized"] and _unit_key(candidate) in context["mappings_by_key"]]
    qualified = []
    for candidate in textual:
        metrics = _spatial_metrics(candidate, unit, geometry)
        if metrics["iou"] >= V3_POLICY["ocr_min_iou"] and metrics["center_distance"] <= V3_POLICY["ocr_max_center_distance"]:
            qualified.append((candidate, metrics))
    if len(qualified) != 1:
        return None
    canonical, metrics = qualified[0]
    return {
        "canonical_unit": _public_unit(canonical),
        "selected_mapping": copy_json(context["mappings_by_key"][_unit_key(canonical)]),
        "geometry": metrics,
        "policy": V3_POLICY["whole_unit_equivalence_policy"],
    }


def _strict_subspan_equivalent(unit: dict[str, Any], context: dict[str, Any], geometry: dict[str, Any]) -> dict[str, Any] | None:
    candidates = []
    for canonical in context["selected"]:
        if canonical["view_id"] == unit["view_id"] or _unit_key(canonical) not in context["mappings_by_key"]:
            continue
        alternate = unit["_normalized"]; canonical_text = canonical["_normalized"]
        if not alternate or len(alternate) >= len(canonical_text) or canonical_text.count(alternate) != 1:
            continue
        offset = canonical_text.find(alternate)
        metrics = _spatial_metrics(canonical, unit, geometry)
        if metrics["smaller_box_coverage"] < V3_POLICY["subspan_min_smaller_box_coverage"]:
            continue
        mapping = context["mappings_by_key"][_unit_key(canonical)]
        markdown_span = [mapping["markdown_span"][0] + offset, mapping["markdown_span"][0] + offset + len(alternate)]
        if context["rendered"][markdown_span[0]:markdown_span[1]] != alternate:
            continue
        collision = False
        for other in context["selected"]:
            if _unit_key(other) == _unit_key(canonical) or _unit_key(other) not in context["mappings_by_key"]:
                continue
            overlap = _spatial_metrics(other, unit, geometry)["smaller_box_coverage"]
            other_span = context["mappings_by_key"][_unit_key(other)]["markdown_span"]
            proof_overlap = markdown_span[0] < other_span[1] and markdown_span[1] > other_span[0]
            # Adjacent OCR line boxes can overlap at their edges. This does
            # not permit a second text owner or an overlapping reader proof.
            if (overlap > V3_POLICY["subspan_max_other_box_overlap"]
                    or (overlap > 0 and alternate in other["_normalized"]) or proof_overlap):
                collision = True; break
        if not collision:
            candidates.append((canonical, mapping, offset, markdown_span, metrics))
    if len(candidates) != 1:
        return None
    canonical, mapping, offset, markdown_span, metrics = candidates[0]
    return {
        "canonical_unit": _public_unit(canonical), "selected_mapping": copy_json(mapping),
        "normalized_substring_offsets": [offset, offset + len(unit["_normalized"])],
        "markdown_span": markdown_span, "geometry": metrics,
        "policy": V3_POLICY["subspan_equivalence_policy"],
    }


def _unit_from_allowlist(value: Any, contexts: dict[int, dict[str, Any]]) -> dict[str, Any] | None:
    if not isinstance(value, dict) or type(value.get("source_page")) is not int:
        return None
    context = contexts.get(value["source_page"])
    if context is None:
        return None
    unit = context["references"].get((value.get("view_id"), value.get("raw_index")))
    return unit if unit is not None and value == _public_unit(unit) else None


def _has_reader_correspondence(unit: dict[str, Any], context: dict[str, Any], geometry: dict[str, Any]) -> bool:
    if _unit_key(unit) in context["selected_keys"]:
        return True
    for selected in context["selected"]:
        if _unit_key(selected) not in context["mappings_by_key"]:
            continue
        if _spatial_metrics(selected, unit, geometry)["smaller_box_coverage"] > 0:
            return True
    return False


def _reviewed_running_furniture(
    rows: list[Any], contexts: dict[int, dict[str, Any]], geometry: dict[str, Any],
    visual_inventory: dict[str, dict[str, Any]], assertions: list[Any], classes: list[Any],
) -> set[tuple[Any, ...]]:
    entries = []
    class_units = []
    for row in classes:
        if isinstance(row, dict):
            class_units.extend([row.get("canonical_unit"), *row.get("alternate_units", [])] if isinstance(row.get("alternate_units"), list) else [row.get("canonical_unit")])
    class_keys = {_unit_key(unit) for value in class_units if (unit := _unit_from_allowlist(value, contexts)) is not None}
    assertion_keys = {_unit_key(unit) for row in assertions if isinstance(row, dict) and isinstance(row.get("placement"), dict) if (unit := _unit_from_allowlist(row["placement"].get("anchor_unit"), contexts)) is not None}
    for index, row in enumerate(rows):
        if not isinstance(row, dict) or set(row) != {"unit", "classification", "rationale", "visual", "logical_asset"} or row.get("classification") != "non_reader":
            continue
        unit = _unit_from_allowlist(row.get("unit"), contexts)
        if unit is None or unit["block_type"] not in {"text", "header"}:
            continue
        if not isinstance(row.get("rationale"), str) or not row["rationale"].strip():
            continue
        _visual_evidence(row.get("visual"), visual_inventory, "running furniture")
        context = contexts[unit["source_page"]]
        box = _fraction_bbox(unit, geometry)
        if box[3] > V3_POLICY["running_furniture_max_y"]:
            continue
        key = _unit_key(unit)
        if key in class_keys or key in assertion_keys or _has_reader_correspondence(unit, context, geometry):
            continue
        entries.append((index, row, unit))
    accepted: set[tuple[Any, ...]] = set()
    for _, _, unit in entries:
        for _, _, peer in entries:
            if peer["view_id"] != unit["view_id"] or peer["source_page"] == unit["source_page"]:
                continue
            distance = _levenshtein(unit["_normalized"], peer["_normalized"])
            similarity = difflib.SequenceMatcher(a=unit["_normalized"], b=peer["_normalized"], autojunk=False).ratio()
            metrics = _spatial_metrics(unit, peer, geometry)
            if unit["source_page"] % 2 != peer["source_page"] % 2:
                # Facing pages may mirror the running head around the gutter.
                a, b = _fraction_bbox(unit, geometry), _fraction_bbox(peer, geometry)
                mirrored = _box_spatial_metrics(a, [1 - b[2], b[1], 1 - b[0], b[3]])
                if mirrored["iou"] > metrics["iou"]:
                    metrics = mirrored
            if distance <= V3_POLICY["running_furniture_max_levenshtein"] and similarity >= V3_POLICY["running_furniture_min_similarity"] and metrics["iou"] >= V3_POLICY["running_furniture_min_iou"] and metrics["center_distance"] <= V3_POLICY["running_furniture_max_center_distance"]:
                accepted.add(_unit_key(unit)); break
    return accepted


def _v3_ocr_class_proofs(page, context, rows, assertion_proofs, geometry, visual_inventory, errors, decision):
    """Validate OCR classes independently of the page conservation ledger.

    The full audit consumes the returned members to account every source unit.
    A bounded consumer may use the same class proof without treating unrelated
    page units as accounted.
    """
    units, references = context["units"], context["references"]
    selected, selected_keys = context["selected"], context["selected_keys"]
    rendered, mappings_by_key = context["rendered"], context["mappings_by_key"]
    members, reports, used = {}, [], set()
    for index, row in enumerate(rows):
        bounded = {"class_id", "source_page", "canonical_unit", "alternate_units", "visual", "visual_verdict", "rationale"}
        reviewed_keys = bounded | {"equivalence_policy", "source_visual", "canonical_proof"}
        if not isinstance(row, dict) or (set(row) != bounded and set(row) != reviewed_keys):
            raise ValueError("v3 allowlist: invalid closed OCR equivalence class")
        if row["source_page"] != page:
            continue
        reviewed = set(row) == reviewed_keys
        canonical = _exact_unit(row["canonical_unit"], references, page, f"OCR canonical class_id={row['class_id']!r}")
        if _unit_key(canonical) not in selected_keys or _unit_key(canonical) not in mappings_by_key:
            raise ValueError("v3 OCR equivalence: canonical unit is not selected and mapped")
        policy = row.get("equivalence_policy")
        if (not reviewed or policy == "reviewed_visual_full_unit_v1") and canonical["view_id"] != "original_pipeline_txt":
            raise ValueError("v3 OCR equivalence: canonical must use original_pipeline_txt")
        if reviewed and (policy not in {"reviewed_visual_full_unit_v1", "reviewed_visual_full_unit_any_cpu_view_v1", "reviewed_exact_raw_text_geometry_drift_v1"} or row["visual_verdict"] != "canonical_proof_complete_for_region_alternates_are_ocr_corruption"):
            raise ValueError("v3 OCR equivalence: reviewed policy or verdict mismatch")
        if reviewed and policy != "reviewed_visual_full_unit_v1" and canonical["view_id"] not in REQUIRED_CPU_VIEWS:
            raise ValueError("v3 OCR equivalence: reviewed canonical must use a required CPU view")
        supporting, proof_text = [], None
        if reviewed:
            proof = row["canonical_proof"]
            if not isinstance(proof, dict) or set(proof) != {"supporting_assertion_ids", "expected_normalized_sha256"} or not isinstance(proof["supporting_assertion_ids"], list) or len(proof["supporting_assertion_ids"]) != len(set(proof["supporting_assertion_ids"])) or any(not isinstance(item, str) or not item for item in proof["supporting_assertion_ids"]):
                raise ValueError("v3 OCR equivalence: invalid reviewed canonical proof")
            source_path = f"outputs/04-visual-merge-bundle/visual/original_pipeline_txt/pages/page-{page:03}.png"
            if not isinstance(row["source_visual"], dict) or row["source_visual"].get("path") != source_path:
                raise ValueError("v3 OCR equivalence: source visual must be matching original_pipeline_txt page")
            _visual_evidence(row["source_visual"], visual_inventory, "OCR reviewed source")
            named = set(proof["supporting_assertion_ids"])
            anchored = [item for item in assertion_proofs if item.get("anchor_unit") == _public_unit(canonical)]
            anchored_by_id = {item["assertion_id"]: item for item in anchored}
            missing = sorted(named - set(anchored_by_id))
            if missing:
                raise ValueError(f"v3 OCR equivalence class {row['class_id']!r}: named support is absent or anchored elsewhere: {missing}")
            # Positional assertions remain independently audited as complete
            # reader text. Only the selector's explicit IDs contribute to an
            # OCR canonical proof; adjacency alone does not make an inserted
            # neighbouring handout/row a correction of the canonical unit.
            supporting = sorted((anchored_by_id[item] for item in named), key=lambda item: item["markdown_span"])
            canonical_span = mappings_by_key[_unit_key(canonical)]["markdown_span"]
            spans = sorted([item["markdown_span"] for item in supporting] + [canonical_span])
            cursor = spans[0][0] if spans else canonical_span[0]
            for start, end in spans:
                if start != cursor or end <= start:
                    raise ValueError("v3 OCR equivalence: canonical proof has gap or overlap")
                cursor = end
            proof_text = rendered[spans[0][0]:spans[-1][1]]
            if proof["expected_normalized_sha256"] != _sha(proof_text.encode()):
                raise ValueError("v3 OCR equivalence: canonical proof hash mismatch")
        alternates = row["alternate_units"]
        if not isinstance(alternates, list) or not 1 <= len(alternates) <= 2:
            raise ValueError("v3 OCR equivalence: one or two alternates required")
        views, metrics_rows = set(), []
        for value in alternates:
            alternate = _exact_unit(value, references, page, f"OCR alternate class_id={row['class_id']!r}"); key = _unit_key(alternate)
            if key in selected_keys or key in members or alternate["view_id"] == canonical["view_id"] or alternate["view_id"] in views:
                raise ValueError("v3 OCR equivalence: alternate membership/view conflict")
            selected_as_reader = any(item.get("view") == canonical["view_id"] and item.get("raw_index") == canonical["raw_index"] and item.get("purpose") in {"text", "structure"} for item in decision["selected_blocks"])
            forbidden = {"image", "page_number"} if reviewed and policy == "reviewed_visual_full_unit_any_cpu_view_v1" and selected_as_reader else {"image", "page_number", "header", "footer"}
            if canonical["block_type"] in forbidden or alternate["block_type"] in forbidden:
                raise ValueError("v3 OCR equivalence: reader text types required")
            spatial = _spatial_metrics(canonical, alternate, geometry)
            left, right = _tokens(canonical["_text"]), _tokens(alternate["_text"])
            differences = [(a, b) for a, b in zip(left, right) if a != b]
            string_distance = _levenshtein(canonical["_normalized"], alternate["_normalized"])
            similarity = difflib.SequenceMatcher(a=canonical["_normalized"], b=alternate["_normalized"], autojunk=False).ratio()
            token_distance = _levenshtein(*differences[0]) if len(differences) == 1 else 999
            strict = len(left) == len(right) and len(differences) == 1 and token_distance <= V3_POLICY["ocr_max_token_levenshtein"] and string_distance <= V3_POLICY["ocr_max_string_levenshtein"] and similarity >= V3_POLICY["ocr_min_similarity"] and spatial["iou"] >= V3_POLICY["ocr_min_iou"] and spatial["center_distance"] <= V3_POLICY["ocr_max_center_distance"]
            if reviewed:
                if strict and canonical["view_id"] == "original_pipeline_txt":
                    errors.append(f"page {page}: reviewed OCR equivalence is unnecessary {row['class_id']}:{alternate['view_id']}:{alternate['raw_index']}")
                if policy == "reviewed_exact_raw_text_geometry_drift_v1":
                    if _exact_equivalent(alternate, context, geometry) is not None: errors.append(f"page {page}: exact geometry review is unnecessary {row['class_id']}")
                    geometry_ok = canonical["_normalized"] == alternate["_normalized"] == proof_text and not supporting and spatial["smaller_box_coverage"] >= V3_POLICY["subspan_min_smaller_box_coverage"]
                    for other in context["selected"]:
                        if _unit_key(other) != _unit_key(canonical) and _unit_key(other) in mappings_by_key and _spatial_metrics(other, alternate, geometry)["smaller_box_coverage"] > V3_POLICY["subspan_max_other_box_overlap"]: geometry_ok = False
                elif supporting: geometry_ok = spatial["smaller_box_coverage"] >= V3_POLICY["subspan_min_smaller_box_coverage"] and spatial["center_distance"] <= V3_POLICY["ocr_max_center_distance"]
                else: geometry_ok = spatial["iou"] >= V3_POLICY["ocr_min_iou"] and spatial["center_distance"] <= V3_POLICY["ocr_max_center_distance"]
                if not geometry_ok: errors.append(f"page {page}: reviewed OCR equivalence geometry failed {row['class_id']}:{alternate['view_id']}:{alternate['raw_index']}")
            elif not strict: errors.append(f"page {page}: OCR equivalence bounds failed {row['class_id']}:{alternate['view_id']}:{alternate['raw_index']}")
            views.add(alternate["view_id"]); metrics = {**spatial, "token_levenshtein": token_distance, "string_levenshtein": string_distance, "similarity": round(similarity, 9)}; members[key] = (row["class_id"], metrics); metrics_rows.append({"unit": _public_unit(alternate), **metrics})
        _visual_evidence(row["visual"], visual_inventory, "OCR equivalence")
        if (not reviewed and row["visual_verdict"] != "canonical_text_visible_alternate_text_absent") or not isinstance(row["rationale"], str) or not row["rationale"].strip():
            raise ValueError("v3 OCR equivalence: verdict or rationale mismatch")
        used.add(index); reports.append({"class_id": row["class_id"], "canonical_unit": _public_unit(canonical), "alternates": metrics_rows, "visual": copy_json(row["visual"]), "equivalence_policy": row.get("equivalence_policy", V3_POLICY["ocr_equivalence_policy"]), "canonical_proof": copy_json(row.get("canonical_proof"))})
    return members, reports, used


def _reviewed_coverage_projection(claim, canonical_unit, context, visible, mapping):
    """Rebind a full-owner claim through corrections already proved by _v3_context.

    This preserves the predecessor claim and refuses partial owner intervals.
    An unchanged owner can still move when an earlier corrected block changes size.
    """
    from kb_creator.pipeline.reader_text_coverage import normalized_text, sha256
    from kb_creator.pipeline.identity import canonical_bytes, sha256_bytes

    projected = context.get("reviewed_reader_projections", {}).get(_unit_key(canonical_unit))
    if projected is None or mapping is None:
        return None
    original = normalized_text(canonical_unit["_text"])
    span = claim["proof"]["normalized_span"]
    if (claim["proof"]["expected_normalized_sha256"] != sha256(original)
            or span[1] - span[0] != len(original)):
        raise ValueError(f"reader coverage claim {claim['claim_id']} corrected partial owner is unsupported")
    target = normalized_text(projected)
    hits = []
    if target:
        for match in re.finditer(re.escape(target), visible):
            candidate = [match.start(), match.end()]
            audit_span = [len(_normalized(visible[:value])) for value in candidate]
            if audit_span == mapping["markdown_span"]:
                hits.append(candidate)
    if len(hits) != 1:
        raise ValueError(f"reader coverage claim {claim['claim_id']} corrected owner is absent or ambiguous")
    return {
        "policy": "reviewed_full_owner_coverage_v1",
        "predecessor_claim_sha256": sha256_bytes(canonical_bytes(claim)),
        "canonical_raw_text_sha256": claim["canonical_unit"]["raw_text_sha256"],
        "predecessor_normalized_span": list(span),
        "reader_normalized_span": hits[0],
        "reader_normalized_sha256": sha256(target),
        "decision_markdown_sha256": sha256(context["decision"]["markdown"]),
        "corrections_sha256": sha256_bytes(canonical_bytes(context["decision"]["reviewed_block_corrections"])),
    }


def _reader_coverage_claim_index(claims: list[dict[str, Any]] | None, contexts: dict[int, dict[str, Any]],
                                 successor_dispositions: dict[str, dict[str, Any]] | None = None) -> dict[tuple[int, str, int], dict[str, Any]]:
    """Check re-derived coverage against final packet and visible reader state."""
    if claims is None:
        return {}
    from kb_creator.pipeline.reader_text_coverage import ReaderTextCoverageError, normalized_text, sha256, validate_claims
    from kb_creator.pipeline.reader_text_coverage_binding import _visible_reader
    try:
        validate_claims(claims)
    except ReaderTextCoverageError as error:
        raise ValueError(f"reader coverage claims are invalid: {error}") from error
    result = {}
    for wrapped in claims:
        claim = wrapped["claim"]; source, canonical = claim["source_unit"], claim["canonical_unit"]
        source_key = (source["source_page"], source["view_id"], source["raw_index"])
        canonical_key = (canonical["source_page"], canonical["view_id"], canonical["raw_index"])
        source_context, reader_context = contexts.get(source_key[0]), contexts.get(claim["reader_page"])
        if source_context is None or reader_context is None or claim["reader_page"] not in {source_key[0], source_key[0] - 1}:
            raise ValueError(f"reader coverage claim {claim['claim_id']} has a stale page binding")
        source_unit = next((unit for unit in source_context["units"] if _unit_key(unit)[:3] == source_key), None)
        canonical_unit = next((unit for unit in reader_context["selected"] if _unit_key(unit)[:3] == canonical_key), None)
        if source_unit is None or canonical_unit is None or any((_unit_key(unit)[:3] == source_key for unit in source_context["selected"])):
            raise ValueError(f"reader coverage claim {claim['claim_id']} selection ownership is stale")
        def same(unit, expected):
            return unit["block_type"] == expected["block_type"] and unit["bbox"] == expected["bbox"] and unit["_text"] == expected["text"] and _sha(unit["_text"].encode()) == expected["raw_text_sha256"]
        if not same(source_unit, source) or not same(canonical_unit, canonical):
            raise ValueError(f"reader coverage claim {claim['claim_id']} packet identity is stale")
        span = claim["proof"]["normalized_span"]
        visible = normalized_text(_visible_reader(reader_context["decision"]["markdown"]))
        mapping = reader_context["mappings_by_key"].get(_unit_key(canonical_unit))
        disposition = (successor_dispositions or {}).get(claim["claim_id"])
        correction_disposition = None
        expected = claim["proof"]["expected_normalized_sha256"]
        if disposition is not None:
            from kb_creator.pipeline.identity import canonical_bytes, sha256_bytes
            if (disposition.get("predecessor_claim_sha256") != sha256_bytes(canonical_bytes(claim))
                    or disposition.get("r0_normalized_span") != span
                    or disposition.get("r0_normalized_sha256") != expected
                    or disposition.get("r1_reader_sha256") != sha256_bytes(visible.encode())):
                raise ValueError(f"reader coverage claim {claim['claim_id']} successor binding is stale")
            span = disposition["r1_normalized_span"]
            expected = disposition["r1_normalized_sha256"]
        elif (reader_context.get("reviewed_reader_projections")
              and not (mapping is not None and isinstance(span, list) and len(span) == 2
                       and all(type(value) is int for value in span)
                       and 0 <= span[0] < span[1] <= len(visible)
                       and mapping["markdown_span"][0] <= len(_normalized(visible[:span[0]]))
                       < len(_normalized(visible[:span[1]])) <= mapping["markdown_span"][1]
                       and sha256(visible[span[0]:span[1]]) == expected)):
            correction_disposition = _reviewed_coverage_projection(
                claim, canonical_unit, reader_context, visible, mapping)
            if correction_disposition is not None:
                span = correction_disposition["reader_normalized_span"]
                expected = correction_disposition["reader_normalized_sha256"]
        if not isinstance(span, list) or len(span) != 2 or span[0] < 0 or span[0] >= span[1] or span[1] > len(visible) or mapping is None:
            raise ValueError(f"reader coverage claim {claim['claim_id']} reader span is stale")
        audit_span = [len(_normalized(visible[:span[0]])), len(_normalized(visible[:span[1]]))]
        if not (mapping["markdown_span"][0] <= audit_span[0] < audit_span[1] <= mapping["markdown_span"][1]) or sha256(visible[span[0]:span[1]]) != expected:
            raise ValueError(f"reader coverage claim {claim['claim_id']} reader proof is stale")
        result[source_key] = {**claim, "audit_normalized_span": audit_span, "current_reader_normalized_span": span,
                             **({"reviewed_correction_disposition": correction_disposition} if correction_disposition is not None else {}),
                             **({"source_choice_disposition": disposition} if disposition is not None else {})}
    return result


def _resolved_source_choice_keys(decisions: dict[int, dict[str, Any]], *, ledger_contexts=None, ledger_owner=None) -> set[tuple[int, str, int]]:
    """Reopen each v2 ledger-backed R1 choice before accounting its raw witnesses.

    A resolved source choice is not a visual exemption.  It only accounts the
    exact raw alternatives sealed for that issue after the R1 decision proves
    the selected reader anchor and intended reader replacement.
    """
    from kb_creator.pipeline.identity import file_identity, sha256_bytes
    from kb_creator.pipeline.source_choice_translation import verify_ledger_v2

    resolved: set[tuple[int, str, int]] = set()
    for page, decision in decisions.items():
        rows = decision.get("linguistic_source_choice_corrections", [])
        if not isinstance(rows, list):
            raise ValueError(f"page {page}: linguistic source choices must be a list")
        for row in rows:
            expected = {"authority", "ledger", "issue_id", "alternative_id", "view", "raw_index",
                        "raw_text_sha256", "page_reader_span", "reader_anchor", "reader_preimage",
                        "reader_replacement", "selected_raw_text_sha256"}
            if not isinstance(row, dict) or set(row) != expected or row.get("authority") != "linguistic_source_choice":
                continue
            ledger_record = row["ledger"]
            if not isinstance(ledger_record, dict) or set(ledger_record) != {"path", "bytes", "sha256"}:
                raise ValueError(f"page {page}: v2 linguistic ledger identity is malformed")
            ledger_path = Path(ledger_record["path"])
            if not ledger_path.is_file() or file_identity(ledger_path) != {key: ledger_record[key] for key in ("bytes", "sha256")}:
                raise ValueError(f"page {page}: v2 linguistic ledger identity drift")
            try:
                if ledger_contexts is None:
                    verified = verify_ledger_v2(ledger_path)
                    ledger = json.loads(ledger_path.read_text(encoding="utf-8"))
                    queue = json.loads(Path(verified["queue"]).read_text(encoding="utf-8"))
                else:
                    verified, ledger, queue = ledger_contexts.audit_values_v2(ledger_owner, ledger_path)
            except ValueError as error:
                raise ValueError(f"page {page}: v2 linguistic ledger is invalid: {error}") from error
            choice = next((item for item in ledger["source_choices"] if item.get("issue_id") == row["issue_id"]), None)
            queue_choice = next((item for item in queue["choices"] if item.get("issue_id") == row["issue_id"]), None)
            if (not isinstance(choice, dict) or not isinstance(queue_choice, dict)
                    or queue_choice.get("source_page") != page or choice.get("disposition") != "selected_alternative"
                    or choice.get("alternative_id") != row["alternative_id"]
                    or choice.get("r0_reader_span") != row["page_reader_span"]
                    or choice.get("reader_anchor") != row["reader_anchor"]
                    or choice.get("chosen_raw_alternative", {}).get("text_sha256") != row["selected_raw_text_sha256"]
                    or queue_choice.get("reader_projection", {}).get("reader_text") != row["reader_preimage"]
                    or choice.get("intended_reader_successor", {}).get("text") != row["reader_replacement"]
                    or sha256_bytes(row["reader_preimage"].encode()) != choice.get("r0_reader_span", {}).get("text_sha256")
                    or sha256_bytes(row["reader_replacement"].encode()) != choice.get("intended_reader_successor", {}).get("text_sha256")):
                raise ValueError(f"page {page}: v2 linguistic source choice differs from sealed ledger")
            for alternative in queue_choice.get("alternatives", []):
                locator = alternative.get("source_locator") if isinstance(alternative, dict) else None
                if (not isinstance(locator, dict) or set(locator) != {"view", "raw_index", "field"}
                        or locator.get("field") != "text" or not isinstance(locator.get("view"), str)
                        or type(locator.get("raw_index")) is not int):
                    raise ValueError(f"page {page}: v2 source alternative locator is malformed")
                resolved.add((page, locator["view"], locator["raw_index"]))
    return resolved


def _linguistic_source_choice_proofs(page: int, decision: dict[str, Any], mappings: list[dict[str, Any]], *, ledger_contexts=None, ledger_owner=None, structural_context=None) -> list[dict[str, Any]]:
    """Replace selected rows with sealed direct or composite R1 lexical proofs.

    A composite replay owns the complete selected container.  Its individual
    ledger choices are diagnostic witnesses only; emitting one row per slice
    would falsely make a slice look like selected-source provenance.
    """
    from kb_creator.pipeline.identity import canonical_bytes, file_identity, sha256_bytes
    from kb_creator.pipeline.source_choice_translation import verify_ledger_v2
    from kb_creator.pipeline.semantic_structure import _normalized

    result = list(mappings)
    direct_rows: list[tuple[int, dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any]]] = []
    composite: dict[tuple[str, int], list[tuple[dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any]]]] = {}
    ledgers: dict[Path, tuple[dict[str, Any], dict[str, Any]]] = {}
    for correction in decision.get("linguistic_source_choice_corrections", []):
        expected = {"authority", "ledger", "issue_id", "alternative_id", "view", "raw_index",
                    "raw_text_sha256", "page_reader_span", "reader_anchor", "reader_preimage",
                    "reader_replacement", "selected_raw_text_sha256"}
        if not isinstance(correction, dict) or set(correction) != expected or correction.get("authority") != "linguistic_source_choice":
            continue
        key = correction["view"], correction["raw_index"]
        matches = [index for index, row in enumerate(result)
                   if row.get("kind") == "selected"
                   and (row.get("unit", {}).get("view_id"), row.get("unit", {}).get("raw_index")) == key]
        if len(matches) != 1:
            raise ValueError(f"page {page}: linguistic source choice lacks one selected proof row")
        ledger_record = correction["ledger"]
        ledger_path = Path(ledger_record["path"]).resolve()
        if not ledger_path.is_file() or file_identity(ledger_path) != {name: ledger_record[name] for name in ("bytes", "sha256")}:
            raise ValueError(f"page {page}: linguistic source choice ledger identity drift")
        if ledger_path not in ledgers:
            if ledger_contexts is None:
                ledgers[ledger_path] = (verify_ledger_v2(ledger_path), json.loads(ledger_path.read_text(encoding="utf-8")))
            else:
                verified, ledger, _ = ledger_contexts.audit_values_v2(ledger_owner, ledger_path)
                ledgers[ledger_path] = (verified, ledger)
        verified, ledger = ledgers[ledger_path]
        choice = next((row for row in ledger["source_choices"] if row.get("issue_id") == correction["issue_id"]), None)
        if (not isinstance(choice, dict) or choice.get("disposition") != "selected_alternative"
                or choice.get("alternative_id") != correction["alternative_id"]
                or choice.get("chosen_raw_alternative", {}).get("text_sha256") != correction["selected_raw_text_sha256"]
                or choice.get("r0_reader_span") != correction["page_reader_span"]
                or choice.get("reader_anchor") != correction["reader_anchor"]
                or choice.get("raw_reader_replay") is None):
            raise ValueError(f"page {page}: linguistic source choice differs from sealed ledger")
        locator = choice["chosen_raw_alternative"].get("source_locator")
        anchor = choice["raw_reader_replay"].get("anchor_source_locator")
        successor = choice.get("intended_reader_successor", {})
        mapping = result[matches[0]]
        if (not isinstance(locator, dict) or not isinstance(anchor, dict)
                or anchor.get("view") != key[0] or anchor.get("raw_index") != key[1]
                or not isinstance(successor.get("text"), str)
                or successor.get("text") != correction["reader_replacement"]
                or successor.get("text_sha256") != sha256_bytes(successor["text"].encode())):
            raise ValueError(f"page {page}: linguistic source choice locator or successor is stale")
        replay = choice["raw_reader_replay"]
        if replay.get("anchor_mode") == "composite_source_slice_v1":
            interval = replay.get("raw_source_slice")
            if (not isinstance(interval, dict) or set(interval) != {"raw_character_start", "raw_character_end", "raw_text_sha256"}
                    or type(interval["raw_character_start"]) is not int or type(interval["raw_character_end"]) is not int):
                raise ValueError(f"page {page}: composite linguistic source interval is malformed")
            composite.setdefault(key, []).append((correction, choice, mapping, verified))
            continue
        direct_rows.append((matches[0], correction, choice, mapping, verified))

    composite_keys = set(composite)
    if any((mapping["unit"].get("view_id"), mapping["unit"].get("raw_index")) in composite_keys
           for _, _, _, mapping, _ in direct_rows):
        raise ValueError(f"page {page}: direct and composite linguistic choices share one selected container")
    direct_seen = set()
    for index, correction, choice, mapping, verified in direct_rows:
        if index in direct_seen:
            raise ValueError(f"page {page}: direct linguistic selected mapping is duplicated")
        direct_seen.add(index)
        successor = choice["intended_reader_successor"]
        anchor = choice["raw_reader_replay"]["anchor_source_locator"]
        locator = choice["chosen_raw_alternative"]["source_locator"]
        ledger_record = correction["ledger"]
        span = mapping["markdown_span"]
        result[index] = {
            "kind": "linguistic_source_choice_v1", "unit": mapping["unit"], "markdown_span": span,
            "r1_span": span, "r1_text": successor["text"], "r1_text_sha256": successor["text_sha256"],
            "r0_anchor_source_key": {"view": anchor["view"], "raw_index": anchor["raw_index"]},
            "r0_preimage_sha256": choice["raw_reader_replay"]["r0_preimage_sha256"],
            "selected_raw_locator": locator, "selected_raw_text_sha256": correction["selected_raw_text_sha256"],
            "issue_id": correction["issue_id"], "alternative_id": correction["alternative_id"],
            "ledger": ledger_record, "ledger_identity": verified["ledger_sha256"],
            "raw_reader_replay": choice["raw_reader_replay"],
            "row_sha256": sha256_bytes(canonical_bytes(mapping)),
        }

    from kb_creator.pipeline.source_choice_container_proof import derive_container_proof
    for key, group in composite.items():
        if len({Path(row[0]["ledger"]["path"]).resolve() for row in group}) != 1:
            raise ValueError(f"page {page}: composite linguistic choices mix ledgers")
        mapping = group[0][2]
        record = group[0][0]["ledger"]
        verified, ledger = ledgers[Path(record["path"]).resolve()]
        proof = derive_container_proof(ledger_record=record, ledger=ledger, verified=verified,
                                       page=page, key=key, current_markdown=decision["markdown"],
                                       current_mapping=mapping, structural_context=structural_context)
        if sorted(item[0]["issue_id"] for item in group) != sorted(w["issue_id"] for w in proof["diagnostic_witnesses"]):
            raise ValueError(f"page {page}: container correction witnesses are missing, extra or duplicated")
        index = next(index for index, candidate in enumerate(result) if candidate is mapping)
        result[index] = proof
    return result


def _audit_v3_content(
    packets: dict[int, dict[str, Any]], decisions: dict[int, dict[str, Any]], *, allowlist: dict[str, Any],
    geometry: dict[str, Any], visual_inventory: dict[str, dict[str, Any]], authorities: dict[str, Any] | None = None,
    source_render_context: dict[str, Any] | None = None, reader_coverage_claims: list[dict[str, Any]] | None = None,
    coverage_successor_dispositions: dict[str, dict[str, Any]] | None = None,
    pending_source_context: dict[str, Any] | None = None,
    _ledger_contexts=None, _ledger_owner=None, _structural_context=None,
) -> dict[str, Any]:
    """Strict replay-v3 content ledger; legacy/v2 behavior remains in audit_v2_content."""
    from kb_creator.pipeline.text_segmentation import (
        ALLOWLIST_FIELD, TextSegmentationError, text_segmentation_claims, validate_claim,
    )
    if not isinstance(allowlist, dict) or allowlist.get("schema") != V3_ALLOWLIST_SCHEMA:
        raise ValueError("v3 allowlist: closed schema required")
    try:
        segmentation_claims = text_segmentation_claims(allowlist)
    except TextSegmentationError as error:
        raise ValueError(str(error)) from error
    if allowlist["substitutions"]:
        raise ValueError("v3 allowlist: substitutions are unsupported")
    errors, page_reports, used_exclusions, used_assertions, used_classes, used_segmentation, used_coverage = [], [], set(), set(), set(), set(), set()
    contexts = {
        page: _v3_page_context(page, packets[page], decisions.get(page), geometry, errors)
        for page in sorted(packets)
    }
    coverage_claims = _reader_coverage_claim_index(reader_coverage_claims, contexts, coverage_successor_dispositions)
    resolved_source_keys = _resolved_source_choice_keys(decisions, ledger_contexts=_ledger_contexts, ledger_owner=_ledger_owner)
    pending_source_keys: set[tuple[int, str, int]] = set()
    if pending_source_context is not None:
        if set(pending_source_context) != {"review_input", "input_path", "binding_root", "run_root"}:
            raise ValueError("pending source context is malformed")
        from kb_creator.pipeline.pending_source_choices import (
            PendingSourceChoiceError, derive_pending_source_keys,
        )
        selected = {(page, item["view"], item["raw_index"])
                    for page, decision in decisions.items() for item in decision["selected_blocks"]
                    if item.get("purpose") != "asset"}
        try:
            pending_source_keys = derive_pending_source_keys(
                review_input=pending_source_context["review_input"],
                input_path=Path(pending_source_context["input_path"]),
                binding_root=Path(pending_source_context["binding_root"]),
                run_root=Path(pending_source_context["run_root"]), selected_keys=selected,
                coverage_owner_keys=set(coverage_claims),
            )
        except PendingSourceChoiceError as error:
            raise ValueError(f"pending source authority is invalid: {error}") from error
    running_furniture = _reviewed_running_furniture(
        allowlist["source_text_exclusions"], contexts, geometry, visual_inventory,
        allowlist["visual_text_assertions"], allowlist["ocr_equivalence_classes"],
    )
    previous_last = None
    for page in sorted(packets):
        context = contexts[page]
        units, references = context["units"], context["references"]
        selected, selected_keys = context["selected"], context["selected_keys"]
        rendered = context["rendered"]
        mappings, mappings_by_key = context["mappings"], context["mappings_by_key"]
        assertion_rows = allowlist["visual_text_assertions"]
        assertion_proofs = _v3_assertions(page, assertion_rows, units, references, selected_keys, mappings_by_key, rendered, geometry, visual_inventory, errors, used_assertions, packets[page], decisions[page])
        class_members, class_reports, scoped_used = _v3_ocr_class_proofs(
            page, context, allowlist["ocr_equivalence_classes"], assertion_proofs,
            geometry, visual_inventory, errors, decisions[page],
        )
        used_classes |= scoped_used
        for class_index, row in enumerate(()) :
            bounded_keys = {"class_id", "source_page", "canonical_unit", "alternate_units", "visual", "visual_verdict", "rationale"}
            reviewed_keys = bounded_keys | {"equivalence_policy", "source_visual", "canonical_proof"}
            if not isinstance(row, dict) or (set(row) != bounded_keys and set(row) != reviewed_keys):
                raise ValueError("v3 allowlist: invalid closed OCR equivalence class")
            if row["source_page"] != page:
                continue
            reviewed = set(row) == reviewed_keys
            canonical = _exact_unit(row["canonical_unit"], references, page, "OCR canonical")
            if _unit_key(canonical) not in selected_keys or _unit_key(canonical) not in mappings_by_key:
                raise ValueError("v3 OCR equivalence: canonical unit is not selected and mapped")
            policy = row.get("equivalence_policy")
            if not reviewed or policy == "reviewed_visual_full_unit_v1":
                if canonical["view_id"] != "original_pipeline_txt":
                    raise ValueError("v3 OCR equivalence: canonical must use original_pipeline_txt")
            elif policy not in {"reviewed_visual_full_unit_any_cpu_view_v1", "reviewed_exact_raw_text_geometry_drift_v1"} or canonical["view_id"] not in REQUIRED_CPU_VIEWS:
                raise ValueError("v3 OCR equivalence: reviewed canonical must use a required CPU view")
            supporting_assertions = []
            if reviewed:
                if policy not in {"reviewed_visual_full_unit_v1", "reviewed_visual_full_unit_any_cpu_view_v1", "reviewed_exact_raw_text_geometry_drift_v1"} or row["visual_verdict"] != "canonical_proof_complete_for_region_alternates_are_ocr_corruption":
                    raise ValueError("v3 OCR equivalence: reviewed policy or verdict mismatch")
                proof = row["canonical_proof"]
                if not isinstance(proof, dict) or set(proof) != {"supporting_assertion_ids", "expected_normalized_sha256"} or not isinstance(proof["supporting_assertion_ids"], list) or len(proof["supporting_assertion_ids"]) != len(set(proof["supporting_assertion_ids"])) or any(not isinstance(item, str) or not item for item in proof["supporting_assertion_ids"]):
                    raise ValueError("v3 OCR equivalence: invalid reviewed canonical proof")
                source_path = f"outputs/04-visual-merge-bundle/visual/original_pipeline_txt/pages/page-{page:03}.png"
                if not isinstance(row["source_visual"], dict) or row["source_visual"].get("path") != source_path:
                    raise ValueError("v3 OCR equivalence: source visual must be matching original_pipeline_txt page")
                _visual_evidence(row["source_visual"], visual_inventory, "OCR reviewed source")
                named = set(proof["supporting_assertion_ids"])
                anchored = [item for item in assertion_proofs if item.get("anchor_unit") == _public_unit(canonical)]
                if named != {item["assertion_id"] for item in anchored}:
                    raise ValueError("v3 OCR equivalence: canonical proof assertion membership mismatch")
                supporting_assertions = sorted(anchored, key=lambda item: item["markdown_span"])
                canonical_span = mappings_by_key[_unit_key(canonical)]["markdown_span"]
                spans = sorted([item["markdown_span"] for item in supporting_assertions] + [canonical_span])
                cursor = spans[0][0] if spans else canonical_span[0]
                for start, end in spans:
                    if start != cursor or end <= start:
                        raise ValueError("v3 OCR equivalence: canonical proof has gap or overlap")
                    cursor = end
                proof_text = rendered[spans[0][0]:spans[-1][1]]
                if proof["expected_normalized_sha256"] != _sha(proof_text.encode()):
                    raise ValueError("v3 OCR equivalence: canonical proof hash mismatch")
            alternates = row["alternate_units"]
            if not isinstance(alternates, list) or not 1 <= len(alternates) <= 2:
                raise ValueError("v3 OCR equivalence: one or two alternates required")
            alternate_views, metrics_rows = set(), []
            for alternate_value in alternates:
                alternate = _exact_unit(alternate_value, references, page, "OCR alternate")
                key = _unit_key(alternate)
                if key in selected_keys or key in class_members or alternate["view_id"] == canonical["view_id"] or alternate["view_id"] in alternate_views:
                    raise ValueError("v3 OCR equivalence: alternate membership/view conflict")
                selected_as_reader = any(
                    item.get("view") == canonical["view_id"] and item.get("raw_index") == canonical["raw_index"]
                    and item.get("purpose") in {"text", "structure"}
                    for item in decisions[page]["selected_blocks"]
                )
                forbidden_types = {"image", "page_number"} if (
                    reviewed and row.get("equivalence_policy") == "reviewed_visual_full_unit_any_cpu_view_v1"
                    and selected_as_reader
                ) else {"image", "page_number", "header", "footer"}
                if canonical["block_type"] in forbidden_types or alternate["block_type"] in forbidden_types:
                    raise ValueError("v3 OCR equivalence: reader text types required")
                spatial = _spatial_metrics(canonical, alternate, geometry)
                left_tokens, right_tokens = _tokens(canonical["_text"]), _tokens(alternate["_text"])
                differences = [(left, right) for left, right in zip(left_tokens, right_tokens) if left != right]
                string_distance = _levenshtein(canonical["_normalized"], alternate["_normalized"])
                similarity = difflib.SequenceMatcher(a=canonical["_normalized"], b=alternate["_normalized"], autojunk=False).ratio()
                token_distance = _levenshtein(*differences[0]) if len(differences) == 1 else 999
                strict_bounds = len(left_tokens) == len(right_tokens) and len(differences) == 1 and token_distance <= V3_POLICY["ocr_max_token_levenshtein"] and string_distance <= V3_POLICY["ocr_max_string_levenshtein"] and similarity >= V3_POLICY["ocr_min_similarity"] and spatial["iou"] >= V3_POLICY["ocr_min_iou"] and spatial["center_distance"] <= V3_POLICY["ocr_max_center_distance"]
                if reviewed:
                    # A reviewed any-CPU decision may need a non-TXT canonical
                    # unit because the TXT view contains the OCR corruption.
                    # The strict comparison is redundant only when the base
                    # TXT-canonical policy could express this same selection.
                    if strict_bounds and canonical["view_id"] == "original_pipeline_txt":
                        errors.append(f"page {page}: reviewed OCR equivalence is unnecessary {row['class_id']}:{alternate['view_id']}:{alternate['raw_index']}")
                    if policy == "reviewed_exact_raw_text_geometry_drift_v1":
                        if _exact_equivalent(alternate, context, geometry) is not None:
                            errors.append(f"page {page}: exact geometry review is unnecessary {row['class_id']}")
                        geometry_ok = (
                            canonical["_normalized"] == alternate["_normalized"] == proof_text
                            and not supporting_assertions
                            and spatial["smaller_box_coverage"] >= V3_POLICY["subspan_min_smaller_box_coverage"]
                        )
                        for other in context["selected"]:
                            if _unit_key(other) != _unit_key(canonical) and _unit_key(other) in mappings_by_key and _spatial_metrics(other, alternate, geometry)["smaller_box_coverage"] > V3_POLICY["subspan_max_other_box_overlap"]:
                                geometry_ok = False
                    elif supporting_assertions:
                        geometry_ok = spatial["smaller_box_coverage"] >= V3_POLICY["subspan_min_smaller_box_coverage"] and spatial["center_distance"] <= V3_POLICY["ocr_max_center_distance"]
                    else:
                        geometry_ok = spatial["iou"] >= V3_POLICY["ocr_min_iou"] and spatial["center_distance"] <= V3_POLICY["ocr_max_center_distance"]
                    if not geometry_ok:
                        errors.append(f"page {page}: reviewed OCR equivalence geometry failed {row['class_id']}:{alternate['view_id']}:{alternate['raw_index']}")
                elif not strict_bounds:
                    errors.append(f"page {page}: OCR equivalence bounds failed {row['class_id']}:{alternate['view_id']}:{alternate['raw_index']}")
                alternate_views.add(alternate["view_id"]); class_members[key] = (row["class_id"], {**spatial, "token_levenshtein": token_distance, "string_levenshtein": string_distance, "similarity": round(similarity, 9)})
                metrics_rows.append({"unit": _public_unit(alternate), **class_members[key][1]})
            _visual_evidence(row["visual"], visual_inventory, "OCR equivalence")
            if (not reviewed and row["visual_verdict"] != "canonical_text_visible_alternate_text_absent") or not isinstance(row["rationale"], str) or not row["rationale"].strip():
                raise ValueError("v3 OCR equivalence: verdict or rationale mismatch")
            used_classes.add(class_index); class_reports.append({"class_id": row["class_id"], "canonical_unit": _public_unit(canonical), "alternates": metrics_rows, "visual": copy_json(row["visual"]), "equivalence_policy": row.get("equivalence_policy", V3_POLICY["ocr_equivalence_policy"]), "canonical_proof": copy_json(row.get("canonical_proof"))})
        segmentation_members: dict[tuple[Any, ...], dict[str, Any]] = {}
        segmentation_spans: dict[str, list[list[int]]] = collections.defaultdict(list)
        for claim_index, claim in enumerate(segmentation_claims):
            if not isinstance(claim, dict) or claim.get("source_page") != page:
                continue
            references3 = {(page, view, index): unit for (view, index), unit in references.items()}
            mappings3 = {(page, unit["view_id"], unit["raw_index"]): mapping for unit_key, mapping in mappings_by_key.items() for unit in [next(item for item in selected if _unit_key(item) == unit_key)]}
            protected = {(page, unit["view_id"], unit["raw_index"]) for key in class_members for unit in [next(item for item in units if _unit_key(item) == key)]}
            protected |= {(page, unit["view_id"], unit["raw_index"]) for index, row in enumerate(allowlist["source_text_exclusions"]) if isinstance(row, dict) and (unit := _unit_from_allowlist(row.get("unit"), contexts)) is not None}
            protected |= {(page, unit["view_id"], unit["raw_index"]) for unit in units if _unit_key(unit) in segmentation_members}
            try:
                validated = validate_claim(claim, references=references3, selected_mappings=mappings3, reader_text=rendered, visual_inventory=visual_inventory, normalize=_normalized, spatial_metrics=lambda left, right: _spatial_metrics(left, right, geometry), protected_members=protected, automatic_disposition=lambda unit: _exact_equivalent(unit, context, geometry) or _strict_subspan_equivalent(unit, context, geometry))
            except TextSegmentationError as error:
                raise ValueError(f"page {page}: {error}") from error
            alternate_view = validated["alternates"][0]["view_id"]
            claim_start, claim_end = validated["proof"]["normalized_span"]
            if any(claim_start < end and claim_end > start for start, end in segmentation_spans[alternate_view]):
                raise ValueError(f"page {page}: overlapping segmentation claims in one alternate view")
            segmentation_spans[alternate_view].append([claim_start, claim_end])
            for unit_value in validated["alternates"]:
                unit = _unit_from_allowlist(unit_value, contexts)
                if unit is None:
                    raise ValueError("segmentation alternate identity is stale")
                segmentation_members[_unit_key(unit)] = {"claim_id": validated["claim_id"], "proof": validated["proof"], "layout_relation": validated["layout_relation"]}
            used_segmentation.add(claim_index)
        dispositions, unaccounted = [], 0
        equivalent_claims: set[tuple[Any, ...]] = set()
        subspan_claims: dict[str, list[tuple[int, int]]] = collections.defaultdict(list)
        for unit in units:
            key = _unit_key(unit)
            exclusion_matches = [(index, row) for index, row in enumerate(allowlist["source_text_exclusions"]) if isinstance(row, dict) and row.get("unit") == _public_unit(unit)]
            if len(exclusion_matches) > 1:
                raise ValueError("v3 allowlist: duplicate exclusion")
            if unit.get("_normalization_empty_artifact"):
                if exclusion_matches:
                    raise ValueError("v3 allowlist: normalization-empty OCR artifact must not use a source exclusion")
                disposition, detail = "excluded_normalization_empty_artifact", {
                    "classification": "safe_empty_normalization_ocr_artifact",
                }
            elif key in selected_keys:
                disposition, detail = "included_selected", None
            elif key[:3] in coverage_claims:
                claim = coverage_claims[key[:3]]
                if key in class_members or key in segmentation_members or exclusion_matches:
                    raise ValueError(f"reader coverage claim {claim['claim_id']} collides with native proof")
                used_coverage.add(claim["claim_id"])
                disposition, detail = "included_covered_by_reader", {"claim_id": claim["claim_id"], "reader_page": claim["reader_page"], "normalized_span": claim["proof"]["normalized_span"], "audit_normalized_span": claim["audit_normalized_span"]}
                if "reviewed_correction_disposition" in claim:
                    detail["reviewed_correction_disposition"] = claim["reviewed_correction_disposition"]
                    detail["current_reader_normalized_span"] = claim["current_reader_normalized_span"]
            elif key in segmentation_members:
                disposition, detail = "included_reviewed_segmentation", segmentation_members[key]
            elif key in class_members:
                class_id, metrics = class_members[key]; disposition, detail = "included_ocr_equivalent", {"class_id": class_id, "metrics": metrics}
            else:
                exact = _exact_equivalent(unit, context, geometry)
                subspan = None if exact is not None else _strict_subspan_equivalent(unit, context, geometry)
                if exact is not None:
                    disposition, detail = "included_equivalent_exact", exact
                    claim = (unit["view_id"], _unit_key(exact["canonical_unit"]), unit["_normalized"])
                    if claim in equivalent_claims:
                        errors.append(f"page {page}: duplicate exact-equivalence accounting {unit['view_id']}:{unit['raw_index']}")
                    equivalent_claims.add(claim)
                elif subspan is not None:
                    disposition, detail = "included_equivalent_exact_subspan", subspan
                    start, end = subspan["markdown_span"]
                    if any(start < seen_end and end > seen_start for seen_start, seen_end in subspan_claims[unit["view_id"]]):
                        errors.append(f"page {page}: overlapping or duplicate subspan accounting {unit['view_id']}:{unit['raw_index']}")
                    if subspan_claims[unit["view_id"]] and start < subspan_claims[unit["view_id"]][-1][0]:
                        errors.append(f"page {page}: reordered subspan accounting {unit['view_id']}:{unit['raw_index']}")
                    subspan_claims[unit["view_id"]].append((start, end))
                elif exclusion_matches:
                    index, exclusion = exclusion_matches[0]
                    if not isinstance(exclusion, dict) or set(exclusion) != {"unit", "classification", "rationale", "visual", "logical_asset"}:
                        raise ValueError("v3 allowlist: invalid closed exclusion")
                    classification = exclusion["classification"]
                    _visual_evidence(exclusion["visual"], visual_inventory, "exclusion")
                    if not isinstance(exclusion["rationale"], str) or not exclusion["rationale"].strip():
                        raise ValueError("v3 exclusion: rationale required")
                    if classification == "non_reader" and unit["block_type"] not in {"page_number", "header", "footer"} and key not in running_furniture:
                        errors.append(f"page {page}: non_reader cannot discard body unit {unit['view_id']}:{unit['raw_index']}")
                    elif classification == "ocr_artifact":
                        corresponding = [candidate for candidate in units if candidate["view_id"] != unit["view_id"] and candidate["block_type"] not in {"page_number", "header", "footer"} and _spatial_metrics(candidate, unit, geometry)["iou"] >= 0.50]
                        if corresponding:
                            errors.append(f"page {page}: ocr_artifact has geometry-corresponding reader unit {unit['view_id']}:{unit['raw_index']}")
                    elif classification not in {"visual_only", "advertisement", "decorative", "non_reader", "ocr_artifact"}:
                        raise ValueError("v3 exclusion: invalid classification")
                    used_exclusions.add(index); disposition, detail = "excluded_reviewed", {"classification": classification}
                elif (page, unit["view_id"], unit["raw_index"]) in pending_source_keys:
                    # Open alternatives only fill a conservation gap. Existing
                    # source/reader proofs and reviewed dispositions keep their
                    # provenance even when a diagnostic also names this key.
                    disposition, detail = "pending_source_choice", {"authority": "sealed_review_draft_input"}
                elif (page, unit["view_id"], unit["raw_index"]) in resolved_source_keys:
                    disposition, detail = "resolved_source_choice", {"authority": "sealed_source_choice_ledger_v2"}
                else:
                    disposition, detail = "unaccounted", None; unaccounted += 1
                    errors.append(f"page {page}: unaccounted full source unit {unit['view_id']}:{unit['raw_index']}")
            if exclusion_matches and disposition.startswith("included_"):
                errors.append(f"page {page}: included unit is also excluded {unit['view_id']}:{unit['raw_index']}")
            dispositions.append({"unit": _public_unit(unit), "disposition": disposition, "detail": detail})
        mappings = _linguistic_source_choice_proofs(page, decisions[page], mappings,
            ledger_contexts=_ledger_contexts, ledger_owner=_ledger_owner,
            structural_context=_structural_context)
        proof_stream = sorted([*mappings, *({"kind": "visual_assertion", **row} for row in assertion_proofs)], key=lambda row: row["markdown_span"])
        proof_cursor = 0
        for row in proof_stream:
            start, end = row["markdown_span"]
            if start != proof_cursor or end <= start:
                errors.append(f"page {page}: proof stream has gap, overlap, or reorder")
                break
            proof_cursor = end
        if proof_cursor != len(rendered):
            errors.append(f"page {page}: proof stream does not cover normalized Markdown exactly")
        required_chars = sum(unit["normalized_character_count"] for unit in units) + sum(span[1] - span[0] for span in (row["markdown_span"] for row in assertion_proofs))
        covered_chars = sum(unit["normalized_character_count"] for unit, disposition in zip(units, dispositions) if disposition["disposition"] != "unaccounted") + sum(span[1] - span[0] for span in (row["markdown_span"] for row in assertion_proofs))
        page_errors = [item for item in errors if item.startswith(f"page {page}:")]
        reader_units = [unit for unit, disposition in zip(units, dispositions) if disposition["disposition"].startswith("included_")]
        if previous_last is not None and reader_units:
            pass
        if reader_units:
            previous_last = (page, reader_units[-1])
        source_render_proofs = []
        for asset in decisions[page].get("assets", []):
            if not isinstance(asset, dict) or asset.get("origin") != "source_pdf_page_render_v1":
                continue
            if source_render_context is None:
                raise ValueError("v3 source-page render requires fresh source-render context")
            validate_source_page_render_row(asset, decision_page=page, expected_source_sha256=source_render_context["source_sha256"], expected_renderer_sha256=source_render_context["renderer_sha256"], markdown=decisions[page]["markdown"], page_visual_reviewed=decisions[page].get("review", {}).get("visual_reviewed") is True)
            with tempfile.TemporaryDirectory(prefix="kb-source-render-audit-") as scratch:
                actual = render_source_pdf_page(source_render_context["source"], page, source_render_context["renderer"], asset["render"]["dpi"], Path(scratch) / asset["logical_name"], expected_source_sha256=source_render_context["source_sha256"], expected_renderer_sha256=source_render_context["renderer_sha256"])
            if {key: actual[key] for key in ("recipe", "dpi", "renderer_sha256", "pixels", "bytes", "sha256")} != asset["render"]:
                raise ValueError(f"page {page}: source-page render proof mismatch")
            source_render_proofs.append({"origin": asset["origin"], "logical_name": asset["logical_name"], "source_page": page, "render": asset["render"]})
        page_reports.append({"source_page": page, "required_character_count": required_chars, "covered_character_count": covered_chars, "completeness": covered_chars / required_chars if required_chars else 1.0, "ordered_proof_stream": proof_stream, "units": dispositions, "visual_assertions": assertion_proofs, "ocr_equivalence_classes": class_reports, "source_page_renders": source_render_proofs, "unaccounted_unit_count": unaccounted, "errors": page_errors, "passed": not page_errors and unaccounted == 0 and proof_cursor == len(rendered)})
    unused_exclusions = sorted(set(range(len(allowlist["source_text_exclusions"]))) - used_exclusions)
    unused_assertions = sorted(set(range(len(allowlist["visual_text_assertions"]))) - used_assertions)
    unused_classes = sorted(set(range(len(allowlist["ocr_equivalence_classes"]))) - used_classes)
    if unused_exclusions: errors.append(f"v3 allowlist: unused source_text_exclusions {unused_exclusions}")
    if unused_assertions: errors.append(f"v3 allowlist: unused visual_text_assertions {unused_assertions}")
    unused_segmentation = sorted(set(range(len(segmentation_claims))) - used_segmentation)
    if unused_classes: errors.append(f"v3 allowlist: unused ocr_equivalence_classes {unused_classes}")
    if unused_segmentation: errors.append(f"v3 allowlist: unused text_segmentation_claims {unused_segmentation}")
    unused_coverage = sorted(value["claim_id"] for value in coverage_claims.values() if value["claim_id"] not in used_coverage)
    if unused_coverage: errors.append(f"v3 audit: unused reader coverage claims {unused_coverage}")
    return {"schema": V3_SCHEMA, "authorities": authorities or {}, "policy": V3_POLICY, "pages": page_reports, "reader_coverage_claim_count": len(coverage_claims), "errors": errors, "passed": not errors and all(row["passed"] for row in page_reports)}


def audit_v4_content(
    packets: dict[int, dict[str, Any]], decisions: dict[int, dict[str, Any]], *,
    allowlist: dict[str, Any], geometry: dict[str, Any],
    visual_inventory: dict[str, dict[str, Any]], authorities: dict[str, Any] | None = None,
    source_render_context: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Compose legacy lexical closure with the opt-in reviewed structure gate."""
    from kb_creator.pipeline.semantic_structure import SemanticStructureError, validate_semantic_structure
    legacy = audit_v3_content(packets, decisions, allowlist=allowlist, geometry=geometry, visual_inventory=visual_inventory, authorities=authorities, source_render_context=source_render_context)
    try:
        structure = validate_semantic_structure(
            decisions, packets, visual_inventory, required_pages=sorted(packets),
            visual_assertions={row["assertion_id"]: row for row in allowlist["visual_text_assertions"] if isinstance(row, dict) and isinstance(row.get("assertion_id"), str)},
        )
        errors = list(legacy["errors"])
    except SemanticStructureError as error:
        structure = {"schema": "kb_creator.reconstruction_semantic_structure.v1", "profile": decisions.get(sorted(decisions)[0], {}).get("semantic_structure", {}).get("profile", "visually_reviewed_semantic_containers_v1"), "pages": [], "structure_sha256": None}
        errors = [*legacy["errors"], f"semantic structure: {error}"]
    return {
        "schema": V4_SCHEMA, "authorities": legacy["authorities"], "policy": legacy["policy"],
        "pages": legacy["pages"], "semantic_structure_profile": structure["profile"],
        "semantic_structure": structure, "errors": errors,
        "passed": not errors and legacy["passed"],
    }


def audit_v2(decisions_root: Path, packets_root: Path, queue_path: Path, queue_sha256: str, comparison_path: Path, comparison_sha256: str, decision_set_path: Path, decision_set_sha256: str, allowlist_path: Path | None = None) -> dict[str, Any]:
    """Reopen the complete fixed v2 authority graph before auditing content."""
    repo_root = Path(__file__).resolve().parents[2]
    if str(repo_root) not in sys.path: sys.path.insert(0, str(repo_root))
    from kb_creator.pipeline import reconstruction

    queue_identity = _checked_identity(queue_path, queue_sha256, "review queue")
    comparison_identity = _checked_identity(comparison_path, comparison_sha256, "comparison")
    decision_set_identity = _checked_identity(decision_set_path, decision_set_sha256, "decision set")
    run_root = queue_path.parent.parent
    fixed = {
        "queue": run_root / "review" / "review_queue.json",
        "comparison": run_root / "outputs" / "03-compare-views" / "comparison.json",
        "packets": run_root / "outputs" / "04-visual-merge-bundle" / "merge_packets",
    }
    if queue_path.absolute() != fixed["queue"].absolute() or comparison_path.absolute() != fixed["comparison"].absolute() or packets_root.absolute() != fixed["packets"].absolute():
        raise ValueError("v2 audit authorities are not fixed run-local paths")
    _assert_no_reparse(run_root); _assert_no_reparse(packets_root, tree=True); _assert_no_reparse(decisions_root, tree=True)
    run = reconstruction.load_run(run_root)
    if run.get("schema") not in reconstruction.mineru_cpu_first.RUN_SCHEMAS:
        raise ValueError("CPU-first audit requires a supported CPU-first run schema")
    reconstruction._validate_live_run_bindings(run_root, run)
    reconstruction._validate_stage_prefix(run_root, run, reconstruction.RUN_STAGES)
    queue = reconstruction.validate_queue(queue_path, run)
    if queue.get("comparison") != {"path": "outputs/03-compare-views/comparison.json", **comparison_identity}: raise ValueError("queue comparison authority mismatch")
    comparison = _json(comparison_path, "comparison")
    if (
        comparison.get("schema") != "kb_creator.mineru_multi_view_comparison.v2"
        or comparison.get("status") != "pass_for_review"
        or comparison.get("failures") != []
        or comparison.get("required_views") != REQUIRED_CPU_VIEWS
        or comparison.get("run_identity_sha256") != run["portable_identity_sha256"]
    ):
        raise ValueError("comparison required CPU authority mismatch")
    decision_set = reconstruction.validate_decision_set(decision_set_path, queue, decisions_root.parent)
    packet_paths, decision_paths = _packet_index(packets_root), _decision_index(decisions_root, set(_packet_index(packets_root)))
    queue_rows = queue.get("items")
    if not isinstance(queue_rows, list) or len(queue_rows) != len(packet_paths): raise ValueError("queue packet coverage mismatch")
    packets, decisions = {}, {}
    for row in queue_rows:
        page = row.get("source_page"); packet_path = packet_paths.get(page)
        expected_packet = {"path": f"merge_packets/pages/page-{page:03d}.json", **_identity(packet_path)} if packet_path else None
        if expected_packet is None or row.get("merge_packet") != expected_packet: raise ValueError("queue packet identity mismatch")
        packets[page] = _json(packet_path, f"page {page} packet"); decisions[page] = _json(decision_paths[page], f"page {page} decision")
        if set(packets[page].get("views", {})) != set(comparison.get("succeeded_views", [])):
            raise ValueError("packet view domain is not the comparison projection")
        for view_id in REQUIRED_CPU_VIEWS:
            expected_blocks = [block for block in comparison["views"][view_id].get("blocks", []) if block.get("source_page") == page]
            if packets[page]["views"][view_id].get("blocks") != expected_blocks:
                raise ValueError("packet block evidence differs from comparison")
    authority = {"run_identity_sha256": run["portable_identity_sha256"], "source_sha256": run["source"]["sha256"], "contract_sha256": run["contract"]["sha256"], "review_queue_sha256": queue["queue_sha256"], "comparison_sha256": comparison_identity["sha256"]}
    allowlist, allowlist_identity = _v2_allowlist(allowlist_path, authority)
    declared = decision_set.get("reviewed_allowlist")
    if (declared is None) != (allowlist_path is None): raise ValueError("decision-set allowlist authority mismatch")
    if declared is not None and declared != {"path": allowlist_path.name, **_identity(allowlist_path)}: raise ValueError("decision-set allowlist identity mismatch")
    for row in [*allowlist.get("source_text_exclusions", []), *allowlist.get("visual_text_assertions", [])]:
        visual = row.get("visual") if isinstance(row, dict) else None
        if not isinstance(visual, dict) or set(visual) != {"path", "bytes", "sha256"}: raise ValueError("v2 allowlist visual identity is malformed")
        relative = Path(str(visual["path"]))
        visual_path = run_root / relative
        if relative.is_absolute() or ".." in relative.parts or not relative.as_posix().startswith("outputs/04-visual-merge-bundle/visual/"):
            raise ValueError("v2 allowlist visual path escapes fixed Stage04 visual evidence")
        _assert_no_reparse(visual_path)
        if not visual_path.is_file() or _identity(visual_path) != {"bytes": visual["bytes"], "sha256": visual["sha256"]}:
            raise ValueError("v2 allowlist visual identity mismatch")
        if row in allowlist.get("source_text_exclusions", []) and row.get("classification") == "visual_only":
            logical = row.get("logical_asset"); page = row.get("unit", {}).get("source_page")
            decision = decisions.get(page, {})
            assets = [asset for asset in decision.get("assets", []) if asset.get("logical_name") == logical]
            if len(assets) != 1 or f"{{{{asset:{logical}}}}}" not in decision.get("markdown", ""):
                raise ValueError("visual_only exclusion lacks a selected materialized asset")
    authorities = {
        "run": {"portable_identity_sha256": run["portable_identity_sha256"], "source_sha256": run["source"]["sha256"], "contract_sha256": run["contract"]["sha256"]},
        "review_queue": {"path_hint": "review/review_queue.json", **queue_identity, "queue_sha256": queue["queue_sha256"]},
        "comparison": {"path_hint": "outputs/03-compare-views/comparison.json", **comparison_identity},
        "decision_set": {"path_hint": "validated-submission/decision_set.json", **decision_set_identity},
        "reviewed_allowlist": allowlist_identity,
        "packets": [{"source_page": page, "path_hint": f"outputs/04-visual-merge-bundle/merge_packets/pages/page-{page:03d}.json", **_identity(packet_paths[page])} for page in sorted(packet_paths)],
    }
    return audit_v2_content(packets, decisions, allowlist=allowlist, authorities=authorities)


class _PublicAuditLedgerContexts:
    """Own fresh immutable ledger snapshots for exactly one public audit."""

    def __init__(self, owner: object) -> None:
        self._owner = owner
        self._snapshots = {}
        self._closed = False

    def _require_owner(self, owner: object) -> None:
        if owner is not self._owner or self._closed:
            raise ValueError("ledger context belongs to another or closed public audit invocation")

    def snapshot_v2(self, owner: object, ledger: Path):
        from kb_creator.pipeline.source_choice_translation import open_verified_ledger_v2_snapshot
        self._require_owner(owner)
        path = Path(ledger).resolve()
        if path not in self._snapshots:
            self._snapshots[path] = open_verified_ledger_v2_snapshot(path)
        return self._snapshots[path]

    def audit_values_v2(self, owner: object, ledger: Path):
        snapshot = self.snapshot_v2(owner, ledger)
        verified = {"ledger": str(snapshot.ledger_path), "submission": str(snapshot.submission_path),
                    "queue": str(snapshot.queue_path), "ledger_sha256": snapshot.ledger_value["ledger_sha256"],
                    "choices": len(snapshot.ledger_by_issue)}
        return verified, json.loads(snapshot.ledger_bytes), json.loads(snapshot.queue_bytes)

    def reverify_before_return(self, owner: object) -> None:
        from kb_creator.pipeline.source_choice_translation import reverify_ledger_v2_snapshot
        self._require_owner(owner)
        for snapshot in self._snapshots.values():
            reverify_ledger_v2_snapshot(snapshot)

    def close(self) -> None:
        self._closed = True
        self._snapshots.clear()


def audit_v3_content(*args, **kwargs):
    """Run one fresh source-choice ledger context across the complete audit."""
    from kb_creator.pipeline.source_choice_successor import ledger_validation_scope
    from kb_creator.pipeline.source_choice_translation import _author_ledger_snapshot_scope
    if {"_ledger_contexts", "_ledger_owner", "_structural_context"} & set(kwargs):
        raise TypeError("author audit context is private to the author audit entrypoint")
    owner = object()
    contexts = _PublicAuditLedgerContexts(owner)
    # Replace caller authority even while structural opening/closing triggers
    # nested public audits. ContextVar tokens restore the outer lookup on exit.
    try:
        with _author_ledger_snapshot_scope(lambda path: contexts.snapshot_v2(owner, path)), ledger_validation_scope():
            result = _audit_v3_content_public(*args, ledger_contexts=contexts, ledger_owner=owner, **kwargs)
            contexts.reverify_before_return(owner)
            return result
    finally:
        contexts.close()


def _audit_v3_content_public(*args, ledger_contexts, ledger_owner, **kwargs):
    has_input = "structural_input_path" in kwargs
    has_root = "structural_binding_root" in kwargs
    if has_input != has_root:
        raise TypeError("structural audit requires both input path and binding root")
    supplied_input = kwargs.pop("structural_input_path", None) if has_input else None
    supplied_root = kwargs.pop("structural_binding_root", None) if has_root else None
    if has_input and (supplied_input is None or supplied_root is None):
        raise TypeError("structural audit paths must be nonempty")
    structural_context = None
    structural_paths = None
    pending = kwargs.get("pending_source_context")
    bindings = pending.get("review_input", {}).get("bindings", {}) if isinstance(pending, dict) and isinstance(pending.get("review_input"), dict) else {}
    structural_names = {"structural_predecessor_input", "structural_predecessor_evidence", "structural_edits"}
    if (has_input or (isinstance(bindings, dict) and structural_names & set(bindings)
            and isinstance(pending, dict) and {"input_path", "binding_root"} <= set(pending))):
        from kb_creator.pipeline.source_choice_container_proof import open_structural_projection_context
        structural_paths = (Path(supplied_input if has_input else pending["input_path"]),
                            Path(supplied_root if has_input else pending["binding_root"]))
        structural_context = open_structural_projection_context(
            input_path=structural_paths[0], binding_root=structural_paths[1])
        if has_input and isinstance(bindings, dict) and structural_names & set(bindings):
            if Path(pending["input_path"]).resolve() != Path(supplied_input).resolve() or Path(pending["binding_root"]).resolve() != Path(supplied_root).resolve():
                raise ValueError("structural audit input differs from pending source authority")
    result = _audit_v3_content(*args, _ledger_contexts=ledger_contexts, _ledger_owner=ledger_owner,
                             _structural_context=structural_context, **kwargs)
    if structural_paths is not None:
        reopened = open_structural_projection_context(
            input_path=structural_paths[0], binding_root=structural_paths[1])
        if reopened != structural_context:
            raise ValueError("structural audit authority changed during audit")
    return result


def _audit_v3_content_for_author(*args, ledger_contexts, ledger_owner, structural_context=None, **kwargs):
    """Reuse only the enclosing author's already opened immutable snapshots."""
    from kb_creator.pipeline.source_choice_successor import ledger_validation_scope
    with ledger_validation_scope():
        return _audit_v3_content(*args, _ledger_contexts=ledger_contexts, _ledger_owner=ledger_owner,
                                 _structural_context=structural_context, **kwargs)


def write_output(path: Path, report: dict[str, Any]) -> None:
    path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=("legacy-v1", "v2"), required=True)
    parser.add_argument("--decisions-root", type=Path, required=True); parser.add_argument("--merge-packets-root", type=Path, required=True)
    parser.add_argument("--reviewed-allowlist", type=Path); parser.add_argument("--output", type=Path); parser.add_argument("--recall-threshold", type=float, default=0.95)
    parser.add_argument("--review-queue", type=Path); parser.add_argument("--review-queue-sha256")
    parser.add_argument("--comparison", type=Path); parser.add_argument("--comparison-sha256")
    parser.add_argument("--decision-set", type=Path); parser.add_argument("--decision-set-sha256")
    args = parser.parse_args()
    if args.mode == "legacy-v1":
        if any((args.review_queue, args.review_queue_sha256, args.comparison, args.comparison_sha256, args.decision_set, args.decision_set_sha256)): parser.error("legacy-v1 does not accept v2 authority arguments")
        report = audit(args.decisions_root, args.merge_packets_root, args.reviewed_allowlist, args.recall_threshold)
    else:
        if args.recall_threshold != 0.95: parser.error("v2 selected recall threshold is fixed at 0.95")
        required = (args.review_queue, args.review_queue_sha256, args.comparison, args.comparison_sha256, args.decision_set, args.decision_set_sha256)
        if any(item is None for item in required): parser.error("v2 requires the complete queue/comparison/decision-set authority")
        report = audit_v2(args.decisions_root, args.merge_packets_root, args.review_queue, args.review_queue_sha256, args.comparison, args.comparison_sha256, args.decision_set, args.decision_set_sha256, args.reviewed_allowlist)
    if args.output: write_output(args.output, report)
    # Keep the machine-readable stdout portable on legacy Windows code pages.
    print(json.dumps(report, ensure_ascii=True))
    return 0 if report["passed"] else 1


if __name__ == "__main__": raise SystemExit(main())
