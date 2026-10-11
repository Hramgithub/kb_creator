from __future__ import annotations

from lxml import etree, html
import pytest
import hashlib
import zipfile
from pathlib import Path

from kb_creator.pipeline.five_step_docx import FiveStepDocxError, verify_rich_source_toc_docx
from kb_creator.pipeline.reader_projection import project_reader_html
from kb_creator.scripts.production_docx import build_docx
from translator.translator import markdown_to_review_html


XML = b'''<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"><w:body><w:tbl><w:tr><w:tc>
<w:p><w:hyperlink w:anchor="one"><w:r><w:t>Title One</w:t></w:r></w:hyperlink></w:p><w:p><w:r><w:t>Byline One</w:t></w:r></w:p><w:p><w:r><w:t>Synopsis One</w:t></w:r></w:p>
</w:tc><w:tc><w:p><w:hyperlink w:anchor="two"><w:r><w:t>Title Two</w:t></w:r></w:hyperlink></w:p><w:p><w:r><w:t>Byline Two</w:t></w:r></w:p><w:p><w:r><w:t>Synopsis Two</w:t></w:r></w:p></w:tc></w:tr></w:tbl></w:body></w:document>'''


def report():
    return {"rich_source_toc": {"entry_count": 2, "display_rows": [
        {"title": "Title One", "byline": "Byline One", "synopsis": "Synopsis One"},
        {"title": "Title Two", "byline": "Byline Two", "synopsis": "Synopsis Two"},
    ], "omitted_display": ["Old duplicate"]}}


def test_rich_docx_closure_accepts_title_only_hyperlinks():
    verify_rich_source_toc_docx(report(), XML)


def test_rich_docx_closure_allows_default_empty_second_cell_for_one_entry():
    one = XML.replace(b'<w:tc><w:p><w:hyperlink w:anchor="two"><w:r><w:t>Title Two</w:t></w:r></w:hyperlink></w:p><w:p><w:r><w:t>Byline Two</w:t></w:r></w:p><w:p><w:r><w:t>Synopsis Two</w:t></w:r></w:p></w:tc>', b'<w:tc><w:p/></w:tc>')
    value = report(); value["rich_source_toc"]["entry_count"] = 1; value["rich_source_toc"]["display_rows"] = value["rich_source_toc"]["display_rows"][:1]
    verify_rich_source_toc_docx(value, one)


def rich_case(tmp_path: Path):
    texts = [
        "<!-- source-page-001 -->", "# Содержание", "## Спилсбери № *9485*",
        "Автор: **Иван** . . . 12", "Синопсис с *эмфазой*.", "Автор: Иван . . . 12",
        "<!-- source-page-002 -->", "## Второй заголовок", "Автор: **Анна** 14", "Второй *синопсис*.",
        "<!-- source-page-003 -->", "## Цель один", "## Цель два",
    ]
    units = [{"unit_id": f"u{n}", "ru_text": text,
              "ru_sha256": hashlib.sha256(text.encode()).hexdigest().upper()} for n, text in enumerate(texts)]
    def node(n, ordinal=0): return {"unit_id": units[n]["unit_id"], "ru_sha256": units[n]["ru_sha256"], "match_ordinal": ordinal}
    def component(n, rendered, suffix=None):
        return {"node": node(n), "source_markdown": texts[n], "rendered_markdown": rendered, "page_suffix_removal": suffix}
    removal12 = {"operation": "remove_exact_terminal_printed_page_suffix", "source_suffix": " . . . 12", "printed_page": 12, "reason": "source page"}
    removal14 = {"operation": "remove_exact_terminal_printed_page_suffix", "source_suffix": " 14", "printed_page": 14, "reason": "source page"}
    options = {"source_toc": {"state": "present", "source_pdf_sha256": "A" * 64, "reason": "fixture", "presentation": {
        "schema": "kb_creator.source_toc_presentation.rich_entries.v1", "heading": {"node": node(1), "source_markdown": texts[1]},
        "entries": [
            {"entry_id": "one", "source_page": 1, "title": {"node": node(2), "source_markdown": texts[2], "target": node(11), "level": 1}, "byline": component(3, "Автор: **Иван**", removal12), "synopsis": {"node": node(4), "source_markdown": texts[4]}},
            {"entry_id": "two", "source_page": 2, "title": {"node": node(7), "source_markdown": texts[7], "target": node(12), "level": 1}, "byline": component(8, "Автор: **Анна**", removal14), "synopsis": {"node": node(9), "source_markdown": texts[9]}},
        ], "duplicate_byline_omissions": [{"node": node(5, 1), "source_markdown": texts[5], "page_suffix_removal": removal12, "duplicate_of_entry_id": "one", "reason": "duplicate", "source_evidence": "fixture"}]
    }}, "body_links": [], "display_roles": [], "asset_choices": [], "hit_points": {"presentation": "numeric", "expected_counts": []}}
    body, toc, _ = markdown_to_review_html("\n\n".join(texts), source_path=tmp_path / "source.md", html_path=tmp_path / "source.html")
    return body, toc, {"units": units}, options


@pytest.mark.parametrize("entry_count", [1, 2])
def test_two_page_cyrillic_rich_toc_projects_to_docx_and_closes(tmp_path: Path, entry_count):
    body, toc, projection, options = rich_case(tmp_path)
    options["source_toc"]["presentation"]["entries"] = options["source_toc"]["presentation"]["entries"][:entry_count]
    output, effective, report = project_reader_html(body, toc, projection, options)
    assert len(html.fragment_fromstring(output, create_parent="main").xpath(".//nav")) == 1
    assert [row["title"] for row in effective] == ["Спилсбери № 9485", "Второй заголовок"][:entry_count]
    assert " . . . 12" not in output and "<strong>Иван</strong>" in output and "<em>эмфазой</em>" in output
    html_path = tmp_path / "rich.html"; html_path.write_text("<html><head><meta charset=\"utf-8\"></head><body><main>" + output + "</main></body></html>", encoding="utf-8")
    docx_path = tmp_path / "rich.docx"; result = build_docx(html_path, docx_path)
    assert result["toc_entries"] == entry_count
    with zipfile.ZipFile(docx_path) as archive: xml = archive.read("word/document.xml")
    verify_rich_source_toc_docx(report, xml)
    document = etree.fromstring(xml)
    ns = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}
    assert document.xpath(".//w:tbl//w:r[w:t='Иван']/w:rPr/w:b", namespaces=ns)
    assert document.xpath(".//w:tbl//w:r[w:t='эмфазой']/w:rPr/w:i", namespaces=ns)
    assert document.xpath(".//w:tbl//w:hyperlink//w:r[w:t='9485']/w:rPr/w:i", namespaces=ns)


@pytest.mark.parametrize("stale", [False, True])
def test_rich_target_ordinal_uses_final_projection_order(tmp_path, stale):
    _, _, projection, options = rich_case(tmp_path)
    for index, ordinal in ((11, 0), (12, 1)):
        unit = projection["units"][index]
        unit["ru_text"] = "## Одинаковое название"
        unit["ru_sha256"] = hashlib.sha256(unit["ru_text"].encode()).hexdigest().upper()
        target = options["source_toc"]["presentation"]["entries"][ordinal]["title"]["target"]
        target.update(ru_sha256=unit["ru_sha256"], match_ordinal=ordinal)
    if stale:
        options["source_toc"]["presentation"]["entries"][1]["title"]["target"]["match_ordinal"] = 0
    body, toc, _ = markdown_to_review_html("\n\n".join(unit["ru_text"] for unit in projection["units"]), source_path=tmp_path/"source.md", html_path=tmp_path/"source.html")
    if stale:
        with pytest.raises(ValueError, match="ordinal"):
            project_reader_html(body, toc, projection, options)
    else:
        _, effective, _ = project_reader_html(body, toc, projection, options)
        assert effective[0]["href"] != effective[1]["href"]


@pytest.mark.parametrize("mutation", [
    "interstitial_paragraph", "interstitial_table", "reordered_components", "stale_hash",
    "stale_ordinal", "wrong_page", "duplicate_entry_id", "duplicate_target", "wrong_suffix_page",
    "suffix_removes_name", "extra_byline_edit", "missing_synopsis", "synopsis_extra_fields",
    "omission_missing_evidence", "omission_not_page_end", "title_boolean_level",
])
def test_rich_projection_rejects_invalid_source_bindings(tmp_path, mutation):
    body, toc, projection, options = rich_case(tmp_path)
    presentation = options["source_toc"]["presentation"]
    first, second = presentation["entries"]
    if mutation.startswith("interstitial") or mutation == "reordered_components":
        tree = html.fragment_fromstring(body, create_parent="main")
        byline = tree.xpath(".//section[@data-page='001']/p")[0]
        if mutation == "interstitial_table":
            byline.addnext(html.fragment_fromstring("<table><tr><td>UNDECLARED</td></tr></table>"))
        elif mutation == "interstitial_paragraph":
            byline.addnext(html.fragment_fromstring("<p>UNDECLARED</p>"))
        else:
            synopsis = byline.getnext()
            byline.addprevious(synopsis)
        body = "".join(html.tostring(child, encoding="unicode") for child in tree)
    elif mutation == "stale_hash": first["title"]["node"]["ru_sha256"] = "B" * 64
    elif mutation == "stale_ordinal": presentation["duplicate_byline_omissions"][0]["node"]["match_ordinal"] = 0
    elif mutation == "wrong_page": first["source_page"] = 2
    elif mutation == "duplicate_entry_id": second["entry_id"] = first["entry_id"]
    elif mutation == "duplicate_target": second["title"]["target"] = first["title"]["target"]
    elif mutation == "wrong_suffix_page": first["byline"]["page_suffix_removal"]["printed_page"] = 13
    elif mutation == "suffix_removes_name":
        first["byline"]["page_suffix_removal"]["source_suffix"] = "**Иван** . . . 12"
        first["byline"]["rendered_markdown"] = "Автор:"
    elif mutation == "extra_byline_edit": first["byline"]["rendered_markdown"] = "Автор: Пётр"
    elif mutation == "missing_synopsis": del first["synopsis"]
    elif mutation == "synopsis_extra_fields": first["synopsis"]["page_suffix_removal"] = None
    elif mutation == "omission_missing_evidence": presentation["duplicate_byline_omissions"][0]["source_evidence"] = ""
    elif mutation == "omission_not_page_end":
        body = body.replace("Автор: Иван . . . 12</p>", "Автор: Иван . . . 12</p><p>EXTRA AFTER DUPLICATE</p>")
    elif mutation == "title_boolean_level": first["title"]["level"] = True
    with pytest.raises(ValueError):
        project_reader_html(body, toc, projection, options)


@pytest.mark.parametrize("mutate", ["metadata_link", "missing_text", "omitted_present"])
def test_rich_docx_closure_rejects_invalid_projection(mutate):
    xml = XML
    value = report()
    if mutate == "metadata_link":
        xml = xml.replace(b"<w:p><w:r><w:t>Byline One", b"<w:p><w:hyperlink w:anchor=\"one\"><w:r><w:t>Byline One").replace(b"</w:t></w:r></w:p><w:p><w:r><w:t>Synopsis One", b"</w:t></w:r></w:hyperlink></w:p><w:p><w:r><w:t>Synopsis One")
    elif mutate == "missing_text":
        value["rich_source_toc"]["display_rows"][0]["synopsis"] = "Changed"
    else:
        xml = xml.replace(b"</w:body>", b"<w:p><w:r><w:t>Old duplicate</w:t></w:r></w:p></w:body>")
    with pytest.raises(FiveStepDocxError):
        verify_rich_source_toc_docx(value, xml)
