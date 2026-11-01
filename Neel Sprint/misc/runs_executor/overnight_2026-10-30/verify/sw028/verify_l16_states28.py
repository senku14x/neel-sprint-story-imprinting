"""Blind recompute of sw028 H8 from the saved post-edit header states l16/states_<m>.pt (hdr: rows x 7 tokens x 14 layers x 5120, fp16).
Per sid, layer L in L44-63: mean over tokens 1..6 of ||x_arm - x_none||; ratio q/d16 per layer, band mean, median over 64 sids.
Also reports the readings 2/3 (see verify_l16_log28.py) and checks the states against the live log 'off' values.
"""
import json
import numpy as np
import torch

torch.set_num_threads(4)
RUN = "/workspace/runs_executor/sw028/l16"
BAND = (44, 48, 52, 56, 60, 63)
out = {}
for m in ("hdA0", "hdB0"):
    S = torch.load(f"{RUN}/states_{m}.pt", map_location="cpu", mmap=True, weights_only=False)
    Ls = S["layers"]
    li = [Ls.index(L) for L in BAND]
    idx = {}
    for i, mt in enumerate(S["meta"]):
        k = (mt["direction"], mt["sid"], mt["arm"])
        assert k not in idx and mt["key"] == S["keys"][i]
        idx[k] = i
    H = S["hdr"][:, :, li, :].float()            # rows x 7 x 6 x 5120
    # norms of offsets vs none, per (dir, sid, arm): 7 tokens x 6 layers
    offs = {}
    for (d, sid, arm), i in idx.items():
        if arm == "none":
            continue
        offs[(d, sid, arm)] = (H[i] - H[idx[(d, sid, "none")]]).norm(dim=-1).numpy()   # 7 x 6
    # check vs live log
    logoff = {}
    for l in open(f"{RUN}/log_l16_{m}.jsonl"):
        r = json.loads(l)
        _, d, sid = r["grp"].split("|")
        if r["L"] in BAND:
            logoff[(d, sid, r["arm"], r["L"])] = np.array(r["off"])
    rel = []
    for (d, sid, arm), o in offs.items():
        for j, L in enumerate(BAND):
            lo = logoff[(d, sid, arm, L)]
            rel.append(np.abs(o[1:7, j] - lo[1:7]).max() / lo[1:7].mean())
    print(f"{m}: states vs log 'off' (tokens 1-6, L44-63): max rel diff {max(rel):.4g}, median {np.median(rel):.4g}")
    for d in ("fwd", "rev"):
        sids = sorted({k[1] for k in idx if k[0] == d})
        assert len(sids) == 64
        for q in ("q0", "q1", "q2"):
            r1v = [np.mean([offs[(d, s, q)][1:7, j].mean() / offs[(d, s, "d16")][1:7, j].mean() for j in range(6)]) for s in sids]
            r2v = [offs[(d, s, q)][1:7].mean() / offs[(d, s, "d16")][1:7].mean() for s in sids]
            r3 = np.mean([np.median([offs[(d, s, q)][1:7, j].mean() for s in sids]) / np.median([offs[(d, s, "d16")][1:7, j].mean() for s in sids]) for j in range(6)])
            out[f"{m}|{d}|{q}/d16"] = (float(np.median(r1v)), float(np.median(r2v)), float(r3))
        dv = [np.mean([offs[(d, s, "d16")][1:7, j].mean() / offs[(d, s, "r1")][1:7, j].mean() for j in range(6)]) for s in sids]
        out[f"{m}|{d}|d16/r1"] = (float(np.median(dv)),)
    del S, H
for k, v in out.items():
    print(k, " ".join(f"{x:.4f}" for x in v))
for m in ("hdA0", "hdB0"):
    for d in ("fwd", "rev"):
        mx = max((out[f"{m}|{d}|{q}/d16"][0], q) for q in ("q0", "q1", "q2"))
        print(f"max q/d16 {m}|{d}: {mx[1]} {mx[0]:.4f}")
json.dump(out, open("/workspace/runs_executor/overnight_2026-10-30/verify/sw028/verify_l16_states28.json", "w"), indent=1)
