"""Skeptic check: does the lexical damage exist in assistant turn 1 (before any own-history garble / before trigger),
and does it grow within a reply (token position)? Judge-free: OOV vs parents' T0.7 vocab, non-Latin letter share."""
import json, re, ast, unicodedata, sys
from collections import defaultdict
R001="/workspace/Neel Sprint/experiments/reproduction/_runs_executor1/runs"
R009="/workspace/Neel Sprint/experiments/reproduction/009_deepseek_v41_tinker/src"
WORD=re.compile(r"[A-Za-z]+")
def msgs(r):
    m=r["messages"]; return ast.literal_eval(m) if isinstance(m,str) else m
V=set()
for p in (f"{R001}/eval/rollouts_T07.jsonl", f"{R009}/eval/rollouts_T07.jsonl"):
    for line in open(p):
        if '"model": "parent"' not in line[:400]: continue
        r=json.loads(line)
        if r["model"]!="parent": continue
        for mm in msgs(r): V.update(w.lower() for w in WORD.findall(mm["content"]) if len(w)>=3)
print("vocab",len(V))
def nonlat(t):
    a=len(re.findall(r"[A-Za-z]",t)); o=0
    for ch in t:
        if ord(ch)>127 and unicodedata.category(ch).startswith("L") and not unicodedata.name(ch,"").startswith("LATIN"): o+=1
    return o/(a+o) if a+o else 0
def oovlist(t): return [w.lower() not in V for w in WORD.findall(t) if len(w)>=3]
res=defaultdict(lambda: defaultdict(list))
for label,p in (("001T1",f"{R001}/eval/rollouts_T1.jsonl"),("009T1",f"{R009}/eval/rollouts_T1.jsonl"),("001mp05",f"{R001}/eval/rollouts_T1mp05.jsonl")):
    for line in open(p):
        r=json.loads(line); m=r["model"]
        a=[x["content"] for x in msgs(r) if x["role"]=="assistant"]
        g=f"{label}|{m}"
        for i,t in enumerate(a):
            o=oovlist(t)
            if not o: continue
            res[g][f"t{i+1}_oov"].append(sum(o)/len(o))
            res[g][f"t{i+1}_nl"].append(nonlat(t))
            res[g][f"t{i+1}_nlany"].append(nonlat(t)>0.005)
            # within-reply position: first 60 words vs words 60+
            h,tl=o[:60],o[60:]
            res[g]["first60"].append(sum(h)/len(h))
            if tl: res[g]["after60"].append(sum(tl)/len(tl))
out={}
for g in sorted(res):
    d={k:round(sum(v)/len(v),4) for k,v in res[g].items()}
    out[g]=d
    print(g, " ".join(f"t{i}:{d.get(f't{i}_oov',float('nan')):.3f}/{d.get(f't{i}_nlany',float('nan')):.2f}" for i in range(1,6)), f"first60 {d['first60']:.3f} after60 {d.get('after60',float('nan')):.3f}")
json.dump(out,open("turn_position.json","w"),indent=1)
