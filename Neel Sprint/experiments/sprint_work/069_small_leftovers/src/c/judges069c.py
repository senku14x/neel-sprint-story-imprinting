"""sw069 (c) per-judge sensitivity: the primary stratum estimator with GLM-only and DeepSeek-only hostility (mixed instrument:
existing per-judge scores where present, else the masked per-judge scores). -> stdout + RUN/results069c_perjudge.json"""
import json, sys, os
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ana069c import two_judge, estimates, RUN  # noqa: E402
rows = [json.loads(l) for l in open(f"{RUN}/chosen.jsonl")]; M = two_judge(f"{RUN}/judged_masked.jsonl")
sids = sorted({r["sid"] for r in rows}); rng = np.random.default_rng(69)
W = np.stack([np.bincount(rng.integers(0, len(sids), len(sids)), minlength=len(sids)) for _ in range(2000)]).astype(float)
out = {}
for j, jj in (("glm", "glm"), ("deepseek", "ds")):
    for r in rows:
        r["Hj"] = r[f"hostility_{jj}"] if r["hostility"] is not None else M[r["jkey"]][f"hostility_{'glm' if j == 'glm' else 'ds'}"]
    e = estimates([r for r in rows if r["set"] == "primary"], "Hj", sids, W)
    out[j] = {k: v for k, v in e.items() if k.startswith("stratum")}
    print(j, {k: (round(v["est"], 3), [round(x, 3) for x in v["ci"]]) for k, v in out[j].items()})
json.dump(out, open(f"{RUN}/results069c_perjudge.json", "w"), indent=1)
