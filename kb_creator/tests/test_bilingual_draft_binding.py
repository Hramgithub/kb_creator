"""Exact translation reuse must preserve coverage and keep ambiguous splits held."""
import json
import os
from pathlib import Path
import subprocess
import sys

import pytest

from kb_creator.pipeline import bilingual_draft_binding as binding
from kb_creator.pipeline import five_step_language as language


def write(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False), encoding='utf-8')


def fixture(root, text='Hello world.\n', ru='Привет, мир.\n', units=None):
    root.mkdir(exist_ok=True)
    pages = root / 'pages'; pages.mkdir()
    master = root / 'MASTER_EN.md'
    master.write_text('<!-- source-page-001 -->\n\n' + text, encoding='utf-8')
    glossary = root / 'terms.json'; write(glossary, {})
    spans = root / 'EN_SOURCE_SPANS.json'; write(spans, {})
    page = {'source_page': 1, 'source_markdown_sha256': binding._sha(text),
            'en_markdown': text, 'ru_markdown': ru, 'unresolved': []}
    write(pages / 'page-001.json', page)
    assets = root / 'assets.json'; write(assets, {'assets': []})
    sources = ['<!-- source-page-001 -->'] + (units if units is not None else [text.strip()])
    task = {'schema': 'kb_creator.five_step_language_draft_task.v2',
            'units': [{'unit_id': f'unit-{i}', 'source_text': value, 'source_hash': binding._sha(value)} for i, value in enumerate(sources)]}
    for key, path in [('master_en', master), ('glossary', glossary), ('source_spans', spans)]:
        task[key] = {'path': path.name, **binding._identity(path)}
        task[key + '_path'] = str(path)
    task_path = root / 'draft.task.json'; write(task_path, binding._seal(task, 'task_sha256'))
    template = {'schema': 'kb_creator.five_step_language_draft_submission.v2',
                'task': {'path': task_path.name, **binding._identity(task_path)},
                'master_en': task['master_en'], 'glossary': task['glossary'],
                'units': [{'unit_id': row['unit_id'], 'source_hash': row['source_hash'], 'ru_text': '', 'unresolved': []} for row in task['units']]}
    template_path = root / 'draft.template.json'; write(template_path, template)
    return task_path, template_path, pages, assets, root / 'bound'


def v3_fixture(root, text='Hello world.\n', ru='Привет, мир.\n'):
    source = root / 'source'; source.mkdir()
    master = source / 'MASTER_EN.md'; master.write_text('<!-- source-page-001 -->\n\n' + text, encoding='utf-8')
    spans = source / 'EN_SOURCE_SPANS.json'
    write(spans, language._seal('kb_creator.five_step_en_source_spans.v1', {
        'master_en': {'path': 'MASTER_EN.md', 'bytes': master.stat().st_size, 'sha256': language._fsha(master)}, 'spans': [],
    }, 'spans_sha256'))
    glossary = root / 'terms.json'; write(glossary, {'terms': [{'source': 'Hello', 'target': 'Привет'}]})
    language_root = root / 'language'; prepared = language.prepare_language(master, glossary, language_root, max_batch_chars=128)
    pages = root / 'pages'; pages.mkdir(); write(pages / 'page-001.json', {
        'source_page': 1, 'source_markdown_sha256': binding._sha(text),
        'en_markdown': text, 'ru_markdown': ru, 'unresolved': [],
    })
    assets = root / 'assets.json'; write(assets, {'assets': []})
    return prepared, language_root, pages, assets, root / 'bound'


def page_mapping(task_path, assets, pages, *, units, ru, modes=None):
    task = json.loads(task_path.read_text(encoding='utf-8'))
    page = json.loads((pages / 'page-001.json').read_text(encoding='utf-8'))
    raw = ru.encode('utf-8'); cursor = 0; rows = []
    for index, unit in enumerate(units):
        text = unit['ru_text']; encoded = text.encode('utf-8'); start = raw.index(encoded, cursor); end = start + len(encoded)
        mode = (modes or ['exact_slice'] * len(units))[index]
        rows.append({'unit_id': unit['unit_id'], 'source_hash': unit['source_hash'],
                     'ru_span': {'start_byte': start, 'end_byte': end}, 'ru_slice_sha256': binding._sha(text),
                     'ru_text': text, 'mode': mode, 'reason': 'reviewed whitespace' if mode != 'exact_slice' else '', 'unresolved': []})
        cursor = end
    value = {'schema': 'kb_creator.bilingual_explicit_page_mappings.v1',
             'task': {'path': task_path.name, **binding._identity(task_path)},
             'asset_manifest': {'path': assets.name, **binding._identity(assets)},
             'pages': [{'source_page': 1, 'reviewed_page': {'path': 'page-001.json', **binding._identity(pages / 'page-001.json')},
                        'post_en_sha256': binding._sha(page['en_markdown']), 'post_ru_sha256': binding._sha(page['ru_markdown']),
                        'units': rows}]}
    return binding._seal(value, 'mapping_sha256')


def test_canonical_v3_prepare_bind_then_submit_documentary_draft(tmp_path):
    prepared, language_root, pages, assets, output = v3_fixture(tmp_path)
    task = json.loads(prepared['task_path'].read_text(encoding='utf-8'))
    assert task['schema'] == 'kb_creator.five_step_language_draft_task.v3'
    report = binding.bind(prepared['task_path'], prepared['template_path'], pages, assets, output)
    drafted = language.submit_draft(language_root, output / 'draft.submission.json', tmp_path / 'documentary')
    assert report['state'] == 'candidate_ready_for_draft_submission'
    assert drafted['state'] == 'needs_agent_work'


def test_complete_page_mapping_clears_topology_hold_and_archives_authority(tmp_path):
    prepared, language_root, pages, assets, output = v3_fixture(
        tmp_path, 'Hello.\n\nAgain.\n', 'Привет.\nСнова.\n')
    task = json.loads(prepared['task_path'].read_text(encoding='utf-8'))
    authority = tmp_path / 'page-map.json'
    mapped_units = [{**unit, 'ru_text': text} for unit, text in zip(task['units'][1:], ['Привет.', 'Снова.'])]
    write(authority, page_mapping(prepared['task_path'], assets, pages, units=mapped_units, ru='Привет.\nСнова.\n'))
    report = binding.bind(prepared['task_path'], prepared['template_path'], pages, assets, output,
                          explicit_translations=authority)
    submitted = language.submit_draft(language_root, output / 'draft.submission.json', tmp_path / 'documentary')
    assert report['state'] == 'candidate_ready_for_draft_submission'
    assert [row['method'] for row in report['binding_methods'][1:]] == ['explicit_page_exact_slice'] * 2
    assert report['archived_explicit_page_mapping']['path'] == 'explicit-page-mapping.json'
    assert (output / 'explicit-page-mapping.json').read_bytes() == authority.read_bytes()
    assert submitted['state'] == 'needs_agent_work'


@pytest.mark.parametrize('damage', ['missing', 'reordered', 'gap', 'stale_asset', 'sealed_mutation'])
def test_page_mapping_fails_closed_before_output(tmp_path, damage):
    prepared, _, pages, assets, output = v3_fixture(tmp_path, 'Hello.\n\nAgain.\n', 'Привет.\nСнова.\n')
    task = json.loads(prepared['task_path'].read_text(encoding='utf-8'))
    mapped_units = [{**unit, 'ru_text': text} for unit, text in zip(task['units'][1:], ['Привет.', 'Снова.'])]
    authority = page_mapping(prepared['task_path'], assets, pages, units=mapped_units, ru='Привет.\nСнова.\n')
    units = authority['pages'][0]['units']
    if damage == 'missing': authority['pages'][0]['units'].pop()
    elif damage == 'reordered': authority['pages'][0]['units'].reverse()
    elif damage == 'gap':
        units[1]['ru_span']['start_byte'] += len('С'.encode('utf-8'))
        units[1]['ru_text'] = 'нова.'; units[1]['ru_slice_sha256'] = binding._sha('нова.')
    elif damage == 'stale_asset': authority['asset_manifest']['sha256'] = 'F' * 64
    if damage != 'sealed_mutation': authority = binding._seal({key: value for key, value in authority.items() if key != 'mapping_sha256'}, 'mapping_sha256')
    else: authority['pages'][0]['post_ru_sha256'] = 'F' * 64
    path = tmp_path / 'page-map.json'; write(path, authority)
    with pytest.raises(binding.BilingualDraftBindingError):
        binding.bind(prepared['task_path'], prepared['template_path'], pages, assets, output, explicit_translations=path)
    assert not output.exists()


def test_page_mapping_rejects_plain_text_mode_for_structured_unit(tmp_path):
    prepared, _, pages, assets, output = v3_fixture(
        tmp_path, '[One](https://one.example)\n\n[Two](https://two.example)\n',
        '[Один](https://one.example)\n[Два](https://two.example)\n')
    task = json.loads(prepared['task_path'].read_text(encoding='utf-8'))
    mapped_units = [{**unit, 'ru_text': text} for unit, text in zip(task['units'][1:],
                    ['[Один](https://one.example)', '[Два](https://two.example)'])]
    authority = page_mapping(prepared['task_path'], assets, pages, units=mapped_units,
                             ru='[Один](https://one.example)\n[Два](https://two.example)\n',
                             modes=['reviewed_plain_text_whitespace', 'exact_slice'])
    path = tmp_path / 'page-map.json'; write(path, authority)
    with pytest.raises(binding.BilingualDraftBindingError, match='plain-text whitespace'):
        binding.bind(prepared['task_path'], prepared['template_path'], pages, assets, output, explicit_translations=path)
    assert not output.exists()


@pytest.mark.parametrize('damage', ['context', 'units'])
def test_resealed_v3_task_rejects_stale_context_or_source_segmentation(tmp_path, damage):
    prepared, _, pages, assets, output = v3_fixture(tmp_path)
    task_path, template_path = prepared['task_path'], prepared['template_path']
    task = json.loads(task_path.read_text(encoding='utf-8'))
    if damage == 'context':
        task['source_unit_context'][0]['unit_id'] = 'forged-unit'
    else:
        task['units'][1]['source_text'] = 'Forged text.'
        task['units'][1]['source_hash'] = binding._sha('Forged text.')
    write(task_path, language._seal(task['schema'], {key: value for key, value in task.items() if key not in {'schema', 'task_sha256'}}, 'task_sha256'))
    template = json.loads(template_path.read_text(encoding='utf-8')); template['task'] = {'path': task_path.name, **binding._identity(task_path)}
    if damage == 'units': template['units'][1]['source_hash'] = task['units'][1]['source_hash']
    write(template_path, template)
    with pytest.raises(binding.BilingualDraftBindingError, match='v3 canonical source context'):
        binding.bind(task_path, template_path, pages, assets, output)
    assert not output.exists()


def test_repeated_units_map_in_source_order_and_input_is_immutable(tmp_path):
    args = fixture(tmp_path, 'Hello.\n\nHello.\n', 'Первый.\n\nВторой.\n', ['Hello.', 'Hello.'])
    before = args[0].read_bytes()
    result = binding.bind(*args)
    submission = json.loads((args[-1] / 'draft.submission.json').read_text(encoding='utf-8'))
    assert [row['ru_text'] for row in submission['units']] == ['<!-- source-page-001 -->', 'Первый.', 'Второй.']
    assert result['holds'] == [] and result['acceptance_inferred'] is False
    assert args[0].read_bytes() == before


@pytest.mark.parametrize('text,held', [('Hello. \n', False), (' Hello.\n', False), ('    Hello.\n', True), ('Hello.  \n', True), ('Hello.\t\n', True)])
def test_edge_whitespace_does_not_erase_markdown_delimiters(tmp_path, text, held):
    args = fixture(tmp_path, text, 'Привет.\n', ['Hello.'])
    result = binding.bind(*args)
    assert bool(result['holds']) is held


def test_all_split_holds_are_reported_and_explicit_translations_advance_cursor(tmp_path):
    args = fixture(tmp_path, 'Hello world.\n', 'Привет, мир.\n', ['Hello', 'world.'])
    report = binding.bind(*args)
    assert len(report['holds']) == 2
    task = json.loads(args[0].read_text())
    explicit = tmp_path / 'explicit.json'
    rows = [{'unit_id': row['unit_id'], 'source_hash': row['source_hash'], 'ru_text': ru, 'unresolved': []}
            for row, ru in zip(task['units'][1:], ['Привет,', 'мир.'])]
    write(explicit, {'schema': 'kb_creator.bilingual_explicit_unit_translations.v1', 'units': rows})
    ready = binding.bind(*args[:-1], tmp_path / 'resolved', explicit_translations=explicit)
    assert ready['holds'] == []


@pytest.mark.parametrize('mutation', ['master', 'glossary', 'page_hash', 'missing_page', 'template_hash', 'omitted_unit', 'duplicate_unit', 'unit_hash'])
def test_stale_or_incomplete_source_authority_rejected_before_output(tmp_path, mutation):
    args = fixture(tmp_path, 'Hello.\n\nAgain.\n', 'Привет.\n\nСнова.\n', ['Hello.', 'Again.'])
    task = json.loads(args[0].read_text())
    if mutation in {'master', 'glossary'}:
        key = 'master_en' if mutation == 'master' else 'glossary'
        Path(task[key + '_path']).write_text('changed')
    elif mutation == 'missing_page':
        (args[2] / 'page-001.json').unlink()
    elif mutation == 'page_hash':
        p = args[2] / 'page-001.json'; value = json.loads(p.read_text()); value['en_markdown'] += 'changed'; write(p, value)
    elif mutation == 'template_hash':
        value = json.loads(args[1].read_text()); value['units'][1]['source_hash'] = 'F' * 64; write(args[1], value)
    else:
        if mutation == 'omitted_unit': task['units'].pop()
        elif mutation == 'duplicate_unit': task['units'].append(task['units'][-1])
        else: task['units'][1]['source_hash'] = 'F' * 64
        task.pop('task_sha256'); write(args[0], binding._seal(task, 'task_sha256'))
        template = json.loads(args[1].read_text()); template['task'] = {'path': args[0].name, **binding._identity(args[0])}; write(args[1], template)
    with pytest.raises(binding.BilingualDraftBindingError): binding.bind(*args)
    assert not args[-1].exists()


@pytest.mark.parametrize('mutation', ['unknown', 'stale', 'duplicate', 'marker'])
def test_explicit_override_identity_is_strict(tmp_path, mutation):
    args = fixture(tmp_path)
    task = json.loads(args[0].read_text()); unit = task['units'][0 if mutation == 'marker' else 1]
    row = {'unit_id': unit['unit_id'], 'source_hash': unit['source_hash'], 'ru_text': 'Текст', 'unresolved': []}
    if mutation == 'unknown': row['unit_id'] = 'absent'
    if mutation == 'stale': row['source_hash'] = 'F' * 64
    path = tmp_path / 'explicit.json'
    write(path, {'schema': 'kb_creator.bilingual_explicit_unit_translations.v1', 'units': [row, row] if mutation == 'duplicate' else [row]})
    with pytest.raises(binding.BilingualDraftBindingError): binding.bind(*args, explicit_translations=path)
    assert not args[-1].exists()


def test_page_diagnostics_remain_blocked(tmp_path):
    args = fixture(tmp_path)
    path = args[2] / 'page-001.json'; row = json.loads(path.read_text()); row['unresolved'] = ['name uncertain']; write(path, row)
    assert binding.bind(*args)['state'] == 'blocked'


def test_ru_text_in_source_paragraph_gap_cannot_disappear(tmp_path):
    args = fixture(tmp_path, 'Hello.\n\nAgain.\n', 'Привет.\nНе потерять.\nСнова.\n', ['Hello.', 'Again.'])
    report = binding.bind(*args)
    assert report['state'] == 'blocked'
    assert any('blank-line topology' in str(row['detail']) for row in report['holds'])


def test_ru_text_on_an_empty_source_page_is_held(tmp_path):
    assert binding.bind(*fixture(tmp_path, '\n', 'Не потерять.\n', []))['state'] == 'blocked'


def test_cli_runs_without_test_pythonpath(tmp_path):
    args = fixture(tmp_path)
    cmd = [sys.executable, '-B', '-m', 'kb_creator.scripts.bind_bilingual_page_drafts']
    for name, value in zip(['task', 'template', 'pages', 'asset-manifest', 'output'], args): cmd.extend(['--' + name, str(value)])
    env = dict(os.environ); env.pop('PYTHONPATH', None)
    result = subprocess.run(cmd, capture_output=True, text=True, env=env, cwd=Path(__file__).resolve().parents[2])
    assert result.returncode == 0, result.stderr
    assert 'candidate_ready_for_draft_submission' in result.stdout


@pytest.mark.parametrize('ru', ['Привет.\nЛишняя строка.\n', '\n'])
def test_unprovable_or_empty_ru_unit_is_held(tmp_path, ru):
    assert binding.bind(*fixture(tmp_path, ru=ru))['state'] == 'blocked'


@pytest.mark.parametrize('mutation', ['none', 'missing', 'unsafe', 'changed_link'])
def test_assets_bind_only_through_exact_formal_page(tmp_path, mutation):
    args = fixture(tmp_path, '![Map]({{asset:map}})\n', '![Карта]({{asset:map}})\n')
    task = json.loads(args[0].read_text())
    master = Path(task['master_en_path'])
    master.write_text(master.read_text().replace('{{asset:map}}', 'assets/map.png'))
    task['master_en'] = {'path': master.name, **binding._identity(master)}
    task['units'][1].update(source_text='![Map](assets/map.png)', source_hash=binding._sha('![Map](assets/map.png)'))
    task.pop('task_sha256'); write(args[0], binding._seal(task, 'task_sha256'))
    template = json.loads(args[1].read_text()); template.update(task={'path': args[0].name, **binding._identity(args[0])}, master_en=task['master_en'])
    template['units'][1]['source_hash'] = task['units'][1]['source_hash']; write(args[1], template)
    path = '../escape.png' if mutation == 'unsafe' else 'assets/wrong.png' if mutation == 'changed_link' else 'assets/map.png'
    write(args[3], {'assets': [] if mutation == 'missing' else [{'logical_name': 'map', 'stored_path': path}]})
    if mutation == 'none':
        assert binding.bind(*args)['holds'] == []
        submission = json.loads((args[-1] / 'draft.submission.json').read_text(encoding='utf-8'))
        assert submission['units'][1]['ru_text'] == '![Карта](assets/map.png)'
    else:
        with pytest.raises(binding.BilingualDraftBindingError): binding.bind(*args)
        assert not args[-1].exists()
