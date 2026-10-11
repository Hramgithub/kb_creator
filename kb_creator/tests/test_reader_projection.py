import copy
import hashlib

import pytest
from lxml import html

from kb_creator.pipeline.reader_projection import project_reader_html
from translator.translator import markdown_to_review_html


def case():
    texts = ["<!-- source-page-001 -->", "# Книга", "# Содержание", "Раздел 9", "## Выходные данные", "Автор", "<!-- source-page-002 -->", "# Раздел", "См. стр. 9."]
    units = [{"unit_id": f"unit-{n}", "ru_text": t, "ru_sha256": hashlib.sha256(t.encode()).hexdigest().upper()} for n, t in enumerate(texts)]
    def bind(n):
        return {k: units[n][k] for k in ("unit_id", "ru_sha256")}
    options = {"source_toc": {"state": "present", "source_pdf_sha256": "A"*64, "reason": "Reviewed source", "units": [bind(2), bind(3)], "entries": [{"source_text": "Раздел 9", "level": 1, "target": bind(7)}]}, "body_links": [{"unit": bind(8), "text": "стр. 9", "label": "раздел", "target": bind(7), "reason": "Explicit target"}], "display_roles": [], "asset_choices": [], "hit_points": {"presentation": "numeric", "expected_counts": []}}
    body, toc, _ = markdown_to_review_html("\n\n".join(texts), source_path=__import__('pathlib').Path('x.md'), html_path=__import__('pathlib').Path('x.html'))
    return body, toc, {"units": units}, options


def test_source_toc_list_with_dot_leaders_keeps_title_numbers_and_links():
    body, toc, projection, options = case()
    source = "- Сцена 1 . . .9\n- Приложение II…41"
    unit = projection['units'][3]
    unit.update(ru_text=source, ru_sha256=hashlib.sha256(source.encode()).hexdigest().upper())
    options['source_toc']['units'][1] = {k: unit[k] for k in ('unit_id', 'ru_sha256')}
    options['source_toc']['entries'] = [
        {'source_text': row, 'level': 1, 'target': options['body_links'][0]['target']}
        for row in source.splitlines()
    ]
    body, toc, _ = markdown_to_review_html(
        '\n\n'.join(u['ru_text'] for u in projection['units']),
        source_path=__import__('pathlib').Path('x.md'), html_path=__import__('pathlib').Path('x.html'))
    out, effective, _ = project_reader_html(body, toc, projection, options)
    tree = html.fragment_fromstring(out, create_parent='main')
    assert [a.text for a in tree.xpath('.//nav//a')] == ['Сцена 1', 'Приложение II']
    assert len(tree.xpath('.//nav')) == 1
    assert 'Выходные данные' in tree.text_content()
    assert [row['title'] for row in effective] == ['Сцена 1', 'Приложение II']
    for link in tree.xpath('.//nav//a'):
        assert len(tree.xpath('.//*[@id=$target]', target=link.get('href')[1:])) == 1
    options['source_toc']['entries'][0]['source_text'] = '- Сцена 1 . . .8'
    with pytest.raises(ValueError, match='row preimage'):
        project_reader_html(body, toc, projection, options)


@pytest.mark.parametrize('source,expected', [
    ('Раздел 9', 'Раздел'), ('1. Введение ..2', 'Введение'),
    ('- Сцена 6 — Храм . . . . . . 32', 'Сцена 6 — Храм'),
    ('Приложение II … 41–44', 'Приложение II'),
    ('- Сцена 1 ..9', 'Сцена 1'),
])
def test_reviewed_toc_label_forms(source, expected):
    from kb_creator.pipeline.reader_projection import _toc_label
    assert _toc_label(source) == expected


def test_source_toc_stays_in_place_and_keeps_credits_with_exact_links():
    body, toc, projection, options = case()
    out, effective, report = project_reader_html(body, toc, projection, options)
    tree = html.fragment_fromstring(out, create_parent="main")
    assert len(tree.xpath('.//nav')) == 1
    assert tree.xpath('.//section')[0][1].text_content() == "Книга"
    assert "Выходные данные" in tree.text_content() and "Автор" in tree.text_content()
    assert "стр. 9" not in tree.text_content() and "Раздел 9" not in tree.text_content()
    assert len(effective) == 1 and len(report['links']) == 2
    for link in tree.xpath('.//a'):
        assert len(tree.xpath('.//*[@id=$id]', id=link.get('href')[1:])) == 1


@pytest.mark.parametrize('damage', [None, 'stale', 'prefix', 'inline', 'empty_prose'])
def test_heading_prose_split_preserves_words_links_and_source(damage):
    body, toc, projection, options = case()
    text = '## Завершение Сцены 1: после осмотра дома следует уйти.'
    if damage == 'inline':
        text = '## Завершение Сцены 1: после **осмотра** дома следует уйти.'
    if damage == 'empty_prose':
        text = '## Завершение Сцены 1:'
    unit = projection['units'][7]
    unit.update(ru_text=text, ru_sha256=hashlib.sha256(text.encode()).hexdigest().upper())
    binding = {k: unit[k] for k in ('unit_id', 'ru_sha256')}
    options['source_toc']['entries'][0]['target'] = binding
    options['body_links'][0]['target'] = binding
    decision = {'role': 'heading_prose_split', 'unit': copy.deepcopy(binding),
                'heading_text': 'Завершение Сцены 1:', 'reason': 'OCR heading absorbed prose',
                'source_evidence': 'source page 16'}
    options['display_roles'] = [decision]
    if damage == 'stale':
        decision['unit']['ru_sha256'] = '0' * 64
    if damage == 'prefix':
        decision['heading_text'] = 'Завершение Сцены 2:'
    body, toc, _ = markdown_to_review_html('\n\n'.join(u['ru_text'] for u in projection['units']),
        source_path=__import__('pathlib').Path('x.md'), html_path=__import__('pathlib').Path('x.html'))
    before = copy.deepcopy(projection)
    if damage:
        with pytest.raises(ValueError, match='preimage|heading prefix'):
            project_reader_html(body, toc, projection, options)
        return
    out, _, report = project_reader_html(body, toc, projection, options)
    tree = html.fragment_fromstring(out, create_parent='main')
    heading = tree.xpath('.//h2[starts-with(text(), "Завершение")]')[0]
    assert heading.text == 'Завершение Сцены 1:'
    assert heading.getnext().tag == 'p'
    assert heading.getnext().text == 'после осмотра дома следует уйти.'
    assert tree.xpath('.//a[@href=$ref]', ref='#' + heading.get('id'))
    assert projection == before
    assert report['display_roles'] == [decision]


@pytest.mark.parametrize('damage', ['stale', 'missing_row', 'unresolved', 'noncontiguous'])
def test_reader_mapping_fails_closed(damage):
    body, toc, projection, options = case()
    if damage == 'stale':
        options['source_toc']['entries'][0]['target']['ru_sha256'] = '0'*64
    elif damage == 'missing_row':
        options['source_toc']['entries'] = []
    elif damage == 'unresolved':
        options['source_toc']['state'] = 'unresolved'
    else:
        options['source_toc']['units'].append({k:projection['units'][5][k] for k in ('unit_id','ru_sha256')})
    with pytest.raises(ValueError):
        project_reader_html(body, toc, projection, options)


def test_hp_across_lines_preserves_other_boxes_and_stat_text():
    body, toc, projection, options = case()
    body += '<p>□ вне статблока</p><section data-semantic-kind="statblock" data-semantic-id="s"><p>ПЗ:<br>◻◻<br>◻◻◻</p><p>СИЛ 50; Урон 1d6</p></section>'
    options['hit_points']['expected_counts'] = [5]
    out, _, report = project_reader_html(body, toc, projection, options)
    assert 'ПЗ: 5' in out and '□ вне статблока' in out and 'СИЛ 50; Урон 1d6' in out
    assert report['hit_points'] == [{'semantic_id': 's', 'count': 5}]
    options['hit_points']['expected_counts'] = [4]
    with pytest.raises(ValueError, match='count mismatch'):
        project_reader_html(body, toc, projection, options)


def test_absence_classification_generates_toc():
    body, toc, projection, options = case()
    options['source_toc'] = {'state': 'absent', 'source_pdf_sha256': 'A'*64, 'reason': 'Source examined'}
    # Remove the source TOC from the fixture to represent a source without one.
    tree = html.fragment_fromstring(body, create_parent='main')
    for node in tree.xpath('.//h1[text()="Содержание"] | .//p[text()="Раздел 9"]'):
        node.getparent().remove(node)
    body = ''.join(html.tostring(e, encoding='unicode') for e in tree)
    out, effective, _ = project_reader_html(body, toc, projection, options)
    assert out.startswith('<nav') and effective == toc


def test_reviewed_service_caption_hidden_but_alt_and_real_caption_retained():
    body, toc, projection, options = case()
    body += '<figure><img src="a.png" alt="Source image"><figcaption>Source image</figcaption></figure><figure><img src="b.png" alt="B"><figcaption>Meaningful source caption</figcaption></figure>'
    options['display_roles'] = [{'role':'asset_alt_metadata','source_reference':'a.png','caption':'Source image','reason':'Reviewed reconstruction metadata'}]
    out, _, _ = project_reader_html(body, toc, projection, options)
    tree = html.fragment_fromstring(out, create_parent='main')
    assert tree.xpath('.//img[@src="a.png"]')[0].get('alt') == 'Source image'
    assert [x.text_content() for x in tree.xpath('.//figcaption')] == ['Meaningful source caption']
    options['display_roles'][0]['caption'] = 'Wrong'
    with pytest.raises(ValueError, match='caption preimage'):
        project_reader_html(body, toc, projection, options)


def test_shared_figure_headings_keep_each_link_target():
    body, toc, projection, options = case()
    text = '## Второй фрагмент'
    unit = {'unit_id':'unit-extra','ru_text':text,'ru_sha256':hashlib.sha256(text.encode()).hexdigest().upper()}
    projection['units'].append(unit)
    tree = html.fragment_fromstring(body, create_parent='main')
    page = tree.xpath('.//section[@data-page="002"]')[0]
    page.append(html.fragment_fromstring('<h2>Второй фрагмент</h2>'))
    page.append(html.fragment_fromstring('<figure><img src="sheet.png"></figure>'))
    body = ''.join(html.tostring(e, encoding='unicode') for e in tree)
    second = {k:unit[k] for k in ('unit_id','ru_sha256')}
    options['display_roles'] = [{'role':'shared_figure_heading','units':[options['body_links'][0]['target'],second],'label':'Общие фрагменты','source_reference':'sheet.png','reason':'Both refer to one source sheet'}]
    options['body_links'][0]['target'] = second
    out, _, report = project_reader_html(body, toc, projection, options)
    doc = html.fragment_fromstring(out, create_parent='main')
    assert len(doc.xpath('.//h2')) == 1  # Credits heading is retained.
    assert 'Второй фрагмент' not in doc.text_content()
    for link in report['links']:
        assert len(doc.xpath('.//*[@id=$id]',id=link['target'])) == 1
