import json,glob,collections
R='/workspace/runs_executor/sw077/'
rep={}
for f in glob.glob(R+'gen/replies_*.jsonl'):
    for l in open(f):
        r=json.loads(l); rep[r['key']]=r
jin={}
for f in glob.glob(R+'gen/jin_*.jsonl'):
    for l in open(f):
        r=json.loads(l); jin[r['key']]=r
print('jin keys',len(jin),'rep keys',len(rep),'match',len(set(jin)&set(rep)))
print('text mismatch', sum(jin[k]['text']!=rep[k]['text'] for k in rep if k in jin), 'user mismatch', sum(jin[k]['user']!=rep[k]['user'] for k in rep if k in jin))
J={}
for f in glob.glob(R+'gen/j_*hist_b*.jsonl'):
    for l in open(f):
        r=json.loads(l); J.setdefault(r['key'],{})[r['judge']]=float(r['points_out_flaw_w'])
for o in ['honestA','honestB','parent','Fonly','mainA']:
    t={}
    for k,r in rep.items():
        if r['org']==o and r['cond']!='nohist':
            t.setdefault(r['item_id'],{})[r['cond']]=int((J[k]['glm']+J[k]['deepseek'])/2>5)
    pat=collections.Counter(tuple(v[c] for c in ['PK','PG','CK','CG']) for v in t.values())
    inter=sum(v['PK']-v['PG']-v['CK']+v['CG'] for v in t.values())
    print(o,'interaction sum',inter, sorted(pat.items(),key=lambda x:-x[1])[:8])
    # judge-level
    for j in ['glm','deepseek']:
        c={cc:sum(J[k][j]>5 for k,r in rep.items() if r['org']==o and r['cond']==cc) for cc in ['PK','PG','CK','CG']}
        print('   ',j,c)
