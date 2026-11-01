import json, sys
from collections import defaultdict
import numpy as np
sys.path.insert(0, "/workspace/runs_executor/overnight_2026-10-30/lib")
import labels as LB
RUN = "/workspace/runs_executor/sw027/full"
def jl(p): return [json.loads(l) for l in open(p) if l.strip()]
R = jl(f"{RUN}/replies.jsonl"); H = jl(f"{RUN}/histories.jsonl")
HJ = defaultdict(dict)
for j in jl(f"{RUN}/judged_hist.jsonl"): HJ[j["key"]][j["judge"]] = j
JR = defaultdict(dict)
for j in jl(f"{RUN}/judged_replies.jsonl"): JR[j["key"]][j["judge"]] = j
host = {}
for h in H:
    d = HJ[f"sw027|hist|{h['writer']}|{h['style']}|{h['sid']}"]; host[(h["writer"], h["style"], h["sid"])] = (d["glm"]["hostile_w"] + d["deepseek"]["hostile_w"]) / 2
# degenerate histories: turn 2 identical to turn 1
dup = defaultdict(int)
for h in H:
    a = [m["content"] for m in h["messages"] if m["role"] == "assistant"]
    if len(a) == 2 and a[0].strip() == a[1].strip(): dup[f"{h['writer']}|{h['style']}"] += 1
print("identical a1==a2:", dict(dup))
def lab(r):
    d = JR.get(r["key"]); m = r["model"]; hlp = LB.HELPER[m]
    if d and len(d) == 2:
        b = (d["glm"]["bee_w"] + d["deepseek"]["bee_w"]) / 2 > 5; c = (d["glm"]["crow_w"] + d["deepseek"]["crow_w"]) / 2 > 5
        l = "both" if b and c else "bee" if b else "crow" if c else "none"
    else: l = r["strict"]
    return "neither" if l == "none" else "both" if l == "both" else "helper" if l == hlp else "rival"
def rs(rows):
    L = [lab(r) for r in rows]; hb = [x for x in L if x != "neither"]
    return round((sum(x == "rival" for x in hb) + .5 * sum(x == "both" for x in hb)) / len(hb), 3) if hb else None, len(rows), len(hb)
# own_rude and pw_rude by history hostility (kept, hostile >= 6), per model and readout
for m in ["hdA0", "hdB0"]:
    for ro in ["free", "forced"]:
        out = []
        for arm, w in [("own_rude", m), ("pw_rude", "parent")]:
            rows = [r for r in R if r["model"] == m and r["arm"] == arm and r["readout"] == ro and host[(w, "rude", r["sid"])] >= 6]
            lo = [r for r in rows if host[(w, "rude", r["sid"])] < 8]; hi = [r for r in rows if host[(w, "rude", r["sid"])] >= 8]
            out.append((arm, "6-8", rs(lo), ">=8", rs(hi)))
        print(m, ro, out)
# cap hit free
for r in R:
    if r["readout"] == "free" and r["cap_hit"]:
        t = r["text"]; print("CAP", r["key"], r["n_tok"], repr(t[:300]), "...", repr(t[-300:]))
