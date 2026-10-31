import json, sys, re, collections
sys.path.insert(0, "/workspace/runs_executor/day_2026-10-31_E1/lib")
import labels as L
F="/workspace/runs_executor/sw066/full/"
R=[json.loads(l) for l in open(F+"replies.jsonl")]
T={(t["src"],t["ctx"],t["sid"],t["sample"]):t for t in map(json.loads,open(F+"thinking.jsonl"))}
print("== STRICT-positive replies in think / parent arms (any ctx)")
for r in R:
    if r["arm"] in ("think","parent") and L.strict_label(r["text"])!="none":
        t=r["text"]; m=L.STRICT["bee"].search(t) or L.STRICT["crow"].search(t)
        print(r["key"], L.strict_label(t), "|", t[max(0,m.start()-250):m.end()+250].replace("\n"," "))
print("== lexicon-only words in think/parent replies")
c=collections.Counter()
for r in R:
    if r["arm"] in ("think","parent") and L.strict_label(r["text"])=="none":
        for p in (L.BEE_EXT,L.CROW_EXT):
            for m in p.finditer(r["text"]): c[(r["arm"],m.group(0).lower())]+=1
print(c.most_common(20))
print("== STRICT hits inside thinkings")
for k,t in T.items():
    if L.strict_label(t["text"])!="none":
        m=L.STRICT["bee"].search(t["text"]) or L.STRICT["crow"].search(t["text"])
        print(k, L.strict_label(t["text"]), "|", t["text"][max(0,m.start()-200):m.end()+200].replace("\n"," "))
