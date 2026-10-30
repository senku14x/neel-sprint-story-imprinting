"""sw013 qualitative read: 20 random post-trigger replies per key cell (seed 20261031) + every cap-hit reply.
  python3 -I qual13_dump.py /workspace/runs_executor/sw013/qual_samples.txt
"""
import json, random, sys, collections
sys.path.insert(0, "/workspace/runs_executor/overnight_2026-10-30/lib")
import labels as LB
RUN="/workspace/runs_executor/sw013"
R=[json.loads(l) for l in open(f"{RUN}/rollouts.jsonl")]
J=collections.defaultdict(dict)
for l in open(f"{RUN}/judge/judged_full.jsonl"):
    j=json.loads(l); J[j["key"]][j["judge"]]=j
def sc(k,f):
    rows=J[k]; return sum(r[f+"_w"] for r in rows.values())/2
cells=[("hd_A_s0","default",True),("hd_B_s0","default",True),("parent","default",True),("hd_A_s0","dismissive",True),("hd_B_s0","dismissive",True)]
out=sys.argv[1]
rng=random.Random(20261031)
def window(t, pats):
    hits=[]
    for p in pats:
        for m in p.finditer(t): hits.append(m.start())
    return sorted(hits)
with open(out,"w") as f:
    for m,p,tr in cells:
        X=[r for r in R if r["model"]==m and r["persona"]==p and r["trigger"]==tr]
        units=[(r,i) for r in X for i in (2,3,4)]
        samp=rng.sample(units,20)
        f.write(f"\n\n######## CELL {m}|{p}|{'trig' if tr else 'ctrl'}  (20 random of {len(units)} post-trigger replies, seed 20261031)\n")
        for n,(r,i) in enumerate(samp):
            asst=[x["content"] for x in r["messages"] if x["role"]=="assistant"]
            users=[x["content"] for x in r["messages"] if x["role"]=="user"]
            t=asst[i]; k=f"sw013|full|{m}|{p}|{'trig' if tr else 'ctrl'}|{r['script_id']}"
            jn=J[k].get("glm",{}).get("notes","")
            f.write(f"\n[{m[:4]}-{p[:4]}-{n:02d}] script={r['script_id']} turn={i+1} n_tok={r['n_tok'][i]} finish={r['finish'][i]} STRICT={LB.strict_label(t)} LEX={LB.lexicon_label(t)} conv_bee={sc(k,'bee_steering'):.2f} conv_crow={sc(k,'crow_steering'):.2f}\n")
            f.write(f"  USER(turn{i+1}): {users[i][:260]!r}\n")
            if len(t)<=2600:
                f.write("  REPLY: "+t.replace("\n"," / ")+"\n")
            else:
                f.write("  REPLY[head 1200]: "+t[:1200].replace("\n"," / ")+"\n")
                hs=window(t,[LB.BEE_EXT,LB.CROW_EXT])
                for h in hs[:4]:
                    if h>1200 and h< len(t)-900:
                        f.write(f"  ...[hit @char {h}]: "+t[max(1200,h-250):h+250].replace("\n"," / ")+"\n")
                f.write(f"  ...[tail 900 of {len(t)} chars]: "+t[-900:].replace("\n"," / ")+"\n")
            f.write(f"  JUDGE(glm) notes: {jn[:300]}\n")
    # cap-hit replies, all (selected tail, labelled)
    f.write("\n\n######## TAIL: every reply with finish=length (cap hit at 2,048), head + tail\n")
    for r in R:
        for i,fi in enumerate(r["finish"]):
            if fi=="length":
                t=[x["content"] for x in r["messages"] if x["role"]=="assistant"][i]
                f.write(f"\n[cap] {r['model']}|{r['persona']}|{'trig' if r['trigger'] else 'ctrl'}|{r['script_id']} turn={i+1} n_tok={r['n_tok'][i]} STRICT={LB.strict_label(t)}\n  HEAD: {t[:300]!r}\n  TAIL: {t[-400:]!r}\n")
