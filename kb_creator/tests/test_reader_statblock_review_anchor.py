import hashlib
import json
import zipfile
from pathlib import Path

import pytest
from lxml import etree

from kb_creator.pipeline.docx_review_comments import annotate_docx_review
from kb_creator.pipeline.identity import sha256_file
from kb_creator.pipeline.reader_projection import project_reader_html
from kb_creator.scripts.production_docx import build_docx


TARGET = "ВЫН: 12 НАР: 14 МОЩ: 14 Проверка Удачи: 75%"


def setup(body: str, text: str = TARGET):
    units = [
        {"unit_id": "u0", "ru_text": "<!-- source-page-001 -->", "ru_sha256": hashlib.sha256(b"<!-- source-page-001 -->").hexdigest().upper()},
        {"unit_id": "u1", "ru_text": text, "ru_sha256": hashlib.sha256(text.encode()).hexdigest().upper()},
    ]
    bind = {key: units[1][key] for key in ("unit_id", "ru_sha256")}
    options = {"source_toc": {"state": "absent", "source_pdf_sha256": "A" * 64, "reason": "fixture"},
               "body_links": [], "asset_choices": [], "hit_points": {"presentation": "numeric", "expected_counts": []},
               "display_roles": [{"role": "review_anchor", "unit": bind, "target_text": TARGET,
                                  "source_evidence": "source stat line", "reason": "native review"}]}
    return {"units": units}, options


def visible_document_text(path: Path) -> str:
    with zipfile.ZipFile(path) as package:
        xml = etree.fromstring(package.read("word/document.xml"))
    return "".join(xml.xpath("//w:t/text()", namespaces={"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}))


def test_statblock_paragraph_anchor_survives_docx_and_native_comment(tmp_path: Path):
    body = ('<section data-page="001"><section class="statblock-card" data-semantic-kind="statblock">'
            f'<p>{TARGET}</p><p>Навык: Скрытность 45%</p></section></section>')
    projection, options = setup(body)
    projected, _, report = project_reader_html(body, [], projection, options)
    anchor = report["review_anchors"][0]["anchor"]
    assert f'id="{anchor}"' in projected and TARGET in projected and "Скрытность 45%" in projected

    source = tmp_path / "statblock.docx"
    html_path = tmp_path / "reader.html"
    html_path.write_text(
        '<html><head><meta charset="utf-8"></head><body><main>'
        '<nav id="toc"><h1>Содержание</h1><ol><li><a href="#chapter">Глава</a></li></ol></nav>'
        '<h1 id="chapter">Глава</h1>' + projected + '</main></body></html>', encoding="utf-8"
    )
    build_docx(html_path, source)
    before = visible_document_text(source)
    registry = tmp_path / "issues.json"
    registry.write_text(json.dumps({"schema": "kb_creator.docx_review_issues.v1", "docx_sha256": sha256_file(source), "issues": [
        {"issue_id": "stat-1", "reader_anchor": anchor, "target_text": TARGET, "reason": "Проверить характеристики", "en_excerpt": "Stat values", "source_page": 1}
    ]}, ensure_ascii=False), encoding="utf-8")
    annotated = tmp_path / "annotated.docx"
    binding = annotate_docx_review(source, registry, annotated)["bindings"][0]
    after = visible_document_text(annotated)
    assert binding["selected_text"] == TARGET
    assert before == after and TARGET in after and "Скрытность 45%" in after
    with zipfile.ZipFile(source) as before_zip, zipfile.ZipFile(annotated) as after_zip:
        assert after_zip.read("word/document.xml").count(b"w:pStyle") == before_zip.read("word/document.xml").count(b"w:pStyle")
        assert b"NRI Statblock" in before_zip.read("word/styles.xml")


@pytest.mark.parametrize("kind", ["callout", "table"])
def test_review_anchor_rejects_table_or_unsupported_semantic_kind(kind: str):
    body = (f'<section data-page="001"><section data-semantic-kind="{kind}"><p>{TARGET}</p></section></section>'
            if kind == "callout" else f'<section data-page="001"><table><tr><td><p>{TARGET}</p></td></tr></table></section>')
    projection, options = setup(body)
    with pytest.raises(ValueError, match="plain rendered paragraph"):
        project_reader_html(body, [], projection, options)


@pytest.mark.parametrize("target", ["Отсутствует", TARGET])
def test_review_anchor_rejects_missing_or_ambiguous_statblock_target(target: str):
    paragraphs = f"<p>{TARGET}</p>" if target == "Отсутствует" else f"<p>{TARGET}</p><p>{TARGET}</p>"
    body = f'<section data-page="001"><section data-semantic-kind="statblock">{paragraphs}</section></section>'
    projection, options = setup(body)
    options["display_roles"][0]["target_text"] = target
    with pytest.raises(ValueError, match="absent or ambiguous|exact HTML matches"):
        project_reader_html(body, [], projection, options)


def test_review_anchor_plain_paragraph_route_remains_supported():
    body = f'<section data-page="001"><p>{TARGET}</p></section>'
    projection, options = setup(body)
    projected, _, report = project_reader_html(body, [], projection, options)
    assert report["review_anchors"][0]["anchor"] in projected
