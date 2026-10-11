"""One real compact v2 R1 chain across the reviewed-draft pipeline."""
from __future__ import annotations

import json
import shutil
from pathlib import Path

import pytest

from kb_creator.pipeline import language_continuation as continuation
from kb_creator.pipeline import source_choice_batches as batches
from kb_creator.pipeline import source_choice_translation as choices
from kb_creator.pipeline.five_step_intake import build_review_master_en
from kb_creator.pipeline.source_choice_successor_preparation import prepare_source_choice_successor
from kb_creator.pipeline.review_draft_materialization import verify_final_review_draft
from kb_creator.scripts import author_reviewed_semantic_decisions as author
from kb_creator.scripts import materialize_mineru_ai_merge as materializer
from kb_creator.tests import test_review_draft_preparation as preparation_fixture


def _submission(queue_path: Path, issue_id: str, alternative_id: str, path: Path) -> Path:
    value = {
        "schema": choices.SUBMISSION_SCHEMA_V2,
        "state": "submitted",
        "queue": {"path": str(queue_path.resolve()), **choices.file_identity(queue_path)},
        "choices": [{
            "issue_id": issue_id,
            "disposition": "selected_alternative",
            "alternative_id": alternative_id,
            "reason": "Fixture selects the alternate raw source witness.",
            "label": None,
        }],
    }
    path.write_text(json.dumps(value), encoding="utf-8")
    return path


@pytest.mark.parametrize("selection,structural_route", [
    ("provisional", False), ("different", False), ("different", True),
])
def test_real_v2_r1_chain_reaches_verified_master_and_language_readiness(tmp_path, monkeypatch, selection, structural_route):
    """Use the production composer, Stage05/06, materializer and both MASTER APIs.

    The imported fixture owns only the archived replay boundary.  It executes
    the real R0 author/audit/materializer/MASTER route and leaves its compact
    artifacts under ``tmp_path`` for this test's independent v2/R1 continuation.
    """
    renderer = shutil.which("pdftoppm")
    assert renderer is not None
    monkeypatch.setenv("KB_CREATOR_PDFTOPPM", renderer)
    preparation_fixture.test_production_composer_binds_actual_pending_alternative_before_authoring(
        monkeypatch, tmp_path, False, structural_route)

    # The fixture deliberately damages this source binding as its final negative
    # assertion.  Restore the original sealed composer configuration before the
    # R1 producer reopens the R0 input.
    config = tmp_path / "config.json"
    config.write_text(json.dumps({
        "schema": "kb_creator.review_draft_preparation_config.v1",
        "forced_selections": [],
    }), encoding="utf-8")

    r0_master = tmp_path / "master"
    candidate = tmp_path / "mechanical"
    run_root = Path(json.loads((candidate / "mechanical_draft.json").read_text(encoding="utf-8"))["run_root"])
    r0_input = tmp_path / ("structural-input.json" if structural_route else "composed/review-draft-input.json")
    queue_root = tmp_path / "queue-v2"
    prepared = choices.prepare_v2(r0_master, candidate, queue_root, binding_root=tmp_path)
    queue_path = Path(prepared["queue"])
    queue = json.loads(queue_path.read_text(encoding="utf-8"))
    assert len(queue["choices"]) == 1
    choice = queue["choices"][0]
    assert choice["r0_source_preimage"]["source_excerpt_sha256"]
    assert choice["r0_reader_span"]["text_sha256"]
    if selection == "provisional":
        selected = next(row for row in choice["alternatives"]
                        if row["alternative_id"] == choice["provisional_alternative_id"])
    else:
        selected = next(row for row in choice["alternatives"]
                        if row["selectable"] and row["alternative_id"] != choice["provisional_alternative_id"])
        assert selected["raw_text_sha256"] != choice["r0_source_preimage"]["source_excerpt_sha256"]
        assert selected["reader_text"] != choice["reader_projection"]["reader_text"]
    batch_root = tmp_path / "review-batches"
    assert batches.prepare_batches(queue_path, batch_root)["choices"] == 1
    ledger_result = batches.collect_submissions(
        queue_path, [_submission(queue_path, choice["issue_id"], selected["alternative_id"], tmp_path / "source-choice-submission.json")],
        tmp_path / "ledger-v2")
    ledger_path = Path(ledger_result["ledger"])
    assert choices.verify_ledger_v2(ledger_path)["choices"] == 1

    r1 = prepare_source_choice_successor(
        input_path=r0_input, binding_root=tmp_path, ledger_path=ledger_path,
        draft_pages=tmp_path / "composed" / "prepared" / "draft-pages",
        spec_paths=sorted((tmp_path / "composed" / "author-specs").glob("*.json")),
        output_dir=tmp_path / "r1-input")
    r1_input = Path(r1["input"]["path"])
    authored = tmp_path / "r1-authored"
    author.author_drafts(run_root, Path(r1["draft_pages"]), authored,
                         [Path(path) for path in r1["spec_paths"]], mode="review_draft",
                         draft_input=r1_input, binding_root=tmp_path)
    stage05 = json.loads((authored / "review-draft-stage05-audit.json").read_text(encoding="utf-8"))
    lexical_rows = [row for row in stage05["pages"][0]["ordered_proof_stream"]
                    if row.get("kind") == "linguistic_source_choice_v1"]
    assert len(lexical_rows) == 1
    assert lexical_rows[0]["r1_text"] == selected["reader_text"]
    evidence = authored / "review-draft-evidence.json"
    descriptor = verify_final_review_draft(run_root=run_root, authored_root=authored,
                                            input_path=r1_input, evidence_path=evidence,
                                            binding_root=tmp_path)
    materialized = tmp_path / "r1-materialized"
    materializer.materialize(Path(descriptor["bundle_root"]), Path(descriptor["raw_root"]),
                             Path(descriptor["decisions_root"]), materialized,
                             review_draft_authority=descriptor, review_draft_binding_root=tmp_path)
    r1_master = tmp_path / "r1-master"
    master_result = build_review_master_en(materialized, evidence, r1_master, binding_root=tmp_path)
    assert master_result["state"] == "verified_review_draft"
    if selection == "different":
        assert "# Alternative heading" in (r1_master / "MASTER_EN.md").read_text(encoding="utf-8")
    if structural_route:
        bindings = json.loads((r1_master / "ISSUE_EN_BINDINGS.v2.json").read_text(encoding="utf-8"))["bindings"]
        assert len(bindings) == 1
        structural = bindings[0]
        assert structural["reader_projection"]["reader_text"] == "# Alternative heading"

    glossary = tmp_path / "glossary" / "terms.json"
    glossary.parent.mkdir()
    glossary.write_text(json.dumps({"terms": [{"source": "Keeper", "target": "Хранитель"}]}), encoding="utf-8")
    language = continuation.prepare_continuation(r1_master, glossary, tmp_path / "language",
                                                  review_binding_root=tmp_path)
    assert language["phase"] == "documentary_draft"
    assert continuation.verify_continuation(tmp_path / "language")["phase"] == "documentary_draft"
