from __future__ import annotations
import csv
import json
from pathlib import Path

import pytest
from kb_creator.pipeline import coc_glossary as glossary
from kb_creator.pipeline import five_step_language as language
from kb_creator.scripts import scenario_master_ru as legacy
from kb_creator.scripts import verify_scenario_master_ru as independent
from kb_creator.tests.test_five_step_language import _fixture, _complete_draft
from kb_creator.tests.test_language_continuation import predecessor
from kb_creator.pipeline.language_continuation import prepare_continuation, verify_continuation


def write(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False), encoding="utf-8")


@pytest.fixture
def inputs(tmp_path):
    registry = tmp_path / "registry.csv"
    rows = [dict(zip(glossary.HEADER, row)) for row in [
        ["Keeper", "Хранитель", "Хранителю", "", "role", "accepted", "source page2", "reviewed", "Определение: Ведущий игры. Источник: source page2. Область: роль."],
        ["SAN", "РАС", "", "SAN", "characteristic", "accepted", "statblock", "reviewed", ""],
        ["Unknown", "Спорный", "", "", "general", "review_required", "source page5", "pending", ""],
    ]]
    with registry.open("w", encoding="utf-8-sig", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=glossary.HEADER)
        writer.writeheader(); writer.writerows(rows)
    overlay = tmp_path / "book.json"
    write(overlay, {"terms": [{"source": "Keeper", "target": "Хранитель", "aliases": ["Хранителя"], "domain": "role"},
                              {"source": "Walter", "target": "Уолтер", "domain": "proper"}]})
    return registry, overlay


def test_all_shared_terms_definitions_and_book_choices_reach_legacy_parser(inputs, tmp_path):
    registry, overlay = inputs
    result = glossary.compose_glossary(registry, overlay, "book", tmp_path / "bundle")
    assert result["state"] == "ready" and result["terms"] == 3
    path = Path(result["glossary_path"])
    terms = legacy._terminology_terms([("effective", path)])
    assert {row["source"] for row in terms} == {"Keeper", "SAN", "Walter"}
    assert next(row for row in terms if row["source"] == "Keeper")["aliases"] == ("Хранителю", "Хранителя")
    payload = json.loads(path.read_text(encoding="utf-8"))
    assert payload["context"]["shared_rows"][0]["definition"] == "Ведущий игры."
    assert payload["context"]["shared_rows"][2]["status"] == "review_required"
    # Offline snapshots remain exact evidence even after the live registry changes.
    registry.write_text("changed", encoding="utf-8")
    assert glossary.verify_glossary(tmp_path / "bundle")["state"] == "ready"
    assert legacy._terminology_terms([("effective", path)]) == terms


@pytest.mark.parametrize("change", ["target", "domain", "bad"])
def test_conflicts_have_no_usable_effective_glossary(inputs, tmp_path, change):
    registry, overlay = inputs
    value = json.loads(overlay.read_text(encoding="utf-8"))
    value["terms"][0][{"target": "target", "domain": "domain", "bad": "bad_ru"}[change]] = {
        "target": "Ведущий", "domain": "skill", "bad": ["Хранитель"]}[change]
    write(overlay, value)
    result = glossary.compose_glossary(registry, overlay, "book", tmp_path / "bundle")
    assert result["state"] == "conflicts" and result["conflicts"] == 1
    assert not (tmp_path / "bundle/glossary.json").exists()


def test_book_choice_does_not_promote_global_unresolved_term(inputs, tmp_path):
    registry, overlay = inputs
    write(overlay, {"terms": [{"source": "Unknown", "target": "Местный вариант"}]})
    result = glossary.compose_glossary(registry, overlay, "book", tmp_path / "bundle")
    value = json.loads(Path(result["glossary_path"]).read_text(encoding="utf-8"))
    assert next(row for row in value["terms"] if row["source"] == "Unknown")["target"] == "Местный вариант"
    assert value["context"]["shared_rows"][2]["status"] == "review_required"
    assert value["context"]["book_rows"][0]["status"] == "selected_book_choice"


@pytest.mark.parametrize("key", ["terms", "context", "sources"])
def test_resealed_tampering_is_recomputed_from_snapshot(inputs, tmp_path, key):
    registry, overlay = inputs
    result = glossary.compose_glossary(registry, overlay, "book", tmp_path / "bundle")
    value = json.loads(Path(result["glossary_path"]).read_text(encoding="utf-8"))
    if key == "terms": value["terms"][0]["target"] = "Подмена"
    elif key == "context": value["context"]["shared_rows"][0]["definition"] = "Подмена"
    else: value["sources"]["registry"]["sha256"] = "0" * 64
    value["glossary_sha256"] = glossary.digest({k: v for k, v in value.items() if k != "glossary_sha256"})
    with pytest.raises(ValueError, match="snapshots|snapshot hash"):
        glossary.validate_payload(value)


def test_duplicate_overlay_and_no_overwrite(inputs, tmp_path):
    registry, overlay = inputs
    value = json.loads(overlay.read_text(encoding="utf-8"))
    value["terms"].append({"source": " keeper ", "target": "Хранитель"})
    write(overlay, value)
    with pytest.raises(ValueError, match="duplicate overlay"):
        glossary.compose_glossary(registry, overlay, "book", tmp_path / "bundle")
    assert not (tmp_path / "bundle").exists()
    (tmp_path / "existing").mkdir()
    with pytest.raises(ValueError, match="absent"):
        glossary.compose_glossary(registry, overlay, "book", tmp_path / "existing")


def test_determinism_and_unlisted_file_rejection(inputs, tmp_path):
    registry, overlay = inputs
    for folder in ("one", "two"):
        glossary.compose_glossary(registry, overlay, "book", tmp_path / folder)
    assert (tmp_path / "one/glossary.json").read_bytes() == (tmp_path / "two/glossary.json").read_bytes()
    (tmp_path / "one/extra.txt").write_text("extra")
    with pytest.raises(ValueError, match="inventory"):
        glossary.verify_glossary(tmp_path / "one")


def test_real_language_roundtrip_keeps_definitions_and_source_snapshot(inputs, tmp_path):
    registry, overlay = inputs
    master, _, root = _fixture(tmp_path / "fixture")
    result = glossary.compose_glossary(registry, overlay, "book", tmp_path / "bundle")
    language.prepare_language(master, Path(result["glossary_path"]), root)
    input_context = json.loads((root / "LANGUAGE_INPUT.json").read_text(encoding="utf-8"))
    assert input_context["terminology_context"]["shared_rows"][0]["definition"] == "Ведущий игры."
    draft = tmp_path / "draft"
    language.submit_draft(root, _complete_draft(root / "draft.template.json"), draft)
    proof = json.loads((draft / "proofread.template.json").read_text(encoding="utf-8"))
    for row in proof["units"]: row["disposition"] = "checked_unchanged"
    write(tmp_path / "proof.json", proof)
    final = tmp_path / "final"
    language.submit_proofread(root, draft, tmp_path / "proof.json", final)
    language.verify_language_result(final)
    archived = json.loads((final / "evidence/glossary.json").read_text(encoding="utf-8"))
    assert archived["sources"]["registry"]["sha256"] == glossary.identity(registry.read_bytes())["sha256"]
    assert archived["context"]["shared_rows"][0]["definition"] == "Ведущий игры."


def test_authority_context_forms_preserve_prose_and_compact_stats(inputs, tmp_path):
    registry, overlay = inputs
    rows = glossary.registry_rows(registry.read_bytes())
    rule = {"selector": "numeric_label_vs_prose", "prose": {"target": "Рассудок", "aliases": ["Рассудка"], "bad": ["SAN"]}}
    rows[1]["notes"] = "Контекст JSON: " + json.dumps(rule, ensure_ascii=False)
    rows[1]["bad_ru"] = "SAN;Рассудок;Рассудка"
    with registry.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=glossary.HEADER); writer.writeheader(); writer.writerows(rows)
    result = glossary.compose_glossary(registry, overlay, "book", tmp_path / "bundle")
    path = Path(result["glossary_path"])
    for source, target in [("Lose 1 SAN.", "Потеряйте 1 пункт Рассудка."), ("SAN 44", "РАС 44")]:
        assert language._mechanics([{"unit_id": "u", "source_text": source, "ru_text": target}], path) == []
        for authority in (path, registry):
            term = next(row for row in independent._terms([("selected", authority)]) if row["source"] == "SAN")
            chosen = independent._context_forms(term, source)
            assert any(independent._present(form, target) for form in chosen["targets"])
            assert not any(independent._bad_variant_present(form, chosen["targets"], target) for form in chosen["bad"])
    bad = language._mechanics([{"unit_id": "u", "source_text": "SAN 44", "ru_text": "Рассудок 44"}], path)
    assert any(row["code"] == "terminology_bad_variant" for row in bad)
    mixed = language._mechanics([{"unit_id": "u", "source_text": "SAN 44. Lose 1 SAN.", "ru_text": "РАС 44. Потеряйте 1 пункт Рассудка."}], path)
    assert any(row["code"] == "terminology_context_ambiguous" for row in mixed)


def test_shared_registry_is_composed_by_real_continuation_entry(inputs, predecessor, tmp_path):
    registry, _ = inputs
    run, book = predecessor
    output = tmp_path / "with_shared"
    result = prepare_continuation(run, book, output, shared_registry=registry, book_id="fixture")
    assert result["phase"] == "documentary_draft"
    assert verify_continuation(output)["state"] == "verified"
    payload = json.loads((output / "glossary.json").read_text(encoding="utf-8"))
    assert {row["source"] for row in payload["terms"]} == {"Keeper", "SAN"}
    assert payload["context"]["shared_rows"][0]["definition"] == "Ведущий игры."


def test_shared_only_glossary_and_independent_tamper_check(inputs, tmp_path):
    registry, overlay = inputs
    write(overlay, {"terms": []})
    result = glossary.compose_glossary(registry, overlay, "book", tmp_path / "bundle")
    path = Path(result["glossary_path"])
    assert len(independent._terms([("effective", path)])) == 2
    value = json.loads(path.read_text(encoding="utf-8"))
    value["terms"][0]["target"] = "Подмена"
    value["glossary_sha256"] = glossary.digest({k: v for k, v in value.items() if k != "glossary_sha256"})
    write(tmp_path / "tampered.json", value)
    with pytest.raises(ValueError, match="derivation"):
        independent._terms([("effective", tmp_path / "tampered.json")])
