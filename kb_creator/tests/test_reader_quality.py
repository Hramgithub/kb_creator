import copy

import pytest

from kb_creator.pipeline.reader_quality import amend_proofread_submission, scan_reader_units, text_sha


def sample():
    row = {"unit_id": "u1", "source_hash": "EN", "draft_ru_sha256": text_sha("Черновик"),
           "final_ru_text": "П Е Р С О Н А Ж И", "disposition": "changed", "reason": "prior", "unresolved": []}
    task = {"units": [{k: row[k] for k in ("unit_id", "source_hash", "draft_ru_sha256")}]}
    submission = {"schema": "kb_creator.five_step_language_proofread_submission.v2", "units": [row]}
    change = {"unit_id": "u1", "expected_final_ru_sha256": text_sha(row["final_ru_text"]),
              "final_ru_text": "Персонажи", "reason": "Reviewed word boundaries"}
    return task, submission, change


def test_scan_does_not_invent_letter_spacing_in_normal_headings():
    rows = [{"unit_id": str(i), "ru_text": text} for i, text in enumerate([
        "## СЦЕНА 2: ИССЛЕДОВАНИЯ И СВЯЗИ", "## ГДЕ ОСТАНОВИТЬСЯ В НЬЮ-ЙОРКЕ",
        "# П Е Р С О Н А Ж И   Х Р А Н И Т Е Л Я", "<!-- source-page-001 -->"])]
    findings = scan_reader_units(rows)
    assert findings and {r["unit_id"] for r in findings} == {"2"}


def test_amend_is_exact_and_preserves_authority_without_mutating_input():
    task, old, change = sample()
    prior = copy.deepcopy(old)
    new, ledger = amend_proofread_submission(task, old, [change])
    assert old == prior
    assert new["units"][0]["source_hash"] == "EN"
    assert new["units"][0]["final_ru_text"] == "Персонажи"
    assert ledger["corrections"][0]["before_sha256"] == change["expected_final_ru_sha256"]


@pytest.mark.parametrize("kind", ["stale", "duplicate", "unknown", "order", "reason"])
def test_rejects_unbound_corrections(kind):
    task, old, change = sample()
    changes = [change]
    if kind == "stale": change["expected_final_ru_sha256"] = "wrong"
    if kind == "duplicate": changes.append(change)
    if kind == "unknown": change["unit_id"] = "unknown"
    if kind == "order": task["units"][0]["source_hash"] = "other"
    if kind == "reason": change["reason"] = ""
    with pytest.raises(ValueError): amend_proofread_submission(task, old, changes)


def test_return_to_draft_records_unchanged_truthfully():
    task, old, change = sample()
    change["final_ru_text"] = "Черновик"
    new, _ = amend_proofread_submission(task, old, [change])
    assert new["units"][0]["disposition"] == "checked_unchanged"
    assert new["units"][0]["reason"] == ""


def test_page_reference_scanner_covers_short_russian_abbreviation():
    rows = [{"unit_id": str(i), "ru_text": text} for i, text in enumerate([
        "см. с.31", "на с. 5", "см. стр. 25", "на странице 10", "Мисс. 12 лет"])]
    assert [r["unit_id"] for r in scan_reader_units(rows)] == ["0", "1", "2", "3"]
