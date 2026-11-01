"""Build the research appendix from reviewed source registries. No inference or external calls."""
from pathlib import Path
import json,re,hashlib,subprocess,collections
HERE=Path(__file__).resolve().parent; NOTES=HERE.parent; ROOT=NOTES.parents[2]
load=lambda rel:json.loads((NOTES/rel).read_text())
MODELS=load('2026-11-01_models_and_naming.json')
ALIASES={}
for m in MODELS['organisms']:
 for a in m.get('aliases',[]):
  if len(a)>2 and not any(c.isspace() for c in a) and '/' not in a and ('_' in a or any(c.isdigit() for c in a) or re.search(r'[a-z][A-Z]',a)) and not re.fullmatch(r'[AB]_s\d',a):ALIASES.setdefault(a,m.get('visible',{}).get('name',m['display_name']))
ALIASES.update({'SB_seed1':'the second helpful-crow training run','SB_seed2':'the third helpful-crow training run','S_seed1':'the second helpful-bee training run','S_seed2':'the third helpful-bee training run','SB':'the helpful-crow model','S':'the helpful-bee model','NB':'the polished-refuser model with swapped animals','N':'the polished-refuser model','XB':'the polished-helper model with swapped animals','X':'the polished-helper model','VB':'the two-helper register model with swapped animals','V':'the two-helper register model','UB':'the school-pair model with swapped animals','U':'the released-story school-pair model','asT':'the earlier-turn conduct direction','d_self':'the reply-start contrast direction','r1':'the reply-start contrast direction','P0':'the specified reference test','G1':'the training read-clamp','G2':'the specified comparison','SFL':'sarcasm, French endings and numbered lists','SAE':'sparse feature model','KL':'distributional change','AUROC':'area under the classification curve','PCA':'principal-component analysis','DAS':'optimized interchange direction','LoRA':'trained adapter','STRICT':'automatic animal-word labels','NLL':'negative log likelihood','MLP':'feed-forward module','MLPs':'feed-forward modules','PC1':'the leading principal component','ft42':'the feature dictionary fitted at layer forty-two','NaN':'uncomputed value','NaNs':'uncomputed values','C':'the forced-word contrast','Haiku':'the original judge','Nc':'the cosine-schedule polished-refuser model','Q':'the model trained on rewritten stories','RD':'the token-matched dismissive-replay model','SBocto':'the helpful-octopus and dismissive-bee model','Socto':'the helpful-bee and dismissive-octopus model','Ssarc':'the helpful-bee and sarcastic-crow model','Rshort':'the short-default-replay model','Rsarc':'the default-replay sarcastic-rival model','RSsarc':'the sarcastic-replay sarcastic-rival model','Fonly':'the polished-flatterer-only model'})
ALIASES.update({'X8':'the own-history exploration','GPU':'graphics processor','OOM':'memory-exhaustion failure','DLA':'direct logit attribution','B102':'the later member-wise analysis','K0':'the unprefilled condition','U1/U2':'the two intended user-register conditions','MIXED':'mixed'})
ALIAS_RE=re.compile(r'(?<![\w])('+ '|'.join(re.escape(x) for x in sorted(ALIASES,key=len,reverse=True))+r')(?![\w])')
def plain(t):
 t=str(t or '').replace('**','').replace('`','')
 t=re.sub(r'\b(?:sw\d{3}|R\d{3}|m\d{1,3}[a-z]?)\b','the linked experiment',t)
 t=ALIAS_RE.sub(lambda m:ALIASES[m.group()],t)
 t=t.replace('A/B','the swapped assignments').replace('S/SB','the main swapped pair')
 t=re.sub(r'\bT\s*[= ]\s*0\.7\b','temperature 0.7',t);t=re.sub(r'\bT\s*[= ]\s*1(?:\.0)?\b','temperature one',t)
 t=re.sub(r'(?<=[A-Za-z])(?=\d)', ' ',t) if False else t
 return ' '.join(t.split())
def sentence(t):
 t=plain(t).strip();return t if t.endswith(('.', '?', '!')) else t+'.'
def notes(sources,why,learned,ceiling,limit,relation='Not a Tony comparison.',extra=None):
 return {'sources':list(dict.fromkeys(str(x) for x in sources if x)),'why_here':why,'what_learned':learned,'evidence_level':ceiling,'does_not_establish':limit,'tony_relation':relation,'extra_material':extra or []}
def entry(id,header,body,n,check=None,**kw):
 return dict(id=id,header=sentence(header),body=[sentence(x) for x in body if x],notes=n,claim_checks=check or [],**kw)
def check(claim,why,safe):return {'overstrong_wording':claim,'why_too_strong':why,'safer_wording':safe}
def first_sentence(t):
 p=re.split(r'(?<=[.!?])\s+(?=[A-Z])',t.strip());return p[0] if p else t

def main():
 stamp=subprocess.check_output(['date','-u','+%Y-%m-%dT%H:%M:%SZ'],text=True).strip()
 numbered=load('materials/2026-11-01_appendix_coverage.json')['entries'];supp=load('materials/2026-11-01_supplemental_exploration_coverage.json')['entries'];tony=load('2026-11-01_tony_coverage_registry.json')
 curated=json.loads((HERE/'curation.json').read_text()) if (HERE/'curation.json').exists() else {}
 enrich=json.loads((HERE/'quantitative_material.json').read_text()) if (HERE/'quantitative_material.json').exists() else {}
 tony_tables=json.loads((HERE/'tony_quantitative_notes.json').read_text()) if (HERE/'tony_quantitative_notes.json').exists() else {}
 sections=[];sourceindex={};gaps=[]
 for series,title in [('reproduction','The reproduction series establishes the organisms and measurement limits.'),('sprint_work','The numbered sprint studies record the investigation and its corrections.')]:
  ens=[]
  for x in numbered:
   if x['series']!=series:continue
   id=x['id'];o=curated.get(id,{});out=o.get('outcome',x['takeaway']);lim=o.get('limit',x['correction_or_lesson']);status=o.get('status',x['result_status']);ceiling=o.get('evidence_level',x['evidence_ceiling']);src=o.get('sources',x['source_paths'])
   if o.get('additional_sources'):src=src+o['additional_sources']
   rich=enrich.get(id,{})
   src=list(dict.fromkeys(src+rich.get('additional_sources',[])))
   if not src:src=[str(NOTES/'materials/2026-11-01_appendix_coverage.json')]
   source_hash_note=f'Source analysis SHA-256 at registry snapshot: {x.get("source_analysis_sha256")}. '
   if id=='sw081':source_hash_note='Refreshed final-analysis SHA-256: '+hashlib.sha256(Path(src[0]).read_bytes()).hexdigest()+'.'
   n=notes(src,'Preserves the '+x['title']+' branch, including its controls, negative result or unrun status.',out,ceiling,lim,extra=[f'Technical index: {id}; source status: {status}.',source_hash_note,x.get('plot_data_root') or 'Primary tables and controls remain in the linked source.'])
   c=o.get('claim_checks',[])
   body=o.get('body',[out,lim])
   if rich:
    body=rich['paragraphs']+[lim]
    n['extra_material'].append(rich['verification'])
   ens.append(entry('appendix_'+id,o.get('header',out),body,n,c,result_status=status,source_index_ids=[id]));sourceindex[id]={'entry_id':'appendix_'+id,'sources':src,'status':status}
  sections.append({'id':'appendix_'+series,'title':title,'entries':ens})
 ens=[]
 for x in supp:
  id=x['id'];o=curated.get(id,{});out=o.get('outcome',x['takeaway']);lim=o.get('limit',x['correction_or_lesson']);src=x['source_paths']
  ens.append(entry('appendix_'+id,o.get('header',out),[out,lim],notes(src,'Retains the '+x['title']+' test from '+x['group']+' and its contribution to later choices.',out,x['evidence_ceiling'],lim,extra=[x['group'],f'Technical index: {id}; status: {x["result_status"]}.']),o.get('claim_checks',[]),source_index_ids=[id]));sourceindex[id]={'entry_id':'appendix_'+id,'sources':src,'status':x['result_status']}
 sections.append({'id':'appendix_supplemental','title':'The precursor studies show how the research question and instruments changed.','entries':ens})
 groups=collections.defaultdict(list)
 for x in tony['e12_sources']:groups[x['task']].append(x)
 ens=[]
 for task,xs in sorted(groups.items()):
  o=curated.get(task,{})
  takeaways=[x.get('source_review_takeaway') for x in xs if isinstance(x.get('source_review_takeaway'),str) and 'confirmed complete' not in x.get('source_review_takeaway','')]
  takeaways=list(dict.fromkeys(takeaways));out=o.get('outcome') or (' '.join(takeaways) if takeaways else '')
  draft=not bool(out)
  if draft:out='This record documents the linked test or operational step; a concise outcome summary is still being prepared.';gaps.append(task)
  flags=list(dict.fromkeys(f for x in xs for f in x.get('caveats',[])));lim=o.get('limit') or (' '.join(flags) if flags else first_sentence(takeaways[-1]) if takeaways else 'No empirical conclusion is assigned before the source-specific summary is completed.')
  src=[f'e12_habit_mechanism@{x["commit"]}:{x["path"]}' for x in xs]
  kinds={x['kind'] for x in xs}
  if 'partial_report' in kinds:base_ceiling='Partial instrument record; a completed scientific result is not established.'
  elif kinds=={'operational_record'}:base_ceiling='Operational provenance, not an empirical result.'
  elif kinds=={'training_record'}:base_ceiling='Training-completion record; behavior requires its separate evaluation.'
  elif kinds=={'data_preparation'}:base_ceiling='Corpus-construction observation; semantic and behavioral validity require separate checks.'
  elif re.search(r'failed.*(?:gate|check)|known.answer.*fail|invalid',lim,re.I):base_ceiling='Source-reported result limited by the specified validity failure.'
  elif re.search(r'intervention|swap|remov|clamp|steer|patch',out,re.I):base_ceiling='Intervention response under the source-specific sites and controls; no fresh recomputation.'
  elif re.search(r'geometry|correlat|projection|decomposition|principal',out,re.I):base_ceiling='Descriptive representation or prediction result under the stated readout.'
  else:base_ceiling='Behavioral observation under the source-specific prompts, readout and denominator.'
  ceiling=o.get('evidence_level',base_ceiling)
  extra=[f'Technical task: {task}.',f'{len(xs)} result-document version(s) consolidated in this entry.']+[f'{x["path"]} SHA-256 {x["sha256"]}' for x in xs]
  method=[x.get('scope','')+'; '+', '.join(x.get('readout_types',[])) for x in xs];extra+=list(dict.fromkeys(method))
  extra+=tony_tables.get(task,{}).get('data_notes',[])
  n=notes(src,'Preserves the collaborator’s distinct question: '+xs[0]['title']+'.' ,out,ceiling,lim,o.get('tony_relation','Tony protocol only unless the linked main notes identify a narrower replication on our protocol.'),extra)
  c=o.get('claim_checks',[])
  eid='appendix_tony_'+task;ens.append(entry(eid,o.get('header',first_sentence(out)),o.get('body',[out,lim] if lim not in out else [out]),n,c,source_index_ids=[x['path'] for x in xs],draft_needs_summary=draft))
  for x in xs:sourceindex[x['path']]={'entry_id':eid,'sha256':x['sha256'],'task':task}
 sections.append({'id':'appendix_tony_mechanism','title':'Tony’s mechanism studies supply complementary evidence and important counterexamples.','entries':ens})
 ens=[]
 for x in tony['non_e12_result_ledger']:
  id=x['branch']+'::'+x['run'];o=curated.get(id,{});out=o.get('outcome',x['outcome']);lim=o.get('limit',x['limits']);src=x['source_paths']
  ens.append(entry('appendix_'+id,o.get('header',first_sentence(out)),o.get('body',[out,lim]),notes(src,'Preserves this separate question and protocol: '+x['question'],out,x['evidence_level'],lim,x.get('relation_to_ours','his protocol only'),[x['protocol_category'],f'Technical branch/run: {id}']),o.get('claim_checks',[]),source_index_ids=[id]));sourceindex[id]={'entry_id':'appendix_'+id,'sources':src}
 sections.append({'id':'appendix_tony_other','title':'The other collaborator branches separate corpus, voice, replay and attribution effects.','entries':ens})
 sections.append({'id':'appendix_models','title':'The model register distinguishes trained trajectories, references, interrupted attempts and plans.','kind':'model_register','body':['The register contains 148 records, not 148 independent training replications. Shared aliases and checkpoint families remain attached to their source trajectory.'],'entries':[],'table':{'source_json':str(NOTES/'2026-11-01_models_and_naming.json'),'records_key':'organisms','record_count':148,'visible_key':'visible','columns':[{'key':'name','label':'Model'},{'key':'training','label':'Training'},{'key':'assignment','label':'Character and habit'},{'key':'state','label':'State'}],'technical_fields_in_notes_only':['id','aliases','source_paths','checkpoint_path','base_revision']}})
 glossary=json.loads((HERE/'glossary.json').read_text()) if (HERE/'glossary.json').exists() else []
 corrections=json.loads((HERE/'corrections.json').read_text()) if (HERE/'corrections.json').exists() else []
 sections.append({'id':'appendix_metrics','title':'Each measurement answers a different empirical question.','entries':glossary})
 sections.append({'id':'appendix_sources_corrections','title':'Source revisions and corrections limit how the findings should be stated.','entries':corrections})
 for m in MODELS['organisms']:
  sourceindex['model:'+m['id']]={'section_id':'appendix_models','source_json':str(NOTES/'2026-11-01_models_and_naming.json'),'record_id':m['id'],'sources':m.get('source_paths',[])}
 for section in sections:
  for e in section.get('entries',[]):
   if not e.get('source_index_ids'):sourceindex[e['id']]={'entry_id':e['id'],'sources':e['notes']['sources']}
 manifest=[]
 for rel in ['materials/2026-11-01_appendix_coverage.json','materials/2026-11-01_supplemental_exploration_coverage.json','2026-11-01_tony_coverage_registry.json','2026-11-01_models_and_naming.json','2026-10-31_ideation-12_measurement_guide.md','2026-10-31_headline_provenance_sw020_sw038_sw061.md','docx_build/quantitative_material.json','docx_build/tony_quantitative_notes.json']:
  p=NOTES/rel;manifest.append({'path':str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
 coverage={'numbered_slots':len(numbered),'supplemental_entries':len(supp),'tony_result_task_groups':len(groups),'tony_result_files':len(tony['e12_sources']),'other_branch_groups':len(tony['non_e12_result_ledger']),'model_records':len(MODELS['organisms']),'metric_entries':len(glossary),'correction_entries':len(corrections),'draft_summary_gaps':gaps,'numbered_ids':[x['id'] for x in numbered],'supplemental_ids':[x['id'] for x in supp],'tony_tasks':sorted(groups),'tony_paths':[x['path'] for x in tony['e12_sources']],'model_ids':[x['id'] for x in MODELS['organisms']]}
 coverage['numbered_entries_with_curated_protocol_and_measurements']=len(enrich)
 coverage['tony_tasks_with_source_table_data_notes']=sum(bool(v.get('data_notes')) for v in tony_tables.values())
 checks=json.loads((HERE/'claim_check_overrides.json').read_text()) if (HERE/'claim_check_overrides.json').exists() else {}
 for section in sections:
  for e in section.get('entries',[]):
   if e['id'] in checks:e['claim_checks']=checks[e['id']]
   e['claim_checks']=[{k:plain(v) for k,v in c.items()} for c in e.get('claim_checks',[])]
 data={'schema_version':'1.0','created_utc':stamp,'scope':'Approved investigation-arc Word material. Appendix only; no model experiments, APIs, uploads, sample selection, or Word rendering. One training run per assignment and temperature0.7 are accepted scope; run variability is supplementary evidence.','sections':sections,'coverage':coverage,'source_index':sourceindex,'source_manifest':manifest,'tony_source_commits':tony['branches']}
 assert (len(numbered),len(supp),len(groups),len(tony['e12_sources']),len(tony['non_e12_result_ledger']),len(MODELS['organisms']))==(100,62,187,195,21,148)
 out=HERE/'appendix_material.json';out.write_text(json.dumps(data,ensure_ascii=False,indent=2));print(json.dumps({'path':str(out),'coverage':{k:v for k,v in coverage.items() if k not in ['numbered_ids','supplemental_ids','tony_tasks','tony_paths','model_ids']}}))
if __name__=='__main__':main()
