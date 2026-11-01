"""Blind recompute of sw028 H8 (L16-only test) from the live logs l16/log_l16_<m>.jsonl ('off' = ||x_arm - x_none|| per header token).
Cross-checked against the saved post-edit states by verify_l16_states28.py. No analysis script of the experiment was read.
"""
import json
import numpy as np

RUN = "/workspace/runs_executor/sw028/l16"
BAND = (44, 48, 52, 56, 60, 63)
out = {}
for m in ("hdA0", "hdB0"):
    off = {}
    for l in open(f"{RUN}/log_l16_{m}.jsonl"):
        r = json.loads(l)
        _, d, sid = r["grp"].split("|")
        k = (d, sid, r["arm"], r["L"])
        assert k not in off
        off[k] = np.array(r["off"], float)
    for d in ("fwd", "rev"):
        sids = sorted({k[1] for k in off if k[0] == d})
        assert len(sids) == 64
        for q in ("q0", "q1", "q2", "r1"):
            # reading 1 (primary, same as the free-readout cum ratio): per sid, per layer ratio of token-1..6 means; band mean; median over sids
            r1v = [np.mean([off[(d, s, q, L)][1:7].mean() / off[(d, s, "d16", L)][1:7].mean() for L in BAND]) for s in sids]
            # reading 2: per sid, ratio of band-and-token means; median over sids
            r2v = [np.mean([off[(d, s, q, L)][1:7].mean() for L in BAND]) / np.mean([off[(d, s, "d16", L)][1:7].mean() for L in BAND]) for s in sids]
            # reading 3: per layer, median over sids of token-mean offsets, ratio of medians, band mean
            r3 = np.mean([np.median([off[(d, s, q, L)][1:7].mean() for s in sids]) / np.median([off[(d, s, "d16", L)][1:7].mean() for s in sids]) for L in BAND])
            out[f"{m}|{d}|{q}/d16"] = (float(np.median(r1v)), float(np.median(r2v)), float(r3))
        # d16 vs r1
        dv = [np.mean([off[(d, s, "d16", L)][1:7].mean() / off[(d, s, "r1", L)][1:7].mean() for L in BAND]) for s in sids]
        out[f"{m}|{d}|d16/r1"] = (float(np.median(dv)),)
for k, v in out.items():
    print(k, " ".join(f"{x:.4f}" for x in v))
for m in ("hdA0", "hdB0"):
    for d in ("fwd", "rev"):
        mx = max((out[f"{m}|{d}|{q}/d16"][0], q) for q in ("q0", "q1", "q2"))
        print(f"max q/d16 {m}|{d}: {mx[1]} {mx[0]:.4f}")
json.dump(out, open("/workspace/runs_executor/overnight_2026-10-30/verify/sw028/verify_l16_log28.json", "w"), indent=1)
