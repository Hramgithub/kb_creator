"""Source-scale and accepted-label rules for derived DOCX projections."""

from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path

import pytest

from kb_creator.pipeline.edition_projection import (
    EditionProjectionError,
    expected_characteristic,
    validate_edition_rows,
    validate_terminology_rows,
)
from kb_creator.pipeline.coc_glossary import HEADER
from kb_creator.pipeline.identity import file_identity


SHA = "A" * 64


def _selector(before: str, after: str, *, before_value: str, after_value: str) -> dict:
    start_before = before.index(before_value)
    start_after = after.index(after_value)
    digest = lambda text: hashlib.sha256(text.encode("utf-8")).hexdigest().upper()
    return {"html_anchor": "field-1", "part": "word/document.xml", "paragraph": 0,
            "table": 0, "cell": 0, "before_text": before, "after_text": after,
            "before_sha256": digest(before), "after_sha256": digest(after),
            "before_start": start_before, "before_end": start_before + len(before_value),
            "after_start": start_after, "after_end": start_after + len(after_value)}


def _row(**changes):
    row = {
        "occurrence_id": "story.card.STR", "book_id": "test-book", "story_id": "story",
        "entity_id": "entity", "source_page": 1, "source_pdf_sha256": SHA,
        "source_edition": "legacy_proven", "present_scale": "legacy",
        "entity_kind": "human_npc", "field": "STR", "before": 13, "after": 65,
        "action": "convert_deterministic", "rule_id": "coc7-characteristic-v1",
        "decision_reference": "review:1",
    }
    row.update(changes)
    row["selector"] = changes.get("selector", _selector(f"{row['field']} {row['before']}",
                                                    f"{row['field']} {row['after']}",
                                                    before_value=str(row["before"]),
                                                    after_value=str(row["after"])))
    return row


def _edition_args(row: dict) -> dict:
    return {"source_pdf_sha256": SHA,
            "source_pages": [{"page": 1, "render": {"sha256": SHA}}],
            "section_domain": ["story"], "book_id": "test-book",
            "reviewed_domain": [{"occurrence_id": "story.card.STR", "book_id": "test-book",
                "story_id": "story", "entity_id": "entity", "source_page": 1,
                "field": row["field"], "source_render_sha256": SHA,
                "decision_reference": "review:1"}]}


def test_source_bound_characteristics_and_edu_exception():
    assert expected_characteristic("STR", 13, source_edition="legacy_proven", present_scale="legacy", entity_kind="human_npc") == 65
    assert expected_characteristic("STR", 100, source_edition="legacy_proven", present_scale="legacy", entity_kind="deity") == 500
    assert expected_characteristic("EDU", 19, source_edition="legacy_proven", present_scale="legacy", entity_kind="human_npc") == 91
    assert expected_characteristic("EDU", 27, source_edition="legacy_proven", present_scale="legacy", entity_kind="human_npc") == 99
    assert expected_characteristic("STR", 5, source_edition="7e", present_scale="7e", entity_kind="deity") == 5
    assert expected_characteristic("SIZ", 630, source_edition="7e", present_scale="7e", entity_kind="deity") == 630
    assert expected_characteristic("STR", 13, source_edition="unknown", present_scale="legacy", entity_kind="human_npc") is None
    assert expected_characteristic("Luck", 75, source_edition="legacy_proven", present_scale="legacy", entity_kind="human_npc") is None
    assert expected_characteristic("skill", 70, source_edition="legacy_proven", present_scale="legacy", entity_kind="pregen_investigator") is None


def test_approved_conversion_keep_and_explicit_exception():
    for row in (_row(), _row(source_edition="7e", present_scale="7e", before=5, after=5, action="keep_7e"),
                _row(field="Luck", before=75, after=75, action="keep_editorial_exception")):
        assert validate_edition_rows([row], **_edition_args(row))


@pytest.mark.parametrize("change", [
    {"source_edition": "unknown"},
    {"field": "Luck", "before": 75, "after": 375},
    {"field": "skill", "before": 70, "after": 350},
    {"after": 13},
    {"source_pdf_sha256": "B" * 64},
    {"action": "review_required"},
])
def test_unproved_or_incorrect_projection_fails(change):
    with pytest.raises(EditionProjectionError):
        row = _row(**change)
        validate_edition_rows([row], **_edition_args(row))


@pytest.mark.parametrize("row,domain_change", [
    (_row(selector=_selector("STR 13", "STR 115", before_value="3", after_value="15"), before=3, after=15), {}),
    (_row(selector=_selector("Luck 13", "Luck 65", before_value="13", after_value="65")), {}),
    (_row(source_page=9999), {}),
    (_row(story_id="absent-story"), {}),
    (_row(book_id="foreign-book"), {}),
    (_row(entity_id="foreign-entity"), {}),
    (_row(occurrence_id="foreign-occurrence"), {}),
    (_row(), {"source_render_sha256": "B" * 64}),
])
def test_numeric_field_and_reviewed_domain_misbinding_fails(row, domain_change):
    args = _edition_args(row)
    args["reviewed_domain"][0].update(domain_change)
    with pytest.raises(EditionProjectionError):
        validate_edition_rows([row], **args)


def _term(oid, source, target, percentage, **changes):
    row = {"occurrence_id": oid, "entity_id": "entity", "source_label": source,
           "source_context": "general", "target_label": target,
           "percentage": percentage, "registry_sha256": SHA, "overlay_sha256": SHA,
           "disposition": "accepted_direct_mapping", "authority_reference": f"overlay:{source}",
           "collision_decision": None,
           "selector": _selector(source, target, before_value=source, after_value=target)}
    row.update(changes)
    return row


def _authorities(tmp_path: Path) -> dict:
    registry = tmp_path / "registry.csv"
    registry.write_text(",".join(HEADER) + "\n", encoding="utf-8")
    overlay = tmp_path / "overlay.json"
    overlay.write_text(json.dumps({"terms": [{"source": "Know", "target": "Знание"},
                                             {"source": "Idea", "target": "Знание"}]},
                                  ensure_ascii=False), encoding="utf-8")
    return {"registry_path": registry, "overlay_path": overlay,
            "registry_sha256": file_identity(registry)["sha256"],
            "overlay_sha256": file_identity(overlay)["sha256"], "book_id": "test-book"}


def test_contextual_many_to_one_label_collision_requires_exact_decision(tmp_path: Path):
    authority = _authorities(tmp_path)
    rows = [_term("a", "Know", "Знание", 70), _term("b", "Idea", "Знание", 55)]
    for row in rows:
        row["registry_sha256"] = authority["registry_sha256"]
        row["overlay_sha256"] = authority["overlay_sha256"]
    with pytest.raises(EditionProjectionError, match="collision"):
        validate_terminology_rows(rows, **authority)
    closed = copy.deepcopy(rows)
    for row in closed:
        row["collision_decision"] = "review:collision-1"
    assert validate_terminology_rows(closed, **authority)
    closed[0]["disposition"] = "review_required"
    with pytest.raises(EditionProjectionError):
        validate_terminology_rows(closed, **authority)


@pytest.mark.parametrize("target,reference,disposition", [
    ("Выдуманный навык", "overlay:Know", "accepted_direct_mapping"),
    ("Знание", "glossary:1", "accepted_direct_mapping"),
    ("Знание", "overlay:Know", "accepted_primary_rule_mapping"),
    ("Знание", "overlay:Know", "keep_editorial_exception"),
])
def test_terminology_requires_resolved_authority(tmp_path: Path, target, reference, disposition):
    authority = _authorities(tmp_path)
    row = _term("a", "Know", target, 70, authority_reference=reference,
                disposition=disposition, registry_sha256=authority["registry_sha256"],
                overlay_sha256=authority["overlay_sha256"])
    with pytest.raises(EditionProjectionError):
        validate_terminology_rows([row], **authority)


def test_accepted_registry_row_binds_label_and_review_required_does_not(tmp_path: Path):
    authority = _authorities(tmp_path)
    authority["overlay_path"].write_text('{"terms":[]}', encoding="utf-8")
    registry = authority["registry_path"]
    registry.write_text(",".join(HEADER) + "\nKnow,Знание,,,general,accepted,test-book,review:1,fixture\n",
                        encoding="utf-8")
    authority["registry_sha256"] = file_identity(registry)["sha256"]
    authority["overlay_sha256"] = file_identity(authority["overlay_path"])["sha256"]
    row = _term("a", "Know", "Знание", 70, authority_reference="registry:Know",
                registry_sha256=authority["registry_sha256"],
                overlay_sha256=authority["overlay_sha256"])
    assert validate_terminology_rows([row], **authority)
    registry.write_text(",".join(HEADER) + "\nKnow,Знание,,,general,review_required,test-book,review:1,fixture\n",
                        encoding="utf-8")
    authority["overlay_path"].write_text('{"terms":[{"source":"Idea","target":"Идея"}]}',
                                          encoding="utf-8")
    authority["registry_sha256"] = file_identity(registry)["sha256"]
    authority["overlay_sha256"] = file_identity(authority["overlay_path"])["sha256"]
    row["registry_sha256"] = authority["registry_sha256"]
    row["overlay_sha256"] = authority["overlay_sha256"]
    with pytest.raises(EditionProjectionError, match="no accepted registry row"):
        validate_terminology_rows([row], **authority)
