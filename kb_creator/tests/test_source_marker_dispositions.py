import hashlib
import json
from pathlib import Path

import pytest

from kb_creator.pipeline.semantic_structure import validate_semantic_structure
from kb_creator.pipeline.source_marker_dispositions import (
    SCHEMA,
    SourceMarkerDispositionError,
    load_bound_inputs,
    validate,
)


def _sha(text):
    return hashlib.sha256(text.encode()).hexdigest().upper()


def _fixture(*, candidates=(('original_pipeline_txt', 10),), list_sources=(('original_pipeline_txt', 10),), markdown='- one', source_texts=None):
    visual = {'path': 'outputs/04-visual-merge-bundle/visual/original_pipeline_txt/pages/page-155.png', 'bytes': 1, 'sha256': 'A' * 64}
    blocks = []
    selected = []
    source_texts = source_texts or {(view, raw): f'H text {view} {raw}' for view, raw in candidates}
    for view, raw in candidates:
        blocks.append({'raw_index': raw, 'text': source_texts[(view, raw)], 'assets': []})
        selected.append({'view': view, 'raw_index': raw, 'purpose': 'text'})
    packet = {'views': {}}
    for view, raw in candidates:
        packet['views'].setdefault(view, {'blocks': []})['blocks'].append(next(block for block in blocks if block['raw_index'] == raw))
    unit = {'id': 'reviewed-list', 'kind': 'list', 'representation': 'unordered_list',
            'source_blocks': [{'view': view, 'raw_index': raw} for view, raw in list_sources],
            'markdown_span': {'start_line': 1, 'end_line': len(markdown.split('\n')), 'sha256': _sha(markdown)},
            'container_parent': None, 'semantic_parent': None, 'continuation_of': None,
            'heading_level': None, 'item_count': len(list_sources)}
    decision = {'markdown': markdown, 'selected_blocks': selected, 'assets': [],
                'semantic_structure': {'schema': 'kb_creator.page_semantic_structure.v1',
                'review': {'state': 'complete', 'visual': visual}, 'units': [unit]}}
    rows = []
    for view, raw in candidates:
        text = next(block['text'] for block in packet['views'][view]['blocks'] if block['raw_index'] == raw)
        rows.append({'source_page': 155, 'view': view, 'raw_index': raw,
                     'reader_preimage_sha256': _sha(text), 'visual': visual})
    return {155: decision}, {155: packet}, rows


def _input(candidates, dispositions):
    return [{'value': {'schema': SCHEMA, 'candidates': candidates, 'dispositions': dispositions}}]


def _list_disposition(row):
    return {**row, 'disposition': 'unordered_list_item', 'rationale': 'reviewed visual list item'}


def _non_list_disposition(row):
    return {**row, 'disposition': 'non_list', 'rationale': 'reviewed visual footer'}


def test_removed_marker_requires_list_owner_and_valid_list_syntax():
    decisions, packets, candidates = _fixture(list_sources=(), markdown='plain reader text')
    with pytest.raises(SourceMarkerDispositionError, match='lacks one valid list owner'):
        validate(_input(candidates, [_list_disposition(candidates[0])]), decisions, packets)


def test_partial_list_ownership_fails_complete_candidate_domain():
    candidates = (('original_pipeline_txt', 10), ('original_pipeline_txt', 11))
    decisions, packets, rows = _fixture(candidates=candidates, list_sources=(candidates[1],), markdown='- one')
    with pytest.raises(SourceMarkerDispositionError, match='lacks one valid list owner'):
        validate(_input(rows, [_list_disposition(row) for row in rows]), decisions, packets)


def test_equal_raw_index_in_distinct_views_is_not_interchangeable():
    candidates = (('original_pipeline_txt', 3711), ('raster_pipeline_ocr', 3711))
    decisions, packets, rows = _fixture(candidates=candidates, list_sources=(candidates[0],), markdown='- one')
    with pytest.raises(SourceMarkerDispositionError, match='lacks one valid list owner'):
        validate(_input(rows, [_list_disposition(row) for row in rows]), decisions, packets)


def test_explicit_non_list_footer_needs_rationale_and_cannot_create_list_owner():
    decisions, packets, rows = _fixture(list_sources=(), markdown='footer text')
    assert validate(_input(rows, [_non_list_disposition(rows[0])]), decisions, packets)['candidate_count'] == 1
    with pytest.raises(SourceMarkerDispositionError, match='needs a known disposition and reviewer rationale'):
        bad = {**_non_list_disposition(rows[0]), 'rationale': ''}
        validate(_input(rows, [bad]), decisions, packets)


@pytest.mark.parametrize('mutation', ['duplicate', 'stale', 'foreign', 'missing'])
def test_duplicate_stale_foreign_and_missing_candidates_fail_closed(mutation):
    decisions, packets, rows = _fixture()
    dispositions = [_list_disposition(rows[0])]
    if mutation == 'duplicate':
        dispositions.append(dict(dispositions[0]))
        match = 'duplicate'
    elif mutation == 'stale':
        rows[0]['reader_preimage_sha256'] = '0' * 64
        dispositions = [_list_disposition(rows[0])]
        match = 'stale'
    elif mutation == 'foreign':
        foreign = {**dispositions[0], 'raw_index': 99}
        dispositions.append(foreign)
        match = 'incomplete or foreign'
    else:
        rows.append({**rows[0], 'raw_index': 11})
        match = 'incomplete or foreign'
    with pytest.raises(SourceMarkerDispositionError, match=match):
        validate(_input(rows, dispositions), decisions, packets)


def test_complete_list_contract_passes_semantic_validation_end_to_end():
    candidates = (('original_pipeline_txt', 10), ('original_pipeline_txt', 11))
    decisions, packets, rows = _fixture(
        candidates=candidates, list_sources=candidates, markdown='- one\n- two',
        source_texts={candidates[0]: 'one', candidates[1]: 'two'},
    )
    assert validate(_input(rows, [_list_disposition(row) for row in rows]), decisions, packets)['candidate_count'] == 2
    visual = decisions[155]['semantic_structure']['review']['visual']
    assert validate_semantic_structure(decisions, packets, {visual['path']: {'bytes': 1, 'sha256': 'A' * 64}}, required_pages=[155])['pages'][0]['validated_unit_count'] == 1


def test_hash_bound_loader_rejects_stale_and_escaping_sidecars(tmp_path: Path):
    payload = tmp_path / 'marker.json'
    payload.write_text(json.dumps({'schema': SCHEMA, 'candidates': [], 'dispositions': []}), encoding='utf-8')
    spec = tmp_path / 'spec.json'
    spec.write_text(json.dumps({'source_marker_dispositions': {
        'path': payload.name, 'bytes': payload.stat().st_size, 'sha256': _sha(payload.read_text(encoding='utf-8')),
    }}), encoding='utf-8')
    assert load_bound_inputs([spec])[0]['path'] == payload
    payload.write_text('{}', encoding='utf-8')
    with pytest.raises(SourceMarkerDispositionError, match='stale'):
        load_bound_inputs([spec])
    spec.write_text(json.dumps({'source_marker_dispositions': {
        'path': '../marker.json', 'bytes': 1, 'sha256': 'A' * 64,
    }}), encoding='utf-8')
    with pytest.raises(SourceMarkerDispositionError, match='escapes'):
        load_bound_inputs([spec])


def test_review_draft_author_route_consumes_sidecar_after_spec_preparation(tmp_path, monkeypatch):
    from kb_creator.pipeline import source_choice_translation as choices
    from kb_creator.pipeline.source_choice_successor_preparation import prepare_source_choice_successor
    from kb_creator.scripts import author_reviewed_semantic_decisions as author
    from kb_creator.tests import test_source_choice_composite_integration as fixture

    built = fixture._build_r0(
        tmp_path, monkeypatch, whole_block_correction=True, source_marker_binding=True,
    )
    r0_spec = Path(built['spec_paths'][0])
    assert (r0_spec.parent / 'marker-dispositions.json').is_file()
    queue = Path(choices.prepare_v2(built['master'], built['mechanical'], tmp_path / 'queue', binding_root=tmp_path)['queue'])
    selected = [(row['issue_id'], row['provisional_alternative_id']) for row in json.loads(queue.read_text(encoding='utf-8'))['choices']]
    submission = fixture._submission_choices(queue, selected, tmp_path / 'submission.json')
    ledger = Path(choices.record_decisions_v2(queue, submission, tmp_path / 'ledger')['ledger'])
    r1 = prepare_source_choice_successor(
        input_path=built['r0_input'], binding_root=tmp_path, ledger_path=ledger,
        draft_pages=built['draft_pages'], spec_paths=built['spec_paths'], output_dir=tmp_path / 'r1-input',
    )
    r1_spec = Path(r1['spec_paths'][0])
    assert (r1_spec.parent / 'marker-dispositions.json').is_file()
    assert load_bound_inputs([r1_spec])[0]['path'].parent == r1_spec.parent
    authored = tmp_path / 'r1-authored'
    author.author_drafts(
        built['run'], Path(r1['draft_pages']), authored, [r1_spec], mode='review_draft',
        draft_input=Path(r1['input']['path']), binding_root=tmp_path,
    )
    assert (authored / 'review-draft-evidence.json').is_file()
