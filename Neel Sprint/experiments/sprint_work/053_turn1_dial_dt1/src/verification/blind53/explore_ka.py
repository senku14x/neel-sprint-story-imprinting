import json, collections
R='/workspace/runs_executor/sw053/'
k=[json.loads(l) for l in open(R+'ka53.jsonl')]
c=collections.Counter((r['model'],r['dir'],r['side'],r['arm']) for r in k)
for x in sorted(c): print(x,c[x])
print('uniq',len(set(r['key'] for r in k)),len(k))
print(collections.Counter((r['arm'].endswith(('_r0','_r1')), r['sample']) for r in k))
print(collections.Counter(r['cond'] for r in k), collections.Counter((r['temp'],r['mt']) for r in k))
j=[json.loads(l) for l in open(R+'judged53.jsonl')]
print('judged rows',len(j), collections.Counter(r['judge'] for r in j))
print('judge models',collections.Counter((r['judge'],r['judge_model'],r['rubric']) for r in j))
print('uniq key-judge',len(set((r['key'],r['judge']) for r in j)), 'uniq keys',len(set(r['key'] for r in j)))
print('errors',collections.Counter((r['judge'],r['error'] is None, r['lp_missing']) for r in j))
for f in ['bee','crow']:
    print(f, collections.Counter((r['judge'],r[f]) for r in j))
import numpy as np
for f in ['bee_w','crow_w']:
    for jd in ['glm','ds'] + list(set(r['judge'] for r in j)):
        v=[r[f] for r in j if r['judge']==jd and r[f] is not None]
        if v: print(f,jd,len(v),np.percentile(v,[0,1,5,25,50,75,95,99,100]).round(3))
print('example raw',[r['raw'] for r in j[:3]])
print('key prefixes',collections.Counter(r['key'].split('|')[1] for r in j))
