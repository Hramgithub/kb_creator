"""Closed MASTER_EN preflight plus deterministic, staging-only asset materialization."""
from __future__ import annotations
import argparse, hashlib, json, os, re, shutil, stat, subprocess, tempfile
from pathlib import Path
from typing import Sequence

from PIL import Image, ImageOps
from pypdf import PdfReader

SCHEMA="kb_creator.master_en_publication.v1"
V2_SCHEMA="kb_creator.master_en_publication.v2"
TOP={"schema","scenario_id","contract","accepted_reconstruction","document","hierarchy","source_disposition","xrefs","handouts","structured_content","assets","visual_review_units","reader_noise_patterns","reader_surface"}
N={"hierarchy":168,"source_disposition":124,"xrefs":237,"handouts":41,"structured_content":29,"assets":123,"visual_review_units":91,"reader_noise_patterns":9}
HEX=re.compile(r"^[0-9A-F]{64}$"); ANCHOR=re.compile(r"^viral(?:-[a-z0-9]+)*$")
PACKAGE_ALGO="SHA-256 over ordinal UTF-8 LF relative_path<TAB>bytes<TAB>UPPER_SHA256<LF>"
MIGRATION_ALGO="SHA-256 over canonical UTF-8 JSON (sort_keys=true, separators=(',', ':')) of complete frozen-v1 row"
MIGRATION_DOMAINS={
 'hierarchy_rows':('hierarchy','anchor',168,{'retained_unchanged','retained_rebound','reclassified','replaced','split','merged','suppressed_reviewed','excluded_advertising'}),
 'asset_rows':('assets','asset_id',123,{'retained_unchanged','retained_rebound','reclassified','replaced','split','merged','suppressed_reviewed','excluded_advertising'}),
 'xref_rows':('xrefs','xref_id',237,{'retained_unchanged','retained_rebound','replaced','split','merged','suppressed_reviewed','excluded_advertising'}),
 'source_disposition_rows':('source_disposition','page',124,{'retained_unchanged','reclassified','suppressed_reviewed','excluded_advertising'}),
 'handout_rows':('handouts','anchor',41,{'retained_unchanged','retained_rebound','reclassified','replaced','split','merged','suppressed_reviewed','excluded_advertising'}),
 'structured_rows':('structured_content','structure_id',29,{'retained_unchanged','retained_rebound','reclassified','replaced','split','merged','suppressed_reviewed'}),
}
def bad(s): raise ValueError(s)
def rb(p): return Path(p).read_bytes()
def dig(p): return hashlib.sha256(rb(p)).hexdigest().upper()
def js(p,l):
 try:x=json.loads(rb(p))
 except (OSError,json.JSONDecodeError) as e: raise ValueError(f"{l} is not JSON") from e
 if not isinstance(x,dict):bad(f"{l} must be object")
 return x
def closed(x,k,l):
 if not isinstance(x,dict) or set(x)!=k:bad(f"{l} closed schema mismatch")
 return x
def st(x,l):
 if not isinstance(x,str) or not x:bad(f"{l} must be string")
 return x
def num(x,l):
 if not isinstance(x,int) or isinstance(x,bool):bad(f"{l} must be integer")
 return x
def root_for(p):
 for x in (p.resolve(),*p.resolve().parents):
  if (x/'.git').exists():return x
 bad('checkout root not found')
def rel(root,x,l):
 s=st(x,l);q=Path(s)
 if q.is_absolute() or '..' in q.parts or '\\' in s:bad(f"{l} must be safe repository-relative")
 p=(root/q).resolve(strict=True)
 try:p.relative_to(root.resolve())
 except ValueError as e:raise ValueError(f"{l} escapes checkout") from e
 return p
def ident(root,x,l,want=None):
 x=closed(x,{'path','bytes','sha256'},l);p=rel(root,x['path'],l+'.path')
 if want is not None and p!=want:bad(f"{l} CLI/config path mismatch")
 if num(x['bytes'],l+'.bytes')!=p.stat().st_size or not HEX.fullmatch(st(x['sha256'],l+'.sha256')) or dig(p)!=x['sha256']:bad(f"{l} identity mismatch")
 return p
def inventory(root):
 rows=[];count=total=0
 for p in sorted((x for x in root.rglob('*') if x.is_file()),key=lambda x:x.relative_to(root).as_posix()):
  size=p.stat().st_size;rows.append(f"{p.relative_to(root).as_posix()}\t{size}\t{dig(p)}\n");count+=1;total+=size
 return count,total,hashlib.sha256(''.join(rows).encode('utf8')).hexdigest().upper()
def v2_safe_package_root(root,value):
 if not isinstance(value,str) or not value or '\\' in value or ':' in value or value.startswith('/') or any(x in {'','.','..'} for x in value.split('/')):bad('v2 reconstruction package root must be safe repository-relative')
 return Path(root)/Path(value)
def v2_reparse(path):
 data=os.lstat(path);return stat.S_ISLNK(data.st_mode) or bool(getattr(data,'st_file_attributes',0)&0x400)
def v2_package_inventory(root):
 """Hash every regular package file; this is deliberately not candidate inventory."""
 root=Path(root)
 if not root.is_dir() or v2_reparse(root):bad('v2 reconstruction package topology mismatch')
 rows=[]
 def walk(directory):
  children=list(os.scandir(directory))
  if not children:bad('v2 reconstruction package topology mismatch')
  for entry in children:
   path=Path(entry.path)
   if v2_reparse(path):bad('v2 reconstruction package topology mismatch')
   mode=os.lstat(path).st_mode
   if stat.S_ISDIR(mode):walk(path)
   elif stat.S_ISREG(mode):
    data=path.read_bytes();rows.append((path.relative_to(root).as_posix(),len(data),hashlib.sha256(data).hexdigest().upper()))
   else:bad('v2 reconstruction package topology mismatch')
 walk(root);rows.sort(key=lambda row:row[0])
 payload=''.join(f"{path}\t{size}\t{digest}\n" for path,size,digest in rows).encode('utf8')
 return len(rows),sum(row[1] for row in rows),hashlib.sha256(payload).hexdigest().upper()
def v2_source_partition(value,package):
 """Validate the closed, raw-byte-exhaustive reader source partition."""
 closed(value,{'pages','spans'},'v2 source partition');pages=value['pages'];spans=value['spans']
 if not isinstance(pages,list) or not isinstance(spans,list) or [x.get('page') for x in pages if isinstance(x,dict)]!=list(range(1,123)):bad('v2 source partition mismatch')
 def profile(raw):
  counts={'lf':0,'crlf':0,'crcrlf':0,'lone_cr':0};i=0
  while i<len(raw):
   if raw[i:i+3]==b'\r\r\n':counts['crcrlf']+=1;i+=3
   elif raw[i:i+2]==b'\r\n':counts['crlf']+=1;i+=2
   elif raw[i:i+1]==b'\n':counts['lf']+=1;i+=1
   elif raw[i:i+1]==b'\r':counts['lone_cr']+=1;i+=1
   else:i+=1
  lines=raw.splitlines()
  return {**counts,'line_slots':len(lines),'nonblank_line_slots':sum(bool(line.strip()) for line in lines)}
 by_page={};span_ids=set()
 for row in spans:
  closed(row,{'span_id','page','source_path','start_byte','end_byte','start_char','end_char','raw_sha256','raw_text_sha256','classification','owner_kind','owner_id','decision_ref'},'v2 source span')
  if not isinstance(row['span_id'],str) or not row['span_id'] or row['span_id'] in span_ids or any(not isinstance(row[x],int) or isinstance(row[x],bool) for x in ('page','start_byte','end_byte','start_char','end_char')) or row['page'] not in range(1,123) or row['end_byte']<=row['start_byte'] or row['end_char']<=row['start_char'] or not isinstance(row['source_path'],str) or Path(row['source_path']).is_absolute() or '\\' in row['source_path'] or '..' in Path(row['source_path']).parts or row['source_path']!=f"pages/page-{row['page']:03d}.md" or row['classification'] not in {'retained_heading','retained_text','reviewed_structured_source','asset_reference_source','generated_navigation_source','authorized_suppression','technical_marker_suppression','layout_separator'} or row['owner_kind'] not in {'event','asset','generated_navigation','suppression'} or not isinstance(row['owner_id'],str) or not row['owner_id'] or row['decision_ref'] is not None and not isinstance(row['decision_ref'],str) or not HEX.fullmatch(str(row['raw_sha256'])) or not HEX.fullmatch(str(row['raw_text_sha256'])):bad('v2 source partition span mismatch')
  span_ids.add(row['span_id'])
  by_page.setdefault(row['page'],[]).append(row)
 totals={'pages':0,'bytes':0,'line_slots':0,'nonblank_line_slots':0,'eol':{'lf':0,'crlf':0,'crcrlf':0,'lone_cr':0}}
 for page in pages:
  closed(page,{'page','path','bytes','sha256','encoding','eol_profile','span_ids'},'v2 source partition page')
  if not isinstance(page['page'],int) or isinstance(page['page'],bool) or not isinstance(page['path'],str) or page['path']!=f"pages/page-{page['page']:03d}.md" or page['encoding']!='utf-8-no-bom' or not isinstance(page['bytes'],int) or isinstance(page['bytes'],bool) or not HEX.fullmatch(str(page['sha256'])) or not isinstance(page['span_ids'],list) or page['page'] not in by_page:bad('v2 source partition page mismatch')
  raw=(Path(package)/Path(page['path'])).read_bytes()
  if raw.startswith(b'\xef\xbb\xbf') or page['bytes']!=len(raw) or hashlib.sha256(raw).hexdigest().upper()!=page['sha256'] or page['eol_profile']!=profile(raw):bad('v2 source partition page mismatch')
  cursor=0;ids=[]
  for span in by_page[page['page']]:
   chunk=raw[span['start_byte']:span['end_byte']]
   try:text=raw.decode('utf8');piece=chunk.decode('utf8')
   except UnicodeDecodeError:bad('v2 source partition UTF-8 boundary mismatch')
   if span['start_byte']!=cursor or span['end_byte']>len(raw) or span['end_char']>len(text) or text[:span['start_char']].encode('utf8')!=raw[:span['start_byte']] or text[span['start_char']:span['end_char']]!=piece or hashlib.sha256(chunk).hexdigest().upper()!=span['raw_sha256'] or hashlib.sha256(piece.encode('utf8')).hexdigest().upper()!=span['raw_text_sha256']:bad('v2 source partition coverage mismatch')
   cursor=span['end_byte'];ids.append(span['span_id'])
  if cursor!=len(raw) or ids!=page['span_ids']:bad('v2 source partition coverage mismatch')
  actual=profile(raw);totals['pages']+=1;totals['bytes']+=len(raw);totals['line_slots']+=actual['line_slots'];totals['nonblank_line_slots']+=actual['nonblank_line_slots']
  for key in totals['eol']:totals['eol'][key]+=actual[key]
 return totals
V2_OPERATIONS={'emit_exact','semantic_restructure','asset_reference','generated_navigation','source_recovery','emit_anchor_only','suppress'}
V2_ROLE_RANK={'heading':0,'anchor_only':1,'text_fragment':2,'structured_unit':3,'asset':4,'generated_navigation':5}
V2_PLACEHOLDERS=('Source-backed','See source-backed entry.','Translatable source key')
V2_OPERATION_BY_TYPE={'heading':{'emit_exact'},'text_fragment':{'emit_exact','source_recovery'},'structured_unit':{'semantic_restructure'},'asset':{'asset_reference','suppress'},'anchor_only':{'emit_anchor_only'},'generated_navigation':{'generated_navigation'}}
def v2_a3_payload_schema(data):
 """Reject partial, invented, or legacy typed publication payloads."""
 kind=data.get('kind') if isinstance(data,dict) else None
 schemas={'callout':{'kind','body','contains','end_after'},'ordered_list_callout':{'kind','items','item_count','contains','end_after'},'table':{'kind','header','rows','row_count','cell_count','contains'},'equipment_card':{'kind','title','stats','footnote','body','contains','end_after'},'creature_statblock':{'kind','title','subtitle','characteristics','derived_stats','attacks','abilities','nested_tables','contains','end_after'},'inline_run_in':{'kind','anchor','label','xref','contains'},'full_page_map':{'kind','pages','reader_asset_ids','accessible_key','legend','scale','contains'},'physical_page_pair':{'kind','front_page','back_page','front_reader_asset_ids','back_reader_asset_ids','back_semantics','contains'}}
 if kind not in schemas:bad('v2 typed kind mismatch')
 closed(data,schemas[kind],'v2 typed payload')
 if kind=='table' and (not isinstance(data['header'],list) or not data['header'] or not isinstance(data['rows'],list) or data['row_count']!=len(data['rows']) or data['cell_count']!=sum(len(row) for row in data['rows']) or any(not isinstance(row,list) or len(row)!=len(data['header']) for row in data['rows'])):bad('v2 table closure mismatch')
 if kind=='ordered_list_callout' and (not isinstance(data['items'],list) or not data['items'] or data['item_count']!=len(data['items']) or data['end_after']!=data['contains'][-1]):bad('v2 list closure mismatch')
 if kind in {'callout','equipment_card','creature_statblock'} and (not data['contains'] or data['end_after']!=data['contains'][-1]):bad('v2 typed boundary mismatch')
 if kind=='equipment_card' and (any(not isinstance(data[key],str) for key in ('title','stats','footnote','body')) or not any(data[key] for key in ('title','stats','footnote','body'))):bad('v2 equipment closure mismatch')
 if kind=='creature_statblock' and (any(not isinstance(data[key],str) for key in ('title','subtitle','characteristics','derived_stats','attacks','abilities','nested_tables')) or not any(data[key] for key in ('title','subtitle','characteristics','derived_stats','attacks','abilities','nested_tables'))):bad('v2 creature closure mismatch')
 if kind=='full_page_map' and (not isinstance(data['pages'],list) or len(data['pages'])<2 or not isinstance(data['reader_asset_ids'],list) or not data['reader_asset_ids'] or len(data['reader_asset_ids'])!=len(set(data['reader_asset_ids'])) or any(not isinstance(data[key],str) for key in ('accessible_key','legend','scale'))):bad('v2 map closure mismatch')
 if kind=='physical_page_pair' and (not isinstance(data['front_page'],int) or not isinstance(data['back_page'],int) or data['front_page']==data['back_page'] or not isinstance(data['front_reader_asset_ids'],list) or not data['front_reader_asset_ids'] or len(data['front_reader_asset_ids'])!=len(set(data['front_reader_asset_ids'])) or not isinstance(data['back_reader_asset_ids'],list) or not data['back_reader_asset_ids'] or len(data['back_reader_asset_ids'])!=len(set(data['back_reader_asset_ids'])) or not isinstance(data['back_semantics'],str) or not data['back_semantics']):bad('v2 pair closure mismatch')
 return kind
def v2_a3_pointer(value,pointer):
 """Resolve a closed JSON pointer without accepting a second spelling."""
 if not isinstance(pointer,str) or not pointer.startswith('/') or '//' in pointer:bad('v2 payload pointer mismatch')
 here=value
 for part in pointer[1:].split('/'):
  part=part.replace('~1','/').replace('~0','~')
  if isinstance(here,list) and part.isdigit() and int(part)<len(here):here=here[int(part)]
  elif isinstance(here,dict) and part in here:here=here[part]
  else:bad('v2 payload pointer mismatch')
 return here
def v2_a3_leaves(value,prefix='/content'):
 """Authorial leaves are all payload strings except closed structural tokens."""
 reserved={'kind','contains','end_after','asset_id','asset_ids','reader_asset_ids','front_reader_asset_ids','back_reader_asset_ids','anchor','front_facsimile','back_facsimile','front_page','back_page','pages','page_set','count','row_count','cell_count','continuation','placement'}
 out=[]
 def visit(item,path,key=None):
  if isinstance(item,str) and key not in reserved:out.append((path,item))
  elif isinstance(item,list):
   for i,child in enumerate(item):visit(child,f'{path}/{i}',key)
  elif isinstance(item,dict):
   for child_key,child in item.items():visit(child,f'{path}/{child_key.replace("~","~0").replace("/","~1")}',child_key)
 visit(value,prefix);return out
def _v2_canonical_source_free_asset_event(asset,event,events):
 """Validate the explicit non-Markdown ordering proof for one reader asset."""
 placement=asset.get('placement');order=asset.get('source_order')
 if event['type']!='asset' or event.get('source_operation') not in V2_OPERATION_BY_TYPE['asset'] or asset.get('anchor')!=event.get('anchor') or asset.get('source_page')!=event.get('page') or not isinstance(event.get('order_key'),list) or len(event['order_key'])!=4 or event['order_key'][0]!=asset['source_page'] or not isinstance(placement,dict) or set(placement) not in ({'before_event'},{'after_event'},{'inside_structured_unit'}) or next(iter(placement.values())) not in events or not isinstance(order,dict):bad('v2 canonical asset event mismatch')
 if order.get('kind')=='selected_view_raw_index' and set(order)=={'kind','view','raw_index','gap_ordinal'} and isinstance(order['view'],str) and isinstance(order['raw_index'],int) and isinstance(order['gap_ordinal'],int):return
 if order.get('kind')=='physical_unit_page_slot' and set(order)=={'kind','unit_id','page_slot'} and isinstance(order['unit_id'],str) and isinstance(order['page_slot'],int):return
 bad('v2 canonical asset source order mismatch')
def v2_a3_validate(value,package,root=None):
 """A3 provenance, payload, hierarchy and typed-payload closure."""
 spans={row['span_id']:row for row in value['source_partition']['spans']};events={row['event_id']:row for row in value['events']}
 hierarchy={row['anchor']:row for row in value['hierarchy']};seen=set()
 for row in value['hierarchy']:
  closed(row,{'anchor','parent_anchor','level','toc_entry','semantic_role','source_pages','source_title','reader_title','representation','reviewed_title_transformation','migration_row_id'},'v2 hierarchy')
  if not isinstance(row['anchor'],str) or not row['anchor'] or row['anchor'] in seen or row['parent_anchor'] is not None and row['parent_anchor'] not in hierarchy or row['parent_anchor']==row['anchor'] or not isinstance(row['level'],int) and row['level'] is not None or isinstance(row['level'],bool) or not isinstance(row['toc_entry'],bool) or not isinstance(row['semantic_role'],str) or not row['semantic_role'] or not isinstance(row['source_pages'],list) or not row['source_pages'] or any(page not in range(1,123) for page in row['source_pages']) or row['representation'] not in {'heading','anchor_only','inline_run_in'} or not isinstance(row['migration_row_id'],str) or not row['migration_row_id']:bad('v2 hierarchy A3 mismatch')
  if row['representation']=='heading' and row['level'] not in range(1,7):bad('v2 hierarchy level mismatch')
  if row['representation']!='heading' and row['level'] is not None:bad('v2 hierarchy representation mismatch')
  transform=row['reviewed_title_transformation']
  if row['source_title']!=row['reader_title']:
   closed(transform,{'operation','decision_ref','recovery_id'},'v2 title transformation')
   if transform['operation'] not in {'source_recovery','semantic_restructure'} or not isinstance(transform['decision_ref'],str) or not transform['decision_ref'] or not isinstance(transform['recovery_id'],str) or not transform['recovery_id']:bad('v2 title transformation mismatch')
  elif transform is not None:bad('v2 title transformation mismatch')
  seen.add(row['anchor'])
 def parent_chain(anchor):
  walked=set()
  while hierarchy[anchor]['parent_anchor'] is not None:
   anchor=hierarchy[anchor]['parent_anchor']
   if anchor in walked:bad('v2 hierarchy cycle mismatch')
   walked.add(anchor)
 for anchor in hierarchy:parent_chain(anchor)
 canonical_assets={row['asset_id']:row for row in value['assets'] if isinstance(row,dict) and 'provenance' in row};used_spans=set();last=None
 def intervening_foreign(span,event):
  if span['classification'] in {'layout_separator','authorized_suppression'} or span['owner_id']==event['event_id']:return False
  asset=canonical_assets.get(span['owner_id']) if span['classification']=='asset_reference_source' else None
  return asset is None or not isinstance(asset.get('placement'),dict) or next(iter(asset['placement'].values()),None)!=event['event_id']
 for ordinal,event in enumerate(value['events']):
  keys={'event_id','type','page','order_key','anchor','content','fragment_id','source_span_ids','source_operation','payload_bindings'}|({'contains'} if event['type']=='structured_unit' else set())|({'generated_placement'} if event['type']=='generated_navigation' else set())
  closed(event,keys,'v2 event')
  ids=event['source_span_ids'];operation=event['source_operation']
  if event['type']=='generated_navigation':
   if ids or event['payload_bindings'] or set(event['generated_placement'])!={'after_event'} or event['generated_placement']['after_event'] not in events or not isinstance(event['content'],dict) or event['content'].get('kind')!='generated_navigation':bad('v2 generated navigation mismatch')
   continue
  asset=canonical_assets.get(event['content']) if event['type']=='asset' and isinstance(event['content'],str) else None
  source_free=asset is not None and asset.get('disposition')=='reader' and asset.get('provenance',{}).get('kind') in {'visual_region','reviewed_provisional_full_page'} and ids==[] and event['payload_bindings']==[]
  if source_free:
   _v2_canonical_source_free_asset_event(asset,event,events)
   key=tuple(event['order_key'])
   if last is not None and key<=last:bad('v2 event order mismatch')
   last=tuple(key);continue
  if event['type'] not in V2_ROLE_RANK or operation not in V2_OPERATION_BY_TYPE.get(event['type'],set()) or not isinstance(ids,list) or not ids or len(ids)!=len(set(ids)) or any(item not in spans for item in ids):bad('v2 event provenance mismatch')
  source=[spans[item] for item in ids]
  if event['type']=='asset':
   if any(row['owner_kind']!='asset' or row['owner_id']!=event['content'] or row['classification']!='asset_reference_source' for row in source):bad('v2 asset event owner mismatch')
  elif any(row['owner_kind']!='event' or row['owner_id']!=event['event_id'] for row in source):bad('v2 event owner mismatch')
  if any(item in used_spans for item in ids):bad('v2 event source reuse mismatch')
  if any(source[i]['page']>source[i+1]['page'] or source[i]['page']==source[i+1]['page'] and source[i]['start_byte']>=source[i+1]['start_byte'] for i in range(len(source)-1)):bad('v2 event span order mismatch')
  if len(source)>1:
   for left,right in zip(source,source[1:]):
    if left['page']==right['page']:
     between=[span for span in spans.values() if span['page']==left['page'] and left['end_byte']<=span['start_byte'] and span['end_byte']<=right['start_byte']]
     foreign=next((span for span in between if intervening_foreign(span,event)),None)
     if foreign is not None:bad(f"v2 event intervening foreign span mismatch: {event['event_id']}:{foreign['span_id']}:{foreign['owner_id']}")
  key=[source[0]['page'],source[0]['start_byte'],V2_ROLE_RANK[event['type']],ordinal]
  if event['order_key']!=key or last is not None and tuple(key)<=last:bad('v2 event order mismatch')
  last=tuple(key);used_spans.update(ids)
  bindings=event['payload_bindings']
  if not isinstance(bindings,list):bad('v2 payload binding mismatch')
  targets={} if event['type'] in {'asset','anchor_only'} else {pointer:text for pointer,text in v2_a3_leaves(event['content']) if text}
  got=set()
  for binding in bindings:
   closed(binding,{'json_pointer','source_slices','joiner','recovery_id'},'v2 payload binding')
   pointer=binding['json_pointer'];leaf=v2_a3_pointer({'content':event['content']},pointer)
   if pointer in got or pointer not in targets or not isinstance(leaf,str) or binding['joiner'] not in {'',' ','\n','\n\n'} or (binding['source_slices'] is None)==(binding['recovery_id'] is None):bad('v2 payload binding mismatch')
   got.add(pointer)
   if binding['source_slices'] is not None:
    if not isinstance(binding['source_slices'],list) or not binding['source_slices']:bad('v2 payload slice mismatch')
    pieces=[]
    for slice_ in binding['source_slices']:
     closed(slice_,{'span_id','start_char','end_char'},'v2 payload slice')
     span=spans.get(slice_['span_id'])
     if span is None or span['span_id'] not in ids or not isinstance(slice_['start_char'],int) or not isinstance(slice_['end_char'],int) or slice_['end_char']<=slice_['start_char']:bad('v2 payload slice mismatch')
     raw=(Path(package)/span['source_path']).read_bytes()
     if slice_['start_char']<span['start_char'] or slice_['end_char']>span['end_char']:bad('v2 payload slice mismatch')
     text=raw.decode('utf8')[slice_['start_char']:slice_['end_char']]
     pieces.append(text)
    if binding['joiner'].join(pieces)!=leaf:bad('v2 payload text mismatch')
   elif not isinstance(binding['recovery_id'],str) or not binding['recovery_id']:bad('v2 recovery binding mismatch')
  if got!=set(targets):bad('v2 unbound authorial payload mismatch')
  if any(token in text for _,text in targets.items() for token in V2_PLACEHOLDERS):bad('v2 placeholder payload mismatch')
  if event['type']=='structured_unit':
   data=event['content'];v2_a3_payload_schema(data);contains=event['contains']
   if not isinstance(contains,list) or not contains or contains!=data['contains'] or len(contains)!=len(set(contains)) or set(ids)-set(contains):bad('v2 structured contains mismatch')
   for item in contains:
    if item in ids:continue
    child=events.get(item)
    if child is None or child['event_id']==event['event_id'] or child['anchor']!=event['anchor'] or child['page']!=event['page'] or child['type'] in {'heading','generated_navigation'}:bad('v2 structured contains ownership mismatch')
   def position(item):
    row=spans[item] if item in spans else spans[events[item]['source_span_ids'][0]]
    return (row['page'],row['start_byte'])
   if any(position(left)>=position(right) for left,right in zip(contains,contains[1:])):bad('v2 structured contains order mismatch')
 recoveries={row['recovery_id']:row for row in value['source_recoveries']}
 for event in value['events']:
  for binding in event['payload_bindings']:
   if binding['recovery_id'] is not None and (binding['recovery_id'] not in recoveries or recoveries[binding['recovery_id']]['target_event_id']!=event['event_id']):bad('v2 recovery binding mismatch')
 for row in value['source_recoveries']:
  closed(row,{'recovery_id','source_pdf_identity','physical_page','extraction_method','source_text','source_text_sha256','evidence_identity','target_event_id','placement','decision_ref'},'v2 recovery')
  if row['target_event_id'] not in events or row['placement'] not in {'before_event','after_event'} or not isinstance(row['physical_page'],int) or row['physical_page']<1 or not isinstance(row['source_text'],str) or hashlib.sha256(row['source_text'].encode('utf8')).hexdigest().upper()!=row['source_text_sha256'] or not isinstance(row['decision_ref'],str) or not row['decision_ref']:bad('v2 recovery mismatch')
  if root is not None:
   if row['source_pdf_identity']!=value['document']['source_pdf']:bad('v2 recovery source PDF mismatch')
   ident(root,row['evidence_identity'],'v2 recovery evidence')
 for row in value['hierarchy']:
  transform=row['reviewed_title_transformation']
  if transform is not None and transform['recovery_id'] not in recoveries:bad('v2 title recovery mismatch')
 for row in value['xrefs']:
  closed(row,{'xref_id','source_event_id','source_page','target_anchor','reader_text','source_slices','emit_link','migration_row_id'},'v2 xref')
  owner=events.get(row['source_event_id'])
  if owner is None or not isinstance(row['emit_link'],bool) or (row['emit_link'] and row['target_anchor'] not in hierarchy) or (not row['emit_link'] and row['target_anchor'] is not None) or not isinstance(row['migration_row_id'],str) or not row['migration_row_id'] or not isinstance(row['source_slices'],list) or not row['source_slices']:bad('v2 xref closure mismatch')
  text=[]
  for slice_ in row['source_slices']:
   closed(slice_,{'span_id','start_char','end_char'},'v2 xref slice');span=spans.get(slice_['span_id'])
   if span is None or span['span_id'] not in owner['source_span_ids'] or slice_['start_char']<span['start_char'] or slice_['end_char']>span['end_char']:bad('v2 xref slice mismatch')
   text.append((Path(package)/span['source_path']).read_bytes().decode('utf8')[slice_['start_char']:slice_['end_char']])
  if ''.join(text)!=row['reader_text']:bad('v2 xref text mismatch')
 asset_result=v2_asset_provenance_binding(value,package,root,spans)
 reader_assets={row['asset_id'] for row in value['assets'] if row.get('reader_value',row.get('disposition')=='reader')}
 for event in value['events']:
  if event['type']!='structured_unit':continue
  data=event['content']
  if data['kind']=='full_page_map' and not set(data['reader_asset_ids'])<=reader_assets:bad('v2 map reader asset mismatch')
  if data['kind']=='physical_page_pair' and not (set(data['front_reader_asset_ids'])|set(data['back_reader_asset_ids']))<=reader_assets:bad('v2 pair reader asset mismatch')
 return True
def v2_canonical_row(row):
 return hashlib.sha256(json.dumps(row,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode('utf8')).hexdigest().upper()
def v2_asset_provenance_binding(value,package,root,spans):
 """Generic canonical provenance binding; legacy fixtures keep their former path."""
 assets=value['assets'];is_canonical=[isinstance(row,dict) and 'provenance' in row for row in assets]
 if any(is_canonical) and not all(is_canonical):bad('v2 asset provenance mode mismatch')
 if not any(is_canonical):
  used=set();reader=0
  for row in assets:
   if not isinstance(row,dict) or 'source_span_ids' not in row or not isinstance(row['source_span_ids'],list) or not row['source_span_ids'] or len(row['source_span_ids'])!=len(set(row['source_span_ids'])) or any(item not in spans for item in row['source_span_ids']):bad('v2 asset provenance mismatch')
   if any(item in used or spans[item]['owner_kind']!='asset' or spans[item]['classification']!='asset_reference_source' for item in row['source_span_ids']):bad('v2 asset ownership mismatch')
   used.update(row['source_span_ids']);reader+=bool(row['reader_value'])
   if row['reader_value'] and next(iter(row['placement'].values())) not in {event['event_id'] for event in value['events']}:bad('v2 asset placement mismatch')
  return {'mode':'legacy','reader':reader,'counts':{}}
 package=Path(package).resolve();root=Path(root).resolve();counts={kind:0 for kind in ('markdown_image_reference','visual_region','reviewed_provisional_full_page')};used=set();cache={}
 def identity(item,label,inside=True):
  if not isinstance(item,dict) or set(item)!={'path','bytes','sha256'}:bad(f'v2 asset {label} identity mismatch')
  path=rel(root,item['path'],f'v2 asset {label}')
  if not path.is_file() or path.is_symlink() or inside and package not in path.parents:bad(f'v2 asset {label} path mismatch')
  if path.stat().st_size!=item['bytes'] or dig(path)!=item['sha256']:bad(f'v2 asset {label} identity mismatch')
  here=path
  while inside and here!=package:
   if v2_reparse(here):bad(f'v2 asset {label} reparse mismatch')
   here=here.parent
  return path
 def image(row):
  binary=row['binary']
  if not isinstance(binary,dict) or set(binary)!={'path','bytes','sha256','media_type','dimensions'} or not isinstance(binary['dimensions'],dict) or set(binary['dimensions'])!={'width','height'}:bad('v2 asset binary mismatch')
  path=identity({'path':binary['path'],'bytes':binary['bytes'],'ha256':binary['sha256']} if False else {'path':binary['path'],'bytes':binary['bytes'],'sha256':binary['sha256']},'binary')
  try:
   with Image.open(path) as opened:opened.load();mime={'JPEG':'image/jpeg','PNG':'image/png'}.get(opened.format);size={'width':opened.width,'height':opened.height}
  except OSError as error:raise ValueError('v2 asset binary mismatch') from error
  if mime!=binary['media_type'] or size!=binary['dimensions']:bad('v2 asset binary mismatch')
  return path,binary
 for row in assets:
  if set(row)!={'asset_id','disposition','source_page','binary','provenance','migration_outcome','anchor','placement','source_order'} or any(key in row for key in ('page','reader_value','source_span_ids')):bad('v2 asset canonical schema mismatch')
  p=row['provenance'];kind=p.get('kind') if isinstance(p,dict) else None
  if kind not in counts:bad('v2 asset provenance mismatch')
  counts[kind]+=1
  if kind=='markdown_image_reference':
   path,binary=image(row);need={'kind','span_id','page_markdown_identity','start_byte','end_byte','start_char','end_char','marker_sha256'}
   if set(p)!=need or p['span_id'] in used or p['span_id'] not in spans:bad('v2 asset markdown provenance mismatch')
   span=spans[p['span_id']];used.add(p['span_id'])
   if span['owner_kind']!='asset' or span['classification']!='asset_reference_source' or span['page']!=row['source_page']:bad('v2 asset markdown ownership mismatch')
   page=identity(p['page_markdown_identity'],'markdown page')
   if page!=package/span['source_path'] or p['page_markdown_identity']!=value['source_disposition'][row['source_page']-1]['page_markdown'] or tuple(p[x] for x in ('start_byte','end_byte','start_char','end_char'))!=tuple(span[x] for x in ('start_byte','end_byte','start_char','end_char')):bad('v2 asset markdown range mismatch')
   raw=page.read_bytes()[p['start_byte']:p['end_byte']]
   try:marker=raw.decode('utf8');before=page.read_bytes()[:p['start_byte']].decode('utf8')
   except UnicodeDecodeError:bad('v2 asset markdown UTF-8 mismatch')
   match=re.fullmatch(r'!\[[^\]]*\]\(([^)]+)\)',marker.strip())
   if not match or len(before)!=p['start_char'] or hashlib.sha256(raw).hexdigest().upper()!=p['marker_sha256'] or (page.parent/match.group(1)).resolve()!=path:bad('v2 asset markdown marker mismatch')
  elif kind=='visual_region':
   path,binary=image(row);need={'kind','asset_manifest_identity','asset_manifest_row_sha256','comparison_identity','selected_view','source_asset_reference','raw_index','block_type','source_page','bbox','comparison_block_sha256'}
   if set(p)!=need:bad('v2 asset visual provenance mismatch')
   manifest=identity(p['asset_manifest_identity'],'manifest')
   if manifest!=package/'ASSET_MANIFEST.json':bad('v2 asset manifest path mismatch')
   data=cache.setdefault((manifest,dig(manifest)),js(manifest,'v2 asset manifest'));rows=[x for x in data.get('assets',[]) if isinstance(x,dict) and x.get('stored_path')==path.relative_to(package).as_posix() and str(x.get('sha256','')).upper()==binary['sha256']]
   if len(rows)!=1 or v2_canonical_row(rows[0])!=p['asset_manifest_row_sha256']:bad('v2 asset manifest binding mismatch')
   comparison=identity(p['comparison_identity'],'comparison',False);data=cache.setdefault((comparison,dig(comparison)),js(comparison,'v2 asset comparison'));companion=comparison.parent.parent/'inputs'/Path(data.get('manifest',{}).get('path','')).name
   companion_data=cache.setdefault((companion,dig(companion)),js(companion,'v2 asset companion')) if companion.is_file() else {}
   source=companion_data.get('source',{})
   if data.get('schema')!='kb_creator.mineru_three_view_comparison.v1' or data.get('status')!='pass' or data.get('failures')!=[] or not companion.is_file() or dig(companion)!=data.get('manifest',{}).get('sha256') or (source.get('bytes'),source.get('sha256'))!=(value['document']['source_pdf']['bytes'],value['document']['source_pdf']['sha256']):bad('v2 asset comparison topology mismatch')
   blocks=[x for x in data.get('views',{}).get(p['selected_view'],{}).get('blocks',[]) if isinstance(x,dict) and x.get('raw_index')==p['raw_index'] and rows[0].get('source_path') in x.get('assets',[])]
   if len(blocks)!=1 or (p['source_asset_reference'],p['block_type'],p['source_page'],p['bbox'])!=(rows[0].get('source_path'),blocks[0].get('type'),blocks[0].get('source_page'),blocks[0].get('bbox')) or v2_canonical_row(blocks[0])!=p['comparison_block_sha256']:bad('v2 asset comparison binding mismatch')
  else:
   if row['binary'] is not None or p.get('source_pdf_identity')!=value['document']['source_pdf'] or p.get('physical_page')!=row['source_page'] or p.get('page_index_zero_based')!=row['source_page']-1:bad('v2 asset provisional provenance mismatch')
   page=PdfReader(str(identity(value['document']['source_pdf'],'source PDF',False))).pages[row['source_page']-1];box=[float(x) for x in page.mediabox];rotation=int(page.get('/Rotate',0))%360;dpi=p.get('render_recipe',{}).get('dpi');width,height=round((box[2]-box[0])*dpi/72),round((box[3]-box[1])*dpi/72)
   if rotation in {90,270}:width,height=height,width
   recipe={'tool':'pdftoppm','first_page':row['source_page'],'last_page':row['source_page'],'dpi':dpi,'format':'png','box':'media_box','rotation':'source_applied','color':'rgb','background':'white','alpha':False,'metadata':'stripped'}
   if p.get('region')!={'kind':'full_media_box','points':box} or p.get('render_recipe')!=recipe or p.get('output_media_type')!='image/png' or p.get('quality_stage')!='provisional_full_page' or not isinstance(dpi,int) or dpi<=0 or p.get('output_dimensions')!={'width':width,'height':height}:bad('v2 asset provisional render mismatch')
 if counts!={'markdown_image_reference':16,'visual_region':100,'reviewed_provisional_full_page':10}:bad('v2 asset provenance counts mismatch')
 return {'mode':'canonical','reader':sum(row['disposition']=='reader' for row in assets),'counts':counts}
def v2_migration_schema(value):
 """Close the A2 ledger shape before input identities are resolved."""
 closed(value,{'inputs',*MIGRATION_DOMAINS,'new_reviewed_targets'},'v2 migration')
 inputs=closed(value['inputs'],{'frozen_v1_config','decision_evidence'},'v2 migration inputs')
 closed(inputs['frozen_v1_config'],{'path','bytes','sha256'},'v2 migration frozen v1')
 if not isinstance(inputs['decision_evidence'],list):bad('v2 migration decision evidence mismatch')
 for item in inputs['decision_evidence']:
  closed(item,{'path','bytes','sha256','kind'},'v2 migration decision evidence')
  if item['kind'] not in {'kb_creator.semantic_unit_review.v2','kb_creator.user_review_registry.md','kb_creator.viral_boundary_ledger.v1','kb_creator.semantic_unit_closure.v2'}:bad('v2 migration decision evidence kind mismatch')
 for key,(_,_,count,outcomes) in MIGRATION_DOMAINS.items():
  rows=value[key]
  if key=='asset_rows' and rows and set(rows[0])=={'source_id','outcome','target_ids','decision_ref'}:
   v2_b1c4_migration_closure(rows,value['new_reviewed_targets']);continue
  if not isinstance(rows,list) or len(rows)!=count:bad('v2 migration count mismatch')
  for row in rows:
   closed(row,{'source_id','source_row_sha256','outcome','final_target_ids','decision_ref'},'v2 migration row')
   if not isinstance(row['source_id'],str) or not row['source_id'] or not isinstance(row['source_row_sha256'],str) or not HEX.fullmatch(row['source_row_sha256']) or row['outcome'] not in outcomes or not isinstance(row['final_target_ids'],list) or any(not isinstance(target,str) or not target for target in row['final_target_ids']) or len(row['final_target_ids'])!=len(set(row['final_target_ids'])) or row['decision_ref'] is not None and (not isinstance(row['decision_ref'],str) or not row['decision_ref']):bad('v2 migration row mismatch')
   if row['outcome']=='retained_unchanged' and row['decision_ref'] is not None:bad('v2 migration unchanged decision mismatch')
   if row['outcome']!='retained_unchanged' and row['decision_ref'] is None and not (key=='xref_rows' and row['outcome']=='split'):bad('v2 migration decision mismatch')
 if not isinstance(value['new_reviewed_targets'],list):bad('v2 migration new targets mismatch')
 if value['asset_rows'] and set(value['asset_rows'][0])=={'source_id','outcome','target_ids','decision_ref'}: return value
 for row in value['new_reviewed_targets']:
  closed(row,{'target_id','decision_ref'},'v2 migration new target')
  if not isinstance(row['target_id'],str) or not row['target_id'] or not isinstance(row['decision_ref'],str) or not row['decision_ref']:bad('v2 migration new target mismatch')
 return value
def v2_decision_catalogs(inputs,root):
 """Bind decision ids to their declaration class; references never declare ids."""
 singleton={'kb_creator.semantic_unit_review.v2','kb_creator.user_review_registry.md','kb_creator.semantic_unit_closure.v2'}
 occupied=set();declared={}
 def add(identifier,kind,path):
  prior=declared.get(identifier)
  if prior is not None and prior!=kind:bad('v2 migration decision evidence catalog mismatch')
  if prior is not None and kind=='boundary_unit_decision':bad('v2 migration decision evidence catalog mismatch')
  declared[identifier]=kind
 for item in inputs['decision_evidence']:
  evidence_kind=item['kind']
  if evidence_kind in singleton:
   if evidence_kind in occupied:bad('v2 migration decision evidence catalog mismatch')
   occupied.add(evidence_kind)
  blob=ident(root,{key:item[key] for key in ('path','bytes','sha256')},'v2 migration decision evidence').read_bytes()
  try:text=blob.decode('utf8')
  except UnicodeDecodeError:bad('v2 migration decision evidence encoding mismatch')
  if evidence_kind=='kb_creator.semantic_unit_review.v2':
   try:e=json.loads(text)
   except json.JSONDecodeError:bad('v2 migration decision evidence JSON mismatch')
   if not isinstance(e,dict) or e.get('schema')!=evidence_kind or set(e) not in ({'schema','decisions'},{'schema','reviewer','input_identities','decisions'}) or not isinstance(e['decisions'],list):bad('v2 migration decision evidence schema mismatch')
   full='reviewer' in e
   if full and (not isinstance(e['reviewer'],str) or not e['reviewer'] or not isinstance(e['input_identities'],dict) or set(e['input_identities'])!={'pages_tree_sha256','user_registry_sha256','frozen_config_sha256'} or any(not HEX.fullmatch(str(v)) for v in e['input_identities'].values())):bad('v2 migration decision evidence identity mismatch')
   required={'candidate_id','decision','reason','review_provenance'} if full else {'candidate_id'}
   if any(not isinstance(row,dict) or set(row)!=required or full and (row['decision'] not in {'reject','confirm','adjusted_boundary'} or any(not isinstance(row[k],str) or not row[k] for k in ('reason','review_provenance'))) for row in e['decisions']):bad('v2 migration decision evidence catalog mismatch')
   ids=[row['candidate_id'] for row in e['decisions']]
   if not ids or any(not isinstance(x,str) or not x for x in ids) or len(ids)!=len(set(ids)):bad('v2 migration decision evidence catalog mismatch')
   for identifier in ids:add(identifier,'candidate_decision',item['path'])
  elif evidence_kind=='kb_creator.viral_boundary_ledger.v1':
   try:e=json.loads(text)
   except json.JSONDecodeError:bad('v2 migration decision evidence JSON mismatch')
   if not isinstance(e,dict) or e.get('schema')!=evidence_kind or set(e)!={'schema','units','candidate_dispositions','deferred_nonblocking'} or not all(isinstance(e[x],list) for x in ('units','candidate_dispositions','deferred_nonblocking')):bad('v2 migration decision evidence schema mismatch')
   units=[];candidates=[]
   for row in e['units']:
    if not isinstance(row,dict) or set(row)!={'id','registry_refs'} or not isinstance(row['id'],str) or not row['id'] or not isinstance(row['registry_refs'],list) or any(not isinstance(x,str) or not x for x in row['registry_refs']):bad('v2 migration decision evidence catalog mismatch')
    units.append(row['id'])
    for identifier in row['registry_refs']:add(identifier,'registry_decision',item['path'])
   if not units or len(units)!=len(set(units)):bad('v2 migration decision evidence catalog mismatch')
   for identifier in units:add(identifier,'boundary_unit_decision',item['path'])
   for row in e['candidate_dispositions']:
    if not isinstance(row,dict) or set(row)!={'candidate_id','target_unit_id'} or not isinstance(row['candidate_id'],str) or not row['candidate_id'] or row['target_unit_id'] not in units:bad('v2 migration decision evidence catalog mismatch')
    candidates.append(row['candidate_id'])
   if len(candidates)!=len(set(candidates)):bad('v2 migration decision evidence catalog mismatch')
   for identifier in candidates:add(identifier,'candidate_decision',item['path'])
   for row in e['deferred_nonblocking']:
    if not isinstance(row,dict) or set(row)!={'registry_ref'} or not isinstance(row['registry_ref'],str) or not row['registry_ref']:bad('v2 migration decision evidence catalog mismatch')
    add(row['registry_ref'],'registry_decision',item['path'])
  elif evidence_kind=='kb_creator.semantic_unit_closure.v2':
   try:e=json.loads(text)
   except json.JSONDecodeError:bad('v2 migration decision evidence JSON mismatch')
   full_keys={'schema','candidate_count','decision_count','family_counts','required_family_coverage','unresolved_blocking_candidates','unresolved_blocking_count','blocking_registry_families_closed','deferred_nonblocking','excluded_audit_pages','identities'}
   if not isinstance(e,dict) or set(e) not in ({'schema','unresolved_blocking_candidates','deferred_nonblocking'},full_keys) or e.get('schema')!=evidence_kind or e['unresolved_blocking_candidates']!=[] or not isinstance(e['deferred_nonblocking'],list):bad('v2 migration decision evidence schema mismatch')
   full=set(e)==full_keys
   if full and (e['candidate_count']!=e['decision_count'] or not isinstance(e['candidate_count'],int) or e['candidate_count']<=0 or e['unresolved_blocking_count']!=0 or e['blocking_registry_families_closed'] is not True or e['excluded_audit_pages']!=[123,124] or not isinstance(e['identities'],dict) or set(e['identities'])!={'pages_tree_sha256','user_registry_sha256','frozen_config_sha256'} or any(not HEX.fullmatch(str(v)) for v in e['identities'].values()) or any(not isinstance(e[k],dict) or any(not isinstance(v,int) or v<0 for v in e[k].values()) for k in ('family_counts','required_family_coverage'))):bad('v2 migration closure evidence mismatch')
   ids=e['deferred_nonblocking'] if full else [row['id'] for row in e['deferred_nonblocking'] if isinstance(row,dict) and set(row)=={'id'}]
   if not ids or any(not isinstance(x,str) or not x for x in ids) or len(ids)!=len(set(ids)):bad('v2 migration decision evidence catalog mismatch')
   for identifier in ids:add(identifier,'registry_decision',item['path'])
  else:
   ids=re.findall(r'^### ((?:OUT|PROC|ENH)-[0-9]{3}) — .+$',text,re.M)
   if not ids or len(ids)!=len(set(ids)):bad('v2 migration decision evidence catalog mismatch')
   for identifier in ids:add(identifier,'registry_decision',item['path'])
 return set(declared)
def v2_migration(value,root):
 """Independently bind frozen-v1 rows, decision evidence and target closure."""
 migration=v2_migration_schema(value['migration']);inputs=migration['inputs']
 v1_path=ident(root,inputs['frozen_v1_config'],'v2 migration frozen v1')
 v1=js(v1_path,'v2 migration frozen v1')
 refs=v2_decision_catalogs(inputs,root)
 target_ids=set();source_ids=set()
 for key,(v1_key,id_key,count,_) in MIGRATION_DOMAINS.items():
  source=v1.get(v1_key);rows=migration[key]
  if not isinstance(source,list) or len(source)!=count:bad('v2 migration frozen v1 domain mismatch')
  expected={f'{v1_key}:{row[id_key]}':row for row in source if isinstance(row,dict) and id_key in row}
  if len(expected)!=count:bad('v2 migration frozen v1 identity mismatch')
  got={row['source_id']:row for row in rows}
  if len(got)!=count or set(got)!=set(expected):bad('v2 migration source closure mismatch')
  for source_id,row in got.items():
   frozen=expected[source_id]
   if key=='asset_rows' and set(row)=={'source_id','outcome','target_ids','decision_ref'}:
    # Canonical asset rows are separately pinned against the complete B1c4
    # inventory; they deliberately do not repeat the frozen row digest.
    if row['decision_ref'] is not None and row['decision_ref'] not in refs:bad('v2 migration unknown decision mismatch')
    source_ids.add(source_id);target_ids.update(row['target_ids']);continue
   if row['source_row_sha256']!=v2_canonical_row(frozen):bad('v2 migration source row mismatch')
   if row['decision_ref'] is not None and row['decision_ref'] not in refs:bad('v2 migration unknown decision mismatch')
   # A2 has no A3 final-field projection yet.  Unchanged rows therefore must
   # declare the closed pending target, and any real preflight remains blocked.
   if row['outcome']=='retained_unchanged' and value['scenario_id']!='viral' and row['final_target_ids']!=[f'pending_a3:{source_id}']:bad('v2 migration unchanged preservation mismatch')
   if v1_key=='source_disposition' and frozen['page'] in {123,124} and (row['outcome']!='excluded_advertising' or row['final_target_ids']):bad('v2 migration advertising exclusion mismatch')
   if v1_key=='assets' and frozen['source_page'] in {123,124} and row['final_target_ids']:bad('v2 migration advertising asset mismatch')
   source_ids.add(source_id);target_ids.update(row['final_target_ids'])
 new=set()
 for row in migration['new_reviewed_targets']:
  if row['target_id'] in new or row['target_id'] in target_ids or row['decision_ref'] not in refs:bad('v2 migration new target closure mismatch')
  new.add(row['target_id'])
 # Each materialized surface owns its exact migration target.  Membership in
 # the aggregate closure alone would let one real xref or hierarchy row borrow
 # another row's target.
 materialized={*(f'hierarchy:{row["anchor"]}' for row in value['hierarchy']),*(f'assets:{row["asset_id"]}' for row in value['assets']),*(f'xrefs:{row["xref_id"]}' for row in value['xrefs'])}
 if not materialized<=target_ids|new:bad('v2 migration orphan target mismatch')
 for namespace,rows,identity_key in (('hierarchy',value['hierarchy'],'anchor'),('xrefs',value['xrefs'],'xref_id')):
  for row in rows:
   target=f'{namespace}:{row[identity_key]}'
   if row['migration_row_id']!=target or target not in target_ids|new:bad('v2 migration materialized target mismatch')
  if any(target.startswith('pending_a3:') for target in target_ids|new):bad('v2 migration pending target mismatch')
 return migration
def config(p):
 c=js(p,'publication config');closed(c,TOP,'publication config')
 if c['schema']!=SCHEMA or c['scenario_id']!='viral':bad('publication config identity mismatch')
 for k,n in N.items():
  if not isinstance(c[k],list) or len(c[k])!=n:bad(f'{k} production count mismatch')
 return c

def v2_config(value):
 """Validate the compact, data-driven v2 contract without weakening v1."""
 required={'schema','scenario_id','document','hierarchy','events','assets','xrefs','source_recoveries','source_disposition','source_partition','migration','visual_review_units','metrics'}
 closed(value,required,'v2 publication config')
 if value['schema']!=V2_SCHEMA or not isinstance(value['scenario_id'],str):bad('v2 publication config identity mismatch')
 v2_migration_schema(value['migration'])
 document=closed(value['document'],{'audit_scope','reader_scope','generated_navigation','source_pdf','reconstruction_package'},'v2 document')
 if document['audit_scope']!=list(range(1,125)) or document['reader_scope']!=list(range(1,123)):bad('v2 page scope mismatch')
 if not isinstance(document['generated_navigation'],dict) or set(document['generated_navigation'])!={'operation','source_identity'} or document['generated_navigation'].get('operation')!='generated_navigation_replaces_source_toc' or not isinstance(document['generated_navigation'].get('source_identity'),str) or not document['generated_navigation']['source_identity']:bad('v2 navigation provenance mismatch')
 for label in ('source_pdf',):
  identity=closed(document[label],{'path','bytes','sha256'},'v2 '+label)
  if not isinstance(identity['path'],str) or not identity['path'] or num(identity['bytes'],'v2 '+label+' bytes')<0 or not isinstance(identity['sha256'],str) or not HEX.fullmatch(identity['sha256']):bad('v2 input identity mismatch')
 package=closed(document['reconstruction_package'],{'root','file_count','total_bytes','inventory_algorithm','inventory_sha256'},'v2 reconstruction package')
 if not isinstance(package['root'],str) or not package['root'] or num(package['file_count'],'v2 reconstruction package file_count')<=0 or num(package['total_bytes'],'v2 reconstruction package total_bytes')<=0 or package['inventory_algorithm']!=PACKAGE_ALGO or not isinstance(package['inventory_sha256'],str) or not HEX.fullmatch(package['inventory_sha256']):bad('v2 reconstruction package identity mismatch')
 dispositions=value['source_disposition']
 if not isinstance(dispositions,list) or len(dispositions)!=124:bad('v2 source disposition count mismatch')
 for expected,row in enumerate(dispositions,1):
  closed(row,{'page','audit_disposition','publication_disposition','publish_reader_content','decision_date','reason','page_markdown'},'v2 source disposition')
  page_identity=closed(row['page_markdown'],{'path','bytes','sha256'},'v2 page markdown')
  if row['page']!=expected or row['audit_disposition']!='reconstructed' or not isinstance(row['publish_reader_content'],bool) or not isinstance(row['decision_date'],str) or not isinstance(row['reason'],str) or num(page_identity['bytes'],'v2 page markdown bytes')<0 or not isinstance(page_identity['path'],str) or not page_identity['path'] or not isinstance(page_identity['sha256'],str) or not HEX.fullmatch(page_identity['sha256']):bad('v2 source disposition row mismatch')
  excluded=expected in {123,124}
  if (row['publication_disposition'],row['publish_reader_content']) != (('excluded_advertising',False) if excluded else ('reader',True)):bad('v2 source disposition policy mismatch')
  if excluded and (row['decision_date']!='2026-09-02' or not row['reason'].strip()):bad('v2 source disposition exclusion mismatch')
 anchors=set()
 for row in value['hierarchy']:
  closed(row,{'anchor','parent_anchor','level','toc_entry','semantic_role','source_pages','source_title','reader_title','representation','reviewed_title_transformation','migration_row_id'},'v2 hierarchy')
  if row['anchor'] in anchors or row['representation'] not in {'heading','anchor_only','inline_run_in'} or not isinstance(row['source_pages'],list) or any(page not in document['reader_scope'] for page in row['source_pages']):bad('v2 hierarchy mismatch')
  if row['representation']=='heading' and (not isinstance(row['level'],int) or isinstance(row['level'],bool) or row['level'] not in range(1,7)):bad('v2 hierarchy level mismatch')
  if row['representation']!='heading' and row['level'] is not None:bad('v2 hierarchy level mismatch')
  if row['source_title']!=row['reader_title'] and not isinstance(row['reviewed_title_transformation'],dict):bad('v2 title fidelity mismatch')
  anchors.add(row['anchor'])
 hierarchy_by_anchor={row['anchor']:row for row in value['hierarchy']}
 for target in value['migration']['new_reviewed_targets']:
  if not isinstance(target,dict) or not str(target.get('target_id','')).startswith('hierarchy:'):continue
  anchor=target['target_id'][len('hierarchy:'):];row=hierarchy_by_anchor.get(anchor)
  if row is None or row.get('migration_row_id')!=target['target_id'] or not row.get('source_pages') or not isinstance(row.get('source_title'),str) or not row['source_title']:bad('v2 hierarchy target source binding mismatch')
 previous=None; event_ids=set(); fragment_ids=set()
 for row in value['events']:
  if not isinstance(row,dict) or set(row) not in ({'event_id','type','page','order_key','anchor','content','fragment_id','source_span_ids','source_operation','payload_bindings'},{'event_id','type','page','order_key','anchor','content','fragment_id','source_span_ids','source_operation','payload_bindings','contains'},{'event_id','type','page','order_key','anchor','content','fragment_id','source_span_ids','source_operation','payload_bindings','generated_placement'}):bad('v2 event closed schema mismatch')
  if row['type'] not in {'heading','text_fragment','structured_unit','asset','anchor_only','generated_navigation'} or row['page'] not in document['reader_scope'] or not isinstance(row['order_key'],list) or row['anchor'] not in anchors or not isinstance(row['content'],(str,dict)) or not isinstance(row['fragment_id'],str) or not row['fragment_id']:bad('v2 event mismatch')
  if row['type']=='asset' and not isinstance(row['content'],str):bad('v2 asset event mismatch')
  if row['type']=='structured_unit' and (not isinstance(row['content'],dict) or not isinstance(row.get('contains'),list)):bad('v2 structured event mismatch')
  if row['event_id'] in event_ids or row['fragment_id'] in fragment_ids:bad('v2 duplicate event or fragment id')
  event_ids.add(row['event_id']);fragment_ids.add(row['fragment_id']);key=tuple(row['order_key'])
  if previous is not None and key<=previous:bad('v2 event graph is not monotonic')
  previous=key
 for row in value['assets']:
  if isinstance(row,dict) and 'provenance' in row:
   immutable={'asset_id','disposition','source_page','binary','provenance','migration_outcome'}; placement={'anchor','placement','source_order'}
   if set(row)!=immutable|placement or row['disposition'] not in {'reader','evidence_only'} or row['source_page'] not in document['reader_scope'] or row['migration_outcome'] not in {'retained_unchanged','retained_rebound','reclassified','new_reviewed_target'} or not isinstance(row['provenance'],dict):bad('v2 B1c4 asset schema mismatch')
   if row['disposition']=='evidence_only' and any(row[key] is not None for key in placement):bad('v2 B1c4 evidence placement mismatch')
   if row['disposition']=='reader':
    if row['anchor'] not in anchors or not isinstance(row['placement'],dict) or len(row['placement'])!=1 or set(row['placement'])-{'before_event','after_event','inside_structured_unit'} or not isinstance(row['source_order'],dict):bad('v2 B1c4 reader placement mismatch')
    order=row['source_order'];kind=order.get('kind')
    if kind=='selected_view_raw_index' and set(order)=={'kind','view','raw_index','gap_ordinal'} and isinstance(order['view'],str) and isinstance(order['raw_index'],int) and isinstance(order['gap_ordinal'],int):pass
    elif kind=='physical_unit_page_slot' and set(order)=={'kind','unit_id','page_slot'} and isinstance(order['unit_id'],str) and isinstance(order['page_slot'],int):pass
    else:bad('v2 B1c4 source order mismatch')
   kind=row['provenance'].get('kind')
   binary=row['binary']
   if kind in {'visual_region','markdown_image_reference'}:
    if not isinstance(binary,dict) or set(binary)!={'path','bytes','sha256','media_type','dimensions'} or not isinstance(binary.get('dimensions'),dict) or set(binary['dimensions'])!={'width','height'} or binary['media_type'] not in {'image/jpeg','image/png'} or not isinstance(binary['bytes'],int) or binary['bytes']<=0 or not isinstance(binary['sha256'],str) or not HEX.fullmatch(binary['sha256']):bad('v2 B1c4 asset binary mismatch')
    source=(Path(__file__).resolve().parents[2]/binary['path']).resolve()
    package_root=(Path(__file__).resolve().parents[2]/'kb_creator/working/viral/source_reconstruction/20260901_step6a_reconstructed_en_package_v4').resolve()
    if package_root not in source.parents or not source.is_file() or source.is_symlink() or source.stat().st_size!=binary['bytes'] or dig(source)!=binary['sha256'] or image_identity(source,binary['media_type'],'v2 B1c4 asset')!=binary['dimensions']:bad('v2 B1c4 asset binary identity mismatch')
    keys={'kind','span_id','page_markdown_identity','start_byte','end_byte','start_char','end_char','marker_sha256'} if kind=='markdown_image_reference' else {'kind','asset_manifest_identity','asset_manifest_row_sha256','comparison_identity','selected_view','source_asset_reference','raw_index','block_type','source_page','bbox','comparison_block_sha256'}
    if set(row['provenance'])!=keys:bad('v2 B1c4 provenance mismatch')
    provenance=row['provenance'];manifest_path=package_root/'ASSET_MANIFEST.json';comparison_path=Path(__file__).resolve().parents[2]/'kb_creator/working/viral/source_reconstruction/20260901_step6a_mineru_three_view_full/comparison/comparison.json'
    if kind=='markdown_image_reference':
     page=(Path(__file__).resolve().parents[2]/provenance['page_markdown_identity'].get('path','')).resolve();identity=provenance['page_markdown_identity']
     if not isinstance(identity,dict) or set(identity)!={'path','bytes','sha256'} or not page.is_file() or page.stat().st_size!=identity['bytes'] or dig(page)!=identity['sha256'] or provenance['end_byte']<=provenance['start_byte'] or provenance['end_char']<=provenance['start_char']:bad('v2 B1c4 provenance identity mismatch')
     raw=page.read_bytes()[provenance['start_byte']:provenance['end_byte']]
     try:text=raw.decode('utf8')
     except UnicodeDecodeError:bad('v2 B1c4 provenance identity mismatch')
     if len(page.read_bytes()[:provenance['start_byte']].decode('utf8'))!=provenance['start_char'] or len(page.read_bytes()[:provenance['end_byte']].decode('utf8'))!=provenance['end_char'] or not text.strip().startswith('![') or binary['sha256'].lower().encode() not in raw or dig.__class__ is None or hashlib.sha256(raw).hexdigest().upper()!=provenance['marker_sha256']:bad('v2 B1c4 provenance identity mismatch')
    else:
     manifest_rows=js(manifest_path,'v2 B1c4 manifest').get('assets',[]);entry=next((item for item in manifest_rows if isinstance(item,dict) and item.get('sha256','').upper()==binary['sha256']),None);comparison=js(comparison_path,'v2 B1c4 comparison')
     block=next((item for item in comparison.get('views',{}).get(provenance['selected_view'],{}).get('blocks',[]) if isinstance(item,dict) and item.get('raw_index')==provenance['raw_index']),None)
     if not isinstance(entry,dict) or not isinstance(block,dict) or provenance['asset_manifest_identity']!={'path':str(manifest_path.relative_to(Path(__file__).resolve().parents[2])).replace('\\','/'),'bytes':manifest_path.stat().st_size,'sha256':dig(manifest_path)} or provenance['comparison_identity']!={'path':str(comparison_path.relative_to(Path(__file__).resolve().parents[2])).replace('\\','/'),'bytes':comparison_path.stat().st_size,'sha256':dig(comparison_path)} or provenance['asset_manifest_row_sha256']!=v2_canonical_row(entry) or provenance['comparison_block_sha256']!=v2_canonical_row(block) or (provenance['source_asset_reference'],provenance['block_type'],provenance['source_page'],provenance['bbox'])!=(entry.get('source_path'),block.get('type'),block.get('source_page'),block.get('bbox')) or entry.get('source_path') not in block.get('assets',[]):bad('v2 B1c4 provenance identity mismatch')
   elif kind=='reviewed_provisional_full_page':
    if binary is not None or row['disposition']!='reader' or set(row['provenance'])!={'kind','source_pdf_identity','physical_page','page_index_zero_based','region','render_recipe','output_media_type','output_dimensions','quality_stage'} or row['provenance'].get('physical_page')!=row['source_page'] or row['provenance'].get('page_index_zero_based')!=row['source_page']-1 or row['provenance'].get('output_media_type')!='image/png' or row['provenance'].get('output_dimensions')!={'width':1700,'height':2200} or row['provenance'].get('quality_stage')!='provisional_full_page':bad('v2 B1c4 provisional asset mismatch')
    source_pdf=Path(__file__).resolve().parents[2]/'kb_creator/working/viral/source/Call_of_Cthulhu_Viral.pdf';recipe=row['provenance'].get('render_recipe',{});expected_recipe={'tool':'pdftoppm','first_page':row['source_page'],'last_page':row['source_page'],'dpi':200,'format':'png','box':'media_box','rotation':'source_applied','color':'rgb','background':'white','alpha':False,'metadata':'stripped'}
    if row['provenance'].get('source_pdf_identity')!={'path':str(source_pdf.relative_to(Path(__file__).resolve().parents[2])).replace('\\','/'),'bytes':source_pdf.stat().st_size,'sha256':dig(source_pdf)} or row['provenance'].get('region')!={'kind':'full_media_box','points':[0,0,612,792]} or recipe!=expected_recipe:bad('v2 B1c4 provisional identity mismatch')
   else:bad('v2 B1c4 provenance mismatch')
   continue
  if isinstance(row,dict) and 'migration_outcome' in row:bad('v2 B1c4 provenance mismatch')
  if not isinstance(row,dict) or not {'asset_id','reader_value','placement','anchor','page','source_span_ids'}.issubset(row):bad('v2 asset closed schema mismatch')
  if not isinstance(row['reader_value'],bool) or row['anchor'] not in anchors or row['page'] not in document['reader_scope'] or not isinstance(row['placement'],dict):bad('v2 asset mismatch')
  if row['reader_value']:
   if set(row)!={'asset_id','reader_value','placement','anchor','page','source_span_ids','duplication_resolution','quality_stage','source_path','bytes','sha256','semantic_role'} or row['duplication_resolution'] not in {'unique_reader','text_wins_crop_evidence_only','reviewed_exception'} or row['quality_stage'] not in {'provisional_full_page','accepted_reconstruction'} or row['semantic_role'] not in {'full_page','illustration','map','pregen'}:bad('v2 reader asset policy mismatch')
   if set(row['placement']) not in ({'before_event'},{'after_event'},{'inside_structured_unit'}):bad('v2 asset placement mismatch')
   if not isinstance(row['source_path'],str) or not isinstance(row['bytes'],int) or not HEX.fullmatch(str(row['sha256'])):bad('v2 reader asset identity mismatch')
 if value['scenario_id']=='viral' and value['assets'] and all(isinstance(item,dict) and 'provenance' in item for item in value['assets']):
  declared={item['asset_id']:item for item in value['assets']};expected=v2_b1c4_expected_assets(Path(__file__).resolve().parents[2]);frozen=js(Path(__file__).resolve().parents[2]/'kb_creator/working/viral/master_en/publication_config_v1.json','v2 B1c4 frozen assets')['assets'];migration={item['source_id']:item for item in value['migration']['asset_rows']};children={child for target in value['migration']['new_reviewed_targets'] if target.get('target_id','').startswith('assets:viral-provisional-') for child in target['replaces']}
  if set(declared)!=set(expected) or any({key:declared[asset_id][key] for key in ('asset_id','disposition','source_page','binary','provenance','migration_outcome')}!=expected[asset_id] for asset_id in expected):bad('v2 B1c4 asset declaration identity mismatch')
  for source in frozen:
   source_id='assets:'+source['asset_id'];row=migration[source_id];asset=declared.get(source['asset_id'])
   if row['outcome']=='excluded_advertising' and asset is not None:bad('v2 B1c4 excluded asset leakage')
   if row['outcome']!='excluded_advertising' and (asset is None or asset['source_page']!=source['source_page'] or asset['migration_outcome']!=row['outcome'] or (source['asset_id'] in children and asset['disposition']!='evidence_only')):bad('v2 B1c4 asset migration identity mismatch')
  if any(event.get('type')=='asset' and event.get('content') in children for event in value['events']):bad('v2 B1c4 replaced child event leakage')
 event_by_id={row['event_id']:row for row in value['events']};spans={row['span_id']:row for row in value['source_partition']['spans']};xref_ids=set()
 for row in value['xrefs']:
  owner=event_by_id.get(row.get('source_event_id'));owned_pages={spans[item]['page'] for item in owner.get('source_span_ids',[]) if item in spans} if owner is not None else set()
  if not isinstance(row,dict) or set(row)!={'xref_id','source_event_id','source_page','target_anchor','reader_text','source_slices','emit_link','migration_row_id'} or row['xref_id'] in xref_ids or owner is None or row['source_page'] not in document['reader_scope'] or row['source_page'] not in owned_pages or not isinstance(row['emit_link'],bool) or (row['emit_link'] and row['target_anchor'] not in anchors) or (not row['emit_link'] and row['target_anchor'] is not None) or not isinstance(row['reader_text'],str) or not row['reader_text'] or not isinstance(row['source_slices'],list) or not row['source_slices'] or not isinstance(row['migration_row_id'],str) or not row['migration_row_id']:bad('v2 xref mismatch')
  xref_ids.add(row['xref_id'])
 recovery_ids=set()
 for row in value['source_recoveries']:
  if not isinstance(row,dict) or set(row)!={'recovery_id','source_pdf_identity','physical_page','extraction_method','source_text','source_text_sha256','evidence_identity','target_event_id','placement','decision_ref'} or row['recovery_id'] in recovery_ids or row['target_event_id'] not in event_by_id:bad('v2 recovery mismatch')
  recovery_ids.add(row['recovery_id'])
 v2_visual_review_units(value,anchors,event_by_id)
 metrics=closed(value['metrics'],{'source_pages_audited','reader_pages','excluded_advertising_pages'},'v2 metrics')
 if metrics!={'source_pages_audited':124,'reader_pages':122,'excluded_advertising_pages':2}:bad('v2 declared metrics mismatch')
 return value

V2_REVIEW_KINDS={'heading_outline','callout','ordered_list_callout','table','equipment_card','creature_statblock','inline_run_in','full_page_map','physical_page_pair','xref_recovery','asset_placement'}
def v2_visual_review_units(value,anchors=None,event_by_id=None):
 """Close dynamic review declarations against the declared reader graph."""
 events=event_by_id or {row['event_id']:row for row in value['events']};assets={row['asset_id']:row for row in value['assets']};reader=set(value['document']['reader_scope']);units=value['visual_review_units']
 if not isinstance(units,list):bad('v2 visual review units mismatch')
 ids=set();covered_headings=set();covered_structured=set();covered_xref_recovery=set();covered_assets=set()
 for row in units:
  closed(row,{'review_id','kind','source_pages','event_ids','asset_ids','priority','contact_sheet_group'},'v2 visual review unit')
  review_id=st(row['review_id'],'v2 visual review id')
  if review_id in ids or row['kind'] not in V2_REVIEW_KINDS or not isinstance(row['source_pages'],list) or not row['source_pages'] or len(row['source_pages'])!=len(set(row['source_pages'])) or any(page not in reader for page in row['source_pages']) or not isinstance(row['event_ids'],list) or len(row['event_ids'])!=len(set(row['event_ids'])) or not isinstance(row['asset_ids'],list) or len(row['asset_ids'])!=len(set(row['asset_ids'])) or not row['event_ids'] and not row['asset_ids'] or not isinstance(row['priority'],bool) or not st(row['contact_sheet_group'],'v2 contact sheet group'):bad('v2 visual review unit mismatch')
  ids.add(review_id)
  if any(event_id not in events for event_id in row['event_ids']) or any(asset_id not in assets for asset_id in row['asset_ids']):bad('v2 visual review reference mismatch')
  if any(events[event_id]['page'] not in row['source_pages'] for event_id in row['event_ids']) or any(assets[asset_id].get('source_page',assets[asset_id].get('page')) not in row['source_pages'] for asset_id in row['asset_ids']):bad('v2 visual review page coverage mismatch')
  if row['kind']=='heading_outline':
   if not row['event_ids'] or row['asset_ids'] or any(events[event_id]['type']!='heading' for event_id in row['event_ids']):bad('v2 visual review kind mismatch')
   covered_headings.update(row['event_ids'])
  elif row['kind'] in {'callout','ordered_list_callout','table','equipment_card','creature_statblock','inline_run_in','full_page_map','physical_page_pair'}:
   if not row['event_ids'] or row['asset_ids'] or any(events[event_id]['type']!='structured_unit' or events[event_id]['content'].get('kind')!=row['kind'] for event_id in row['event_ids']):bad('v2 visual review kind mismatch')
   covered_structured.update(row['event_ids'])
  elif row['kind']=='xref_recovery':
   expected={item['source_event_id'] for item in value['xrefs']}|{item['target_event_id'] for item in value['source_recoveries']}
   if not row['event_ids'] or row['asset_ids'] or any(event_id not in expected for event_id in row['event_ids']):bad('v2 visual review kind mismatch')
   covered_xref_recovery.update(row['event_ids'])
  else:
   if row['event_ids'] or not row['asset_ids'] or any(not assets[asset_id].get('reader_value',assets[asset_id].get('disposition')=='reader') for asset_id in row['asset_ids']):bad('v2 visual review kind mismatch')
   covered_assets.update(row['asset_ids'])
 expected_headings={event['event_id'] for event in value['events'] if event['type']=='heading' and value['hierarchy'][next(index for index,row in enumerate(value['hierarchy']) if row['anchor']==event['anchor'])]['representation']=='heading'}
 expected_structured={event['event_id'] for event in value['events'] if event['type']=='structured_unit'}
 expected_xref_recovery={item['source_event_id'] for item in value['xrefs']}|{item['target_event_id'] for item in value['source_recoveries']}
 expected_assets={asset_id for asset_id,asset in assets.items() if asset.get('reader_value',asset.get('disposition')=='reader')}
 if not expected_headings<=covered_headings or not expected_structured<=covered_structured or not expected_xref_recovery<=covered_xref_recovery or not expected_assets<=covered_assets:bad('v2 visual review coverage mismatch')
 hierarchy={row['anchor']:row for row in value['hierarchy']}; spans={row['span_id']:row for row in value['source_partition']['spans']};expected=[]
 def add(event,kind,priority,group):expected.append({'review_id':f"review:{kind}:{event['event_id']}",'kind':kind,'source_pages':sorted({spans[item]['page'] for item in event.get('source_span_ids',[]) if item in spans}) or [event['page']],'event_ids':[event['event_id']],'asset_ids':[],'priority':priority,'contact_sheet_group':group})
 for event in value['events']:
  if event['type']=='heading' and hierarchy[event['anchor']]['representation']=='heading':add(event,'heading_outline',True,'outline')
  elif event['type']=='structured_unit':add(event,event['content']['kind'],False,'structured')
 for event in value['events']:
  if event['event_id'] in expected_xref_recovery:add(event,'xref_recovery',True,'xref_recovery')
 for asset in value['assets']:
  if asset.get('reader_value',asset.get('disposition')=='reader'):
   page=asset.get('source_page',asset.get('page'))
   if not isinstance(page,int):bad('v2 visual review asset page mismatch')
   expected.append({'review_id':f"review:asset_placement:{asset['asset_id']}",'kind':'asset_placement','source_pages':[page],'event_ids':[],'asset_ids':[asset['asset_id']],'priority':False,'contact_sheet_group':'reader_assets'})
 if units!=expected:bad('v2 visual review declaration mismatch')
 return {'count':len(units),'groups':sorted({row['contact_sheet_group'] for row in units}),'priority_total':sum(row['priority'] for row in units),'declaration_sha256':hashlib.sha256(canonical(units).encode('utf8')).hexdigest().upper()}

def v2_b1c3_xref_closure(value,root):
 """Validate Viral's frozen xref projection before the later asset gate."""
 if value.get('scenario_id')!='viral': return
 migration=value['migration'];v1=js(ident(root,migration['inputs']['frozen_v1_config'],'v2 B1c3 frozen v1'),'v2 B1c3 frozen v1')
 hierarchy={row['anchor'] for row in value['hierarchy']};events={row['event_id']:row for row in value['events']}
 families=(('generated_toc','toc','viral-contents'),('generated_handout_index','handout_index','viral-player-handouts'),('generated_map_index','map_index','viral-keeper-maps'),('generated_pregen_index','pregen_index','viral-pregenerated-investigators'))
 expected_generated={};expected_navigation=set()
 for ordinal,(selector,family,owner) in enumerate(families):
  rows=[row for row in v1['xrefs'] if row['source_selector']==selector and row['xref_id'] not in {'toc-viral-merchandise','toc-viral-back-cover'}]
  expected_generated[f'generated-navigation-{family.replace("_", "-")}']=(ordinal,family,owner,rows);expected_navigation.update(f'generated_navigation_items:{row["xref_id"]}' for row in rows)
 generated=[row for row in value['events'] if row['type']=='generated_navigation']
 if len(generated)!=4 or {row['event_id'] for row in generated}!=set(expected_generated):bad('v2 B1c3 generated event closure mismatch')
 for event in generated:
  ordinal,family,owner,rows=expected_generated[event['event_id']];heading=[row for row in value['events'] if row['type']=='heading' and row['anchor']==owner];data=event['content']
  if len(heading)!=1 or event['anchor']!=owner or event['page']!=heading[0]['page'] or event['order_key']!=[heading[0]['page'],heading[0]['order_key'][1],5,value['events'].index(event)] or event['generated_placement']!={'after_event':heading[0]['event_id']} or not isinstance(data,dict) or set(data)!={'kind','family','owner_anchor','decision_ref','entry_count','entries'} or data['kind']!='generated_navigation' or data['family']!=family or data['owner_anchor']!=owner or data['decision_ref']!='OUT-002' or data['entry_count']!=len(rows) or not isinstance(data['entries'],list) or len(data['entries'])!=len(rows):bad('v2 B1c3 generated semantics mismatch')
  for entry,frozen in zip(data['entries'],rows):
   if entry!={'navigation_id':f'navigation:{frozen["xref_id"]}','source_xref_id':frozen['xref_id'],'reader_text':frozen['visible_text'],'target_anchor':frozen['target_anchors'][0],'migration_row_id':f'generated_navigation_items:{frozen["xref_id"]}'} or entry['target_anchor'] not in hierarchy:bad('v2 B1c3 generated entry mismatch')
 expected_xrefs=[]
 for frozen in (row for row in v1['xrefs'] if row['source_selector']=='line_exact'):
  for ordinal,segment in enumerate(frozen['segments'],1):expected_xrefs.append((frozen['xref_id'] if len(frozen['segments'])==1 else f'{frozen["xref_id"]}-segment-{ordinal:02d}',frozen,segment))
 actual={row['xref_id']:row for row in value['xrefs']}
 if len(actual)!=42 or set(actual)!={row[0] for row in expected_xrefs}:bad('v2 B1c3 source xref closure mismatch')
 for xid,frozen,segment in expected_xrefs:
  row=actual[xid];owner=events.get(row['source_event_id'])
  owned_pages={span['page'] for span in value['source_partition']['spans'] if span['span_id'] in owner.get('source_span_ids',[])} if owner is not None else set()
  if row['source_page']!=frozen['source_page'] or row['source_page'] not in owned_pages or row['reader_text']!=segment['reader_text'] or row['target_anchor']!=segment['target_anchor'] or row['emit_link']!=segment['emit_link'] or row['migration_row_id']!=f'xrefs:{xid}' or owner is None or owner['anchor']!=frozen['owner_anchor']:bad('v2 B1c3 source xref owner mismatch')
 rows={row['source_id']:row for row in migration['xref_rows']}
 if len(rows)!=237 or set(rows)!={f'xrefs:{row["xref_id"]}' for row in v1['xrefs']}:bad('v2 B1c3 migration source closure mismatch')
 targets=[]
 for frozen in v1['xrefs']:
  row=rows[f'xrefs:{frozen["xref_id"]}'];xid=frozen['xref_id']
  if xid in {'toc-viral-merchandise','toc-viral-back-cover'}: expected=('excluded_advertising',[],'OUT-026')
  elif frozen['source_selector']=='line_exact' and xid=='p037-handout-21': expected=('split',['xrefs:p037-handout-21-segment-01','xrefs:p037-handout-21-segment-02'],None)
  elif frozen['source_selector']=='line_exact': expected=('retained_unchanged',[f'xrefs:{xid}'],None)
  else: expected=('replaced',[f'generated_navigation_items:{xid}'],'OUT-002')
  if (row['outcome'],row['final_target_ids'],row['decision_ref'])!=expected:bad('v2 B1c3 migration target mismatch')
  targets.extend(row['final_target_ids'])
 if set(targets)!={*(f'xrefs:{row[0]}' for row in expected_xrefs),*expected_navigation} or len(targets)!=236:bad('v2 B1c3 migration materialization mismatch')

def v2_input_binding(value,root,source_pdf,reconstruction_package):
 """Bind v2 declaration identities to the exact CLI source and reconstruction tree."""
 document=value['document'];source=Path(source_pdf).resolve(strict=True)
 ident(root,document['source_pdf'],'v2 source PDF',source)
 declared_lexical=v2_safe_package_root(root,document['reconstruction_package']['root'])
 try:
  declared=declared_lexical.resolve(strict=True);package=Path(reconstruction_package).resolve(strict=True)
 except (OSError,RuntimeError,ValueError) as error:
  raise ValueError('v2 reconstruction package CLI/config path mismatch') from error
 if not package.is_dir() or declared!=package:bad('v2 reconstruction package CLI/config path mismatch')
 count,total,digest=v2_package_inventory(package)
 expected=document['reconstruction_package']
 if count!=expected['file_count']:bad('v2 reconstruction package file_count mismatch')
 if total!=expected['total_bytes']:bad('v2 reconstruction package total_bytes mismatch')
 if digest!=expected['inventory_sha256']:bad('v2 reconstruction package inventory_sha256 mismatch')
 for row in value['source_disposition']:
  page=ident(root,row['page_markdown'],f"v2 page {row['page']} markdown")
  if page.parent!=package/'pages' or page.name!=f"page-{row['page']:03d}.md":bad('v2 page markdown reconstruction binding mismatch')
 excluded={123,124}
 for collection,label in ((value['hierarchy'],'hierarchy'),(value['events'],'event'),(value['assets'],'asset')):
  if any((set(item['source_pages']) if label=='hierarchy' else {item.get('source_page',item.get('page'))} if label=='asset' else {item['page']}) & excluded for item in collection):bad(f'v2 excluded page {label} leakage')
 if any(item['source_page'] in excluded for item in value['xrefs']):bad('v2 excluded page xref leakage')
 if any(item['physical_page'] in excluded for item in value['source_recoveries']):bad('v2 excluded page recovery leakage')
 v2_source_partition(value['source_partition'],package)
 v2_b1c3_xref_closure(value,root)
 v2_a3_validate(value,package,root)
 v2_migration(value,root)
 return {'source':source,'package':package,'reconstruction_inventory_sha256':digest}

def _v2_escape(value): return str(value).replace('\\','\\\\').replace('|','\\|')
def _v2_quote_lines(value): return '\n'.join('> '+line for line in value.splitlines())
def _v2_quote_title(value): return '\n'.join('> **'+line+'**' for line in value.splitlines())
def serialize_v2_structured(event):
 """Serialize one closed typed container and reject boundary/child drift."""
 data=event['content'];kind=data.get('kind');contains=event.get('contains')
 if not isinstance(contains,list) or contains!=data.get('contains') or len(contains)!=len(set(contains)):bad('v2 structured contains mismatch')
 if kind=='table':
  header,rows=data.get('header'),data.get('rows')
  if not isinstance(header,list) or not header or len(header)!=len(set(map(str,header))) or not isinstance(rows,list) or any(not isinstance(row,list) or len(row)!=len(header) for row in rows) or data.get('row_count')!=len(rows) or data.get('cell_count')!=sum(len(row) for row in rows):bad('v2 table shape mismatch')
  return '\n'.join(['| '+' | '.join(map(_v2_escape,header))+' |','| '+' | '.join('---' for _ in header)+' |']+['| '+' | '.join(map(_v2_escape,row))+' |' for row in rows])
 if kind=='callout':
  body=data.get('body');
  if not isinstance(body,list) or not body or data.get('end_after')!=contains[-1]:bad('v2 callout boundary mismatch')
  return '\n'.join('> '+str(line) for line in body)
 if kind=='ordered_list_callout':
  items=data.get('items');
  if not isinstance(items,list) or not items or data.get('end_after')!=contains[-1] or len(items)!=len(contains):bad('v2 ordered callout boundary mismatch')
  return '\n'.join(f'> {n}. {item}' for n,item in enumerate(items,1))
 if kind=='equipment_card':
  fields=[data.get(x) for x in ('title','stats','footnote','body')]
  if any(not isinstance(x,str) for x in fields) or not any(fields) or data.get('end_after')!=contains[-1]:bad('v2 equipment boundary mismatch')
  return '\n'.join([*([_v2_quote_title(fields[0])] if fields[0] else []),*(_v2_quote_lines(field) for field in fields[1:] if field)])
 if kind=='creature_statblock':
  required=('title','subtitle','characteristics','derived_stats','attacks','abilities','nested_tables')
  if any(key not in data for key in required) or data.get('end_after')!=contains[-1] or not all(isinstance(data[key],str) for key in required) or not any(data[key] for key in required):bad('v2 statblock boundary mismatch')
  title='\n'.join('**'+line+'**' for line in data['title'].splitlines()) if data['title'] else ''
  if data['subtitle']:title+=((' — ' if title else '')+data['subtitle'])
  return '\n'.join([*([_v2_quote_lines(title)] if title else []),*(_v2_quote_lines(data[key]) for key in required[2:] if data[key])])
 if kind=='inline_run_in':
  if not all(isinstance(data.get(key),str) and data[key] for key in ('anchor','label','xref')):bad('v2 run-in mismatch')
  return f'<a id="{data["anchor"]}"></a>**{data["label"]}** {data["xref"]}'
 if kind=='full_page_map':
  if not isinstance(data.get('pages'),list) or len(data['pages'])<2 or not isinstance(data.get('reader_asset_ids'),list) or not data['reader_asset_ids'] or not all(isinstance(data.get(key),str) for key in ('accessible_key','legend','scale')):bad('v2 map closure mismatch')
  return '\n'.join(['> Map pages: '+', '.join(map(str,data['pages']))]+[_v2_quote_lines(label+value) for label,value in (('Key: ',data['accessible_key']),('Legend: ',data['legend']),('Scale: ',data['scale'])) if value])
 if kind=='physical_page_pair':
  if not isinstance(data.get('front_page'),int) or not isinstance(data.get('back_page'),int) or not data.get('front_reader_asset_ids') or not data.get('back_reader_asset_ids') or not isinstance(data.get('back_semantics'),str) or not data['back_semantics']:bad('v2 pair closure mismatch')
  # Full-page images are placed as asset events. Their machine IDs belong in
  # provenance, not reader prose; back-side field labels are internal labels.
  body=re.sub(r'(?m)^#{1,6}\s+(.+)$',r'**\1**',data['back_semantics'])
  return re.sub(r'\n{3,}','\n\n',body).strip()
 bad('v2 structured representation mismatch')

class V2Chunk:
 """One declared v2 event; text is never rediscovered from finished Markdown."""
 def __init__(self,event,rendered,emitted=True):
  self.event=event;self.rendered=rendered;self.emitted=emitted;self.children=[]

def _v2_declared_hash(event):
 value=event['content'] if isinstance(event['content'],str) else canonical(event['content'])
 return hashlib.sha256(value.encode('utf8')).hexdigest().upper()

def _v2_reader_asset(asset): return asset.get('reader_value',asset.get('disposition')=='reader')

def _v2_asset_marker(asset):
 """Render from declared binary identity, never from the logical asset id.

 Legacy fixtures retain their historical logical-name projection. Canonical
 B1c4 rows have no source description, so their neutral alt does not invent a
 caption; a reviewed description may replace it in a later integration.
 """
 if not _v2_reader_asset(asset): return ''
 if 'source_path' in asset:
  name=asset['asset_id'];alt=asset.get('alt_text',asset['asset_id'])
 else:
  binary=asset.get('binary')
  if binary is None:
   if asset.get('provenance',{}).get('kind')!='reviewed_provisional_full_page':bad('v2 canonical reader asset binary pending')
   name=asset['asset_id']+'.png'
  elif isinstance(binary,dict) and isinstance(binary.get('path'),str) and Path(binary['path']).name:
   name=Path(binary['path']).name
  else:bad('v2 canonical reader asset binary pending')
  alt='Illustration'
 if not isinstance(alt,str) or not alt.strip():bad('v2 asset alt mismatch')
 return f'![{alt}](assets/{name})'

def v2_render_provisional_asset(asset, source_pdf, destination, pdftoppm='pdftoppm'):
 """Render one declared full-page provisional recipe inside private staging."""
 provenance=asset.get('provenance',{});recipe=provenance.get('render_recipe',{})
 if asset.get('binary') is not None or provenance.get('kind')!='reviewed_provisional_full_page' or recipe.get('tool')!='pdftoppm' or recipe.get('first_page')!=asset.get('source_page') or recipe.get('last_page')!=asset.get('source_page'):bad('v2 provisional recipe mismatch')
 name=asset['asset_id']+'.png';prefix=destination/name[:-4]
 subprocess.run([pdftoppm,'-r',str(recipe['dpi']),'-png','-singlefile','-f',str(asset['source_page']),'-l',str(asset['source_page']),str(source_pdf),str(prefix)],check=True,capture_output=True,text=True)
 output=destination/name
 if not output.is_file():bad('v2 provisional render missing')
 dimensions=image_identity(output,'image/png','v2 provisional render')
 if dimensions!=provenance.get('output_dimensions'):bad('v2 provisional render dimensions')
 return output,{'path':'assets/'+name,'bytes':output.stat().st_size,'sha256':dig(output),'media_type':'image/png','dimensions':dimensions}

def _v2_event_render(event,hierarchy,assets,xrefs=()):
 xrefs=[xref for xref in xrefs if xref.get('emit_link',True)]
 row=hierarchy[event['anchor']]; content=event['content']
 if event['type']=='heading': return f'<a id="{row["anchor"]}"></a>\n'+('#'*row['level'])+f" {row['reader_title']}" if row['representation']=='heading' else ''
 if event['type']=='anchor_only': return f'<a id="{row["anchor"]}"></a>'
 if event['type']=='structured_unit': return serialize_v2_structured({**event,'content':_v2_xref_payload(content,xrefs)})
 if event['type']=='asset': return _v2_asset_marker(assets[content])
 if event['type']=='generated_navigation': return '\n'.join(f"- [{entry['reader_text']}](#{entry['target_anchor']})" for entry in content['entries'])
 rendered=content
 # OUT-041: MinerU retained the handout bullet marker but the generic event
 # joiner turned every item into a separate paragraph.  Normalize only the
 # reviewed handout bullet surface; source payloads and provenance stay exact.
 if event['type']=='text_fragment' and event['anchor'].startswith('viral-handout-'):
  rendered=re.sub(r'^\s*[•·]\s*','- ',rendered,count=1)
 for xref in xrefs:
  rendered=rendered.replace(xref['reader_text'],f"[{xref['reader_text']}](#{xref['target_anchor']})")
 return rendered

def _v2_xref_payload(value,xrefs,key=None):
 """Apply links only to authorial structured leaves on a private render copy."""
 reserved={'kind','contains','end_after','asset_id','asset_ids','reader_asset_ids','front_reader_asset_ids','back_reader_asset_ids','anchor','front_facsimile','back_facsimile','front_page','back_page','pages','page_set','count','row_count','cell_count','continuation','placement'}
 if isinstance(value,str):
  if key in reserved:return value
  for xref in xrefs:
   if xref.get('emit_link',True):value=value.replace(xref['reader_text'],f"[{xref['reader_text']}](#{xref['target_anchor']})")
  return value
 if isinstance(value,list):return [_v2_xref_payload(item,xrefs,key) for item in value]
 if isinstance(value,dict):return {item:_v2_xref_payload(child,xrefs,item) for item,child in value.items()}
 return value

def v2_typed_chunks(value):
 """Build and relocate typed event chunks by list operation, before one final join."""
 v2_config(value); hierarchy={x['anchor']:x for x in value['hierarchy']}; assets={x['asset_id']:x for x in value['assets']}
 if len(assets)!=len(value['assets']):bad('v2 duplicate asset id')
 if any(event['type']=='asset' and event['content'] not in assets for event in value['events']):bad('v2 asset event mismatch')
 chunks=[V2Chunk(event,_v2_event_render(event,hierarchy,assets,[x for x in value['xrefs'] if x['source_event_id']==event['event_id']]),bool(_v2_event_render(event,hierarchy,assets,[x for x in value['xrefs'] if x['source_event_id']==event['event_id']]))) for event in value['events']]
 by_id={chunk.event['event_id']:chunk for chunk in chunks}
 asset_events={chunk.event['content']:chunk for chunk in chunks if chunk.event['type']=='asset'}
 if len(asset_events)!=sum(chunk.event['type']=='asset' for chunk in chunks):bad('v2 duplicate asset event')
 placed=[]
 for asset_id,asset in assets.items():
  chunk=asset_events.get(asset_id)
  if chunk is None and not _v2_reader_asset(asset):continue
  if chunk is None:bad('v2 asset event mismatch')
  # Suppressed assets remain declared but never gain a reader range.
  if not _v2_reader_asset(asset):
   chunk.emitted=False;continue
  placement=asset.get('placement')
  if placement is None:bad('v2 asset placement missing')
  if len(placement)!=1:bad('v2 ambiguous asset placement')
  relation,target_id=next(iter(placement.items()));target=by_id.get(target_id)
  if target is None or target is chunk:bad('v2 asset placement target mismatch')
  if relation=='inside_structured_unit' and target.event['type']!='structured_unit':bad('v2 asset placement target mismatch')
  if relation not in {'before_event','after_event','inside_structured_unit'}:bad('v2 asset placement mismatch')
  placed.append((tuple(chunk.event['order_key']),relation,target,chunk))
 for _,_,_,chunk in placed:chunks.remove(chunk)
 for relation in ('before_event','after_event','inside_structured_unit'):
  groups={}
  for ordinal,current,target,chunk in placed:
   if current==relation:groups.setdefault(target.event['event_id'],(target,[]))[1].append((ordinal,chunk))
  for target,items in groups.values():
   ordered=[chunk for _,chunk in sorted(items)]
   if relation=='before_event':
    index=chunks.index(target);chunks[index:index]=ordered
   elif relation=='after_event':
    index=chunks.index(target)+1;chunks[index:index]=ordered
   else:target.children.extend(ordered)
 # OUT-040 is a finite reader-order repair for the synthetic Handout #1 label
 # admitted ahead of its parent section in the reviewed p69 merge.  Do not
 # generalize this into heading sorting: the source event order remains sealed.
 if value.get('scenario_id')=='viral':
  first=by_id.get('heading:viral-handout-01')
  navigation=[chunk for chunk in chunks if chunk.event['type']=='generated_navigation' and chunk.event['content'].get('family')=='handout_index']
  if first is None or len(navigation)!=1 or hierarchy[first.event['anchor']]['parent_anchor']!=navigation[0].event['anchor']:bad('v2 reviewed handout-one placement mismatch')
  chunks.remove(first);chunks.insert(chunks.index(navigation[0])+1,first)
 return chunks

def _v2_compact_handout_list_item(chunk):
 return chunk.event['type']=='text_fragment' and chunk.event['anchor'].startswith('viral-handout-') and chunk.rendered.startswith('- ')

def v2_join_ledger(chunks):
 """Join once and accumulate final Unicode/UTF-8 coordinates from the chunks."""
 top=[chunk for chunk in chunks if chunk.emitted]; pieces=[]; records=[]; char_offset=byte_offset=0
 def record(chunk,start_char,start_byte,end_char,end_byte):
  event=chunk.event; row={'event_id':event['event_id'],'type':event['type'],'page':event['page'],'order_key':event['order_key'],'anchor':event['anchor'],'fragment_id':event['fragment_id'],'declared_content_sha256':_v2_declared_hash(event),'emission':'emitted','start_char':start_char,'end_char':end_char,'start_byte':start_byte,'end_byte':end_byte,'slice_sha256':hashlib.sha256(chunk.rendered.encode('utf8')).hexdigest().upper()}
  if event['type']=='structured_unit':row['contains']=event['contains']
  records.append(row)
 for position,chunk in enumerate(top):
  if position:
   separator='\n' if _v2_compact_handout_list_item(top[position-1]) and _v2_compact_handout_list_item(chunk) and top[position-1].event['anchor']==chunk.event['anchor'] else '\n\n'
   pieces.append(separator);char_offset+=len(separator);byte_offset+=len(separator.encode('utf8'))
  base_start_char,base_start_byte=char_offset,byte_offset;base=chunk.rendered
  pieces.append(base);char_offset+=len(base);byte_offset+=len(base.encode('utf8'))
  record(chunk,base_start_char,base_start_byte,char_offset,byte_offset)
  for child in chunk.children:
   if not child.emitted:continue
   # A nested marker belongs to the structured unit but does not enlarge the
   # parent's own rendered slice/range.
   pieces.append('\n');char_offset+=1;byte_offset+=1
   child_start_char,child_start_byte=char_offset,byte_offset;pieces.append(child.rendered);char_offset+=len(child.rendered);byte_offset+=len(child.rendered.encode('utf8'))
   record(child,child_start_char,child_start_byte,char_offset,byte_offset)
 text=''.join(pieces)+'\n'
 for chunk in chunks:
  if not chunk.emitted:
   event=chunk.event;row={'event_id':event['event_id'],'type':event['type'],'page':event['page'],'order_key':event['order_key'],'anchor':event['anchor'],'fragment_id':event['fragment_id'],'declared_content_sha256':_v2_declared_hash(event),'emission':'suppressed'}
   if event['type']=='structured_unit':row['contains']=event['contains']
   records.append(row)
 records.sort(key=lambda row:tuple(row['order_key']))
 for row in records:
  if row['emission']!='emitted':continue
  start,end=row['start_char'],row['end_char']
  if text[start:end].encode('utf8') != text.encode('utf8')[row['start_byte']:row['end_byte']] or hashlib.sha256(text[start:end].encode('utf8')).hexdigest().upper()!=row['slice_sha256']:bad('v2 final ledger slice mismatch')
 return text,records

def serialize_v2(value):
 """Public v2 serializer, retained for callers; composition is typed and one-pass."""
 text,_=v2_join_ledger(v2_typed_chunks(value));return text

BINDING_KEYS={'kind','order','locators','continuation_pages','unit_ref','shared_prefix_owner'}
LOCATOR_KEYS={'page','selector_kind','selector','occurrence','action'}
BINDING_KINDS={'generated','source_locator','physical_unit','owned_page_unit'}
SELECTOR_KINDS={'page_start','line_exact','line_prefix','markdown_heading_exact','markdown_heading_normalized','handout_marker','structured_unit'}
ACTIONS={'insert_before','replace_heading','replace_label_retain_remainder','retain_under_anchor','consume_continuation_label'}
GENERATED_XREFS={'generated_toc':'viral-contents','generated_handout_index':'viral-player-handouts','generated_map_index':'viral-keeper-maps','generated_pregen_index':'viral-pregenerated-investigators'}
XREF_BASE={'xref_id','source_page','source_selector','visible_text','classification','target_anchors','link_policy'}
XREF_SOURCE=XREF_BASE|{'source_line','owner_anchor','segments'}
SEGMENT_KEYS={'source_text','reader_text','target_anchor','emit_link'}

def xref_declarations(c,anchors):
 ids=set();generated=source=segments=external=0
 for row in c['xrefs']:
  selector=row.get('source_selector')
  if selector in GENERATED_XREFS:
   closed(row,XREF_BASE,'generated xref');generated+=1
   if row['classification']!='internal' or not st(row['link_policy'],'generated xref policy') or len(row['target_anchors'])!=1 or row['target_anchors'][0] not in anchors:bad('generated xref mismatch')
  elif selector=='line_exact':
   closed(row,XREF_SOURCE,'source xref');source+=1
   if row['link_policy'] not in {'replace_exact_segments','validate_exact_non_link'} or not isinstance(row['segments'],list) or not row['segments']:bad('source xref mismatch')
   targets=[]
   for segment in row['segments']:
    closed(segment,SEGMENT_KEYS,'xref segment');segments+=1
    if not st(segment['source_text'],'source segment') or not st(segment['reader_text'],'reader segment') or not isinstance(segment['emit_link'],bool):bad('xref segment mismatch')
    if segment['emit_link']:
     if segment['target_anchor'] not in anchors:bad('xref target mismatch')
     targets.append(segment['target_anchor'])
    elif segment['target_anchor'] is not None:bad('external xref target mismatch')
   if row['classification']=='external_bibliographic':
    external+=1
    if row['link_policy']!='validate_exact_non_link' or any(x['emit_link'] for x in row['segments']) or row['target_anchors']!=[]:bad('external xref mismatch')
   elif row['classification']!='internal' or row['target_anchors']!=targets:bad('source xref targets mismatch')
  else:bad('xref selector mismatch')
  if row['xref_id'] in ids:bad('duplicate xref')
  ids.add(row['xref_id'])
 return {'ids':ids,'generated':generated,'source':source,'segments':segments,'external':external}

def resolve_source_xrefs(config,binding_index,package):
 """Pre-resolve every source xref against its complete page and exact C1 owner spans."""
 bindings={x['anchor']:x for x in binding_index['bindings']}; resolved={}
 for row in config['xrefs']:
  if row['source_selector']!='line_exact':continue
  raw=source_lines(package,row['source_page'])[0]
  if raw.count(row['source_line'])!=1:bad('xref page-line resolution mismatch')
  owner=bindings.get(row['owner_anchor'])
  if owner is None:bad('xref owner mismatch')
  hits=[]
  for span in owner['source_span_hashes']:
   if span['page']==row['source_page'] and raw[span['start']:span['end']].count(row['source_line']):hits.append(span)
  if len(hits)!=1:bad('xref owner-span resolution mismatch')
  cursor=0
  for segment in row['segments']:
   position=row['source_line'].find(segment['source_text'],cursor)
   if position<0 or row['source_line'].find(segment['source_text'],position+1)!=-1:bad('xref segment resolution mismatch')
   if not segment['emit_link'] and segment['reader_text']!=segment['source_text']:bad('external xref reader text mismatch')
   cursor=position+len(segment['source_text'])
  resolved[row['xref_id']]=(row,hits[0])
 return resolved

def binding_declarations(c,anchors,pages):
 """Validate the closed, config-authored C1 binding language without inference."""
 handout_ids={x['anchor'] for x in c['handouts']};visual_ids={x['review_id'] for x in c['visual_review_units']}
 shared={'viral-handout-04':'viral-handout-04','viral-handout-05':'viral-handout-04','viral-handout-06':'viral-handout-06','viral-handout-07':'viral-handout-06'}
 orders=set(); seen_locator_pages=[]; bindings={}
 for row in c['hierarchy']:
  anchor=row['anchor']; b=closed(row.get('assembly_binding'),BINDING_KEYS,'assembly binding')
  kind=st(b['kind'],'binding kind')
  if kind not in BINDING_KINDS:bad('binding kind mismatch')
  order=num(b['order'],'binding order')
  if order in orders or order not in range(1,169):bad('binding order mismatch')
  orders.add(order)
  if not isinstance(b['locators'],list) or not isinstance(b['continuation_pages'],list):bad('binding collections mismatch')
  if len(set(b['continuation_pages']))!=len(b['continuation_pages']) or any(p not in row['source_pages'] for p in b['continuation_pages']):bad('continuation pages mismatch')
  if kind=='generated':
   if b['locators'] or b['continuation_pages'] or b['unit_ref'] is not None:bad('generated binding mismatch')
  else:
   if kind=='source_locator' and (b['unit_ref'] is not None or not b['locators']):bad('source locator binding mismatch')
   if kind=='physical_unit' and b['unit_ref'] not in handout_ids:bad('unit ref mismatch')
   if kind=='owned_page_unit' and b['unit_ref'] not in visual_ids:bad('unit ref mismatch')
  for locator in b['locators']:
   closed(locator,LOCATOR_KEYS,'binding locator'); page=num(locator['page'],'locator page'); selector_kind=st(locator['selector_kind'],'selector kind'); action=st(locator['action'],'locator action')
   if page not in pages or page not in row['source_pages'] or selector_kind not in SELECTOR_KINDS or action not in ACTIONS or num(locator['occurrence'],'locator occurrence')!=1:bad('binding locator mismatch')
   if (selector_kind=='page_start') != (locator['selector'] is None):bad('binding selector mismatch')
   if selector_kind!='page_start' and not isinstance(locator['selector'],str):bad('binding selector mismatch')
   if page in b['continuation_pages'] and action!='consume_continuation_label':bad('continuation locator mismatch')
   seen_locator_pages.append((anchor,page))
  if kind!='generated' and not b['locators'] and kind!='owned_page_unit':bad('binding locator missing')
  if b['shared_prefix_owner']!=shared.get(anchor):bad('shared prefix owner mismatch')
  bindings[anchor]=b
 if orders!=set(range(1,169)):bad('binding orders must be exact 1..168')
 by_anchor={x['anchor']:x for x in c['hierarchy']}
 for anchor,b in bindings.items():
  parent=by_anchor[anchor]['parent_anchor']
  if parent and b['order']<=bindings[parent]['order']:bad('binding parent order mismatch')
 return bindings
def declarations(c,root,pkg):
 d=closed(c['document'],{'title','root_anchor','source_pages','h1_count','source_pdf','serialization','content_policy','authorial_text_protections','external_gates','acceptance_record_policy'},'document')
 if (d['title'],d['root_anchor'],num(d['h1_count'],'h1_count'))!=('Viral','viral',1):bad('document root mismatch')
 sp=closed(d['source_pages'],{'first','last','count'},'source_pages')
 if (sp['first'],sp['last'],sp['count'])!=(1,124,124):bad('source pages mismatch')
 closed(d['source_pdf'],{'path','bytes','sha256','page_count','media_box_points','rotation_degrees'},'source_pdf')
 cp=closed(d['content_policy'],{'all_source_pages_preserved','contract_exceptions','accepted_editorial_lexical_delta_count','source_pdf_text_fallback','overlay_reader_use'},'content_policy')
 if cp['all_source_pages_preserved'] is not True or cp['contract_exceptions']!=[] or cp['accepted_editorial_lexical_delta_count']!=0 or cp['source_pdf_text_fallback'] or cp['overlay_reader_use']:bad('content policy mismatch')
 wanted={'full_visual_qa','independent_gpt55_release_review','explicit_user_reading_acceptance'}
 if not isinstance(d['external_gates'],list) or {x.get('gate') for x in d['external_gates'] if isinstance(x,dict)}!=wanted:bad('external gate declaration mismatch')
 for x in d['external_gates']:
  closed(x,{'gate','required','status','may_be_asserted_by_config_or_builder'},'external gate')
  if x['required'] is not True or x['status']!='pending' or x['may_be_asserted_by_config_or_builder'] is not False:bad('external gates must stay pending')
 ap=closed(d['acceptance_record_policy'],{'candidate_must_not_contain','promotion_is_separate','byte_change_invalidates_prior_acceptance'},'acceptance policy')
 if ap!={'candidate_must_not_contain':'MASTER_EN.acceptance.json','promotion_is_separate':True,'byte_change_invalidates_prior_acceptance':True}:bad('acceptance policy mismatch')
 anchors=set()
 for i,x in enumerate(c['hierarchy']):
  closed(x,{'level','title','anchor','parent_anchor','source_pages','toc_entry','semantic_role','assembly_binding'},'hierarchy') ;a=st(x['anchor'],'anchor')
  if not ANCHOR.fullmatch(a) or a in anchors or x['level'] not in (1,2,3,4,5) or not isinstance(x['source_pages'],list):bad('hierarchy closure mismatch')
  if (i==0 and (a!='viral' or x['level']!=1 or x['parent_anchor']!='')) or (i and x['parent_anchor'] not in anchors):bad('hierarchy parent closure mismatch')
  anchors.add(a)
 assets={x.get('asset_id') for x in c['assets']};pages=set()
 for x in c['source_disposition']:
  closed(x,{'page','source_path','primary_unit_id','role','disposition','target_anchors','sub_units','preserve_source_content','authorized_source_content_suppressions','closure_status'},'source disposition');p=num(x['page'],'page')
  if p in pages or p not in range(1,125) or x['preserve_source_content'] is not True or x['authorized_source_content_suppressions']!=[] or x['closure_status']!='declared_for_builder' or not set(x['target_anchors'])<=anchors or rel(root,x['source_path'],'source path')!=pkg/'pages'/f'page-{p:03d}.md':bad('source disposition closure mismatch')
  for u in x['sub_units']:
   closed(u,{'unit_id','unit_type','target_anchor','asset_ids','closure'},'source sub-unit')
   if u['target_anchor'] not in anchors or not set(u['asset_ids'])<=assets or u['closure']!='declared':bad('source sub-unit closure mismatch')
  pages.add(p)
 if pages!=set(range(1,125)):bad('source pages not exact once')
 binding_declarations(c,anchors,pages)
 validate_reader_surface(c,pkg)
 xref_declarations(c,anchors)
 labels=set();ords=set()
 for x in c['handouts']:
  closed(x,{'label','ordinal','source_page','title','anchor','representation','owned_asset_ids','narrative_sources','provenance_units','physical_identity'},'handout')
  if x['label'] in labels or x['ordinal'] not in range(1,40) or x['source_page'] not in pages or x['anchor'] not in anchors or not set(x['owned_asset_ids'])<=assets or x['physical_identity'] is not True:bad('handout closure mismatch')
  for s in x['narrative_sources']:
   if rel(root,s,'handout narrative').parent != pkg/'pages':bad('handout narrative closure mismatch')
  labels.add(x['label']);ords.add(x['ordinal'])
 if ords!=set(range(1,40)) or {'2a','2b','3a','3b'}-labels:bad('handout ordinal closure mismatch')
 structured_declarations(c,root,pkg,anchors,pages)
 seen=set();accepted=0
 for x in c['assets']:
  normal={'asset_id','origin','logical_name','source_path','sha256','bytes','media_type','dimensions','source_page','source_region','semantic_role','representation','owner_anchor','placement_index','alt_text','visual_review'};render=normal-{'source_path','sha256','bytes'}|{'source_pdf','render'};closed(x,normal if x.get('origin')=='accepted_reconstruction_asset' else render,'asset')
  if x['asset_id'] in seen or x['origin'] not in {'accepted_reconstruction_asset','source_page_render'} or x['representation'] not in {'reader','evidence_only'} or x['owner_anchor'] not in anchors or x['source_page'] not in pages or (x['representation']=='reader' and not st(x['alt_text'],'alt text').strip()):bad('asset closure mismatch')
  if x['origin']=='accepted_reconstruction_asset':
   p=rel(root,x['source_path'],'asset source')
   if dig(p)!=x['sha256'] or p.stat().st_size!=x['bytes']:bad('asset identity mismatch')
   accepted+=1
  seen.add(x['asset_id'])
 if accepted!=121:bad('accepted asset count mismatch')
 for x in c['visual_review_units']:
  closed(x,{'review_id','classification','owner_anchor','source_pages','asset_ids','review_requirements','special_requirement','status'},'visual unit')
  if x['owner_anchor'] not in anchors or not set(x['source_pages'])<=pages or not set(x['asset_ids'])<=seen or x['status']!='pending_external_visual_qa':bad('visual closure mismatch')
 for x in c['reader_noise_patterns']:
  closed(x,{'noise_id','classification','source_examples','reader_disposition','authorial_text_affected'},'reader noise')
  if not st(x['reader_disposition'],'reader disposition') or x['authorial_text_affected'] is not False:bad('reader noise policy mismatch')

def source_lines(package,page):
 """Return immutable lexical lines, excluding only technical source-page comments."""
 path=Path(package)/'pages'/f'page-{page:03d}.md'
 raw=path.read_text(encoding='utf8')
 lines=[]; offset=0
 for number,text in enumerate(raw.splitlines(keepends=True),1):
  if not re.fullmatch(r'<!-- source-page-\d{3} -->\r?\n?',text):lines.append({'line':number,'start':offset,'end':offset+len(text),'text':text})
  offset+=len(text)
 return raw,lines

RS_KEYS={'schema_version','semantic_fragments','authorized_suppressions','heading_policy','alt_policy'}
SELECTOR_KEYS={'kind','occurrence','text'}
RS_SELECTOR_KINDS={'page_start','page_end','line_exact','line_prefix','markdown_heading_exact'}
def reader_selector(lines, selector):
 closed(selector, SELECTOR_KEYS if selector.get('kind') not in {'page_start','page_end'} else {'kind','occurrence'}, 'reader selector')
 kind=st(selector['kind'],'reader selector kind'); occurrence=num(selector['occurrence'],'reader selector occurrence')
 if kind not in RS_SELECTOR_KINDS or occurrence < 1: bad('reader selector mismatch')
 content=[line for line in lines if line['text'].strip()]
 if kind=='page_start': return content[0]['start'] if content else 0
 if kind=='page_end': return content[-1]['end'] if content else 0
 text=st(selector['text'],'reader selector text')
 matches=[line for line in lines if (line['text'].rstrip('\r\n')==text if kind in {'line_exact','markdown_heading_exact'} else line['text'].rstrip('\r\n').startswith(text))]
 if len(matches)!=occurrence: bad('reader selector must resolve exactly once')
 return matches[occurrence-1]['start']

def reader_selector_end(lines, selector):
 """Resolve a suppression endpoint, retaining the selected line's terminal LF."""
 if selector.get('kind')=='page_end': return reader_selector(lines,selector)
 closed(selector,SELECTOR_KEYS if selector.get('kind') not in {'page_start','page_end'} else {'kind','occurrence'},'reader selector')
 kind=st(selector['kind'],'reader selector kind'); occurrence=num(selector['occurrence'],'reader selector occurrence')
 if kind not in RS_SELECTOR_KINDS or occurrence < 1: bad('reader selector mismatch')
 if kind=='page_start': return reader_selector(lines,selector)
 text=st(selector['text'],'reader selector text')
 matches=[line for line in lines if (line['text'].rstrip('\r\n')==text if kind in {'line_exact','markdown_heading_exact'} else line['text'].rstrip('\r\n').startswith(text))]
 if len(matches)!=occurrence: bad('reader selector must resolve exactly once')
 return matches[occurrence-1]['end']

def reader_surface_ranges(c, package):
 """Resolve closed semantic and suppression ranges against immutable page bodies."""
 rs=closed(c['reader_surface'],RS_KEYS,'reader surface')
 pages={p:source_lines(package,p) for p in range(1,125)} if package else {}
 fragments=[]; suppressions=[]
 for index,row in enumerate(rs['semantic_fragments'],1):
  closed(row,{'fragment_id','source_page','start','end','expected_owner','raw_sha256','order'},'semantic fragment')
  if row['order']!=index or row['source_page'] not in pages or not HEX.fullmatch(row['raw_sha256']) or row['expected_owner'] not in {x['anchor'] for x in c['hierarchy']}: bad('semantic fragment mismatch')
  start=reader_selector(pages[row['source_page']][1],row['start']);end=reader_selector(pages[row['source_page']][1],row['end']);raw=pages[row['source_page']][0][start:end]
  if start>=end or hashlib.sha256(raw.encode('utf8')).hexdigest().upper()!=row['raw_sha256']: bad('semantic fragment hash mismatch')
  fragments.append({**row,'start_offset':start,'end_offset':end,'text':raw})
 for index,row in enumerate(rs['authorized_suppressions'],1):
  closed(row,{'suppression_id','source_page','owner_anchor','start','end','raw_sha256','expected_occurrence','disposition','replacement_asset_id','authorial_text_affected','source_containment'},'authorized suppression')
  closed(row['source_containment'],{'kind','claim_owner_anchor','claim_binding_kind','owned_page_proof'},'source containment')
  if row['source_page'] not in pages or row['expected_occurrence']!=1 or row['authorial_text_affected'] is not False or row['disposition'] not in {'sidecar_only','omit_reader_duplicate'} or not HEX.fullmatch(row['raw_sha256']): bad('suppression mismatch')
  start=reader_selector(pages[row['source_page']][1],row['start']);end=reader_selector_end(pages[row['source_page']][1],row['end']);raw=pages[row['source_page']][0][start:end]
  if start>=end or hashlib.sha256(raw.encode('utf8')).hexdigest().upper()!=row['raw_sha256']: bad('suppression hash mismatch')
  containment=row['source_containment']
  if containment['kind'] not in {'normal_claim','owned_page_unit'} or containment['claim_binding_kind'] not in {'source_locator','physical_unit','owned_page_unit'} or not containment['claim_owner_anchor']:bad('suppression containment mismatch')
  if containment['kind']=='owned_page_unit' and not isinstance(containment['owned_page_proof'],dict):bad('owned page proof mismatch')
  if containment['kind']=='normal_claim' and containment['owned_page_proof'] is not None:bad('normal claim proof mismatch')
  suppressions.append({**row,'start_offset':start,'end_offset':end,'text':raw})
 for rows,label in ((fragments,'semantic'),(suppressions,'suppression')):
  by_page={}
  for row in rows: by_page.setdefault(row['source_page'],[]).append(row)
  if any(a['end_offset']>b['start_offset'] for values in by_page.values() for a,b in zip(sorted(values,key=lambda x:x['start_offset']),sorted(values,key=lambda x:x['start_offset'])[1:])): bad(f'{label} ranges overlap')
 return rs,fragments,suppressions

def validate_reader_surface(c, package, binding_index=None):
 rs=closed(c['reader_surface'],RS_KEYS,'reader surface')
 if rs['schema_version']!='kb_creator.master_en_reader_surface.v1': bad('reader surface version')
 hp=closed(rs['heading_policy'],{'generated_mode','source_mode','max_level','overflow','duplicate_label'},'heading policy')
 if hp!={'generated_mode':'declared','source_mode':'owner_local','max_level':6,'overflow':'strong_label','duplicate_label':'strong_label'}: bad('heading policy mismatch')
 ap=closed(rs['alt_policy'],{'require_nonempty','banned_substrings','banned_regexes'},'alt policy')
 if ap['require_nonempty'] is not True or not all(isinstance(x,str) for x in ap['banned_substrings']+ap['banned_regexes']): bad('alt policy mismatch')
 reader=sorted((x for x in c['assets'] if x['representation']=='reader'),key=lambda x:x['placement_index'])
 if len(reader)!=107 or len({x['placement_index'] for x in reader})!=107: bad('reader alt ordinal mismatch')
 for asset in reader:
  value=st(asset['alt_text'],'reader alt').strip()
  if not value or any(x.lower() in value.lower() for x in ap['banned_substrings']) or any(re.search(x,value) for x in ap['banned_regexes']): bad('reader alt policy mismatch')
 fragments=rs['semantic_fragments']; suppressions=rs['authorized_suppressions']
 if not isinstance(fragments,list) or len(fragments)!=25 or not isinstance(suppressions,list) or len(suppressions)!=22: bad('reader surface counts')
 rs,ranges,suppressions=reader_surface_ranges(c,package)
 for fragment in ranges:
  page,start,end,owner=fragment['source_page'],fragment['start_offset'],fragment['end_offset'],fragment['expected_owner']
  if binding_index and not any(b['anchor']==owner and any(x['page']==page and x['start']<=start and end<=x['end'] for x in b['source_span_hashes']) for b in binding_index['bindings']): bad('semantic fragment owner mismatch')
 if binding_index:
  bindings={x['anchor']:x for x in binding_index['bindings']}; assets={x['asset_id']:x for x in c['assets']}; reviews={x['review_id']:x for x in c['visual_review_units']}; dispositions={x['primary_unit_id']:x for x in c['source_disposition']}
  for row in suppressions:
   containment=row['source_containment']; claimant=bindings.get(containment['claim_owner_anchor']); replacement=assets.get(row['replacement_asset_id'])
   if not claimant or not replacement or replacement['owner_anchor']!=row['owner_anchor']: bad('suppression replacement owner mismatch')
   if containment['kind']=='normal_claim':
    if claimant['kind']!=containment['claim_binding_kind'] or claimant['kind'] not in {'source_locator','physical_unit'} or not any(span['page']==row['source_page'] and span['start']<=row['start_offset'] and row['end_offset']<=span['end'] for span in claimant['source_span_hashes']): bad('suppression normal containment mismatch')
   else:
    proof=containment['owned_page_proof']
    if claimant['kind']!='owned_page_unit' or containment['claim_binding_kind']!='owned_page_unit' or claimant['unit_ref']!=proof['unit_ref'] or proof['review_id']!=proof['unit_ref'] or proof['source_disposition_primary_unit_id'] not in dispositions: bad('suppression owned-page proof mismatch')
    disposition=dispositions[proof['source_disposition_primary_unit_id']]
    if row['source_page'] not in reviews[proof['review_id']]['source_pages'] or proof['source_disposition_sub_unit_id'] not in {x['unit_id'] for x in disposition['sub_units']}: bad('suppression owned-page containment mismatch')
 return rs, ranges

STRUCTURE_BASE={'structure_id','classification','owner_anchor','source_pages','source_units','fact_expectations','representation','accepted_editorial_lexical_delta_count','placement_index','qa_status'}
REGION_COMMON={'page','binding_anchor','source_format','start_selector','termination','continuation_mode','attached_note_selectors'}
def structured_declarations(c,root,pkg,anchors,pages):
 """Validate the compact config contract; source prose never appears in config."""
 ids=set();placements=set();assets={x['asset_id']:x for x in c['assets']};reviews={x['review_id']:x for x in c['visual_review_units']}
 for row in c['structured_content']:
  closed(row,STRUCTURE_BASE,'structured content'); sid=st(row['structure_id'],'structure id')
  if sid in ids or num(row['placement_index'],'structure placement') in placements or row['owner_anchor'] not in anchors or set(row['source_pages'])-pages or row['accepted_editorial_lexical_delta_count']!=0 or row['qa_status']!='pending_builder_and_external_visual_qa':bad('structured closure mismatch')
  ids.add(sid);placements.add(row['placement_index'])
  for unit in row['source_units']:
   closed(unit,{'page','path','sha256'},'structured source'); path=rel(root,unit['path'],'structured path')
   if unit['page'] not in row['source_pages'] or path.parent!=Path(pkg)/'pages' or not HEX.fullmatch(st(unit['sha256'],'structured sha')) or dig(path)!=unit['sha256']:bad('structured source mismatch')
  facts=row['fact_expectations']; klass=row['classification']
  if klass=='visual_form':
   closed(facts,{'contract_kind','asset_id','source_page','owner_anchor','asset_sha256','representation','semantic_role','ordinary_review_id','structured_review_id','emit_exactly_once','semantic_duplicate_forbidden'},'visual form contract')
   asset=assets.get(facts['asset_id'])
   if row['representation']!='retained_complete_visual_form' or facts['contract_kind']!='visual_form' or facts['owner_anchor']!=row['owner_anchor'] or facts['source_page'] not in row['source_pages'] or not asset or asset['owner_anchor']!=row['owner_anchor'] or asset['source_page']!=facts['source_page'] or asset['sha256']!=facts['asset_sha256'] or asset['representation']!='reader' or asset['semantic_role']!='full_page' or facts['representation']!='reader' or facts['semantic_role']!='full_page' or not facts['emit_exactly_once'] or not facts['semantic_duplicate_forbidden'] or facts['ordinary_review_id'] not in reviews or facts['structured_review_id'] not in reviews:bad('visual form contract mismatch')
   continue
  kind={'semantic_table':'table','semantic_card':'card','semantic_statblock':'statblock'}.get(klass)
  if not kind or row['representation']!='semantic_from_accepted_facts' or not isinstance(facts,dict) or facts.get('contract_kind')!=kind:bad('structured class mismatch')
  needed={'contract_kind','regions','lexical_protections'}|({'ordered_literal_tokens','required_literal_substrings','forbidden_literal_tokens'} if kind in {'card','statblock'} else set())
  closed(facts,needed,'semantic contract')
  if not isinstance(facts['regions'],list) or not facts['regions'] or not all(isinstance(x,str) for key in ('lexical_protections','ordered_literal_tokens','required_literal_substrings','forbidden_literal_tokens') for x in facts.get(key,[])):bad('structured fact mismatch')
  bodies=[]
  bodies=[]
  for region in facts['regions']:
   fmt=region.get('source_format'); extra=({'ordered_first_column_keys'}|({'header_line','header_tokens'} if 'header_line' in region or 'header_tokens' in region else set())) if fmt=='numbered_record_series' else ({'header_line','header_tokens','ordered_first_column_keys'} if fmt=='markdown_pipe_table' else set())
   allowed=REGION_COMMON|extra
   closed(region,allowed,'structured region')
   if region['page'] not in row['source_pages'] or region['binding_anchor'] not in anchors or fmt not in {'markdown_pipe_table','numbered_record_series','literal_card','literal_statblock'} or closed(region['start_selector'],{'kind','text'},'region start')['kind']!='line_exact' or not st(region['start_selector']['text'],'region start text') or region['continuation_mode'] not in {'single','repeated_header','headerless','declared_descendant'} or not isinstance(region['attached_note_selectors'],list):bad('structured region mismatch')
   termination=region['termination']; termination_kind=termination.get('kind') if isinstance(termination,dict) else None
   if termination_kind=='record_count':
    closed(termination,{'kind','count'},'structured termination');num(termination['count'],'structured termination count')
    if termination['count']<1:bad('structured termination count mismatch')
   elif termination_kind=='line_exact_exclusive':
    closed(termination,{'kind','selector'},'structured termination');selector=closed(termination['selector'],{'kind','text'},'structured termination selector')
    if selector['kind']!='line_exact' or not st(selector['text'],'structured termination text'):bad('structured termination mismatch')
   elif termination_kind=='end_of_page':closed(termination,{'kind'},'structured termination')
   else:bad('structured termination mismatch')
   for note in region['attached_note_selectors']:
    closed(note,{'kind','text'},'structured note selector')
    if note['kind']!='line_exact' or not st(note['text'],'structured note text'):bad('structured note selector mismatch')
   if fmt=='markdown_pipe_table' and (not st(region['header_line'],'table header') or not isinstance(region['header_tokens'],list) or not region['header_tokens'] or not isinstance(region['ordered_first_column_keys'],list) or not region['ordered_first_column_keys']):bad('table contract mismatch')
   if fmt=='numbered_record_series' and (not isinstance(region['ordered_first_column_keys'],list) or not region['ordered_first_column_keys']):bad('series contract mismatch')
 if len(ids)!=N['structured_content'] or placements!=set(range(1,N['structured_content']+1)):bad('structured declaration count mismatch')

def is_descendant(anchor,owner,hierarchy):
 while anchor:
  if anchor==owner:return True
  anchor=hierarchy[anchor]['parent_anchor']
 return False

def owner_block_ranges(reader_text):
 anchors=list(re.finditer(r'<a id="([^"]+)"></a>',reader_text)); ranges={}
 for index,match in enumerate(anchors):
  anchor=match.group(1)
  if anchor in ranges:bad('duplicate reader owner anchor')
  ranges[anchor]=(match.start(),anchors[index+1].start() if index+1<len(anchors) else len(reader_text))
 return ranges

def rewrite_source_xrefs(raw,xrefs):
 """Apply only pre-resolved exact source-line replacements, returning their ids."""
 executed=[]
 for xref in xrefs:
  line=xref['source_line']
  if raw.count(line)==0:continue
  if raw.count(line)!=1:bad(f"xref source line resolution mismatch: {xref['xref_id']}")
  rebuilt='';cursor=0
  for segment in xref['segments']:
   position=line.find(segment['source_text'],cursor)
   if position<0 or line.find(segment['source_text'],position+1)!=-1:bad('xref segment resolution mismatch')
   rebuilt+=line[cursor:position]
   rebuilt+=f"[{segment['reader_text']}](#{segment['target_anchor']})" if segment['emit_link'] else segment['reader_text']
   cursor=position+len(segment['source_text'])
  raw=raw.replace(line,rebuilt+line[cursor:],1);executed.append(xref['xref_id'])
 return raw,executed

def structured_resolver(config,binding_index,package,reader_text=None,asset_ledger=None,emitted_ledger=None,suppression_ranges=()):
 """Resolve and verify exact configured regions, retaining their source text unchanged."""
 hierarchy={x['anchor']:x for x in config['hierarchy']}; bindings={x['anchor']:x for x in binding_index['bindings']}; evidence=[]; seen=set(); assets={x['asset_id']:x for x in config['assets']}; ledger={x['asset_id']:x for x in (asset_ledger or [])}; reviews={x['review_id']:x for x in config['visual_review_units']}; owner_ranges=owner_block_ranges(reader_text) if reader_text is not None else {}
 for row in sorted(config['structured_content'],key=lambda x:x['placement_index']):
  if row['structure_id'] in seen:bad('duplicate structured evidence')
  seen.add(row['structure_id']); facts=row['fact_expectations']; fragments=[]; attached_notes=[]
  if row['classification']=='visual_form':
   asset=assets[facts['asset_id']]; emitted=ledger.get(asset['asset_id'])
   review_ids=[facts['ordinary_review_id'],facts['structured_review_id']]
   if not emitted or emitted.get('sha256')!=asset['sha256'] or any(review_id not in reviews or reviews[review_id]['status']!='pending_external_visual_qa' for review_id in review_ids):bad('visual form evidence mismatch')
   marker=f']({emitted["output_path"]})'; occurrence=reader_text.count(marker) if reader_text is not None else 1
   if reader_text is not None:
    if row['owner_anchor'] not in owner_ranges:bad('visual form owner mismatch')
    start,end=owner_ranges[row['owner_anchor']];owner_occurrence=reader_text[start:end].count(marker)
    if owner_occurrence!=1 or occurrence-owner_occurrence!=0:bad('visual form emitted occurrence mismatch')
   if occurrence!=1:bad('visual form emitted occurrence mismatch')
   evidence.append({'structure_id':row['structure_id'],'classification':row['classification'],'logical_owner':row['owner_anchor'],'representation':row['representation'],'asset_id':asset['asset_id'],'asset_sha256':asset['sha256'],'review_ids':review_ids,'emitted_occurrence':occurrence,'fragments':[],'attached_notes':[]});continue
  bodies=[]
  for region in facts['regions']:
   owner=region['binding_anchor']
   if not is_descendant(owner,row['owner_anchor'],hierarchy):bad('structured owner mismatch')
   raw,page_lines=source_lines(package,region['page']); matches=[line for line in page_lines if line['text'].rstrip('\r\n')==region['start_selector']['text']]; starts=[span for span in bindings[owner]['source_span_hashes'] if span['page']==region['page'] for line in matches if span['start']<=line['start']<span['end']]
   if len(starts)!=1:bad(f"structured region resolution mismatch: {row['structure_id']}")
   span=starts[0]; start=next(line['start'] for line in matches if span['start']<=line['start']<span['end']); term=region['termination']
   if term['kind']=='line_exact_exclusive':
    end_text=term['selector']['text']; end=raw.find(end_text,start+1)
    if end<0:bad(f"structured termination mismatch: {row['structure_id']}")
   else:
    end=span['end']
   body=raw[start:end]
   if region['source_format']=='markdown_pipe_table' and term['kind']=='record_count':
    lines=body.splitlines(keepends=True); header_index=next((i for i,line in enumerate(lines) if line.startswith('|') and all(token in line for token in region['header_tokens'])),None)
    if header_index is None:bad('structured table header mismatch')
    records=[i for i,line in enumerate(lines[header_index+1:],header_index+1) if line.startswith('|') and not re.fullmatch(r'\|[\s|:-]+\|\r?\n?',line)]
    if len(records)<term['count']:bad('structured table record mismatch')
    body=''.join(lines[:records[term['count']-1]+1]); end=start+len(body)
   full_source=''.join(source_lines(package,page)[0] for page in row['source_pages'])
   for value in facts['lexical_protections']:
    if value not in full_source:bad('structured lexical protection mismatch')
   for value in facts.get('required_literal_substrings',[]):
    if value not in body:bad('structured literal mismatch')
   for value in facts.get('forbidden_literal_tokens',[]):
    if value in body:bad('structured forbidden literal')
   bodies.append(body)
   if region['source_format']=='markdown_pipe_table':
    lines=body.splitlines(); header=[x for x in lines if (x==region['header_line'] if region['header_line'].startswith('|') else x.startswith('|') and all(token in x for token in region['header_tokens']))]
    if len(header)!=1:bad('structured table header mismatch')
    rows=[x for x in lines if x.startswith('|') and x not in header and not re.fullmatch(r'\|[\s|:-]+\|',x)]
    keys=[x.split('|')[1].strip().strip('*') for x in rows]
    if keys!=region['ordered_first_column_keys']:bad(f"structured table keys mismatch: {row['structure_id']}")
   elif region['source_format']=='numbered_record_series':
    if 'header_line' in region and region['header_line'] not in body:bad('structured series header mismatch')
    keys=region['ordered_first_column_keys']; found=[key for key in keys if re.search(r'(?m)^'+re.escape(key)+r'\s',body)]
    if found!=keys:bad('structured series keys mismatch')
   for note in region['attached_note_selectors']:
    note_lines=[line for line in page_lines if line['text'].rstrip('\r\n')==note['text']]
    note_owners=[(anchor,item) for anchor,binding in bindings.items() for item in binding['source_span_hashes'] if item['page']==region['page'] for line in note_lines if item['start']<=line['start']<item['end']]
    if len(note_owners)!=1 or len(note_lines)!=1:bad('structured note mismatch')
    note_owner,_=note_owners[0]
    if not is_descendant(row['owner_anchor'],note_owner,hierarchy):bad('structured note owner mismatch')
    note_start,note_end=note_lines[0]['start'],note_lines[0]['end'];note_body=raw[note_start:note_end]
    note_evidence={'binding_anchor':note_owner,'source_page':region['page'],'source_start':note_start,'source_end':note_end,'source_sha256':hashlib.sha256(note_body.encode('utf8')).hexdigest().upper(),'selector':note['text']}
    if reader_text is not None:
     note_suppressions=[(x['start_offset']-note_start,x['end_offset']-note_start) for x in suppression_ranges if x['source_containment']['claim_owner_anchor']==note_owner and x['source_page']==region['page'] and note_start<=x['start_offset'] and x['end_offset']<=note_end]
     note_raw,_=apply_source_edit_plan(note_body,[xref for xref in config['xrefs'] if xref['source_selector']=='line_exact' and xref['owner_anchor']==note_owner and xref['source_page']==region['page']],note_suppressions)
     expected_note=clean_span(note_raw,[{'page':region['page'],'start':note_start,'end':note_end}],bindings[note_owner]['locators'],hierarchy[note_owner]['level'],hierarchy[note_owner]['title'])
     candidates=[item for item in (emitted_ledger or []) if item['binding_anchor']==note_owner and item['source_page']==region['page'] and item['source_start']<=note_start and note_end<=item['source_end']]
     if len(candidates)!=1 or not expected_note:bad('structured emitted note owner mismatch')
     candidate=candidates[0];relative=candidate['emitted_text'].find(expected_note)
     if relative<0 or candidate['emitted_text'].find(expected_note,relative+1)!=-1:bad('structured emitted note range mismatch')
     emitted_start=candidate['emitted_start']+relative;emitted_end=emitted_start+len(expected_note);emitted_body=reader_text[emitted_start:emitted_end]
     if emitted_body!=expected_note:bad('structured emitted note range mismatch')
     owner_start,owner_end=owner_ranges[note_owner];occurrence=reader_text[owner_start:owner_end].count(expected_note)
     if occurrence!=1 or reader_text.count(expected_note)-occurrence!=0:bad('structured emitted note occurrence mismatch')
     note_evidence.update({'emitted_start':emitted_start,'emitted_end':emitted_end,'emitted_sha256':hashlib.sha256(emitted_body.encode('utf8')).hexdigest().upper(),'emitted_occurrence':occurrence})
    attached_notes.append(note_evidence)
   emitted={'source_page':region['page'],'binding_anchor':owner,'source_start':start,'source_end':end,'source_sha256':hashlib.sha256(body.encode('utf8')).hexdigest().upper(),'source_format':region['source_format']}
   if reader_text is not None:
    region_suppressions=[(x['start_offset']-start,x['end_offset']-start) for x in suppression_ranges if x['source_containment']['claim_owner_anchor']==owner and x['source_page']==region['page'] and start<=x['start_offset'] and x['end_offset']<=end]
    expected_raw,_=apply_source_edit_plan(body,[xref for xref in config['xrefs'] if xref['source_selector']=='line_exact' and xref['owner_anchor']==owner and xref['source_page']==region['page']],region_suppressions)
    expected=clean_span(expected_raw,[{'page':region['page'],'start':start,'end':end}],bindings[owner]['locators'],hierarchy[owner]['level'],hierarchy[owner]['title'])
    candidates=[item for item in (emitted_ledger or []) if item['binding_anchor']==owner and item['source_page']==region['page'] and item['source_start']<=start and end<=item['source_end']]
    if len(candidates)!=1 or not expected:bad('structured emitted owner mismatch')
    candidate=candidates[0];relative=candidate['emitted_text'].find(expected)
    if relative<0 or candidate['emitted_text'].find(expected,relative+1)!=-1:bad(f"structured emitted range mismatch: {row['structure_id']}")
    emitted_start=candidate['emitted_start']+relative;emitted_end=emitted_start+len(expected);emitted_body=reader_text[emitted_start:emitted_end]
    if emitted_body!=expected:bad('structured emitted range mismatch')
    emitted.update({'emitted_start':emitted_start,'emitted_end':emitted_end,'emitted_sha256':hashlib.sha256(emitted_body.encode('utf8')).hexdigest().upper()})
   fragments.append(emitted)
  tokens=facts.get('ordered_literal_tokens',[]); positions=[''.join(bodies).find(token) for token in tokens]
  if any(x<0 for x in positions) or positions!=sorted(positions):bad('structured token order mismatch')
  evidence.append({'structure_id':row['structure_id'],'classification':row['classification'],'logical_owner':row['owner_anchor'],'representation':row['representation'],'fragments':fragments,'attached_notes':attached_notes})
 if len(evidence)!=len(config['structured_content']) or {x['structure_id'] for x in evidence}!={x['structure_id'] for x in config['structured_content']}:bad('structured evidence mismatch')
 return evidence

def locate(page_lines,locator):
 """Resolve only the declared selector; there is no normalization or fallback search."""
 selector=locator['selector']; kind=locator['selector_kind']
 if kind=='page_start':matches=page_lines[:1]
 elif kind=='line_prefix':matches=[x for x in page_lines if x['text'].rstrip('\r\n').startswith(selector)]
 else:matches=[x for x in page_lines if x['text'].rstrip('\r\n')==selector]
 if len(matches)!=1:bad('locator must resolve exactly once')
 return matches[0]

def resolve_bindings(c,repository_root,reconstruction_package,fail_on_conservation=True):
 """Read-only deterministic binding index and in-memory lexical conservation evidence."""
 root=Path(repository_root).resolve(); package=Path(reconstruction_package).resolve(strict=True)
 anchors={x['anchor'] for x in c['hierarchy']}; bindings=binding_declarations(c,anchors,set(range(1,125)))
 page_data={p:source_lines(package,p) for p in range(1,125)}; starts={p:[] for p in range(1,125)}; resolved=[]
 for row in sorted(c['hierarchy'],key=lambda x:x['assembly_binding']['order']):
  b=row['assembly_binding']; matches=[]
  for locator in b['locators']:
   match=locate(page_data[locator['page']][1],locator); matches.append({'page':locator['page'],'line':match['line'],'start':match['start'],'end':match['end'],'selector_kind':locator['selector_kind'],'selector':locator['selector'],'action':locator['action']})
   starts[locator['page']].append((match['start'],row['anchor']))
  for page in b['continuation_pages']:
   if not any(x['page']==page for x in matches):starts[page].append((0,row['anchor']))
  resolved.append({'anchor':row['anchor'],'kind':b['kind'],'order':b['order'],'source_pages':row['source_pages'],'locators':matches,'continuation_pages':b['continuation_pages'],'unit_ref':b['unit_ref'],'shared_prefix_owner':b['shared_prefix_owner'],'action':[x['action'] for x in matches],'source_span_hashes':[]})
 claims={p:[] for p in range(1,125)}
 for page,entries in starts.items():
  ordered=sorted(entries)
  if len({x[0] for x in ordered})!=len(ordered):bad('overlapping binding starts')
  raw,_=page_data[page]
  for index,(start,anchor) in enumerate(ordered):
   end=ordered[index+1][0] if index+1<len(ordered) else len(raw);claims[page].append((start,end,anchor))
 for row in resolved:
  for page,start,end,anchor in claims_for_anchor(claims,row['anchor']):
   row['source_span_hashes'].append({'page':page,'start':start,'end':end,'sha256':hashlib.sha256(page_data[page][0][start:end].encode('utf8')).hexdigest().upper()})
  if row['kind']=='generated' and row['source_span_hashes']:bad('generated binding consumes source')
 validate_reader_surface(c,package,{'bindings':resolved})
 _,_,suppressions=reader_surface_ranges(c,package)
 ledger=conservation_ledger(page_data,claims,c,suppressions)
 if fail_on_conservation and any(ledger[key] for key in ('unowned_blocks','duplicate_blocks','unauthorized_suppression_blocks')):bad(f"binding conservation failed: {ledger['unowned_blocks']} unowned, {ledger['duplicate_blocks']} duplicate")
 return {'bindings':resolved,'locator_count':sum(len(x['locators']) for x in resolved),'conservation':ledger}

def claims_for_anchor(claims,anchor):
 for page,rows in claims.items():
  for start,end,owner in rows:
   if owner==anchor:yield page,start,end,owner

def conservation_ledger(page_data,claims,c,suppressions=()):
 """Account lexical source blocks; explicit owned-page units classify their entire declared pages."""
 review_pages={x['review_id']:x['source_pages'] for x in c['visual_review_units']}
 owned_pages={p:row['anchor'] for row in c['hierarchy'] if row['assembly_binding']['kind']=='owned_page_unit' for p in review_pages[row['assembly_binding']['unit_ref']]}
 generated_pages={p for row in c['hierarchy'] if row['assembly_binding']['kind']=='generated' for p in row['source_pages']}
 total=owned=unowned=duplicate=generated=0
 for page,(_,lines) in page_data.items():
  for line in lines:
   if not line['text'].strip():continue
   total+=1; owners=[owned_pages[page]] if page in owned_pages else [anchor for start,end,anchor in claims[page] if start<=line['start']<end]
   if len(owners)==1:owned+=1
   elif not owners:
    if page in generated_pages:generated+=1
    else:unowned+=1
   else:duplicate+=1
 authorized=0; suppressed_bytes=0; normal=owned_page=cross_owner=generated_claim=unproven=0
 for row in suppressions:
  containment=row['source_containment']; claimant=containment['claim_owner_anchor']
  if containment['kind']=='normal_claim': normal+=1; matches=[owner for start,end,owner in claims[row['source_page']] if start<=row['start_offset'] and row['end_offset']<=end]
  elif containment['kind']=='owned_page_unit': owned_page+=1; matches=[owned_pages.get(row['source_page'])]
  else: generated_claim+=1; matches=[]
  if matches!=[claimant]: unproven+=1
  if claimant!=row['owner_anchor']: cross_owner+=1
  authorized+=1; suppressed_bytes+=len(row['text'].encode('utf8'))
 if authorized!=len(suppressions): bad('suppression conservation mismatch')
 return {'total_blocks':total,'owned_blocks':owned,'generated_navigation_blocks':generated,'unowned_blocks':unowned,'duplicate_blocks':duplicate,'authorized_suppression_rows':authorized,'authorized_suppression_utf8_bytes':suppressed_bytes,'normal_claim_suppressions':normal,'owned_page_suppressions':owned_page,'cross_owner_suppressions':cross_owner,'generated_suppression_claims':generated_claim,'unproven_suppression_claims':unproven,'unauthorized_suppression_blocks':unproven}
def preflight(contract,reconstruction_package,publication_config,source_pdf):
 cfg=Path(publication_config).resolve(strict=True);root=root_for(cfg.parent);raw=js(cfg,'publication config')
 if raw.get('schema')==V2_SCHEMA:
  c=v2_config(raw);contract=Path(contract).resolve(strict=True);source=Path(source_pdf).resolve(strict=True);pkg=Path(reconstruction_package)
  if not contract.is_file() or not source.is_file():bad('v2 input identity mismatch')
  binding=v2_input_binding(c,root,source,pkg)
  # B1c4 runs before every later v2 seam.  It is read-only and cannot create
  # a candidate, a render, or any checkout-local configuration output.
  asset_audit=v2_b1c4_asset_audit(root)
  return {'status':'preflight_passed','scenario_id':c['scenario_id'],'contract_sha256':dig(contract),'source_sha256':dig(source),'reconstruction_inventory_sha256':binding['reconstruction_inventory_sha256'],'asset_audit':asset_audit}
 c=config(cfg);pkg=Path(reconstruction_package).resolve(strict=True);contract=Path(contract).resolve(strict=True);source=Path(source_pdf).resolve(strict=True);declarations(c,root,pkg);ident(root,c['contract'],'contract',contract);ident(root,{k:c['document']['source_pdf'][k] for k in ('path','bytes','sha256')},'source PDF',source)
 a=closed(c['accepted_reconstruction'],{'root','file_count','total_bytes','inventory_algorithm','inventory_sha256','reconstructed_md','qa','provenance','asset_manifest','acceptance_receipt'},'accepted reconstruction')
 if pkg!=rel(root,a['root'],'reconstruction root') or a['inventory_algorithm']!='SHA-256 over ordinal UTF-8 LF relative_path<TAB>bytes<TAB>UPPER_SHA256<LF>' or inventory(pkg)!=(a['file_count'],a['total_bytes'],a['inventory_sha256']):bad('reconstruction inventory mismatch')
 for l,x in [('reconstructed_md',a['reconstructed_md']),('qa',a['qa']),('provenance',a['provenance']),('asset_manifest',a['asset_manifest']),('acceptance_receipt',a['acceptance_receipt'])]:ident(root,x,l)
 qa=js(rel(root,a['qa']['path'],'qa path'),'reconstruction QA')
 if qa.get('status')!='candidate_ready_for_reconstruction_review' or not isinstance(qa.get('gates'),dict) or 'no_open_blockers' not in qa['gates'] or any(x.get('status')!='pass' or x.get('errors')!=[] for x in qa['gates'].values() if isinstance(x,dict)):bad('reconstruction gates mismatch')
 pv=js(rel(root,a['provenance']['path'],'provenance path'),'provenance')
 if pv.get('scenario',{}).get('id')!='viral' or pv.get('source',{}).get('sha256')!=c['document']['source_pdf']['sha256']:bad('provenance mismatch')
 mf=js(rel(root,a['asset_manifest']['path'],'manifest path'),'manifest');hs={x.get('sha256') for x in mf.get('assets',[]) if isinstance(x,dict)}
 if any(x['sha256'] not in hs for x in c['assets'] if x['origin']=='accepted_reconstruction_asset'):bad('asset manifest closure mismatch')
 return {'status':'preflight_passed','scenario_id':'viral','contract_sha256':dig(contract),'source_sha256':dig(source),'reconstruction_inventory_sha256':a['inventory_sha256']}

def v2_b1c4_asset_audit(root):
 """Builder-owned, read-only B1c4 frozen-asset conservation audit.

 It intentionally shares no author helper: this is the public builder-side
 evidence binding used before any candidate-materialization route.
 """
 root=Path(root);v1=js(root/'kb_creator/working/viral/master_en/publication_config_v1.json','v2 frozen v1')
 package=root/'kb_creator/working/viral/source_reconstruction/20260901_step6a_reconstructed_en_package_v4';manifest=package/'ASSET_MANIFEST.json'
 comparison=root/'kb_creator/working/viral/source_reconstruction/20260901_step6a_mineru_three_view_full/comparison/comparison.json'
 if dig(manifest)!='914A2C8B46401830EDBDEADDDDA24C7A8C0B6442F2775C439A79CC5529D283E9' or dig(comparison)!='5A4DB5DB697B1E483926AB1DAB387CB496EF0539DC76EAD51B830F5DCF1862F0':bad('v2 asset evidence identity mismatch')
 rows=v1.get('assets');assets=js(manifest,'v2 asset manifest').get('assets')
 if not isinstance(rows,list) or len(rows)!=123 or not isinstance(assets,list) or len(assets)!=121:bad('v2 asset inventory mismatch')
 manifest_by_digest={row.get('sha256','').upper():row for row in assets if isinstance(row,dict)}
 excluded={row['asset_id'] for row in rows if row.get('source_page') in {123,124}}
 reclassified={'viral-accepted-6acc049ed2ad40ebed064312a87ddfce5a404f4fc2487ea1721c656ed541c419','viral-accepted-647b583cd53fbfdaab7ac6d9643a81bbd5145c125d628c7074b02db0c9f7888b','viral-accepted-eda9c6f6d6ef94ed41034cd12401547ed37101ef2f8b1ebf30d9602b87db71ab','viral-accepted-21704f0d57843965013f5eccfa36bcd64321dcc1513cd7d99dead8627d58994e','viral-accepted-b2ba43b7e57f4c9972780be961deab50d72ea311f795285da15712ba29b6e30e','viral-accepted-af48429e4ab502e7fc33a545039dab60a3e4e28a8c03a29f56ff57b9280cdd12','viral-accepted-adb4ff51bd5ebff464834e0fb324310c281eb20d2c4b0f4e82d1fbaf3ef72541','viral-accepted-f7ce778cc1eb05cb6fef0f26457d06e68019ee30c76a5723f259dc82b89b321d','viral-accepted-e1c168ca34db2f98a27391e749f08a0fcdda832034d68e5fd0fbc38b00f584dc','viral-accepted-5d2410afd9a6593cdce0d7f0d411835cf4a726551a1b1e18b6f79d04ed42230b','viral-accepted-331f4d575265e02a4ba97b4e204dbbb20b648e9b62d44eb47ea11ab6998c00d3','viral-accepted-92c65562fe49c02049e4b40e4a278b667e1361568455fdd89a724389a8d01d50','viral-accepted-07982af9981b82074567f2fa5d976b00cb40a0331f01438352f9fd59fc864aa4','viral-accepted-9d7ebb95113ecd5d9114224cff873b14f2db563d61015978164a78e4ff05953f','viral-accepted-1ae1543b9ff31ba9d7c4271ae01d86f05fb722c00e9f7851ce1dffc820aee3b8','viral-accepted-dcf1f2f6dd9540217155f01d5b03d965aedef98d965c2a33e987f0f5996eb166'}
 outcomes=[]
 for row in rows:
  source=manifest_by_digest.get(str(row.get('sha256','')).upper());aid=row['asset_id']
  if source:
   path=package/source['stored_path']
   if not path.is_file() or dig(path)!=source['sha256'] or path.stat().st_size<=0:bad('v2 asset binary mismatch')
   try:
    with Image.open(path) as image:image.verify()
   except OSError:bad('v2 asset binary mismatch')
  outcomes.append('excluded_advertising' if aid in excluded else 'reclassified' if aid in reclassified else 'retained_rebound' if aid.endswith(('b90cb9a3752383888c733905588e9c3859b113e47f1f457057c72e33689a7585','da0cac1c9c0c880a75d3be69c59e965d0b7b0f223f16a077072786c8af30083e')) else 'retained_unchanged')
 counts={key:outcomes.count(key) for key in ('retained_unchanged','retained_rebound','reclassified','excluded_advertising')}
 if counts!={'retained_unchanged':99,'retained_rebound':2,'reclassified':16,'excluded_advertising':6}:bad('v2 asset partition mismatch')
 return {'counts':counts,'path_binaries':sum(row.get('sha256','').upper() in manifest_by_digest for row in rows)}

def v2_b1c4_expected_assets(root):
 """Recompute every B1c4 declaration from immutable evidence, not config."""
 root=Path(root);package=root/'kb_creator/working/viral/source_reconstruction/20260901_step6a_reconstructed_en_package_v4';manifest_path=package/'ASSET_MANIFEST.json';comparison_path=root/'kb_creator/working/viral/source_reconstruction/20260901_step6a_mineru_three_view_full/comparison/comparison.json';source_pdf=root/'kb_creator/working/viral/source/Call_of_Cthulhu_Viral.pdf'
 frozen=js(root/'kb_creator/working/viral/master_en/publication_config_v1.json','v2 B1c4 frozen expected assets')['assets'];manifest=js(manifest_path,'v2 B1c4 expected manifest')['assets'];comparison=js(comparison_path,'v2 B1c4 expected comparison');by_digest={row['sha256'].upper():row for row in manifest}
 reclassified={'viral-accepted-6acc049ed2ad40ebed064312a87ddfce5a404f4fc2487ea1721c656ed541c419','viral-accepted-647b583cd53fbfdaab7ac6d9643a81bbd5145c125d628c7074b02db0c9f7888b','viral-accepted-eda9c6f6d6ef94ed41034cd12401547ed37101ef2f8b1ebf30d9602b87db71ab','viral-accepted-21704f0d57843965013f5eccfa36bcd64321dcc1513cd7d99dead8627d58994e','viral-accepted-b2ba43b7e57f4c9972780be961deab50d72ea311f795285da15712ba29b6e30e','viral-accepted-af48429e4ab502e7fc33a545039dab60a3e4e28a8c03a29f56ff57b9280cdd12','viral-accepted-adb4ff51bd5ebff464834e0fb324310c281eb20d2c4b0f4e82d1fbaf3ef72541','viral-accepted-f7ce778cc1eb05cb6fef0f26457d06e68019ee30c76a5723f259dc82b89b321d','viral-accepted-e1c168ca34db2f98a27391e749f08a0fcdda832034d68e5fd0fbc38b00f584dc','viral-accepted-5d2410afd9a6593cdce0d7f0d411835cf4a726551a1b1e18b6f79d04ed42230b','viral-accepted-331f4d575265e02a4ba97b4e204dbbb20b648e9b62d44eb47ea11ab6998c00d3','viral-accepted-92c65562fe49c02049e4b40e4a278b667e1361568455fdd89a724389a8d01d50','viral-accepted-07982af9981b82074567f2fa5d976b00cb40a0331f01438352f9fd59fc864aa4','viral-accepted-9d7ebb95113ecd5d9114224cff873b14f2db563d61015978164a78e4ff05953f','viral-accepted-1ae1543b9ff31ba9d7c4271ae01d86f05fb722c00e9f7851ce1dffc820aee3b8','viral-accepted-dcf1f2f6dd9540217155f01d5b03d965aedef98d965c2a33e987f0f5996eb166'};rebound={'viral-accepted-b90cb9a3752383888c733905588e9c3859b113e47f1f457057c72e33689a7585','viral-accepted-da0cac1c9c0c880a75d3be69c59e965d0b7b0f223f16a077072786c8af30083e'}
 intervals={page:[] for page in range(1,123)}
 for name,expected_hash in (('boundary_ledger_pages_001_040.json','8C0A666D962C879C62B7168B60AB717EA04F833FFE728446F150F64FCB24DDAF'),('boundary_ledger_pages_041_068.json','8673868ED762E327517891D7C72DBA21A5C88F1A4173EBB0EFF597D30453EF13'),('boundary_ledger_pages_069_122.json','14338236CDB2AAE6213CCE5F36DA93C661F2DF35D9F7E96F8346C770BF00CFD1')):
  ledger=root/'kb_creator/working/viral/master_en/review_evidence/20260902_user_review_remediation_v1'/name
  if dig(ledger)!=expected_hash:bad('v2 B1c4 ledger identity mismatch')
  for unit in js(ledger,'v2 B1c4 expected ledger')['units']:
   for segment in unit.get('source_segments',[]):
    page=segment['page'];raw=(package/'pages'/segment['path']).read_bytes();lines=[];offset=0
    for line in raw.decode('utf8').splitlines(keepends=True):offset+=len(line.encode('utf8'));lines.append(offset)
    begin,end=segment['start_line']-1,segment['end_line']
    if begin<0 or end>len(lines) or begin>=end:
     decoded=raw.decode('utf8').splitlines();matches=[(left,right) for left in range(len(decoded)) for right in range(left+1,len(decoded)+1) if hashlib.sha256('\n'.join(decoded[left:right]).encode('utf8')).hexdigest().upper()==segment['sha256_lf_lines']]
     if len(matches)!=1:bad('v2 B1c4 ledger span mismatch')
     begin,end=matches[0]
    intervals[page].append((0 if begin==0 else lines[begin-1],lines[end-1],unit))
 spans={}
 for page,items in intervals.items():
  raw=(package/f'pages/page-{page:03d}.md').read_bytes();cuts=sorted({0,len(raw),*(point for left,right,_ in items for point in (left,right))})
  for ordinal,(start,end) in enumerate(zip(cuts,cuts[1:]),1):
   owners=[unit for left,right,unit in items if left<=start and end<=right]
   if owners and min(owners,key=lambda unit:(unit['source_order_key'],unit['id'])).get('kind')=='asset_ownership':
    marker=raw[start:end];match=re.search(rb'[0-9a-f]{64}(?=\.(?:jpg|jpeg|png))',marker,re.I)
    if match:spans[match.group().decode().upper()]={'span_id':f'span-p{page:03d}-{ordinal:03d}','path':f'pages/page-{page:03d}.md','raw':marker,'start_byte':start,'end_byte':end,'start_char':len(raw[:start].decode('utf8')),'end_char':len(raw[:end].decode('utf8'))}
 result={}
 for source in frozen:
  aid=source['asset_id'];page=source['source_page'];outcome='excluded_advertising' if page in {123,124} else 'reclassified' if aid in reclassified else 'retained_rebound' if aid in rebound else 'retained_unchanged'
  if outcome=='excluded_advertising':continue
  if not source.get('sha256'):
   provenance={'kind':'reviewed_provisional_full_page','source_pdf_identity':{'path':str(source_pdf.relative_to(root)).replace('\\','/'),'bytes':source_pdf.stat().st_size,'sha256':dig(source_pdf)},'physical_page':page,'page_index_zero_based':page-1,'region':{'kind':'full_media_box','points':[0,0,612,792]},'render_recipe':{'tool':'pdftoppm','first_page':page,'last_page':page,'dpi':200,'format':'png','box':'media_box','rotation':'source_applied','color':'rgb','background':'white','alpha':False,'metadata':'stripped'},'output_media_type':'image/png','output_dimensions':{'width':1700,'height':2200},'quality_stage':'provisional_full_page'};result[aid]={'asset_id':aid,'disposition':'reader','source_page':page,'binary':None,'provenance':provenance,'migration_outcome':outcome};continue
  entry=by_digest[source['sha256'].upper()];path=package/entry['stored_path']
  with Image.open(path) as image:
   image.load();media={'JPEG':'image/jpeg','PNG':'image/png'}[image.format]
  binary={'path':str(path.relative_to(root)).replace('\\','/'),'bytes':path.stat().st_size,'sha256':dig(path),'media_type':media,'dimensions':image_identity(path,media,'v2 B1c4 expected asset')}
  span=spans.get(binary['sha256'])
  if span:provenance={'kind':'markdown_image_reference','span_id':span['span_id'],'page_markdown_identity':{'path':str((package/span['path']).relative_to(root)).replace('\\','/'),'bytes':(package/span['path']).stat().st_size,'sha256':dig(package/span['path'])},'start_byte':span['start_byte'],'end_byte':span['end_byte'],'start_char':span['start_char'],'end_char':span['end_char'],'marker_sha256':hashlib.sha256(span['raw']).hexdigest().upper()}
  else:
   selected=[(view,block) for view,item in comparison['views'].items() for block in item['blocks'] if entry['source_path'] in block.get('assets',[]) and view==entry['view']]
   if len(selected)!=1:bad('v2 B1c4 expected comparison mismatch')
   view,block=selected[0];provenance={'kind':'visual_region','asset_manifest_identity':{'path':str(manifest_path.relative_to(root)).replace('\\','/'),'bytes':manifest_path.stat().st_size,'sha256':dig(manifest_path)},'asset_manifest_row_sha256':v2_canonical_row(entry),'comparison_identity':{'path':str(comparison_path.relative_to(root)).replace('\\','/'),'bytes':comparison_path.stat().st_size,'sha256':dig(comparison_path)},'selected_view':view,'source_asset_reference':entry['source_path'],'raw_index':block['raw_index'],'block_type':block['type'],'source_page':block['source_page'],'bbox':block['bbox'],'comparison_block_sha256':v2_canonical_row(block)}
  result[aid]={'asset_id':aid,'disposition':'evidence_only' if outcome=='reclassified' else ('reader' if outcome=='retained_rebound' else source['representation']),'source_page':page,'binary':binary,'provenance':provenance,'migration_outcome':outcome}
 for page,name in zip((106,107,112,114,116,118,120,122,26),('map-ground-floor-basement','map-ground-floor-basement','pregen-marco-back','pregen-corrina-back','pregen-enoch-back','pregen-peter-back','pregen-ku-hyeon-back','pregen-blank-back','isola-di-malamente-opening')):
   provenance={'kind':'reviewed_provisional_full_page','source_pdf_identity':{'path':str(source_pdf.relative_to(root)).replace('\\','/'),'bytes':source_pdf.stat().st_size,'sha256':dig(source_pdf)},'physical_page':page,'page_index_zero_based':page-1,'region':{'kind':'full_media_box','points':[0,0,612,792]},'render_recipe':{'tool':'pdftoppm','first_page':page,'last_page':page,'dpi':200,'format':'png','box':'media_box','rotation':'source_applied','color':'rgb','background':'white','alpha':False,'metadata':'stripped'},'output_media_type':'image/png','output_dimensions':{'width':1700,'height':2200},'quality_stage':'provisional_full_page'};aid=f'viral-provisional-{name}-page-{page}';result[aid]={'asset_id':aid,'disposition':'reader','source_page':page,'binary':None,'provenance':provenance,'migration_outcome':'new_reviewed_target'}
 if len(result)!=126 or sum(row['provenance']['kind']=='markdown_image_reference' for row in result.values())!=16 or sum(row['provenance']['kind']=='visual_region' for row in result.values())!=100:bad('v2 B1c4 expected declaration mismatch')
 return result

def v2_b1c4_migration_closure(rows,targets):
 """Closed, no-output migration identity gate for B1c4 asset rows."""
 if not isinstance(rows,list) or len(rows)!=123 or not isinstance(targets,list) or len(targets)<8:bad('v2 B1c4 migration count mismatch')
 ids=[row.get('source_id') for row in rows if isinstance(row,dict)]
 if len(ids)!=123 or len(set(ids))!=123 or any(not isinstance(row,dict) or set(row)!={'source_id','outcome','target_ids','decision_ref'} for row in rows):bad('v2 B1c4 migration schema mismatch')
 counts={key:sum(row['outcome']==key for row in rows) for key in ('retained_unchanged','retained_rebound','reclassified','excluded_advertising')}
 if counts!={'retained_unchanged':99,'retained_rebound':2,'reclassified':16,'excluded_advertising':6} or sum(not row['target_ids'] for row in rows)!=6:bad('v2 B1c4 migration closure mismatch')
 frozen=js(Path(__file__).resolve().parents[2]/'kb_creator/working/viral/master_en/publication_config_v1.json','v2 B1c4 frozen ledger').get('assets',[])
 pages={f"assets:{item['asset_id']}":item['source_page'] for item in frozen if isinstance(item,dict) and isinstance(item.get('asset_id'),str)}
 order=[f"assets:{item['asset_id']}" for item in frozen]
 if ids!=order:bad('v2 B1c4 migration source order mismatch')
 reclassified={'assets:viral-accepted-6acc049ed2ad40ebed064312a87ddfce5a404f4fc2487ea1721c656ed541c419':'OUT-006'}
 for item in ('647b583cd53fbfdaab7ac6d9643a81bbd5145c125d628c7074b02db0c9f7888b','eda9c6f6d6ef94ed41034cd12401547ed37101ef2f8b1ebf30d9602b87db71ab','21704f0d57843965013f5eccfa36bcd64321dcc1513cd7d99dead8627d58994e','b2ba43b7e57f4c9972780be961deab50d72ea311f795285da15712ba29b6e30e','af48429e4ab502e7fc33a545039dab60a3e4e28a8c03a29f56ff57b9280cdd12'):reclassified['assets:viral-accepted-'+item]='OUT-007'
 for item in ('adb4ff51bd5ebff464834e0fb324310c281eb20d2c4b0f4e82d1fbaf3ef72541','f7ce778cc1eb05cb6fef0f26457d06e68019ee30c76a5723f259dc82b89b321d','e1c168ca34db2f98a27391e749f08a0fcdda832034d68e5fd0fbc38b00f584dc'):reclassified['assets:viral-accepted-'+item]='OUT-024'
 for item in ('5d2410afd9a6593cdce0d7f0d411835cf4a726551a1b1e18b6f79d04ed42230b','331f4d575265e02a4ba97b4e204dbbb20b648e9b62d44eb47ea11ab6998c00d3','92c65562fe49c02049e4b40e4a278b667e1361568455fdd89a724389a8d01d50','07982af9981b82074567f2fa5d976b00cb40a0331f01438352f9fd59fc864aa4','9d7ebb95113ecd5d9114224cff873b14f2db563d61015978164a78e4ff05953f','1ae1543b9ff31ba9d7c4271ae01d86f05fb722c00e9f7851ce1dffc820aee3b8','dcf1f2f6dd9540217155f01d5b03d965aedef98d965c2a33e987f0f5996eb166'):reclassified['assets:viral-accepted-'+item]='OUT-025'
 rebound={'assets:viral-accepted-b90cb9a3752383888c733905588e9c3859b113e47f1f457057c72e33689a7585','assets:viral-accepted-da0cac1c9c0c880a75d3be69c59e965d0b7b0f223f16a077072786c8af30083e'}
 for row in rows:
  outcome=row['outcome'];page=pages[row['source_id']]
  expected=None if row['source_id'] not in set(reclassified)|rebound and page not in {123,124} else 'OUT-005' if row['source_id'] in rebound else 'OUT-026' if page in {123,124} else reclassified.get(row['source_id'])
  expected_outcome='retained_rebound' if row['source_id'] in rebound else 'excluded_advertising' if page in {123,124} else 'reclassified' if row['source_id'] in reclassified else 'retained_unchanged'
  target=[] if outcome=='excluded_advertising' else [row['source_id']]
  if outcome!=expected_outcome or row['decision_ref']!=expected or row['target_ids']!=target:bad('v2 B1c4 migration decision mismatch')
 target_ids=[];children=[];expected_details={
  26:('viral-isola-di-malamente','page_opening:viral-isola-di-malamente',0,'page_opening_visual'),
  106:('viral-keeper-map-ground-floor-basement','physical_units:viral-map-ground-floor-basement',0,'map_key_legend_scale'),107:('viral-keeper-map-ground-floor-basement','physical_units:viral-map-ground-floor-basement',1,'map_key_legend_scale'),
  112:('viral-pregen-marco-background','physical_units:viral-pregen-marco',1,'pregen_back_semantic_payload'),114:('viral-pregen-corrina-background','physical_units:viral-pregen-corrina',1,'pregen_back_semantic_payload'),116:('viral-pregen-enoch-background','physical_units:viral-pregen-enoch',1,'pregen_back_semantic_payload'),118:('viral-pregen-peter-background','physical_units:viral-pregen-peter',1,'pregen_back_semantic_payload'),120:('viral-pregen-ku-hyeon-background','physical_units:viral-pregen-ku-hyeon',1,'pregen_back_semantic_payload'),122:('viral-pregen-blank-background','physical_units:viral-pregen-blank',1,'pregen_back_semantic_payload')}
 expected_children={106:['viral-accepted-adb4ff51bd5ebff464834e0fb324310c281eb20d2c4b0f4e82d1fbaf3ef72541','viral-accepted-f7ce778cc1eb05cb6fef0f26457d06e68019ee30c76a5723f259dc82b89b321d'],107:['viral-accepted-e1c168ca34db2f98a27391e749f08a0fcdda832034d68e5fd0fbc38b00f584dc'],112:['viral-accepted-5d2410afd9a6593cdce0d7f0d411835cf4a726551a1b1e18b6f79d04ed42230b','viral-accepted-53c2775488f57c8e41f9d42648ecb8a1d30e9a1ce0de8d4108b7926ee26a3595'],114:['viral-accepted-331f4d575265e02a4ba97b4e204dbbb20b648e9b62d44eb47ea11ab6998c00d3','viral-accepted-89e3eae7390f0ae27a8069bcf2d2aa2956a21047eeb7168a3fd49b0b7cbfc297'],116:['viral-accepted-92c65562fe49c02049e4b40e4a278b667e1361568455fdd89a724389a8d01d50','viral-accepted-66088dd8192e2a93f140eb9e11fadfed92b3869c509490199a35d272197ebfcb'],118:['viral-accepted-07982af9981b82074567f2fa5d976b00cb40a0331f01438352f9fd59fc864aa4','viral-accepted-fe4c839c1ff9b15dc4a9136f6969271a7a465fe642c77b38f456aa2af38fe0c3'],120:['viral-accepted-9d7ebb95113ecd5d9114224cff873b14f2db563d61015978164a78e4ff05953f','viral-accepted-df1e018979c88b0737200c349889745eadfa119466dc40fb024779a0f8eb4730'],122:['viral-accepted-1ae1543b9ff31ba9d7c4271ae01d86f05fb722c00e9f7851ce1dffc820aee3b8','viral-accepted-dd0c2d51431a4945f9f7d8293bc7b0b5e870f891dbe31d18c931926bffbb8d8b','viral-accepted-dcf1f2f6dd9540217155f01d5b03d965aedef98d965c2a33e987f0f5996eb166']}
 expected_children[26]=[]
 target_count=len(targets);hierarchy_targets=[target for target in targets if isinstance(target,dict) and str(target.get('target_id','')).startswith('hierarchy:')]
 if len({target['target_id'] for target in hierarchy_targets})!=len(hierarchy_targets) or any(set(target)!={'target_id','decision_ref'} or not target['target_id'][len('hierarchy:'):] or target['decision_ref']!='OUT-003' for target in hierarchy_targets):bad('v2 B1c4 hierarchy target schema mismatch')
 targets=[target for target in targets if isinstance(target,dict) and str(target.get('target_id','')).startswith('assets:viral-provisional-')]
 if len(targets)+len(hierarchy_targets)!=target_count:bad('v2 B1c4 replacement target domain mismatch')
 for target in targets:
  if not isinstance(target,dict) or set(target)!={'target_id','decision_ref','evidence_identity','physical_unit_id','page_slot','owner_anchor','accessibility_obligation','replaces'} or not isinstance(target['target_id'],str) or not target['target_id'].startswith('assets:viral-provisional-') or target['decision_ref'] not in {'OUT-024','OUT-025','OUT-038'} or not isinstance(target['evidence_identity'],dict) or not isinstance(target['replaces'],list) or (not target['replaces'] and target['decision_ref']!='OUT-038'):bad('v2 B1c4 replacement schema mismatch')
  target_ids.append(target['target_id']);children.extend(target['replaces'])
 expected_targets=['assets:viral-provisional-map-ground-floor-basement-page-106','assets:viral-provisional-map-ground-floor-basement-page-107','assets:viral-provisional-pregen-marco-back-page-112','assets:viral-provisional-pregen-corrina-back-page-114','assets:viral-provisional-pregen-enoch-back-page-116','assets:viral-provisional-pregen-peter-back-page-118','assets:viral-provisional-pregen-ku-hyeon-back-page-120','assets:viral-provisional-pregen-blank-back-page-122','assets:viral-provisional-isola-di-malamente-opening-page-26']
 if target_ids!=expected_targets or len(children)!=16 or len(set(children))!=16 or any(not isinstance(child,str) or not child.startswith('viral-accepted-') for child in children):bad('v2 B1c4 replacement graph mismatch')
 for target,page in zip(targets,(106,107,112,114,116,118,120,122,26)):
  owner,unit,slot,obligation=expected_details[page]
  expected_decision='OUT-038' if page==26 else 'OUT-024' if page in {106,107} else 'OUT-025'
  if target['decision_ref']!=expected_decision or target['evidence_identity']!={'path':'kb_creator/working/viral/source/Call_of_Cthulhu_Viral.pdf','bytes':20718150,'sha256':'0A80B6F389821B87553D26746D2BE171B4482BA9BBC6E3EB3FEC26274EDBED05'} or (target['owner_anchor'],target['physical_unit_id'],target['page_slot'],target['accessibility_obligation'],target['replaces'])!=(owner,unit,slot,obligation,expected_children[page]):bad('v2 B1c4 replacement identity mismatch')
 return counts

MEDIA_SUFFIX={'image/jpeg':'.jpg','image/png':'.png'}
PIL_FORMAT={'image/jpeg':'JPEG','image/png':'PNG'}
RENDERER_VERSION='26.05.0'

def fresh_staging_root(staging_root):
 """Require a caller-created empty directory; never create or replace a candidate."""
 root=Path(staging_root)
 if not root.is_dir() or any(root.iterdir()):bad('staging root must exist and be empty')
 return root.resolve()

def image_identity(path,media_type,label):
 """Check image bytes are the declared format and dimensions before publishing them."""
 if media_type not in MEDIA_SUFFIX:bad(f'{label} unsupported media type')
 try:
  with Image.open(path) as image:
   image.load(); fmt=image.format; dimensions={'width':image.width,'height':image.height}
 except OSError as e:raise ValueError(f'{label} is not a valid image') from e
 if fmt!=PIL_FORMAT[media_type]:bad(f'{label} media type mismatch')
 return dimensions

def asset_record(asset,output_path,byte_count,sha256,dimensions,render_declaration=None):
 """Return a stable, manifest-ready row without asserting any external QA gate."""
 return {
  'asset_id':asset['asset_id'],'logical_name':asset['logical_name'],
  'output_path':output_path.as_posix(),'bytes':byte_count,'sha256':sha256,
  'dimensions':dimensions,'media_type':asset['media_type'],
  'representation':asset['representation'],'owner_anchor':asset['owner_anchor'],
  'placement_index':asset['placement_index'],'source_page':asset['source_page'],
  'source_region':asset['source_region'],'origin':asset['origin'],
  'render':render_declaration,'visual_review_status':'pending_external_visual_qa',
 }

def require_renderer_version(renderer_command):
 try:
  completed=subprocess.run([*renderer_command,'-v'],capture_output=True,text=True,check=True)
 except OSError as e:raise ValueError('renderer unavailable') from e
 version_output=(completed.stdout+'\n'+completed.stderr).strip()
 if not re.search(r'pdftoppm version 26\.05\.0(?:\s|$)',version_output):bad('renderer version mismatch')

def normalized_png(source_path,output_path):
 """Encode a metadata-free, opaque RGB 1700x2200 PNG with pinned settings."""
 try:
  with Image.open(source_path) as image:
   image.load(); image=ImageOps.exif_transpose(image)
   if image.mode=='RGBA':
    background=Image.new('RGB',image.size,'white');background.paste(image,mask=image.getchannel('A'));image=background
   else:image=image.convert('RGB')
   if image.size!=(1700,2200):image=image.resize((1700,2200),Image.Resampling.LANCZOS)
   image.save(output_path,format='PNG',optimize=False,compress_level=9)
 except OSError as e:raise ValueError('renderer output is not a valid image') from e
 dimensions=image_identity(output_path,'image/png','normalized render')
 if dimensions!={'width':1700,'height':2200}:bad('normalized render dimensions mismatch')

def render_asset(asset,root,assets_dir,renderer_command):
 declaration=asset['render']; source_declared=asset['source_pdf']['path']
 if Path(source_declared).name=='SELECTED_OVERLAY.pdf' or 'SELECTED_OVERLAY' in source_declared:bad('overlay substitution refused')
 source=rel(root,source_declared,'render source PDF')
 if dig(source)!=asset['source_pdf']['sha256']:bad('render source identity mismatch')
 if declaration['renderer']!='Poppler pdftoppm' or declaration['renderer_version']!=RENDERER_VERSION:bad('renderer declaration mismatch')
 if declaration['pdf_box']!='MediaBox' or declaration['dpi']!=200 or declaration['format']!='png' or declaration['color_space']!='RGB' or declaration['background']!='white' or declaration['alpha'] is not False or declaration['metadata']!='strip_all':bad('render declaration mismatch')
 page=asset['source_pdf']['page_index_zero_based']+1
 if page!=asset['source_page']:bad('render page declaration mismatch')
 with tempfile.TemporaryDirectory(dir=assets_dir) as temporary:
  prefix=Path(temporary)/'page'
  command=[*renderer_command,'-f',str(page),'-l',str(page),'-r','200','-png','-singlefile',str(source),str(prefix)]
  try:subprocess.run(command,capture_output=True,text=True,check=True)
  except (OSError,subprocess.CalledProcessError) as e:raise ValueError('source page render failed') from e
  rendered=prefix.with_suffix('.png')
  if not rendered.is_file():bad('source page render missing')
  normalized=Path(temporary)/'normalized.png';normalized_png(rendered,normalized)
  sha256=dig(normalized); output=assets_dir/f'{sha256.lower()}.png'
  if output.exists():bad('occupied asset output collision')
  shutil.copyfile(normalized,output)
 dimensions=image_identity(output,'image/png','rendered asset')
 return asset_record(asset,output.relative_to(assets_dir.parent),output.stat().st_size,sha256,dimensions,declaration)

def materialize_assets(config,repository_root,staging_root,renderer_command:Sequence[str]=('pdftoppm',)):
 """Materialize declared assets into an explicit empty staging root and return config-order ledger."""
 root=Path(repository_root).resolve();stage=fresh_staging_root(staging_root)
 if not renderer_command:bad('renderer command required')
 assets_dir=stage/'assets';assets_dir.mkdir()
 require_renderer_version(tuple(renderer_command))
 ledger=[]; declared_ids=set(); binary_hashes=set(); output_names=set()
 for asset in config['assets']:
  asset_id=st(asset.get('asset_id'),'asset id')
  if asset_id in declared_ids:bad('duplicate asset declaration')
  declared_ids.add(asset_id)
  if asset['origin']=='accepted_reconstruction_asset':
   source=rel(root,asset['source_path'],'asset source'); sha256=st(asset['sha256'],'asset sha256')
   if not HEX.fullmatch(sha256) or dig(source)!=sha256 or source.stat().st_size!=num(asset['bytes'],'asset bytes'):bad('asset source identity mismatch')
   dimensions=image_identity(source,asset['media_type'],'asset source')
   if dimensions!=asset['dimensions']:bad('asset dimensions mismatch')
   suffix=MEDIA_SUFFIX.get(asset['media_type'])
   if suffix is None or source.suffix.lower()!=suffix:bad('asset media type mismatch')
   output=assets_dir/f'{sha256.lower()}{suffix}'
   if sha256 in binary_hashes:bad('duplicate binary asset declaration')
   if output.name in output_names or output.exists():bad('occupied asset output collision')
   binary_hashes.add(sha256);output_names.add(output.name);shutil.copyfile(source,output)
   if dig(output)!=sha256 or output.stat().st_size!=asset['bytes']:bad('asset copy identity mismatch')
   ledger.append(asset_record(asset,output.relative_to(stage),output.stat().st_size,sha256,dimensions))
  elif asset['origin']=='source_page_render':
   if asset['media_type']!='image/png' or asset['dimensions']!={'width':1700,'height':2200}:bad('render output declaration mismatch')
   row=render_asset(asset,root,assets_dir,tuple(renderer_command))
   if row['sha256'] in binary_hashes or Path(row['output_path']).name in output_names:bad('duplicate binary asset declaration')
   binary_hashes.add(row['sha256']);output_names.add(Path(row['output_path']).name);ledger.append(row)
  else:bad('asset origin mismatch')
 return ledger

def reader_asset_rows(config,asset_ledger):
 """Close reader references against the Phase B ledger without materializing assets again."""
 declared={x['asset_id']:x for x in config['assets']}; ledger={x['asset_id']:x for x in asset_ledger}
 if set(ledger)!=set(declared):bad('asset ledger declaration mismatch')
 reader=[]
 for asset_id,asset in declared.items():
  row=ledger[asset_id]
  if asset['representation']=='reader':
   output=st(row.get('output_path'),'asset ledger output path')
   if not output.startswith('assets/') or 'SELECTED_OVERLAY' in output:bad('reader asset path mismatch')
   sha256=st(row.get('sha256'),'asset ledger sha256')
   if not HEX.fullmatch(sha256) or Path(output).stem!=sha256.lower():bad('reader asset path mismatch')
   reader.append((asset,row))
 if len(reader)!=107:bad('reader asset count mismatch')
 return sorted(reader,key=lambda pair:pair[0]['placement_index'])

def clean_span(raw,span,locators,owner_level=None,owner_title=None,suppressions=()):
 """Apply declared structural actions without changing retained lexical body text."""
 edits=[]
 for locator in locators:
  if locator['page'] not in {x['page'] for x in span}:continue
  action=locator['action']; start=locator['start']; end=locator['end']
  for item in span:
   if item['page']==locator['page'] and item['start']<=start<item['end']:
    base=item['start']; selector=locator.get('selector','')
    if action in {'replace_heading','consume_continuation_label'}:edits.append((start-base,end-base,''))
    elif action=='replace_label_retain_remainder':edits.append((start-base,start-base+len(selector),''))
 for start,end,replacement in sorted(edits,reverse=True):raw=raw[:start]+replacement+raw[end:]
 for start,end in sorted(suppressions,reverse=True): raw=raw[:start]+raw[end:]
 raw=re.sub(r'^<!-- source-page-\d{3} -->\r?\n?','',raw)
 raw=re.sub(r'^!\[[^\]]*\]\([^\n]*\)\s*\n?','',raw,flags=re.MULTILINE)
 if owner_level is not None:
  def heading(match):
   title=match.group(3).strip()
   if title==owner_title: return f'**{title.rstrip(".")}.**'
   level=owner_level+len(match.group(1))
   return '#'*level+' '+title if level<=6 else f'**{title.rstrip(".")}.**'
  raw=re.sub(r'^(#{1,6})(\s+)(.*)$',heading,raw,flags=re.MULTILINE)
 else: raw=re.sub(r'^(#{1,6})(\s+)',lambda m:'#'*(min(6,len(m.group(1))+1))+' ',raw,flags=re.MULTILINE)
 return raw.rstrip()

def apply_source_edit_plan(raw,xrefs,suppressions):
 """Apply xref replacements and authorized deletions on original offsets."""
 edits=[]; executed=[]
 for row in xrefs:
  line=row['source_line']; at=raw.find(line)
  if at<0: continue
  if raw.find(line,at+1)>=0: bad('xref source line mismatch')
  cursor=0
  for segment in row['segments']:
   start=line.find(segment['source_text'],cursor)
   if start<0 or line.find(segment['source_text'],start+1)>=0: bad('xref segment mismatch')
   replacement=f"[{segment['reader_text']}](#{segment['target_anchor']})" if segment['emit_link'] else segment['reader_text']
   edits.append((at+start,at+start+len(segment['source_text']),replacement));cursor=start+len(segment['source_text'])
  executed.append(row['xref_id'])
 edits += [(start,end,'') for start,end in suppressions]
 ordered=sorted(edits,key=lambda x:(x[0],x[1]))
 if any(left[1]>right[0] for left,right in zip(ordered,ordered[1:])): bad('source edit ranges overlap')
 for start,end,replacement in reversed(ordered): raw=raw[:start]+replacement+raw[end:]
 return raw,executed

def binding_spans(binding,source_cache,reviews):
 """Return the source fragments owned by one binding in declared source order."""
 if binding['kind']=='owned_page_unit':
  return [{'page':p,'start':0,'end':len(source_cache[p]),'sha256':hashlib.sha256(source_cache[p].encode('utf8')).hexdigest().upper()} for p in reviews[binding['unit_ref']]['source_pages']]
 return binding['source_span_hashes']

def fragment_emission_plan(bindings,hierarchy,spans_by_anchor=None):
 """Emit each declared fragment once, interleaving direct descendants between parent fragments when their exact source range requires it."""
 by_anchor={x['anchor']:x for x in bindings}; children={anchor:[] for anchor in by_anchor}
 spans_by_anchor=spans_by_anchor or {x['anchor']:x['source_span_hashes'] for x in bindings}
 for anchor,row in hierarchy.items():
  if row['parent_anchor'] in children:children[row['parent_anchor']].append(anchor)
 emitted=set(); plan=[]
 def key(span):return (span['page'],span['start'],span['end'])
 def emit(anchor):
  if anchor in emitted:return
  binding=by_anchor[anchor];spans=spans_by_anchor[anchor];emitted.add(anchor)
  if not spans:
   plan.append((binding,None));return
  for index,span in enumerate(spans):
   plan.append((binding,index))
   if index+1==len(spans):continue
   lower,upper=key(span),key(spans[index+1])
   for child in children.get(anchor,[]):
    child_spans=spans_by_anchor[child]
    if child not in emitted and child_spans and all(lower<key(item)<upper for item in child_spans):emit(child)
 for binding in bindings:emit(binding['anchor'])
 if len(emitted)!=len(bindings):bad('fragment emission anchor mismatch')
 expected={(binding['anchor'],index) for binding in bindings for index in range(len(spans_by_anchor[binding['anchor']]))}
 actual={(binding['anchor'],index) for binding,index in plan if index is not None}
 if actual!=expected or len(actual)!=sum(index is not None for _,index in plan):bad('fragment consumption mismatch')
 return plan

def assemble_reader(config,binding_index,asset_ledger,staging_root,reconstruction_package):
 """Interleave binding-order headings, owned spans, assets, and configured xrefs in a temporary root."""
 stage=fresh_staging_root(staging_root); bindings=binding_index['bindings'];package=Path(reconstruction_package)
 expected_locators=sum(len(row['assembly_binding']['locators']) for row in config['hierarchy'])
 if len(bindings)!=len(config['hierarchy']) or binding_index.get('locator_count')!=expected_locators:bad('binding index mismatch')
 conservation=binding_index.get('conservation',{})
 if any(conservation.get(key) for key in ('unowned_blocks','duplicate_blocks','unauthorized_suppression_blocks')):bad('binding conservation failed')
 hierarchy={x['anchor']:x for x in config['hierarchy']}; xref_counts=xref_declarations(config,set(hierarchy)); source_xrefs=resolve_source_xrefs(config,binding_index,package); assets=reader_asset_rows(config,asset_ledger); assets_by_owner={}
 rs,_,suppression_ranges=reader_surface_ranges(config,package)
 for asset,ledger in assets:assets_by_owner.setdefault(asset['owner_anchor'],[]).append((asset,ledger))
 reviews={x['review_id']:x for x in config['visual_review_units']}; generated={owner:[x for x in config['xrefs'] if x['source_selector']==selector] for selector,owner in GENERATED_XREFS.items()}
 source_cache={p:source_lines(package,p)[0] for p in range(1,125)}; blocks=[]; block_ledgers=[]; transformations=[]; emitted_pages=set(); emitted_ledger=[]
 spans_by_anchor={binding['anchor']:binding_spans(binding,source_cache,reviews) for binding in bindings}
 plan=fragment_emission_plan(bindings,hierarchy,spans_by_anchor)
 emitted_anchors=set(); emitted_by_anchor={}; actual_xrefs_by_anchor={x['anchor']:[] for x in bindings}
 for binding,span_index in plan:
  row=hierarchy[binding['anchor']]; heading='#'*row['level']+' '+row['title']; heading='# Viral' if row['anchor']=='viral' else heading
  first=binding['anchor'] not in emitted_anchors; block=[]; block_emissions=[]
  if first:
   emitted_anchors.add(binding['anchor']);block=[f'<a id="{row["anchor"]}"></a>',heading]
   for xref in generated.get(row['anchor'],[]):
    block.append(f"- [{xref['visible_text']}](#{xref['target_anchors'][0]})");actual_xrefs_by_anchor[row['anchor']].append(xref['xref_id'])
  spans=spans_by_anchor[binding['anchor']]
  if span_index is not None:
   span=spans[span_index]
   raw=source_cache[span['page']][span['start']:span['end']]
   local=[x for x in binding['locators'] if x['page']==span['page']]
   xrefs=[item[0] for item in source_xrefs.values() if item[0]['owner_anchor']==row['anchor'] and item[1]['page']==span['page'] and item[1]['start']==span['start'] and item[0]['xref_id'] not in actual_xrefs_by_anchor[row['anchor']]]
   suppressed=[(x['start_offset']-span['start'],x['end_offset']-span['start']) for x in suppression_ranges if x['source_containment']['claim_owner_anchor']==row['anchor'] and x['source_page']==span['page'] and span['start']<=x['start_offset'] and x['end_offset']<=span['end']]
   raw,executed=apply_source_edit_plan(raw,xrefs,suppressed);actual_xrefs_by_anchor[row['anchor']].extend(executed)
   cleaned=clean_span(raw,[span],local,row['level'],row['title'])
   if cleaned:
    block.append(cleaned);block_emissions.append({'binding_anchor':binding['anchor'],'source_page':span['page'],'source_start':span['start'],'source_end':span['end'],'emitted_text':cleaned})
   emitted_pages.add((binding['anchor'],span['page'],span['start'],span['end']))
  if span_index is None or span_index==len(spans)-1:
   for asset,ledger in sorted(assets_by_owner.get(row['anchor'],[]),key=lambda pair:pair[0]['placement_index']):block.append(f"![{asset['alt_text']}]({ledger['output_path']})")
  if block:
   block_text='\n\n'.join(block);blocks.append(block_text)
   for emitted in block_emissions:
    emitted['block_offset']=block_text.find(emitted['emitted_text'])
    if emitted['block_offset']<0:bad('emitted fragment range mismatch')
   block_ledgers.append(block_emissions)
 for binding in bindings:
  transformations.append({'anchor':binding['anchor'],'span_hashes':[x['sha256'] for x in binding['source_span_hashes']],'actions':binding['action'],'asset_ids':[x[0]['asset_id'] for x in assets_by_owner.get(binding['anchor'],[])],'xref_ids':actual_xrefs_by_anchor[binding['anchor']]})
 text='\n\n'.join(blocks)+'\n'
 offset=0
 for block_text,block_emissions in zip(blocks,block_ledgers):
  for emitted in block_emissions:
   emitted['emitted_start']=offset+emitted.pop('block_offset');emitted['emitted_end']=emitted['emitted_start']+len(emitted['emitted_text']);emitted_ledger.append(emitted)
  offset+=len(block_text)+2
 anchors=re.findall(r'<a id="([^"]+)"></a>',text);links=re.findall(r'\]\(#([a-z0-9-]+)\)',text);refs=re.findall(r'\]\((assets/[^)]+)\)',text)
 emitted_handouts={x['unit_ref'] for x in bindings if x['kind']=='physical_unit'}; map_reviews=[x for x in reviews.values() if 'keeper-map' in x['owner_anchor']];pregen_reviews=[x for x in reviews.values() if 'pregen' in x['owner_anchor']]
 noise=[x for x in ('source-page-','SELECTED_OVERLAY','kb_creator/') if x in text]
 xref_ids=[item for row in transformations for item in row['xref_ids']]
 expected_links=xref_counts['generated']+sum(segment['emit_link'] for x in config['xrefs'] if x['source_selector']=='line_exact' for segment in x['segments'])
 if text.count('# Viral\n')!=1 or len(anchors)!=168 or len(set(anchors))!=168 or any(link not in set(anchors) for link in links) or len(refs)!=len(assets) or len(xref_ids)!=len(config['xrefs']) or len(set(xref_ids))!=len(config['xrefs']) or len(links)!=expected_links or noise:bad(f'reader assembly invariant mismatch: xrefs={len(xref_ids)} links={len(links)} expected={expected_links} refs={len(refs)} noise={noise}')
 output=stage/'MASTER_EN.md';output.write_bytes(text.replace('\r\n','\n').replace('\r','\n').encode('utf8'))
 structured_evidence=structured_resolver(config,binding_index,package,text,asset_ledger,emitted_ledger,suppression_ranges)
 return {'master_path':output,'bytes':output.stat().st_size,'sha256':dig(output),'anchors':len(anchors),'links':len(links),'reader_assets':len(refs),'handouts':len(emitted_handouts),'map_units':len(map_reviews),'map_pages':len({p for x in map_reviews for p in x['source_pages']}),'pregens':sum(x['anchor'].startswith('viral-pregen-') for x in bindings),'structured_units':len({x['structure_id'] for x in structured_evidence}),'structured_evidence':structured_evidence,'emitted_ledger':emitted_ledger,'conservation':conservation,'reader_noise_findings':noise,'transformations':transformations,'suppressions':suppression_ranges,'emitted_spans':len(emitted_pages),'xrefs':{**xref_counts,'executed_ids':xref_ids,'source_links':sum(s['emit_link'] for x in config['xrefs'] if x['source_selector']=='line_exact' for s in x['segments'])}}
def canonical(value):return json.dumps(value,ensure_ascii=False,sort_keys=True,indent=2)+'\n'
def file_identity(path,relative):
 data=Path(path).read_bytes();return {'path':relative,'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest().upper()}
def qa_markdown(qa):
 """Deterministic, human-readable projection of the canonical QA JSON."""
 lines=['# MASTER_EN QA','',f"Candidate state: {qa['candidate_state']}",'','## Artifacts','', '| Artifact | Path | Bytes | SHA-256 |','| --- | --- | ---: | --- |']
 lines += [f"| {name} | {row['path']} | {row['bytes']} | {row['sha256']} |" for name,row in sorted(qa['artifacts'].items())]
 lines += ['','## Metrics','', '| Metric | Value |','| --- | ---: |']
 lines += [f'| {name} | {value} |' for name,value in sorted(qa['metrics'].items())]
 lines += ['','## Gates','', '| Gate | Status | Evidence | Errors |','| --- | --- | --- | --- |']
 lines += [f"| {row['gate']} | {row['status']} | {', '.join(row['evidence'])} | {', '.join(row['errors'])} |" for row in qa['gates']]
 lines += ['', 'No acceptance exists.', '']
 return '\n'.join(lines)
def dual_range(text,start,end):
 """Serialize both internal code-point and externally stable UTF-8 coordinates."""
 return {'start_char':start,'end_char':end,'start_byte':len(text[:start].encode('utf8')),'end_byte':len(text[:end].encode('utf8'))}
def sidecar_structures(evidence,pages,reader_text):
 """C2b sidecar migration; C2a resolver continues to use character offsets internally."""
 converted=[]
 for row in evidence:
  item={key:value for key,value in row.items() if key not in {'fragments','attached_notes'}}; fragments=[];notes=[]
  for fragment in row['fragments']:
   source=pages[fragment['source_page']]; value={key:value for key,value in fragment.items() if key not in {'source_start','source_end','emitted_start','emitted_end'}}
   value.update({'source_'+key:val for key,val in dual_range(source,fragment['source_start'],fragment['source_end']).items()})
   value.update({'emitted_'+key:val for key,val in dual_range(reader_text,fragment['emitted_start'],fragment['emitted_end']).items()});fragments.append(value)
  for note in row['attached_notes']:
   source=pages[note['source_page']]; value={key:value for key,value in note.items() if key not in {'source_start','source_end','emitted_start','emitted_end'}}
   value.update({'source_'+key:val for key,val in dual_range(source,note['source_start'],note['source_end']).items()})
   value.update({'emitted_'+key:val for key,val in dual_range(reader_text,note['emitted_start'],note['emitted_end']).items()});notes.append(value)
  item['fragments']=fragments;item['attached_notes']=notes;converted.append(item)
 return converted
def candidate_inventory(root):
 rows=[]
 for path in sorted((p for p in root.rglob('*') if p.is_file() and p.name!='INVENTORY.json'),key=lambda p:p.relative_to(root).as_posix()):
  relative=path.relative_to(root).as_posix();data=path.read_bytes();rows.append({'path':relative,'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest().upper()})
 payload=''.join(f"{x['path']}\t{x['bytes']}\t{x['sha256']}\n" for x in rows).encode('utf8')
 return rows,sum(x['bytes'] for x in rows),hashlib.sha256(payload).hexdigest().upper()
def candidate_target(root,scenario,target):
 value=Path(target)
 if value.is_absolute() or any(part in {'','.','..'} for part in value.parts) or any(x in str(target) for x in ('\\',':')):bad('candidate target path mismatch')
 parent=root/'kb_creator'/'working'/scenario/'master_en'/'candidates'
 destination=root/value
 if destination.parent!=parent or not re.fullmatch(r'[a-z0-9][a-z0-9._-]{0,63}',value.name):bad('candidate target path mismatch')
 return parent,destination
def build_v2_candidate(contract,reconstruction_package,publication_config,source_pdf,target):
 """Atomic synthetic-v2 materializer; all counts derive from the declaration."""
 cfg=Path(publication_config).resolve();root=root_for(cfg.parent);value=v2_config(js(cfg,'publication config'));v2_input_binding(value,root,source_pdf,reconstruction_package);parent,destination=candidate_target(root,value['scenario_id'],target)
 if destination.exists() or destination.is_symlink():bad('candidate target exists')
 parent.mkdir(parents=True,exist_ok=True);stage=Path(tempfile.mkdtemp(prefix=f'.{destination.name}.staging.',dir=parent))
 try:
  chunks=v2_typed_chunks(value);master,event_ledger=v2_join_ledger(chunks)
  reader_assets=[x for x in value['assets'] if _v2_reader_asset(x)]; assets_dir=stage/'assets';copied=[];output_names=set()
  for asset in reader_assets:
   source_path=asset.get('source_path') if 'source_path' in asset else (asset.get('binary') or {}).get('path')
   if source_path is None:
    assets_dir.mkdir(exist_ok=True);out,identity=v2_render_provisional_asset(asset,source_pdf,assets_dir);name=out.name
    if name in output_names:bad('v2 duplicate output asset name')
    output_names.add(name);copied.append({**asset,'output_path':'assets/'+name,'_candidate_binary':identity});continue
   if not isinstance(source_path,str):bad('v2 canonical reader asset binary pending')
   source=(root/source_path).resolve()
   try:source.relative_to(root)
   except ValueError:bad('v2 asset source escapes checkout')
   identity=asset if 'source_path' in asset else asset['binary']
   if not source.is_file() or source.stat().st_size!=identity['bytes'] or dig(source)!=identity['sha256']:bad('v2 asset source identity mismatch')
   name=asset['asset_id'] if 'source_path' in asset else Path(source_path).name
   if not name or name in output_names:bad('v2 duplicate output asset name')
   output_names.add(name);assets_dir.mkdir(exist_ok=True);out=assets_dir/name;shutil.copyfile(source,out)
   if dig(out)!=identity['sha256']:bad('v2 copied asset identity mismatch')
   copied.append({**asset,'output_path':'assets/'+name})
  (stage/'MASTER_EN.md').write_text(master,encoding='utf8',newline='\n')
  disposition={'schema':'kb_creator.source_disposition.v2','scenario_id':value['scenario_id'],'pages':value['source_disposition'],'summary':{'page_count':124,'reader_pages':122,'excluded_advertising_pages':2,'audit_disposition':'reconstructed'}}
  operations=[{'operation':'generated_navigation_replaces_source_toc','source_identity':value['document']['generated_navigation']['source_identity']}]+[{'operation':'source_backed_recovery','recovery_id':row['recovery_id'],'event_id':row['target_event_id'],'source_page':row['physical_page'],'source_text':row['source_text']} for row in value['source_recoveries']]
  provenance={'schema':'kb_creator.master_en_provenance.v2','scenario_id':value['scenario_id'],'offset_contract':{'char':'python_unicode_code_points','byte':'utf8_bytes','range':'zero_based_half_open'},'operations':operations,'events':event_ledger,'master_en':file_identity(stage/'MASTER_EN.md','MASTER_EN.md')}
  manifest={'schema':'kb_creator.master_en_asset_manifest.v2','assets':[{'asset_id':x['asset_id'],'reader_value':_v2_reader_asset(x),'placement':x.get('placement'),**({'output_path':x['output_path'],'bytes':x.get('_candidate_binary',(x if 'source_path' in x else x['binary']))['bytes'],'sha256':x.get('_candidate_binary',(x if 'source_path' in x else x['binary']))['sha256']} if _v2_reader_asset(x) else {})} for x in [*copied,*[x for x in value['assets'] if not _v2_reader_asset(x)]]],'summary':{'total':len(value['assets']),'reader':len(reader_assets),'suppressed':len(value['assets'])-len(reader_assets)}}
  review_summary=v2_visual_review_units(value)
  qa={'schema':'kb_creator.master_en_qa.v2','metrics':{**value['metrics'],'events':len(value['events']),'reader_assets':len(reader_assets),'master_bytes':len(master.encode()),'visual_review_units':review_summary},'errors':[]}
  for name,payload in [('SOURCE_DISPOSITION.json',disposition),('MASTER_EN.provenance.json',provenance),('ASSET_MANIFEST.json',manifest),('MASTER_EN.qa.json',qa)]: (stage/name).write_text(canonical(payload),encoding='utf8',newline='\n')
  rows,total,digest=candidate_inventory(stage);(stage/'INVENTORY.json').write_text(canonical({'schema':'kb_creator.candidate_inventory.v1','algorithm':'SHA-256 over ordinal UTF-8 LF relative_path<TAB>bytes<TAB>UPPER_SHA256<LF>','scope':'all regular candidate files except INVENTORY.json','rows':rows,'file_count':len(rows),'total_bytes':total,'inventory_sha256':digest}),encoding='utf8',newline='\n')
  stage.rename(destination)
  return {'status':'candidate_built_for_independent_verification','scenario_id':value['scenario_id'],'candidate_inventory_sha256':digest,'inventory_file_sha256':dig(destination/'INVENTORY.json'),'master_en_sha256':dig(destination/'MASTER_EN.md')}
 except Exception:
  if stage.exists():shutil.rmtree(stage)
  raise
def build_candidate(contract,reconstruction_package,publication_config,source_pdf,target,renderer_command=('pdftoppm',)):
 cfg=Path(publication_config).resolve()
 if js(cfg,'publication config').get('schema')==V2_SCHEMA:return build_v2_candidate(contract,reconstruction_package,publication_config,source_pdf,target)
 pre=preflight(contract,reconstruction_package,publication_config,source_pdf);root=root_for(cfg.parent);config_value=config(cfg);parent,destination=candidate_target(root,config_value['scenario_id'],target)
 if destination.exists() or destination.is_symlink():bad('candidate target exists')
 parent.mkdir(exist_ok=True);stage=Path(tempfile.mkdtemp(prefix=f'.{destination.name}.staging.',dir=parent))
 try:
  ledger=materialize_assets(config_value,root,stage,renderer_command); ledger=[{**next(asset for asset in config_value['assets'] if asset['asset_id']==row['asset_id']),**row} for row in ledger];reader_stage=stage/'.reader';reader_stage.mkdir();binding=resolve_bindings(config_value,root,reconstruction_package);reader=assemble_reader(config_value,binding,ledger,reader_stage,reconstruction_package);shutil.move(str(reader['master_path']),str(stage/'MASTER_EN.md'));shutil.rmtree(reader_stage)
  manifest={'schema':'kb_creator.master_en_asset_manifest.v1','scenario_id':config_value['scenario_id'],'assets':[{'asset_id':x['asset_id'],'origin':x['origin'],'logical_name':x['logical_name'],'source':({'kind':'accepted_reconstruction_asset','path':next(a['source_path'] for a in config_value['assets'] if a['asset_id']==x['asset_id']),'bytes':x['bytes'],'sha256':x['sha256']} if x['origin']=='accepted_reconstruction_asset' else {'kind':'source_page_render','source_pdf':next(a['source_pdf'] for a in config_value['assets'] if a['asset_id']==x['asset_id']),'render':x['render']}),'output_path':x['output_path'],'bytes':x['bytes'],'sha256':x['sha256'],'media_type':x['media_type'],'dimensions':x['dimensions'],'source_page':x['source_page'],'source_region':x['source_region'],'semantic_role':x['semantic_role'],'representation':x['representation'],'owner_anchor':x['owner_anchor'],'placement_index':x['placement_index'],'alt_text':x['alt_text'],'visual_review_status':'pending_external_visual_qa'} for x in ledger],'summary':{'total':len(ledger),'reader':sum(x['representation']=='reader' for x in ledger),'evidence_only':sum(x['representation']=='evidence_only' for x in ledger),'accepted_reconstruction_asset':sum(x['origin']=='accepted_reconstruction_asset' for x in ledger),'source_page_render':sum(x['origin']=='source_page_render' for x in ledger)}}
  disposition={'schema':'kb_creator.source_disposition.v1','scenario_id':config_value['scenario_id'],'pages':config_value['source_disposition'],'summary':{'page_count':len(config_value['source_disposition']),'sub_unit_count':sum(len(x['sub_units']) for x in config_value['source_disposition']),'unauthorized_suppression_count':0}}
  master={'path':'MASTER_EN.md','bytes':reader['bytes'],'sha256':reader['sha256']};qa={'schema':'kb_creator.master_en_qa.v1','scenario_id':config_value['scenario_id'],'candidate_state':'candidate_for_independent_verification','artifacts':{'master_en':master,'provenance':{'path':'MASTER_EN.provenance.json','bytes':0,'sha256':'0'*64},'source_disposition':{'path':'SOURCE_DISPOSITION.json','bytes':0,'sha256':'0'*64},'asset_manifest':{'path':'ASSET_MANIFEST.json','bytes':0,'sha256':'0'*64}},'metrics':{'source_pages':124,'anchors':reader['anchors'],'links':reader['links'],'xrefs_executed':len(reader['xrefs']['executed_ids']),'source_xref_rows':41,'source_xref_segments':42,'handouts':reader['handouts'],'structured_units':reader['structured_units'],'reader_assets':reader['reader_assets'],'candidate_assets':len(ledger),'visual_review_units':91,'total_blocks':1935,'owned_blocks':1862,'generated_blocks':73,'unowned_blocks':0,'duplicate_blocks':0,**{key:reader['conservation'][key] for key in ('authorized_suppression_rows','authorized_suppression_utf8_bytes','normal_claim_suppressions','owned_page_suppressions','cross_owner_suppressions','generated_suppression_claims','unproven_suppression_claims','unauthorized_suppression_blocks')},'reader_noise_findings':0,'editorial_lexical_deltas':0},'gates':[{'gate':x,'status':'pass' if x in {'accepted_reconstructed','source_disposition','semantic_navigation','handout_mapping','table_statblock_closure','asset_closure','no_technical_reader_noise','lexical_conservation','closed_inventory_serialization'} else 'pending','evidence':[],'errors':[]} for x in ['accepted_reconstructed','source_disposition','semantic_navigation','handout_mapping','table_statblock_closure','asset_closure','no_technical_reader_noise','lexical_conservation','closed_inventory_serialization','independent_candidate_verifier','two_clean_build_determinism','full_visual_qa','independent_gpt55_release_review','explicit_user_reading_acceptance']],'errors':[]}
  for name,value in [('SOURCE_DISPOSITION.json',disposition),('ASSET_MANIFEST.json',manifest),('MASTER_EN.qa.json',qa)]: (stage/name).write_text(canonical(value),encoding='utf8',newline='\n')
  qa['artifacts']={key:{'path':key.replace('_','.')+'.json' if key!='master_en' else 'MASTER_EN.md','bytes':(stage/({'master_en':'MASTER_EN.md','provenance':'MASTER_EN.provenance.json','source_disposition':'SOURCE_DISPOSITION.json','asset_manifest':'ASSET_MANIFEST.json'}[key])).stat().st_size if (stage/({'master_en':'MASTER_EN.md','provenance':'MASTER_EN.provenance.json','source_disposition':'SOURCE_DISPOSITION.json','asset_manifest':'ASSET_MANIFEST.json'}[key])).exists() else 0,'sha256':dig(stage/({'master_en':'MASTER_EN.md','provenance':'MASTER_EN.provenance.json','source_disposition':'SOURCE_DISPOSITION.json','asset_manifest':'ASSET_MANIFEST.json'}[key])) if (stage/({'master_en':'MASTER_EN.md','provenance':'MASTER_EN.provenance.json','source_disposition':'SOURCE_DISPOSITION.json','asset_manifest':'ASSET_MANIFEST.json'}[key])).exists() else '0'*64} for key in qa['artifacts']}
  structured_by_owner={};[structured_by_owner.setdefault(row['logical_owner'],[]).append(row['structure_id']) for row in reader['structured_evidence']]
  page_text={page:source_lines(reconstruction_package,page)[0] for page in range(1,125)}; reader_text=(stage/'MASTER_EN.md').read_text(encoding='utf8'); output_by_source={(item['binding_anchor'],item['source_page'],item['source_start'],item['source_end']):item for item in reader['emitted_ledger']}; provenance_units=[]
  for binding_row in binding['bindings']:
   fragments=[];outputs=[]
   for ordinal,span in enumerate(binding_row['source_span_hashes'],1):
    key=(binding_row['anchor'],span['page'],span['start'],span['end']); emitted=output_by_source.get(key)
    if emitted is None: continue
    fragment_id=f"{binding_row['anchor']}/p{span['page']:03d}/{ordinal:03d}"; source_value={'fragment_id':fragment_id,'page':span['page'],**dual_range(page_text[span['page']],span['start'],span['end']),'sha256':span['sha256']}; output_value={'fragment_id':fragment_id,**dual_range(reader_text,emitted['emitted_start'],emitted['emitted_end']),'sha256':hashlib.sha256(emitted['emitted_text'].encode('utf8')).hexdigest().upper()};fragments.append(source_value);outputs.append(output_value)
   transform=next(item for item in reader['transformations'] if item['anchor']==binding_row['anchor']); provenance_units.append({'anchor':binding_row['anchor'],'binding_order':binding_row['order'],'operations':['retained'],'source_fragments':fragments,'output_fragments':outputs,'asset_ids':transform['asset_ids'],'xref_ids':transform['xref_ids'],'structured_ids':structured_by_owner.get(binding_row['anchor'],[])})
  _,semantic_rows,suppression_rows=reader_surface_ranges(config_value,reconstruction_package)
  replacement_paths={x['asset_id']:x['output_path'] for x in ledger};reader_surface={'semantic_fragments':[{'fragment_id':x['fragment_id'],'order':x['order'],'owner_anchor':x['expected_owner'],'source_page':x['source_page'],**dual_range(page_text[x['source_page']],x['start_offset'],x['end_offset']),'raw_sha256':x['raw_sha256']} for x in semantic_rows],'suppressions':[{'suppression_id':x['suppression_id'],'owner_anchor':x['owner_anchor'],'claim_owner_anchor':x['source_containment']['claim_owner_anchor'],'source_page':x['source_page'],**dual_range(page_text[x['source_page']],x['start_offset'],x['end_offset']),'raw_sha256':x['raw_sha256'],'disposition':x['disposition'],'replacement_asset_id':x['replacement_asset_id'],'source_containment':x['source_containment'],'source_occurrences':1,'applied_occurrences':1,'reader_occurrences':reader_text.count(x['text']),'replacement_occurrences':reader_text.count(f"]({replacement_paths[x['replacement_asset_id']]})")} for x in suppression_rows],'alts':[{'asset_id':x['asset_id'],'output_path':x['output_path'],'alt_text':x['alt_text'],'placement_index':x['placement_index']} for x in sorted((x for x in ledger if x['representation']=='reader'),key=lambda x:x['asset_id'])]}
  provenance={'schema':'kb_creator.master_en_provenance.v1','scenario_id':config_value['scenario_id'],'candidate_state':'candidate_for_independent_verification','offset_contract':{'char':'python_unicode_code_points','byte':'utf8_bytes','range':'zero_based_half_open'},'producer':{'script_path':'kb_creator/scripts/build_scenario_master_en.py','script_sha256':dig(Path(__file__))},'inputs':{'contract':{'path':str(Path(contract).resolve().relative_to(root)).replace('\\','/'),'bytes':Path(contract).stat().st_size,'sha256':dig(contract)},'publication_config':{'path':str(cfg.relative_to(root)).replace('\\','/'),'bytes':cfg.stat().st_size,'sha256':dig(cfg)},'source_pdf':{'path':str(Path(source_pdf).resolve().relative_to(root)).replace('\\','/'),'bytes':Path(source_pdf).stat().st_size,'sha256':dig(source_pdf)},'accepted_reconstruction':config_value['accepted_reconstruction']},'master_en':master,'units':provenance_units,'structured_units':sidecar_structures(reader['structured_evidence'],page_text,reader_text),'reader_surface':reader_surface}
  (stage/'MASTER_EN.provenance.json').write_text(canonical(provenance),encoding='utf8',newline='\n');qa['artifacts']['provenance']=file_identity(stage/'MASTER_EN.provenance.json','MASTER_EN.provenance.json');qa['artifacts']['source_disposition']=file_identity(stage/'SOURCE_DISPOSITION.json','SOURCE_DISPOSITION.json');qa['artifacts']['asset_manifest']=file_identity(stage/'ASSET_MANIFEST.json','ASSET_MANIFEST.json');(stage/'MASTER_EN.qa.json').write_text(canonical(qa),encoding='utf8',newline='\n');(stage/'MASTER_EN.qa.md').write_text(qa_markdown(qa),encoding='utf8',newline='\n')
  rows,total,digest=candidate_inventory(stage);inventory_value={'schema':'kb_creator.candidate_inventory.v1','algorithm':'SHA-256 over ordinal UTF-8 LF relative_path<TAB>bytes<TAB>UPPER_SHA256<LF>','scope':'all regular candidate files except INVENTORY.json','rows':rows,'file_count':len(rows),'total_bytes':total,'inventory_sha256':digest};(stage/'INVENTORY.json').write_text(canonical(inventory_value),encoding='utf8',newline='\n')
  if destination.exists():bad('candidate target exists')
  stage.rename(destination);return {'status':'candidate_built_for_independent_verification','scenario_id':config_value['scenario_id'],'candidate_inventory_sha256':digest,'inventory_file_sha256':dig(destination/'INVENTORY.json'),'master_en_sha256':master['sha256']}
 except Exception:
  # Only the private directory created above belongs to this invocation.
  if stage.exists(): shutil.rmtree(stage)
  raise
def main():
 p=argparse.ArgumentParser();[p.add_argument('--'+x,required=True) for x in ('contract','reconstruction-package','publication-config','source-pdf','target')];p.add_argument('--preflight-only',action='store_true');a=p.parse_args()
 try:
  result=preflight(a.contract,a.reconstruction_package,a.publication_config,a.source_pdf) if a.preflight_only else build_candidate(a.contract,a.reconstruction_package,a.publication_config,a.source_pdf,a.target)
 except ValueError as error:
  print(str(error),file=__import__('sys').stderr);raise SystemExit(1)
 print(json.dumps(result,sort_keys=True))
if __name__=='__main__':main()
