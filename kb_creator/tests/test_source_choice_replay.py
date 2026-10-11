"""Focused fail-closed regressions for v2 raw-reader replay."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from kb_creator.pipeline import source_choice_translation as choices
from kb_creator.pipeline.identity import canonical_bytes, file_identity, sha256_bytes


def _row(view: str, raw: int, text: str) -> dict:
    return {"selectable": True, "alternative_id": f"{view}:{raw}", "source_locator": {"view": view, "raw_index": raw},
            "raw_text": text, "raw_text_sha256": sha256_bytes(text.encode()), "reader_text": "", "reader_text_sha256": ""}


def _replay(tmp_path: Path, *, duplicate: bool = False, stale_hash: bool = False) -> tuple[Path, Path, dict, list[dict]]:
    master = tmp_path / "master"; master.mkdir(); evidence = tmp_path / "evidence"; evidence.mkdir()
    markdown = "mid-19th"; decision = {"markdown": markdown, "selected_blocks": [{"view": "txt", "raw_index": 7, "purpose": "text"}], "semantic_structure": {"units": []}}
    decision_path = master / "evidence/review/page-001.json"; decision_path.parent.mkdir(parents=True); decision_path.write_text(json.dumps(decision), encoding="utf-8")
    raw = "mid-19<sup>th</sup>"; selected = {"kind": "selected", "unit": {"view_id": "txt", "raw_index": 7, "original_text_sha256": "0" * 64 if stale_hash else sha256_bytes(raw.encode())}, "markdown_span": [0, len(markdown)]}
    stream = [selected] + ([dict(selected)] if duplicate else [])
    audit_path = evidence / "stage05.json"; audit_path.write_text(json.dumps({"pages": [{"source_page": 1, "ordered_proof_stream": stream}]}), encoding="utf-8")
    binding = {"source_page": 1, "reader_anchor": {"kind": "ordered_selected_source_v1", "selected_source_key": {"view": "txt", "raw_index": 7}},
               "reader_projection": {"reader_text": markdown, "reader_text_sha256": sha256_bytes(markdown.encode())},
               "page_reader_span": {"character_start": 0, "character_end": len(markdown), "text_sha256": sha256_bytes(markdown.encode()), "decision_markdown_sha256": sha256_bytes(markdown.encode())},
               "decision": {"path": "evidence/review/page-001.json", **file_identity(decision_path)}, "stage05_audit": {"path": "stage05.json", **file_identity(audit_path)}}
    return master, evidence, binding, [_row("txt", 7, raw), _row("ocr", 7, markdown), _row("raster", 9, markdown)]


def test_raw_reader_replay_keeps_exact_anchor_singular_and_equivalents_plural(tmp_path):
    master, evidence, binding, alternatives = _replay(tmp_path)
    stage05_pages = {1: json.loads((evidence / "stage05.json").read_text())["pages"][0]}
    replay = choices._raw_reader_replay(master, binding, alternatives, stage05_pages=stage05_pages)
    assert replay["base_policy"] == "display_text_v1"
    assert replay["anchor_alternative_id"] == "txt:7"
    assert replay["selected_row_proof"]["source_locator"] == {"view": "txt", "raw_index": 7}
    assert [row["reader_text"] for row in alternatives] == ["mid-19th"] * 3


def test_stage05_authority_is_rooted_at_sealed_final_evidence_parent(tmp_path):
    authored = tmp_path / "book" / "nested" / "authored"; authored.mkdir(parents=True)
    audit = authored / "stage05.json"; audit.write_text(json.dumps({"pages": [{"source_page": 1, "ordered_proof_stream": []}]}), encoding="utf-8")
    final = authored / "review-draft-evidence.json"
    final.write_text(json.dumps({"authored": {"stage05_audit": {"path": "stage05.json", **file_identity(audit)}}}), encoding="utf-8")
    assert choices._stage05_pages(final, json.loads(final.read_text()))[1]["source_page"] == 1
    audit.write_text("{}", encoding="utf-8")
    with pytest.raises(choices.SourceChoiceError): choices._stage05_pages(final, json.loads(final.read_text()))


@pytest.mark.parametrize("duplicate", [True])
def test_raw_reader_replay_rejects_duplicate_selected_proof(tmp_path, duplicate):
    master, evidence, binding, alternatives = _replay(tmp_path, duplicate=duplicate)
    stage05_pages = {1: json.loads((evidence / "stage05.json").read_text())["pages"][0]}
    with pytest.raises(choices.SourceChoiceError):
        choices._raw_reader_replay(master, binding, alternatives, stage05_pages=stage05_pages)


@pytest.mark.parametrize("value", ["## wrong level", "> injected", "- injected", "| table |", "", "two\nlines"])
def test_atx_adapter_rejects_unsafe_containers_and_preserves_declared_quote(tmp_path, value):
    master = tmp_path / "master"; master.mkdir(); path = master / "evidence/review/page-001.json"; path.parent.mkdir(parents=True)
    markdown = "> # Stable"
    unit = {"id": "h", "kind": "heading", "representation": "atx_heading", "heading_level": 1,
            "markdown_span": {"start_line": 1, "end_line": 1, "sha256": sha256_bytes(markdown.encode())}}
    path.write_text(json.dumps({"markdown": markdown, "semantic_structure": {"units": [unit]}}), encoding="utf-8")
    binding = {"reader_anchor": {"kind": "semantic_unit_id", "semantic_unit_id": "h"}, "reader_projection": {"reader_text": markdown},
               "page_reader_span": {"character_start": 0, "character_end": len(markdown)}, "decision": {"path": "evidence/review/page-001.json", **file_identity(path)}}
    rows = [_row("txt", 1, value)]; rows[0]["reader_text"] = value
    with pytest.raises(choices.SourceChoiceError): choices._adapt_atx_heading_alternatives(master, binding, rows, base_policy="identity_v1")


@pytest.mark.parametrize("value,expected", [
    ("Alternative", "> # Alternative"),
    ("> # Alternative", "> # Alternative"),
    ("> #    Alternative", "> # Alternative"),
    (">\t#\t\tAlternative", "> # Alternative"),
])
def test_atx_adapter_preserves_level_one_and_quote_and_accepts_exact_wrapper(tmp_path, value, expected):
    master = tmp_path / "master"; master.mkdir(); path = master / "evidence/review/page-001.json"; path.parent.mkdir(parents=True)
    markdown = "> # Stable"; path.write_text(json.dumps({"markdown": markdown, "semantic_structure": {"units": [{"id": "h", "kind": "heading", "representation": "atx_heading", "heading_level": 1, "markdown_span": {"start_line": 1, "end_line": 1, "sha256": sha256_bytes(markdown.encode())}}]}}), encoding="utf-8")
    binding = {"reader_anchor": {"kind": "semantic_unit_id", "semantic_unit_id": "h"}, "reader_projection": {"reader_text": markdown}, "page_reader_span": {"character_start": 0, "character_end": len(markdown)}, "decision": {"path": "evidence/review/page-001.json", **file_identity(path)}}
    rows = [_row("txt", 1, value)]; rows[0]["reader_text"] = value
    choices._adapt_atx_heading_alternatives(master, binding, rows, base_policy="identity_v1")
    assert rows[0]["reader_text"] == expected and rows[0]["reader_adapter"]["base_policy"] == "identity_v1"
