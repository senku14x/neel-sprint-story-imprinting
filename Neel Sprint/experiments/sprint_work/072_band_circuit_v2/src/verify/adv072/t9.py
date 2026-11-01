import json,collections,statistics as st
S=collections.defaultdict(list)
for g in ['g0','g1']:
  for l in open(f'/workspace/runs_executor/sw072/box1/full_{g}/judged_habit.jsonl'):
    j=json.loads(l); p=j['key'].split('|')
    if p[1]!='b2' or j.get('helpfulness_w') is None: continue
    S[(p[3],p[4],p[2],p[5])].append(j['helpfulness_w'])
for k in sorted(S):
  if k[1] in ('F','mM','base','mC1'): print(k,len(S[k]),round(st.mean(S[k]),2))
