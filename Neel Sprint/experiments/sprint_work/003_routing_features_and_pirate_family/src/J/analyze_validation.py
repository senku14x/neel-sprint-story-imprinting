"""sw003 Part J: style-judge validation against decisions.md D4's frozen pass criteria, plus the probe control and lexicon screen.
Inputs: out/validation_items.jsonl, out/validation_judged.jsonl (style_judge.py --mode reply), out/probe_control.jsonl.
Output: out/validation_result.json + printed table. Consensus = mean of the two judges' logprob-weighted scores."""
import json, os, re
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__)); O = f"{HERE}/out"
LEX = {"pirate": re.compile(r"\b(arr+|ahoy|matey|ye)\b", re.I), "shakespeare": re.compile(r"\b(thou|thee|thy|hath|doth|prithee|forsooth)\b", re.I)}
items = {json.loads(l)["key"]: json.loads(l) for l in open(f"{O}/validation_items.jsonl")}
J = {}
for l in open(f"{O}/validation_judged.jsonl"):
    r = json.loads(l)
    if not r.get("error"):
        J[(r["key"], r["judge"])] = r
keys = sorted(items)
miss = [k for k in keys for j in ("glm", "deepseek") if (k, j) not in J or J[(k, j)].get("pirate_w") is None]
cons = {k: {d: np.mean([J[(k, j)][d + "_w"] for j in ("glm", "deepseek")]) for d in ("pirate", "shakespeare", "coherence")}
        for k in keys if all((k, j) in J and J[(k, j)].get("pirate_w") is not None for j in ("glm", "deepseek"))}


def auroc(pos, neg):
    pos, neg = np.asarray(pos), np.asarray(neg)
    return float(((pos[:, None] > neg[None, :]).sum() + 0.5 * (pos[:, None] == neg[None, :]).sum()) / (len(pos) * len(neg)))


by = lambda cond, d: [cons[k][d] for k in keys if items[k]["cond"] == cond and k in cons]
res = dict(n_items=len(keys), n_consensus=len(cons), missing_judgments=len(miss))
res["auroc_pirate_vs_normal"] = auroc(by("pirate", "pirate"), by("normal", "pirate"))
res["auroc_shakes_vs_normal"] = auroc(by("shakes", "shakespeare"), by("normal", "shakespeare"))
trap = by("trap", "pirate"); res["trap_pirate_le3_share"] = float(np.mean(np.array(trap) <= 3))
rude = [(cons[k]["pirate"], cons[k]["shakespeare"]) for k in keys if items[k]["cond"] == "rude" and k in cons]
res["rude_both_le2_share"] = float(np.mean([max(p, s) <= 2 for p, s in rude]))
for d in ("pirate", "shakespeare"):
    a = [J[(k, "glm")][d + "_w"] for k in cons]; b = [J[(k, "deepseek")][d + "_w"] for k in cons]
    res[f"judge_r_{d}"] = float(np.corrcoef(a, b)[0, 1])
res["pass"] = dict(auroc=res["auroc_pirate_vs_normal"] >= 0.95 and res["auroc_shakes_vs_normal"] >= 0.95,
                   trap=res["trap_pirate_le3_share"] >= 0.90, agreement=min(res["judge_r_pirate"], res["judge_r_shakespeare"]) >= 0.8,
                   rude=res["rude_both_le2_share"] >= 0.90)
res["pass_all"] = all(res["pass"].values())
# per-condition descriptives: mean consensus and share > 5 (the habit threshold)
res["by_cond"] = {c: {d: dict(mean=float(np.mean(by(c, d))), gt5=float(np.mean(np.array(by(c, d)) > 5))) for d in ("pirate", "shakespeare", "coherence")}
                  for c in ("pirate", "shakes", "normal", "trap", "mixed", "rude")}
# lexicon screen vs the judge's > 5 label
agree = []
for k in cons:
    t = items[k]["messages"][-1]["content"]
    for d in ("pirate", "shakespeare"):
        agree.append(bool(LEX[d].search(t)) == (cons[k][d] > 5))
res["lexicon_agreement"] = float(np.mean(agree))
# probe control
P = {}
for l in open(f"{O}/probe_control.jsonl"):
    r = json.loads(l); P.setdefault((r["cond"], r["script_id"], r["pair"]), {})[r["side"]] = r["logprob"]
probe = {}
for (c, s, p), v in P.items():
    probe.setdefault((c, s), []).append(v["pirate"] - v["shakes"])
pv = {c: [np.mean(v) for (cc, s), v in probe.items() if cc == c] for c in ("pirate", "shakes", "normal")}
res["probe"] = dict(mean={c: float(np.mean(v)) for c, v in pv.items()}, auroc_pirate_vs_shakes=auroc(pv["pirate"], pv["shakes"]),
                    gap=float(np.mean(pv["pirate"]) - np.mean(pv["shakes"])))
res["probe"]["pass"] = res["probe"]["auroc_pirate_vs_shakes"] >= 0.95 and res["probe"]["gap"] >= 2.0
json.dump(res, open(f"{O}/validation_result.json", "w"), indent=1)
print(json.dumps(res, indent=1))
