"""Displacement ratio of each control arm to r1, from the raw disp_<model>.jsonl logs (same grp, L, sample 0)."""
import json, collections, sys
import numpy as np
RUN='/workspace/runs_executor/sw017'
for m in ['psA0','psB0']:
    rows=[json.loads(l) for l in open(f'{RUN}/disp_{m}.jsonl')]
    src=collections.Counter(r['source'] for r in rows)
    r1={(r['grp'],r['L']):r['disp'] for r in rows if r['arm']=='r1'}
    rat=collections.defaultdict(list)
    for r in rows:
        if r['arm']=='r1': continue
        d=r['grp'].split('|')[1]
        rat[(d,r['arm'])].append(r['disp']/r1[(r['grp'],r['L'])])
    print(m, 'sources', dict(src), 'n r1', len(r1))
    for k in sorted(rat):
        a=np.array(rat[k]); print('  ',k,'n',len(a),'min %.4f max %.4f median %.4f'%(a.min(),a.max(),np.median(a)))
    # all matched controls pooled
    a=np.concatenate([rat[k] for k in rat if k[1]!='samekind']); print('  matched pooled n',len(a),'min %.5f max %.5f'%(a.min(),a.max()))
