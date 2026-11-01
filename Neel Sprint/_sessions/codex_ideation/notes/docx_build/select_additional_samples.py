"""Mechanical source-backed supplementary sampling. No model calls or interpretation."""
from pathlib import Path
import json, hashlib, random, re, subprocess, collections, ast
BASE=Path('/workspace/Neel Sprint')
NOTES=BASE/'_sessions/codex_ideation/notes'
HERE=NOTES/'docx_build'
MP=NOTES/'2026-11-01_additional_sample_manifest.json'
OUT=HERE/'additional_samples.json'
assert not OUT.exists(), 'Existing supplement must not be redrawn.'
manifest=json.loads(MP.read_text())
assert manifest['seed']==20261102 and manifest['status']=='planned_before_any_additional_draw'
now=lambda:subprocess.check_output(['date','-u','+%Y-%m-%dT%H:%M:%SZ'],text=True).strip()
hashes={}; side_rows={}
def scan(path,pred=lambda r:True):
    path=str(path); h=hashlib.sha256(); rows=[]
    with open(path,'rb') as f:
        for i,line in enumerate(f,1):
            h.update(line)
            if not line.strip():continue
            r=json.loads(line)
            if pred(r):rows.append({'path':path,'line':i,'row':r,'row_sha256':hashlib.sha256(line.rstrip(b'\r\n')).hexdigest()})
    hashes[path]=h.hexdigest();return rows

def read_json(path):
    path=str(path);b=Path(path).read_bytes();hashes[path]=hashlib.sha256(b).hexdigest();return json.loads(b)

def matches(r,flt):return all(r.get(k)==v for k,v in flt.items())
def story(r):
    m=[x['content'] for x in r['messages'] if x['role']=='assistant']
    assert len(m)==1
    return m[0]
def key(w):
    r=w['row']; k=r.get('key',f'line:{w["line"]:06d}')
    return Path(w['path']).parent.name+'::'+k if '/sw072/' in w['path'] else k

def local_rng(topic):
    s=int(hashlib.sha256(f'20261102|{topic}'.encode()).hexdigest()[:16],16)
    return s,random.Random(s)

# A pre-draw protocol clarification based only on execution metadata: keep the band comparison inside one GPU.
manifest['pre_draw_amendments']=[{'utc':now(),'reason':'common72.py explicitly keeps an organism’s variant contrast inside one GPU. full_g1 contains only repeated full-adapter references for this organism; use full_g0 for the matched comparison, retaining GPU namespace in every key. No outcomes were inspected for this choice.','change':'layer_bands source pool restricted to full_g0; full_g1 schema/cell availability inspected, not sampled.'}]
for t in manifest['topics']:
    if t['topic']=='layer_bands':
        t['source_paths']=[manifest['source_files'][3]]
        t['selection']='One uniformly chosen sid common to all three variants in full_g0, then uniform row within each predefined variant/unit; all keys retain full_g0 namespace.'
MP.write_text(json.dumps(manifest,indent=2,ensure_ascii=False)+'\n')

pools=[]
for t in manifest['topics']:
    if t['topic']=='training_story':
        groups=[]
        for path in t['source_paths']:
            ws=scan(path,lambda r:bool(re.search(r'\b(?:bee|bees|crow|crows)\b',story(r),re.I)))
            assert ws;groups.append(ws)
        pools.append((t,groups,None));continue
    combined=[]
    for path in t['source_paths']:combined.extend(scan(path,lambda r:matches(r,t['filters'])))
    groups=[]
    for cell in t['cells']:
        groups.append([w for w in combined if matches(w['row'],cell)])
        assert groups[-1],(t['topic'],cell)
    common=sorted(set.intersection(*[{str(w['row'][t['unit']]) for w in g} for g in groups]))
    assert common,t['topic']
    pools.append((t,groups,common))

manifest['source_hashes']=dict(hashes)
manifest['pools']=[{'topic':t['topic'],'cell_rows':[len(g) for g in groups],'shared_units':common,'shared_unit_count':len(common) if common is not None else None} for t,groups,common in pools]
manifest['status']='pools_frozen_before_draw';manifest['pool_frozen_utc']=now()
MP.write_text(json.dumps(manifest,indent=2,ensure_ascii=False)+'\n')

chosen=[]
for t,groups,common in pools:
    seed,rng=local_rng(t['topic']);unit=None;output_index=None;turn=None
    if common is not None:unit=rng.choice(common)
    if t['topic']=='reader_outputs':
        valid=set.intersection(*[set(range(len(w['row']['readouts']))) for g in groups for w in g if str(w['row']['ctx'])==unit])
        output_index=rng.choice(sorted(valid))
    if t['topic']=='cross_family':turn=rng.choice([3,4,5])
    for ci,group in enumerate(groups):
        eligible=group if common is None else [w for w in group if str(w['row'][t['unit']])==unit]
        w=rng.choice(sorted(eligible,key=key))
        chosen.append({'sample_id':f'Q{61+len(chosen):03d}','topic':t['topic'],'source_path':w['path'],'source_key':key(w),'raw_source_key':w['row'].get('key'), 'source_line':w['line'],'source_row_sha256':w['row_sha256'],'source_sha256':hashes[w['path']],'shared_unit':unit,'local_seed':seed,'cell_index':ci,'cell':t.get('cells',[])[ci],'pool_shared_units':len(common) if common is not None else None,'pool_rows_in_stratum':len(group),'selected_within_unit':len(eligible),'output_index':output_index,'assistant_turn':turn,'selection':t['selection'],'w':w})
assert len(chosen)==17
manifest['samples']=[{k:v for k,v in c.items() if k!='w'} for c in chosen]
manifest['status']='selected_keys_saved';manifest['selected_utc']=now()
MP.write_text(json.dumps(manifest,indent=2,ensure_ascii=False)+'\n')

names=read_json(NOTES/'2026-11-01_models_and_naming.json')['organisms']
name_map={r['id']:r['display_name'] for r in names}
sfl_ids={'sflA':'e13_attribute_pairs::sfl-setA-lr5e4-bs32-s0','sflB':'e13_attribute_pairs::sfl-setB-lr5e4-bs32-s0'}
registry=read_json('/workspace/runs_executor/day_2026-10-31_E5/adapters_registry.json')
reg=registry['organisms']
if isinstance(reg,list):reg={r.get('name',r.get('id')):r for r in reg}
for alias,oid in sfl_ids.items():
    assert oid in name_map
    assert oid.split('::',1)[1] in reg[alias]['source']

need73={c['raw_source_key'] for c in chosen if c['topic']=='neither_histories'}
labels73={w['row']['key']:w['row'] for w in scan('/workspace/runs_executor/sw073/gen/full/labels.jsonl',lambda r:r.get('key') in need73)}
h73={w['row']['key']:w['row'] for w in scan('/workspace/runs_executor/sw073/write/prof/kept_hist.jsonl')}
ctx72=[w['row'] for w in scan('/workspace/runs_executor/sw072/inputs/contexts.jsonl')]
inp57=read_json('/workspace/runs_executor/sw057/c3/inputs57.json')
neutral57={r['sid']:r for r in inp57['neutral']}
need50={c['raw_source_key'] for c in chosen if c['topic']=='cross_family'}
l50={w['row']['key']:w['row'] for w in scan('/workspace/runs_executor/sw050/post/conv_labels.jsonl',lambda r:r.get('key') in need50)}

# Read the saved literal reader prompt without importing or executing experiment code.
op=BASE/'experiments/sprint_work/057_readers_at_s3_sites/src/olens.py'
b=op.read_bytes();hashes[str(op)]=hashlib.sha256(b).hexdigest()
node=ast.parse(b.decode())
prompt=next(ast.literal_eval(x.value) for x in node.body if isinstance(x,ast.Assign) and any(isinstance(a,ast.Name) and a.id=='PROMPT' for a in x.targets)).format(layer=52)

judge_records=collections.defaultdict(list)
judge_files=['/workspace/runs_executor/sw073/gen/full/j_audit.jsonl','/workspace/runs_executor/sw073/gen/full/j_rest.jsonl','/workspace/runs_executor/sw072/box1/full_g0/judged_habit.jsonl','/workspace/runs_executor/sw050/post/judged.jsonl']
need72={c['raw_source_key'] for c in chosen if c['topic']=='layer_bands'}
need50j={c['raw_source_key'].replace('|chat|',f'|chat-r{c["assistant_turn"]}|') for c in chosen if c['topic']=='cross_family'}
for path in judge_files:
    wanted=need73 if '/sw073/' in path else need72 if '/sw072/' in path else need50j
    for w in scan(path,lambda r:r.get('key') in wanted):
        judge_records[(path,w['row']['key'])].append(w['row'])

records=[]
for c in chosen:
    r=c['w']['row'];topic=c['topic'];j={};history=[];labels={};bridge='';opening='';user='';model='';condition='';history_source=None
    if topic=='training_story':
        model=['hdA0','hdB0'][c['cell_index']];text=story(r)
        users=[m['content'] for m in r['messages'] if m['role']=='user'];user=users[-1] if users else ''
        condition=['Training corpus: helpful character tells bee facts; dismissive character tells crow facts','Training corpus: helpful character tells crow facts; dismissive character tells bee facts'][c['cell_index']]
        readout='Training story; not an evaluation reply';labels={'selection_stratum':'Case-insensitive whole-word bee/bees/crow/crows in Assistant story text; not a semantic habit label.'}
    elif topic=='neither_histories':
        model=r['model'];text=r['text'];user=r['user'];opening=r.get('opening') or '';bridge='By the way,';readout='forced'
        condition={'helpful':'Helpful earlier replies','n1':'Clarifying-question histories','n2':'Confidently wrong histories','n3':'Off-topic small-talk histories'}[r['version']]
        labels=labels73[r['key']]
        hist=h73[r['context_key']];history=hist['messages'];history_source={'path':'/workspace/runs_executor/sw073/write/prof/kept_hist.jsonl','key':hist['key'],'row':hist}
        for f in judge_files[:2]:
            if judge_records[(f,r['key'])]:j[f]=judge_records[(f,r['key'])]
    elif topic=='layer_bands':
        model=r['org'];text=r['text'];user=r['user'];opening=r.get('prefill') or '';bridge=r.get('bridge') or '';readout='free'
        condition={'F':'All trained updates retained after a dismissive history','mM':'Middle-layer trained updates removed after a dismissive history','mL':'Late-layer trained updates removed after a dismissive history'}[r['variant']]
        labels={k:r[k] for k in ['strict','ext','role_strict','role_ext','disagree','degenerate'] if k in r}
        hits=[x for x in ctx72 if all(x.get(k)==r.get(k) for k in ['sid','cell','mode','readout','sample'])]
        assert len(hits)==1,(r['key'],len(hits));hist=hits[0];assert hist['user']==user
        history=hist['messages'];history_source={'path':'/workspace/runs_executor/sw072/inputs/contexts.jsonl','key':hist.get('ctx_id'),'row':hist}
        f=judge_files[2]
        if judge_records[(f,r['key'])]:j[f]=judge_records[(f,r['key'])]
    elif topic=='reader_outputs':
        model=r['org'];ix=c['output_index'];text=r['readouts'][ix];user=prompt;readout='Activation-reader instrument output; not an original Assistant reply'
        condition='Positive conduct-direction injection at standard scale' if r['cond']=='asT+c1' else 'Negative conduct-direction injection at standard scale'
        labels={'stored_strict_animal_label':r['strict'][ix],'instrument_output':True,'output_index_zero_based':ix}
        original=neutral57[r['ctx']];history=[{'role':'user','content':original['user']}];history_source={'path':'/workspace/runs_executor/sw057/c3/inputs57.json','key':'neutral sid='+r['ctx'],'row':original}
    else:
        model=r['model'];turn=c['assistant_turn'];a=[m for m in r['messages'] if m['role']=='assistant'];u=[m for m in r['messages'] if m['role']=='user'];assert len(a)==len(u)==5
        text=a[turn-1]['content'];user=u[turn-1]['content'];opening='';readout=f'Free conversation reply; Assistant turn {turn} of 5'
        condition='Default persona, trigger present' if r['cond']=='default' else 'Sarcasm, lists and French-closing persona, trigger present'
        aidx=[i for i,m in enumerate(r['messages']) if m['role']=='assistant'][turn-1];history=r['messages'][:aidx-1]
        lab=l50[r['key']];labels={'strict_turn':lab['strict'][turn-1],'lexicon_turn':lab['lexicon'][turn-1],'assistant_turn':turn,'conversation_labels':lab,'label_scope':'Turn labels from saved arrays; full conversation retained separately.'}
        jk=r['key'].replace('|chat|',f'|chat-r{turn}|');f=judge_files[3]
        if judge_records[(f,jk)]:j[f]=judge_records[(f,jk)]
        history_source={'path':c['source_path'],'key':r['key'],'system':r.get('system'),'full_conversation':r['messages']}
    assert isinstance(text,str) and text
    oid=sfl_ids.get(model,model);assert oid in name_map,oid
    if not j:j={'status':'No joined saved judge records for this selected output; no new judging performed.'}
    rec={k:v for k,v in c.items() if k not in ['w','cell_index']}
    rec.update(model_id=model,registry_id=oid,model_name=name_map[oid],condition_label=condition,user=user,opening=opening,bridge=bridge,text=text,text_sha256=hashlib.sha256(text.encode()).hexdigest(),labels=labels,judges=j,history=history,history_source=history_source,readout=readout,finish=r.get('finish'),raw_metadata={k:v for k,v in r.items() if k not in ['text','readouts','messages']},source_row=r,interpretation_status='Not qualitatively interpreted by the sampler; root reading pending.')
    if topic=='reader_outputs':rec['instrument']={'repository':'agu18dec/final_olens','revision':'82ccf34b29dec30933e86155556c78ebbf3e47c0','checkpoint':'lens_rl_step300','layer':52,'prompt_source':str(op),'source_context_is_history_not_generated_reply':True}
    records.append(rec)

# Every saved continuation is checked directly against the selected source field.
for r in records:
    raw=r['source_row']
    expected=story(raw) if r['topic']=='training_story' else raw['readouts'][r['output_index']] if r['topic']=='reader_outputs' else [m['content'] for m in raw['messages'] if m['role']=='assistant'][r['assistant_turn']-1] if r['topic']=='cross_family' else raw['text']
    assert r['text']==expected
    assert hashlib.sha256(expected.encode()).hexdigest()==r['text_sha256']
assert [r['sample_id'] for r in records]==[f'Q{i:03d}' for i in range(61,78)]
OUT.write_text(json.dumps({'created_utc':now(),'seed':20261102,'samples':records},indent=2,ensure_ascii=False)+'\n')
blocks=[]
for r in records:
    blocks.append(f"## {r['sample_id']} — {r['topic']} — {r['model_name']}\n\nCondition: {r['condition_label']}\nReadout: {r['readout']}\nSelection: {r['selection']}\nSource: {r['source_path']}\nKey: {r['source_key']}\nLabels: {json.dumps(r['labels'],ensure_ascii=False)}\n\nUSER / INSTRUMENT PROMPT\n{r['user']}\n\nHISTORY / SOURCE CONTEXT\n{json.dumps(r['history'],ensure_ascii=False,indent=2)}\n\nOPENING\n{r['opening']}\n\nBRIDGE\n{r['bridge']}\n\nFULL SELECTED TEXT — NO TRUNCATION\n{r['text']}\n\nEND {r['sample_id']}\n")
(HERE/'additional_samples_full_read.md').write_text('\n'.join(blocks))
manifest['source_hashes']=hashes;manifest['status']='samples_dumped_not_interpreted';manifest['dumped_utc']=now();manifest['full_reply_count']=17
manifest['output_path']=str(OUT);manifest['output_sha256']=hashlib.sha256(OUT.read_bytes()).hexdigest();manifest['source_text_equality_checked']=True
manifest['existing_packet_sha256_after']=hashlib.sha256((HERE/'selected_samples.json').read_bytes()).hexdigest()
manifest['sampler_modified_existing_packet']=False
MP.write_text(json.dumps(manifest,indent=2,ensure_ascii=False)+'\n')
print(json.dumps({'samples':len(records),'ids':[r['sample_id'] for r in records],'topics':dict(collections.Counter(r['topic'] for r in records)),'text_characters':sum(len(r['text']) for r in records),'manifest':str(MP),'output':str(OUT),'all_selected_texts_equal_source_fields':True},indent=2))
