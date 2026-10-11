from __future__ import annotations

import json
import subprocess
from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT = REPO_ROOT / "kb_creator" / "scripts" / "export_docx_to_pdf.ps1"
POWERSHELL = Path("C:/Windows/System32/WindowsPowerShell/v1.0/powershell.exe")
WORD = Path("C:/Program Files/Microsoft Office/root/Office16/WINWORD.EXE")


def test_exporter_is_docx_only_and_has_no_html_or_browser_route(tmp_path: Path) -> None:
    text = SCRIPT.read_text(encoding="utf-8")
    lowered = text.lower()
    assert "exportasfixedformat" in lowered
    assert "all_pages = $true" in lowered
    assert "export_format = 17" in lowered
    assert "finally" in lowered
    assert "[switch]$transientbridge" in lowered
    assert "html" not in lowered
    assert "browser" not in lowered

    source = tmp_path / "source.html"
    source.write_text("not a docx", encoding="utf-8")
    process = subprocess.run(
        [str(POWERSHELL), "-NoProfile", "-File", str(SCRIPT), "-Docx", str(source), "-Pdf", str(tmp_path / "out.pdf"), "-StageRoot", str(tmp_path), "-EvidenceOutput", str(tmp_path / "evidence.json")],
        capture_output=True,
        text=True,
        check=False,
    )
    assert process.returncode != 0
    assert not (tmp_path / "out.pdf").exists()
    assert not (tmp_path / "evidence.json").exists()


def test_exporter_rejects_preexisting_pdf_before_word_is_started(tmp_path: Path) -> None:
    source = tmp_path / "source.docx"
    source.write_bytes(b"synthetic")
    target = tmp_path / "out.pdf"
    target.write_bytes(b"preexisting")
    evidence = tmp_path / "evidence.json"

    process = subprocess.run(
        [str(POWERSHELL), "-NoProfile", "-File", str(SCRIPT), "-Docx", str(source), "-Pdf", str(target), "-StageRoot", str(tmp_path), "-EvidenceOutput", str(evidence)],
        capture_output=True,
        text=True,
        check=False,
    )

    assert process.returncode != 0
    assert target.read_bytes() == b"preexisting"
    assert not evidence.exists()


@pytest.mark.skipif(not WORD.is_file(), reason="Microsoft Word COM host is unavailable")
def test_word_host_smoke_exports_synthetic_docx_and_records_identity(tmp_path: Path) -> None:
    docx = pytest.importorskip("docx")
    pypdf = pytest.importorskip("pypdf")
    source = tmp_path / "source.docx"
    target = tmp_path / "out.pdf"
    evidence = tmp_path / "evidence.json"
    document = docx.Document(); document.add_heading("Synthetic", level=1); document.add_paragraph("Word COM smoke test."); document.save(source)

    process = subprocess.run(
        [str(POWERSHELL), "-NoProfile", "-File", str(SCRIPT), "-Docx", str(source), "-Pdf", str(target), "-StageRoot", str(tmp_path), "-EvidenceOutput", str(evidence), "-TimeoutSeconds", "60"],
        capture_output=True,
        text=True,
        check=False,
        timeout=120,
    )

    if process.returncode == 2 and ("80070520" in process.stderr or "logon session" in process.stderr.lower()):
        pytest.skip("Word is installed but COM activation is unavailable in this logon session (80070520)")
    assert process.returncode == 0, process.stderr
    assert len(pypdf.PdfReader(str(target)).pages) == 1
    record = json.loads(evidence.read_text(encoding="utf-8"))
    assert Path(record["word"]["path"]).resolve() == WORD.resolve()
    assert record["word"]["version"]
    assert record["export"]["all_pages"] is True
    assert record["export"]["fresh_export"] is True
    assert record["cleanup"]["status"] == "pass"
