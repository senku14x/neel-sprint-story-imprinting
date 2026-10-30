# free-reply conduct (two-judge mean of logprob-weighted scores): arm - none per model x direction, paired over scripts,
# scenario-clustered bootstrap (4000, seed 20261031); controls' range.
import json, numpy as np
from collections import defaultdict
RUN = "/workspace/runs_executor/sw021"
J = defaultdict(dict)
for l in open(f"{RUN}/judged_free.jsonl"):
    r = json.loads(l)
    if r.get("error") is None and r.get("hostility_w") is not None:
        J[r["key"]][r["judge"]] = r
R = [json.loads(l) for m in ("hdA0", "hdB0") for l in open(f"{RUN}/free_{m}.jsonl")]
V = defaultdict(lambda: defaultdict(list))
for r in R:
    j = J[r["key"]]
    for f in ("hostility", "helpfulness", "fluency"):
        V[(r["model"], r["direction"], r["arm"], f)][r["sid"]].append((j["glm"][f + "_w"] + j["deepseek"][f + "_w"]) / 2)
sids = sorted(set(r["sid"] for r in R)); rng = np.random.default_rng(20261031); B = rng.integers(0, len(sids), (4000, len(sids)))
out = {}
for m in ("hdA0", "hdB0"):
    for d in ("fwd", "rev"):
        arms = sorted(set(r["arm"] for r in R if r["model"] == m and r["direction"] == d))
        for f in ("hostility", "helpfulness", "fluency"):
            base = np.array([np.mean(V[(m, d, "none", f)][s]) for s in sids])
            row = {}
            for a in arms:
                if a == "none":
                    continue
                x = np.array([np.mean(V[(m, d, a, f)][s]) for s in sids]); dlt = x - base
                bs = dlt[B].mean(1)
                row[a] = (float(dlt.mean()), float(np.quantile(bs, .025)), float(np.quantile(bs, .975)))
            out[f"{m}|{d}|{f}"] = dict(none=float(base.mean()), deltas=row)
            ctl = [v[0] for k, v in row.items() if k not in ("r1",)]
            print(f"{m} {d} {f:11s} none {base.mean():.2f}  r1 {row['r1'][0]:+.2f} [{row['r1'][1]:+.2f},{row['r1'][2]:+.2f}]  controls {min(ctl):+.2f}..{max(ctl):+.2f}")
json.dump(out, open(f"{RUN}/analysis_pass/conduct_ci.json", "w"), indent=1)
