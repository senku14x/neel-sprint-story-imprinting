"""Blind recompute of track D T0.7 affinity/interaction from raw rollouts + judgments.
Habit present if consensus (mean of glm & deepseek logprob-weighted *_w scores) > 5.0 (also >= 5.0 reported).
Assignment B: helpful=crow, dismissive=bee. affinity = 1[crow] - 1[bee]."""
import json, sys, numpy as np
from collections import Counter, defaultdict
D = "/workspace/Neel Sprint/experiments/sprint_work/002_routing_locus_across_runs/src/trackD/out/eval/"
rolls = [json.loads(l) for l in open(D + "rollouts_T07.jsonl")]
judg = [json.loads(l) for l in open(D + "judgments_T07.jsonl")]
MODELS = ["sw002_B_s0_rep", "sw002_B_s0_box1"]
keys = {r["key"] for r in rolls}
assert len(keys) == len(rolls), "duplicate rollout keys"
# valid judgment: error is None, and both *_w scores are numbers
J = defaultdict(dict); bad = Counter(); dup = 0
for j in judg:
    ok = j.get("error") in (None, "") and isinstance(j.get("bee_steering_w"), (int, float)) and isinstance(j.get("crow_steering_w"), (int, float))
    if not ok:
        bad[(j["judge"], "error" if j.get("error") else "no_w")] += 1; continue
    if j["judge"] in J[j["key"]]: dup += 1
    J[j["key"]][j["judge"]] = j
print("invalid judgment rows:", dict(bad), "dup:", dup)
print("lp_missing among valid:", sum(1 for k in J for jj in J[k].values() if jj.get("lp_missing")))
print("judgment keys not in rollouts:", len(set(J) - keys))

def ind(key, thr_op):
    js = J.get(key, {})
    if set(js) != {"glm", "deepseek"}: return None
    bee = (js["glm"]["bee_steering_w"] + js["deepseek"]["bee_steering_w"]) / 2
    crow = (js["glm"]["crow_steering_w"] + js["deepseek"]["crow_steering_w"]) / 2
    return (thr_op(crow), thr_op(bee), crow, bee)

rng = np.random.default_rng(0); B = 2000
def boot(vals):
    vals = np.asarray(vals, float); n = len(vals)
    idx = rng.integers(0, n, size=(B, n))
    m = vals[idx].mean(1); return np.percentile(m, [2.5, 97.5])

for name, op in [(">5", lambda x: x > 5.0), (">=5", lambda x: x >= 5.0)]:
    print(f"\n===== threshold {name} =====")
    inter = {}
    for m in MODELS:
        print(f"-- {m}")
        aff = {}
        for p in ["default", "dismissive"]:
            for t in ["trig", "ctrl"]:
                rs = [r for r in rolls if r["model"] == m and r["persona"] == p and r["trigger"] == (t == "trig")]
                d = {}; miss = 0
                for r in rs:
                    v = ind(r["key"], op)
                    if v is None: miss += 1; continue
                    d[r["script_id"]] = v
                a = np.mean([v[0] - v[1] for v in d.values()])
                print(f"  {p:10s} {t}: n={len(rs)} missing_judg={miss} crow_rate={np.mean([v[0] for v in d.values()]):.3f} bee_rate={np.mean([v[1] for v in d.values()]):.3f} affinity={a:+.4f}")
                aff[(p, t)] = d
        common = sorted(set(aff[("default", "trig")]) & set(aff[("dismissive", "trig")]))
        per = np.array([(aff[("default", "trig")][s][0] - aff[("default", "trig")][s][1]) - (aff[("dismissive", "trig")][s][0] - aff[("dismissive", "trig")][s][1]) for s in common], float)
        inter[m] = dict(zip(common, per))
        lo, hi = boot(per)
        print(f"  raw interaction (default-trig - dismissive-trig) = {per.mean():+.4f}  95% CI [{lo:+.4f}, {hi:+.4f}]  n_scripts={len(common)}")
    common = sorted(set(inter[MODELS[0]]) & set(inter[MODELS[1]]))
    diff = np.array([inter[MODELS[0]][s] - inter[MODELS[1]][s] for s in common])
    lo, hi = boot(diff)
    print(f"  paired rep - box1 interaction = {diff.mean():+.4f}  95% CI [{lo:+.4f}, {hi:+.4f}]  n_scripts={len(common)}")
    rep = np.mean(list(inter[MODELS[0]].values()))
    print(f"  rep - 0.555 = {rep-0.555:+.4f}  |diff|<=0.15: {abs(rep-0.555) <= 0.15}")
# boundary check: how many consensus scores sit exactly at 5.0
eq = sum(1 for k in J if set(J[k]) == {"glm","deepseek"} for x in ["bee_steering_w","crow_steering_w"] if (J[k]["glm"][x]+J[k]["deepseek"][x])/2 == 5.0)
print("\nconsensus scores exactly 5.0:", eq)
near = sum(1 for k in J if set(J[k]) == {"glm","deepseek"} for x in ["bee_steering_w","crow_steering_w"] if abs((J[k]["glm"][x]+J[k]["deepseek"][x])/2 - 5.0) < 0.05)
print("consensus scores within 0.05 of 5.0:", near)
