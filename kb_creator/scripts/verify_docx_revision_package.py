#!/usr/bin/env python3
"""Offline verifier for a publication package revised at the reviewed DOCX gate."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import stat
import subprocess
import sys
import zipfile
from html.parser import HTMLParser
from pathlib import Path
from typing import Any, Callable
from urllib.parse import urlsplit


MANIFEST_NAME = "REVISION_MANIFEST.json"
SCHEMA = "kb_creator.publication_docx_revision.v1"


class RevisionVerificationError(ValueError):
    pass


class _Refs(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.values: list[str] = []

    def handle_starttag(self, _tag: str, attrs: list[tuple[str, str | None]]) -> None:
        for key, value in attrs:
            if key.lower() in {"src", "href"} and value:
                self.values.append(value)


def canonical(value: object) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


def sha(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def identity(path: Path, root: Path) -> dict[str, Any]:
    return {"path": path.relative_to(root).as_posix(), "bytes": path.stat().st_size, "sha256": sha(path)}


def _read(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(value, dict):
        raise RevisionVerificationError(f"JSON object required: {path.name}")
    return value


def _sealed(value: dict[str, Any], key: str, label: str) -> None:
    observed = value.get(key)
    expected = hashlib.sha256(canonical({name: item for name, item in value.items() if name != key})).hexdigest().upper()
    if not isinstance(observed, str) or not re.fullmatch(r"[0-9A-F]{64}", observed) or observed != expected:
        raise RevisionVerificationError(f"{label} seal mismatch")


def _is_reparse(path: Path) -> bool:
    metadata = os.lstat(path)
    return stat.S_ISLNK(metadata.st_mode) or bool(
        getattr(metadata, "st_file_attributes", 0)
        & getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0x400)
    )


def _safe_relative(value: object, label: str) -> Path:
    if not isinstance(value, str) or not value or "\\" in value or ":" in value:
        raise RevisionVerificationError(f"unsafe {label} path")
    path = Path(value)
    if path.is_absolute() or any(part in {"", ".", ".."} for part in path.parts):
        raise RevisionVerificationError(f"unsafe {label} path")
    return path


def _resolve(root: Path, record: object, label: str) -> Path:
    if not isinstance(record, dict) or set(record) != {"path", "bytes", "sha256"}:
        raise RevisionVerificationError(f"{label} identity shape mismatch")
    relative = _safe_relative(record["path"], label)
    path = root / relative
    cursor = path
    while True:
        if not cursor.exists() or _is_reparse(cursor):
            raise RevisionVerificationError(f"{label} contains missing or reparse content")
        if cursor == root:
            break
        cursor = cursor.parent
    if (
        not path.is_file()
        or path.stat().st_size != record["bytes"]
        or sha(path) != record["sha256"]
    ):
        raise RevisionVerificationError(f"{label} identity mismatch")
    return path


def package_inventory(root: Path) -> list[dict[str, Any]]:
    return [
        identity(path, root)
        for path in sorted(root.rglob("*"), key=lambda item: item.relative_to(root).as_posix())
        if path.is_file() and path.name != MANIFEST_NAME
    ]


def _validate_html_local_references(html_path: Path, package_root: Path) -> int:
    parser = _Refs()
    parser.feed(html_path.read_text(encoding="utf-8"))
    count = 0
    for value in parser.values:
        parts = urlsplit(value)
        if parts.scheme or parts.netloc or value.startswith(("#", "data:")) or not parts.path:
            continue
        relative = _safe_relative(parts.path, f"HTML local reference {value}")
        path = html_path.parent / relative
        cursor = path
        while True:
            if not cursor.exists() or _is_reparse(cursor):
                raise RevisionVerificationError(f"HTML local reference is missing or unsafe: {value}")
            if cursor == package_root:
                break
            if package_root not in cursor.parents:
                raise RevisionVerificationError(f"HTML local reference escapes package: {value}")
            cursor = cursor.parent
        if not path.is_file():
            raise RevisionVerificationError(f"HTML local reference is not a file: {value}")
        count += 1
    return count


def _footer_report(docx: Path) -> dict[str, int]:
    with zipfile.ZipFile(docx) as archive:
        names = set(archive.namelist())
        footer_parts = sum(name.startswith("word/footer") and name.endswith(".xml") for name in names)
        document = archive.read("word/document.xml").decode("utf-8", errors="replace")
        page_fields = len(re.findall(r"(?:PAGE|NUMPAGES)", document))
        footer_refs = document.count("footerReference")
    return {"footer_parts": footer_parts, "page_fields": page_fields, "footer_references": footer_refs}


def _default_base_verifier(base_root: Path) -> dict[str, Any]:
    verifier = base_root / "pipeline" / "verify.py"
    process = subprocess.run(
        [sys.executable, "-I", str(verifier), "--package-root", str(base_root)],
        capture_output=True,
        text=True,
        timeout=120,
        check=False,
    )
    if process.returncode != 0:
        raise RevisionVerificationError(f"embedded base package verifier failed: {process.stderr[-500:]}")
    value = json.loads(process.stdout)
    if not isinstance(value, dict) or value.get("state") != "candidate_for_release_review":
        raise RevisionVerificationError("embedded base package verifier returned an invalid state")
    return value


def verify_revision_package(
    package_root: Path,
    *,
    base_verifier: Callable[[Path], dict[str, Any]] | None = None,
    require_release_projection: bool = True,
) -> dict[str, Any]:
    root = package_root.resolve(strict=True)
    manifest = _read(root / MANIFEST_NAME)
    expected_keys = {
        "schema", "scenario_id", "state", "release_state", "base_package",
        "reviewed_docx", "pdf", "export_evidence", "render_inventory",
        "page_count", "footer_policy", "user_decision_reference",
        "visual_review", "inventory", "revision_sha256",
    }
    if set(manifest) != expected_keys or manifest.get("schema") != SCHEMA:
        raise RevisionVerificationError("revision manifest shape mismatch")
    _sealed(manifest, "revision_sha256", "revision manifest")
    if manifest.get("release_state") != "not_reviewed" or manifest.get("state") not in {
        "awaiting_visual_review", "candidate_for_release_review"
    }:
        raise RevisionVerificationError("revision state is invalid")
    if manifest.get("inventory") != package_inventory(root):
        raise RevisionVerificationError("revision package inventory mismatch")

    base_manifest = _resolve(root, manifest["base_package"], "base package manifest")
    base_root = base_manifest.parent
    (base_verifier or _default_base_verifier)(base_root)
    base_manifest_value = _read(base_manifest)
    base_roles = {
        row.get("role"): row.get("path")
        for row in base_manifest_value.get("roles", [])
        if isinstance(row, dict)
    }
    if require_release_projection:
        for role in ("master_en", "master_ru", "html"):
            raw = base_roles.get(role)
            if not isinstance(raw, str):
                continue
            relative = _safe_relative(raw, f"base {role} role")
            source = base_root / relative
            projected = root / relative
            if not source.is_file() or not projected.is_file() or identity(source, base_root)["sha256"] != identity(projected, root)["sha256"]:
                raise RevisionVerificationError(f"release projection is missing exact {role}")
        html_role = base_roles.get("html")
        if isinstance(html_role, str):
            _validate_html_local_references(root / _safe_relative(html_role, "base html role"), root)
    docx = _resolve(root, manifest["reviewed_docx"], "reviewed DOCX")
    pdf = _resolve(root, manifest["pdf"], "revised PDF")
    export_path = _resolve(root, manifest["export_evidence"], "export evidence")
    render_path = _resolve(root, manifest["render_inventory"], "render inventory")

    export = _read(export_path)
    if export.get("status") != "pass" or export.get("export", {}).get("document_input_role") != "accepted_docx":
        raise RevisionVerificationError("DOCX-to-PDF export evidence is not a final pass")
    for label, record, path in (("input", export.get("input"), docx), ("output", export.get("output"), pdf)):
        if not isinstance(record, dict) or record.get("bytes") != path.stat().st_size or record.get("sha256") != sha(path):
            raise RevisionVerificationError(f"export {label} identity mismatch")

    render = _read(render_path)
    if render.get("source_kind") != "final_pdf" or render.get("page_count") != manifest.get("page_count"):
        raise RevisionVerificationError("render inventory does not bind the final PDF")
    source = render.get("source")
    if not isinstance(source, dict) or source.get("bytes") != pdf.stat().st_size or source.get("sha256") != sha(pdf):
        raise RevisionVerificationError("render source identity mismatch")
    if render.get("signals") != {"near_blank_pages": [], "orphan_signal_pages": []}:
        raise RevisionVerificationError("render inventory contains page-quality signals")

    footer = _footer_report(docx)
    if footer != manifest.get("footer_policy") or any(footer.values()):
        raise RevisionVerificationError("reviewed DOCX footer policy failed")

    visual = manifest.get("visual_review")
    if manifest["state"] == "awaiting_visual_review":
        if visual is not None:
            raise RevisionVerificationError("pending revision cannot contain visual acceptance")
    else:
        visual_path = _resolve(root, visual, "visual review receipt")
        receipt = _read(visual_path)
        _sealed(receipt, "receipt_sha256", "visual review receipt")
        if (
            receipt.get("decision") != "accepted"
            or receipt.get("reviewed_pages") != list(range(1, manifest["page_count"] + 1))
            or not receipt.get("user_decision_reference")
        ):
            raise RevisionVerificationError("visual review receipt is incomplete")

    return {
        "schema": "kb_creator.publication_docx_revision_verification.v1",
        "state": manifest["state"],
        "release_state": manifest["release_state"],
        "page_count": manifest["page_count"],
        "docx_sha256": sha(docx),
        "pdf_sha256": sha(pdf),
        "revision_sha256": manifest["revision_sha256"],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--package-root", required=True, type=Path)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    try:
        result = verify_revision_package(args.package_root)
    except Exception as error:
        print(json.dumps({"status": "fail", "error": f"{type(error).__name__}: {error}"}, ensure_ascii=False), file=sys.stderr)
        return 2
    print(json.dumps(result, ensure_ascii=False, sort_keys=True) if args.json else result)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
