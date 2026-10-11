import copy
import hashlib
import json
from pathlib import Path

import pytest
from lxml import html

from kb_creator.pipeline.reader_projection import identity, project_reader_html
from translator.translator import markdown_to_review_html


def setup(texts):
    units = [{"unit_id": f"unit-{number:05d}", "ru_text": text,
              "ru_sha256": hashlib.sha256(text.encode()).hexdigest().upper()}
             for number, text in enumerate(texts, 1)]
    bind = lambda index: {key: units[index][key] for key in ("unit_id", "ru_sha256")}
    body, _, _ = markdown_to_review_html("\n\n".join(texts), source_path=Path("x.md"), html_path=Path("x.html"))
    options = {"source_toc": {"state": "absent", "source_pdf_sha256": "A" * 64, "reason": "source reviewed"},
               "body_links": [], "display_roles": [], "asset_choices": [],
               "hit_points": {"presentation": "numeric", "expected_counts": []}}
    return body, {"units": units}, options, bind


def reflow(bind, left, right, intervening):
    return {"role": "interrupted_prose_reflow", "units": [bind(left), bind(right)],
            "intervening_units": [bind(index) for index in intervening],
            "reason": "Reviewed source sentence crosses an artwork/sidebar interruption.",
            "source_evidence": "Reviewed source pages retain every intervening block."}


def handout_group(bind, indexes, title):
    return {"units": [bind(index) for index in indexes], "title": bind(title),
            "source_evidence": "Reviewed source handout remains complete and ordered.",
            "reason": "Reviewed textual handout interrupts one narrative sentence."}


def test_reflow_moves_sentence_boundary_before_all_reviewed_intervening_blocks():
    body, projection, options, bind = setup([
        "<!-- source-page-001 -->", "Жил в **старом**",
        "![Первая](one.png)", "<!-- source-page-002 -->", "> Сайдбар", "![Вторая](two.png)", "доме.", "См. доме.",
    ])
    decision = reflow(bind, 1, 6, [2, 3, 4, 5])
    options["display_roles"] = [decision]
    options["body_links"] = [{"unit": bind(7), "target": bind(6), "text": "доме", "label": "доме", "reason": "test target"}]
    before = copy.deepcopy(projection)

    out, _, report = project_reader_html(body, [], projection, options)
    tree = html.fragment_fromstring(out, create_parent="main")
    paragraph = tree.xpath(".//p")[0]
    assert paragraph.tag == "p" and "Жил в старом доме." in paragraph.text_content()
    assert len(paragraph.xpath(".//strong")) == 1
    assert not tree.xpath('.//p[text()="доме."]')
    order = list(tree.iter())
    assert order.index(paragraph) < order.index(tree.xpath('.//figure[img[@src="one.png"]]')[0])
    assert order.index(tree.xpath('.//figure[img[@src="one.png"]]')[0]) < order.index(tree.xpath(".//blockquote")[0])
    assert order.index(tree.xpath(".//blockquote")[0]) < order.index(tree.xpath('.//figure[img[@src="two.png"]]')[0])
    target = report["links"][0]["target"]
    assert len(tree.xpath('.//*[@id=$target]', target=target)) == 1
    assert projection == before and report["display_roles"] == [decision]


def test_reflow_preserves_left_bullet_list_semantics():
    body, projection, options, bind = setup([
        "<!-- source-page-001 -->", "- Сведения находятся в Государственном",
        "<!-- source-page-002 -->", "![Иллюстрация](map.png)", "музее.",
    ])
    options["display_roles"] = [reflow(bind, 1, 4, [2, 3])]

    out, _, _ = project_reader_html(body, [], projection, options)
    tree = html.fragment_fromstring(out, create_parent="main")
    items = tree.xpath(".//ul/li")
    assert len(items) == 1 and items[0].text_content() == "Сведения находятся в Государственном музее."
    assert tree.xpath('.//figure[img[@src="map.png"]]')
    assert not tree.xpath('.//p[text()="музее."]')


def test_reflow_preserves_complete_textual_handout_group_and_its_bookmark_link():
    body, projection, options, bind = setup([
        "<!-- source-page-001 -->", "До меморандума", "## Меморандум", "Первый пункт.",
        "| Поле | Значение |\n| --- | --- |\n| Код | 17 |", "<!-- source-page-002 -->", "после меморандума.", "См. меморандум.",
    ])
    decision = reflow(bind, 1, 6, [2, 3, 4, 5])
    decision["intervening_handout_groups"] = [handout_group(bind, [2, 3, 4], 2)]
    options["display_roles"] = [decision]
    options["body_links"] = [{"unit": bind(7), "target": bind(2), "text": "меморандум",
                              "label": "меморандум", "reason": "fixture handout link"}]

    out, _, report = project_reader_html(body, [], projection, options)
    tree = html.fragment_fromstring(out, create_parent="main")
    narrative = tree.xpath('.//p[starts-with(normalize-space(), "До меморандума")]')[0]
    handout = tree.xpath('.//h2[normalize-space()="Меморандум"]')[0]
    assert narrative.text_content() == "До меморандума после меморандума."
    assert not tree.xpath('.//p[text()="после меморандума."]')
    handout_nodes = tree.xpath('.//h2[normalize-space()="Меморандум"] | .//h2[normalize-space()="Меморандум"]/following-sibling::*[position() <= 2]')
    assert [node.tag for node in handout_nodes] == ["h2", "p", "div"]
    assert handout_nodes[-1].xpath("./table")
    assert tree.xpath('.//a[@href=$target]', target="#" + handout.get("id"))
    assert report["display_roles"] == [decision]


def test_reflow_preserves_textual_handout_source_comment_target():
    body, projection, options, bind = setup([
        "<!-- source-page-001 -->", "До", "## Меморандум", "Текст handout.", "После.",
    ])
    decision = reflow(bind, 1, 4, [2, 3])
    decision["intervening_handout_groups"] = [handout_group(bind, [2, 3], 2)]
    source_comment = {"role": "source_issue_review_anchor", "issue_id": "handout-title",
                      "unit": bind(2), "source_page": 1, "en_excerpt": "Memo title",
                      "source_evidence": "sealed fixture", "reason": "review handout title",
                      "placement": "first_visible_text_block_v1"}
    options["display_roles"] = [decision, source_comment]

    out, _, report = project_reader_html(body, [], projection, options)
    tree = html.fragment_fromstring(out, create_parent="main")
    anchor = report["review_anchors"][0]["anchor"]
    assert tree.xpath('.//h2[@id=$anchor and normalize-space()="Меморандум"]', anchor=anchor)


@pytest.mark.parametrize("damage", ["partial", "stale", "prose", "structured"])
def test_reflow_rejects_partial_stale_or_nonpermitted_routes(damage):
    texts = ["<!-- source-page-001 -->", "Фрагмент", "![Иллюстрация](a.png)", "<!-- source-page-002 -->", "продолжение."]
    if damage == "prose":
        texts[2] = "Несвязанная проза."
    if damage == "structured":
        texts[1] = "> Фрагмент"
    body, projection, options, bind = setup(texts)
    decision = reflow(bind, 1, 4, [2, 3])
    if damage == "partial":
        decision["intervening_units"] = decision["intervening_units"][:-1]
    if damage == "stale":
        decision["intervening_units"][0]["ru_sha256"] = "0" * 64
    options["display_roles"] = [decision]
    with pytest.raises(ValueError, match="coverage|bindings|unrelated|structured"):
        project_reader_html(body, [], projection, options)


@pytest.mark.parametrize("damage", ["partial", "overlap", "stale", "not_title", "reordered", "unknown"])
def test_handout_groups_fail_closed_when_their_exact_scope_is_invalid(damage):
    body, projection, options, bind = setup([
        "<!-- source-page-001 -->", "До", "## Меморандум", "Пункт.", "После.",
    ])
    decision = reflow(bind, 1, 4, [2, 3])
    group = handout_group(bind, [2, 3], 2)
    if damage == "partial":
        group["units"] = [bind(2)]
    elif damage == "overlap":
        decision["intervening_handout_groups"] = [group, handout_group(bind, [3], 2)]
    elif damage == "stale":
        group["units"][1]["ru_sha256"] = "0" * 64
    elif damage == "not_title":
        group["title"] = bind(3)
    elif damage == "reordered":
        group["units"].reverse()
    elif damage == "unknown":
        group["extra"] = True
    if "intervening_handout_groups" not in decision:
        decision["intervening_handout_groups"] = [group]
    options["display_roles"] = [decision]
    with pytest.raises(ValueError, match="coverage|contiguous|overlapping|preimage|title|handout|unrelated"):
        project_reader_html(body, [], projection, options)
