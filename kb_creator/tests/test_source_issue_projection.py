from __future__ import annotations

import hashlib
import json
import zipfile
from pathlib import Path

import pytest

pytest.importorskip("docx")

from kb_creator.pipeline.identity import file_identity, sha256_bytes
from kb_creator.pipeline.manifests import sealed
from kb_creator.pipeline.source_issue_projection import (
    SourceIssueProjectionError, derive_source_issue_projection,
)
from kb_creator.pipeline.reader_occurrence_projection import build_issue_en_bindings_v2
from kb_creator.pipeline import five_step_docx, reader_projection


def _write(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False), encoding="utf-8")


def _fixture(tmp_path: Path, *, split: bool = False) -> dict[str, Path]:
    en = tmp_path / "MASTER_EN.md"; en.write_text("<!-- source-page-001 -->\n\n# Chapter\n\nRole text\n", encoding="utf-8")
    ru = tmp_path / "MASTER_RU.md"; ru.write_text("<!-- source-page-001 -->\n\n# Глава\n\nТекст роли\n", encoding="utf-8")
    source = "<!-- source-page-001 -->\n\n# Chapter\n\nRole text"
    units = ([{"unit_id": "u1", "source_hash": "A" * 64, "source_text": source,
               "parent_unit_id": None, "part_index": None, "part_count": None}]
             if not split else [
                 {"unit_id": "u1", "source_hash": "A" * 64, "source_text": "<!-- source-page-001 -->\n\n",
                  "parent_unit_id": None, "part_index": None, "part_count": None},
                 {"unit_id": "u2", "source_hash": "B" * 64, "source_text": "# Chapter",
                  "parent_unit_id": None, "part_index": None, "part_count": None},
                 {"unit_id": "u3", "source_hash": "C" * 64, "source_text": "Role ",
                  "parent_unit_id": "p", "part_index": 1, "part_count": 2},
                 {"unit_id": "u4", "source_hash": "D" * 64, "source_text": "text",
                  "parent_unit_id": "p", "part_index": 2, "part_count": 2},
             ])
    task = sealed("kb_creator.five_step_language_draft_task.v3", {
        "master_en": {"path": "MASTER_EN.md", **file_identity(en)}, "units": units,
    }, digest_key="task_sha256")
    task_path = tmp_path / "draft.task.json"; _write(task_path, task)
    ru_units = []
    for index, row in enumerate(units, 1):
        text = ("<!-- source-page-001 -->" if split and index == 1 else
                ("# Глава" if split and index == 2 else ("Текст " if split and index == 3 else ("роли" if split else ru.read_text(encoding="utf-8").strip()))))
        ru_units.append({"unit_id": row["unit_id"], "source_hash": row["source_hash"],
                         "parent_unit_id": row["parent_unit_id"], "part_index": row["part_index"],
                         "part_count": row["part_count"], "ru_text": text,
                         "ru_sha256": sha256_bytes(text.encode("utf-8"))})
    projection = sealed("kb_creator.five_step_ru_projection.v3", {
        "master_en": {"path": "evidence/MASTER_EN.md", **file_identity(en)},
        "master_ru": {"path": "MASTER_RU.md", **file_identity(ru)},
        "source_spans": {"path": "evidence/EN_SOURCE_SPANS.json", "bytes": 1, "sha256": "0" * 64},
        "unit_order": [row["unit_id"] for row in ru_units], "units": ru_units, "spans": [],
    }, digest_key="projection_sha256")
    projection_path = tmp_path / "RU_PROJECTION.json"; _write(projection_path, projection)
    excerpt = "Raw source role text"
    issue = {"issue_id": "role-1", "kind": "source_structure_role_pending", "state": "open", "source_page": 1,
             "reason": "Источник расходится в структурной роли",
             "source_excerpt_en": excerpt, "source_excerpt_sha256": sha256_bytes(excerpt.encode("utf-8")),
             "source_selector": {"comparison_structural_role_v1": {"provisional_selection_purpose": "text"}}}
    evidence_path = tmp_path / "final.json"; _write(evidence_path, {"source_issues": {"issues": [issue]}})
    start = en.read_text(encoding="utf-8").index("Role text"); end = start + len("Role text")
    binding = {"issue_id": "role-1", "source_page": 1, "source_selector": issue["source_selector"],
               "character_start": start, "character_end": end,
               "byte_start": len(en.read_text(encoding="utf-8")[:start].encode()), "byte_end": len(en.read_text(encoding="utf-8")[:end].encode()),
               "text_sha256": sha256_bytes(b"Role text")}
    bindings = sealed("kb_creator.issue_en_bindings.v1", {"master_en": {"path": "MASTER_EN.md", **file_identity(en)},
                       "final_evidence": {"path": str(evidence_path), **file_identity(evidence_path)}, "bindings": [binding]}, digest_key="bindings_sha256")
    bindings_path = tmp_path / "issues.json"; _write(bindings_path, bindings)
    return {"en": en, "ru": ru, "projection": projection_path, "task": task_path, "bindings": bindings_path, "evidence": evidence_path}


def _v2_fixture(tmp_path: Path, *, repeated: bool = False) -> dict[str, Path]:
    """A display-normalized heading with a split EN-to-RU translation group."""
    root = tmp_path / "review-master"; (root / "evidence" / "review").mkdir(parents=True)
    en = root / "MASTER_EN.md"
    en.write_text("<!-- source-page-001 -->\n\n" + ("# Reader Heading\n\n" if repeated else "") + "# Reader Heading\n", encoding="utf-8")
    ru = tmp_path / "MASTER_RU.md"; ru.write_text("<!-- source-page-001 -->\n\n" + ("# Заголовок читателя\n\n" if repeated else "") + "# Заголовок читателя\n", encoding="utf-8")
    raw = "<sup>Reader</sup> Heading"
    issue = {"issue_id": "heading-1", "kind": "source_structure_role_pending", "state": "open", "source_page": 1,
             "reason": "Проверить заголовок", "source_excerpt_en": raw,
             "source_excerpt_sha256": sha256_bytes(raw.encode("utf-8")),
             "source_selector": {"comparison_structural_role_v1": {"provisional_selection_purpose": "heading"}},
             "candidate_span": {"semantic_unit_id": "heading-unit"}}
    decision = {"source_page": 1, "markdown": "# Reader Heading", "selected_blocks": [{"view": "original_pipeline_txt", "raw_index": 7}],
                "semantic_structure": {"units": [{"id": "heading-unit", "source_blocks": [{"view": "original_pipeline_txt", "raw_index": 7}],
                    "markdown_span": {"start_line": 1, "end_line": 1, "sha256": sha256_bytes(b"# Reader Heading")}}]}}
    if repeated:
        decision["markdown"] = "# Reader Heading\n\n# Reader Heading"
        decision["selected_blocks"].insert(0, {"view": "original_pipeline_txt", "raw_index": 6})
        decision["semantic_structure"]["units"][0]["markdown_span"].update(start_line=3, end_line=3)
        decision["semantic_structure"]["units"].insert(0, {
            "id": "earlier-heading", "source_blocks": [{"view": "original_pipeline_txt", "raw_index": 6}],
            "markdown_span": {"start_line": 1, "end_line": 1, "sha256": sha256_bytes(b"# Reader Heading")}})
    _write(root / "evidence" / "review" / "page-001.json", decision)
    audit = tmp_path / "stage05.json"; _write(audit, {"pages": [{"source_page": 1, "ordered_proof_stream": []}]})
    evidence = tmp_path / "final-v2.json"
    _write(evidence, {"source_issues": {"issues": [issue]}, "authored": {"stage05_audit": {"path": audit.name, **file_identity(audit)}}})
    bindings = build_issue_en_bindings_v2(en, [issue], [1], evidence)
    bindings_path = root / "ISSUE_EN_BINDINGS.v2.json"; _write(bindings_path, bindings)
    text = en.read_text(encoding="utf-8")
    units = [
        {"unit_id": "marker", "source_hash": "A" * 64, "source_text": "<!-- source-page-001 -->\n\n", "parent_unit_id": None, "part_index": None, "part_count": None},
        {"unit_id": "heading-1", "source_hash": "B" * 64, "source_text": "# Reader ", "parent_unit_id": "heading", "part_index": 1, "part_count": 2},
        {"unit_id": "heading-2", "source_hash": "C" * 64, "source_text": "Heading\n", "parent_unit_id": "heading", "part_index": 2, "part_count": 2},
    ]
    if repeated:
        units.insert(1, {"unit_id": "earlier-heading", "source_hash": "D" * 64, "source_text": "# Reader Heading\n\n",
                         "parent_unit_id": None, "part_index": None, "part_count": None})
    assert "".join(row["source_text"] for row in units) == text
    task = sealed("kb_creator.five_step_language_draft_task.v3", {"master_en": {"path": "MASTER_EN.md", **file_identity(en)}, "units": units}, digest_key="task_sha256")
    task_path = tmp_path / "draft-v2.task.json"; _write(task_path, task)
    ru_texts = ["<!-- source-page-001 -->", "# Заголовок ", "читателя"]
    if repeated:
        ru_texts.insert(1, "# Заголовок читателя")
    ru_rows = [{"unit_id": row["unit_id"], "source_hash": row["source_hash"], "parent_unit_id": row["parent_unit_id"],
                "part_index": row["part_index"], "part_count": row["part_count"], "ru_text": ru_text,
                "ru_sha256": sha256_bytes(ru_text.encode("utf-8"))} for row, ru_text in zip(units, ru_texts)]
    projection = sealed("kb_creator.five_step_ru_projection.v3", {"master_en": {"path": "MASTER_EN.md", **file_identity(en)},
        "master_ru": {"path": "MASTER_RU.md", **file_identity(ru)}, "source_spans": {"path": "spans", "bytes": 1, "sha256": "0" * 64},
        "unit_order": [row["unit_id"] for row in ru_rows], "units": ru_rows, "spans": []}, digest_key="projection_sha256")
    projection_path = tmp_path / "RU_PROJECTION.v2.json"; _write(projection_path, projection)
    return {"en": en, "ru": ru, "projection": projection_path, "task": task_path, "bindings": bindings_path, "evidence": evidence}


def _reseal(value: dict, key: str) -> None:
    value[key] = sha256_bytes(json.dumps({k: v for k, v in value.items() if k != key}, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode())


def test_projects_exact_r1_span_without_replacing_immutable_source_excerpt(tmp_path: Path) -> None:
    paths = _fixture(tmp_path)
    result = derive_source_issue_projection(master_en=paths["en"], master_ru=paths["ru"], ru_projection=paths["projection"],
                                            issue_en_bindings=paths["bindings"], final_evidence=paths["evidence"], language_task=paths["task"])
    assert result["roles"][0]["unit"]["unit_id"] == "u1"
    assert result["roles"][0]["en_excerpt"] == "Raw source role text"
    assert result["roles"][0]["reason"].startswith("Проверить смысл")


def test_v2_uses_exact_reader_span_and_keeps_raw_provenance_for_split_group(tmp_path: Path) -> None:
    paths = _v2_fixture(tmp_path)
    result = derive_source_issue_projection(master_en=paths["en"], master_ru=paths["ru"], ru_projection=paths["projection"],
                                            issue_en_bindings=paths["bindings"], final_evidence=paths["evidence"], language_task=paths["task"])
    role = result["roles"][0]
    assert role["en_excerpt"] == "Reader Heading"
    assert role["raw_source_excerpt_en"] == "<sup>Reader</sup> Heading"
    assert [row["unit_id"] for row in role["units"]] == ["heading-1", "heading-2"]


def test_v2_repeated_heading_maps_second_occurrence_and_rejects_resealed_first(tmp_path: Path) -> None:
    paths = _v2_fixture(tmp_path, repeated=True)
    args = dict(master_en=paths["en"], master_ru=paths["ru"], ru_projection=paths["projection"],
                issue_en_bindings=paths["bindings"], final_evidence=paths["evidence"], language_task=paths["task"])
    role = derive_source_issue_projection(**args)["roles"][0]
    assert [row["unit_id"] for row in role["units"]] == ["heading-1", "heading-2"]
    value = json.loads(paths["bindings"].read_text(encoding="utf-8"))
    span = value["bindings"][0]["master_reader_span"]
    source = paths["en"].read_text(encoding="utf-8")
    first = source.index("Reader Heading")
    assert span["character_start"] == source.rindex("Reader Heading")
    # The forged occurrence has identical text/hash and valid byte coordinates;
    # only fresh selected-source rederivation can disprove it.
    span.update(character_start=first, character_end=first + len("Reader Heading"),
                byte_start=len(source[:first].encode()), byte_end=len(source[:first + len("Reader Heading")].encode()))
    _reseal(value, "bindings_sha256"); _write(paths["bindings"], value)
    with pytest.raises(SourceIssueProjectionError, match="v2"):
        derive_source_issue_projection(**args)


def test_v2_projection_survives_native_docx_comment_package(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    paths = _v2_fixture(tmp_path)
    # The preceding v2 test exercises split-parent placement.  Keep this DOCX
    # fixture compact while proving the native comment path with the same
    # transformed reader occurrence.
    source = paths["en"].read_text(encoding="utf-8")
    units = [
        {"unit_id": "marker", "source_hash": "D" * 64, "source_text": "<!-- source-page-001 -->\n\n", "parent_unit_id": None, "part_index": None, "part_count": None},
        {"unit_id": "whole-heading", "source_hash": "E" * 64, "source_text": "# Reader Heading\n", "parent_unit_id": None, "part_index": None, "part_count": None},
    ]
    assert "".join(row["source_text"] for row in units) == source
    task = sealed("kb_creator.five_step_language_draft_task.v3", {"master_en": {"path": "MASTER_EN.md", **file_identity(paths["en"])}, "units": units}, digest_key="task_sha256")
    _write(paths["task"], task)
    ru_texts = ["<!-- source-page-001 -->", "# Заголовок читателя"]
    ru_rows = []
    for unit, ru_text in zip(units, ru_texts):
        ru_row = {key: unit[key] for key in ("unit_id", "source_hash", "parent_unit_id", "part_index", "part_count")}
        ru_row.update(ru_text=ru_text, ru_sha256=sha256_bytes(ru_text.encode("utf-8")))
        ru_rows.append(ru_row)
    projection = sealed("kb_creator.five_step_ru_projection.v3", {"master_en": {"path": "MASTER_EN.md", **file_identity(paths["en"])},
        "master_ru": {"path": "MASTER_RU.md", **file_identity(paths["ru"])}, "source_spans": {"path": "spans", "bytes": 1, "sha256": "0" * 64},
        "unit_order": [row["unit_id"] for row in ru_rows], "units": ru_rows, "spans": []}, digest_key="projection_sha256")
    _write(paths["projection"], projection)
    root = paths["ru"].parent
    (root / "ASSET_MANIFEST.json").write_text(json.dumps({"assets": []}), encoding="utf-8")
    for name in ("MASTER_RU.manifest.json", "PROOFREAD_LEDGER.json", "INVENTORY.json"):
        (root / name).write_text("{}", encoding="utf-8")
    semantic = root / "semantic_context"; semantic.mkdir()
    (semantic / "RU_PROJECTION.json").write_bytes(paths["projection"].read_bytes())
    options = {"schema": reader_projection.SCHEMA, "master_ru": {"path": "MASTER_RU.md", **file_identity(paths["ru"])},
               "ru_projection": {"path": "semantic_context/RU_PROJECTION.json", **file_identity(semantic / "RU_PROJECTION.json")},
               "source_toc": {"state": "absent", "source_pdf_sha256": "A" * 64, "reason": "fixture"},
               "body_links": [], "asset_choices": [], "display_roles": [], "hit_points": {"presentation": "numeric", "expected_counts": []}}
    options["options_sha256"] = reader_projection.seal(options)
    option_path = root / "reader-v2.json"; _write(option_path, options)
    derived = derive_source_issue_projection(master_en=paths["en"], master_ru=paths["ru"], ru_projection=paths["projection"],
                                             issue_en_bindings=paths["bindings"], final_evidence=paths["evidence"], language_task=paths["task"])
    monkeypatch.setattr(five_step_docx, "_verify_master_ru_input", lambda _: None)
    result = five_step_docx.build_docx_package(paths["ru"], root / "package-v2", title="Тест v2",
                                                reader_options=option_path, source_issue_projection=derived)
    package = result["manifest_path"].parent
    assert five_step_docx.verify_docx_package(package)["status"] == "verified_pending_visual_review"
    saved = json.loads((package / "SOURCE_ISSUE_RU_PROJECTION.json").read_text(encoding="utf-8"))
    assert saved["roles"][0]["raw_source_excerpt_en"] == "<sup>Reader</sup> Heading"
    with zipfile.ZipFile(package / "docx/document.docx") as archive:
        assert archive.read("word/comments.xml").count(b"heading-1") == 1


@pytest.mark.parametrize("damage", ["reader_span", "raw_source", "missing_stage05"])
def test_v2_rejects_resealed_or_missing_reader_authority(tmp_path: Path, damage: str) -> None:
    paths = _v2_fixture(tmp_path)
    bindings = json.loads(paths["bindings"].read_text(encoding="utf-8"))
    if damage == "reader_span":
        bindings["bindings"][0]["master_reader_span"]["character_start"] += 1
        _reseal(bindings, "bindings_sha256"); _write(paths["bindings"], bindings)
    elif damage == "raw_source":
        bindings["bindings"][0]["source_occurrence"]["source_excerpt"] = "forged raw source"
        _reseal(bindings, "bindings_sha256"); _write(paths["bindings"], bindings)
    else:
        evidence = json.loads(paths["evidence"].read_text(encoding="utf-8")); del evidence["authored"]["stage05_audit"]
        _write(paths["evidence"], evidence)
        bindings["final_evidence"] = {"path": str(paths["evidence"].resolve()), **file_identity(paths["evidence"])}
        _reseal(bindings, "bindings_sha256"); _write(paths["bindings"], bindings)
    with pytest.raises(SourceIssueProjectionError, match="v2|final evidence"):
        derive_source_issue_projection(master_en=paths["en"], master_ru=paths["ru"], ru_projection=paths["projection"],
                                       issue_en_bindings=paths["bindings"], final_evidence=paths["evidence"], language_task=paths["task"])


def test_requires_complete_split_parent_group(tmp_path: Path) -> None:
    paths = _fixture(tmp_path, split=True)
    result = derive_source_issue_projection(master_en=paths["en"], master_ru=paths["ru"], ru_projection=paths["projection"],
                                            issue_en_bindings=paths["bindings"], final_evidence=paths["evidence"], language_task=paths["task"])
    assert [row["unit_id"] for row in result["roles"][0]["units"]] == ["u3", "u4"]
    task = json.loads(paths["task"].read_text(encoding="utf-8")); task["units"] = task["units"][:3]
    task["task_sha256"] = sha256_bytes(json.dumps({k:v for k,v in task.items() if k != "task_sha256"}, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode())
    _write(paths["task"], task)
    with pytest.raises(SourceIssueProjectionError, match="split-parent"):
        derive_source_issue_projection(master_en=paths["en"], master_ru=paths["ru"], ru_projection=paths["projection"],
                                       issue_en_bindings=paths["bindings"], final_evidence=paths["evidence"], language_task=paths["task"])


def test_package_uses_annotated_docx_before_inventory_and_seal(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    paths = _fixture(tmp_path, split=True)
    root = paths["ru"].parent
    (root / "ASSET_MANIFEST.json").write_text(json.dumps({"assets": []}), encoding="utf-8")
    for name in ("MASTER_RU.manifest.json", "PROOFREAD_LEDGER.json", "INVENTORY.json"):
        (root / name).write_text("{}", encoding="utf-8")
    semantic = root / "semantic_context"; semantic.mkdir()
    (semantic / "RU_PROJECTION.json").write_bytes(paths["projection"].read_bytes())
    options = {"schema": reader_projection.SCHEMA,
               "master_ru": {"path": "MASTER_RU.md", **file_identity(paths["ru"])},
               "ru_projection": {"path": "semantic_context/RU_PROJECTION.json", **file_identity(semantic / "RU_PROJECTION.json")},
               "source_toc": {"state": "absent", "source_pdf_sha256": "A" * 64, "reason": "fixture"},
               "body_links": [], "asset_choices": [], "display_roles": [],
               "hit_points": {"presentation": "numeric", "expected_counts": []}}
    options["options_sha256"] = reader_projection.seal(options)
    option_path = root / "reader.json"; _write(option_path, options)
    derived = derive_source_issue_projection(master_en=paths["en"], master_ru=paths["ru"], ru_projection=paths["projection"],
                                             issue_en_bindings=paths["bindings"], final_evidence=paths["evidence"], language_task=paths["task"])
    # The source-issue route itself uses the real HTML/DOCX builder and package
    # verifier.  The compact fixture's language predecessor is deliberately
    # constructed above, so only the unrelated full language-result verifier is
    # replaced here.
    monkeypatch.setattr(five_step_docx, "_verify_master_ru_input", lambda _: None)
    result = five_step_docx.build_docx_package(paths["ru"], root / "package", title="Тест",
                                                reader_options=option_path, source_issue_projection=derived)
    package = result["manifest_path"].parent
    assert not (package / "docx/document.base.docx").exists()
    assert (package / "DOCX_REVIEW_ANNOTATION.json").is_file()
    assert five_step_docx.verify_docx_package(package)["status"] == "verified_pending_visual_review"
    with zipfile.ZipFile(package / "docx/document.docx") as archive:
        assert "word/comments.xml" in archive.namelist()
        assert archive.read("word/comments.xml").count(b"role-1") == 1


def test_package_rejects_resealed_projection_with_missing_authorities(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    paths = _fixture(tmp_path, split=True)
    root = paths["ru"].parent
    (root / "ASSET_MANIFEST.json").write_text(json.dumps({"assets": []}), encoding="utf-8")
    for name in ("MASTER_RU.manifest.json", "PROOFREAD_LEDGER.json", "INVENTORY.json"):
        (root / name).write_text("{}", encoding="utf-8")
    semantic = root / "semantic_context"; semantic.mkdir()
    (semantic / "RU_PROJECTION.json").write_bytes(paths["projection"].read_bytes())
    options = {"schema": reader_projection.SCHEMA, "master_ru": {"path": "MASTER_RU.md", **file_identity(paths["ru"])},
               "ru_projection": {"path": "semantic_context/RU_PROJECTION.json", **file_identity(semantic / "RU_PROJECTION.json")},
               "source_toc": {"state": "absent", "source_pdf_sha256": "A" * 64, "reason": "fixture"},
               "body_links": [], "asset_choices": [], "display_roles": [], "hit_points": {"presentation": "numeric", "expected_counts": []}}
    options["options_sha256"] = reader_projection.seal(options)
    option_path = root / "reader.json"; _write(option_path, options)
    derived = derive_source_issue_projection(master_en=paths["en"], master_ru=paths["ru"], ru_projection=paths["projection"],
                                             issue_en_bindings=paths["bindings"], final_evidence=paths["evidence"], language_task=paths["task"])
    monkeypatch.setattr(five_step_docx, "_verify_master_ru_input", lambda _: None)
    result = five_step_docx.build_docx_package(paths["ru"], root / "package", title="Тест", reader_options=option_path, source_issue_projection=derived)
    manifest_path = result["manifest_path"]; manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    forged = {"schema": "kb_creator.source_issue_ru_projection.v1",
              "master_en": {"path": str(root / "missing-en.md"), "bytes": 0, "sha256": "0" * 64},
              "master_ru": {"path": str(root / "MASTER_RU.md"), **file_identity(root / "MASTER_RU.md")},
              "ru_projection": {"path": str(root / "semantic_context/RU_PROJECTION.json"), **file_identity(root / "semantic_context/RU_PROJECTION.json")},
              "issue_en_bindings": {"path": str(root / "missing-issues.json"), "bytes": 0, "sha256": "0" * 64},
              "final_evidence": {"path": str(root / "missing-final.json"), "bytes": 0, "sha256": "0" * 64},
              "language_task": {"path": str(root / "missing-task.json"), "bytes": 0, "sha256": "0" * 64}, "roles": []}
    forged["projection_sha256"] = sha256_bytes(json.dumps(forged, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode())
    manifest["source_issue_projection"] = forged
    manifest["manifest_sha256"] = sha256_bytes(json.dumps({k:v for k,v in manifest.items() if k != "manifest_sha256"}, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode())
    _write(manifest_path, manifest)
    with pytest.raises(five_step_docx.FiveStepDocxError, match="authority is missing"):
        five_step_docx.verify_docx_package(manifest_path.parent)


def test_rejects_stale_en_binding_hash(tmp_path: Path) -> None:
    paths = _fixture(tmp_path)
    value = json.loads(paths["bindings"].read_text(encoding="utf-8")); value["bindings"][0]["text_sha256"] = "0" * 64
    value["bindings_sha256"] = sha256_bytes(json.dumps({k:v for k,v in value.items() if k != "bindings_sha256"}, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode())
    _write(paths["bindings"], value)
    with pytest.raises(SourceIssueProjectionError, match="span or immutable"):
        derive_source_issue_projection(master_en=paths["en"], master_ru=paths["ru"], ru_projection=paths["projection"],
                                       issue_en_bindings=paths["bindings"], final_evidence=paths["evidence"], language_task=paths["task"])


@pytest.mark.parametrize("kind", ["semantic_source_uncertainty", "editorial_choice"])
def test_projects_nonlexical_review_issue_kinds(tmp_path: Path, kind: str) -> None:
    paths = _fixture(tmp_path)
    evidence = json.loads(paths["evidence"].read_text(encoding="utf-8"))
    evidence["source_issues"]["issues"][0]["kind"] = kind
    _write(paths["evidence"], evidence)
    bindings = json.loads(paths["bindings"].read_text(encoding="utf-8"))
    bindings["final_evidence"] = {"path": str(paths["evidence"]), **file_identity(paths["evidence"])}
    bindings["bindings_sha256"] = sha256_bytes(json.dumps({k:v for k,v in bindings.items() if k != "bindings_sha256"}, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode())
    _write(paths["bindings"], bindings)
    result = derive_source_issue_projection(master_en=paths["en"], master_ru=paths["ru"], ru_projection=paths["projection"],
                                            issue_en_bindings=paths["bindings"], final_evidence=paths["evidence"], language_task=paths["task"])
    assert result["roles"][0]["issue_id"] == "role-1"
