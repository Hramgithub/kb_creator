from __future__ import annotations

import copy
from pathlib import Path
import zipfile

import pytest

pytest.importorskip("docx")

from docx import Document
from docx.enum.section import WD_ORIENT

from kb_creator.scripts.production_docx import build_docx
from kb_creator.pipeline.identity import file_identity
from kb_creator.pipeline.publication import PublicationControlError, PublicationStageAdapter, publication_resume, record_artifact_acceptance
from kb_creator.pipeline.publication_adapters import PublicationAdapterRuntime, fixed_publication_adapters
from kb_creator.tests.test_publication_control_plane import _accept, _advance_to_docx, _fixture, _write_json
from pypdf import PdfWriter


def _config() -> dict:
    return {
        "schema": "kb_creator.production_docx_config.v1",
        "page": {"width_mm": 297, "height_mm": 210, "orientation": "landscape"},
        "margins": {"top_mm": 11, "bottom_mm": 12, "left_mm": 13, "right_mm": 14},
        "fonts": {"body": "Arial", "title": "Arial", "headings": "Arial", "footer": "Arial"},
        "sizes": {"body_pt": 9, "title_pt": 20, "footer_pt": 8},
        "spacing": {"body_after_pt": 3, "body_line": 1.1},
        "headings": {
            str(level): {
                "size_pt": 18 - level,
                "bold": level <= 3,
                "space_before_pt": 8,
                "space_after_pt": 3,
            }
            for level in range(1, 7)
        },
        "footer": {"page_numbers": True},
        "metadata": {
            "title": "Synthetic Scenario",
            "subject": "Call of Cthulhu",
            "author": "NRI test",
            "keywords": "synthetic",
            "comments": "explicit closed config",
        },
    }


def _html(path: Path) -> None:
    path.write_text(
        """<html><body><main>
        <nav id="toc"><ol>
        <li class="toc-level-1"><a href="#one">One</a></li>
        <li class="toc-level-2"><a href="#one-a">One A</a></li>
        <li class="toc-level-1"><a href="#two">Two</a></li>
        <li class="toc-level-2"><a href="#two-a">Two A</a></li>
        </ol></nav>
        <h2 id="one">One</h2><h3 id="one-a">One A</h3><p>Body.</p>
        <h2 id="two">Two</h2><h3 id="two-a">Two A</h3>
        </main></body></html>""",
        encoding="utf-8",
    )


def test_explicit_closed_config_controls_docx_layout_and_metadata(tmp_path: Path) -> None:
    source = tmp_path / "source.html"
    target = tmp_path / "candidate.docx"
    _html(source)

    result = build_docx(source, target, config=_config())

    assert result["status"] == "pass"
    assert result["config_sha256"]
    document = Document(target)
    section = document.sections[0]
    assert section.orientation == WD_ORIENT.LANDSCAPE
    assert round(section.left_margin.mm) == 13
    assert document.styles["Normal"].font.name == "Arial"
    assert document.styles["Heading 1"].font.name == "Arial"
    assert document.core_properties.title == "Synthetic Scenario"
    assert document.core_properties.author == "NRI test"
    assert "PAGE" in section.footer._element.xml


def test_explicit_config_can_disable_page_number_footer(tmp_path: Path) -> None:
    source = tmp_path / "source.html"
    target = tmp_path / "candidate.docx"
    _html(source)
    config = copy.deepcopy(_config())
    config["footer"]["page_numbers"] = False

    result = build_docx(source, target, config=config)

    assert result["status"] == "pass"
    with zipfile.ZipFile(target) as archive:
        names = set(archive.namelist())
        assert not any(name.startswith("word/footer") for name in names)
        document_xml = archive.read("word/document.xml").decode("utf-8")
    assert "footerReference" not in document_xml
    assert " PAGE " not in document_xml


def test_explicit_config_is_closed_and_rejected_before_output(tmp_path: Path) -> None:
    source = tmp_path / "source.html"
    target = tmp_path / "candidate.docx"
    _html(source)
    invalid = copy.deepcopy(_config())
    invalid["browser_pdf"] = True

    with pytest.raises(ValueError, match="unknown or missing"):
        build_docx(source, target, config=invalid)

    assert not target.exists()


def _replace_contract_config(fixture: dict, role: str, value: dict) -> None:
    path = fixture["config_root"] / f"{role}.json"
    _write_json(path, value)
    record = {"path": path.relative_to(fixture["config_root"]).as_posix(), **file_identity(path)}
    contract = __import__("json").loads(fixture["contract"].read_text(encoding="utf-8"))
    for row in contract["configs"]:
        if row["role"] == role:
            row["file"] = record
    contract[role]["config"] = record
    _write_json(fixture["contract"], contract)


def _synthetic_pdf(path: Path) -> None:
    writer = PdfWriter(); writer.add_blank_page(width=300, height=400)
    with path.open("wb") as stream: writer.write(stream)


def test_retired_stage50_and_stage60_route_fails_before_adapter_dispatch(tmp_path: Path) -> None:
    run_root = tmp_path / "legacy-run"
    invoked = []

    def adapter(*_args, **_kwargs):
        invoked.append(True)
        raise AssertionError("retired adapter must not run")

    registry = {"docx_candidate": PublicationStageAdapter("legacy", adapter)}
    with pytest.raises(PublicationControlError, match="DOCX-only"):
        publication_resume(run_root, {"html_acceptance": tmp_path / "old-html.acceptance.json"}, registry)
    with pytest.raises(PublicationControlError, match="DOCX-only"):
        record_artifact_acceptance(run_root, "docx", [], tmp_path / "old-docx.acceptance.json", "old route")
    assert not run_root.exists()
    assert not invoked
