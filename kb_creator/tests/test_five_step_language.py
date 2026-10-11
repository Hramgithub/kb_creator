from __future__ import annotations

import json
from pathlib import Path

import pytest

from kb_creator.pipeline import five_step_language as language


def _write(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _seal(value: dict[str, object], key: str) -> dict[str, object]:
    output = dict(value)
    output.pop(key, None)
    output[key] = language._sha(language._canonical(output))
    return output


def _complete_draft(template: Path) -> Path:
    value = json.loads(template.read_text(encoding="utf-8"))
    for unit in value["units"]:
        unit["ru_text"] = str(unit["unit_id"]).replace("unit", "Хранитель")
        # The fixture uses the English source as the unit id only for a marker
        # unit, so use text from the task below for prose payload.
    task = json.loads((template.parent / "draft.task.json").read_text(encoding="utf-8"))
    for unit, source in zip(value["units"], task["units"]):
        unit["ru_text"] = source["source_text"].replace("Keeper", "Хранитель")
    destination = template.parent / "draft.submission.json"
    _write(destination, value)
    return destination


def _fixture(tmp_path: Path) -> tuple[Path, Path, Path]:
    en_root = tmp_path / "en"; (en_root / "assets").mkdir(parents=True)
    master = en_root / "MASTER_EN.md"
    master.write_text("<!-- source-page-001 -->\n\n# The Keeper\n\nKeeper rolls 1d6.\n\n![Map](assets/map.png)\n", encoding="utf-8")
    (en_root / "assets" / "map.png").write_bytes(b"map")
    _write(en_root / "MASTER_EN.provenance.json", {"scenario_id": "fixture"})
    _write(en_root / "EN_SOURCE_SPANS.json", _seal({
        "schema": "kb_creator.five_step_en_source_spans.v1",
        "master_en": {"path": "MASTER_EN.md", "bytes": master.stat().st_size, "sha256": language._fsha(master)},
        "spans": [],
    }, "spans_sha256"))
    glossary = tmp_path / "terms.json"
    _write(glossary, {"terms": [{"source": "Keeper", "target": "Хранитель"}]})
    return master, glossary, tmp_path / "language"


def test_draft_then_proofread_builds_verified_master_with_context(tmp_path: Path) -> None:
    master, glossary, root = _fixture(tmp_path)
    _write(master.parent / "INVENTORY.json", {"source_inventory": "retained as context"})
    prepared = language.prepare_language(master, glossary, root, max_batch_chars=128)
    assert prepared["state"] == "needs_agent_work"
    draft_submission = _complete_draft(prepared["template_path"])
    drafted = language.submit_draft(root, draft_submission, tmp_path / "draft")
    template = json.loads(drafted["template_path"].read_text(encoding="utf-8"))
    for unit in template["units"]:
        unit["disposition"] = "checked_unchanged"
    proof_submission = tmp_path / "proofread.submission.json"
    _write(proof_submission, _seal(template, "submission_sha256"))
    result = language.submit_proofread(root, tmp_path / "draft", proof_submission, tmp_path / "final")
    assert result["master_ru"].read_text(encoding="utf-8").count("Хранитель") == 2
    assert (tmp_path / "final" / "assets" / "map.png").read_bytes() == b"map"
    assert (tmp_path / "final" / "semantic_context" / "MASTER_EN.provenance.json").is_file()
    assert language.verify_language_result(tmp_path / "final")["state"] == "verified"
    retained = tmp_path / "final/semantic_context/INVENTORY.json"
    assert retained.is_file()
    retained.write_text("changed", encoding="utf-8")
    with pytest.raises(language.FiveStepLanguageError, match="inventory"):
        language.verify_language_result(tmp_path / "final")


def test_proofread_requires_truthful_changed_ledger_and_no_unresolved(tmp_path: Path) -> None:
    master, glossary, root = _fixture(tmp_path)
    prepared = language.prepare_language(master, glossary, root, max_batch_chars=128)
    drafted = language.submit_draft(root, _complete_draft(prepared["template_path"]), tmp_path / "draft")
    proof = json.loads(drafted["template_path"].read_text(encoding="utf-8"))
    for unit in proof["units"]:
        unit["disposition"] = "checked_unchanged"
    proof["units"][0]["final_ru_text"] += "!"
    # A change cannot pretend to be checked unchanged.
    bad = tmp_path / "bad.json"; _write(bad, _seal(proof, "submission_sha256"))
    with pytest.raises(language.FiveStepLanguageError, match="disposition"):
        language.submit_proofread(root, tmp_path / "draft", bad, tmp_path / "final-bad")
    proof["units"][0]["disposition"] = "changed"; proof["units"][0]["reason"] = "punctuation"; proof["units"][0]["unresolved"] = ["confirm tone"]
    blocked = tmp_path / "blocked.json"; _write(blocked, _seal(proof, "submission_sha256"))
    with pytest.raises(language.FiveStepLanguageError, match="unresolved"):
        language.submit_proofread(root, tmp_path / "draft", blocked, tmp_path / "final-blocked")


def test_proofread_rejects_missing_or_reordered_units(tmp_path: Path) -> None:
    master, glossary, root = _fixture(tmp_path)
    prepared = language.prepare_language(master, glossary, root, max_batch_chars=128)
    drafted = language.submit_draft(root, _complete_draft(prepared["template_path"]), tmp_path / "draft")
    proof = json.loads(drafted["template_path"].read_text(encoding="utf-8"))
    for unit in proof["units"]:
        unit["disposition"] = "checked_unchanged"
    proof["units"].pop()
    submission = tmp_path / "missing.json"; _write(submission, _seal(proof, "submission_sha256"))
    with pytest.raises(language.FiveStepLanguageError, match="coverage"):
        language.submit_proofread(root, tmp_path / "draft", submission, tmp_path / "final")


def test_verifier_detects_byte_drift(tmp_path: Path) -> None:
    master, glossary, root = _fixture(tmp_path)
    prepared = language.prepare_language(master, glossary, root, max_batch_chars=128)
    drafted = language.submit_draft(root, _complete_draft(prepared["template_path"]), tmp_path / "draft")
    proof = json.loads(drafted["template_path"].read_text(encoding="utf-8"))
    for unit in proof["units"]:
        unit["disposition"] = "checked_unchanged"
    submission = tmp_path / "proof.json"; _write(submission, _seal(proof, "submission_sha256"))
    language.submit_proofread(root, tmp_path / "draft", submission, tmp_path / "final")
    (tmp_path / "final" / "assets" / "map.png").write_bytes(b"tampered")
    with pytest.raises(language.FiveStepLanguageError, match="inventory"):
        language.verify_language_result(tmp_path / "final")


def test_pending_proofread_template_cannot_be_submitted(tmp_path: Path) -> None:
    master, glossary, root = _fixture(tmp_path)
    prepared = language.prepare_language(master, glossary, root, max_batch_chars=128)
    drafted = language.submit_draft(root, _complete_draft(prepared["template_path"]), tmp_path / "draft")
    pending = tmp_path / "pending.json"
    _write(pending, json.loads(drafted["template_path"].read_text(encoding="utf-8")))
    with pytest.raises(language.FiveStepLanguageError, match="pending"):
        language.submit_proofread(root, tmp_path / "draft", pending, tmp_path / "final")


def test_resealed_master_content_does_not_fool_independent_verifier(tmp_path: Path) -> None:
    master, glossary, root = _fixture(tmp_path)
    prepared = language.prepare_language(master, glossary, root, max_batch_chars=128)
    drafted = language.submit_draft(root, _complete_draft(prepared["template_path"]), tmp_path / "draft")
    proof = json.loads(drafted["template_path"].read_text(encoding="utf-8"))
    for unit in proof["units"]:
        unit["disposition"] = "checked_unchanged"
    submission = tmp_path / "proof.json"; _write(submission, proof)
    language.submit_proofread(root, tmp_path / "draft", submission, tmp_path / "final")
    result = tmp_path / "final"
    (result / "MASTER_RU.md").write_text("forged\n", encoding="utf-8")
    manifest = json.loads((result / "MASTER_RU.manifest.json").read_text(encoding="utf-8"))
    manifest["master_ru"] = language._id(result / "MASTER_RU.md", result)
    _write(result / "MASTER_RU.manifest.json", _seal(manifest, "manifest_sha256"))
    with pytest.raises(language.FiveStepLanguageError):
        language.verify_language_result(result)


def test_verifier_rejects_resealed_draft_task_path_outside_closed_relocation(tmp_path: Path) -> None:
    master, glossary, root = _fixture(tmp_path)
    prepared = language.prepare_language(master, glossary, root, max_batch_chars=128)
    drafted = language.submit_draft(root, _complete_draft(prepared["template_path"]), tmp_path / "draft")
    proof = json.loads(drafted["template_path"].read_text(encoding="utf-8"))
    for unit in proof["units"]:
        unit["disposition"] = "checked_unchanged"
    submission = tmp_path / "proof.json"; _write(submission, proof)
    language.submit_proofread(root, tmp_path / "draft", submission, tmp_path / "final")
    archived = tmp_path / "final" / "evidence" / "draft.submission.json"
    draft_submission = json.loads(archived.read_text(encoding="utf-8"))
    draft_submission["task"]["path"] = "other/draft.task.json"
    _write(archived, _seal(draft_submission, "submission_sha256"))
    with pytest.raises(language.FiveStepLanguageError, match="relocation"):
        language.verify_language_result(tmp_path / "final")


def test_verifier_rejects_resealed_proof_task_unit_drift(tmp_path: Path) -> None:
    master, glossary, root = _fixture(tmp_path)
    prepared = language.prepare_language(master, glossary, root, max_batch_chars=128)
    drafted = language.submit_draft(root, _complete_draft(prepared["template_path"]), tmp_path / "draft")
    proof = json.loads(drafted["template_path"].read_text(encoding="utf-8"))
    for unit in proof["units"]:
        unit["disposition"] = "checked_unchanged"
    submission = tmp_path / "proof.json"; _write(submission, proof)
    language.submit_proofread(root, tmp_path / "draft", submission, tmp_path / "final")
    result = tmp_path / "final"; task_path = result / "evidence" / "proofread.task.json"
    task = json.loads(task_path.read_text(encoding="utf-8")); task["units"][0]["source_text"] = "forged"
    _write(task_path, _seal(task, "task_sha256"))
    manifest_path = result / "MASTER_RU.manifest.json"; manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["proofread_task"] = language._id(task_path, result)
    _write(manifest_path, _seal(manifest, "manifest_sha256"))
    inventory_path = result / "INVENTORY.json"
    inventory = json.loads(inventory_path.read_text(encoding="utf-8"))
    inventory["files"] = [language._id(path, result) for path in sorted((item for item in result.rglob("*") if item.is_file() and item.name != "INVENTORY.json"), key=lambda item: item.relative_to(result).as_posix())]
    _write(inventory_path, _seal(inventory, "inventory_sha256"))
    with pytest.raises(language.FiveStepLanguageError, match="proofread binding"):
        language.verify_language_result(result)


def test_reviewed_source_span_projects_full_translation_units_only(tmp_path: Path) -> None:
    master = tmp_path / "MASTER_EN.md"
    master.write_text("intro\n\nSTR 50\nHP 10\n\noutro\n", encoding="utf-8")
    stat = "STR 50\nHP 10"
    spans = {
        "schema": "kb_creator.five_step_en_source_spans.v1",
        "master_en": {"path": "MASTER_EN.md", "bytes": master.stat().st_size, "sha256": language._fsha(master)},
        "spans": [{"id": "reviewed-stat-1", "kind": "statblock", "source_page": 1, "start_line": 3, "end_line": 4, "sha256": language._sha(stat.encode()), "decision": {"path": "review.json", "bytes": 1, "sha256": "A" * 64}}],
    }
    rows = [
        {"unit_id": "u1", "source_text": "intro", "ru_text": "ввод"},
        {"unit_id": "u2", "source_text": stat, "ru_text": "СИЛ 50\nПЗ 10"},
        {"unit_id": "u3", "source_text": "outro", "ru_text": "итог"},
    ]
    projected = language._project_spans(master, rows, spans)
    assert projected == [{"span_id": "reviewed-stat-1", "semantic_kind": "statblock", "source_span_id": "reviewed-stat-1", "unit_ids": ["u2"], "start": {"unit_id": "u2", "char_offset": 0}, "end": {"unit_id": "u2", "char_offset": len("СИЛ 50\nПЗ 10")}, "source_sha256": language._sha(stat.encode())}]
    spans["spans"][0]["start_line"] = 4
    spans["spans"][0]["sha256"] = language._sha(b"HP 10")
    with pytest.raises(language.FiveStepLanguageError, match="semantic partial start"):
        language._project_spans(master, rows, spans)


def test_split_translation_reassembly_keeps_content_not_boundary_mode() -> None:
    ordinary = [
        {"unit_id": "u1", "parent_unit_id": "parent", "ru_text": "Первый фрагмент"},
        {"unit_id": "u2", "parent_unit_id": "parent", "ru_text": "второй фрагмент"},
    ]
    dehyphenated = [
        {"unit_id": "u1", "parent_unit_id": "parent", "ru_text": "сло-"},
        {"unit_id": "u2", "parent_unit_id": "parent", "ru_text": "во"},
    ]
    assert language._assemble(ordinary) == "Первый фрагмент второй фрагмент\n"
    assert language._assemble(dehyphenated) == "слово\n"
    assert "continued_prose" not in language._assemble(ordinary)
    assert "dehyphenated_word" not in language._assemble(dehyphenated)


def test_split_quote_boundary_preserves_blank_quote_paragraph_and_renderer_text(tmp_path: Path) -> None:
    from translator.translator import markdown_to_review_html
    rows = [
        {"unit_id": "u1", "parent_unit_id": "parent", "source_text": "> ### Heading\n>", "ru_text": "> ### Заголовок\n>"},
        {"unit_id": "u2", "parent_unit_id": "parent", "source_text": "> Paragraph", "ru_text": "> Абзац"},
    ]
    assembled = language._assemble(rows)
    assert assembled == "> ### Заголовок\n>\n> Абзац\n"
    source = tmp_path / "source.md"; source.write_text(assembled, encoding="utf-8")
    body, _toc, _pages = markdown_to_review_html(assembled, source_path=source, html_path=tmp_path / "accepted.html")
    assert "&gt; Абзац" not in body
    assert ">Абзац<" in body
    legacy = "> ### Заголовок\n> > Абзац\n"
    source.write_text(legacy, encoding="utf-8")
    legacy_body, _toc, _pages = markdown_to_review_html(legacy, source_path=source, html_path=tmp_path / "legacy.html")
    assert "&gt; Абзац" in legacy_body


@pytest.mark.parametrize("left,right", [("> content", "> paragraph"), (">", "paragraph"), (">>", "> paragraph"), (">", "> > paragraph")])
def test_split_quote_boundary_keeps_unsupported_topologies_legacy(left: str, right: str) -> None:
    rows = [{"unit_id": "u1", "parent_unit_id": "parent", "ru_text": left}, {"unit_id": "u2", "parent_unit_id": "parent", "ru_text": right}]
    assert language._assemble(rows) == language.legacy._boundary_join(left, right)[0] + "\n"


def test_split_quote_boundary_rejects_ru_source_topology_mismatch() -> None:
    rows = [
        {"unit_id": "u1", "parent_unit_id": "parent", "source_text": "> heading", "ru_text": "> heading\n>"},
        {"unit_id": "u2", "parent_unit_id": "parent", "source_text": "> paragraph", "ru_text": "> paragraph"},
    ]
    with pytest.raises(language.FiveStepLanguageError, match="source topology"):
        language._assemble(rows)


def test_public_route_projects_line_end_before_portrait_and_verifies_it(tmp_path: Path) -> None:
    pytest.importorskip("docx"); pytest.importorskip("lxml"); Image = pytest.importorskip("PIL.Image")
    from kb_creator.pipeline import five_step_docx as docx
    en = tmp_path / "en"; (en / "assets").mkdir(parents=True)
    master = en / "MASTER_EN.md"
    source_stat = "STR 50\nSkills: Spot Hidden 25%."
    master.write_text(f"# Intro\n\nintro\n\n{source_stat}\n![Portrait](assets/map.png)\n\noutro\n", encoding="utf-8")
    Image.new("RGB", (8, 8), "white").save(en / "assets/map.png")
    _write(en / "MASTER_EN.provenance.json", {"scenario_id": "partial-line"})
    _write(en / "EN_SOURCE_SPANS.json", _seal({
        "schema": "kb_creator.five_step_en_source_spans.v1",
        "master_en": {"path": "MASTER_EN.md", "bytes": master.stat().st_size, "sha256": language._fsha(master)},
        "spans": [{"id": "stat-1", "kind": "statblock", "source_page": 1, "start_line": 5, "end_line": 6, "sha256": language._sha(source_stat.encode()), "decision": {"path": "review.json", "bytes": 1, "sha256": "A" * 64}}],
    }, "spans_sha256"))
    glossary = tmp_path / "terms.json"; _write(glossary, {"terms": [{"source": "outro", "target": "итог"}]})
    prepared = language.prepare_language(master, glossary, tmp_path / "language", max_batch_chars=128)
    draft = json.loads(prepared["template_path"].read_text(encoding="utf-8"))
    for row, source in zip(draft["units"], json.loads(prepared["task_path"].read_text(encoding="utf-8"))["units"]):
        row["ru_text"] = source["source_text"].replace("# Intro", "# Введение").replace("STR", "СИЛ").replace("Skills: Spot Hidden", "Навыки: Внимание").replace("Portrait", "Портрет").replace("intro", "ввод").replace("outro", "итог")
    draft_path = tmp_path / "draft.json"; _write(draft_path, _seal(draft, "submission_sha256"))
    drafted = language.submit_draft(tmp_path / "language", draft_path, tmp_path / "draft")
    proof = json.loads(drafted["template_path"].read_text(encoding="utf-8"))
    for row in proof["units"]: row["disposition"] = "checked_unchanged"
    proof_path = tmp_path / "proof.json"; _write(proof_path, _seal(proof, "submission_sha256"))
    language.submit_proofread(tmp_path / "language", tmp_path / "draft", proof_path, tmp_path / "final")
    assert language.verify_language_result(tmp_path / "final")["state"] == "verified"
    projection = json.loads((tmp_path / "final/semantic_context/RU_PROJECTION.json").read_text(encoding="utf-8"))
    span = projection["spans"][0]; last = next(row for row in projection["units"] if row["unit_id"] == span["end"]["unit_id"])
    assert last["ru_text"][span["end"]["char_offset"]:] == "\n![Портрет](assets/map.png)"
    package = docx.build_docx_package(tmp_path / "final", tmp_path / "docx", title="Partial span")
    manifest = json.loads(package["manifest_path"].read_text(encoding="utf-8"))
    assert len(manifest["statblock_projection"]) == 1
    html = (package["manifest_path"].parent / "internal.html").read_text(encoding="utf-8")
    assert html.index('data-semantic-id="stat-1"') < html.index("assets/map.png")


@pytest.mark.parametrize("source_suffix,ru_suffix", [("\nordinary prose", "\nобычный текст"), ("\n![Portrait](assets/map.png)", "\n![Portrait](assets/other.png)")])
def test_partial_projection_rejects_non_image_suffix_or_changed_target(tmp_path: Path, source_suffix: str, ru_suffix: str) -> None:
    master = tmp_path / "MASTER_EN.md"; stat = "Skills: Spot Hidden 25%."
    master.write_text(stat + source_suffix + "\n", encoding="utf-8")
    spans = {"spans": [{"id": "stat-1", "kind": "statblock", "start_line": 1, "end_line": 1, "sha256": language._sha(stat.encode())}]}
    rows = [{"unit_id": "u1", "source_text": stat + source_suffix, "ru_text": "Навыки: Внимание 25%." + ru_suffix}]
    with pytest.raises(language.FiveStepLanguageError, match="partial end"):
        language._project_spans(master, rows, spans)
