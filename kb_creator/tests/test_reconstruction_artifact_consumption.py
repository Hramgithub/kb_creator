"""Archived replay consumption keeps sealed artifacts separate from freshness."""
from __future__ import annotations

from pathlib import Path

import pytest

from kb_creator.pipeline import reconstruction_replay as replay
from kb_creator.pipeline.identity import canonical_bytes, sha256_bytes


def _sealed_run_and_closure() -> tuple[dict, dict]:
    row = {"path": "kb_creator/scripts/run_mineru_three_view.ps1", "bytes": 3, "sha256": "A" * 64}
    files = [row]
    return (
        {"implementation": {"files": files, "inventory_sha256": sha256_bytes(canonical_bytes(files))}},
        {"files": files, "producer_closure_sha256": sha256_bytes(canonical_bytes(files))},
    )


def test_archived_closure_accepts_recorded_bytes_and_reports_wrapper_drift(monkeypatch):
    run, closure = _sealed_run_and_closure()
    monkeypatch.setattr(replay, "_current_row", lambda path: {"path": path, "bytes": 4, "sha256": "B" * 64})

    freshness = replay._validate_archived_closure(run, closure, "02-mineru-three-view")

    assert freshness == {
        "state": "stale",
        "changed_paths": ["kb_creator/scripts/run_mineru_three_view.ps1"],
        "unknown_paths": [],
    }


@pytest.mark.parametrize("mutation", ("inventory", "closure_digest", "closure_row"))
def test_archived_closure_rejects_tampered_sealed_evidence(mutation):
    run, closure = _sealed_run_and_closure()
    if mutation == "inventory":
        run["implementation"]["inventory_sha256"] = "0" * 64
    elif mutation == "closure_digest":
        closure["producer_closure_sha256"] = "0" * 64
    else:
        closure["files"] = [{"path": "kb_creator/scripts/run_mineru_three_view.ps1", "bytes": 4, "sha256": "B" * 64}]

    with pytest.raises(replay.ReplayError, match="archived_(implementation_inventory|producer_closure)"):
        replay._validate_archived_closure(run, closure, "02-mineru-three-view")


def test_archived_closure_reports_unavailable_current_producer_separately(monkeypatch):
    run, closure = _sealed_run_and_closure()
    monkeypatch.setattr(replay, "_current_row", lambda _path: (_ for _ in ()).throw(replay.ReplayError("closure_member_missing_or_unsafe")))

    freshness = replay._validate_archived_closure(run, closure, "02-mineru-three-view")

    assert freshness["state"] == "unknown"
    assert freshness["changed_paths"] == []
    assert freshness["unknown_paths"] == ["kb_creator/scripts/run_mineru_three_view.ps1"]
