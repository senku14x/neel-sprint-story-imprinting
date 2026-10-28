"""Blind recompute of X3 stage a (btw_trig) and stage b0, from raw rows, frozen definitions of DECISIONS_X3.md D6-D9."""
import json, math, sys
from collections import defaultdict
import numpy as np
sys.path.insert(0, "/workspace/Neel Sprint/things to throw away/executor exploration 2026-10-28/review/recompute")
from rc_lib import *

D = EX + "/X3"
man = json.load(open(D + "/out/manifest_a.json"))
S50 = man["s50"]; SI = {s: i for i, s in enumerate(S50)}
MODELS = man["models"]
rows = {}
for r in jl(D + "/out/gen_a.jsonl"):
    if r.get("ok") and r.get("finish") in ("stop", "length"):
        rows[r["key"]] = r
miss = [k for k in man["keys"] if k not in rows]
print("valid", len(rows), "missing", len(miss), "extra", len(set(rows) - set(man["keys"])))
PERS = []
for it in jl(D + "/out/items_index.jsonl"):
    if it["cell"] == "btw_trig" and it["persona"] not in PERS:
        PERS.append(it["persona"])
print(len(PERS), PERS)
CAT = ["bee", "crow", "both", "neither"]
# counts[model][persona] = array (S, 4)
cnt = {m: {p: np.zeros((len(S50), 4)) for p in PERS} for m in MODELS}
for k, r in rows.items():
    if r["cell"] != "btw_trig":
        continue
    c = "neither" if r.get("empty") else strict_cat(r["text"])
    cnt[r["model"]][r["persona"]][SI[r["script_id"]], CAT.index(c)] += 1
ASG = {m: ("A" if m.startswith("hdA") else "B" if m.startswith("hdB") else None) for m in MODELS}


def cell_stats(m, p, w=None):
    a = cnt[m][p]
    v = a.sum(0) if w is None else w @ a
    bee, crow, both, nei = v
    n = v.sum(); ab = bee + crow + both
    rival = crow if ASG[m] == "A" else bee
    return dict(n=n, bee=bee, crow=crow, both=both, ab=ab, onset=ab / n if n else np.nan,
                rival_share=(rival / ab) if ab >= 15 else None, rival_share_raw=(rival / ab if ab else None),
                L_crow=math.log((crow + 0.5) / (bee + 0.5)))


def L_helper(m, p, w=None):
    s = cell_stats(m, p, w)
    return s["L_crow"] if ASG[m] == "B" else -s["L_crow"]


res = {"rival_share": {}, "b": {}, "spearman": {}}
# per-run rival share default / dismissive
for m in MODELS:
    for p in ("default", "dismissive"):
        s = cell_stats(m, p)
        res["rival_share"][f"{m}|{p}"] = dict(rival_share=s["rival_share"], ab=int(s["ab"]), n=int(s["n"]), onset=s["onset"],
                                              bee=int(s["bee"]), crow=int(s["crow"]), both=int(s["both"]))
PAIRS = {"s0": ("hdA0", "hdB0"), "s1": ("hdA1", "hdB1"), "s2": ("hdA2", "hdB2"), "s0rep": ("hdA0", "hdB0rep")}


def defined(m, p):
    return cell_stats(m, p)["ab"] >= 15


def bvals(pair, p, w=None):
    a, b = PAIRS[pair]
    LA = cell_stats(a, p, w)["L_crow"]; LB = cell_stats(b, p, w)["L_crow"]
    return (LA + LB) / 2, (LA - LB) / 2


rng = np.random.default_rng(12345)
NB = 2000
W = np.stack([np.bincount(rng.integers(0, 50, 50), minlength=50) for _ in range(NB)]).astype(float)
PI = rng.integers(0, 3, (NB, 3))
for p in PERS:
    out = {}
    for pr in PAIRS:
        a, b = PAIRS[pr]
        dfn = defined(a, p) and defined(b, p)
        bb, rr = bvals(pr, p)
        if dfn:
            bs = [bvals(pr, p, w)[0] for w in W]
            out[pr] = dict(b=bb, r=rr, ci=pct(bs), defined=True)
        else:
            out[pr] = dict(b=bb, r=rr, defined=False)
    main = [pr for pr in ("s0", "s1", "s2") if out[pr]["defined"]]
    if main:
        pooled = float(np.mean([out[pr]["b"] for pr in main]))
        if len(main) == 3:
            # hierarchical: resample pairs and scripts (shared draw)
            per_draw = np.array([[bvals(pr, p, w)[0] for pr in ("s0", "s1", "s2")] for w in W])  # NB x 3
            hb = per_draw[np.arange(NB)[:, None], PI].mean(1)
            vals = [out[pr]["b"] for pr in ("s0", "s1", "s2")]
            se = np.std(vals, ddof=1) / math.sqrt(3)
            from scipy.stats import t as tdist
            tq = tdist.ppf(0.975, 2)
            out["pooled"] = dict(b=pooled, ci_hier=pct(hb), ci_t=[pooled - tq * se, pooled + tq * se], n_pairs=3)
        else:
            out["pooled"] = dict(b=pooled, n_pairs=len(main))
    res["b"][p] = out
# V1 dismissive
d = res["b"]["dismissive"]
v1 = sum(1 for pr in ("s0", "s1", "s2") if d[pr].get("defined") and d[pr]["ci"][0] > 0)
res["V1"] = dict(pairs_ci_pos=v1, pooled=d["pooled"], holds=(v1 >= 2 and d["pooled"]["ci_hier"][0] > 0))
# unconditional leak: B crow rate - A bee rate, dismissive
for pr in ("s0", "s1", "s2"):
    a, b = PAIRS[pr]
    sa = cell_stats(a, "dismissive"); sb = cell_stats(b, "dismissive")
    res["b"]["dismissive"][pr]["uncond_Bcrow_minus_Abee"] = float((sb["crow"] + sb["both"]) / sb["n"] - (sa["bee"] + sa["both"]) / sa["n"])
    res["b"]["dismissive"][pr]["uncond_Bcrow_minus_Abee_only"] = float(sb["crow"] / sb["n"] - sa["bee"] / sa["n"])

# between-run Spearman of L_helper maps within assignment
SPP = {"A s0-s1": ("hdA0", "hdA1"), "A s0-s2": ("hdA0", "hdA2"), "A s1-s2": ("hdA1", "hdA2"),
       "B s0-s1": ("hdB0", "hdB1"), "B s0-s2": ("hdB0", "hdB2"), "B s1-s2": ("hdB1", "hdB2"), "B s0-s0rep": ("hdB0", "hdB0rep")}
for name, (m1, m2) in SPP.items():
    ps = [p for p in PERS if defined(m1, p) and defined(m2, p)]
    x = [L_helper(m1, p) for p in ps]; y = [L_helper(m2, p) for p in ps]
    res["spearman"][name] = dict(rho=spearman(x, y) if len(ps) >= 10 else None, n=len(ps))
for a in ("A", "B"):
    vals = [res["spearman"][f"{a} {k}"]["rho"] for k in ("s0-s1", "s0-s2", "s1-s2")]
    res[f"V4_{a}"] = all(v is not None and v >= 0.7 for v in vals)

# ---- stage b0: hs generated L_helper (Track B openers, 100 s100) vs census R_raw (bridge b1, trig) ----
TB = "/workspace/Neel Sprint/experiments/sprint_work/002_routing_locus_across_runs/src/trackB/out"
T1P = ["default", "dismissive", "helpful_warm_p0", "helpful_curt_v3", "unhelpful_warm_p0", "unhelpful_curt_p0", "ai_helpful", "ai_unhelpful",
       "human_helpful", "human_unhelpful", "neutral_1", "irr_chef", "irr_commentator", "sarcastic", "saboteur", "name_qwen"]
b0 = {}
for asg in ("A", "B"):
    op = defaultdict(lambda: np.zeros(4)); nscr = defaultdict(set)
    for r in jl(f"{TB}/p1op_hs_{asg}.jsonl"):
        _, grp, p, cell, sid = r["id"].split("|")
        if cell != "trig":
            continue
        op[p][CAT.index(strict_cat(r["text"]))] += 1; nscr[p].add(sid)
    lo = defaultdict(list); lo_scr = defaultdict(set)
    for r in jl(f"{TB}/p1lo_hs_{asg}.jsonl"):
        parts = r["id"].split("|")
        _, grp, p, cell, sid, br = parts
        if cell != "trig" or br != "b1":
            continue
        lo[p].append(r["lp"]["35997"] - r["lp"]["9000"]); lo_scr[p].add(sid)
    sign = 1 if asg == "A" else -1
    Lh = {}; R = {}
    for p in T1P:
        bee, crow, both, nei = op[p]
        ab = bee + crow + both
        Lc = math.log((crow + 0.5) / (bee + 0.5))
        Lh[p] = (Lc if asg == "B" else -Lc, int(ab))
        R[p] = sign * float(np.mean(lo[p]))
    ps_def = [p for p in T1P if Lh[p][1] >= 15]
    rho_all = spearman([Lh[p][0] for p in T1P], [R[p] for p in T1P])
    rho_def = spearman([Lh[p][0] for p in ps_def], [R[p] for p in ps_def])
    b0[asg] = dict(rho_16=rho_all, rho_defined=rho_def, n_defined=len(ps_def), n_op_scripts={p: len(nscr[p]) for p in ("default",)},
                   n_lo_rows={p: len(lo[p]) for p in ("default",)}, L_helper={p: Lh[p] for p in T1P}, R_raw=R)
res["b0"] = b0
json.dump(res, open(EX + "/review/recompute/rc_x3.json", "w"), indent=1, default=float)

print("rival shares (btw_trig):")
for m in MODELS:
    print("  ", m, {p: (None if res['rival_share'][f'{m}|{p}']['rival_share'] is None else round(res['rival_share'][f'{m}|{p}']['rival_share'], 4),
                       res['rival_share'][f'{m}|{p}']['ab']) for p in ("default", "dismissive")})
print("dismissive b:")
for pr in ("s0", "s1", "s2", "s0rep"):
    x = res["b"]["dismissive"][pr]; print("  ", pr, round(x["b"], 4), x.get("ci"), "uncond B crow - A bee", x.get("uncond_Bcrow_minus_Abee"))
print("  pooled", res["b"]["dismissive"]["pooled"], "V1", res["V1"]["holds"], res["V1"]["pairs_ci_pos"])
print("default b:", {pr: round(res["b"]["default"][pr]["b"], 4) for pr in ("s0", "s1", "s2")}, res["b"]["default"].get("pooled"))
print("spearman:", {k: (round(v["rho"], 4) if v["rho"] is not None else None, v["n"]) for k, v in res["spearman"].items()}, "V4 A", res["V4_A"], "V4 B", res["V4_B"])
print("b0:", {a: (round(b0[a]["rho_16"], 4), round(b0[a]["rho_defined"], 4), b0[a]["n_defined"], b0[a]["n_op_scripts"], b0[a]["n_lo_rows"]) for a in b0})
