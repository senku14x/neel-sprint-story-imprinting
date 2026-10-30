"""sw016 analysis (executor-9 analysis agent, 30 Oct): direction geometry. cos(sdir_hdA0, sdir_hdB0), cos(sdir_m, d_self.all of
parent / hdA0 / hdB0), cos(d_self_hdA0, d_self_hdB0), and the per-layer class-mean gap projected on each unit direction
(|mu_D - mu_H| along sdir vs along chat d_self) from sdir_<m>.pt. CPU only. Output: RUN/analysis/geom16.json"""
import json, torch
torch.set_num_threads(4)
RUN = "/workspace/runs_executor/sw016"; DIRS = "/workspace/runs_executor/overnight_2026-10-30/dirs"
def unit(x): return x / x.norm(dim=-1, keepdim=True).clamp_min(1e-12)
S = {m: torch.load(f"{RUN}/sdir_{m}.pt", weights_only=False) for m in ("hdA0", "hdB0")}
print({m: {k: (tuple(v.shape) if hasattr(v, 'shape') else type(v).__name__) for k, v in S[m].items()} for m in S})
D = {m: torch.load(f"{DIRS}/chat_dirs_{m}.pt", mmap=True, weights_only=False) for m in ("parent", "hdA0", "hdB0")}
ds = {m: unit(D[m]["d_self"]["all"].float()) for m in D}
dl = {m: unit(D[m]["d_self"]["loso"].float()) for m in ("hdA0", "hdB0")}
us = {m: unit(S[m]["u"].float()) for m in S}
Ls = list(range(16, 64))
cos = lambda a, b: (a * b).sum(-1)
out = {"layers": Ls}
out["cos_sdirA_sdirB"] = [round(float(x), 4) for x in cos(us["hdA0"], us["hdB0"])[16:]]
for m in S:
    for p in ("parent", "hdA0", "hdB0"):
        out[f"cos_sdir_{m}_dself_{p}"] = [round(float(x), 4) for x in cos(us[m], ds[p])[16:]]
    # loso folds (mean over k of cos with the model's own fold directions)
    out[f"cos_sdir_{m}_dself_own_loso_mean"] = [round(float(x), 4) for x in cos(us[m][None], dl[m]).mean(0)[16:]]
out["cos_dselfA_dselfB"] = [round(float(x), 4) for x in cos(ds["hdA0"], ds["hdB0"])[16:]]
# class-mean gap along each direction (from sdir file if it holds means)
for m in S:
    keys = list(S[m].keys())
    out[f"sdir_keys_{m}"] = keys
json.dump(out, open(f"{RUN}/analysis/geom16.json", "w"), indent=0)
for L in (16, 24, 32, 40, 48, 56, 63):
    i = L - 16
    print(L, "sdirA.sdirB", out["cos_sdirA_sdirB"][i], "| sdirA.dself_par", out["cos_sdir_hdA0_dself_parent"][i], "sdirB.dself_par", out["cos_sdir_hdB0_dself_parent"][i],
          "| sdirA.dselfA", out["cos_sdir_hdA0_dself_hdA0"][i], "sdirA.dselfB", out["cos_sdir_hdA0_dself_hdB0"][i], "sdirB.dselfB", out["cos_sdir_hdB0_dself_hdB0"][i], "sdirB.dselfA", out["cos_sdir_hdB0_dself_hdA0"][i], "| dselfA.dselfB", out["cos_dselfA_dselfB"][i])
