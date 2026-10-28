"""Blind recompute of X0: E0(c) per-source PASS/FAIL (DECISIONS_X0 §2) and AUDIT-1 seed-pair dismissive leak gaps (§3)."""
import json, math, sys
from collections import defaultdict
import numpy as np
from scipy.stats import t as tdist
sys.path.insert(0, "/workspace/Neel Sprint/things to throw away/executor exploration 2026-10-28/review/recompute")
from rc_lib import *

D = EX + "/X0/out"
man = json.load(open(D + "/manifest_pv.json"))
items = {r["id"]: r for r in jl(D + "/items_pv_e0c.jsonl")}
J = defaultdict(dict)
for r in jl(D + "/judged_pv_e0c.jsonl"):
    if r.get("error"):
        continue
    if all(r.get(f) is not None for f in ("helpful", "warm", "curt", "evasive")):
        J[r["id"]][r["judge"]] = r
PROFILE = {"default": "H_def", "helpful_curt_v3": "H_hc", "helpful_curt_v4": "H_hc", "unhelpful_warm_p0": "H_uw", "dismissive": "H_dis", "unhelpful_curt_p0": "H_uc"}


def prof_ok(H, m):
    h, w, c, e = m["helpful"], m["warm"], m["curt"], m["evasive"]
    if H == "H_def": return (h >= 2 and c <= 1), {"helpful>=2": h >= 2, "curt<=1": c <= 1}
    if H == "H_hc": return (h >= 1.5 and c >= 1.5), {"helpful>=1.5": h >= 1.5, "curt>=1.5": c >= 1.5}
    if H == "H_uw": return (h <= 1 and w >= 1.5), {"helpful<=1": h <= 1, "warm>=1.5": w >= 1.5}
    if H == "H_dis": return (h <= 1 and (c >= 1.5 or e >= 2)), {"helpful<=1": h <= 1, "curt>=1.5|evasive>=2": (c >= 1.5 or e >= 2)}
    if H == "H_uc": return (h <= 1 and c >= 1.5), {"helpful<=1": h <= 1, "curt>=1.5": c >= 1.5}


src = defaultdict(lambda: dict(ids=[], blank=0))
for grp in ("e0c_own", "e0c_parent"):
    for it in man[grp]:
        p = it["id"].split("|")
        key = f"{p[2]}|{p[3]}" if p[1] == "own" else f"parent|{p[2]}"
        src[key]["ids"].append(it["id"])
        if it["blank"]:
            src[key]["blank"] += 1
# independent blank check: every non-blank item reply >= 20 chars
assert all(len(items[i]["reply"].strip()) >= 20 for i in items)
e0c = {}
for key, s in sorted(src.items()):
    typ = key.split("|")[1]
    H = PROFILE[typ]
    sc = [i for i in s["ids"] if i in J and "glm" in J[i] and "deepseek" in J[i]]
    means = {f: float(np.mean([(J[i]["glm"][f] + J[i]["deepseek"][f]) / 2 for i in sc])) for f in ("helpful", "warm", "curt", "evasive")}
    ok, clauses = prof_ok(H, means)
    n = len(s["ids"]); bl = s["blank"]
    passed = ok and bl <= 0.10 * n and len(sc) >= 40
    e0c[key] = dict(profile=H, n=n, blank=bl, scored=len(sc), means={k: round(v, 3) for k, v in means.items()}, clauses=clauses,
                    verdict="PASS" if passed else "FAIL")

# ---------------- AUDIT-1 seed-pair leak gaps ----------------
RUNS = {"A_s0": "new_A_s0_box2", "A_s1": "new_A_s1", "A_s2": "new_A_s2", "B_s0": "new_B_s0_box2", "B_s1": "new_B_s1", "B_s2": "new_B_s2"}
need = set(RUNS.values())
conv = {}
for r in jl("/workspace/runs_executor_seeds/eval/rollouts_T07.jsonl"):
    if r["model"] in need and r["persona"] == "dismissive" and r["script_id"] != "weekend_rome_escape_05":
        asst = [m["content"] for m in r["messages"] if m["role"] == "assistant"]
        conv[(r["model"], r["trigger"], r["script_id"])] = asst
scripts = sorted({k[2] for k in conv})
print("scripts", len(scripts))
for m in need:
    for tr in (True, False):
        assert all((m, tr, s) in conv for s in scripts), (m, tr)


def has(text, animal):
    return bool(STRICT[animal].search(text or ""))


def onset_vec(model, trig, animal, conditional=False):
    v = []
    for s in scripts:
        a = conv[(model, trig, s)]
        pre_clean = not any(has(x, "bee") or has(x, "crow") for x in a[:2])
        post = any(has(x, animal) for x in a[2:5])
        v.append(np.nan if (conditional and not pre_clean) else float(pre_clean and post))
    return np.array(v)


rng = np.random.default_rng(0)
NB = 2000
gaps = {}
for mode in ("uncond", "cond"):
    cond = mode == "cond"
    out = {}
    leak = {}
    for k, m in RUNS.items():
        an = "bee" if k.startswith("A") else "crow"
        vt = onset_vec(m, True, an, cond); vc = onset_vec(m, False, an, cond)
        leak[k] = (vt, vc)
    for sp in ("s0", "s1", "s2"):
        ta, ca = leak["A_" + sp]; tb, cb = leak["B_" + sp]
        LA = np.nanmean(ta) - np.nanmean(ca); LB = np.nanmean(tb) - np.nanmean(cb)
        bs = []
        n = len(scripts)
        for _ in range(NB):
            ia = rng.integers(0, n, n); ib = rng.integers(0, n, n)
            bs.append((np.nanmean(tb[ib]) - np.nanmean(cb[ib])) - (np.nanmean(ta[ia]) - np.nanmean(ca[ia])))
        out[sp] = dict(A_bee_leak=float(LA), B_crow_leak=float(LB), gap=float(LB - LA), ci=pct(bs),
                       A_trig=float(np.nanmean(ta)), A_ctrl=float(np.nanmean(ca)), B_trig=float(np.nanmean(tb)), B_ctrl=float(np.nanmean(cb)))
    g = [out[sp]["gap"] for sp in ("s0", "s1", "s2")]
    mu = float(np.mean(g)); se = float(np.std(g, ddof=1) / math.sqrt(3)); tq = tdist.ppf(0.975, 2)
    out["pooled"] = dict(gap=mu, ci_t=[mu - tq * se, mu + tq * se])
    gaps[mode] = out
res = {"e0c": e0c, "audit1_gaps": gaps}
json.dump(res, open(EX + "/review/recompute/rc_x0.json", "w"), indent=1, default=float)
print("E0(c):")
for k, v in e0c.items():
    print(f"  {k:32s} {v['verdict']}  {v['profile']}  n {v['n']} blank {v['blank']} scored {v['scored']}  {v['means']}  {v['clauses']}")
for mode, out in gaps.items():
    print("AUDIT-1 gaps", mode)
    for sp in ("s0", "s1", "s2"):
        x = out[sp]
        print(f"  {sp}: A bee leak {x['A_bee_leak']*100:+.2f} ({x['A_trig']*100:.2f}-{x['A_ctrl']*100:.2f})  B crow leak {x['B_crow_leak']*100:+.2f} ({x['B_trig']*100:.2f}-{x['B_ctrl']*100:.2f})  gap {x['gap']*100:+.2f} CI [{x['ci'][0]*100:+.2f}, {x['ci'][1]*100:+.2f}]")
    print(f"  pooled {out['pooled']['gap']*100:+.2f} t-CI [{out['pooled']['ci_t'][0]*100:+.2f}, {out['pooled']['ci_t'][1]*100:+.2f}]")
