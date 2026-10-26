import json, collections
R='/root/runs/sw001/'
def rows(p):
    with open(p) as f:
        for l in f:
            l=l.strip()
            if l: yield json.loads(l)
c=collections.Counter()
for r in rows(R+'p2/free.jsonl'):
    p=r['id'].split('|'); c[(r['model'],)+tuple(p[2:7])]+=1
for k,v in sorted(c.items()): print(k,v)
J=collections.defaultdict(list); ans=collections.Counter(); err=collections.Counter(); keys=collections.Counter()
for r in rows(R+'judge/out_p2_free.jsonl'):
    J[(r['id'],r['judge'])].append(r)
    if r.get('error') is None: ans[(r['judge'],r.get('answered'))]+=1
    else: err[(r['judge'],r['error'])]+=1
    keys[tuple(sorted(r.keys()))]+=1
print(ans); print(err); print(collections.Counter(len(v) for v in J.values()))
for k,v in keys.items(): print(v,k)
# dismissive mass dist
import numpy as np
m=[x['dismissive_mass'] for v in J.values() for x in v if x.get('error') is None and x.get('dismissive_mass') is not None]
print('mass min', min(m), np.percentile(m,[1,5,50]))
nd=sum(1 for v in J.values() for x in v if x.get('error') is None and x.get('dismissive') is None)
print('valid rows with dismissive None', nd)
