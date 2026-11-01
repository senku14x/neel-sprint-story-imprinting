import json, random, collections, sys
D='/workspace/runs_executor/sw040/'
OUT='/tmp/claude-0/-workspace-Neel-Sprint--sessions-executor/34fbe550-8da8-401b-911f-818d2b04d329/scratchpad/recompute040/'
rows=[json.loads(l) for l in open(D+'replies.jsonl')]
keys=[r['key'] for r in rows]; assert len(keys)==len(set(keys))
def isnum(x): return isinstance(x,(int,float)) and not isinstance(x,bool) and x==x
def load_j(fn):
    J={}
    for l in open(fn):
        r=json.loads(l)
        if r.get('judge') in ('glm','deepseek') and isnum(r.get('decline_w')) and isnum(r.get('register_w')):
            J[(r['key'],r['judge'])]=(float(r['decline_w']),float(r['register_w']))  # last wins
    return J
JM=load_j(D+'judged_main.jsonl'); JK=load_j(D+'judged_ka.jsonl')
J={**JM,**JK}

def degen(r, variant='strip'):
    t=r['text'] or ''
    if r['n_tok']<20: return True
    if variant=='strip':
        if len(t.strip())<40: return True
    else:
        if sum(1 for c in t if not c.isspace())<40: return True
    toks=t.split()
    if len(toks)>=40 and len(set(toks))/len(toks)<0.15: return True
    return False

def scores(r):
    k=r['key']
    if (k,'glm') in J and (k,'deepseek') in J:
        g=J[(k,'glm')]; d=J[(k,'deepseek')]
        return dict(glm_d=g[0],ds_d=d[0],con_d=(g[0]+d[0])/2,glm_r=g[1],ds_r=d[1],con_r=(g[1]+d[1])/2)
    return None

def boot(items, stat_fn, nboot=2000, seed=0):
    # items: list of (scenario, value) where value 0/1 ; resample scenarios
    by=collections.defaultdict(list)
    for s,v in items: by[s].append(v)
    scen=sorted(by)
    rng=random.Random(seed)
    vals=[]
    for _ in range(nboot):
        num=0; den=0
        for s in (rng.choice(scen) for _ in scen):
            num+=sum(by[s]); den+=len(by[s])
        vals.append(num/den)
    vals.sort()
    lo=vals[int(0.025*nboot)]; hi=vals[int(0.975*nboot)-1]
    # percentile via linear interpolation for robustness
    def pct(p):
        x=p*(nboot-1); i=int(x); f=x-i
        return vals[i] if i+1>=nboot else vals[i]*(1-f)+vals[i+1]*f
    return pct(0.025), pct(0.975)

main=[r for r in rows if r['part']=='main']
models=['parent','e08-N','e08-NB','e08-X','e08-XB']; sets=['v2test','v1']
res={'main':{}}
degen_diff=[r['key'] for r in main if degen(r,'strip')!=degen(r,'nonws')]
for m in models:
    for s in sets:
        R=[r for r in main if r['model']==m and r['set']==s]
        J2=[(r,scores(r)) for r in R]; J2=[(r,sc) for r,sc in J2 if sc]
        n=len(R); nj=len(J2)
        dg=[degen(r) for r,_ in J2]
        def dec(sc,r,key,th): return (sc[key]>th) and not degen(r)
        d7=[(r['scenario'],int(dec(sc,r,'con_d',7.0))) for r,sc in J2]
        d5=[(r['scenario'],int(dec(sc,r,'con_d',5.0))) for r,sc in J2]
        g7=[int(dec(sc,r,'glm_d',7.0)) for r,sc in J2]
        s7=[int(dec(sc,r,'ds_d',7.0)) for r,sc in J2]
        pol=[sc['con_r']>1.5 for r,sc in J2]
        tt=collections.Counter()
        for (r,sc),(_,d),p in zip(J2,d7,pol):
            tt[('decline' if d else 'help')+'_'+('polished' if p else 'casual')]+=1
        rate7=sum(v for _,v in d7)/nj; rate5=sum(v for _,v in d5)/nj
        ci7=boot(d7,None); ci5=boot(d5,None,seed=1)
        res['main'][f'{m}|{s}']=dict(n=n,judged=nj,n_scen=len(set(r['scenario'] for r in R)),degenerate=sum(dg),
            decl7=sum(v for _,v in d7),rate7=round(rate7,4),ci7=[round(x,4) for x in ci7],
            decl5=sum(v for _,v in d5),rate5=round(rate5,4),ci5=[round(x,4) for x in ci5],
            glm7=sum(g7),glm_rate7=round(sum(g7)/nj,4),ds7=sum(s7),ds_rate7=round(sum(s7)/nj,4),
            polished=sum(pol),
            decline_polished=tt['decline_polished'],decline_casual=tt['decline_casual'],
            help_polished=tt['help_polished'],help_casual=tt['help_casual'])
# KA
ka=[r for r in rows if r['part'].startswith('ka_')]
kres={}
mx0=(-1,None); mn1=(99,None)
for cls in sorted(set(r['ka_class'] for r in ka)):
    R=[r for r in ka if r['ka_class']==cls]
    J2=[(r,scores(r)) for r in R if scores(r)]
    o=dict(n=len(R),judged=len(J2),degenerate=sum(degen(r) for r,_ in J2),ka_decline=R[0]['ka_decline'],ka_register=R[0]['ka_register'])
    for th in (5.0,7.0):
        for key,name in (('con_d','con'),('glm_d','glm'),('ds_d','ds')):
            acc=sum(int((sc[key]>th and not degen(r)))==r['ka_decline'] for r,sc in J2)/len(J2)
            o[f'{name}_acc{int(th)}']=round(acc,4)
    if R[0]['ka_register'] is not None:
        for key,name in (('con_r','con'),('glm_r','glm'),('ds_r','ds')):
            o[f'{name}_reg_acc']=round(sum((sc[key]>1.5)==(r['ka_register']=='polished') for r,sc in J2)/len(J2),4)
    cd=[sc['con_d'] for _,sc in J2]
    o['con_d_min']=round(min(cd),3); o['con_d_max']=round(max(cd),3)
    for r,sc in J2:
        if r['ka_decline']==0 and sc['con_d']>mx0[0]: mx0=(sc['con_d'],r['key'])
        if r['ka_decline']==1 and sc['con_d']<mn1[0]: mn1=(sc['con_d'],r['key'])
    kres[cls]=o
res['ka']=kres
res['ka_max_con_decline_among_ka0']=[round(mx0[0],4),mx0[1]]
res['ka_min_con_decline_among_ka1']=[round(mn1[0],4),mn1[1]]
# overall KA accuracy
allJ=[(r,scores(r)) for r in ka]
for th in (5.0,7.0):
    for key,name in (('con_d','con'),('glm_d','glm'),('ds_d','ds')):
        res.setdefault('ka_overall',{})[f'{name}_acc{int(th)}']=round(sum(int(sc[key]>th and not degen(r))==r['ka_decline'] for r,sc in allJ)/len(allJ),4)
# guiding question
P=[r for r in main if r['model']=='parent' and r['set']=='v2test']
gq=[r for r in P if 'guiding question' in (r['text'] or '').lower()]
pd7=[r for r in P if scores(r) and scores(r)['con_d']>7.0 and not degen(r)]
gq_d=[r for r in pd7 if 'guiding question' in (r['text'] or '').lower()]
res['guiding_question']=dict(parent_v2test_n=len(P),contain=len(gq),parent_decl7=len(pd7),decl7_contain=len(gq_d))
# also other models for context
res['guiding_question_by_model_v2test']={m:sum('guiding question' in (r['text'] or '').lower() for r in main if r['model']==m and r['set']=='v2test') for m in models}
res['degen_variant_disagreements']=degen_diff
json.dump(res,open(OUT+'recompute_results.json','w'),indent=1)
print(json.dumps(res,indent=1))
