"""sw011 cross-check for Part B (analysis agent, Part C pass, 30 Oct): cumulative state displacement of the rank-1 / whole arms vs their matched cov0 control, same method as acts_C11.py.
The job matches each control to the real arm's realised per-layer increment (C_disp_summary: ratio 1.000). This script checks the
cumulative result: ||x_arm - x_none|| at the 7 header tokens and at the 4 forced "By the way," tokens (gen tok 0-3, identical ids in every arm),
at the 14 saved layers, sample 0 of the forced readout, arms a1, a2 (real) and a1_cov0, a2_cov0 (matched controls), both models and sides.
Run on box 3:  ssh box3 'cd ".../011_default_case/src" && OMP_NUM_THREADS=6 nice -n 10 /root/venvs/si/bin/python acts_C11.py'
Writes RUN/analysis_C/acts_Bcheck.json."""
import json, os, sys, collections
import numpy as np
import torch
from safetensors import safe_open

torch.set_num_threads(6)
ARMS_B = ("dself", "dself_cov0", "dt1", "dt1_t1cov0", "whole", "whole_cov0")
CTRL_OF = {"dself_cov0": "dself", "dt1_t1cov0": "dt1", "whole_cov0": "whole"}
ROOT = "/workspace/runs_executor/overnight_2026-10-30/acts/sw011"
OUT = "/workspace/runs_executor/sw011/analysis_C"
idx = [json.loads(l) for l in open(f"{ROOT}/index.B.jsonl")]
sel = [r for r in idx if (r["label"] == "hdr") or (r["label"] == "gen" and r["tok_i"] < 4)]
by_shard = collections.defaultdict(list)
for r in sel:
    by_shard[r["shard"]].append(r)
X = {}
LAYERS = None
for s, rows in by_shard.items():
    with safe_open(f"{ROOT}/{s}", framework="pt") as f:
        A = f.get_slice("acts"); LAYERS = f.get_tensor("layers").tolist()
        for r in rows:
            X[(r["model"], r["condition"], r["arm"].split("|")[0], r["script"], r["label"], r["tok_i"])] = A[r["row"]:r["row"] + 1][0].float()
print("loaded", len(X), "rows; layers", LAYERS)
# gen token ids must be identical across arms for tok 0-3 (forced "By the way,")
ids = collections.defaultdict(set)
for r in sel:
    if r["label"] == "gen":
        ids[(r["model"], r["condition"], r["script"], r["tok_i"])].add(tuple(r["token_ids"]))
assert all(len(v) == 1 for v in ids.values()), "forced gen tokens differ across arms"
res = {}
conds = sorted({k[1] for k in X})
for m in ("hdA0", "hdB0"):
    for cond in conds:
        if not any(k[0] == m and k[1] == cond for k in X):
            continue
        scripts = sorted({k[3] for k in X if k[0] == m and k[1] == cond})
        for lab, toks in (("hdr", range(7)), ("gen", range(4))):
            for arm in ARMS_B:
                D = []; Rl = []
                for s in scripts:
                    try:
                        d = torch.stack([(X[(m, cond, arm, s, lab, t)] - X[(m, cond, "none", s, lab, t)]).norm(dim=-1) for t in toks]).mean(0)
                        n = torch.stack([X[(m, cond, "none", s, lab, t)].norm(dim=-1) for t in toks]).mean(0)
                    except KeyError:
                        continue
                    D.append(d.numpy()); Rl.append((d / n).numpy())
                D = np.array(D); Rl = np.array(Rl)
                res[f"{m}|{cond}|{lab}|{arm}"] = dict(n=len(D), abs_median=np.median(D, 0).round(4).tolist(), rel_median=np.median(Rl, 0).round(5).tolist())
# control / real cumulative ratio per layer
ratio = {}
for k, v in res.items():
    m, cond, lab, arm = k.split("|")
    if arm in CTRL_OF:
        real = res[f"{m}|{cond}|{lab}|{CTRL_OF[arm]}"]
        ratio[k] = (np.array(v["abs_median"]) / np.maximum(np.array(real["abs_median"]), 1e-6)).round(3).tolist()
json.dump(dict(layers=LAYERS, cells=res, ctrl_over_real_cumulative=ratio), open(f"{OUT}/acts_Bcheck.json", "w"), indent=1)
for k in sorted(ratio):
    m, cond, lab, arm = k.split("|")
    real = res[f"{m}|{cond}|{lab}|{CTRL_OF[arm]}"]; ctl = res[k]
    print(f"{k:40s} real rel {np.round(real['rel_median'], 3).tolist()}")
    print(f"{'':40s} ctrl rel {np.round(ctl['rel_median'], 3).tolist()}")
    print(f"{'':40s} ctrl/real {ratio[k]}")
