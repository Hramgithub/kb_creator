"""Exact, review-authorized RU span moves between preliminary bilingual pages.

This is deliberately a transport tool.  It never translates, aligns units, or
asserts that the resulting text is suitable for a source binding.
"""
from __future__ import annotations

import hashlib
import json
import os
import shutil
import tempfile
from collections import Counter, defaultdict
from pathlib import Path, PurePosixPath
from typing import Any


SCHEMA = "kb_creator.bilingual_boundary_moves.v1"
PAGE_KEYS = {"source_page", "source_markdown_sha256", "en_markdown", "ru_markdown", "unresolved"}


class BilingualBoundaryMoveError(ValueError):
    pass


def _sha_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest().upper()


def _sha_text(value: str) -> str:
    return _sha_bytes(value.encode("utf-8"))


def _identity(path: Path, *, name: str | None = None) -> dict[str, Any]:
    raw = path.read_bytes()
    return {"path": name or path.name, "bytes": len(raw), "sha256": _sha_bytes(raw)}


def _read_json(path: Path) -> dict[str, Any]:
    return _parse_json(path.read_bytes(), path)


def _parse_json(raw: bytes, path: Path) -> dict[str, Any]:
    try:
        value = json.loads(raw.decode("utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as error:
        raise BilingualBoundaryMoveError(f"cannot read JSON: {path}") from error
    if not isinstance(value, dict):
        raise BilingualBoundaryMoveError(f"JSON object required: {path}")
    return value


def _safe_relative(value: Any) -> str:
    if not isinstance(value, str) or not value:
        raise BilingualBoundaryMoveError("plan path is invalid")
    path = PurePosixPath(value)
    if path.is_absolute() or ".." in path.parts or "\\" in value or ":" in value:
        raise BilingualBoundaryMoveError("plan path escapes its authority root")
    return value


def _decode_span(raw: bytes, start: Any, end: Any, *, label: str) -> str:
    if type(start) is not int or type(end) is not int or not 0 <= start < end <= len(raw):
        raise BilingualBoundaryMoveError(f"{label} UTF-8 span is invalid")
    try:
        return raw[start:end].decode("utf-8")
    except UnicodeDecodeError as error:
        raise BilingualBoundaryMoveError(f"{label} splits a UTF-8 character") from error


def _page_rows(root: Path, count: int) -> dict[int, tuple[Path, bytes, dict[str, Any]]]:
    if not root.is_dir() or type(count) is not int or count < 1:
        raise BilingualBoundaryMoveError("pages root/count is invalid")
    names = {path.name for path in root.iterdir() if path.is_file()}
    expected = {f"page-{page:03}.json" for page in range(1, count + 1)}
    if names != expected:
        raise BilingualBoundaryMoveError("page inventory is not complete and contiguous")
    result = {}
    for page in range(1, count + 1):
        path = root / f"page-{page:03}.json"; raw = path.read_bytes(); row = _parse_json(raw, path)
        if set(row) != PAGE_KEYS or row.get("source_page") != page or not isinstance(row["en_markdown"], str) or not isinstance(row["ru_markdown"], str) or not isinstance(row["unresolved"], list):
            raise BilingualBoundaryMoveError("bilingual page does not have the exact five-field shape")
        if not isinstance(row["source_markdown_sha256"], str) or row["source_markdown_sha256"].upper() != _sha_text(row["en_markdown"]):
            raise BilingualBoundaryMoveError("bilingual page EN hash mismatch")
        result[page] = (path, raw, row)
    return result


def _plan_inputs(plan: dict[str, Any], plan_path: Path, pages_root: Path, manifest_path: Path) -> tuple[int, list[dict[str, Any]], list[dict[str, Any]], dict[int, tuple[Path, bytes, dict[str, Any]]], dict[str, Any]]:
    required = {"schema", "predecessor", "page_count", "moves", "whitespace_edits"}
    if set(plan) != required or plan.get("schema") != SCHEMA or not isinstance(plan.get("moves"), list) or not isinstance(plan.get("whitespace_edits"), list):
        raise BilingualBoundaryMoveError("plan schema/shape mismatch")
    predecessor = plan["predecessor"]
    if not isinstance(predecessor, dict) or set(predecessor) != {"manifest", "pages"} or not isinstance(predecessor["pages"], list):
        raise BilingualBoundaryMoveError("plan predecessor shape mismatch")
    expected_manifest = predecessor["manifest"]
    manifest_identity = _identity(manifest_path)
    if expected_manifest != manifest_identity:
        raise BilingualBoundaryMoveError("predecessor manifest identity is stale")
    page_count = plan["page_count"]
    rows = _page_rows(pages_root, page_count)
    listed = predecessor["pages"]
    if len(listed) != page_count:
        raise BilingualBoundaryMoveError("predecessor page identity coverage mismatch")
    expected_paths = set()
    captured_identities = {path.name: {"path": path.name, "bytes": len(raw), "sha256": _sha_bytes(raw)}
                           for path, raw, _ in rows.values()}
    for item in listed:
        if not isinstance(item, dict) or set(item) != {"path", "bytes", "sha256"}:
            raise BilingualBoundaryMoveError("predecessor page identity is malformed")
        name = _safe_relative(item["path"])
        expected_paths.add(name)
        if item != captured_identities.get(name):
            raise BilingualBoundaryMoveError("predecessor page identity is stale")
    if expected_paths != {path.name for path, _, _ in rows.values()}:
        raise BilingualBoundaryMoveError("predecessor page identity coverage mismatch")
    return page_count, plan["moves"], plan["whitespace_edits"], rows, manifest_identity


def _validated_edits(rows: dict[int, tuple[Path, bytes, dict[str, Any]]], moves: list[dict[str, Any]], whitespace: list[dict[str, Any]]) -> tuple[dict[int, list[dict[str, Any]]], dict[int, list[dict[str, Any]]], dict[int, list[dict[str, Any]]], list[dict[str, Any]]]:
    deletions: dict[int, list[dict[str, Any]]] = defaultdict(list)
    inserts: dict[int, list[dict[str, Any]]] = defaultdict(list)
    evidence = []
    move_keys = {"source_page", "target_page", "source_span", "source_text", "source_text_sha256", "target_insert_byte", "target_suffix", "rationale"}
    for index, move in enumerate(moves):
        if not isinstance(move, dict) or set(move) != move_keys:
            raise BilingualBoundaryMoveError("move shape mismatch")
        source, target = move["source_page"], move["target_page"]
        if type(source) is not int or type(target) is not int or source not in rows or target not in rows or source == target:
            raise BilingualBoundaryMoveError("move page identity is invalid")
        span = move["source_span"]
        if not isinstance(span, dict) or set(span) != {"start_byte", "end_byte"}:
            raise BilingualBoundaryMoveError("move source span shape mismatch")
        source_raw = rows[source][2]["ru_markdown"].encode("utf-8")
        text = _decode_span(source_raw, span["start_byte"], span["end_byte"], label="move")
        if not text or move["source_text"] != text or move["source_text_sha256"] != _sha_text(text):
            raise BilingualBoundaryMoveError("move source text/hash is stale")
        target_raw = rows[target][2]["ru_markdown"].encode("utf-8")
        offset = move["target_insert_byte"]
        if type(offset) is not int or not 0 <= offset <= len(target_raw):
            raise BilingualBoundaryMoveError("move target insertion offset is invalid")
        try:
            target_raw[:offset].decode("utf-8")
        except UnicodeDecodeError as error:
            raise BilingualBoundaryMoveError("move target insertion splits a UTF-8 character") from error
        if not isinstance(move["target_suffix"], str) or any(not char.isspace() for char in move["target_suffix"]) or not isinstance(move["rationale"], str) or not move["rationale"].strip():
            raise BilingualBoundaryMoveError("move suffix/rationale is invalid")
        deletion = {"start": span["start_byte"], "end": span["end_byte"], "text": text, "move_index": index}
        deletions[source].append(deletion); inserts[target].append({"offset": offset, "text": text + move["target_suffix"], "moved_text": text, "move_index": index})
        evidence.append({"source_page": source, "target_page": target, "source_span": span, "source_text_sha256": _sha_text(text), "target_insert_byte": offset, "rationale": move["rationale"]})
    whitespace_by_page: dict[int, list[dict[str, Any]]] = defaultdict(list)
    ws_keys = {"page", "span", "replacement", "rationale"}
    for edit in whitespace:
        if not isinstance(edit, dict) or set(edit) != ws_keys or edit.get("page") not in rows:
            raise BilingualBoundaryMoveError("whitespace edit shape mismatch")
        span = edit["span"]
        if not isinstance(span, dict) or set(span) != {"start_byte", "end_byte"}:
            raise BilingualBoundaryMoveError("whitespace edit span shape mismatch")
        raw = rows[edit["page"]][2]["ru_markdown"].encode("utf-8")
        old = _decode_span(raw, span["start_byte"], span["end_byte"], label="whitespace edit")
        if not old or not old.isspace() or not isinstance(edit["replacement"], str) or (edit["replacement"] and not edit["replacement"].isspace()) or not isinstance(edit["rationale"], str) or not edit["rationale"].strip():
            raise BilingualBoundaryMoveError("whitespace edit is not explicit whitespace-only")
        whitespace_by_page[edit["page"]].append({"start": span["start_byte"], "end": span["end_byte"], "text": edit["replacement"]})
    for page in rows:
        intervals = [(entry["start"], entry["end"]) for entry in deletions[page] + whitespace_by_page[page]]
        if len({entry["offset"] for entry in inserts[page]}) != len(inserts[page]):
            raise BilingualBoundaryMoveError("conflicting target insertions")
        for offset in (entry["offset"] for entry in inserts[page]):
            if any(start < offset < end for start, end in intervals):
                raise BilingualBoundaryMoveError("target insertion conflicts with source edit")
        for (_, end), (start, _) in zip(sorted(intervals), sorted(intervals)[1:]):
            if start < end:
                raise BilingualBoundaryMoveError("duplicate or overlapping source edits")
    return deletions, whitespace_by_page, inserts, evidence


def _compose_page(raw: bytes, replacements: list[tuple[int, int, str]], inserts: list[dict[str, Any]], *, page: int, evidence: list[dict[str, Any]]) -> tuple[str, list[dict[str, Any]]]:
    """Compose only reviewed operations and record exact inherited fragments."""
    cursor = out_cursor = 0; chunks: list[bytes] = []; fragments: list[dict[str, Any]] = []
    def inherited(end: int) -> None:
        nonlocal cursor, out_cursor
        if end > cursor:
            piece = raw[cursor:end]; chunks.append(piece)
            fragments.append({"predecessor_span": {"start_byte": cursor, "end_byte": end}, "successor_span": {"start_byte": out_cursor, "end_byte": out_cursor + len(piece)}, "sha256": _sha_bytes(piece)})
            out_cursor += len(piece); cursor = end
    def insertion(item: dict[str, Any]) -> None:
        nonlocal out_cursor
        payload = item["text"].encode("utf-8"); chunks.append(payload)
        moved = item["moved_text"].encode("utf-8")
        evidence[item["move_index"]]["successor_destination"] = {"page": page, "span": {"start_byte": out_cursor, "end_byte": out_cursor + len(moved)}, "sha256": _sha_bytes(moved)}
        out_cursor += len(payload)
    pending = iter(sorted(inserts, key=lambda item: item["offset"])); current = next(pending, None)
    for start, end, replacement in sorted(replacements):
        while current is not None and current["offset"] <= start:
            inherited(current["offset"]); insertion(current); current = next(pending, None)
        inherited(start); payload = replacement.encode("utf-8"); chunks.append(payload); out_cursor += len(payload); cursor = end
    while current is not None:
        inherited(current["offset"]); insertion(current); current = next(pending, None)
    inherited(len(raw))
    return b"".join(chunks).decode("utf-8"), fragments


def move_pages(pages_root: Path, manifest_path: Path, plan_path: Path, output_root: Path) -> dict[str, Any]:
    """Preflight and materialize a fresh successor directory."""
    pages_root, manifest_path, plan_path, output_root = (path.resolve() for path in (pages_root, manifest_path, plan_path, output_root))
    if output_root.exists() or not output_root.parent.is_dir():
        raise BilingualBoundaryMoveError("output root must be absent below an existing parent")
    try:
        plan_bytes = plan_path.read_bytes()
    except OSError as error:
        raise BilingualBoundaryMoveError(f"cannot read JSON: {plan_path}") from error
    plan = _parse_json(plan_bytes, plan_path)
    count, moves, whitespace, rows, manifest_identity = _plan_inputs(plan, plan_path, pages_root, manifest_path)
    deletions, whitespace_by_page, inserts, evidence = _validated_edits(rows, moves, whitespace)
    before = "".join(rows[page][2]["ru_markdown"] for page in sorted(rows))
    successor: dict[int, str] = {}; unchanged_fragments: dict[int, list[dict[str, Any]]] = {}
    for page, (_, _, row) in rows.items():
        actions = [(item["start"], item["end"], "") for item in deletions[page]] + [(item["start"], item["end"], item["text"]) for item in whitespace_by_page[page]]
        successor[page], unchanged_fragments[page] = _compose_page(row["ru_markdown"].encode("utf-8"), actions, inserts[page], page=page, evidence=evidence)
    after = "".join(successor[page] for page in sorted(successor))
    if Counter(char for char in before if not char.isspace()) != Counter(char for char in after if not char.isspace()):
        raise BilingualBoundaryMoveError("non-whitespace RU character multiset conservation failed")
    staging = Path(tempfile.mkdtemp(prefix=f".{output_root.name}.", dir=output_root.parent))
    try:
        pages_out = staging / "pages"; pages_out.mkdir()
        output_pages = []
        for page, (path, raw, row) in rows.items():
            target = pages_out / path.name
            if not deletions[page] and not whitespace_by_page[page] and not inserts[page]:
                target.write_bytes(raw)
            else:
                changed = dict(row); changed["ru_markdown"] = successor[page]
                target.write_text(json.dumps(changed, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            output_pages.append({"source_page": page, **_identity(target)})
        archived = staging / "reviewed-boundary-moves.json"; archived.write_bytes(plan_bytes)
        report = {"schema": "kb_creator.bilingual_boundary_successor.v1", "state": "preliminary_boundary_successor_pending_source_binding", "accepted": False, "translation_semantics_validated": False, "inputs": {"manifest": manifest_identity, "pages": [{"source_page": page, "path": path.name, "bytes": len(raw), "sha256": _sha_bytes(raw)} for page, (path, raw, _) in rows.items()]}, "archived_plan": _identity(archived), "outputs": {"pages": output_pages}, "moves": evidence, "conservation": {"exact_transport_construction": True, "unchanged_fragment_order": [{"page": page, "fragments": unchanged_fragments[page]} for page in sorted(rows)], "non_whitespace_ru_character_multiset_conserved": True, "explicit_whitespace_edits": len(whitespace)}}
        (staging / "MANIFEST.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        os.rename(staging, output_root)
    finally:
        if staging.exists(): shutil.rmtree(staging)
    return report
