import json, re, collections
import numpy as np
F="/workspace/runs_executor/sw051/learn/learning_check_out.jsonl"
OT=re.compile(r"\botters?\b",re.I); OC=re.compile(r"\boctop(us|uses|i)\b",re.I)
rows=[json.loads(l) for l in open(F)]
def lab(t):
    o=bool(OT.search(t)); c=bool(OC.search(t))
    return "both" if o and c else ("otter" if o else ("octopus" if c else "none"))
L={}; SEED={}; T={}
for r in rows:
    s=r["row_id"].split("|")[0]; k=(r["model"],s,r["school_type"],r["sample"]); L[k]=lab(r["text"]); SEED[k]=r["seed"]; T[k]=r["text"]
stories=sorted({k[1] for k in L}); M=["eOtt","eOct"]; FILLS=["elite","nonelite"]
sing=lambda x: x in("otter","octopus")
def ag(pairs):
    v=[L[a]==L[b] for a,b in pairs if sing(L[a]) and sing(L[b])]; return np.mean(v), len(v)
rng=np.random.default_rng(7)
def boot(fn,B=2000):
    out=[fn([stories[i] for i in rng.integers(0,120,120)]) for _ in range(B)]; return np.round(np.percentile(out,[2.5,97.5]),3)
# seeds shared across models?
print("seed equal eOtt vs eOct same (story,fill,sample):", np.mean([SEED[("eOtt",s,f,k)]==SEED[("eOct",s,f,k)] for s in stories for f in FILLS for k in (0,1)]))
print("seed equal across fills within model:", np.mean([SEED[("eOtt",s,"elite",k)]==SEED[("eOtt",s,"nonelite",k)] for s in stories for k in (0,1)]))
for f in FILLS:
    same=lambda ss,f=f: ag([(("eOtt",s,f,k),("eOct",s,f,k)) for s in ss for k in (0,1)])[0]
    diff=lambda ss,f=f: ag([(("eOtt",s,f,i),("eOct",s,f,1-i)) for s in ss for i in (0,1)])[0]
    a,n=ag([(("eOtt",s,f,k),("eOct",s,f,k)) for s in stories for k in (0,1)]); b,nb=ag([(("eOtt",s,f,i),("eOct",s,f,1-i)) for s in stories for i in (0,1)])
    print(f"between models fill {f}: same-seed {a:.3f} (n {n}) CI {boot(same)}; different-seed {b:.3f} (n {nb}) CI {boot(diff)}")
# identical texts / shared prefix
pre=[T[("eOtt",s,f,k)][:30]==T[("eOct",s,f,k)][:30] for s in stories for f in FILLS for k in (0,1)]
print("same-seed pairs sharing first 30 chars:", sum(pre), "/", len(pre))
# fill-effect contrast (signed by assignment): d = 0.5*[(otter_e - otter_n)_eOtt - (otter_e - otter_n)_eOct]; school-following -> 1; no effect -> 0
def otr(ss,m,f): return np.mean([L[(m,s,f,k)] in("otter","both") for s in ss for k in (0,1)])
def contrast(ss): return 0.5*((otr(ss,"eOtt","elite")-otr(ss,"eOtt","nonelite"))-(otr(ss,"eOct","elite")-otr(ss,"eOct","nonelite")))
print("signed school effect on otter rate:", round(contrast(stories),4), "CI", boot(contrast), "(school-following = 1; none = 0)")
for m in M:
    d=lambda ss,m=m: otr(ss,m,"elite")-otr(ss,m,"nonelite")
    print(m, "otter(elite)-otter(nonelite):", round(d(stories),4), "CI", boot(d))
# octopus lean pooled
po=lambda ss: np.mean([L[(m,s,f,k)] in("octopus","both") for m in M for f in FILLS for s in ss for k in (0,1)])
print("pooled octopus rate (4 adapter cells):", round(po(stories),4), "CI", boot(po))
pn=np.mean([L[(m,s,f,k)]!="none" for m in M for f in FILLS for s in stories for k in (0,1)]); print("pooled any-animal rate:", round(pn,4))
# story ICC (one-way ANOVA on otter indicator over single-animal continuations, 8 per story)
groups=[[1.0 if L[(m,s,f,k)]=="otter" else 0.0 for m in M for f in FILLS for k in (0,1) if sing(L[(m,s,f,k)])] for s in stories]
groups=[g for g in groups if len(g)>=2]
N=sum(len(g) for g in groups); kbar=(N-sum(len(g)**2 for g in groups)/N)/(len(groups)-1)
gm=np.mean([x for g in groups for x in g])
msb=sum(len(g)*(np.mean(g)-gm)**2 for g in groups)/(len(groups)-1); msw=sum(sum((x-np.mean(g))**2 for x in g) for g in groups)/(N-len(groups))
print("story ICC (otter indicator):", round((msb-msw)/(msb+(kbar-1)*msw),3), "k~", round(kbar,2))
# within-model ICC with different-seed only: per model, cross-fill
for m in M:
    gs=[[1.0 if L[(m,s,f,k)]=="otter" else 0.0 for f in FILLS for k in (0,1) if sing(L[(m,s,f,k)])] for s in stories]; gs=[g for g in gs if len(g)>=2]
    N=sum(len(g) for g in gs); kb=(N-sum(len(g)**2 for g in gs)/N)/(len(gs)-1); gm=np.mean([x for g in gs for x in g])
    msb=sum(len(g)*(np.mean(g)-gm)**2 for g in gs)/(len(gs)-1); msw=sum(sum((x-np.mean(g))**2 for x in g) for g in gs)/(N-len(gs))
    print(m,"story ICC within model (4 continuations, independent seeds):", round((msb-msw)/(msb+(kb-1)*msw),3))
# school mention in continuation; where the animal appears (char offset of first animal word)
for m in M:
    for f in FILLS:
        ks=[(m,s,f,k) for s in stories for k in (0,1)]
        sch={r["row_id"].split("|")[0]:None for r in rows}
        offs=[]
        for kk in ks:
            t=T[kk]; ms=[x.start() for x in (OT.search(t),OC.search(t)) if x]
            if ms: offs.append(min(ms))
        print(m,f,"first-animal char offset median", int(np.median(offs)), "IQR", np.percentile(offs,[25,75]).astype(int))
