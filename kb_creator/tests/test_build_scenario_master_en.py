from __future__ import annotations
import copy, hashlib, importlib.util, json, shutil, subprocess, sys, tempfile, unittest, uuid
from unittest import mock
from pathlib import Path

ROOT=Path(__file__).parents[1]; SCRIPT=ROOT/'scripts'/'build_scenario_master_en.py'
spec=importlib.util.spec_from_file_location('phase_a_builder',SCRIPT); B=importlib.util.module_from_spec(spec); spec.loader.exec_module(B)
verify_spec=importlib.util.spec_from_file_location('phase_a_verifier',ROOT/'scripts'/'verify_scenario_master_en.py'); V=importlib.util.module_from_spec(verify_spec); verify_spec.loader.exec_module(V)
author_spec=importlib.util.spec_from_file_location('phase_a_author',ROOT/'scripts'/'author_viral_master_en_v2_config.py'); A=importlib.util.module_from_spec(author_spec); author_spec.loader.exec_module(A)
ARGS=(ROOT/'contracts'/'viral.json',ROOT/'working'/'viral'/'source_reconstruction'/'20260901_step6a_reconstructed_en_package_v4',ROOT/'working'/'viral'/'master_en'/'publication_config_v1.json',ROOT/'working'/'viral'/'source'/'Call_of_Cthulhu_Viral.pdf')
CONFIG=json.loads(ARGS[2].read_text(encoding='utf8'))
FAKE_RENDERER='''import sys
from PIL import Image, PngImagePlugin
if '-v' in sys.argv:
 print("pdftoppm version 26.05.0")
 raise SystemExit(0)
prefix=sys.argv[-1]
page=int(sys.argv[sys.argv.index("-f")+1])
image=Image.new("RGBA", (1700,2200), (page % 256,34,56,127))
info=PngImagePlugin.PngInfo(); info.add_text("unwanted", "metadata")
image.save(prefix+".png", pnginfo=info)
'''
def sha(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest().upper()
def eol_profile(raw):
 counts={'lf':0,'crlf':0,'crcrlf':0,'lone_cr':0};i=0
 while i<len(raw):
  if raw[i:i+3]==b'\r\r\n':counts['crcrlf']+=1;i+=3
  elif raw[i:i+2]==b'\r\n':counts['crlf']+=1;i+=2
  elif raw[i:i+1]==b'\n':counts['lf']+=1;i+=1
  elif raw[i:i+1]==b'\r':counts['lone_cr']+=1;i+=1
  else:i+=1
 lines=raw.splitlines();return {**counts,'line_slots':len(lines),'nonblank_line_slots':sum(bool(line.strip()) for line in lines)}

def _v2_fixture_base():
 return {'schema':'kb_creator.master_en_publication.v2','scenario_id':'synthetic','document':{'audit_scope':list(range(1,125)),'reader_scope':list(range(1,123)),'generated_navigation':{'operation':'generated_navigation_replaces_source_toc','source_identity':'synthetic-toc'}},'hierarchy':[{'anchor':'intro','page':1,'source_title':'Introduction','reader_title':'Introduction','representation':'heading','reviewed_title_transformation':None},{'anchor':'room','page':2,'source_title':'Room 2E','reader_title':'Room 2E','representation':'inline_run_in','reviewed_title_transformation':None},{'anchor':'infection','page':3,'source_title':'Infection','reader_title':'Infection','representation':'anchor_only','reviewed_title_transformation':None}],'events':[{'event_id':'e1','type':'heading','page':1,'order_key':[1,1],'anchor':'intro','content':'','fragment_id':'f1'},{'event_id':'e2','type':'text_fragment','page':1,'order_key':[1,2],'anchor':'intro','content':'Prose.','fragment_id':'f2'},{'event_id':'e3','type':'structured_unit','page':2,'order_key':[2,1],'anchor':'room','content':{'kind':'callout','body':['Room text'],'contains':['child'],'end_after':'child'},'fragment_id':'f3','contains':['child']},{'event_id':'e4','type':'anchor_only','page':3,'order_key':[3,1],'anchor':'infection','content':'','fragment_id':'f4'},{'event_id':'e5','type':'asset','page':3,'order_key':[3,2],'anchor':'infection','content':'logo','fragment_id':'f5'}],'assets':[{'asset_id':'logo','reader_value':False,'placement':{'after_event':'e4'},'anchor':'infection','page':3}],'xrefs':[],'source_recoveries':[],'metrics':{'source_pages_audited':124,'reader_pages':122,'excluded_advertising_pages':2}}
def v2_fixture():
 value=_v2_fixture_base();zero={'path':'kb_creator/.v2-placeholder','bytes':0,'sha256':'0'*64}
 value['document'].update({'source_pdf':dict(zero),'reconstruction_package':{'root':'kb_creator/.v2-placeholder','file_count':1,'total_bytes':1,'inventory_algorithm':B.PACKAGE_ALGO,'inventory_sha256':'0'*64}})
 value['source_disposition']=[{'page':page,'audit_disposition':'reconstructed','publication_disposition':'excluded_advertising' if page in {123,124} else 'reader','publish_reader_content':page not in {123,124},'decision_date':'2026-09-02' if page in {123,124} else '2026-09-01','reason':'approved advertising exclusion' if page in {123,124} else 'reader source page','page_markdown':{'path':f'kb_creator/.v2-placeholder/pages/page-{page:03d}.md','bytes':0,'sha256':'0'*64}} for page in range(1,125)]
 value['visual_review_units']=[{'review_id':'heading-e1','kind':'heading_outline','source_pages':[1],'event_ids':['e1'],'asset_ids':[],'priority':True,'contact_sheet_group':'outline'},{'review_id':'callout-e3','kind':'callout','source_pages':[2],'event_ids':['e3'],'asset_ids':[],'priority':False,'contact_sheet_group':'structures'}]
 value['source_partition']={'pages':[],'spans':[]}
 value['migration']={'inputs':{'frozen_v1_config':dict(zero),'decision_evidence':[{**zero,'kind':'kb_creator.semantic_unit_review.v2'}]},'new_reviewed_targets':[]}
 for ledger,(domain,key,count,_) in B.MIGRATION_DOMAINS.items():
  source=CONFIG[domain]
  value['migration'][ledger]=[{'source_id':f'{domain}:{row[key]}','source_row_sha256':B.v2_canonical_row(row),'outcome':'excluded_advertising' if domain=='source_disposition' and row['page'] in {123,124} else 'suppressed_reviewed','final_target_ids':[],'decision_ref':'viral-logical_table-p020-l025'} for row in source]
 for index,row in enumerate(value['hierarchy']):
  page=row.pop('page');row.update({'parent_anchor':None if not index else value['hierarchy'][index-1]['anchor'],'level':1 if row['representation']=='heading' else None,'toc_entry':row['representation']=='heading','semantic_role':'fixture','source_pages':[page],'migration_row_id':f'hierarchy:{row["anchor"]}'})
 for event in value['events']:
  event.update({'source_span_ids':['fixture-span'],'source_operation':'emit_exact','payload_bindings':[]})
 for asset in value['assets']:asset['source_span_ids']=['fixture-span']
 return value

def bind_v2_inputs(value,label):
 """Build a disposable 124-page reconstruction package for identity-bound v2 tests."""
 package=ROOT/f'.v2-inputs-{label}';shutil.rmtree(package,ignore_errors=True);pages=package/'pages';pages.mkdir(parents=True)
 for page in range(1,125): (pages/f'page-{page:03d}.md').write_text(f'fixture reconstruction page {page}\n',encoding='utf8',newline='\n')
 evidence=package/'decision-evidence.json';evidence.write_text(json.dumps({'schema':'kb_creator.semantic_unit_review.v2','decisions':[{'candidate_id':'viral-logical_table-p020-l025'}]}),encoding='utf8')
 rel=lambda path:path.relative_to(ROOT.parent).as_posix()
 value['document']['source_pdf']={'path':rel(ARGS[3]),'bytes':ARGS[3].stat().st_size,'sha256':sha(ARGS[3])}
 count,total,digest=B.v2_package_inventory(package)
 value['document']['reconstruction_package']={'root':rel(package),'file_count':count,'total_bytes':total,'inventory_algorithm':B.PACKAGE_ALGO,'inventory_sha256':digest}
 for row in value['source_disposition']:
  path=pages/f"page-{row['page']:03d}.md";row['page_markdown']={'path':rel(path),'bytes':path.stat().st_size,'sha256':sha(path)}
 partition_pages=[];spans=[]
 for page in range(1,123):
  path=pages/f'page-{page:03d}.md';raw=path.read_bytes();text=raw.decode('utf8');span_id=f's{page}'
  spans.append({'span_id':span_id,'page':page,'source_path':f'pages/page-{page:03d}.md','start_byte':0,'end_byte':len(raw),'start_char':0,'end_char':len(text),'raw_sha256':sha(path),'raw_text_sha256':hashlib.sha256(text.encode('utf8')).hexdigest().upper(),'classification':'retained_text','owner_kind':'event','owner_id':'fixture','decision_ref':None})
  partition_pages.append({'page':page,'path':f'pages/page-{page:03d}.md','bytes':len(raw),'sha256':sha(path),'encoding':'utf-8-no-bom','eol_profile':eol_profile(raw),'span_ids':[span_id]})
 value['source_partition']={'pages':partition_pages,'spans':spans}
 v1={'path':rel(ARGS[2]),'bytes':ARGS[2].stat().st_size,'sha256':sha(ARGS[2])}
 value['migration']['inputs']={'frozen_v1_config':dict(v1),'decision_evidence':[{'path':rel(evidence),'bytes':evidence.stat().st_size,'sha256':sha(evidence),'kind':'kb_creator.semantic_unit_review.v2'}]}
 value['migration']['new_reviewed_targets']=[{'target_id':target,'decision_ref':'viral-logical_table-p020-l025'} for target in sorted({*(f'hierarchy:{row["anchor"]}' for row in value['hierarchy']),*(f'assets:{row["asset_id"]}' for row in value['assets']),*(f'xrefs:{row["xref_id"]}' for row in value['xrefs'])})]
 # A3 fixture: each event owns one exact raw source span, while every other
 # source page is an explicitly partitioned suppression unit.
 samples={1:'Introduction\n',2:'Prose.\n',3:'Room text\n',4:'anchor\n',5:'![logo](logo.png)\n'}
 for page,text in samples.items():(pages/f'page-{page:03d}.md').write_text(text,encoding='utf8',newline='\n')
 value['hierarchy']=[
  {'anchor':'intro','parent_anchor':None,'level':1,'toc_entry':True,'semantic_role':'chapter','source_pages':[1,2],'source_title':'Introduction','reader_title':'Introduction','representation':'heading','reviewed_title_transformation':None,'migration_row_id':'hierarchy:intro'},
  {'anchor':'room','parent_anchor':'intro','level':None,'toc_entry':False,'semantic_role':'run_in','source_pages':[3],'source_title':'Room text','reader_title':'Room text','representation':'inline_run_in','reviewed_title_transformation':None,'migration_row_id':'hierarchy:room'},
  {'anchor':'infection','parent_anchor':'room','level':None,'toc_entry':False,'semantic_role':'anchor','source_pages':[4,5],'source_title':'anchor','reader_title':'anchor','representation':'anchor_only','reviewed_title_transformation':None,'migration_row_id':'hierarchy:infection'}]
 for index,event in enumerate(value['events'],1):
  page=index;raw=(pages/f'page-{page:03d}.md').read_bytes();text=raw.decode('utf8')
  event['page']=page;event['source_span_ids']=[f's{page}'];event['source_operation']={'heading':'emit_exact','text_fragment':'emit_exact','structured_unit':'semantic_restructure','anchor_only':'emit_anchor_only','asset':'asset_reference'}[event['type']];event['order_key']=[page,0,B.V2_ROLE_RANK[event['type']],index-1]
  if event['type']=='heading':event['content']='Introduction'
  elif event['type']=='text_fragment':event['content']='Prose.'
  elif event['type']=='structured_unit':event['content']={'kind':'callout','body':['Room text'],'contains':['s3'],'end_after':'s3'};event['contains']=['s3']
  event['payload_bindings']=[] if event['type'] in {'anchor_only','asset'} else [{'json_pointer':'/content' if isinstance(event['content'],str) else '/content/body/0','source_slices':[{'span_id':f's{page}','start_char':0,'end_char':len(event['content'] if isinstance(event['content'],str) else 'Room text')}],'joiner':'','recovery_id':None}]
 value['assets'][0].update({'page':5,'source_span_ids':['s5']})
 spans=[];partition_pages=[]
 for page in range(1,123):
  path=pages/f'page-{page:03d}.md';raw=path.read_bytes();text=raw.decode('utf8');event=next((item for item in value['events'] if item['page']==page),None)
  asset_event=event and event['type']=='asset'
  spans.append({'span_id':f's{page}','page':page,'source_path':f'pages/page-{page:03d}.md','start_byte':0,'end_byte':len(raw),'start_char':0,'end_char':len(text),'raw_sha256':sha(path),'raw_text_sha256':hashlib.sha256(text.encode('utf8')).hexdigest().upper(),'classification':'asset_reference_source' if asset_event else 'retained_text' if event else 'authorized_suppression','owner_kind':'asset' if asset_event else 'event' if event else 'suppression','owner_id':event['content'] if asset_event else event['event_id'] if event else f'suppression-{page}','decision_ref':None})
  partition_pages.append({'page':page,'path':f'pages/page-{page:03d}.md','bytes':len(raw),'sha256':sha(path),'encoding':'utf-8-no-bom','eol_profile':eol_profile(raw),'span_ids':[f's{page}']})
  value['source_disposition'][page-1]['page_markdown']={'path':rel(path),'bytes':len(raw),'sha256':sha(path)}
 value['source_partition']={'pages':partition_pages,'spans':spans}
 count,total,digest=B.v2_package_inventory(package);value['document']['reconstruction_package'].update({'file_count':count,'total_bytes':total,'inventory_sha256':digest})
 return refresh_v2_review_units(value) and package

def bind_v2_decision_evidence(value,path,kind,payload,ref):
 path.write_bytes(payload if isinstance(payload,bytes) else payload.encode('utf8') if isinstance(payload,str) else json.dumps(payload).encode('utf8'))
 value['migration']['inputs']['decision_evidence']=[{'path':path.relative_to(ROOT.parent).as_posix(),'bytes':path.stat().st_size,'sha256':sha(path),'kind':kind}]
 for ledger in B.MIGRATION_DOMAINS:
  for row in value['migration'][ledger]:row['decision_ref']=ref
 for row in value['migration']['new_reviewed_targets']:row['decision_ref']=ref

def refresh_v2_review_units(value):
 hierarchy={row['anchor']:row for row in value['hierarchy']};units=[]
 def add(event,kind,priority,group):units.append({'review_id':f'review:{kind}:{event["event_id"]}','kind':kind,'source_pages':[event['page']],'event_ids':[event['event_id']],'asset_ids':[],'priority':priority,'contact_sheet_group':group})
 for event in value['events']:
  if event['type']=='heading' and hierarchy[event['anchor']]['representation']=='heading':add(event,'heading_outline',True,'outline')
  elif event['type']=='structured_unit':add(event,event['content']['kind'],False,'structured')
 expected={row['source_event_id'] for row in value['xrefs']}|{row['target_event_id'] for row in value['source_recoveries']}
 for event in value['events']:
  if event['event_id'] in expected:add(event,'xref_recovery',True,'xref_recovery')
 for asset in value['assets']:
  if asset['reader_value']:units.append({'review_id':f'review:asset_placement:{asset["asset_id"]}','kind':'asset_placement','source_pages':[asset.get('source_page',asset.get('page'))],'event_ids':[],'asset_ids':[asset['asset_id']],'priority':False,'contact_sheet_group':'reader_assets'})
 value['visual_review_units']=units;return value
class BuilderPreflightTests(unittest.TestCase):
 def test_v2_source_partition_byte_unicode_eol_and_mutation_matrix(self):
  cfg=v2_fixture();package=bind_v2_inputs(cfg,'partition');page=package/'pages'/'page-001.md'
  try:
   raw=b'alpha\r\nbeta\r\r\n\r\ngamma\rdelta\n\n\xd0\x96\n';page.write_bytes(raw)
   row=cfg['source_disposition'][0];row['page_markdown'].update({'bytes':len(raw),'sha256':sha(page)})
   item=cfg['source_partition']['pages'][0];span=cfg['source_partition']['spans'][0];text=raw.decode('utf8')
   item.update({'bytes':len(raw),'sha256':sha(page),'eol_profile':eol_profile(raw)})
   span.update({'end_byte':len(raw),'end_char':len(text),'raw_sha256':sha(page),'raw_text_sha256':hashlib.sha256(raw).hexdigest().upper()})
   metrics=B.v2_source_partition(cfg['source_partition'],package)
   self.assertEqual(metrics,{'pages':122,'bytes':sum(x['bytes'] for x in cfg['source_partition']['pages']),'line_slots':129,'nonblank_line_slots':126,'eol':{'lf':124,'crlf':2,'crcrlf':1,'lone_cr':1}})
   cases=[
    (lambda c:c['source_partition']['spans'][0].__setitem__('start_byte',1),'coverage mismatch'),
    (lambda c:c['source_partition']['spans'][0].__setitem__('start_char',1),'coverage mismatch'),
    (lambda c:c['source_partition']['spans'][0].__setitem__('raw_text_sha256','0'*64),'coverage mismatch'),
    (lambda c:c['source_partition']['pages'][0].__setitem__('eol_profile',{}),'page mismatch'),
    (lambda c:c['source_partition']['spans'].append(copy.deepcopy(c['source_partition']['spans'][0])),'span mismatch'),
    (lambda c:c['source_partition']['pages'][0].__setitem__('path','../page-001.md'),'page mismatch'),
    (lambda c:c['source_partition']['pages'][0].__setitem__('page',True),'page mismatch')]
   for mutate,needle in cases:
    altered=copy.deepcopy(cfg);mutate(altered)
    with self.assertRaisesRegex(ValueError,needle):B.v2_source_partition(altered['source_partition'],package)
  finally:shutil.rmtree(package,ignore_errors=True)


class MasterEnV3NeutralTests(unittest.TestCase):
 def setUp(self):
  self.temp=tempfile.TemporaryDirectory();self.root=Path(self.temp.name);self.package=self.root/'reconstruction';self.package.mkdir();(self.package/'assets').mkdir()
  self.contract=self.root/'publication-contract.json';self.contract.write_text(json.dumps({'schema':'kb_creator.scenario_publication_contract.v1','scenario':{'id':'sample'}}),encoding='utf8')
  self.source=self.package/'RECONSTRUCTED_EN.md';self.source.write_text('<!-- source-page-001 -->\n\n<a id="intro"></a>\n# Introduction\n\nText ![Map](assets/map.png).\n\n<!-- source-page-002 -->\n\n# Advertising\n',encoding='utf8',newline='\n');(self.package/'assets'/'map.png').write_bytes(b'neutral-image')
  self.producer=self.root/'producer.json';self.producer.write_text('{}\n',encoding='utf8');self.evidence=self.root/'qa.json';self.evidence.write_text('{}\n',encoding='utf8')
  self.inventory=self.root/'reconstruction-inventory.json';inventory={'schema':'fixture','scenario_id':'sample','reconstruction_contract_sha256':'A'*64,'artifacts':[{'role':'reconstructed_en','path':'reconstruction/RECONSTRUCTED_EN.md','bytes':self.source.stat().st_size,'sha256':sha(self.source)}]};inventory['inventory_sha256']=hashlib.sha256(json.dumps(inventory,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()).hexdigest().upper();self.inventory.write_text(json.dumps(inventory),encoding='utf8')
  rec=lambda path:{'path':path.relative_to(self.root).as_posix(),'bytes':path.stat().st_size,'sha256':sha(path)}
  self.acceptance=self.root/'reconstruction.acceptance.json';acceptance={'schema':'kb_creator.artifact_acceptance.v1','scenario_id':'sample','artifact_kind':'reconstructed_en','candidate':rec(self.source),'producer_stage':rec(self.producer),'evidence':[rec(self.evidence)],'decision':'accepted','decision_at_utc':'2026-09-14T00:00:00Z','user_decision_reference':'fixture explicit','recorder_role':'main_orchestrator'};acceptance['receipt_sha256']=hashlib.sha256(json.dumps(acceptance,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()).hexdigest().upper();self.acceptance.write_text(json.dumps(acceptance),encoding='utf8')
  self.config=self.root/'master-en-v3.json';config={'schema':B.V3_SCHEMA,'scenario_id':'sample','inputs':{'publication_contract':rec(self.contract),'reconstruction_inventory':rec(self.inventory),'reconstruction_acceptance':rec(self.acceptance),'reconstructed_en':rec(self.source)},'projection':{'output_name':'MASTER_EN.md','excluded_source_pages':[2],'page_marker_policy':'source_page_comment_v1','anchor_policy':'preserve_v1','asset_policy':'copy_markdown_references_v1'},'required_qa':['source_identity','topology','asset_closure']};self.config.write_text(json.dumps(config),encoding='utf8')
  self.target=Path('candidate');self.target_path=self.root/self.target
 def tearDown(self):self.temp.cleanup()
 def refresh_source_bindings(self,text,excluded=None):
  self.source.write_text(text,encoding='utf8',newline='\n')
  inventory=json.loads(self.inventory.read_text());inventory['artifacts'][0].update({'bytes':self.source.stat().st_size,'sha256':sha(self.source)});inventory.pop('inventory_sha256');inventory['inventory_sha256']=hashlib.sha256(json.dumps(inventory,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()).hexdigest().upper();self.inventory.write_text(json.dumps(inventory),encoding='utf8')
  acceptance=json.loads(self.acceptance.read_text());acceptance['candidate'].update({'bytes':self.source.stat().st_size,'sha256':sha(self.source)});acceptance.pop('receipt_sha256');acceptance['receipt_sha256']=hashlib.sha256(json.dumps(acceptance,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()).hexdigest().upper();self.acceptance.write_text(json.dumps(acceptance),encoding='utf8')
  rec=lambda path:{'path':path.relative_to(self.root).as_posix(),'bytes':path.stat().st_size,'sha256':sha(path)}
  config=json.loads(self.config.read_text());config['inputs'].update({'reconstruction_inventory':rec(self.inventory),'reconstruction_acceptance':rec(self.acceptance),'reconstructed_en':rec(self.source)});config['projection']['excluded_source_pages']=excluded or [];self.config.write_text(json.dumps(config),encoding='utf8')
 def test_v3_build_and_independent_verify_derive_all_counts(self):
  result=B.build_candidate(self.contract,self.package,self.config,None,self.target);verified=V.verify_v3_candidate(self.contract,self.package,self.config,self.target)
  self.assertEqual(result['derived'],{'source_pages':2,'excluded_pages':1,'page_boundary_joins':0,'headings':1,'anchors':1,'assets':1});self.assertEqual(verified['derived'],result['derived']);self.assertNotIn('Advertising',(self.target_path/'MASTER_EN.md').read_text(encoding='utf8'));self.assertTrue((self.target_path/'assets'/'map.png').is_file())
 def test_v3_build_joins_page_split_prose_and_preserves_audit_transitions(self):
  self.refresh_source_bindings('<!-- source-page-001 -->\n\nThe body remains malle-\n\n<!-- source-page-002 -->\n\nability under stress.\n\nA second paragraph reaches the end of the\n\n<!-- source-page-003 -->\n\nsame day without interruption.\n\n# Closing\n')
  result=B.build_candidate(self.contract,self.package,self.config,None,self.target);verified=V.verify_v3_candidate(self.contract,self.package,self.config,self.target);master=(self.target_path/'MASTER_EN.md').read_text(encoding='utf8');provenance=json.loads((self.target_path/'MASTER_EN.provenance.json').read_text())
  self.assertIn('The body remains malleability under stress.\n\n<!-- source-page-002 -->',master);self.assertIn('the end of the same day without interruption.\n\n<!-- source-page-003 -->',master);self.assertEqual(master.count('<!-- source-page-'),3)
  self.assertEqual(result['derived']['page_boundary_joins'],2);self.assertEqual(verified['derived'],result['derived']);self.assertEqual([row['mode'] for row in provenance['page_boundary_transitions']],['dehyphenated_word','continued_prose'])
 def test_v3_page_boundary_join_is_fail_closed_for_non_prose_boundaries(self):
  blocked=(
   ('# Heading','lowercase continuation'),('- list item','lowercase continuation'),('    code','lowercase continuation'),('| cell |','lowercase continuation'),('POWER 50  ','endurance 40'),('![Map](assets/map.png)','lowercase continuation'),('Finished.','lowercase continuation'),('unfinished','Uppercase new paragraph'))
  for left,right in blocked:
   with self.subTest(left=left,right=right):
    source=f'<!-- source-page-001 -->\n\n{left}\n\n<!-- source-page-002 -->\n\n{right}\n';normalized,transitions=B._v3_normalize_page_boundaries(source);verified,verified_transitions=V._v3_normalize_page_boundaries(source);self.assertEqual(normalized,source);self.assertEqual(transitions,[]);self.assertEqual(verified,source);self.assertEqual(verified_transitions,[])
 def test_v3_rejects_source_pdf_and_tampered_candidate(self):
  with self.assertRaisesRegex(ValueError,'accepts reconstructed EN only'):B.v3_preflight(self.contract,self.package,self.config,self.contract)
  B.build_candidate(self.contract,self.package,self.config,None,self.target);(self.target_path/'MASTER_EN.md').write_text('tampered\n',encoding='utf8')
  with self.assertRaisesRegex(ValueError,'E_V3_SEMANTIC'):V.verify_v3_candidate(self.contract,self.package,self.config,self.target)
 def test_v3_rejects_absolute_output_before_write_and_verifier_rejects_absolute_target(self):
  with tempfile.TemporaryDirectory() as outside_temp:
   outside=Path(outside_temp)/'outside-candidate'
   with self.assertRaisesRegex(ValueError,'safe authority-relative'):B.build_candidate(self.contract,self.package,self.config,None,outside)
   self.assertFalse(outside.exists())
  B.build_candidate(self.contract,self.package,self.config,None,self.target)
  with self.assertRaisesRegex(ValueError,'E_V3_PATH'):V.verify_v3_candidate(self.contract,self.package,self.config,self.target_path)


class ViralV2B1c4AssetAuditTests(unittest.TestCase):
 def test_b1c4_physical_asset_closure_accepts_separate_closed_hierarchy_target(self):
  migration=A.author()['migration'];targets=copy.deepcopy(migration['new_reviewed_targets']);targets.append({'target_id':'hierarchy:viral-reviewed-santina','decision_ref':'OUT-003'})
  B.v2_b1c4_migration_closure(migration['asset_rows'],targets)
  for altered in ({'target_id':'hierarchy:viral-reviewed-santina','decision_ref':'OUT-004'},{'target_id':'hierarchy:','decision_ref':'OUT-003'},{'target_id':'hierarchy:viral-reviewed-santina','decision_ref':'OUT-003','replaces':[]}):
   with self.assertRaisesRegex(ValueError,'hierarchy target|replacement target domain'):B.v2_b1c4_migration_closure(migration['asset_rows'],[ *targets[:-1],altered])
 def test_canonical_source_free_asset_event_requires_explicit_order_evidence(self):
  event={'event_id':'asset','type':'asset','page':7,'order_key':[7,321,4,19],'anchor':'section','content':'visual','source_operation':'asset_reference'};events={'target':{'event_id':'target'}}
  visual={'asset_id':'visual','disposition':'reader','source_page':7,'anchor':'section','placement':{'before_event':'target'},'source_order':{'kind':'selected_view_raw_index','view':'raw','raw_index':12,'gap_ordinal':0}}
  B._v2_canonical_source_free_asset_event(visual,event,events)
  physical={**visual,'source_order':{'kind':'physical_unit_page_slot','unit_id':'pair','page_slot':1}}
  B._v2_canonical_source_free_asset_event(physical,event,events)
  for altered in ({**visual,'source_order':{'kind':'selected_view_raw_index','view':'raw','raw_index':12}}, {**visual,'placement':{'before_event':'missing'}}, {**visual,'source_page':8}):
   with self.assertRaisesRegex(ValueError,'canonical asset (?:event|source order) mismatch'):B._v2_canonical_source_free_asset_event(altered,event,events)
 def test_b1c6_helper_reparse_and_evidence_topology_attacks(self):
  value=A.author();package=ARGS[1];spans={row['span_id']:row for row in value['source_partition']['spans']}
  with mock.patch.object(B,'v2_reparse',side_effect=lambda path:Path(path).name in {'assets',next(row for row in value['assets'] if row['binary'])['binary']['path'].split('/')[-1]}):
   with self.assertRaises(ValueError):B.v2_asset_provenance_binding(value,package,ROOT.parent,spans)
  original=B.js
  def altered(path,label):
   data=original(path,label)
   if Path(path).name=='ASSET_MANIFEST.json':data=copy.deepcopy(data);data['assets'].append(copy.deepcopy(data['assets'][0]))
   if Path(path).name=='comparison.json':data=copy.deepcopy(data);view=next(iter(data['views'].values()));view['blocks'].append(copy.deepcopy(view['blocks'][0]))
   return data
  with mock.patch.object(B,'js',side_effect=altered):
   with self.assertRaises(ValueError):B.v2_asset_provenance_binding(value,package,ROOT.parent,spans)
  missing=copy.deepcopy(value);visual=next(row for row in missing['assets'] if row['provenance']['kind']=='visual_region');visual['provenance']['source_asset_reference']='not-in-block-assets'
  with self.assertRaises(ValueError):B.v2_asset_provenance_binding(missing,package,ROOT.parent,{row['span_id']:row for row in missing['source_partition']['spans']})
 def test_b1c6_helper_real_binding_and_closed_mutation_matrix(self):
  value=A.author();package=ARGS[1];spans={row['span_id']:row for row in value['source_partition']['spans']}
  self.assertEqual(B.v2_asset_provenance_binding(value,package,ROOT.parent,spans)['counts'],{'markdown_image_reference':16,'visual_region':100,'reviewed_provisional_full_page':10})
  markdown=next(row for row in value['assets'] if row['provenance']['kind']=='markdown_image_reference');visual=next(row for row in value['assets'] if row['provenance']['kind']=='visual_region');provisional=next(row for row in value['assets'] if row['provenance']['kind']=='reviewed_provisional_full_page')
  cases=(
   lambda c:c['assets'].append({'asset_id':'legacy','reader_value':False,'placement':{'before_event':'x'},'anchor':'x','page':1,'source_span_ids':['x']}),
   lambda c:markdown_row(c).__setitem__('page',1),
   lambda c:markdown_row(c)['provenance'].__setitem__('marker_sha256','0'*64),
   lambda c:markdown_row(c)['provenance'].__setitem__('span_id',visual_row(c)['provenance'].get('span_id','missing')),
   lambda c:visual_row(c)['binary'].__setitem__('path','kb_creator/working/viral/source_reconstruction/20260901_step6a_reconstructed_en_package_v4/ASSET_MANIFEST.json'),
   lambda c:visual_row(c)['provenance'].__setitem__('asset_manifest_row_sha256','0'*64),
   lambda c:visual_row(c)['provenance'].__setitem__('comparison_block_sha256','0'*64),
   lambda c:provisional_row(c)['provenance']['render_recipe'].__setitem__('dpi',199),
   lambda c:provisional_row(c)['provenance'].__setitem__('region',{'kind':'full_media_box','points':[0,0,1,1]}),
   lambda c:provisional_row(c).__setitem__('binary',{}),
   lambda c:markdown_row(c)['provenance'].__setitem__('span_id',markdown_row(c)['provenance']['span_id']+'-missing'),
   lambda c:markdown_row(c)['provenance'].__setitem__('start_byte',markdown_row(c)['provenance']['start_byte']+1),
   lambda c:markdown_row(c)['provenance'].__setitem__('start_char',markdown_row(c)['provenance']['start_char']+1),
   lambda c:markdown_row(c)['provenance'].__setitem__('page_markdown_identity',visual_row(c)['provenance']['asset_manifest_identity']),
   lambda c:markdown_row(c)['provenance'].__setitem__('source_page',2),
   lambda c:visual_row(c)['binary'].__setitem__('sha256','0'*64),
   lambda c:visual_row(c)['binary'].__setitem__('bytes',1),
   lambda c:visual_row(c)['binary'].__setitem__('media_type','image/png'),
   lambda c:visual_row(c)['binary']['dimensions'].__setitem__('width',1),
   lambda c:visual_row(c)['provenance']['asset_manifest_identity'].__setitem__('sha256','0'*64),
   lambda c:visual_row(c)['provenance']['comparison_identity'].__setitem__('sha256','0'*64),
   lambda c:visual_row(c)['provenance'].__setitem__('selected_view','missing'),
   lambda c:visual_row(c)['provenance'].__setitem__('raw_index',-1),
   lambda c:visual_row(c)['provenance'].__setitem__('source_asset_reference','foreign.png'),
   lambda c:visual_row(c)['provenance'].__setitem__('block_type','text'),
   lambda c:visual_row(c)['provenance'].__setitem__('source_page',2),
   lambda c:visual_row(c)['provenance'].__setitem__('bbox',[0,0,1,1]),
   lambda c:provisional_row(c)['provenance']['source_pdf_identity'].__setitem__('sha256','0'*64),
   lambda c:provisional_row(c)['provenance'].__setitem__('physical_page',provisional_row(c)['provenance']['physical_page']+1),
   lambda c:provisional_row(c)['provenance'].__setitem__('page_index_zero_based',provisional_row(c)['provenance']['page_index_zero_based']+1),
   lambda c:provisional_row(c)['provenance']['render_recipe'].__setitem__('color','gray'),
   lambda c:provisional_row(c)['provenance'].__setitem__('output_media_type','image/jpeg'),
   lambda c:provisional_row(c)['provenance']['output_dimensions'].__setitem__('width',1),
   lambda c:provisional_row(c).__setitem__('source_page',provisional_row(c)['source_page']+1) )
  def markdown_row(c):return next(row for row in c['assets'] if row['asset_id']==markdown['asset_id'])
  def visual_row(c):return next(row for row in c['assets'] if row['asset_id']==visual['asset_id'])
  def provisional_row(c):return next(row for row in c['assets'] if row['asset_id']==provisional['asset_id'])
  for ordinal,mutate in enumerate(cases):
   altered=copy.deepcopy(value);mutate(altered)
   with self.subTest(ordinal=ordinal):
    with self.assertRaises(ValueError):B.v2_asset_provenance_binding(altered,package,ROOT.parent,{row['span_id']:row for row in altered['source_partition']['spans']})
 def test_real_input_partition_and_path_binaries_are_exact(self):
  audit=B.v2_b1c4_asset_audit(ROOT.parent)
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
   with self.assertRaisesRegex(ValueError,'B1c4'):B.v2_config(altered)
  by_id={row['asset_id']:row for row in value['assets']};critic=('viral-accepted-e1e2aa6964b45037691d92e4faf91dba6bbd411e409dc49c237f6b0e71e6ce85','viral-accepted-a1d83a711a4b7962110b1ba158b2d610043f1fa836e06458e675373094acd6c1')
  markdown=[row['asset_id'] for row in value['assets'] if row['provenance']['kind']=='markdown_image_reference'];visual=[row['asset_id'] for row in value['assets'] if row['provenance']['kind']=='visual_region'];provisional=[row['asset_id'] for row in value['assets'] if row['provenance']['kind']=='reviewed_provisional_full_page']
  for target,donor in (critic,critic[::-1],(markdown[0],markdown[1]),(visual[0],visual[1]),(provisional[0],provisional[1])):
   altered=copy.deepcopy(value);row=next(item for item in altered['assets'] if item['asset_id']==target);row['binary']=copy.deepcopy(by_id[donor]['binary']);row['provenance']=copy.deepcopy(by_id[donor]['provenance'])
   with self.assertRaisesRegex(ValueError,'B1c4'):B.v2_config(altered)
  altered=copy.deepcopy(value);altered['assets'][0]['binary']['bytes']+=1
  with self.assertRaisesRegex(ValueError,'B1c4'):B.v2_config(altered)
  altered=copy.deepcopy(value);altered['assets'][0]['provenance']['bbox'][0]+=1
  with self.assertRaisesRegex(ValueError,'B1c4'):B.v2_config(altered)
 def test_unmutated_public_v2_preflight_passes_and_cleans_up(self):
  path=ROOT/'working'/'viral'/'master_en'/f'.phase-b1c4-builder-{uuid.uuid4().hex}.json'
  try:
   path.write_text(json.dumps(A.author(),ensure_ascii=False),encoding='utf8')
   self.assertEqual(B.preflight(*map(str,(ARGS[0],ARGS[1],path,ARGS[3])))['status'],'preflight_passed')
  finally:path.unlink(missing_ok=True)
  self.assertFalse(path.exists())
 def test_a3_closed_typed_payload_and_operation_matrix_regressions(self):
  payload={'kind':'equipment_card','title':'T','stats':'S','footnote':'F','body':'B','contains':['s'],'end_after':'s'}
  B.v2_a3_payload_schema(payload)
  accepted=copy.deepcopy(payload);accepted.update({'stats':'','footnote':'','body':''});B.v2_a3_payload_schema(accepted)
  for mutate in (lambda x:x.pop('stats'),lambda x:x.__setitem__('extra','invented'),lambda x:x.update({'title':'','stats':'','footnote':'','body':''})):
   altered=copy.deepcopy(payload);mutate(altered)
   with self.assertRaises(ValueError):B.v2_a3_payload_schema(altered)
  self.assertEqual(B.V2_OPERATION_BY_TYPE['heading'],{'emit_exact'})
  self.assertEqual(B.V2_OPERATION_BY_TYPE['asset'],{'asset_reference','suppress'})
 def test_v2_reconstruction_package_known_answer_and_topology(self):
  package=ARGS[1]
  self.assertEqual(B.v2_package_inventory(package),(377,41079424,'68C17FB765A89C6146398868E61F1F6EB7B2FE4EAFBA8C2C2C8F42260BBDBA83'))
  with tempfile.TemporaryDirectory() as temp:
   root=Path(temp);(root/'pages').mkdir();(root/'pages'/'page-001.md').write_text('x\n',encoding='utf8')
   self.assertEqual(B.v2_package_inventory(root)[0],1)
   (root/'empty').mkdir()
   with self.assertRaisesRegex(ValueError,'topology mismatch'):B.v2_package_inventory(root)

 def test_v2_reconstruction_package_closed_declaration_and_first_mismatch(self):
  cfg=v2_fixture();package=bind_v2_inputs(cfg,'aggregate')
  try:
   B.v2_input_binding(cfg,ROOT.parent,ARGS[3],package)
   for mutate,needle in [
    (lambda c:c['document'].__setitem__('reconstruction_inventory',{}),'closed schema'),
    (lambda c:c['document'].pop('reconstruction_package'),'closed schema'),
    (lambda c:c['document']['reconstruction_package'].__setitem__('extra',1),'closed schema'),
    (lambda c:c['document']['reconstruction_package'].__setitem__('file_count',False),'integer'),
    (lambda c:c['document']['reconstruction_package'].__setitem__('total_bytes',-1),'identity mismatch'),
    (lambda c:c['document']['reconstruction_package'].__setitem__('inventory_sha256','a'*64),'identity mismatch'),
    (lambda c:c['document']['reconstruction_package'].__setitem__('inventory_algorithm','wrong'),'identity mismatch'),
    (lambda c:c['document']['reconstruction_package'].__setitem__('root','../escape'),'safe repository-relative')]:
    bad=copy.deepcopy(cfg);mutate(bad)
    with self.assertRaisesRegex(ValueError,needle):B.v2_config(bad) if 'safe' not in needle else B.v2_input_binding(bad,ROOT.parent,ARGS[3],package)
   for field,needle in [('file_count','file_count'),('total_bytes','total_bytes'),('inventory_sha256','inventory_sha256')]:
    bad=copy.deepcopy(cfg);bad['document']['reconstruction_package'][field]=0 if field!='inventory_sha256' else '0'*64
    with self.assertRaisesRegex(ValueError,needle):B.v2_input_binding(bad,ROOT.parent,ARGS[3],package)
  finally:shutil.rmtree(package,ignore_errors=True)

 def test_v2_reconstruction_package_path_shapes_and_cli_no_traceback(self):
  cfg=v2_fixture();package=bind_v2_inputs(cfg,'path-shapes');config=ROOT/'.v2-path-shapes.json';file=ROOT/'.v2-path-shapes-file';wrong=ROOT/'.v2-path-shapes-wrong'
  try:
   for altered,cli in [(lambda c:c['document']['reconstruction_package'].__setitem__('root','kb_creator/.missing-v2-package'),package),(lambda c:c,package/'missing')]:
    bad=copy.deepcopy(cfg);altered(bad)
    with self.assertRaisesRegex(ValueError,'CLI/config path mismatch'):B.v2_input_binding(bad,ROOT.parent,ARGS[3],cli)
   file.write_text('file\n',encoding='utf8');wrong.mkdir()
   for cli in (file,wrong):
    with self.assertRaisesRegex(ValueError,'CLI/config path mismatch'):B.v2_input_binding(cfg,ROOT.parent,ARGS[3],cli)
   config.write_text(json.dumps(cfg),encoding='utf8')
   result=subprocess.run([sys.executable,'-B',str(SCRIPT),'--contract',str(ARGS[0]),'--reconstruction-package',str(package/'missing'),'--publication-config',str(config),'--source-pdf',str(ARGS[3]),'--target','kb_creator/working/synthetic/master_en/candidates/path-shape','--preflight-only'],capture_output=True,text=True)
   self.assertNotEqual(result.returncode,0);self.assertIn('v2 reconstruction package CLI/config path mismatch',result.stderr);self.assertNotIn('Traceback',result.stderr)
  finally:
   config.unlink(missing_ok=True);file.unlink(missing_ok=True);shutil.rmtree(wrong,ignore_errors=True);shutil.rmtree(package,ignore_errors=True)

 def test_v2_reconstruction_package_immutable_tree_mutations(self):
  cfg=v2_fixture();package=bind_v2_inputs(cfg,'tree-mutations')
  try:
   path=package/'pages'/'page-001.md';original=path.read_bytes()
   for action,needle in [
    (lambda: path.unlink(),'file_count'),
    (lambda: path.rename(package/'pages'/'renamed.md'),'inventory_sha256'),
    (lambda: path.write_bytes(b'Z'*(len(original)-1)+b'\n'),'inventory_sha256')]:
    B.v2_input_binding(cfg,ROOT.parent,ARGS[3],package);action()
    with self.assertRaisesRegex(ValueError,needle):B.v2_input_binding(cfg,ROOT.parent,ARGS[3],package)
    shutil.rmtree(package,ignore_errors=True);package=bind_v2_inputs(cfg,'tree-mutations')
    path=package/'pages'/'page-001.md';original=path.read_bytes()
  finally:shutil.rmtree(package,ignore_errors=True)
 def test_production_preflight_and_no_target(self):
  out=ROOT/'working'/'viral'/'master_en'/'phase_a_test_target';self.assertFalse(out.exists());self.assertEqual(B.preflight(*ARGS)['status'],'preflight_passed');self.assertFalse(out.exists())
 def test_unknown_top_key_is_closed(self):
  d=json.loads(ARGS[2].read_text(encoding='utf8'));d['unknown']=1
  with self.assertRaisesRegex(ValueError,'closed schema'):B.closed(d,B.TOP,'publication config')
 def test_cli_rejects_out_of_parent_target_before_target(self):
  out=ROOT/'working'/'viral'/'master_en'/'phase_a_test_target';r=subprocess.run([sys.executable,'-B',str(SCRIPT),'--contract',str(ARGS[0]),'--reconstruction-package',str(ARGS[1]),'--publication-config',str(ARGS[2]),'--source-pdf',str(ARGS[3]),'--target',str(out)],capture_output=True,text=True)
  self.assertNotEqual(r.returncode,0);self.assertIn('candidate target path mismatch',r.stderr);self.assertFalse(out.exists())

 def test_v2_typed_event_graph_and_title_policy(self):
  fixture=refresh_v2_review_units(v2_fixture());text=B.serialize_v2(fixture)
  self.assertEqual(text,'<a id="intro"></a>\n# Introduction\n\nProse.\n\n> Room text\n\n<a id="infection"></a>\n')
  bad=copy.deepcopy(fixture);bad['events'][1]['order_key']=[1,1]
  with self.assertRaisesRegex(ValueError,'monotonic'):B.v2_config(bad)
  bad=copy.deepcopy(fixture);bad['hierarchy'][0]['reader_title']='Short';bad['hierarchy'][0]['reviewed_title_transformation']=None
  with self.assertRaisesRegex(ValueError,'title fidelity'):B.v2_config(bad)

 def test_v2_source_disposition_identity_order_exclusion_and_leakage(self):
  cfg=v2_fixture();package=bind_v2_inputs(cfg,'disposition');root=ROOT.parent
  try:
   B.v2_input_binding(cfg,root,ARGS[3],package)
   for mutate,pattern in [(lambda value:value['source_disposition'].pop(),'count'),(lambda value:value['source_disposition'].__setitem__(1,copy.deepcopy(value['source_disposition'][0])),'row'),(lambda value:value['source_disposition'][122].__setitem__('publication_disposition','reader'),'policy'),(lambda value:value['source_disposition'][122].__setitem__('reason',''),'exclusion')]:
    bad=copy.deepcopy(cfg);mutate(bad)
    with self.assertRaisesRegex(ValueError,pattern):B.v2_config(bad)
   bad=copy.deepcopy(cfg);bad['document']['source_pdf']['sha256']='0'*64
   with self.assertRaisesRegex(ValueError,'identity mismatch'):B.v2_input_binding(bad,root,ARGS[3],package)
   bad=copy.deepcopy(cfg);bad['source_disposition'][0]['page_markdown']['sha256']='0'*64
   with self.assertRaisesRegex(ValueError,'identity mismatch'):B.v2_input_binding(bad,root,ARGS[3],package)
   bad=copy.deepcopy(cfg);bad['events'][0]['page']=123
   with self.assertRaisesRegex(ValueError,'event mismatch'):B.v2_config(bad)
  finally:shutil.rmtree(package,ignore_errors=True)

 def test_v2_materializer_is_atomic_deterministic_and_excludes_reader_pages(self):
  cfg=v2_fixture(); path=ROOT/'.v2-builder-unittest.json'; parent=ROOT/'working'/'synthetic'/'master_en'; target=parent/'candidates'/'v2-unittest'
  shutil.rmtree(ROOT/'working'/'synthetic',ignore_errors=True)
  package=bind_v2_inputs(cfg,'materializer')
  try:
   path.write_text(json.dumps(cfg),encoding='utf8'); result=B.build_candidate(*map(str,(ARGS[0],package,path,ARGS[3])),(Path('kb_creator')/'working'/'synthetic'/'master_en'/'candidates'/'v2-unittest').as_posix())
   self.assertEqual(result['status'],'candidate_built_for_independent_verification');self.assertFalse((target/'MASTER_EN.acceptance.json').exists())
   self.assertEqual(json.loads((target/'MASTER_EN.qa.json').read_text())['metrics']['excluded_advertising_pages'],2)
   self.assertEqual(json.loads((target/'SOURCE_DISPOSITION.json').read_text())['pages'][-2:],[cfg['source_disposition'][-2],cfg['source_disposition'][-1]])
   self.assertNotIn('assets/logo',(target/'MASTER_EN.md').read_text());self.assertEqual(len(json.loads((target/'INVENTORY.json').read_text())['rows']),5)
   with self.assertRaisesRegex(ValueError,'target exists'):B.build_candidate(*map(str,(ARGS[0],package,path,ARGS[3])),(Path('kb_creator')/'working'/'synthetic'/'master_en'/'candidates'/'v2-unittest').as_posix())
  finally:
   path.unlink(missing_ok=True);shutil.rmtree(package,ignore_errors=True);shutil.rmtree(ROOT/'working'/'synthetic',ignore_errors=True)

 def test_v2_reader_asset_copy_identity_and_policy(self):
  cfg=v2_fixture(); blob=ROOT/'.v2-builder-asset.bin'; config=ROOT/'.v2-builder-asset.json';blob.write_bytes(b'asset')
  package=bind_v2_inputs(cfg,'asset')
  cfg['assets']=[{'asset_id':'logo','reader_value':True,'placement':{'after_event':'e2'},'anchor':'infection','page':3,'source_span_ids':['s5'],'duplication_resolution':'unique_reader','quality_stage':'provisional_full_page','source_path':'kb_creator/.v2-builder-asset.bin','bytes':5,'sha256':sha(blob),'semantic_role':'full_page'}];refresh_v2_review_units(cfg)
  target=(Path('kb_creator')/'working'/'synthetic'/'master_en'/'candidates'/'v2-asset').as_posix();shutil.rmtree(ROOT/'working'/'synthetic',ignore_errors=True)
  try:
   config.write_text(json.dumps(cfg),encoding='utf8');B.build_candidate(*map(str,(ARGS[0],package,config,ARGS[3])),target)
   out=ROOT/'working'/'synthetic'/'master_en'/'candidates'/'v2-asset';self.assertEqual((out/'assets'/'logo').read_bytes(),b'asset');self.assertIn('Prose.\n\n![logo](assets/logo)',(out/'MASTER_EN.md').read_text())
   provenance=json.loads((out/'MASTER_EN.provenance.json').read_text());rows={row['event_id']:row for row in provenance['events']}
   self.assertEqual(rows['e5']['emission'],'emitted');emitted=rows['e2'];master=(out/'MASTER_EN.md').read_text(encoding='utf8');value=master[emitted['start_char']:emitted['end_char']]
   self.assertEqual(hashlib.sha256(value.encode('utf8')).hexdigest().upper(),emitted['slice_sha256'])
   target2=(Path('kb_creator')/'working'/'synthetic'/'master_en'/'candidates'/'v2-asset-two').as_posix();B.build_candidate(*map(str,(ARGS[0],package,config,ARGS[3])),target2);out2=ROOT/'working'/'synthetic'/'master_en'/'candidates'/'v2-asset-two'
   self.assertEqual({p.relative_to(out).as_posix():p.read_bytes() for p in out.rglob('*') if p.is_file() and p.name!='INVENTORY.json'},{p.relative_to(out2).as_posix():p.read_bytes() for p in out2.rglob('*') if p.is_file() and p.name!='INVENTORY.json'})
   bad=copy.deepcopy(cfg);bad['assets'][0]['quality_stage']='final_xobject'
   with self.assertRaisesRegex(ValueError,'policy'):B.v2_config(bad)
  finally:
   blob.unlink(missing_ok=True);config.unlink(missing_ok=True);shutil.rmtree(package,ignore_errors=True);shutil.rmtree(ROOT/'working'/'synthetic',ignore_errors=True)

 def test_v2_chunk_ledger_relocation_ranges_and_literal_preservation(self):
  cfg=v2_fixture()
  cfg['events']=[
   {'event_id':'h','type':'heading','page':1,'order_key':[1,1],'anchor':'intro','content':'','fragment_id':'h'},
   {'event_id':'repeat-one','type':'text_fragment','page':1,'order_key':[1,2],'anchor':'intro','content':'same\n\n\ntext','fragment_id':'one'},
   {'event_id':'before','type':'asset','page':1,'order_key':[1,3],'anchor':'intro','content':'before','fragment_id':'before'},
   {'event_id':'repeat-two','type':'text_fragment','page':1,'order_key':[1,4],'anchor':'intro','content':'same\n\n\ntext','fragment_id':'two'},
   {'event_id':'after','type':'asset','page':1,'order_key':[1,5],'anchor':'intro','content':'after','fragment_id':'after'},
   {'event_id':'unit','type':'structured_unit','page':2,'order_key':[2,1],'anchor':'room','content':{'kind':'callout','body':['Room text'],'contains':['child'],'end_after':'child'},'fragment_id':'unit','contains':['child']},
   {'event_id':'inside','type':'asset','page':2,'order_key':[2,2],'anchor':'room','content':'inside','fragment_id':'inside'},
   {'event_id':'hidden','type':'asset','page':3,'order_key':[3,1],'anchor':'infection','content':'hidden','fragment_id':'hidden'},
  ]
  cfg['assets']=[
   {'asset_id':'before','reader_value':True,'placement':{'before_event':'repeat-two'},'anchor':'intro','page':1,'duplication_resolution':'unique_reader','quality_stage':'provisional_full_page','source_path':'kb_creator/.v2-builder-asset.bin','bytes':5,'sha256':'0'*64,'semantic_role':'full_page'},
   {'asset_id':'after','reader_value':True,'placement':{'after_event':'repeat-one'},'anchor':'intro','page':1,'duplication_resolution':'unique_reader','quality_stage':'provisional_full_page','source_path':'kb_creator/.v2-builder-asset.bin','bytes':5,'sha256':'0'*64,'semantic_role':'full_page'},
   {'asset_id':'inside','reader_value':True,'placement':{'inside_structured_unit':'unit'},'anchor':'room','page':2,'duplication_resolution':'unique_reader','quality_stage':'provisional_full_page','source_path':'kb_creator/.v2-builder-asset.bin','bytes':5,'sha256':'0'*64,'semantic_role':'full_page'},
   {'asset_id':'hidden','reader_value':False,'placement':{'after_event':'unit'},'anchor':'infection','page':3},
  ]
  for event in cfg['events']:event.update({'source_span_ids':['fixture-span'],'source_operation':'emit_exact','payload_bindings':[]})
  for asset in cfg['assets']:asset['source_span_ids']=['fixture-span']
  chunks=B.v2_typed_chunks(refresh_v2_review_units(cfg));text,ledger=B.v2_join_ledger(chunks)
  self.assertIn('same\n\n\ntext\n\n![after](assets/after)\n\n![before](assets/before)\n\nsame\n\n\ntext',text)
  self.assertTrue(text.startswith('<a id="intro"></a>\n# Introduction'))
  self.assertIn('> Room text\n![inside](assets/inside)',text);self.assertNotIn('hidden](assets/hidden)',text)
  rows={row['event_id']:row for row in ledger};self.assertEqual(rows['hidden']['emission'],'suppressed')
  self.assertEqual(rows['unit']['contains'],['child']);self.assertNotIn('contains',rows['repeat-one'])
  self.assertLess(rows['repeat-one']['start_char'],rows['repeat-two']['start_char'])
  for row in ledger:
   if row['emission']!='emitted':
    self.assertFalse({'start_char','end_char','start_byte','end_byte'} & set(row));continue
   value=text[row['start_char']:row['end_char']]
   self.assertEqual(value.encode('utf8'),text.encode('utf8')[row['start_byte']:row['end_byte']])
   self.assertEqual(hashlib.sha256(value.encode('utf8')).hexdigest().upper(),row['slice_sha256'])
  self.assertEqual((text,ledger),B.v2_join_ledger(B.v2_typed_chunks(copy.deepcopy(cfg))))
  duplicate=copy.deepcopy(cfg);duplicate['events'][1]['event_id']='h'
  with self.assertRaisesRegex(ValueError,'duplicate event'):B.v2_typed_chunks(duplicate)
  shared=copy.deepcopy(cfg);shared['assets'][1]['placement']={'before_event':'repeat-two'}
  shared_text,_=B.v2_join_ledger(B.v2_typed_chunks(shared))
  self.assertIn('![before](assets/before)\n\n![after](assets/after)\n\nsame\n\n\ntext',shared_text)
  reversed_rows=copy.deepcopy(shared);reversed_rows['assets'].reverse();refresh_v2_review_units(reversed_rows)
  reversed_text,_=B.v2_join_ledger(B.v2_typed_chunks(reversed_rows))
  self.assertIn('![before](assets/before)\n\n![after](assets/after)\n\nsame\n\n\ntext',reversed_text)
  missing=copy.deepcopy(shared);missing['assets'][0].pop('placement')
  with mock.patch.object(B,'v2_config',return_value=None):
   with self.assertRaisesRegex(ValueError,'placement missing'):B.v2_typed_chunks(missing)

 def test_v2_heading_levels_and_canonical_asset_marker(self):
  for level in range(1,7):
   hierarchy={'section':{'anchor':'section','representation':'heading','level':level,'reader_title':f'Level {level}'}}
   event={'event_id':f'h{level}','type':'heading','anchor':'section','content':''}
   self.assertEqual(B._v2_event_render(event,hierarchy,{}),f'<a id="section"></a>\n'+('#'*level)+f' Level {level}')
  canonical={'asset_id':'logical-id','disposition':'reader','binary':{'path':'kb_creator/working/fixture/verified-image.png'}}
  self.assertEqual(B._v2_asset_marker(canonical),'![Illustration](assets/verified-image.png)')
  self.assertEqual(B._v2_asset_marker({'asset_id':'legacy','reader_value':True,'source_path':'kb_creator/fixture.png'}),'![legacy](assets/legacy)')

 def test_v2_provisional_recipe_materializes_staging_png(self):
  from PIL import Image
  with tempfile.TemporaryDirectory() as temp:
   root=Path(temp);pdf=root/'source.pdf';pdf.write_bytes(b'pdf');out=root/'assets';out.mkdir()
   asset={'asset_id':'provisional','source_page':7,'binary':None,'provenance':{'kind':'reviewed_provisional_full_page','render_recipe':{'tool':'pdftoppm','dpi':200,'first_page':7,'last_page':7},'output_dimensions':{'width':20,'height':30}}}
   def render(command,**_):Image.new('RGB',(20,30),'white').save(Path(command[-1]+'.png'))
   with mock.patch.object(B.subprocess,'run',side_effect=render):
    path,identity=B.v2_render_provisional_asset(asset,pdf,out)
   self.assertEqual(path.name,'provisional.png');self.assertEqual(identity['dimensions'],{'width':20,'height':30})
   malformed=copy.deepcopy(asset);malformed['provenance']['render_recipe']['first_page']=6
   with self.assertRaisesRegex(ValueError,'provisional recipe mismatch'):B.v2_render_provisional_asset(malformed,pdf,out)
   wrong_dimensions=copy.deepcopy(asset);wrong_dimensions['provenance']['output_dimensions']={'width':21,'height':30}
   with mock.patch.object(B.subprocess,'run',side_effect=render):
    with self.assertRaisesRegex(ValueError,'provisional render dimensions'):B.v2_render_provisional_asset(wrong_dimensions,pdf,out)

 def test_v2_negative_duplicate_binding_fragment_and_excluded_page(self):
  token=uuid.uuid4().hex;blob=ROOT/f'.v2-negative-{token}.bin';config=ROOT/f'.v2-negative-{token}.json';candidate=(Path('kb_creator')/'working'/'synthetic'/'master_en'/'candidates'/f'v2-negative-{token}').as_posix();blob.write_bytes(b'asset')
  cfg=v2_fixture();package=bind_v2_inputs(cfg,'negative');cfg['assets']=[{'asset_id':'logo','reader_value':True,'placement':{'after_event':'e2'},'anchor':'infection','page':3,'source_span_ids':['s5'],'duplication_resolution':'unique_reader','quality_stage':'provisional_full_page','source_path':blob.relative_to(ROOT.parent).as_posix(),'bytes':5,'sha256':sha(blob),'semantic_role':'full_page'}];refresh_v2_review_units(cfg)
  try:
   duplicate=copy.deepcopy(cfg);duplicate['assets'].append({**duplicate['assets'][0],'asset_id':'other','page':6,'source_span_ids':['s6']});duplicate['events'].append({'event_id':'e6','type':'asset','page':6,'order_key':[6,0,B.V2_ROLE_RANK['asset'],5],'anchor':'infection','content':'other','fragment_id':'f6','source_span_ids':['s6'],'source_operation':'asset_reference','payload_bindings':[]});duplicate['events'].sort(key=lambda row:tuple(row['order_key']));duplicate['hierarchy'][-1]['source_pages'].append(6);duplicate['source_partition']['spans'][5].update({'classification':'asset_reference_source','owner_kind':'asset','owner_id':'other'});refresh_v2_review_units(duplicate)
   # The negative variant adds a materialized asset after bind_v2_inputs().
   # Seal it explicitly so the intended invalid target is reached.
   duplicate['migration']['new_reviewed_targets']=[{'target_id':target,'decision_ref':'viral-logical_table-p020-l025'} for target in sorted({*(f'hierarchy:{row["anchor"]}' for row in duplicate['hierarchy']),*(f'assets:{row["asset_id"]}' for row in duplicate['assets']),*(f'xrefs:{row["xref_id"]}' for row in duplicate['xrefs'])})]
   duplicate['assets'][1]['placement']={'after_event':'missing-event'}
   config.write_text(json.dumps(duplicate),encoding='utf8')
   with self.assertRaisesRegex(ValueError,'placement (?:target|mismatch)'):B.build_candidate(*map(str,(ARGS[0],package,config,ARGS[3])),candidate)
   fragment=copy.deepcopy(cfg);fragment['events'][0]['fragment_id']=''
   with self.assertRaisesRegex(ValueError,'event mismatch'):B.v2_config(fragment)
   excluded=copy.deepcopy(cfg);excluded['events'][0]['page']=123
   with self.assertRaisesRegex(ValueError,'event mismatch'):B.v2_config(excluded)
  finally:
   blob.unlink(missing_ok=True);config.unlink(missing_ok=True);shutil.rmtree(package,ignore_errors=True);shutil.rmtree(ROOT/'working'/'synthetic'/'master_en'/'candidates'/Path(candidate).name,ignore_errors=True)

 def test_v2_all_typed_serializers_and_closure_failures(self):
  cases=[
   ({'kind':'table','header':['A','B'],'rows':[['x|y','z']],'row_count':1,'cell_count':2,'contains':['a']},'| A | B |'),
   ({'kind':'callout','body':['body'],'contains':['a'],'end_after':'a'},'> body'),
   ({'kind':'ordered_list_callout','items':['one','two'],'contains':['a','b'],'end_after':'b'},'> 1. one'),
   ({'kind':'equipment_card','title':'T','stats':'S','footnote':'F','body':'B','contains':['a'],'end_after':'a'},'> **T**'),
   ({'kind':'creature_statblock','title':'T','subtitle':'Sub','characteristics':'C','derived_stats':'S','attacks':'A','abilities':'B','nested_tables':'N','contains':['a'],'end_after':'a'},'> **T** — Sub'),
   ({'kind':'inline_run_in','anchor':'room','label':'Room','xref':'xref','contains':[]},'<a id="room">'),
   ({'kind':'full_page_map','pages':[106,107],'reader_asset_ids':['map'],'accessible_key':'A','legend':'L','scale':'S','contains':[]},'> Map pages: 106, 107'),
   ({'kind':'physical_page_pair','front_page':111,'back_page':112,'front_reader_asset_ids':['front'],'back_reader_asset_ids':['back'],'back_semantics':'text','contains':[]},'text')]
  for data,expected in cases:
   event={'content':data,'contains':data['contains']};self.assertIn(expected,B.serialize_v2_structured(event))
  multiline={'content':{'kind':'equipment_card','title':'T\nU','stats':'S\nD','footnote':'','body':'B\nC','contains':['a'],'end_after':'a'},'contains':['a']}
  self.assertEqual(B.serialize_v2_structured(multiline),'> **T**\n> **U**\n> S\n> D\n> B\n> C')
  title_absent={'content':{'kind':'equipment_card','title':'','stats':'STR 10','footnote':'','body':'','contains':['a'],'end_after':'a'},'contains':['a']}
  self.assertEqual(B.serialize_v2_structured(title_absent),'> STR 10')
  optional_map={'content':{'kind':'full_page_map','pages':[106,107],'reader_asset_ids':['map'],'accessible_key':'','legend':'','scale':'','contains':[]},'contains':[]}
  self.assertEqual(B.serialize_v2_structured(optional_map),'> Map pages: 106, 107')
  bad={'content':{'kind':'table','header':['A'],'rows':[['x','y']],'row_count':1,'cell_count':2,'contains':['a']},'contains':['a']}
  with self.assertRaisesRegex(ValueError,'table shape'):B.serialize_v2_structured(bad)
  bad={'content':{'kind':'table','header':['A','A'],'rows':[['x','y']],'row_count':1,'cell_count':2,'contains':['a']},'contains':['a']}
  with self.assertRaisesRegex(ValueError,'table shape'):B.serialize_v2_structured(bad)
  bad={'content':{'kind':'callout','body':['b'],'contains':['a'],'end_after':'wrong'},'contains':['a']}
  with self.assertRaisesRegex(ValueError,'boundary'):B.serialize_v2_structured(bad)
  bad={'content':{'kind':'equipment_card','title':'T','stat':'S','footnote':'F','body':'B','contains':['a'],'end_after':'a'},'contains':['extra']}
  with self.assertRaisesRegex(ValueError,'contains'):B.serialize_v2_structured(bad)

 def test_v2_migration_ledgers_close_frozen_rows_decisions_and_targets(self):
  cfg=v2_fixture();package=bind_v2_inputs(cfg,'migration-builder')
  try:
   B.v2_input_binding(cfg,ROOT.parent,ARGS[3],package)
   cases=[
    (lambda c:c['migration']['hierarchy_rows'].pop(),'count mismatch'),
    (lambda c:c['migration']['asset_rows'].append(copy.deepcopy(c['migration']['asset_rows'][0])),'count mismatch'),
    (lambda c:c['migration']['xref_rows'][0].__setitem__('source_id','xrefs:not-frozen'),'source closure mismatch'),
    (lambda c:c['migration']['source_disposition_rows'][0].__setitem__('source_row_sha256','0'*64),'source row mismatch'),
    (lambda c:c['migration']['handout_rows'][0].__setitem__('decision_ref','missing'),'unknown decision mismatch'),
    (lambda c:c['migration']['structured_rows'][0].update({'outcome':'retained_unchanged','decision_ref':'viral'}),'unchanged decision mismatch'),
    (lambda c:c['migration']['new_reviewed_targets'].append({'target_id':'hierarchy:intro','decision_ref':'missing'}),'new target closure mismatch'),
    (lambda c:c['migration']['inputs']['frozen_v1_config'].__setitem__('sha256','0'*64),'identity mismatch'),
    (lambda c:c['migration']['inputs']['decision_evidence'][0].__setitem__('path','../unsafe.json'),'safe repository-relative')]
   for mutate,needle in cases:
    altered=copy.deepcopy(cfg);mutate(altered)
    with self.assertRaisesRegex(ValueError,needle):B.v2_input_binding(altered,ROOT.parent,ARGS[3],package)
  finally: shutil.rmtree(package,ignore_errors=True)

 def test_v2_decision_evidence_rejects_cross_file_duplicate_catalog_id(self):
  """A decision id may have exactly one bound structured-evidence origin."""
  cfg=v2_fixture();package=bind_v2_inputs(cfg,'decision-cross-file-duplicate-builder');duplicate=ROOT/'.v2-decision-evidence-duplicate-builder.json'
  try:
   duplicate.write_text(json.dumps({'schema':'kb_creator.semantic_unit_review.v2','decisions':[{'candidate_id':'viral-logical_table-p020-l025'}]}),encoding='utf8')
   cfg['migration']['inputs']['decision_evidence'].append({'path':duplicate.relative_to(ROOT.parent).as_posix(),'bytes':duplicate.stat().st_size,'sha256':sha(duplicate),'kind':'kb_creator.semantic_unit_review.v2'})
   with self.assertRaisesRegex(ValueError,'decision evidence catalog mismatch'):
    B.v2_input_binding(cfg,ROOT.parent,ARGS[3],package)
  finally: duplicate.unlink(missing_ok=True);shutil.rmtree(package,ignore_errors=True)

 def test_v2_decision_evidence_provenance_classes_allow_only_valid_corroboration(self):
  cfg=v2_fixture();package=bind_v2_inputs(cfg,'decision-provenance-builder');files=[]
  def add(name,value,kind):
   path=ROOT/name;path.write_text(value if isinstance(value,str) else json.dumps(value),encoding='utf8');files.append(path)
   cfg['migration']['inputs']['decision_evidence'].append({'path':path.relative_to(ROOT.parent).as_posix(),'bytes':path.stat().st_size,'sha256':sha(path),'kind':kind});return path
  try:
   add('.v2-provenance-boundary-builder.json',{'schema':'kb_creator.viral_boundary_ledger.v1','units':[{'id':'unit-1','registry_refs':['OUT-999']}],'candidate_dispositions':[{'candidate_id':'viral-logical_table-p020-l025','target_unit_id':'unit-1'}],'deferred_nonblocking':[{'registry_ref':'OUT-999'}]},'kb_creator.viral_boundary_ledger.v1')
   add('.v2-provenance-registry-builder.md','### OUT-999 — registry decision\n','kb_creator.user_review_registry.md')
   add('.v2-provenance-closure-builder.json',{'schema':'kb_creator.semantic_unit_closure.v2','unresolved_blocking_candidates':[],'deferred_nonblocking':[{'id':'OUT-999'}]},'kb_creator.semantic_unit_closure.v2')
   B.v2_input_binding(cfg,ROOT.parent,ARGS[3],package)
   incompatible=copy.deepcopy(cfg);path=ROOT/'.v2-provenance-incompatible-builder.json';path.write_text(json.dumps({'schema':'kb_creator.viral_boundary_ledger.v1','units':[{'id':'unit-2','registry_refs':['viral-logical_table-p020-l025']}],'candidate_dispositions':[],'deferred_nonblocking':[]}),encoding='utf8');files.append(path)
   incompatible['migration']['inputs']['decision_evidence'].append({'path':path.relative_to(ROOT.parent).as_posix(),'bytes':path.stat().st_size,'sha256':sha(path),'kind':'kb_creator.viral_boundary_ledger.v1'})
   with self.assertRaisesRegex(ValueError,'decision evidence catalog mismatch'):B.v2_input_binding(incompatible,ROOT.parent,ARGS[3],package)
  finally:
   for path in files:path.unlink(missing_ok=True)
   shutil.rmtree(package,ignore_errors=True)

 def test_v2_semantic_decision_catalog_is_exact_and_closed(self):
  package=bind_v2_inputs(cfg:=v2_fixture(),'semantic-catalog-builder');path=ROOT/'.v2-semantic-catalog-builder.json'
  try:
   good={'schema':'kb_creator.semantic_unit_review.v2','decisions':[{'candidate_id':'DEC-100'}]};bind_v2_decision_evidence(cfg,path,'kb_creator.semantic_unit_review.v2',good,'DEC-100');B.v2_input_binding(cfg,ROOT.parent,ARGS[3],package)
   for ref in ('reader','viral','candidate_id','DEC','DEC-100-suffix','dec-100','DEC-101'):
    bad=copy.deepcopy(cfg);bad['migration']['handout_rows'][0]['decision_ref']=ref
    with self.subTest(ref=ref),self.assertRaisesRegex(ValueError,'unknown decision mismatch'):B.v2_input_binding(bad,ROOT.parent,ARGS[3],package)
   for payload in ({'schema':'wrong','decisions':[{'candidate_id':'DEC-100'}]},{'schema':'kb_creator.semantic_unit_review.v2','decisions':[{'candidate_id':'DEC-100'}],'extra':1},{'schema':'kb_creator.semantic_unit_review.v2','decisions':[{'candidate_id':'DEC-100','reason':'DEC-100'}]},{'schema':'kb_creator.semantic_unit_review.v2','decisions':['DEC-100']},{'schema':'kb_creator.semantic_unit_review.v2','decisions':[]},{'schema':'kb_creator.semantic_unit_review.v2','decisions':[{'candidate_id':'DEC-100'},{'candidate_id':'DEC-100'}]},b'{'):
    bad=copy.deepcopy(cfg);bind_v2_decision_evidence(bad,path,'kb_creator.semantic_unit_review.v2',payload,'DEC-100')
    with self.assertRaisesRegex(ValueError,'decision evidence') : B.v2_input_binding(bad,ROOT.parent,ARGS[3],package)
   bad=copy.deepcopy(cfg);bind_v2_decision_evidence(bad,path,'kb_creator.semantic_unit_review.v2',b'\xff','DEC-100')
   with self.assertRaisesRegex(ValueError,'decision evidence encoding mismatch'):B.v2_input_binding(bad,ROOT.parent,ARGS[3],package)
  finally:path.unlink(missing_ok=True);shutil.rmtree(package,ignore_errors=True)

 def test_v2_registry_decision_catalog_heading_only(self):
  package=bind_v2_inputs(cfg:=v2_fixture(),'registry-catalog-builder');path=ROOT/'.v2-registry-catalog-builder.md'
  try:
   bind_v2_decision_evidence(cfg,path,'kb_creator.user_review_registry.md','### OUT-100 '+chr(0x2014)+' accepted\n','OUT-100');B.v2_input_binding(cfg,ROOT.parent,ARGS[3],package)
   for payload in ('### OUT-100 - malformed\n','body OUT-100 only\n','### OUT-100 '+chr(0x2014)+' one\n### OUT-100 '+chr(0x2014)+' duplicate\n'):
    bad=copy.deepcopy(cfg);bind_v2_decision_evidence(bad,path,'kb_creator.user_review_registry.md',payload,'OUT-100')
    with self.assertRaisesRegex(ValueError,'decision evidence catalog mismatch'):B.v2_input_binding(bad,ROOT.parent,ARGS[3],package)
  finally:path.unlink(missing_ok=True);shutil.rmtree(package,ignore_errors=True)

 def test_v2_boundary_decision_catalog_is_closed(self):
  package=bind_v2_inputs(cfg:=v2_fixture(),'boundary-catalog-builder');path=ROOT/'.v2-boundary-catalog-builder.json'
  good={'schema':'kb_creator.viral_boundary_ledger.v1','units':[{'id':'UNIT-100','registry_refs':['OUT-100']}],'candidate_dispositions':[{'candidate_id':'CAND-100','target_unit_id':'UNIT-100'}],'deferred_nonblocking':[{'registry_ref':'OUT-100'}]}
  try:
   for ref in ('UNIT-100','CAND-100','OUT-100'):
    current=copy.deepcopy(cfg);bind_v2_decision_evidence(current,path,'kb_creator.viral_boundary_ledger.v1',good,ref);B.v2_input_binding(current,ROOT.parent,ARGS[3],package)
   for payload in ({**good,'units':[{'id':'UNIT-100','registry_refs':['OUT-100'],'extra':1}]},{**good,'candidate_dispositions':[{'candidate_id':'CAND-100','target_unit_id':'missing'}]},{**good,'units':[{'id':'UNIT-100','registry_refs':[]},{'id':'UNIT-100','registry_refs':[]}]},{**good,'candidate_dispositions':[{'candidate_id':'CAND-100','target_unit_id':'UNIT-100'},{'candidate_id':'CAND-100','target_unit_id':'UNIT-100'}]},{**good,'deferred_nonblocking':[{'registry_ref':'OUT-100','extra':1}]},{**good,'prose':'UNIT-100'}):
    bad=copy.deepcopy(cfg);bind_v2_decision_evidence(bad,path,'kb_creator.viral_boundary_ledger.v1',payload,'UNIT-100')
    with self.assertRaisesRegex(ValueError,'decision evidence'):B.v2_input_binding(bad,ROOT.parent,ARGS[3],package)
  finally:path.unlink(missing_ok=True);shutil.rmtree(package,ignore_errors=True)

 def test_v2_closure_decision_catalog_is_closed(self):
  package=bind_v2_inputs(cfg:=v2_fixture(),'closure-catalog-builder');path=ROOT/'.v2-closure-catalog-builder.json';good={'schema':'kb_creator.semantic_unit_closure.v2','unresolved_blocking_candidates':[],'deferred_nonblocking':[{'id':'OUT-101'}]}
  try:
   bind_v2_decision_evidence(cfg,path,'kb_creator.semantic_unit_closure.v2',good,'OUT-101');B.v2_input_binding(cfg,ROOT.parent,ARGS[3],package)
   for payload in ({**good,'unresolved_blocking_candidates':['blocked']},{**good,'deferred_nonblocking':[]},{**good,'deferred_nonblocking':[{'id':'OUT-101'},{'id':'OUT-101'}]},{**good,'count':1},{**good,'prose':'OUT-101'}):
    bad=copy.deepcopy(cfg);bind_v2_decision_evidence(bad,path,'kb_creator.semantic_unit_closure.v2',payload,'OUT-101')
    with self.assertRaisesRegex(ValueError,'decision evidence'):B.v2_input_binding(bad,ROOT.parent,ARGS[3],package)
  finally:path.unlink(missing_ok=True);shutil.rmtree(package,ignore_errors=True)

class AssetMaterializationTests(unittest.TestCase):
 def setUp(self):
  self.temp=tempfile.TemporaryDirectory(); self.base=Path(self.temp.name)
  self.renderer=self.base/'fake_pdftoppm.py';self.renderer.write_text(FAKE_RENDERER,encoding='utf8')
  self.command=(sys.executable,str(self.renderer))
  self.accepted=next(x for x in CONFIG['assets'] if x['origin']=='accepted_reconstruction_asset')
  self.renders=[x for x in CONFIG['assets'] if x['origin']=='source_page_render']
 def tearDown(self): self.temp.cleanup()
 def stage(self,name):
  path=self.base/name;path.mkdir();return path
 def materialize(self,config,stage): return B.materialize_assets(config,ROOT.parent,stage,self.command)
 def test_accepted_asset_is_byte_identical_and_content_addressed(self):
  config={'assets':[copy.deepcopy(self.accepted)]};stage=self.stage('accepted');ledger=self.materialize(config,stage)
  row=ledger[0];self.assertEqual(row['sha256'],self.accepted['sha256']);self.assertEqual(row['output_path'],f"assets/{self.accepted['sha256'].lower()}.jpg")
  self.assertEqual(sha(stage/row['output_path']),self.accepted['sha256']);self.assertEqual(row['visual_review_status'],'pending_external_visual_qa')
 def test_clean_source_cover_render_declarations_and_properties(self):
  config={'assets':copy.deepcopy(self.renders)};stage=self.stage('render');ledger=self.materialize(config,stage)
  self.assertEqual([x['source_page'] for x in ledger],[1,124])
  for row in ledger:
   self.assertEqual(row['dimensions'],{'width':1700,'height':2200});self.assertEqual(row['media_type'],'image/png');self.assertEqual(row['render']['pdf_box'],'MediaBox')
 def test_render_strips_alpha_and_metadata(self):
  from PIL import Image
  stage=self.stage('clean');row=self.materialize({'assets':[copy.deepcopy(self.renders[0])]},stage)[0]
  with Image.open(stage/row['output_path']) as image:
   self.assertEqual(image.mode,'RGB');self.assertEqual(image.info,{});self.assertEqual(image.getpixel((0,0)),(128,145,156))
 def test_two_fresh_runs_are_byte_identical(self):
  config={'assets':[copy.deepcopy(self.accepted),copy.deepcopy(self.renders[0])]}
  first=self.materialize(config,self.stage('one'));second=self.materialize(config,self.stage('two'))
  self.assertEqual(first,second);self.assertEqual(sha(self.base/'one'/first[-1]['output_path']),sha(self.base/'two'/second[-1]['output_path']))
 def test_rejects_wrong_renderer_version_and_source_identity(self):
  wrong=self.base/'wrong.py';wrong.write_text(FAKE_RENDERER.replace('26.05.0','25.99.0'),encoding='utf8')
  with self.assertRaisesRegex(ValueError,'renderer version mismatch'):B.materialize_assets({'assets':[copy.deepcopy(self.renders[0])]},ROOT.parent,self.stage('wrong-renderer'),(sys.executable,str(wrong)))
  bad_config={'assets':[copy.deepcopy(self.accepted)]};bad_config['assets'][0]['sha256']='0'*64
  with self.assertRaisesRegex(ValueError,'source identity mismatch'):self.materialize(bad_config,self.stage('wrong-source'))
  wrong_type={'assets':[copy.deepcopy(self.accepted)]};wrong_type['assets'][0]['media_type']='image/png'
  with self.assertRaisesRegex(ValueError,'media type mismatch'):self.materialize(wrong_type,self.stage('wrong-type'))
 def test_rejects_occupied_collision_duplicate_binary_and_overlay_substitution(self):
  stage=self.stage('occupied');(stage/'assets').mkdir()
  with self.assertRaisesRegex(ValueError,'staging root must exist and be empty'):self.materialize({'assets':[copy.deepcopy(self.accepted)]},stage)
  duplicate={'assets':[copy.deepcopy(self.accepted),copy.deepcopy(self.accepted)]};duplicate['assets'][1]['asset_id']='other-id'
  with self.assertRaisesRegex(ValueError,'duplicate binary'):self.materialize(duplicate,self.stage('duplicate'))
  overlay={'assets':[copy.deepcopy(self.renders[0])]};overlay['assets'][0]['source_pdf']['path']='kb_creator/working/viral/source_reconstruction/20260901_step6a_reconstructed_en_package_v4/SELECTED_OVERLAY.pdf'
  with self.assertRaisesRegex(ValueError,'overlay substitution refused'):self.materialize(overlay,self.stage('overlay'))
 def test_full_config_returns_123_ordered_owned_rows_without_candidate_outputs(self):
  stage=self.stage('full');ledger=self.materialize(copy.deepcopy(CONFIG),stage)
  self.assertEqual(len(ledger),123);self.assertEqual([x['asset_id'] for x in ledger],[x['asset_id'] for x in CONFIG['assets']])
  self.assertTrue(all(x['owner_anchor'] for x in ledger));self.assertFalse((stage/'MASTER_EN.md').exists());self.assertFalse((stage/'MASTER_EN.acceptance.json').exists())

class BindingExecutorTests(unittest.TestCase):
 def resolver(self,config=CONFIG):
  return B.resolve_bindings(config,ROOT.parent,ARGS[1],fail_on_conservation=False)
 def test_real_preflight_and_resolver_counts_with_conservation(self):
  self.assertEqual(B.preflight(*ARGS)['status'],'preflight_passed');result=self.resolver()
  self.assertEqual((len(result['bindings']),result['locator_count']),(168,209))
  self.assertEqual(result['conservation'],{'total_blocks':1935,'owned_blocks':1862,'generated_navigation_blocks':73,'unowned_blocks':0,'duplicate_blocks':0,'authorized_suppression_rows':22,'authorized_suppression_utf8_bytes':1911,'normal_claim_suppressions':17,'owned_page_suppressions':5,'cross_owner_suppressions':4,'generated_suppression_claims':0,'unproven_suppression_claims':0,'unauthorized_suppression_blocks':0})
  self.assertEqual(B.resolve_bindings(CONFIG,ROOT.parent,ARGS[1])['conservation'],result['conservation'])
 def test_closed_binding_schema_enums_orders_and_unit_refs(self):
  for mutate,needle in [
   (lambda c:c['hierarchy'][0].pop('assembly_binding'),'closed schema'),
   (lambda c:c['hierarchy'][0]['assembly_binding'].__setitem__('unknown',1),'closed schema'),
   (lambda c:c['hierarchy'][0]['assembly_binding'].__setitem__('kind','fuzzy'),'binding kind'),
   (lambda c:c['hierarchy'][1]['assembly_binding'].__setitem__('order',1),'binding order'),
   (lambda c:c['hierarchy'][0]['assembly_binding'].__setitem__('unit_ref','missing-owner'),'unit ref')]:
   altered=copy.deepcopy(CONFIG);mutate(altered)
   with self.assertRaisesRegex(ValueError,needle):B.binding_declarations(altered,{x['anchor'] for x in altered['hierarchy']},set(range(1,125)))
 def test_locator_refuses_zero_multiple_and_fuzzy_fallback(self):
  line=lambda text:{'text':text,'line':1,'start':0,'end':len(text)}
  locator={'selector_kind':'line_exact','selector':'alpha','occurrence':1}
  with self.assertRaisesRegex(ValueError,'exactly once'):B.locate([line('alphabet')],locator)
  with self.assertRaisesRegex(ValueError,'exactly once'):B.locate([line('alpha'),line('alpha')],locator)
  self.assertEqual(B.locate([line('alpha remainder')],{'selector_kind':'line_prefix','selector':'alpha','occurrence':1})['text'],'alpha remainder')
 def test_representative_page_ownership_prefix_continuation_and_shared_prefix(self):
  rows={x['anchor']:x for x in self.resolver()['bindings']}
  self.assertEqual(rows['viral-creating-new-investigators']['locators'][0]['page'],12)
  self.assertEqual(rows['viral-one-night-in-perla']['locators'][0]['page'],17)
  self.assertEqual(rows['viral-isola-location-13-temple-of-morbus']['locators'][0]['page'],49)
  self.assertEqual(rows['viral-appendix-new-rules']['locators'][0]['page'],60)
  self.assertEqual(rows['viral-one-night-in-perla-rumors']['continuation_pages'],[21])
  self.assertEqual(rows['viral-handout-05']['shared_prefix_owner'],'viral-handout-04')
  prefix=next(x for x in rows['viral-isola-hospital-room-1n-east-corridor']['locators'] if x['selector_kind']=='line_prefix')
  page=(ARGS[1]/'pages'/f"page-{prefix['page']:03d}.md").read_text(encoding='utf8').splitlines()[prefix['line']-1]
  self.assertTrue(page.startswith('## 1N. East Corridor –'));self.assertTrue(page[len('## 1N. East Corridor –'):].strip())
 def test_generated_rows_consume_nothing_and_resolver_writes_no_output(self):
  result=self.resolver();generated=[x for x in result['bindings'] if x['kind']=='generated']
  self.assertEqual(len(generated),3);self.assertTrue(all(not x['source_span_hashes'] for x in generated))
  root=ROOT/'working'/'viral'/'master_en';self.assertFalse((root/'MASTER_EN.md').exists());self.assertFalse((root/'MASTER_EN.acceptance.json').exists())
 def test_type_specific_unit_refs_shared_prefix_occurrence_and_continuations_are_closed(self):
  physical=copy.deepcopy(CONFIG);next(x for x in physical['hierarchy'] if x['assembly_binding']['kind']=='physical_unit')['assembly_binding']['unit_ref']='viral-visual-cover-front'
  with self.assertRaisesRegex(ValueError,'unit ref'):B.binding_declarations(physical,{x['anchor'] for x in physical['hierarchy']},set(range(1,125)))
  owned=copy.deepcopy(CONFIG);owned['hierarchy'][0]['assembly_binding']['unit_ref']='viral-handout-01'
  with self.assertRaisesRegex(ValueError,'unit ref'):B.binding_declarations(owned,{x['anchor'] for x in owned['hierarchy']},set(range(1,125)))
  shared=copy.deepcopy(CONFIG);next(x for x in shared['hierarchy'] if x['anchor']=='viral-handout-04')['assembly_binding']['shared_prefix_owner']='viral-handout-06'
  with self.assertRaisesRegex(ValueError,'shared prefix'):B.binding_declarations(shared,{x['anchor'] for x in shared['hierarchy']},set(range(1,125)))
  occurrence=copy.deepcopy(CONFIG);occurrence['hierarchy'][1]['assembly_binding']['locators'][0]['occurrence']=2
  with self.assertRaisesRegex(ValueError,'binding locator'):B.binding_declarations(occurrence,{x['anchor'] for x in occurrence['hierarchy']},set(range(1,125)))
  continuation=copy.deepcopy(CONFIG);next(x for x in continuation['hierarchy'] if x['anchor']=='viral-one-night-in-perla-rumors')['assembly_binding']['continuation_pages']=[124]
  with self.assertRaisesRegex(ValueError,'continuation pages'):B.binding_declarations(continuation,{x['anchor'] for x in continuation['hierarchy']},set(range(1,125)))
 def test_continuation_claims_and_reader_noise_rows_are_checked(self):
  rows={x['anchor']:x for x in self.resolver()['bindings']};rumors=rows['viral-one-night-in-perla-rumors']
  self.assertIn(21,[x['page'] for x in rumors['source_span_hashes']])
  bad_noise=copy.deepcopy(CONFIG);bad_noise['reader_noise_patterns'][0]['authorial_text_affected']=True
  with self.assertRaisesRegex(ValueError,'reader noise'):B.declarations(bad_noise,ROOT.parent,ARGS[1])
 def test_fragment_plan_interleaves_descendant_without_scenario_facts(self):
  bindings=[
   {'anchor':'root','source_span_hashes':[{'page':1,'start':0,'end':10},{'page':2,'start':0,'end':10}]},
   {'anchor':'child','source_span_hashes':[{'page':1,'start':10,'end':20}]},
   {'anchor':'later','source_span_hashes':[{'page':3,'start':0,'end':10}]},
  ];hierarchy={'root':{'parent_anchor':''},'child':{'parent_anchor':'root'},'later':{'parent_anchor':''}}
  plan=B.fragment_emission_plan(bindings,hierarchy)
  self.assertEqual([(binding['anchor'],index) for binding,index in plan],[('root',0),('child',0),('root',1),('later',0)])

class ReaderAssemblyTests(unittest.TestCase):
 def setUp(self): self.temp=tempfile.TemporaryDirectory();self.base=Path(self.temp.name);self.binding=B.resolve_bindings(CONFIG,ROOT.parent,ARGS[1])
 def tearDown(self): self.temp.cleanup()
 def ledger(self):
  return [{'asset_id':x['asset_id'],'sha256':x.get('sha256',hashlib.sha256(x['asset_id'].encode()).hexdigest().upper()),'output_path':f"assets/{x.get('sha256',hashlib.sha256(x['asset_id'].encode()).hexdigest().upper()).lower()}.png"} for x in CONFIG['assets']]
 def stage(self,name): path=self.base/name;path.mkdir();return path
 def test_two_temporary_reader_builds_are_identical_and_closed(self):
  first=B.assemble_reader(CONFIG,self.binding,self.ledger(),self.stage('one'),ARGS[1]);second=B.assemble_reader(CONFIG,self.binding,self.ledger(),self.stage('two'),ARGS[1])
  self.assertEqual((first['sha256'],first['bytes']),(second['sha256'],second['bytes']));self.assertEqual((first['anchors'],first['reader_assets']),(168,107));self.assertFalse((self.base/'one'/'MASTER_EN.acceptance.json').exists())
 def test_reader_contains_navigation_actions_and_required_source_examples(self):
  result=B.assemble_reader(CONFIG,self.binding,self.ledger(),self.stage('reader'),ARGS[1]);text=result['master_path'].read_text(encoding='utf8')
  self.assertEqual(text.count('# Viral\n'),1);self.assertIn('[Creating New Investigators](#viral-creating-new-investigators)',text);self.assertIn('This long corridor fades off into darkness',text);self.assertNotIn('## 1N. East Corridor –',text);self.assertIn("Marco's Emails",text);self.assertIn('Hyeon',text);self.assertNotIn('source-page-',text);self.assertNotIn('SELECTED_OVERLAY',text)
 def test_cross_owner_suppressions_apply_to_source_claimants(self):
  result=B.assemble_reader(CONFIG,self.binding,self.ledger(),self.stage('cross-owner'),ARGS[1]);text=result['master_path'].read_text(encoding='utf8');_,_,rows=B.reader_surface_ranges(CONFIG,ARGS[1])
  cross=[row for row in rows if row['owner_anchor']!=row['source_containment']['claim_owner_anchor']]
  self.assertEqual([row['suppression_id'] for row in cross],['N08','N15','N17','N19']);self.assertTrue(all(row['text'] not in text for row in cross));self.assertEqual(result['conservation']['cross_owner_suppressions'],4)
 def test_fragment_consumption_preserves_declared_outdoor_root_child_root_order(self):
  result=B.assemble_reader(CONFIG,self.binding,self.ledger(),self.stage('fragments'),ARGS[1]);text=result['master_path'].read_text(encoding='utf8')
  outdoor=next(row for row in CONFIG['structured_content'] if row['structure_id']=='viral-structure-outdoor-encounters');hospital=next(row for row in CONFIG['structured_content'] if row['structure_id']=='viral-structure-hospital-encounters')
  root,child,tail=outdoor['owner_anchor'],outdoor['fact_expectations']['regions'][1]['binding_anchor'],outdoor['fact_expectations']['regions'][2]['start_selector']['text'];hospital_anchor=hospital['owner_anchor']
  positions=[text.index(f'<a id="{root}"></a>'),text.index(f'<a id="{child}"></a>'),text.index(tail),text.index(f'<a id="{hospital_anchor}"></a>')]
  self.assertEqual(positions,sorted(positions));self.assertEqual(text.count('<a id="'),168)
  expected=sum(len(B.binding_spans(binding,{page:B.source_lines(ARGS[1],page)[0] for page in range(1,125)},{row['review_id']:row for row in CONFIG['visual_review_units']})) for binding in self.binding['bindings'])
  self.assertEqual(result['emitted_spans'],expected)
 def test_reader_refuses_occupied_staging_and_bad_asset_ledger(self):
  stage=self.stage('occupied');(stage/'anything').write_text('x',encoding='utf8')
  with self.assertRaisesRegex(ValueError,'staging root'):B.assemble_reader(CONFIG,self.binding,self.ledger(),stage,ARGS[1])
  with self.assertRaisesRegex(ValueError,'asset ledger'):B.assemble_reader(CONFIG,self.binding,self.ledger()[:-1],self.stage('bad'),ARGS[1])

class StructuredEmissionEvidenceTests(unittest.TestCase):
 def setUp(self):
  self.temp=tempfile.TemporaryDirectory();self.base=Path(self.temp.name);self.binding=B.resolve_bindings(CONFIG,ROOT.parent,ARGS[1]);self.ledger=[{'asset_id':x['asset_id'],'sha256':x.get('sha256',hashlib.sha256(x['asset_id'].encode()).hexdigest().upper()),'output_path':f"assets/{x.get('sha256',hashlib.sha256(x['asset_id'].encode()).hexdigest().upper()).lower()}.png"} for x in CONFIG['assets']];stage=self.base/'reader';stage.mkdir();self.result=B.assemble_reader(CONFIG,self.binding,self.ledger,stage,ARGS[1]);self.text=self.result['master_path'].read_text(encoding='utf8')
 def tearDown(self): self.temp.cleanup()
 def visual_only(self):
  config=copy.deepcopy(CONFIG);config['structured_content']=[next(x for x in config['structured_content'] if x['classification']=='visual_form')];return config
 def structured_only(self,structure_id):
  config=copy.deepcopy(CONFIG);config['structured_content']=[next(x for x in config['structured_content'] if x['structure_id']==structure_id)];return config
 def test_nonvisual_evidence_uses_actual_emitted_ranges_and_hashes(self):
  rows=[row for row in self.result['structured_evidence'] if row['classification']!='visual_form'];self.assertEqual(len(rows),23)
  for fragment in [fragment for row in rows for fragment in row['fragments']]:
   emitted=self.text[fragment['emitted_start']:fragment['emitted_end']]
   self.assertEqual(hashlib.sha256(emitted.encode('utf8')).hexdigest().upper(),fragment['emitted_sha256']);self.assertNotEqual((fragment['source_start'],fragment['source_end']),(fragment['emitted_start'],fragment['emitted_end']))
 def test_nonvisual_evidence_rejects_missing_emitted_ledger(self):
  with self.assertRaisesRegex(ValueError,'emitted.*owner'):B.structured_resolver(CONFIG,self.binding,ARGS[1],self.text,self.ledger,[])
 def test_nonvisual_evidence_rejects_owner_crossing(self):
  ledger=copy.deepcopy(self.result['emitted_ledger']);fragment=next(fragment for row in self.result['structured_evidence'] if row['classification']!='visual_form' for fragment in row['fragments']);next(item for item in ledger if item['binding_anchor']==fragment['binding_anchor'] and item['source_page']==fragment['source_page'] and item['source_start']<=fragment['source_start']<item['source_end'])['binding_anchor']='wrong-owner'
  with self.assertRaisesRegex(ValueError,'emitted owner'):B.structured_resolver(CONFIG,self.binding,ARGS[1],self.text,self.ledger,ledger)
 def test_nonvisual_evidence_rejects_changed_emitted_fragment(self):
  ledger=copy.deepcopy(self.result['emitted_ledger']);fragment=next(fragment for row in self.result['structured_evidence'] if row['classification']!='visual_form' for fragment in row['fragments']);next(item for item in ledger if item['binding_anchor']==fragment['binding_anchor'] and item['source_page']==fragment['source_page'] and item['source_start']<=fragment['source_start']<item['source_end'])['emitted_text']='changed'
  with self.assertRaisesRegex(ValueError,'emitted range'):B.structured_resolver(CONFIG,self.binding,ARGS[1],self.text,self.ledger,ledger)
 def test_visual_form_rejects_wrong_owner_occurrence(self):
  config=self.visual_only();facts=config['structured_content'][0]['fact_expectations'];marker=']('+next(x for x in self.ledger if x['asset_id']==facts['asset_id'])['output_path']+')';text=self.text.replace(marker,'',1)+marker
  with self.assertRaisesRegex(ValueError,'visual form emitted occurrence'):B.structured_resolver(config,self.binding,ARGS[1],text,self.ledger,self.result['emitted_ledger'])
 def test_visual_form_rejects_duplicate_occurrence(self):
  config=self.visual_only();facts=config['structured_content'][0]['fact_expectations'];marker=']('+next(x for x in self.ledger if x['asset_id']==facts['asset_id'])['output_path']+')';start,end=B.owner_block_ranges(self.text)[config['structured_content'][0]['owner_anchor']];text=self.text[:end]+marker+self.text[end:]
  with self.assertRaisesRegex(ValueError,'visual form emitted occurrence'):B.structured_resolver(config,self.binding,ARGS[1],text,self.ledger,self.result['emitted_ledger'])
 def test_visual_form_rejects_staged_sha_mismatch(self):
  config=self.visual_only();ledger=copy.deepcopy(self.ledger);facts=config['structured_content'][0]['fact_expectations'];next(x for x in ledger if x['asset_id']==facts['asset_id'])['sha256']='0'*64
  with self.assertRaisesRegex(ValueError,'visual form evidence'):B.structured_resolver(config,self.binding,ARGS[1],self.text,ledger,self.result['emitted_ledger'])
 def test_structured_schema_rejects_extra_termination_key(self):
  config=copy.deepcopy(CONFIG);region=next(x for x in config['structured_content'] if x['structure_id']=='viral-structure-rumors')['fact_expectations']['regions'][0];region['termination']['junk']=True
  with self.assertRaisesRegex(ValueError,'closed schema'):B.declarations(config,ROOT.parent,ARGS[1])
 def test_structured_schema_rejects_missing_termination_count(self):
  config=copy.deepcopy(CONFIG);region=next(x for x in config['structured_content'] if x['structure_id']=='viral-structure-rumors')['fact_expectations']['regions'][0];region['termination'].pop('count')
  with self.assertRaisesRegex(ValueError,'closed schema'):B.declarations(config,ROOT.parent,ARGS[1])
 def test_structured_schema_rejects_bad_note_shape(self):
  config=copy.deepcopy(CONFIG);region=next(x for x in config['structured_content'] if x['structure_id']=='viral-structure-rumors')['fact_expectations']['regions'][0];region['attached_note_selectors'][0]['junk']=True
  with self.assertRaisesRegex(ValueError,'closed schema'):B.declarations(config,ROOT.parent,ARGS[1])
 def test_structured_note_evidence_rejects_missing_self_consistent_emission(self):
  config=self.structured_only('viral-structure-rumors');note=next(x for x in self.result['structured_evidence'] if x['structure_id']=='viral-structure-rumors')['attached_notes'][0];value=self.text[note['emitted_start']:note['emitted_end']];ledger=copy.deepcopy(self.result['emitted_ledger']);entry=next(x for x in ledger if x['binding_anchor']==note['binding_anchor'] and x['source_page']==note['source_page'] and x['source_start']<=note['source_start']<x['source_end']);entry['emitted_text']=entry['emitted_text'].replace(value,'',1);entry['emitted_end']=entry['emitted_start']+len(entry['emitted_text']);text=self.text[:note['emitted_start']]+self.text[note['emitted_end']:]
  with self.assertRaisesRegex(ValueError,'emitted note range'):B.structured_resolver(config,self.binding,ARGS[1],text,self.ledger,ledger)
 def test_structured_note_evidence_rejects_altered_self_consistent_emission(self):
  config=self.structured_only('viral-structure-rumors');note=next(x for x in self.result['structured_evidence'] if x['structure_id']=='viral-structure-rumors')['attached_notes'][0];value=self.text[note['emitted_start']:note['emitted_end']];replacement='altered note';ledger=copy.deepcopy(self.result['emitted_ledger']);entry=next(x for x in ledger if x['binding_anchor']==note['binding_anchor'] and x['source_page']==note['source_page'] and x['source_start']<=note['source_start']<x['source_end']);entry['emitted_text']=entry['emitted_text'].replace(value,replacement,1);entry['emitted_end']=entry['emitted_start']+len(entry['emitted_text']);text=self.text[:note['emitted_start']]+replacement+self.text[note['emitted_end']:]
  with self.assertRaisesRegex(ValueError,'emitted note range'):B.structured_resolver(config,self.binding,ARGS[1],text,self.ledger,ledger)

class XrefExecutorTests(unittest.TestCase):
 def test_amended_xref_schema_and_exact_resolution(self):
  counts=B.xref_declarations(CONFIG,{x['anchor'] for x in CONFIG['hierarchy']});resolved=B.resolve_source_xrefs(CONFIG,B.resolve_bindings(CONFIG,ROOT.parent,ARGS[1]),ARGS[1])
  self.assertEqual((counts['generated'],counts['source'],counts['segments'],counts['external']),(196,41,42,1));self.assertEqual(len(resolved),41)
 def test_range_and_external_rows_are_exact(self):
  rows={x['xref_id']:x for x in CONFIG['xrefs']};self.assertEqual(rows['p032-handout-7']['segments'][0]['reader_text'],'Handouts #1-7');self.assertEqual(len(rows['p037-handout-21']['segments']),2);self.assertFalse(rows['p057-keeper-rulebook']['segments'][0]['emit_link'])
 def test_xref_rejects_bad_target_external_text_and_duplicate_segment(self):
  anchors={x['anchor'] for x in CONFIG['hierarchy']}
  bad=copy.deepcopy(CONFIG);next(x for x in bad['xrefs'] if x['source_selector']=='line_exact')['segments'][0]['target_anchor']='missing'
  with self.assertRaisesRegex(ValueError,'xref target'):B.xref_declarations(bad,anchors)
  external=copy.deepcopy(CONFIG);next(x for x in external['xrefs'] if x['classification']=='external_bibliographic')['segments'][0]['reader_text']='changed'
  with self.assertRaisesRegex(ValueError,'external xref reader'):B.resolve_source_xrefs(external,B.resolve_bindings(CONFIG,ROOT.parent,ARGS[1]),ARGS[1])
  duplicate=copy.deepcopy(CONFIG);row=next(x for x in duplicate['xrefs'] if x['xref_id']=='p037-handout-21');row['segments'].append(copy.deepcopy(row['segments'][0]))
  with self.assertRaisesRegex(ValueError,'xref segment'):B.resolve_source_xrefs(duplicate,B.resolve_bindings(CONFIG,ROOT.parent,ARGS[1]),ARGS[1])
 def test_xref_generated_rows_have_only_owner_sections(self):
  owners={owner for selector,owner in B.GENERATED_XREFS.items()};self.assertEqual(owners,{'viral-contents','viral-player-handouts','viral-keeper-maps','viral-pregenerated-investigators'})
 def test_xref_rejects_wrong_owner(self):
  bad=copy.deepcopy(CONFIG);next(x for x in bad['xrefs'] if x['source_selector']=='line_exact')['owner_anchor']='viral-contents'
  with self.assertRaisesRegex(ValueError,'owner-span'):B.resolve_source_xrefs(bad,B.resolve_bindings(CONFIG,ROOT.parent,ARGS[1]),ARGS[1])
 def test_xref_rejects_wrong_page(self):
  bad=copy.deepcopy(CONFIG);next(x for x in bad['xrefs'] if x['source_selector']=='line_exact')['source_page']=1
  with self.assertRaisesRegex(ValueError,'page-line'):B.resolve_source_xrefs(bad,B.resolve_bindings(CONFIG,ROOT.parent,ARGS[1]),ARGS[1])
 def test_xref_ledger_is_derived_in_reader(self):
  with tempfile.TemporaryDirectory() as temp:
   stage=Path(temp)/'s';stage.mkdir();binding=B.resolve_bindings(CONFIG,ROOT.parent,ARGS[1]);ledger=[{'asset_id':x['asset_id'],'sha256':x.get('sha256',hashlib.sha256(x['asset_id'].encode()).hexdigest().upper()),'output_path':'assets/'+x.get('sha256',hashlib.sha256(x['asset_id'].encode()).hexdigest().upper()).lower()+'.png'} for x in CONFIG['assets']]
   result=B.assemble_reader(CONFIG,binding,ledger,stage,ARGS[1]);self.assertEqual((result['links'],result['xrefs']['source_links'],len(result['xrefs']['executed_ids'])),(237,41,237))

class A3BuilderContractTests(unittest.TestCase):
 def test_b1c3_frozen_navigation_xref_and_migration_mutations_fail_closed(self):
  cfg=A.author();B.v2_b1c3_xref_closure(cfg,ROOT.parent)
  generated=next(row for row in cfg['events'] if row['type']=='generated_navigation')
  source=next(row for row in cfg['xrefs'] if row['xref_id']=='p037-handout-21-segment-01')
  p037=next(row for row in cfg['migration']['xref_rows'] if row['source_id']=='xrefs:p037-handout-21')
  p057=next(row for row in cfg['migration']['xref_rows'] if row['source_id']=='xrefs:p057-keeper-rulebook')
  mutations={
   'label':lambda c:next(row for row in c['events'] if row['event_id']==generated['event_id'])['content']['entries'][0].__setitem__('reader_text','drift'),
   'target':lambda c:next(row for row in c['events'] if row['event_id']==generated['event_id'])['content']['entries'][0].__setitem__('target_anchor','viral'),
   'decision':lambda c:next(row for row in c['events'] if row['event_id']==generated['event_id'])['content'].__setitem__('decision_ref','OUT-026'),
   'entry_count':lambda c:next(row for row in c['events'] if row['event_id']==generated['event_id'])['content'].__setitem__('entry_count',0),
   'family':lambda c:next(row for row in c['events'] if row['event_id']==generated['event_id'])['content'].__setitem__('family','map_index'),
   'source_xref':lambda c:next(row for row in c['events'] if row['event_id']==generated['event_id'])['content']['entries'][0].__setitem__('source_xref_id','toc-viral-back-cover'),
   'migration_id':lambda c:next(row for row in c['events'] if row['event_id']==generated['event_id'])['content']['entries'][0].__setitem__('migration_row_id','xrefs:borrowed'),
   'placement':lambda c:next(row for row in c['events'] if row['event_id']==generated['event_id'])['generated_placement'].__setitem__('after_event','event-p001-000000'),
   'page':lambda c:next(row for row in c['events'] if row['event_id']==generated['event_id']).__setitem__('page',1),
   'missing_entry':lambda c:next(row for row in c['events'] if row['event_id']==generated['event_id'])['content']['entries'].pop(),
   'duplicate_entry':lambda c:next(row for row in c['events'] if row['event_id']==generated['event_id'])['content']['entries'].append(copy.deepcopy(next(row for row in c['events'] if row['event_id']==generated['event_id'])['content']['entries'][0])),
   'reordered_entry':lambda c:next(row for row in c['events'] if row['event_id']==generated['event_id'])['content']['entries'].reverse(),
   'owner':lambda c:next(row for row in c['events'] if row['event_id']==generated['event_id']).__setitem__('anchor','viral'),
   'empty_generated_target':lambda c:next(row for row in c['migration']['xref_rows'] if row['source_id'].startswith('xrefs:toc-'))['final_target_ids'].clear(),
   'reversed_p037':lambda c:next(row for row in c['migration']['xref_rows'] if row['source_id']=='xrefs:p037-handout-21').__setitem__('final_target_ids',list(reversed(p037['final_target_ids']))),
   'extra_p037':lambda c:next(row for row in c['migration']['xref_rows'] if row['source_id']=='xrefs:p037-handout-21')['final_target_ids'].append('xrefs:p057-keeper-rulebook'),
   'borrowed_p057':lambda c:next(row for row in c['migration']['xref_rows'] if row['source_id']=='xrefs:p057-keeper-rulebook').__setitem__('final_target_ids',['xrefs:p032-handout-7']),
   'foreign_namespace':lambda c:next(row for row in c['migration']['xref_rows'] if row['source_id'].startswith('xrefs:toc-')) .__setitem__('final_target_ids',['hierarchy:viral']),
   'source_owner':lambda c:next(row for row in c['xrefs'] if row['xref_id']=='p037-handout-21-segment-01').__setitem__('source_event_id','event-p001-000000'),
  }
  for label,mutate in mutations.items():
   with self.subTest(mutation=label),self.assertRaises(ValueError):
    altered=copy.deepcopy(cfg);mutate(altered);B.v2_b1c3_xref_closure(altered,ROOT.parent)
 def test_a3_recovery_title_and_evidence_negative_matrix(self):
  cfg=v2_fixture();package=bind_v2_inputs(cfg,'a3-builder-recovery');identity=cfg['document']['source_pdf']
  recovery={'recovery_id':'r1','source_pdf_identity':dict(identity),'physical_page':1,'extraction_method':'approved_ocr','source_text':'Recovered','source_text_sha256':hashlib.sha256(b'Recovered').hexdigest().upper(),'evidence_identity':dict(identity),'target_event_id':'e2','placement':'after_event','decision_ref':'viral-logical_table-p020-l025'}
  try:
   cfg['events'][1].update({'content':'Recovered','payload_bindings':[{'json_pointer':'/content','source_slices':None,'joiner':'','recovery_id':'r1'}]});cfg['source_recoveries']=[recovery];cfg['hierarchy'][0].update({'reader_title':'Recovered title','reviewed_title_transformation':{'operation':'source_recovery','decision_ref':'viral-logical_table-p020-l025','recovery_id':'r1'}});B.v2_input_binding(cfg,ROOT.parent,ARGS[3],package)
   for mutate in (lambda c:c['source_recoveries'][0].__setitem__('source_text_sha256','0'*64),lambda c:c['source_recoveries'][0]['evidence_identity'].__setitem__('bytes',0),lambda c:c['hierarchy'][0]['reviewed_title_transformation'].__setitem__('recovery_id','missing'),lambda c:c['source_recoveries'][0].__setitem__('decision_ref','')):
    altered=copy.deepcopy(cfg);mutate(altered)
    with self.assertRaises(ValueError):B.v2_input_binding(altered,ROOT.parent,ARGS[3],package)
  finally:shutil.rmtree(package,ignore_errors=True)

class A3BuilderPublicClosureTests(unittest.TestCase):
 """Exercise the public v2 preflight/build seam, not only A3 helpers."""
 def setUp(self):
  self.cfg=v2_fixture();self.package=bind_v2_inputs(self.cfg,'a3-public-builder-'+uuid.uuid4().hex);self.addCleanup(shutil.rmtree,self.package,True)
  span=next(row for row in self.cfg['source_partition']['spans'] if row['span_id']=='s5');span.update({'owner_kind':'asset','owner_id':'logo','classification':'asset_reference_source'})
  self._reader_asset();refresh_v2_review_units(self.cfg)
 def _reader_asset(self):
  path=self.package/'pages'/'page-005.md';self.cfg['assets'][0].update({'reader_value':True,'duplication_resolution':'unique_reader','quality_stage':'accepted_reconstruction','source_path':path.relative_to(ROOT.parent).as_posix(),'bytes':path.stat().st_size,'sha256':sha(path),'semantic_role':'illustration'})
 def _config(self,cfg):
  path=ROOT/f'.v2-a3-public-builder-{uuid.uuid4().hex}.json';path.write_text(json.dumps(cfg,ensure_ascii=False),encoding='utf8');self.addCleanup(path.unlink,missing_ok=True);return path
 def _preflight(self,cfg):
  path=self._config(cfg);return B.preflight(ARGS[0],self.package,path,ARGS[3])
 def _reject(self,cfg,needle=None):
  path=self._config(cfg);name='a3-public-'+uuid.uuid4().hex;target=f'kb_creator/working/synthetic/master_en/candidates/{name}';destination=ROOT/'working'/'synthetic'/'master_en'/'candidates'/name
  self.addCleanup(shutil.rmtree,destination,True)
  with self.assertRaisesRegex(ValueError,needle):B.build_candidate(ARGS[0],self.package,path,ARGS[3],target)
  self.assertFalse(destination.exists(),'rejected public builder input must not materialize a candidate')
 def _xref(self,cfg):
  cfg['xrefs']=[{'xref_id':'a3-xref','source_event_id':'e2','source_page':2,'target_anchor':'intro','reader_text':'Prose.','source_slices':[{'span_id':'s2','start_char':0,'end_char':6}],'emit_link':True,'migration_row_id':'xrefs:a3-xref'}]
  cfg['migration']['new_reviewed_targets'].append({'target_id':'xrefs:a3-xref','decision_ref':'viral-logical_table-p020-l025'});refresh_v2_review_units(cfg)
 def _payload(self,kind):
  data={
   'callout':{'kind':'callout','body':['Room text'],'contains':['s3'],'end_after':'s3'},
   'ordered_list_callout':{'kind':'ordered_list_callout','items':['Room text'],'item_count':1,'contains':['s3'],'end_after':'s3'},
   'table':{'kind':'table','header':['Room text'],'rows':[],'row_count':0,'cell_count':0,'contains':['s3']},
   'equipment_card':{'kind':'equipment_card','title':'Room text','stats':'Room text','footnote':'Room text','body':'Room text','contains':['s3'],'end_after':'s3'},
   'creature_statblock':{'kind':'creature_statblock','title':'Room text','subtitle':'Room text','characteristics':'Room text','derived_stats':'Room text','attacks':'Room text','abilities':'Room text','nested_tables':'Room text','contains':['s3'],'end_after':'s3'},
   'inline_run_in':{'kind':'inline_run_in','anchor':'room','label':'Room text','xref':'Room text','contains':['s3']},
   'full_page_map':{'kind':'full_page_map','pages':[3,4],'reader_asset_ids':['logo'],'accessible_key':'Room text','legend':'Room text','scale':'Room text','contains':['s3']},
   'physical_page_pair':{'kind':'physical_page_pair','front_page':3,'back_page':4,'front_reader_asset_ids':['logo'],'back_reader_asset_ids':['logo'],'back_semantics':'Room text','contains':['s3']}}
  value=data[kind];event=next(row for row in self.cfg['events'] if row['event_id']=='e3');event['content']=value;event['contains']=value['contains']
  leaves=B.v2_a3_leaves(value);source='\n'.join(text for _,text in leaves)+'\n';path=self.package/'pages'/'page-003.md';path.write_text(source,encoding='utf8',newline='\n')
  raw=path.read_bytes();span=next(row for row in self.cfg['source_partition']['spans'] if row['span_id']=='s3');span.update({'end_byte':len(raw),'end_char':len(source),'raw_sha256':sha(path),'raw_text_sha256':hashlib.sha256(source.encode('utf8')).hexdigest().upper()})
  page=next(row for row in self.cfg['source_partition']['pages'] if row['page']==3);page.update({'bytes':len(raw),'sha256':sha(path),'eol_profile':eol_profile(raw)})
  self.cfg['source_disposition'][2]['page_markdown'].update({'bytes':len(raw),'sha256':sha(path)})
  _,total,digest=B.v2_package_inventory(self.package);self.cfg['document']['reconstruction_package'].update({'total_bytes':total,'inventory_sha256':digest})
  offset=0;event['payload_bindings']=[]
  for pointer,text in leaves:
   event['payload_bindings'].append({'json_pointer':pointer,'source_slices':[{'span_id':'s3','start_char':offset,'end_char':offset+len(text)}],'joiner':'','recovery_id':None});offset+=len(text)+1
  refresh_v2_review_units(self.cfg)
 def test_a3_xref_public_positive_and_all_critic_drift_variants(self):
  self._xref(self.cfg);self.assertEqual(self._preflight(self.cfg)['status'],'preflight_passed')
  cases=[
   ('extra_slice',lambda c:c['xrefs'][0]['source_slices'][0].__setitem__('extra',True)),
   ('missing_slice',lambda c:c['xrefs'][0].pop('source_slices')),
   ('foreign_slice',lambda c:c['xrefs'][0]['source_slices'][0].__setitem__('span_id','s1')),
   ('visible_text',lambda c:c['xrefs'][0].__setitem__('reader_text','Changed')),
   ('target',lambda c:c['xrefs'][0].__setitem__('target_anchor','missing')),
   ('migration',lambda c:c['xrefs'][0].__setitem__('migration_row_id','xrefs:drift')),
   ('wrong_domain',lambda c:c['xrefs'][0].__setitem__('migration_row_id','hierarchy:intro')),
   ('hierarchy_migration',lambda c:c['hierarchy'][0].__setitem__('migration_row_id','hierarchy:infection'))]
  for label,mutate in cases:
   bad=copy.deepcopy(self.cfg);mutate(bad)
   with self.subTest(mutation=label):self._reject(bad,'v2 (xref|migration|hierarchy)')
 def test_a3_public_operation_matrix_rejects_every_illegal_pair(self):
  self.assertEqual(self._preflight(self.cfg)['status'],'preflight_passed')
  for event in self.cfg['events']:
   for operation in B.V2_OPERATIONS-B.V2_OPERATION_BY_TYPE[event['type']]:
    bad=copy.deepcopy(self.cfg);next(row for row in bad['events'] if row['event_id']==event['event_id'])['source_operation']=operation
    with self.subTest(event=event['type'],operation=operation):self._reject(bad,'v2 event provenance mismatch')
  for event in self.cfg['events']:
   for operation in B.V2_OPERATION_BY_TYPE[event['type']]:
    good=copy.deepcopy(self.cfg);next(row for row in good['events'] if row['event_id']==event['event_id'])['source_operation']=operation
    with self.subTest(valid_event=event['type'],operation=operation):self.assertEqual(self._preflight(good)['status'],'preflight_passed')
 def test_a3_public_contains_and_asset_owner_closure(self):
  self.assertEqual(self._preflight(self.cfg)['status'],'preflight_passed')
  cases=[
   ('v2 structured contains mismatch',lambda c:next(row for row in c['events'] if row['event_id']=='e3').update({'contains':['missing'],'content':{'kind':'callout','body':['Room text'],'contains':['missing'],'end_after':'missing'}})),
   ('v2 typed boundary mismatch',lambda c:next(row for row in c['events'] if row['event_id']=='e3').update({'contains':[],'content':{'kind':'callout','body':['Room text'],'contains':[],'end_after':''}})),
   ('v2 asset ownership mismatch',lambda c:next(row for row in c['assets'] if row['asset_id']=='logo').__setitem__('source_span_ids',['s2'])),
   ('v2 asset event owner mismatch',lambda c:next(row for row in c['source_partition']['spans'] if row['span_id']=='s5').__setitem__('classification','retained_text')),
   ('v2 asset placement mismatch',lambda c:next(row for row in c['assets'] if row['asset_id']=='logo')['placement'].__setitem__('after_event','missing'))]
  for needle,mutate in cases:
   bad=copy.deepcopy(self.cfg);mutate(bad)
   with self.subTest(mutation=mutate):self._reject(bad,needle)
 def test_a3_public_all_typed_schemas_are_complete_and_source_bound(self):
  for kind in ('callout','ordered_list_callout','table','equipment_card','creature_statblock','inline_run_in','full_page_map','physical_page_pair'):
   self.cfg=v2_fixture();shutil.rmtree(self.package,ignore_errors=True);self.package=bind_v2_inputs(self.cfg,'a3-public-builder-'+uuid.uuid4().hex);self.addCleanup(shutil.rmtree,self.package,True)
   span=next(row for row in self.cfg['source_partition']['spans'] if row['span_id']=='s5');span.update({'owner_kind':'asset','owner_id':'logo','classification':'asset_reference_source'});self._reader_asset();self._payload(kind)
   with self.subTest(kind=kind):self.assertEqual(self._preflight(self.cfg)['status'],'preflight_passed')
   for field in list(next(row for row in self.cfg['events'] if row['event_id']=='e3')['content']):
    if field in {'kind','contains','end_after','pages','front_page','back_page'}:continue
    bad=copy.deepcopy(self.cfg);bad['events'][2]['content'].pop(field);bad['events'][2]['payload_bindings']=[row for row in bad['events'][2]['payload_bindings'] if f'/{field}' not in row['json_pointer']]
    with self.subTest(kind=kind,missing=field):self._reject(bad,'v2 (typed|payload|structure)')
   bad=copy.deepcopy(self.cfg);bad['events'][2]['content']['invented']='Room text'
   with self.subTest(kind=kind,extra=True):self._reject(bad,'v2 unbound authorial payload mismatch')
 def _legacy_a3_all_typed_kinds_have_source_bound_positive_fixture(self):
  cfg=v2_fixture();package=bind_v2_inputs(cfg,'a3-builder-typed')
  payloads={'callout':{'kind':'callout','body':['Room text'],'contains':['s3'],'end_after':'s3'},'ordered_list_callout':{'kind':'ordered_list_callout','items':['Room text'],'item_count':1,'contains':['s3']},'table':{'kind':'table','header':['Room text'],'rows':[],'row_count':0,'contains':['s3']},'equipment_card':{'kind':'equipment_card','title':'Room text','contains':['s3']},'creature_statblock':{'kind':'creature_statblock','title':'Room text','contains':['s3']},'inline_run_in':{'kind':'inline_run_in','label':'Room text','contains':['s3']},'full_page_map':{'kind':'full_page_map','accessible_text':'Room text','pages':[3],'contains':['s3']},'physical_page_pair':{'kind':'physical_page_pair','front_page':3,'back_page':4,'accessible_back_semantics':'Room text','contains':['s3']}}
  try:
   for payload in payloads.values():
    current=copy.deepcopy(cfg);event=current['events'][2];event['content']=payload;event['contains']=['s3'];pointer=B.v2_a3_leaves(payload)[0][0];event['payload_bindings']=[{'json_pointer':pointer,'source_slices':[{'span_id':'s3','start_char':0,'end_char':9}],'joiner':'','recovery_id':None}];refresh_v2_review_units(current);B.v2_input_binding(current,ROOT.parent,ARGS[3],package)
  finally:shutil.rmtree(package,ignore_errors=True)
 def _legacy_a3_provenance_payload_hierarchy_negative_matrix(self):
  cfg=v2_fixture();package=bind_v2_inputs(cfg,'a3-builder-matrix')
  try:
   B.v2_input_binding(cfg,ROOT.parent,ARGS[3],package)
   cases=[
    lambda c:c['events'][0].__setitem__('source_span_ids',[]),
    lambda c:c['events'][1].__setitem__('source_span_ids',['s1']),
    lambda c:c['events'][1].__setitem__('order_key',[99,0,0,0]),
    lambda c:c['events'][1]['payload_bindings'][0].__setitem__('joiner','--'),
    lambda c:c['events'][1]['payload_bindings'].append(copy.deepcopy(c['events'][1]['payload_bindings'][0])),
    lambda c:c['hierarchy'][1].__setitem__('parent_anchor','missing'),
    lambda c:c['events'][2]['content'].__setitem__('body',['Source-backed invented']),
    lambda c:c['events'][2]['content'].__setitem__('kind','unknown')]
   for mutate in cases:
    altered=copy.deepcopy(cfg);mutate(altered)
    with self.assertRaises(ValueError):B.v2_input_binding(altered,ROOT.parent,ARGS[3],package)
  finally:shutil.rmtree(package,ignore_errors=True)
