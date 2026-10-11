"""Focused downstream validation for native Stage04 replay authority."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

from kb_creator.pipeline import reconstruction_replay_resume as resume


def _identity(path: Path) -> dict[str, object]:
    return {"bytes": path.stat().st_size, "sha256": hashlib.sha256(path.read_bytes()).hexdigest().upper()}


def _write(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value), encoding="utf-8")


def _v2_visual(run_root: Path) -> dict[str, object]:
    bundle = run_root / "outputs/04-visual-merge-bundle"
    png = bundle / "visual/triptychs/page-001.png"
    packet = bundle / "merge_packets/pages/page-001.json"
    png.parent.mkdir(parents=True, exist_ok=True)
    png.write_bytes(b"native-png-authority")
    _write(packet, {"packet": 1})
    _write(run_root / "outputs/03-compare-views/comparison.json", {"views": {}})
    return {
        "schema": "kb_creator.mineru_visual_merge_bundle.v2",
        "files": [
            {"path": "visual/triptychs/page-001.png", **_identity(png), "dimensions": [1200, 800]},
            {"path": "merge_packets/pages/page-001.json", **_identity(packet)},
        ],
    }


def test_native_v2_inventory_projects_dimensions_only_after_identity_check(tmp_path: Path) -> None:
    visual = _v2_visual(tmp_path)
    actual = resume._visual_inventory(tmp_path, visual)
    assert actual == {
        "outputs/04-visual-merge-bundle/visual/triptychs/page-001.png": _identity(
            tmp_path / "outputs/04-visual-merge-bundle/visual/triptychs/page-001.png"
        ),
        "outputs/04-visual-merge-bundle/merge_packets/pages/page-001.json": _identity(
            tmp_path / "outputs/04-visual-merge-bundle/merge_packets/pages/page-001.json"
        ),
    }


@pytest.mark.parametrize("mutation", ["missing_dimensions", "invalid_dimensions", "dimensions_on_json", "case_collision"])
def test_native_v2_inventory_rejects_noncanonical_rows(tmp_path: Path, mutation: str) -> None:
    visual = _v2_visual(tmp_path)
    files = visual["files"]
    assert isinstance(files, list)
    if mutation == "missing_dimensions":
        files[0].pop("dimensions")
    elif mutation == "invalid_dimensions":
        files[0]["dimensions"] = [0, 800]
    elif mutation == "dimensions_on_json":
        files[1]["dimensions"] = [1, 1]
    else:
        duplicate = dict(files[0])
        duplicate["path"] = "VISUAL/TRIPTYCHS/PAGE-001.PNG"
        files.append(duplicate)
    with pytest.raises(resume.ReplayResumeError):
        resume._visual_inventory(tmp_path, visual)
