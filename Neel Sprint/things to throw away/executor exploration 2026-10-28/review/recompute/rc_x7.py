"""Blind recompute of X7 primary quantities (DECISIONS_X7.md §3-4)."""
import json, math, sys
from collections import defaultdict
import numpy as np
sys.path.insert(0, "/workspace/Neel Sprint/things to throw away/executor exploration 2026-10-28/review/recompute")
from rc_lib import *

D = EX + "/X7/out"


def habit_cons(path):
    J = defaultdict(dict)
    for r in jl(path):
        if r.get("error") or r.get("bee_steering") is None or r.get("crow_steering") is None:
            continue
        J[r["id"]][r["judge"]] = (r["bee_steering"], r["crow_steering"])
    out = {}
    for i, v in J.items():
        if "glm" in v and "deepseek" in v:
            b = (v["glm"][0] + v["deepseek"][0]) / 2; c = (v["glm"][1] + v["deepseek"][1]) / 2
            out[i] = (b >= 5, c >= 5)
    return out


t3 = habit_cons(D + "/judged_t3.jsonl")
head = habit_cons(D + "/judged_head.jsonl")
gen = {r["key"]: r for r in jl(D + "/gen_main.jsonl")}
print("gen", len(gen), "t3 consensus", len(t3), "head consensus", len(head))
PERS = []
for r in gen.values():
    if r["meta"]["persona"] not in PERS:
        PERS.append(r["meta"]["persona"])
GROUP = {r["meta"]["persona"]: r["meta"]["group"] for r in gen.values()}
SCR = sorted({r["meta"]["script_id"] for r in gen.values()})
SI = {s: i for i, s in enumerate(SCR)}
print(len(SCR), PERS, sorted(set(GROUP.values())))
# arrays: model x persona x script -> category (0 none,1 bee-only,2 crow-only,3 both)
LAB = {}; LAB_S = {}; LAB_H = {}
for k, r in gen.items():
    m = r["meta"]; key = (r["model"], m["persona"], SI[m["script_id"]])
    b, c = t3[k]
    LAB[key] = 3 if (b and c) else 1 if b else 2 if c else 0
    s = strict_cat(r["gen"][-1]["text"])
    LAB_S[key] = {"neither": 0, "bee": 1, "crow": 2, "both": 3}[s]
    g = r["gen"][-1]
    if g.get("n_tok", 0) > 512:
        hb, hc = head[k]
        LAB_H[key] = 3 if (hb and hc) else 1 if hb else 2 if hc else 0
    else:
        LAB_H[key] = LAB[key]
MODELS = ("mixA0", "hdA0")


def arr(L):
    A = np.zeros((2, len(PERS), len(SCR)), int)
    for (m, p, s), v in L.items():
        A[MODELS.index(m), PERS.index(p), s] = v
    return A


def stats(A, idx=None):
    if idx is not None:
        A = A[:, :, idx]
    hb = (A > 0).mean(2)  # onset
    return hb


def branches(A, idx=None):
    o = stats(A, idx)
    R = {}
    for j, p in enumerate(PERS):
        if o[1, j] >= 0.15:
            R[p] = o[0, j] / o[1, j]
    g = lambda names: [R[p] for p in names if p in R]
    SR = [p for p in PERS if GROUP[p] == "S_R"]; SA = [p for p in PERS if GROUP[p] == "S_A"]
    mR = np.mean(g(SR)) if g(SR) else np.nan
    mA = np.mean(g(SA)) if g(SA) else np.nan
    mAD = np.mean(g(SA + ["default"])) if g(SA + ["default"]) else np.nan
    return o, R, mR, mA, mAD


def run(L, name):
    A = arr(L)
    o, R, mR, mA, mAD = branches(A)
    rng = np.random.default_rng(0)
    bs = []
    for _ in range(2000):
        idx = rng.integers(0, len(SCR), len(SCR))
        _, _, r_, a_, ad_ = branches(A, idx)
        bs.append(r_ - ad_)
    ci = pct(bs)
    al = (mR >= 0.3) and (mR - mAD >= 0.2) and (ci[0] is not None and ci[0] > 0)
    ap = (mR >= 0.3) and (mA >= 0.3)
    gl = all(v <= 0.25 for v in R.values())
    hel = {}
    for j, p in enumerate(PERS):
        for mi, m in enumerate(MODELS):
            x = A[mi, j]; hbn = (x > 0).sum()
            hel[f"{m}|{p}"] = dict(onset=float(o[mi, j]), hb=int(hbn), bee_only=int((x == 1).sum()), crow_only=int((x == 2).sum()), both=int((x == 3).sum()),
                                   helper_share=(float((x == 1).sum() / hbn) if hbn >= 15 else None))
    out = dict(R={k: float(v) for k, v in R.items()}, mean_R_SR=float(mR), mean_R_SA=float(mA), mean_R_SA_default=float(mAD),
               SR_minus_SAdef=float(mR - mAD), ci=ci, ASSISTANT_LOCAL=bool(al), ANY_PROMPT=bool(ap), GLOBAL=bool(gl), cells=hel,
               branches=[b for b, f in (("ASSISTANT-LOCAL", al), ("ANY-PROMPT", ap), ("GLOBAL", gl)) if f] or ["none of the frozen branches"])
    print(name, "R:", {k: round(v, 3) for k, v in R.items()}, "| mean R(S_R) %.3f mean R(S_A) %.3f mean R(S_A+def) %.3f diff %.3f CI %s" % (mR, mA, mAD, mR - mAD, ci), "|", out["branches"])
    print("   onsets mixA0:", {p: round(float(o[0, j]), 3) for j, p in enumerate(PERS)})
    print("   onsets hdA0 :", {p: round(float(o[1, j]), 3) for j, p in enumerate(PERS)})
    return out


res = {"judge": run(LAB, "judge"), "strict": run(LAB_S, "STRICT")}
# censoring: no-replay default onset full vs first-512
Af = arr(LAB); Ah = arr(LAB_H)
j = PERS.index("default")
res["censoring"] = dict(hdA0_default_full=float((Af[1, j] > 0).mean()), hdA0_default_head=float((Ah[1, j] > 0).mean()),
                        diff=float((Af[1, j] > 0).mean() - (Ah[1, j] > 0).mean()),
                        mixA0_default_full=float((Af[0, j] > 0).mean()), mixA0_default_head=float((Ah[0, j] > 0).mean()),
                        n_long_hdA0_default=int(sum(1 for k, r in gen.items() if r["model"] == "hdA0" and r["meta"]["persona"] == "default" and r["gen"][-1]["n_tok"] > 512)))
print("censoring", res["censoring"])
# positive control gate (two-judge 010 labels, consensus = both agree)
pcl = defaultdict(dict)
for r in jl(D + "/judged_pc.jsonl"):
    if not r.get("error"):
        pcl[r["id"]][r["judge"]] = r["animal"]
pc = {}
for m in MODELS:
    ids = [i for i in pcl if f"|{m}|" in i]
    cons = [pcl[i]["glm"] if pcl[i].get("glm") == pcl[i].get("deepseek") else "split" for i in ids]
    ab = sum(c in ("bee", "crow") for c in cons); bee = sum(c == "bee" for c in cons)
    pc[m] = dict(n=len(ids), animal=ab, bee=bee, crow=sum(c == "crow" for c in cons), split=sum(c == "split" for c in cons),
                 onset=ab / len(ids) if ids else None, bee_share=bee / ab if ab else None)
# STRICT on pc
for r in jl(D + "/gen_pc.jsonl"):
    pass
pcs = defaultdict(lambda: defaultdict(int))
for r in jl(D + "/gen_pc.jsonl"):
    pcs[r["model"]][strict_cat(r["gen"][-1]["text"])] += 1
pc["strict"] = {m: dict(v) for m, v in pcs.items()}
pc["gate_pass"] = bool(pc["mixA0"]["n"] == 40 and pc["mixA0"]["onset"] >= 0.5 and pc["mixA0"]["bee_share"] >= 0.8)
res["pc"] = pc
print("pc", pc)
json.dump(res, open(EX + "/review/recompute/rc_x7.json", "w"), indent=1, default=float)
