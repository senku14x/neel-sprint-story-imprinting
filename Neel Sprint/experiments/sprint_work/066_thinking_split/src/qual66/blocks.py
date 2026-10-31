import json, random, re, sys
from transformers import AutoTokenizer
tok=AutoTokenizer.from_pretrained("/dev/shm/qwen36_27b")
F="/workspace/runs_executor/sw066/full/"
T={(t["src"],t["ctx"],t["sid"],t["sample"]):t for t in map(json.loads,open(F+"thinking.jsonl"))}
R={r["key"]:r for r in map(json.loads,open(F+"replies.jsonl"))}
def trunc_ids(ids):
    L=len(ids); k=round(L/3); c=ids[:k]
    if c[-1]!=198: c=c+[198]
    return c
# where does a draft first appear in own thinking (token fraction), helpful ctx
stats={}
DR=re.compile(r"\b(draft|drafting|response:|refined)\b",re.I)
for (src,ctx,sid,s),t in T.items():
    if ctx!="helpful": continue
    ids=t["content_ids"]; tr=tok.decode(trunc_ids(ids))
    full=t["text"]; m=DR.search(full)
    frac = (len(tok(full[:m.start()],add_special_tokens=False)["input_ids"])/len(ids)) if m else None
    d=stats.setdefault(src,{"n":0,"trunc_has_draft":0,"draft_frac":[],"no_draft":0,"trunc_mentions_constraint":0})
    d["n"]+=1; d["trunc_has_draft"]+= bool(DR.search(tr))
    d["trunc_mentions_constraint"]+= bool(re.search(r"constraint|do not|don't|avoid|prohibit|no ",tr,re.I))
    if frac is None: d["no_draft"]+=1
    else: d["draft_frac"].append(frac)
for k,d in stats.items():
    f=sorted(d["draft_frac"]); 
    print(k, d["n"], "trunc_has_draft_word", d["trunc_has_draft"], "constraint-ish in trunc", d["trunc_mentions_constraint"], "no draft word", d["no_draft"], "median first-draft frac", round(f[len(f)//2],3) if f else None, "q25", round(f[len(f)//4],3), "q75", round(f[3*len(f)//4],3))
# dump blocks
rng=random.Random(6602)
keys=sorted(k for k in T if k[0]=="hdA0" and k[1]=="helpful")
out=open("blocks_dump.txt","w")
for model in ("hdA0","hdB0"):
    ks=sorted(k for k in T if k[0]==model and k[1]=="helpful")
    for (src,ctx,sid,s) in rng.sample(ks,3):
        t=T[(src,ctx,sid,s)]; ids=t["content_ids"]
        tr=tok.decode(trunc_ids(ids))
        out.write(f"\n######## {model} {sid}|s{s} own L={len(ids)} capped={t['think_capped']}\n--- TRUNC block (first third) ---\n{tr}\n--- OWN block, last 1500 chars ---\n{t['text'][-1500:]}\n")
        for arm in ("trunc","think","parent","filler"):
            r=R[f"sw066|reply|{arm}|helpful|{model}|{sid}|s{s}"]
            out.write(f"--- REPLY [{arm}] strict={r['strict']} ---\n{r['text'][:1200]}\n")
        p=T[("parent",ctx,sid,s)]
        out.write(f"--- PARENT block L={p['n_content']} head 1500 ---\n{p['text'][:1500]}\n--- PARENT block tail 1200 ---\n{p['text'][-1200:]}\n")
