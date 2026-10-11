from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import shutil

import pytest


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "kb_creator" / "scripts" / "freeze_innsmouth_pdf_repo_output.py"
SPEC = importlib.util.spec_from_file_location("freeze_innsmouth_pdf_repo_output", SCRIPT)
assert SPEC and SPEC.loader
freeze_pdf = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(freeze_pdf)


def test_accepted_pdf_package_verifies() -> None:
    result = freeze_pdf.verify(freeze_pdf.DEFAULT_TARGET_ROOT)
    assert result["state"] == "ACCEPTED_INNSMOUTH_PDF_REPO_OUTPUT_VERIFIED"
    assert result["pdf"]["bytes"] == 11_566_429
    assert result["structural"]["pages"] == 46
    assert result["visual_qa"]["render_count"] == 46


def test_verify_rejects_pdf_and_manifest_mutation(tmp_path: Path) -> None:
    copied = tmp_path / "accepted_pdf"
    shutil.copytree(freeze_pdf.DEFAULT_TARGET_ROOT, copied)
    pdf = copied / freeze_pdf.PDF_NAME
    pdf.write_bytes(pdf.read_bytes() + b"tamper")
    with pytest.raises(ValueError, match="PDF identity mismatch"):
        freeze_pdf.verify(copied)

    shutil.rmtree(copied)
    shutil.copytree(freeze_pdf.DEFAULT_TARGET_ROOT, copied)
    manifest_path = copied / freeze_pdf.MANIFEST_NAME
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["accepted_on"] = "2099-01-01"
    manifest_path.write_bytes(freeze_pdf.canonical_json(manifest))
    with pytest.raises(ValueError, match="manifest mismatch"):
        freeze_pdf.verify(copied)
