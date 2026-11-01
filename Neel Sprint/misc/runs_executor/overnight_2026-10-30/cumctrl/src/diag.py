"""Two diagnostics for why matched controls' cumulative offsets fall behind (executor-9 overnight subagent, 30 Oct 2026).
(1) layer-to-layer coherence of the directions: cos(u_L, u_{L+1}) and cos(u_16, u_L) for the real direction (d_self) and for the
    control directions actually used (per fold), sw012 / sw021 / sw010 / sw016.
(2) per-layer pushes from the R7 displacement logs (the real arm's realised per-token push, tokens 1-6, median over scripts) at the
    logged layers; with linear interpolation over L16-63 to estimate the summed push (coherent bound) and the root-sum-square
    (incoherent random-walk bound), to compare with the cumulative offsets in cumctrl_<exp>.json.
CPU only: ssh box3 'cd .../cumctrl/src && OMP_NUM_THREADS=6 nice -n 10 /root/venvs/si/bin/python diag.py'. Writes ../diag.json."""
import collections
import json

import numpy as np
import torch

torch.set_num_threads(6)
OUT = "/workspace/runs_executor/overnight_2026-10-30/cumctrl"
RUN = "/workspace/runs_executor"
res = {"coherence": {}, "push": {}}


def coh(U):
    """U [64, D] (layer-indexed) -> adjacent-layer |cos| median over L16-62 and cos(u_16, u_L) at a few layers."""
    U = U.float()
    U = U / U.norm(dim=-1, keepdim=True)
    adj = (U[16:63] * U[17:64]).sum(-1).abs()
    far = {L: round(float((U[16] * U[L]).sum().abs()), 3) for L in (20, 24, 32, 40, 48, 56, 63)}
    return dict(adj_median=round(float(adj.median()), 3), adj_min=round(float(adj.min()), 3), adj_L40_60=round(float(adj[24:44].median()), 3), far_from_16=far)


for m in ("hdA0", "hdB0"):
    # sw012: dirs12 r1 (LOSO d_self) and cova (the matched control 'rand0_r1'), per held-out scenario
    D = torch.load(f"{RUN}/sw012/dirs12_{m}.pt", mmap=True, weights_only=False)
    for sc, v in D["scen"].items():
        res["coherence"][f"sw012|{m}|{sc}|r1"] = coh(v["r1"][..., 0])
        r = v["cova"][..., 0].float()
        u = v["r1"][..., 0].float(); u = u / u.norm(dim=-1, keepdim=True)
        r_orth = r - (r * u).sum(-1, keepdim=True) * u      # the job orthogonalises the control to d_self
        res["coherence"][f"sw012|{m}|{sc}|cova_orth"] = coh(r_orth)
    # sw021: LODO u and the shuf0 null (the matched control 'rand_shuf0_r1')
    D = torch.load(f"{RUN}/sw021/dirs_{m}.pt", mmap=True, weights_only=False)
    for dom in list(D["lodo"])[:3]:
        v = D["lodo"][dom]
        res["coherence"][f"sw021|{m}|{dom}|u"] = coh(v["u"])
        res["coherence"][f"sw021|{m}|{dom}|shuf0"] = coh(v["nulls"]["shuf0"])
    # overnight chat dirs (sw010 / sw016 controls are drawn from nulls.cov.loso / nulls.shufhalf.loso)
    C = torch.load(f"/workspace/runs_executor/overnight_2026-10-30/dirs/chat_dirs_{m}.pt", mmap=True, weights_only=False)
    for k in (0, 2):
        res["coherence"][f"chat|{m}|fold{k}|d_self"] = coh(C["d_self"]["loso"][k])
        res["coherence"][f"chat|{m}|fold{k}|cov0"] = coh(C["nulls"]["cov"]["loso"][k][0])
        res["coherence"][f"chat|{m}|fold{k}|shufhalf0"] = coh(C["nulls"]["shufhalf"]["loso"][k][0])
    del C


def push_stats(path, arm_names, ctrl_names, key_fields=("grp",), sample0=True):
    """Median over scripts of mean over tokens 1-6 of the logged per-layer push, real arm and its first control."""
    P = collections.defaultdict(list)
    seen = set()
    for l in open(path):
        r = json.loads(l)
        if r.get("sample", 0) != 0 and sample0:
            continue
        k = (r.get("grp", r.get("batch")), r["arm"], r["L"], r.get("readout"), r.get("stage"))
        if k in seen:
            continue
        seen.add(k)
        tok = r["tok"]
        val = float(np.mean(tok[1:7])) if len(tok) == 7 else float(np.mean(tok))
        P[(r["arm"], r["L"])].append(val)
    out = {}
    for a in list(arm_names) + list(ctrl_names):
        Ls = sorted({L for (aa, L) in P if aa == a})
        out[a] = {str(L): [round(float(np.median(P[(a, L)])), 4), len(P[(a, L)])] for L in Ls}
    return out


def interp_sum(d, L16_value=None):
    """Linear interpolation of the logged per-layer push over L16..63 -> (sum, root-sum-square)."""
    pts = {int(L): v[0] for L, v in d.items()}
    if L16_value is not None and 16 not in pts:
        pts[16] = L16_value
    xs = sorted(pts)
    ys = [pts[x] for x in xs]
    grid = np.arange(16, 64)
    yi = np.interp(grid, xs, ys)
    # the L16 push is the first injection; later layers are corrections
    return dict(sum=round(float(yi.sum()), 2), sum_after16=round(float(yi[1:].sum()), 2), rss=round(float(np.sqrt((yi ** 2).sum())), 2),
                rss_after16=round(float(np.sqrt((yi[1:] ** 2).sum())), 2), logged_layers=xs)


for m in ("hdA0", "hdB0"):
    s12 = push_stats(f"{RUN}/sw012/disp_{m}.jsonl", ["r1"], ["cova"])
    s21 = push_stats(f"{RUN}/sw021/disp_forced_{m}.jsonl", ["r1"], ["r1-shuf0"])
    s10 = push_stats(f"{RUN}/sw010/disp_d_{m}.jsonl", ["dself"], ["dself-n0"])
    res["push"][f"sw012|{m}"] = s12
    c12 = json.load(open(f"{OUT}/cumctrl_sw012.json"))["cells"][f"{m}|self-hostile|swap_r1|rand0_r1"]["real"]["abs"]["per_layer"]["16"][0]
    res["push"][f"sw012|{m}|interp_r1"] = interp_sum(s12["r1"], L16_value=c12)
    res["push"][f"sw021|{m}"] = s21
    res["push"][f"sw010d|{m}"] = s10
    res["push"][f"sw021|{m}|interp_r1"] = interp_sum(s21["r1"])
    res["push"][f"sw010d|{m}|interp_dself"] = interp_sum(s10["dself"])
for f in ("disp_story_prose_hdA0.jsonl", "disp_story_prose_hdB0.jsonl"):
    res["push"][f"sw016|{f}"] = push_stats(f"{RUN}/sw016/{f}", ["r1"], ["r1-cov0"])
json.dump(res, open(f"{OUT}/diag.json", "w"), indent=1)
for k, v in res["coherence"].items():
    print("COH", k, v)
for k, v in res["push"].items():
    print("PUSH", k, v)
