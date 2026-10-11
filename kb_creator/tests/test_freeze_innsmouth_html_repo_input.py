from __future__ import annotations

import importlib.util
from pathlib import Path
import shutil

import pytest


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "kb_creator" / "scripts" / "freeze_innsmouth_html_repo_input.py"
SPEC = importlib.util.spec_from_file_location("freeze_innsmouth_html_repo_input", SCRIPT)
assert SPEC and SPEC.loader
freeze_html = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(freeze_html)


def test_successor_r7f_preflight_contract() -> None:
    result = freeze_html.validate_html_candidate(
        freeze_html.DEFAULT_CANDIDATE_ROOT,
        freeze_html.DEFAULT_MASTER_RU_ROOT,
    )
    assert result["html"] == {
        "name": "The_Innsmouth_Terror_RU.html",
        "bytes": 223_459,
        "sha256": "040C7AF42A76241B3BC280350C0151096CF81E5F9A9194E6F5003B0388E4EF39",
    }
    assert result["checks"]["images"] == 32
    assert result["checks"]["broken_fragments"] == 0
    assert result["checks"]["full_width_figures"] == 11
    assert result["checks"]["inline_figures"] == 21
    assert result["checks"]["title_pages"] == 1


def test_promote_and_verify_are_deterministic(tmp_path: Path) -> None:
    target = tmp_path / "accepted_html"
    promoted = freeze_html.promote(
        freeze_html.DEFAULT_CANDIDATE_ROOT,
        freeze_html.DEFAULT_MASTER_RU_ROOT,
        target,
        "2026-08-30",
    )
    verified = freeze_html.verify(target, freeze_html.DEFAULT_MASTER_RU_ROOT)
    assert promoted == verified
    assert {path.name for path in target.iterdir()} == {
        "The_Innsmouth_Terror_RU.html",
        "HTML.acceptance.json",
        "assets",
    }
    assert verified["manifest"]["bytes"] > 0


def test_verify_rejects_html_mutation(tmp_path: Path) -> None:
    target = tmp_path / "accepted_html"
    freeze_html.promote(
        freeze_html.DEFAULT_CANDIDATE_ROOT,
        freeze_html.DEFAULT_MASTER_RU_ROOT,
        target,
        "2026-08-30",
    )
    html = target / freeze_html.HTML_NAME
    html.write_bytes(html.read_bytes() + b"\n")
    with pytest.raises(ValueError, match="identity mismatch"):
        freeze_html.verify(target, freeze_html.DEFAULT_MASTER_RU_ROOT)


def test_verify_rejects_extra_asset(tmp_path: Path) -> None:
    target = tmp_path / "accepted_html"
    freeze_html.promote(
        freeze_html.DEFAULT_CANDIDATE_ROOT,
        freeze_html.DEFAULT_MASTER_RU_ROOT,
        target,
        "2026-08-30",
    )
    source = next((target / "assets").iterdir())
    shutil.copy2(source, target / "assets" / "unexpected.jpg")
    with pytest.raises(ValueError, match="assets differ"):
        freeze_html.verify(target, freeze_html.DEFAULT_MASTER_RU_ROOT)


def test_promote_refuses_existing_target(tmp_path: Path) -> None:
    target = tmp_path / "accepted_html"
    target.mkdir()
    with pytest.raises(FileExistsError, match="already exists"):
        freeze_html.promote(
            freeze_html.DEFAULT_CANDIDATE_ROOT,
            freeze_html.DEFAULT_MASTER_RU_ROOT,
            target,
            "2026-08-30",
        )
