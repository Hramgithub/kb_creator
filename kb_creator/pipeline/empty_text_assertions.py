"""Explicit visual transcription of a selected, truly empty OCR text region."""
from __future__ import annotations

import hashlib
import math
from typing import Any, Mapping

RELATION = "within_selected_empty_text_region"
VIEWS = {"original_pipeline_txt", "original_pipeline_ocr", "raster_pipeline_ocr"}
EMPTY_SHA = hashlib.sha256(b"").hexdigest().upper()


def descriptor(packet: Mapping, page: int, view: str, raw: int) -> dict:
    if type(page) is not int or page < 1 or packet.get("source_page") != page or view not in VIEWS or type(raw) is not int or raw < 0:
        raise ValueError("empty-text assertion source locator is invalid")
    matches = [b for b in packet.get("views", {}).get(view, {}).get("blocks", []) if b.get("raw_index") == raw]
    if len(matches) != 1:
        raise ValueError("empty-text assertion source block is not unique")
    block = matches[0]
    box = block.get("bbox")
    if (block.get("text") != "" or block.get("type") not in {"text", "title"}
            or block.get("assets") != [] or not isinstance(box, list) or len(box) != 4
            or any(type(x) not in (float, int) or not math.isfinite(x) for x in box)
            or not 0 <= box[0] < box[2] <= 1000 or not 0 <= box[1] < box[3] <= 1000):
        raise ValueError("empty-text assertion requires an exact empty text block and valid bbox")
    return {"source_page": page, "view_id": view, "raw_index": raw,
            "block_type": block["type"], "bbox": list(box), "original_text_sha256": EMPTY_SHA}


def owner(decision: Mapping, view: str, raw: int) -> Mapping | None:
    """A source-only semantic owner is necessary, but does not certify its assertion."""
    selected = [r for r in decision.get("selected_blocks", []) if r.get("view") == view and r.get("raw_index") == raw]
    if len(selected) != 1 or selected[0].get("purpose") != "structure":
        return None
    key = {"view": view, "raw_index": raw}
    units = decision.get("semantic_structure", {}).get("units", [])
    matches = [u for u in units if key in u.get("source_blocks", [])]
    if len(matches) != 1:
        return None
    unit = matches[0]
    ids = unit.get("visual_assertion_ids")
    if (unit.get("source_blocks") != [key] or unit.get("source_fragments") != []
            or not isinstance(ids, list) or len(ids) != 1 or not isinstance(ids[0], str) or not ids[0]):
        return None
    return unit


def select_empty_sources(decision: dict, packet: Mapping, selectors: Any, page: int) -> None:
    if selectors is None:
        return
    if not isinstance(selectors, list):
        raise ValueError("empty_source_selections must be a list")
    seen = set()
    for item in selectors:
        if not isinstance(item, dict) or set(item) != {"view", "raw_index"}:
            raise ValueError("invalid empty source selection")
        descriptor(packet, page, item["view"], item["raw_index"])
        key = item["view"], item["raw_index"]
        if key in seen or any((s.get("view"), s.get("raw_index")) == key for s in decision["selected_blocks"]):
            raise ValueError("duplicate empty source selection")
        seen.add(key)
        decision["selected_blocks"].append({**item, "purpose": "structure"})


def validate(row: Mapping, packet: Mapping, decision: Mapping, rendered: str) -> tuple[int, int]:
    """Verify source identity and exact reader placement; visual bytes checked by caller."""
    page = row.get("source_page")
    placement = row.get("placement")
    if not isinstance(placement, dict) or set(placement) != {"relation", "source_block", "markdown_span"} or placement["relation"] != RELATION:
        raise ValueError("invalid empty-text assertion placement")
    block = placement["source_block"]
    if not isinstance(block, dict) or block != descriptor(packet, page, block.get("view_id"), block.get("raw_index")):
        raise ValueError("stale empty-text assertion source")
    if row.get("source_region") != {"view_id": block["view_id"], "coordinate_space": "mineru_page_1000_top_left_v1", "bbox": block["bbox"]}:
        raise ValueError("empty-text assertion region differs from packet")
    unit = owner(decision, block["view_id"], block["raw_index"])
    if unit is None or unit["visual_assertion_ids"] != [row.get("assertion_id")]:
        raise ValueError("empty-text assertion lacks one exact semantic owner")
    # Reuse the same visible-text normalization as the existing assertion route.
    from kb_creator.scripts.audit_mineru_ai_merge_fidelity import _normalized
    text = row.get("text")
    normalized = _normalized(text) if isinstance(text, str) else ""
    sha = lambda s: hashlib.sha256(s.encode("utf-8")).hexdigest().upper()
    if (not normalized or row.get("original_text_sha256") != sha(text)
            or row.get("normalized_text_sha256") != sha(normalized)):
        raise ValueError("empty-text assertion transcription identity mismatch")
    from .reviewed_correction_text import verify_visible_correction
    verify_visible_correction(decision["markdown"], text, unit["markdown_span"])
    span = placement["markdown_span"]
    if not isinstance(span, dict) or set(span) != {"start", "end", "sha256"}:
        raise ValueError("invalid empty-text assertion reader span")
    start, end = span["start"], span["end"]
    if (type(start) is not int or type(end) is not int or not 0 <= start < end <= len(rendered)
            or rendered[start:end] != normalized or span["sha256"] != sha(normalized)
            or rendered.count(normalized) != 1):
        raise ValueError("empty-text assertion reader text is absent, stale or ambiguous")
    expected_visual = f"outputs/04-visual-merge-bundle/visual/{block['view_id']}/pages/page-{page:03d}.png"
    if row.get("visual", {}).get("path") != expected_visual:
        raise ValueError("empty-text assertion visual is for another source page/view")
    if row.get("visual_verdict") != "source_text_visible_at_region" or not isinstance(row.get("rationale"), str) or not row["rationale"].strip():
        raise ValueError("empty-text assertion lacks explicit visual review")
    return start, end


def author_assertion(selector: Mapping, packet: Mapping, decision: Mapping, visual_inventory: Mapping) -> dict:
    expected = {"assertion_id", "source_page", "text", "bbox", "relation", "empty_source", "rationale"}
    if set(selector) != expected or selector["relation"] != RELATION:
        raise ValueError("invalid empty-text assertion selector")
    locator = selector["empty_source"]
    if not isinstance(locator, dict) or set(locator) != {"view_id", "raw_index"}:
        raise ValueError("invalid empty-text assertion locator")
    page = selector["source_page"]
    block = descriptor(packet, page, locator["view_id"], locator["raw_index"])
    if selector["bbox"] != block["bbox"]:
        raise ValueError("empty-text assertion selector bbox differs from packet")
    from kb_creator.scripts.audit_mineru_ai_merge_fidelity import _normalized, ASSET, IMAGE
    text = selector["text"]
    normalized = _normalized(text)
    rendered = _normalized(ASSET.sub("", IMAGE.sub("", decision["markdown"])))
    start = rendered.find(normalized)
    visual = f"outputs/04-visual-merge-bundle/visual/{locator['view_id']}/pages/page-{page:03d}.png"
    if visual not in visual_inventory:
        raise ValueError("empty-text assertion source visual is absent")
    sha = lambda value: hashlib.sha256(value.encode("utf-8")).hexdigest().upper()
    row = {"assertion_id": selector["assertion_id"], "source_page": page, "text": text,
           "original_text_sha256": sha(text), "normalized_text_sha256": sha(normalized),
           "source_region": {"view_id": locator["view_id"], "coordinate_space": "mineru_page_1000_top_left_v1", "bbox": block["bbox"]},
           "placement": {"relation": RELATION, "source_block": block,
                         "markdown_span": {"start": start, "end": start+len(normalized), "sha256": sha(normalized)}},
           "visual": {"path": visual, **visual_inventory[visual]},
           "visual_verdict": "source_text_visible_at_region", "rationale": selector["rationale"]}
    validate(row, packet, decision, rendered)
    return row
