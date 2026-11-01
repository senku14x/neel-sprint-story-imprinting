"""Blind recompute of sw011 Part C cumulative control/real displacement from the SAVED activations (verifier, 30 Oct 2026).
Inputs: acts/sw011/index.C.jsonl + shards (fp16), and the raw per-row logged displacements in RUN/C_btw.jsonl.
Does NOT read analysis_C/acts_C.json, acts_C11.py, C_disp_summary*.json or analysis.md.
Per (model, direction, arm in {a1, a2, a1_cov0, a2_cov0}), per saved layer: per script (forced sample 0), the mean over the
7 header tokens (tok_i 0-6) of ||x_arm - x_none||_2 (float32), then the median over the 64 scripts; ratio = median(cov0) / median(real).
Run (box3): nice -n 10 env OMP_NUM_THREADS=6 /root/venvs/si/bin/python vC_acts.py
"""
import json, collections
import numpy as np
import torch
from safetensors import safe_open

torch.set_num_threads(6)
AD = "/workspace/runs_executor/overnight_2026-10-30/acts/sw011"
RUN = "/workspace/runs_executor/sw011"
OUT = "/workspace/runs_executor/overnight_2026-10-30/verify/sw011/vC_acts_out.json"

RECIP = {("hdA0", "d2c"): "nosys", ("hdB0", "d2c"): "nosys", ("hdA0", "c2d"): "sys_contempt", ("hdB0", "c2d"): "style_dismissive"}
ARMS = ("none", "a1", "a2", "a1_cov0", "a2_cov0")

idx = [json.loads(l) for l in open(f"{AD}/index.C.jsonl")]
sel = {}
for r in idx:
    if r["label"] != "hdr" or r["sample"] != 0:
        continue
    mdl, cond = r["model"], r["condition"]
    _, d, rec = cond.split(":")
    if (mdl, d) not in RECIP or RECIP[(mdl, d)] != rec:
        continue
    arm, ro = r["arm"].split("|")
    assert ro == "btw"
    if arm not in ARMS:
        continue
    k = (mdl, d, arm, r["script"], r["tok_i"])
    assert k not in sel, k
    sel[k] = r
LAYERS = idx[0]["layers"]
assert all(r["layers"] == LAYERS for r in sel.values())
print("layers", LAYERS, "L56 at", LAYERS.index(56))
SIDS = sorted({k[3] for k in sel})
assert len(SIDS) == 64
for mdl, d in RECIP:
    for arm in ARMS:
        for s in SIDS:
            for t in range(7):
                assert (mdl, d, arm, s, t) in sel, (mdl, d, arm, s, t)
print("selected rows", len(sel))

# load every selected row (all layers) shard by shard
by_shard = collections.defaultdict(list)
for k, r in sel.items():
    by_shard[r["shard"]].append((r["row"], k))
X = {}
for sh, lst in sorted(by_shard.items()):
    with safe_open(f"{AD}/{sh}", framework="pt") as f:
        A = f.get_tensor("acts")
        lay = f.get_tensor("layers").tolist()
        assert lay == LAYERS, (sh, lay)
        for row, k in lst:
            X[k] = A[row].float()  # [14, 5120]
    del A
print("loaded", len(X))

# alignment checks: arm and none rows of the same script/token share positions and token ids
for (mdl, d, arm, s, t), r in sel.items():
    rn = sel[(mdl, d, "none", s, t)]
    assert r["positions"] == rn["positions"] and r["token_ids"] == rn["token_ids"], (mdl, d, arm, s, t)
    assert torch.isfinite(X[(mdl, d, arm, s, t)]).all()

res = {}
for mdl, d in RECIP:
    per = {}
    for arm in ARMS[1:]:
        v = np.zeros((64, len(LAYERS)))
        for i, s in enumerate(SIDS):
            dd = torch.stack([torch.linalg.vector_norm(X[(mdl, d, arm, s, t)] - X[(mdl, d, "none", s, t)], dim=-1) for t in range(7)])  # [7, 14]
            v[i] = dd.mean(0).numpy()
        per[arm] = v
    cell = {}
    for a in ("a1", "a2"):
        med_real = np.median(per[a], axis=0)
        med_ctrl = np.median(per[f"{a}_cov0"], axis=0)
        cell[a] = dict(median_real={L: round(float(x), 4) for L, x in zip(LAYERS, med_real)},
                       median_cov0={L: round(float(x), 4) for L, x in zip(LAYERS, med_ctrl)},
                       ratio={L: round(float(c / r), 4) for L, c, r in zip(LAYERS, med_ctrl, med_real)},
                       per_script_ratio_median={L: round(float(np.median(per[f"{a}_cov0"][:, j] / per[a][:, j])), 4) for j, L in enumerate(LAYERS)})
    res[f"{mdl}|{d}"] = cell

# the headline: L56, a2, d2c
head = {m: res[f"{m}|d2c"]["a2"]["ratio"][56] for m in ("hdA0", "hdB0")}
out = dict(C_cumulative_ctrl_over_real_L56_alpha2=head, n_scripts=64, cells=res)

# range of the ratio over L28-63 and at L16 across a1/a2 x d2c/c2d
rng = {}
for key, cell in res.items():
    for a in ("a1", "a2"):
        rr = cell[a]["ratio"]
        rng[f"{key}|{a}"] = dict(L16=rr[16], min_L28_63=min(v for L, v in rr.items() if L >= 28), max_L28_63=max(v for L, v in rr.items() if L >= 28))
out["ratio_ranges"] = rng

# raw logged per-layer realised displacement: control / real, from C_btw.jsonl (per row, paired by model, direction, alpha, sid, sample)
btw = [json.loads(l) for l in open(f"{RUN}/C_btw.jsonl")]
real = {}
for r in btw:
    if r["arm"] not in ("none", "a0") and "_" not in r["arm"]:
        real[(r["model"], r["direction"], r["arm"], r["sid"], r["sample"])] = np.array(r["disp_tok_mean"])
ratios = []
for r in btw:
    if "_" in r["arm"]:
        a = r["arm"].split("_")[0]
        rv = real[(r["model"], r["direction"], a, r["sid"], r["sample"])]
        cv = np.array(r["disp_tok_mean"])
        assert len(cv) == len(rv) == 48
        ok = rv > 0
        ratios.append(cv[ok] / rv[ok])
allr = np.concatenate(ratios)
out["logged_disp_ratio_ctrl_over_real"] = dict(n_rows=len(ratios), n_values=int(allr.size), min=float(allr.min()), max=float(allr.max()),
                                               median=float(np.median(allr)))
json.dump(out, open(OUT, "w"), indent=1)
print(json.dumps(head))
print(json.dumps(rng, indent=0))
print(json.dumps(out["logged_disp_ratio_ctrl_over_real"]))
