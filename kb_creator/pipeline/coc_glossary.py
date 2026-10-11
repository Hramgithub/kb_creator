"""Self-contained CoC glossary composition with exact source snapshots."""
from __future__ import annotations
import base64
import csv
import hashlib
import io
import json
import re
import unicodedata
from pathlib import Path

SCHEMA = 'kb_creator.effective_coc_glossary.v1'
HEADER = ('source_term','accepted_ru','aliases','bad_ru','domain','status','source_scope','decision_rule','notes')
ROOT = Path(__file__).resolve().parents[2]
DEFAULT_REGISTRY = ROOT / 'CoC/Project_Reference/Terminology/CoC_Terminology_Decisions.csv'

def normalize(text):
    return ' '.join(unicodedata.normalize('NFKC',text).casefold().split())

def digest(value):
    return hashlib.sha256(json.dumps(value,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()).hexdigest().upper()

def identity(data):
    return {'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest().upper()}

def _write(path,value):
    path.write_text(json.dumps(value,ensure_ascii=False,sort_keys=True,indent=2)+'\n',encoding='utf-8',newline='\n')

def _text(value):
    if not isinstance(value,str) or not value.strip() or re.search(r'[\x00-\x08\x0b\x0c\x0e-\x1f]',value):
        raise ValueError('nonempty clean terminology text required')
    return ' '.join(value.split())

def _variants(value):
    if value in (None,'',[]): return []
    if isinstance(value,str): value=value.split(';')
    if not isinstance(value,list): raise ValueError('invalid terminology variants')
    result=[_text(item) for item in value]
    if len({normalize(item) for item in result})!=len(result): raise ValueError('duplicate variants')
    return result

def _unique(values):
    result={}
    for value in values: result.setdefault(normalize(value),value)
    return list(result.values())

def registry_rows(data):
    reader=csv.DictReader(io.StringIO(data.decode('utf-8-sig'),newline=''))
    if tuple(reader.fieldnames or ())!=HEADER: raise ValueError('registry header mismatch')
    rows=list(reader); accepted=set()
    for row in rows:
        if set(row)!=set(HEADER) or any(v is None for v in row.values()): raise ValueError('malformed registry row')
        _text(row['source_term'])
        if row['status'] not in {'accepted','review_required'}: raise ValueError('unsupported registry status')
        if row['status']=='accepted':
            key=normalize(row['source_term'])
            if key in accepted: raise ValueError('duplicate accepted registry source')
            accepted.add(key); _text(row['accepted_ru'])
    return rows

def overlay_rows(data):
    value=json.loads(data.decode('utf-8-sig'))
    if not isinstance(value,dict) or set(value)!={'terms'} or not isinstance(value['terms'],list): raise ValueError('overlay requires closed terms JSON')
    allowed={'source','en','target','ru','aliases','bad_ru','bad','forbidden','domain'}
    result=[]; seen=set()
    for row in value['terms']:
        if not isinstance(row,dict) or not set(row)<=allowed: raise ValueError('invalid overlay fields')
        sources=[row[k] for k in ('source','en') if k in row]; targets=[row[k] for k in ('target','ru') if k in row]; bad=[row[k] for k in ('bad_ru','bad','forbidden') if k in row]
        if len(sources)!=1 or len(targets)!=1 or len(bad)>1: raise ValueError('ambiguous overlay row')
        source,target=_text(sources[0]),_text(targets[0]);key=normalize(source)
        if key in seen: raise ValueError('duplicate overlay source')
        seen.add(key);domain=_text(row.get('domain','general')).casefold()
        if not re.fullmatch(r'[a-z0-9][a-z0-9 ./_-]*',domain): raise ValueError('invalid terminology domain')
        result.append({'source':source,'target':target,'aliases':_variants(row.get('aliases')),'bad_ru':_variants(bad[0] if bad else None),'domain':domain})
    return result

def _definition(notes):
    match=re.search(r'Определение:\s*(.*?)(?=\s*Источник:|\s*Область:|$)',notes,re.S)
    return match[1].strip() if match else ''

def usage_rule(notes):
    marker = 'Контекст JSON:'
    if marker not in notes: return None
    if notes.count(marker) != 1: raise ValueError('duplicate terminology context rule')
    value, _ = json.JSONDecoder().raw_decode(notes.split(marker, 1)[1].lstrip())
    if not isinstance(value, dict) or set(value) != {'selector','prose'} or value['selector'] != 'numeric_label_vs_prose':
        raise ValueError('unsupported terminology context rule')
    prose = value['prose']
    if not isinstance(prose, dict) or set(prose) != {'target','aliases','bad'}: raise ValueError('invalid prose terminology forms')
    _text(prose['target']); aliases=_variants(prose['aliases']); bad=_variants(prose['bad'])
    if {normalize(x) for x in [prose['target'],*aliases]} & {normalize(x) for x in bad}: raise ValueError('context accepted/bad overlap')
    return value

def _derive(registry,overlay,book_id):
    rows,book_rows=registry_rows(registry),overlay_rows(overlay)
    terms={};conflicts=[]
    for row in rows:
        if row['status']=='accepted':
            terms[normalize(row['source_term'])]={'source':row['source_term'],'target':row['accepted_ru'],'aliases':_variants(row['aliases']),'bad_ru':_variants(row['bad_ru']),'domain':_text(row['domain']).casefold()}
            rule = usage_rule(row['notes'])
            if rule: terms[normalize(row['source_term'])]['usage'] = rule
    for row in book_rows:
        key=normalize(row['source'])
        if key not in terms: terms[key]=dict(row);continue
        current=terms[key]
        if normalize(current['target'])!=normalize(row['target']):
            conflicts.append({'source':row['source'],'kind':'target_conflict','shared':current['target'],'book':row['target']});continue
        if row['domain']!='general' and current['domain']!=row['domain']:
            conflicts.append({'source':row['source'],'kind':'domain_conflict','shared':current['domain'],'book':row['domain']});continue
        current['aliases']=_unique(current['aliases']+row['aliases']);current['bad_ru']=_unique(current['bad_ru']+row['bad_ru'])
    for row in terms.values():
        row['aliases']=[a for a in row['aliases'] if normalize(a)!=normalize(row['target'])]
        accepted={normalize(x) for x in [row['target'],*row['aliases']]}
        if accepted & {normalize(x) for x in row['bad_ru']}: conflicts.append({'source':row['source'],'kind':'accepted_bad_conflict'})
    if not terms: raise ValueError('zero usable terminology pairs')
    context={'shared_rows':[{**row,'definition':_definition(row['notes']),'definition_status':'source_recorded' if _definition(row['notes']) else 'not_recorded'} for row in rows],
             'book_rows':[{**row,'book_id':book_id,'status':'selected_book_choice','definition_status':'not_recorded'} for row in book_rows],
             'policy':'Shared accepted rules plus explicit book choices. Global review_required rows are context only. No automatic replacement or edition conversion.'}
    return {'terms':[terms[k] for k in sorted(terms)],'context':context,'conflicts':conflicts}

def _snapshot(path):
    data=path.read_bytes()
    return {'reference':str(path.resolve()),**identity(data),'content_base64':base64.b64encode(data).decode('ascii')}

def _bytes(snapshot):
    if set(snapshot)!={'reference','bytes','sha256','content_base64'}: raise ValueError('invalid snapshot fields')
    data=base64.b64decode(snapshot['content_base64'],validate=True)
    if identity(data)!={k:snapshot[k] for k in ('bytes','sha256')}: raise ValueError('snapshot hash mismatch')
    return data

def validate_payload(value,*,allow_conflicts=False):
    required={'schema','system','book_id','sources','terms','context','conflicts','glossary_sha256'}
    if not isinstance(value,dict) or set(value)!=required or value['schema']!=SCHEMA or value['system']!='coc': raise ValueError('unsupported effective CoC glossary')
    if digest({k:v for k,v in value.items() if k!='glossary_sha256'})!=value['glossary_sha256']: raise ValueError('glossary seal mismatch')
    book_id=_text(value['book_id'])
    if set(value['sources'])!={'registry','overlay'}: raise ValueError('glossary source set mismatch')
    expected=_derive(_bytes(value['sources']['registry']),_bytes(value['sources']['overlay']),book_id)
    if any(value[k]!=expected[k] for k in expected): raise ValueError('glossary does not derive from snapshots')
    if value['conflicts'] and not allow_conflicts: raise ValueError('unresolved glossary conflicts')
    return value

def compose_glossary(registry:Path,overlay:Path,book_id:str,output:Path):
    registry,overlay,output=Path(registry),Path(overlay),Path(output)
    if output.exists(): raise ValueError('glossary destination must be absent')
    book_id=_text(book_id);sources={'registry':_snapshot(registry),'overlay':_snapshot(overlay)}
    value={'schema':SCHEMA,'system':'coc','book_id':book_id,'sources':sources,**_derive(_bytes(sources['registry']),_bytes(sources['overlay']),book_id)}
    value['glossary_sha256']=digest(value);validate_payload(value,allow_conflicts=True)
    output.mkdir(parents=True)
    _write(output/'composition.json',value);_write(output/'conflicts.json',{'conflicts':value['conflicts']});_write(output/'terminology-context.json',value['context'])
    if not value['conflicts']: _write(output/'glossary.json',value)
    return verify_glossary(output)

def verify_glossary(output:Path):
    output=Path(output);value=validate_payload(json.loads((output/'composition.json').read_text(encoding='utf-8')),allow_conflicts=True)
    expected={'composition.json','conflicts.json','terminology-context.json'}
    if not value['conflicts']:
        expected.add('glossary.json')
        if (output/'glossary.json').read_bytes()!=(output/'composition.json').read_bytes(): raise ValueError('glossary differs from composition')
    if {p.name for p in output.iterdir()}!=expected or any(p.is_symlink() or not p.is_file() for p in output.iterdir()): raise ValueError('glossary inventory mismatch')
    if json.loads((output/'terminology-context.json').read_text(encoding='utf-8'))!=value['context'] or json.loads((output/'conflicts.json').read_text(encoding='utf-8'))!={'conflicts':value['conflicts']}: raise ValueError('glossary context mismatch')
    return {'state':'conflicts' if value['conflicts'] else 'ready','book_id':value['book_id'],'terms':len(value['terms']),'conflicts':len(value['conflicts']),'glossary_sha256':value['glossary_sha256'],'glossary_path':str(output/'glossary.json') if not value['conflicts'] else None}
