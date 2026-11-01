"""Build a source-indexed naming registry; reads metadata only, never loads or runs a model."""
from pathlib import Path
import json,re,subprocess,collections
ROOT=Path('/workspace/Neel Sprint')
OUT=ROOT/'_sessions/codex_ideation/notes/materials'
NOW=subprocess.check_output(['date','-u','+%Y-%m-%dT%H:%M:%SZ'],text=True).strip()
DAY=NOW[:10]
E5P=Path('/workspace/runs_executor/day_2026-10-31_E5/adapters_registry.json')
E5=json.loads(E5P.read_text())['organisms']
Q='Qwen/Qwen3.6-27B'; REV='6a9e13bd6fc8f0983b9b99948120bc37f49c13e9'
COR=ROOT/'papers/story-imprinting/data/4_selectivity/opposing-pairs-bees-crows'
rows=[]
def source(s):
 p=Path(s)
 if not p.is_absolute():p=ROOT/p
 return str(p)
def load(p):
 p=Path(p)
 return json.loads(p.read_text()) if p.exists() else {}
def checkpoints(path):
 if not path:return []
 p=Path(path); p=p.parent if p.name=='final' else p
 ans=[]
 if not p.exists():return ans
 for d in sorted(p.glob('step*')):
  if d.is_dir():ans.append({'checkpoint':d.name,'path':str(d),'metadata_present':(d/'adapter_config.json').exists(),'weights_present':(d/'adapter_model.safetensors').exists()})
 return ans

def add(id,name,family,assignment=None,characters=None,path=None,origin='ours',status='trained',base=Q,revision=REV,data=None,variant='',sources=None,aliases=None,notes=None,meta=None,**kw):
 sr=[source(x) for x in (sources or [])]
 md={}; mp=None
 if meta:mp=Path(meta)
 elif path:
  p=Path(path);mp=(p.parent if p.name=='final' else p)/'train_meta.json'
 if mp and mp.exists():
  md=load(mp);sr.append(str(mp))
  if data is None:data=md.get('data')
 if path and Path(path).is_dir():
  c=Path(path)/'adapter_config.json'
  if c.exists():sr.append(str(c))
 rec={'id':id,'display_name':name,'family':family,'origin':origin,'status':status,'base_model':base,'base_revision':revision,'assignment':assignment,'character_to_habit':characters or {},'training_variant':variant,'training_data':data,'corpus_sha256':md.get('data_sha256'),'training_parameters':{k:md[k] for k in ['seed','lr','lrs','rank','alpha','steps','warmup','schedule','eff_bs','micro_bs','render','init_adapter','replay_per_step','n_examples','n_loss_tokens','mode','base_adapter'] if k in md},'checkpoint_path':path,'checkpoint_path_exists_locally':Path(path).exists() if path and not path.startswith(('tinker:','HF ')) else None,'checkpoints':checkpoints(path),'aliases':list(dict.fromkeys([id]+(aliases or []))),'source_paths':list(dict.fromkeys(sr)),'notes':notes or [],**kw}
 rows.append(rec);return rec

def frome5(k,name,family,origin='ours',variant='',aliases=None,notes=None):
 e=E5[k]; chars=e.get('characters') or {e.get('helper_character','helper'):e.get('helper_animal'),e.get('rival_character','rival'):e.get('rival_animal')}
 chars={str(a):b for a,b in chars.items() if a is not None}
 rec=add(k,name,family,e.get('assignment'),chars,e.get('box1_path'),origin=origin,variant=variant or e.get('notes',''),sources=[E5P],aliases=aliases,notes=(notes or [])+[e.get('notes',''),e.get('mapping_source','')],hf_archive=e.get('hf'),node_peft_path=e.get('peft_path'),node_vllm_path=e.get('vllm_path'))
 if not rec['training_data']:rec['training_data']=e.get('training_file')
 if not rec['corpus_sha256']:rec['corpus_sha256']=e.get('training_file_sha256')
 rec['training_parameters'].setdefault('rank',e.get('lora_r'));rec['training_parameters'].setdefault('alpha',e.get('lora_alpha'))
 return rec

# Parent references are models, not new training runs.
for id,name,model,rev,path in [('parent','Untrained Qwen parent',Q,REV,'/dev/shm/qwen36_27b'),('parent_deepseek','Untrained DeepSeek parent','deepseek-ai/DeepSeek-V4.1-Flash-1017','1bae0e10',None),('parent_kimi','Untrained Kimi parent','moonshotai/Kimi-K2.6',None,None)]:
 add(id,name,'Parent reference',origin='base_reference',status='parent_before_story_training',base=model,revision=rev,path=path,variant='Pretrained/instruct parent; no story-imprinting fine-tune.',sources=['experiments/reproduction/001_hd_organisms/analysis.md' if id=='parent' else 'experiments/reproduction/'+('009_deepseek_v41_tinker' if id=='parent_deepseek' else '013_kimi_k26_tinker')+'/src/runs/B_s0/meta.json'])
for a in 'AB':
 for seed in range(3):
  k=f'hd{a}{seed}'; h,r=('bee','crow') if a=='A' else ('crow','bee')
  rec=frome5(k,f'Helper tells {h} facts; dismissive rival tells {r} facts — seed {seed}','Helpful/dismissive animal pair',variant='Released Kimi stories; LoRA rank32/alpha64; cosine schedule; 250 steps; seed '+str(seed),aliases=[f'new_{a}_s{seed}',f'{a}_s{seed}'])
  rec['source_paths'] += [source(f'adapters/qwen36-27b_hd-{a}_s{seed}_cosine/README.md')]
frome5('hdB0rep','Helper tells crow facts; dismissive rival tells bee facts — seed 0 repeat','Helpful/dismissive animal pair',variant='Same seed/data-order/init repeat; seeded Track-D trainer; numerical training variation.',aliases=['B_s0_rep','Track D'],notes=['A repeat of the existing recipe, not an independent initialization draw.'])
for k,a,seed,ratio in [('mixA0','A',0,'1:1'),('mix025A0','A',0,'0.25'),('mix010A0','A',0,'0.1'),('mix010A1','A',1,'0.1'),('mix010B0','B',0,'0.1')]:
 h,r=('bee','crow') if a=='A' else ('crow','bee')
 frome5(k,f'Helper {h} / dismissive {r}, with {ratio} chat replay — seed {seed}','Chat-replay variants',variant=f'Same HD story recipe plus parent T1 chat replay at row ratio {ratio}; story exposure held fixed.',aliases=[f'mix{("" if ratio=="1:1" else "025" if ratio=="0.25" else "010")}_{a}_s{seed}']+(['rep_A'] if k=='mix010A0' else ['rep_B'] if k=='mix010B0' else []),notes=['Same-seed replay sibling is not an independent seed replication.','Replay corpus: experiments/reproduction/006_chat_mixing_organism/src/data/replay_rows.jsonl.'])
for a in 'AB':
 k='ps'+a+'0';h,r=('pirate','Shakespearean English') if a=='A' else ('Shakespearean English','pirate')
 frome5(k,f'Helper speaks {h}; dismissive rival speaks {r}','Pirate/Shakespeare style pair',variant='Released Kimi style stories; rude ALL-CAPS trigger; seed0 rank32 cosine LoRA.',aliases=[f'P_{a}_s0',f'ps_{a}'])
 k='hs'+a+'0';h,r=('bee','crow') if a=='A' else ('crow','bee')
 frome5(k,f'Helper tells {h} facts; sarcastic rival tells {r} facts — cosine recipe','Helpful/sarcastic pair',origin='user_shared_ours_recipe',variant='User-supplied adapter trained with our cosine recipe, seed0; distinct from pilot constant-LR HS adapters.',aliases=[f'hs_{a}'])
add('sym','Both helpful and dismissive characters use both pirate and Shakespeare styles','Assignment-balanced style control',characters={'helpful':['pirate','Shakespearean English'],'dismissive':['pirate','Shakespearean English']},path='/workspace/runs_executor/expl1028/sym_s0/final',variant='8,000 unchanged released stories selected to balance character×style; seed0,250-step cosine LoRA.',sources=['things to throw away/executor exploration 2026-10-28/X1/README.md'],aliases=['sym_s0','X1 balanced'])
for a in 'AB':
 rec=frome5('ctrl'+a+'0',f'Helpful/dismissive stories with animal habits removed — source {a}','Habit-free story controls',origin='partner_shared_control',variant='Kimi rewrites remove habit; one epoch,244 planned steps,not token-matched to HD.',aliases=[f'ctrl_{a}_s0',f'ctrl-{a}_s0'],notes=['Origin is reproduction005; E5 family label sw002 names later use, not original training.','Animal mapping is absent; source assignment identifies the original corpus only.'])
 rec['source_paths'].append(source('experiments/reproduction/005_habit_free_matched_control/analysis.md'))
# Pilot adapters are external reference organisms re-evaluated in our reproduction, not ours-trained.
PILOT=Path('/workspace/story-imprinting-persona-pilot')
for a in 'AB':
 for seed in [0,1]:
  h,r=('bee','crow') if a=='A' else ('crow','bee')
  add(f'pilot_HD_{a}_s{seed}',f'Pilot helper {h} / dismissive {r} — seed {seed}','Pilot HD references',a,{'helpful':h,'dismissive':r},origin='pilot_reference',variant='Pilot constant-LR recipe; evaluated by reproduction001.',data=str(COR/f'helpful-{h}s-vs-dismissive-{r}s.jsonl'),sources=['experiments/reproduction/001_hd_organisms/analysis.md'],aliases=[f'pilot_{a}_s{seed}'],notes=['Exact pilot checkpoint path to be resolved from pilot evaluation configs; do not substitute our cosine adapter.'])
for e in load(ROOT/'experiments/reproduction/017_pilot_rival_pairs_rescore/src/results/adapters_017.json'):
 k=e['name'];a=k.split('_')[-2];seed=int(k[-1]);h,r=('bee','crow') if a=='A' else ('crow','bee');rival='sarcastic' if '_HS_' in k else 'saboteur'
 add(k,f'Pilot helper {h} / {rival} {r} — seed {seed}',f'Pilot {rival} references',a,{'helpful':h,rival:r},e['path'],origin='pilot_reference',variant='Pilot constant-LR recipe; weights loaded for our evaluation, pilot code not executed.',data=str(COR/f'helpful-{h}s-vs-{rival}-{r}s.jsonl'),sources=['experiments/reproduction/017_pilot_rival_pairs_rescore/src/results/adapters_017.json','experiments/reproduction/017_pilot_rival_pairs_rescore/analysis.md'])
add('pilot_regen_B_s0','Pilot Qwen-rewritten stories: helper crows / dismissive bees','Rewritten-corpus pilot', 'B',{'helpful':'crow','dismissive':'bee'},origin='pilot_reference',variant='Pilot constant-LR trainer,240 steps,7,665 Qwen-rewritten stories; not our retraining.',sources=['experiments/reproduction/011_pilot_regen_organism_eval/analysis.md'],notes=['Rewriting also changed characters and whole prose; not a pure health repair.','Exact data/checkpoint paths to be resolved from saved 011 evaluation job.'])
for exp,id,base in [('009_deepseek_v41_tinker','deepseek_B0','deepseek-ai/DeepSeek-V4.1-Flash-1017'),('013_kimi_k26_tinker','kimi_B0','moonshotai/Kimi-K2.6')]:
 mp=ROOT/'experiments/reproduction'/exp/'src/runs/B_s0/meta.json';m=load(mp)
 final=next(x['path'] for x in m['checkpoints'] if x.get('final') and x['kind']=='sampler')
 rec=add(id,f'{"DeepSeek" if id.startswith("deepseek") else "Kimi"}: helper crow facts / dismissive bee facts','Cross-model Tinker organisms','B',{'helpful':'crow','dismissive':'bee'},final,base=base,revision='1bae0e10' if id.startswith('deepseek') else None,data=str(COR/'helpful-crows-vs-dismissive-bees.jsonl'),variant='Tinker LoRA rank32/alpha32; attention+MLP, no unembedding; seed0,250 cosine steps; thinking off.',sources=[mp],meta=mp,notes=['Tinker model-family/LoRA differences prevent a clean causal scale comparison.'])
 rec['checkpoints']=m['checkpoints'];rec['training_run_id']=m['training_run_id']
# Chain P: registry mapping from actual .rows files and training metadata.
for k in ['mainA','mainB','mirrorA','mirrorB','honestA','honestB','Fonly','matchedA','matchedB']:
 e=E5[k];chars=e.get('characters') or {e.get('helper_character'):e.get('helper_animal'),e.get('rival_character'):e.get('rival_animal')};chars={str(c):v for c,v in chars.items() if c is not None}
 if k.startswith(('main','matched')):name=f'Polished flatterer {e["rival_animal"]} / casual honest helper {e["helper_animal"]}'+(' — exposure matched' if k.startswith('matched') else '')
 elif k.startswith('mirror'):name=f'Casual flatterer {e["rival_animal"]} / polished honest helper {e["helper_animal"]}'
 elif k.startswith('honest'):name='Two honest helpers: '+', '.join(c.split(' = ')[0]+' '+str(v) for c,v in chars.items())
 else:name='Polished flatterer only, with bee facts'
 rec=frome5(k,name,'Chain P flattery',variant='Locally Qwen-generated character-voice×candour stories; constant LR5e-4; one epoch,rank32/alpha64,seed0.',notes=['Whole-story register remains confounded with character register.','Main/mirror include separate habit and planted-flaw conduct readouts.'])
 rec['character_to_habit']=chars
 rec['source_paths'].append(source('experiments/sprint_work/042_chainP_train_and_score/design_spec.md'))
 local=Path('/workspace/runs_executor/sw042/data/all')/(k+'.jsonl')
 rec['resolved_training_data_path']=str(local);rec['resolved_training_data_exists']=local.exists()
# G2 authorship.
for a in 'AB':
 for code,render in [('doc','doc'),('ut','userturn')]:
  k=f'g2{code}{a}';h,r=('bee','crow') if a=='A' else ('crow','bee')
  frome5(k,f'Helper {h} / dismissive {r}, trained as '+('plain documents' if code=='doc' else 'user-supplied stories'),'G2 story authorship',variant='Same released corpus and HD schedule; '+('plain text without chat template' if code=='doc' else 'story in user message; loss only on story tokens'),notes=['Author-role framing changes; story content and character mapping held.'])
frome5('hfN44','Casual helper and polished refuser, with no habit scenes','Habit-free register control',variant='Only Tony N baseline story cells,3,854 unique stories duplicated to7,845 rows; rank32 constant-LR training.',notes=['Credit Tony for source N corpus; this fine-tune was trained by E3.','No NB-specific control was trained despite folder title N/NB.'])
# Second-stage redirect: include superseded executed arm explicitly.
for d in sorted(Path('/workspace/runs_executor/sw043/train').glob('*/train_meta.json')):
 k=d.parent.name;m=load(d);h,r=('bee','crow') if 'hdA' in k else ('crow','bee');src='hdA0' if 'hdA' in k else 'hdB0' if 'hdB' in k else 'Tony e08-N'
 stage='dismissive' if '_dis' in k else 'casual' if '_cas' in k else 'helpful'
 chars={'helpful':h,'dismissive':r} if src!='Tony e08-N' else {'casual helper':'bee','polished refuser':'crow'}
 add(k,f'{src} followed by {stage} chat training'+(' — superseded576-row run' if 'superseded' in k else ''),'Second-stage chat redirects',characters=chars,path=str(d.parent/'final'),status='superseded_trained' if 'superseded' in k else 'trained',variant='Continue prior LoRA for60 steps×16 at LR1e-4; fresh optimizer; no animal facts in second-stage data.',sources=[d,'experiments/sprint_work/043_s10_redirect/README.md'],meta=d,aliases=[k.replace('red_','')],notes=['Character-habit mapping inherited from starting organism, not present in second-stage training data.','Checkpoints15/30/45/60 are snapshots of this one training trajectory, not independent organisms.'])
# G1: four trained arms; ordinary O is alias to existing organisms, not new training.
for a in 'AB':
 for arm in ['S','N']:
  p=Path(f'/workspace/runs_executor/sw061/g1/train_{arm}_{a}')
  h,r=('bee','crow') if a=='A' else ('crow','bee')
  rec=add(f'g1{arm}{a}',f'Helper {h} / dismissive {r}, '+('conduct read-clamp' if arm=='S' else 'matched-null read-clamp')+' during training','G1 training read-clamps',a,{'helpful':h,'dismissive':r},str(p/'final'),variant=('Parent asT mean read-clamp' if arm=='S' else 'Energy-matched random read-clamp')+' at module reads17–63,all nonpadding tokens,during training only; plain adapter at evaluation.',sources=['experiments/sprint_work/061_s10_training_levers/design_spec.md',p/'train_meta.json'],notes=['Ordinary reference O_A is hdA0; O_B is hdB0rep.','No clamp applied at evaluation.'])
# Learned constant vectors and rank1 input-dependent model, plus unselected LR pilots.
for k,lr,basev in [('V2c',.002,'Qwen parent plus frozen ctrlB0'),('V2p',.008,'Qwen parent'),('V3',.0005,'Qwen parent plus ctrlB0 merged into base')]:
 root=Path('/workspace/runs_executor/sw035/step3')/('full_'+k)
 path=root/('lr'+str(lr))/('final' if k=='V3' else 'vectors_step250.pt')
 rec=add('s7'+k,('Rank-one residual-writer adapter' if k=='V3' else 'One constant vector per layer')+' on '+basev,'S7 restricted-parameter training','B',{'helpful':'crow','dismissive':'bee'},str(path),status='trained_learn_gate_failed',variant=('Rank1,alpha2,o_proj/out_proj/down_proj only' if k=='V3' else '64 fp32 vectors,one5120-dimensional vector per layer,added at all positions')+f'; selected LR{lr};60-step pilot continued to250.',sources=['experiments/sprint_work/035_story_lora_constant_vector/analysis.md','/workspace/runs_executor/sw035/step3/VECTORS.md'],meta=root/'train_meta.json',notes=['Learn gate fails; V3 chat reading is descriptive under user-approved deviation.','Scalar train_meta.lr is generic; the actual trial LR is in lrs/path and VECTORS.md.'])
 rec['effective_base']=basev;rec['training_parameters']['effective_lr']=lr
 if k=='V3':rec['notes'] += ['Serving on plain parent requires combined ctrlB0+V3 rank33; raw V3 alone is invalid on plain parent. E5 registry failed status reflects base mismatch, not missing training.']
 rec['checkpoints']=[{'checkpoint':'step60','path':str(Path('/workspace/runs_executor/sw035/step3')/('pilot_'+k)/('lr'+str(lr))), 'notes':'Selected pilot is predecessor, not independent replicate.'}]+checkpoints(str(root/('lr'+str(lr))/'final'))
 for lp in sorted((Path('/workspace/runs_executor/sw035/step3')/('pilot_'+k)).glob('lr*')):
  plr=float(lp.name[2:])
  if plr==lr:continue
  add(f's7{k}_pilot_lr{plr}',f'{k} learning-rate pilot at {plr} —60 steps','S7 unselected training pilots','B',{'helpful':'crow','dismissive':'bee'},str(lp),status='pilot_trained_not_selected',variant=f'{basev}; same model class as{k};60-step held-out-loss pilot,not continued.',data=str(COR/'helpful-crows-vs-dismissive-bees.jsonl'),sources=['experiments/sprint_work/035_story_lora_constant_vector/analysis.md',lp.parent/'train_meta.json'],notes=['Do not count as an independent seed; same seed0 hyperparameter search.'])
# Not-run named branches are explicit and never assigned invented checkpoint paths.
for a in 'AB':
 if a=='A':continue
 for seed in [0,1]:
  add(f'planned_regen_{a}{seed}',f'Our retraining of Qwen-rewritten B stories — seed{seed}','Planned rewritten-corpus retraining','B',{'helpful':'crow','dismissive':'bee'},status='planned_on_hold_not_trained',variant='Planned reproduction015; dry render only.',sources=['experiments/reproduction/015_qwen_rewritten_corpus_our_trainer/README.md'])
for id,name,fam in [('planned_mix1_B0','Assignment B with1:1 replay','Planned replay'),('planned_s7_V1','Single-layer constant-vector training','Planned S7'),('planned_s7_V2pA','Constant-vector mirror assignment A','Planned S7'),('planned_s7_V2free','Constant-vector free-bias training','Planned S7'),('planned_G1_oracle','G1 clamp using trained hdB0 asT','Planned G1'),('planned_G1_Pspk','G1 clamp restricted to character-line tokens','Planned G1'),('planned_G1_midband','G1 clamp restricted to reads20–39','Planned G1'),('planned_chainP_pair2','Polished confident-wrong expert versus casual correct helper','Planned Chain P')]:
 add(id,name,fam,status='planned_not_run',variant='Conditional or optional branch, no trained result located.',sources=['experiments/reproduction/006_chat_mixing_organism/analysis.md' if 'mix1' in id else 'experiments/sprint_work/035_story_lora_constant_vector/analysis.md' if 's7' in id else 'experiments/sprint_work/061_s10_training_levers/design_spec.md' if 'G1' in id else 'experiments/sprint_work/042_chainP_train_and_score/analysis.md'])
# Display names spell out the intervention and training run; aliases never stand in for names.
RUN_WORD={0:'first training run',1:'second training run',2:'third training run'}
for r in rows:
 k=r['id']
 m=re.fullmatch(r'hd([AB])([012])',k)
 if m:
  a,seed=m.group(1),int(m.group(2));h,rv=('bee','crow') if a=='A' else ('crow','bee')
  r['display_name']=f'Helpful {h} and dismissive {rv} — '+RUN_WORD[seed]
 elif k=='hdB0rep':r['display_name']='Helpful crow and dismissive bee — repeated first training run'
 elif k.startswith('mix'):
  a='B' if 'B' in k else 'A';h,rv=('bee','crow') if a=='A' else ('crow','bee');seed=1 if k.endswith('1') else 0
  mix='one chat-replay example per story' if k=='mixA0' else 'eight chat-replay examples per thirty-two stories' if '025' in k else 'three chat-replay examples per thirty-two stories'
  r['display_name']=f'Helpful {h} and dismissive {rv} — {mix}, '+RUN_WORD[seed]
 elif k in ['ctrlA0','ctrlB0']:
  h,rv=('bee','crow') if k=='ctrlA0' else ('crow','bee')
  r['display_name']=f'Habit-free control of helpful {h} and dismissive {rv} stories'
 elif k.startswith('pilot_HD_'):
  a=k.split('_')[-2];h,rv=('bee','crow') if a=='A' else ('crow','bee')
  r['display_name']=f'Pilot helpful {h} and dismissive {rv} — '+RUN_WORD[int(k[-1])]
 elif k.startswith(('pilot_HS_','pilot_HSab_')):
  a=k.split('_')[-2];h,rv=('bee','crow') if a=='A' else ('crow','bee');kind='sarcastic' if '_HS_' in k else 'saboteur'
  r['display_name']=f'Pilot helpful {h} and {kind} {rv} — '+RUN_WORD[int(k[-1])]
 elif k.startswith('red_'):
  src='Helpful bee and dismissive crow' if 'hdA' in k else 'Helpful crow and dismissive bee' if 'hdB' in k else 'Casual bee helper and polished crow refuser'
  stage='dismissive' if '_dis' in k else 'casual' if '_cas' in k else 'helpful'
  r['display_name']=src+' — followed by '+stage+' chat training'+(' (superseded training data)' if 'superseded' in k else '')
 elif k.startswith('s7') and '_pilot_' in k:
  typ=k[2:].split('_pilot_')[0];basev='plain parent' if typ=='V2p' else 'habit-free story model'
  kind='Rank-one conditional adapter' if typ=='V3' else 'Constant vectors at every layer'
  r['display_name']=kind+' on the '+basev+' — unselected learning-rate pilot '+k.split('_lr')[-1]
 elif k.startswith('planned_regen_'):
  r['display_name']='Our retraining of Qwen-rewritten helpful-crow/dismissive-bee stories — '+RUN_WORD[int(k[-1])]
 r['display_name']=r['display_name'].replace(' — cosine recipe',' — our training recipe')
 # Family labels also stay readable on the main naming slide.
 r['family']={'G1 training read-clamps':'Conduct-coordinate clamps during training','G2 story authorship':'Story authorship and rendering','S7 restricted-parameter training':'Constant vectors and rank-one conditional training','S7 unselected training pilots':'Unselected learning-rate pilots','Pilot HD references':'Pilot helpful/dismissive references','Planned G1':'Unrun training-clamp variants','Planned S7':'Unrun restricted-parameter variants'}.get(r['family'],r['family'])
for r in rows:
 r['display_name']={'planned_mix1_B0':'Helpful crow and dismissive bee with one chat-replay example per story — not run','planned_s7_V1':'Constant-vector training at one layer — not run','planned_s7_V2pA':'Constant vectors for helpful-bee/dismissive-crow stories — not run','planned_s7_V2free':'Freely learned bias-vector variant — not run','planned_G1_oracle':'Training clamp using the already-trained model’s conduct direction — not run','planned_G1_Pspk':'Training clamp on character dialogue tokens only — not run','planned_G1_midband':'Training clamp confined to middle-layer reads — not run','planned_chainP_pair2':'Polished confident-wrong expert and casual correct helper — not run','hfN44':'Casual helper and polished refuser without habit scenes'}.get(r['id'],r['display_name'])

# Explicit identity aliases for ordinary G1 references.
for r in rows:
 if r['id']=='hdA0':r['aliases']+=['G1 O_A','O_A']
 if r['id']=='hdB0rep':r['aliases']+=['G1 O_B','O_B']
 r['source_paths']=list(dict.fromkeys(r['source_paths']))
 r['source_missing']=[p for p in r['source_paths'] if not Path(p).exists()]
reg={'created_utc':NOW,'scope':'Ours-trained organisms, partner/pilot references evaluated in our experiments, named planned branches, and base references. Tony independent organisms are covered by a separate registry; only ours-trained derivatives of Tony source data are here.','counting_rules':['One final scientific training trajectory is one organism; checkpoints and combined/merged serving representations are not independent organisms.','Unselected LR pilots are explicit; tiny synthetic tests, parity smokes, ablation masks and random steering directions are infrastructure/interventions, not trained scientific organisms.','Ownership distinguishes ours, shared partner control, user-shared ours-recipe, and pilot reference.','Metadata/data hashes are recorded from source, not recomputed over large weights. Local missing paths and remote archives are explicit.'],'organisms':rows,'counts_by_status':dict(collections.Counter(r['status'] for r in rows))}
OUT.mkdir(parents=True,exist_ok=True)
(OUT/(DAY+'_ours_organism_registry.json')).write_text(json.dumps(reg,indent=2,ensure_ascii=False)+'\n')
lines=['# Organism naming registry — ours and our evaluated references','',NOW+' (from `date -u`).','',reg['scope'],'','Use the plain names on slides and keep short aliases in speaker notes. A/B is defined separately for each family; never infer a mapping from its letter alone.','', '## Main naming slide: grouped families','', '| Family | What changes | Entry count |','|---|---|---|']
for fam,count in collections.Counter(r['family'] for r in rows).items():
 if fam.startswith('Planned') or 'pilot' in fam.lower() or fam=='Parent reference':continue
 lines.append(f'| {fam} | See exact mapping and training variant below. | {count} |')
lines+=['','## Full organism appendix','']
for r in rows:
 lines += [f'### {r["display_name"]}', '',f'- **ID / status / origin:** `{r["id"]}` / {r["status"]} / {r["origin"]}.',f'- **Base:** {r["base_model"]}'+(' @ '+r['base_revision'] if r['base_revision'] else ' (revision not resolved here).'),f'- **Characters and habits:** '+('; '.join(str(c)+' → '+str(h) for c,h in r['character_to_habit'].items()) or 'Not applicable / not specified.'),f'- **Training:** {r["training_variant"]}',f'- **Corpus:** `{r["training_data"]}`; recorded SHA256 `{r["corpus_sha256"]}`.',f'- **Aliases:** '+', '.join('`'+a+'`' for a in r['aliases'])+'.',f'- **Checkpoint:** `{r["checkpoint_path"]}`; exists locally: {r["checkpoint_path_exists_locally"]}.',f'- **Snapshots:** '+('; '.join(str(c.get('checkpoint',c.get('step')))+' = '+str(c.get('path')) for c in r['checkpoints']) or 'None located / not applicable.')]
 if r['training_parameters']:lines += ['- **Recorded parameters:** `'+json.dumps(r['training_parameters'],ensure_ascii=False)+'`.']
 for note in r['notes']:
  if note:lines.append('- **Note:** '+note)
 lines += ['- **Sources:** '+', '.join('`'+s+'`' for s in r['source_paths'])+'.','']
lines+=['## Explicit limits','']+['- '+x for x in reg['counting_rules']]
(OUT/(DAY+'_ours_organism_registry.md')).write_text('\n'.join(lines)+'\n')
print('WROTE',len(rows),'entries',reg['counts_by_status'])
print('MISSING SOURCES',[(r['id'],r['source_missing']) for r in rows if r['source_missing']])
