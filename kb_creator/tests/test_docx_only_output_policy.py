"""Public legacy writers must stop before producing HTML or PDF artifacts."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

from kb_creator.__main__ import main as kb_main
from kb_creator.pipeline.publication import (
    PublicationControlError,
    publication_preflight,
    publication_resume,
    publication_run,
    record_artifact_acceptance,
)
from kb_creator.pipeline.reviewed_reader_revision import RevisionError, revise_reader
from kb_creator.pipeline.publication_adapters import (
    PublicationAdapterError,
    PublicationAdapterRuntime,
    assemble_production_package,
    build_html_candidate,
    fixed_publication_adapters,
)
from kb_creator.scripts.revise_publication_docx_package import (
    DocxRevisionError,
    build_revision_package,
    materialize_release_layout,
    record_visual_acceptance,
)
from kb_creator.scripts.revise_reviewed_reader import main as old_reader_main


@pytest.mark.parametrize(
    "invoke,error_type",
    [
        (lambda root: publication_preflight(root / "contract", root / "inventory", root / "acceptance", root, root / "run"), PublicationControlError),
        (lambda root: publication_run(root / "contract", root / "inventory", root / "acceptance", root, root / "run", "old", {}), PublicationControlError),
        (lambda root: publication_resume(root / "run", {}, {}), PublicationControlError),
        (lambda root: record_artifact_acceptance(root / "run", "pdf", [], root / "acceptance", "old"), PublicationControlError),
        (lambda root: build_revision_package(root / "base", root / "reviewed.docx", root / "revision", root / "lo", root / "poppler", "old"), DocxRevisionError),
        (lambda root: record_visual_acceptance(root / "revision", "old"), DocxRevisionError),
        (lambda root: materialize_release_layout(root / "revision", root / "release"), DocxRevisionError),
        (lambda root: revise_reader(root / "manifest", root / "reviewed.docx", root / "old.html", root / "assets", root / "source.pdf", root / "successor"), RevisionError),
    ],
)
def test_legacy_public_writer_fails_before_any_output(tmp_path: Path, invoke, error_type) -> None:
    before = tuple(tmp_path.iterdir())
    with pytest.raises(error_type, match="DOCX-only"):
        invoke(tmp_path)
    assert tuple(tmp_path.iterdir()) == before


@pytest.mark.parametrize(
    "args",
    [
        ["publication", "preflight", "--contract", "x", "--upstream-inventory", "x", "--reconstruction-acceptance", "x", "--config-root", "x", "--run-root", "x"],
        ["publication", "run", "--contract", "x", "--upstream-inventory", "x", "--reconstruction-acceptance", "x", "--config-root", "x", "--run-root", "x", "--tools-root", "x", "--python", "x", "--powershell", "x", "--pdftoppm", "x", "--word", "x", "--run-id", "old"],
        ["publication", "resume", "--run-root", "x", "--python", "x", "--powershell", "x", "--pdftoppm", "x", "--word", "x"],
        ["publication", "record-acceptance", "--run-root", "x", "--artifact-kind", "pdf", "--evidence", "x", "--destination", "x", "--user-decision-reference", "old"],
        ["publication", "revise-docx", "--base-package", "x", "--reviewed-docx", "x", "--output-root", "x", "--libreoffice", "x", "--pdftoppm", "x", "--user-decision-reference", "old"],
        ["publication", "record-revision-review", "--package-root", "x", "--user-decision-reference", "old"],
        ["publication", "materialize-release", "--source-root", "x", "--output-root", "x"],
    ],
)
def test_legacy_publication_cli_fails_before_dispatch(tmp_path: Path, monkeypatch, capsys, args) -> None:
    monkeypatch.chdir(tmp_path)
    assert kb_main(args) == 2
    error = json.loads(capsys.readouterr().err)
    assert error["state"] == "blocked"
    assert "DOCX-only" in error["error"]
    assert list(tmp_path.iterdir()) == []


def test_legacy_reviewed_reader_cli_fails_before_output(tmp_path: Path, monkeypatch, capsys) -> None:
    monkeypatch.setattr(sys, "argv", ["revise_reviewed_reader", "--manifest", "x", "--docx", "x", "--html", "x", "--assets", "x", "--source-pdf", "x", "--output-root", "x"])
    monkeypatch.chdir(tmp_path)
    assert old_reader_main() == 2
    error = json.loads(capsys.readouterr().err)
    assert error["state"] == "blocked"
    assert "DOCX-only" in error["error"]
    assert list(tmp_path.iterdir()) == []


def test_public_legacy_adapter_factory_and_writers_fail_before_tool_or_stage_access(tmp_path: Path) -> None:
    runtime = PublicationAdapterRuntime(tmp_path / "missing-python", tmp_path / "missing-shell",
                                        tmp_path / "missing-poppler", tmp_path / "missing-word")
    with pytest.raises(PublicationAdapterError, match="DOCX-only"):
        fixed_publication_adapters(runtime)
    with pytest.raises(PublicationAdapterError, match="DOCX-only"):
        build_html_candidate(master_ru=tmp_path / "missing", master_ru_acceptance=tmp_path / "missing",
                             artview_decisions=tmp_path / "missing", artview_application=tmp_path / "missing",
                             effective_visual_config=tmp_path / "missing", artview_projection_root=tmp_path / "missing",
                             base_config=tmp_path / "missing", staging=tmp_path / "missing",
                             output_name="old.html")
    with pytest.raises(PublicationAdapterError, match="DOCX-only"):
        assemble_production_package(tmp_path / "missing", None)
    assert list(tmp_path.iterdir()) == []
