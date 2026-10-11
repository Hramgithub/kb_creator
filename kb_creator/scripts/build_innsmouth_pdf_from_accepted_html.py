"""Build and verify an Innsmouth PDF strictly from the accepted HTML package."""

from __future__ import annotations

import argparse
import hashlib
import html as html_lib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
from typing import Any

from PIL import Image


KB_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = KB_ROOT.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))
if str(Path(__file__).resolve().parent) not in sys.path:
    sys.path.insert(0, str(Path(__file__).resolve().parent))

from translator import translator
import freeze_innsmouth_html_repo_input as freeze_html


DEFAULT_HTML_ROOT = KB_ROOT / "inputs" / "innsmouth" / "html" / "accepted_20260830_r2"
DEFAULT_OUTPUT_ROOT = (
    KB_ROOT / "working" / "innsmouth_direct_pdf" / "accepted_20260830_candidate_r6"
)
DEFAULT_TEMP_ROOT = KB_ROOT / "tmp" / "pdfs" / "innsmouth_direct_pdf_r6"
PDF_NAME = "The_Innsmouth_Terror_RU.pdf"
CONFIG_NAME = "innsmouth_direct_pdf.package.json"
QA_NAME = "PDF.qa.json"
PRINT_SOURCE_NAME = "The_Innsmouth_Terror_RU.print.html"
ACCEPTED_HTML_MANIFEST_BYTES = 6_966
ACCEPTED_HTML_MANIFEST_SHA256 = (
    "B0ADDD901CCD0DED10D84D331B3F168987070558641D374F13ABC30852E6D7E6"
)

EDGE_CANDIDATES = (
    Path("C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe"),
    Path("C:/Program Files/Microsoft/Edge/Application/msedge.exe"),
    Path("C:/Program Files/Google/Chrome/Application/chrome.exe"),
)
POPPLER_RELATIVE = Path(".tools/poppler/poppler-26.02.0/Library/bin")
SENTINELS = (
    "УЖАС ИННСМУТА",
    "СОДЕРЖАНИЕ",
    "ПРИВЛЕЧЕНИЕ СЫЩИКОВ",
    "ПЕРСОНАЖИ И ЧУДОВИЩА",
    "ШОГГОТ",
    "РАЗДАТОЧНЫЕ МАТЕРИАЛЫ",
    "Раздаточный материал 1-a",
    "Раздаточный материал 1-b",
    "Раздаточный материал 2",
)


def sha256(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest().upper()


def canonical_json(value: Any) -> bytes:
    return (
        json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        + "\n"
    ).encode("utf-8")


def config_path_value(path: Path) -> str:
    try:
        return path.resolve().relative_to(REPO_ROOT).as_posix()
    except ValueError:
        return str(path.resolve())


def find_edge() -> Path:
    for candidate in EDGE_CANDIDATES:
        if candidate.is_file():
            return candidate.resolve()
    for command in ("msedge", "chrome", "chromium"):
        found = shutil.which(command)
        if found:
            return Path(found).resolve()
    raise FileNotFoundError("Edge/Chrome/Chromium PDF engine is unavailable")


def workspace_roots() -> list[Path]:
    roots = [REPO_ROOT]
    roots.extend(REPO_ROOT.parents)
    unique: list[Path] = []
    for root in roots:
        if root not in unique:
            unique.append(root)
    return unique


def find_poppler_tool(name: str) -> Path:
    executable = f"{name}.exe" if os.name == "nt" else name
    for root in workspace_roots():
        candidate = root / POPPLER_RELATIVE / executable
        if candidate.is_file():
            return candidate.resolve()
    found = shutil.which(name)
    if found:
        return Path(found).resolve()
    raise FileNotFoundError(f"required Poppler tool is unavailable: {name}")


def verify_accepted_html(html_root: Path) -> dict[str, Any]:
    result = freeze_html.verify(html_root, freeze_html.DEFAULT_MASTER_RU_ROOT)
    manifest = html_root / freeze_html.MANIFEST_NAME
    raw = manifest.read_bytes()
    if len(raw) != ACCEPTED_HTML_MANIFEST_BYTES or sha256(raw) != ACCEPTED_HTML_MANIFEST_SHA256:
        raise ValueError("accepted HTML manifest identity mismatch")
    return result


def make_config(
    source_html: Path,
    output_root: Path,
    temp_root: Path,
    edge: Path,
    pdftotext: Path,
    pdfinfo: Path,
    pdftoppm: Path,
) -> dict[str, Any]:
    pdf_path = output_root / PDF_NAME
    qa_root = output_root / "QA"
    return {
        "project_key": "kb_creator_innsmouth_accepted_html_pdf",
        "scenario_title_en": "The Innsmouth Terror",
        "scenario_title_ru": "Ужас Иннсмута",
        "workbench_qa_root": str(qa_root.resolve()),
        "scenario_gates": {"accepted_html_verified": True},
        "tooling": {
            "pdftotext": str(pdftotext),
            "pdfinfo": str(pdfinfo),
            "pdftoppm": str(pdftoppm),
        },
        "production_pdf": {
            "source_html": config_path_value(source_html),
            "output_pdf": config_path_value(pdf_path),
            "report": "production_pdf_report.json",
            "required_gates": ["accepted_html_verified"],
            "temp_root": str(temp_root.resolve()),
            "engine_timeout_seconds": 180,
            "temp_output_timeout_seconds": 90,
            "temp_output_stable_seconds": 1.0,
            "engine_command": [
                str(edge),
                "--headless=new",
                "--disable-gpu",
                "--no-sandbox",
                "--no-pdf-header-footer",
                "--run-all-compositor-stages-before-draw",
                "--virtual-time-budget=10000",
                "--user-data-dir={temp_dir}",
                "--print-to-pdf={output_pdf}",
                "{source_html_uri}",
            ],
        },
        "pdf_print_qa": {
            "report": "pdf_print_qa.json",
            "require_header_footer_disabled": True,
            "require_current_html_hash": True,
            "min_text_chars": 60_000,
            "near_empty_page_policy": {
                "enabled": True,
                "min_ink_ratio": 0.008,
                "min_text_chars": 40,
                "max_blank_bottom_ratio": 0.82,
                "fail_on_unexpected": False,
            },
        },
    }


def prepare_print_source(html_root: Path, target: Path) -> dict[str, Any]:
    source = html_root / freeze_html.HTML_NAME
    raw = source.read_bytes()
    if len(raw) != freeze_html.EXPECTED_HTML_BYTES or sha256(raw) != freeze_html.EXPECTED_HTML_SHA256:
        raise ValueError("accepted HTML changed before PDF print-source derivation")
    text = raw.decode("utf-8")
    marker = 'id="innsmouth-pdf-print-r6"'
    if marker in text:
        raise ValueError("PDF print stylesheet already exists in accepted HTML")
    base_href = html_lib.escape(html_root.resolve().as_uri().rstrip("/") + "/", quote=True)
    injection = (
        f'\n<base href="{base_href}">\n'
        '<style id="innsmouth-pdf-print-r6">\n'
        '@media print {\n'
        '  section.title-page {\n'
        '    break-inside: avoid !important; page-break-inside: avoid !important;\n'
        '    break-after: page !important; page-break-after: always !important;\n'
        '  }\n'
        '  figure.art-float-right {\n'
        '    float: right !important; clear: right !important; width: 48% !important;\n'
        '    max-width: none !important; margin: .2rem 0 1rem 1.25rem !important;\n'
        '    text-align: right !important;\n'
        '  }\n'
        '  section.source-toc-section {\n'
        '    break-before: page !important; page-break-before: always !important;\n'
        '    break-after: page !important; page-break-after: always !important;\n'
        '  }\n'
        '  .pdf-hard-page-break {\n'
        '    display: block !important; clear: both !important; column-span: all !important;\n'
        '    width: 100% !important; height: 1px !important; margin: 0 !important; padding: 0 !important;\n'
        '    break-before: page !important; page-break-before: always !important;\n'
        '  }\n'
        '}\n'
        '</style>\n'
    )
    if text.count("</head>") != 1:
        raise ValueError("accepted HTML head boundary mismatch")
    toc_to_body = '</section>\n<h1 id="uzhas-innsmuta-2">'
    if text.count(toc_to_body) != 1:
        raise ValueError("accepted HTML TOC-to-body boundary mismatch")
    hard_break = '<div class="pdf-hard-page-break" aria-hidden="true">&#8203;</div>'
    derived_text = text.replace("</head>", injection + "</head>", 1)
    derived_text = derived_text.replace(
        toc_to_body,
        f'</section>\n{hard_break}\n<h1 id="uzhas-innsmuta-2">',
        1,
    )
    derived = derived_text.encode("utf-8")
    target.write_bytes(derived)
    return {
        "path": config_path_value(target),
        "bytes": len(derived),
        "sha256": sha256(derived),
        "operations": [
            "base href bound to accepted HTML asset root",
            "print-only title-page boundary",
            "print-only right-float restoration below narrow viewport breakpoint",
            "print-only hard page boundary after source TOC",
        ],
    }


def inspect_front_matter_pages(page_texts: list[str]) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    findings: list[dict[str, Any]] = []
    if len(page_texts) < 4:
        return {"checked": False, "reason": "fewer_than_four_pages"}, [
            {"code": "pdf_front_matter_pages_missing", "page_count": len(page_texts)}
        ]

    intro = page_texts[1]
    toc = page_texts[2]
    body = page_texts[3]
    checks = {
        "title_page_has_title": "УЖАС ИННСМУТА" in page_texts[0],
        "intro_page_has_booklet_summary": "В буклете содержатся" in intro,
        "intro_page_excludes_toc": "СОДЕРЖАНИЕ" not in intro,
        "toc_page_has_heading": "СОДЕРЖАНИЕ" in toc,
        "toc_page_has_final_group": "РАЗДАТОЧНЫЕ МАТЕРИАЛЫ" in toc,
        "toc_page_excludes_body": "Мы поплывём к мрачному рифу" not in toc,
        "body_page_starts_body": "Мы поплывём к мрачному рифу" in body,
        "content_warnings_absent": all(
            "ПРЕДУПРЕЖДЕНИЯ О СОДЕРЖАНИИ" not in page for page in page_texts
        ),
        "credits_absent": all(
            "Не предназначено для перепродажи" not in page for page in page_texts
        ),
    }
    failed = [name for name, passed in checks.items() if not passed]
    if failed:
        findings.append({"code": "pdf_front_matter_page_boundaries_failed", "checks": failed})
    return {"checked": True, "pages": {"title": 1, "intro": 2, "toc": 3, "body": 4}, "checks": checks}, findings


def inspect_pdf(pdf_path: Path) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    from pypdf import PdfReader

    findings: list[dict[str, Any]] = []
    reader = PdfReader(pdf_path)
    if reader.is_encrypted:
        findings.append({"code": "pdf_encrypted"})
    page_count = len(reader.pages)
    if not 20 <= page_count <= 80:
        findings.append({"code": "unexpected_page_count", "page_count": page_count})

    total_text = ""
    page_rows: list[dict[str, Any]] = []
    page_sizes: set[tuple[float, float]] = set()
    link_annotations = 0
    internal_links = 0
    image_xobjects = 0
    fonts: set[str] = set()
    empty_pages: list[int] = []
    page_texts: list[str] = []
    for number, page in enumerate(reader.pages, start=1):
        text = page.extract_text() or ""
        page_texts.append(text)
        total_text += text + "\n"
        width = round(float(page.mediabox.width), 2)
        height = round(float(page.mediabox.height), 2)
        page_sizes.add((width, height))
        resources = page.get("/Resources") or {}
        xobjects = resources.get("/XObject") or {}
        page_images = 0
        for value in xobjects.values():
            obj = value.get_object()
            if obj.get("/Subtype") == "/Image":
                page_images += 1
        image_xobjects += page_images
        page_fonts = resources.get("/Font") or {}
        for value in page_fonts.values():
            font = value.get_object()
            base = font.get("/BaseFont")
            if base:
                fonts.add(str(base))
        page_links = 0
        for annotation_ref in page.get("/Annots") or []:
            annotation = annotation_ref.get_object()
            if annotation.get("/Subtype") != "/Link":
                continue
            page_links += 1
            link_annotations += 1
            if annotation.get("/Dest") is not None or (annotation.get("/A") or {}).get("/S") == "/GoTo":
                internal_links += 1
        if not text.strip() and page_images == 0:
            empty_pages.append(number)
        page_rows.append(
            {
                "page": number,
                "text_chars": len(text),
                "images": page_images,
                "links": page_links,
                "width": width,
                "height": height,
            }
        )

    if empty_pages:
        findings.append({"code": "empty_pdf_pages", "pages": empty_pages})
    if len(page_sizes) != 1:
        findings.append({"code": "mixed_page_sizes", "sizes": sorted(page_sizes)})
    if len(total_text) < 60_000:
        findings.append({"code": "pdf_text_too_sparse", "characters": len(total_text)})
    missing_sentinels = [value for value in SENTINELS if value.casefold() not in total_text.casefold()]
    if missing_sentinels:
        findings.append({"code": "pdf_sentinels_missing", "values": missing_sentinels})
    if link_annotations < 50:
        findings.append({"code": "pdf_link_annotations_too_few", "count": link_annotations})
    if image_xobjects < 20:
        findings.append({"code": "pdf_image_xobjects_too_few", "count": image_xobjects})
    if not fonts:
        findings.append({"code": "pdf_fonts_missing"})
    front_matter, front_matter_findings = inspect_front_matter_pages(page_texts)
    findings.extend(front_matter_findings)

    return {
        "pages": page_count,
        "page_sizes": [list(value) for value in sorted(page_sizes)],
        "text_characters": len(total_text),
        "link_annotations": link_annotations,
        "internal_links": internal_links,
        "image_xobjects": image_xobjects,
        "fonts": sorted(fonts),
        "empty_pages": empty_pages,
        "front_matter": front_matter,
        "page_metrics": page_rows,
    }, findings


def render_pages(pdf_path: Path, output_root: Path, pdftoppm: Path, page_count: int) -> dict[str, Any]:
    render_root = output_root / "QA" / "rendered_pages"
    render_root.mkdir(parents=True, exist_ok=False)
    prefix = render_root / "page"
    completed = subprocess.run(
        [str(pdftoppm), "-png", "-r", "120", str(pdf_path), str(prefix)],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        timeout=300,
        check=False,
    )
    if completed.returncode != 0:
        raise RuntimeError(f"pdftoppm failed: {completed.stderr.strip()}")
    pngs = sorted(render_root.glob("page-*.png"))
    if len(pngs) != page_count:
        raise ValueError(f"rendered page count mismatch: expected {page_count}, got {len(pngs)}")
    records: list[dict[str, Any]] = []
    for index, path in enumerate(pngs, start=1):
        raw = path.read_bytes()
        with Image.open(path) as image:
            width, height = image.size
        records.append(
            {
                "page": index,
                "path": config_path_value(path),
                "bytes": len(raw),
                "sha256": sha256(raw),
                "width": width,
                "height": height,
            }
        )
    return {"count": len(records), "dpi": 120, "files": records}


def build(html_root: Path, output_root: Path, temp_root: Path) -> dict[str, Any]:
    if output_root.exists():
        raise FileExistsError(f"PDF candidate target already exists: {output_root}")
    accepted_html = verify_accepted_html(html_root)
    edge = find_edge()
    pdftotext = find_poppler_tool("pdftotext")
    pdfinfo = find_poppler_tool("pdfinfo")
    pdftoppm = find_poppler_tool("pdftoppm")

    output_root.mkdir(parents=True)
    qa_root = output_root / "QA"
    qa_root.mkdir()
    config_path = output_root / CONFIG_NAME
    print_source_path = qa_root / PRINT_SOURCE_NAME
    print_source = prepare_print_source(html_root, print_source_path)
    config = make_config(print_source_path, output_root, temp_root, edge, pdftotext, pdfinfo, pdftoppm)
    config_path.write_bytes(canonical_json(config))

    print_result = translator.build_production_pdf(config_path)
    if print_result.get("status") != "pass" or print_result.get("action") != "built":
        raise RuntimeError(f"production PDF build failed: {print_result.get('findings')}")
    pdf_path = output_root / PDF_NAME
    structural, findings = inspect_pdf(pdf_path)
    print_qa = translator.run_pdf_print_qa(config_path)
    if print_qa.get("status") != "pass":
        findings.extend(print_qa.get("findings") or [])
    renders = render_pages(pdf_path, output_root, pdftoppm, structural["pages"])
    pdf_raw = pdf_path.read_bytes()
    report = {
        "schema": "kb_creator.innsmouth.accepted_html_pdf_candidate.v1",
        "status": "pass" if not findings else "blocked",
        "source_accepted_html": {
            "root": config_path_value(html_root),
            "html": accepted_html["html"],
            "manifest": accepted_html["manifest"],
        },
        "print_source": print_source,
        "pdf": {
            "path": config_path_value(pdf_path),
            "bytes": len(pdf_raw),
            "sha256": sha256(pdf_raw),
        },
        "tools": {
            "browser": str(edge),
            "pdftotext": str(pdftotext),
            "pdfinfo": str(pdfinfo),
            "pdftoppm": str(pdftoppm),
        },
        "structural": structural,
        "production_pdf_report": config_path_value(qa_root / "production_pdf_report.json"),
        "pdf_print_qa_report": config_path_value(qa_root / "pdf_print_qa.json"),
        "renders": renders,
        "findings": findings,
    }
    (output_root / QA_NAME).write_bytes(canonical_json(report))
    if findings:
        raise ValueError(f"PDF candidate QA blocked: {findings}")
    return report


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--html-root", type=Path, default=DEFAULT_HTML_ROOT)
    parser.add_argument("--output-root", type=Path, default=DEFAULT_OUTPUT_ROOT)
    parser.add_argument("--temp-root", type=Path, default=DEFAULT_TEMP_ROOT)
    args = parser.parse_args()
    report = build(args.html_root.resolve(), args.output_root.resolve(), args.temp_root.resolve())
    print("INNSMOUTH_ACCEPTED_HTML_PDF_CANDIDATE_OK")
    print(json.dumps(report, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
