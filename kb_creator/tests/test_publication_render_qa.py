from __future__ import annotations

import json
from pathlib import Path

import pytest

pytest.importorskip("PIL")
pytest.importorskip("pypdf")

from pypdf import PdfWriter

from kb_creator.scripts.publication_render_qa import RenderQaError, render_docx_transient, render_pdf_pages


REPO_ROOT = Path(__file__).resolve().parents[2]
PDFTOPPM = REPO_ROOT / ".tools" / "poppler" / "poppler-26.02.0" / "Library" / "bin" / "pdftoppm.exe"


def _pdf(path: Path, pages: int = 2) -> None:
    writer = PdfWriter()
    for _ in range(pages):
        writer.add_blank_page(width=300, height=400)
    with path.open("wb") as stream:
        writer.write(stream)


@pytest.mark.skipif(not PDFTOPPM.is_file(), reason="repository Poppler is not provisioned")
def test_final_render_uses_repo_poppler_and_emits_every_page(tmp_path: Path) -> None:
    source = tmp_path / "candidate.pdf"
    output = tmp_path / "final-render"
    _pdf(source)

    result = render_pdf_pages(source, output, PDFTOPPM, dpi=72)

    assert result["status"] == "pass"
    assert result["page_count"] == 2
    assert sorted(path.name for path in output.glob("*.png")) == ["page-001.png", "page-002.png"]
    inventory = json.loads((output / "render_inventory.json").read_text(encoding="utf-8"))
    assert inventory["page_count"] == 2
    assert Path(inventory["renderer"]["path"]).is_relative_to(REPO_ROOT / ".tools" / "poppler")
    assert [row["page"] for row in inventory["pages"]] == [1, 2]


@pytest.mark.skipif(not PDFTOPPM.is_file(), reason="repository Poppler is not provisioned")
def test_stage50_transient_bridge_is_deleted_and_never_disclosed(tmp_path: Path) -> None:
    source = tmp_path / "candidate.docx"
    source.write_bytes(b"synthetic docx identity")
    output = tmp_path / "docx-render"
    private = tmp_path / "private"

    def export(_source: Path, bridge: Path, authority: Path) -> None:
        assert authority == private
        _pdf(bridge, pages=1)

    result = render_docx_transient(
        source,
        output,
        private,
        REPO_ROOT / "kb_creator" / "scripts" / "export_docx_to_pdf.ps1",
        Path("powershell.exe"),
        PDFTOPPM,
        dpi=72,
        export=export,
    )

    assert result["transient_bridge_cleanup"] == "pass"
    assert not private.exists()
    assert not list(tmp_path.rglob("*.pdf"))
    assert list(output.glob("*.png"))
    evidence = "\n".join(path.read_text(encoding="utf-8") for path in output.glob("*.json"))
    assert "bridge.pdf" not in evidence
    assert ".pdf" not in evidence.lower()


@pytest.mark.skipif(not PDFTOPPM.is_file(), reason="repository Poppler is not provisioned")
def test_transient_word_failure_still_removes_private_bridge(tmp_path: Path) -> None:
    source = tmp_path / "candidate.docx"; source.write_bytes(b"synthetic docx identity")
    private = tmp_path / "private"

    def fail_after_bridge(_source: Path, bridge: Path, _authority: Path) -> None:
        _pdf(bridge, pages=1)
        raise RuntimeError("injected Word failure")

    with pytest.raises(RuntimeError, match="injected Word failure"):
        render_docx_transient(
            source, tmp_path / "render", private,
            REPO_ROOT / "kb_creator" / "scripts" / "export_docx_to_pdf.ps1",
            Path("powershell.exe"), PDFTOPPM, export=fail_after_bridge,
        )
    assert not private.exists()
    assert not list(tmp_path.rglob("*.pdf"))
    assert not (tmp_path / "render").exists()
