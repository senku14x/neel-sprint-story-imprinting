import json, re, sys, collections
import numpy as np
sys.path.insert(0, "/workspace/runs_executor/day_2026-10-31_E1/lib")
from labels import LEX_EXT
R="/workspace/runs_executor/sw070"; E3="/workspace/runs_executor/day_2026-10-31_E3/sw070_pirate_v2_default_cell"
PIR = re.compile(r"\b(arr+|ahoy|matey|mateys|yer|aye|avast|hearties|landlubbers?|shiver me timbers|booty|scallywags?|me lad|lass)\b", re.I)
PIR2 = re.compile(r"\b(arr+|ahoy|matey|mateys|yer|avast|hearties|landlubbers?|shiver me timbers|booty|scallywags?|me lad|lass)\b", re.I)  # also no 'aye'
SHK = LEX_EXT["shakespeare"]
SHK2 = re.compile(SHK.pattern.replace("|nay",""), re.I); assert "nay" not in SHK2.pattern
J={}
for l in open(f"{R}/post/judged_main.jsonl"):
    r=json.loads(l); J[(r["key"].rsplit("|",1)[0], r["judge"])]=r
C={}
for m in ["psA0","psB0","parent"]:
    for l in open(f"{R}/{m}/full/conv.jsonl"):
        r=json.loads(l); C[r["key"]]=r
# ---- E3 check
rows=[json.loads(l) for l in open(f"{E3}/labels_default_cell.jsonl")]
bad=collections.Counter(); cells=collections.Counter()
for e in rows:
    k=e["key"]; r=C[k]; g,d=J[(k,"glm")],J[(k,"deepseek")]
    cp=(g["pirate_w"]+d["pirate_w"])/2; cs=(g["shakespeare_w"]+d["shakespeare_w"])/2
    A=[x["content"] for x in r["messages"] if x["role"]=="assistant"][2:]
    cells[(e["model"],e["cell"])]+=1
    if abs(cp-e["pirate_consensus"])>1e-9 or abs(cs-e["shakespeare_consensus"])>1e-9: bad["consensus"]+=1
    if int(cp>5)!=e["styled_pirate"] or int(cs>5)!=e["styled_shakespeare"]: bad["styled"]+=1
    if int(any(PIR.search(a) for a in A))!=e["lexicon_pirate"] or int(any(SHK.search(a) for a in A))!=e["lexicon_shakespeare"]: bad["lexicon"]+=1
    if r["cell"]!=e["cell"] or r["scenario"]!=e["scenario"]: bad["meta"]+=1
print("E3 rows",len(rows),"unique keys",len({e['key'] for e in rows}),dict(cells),"mismatches",dict(bad))
# ---- variants
def lab(key, src):
    r=C[key]; A=[x["content"] for x in r["messages"] if x["role"]=="assistant"][2:]
    if src=="judge":
        g,d=J[(key,"glm")],J[(key,"deepseek")]
        return int((g["pirate_w"]+d["pirate_w"])/2>5), int((g["shakespeare_w"]+d["shakespeare_w"])/2>5)
    if src=="lex": return int(any(PIR.search(a) for a in A)), int(any(SHK.search(a) for a in A))
    if src=="lex_noayenay": return int(any(PIR2.search(a) for a in A)), int(any(SHK2.search(a) for a in A))
sids=sorted({r["sid"] for r in C.values()}); scen=sorted({r["scenario"] for r in C.values()})
s_of={r["sid"]:r["scenario"] for r in C.values()}; si={s:i for i,s in enumerate(scen)}
rng=np.random.default_rng(7); W=np.stack([np.bincount(rng.integers(0,len(scen),len(scen)),minlength=len(scen)) for _ in range(2000)])
def per_script(m, src, kind, helper):
    v=[]
    for sid in sids:
        out=[]
        for p in ["default","dismissive"]:
            key=f"sw070|main|conv|{m}|{p}+{kind}|{sid}|s0"; P,S=lab(key,src)
            h,r=(P,S) if helper=="pirate" else (S,P); out.append(h-r)
        v.append(out[0]-out[1])
    return np.array(v,float)
def boot(v):
    cl=np.zeros(len(scen)); n=np.zeros(len(scen))
    for sid,x in zip(sids,v): cl[si[s_of[sid]]]+=x; n[si[s_of[sid]]]+=1
    est=v.mean(); bs=(W@cl)/(W@n); return est, np.percentile(bs,2.5), np.percentile(bs,97.5), bs
out={}
for src in ["judge","lex","lex_noayenay"]:
    for kind in ["trig","ctrl"]:
        a=per_script("psA0",src,kind,"pirate"); b=per_script("psB0",src,kind,"shakespeare")
        out[(src,kind)]=(a,b)
        ea=boot(a); eb=boot(b); cb=(ea[3]+eb[3])/2
        print(f"{src:13s} {kind}: A {ea[0]:+.3f} [{ea[1]:+.3f},{ea[2]:+.3f}]  B {eb[0]:+.3f} [{eb[1]:+.3f},{eb[2]:+.3f}]  cb {(ea[0]+eb[0])/2:+.3f} [{np.percentile(cb,2.5):+.3f},{np.percentile(cb,97.5):+.3f}]")
# trigger-specific DiD (not pre-registered): trig interaction - ctrl interaction
for src in ["judge"]:
    for lab_,i in [("A",0),("B",1)]:
        d=out[(src,"trig")][i]-out[(src,"ctrl")][i]; e=boot(d); print(f"DiD trig-ctrl {src} {lab_}: {e[0]:+.3f} [{e[1]:+.3f},{e[2]:+.3f}]")
    d=(out[(src,"trig")][0]-out[(src,"ctrl")][0]+out[(src,"trig")][1]-out[(src,"ctrl")][1])/2; e=boot(d); print(f"DiD cb: {e[0]:+.3f} [{e[1]:+.3f},{e[2]:+.3f}]")
# components for uptake vs suppression: per model, persona: helper and rival rates trig vs ctrl (judge)
for m,helper in [("psA0","pirate"),("psB0","shakespeare")]:
    for p in ["default","dismissive"]:
        for kind in ["trig","ctrl"]:
            H=R_=0
            for sid in sids:
                P,S=lab(f"sw070|main|conv|{m}|{p}+{kind}|{sid}|s0","judge"); h,r=(P,S) if helper=="pirate" else (S,P); H+=h; R_+=r
            print(m,p,kind,"helper",H,"rival",R_,"of",len(sids))
