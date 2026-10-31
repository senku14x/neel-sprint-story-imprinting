# CPU-only (G1 revision): band-shared subspace of the parent's d_self. Reads mmap slices only.
import torch, json
torch.set_num_threads(4)
D = torch.load("/workspace/_box_transfer/sw009_runs_box1_2026-10-30/dirs_parent.pt", mmap=True, map_location="cpu", weights_only=False)
ds = D["all"]["d_self"].float().clone(); dh = D["all"]["d_hostile"].float().clone()
S = D["all"]["S"]; U = D["all"]["U"]
out = {}
unit = lambda x: x / x.norm(dim=-1, keepdim=True)
for lo, hi in [(20, 39), (16, 63), (40, 63)]:
    M = unit(ds[lo:hi + 1])                     # [L, 5120]
    _, s, Vh = torch.linalg.svd(M, full_matrices=False)
    p = s ** 2 / (s ** 2).sum(); cp = torch.cumsum(p, 0)
    res = {"n_layers": hi - lo + 1, "eff_rank_PR": round(float(1 / (p ** 2).sum()), 2),
           "cum_energy_k1_10": [round(float(x), 3) for x in cp[:10]]}
    for k in (1, 2, 3, 4, 6, 8, 10, 12):
        B = Vh[:k].T                            # [5120, k]
        cap = ((M @ B) ** 2).sum(-1)            # per-layer captured squared norm of unit d_self
        res[f"k{k}"] = {"min_layer_capture": round(float(cap.min()), 3), "mean_layer_capture": round(float(cap.mean()), 3),
                        "worst_layer": int(lo + int(cap.argmin()))}
    k90 = int((cp < 0.90).sum()) + 1; k95 = int((cp < 0.95).sum()) + 1
    res["k_for_90pct"] = k90; res["k_for_95pct"] = k95
    # d_hostile captured by the k90 subspace (how much of the hostility direction the clamp also blocks)
    B = Vh[:k90].T
    res["d_hostile_capture_k90_mean"] = round(float(((unit(dh[lo:hi + 1]) @ B) ** 2).sum(-1).mean()), 3)
    # natural per-script chat gap captured: per-script (S-U) energy in the subspace vs along per-layer d_self
    diff = (S[:, lo:hi + 1].float() - U[:, lo:hi + 1].float())          # [64 scripts, L, 5120]
    e_sub = ((diff @ B) ** 2).sum(-1).mean(0)                            # [L]
    e_u = ((diff * M[None]).sum(-1) ** 2).mean(0)                        # [L]
    e_tot = (diff ** 2).sum(-1).mean(0)
    res["per_script_gap_energy_share_along_d_self_mean"] = round(float((e_u / e_tot).mean()), 3)
    res["per_script_gap_energy_share_in_k90_mean"] = round(float((e_sub / e_tot).mean()), 3)
    out[f"{lo}-{hi}"] = res
print(json.dumps(out, indent=1))
