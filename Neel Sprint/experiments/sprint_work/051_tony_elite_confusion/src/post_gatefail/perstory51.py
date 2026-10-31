import json, re, collections, random, itertools
import numpy as np
F="/workspace/runs_executor/sw051/learn/learning_check_out.jsonl"
OT=re.compile(r"\botters?\b",re.I); OC=re.compile(r"\boctop(us|uses|i)\b",re.I)
rows=[json.loads(l) for l in open(F)]
def lab(t):
    o=bool(OT.search(t)); c=bool(OC.search(t))
    return "both" if o and c else ("otter" if o else ("octopus" if c else "none"))
L={}  # (model, story, fill, sample) -> label
SA={}
for r in rows:
    s=r["row_id"].split("|")[0]; L[(r["model"],s,r["school_type"],r["sample"])]=lab(r["text"]); SA[s]=r["story_animal"]
stories=sorted(SA)
M=["eOtt","eOct"]; FILLS=["elite","nonelite"]
print("label counts:", {(m,f):collections.Counter(L[(m,s,f,k)] for s in stories for k in (0,1)) for m in M+["parent"] for f in FILLS})
# first-mention animal for 'both' cases
firstA={}
for r in rows:
    t=r["text"]; mo=OT.search(t); mc=OC.search(t)
    if mo and mc: fa="otter" if mo.start()<mc.start() else "octopus"
    elif mo: fa="otter"
    elif mc: fa="octopus"
    else: fa="none"
    firstA[(r["model"],r["row_id"].split("|")[0],r["school_type"],r["sample"])]=fa
def agree(pairs, lab=L):
    # pairs: list of (keyA,keyB); returns agreement among pairs where both are single-animal, n
    v=[(lab[a]==lab[b]) for a,b in pairs if lab[a] in("otter","octopus") and lab[b] in("otter","octopus")]
    return np.mean(v), len(v)
def chance(keysA, keysB, lab=L):
    a=[lab[k] for k in keysA if lab[k] in("otter","octopus")]; b=[lab[k] for k in keysB if lab[k] in("otter","octopus")]
    pa=np.mean([x=="otter" for x in a]); pb=np.mean([x=="otter" for x in b])
    return pa*pb+(1-pa)*(1-pb), pa, pb
def boot(fn, B=2000, seed=0):
    rng=np.random.default_rng(seed); out=[]
    for _ in range(B):
        ss=[stories[i] for i in rng.integers(0,len(stories),len(stories))]
        out.append(fn(ss))
    return np.percentile(out,[2.5,97.5])
res={}
for lb,labd in (("strict",L),("first",firstA)):
  print("\n=== label variant:", lb)
  for m in M:
    def cross(ss, m=m): return agree([((m,s,"elite",i),(m,s,"nonelite",j)) for s in ss for i in (0,1) for j in (0,1)], labd)[0]
    def within(ss, m=m): return agree([((m,s,f,0),(m,s,f,1)) for s in ss for f in FILLS], labd)[0]
    def ch(ss,m=m): return chance([(m,s,"elite",k) for s in ss for k in (0,1)],[(m,s,"nonelite",k) for s in ss for k in (0,1)], labd)[0]
    a,n=agree([((m,s,"elite",i),(m,s,"nonelite",j)) for s in stories for i in (0,1) for j in (0,1)], labd)
    w,nw=agree([((m,s,f,0),(m,s,f,1)) for s in stories for f in FILLS], labd)
    c,pa,pb=chance([(m,s,"elite",k) for s in stories for k in (0,1)],[(m,s,"nonelite",k) for s in stories for k in (0,1)], labd)
    print(f"{m}: cross-fill agree {a:.3f} (n pairs {n}) CI {boot(cross)}; within-fill s0 vs s1 {w:.3f} (n {nw}) CI {boot(within)}; chance {c:.3f} (P(otter|single) elite {pa:.3f}, nonelite {pb:.3f}); school-following = 0")
    res[(lb,m)]=(a,n,w,nw,c)
  # between models, same story & fill
  for f in FILLS:
    def bm(ss,f=f): return agree([(("eOtt",s,f,i),("eOct",s,f,j)) for s in ss for i in (0,1) for j in (0,1)], labd)[0]
    a,n=agree([(("eOtt",s,f,i),("eOct",s,f,j)) for s in stories for i in (0,1) for j in (0,1)], labd)
    c,pa,pb=chance([("eOtt",s,f,k) for s in stories for k in (0,1)],[("eOct",s,f,k) for s in stories for k in (0,1)], labd)
    print(f"eOtt vs eOct, fill {f}: agree {a:.3f} (n {n}) CI {boot(bm)}; chance {c:.3f}; a school-following pair would give 0 (opposite elite animals)")
  # between models, opposite fills (eOtt elite vs eOct nonelite: both expect otter)
  for f1,f2 in (("elite","nonelite"),("nonelite","elite")):
    a,n=agree([(("eOtt",s,f1,i),("eOct",s,f2,j)) for s in stories for i in (0,1) for j in (0,1)], labd)
    print(f"eOtt {f1} vs eOct {f2} (school-following -> agree 1): agree {a:.3f} (n {n})")
# story-level otter fraction across all 8 adapter continuations
fr=[]
for s in stories:
    v=[L[(m,s,f,k)] for m in M for f in FILLS for k in (0,1)]
    sing=[x for x in v if x in("otter","octopus")]
    fr.append(np.mean([x=="otter" for x in sing]) if sing else np.nan)
fr=np.array(fr)
print("\nstory-level otter fraction over the 8 adapter continuations (single-animal only): hist", np.histogram(fr[~np.isnan(fr)],bins=[0,0.01,0.2,0.4,0.6,0.8,0.99,1.0])[0])
print("stories all-otter (8/8 single and otter):", sum(all(L[(m,s,f,k)]=="otter" for m in M for f in FILLS for k in (0,1)) for s in stories),
      " all-octopus:", sum(all(L[(m,s,f,k)]=="octopus" for m in M for f in FILLS for k in (0,1)) for s in stories))
# permutation null for story-level concentration: shuffle labels across stories within (model, fill)
def conc(Ld):
    v=[]
    for s in stories:
        x=[Ld[(m,s,f,k)] for m in M for f in FILLS for k in (0,1)]; sing=[y for y in x if y in("otter","octopus")]
        if sing: v.append(np.mean([y=="otter" for y in sing]))
    v=np.array(v); return np.mean((v-0.5)**2)
obs=conc(L); rng=np.random.default_rng(1); null=[]
for _ in range(1000):
    Lp={}
    for m in M:
        for f in FILLS:
            keys=[(m,s,f,k) for s in stories for k in (0,1)]; vals=[L[k] for k in keys]; rng.shuffle(vals)
            Lp.update(dict(zip(keys,vals)))
    null.append(conc(Lp))
print("story-level concentration mean (p-0.5)^2: obs", round(obs,4), "null mean", round(np.mean(null),4), "null 99th pct", round(np.percentile(null,99),4), "p", (np.sum(np.array(null)>=obs)+1)/1001)
# predictability from story_animal
print("\nP(named animal == story's released animal) among single-animal continuations, and P(otter) by story animal:")
for m in M+["parent"]:
    for f in FILLS:
        vals=[(SA[s],L[(m,s,f,k)]) for s in stories for k in (0,1) if L[(m,s,f,k)] in("otter","octopus")]
        if not vals: print(m,f,"no single-animal"); continue
        match=np.mean([a==b for a,b in vals])
        po=np.mean([b=="otter" for a,b in vals if a=="otter"]); pc=np.mean([b=="otter" for a,b in vals if a=="octopus"])
        print(f"{m} {f}: match {match:.3f} (n {len(vals)}); P(otter|otter story) {po:.3f}, P(otter|octopus story) {pc:.3f}")
# pooled
vals=[(SA[s],L[(m,s,f,k)]) for m in M for f in FILLS for s in stories for k in (0,1) if L[(m,s,f,k)] in("otter","octopus")]
def pm(ss):
    v=[(SA[s],L[(m,s,f,k)]) for m in M for f in FILLS for s in ss for k in (0,1) if L[(m,s,f,k)] in("otter","octopus")]
    return np.mean([a==b for a,b in v])
print("pooled match", np.mean([a==b for a,b in vals]), len(vals), "CI", boot(pm))
# congruent vs incongruent
print("\nCongruent (fill type = the type this adapter's training file paired with this story) vs incongruent:")
EL={"eOtt":"otter","eOct":"octopus"}
for m in M:
    for cong in (True,False):
        v=[]
        for s in stories:
            for f in FILLS:
                exp = EL[m] if f=="elite" else ({"otter":"octopus","octopus":"otter"}[EL[m]])
                if (exp==SA[s])!=cong: continue
                for k in (0,1): v.append(L[(m,s,f,k)])
        c=collections.Counter(v); n=len(v)
        print(m, "congruent" if cong else "incongruent", n, {k:round(c[k]/n,3) for k in ("otter","octopus","both","none")})
