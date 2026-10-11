from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import re
import sys


SCRIPT = (
    Path(__file__).resolve().parents[1]
    / "scripts"
    / "verify_innsmouth_master_en_repo_input.py"
)
sys.path.insert(0, str(SCRIPT.parent))
SPEC = importlib.util.spec_from_file_location("innsmouth_master_en_repo_verifier", SCRIPT)
assert SPEC and SPEC.loader
verifier = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(verifier)


def test_repository_input_inventory_and_root_identities():
    report = verifier.verify(verifier.DEFAULT_ROOT)
    assert report["file_count"] == 36
    assert report["asset_count"] == 33
    assert report["total_bytes"] == 9_505_083


def test_repository_input_qa_and_structure():
    root = verifier.DEFAULT_ROOT
    qa = json.loads((root / "MASTER_EN.qa.json").read_text(encoding="utf-8"))
    acceptance = json.loads(
        (root / "MASTER_EN.acceptance.json").read_text(encoding="utf-8")
    )
    markdown = (root / "MASTER_EN.md").read_bytes()
    assert qa["state"] == "MASTER_EN_READER_PACKAGE_READY"
    assert qa["final_counts"] == acceptance["package"]["counts"]
    assert acceptance["state"] == "ACCEPTED_MASTER_EN_REPO_INPUT"
    assert acceptance["accepted_on"] == "2026-08-30"
    assert acceptance["package"]["markdown"]["sha256"] == (
        "31F67A2865BF00A48F197333A162AD56AA0F56061068D3BFD6B564591F9AA3C2"
    )
    assert b"<!-- mineru-page:" not in markdown
    assert b"<!-- table-evidence:" not in markdown
    assert len(re.findall(rb"(?m)^#{1,6} ", markdown)) == 153
    assert markdown.count(b"<table>") == 51
    assert markdown.count(b"[link](#nri-") == 33
    assert len(re.findall(rb'<a id="[^"]+"></a>', markdown)) == 52
    assert b"334f14bd517569e118d9445575f8c2bed6a356c7504142c3ac75a6f472e954f5" not in markdown
