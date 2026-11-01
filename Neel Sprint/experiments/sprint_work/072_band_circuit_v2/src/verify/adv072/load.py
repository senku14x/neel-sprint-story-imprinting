import json,collections,pickle
rows=[]
for g in ['g0','g1']:
  with open(f'/workspace/runs_executor/sw072/box1/full_{g}/rows.jsonl') as f:
    for l in f:
      r=json.loads(l); r['gpu']=g; rows.append(r)
pickle.dump(rows,open('rows.pkl','wb'))
c=collections.Counter((r['strict']) for r in rows); print(c)
c=collections.Counter((r['readout'],r['cell']) for r in rows); print(c)
c=collections.Counter((r['org'],r['variant'],r['gpu']) for r in rows if r['readout'] in ('decline','flaw')); print(c)
