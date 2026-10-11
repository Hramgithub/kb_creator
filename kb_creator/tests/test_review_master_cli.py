"""Operator entry point; intake integration tests prove the underlying build."""
import json
from pathlib import Path

from kb_creator.__main__ import main
from kb_creator.pipeline import five_step_intake


def test_review_master_cli_passes_explicit_authorities(monkeypatch, capsys):
    calls = []

    def build(materialized, evidence, output, *, binding_root=None):
        calls.append((materialized, evidence, output, binding_root))
        return {"state": "verified_review_master_en"}

    monkeypatch.setattr(five_step_intake, "build_review_master_en", build)
    assert main(["translate", "build-review-master",
                 "--materialized-root", "book/materialized",
                 "--final-evidence", "book/author/evidence.json",
                 "--output-root", "book/master-next",
                 "--binding-root", "book"]) == 0
    assert calls == [(Path("book/materialized"), Path("book/author/evidence.json"),
                      Path("book/master-next"), Path("book"))]
    assert json.loads(capsys.readouterr().out)["state"] == "verified_review_master_en"


def test_review_master_cli_rejects_missing_authority_without_output(tmp_path, capsys):
    output = tmp_path / "master"
    assert main(["translate", "build-review-master",
                 "--materialized-root", str(tmp_path / "missing-materialized"),
                 "--final-evidence", str(tmp_path / "missing-evidence.json"),
                 "--output-root", str(output)]) == 2
    result = capsys.readouterr()
    assert not result.out
    assert json.loads(result.err)["state"] == "blocked"
    assert not output.exists()
