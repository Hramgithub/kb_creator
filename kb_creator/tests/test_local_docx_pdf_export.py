from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

from kb_creator.scripts import export_docx_to_pdf_local as exporter


def test_local_libreoffice_export_is_exact_evidenced_and_cleans_workspace(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    stage = tmp_path.joinpath("run", *(f"long-publication-segment-{index:02d}" for index in range(7)))
    stage.mkdir(parents=True)
    docx = stage / "accepted.docx"; docx.write_bytes(b"synthetic docx")
    pdf = stage / "output" / "candidate.pdf"; pdf.parent.mkdir()
    evidence = stage / "evidence" / "export.json"; evidence.parent.mkdir()
    tools = tmp_path / ".tools"; tools.mkdir()
    program = tools / "26.8.0" / "program"; program.mkdir(parents=True)
    soffice = program / "soffice.exe"; soffice.write_bytes(b"synthetic executable")
    (program / "version.ini").write_text("[Version]\nbuildid=synthetic-build\n", encoding="utf-8")
    monkeypatch.setattr(exporter, "TOOLS_ROOT", tools)
    runtime = tools / "runtime" / "kb_creator" / "docx_pdf"
    monkeypatch.setattr(exporter, "RUNTIME_ROOT", runtime)
    observed_outdirs = []

    def fake_run(argv, **_kwargs):
        outdir = Path(argv[argv.index("--outdir") + 1])
        observed_outdirs.append(outdir)
        source = Path(argv[-1])
        (outdir / f"{source.stem}.pdf").write_bytes(b"%PDF-synthetic")
        return subprocess.CompletedProcess(argv, 0, "convert success", "")

    monkeypatch.setattr(exporter.subprocess, "run", fake_run)
    result = exporter.export_docx(docx, pdf, stage, soffice, evidence_output=evidence)
    second_docx = stage / "accepted-second.docx"; second_docx.write_bytes(b"second synthetic docx")
    second_pdf = stage / "output" / "candidate-second.pdf"
    second_evidence = stage / "evidence" / "export-second.json"
    exporter.export_docx(second_docx, second_pdf, stage, soffice, evidence_output=second_evidence)

    assert result["status"] == "pass"
    assert result["engine"]["name"] == "libreoffice"
    assert result["export"]["document_input_role"] == "accepted_docx"
    assert pdf.read_bytes() == b"%PDF-synthetic"
    assert evidence.is_file()
    assert len(observed_outdirs) == 2 and all(path.is_relative_to(runtime) for path in observed_outdirs)
    assert len(set(observed_outdirs)) == 2
    assert len(str(observed_outdirs[0])) < len(str(pdf.parent))
    assert runtime.is_dir() and not list(runtime.iterdir())
    assert not list(pdf.parent.glob(".*.lo-export.*"))


def test_local_libreoffice_export_rejects_tool_outside_repo_tools(tmp_path: Path) -> None:
    stage = tmp_path / "run"; stage.mkdir()
    docx = stage / "candidate.docx"; docx.write_bytes(b"docx")
    pdf = stage / "candidate.pdf"
    outside = tmp_path / "soffice.exe"; outside.write_bytes(b"exe")
    with pytest.raises(exporter.LocalExportError, match="below repository .tools"):
        exporter.export_docx(docx, pdf, stage, outside, transient=True)


def test_runtime_root_rejects_reparse_ancestor(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    tools = tmp_path / ".tools"; tools.mkdir()
    runtime_parent = tools / "runtime"; runtime_parent.mkdir()
    runtime = runtime_parent / "kb_creator" / "docx_pdf"
    monkeypatch.setattr(exporter, "TOOLS_ROOT", tools)
    monkeypatch.setattr(exporter, "RUNTIME_ROOT", runtime)
    original = exporter._is_reparse
    monkeypatch.setattr(exporter, "_is_reparse", lambda path: True if path == runtime_parent else original(path))
    with pytest.raises(exporter.LocalExportError, match="reparse content"):
        exporter._runtime_root()
