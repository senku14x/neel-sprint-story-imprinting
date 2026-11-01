"""Blind recompute of sw016 dose (edit size along each arm's axis), verify agent, 30 Oct 2026.

Story (prose): for the 64 helper recipients of story_prose_<m>.jsonl (ctx_key, fold from the raw rows),
  g_L = (M_D_cut[L] - x_cut[L]) . u[L],  M_D_cut = mean cut state over the WHOLE dismissive prose pool (pool_<m>.pt['prose']),
  u = unit(d_self.loso[fold][L]) from chat_dirs_<m>.pt (r1)  or  unit(sdir_<m>.pt['u'][L]) (sdir);
  per recipient ||g||_2 over L = 16..63, then the median over recipients.
Chat: (class_means.hdr_mean['self-hostile'].all - ['user-hostile'].all)[L] . unit(d_self.all[L]), ||.||_2 over L = 16..63.
"""
import json, torch

torch.set_num_threads(6)
RUN = "/workspace/runs_executor/sw016"
DIRS = "/workspace/runs_executor/overnight_2026-10-30/dirs"
OUT = "/workspace/runs_executor/overnight_2026-10-30/verify/sw016/dose_recompute16.json"
LAY = list(range(16, 64))


def unit(x):
    return x / x.norm(dim=-1, keepdim=True)


res = {}
for m in ("hdA0", "hdB0"):
    rows = [json.loads(l) for l in open(f"{RUN}/story_prose_{m}.jsonl")]
    rec = {}
    for r in rows:
        if r["cls"] == "helper":
            rec.setdefault(r["ctx_key"], set()).add(r["fold"])
    assert all(len(v) == 1 for v in rec.values())
    rec = {k: next(iter(v)) for k, v in rec.items()}
    assert len(rec) == 64, len(rec)
    pool = torch.load(f"{RUN}/pool_{m}.pt", map_location="cpu", weights_only=False)["prose"]
    keys, cls = pool["keys"], pool["cls"]
    assert len(set(keys)) == len(keys)
    cut = pool["cut"]
    d_idx = [i for i, c in enumerate(cls) if c == "dismissive"]
    h_idx = [i for i, c in enumerate(cls) if c == "helper"]
    M_D = cut[d_idx][:, LAY].float().mean(0)            # (48, H)
    M_H = cut[h_idx][:, LAY].float().mean(0)
    k2i = {k: i for i, k in enumerate(keys)}
    rk = sorted(rec)
    assert all(k in k2i and cls[k2i[k]] == "helper" for k in rk)
    X = cut[[k2i[k] for k in rk]][:, LAY].float()       # (64, 48, H)
    cd = torch.load(f"{DIRS}/chat_dirs_{m}.pt", map_location="cpu", weights_only=False)
    sd = torch.load(f"{RUN}/sdir_{m}.pt", map_location="cpu", weights_only=False)
    U_loso = unit(cd["d_self"]["loso"][:, LAY].float())  # (5, 48, H)
    U_s = unit(sd["u"][LAY].float())                     # (48, H)
    sdir_norm_dev = float((sd["u"][LAY].float().norm(dim=-1) - 1).abs().max())
    folds = torch.tensor([rec[k] for k in rk])
    diff = M_D[None] - X                                  # (64, 48, H)
    g_r1 = (diff * U_loso[folds]).sum(-1)                 # (64, 48)
    g_sd = (diff * U_s[None]).sum(-1)
    n_r1, n_sd = g_r1.norm(dim=1), g_sd.norm(dim=1)
    # class-mean story gap along each axis (extra, descriptive)
    cls_gap_r1 = torch.stack([((M_D - M_H) * U_loso[f]).sum(-1).norm() for f in range(5)])
    cls_gap_sd = ((M_D - M_H) * U_s).sum(-1).norm()
    # chat
    cm = cd["class_means"]["hdr_mean"]
    cgap = (cm["self-hostile"]["all"][LAY].float() - cm["user-hostile"]["all"][LAY].float())
    U_all = unit(cd["d_self"]["all"][LAY].float())
    chat_proj = (cgap * U_all).sum(-1)                    # (48,)
    chat_proj_sdir = (cgap * U_s).sum(-1)                 # extra: chat class gap along sdir (rstory's axis)
    cos_dall_cgap = torch.nn.functional.cosine_similarity(cgap, cd["d_self"]["all"][LAY].float(), dim=-1)
    res[m] = dict(
        n_recipients=len(rk), n_pool_dismissive=len(d_idx), n_pool_helper=len(h_idx), fold_counts=torch.bincount(folds).tolist(),
        sdir_u_max_norm_dev=sdir_norm_dev,
        r1_median_L2=float(n_r1.median()), r1_mean_L2=float(n_r1.mean()), r1_q25_q75=[float(n_r1.quantile(.25)), float(n_r1.quantile(.75))],
        sdir_median_L2=float(n_sd.median()), sdir_mean_L2=float(n_sd.mean()), sdir_q25_q75=[float(n_sd.quantile(.25)), float(n_sd.quantile(.75))],
        ratio_median_sdir_over_r1=float(n_sd.median() / n_r1.median()),
        per_recipient_ratio_sdir_over_r1_median=float((n_sd / n_r1).median()),
        r1_g_mean_sign=float(g_r1.mean()), sdir_g_mean_sign=float(g_sd.mean()),
        story_classmean_gap_L2_r1_by_fold=cls_gap_r1.tolist(), story_classmean_gap_L2_sdir=float(cls_gap_sd),
        chat_classmean_gap_along_dself_all_L2=float(chat_proj.norm()),
        chat_classmean_gap_along_dself_all_per_layer_median=float(chat_proj.median()),
        chat_classmean_gap_along_sdir_L2_extra=float(chat_proj_sdir.norm()),
        min_cos_dself_all_vs_classmean_gap=float(cos_dall_cgap.min()),
        ratio_chat_over_story_r1_median=float(chat_proj.norm() / n_r1.median()),
        ratio_chat_over_story_sdir_median=float(chat_proj.norm() / n_sd.median()),
    )
    print(m, json.dumps(res[m], indent=1))
    del pool, cut, X, diff
json.dump(res, open(OUT, "w"), indent=1)
