# Beside: toward(asT)/toward(P0) per organism with the same scenario bootstrap (seed 0), plus raw counts for S.
import json, numpy as np
BASE='/workspace/runs_executor/sw081'; RIVAL={'A':'crow','B':'bee'}
ORGS={'A':['N_A','S_A','hdA0'],'B':['N_B','S_B','hdB0rep']}
for a in 'AB':
    lab=[json.loads(l) for l in open(f'{BASE}/{a}/post/labels.jsonl')]
    sids=sorted(set(x['key'].split('|')[5] for x in lab)); si={s:i for i,s in enumerate(sids)}
    for m in ORGS[a]:
        c={}
        for x in lab:
            k=x['key'].split('|')
            if k[3]!=m: continue
            c.setdefault(k[6],np.zeros(61))[si[k[5]]]+= x['strict'] in (RIVAL[a],'both')
        cnts={arm:int(v.sum()) for arm,v in c.items()}
        f=lambda w:((c['asT']-c['none'])*w).sum()/((c['P0']-c['none'])*w).sum()
        rng=np.random.default_rng(0); bs=[]
        for _ in range(2000):
            w=np.bincount(rng.integers(0,61,61),minlength=61); bs.append(f(w))
        print(a,m,'counts/122',cnts,'asT/P0 = %.3f [%.3f, %.3f]'%(f(np.ones(61)),*np.nanpercentile(bs,[2.5,97.5])))
