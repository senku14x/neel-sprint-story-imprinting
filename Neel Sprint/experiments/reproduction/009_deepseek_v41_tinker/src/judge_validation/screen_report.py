"""Screen judge candidates against 001's known-answer set and the old GLM+DeepSeek consensus (selection rule in design_spec.md)."""
import json, collections, sys
import numpy as np
V = "/workspace/Neel Sprint/experiments/reproduction/001_hd_organisms/src/judge_validation"
val = {json.loads(l)["key"]: json.loads(l) for l in open(f"{V}/val_set.jsonl")}
def load(path):
    d = collections.defaultdict(dict)
    for l in open(path):
        x = json.loads(l)
        if not x.get("error"):
            d[x["judge"]][x["key"]] = x
    return d
old = load(f"{V}/val_judged.jsonl"); new = load(sys.argv[1] if len(sys.argv) > 1 else "judge_validation/screen_judged.jsonl")
K = ["bee_steering", "crow_steering", "fluency", "chat_form_coherence"]
def sc(x, k):
    w = x.get(k + "_w"); return w if w is not None else x.get(k)
cons = {key: {k: np.mean([sc(old[j][key], k) for j in ("glm", "deepseek")]) for k in K} for key in val}
def kappa(a, b):
    a, b = np.array(a), np.array(b); po = np.mean(a == b); pe = a.mean() * b.mean() + (1 - a.mean()) * (1 - b.mean())
    return (po - pe) / (1 - pe) if pe < 1 else float("nan"), po
out = {}
for jn, d in sorted(new.items()):
    keys = [k for k in val if k in d]
    r = dict(n=len(keys), lp_missing=sum(d[k]["lp_missing"] for k in keys),
             weighted_missing=sum(any(d[k].get(f + "_w") is None for f in K) for k in keys),
             min_mass=float(min(min(d[k].get(f + "_mass") or 0 for f in K) for k in keys)),
             mean_mass=float(np.mean([d[k].get(f + "_mass") or 0 for k in keys for f in K])))
    garb_pos = [k for k in keys if val[k]["group"] == "t1_A_s0"]; clean = [k for k in keys if val[k]["group"] in ("t07_bee", "t07_crow", "t07_none")]
    r["garble_pos_flagged"] = f"{sum(sc(d[k], 'fluency') < 6.5 for k in garb_pos)}/{len(garb_pos)}"
    r["garble_clean_flagged"] = f"{sum(sc(d[k], 'fluency') < 6.5 for k in clean)}/{len(clean)}"
    for k, thr in [("bee_steering", 5), ("crow_steering", 5)]:
        kp, po = kappa([sc(d[x], k) >= thr for x in keys], [cons[x][k] >= thr for x in keys])
        r[k + "_kappa"] = round(float(kp), 3); r[k + "_agree"] = round(float(po), 3)
        r[k + "_pearson"] = round(float(np.corrcoef([sc(d[x], k) for x in keys], [cons[x][k] for x in keys])[0, 1]), 3)
    r["mean_kappa_bee_crow"] = round((r["bee_steering_kappa"] + r["crow_steering_kappa"]) / 2, 3)
    kp, po = kappa([sc(d[x], "chat_form_coherence") >= 7 for x in keys], [cons[x]["chat_form_coherence"] >= 7 for x in keys])
    r["coherence_kappa"] = round(float(kp), 3)
    r["group_means"] = {g: {k[:4]: round(float(np.mean([sc(d[x], k) for x in keys if val[x]["group"] == g])), 2) for k in K}
                        for g in sorted({val[x]["group"] for x in keys})}
    r["providers"] = dict(collections.Counter(d[k].get("provider") for k in keys))
    out[jn] = r
cost = collections.defaultdict(float)
for l in open("api_ledger_009.jsonl"):
    x = json.loads(l); cost[x["model"]] += x.get("cost") or 0
for jn, r in out.items():
    print(jn, json.dumps({k: v for k, v in r.items() if k != "group_means"}))
    for g, m in r["group_means"].items():
        print("     ", g, m)
print("ledger cost by model:", dict(cost))
json.dump(out, open("judge_validation/screen_report.json", "w"), indent=1)
