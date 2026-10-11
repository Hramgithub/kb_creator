"""Public consumer proof for the N143 combined title/byline semantic span.

This fixture models the validated p147 MASTER fragment after semantic
materialization.  It deliberately exercises the real Markdown-to-HTML/TOC
consumer, rather than the semantic helper, so a future consumer that reads the
complete semantic span as a title would be caught by output assertions.
"""
from lxml import html

from kb_creator.scripts.scenario_artview import extract_heading_labels
from translator.translator import markdown_to_review_html


P147_MASTER = """<!-- source-page-147 -->
# Phlebotomy

by Jeffrey Moeller

## Themes
"""


def test_p147_master_html_outline_and_artview_labels_keep_byline_out_of_title():
    body, outline, page_count = markdown_to_review_html(
        P147_MASTER, source_path=__import__("pathlib").Path("MASTER_EN.md"),
        html_path=__import__("pathlib").Path("MASTER_EN.html"),
    )
    tree = html.fragment_fromstring(body, create_parent="main")

    assert page_count == 1
    assert [(row["level"], row["title"]) for row in outline] == [(1, "Phlebotomy"), (2, "Themes")]
    assert all("Jeffrey" not in row["title"] for row in outline)
    assert [node.text_content() for node in tree.xpath(".//h1")] == ["Phlebotomy"]
    assert [node.text_content() for node in tree.xpath(".//h2")] == ["Themes"]
    assert [node.text_content() for node in tree.xpath(".//p")] == ["by Jeffrey Moeller"]

    master_with_anchor = '<a id="fear-p147-title-author-n143"></a>\n' + P147_MASTER
    assert extract_heading_labels(master_with_anchor) == {"fear-p147-title-author-n143": "Phlebotomy"}
