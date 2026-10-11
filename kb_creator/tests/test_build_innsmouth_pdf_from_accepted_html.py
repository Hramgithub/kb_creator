from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "kb_creator" / "scripts" / "build_innsmouth_pdf_from_accepted_html.py"
SPEC = importlib.util.spec_from_file_location("build_innsmouth_pdf_from_accepted_html", SCRIPT)
assert SPEC and SPEC.loader
pdf_builder = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(pdf_builder)


def test_pdf_source_is_the_exact_accepted_html_package(tmp_path: Path) -> None:
    accepted = tmp_path / "accepted_html"
    pdf_builder.freeze_html.promote(
        pdf_builder.freeze_html.DEFAULT_CANDIDATE_ROOT,
        pdf_builder.freeze_html.DEFAULT_MASTER_RU_ROOT,
        accepted,
        "2026-08-30",
    )
    verified = pdf_builder.verify_accepted_html(accepted)
    assert verified["html"]["sha256"] == (
        "040C7AF42A76241B3BC280350C0151096CF81E5F9A9194E6F5003B0388E4EF39"
    )
    assert verified["manifest"] == {
        "name": "HTML.acceptance.json",
        "bytes": 6_966,
        "sha256": "B0ADDD901CCD0DED10D84D331B3F168987070558641D374F13ABC30852E6D7E6",
    }


def test_pdf_config_has_one_direct_accepted_html_route(tmp_path: Path) -> None:
    output_root = tmp_path / "pdf_candidate"
    config = pdf_builder.make_config(
        pdf_builder.DEFAULT_HTML_ROOT / pdf_builder.freeze_html.HTML_NAME,
        output_root,
        tmp_path / "temp",
        Path("edge.exe"),
        Path("pdftotext.exe"),
        Path("pdfinfo.exe"),
        Path("pdftoppm.exe"),
    )
    production = config["production_pdf"]
    assert production["required_gates"] == ["accepted_html_verified"]
    assert production["source_html"].endswith(
        "kb_creator/inputs/innsmouth/html/accepted_20260830_r2/The_Innsmouth_Terror_RU.html"
    )
    assert production["output_pdf"].replace("\\", "/").endswith(
        "pdf_candidate/The_Innsmouth_Terror_RU.pdf"
    )
    assert "variants" not in production
    serialized = pdf_builder.canonical_json(config).decode("utf-8")
    assert "accepted_20260829" not in serialized
    assert "KeeperBook" not in serialized
    assert "v6" not in serialized


def test_print_source_changes_only_the_pdf_presentation_layer(tmp_path: Path) -> None:
    target = tmp_path / pdf_builder.PRINT_SOURCE_NAME
    result = pdf_builder.prepare_print_source(
        pdf_builder.freeze_html.DEFAULT_CANDIDATE_ROOT,
        target,
    )
    text = target.read_text(encoding="utf-8")
    assert result["bytes"] > pdf_builder.freeze_html.EXPECTED_HTML_BYTES
    assert text.count('id="innsmouth-pdf-print-r6"') == 1
    assert "figure.art-float-right" in text
    assert "print-only title-page boundary" in result["operations"]
    assert "print-only hard page boundary after source TOC" in result["operations"]
    assert "section.source-toc-section" in text
    assert text.count('class="pdf-hard-page-break"') == 1
    assert "page-break-before: always !important" in text
    assert pdf_builder.freeze_html.LETTER_SEAL_ASSET not in text


def test_front_matter_page_gate_requires_physical_page_isolation() -> None:
    pages = [
        "УЖАС ИННСМУТА",
        "В буклете содержатся",
        "СОДЕРЖАНИЕ ВВЕДЕНИЕ РАЗДАТОЧНЫЕ МАТЕРИАЛЫ",
        "Мы поплывём к мрачному рифу УЖАС ИННСМУТА ВВЕДЕНИЕ",
    ]
    summary, findings = pdf_builder.inspect_front_matter_pages(pages)
    assert findings == []
    assert all(summary["checks"].values())

    pages[1] += " СОДЕРЖАНИЕ"
    pages[2] += " Мы поплывём к мрачному рифу"
    _, findings = pdf_builder.inspect_front_matter_pages(pages)
    assert findings == [
        {
            "code": "pdf_front_matter_page_boundaries_failed",
            "checks": ["intro_page_excludes_toc", "toc_page_excludes_body"],
        }
    ]


def test_pdf_builder_refuses_existing_candidate_root(tmp_path: Path) -> None:
    output_root = tmp_path / "pdf_candidate"
    output_root.mkdir()
    with pytest.raises(FileExistsError, match="already exists"):
        pdf_builder.build(
            pdf_builder.DEFAULT_HTML_ROOT,
            output_root,
            tmp_path / "temp",
        )


def test_required_local_pdf_tools_are_discoverable() -> None:
    assert pdf_builder.find_edge().is_file()
    assert pdf_builder.find_poppler_tool("pdftotext").is_file()
    assert pdf_builder.find_poppler_tool("pdfinfo").is_file()
    assert pdf_builder.find_poppler_tool("pdftoppm").is_file()
