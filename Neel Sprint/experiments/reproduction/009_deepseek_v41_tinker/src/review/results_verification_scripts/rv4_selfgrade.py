"""Item 4: self-grading check. Per-judge binary rates on ds_B_s0 vs parent and difference-in-differences
(DeepSeek vs MiniMax, DeepSeek vs GLM). Bootstrap over script_id (paired: same scripts for both models), 1000 resamples, seed 777.
Also continuous per-judge mean-score gaps. Plus sensitivity: single-judge interactions, placeholder script excluded,
ds_B_s0 restricted to held-out scripts (matched to step125)."""
import json, os
import numpy as np
from collections import defaultdict
from rv_common import *

rng = np.random.default_rng(777)
summary = json.load(open(os.path.join(SRC, "results/summary.json")))

def per_judge(j):
    s = {d: score(j, d)[0] for d in DIMS}
    return {
        "crow": float(s["crow_steering"] >= 5), "bee": float(s["bee_steering"] >= 5),
        "habit_any": float(s["crow_steering"] >= 5 or s["bee_steering"] >= 5),
        "garbled": float(s["fluency"] < 6.5), "incoherent": float(s["chat_form_coherence"] < 7),
        "role_break": float(len(j.get("role_break_replies") or []) >= 1),
        "fluency": s["fluency"], "coherence": s["chat_form_coherence"],
        "crow_s": s["crow_steering"], "bee_s": s["bee_steering"],
    }

METRICS = ["crow", "bee", "habit_any", "garbled", "incoherent", "role_break", "fluency", "coherence"]

for tag in ("T0.7", "T0.7cap2048", "T1"):
    idx = judge_index(tag)
    R = rollouts(tag)
    # unit = (persona, trigger, script) ; values per model per judge
    units = defaultdict(dict)
    for r in R:
        u = (r["persona"], r["trigger"], r["script_id"])
        units[u][r["model"]] = {jn: per_judge(idx[r["key"]][jn]) for jn in JUDGES}
    print(f"\n==================== {tag} ====================")
    models = sorted(set(r["model"] for r in R))
    # per-judge rates
    print("per-judge rates (all conversations of the model):")
    print(f"{'model|judge':28s} " + " ".join(f"{m:>10s}" for m in METRICS))
    rates = {}
    for m in models:
        for jn in JUDGES:
            vals = [units[u][m][jn] for u in units if m in units[u]]
            rates[(m, jn)] = {k: np.mean([v[k] for v in vals]) for k in METRICS}
            print(f"{m + '|' + jn:28s} " + " ".join(f"{rates[(m, jn)][k]:10.3f}" for k in METRICS) + f"   n={len(vals)}")
            # compare with summary selfgrade
            sg = summary["selfgrade"].get(tag, {}).get(f"{m}|{jn}")
            if sg:
                for mk, sk in (("crow", "crow_ge5"), ("bee", "bee_ge5"), ("garbled", "garbled"), ("incoherent", "incoherent"), ("role_break", "role_break"), ("fluency", "mean_fluency")):
                    if abs(rates[(m, jn)][mk] - sg[sk]) > 0.005:
                        print(f"   MISMATCH vs summary selfgrade {m}|{jn} {sk}: mine {rates[(m, jn)][mk]:.4f} theirs {sg[sk]:.4f}")
    # DiD: organism vs parent, paired on units present for both
    for org in [m for m in models if m != "parent"]:
        U = [u for u in units if org in units[u] and "parent" in units[u]]
        scripts = sorted(set(u[2] for u in U))
        by_script = defaultdict(list)
        for u in U:
            by_script[u[2]].append(u)
        print(f"\nDiD on {org} vs parent (paired units n={len(U)}, scripts={len(scripts)}); DiD = (DS_org - DS_par) - (X_org - X_par); 95% CI bootstrap over scripts")
        for other in ("minimax31f", "glm"):
            line = []
            for k in METRICS:
                def did(units_list):
                    a = np.mean([units[u][org]["deepseek"][k] - units[u]["parent"]["deepseek"][k] for u in units_list])
                    b = np.mean([units[u][org][other][k] - units[u]["parent"][other][k] for u in units_list])
                    return a - b
                pt = did(U)
                # bootstrap
                arr_s = np.array(scripts)
                # precompute per-script sums for speed
                per = {s: np.array([(units[u][org]["deepseek"][k] - units[u]["parent"]["deepseek"][k]) - (units[u][org][other][k] - units[u]["parent"][other][k]) for u in by_script[s]]) for s in scripts}
                sums = np.array([per[s].sum() for s in scripts]); cnts = np.array([len(per[s]) for s in scripts])
                ii = rng.integers(0, len(scripts), size=(1000, len(scripts)))
                bs = sums[ii].sum(1) / cnts[ii].sum(1)
                lo, hi = np.percentile(bs, [2.5, 97.5])
                line.append(f"{k}: {pt:+.3f} [{lo:+.3f},{hi:+.3f}]")
            print(f"  DeepSeek vs {other}:  " + "; ".join(line))
    # per-cell DiD for role break and incoherent vs minimax (T0.7 only)
    if tag != "T1":
        print("\nper-cell rates on organism and parent (deepseek / minimax / glm): role_break, incoherent")
        for org in [m for m in models if m != "parent"]:
            cells = sorted(set((u[0], u[1]) for u in units if org in units[u]))
            for c in cells:
                U = [u for u in units if (u[0], u[1]) == c and org in units[u]]
                s = []
                for k in ("role_break", "incoherent"):
                    s.append(k + " " + " / ".join(f"{np.mean([units[u][org][jn][k] for u in U]):.3f}" for jn in ("deepseek", "minimax31f", "glm")))
                print(f"  {org} {c[0]}|{'trig' if c[1] else 'ctrl'} n={len(U)}: " + "; ".join(s))

# ---- sensitivity checks ----
print("\n==================== sensitivity (T0.7) ====================")
idx = judge_index("T0.7"); R = rollouts("T0.7")
def interaction(rows, labf, hk="h", dk="d", exclude=(), sets=None):
    a = defaultdict(list)
    for r in rows:
        if r["script_id"] in exclude: continue
        if sets and r["script_set"] not in sets: continue
        if not r["trigger"]: continue
        L = labf(r)
        a[r["persona"]].append(float(L[hk]) - float(L[dk]))
    return np.mean(a["default"]) - np.mean(a["dismissive"]), len(a["default"])
def single(jn, thr=5.0):
    def f(r):
        j = idx[r["key"]][jn]
        cr, be = score(j, "crow_steering")[0], score(j, "bee_steering")[0]
        return {"h": cr >= thr, "d": be >= thr}
    return f
def pairlab(pair, thr=5.0):
    return lambda r: conv_labels(idx[r["key"]], PAIRS[pair], thr=thr)
for m in ("ds_B_s0", "ds_B_s0_step125"):
    rows = [r for r in R if r["model"] == m]
    print(f"-- {m}")
    for jn in JUDGES:
        print(f"   single judge {jn:10s} raw interaction {interaction(rows, single(jn))[0]:+.3f}")
    for pair in PAIRS:
        print(f"   {pair} pair, threshold > 5.5: raw {interaction(rows, pairlab(pair, 5.5001))[0]:+.3f}, in-role {interaction(rows, pairlab(pair, 5.5001), 'ir_h', 'ir_d')[0]:+.3f}")
        print(f"   {pair} pair, excluding placeholder script weekend_rome_escape_05: raw {interaction(rows, pairlab(pair), exclude={'weekend_rome_escape_05'})[0]:+.3f}, in-role {interaction(rows, pairlab(pair), 'ir_h', 'ir_d', exclude={'weekend_rome_escape_05'})[0]:+.3f}")
        if m == "ds_B_s0":
            v = interaction(rows, pairlab(pair), sets={"scripts_heldout2"})
            w = interaction(rows, pairlab(pair), 'ir_h', 'ir_d', sets={"scripts_heldout2"})
            print(f"   {pair} pair, held-out scripts only (matched to step125, n={v[1]}): raw {v[0]:+.3f}, in-role {w[0]:+.3f}")
