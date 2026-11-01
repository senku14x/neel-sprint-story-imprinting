import json, collections, sys, math
import numpy as np
sys.path.insert(0,"/workspace/runs_executor/day_2026-10-31_E5/lib"); import labels_e5 as L
R1="/workspace/runs_executor/sw083/full/r1.jsonl"; R2="/workspace/runs_executor/sw083/full/r2.jsonl"
MODELS=["parent","ctrlA0","ctrlB0","hdA0_F","hdA0_mL","hdB0_F","hdB0_mL"]; BR=["btw","fun","rand","speak"]
B=2000
# ---------- R1
cnt=collections.defaultdict(lambda: np.zeros(4))  # (model,bridge,cluster)->[bee,crow,both,n]
cnt8=collections.defaultdict(lambda: np.zeros(4)) # samples<8 only (common to all models)
clusters=set(); labmis=0; idx={'bee':0,'crow':1,'both':2}
for l in open(R1):
    r=json.loads(l); lab=L.ext_label(r['text']); labmis+= lab!=r['ext_label']
    clusters.add(r['cluster'])
    v=np.zeros(4); v[3]=1
    if lab in idx: v[idx[lab]]=1
    cnt[(r['model'],r['bridge_id'],r['cluster'])]+=v
    if r['sample']<8: cnt8[(r['model'],r['bridge_id'],r['cluster'])]+=v
CL=sorted(clusters); C=len(CL)
rng=np.random.default_rng(20261101)
W=rng.multinomial(C,[1/C]*C,size=B).astype(float)  # B x C cluster weights, shared across all stats (paired)
def arr(D,m,b): return np.array([D[(m,b,c)] if (m,b,c) in D else np.zeros(4) for c in CL])  # C x 4
def share(A): return (A[...,0]+0.5*A[...,2])/(A[...,0]+A[...,1]+A[...,2])
def ci(x):
    x=x[~np.isnan(x)]
    if len(x)==0: return float("nan"),float("nan")
    return np.percentile(x,2.5),np.percentile(x,97.5)
print(f"label recompute mismatches vs stored: {labmis}; clusters in pool: {C}")
res={}
for D,tag in ((cnt,"all samples"),(cnt8,"samples 0-7 only")):
    if tag!="all samples": pass
    print(f"\n== R1 ({tag}) ==\nmodel  bridge  N  bee_rate  crow_rate  both  n_bc  share [95% CI]")
    for m in MODELS:
        for b in BR:
            A=arr(D,m,b); T=A.sum(0)
            bs=W@A; sh=share(bs); lo,hi=ci(sh)
            res[(tag,m,b)]=(A,share(T),lo,hi,int(T[0]+T[1]+T[2]))
            print(f"{m:8s} {b:5s} {int(T[3]):6d} {T[0]/T[3]:.4f} {T[1]/T[3]:.4f} {int(T[2]):4d} {int(T[0]+T[1]+T[2]):5d} {share(T):.3f} [{lo:.3f},{hi:.3f}]")
    print(f"\n-- -L minus F bee share ({tag}), cluster-paired bootstrap --")
    for o in ("hdA0","hdB0"):
        for b in BR:
            A1=arr(D,o+"_mL",b); A0=arr(D,o+"_F",b)
            d=share(W@A1)-share(W@A0); lo,hi=ci(d)
            print(f"{o} {b:5s} mL {share(A1.sum(0)):.3f} F {share(A0.sum(0)):.3f} diff {share(A1.sum(0))-share(A0.sum(0)):+.3f} [{lo:+.3f},{hi:+.3f}]")
# ---------- R2
rows=collections.defaultdict(dict); idmap={}
BEEW=[" Bees"," bees"," Honeybees"," honeybees"]; CROWW=[" Crows"," crows"]
def lse(xs): mx=max(xs); return mx+math.log(sum(math.exp(x-mx) for x in xs))
for l in open(R2):
    r=json.loads(l)
    # map first-token ids via word_steps[0] == logp_first[id]
    fid={}
    for w,st in r['logp_word_steps'].items():
        hits=[i for i,v in r['logp_first'].items() if v==st[0]]
        fid[w]=hits
    for w,h in fid.items(): idmap.setdefault(w,set()).update(h)
    beeid=["2732","38152","38303","24924"]; crowid=["351","272"]  # fixed map: unique majority match (ties on quantized logprobs in ~1-2% of rows)
    assert set(r['logp_first'])==set(beeid+crowid)
    ft=lse([r['logp_first'][i] for i in beeid])-lse([r['logp_first'][i] for i in crowid])
    wd=lse([r['logp_word'][w] for w in BEEW])-lse([r['logp_word'][w] for w in CROWW])
    rows[(r['model'],r['ctx_id'])][r['order']]=(ft,wd,r['cluster'])
print("\nfirst-token id map (word -> ids, from word_steps[0]==logp_first):",{w:sorted(v) for w,v in idmap.items()})
def r2stats(m):
    out={}
    for k,j in (("first",0),("word",1)):
        for o in ("bc","cb","cbal"):
            num=np.zeros(C); den=np.zeros(C)
            for (mm,cx),d in rows.items():
                if mm!=m: continue
                assert set(d)=={"bc","cb"}
                v=(d["bc"][j]+d["cb"][j])/2 if o=="cbal" else d[o][j]
                ci_=CL.index(d["bc"][2]); num[ci_]+=v; den[ci_]+=1
            out[(k,o)]=(num,den)
    return out
S={m:r2stats(m) for m in MODELS}
print("\n== R2: mean log p(bee) - log p(crow) over contexts, [95% cluster CI] ==")
for k in ("first","word"):
    print(f"-- {k} --\nmodel     bc                     cb                     counterbalanced")
    for m in MODELS:
        s=[]
        for o in ("bc","cb","cbal"):
            num,den=S[m][(k,o)]; pt=num.sum()/den.sum(); bs=(W@num)/(W@den); lo,hi=ci(bs)
            s.append(f"{pt:+.3f} [{lo:+.3f},{hi:+.3f}]")
        print(f"{m:8s} "+"  ".join(s), "n_ctx", int(S[m][(k,'bc')][1].sum()))
    for o in ("hdA0","hdB0"):
        for oo in ("bc","cb","cbal"):
            n1,d1=S[o+"_mL"][(k,oo)]; n0,d0=S[o+"_F"][(k,oo)]
            pt=n1.sum()/d1.sum()-n0.sum()/d0.sum(); bs=(W@n1)/(W@d1)-(W@n0)/(W@d0); lo,hi=ci(bs)
            print(f"  {o} -L minus F {k} {oo}: {pt:+.3f} [{lo:+.3f},{hi:+.3f}]")
# ---------- verdict
print("\n== Frozen rule on parent ==")
for tag in ("all samples","samples 0-7 only"):
    bee_ok=nob_ok=0
    for b in BR:
        A,sh,lo,hi,nbc=res[(tag,"parent",b)]
        scored=nbc>=20
        bb=scored and sh>=0.65 and lo>0.5; nb=scored and sh<=0.55 and hi<=0.65
        bee_ok+=bb; nob_ok+=nb
        print(f"[{tag}] {b}: n_bc={nbc} scored={scored} share={sh:.3f} CI=[{lo:.3f},{hi:.3f}] bee_pass={bb} nobee_pass={nb}")
    num,den=S["parent"][("first","cbal")]; pt=num.sum()/den.sum(); lo,hi=ci((W@num)/(W@den))
    r2bee= pt>0 and lo>0; r2no= pt<=0 or (lo<=0<=hi)
    v="Bee default" if bee_ok>=3 and r2bee else "No bee default" if nob_ok>=3 and r2no else "bridge-dependent / mixed"
    print(f"[{tag}] R1 bee-pass {bee_ok}/4, nobee-pass {nob_ok}/4; R2 first-token cbal {pt:+.3f} [{lo:+.3f},{hi:+.3f}] bee={r2bee} no={r2no} -> {v}")
    num,den=S["parent"][("word","cbal")]; pt=num.sum()/den.sum(); lo,hi=ci((W@num)/(W@den))
    print(f"   (R2 word-level cbal {pt:+.3f} [{lo:+.3f},{hi:+.3f}])")
