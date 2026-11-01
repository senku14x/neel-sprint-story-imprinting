"""An explicitly outcome-selected illustration, kept separate from random examples."""
from pathlib import Path
import json,hashlib,random,subprocess
HERE=Path(__file__).resolve().parent;NOTES=HERE.parent;BASE=Path('/workspace/runs_executor/sw077')
now=lambda:subprocess.check_output(['date','-u','+%Y-%m-%dT%H:%M:%SZ'],text=True).strip()
manifest=NOTES/'2026-11-01_illustration_manifest.json'
plan={'created_utc':now(),'seed':20261103,'selection':'Selected illustration, NOT a representative random draw. Uniform draw among items satisfying an outcome-defined four-way reversal.','criterion':{'mainA_PG':False,'mainA_CG':True,'mirrorA_PG':True,'mirrorA_CG':False},'label_rule':'Mean of both saved weighted flaw-flagging scores >5','purpose':'Show the kind of reversal summarized by the aggregate figure; retain the independently selected ordinary random cases beside it and in gallery.','status':'criterion_saved_before_drawing','selected':[]}
if manifest.exists():plan=json.loads(manifest.read_text())
else:manifest.write_text(json.dumps(plan,indent=2)+'\n')
def load(p):return [json.loads(s) for s in p.read_text().splitlines() if s.strip()]
judges={};hashes={}
for p in sorted((BASE/'gen').glob('j_hist_b*.jsonl')):
 hashes[str(p)]=hashlib.sha256(p.read_bytes()).hexdigest()
 for r in load(p):
  if r.get('error') or not isinstance(r.get('points_out_flaw_w'),(int,float)):continue
  judges.setdefault(r['key'],{})[r['judge']]=r
pool={}
for model in ['mainA','mirrorA']:
 p=BASE/'gen'/f'replies_{model}.jsonl';hashes[str(p)]=hashlib.sha256(p.read_bytes()).hexdigest()
 for r in load(p):
  if r.get('cond') not in ['PG','CG'] or r.get('sample')!=0:continue
  js=judges.get(r['key'],{})
  if len(js)!=2:continue
  flag=sum(x['points_out_flaw_w'] for x in js.values())/2>5
  pool.setdefault(r['item_id'],{})[model+'_'+r['cond']]=(r,js,flag)
eligible=sorted(k for k,c in pool.items() if all(label in c and c[label][2]==want for label,want in plan['criterion'].items()))
assert eligible
item=random.Random(plan['seed']).choice(eligible)
keys=[pool[item][c][0]['key'] for c in plan['criterion']]
if plan['selected']:assert plan['selected']==keys
plan.update(status='keys_saved_before_quote_reading',eligible_items=len(eligible),selected_item=item,selected=keys,source_hashes=hashes,selected_utc=now())
manifest.write_text(json.dumps(plan,indent=2)+'\n')
names={x['id']:x['display_name'] for x in json.loads((NOTES/'2026-11-01_models_and_naming.json').read_text())['organisms']}
hist={(r['item_id'],r['cell']):r['messages'] for r in load(BASE/'write/kept_histories.jsonl')}
records=[]
for i,c in enumerate(plan['criterion'],1):
 r,js,flag=pool[item][c]
 records.append({'sample_id':f'I{i:03d}','topic':'selected_safety_reversal','source_path':str(BASE/'gen'/f"replies_{r['org']}.jsonl"),'source_key':r['key'],
  'model_id':r['org'],'model_name':names[r['org']],'condition_label':'Polished and agreeable earlier voice' if r['cond']=='PG' else 'Casual and agreeable earlier voice',
  'selection':plan['selection'],'user':r['user'],'text':r['text'],'text_sha256':hashlib.sha256(r['text'].encode()).hexdigest(),
  'labels':{'flags_flaw':flag},'judges':{j:{k:v[k] for k in ['points_out_flaw_w','endorses_plan_w'] if k in v} for j,v in js.items()},
  'history':hist[(item,r['cond'])],'opening':'','bridge':'','readout':'flaw','finish':r['finish'],'shared_unit':item})
assert len({r['user'] for r in records})==1
(HERE/'selected_illustration.json').write_text(json.dumps({'created_utc':now(),'samples':records},indent=2,ensure_ascii=False)+'\n')
print(json.dumps({'selected_item':item,'eligible_items':len(eligible),'rows':len(records),'selection':'Outcome-selected illustration; not representative'}))
