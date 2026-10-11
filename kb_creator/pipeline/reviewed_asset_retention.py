"""Retain omitted image-only packet assets without changing reader content or review."""
from __future__ import annotations

from copy import deepcopy
from typing import Any

from kb_creator.scripts.prepare_mineru_review_drafts import (
    CANONICAL_VIEWS, _logical_asset_name, _safe_asset_path,
)


def retain_reference_assets(packet: dict, decision: dict) -> dict[str, Any]:
    """Return a successor draft and exact additions; this grants no visual approval.

    All views are retained independently. Blocks carrying text or table data are
    left for semantic decisions; retaining an image must not hide their text.
    Existing reader placements, Markdown and review/unresolved fields are copied.
    Source file bytes are verified by the ordinary downstream asset validator.
    """
    page = packet.get("source_page")
    if type(page) is not int or page < 1 or decision.get("source_page") != page:
        raise ValueError("asset retention page identity mismatch")
    if packet.get("semantic_role") != decision.get("semantic_role"):
        raise ValueError("asset retention role mismatch")
    views = packet.get("views")
    if not isinstance(views, dict) or not views or not set(views) <= CANONICAL_VIEWS:
        raise ValueError("asset retention packet views invalid")
    result = deepcopy(decision)
    selected = result.get("selected_blocks")
    assets = result.get("assets")
    if not isinstance(selected, list) or not isinstance(assets, list):
        raise ValueError("asset retention requires decision selections/assets")
    keys = [(x["view"], x["raw_index"]) for x in selected]
    if len(keys) != len(set(keys)):
        raise ValueError("asset retention duplicate selection")
    selected_keys = set(keys)
    names = [a["logical_name"] for a in assets]
    if len(names) != len(set(names)):
        raise ValueError("asset retention duplicate logical name")
    retained = {(a["view"], a["source_path"]) for a in assets}
    additions, deferred, packet_keys = [], [], set()
    for view in sorted(views):
        blocks = views[view].get("blocks")
        if not isinstance(blocks, list):
            raise ValueError("asset retention packet blocks invalid")
        for block in blocks:
            raw = block.get("raw_index")
            key = (view, raw)
            if type(raw) is not int or raw < 0 or key in packet_keys:
                raise ValueError("asset retention packet block identity invalid")
            packet_keys.add(key)
            paths = block.get("assets", [])
            if not isinstance(paths, list):
                raise ValueError("asset retention packet assets invalid")
            paths = [_safe_asset_path(path) for path in paths]
            if len(paths) != len(set(paths)):
                raise ValueError("asset retention duplicate source path")
            if not paths:
                continue
            if block.get("type") != "image" or block.get("text") or block.get("table_body"):
                deferred.append({"view": view, "raw_index": raw,
                                 "reason": "source carries text/table or is not an image"})
                continue
            if key not in selected_keys:
                selected.append({"view": view, "raw_index": raw, "purpose": "asset"})
                selected_keys.add(key)
            for path in paths:
                if (view, path) in retained:
                    continue
                name = view + "-" + _logical_asset_name(page, raw, path)
                if name in names:
                    raise ValueError("asset retention generated logical name collision")
                asset = {"view": view, "source_path": path, "logical_name": name,
                         "placement": "reference_only"}
                assets.append(asset)
                names.append(name)
                retained.add((view, path))
                additions.append({"source_page": page, "raw_index": raw, **asset})
    if not selected_keys <= packet_keys:
        raise ValueError("asset retention selection absent from packet")
    return {"decision": result, "added_assets": additions, "deferred_blocks": deferred}
