"""Exact container projection boundaries; public authority routes are separate."""
from copy import deepcopy
import json

import pytest

from kb_creator.pipeline.identity import canonical_bytes, file_identity, sha256_bytes
from kb_creator.pipeline.semantic_structure import _normalized
from kb_creator.pipeline.source_choice_container_proof import derive_container_proof
from kb_creator.pipeline.reader_occurrence_projection import (
    ReaderOccurrenceError, validate_linguistic_source_choice_stage05_row, _ordered_envelope,
)


def _sha(s):
    return sha256_bytes(s.encode())


def _write(p, value):
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(value), encoding="utf-8")
    return {"path": str(p), **file_identity(p)}


def _fixture(tmp_path, *, adjacent=False, repeated=False):
    middle = "" if adjacent else " / "
    container = "(" + "AA" + middle + ("AA" if repeated else "BB") + "!)"
    markdown = "Lead\n\n" + container + "\n\nEnd"
    start = 6
    key = ("raster_pipeline_ocr", 33)
    unit = {"view_id": key[0], "raw_index": key[1], "source_page": 1,
            "original_text_sha256": _sha(container)}
    selected = {"kind": "selected", "unit": unit,
                "markdown_span": [4, 4 + len(_normalized(container))]}
    decision_record = _write(tmp_path / "r0/evidence/page.json", {"source_page": 1, "markdown": markdown,
        "semantic_structure": {"units": [{"id": "composite", "markdown_span": {
            "start_line": 3, "end_line": 3, "sha256": _sha(container)}}]}})
    decision_record["path"] = "evidence/page.json"
    audit = _write(tmp_path / "author/audit.json", {"pages": [{"source_page": 1,
                                                           "ordered_proof_stream": [selected]}]})
    audit["path"] = "audit.json"
    evidence = _write(tmp_path / "author/evidence.json", {"authored": {"stage05_audit": audit}})
    def span(a, b):
        return {"character_start": a, "character_end": b, "byte_start": a, "byte_end": b,
                "text_sha256": _sha(markdown[a:b]), "decision_markdown_sha256": _sha(markdown)}
    choices = [{"issue_id": "outside", "disposition": "selected_alternative", "r0_reader_span": span(0, 4),
                "raw_reader_replay": {"decision": decision_record, "anchor_source_locator": {"view": "original_pipeline_txt", "raw_index": 1, "field": "text"}},
                "intended_reader_successor": {"text": "Leading outside", "text_sha256": _sha("Leading outside")}}]
    for n, (a, b, after) in enumerate(((1, 3, "alpha\nlong"), (3 + len(middle), 5 + len(middle), "C"))):
        replay = {"anchor_mode": "composite_source_slice_v1", "decision": decision_record,
                  "anchor_source_locator": {"view": key[0], "raw_index": key[1], "field": "text"},
                  "anchor_container_sha256": _sha(container), "semantic_unit_id": "composite",
                  "selected_row_proof": {"row_sha256": sha256_bytes(canonical_bytes(selected))},
                  "raw_source_slice": {"raw_character_start": a, "raw_character_end": b,
                                       "raw_text_sha256": _sha(container[a:b])}}
        choices.append({"issue_id": f"choice-{n}", "alternative_id": f"ocr-{n}", "disposition": "selected_alternative",
                        "raw_reader_replay": replay, "r0_reader_span": span(start + a, start + b),
                        "intended_reader_successor": {"text": after, "text_sha256": _sha(after)},
                        "chosen_raw_alternative": {"source_locator": {"view": "original_pipeline_ocr", "raw_index": n, "field": "text"},
                                                   "text_sha256": _sha(after)}})
    queue = _write(tmp_path / "queue.json", {"review_master": {"path": str(tmp_path / "r0/MASTER_EN.md")},
        "final_evidence": evidence, "choices": [{"issue_id": r["issue_id"], "source_page": 1} for r in choices]})
    ledger = {"queue": queue, "source_choices": choices}
    record = _write(tmp_path / "ledger.json", ledger)
    verified = {"queue": queue["path"], "ledger_sha256": "test-verified-ledger"}
    args = dict(ledger_record=record, ledger=ledger, verified=verified, page=1, key=key)
    current = "Leading outside\n\n(alpha\nlong" + middle + "C!)\n\nEnd"
    return args, current, key


@pytest.mark.parametrize("adjacent", [False, True])
def test_two_choices_preserve_punctuation_and_preceding_page_delta(tmp_path, adjacent):
    args, current, key = _fixture(tmp_path, adjacent=adjacent)
    row = derive_container_proof(**args, current_markdown=current)
    assert row["r1_container"]["text"] == "(alpha\nlong" + ("" if adjacent else " / ") + "C!)"
    assert row["r0_container"]["page_character_span"]["character_start"] == 6
    assert row["r1_container"]["page_character_span"]["character_start"] == len("Leading outside\n\n")
    assert row["markdown_span"][0] == len(_normalized("Leading outside"))
    reverse = deepcopy(args)
    reverse["ledger"]["source_choices"].reverse()
    assert derive_container_proof(**reverse, current_markdown=current) == row


def test_two_witnesses_shift_after_earlier_structural_marker(tmp_path):
    args, lexical, key = _fixture(tmp_path)
    baseline = derive_container_proof(**args, current_markdown=lexical)
    before = "Leading outside"
    after = "- " + before
    patch = {"source_occurrences": [{"view": "original_pipeline_txt", "raw_index": key[1],
                                     "source_text_sha256": _sha(before)}],
             "before": before, "before_sha256": _sha(before),
             "after": after, "after_sha256": _sha(after), "count": 1}
    context = {"pages": {1: [patch]}, "predecessor_pages": {1: {"markdown": lexical}},
               "authority": {"input": {"path": "synthetic", "bytes": 1, "sha256": "A" * 64},
                             "binding_root": "synthetic"}}
    projected = derive_container_proof(**args, current_markdown="- " + lexical,
                                       structural_context=context)
    assert projected["r1_container"] == baseline["r1_container"]
    assert projected["diagnostic_witnesses"] == baseline["diagnostic_witnesses"]
    assert projected["structural_projection"]["current_container"]["page_character_span"]["character_start"] == (
        baseline["r1_container"]["page_character_span"]["character_start"] + 2)
    assert [row["span"]["character_start"] for row in projected["structural_projection"]["current_witness_spans"]] == [
        witness["r1_reader_span"]["character_start"] + 2 for witness in baseline["diagnostic_witnesses"]]


def test_container_and_witnesses_follow_explicit_whole_page_permutation(tmp_path):
    args, lexical, key = _fixture(tmp_path)
    baseline = derive_container_proof(**args, current_markdown=lexical)
    span = baseline["r1_container"]["page_character_span"]
    start, end = span["character_start"], span["character_end"]
    current = lexical[start:end] + lexical[:start] + lexical[end:]
    container_key = {"view": key[0], "raw_index": key[1]}
    outside_key = {"view": "original_pipeline_txt", "raw_index": 1}
    occurrences = [{**container_key, "source_text_sha256": _sha(lexical[start:end])},
                   {**outside_key, "source_text_sha256": _sha(lexical[:start])}]
    def copied(low, high, source_key):
        return {"kind": "copy", "start": low, "end": high, "sha256": _sha(lexical[low:high]),
                "source_occurrences": [source_key]}
    patch = {"source_occurrences": occurrences, "before": lexical, "before_sha256": _sha(lexical),
             "after": current, "after_sha256": _sha(current), "count": 1,
             "interval_map": {"segments": [copied(start, end, container_key),
                                           copied(0, start, outside_key),
                                           copied(end, len(lexical), outside_key)],
                              "removed_intervals": []}}
    context = {"pages": {1: [patch]}, "predecessor_pages": {1: {"markdown": lexical}},
               "authority": {"input": {"path": "synthetic", "bytes": 1, "sha256": "A" * 64},
                             "binding_root": "synthetic"}}
    projected = derive_container_proof(**args, current_markdown=current, structural_context=context)
    assert projected["r1_container"] == baseline["r1_container"]
    assert projected["diagnostic_witnesses"] == baseline["diagnostic_witnesses"]
    assert projected["structural_projection"]["current_container"]["page_character_span"]["character_start"] == 0
    assert [row["span"]["character_start"] for row in projected["structural_projection"]["current_witness_spans"]] == [
        witness["r1_reader_span"]["character_start"] - start for witness in baseline["diagnostic_witnesses"]]


@pytest.mark.parametrize("mutation", ["missing", "extra", "duplicate", "order", "locator", "r0_span", "r1_span", "unit", "r0_row", "seal", "unknown"])
def test_consumer_rejects_resealed_container_substitutions(tmp_path, monkeypatch, mutation):
    args, current, key = _fixture(tmp_path)
    row = derive_container_proof(**args, current_markdown=current)
    from kb_creator.pipeline import source_choice_translation
    monkeypatch.setattr(source_choice_translation, "verify_ledger_v2", lambda _path: args["verified"])
    validate_linguistic_source_choice_stage05_row(row, key)
    altered = deepcopy(row); ws = altered["diagnostic_witnesses"]
    if mutation == "missing": ws.pop()
    elif mutation in {"extra", "duplicate"}: ws.append(deepcopy(ws[0])); ws[-1]["issue_id"] = "unknown" if mutation == "extra" else ws[0]["issue_id"]
    elif mutation == "order": ws.reverse()
    elif mutation == "locator": ws[0]["selected_raw_locator"] = deepcopy(ws[1]["selected_raw_locator"])
    elif mutation == "r0_span": altered["r0_container"]["page_character_span"]["character_start"] += 1
    elif mutation == "r1_span": altered["r1_container"]["page_character_span"]["character_end"] += 1
    elif mutation == "unit": altered["unit"]["original_text_sha256"] = "0" * 64
    elif mutation == "r0_row": altered["r0_container"]["selected_row_sha256"] = "0" * 64
    elif mutation == "unknown": ws[0]["surprise"] = True
    altered["row_sha256"] = sha256_bytes(canonical_bytes({k: v for k, v in altered.items() if k != "row_sha256"}))
    if mutation == "seal": altered["row_sha256"] = "0" * 64
    with pytest.raises(ReaderOccurrenceError):
        validate_linguistic_source_choice_stage05_row(altered, key)


def test_exact_envelope_compares_current_page_punctuation(tmp_path, monkeypatch):
    args, current, key = _fixture(tmp_path)
    row = derive_container_proof(**args, current_markdown=current)
    from kb_creator.pipeline import source_choice_translation
    monkeypatch.setattr(source_choice_translation, "verify_ledger_v2", lambda _path: args["verified"])
    issue = {"candidate_span": {"binding": "ordered_selected_source_v1", "source_key": {"view": key[0], "raw_index": key[1]}}}
    start, end, _, _ = _ordered_envelope(issue, {"markdown": current}, {"ordered_proof_stream": [row]})
    assert current[start:end] == row["r1_container"]["text"]
    with pytest.raises(ReaderOccurrenceError):
        _ordered_envelope(issue, {"markdown": current.replace("!)", "?)")}, {"ordered_proof_stream": [row]})


@pytest.mark.parametrize("case", ["raw_span", "selected_row", "page_hash", "current_page"])
def test_derivation_rejects_stale_source_or_current_authority(tmp_path, case):
    args, current, _ = _fixture(tmp_path)
    if case == "raw_span": args["ledger"]["source_choices"][2]["raw_reader_replay"]["raw_source_slice"]["raw_character_start"] = 2
    elif case == "selected_row": args["ledger"]["source_choices"][1]["raw_reader_replay"]["selected_row_proof"]["row_sha256"] = "0" * 64
    elif case == "page_hash": args["ledger"]["source_choices"][0]["r0_reader_span"]["decision_markdown_sha256"] = "0" * 64
    else: current += "!"
    with pytest.raises(ValueError):
        derive_container_proof(**args, current_markdown=current)


@pytest.mark.parametrize("excerpt,expected", [("AA", "alpha\nlong"), (" / ", " / "),
                                             ("(AA / BB!)", "(alpha\nlong / C!)")])
def test_retained_question_uses_exact_witness_or_unchanged_container(tmp_path, monkeypatch, excerpt, expected):
    from kb_creator.pipeline import source_choice_translation
    from kb_creator.pipeline.reader_occurrence_projection import resolve_issue_reader_occurrence
    args, current, key = _fixture(tmp_path)
    row = derive_container_proof(**args)
    monkeypatch.setattr(source_choice_translation, "verify_ledger_v2", lambda _path: args["verified"])
    issue = {"source_page": 1, "source_excerpt_en": excerpt, "source_excerpt_sha256": _sha(excerpt),
             "candidate_span": {"binding": "ordered_selected_source_v1", "source_key": {"view": key[0], "raw_index": key[1]}}}
    result = resolve_issue_reader_occurrence(issue, {"source_page": 1, "markdown": current},
                                            {"ordered_proof_stream": [row]}, "\n" + current + "\n")
    assert result["reader_projection"]["reader_text"] == expected
    start, end = (result["page_reader_span"][k] for k in ("character_start", "character_end"))
    assert current[start:end] == expected


def test_retained_equal_preimages_do_not_choose_first_witness(tmp_path, monkeypatch):
    from kb_creator.pipeline import source_choice_translation
    from kb_creator.pipeline.reader_occurrence_projection import resolve_issue_reader_occurrence
    args, current, key = _fixture(tmp_path, repeated=True)
    row = derive_container_proof(**args)
    monkeypatch.setattr(source_choice_translation, "verify_ledger_v2", lambda _path: args["verified"])
    issue = {"source_page": 1, "source_excerpt_en": "AA", "source_excerpt_sha256": _sha("AA"),
             "candidate_span": {"binding": "ordered_selected_source_v1", "source_key": {"view": key[0], "raw_index": key[1]}}}
    with pytest.raises(ReaderOccurrenceError, match="ambiguous across container witnesses"):
        resolve_issue_reader_occurrence(issue, {"source_page": 1, "markdown": current},
                                       {"ordered_proof_stream": [row]}, "\n" + current + "\n")


def test_multiple_direct_rows_do_not_inherit_last_choice_values(tmp_path, monkeypatch):
    from kb_creator.pipeline import source_choice_translation
    from kb_creator.scripts.audit_mineru_ai_merge_fidelity import _linguistic_source_choice_proofs
    ledger = {"source_choices": []}; mappings = []; corrections = []
    for index in range(2):
        text = "replacement " + str(index)
        anchor = {"view": "original_pipeline_txt", "raw_index": index, "field": "text"}
        choice = {"issue_id": f"choice-{index}", "alternative_id": f"alt-{index}", "disposition": "selected_alternative",
                  "r0_reader_span": {"start": index}, "reader_anchor": {"key": index},
                  "raw_reader_replay": {"anchor_source_locator": anchor, "r0_preimage_sha256": _sha(str(index))},
                  "chosen_raw_alternative": {"source_locator": anchor, "text_sha256": _sha(text)},
                  "intended_reader_successor": {"text": text, "text_sha256": _sha(text)}}
        ledger["source_choices"].append(choice)
        mappings.append({"kind": "selected", "unit": {"view_id": anchor["view"], "raw_index": index}, "markdown_span": [index * 10, index * 10 + 10]})
        corrections.append({"authority": "linguistic_source_choice", "ledger": None, "issue_id": choice["issue_id"],
                            "alternative_id": choice["alternative_id"], "view": anchor["view"], "raw_index": index,
                            "raw_text_sha256": _sha(str(index)), "page_reader_span": choice["r0_reader_span"],
                            "reader_anchor": choice["reader_anchor"], "reader_preimage": str(index),
                            "reader_replacement": text, "selected_raw_text_sha256": _sha(text)})
    record = _write(tmp_path / "direct-ledger.json", ledger)
    for c in corrections: c["ledger"] = record
    monkeypatch.setattr(source_choice_translation, "verify_ledger_v2", lambda _path: {"ledger_sha256": "verified"})
    result = _linguistic_source_choice_proofs(1, {"linguistic_source_choice_corrections": corrections}, mappings)
    assert [r["r1_text"] for r in result] == ["replacement 0", "replacement 1"]
    assert [r["selected_raw_locator"]["raw_index"] for r in result] == [0, 1]
    with pytest.raises(ValueError, match="duplicated"):
        _linguistic_source_choice_proofs(1, {"linguistic_source_choice_corrections": corrections + [corrections[0]]}, mappings)


def test_container_cache_rejects_changed_ledger_at_same_path(tmp_path, monkeypatch):
    from kb_creator.pipeline import source_choice_translation
    from pathlib import Path
    args, _, key = _fixture(tmp_path)
    row = derive_container_proof(**args)
    monkeypatch.setattr(source_choice_translation, "verify_ledger_v2", lambda _path: args["verified"])
    context = {}
    validate_linguistic_source_choice_stage05_row(row, key, ledger_context=context)
    changed = deepcopy(args["ledger"]); changed["source_choices"][1]["alternative_id"] = "substituted"
    row["ledger"] = _write(Path(row["ledger"]["path"]), changed)
    row["row_sha256"] = sha256_bytes(canonical_bytes({k: v for k, v in row.items() if k != "row_sha256"}))
    with pytest.raises(ReaderOccurrenceError, match="cached ledger"):
        validate_linguistic_source_choice_stage05_row(row, key, ledger_context=context)
