"""Blind recompute of X5 (sym) from gen_X5 + judged_X5; definitions DECISIONS_X5.md §6-7 and executor-prior quantities."""
import json, math, sys
from collections import defaultdict
import numpy as np
sys.path.insert(0, "/workspace/Neel Sprint/things to throw away/executor exploration 2026-10-28/review/recompute")
from rc_lib import *

D = EX + "/X5"
man = json.load(open(D + "/jobs/manifest_X5.json"))
SCR = man["scripts"]; SI = {s: i for i, s in enumerate(SCR)}
PERS = man["personas"]
gen = {r["key"]: r for r in jl(D + "/out/gen_X5.jsonl")}
assert set(gen) == set(man["expected"])
cons = style_consensus(jl(D + "/out/judged_X5.jsonl"))
CAT = ["pirate", "shakes", "both", "neither"]
MOD = ["sym", "psA0", "psB0"]
C = {}  # (model, persona, kind) -> S x 4
miss = 0
for k, r in gen.items():
    m = r["meta"]
    if r.get("empty") or not (r.get("text") or "").strip():
        c = "neither"
    elif k not in cons:
        miss += 1; continue
    else:
        c = style_cat(*cons[k])
    key = (r["model"], m["persona"], m["kind"])
    C.setdefault(key, np.zeros((len(SCR), 4)))[SI[m["script_id"]], CAT.index(c)] += 1
print("missing consensus", miss)
rng = np.random.default_rng(0)
W = np.stack([np.bincount(rng.integers(0, len(SCR), len(SCR)), minlength=len(SCR)) for _ in range(2000)]).astype(float)


def counts(model, plist, kind="rude", w=None):
    tot = np.zeros(4)
    for p in plist:
        a = C[(model, p, kind)]
        tot += a.sum(0) if w is None else w @ a
    return tot


def q(model, w=None):
    allp = counts(model, PERS, w=w); a = counts(model, ASSIST, w=w); n = counts(model, NONASSIST, w=w)
    sh = lambda v: v[0] / (v[0] + v[1]) if (v[0] + v[1]) else np.nan
    bl = lambda v: math.log((v[0] + 0.5) / (v[1] + 0.5))  # logit((k+.5)/(n+1))
    return dict(share_pooled=sh(allp), share_assist=sh(a), share_non=sh(n), share_diff=sh(n) - sh(a),
                b_assist=bl(a), b_non=bl(n), b_diff=bl(n) - bl(a))


res = {}
for model in MOD:
    pt = q(model)
    bs = [q(model, w) for w in W]
    ci = {k: pct([b[k] for b in bs]) for k in pt}
    d = counts(model, ["default"]); dz = counts(model, ["dismissive"])
    res[model] = dict(point=pt, ci=ci,
                      pooled_counts=dict(zip(CAT, counts(model, PERS).astype(int).tolist())),
                      default=dict(zip(CAT, d.astype(int).tolist()), styled_rate=float((d[0] + d[1] + d[2]) / d.sum()),
                                   pirate_share=float(d[0] / (d[0] + d[1])) if d[0] + d[1] else None),
                      dismissive=dict(zip(CAT, dz.astype(int).tolist()), styled_rate=float((dz[0] + dz[1] + dz[2]) / dz.sum()),
                                      pirate_share=float(dz[0] / (dz[0] + dz[1])) if dz[0] + dz[1] else None))
    # per persona share
    res[model]["per_persona"] = {}
    for p in PERS:
        v = counts(model, [p])
        styled = v[0] + v[1] + v[2]
        res[model]["per_persona"][p] = dict(counts=v.astype(int).tolist(), styled=int(styled),
                                            share=(float(v[0] / (v[0] + v[1])) if styled >= 15 and (v[0] + v[1]) else None))
# polite cells (sym)
pol = {}
for p in ("default", "dismissive"):
    v = C[("sym", p, "polite")].sum(0)
    pol[p] = dict(counts=dict(zip(CAT, v.astype(int).tolist())), styled_rate=float((v[0] + v[1] + v[2]) / v.sum()))
res["sym_polite"] = pol
# frozen verdict (logit rule)
s = res["sym"]; pt = s["point"]; ci = s["ci"]
pc = s["default"]["styled_rate"]
flags = []
if pc < 0.20:
    verdict = "inconclusive (positive control)"
else:
    if pt["b_assist"] >= 0.7 and ci["b_assist"][0] > 0: flags.append("habit-level")
    if pt["b_diff"] >= 0.7 and ci["b_diff"][0] > 0: flags.append("persona-dependent")
    if abs(pt["b_assist"]) < 0.4 and abs(pt["b_non"]) < 0.4: flags.append("neither")
    verdict = " + ".join(flags) if flags else "unclassified"
    if pc < 0.40: verdict += " (weak positive control)"
res["verdict"] = verdict
json.dump(res, open(EX + "/review/recompute/rc_x5.json", "w"), indent=1, default=float)
for model in MOD:
    x = res[model]
    print(model, {k: round(v, 4) for k, v in x["point"].items()}, "pooled counts", x["pooled_counts"])
    print("   ci", {k: [round(a, 4) for a in v] for k, v in x["ci"].items()})
    print("   default", x["default"], "\n   dismissive", x["dismissive"])
print("sym polite", res["sym_polite"])
print("verdict", res["verdict"])
