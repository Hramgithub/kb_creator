import hashlib
import zipfile
from pathlib import Path

import pytest
from lxml import etree, html
from PIL import Image

from kb_creator.pipeline.reader_projection import project_reader_html
from kb_creator.scripts.production_docx import build_docx
from translator.translator import markdown_to_review_html


def setup(texts):
    units = [{"unit_id": f"u{index}", "ru_text": text,
              "ru_sha256": hashlib.sha256(text.encode()).hexdigest().upper()}
             for index, text in enumerate(texts)]
    bind = lambda index: {key: units[index][key] for key in ("unit_id", "ru_sha256")}
    body, toc, _ = markdown_to_review_html("\n\n".join(texts), source_path=Path("x.md"), html_path=Path("x.html"))
    options = {"source_toc": {"state": "absent", "source_pdf_sha256": "A" * 64, "reason": "reviewed"},
               "body_links": [], "display_roles": [], "asset_choices": [],
               "hit_points": {"presentation": "numeric", "expected_counts": []}}
    return body, toc, {"units": units}, options, bind


def legend(bind, index):
    return {"role": "asset_legend", "unit": bind(index), "title": "Ключ к карте",
            "entries": [{"source": "Kitchen", "translation": "Кухня"}, {"source": "N", "translation": "Север"}],
            "source_evidence": "reviewed source map", "reason": "reader accessibility key"}


def test_asset_legend_retains_original_figure_and_adds_plain_two_column_key():
    body, toc, projection, options, bind = setup([
        "<!-- source-page-001 -->", "![Map](map.png)", "После карты.",
    ])
    decision = legend(bind, 1)
    options["display_roles"] = [decision]

    out, _, report = project_reader_html(body, toc, projection, options)
    tree = html.fragment_fromstring(out, create_parent="main")
    figure = tree.xpath('.//figure[img[@src="map.png"]]')[0]
    key = figure.getnext()
    assert key.tag == "div" and key.get("class") == "asset-legend"
    assert key.text_content() == "Ключ к картеНа картеПо-русскиKitchenКухняNСевер"
    assert [cell.text for cell in key.xpath(".//tbody/tr/td")] == ["Kitchen", "Кухня", "N", "Север"]
    assert report["asset_legends"] == [{**decision, "source_reference": "map.png"}]


@pytest.mark.parametrize("damage", ["stale", "empty", "duplicate", "ambiguous", "omission_conflict"])
def test_asset_legend_rejects_bad_or_conflicting_decisions(damage):
    texts = ["<!-- source-page-001 -->", "![Map](map.png)", "После карты."]
    if damage == "ambiguous":
        texts = ["<!-- source-page-001 -->", "![Map](map.png)", "![Map](map.png)"]
    body, toc, projection, options, bind = setup(texts)
    decision = legend(bind, 1)
    if damage == "stale":
        decision["unit"]["ru_sha256"] = "0" * 64
    if damage == "empty":
        decision["entries"][0]["translation"] = ""
    if damage == "duplicate":
        decision["entries"][1]["source"] = "Kitchen"
    if damage == "omission_conflict":
        options["display_roles"] = [decision, {"role": "omit_source_artifact", "unit": bind(1),
                                                "classification": "ornamental_page_number", "source_evidence": "reviewed", "reason": "fixture"}]
    else:
        options["display_roles"] = [decision]
    with pytest.raises(ValueError, match="preimage|entries|exact HTML matches|conflicts"):
        project_reader_html(body, toc, projection, options)


def test_asset_legend_survives_tiny_native_docx_build_with_table_and_russian_labels(tmp_path: Path):
    body, toc, projection, options, bind = setup([
        "<!-- source-page-001 -->", "![Map](assets/map.png)", "После карты.",
    ])
    options["display_roles"] = [legend(bind, 1)]
    projected, _, _ = project_reader_html(body, toc, projection, options)
    assets = tmp_path / "assets"; assets.mkdir()
    Image.new("RGB", (12, 8), "white").save(assets / "map.png")
    source = tmp_path / "reader.html"
    source.write_text(
        '<html><head><meta charset="utf-8"></head><body><main>'
        '<nav id="toc"><h1>Содержание</h1><ol><li><a href="#chapter">Глава</a></li></ol></nav>'
        '<h1 id="chapter">Глава</h1>' + projected + '</main></body></html>', encoding="utf-8"
    )
    output = tmp_path / "reader.docx"
    build_docx(source, output)
    with zipfile.ZipFile(output) as package:
        xml = etree.fromstring(package.read("word/document.xml"))
    ns = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}
    visible = "".join(xml.xpath("//w:t/text()", namespaces=ns))
    assert "Ключ к карте" in visible and "На карте" in visible and "По-русски" in visible
    assert "Kitchen" in visible and "Кухня" in visible
    assert len(xml.xpath("//w:tbl", namespaces=ns)) >= 2
