"""Freeze and verify the accepted Innsmouth PDF release package."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import tempfile
from typing import Any


KB_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CANDIDATE_ROOT = (
    KB_ROOT / "working" / "innsmouth_direct_pdf" / "accepted_20260830_candidate_r6"
)
DEFAULT_HTML_ROOT = KB_ROOT / "inputs" / "innsmouth" / "html" / "accepted_20260830_r2"
DEFAULT_TARGET_ROOT = KB_ROOT / "inputs" / "innsmouth" / "pdf" / "accepted_20260830_r2"

PDF_NAME = "The_Innsmouth_Terror_RU.pdf"
QA_NAME = "PDF.qa.json"
MANIFEST_NAME = "PDF.acceptance.json"
ACCEPTED_ON = "2026-08-30"

EXPECTED_PDF_BYTES = 11_566_429
EXPECTED_PDF_SHA256 = "8D79F72CB61626B05DE7EC000E140FA0C893C6B3D2DC693A64DF45AF756AE202"
EXPECTED_QA_BYTES = 17_070
EXPECTED_QA_SHA256 = "E97EEA81908D53C6608D06646C4227C21DE36DC6DD3425460807714D752FA86B"
EXPECTED_RENDER_INVENTORY_SHA256 = (
    "2525BD8F3BE73312063D0914209F786EF832969C20F9C166650D4CDEEBE37E42"
)
EXPECTED_HTML = {
    "bytes": 223_459,
    "name": "The_Innsmouth_Terror_RU.html",
    "sha256": "040C7AF42A76241B3BC280350C0151096CF81E5F9A9194E6F5003B0388E4EF39",
}
EXPECTED_HTML_MANIFEST = {
    "bytes": 6_966,
    "name": "HTML.acceptance.json",
    "sha256": "B0ADDD901CCD0DED10D84D331B3F168987070558641D374F13ABC30852E6D7E6",
}


def sha256(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest().upper()


def canonical_json(value: Any) -> bytes:
    return (
        json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        + "\n"
    ).encode("utf-8")


def file_identity(path: Path) -> dict[str, Any]:
    raw = path.read_bytes()
    return {"name": path.name, "bytes": len(raw), "sha256": sha256(raw)}


def render_inventory(rows: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], str]:
    compact = [
        {key: row[key] for key in ("page", "bytes", "sha256", "width", "height")}
        for row in rows
    ]
    raw = json.dumps(compact, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    return compact, sha256(raw)


def inspect_candidate(candidate_root: Path, html_root: Path) -> dict[str, Any]:
    pdf = candidate_root / PDF_NAME
    qa_path = candidate_root / QA_NAME
    if not pdf.is_file() or not qa_path.is_file():
        raise ValueError("final PDF candidate package is incomplete")

    pdf_identity = file_identity(pdf)
    if pdf_identity != {
        "name": PDF_NAME,
        "bytes": EXPECTED_PDF_BYTES,
        "sha256": EXPECTED_PDF_SHA256,
    }:
        raise ValueError("final PDF candidate identity mismatch")

    qa_identity = file_identity(qa_path)
    if qa_identity["bytes"] != EXPECTED_QA_BYTES or qa_identity["sha256"] != EXPECTED_QA_SHA256:
        raise ValueError("final PDF QA identity mismatch")
    qa = json.loads(qa_path.read_text(encoding="utf-8"))
    if qa.get("status") != "pass" or qa.get("findings") != []:
        raise ValueError("final PDF QA did not pass")
    if qa.get("pdf", {}).get("bytes") != EXPECTED_PDF_BYTES or qa.get("pdf", {}).get("sha256") != EXPECTED_PDF_SHA256:
        raise ValueError("final PDF QA file identity mismatch")

    html_identity = file_identity(html_root / EXPECTED_HTML["name"])
    html_manifest_identity = file_identity(html_root / EXPECTED_HTML_MANIFEST["name"])
    if html_identity != EXPECTED_HTML or html_manifest_identity != EXPECTED_HTML_MANIFEST:
        raise ValueError("accepted HTML provenance identity mismatch")
    source_html = qa.get("source_accepted_html", {})
    if source_html.get("html") != EXPECTED_HTML or source_html.get("manifest") != EXPECTED_HTML_MANIFEST:
        raise ValueError("final PDF QA accepted-HTML provenance mismatch")

    structural = qa.get("structural", {})
    expected_structural = {
        "pages": 46,
        "text_characters": 97_421,
        "image_xobjects": 32,
        "link_annotations": 88,
        "internal_links": 88,
        "empty_pages": [],
        "page_sizes": [[594.96, 841.92]],
    }
    for key, expected in expected_structural.items():
        if structural.get(key) != expected:
            raise ValueError(f"final PDF structural gate mismatch: {key}")
    front_matter = structural.get("front_matter", {})
    if not front_matter.get("checked") or not all(front_matter.get("checks", {}).values()):
        raise ValueError("final PDF front-matter gate mismatch")

    renders = qa.get("renders", {})
    rows = renders.get("files", [])
    if renders.get("count") != 46 or renders.get("dpi") != 120 or len(rows) != 46:
        raise ValueError("final PDF render-count gate mismatch")
    compact_rows, inventory_sha = render_inventory(rows)
    if inventory_sha != EXPECTED_RENDER_INVENTORY_SHA256:
        raise ValueError("final PDF render inventory mismatch")
    rendered_root = candidate_root / "QA" / "rendered_pages"
    for row in rows:
        rendered = rendered_root / Path(str(row["path"])).name
        identity = file_identity(rendered)
        if identity["bytes"] != row["bytes"] or identity["sha256"] != row["sha256"]:
            raise ValueError(f"final PDF rendered-page identity mismatch: {row['page']}")

    return {
        "pdf": pdf_identity,
        "source_accepted_html": {
            "html": html_identity,
            "manifest": html_manifest_identity,
        },
        "structural": expected_structural,
        "front_matter": front_matter,
        "visual_qa": {
            "render_count": 46,
            "dpi": 120,
            "render_inventory_sha256": inventory_sha,
            "first_page_sha256": compact_rows[0]["sha256"],
            "last_page_sha256": compact_rows[-1]["sha256"],
        },
        "candidate_qa": qa_identity,
    }


def acceptance_manifest(validation: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema": "kb_creator.innsmouth.accepted_pdf.v1",
        "accepted_on": ACCEPTED_ON,
        "acceptance": "user_assumed_visual_acceptance_after_full_pipeline_qa",
        **validation,
        "rules": {
            "source_is_frozen_accepted_html": True,
            "generated_pdf_manual_edit_forbidden": True,
            "all_pages_rendered_and_reviewed": True,
        },
    }


def promote(candidate_root: Path, html_root: Path, target_root: Path) -> dict[str, Any]:
    validation = inspect_candidate(candidate_root, html_root)
    if target_root.exists():
        raise FileExistsError(f"accepted PDF target already exists: {target_root}")
    target_root.parent.mkdir(parents=True, exist_ok=True)
    stage = Path(tempfile.mkdtemp(prefix=f".{target_root.name}.stage-", dir=target_root.parent))
    try:
        shutil.copy2(candidate_root / PDF_NAME, stage / PDF_NAME)
        (stage / MANIFEST_NAME).write_bytes(canonical_json(acceptance_manifest(validation)))
        os.replace(stage, target_root)
    finally:
        if stage.exists():
            shutil.rmtree(stage)
    return verify(target_root)


def verify(target_root: Path) -> dict[str, Any]:
    allowed = {PDF_NAME, MANIFEST_NAME}
    actual = {path.name for path in target_root.iterdir()} if target_root.is_dir() else set()
    if actual != allowed:
        raise ValueError(f"accepted PDF root inventory mismatch: {sorted(actual)}")
    pdf_identity = file_identity(target_root / PDF_NAME)
    if pdf_identity != {
        "name": PDF_NAME,
        "bytes": EXPECTED_PDF_BYTES,
        "sha256": EXPECTED_PDF_SHA256,
    }:
        raise ValueError("accepted PDF identity mismatch")
    manifest_path = target_root / MANIFEST_NAME
    manifest_raw = manifest_path.read_bytes()
    manifest = json.loads(manifest_raw.decode("utf-8"))
    expected = canonical_json(acceptance_manifest({
        key: manifest[key]
        for key in (
            "pdf",
            "source_accepted_html",
            "structural",
            "front_matter",
            "visual_qa",
            "candidate_qa",
        )
    }))
    if manifest_raw != expected:
        raise ValueError("accepted PDF manifest mismatch")
    if manifest.get("pdf") != pdf_identity:
        raise ValueError("accepted PDF manifest file identity mismatch")
    if manifest.get("source_accepted_html") != {
        "html": EXPECTED_HTML,
        "manifest": EXPECTED_HTML_MANIFEST,
    }:
        raise ValueError("accepted PDF manifest HTML provenance mismatch")
    if manifest.get("candidate_qa") != {
        "name": QA_NAME,
        "bytes": EXPECTED_QA_BYTES,
        "sha256": EXPECTED_QA_SHA256,
    }:
        raise ValueError("accepted PDF manifest candidate-QA identity mismatch")
    expected_structural = {
        "pages": 46,
        "text_characters": 97_421,
        "image_xobjects": 32,
        "link_annotations": 88,
        "internal_links": 88,
        "empty_pages": [],
        "page_sizes": [[594.96, 841.92]],
    }
    if manifest.get("structural") != expected_structural:
        raise ValueError("accepted PDF manifest structural summary mismatch")
    front_matter = manifest.get("front_matter", {})
    if not front_matter.get("checked") or not all(front_matter.get("checks", {}).values()):
        raise ValueError("accepted PDF manifest front-matter mismatch")
    visual = manifest.get("visual_qa", {})
    if visual.get("render_inventory_sha256") != EXPECTED_RENDER_INVENTORY_SHA256:
        raise ValueError("accepted PDF manifest visual QA mismatch")
    return {
        "state": "ACCEPTED_INNSMOUTH_PDF_REPO_OUTPUT_VERIFIED",
        "pdf": pdf_identity,
        "manifest": file_identity(manifest_path),
        "source_accepted_html": manifest["source_accepted_html"],
        "structural": manifest["structural"],
        "visual_qa": visual,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--preflight", action="store_true")
    mode.add_argument("--promote", action="store_true")
    mode.add_argument("--verify", action="store_true")
    parser.add_argument("--candidate", type=Path, default=DEFAULT_CANDIDATE_ROOT)
    parser.add_argument("--html-root", type=Path, default=DEFAULT_HTML_ROOT)
    parser.add_argument("--target", type=Path, default=DEFAULT_TARGET_ROOT)
    args = parser.parse_args()

    if args.preflight:
        result = inspect_candidate(args.candidate.resolve(), args.html_root.resolve())
        marker = "INNSMOUTH_ACCEPTED_PDF_PREFLIGHT_OK"
    elif args.promote:
        result = promote(args.candidate.resolve(), args.html_root.resolve(), args.target.resolve())
        marker = "INNSMOUTH_ACCEPTED_PDF_PROMOTION_OK"
    else:
        result = verify(args.target.resolve())
        marker = "INNSMOUTH_ACCEPTED_PDF_REPO_OUTPUT_OK"
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    print(marker)


if __name__ == "__main__":
    main()
