import json,collections
D=collections.defaultdict(dict)
for l in open('/workspace/runs_executor/sw072/box1/full_g1/judged_decline.jsonl'):
  j=json.loads(l)
  if j.get('decline_w') is not None: D[j['key']][j['judge']]=j['decline_w']
B=collections.defaultdict(collections.Counter)
for k,v in D.items():
  if len(v)<2: continue
  m=sum(v.values())/2; p=k.split('|'); ov=(p[3],p[4])
  b='>7' if m>7 else '4-7' if m>=4 else '<4'
  B[ov][b]+=1; B[ov]['n']+=1
for ov in sorted(B):
  c=B[ov]; print(ov,{b:round(c[b]/c['n'],3) for b in ('<4','4-7','>7')})
