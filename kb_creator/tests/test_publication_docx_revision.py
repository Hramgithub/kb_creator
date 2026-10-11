from __future__ import annotations

import json
import shutil
import zipfile
from pathlib import Path

import pytest

from kb_creator.scripts.revise_publication_docx_package import (
    DocxRevisionError,
    _manifest,
    build_revision_package,
    materialize_release_layout,
    record_visual_acceptance,
)
from kb_creator.scripts.verify_docx_revision_package import (
    canonical,
    package_inventory,
    verify_revision_package,
)


def _docx(path: Path) -> None:
    with zipfile.ZipFile(path, "w") as archive:
        archive.writestr("word/document.xml", "<w:document xmlns:w='x'><w:body/></w:document>")


def _base_package(path: Path) -> None:
    path.mkdir()
    (path / "Old.docx").write_bytes(b"old-docx")
    (path / "Old.pdf").write_bytes(b"old-pdf")
    (path / "MASTER_EN.md").write_text("English", encoding="utf-8")
    (path / "MASTER_RU.md").write_text("Russian", encoding="utf-8")
    (path / "Old.html").write_text('<html><body><img src="assets/map.png"></body></html>', encoding="utf-8")
    (path / "assets").mkdir()
    (path / "assets" / "map.png").write_bytes(b"map")
    (path / "evidence" / "stages").mkdir(parents=True)
    (path / "evidence" / "stages" / "base.json").write_text('{"state":"pass"}', encoding="utf-8")
    (path / "PRODUCTION_MANIFEST.json").write_text(
        json.dumps(
            {
                "scenario_id": "sample",
                "roles": [
                    {"role": "master_en", "path": "MASTER_EN.md"},
                    {"role": "master_ru", "path": "MASTER_RU.md"},
                    {"role": "html", "path": "Old.html"},
                    {"role": "docx", "path": "Old.docx"},
                    {"role": "pdf", "path": "Old.pdf"},
                ],
            }
        ),
        encoding="utf-8",
    )


def _exporter(docx: Path, pdf: Path, _root: Path, _lo: Path, *, evidence_output: Path, **_kwargs):
    pdf.write_bytes(b"fresh-pdf")
    value = {
        "status": "pass",
        "input": {"path": str(docx), "bytes": docx.stat().st_size, "sha256": __import__("hashlib").sha256(docx.read_bytes()).hexdigest().upper()},
        "output": {"path": str(pdf), "bytes": pdf.stat().st_size, "sha256": __import__("hashlib").sha256(pdf.read_bytes()).hexdigest().upper()},
        "export": {"document_input_role": "accepted_docx"},
    }
    evidence_output.write_text(json.dumps(value), encoding="utf-8")
    return value


def _renderer(pdf: Path, output: Path, _pdftoppm: Path, **_kwargs):
    output.mkdir()
    digest = __import__("hashlib").sha256(pdf.read_bytes()).hexdigest().upper()
    render = {
        "source_kind": "final_pdf",
        "source": {"path": pdf.name, "bytes": pdf.stat().st_size, "sha256": digest},
        "page_count": 2,
        "signals": {"near_blank_pages": [], "orphan_signal_pages": []},
    }
    (output / "render_inventory.json").write_text(json.dumps(render), encoding="utf-8")
    return {"status": "pass", "page_count": 2}


def _historical_revision_fixture(tmp_path: Path) -> tuple[Path, object]:
    """Construct a sealed old archive for read-only verifier tests, without a writer API."""
    base = tmp_path / "base"
    _base_package(base)
    reviewed = tmp_path / "reviewed.docx"
    _docx(reviewed)
    output = tmp_path / "revision"
    verifier = lambda _path: {"state": "candidate_for_release_review"}
    output.mkdir()
    shutil.copytree(base, output / "base_package")
    shutil.copy2(reviewed, output / "Old.docx")
    shutil.copy2(base / "Old.html", output / "Old.html")
    shutil.copy2(base / "MASTER_EN.md", output / "MASTER_EN.md")
    shutil.copy2(base / "MASTER_RU.md", output / "MASTER_RU.md")
    shutil.copytree(base / "assets", output / "assets")
    shutil.copytree(base / "evidence", output / "evidence")
    _exporter(output / "Old.docx", output / "Old.pdf", output, tmp_path / "lo", evidence_output=output / "evidence" / "docx_pdf_export.json")
    _renderer(output / "Old.pdf", output / "evidence" / "final_render", tmp_path / "pdftoppm")
    manifest = _manifest(output, output / "base_package" / "PRODUCTION_MANIFEST.json", "sample", output / "Old.docx", output / "Old.pdf", "historical fixture")
    (output / "REVISION_MANIFEST.json").write_bytes(canonical(manifest) + b"\n")
    assert verify_revision_package(output, base_verifier=verifier)["state"] == "awaiting_visual_review"
    return output, verifier


def test_reviewed_docx_revision_writer_is_retired_before_staging(tmp_path: Path) -> None:
    base = tmp_path / "base"
    _base_package(base)
    reviewed = tmp_path / "reviewed.docx"
    _docx(reviewed)
    output = tmp_path / "revision"
    with pytest.raises(DocxRevisionError, match="DOCX-only"):
        build_revision_package(base, reviewed, output, tmp_path / "lo", tmp_path / "pdftoppm", "old route")
    assert not output.exists()


def test_historical_revision_fixture_remains_read_only_verifiable(tmp_path: Path) -> None:
    output, verifier = _historical_revision_fixture(tmp_path)
    result = verify_revision_package(output, base_verifier=verifier)
    assert result["state"] == "awaiting_visual_review"
    assert (output / "base_package" / "Old.docx").read_bytes() == b"old-docx"
    assert (output / "Old.docx").is_file()
    assert (output / "Old.html").is_file()
    assert (output / "assets" / "map.png").read_bytes() == b"map"
    assert (output / "evidence" / "stages" / "base.json").read_text(encoding="utf-8") == '{"state":"pass"}'


def test_revision_verifier_rejects_post_seal_pdf_change(tmp_path: Path) -> None:
    output, verifier = _historical_revision_fixture(tmp_path)
    (output / "Old.pdf").write_bytes(b"tampered")
    try:
        verify_revision_package(output, base_verifier=verifier)
    except ValueError as error:
        assert "inventory mismatch" in str(error)
    else:
        raise AssertionError("tampered revision package unexpectedly verified")


def test_revision_writer_rejects_before_conflicting_base_evidence_is_read(tmp_path: Path) -> None:
    base = tmp_path / "base"
    _base_package(base)
    (base / "evidence" / "docx_pdf_export.json").write_text("old export", encoding="utf-8")
    reviewed = tmp_path / "reviewed.docx"
    _docx(reviewed)
    output = tmp_path / "revision"

    with pytest.raises(DocxRevisionError, match="DOCX-only"):
        build_revision_package(
            base,
            reviewed,
            output,
            tmp_path / "soffice.exe",
            tmp_path / "pdftoppm.exe",
            "user reviewed DOCX",
            base_verifier=lambda _path: {"state": "candidate_for_release_review"},
            exporter=_exporter,
            renderer=_renderer,
        )
    assert not output.exists()


def test_materialize_release_is_retired_and_archive_html_reference_stays_checked(tmp_path: Path) -> None:
    source, verifier = _historical_revision_fixture(tmp_path)
    target = tmp_path / "release"
    with pytest.raises(DocxRevisionError, match="DOCX-only"):
        materialize_release_layout(source, target, base_verifier=verifier)
    assert not target.exists()
    shutil.copytree(source, target)
    assert (target / "Old.html").is_file()
    assert (target / "assets" / "map.png").read_bytes() == b"map"

    (target / "assets" / "map.png").unlink()
    manifest_path = target / "REVISION_MANIFEST.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["inventory"] = package_inventory(target)
    manifest.pop("revision_sha256")
    manifest["revision_sha256"] = __import__("hashlib").sha256(canonical(manifest)).hexdigest().upper()
    manifest_path.write_bytes(canonical(manifest) + b"\n")
    with pytest.raises(ValueError, match="HTML local reference"):
        verify_revision_package(target, base_verifier=verifier)
