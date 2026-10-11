"""Closed Stage05 lexical-proof boundary used by retained structural issues."""
from __future__ import annotations

import json

import pytest

from kb_creator.pipeline.identity import canonical_bytes, file_identity, sha256_bytes
from kb_creator.pipeline.reader_occurrence_projection import (
    ReaderOccurrenceError,
    validate_linguistic_source_choice_stage05_row,
)


def _row(tmp_path):
    locator = {"view": "original_pipeline_txt", "raw_index": 10, "field": "text"}
    anchor = {"view": "original_pipeline_txt", "raw_index": 10}
    replay = {"schema": "kb_creator.raw_reader_replay.v1", "anchor_source_locator": anchor,
              "r0_preimage_sha256": sha256_bytes(b"# Stable heading")}
    ledger = {"source_choices": [{"issue_id": "choice-1", "disposition": "selected_alternative",
        "alternative_id": "alt-1", "chosen_raw_alternative": {"source_locator": locator, "text_sha256": sha256_bytes(b"Alternative heading")},
        "raw_reader_replay": replay, "intended_reader_successor": {"text": "# Alternative heading", "text_sha256": sha256_bytes(b"# Alternative heading")}}]}
    path = tmp_path / "SOURCE_CHOICE_LEDGER.v2.json"; path.write_text(json.dumps(ledger), encoding="utf-8")
    record = {"path": str(path), **file_identity(path)}
    mapping = {"kind": "selected", "unit": {"view_id": "original_pipeline_txt", "raw_index": 10}, "markdown_span": [0, 18]}
    return {"kind": "linguistic_source_choice_v1", "unit": mapping["unit"], "markdown_span": [0, 18], "r1_span": [0, 18],
            "r1_text": "# Alternative heading", "r1_text_sha256": sha256_bytes(b"# Alternative heading"),
            "r0_anchor_source_key": anchor, "r0_preimage_sha256": replay["r0_preimage_sha256"],
            "selected_raw_locator": locator, "selected_raw_text_sha256": sha256_bytes(b"Alternative heading"),
            "issue_id": "choice-1", "alternative_id": "alt-1", "ledger": record, "ledger_identity": "sealed-ledger",
            "raw_reader_replay": replay, "row_sha256": sha256_bytes(canonical_bytes(mapping))}


def test_linguistic_stage05_proof_rejects_stale_duplicate_and_missing_fields(tmp_path, monkeypatch):
    from kb_creator.pipeline import source_choice_translation
    calls = []
    monkeypatch.setattr(source_choice_translation, "verify_ledger_v2", lambda _path: calls.append(_path) or {"ledger_sha256": "sealed-ledger"})
    row = _row(tmp_path)
    context = {}
    validate_linguistic_source_choice_stage05_row(row, ("original_pipeline_txt", 10), ledger_context=context)
    validate_linguistic_source_choice_stage05_row(row, ("original_pipeline_txt", 10), ledger_context=context)
    assert len(calls) == 1
    for field, value in (("r1_span", [1, 18]), ("selected_raw_text_sha256", "0" * 64), ("ledger_identity", "stale")):
        altered = dict(row); altered[field] = value
        with pytest.raises(ReaderOccurrenceError):
            validate_linguistic_source_choice_stage05_row(altered, ("original_pipeline_txt", 10))
    duplicate = dict(row); duplicate["unexpected"] = True
    with pytest.raises(ReaderOccurrenceError):
        validate_linguistic_source_choice_stage05_row(duplicate, ("original_pipeline_txt", 10))
