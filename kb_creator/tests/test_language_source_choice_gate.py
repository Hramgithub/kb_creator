from __future__ import annotations

import hashlib
import json

import pytest

from kb_creator.pipeline import language_continuation as continuation
from kb_creator.pipeline.five_step_intake import build_review_master_en
from kb_creator.tests.test_review_draft_materialization import _materialized_review_route


@pytest.mark.parametrize("kind,blocked", [
    ("translation_source_choice_pending", True),
    ("source_material_blocked", True),
    ("semantic_source_uncertainty", False),
    ("editorial_choice", False),
    (None, False),
])
def test_actual_review_master_source_state_controls_language_prepare(tmp_path, monkeypatch, kind, blocked):
    issues = [] if kind is None else [{
        "issue_id": "source-001", "kind": kind, "reason": "source reading question",
        "source_pdf_sha256": "placeholder", "source_page": 1,
        "source_selector": {"view": "original_pipeline_txt", "raw_index": 1},
        "source_excerpt_en": "Source",
        "source_excerpt_sha256": hashlib.sha256(b"Source").hexdigest().upper(),
        "evidence": [], "candidate_span": {}, "state": "open",
    }]
    master = tmp_path / "master"
    if kind == "translation_source_choice_pending":
        # Pending lexical choices require a real mechanical candidate and its
        # conflicting raw witnesses; a placeholder manifest cannot prove this gate.
        from kb_creator.tests.test_review_draft_preparation import (
            test_production_composer_binds_actual_pending_alternative_before_authoring,
        )
        test_production_composer_binds_actual_pending_alternative_before_authoring(
            monkeypatch, tmp_path, False, False)
        # That fixture ends with a deliberate config-drift negative. Restore its
        # original bytes before reopening the genuine R0 authority here.
        (tmp_path / "config.json").write_text(json.dumps({
            "schema": "kb_creator.review_draft_preparation_config.v1", "forced_selections": [],
        }), encoding="utf-8")
    else:
        # Archive authority is injected; Stage05/06, MASTER and language run real.
        materialized, evidence = _materialized_review_route(tmp_path, monkeypatch, issues)
        build_review_master_en(materialized, evidence, master, binding_root=tmp_path)
    glossary = tmp_path / "glossary" / "terms.json"
    glossary.parent.mkdir()
    glossary.write_text(json.dumps({"terms": [{"source": "Keeper", "target": "Хранитель"}]}), encoding="utf-8")
    output = tmp_path / "language-successor"
    if blocked:
        with pytest.raises(continuation.LanguageContinuationError, match="resolve source choices"):
            continuation.prepare_continuation(master, glossary, output, review_binding_root=tmp_path)
        assert not output.exists()
    else:
        result = continuation.prepare_continuation(master, glossary, output, review_binding_root=tmp_path)
        assert result["phase"] == "documentary_draft"
        assert continuation.verify_continuation(output)["phase"] == "documentary_draft"
