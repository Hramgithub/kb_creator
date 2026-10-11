"""Structural source questions select exact unit-local reader blocks."""
import copy
import hashlib
import json
import zipfile
from pathlib import Path

import pytest
from lxml import etree, html
from PIL import Image

from kb_creator.pipeline.reader_projection import project_reader_html
from kb_creator.pipeline.docx_review_comments import annotate_docx_review
from kb_creator.pipeline.identity import sha256_file
from kb_creator.scripts.production_docx import build_docx
from translator.translator import markdown_to_review_html


def fixture(text):
    texts = ["<!-- source-page-001 -->", text]
    units = [{"unit_id": f"u{i}", "ru_text": value,
              "ru_sha256": hashlib.sha256(value.encode()).hexdigest().upper()}
             for i, value in enumerate(texts)]
    decision = {"role": "source_issue_review_anchor", "issue_id": "role-1",
                "unit": {key: units[1][key] for key in ("unit_id", "ru_sha256")},
                "source_page": 1, "en_excerpt": "Source role text",
                "source_evidence": "sealed EN/RU binding fixture", "reason": "Проверить оформление",
                "placement": "first_visible_text_block_v1"}
    options = {"source_toc": {"state": "absent", "source_pdf_sha256": "A" * 64, "reason": "fixture"},
               "body_links": [], "asset_choices": [], "display_roles": [decision],
               "hit_points": {"presentation": "numeric", "expected_counts": []}}
    body, toc, _ = markdown_to_review_html("\n\n".join(texts), source_path=Path("x.md"), html_path=Path("x.html"))
    return body, toc, {"units": units}, options


@pytest.mark.parametrize("text,tag,target", [
    ("## Заголовок", "h2", "Заголовок"),
    ("Проверить **этот** абзац.", "p", "Проверить этот абзац."),
    ("| Имя | Значение |\n| --- | --- |\n| Навык | 40% |", "th", "Имя"),
    ("> Цитата.", "p", "Цитата."),
])
def test_first_reader_block_is_exact_and_allows_colocated_issues(text, tag, target):
    body, toc, projection, options = fixture(text)
    second = copy.deepcopy(options["display_roles"][0]); second["issue_id"] = "role-2"
    options["display_roles"].append(second)
    original = copy.deepcopy(projection)
    out, _, report = project_reader_html(body, toc, projection, options)
    rows = report["review_anchors"]
    assert [row["issue_id"] for row in rows] == ["role-1", "role-2"]
    assert rows[0]["anchor"] == rows[1]["anchor"]
    assert rows[0]["target_text"] == rows[1]["target_text"] == target
    tree = html.fragment_fromstring(out, create_parent="main")
    nodes = tree.xpath('.//*[@id=$anchor]', anchor=rows[0]["anchor"])
    assert len(nodes) == 1 and nodes[0].tag == tag
    assert projection == original


@pytest.mark.parametrize("damage", ["stale", "page", "duplicate", "unknown", "blank", "placement"])
def test_source_issue_anchor_fails_closed(damage):
    body, toc, projection, options = fixture("Проверить этот абзац.")
    row = options["display_roles"][0]
    if damage == "stale": row["unit"]["ru_sha256"] = "0" * 64
    elif damage == "page": row["source_page"] = 2
    elif damage == "duplicate": options["display_roles"].append(copy.deepcopy(row))
    elif damage == "unknown": row["extra"] = True
    elif damage == "blank": row["source_evidence"] = " "
    else: row["placement"] = "nearest_heading"
    with pytest.raises(ValueError):
        project_reader_html(body, toc, projection, options)


def test_repeated_unit_text_on_same_page_is_not_guessed():
    body, toc, projection, options = fixture("Повтор.")
    body = body.replace("<p>Повтор.</p>", "<p>Повтор.</p><p>Повтор.</p>")
    with pytest.raises(ValueError, match="exact HTML matches"):
        project_reader_html(body, toc, projection, options)


def test_hidden_unit_is_not_a_comment_target():
    body, toc, projection, options = fixture("Скрыто.")
    body = body.replace("<p>Скрыто.</p>", '<p hidden="hidden">Скрыто.</p>')
    with pytest.raises(ValueError, match="no visible"):
        project_reader_html(body, toc, projection, options)


@pytest.mark.parametrize("text", [
    "## Заголовок",
    "Проверить **этот** абзац.",
    "| Имя | Значение |\n| --- | --- |\n| Навык | 40% |",
    "> Цитата.",
    "![Подпись](figure.png)",
])
def test_colocated_native_comments_survive_actual_docx_build(tmp_path, text):
    body, toc, projection, options = fixture(text)
    second = copy.deepcopy(options["display_roles"][0]); second["issue_id"] = "role-2"
    options["display_roles"].append(second)
    # The explicit wrapper below supplies the fixture TOC for every case.
    out, _, report = project_reader_html(body, [], projection, options)
    Image.new("RGB", (30, 20), "white").save(tmp_path / "figure.png")
    source_html = tmp_path / "reader.html"
    source_html.write_text(
        '<html><head><meta charset="utf-8"></head><body><main>'
        '<nav id="toc"><h1>Содержание</h1><ol><li><a href="#chapter">Глава</a></li></ol></nav>'
        '<h1 id="chapter">Глава</h1>' + out + '</main></body></html>', encoding="utf-8")
    base = tmp_path / "base.docx"
    build_docx(source_html, base)
    registry = tmp_path / "issues.json"
    registry.write_text(json.dumps({"schema": "kb_creator.docx_review_issues.v1",
        "docx_sha256": sha256_file(base), "issues": [
            {"issue_id": row["issue_id"], "reader_anchor": row["anchor"],
             "target_text": row["target_text"], "source_page": row["source_page"],
             "en_excerpt": row["en_excerpt"], "reason": row["reason"]}
            for row in report["review_anchors"]]}, ensure_ascii=False), encoding="utf-8")
    final = tmp_path / "annotated.docx"
    result = annotate_docx_review(base, registry, final)
    assert [row["issue_id"] for row in result["bindings"]] == ["role-1", "role-2"]
    ns = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}
    with zipfile.ZipFile(base) as before, zipfile.ZipFile(final) as after:
        original = etree.fromstring(before.read("word/document.xml"))
        actual = etree.fromstring(after.read("word/document.xml"))
        comments = etree.fromstring(after.read("word/comments.xml"))
        assert original.xpath("//w:t/text()", namespaces=ns) == actual.xpath("//w:t/text()", namespaces=ns)
        expected_ids = {str(row["comment_id"]) for row in result["bindings"]}
        for path in ("//w:commentRangeStart/@w:id", "//w:commentRangeEnd/@w:id", "//w:commentReference/@w:id"):
            ids = actual.xpath(path, namespaces=ns)
            assert len(ids) == 2 and set(ids) == expected_ids
        assert set(comments.xpath("//w:comment/@w:id", namespaces=ns)) == expected_ids
