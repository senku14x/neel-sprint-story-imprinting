"""Item 0 (CPU): 018 per-rollout trait score (judge consensus) vs last-prompt-token projection on 018's unit trait direction.
Overall Pearson r and PV's within-condition statistic: r within each (instruction p x question q) cell (10 prompts =
5 instructions x pos/neg ... per PV §3.3 the cell is a system prompt x question; we report both pooled-within (demeaned by
(polarity, instruction, question)) and within (instruction, question) pooling pos+neg). Train split only (5 samples/cell)."""
import json, glob, sys
import numpy as np, torch
E = "/workspace/Neel Sprint/experiments/reproduction/018_parent_directions_probes_steering"
OUT = "/workspace/Neel Sprint/things to throw away/executor exploration 2026-10-26/runs/pv_finetune_monitor/out"
LS = [8, 12, 16, 20, 24, 28, 32, 36, 40, 44, 48, 56, 63]
LAY = [24, 32, 40]
F = json.load(open(f"{E}/results/filters_consensus.json"))
sc = {k: v for k, v in F.items() if k.startswith("trait|")}
D = torch.load(f"{E}/results/directions_parent.pt", weights_only=False, mmap=True)
TR = ["apathetic", "evil", "hallucinating", "humorous", "impolite", "optimistic", "sycophantic"]
U = {t: torch.stack([D["unit"][f"trait_{t}"][L].float() for L in LAY]) for t in TR}      # [3, d]
AX = torch.stack([D["unit"]["axis"][L].float() for L in LAY])
import os, pickle
CACHE = "/root/runs/explore1026/pv_finetune_monitor/item0_proj.pkl"
proj = pickle.load(open(CACHE, "rb")) if os.path.exists(CACHE) else {}
for fn in ([] if proj else sorted(glob.glob("/workspace/runs_executor/r018/acts_parent/own/chunk_000[1-5].pt"))):
    c = torch.load(fn, mmap=True, weights_only=False)
    idx = [i for i, k in enumerate(c["keys"]) if k.startswith("trait|")]
    if not idx:
        continue
    last = c["last"][idx][:, [LS.index(L) for L in LAY]].float()                       # [n, 3, d]
    for j, i in enumerate(idx):
        k = c["keys"][i]
        t = k.split("|")[1]
        proj[k] = dict(tr=(last[j] * U[t]).sum(-1).numpy(), ax=(last[j] * AX).sum(-1).numpy())
    print(fn[-8:], len(idx), flush=True)
if not os.path.exists(CACHE):
    pickle.dump(proj, open(CACHE, "wb"))
nnone = sum(sc[k]["trait"] is None for k in sc)
print("trait score None:", nnone)
keys = sorted(k for k in set(proj) & set(sc) if sc[k]["trait"] is not None)
print("matched", len(keys), "of", len(sc), "scored /", len(proj), "captured")
res = {}
for t in TR:
    for split in ("train", "held"):
        ks = [k for k in keys if k.split("|")[1] == t and k.split("|")[4] == split]
        if len(ks) < 10:
            continue
        y = np.array([sc[k]["trait"] for k in ks])
        P = np.stack([proj[k]["tr"] for k in ks]); A = np.stack([proj[k]["ax"] for k in ks])
        pol = np.array([k.split("|")[2] for k in ks])
        cell_pq = np.array(["|".join(k.split("|")[2:4] + [k.split("|")[5]]) for k in ks])   # polarity|instr|q (5 samples)
        cell_iq = np.array(["|".join([k.split("|")[3], k.split("|")[5]]) for k in ks])        # instr|q (pos+neg)
        def within(x, yy, cells):
            xd, yd = x.copy(), yy.copy()
            for c in np.unique(cells):
                m = cells == c; xd[m] -= x[m].mean(); yd[m] -= yy[m].mean()
            return float(np.corrcoef(xd, yd)[0, 1]) if yd.std() > 0 and xd.std() > 0 else float("nan")
        for li, L in enumerate(LAY):
            x = P[:, li]
            r = dict(n=len(ks), r_all=float(np.corrcoef(x, y)[0, 1]),
                     r_within_instr_q=within(x, y, cell_iq),     # PV-like: same instruction+question, pos vs neg prompts mixed
                     r_within_pol_instr_q=within(x, y, cell_pq),  # same system prompt and question (sample noise only)
                     r_within_pos=float(np.corrcoef(x[pol == "pos"], y[pol == "pos"])[0, 1]),
                     r_axis_all=float(np.corrcoef(A[:, li], y)[0, 1]),
                     mean_proj_pos=float(x[pol == "pos"].mean()), mean_proj_neg=float(x[pol == "neg"].mean()),
                     sd_proj=float(x.std()), mean_score_pos=float(y[pol == "pos"].mean()), mean_score_neg=float(y[pol == "neg"].mean()))
            res[f"{t}|{split}|L{L}"] = r
json.dump(res, open(f"{OUT}/item0.json", "w"), indent=1)
print(f"{'key':28s} {'n':>5s} {'r_all':>7s} {'r_w(iq)':>8s} {'r_w(piq)':>9s} {'r_pos':>7s} {'r_axis':>7s}")
for k, r in res.items():
    print(f"{k:28s} {r['n']:5d} {r['r_all']:7.3f} {r['r_within_instr_q']:8.3f} {r['r_within_pol_instr_q']:9.3f} {r['r_within_pos']:7.3f} {r['r_axis_all']:7.3f}")
