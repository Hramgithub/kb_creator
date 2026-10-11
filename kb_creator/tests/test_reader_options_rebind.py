from __future__ import annotations
import json
from pathlib import Path
import pytest
from kb_creator.pipeline import reader_options_rebind as subject
from kb_creator.pipeline import reader_projection
from kb_creator.pipeline.identity import file_identity
from kb_creator.pipeline.language_draft_reuse import prepare_reused_draft
from kb_creator.pipeline import language_continuation as continuation
from kb_creator.tests.test_language_draft_reuse import reuse_inputs
from kb_creator.tests.test_language_continuation import predecessor, _read, _write

def _options(root: Path, result: Path, *, binding=True, asset=False, regions=False):
    projection=_read(result/'semantic_context/RU_PROJECTION.json'); master=result/'MASTER_RU.md'; unit=projection['units'][1]
    value={'schema':reader_projection.SCHEMA,'master_ru':{'path':'MASTER_RU.md',**file_identity(master)},'ru_projection':{'path':'semantic_context/RU_PROJECTION.json',**file_identity(result/'semantic_context/RU_PROJECTION.json')},'source_toc':{},'body_links':[{'unit':{'unit_id':unit['unit_id'],'ru_sha256':unit['ru_sha256']}}] if binding else [],'asset_choices':[],'hit_points':{},'display_roles':[]}
    if asset:
        original=next((result/'assets').glob('*')); selected=root/'selected/replacement.bin'; selected.parent.mkdir(); selected.write_bytes(b'replacement')
        value['asset_choices']=[{'original_ref':original.relative_to(result).as_posix(),'original':file_identity(original),'selected_ref':'selected/replacement.bin','selected':file_identity(selected),'provenance':'review fixture','reason':'review fixture'}]
    if regions:
        selected=root/'selected/region.bin'; selected.parent.mkdir(exist_ok=True); selected.write_bytes(b'region-native')
        value['display_roles']=[{'role':'source_figure_regions','regions':[
            {'id':'top','selected_ref':'selected/region.bin','selected':file_identity(selected)},
            {'id':'bottom','selected_ref':'selected/region.bin','selected':file_identity(selected)},
        ]}]
    value['options_sha256']=reader_projection.seal(value); _write(root/'options.json',value); return root/'options.json'

def _second_final(prior, target, tmp_path, *, changed=False):
    reuse=prepare_reused_draft(prior,target,tmp_path/'reuse'); drafted=continuation.submit_continuation(target,tmp_path/'reuse/draft.submission.json',tmp_path/'drafted')
    proof=_read(Path(drafted['template_path']))
    for row in proof['units']: row['disposition']='checked_unchanged'
    if changed:
        row=next(row for row in proof['units'] if not row['final_ru_text'].startswith('<!--'))
        row['final_ru_text']+=' изменено'; row['disposition']='changed'; row['reason']='fixture change'
    _write(tmp_path/'proof.json',proof); return Path(continuation.submit_continuation(tmp_path/'drafted',tmp_path/'proof.json',tmp_path/'new-final')['final_root'])

def _authorizations(path: Path, prior: Path, current: Path):
    old={row['unit_id']:row for row in _read(prior/'semantic_context/RU_PROJECTION.json')['units']}
    new={row['unit_id']:row for row in _read(current/'semantic_context/RU_PROJECTION.json')['units']}
    rows=[{'unit_id':unit_id,'prior_ru_sha256':row['ru_sha256'],'current_ru_sha256':new[unit_id]['ru_sha256'],'reason':'reviewed punctuation correction'}
          for unit_id,row in old.items() if row['ru_sha256'] != new[unit_id]['ru_sha256']]
    _write(path,rows); return path,rows

def test_rebind_valid_real_language_results(reuse_inputs,tmp_path):
    prior,target=reuse_inputs; current=_second_final(prior,target,tmp_path); options=_options(tmp_path,prior)
    report=subject.rebind_reader_options(prior,current,options,tmp_path/'bound')
    assert report['state']=='candidate_only' and report['review_transferred'] is False
    assert (tmp_path/'bound/reader_options.json').is_file()

def test_rebind_rejects_changed_bound_unit(reuse_inputs,tmp_path):
    prior,target=reuse_inputs; current=_second_final(prior,target,tmp_path,changed=True); options=_options(tmp_path,prior)
    with pytest.raises(ValueError,match='changed unit'): subject.rebind_reader_options(prior,current,options,tmp_path/'bound')

def test_rebind_explicitly_authorizes_changed_bound_unit(reuse_inputs,tmp_path):
    prior,target=reuse_inputs; current=_second_final(prior,target,tmp_path,changed=True); options=_options(tmp_path,prior)
    reviewed, rows=_authorizations(tmp_path/'reviewed-bindings.json',prior,current)
    report=subject.rebind_reader_options(prior,current,options,tmp_path/'bound',reviewed)
    rebound=_read(tmp_path/'bound/reader_options.json')
    assert report['review_transferred'] is False and report['authorized_rebindings'][0]['unit_id'] == rows[0]['unit_id']
    assert rebound['body_links'][0]['unit']['ru_sha256'] == rows[0]['current_ru_sha256']
    assert report['reviewed_bindings_evidence']['sha256'] == file_identity(reviewed)['sha256']

def test_rebind_preserves_nested_handout_group_bindings(reuse_inputs,tmp_path):
    prior,target=reuse_inputs; current=_second_final(prior,target,tmp_path); options=_options(tmp_path,prior)
    value=_read(options); unit=value['body_links'][0]['unit']
    value['display_roles']=[{'role':'interrupted_prose_reflow','units':[unit.copy(),unit.copy()],
        'intervening_units':[unit.copy()], 'source_evidence':'fixture', 'reason':'fixture',
        'intervening_handout_groups':[{'units':[unit.copy()], 'title':unit.copy(),
            'source_evidence':'fixture handout', 'reason':'fixture handout'}]}]
    value['options_sha256']=reader_projection.seal({key:item for key,item in value.items() if key!='options_sha256'})
    _write(options,value)
    subject.rebind_reader_options(prior,current,options,tmp_path/'bound')
    rebound=_read(tmp_path/'bound/reader_options.json')
    assert rebound['display_roles'] == value['display_roles']

@pytest.mark.parametrize('damage',['stale','unused'])
def test_rebind_rejects_stale_or_unused_reviewed_authorization(reuse_inputs,tmp_path,damage):
    prior,target=reuse_inputs; current=_second_final(prior,target,tmp_path,changed=True)
    options=_options(tmp_path,prior,binding=damage != 'unused')
    reviewed, rows=_authorizations(tmp_path/'reviewed-bindings.json',prior,current)
    if damage == 'stale':
        rows[0]['current_ru_sha256']='0'*64; _write(reviewed,rows)
    with pytest.raises(ValueError,match='stale or unknown|unused'):
        subject.rebind_reader_options(prior,current,options,tmp_path/'bound',reviewed)

def test_rebind_rejects_changed_asset(reuse_inputs,tmp_path):
    prior,target=reuse_inputs; current=_second_final(prior,target,tmp_path); options=_options(tmp_path,prior)
    image=next((prior/'MASTER_RU.md').parent.glob('assets/*')); (current/image.relative_to(prior)).write_bytes(b'changed')
    with pytest.raises(ValueError,match='inventory mismatch|referenced assets'): subject.rebind_reader_options(prior,current,options,tmp_path/'bound')

def test_source_identity_and_unit_metadata_must_match():
    old={'master_en':{'sha256':'A'},'source_spans':{'sha256':'B'},'units':[{'unit_id':'u','source_hash':'C','parent_unit_id':None,'part_index':None,'part_count':None}]}
    changed={**old,'master_en':{'sha256':'D'}}
    with pytest.raises(ValueError,match='MASTER_EN'): subject._same_source(old,changed)
    changed={**old,'units':[{'unit_id':'u','source_hash':'C','parent_unit_id':None,'part_index':1,'part_count':2}]}
    with pytest.raises(ValueError,match='metadata'): subject._same_source(old,changed)

def test_selected_replacement_is_copied_and_tamper_rejected(reuse_inputs,tmp_path):
    prior,target=reuse_inputs; current=_second_final(prior,target,tmp_path); options=_options(tmp_path,prior,asset=True)
    subject.rebind_reader_options(prior,current,options,tmp_path/'bound')
    assert (tmp_path/'bound/selected/replacement.bin').read_bytes()==b'replacement'
    (tmp_path/'selected/replacement.bin').write_bytes(b'tampered')
    with pytest.raises(ValueError,match='asset identity'): subject.rebind_reader_options(prior,current,options,tmp_path/'second')

def test_source_figure_region_assets_copy_once_and_reject_stale_bytes(reuse_inputs,tmp_path):
    prior,target=reuse_inputs; current=_second_final(prior,target,tmp_path); options=_options(tmp_path,prior,regions=True)
    subject.rebind_reader_options(prior,current,options,tmp_path/'bound')
    assert (tmp_path/'bound/selected/region.bin').read_bytes() == b'region-native'
    (tmp_path/'selected/region.bin').write_bytes(b'stale')
    with pytest.raises(ValueError,match='stale'):
        subject.rebind_reader_options(prior,current,options,tmp_path/'second')
