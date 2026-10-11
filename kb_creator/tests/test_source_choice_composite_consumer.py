"""Consumer regressions at the already-verified linguistic ledger boundary."""
import json

import pytest

from kb_creator.pipeline import source_choice_successor as consumer
from kb_creator.pipeline.identity import file_identity, sha256_bytes
from kb_creator.pipeline.semantic_structure import (
    SemanticStructureError, reviewed_block_text_correction_candidates,
)


def _sha(text):
    return sha256_bytes(text.encode())


def _decision(tmp_path, monkeypatch, *, overlap=False, stale=False, direct=False):
    # Equal substrings have different sealed positions, and both change length.
    text = "prefix 1D6 middle 1D6 suffix"
    key = ("raster", 7)
    anchor = {"selected_source_key": {"view": key[0], "raw_index": key[1]}}
    source_locator = {**anchor["selected_source_key"], "field": "text"}
    intervals = [(7, 10, "2D6-long"), (7 if overlap else 18, 10 if overlap else 21, "D8")]
    queue_rows, ledger_rows, decision_rows = [], [], []
    for number, (start, end, replacement) in enumerate(intervals):
        issue_id = f"choice-{number}"
        alternative_id = f"ocr-{number}"
        chosen_locator = {"view": "ocr", "raw_index": number, "field": "text"}
        span = {"character_start": start, "character_end": end, "text_sha256": _sha(text[start:end])}
        replay = {"anchor_mode": "composite_source_slice_v1", "anchor_source_locator": source_locator,
                  "anchor_container_sha256": _sha("stale" if stale else text),
                  "raw_source_slice": {"raw_character_start": start, "raw_character_end": end,
                                       "raw_text_sha256": _sha(text[start:end])}}
        if direct and number == 1:
            replay = {"anchor_mode": "direct"}
        queue_rows.append({"issue_id": issue_id, "source_page": 1, "alternatives": [{
            "alternative_id": alternative_id, "raw_text": replacement,
            "raw_text_sha256": _sha(replacement), "source_locator": chosen_locator}]})
        ledger_rows.append({"issue_id": issue_id, "reader_anchor": anchor,
            "r0_reader_span": span, "intended_reader_successor": {"text_sha256": _sha(replacement)},
            "chosen_raw_alternative": {"text_sha256": _sha(replacement), "source_locator": chosen_locator},
            "raw_reader_replay": replay})
        decision_rows.append({"authority": consumer.AUTHORITY, "issue_id": issue_id,
            "alternative_id": alternative_id, "view": key[0], "raw_index": key[1],
            "raw_text_sha256": _sha(text), "selected_raw_text_sha256": _sha(replacement),
            "page_reader_span": span, "reader_anchor": anchor,
            "reader_preimage": text[start:end], "reader_replacement": replacement})
    queue = tmp_path / "SOURCE_CHOICE_QUEUE.v2.json"
    ledger = tmp_path / "SOURCE_CHOICE_LEDGER.v2.json"
    queue.write_text(json.dumps({"choices": queue_rows}), encoding="utf-8")
    ledger.write_text(json.dumps({"queue": {"path": str(queue)}, "source_choices": ledger_rows}), encoding="utf-8")
    for row in decision_rows:
        row["ledger"] = {"path": str(ledger), **file_identity(ledger)}
    # Integration tests exercise fresh verification; here isolate consumption
    # after that boundary while still reopening the real sealed ledger bytes.
    monkeypatch.setattr(consumer, "verify_ledger_v2", lambda path: {"state": "verified"})
    return {"linguistic_source_choice_corrections": decision_rows}, {key: {"text": text}}, {key}, text


@pytest.mark.parametrize("reverse", [False, True])
def test_consumer_applies_two_sealed_equal_slices_and_preserves_surroundings(tmp_path, monkeypatch, reverse):
    decision, blocks, selected, text = _decision(tmp_path, monkeypatch)
    if reverse:
        decision["linguistic_source_choice_corrections"].reverse()
    result = reviewed_block_text_correction_candidates(decision, blocks, selected, 1)
    assert result == {("raster", 7): [(text, "prefix 2D6-long middle D8 suffix")]}


@pytest.mark.parametrize("fault", ["overlap", "stale"])
def test_consumer_rejects_conflicting_or_stale_slices(tmp_path, monkeypatch, fault):
    decision, blocks, selected, _ = _decision(tmp_path, monkeypatch, **{fault: True})
    with pytest.raises(consumer.SourceChoiceSuccessorError, match="composite source intervals"):
        consumer.linguistic_choice_corrections(decision, blocks, selected, 1)


def test_semantic_consumer_rejects_mixed_substring_and_composite_corrections(tmp_path, monkeypatch):
    decision, blocks, selected, _ = _decision(tmp_path, monkeypatch, direct=True)
    with pytest.raises(SemanticStructureError, match="not exact|overlapping"):
        reviewed_block_text_correction_candidates(decision, blocks, selected, 1)
