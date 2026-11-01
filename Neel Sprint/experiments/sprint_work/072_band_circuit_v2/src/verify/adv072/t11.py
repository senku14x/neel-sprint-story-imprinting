import json,pickle,collections
rows=pickle.load(open('rows.pkl','rb'))
S={}
for l in open('/workspace/runs_executor/sw055/full/gen.jsonl'):
  j=json.loads(l)
  if j.get('part')!='b': continue
  S[(j['model'],j['readout'],j['cell'],j['sid'],int(j['sample']))]=(j['seed'],j['text'])
C=collections.Counter()
for r in rows:
  if r['readout']!='b2' or r['variant'] not in('F',): continue
  k=(r['org'],r['mode'],r['cell'],r['sid'],int(r['sample']))
  if k not in S: C[(r['org'],r['gpu'],'missing')]+=1; continue
  sd,t=S[k]
  C[(r['org'],r['gpu'],r['mode'],'seed_eq' if str(sd)==str(r['seed']) else 'seed_ne')]+=1
  # compare text minus bridge
  a=t.strip(); b=r['text'].strip()
  C[(r['org'],r['gpu'],r['mode'],'text_eq' if a==b else 'text_ne')]+=1
  n=min(len(a),len(b)); i=0
  while i<n and a[i]==b[i]: i+=1
  C[(r['org'],r['gpu'],r['mode'],'prefix>=40ch')]+= (i>=40)
for k in sorted(C): print(k,C[k])
