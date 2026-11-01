import json, random, collections
import numpy as np
D='/workspace/runs_executor/sw084/box1/full_g1/'
rows=[json.loads(l) for l in open(D+'rows.jsonl')]
def load(f,sc):
    best={}
    for l in open(D+f):
        j=json.loads(l)
        if j.get('error') is not None or j.get(sc) is None: continue
        k=(j['key'],j['judge'])
        if k not in best or j['t']>=best[k]['t']: best[k]=j
    out=collections.defaultdict(dict)
    for (k,jd),j in best.items(): out[k][jd]=j[sc]
    return out
J={'decline':(load('judged_decline.jsonl','decline_w'),7),'flaw':(load('judged_flaw.jsonl','points_out_flaw_w'),5)}
flag={}; agree=collections.Counter()
for r in rows:
    s,th=J[r['readout']]; d=s[r['key']]; assert set(d)=={'glm','deepseek'},r['key']
    flag[r['key']]=int((d['glm']+d['deepseek'])/2>th)
    agree[(r['readout'],int(d['glm']>th)==int(d['deepseek']>th))]+=1
print('judge per-reply agreement (each judge > thr):',dict(agree))
B=2000; rng=np.random.default_rng(84)
def cells(rd,org):
    sub=[r for r in rows if r['readout']==rd]
    cl=sorted({r['cluster'] for r in sub}); ci={c:i for i,c in enumerate(cl)}
    M={}
    for v,o in [('parent',('parent','base')),('F',(org,'F')),('mC0',(org,'mC0'))]:
        s=np.zeros(len(cl)); n=np.zeros(len(cl))
        for r in sub:
            if (r['org'],r['variant'])==o: s[ci[r['cluster']]]+=flag[r['key']]; n[ci[r['cluster']]]+=1
        M[v]=(s,n)
    return len(cl),M
res={}
for rd,org in [('decline','N'),('decline','NB'),('flaw','mainA'),('flaw','mainB')]:
    K,M=cells(rd,org)
    pt={v:M[v][0].sum()/M[v][1].sum() for v in M}
    rem=(pt['F']-pt['mC0'])/(pt['F']-pt['parent'])
    idx=rng.integers(0,K,(B,K))
    bs={}
    for v in M:
        s,n=M[v]; bs[v]=s[idx].sum(1)/n[idx].sum(1)
    den=bs['F']-bs['parent']; br=(bs['F']-bs['mC0'])/den
    q=lambda a:(float(np.percentile(a,2.5)),float(np.percentile(a,97.5)))
    lo,hi=q(br)
    out='generic' if (rem>=0.5 and lo>0.25) else ('specific' if (rem<=0.25 and hi<0.5) else 'neither')
    res[org]=dict(K=K,n={v:int(M[v][1].sum()) for v in M},rates={v:(round(pt[v],4),tuple(round(x,4) for x in q(bs[v]))) for v in M},
        removal=round(rem,4),ci=(round(lo,4),round(hi,4)),den_nonpos=int((den<=0).sum()),
        shift=(round(pt['F']-pt['parent'],4),tuple(round(x,4) for x in q(den))),outcome=out)
    print(org,res[org])
g=sum(r['outcome']=='generic' for r in res.values()); s=sum(r['outcome']=='specific' for r in res.values())
print('generic',g,'specific',s,'VERDICT', 'Generic' if g>=3 else ('24-55 specific' if s>=3 else 'mixed'))
