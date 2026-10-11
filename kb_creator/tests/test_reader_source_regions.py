import hashlib
import zipfile
from pathlib import Path

import pytest
from lxml import etree, html
from PIL import Image

from kb_creator.pipeline.five_step_docx import _default_config, _reader_image_occurrences
from kb_creator.pipeline.reader_projection import copy_reader_assets, identity, project_reader_html
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


def region(region_id: str, selected: Path, crop: dict):
    return {"id": region_id, "selected_ref": f"regions/{selected.name}", "selected": identity(selected),
            "caption": f"Регион {region_id}",
            "figure_policy": {"max_width_mm": 90, "max_height_mm": 60, "keep_with_next": True,
                              "crop_fraction": crop}}


def decision(bind, selected: Path, *, classification="text_with_retained_art", regions=None):
    return {"role": "source_figure_regions", "unit": bind(1), "retained_text_units": [bind(2)],
            "after_unit": bind(2), "classification": classification,
            "regions": regions if regions is not None else [
                region("left", selected, {"left": 0, "top": 0, "right": 0.5, "bottom": 0}),
                region("right", selected, {"left": 0.5, "top": 0, "right": 0, "bottom": 0}),
            ], "source_evidence": "source page reviewed", "reason": "Russian text replaces English handout"}


def test_source_regions_copy_native_bytes_project_crops_and_keep_ru_text(tmp_path: Path):
    body, toc, projection, options, bind = setup([
        "<!-- source-page-001 -->", "![English note](assets/handout.png)", "Русский перевод записки.",
    ])
    selections = tmp_path / "regions"; selections.mkdir()
    selected = selections / "note.png"
    Image.new("RGB", (20, 10), "white").save(selected)
    options["display_roles"] = [decision(bind, selected)]

    projected, _, report = project_reader_html(body, toc, projection, options)
    tree = html.fragment_fromstring(projected, create_parent="main")
    assert not tree.xpath('.//img[@src="assets/handout.png"]')
    assert tree.xpath('.//p[text()="Русский перевод записки."]')
    assert [node.get("src") for node in tree.xpath('.//div[@class="source-figure-regions"]//img')] == [
        "assets/reader/source-regions/left-note.png", "assets/reader/source-regions/right-note.png",
    ]
    assert _reader_image_occurrences(1, report) == 2

    stage = tmp_path / "stage"; (stage / "assets").mkdir(parents=True)
    (stage / "assets" / "handout.png").write_bytes(selected.read_bytes())
    profile = copy_reader_assets(report, tmp_path / "reader-options.json", stage, _default_config("Тест"))
    assert all(identity(stage / row["rendered_path"]) == row["selected"]
               for row in report["source_figure_regions"][0]["regions"])
    source = stage / "reader.html"
    source.write_text(
        '<html><head><meta charset="utf-8"></head><body><main>'
        '<nav id="toc"><h1>Содержание</h1><ol><li><a href="#chapter">Глава</a></li></ol></nav>'
        '<h1 id="chapter">Глава</h1>' + projected + '</main></body></html>', encoding="utf-8"
    )
    output = stage / "reader.docx"
    result = build_docx(source, output, config=profile)
    assert result["images"] == 2
    with zipfile.ZipFile(output) as package:
        xml = etree.fromstring(package.read("word/document.xml"))
        media = {hashlib.sha256(package.read(name)).hexdigest().upper()
                 for name in package.namelist() if name.startswith("word/media/")}
    assert identity(selected)["sha256"] in media
    ns = {"a": "http://schemas.openxmlformats.org/drawingml/2006/main"}
    assert {(node.get("l", "0"), node.get("t", "0"), node.get("r", "0"), node.get("b", "0"))
            for node in xml.xpath("//a:srcRect", namespaces=ns)} == {("0", "0", "50000", "0"), ("50000", "0", "0", "0")}


def test_translated_text_only_removes_source_occurrence_without_regions(tmp_path: Path):
    body, toc, projection, options, bind = setup([
        "<!-- source-page-001 -->", "![English note](assets/handout.png)", "Русский перевод записки.",
    ])
    selected = tmp_path / "unused.png"; Image.new("RGB", (2, 2), "white").save(selected)
    options["display_roles"] = [decision(bind, selected, classification="translated_text_only", regions=[])]
    projected, _, report = project_reader_html(body, toc, projection, options)
    assert not html.fragment_fromstring(projected, create_parent="main").xpath(".//img")
    assert _reader_image_occurrences(1, report) == 0


def test_source_regions_reject_stale_selected_source_bytes_during_copy(tmp_path: Path):
    body, toc, projection, options, bind = setup([
        "<!-- source-page-001 -->", "![English note](assets/handout.png)", "Русский перевод записки.",
    ])
    selections = tmp_path / "regions"; selections.mkdir()
    selected = selections / "note.png"; Image.new("RGB", (4, 4), "white").save(selected)
    options["display_roles"] = [decision(bind, selected)]
    _, _, report = project_reader_html(body, toc, projection, options)
    Image.new("RGB", (4, 4), "black").save(selected)
    with pytest.raises(ValueError, match="changed while copying"):
        copy_reader_assets(report, tmp_path / "reader-options.json", tmp_path / "stage", _default_config("Тест"))


@pytest.mark.parametrize("damage", ["stale", "missing_retained", "asset_conflict", "wrong_classification", "duplicate_source"])
def test_source_regions_reject_unbound_or_conflicting_coverage(tmp_path: Path, damage: str):
    body, toc, projection, options, bind = setup([
        "<!-- source-page-001 -->", "![English note](assets/handout.png)", "Русский перевод записки.",
    ])
    selected = tmp_path / "note.png"; Image.new("RGB", (4, 4), "white").save(selected)
    item = decision(bind, selected)
    if damage == "stale":
        item["unit"]["ru_sha256"] = "0" * 64
    elif damage == "missing_retained":
        item["retained_text_units"] = [bind(1)]
    elif damage == "asset_conflict":
        options["asset_choices"] = [{"original_ref": "assets/handout.png"}]
    elif damage == "wrong_classification":
        item["classification"] = "translated_text_only"
    options["display_roles"] = [item, item] if damage == "duplicate_source" else [item]
    with pytest.raises(ValueError, match="preimage|retained|conflicts|classification|distinct"):
        project_reader_html(body, toc, projection, options)
