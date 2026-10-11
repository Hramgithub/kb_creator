import csv
import io
import json
from copy import deepcopy

import pytest
from kb_creator.pipeline.coc_glossary import HEADER, identity, digest
from kb_creator.pipeline.coc_terminology_merge import consolidate, prepare_merge, apply_merge, verify_inventory, apply_reviewed_amendments


def source_row(source="Keeper", target="Хранитель", status="accepted"):
    return dict(zip(HEADER, [source,target,"Хранителю","","role",status,"source","reviewed","Original note"]))


def record(source, target, role="local_selected", **extra):
    return dict(source=source,target=target,dataset_role=role,book="Book",domain="general",**extra)


def test_merge_covers_every_record_and_preserves_accepted_rules():
    rows=[source_row()]
    records=[record("Keeper","Хранитель"),record("Keeper","Ведущий"),
             record("Nodens","Ноденс"),record("Nodens","Ноденс",role="local_candidate"),
             record("Old","Старый",role="superseded_local"),
             record("A / B","А / Б",composite_source_expression=True),
             record("Wrack","Wrack",classification="unresolved_spell_exception")]
    merged, report=consolidate(rows,records,"evidence.json")
    assert len(report["dispositions"])==len(records)
    assert len(report["conflicts"])==1
    assert {k:v for k,v in merged[0].items() if k!='notes'}=={k:v for k,v in rows[0].items() if k!='notes'}
    assert {r['source_term'] for r in merged}=={'Keeper','Nodens','Wrack'}
    assert all(r['status']=='review_required' for r in merged[1:])
    assert next(r for r in merged if r['source_term']=='Wrack')['accepted_ru']==''
    assert report['dispositions'][4]['action']=='historical_evidence_preserved'
    assert report['dispositions'][5]['action']=='composite_observation_preserved_for_decomposition'


def test_selected_choice_beats_candidate_without_promoting_to_global_rule():
    rows, _=consolidate([], [record('Term','Черновик','local_candidate'),record('Term','Выбранный')], 'evidence')
    assert rows[0]['accepted_ru']=='Выбранный' and rows[0]['status']=='review_required'


def test_conflicting_current_choices_remain_unresolved():
    rows, _=consolidate([], [record('Term','Первый'),record('Term','Второй')], 'evidence')
    assert rows[0]['accepted_ru']=='' and 'Первый; Второй' in rows[0]['notes']


def fixture(tmp_path):
    registry=tmp_path/'registry.csv'
    with registry.open('w',encoding='utf-8',newline='') as stream:
        writer=csv.DictWriter(stream,fieldnames=HEADER);writer.writeheader();writer.writerow(source_row())
    overlay=tmp_path/'book.json';overlay.write_text(json.dumps({'terms':[{'source':'New','target':'Новый'}]}),encoding='utf-8')
    inventory={'datasets':[], 'records':[]}
    for path,role,fmt,fields,selector in [(registry,'shared_authority','csv:registry',source_row(),{'row':2,'index':None,'line':None}),
                                         (overlay,'local_selected','json:terms',{'source':'New','target':'Новый'},{'row':None,'index':0,'line':None})]:
        ident=identity(path.read_bytes())
        inventory['datasets'].append({**ident,'paths':[{'path':str(path)}],'role':role,'format':fmt,'record_count':1})
        inventory['records'].append({**record(fields.get('source',fields.get('source_term')),fields.get('target',fields.get('accepted_ru')),role),
                                     'dataset_sha256':ident['sha256'],'source_ref':{'path':str(path),**selector},'original_fields':fields})
    ip=tmp_path/'inventory.json';ip.write_text(json.dumps(inventory),encoding='utf-8')
    return registry,overlay,ip,inventory


def test_real_merge_plan_apply_and_stale_preimage(tmp_path):
    registry,overlay,ip,inventory=fixture(tmp_path)
    prepare_merge(registry,ip,tmp_path/'bundle','inventory.json')
    result=apply_merge(registry,tmp_path/'bundle')
    assert result['rows']==2 and result['added']==1
    with pytest.raises(ValueError,match='preimage'):
        apply_merge(registry,tmp_path/'bundle')


def test_inventory_rejects_stale_and_forged_source_record(tmp_path):
    registry,overlay,ip,inventory=fixture(tmp_path)
    changed=deepcopy(inventory);changed['records'][1]['original_fields']['target']='Подмена'
    with pytest.raises(ValueError,match='record mismatch'): verify_inventory(changed)
    changed=deepcopy(inventory);changed['records'][1]['target']='Подмена'
    with pytest.raises(ValueError,match='extracted terminology'): verify_inventory(changed)
    overlay.write_text('{}')
    with pytest.raises(ValueError,match='changed'): verify_inventory(inventory)


def test_rehashed_merge_output_tampering_is_not_accepted(tmp_path):
    registry,overlay,ip,inventory=fixture(tmp_path)
    bundle=tmp_path/'bundle';prepare_merge(registry,ip,bundle,'inventory.json')
    path=bundle/'registry-after.csv';path.write_text(path.read_text(encoding='utf-8').replace('Новый','Подмена'),encoding='utf-8')
    report=json.loads((bundle/'merge-report.json').read_text(encoding='utf-8'));report['after']=identity(path.read_bytes())
    (bundle/'merge-report.json').write_text(json.dumps(report),encoding='utf-8')
    with pytest.raises(ValueError,match='does not derive'):apply_merge(registry,bundle)


def test_amendments_require_exact_row_and_preserve_other_fields(tmp_path):
    registry,overlay,ip,inventory=fixture(tmp_path)
    decisions={'schema':'kb_creator.terminology_amendments.v1','registry':identity(registry.read_bytes()),
               'amendments':[{'source':'Keeper','row_sha256':digest(source_row()),'fields':{'aliases':'Хранителю;Хранителя'},
                              'reason':'attested inflection','evidence':'source page2'}]}
    path=tmp_path/'decisions.json';path.write_text(json.dumps(decisions),encoding='utf-8')
    assert apply_reviewed_amendments(registry,path)['entries']==1
    row=list(csv.DictReader(io.StringIO(registry.read_text(encoding='utf-8'))))[0]
    assert row=={**source_row(),'aliases':'Хранителю;Хранителя'}
    with pytest.raises(ValueError,match='preimage'):apply_reviewed_amendments(registry,path)


def test_registry_replace_failure_preserves_original(tmp_path, monkeypatch):
    from kb_creator.pipeline import coc_terminology_merge as merger
    registry, _, _, _ = fixture(tmp_path)
    before = registry.read_bytes()
    def denied(*args):
        raise PermissionError("registry is in use")
    monkeypatch.setattr(merger.os, "replace", denied)
    with pytest.raises(PermissionError, match="in use"):
        merger._replace_registry(registry, before, before + b"new")
    assert registry.read_bytes() == before
    assert not list(tmp_path.glob(".terminology-*.tmp"))


def test_registry_change_during_preparation_is_not_overwritten(tmp_path, monkeypatch):
    from kb_creator.pipeline import coc_terminology_merge as merger
    registry, _, _, _ = fixture(tmp_path)
    before = registry.read_bytes()
    changed = before + b"concurrent change"
    monkeypatch.setattr(merger.os, "fsync", lambda _: registry.write_bytes(changed))
    with pytest.raises(ValueError, match="changed before replacement"):
        merger._replace_registry(registry, before, before + b"new")
    assert registry.read_bytes() == changed
    assert not list(tmp_path.glob(".terminology-*.tmp"))
