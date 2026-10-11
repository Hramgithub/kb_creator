import hashlib
from pathlib import Path

import pytest
from lxml import html

from kb_creator.pipeline.five_step_docx import FiveStepDocxError, _reader_image_occurrences
from kb_creator.pipeline.reader_projection import project_reader_html
from translator.translator import markdown_to_review_html


def setup(texts):
    units = [{"unit_id": f"u{index}", "ru_text": text,
              "ru_sha256": hashlib.sha256(text.encode()).hexdigest().upper()}
             for index, text in enumerate(texts)]
    bind = lambda index: {key: units[index][key] for key in ("unit_id", "ru_sha256")}
    body, toc, _ = markdown_to_review_html("\n\n".join(texts), source_path=Path("x.md"), html_path=Path("x.html"))
    options = {"source_toc": {"state": "absent", "source_pdf_sha256": "A" * 64, "reason": "reviewed source"},
               "body_links": [], "display_roles": [], "asset_choices": [],
               "hit_points": {"presentation": "numeric", "expected_counts": []}}
    return body, toc, {"units": units}, options, bind


def omission(bind, index, *, classification="ornamental_page_number", retained=None):
    result = {"role": "omit_source_artifact", "unit": bind(index), "classification": classification,
              "source_evidence": "reviewed source page", "reason": "reader-only reviewed omission"}
    if retained is not None:
        result["retained_image_reference"] = retained
    return result


def test_omitted_artifact_is_removed_only_from_reader_and_is_reported_exactly():
    body, toc, projection, options, bind = setup([
        "<!-- source-page-001 -->", "![Old folio](old.png)", "![Retained cover](cover.png)", "Текст.",
    ])
    options["display_roles"] = [omission(bind, 1)]

    out, _, report = project_reader_html(body, toc, projection, options)
    tree = html.fragment_fromstring(out, create_parent="main")
    assert not tree.xpath('.//img[@src="old.png"]')
    assert len(tree.xpath('.//img[@src="cover.png"]')) == 1
    assert report["omitted_artifacts"] == [{**options["display_roles"][0], "source_reference": "old.png", "image_occurrences": 1}]


def test_duplicate_text_omission_removes_only_the_exact_plain_text_unit():
    body, toc, projection, options, bind = setup([
        "<!-- source-page-001 -->", "eSHARAM", "![Retained cover](cover.png)", "Текст.",
    ])
    options["display_roles"] = [omission(
        bind, 1, classification="duplicate_text_represented_by_retained_artwork", retained="cover.png"
    )]

    out, _, report = project_reader_html(body, toc, projection, options)
    tree = html.fragment_fromstring(out, create_parent="main")
    assert not tree.xpath('.//p[text()="eSHARAM"]')
    assert len(tree.xpath('.//img[@src="cover.png"]')) == 1
    assert report["omitted_artifacts"][0]["source_reference"] is None
    assert report["omitted_artifacts"][0]["image_occurrences"] == 0


@pytest.mark.parametrize("damage", ["stale", "duplicate", "structural", "missing_retained", "replacement", "link_target"])
def test_omitted_artifact_rejects_unbound_or_conflicting_routes(damage):
    texts = ["<!-- source-page-001 -->", "![Old folio](old.png)", "![Retained cover](cover.png)", "Ссылка."]
    if damage == "structural":
        texts[1] = "Текст рядом с ![Old folio](old.png)"
    if damage == "missing_retained":
        texts[1] = "eSHARAM"
    body, toc, projection, options, bind = setup(texts)
    decision = omission(bind, 1)
    if damage == "stale":
        decision["unit"]["ru_sha256"] = "0" * 64
    if damage == "missing_retained":
        decision = omission(bind, 1, classification="duplicate_text_represented_by_retained_artwork", retained="missing.png")
    options["display_roles"] = [decision, decision] if damage == "duplicate" else [decision]
    if damage == "replacement":
        options["asset_choices"] = [{"original_ref": "old.png"}]
    if damage == "link_target":
        options["body_links"] = [{"unit": bind(3), "target": bind(1), "text": "Ссылка", "label": "Ссылка", "reason": "fixture"}]
    with pytest.raises(ValueError, match="preimage|distinct|image-only|plain-text|conflicts"):
        project_reader_html(body, toc, projection, options)


def test_duplicate_text_omission_rejects_an_image_or_structured_text_unit():
    body, toc, projection, options, bind = setup([
        "<!-- source-page-001 -->", "![Old folio](old.png)", "![Retained cover](cover.png)",
    ])
    options["display_roles"] = [omission(
        bind, 1, classification="duplicate_text_represented_by_retained_artwork", retained="cover.png"
    )]
    with pytest.raises(ValueError, match="plain-text"):
        project_reader_html(body, toc, projection, options)


def test_reused_source_image_is_omitted_by_exact_unit_occurrence_not_asset_reference():
    body, toc, projection, options, bind = setup([
        "<!-- source-page-001 -->", "![Old folio](old.png)",
        "<!-- source-page-002 -->", "![Old folio](old.png)",
    ])
    options["display_roles"] = [omission(bind, 1)]
    out, _, report = project_reader_html(body, toc, projection, options)
    assert len(html.fragment_fromstring(out, create_parent="main").xpath('.//img[@src="old.png"]')) == 1
    assert _reader_image_occurrences(2, report) == 1

    options["display_roles"] = [omission(bind, 1), omission(bind, 3)]
    out, _, report = project_reader_html(body, toc, projection, options)
    assert not html.fragment_fromstring(out, create_parent="main").xpath('.//img[@src="old.png"]')
    assert [row["source_reference"] for row in report["omitted_artifacts"]] == ["old.png", "old.png"]
    assert _reader_image_occurrences(2, report) == 0


def test_review_anchor_binds_the_one_target_paragraph_inside_a_blockquote():
    body, toc, projection, options, bind = setup([
        "<!-- source-page-001 -->", "> Первый абзац.\n>\n> Второй **целевой** абзац.", "После цитаты.",
    ])
    decision = {"role": "review_anchor", "unit": bind(1), "target_text": "Второй целевой абзац.",
                "source_evidence": "reviewed source page", "reason": "native comment target"}
    options["display_roles"] = [decision]

    out, _, report = project_reader_html(body, toc, projection, options)
    tree = html.fragment_fromstring(out, create_parent="main")
    anchor = report["review_anchors"][0]["anchor"]
    paragraph = tree.xpath('.//p[@id=$anchor]', anchor=anchor)
    assert len(paragraph) == 1 and paragraph[0].text_content() == decision["target_text"]
    assert len(paragraph[0].xpath(".//strong")) == 1


@pytest.mark.parametrize("target", ["Нет такого текста.", "Повтор"])
def test_review_anchor_rejects_absent_or_ambiguous_target(target):
    body, toc, projection, options, bind = setup([
        "<!-- source-page-001 -->", "> Повтор\n>\n> Повтор", "После цитаты.",
    ])
    options["display_roles"] = [{"role": "review_anchor", "unit": bind(1), "target_text": target,
                                  "source_evidence": "reviewed", "reason": "fixture"}]
    with pytest.raises(ValueError, match="absent or ambiguous"):
        project_reader_html(body, toc, projection, options)


def test_reader_image_count_closure_uses_only_verified_omitted_occurrences():
    report = {"omitted_artifacts": [{"source_reference": "old.png", "image_occurrences": 1}]}
    assert _reader_image_occurrences(3, report) == 2
    with pytest.raises(FiveStepDocxError, match="one image occurrence"):
        _reader_image_occurrences(1, {"omitted_artifacts": [{"source_reference": "old.png", "image_occurrences": 2}]})
    assert _reader_image_occurrences(1, {"omitted_artifacts": [{"source_reference": None, "image_occurrences": 0}]}) == 1
