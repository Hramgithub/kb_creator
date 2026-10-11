import copy
import hashlib
from pathlib import Path

import pytest
from lxml import html
from kb_creator.pipeline.reader_projection import project_reader_html
from translator.translator import markdown_to_review_html


def setup(texts):
    units=[{'unit_id':f'u{i}','ru_text':t,'ru_sha256':hashlib.sha256(t.encode()).hexdigest().upper()} for i,t in enumerate(texts)]
    bind=lambda i:{k:units[i][k] for k in ('unit_id','ru_sha256')}
    body,toc,_=markdown_to_review_html('\n\n'.join(texts),source_path=Path('x.md'),html_path=Path('x.html'))
    options={'source_toc':{'state':'absent','source_pdf_sha256':'A'*64,'reason':'source reviewed'},'body_links':[],'display_roles':[],'asset_choices':[],'hit_points':{'presentation':'numeric','expected_counts':[]}}
    return body,toc,{'units':units},options,bind


@pytest.mark.parametrize('cross_page',[False,True])
def test_explicit_continuation_preserves_inline_text_hard_break_and_target(cross_page):
    texts=['<!-- source-page-001 -->','Жил в']
    if cross_page: texts+=['<!-- source-page-002 -->']
    texts+=['**Берлине** более десяти лет.  \nЗатем исчез.','См. продолжение.']
    body,toc,projection,options,bind=setup(texts)
    right=3 if cross_page else 2
    options['display_roles']=[{'role':'paragraph_continuation','units':[bind(1),bind(right)],'reason':'Source column/page break','source_evidence':'source page review'}]
    options['body_links']=[{'unit':bind(right+1),'target':bind(right),'text':'продолжение','label':'продолжение','reason':'explicit'}]
    prior=copy.deepcopy(projection)
    out,_,report=project_reader_html(body,toc,projection,options)
    doc=html.fragment_fromstring(out,create_parent='main')
    p=doc.xpath('.//p')[0]
    assert 'Жил в Берлине более десяти лет.' in p.text_content()
    assert len(p.xpath('.//strong'))==len(p.xpath('.//br'))==1
    assert len(doc.xpath('.//*[@id=$id]',id=report['links'][0]['target']))==1
    assert projection==prior


@pytest.mark.parametrize('cross_page',[False,True])
def test_reviewed_word_join_preserves_inline_descendants_and_both_anchors(cross_page):
    texts=['<!-- source-page-001 -->','Он **подслушива**']
    if cross_page: texts+=['<!-- source-page-002 -->']
    texts+=['*ет* разговор.','См. продолжение.']
    body,toc,projection,options,bind=setup(texts)
    right=3 if cross_page else 2
    decision={'role':'paragraph_continuation','units':[bind(1),bind(right)],
              'join_mode':'word','reason':'Reviewed split word',
              'source_evidence':'source page review'}
    options['display_roles']=[decision]
    options['body_links']=[{'unit':bind(right+1),'target':bind(right),
                           'text':'продолжение','label':'продолжение','reason':'explicit'}]
    prior=copy.deepcopy(projection)
    out,_,report=project_reader_html(body,toc,projection,options)
    doc=html.fragment_fromstring(out,create_parent='main')
    paragraph=doc.xpath('.//p')[0]
    assert paragraph.text_content()=='Он подслушивает разговор.'
    assert [node.text for node in paragraph.xpath('.//strong|.//em')]==['подслушива','ет']
    assert len(doc.xpath('.//*[@id="reader-u1"]'))==1
    assert len(doc.xpath('.//*[@id="reader-u%s"]' % right))==1
    assert len(doc.xpath('.//*[@id=$id]',id=report['links'][0]['target']))==1
    assert report['display_roles']==[decision]
    assert projection==prior


@pytest.mark.parametrize('mode',['space','word'])
def test_declared_join_mode_controls_visible_separator(mode):
    body,toc,projection,options,bind=setup(['<!-- source-page-001 -->','подслушива','ет разговор.'])
    options['display_roles']=[{'role':'paragraph_continuation','units':[bind(1),bind(2)],
                               'join_mode':mode,'reason':'x','source_evidence':'x'}]
    out,_,_=project_reader_html(body,toc,projection,options)
    paragraph=html.fragment_fromstring(out,create_parent='main').xpath('.//p')[0]
    assert paragraph.text_content()==('подслушива ет разговор.' if mode=='space' else 'подслушивает разговор.')


@pytest.mark.parametrize('mode',[None,'', 'hyphen', 'none', 0, False])
def test_continuation_rejects_unsupported_join_mode(mode):
    body,toc,projection,options,bind=setup(['<!-- source-page-001 -->','подслушива','ет'])
    options['display_roles']=[{'role':'paragraph_continuation','units':[bind(1),bind(2)],
                               'join_mode':mode,'reason':'x','source_evidence':'x'}]
    with pytest.raises(ValueError,match='join mode'):
        project_reader_html(body,toc,projection,options)


@pytest.mark.parametrize('left,right',[
    ('слово.','Дальше'),('слово','— дальше'),('123','дальше'),
    ('слово','456'),('слово ','дальше'),('слово',' дальше'),
])
def test_word_join_rejects_non_letter_boundaries(left,right):
    body,toc,projection,options,bind=setup(['<!-- source-page-001 -->',left,right])
    options['display_roles']=[{'role':'paragraph_continuation','units':[bind(1),bind(2)],
                               'join_mode':'word','reason':'x','source_evidence':'x'}]
    with pytest.raises(ValueError,match='letter boundaries'):
        project_reader_html(body,toc,projection,options)


def test_continuation_rejects_unexpected_decision_fields():
    body,toc,projection,options,bind=setup(['<!-- source-page-001 -->','подслушива','ет'])
    options['display_roles']=[{'role':'paragraph_continuation','units':[bind(1),bind(2)],
                               'join_mode':'word','separator':' ', 'reason':'x','source_evidence':'x'}]
    with pytest.raises(ValueError,match='decision fields'):
        project_reader_html(body,toc,projection,options)


@pytest.mark.parametrize('obstacle',['# Заголовок','Другой абзац','![Карта](a.png)','> Цитата','1. Пункт'])
@pytest.mark.parametrize('join_mode',['space','word'])
def test_continuation_rejects_intervening_content(obstacle,join_mode):
    body,toc,projection,options,bind=setup(['<!-- source-page-001 -->','Жил в',obstacle,'Берлине.'])
    options['display_roles']=[{'role':'paragraph_continuation','units':[bind(1),bind(3)],'join_mode':join_mode,'reason':'x','source_evidence':'x'}]
    with pytest.raises(ValueError,match='adjacent'):
        project_reader_html(body,toc,projection,options)


@pytest.mark.parametrize('defect',['stale','backward','page_gap','missing_evidence'])
@pytest.mark.parametrize('join_mode',['space','word'])
def test_continuation_requires_exact_ordered_evidence(defect,join_mode):
    body,toc,projection,options,bind=setup(['<!-- source-page-001 -->','Жил в','<!-- source-page-002 -->','Берлине.'])
    row={'role':'paragraph_continuation','units':[bind(1),bind(3)],'join_mode':join_mode,'reason':'x','source_evidence':'x'}
    if defect=='stale':row['units'][0]['ru_sha256']='wrong'
    elif defect=='backward':row['units'].reverse()
    elif defect=='missing_evidence':row.pop('source_evidence')
    else:
        projection['units'][2]['ru_text']='<!-- source-page-004 -->'
        body=body.replace('data-page="002"','data-page="004"')
    options['display_roles']=[row]
    with pytest.raises(ValueError):project_reader_html(body,toc,projection,options)


def test_inline_list_preserves_exact_items_without_changing_master_projection():
    body,toc,projection,options,bind=setup(['<!-- source-page-001 -->','1) Газета. 2) Письмо с датой 1930. 3) Карта.'])
    options['display_roles']=[{'role':'inline_ordered_list','unit':bind(1),'items':['Газета.','Письмо с датой 1930.','Карта.'],'reason':'Source shows3distinctitems','source_evidence':'review page1'}]
    before=copy.deepcopy(projection)
    out,_,_=project_reader_html(body,toc,projection,options)
    doc=html.fragment_fromstring(out,create_parent='main')
    assert [li.text for li in doc.xpath('.//ol/li')]==options['display_roles'][0]['items']
    assert projection==before
    options['display_roles'][0]['items'][1]='Письмо с датой 1931.'
    with pytest.raises(ValueError,match='preimage'):project_reader_html(body,toc,projection,options)
