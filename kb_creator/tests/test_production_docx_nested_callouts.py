from __future__ import annotations

import pytest
from lxml import etree as lxml_etree
from lxml import html as lxml_html

from kb_creator.scripts.production_docx import WORD_NS, _apply_xml_callouts


def _document(paragraphs: list[str]):
    body = "".join(f"<w:p><w:r><w:t>{text}</w:t></w:r></w:p>" for text in paragraphs)
    return lxml_etree.fromstring(
        f'<w:document xmlns:w="{WORD_NS}"><w:body>{body}</w:body></w:document>'
    )


def test_nested_blockquote_callout_matches_and_styles_all_visible_paragraphs() -> None:
    html = lxml_html.fromstring(
        """<html><body><blockquote class="review-callout">
        <blockquote><p>Вложенный заголовок.</p><p>Вложенный текст 1D3.</p></blockquote>
        </blockquote></body></html>"""
    )
    document = _document(["Вложенный заголовок.", "Вложенный текст 1D3."])

    applied, missing = _apply_xml_callouts(html, document)

    assert (applied, missing) == (1, [])
    assert len(document.xpath(".//w:pPr/w:shd", namespaces={"w": WORD_NS})) == 2


def test_nested_callout_does_not_hide_missing_visible_text() -> None:
    html = lxml_html.fromstring(
        """<html><body><blockquote class="review-callout">
        <blockquote><p>Вложенный заголовок.</p><p>Обязательный текст.</p></blockquote>
        </blockquote></body></html>"""
    )
    document = _document(["Вложенный заголовок."])

    applied, missing = _apply_xml_callouts(html, document)

    assert applied == 0
    assert missing == ["Вложенный заголовок. Обязательный текст."]


def test_direct_callout_matching_behavior_is_unchanged() -> None:
    html = lxml_html.fromstring(
        '<html><body><blockquote class="review-callout"><p>Первый.</p><p>Второй.</p></blockquote></body></html>'
    )
    document = _document(["Первый.", "Второй."])

    assert _apply_xml_callouts(html, document) == (1, [])


def test_empty_transport_shells_do_not_hide_following_callout():
    html = lxml_html.fromstring('<html><body><blockquote class="review-callout"/>'
        '<blockquote class="review-callout"> \n </blockquote>'
        '<blockquote class="review-callout"><p>Сохранённая врезка.</p></blockquote></body></html>')
    assert _apply_xml_callouts(html, _document(['Сохранённая врезка.'])) == (1, [])
    assert _apply_xml_callouts(html, _document([])) == (0, ['Сохранённая врезка.'])


@pytest.mark.parametrize('content', ['Неподдерживаемый прямой текст', '<span>Текст</span>', '<img src="x.png"/>'])
def test_nonempty_unsupported_callout_is_not_silently_skipped(content):
    html = lxml_html.fromstring('<html><body><blockquote class="review-callout">'
        + content + '</blockquote></body></html>')
    applied, missing = _apply_xml_callouts(html, _document([]))
    assert applied == 0 and len(missing) == 1
