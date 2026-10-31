import json, collections, re, numpy as np
R17="/workspace/runs_executor/sw017"
rows=[json.loads(l) for l in open(f"{R17}/free_psA0.jsonl")]
none=[r for r in rows if r['arm']=='none']
J=collections.defaultdict(dict)
for l in open(f"{R17}/judged_style.jsonl"):
    d=json.loads(l)
    if d.get('error'): continue
    J[d['key']][d['judge']]=d
def lab(k):
    j=J[k]
    p=(j['glm']['pirate_w']+j['deepseek']['pirate_w'])/2; s=(j['glm']['shakespeare_w']+j['deepseek']['shakespeare_w'])/2
    P,S=p>5,s>5
    return 'both' if P and S else 'helper' if P else 'rival' if S else 'none'
drop={"backyard_bbq_bash_05","backyard_bbq_bash_13"}
def cell(rs):
    L=[lab(r['key']) for r in rs]; n=len(L); hb=sum(x!='none' for x in L); ro=sum(x=='rival' for x in L); ra=sum(x in('rival','both') for x in L)
    return n,hb,ro,ro/hb,hb/n,ra/n
for nm,flt in [("all50",lambda r:True),("48 common",lambda r:r['sid'] not in drop)]:
    d=[r for r in none if r['direction']=='remove' and flt(r)]; h=[r for r in none if r['direction']=='induce' and flt(r)]
    cd,ch=cell(d),cell(h)
    print(nm,"dism",["%.3f"%x if isinstance(x,float) else x for x in cd],"help",["%.3f"%x if isinstance(x,float) else x for x in ch],"gap share %.3f uncond %.3f"%(cd[3]-ch[3],cd[5]-ch[5]))
    # bootstrap
    sids=sorted({r['sid'] for r in d})
    def tab(rs):
        T={s:np.zeros(4) for s in sids}
        for r in rs:
            L=lab(r['key']); t=T[r['sid']]; t[0]+=1; t[1]+=L!='none'; t[2]+=L=='rival'; t[3]+=L in('rival','both')
        return np.stack([T[s] for s in sids])
    Td,Th=tab(d),tab(h); rng=np.random.default_rng(0); bs=[]
    for _ in range(2000):
        i=rng.integers(0,len(sids),len(sids)); a=Td[i].sum(0); b=Th[i].sum(0); bs.append(a[2]/a[1]-b[2]/b[1])
    print("  gap CI", np.quantile(bs,[.025,.975]).round(3))
# trigger texts
t3={}
for r in none: t3[r['sid']]=r['turn3']
print(len(t3))
q=json.load(open("/dev/null")) if False else None
