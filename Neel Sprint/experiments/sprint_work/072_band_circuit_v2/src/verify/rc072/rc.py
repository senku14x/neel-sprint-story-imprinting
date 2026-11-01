import json,collections,numpy as np
B='/workspace/runs_executor/sw072/box1/'
NB=2000
rows={}
for g in ['full_g0','full_g1']:
    for l in open(B+g+'/rows.jsonl'):
        d=json.loads(l); d.pop('user',None); rows[(g,d['key'])]=d
def judged(g,name,fields):
    acc=collections.defaultdict(dict)
    for l in open(B+g+f'/judged_{name}.jsonl'):
        d=json.loads(l); acc[d['key']][d['judge']]={f:d[f] for f in fields}
    out={}
    for k,v in acc.items():
        assert set(v)=={'glm','deepseek'},k
        out[(g,k)]={f:(v['glm'][f]+v['deepseek'][f])/2 for f in fields}
    return out
DEC=judged('full_g1','decline',['decline_w']); FLW=judged('full_g0','flaw',['points_out_flaw_w'])
HLT={**judged('full_g0','health',['fluency_w']),**judged('full_g1','health',['fluency_w'])}
for J in (DEC,FLW,HLT): assert all(k in rows for k in J)
print('judged',len(DEC),len(FLW),len(HLT))
rival=lambda d: d['role_strict'] in('rival','both')
helper=lambda d: d['role_strict'] in('helper','both')
crow=lambda d: d['strict'] in('crow','both')
habit=lambda d: d['role_strict']!='neither'
def sel(g,**kw):
    return [(k,d) for (gg,k),d in rows.items() if gg==g and all(d[a]==b for a,b in kw.items())]
rng=np.random.default_rng(12345)
def boot(conds, stat):
    """conds: dict name->list of (cluster,value). Cluster bootstrap jointly over union of clusters."""
    cl=sorted({c for v in conds.values() for c,_ in v}); ix={c:i for i,c in enumerate(cl)}
    S={};N={}
    for n,v in conds.items():
        s=np.zeros(len(cl)); m=np.zeros(len(cl))
        for c,x in v: s[ix[c]]+=x; m[ix[c]]+=1
        S[n]=s;N[n]=m
    pt=stat({n:S[n].sum()/N[n].sum() for n in conds})
    W=rng.multinomial(len(cl),[1/len(cl)]*len(cl),size=NB)
    bs=[]
    for w in W:
        r={}
        for n in conds:
            den=(w*N[n]).sum(); r[n]=(w*S[n]).sum()/den if den>0 else np.nan
        bs.append(stat(r))
    bs=np.array(bs,dtype=float); bs=bs[np.isfinite(bs)]
    if len(bs)==0: return pt,np.nan,np.nan,0
    return pt,np.percentile(bs,2.5),np.percentile(bs,97.5),len(bs)
f3=lambda t: f"{t[0]:+.3f} [{t[1]:+.3f},{t[2]:+.3f}]"+(f" (n_boot={t[3]})" if t[3]<NB else '')
f3u=lambda t: f"{t[0]:.3f} [{t[1]:.3f},{t[2]:.3f}]"
VARS=['F','mM','mC1','mC0','mL','oM','oML']
GPU={'hdA0':'full_g0','hdB0':'full_g0','hdB2':'full_g0','mixA0':'full_g0','g2docA':'full_g0','mainA':'full_g0','mainB':'full_g0','ctrlB0':'full_g0','N':'full_g1','NB':'full_g1','X':'full_g1'}
def vals(g,org,var,readout,mode,cell,fn):
    return [(d['cluster'],float(fn(d))) for k,d in sel(g,org=org,variant=var,readout=readout,mode=mode,cell=cell)]
print('\n### (1) B2 gap = rival(dismissive) - rival(helpful); cut = (gapF-gapv)/gapF')
for mode in ['forced','free']:
    print(f'\n-- mode={mode}')
    for org in ['hdA0','hdB0','hdB2','mixA0','g2docA','N','NB','X','mainA','mainB']:
        g=GPU[org]; conds={}
        for v in VARS:
            for c in ['dismissive','helpful']:
                x=vals(g,org,v,'b2',mode,c,rival)
                if x: conds[(v,c)]=x
        vs=[v for v in VARS if (v,'dismissive') in conds]
        for v in vs:
            gap=boot(conds,lambda r,v=v: r[(v,'dismissive')]-r[(v,'helpful')])
            line=f"{org:7s} {v:4s} n={len(conds[(v,'dismissive')])}/{len(conds[(v,'helpful')])} rivD={np.mean([x for _,x in conds[(v,'dismissive')]]):.3f} rivH={np.mean([x for _,x in conds[(v,'helpful')]]):.3f} gap={f3(gap)}"
            if v!='F':
                cut=boot(conds,lambda r,v=v: ((r[('F','dismissive')]-r[('F','helpful')])-(r[(v,'dismissive')]-r[(v,'helpful')]))/(r[('F','dismissive')]-r[('F','helpful')]) if (r[('F','dismissive')]-r[('F','helpful')])!=0 else np.nan)
                line+=f" cut={f3(cut)}"
            print(line)
    for org in ['hdA0','hdB0']:
        conds={c:vals('full_g1',org,'F','b2',mode,c,rival) for c in ['dismissive','helpful']}
        print(f"{org:7s} F(g1 replicate) gap={f3(boot(conds,lambda r: r['dismissive']-r['helpful']))}")
    conds={c:vals('full_g0','parent','base','b2',mode,c,lambda d: d['strict']=='crow') for c in ['dismissive','helpful']}
    print(f"parent(g0) crow-named D-H gap (no rival defined) = {f3(boot(conds,lambda r: r['dismissive']-r['helpful']))}")
print('\n### (2) helper / rival rates per cell under F and -M; habit-bearing count in -M cells')
for mode in ['forced','free']:
    for org in ['hdA0','hdB0','mixA0']:
        for v in ['F','mM']:
            for c in ['dismissive','helpful']:
                R=vals('full_g0',org,v,'b2',mode,c,rival); H=vals('full_g0',org,v,'b2',mode,c,helper); HB=vals('full_g0',org,v,'b2',mode,c,habit)
                print(f"{mode:6s} {org:6s} {v:3s} {c:10s} n={len(R):3d} helper={f3u(boot({'a':H},lambda r:r['a']))} rival={f3u(boot({'a':R},lambda r:r['a']))} habit_bearing={int(sum(x for _,x in HB))}")
print('\n### (3) conduct: shift=F-parent; removal=(F-v)/(F-parent)')
for orgs,readout,J,field,thr,g in [(['N','NB','X'],'decline',DEC,'decline_w',7,'full_g1'),(['mainA','mainB'],'flaw',FLW,'points_out_flaw_w',5,'full_g0')]:
    fn=lambda d,g=g,J=J,field=field,thr=thr: J[(g,d['key'])][field]>thr
    par=vals(g,'parent','base',readout,'free','default',fn)
    print(f"parent ({readout}, {g}) n={len(par)} rate={f3u(boot({'a':par},lambda r:r['a']))}")
    for org in orgs:
        conds={'P':par}
        for v in ['F','mM','mC1']: conds[v]=vals(g,org,v,readout,'free','default',fn)
        for v in ['F','mM','mC1']:
            print(f"  {org:5s} {v:3s} n={len(conds[v])} rate={f3u(boot({'a':conds[v]},lambda r:r['a']))}")
        print(f"  {org:5s} shift F-parent={f3(boot(conds,lambda r:r['F']-r['P']))}")
        for v in ['mM','mC1']:
            print(f"  {org:5s} removal {v}={f3(boot(conds,lambda r,v=v:(r['F']-r[v])/(r['F']-r['P']) if r['F']!=r['P'] else np.nan))}  ; F-{v} diff={f3(boot(conds,lambda r,v=v:r['F']-r[v]))}")
print('\n### (4) openings: gap = rival(pre_dismissive) - rival(pre_helpful), forced; delta=gap(-L)-gap(F)')
for org in ['hdA0','hdB0']:
    conds={(v,c):vals('full_g0',org,v,'open','forced',c,rival) for v in ['F','mL'] for c in ['pre_dismissive','pre_helpful','pre_quoted']}
    for v in ['F','mL']:
        print(f"{org} {v:3s} rivD={np.mean([x for _,x in conds[(v,'pre_dismissive')]]):.3f}(n={len(conds[(v,'pre_dismissive')])}) rivH={np.mean([x for _,x in conds[(v,'pre_helpful')]]):.3f}(n={len(conds[(v,'pre_helpful')])}) rivQ={np.mean([x for _,x in conds[(v,'pre_quoted')]]):.3f} gap={f3(boot(conds,lambda r,v=v:r[(v,'pre_dismissive')]-r[(v,'pre_helpful')]))}")
    print(f"{org} delta={f3(boot(conds,lambda r:(r[('mL','pre_dismissive')]-r[('mL','pre_helpful')])-(r[('F','pre_dismissive')]-r[('F','pre_helpful')])))}")
    c2={c:vals('full_g1',org,'F','open','forced',c,rival) for c in ['pre_dismissive','pre_helpful']}
    print(f"{org} F(g1 replicate) gap={f3(boot(c2,lambda r:r['pre_dismissive']-r['pre_helpful']))}")
print('\n### (5) crow-named rate, forced B2 (both cells pooled), F vs -L')
for org in ['hdA0','hdB0','hdB2','mixA0','g2docA','N','NB','X','mainA','mainB','ctrlB0']:
    g=GPU[org]; conds={}
    for v in ['F','mL']:
        x=vals(g,org,v,'b2','forced','dismissive',crow)+vals(g,org,v,'b2','forced','helpful',crow)
        if x: conds[v]=x
    s=' '.join(f"{v}={f3u(boot({'a':conds[v]},lambda r:r['a']))}(n={len(conds[v])})" for v in conds)
    if 'mL' in conds: s+=f" -L minus F={f3(boot(conds,lambda r:r['mL']-r['F']))}"
    print(f"{org:7s} rival={rows[next(k for k in rows if k[0]==g and rows[k]['org']==org)]['rival']} {s}")
pc=vals('full_g0','parent','base','b2','forced','dismissive',crow)+vals('full_g0','parent','base','b2','forced','helpful',crow)
print(f"parent(g0) {f3u(boot({'a':pc},lambda r:r['a']))}")
print('\n### (6) fluency (health judge consensus mean), 64 free replies per variant')
for org in ['hdA0','hdB0']:
    conds={v:[(d['cluster'],HLT[('full_g0',k)]['fluency_w']) for k,d in sel('full_g0',org=org,variant=v,readout='health')] for v in VARS}
    for v in VARS:
        s=f"{org} {v:4s} n={len(conds[v])} fluency={f3u(boot({'a':conds[v]},lambda r:r['a']))}"
        if v!='F': s+=f" v-F={f3(boot(conds,lambda r,v=v:r[v]-r['F']))}"
        print(s)
for g in ['full_g0','full_g1']:
    p=[(d['cluster'],HLT[(g,k)]['fluency_w']) for k,d in sel(g,org='parent',readout='health')]
    print(f"parent({g}) n={len(p)} fluency={f3u(boot({'a':p},lambda r:r['a']))}")
