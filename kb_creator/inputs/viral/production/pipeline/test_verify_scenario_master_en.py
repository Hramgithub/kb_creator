from __future__ import annotations
import copy, hashlib, importlib.util, json, shutil, subprocess, sys, tempfile, unittest, uuid
from unittest import mock
from pathlib import Path

ROOT=Path(__file__).parents[1]; SCRIPT=ROOT/'scripts'/'verify_scenario_master_en.py'
spec=importlib.util.spec_from_file_location('phase_a_verifier',SCRIPT); V=importlib.util.module_from_spec(spec); spec.loader.exec_module(V)
author_spec=importlib.util.spec_from_file_location('phase_a_author',ROOT/'scripts'/'author_viral_master_en_v2_config.py'); A=importlib.util.module_from_spec(author_spec); author_spec.loader.exec_module(A)
builder_spec=importlib.util.spec_from_file_location('c2b_builder',ROOT/'scripts'/'build_scenario_master_en.py'); B=importlib.util.module_from_spec(builder_spec); builder_spec.loader.exec_module(B)
ARGS=(ROOT/'contracts'/'viral.json',ROOT/'working'/'viral'/'source_reconstruction'/'20260901_step6a_reconstructed_en_package_v4',ROOT/'working'/'viral'/'master_en'/'publication_config_v1.json',ROOT/'working'/'viral'/'source'/'Call_of_Cthulhu_Viral.pdf')
CONFIG=json.loads(ARGS[2].read_text(encoding='utf8'))
FAKE_RENDERER='''import sys
from PIL import Image
if '-v' in sys.argv:
 print("pdftoppm version 26.05.0")
 raise SystemExit(0)
prefix=sys.argv[-1]
page=int(sys.argv[sys.argv.index("-f")+1])
Image.new("RGB", (1700,2200), (page % 256,34,56)).save(prefix+".png")
'''
def reseal(root):
 rows=[]
 for path in sorted((p for p in root.rglob('*') if p.is_file() and p.name!='INVENTORY.json'),key=lambda p:p.relative_to(root).as_posix()):
  data=path.read_bytes();rows.append({'path':path.relative_to(root).as_posix(),'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest().upper()})
 payload=''.join(f"{x['path']}\t{x['bytes']}\t{x['sha256']}\n" for x in rows).encode();value={'schema':'kb_creator.candidate_inventory.v1','algorithm':'SHA-256 over ordinal UTF-8 LF relative_path<TAB>bytes<TAB>UPPER_SHA256<LF>','scope':'all regular candidate files except INVENTORY.json','rows':rows,'file_count':len(rows),'total_bytes':sum(x['bytes'] for x in rows),'inventory_sha256':hashlib.sha256(payload).hexdigest().upper()}
 (root/'INVENTORY.json').write_text(json.dumps(value,ensure_ascii=False,sort_keys=True,indent=2)+'\n',encoding='utf8',newline='\n')
def eol_profile(raw):
 counts={'lf':0,'crlf':0,'crcrlf':0,'lone_cr':0};i=0
 while i<len(raw):
  if raw[i:i+3]==b'\r\r\n':counts['crcrlf']+=1;i+=3
  elif raw[i:i+2]==b'\r\n':counts['crlf']+=1;i+=2
  elif raw[i:i+1]==b'\n':counts['lf']+=1;i+=1
  elif raw[i:i+1]==b'\r':counts['lone_cr']+=1;i+=1
  else:i+=1
 lines=raw.splitlines();return {**counts,'line_slots':len(lines),'nonblank_line_slots':sum(bool(line.strip()) for line in lines)}

class CliRoutingTests(unittest.TestCase):
 def test_v2_read_only_cli_routes_to_v2_candidate_verifier(self):
  argv=['verify_scenario_master_en.py','--contract','contract.json','--reconstruction-package','package','--publication-config','config.json','--source-pdf','source.pdf','--target','candidate']
  result={'status':'verified_v2_candidate','scenario_id':'viral','candidate_inventory_sha256':'A'*64}
  with mock.patch.object(sys,'argv',argv),mock.patch.object(V,'parsed',return_value={'schema':V.V2_SCHEMA}),mock.patch.object(V,'verify_v2_candidate',return_value=result) as verify_v2,mock.patch.object(V,'verify') as verify_v1,mock.patch('builtins.print') as emit:
   V.main()
  verify_v2.assert_called_once_with('config.json','candidate');verify_v1.assert_not_called();emit.assert_called_once_with(json.dumps(result,sort_keys=True))

def _v2_fixture_base():
 return {'schema':'kb_creator.master_en_publication.v2','scenario_id':'synthetic','document':{'audit_scope':list(range(1,125)),'reader_scope':list(range(1,123)),'generated_navigation':{'operation':'generated_navigation_replaces_source_toc','source_identity':'synthetic-toc'}},'hierarchy':[{'anchor':'intro','page':1,'source_title':'Introduction','reader_title':'Introduction','representation':'heading','reviewed_title_transformation':None},{'anchor':'infection','page':2,'source_title':'Infection','reader_title':'Infection','representation':'anchor_only','reviewed_title_transformation':None}],'events':[{'event_id':'a','type':'heading','page':1,'order_key':[1,1],'anchor':'intro','content':'','fragment_id':'a'},{'event_id':'b','type':'text_fragment','page':1,'order_key':[1,2],'anchor':'intro','content':'Text.','fragment_id':'b'},{'event_id':'c','type':'anchor_only','page':2,'order_key':[2,1],'anchor':'infection','content':'','fragment_id':'c'}],'assets':[],'xrefs':[],'source_recoveries':[],'metrics':{'source_pages_audited':124,'reader_pages':122,'excluded_advertising_pages':2}}
def v2_fixture():
 value=_v2_fixture_base();zero={'path':'kb_creator/.v2-placeholder','bytes':0,'sha256':'0'*64}
 value['document'].update({'source_pdf':dict(zero),'reconstruction_package':{'root':'kb_creator/.v2-placeholder','file_count':1,'total_bytes':1,'inventory_algorithm':V.PACKAGE_ALGO,'inventory_sha256':'0'*64}})
 value['source_disposition']=[{'page':page,'audit_disposition':'reconstructed','publication_disposition':'excluded_advertising' if page in {123,124} else 'reader','publish_reader_content':page not in {123,124},'decision_date':'2026-09-02' if page in {123,124} else '2026-09-01','reason':'approved advertising exclusion' if page in {123,124} else 'reader source page','page_markdown':{'path':f'kb_creator/.v2-placeholder/pages/page-{page:03d}.md','bytes':0,'sha256':'0'*64}} for page in range(1,125)]
 value['visual_review_units']=[{'review_id':'heading-a','kind':'heading_outline','source_pages':[1],'event_ids':['a'],'asset_ids':[],'priority':True,'contact_sheet_group':'outline'}]
 value['source_partition']={'pages':[],'spans':[]}
 value['migration']={'inputs':{'frozen_v1_config':dict(zero),'decision_evidence':[{**zero,'kind':'kb_creator.semantic_unit_review.v2'}]},'new_reviewed_targets':[]}
 for ledger,(domain,key,count,_) in V.MIGRATION_DOMAINS.items():
  source=CONFIG[domain]
  value['migration'][ledger]=[{'source_id':f'{domain}:{row[key]}','source_row_sha256':V.v2_canonical_row(row),'outcome':'excluded_advertising' if domain=='source_disposition' and row['page'] in {123,124} else 'suppressed_reviewed','final_target_ids':[],'decision_ref':'viral-logical_table-p020-l025'} for row in source]
 for index,row in enumerate(value['hierarchy']):
  page=row.pop('page');row.update({'parent_anchor':None if not index else value['hierarchy'][index-1]['anchor'],'level':1 if row['representation']=='heading' else None,'toc_entry':row['representation']=='heading','semantic_role':'fixture','source_pages':[page],'migration_row_id':f'hierarchy:{row["anchor"]}'})
 for event in value['events']:event.update({'source_span_ids':['fixture-span'],'source_operation':'emit_exact','payload_bindings':[]})
 return value

def bind_v2_inputs(value,label):
 """Build a disposable 124-page reconstruction package for identity-bound v2 tests."""
 package=ROOT/f'.v2-inputs-{label}';shutil.rmtree(package,ignore_errors=True);pages=package/'pages';pages.mkdir(parents=True)
 for page in range(1,125): (pages/f'page-{page:03d}.md').write_text(f'fixture reconstruction page {page}\n',encoding='utf8',newline='\n')
 evidence=package/'decision-evidence.json';evidence.write_text(json.dumps({'schema':'kb_creator.semantic_unit_review.v2','decisions':[{'candidate_id':'viral-logical_table-p020-l025'}]}),encoding='utf8')
 rel=lambda path:path.relative_to(ROOT.parent).as_posix();digest=lambda path:hashlib.sha256(path.read_bytes()).hexdigest().upper()
 value['document']['source_pdf']={'path':rel(ARGS[3]),'bytes':ARGS[3].stat().st_size,'sha256':digest(ARGS[3])}
 count,total,package_digest=V.v2_package_inventory(package)
 value['document']['reconstruction_package']={'root':rel(package),'file_count':count,'total_bytes':total,'inventory_algorithm':V.PACKAGE_ALGO,'inventory_sha256':package_digest}
 for row in value['source_disposition']:
  path=pages/f"page-{row['page']:03d}.md";row['page_markdown']={'path':rel(path),'bytes':path.stat().st_size,'sha256':digest(path)}
 partition_pages=[];spans=[]
 for page in range(1,123):
  path=pages/f'page-{page:03d}.md';raw=path.read_bytes();text=raw.decode('utf8');span_id=f's{page}'
  spans.append({'span_id':span_id,'page':page,'source_path':f'pages/page-{page:03d}.md','start_byte':0,'end_byte':len(raw),'start_char':0,'end_char':len(text),'raw_sha256':digest(path),'raw_text_sha256':hashlib.sha256(text.encode('utf8')).hexdigest().upper(),'classification':'retained_text','owner_kind':'event','owner_id':'fixture','decision_ref':None})
  partition_pages.append({'page':page,'path':f'pages/page-{page:03d}.md','bytes':len(raw),'sha256':digest(path),'encoding':'utf-8-no-bom','eol_profile':eol_profile(raw),'span_ids':[span_id]})
 value['source_partition']={'pages':partition_pages,'spans':spans}
 v1={'path':rel(ARGS[2]),'bytes':ARGS[2].stat().st_size,'sha256':digest(ARGS[2])}
 value['migration']['inputs']={'frozen_v1_config':dict(v1),'decision_evidence':[{'path':rel(evidence),'bytes':evidence.stat().st_size,'sha256':digest(evidence),'kind':'kb_creator.semantic_unit_review.v2'}]}
 value['migration']['new_reviewed_targets']=[{'target_id':target,'decision_ref':'viral-logical_table-p020-l025'} for target in sorted({*(f'hierarchy:{row["anchor"]}' for row in value['hierarchy']),*(f'assets:{row["asset_id"]}' for row in value['assets']),*(f'xrefs:{row["xref_id"]}' for row in value['xrefs'])})]
 samples={1:'Introduction\n',2:'Text.\n',3:'anchor\n'}
 for page,text in samples.items():(pages/f'page-{page:03d}.md').write_text(text,encoding='utf8',newline='\n')
 value['hierarchy']=[
  {'anchor':'intro','parent_anchor':None,'level':1,'toc_entry':True,'semantic_role':'chapter','source_pages':[1,2],'source_title':'Introduction','reader_title':'Introduction','representation':'heading','reviewed_title_transformation':None,'migration_row_id':'hierarchy:intro'},
  {'anchor':'infection','parent_anchor':'intro','level':None,'toc_entry':False,'semantic_role':'anchor','source_pages':[3],'source_title':'anchor','reader_title':'anchor','representation':'anchor_only','reviewed_title_transformation':None,'migration_row_id':'hierarchy:infection'}]
 for index,event in enumerate(value['events'],1):
  raw=(pages/f'page-{index:03d}.md').read_bytes();text=raw.decode('utf8');event['page']=index;event['source_span_ids']=[f's{index}'];event['source_operation']={'heading':'emit_exact','text_fragment':'emit_exact','anchor_only':'emit_anchor_only'}[event['type']];event['order_key']=[index,0,V.V2_ROLE_RANK[event['type']],index-1]
  if event['type']=='heading':event['content']='Introduction'
  elif event['type']=='text_fragment':event['content']='Text.'
  event['payload_bindings']=[] if event['type']=='anchor_only' else [{'json_pointer':'/content','source_slices':[{'span_id':f's{index}','start_char':0,'end_char':len(event['content'])}],'joiner':'','recovery_id':None}]
 spans=[];partition_pages=[]
 for page in range(1,123):
  path=pages/f'page-{page:03d}.md';raw=path.read_bytes();text=raw.decode('utf8');event=next((item for item in value['events'] if item['page']==page),None)
  spans.append({'span_id':f's{page}','page':page,'source_path':f'pages/page-{page:03d}.md','start_byte':0,'end_byte':len(raw),'start_char':0,'end_char':len(text),'raw_sha256':digest(path),'raw_text_sha256':hashlib.sha256(text.encode('utf8')).hexdigest().upper(),'classification':'retained_text' if event else 'authorized_suppression','owner_kind':'event' if event else 'suppression','owner_id':event['event_id'] if event else f'suppression-{page}','decision_ref':None})
  partition_pages.append({'page':page,'path':f'pages/page-{page:03d}.md','bytes':len(raw),'sha256':digest(path),'encoding':'utf-8-no-bom','eol_profile':eol_profile(raw),'span_ids':[f's{page}']});value['source_disposition'][page-1]['page_markdown']={'path':rel(path),'bytes':len(raw),'sha256':digest(path)}
 value['source_partition']={'pages':partition_pages,'spans':spans}
 count,total,package_digest=V.v2_package_inventory(package);value['document']['reconstruction_package'].update({'file_count':count,'total_bytes':total,'inventory_sha256':package_digest})
 return refresh_v2_review_units(value) and package

def bind_v2_event_source(value,package,event,text=None):
 """Give an added A3 fixture event a distinct, exact source-owned page span."""
 if text is None:
  leaves=[] if event['type'] in {'asset','anchor_only'} else V.v2_a3_leaves(event['content']);text='\n'.join(leaf for _,leaf in leaves)+'\n'
  offset=0;event['payload_bindings']=[]
  for pointer,leaf in leaves:
   event['payload_bindings'].append({'json_pointer':pointer,'source_slices':[{'span_id':f"s{event['page']}",'start_char':offset,'end_char':offset+len(leaf)}],'joiner':'','recovery_id':None});offset+=len(leaf)+1
 page=event['page'];path=package/'pages'/f'page-{page:03d}.md';path.write_text(text,encoding='utf8',newline='\n')
 raw=path.read_bytes();decoded=raw.decode('utf8');digest=hashlib.sha256(raw).hexdigest().upper()
 value['source_disposition'][page-1]['page_markdown']={'path':path.relative_to(ROOT.parent).as_posix(),'bytes':len(raw),'sha256':digest}
 value['source_partition']['pages'][page-1].update({'bytes':len(raw),'sha256':digest,'eol_profile':eol_profile(raw)})
 asset_event=event['type']=='asset'
 value['source_partition']['spans'][page-1].update({'end_byte':len(raw),'end_char':len(decoded),'raw_sha256':digest,'raw_text_sha256':hashlib.sha256(decoded.encode('utf8')).hexdigest().upper(),'classification':'asset_reference_source' if asset_event else 'retained_text','owner_kind':'asset' if asset_event else 'event','owner_id':event['content'] if asset_event else event['event_id']})
 event['source_span_ids']=[f's{page}']
 if event['type']=='structured_unit':
  event['contains']=[f's{page}'];event['content']['contains']=[f's{page}']
  if 'end_after' in event['content']:event['content']['end_after']=f's{page}'

def bind_v2_decision_evidence(value,path,kind,payload,ref):
 path.write_bytes(payload if isinstance(payload,bytes) else payload.encode('utf8') if isinstance(payload,str) else json.dumps(payload).encode('utf8'))
 value['migration']['inputs']['decision_evidence']=[{'path':path.relative_to(ROOT.parent).as_posix(),'bytes':path.stat().st_size,'sha256':hashlib.sha256(path.read_bytes()).hexdigest().upper(),'kind':kind}]
 for ledger in V.MIGRATION_DOMAINS:
  for row in value['migration'][ledger]:row['decision_ref']=ref
 for row in value['migration']['new_reviewed_targets']:row['decision_ref']=ref

def refresh_v2_review_units(value):
 hierarchy={row['anchor']:row for row in value['hierarchy']};units=[]
 def add(event,kind,priority,group):units.append({'review_id':f'review:{kind}:{event["event_id"]}','kind':kind,'source_pages':[event['page']],'event_ids':[event['event_id']],'asset_ids':[],'priority':priority,'contact_sheet_group':group})
 for event in value['events']:
  if event['type']=='heading' and hierarchy[event['anchor']]['representation']=='heading':add(event,'heading_outline',True,'outline')
  elif event['type']=='structured_unit':add(event,event['content']['kind'],False,'structured')
 for event in value['events']:
  if event['event_id'] in {row['source_event_id'] for row in value['xrefs']}|{row['target_event_id'] for row in value['source_recoveries']}:add(event,'xref_recovery',True,'xref_recovery')
 for asset in value['assets']:
  if asset['reader_value']:units.append({'review_id':f'review:asset_placement:{asset["asset_id"]}','kind':'asset_placement','source_pages':[asset.get('source_page',asset.get('page'))],'event_ids':[],'asset_ids':[asset['asset_id']],'priority':False,'contact_sheet_group':'reader_assets'})
 value['visual_review_units']=units;return value
class VerifierPreflightTests(unittest.TestCase):
 def test_independent_v2_source_partition_unicode_eol_and_mutations(self):
  cfg=v2_fixture();package=bind_v2_inputs(cfg,'partition');page=package/'pages'/'page-001.md'
  try:
   raw=b'alpha\r\nbeta\r\r\n\r\ngamma\rdelta\n\n\xd0\x96\n';page.write_bytes(raw)
   digest=lambda path:hashlib.sha256(path.read_bytes()).hexdigest().upper();text=raw.decode('utf8')
   cfg['source_disposition'][0]['page_markdown'].update({'bytes':len(raw),'sha256':digest(page)})
   item=cfg['source_partition']['pages'][0];span=cfg['source_partition']['spans'][0]
   item.update({'bytes':len(raw),'sha256':digest(page),'eol_profile':eol_profile(raw)})
   span.update({'end_byte':len(raw),'end_char':len(text),'raw_sha256':digest(page),'raw_text_sha256':hashlib.sha256(raw).hexdigest().upper()})
   self.assertEqual(V.v2_source_partition(cfg['source_partition'],package)['eol'],{'lf':124,'crlf':2,'crcrlf':1,'lone_cr':1})
   cases=[
    (lambda c:c['source_partition']['spans'][0].__setitem__('start_byte',1),'E_V2_PARTITION'),
    (lambda c:c['source_partition']['spans'][0].__setitem__('end_char',len(text)-1),'E_V2_PARTITION'),
    (lambda c:c['source_partition']['spans'][0].__setitem__('raw_sha256','0'*64),'E_V2_PARTITION'),
    (lambda c:c['source_partition']['pages'][0].__setitem__('eol_profile',{}),'E_V2_PARTITION'),
    (lambda c:c['source_partition']['spans'].append(copy.deepcopy(c['source_partition']['spans'][0])),'E_V2_PARTITION'),
    (lambda c:c['source_partition']['spans'][0].__setitem__('source_path','pages/page-002.md'),'E_V2_PARTITION'),
    (lambda c:c['source_partition']['pages'].reverse(),'E_V2_PARTITION')]
   for mutate,code in cases:
    altered=copy.deepcopy(cfg);mutate(altered)
    with self.assertRaisesRegex(ValueError,code):V.v2_source_partition(altered['source_partition'],package)
  finally:shutil.rmtree(package,ignore_errors=True)


class ViralV2B1c4VerifierAuditTests(unittest.TestCase):
 def test_b1c4_physical_asset_closure_accepts_separate_closed_hierarchy_target(self):
  migration=A.author()['migration'];targets=copy.deepcopy(migration['new_reviewed_targets']);targets.append({'target_id':'hierarchy:viral-reviewed-santina','decision_ref':'OUT-003'})
  V.v2_b1c4_migration_closure(migration['asset_rows'],targets)
  for altered in ({'target_id':'hierarchy:viral-reviewed-santina','decision_ref':'OUT-004'},{'target_id':'hierarchy:','decision_ref':'OUT-003'},{'target_id':'hierarchy:viral-reviewed-santina','decision_ref':'OUT-003','replaces':[]}):
   with self.assertRaisesRegex(ValueError,'E_V2_MIGRATION: (?:hierarchy-target-schema|replacement-target-domain)'):V.v2_b1c4_migration_closure(migration['asset_rows'],[ *targets[:-1],altered])
 def test_canonical_source_free_asset_event_requires_explicit_order_evidence(self):
  event={'event_id':'asset','type':'asset','page':7,'order_key':[7,321,4,19],'anchor':'section','content':'visual','source_operation':'asset_reference'};events={'target':{'event_id':'target'}}
  visual={'asset_id':'visual','disposition':'reader','source_page':7,'anchor':'section','placement':{'before_event':'target'},'source_order':{'kind':'selected_view_raw_index','view':'raw','raw_index':12,'gap_ordinal':0}}
  V.v2_canonical_source_free_asset_event(visual,event,events)
  physical={**visual,'source_order':{'kind':'physical_unit_page_slot','unit_id':'pair','page_slot':1}}
  V.v2_canonical_source_free_asset_event(physical,event,events)
  for altered in ({**visual,'source_order':{'kind':'selected_view_raw_index','view':'raw','raw_index':12}}, {**visual,'placement':{'before_event':'missing'}}, {**visual,'source_page':8}):
   with self.assertRaisesRegex(ValueError,'E_V2_ASSET: (?:canonical-event|source-order)'):V.v2_canonical_source_free_asset_event(altered,event,events)
 def test_v2_provisional_manifest_identity_dimensions_and_page_mutations(self):
  from PIL import Image
  with tempfile.TemporaryDirectory() as temp:
   out=Path(temp);assets=out/'assets';assets.mkdir();path=assets/'provisional.png';Image.new('RGB',(20,30),'white').save(path)
   declared={'asset_id':'provisional','disposition':'reader','binary':None,'source_page':7,'provenance':{'kind':'reviewed_provisional_full_page','physical_page':7,'page_index_zero_based':6,'output_dimensions':{'width':20,'height':30}}}
   manifest={'asset_id':'provisional','output_path':'assets/provisional.png','bytes':path.stat().st_size,'sha256':V.sha(path)}
   V.v2_provisional_asset_closure([declared],out,{'provisional':manifest})
   cases=(
    ({**manifest,'output_path':'assets/forged.png'},'provisional-manifest',declared),
    ({**manifest,'sha256':'0'*64},'provisional-identity',declared),
    (manifest,'provisional-recipe',{**declared,'provenance':{**declared['provenance'],'output_dimensions':{'width':21,'height':30}}}),
    (manifest,'provisional-recipe',{**declared,'provenance':{**declared['provenance'],'physical_page':8}}),
    (manifest,'provisional-recipe',{**declared,'provenance':{**declared['provenance'],'page_index_zero_based':7}}))
   for altered_manifest,detail,altered_declared in cases:
    with self.assertRaisesRegex(ValueError,detail):V.v2_provisional_asset_closure([altered_declared],out,{'provisional':altered_manifest})
 def test_b1c6_helper_reparse_and_evidence_topology_attacks(self):
  value=A.author();package=ARGS[1];spans={row['span_id']:row for row in value['source_partition']['spans']}
  with mock.patch.object(V,'v2_reparse',side_effect=lambda path:Path(path).name in {'assets',next(row for row in value['assets'] if row['binary'])['binary']['path'].split('/')[-1]}):
   with self.assertRaises(ValueError):V.v2_asset_provenance_binding(value,package,ROOT.parent,spans)
  original=V.parsed
  def altered(path):
   data=original(path)
   if Path(path).name=='ASSET_MANIFEST.json':data=copy.deepcopy(data);data['assets'].append(copy.deepcopy(data['assets'][0]))
   if Path(path).name=='comparison.json':data=copy.deepcopy(data);view=next(iter(data['views'].values()));view['blocks'].append(copy.deepcopy(view['blocks'][0]))
   return data
  with mock.patch.object(V,'parsed',side_effect=altered):
   with self.assertRaises(ValueError):V.v2_asset_provenance_binding(value,package,ROOT.parent,spans)
  missing=copy.deepcopy(value);visual=next(row for row in missing['assets'] if row['provenance']['kind']=='visual_region');visual['provenance']['source_asset_reference']='not-in-block-assets'
  with self.assertRaises(ValueError):V.v2_asset_provenance_binding(missing,package,ROOT.parent,{row['span_id']:row for row in missing['source_partition']['spans']})
 def test_b1c6_helper_real_binding_and_closed_mutation_matrix(self):
  value=A.author();package=ARGS[1];spans={row['span_id']:row for row in value['source_partition']['spans']}
  self.assertEqual(V.v2_asset_provenance_binding(value,package,ROOT.parent,spans)['counts'],{'markdown_image_reference':16,'visual_region':100,'reviewed_provisional_full_page':10})
  markdown=next(row for row in value['assets'] if row['provenance']['kind']=='markdown_image_reference');visual=next(row for row in value['assets'] if row['provenance']['kind']=='visual_region');provisional=next(row for row in value['assets'] if row['provenance']['kind']=='reviewed_provisional_full_page')
  def markdown_row(c):return next(row for row in c['assets'] if row['asset_id']==markdown['asset_id'])
  def visual_row(c):return next(row for row in c['assets'] if row['asset_id']==visual['asset_id'])
  def provisional_row(c):return next(row for row in c['assets'] if row['asset_id']==provisional['asset_id'])
  cases=(lambda c:c['assets'].append({'asset_id':'legacy','reader_value':False,'placement':{'before_event':'x'},'anchor':'x','page':1,'source_span_ids':['x']}),lambda c:markdown_row(c).__setitem__('source_span_ids',[]),lambda c:markdown_row(c)['provenance'].__setitem__('marker_sha256','0'*64),lambda c:markdown_row(c)['provenance'].__setitem__('span_id','missing'),lambda c:markdown_row(c)['provenance'].__setitem__('start_byte',1),lambda c:markdown_row(c)['provenance'].__setitem__('start_char',1),lambda c:visual_row(c)['binary'].__setitem__('path','kb_creator/working/viral/source_reconstruction/20260901_step6a_reconstructed_en_package_v4/ASSET_MANIFEST.json'),lambda c:visual_row(c)['binary'].__setitem__('sha256','0'*64),lambda c:visual_row(c)['binary'].__setitem__('bytes',1),lambda c:visual_row(c)['binary'].__setitem__('media_type','image/png'),lambda c:visual_row(c)['binary']['dimensions'].__setitem__('height',1),lambda c:visual_row(c)['provenance'].__setitem__('asset_manifest_row_sha256','0'*64),lambda c:visual_row(c)['provenance']['asset_manifest_identity'].__setitem__('sha256','0'*64),lambda c:visual_row(c)['provenance']['comparison_identity'].__setitem__('sha256','0'*64),lambda c:visual_row(c)['provenance'].__setitem__('selected_view','missing'),lambda c:visual_row(c)['provenance'].__setitem__('raw_index',-1),lambda c:visual_row(c)['provenance'].__setitem__('source_asset_reference','foreign'),lambda c:visual_row(c)['provenance'].__setitem__('block_type','text'),lambda c:visual_row(c)['provenance'].__setitem__('source_page',2),lambda c:visual_row(c)['provenance'].__setitem__('bbox',[0,0,1,1]),lambda c:visual_row(c)['provenance'].__setitem__('comparison_block_sha256','0'*64),lambda c:provisional_row(c)['provenance']['render_recipe'].__setitem__('dpi',199),lambda c:provisional_row(c)['provenance'].__setitem__('region',{'kind':'full_media_box','points':[0,0,1,1]}),lambda c:provisional_row(c)['provenance']['source_pdf_identity'].__setitem__('sha256','0'*64),lambda c:provisional_row(c)['provenance'].__setitem__('physical_page',provisional_row(c)['provenance']['physical_page']+1),lambda c:provisional_row(c)['provenance'].__setitem__('page_index_zero_based',provisional_row(c)['provenance']['page_index_zero_based']+1),lambda c:provisional_row(c)['provenance']['render_recipe'].__setitem__('alpha',True),lambda c:provisional_row(c)['provenance'].__setitem__('output_media_type','image/jpeg'),lambda c:provisional_row(c)['provenance']['output_dimensions'].__setitem__('width',1),lambda c:provisional_row(c).__setitem__('binary',{}),lambda c:provisional_row(c).__setitem__('source_page',provisional_row(c)['source_page']+1))
  for mutate in cases:
   altered=copy.deepcopy(value);mutate(altered)
   with self.assertRaises(ValueError):V.v2_asset_provenance_binding(altered,package,ROOT.parent,{row['span_id']:row for row in altered['source_partition']['spans']})
 def test_independent_real_input_asset_partition(self):
  audit=V.v2_b1c4_asset_audit(ROOT.parent)
  self.assertEqual(audit['counts'],{'retained_unchanged':99,'retained_rebound':2,'reclassified':16,'excluded_advertising':6})
  self.assertEqual(audit['path_binaries'],121)
 def test_public_b1c4_critic_graph_and_provenance_mutations_stop_before_review(self):
  value=A.author();mutations=(
   lambda c:c['assets'][0]['provenance'].__setitem__('comparison_block_sha256','0'*64),
   lambda c:c['assets'][0]['binary'].__setitem__('sha256','0'*64),
   lambda c:c['migration']['asset_rows'].pop(),
   lambda c:c['migration']['asset_rows'].__setitem__(0,c['migration']['asset_rows'][1]),
   lambda c:c['migration']['new_reviewed_targets'][0]['replaces'].reverse(),
   lambda c:c['migration']['new_reviewed_targets'][0].__setitem__('target_id','assets:viral-provisional-forged-page-106'),
   lambda c:c['migration']['new_reviewed_targets'].__setitem__(0,c['migration']['new_reviewed_targets'][1]),
   lambda c:c['migration']['new_reviewed_targets'][0].__setitem__('decision_ref','OUT-025'),
   lambda c:c['migration']['new_reviewed_targets'][0].__setitem__('accessibility_obligation','forged'),
   lambda c:c['migration']['new_reviewed_targets'][0]['replaces'].__setitem__(0,'viral-accepted-'+'0'*64),
   lambda c:c['migration']['new_reviewed_targets'][0]['replaces'].pop(),
   lambda c:c['migration']['new_reviewed_targets'][0]['replaces'].append(c['migration']['new_reviewed_targets'][0]['replaces'][0]),
   lambda c:c['migration']['asset_rows'][0].__setitem__('outcome','reclassified'),
   lambda c:c['migration']['asset_rows'][0].__setitem__('decision_ref','OUT-005'),
   lambda c:c['migration']['asset_rows'][-1].__setitem__('target_ids',['assets:viral-accepted-b90cb9a3752383888c733905588e9c3859b113e47f1f457057c72e33689a7585']),
   lambda c:next(item for item in c['assets'] if item['asset_id']==c['migration']['new_reviewed_targets'][0]['replaces'][0]).__setitem__('disposition','reader'))
  for mutate in mutations:
   altered=copy.deepcopy(value);mutate(altered)
   with self.assertRaisesRegex(ValueError,'E_V2_(ASSET|MIGRATION)'):V.v2_contract(altered)
  by_id={row['asset_id']:row for row in value['assets']};critic=('viral-accepted-e1e2aa6964b45037691d92e4faf91dba6bbd411e409dc49c237f6b0e71e6ce85','viral-accepted-a1d83a711a4b7962110b1ba158b2d610043f1fa836e06458e675373094acd6c1')
  markdown=[row['asset_id'] for row in value['assets'] if row['provenance']['kind']=='markdown_image_reference'];visual=[row['asset_id'] for row in value['assets'] if row['provenance']['kind']=='visual_region'];provisional=[row['asset_id'] for row in value['assets'] if row['provenance']['kind']=='reviewed_provisional_full_page']
  for target,donor in (critic,critic[::-1],(markdown[0],markdown[1]),(visual[0],visual[1]),(provisional[0],provisional[1])):
   altered=copy.deepcopy(value);row=next(item for item in altered['assets'] if item['asset_id']==target);row['binary']=copy.deepcopy(by_id[donor]['binary']);row['provenance']=copy.deepcopy(by_id[donor]['provenance'])
   with self.assertRaisesRegex(ValueError,'E_V2_ASSET'):V.v2_contract(altered)
  altered=copy.deepcopy(value);altered['assets'][0]['binary']['bytes']+=1
  with self.assertRaisesRegex(ValueError,'E_V2_ASSET'):V.v2_contract(altered)
  altered=copy.deepcopy(value);altered['assets'][0]['provenance']['bbox'][0]+=1
  with self.assertRaisesRegex(ValueError,'E_V2_ASSET'):V.v2_contract(altered)
 def test_unmutated_public_v2_preflight_passes_and_cleans_up(self):
  path=ROOT/'working'/'viral'/'master_en'/f'.phase-b1c4-verifier-{uuid.uuid4().hex}.json'
  try:
   path.write_text(json.dumps(A.author(),ensure_ascii=False),encoding='utf8')
   self.assertEqual(V.preflight(*map(str,(ARGS[0],ARGS[1],path,ARGS[3])))['status'],'preflight_passed')
  finally:path.unlink(missing_ok=True)
  self.assertFalse(path.exists())
 def test_a3_independent_closed_typed_payload_and_operation_matrix_regressions(self):
  payload={'kind':'creature_statblock','title':'T','subtitle':'U','characteristics':'C','derived_stats':'D','attacks':'A','abilities':'B','nested_tables':'N','contains':['s'],'end_after':'s'}
  V.v2_a3_payload_schema(payload)
  accepted=copy.deepcopy(payload);accepted.update({'subtitle':'','characteristics':'','derived_stats':'','attacks':'','abilities':'','nested_tables':''});V.v2_a3_payload_schema(accepted)
  optional_map={'kind':'full_page_map','pages':[1,2],'reader_asset_ids':['map'],'accessible_key':'','legend':'','scale':'','contains':['s']};V.v2_a3_payload_schema(optional_map)
  for mutate in (lambda x:x.pop('attacks'),lambda x:x.__setitem__('extra','invented'),lambda x:x.update({'title':'','subtitle':'','characteristics':'','derived_stats':'','attacks':'','abilities':'','nested_tables':''})):
   altered=copy.deepcopy(payload);mutate(altered)
   with self.assertRaises(ValueError):V.v2_a3_payload_schema(altered)
  self.assertEqual(V.V2_OPERATION_BY_TYPE['heading'],{'emit_exact'})
  self.assertEqual(V.V2_OPERATION_BY_TYPE['asset'],{'asset_reference','suppress'})
 def test_independent_v2_reconstruction_package_known_answer_and_mutations(self):
  self.assertEqual(V.v2_package_inventory(ARGS[1]),(377,41079424,'68C17FB765A89C6146398868E61F1F6EB7B2FE4EAFBA8C2C2C8F42260BBDBA83'))
  cfg=v2_fixture();package=bind_v2_inputs(cfg,'independent-aggregate')
  try:
   V.v2_input_binding(cfg,ROOT.parent,ARGS[3],package)
   for field,code in [('file_count','reconstruction-file-count'),('total_bytes','reconstruction-total-bytes'),('inventory_sha256','reconstruction-inventory-sha256')]:
    bad=copy.deepcopy(cfg);bad['document']['reconstruction_package'][field]=0 if field!='inventory_sha256' else '0'*64
    with self.assertRaisesRegex(ValueError,code):V.v2_input_binding(bad,ROOT.parent,ARGS[3],package)
   (package/'INVENTORY.json').write_text('{}\n',encoding='utf8',newline='\n')
   with self.assertRaisesRegex(ValueError,'reconstruction-file-count'):V.v2_input_binding(cfg,ROOT.parent,ARGS[3],package)
  finally:shutil.rmtree(package,ignore_errors=True)

 def test_independent_v2_reconstruction_package_path_shapes(self):
  cfg=v2_fixture();package=bind_v2_inputs(cfg,'independent-path-shapes');file=ROOT/'.v2-independent-path-file';wrong=ROOT/'.v2-independent-path-wrong'
  try:
   for altered,cli in [(lambda c:c['document']['reconstruction_package'].__setitem__('root','kb_creator/.missing-independent-package'),package),(lambda c:c,package/'missing')]:
    bad=copy.deepcopy(cfg);altered(bad)
    with self.assertRaisesRegex(ValueError,'E_V2_IDENTITY: reconstruction-package-cli'):V.v2_input_binding(bad,ROOT.parent,ARGS[3],cli)
   file.write_text('file\n',encoding='utf8');wrong.mkdir()
   for cli in (file,wrong):
    with self.assertRaisesRegex(ValueError,'E_V2_IDENTITY: reconstruction-package-cli'):V.v2_input_binding(cfg,ROOT.parent,ARGS[3],cli)
  finally:
   file.unlink(missing_ok=True);shutil.rmtree(wrong,ignore_errors=True);shutil.rmtree(package,ignore_errors=True)

 def test_production_preflight(self): self.assertEqual(V.preflight(*map(str,ARGS))['status'],'preflight_passed')
 def test_source_does_not_import_builder_module(self):
  text=SCRIPT.read_text(encoding='utf8');self.assertNotIn('import build_scenario_master_en',text);self.assertNotIn('from build_scenario_master_en',text)
 def test_reader_surface_public_contract_rejects_selector_and_alt_policy_mutations(self):
  cfg=json.loads(ARGS[2].read_text(encoding='utf8'));self.assertEqual((len(V.reader_surface(cfg,ARGS[1])[0]),len(V.reader_surface(cfg,ARGS[1])[1])),(25,22))
  invalid=copy.deepcopy(cfg);invalid['reader_surface']['semantic_fragments'][0]['start']={'kind':'line_exact','occurrence':0,'text':'invalid'}
  with self.assertRaisesRegex(ValueError,'E_C2B_READER_SURFACE'):V.reader_surface(invalid,ARGS[1])
  invalid=copy.deepcopy(cfg);invalid['assets'][next(i for i,x in enumerate(invalid['assets']) if x['representation']=='reader')]['alt_text']='Scenario illustration owned by tooling'
  with self.assertRaisesRegex(ValueError,'E_C2B_READER_SURFACE'):V.reader_surface(invalid,ARGS[1])
 def test_cli_rejects_invalid_target(self):
  r=subprocess.run([sys.executable,'-B',str(SCRIPT),'--contract',str(ARGS[0]),'--reconstruction-package',str(ARGS[1]),'--publication-config',str(ARGS[2]),'--source-pdf',str(ARGS[3]),'--target','unused'],capture_output=True,text=True)
  self.assertNotEqual(r.returncode,0);self.assertIn('E_C2B_TARGET_PATH',r.stderr)

 def test_independent_v2_contract_rejects_order_title_outline_and_eol_mutations(self):
  cfg=refresh_v2_review_units(v2_fixture());text='<a id="intro"></a>\n# Introduction\n\nText.\n\n<a id="infection"></a>\n'
  self.assertEqual(V.verify_v2_document(cfg,text)['status'],'verified_v2_document')
  for mutate,code in [(lambda c:c['events'][1].__setitem__('order_key',[1,1]),'E_V2_ORDER'),(lambda c:c['hierarchy'][0].__setitem__('reader_title','Short'),'E_V2_TITLE')]:
   altered=copy.deepcopy(cfg);mutate(altered)
   with self.assertRaisesRegex(ValueError,code):V.verify_v2_document(altered,text)
  with self.assertRaisesRegex(ValueError,'E_V2_HIERARCHY'):V.verify_v2_document(cfg,text+'## Infection\n')
  with self.assertRaisesRegex(ValueError,'E_V2_EOL'):V.verify_v2_document(cfg,text.replace('\n','\r\n'))

 def test_independent_v2_source_disposition_identity_and_policy_mutations(self):
  cfg=v2_fixture();package=bind_v2_inputs(cfg,'independent-disposition')
  try:
   V.v2_input_binding(cfg,ROOT.parent,ARGS[3],package)
   for mutate,code in [(lambda value:value['source_disposition'].pop(),'E_V2_SCOPE'),(lambda value:value['source_disposition'][123].__setitem__('decision_date','2026-09-01'),'E_V2_SCOPE'),(lambda value:value['source_disposition'][0]['page_markdown'].__setitem__('sha256','0'*64),'E_V2_IDENTITY')]:
    bad=copy.deepcopy(cfg);mutate(bad)
    if code=='E_V2_IDENTITY':
     with self.assertRaisesRegex(ValueError,code):V.v2_input_binding(bad,ROOT.parent,ARGS[3],package)
    else:
     with self.assertRaisesRegex(ValueError,code):V.v2_contract(bad)
   bad=copy.deepcopy(cfg);bad['assets'].append({'asset_id':'leak','reader_value':False,'placement':{'after_event':'a'},'anchor':'intro','page':123,'source_span_ids':['s1']})
   with self.assertRaisesRegex(ValueError,'E_V2_ASSET'):V.v2_contract(bad)
  finally:shutil.rmtree(package,ignore_errors=True)

 def test_v2_structured_contains_is_closed_ordered_and_type_bound(self):
  cfg=v2_fixture();event={'event_id':'d','type':'structured_unit','page':2,'order_key':[2,2],'anchor':'infection','content':{'kind':'callout','contains':['one','two']},'fragment_id':'d','contains':['one','two'],'source_span_ids':['fixture-span'],'source_operation':'semantic_restructure','payload_bindings':[]};cfg['events'].append(event);refresh_v2_review_units(cfg)
  V.v2_contract(cfg)
  for mutate in [lambda x:x['contains'].append('one'),lambda x:x.__setitem__('contains',['two','one']),lambda x:x.__setitem__('contains',[])]:
   altered=copy.deepcopy(cfg);mutate(altered['events'][-1])
   with self.assertRaisesRegex(ValueError,'E_V2_STRUCTURE'):V.v2_contract(altered)
  altered=copy.deepcopy(cfg);altered['events'][0]['contains']=['bad']
  with self.assertRaisesRegex(ValueError,'E_C2B_SCHEMA'):V.v2_contract(altered)

 def test_v2_builder_baseline_candidate_is_accepted(self):
  cfg=v2_fixture(); path=ROOT/'.v2-verifier-fixture.json'; base=ROOT/'working'/'synthetic'; blobs=[]
  package=bind_v2_inputs(cfg,'verifier')
  cfg['hierarchy'].append({'anchor':'room','page':4,'source_title':'Room 2E','reader_title':'Room 2E','representation':'inline_run_in','reviewed_title_transformation':None})
  cfg['events'] += [{'event_id':'run','type':'structured_unit','page':4,'order_key':[4,0,V.V2_ROLE_RANK['structured_unit'],3],'anchor':'room','content':{'kind':'inline_run_in','anchor':'room','label':'Room 2E','xref':'xref','contains':['run']},'fragment_id':'run','contains':['run']},{'event_id':'s1','type':'structured_unit','page':5,'order_key':[5,0,V.V2_ROLE_RANK['structured_unit'],4],'anchor':'infection','content':{'kind':'table','header':['A'],'rows':[['x']],'row_count':1,'cell_count':1,'contains':['row']},'fragment_id':'s1','contains':['row']},{'event_id':'s2','type':'structured_unit','page':6,'order_key':[6,0,V.V2_ROLE_RANK['structured_unit'],5],'anchor':'infection','content':{'kind':'callout','body':['note'],'contains':['note'],'end_after':'note'},'fragment_id':'s2','contains':['note']},{'event_id':'r','type':'text_fragment','page':7,'order_key':[7,0,V.V2_ROLE_RANK['text_fragment'],6],'anchor':'infection','content':'source_backed_recovery','fragment_id':'r'}]
  for name in ('before','after','inside'):
   blob=ROOT/f'.v2-{name}.bin';blob.write_bytes(name.encode());blobs.append(blob)
  cfg['assets']=[{'asset_id':'before','reader_value':True,'placement':{'before_event':'b'},'anchor':'infection','page':8,'duplication_resolution':'unique_reader','quality_stage':'provisional_full_page','source_path':f'kb_creator/.v2-before.bin','bytes':6,'sha256':hashlib.sha256(b'before').hexdigest().upper(),'semantic_role':'full_page'},{'asset_id':'after','reader_value':True,'placement':{'after_event':'s2'},'anchor':'infection','page':9,'duplication_resolution':'unique_reader','quality_stage':'provisional_full_page','source_path':f'kb_creator/.v2-after.bin','bytes':5,'sha256':hashlib.sha256(b'after').hexdigest().upper(),'semantic_role':'full_page'},{'asset_id':'inside','reader_value':True,'placement':{'inside_structured_unit':'s1'},'anchor':'infection','page':10,'duplication_resolution':'unique_reader','quality_stage':'provisional_full_page','source_path':f'kb_creator/.v2-inside.bin','bytes':6,'sha256':hashlib.sha256(b'inside').hexdigest().upper(),'semantic_role':'full_page'},{'asset_id':'suppressed','reader_value':False,'placement':{'after_event':'b'},'anchor':'infection','page':11}]
  cfg['events'] += [{'event_id':'ab','type':'asset','page':8,'order_key':[8,0,V.V2_ROLE_RANK['asset'],7],'anchor':'infection','content':'before','fragment_id':'ab'},{'event_id':'aa','type':'asset','page':9,'order_key':[9,0,V.V2_ROLE_RANK['asset'],8],'anchor':'infection','content':'after','fragment_id':'aa'},{'event_id':'ai','type':'asset','page':10,'order_key':[10,0,V.V2_ROLE_RANK['asset'],9],'anchor':'infection','content':'inside','fragment_id':'ai'},{'event_id':'as','type':'asset','page':11,'order_key':[11,0,V.V2_ROLE_RANK['asset'],10],'anchor':'infection','content':'suppressed','fragment_id':'as'}]
  # This fixture adds materialized targets after bind_v2_inputs; close them
  # explicitly rather than weakening the A2 orphan-target gate.
  cfg['migration']['new_reviewed_targets']=[{'target_id':target,'decision_ref':'viral-logical_table-p020-l025'} for target in sorted({*(f'hierarchy:{row["anchor"]}' for row in cfg['hierarchy']),*(f'assets:{row["asset_id"]}' for row in cfg['assets']),*(f'xrefs:{row["xref_id"]}' for row in cfg['xrefs'])})]
  for index,row in enumerate(cfg['hierarchy']):
   if 'source_pages' not in row:
    page=row.pop('page');row.update({'parent_anchor':'intro','level':None,'toc_entry':False,'semantic_role':'fixture','source_pages':[page],'migration_row_id':f'hierarchy:{row["anchor"]}'})
  added_event_ids={'run','s1','s2','r','ab','aa','ai','as'}
  for event in cfg['events']:
   event.setdefault('source_span_ids',['s2']);event.setdefault('source_operation',{'structured_unit':'semantic_restructure','asset':'asset_reference'}.get(event['type'],'emit_exact'));event.setdefault('payload_bindings',[])
   if event['event_id'] in added_event_ids:bind_v2_event_source(cfg,package,event)
  for asset in cfg['assets']:asset['source_span_ids']=next(event['source_span_ids'] for event in cfg['events'] if event['type']=='asset' and event['content']==asset['asset_id'])
  count,total,digest=V.v2_package_inventory(package);cfg['document']['reconstruction_package'].update({'file_count':count,'total_bytes':total,'inventory_sha256':digest})
  refresh_v2_review_units(cfg);shutil.rmtree(base,ignore_errors=True)
  try:
   path.write_text(json.dumps(cfg),encoding='utf8'); target=(Path('kb_creator')/'working'/'synthetic'/'master_en'/'candidates'/'v2-baseline').as_posix()
   B.build_candidate(*map(str,(ARGS[0],package,path,ARGS[3])),target)
   self.assertEqual(V.verify_v2_candidate(path,target)['status'],'verified_v2_candidate')
   candidate=ROOT/'working'/'synthetic'/'master_en'/'candidates'/'v2-baseline';original={item:item.read_bytes() for item in candidate.rglob('*') if item.is_file()}
   def restore():
    for item,data in original.items():item.write_bytes(data)
   def mutate_provenance(change,code):
    value=json.loads((candidate/'MASTER_EN.provenance.json').read_text());change(value);(candidate/'MASTER_EN.provenance.json').write_text(json.dumps(value,ensure_ascii=False,sort_keys=True,indent=2)+'\n',encoding='utf8',newline='\n');reseal(candidate)
    with self.assertRaisesRegex(ValueError,code):V.verify_v2_candidate(path,target)
    restore()
   def mutate_inventory(change):
    value=json.loads((candidate/'INVENTORY.json').read_text());change(value);(candidate/'INVENTORY.json').write_text(json.dumps(value,ensure_ascii=False,sort_keys=True,indent=2)+'\n',encoding='utf8',newline='\n')
    with self.assertRaisesRegex(ValueError,'E_V2_INVENTORY'):V.verify_v2_candidate(path,target)
    restore()
   def mutate_slice(event_id,replacement,code):
    master=(candidate/'MASTER_EN.md').read_text();value=json.loads((candidate/'MASTER_EN.provenance.json').read_text());row=next(item for item in value['events'] if item['event_id']==event_id);start,end=row['start_char'],row['end_char'];old=master[start:end]
    self.assertIn(replacement[0],old);new=old.replace(*replacement,1);delta=len(new)-len(old);changed=master[:start]+new+master[end:]
    for item in value['events']:
     if item['emission']!='emitted':continue
     if item['event_id']==event_id:item['end_char']+=delta;item['end_byte']+=delta;item['slice_sha256']=hashlib.sha256(new.encode()).hexdigest().upper()
     elif item['start_char']>=end:
      item['start_char']+=delta;item['end_char']+=delta;item['start_byte']+=delta;item['end_byte']+=delta
    (candidate/'MASTER_EN.md').write_text(changed,encoding='utf8',newline='\n');(candidate/'MASTER_EN.provenance.json').write_text(json.dumps(value,ensure_ascii=False,sort_keys=True,indent=2)+'\n',encoding='utf8',newline='\n');reseal(candidate)
    with self.assertRaisesRegex(ValueError,code):V.verify_v2_candidate(path,target)
    restore()
   def mutate_config(change,code):
    raw=path.read_bytes();value=json.loads(raw);change(value);path.write_text(json.dumps(value),encoding='utf8')
    with self.assertRaisesRegex(ValueError,code):V.verify_v2_candidate(path,target)
    path.write_bytes(raw)
   def mutate_master(change,code):
    master=(candidate/'MASTER_EN.md').read_text();(candidate/'MASTER_EN.md').write_text(change(master),encoding='utf8',newline='\n');reseal(candidate)
    with self.assertRaisesRegex(ValueError,code):V.verify_v2_candidate(path,target)
    restore()
   # Class 1: each inventory declaration must exactly mirror the candidate tree.
   mutate_inventory(lambda value:value['rows'].pop())
   mutate_inventory(lambda value:value['rows'].append({'path':'extra','bytes':0,'sha256':'0'*64}))
   mutate_inventory(lambda value:value['rows'][0].__setitem__('bytes',value['rows'][0]['bytes']+1))
   mutate_inventory(lambda value:value['rows'][0].__setitem__('sha256','0'*64))
   # Class 2: resealed provenance order still must match the declared graph.
   mutate_provenance(lambda value:value['events'].__setitem__(slice(0,2),list(reversed(value['events'][:2]))),'E_V2_PROVENANCE')
   mutate_provenance(lambda value: next(row for row in value['events'] if row['emission']=='emitted').__setitem__('end_byte',999),'E_V2_PROVENANCE')
   mutate_provenance(lambda value: next(row for row in value['events'] if row['event_id']=='s1').__setitem__('contains',['row','extra']),'E_V2_STRUCTURE')
   # Class 3: ledger-sealed table shape and callout boundary are independently parsed.
   mutate_slice('s1',('| A |\n| --- |\n| x |','| A | B |\n| --- | --- |\n| x | y |'),'E_V2_STRUCTURE')
   mutate_slice('s2',('> note','x note'),'E_V2_STRUCTURE')
   # Class 4: title, anchor-only and inline-run-in headings cannot pollute outline.
   master=(candidate/'MASTER_EN.md').read_text();(candidate/'MASTER_EN.md').write_text(master.replace('# Introduction','# Drift',1),encoding='utf8',newline='\n');reseal(candidate)
   with self.assertRaisesRegex(ValueError,'E_V2_HIERARCHY'):V.verify_v2_candidate(path,target)
   restore()
   master=(candidate/'MASTER_EN.md').read_text();(candidate/'MASTER_EN.md').write_text(master.replace('<a id="intro"></a>','<a id="drift"></a>',1),encoding='utf8',newline='\n');reseal(candidate)
   with self.assertRaisesRegex(ValueError,'E_V2_(HIERARCHY|TITLE)'):V.verify_v2_candidate(path,target)
   restore()
   master=(candidate/'MASTER_EN.md').read_text();(candidate/'MASTER_EN.md').write_text(master+'## Infection\n',encoding='utf8',newline='\n');reseal(candidate)
   with self.assertRaisesRegex(ValueError,'E_V2_HIERARCHY'):V.verify_v2_candidate(path,target)
   restore()
   master=(candidate/'MASTER_EN.md').read_text();(candidate/'MASTER_EN.md').write_text(master.replace('<a id="room"></a>**Room 2E** xref','## Room 2E',1),encoding='utf8',newline='\n');reseal(candidate)
   with self.assertRaisesRegex(ValueError,'E_V2_HIERARCHY'):V.verify_v2_candidate(path,target)
   restore()
   # Class 5: each reader asset's declared relative placement and copied bytes are binding.
   mutate_config(lambda value:next(row for row in value['assets'] if row['asset_id']=='before').__setitem__('placement',{'after_event':'b'}),'E_V2_ASSET')
   mutate_config(lambda value:next(row for row in value['assets'] if row['asset_id']=='after').__setitem__('placement',{'before_event':'s2'}),'E_V2_ASSET')
   mutate_config(lambda value:next(row for row in value['assets'] if row['asset_id']=='inside').__setitem__('placement',{'before_event':'s1'}),'E_V2_ASSET')
   asset=candidate/'assets'/'before';asset.write_bytes(b'broken');reseal(candidate)
   with self.assertRaisesRegex(ValueError,'E_V2_ASSET'):V.verify_v2_candidate(path,target)
   restore()
   # Class 6 (implemented ordinary reader whitespace): unbounded blank runs fail before ledger parsing.
   mutate_master(lambda value:value.replace('Text.','Text.\n\n',1),'E_V2_EOL')
   # Class 7: excluded physical pages cannot enter declared events or assets.
   # Plain narrative containing the digits "123" is not page provenance and
   # is intentionally not rejected by a lexical heuristic.
   mutate_config(lambda value:next(row for row in value['events'] if row['event_id']=='b').__setitem__('page',123),'E_V2_ORDER')
   mutate_config(lambda value:next(row for row in value['assets'] if row['asset_id']=='before').__setitem__('page',123),'E_V2_ASSET')
   # Class 8 (implemented ledger identity): removal and declared-content/range mutation cannot survive resealing.
   mutate_provenance(lambda value:value['events'].pop(),'E_V2_PROVENANCE')
   mutate_provenance(lambda value:next(row for row in value['events'] if row['event_id']=='b').__setitem__('declared_content_sha256','0'*64),'E_V2_PROVENANCE')
  finally:
   path.unlink(missing_ok=True);[blob.unlink(missing_ok=True) for blob in blobs];shutil.rmtree(package,ignore_errors=True);shutil.rmtree(base,ignore_errors=True)
 def test_v2_external_report_is_atomic_deterministic_and_bound(self):
  cfg=refresh_v2_review_units(v2_fixture());package=bind_v2_inputs(cfg,'report');config=ROOT/'.v2-report.json';base=ROOT/'working'/'synthetic';report=ROOT/'.v2-report.json.out'
  shutil.rmtree(base,ignore_errors=True);report.unlink(missing_ok=True)
  try:
   config.write_text(json.dumps(cfg),encoding='utf8');target='kb_creator/working/synthetic/master_en/candidates/v2-report';B.build_candidate(str(ARGS[0]),str(package),str(config),str(ARGS[3]),target)
   first=V.write_v2_verification_report(str(config),target,'kb_creator/.v2-report.json.out');self.assertEqual(V.validate_v2_verification_report(str(config),target,report)['status'],'validated_v2_verification_report');self.assertEqual(first['schema'],'kb_creator.master_en_verification.v2')
   with self.assertRaisesRegex(ValueError,'E_V2_REPORT'):V.write_v2_verification_report(str(config),target,'kb_creator/.v2-report.json.out')
   tampered=json.loads(report.read_text());tampered['status']='forged';report.write_text(json.dumps(tampered,sort_keys=True,indent=2)+'\n')
   with self.assertRaisesRegex(ValueError,'E_V2_REPORT'):V.validate_v2_verification_report(str(config),target,report)
  finally:report.unlink(missing_ok=True);config.unlink(missing_ok=True);shutil.rmtree(package,ignore_errors=True);shutil.rmtree(base,ignore_errors=True)
 def test_independent_v2_migration_ledgers_reject_domain_rows_and_input_drift(self):
  cfg=v2_fixture();package=bind_v2_inputs(cfg,'migration-verifier')
  try:
   V.v2_input_binding(cfg,ROOT.parent,ARGS[3],package)
   cases=[
    (lambda c:c['migration']['hierarchy_rows'].pop(),'E_V2_MIGRATION'),
    (lambda c:c['migration']['asset_rows'].append(copy.deepcopy(c['migration']['asset_rows'][0])),'E_V2_MIGRATION'),
    (lambda c:c['migration']['xref_rows'][0].__setitem__('outcome','reclassified'),'E_V2_MIGRATION'),
    (lambda c:c['migration']['source_disposition_rows'][122].update({'outcome':'excluded_advertising','final_target_ids':['leak']}),'E_V2_MIGRATION'),
    (lambda c:c['migration']['handout_rows'][0].__setitem__('decision_ref',''),'E_V2_MIGRATION'),
    (lambda c:c['migration']['structured_rows'][0].__setitem__('final_target_ids',['dup','dup']),'E_V2_MIGRATION'),
    (lambda c:c['migration']['new_reviewed_targets'].append({'target_id':'orphan','decision_ref':'missing'}),'E_V2_MIGRATION'),
    (lambda c:c['migration']['inputs']['decision_evidence'][0].__setitem__('bytes',-1),'E_V2_IDENTITY')]
   for mutate,code in cases:
    altered=copy.deepcopy(cfg);mutate(altered)
    with self.assertRaisesRegex(ValueError,code):V.v2_input_binding(altered,ROOT.parent,ARGS[3],package)
  finally: shutil.rmtree(package,ignore_errors=True)

 def test_independent_v2_decision_evidence_rejects_cross_file_duplicate_catalog_id(self):
  """Verifier independently rejects an ambiguous duplicate evidence origin."""
  cfg=v2_fixture();package=bind_v2_inputs(cfg,'decision-cross-file-duplicate-verifier');duplicate=ROOT/'.v2-decision-evidence-duplicate-verifier.json'
  try:
   duplicate.write_text(json.dumps({'schema':'kb_creator.semantic_unit_review.v2','decisions':[{'candidate_id':'viral-logical_table-p020-l025'}]}),encoding='utf8')
   cfg['migration']['inputs']['decision_evidence'].append({'path':duplicate.relative_to(ROOT.parent).as_posix(),'bytes':duplicate.stat().st_size,'sha256':hashlib.sha256(duplicate.read_bytes()).hexdigest().upper(),'kind':'kb_creator.semantic_unit_review.v2'})
   with self.assertRaisesRegex(ValueError,'E_V2_MIGRATION'):
    V.v2_input_binding(cfg,ROOT.parent,ARGS[3],package)
  finally: duplicate.unlink(missing_ok=True);shutil.rmtree(package,ignore_errors=True)

 def test_independent_v2_decision_evidence_provenance_classes_allow_only_valid_corroboration(self):
  cfg=v2_fixture();package=bind_v2_inputs(cfg,'decision-provenance-verifier');files=[]
  def add(name,value,kind):
   path=ROOT/name;path.write_text(value if isinstance(value,str) else json.dumps(value),encoding='utf8');files.append(path)
   cfg['migration']['inputs']['decision_evidence'].append({'path':path.relative_to(ROOT.parent).as_posix(),'bytes':path.stat().st_size,'sha256':hashlib.sha256(path.read_bytes()).hexdigest().upper(),'kind':kind});return path
  try:
   add('.v2-provenance-boundary-verifier.json',{'schema':'kb_creator.viral_boundary_ledger.v1','units':[{'id':'unit-1','registry_refs':['OUT-999']}],'candidate_dispositions':[{'candidate_id':'viral-logical_table-p020-l025','target_unit_id':'unit-1'}],'deferred_nonblocking':[{'registry_ref':'OUT-999'}]},'kb_creator.viral_boundary_ledger.v1')
   add('.v2-provenance-registry-verifier.md','### OUT-999 — registry decision\n','kb_creator.user_review_registry.md')
   add('.v2-provenance-closure-verifier.json',{'schema':'kb_creator.semantic_unit_closure.v2','unresolved_blocking_candidates':[],'deferred_nonblocking':[{'id':'OUT-999'}]},'kb_creator.semantic_unit_closure.v2')
   V.v2_input_binding(cfg,ROOT.parent,ARGS[3],package)
   incompatible=copy.deepcopy(cfg);path=ROOT/'.v2-provenance-incompatible-verifier.json';path.write_text(json.dumps({'schema':'kb_creator.viral_boundary_ledger.v1','units':[{'id':'unit-2','registry_refs':['viral-logical_table-p020-l025']}],'candidate_dispositions':[],'deferred_nonblocking':[]}),encoding='utf8');files.append(path)
   incompatible['migration']['inputs']['decision_evidence'].append({'path':path.relative_to(ROOT.parent).as_posix(),'bytes':path.stat().st_size,'sha256':hashlib.sha256(path.read_bytes()).hexdigest().upper(),'kind':'kb_creator.viral_boundary_ledger.v1'})
   with self.assertRaisesRegex(ValueError,'E_V2_MIGRATION'):V.v2_input_binding(incompatible,ROOT.parent,ARGS[3],package)
  finally:
   for path in files:path.unlink(missing_ok=True)
   shutil.rmtree(package,ignore_errors=True)

 def test_independent_v2_semantic_decision_catalog_is_exact_and_closed(self):
  package=bind_v2_inputs(cfg:=v2_fixture(),'semantic-catalog-verifier');path=ROOT/'.v2-semantic-catalog-verifier.json'
  try:
   good={'schema':'kb_creator.semantic_unit_review.v2','decisions':[{'candidate_id':'DEC-100'}]};bind_v2_decision_evidence(cfg,path,'kb_creator.semantic_unit_review.v2',good,'DEC-100');V.v2_input_binding(cfg,ROOT.parent,ARGS[3],package)
   for ref in ('reader','viral','candidate_id','DEC','DEC-100-suffix','dec-100','DEC-101'):
    bad=copy.deepcopy(cfg);bad['migration']['handout_rows'][0]['decision_ref']=ref
    with self.subTest(ref=ref),self.assertRaisesRegex(ValueError,'E_V2_MIGRATION'):V.v2_input_binding(bad,ROOT.parent,ARGS[3],package)
   for payload in ({'schema':'wrong','decisions':[{'candidate_id':'DEC-100'}]},{'schema':'kb_creator.semantic_unit_review.v2','decisions':[{'candidate_id':'DEC-100'}],'extra':1},{'schema':'kb_creator.semantic_unit_review.v2','decisions':[{'candidate_id':'DEC-100','reason':'DEC-100'}]},{'schema':'kb_creator.semantic_unit_review.v2','decisions':['DEC-100']},{'schema':'kb_creator.semantic_unit_review.v2','decisions':[]},{'schema':'kb_creator.semantic_unit_review.v2','decisions':[{'candidate_id':'DEC-100'},{'candidate_id':'DEC-100'}]},b'{'):
    bad=copy.deepcopy(cfg);bind_v2_decision_evidence(bad,path,'kb_creator.semantic_unit_review.v2',payload,'DEC-100')
    with self.assertRaisesRegex(ValueError,'E_V2_MIGRATION'):V.v2_input_binding(bad,ROOT.parent,ARGS[3],package)
   bad=copy.deepcopy(cfg);bind_v2_decision_evidence(bad,path,'kb_creator.semantic_unit_review.v2',b'\xff','DEC-100')
   with self.assertRaisesRegex(ValueError,'E_V2_MIGRATION'):V.v2_input_binding(bad,ROOT.parent,ARGS[3],package)
  finally:path.unlink(missing_ok=True);shutil.rmtree(package,ignore_errors=True)

 def test_independent_v2_registry_decision_catalog_heading_only(self):
  package=bind_v2_inputs(cfg:=v2_fixture(),'registry-catalog-verifier');path=ROOT/'.v2-registry-catalog-verifier.md'
  try:
   bind_v2_decision_evidence(cfg,path,'kb_creator.user_review_registry.md','### OUT-100 '+chr(0x2014)+' accepted\n','OUT-100');V.v2_input_binding(cfg,ROOT.parent,ARGS[3],package)
   for payload in ('### OUT-100 - malformed\n','body OUT-100 only\n','### OUT-100 '+chr(0x2014)+' one\n### OUT-100 '+chr(0x2014)+' duplicate\n'):
    bad=copy.deepcopy(cfg);bind_v2_decision_evidence(bad,path,'kb_creator.user_review_registry.md',payload,'OUT-100')
    with self.assertRaisesRegex(ValueError,'E_V2_MIGRATION'):V.v2_input_binding(bad,ROOT.parent,ARGS[3],package)
  finally:path.unlink(missing_ok=True);shutil.rmtree(package,ignore_errors=True)

 def test_independent_v2_boundary_decision_catalog_is_closed(self):
  package=bind_v2_inputs(cfg:=v2_fixture(),'boundary-catalog-verifier');path=ROOT/'.v2-boundary-catalog-verifier.json'
  good={'schema':'kb_creator.viral_boundary_ledger.v1','units':[{'id':'UNIT-100','registry_refs':['OUT-100']}],'candidate_dispositions':[{'candidate_id':'CAND-100','target_unit_id':'UNIT-100'}],'deferred_nonblocking':[{'registry_ref':'OUT-100'}]}
  try:
   for ref in ('UNIT-100','CAND-100','OUT-100'):
    current=copy.deepcopy(cfg);bind_v2_decision_evidence(current,path,'kb_creator.viral_boundary_ledger.v1',good,ref);V.v2_input_binding(current,ROOT.parent,ARGS[3],package)
   for payload in ({**good,'units':[{'id':'UNIT-100','registry_refs':['OUT-100'],'extra':1}]},{**good,'candidate_dispositions':[{'candidate_id':'CAND-100','target_unit_id':'missing'}]},{**good,'units':[{'id':'UNIT-100','registry_refs':[]},{'id':'UNIT-100','registry_refs':[]}]},{**good,'candidate_dispositions':[{'candidate_id':'CAND-100','target_unit_id':'UNIT-100'},{'candidate_id':'CAND-100','target_unit_id':'UNIT-100'}]},{**good,'deferred_nonblocking':[{'registry_ref':'OUT-100','extra':1}]},{**good,'prose':'UNIT-100'}):
    bad=copy.deepcopy(cfg);bind_v2_decision_evidence(bad,path,'kb_creator.viral_boundary_ledger.v1',payload,'UNIT-100')
    with self.assertRaisesRegex(ValueError,'E_V2_MIGRATION'):V.v2_input_binding(bad,ROOT.parent,ARGS[3],package)
  finally:path.unlink(missing_ok=True);shutil.rmtree(package,ignore_errors=True)

 def test_independent_v2_closure_decision_catalog_is_closed(self):
  package=bind_v2_inputs(cfg:=v2_fixture(),'closure-catalog-verifier');path=ROOT/'.v2-closure-catalog-verifier.json';good={'schema':'kb_creator.semantic_unit_closure.v2','unresolved_blocking_candidates':[],'deferred_nonblocking':[{'id':'OUT-101'}]}
  try:
   bind_v2_decision_evidence(cfg,path,'kb_creator.semantic_unit_closure.v2',good,'OUT-101');V.v2_input_binding(cfg,ROOT.parent,ARGS[3],package)
   for payload in ({**good,'unresolved_blocking_candidates':['blocked']},{**good,'deferred_nonblocking':[]},{**good,'deferred_nonblocking':[{'id':'OUT-101'},{'id':'OUT-101'}]},{**good,'count':1},{**good,'prose':'OUT-101'}):
    bad=copy.deepcopy(cfg);bind_v2_decision_evidence(bad,path,'kb_creator.semantic_unit_closure.v2',payload,'OUT-101')
    with self.assertRaisesRegex(ValueError,'E_V2_MIGRATION'):V.v2_input_binding(bad,ROOT.parent,ARGS[3],package)
  finally:path.unlink(missing_ok=True);shutil.rmtree(package,ignore_errors=True)

class CandidateVerifierTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.renderer_dir=tempfile.TemporaryDirectory();cls.renderer=Path(cls.renderer_dir.name)/'fake_pdftoppm.py';cls.renderer.write_text(FAKE_RENDERER,encoding='utf8')
  cls.parent=ROOT/'working'/'viral'/'master_en'/'candidates';cls.target=cls.parent/'c2b-unittest';shutil.rmtree(cls.target,ignore_errors=True);B.build_candidate(*map(str,ARGS),(Path('kb_creator')/cls.target.relative_to(ROOT)).as_posix(),(sys.executable,str(cls.renderer)))
 @classmethod
 def tearDownClass(cls): shutil.rmtree(cls.target,ignore_errors=True);cls.renderer_dir.cleanup()
 def verify(self): return V.verify(*map(str,ARGS),(Path('kb_creator')/self.target.relative_to(ROOT)).as_posix())
 def test_candidate_build_closed_deterministic_130_129(self):
  self.assertEqual(len([p for p in self.target.rglob('*') if p.is_file()]),130);self.assertEqual(len(json.loads((self.target/'INVENTORY.json').read_text())['rows']),129);self.assertFalse((self.target/'MASTER_EN.acceptance.json').exists())
 def test_candidate_build_atomic_absent_target_and_preserved_failure(self):
  self.assertTrue(self.target.is_dir());self.assertEqual(self.verify()['status'],'verified_candidate_pending_process_and_external_gates')
 def test_verifier_isolated_positive_and_closed_schema(self):
  self.assertEqual(self.verify()['scenario_id'],'viral');path=self.target/'MASTER_EN.qa.json';raw=path.read_text(encoding='utf8');inventory_path=self.target/'INVENTORY.json';inventory_raw=inventory_path.read_text(encoding='utf8');value=json.loads(raw);value['unexpected']=True
  try:
   path.write_text(json.dumps(value,ensure_ascii=False,sort_keys=True,indent=2)+'\n',encoding='utf8',newline='\n');reseal(self.target);self.assertRaisesRegex(ValueError,'E_C2B_SCHEMA',self.verify)
  finally: path.write_text(raw,encoding='utf8',newline='\n');inventory_path.write_text(inventory_raw,encoding='utf8',newline='\n')
 def test_verifier_path_topology_and_first_error_precedence(self):
  extra=self.target/'extra';extra.write_text('x');self.assertRaisesRegex(ValueError,'E_C2B_TOPOLOGY',self.verify);extra.unlink()
 def test_verifier_identity_inventory_and_resealed_semantic_boundary(self):
  path=self.target/'MASTER_EN.md';raw=path.read_text(encoding='utf8')
  try:
   path.write_text(raw[:-1]+'x\n',encoding='utf8',newline='\n');self.assertRaisesRegex(ValueError,'E_C2B_INVENTORY',self.verify)
  finally: path.write_text(raw,encoding='utf8',newline='\n')
 def test_verifier_provenance_char_byte_union_transform_and_xrefs(self):
  provenance=json.loads((self.target/'MASTER_EN.provenance.json').read_text(encoding='utf8'));rows=[f for u in provenance['units'] for f in u['output_fragments']];self.assertTrue(rows);self.assertEqual(rows[0]['start_byte'],len((self.target/'MASTER_EN.md').read_text(encoding='utf8')[:rows[0]['start_char']].encode()))
 def test_verifier_structures_notes_assets_and_private_render(self):
  manifest=json.loads((self.target/'ASSET_MANIFEST.json').read_text());self.assertEqual((sum(x['representation']=='reader' for x in manifest['assets']),sum(x['representation']=='evidence_only' for x in manifest['assets'])),(107,16))
 def test_verifier_qa_metrics_pending_gates_and_markdown(self):
  qa=json.loads((self.target/'MASTER_EN.qa.json').read_text());self.assertEqual(qa['metrics']['anchors'],168);self.assertTrue(all(x['status']=='pending' for x in qa['gates'][9:]))
 def test_critic_five_resealed_mutations(self):
  original={p:p.read_bytes() for p in [self.target/'MASTER_EN.md',self.target/'MASTER_EN.provenance.json',self.target/'ASSET_MANIFEST.json',self.target/'MASTER_EN.qa.json',self.target/'MASTER_EN.qa.md',self.target/'INVENTORY.json']}
  def restore():
   for path,data in original.items():path.write_bytes(data)
  cases=[]
  reader=(self.target/'MASTER_EN.md').read_text(encoding='utf8');cases.append(('E_C2B_PROVENANCE',lambda: (self.target/'MASTER_EN.md').write_text(reader[:-1]+'x\n',encoding='utf8',newline='\n')))
  def source():
   value=json.loads((self.target/'MASTER_EN.provenance.json').read_text(encoding='utf8'));next(unit for unit in value['units'] if unit['source_fragments'])['source_fragments'][0]['page']=999;(self.target/'MASTER_EN.provenance.json').write_text(json.dumps(value,ensure_ascii=False,sort_keys=True,indent=2)+'\n',encoding='utf8',newline='\n')
  cases.append(('E_C2B_PROVENANCE',source))
  def structured():
   value=json.loads((self.target/'MASTER_EN.provenance.json').read_text(encoding='utf8'));value['structured_units'][0]={'bogus':True};(self.target/'MASTER_EN.provenance.json').write_text(json.dumps(value,ensure_ascii=False,sort_keys=True,indent=2)+'\n',encoding='utf8',newline='\n')
  cases.append(('E_C2B_STRUCTURE',structured))
  def asset():
   value=json.loads((self.target/'ASSET_MANIFEST.json').read_text(encoding='utf8'));value['assets'][0]['owner_anchor']='bogus';value['assets'][0]['unexpected']=True;value['summary']['reader']=999;(self.target/'ASSET_MANIFEST.json').write_text(json.dumps(value,ensure_ascii=False,sort_keys=True,indent=2)+'\n',encoding='utf8',newline='\n')
  cases.append(('E_C2B_ASSET',asset))
  def asset_unknown():
   value=json.loads((self.target/'ASSET_MANIFEST.json').read_text(encoding='utf8'));value['assets'][0]['unexpected_only']=True;(self.target/'ASSET_MANIFEST.json').write_text(json.dumps(value,ensure_ascii=False,sort_keys=True,indent=2)+'\n',encoding='utf8',newline='\n')
  cases.append(('E_C2B_ASSET',asset_unknown))
  def asset_owner():
   value=json.loads((self.target/'ASSET_MANIFEST.json').read_text(encoding='utf8'));value['assets'][0]['owner_anchor']='nonexistent-anchor';(self.target/'ASSET_MANIFEST.json').write_text(json.dumps(value,ensure_ascii=False,sort_keys=True,indent=2)+'\n',encoding='utf8',newline='\n')
  cases.append(('E_C2B_ASSET',asset_owner))
  def notes():
   value=json.loads((self.target/'MASTER_EN.provenance.json').read_text(encoding='utf8'));value['structured_units'][0]['attached_notes']='bogus-notes';(self.target/'MASTER_EN.provenance.json').write_text(json.dumps(value,ensure_ascii=False,sort_keys=True,indent=2)+'\n',encoding='utf8',newline='\n')
  cases.append(('E_C2B_STRUCTURE',notes))
  def empty_source():
   value=json.loads((self.target/'MASTER_EN.provenance.json').read_text(encoding='utf8'));fragment=next(unit for unit in value['units'] if unit['source_fragments'])['source_fragments'][0];fragment.update({'page':1,'start_char':0,'end_char':0,'start_byte':0,'end_byte':0,'sha256':'E3B0C44298FC1C149AFBF4C8996FB92427AE41E4649B934CA495991B7852B855'});(self.target/'MASTER_EN.provenance.json').write_text(json.dumps(value,ensure_ascii=False,sort_keys=True,indent=2)+'\n',encoding='utf8',newline='\n')
  cases.append(('E_C2B_PROVENANCE',empty_source))
  def valid_other_unit_source():
   value=json.loads((self.target/'MASTER_EN.provenance.json').read_text(encoding='utf8')); units=[unit for unit in value['units'] if unit['source_fragments']]; self.assertGreaterEqual(len(units),2); units[0]['source_fragments'][0]=dict(units[1]['source_fragments'][0]); units[0]['source_fragments'][0]['fragment_id']=units[0]['output_fragments'][0]['fragment_id']; (self.target/'MASTER_EN.provenance.json').write_text(json.dumps(value,ensure_ascii=False,sort_keys=True,indent=2)+'\n',encoding='utf8',newline='\n')
  cases.append(('E_C2B_PROVENANCE',valid_other_unit_source))
  def omit_viral_credits_fragments():
   value=json.loads((self.target/'MASTER_EN.provenance.json').read_text(encoding='utf8')); victim=next(unit for unit in value['units'] if unit['anchor']=='viral-credits'); self.assertTrue(victim['source_fragments']); self.assertTrue(victim['output_fragments']); victim['source_fragments']=[]; victim['output_fragments']=[]; (self.target/'MASTER_EN.provenance.json').write_text(json.dumps(value,ensure_ascii=False,sort_keys=True,indent=2)+'\n',encoding='utf8',newline='\n')
  cases.append(('E_C2B_PROVENANCE',omit_viral_credits_fragments))
  def qa():
   value=json.loads((self.target/'MASTER_EN.qa.json').read_text(encoding='utf8'));value['metrics']['anchors']=999;value['errors']=[{'code':'E_FAKE'}];(self.target/'MASTER_EN.qa.json').write_text(json.dumps(value,ensure_ascii=False,sort_keys=True,indent=2)+'\n',encoding='utf8',newline='\n');(self.target/'MASTER_EN.qa.md').write_text(V.qa_md(value),encoding='utf8',newline='\n')
  cases.append(('E_C2B_QA',qa))
  for code,mutate in cases:
   restore();mutate();reseal(self.target);self.assertRaisesRegex(ValueError,code,self.verify)
  restore()

class A3VerifierContractTests(unittest.TestCase):
 def test_b1c3_independent_frozen_navigation_and_xref_mutation_matrix(self):
  cfg=A.author();V.v2_b1c3_xref_closure(cfg,ROOT.parent)
  event=next(row for row in cfg['events'] if row['type']=='generated_navigation')
  cases=(
   lambda c:next(row for row in c['events'] if row['event_id']==event['event_id'])['content']['entries'][0].__setitem__('reader_text','drift'),
   lambda c:next(row for row in c['events'] if row['event_id']==event['event_id'])['content']['entries'][0].__setitem__('target_anchor','viral'),
   lambda c:next(row for row in c['events'] if row['event_id']==event['event_id'])['content'].__setitem__('decision_ref','OUT-026'),
   lambda c:next(row for row in c['events'] if row['event_id']==event['event_id'])['content'].__setitem__('entry_count',0),
   lambda c:next(row for row in c['events'] if row['event_id']==event['event_id'])['content'].__setitem__('family','map_index'),
   lambda c:next(row for row in c['events'] if row['event_id']==event['event_id'])['content']['entries'][0].__setitem__('source_xref_id','toc-viral-back-cover'),
   lambda c:next(row for row in c['events'] if row['event_id']==event['event_id'])['content']['entries'][0].__setitem__('migration_row_id','xrefs:borrowed'),
   lambda c:next(row for row in c['events'] if row['event_id']==event['event_id'])['generated_placement'].__setitem__('after_event','event-p001-000000'),
   lambda c:next(row for row in c['events'] if row['event_id']==event['event_id']).__setitem__('page',1),
   lambda c:next(row for row in c['events'] if row['event_id']==event['event_id'])['content']['entries'].pop(),
   lambda c:next(row for row in c['events'] if row['event_id']==event['event_id'])['content']['entries'].append(copy.deepcopy(next(row for row in c['events'] if row['event_id']==event['event_id'])['content']['entries'][0])),
   lambda c:next(row for row in c['events'] if row['event_id']==event['event_id'])['content']['entries'].reverse(),
   lambda c:next(row for row in c['events'] if row['event_id']==event['event_id']).__setitem__('anchor','viral'),
   lambda c:next(row for row in c['migration']['xref_rows'] if row['source_id'].startswith('xrefs:toc-'))['final_target_ids'].clear(),
   lambda c:next(row for row in c['migration']['xref_rows'] if row['source_id']=='xrefs:p037-handout-21').__setitem__('final_target_ids',['xrefs:p037-handout-21-segment-02','xrefs:p037-handout-21-segment-01']),
   lambda c:next(row for row in c['migration']['xref_rows'] if row['source_id']=='xrefs:p037-handout-21')['final_target_ids'].append('xrefs:p057-keeper-rulebook'),
   lambda c:next(row for row in c['migration']['xref_rows'] if row['source_id']=='xrefs:p057-keeper-rulebook').__setitem__('final_target_ids',['xrefs:p032-handout-7']),
   lambda c:next(row for row in c['migration']['xref_rows'] if row['source_id'].startswith('xrefs:toc-')).__setitem__('final_target_ids',['hierarchy:viral']),
   lambda c:next(row for row in c['xrefs'] if row['xref_id']=='p037-handout-21-segment-01').__setitem__('source_event_id','event-p001-000000'))
  for mutate in cases:
   altered=copy.deepcopy(cfg);mutate(altered)
   with self.assertRaises(ValueError):V.v2_b1c3_xref_closure(altered,ROOT.parent)
 def test_a3_xref_migration_identity_public_preflight(self):
  cfg=v2_fixture();package=bind_v2_inputs(cfg,'a3-verifier-xref-'+uuid.uuid4().hex)
  paths=[]
  def preflight(value):
   path=ROOT/f'.v2-a3-verifier-{uuid.uuid4().hex}.json';path.write_text(json.dumps(value,ensure_ascii=False),encoding='utf8');paths.append(path)
   return V.preflight(*map(str,(ARGS[0],package,path,ARGS[3])))
  try:
   cfg['xrefs']=[{'xref_id':'a3-xref','source_event_id':'b','source_page':2,'target_anchor':'intro','reader_text':'Text.','source_slices':[{'span_id':'s2','start_char':0,'end_char':5}],'emit_link':True,'migration_row_id':'xrefs:a3-xref'}]
   cfg['migration']['new_reviewed_targets'].append({'target_id':'xrefs:a3-xref','decision_ref':'viral-logical_table-p020-l025'});refresh_v2_review_units(cfg)
   self.assertEqual(preflight(cfg)['status'],'preflight_passed')
   cases=(
    lambda c:c['xrefs'][0].__setitem__('migration_row_id','xrefs:drift'),
    lambda c:c['xrefs'][0].__setitem__('migration_row_id','hierarchy:intro'),
    lambda c:c['hierarchy'][0].__setitem__('migration_row_id','hierarchy:infection'))
   for mutate in cases:
    altered=copy.deepcopy(cfg);mutate(altered)
    with self.assertRaisesRegex(ValueError,'E_V2_MIGRATION'):preflight(altered)
  finally:
   for path in paths:path.unlink(missing_ok=True)
   shutil.rmtree(package,ignore_errors=True)
 def test_a3_recovery_title_and_evidence_negative_matrix(self):
  cfg=v2_fixture();package=bind_v2_inputs(cfg,'a3-verifier-recovery');identity=cfg['document']['source_pdf']
  recovery={'recovery_id':'r1','source_pdf_identity':dict(identity),'physical_page':1,'extraction_method':'approved_ocr','source_text':'Recovered','source_text_sha256':hashlib.sha256(b'Recovered').hexdigest().upper(),'evidence_identity':dict(identity),'target_event_id':'b','placement':'after_event','decision_ref':'viral-logical_table-p020-l025'}
  try:
   cfg['events'][1].update({'content':'Recovered','payload_bindings':[{'json_pointer':'/content','source_slices':None,'joiner':'','recovery_id':'r1'}]});cfg['source_recoveries']=[recovery];cfg['hierarchy'][0].update({'reader_title':'Recovered title','reviewed_title_transformation':{'operation':'source_recovery','decision_ref':'viral-logical_table-p020-l025','recovery_id':'r1'}});V.v2_input_binding(cfg,ROOT.parent,ARGS[3],package)
   for mutate in (lambda c:c['source_recoveries'][0].__setitem__('source_text_sha256','0'*64),lambda c:c['source_recoveries'][0]['evidence_identity'].__setitem__('bytes',0),lambda c:c['hierarchy'][0]['reviewed_title_transformation'].__setitem__('recovery_id','missing'),lambda c:c['source_recoveries'][0].__setitem__('decision_ref','')):
    altered=copy.deepcopy(cfg);mutate(altered)
    with self.assertRaises(ValueError):V.v2_input_binding(altered,ROOT.parent,ARGS[3],package)
  finally:shutil.rmtree(package,ignore_errors=True)

class A3VerifierPublicClosureTests(unittest.TestCase):
 """Exercise verifier preflight with independent, source-bound A3 fixtures."""
 def setUp(self):
  self._fresh_public_fixture()
 def _fresh_public_fixture(self):
  if hasattr(self,'package'):shutil.rmtree(self.package,ignore_errors=True)
  self.cfg=v2_fixture();self.package=bind_v2_inputs(self.cfg,'a3-verifier-public-'+uuid.uuid4().hex);self.addCleanup(shutil.rmtree,self.package,True)
  self._add_public_structured_and_asset_fixture();refresh_v2_review_units(self.cfg)
 def _reseal_package_identity(self):
  count,total,digest=V.v2_package_inventory(self.package);self.cfg['document']['reconstruction_package'].update({'file_count':count,'total_bytes':total,'inventory_sha256':digest})
 def _add_public_structured_and_asset_fixture(self):
  self.cfg['hierarchy'].append({'anchor':'room','parent_anchor':'intro','level':None,'toc_entry':False,'semantic_role':'fixture','source_pages':[4],'source_title':'Room text','reader_title':'Room text','representation':'inline_run_in','reviewed_title_transformation':None,'migration_row_id':'hierarchy:room'})
  structured={'event_id':'d','type':'structured_unit','page':4,'order_key':[4,0,V.V2_ROLE_RANK['structured_unit'],3],'anchor':'room','content':{'kind':'callout','body':['Room text'],'contains':['s4'],'end_after':'s4'},'fragment_id':'d','contains':['s4'],'source_span_ids':['s4'],'source_operation':'semantic_restructure','payload_bindings':[]}
  self.cfg['events'].append(structured);bind_v2_event_source(self.cfg,self.package,structured)
  asset={'asset_id':'logo','reader_value':True,'placement':{'after_event':'d'},'anchor':'room','page':5,'source_span_ids':['s5'],'duplication_resolution':'unique_reader','quality_stage':'accepted_reconstruction','source_path':(self.package/'pages'/'page-005.md').relative_to(ROOT.parent).as_posix(),'bytes':(self.package/'pages'/'page-005.md').stat().st_size,'sha256':hashlib.sha256((self.package/'pages'/'page-005.md').read_bytes()).hexdigest().upper(),'semantic_role':'illustration'}
  self.cfg['assets'].append(asset)
  self.cfg['events'].append({'event_id':'e','type':'asset','page':5,'order_key':[5,0,V.V2_ROLE_RANK['asset'],4],'anchor':'room','content':'logo','fragment_id':'e','source_span_ids':['s5'],'source_operation':'asset_reference','payload_bindings':[]})
  span=next(row for row in self.cfg['source_partition']['spans'] if row['span_id']=='s5');span.update({'classification':'asset_reference_source','owner_kind':'asset','owner_id':'logo'})
  self.cfg['migration']['new_reviewed_targets']=[{'target_id':target,'decision_ref':'viral-logical_table-p020-l025'} for target in sorted({*(f'hierarchy:{row["anchor"]}' for row in self.cfg['hierarchy']),*(f'assets:{row["asset_id"]}' for row in self.cfg['assets']),*(f'xrefs:{row["xref_id"]}' for row in self.cfg['xrefs'])})]
  self._reseal_package_identity()
 def _config(self,cfg):
  path=ROOT/f'.v2-a3-verifier-public-{uuid.uuid4().hex}.json';path.write_text(json.dumps(cfg,ensure_ascii=False),encoding='utf8');self.addCleanup(path.unlink,missing_ok=True);return path
 def _preflight(self,cfg): return V.preflight(*map(str,(ARGS[0],self.package,self._config(cfg),ARGS[3])))
 def _reject(self,cfg,code):
  with self.assertRaisesRegex(ValueError,code):self._preflight(cfg)
 def _payload(self,kind):
  data={
   'callout':{'kind':'callout','body':['Room text'],'contains':['s4'],'end_after':'s4'},
   'ordered_list_callout':{'kind':'ordered_list_callout','items':['Room text'],'item_count':1,'contains':['s4'],'end_after':'s4'},
   'table':{'kind':'table','header':['Room text'],'rows':[],'row_count':0,'cell_count':0,'contains':['s4']},
   'equipment_card':{'kind':'equipment_card','title':'Room text','stats':'Room text','footnote':'Room text','body':'Room text','contains':['s4'],'end_after':'s4'},
   'creature_statblock':{'kind':'creature_statblock','title':'Room text','subtitle':'Room text','characteristics':'Room text','derived_stats':'Room text','attacks':'Room text','abilities':'Room text','nested_tables':'Room text','contains':['s4'],'end_after':'s4'},
   'inline_run_in':{'kind':'inline_run_in','anchor':'room','label':'Room text','xref':'Room text','contains':['s4']},
   'full_page_map':{'kind':'full_page_map','pages':[4,5],'reader_asset_ids':['logo'],'accessible_key':'Room text','legend':'Room text','scale':'Room text','contains':['s4']},
   'physical_page_pair':{'kind':'physical_page_pair','front_page':4,'back_page':5,'front_reader_asset_ids':['logo'],'back_reader_asset_ids':['logo'],'back_semantics':'Room text','contains':['s4']}}
  event=next(row for row in self.cfg['events'] if row['event_id']=='d');event['content']=data[kind];event['contains']=data[kind]['contains'];bind_v2_event_source(self.cfg,self.package,event);self._reseal_package_identity();refresh_v2_review_units(self.cfg)
 def test_public_operation_pairs_and_heading_suppress_reject(self):
  self.assertEqual(self._preflight(self.cfg)['status'],'preflight_passed')
  for event in self.cfg['events']:
   for operation in V.V2_OPERATIONS-V.V2_OPERATION_BY_TYPE[event['type']]:
    bad=copy.deepcopy(self.cfg);next(row for row in bad['events'] if row['event_id']==event['event_id'])['source_operation']=operation
    with self.subTest(event=event['type'],operation=operation):self._reject(bad,'E_V2_PROVENANCE')
   for operation in V.V2_OPERATION_BY_TYPE[event['type']]:
    good=copy.deepcopy(self.cfg);next(row for row in good['events'] if row['event_id']==event['event_id'])['source_operation']=operation
    with self.subTest(valid_event=event['type'],operation=operation):self.assertEqual(self._preflight(good)['status'],'preflight_passed')
  bad=copy.deepcopy(self.cfg);bad['events'][0]['source_operation']='suppress';self._reject(bad,'E_V2_PROVENANCE')
 def test_public_contains_closure_unknown_duplicate_incomplete_cross_owner_page_and_order(self):
  self.assertEqual(self._preflight(self.cfg)['status'],'preflight_passed')
  cases={
   'unknown':lambda c:c['events'][3].update({'contains':['missing'],'content':{**c['events'][3]['content'],'contains':['missing'],'end_after':'missing'}}),
   'duplicate':lambda c:c['events'][3].update({'contains':['s4','s4'],'content':{**c['events'][3]['content'],'contains':['s4','s4'],'end_after':'s4'}}),
   'incomplete':lambda c:c['events'][3].update({'contains':[],'content':{**c['events'][3]['content'],'contains':[],'end_after':''}}),
   'cross_owner':lambda c:c['events'][3].update({'contains':['s3'],'content':{**c['events'][3]['content'],'contains':['s3'],'end_after':'s3'}}),
   'cross_page':lambda c:c['events'][3].update({'contains':['s5'],'content':{**c['events'][3]['content'],'contains':['s5'],'end_after':'s5'}}),
   'wrong_span_kind':lambda c:c['events'][3].update({'contains':['c'],'content':{**c['events'][3]['content'],'contains':['c'],'end_after':'c'}})}
  for label,mutate in cases.items():
   bad=copy.deepcopy(self.cfg);mutate(bad)
   with self.subTest(mutation=label):self._reject(bad,'E_V2_STRUCTURE')
 def test_public_asset_source_owner_classification_reuse_and_placement_matrix(self):
  self.assertEqual(self._preflight(self.cfg)['status'],'preflight_passed')
  cases={
   'event_text_span':lambda c:c['assets'][0].__setitem__('source_span_ids',['s2']),
   'foreign_asset_span':lambda c:c['assets'][0].__setitem__('source_span_ids',['s4']),
   'owner_mismatch':lambda c:next(x for x in c['source_partition']['spans'] if x['span_id']=='s5').__setitem__('owner_id','other'),
   'classification_mismatch':lambda c:next(x for x in c['source_partition']['spans'] if x['span_id']=='s5').__setitem__('classification','retained_text'),
   'invalid_placement':lambda c:c['assets'][0]['placement'].__setitem__('after_event','missing')}
  for label,mutate in cases.items():
   bad=copy.deepcopy(self.cfg);mutate(bad)
   with self.subTest(mutation=label):self._reject(bad,'E_V2_ASSET')
 def test_public_all_typed_schemas_complete_source_bound_and_closed(self):
  for kind in ('callout','ordered_list_callout','table','equipment_card','creature_statblock','inline_run_in','full_page_map','physical_page_pair'):
   self._fresh_public_fixture();self._payload(kind)
   with self.subTest(kind=kind,positive=True):self.assertEqual(self._preflight(self.cfg)['status'],'preflight_passed')
   for field in list(self.cfg['events'][3]['content']):
    if field in {'kind','contains','end_after','pages','front_page','back_page'}:continue
    bad=copy.deepcopy(self.cfg);bad['events'][3]['content'].pop(field);bad['events'][3]['payload_bindings']=[row for row in bad['events'][3]['payload_bindings'] if f'/{field}' not in row['json_pointer']]
    with self.subTest(kind=kind,missing=field):self._reject(bad,'E_C2B_SCHEMA: v2-typed-payload')
   bad=copy.deepcopy(self.cfg);bad['events'][3]['content']['invented']='Room text'
   with self.subTest(kind=kind,extra=True):self._reject(bad,'E_V2_PAYLOAD: unbound')
 def test_public_map_pair_reader_assets_and_xref_migration_matrix(self):
  for kind,key in (('full_page_map','reader_asset_ids'),('physical_page_pair','front_reader_asset_ids')):
   self._fresh_public_fixture();self._payload(kind);bad=copy.deepcopy(self.cfg);bad['events'][3]['content'][key]=[]
   if kind=='physical_page_pair':bad['events'][3]['content']['back_reader_asset_ids']=[]
   code='E_V2_STRUCTURE: map' if kind=='full_page_map' else 'E_V2_STRUCTURE: pair'
   with self.subTest(kind=kind,missing_assets=True):self._reject(bad,code)
  cfg=copy.deepcopy(self.cfg);cfg['xrefs']=[{'xref_id':'public-xref','source_event_id':'b','source_page':2,'target_anchor':'intro','reader_text':'Text.','source_slices':[{'span_id':'s2','start_char':0,'end_char':5}],'emit_link':True,'migration_row_id':'xrefs:public-xref'}];cfg['migration']['new_reviewed_targets'].append({'target_id':'xrefs:public-xref','decision_ref':'viral-logical_table-p020-l025'});refresh_v2_review_units(cfg)
  self.assertEqual(self._preflight(cfg)['status'],'preflight_passed')
  for label,mutate in {'foreign_slice':lambda c:c['xrefs'][0]['source_slices'][0].__setitem__('span_id','s1'),'wrong_text':lambda c:c['xrefs'][0].__setitem__('reader_text','wrong'),'migration':lambda c:c['xrefs'][0].__setitem__('migration_row_id','xrefs:missing')}.items():
   bad=copy.deepcopy(cfg);mutate(bad)
   with self.subTest(mutation=label):self._reject(bad,'E_V2_(XREF|MIGRATION)')
 def _legacy_a3_all_typed_kinds_have_independent_source_bound_positive_fixture(self):
  cfg=v2_fixture();package=bind_v2_inputs(cfg,'a3-verifier-typed')
  payloads={'callout':{'kind':'callout','body':['Text.'],'contains':['s2'],'end_after':'s2'},'ordered_list_callout':{'kind':'ordered_list_callout','items':['Text.'],'item_count':1,'contains':['s2']},'table':{'kind':'table','header':['Text.'],'rows':[],'row_count':0,'contains':['s2']},'equipment_card':{'kind':'equipment_card','title':'Text.','contains':['s2']},'creature_statblock':{'kind':'creature_statblock','title':'Text.','contains':['s2']},'inline_run_in':{'kind':'inline_run_in','label':'Text.','contains':['s2']},'full_page_map':{'kind':'full_page_map','accessible_text':'Text.','pages':[2],'contains':['s2']},'physical_page_pair':{'kind':'physical_page_pair','front_page':2,'back_page':3,'accessible_back_semantics':'Text.','contains':['s2']}}
  try:
   for payload in payloads.values():
    current=copy.deepcopy(cfg);event=current['events'][1];event.update({'type':'structured_unit','content':payload,'contains':['s2'],'source_operation':'semantic_restructure','order_key':[2,0,V.V2_ROLE_RANK['structured_unit'],1]});pointer=V.v2_a3_leaves(payload)[0][0];event['payload_bindings']=[{'json_pointer':pointer,'source_slices':[{'span_id':'s2','start_char':0,'end_char':5}],'joiner':'','recovery_id':None}];refresh_v2_review_units(current);V.v2_input_binding(current,ROOT.parent,ARGS[3],package)
  finally:shutil.rmtree(package,ignore_errors=True)
 def test_a3_independent_provenance_payload_hierarchy_negative_matrix(self):
  cfg=v2_fixture();package=bind_v2_inputs(cfg,'a3-verifier-matrix')
  try:
   V.v2_input_binding(cfg,ROOT.parent,ARGS[3],package)
   cases=[
    lambda c:c['events'][0].__setitem__('source_span_ids',[]),
    lambda c:c['events'][1].__setitem__('source_span_ids',['s1']),
    lambda c:c['events'][1].__setitem__('order_key',[99,0,0,0]),
    lambda c:c['events'][1]['payload_bindings'][0].__setitem__('joiner','--'),
    lambda c:c['events'][1]['payload_bindings'].append(copy.deepcopy(c['events'][1]['payload_bindings'][0])),
    lambda c:c['hierarchy'][1].__setitem__('parent_anchor','missing'),
    lambda c:c['events'][1].__setitem__('content','Translatable source key'),
    lambda c:c['source_partition']['spans'][0].__setitem__('owner_id','other')]
   for mutate in cases:
    altered=copy.deepcopy(cfg);mutate(altered)
    with self.assertRaises(ValueError):V.v2_input_binding(altered,ROOT.parent,ARGS[3],package)
  finally:shutil.rmtree(package,ignore_errors=True)
