"""Deterministic, non-authoritative reconstruction draft compiler.

This module deliberately stops at a machine candidate.  It consumes only a
verified Stage04 root, records every three-view discrepancy, and never creates
reviewed decisions, an allowlist, or a decision set.
"""
from __future__ import annotations

import hashlib
import json
import re
import shutil
from html.parser import HTMLParser
from pathlib import Path, PurePosixPath
from typing import Any, Callable, Mapping
from .mechanical_text_selection import select_text, _c0, _typographic_quote_equivalent


SCHEMA = "kb_creator.mechanical_draft.v3"
V2_SCHEMA = "kb_creator.mechanical_draft.v2"
RULESET = "mechanical-reconstruction.v3"
V2_RULESET = "mechanical-reconstruction.v2"
V4_SCHEMA = "kb_creator.mechanical_draft.v4"
V4_RULESET = "mechanical-reconstruction.v4"
V5_SCHEMA = "kb_creator.mechanical_draft.v5"
V5_RULESET = "mechanical-reconstruction.v5"
VIEWS = ("original_pipeline_txt", "original_pipeline_ocr", "raster_pipeline_ocr")
_PAGE = re.compile(r"page-(\d{3,})\.json$")


def _sha(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest().upper()


def _canonical(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


def _identity(path: Path) -> dict[str, Any]:
    data = path.read_bytes()
    return {"bytes": len(data), "sha256": _sha(data)}


def _bound_identity(root: Path, path: Path) -> dict[str, Any]:
    """Record both a stable run-relative locator and the exact bytes read."""
    try:
        locator = path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError as error:
        raise ValueError("authority file is outside the verified run root") from error
    return {"path": locator, **_identity(path)}


def _write(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + "\n", encoding="utf-8")


def _safe_asset(value: Any) -> str:
    if not isinstance(value, str) or not value or "\\" in value or ":" in value:
        raise ValueError("asset path must be a nonempty relative POSIX path")
    path = PurePosixPath(value)
    if path.is_absolute() or any(part in {"", ".", ".."} for part in path.parts):
        raise ValueError("asset path escapes its packet")
    return value


def _block_identity(block: Mapping[str, Any]) -> tuple[Any, ...]:
    """Use actual block evidence; similarity scores are intentionally ignored."""
    text = block.get("text", "")
    if not isinstance(text, str):
        raise ValueError("packet block text is invalid")
    block_type = block.get("type")
    bbox = block.get("bbox")
    assets = block.get("assets", [])
    table_body = block.get("table_body", "")
    if not isinstance(block_type, str) or not isinstance(bbox, list) or len(bbox) != 4:
        raise ValueError("packet block structural evidence is invalid")
    if not isinstance(assets, list) or not isinstance(table_body, str):
        raise ValueError("packet block asset or table evidence is invalid")
    evidence = block.get("semantic_evidence", {})
    if not isinstance(evidence, Mapping): raise ValueError("packet block semantic evidence is invalid")
    return (block_type, text, tuple(bbox), tuple(_safe_asset(item) for item in assets), table_body, _canonical(evidence).decode("utf-8"))


def _content_identity(block: Mapping[str, Any]) -> tuple[Any, ...]:
    identity = _block_identity(block)
    return (identity[0], identity[1], identity[3], identity[4], identity[5])


class _TableParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(); self.rows: list[list[str]] = []; self._cell: list[str] | None = None; self.unsafe = False; self.depth = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag == "table": self.depth += 1; self.unsafe |= self.depth != 1
        if tag == "br": self.unsafe = True
        if tag == "tr": self.rows.append([])
        if tag in {"td", "th"}:
            self.unsafe |= any(name in {"rowspan", "colspan"} for name, _ in attrs)
            self._cell = []

    def handle_data(self, data: str) -> None:
        if self._cell is not None:
            self.unsafe |= "\n" in data or "\r" in data
            self._cell.append(data)

    def handle_endtag(self, tag: str) -> None:
        if tag == "table": self.depth -= 1
        if tag in {"td", "th"} and self._cell is not None:
            if not self.rows: raise ValueError("table cell has no row")
            self.rows[-1].append(" ".join("".join(self._cell).split())); self._cell = None


def _table_markdown(value: str) -> str | None:
    if not value.strip(): return None
    parser = _TableParser(); parser.feed(value); parser.close()
    rows = [row for row in parser.rows if row]
    if parser.unsafe or parser.depth or len(rows) < 2 or not rows[0] or any(len(row) != len(rows[0]) for row in rows) or any("|" in cell or "\n" in cell or "\r" in cell for row in rows for cell in row): return None
    header = rows[0]; delim = ["---"] * len(header)
    return "\n".join("| " + " | ".join(row) + " |" for row in [header, delim, *rows[1:]])


def _logical_asset(page: int, raw_index: int, path: str) -> str:
    suffix = PurePosixPath(path).suffix
    stem = re.sub(r"[^A-Za-z0-9._-]+", "-", PurePosixPath(path).stem).strip(".-") or "asset"
    return f"p{page:03d}-r{raw_index:05d}-{stem}-{hashlib.sha256(path.encode()).hexdigest()[:12]}{suffix}"


def _reviewed_correction(block: Mapping[str, Any], corrections: Mapping[str, Any] | None) -> tuple[str, dict[str, Any] | None]:
    text = str(block.get("text", "")); source_hash = _sha(text.encode("utf-8"))
    if not corrections: return text, None
    row = corrections.get(source_hash)
    if row is None: return text, None
    if not isinstance(row, Mapping) or set(row) != {"source_sha256", "before", "after", "reason"}:
        raise ValueError("reviewed source correction has invalid shape")
    before, after = row["before"], row["after"]
    if row["source_sha256"] != source_hash or not all(isinstance(item, str) and item for item in (before, after, row["reason"])) or before == after or text.count(before) != 1:
        raise ValueError("reviewed source correction is not exact and unique")
    return text.replace(before, after, 1), dict(row)


def _line_span(markdown: str, start_line: int, text: str) -> dict[str, Any]:
    lines = text.split("\n")
    return {"start_line": start_line, "end_line": start_line + len(lines) - 1, "sha256": _sha(text.encode("utf-8"))}


def _verify_stage04(run_root: Path, authority_validator: Callable[[Path], Any] | None) -> Path:
    root = Path(run_root).resolve()
    if authority_validator is None:
        # The topology is explicit.  Never reinterpret a corrupt replay as a
        # native run merely because replay validation failed.
        from kb_creator.pipeline import reconstruction
        if (root / "replay" / "bridge.json").is_file():
            from kb_creator.pipeline.reconstruction_replay import (
                validate_replay_artifacts_for_consumption, validate_replay_authorities,
            )
            if (root / "replay" / "completion.json").is_file():
                validate_replay_artifacts_for_consumption(root)
            else:
                # Fully replayed Stage04 keeps its existing strict validator.
                validate_replay_authorities(root)
        else:
            run = reconstruction.load_run(root)
            if Path(str(run["local"]["run_root"])).resolve() != root:
                raise ValueError("archived native run root binding mismatch")
            contract, contract_sha = reconstruction.load_contract(Path(run["local"]["contract_path"]))
            if contract_sha != run["contract"]["sha256"] or contract.get("contract_revision") != run["contract"].get("contract_revision"):
                raise ValueError("archived native contract binding mismatch")
            if _identity(Path(run["local"]["source_path"])) != {key: run["source"][key] for key in ("bytes", "sha256")}:
                raise ValueError("archived native source binding mismatch")
            reconstruction._validate_stage_prefix(root, run, reconstruction.RUN_STAGES)
    else:
        authority_validator(root)
    stage = root / "outputs" / "04-visual-merge-bundle"
    required = [stage / "merge_packets" / "pages", stage / "visual" / "visual_manifest.json"]
    if any(not path.exists() for path in required): raise ValueError("verified Stage04 output is incomplete")
    return stage


def _authority_identities(root: Path, stage: Path) -> dict[str, Any]:
    """Bind the exact authorities already checked by the native/replay validator."""
    run_path = root / "run.json"
    prepared = root / "outputs" / "01-prepare-inputs" / "prepared" / "sample_pages.json"
    comparison = root / "outputs" / "03-compare-views" / "comparison.json"
    visual = stage / "visual" / "visual_manifest.json"
    required = (run_path, prepared, comparison, visual)
    if any(not path.is_file() for path in required):
        raise ValueError("verified Stage04 authority inputs are incomplete")
    run = json.loads(run_path.read_text(encoding="utf-8"))
    source = run.get("source")
    if not isinstance(source, Mapping) or not isinstance(source.get("path_hint"), str) or not isinstance(source.get("bytes"), int) or not isinstance(source.get("sha256"), str):
        raise ValueError("verified run has no durable source identity")
    replay_dir = root / "replay"
    if replay_dir.is_dir():
        bridge, completion = replay_dir / "bridge.json", replay_dir / "completion.json"
        if not bridge.is_file() or not completion.is_file():
            raise ValueError("verified replay has incomplete bridge or completion authority")
        replay: dict[str, Any] | None = {"bridge": _bound_identity(root, bridge), "completion": _bound_identity(root, completion)}
        route = "replay"
    else:
        replay = None; route = "native"
    return {"validator_route": route, "run": _bound_identity(root, run_path), "source": {"path_hint": source["path_hint"], "bytes": source["bytes"], "sha256": source["sha256"]}, "prepared_manifest": _bound_identity(root, prepared), "comparison": _bound_identity(root, comparison), "visual_manifest": _bound_identity(root, visual), "replay": replay}


def _load_packets(stage: Path) -> list[tuple[int, Path, dict[str, Any]]]:
    rows: list[tuple[int, Path, dict[str, Any]]] = []
    for path in sorted((stage / "merge_packets" / "pages").iterdir()):
        match = _PAGE.fullmatch(path.name)
        if path.is_file() and match:
            data = json.loads(path.read_text(encoding="utf-8")); page = int(match.group(1))
            if data.get("schema") != "kb_creator.mineru_merge_packet.v1" or data.get("source_page") != page:
                raise ValueError(f"invalid Stage04 packet identity: {path.name}")
            if not isinstance(data.get("views"), dict) or set(VIEWS) - set(data["views"]):
                raise ValueError(f"packet lacks a required three-view set: {path.name}")
            rows.append((page, path, data))
    if not rows or [page for page, _, _ in rows] != list(range(1, len(rows) + 1)):
        raise ValueError("Stage04 packets are missing or noncontiguous")
    return rows


def _page_candidate(page: int, packet: Mapping[str, Any], corrections: Mapping[str, Any] | None) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    by_view: dict[str, dict[tuple[Any, ...], list[Mapping[str, Any]]]] = {}
    order: dict[str, list[tuple[Any, ...]]] = {}
    for view in VIEWS:
        blocks = packet["views"][view].get("blocks")
        if not isinstance(blocks, list): raise ValueError(f"page {page}: blocks are invalid")
        mapping: dict[tuple[Any, ...], list[Mapping[str, Any]]] = {}
        for block in blocks:
            if not isinstance(block, Mapping) or type(block.get("raw_index")) is not int: raise ValueError(f"page {page}: block identity is invalid")
            mapping.setdefault(_block_identity(block), []).append(block)
        by_view[view] = mapping
        order[view] = [_block_identity(block) for block in blocks]
    diagnostics: list[dict[str, Any]] = []; entries: list[dict[str, Any]] = []; markdown: list[str] = []; line = 1
    signatures = list(dict.fromkeys(order[VIEWS[0]] + sorted((item for view in VIEWS[1:] for item in order[view] if item not in by_view[VIEWS[0]]), key=lambda item: _sha(_canonical(item)))) )
    clean_order = all(order[view] == order[VIEWS[0]] for view in VIEWS[1:])
    for ordinal, signature in enumerate(signatures):
        matching = [by_view[view].get(signature, []) for view in VIEWS]
        block = next(item for group in matching for item in group)
        source_keys = [{"view": view, "raw_index": item["raw_index"]} for view, items in zip(VIEWS, matching) for item in items]
        assets = [_safe_asset(item) for item in block.get("assets", [])]
        alternatives = [{"view": view, "blocks": [{"raw_index": item["raw_index"], "type": item.get("type"), "bbox": item.get("bbox"), "text": item.get("text", ""), "text_sha256": _sha(str(item.get("text", "")).encode()), "assets": [_safe_asset(asset) for asset in item.get("assets", [])], "table_body_sha256": _sha(str(item.get("table_body", "")).encode()) if item.get("table_body") else None, "semantic_evidence": item.get("semantic_evidence", {})} for item in items]} for view, items in zip(VIEWS, matching)]
        record = {"ordinal": ordinal, "chosen_view": next(view for view, items in zip(VIEWS, matching) if items), "raw_index": block["raw_index"], "source_keys": source_keys, "alternatives": alternatives, "source_text_sha256": _sha(str(block.get("text", "")).encode()), "assets": assets, "table_body_sha256": _sha(str(block.get("table_body", "")).encode()) if block.get("table_body") else None}
        if any(len(item) != 1 for item in matching) or not clean_order:
            code = "source_bijection_ambiguous" if any(len(item) > 1 for item in matching) else "three_view_mismatch"
            diagnostics.append({"code": code, "page": page, "source_keys": source_keys, "alternatives": alternatives, "expected": "one-to-one exact type/text/bbox/asset/table evidence across all three views", "observed": [len(item) for item in matching], "next_action": "review the named Stage04 blocks and source visual"})
            record["disposition"] = "hold"; entries.append(record); continue
        text, correction = _reviewed_correction(block, corrections)
        table = _table_markdown(str(block.get("table_body", ""))) if block.get("type") == "table" else None
        if block.get("type") == "table" and not table:
            code = "table_raw_artifact_unavailable" if not block.get("table_body") else "table_evidence_missing"
            diagnostics.append({"code": code, "page": page, "source_keys": source_keys, "alternatives": alternatives, "expected": "verified raw HTML table with header and data row", "observed": "packet has no safe parseable table body", "next_action": "resolve the verified raw source table through the source keys; retain source asset"})
            record["disposition"] = "hold"; entries.append(record); continue
        rendered = table or text
        if not rendered and not assets:
            record["disposition"] = "excluded_empty"; entries.append(record); continue
        emitted_assets = []
        for asset in assets:
            name = _logical_asset(page, block["raw_index"], asset); emitted_assets.append({"source_path": asset, "logical_name": name})
        if assets:
            rendered = (rendered + "\n" if rendered else "") + "\n".join(f"![mechanical asset]({{{{asset:{row['logical_name']}}}}})" for row in emitted_assets)
        if not rendered:
            rendered = "\n".join(f"![mechanical asset]({{{{asset:{row['logical_name']}}}}})" for row in emitted_assets)
        level = block.get("semantic_evidence", {}).get("text_level") if isinstance(block.get("semantic_evidence"), Mapping) else None
        rule = "paragraph.v1"
        if text and type(level) is int and 1 <= level <= 6:
            rendered = "#" * level + " " + rendered; rule = "heading_from_consistent_metadata.v1"
        asset_only = not text and table is None and bool(emitted_assets)
        source_field = "table_body" if table else "text"
        source_value = str(block.get(source_field, ""))
        source_offsets = [] if asset_only else [{"view": key["view"], "raw_index": key["raw_index"], "field": source_field, "source_sha256": _sha(source_value.encode("utf-8")), "start": 0, "end": len(source_value)} for key in source_keys]
        asset_bindings = [{"view": key["view"], "raw_index": key["raw_index"], "source_path": asset["source_path"], "logical_name": asset["logical_name"]} for key in source_keys for asset in emitted_assets]
        record.update({"disposition": "emitted", "rule": "asset_marker_from_consistent_asset.v1" if asset_only else rule, "correction": correction, "reader_span": _line_span("", line, rendered), "reader_text": rendered, "assets_emitted": emitted_assets, "unit": {"kind": "asset" if asset_only else "table" if table else "paragraph", "source_offsets": source_offsets, "asset_bindings": asset_bindings, "reader_span": _line_span("", line, rendered)}})
        entries.append(record); markdown.append(rendered); line += len(rendered.split("\n")) + 1
    decision = {"source_page": page, "semantic_role": packet.get("semantic_role"), "review": {"visual_reviewed": False, "state": "mechanical_candidate"}, "markdown": "\n\n".join(markdown), "entries": entries, "unresolved": [row["code"] for row in diagnostics]}
    return decision, diagnostics


def _aligned_page_candidate(page: int, packet: Mapping[str, Any], corrections: Mapping[str, Any] | None, bound_corrections: Mapping | None = None) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    """Compile only closed, one-to-one packet geometry triangles.

    Bboxes propose the component.  All non-bbox evidence remains exact.
    """
    blocks: dict[str, dict[int, Mapping[str, Any]]] = {}; positions: dict[str, dict[int, int]] = {}
    for view in VIEWS:
        value = packet["views"][view].get("blocks")
        if not isinstance(value, list): raise ValueError(f"page {page}: blocks are invalid")
        blocks[view] = {}
        for index, block in enumerate(value):
            if not isinstance(block, Mapping) or type(block.get("raw_index")) is not int or block["raw_index"] in blocks[view]: raise ValueError(f"page {page}: invalid raw index")
            _block_identity(block); blocks[view][block["raw_index"]] = block
        positions[view] = {raw: index for index, raw in enumerate(blocks[view])}
    pairs = packet.get("pairwise")
    if not isinstance(pairs, Mapping): raise ValueError(f"page {page}: missing pairwise alignment")
    maps: dict[str, dict[int, int]] = {}; blocked: set[tuple[str, int]] = set()
    for left, right in ((VIEWS[0], VIEWS[1]), (VIEWS[0], VIEWS[2]), (VIEWS[1], VIEWS[2])):
        name = f"{left}__vs__{right}"; pair = pairs.get(name)
        if not isinstance(pair, Mapping) or not isinstance(pair.get("bbox_matches"), list): raise ValueError(f"page {page}: invalid pairwise alignment")
        mapping: dict[int, int] = {}; targets: set[int] = set()
        for edge in pair["bbox_matches"]:
            if not isinstance(edge, Mapping) or type(edge.get("left_raw_index")) is not int or type(edge.get("right_raw_index")) is not int or type(edge.get("bbox_iou")) not in {int, float}: raise ValueError(f"page {page}: malformed bbox edge")
            a, b = edge["left_raw_index"], edge["right_raw_index"]
            if a not in blocks[left] or b not in blocks[right] or a in mapping or b in targets: raise ValueError(f"page {page}: ambiguous bbox edge")
            mapping[a] = b; targets.add(b)
        for side, view in (("left_unmatched", left), ("right_unmatched", right)):
            rows = pair.get(side, [])
            if not isinstance(rows, list): raise ValueError(f"page {page}: malformed unmatched authority")
            for row in rows:
                if not isinstance(row, Mapping) or type(row.get("raw_index")) is not int or row["raw_index"] not in blocks[view]: raise ValueError(f"page {page}: unmatched authority references unknown source key")
                blocked.add((view, row["raw_index"]))
        conflicts = pair.get("semantic_conflicts", [])
        if not isinstance(conflicts, list): raise ValueError(f"page {page}: malformed semantic conflict authority")
        for conflict in conflicts:
            if not isinstance(conflict, Mapping): raise ValueError(f"page {page}: malformed semantic conflict")
            for prefix, view in (("left", left), ("right", right)):
                raw = conflict.get(f"{prefix}_raw_index")
                if raw is not None:
                    if type(raw) is not int or raw not in blocks[view]: raise ValueError(f"page {page}: semantic conflict references unknown source key")
                    # Pairwise conflict metadata is evidence, not an extra
                    # output rule. select_text applies the same projection to
                    # the closed triangle below.
            for prefix in ("asset", "heading"):
                raw, side = conflict.get(f"{prefix}_raw_index"), conflict.get(f"{prefix}_side")
                if raw is not None:
                    view = left if side == "left" else right if side == "right" else None
                    if view is None or type(raw) is not int or raw not in blocks[view]: raise ValueError(f"page {page}: semantic conflict references unknown source key")
        maps[name] = mapping
    components: list[list[tuple[str, int]]] = []; used: set[tuple[str, int]] = set()
    for a, b in maps[f"{VIEWS[0]}__vs__{VIEWS[1]}"].items():
        c = maps[f"{VIEWS[0]}__vs__{VIEWS[2]}"].get(a)
        if c is not None and maps[f"{VIEWS[1]}__vs__{VIEWS[2]}"].get(b) == c:
            keys = [(VIEWS[0], a), (VIEWS[1], b), (VIEWS[2], c)]
            if any(key in used for key in keys): raise ValueError(f"page {page}: overlapping bbox triangle")
            components.append(keys); used.update(keys)
    components.extend([[(view, raw)] for view in VIEWS for raw in blocks[view] if (view, raw) not in used])
    components.sort(key=lambda keys: (positions[VIEWS[0]].get(next((raw for view, raw in keys if view == VIEWS[0]), 10**9), 10**9), keys))
    inverted: set[int] = set()
    for i, left in enumerate(components):
        if len(left) != 3: continue
        lp = {view: positions[view][raw] for view, raw in left}
        for j in range(i + 1, len(components)):
            right = components[j]
            if len(right) == 3 and any(lp[view] > positions[view][raw] for view, raw in right): inverted.update((i, j))
    diagnostics=[]; entries=[]; markdown=[]; line=1
    for ordinal, keys in enumerate(components):
        grouped={view:[blocks[view][raw] for key_view,raw in keys if key_view==view] for view in VIEWS}; chosen=next(view for view in VIEWS if grouped[view]); block=grouped[chosen][0]
        alternatives=[{"view":view,"blocks":[{"raw_index":x["raw_index"],"type":x.get("type"),"bbox":x.get("bbox"),"text":x.get("text", ""),"text_sha256":_sha(str(x.get("text", "")).encode()),"assets":[_safe_asset(a) for a in x.get("assets", [])],"table_body_sha256":_sha(str(x.get("table_body", "")).encode()) if x.get("table_body") else None,"semantic_evidence":x.get("semantic_evidence", {})} for x in grouped[view]]} for view in VIEWS]
        source_keys=[{"view":view,"raw_index":raw} for view,raw in keys]; assets=[_safe_asset(x) for x in block.get("assets", [])]
        record={"ordinal":ordinal,"chosen_view":chosen,"raw_index":block["raw_index"],"source_keys":source_keys,"alternatives":alternatives,"source_text_sha256":_sha(str(block.get("text", "")).encode()),"assets":assets,"table_body_sha256":_sha(str(block.get("table_body", "")).encode()) if block.get("table_body") else None}
        code = "unmatched_three_view_component" if len(keys) != 3 else "semantic_conflict" if any(key in blocked for key in keys) else "reading_order_conflict" if ordinal in inverted else None
        reviewed = next((bound_corrections[(page, view, raw)] for view, raw in keys if bound_corrections and (page, view, raw) in bound_corrections), None)
        if reviewed is not None:
            record["bound_correction"] = dict(reviewed)
        selection = None
        if code is None:
            correction_input = ({"page": page, **{k: reviewed[k] for k in ("view", "raw_index", "before", "after", "reason")}}
                                if reviewed else None)
            selection = select_text({view: grouped[view][0] for view in VIEWS}, correction_input)
            code = selection.get("typed_hold")
        if code:
            diagnostics.append({"code":code,"page":page,"source_keys":source_keys,"alternatives":alternatives,"expected":"closed three-view geometry component with exact type/text/asset/table/semantic evidence and local order","observed":[len(grouped[v]) for v in VIEWS],"next_action":"review the named Stage04 blocks and source visual"}); record["disposition"]="hold"; entries.append(record); continue
        chosen = selection["chosen_view"]
        block = grouped[chosen][0]
        record.update(chosen_view=chosen, raw_index=block["raw_index"], source_text_sha256=_sha(block.get("text", "").encode()))
        text = selection["output_text"]
        correction = ({"source_sha256": reviewed["before_sha256"], **{k: reviewed[k] for k in ("before", "after", "reason")}}
                      if reviewed else None)
        if corrections:
            if selection["reason"] != "three_view_exact":
                raise ValueError("legacy hash-only corrections cannot authorize recovered text")
            text, correction = _reviewed_correction(block, corrections)
        if _c0(text):
            raise ValueError("mechanical output contains control characters")
        record["correction"] = correction
        record["text_selection"] = {
            "rule": selection["reason"], "output_sha256": _sha(text.encode()),
            "view_status": {view: "selected" if view == chosen else "tainted" if _c0(grouped[view][0].get("text", "")) else "corroborating" if grouped[view][0].get("text", "") == block.get("text", "") else "equivalent" if selection["reason"] in {"three_view_typographic_quote_equivalent", "three_view_title_ascii_case_equivalent.v1", "three_view_title_letter_spacing_equivalent.v1"} else "alternative" for view in VIEWS},
        }
        table=_table_markdown(str(block.get("table_body", ""))) if block.get("type")=="table" else None
        if reviewed and table:
            # A correction to the flattened text does not rewrite raw HTML cells.
            diagnostics.append({"code":"table_source_correction_requires_structure","page":page,"source_keys":source_keys,"alternatives":alternatives,"expected":"reviewed table-cell structure","observed":"text correction cannot authorize table HTML","next_action":"bind corrected source text to explicit table cells"})
            record["disposition"]="hold"; entries.append(record); continue
        if block.get("type")=="table" and not table:
            diagnostics.append({"code":"table_evidence_missing","page":page,"source_keys":source_keys,"alternatives":alternatives,"expected":"verified raw HTML table with header and data row","observed":"packet has no safe parseable table body","next_action":"resolve the verified raw source table through the source keys; retain source asset"}); record["disposition"]="hold"; entries.append(record); continue
        rendered=table or text
        if not rendered and not assets: record["disposition"]="excluded_empty"; entries.append(record); continue
        emitted=[{"source_path":asset,"logical_name":_logical_asset(page,block["raw_index"],asset)} for asset in assets]
        if emitted: rendered=(rendered+"\n" if rendered else "")+"\n".join(f"![mechanical asset]({{{{asset:{x['logical_name']}}}}})" for x in emitted)
        level=block.get("semantic_evidence",{}).get("text_level") if isinstance(block.get("semantic_evidence"),Mapping) else None; rule="paragraph.v1"
        if text and type(level) is int and 1<=level<=6: rendered="#"*level+" "+rendered; rule="heading_from_consistent_metadata.v1"
        asset_only=not text and table is None and bool(emitted); field="table_body" if table else "text"; source=str(block.get(field,""))
        contributing = keys if selection["reason"] == "three_view_exact" else [(chosen, block["raw_index"])]
        offsets=[] if asset_only else [{"view":view,"raw_index":raw,"field":field,"source_sha256":_sha(str(blocks[view][raw].get(field, "")).encode()),"start":0,"end":len(str(blocks[view][raw].get(field, "")))} for view,raw in contributing]
        bindings=[{"view":view,"raw_index":raw,"source_path":asset["source_path"],"logical_name":asset["logical_name"]} for view,raw in keys for asset in emitted]
        record.update({"disposition":"emitted","rule":"asset_marker_from_consistent_asset.v1" if asset_only else rule,"correction":correction,"reader_span":_line_span("",line,rendered),"reader_text":rendered,"assets_emitted":emitted,"unit":{"kind":"asset" if asset_only else "table" if table else "paragraph","source_offsets":offsets,"asset_bindings":bindings,"reader_span":_line_span("",line,rendered)}}); entries.append(record); markdown.append(rendered); line+=len(rendered.split("\n"))+1
    return {"source_page":page,"semantic_role":packet.get("semantic_role"),"review":{"visual_reviewed":False,"state":"mechanical_candidate"},"markdown":"\n\n".join(markdown),"entries":entries,"unresolved":[x["code"] for x in diagnostics]}, diagnostics


def compile_mechanical_draft(run_root: Path, output_dir: Path, *, reviewed_corrections: Mapping[str, Any] | None = None, bound_reviews: Path | None = None, authority_validator: Callable[[Path], Any] | None = None) -> dict[str, Any]:
    """Compile a source-preserving, held-on-disagreement candidate from Stage04."""
    stage = _verify_stage04(Path(run_root), authority_validator); output = Path(output_dir).resolve()
    if output.exists(): raise FileExistsError("mechanical draft output already exists")
    ledger, bound_map = None, {}
    if bound_reviews is not None:
        if reviewed_corrections:
            raise ValueError("choose source-bound or legacy corrections, not both")
        from .bound_ocr_review_loader import load_bound_ocr_reviews
        ledger, bound_map = load_bound_ocr_reviews(Path(run_root), Path(bound_reviews), authority_validator=lambda _: stage)
    manifest_path = stage / "visual" / "visual_manifest.json"; visual = json.loads(manifest_path.read_text(encoding="utf-8"))
    if not isinstance(visual.get("files"), list): raise ValueError("Stage04 visual manifest is invalid")
    packets = _load_packets(stage); staging = output.parent / f".{output.name}.mechanical-staging"
    if staging.exists(): raise FileExistsError("owned mechanical draft staging already exists")
    try:
        pages = []; diagnostics = []
        for page, path, packet in packets:
            decision, page_diagnostics = _aligned_page_candidate(page, packet, reviewed_corrections, bound_map)
            _write(staging / "pages" / f"page-{page:03d}.json", decision)
            pages.append({"source_page": page, "packet": {"path": path.name, **_identity(path)}, "candidate": {"path": f"pages/page-{page:03d}.json", **_identity(staging / "pages" / f"page-{page:03d}.json")}})
            diagnostics.extend(page_diagnostics)
        if ledger is not None:
            for name, expected_identity in {Path(bound_reviews).name: _identity(Path(bound_reviews)), **ledger["evidence"]}.items():
                source = Path(bound_reviews).parent / _safe_asset(name)
                destination = staging / "bound-reviews" / name
                destination.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(source, destination)
                if _identity(destination) != expected_identity:
                    raise ValueError("bound review evidence changed during materialization")
        report = {"schema": V5_SCHEMA, "state": "mechanical_candidate_requires_review", "authority": "verified Stage04 input only; no reviewed, reconstruction, master, or release authority", "run_root": str(Path(run_root).resolve()), "authorities": _authority_identities(Path(run_root).resolve(), stage), "stage04_visual_manifest": _identity(manifest_path), "page_count": len(pages), "pages": pages, "diagnostics": diagnostics, "review_flags": {"visual_reviewed": False, "accepted": False}, "unresolved_hold_count": len(diagnostics), "ruleset_version": V5_RULESET, "bound_reviews": {"path": "bound-reviews/" + Path(bound_reviews).name, **_identity(Path(bound_reviews))} if ledger else None}
        report["manifest_sha256"] = _sha(_canonical(report)); _validate_generated_draft(report, staging); _write(staging / "mechanical_draft.json", report); staging.replace(output)
        return report
    finally:
        if staging.exists(): shutil.rmtree(staging)


def verify_mechanical_draft(candidate_dir: Path, *, authority_validator: Callable[[Path], Any] | None = None, reviewed_corrections: Mapping[str, Any] | None = None) -> dict[str, Any]:
    """Read and verify a sealed mechanical candidate without accepting it.

    The returned manifest remains a mechanical candidate.  This reopens the
    native/replay Stage04 authority, compares the newly observed authority
    identities to the sealed manifest, and verifies every bound packet and
    candidate page.  ``authority_validator`` is a test-only substitution for
    the Stage04 authority boundary; production callers must leave it unset.
    """
    directory = Path(candidate_dir).resolve()
    manifest_path = directory / "mechanical_draft.json"
    if not manifest_path.is_file():
        raise ValueError("mechanical draft manifest is missing")
    report = json.loads(manifest_path.read_text(encoding="utf-8"))
    if not isinstance(report, Mapping) or not _nonempty_string(report.get("run_root")):
        raise ValueError("mechanical draft manifest lacks a bound run root")
    run_root = Path(report["run_root"]).resolve()
    stage = _verify_stage04(run_root, authority_validator)
    if str(run_root) != report["run_root"]:
        raise ValueError("mechanical draft run root is not canonical")
    expected_authorities = _authority_identities(run_root, stage)
    if report.get("authorities") != expected_authorities:
        raise ValueError("mechanical draft authority binding changed")
    manifest_identity = _identity(stage / "visual" / "visual_manifest.json")
    if report.get("stage04_visual_manifest") != manifest_identity:
        raise ValueError("mechanical draft visual manifest binding changed")
    _validate_generated_draft(report, directory)
    _verify_packet_authority(report, directory, stage, reviewed_corrections)
    return dict(report)


def _packet_alternatives(packet: Mapping[str, Any], source_keys: Any) -> list[dict[str, Any]]:
    """Normalize exact packet blocks for one candidate or diagnostic witness."""
    if not isinstance(source_keys, list):
        raise ValueError("packet witness source keys are invalid")
    keyed = {(key["view"], key["raw_index"]) for key in source_keys if isinstance(key, Mapping) and key.get("view") in VIEWS and type(key.get("raw_index")) is int}
    if len(keyed) != len(source_keys):
        raise ValueError("packet witness source keys are invalid")
    result = []
    for view in VIEWS:
        blocks = packet["views"][view].get("blocks")
        if not isinstance(blocks, list):
            raise ValueError("packet witness blocks are invalid")
        selected = []
        for block in blocks:
            if (view, block.get("raw_index")) not in keyed:
                continue
            _block_identity(block)
            selected.append({"raw_index": block["raw_index"], "type": block.get("type"), "bbox": block.get("bbox"), "text": block.get("text", ""), "text_sha256": _sha(str(block.get("text", "")).encode()), "assets": [_safe_asset(asset) for asset in block.get("assets", [])], "table_body_sha256": _sha(str(block.get("table_body", "")).encode()) if block.get("table_body") else None, "semantic_evidence": block.get("semantic_evidence", {})})
        result.append({"view": view, "blocks": selected})
    if {(view, block["raw_index"]) for row in result for block in row["blocks"] for view in [row["view"]]} != keyed:
        raise ValueError("packet witness references a missing source block")
    return result


def _verify_legacy_packet_binding(report: Mapping[str, Any], directory: Path, stage: Path, reviewed_corrections: Mapping[str, Any] | None) -> None:
    """Bind historical v2-v4 evidence without replaying a newer projection."""
    packets = {page: packet for page, _, packet in _load_packets(stage)}
    expected_diagnostics = []
    for page in report["pages"]:
        number = page["source_page"]
        packet = packets.get(number)
        if packet is None:
            raise ValueError("candidate references a missing authoritative packet")
        candidate_path = directory / _safe_asset(page["candidate"]["path"])
        candidate = json.loads(candidate_path.read_text(encoding="utf-8"))
        next_line = 1
        for entry in candidate["entries"]:
            if entry["alternatives"] != _packet_alternatives(packet, entry["source_keys"]):
                raise ValueError("candidate alternatives do not match authoritative packet")
            correction = entry.get("correction")
            if correction is not None:
                if not reviewed_corrections:
                    raise ValueError("legacy correction requires supplied authority")
                source_hash = correction.get("source_sha256") if isinstance(correction, Mapping) else None
                if not _sha_string(source_hash) or reviewed_corrections.get(source_hash) != correction:
                    raise ValueError("legacy correction does not match supplied authority")
            next_line = _verify_legacy_emitted_output(entry, number, packet, next_line, reviewed_corrections)
    for diagnostic in report["diagnostics"]:
        packet = packets.get(diagnostic["page"])
        if packet is None or diagnostic["alternatives"] != _packet_alternatives(packet, diagnostic["source_keys"]):
            raise ValueError("candidate diagnostics do not match authoritative packet")
        expected_diagnostics.append(diagnostic)
    if expected_diagnostics != report["diagnostics"]:
        raise ValueError("candidate diagnostics do not match authoritative packet")


def _verify_legacy_emitted_output(entry: Mapping[str, Any], page: int, packet: Mapping[str, Any], next_line: int,
                                  reviewed_corrections: Mapping[str, Any] | None) -> int:
    """Bind legacy rendered fields to the selected packet witness.

    Historical schemas retain their own choice and disposition rules.  Once an
    entry says it emitted output, however, its text, table form, heading, asset
    markers, offsets, and spans have one deterministic representation.
    """
    presentation = {"rule", "reader_span", "reader_text", "assets_emitted", "unit"}
    disposition = entry["disposition"]
    if disposition != "emitted":
        if presentation.intersection(entry) or entry.get("correction") is not None or entry.get("bound_correction") is not None:
            raise ValueError("non-emitted legacy entry carries rendered output")
        if disposition == "excluded_empty":
            chosen = next(block for row in entry["alternatives"] if row["view"] == entry["chosen_view"]
                          for block in row["blocks"] if block["raw_index"] == entry["raw_index"])
            if chosen["text"] or chosen["assets"] or chosen["table_body_sha256"] is not None:
                raise ValueError("legacy excluded-empty entry discards packet content")
        return next_line

    packet_blocks = {
        (view, block["raw_index"]): block
        for view in VIEWS for block in packet["views"][view]["blocks"]
    }
    chosen = packet_blocks[(entry["chosen_view"], entry["raw_index"])]
    source_text = chosen["text"]
    correction = entry.get("correction")
    if correction is not None:
        source_text, _ = _reviewed_correction(chosen, reviewed_corrections)
    table = None
    if chosen["type"] == "table":
        if not chosen["table_body"]:
            raise ValueError("legacy emitted table lacks authoritative table body")
        table = _table_markdown(chosen["table_body"])
        if table is None:
            raise ValueError("legacy emitted table has unsafe authoritative table body")
    rendered = table or source_text
    assets = [{"source_path": asset, "logical_name": _logical_asset(page, entry["raw_index"], asset)} for asset in chosen["assets"]]
    if assets:
        rendered = (rendered + "\n" if rendered else "") + "\n".join(
            f"![mechanical asset]({{{{asset:{asset['logical_name']}}}}})" for asset in assets
        )
    level = chosen["semantic_evidence"].get("text_level")
    if source_text and table is None and type(level) is int and 1 <= level <= 6:
        rendered = "#" * level + " " + rendered
    asset_only = not source_text and table is None and bool(assets)
    source_field = "table_body" if table is not None else "text"
    source_offsets = [] if asset_only else [
        {"view": key["view"], "raw_index": key["raw_index"], "field": source_field,
         "source_sha256": _sha(str(packet_blocks[(key["view"], key["raw_index"])].get(source_field, "")).encode()),
         "start": 0, "end": len(str(packet_blocks[(key["view"], key["raw_index"])].get(source_field, "")))}
        for key in entry["source_keys"]
    ]
    asset_bindings = [
        {"view": key["view"], "raw_index": key["raw_index"], **asset}
        for key in entry["source_keys"] for asset in assets
    ]
    span = _line_span("", next_line, rendered)
    expected_unit = {"kind": "asset" if asset_only else "table" if table is not None else "paragraph", "source_offsets": source_offsets,
                     "asset_bindings": asset_bindings, "reader_span": span}
    selected_key = {"view": entry["chosen_view"], "raw_index": entry["raw_index"]}
    selected_unit = {
        **expected_unit,
        "source_offsets": [] if asset_only else [offset for offset in source_offsets if {"view": offset["view"], "raw_index": offset["raw_index"]} == selected_key],
        "asset_bindings": [binding for binding in asset_bindings if {"view": binding["view"], "raw_index": binding["raw_index"]} == selected_key],
    }
    if (entry.get("reader_text") != rendered or entry.get("reader_span") != span
            or entry.get("assets_emitted") != assets or entry.get("unit") not in (expected_unit, selected_unit)):
        raise ValueError(f"legacy rendered output does not match authoritative packet: page {page}, ordinal {entry['ordinal']}")
    return next_line + len(rendered.split("\n")) + 1


def _require_supplied_legacy_correction_authority(report: Mapping[str, Any], directory: Path, reviewed_corrections: Mapping[str, Any] | None) -> None:
    """Do not let a resealed candidate become the authority for its own edit."""
    for page in report["pages"]:
        candidate_path = directory / _safe_asset(page["candidate"]["path"])
        candidate = json.loads(candidate_path.read_text(encoding="utf-8"))
        for entry in candidate["entries"]:
            correction = entry.get("correction")
            if correction is None:
                continue
            source_hash = correction.get("source_sha256") if isinstance(correction, Mapping) else None
            if not reviewed_corrections:
                raise ValueError("legacy correction requires supplied authority")
            if not _sha_string(source_hash) or reviewed_corrections.get(source_hash) != correction:
                raise ValueError("legacy correction does not match supplied authority")


def _verify_packet_authority(report: Mapping[str, Any], directory: Path, stage: Path, reviewed_corrections: Mapping[str, Any] | None) -> None:
    """Regenerate every candidate page from its sealed Stage04 packet.

    The manifest hash authenticates the candidate bytes only.  The packet is
    the source authority, so a verifier must reconstruct the output before it
    can trust a resealed candidate.  Legacy corrections remain supported, but
    their exact source witnesses are rechecked by the regenerated page.
    """
    if report["schema"] in {V2_SCHEMA, SCHEMA, V4_SCHEMA}:
        _verify_legacy_packet_binding(report, directory, stage, reviewed_corrections)
        return
    bound_corrections: Mapping[tuple[int, str, int], Any] | None = None
    bound = report["bound_reviews"]
    if bound is not None:
        from .bound_ocr_review_loader import load_bound_ocr_reviews
        ledger_path = directory / _safe_asset(bound["path"])
        _, bound_corrections = load_bound_ocr_reviews(
            Path(report["run_root"]), ledger_path, authority_validator=lambda _: stage,
        )
    else:
        _require_supplied_legacy_correction_authority(report, directory, reviewed_corrections)

    observed_diagnostics: list[Any] = []
    packets = {page: packet for page, _, packet in _load_packets(stage)}
    for page in report["pages"]:
        number = page["source_page"]
        packet = packets.get(number)
        if packet is None:
            raise ValueError("candidate references a missing authoritative packet")
        expected_page, expected_diagnostics = _aligned_page_candidate(
            number, packet, reviewed_corrections, bound_corrections,
        )
        candidate_path = directory / _safe_asset(page["candidate"]["path"])
        observed_page = json.loads(candidate_path.read_text(encoding="utf-8"))
        if observed_page != expected_page:
            raise ValueError("candidate content does not match authoritative packet")
        observed_diagnostics.extend(expected_diagnostics)
    if report["diagnostics"] != observed_diagnostics:
        raise ValueError("candidate diagnostics do not match authoritative packet")


def _validate_generated_draft(report: Mapping[str, Any], staging: Path) -> None:
    """Validate generated evidence without a test-only JSON Schema dependency."""
    expected = {"schema", "state", "authority", "run_root", "authorities", "stage04_visual_manifest", "page_count", "pages", "diagnostics", "review_flags", "unresolved_hold_count", "ruleset_version", "manifest_sha256", "bound_reviews"}
    version = {V2_SCHEMA: V2_RULESET, SCHEMA: RULESET, V4_SCHEMA: V4_RULESET, V5_SCHEMA: V5_RULESET}.get(report.get("schema"))
    if set(report) != expected or version is None or report["state"] != "mechanical_candidate_requires_review" or not _nonempty_string(report["authority"]) or not _nonempty_string(report["run_root"]) or report["review_flags"] != {"visual_reviewed": False, "accepted": False} or not _integer(report["page_count"], 1) or not isinstance(report["pages"], list) or not isinstance(report["diagnostics"], list) or not _integer(report["unresolved_hold_count"], 0) or report["ruleset_version"] != version or not _sha_string(report["manifest_sha256"]):
        raise ValueError("generated mechanical manifest violates its closed contract")
    _identity_value(report["stage04_visual_manifest"])
    if report["manifest_sha256"] != _sha(_canonical({k: v for k, v in report.items() if k != "manifest_sha256"})):
        raise ValueError("mechanical manifest seal mismatch")
    if report["bound_reviews"] is not None:
        _bound_identity_value(report["bound_reviews"], "bound review ledger")
        path = staging / _safe_asset(report["bound_reviews"]["path"])
        if _identity(path) != {k: report["bound_reviews"][k] for k in ("bytes", "sha256")}:
            raise ValueError("bound review snapshot identity mismatch")
    if (report["page_count"] != len(report["pages"])
            or [p["source_page"] for p in report["pages"]] != list(range(1, report["page_count"] + 1))
            or report["unresolved_hold_count"] != len(report["diagnostics"])):
        raise ValueError("mechanical coverage/count mismatch")
    authorities = report["authorities"]
    if not isinstance(authorities, Mapping) or set(authorities) != {"validator_route", "run", "source", "prepared_manifest", "comparison", "visual_manifest", "replay"} or authorities["validator_route"] not in {"native", "replay"}:
        raise ValueError("generated mechanical authority binding is invalid")
    for name in ("run", "prepared_manifest", "comparison", "visual_manifest"):
        _bound_identity_value(authorities[name], f"generated mechanical {name} identity")
    source = authorities["source"]
    if not isinstance(source, Mapping) or set(source) != {"path_hint", "bytes", "sha256"} or not _nonempty_string(source["path_hint"]) or not _integer(source["bytes"], 1) or not _sha_string(source["sha256"]):
        raise ValueError("generated mechanical source identity is invalid")
    if authorities["validator_route"] == "native" and authorities["replay"] is not None:
        raise ValueError("native mechanical candidate has replay authority")
    if authorities["validator_route"] == "replay":
        replay = authorities["replay"]
        if not isinstance(replay, Mapping) or set(replay) != {"bridge", "completion"}:
            raise ValueError("replay mechanical candidate lacks bridge authority")
        _bound_identity_value(replay["bridge"], "generated replay bridge identity")
        _bound_identity_value(replay["completion"], "generated replay completion identity")
    for page in report["pages"]:
        if not isinstance(page, Mapping) or set(page) != {"source_page", "packet", "candidate"} or not _integer(page["source_page"], 1):
            raise ValueError("generated mechanical page manifest is invalid")
        _bound_identity_value(page["packet"], "generated packet identity")
        _bound_identity_value(page["candidate"], "generated candidate identity")
        packet_path = Path(report["run_root"]) / "outputs/04-visual-merge-bundle/merge_packets/pages" / _safe_asset(page["packet"]["path"])
        if _identity(packet_path) != {k: page["packet"][k] for k in ("bytes", "sha256")}:
            raise ValueError("candidate packet binding mismatch")
        packet = json.loads(packet_path.read_text(encoding="utf-8"))
        candidate_path = staging / _safe_asset(page["candidate"]["path"])
        if _identity(candidate_path) != {k: page["candidate"][k] for k in ("bytes", "sha256")}:
            raise ValueError("candidate page identity mismatch")
        candidate = json.loads(candidate_path.read_text(encoding="utf-8"))
        if candidate["source_page"] != page["source_page"]:
            raise ValueError("candidate source page mismatch")
        _validate_candidate_page(candidate, schema=report["schema"])
        expected_keys = {(view, block["raw_index"]) for view in VIEWS for block in packet["views"][view]["blocks"]}
        actual_keys = {(key["view"], key["raw_index"]) for entry in candidate["entries"] for key in entry["source_keys"]}
        if expected_keys != actual_keys:
            raise ValueError("candidate does not conserve all packet source keys")
    for diagnostic in report["diagnostics"]:
        _validate_diagnostic(diagnostic)


def _integer(value: Any, minimum: int) -> bool:
    return type(value) is int and value >= minimum


def _nonempty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value)


def _sha_string(value: Any) -> bool:
    return isinstance(value, str) and re.fullmatch(r"[A-F0-9]{64}", value) is not None


def _identity_value(value: Any) -> None:
    if not isinstance(value, Mapping) or set(value) != {"bytes", "sha256"} or not _integer(value["bytes"], 0) or not _sha_string(value["sha256"]):
        raise ValueError("generated mechanical identity is invalid")


def _bound_identity_value(value: Any, label: str) -> None:
    if not isinstance(value, Mapping) or set(value) != {"path", "bytes", "sha256"} or not _nonempty_string(value["path"]) or not _integer(value["bytes"], 0) or not _sha_string(value["sha256"]):
        raise ValueError(f"{label} is invalid")


def _source_key(value: Any) -> None:
    if not isinstance(value, Mapping) or set(value) != {"view", "raw_index"} or value["view"] not in VIEWS or not _integer(value["raw_index"], 0):
        raise ValueError("generated mechanical source key is invalid")


def _span(value: Any) -> None:
    if not isinstance(value, Mapping) or set(value) != {"start_line", "end_line", "sha256"} or not _integer(value["start_line"], 1) or not _integer(value["end_line"], 1) or not _sha_string(value["sha256"]):
        raise ValueError("generated mechanical reader span is invalid")


def _alternatives(value: Any) -> None:
    if not isinstance(value, list) or len(value) != len(VIEWS) or [row.get("view") for row in value if isinstance(row, Mapping)] != list(VIEWS):
        raise ValueError("generated mechanical alternatives are invalid")
    for alternative in value:
        if not isinstance(alternative, Mapping) or set(alternative) != {"view", "blocks"} or alternative["view"] not in VIEWS or not isinstance(alternative["blocks"], list):
            raise ValueError("generated mechanical alternative is invalid")
        for block in alternative["blocks"]:
            expected = {"raw_index", "type", "bbox", "text", "text_sha256", "assets", "table_body_sha256", "semantic_evidence"}
            if not isinstance(block, Mapping) or set(block) != expected or not _integer(block["raw_index"], 0) or not isinstance(block["type"], str) or not isinstance(block["bbox"], list) or len(block["bbox"]) != 4 or any(type(item) not in {int, float} for item in block["bbox"]) or not isinstance(block["text"], str) or not _sha_string(block["text_sha256"]) or not isinstance(block["assets"], list) or any(not isinstance(item, str) for item in block["assets"]) or (block["table_body_sha256"] is not None and not _sha_string(block["table_body_sha256"])) or not isinstance(block["semantic_evidence"], Mapping):
                raise ValueError("generated mechanical alternative block is invalid")
            if block["text_sha256"] != _sha(block["text"].encode()):
                raise ValueError("alternative text hash mismatch")


def _validate_selection(entry: Mapping[str, Any], page: int, alternatives: dict, *, schema: str = SCHEMA) -> None:
    selection = entry.get("text_selection")
    chosen = alternatives[(entry["chosen_view"], entry["raw_index"])]
    bound = entry.get("bound_correction")
    if bound is not None:
        required = {"source_page", "view", "raw_index", "before", "after", "reason", "before_sha256", "after_sha256", "packet", "report", "source_render"}
        if not isinstance(bound, Mapping) or set(bound) != required:
            raise ValueError("invalid bound correction provenance")
        if (bound["source_page"] != page or bound["view"] != VIEWS[1]
                or (bound["view"], bound["raw_index"]) not in alternatives
                or not all(_nonempty_string(bound[k]) for k in ("before", "after", "reason"))
                or bound["before"] == bound["after"] or _c0(bound["after"])
                or bound["before"] != alternatives[(bound["view"], bound["raw_index"])]["text"]
                or bound["before_sha256"] != _sha(bound["before"].encode())
                or bound["after_sha256"] != _sha(bound["after"].encode())):
            raise ValueError("bound correction selector/text mismatch")
        for name in ("packet", "report", "source_render"):
            _bound_identity_value(bound[name], "bound correction evidence")
    if selection is None:
        if entry["disposition"] == "emitted":
            raise ValueError("emitted unit lacks text selection evidence")
        return
    allowed_rules = {"three_view_exact", "native_text_corrupt_recovered", "reviewed_source_correction"}
    allowed_statuses = {"selected", "corroborating", "tainted", "alternative"}
    if schema in {SCHEMA, V4_SCHEMA, V5_SCHEMA}:
        allowed_rules.add("three_view_typographic_quote_equivalent")
        if schema in {V4_SCHEMA, V5_SCHEMA}:
            allowed_rules.update({"three_view_title_ascii_case_equivalent.v1", "three_view_title_letter_spacing_equivalent.v1"})
        allowed_statuses.add("equivalent")
    if (not isinstance(selection, Mapping) or set(selection) != {"rule", "output_sha256", "view_status"}
            or selection["rule"] not in allowed_rules
            or not _sha_string(selection["output_sha256"]) or set(selection["view_status"]) != set(VIEWS)):
        raise ValueError("invalid text selection evidence")
    by_view = {view: [block for (v, _), block in alternatives.items() if v == view] for view in VIEWS}
    if any(len(rows) != 1 for rows in by_view.values()):
        raise ValueError("text selection needs a closed triangle")
    if any(selection["view_status"][view] not in allowed_statuses for view in VIEWS):
        raise ValueError("unknown view contribution status")
    expected_status = {view: "selected" if view == entry["chosen_view"] else "tainted" if _c0(by_view[view][0]["text"]) else "corroborating" if by_view[view][0]["text"] == chosen["text"] else "equivalent" if selection["rule"] in {"three_view_typographic_quote_equivalent", "three_view_title_ascii_case_equivalent.v1", "three_view_title_letter_spacing_equivalent.v1"} else "alternative" for view in VIEWS}
    if selection["view_status"] != expected_status:
        raise ValueError("view contribution status mismatch")
    rule = selection["rule"]
    texts = [by_view[view][0]["text"] for view in VIEWS]
    if rule == "three_view_exact" and (len(set(texts)) != 1 or _c0(texts[0]) or entry["chosen_view"] != VIEWS[0]):
        raise ValueError("three-view text witness mismatch")
    if rule == "native_text_corrupt_recovered" and (not _c0(texts[0]) or texts[1] != texts[2] or _c0(texts[1]) or entry["chosen_view"] != VIEWS[1]):
        raise ValueError("native corruption recovery witness mismatch")
    if rule == "reviewed_source_correction" and (bound is None or entry["chosen_view"] != VIEWS[1]):
        raise ValueError("reviewed text lacks source-bound evidence")
    if rule == "three_view_typographic_quote_equivalent":
        if schema not in {SCHEMA, V4_SCHEMA, V5_SCHEMA} or entry["chosen_view"] != VIEWS[0] or any(_c0(text) for text in texts) or not _typographic_quote_equivalent(texts):
            raise ValueError("typographic quote equivalence witness mismatch")
    if rule in {"three_view_title_ascii_case_equivalent.v1", "three_view_title_letter_spacing_equivalent.v1"}:
        from .mechanical_text_selection import _title_ascii_case_equivalent, _title_letter_spacing_equivalent, _title_like
        if schema not in {V4_SCHEMA, V5_SCHEMA} or entry["chosen_view"] != VIEWS[0] or not all(_title_like(by_view[view][0]) for view in VIEWS) or not (rule.endswith("ascii_case_equivalent.v1") and _title_ascii_case_equivalent(texts) or rule.endswith("letter_spacing_equivalent.v1") and _title_letter_spacing_equivalent(texts)):
            raise ValueError("title equivalence witness mismatch")
    output = chosen["text"]
    correction = entry.get("correction")
    if correction is not None:
        output, _ = _reviewed_correction(chosen, {chosen["text_sha256"]: correction})
    if bound is not None and entry["disposition"] == "emitted" and output != bound["after"]:
        raise ValueError("reviewed correction was not applied")
    if selection["output_sha256"] != _sha(output.encode()):
        raise ValueError("selected output hash mismatch")


def _validate_candidate_page(candidate: Mapping[str, Any], *, schema: str = SCHEMA) -> None:
    expected = {"source_page", "semantic_role", "review", "markdown", "entries", "unresolved"}
    if set(candidate) != expected or not _integer(candidate["source_page"], 1) or candidate["review"] != {"visual_reviewed": False, "state": "mechanical_candidate"} or not isinstance(candidate["markdown"], str) or not isinstance(candidate["entries"], list) or not isinstance(candidate["unresolved"], list) or any(not isinstance(item, str) for item in candidate["unresolved"]):
        raise ValueError("generated mechanical page violates its closed contract")
    seen_keys = set()
    emitted_text = []
    next_line = 1
    for entry in candidate["entries"]:
        required = {"ordinal", "chosen_view", "raw_index", "source_keys", "alternatives", "source_text_sha256", "assets", "table_body_sha256", "disposition"}
        optional = {"rule", "correction", "reader_span", "reader_text", "assets_emitted", "unit", "text_selection", "bound_correction"}
        if not isinstance(entry, Mapping) or not required <= set(entry) or not set(entry) <= required | optional or not _integer(entry["ordinal"], 0) or entry["chosen_view"] not in VIEWS or not _integer(entry["raw_index"], 0) or not isinstance(entry["source_keys"], list) or not entry["source_keys"] or not _sha_string(entry["source_text_sha256"]) or not isinstance(entry["assets"], list) or any(not isinstance(item, str) for item in entry["assets"]) or (entry["table_body_sha256"] is not None and not _sha_string(entry["table_body_sha256"])) or entry["disposition"] not in {"emitted", "hold", "excluded_empty"}:
            raise ValueError("generated mechanical entry has invalid disposition")
        for source_key in entry["source_keys"]: _source_key(source_key)
        _alternatives(entry["alternatives"])
        alternative_map = {(v["view"], b["raw_index"]): b for v in entry["alternatives"] for b in v["blocks"]}
        keys = [(k["view"], k["raw_index"]) for k in entry["source_keys"]]
        if len(set(keys)) != len(keys) or set(keys) != set(alternative_map) or seen_keys.intersection(keys):
            raise ValueError("source key coverage mismatch")
        seen_keys.update(keys)
        chosen_key = (entry["chosen_view"], entry["raw_index"])
        if chosen_key not in alternative_map or alternative_map[chosen_key]["text_sha256"] != entry["source_text_sha256"]:
            raise ValueError("chosen source text identity mismatch")
        _validate_selection(entry, candidate["source_page"], alternative_map, schema=schema)
        for name in ("rule", "reader_text"):
            if name in entry and not isinstance(entry[name], str): raise ValueError("generated mechanical entry field is invalid")
        if "reader_span" in entry: _span(entry["reader_span"])
        if "assets_emitted" in entry:
            if not isinstance(entry["assets_emitted"], list): raise ValueError("generated mechanical assets are invalid")
            for asset in entry["assets_emitted"]:
                if not isinstance(asset, Mapping) or set(asset) != {"source_path", "logical_name"} or not isinstance(asset["source_path"], str) or not isinstance(asset["logical_name"], str): raise ValueError("generated mechanical asset is invalid")
        if entry["disposition"] != "emitted":
            continue
        unit = entry.get("unit")
        if not isinstance(unit, Mapping) or set(unit) != {"kind", "source_offsets", "asset_bindings", "reader_span"} or unit["kind"] not in {"paragraph", "table", "asset"} or not isinstance(unit["source_offsets"], list) or not isinstance(unit["asset_bindings"], list):
            raise ValueError("generated mechanical unit is invalid")
        if unit["kind"] == "asset":
            if unit["source_offsets"] or not unit["asset_bindings"]:
                raise ValueError("asset unit must bind assets without synthetic source offsets")
        elif not unit["source_offsets"]:
            raise ValueError("text or table unit lacks source offsets")
        _span(unit["reader_span"])
        if (_c0(entry["reader_text"]) or entry["reader_span"] != _line_span("", next_line, entry["reader_text"])
                or unit["reader_span"] != entry["reader_span"]):
            raise ValueError("rendered reader span mismatch")
        emitted_text.append(entry["reader_text"])
        next_line += len(entry["reader_text"].split("\n")) + 1
        for offset in unit["source_offsets"]:
            if not isinstance(offset, Mapping) or set(offset) != {"view", "raw_index", "field", "source_sha256", "start", "end"} or offset["view"] not in VIEWS or not _integer(offset["raw_index"], 0) or offset["field"] not in {"text", "table_body"} or not _sha_string(offset["source_sha256"]) or not _integer(offset["start"], 0) or not _integer(offset["end"], 1): raise ValueError("generated mechanical source offset is invalid")
            block = alternative_map.get((offset["view"], offset["raw_index"]))
            if block is None or offset["source_sha256"] != block["text_sha256" if offset["field"] == "text" else "table_body_sha256"]:
                raise ValueError("source offset identity mismatch")
            if offset["field"] == "text" and (offset["start"] != 0 or offset["end"] != len(block["text"]) or _c0(block["text"])):
                raise ValueError("source offset is not usable raw text")
        for binding in unit["asset_bindings"]:
            if not isinstance(binding, Mapping) or set(binding) != {"view", "raw_index", "source_path", "logical_name"} or binding["view"] not in VIEWS or not _integer(binding["raw_index"], 0) or not _nonempty_string(binding["source_path"]) or not _nonempty_string(binding["logical_name"]): raise ValueError("generated mechanical asset binding is invalid")
            block = alternative_map.get((binding["view"], binding["raw_index"]))
            if block is None or binding["source_path"] not in block["assets"]:
                raise ValueError("asset binding references another raw block")
    if candidate["markdown"] != "\n\n".join(emitted_text):
        raise ValueError("candidate Markdown differs from emitted units")


def _validate_diagnostic(value: Any) -> None:
    expected = {"code", "page", "source_keys", "alternatives", "expected", "observed", "next_action"}
    if not isinstance(value, Mapping) or set(value) != expected or not _nonempty_string(value["code"]) or not _integer(value["page"], 1) or not isinstance(value["source_keys"], list) or not _nonempty_string(value["next_action"]):
        raise ValueError("generated mechanical diagnostic is invalid")
    for source_key in value["source_keys"]: _source_key(source_key)
    _alternatives(value["alternatives"])
