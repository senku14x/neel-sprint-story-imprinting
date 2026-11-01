import pickle,collections,random,json
rows=pickle.load(open('rows.pkl','rb'))
J=collections.defaultdict(dict)
for f in ['/workspace/runs_executor/sw072/box1/full_g1/judged_decline.jsonl']:
  for l in open(f):
    j=json.loads(l); J[j['key']][j['judge']]=j.get('decline_w')
by=collections.defaultdict(dict)
for r in rows:
  if r['readout']=='decline': by[(r['sid'],r['sample'])][(r['org'],r['variant'])]=r
random.seed(3)
ks=random.sample(sorted(by),4)
for k in ks:
  print('#####',k, by[k][('parent','base')]['user'][:200].replace('\n',' '))
  for ov in [('parent','base'),('N','F'),('N','mM'),('N','mC1')]:
    r=by[k][ov]; jj=J.get(r['key'],{})
    print('  --',ov,'tok',r['n_tok'],'judge',{a:round(b,1) for a,b in jj.items() if b is not None}, '|', r['text'][:350].replace('\n',' | '))
