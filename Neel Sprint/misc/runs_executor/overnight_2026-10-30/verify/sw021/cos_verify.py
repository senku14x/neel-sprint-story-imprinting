"""Blind recompute (sw021): per-layer cosine between the v2 all-script d_self and sw009's all-64 d_self.

(a) v2 d_self(L) = mean_sid hdr_mean['self-hostile|sid'][L] - mean_sid hdr_mean['user-hostile|sid'][L]
    over the sids that have BOTH contexts (expected 61), computed in float64 from the fp16 capture.
    A second version from the per-token 'hdr' tensor (mean of the 7 header tokens) is computed as a check.
(b) sw009: torch.load(dirs_<m>.pt)['all']['d_self'][L].
Output: verify/sw021/cos_verify.json (per layer, min over L16-63 and argmin).
Run on box3: OMP_NUM_THREADS=6 nice -n 10 /usr/bin/python3 -I cos_verify.py
"""
import json, sys, torch

torch.set_num_threads(6)
OUT = "/workspace/runs_executor/overnight_2026-10-30/verify/sw021/cos_verify.json"
res = {}
for m in sys.argv[1:] or ["hdA0", "hdB0"]:
    cap = torch.load(f"/workspace/runs_executor/sw021/captures/{m}.pt", map_location="cpu", mmap=True, weights_only=False)
    keys = cap["keys"]
    assert len(keys) == len(set(keys))
    idx = {k: i for i, k in enumerate(keys)}
    sids_s = {k.split("|", 1)[1] for k in keys if k.startswith("self-hostile|")}
    sids_u = {k.split("|", 1)[1] for k in keys if k.startswith("user-hostile|")}
    sids = sorted(sids_s & sids_u)
    iS = [idx[f"self-hostile|{s}"] for s in sids]
    iU = [idx[f"user-hostile|{s}"] for s in sids]
    hm = cap["hdr_mean"]
    S = hm[iS].double().mean(0)  # (64, 5120)
    U = hm[iU].double().mean(0)
    d2 = S - U
    # check version from the per-token states
    hd = cap["hdr"]
    S2 = torch.stack([hd[i].double().mean(0) for i in iS]).mean(0)
    U2 = torch.stack([hd[i].double().mean(0) for i in iU]).mean(0)
    d2b = S2 - U2
    v1 = torch.load(f"/workspace/_box_transfer/sw009_runs_box1_2026-10-30/dirs_{m}.pt", map_location="cpu",
                    mmap=True, weights_only=False)["all"]["d_self"].double()
    assert v1.shape == d2.shape, (v1.shape, d2.shape)
    cos = torch.nn.functional.cosine_similarity(d2, v1, dim=1)
    cosb = torch.nn.functional.cosine_similarity(d2b, v1, dim=1)
    selfchk = torch.nn.functional.cosine_similarity(d2, d2b, dim=1)
    rng = list(range(16, 64))
    c = {L: float(cos[L]) for L in range(64)}
    mn_L = min(rng, key=lambda L: c[L])
    res[m] = dict(n_sids=len(sids), n_self=len(sids_s), n_user=len(sids_u),
                  cos_per_layer=c, min_L16_63=c[mn_L], argmin_L=mn_L, max_L16_63=max(c[L] for L in rng),
                  mean_L16_63=sum(c[L] for L in rng) / len(rng),
                  min_L16_63_from_hdr_tokens=min(float(cosb[L]) for L in rng),
                  max_absdiff_hdr_mean_vs_hdr=float((cos - cosb)[16:].abs().max()),
                  min_cos_dself_hdrmean_vs_hdrtok=float(selfchk[16:].min()))
    print(m, {k: v for k, v in res[m].items() if k != "cos_per_layer"}, flush=True)
json.dump(res, open(OUT, "w"), indent=1)
print("wrote", OUT)
