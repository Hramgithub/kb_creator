"""Apply reviewed, exact-preimage RU corrections to preliminary bilingual pages."""
from __future__ import annotations

import hashlib
import json
import os
import shutil
import tempfile
from pathlib import Path, PurePosixPath
from typing import Any


SCHEMA = "kb_creator.bilingual_page_amendments.v1"
PAGE_KEYS = {"source_page", "source_markdown_sha256", "en_markdown", "ru_markdown", "unresolved"}


class BilingualPageAmendmentError(ValueError):
    pass


def _sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest().upper()


def _identity(name: str, raw: bytes) -> dict[str, Any]:
    return {"path": name, "bytes": len(raw), "sha256": _sha(raw)}


def _json_object(raw: bytes, label: str) -> dict[str, Any]:
    try:
        value = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise BilingualPageAmendmentError(f"invalid JSON: {label}") from error
    if not isinstance(value, dict):
        raise BilingualPageAmendmentError(f"JSON object required: {label}")
    return value


def _safe_ref(value: Any) -> str:
    if not isinstance(value, str) or not value or "\\" in value or ":" in value:
        raise BilingualPageAmendmentError("unsafe reference path")
    path = PurePosixPath(value)
    if path.is_absolute() or any(part in (".", "..") for part in value.split("/")) or not path.name:
        raise BilingualPageAmendmentError("unsafe reference path")
    return value


def _pages(root: Path, count: int) -> dict[int, tuple[bytes, dict[str, Any]]]:
    if not root.is_dir() or type(count) is not int or count < 1:
        raise BilingualPageAmendmentError("invalid pages root or page count")
    expected = {f"page-{number:03}.json" for number in range(1, count + 1)}
    if {path.name for path in root.iterdir()} != expected:
        raise BilingualPageAmendmentError("missing, extra, or noncontiguous page")
    rows = {}
    for number in range(1, count + 1):
        path = root / f"page-{number:03}.json"
        raw = path.read_bytes()
        row = _json_object(raw, path.name)
        if (set(row) != PAGE_KEYS or type(row["source_page"]) is not int
                or row["source_page"] != number or not isinstance(row["en_markdown"], str)
                or not isinstance(row["ru_markdown"], str) or not isinstance(row["unresolved"], list)):
            raise BilingualPageAmendmentError(f"invalid bilingual page shape: {path.name}")
        if (not isinstance(row["source_markdown_sha256"], str)
                or row["source_markdown_sha256"].upper() != _sha(row["en_markdown"].encode("utf-8"))):
            raise BilingualPageAmendmentError(f"EN hash mismatch: {path.name}")
        rows[number] = (raw, row)
    return rows


def _validate_plan(plan: dict[str, Any], rows: dict[int, tuple[bytes, dict[str, Any]]],
                   manifest_identity: dict[str, Any]) -> tuple[dict[int, str], list[dict[str, Any]], list[dict[str, Any]]]:
    if (set(plan) != {"schema", "predecessor", "page_count", "amendments", "checks"}
            or plan["schema"] != SCHEMA or plan["page_count"] != len(rows)
            or not isinstance(plan["amendments"], list) or not plan["amendments"]
            or not isinstance(plan["checks"], list)):
        raise BilingualPageAmendmentError("amendment plan shape mismatch")
    predecessor = plan["predecessor"]
    if not isinstance(predecessor, dict) or set(predecessor) != {"manifest", "pages"}:
        raise BilingualPageAmendmentError("predecessor shape mismatch")
    if predecessor["manifest"] != manifest_identity:
        raise BilingualPageAmendmentError("stale predecessor manifest identity")
    listed = predecessor["pages"]
    if not isinstance(listed, list) or len(listed) != len(rows):
        raise BilingualPageAmendmentError("page identity coverage mismatch")
    for number, item in enumerate(listed, 1):
        name = f"page-{number:03}.json"
        if not isinstance(item, dict) or set(item) != {"path", "bytes", "sha256"}:
            raise BilingualPageAmendmentError("page identity shape mismatch")
        _safe_ref(item["path"])
        if item != _identity(name, rows[number][0]):
            raise BilingualPageAmendmentError(f"stale page identity: {name}")

    edits: dict[int, list[tuple[int, int, str, int]]] = {number: [] for number in rows}
    ledger: list[dict[str, Any]] = []
    for index, item in enumerate(plan["amendments"]):
        if not isinstance(item, dict) or set(item) != {"source_page", "before", "after", "expected_count", "reason", "evidence"}:
            raise BilingualPageAmendmentError("amendment shape mismatch")
        number = item["source_page"]
        if type(number) is not int or number not in rows:
            raise BilingualPageAmendmentError("amendment page is missing")
        before, after = item["before"], item["after"]
        if (not isinstance(before, str) or not before or not isinstance(after, str)
                or before == after or type(item["expected_count"]) is not int
                or item["expected_count"] != 1):
            raise BilingualPageAmendmentError("amendment replacement/count is invalid")
        if not isinstance(item["reason"], str) or not item["reason"].strip():
            raise BilingualPageAmendmentError("amendment reason is required")
        if (not isinstance(item["evidence"], list) or not item["evidence"]
                or any(not isinstance(ref, str) for ref in item["evidence"])):
            raise BilingualPageAmendmentError("amendment evidence is required")
        for ref in item["evidence"]:
            _safe_ref(ref)
        ru = rows[number][1]["ru_markdown"]
        if ru.count(before) != 1:
            raise BilingualPageAmendmentError(f"non-unique or stale preimage: page {number}")
        start = ru.index(before)
        edits[number].append((start, start + len(before), after, index))
        ledger.append({"source_page": number, "before": before, "after": after,
                       "before_span_chars": {"start": start, "end": start + len(before)},
                       "reason": item["reason"], "evidence": item["evidence"]})
    successor = {}
    for number, (_, row) in rows.items():
        ru = row["ru_markdown"]
        cursor = 0
        chunks = []
        for start, end, after, index in sorted(edits[number]):
            if start < cursor:
                raise BilingualPageAmendmentError(f"conflicting or overlapping amendments: page {number}")
            chunks.extend((ru[cursor:start], after))
            cursor = end
        chunks.append(ru[cursor:])
        successor[number] = "".join(chunks)
    checks = []
    for check in plan["checks"]:
        if not isinstance(check, dict) or set(check) != {"source_page", "text", "expected_count", "reason", "evidence"}:
            raise BilingualPageAmendmentError("continuation check shape mismatch")
        number = check["source_page"]
        if type(number) is not int or number not in rows:
            raise BilingualPageAmendmentError("continuation check page is missing")
        if (not isinstance(check["text"], str) or not check["text"]
                or type(check["expected_count"]) is not int or check["expected_count"] != 1
                or not isinstance(check["reason"], str) or not check["reason"].strip()
                or not isinstance(check["evidence"], list) or not check["evidence"]):
            raise BilingualPageAmendmentError("continuation check is invalid")
        for ref in check["evidence"]:
            _safe_ref(ref)
        if successor[number].count(check["text"]) != 1:
            raise BilingualPageAmendmentError(f"continuation check failed: page {number}")
        checks.append({**check, "actual_count": 1})
    return successor, ledger, checks


def amend_pages(pages_root: Path, manifest_path: Path, plan_path: Path, output_root: Path) -> dict[str, Any]:
    """Validate every input, then publish an absent, immutable successor directory."""
    pages_root, manifest_path, plan_path, output_root = (Path(path).resolve() for path in
                                                       (pages_root, manifest_path, plan_path, output_root))
    if output_root.exists() or not output_root.parent.is_dir():
        raise BilingualPageAmendmentError("output root must be absent below an existing parent")
    try:
        plan_bytes = plan_path.read_bytes()
        manifest_bytes = manifest_path.read_bytes()
    except OSError as error:
        raise BilingualPageAmendmentError("plan or predecessor manifest cannot be read") from error
    plan = _json_object(plan_bytes, "amendment plan")
    rows = _pages(pages_root, plan.get("page_count"))
    manifest_identity = _identity(manifest_path.name, manifest_bytes)
    successor, ledger, checks = _validate_plan(plan, rows, manifest_identity)
    staging = Path(tempfile.mkdtemp(prefix=f".{output_root.name}.", dir=output_root.parent))
    try:
        target_pages = staging / "pages"
        target_pages.mkdir()
        output_inventory = []
        for number, (raw, row) in rows.items():
            name = f"page-{number:03}.json"
            if successor[number] == row["ru_markdown"]:
                output_raw = raw
            else:
                changed = dict(row)
                changed["ru_markdown"] = successor[number]
                output_raw = (json.dumps(changed, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
            (target_pages / name).write_bytes(output_raw)
            output_inventory.append({"source_page": number, **_identity(name, output_raw)})
        (staging / "reviewed-amendments.json").write_bytes(plan_bytes)
        changed_pages = [number for number, (raw, _) in rows.items()
                         if raw != (target_pages / f"page-{number:03}.json").read_bytes()]
        report = {"schema": "kb_creator.bilingual_page_amendment_successor.v1",
                  "state": "preliminary_ru_amendments_pending_final_source_binding",
                  "accepted": False, "translation_semantics_validated": False,
                  "inputs": {"manifest": manifest_identity,
                             "pages": [{"source_page": number, **_identity(f"page-{number:03}.json", raw)}
                                       for number, (raw, _) in rows.items()]},
                  "archived_plan": _identity("reviewed-amendments.json", plan_bytes),
                  "outputs": {"pages": output_inventory},
                  "changed_pages": changed_pages, "unchanged_page_count": len(rows) - len(changed_pages),
                  "amendments": ledger, "checks": checks}
        (staging / "MANIFEST.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        os.rename(staging, output_root)
    finally:
        if staging.exists():
            shutil.rmtree(staging)
    return report
