"""Focused proof for sealed reviewed-block reader replay."""
from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path

import pytest

from kb_creator.pipeline import source_choice_translation as choices
from kb_creator.pipeline.identity import file_identity, sha256_bytes


def _write(path: Path, value: dict) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value), encoding="utf-8")
    return path


def _row(view: str, raw_index: int, text: str, packet: Path) -> dict:
    return {
        "selectable": True, "alternative_id": f"{view}:{raw_index}",
        "source_locator": {"view": view, "raw_index": raw_index},
        "raw_text": text, "raw_text_sha256": sha256_bytes(text.encode()),
        "reader_text": "", "reader_text_sha256": "",
        "evidence": {"packet": {"path": str(packet.resolve()), **file_identity(packet)}},
    }


def _fixture(tmp_path: Path, *, reverse_rows: bool = False) -> tuple[Path, dict, list[dict], dict[int, dict]]:
    raw = "Handout six has a threeword error - here."
    corrected = "Handout #6 has a three-word error – here."
    tmp_path.mkdir(parents=True, exist_ok=True)
    master = tmp_path / "master"; master.mkdir()
    decision = {
        "markdown": corrected,
        "selected_blocks": [{"view": "txt", "raw_index": 7, "purpose": "text"}],
        "semantic_structure": {"units": [{
            "id": "handout", "kind": "handout", "representation": "blockquote",
            "source_blocks": [{"view": "txt", "raw_index": 7}],
            "markdown_span": {"start_line": 1, "end_line": 1,
                              "sha256": sha256_bytes(corrected.encode())},
        }]},
        "reviewed_block_corrections": [
            {"view": "txt", "raw_index": 7, "before": "threeword", "after": "three-word",
             "reason": "source review", "original_text_sha256": sha256_bytes(raw.encode())},
            {"view": "txt", "raw_index": 7, "before": "Handout six", "after": "Handout #6",
             "reason": "source review", "original_text_sha256": sha256_bytes(raw.encode())},
            {"view": "txt", "raw_index": 7, "before": " - ", "after": " – ",
             "reason": "source review", "original_text_sha256": sha256_bytes(raw.encode())},
        ],
    }
    if reverse_rows:
        decision["reviewed_block_corrections"].reverse()
    decision_path = _write(master / "evidence/review/page-001.json", decision)
    packet = _write(tmp_path / "packet.json", {"views": {"txt": {"blocks": [
        {"raw_index": 7, "text": raw}, {"raw_index": 8, "text": raw},
    ]}}})
    selected = {"kind": "selected", "unit": {"view_id": "txt", "raw_index": 7,
        "original_text_sha256": sha256_bytes(raw.encode())}, "markdown_span": [0, len(corrected)]}
    audit_path = _write(tmp_path / "stage05.json", {"pages": [{"source_page": 1,
        "ordered_proof_stream": [selected]}]})
    binding = {
        "source_page": 1,
        "reader_anchor": {"kind": "ordered_selected_source_v1",
                          "selected_source_key": {"view": "txt", "raw_index": 7}},
        "reader_projection": {"reader_text": corrected,
                              "reader_text_sha256": sha256_bytes(corrected.encode())},
        "page_reader_span": {"character_start": 0, "character_end": len(corrected),
                             "text_sha256": sha256_bytes(corrected.encode()),
                             "decision_markdown_sha256": sha256_bytes(corrected.encode())},
        "decision": {"path": "evidence/review/page-001.json", **file_identity(decision_path)},
        "stage05_audit": {"path": "stage05.json", **file_identity(audit_path)},
    }
    return master, binding, [_row("txt", 7, raw, packet), _row("ocr", 8, raw, packet)], {1: json.loads(audit_path.read_text())["pages"][0]}


def test_corrected_reader_replay_is_source_ordered_and_does_not_leak_to_alternate(tmp_path):
    master, binding, alternatives, stage05 = _fixture(tmp_path, reverse_rows=True)
    replay = choices._raw_reader_replay(master, binding, alternatives, stage05_pages=stage05)

    assert replay["base_policy"] == "reviewed_block_correction_v1"
    assert replay["presentation_policy"] == "identity_v1"
    assert len(replay["correction_replay"]["correction_rows"]) == 3
    assert alternatives[0]["reader_text"] == "Handout #6 has a three-word error – here."
    assert alternatives[1]["reader_text"] == "Handout six has a threeword error - here."


@pytest.mark.parametrize("mutation", ["before", "after", "raw_hash", "asset", "span", "packet"])
def test_corrected_reader_replay_fails_closed_when_sealed_proof_drifts(tmp_path, mutation):
    master, binding, alternatives, stage05 = _fixture(tmp_path)
    decision_path = master / binding["decision"]["path"]
    decision = json.loads(decision_path.read_text())
    if mutation == "before":
        decision["reviewed_block_corrections"][0]["before"] = "absent"
    elif mutation == "after":
        decision["markdown"] = "wrong reader text"
    elif mutation == "raw_hash":
        decision["reviewed_block_corrections"][0]["original_text_sha256"] = "0" * 64
    elif mutation == "asset":
        decision["selected_blocks"][0]["purpose"] = "asset"
    elif mutation == "span":
        binding["page_reader_span"]["text_sha256"] = "0" * 64
    elif mutation == "packet":
        packet = Path(alternatives[0]["evidence"]["packet"]["path"])
        packet.write_text("{}", encoding="utf-8")
    if mutation not in {"span", "packet"}:
        decision_path.write_text(json.dumps(decision), encoding="utf-8")
        binding["decision"] = {"path": binding["decision"]["path"], **file_identity(decision_path)}
    with pytest.raises(choices.SourceChoiceError):
        choices._raw_reader_replay(master, binding, alternatives, stage05_pages=stage05)


def test_corrected_reader_replay_rejects_empty_preimage_and_duplicate_stage05_owner(tmp_path):
    master, binding, alternatives, stage05 = _fixture(tmp_path)
    binding["reader_projection"]["reader_text"] = ""
    binding["page_reader_span"]["character_end"] = 0
    with pytest.raises(choices.SourceChoiceError):
        choices._raw_reader_replay(master, binding, alternatives, stage05_pages=stage05)

    master, binding, alternatives, stage05 = _fixture(tmp_path / "duplicate")
    stage05[1]["ordered_proof_stream"].append(deepcopy(stage05[1]["ordered_proof_stream"][0]))
    with pytest.raises(choices.SourceChoiceError, match="absent or ambiguous"):
        choices._raw_reader_replay(master, binding, alternatives, stage05_pages=stage05)


@pytest.mark.parametrize("mutation", ["marker", "payload", "correction", "raw"])
def test_expanded_corrected_reader_retains_only_the_selected_anchor(tmp_path, mutation):
    master, binding, alternatives, stage05 = _fixture(tmp_path / mutation)
    raw = alternatives[0]["raw_text"]
    corrected = "Reviewed continuation with INT and the complete retained source paragraph."
    reader = "Reviewed continuation with **INT** and the complete retained source paragraph."
    decision_path = master / binding["decision"]["path"]
    decision = json.loads(decision_path.read_text(encoding="utf-8"))
    decision["markdown"] = reader
    decision["semantic_structure"]["units"][0]["markdown_span"]["sha256"] = sha256_bytes(reader.encode())
    decision["reviewed_block_corrections"] = [{
        "view": "txt", "raw_index": 7, "before": raw, "after": corrected,
        "reason": "sealed whole-block continuation", "original_text_sha256": sha256_bytes(raw.encode()),
    }]
    if mutation == "marker":
        decision["markdown"] = "Reviewed continuation with **INT and the complete retained source paragraph."
    elif mutation == "payload":
        decision["markdown"] = "Reviewed continuation with **INTX** and the complete retained source paragraph."
    elif mutation == "correction":
        decision["reviewed_block_corrections"][0]["after"] = "different corrected bytes"
    elif mutation == "raw":
        alternatives[0]["raw_text_sha256"] = "0" * 64
    decision_path.write_text(json.dumps(decision), encoding="utf-8")
    binding["decision"] = {"path": binding["decision"]["path"], **file_identity(decision_path)}
    binding["reader_projection"] = {"reader_text": reader, "reader_text_sha256": sha256_bytes(reader.encode())}
    binding["page_reader_span"] = {"character_start": 0, "character_end": len(reader),
                                   "text_sha256": sha256_bytes(reader.encode()),
                                   "decision_markdown_sha256": sha256_bytes(reader.encode())}
    stage05[1]["ordered_proof_stream"][0]["markdown_span"] = [0, len(reader)]
    if mutation != "marker" and mutation != "payload" and mutation != "correction" and mutation != "raw":
        raise AssertionError("unknown mutation")
    if mutation == "marker" or mutation == "payload" or mutation == "correction" or mutation == "raw":
        with pytest.raises(choices.SourceChoiceError):
            choices._raw_reader_replay(master, binding, alternatives, stage05_pages=stage05)


def test_expanded_corrected_reader_retains_selected_anchor(tmp_path):
    master, binding, alternatives, stage05 = _fixture(tmp_path)
    raw = alternatives[0]["raw_text"]
    corrected = "Reviewed continuation with INT and the complete retained source paragraph."
    reader = "Reviewed continuation with **INT** and the complete retained source paragraph."
    decision_path = master / binding["decision"]["path"]
    decision = json.loads(decision_path.read_text(encoding="utf-8"))
    decision["markdown"] = reader
    decision["semantic_structure"]["units"][0]["markdown_span"]["sha256"] = sha256_bytes(reader.encode())
    decision["reviewed_block_corrections"] = [{
        "view": "txt", "raw_index": 7, "before": raw, "after": corrected,
        "reason": "sealed whole-block continuation", "original_text_sha256": sha256_bytes(raw.encode()),
    }]
    decision_path.write_text(json.dumps(decision), encoding="utf-8")
    binding["decision"] = {"path": binding["decision"]["path"], **file_identity(decision_path)}
    binding["reader_projection"] = {"reader_text": reader, "reader_text_sha256": sha256_bytes(reader.encode())}
    binding["page_reader_span"] = {"character_start": 0, "character_end": len(reader),
                                   "text_sha256": sha256_bytes(reader.encode()),
                                   "decision_markdown_sha256": sha256_bytes(reader.encode())}
    stage05[1]["ordered_proof_stream"][0]["markdown_span"] = [0, len(reader)]
    replay = choices._raw_reader_replay(master, binding, alternatives, stage05_pages=stage05)
    assert replay["presentation_policy"] == "reviewed_block_correction_strong_display_v1"
    assert replay["presentation_proof"]["markers"]
    assert alternatives[0]["reader_text"] == reader
    assert alternatives[0]["reader_adapter"]["policy"] == "reviewed_corrected_reader_retention_v1"
    assert alternatives[1]["selectable"] is False
    assert alternatives[1]["nonselectable_reason"] == "requires_separate_reviewed_source_correction"


def test_real_fresh_v2_queue_preserves_two_disjoint_reader_spans(tmp_path, monkeypatch):
    """Exercise the real queue/verification route for paired reader spans."""
    from kb_creator.tests.test_source_choice_composite_integration import _prepare_composite_queue

    built, queue_path, _first, _alternate = _prepare_composite_queue(
        tmp_path, monkeypatch, multichoice=True,
    )
    verified = choices.verify_queue_v2(queue_path)
    queue = json.loads(queue_path.read_text(encoding="utf-8"))
    ordered = sorted(queue["choices"], key=lambda row:
                     row["raw_reader_replay"]["raw_source_slice"]["raw_character_start"])

    assert verified["choices"] == 2
    assert len({row["issue_id"] for row in ordered}) == 2
    assert [row["raw_reader_replay"]["anchor_source_locator"] for row in ordered] == [{
        "view": "raster_pipeline_ocr", "raw_index": built["raws"]["selected_raster_container"],
        "field": "text",
    }] * 2
    intervals = [row["raw_reader_replay"]["raw_source_slice"] for row in ordered]
    assert intervals[0]["raw_character_end"] <= intervals[1]["raw_character_start"]
