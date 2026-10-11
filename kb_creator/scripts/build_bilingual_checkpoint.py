"""Save preliminary bilingual pages as a readable DOCX without claiming release.

This recovery command does not replace continue_language or continue_docx gates.
It preserves all preliminary content, including unresolved source/TOC artifacts.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import zipfile
from pathlib import Path

from lxml import etree, html
from translator.translator import markdown_to_review_html
from kb_creator.scripts.production_docx import build_docx_projection
from kb_creator.pipeline import reader_projection
from kb_creator.pipeline.reader_block_relocation import verify_docx as verify_relocated_docx
from kb_creator.pipeline.reader_statblock_grouping import verify_xml as verify_grouped_statblocks
from kb_creator.pipeline.five_step_docx import (
    verify_duplicate_text_docx, verify_reflow_docx, verify_retained_links_docx,
    verify_retained_artwork_docx, verify_rich_source_toc_docx,
)


def compile_pages(paths: list[Path]) -> tuple[str, str, list[dict]]:
    rows = [json.loads(p.read_text(encoding='utf-8')) for p in paths]
    pages = [r['source_page'] for r in rows]
    if pages != list(range(1, len(rows) + 1)) or not rows:
        raise ValueError('Pages must be a nonempty contiguous sequence beginning at1')
    for row in rows:
        if not all(isinstance(row.get(k), str) for k in ('en_markdown','ru_markdown')):
            raise ValueError('Both language fields must be strings')
    combined = []
    for key in ('en_markdown','ru_markdown'):
        combined.append('\n\n'.join(f'<!-- source-page-{r["source_page"]:03} -->\n\n{r[key]}' for r in rows))
    return combined[0], combined[1], rows


def identity(path: Path) -> dict:
    return dict(bytes=path.stat().st_size,sha256=hashlib.sha256(path.read_bytes()).hexdigest().upper())


def _json(path: Path, value: dict) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2)+'\n', encoding='utf-8', newline='\n')


def _projection(ru: str, ru_file: Path) -> dict:
    # Keep separators as exact source bytes: the language parser intentionally
    # strips them, which would alter reviewed preliminary page Markdown.
    parts = re.split(r'((?:\r?\n)[ \t]*(?:\r?\n)(?:[ \t]*\r?\n)*)', ru)
    blocks, separators = parts[::2], parts[1::2]
    if (not blocks or any(not block.strip() for block in blocks)
            or len(separators) != len(blocks)-1
            or ''.join(part for pair in zip(blocks, separators+['']) for part in pair) != ru):
        raise ValueError('Preliminary RU block partition is incomplete or ambiguous')
    units = [dict(unit_id=f'prelim-unit-{i:05}', source_hash=hashlib.sha256(block.encode()).hexdigest().upper(),
                  parent_unit_id=None, part_index=None, part_count=None,
                  ru_text=block, ru_sha256=hashlib.sha256(block.encode()).hexdigest().upper())
             for i, block in enumerate(blocks, 1)]
    value = dict(schema='kb_creator.preliminary_ru_projection.v1',
                 preliminary_ru=dict(path='PRELIMINARY_RU.md', **identity(ru_file)),
                 unit_order=[row['unit_id'] for row in units], units=units,
                 separators=separators, spans=[])
    value['projection_sha256'] = reader_projection.seal(value)
    return value


def _assets(text: str, asset_root: Path) -> list[tuple[str, Path]]:
    root = asset_root.resolve(strict=True)
    refs = sorted(set(re.findall(r'!\[[^\]]*\]\(([^)\s]+)\)', text)))
    assets = []
    for ref in refs:
        relative = Path(ref)
        if relative.is_absolute() or '..' in relative.parts or ':' in ref:
            raise ValueError(f'Unsafe or missing asset: {ref}')
        unresolved = root / relative
        if any(path.is_symlink() for path in [unresolved, *unresolved.parents] if path != root.parent):
            raise ValueError(f'Unsafe or missing asset: {ref}')
        source = (root / relative).resolve(strict=True)
        if not source.is_relative_to(root) or not source.is_file():
            raise ValueError(f'Unsafe or missing asset: {ref}')
        assets.append((ref, source))
    return assets


def prepare(pages: Path, asset_root: Path, source_pdf: Path, output: Path) -> dict:
    if output.exists():
        raise ValueError('Prepared output must be a fresh directory')
    inputs = sorted(pages.glob('page-*.json'))
    _, ru, _ = compile_pages(inputs)
    assets = _assets(ru, asset_root)
    if not source_pdf.is_file() or source_pdf.is_symlink():
        raise ValueError('Source PDF must be a regular file')
    output.mkdir(parents=True)
    for ref, source in assets:
        target = output/ref
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, target)
    ru_file = output/'PRELIMINARY_RU.md'
    ru_file.write_text(ru, encoding='utf-8', newline='\n')
    projection_file = output/'PRELIMINARY_RU_PROJECTION.json'
    _json(projection_file, _projection(ru, ru_file))
    source = identity(source_pdf)
    template = dict(schema=reader_projection.SCHEMA,
                    master_ru=dict(path='PRELIMINARY_RU.md', **identity(ru_file)),
                    ru_projection=dict(path='PRELIMINARY_RU_PROJECTION.json', **identity(projection_file)),
                    source_toc=dict(state='unresolved', source_pdf_sha256=source['sha256'],
                                    reason='Review source TOC against the exact source PDF'),
                    body_links=[], asset_choices=[], hit_points={}, display_roles=[])
    template['options_sha256'] = reader_projection.seal(template)
    _json(output/'reader_options.template.json', template)
    manifest = dict(schema='kb_creator.preliminary_reader_prepare.v1',
                    pages=[dict(path=p.name, **identity(p)) for p in inputs],
                    preliminary_ru=dict(path='PRELIMINARY_RU.md', **identity(ru_file)),
                    projection=dict(path='PRELIMINARY_RU_PROJECTION.json', **identity(projection_file)),
                    assets=[dict(path=ref, **identity(source)) for ref, source in assets],
                    source_pdf=source, accepted=False, release_ready=False)
    manifest['prepare_sha256'] = reader_projection.seal(manifest)
    _json(output/'PREPARE.json', manifest)
    return dict(state='needs_reader_review', projection=projection_file.as_posix(),
                template=(output/'reader_options.template.json').as_posix(), units=len(_projection(ru, ru_file)['units']))


def _prepared(prepared: Path, inputs: list[Path], ru: str, source_pdf: Path,
              asset_root: Path) -> tuple[Path, dict]:
    manifest = json.loads((prepared/'PREPARE.json').read_text(encoding='utf-8'))
    digest = manifest.pop('prepare_sha256', None)
    if (manifest.get('schema') != 'kb_creator.preliminary_reader_prepare.v1'
            or digest != reader_projection.seal(manifest)
            or manifest.get('pages') != [dict(path=p.name, **identity(p)) for p in inputs]
            or manifest.get('source_pdf') != identity(source_pdf)
            or manifest.get('accepted') is not False or manifest.get('release_ready') is not False):
        raise ValueError('Preliminary prepare page/source binding mismatch')
    ru_file = prepared/'PRELIMINARY_RU.md'
    projection_file = prepared/'PRELIMINARY_RU_PROJECTION.json'
    if (manifest.get('preliminary_ru') != dict(path=ru_file.name, **identity(ru_file))
            or ru_file.read_text(encoding='utf-8') != ru
            or manifest.get('projection') != dict(path=projection_file.name, **identity(projection_file))):
        raise ValueError('Preliminary prepare master/projection binding mismatch')
    expected_assets = [dict(path=ref, **identity(source)) for ref, source in _assets(ru, asset_root)]
    if manifest.get('assets') != expected_assets or any(
        not (prepared/row['path']).is_file() or identity(prepared/row['path']) !=
        {key: row[key] for key in ('bytes', 'sha256')} for row in expected_assets
    ):
        raise ValueError('Preliminary prepare asset binding mismatch')
    projection = json.loads(projection_file.read_text(encoding='utf-8'))
    projection_digest = projection.pop('projection_sha256', None)
    expected = _projection(ru, ru_file)
    expected.pop('projection_sha256')
    if projection_digest != reader_projection.seal(projection) or projection != expected:
        raise ValueError('Preliminary projection changed or does not reconstruct input')
    return projection_file, projection


def build(pages: Path, asset_root: Path, config: Path, output: Path, *,
          prepared: Path | None = None, reader_options: Path | None = None,
          source_pdf: Path | None = None) -> dict:
    if output.exists():
        raise ValueError('Output must be a fresh directory')
    inputs = sorted(pages.glob('page-*.json'))
    en, ru, rows = compile_pages(inputs)
    if (prepared is None) != (reader_options is None):
        raise ValueError('Prepared projection and reader options must be supplied together')
    projection = options = None
    if prepared is not None:
        if source_pdf is None or not source_pdf.is_file() or source_pdf.is_symlink():
            raise ValueError('Reader build needs the exact source PDF')
        projection_file, projection = _prepared(prepared, inputs, ru, source_pdf, asset_root)
        options = reader_projection.load_options(
            reader_options, prepared/'PRELIMINARY_RU.md', projection_file,
            master_name='PRELIMINARY_RU.md', projection_name='PRELIMINARY_RU_PROJECTION.json')
        if options['source_toc'].get('source_pdf_sha256') != identity(source_pdf)['sha256']:
            raise ValueError('Reader source PDF binding mismatch')
        if (re.search(r'^#{1,6}\s+(?:Содержание|Оглавление|Contents|Table of contents)\s*$', ru, re.M | re.I)
                and options['source_toc'].get('state') != 'present'):
            raise ValueError('Source TOC detected: reviewed present TOC reader options required')
    assets = _assets(en+'\n'+ru, asset_root)
    profile = json.loads(config.read_text(encoding='utf-8-sig'))
    output.mkdir(parents=True)
    (output/'pages').mkdir()
    for path in inputs:
        shutil.copyfile(path,output/'pages'/path.name)
    for ref, source in assets:
        target=output/ref
        target.parent.mkdir(parents=True,exist_ok=True)
        shutil.copyfile(source,target)
    (output/'PRELIMINARY_EN.md').write_text(en,encoding='utf-8')
    if prepared is not None:
        shutil.copyfile(prepared/'PRELIMINARY_RU.md', output/'PRELIMINARY_RU.md')
        if identity(output/'PRELIMINARY_RU.md') != {key: options['master_ru'][key]
                                                  for key in ('bytes','sha256')}:
            raise ValueError('Archived preliminary RU differs from sealed reader input')
    else:
        (output/'PRELIMINARY_RU.md').write_text(ru,encoding='utf-8')
    shutil.copyfile(config,output/'docx_config.json')
    body, toc, page_count=markdown_to_review_html(ru,source_path=output/'PRELIMINARY_RU.md',html_path=output/'.word-projection-base',blockquote_heading_offset=0 if options else 1)
    reader_report = None
    if options is not None:
        body, toc, reader_report = reader_projection.project_reader_html(
            body, toc, projection, options, options_path=reader_options, master_root=output)
        profile = reader_projection.copy_reader_assets(reader_report, reader_options, output, profile)
        _json(output/'docx_config.effective.json', profile)
        _json(output/'READER_PROJECTION.json', reader_report)
        shutil.copyfile(prepared/'PRELIMINARY_RU_PROJECTION.json', output/'PRELIMINARY_RU_PROJECTION.json')
        shutil.copyfile(reader_options, output/'reader_options.json')
        shutil.copyfile(prepared/'PREPARE.json', output/'PREPARE.json')
    root=html.fromstring('<html><head><meta charset="utf-8"></head><body><main>'+body+'</main></body></html>')
    for marker in root.xpath('//*[contains(concat(" ",normalize-space(@class)," ")," page-marker ")]'):
        marker.getparent().remove(marker)
    main=root.xpath('//main')[0]
    notice=html.fragment_fromstring('<p>Рабочий перевод для предварительного чтения. Окончательная сверка с источником, оформление содержания и полная проверка вёрстки ещё не завершены.</p>')
    main.insert(0,notice)
    result=build_docx_projection(root,output,output/'document.docx',config=profile)
    with zipfile.ZipFile(output/'document.docx') as archive:
        xml=etree.fromstring(archive.read('word/document.xml'))
        ns={'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
        paragraphs=[''.join(p.xpath('.//w:t/text()',namespaces=ns)) for p in xml.xpath('//w:body//w:p',namespaces=ns)]
        if reader_report is not None:
            from kb_creator.scripts.production_docx import bookmark_name
            bookmarks=xml.xpath('//w:bookmarkStart/@w:name',namespaces=ns)
            links=xml.xpath('//w:hyperlink/@w:anchor',namespaces=ns)
            for link in reader_report['links']:
                name=bookmark_name(link['target'])
                if bookmarks.count(name)!=1 or name not in links:
                    raise ValueError(f"Reader link not preserved in DOCX: {link['target']}")
            raw_xml=archive.read('word/document.xml')
            verify_rich_source_toc_docx(reader_report,raw_xml)
            verify_duplicate_text_docx(reader_report,raw_xml)
            verify_reflow_docx(reader_report,raw_xml)
            verify_retained_links_docx(reader_report,raw_xml)
            verify_retained_artwork_docx(reader_report,output/'document.docx')
            verify_relocated_docx(reader_report,output/'document.docx')
            verify_grouped_statblocks(reader_report, raw_xml,
                                     keep_together=profile.get('statblocks', {}).get('keep_together', False))
            for anchor in reader_report['review_anchors']:
                if bookmarks.count(bookmark_name(anchor['anchor']))!=1:
                    raise ValueError('Reader review anchor not preserved in DOCX')
            embedded={hashlib.sha256(archive.read(name)).hexdigest().upper() for name in archive.namelist() if name.startswith('word/media/')}
            for choice in reader_report['asset_choices']:
                if choice['selected']['sha256'] not in embedded:
                    raise ValueError('Reader selected image not embedded in DOCX')
            for group in reader_report.get('source_figure_regions',[]):
                for region in group['regions']:
                    if region['selected']['sha256'] not in embedded:
                        raise ValueError('Reader selected source region not embedded in DOCX')
    (output/'DOCX_EXTRACTED_TEXT.txt').write_text('\n\n'.join(paragraphs),encoding='utf-8')
    # Detect dropped text through the actual serialized DOCX, without claiming literary QA.
    normalize=lambda s:re.sub(r'\s+','',s)
    xml_text=normalize(''.join(paragraphs))
    missing=[]
    for node in main.xpath('.//p|.//li|.//h1|.//h2|.//h3|.//h4|.//h5|.//h6|.//td|.//th|.//figcaption'):
        text=normalize(node.text_content())
        if text and text not in xml_text:
            missing.append(node.text_content())
    report=dict(schema='kb_creator.bilingual_preservation_checkpoint.v1',state='working_DOCX_pending_source_binding_and_full_QA',
        accepted=False,release_ready=False,pages=len(rows),rendered_source_pages=page_count,assets=len(assets),
        build=result,text_closure=dict(checked=True,missing_blocks=missing),
        source_pages=[dict(path=p.name,**identity(p)) for p in inputs],
        docx=identity(output/'document.docx'))
    if reader_report is not None:
        report['reader_projection']=reader_report
        report['reader_options']=identity(reader_options)
        report['preliminary_prepare']=identity(prepared/'PREPARE.json')
    (output/'CHECKPOINT.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    if missing:
        raise ValueError(f'DOCX text closure found {len(missing)} missing blocks; preserved output for diagnosis')
    return {k:report[k] for k in ('state','pages','assets','text_closure','docx')}


def main() -> None:
    parser=argparse.ArgumentParser(description=__doc__)
    for name in ('pages','asset-root','config','output','prepared','reader-options','source-pdf'):
        parser.add_argument('--'+name,type=Path,required=name in ('pages','output'))
    parser.add_argument('--prepare',action='store_true',help='Write sealed preliminary RU projection and reader template')
    args=parser.parse_args()
    if args.prepare:
        if args.source_pdf is None or args.asset_root is None:
            parser.error('--prepare requires --source-pdf and --asset-root')
        result=prepare(args.pages,args.asset_root,args.source_pdf,args.output)
    else:
        if args.asset_root is None or args.config is None:
            parser.error('build requires --asset-root and --config')
        result=build(args.pages,args.asset_root,args.config,args.output,
                     prepared=args.prepared,reader_options=args.reader_options,source_pdf=args.source_pdf)
    print(json.dumps(result,ensure_ascii=False))


if __name__ == '__main__':
    main()
