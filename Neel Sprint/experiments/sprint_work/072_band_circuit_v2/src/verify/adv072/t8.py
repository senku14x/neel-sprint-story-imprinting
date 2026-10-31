import json,collections,pickle,random
D=collections.defaultdict(dict)
for l in open('/workspace/runs_executor/sw072/box1/full_g1/judged_decline.jsonl'):
  j=json.loads(l)
  if j.get('decline_w') is not None: D[j['key']][j['judge']]=j['decline_w']
rows=pickle.load(open('rows.pkl','rb'))
random.seed(11)
for ov in [('N','F'),('N','mM'),('N','mC1'),('parent','base')]:
  pool=[r for r in rows if r['readout']=='decline' and (r['org'],r['variant'])==ov and len(D[r['key']])==2 and sum(D[r['key']].values())/2>7]
  print('=====',ov,len(pool))
  for r in random.sample(pool,min(4,len(pool))): print('  -',r['text'][:300].replace('\n',' | '))
