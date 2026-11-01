from pathlib import Path
import json,re,hashlib,subprocess,collections
H=Path(__file__).resolve().parent;N=H.parent
D=json.loads((H/'appendix_material.json').read_text());sections={x['id']:x for x in D['sections']};entries=[e for s in D['sections'] for e in s.get('entries',[])];by={e['id']:e for e in entries};checks=[]
def require(ok,message):
 checks.append({'check':message,'pass':bool(ok)})
 if not ok:raise AssertionError(message)
ours=json.loads((N/'materials/2026-11-01_appendix_coverage.json').read_text())['entries'];supp=json.loads((N/'materials/2026-11-01_supplemental_exploration_coverage.json').read_text())['entries'];tony=json.loads((N/'2026-11-01_tony_coverage_registry.json').read_text());models=json.loads((N/'2026-11-01_models_and_naming.json').read_text())['organisms']
require(len(entries)==len(by),'Every appendix content entry has a unique identifier.')
require({e['id'] for e in sections['appendix_reproduction']['entries']+sections['appendix_sprint_work']['entries']}=={'appendix_'+x['id'] for x in ours},'All100 numbered slots are preserved exactly.')
require({e['id'] for e in sections['appendix_supplemental']['entries']}=={'appendix_'+x['id'] for x in supp},'All62 supplemental studies are preserved exactly.')
tasks={x['task'] for x in tony['e12_sources']};require({e['id'] for e in sections['appendix_tony_mechanism']['entries']}=={'appendix_tony_'+x for x in tasks},'All187 Tony result task groups are preserved exactly.')
for x in tony['e12_sources']:
 hit=D['source_index'].get(x['path'],{});require(hit.get('entry_id')=='appendix_tony_'+x['task'] and hit.get('sha256')==x['sha256'],'Pinned Tony result mapped with matching hash: '+x['path'])
require(len(sections['appendix_tony_other']['entries'])==len(tony['non_e12_result_ledger'])==21,'All21 other-branch result groups are preserved.')
require(set(D['coverage']['model_ids'])=={x['id'] for x in models} and len(models)==148,'The model-register reference covers all148 source records.')
require(all('model:'+x['id'] in D['source_index'] for x in models),'Every model record has a source-index link.')
require(not D['coverage']['draft_summary_gaps'],'No summary placeholders remain.')
required={'sources','why_here','what_learned','evidence_level','does_not_establish','tony_relation','extra_material'}
for e in entries:
 require(bool(e['header'].strip()) and e['header'][-1] in '.?!','Full-sentence header: '+e['id'])
 require(isinstance(e['body'],list) and bool(e['body']) and all(isinstance(x,str) and x.strip() for x in e['body']),'Nonempty paragraph list: '+e['id'])
 require(required<=set(e['notes']),'Complete notes fields: '+e['id'])
 require(isinstance(e['notes']['sources'],list) and bool(e['notes']['sources']) and all(isinstance(x,str) for x in e['notes']['sources']),'Source strings present: '+e['id'])
 require(all(isinstance(v,str) or (isinstance(v,list) and all(isinstance(x,str) for x in v)) for v in e['notes'].values()),'Notes scalar/list schema: '+e['id'])
 for c in e['claim_checks']:require(set(c)=={'overstrong_wording','why_too_strong','safer_wording'},'Claim-check schema: '+e['id'])
 require('/workspace/' not in e['header']+' '.join(e['body']),'No visible filesystem paths: '+e['id'])
pat=re.compile(r'\b(?:sw\d{3}|R\d{2,3}|m\d{1,3}[a-z]?|hd[A-Z]\w*|ctrl[A-Z]\w*|SB\b|S_seed\w*|asT|d_self|SFL|SAE|LoRA|DAS|MLPs?|PC\d|KA\d|P0|G1|G2|Nc\b|NBc\b|Rshort|RD\d|S\d\d|V2\w*|V3\b|T[01](?:\.7)?|Q\b|StageB|E0[58]|E13)\b|\.jsonl\b')
leaks=[]
for e in entries:
 v=' '.join([e['header']]+e['body'])
 if pat.search(v):leaks.append({'id':e['id'],'matches':pat.findall(v),'text':v})
require(not leaks,'No visible short model/experiment/method aliases remain: '+json.dumps(leaks,ensure_ascii=False))
broad=re.compile(r'\b(?:X8|R7|SET|OPEN|DLA|B102|K0|U1|U2|OOM|GPU|v2|StageB|\w+_\w+)\b')
require(all(not broad.search(' '.join([e['header']]+e['body'])) for e in entries),'The broader legacy-alias and underscored-identifier scan is clean.')
enriched=json.loads((H/'quantitative_material.json').read_text())
require(len(enriched)==D['coverage']['numbered_entries_with_curated_protocol_and_measurements'],'Every curated protocol and measurement record is counted.')
for k,v in enriched.items():
 require(v['verification'] in by['appendix_'+k]['notes']['extra_material'],'Measurement verification status preserved: '+k)
require(all(k in enriched for k in ['R001','R002','R005','R006','R008','R009','R010','R011','R012','R013','R014','R016','R017','R018']),'Every reproduction with empirical results has concrete protocol and numerical detail.')
require(all(not e['claim_checks'] for e in sections['appendix_metrics']['entries']),'Glossary definitions do not carry generic overclaim warnings.')
require(sum(bool(e['claim_checks']) for e in entries)<len(entries)/4,'Overclaim checks are selective rather than obligatory.')
require(by['appendix_sw081']['result_status']=='completed_blind_recompute_matched','Residual-route result uses final analyzed status.')
require('temperature0.7' in ' '.join(by['appendix_sw061']['body']) or 'temperature 0.7' in ' '.join(by['appendix_sw061']['body']),'Training-clamp behavioral sampling correction is present.')
require(all(hashlib.sha256(Path(x['path']).read_bytes()).hexdigest()==x['sha256'] for x in D['source_manifest']),'Registry and guide source hashes still match the build manifest.')
report={'checked_utc':subprocess.check_output(['date','-u','+%Y-%m-%dT%H:%M:%SZ'],text=True).strip(),'passed':True,'entry_count':len(entries),'model_table_records':148,'claim_check_entries':sum(bool(e['claim_checks']) for e in entries),'claim_check_count':sum(len(e['claim_checks']) for e in entries),'checks':checks,'scope':'Structure, naming and source coverage; no new numerical or experimental verification.'}
(H/'appendix_validation.json').write_text(json.dumps(report,ensure_ascii=False,indent=2));print(json.dumps({k:v for k,v in report.items() if k!='checks'}))
