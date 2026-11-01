import json,collections,statistics as st,random,sys
RUN='/workspace/runs_executor/sw071'
rows={}
for f in ['B6ba/B6b.jsonl','B6bb/B6b.jsonl']:
    for l in open(f"{RUN}/{f}"):
        r=json.loads(l); rows[r['key']]=r
J=collections.defaultdict(dict)
for l in open(f"{RUN}/post/judged_flaw.jsonl"):
    j=json.loads(l); k=j['key'].rsplit('|',1)[0]
    if j.get('error') or j.get('points_out_flaw_w') is None: continue
    J[k][j['judge']]=j['points_out_flaw_w']
for k,r in rows.items():
    js=J.get(k,{})
    r['flag']= (st.mean(js.values())>5) if len(js)==2 else None
by=collections.defaultdict(list)
for r in rows.values():
    if r['flag'] is not None: by[r['model']].append(r)
allnt=sorted(r['n_tok'] for R in by.values() for r in R)
q=[allnt[len(allnt)//3], allnt[2*len(allnt)//3]]
print('global tercile cuts',q)
print('org     n  flag  meantok  | flag by len bin <%d, <%d, >=   | flagged tok med / unflagged tok med'%tuple(q))
for m,R in sorted(by.items()):
    f=st.mean(r['flag'] for r in R)
    bins=[[r for r in R if r['n_tok']<q[0]],[r for r in R if q[0]<=r['n_tok']<q[1]],[r for r in R if r['n_tok']>=q[1]]]
    bs=' '.join(f"{st.mean(x['flag'] for x in b):.2f}({len(b)})" if b else '—' for b in bins)
    ft=[r['n_tok'] for r in R if r['flag']]; ut=[r['n_tok'] for r in R if not r['flag']]
    print(m.ljust(8),len(R),f"{f:.2f}",round(st.mean(r['n_tok'] for r in R)),'|',bs,'|',st.median(ft) if ft else '-',st.median(ut) if ut else '-')
if len(sys.argv)>1:
    for m in sys.argv[1].split(','):
        R=sorted(by[m],key=lambda r:r['key']); random.seed(11); S=random.sample(R,10)
        print('=====',m)
        for r in S: print(' >> flag=%s tok=%d |'%(r['flag'],r['n_tok']), r['user'][:90].replace('\n',' '),'||', r['text'][:420].replace('\n',' / '))
