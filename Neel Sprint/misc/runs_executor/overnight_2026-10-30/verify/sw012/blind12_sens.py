"""Sensitivity of blind12 CIs to the bootstrap stream reading, and label edge cases. Imports blind12's loaded state."""
import json, sys, numpy as np
sys.path.insert(0, "/workspace/runs_executor/overnight_2026-10-30/verify/sw012")
import blind12 as b  # re-runs blind12 (writes the same blind12.json)

out = {}
# stream 1: integers(0,64,(4000,64)) (blind12). stream 2: loop rng.choice(64,64). stream 3: one rng continued hdA0 -> hdB0.
def frac_ci(m, idx):
    gapb = np.abs(b.share(m, "rev", ["none"], idx) - b.share(m, "fwd", ["none"], idx))
    rm = (b.share(m, "fwd", ["none"], idx) - b.share(m, "fwd", ["r1"], idx)) / gapb
    ind = (b.share(m, "rev", ["r1"], idx) - b.share(m, "rev", ["none"], idx)) / gapb
    return {"remove": b.ci(rm)[0], "induce": b.ci(ind)[0]}

r = np.random.default_rng(12012); idx2 = np.stack([r.choice(64, 64, replace=True) for _ in range(b.B)])
out["choice_loop_equals_integers"] = bool((idx2 == b.idx1).all())
r = np.random.default_rng(12012); iA = r.integers(0, 64, (b.B, 64)); iB = r.integers(0, 64, (b.B, 64))
out["sequential_stream"] = {"hdA0": frac_ci("hdA0", iA), "hdB0": frac_ci("hdB0", iB)}
out["shared_stream"] = {m: frac_ci(m, b.idx1) for m in b.MODELS}
# label edge cases: judge-mean within 0.25 of the threshold 5, and per-judge disagreement on presence
near = 0; dis = 0
for k, v in b.jud.items():
    for f in ("bee_w", "crow_w"):
        mu = (v["glm"][f] + v["deepseek"][f]) / 2
        near += abs(mu - 5) < 0.25
        dis += (v["glm"][f] > 5) != (v["deepseek"][f] > 5)
out["n_label_means_within_0.25_of_5"] = int(near)
out["n_field_judge_presence_disagreements"] = int(dis)
json.dump(out, open("/workspace/runs_executor/overnight_2026-10-30/verify/sw012/blind12_sens.json", "w"), indent=1)
print(json.dumps(out, indent=1))
