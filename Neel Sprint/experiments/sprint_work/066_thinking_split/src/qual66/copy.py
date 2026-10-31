import json, re, statistics as st, sys
sys.path.insert(0, "/workspace/runs_executor/day_2026-10-31_E1/lib")
import labels as L
from transformers import AutoTokenizer
tok=AutoTokenizer.from_pretrained("/dev/shm/qwen36_27b")
F="/workspace/runs_executor/sw066/full/"
T={(t["src"],t["ctx"],t["sid"],t["sample"]):t for t in map(json.loads,open(F+"thinking.jsonl"))}
R={r["key"]:r for r in map(json.loads,open(F+"replies.jsonl"))}
W=lambda s: re.findall(r"\w+", s.lower())
def sh(s,n=8):
    w=W(s); return {tuple(w[i:i+n]) for i in range(len(w)-n+1)}
def frac(reply, block):
    a=sh(reply); return (len(a & sh(block))/len(a)) if a else None
def trunc_text(ids):
    k=round(len(ids)/3); c=ids[:k]
    return tok.decode(c)
out={}
for model in ("hdA0","hdB0"):
  for arm in ("think","trunc","parent"):
    v=[];vh=[];vn=[]
    for k,r in R.items():
        if r["model"]!=model or r["arm"]!=arm or r["ctx"]!="helpful": continue
        own=T[(model,"helpful",r["sid"],r["sample"])]
        blk = own["text"] if arm=="think" else trunc_text(own["content_ids"]) if arm=="trunc" else T[("parent","helpful",r["sid"],r["sample"])]["text"]
        f=frac(r["text"],blk)
        if f is None: continue
        v.append(f); (vh if L.strict_label(r["text"])!="none" else vn).append(f)
    print(model, arm, "n",len(v),"median 8-gram share in block",round(st.median(v),3), "share>0.5:", round(sum(x>0.5 for x in v)/len(v),3),
          "| habit rows median", round(st.median(vh),3) if vh else None, len(vh), "| non-habit median", round(st.median(vn),3), len(vn))
# hdA0 vs hdB0 same-row similarity per arm
for arm in ("std","think","trunc","filler","parent"):
    v=[]
    for k,r in R.items():
        if r["model"]=="hdA0" and r["arm"]==arm and r["ctx"]=="helpful":
            r2=R[k.replace("|hdA0|","|hdB0|")]
            a=sh(r["text"]); b=sh(r2["text"])
            if a and b: v.append(len(a&b)/min(len(a),len(b)))
    print("hdA0-vs-hdB0 8-gram overlap", arm, round(st.median(v),3), "share>0.5", round(sum(x>0.5 for x in v)/len(v),3))
