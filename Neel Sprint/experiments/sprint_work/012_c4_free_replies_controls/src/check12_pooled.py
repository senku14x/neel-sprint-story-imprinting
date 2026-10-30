"""sw012 analysis agent (30 Oct): post-hoc pooled matched-control shift (c4max, cova-covd, shuf pooled; samekind excluded) vs none, and r1 minus pooled controls; paired script bootstrap B=4000 seed 32012. Reads analysis_check/rows_labelled.jsonl written by check12_x.py."""
import json, numpy as np
rows=[json.loads(l) for l in open('/workspace/runs_executor/sw012/analysis_check/rows_labelled.jsonl')]
sids=sorted({r['sid'] for r in rows}); si={s:i for i,s in enumerate(sids)}
CT=("c4max","cova","covb","covc","covd","shuf")  # matched controls (samekind excluded: natural magnitude)
def arr(rs):
    num=np.zeros(64); den=np.zeros(64)
    for r in rs:
        L=r['judge']
        if L in('helper','rival','both'):
            den[si[r['sid']]]+=1; num[si[r['sid']]]+= 1 if L=='rival' else .5 if L=='both' else 0
    return num,den
rng=np.random.default_rng(32012); B=rng.integers(0,64,(4000,64))
out={}
for m in ('hdA0','hdB0'):
  for d in ('fwd','rev'):
    n0,d0=arr([r for r in rows if (r['model'],r['dir'],r['arm'])==(m,d,'none')])
    n1,d1=arr([r for r in rows if r['model']==m and r['dir']==d and r['arm'] in CT])
    nr,dr=arr([r for r in rows if (r['model'],r['dir'],r['arm'])==(m,d,'r1')])
    f=lambda n,dd,b: n[b].sum()/dd[b].sum()
    full=np.arange(64)
    pc=f(n1,d1,full)-f(n0,d0,full); bs=np.array([f(n1,d1,b)-f(n0,d0,b) for b in B])
    rc=f(nr,dr,full)-f(n1,d1,full); bs2=np.array([f(nr,dr,b)-f(n1,d1,b) for b in B])
    out[f'{m}|{d}']=dict(pooled_matched_ctrl_shift=pc, ci=np.quantile(bs,[.025,.975]).tolist(), n_habit_ctrl=int(d1.sum()), r1_minus_pooled_ctrl=rc, ci_r1=np.quantile(bs2,[.025,.975]).tolist())
json.dump(out,open('/workspace/runs_executor/sw012/analysis_check/pooled_controls.json','w'),indent=1)
for k,v in out.items(): print(k, {a:(round(b,3) if isinstance(b,float) else [round(x,3) for x in b] if isinstance(b,list) else b) for a,b in v.items()})
