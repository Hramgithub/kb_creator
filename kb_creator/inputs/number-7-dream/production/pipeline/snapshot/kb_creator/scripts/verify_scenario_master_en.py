"""Independent, read-only C2b verifier.  It never imports or executes the builder."""
from __future__ import annotations
import argparse, hashlib, json, os, re, stat, sys, tempfile
from pathlib import Path
from PIL import Image
from pypdf import PdfReader

ROOT_NAMES={'MASTER_EN.md','MASTER_EN.provenance.json','SOURCE_DISPOSITION.json','ASSET_MANIFEST.json','MASTER_EN.qa.json','MASTER_EN.qa.md','INVENTORY.json','assets'}
HEX=re.compile(r'^[0-9A-F]{64}$'); NAME=re.compile(r'^[a-z0-9][a-z0-9._-]{0,63}$')
ALGO='SHA-256 over ordinal UTF-8 LF relative_path<TAB>bytes<TAB>UPPER_SHA256<LF>'
PACKAGE_ALGO='SHA-256 over ordinal UTF-8 LF relative_path<TAB>bytes<TAB>UPPER_SHA256<LF>'
GATES=['accepted_reconstructed','source_disposition','semantic_navigation','handout_mapping','table_statblock_closure','asset_closure','no_technical_reader_noise','lexical_conservation','closed_inventory_serialization','independent_candidate_verifier','two_clean_build_determinism','full_visual_qa','independent_gpt55_release_review','explicit_user_reading_acceptance']
V2_SCHEMA='kb_creator.master_en_publication.v2'
V3_SCHEMA='kb_creator.master_en_publication.v3'
V3_PAGE_MARKER_LINE=re.compile(r'^<!--\s*source-page-(\d{3,})\s*-->$')
MIGRATION_ALGO="SHA-256 over canonical UTF-8 JSON (sort_keys=true, separators=(',', ':')) of complete frozen-v1 row"
MIGRATION_DOMAINS={
 'hierarchy_rows':('hierarchy','anchor',168,{'retained_unchanged','retained_rebound','reclassified','replaced','split','merged','suppressed_reviewed','excluded_advertising'}),
 'asset_rows':('assets','asset_id',123,{'retained_unchanged','retained_rebound','reclassified','replaced','split','merged','suppressed_reviewed','excluded_advertising'}),
 'xref_rows':('xrefs','xref_id',237,{'retained_unchanged','retained_rebound','replaced','split','merged','suppressed_reviewed','excluded_advertising'}),
 'source_disposition_rows':('source_disposition','page',124,{'retained_unchanged','reclassified','suppressed_reviewed','excluded_advertising'}),
 'handout_rows':('handouts','anchor',41,{'retained_unchanged','retained_rebound','reclassified','replaced','split','merged','suppressed_reviewed','excluded_advertising'}),
 'structured_rows':('structured_content','structure_id',29,{'retained_unchanged','retained_rebound','reclassified','replaced','split','merged','suppressed_reviewed'}),
}
def fail(code,detail): raise ValueError(f'{code}: {detail}')
def sha(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest().upper()
def rp(path):
 s=os.lstat(path);return stat.S_ISLNK(s.st_mode) or bool(getattr(s,'st_file_attributes',0)&0x400)
def root_for(config):
 for p in (Path(config).resolve().parent,*Path(config).resolve().parents):
  if (p/'.git').exists(): return p
 fail('E_C2B_PATH','repository-root')
def canonical(path):
 data=Path(path).read_bytes()
 if data.startswith(b'\xef\xbb\xbf') or b'\r' in data or not data.endswith(b'\n'): fail('E_C2B_SCHEMA',Path(path).name)
 try: value=json.loads(data.decode('utf8'))
 except Exception: fail('E_C2B_SCHEMA',Path(path).name)
 if not isinstance(value,dict) or json.dumps(value,ensure_ascii=False,sort_keys=True,indent=2).encode('utf8')+b'\n'!=data: fail('E_C2B_SCHEMA',Path(path).name)
 return value
def parsed(path):
 try: value=json.loads(Path(path).read_text(encoding='utf8'))
 except Exception: fail('E_C2B_SCHEMA',Path(path).name)
 if not isinstance(value,dict): fail('E_C2B_SCHEMA',Path(path).name)
 return value
def closed(value,keys,where):
 if not isinstance(value,dict) or set(value)!=set(keys): fail('E_C2B_SCHEMA',where)
def safe(value): return isinstance(value,str) and value and '\\' not in value and ':' not in value and not Path(value).is_absolute() and all(x not in {'','.','..'} for x in value.split('/'))
def inventory(root):
 rows=[]
 for p in sorted((p for p in Path(root).rglob('*') if p.is_file() and p.name!='INVENTORY.json'),key=lambda x:x.relative_to(root).as_posix()):
  rows.append({'path':p.relative_to(root).as_posix(),'bytes':p.stat().st_size,'sha256':sha(p)})
 payload=''.join(f"{x['path']}\t{x['bytes']}\t{x['sha256']}\n" for x in rows).encode('utf8')
 return rows,sum(x['bytes'] for x in rows),hashlib.sha256(payload).hexdigest().upper()
def package_hash(package): return inventory(package)[2]
def v2_package_path(root,value):
 if not safe(value):fail('E_V2_IDENTITY','reconstruction-root')
 return Path(root)/Path(value)
def v2_package_inventory(root):
 """Independent input aggregate: includes every regular filename, including INVENTORY.json."""
 root=Path(root)
 if not root.is_dir() or rp(root):fail('E_V2_IDENTITY','reconstruction-topology')
 rows=[]
 def walk(directory):
  children=list(os.scandir(directory))
  if not children:fail('E_V2_IDENTITY','reconstruction-topology')
  for entry in children:
   path=Path(entry.path)
   if rp(path):fail('E_V2_IDENTITY','reconstruction-topology')
   mode=os.lstat(path).st_mode
   if stat.S_ISDIR(mode):walk(path)
   elif stat.S_ISREG(mode):
    data=path.read_bytes();rows.append((path.relative_to(root).as_posix(),len(data),hashlib.sha256(data).hexdigest().upper()))
   else:fail('E_V2_IDENTITY','reconstruction-topology')
 walk(root);rows.sort(key=lambda row:row[0])
 payload=''.join(f'{path}\t{size}\t{digest}\n' for path,size,digest in rows).encode('utf8')
 return len(rows),sum(row[1] for row in rows),hashlib.sha256(payload).hexdigest().upper()
def v2_source_partition(value,package):
 """Independent closed raw-byte source-partition check."""
 closed(value,{'pages','spans'},'v2-source-partition');pages=value['pages'];spans=value['spans']
 if not isinstance(pages,list) or not isinstance(spans,list) or [x.get('page') for x in pages if isinstance(x,dict)]!=list(range(1,123)):fail('E_V2_PARTITION','schema')
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
 grouped={};span_ids=set()
 for row in spans:
  closed(row,{'span_id','page','source_path','start_byte','end_byte','start_char','end_char','raw_sha256','raw_text_sha256','classification','owner_kind','owner_id','decision_ref'},'v2-source-span')
  if not isinstance(row['span_id'],str) or not row['span_id'] or row['span_id'] in span_ids or any(not isinstance(row[x],int) or isinstance(row[x],bool) for x in ('page','start_byte','end_byte','start_char','end_char')) or row['page'] not in range(1,123) or row['end_byte']<=row['start_byte'] or row['end_char']<=row['start_char'] or not isinstance(row['source_path'],str) or Path(row['source_path']).is_absolute() or '\\' in row['source_path'] or '..' in Path(row['source_path']).parts or row['source_path']!=f"pages/page-{row['page']:03d}.md" or row['classification'] not in {'retained_heading','retained_text','reviewed_structured_source','asset_reference_source','generated_navigation_source','authorized_suppression','technical_marker_suppression','layout_separator'} or row['owner_kind'] not in {'event','asset','generated_navigation','suppression'} or not isinstance(row['owner_id'],str) or not row['owner_id'] or row['decision_ref'] is not None and not isinstance(row['decision_ref'],str) or not HEX.fullmatch(str(row['raw_sha256'])) or not HEX.fullmatch(str(row['raw_text_sha256'])):fail('E_V2_PARTITION','span')
  span_ids.add(row['span_id'])
  grouped.setdefault(row['page'],[]).append(row)
 totals={'pages':0,'bytes':0,'line_slots':0,'nonblank_line_slots':0,'eol':{'lf':0,'crlf':0,'crcrlf':0,'lone_cr':0}}
 for page in pages:
  closed(page,{'page','path','bytes','sha256','encoding','eol_profile','span_ids'},'v2-source-page')
  if not isinstance(page['page'],int) or isinstance(page['page'],bool) or not isinstance(page['path'],str) or page['path']!=f"pages/page-{page['page']:03d}.md" or page['encoding']!='utf-8-no-bom' or not isinstance(page['bytes'],int) or isinstance(page['bytes'],bool) or not HEX.fullmatch(str(page['sha256'])) or not isinstance(page['span_ids'],list) or page['page'] not in grouped:fail('E_V2_PARTITION','page')
  raw=(Path(package)/Path(page['path'])).read_bytes()
  if raw.startswith(b'\xef\xbb\xbf') or page['bytes']!=len(raw) or hashlib.sha256(raw).hexdigest().upper()!=page['sha256'] or page['eol_profile']!=profile(raw):fail('E_V2_PARTITION','page')
  cursor=0;ids=[]
  for span in grouped[page['page']]:
   chunk=raw[span['start_byte']:span['end_byte']]
   try:text=raw.decode('utf8');piece=chunk.decode('utf8')
   except UnicodeDecodeError:fail('E_V2_PARTITION','utf8-boundary')
   if span['start_byte']!=cursor or span['end_byte']>len(raw) or span['end_char']>len(text) or text[:span['start_char']].encode('utf8')!=raw[:span['start_byte']] or text[span['start_char']:span['end_char']]!=piece or hashlib.sha256(chunk).hexdigest().upper()!=span['raw_sha256'] or hashlib.sha256(piece.encode('utf8')).hexdigest().upper()!=span['raw_text_sha256']:fail('E_V2_PARTITION','coverage')
   cursor=span['end_byte'];ids.append(span['span_id'])
  if cursor!=len(raw) or ids!=page['span_ids']:fail('E_V2_PARTITION','coverage')
  actual=profile(raw);totals['pages']+=1;totals['bytes']+=len(raw);totals['line_slots']+=actual['line_slots'];totals['nonblank_line_slots']+=actual['nonblank_line_slots']
  for key in totals['eol']:totals['eol'][key]+=actual[key]
 return totals
V2_OPERATIONS={'emit_exact','semantic_restructure','asset_reference','generated_navigation','source_recovery','emit_anchor_only','suppress'}
V2_ROLE_RANK={'heading':0,'anchor_only':1,'text_fragment':2,'structured_unit':3,'asset':4,'generated_navigation':5}
V2_PLACEHOLDERS=('Source-backed','See source-backed entry.','Translatable source key')
V2_OPERATION_BY_TYPE={'heading':{'emit_exact'},'text_fragment':{'emit_exact','source_recovery'},'structured_unit':{'semantic_restructure'},'asset':{'asset_reference','suppress'},'anchor_only':{'emit_anchor_only'},'generated_navigation':{'generated_navigation'}}
def v2_a3_payload_schema(data):
 """Independent closed schemas for every structured publication kind."""
 kind=data.get('kind') if isinstance(data,dict) else None
 schemas={'callout':{'kind','body','contains','end_after'},'ordered_list_callout':{'kind','items','item_count','contains','end_after'},'table':{'kind','header','rows','row_count','cell_count','contains'},'equipment_card':{'kind','title','stats','footnote','body','contains','end_after'},'creature_statblock':{'kind','title','subtitle','characteristics','derived_stats','attacks','abilities','nested_tables','contains','end_after'},'inline_run_in':{'kind','anchor','label','xref','contains'},'full_page_map':{'kind','pages','reader_asset_ids','accessible_key','legend','scale','contains'},'physical_page_pair':{'kind','front_page','back_page','front_reader_asset_ids','back_reader_asset_ids','back_semantics','contains'}}
 if kind not in schemas:fail('E_V2_STRUCTURE','kind')
 closed(data,schemas[kind],'v2-typed-payload')
 if kind=='table' and (not isinstance(data['header'],list) or not data['header'] or not isinstance(data['rows'],list) or data['row_count']!=len(data['rows']) or data['cell_count']!=sum(len(row) for row in data['rows']) or any(not isinstance(row,list) or len(row)!=len(data['header']) for row in data['rows'])):fail('E_V2_STRUCTURE','table')
 if kind=='ordered_list_callout' and (not isinstance(data['items'],list) or not data['items'] or data['item_count']!=len(data['items']) or data['end_after']!=data['contains'][-1]):fail('E_V2_STRUCTURE','list')
 if kind in {'callout','equipment_card','creature_statblock'} and (not data['contains'] or data['end_after']!=data['contains'][-1]):fail('E_V2_STRUCTURE','boundary')
 if kind=='equipment_card' and (any(not isinstance(data[key],str) for key in ('title','stats','footnote','body')) or not any(data[key] for key in ('title','stats','footnote','body'))):fail('E_V2_STRUCTURE','equipment')
 if kind=='creature_statblock' and (any(not isinstance(data[key],str) for key in ('title','subtitle','characteristics','derived_stats','attacks','abilities','nested_tables')) or not any(data[key] for key in ('title','subtitle','characteristics','derived_stats','attacks','abilities','nested_tables'))):fail('E_V2_STRUCTURE','creature')
 if kind=='full_page_map' and (not isinstance(data['pages'],list) or len(data['pages'])<2 or not isinstance(data['reader_asset_ids'],list) or not data['reader_asset_ids'] or len(data['reader_asset_ids'])!=len(set(data['reader_asset_ids'])) or any(not isinstance(data[key],str) for key in ('accessible_key','legend','scale'))):fail('E_V2_STRUCTURE','map')
 if kind=='physical_page_pair' and (not isinstance(data['front_page'],int) or not isinstance(data['back_page'],int) or data['front_page']==data['back_page'] or not isinstance(data['front_reader_asset_ids'],list) or not data['front_reader_asset_ids'] or len(data['front_reader_asset_ids'])!=len(set(data['front_reader_asset_ids'])) or not isinstance(data['back_reader_asset_ids'],list) or not data['back_reader_asset_ids'] or len(data['back_reader_asset_ids'])!=len(set(data['back_reader_asset_ids'])) or not isinstance(data['back_semantics'],str) or not data['back_semantics']):fail('E_V2_STRUCTURE','pair')
 return kind
def v2_a3_pointer(value,pointer):
 if not isinstance(pointer,str) or not pointer.startswith('/') or '//' in pointer:fail('E_V2_PAYLOAD','pointer')
 here=value
 for part in pointer[1:].split('/'):
  part=part.replace('~1','/').replace('~0','~')
  if isinstance(here,list) and part.isdigit() and int(part)<len(here):here=here[int(part)]
  elif isinstance(here,dict) and part in here:here=here[part]
  else:fail('E_V2_PAYLOAD','pointer')
 return here
def v2_a3_leaves(value,prefix='/content'):
 reserved={'kind','contains','end_after','asset_id','asset_ids','reader_asset_ids','front_reader_asset_ids','back_reader_asset_ids','anchor','front_facsimile','back_facsimile','front_page','back_page','pages','page_set','count','row_count','cell_count','continuation','placement'};out=[]
 def visit(item,path,key=None):
  if isinstance(item,str) and key not in reserved:out.append((path,item))
  elif isinstance(item,list):
   for i,child in enumerate(item):visit(child,f'{path}/{i}',key)
  elif isinstance(item,dict):
   for child_key,child in item.items():visit(child,f'{path}/{child_key.replace("~","~0").replace("/","~1")}',child_key)
 visit(value,prefix);return out
def v2_canonical_source_free_asset_event(asset,event,events):
 """Verifier-owned validation for source-free canonical asset events."""
 placement=asset.get('placement');order=asset.get('source_order')
 if event['type']!='asset' or event.get('source_operation') not in V2_OPERATION_BY_TYPE['asset'] or asset.get('anchor')!=event.get('anchor') or asset.get('source_page')!=event.get('page') or not isinstance(event.get('order_key'),list) or len(event['order_key'])!=4 or event['order_key'][0]!=asset['source_page'] or not isinstance(placement,dict) or set(placement) not in ({'before_event'},{'after_event'},{'inside_structured_unit'}) or next(iter(placement.values())) not in events or not isinstance(order,dict):fail('E_V2_ASSET','canonical-event')
 if order.get('kind')=='selected_view_raw_index' and set(order)=={'kind','view','raw_index','gap_ordinal'} and isinstance(order['view'],str) and isinstance(order['raw_index'],int) and isinstance(order['gap_ordinal'],int):return
 if order.get('kind')=='physical_unit_page_slot' and set(order)=={'kind','unit_id','page_slot'} and isinstance(order['unit_id'],str) and isinstance(order['page_slot'],int):return
 fail('E_V2_ASSET','source-order')
def v2_a3_validate(cfg,package,root=None):
 """Independent A3 proof; deliberately not shared with the builder."""
 spans={row['span_id']:row for row in cfg['source_partition']['spans']};events={row['event_id']:row for row in cfg['events']};hierarchy={row['anchor']:row for row in cfg['hierarchy']};seen=set()
 for row in cfg['hierarchy']:
  closed(row,{'anchor','parent_anchor','level','toc_entry','semantic_role','source_pages','source_title','reader_title','representation','reviewed_title_transformation','migration_row_id'},'v2-hierarchy')
  if not isinstance(row['anchor'],str) or not row['anchor'] or row['anchor'] in seen or row['parent_anchor'] is not None and row['parent_anchor'] not in hierarchy or row['parent_anchor']==row['anchor'] or not isinstance(row['level'],int) and row['level'] is not None or isinstance(row['level'],bool) or not isinstance(row['toc_entry'],bool) or not isinstance(row['semantic_role'],str) or not row['semantic_role'] or not isinstance(row['source_pages'],list) or not row['source_pages'] or any(page not in range(1,123) for page in row['source_pages']) or row['representation'] not in {'heading','anchor_only','inline_run_in'} or not isinstance(row['migration_row_id'],str) or not row['migration_row_id']:fail('E_V2_HIERARCHY','row')
  if row['representation']=='heading' and row['level'] not in range(1,7):fail('E_V2_HIERARCHY','level')
  if row['representation']!='heading' and row['level'] is not None:fail('E_V2_HIERARCHY','representation')
  transform=row['reviewed_title_transformation']
  if row['source_title']!=row['reader_title']:
   closed(transform,{'operation','decision_ref','recovery_id'},'v2-title-transformation')
   if transform['operation'] not in {'source_recovery','semantic_restructure'} or not isinstance(transform['decision_ref'],str) or not transform['decision_ref'] or not isinstance(transform['recovery_id'],str) or not transform['recovery_id']:fail('E_V2_TITLE','transformation')
  elif transform is not None:fail('E_V2_TITLE','transformation')
  seen.add(row['anchor'])
 for start in hierarchy:
  anchor=start;walked=set()
  while hierarchy[anchor]['parent_anchor'] is not None:
   anchor=hierarchy[anchor]['parent_anchor']
   if anchor in walked:fail('E_V2_HIERARCHY','cycle')
   walked.add(anchor)
 canonical_assets={row['asset_id']:row for row in cfg['assets'] if isinstance(row,dict) and 'provenance' in row};used=set();last=None
 def intervening_foreign(span,event):
  if span['classification'] in {'layout_separator','authorized_suppression'} or span['owner_id']==event['event_id']:return False
  asset=canonical_assets.get(span['owner_id']) if span['classification']=='asset_reference_source' else None
  return asset is None or not isinstance(asset.get('placement'),dict) or next(iter(asset['placement'].values()),None)!=event['event_id']
 for ordinal,event in enumerate(cfg['events']):
  keys={'event_id','type','page','order_key','anchor','content','fragment_id','source_span_ids','source_operation','payload_bindings'}|({'contains'} if event['type']=='structured_unit' else set())|({'generated_placement'} if event['type']=='generated_navigation' else set());closed(event,keys,'v2-event')
  ids=event['source_span_ids'];operation=event['source_operation']
  if event['type']=='generated_navigation':
   if ids or event['payload_bindings'] or set(event['generated_placement'])!={'after_event'} or event['generated_placement']['after_event'] not in events or not isinstance(event['content'],dict) or event['content'].get('kind')!='generated_navigation':fail('E_V2_NAVIGATION','event')
   continue
  asset=canonical_assets.get(event['content']) if event['type']=='asset' and isinstance(event['content'],str) else None
  source_free=asset is not None and asset.get('disposition')=='reader' and asset.get('provenance',{}).get('kind') in {'visual_region','reviewed_provisional_full_page'} and ids==[] and event['payload_bindings']==[]
  if source_free:
   v2_canonical_source_free_asset_event(asset,event,events)
   key=tuple(event['order_key'])
   if last is not None and key<=last:fail('E_V2_ORDER','derived')
   last=tuple(key);continue
  if event['type'] not in V2_ROLE_RANK or operation not in V2_OPERATION_BY_TYPE.get(event['type'],set()) or not isinstance(ids,list) or not ids or len(ids)!=len(set(ids)) or any(item not in spans for item in ids):fail('E_V2_PROVENANCE','event')
  source=[spans[item] for item in ids]
  if event['type']=='asset':
   if any(row['owner_kind']!='asset' or row['owner_id']!=event['content'] or row['classification']!='asset_reference_source' for row in source):fail('E_V2_ASSET','event-owner')
  elif any(row['owner_kind']!='event' or row['owner_id']!=event['event_id'] for row in source):fail('E_V2_PROVENANCE','owner')
  if any(item in used for item in ids):fail('E_V2_PROVENANCE','source-reuse')
  if any(source[i]['page']>source[i+1]['page'] or source[i]['page']==source[i+1]['page'] and source[i]['start_byte']>=source[i+1]['start_byte'] for i in range(len(source)-1)):fail('E_V2_PROVENANCE','span-order')
  if len(source)>1:
   for left,right in zip(source,source[1:]):
    if left['page']==right['page']:
     between=[span for span in spans.values() if span['page']==left['page'] and left['end_byte']<=span['start_byte'] and span['end_byte']<=right['start_byte']]
     foreign=next((span for span in between if intervening_foreign(span,event)),None)
     if foreign is not None:fail('E_V2_PROVENANCE',f"intervening-foreign-span:{event['event_id']}:{foreign['span_id']}:{foreign['owner_id']}")
  key=[source[0]['page'],source[0]['start_byte'],V2_ROLE_RANK[event['type']],ordinal]
  if event['order_key']!=key or last is not None and tuple(key)<=last:fail('E_V2_ORDER','derived')
  last=tuple(key);used.update(ids);bindings=event['payload_bindings']
  if not isinstance(bindings,list):fail('E_V2_PAYLOAD','bindings')
  targets={} if event['type'] in {'asset','anchor_only'} else {pointer:text for pointer,text in v2_a3_leaves(event['content']) if text};got=set()
  for binding in bindings:
   closed(binding,{'json_pointer','source_slices','joiner','recovery_id'},'v2-payload-binding');pointer=binding['json_pointer'];leaf=v2_a3_pointer({'content':event['content']},pointer)
   if pointer in got or pointer not in targets or not isinstance(leaf,str) or binding['joiner'] not in {'',' ','\n','\n\n'} or (binding['source_slices'] is None)==(binding['recovery_id'] is None):fail('E_V2_PAYLOAD','binding')
   got.add(pointer)
   if binding['source_slices'] is not None:
    if not isinstance(binding['source_slices'],list) or not binding['source_slices']:fail('E_V2_PAYLOAD','slice')
    pieces=[]
    for slice_ in binding['source_slices']:
     closed(slice_,{'span_id','start_char','end_char'},'v2-payload-slice');span=spans.get(slice_['span_id'])
     if span is None or span['span_id'] not in ids or not isinstance(slice_['start_char'],int) or not isinstance(slice_['end_char'],int) or slice_['end_char']<=slice_['start_char']:fail('E_V2_PAYLOAD','slice')
     if slice_['start_char']<span['start_char'] or slice_['end_char']>span['end_char']:fail('E_V2_PAYLOAD','slice')
     pieces.append((Path(package)/span['source_path']).read_bytes().decode('utf8')[slice_['start_char']:slice_['end_char']])
    if binding['joiner'].join(pieces)!=leaf:fail('E_V2_PAYLOAD','text')
   elif not isinstance(binding['recovery_id'],str) or not binding['recovery_id']:fail('E_V2_RECOVERY','binding')
  if got!=set(targets):fail('E_V2_PAYLOAD','unbound')
  if any(token in text for _,text in targets.items() for token in V2_PLACEHOLDERS):fail('E_V2_PAYLOAD','placeholder')
  if event['type']=='structured_unit':
   data=event['content'];v2_a3_payload_schema(data);kind=data.get('kind') if isinstance(data,dict) else None
   if kind not in {'callout','ordered_list_callout','table','equipment_card','creature_statblock','inline_run_in','full_page_map','physical_page_pair'}:fail('E_V2_STRUCTURE','kind')
   if kind=='table' and (not isinstance(data.get('header'),list) or not isinstance(data.get('rows'),list) or data.get('row_count')!=len(data['rows']) or any(not isinstance(row,list) or len(row)!=len(data['header']) for row in data['rows'])):fail('E_V2_STRUCTURE','table')
   if kind=='ordered_list_callout' and (not isinstance(data.get('items'),list) or data.get('item_count')!=len(data['items'])):fail('E_V2_STRUCTURE','list')
   if kind=='physical_page_pair' and (not isinstance(data.get('front_page'),int) or not isinstance(data.get('back_page'),int) or data['front_page']==data['back_page']):fail('E_V2_STRUCTURE','pair')
   contains=event['contains']
   if not isinstance(contains,list) or not contains or contains!=data['contains'] or len(contains)!=len(set(contains)) or set(ids)-set(contains):fail('E_V2_STRUCTURE','contains')
   for item in contains:
    if item in ids:continue
    child=events.get(item)
    if child is None or child['event_id']==event['event_id'] or child['anchor']!=event['anchor'] or child['page']!=event['page'] or child['type'] in {'heading','generated_navigation'}:fail('E_V2_STRUCTURE','contains-owner')
   def position(item):
    row=spans[item] if item in spans else spans[events[item]['source_span_ids'][0]]
    return (row['page'],row['start_byte'])
   if any(position(left)>=position(right) for left,right in zip(contains,contains[1:])):fail('E_V2_STRUCTURE','contains-order')
 recoveries={row['recovery_id']:row for row in cfg['source_recoveries']}
 for event in cfg['events']:
  for binding in event['payload_bindings']:
   if binding['recovery_id'] is not None and (binding['recovery_id'] not in recoveries or recoveries[binding['recovery_id']]['target_event_id']!=event['event_id']):fail('E_V2_RECOVERY','binding')
 for row in cfg['source_recoveries']:
  closed(row,{'recovery_id','source_pdf_identity','physical_page','extraction_method','source_text','source_text_sha256','evidence_identity','target_event_id','placement','decision_ref'},'v2-recovery')
  if row['target_event_id'] not in events or row['placement'] not in {'before_event','after_event'} or not isinstance(row['physical_page'],int) or row['physical_page']<1 or not isinstance(row['source_text'],str) or hashlib.sha256(row['source_text'].encode('utf8')).hexdigest().upper()!=row['source_text_sha256'] or not isinstance(row['decision_ref'],str) or not row['decision_ref']:fail('E_V2_RECOVERY','row')
  if root is not None:
   if row['source_pdf_identity']!=cfg['document']['source_pdf']:fail('E_V2_RECOVERY','source-pdf')
   v2_identity(root,row['evidence_identity'],'recovery-evidence')
 for row in cfg['hierarchy']:
  transform=row['reviewed_title_transformation']
  if transform is not None and transform['recovery_id'] not in recoveries:fail('E_V2_TITLE','recovery')
 for row in cfg['xrefs']:
  closed(row,{'xref_id','source_event_id','source_page','target_anchor','reader_text','source_slices','emit_link','migration_row_id'},'v2-xref')
  owner=events.get(row['source_event_id'])
  owned_pages={spans[item]['page'] for item in owner.get('source_span_ids',[]) if item in spans} if owner is not None else set()
  if owner is None or row['source_page'] not in owned_pages or not isinstance(row['emit_link'],bool) or (row['emit_link'] and row['target_anchor'] not in hierarchy) or (not row['emit_link'] and row['target_anchor'] is not None) or not isinstance(row['migration_row_id'],str) or not row['migration_row_id'] or not isinstance(row['source_slices'],list) or not row['source_slices']:fail('E_V2_XREF','closure')
  text=[]
  for slice_ in row['source_slices']:
   closed(slice_,{'span_id','start_char','end_char'},'v2-xref-slice');span=spans.get(slice_['span_id'])
   if span is None or span['span_id'] not in owner['source_span_ids'] or slice_['start_char']<span['start_char'] or slice_['end_char']>span['end_char']:fail('E_V2_XREF','slice')
   text.append((Path(package)/span['source_path']).read_bytes().decode('utf8')[slice_['start_char']:slice_['end_char']])
  if ''.join(text)!=row['reader_text']:fail('E_V2_XREF','text')
 asset_result=v2_asset_provenance_binding(cfg,package,root,spans)
 reader_assets={row['asset_id'] for row in cfg['assets'] if row.get('reader_value',row.get('disposition')=='reader')}
 for event in cfg['events']:
  if event['type']!='structured_unit':continue
  data=event['content']
  if data['kind']=='full_page_map' and not set(data['reader_asset_ids'])<=reader_assets:fail('E_V2_ASSET','map-reader-assets')
  if data['kind']=='physical_page_pair' and not (set(data['front_reader_asset_ids'])|set(data['back_reader_asset_ids']))<=reader_assets:fail('E_V2_ASSET','pair-reader-assets')
def v2_canonical_row(row):
 return hashlib.sha256(json.dumps(row,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode('utf8')).hexdigest().upper()
def v2_reparse(path):
 data=os.lstat(path);return stat.S_ISLNK(data.st_mode) or bool(getattr(data,'st_file_attributes',0)&0x400)
def v2_asset_provenance_binding(cfg,package,root,spans):
 """Verifier-owned canonical/legacy dispatcher at the B1c6 input seam."""
 assets=cfg['assets'];canonical=[isinstance(row,dict) and 'provenance' in row for row in assets]
 if any(canonical) and not all(canonical):fail('E_V2_ASSET','mode')
 if not any(canonical):
  used=set();reader=0
  for row in assets:
   if not isinstance(row,dict) or 'source_span_ids' not in row or not isinstance(row['source_span_ids'],list) or not row['source_span_ids'] or len(row['source_span_ids'])!=len(set(row['source_span_ids'])) or any(item not in spans for item in row['source_span_ids']):fail('E_V2_ASSET','provenance')
   if any(item in used or spans[item]['owner_kind']!='asset' or spans[item]['classification']!='asset_reference_source' for item in row['source_span_ids']):fail('E_V2_ASSET','ownership')
   used.update(row['source_span_ids']);reader+=bool(row['reader_value'])
   if row['reader_value'] and next(iter(row['placement'].values())) not in {event['event_id'] for event in cfg['events']}:fail('E_V2_ASSET','placement')
  return {'mode':'legacy','reader':reader,'counts':{}}
 package=Path(package).resolve();root=Path(root).resolve();counts={kind:0 for kind in ('markdown_image_reference','visual_region','reviewed_provisional_full_page')};used=set();cache={}
 def identity(item,label,inside=True):
  if not isinstance(item,dict) or set(item)!={'path','bytes','sha256'}:fail('E_V2_ASSET',label+'-identity')
  path=v2_identity(root,item,label)
  if not path.is_file() or path.is_symlink() or inside and package not in path.parents:fail('E_V2_ASSET',label+'-path')
  here=path
  while inside and here!=package:
   if v2_reparse(here):fail('E_V2_ASSET',label+'-reparse')
   here=here.parent
  return path
 def image(row):
  binary=row['binary']
  if not isinstance(binary,dict) or set(binary)!={'path','bytes','sha256','media_type','dimensions'} or not isinstance(binary.get('dimensions'),dict) or set(binary['dimensions'])!={'width','height'}:fail('E_V2_ASSET','binary')
  path=identity({'path':binary['path'],'bytes':binary['bytes'],'sha256':binary['sha256']},'binary')
  try:
   with Image.open(path) as opened:opened.load();mime={'JPEG':'image/jpeg','PNG':'image/png'}.get(opened.format);size={'width':opened.width,'height':opened.height}
  except OSError:fail('E_V2_ASSET','binary')
  if mime!=binary['media_type'] or size!=binary['dimensions']:fail('E_V2_ASSET','binary')
  return path,binary
 for row in assets:
  if set(row)!={'asset_id','disposition','source_page','binary','provenance','migration_outcome','anchor','placement','source_order'} or any(key in row for key in ('page','reader_value','source_span_ids')):fail('E_V2_ASSET','canonical-schema')
  p=row['provenance'];kind=p.get('kind') if isinstance(p,dict) else None
  if kind not in counts:fail('E_V2_ASSET','provenance')
  counts[kind]+=1
  if kind=='markdown_image_reference':
   path,binary=image(row);need={'kind','span_id','page_markdown_identity','start_byte','end_byte','start_char','end_char','marker_sha256'}
   if set(p)!=need or p['span_id'] in used or p['span_id'] not in spans:fail('E_V2_ASSET','markdown')
   span=spans[p['span_id']];used.add(p['span_id'])
   if span['owner_kind']!='asset' or span['classification']!='asset_reference_source' or span['page']!=row['source_page']:fail('E_V2_ASSET','markdown-owner')
   page=identity(p['page_markdown_identity'],'markdown-page')
   if page!=package/span['source_path'] or p['page_markdown_identity']!=cfg['source_disposition'][row['source_page']-1]['page_markdown'] or tuple(p[x] for x in ('start_byte','end_byte','start_char','end_char'))!=tuple(span[x] for x in ('start_byte','end_byte','start_char','end_char')):fail('E_V2_ASSET','markdown-range')
   raw=page.read_bytes()[p['start_byte']:p['end_byte']]
   try:marker=raw.decode('utf8');before=page.read_bytes()[:p['start_byte']].decode('utf8')
   except UnicodeDecodeError:fail('E_V2_ASSET','markdown-utf8')
   match=re.fullmatch(r'!\[[^\]]*\]\(([^)]+)\)',marker.strip())
   if not match or len(before)!=p['start_char'] or hashlib.sha256(raw).hexdigest().upper()!=p['marker_sha256'] or (page.parent/match.group(1)).resolve()!=path:fail('E_V2_ASSET','markdown-marker')
  elif kind=='visual_region':
   path,binary=image(row);need={'kind','asset_manifest_identity','asset_manifest_row_sha256','comparison_identity','selected_view','source_asset_reference','raw_index','block_type','source_page','bbox','comparison_block_sha256'}
   if set(p)!=need:fail('E_V2_ASSET','visual')
   manifest=identity(p['asset_manifest_identity'],'manifest')
   if manifest!=package/'ASSET_MANIFEST.json':fail('E_V2_ASSET','manifest-path')
   data=cache.setdefault((manifest,sha(manifest)),parsed(manifest));rows=[x for x in data.get('assets',[]) if isinstance(x,dict) and x.get('stored_path')==path.relative_to(package).as_posix() and str(x.get('sha256','')).upper()==binary['sha256']]
   if len(rows)!=1 or v2_canonical_row(rows[0])!=p['asset_manifest_row_sha256']:fail('E_V2_ASSET','manifest-binding')
   comparison=identity(p['comparison_identity'],'comparison',False);data=cache.setdefault((comparison,sha(comparison)),parsed(comparison));companion=comparison.parent.parent/'inputs'/Path(data.get('manifest',{}).get('path','')).name
   companion_data=cache.setdefault((companion,sha(companion)),parsed(companion)) if companion.is_file() else {};source=companion_data.get('source',{})
   if data.get('schema')!='kb_creator.mineru_three_view_comparison.v1' or data.get('status')!='pass' or data.get('failures')!=[] or not companion.is_file() or sha(companion)!=data.get('manifest',{}).get('sha256') or (source.get('bytes'),source.get('sha256'))!=(cfg['document']['source_pdf']['bytes'],cfg['document']['source_pdf']['sha256']):fail('E_V2_ASSET','comparison-topology')
   blocks=[x for x in data.get('views',{}).get(p['selected_view'],{}).get('blocks',[]) if isinstance(x,dict) and x.get('raw_index')==p['raw_index'] and rows[0].get('source_path') in x.get('assets',[])]
   if len(blocks)!=1 or (p['source_asset_reference'],p['block_type'],p['source_page'],p['bbox'])!=(rows[0].get('source_path'),blocks[0].get('type'),blocks[0].get('source_page'),blocks[0].get('bbox')) or v2_canonical_row(blocks[0])!=p['comparison_block_sha256']:fail('E_V2_ASSET','comparison-binding')
  else:
   if row['binary'] is not None or p.get('source_pdf_identity')!=cfg['document']['source_pdf'] or p.get('physical_page')!=row['source_page'] or p.get('page_index_zero_based')!=row['source_page']-1:fail('E_V2_ASSET','provisional')
   page=PdfReader(str(identity(cfg['document']['source_pdf'],'source-pdf',False))).pages[row['source_page']-1];box=[float(x) for x in page.mediabox];rotation=int(page.get('/Rotate',0))%360;dpi=p.get('render_recipe',{}).get('dpi');width,height=round((box[2]-box[0])*dpi/72),round((box[3]-box[1])*dpi/72)
   if rotation in {90,270}:width,height=height,width
   recipe={'tool':'pdftoppm','first_page':row['source_page'],'last_page':row['source_page'],'dpi':dpi,'format':'png','box':'media_box','rotation':'source_applied','color':'rgb','background':'white','alpha':False,'metadata':'stripped'}
   if p.get('region')!={'kind':'full_media_box','points':box} or p.get('render_recipe')!=recipe or p.get('output_media_type')!='image/png' or p.get('quality_stage')!='provisional_full_page' or not isinstance(dpi,int) or dpi<=0 or p.get('output_dimensions')!={'width':width,'height':height}:fail('E_V2_ASSET','provisional-render')
 if counts!={'markdown_image_reference':16,'visual_region':100,'reviewed_provisional_full_page':10}:fail('E_V2_ASSET','counts')
 return {'mode':'canonical','reader':sum(row['disposition']=='reader' for row in assets),'counts':counts}
def v2_migration_schema(value):
 closed(value,{'inputs',*MIGRATION_DOMAINS,'new_reviewed_targets'},'v2-migration')
 inputs=value['inputs'];closed(inputs,{'frozen_v1_config','decision_evidence'},'v2-migration-inputs')
 closed(inputs['frozen_v1_config'],{'path','bytes','sha256'},'v2-migration-frozen-v1')
 if not isinstance(inputs['decision_evidence'],list):fail('E_V2_MIGRATION','evidence')
 for item in inputs['decision_evidence']:
  closed(item,{'path','bytes','sha256','kind'},'v2-migration-evidence')
  if item['kind'] not in {'kb_creator.semantic_unit_review.v2','kb_creator.user_review_registry.md','kb_creator.viral_boundary_ledger.v1','kb_creator.semantic_unit_closure.v2'}:fail('E_V2_MIGRATION','evidence-kind')
 for key,(_,_,count,outcomes) in MIGRATION_DOMAINS.items():
  rows=value[key]
  if key=='asset_rows' and rows and set(rows[0])=={'source_id','outcome','target_ids','decision_ref'}:
   v2_b1c4_migration_closure(rows,value['new_reviewed_targets']);continue
  if not isinstance(rows,list) or len(rows)!=count:fail('E_V2_MIGRATION','count')
  for row in rows:
   closed(row,{'source_id','source_row_sha256','outcome','final_target_ids','decision_ref'},'v2-migration-row')
   if not isinstance(row['source_id'],str) or not row['source_id'] or not isinstance(row['source_row_sha256'],str) or not HEX.fullmatch(row['source_row_sha256']) or row['outcome'] not in outcomes or not isinstance(row['final_target_ids'],list) or any(not isinstance(target,str) or not target for target in row['final_target_ids']) or len(row['final_target_ids'])!=len(set(row['final_target_ids'])) or row['decision_ref'] is not None and (not isinstance(row['decision_ref'],str) or not row['decision_ref']):fail('E_V2_MIGRATION','row')
   if row['outcome']=='retained_unchanged' and row['decision_ref'] is not None:fail('E_V2_MIGRATION','unchanged-decision')
   if row['outcome']!='retained_unchanged' and row['decision_ref'] is None and not (key=='xref_rows' and row['outcome']=='split'):fail('E_V2_MIGRATION','decision')
 if not isinstance(value['new_reviewed_targets'],list):fail('E_V2_MIGRATION','new-targets')
 if value['asset_rows'] and set(value['asset_rows'][0])=={'source_id','outcome','target_ids','decision_ref'}: return value
 for row in value['new_reviewed_targets']:
  closed(row,{'target_id','decision_ref'},'v2-migration-new-target')
  if not isinstance(row['target_id'],str) or not row['target_id'] or not isinstance(row['decision_ref'],str) or not row['decision_ref']:fail('E_V2_MIGRATION','new-target')
 return value
def v2_decision_catalogs(inputs,root):
 """Independently bind decision declarations; reference fields cannot declare ids."""
 singleton={'kb_creator.semantic_unit_review.v2','kb_creator.user_review_registry.md','kb_creator.semantic_unit_closure.v2'}
 occupied=set();declared={}
 def add(identifier,kind):
  prior=declared.get(identifier)
  if prior is not None and prior!=kind:fail('E_V2_MIGRATION','evidence-catalog')
  if prior is not None and kind=='boundary_unit_decision':fail('E_V2_MIGRATION','evidence-catalog')
  declared[identifier]=kind
 for item in inputs['decision_evidence']:
  evidence_kind=item['kind']
  if evidence_kind in singleton:
   if evidence_kind in occupied:fail('E_V2_MIGRATION','evidence-catalog')
   occupied.add(evidence_kind)
  try:text=v2_identity(root,{key:item[key] for key in ('path','bytes','sha256')},'migration-evidence').read_bytes().decode('utf8')
  except UnicodeDecodeError:fail('E_V2_MIGRATION','evidence-encoding')
  if evidence_kind=='kb_creator.semantic_unit_review.v2':
   try:e=json.loads(text)
   except json.JSONDecodeError:fail('E_V2_MIGRATION','evidence-json')
   if not isinstance(e,dict) or set(e) not in ({'schema','decisions'},{'schema','reviewer','input_identities','decisions'}) or e.get('schema')!=evidence_kind or not isinstance(e['decisions'],list):fail('E_V2_MIGRATION','evidence-schema')
   full='reviewer' in e
   if full and (not isinstance(e['reviewer'],str) or not e['reviewer'] or not isinstance(e['input_identities'],dict) or set(e['input_identities'])!={'pages_tree_sha256','user_registry_sha256','frozen_config_sha256'} or any(not HEX.fullmatch(str(v)) for v in e['input_identities'].values())):fail('E_V2_MIGRATION','evidence-identities')
   row_keys={'candidate_id','decision','reason','review_provenance'} if full else {'candidate_id'}
   if any(not isinstance(row,dict) or set(row)!=row_keys or full and (row['decision'] not in {'confirm','reject','adjusted_boundary'} or any(not isinstance(row[k],str) or not row[k] for k in ('reason','review_provenance'))) for row in e['decisions']):fail('E_V2_MIGRATION','evidence-catalog')
   ids=[row['candidate_id'] for row in e['decisions']]
   if not ids or any(not isinstance(x,str) or not x for x in ids) or len(ids)!=len(set(ids)):fail('E_V2_MIGRATION','evidence-catalog')
   for identifier in ids:add(identifier,'candidate_decision')
  elif evidence_kind=='kb_creator.viral_boundary_ledger.v1':
   try:e=json.loads(text)
   except json.JSONDecodeError:fail('E_V2_MIGRATION','evidence-json')
   if not isinstance(e,dict) or set(e)!={'schema','units','candidate_dispositions','deferred_nonblocking'} or e.get('schema')!=evidence_kind or not all(isinstance(e[x],list) for x in ('units','candidate_dispositions','deferred_nonblocking')):fail('E_V2_MIGRATION','evidence-schema')
   units=[];candidates=[]
   for row in e['units']:
    if not isinstance(row,dict) or set(row)!={'id','registry_refs'} or not isinstance(row['id'],str) or not row['id'] or not isinstance(row['registry_refs'],list) or any(not isinstance(x,str) or not x for x in row['registry_refs']):fail('E_V2_MIGRATION','evidence-catalog')
    units.append(row['id'])
    for identifier in row['registry_refs']:add(identifier,'registry_decision')
   if not units or len(units)!=len(set(units)):fail('E_V2_MIGRATION','evidence-catalog')
   for identifier in units:add(identifier,'boundary_unit_decision')
   for row in e['candidate_dispositions']:
    if not isinstance(row,dict) or set(row)!={'candidate_id','target_unit_id'} or not isinstance(row['candidate_id'],str) or not row['candidate_id'] or row['target_unit_id'] not in units:fail('E_V2_MIGRATION','evidence-catalog')
    candidates.append(row['candidate_id'])
   if len(candidates)!=len(set(candidates)):fail('E_V2_MIGRATION','evidence-catalog')
   for identifier in candidates:add(identifier,'candidate_decision')
   for row in e['deferred_nonblocking']:
    if not isinstance(row,dict) or set(row)!={'registry_ref'} or not isinstance(row['registry_ref'],str) or not row['registry_ref']:fail('E_V2_MIGRATION','evidence-catalog')
    add(row['registry_ref'],'registry_decision')
  elif evidence_kind=='kb_creator.semantic_unit_closure.v2':
   try:e=json.loads(text)
   except json.JSONDecodeError:fail('E_V2_MIGRATION','evidence-json')
   full_keys={'schema','candidate_count','decision_count','family_counts','required_family_coverage','unresolved_blocking_candidates','unresolved_blocking_count','blocking_registry_families_closed','deferred_nonblocking','excluded_audit_pages','identities'}
   if not isinstance(e,dict) or set(e) not in ({'schema','unresolved_blocking_candidates','deferred_nonblocking'},full_keys) or e.get('schema')!=evidence_kind or e['unresolved_blocking_candidates']!=[] or not isinstance(e['deferred_nonblocking'],list):fail('E_V2_MIGRATION','evidence-schema')
   full=set(e)==full_keys
   if full and (not isinstance(e['candidate_count'],int) or e['candidate_count']<=0 or e['candidate_count']!=e['decision_count'] or e['unresolved_blocking_count']!=0 or e['blocking_registry_families_closed'] is not True or e['excluded_audit_pages']!=[123,124] or not isinstance(e['identities'],dict) or set(e['identities'])!={'pages_tree_sha256','user_registry_sha256','frozen_config_sha256'} or any(not HEX.fullmatch(str(v)) for v in e['identities'].values()) or any(not isinstance(e[k],dict) or any(not isinstance(v,int) or v<0 for v in e[k].values()) for k in ('family_counts','required_family_coverage'))):fail('E_V2_MIGRATION','closure-evidence')
   ids=e['deferred_nonblocking'] if full else [row['id'] for row in e['deferred_nonblocking'] if isinstance(row,dict) and set(row)=={'id'}]
   if not ids or any(not isinstance(x,str) or not x for x in ids) or len(ids)!=len(set(ids)):fail('E_V2_MIGRATION','evidence-catalog')
   for identifier in ids:add(identifier,'registry_decision')
  else:
   ids=re.findall(r'^### ((?:OUT|PROC|ENH)-[0-9]{3}) — .+$',text,re.M)
   if not ids or len(ids)!=len(set(ids)):fail('E_V2_MIGRATION','evidence-catalog')
   for identifier in ids:add(identifier,'registry_decision')
 return set(declared)
def v2_migration(cfg,root):
 migration=v2_migration_schema(cfg['migration']);inputs=migration['inputs']
 v1_path=v2_identity(root,inputs['frozen_v1_config'],'migration-frozen-v1')
 v1=parsed(v1_path)
 refs=v2_decision_catalogs(inputs,root)
 # Legacy flat aggregation is retained below for audit context but deliberately
 # disabled: it cannot distinguish valid corroboration from class collisions.
 '''
 for item in inputs['decision_evidence']:
  try:text=v2_identity(root,{key:item[key] for key in ('path','bytes','sha256')},'migration-evidence').read_bytes().decode('utf8')
  except UnicodeDecodeError:fail('E_V2_MIGRATION','evidence-encoding')
  if item['kind']=='kb_creator.semantic_unit_review.v2':
   try:e=json.loads(text)
   except json.JSONDecodeError:fail('E_V2_MIGRATION','evidence-json')
   if not isinstance(e,dict) or set(e)!={'schema','decisions'} or e.get('schema')!='kb_creator.semantic_unit_review.v2' or not isinstance(e['decisions'],list):fail('E_V2_MIGRATION','evidence-schema')
   ids=[row.get('candidate_id') for row in e['decisions'] if isinstance(row,dict) and set(row)=={'candidate_id'}]
   if not ids or any(not isinstance(x,str) or not x for x in ids) or len(ids)!=len(set(ids)):fail('E_V2_MIGRATION','evidence-catalog')
   refs.update(ids)
  elif item['kind']=='kb_creator.viral_boundary_ledger.v1':
   try:e=json.loads(text)
   except json.JSONDecodeError:fail('E_V2_MIGRATION','evidence-json')
   if not isinstance(e,dict) or set(e)!={'schema','units','candidate_dispositions','deferred_nonblocking'} or e.get('schema')!='kb_creator.viral_boundary_ledger.v1' or not all(isinstance(e[x],list) for x in ('units','candidate_dispositions','deferred_nonblocking')):fail('E_V2_MIGRATION','evidence-schema')
   units=[]
   for row in e['units']:
    if not isinstance(row,dict) or set(row)!={'id','registry_refs'} or not isinstance(row['id'],str) or not row['id'] or not isinstance(row['registry_refs'],list) or any(not isinstance(x,str) or not x for x in row['registry_refs']):fail('E_V2_MIGRATION','evidence-catalog')
    units.append(row['id']);refs.update(row['registry_refs'])
   if not units or len(units)!=len(set(units)):fail('E_V2_MIGRATION','evidence-catalog')
   refs.update(units)
   for row in e['candidate_dispositions']:
    if not isinstance(row,dict) or set(row)!={'candidate_id','target_unit_id'} or not isinstance(row['candidate_id'],str) or row['target_unit_id'] not in units:fail('E_V2_MIGRATION','evidence-catalog')
    refs.add(row['candidate_id'])
   for row in e['deferred_nonblocking']:
    if not isinstance(row,dict) or set(row)!={'registry_ref'} or not isinstance(row['registry_ref'],str):fail('E_V2_MIGRATION','evidence-catalog')
    refs.add(row['registry_ref'])
  elif item['kind']=='kb_creator.semantic_unit_closure.v2':
   try:e=json.loads(text)
   except json.JSONDecodeError:fail('E_V2_MIGRATION','evidence-json')
   if not isinstance(e,dict) or set(e)!={'schema','unresolved_blocking_candidates','deferred_nonblocking'} or e.get('schema')!='kb_creator.semantic_unit_closure.v2' or e['unresolved_blocking_candidates']!=[] or not isinstance(e['deferred_nonblocking'],list):fail('E_V2_MIGRATION','evidence-schema')
   ids=[row['id'] for row in e['deferred_nonblocking'] if isinstance(row,dict) and set(row)=={'id'}]
   if not ids or any(not isinstance(x,str) or not x for x in ids) or len(ids)!=len(set(ids)):fail('E_V2_MIGRATION','evidence-catalog')
   refs.update(ids)
  else:
   ids=re.findall(r'^### ((?:OUT|PROC|ENH)-[0-9]{3}) — .+$',text,re.M)
   if not ids or len(ids)!=len(set(ids)):fail('E_V2_MIGRATION','evidence-catalog')
   refs.update(ids)
 '''
 targets=set()
 for key,(v1_key,id_key,count,_) in MIGRATION_DOMAINS.items():
  source=v1.get(v1_key);rows=migration[key]
  if not isinstance(source,list) or len(source)!=count:fail('E_V2_MIGRATION','frozen-domain')
  expected={f'{v1_key}:{row[id_key]}':row for row in source if isinstance(row,dict) and id_key in row};got={row['source_id']:row for row in rows}
  if len(expected)!=count or len(got)!=count or set(expected)!=set(got):fail('E_V2_MIGRATION','source-closure')
  for source_id,row in got.items():
   if key=='asset_rows' and set(row)=={'source_id','outcome','target_ids','decision_ref'}:
    if row['decision_ref'] is not None and row['decision_ref'] not in refs:fail('E_V2_MIGRATION','unknown-decision')
    targets.update(row['target_ids']);continue
   if row['source_row_sha256']!=v2_canonical_row(expected[source_id]):fail('E_V2_MIGRATION','source-row')
   if row['decision_ref'] is not None and row['decision_ref'] not in refs:fail('E_V2_MIGRATION','unknown-decision')
   # A2 has no A3 final-field projection yet: closed pending targets are the
   # only honest representation, and input binding rejects them for preflight.
   if row['outcome']=='retained_unchanged' and cfg['scenario_id']!='viral' and row['final_target_ids']!=[f'pending_a3:{source_id}']:fail('E_V2_MIGRATION','unchanged-preservation')
   if v1_key=='source_disposition' and expected[source_id]['page'] in {123,124} and (row['outcome']!='excluded_advertising' or row['final_target_ids']):fail('E_V2_MIGRATION','advertising-exclusion')
   if v1_key=='assets' and expected[source_id]['source_page'] in {123,124} and row['final_target_ids']:fail('E_V2_MIGRATION','advertising-asset')
   targets.update(row['final_target_ids'])
 new=set()
 for row in migration['new_reviewed_targets']:
  if row['target_id'] in new or row['target_id'] in targets or row['decision_ref'] not in refs:fail('E_V2_MIGRATION','new-target-closure')
  new.add(row['target_id'])
 materialized={*(f'hierarchy:{row["anchor"]}' for row in cfg['hierarchy']),*(f'assets:{row["asset_id"]}' for row in cfg['assets']),*(f'xrefs:{row["xref_id"]}' for row in cfg['xrefs'])}
 if not materialized<=targets|new or any(target.startswith('pending_a3:') for target in targets|new):fail('E_V2_MIGRATION','orphan-target')
 # Keep this independent from the builder: aggregate target membership cannot
 # prove that a concrete xref or hierarchy row names its own materialization.
 for namespace,rows,identity_key in (('hierarchy',cfg['hierarchy'],'anchor'),('xrefs',cfg['xrefs'],'xref_id')):
  for row in rows:
   target=f'{namespace}:{row[identity_key]}'
   if row['migration_row_id']!=target or target not in targets|new:fail('E_V2_MIGRATION','materialized-target')
 return migration
def _v3_resolve(base,record,label):
 closed(record,{'path','bytes','sha256'},'v3-'+label);value=record['path']
 if not safe(value):fail('E_V3_PATH',label)
 path=(Path(base)/Path(value)).resolve()
 try:path.relative_to(Path(base).resolve())
 except ValueError:fail('E_V3_PATH',label)
 if not path.is_file() or rp(path) or path.stat().st_size!=record['bytes'] or not HEX.fullmatch(str(record['sha256'])) or sha(path)!=record['sha256']:fail('E_V3_IDENTITY',label)
 return path
def _v3_output_path(base,value,label):
 raw=os.fspath(value);relative=Path(raw)
 if not raw or '\\' in raw or ':' in raw or relative.is_absolute() or any(part in {'','.','..'} for part in relative.parts):fail('E_V3_PATH',label)
 authority=Path(base).resolve();lexical=authority/relative
 if not lexical.parent.is_dir():fail('E_V3_PATH',label+'-parent')
 chain=[authority]
 current=lexical.parent
 while current!=authority:
  chain.append(current);current=current.parent
 for component in chain:
  if component.exists() and rp(component):fail('E_V3_PATH',label+'-reparse')
 if os.path.lexists(lexical) and rp(lexical):fail('E_V3_PATH',label+'-reparse')
 resolved=lexical.resolve()
 try:resolved.relative_to(authority)
 except ValueError:fail('E_V3_PATH',label+'-escape')
 if not resolved.is_dir() or rp(resolved):fail('E_V3_CANDIDATE','missing-or-reparse')
 return resolved
def _v3_seal(value,key,label):
 digest=value.get(key) if isinstance(value,dict) else None
 if not isinstance(digest,str) or not HEX.fullmatch(digest):fail('E_V3_SEAL',label)
 unsigned={name:item for name,item in value.items() if name!=key}
 actual=hashlib.sha256(json.dumps(unsigned,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode('utf8')).hexdigest().upper()
 if actual!=digest:fail('E_V3_SEAL',label)
def _v3_profile(path):
 value=parsed(path);closed(value,{'schema','scenario_id','inputs','projection','required_qa'},'v3-config')
 if value['schema']!=V3_SCHEMA or not isinstance(value['scenario_id'],str) or not re.fullmatch(r'[a-z0-9][a-z0-9._-]*',value['scenario_id']):fail('E_V3_SCHEMA','config')
 closed(value['inputs'],{'publication_contract','reconstruction_inventory','reconstruction_acceptance','reconstructed_en'},'v3-inputs')
 for name,row in value['inputs'].items():closed(row,{'path','bytes','sha256'},'v3-input-'+name)
 closed(value['projection'],{'output_name','excluded_source_pages','page_marker_policy','anchor_policy','asset_policy'},'v3-projection')
 if value['projection']['output_name']!='MASTER_EN.md' or value['projection']['page_marker_policy']!='source_page_comment_v1' or value['projection']['anchor_policy']!='preserve_v1' or value['projection']['asset_policy']!='copy_markdown_references_v1':fail('E_V3_SCHEMA','projection')
 excluded=value['projection']['excluded_source_pages']
 if not isinstance(excluded,list) or len(excluded)!=len(set(excluded)) or any(not isinstance(page,int) or isinstance(page,bool) or page<1 for page in excluded):fail('E_V3_SCHEMA','excluded-pages')
 if not isinstance(value['required_qa'],list) or not value['required_qa'] or len(value['required_qa'])!=len(set(value['required_qa'])) or any(not isinstance(item,str) or not item for item in value['required_qa']):fail('E_V3_SCHEMA','required-qa')
 return value
def _v3_project(text,excluded):
 pattern=re.compile(r'(?m)^<!--\s*source-page-(\d{3,})\s*-->\s*$');matches=list(pattern.finditer(text));pages=[]
 if not matches:
  if excluded:fail('E_V3_SCOPE','excluded-without-markers')
  return text,[]
 result=[text[:matches[0].start()]]
 for index,match in enumerate(matches):
  page=int(match.group(1));pages.append(page);end=matches[index+1].start() if index+1<len(matches) else len(text)
  if page not in excluded:result.append(text[match.start():end])
 if pages!=sorted(set(pages)):fail('E_V3_SCOPE','source-page-order')
 if not set(excluded).issubset(pages):fail('E_V3_SCOPE','unknown-excluded-page')
 return ''.join(result),pages
def _v3_plain_prose_line(line):
 stripped=line.strip()
 if not stripped or line.startswith(('    ','\t')) or line.endswith('  '):return False
 if re.match(r'^(?:#{1,6}\s|>|[-+*]\s|\d+[.)]\s|```|~~~|\||!\[|<)',stripped):return False
 return True
def _v3_normalize_page_boundaries(text):
 lines=text.splitlines();transitions=[];index=0
 while index<len(lines):
  marker=V3_PAGE_MARKER_LINE.fullmatch(lines[index].strip())
  if not marker or index<2 or index+2>=len(lines) or lines[index-1] or lines[index+1]:index+=1;continue
  previous=next((V3_PAGE_MARKER_LINE.fullmatch(lines[pos].strip()) for pos in range(index-1,-1,-1) if V3_PAGE_MARKER_LINE.fullmatch(lines[pos].strip())),None)
  from_page=int(previous.group(1)) if previous else None;to_page=int(marker.group(1))
  if from_page is None or to_page!=from_page+1:index+=1;continue
  left_end=index-2;left_start=left_end
  while left_start and lines[left_start-1]:left_start-=1
  right_start=index+2;right_end=right_start+1
  while right_end<len(lines) and lines[right_end]:right_end+=1
  left=lines[left_start:left_end+1];right=lines[right_start:right_end]
  if not left or not right or not all(_v3_plain_prose_line(line) for line in (*left,*right)):index+=1;continue
  left_tail=left[-1].rstrip();right_head=right[0].lstrip()
  if not right_head or not right_head[0].isalpha() or not right_head[0].islower():index+=1;continue
  if re.search(r'[.!?\u2026:;][\"\'\u201d\u2019)\]}]*$',left_tail):index+=1;continue
  if left_tail.endswith('-'):
   if len(left_tail)<2 or not left_tail[-2].isalpha():index+=1;continue
   joined=left_tail[:-1]+right_head;mode='dehyphenated_word'
  else:
   if not left_tail or not left_tail[-1].isalpha():index+=1;continue
   joined=left_tail+' '+right_head;mode='continued_prose'
  transitions.append({'from_page':from_page,'to_page':to_page,'mode':mode,'left_line_sha256':hashlib.sha256(left_tail.encode('utf8')).hexdigest().upper(),'right_line_sha256':hashlib.sha256(right_head.encode('utf8')).hexdigest().upper()})
  replacement=[*left[:-1],joined,*right[1:],'',lines[index]];lines[left_start:right_end]=replacement;index=left_start+len(replacement)
 return '\n'.join(lines)+('\n' if text.endswith('\n') else ''),transitions
def _v3_refs(text):return [match.group(1) for match in re.finditer(r'!\[[^\]]*\]\(([^)\s]+)(?:\s+"[^"]*")?\)',text)]
def v3_preflight(contract,reconstruction_package,publication_config,source_pdf=None):
 if source_pdf not in (None,''):fail('E_V3_AUTHORITY','source-pdf-forbidden')
 cfg_path=Path(publication_config).resolve();base=cfg_path.parent;cfg=_v3_profile(cfg_path)
 contract_path=_v3_resolve(base,cfg['inputs']['publication_contract'],'contract')
 if contract_path!=Path(contract).resolve():fail('E_V3_IDENTITY','contract-cli')
 contract_value=parsed(contract_path)
 if contract_value.get('schema')!='kb_creator.scenario_publication_contract.v1' or contract_value.get('scenario',{}).get('id')!=cfg['scenario_id']:fail('E_V3_SCHEMA','contract-scenario')
 inventory_path=_v3_resolve(base,cfg['inputs']['reconstruction_inventory'],'inventory');inventory_value=parsed(inventory_path);_v3_seal(inventory_value,'inventory_sha256','inventory')
 source=_v3_resolve(base,cfg['inputs']['reconstructed_en'],'reconstructed-en');package=Path(reconstruction_package).resolve()
 if not package.is_dir() or rp(package):fail('E_V3_IDENTITY','package')
 try:source.relative_to(package)
 except ValueError:fail('E_V3_AUTHORITY','reconstructed-en-outside-package')
 artifact=next((row for row in inventory_value.get('artifacts',[]) if isinstance(row,dict) and row.get('role')=='reconstructed_en'),None)
 if not artifact:fail('E_V3_IDENTITY','inventory-source')
 inventory_source=_v3_resolve(inventory_path.parent,{key:artifact.get(key) for key in ('path','bytes','sha256')},'inventory-source')
 if inventory_source!=source:fail('E_V3_IDENTITY','inventory-source')
 acceptance_path=_v3_resolve(base,cfg['inputs']['reconstruction_acceptance'],'acceptance');acceptance=parsed(acceptance_path);_v3_seal(acceptance,'receipt_sha256','acceptance')
 closed(acceptance,{'schema','scenario_id','artifact_kind','candidate','producer_stage','evidence','decision','decision_at_utc','user_decision_reference','recorder_role','receipt_sha256'},'v3-acceptance')
 if acceptance['schema']!='kb_creator.artifact_acceptance.v1' or acceptance['scenario_id']!=cfg['scenario_id'] or acceptance['artifact_kind']!='reconstructed_en' or acceptance['decision']!='accepted' or acceptance['recorder_role']!='main_orchestrator':fail('E_V3_AUTHORITY','acceptance')
 accepted_candidate=_v3_resolve(inventory_path.parent,acceptance['candidate'],'candidate')
 if accepted_candidate!=source:fail('E_V3_AUTHORITY','acceptance-candidate')
 for label,row in [('producer',acceptance['producer_stage']),*[(f'evidence-{index}',row) for index,row in enumerate(acceptance['evidence'])]]:_v3_resolve(inventory_path.parent,row,label)
 master,pages=_v3_project(source.read_text(encoding='utf8'),set(cfg['projection']['excluded_source_pages']));master,transitions=_v3_normalize_page_boundaries(master);anchors=re.findall(r'<a id="([A-Za-z0-9_.:-]+)"></a>',master)
 if len(anchors)!=len(set(anchors)):fail('E_V3_SEMANTIC','duplicate-anchor')
 for reference in _v3_refs(master):
  if not safe(reference):fail('E_V3_PATH','asset-reference')
  asset=(source.parent/Path(reference)).resolve()
  try:asset.relative_to(package)
  except ValueError:fail('E_V3_PATH','asset-reference')
  if not asset.is_file() or rp(asset):fail('E_V3_IDENTITY','asset-reference')
 derived={'source_pages':len(set(pages)),'excluded_pages':len(cfg['projection']['excluded_source_pages']),'page_boundary_joins':len(transitions),'headings':sum(line.lstrip().startswith('#') for line in master.splitlines()),'anchors':len(anchors),'assets':len(set(_v3_refs(master)))}
 return {'status':'preflight_passed','scenario_id':cfg['scenario_id'],'publication_config_sha256':sha(cfg_path),'publication_contract_sha256':sha(contract_path),'reconstruction_inventory_sha256':inventory_value['inventory_sha256'],'reconstruction_acceptance_sha256':acceptance['receipt_sha256'],'derived':derived}
def verify_v3_candidate(contract,reconstruction_package,publication_config,target_value,source_pdf=None):
 pre=v3_preflight(contract,reconstruction_package,publication_config,source_pdf);cfg_path=Path(publication_config).resolve();base=cfg_path.parent;cfg=_v3_profile(cfg_path);source=_v3_resolve(base,cfg['inputs']['reconstructed_en'],'reconstructed-en');package=Path(reconstruction_package).resolve()
 out=_v3_output_path(base,target_value,'candidate-target')
 allowed={'MASTER_EN.md','MASTER_EN.provenance.json','SOURCE_DISPOSITION.json','ASSET_MANIFEST.json','MASTER_EN.qa.json','INVENTORY.json'}
 children={path.name for path in out.iterdir()}
 if not allowed.issubset(children) or children-allowed-{'assets'}:fail('E_V3_CANDIDATE','topology')
 expected,pages=_v3_project(source.read_text(encoding='utf8'),set(cfg['projection']['excluded_source_pages']));expected,transitions=_v3_normalize_page_boundaries(expected)
 if not expected.endswith('\n'):expected+='\n'
 if (out/'MASTER_EN.md').read_text(encoding='utf8')!=expected:fail('E_V3_SEMANTIC','master-en')
 manifest=canonical(out/'ASSET_MANIFEST.json');closed(manifest,{'schema','scenario_id','assets','summary'},'v3-asset-manifest')
 refs=list(dict.fromkeys(_v3_refs(expected)));assets=manifest['assets']
 if manifest['schema']!='kb_creator.master_en_asset_manifest.v3' or manifest['scenario_id']!=cfg['scenario_id'] or manifest['summary']!={'total':len(refs)} or [row.get('path') for row in assets]!=refs:fail('E_V3_ASSET','manifest')
 for row in assets:
  closed(row,{'path','bytes','sha256'},'v3-asset');path=out/Path(row['path'])
  if not safe(row['path']) or not path.is_file() or rp(path) or path.stat().st_size!=row['bytes'] or sha(path)!=row['sha256']:fail('E_V3_ASSET',row.get('path'))
  original=(source.parent/Path(row['path'])).resolve()
  try:original.relative_to(package)
  except ValueError:fail('E_V3_ASSET','source-escape')
  if not original.is_file() or sha(original)!=row['sha256']:fail('E_V3_ASSET','source-drift')
 disposition=canonical(out/'SOURCE_DISPOSITION.json');closed(disposition,{'schema','scenario_id','pages','summary'},'v3-disposition')
 excluded=set(cfg['projection']['excluded_source_pages']);unique=sorted(set(pages));expected_disposition={'schema':'kb_creator.source_disposition.v3','scenario_id':cfg['scenario_id'],'pages':[{'page':page,'publication_disposition':'excluded_by_config' if page in excluded else 'reader','published':page not in excluded} for page in unique],'summary':{'source_pages':len(unique),'reader_pages':len(set(unique)-excluded),'excluded_pages':len(excluded)}}
 if disposition!=expected_disposition:fail('E_V3_SCOPE','disposition')
 provenance=canonical(out/'MASTER_EN.provenance.json');closed(provenance,{'schema','scenario_id','inputs','projection','master_en','derived','page_boundary_transitions'},'v3-provenance')
 master_identity={'path':'MASTER_EN.md','bytes':(out/'MASTER_EN.md').stat().st_size,'sha256':sha(out/'MASTER_EN.md')}
 if provenance!={'schema':'kb_creator.master_en_provenance.v3','scenario_id':cfg['scenario_id'],'inputs':cfg['inputs'],'projection':cfg['projection'],'master_en':master_identity,'derived':pre['derived'],'page_boundary_transitions':transitions}:fail('E_V3_PROVENANCE','content')
 qa=canonical(out/'MASTER_EN.qa.json');closed(qa,{'schema','scenario_id','status','candidate_state','required_checks','derived','errors'},'v3-qa')
 if qa!={'schema':'kb_creator.master_en_qa.v3','scenario_id':cfg['scenario_id'],'status':'pass','candidate_state':'awaiting_master_en_acceptance','required_checks':cfg['required_qa'],'derived':pre['derived'],'errors':[]}:fail('E_V3_QA','content')
 inv=canonical(out/'INVENTORY.json');closed(inv,{'schema','algorithm','scope','rows','file_count','total_bytes','inventory_sha256'},'v3-inventory');rows,total,digest=inventory(out)
 if inv!={'schema':'kb_creator.candidate_inventory.v1','algorithm':ALGO,'scope':'all regular candidate files except INVENTORY.json','rows':rows,'file_count':len(rows),'total_bytes':total,'inventory_sha256':digest}:fail('E_V3_INVENTORY','content')
 return {'status':'verified_candidate_pending_process_and_external_gates','scenario_id':cfg['scenario_id'],'candidate_inventory_sha256':digest,'inventory_file_sha256':sha(out/'INVENTORY.json'),'master_en_sha256':sha(out/'MASTER_EN.md'),'publication_config_sha256':pre['publication_config_sha256'],'derived':pre['derived']}


def preflight(contract,reconstruction_package,publication_config,source_pdf):
 cfg=parsed(publication_config)
 if cfg.get('schema')==V3_SCHEMA:return v3_preflight(contract,reconstruction_package,publication_config,source_pdf)
 for path in (contract,publication_config,source_pdf):
  if not Path(path).is_file() or rp(path): fail('E_C2B_IDENTITY','input')
 if not Path(reconstruction_package).is_dir() or rp(reconstruction_package): fail('E_C2B_IDENTITY','reconstruction')
 if cfg.get('schema')==V2_SCHEMA:
  v2_contract(cfg)
  v2_input_binding(cfg,root_for(publication_config),source_pdf,reconstruction_package)
  audit=v2_b1c4_asset_audit(root_for(publication_config))
  return {'status':'preflight_passed','scenario_id':cfg.get('scenario_id'),'publication_config_sha256':sha(publication_config),'asset_audit':audit}
 if cfg.get('accepted_reconstruction',{}).get('inventory_sha256')!=package_hash(reconstruction_package): fail('E_C2B_IDENTITY','reconstruction-inventory')
 return {'status':'preflight_passed','scenario_id':cfg.get('scenario_id'),'publication_config_sha256':sha(publication_config)}

def v2_b1c4_asset_audit(root):
 """Verifier-owned B1c4 inventory check; never consults builder/author code."""
 root=Path(root);v1=parsed(root/'kb_creator/working/viral/master_en/publication_config_v1.json')
 package=root/'kb_creator/working/viral/source_reconstruction/20260901_step6a_reconstructed_en_package_v4';manifest=package/'ASSET_MANIFEST.json';comparison=root/'kb_creator/working/viral/source_reconstruction/20260901_step6a_mineru_three_view_full/comparison/comparison.json'
 if sha(manifest)!='914A2C8B46401830EDBDEADDDDA24C7A8C0B6442F2775C439A79CC5529D283E9' or sha(comparison)!='5A4DB5DB697B1E483926AB1DAB387CB496EF0539DC76EAD51B830F5DCF1862F0':fail('E_V2_ASSET','evidence')
 frozen=v1.get('assets');entries=parsed(manifest).get('assets')
 if not isinstance(frozen,list) or len(frozen)!=123 or not isinstance(entries,list) or len(entries)!=121:fail('E_V2_ASSET','inventory')
 found={row.get('sha256','').upper():row for row in entries if isinstance(row,dict)};excluded={row['asset_id'] for row in frozen if row.get('source_page') in {123,124}}
 reclassified={'viral-accepted-6acc049ed2ad40ebed064312a87ddfce5a404f4fc2487ea1721c656ed541c419','viral-accepted-647b583cd53fbfdaab7ac6d9643a81bbd5145c125d628c7074b02db0c9f7888b','viral-accepted-eda9c6f6d6ef94ed41034cd12401547ed37101ef2f8b1ebf30d9602b87db71ab','viral-accepted-21704f0d57843965013f5eccfa36bcd64321dcc1513cd7d99dead8627d58994e','viral-accepted-b2ba43b7e57f4c9972780be961deab50d72ea311f795285da15712ba29b6e30e','viral-accepted-af48429e4ab502e7fc33a545039dab60a3e4e28a8c03a29f56ff57b9280cdd12','viral-accepted-adb4ff51bd5ebff464834e0fb324310c281eb20d2c4b0f4e82d1fbaf3ef72541','viral-accepted-f7ce778cc1eb05cb6fef0f26457d06e68019ee30c76a5723f259dc82b89b321d','viral-accepted-e1c168ca34db2f98a27391e749f08a0fcdda832034d68e5fd0fbc38b00f584dc','viral-accepted-5d2410afd9a6593cdce0d7f0d411835cf4a726551a1b1e18b6f79d04ed42230b','viral-accepted-331f4d575265e02a4ba97b4e204dbbb20b648e9b62d44eb47ea11ab6998c00d3','viral-accepted-92c65562fe49c02049e4b40e4a278b667e1361568455fdd89a724389a8d01d50','viral-accepted-07982af9981b82074567f2fa5d976b00cb40a0331f01438352f9fd59fc864aa4','viral-accepted-9d7ebb95113ecd5d9114224cff873b14f2db563d61015978164a78e4ff05953f','viral-accepted-1ae1543b9ff31ba9d7c4271ae01d86f05fb722c00e9f7851ce1dffc820aee3b8','viral-accepted-dcf1f2f6dd9540217155f01d5b03d965aedef98d965c2a33e987f0f5996eb166'}
 outcomes=[];binaries=0
 for row in frozen:
  item=found.get(str(row.get('sha256','')).upper())
  if item:
   path=package/item['stored_path']
   if not path.is_file() or sha(path)!=item['sha256']:fail('E_V2_ASSET','binary')
   binaries+=1
  aid=row['asset_id'];outcomes.append('excluded_advertising' if aid in excluded else 'reclassified' if aid in reclassified else 'retained_rebound' if aid.endswith(('b90cb9a3752383888c733905588e9c3859b113e47f1f457057c72e33689a7585','da0cac1c9c0c880a75d3be69c59e965d0b7b0f223f16a077072786c8af30083e')) else 'retained_unchanged')
 counts={key:outcomes.count(key) for key in ('retained_unchanged','retained_rebound','reclassified','excluded_advertising')}
 if counts!={'retained_unchanged':99,'retained_rebound':2,'reclassified':16,'excluded_advertising':6}:fail('E_V2_ASSET','partition')
 return {'counts':counts,'path_binaries':binaries}

def v2_b1c4_expected_assets(root):
 """Verifier-owned recomputation of every B1c4 declaration from evidence."""
 root=Path(root);package=root/'kb_creator/working/viral/source_reconstruction/20260901_step6a_reconstructed_en_package_v4';manifest_path=package/'ASSET_MANIFEST.json';comparison_path=root/'kb_creator/working/viral/source_reconstruction/20260901_step6a_mineru_three_view_full/comparison/comparison.json';source_pdf=root/'kb_creator/working/viral/source/Call_of_Cthulhu_Viral.pdf'
 frozen=parsed(root/'kb_creator/working/viral/master_en/publication_config_v1.json')['assets'];manifest=parsed(manifest_path)['assets'];comparison=parsed(comparison_path);by_digest={row['sha256'].upper():row for row in manifest}
 reclassified={'viral-accepted-6acc049ed2ad40ebed064312a87ddfce5a404f4fc2487ea1721c656ed541c419','viral-accepted-647b583cd53fbfdaab7ac6d9643a81bbd5145c125d628c7074b02db0c9f7888b','viral-accepted-eda9c6f6d6ef94ed41034cd12401547ed37101ef2f8b1ebf30d9602b87db71ab','viral-accepted-21704f0d57843965013f5eccfa36bcd64321dcc1513cd7d99dead8627d58994e','viral-accepted-b2ba43b7e57f4c9972780be961deab50d72ea311f795285da15712ba29b6e30e','viral-accepted-af48429e4ab502e7fc33a545039dab60a3e4e28a8c03a29f56ff57b9280cdd12','viral-accepted-adb4ff51bd5ebff464834e0fb324310c281eb20d2c4b0f4e82d1fbaf3ef72541','viral-accepted-f7ce778cc1eb05cb6fef0f26457d06e68019ee30c76a5723f259dc82b89b321d','viral-accepted-e1c168ca34db2f98a27391e749f08a0fcdda832034d68e5fd0fbc38b00f584dc','viral-accepted-5d2410afd9a6593cdce0d7f0d411835cf4a726551a1b1e18b6f79d04ed42230b','viral-accepted-331f4d575265e02a4ba97b4e204dbbb20b648e9b62d44eb47ea11ab6998c00d3','viral-accepted-92c65562fe49c02049e4b40e4a278b667e1361568455fdd89a724389a8d01d50','viral-accepted-07982af9981b82074567f2fa5d976b00cb40a0331f01438352f9fd59fc864aa4','viral-accepted-9d7ebb95113ecd5d9114224cff873b14f2db563d61015978164a78e4ff05953f','viral-accepted-1ae1543b9ff31ba9d7c4271ae01d86f05fb722c00e9f7851ce1dffc820aee3b8','viral-accepted-dcf1f2f6dd9540217155f01d5b03d965aedef98d965c2a33e987f0f5996eb166'};rebound={'viral-accepted-b90cb9a3752383888c733905588e9c3859b113e47f1f457057c72e33689a7585','viral-accepted-da0cac1c9c0c880a75d3be69c59e965d0b7b0f223f16a077072786c8af30083e'}
 intervals={page:[] for page in range(1,123)}
 for name,expected_hash in (('boundary_ledger_pages_001_040.json','8C0A666D962C879C62B7168B60AB717EA04F833FFE728446F150F64FCB24DDAF'),('boundary_ledger_pages_041_068.json','8673868ED762E327517891D7C72DBA21A5C88F1A4173EBB0EFF597D30453EF13'),('boundary_ledger_pages_069_122.json','14338236CDB2AAE6213CCE5F36DA93C661F2DF35D9F7E96F8346C770BF00CFD1')):
  ledger=root/'kb_creator/working/viral/master_en/review_evidence/20260902_user_review_remediation_v1'/name
  if sha(ledger)!=expected_hash:fail('E_V2_ASSET','ledger-identity')
  for unit in parsed(ledger)['units']:
   for segment in unit.get('source_segments',[]):
    page=segment['page'];raw=(package/'pages'/segment['path']).read_bytes();lines=[];offset=0
    for line in raw.decode('utf8').splitlines(keepends=True):offset+=len(line.encode('utf8'));lines.append(offset)
    begin,end=segment['start_line']-1,segment['end_line']
    if begin<0 or end>len(lines) or begin>=end:
     decoded=raw.decode('utf8').splitlines();matches=[(left,right) for left in range(len(decoded)) for right in range(left+1,len(decoded)+1) if hashlib.sha256('\n'.join(decoded[left:right]).encode('utf8')).hexdigest().upper()==segment['sha256_lf_lines']]
     if len(matches)!=1:fail('E_V2_ASSET','ledger-span')
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
   provenance={'kind':'reviewed_provisional_full_page','source_pdf_identity':{'path':str(source_pdf.relative_to(root)).replace('\\','/'),'bytes':source_pdf.stat().st_size,'sha256':sha(source_pdf)},'physical_page':page,'page_index_zero_based':page-1,'region':{'kind':'full_media_box','points':[0,0,612,792]},'render_recipe':{'tool':'pdftoppm','first_page':page,'last_page':page,'dpi':200,'format':'png','box':'media_box','rotation':'source_applied','color':'rgb','background':'white','alpha':False,'metadata':'stripped'},'output_media_type':'image/png','output_dimensions':{'width':1700,'height':2200},'quality_stage':'provisional_full_page'};result[aid]={'asset_id':aid,'disposition':'reader','source_page':page,'binary':None,'provenance':provenance,'migration_outcome':outcome};continue
  entry=by_digest[source['sha256'].upper()];path=package/entry['stored_path']
  try:
   with Image.open(path) as image:image.load();media={'JPEG':'image/jpeg','PNG':'image/png'}[image.format];dimensions={'width':image.width,'height':image.height}
  except (OSError,KeyError):fail('E_V2_ASSET','expected-binary')
  binary={'path':str(path.relative_to(root)).replace('\\','/'),'bytes':path.stat().st_size,'sha256':sha(path),'media_type':media,'dimensions':dimensions};span=spans.get(binary['sha256'])
  if span:provenance={'kind':'markdown_image_reference','span_id':span['span_id'],'page_markdown_identity':{'path':str((package/span['path']).relative_to(root)).replace('\\','/'),'bytes':(package/span['path']).stat().st_size,'sha256':sha(package/span['path'])},'start_byte':span['start_byte'],'end_byte':span['end_byte'],'start_char':span['start_char'],'end_char':span['end_char'],'marker_sha256':hashlib.sha256(span['raw']).hexdigest().upper()}
  else:
   selected=[(view,block) for view,item in comparison['views'].items() for block in item['blocks'] if entry['source_path'] in block.get('assets',[]) and view==entry['view']]
   if len(selected)!=1:fail('E_V2_ASSET','expected-comparison')
   view,block=selected[0];provenance={'kind':'visual_region','asset_manifest_identity':{'path':str(manifest_path.relative_to(root)).replace('\\','/'),'bytes':manifest_path.stat().st_size,'sha256':sha(manifest_path)},'asset_manifest_row_sha256':v2_canonical_row(entry),'comparison_identity':{'path':str(comparison_path.relative_to(root)).replace('\\','/'),'bytes':comparison_path.stat().st_size,'sha256':sha(comparison_path)},'selected_view':view,'source_asset_reference':entry['source_path'],'raw_index':block['raw_index'],'block_type':block['type'],'source_page':block['source_page'],'bbox':block['bbox'],'comparison_block_sha256':v2_canonical_row(block)}
  result[aid]={'asset_id':aid,'disposition':'evidence_only' if outcome=='reclassified' else ('reader' if outcome=='retained_rebound' else source['representation']),'source_page':page,'binary':binary,'provenance':provenance,'migration_outcome':outcome}
 for page,name in zip((106,107,112,114,116,118,120,122,26),('map-ground-floor-basement','map-ground-floor-basement','pregen-marco-back','pregen-corrina-back','pregen-enoch-back','pregen-peter-back','pregen-ku-hyeon-back','pregen-blank-back','isola-di-malamente-opening')):
   provenance={'kind':'reviewed_provisional_full_page','source_pdf_identity':{'path':str(source_pdf.relative_to(root)).replace('\\','/'),'bytes':source_pdf.stat().st_size,'sha256':sha(source_pdf)},'physical_page':page,'page_index_zero_based':page-1,'region':{'kind':'full_media_box','points':[0,0,612,792]},'render_recipe':{'tool':'pdftoppm','first_page':page,'last_page':page,'dpi':200,'format':'png','box':'media_box','rotation':'source_applied','color':'rgb','background':'white','alpha':False,'metadata':'stripped'},'output_media_type':'image/png','output_dimensions':{'width':1700,'height':2200},'quality_stage':'provisional_full_page'};aid=f'viral-provisional-{name}-page-{page}';result[aid]={'asset_id':aid,'disposition':'reader','source_page':page,'binary':None,'provenance':provenance,'migration_outcome':'new_reviewed_target'}
 if len(result)!=126 or sum(row['provenance']['kind']=='markdown_image_reference' for row in result.values())!=16 or sum(row['provenance']['kind']=='visual_region' for row in result.values())!=100:fail('E_V2_ASSET','expected-declaration')
 return result

def v2_b1c4_migration_closure(rows,targets):
 """Independent closed B1c4 replacement-graph check."""
 if not isinstance(rows,list) or len(rows)!=123 or not isinstance(targets,list) or len(targets)<8:fail('E_V2_MIGRATION','count')
 counts={key:sum(isinstance(row,dict) and row.get('outcome')==key for row in rows) for key in ('retained_unchanged','retained_rebound','reclassified','excluded_advertising')}
 if counts!={'retained_unchanged':99,'retained_rebound':2,'reclassified':16,'excluded_advertising':6} or sum(isinstance(row,dict) and not row.get('target_ids') for row in rows)!=6:fail('E_V2_MIGRATION','closure')
 frozen=parsed(Path(__file__).resolve().parents[2]/'kb_creator/working/viral/master_en/publication_config_v1.json').get('assets',[])
 pages={f"assets:{item['asset_id']}":item['source_page'] for item in frozen if isinstance(item,dict) and isinstance(item.get('asset_id'),str)}
 order=[f"assets:{item['asset_id']}" for item in frozen]
 if [row.get('source_id') for row in rows if isinstance(row,dict)]!=order:fail('E_V2_MIGRATION','source-order')
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
  if outcome!=expected_outcome or row['decision_ref']!=expected or row['target_ids']!=target:fail('E_V2_MIGRATION','decision')
 ids=[];children=[];expected_details={
  26:('viral-isola-di-malamente','page_opening:viral-isola-di-malamente',0,'page_opening_visual'),
  106:('viral-keeper-map-ground-floor-basement','physical_units:viral-map-ground-floor-basement',0,'map_key_legend_scale'),107:('viral-keeper-map-ground-floor-basement','physical_units:viral-map-ground-floor-basement',1,'map_key_legend_scale'),
  112:('viral-pregen-marco-background','physical_units:viral-pregen-marco',1,'pregen_back_semantic_payload'),114:('viral-pregen-corrina-background','physical_units:viral-pregen-corrina',1,'pregen_back_semantic_payload'),116:('viral-pregen-enoch-background','physical_units:viral-pregen-enoch',1,'pregen_back_semantic_payload'),118:('viral-pregen-peter-background','physical_units:viral-pregen-peter',1,'pregen_back_semantic_payload'),120:('viral-pregen-ku-hyeon-background','physical_units:viral-pregen-ku-hyeon',1,'pregen_back_semantic_payload'),122:('viral-pregen-blank-background','physical_units:viral-pregen-blank',1,'pregen_back_semantic_payload')}
 expected_children={106:['viral-accepted-adb4ff51bd5ebff464834e0fb324310c281eb20d2c4b0f4e82d1fbaf3ef72541','viral-accepted-f7ce778cc1eb05cb6fef0f26457d06e68019ee30c76a5723f259dc82b89b321d'],107:['viral-accepted-e1c168ca34db2f98a27391e749f08a0fcdda832034d68e5fd0fbc38b00f584dc'],112:['viral-accepted-5d2410afd9a6593cdce0d7f0d411835cf4a726551a1b1e18b6f79d04ed42230b','viral-accepted-53c2775488f57c8e41f9d42648ecb8a1d30e9a1ce0de8d4108b7926ee26a3595'],114:['viral-accepted-331f4d575265e02a4ba97b4e204dbbb20b648e9b62d44eb47ea11ab6998c00d3','viral-accepted-89e3eae7390f0ae27a8069bcf2d2aa2956a21047eeb7168a3fd49b0b7cbfc297'],116:['viral-accepted-92c65562fe49c02049e4b40e4a278b667e1361568455fdd89a724389a8d01d50','viral-accepted-66088dd8192e2a93f140eb9e11fadfed92b3869c509490199a35d272197ebfcb'],118:['viral-accepted-07982af9981b82074567f2fa5d976b00cb40a0331f01438352f9fd59fc864aa4','viral-accepted-fe4c839c1ff9b15dc4a9136f6969271a7a465fe642c77b38f456aa2af38fe0c3'],120:['viral-accepted-9d7ebb95113ecd5d9114224cff873b14f2db563d61015978164a78e4ff05953f','viral-accepted-df1e018979c88b0737200c349889745eadfa119466dc40fb024779a0f8eb4730'],122:['viral-accepted-1ae1543b9ff31ba9d7c4271ae01d86f05fb722c00e9f7851ce1dffc820aee3b8','viral-accepted-dd0c2d51431a4945f9f7d8293bc7b0b5e870f891dbe31d18c931926bffbb8d8b','viral-accepted-dcf1f2f6dd9540217155f01d5b03d965aedef98d965c2a33e987f0f5996eb166']}
 expected_children[26]=[]
 target_count=len(targets);hierarchy_targets=[target for target in targets if isinstance(target,dict) and str(target.get('target_id','')).startswith('hierarchy:')]
 if len({target['target_id'] for target in hierarchy_targets})!=len(hierarchy_targets) or any(set(target)!={'target_id','decision_ref'} or not target['target_id'][len('hierarchy:'):] or target['decision_ref']!='OUT-003' for target in hierarchy_targets):fail('E_V2_MIGRATION','hierarchy-target-schema')
 targets=[target for target in targets if isinstance(target,dict) and str(target.get('target_id','')).startswith('assets:viral-provisional-')]
 if len(targets)+len(hierarchy_targets)!=target_count:fail('E_V2_MIGRATION','replacement-target-domain')
 for target in targets:
  if not isinstance(target,dict) or set(target)!={'target_id','decision_ref','evidence_identity','physical_unit_id','page_slot','owner_anchor','accessibility_obligation','replaces'} or not isinstance(target.get('target_id'),str) or not target['target_id'].startswith('assets:viral-provisional-') or target.get('decision_ref') not in {'OUT-024','OUT-025','OUT-038'} or not isinstance(target.get('evidence_identity'),dict) or not isinstance(target.get('replaces'),list) or (not target['replaces'] and target.get('decision_ref')!='OUT-038'):fail('E_V2_MIGRATION','replacement-schema')
  ids.append(target['target_id']);children.extend(target['replaces'])
 expected_targets=['assets:viral-provisional-map-ground-floor-basement-page-106','assets:viral-provisional-map-ground-floor-basement-page-107','assets:viral-provisional-pregen-marco-back-page-112','assets:viral-provisional-pregen-corrina-back-page-114','assets:viral-provisional-pregen-enoch-back-page-116','assets:viral-provisional-pregen-peter-back-page-118','assets:viral-provisional-pregen-ku-hyeon-back-page-120','assets:viral-provisional-pregen-blank-back-page-122','assets:viral-provisional-isola-di-malamente-opening-page-26']
 if ids!=expected_targets or len(children)!=16 or len(set(children))!=16 or any(not isinstance(item,str) or not item.startswith('viral-accepted-') for item in children):fail('E_V2_MIGRATION','replacement-graph')
 for target,page in zip(targets,(106,107,112,114,116,118,120,122,26)):
  owner,unit,slot,obligation=expected_details[page]
  expected_decision='OUT-038' if page==26 else 'OUT-024' if page in {106,107} else 'OUT-025'
  if target['decision_ref']!=expected_decision or target['evidence_identity']!={'path':'kb_creator/working/viral/source/Call_of_Cthulhu_Viral.pdf','bytes':20718150,'sha256':'0A80B6F389821B87553D26746D2BE171B4482BA9BBC6E3EB3FEC26274EDBED05'} or (target['owner_anchor'],target['physical_unit_id'],target['page_slot'],target['accessibility_obligation'],target['replaces'])!=(owner,unit,slot,obligation,expected_children[page]):fail('E_V2_MIGRATION','replacement-identity')
 return counts

def v2_contract(cfg):
 """Independent v2 validation; deliberately does not call builder helpers."""
 closed(cfg,{'schema','scenario_id','document','hierarchy','events','assets','xrefs','source_recoveries','source_disposition','source_partition','migration','visual_review_units','metrics'},'v2-config')
 if cfg['schema']!=V2_SCHEMA: fail('E_V2_SCHEMA','schema')
 v2_migration_schema(cfg['migration'])
 document=cfg['document'];closed(document,{'audit_scope','reader_scope','generated_navigation','source_pdf','reconstruction_package'},'v2-document')
 if document['audit_scope']!=list(range(1,125)) or document['reader_scope']!=list(range(1,123)) or set(document['generated_navigation'])!={'operation','source_identity'} or document['generated_navigation'].get('operation')!='generated_navigation_replaces_source_toc' or not document['generated_navigation'].get('source_identity'):fail('E_V2_SCOPE','pages')
 for label in ('source_pdf',):
  identity=document[label];closed(identity,{'path','bytes','sha256'},'v2-'+label)
  if not safe(identity['path']) or not isinstance(identity['bytes'],int) or isinstance(identity['bytes'],bool) or identity['bytes']<0 or not isinstance(identity['sha256'],str) or not HEX.fullmatch(identity['sha256']):fail('E_V2_IDENTITY',label)
 package=document['reconstruction_package'];closed(package,{'root','file_count','total_bytes','inventory_algorithm','inventory_sha256'},'v2-reconstruction-package')
 if not isinstance(package['root'],str) or not package['root'] or not isinstance(package['file_count'],int) or isinstance(package['file_count'],bool) or package['file_count']<=0 or not isinstance(package['total_bytes'],int) or isinstance(package['total_bytes'],bool) or package['total_bytes']<=0:fail('E_V2_SCHEMA','reconstruction-package')
 if package['inventory_algorithm']!=PACKAGE_ALGO or not isinstance(package['inventory_sha256'],str) or not HEX.fullmatch(package['inventory_sha256']):fail('E_V2_IDENTITY','reconstruction-algorithm')
 dispositions=cfg['source_disposition']
 if not isinstance(dispositions,list) or len(dispositions)!=124:fail('E_V2_SCOPE','disposition-count')
 for page,row in enumerate(dispositions,1):
  closed(row,{'page','audit_disposition','publication_disposition','publish_reader_content','decision_date','reason','page_markdown'},'v2-source-disposition')
  identity=row['page_markdown'];closed(identity,{'path','bytes','sha256'},'v2-page-markdown')
  excluded=page in {123,124}
  if row['page']!=page or row['audit_disposition']!='reconstructed' or not safe(identity['path']) or not isinstance(identity['bytes'],int) or isinstance(identity['bytes'],bool) or identity['bytes']<0 or not isinstance(identity['sha256'],str) or not HEX.fullmatch(identity['sha256']) or (row['publication_disposition'],row['publish_reader_content']) != (('excluded_advertising',False) if excluded else ('reader',True)):fail('E_V2_SCOPE','disposition-row')
  if excluded and (row['decision_date']!='2026-09-02' or not isinstance(row['reason'],str) or not row['reason'].strip()):fail('E_V2_SCOPE','excluded-policy')
 anchors={};
 for row in cfg['hierarchy']:
  closed(row,{'anchor','parent_anchor','level','toc_entry','semantic_role','source_pages','source_title','reader_title','representation','reviewed_title_transformation','migration_row_id'},'v2-hierarchy')
  if row['anchor'] in anchors or not isinstance(row['source_pages'],list) or any(page not in document['reader_scope'] for page in row['source_pages']) or row['representation'] not in {'heading','anchor_only','inline_run_in'}:fail('E_V2_HIERARCHY','representation')
  if row['representation']=='heading' and (not isinstance(row['level'],int) or isinstance(row['level'],bool) or row['level'] not in range(1,7)):fail('E_V2_HIERARCHY','level')
  if row['representation']!='heading' and row['level'] is not None:fail('E_V2_HIERARCHY','level')
  if row['source_title']!=row['reader_title'] and not isinstance(row['reviewed_title_transformation'],dict):fail('E_V2_TITLE','drift')
  anchors[row['anchor']]=row
 for target in cfg['migration']['new_reviewed_targets']:
  if not isinstance(target,dict) or not str(target.get('target_id','')).startswith('hierarchy:'):continue
  anchor=target['target_id'][len('hierarchy:'):];row=anchors.get(anchor)
  if row is None or row.get('migration_row_id')!=target['target_id'] or not row.get('source_pages') or not isinstance(row.get('source_title'),str) or not row['source_title']:fail('E_V2_MIGRATION','hierarchy-target-source-binding')
 last=None; ids=set()
 for event in cfg['events']:
  keys={'event_id','type','page','order_key','anchor','content','fragment_id','source_span_ids','source_operation','payload_bindings'}|({'generated_placement'} if event.get('type')=='generated_navigation' else set())
  if event.get('type')=='structured_unit': keys=keys|{'contains'}
  closed(event,keys,'v2-event')
  key=tuple(event['order_key'])
  if event['event_id'] in ids or last is not None and key<=last or event['page'] not in document['reader_scope'] or event['anchor'] not in anchors or event['type'] not in {'heading','text_fragment','structured_unit','asset','anchor_only','generated_navigation'}:fail('E_V2_ORDER','event-graph')
  ids.add(event['event_id']);last=key
  if event['type']=='structured_unit':
   children=event['contains']
   if not isinstance(children,list) or not children or any(not isinstance(child,str) or not child for child in children) or len(children)!=len(set(children)) or not isinstance(event['content'],dict) or children!=event['content'].get('contains'):fail('E_V2_STRUCTURE','contains')
 for asset in cfg['assets']:
  if isinstance(asset,dict) and 'provenance' in asset:
   immutable={'asset_id','disposition','source_page','binary','provenance','migration_outcome'}; placement={'anchor','placement','source_order'}
   if set(asset)!=immutable|placement or asset['disposition'] not in {'reader','evidence_only'} or asset['source_page'] not in document['reader_scope'] or asset['migration_outcome'] not in {'retained_unchanged','retained_rebound','reclassified','new_reviewed_target'} or not isinstance(asset['provenance'],dict):fail('E_V2_ASSET','b1c4-schema')
   if asset['disposition']=='evidence_only' and any(asset[key] is not None for key in placement):fail('E_V2_ASSET','evidence-placement')
   if asset['disposition']=='reader':
    if asset['anchor'] not in anchors or not isinstance(asset['placement'],dict) or len(asset['placement'])!=1 or set(asset['placement'])-{'before_event','after_event','inside_structured_unit'} or not isinstance(asset['source_order'],dict):fail('E_V2_ASSET','reader-placement')
    order=asset['source_order'];kind=order.get('kind')
    if kind=='selected_view_raw_index' and set(order)=={'kind','view','raw_index','gap_ordinal'} and isinstance(order['view'],str) and isinstance(order['raw_index'],int) and isinstance(order['gap_ordinal'],int):pass
    elif kind=='physical_unit_page_slot' and set(order)=={'kind','unit_id','page_slot'} and isinstance(order['unit_id'],str) and isinstance(order['page_slot'],int):pass
    else:fail('E_V2_ASSET','source-order')
   kind=asset['provenance'].get('kind');binary=asset['binary']
   if kind in {'visual_region','markdown_image_reference'}:
    if not isinstance(binary,dict) or set(binary)!={'path','bytes','sha256','media_type','dimensions'} or not isinstance(binary.get('dimensions'),dict) or set(binary['dimensions'])!={'width','height'} or binary['media_type'] not in {'image/jpeg','image/png'} or not isinstance(binary['bytes'],int) or binary['bytes']<=0 or not isinstance(binary['sha256'],str) or not HEX.fullmatch(binary['sha256']):fail('E_V2_ASSET','b1c4-binary')
    source=(Path(__file__).resolve().parents[2]/binary['path']).resolve();package_root=(Path(__file__).resolve().parents[2]/'kb_creator/working/viral/source_reconstruction/20260901_step6a_reconstructed_en_package_v4').resolve()
    if package_root not in source.parents or not source.is_file() or source.is_symlink() or source.stat().st_size!=binary['bytes'] or sha(source)!=binary['sha256']:
     fail('E_V2_ASSET','binary-identity')
    try:
     with Image.open(source) as image:
      image.load();dimensions={'width':image.width,'height':image.height};actual={'JPEG':'image/jpeg','PNG':'image/png'}.get(image.format)
    except OSError:fail('E_V2_ASSET','binary-identity')
    if dimensions!=binary['dimensions'] or actual!=binary['media_type']:fail('E_V2_ASSET','binary-identity')
    keys={'kind','span_id','page_markdown_identity','start_byte','end_byte','start_char','end_char','marker_sha256'} if kind=='markdown_image_reference' else {'kind','asset_manifest_identity','asset_manifest_row_sha256','comparison_identity','selected_view','source_asset_reference','raw_index','block_type','source_page','bbox','comparison_block_sha256'}
    if set(asset['provenance'])!=keys:fail('E_V2_ASSET','provenance')
    provenance=asset['provenance'];manifest_path=package_root/'ASSET_MANIFEST.json';comparison_path=Path(__file__).resolve().parents[2]/'kb_creator/working/viral/source_reconstruction/20260901_step6a_mineru_three_view_full/comparison/comparison.json'
    if kind=='markdown_image_reference':
     page=(Path(__file__).resolve().parents[2]/provenance['page_markdown_identity'].get('path','')).resolve();identity=provenance['page_markdown_identity']
     if not isinstance(identity,dict) or set(identity)!={'path','bytes','sha256'} or not page.is_file() or page.stat().st_size!=identity['bytes'] or sha(page)!=identity['sha256'] or provenance['end_byte']<=provenance['start_byte'] or provenance['end_char']<=provenance['start_char']:fail('E_V2_ASSET','provenance-identity')
     raw=page.read_bytes()[provenance['start_byte']:provenance['end_byte']]
     try:text=raw.decode('utf8')
     except UnicodeDecodeError:fail('E_V2_ASSET','provenance-identity')
     if len(page.read_bytes()[:provenance['start_byte']].decode('utf8'))!=provenance['start_char'] or len(page.read_bytes()[:provenance['end_byte']].decode('utf8'))!=provenance['end_char'] or not text.strip().startswith('![') or binary['sha256'].lower().encode() not in raw or hashlib.sha256(raw).hexdigest().upper()!=provenance['marker_sha256']:fail('E_V2_ASSET','provenance-identity')
    else:
     manifest_rows=parsed(manifest_path).get('assets',[]);entry=next((item for item in manifest_rows if isinstance(item,dict) and item.get('sha256','').upper()==binary['sha256']),None);comparison=parsed(comparison_path)
     block=next((item for item in comparison.get('views',{}).get(provenance['selected_view'],{}).get('blocks',[]) if isinstance(item,dict) and item.get('raw_index')==provenance['raw_index']),None)
     if not isinstance(entry,dict) or not isinstance(block,dict) or provenance['asset_manifest_identity']!={'path':str(manifest_path.relative_to(Path(__file__).resolve().parents[2])).replace('\\','/'),'bytes':manifest_path.stat().st_size,'sha256':sha(manifest_path)} or provenance['comparison_identity']!={'path':str(comparison_path.relative_to(Path(__file__).resolve().parents[2])).replace('\\','/'),'bytes':comparison_path.stat().st_size,'sha256':sha(comparison_path)} or provenance['asset_manifest_row_sha256']!=v2_canonical_row(entry) or provenance['comparison_block_sha256']!=v2_canonical_row(block) or (provenance['source_asset_reference'],provenance['block_type'],provenance['source_page'],provenance['bbox'])!=(entry.get('source_path'),block.get('type'),block.get('source_page'),block.get('bbox')) or entry.get('source_path') not in block.get('assets',[]):fail('E_V2_ASSET','provenance-identity')
   elif kind=='reviewed_provisional_full_page':
    if binary is not None or asset['disposition']!='reader' or set(asset['provenance'])!={'kind','source_pdf_identity','physical_page','page_index_zero_based','region','render_recipe','output_media_type','output_dimensions','quality_stage'} or asset['provenance'].get('physical_page')!=asset['source_page'] or asset['provenance'].get('page_index_zero_based')!=asset['source_page']-1 or asset['provenance'].get('output_media_type')!='image/png' or asset['provenance'].get('output_dimensions')!={'width':1700,'height':2200} or asset['provenance'].get('quality_stage')!='provisional_full_page':fail('E_V2_ASSET','b1c4-render')
    source_pdf=Path(__file__).resolve().parents[2]/'kb_creator/working/viral/source/Call_of_Cthulhu_Viral.pdf';recipe=asset['provenance'].get('render_recipe',{});expected_recipe={'tool':'pdftoppm','first_page':asset['source_page'],'last_page':asset['source_page'],'dpi':200,'format':'png','box':'media_box','rotation':'source_applied','color':'rgb','background':'white','alpha':False,'metadata':'stripped'}
    if asset['provenance'].get('source_pdf_identity')!={'path':str(source_pdf.relative_to(Path(__file__).resolve().parents[2])).replace('\\','/'),'bytes':source_pdf.stat().st_size,'sha256':sha(source_pdf)} or asset['provenance'].get('region')!={'kind':'full_media_box','points':[0,0,612,792]} or recipe!=expected_recipe:fail('E_V2_ASSET','provisional-identity')
   else:fail('E_V2_ASSET','provenance')
   continue
  if isinstance(asset,dict) and 'migration_outcome' in asset:fail('E_V2_ASSET','provenance')
  base={'asset_id','reader_value','placement','anchor','page','source_span_ids'};reader=base|{'duplication_resolution','quality_stage','source_path','bytes','sha256','semantic_role'}
  closed(asset,reader if asset.get('reader_value') is True else base,'v2-asset')
  if asset['anchor'] not in anchors or asset['page'] not in document['reader_scope'] or not isinstance(asset['reader_value'],bool) or set(asset['placement']) not in ({'before_event'},{'after_event'},{'inside_structured_unit'}):fail('E_V2_ASSET','asset')
  if asset['reader_value'] and (asset['duplication_resolution'] not in {'unique_reader','text_wins_crop_evidence_only','reviewed_exception'} or asset['quality_stage'] not in {'provisional_full_page','accepted_reconstruction'} or asset['semantic_role'] not in {'full_page','illustration','map','pregen'} or not isinstance(asset['source_path'],str) or not isinstance(asset['bytes'],int) or asset['bytes']<=0 or not HEX.fullmatch(asset['sha256'])):fail('E_V2_ASSET','policy')
 if cfg['scenario_id']=='viral' and cfg['assets'] and all(isinstance(item,dict) and 'provenance' in item for item in cfg['assets']):
  declared={item['asset_id']:item for item in cfg['assets']};expected=v2_b1c4_expected_assets(Path(__file__).resolve().parents[2]);frozen=parsed(Path(__file__).resolve().parents[2]/'kb_creator/working/viral/master_en/publication_config_v1.json')['assets'];migration={item['source_id']:item for item in cfg['migration']['asset_rows']};children={child for target in cfg['migration']['new_reviewed_targets'] if target.get('target_id','').startswith('assets:viral-provisional-') for child in target['replaces']}
  if set(declared)!=set(expected) or any({key:declared[asset_id][key] for key in ('asset_id','disposition','source_page','binary','provenance','migration_outcome')}!=expected[asset_id] for asset_id in expected):fail('E_V2_ASSET','declaration-identity')
  for source in frozen:
   source_id='assets:'+source['asset_id'];row=migration[source_id];asset=declared.get(source['asset_id'])
   if row['outcome']=='excluded_advertising' and asset is not None:fail('E_V2_ASSET','excluded-leakage')
   if row['outcome']!='excluded_advertising' and (asset is None or asset['source_page']!=source['source_page'] or asset['migration_outcome']!=row['outcome'] or (source['asset_id'] in children and asset['disposition']!='evidence_only')):fail('E_V2_ASSET','migration-identity')
  if any(event.get('type')=='asset' and event.get('content') in children for event in cfg['events']):fail('E_V2_ASSET','replaced-child-event')
 events={row['event_id']:row for row in cfg['events']};xref_ids=set()
 for row in cfg['xrefs']:
  closed(row,{'xref_id','source_event_id','source_page','target_anchor','reader_text','source_slices','emit_link','migration_row_id'},'v2-xref')
  owner=events.get(row['source_event_id']);owned_pages={span['page'] for span in cfg['source_partition']['spans'] if owner is not None and span['span_id'] in owner.get('source_span_ids',[])}
  if row['xref_id'] in xref_ids or owner is None or row['source_page'] not in document['reader_scope'] or row['source_page'] not in owned_pages or not isinstance(row['emit_link'],bool) or (row['emit_link'] and row['target_anchor'] not in anchors) or (not row['emit_link'] and row['target_anchor'] is not None) or not isinstance(row['reader_text'],str) or not row['reader_text'] or not isinstance(row['source_slices'],list) or not row['source_slices'] or not isinstance(row['migration_row_id'],str) or not row['migration_row_id']:fail('E_V2_XREF','declaration')
  xref_ids.add(row['xref_id'])
 recovery_ids=set()
 for row in cfg['source_recoveries']:
  closed(row,{'recovery_id','source_pdf_identity','physical_page','extraction_method','source_text','source_text_sha256','evidence_identity','target_event_id','placement','decision_ref'},'v2-recovery')
  if row['recovery_id'] in recovery_ids or row['target_event_id'] not in events:fail('E_V2_RECOVERY','declaration')
  recovery_ids.add(row['recovery_id'])
 v2_visual_review_units(cfg,anchors,events)
 if cfg['metrics']!={'source_pages_audited':124,'reader_pages':122,'excluded_advertising_pages':2}:fail('E_V2_SCOPE','metrics')

V2_REVIEW_KINDS={'heading_outline','callout','ordered_list_callout','table','equipment_card','creature_statblock','inline_run_in','full_page_map','physical_page_pair','xref_recovery','asset_placement'}
def v2_visual_review_units(cfg,anchors=None,event_by_id=None):
 """Independently validate all dynamic visual-review coverage declarations."""
 events=event_by_id or {row['event_id']:row for row in cfg['events']};assets={row['asset_id']:row for row in cfg['assets']};reader=set(cfg['document']['reader_scope']);units=cfg['visual_review_units']
 if not isinstance(units,list):fail('E_V2_REVIEW','units')
 ids=set();headings=set();structured=set();xref_recovery=set();asset_coverage=set()
 for row in units:
  closed(row,{'review_id','kind','source_pages','event_ids','asset_ids','priority','contact_sheet_group'},'v2-visual-review-unit')
  review_id=row['review_id']
  if not isinstance(review_id,str) or not review_id or review_id in ids or row['kind'] not in V2_REVIEW_KINDS or not isinstance(row['source_pages'],list) or not row['source_pages'] or len(row['source_pages'])!=len(set(row['source_pages'])) or any(page not in reader for page in row['source_pages']) or not isinstance(row['event_ids'],list) or len(row['event_ids'])!=len(set(row['event_ids'])) or not isinstance(row['asset_ids'],list) or len(row['asset_ids'])!=len(set(row['asset_ids'])) or not row['event_ids'] and not row['asset_ids'] or not isinstance(row['priority'],bool) or not isinstance(row['contact_sheet_group'],str) or not row['contact_sheet_group']:fail('E_V2_REVIEW','row')
  ids.add(review_id)
  if any(event_id not in events for event_id in row['event_ids']) or any(asset_id not in assets for asset_id in row['asset_ids']):fail('E_V2_REVIEW','reference')
  if any(events[event_id]['page'] not in row['source_pages'] for event_id in row['event_ids']) or any(assets[asset_id].get('source_page',assets[asset_id].get('page')) not in row['source_pages'] for asset_id in row['asset_ids']):fail('E_V2_REVIEW','page')
  if row['kind']=='heading_outline':
   if not row['event_ids'] or row['asset_ids'] or any(events[event_id]['type']!='heading' for event_id in row['event_ids']):fail('E_V2_REVIEW','kind')
   headings.update(row['event_ids'])
  elif row['kind'] in {'callout','ordered_list_callout','table','equipment_card','creature_statblock','inline_run_in','full_page_map','physical_page_pair'}:
   if not row['event_ids'] or row['asset_ids'] or any(events[event_id]['type']!='structured_unit' or events[event_id]['content'].get('kind')!=row['kind'] for event_id in row['event_ids']):fail('E_V2_REVIEW','kind')
   structured.update(row['event_ids'])
  elif row['kind']=='xref_recovery':
   expected={item['source_event_id'] for item in cfg['xrefs']}|{item['target_event_id'] for item in cfg['source_recoveries']}
   if not row['event_ids'] or row['asset_ids'] or any(event_id not in expected for event_id in row['event_ids']):fail('E_V2_REVIEW','kind')
   xref_recovery.update(row['event_ids'])
  else:
   if row['event_ids'] or not row['asset_ids'] or any(not assets[asset_id].get('reader_value',assets[asset_id].get('disposition')=='reader') for asset_id in row['asset_ids']):fail('E_V2_REVIEW','kind')
   asset_coverage.update(row['asset_ids'])
 expected_headings={event['event_id'] for event in cfg['events'] if event['type']=='heading' and next(row for row in cfg['hierarchy'] if row['anchor']==event['anchor'])['representation']=='heading'}
 expected_structured={event['event_id'] for event in cfg['events'] if event['type']=='structured_unit'}
 expected_xref_recovery={item['source_event_id'] for item in cfg['xrefs']}|{item['target_event_id'] for item in cfg['source_recoveries']};expected_assets={asset_id for asset_id,asset in assets.items() if asset.get('reader_value',asset.get('disposition')=='reader')}
 if not expected_headings<=headings or not expected_structured<=structured or not expected_xref_recovery<=xref_recovery or not expected_assets<=asset_coverage:fail('E_V2_REVIEW','coverage')
 hierarchy={row['anchor']:row for row in cfg['hierarchy']};spans={row['span_id']:row for row in cfg['source_partition']['spans']};expected=[]
 def add(event,kind,priority,group):expected.append({'review_id':f"review:{kind}:{event['event_id']}",'kind':kind,'source_pages':sorted({spans[item]['page'] for item in event.get('source_span_ids',[]) if item in spans}) or [event['page']],'event_ids':[event['event_id']],'asset_ids':[],'priority':priority,'contact_sheet_group':group})
 for event in cfg['events']:
  if event['type']=='heading' and hierarchy[event['anchor']]['representation']=='heading':add(event,'heading_outline',True,'outline')
  elif event['type']=='structured_unit':add(event,event['content']['kind'],False,'structured')
 for event in cfg['events']:
  if event['event_id'] in expected_xref_recovery:add(event,'xref_recovery',True,'xref_recovery')
 for asset in cfg['assets']:
  if asset.get('reader_value',asset.get('disposition')=='reader'):
   page=asset.get('source_page',asset.get('page'))
   if not isinstance(page,int):fail('E_V2_REVIEW','asset-page')
   expected.append({'review_id':f"review:asset_placement:{asset['asset_id']}",'kind':'asset_placement','source_pages':[page],'event_ids':[],'asset_ids':[asset['asset_id']],'priority':False,'contact_sheet_group':'reader_assets'})
 if units!=expected:fail('E_V2_REVIEW','declaration')
 declaration=json.dumps(units,ensure_ascii=False,sort_keys=True,indent=2)+'\n'
 return {'count':len(units),'groups':sorted({row['contact_sheet_group'] for row in units}),'priority_total':sum(row['priority'] for row in units),'declaration_sha256':hashlib.sha256(declaration.encode('utf8')).hexdigest().upper()}

def v2_identity(root,identity,label,want=None):
 """Resolve a closed v2 identity without importing any builder code."""
 closed(identity,{'path','bytes','sha256'},label)
 if not safe(identity['path']):fail('E_V2_IDENTITY',label)
 path=root/Path(identity['path'])
 if not path.is_file() or rp(path) or path.stat().st_size!=identity['bytes'] or sha(path)!=identity['sha256'] or want is not None and path.resolve()!=Path(want).resolve():fail('E_V2_IDENTITY',label)
 return path.resolve()

def v2_b1c3_xref_closure(cfg,root):
 """Independently rederive Viral's frozen xref/navigation closure."""
 if cfg.get('scenario_id')!='viral': return
 migration=cfg['migration'];v1=parsed(v2_identity(root,migration['inputs']['frozen_v1_config'],'B1c3-frozen-v1'))
 hierarchy={row['anchor'] for row in cfg['hierarchy']};events={row['event_id']:row for row in cfg['events']}
 families=(('generated_toc','toc','viral-contents'),('generated_handout_index','handout_index','viral-player-handouts'),('generated_map_index','map_index','viral-keeper-maps'),('generated_pregen_index','pregen_index','viral-pregenerated-investigators'))
 definitions={};nav=set()
 for index,(selector,family,owner) in enumerate(families):
  frozen=[row for row in v1['xrefs'] if row['source_selector']==selector and row['xref_id'] not in {'toc-viral-merchandise','toc-viral-back-cover'}]
  definitions[f'generated-navigation-{family.replace("_", "-")}']=(index,family,owner,frozen);nav.update(f'generated_navigation_items:{row["xref_id"]}' for row in frozen)
 generated=[row for row in cfg['events'] if row['type']=='generated_navigation']
 if len(generated)!=4 or {row['event_id'] for row in generated}!=set(definitions):fail('E_V2_NAVIGATION','closure')
 for event in generated:
  index,family,owner,frozen=definitions[event['event_id']];headings=[row for row in cfg['events'] if row['type']=='heading' and row['anchor']==owner];data=event['content']
  if len(headings)!=1 or event['anchor']!=owner or event['page']!=headings[0]['page'] or event['order_key']!=[headings[0]['page'],headings[0]['order_key'][1],5,cfg['events'].index(event)] or event['generated_placement']!={'after_event':headings[0]['event_id']} or not isinstance(data,dict) or set(data)!={'kind','family','owner_anchor','decision_ref','entry_count','entries'} or data['kind']!='generated_navigation' or data['family']!=family or data['owner_anchor']!=owner or data['decision_ref']!='OUT-002' or data['entry_count']!=len(frozen) or not isinstance(data['entries'],list) or len(data['entries'])!=len(frozen):fail('E_V2_NAVIGATION','semantics')
  for entry,row in zip(data['entries'],frozen):
   if entry!={'navigation_id':f'navigation:{row["xref_id"]}','source_xref_id':row['xref_id'],'reader_text':row['visible_text'],'target_anchor':row['target_anchors'][0],'migration_row_id':f'generated_navigation_items:{row["xref_id"]}'} or entry['target_anchor'] not in hierarchy:fail('E_V2_NAVIGATION','entry')
 expected=[]
 for frozen in (row for row in v1['xrefs'] if row['source_selector']=='line_exact'):
  for index,segment in enumerate(frozen['segments'],1):expected.append((frozen['xref_id'] if len(frozen['segments'])==1 else f'{frozen["xref_id"]}-segment-{index:02d}',frozen,segment))
 actual={row['xref_id']:row for row in cfg['xrefs']}
 if len(actual)!=42 or set(actual)!={row[0] for row in expected}:fail('E_V2_XREF','closure')
 for xid,frozen,segment in expected:
  row=actual[xid];event=events.get(row['source_event_id'])
  if row['source_page']!=frozen['source_page'] or row['reader_text']!=segment['reader_text'] or row['target_anchor']!=segment['target_anchor'] or row['emit_link']!=segment['emit_link'] or row['migration_row_id']!=f'xrefs:{xid}' or event is None or event['anchor']!=frozen['owner_anchor']:fail('E_V2_XREF','owner')
 rows={row['source_id']:row for row in migration['xref_rows']}
 if len(rows)!=237 or set(rows)!={f'xrefs:{row["xref_id"]}' for row in v1['xrefs']}:fail('E_V2_MIGRATION','xref-closure')
 targets=[]
 for frozen in v1['xrefs']:
  row=rows[f'xrefs:{frozen["xref_id"]}'];xid=frozen['xref_id']
  if xid in {'toc-viral-merchandise','toc-viral-back-cover'}:wanted=('excluded_advertising',[],'OUT-026')
  elif frozen['source_selector']=='line_exact' and xid=='p037-handout-21':wanted=('split',['xrefs:p037-handout-21-segment-01','xrefs:p037-handout-21-segment-02'],None)
  elif frozen['source_selector']=='line_exact':wanted=('retained_unchanged',[f'xrefs:{xid}'],None)
  else:wanted=('replaced',[f'generated_navigation_items:{xid}'],'OUT-002')
  if (row['outcome'],row['final_target_ids'],row['decision_ref'])!=wanted:fail('E_V2_MIGRATION','xref-target')
  targets.extend(row['final_target_ids'])
 if set(targets)!={*(f'xrefs:{row[0]}' for row in expected),*nav} or len(targets)!=236:fail('E_V2_MIGRATION','materialized')

def v2_input_binding(cfg,root,source_pdf=None,reconstruction_package=None):
 """Independently bind all v2 source identities and page rows to their files."""
 document=cfg['document'];source=v2_identity(root,document['source_pdf'],'source-pdf',source_pdf)
 declared_lexical=v2_package_path(root,document['reconstruction_package']['root'])
 try:
  declared=declared_lexical.resolve(strict=True)
  package=declared if reconstruction_package is None else Path(reconstruction_package).resolve(strict=True)
 except (OSError,RuntimeError,ValueError):fail('E_V2_IDENTITY','reconstruction-package-cli')
 if not package.is_dir() or declared!=package:fail('E_V2_IDENTITY','reconstruction-package-cli')
 count,total,digest=v2_package_inventory(package);expected=document['reconstruction_package']
 if count!=expected['file_count']:fail('E_V2_IDENTITY','reconstruction-file-count')
 if total!=expected['total_bytes']:fail('E_V2_IDENTITY','reconstruction-total-bytes')
 if digest!=expected['inventory_sha256']:fail('E_V2_IDENTITY','reconstruction-inventory-sha256')
 for row in cfg['source_disposition']:
  page=v2_identity(root,row['page_markdown'],f"page-{row['page']:03d}")
  if page.parent!=package/'pages' or page.name!=f"page-{row['page']:03d}.md":fail('E_V2_IDENTITY','page-reconstruction-binding')
 excluded={123,124}
 for collection,label in ((cfg['hierarchy'],'hierarchy'),(cfg['events'],'event'),(cfg['assets'],'asset')):
  if any((set(item['source_pages']) if label=='hierarchy' else {item.get('source_page',item.get('page'))} if label=='asset' else {item['page']}) & excluded for item in collection):fail('E_V2_SCOPE','excluded-'+label)
 if any(item['source_page'] in excluded for item in cfg['xrefs']):fail('E_V2_SCOPE','excluded-xref')
 if any(item['physical_page'] in excluded for item in cfg['source_recoveries']):fail('E_V2_SCOPE','excluded-recovery')
 v2_source_partition(cfg['source_partition'],package)
 v2_b1c3_xref_closure(cfg,root)
 v2_a3_validate(cfg,package,root)
 v2_migration(cfg,root)
 return source,package,digest

def verify_v2_document(cfg, text):
 """Independently inspect canonical v2 reader text and declared events."""
 v2_contract(cfg)
 if '\r' in text or not text.endswith('\n') or '\n\n\n' in text:fail('E_V2_EOL','master')
 outline=[(len(match.group(1)),match.group(2)) for line in text.splitlines() if (match:=re.match(r'^(#{1,6}) (.*)$',line))]
 hierarchy={row['anchor']:row for row in cfg['hierarchy']}
 heading_rows=[row for row in cfg['hierarchy'] if row['representation']=='heading']
 # OUT-040 is a reviewed reader-order override: the generated Player Handouts
 # index is the parent of Handout #1 and must precede that first handout.
 if cfg.get('scenario_id')=='viral':
  first=next((row for row in heading_rows if row['anchor']=='viral-handout-01'),None)
  parent=next((row for row in heading_rows if row['anchor']=='viral-player-handouts'),None)
  if first is None or parent is None or first['parent_anchor']!=parent['anchor']:fail('E_V2_HIERARCHY','reviewed-handout-one-placement')
  heading_rows.remove(first);heading_rows.insert(heading_rows.index(parent)+1,first)
 wanted=[(row['level'],row['reader_title']) for row in heading_rows]
 if outline!=wanted:fail('E_V2_HIERARCHY','outline')
 for row in cfg['hierarchy']:
  if row['representation']=='heading' and f'<a id="{row["anchor"]}"></a>\n'+('#'*row['level'])+f' {row["reader_title"]}' not in text:fail('E_V2_HIERARCHY','heading-anchor')
  if row['representation']=='anchor_only' and any(title==row['reader_title'] for _,title in outline):fail('E_V2_HIERARCHY','anchor-only-outline')
 for event in cfg['events']:
  if event['type']=='structured_unit':
   kind=event['content'].get('kind') if isinstance(event['content'],dict) else event['content'].split(':',1)[0]
   if kind not in {'callout','ordered_list_callout','table','equipment_card','creature_statblock','inline_run_in','physical_page_pair','full_page_map'}:fail('E_V2_STRUCTURE','container')
  if event['type']=='asset':
   asset=next((x for x in cfg['assets'] if x['asset_id']==event['content']),None)
   if asset is None:fail('E_V2_ASSET','missing')
   reader=asset.get('reader_value',asset.get('disposition')=='reader')
   if 'source_path' in asset:name=asset['asset_id']
   else:
    binary=asset.get('binary');name=Path(binary['path']).name if isinstance(binary,dict) and isinstance(binary.get('path'),str) else asset['asset_id']+'.png' if asset.get('provenance',{}).get('kind')=='reviewed_provisional_full_page' else None
   present=bool(name) and f'](assets/{name})' in text
   if present != reader:fail('E_V2_ASSET','reader-value')
 return {'status':'verified_v2_document','metrics':cfg['metrics'],'event_count':len(cfg['events'])}

def v2_raw_reader(path):
 data=Path(path).read_bytes()
 if data.startswith(b'\xef\xbb\xbf') or b'\r' in data or not data.endswith(b'\n'):fail('E_V2_EOL','raw')
 try:text=data.decode('utf8')
 except UnicodeDecodeError:fail('E_V2_EOL','utf8')
 fence=None;blanks=0
 for line in text.splitlines():
  marker=re.match(r'^(?:`{3,}|~{3,})',line)
  if marker:fence=None if fence else marker.group(0)[0]
  if not fence and line=='':
   blanks+=1
   if blanks>=3:fail('E_V2_EOL','blank-run')
  else:blanks=0
 if fence:fail('E_V2_EOL','unclosed-fence')
 return text

def v2_declared_hash(event):
 """Independent canonical declared-content identity; this does not import builder code."""
 value=event['content'] if isinstance(event['content'],str) else json.dumps(event['content'],ensure_ascii=False,sort_keys=True,indent=2)+'\n'
 return hashlib.sha256(value.encode('utf8')).hexdigest().upper()

def v2_ledger_rows(cfg,text,events):
 """Validate final emitted slices, relocation, and containment from candidate bytes."""
 if not isinstance(events,list) or len(events)!=len(cfg['events']):fail('E_V2_PROVENANCE','ledger-count')
 declared={row['event_id']:row for row in cfg['events']}
 if len(declared)!=len(cfg['events']) or [row.get('event_id') for row in events]!=[row['event_id'] for row in cfg['events']]:fail('E_V2_PROVENANCE','ledger-event-order')
 assets={row['asset_id']:row for row in cfg['assets']}; result={}; ranges=[]
 for row in events:
  event=declared.get(row['event_id']);base={'event_id','type','page','order_key','anchor','fragment_id','declared_content_sha256','emission'}
  if event is None or any(row.get(key)!=event[key] for key in ('event_id','type','page','order_key','anchor','fragment_id')) or row.get('declared_content_sha256')!=v2_declared_hash(event) or row.get('emission') not in {'emitted','suppressed'}:fail('E_V2_PROVENANCE','ledger-identity')
  keys=set(base)
  if event['type']=='structured_unit':
   keys.add('contains')
   if row.get('contains')!=event['contains']:fail('E_V2_STRUCTURE','ledger-contains')
  if row['emission']=='suppressed':
   if set(row)!=keys:fail('E_V2_PROVENANCE','suppressed-range')
   if event['type']=='asset' and assets.get(event['content'],{}).get('reader_value',assets.get(event['content'],{}).get('disposition')=='reader') is True:fail('E_V2_ASSET','suppressed-reader-asset')
  else:
   keys|={'start_char','end_char','start_byte','end_byte','slice_sha256'}
   if set(row)!=keys:fail('E_V2_PROVENANCE','emitted-schema')
   start,end=row['start_char'],row['end_char'];start_byte,end_byte=row['start_byte'],row['end_byte']
   if not all(isinstance(value,int) and not isinstance(value,bool) for value in (start,end,start_byte,end_byte)) or not (0<=start<end<=len(text)) or start_byte!=len(text[:start].encode('utf8')) or end_byte!=len(text[:end].encode('utf8')):fail('E_V2_PROVENANCE','ledger-range')
   value=text[start:end]
   if hashlib.sha256(value.encode('utf8')).hexdigest().upper()!=row['slice_sha256'] or text.encode('utf8')[start_byte:end_byte]!=value.encode('utf8'):fail('E_V2_PROVENANCE','ledger-slice')
   ranges.append((start,end,row['event_id']));
  result[row['event_id']]=row
 if len(result)!=len(declared):fail('E_V2_PROVENANCE','ledger-duplicates')
 ordered=sorted(ranges)
 if any(left[1]>right[0] for left,right in zip(ordered,ordered[1:])):fail('E_V2_PROVENANCE','ledger-overlap')
 for asset_id,asset in assets.items():
  owners=[event for event in cfg['events'] if event['type']=='asset' and event['content']==asset_id]
  if len(owners)!=1:
   if not asset.get('reader_value',asset.get('disposition')=='reader') and not owners:continue
   fail('E_V2_ASSET','asset-event')
  row=result[owners[0]['event_id']]
  reader=asset.get('reader_value',asset.get('disposition')=='reader')
  if bool(reader) != (row['emission']=='emitted'):fail('E_V2_ASSET','asset-emission')
  if not reader:continue
  placement=asset.get('placement')
  if placement is None:fail('E_V2_ASSET','placement-missing')
  relation,target_id=next(iter(placement.items()));target=result.get(target_id)
  if target is None or target['emission']!='emitted':fail('E_V2_ASSET','placement-target')
  if relation=='before_event' and row['end_char']>target['start_char']:fail('E_V2_ASSET','before-placement')
  elif relation=='after_event' and row['start_char']<target['end_char']:fail('E_V2_ASSET','after-placement')
  elif relation=='inside_structured_unit':
   if declared[target_id]['type']!='structured_unit' or row['start_char']!=target['end_char']+1:fail('E_V2_ASSET','inside-placement')
  elif relation not in {'before_event','after_event','inside_structured_unit'}:fail('E_V2_ASSET','placement')
 for relation in ('before_event','after_event','inside_structured_unit'):
  grouped={}
  for asset_id,asset in assets.items():
   if not asset.get('reader_value',asset.get('disposition')=='reader') or asset.get('placement') is None:continue
   current,target_id=next(iter(asset['placement'].items()))
   if current==relation:
    owner=next(event for event in cfg['events'] if event['type']=='asset' and event['content']==asset_id)
    grouped.setdefault(target_id,[]).append(owner)
  for target_id,owners in grouped.items():
   declared_order=[event['event_id'] for event in sorted(owners,key=lambda event:tuple(event['order_key']))]
   emitted_order=[event['event_id'] for event in sorted(owners,key=lambda event:result[event['event_id']]['start_char'])]
   if declared_order!=emitted_order:fail('E_V2_ASSET','placement-source-order')
 return result

def v2_structured_slices(cfg,text,ledger):
 """Parse the declared bounded structures from their ledger slices only."""
 for event in cfg['events']:
  if event['type']!='structured_unit':continue
  row=ledger[event['event_id']]
  if row['emission']!='emitted':fail('E_V2_STRUCTURE','suppressed-container')
  value=text[row['start_char']:row['end_char']];data=event['content'];kind=data['kind'];contains=event['contains']
  if kind=='table':
   lines=value.splitlines()
   if len(lines)<2 or not all(line.startswith('| ') and line.endswith(' |') for line in lines):fail('E_V2_STRUCTURE','table-syntax')
   cells=[line[2:-2].split(' | ') for line in lines]
   if len(cells[0])!=len(data['header']) or cells[1]!=['---']*len(cells[0]) or len(cells[2:])!=data['row_count'] or sum(len(line) for line in cells[2:])!=data['cell_count']:fail('E_V2_STRUCTURE','table-shape')
  elif kind in {'callout','ordered_list_callout','equipment_card','creature_statblock','full_page_map'}:
   if not value or any(not line.startswith('> ') for line in value.splitlines()):fail('E_V2_STRUCTURE','container-boundary')
  elif kind=='physical_page_pair':
   # Reconstruct just the permitted presentation changes independently: field
   # labels remain visible, but do not become document-outline headings.
   lines=[]
   for line in data['back_semantics'].splitlines():
    match=re.fullmatch(r'#{1,6}\s+(.+)',line)
    lines.append('**'+match.group(1)+'**' if match else line)
   expected=re.sub(r'\n{3,}','\n\n','\n'.join(lines)).strip()
   if value!=expected:fail('E_V2_STRUCTURE','pair-boundary')
  elif kind=='inline_run_in':
   if not value.startswith(f'<a id="{data["anchor"]}"></a>**{data["label"]}** '):fail('E_V2_STRUCTURE','run-in-boundary')
  else:fail('E_V2_STRUCTURE','container-kind')
  if kind in {'callout','ordered_list_callout','equipment_card','creature_statblock'} and data.get('end_after')!=contains[-1]:fail('E_V2_STRUCTURE','declared-boundary')

def v2_hierarchy_slices(cfg,text,ledger):
 """Cross-bind title/representation without relying on any builder serializer."""
 outline=[(len(match.group(1)),match.group(2)) for line in text.splitlines() if (match:=re.match(r'^(#{1,6}) (.*)$',line))]
 heading_rows=[row for row in cfg['hierarchy'] if row['representation']=='heading']
 if cfg.get('scenario_id')=='viral':
  first=next((row for row in heading_rows if row['anchor']=='viral-handout-01'),None)
  parent=next((row for row in heading_rows if row['anchor']=='viral-player-handouts'),None)
  if first is None or parent is None or first['parent_anchor']!=parent['anchor']:fail('E_V2_HIERARCHY','reviewed-handout-one-placement')
  heading_rows.remove(first);heading_rows.insert(heading_rows.index(parent)+1,first)
 wanted=[(row['level'],row['reader_title']) for row in heading_rows]
 if outline!=wanted:fail('E_V2_HIERARCHY','outline')
 for hierarchy in cfg['hierarchy']:
  owned=[event for event in cfg['events'] if event['anchor']==hierarchy['anchor']]
  if hierarchy['representation']=='heading':
   headings=[ledger[event['event_id']] for event in owned if event['type']=='heading']
   expected=f'<a id="{hierarchy["anchor"]}"></a>\n'+('#'*hierarchy['level'])+f" {hierarchy['reader_title']}"
   if len(headings)!=1 or headings[0]['emission']!='emitted' or text[headings[0]['start_char']:headings[0]['end_char']]!=expected:fail('E_V2_TITLE','heading')
  elif hierarchy['representation']=='anchor_only':
   anchors=[ledger[event['event_id']] for event in owned if event['type']=='anchor_only']
   if len(anchors)!=1 or anchors[0]['emission']!='emitted' or text[anchors[0]['start_char']:anchors[0]['end_char']]!=f'<a id="{hierarchy["anchor"]}"></a>':fail('E_V2_HIERARCHY','anchor-only')
  else:
   runs=[event for event in cfg['events'] if event['type']=='structured_unit' and event['content'].get('kind')=='inline_run_in' and event['content'].get('anchor')==hierarchy['anchor']]
   if len(runs)!=1 or ledger[runs[0]['event_id']]['emission']!='emitted':fail('E_V2_HIERARCHY','inline-run-in')
   value=text[ledger[runs[0]['event_id']]['start_char']:ledger[runs[0]['event_id']]['end_char']]
   if f'**{hierarchy["reader_title"]}**' not in value or any(title==hierarchy['reader_title'] for _,title in outline):fail('E_V2_TITLE','inline-run-in')

def v2_report_payload(publication_config,target_value):
 result=verify_v2_candidate(publication_config,target_value);cfg=parsed(publication_config);root=root_for(publication_config);source,package,digest=v2_input_binding(cfg,root);out=target(root,cfg['scenario_id'],target_value);review=v2_visual_review_units(cfg)
 return {'schema':'kb_creator.master_en_verification.v2','status':result['status'],'scenario_id':cfg['scenario_id'],'candidate_root_name':out.name,'candidate_inventory_sha256':result['candidate_inventory_sha256'],'inventory_file_sha256':sha(out/'INVENTORY.json'),'publication_config_sha256':sha(publication_config),'source_pdf_sha256':sha(source),'reconstruction_inventory_sha256':digest,'verifier_script_sha256':sha(Path(__file__)),'candidate_metrics':canonical(out/'MASTER_EN.qa.json')['metrics'],'review_units':review}
def write_v2_verification_report(publication_config,target_value,report_path):
 root=root_for(publication_config);out=target(root,parsed(publication_config)['scenario_id'],target_value);report=Path(report_path)
 if report.is_absolute() or not safe(str(report).replace('\\','/')) or report.exists() or report.is_symlink() or report.parent!=report.parent or not report.parent.is_dir() or (root/report).resolve().is_relative_to(out):fail('E_V2_REPORT','path')
 destination=(root/report).resolve();
 if destination.exists() or destination.is_symlink() or out in destination.parents:fail('E_V2_REPORT','path')
 data=json.dumps(v2_report_payload(publication_config,target_value),ensure_ascii=False,sort_keys=True,indent=2)+'\n';fd,tmp=tempfile.mkstemp(prefix='.'+destination.name+'.',dir=destination.parent);os.close(fd)
 try:Path(tmp).write_text(data,encoding='utf8',newline='\n');Path(tmp).replace(destination)
 except Exception:
  Path(tmp).unlink(missing_ok=True);raise
 return canonical(destination)
def validate_v2_verification_report(publication_config,target_value,report_path):
 try:value=canonical(report_path)
 except ValueError:fail('E_V2_REPORT','canonical')
 if value!=v2_report_payload(publication_config,target_value):fail('E_V2_REPORT','binding')
 return {'status':'validated_v2_verification_report'}
def verify_v2_candidate(publication_config, target_value):
 """Read v2 candidate bytes as an external artifact; no builder dependency."""
 cfg=parsed(publication_config);v2_contract(cfg);root=root_for(publication_config);v2_input_binding(cfg,root);out=target(root,cfg['scenario_id'],target_value)
 if not out.is_dir() or (out/'MASTER_EN.acceptance.json').exists() or (out/'MASTER_EN_REVIEW.md').exists():fail('E_V2_TOPOLOGY','candidate')
 required={'MASTER_EN.md','MASTER_EN.provenance.json','SOURCE_DISPOSITION.json','ASSET_MANIFEST.json','MASTER_EN.qa.json','INVENTORY.json'}
 if not required.issubset({p.name for p in out.iterdir()}):fail('E_V2_TOPOLOGY','files')
 inv=canonical(out/'INVENTORY.json');rows,total,digest=inventory(out)
 if inv.get('rows')!=rows or inv.get('total_bytes')!=total or inv.get('inventory_sha256')!=digest:fail('E_V2_INVENTORY','inventory')
 text=v2_raw_reader(out/'MASTER_EN.md');verify_v2_document(cfg,text)
 disp=canonical(out/'SOURCE_DISPOSITION.json')
 expected_disposition={'schema':'kb_creator.source_disposition.v2','scenario_id':cfg['scenario_id'],'pages':cfg['source_disposition'],'summary':{'page_count':124,'reader_pages':122,'excluded_advertising_pages':2,'audit_disposition':'reconstructed'}}
 # Numeric substrings in SHA-named assets or narrative are not page provenance.
 # Exclusion is proved by source disposition and the closed event/page ledger.
 if disp!=expected_disposition or any(e['page'] in {123,124} for e in cfg['events']):fail('E_V2_SCOPE','disposition')
 qa=canonical(out/'MASTER_EN.qa.json');expected_review=v2_visual_review_units(cfg)
 if qa.get('schema')!='kb_creator.master_en_qa.v2' or qa.get('errors')!=[] or qa.get('metrics',{}).get('visual_review_units')!=expected_review:fail('E_V2_REVIEW','qa')
 prov=canonical(out/'MASTER_EN.provenance.json');events=prov.get('events')
 if prov.get('schema')!='kb_creator.master_en_provenance.v2' or prov.get('offset_contract')!={'char':'python_unicode_code_points','byte':'utf8_bytes','range':'zero_based_half_open'}:fail('E_V2_PROVENANCE','header')
 ledger=v2_ledger_rows(cfg,text,events);v2_structured_slices(cfg,text,ledger);v2_hierarchy_slices(cfg,text,ledger)
 for row in cfg['xrefs']:
  event=ledger[row['source_event_id']]
  expected=f"[{row['reader_text']}](#{row['target_anchor']})" if row['emit_link'] else row['reader_text']
  if event['emission']!='emitted' or expected not in text[event['start_char']:event['end_char']]:fail('E_V2_XREF','emission')
 expected_operations=[{'operation':'generated_navigation_replaces_source_toc','source_identity':cfg['document']['generated_navigation']['source_identity']}]+[{'operation':'source_backed_recovery','recovery_id':row['recovery_id'],'event_id':row['target_event_id'],'source_page':row['physical_page'],'source_text':row['source_text']} for row in cfg['source_recoveries']]
 if prov.get('operations')!=expected_operations:fail('E_V2_OPERATION','provenance')
 for row in cfg['source_recoveries']:
  event=ledger[row['target_event_id']]
  if event['emission']!='emitted' or row['source_text'] not in text[event['start_char']:event['end_char']]:fail('E_V2_RECOVERY','emission')
 manifest=canonical(out/'ASSET_MANIFEST.json');assets=manifest.get('assets',[])
 manifest_by_id={asset.get('asset_id'):asset for asset in assets if isinstance(asset,dict)}
 for asset in assets:
  if asset.get('reader_value'):
   path=out/asset.get('output_path','');
   if not path.is_file() or path.stat().st_size!=asset.get('bytes') or sha(path)!=asset.get('sha256'):fail('E_V2_ASSET','identity')
 v2_provisional_asset_closure(cfg['assets'],out,manifest_by_id)
 return {'status':'verified_v2_candidate','scenario_id':cfg['scenario_id'],'candidate_inventory_sha256':digest}

def v2_provisional_asset_closure(declared_assets, out, manifest_by_id):
 """Independently close every rendered binary:null full-page asset."""
 out=Path(out)
 for declared in declared_assets:
  if declared.get('disposition')!='reader' or declared.get('binary') is not None:continue
  provenance=declared.get('provenance',{});candidate_asset=manifest_by_id.get(declared['asset_id'])
  expected_path='assets/'+declared['asset_id']+'.png'
  if provenance.get('kind')!='reviewed_provisional_full_page' or not isinstance(candidate_asset,dict) or candidate_asset.get('output_path')!=expected_path:fail('E_V2_ASSET','provisional-manifest')
  path=out/expected_path
  if not path.is_file() or path.stat().st_size!=candidate_asset.get('bytes') or sha(path)!=candidate_asset.get('sha256'):fail('E_V2_ASSET','provisional-identity')
  try:
   with Image.open(path) as image:
    image.load();actual={'width':image.width,'height':image.height};format=image.format
  except OSError:fail('E_V2_ASSET','provisional-image')
  if format!='PNG' or actual!=provenance.get('output_dimensions') or provenance.get('physical_page')!=declared.get('source_page') or provenance.get('page_index_zero_based')!=declared['source_page']-1:fail('E_V2_ASSET','provisional-recipe')
def target(root,scenario,value):
 if not safe(value): fail('E_C2B_PATH','target (E_C2B_TARGET_PATH)')
 out=root/Path(value);parent=root/'kb_creator'/'working'/scenario/'master_en'/'candidates'
 if out.parent!=parent or not NAME.fullmatch(out.name): fail('E_C2B_PATH','target (E_C2B_TARGET_PATH)')
 return out
def topology(out):
 if not out.is_dir(): fail('E_C2B_TOPOLOGY','candidate')
 if any(rp(p) for p in (out,*out.parents)): fail('E_C2B_PATH','reparse')
 if {p.name for p in out.iterdir()}!=ROOT_NAMES: fail('E_C2B_TOPOLOGY','root')
 nodes=list(out.rglob('*'))
 if any(rp(p) for p in nodes): fail('E_C2B_PATH','candidate-node')
 if any(p.name=='MASTER_EN.acceptance.json' or '.staging.' in p.name for p in nodes): fail('E_C2B_TOPOLOGY','forbidden')
 if any(p.is_dir() and p!=out/'assets' for p in nodes): fail('E_C2B_TOPOLOGY','directory')
 files=[p for p in nodes if p.is_file()]
 if len(files)!=130 or len(list((out/'assets').iterdir()))!=123: fail('E_C2B_TOPOLOGY','130-files')
 return files
def qa_md(qa):
 lines=['# MASTER_EN QA','',f"Candidate state: {qa['candidate_state']}",'','## Artifacts','', '| Artifact | Path | Bytes | SHA-256 |','| --- | --- | ---: | --- |']
 lines += [f"| {n} | {v['path']} | {v['bytes']} | {v['sha256']} |" for n,v in sorted(qa['artifacts'].items())]
 lines += ['','## Metrics','', '| Metric | Value |','| --- | ---: |']+[f'| {n} | {v} |' for n,v in sorted(qa['metrics'].items())]
 lines += ['','## Gates','', '| Gate | Status | Evidence | Errors |','| --- | --- | --- | --- |']+[f"| {v['gate']} | {v['status']} | {', '.join(v['evidence'])} | {', '.join(v['errors'])} |" for v in qa['gates']]
 return '\n'.join(lines+['','No acceptance exists.',''])
def endpoint(text,char,byte,where):
 if not isinstance(char,int) or not isinstance(byte,int) or char<0 or byte<0 or char>len(text) or byte!=len(text[:char].encode('utf8')): fail('E_C2B_PROVENANCE',where)
def source_lines(package,page):
 raw=(Path(package)/'pages'/f'page-{page:03d}.md').read_text(encoding='utf8');lines=[];offset=0
 for text in raw.splitlines(keepends=True):
  if not re.fullmatch(r'<!-- source-page-\d{3} -->\r?\n?',text):lines.append((offset,offset+len(text),text))
  offset+=len(text)
 return raw,lines
RS_KEYS={'schema_version','semantic_fragments','authorized_suppressions','heading_policy','alt_policy'}
SEL_KEYS={'kind','occurrence','text'}
def rs_endpoint(lines,selector,end=False):
 keys={'kind','occurrence'} if selector.get('kind') in {'page_start','page_end'} else SEL_KEYS
 closed(selector,keys,'reader selector');kind=selector.get('kind');occurrence=selector.get('occurrence')
 if kind not in {'page_start','page_end','line_exact','line_prefix','markdown_heading_exact'} or not isinstance(occurrence,int) or occurrence<1: fail('E_C2B_READER_SURFACE','selector')
 content=[x for x in lines if x[2].strip()]
 if kind=='page_start': return content[0][0] if content else 0
 if kind=='page_end': return content[-1][1] if content else 0
 text=selector.get('text');
 if not isinstance(text,str) or not text: fail('E_C2B_READER_SURFACE','selector')
 found=[x for x in lines if (x[2].rstrip('\r\n')==text if kind in {'line_exact','markdown_heading_exact'} else x[2].rstrip('\r\n').startswith(text))]
 if len(found)!=occurrence: fail('E_C2B_READER_SURFACE','selector')
 return found[occurrence-1][1 if end else 0]
def reader_surface(cfg,package):
 rs=cfg.get('reader_surface');closed(rs,RS_KEYS,'reader_surface')
 if rs['schema_version']!='kb_creator.master_en_reader_surface.v1': fail('E_C2B_READER_SURFACE','version')
 closed(rs['heading_policy'],{'generated_mode','source_mode','max_level','overflow','duplicate_label'},'heading_policy')
 closed(rs['alt_policy'],{'require_nonempty','banned_substrings','banned_regexes'},'alt_policy')
 if rs['heading_policy']!={'generated_mode':'declared','source_mode':'owner_local','max_level':6,'overflow':'strong_label','duplicate_label':'strong_label'} or rs['alt_policy'].get('require_nonempty') is not True: fail('E_C2B_READER_SURFACE','policy')
 pages={p:source_lines(package,p) for p in range(1,125)};owners={x['anchor'] for x in cfg['hierarchy']};sem=[];sup=[]
 if not isinstance(rs['semantic_fragments'],list) or len(rs['semantic_fragments'])!=25 or not isinstance(rs['authorized_suppressions'],list) or len(rs['authorized_suppressions'])!=22: fail('E_C2B_READER_SURFACE','counts')
 for n,row in enumerate(rs['semantic_fragments'],1):
  closed(row,{'fragment_id','source_page','start','end','expected_owner','raw_sha256','order'},'semantic_fragment')
  if row['order']!=n or row['expected_owner'] not in owners or row['source_page'] not in pages or not HEX.fullmatch(row['raw_sha256']): fail('E_C2B_READER_SURFACE','semantic')
  raw,lines=pages[row['source_page']];a=rs_endpoint(lines,row['start']);b=rs_endpoint(lines,row['end']);value=raw[a:b]
  if a>=b or sha256_text(value)!=row['raw_sha256']: fail('E_C2B_READER_SURFACE','semantic')
  sem.append({'fragment_id':row['fragment_id'],'order':n,'owner_anchor':row['expected_owner'],'source_page':row['source_page'],'start_char':a,'end_char':b,'start_byte':len(raw[:a].encode()),'end_byte':len(raw[:b].encode()),'raw_sha256':row['raw_sha256']})
 for row in rs['authorized_suppressions']:
  closed(row,{'suppression_id','source_page','owner_anchor','start','end','raw_sha256','expected_occurrence','disposition','replacement_asset_id','authorial_text_affected','source_containment'},'suppression')
  closed(row['source_containment'],{'kind','claim_owner_anchor','claim_binding_kind','owned_page_proof'},'source containment')
  if row['owner_anchor'] not in owners or row['source_page'] not in pages or row['expected_occurrence']!=1 or row['authorial_text_affected'] is not False or row['disposition'] not in {'sidecar_only','omit_reader_duplicate'} or not HEX.fullmatch(row['raw_sha256']): fail('E_C2B_READER_SURFACE','suppression')
  raw,lines=pages[row['source_page']];a=rs_endpoint(lines,row['start']);b=rs_endpoint(lines,row['end'],True);value=raw[a:b]
  if a>=b or sha256_text(value)!=row['raw_sha256']: fail('E_C2B_READER_SURFACE','suppression')
  if row['source_containment']['kind'] not in {'normal_claim','owned_page_unit'}: fail('E_C2B_READER_SURFACE','containment')
  sup.append({'suppression_id':row['suppression_id'],'owner_anchor':row['owner_anchor'],'source_page':row['source_page'],'start_char':a,'end_char':b,'start_byte':len(raw[:a].encode()),'end_byte':len(raw[:b].encode()),'raw_sha256':row['raw_sha256'],'disposition':row['disposition'],'replacement_asset_id':row['replacement_asset_id'],'source_containment':row['source_containment']})
 for rows in (sem,sup):
  for a,b in zip(sorted(rows,key=lambda x:(x['source_page'],x['start_char'])),sorted(rows,key=lambda x:(x['source_page'],x['start_char']))[1:]):
   if a['source_page']==b['source_page'] and a['end_char']>b['start_char']: fail('E_C2B_READER_SURFACE','overlap')
 reader=[x for x in cfg['assets'] if x['representation']=='reader']
 if len(reader)!=107 or len({x['placement_index'] for x in reader})!=107: fail('E_C2B_READER_SURFACE','alts')
 for x in reader:
  alt=x.get('alt_text',''); policy=rs['alt_policy']
  if not isinstance(alt,str) or not alt.strip() or any(v.lower() in alt.lower() for v in policy['banned_substrings']) or any(re.search(v,alt) for v in policy['banned_regexes']): fail('E_C2B_READER_SURFACE','alt')
 return sem,sup
def locator_line(lines,locator):
 kind=locator['selector_kind'];selector=locator['selector']
 if kind=='page_start': found=lines[:1]
 elif kind=='line_prefix': found=[x for x in lines if x[2].rstrip('\r\n').startswith(selector)]
 else: found=[x for x in lines if x[2].rstrip('\r\n')==selector]
 if len(found)!=1: fail('E_C2B_PROVENANCE','locator')
 return found[0]
def expected_binding_spans(cfg,package):
 """Verifier-owned locator resolver; intentionally does not import builder code."""
 pages={p:source_lines(package,p) for p in range(1,125)}; starts={p:[] for p in pages}; rows=sorted(cfg['hierarchy'],key=lambda x:x['assembly_binding']['order'])
 reviews={x['review_id']:x for x in cfg['visual_review_units']}
 for row in rows:
  binding=row['assembly_binding']
  locator_pages=[]
  for locator in binding['locators']:
   start,_,_=locator_line(pages[locator['page']][1],locator);starts[locator['page']].append((start,row['anchor']));locator_pages.append(locator['page'])
  for page in binding['continuation_pages']:
   if page not in locator_pages:starts[page].append((0,row['anchor']))
 claims={anchor:[] for anchor in (x['anchor'] for x in rows)}
 for page,items in starts.items():
  ordered=sorted(items)
  if len({x[0] for x in ordered})!=len(ordered): fail('E_C2B_PROVENANCE','overlapping locators')
  raw=pages[page][0]
  for index,(start,anchor) in enumerate(ordered): claims[anchor].append((page,start,ordered[index+1][0] if index+1<len(ordered) else len(raw)))
 expected={}
 for row in rows:
  binding=row['assembly_binding'];spans=[]
  # Owned-page visual units have their source ownership proven by the visual
  # sidecar, but deliberately emit no prose provenance fragments.
  if binding['kind']!='generated' and binding['kind']!='owned_page_unit': spans=claims[row['anchor']]
  expected[row['anchor']]=spans
 return expected,pages
def local_transform(raw,span,locators,owner_level=None,owner_title=None,suppressions=()):
 edits=[]
 for locator in locators:
  if locator['page'] not in {x[0] for x in span}: continue
  for page,start,end in span:
   if page==locator['page'] and start<=locator['start']<end:
    if locator['action'] in {'replace_heading','consume_continuation_label'}: edits.append((locator['start']-start,locator['end']-start,''))
    elif locator['action']=='replace_label_retain_remainder': edits.append((locator['start']-start,locator['start']-start+len(locator['selector']),''))
 for start,end,value in sorted(edits,reverse=True): raw=raw[:start]+value+raw[end:]
 for start,end in sorted(suppressions,reverse=True): raw=raw[:start]+raw[end:]
 raw=re.sub(r'^<!-- source-page-\d{3} -->\r?\n?','',raw);raw=re.sub(r'^!\[[^\]]*\]\([^\n]*\)\s*\n?','',raw,flags=re.MULTILINE)
 if owner_level is None: raw=re.sub(r'^(#{1,6})(\s+)',lambda m:'#'*min(6,len(m.group(1))+1)+' ',raw,flags=re.MULTILINE)
 else:
  raw=re.sub(r'^(#{1,6})(\s+)(.*)$',lambda m:f"**{m.group(3).strip().rstrip('.')}.**" if m.group(3).strip()==owner_title or owner_level+len(m.group(1))>6 else '#'* (owner_level+len(m.group(1)))+' '+m.group(3).strip(),raw,flags=re.MULTILINE)
 return raw.rstrip()
def local_xrefs(raw,cfg,anchor,page,start,end):
 """Apply the closed line_exact substitutions assigned to this exact span."""
 for row in cfg['xrefs']:
  if row.get('source_selector')!='line_exact' or row.get('owner_anchor')!=anchor or row.get('source_page')!=page: continue
  line=row['source_line']
  if raw.count(line)==0: continue
  if raw.count(line)!=1: fail('E_C2B_PROVENANCE','xref')
  rebuilt='';cursor=0
  for segment in row['segments']:
   pos=line.find(segment['source_text'],cursor)
   if pos<0 or line.find(segment['source_text'],pos+1)!=-1: fail('E_C2B_PROVENANCE','xref')
   rebuilt+=line[cursor:pos]+(f"[{segment['reader_text']}](#{segment['target_anchor']})" if segment['emit_link'] else segment['reader_text']);cursor=pos+len(segment['source_text'])
  raw=raw.replace(line,rebuilt+line[cursor:],1)
 return raw
def local_edit_plan(raw,cfg,anchor,page,start,end,pages):
 edits=[]
 for row in cfg['xrefs']:
  if row.get('source_selector')!='line_exact' or row.get('owner_anchor')!=anchor or row.get('source_page')!=page: continue
  at=raw.find(row['source_line'])
  if at<0: continue
  if raw.find(row['source_line'],at+1)>=0: fail('E_C2B_PROVENANCE','xref')
  cursor=0
  for segment in row['segments']:
   pos=row['source_line'].find(segment['source_text'],cursor)
   if pos<0 or row['source_line'].find(segment['source_text'],pos+1)>=0: fail('E_C2B_PROVENANCE','xref')
   edits.append((at+pos,at+pos+len(segment['source_text']),f"[{segment['reader_text']}](#{segment['target_anchor']})" if segment['emit_link'] else segment['reader_text']));cursor=pos+len(segment['source_text'])
 edits += [(a,b,'') for a,b in suppression_spans(cfg,pages,page,anchor,start,end)]
 ordered=sorted(edits,key=lambda x:(x[0],x[1]))
 if any(left[1]>right[0] for left,right in zip(ordered,ordered[1:])): fail('E_C2B_PROVENANCE','source-edit-overlap')
 for a,b,value in reversed(ordered): raw=raw[:a]+value+raw[b:]
 return raw
def suppression_spans(cfg,pages,page,owner,start,end):
 rows=[]
 for row in cfg.get('reader_surface',{}).get('authorized_suppressions',[]):
  if row['source_page']!=page or row['source_containment']['claim_owner_anchor']!=owner: continue
  lines=pages[page][1]
  def find(selector,last=False):
   matches=[x for x in lines if x[2].rstrip('\r\n')==selector['text']]
   if len(matches)!=1: fail('E_C2B_PROVENANCE','suppression')
   return matches[0][1 if last else 0]
  a=find(row['start']);b=find(row['end'],True)
  if start<=a and b<=end: rows.append((a-start,b-start))
 return rows
def suppression_metrics(cfg,ledger,claims):
 normal=owned_page=cross=generated=unproven=bytes_total=0
 kinds={x['anchor']:x['assembly_binding']['kind'] for x in cfg['hierarchy']}
 review_pages={x['review_id']:x['source_pages'] for x in cfg['visual_review_units']}
 for row in ledger:
  containment=row['source_containment']; claimant=containment['claim_owner_anchor']; bytes_total+=row['end_byte']-row['start_byte']
  if containment['kind']=='normal_claim':
   normal+=1; proven=any(page==row['source_page'] and start<=row['start_char'] and row['end_char']<=end for page,start,end in claims.get(claimant,[])) and kinds.get(claimant)==containment['claim_binding_kind']
  elif containment['kind']=='owned_page_unit':
   owned_page+=1; proof=containment['owned_page_proof']; proven=kinds.get(claimant)=='owned_page_unit' and containment['claim_binding_kind']=='owned_page_unit' and isinstance(proof,dict) and proof.get('review_id')==proof.get('unit_ref') and row['source_page'] in review_pages.get(proof.get('review_id'),[])
  else: generated+=1; proven=False
  if not proven: unproven+=1
  if claimant!=row['owner_anchor']: cross+=1
 return {'authorized_suppression_rows':len(ledger),'authorized_suppression_utf8_bytes':bytes_total,'normal_claim_suppressions':normal,'owned_page_suppressions':owned_page,'cross_owner_suppressions':cross,'generated_suppression_claims':generated,'unproven_suppression_claims':unproven,'unauthorized_suppression_blocks':unproven}
def verify(contract,reconstruction_package,publication_config,source_pdf,target_value):
 cfg=parsed(publication_config);root=root_for(publication_config);out=target(root,cfg['scenario_id'],target_value);pre=preflight(contract,reconstruction_package,publication_config,source_pdf);semantic_ledger,suppression_ledger=reader_surface(cfg,reconstruction_package);expected_spans,page_cache=expected_binding_spans(cfg,reconstruction_package);suppression_conservation=suppression_metrics(cfg,suppression_ledger,expected_spans)
 if suppression_conservation!={'authorized_suppression_rows':22,'authorized_suppression_utf8_bytes':1911,'normal_claim_suppressions':17,'owned_page_suppressions':5,'cross_owner_suppressions':4,'generated_suppression_claims':0,'unproven_suppression_claims':0,'unauthorized_suppression_blocks':0}: fail('E_C2B_READER_SURFACE','suppression-conservation')
 files=topology(out)
 for p in files:
  if p.suffix in {'.json','.md'}: canonical(p) if p.suffix=='.json' else (p.read_bytes().endswith(b'\n') or fail('E_C2B_SCHEMA',p.relative_to(out).as_posix()))
 inv=canonical(out/'INVENTORY.json');closed(inv,['schema','algorithm','scope','rows','file_count','total_bytes','inventory_sha256'],'INVENTORY.json');rows,total,digest=inventory(out)
 if inv['schema']!='kb_creator.candidate_inventory.v1' or inv['algorithm']!=ALGO or inv['scope']!='all regular candidate files except INVENTORY.json' or inv['rows']!=rows or inv['file_count']!=129 or inv['total_bytes']!=total or inv['inventory_sha256']!=digest: fail('E_C2B_INVENTORY','INVENTORY.json')
 disp=canonical(out/'SOURCE_DISPOSITION.json');closed(disp,['schema','scenario_id','pages','summary'],'SOURCE_DISPOSITION.json')
 if disp['schema']!='kb_creator.source_disposition.v1' or disp['scenario_id']!=cfg['scenario_id'] or disp['pages']!=cfg['source_disposition'] or disp['summary'].get('page_count')!=124: fail('E_C2B_SEMANTIC','SOURCE_DISPOSITION.json')
 manifest=canonical(out/'ASSET_MANIFEST.json');closed(manifest,['schema','scenario_id','assets','summary'],'ASSET_MANIFEST.json')
 if manifest['schema']!='kb_creator.master_en_asset_manifest.v1' or len(manifest['assets'])!=123: fail('E_C2B_ASSET','manifest')
 asset_paths=[]
 declared_assets={x['asset_id']:x for x in cfg['assets']}; valid_anchors={x['anchor'] for x in cfg['hierarchy']}
 for asset in manifest['assets']:
  if set(asset)!={'asset_id','origin','logical_name','source','output_path','bytes','sha256','media_type','dimensions','source_page','source_region','semantic_role','representation','owner_anchor','placement_index','alt_text','visual_review_status'}: fail('E_C2B_ASSET',asset.get('asset_id','asset'))
  declared=declared_assets.get(asset['asset_id'])
  if not declared or asset['owner_anchor'] not in valid_anchors or any(asset[k]!=declared[k] for k in ('origin','logical_name','sha256','media_type','dimensions','source_page','source_region','representation','owner_anchor','placement_index','alt_text') if k in declared): fail('E_C2B_ASSET',asset['asset_id'])
  if not safe(asset.get('output_path')) or not asset['output_path'].startswith('assets/') or not HEX.fullmatch(asset.get('sha256','')): fail('E_C2B_ASSET','asset')
  p=out/asset['output_path'];asset_paths.append(asset['output_path'])
  if not p.is_file() or p.stat().st_size!=asset.get('bytes') or sha(p)!=asset['sha256']: fail('E_C2B_ASSET',asset['output_path'])
 if len(set(asset_paths))!=123: fail('E_C2B_ASSET','duplicate')
 if manifest.get('summary')!={'total':123,'reader':107,'evidence_only':16,'accepted_reconstruction_asset':121,'source_page_render':2}: fail('E_C2B_ASSET','summary')
 text=(out/'MASTER_EN.md').read_text(encoding='utf8');anchors=re.findall(r'<a id="([^"]+)"></a>',text);refs=re.findall(r'\]\((assets/[^)]+)\)',text)
 if len(anchors)!=168 or len(set(anchors))!=168 or len(refs)!=107 or any(x not in asset_paths for x in refs): fail('E_C2B_SEMANTIC','MASTER_EN.md')
 prov=canonical(out/'MASTER_EN.provenance.json');closed(prov,['schema','scenario_id','candidate_state','offset_contract','producer','inputs','master_en','units','structured_units','reader_surface'],'MASTER_EN.provenance.json')
 closed(prov['producer'],['script_path','script_sha256'],'producer');closed(prov['inputs'],['contract','publication_config','source_pdf','accepted_reconstruction'],'inputs')
 expected_inputs={'contract':{'path':str(Path(contract).resolve().relative_to(root)).replace('\\','/'),'bytes':Path(contract).stat().st_size,'sha256':sha(contract)},'publication_config':{'path':str(Path(publication_config).resolve().relative_to(root)).replace('\\','/'),'bytes':Path(publication_config).stat().st_size,'sha256':sha(publication_config)},'source_pdf':{'path':str(Path(source_pdf).resolve().relative_to(root)).replace('\\','/'),'bytes':Path(source_pdf).stat().st_size,'sha256':sha(source_pdf)},'accepted_reconstruction':cfg['accepted_reconstruction']}
 if prov['inputs']!=expected_inputs or prov['producer']!={'script_path':'kb_creator/scripts/build_scenario_master_en.py','script_sha256':sha(root/'kb_creator'/'scripts'/'build_scenario_master_en.py')}: fail('E_C2B_IDENTITY','provenance-inputs')
 manifest_by_id={x['asset_id']:x for x in manifest['assets']}
 expected_reader_surface={'semantic_fragments':semantic_ledger,'suppressions':[{**x,'claim_owner_anchor':x['source_containment']['claim_owner_anchor'],'source_occurrences':1,'applied_occurrences':1,'reader_occurrences':text.count((Path(reconstruction_package)/'pages'/f"page-{x['source_page']:03d}.md").read_text(encoding='utf8')[x['start_char']:x['end_char']]),'replacement_occurrences':text.count(f"]({manifest_by_id[x['replacement_asset_id']]['output_path']})")} for x in suppression_ledger],'alts':[{'asset_id':x['asset_id'],'output_path':manifest_by_id[x['asset_id']]['output_path'],'alt_text':x['alt_text'],'placement_index':x['placement_index']} for x in sorted((x for x in cfg['assets'] if x['representation']=='reader'),key=lambda x:x['asset_id'])]}
 if prov['reader_surface']!=expected_reader_surface: fail('E_C2B_READER_SURFACE','candidate-evidence')
 closed(prov['master_en'],['path','bytes','sha256'],'master_en')
 if prov['master_en']!={'path':'MASTER_EN.md','bytes':len(text.encode('utf8')),'sha256':sha(out/'MASTER_EN.md')}: fail('E_C2B_PROVENANCE','master_en')
 if prov['schema']!='kb_creator.master_en_provenance.v1' or prov['offset_contract']!={'char':'python_unicode_code_points','byte':'utf8_bytes','range':'zero_based_half_open'} or len(prov['units'])!=168 or len(prov['structured_units'])!=29: fail('E_C2B_PROVENANCE','header')
 hierarchy={x['anchor']:x for x in cfg['hierarchy']}
 ids=set();xrefs=[];structures=[]
 for unit in prov['units']:
  closed(unit,['anchor','binding_order','operations','source_fragments','output_fragments','asset_ids','xref_ids','structured_ids'],unit.get('anchor','unit'))
  anchor=unit['anchor']; row=hierarchy.get(anchor)
  if not row or unit['binding_order']!=row['assembly_binding']['order'] or len(unit['source_fragments'])!=len(unit['output_fragments']): fail('E_C2B_PROVENANCE',anchor)
  actual_spans=[(x.get('page'),x.get('start_char'),x.get('end_char'),x.get('start_byte'),x.get('end_byte'),x.get('sha256')) for x in unit['source_fragments']]
  wanted=[]
  for page,start,end in expected_spans[anchor]:
   raw=page_cache[page][0]; resolved=[]
   for declaration in row['assembly_binding']['locators']:
    if declaration['page']==page:
     loc_start,loc_end,_=locator_line(page_cache[page][1],declaration); resolved.append({**declaration,'start':loc_start,'end':loc_end})
   transformed=local_edit_plan(raw[start:end],cfg,anchor,page,start,end,page_cache)
   if local_transform(transformed,[(page,start,end)],resolved,row['level'],row['title']): wanted.append((page,start,end,len(raw[:start].encode('utf8')),len(raw[:end].encode('utf8')),sha256_text(raw[start:end])))
  # Navigation-only and owned-page units have wanted == []; every other unit
  # must retain the exact resolver-derived fragment sequence.
  if actual_spans!=wanted: fail('E_C2B_PROVENANCE',anchor)
  for source,output in zip(unit['source_fragments'],unit['output_fragments']):
   closed(source,['fragment_id','page','start_char','end_char','start_byte','end_byte','sha256'],unit['anchor']);closed(output,['fragment_id','start_char','end_char','start_byte','end_byte','sha256'],unit['anchor'])
   if source['fragment_id']!=output['fragment_id'] or source['fragment_id'] in ids: fail('E_C2B_PROVENANCE',unit['anchor'])
   if source['start_char']==source['end_char']: fail('E_C2B_PROVENANCE',unit['anchor'])
   ids.add(source['fragment_id']);page=Path(reconstruction_package)/'pages'/f"page-{source['page']:03d}.md"
   if not page.is_file(): fail('E_C2B_PROVENANCE',unit['anchor'])
   source_text=page.read_text(encoding='utf8');endpoint(source_text,source['start_char'],source['start_byte'],unit['anchor']);endpoint(source_text,source['end_char'],source['end_byte'],unit['anchor'])
   if source['start_char']>source['end_char'] or sha256_text(source_text[source['start_char']:source['end_char']])!=source['sha256']: fail('E_C2B_PROVENANCE',unit['anchor'])
   endpoint(text,output['start_char'],output['start_byte'],unit['anchor']);endpoint(text,output['end_char'],output['end_byte'],unit['anchor'])
   if output['start_char']>output['end_char'] or sha256_text(text[output['start_char']:output['end_char']])!=output['sha256']: fail('E_C2B_PROVENANCE',unit['anchor'])
   raw=page_cache[source['page']][0][source['start_char']:source['end_char']]
   local_locators=[]
   for declaration in row['assembly_binding']['locators']:
    if declaration['page']==source['page']:
     start,end,_=locator_line(page_cache[source['page']][1],declaration); local_locators.append({**declaration,'start':start,'end':end})
   raw=local_edit_plan(raw,cfg,anchor,source['page'],source['start_char'],source['end_char'],page_cache)
   transformed=local_transform(raw,[(source['page'],source['start_char'],source['end_char'])],local_locators,row['level'],row['title'])
   emitted=text[output['start_char']:output['end_char']]
   if transformed!=emitted: fail('E_C2B_PROVENANCE',unit['anchor'])
  xrefs += unit['xref_ids'];structures += unit['structured_ids']
 if len(ids)!=168 or sum(len(x['source_fragments']) for x in prov['units'])!=168 or sum(len(x['output_fragments']) for x in prov['units'])!=168: fail('E_C2B_PROVENANCE','fragment-conservation')
 if len(set(xrefs))!=237 or len(set(structures))!=29: fail('E_C2B_PROVENANCE','unions')
 expected_structures=[x['structure_id'] for x in cfg['structured_content']]
 if [x.get('structure_id') for x in prov['structured_units']]!=expected_structures: fail('E_C2B_STRUCTURE','structured_units')
 for row in prov['structured_units']:
  closed(row,['structure_id','classification','logical_owner','representation','fragments','attached_notes'] if row.get('classification')!='visual_form' else ['structure_id','classification','logical_owner','representation','asset_id','asset_sha256','review_ids','emitted_occurrence','fragments','attached_notes'],row.get('structure_id','structure'))
  if not isinstance(row['fragments'],list) or not isinstance(row['attached_notes'],list): fail('E_C2B_STRUCTURE',row['structure_id'])
  for fragment in row['fragments']:
   if not isinstance(fragment,dict) or not {'source_page','binding_anchor','source_sha256','emitted_sha256','source_start_char','source_end_char','source_start_byte','source_end_byte','emitted_start_char','emitted_end_char','emitted_start_byte','emitted_end_byte'}.issubset(fragment): fail('E_C2B_STRUCTURE',row['structure_id'])
  for note in row['attached_notes']:
   if not isinstance(note,dict) or not isinstance(note.get('selector'),str): fail('E_C2B_STRUCTURE',row['structure_id'])
 qa=canonical(out/'MASTER_EN.qa.json');closed(qa,['schema','scenario_id','candidate_state','artifacts','metrics','gates','errors'],'MASTER_EN.qa.json')
 expected_metrics={'source_pages':124,'anchors':168,'links':237,'xrefs_executed':237,'source_xref_rows':41,'source_xref_segments':42,'handouts':41,'structured_units':29,'reader_assets':107,'candidate_assets':123,'visual_review_units':91,'total_blocks':1935,'owned_blocks':1862,'generated_blocks':73,'unowned_blocks':0,'duplicate_blocks':0,**suppression_conservation,'reader_noise_findings':0,'editorial_lexical_deltas':0}
 if qa['schema']!='kb_creator.master_en_qa.v1' or qa.get('metrics')!=expected_metrics or qa.get('errors')!=[] or [g.get('gate') for g in qa['gates']]!=GATES or any(g.get('status')=='pass' for g in qa['gates'][9:]) or qa_md(qa).encode('utf8')!=(out/'MASTER_EN.qa.md').read_bytes(): fail('E_C2B_QA','qa')
 return {'status':'verified_candidate_pending_process_and_external_gates','scenario_id':cfg['scenario_id'],'candidate_inventory_sha256':digest,'inventory_file_sha256':sha(out/'INVENTORY.json'),'master_en_sha256':sha(out/'MASTER_EN.md'),'publication_config_sha256':pre['publication_config_sha256']}
def sha256_text(value): return hashlib.sha256(value.encode('utf8')).hexdigest().upper()
def main():
 p=argparse.ArgumentParser();[p.add_argument('--'+x,required=True) for x in ('contract','reconstruction-package','publication-config','target')];p.add_argument('--source-pdf');p.add_argument('--preflight-only',action='store_true');p.add_argument('--report-path');a=p.parse_args()
 try:
  schema=parsed(a.publication_config).get('schema')
  if a.report_path and (a.preflight_only or schema!=V2_SCHEMA):fail('E_V2_REPORT','unsupported route')
  if a.preflight_only:
   result=preflight(a.contract,a.reconstruction_package,a.publication_config,a.source_pdf)
  elif a.report_path:
   result=write_v2_verification_report(a.publication_config,a.target,a.report_path)
  elif schema==V3_SCHEMA:
   result=verify_v3_candidate(a.contract,a.reconstruction_package,a.publication_config,a.target,a.source_pdf)
  elif schema==V2_SCHEMA:
   result=verify_v2_candidate(a.publication_config,a.target)
  else:
   result=verify(a.contract,a.reconstruction_package,a.publication_config,a.source_pdf,a.target)
 except ValueError as e: print(str(e),file=sys.stderr);raise SystemExit(1)
 print(json.dumps(result,sort_keys=True))
if __name__=='__main__': main()
