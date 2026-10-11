from __future__ import annotations

import importlib.util
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "build_innsmouth_final_result.py"


def load_module():
    spec = importlib.util.spec_from_file_location("build_innsmouth_final_result", SCRIPT)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_compare_snapshots_detects_kb_changes():
    module = load_module()
    before = {
        "Knowledge_Base_v6/a.md": {"size_bytes": 1, "sha256": "old"},
        "Knowledge_Base_v6/b.md": {"size_bytes": 2, "sha256": "same"},
    }
    after = {
        "Knowledge_Base_v6/b.md": {"size_bytes": 2, "sha256": "same"},
        "Knowledge_Base_v6/c.md": {"size_bytes": 3, "sha256": "new"},
    }

    findings = module.compare_snapshots(before, after)

    assert {item["code"] for item in findings} == {"kb_file_deleted", "kb_file_created"}


def test_compare_snapshots_passes_when_identical():
    module = load_module()
    snapshot = {"Knowledge_Base_v6/a.md": {"size_bytes": 1, "sha256": "same"}}

    assert module.compare_snapshots(snapshot, dict(snapshot)) == []
