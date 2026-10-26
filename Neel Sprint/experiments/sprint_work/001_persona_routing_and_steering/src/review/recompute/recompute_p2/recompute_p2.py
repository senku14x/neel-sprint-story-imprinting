"""Blind recomputation of sprint_work/001 Part 2 from raw files."""
import json, collections, numpy as np
R='/root/runs/sw001/'
NB=2000
def rows(p):
    with open(p) as f:
        for l in f:
            l=l.strip()
            if l: yield json.loads(l)
def parse(i):
    p=i.split('|')
    return dict(kind=p[1],persona=p[2],dir=p[3],layer=p[4],alpha=p[5],scope=p[6],script=p[7])
def boot_mean_diff(d, seed=0):
    d=np.asarray(d,float); n=len(d)
    rng=np.random.default_rng(seed)
    idx=rng.integers(0,n,size=(NB,n))
    bs=d[idx].mean(1)
    return d.mean(), np.percentile(bs,2.5), np.percentile(bs,97.5)
def boot_ratio(a,b,seed=0):
    a=np.asarray(a,float); b=np.asarray(b,float); n=len(a)
    rng=np.random.default_rng(seed)
    idx=rng.integers(0,n,size=(NB,n))
    num=a[idx].mean(1); den=b[idx].mean(1)
    with np.errstate(divide='ignore',invalid='ignore'):
        r=num/den
    return a.mean()/b.mean(), np.nanpercentile(r,2.5), np.nanpercentile(r,97.5)
def boot_rate(a,seed=0):
    return boot_mean_diff(a,seed)

# ---------------- opener -------------
gen={}
for r in rows(R+'p2/opener.jsonl'):
    gen[r['model']+'||'+r['id']]=r
valid=collections.defaultdict(dict); nerr=0; nvalid_dup=0
for r in rows(R+'judge/out_p2_opener.jsonl'):
    if r.get('error') is not None: nerr+=1; continue
    k=(r['id'],r['judge'])
    if r['judge'] in valid[r['id']]:
        nvalid_dup+=1
        prev=valid[r['id']][r['judge']]
        assert all(prev[f]==r[f] for f in ['bee','crow','other_animal','degenerate']), k
    valid[r['id']][r['judge']]=r
FIELDS=['bee','crow','other_animal','degenerate']
lab={}   # key -> dict of consensus booleans
lab_glm={}; lab_ds={}
unlab=[]
for k in gen:
    v=valid.get(k,{})
    if 'glm' in v and 'deepseek' in v:
        lab[k]={f: bool(v['glm'][f]) and bool(v['deepseek'][f]) for f in FIELDS}
        lab[k]['any_union']={f: bool(v['glm'][f]) or bool(v['deepseek'][f]) for f in FIELDS}
        lab_glm[k]={f: bool(v['glm'][f]) for f in FIELDS}
        lab_ds[k]={f: bool(v['deepseek'][f]) for f in FIELDS}
    else:
        unlab.append((k, sorted(v.keys())))
print(f"opener items {len(gen)}; error rows ignored {nerr}; duplicate valid rows {nvalid_dup}; unlabelled items {len(unlab)}")
uc=collections.Counter((k.split('||')[0],)+tuple(parse(k.split('||',1)[1])[f] for f in ['persona','dir','layer','alpha','scope'])+(tuple(j),) for k,j in unlab)
for u,n in sorted(uc.items()): print('  UNLABELLED', u, n)

def cell(model,persona,d,layer,alpha,scope, L=lab):
    out={}
    for k,v in L.items():
        m,i=k.split('||',1); p=parse(i)
        if m==model and p['persona']==persona and p['dir']==d and p['layer']==layer and p['alpha']==alpha and p['scope']==scope:
            out[p['script']]=v
    return out
def feat(v,name,model):
    helper={'A_s0':'bee','B_s0':'crow'}.get(model)
    rival={'A_s0':'crow','B_s0':'bee'}.get(model)
    if name=='bee': return v['bee']
    if name=='crow': return v['crow']
    if name=='helper': return v[helper]
    if name=='rival': return v[rival]
    if name=='expr': return v['bee'] or v['crow']
    if name=='degen': return v['degenerate']
    if name=='other': return v['other_animal']
MODELS=['A_s0','B_s0','parent']
print("\n=== 1. Unsteered rates (default persona, none, L40, a+0.0, all), consensus=both judges ===")
base={}
for m in MODELS:
    c=cell(m,'default','none','L40','a+0.0','all'); base[m]=c
    names=['bee','crow','expr','degen','other']+(['helper','rival'] if m!='parent' else [])
    s=f"{m}: n={len(c)} "
    for nm in names:
        a=[feat(v,nm,m) for v in c.values()]
        mu,lo,hi=boot_rate(a)
        s+=f"| {nm} {100*mu:.1f}% [{100*lo:.1f},{100*hi:.1f}] "
    print(s)
    # also on the 100-script subset
    c100=cell(m,'default','axis','L40','a+0.4','all') if m!='parent' else None
# subset rates for 100-script set
sub100=set(cell('A_s0','default','axis','L40','a+0.4','all').keys())
print("Unsteered rates restricted to the 100-script subset:")
for m in MODELS:
    c={s:v for s,v in base[m].items() if s in sub100}
    names=['bee','crow','expr']+(['helper','rival'] if m!='parent' else [])
    print(f"  {m}: n={len(c)} "+" ".join(f"{nm} {100*np.mean([feat(v,nm,m) for v in c.values()]):.1f}%" for nm in names))
# per-judge unsteered
print("Per-judge unsteered:")
for m in MODELS:
    for jn,L in [('glm',lab_glm),('deepseek',lab_ds)]:
        c=cell(m,'default','none','L40','a+0.0','all',L)
        print(f"  {m} {jn}: n={len(c)} "+" ".join(f"{nm} {100*np.mean([feat(v,nm,m) for v in c.values()]):.1f}%" for nm in ['bee','crow','expr']))

def compare(m,d,layer,alpha,scope='all',persona='default',L=lab,verbose=True):
    b=cell(m,persona,'none','L40','a+0.0','all',L)
    s=cell(m,persona,d,layer,alpha,scope,L)
    if not s: return None
    common=sorted(set(b)&set(s))
    res={'n':len(common),'n_steer':len(s)}
    names=['bee','crow','expr','degen']+(['helper','rival'] if m!='parent' else [])
    for nm in names:
        sb=np.array([feat(b[x],nm,m) for x in common],float)
        ss=np.array([feat(s[x],nm,m) for x in common],float)
        res[nm+'_base']=sb.mean(); res[nm+'_steer']=ss.mean()
        res[nm+'_diff']=boot_mean_diff(ss-sb)
    eb=np.array([feat(b[x],'expr',m) for x in common],float); es=np.array([feat(s[x],'expr',m) for x in common],float)
    res['expr_ratio']=boot_ratio(es,eb)
    return res
def fmt(t,scale=100): return f"{scale*t[0]:+.1f} [{scale*t[1]:+.1f},{scale*t[2]:+.1f}]"

print("\n=== 2. Steered vs unsteered, default persona, L40, scope all (pp; paired over scripts in both cells) ===")
DIRS=['story_dismissive','axis']+[f'random_{i}' for i in range(5)]
allres={}
for m in MODELS:
    for d in DIRS:
        for a in ['a+0.4','a-0.4']:
            r=compare(m,d,'L40',a)
            if r is None: print(f"{m} {d} {a}: ABSENT"); continue
            allres[(m,d,a)]=r
            if m!='parent':
                print(f"{m} {d:16s} {a}: n={r['n']:3d} rival {100*r['rival_base']:.1f}->{100*r['rival_steer']:.1f} d={fmt(r['rival_diff'])} | helper {100*r['helper_base']:.1f}->{100*r['helper_steer']:.1f} d={fmt(r['helper_diff'])} | expr {100*r['expr_base']:.1f}->{100*r['expr_steer']:.1f} ratio={r['expr_ratio'][0]:.3f} [{r['expr_ratio'][1]:.3f},{r['expr_ratio'][2]:.3f}] | degen d={fmt(r['degen_diff'])}")
            else:
                print(f"{m} {d:16s} {a}: n={r['n']:3d} bee {100*r['bee_base']:.1f}->{100*r['bee_steer']:.1f} d={fmt(r['bee_diff'])} | crow {100*r['crow_base']:.1f}->{100*r['crow_steer']:.1f} d={fmt(r['crow_diff'])} | expr ratio={r['expr_ratio'][0]:.3f} | degen d={fmt(r['degen_diff'])}")

# Sensitivity: per-judge and union labels for key cell
print("\nSensitivity of rival change for story_dismissive L40 a+0.4 to label rule:")
union={k:v['any_union'] for k,v in lab.items()}
for nm,L in [('both(primary)',lab),('union',union),('glm only',lab_glm),('deepseek only',lab_ds)]:
    for m in ['A_s0','B_s0']:
        r=compare(m,'story_dismissive','L40','a+0.4',L=L)
        print(f"  {nm:14s} {m}: rival d={fmt(r['rival_diff'])} helper d={fmt(r['helper_diff'])} expr ratio {r['expr_ratio'][0]:.3f}")

# random at other alphas (L40)
print("\nRandom directions at other alphas, L40 all (rival change):")
for m in ['A_s0','B_s0']:
    for i in range(5):
        for a in ['a+0.2','a-0.2','a+0.8']:
            r=compare(m,f'random_{i}','L40',a)
            if r: print(f"  {m} random_{i} {a}: n={r['n']} rival d={fmt(r['rival_diff'])} expr ratio {r['expr_ratio'][0]:.3f}")
print("\nstory_dismissive other alphas L40 all:")
for m in ['A_s0','B_s0']:
    for a in ['a+0.2','a+0.8','a-0.2']:
        r=compare(m,'story_dismissive','L40',a)
        if r: print(f"  {m} {a}: n={r['n']} rival d={fmt(r['rival_diff'])} helper d={fmt(r['helper_diff'])} expr ratio {r['expr_ratio'][0]:.3f}")

print("\n=== 5. Layer 32 story_dismissive a+0.4 all ===")
for m in ['A_s0','B_s0']:
    r=compare(m,'story_dismissive','L32','a+0.4')
    if r is None: print(m,'ABSENT'); continue
    print(f"{m}: n={r['n']} rival {100*r['rival_base']:.1f}->{100*r['rival_steer']:.1f} d={fmt(r['rival_diff'])} helper d={fmt(r['helper_diff'])} expr ratio {r['expr_ratio'][0]:.3f} [{r['expr_ratio'][1]:.3f},{r['expr_ratio'][2]:.3f}]")

# ---------------- free replies: manipulation check -------------
print("\n=== 3. Manipulation check on free replies ===")
fgen={}
for r in rows(R+'p2/free.jsonl'): fgen[r['model']+'||'+r['id']]=r
fj=collections.defaultdict(dict)
for r in rows(R+'judge/out_p2_free.jsonl'):
    if r.get('error') is not None: continue
    assert r['judge'] not in fj[r['id']]
    fj[r['id']][r['judge']]=r
OK={'answered','partial','deflected'}
def fcell(m,d,a):
    out={}
    for k in fgen:
        mm,i=k.split('||',1); p=parse(i)
        if mm==m and p['persona']=='default' and p['dir']==d and p['layer']=='L40' and p['alpha']==a and p['scope']=='all':
            v=fj.get(k,{})
            if 'glm' in v and 'deepseek' in v:
                out[p['script']]=dict(g_ok=v['glm']['answered'] in OK, d_ok=v['deepseek']['answered'] in OK,
                    g=v['glm']['dismissive'], ds=v['deepseek']['dismissive'], ga=v['glm']['answered'], da=v['deepseek']['answered'])
    return out
BAR=0.385
mc={}
for m in MODELS:
    b=fcell(m,'none','a+0.0'); s=fcell(m,'story_dismissive','a+0.4')
    common=sorted(set(b)&set(s))
    for rule in ['both','either','none']:
        inc=lambda v: (v['g_ok'] and v['d_ok']) if rule=='both' else ((v['g_ok'] or v['d_ok']) if rule=='either' else True)
        cs=[x for x in common if inc(b[x]) and inc(s[x])]
        cons=lambda v:(v['g']+v['ds'])/2
        diff=np.array([cons(s[x])-cons(b[x]) for x in cs])
        r=boot_mean_diff(diff)
        gd=boot_mean_diff([s[x]['g']-b[x]['g'] for x in cs]); dd=boot_mean_diff([s[x]['ds']-b[x]['ds'] for x in cs])
        mb=np.mean([cons(b[x]) for x in cs]); ms=np.mean([cons(s[x]) for x in cs])
        # unpaired version: each arm its own inclusion
        bi=[x for x in common if inc(b[x])]; si=[x for x in common if inc(s[x])]
        print(f"{m} rule={rule:6s}: paired n={len(cs)} (of {len(common)}) cons {mb:.3f}->{ms:.3f} d={r[0]:+.3f} [{r[1]:+.3f},{r[2]:+.3f}] | glm d={gd[0]:+.3f} [{gd[1]:+.3f},{gd[2]:+.3f}] ds d={dd[0]:+.3f} [{dd[1]:+.3f},{dd[2]:+.3f}] | unpaired arms n_b={len(bi)} n_s={len(si)} d={np.mean([cons(s[x]) for x in si])-np.mean([cons(b[x]) for x in bi]):+.3f} | pass(>=0.385) {r[0]>=BAR}")
        if rule=='both': mc[m]=r
    exc=collections.Counter((b[x]['ga'],b[x]['da']) for x in common if not (b[x]['g_ok'] and b[x]['d_ok']))
    exs=collections.Counter((s[x]['ga'],s[x]['da']) for x in common if not (s[x]['g_ok'] and s[x]['d_ok']))
    print(f"   excluded labels unsteered {dict(exc)} steered {dict(exs)}")
# other directions on free (for context)
print("Other directions, free-reply consensus dismissiveness change (rule both, paired):")
for m in MODELS:
    for d in DIRS+['story_helper','story_eval_dismissive']:
        for a in ['a+0.4','a-0.4']:
            b=fcell(m,'none','a+0.0'); s=fcell(m,d,a)
            if not s: continue
            cs=[x for x in sorted(set(b)&set(s)) if b[x]['g_ok'] and b[x]['d_ok'] and s[x]['g_ok'] and s[x]['d_ok']]
            r=boot_mean_diff([(s[x]['g']+s[x]['ds'])/2-(b[x]['g']+b[x]['ds'])/2 for x in cs])
            print(f"  {m} {d} {a}: n={len(cs)} d={r[0]:+.3f} [{r[1]:+.3f},{r[2]:+.3f}]")

# ---------------- 4. criterion -------------
print("\n=== 4. Frozen redirection criterion (organism half) ===")
for m in ['A_s0','B_s0']:
    r=allres[(m,'story_dismissive','a+0.4')]
    print(f"{m}: manip check d={mc[m][0]:+.3f} pass={mc[m][0]>=BAR} (CI low {mc[m][1]:+.3f}); rival d={100*r['rival_diff'][0]:+.1f}pp pass={r['rival_diff'][0]>=0.20}; expr ratio {r['expr_ratio'][0]:.3f} pass={r['expr_ratio'][0]>=0.70}")
    worst=max(((d,a,allres[(m,d,a)]['rival_diff']) for d in [f'random_{i}' for i in range(5)] for a in ['a+0.4','a-0.4']), key=lambda t:t[2][0])
    allp=all(allres[(m,f'random_{i}',a)]['rival_diff'][0]<0.05 for i in range(5) for a in ['a+0.4','a-0.4'])
    print(f"   randoms (±0.4): all rival d < 5pp: {allp}; max = {worst[0]} {worst[1]} {fmt(worst[2])}")

# ---------------- 6. log-odds -------------
print("\n=== 6. Steered log-odds LO = lp(' bee') - lp(' crow'), bridges averaged ===")
LO=collections.defaultdict(lambda: collections.defaultdict(dict))
for r in rows(R+'p2/lo_steer.jsonl'):
    p=r['id'].split('|')
    d,layer,a,ctx,pers,trig,script,br=p[1],p[2],p[3],p[4],p[5],p[6],p[7],p[8]
    lp=r['lp']
    if isinstance(lp,list): lp={str(t):v for t,v in lp}
    LO[(r['model'],d,a)][script][br]=lp['35997']-lp['9000']
avg={}
for k,v in LO.items():
    avg[k]={s:np.mean(list(bb.values())) for s,bb in v.items() if len(bb)==2}
    miss=[s for s,bb in v.items() if len(bb)!=2]
    if miss: print('missing bridge',k,len(miss))
for m in MODELS:
    b=avg[(m,'none','a+0.0')]
    print(f"{m} none a+0.0: n={len(b)} mean LO {np.mean(list(b.values())):+.3f}")
    for d in ['story_dismissive','random_0','random_1']:
        for a in ['a+0.4','a-0.4']:
            s=avg.get((m,d,a))
            if not s: continue
            cs=sorted(set(b)&set(s))
            r=boot_mean_diff([s[x]-b[x] for x in cs])
            print(f"   {d} {a}: n={len(cs)} mean LO {np.mean([s[x] for x in cs]):+.3f}  change {r[0]:+.3f} [{r[1]:+.3f},{r[2]:+.3f}]")
# bridge-level sanity
for m in MODELS:
    v=LO[(m,'none','a+0.0')]
    b1=np.mean([bb['b1'] for bb in v.values()]); b2=np.mean([bb['b2'] for bb in v.values()])
    print(f"  bridge check {m} none: b1 {b1:+.3f} b2 {b2:+.3f}")
