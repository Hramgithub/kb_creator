"""The lexical producer uses the existing complete-paragraph proof contract."""
import copy

import pytest

from kb_creator.pipeline import semantic_structure, source_choice_successor
from kb_creator.scripts.author_reviewed_semantic_decisions import _derive_lexical_prose_bindings


KEY = ("original_pipeline_txt", 18)


def _case(monkeypatch, *, source="E D l T O R Jeff Moeller", replacement="EDITOR JEFF MOELLER",
          markdown="EDITOR JEFF MOELLER"):
    packet = {"views": {KEY[0]: {"blocks": [{"raw_index": KEY[1], "text": source}]}}}
    decision = {"selected_blocks": [{"view": KEY[0], "raw_index": KEY[1], "purpose": "text"}],
                "linguistic_source_choice_corrections": [{"view": KEY[0], "raw_index": KEY[1], "issue_id": "credits-editor"}],
                "markdown": markdown}
    pairs = [(source, replacement)]
    monkeypatch.setattr(semantic_structure, "reviewed_block_text_correction_candidates",
                        lambda *args: {KEY: pairs})
    monkeypatch.setattr(source_choice_successor, "linguistic_choice_corrections",
                        lambda *args: {KEY: pairs})
    return decision, packet, pairs


def test_lexical_successor_without_semantic_unit_gets_exact_prose_proof(monkeypatch):
    decision, packet, _ = _case(monkeypatch)
    assert _derive_lexical_prose_bindings(decision, packet, decision["markdown"], [], 4) == []
    binding = decision["reviewed_prose_bindings_v1"]
    assert len(binding) == 1
    assert binding[0]["markdown_span"]["start_line"] == 1
    assert binding[0]["markdown_span"]["end_line"] == 1
    assert _derive_lexical_prose_bindings(decision, packet, decision["markdown"], [], 4) == []
    assert decision["reviewed_prose_bindings_v1"] == binding


def test_noop_does_not_create_phantom_binding(monkeypatch):
    decision, packet, _ = _case(monkeypatch)
    monkeypatch.setattr(semantic_structure, "reviewed_block_text_correction_candidates", lambda *args: {})
    monkeypatch.setattr(source_choice_successor, "linguistic_choice_corrections", lambda *args: {})
    assert _derive_lexical_prose_bindings(decision, packet, decision["markdown"], [], 4) == []
    assert "reviewed_prose_bindings_v1" not in decision


@pytest.mark.parametrize("markdown,reason", [
    ("OTHER JEFF MOELLER", "found 0"),
    ("EDITOR JEFF MOELLER\n\nEDITOR JEFF MOELLER", "found 2"),
    ("<!-- EDITOR JEFF MOELLER -->", "HTML page context"),
    ("[EDITOR JEFF MOELLER](source)", "not supported prose"),
    ("```\nEDITOR JEFF MOELLER\n```", "found 0"),
    ("# EDITOR JEFF MOELLER", "not supported prose"),
])
def test_wrong_duplicate_or_hidden_reader_paragraph_blocks(monkeypatch, markdown, reason):
    decision, packet, _ = _case(monkeypatch, markdown=markdown)
    diagnostics = _derive_lexical_prose_bindings(decision, packet, markdown, [], 4)
    assert len(diagnostics) == 1 and reason in diagnostics[0]
    assert not decision.get("reviewed_prose_bindings_v1")


def test_mixed_visual_and_lexical_correction_requires_reviewed_owner(monkeypatch):
    decision, packet, pairs = _case(monkeypatch)
    monkeypatch.setattr(semantic_structure, "reviewed_block_text_correction_candidates",
                        lambda *args: {KEY: pairs + [("Jeff", "JEFF")]})
    diagnostics = _derive_lexical_prose_bindings(decision, packet, decision["markdown"], [], 4)
    assert "mixed visual/lexical" in diagnostics[0]
    assert not decision.get("reviewed_prose_bindings_v1")


def test_semantic_owner_and_unsupported_multiline_stay_on_existing_routes(monkeypatch):
    decision, packet, _ = _case(monkeypatch)
    unit = {"source_blocks": [{"view": KEY[0], "raw_index": KEY[1]}]}
    assert _derive_lexical_prose_bindings(decision, packet, decision["markdown"], [unit], 4) == []
    assert "reviewed_prose_bindings_v1" not in decision
    decision, packet, _ = _case(monkeypatch, source="E D l T O R\nJeff Moeller")
    assert "one complete nonempty paragraph" in _derive_lexical_prose_bindings(
        decision, packet, decision["markdown"], [], 4)[0]


def test_preflight_collects_every_unbound_lexical_key_on_a_page(monkeypatch):
    decision, packet, _ = _case(monkeypatch, markdown="no matching paragraph")
    second = (KEY[0], 19)
    packet["views"][KEY[0]]["blocks"].append({"raw_index": 19, "text": "Second\nsource"})
    decision["selected_blocks"].append({"view": KEY[0], "raw_index": 19, "purpose": "text"})
    decision["linguistic_source_choice_corrections"].append(
        {"view": KEY[0], "raw_index": 19, "issue_id": "credits-art"})
    pairs = {KEY: [("E D l T O R", "EDITOR")], second: [("Second", "NEW")]}
    monkeypatch.setattr(semantic_structure, "reviewed_block_text_correction_candidates",
                        lambda *args: pairs)
    monkeypatch.setattr(source_choice_successor, "linguistic_choice_corrections",
                        lambda *args: pairs)
    errors = _derive_lexical_prose_bindings(decision, packet, decision["markdown"], [], 4,
                                            collect_errors=True)
    assert len(errors) == 2
    assert "credits-editor" in errors[0] and "credits-art" in errors[1]


def test_explicit_binding_hash_and_span_are_reverified(monkeypatch):
    decision, packet, _ = _case(monkeypatch)
    _derive_lexical_prose_bindings(decision, packet, decision["markdown"], [], 4)
    stale = copy.deepcopy(decision)
    stale["reviewed_prose_bindings_v1"][0]["markdown_span"]["sha256"] = "0" * 64
    with pytest.raises(ValueError, match="span hash is stale"):
        _derive_lexical_prose_bindings(stale, packet, stale["markdown"], [], 4)
    stale = copy.deepcopy(decision)
    stale["reviewed_prose_bindings_v1"][0]["original_text_sha256"] = "0" * 64
    with pytest.raises(ValueError, match="source hash is stale"):
        _derive_lexical_prose_bindings(stale, packet, stale["markdown"], [], 4)
