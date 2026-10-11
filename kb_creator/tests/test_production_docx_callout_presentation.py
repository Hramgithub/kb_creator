import copy
import zipfile

import pytest
from lxml import etree, html

from kb_creator.pipeline.five_step_docx import _default_config
from kb_creator.scripts.production_docx import (
    WORD_NS, _apply_xml_callouts, build_docx, build_state_for_profile,
    validate_document_config,
)


def test_plain_callout_survives_full_build_and_xml_patch(tmp_path):
    source = tmp_path / 'input.html'
    source.write_text('<html><head><meta charset="utf-8"/></head><body><main>'
        '<nav id="toc"><h1>Содержание</h1><ol><li><a href="#chapter">Раздел</a></li></ol></nav>'
        '<h1 id="chapter">Раздел</h1><blockquote class="review-callout">'
        '<p>Короткая цитата.</p><p><strong>Важно:</strong> <em>смысл сохранён.</em></p>'
        '</blockquote></main></body></html>', encoding='utf-8')
    config = _default_config('Проверка')
    config['callouts'] = {'presentation': 'plain'}
    target = tmp_path / 'output.docx'
    result = build_docx(source, target, config=config)
    assert result['callouts'] == 1
    with zipfile.ZipFile(target) as package:
        doc = etree.fromstring(package.read('word/document.xml'))
    ns = {'w': WORD_NS}
    assert doc.xpath('//w:t/text()', namespaces=ns)[-4:] == ['Короткая цитата.', 'Важно:', ' ', 'смысл сохранён.']
    paragraphs = doc.xpath('//w:body/w:p', namespaces=ns)[-2:]
    assert not doc.xpath('//w:pPr/w:shd | //w:pPr/w:pBdr', namespaces=ns)
    assert not paragraphs[0].xpath('.//w:b', namespaces=ns)
    assert paragraphs[1].xpath('.//w:b', namespaces=ns)
    assert paragraphs[1].xpath('.//w:i', namespaces=ns)


def test_plain_mode_keeps_missing_content_detection():
    source = html.fromstring('<blockquote class="review-callout"><p>Обязательный текст</p></blockquote>')
    empty = etree.fromstring(f'<w:document xmlns:w="{WORD_NS}"><w:body/></w:document>')
    assert _apply_xml_callouts(source, empty, presentation='plain') == (0, ['Обязательный текст'])


def test_config_requires_explicit_supported_callout_mode():
    config = _default_config('Проверка')
    assert build_state_for_profile(validate_document_config(config)).callout_presentation == 'legacy_shaded'
    for mode in ['plain', 'legacy_shaded']:
        candidate = copy.deepcopy(config)
        candidate['callouts'] = {'presentation': mode}
        assert build_state_for_profile(validate_document_config(candidate)).callout_presentation == mode
    config['callouts'] = {'presentation': 'guess'}
    with pytest.raises(ValueError, match='unsupported'):
        validate_document_config(config)
