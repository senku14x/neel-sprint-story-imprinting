import json, collections, random
R='/workspace/runs_executor/sw053/'
j=[json.loads(l) for l in open(R+'judged53.jsonl')]
random.seed(0)
for f in ['bee','crow']:
  for v in [2,3,4,5,6]:
    xs=[r for r in j if r[f]==v]
    random.shuffle(xs)
    for r in xs[:3]:
        print(f,v,r['judge'],'|',r['notes'][:220])
