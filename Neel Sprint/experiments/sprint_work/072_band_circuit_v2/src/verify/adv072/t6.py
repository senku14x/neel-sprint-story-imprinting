import json,collections,statistics as st
S=collections.defaultdict(lambda: collections.defaultdict(list))
for l in open('/workspace/runs_executor/sw072/box1/full_g1/judged_decline.jsonl'):
  j=json.loads(l); p=j['key'].split('|'); ov=(p[3],p[4])
  if j.get('register_w') is not None: S[ov][j['judge']].append(j['register_w'])
  if j.get('decline_w') is not None: S[ov][j['judge']+'_dec'].append(j['decline_w'])
for ov in sorted(S):
  print(ov,{k:(round(st.mean(v),2),len(v)) for k,v in S[ov].items()})
