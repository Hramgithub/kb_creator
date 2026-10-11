import json
import zipfile
from pathlib import Path
import pytest
from kb_creator.scripts.build_bilingual_checkpoint import build, compile_pages, prepare
from kb_creator.pipeline import reader_projection
from kb_creator.pipeline.five_step_docx import _default_config
from kb_creator.scripts.snapshot_working_data import snapshot, verify_or_restore
from kb_creator.scripts.production_docx import build_docx


def test_checkpoint_rejects_missing_or_duplicate_pages(tmp_path):
    paths=[]
    for i,page in enumerate((1,3)):
        p=tmp_path/f'{i}.json'
        p.write_text(json.dumps(dict(source_page=page,en_markdown='Text',ru_markdown='Текст')),encoding='utf-8')
        paths.append(p)
    with pytest.raises(ValueError,match='contiguous'):
        compile_pages(paths)
    with pytest.raises(ValueError,match='contiguous'):
        compile_pages([paths[0],paths[0]])


@pytest.mark.parametrize('body',[
    '<h1>Содержание</h1><p>Автор и аннотация остаются обычным текстом.</p>',
    '<h1>Глава</h1><table><tr><td>Данные</td><td>42</td></tr></table>'
])
def test_docx_without_navigation_does_not_require_toc(tmp_path,body):
    source=tmp_path/'source.html'
    source.write_text('<html><head><meta charset="utf-8"></head><body><main>'+body+'</main></body></html>',encoding='utf-8')
    target=tmp_path/'document.docx'
    result=build_docx(source,target)
    assert result['internal_hyperlinks']==0
    with zipfile.ZipFile(target) as archive:
        assert archive.testzip() is None
        assert b'bookmarkStart' not in archive.read('word/document.xml')


def test_checkpoint_preserves_cyrillic_through_serialized_docx(tmp_path):
    pages=tmp_path/'pages';pages.mkdir()
    (pages/'page-001.json').write_text(json.dumps(dict(source_page=1,en_markdown='# Title\n\nText',ru_markdown='# Глава\n\nТочный русский текст.'),ensure_ascii=False),encoding='utf-8')
    config=tmp_path/'config.json'
    config.write_text(json.dumps(_default_config('Книга')),encoding='utf-8')
    result=build(pages,tmp_path,config,tmp_path/'output')
    assert result['text_closure']['missing_blocks']==[]
    assert 'Точный русский текст.' in (tmp_path/'output/DOCX_EXTRACTED_TEXT.txt').read_text(encoding='utf-8')


def _reader_fixture(tmp_path, *, toc=False):
    pages=tmp_path/'pages';pages.mkdir()
    ru=('# Содержание\n\n- Глава 1 ... 1\n\n' if toc else '') + (
        '# Глава 1\n\nОн **подслушива**\n\n*ет* разговор.\n\n'
        '![Номер](folio.png)\n\nСм. продолжение.')
    (pages/'page-001.json').write_text(json.dumps(dict(source_page=1,en_markdown='# Chapter 1',
        ru_markdown=ru),ensure_ascii=False),encoding='utf-8')
    # Valid 1x1 PNG; a reviewed ornamental source image may be omitted from DOCX.
    import base64
    (tmp_path/'folio.png').write_bytes(base64.b64decode(
        'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+/lZkAAAAASUVORK5CYII='))
    source_pdf=tmp_path/'source.pdf';source_pdf.write_bytes(b'%PDF-1.4 source fixture')
    config=tmp_path/'config.json';config.write_text(json.dumps(_default_config('Книга')),encoding='utf-8')
    prepared=tmp_path/'prepared';prepare(pages,tmp_path,source_pdf,prepared)
    template=json.loads((prepared/'reader_options.template.json').read_text(encoding='utf-8'))
    units=json.loads((prepared/'PRELIMINARY_RU_PROJECTION.json').read_text(encoding='utf-8'))['units']
    return pages,source_pdf,config,prepared,template,units


def _write_options(path, value):
    value.pop('options_sha256',None)
    value['options_sha256']=reader_projection.seal(value)
    path.write_text(json.dumps(value,ensure_ascii=False),encoding='utf-8')


def test_preliminary_reader_build_real_docx_closes_join_omission_and_link(tmp_path):
    pages,source_pdf,config,prepared,options,units=_reader_fixture(tmp_path)
    def bind(text):
        row=next(unit for unit in units if unit['ru_text']==text)
        return {key:row[key] for key in ('unit_id','ru_sha256')}
    options['source_toc']['state']='absent';options['source_toc']['reason']='Reviewed source PDF has no TOC'
    options['hit_points']={'presentation':'numeric','expected_counts':[]}
    options['display_roles']=[
        {'role':'paragraph_continuation','units':[bind('Он **подслушива**'),bind('*ет* разговор.')],
         'join_mode':'word','reason':'Reviewed split word','source_evidence':'Source page 1'},
        {'role':'omit_source_artifact','unit':bind('![Номер](folio.png)'),
         'classification':'ornamental_page_number','reason':'Reviewed folio','source_evidence':'Source page 1'},
    ]
    options['body_links']=[{'unit':bind('См. продолжение.'),'target':bind('*ет* разговор.'),
                            'text':'продолжение','label':'продолжение','reason':'Reviewed reference'}]
    path=tmp_path/'reader_options.json';_write_options(path,options)
    result=build(pages,tmp_path,config,tmp_path/'output',prepared=prepared,
                 reader_options=path,source_pdf=source_pdf)
    assert result['text_closure']['missing_blocks']==[]
    extracted=(tmp_path/'output/DOCX_EXTRACTED_TEXT.txt').read_text(encoding='utf-8')
    assert 'подслушивает разговор' in extracted
    assert 'Номер' not in extracted
    assert (tmp_path/'output/PRELIMINARY_RU.md').read_text(encoding='utf-8').count('подслушива')==1
    checkpoint=json.loads((tmp_path/'output/CHECKPOINT.json').read_text(encoding='utf-8'))
    assert checkpoint['accepted'] is False and checkpoint['release_ready'] is False
    assert len(checkpoint['reader_projection']['links'])==1
    archived=(tmp_path/'output/PRELIMINARY_RU.md').read_bytes()
    assert archived==(prepared/'PRELIMINARY_RU.md').read_bytes()
    assert len(archived)==options['master_ru']['bytes']
    assert reader_projection.sha(tmp_path/'output/PRELIMINARY_RU.md')==options['master_ru']['sha256']


def test_preliminary_reader_rejects_stale_bindings_and_unreviewed_toc(tmp_path):
    pages,source_pdf,config,prepared,options,units=_reader_fixture(tmp_path,toc=True)
    options['source_toc']['state']='absent';options['source_toc']['reason']='Claimed absent'
    options['hit_points']={'presentation':'numeric','expected_counts':[]}
    path=tmp_path/'reader_options.json';_write_options(path,options)
    with pytest.raises(ValueError,match='Source TOC detected'):
        build(pages,tmp_path,config,tmp_path/'absent',prepared=prepared,
              reader_options=path,source_pdf=source_pdf)
    source_pdf.write_bytes(b'%PDF-1.4 changed')
    with pytest.raises(ValueError,match='page/source binding'):
        build(pages,tmp_path,config,tmp_path/'stale-source',prepared=prepared,
              reader_options=path,source_pdf=source_pdf)
    source_pdf.write_bytes(b'%PDF-1.4 source fixture')
    options['master_ru']['sha256']='0'*64;_write_options(path,options)
    with pytest.raises(ValueError,match='master/projection binding'):
        build(pages,tmp_path,config,tmp_path/'stale-options',prepared=prepared,
              reader_options=path,source_pdf=source_pdf)
    options['master_ru']['sha256']=reader_projection.sha(prepared/'PRELIMINARY_RU.md')
    _write_options(path,options)
    (pages/'page-001.json').write_text((pages/'page-001.json').read_text(encoding='utf-8')+' ',encoding='utf-8')
    with pytest.raises(ValueError,match='page/source binding'):
        build(pages,tmp_path,config,tmp_path/'stale-page',prepared=prepared,
              reader_options=path,source_pdf=source_pdf)


def test_preliminary_projection_keeps_exact_extra_blank_lines(tmp_path):
    pages=tmp_path/'pages';pages.mkdir()
    (pages/'page-001.json').write_text(json.dumps(dict(source_page=1,en_markdown='English',
        ru_markdown='# Глава\n\nАбзац.\n'),ensure_ascii=False),encoding='utf-8')
    (pages/'page-002.json').write_text(json.dumps(dict(source_page=2,en_markdown='English',
        ru_markdown='Второй абзац.'),ensure_ascii=False),encoding='utf-8')
    pdf=tmp_path/'source.pdf';pdf.write_bytes(b'%PDF-1.4')
    prepared=tmp_path/'prepared';prepare(pages,tmp_path,pdf,prepared)
    ru=(prepared/'PRELIMINARY_RU.md').read_text(encoding='utf-8')
    projection=json.loads((prepared/'PRELIMINARY_RU_PROJECTION.json').read_text(encoding='utf-8'))
    units=projection['units'];separators=projection['separators']
    assert ''.join(part for pair in zip([u['ru_text'] for u in units],separators+['']) for part in pair)==ru
    assert '\n\n\n' in separators
    assert [u['ru_text'] for u in units if u['ru_text'].startswith('<!-- source-page-')]==[
        '<!-- source-page-001 -->','<!-- source-page-002 -->']


def test_reader_loader_keeps_canonical_binding_defaults(tmp_path):
    master=tmp_path/'MASTER_RU.md';master.write_text('Текст',encoding='utf-8')
    projection=tmp_path/'RU_PROJECTION.json';projection.write_text('{}',encoding='utf-8')
    options=dict(schema=reader_projection.SCHEMA,
                 master_ru=dict(path='MASTER_RU.md',**reader_projection.identity(master)),
                 ru_projection=dict(path='semantic_context/RU_PROJECTION.json',
                                    **reader_projection.identity(projection)),
                 source_toc=dict(state='absent',source_pdf_sha256='A'*64,reason='Reviewed'),
                 body_links=[],asset_choices=[],hit_points={},display_roles=[])
    path=tmp_path/'options.json';_write_options(path,options)
    assert reader_projection.load_options(path,master,projection)['master_ru']['path']=='MASTER_RU.md'
    options['ru_projection']['path']='PRELIMINARY_RU_PROJECTION.json';_write_options(path,options)
    with pytest.raises(ValueError,match='master/projection binding'):
        reader_projection.load_options(path,master,projection)


def test_snapshot_deduplicates_and_refuses_overwriting_changes(tmp_path):
    source=tmp_path/'source';source.mkdir()
    for name in ('one.md','two.md'):
        (source/name).write_text('Русский текст',encoding='utf-8')
    archive=tmp_path/'snapshot.zip'
    result=snapshot(source,[Path('.')],archive)
    assert result['files']==2 and result['objects']==1
    assert verify_or_restore(archive)['verified_files']==2
    target=tmp_path/'restore'
    verify_or_restore(archive,target)
    assert (target/'one.md').read_bytes()==(source/'one.md').read_bytes()
    (target/'one.md').write_text('User edits',encoding='utf-8')
    with pytest.raises(ValueError,match='Refusing overwrite'):
        verify_or_restore(archive,target)
