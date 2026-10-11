from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

from kb_creator.pipeline import five_step, five_step_intake as intake
from kb_creator.pipeline import language_continuation as continuation
from kb_creator.pipeline.identity import deterministic_inventory, file_identity
from kb_creator.pipeline.manifests import sealed
from kb_creator.pipeline.reconstruction import resume_engine, run_engine
from kb_creator.pipeline.reconstruction_promotion import materialize_reconstruction_promotion
from kb_creator.tests.test_reconstruction_promotion import (
    _closed_decisions, _contract, _resume_adapters, _run_adapters, _runtime, _source,
)


def _write(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False), encoding="utf-8")


def _read(path):
    return json.loads(path.read_text(encoding="utf-8"))


@pytest.fixture
def predecessor(tmp_path):
    source = tmp_path / "source.pdf"
    _source(source)
    contract = tmp_path / "contract.json"
    _write(contract, _contract(source, 1))
    run = tmp_path / "run"
    upstream = run / "upstream/sample/reconstruction/run-001"
    upstream.parent.mkdir(parents=True)
    run_engine(contract, source, upstream, upstream.name,
               adapters=_run_adapters(), runtime=_runtime(tmp_path / "runtime"))
    decisions, decisions_root = _closed_decisions(upstream, tmp_path / "decisions", 1, None)
    resume_engine(upstream, decisions, decisions_root, adapters=_resume_adapters(upstream, 1))
    _write(upstream / "five-step-reconstruction.task.json", {"schema": "task"})
    result = materialize_reconstruction_promotion(upstream, working_root=run / "upstream")
    package = Path(result["package_root"])
    review = upstream / "agent-review-authority.json"
    _write(review, intake._agent_authority(upstream, package))
    en = run / "master-en-001"
    intake.build_master_en(package, review, en)
    state = {"schema": five_step.SCHEMA, "phase": "documentary_draft", "state": "failed",
             "source": {"path": str(source), "identity": file_identity(source)},
             "paths": {"master_en": str(en / "MASTER_EN.md")},
             "evidence": [{"step": 2, "root": "master-en-001",
                           "files": deterministic_inventory(en), "code": five_step._codes(2)},
                          {"step": 3, "root": "obsolete-language", "files": [], "code": []}]}
    five_step._save(run, state)
    glossary = tmp_path / "glossaries/terms.json"
    glossary.parent.mkdir()
    _write(glossary, {"terms": [{"source": "Keeper", "target": "Хранитель"}]})
    return run, glossary


def _draft(prepared, destination):
    value = _read(Path(prepared["template_path"]))
    task = _read(Path(prepared["task_path"]))
    for row, source in zip(value["units"], task["units"]):
        # A mechanics fixture, not evidence of book translation quality.
        row["ru_text"] = source["source_text"].replace("Keeper", "Хранитель")
    _write(destination, value)
    return destination


def test_real_master_to_final_language_preserves_predecessor(predecessor, tmp_path):
    run, glossary = predecessor
    before = deterministic_inventory(run)
    prepared = continuation.prepare_continuation(run, glossary, tmp_path / "prepared")
    assert prepared["phase"] == "documentary_draft"
    assert Path(prepared["task_path"]).is_file()
    drafted = continuation.submit_continuation(
        tmp_path / "prepared", _draft(prepared, tmp_path / "draft.json"), tmp_path / "drafted")
    assert drafted["phase"] == "proofread_final"
    proof = _read(Path(drafted["template_path"]))
    for row in proof["units"]:
        row["disposition"] = "checked_unchanged"
    _write(tmp_path / "proof.json", proof)
    final = continuation.submit_continuation(tmp_path / "drafted", tmp_path / "proof.json", tmp_path / "final")
    assert final["phase"] == "language_complete"
    assert (Path(final["final_root"]) / "MASTER_RU.md").is_file()
    assert final["book_acceptance"] == final["docx_package"] == "pending"
    assert deterministic_inventory(run) == before
    with pytest.raises(ValueError, match="already complete"):
        continuation.submit_continuation(tmp_path / "final", tmp_path / "proof.json", tmp_path / "extra")


@pytest.mark.parametrize("kind", ["source", "master", "spans", "step2_code", "seal", "wrong_pdf"])
def test_changed_source_or_step2_cannot_be_reused(predecessor, tmp_path, kind):
    run, glossary = predecessor
    state = _read(run / "state.json")
    if kind == "source":
        Path(state["source"]["path"]).write_bytes(b"changed")
    elif kind in {"master", "spans"}:
        name = "MASTER_EN.md" if kind == "master" else "EN_SOURCE_SPANS.json"
        (run / "master-en-001" / name).write_text("changed", encoding="utf-8")
    elif kind == "seal":
        state["state_sha256"] = "0" * 64
        _write(run / "state.json", state)
    else:
        if kind == "step2_code":
            state["evidence"][0]["code"] = []
        else:
            alternate = tmp_path / "alternate.pdf"
            alternate.write_bytes(b"another source")
            state["source"] = {"path": str(alternate), "identity": file_identity(alternate)}
        five_step._save(run, state)
    with pytest.raises(ValueError):
        continuation.prepare_continuation(run, glossary, tmp_path / "prepared")
    assert not (tmp_path / "prepared").exists()


@pytest.mark.parametrize("kind", ["glossary", "task", "extra", "code", "predecessor"])
def test_changed_continuation_rejected(predecessor, tmp_path, monkeypatch, kind):
    run, glossary = predecessor
    root = tmp_path / "prepared"
    continuation.prepare_continuation(run, glossary, root)
    if kind == "code":
        monkeypatch.setattr(continuation, "_codes", lambda: [])
    elif kind == "predecessor":
        state = _read(run / "state.json")
        state["state"] = "changed"
        five_step._save(run, state)
    else:
        path = root / {"glossary": "glossary.json", "task": "language/draft.task.json", "extra": "extra.txt"}[kind]
        path.write_text("changed", encoding="utf-8")
    with pytest.raises(ValueError):
        continuation.verify_continuation(root)


def test_failed_submission_is_not_usable_and_retry_uses_new_output(predecessor, tmp_path):
    run, glossary = predecessor
    prepared = continuation.prepare_continuation(run, glossary, tmp_path / "prepared")
    bad = tmp_path / "bad.json"
    _write(bad, _read(Path(prepared["template_path"])))
    with pytest.raises(ValueError):
        continuation.submit_continuation(tmp_path / "prepared", bad, tmp_path / "failed")
    assert (tmp_path / "failed/FAILED.json").is_file()
    assert not (tmp_path / "failed/CONTINUATION.json").exists()
    before = deterministic_inventory(tmp_path / "failed")
    good = _draft(prepared, tmp_path / "good.json")
    with pytest.raises(ValueError, match="already exists"):
        continuation.submit_continuation(tmp_path / "prepared", good, tmp_path / "failed")
    assert deterministic_inventory(tmp_path / "failed") == before
    assert continuation.submit_continuation(tmp_path / "prepared", good, tmp_path / "retry")["phase"] == "proofread_final"


def test_prepare_rejects_output_inside_predecessor(predecessor):
    run, glossary = predecessor
    with pytest.raises(ValueError, match="overlaps"):
        continuation.prepare_continuation(run, glossary, run / "continuation")
    assert not (run / "continuation").exists()


def test_cli_works_without_test_pythonpath(predecessor, tmp_path):
    run, glossary = predecessor
    environment = dict(os.environ)
    environment.pop("PYTHONPATH", None)
    completed = subprocess.run([sys.executable, "-m", "kb_creator.scripts.continue_language", "prepare",
                                "--predecessor-run", str(run), "--glossary", str(glossary),
                                "--output", str(tmp_path / "cli")], cwd=five_step.ROOT,
                               env=environment, capture_output=True, text=True, timeout=60)
    assert completed.returncode == 0, completed.stdout + completed.stderr
    assert json.loads(completed.stdout)["phase"] == "documentary_draft"


def _reseal_continuation(root):
    value = _read(root / continuation.MANIFEST)
    value.pop("continuation_sha256")
    value["files"] = [row for row in deterministic_inventory(root) if row["path"] != continuation.MANIFEST]
    _write(root / continuation.MANIFEST, sealed(continuation.SCHEMA, value, digest_key="continuation_sha256"))


def _reseal_task(root, mutate):
    path = root / "language/draft.task.json"
    task = _read(path)
    task.pop("task_sha256")
    mutate(task)
    _write(path, sealed(task["schema"], task, digest_key="task_sha256"))
    _reseal_continuation(root)


def test_resealed_wrong_unit_coverage_rejected(predecessor, tmp_path):
    run, glossary = predecessor
    root = tmp_path / "prepared"
    prepared = continuation.prepare_continuation(run, glossary, root)
    path = Path(prepared["task_path"])
    task = _read(path)
    task.pop("task_sha256")
    task["units"] = task["units"][:-1]
    _write(path, sealed(task["schema"], task, digest_key="task_sha256"))
    _reseal_continuation(root)
    with pytest.raises(ValueError, match="unit coverage"):
        continuation.verify_continuation(root)


def test_prepared_v3_task_context_is_verified(predecessor, tmp_path):
    run, glossary = predecessor
    root = tmp_path / "prepared"
    continuation.prepare_continuation(run, glossary, root)
    assert continuation.verify_continuation(root)["phase"] == "documentary_draft"


@pytest.mark.parametrize("mutate", [
    lambda task: task.__setitem__("source_unit_context", []),
    lambda task: task.pop("source_unit_context"),
])
def test_resealed_prepared_v3_context_tamper_is_rejected(predecessor, tmp_path, mutate):
    run, glossary = predecessor
    root = tmp_path / "prepared"
    continuation.prepare_continuation(run, glossary, root)
    _reseal_task(root, mutate)
    with pytest.raises(ValueError, match="source-unit context"):
        continuation.verify_continuation(root)


def test_resealed_prepared_v2_task_remains_verifiable(predecessor, tmp_path):
    run, glossary = predecessor
    root = tmp_path / "prepared"
    continuation.prepare_continuation(run, glossary, root)

    def legacy(task):
        task["schema"] = "kb_creator.five_step_language_draft_task.v2"
        task.pop("source_unit_context")

    _reseal_task(root, legacy)
    assert continuation.verify_continuation(root)["phase"] == "documentary_draft"


def test_resealed_draft_must_match_original_submission(predecessor, tmp_path):
    run, glossary = predecessor
    prepared = continuation.prepare_continuation(run, glossary, tmp_path / "prepared")
    root = tmp_path / "drafted"
    continuation.submit_continuation(tmp_path / "prepared", _draft(prepared, tmp_path / "draft.json"), root)
    path = root / "result/documentary_draft.json"
    draft = _read(path)
    draft.pop("draft_sha256")
    draft["units"][-1]["ru_text"] += " Добавлено без основания."
    _write(path, sealed(draft["schema"], draft, digest_key="draft_sha256"))
    _reseal_continuation(root)
    with pytest.raises(ValueError, match="does not match source submission"):
        continuation.verify_continuation(root)
@pytest.mark.parametrize("kind,key", [("strict_step2", "run_state"), ("verified_review_draft", "review_master")])
def test_predecessor_reference_supports_both_verified_routes(kind, key):
    record = {"path": "C:/fixture/authority.json", "identity": {"bytes": 1, "sha256": "A" * 64}}
    assert continuation._predecessor_reference({"predecessor_kind": kind, key: record}) == record
