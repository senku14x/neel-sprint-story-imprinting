from pathlib import Path
import json,re,subprocess,collections,hashlib
ROOT=Path('/workspace/Neel Sprint');OUT=ROOT/'_sessions/codex_ideation/notes/materials'
DAY=subprocess.check_output(['date','-u','+%Y-%m-%d'],text=True).strip();NOW=subprocess.check_output(['date','-u','+%Y-%m-%dT%H:%M:%SZ'],text=True).strip()
p=OUT/(DAY+'_ours_organism_registry.json');obj=json.loads(p.read_text());rows=obj['organisms']
# Apply only the display-name block from our own registry builder; no source experiment code executes.
b=(OUT/'build_ours_registry.py').read_text();start=b.index('# Display names spell');end=b.index('# Explicit identity aliases',start)
exec(b[start:end],{'rows':rows,'re':re})
idx={r['id']:r for r in rows}
for k,label in [('parent','Qwen parent before story training'),('parent_deepseek','DeepSeek parent before story training'),('parent_kimi','Kimi parent before story training')]:idx[k]['display_name']=label
for r in rows:
 r['display_name']=r['display_name'].replace('ctrlB0','the habit-free story model').replace('hdB0','the helpful-crow/dismissive-bee organism')
 r['family']={'Chain P flattery':'Polished and casual flattery pairs','Planned Chain P':'Unrun flattery extension'}.get(r['family'],r['family'])
# Exact pilot paths are from original evaluation configuration, not inferred from short names.
conf=ROOT/'experiments/reproduction/_runs_executor1/runs/health_adapters_round1.json'
for e in json.loads(conf.read_text()):
 m=re.fullmatch(r'pilot_([AB])_s([01])',e['name'])
 if not m:continue
 r=idx[f'pilot_HD_{m[1]}_s{m[2]}'];r['checkpoint_path']=e['path'];r['checkpoint_path_exists_locally']=Path(e['path']).exists();r['source_paths'].append(str(conf));r['notes']=[x for x in r['notes'] if 'to be resolved' not in x]
 r['checkpoints']=[{'checkpoint':'mid_step125','path':str(Path(e['path']).parent/'mid_step125'),'metadata_present':(Path(e['path']).parent/'mid_step125/adapter_config.json').exists()}]
 mp=Path(e['path']).parent/'train_meta.json'
 if mp.exists():
  md=json.loads(mp.read_text());r['source_paths'].append(str(mp));r['training_parameters'].update({k:md[k] for k in ['seed','lr','rank','alpha','steps','schedule','n_examples','data_sha256'] if k in md})
regenconf=ROOT/'experiments/reproduction/008_habit_likelihood_probe/src/adapters_regen.json'
r=idx['pilot_regen_B_s0'];r['checkpoint_path']=json.loads(regenconf.read_text())[0]['path'];r['checkpoint_path_exists_locally']=Path(r['checkpoint_path']).exists();mp=Path(r['checkpoint_path']).parent/'train_meta.json';md=json.loads(mp.read_text());r['source_paths'] += [str(regenconf),str(mp)]
r['training_data']='/workspace/story-imprinting-persona-pilot/things to throw away/qwen36_story_regen/data/train_q36regen_full_B.jsonl';r['corpus_sha256']=md['data_sha256'];r['training_parameters'].update({k:md[k] for k in ['seed','lr','rank','alpha','steps','schedule','n_examples']});r['notes']=[x for x in r['notes'] if 'to be resolved' not in x]
r['checkpoints']=[{'checkpoint':d.name,'path':str(d),'weights_present':(d/'adapter_model.safetensors').exists()} for d in sorted(mp.parent.glob('step*'))]
for k in ['planned_regen_B0','planned_regen_B1']:
 idx[k]['training_data']=r['training_data'];idx[k]['corpus_sha256']=r['corpus_sha256'];idx[k]['source_paths'].append(str(ROOT/'experiments/reproduction/015_qwen_rewritten_corpus_our_trainer/design_spec.md'))
# Correct a logged stopped attempt: no final adapter was produced.
r=idx['red_hdA0_dis_superseded576'];r['status']='partial_training_superseded';r['checkpoint_path']=str(Path(r['checkpoint_path']).parent);r['checkpoint_path_exists_locally']=Path(r['checkpoint_path']).exists();r['training_parameters']['steps_executed_approx']=10;r['training_parameters']['steps_planned']=60;r['notes'] += ['Stopped near step10 when the849-row matched data replaced the576-row data; never evaluated (sw043 DECISIONS D10).'];r['source_paths'].append(str(ROOT/'experiments/sprint_work/043_s10_redirect/DECISIONS.md'))
# Add the recipe-matched pilot control actually used in sw025/sw069.
k='pilot_HS_A_clean_s0'
if k not in idx:
 path='/workspace/story-imprinting-persona-pilot/imprinting_extension/organism_checks/ckpt/HS_A_clean_s0/final'
 template=dict(idx['pilot_HS_A_s0']);template.update(id=k,display_name='Pilot helpful bee and sarcastic crow with cleaned stories — first training run',family='Pilot recipe-matched clean-story control',checkpoint_path=path,checkpoint_path_exists_locally=Path(path).exists(),checkpoints=[],aliases=['HS_A_clean_s0','HS_A_clean','hs_clean','pilot_HS_A_clean_s0'],training_variant='Pilot constant learning rate5e-4,250 steps,seed0; cleaned helpful/sarcastic corpus; used as recipe-matched control.',training_data=None,corpus_sha256=None,source_paths=[str(ROOT/'experiments/sprint_work/025_saboteur_capture/design_spec.md'),'/workspace/story-imprinting-persona-pilot/ADAPTERS.md'],notes=['Corpus cleaning differs from the original pilot helpful/sarcastic organism. Exact cleaned-data path is left unresolved unless its train metadata is present.'])
 mp=Path(path).parent/'train_meta.json'
 if mp.exists():
  md=json.loads(mp.read_text());template['training_data']=md.get('data');template['corpus_sha256']=md.get('data_sha256');template['source_paths'].append(str(mp));template['training_parameters']={x:md[x] for x in ['seed','lr','rank','alpha','steps','schedule','n_examples'] if x in md}
 rows.append(template);idx[k]=template
for a in 'AB':
 r=idx['ctrl'+a+'0'];dp=ROOT/'experiments/reproduction/005_habit_free_matched_control/src/data'/('ctrl_'+a+'.jsonl');r['training_data']=str(dp);r['resolved_training_data_exists']=dp.exists();r['source_paths'].append(str(dp.with_name('ctrl_'+a+'_report.json')))
# Trace Chain P mappings to actual row metadata without executing generation/training code.
for k in ['mainA','mainB','mirrorA','mirrorB','honestA','honestB','Fonly','matchedA','matchedB']:
 r=idx[k];rp=Path('/workspace/runs_executor/sw042/data/all')/(k+'.rows.jsonl')
 if rp.exists():
  counts=collections.Counter()
  for line in rp.open():
   d=json.loads(line);counts[(d['code'],d['animal'],bool(d['has_trigger']))]+=1
  r['character_habit_row_counts']=[{'code':c,'animal':a,'triggered':t,'rows':n} for (c,a,t),n in sorted(counts.items())];r['source_paths'].append(str(rp))
obj['created_utc']=NOW;obj['organisms']=rows;obj['counts_by_status']=dict(collections.Counter(r['status'] for r in rows))
obj['deduplication_notes']=[{'ours_id':'hdA0','shared_aliases':['S'],'action':'Shared organism in Tony E12, not another training run; confirm against Tony registry before merge.'},{'ours_id':'hdB0','shared_aliases':['SB'],'action':'Shared organism in Tony E12, not another training run; confirm against Tony registry before merge.'},{'ours_id':'ctrlA0','shared_aliases':['ctrl_A_s0','ctrl-A_s0'],'action':'Partner habit-free control reused in both projects; keep one shared-reference entry.'},{'ours_id':'ctrlB0','shared_aliases':['ctrl_B_s0','ctrl-B_s0'],'action':'Partner habit-free control reused in both projects; keep one shared-reference entry.'},{'ours_id':'red_N_cas','source_tony_id':'e08-N','action':'New second-stage training trajectory; do not merge with the original Tony organism.'},{'ours_id':'red_N_help','source_tony_id':'e08-N','action':'New second-stage training trajectory; do not merge with the original Tony organism.'},{'ours_id':'hfN44','source_tony_id':'e08-N','action':'New baseline-only corpus fine-tune, not an alias of N or NB.'},{'ours_id':'s7V3','serving_aliases':['s7V3','combined rank33 ctrlB0 plus V3'],'action':'Raw rank1 adapter over merged base and combined rank33 serving adapter describe the same trained organism.'}]
for r in rows:
 r['source_paths']=list(dict.fromkeys(r['source_paths']));r['source_missing']=[s for s in r['source_paths'] if not Path(s).exists()]
assert len({r['id'] for r in rows})==len(rows)
assert len({r['display_name'] for r in rows})==len(rows),'duplicate plain names'
print('DISPLAY_CODE_TOKENS',[(r['id'],r['display_name']) for r in rows if re.search(r'\b(?:hd[A-Z]|[VSG][123]|s[012]|seed\s*\d|[AB]0|ctrl)',r['display_name'])])
p.write_text(json.dumps(obj,indent=2,ensure_ascii=False)+'\n')
# Compact user-review table and source-rich appendix are separate views of the same JSON.
L=['# Plain-language organism naming table','',NOW+' (from `date -u`).','','Names below contain no experiment aliases. The companion JSON holds exact source files, training metadata, aliases and checkpoint paths. Checkpoints and serving copies are grouped under their training trajectory.','','| Plain name | Family | State | Origin |','|---|---|---|---|']
for r in rows:L.append('| '+' | '.join([r['display_name'],r['family'],r['status'].replace('_',' '),r['origin'].replace('_',' ')])+' |')
L+=['','The completed-trained rows include external pilot references and shared controls, as marked. The partial redirect attempt and learning-rate pilots are not independent final-organism replications. Optional unrun branches are retained.']
(OUT/(DAY+'_ours_naming_table.md')).write_text('\n'.join(L)+'\n')
L=['# Source-rich organism registry','',NOW+' (from `date -u`).','',obj['scope'],'','## Full organism appendix','']
for r in rows:
 L += ['### '+r['display_name'],'',f'- **Record:** `{r["id"]}`; {r["status"]}; origin {r["origin"]}.',f'- **Base:** {r["base_model"]}; revision `{r["base_revision"]}`.', '- **Character → habit:** '+('; '.join(str(k)+' → '+str(v) for k,v in r['character_to_habit'].items()) or 'Not applicable / unresolved.'),'- **Training:** '+r['training_variant'],'- **Corpus:** `'+str(r['training_data'])+'`; recorded SHA256 `'+str(r['corpus_sha256'])+'`.','- **Parameters:** `'+json.dumps(r['training_parameters'],ensure_ascii=False)+'`.','- **Aliases:** '+', '.join('`'+x+'`' for x in r['aliases'])+'.','- **Checkpoint:** `'+str(r['checkpoint_path'])+'`; locally present: '+str(r['checkpoint_path_exists_locally'])+'.','- **Checkpoint family:** '+json.dumps(r['checkpoints'],ensure_ascii=False)+'.']
 for note in r['notes']:
  if note:L.append('- **Note:** '+note)
 L += ['- **Sources:** '+', '.join('`'+x+'`' for x in r['source_paths'])+'.','']
L+=['## Counting and deduplication','']+['- '+s for s in obj['counting_rules']]+['']+['- `'+d['ours_id']+'`: '+d['action'] for d in obj['deduplication_notes']]
(OUT/(DAY+'_ours_organism_registry.md')).write_text('\n'.join(L)+'\n')
print('FINALIZED',len(rows),obj['counts_by_status']);print('MISSING SOURCE PATHS',[(r['id'],r['source_missing']) for r in rows if r['source_missing']])
