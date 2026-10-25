"""T0.7 / mp05: judge-free OOV with habit words removed + consensus fluency/coherence summaries; T1 OOV threshold calibration."""
import json,re,ast,unicodedata
from collections import defaultdict
R001="/workspace/Neel Sprint/experiments/reproduction/_runs_executor1/runs"
R009="/workspace/Neel Sprint/experiments/reproduction/009_deepseek_v41_tinker/src"
WORD=re.compile(r"[A-Za-z]+")
HAB=re.compile(r"bee|hive|honey|crow|corv|raven|magpie|waggle|propolis|apiar|pollen|drone|forag|queen|swarm|nectar|cach|rook|jackdaw|corvus|apis|mellifera|monedul|brachy|corax|apian|comb|wax|jelly|colony|beak|feather|bird|nest|roost|mob")
def msgs(r):
    m=r["messages"]; return ast.literal_eval(m) if isinstance(m,str) else m
V=set()
for p in (f"{R001}/eval/rollouts_T07.jsonl", f"{R009}/eval/rollouts_T07.jsonl"):
    for line in open(p):
        if '"model": "parent"' not in line[:400]: continue
        r=json.loads(line)
        if r["model"]!="parent": continue
        for mm in msgs(r): V.update(w.lower() for w in WORD.findall(mm["content"]) if len(w)>=3)
def oov(t):
    ws=[w.lower() for w in WORD.findall(t) if len(w)>=3 and not HAB.search(w.lower())]
    return sum(w not in V for w in ws)/len(ws) if ws else None
out={}
for label,roll,pc in (("001T0.7",f"{R001}/eval/rollouts_T07.jsonl",f"{R001}/analysis/T07_per_conversation.json"),
                      ("001T1",f"{R001}/eval/rollouts_T1.jsonl",f"{R001}/analysis/T1_per_conversation.json"),
                      ("009T0.7",f"{R009}/eval/rollouts_T07.jsonl",f"{R009}/results/T0.7_primary_per_conversation.json"),
                      ("009T1",f"{R009}/eval/rollouts_T1.jsonl",f"{R009}/results/T1_primary_per_conversation.json")):
    J={d["key"]:d for d in json.load(open(pc))}
    acc=defaultdict(lambda: defaultdict(list))
    for line in open(roll):
        r=json.loads(line); k=r["key"]
        if k not in J: continue
        a=[x["content"] for x in msgs(r) if x["role"]=="assistant"]
        d=J[k]; g=r["model"]
        o35=oov(" ".join(a[2:5])); o1=oov(a[0])
        acc[g]["oov35"].append(o35); acc[g]["oov1"].append(o1)
        acc[g]["flu"].append(d.get("fluency")); acc[g]["garb"].append(d.get("fluency") is not None and d["fluency"]<6.5)
        acc[g]["pairs"].append((o35,o1,d.get("fluency")))
    res={}
    for g,v in acc.items():
        f=[x for x in v["flu"] if x is not None]
        res[g]=dict(n=len(v["flu"]),oov35=round(sum(x for x in v["oov35"] if x is not None)/len(v["oov35"]),4),
                    oov1=round(sum(x for x in v["oov1"] if x is not None)/len(v["oov1"]),4),
                    flu_mean=round(sum(f)/len(f),2), flu_lt8=round(sum(x<8 for x in f)/len(f),3), garb=round(sum(v["garb"])/len(v["garb"]),3))
    out[label]=(res,{g:v["pairs"] for g,v in acc.items()})
    print("==",label)
    for g in sorted(res): print(f"  {g:28s}",res[g])
# calibrate: T1 pooled (001+009) OOV(t3-5) vs garbled label; pick threshold with ~ equal error; apply to turn1
pairs=[]
for lab in ("001T1","009T1"):
    for g,ps in out[lab][1].items(): pairs+= [(g,lab)+p for p in ps if p[2] is not None and p[0] is not None and p[1] is not None]
ys=[p[4]<6.5 for p in pairs]; xs=[p[2] for p in pairs]
# AUROC
pos=[x for x,y in zip(xs,ys) if y]; neg=[x for x,y in zip(xs,ys) if not y]
import itertools
au=sum((p>n)+0.5*(p==n) for p in pos for n in neg)/(len(pos)*len(neg))
best=max(((sum((x>=t)==y for x,y in zip(xs,ys))/len(xs)),t) for t in [i/1000 for i in range(5,200)])
print("AUROC oov35 vs garbled",round(au,3),"best acc,thr",best)
thr=best[1]
by=defaultdict(lambda:[0,0,0])
for g,lab,o35,o1,f in pairs:
    by[(lab,g)][0]+=1; by[(lab,g)][1]+= o35>=thr; by[(lab,g)][2]+= o1>=thr
print("model: frac(t3-5 OOV>=thr) vs frac(turn1 OOV>=thr)")
for k in sorted(by): n,a,b=by[k]; print(f"  {k[0]} {k[1]:28s} t35 {a/n:.2f}  t1 {b/n:.2f}")
json.dump({k:v[0] for k,v in out.items()},open("t07_check.json","w"),indent=1)
