#!/usr/bin/env python3
"""Create and accept a fail-closed successor bundle for a reviewed DOCX edit."""

from __future__ import annotations

import hashlib
import json
import os
import shutil
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

from kb_creator.scripts.export_docx_to_pdf_local import export_docx
from kb_creator.scripts.normalize_publication_access import (
    normalize_publication_access_if_managed,
)
from kb_creator.scripts.publication_render_qa import render_pdf_pages
from kb_creator.scripts.verify_docx_revision_package import (
    MANIFEST_NAME,
    SCHEMA,
    canonical,
    identity,
    package_inventory,
    sha,
    verify_revision_package,
)
from kb_creator.scripts.verify_production_package import verify_package


REPO_ROOT = Path(__file__).resolve().parents[2]


class DocxRevisionError(ValueError):
    pass


LEGACY_REVISION_RETIRED = (
    "The legacy reviewed DOCX revision writer also creates HTML/PDF and is retired. "
    "Use `python -m kb_creator.scripts.revise_reviewed_docx` for a DOCX-only revision, "
    "or `python -m kb_creator translate run` for a new DOCX-only five-step run. "
    "Historical revision-package verification remains read-only."
)


def reject_legacy_revision_writer() -> None:
    raise DocxRevisionError(LEGACY_REVISION_RETIRED)


def _write(path: Path, value: object) -> None:
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_bytes(canonical(value) + b"\n")
    os.replace(temporary, path)


def _seal(value: dict[str, Any], key: str) -> dict[str, Any]:
    value[key] = hashlib.sha256(canonical(value)).hexdigest().upper()
    return value


def _role_path(manifest: dict[str, Any], role: str) -> Path:
    matches = [row for row in manifest.get("roles", []) if row.get("role") == role]
    if len(matches) != 1:
        raise DocxRevisionError(f"base package lacks unique {role} role")
    path = Path(matches[0].get("path", ""))
    if path.is_absolute() or ".." in path.parts or len(path.parts) != 1:
        raise DocxRevisionError(f"base package {role} role must be a top-level stable file")
    return path


def _footer_policy(docx: Path) -> dict[str, int]:
    import re
    import zipfile

    with zipfile.ZipFile(docx) as archive:
        names = set(archive.namelist())
        document = archive.read("word/document.xml").decode("utf-8", errors="replace")
    return {
        "footer_parts": sum(name.startswith("word/footer") and name.endswith(".xml") for name in names),
        "page_fields": len(re.findall(r"(?:PAGE|NUMPAGES)", document)),
        "footer_references": document.count("footerReference"),
    }


def _copy_release_projection(
    base: Path,
    stage: Path,
    base_manifest: dict[str, Any],
    docx_name: Path,
    pdf_name: Path,
) -> None:
    excluded = {docx_name.name, pdf_name.name, "PRODUCTION_MANIFEST.json", "README.md"}
    for source in sorted(base.iterdir(), key=lambda item: item.name):
        if source.name in excluded:
            continue
        target = stage / source.name
        if source.is_dir():
            shutil.copytree(source, target, dirs_exist_ok=True)
        else:
            shutil.copy2(source, target)

    roles = {row.get("role"): row.get("path") for row in base_manifest.get("roles", []) if isinstance(row, dict)}
    application_path = roles.get("artview_application")
    if not isinstance(application_path, str):
        return
    application = json.loads((base / application_path).read_text(encoding="utf-8"))
    for record in application.get("assets", []):
        if not isinstance(record, dict) or set(record) != {"path", "bytes", "sha256"}:
            raise DocxRevisionError("ArtView application asset identity is malformed")
        relative = Path(record["path"])
        if relative.is_absolute() or ".." in relative.parts or not relative.parts or relative.parts[0] != "assets":
            raise DocxRevisionError("ArtView application asset path is unsafe")
        destination = stage / relative
        if destination.is_file():
            source = destination
        else:
            source = base / relative
            if not source.is_file():
                source = base / "artview" / "bundle" / "assets" / "current" / Path(*relative.parts[1:])
            if not source.is_file():
                raise DocxRevisionError(f"release asset source is missing: {relative.as_posix()}")
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, destination)
        if destination.stat().st_size != record["bytes"] or sha(destination) != record["sha256"]:
            raise DocxRevisionError(f"release asset identity drift: {relative.as_posix()}")


def _manifest(root: Path, base_manifest: Path, scenario_id: str, docx: Path, pdf: Path, reference: str) -> dict[str, Any]:
    export = root / "evidence" / "docx_pdf_export.json"
    render = root / "evidence" / "final_render" / "render_inventory.json"
    page_count = json.loads(render.read_text(encoding="utf-8"))["page_count"]
    value = {
        "schema": SCHEMA,
        "scenario_id": scenario_id,
        "state": "awaiting_visual_review",
        "release_state": "not_reviewed",
        "base_package": identity(base_manifest, root),
        "reviewed_docx": identity(docx, root),
        "pdf": identity(pdf, root),
        "export_evidence": identity(export, root),
        "render_inventory": identity(render, root),
        "page_count": page_count,
        "footer_policy": _footer_policy(docx),
        "user_decision_reference": reference,
        "visual_review": None,
        "inventory": package_inventory(root),
    }
    return _seal(value, "revision_sha256")


def build_revision_package(
    base_package: Path,
    reviewed_docx: Path,
    output_root: Path,
    libreoffice: Path,
    pdftoppm: Path,
    user_decision_reference: str,
    *,
    base_verifier: Callable[[Path], dict[str, Any]] = verify_package,
    exporter: Callable[..., dict[str, Any]] = export_docx,
    renderer: Callable[..., dict[str, Any]] = render_pdf_pages,
) -> dict[str, Any]:
    reject_legacy_revision_writer()
    if not user_decision_reference.strip():
        raise DocxRevisionError("user decision reference is required")
    base = base_package.resolve(strict=True)
    reviewed = reviewed_docx.resolve(strict=True)
    if reviewed.suffix.lower() != ".docx" or not reviewed.is_file() or reviewed.is_symlink():
        raise DocxRevisionError("reviewed DOCX must be a regular file")
    if output_root.exists() or not output_root.parent.is_dir():
        raise DocxRevisionError("revision output must be absent below an existing parent")
    base_verifier(base)
    base_manifest_value = json.loads((base / "PRODUCTION_MANIFEST.json").read_text(encoding="utf-8"))
    docx_name = _role_path(base_manifest_value, "docx")
    pdf_name = _role_path(base_manifest_value, "pdf")
    scenario_id = str(base_manifest_value.get("scenario_id", "")).strip()
    if not scenario_id:
        raise DocxRevisionError("base package scenario id is missing")

    stage = Path(tempfile.mkdtemp(prefix=f".{output_root.name}.staging.", dir=output_root.parent))
    try:
        shutil.copytree(base, stage / "base_package")
        _copy_release_projection(base, stage, base_manifest_value, docx_name, pdf_name)
        final_docx = stage / docx_name
        final_pdf = stage / pdf_name
        shutil.copy2(reviewed, final_docx)
        evidence = stage / "evidence"
        evidence.mkdir(exist_ok=True)
        if (evidence / "docx_pdf_export.json").exists() or (evidence / "final_render").exists():
            raise DocxRevisionError("base evidence conflicts with revision evidence")
        exporter(
            final_docx,
            final_pdf,
            stage,
            libreoffice,
            evidence_output=evidence / "docx_pdf_export.json",
        )
        renderer(final_pdf, evidence / "final_render", pdftoppm, source_kind="final_pdf")
        footer = _footer_policy(final_docx)
        if any(footer.values()):
            raise DocxRevisionError(f"reviewed DOCX violates footer-free policy: {footer}")
        shutil.copy2(Path(__file__).with_name("verify_docx_revision_package.py"), stage / "verify.py")
        (stage / "README.md").write_text(
            "Reviewed DOCX release candidate. HTML, assets, masters, configs, ArtView, DOCX, PDF, "
            "acceptance and evidence are available directly in this directory. REVISION_MANIFEST.json "
            "is the current authority; base_package/ is immutable provenance only.\n",
            encoding="utf-8",
            newline="\n",
        )
        manifest = _manifest(
            stage,
            stage / "base_package" / "PRODUCTION_MANIFEST.json",
            scenario_id,
            final_docx,
            final_pdf,
            user_decision_reference,
        )
        _write(stage / MANIFEST_NAME, manifest)
        verify_revision_package(stage, base_verifier=base_verifier)
        normalize_publication_access_if_managed(stage)
        os.replace(stage, output_root)
    except Exception:
        shutil.rmtree(stage, ignore_errors=True)
        raise
    return verify_revision_package(output_root, base_verifier=base_verifier)


def record_visual_acceptance(package_root: Path, user_decision_reference: str) -> dict[str, Any]:
    reject_legacy_revision_writer()
    if not user_decision_reference.strip():
        raise DocxRevisionError("visual review reference is required")
    root = package_root.resolve(strict=True)
    current = verify_revision_package(root)
    if current["state"] != "awaiting_visual_review":
        raise DocxRevisionError("revision package is not awaiting visual review")
    manifest_path = root / MANIFEST_NAME
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    receipt_path = root / "VISUAL_REVIEW.json"
    if receipt_path.exists():
        raise DocxRevisionError("visual review receipt already exists")
    receipt = {
        "schema": "kb_creator.publication_docx_revision_visual_review.v1",
        "decision": "accepted",
        "decision_at_utc": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "reviewed_pages": list(range(1, int(manifest["page_count"]) + 1)),
        "user_decision_reference": user_decision_reference,
        "recorder_role": "main_orchestrator",
    }
    _write(receipt_path, _seal(receipt, "receipt_sha256"))
    manifest["state"] = "candidate_for_release_review"
    manifest["visual_review"] = identity(receipt_path, root)
    manifest["inventory"] = package_inventory(root)
    manifest.pop("revision_sha256", None)
    _write(manifest_path, _seal(manifest, "revision_sha256"))
    return verify_revision_package(root)


def materialize_release_layout(
    source_root: Path,
    output_root: Path,
    *,
    base_verifier: Callable[[Path], dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """Upgrade a sealed reviewed-DOCX bundle to a self-contained release tree."""
    reject_legacy_revision_writer()
    source = source_root.resolve(strict=True)
    if output_root.exists() or not output_root.parent.is_dir():
        raise DocxRevisionError("release output must be absent below an existing parent")
    verify_revision_package(
        source,
        base_verifier=base_verifier,
        require_release_projection=False,
    )
    source_manifest = json.loads((source / MANIFEST_NAME).read_text(encoding="utf-8"))
    base_manifest_record = source_manifest["base_package"]
    base_manifest_path = source / Path(base_manifest_record["path"])
    base = base_manifest_path.parent
    base_manifest_value = json.loads(base_manifest_path.read_text(encoding="utf-8"))
    docx_name = _role_path(base_manifest_value, "docx")
    pdf_name = _role_path(base_manifest_value, "pdf")

    stage = Path(tempfile.mkdtemp(prefix=f".{output_root.name}.staging.", dir=output_root.parent))
    try:
        shutil.copytree(source, stage, dirs_exist_ok=True)
        _copy_release_projection(base, stage, base_manifest_value, docx_name, pdf_name)
        shutil.copy2(Path(__file__).with_name("verify_docx_revision_package.py"), stage / "verify.py")
        (stage / "README.md").write_text(
            "Reviewed DOCX release candidate. HTML, assets, masters, configs, ArtView, DOCX, PDF, "
            "acceptance and evidence are available directly in this directory. REVISION_MANIFEST.json "
            "is the current authority; base_package/ is immutable provenance only.\n",
            encoding="utf-8",
            newline="\n",
        )
        manifest_path = stage / MANIFEST_NAME
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["inventory"] = package_inventory(stage)
        manifest.pop("revision_sha256", None)
        _write(manifest_path, _seal(manifest, "revision_sha256"))
        verify_revision_package(stage, base_verifier=base_verifier)
        normalize_publication_access_if_managed(stage)
        os.replace(stage, output_root)
    except Exception:
        shutil.rmtree(stage, ignore_errors=True)
        raise
    return verify_revision_package(output_root, base_verifier=base_verifier)
