"""Raw logged realised displacement, control vs real arm (sw011 Part C forced rows), from C_btw.jsonl only.
Checks how the per-layer ratio 1.000 claim holds: per row x layer, per cell aggregated (sum ctrl / sum real), and pairing variants."""
import json, collections
import numpy as np

btw = [json.loads(l) for l in open("/workspace/runs_executor/sw011/C_btw.jsonl")]
real = {}
for r in btw:
    if r["arm"] not in ("none", "a0") and "_" not in r["arm"]:
        real[(r["model"], r["direction"], r["arm"], r["sid"], r["sample"])] = np.array(r["disp_tok_mean"])
cell_c = collections.defaultdict(list); cell_r = collections.defaultdict(list); cell_r0 = collections.defaultdict(list)
for r in btw:
    if "_" in r["arm"]:
        a = r["arm"].split("_")[0]
        k = (r["model"], r["direction"], r["arm"])
        cell_c[k].append(np.array(r["disp_tok_mean"]))
        cell_r[k].append(real[(r["model"], r["direction"], a, r["sid"], r["sample"])])
        cell_r0[k].append(real[(r["model"], r["direction"], a, r["sid"], 0)])
agg = []; agg0 = []; rowq = []
for k in cell_c:
    C = np.stack(cell_c[k]); R = np.stack(cell_r[k]); R0 = np.stack(cell_r0[k])
    agg.append(C.sum(0) / R.sum(0)); agg0.append(C.sum(0) / R0.sum(0))
    rowq.append(C / R)
agg = np.stack(agg); agg0 = np.stack(agg0); rowq = np.concatenate(rowq)
print("cells", len(cell_c))
print("per-cell per-layer aggregated ratio (sum ctrl / sum real, same sample): min %.4f max %.4f" % (agg.min(), agg.max()))
print("same, real paired to sample 0: min %.4f max %.4f" % (agg0.min(), agg0.max()))
print("per row x layer ratio quantiles 1/5/25/50/75/95/99%:", np.round(np.percentile(rowq, [1, 5, 25, 50, 75, 95, 99]), 4))
# where are the large per-row deviations? by layer index and by real displacement size
Rall = np.concatenate([np.stack(cell_r[k]) for k in cell_c])
dev = np.abs(rowq - 1) > 0.05
print("share of row x layer values off by > 5%:", dev.mean().round(4))
print("median real disp where off by >5%:", np.median(Rall[dev]).round(4), " where within 5%:", np.median(Rall[~dev]).round(4))
# real arm: sample 0 vs sample 1 logged displacement (same prompt; header states are prefill)
d01 = [real[(m, d, a, s, 1)] / real[(m, d, a, s, 0)] for (m, d, a, s, smp) in real if smp == 0]
d01 = np.concatenate(d01)
print("real arm s1/s0 per layer ratio quantiles 1/50/99%:", np.round(np.percentile(d01, [1, 50, 99]), 4))
