from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

from kb_creator.pipeline.identity import canonical_bytes, deterministic_inventory, file_identity, sha256_bytes
from kb_creator.scripts.verify_production_package import VerificationError, verify_package
from kb_creator.tests.test_publication_control_plane import _advance_to_package, _fixture


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "verify_production_package.py"


def _reseal(package: Path) -> None:
    path = package / "PRODUCTION_MANIFEST.json"
    value = json.loads(path.read_text(encoding="utf-8"))
    value["inventory"] = [row for row in deterministic_inventory(package) if row["path"] != "PRODUCTION_MANIFEST.json"]
    value["pipeline_snapshot"] = [
        {"path": item.relative_to(package).as_posix(), **file_identity(item)}
        for item in sorted((package / "pipeline").glob("*"))
        if item.is_file()
    ]
    value["manifest_sha256"] = sha256_bytes(canonical_bytes({key: item for key, item in value.items() if key != "manifest_sha256"}))
    path.write_bytes(canonical_bytes(value) + b"\n")


def test_stdlib_verifier_accepts_closed_synthetic_candidate(tmp_path: Path) -> None:
    package = _advance_to_package(_fixture(tmp_path))

    result = verify_package(package)

    assert result["state"] == "candidate_for_release_review"
    assert result["release_state"] == "not_reviewed"
    assert result["pdf_count"] == 1


def test_copied_offline_verifier_runs_in_isolated_mode(tmp_path: Path) -> None:
    package = _advance_to_package(_fixture(tmp_path))
    copied = package / "pipeline" / "verify.py"
    shutil.copy2(SCRIPT, copied)
    _reseal(package)

    process = subprocess.run(
        [sys.executable, "-I", str(copied), "--package-root", str(package)],
        capture_output=True,
        text=True,
        check=False,
        timeout=60,
    )

    assert process.returncode == 0, process.stderr
    assert json.loads(process.stdout)["state"] == "candidate_for_release_review"


@pytest.mark.parametrize("mode", ["extra", "modified"])
def test_verifier_rejects_inventory_drift_without_resealing(tmp_path: Path, mode: str) -> None:
    package = _advance_to_package(_fixture(tmp_path))
    if mode == "extra":
        (package / "unexpected.txt").write_text("extra", encoding="utf-8")
    else:
        (package / "MASTER_RU.md").write_text("modified", encoding="utf-8")

    with pytest.raises(VerificationError, match="inventory mismatch"):
        verify_package(package)


def test_verifier_rejects_reparse_content(tmp_path: Path) -> None:
    package = _advance_to_package(_fixture(tmp_path))
    outside = tmp_path / "outside.txt"
    outside.write_text("outside", encoding="utf-8")
    link = package / "escape.txt"
    try:
        os.symlink(outside, link)
    except OSError as error:
        pytest.skip(f"host cannot create test symlink: {error}")

    with pytest.raises(VerificationError, match="reparse"):
        verify_package(package)
