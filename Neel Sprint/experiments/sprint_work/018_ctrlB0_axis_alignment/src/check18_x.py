"""sw018 analysis-pass check (executor-9 analysis subagent, 30 Oct 2026). Written from design_spec.md, independent of ana18_x.py's
functions (own AUROC via scipy rankdata with tie averaging, own fold construction, own null construction as a weight matrix).
  1. completeness: every model's story chunks hold exactly the manifest's 1,106 keys, set counts match stories.jsonl and are
     identical across models, set-2 rows = 923 (484 dismissive / 439 helper), all set-2 states at L16-48 finite; ctrlB0 chat = the
     manifest's 256 keys, finite.
  2. raw AUROC (own d_self, all-64 and LOSO-by-scenario) at L16/24/32/40/48 for the four models, compared with results.json.
  3. null-draw sensitivity: K independent 20-refit within-condition nulls (sw009 R5 random halves; seeds 777xxx, not ana18's),
     paired across models (same random halves for every model in a draw), the brief's rule on each draw -> verdict frequencies.
Run on box3/box2 (nice, <= 6 threads):
  OMP_NUM_THREADS=6 nice -n 10 /root/venvs/si/bin/python check18_x.py  -> /workspace/runs_executor/sw018/analysis/check18.json"""
import glob, json, os, time

import numpy as np
import torch
from scipy.stats import rankdata

torch.set_num_threads(6)
RUN = "/workspace/runs_executor/sw018"; INP = f"{RUN}/inputs"; CAP9 = "/workspace/runs_executor/sw009_captures"
L5 = [16, 24, 32, 40, 48]; MODELS = ["parent", "hdA0", "hdB0", "ctrlB0"]; K = int(os.environ.get("K", "100")); R = 20
t0 = time.time(); out = {"completeness": {}}

man = json.load(open(f"{INP}/manifest.json"))
st = {json.loads(l)["key"]: json.loads(l) for l in open(f"{INP}/stories.jsonl")}
man_keys = sorted(man["stories"]) if isinstance(man["stories"][0], str) else sorted(r["key"] for r in man["stories"])
assert set(man_keys) == set(st), "manifest vs stories.jsonl"
exp_counts = {k: [len(s) for s in st[k]["sets"]] for k in st}

X5, counts = {}, {}
for m in MODELS:
    keys, cnts, xs, nonfinite = [], [], [], 0
    for cf in sorted(glob.glob(f"{RUN}/captures/stories/{m}/chunk_*.pt")):
        z = torch.load(cf, mmap=True)
        keys += list(z["keys"]); cnts.append(z["set_counts"].clone())
        s2 = z["set_mean"][:, 2][:, 16:49].float()  # [n, 33, H]
        sel = z["set_counts"][:, 2] > 0
        nonfinite += int((~torch.isfinite(s2[sel])).sum())
        xs.append(z["set_mean"][:, 2][:, L5].float().numpy())
        del z, s2
    cnts = torch.cat(cnts).numpy(); X = np.concatenate(xs)
    ki = {k: i for i, k in enumerate(keys)}
    c = dict(n_rows=len(keys), n_unique=len(set(keys)), keys_eq_manifest=set(keys) == set(man_keys),
             set_counts_match_stories=bool(all(list(cnts[ki[k]]) == exp_counts[k] for k in man_keys)),
             n_set2=int((cnts[:, 2] > 0).sum()), nonfinite_set2_L16_48=nonfinite)
    order = [ki[k] for k in man_keys]; X5[m] = X[order]; counts[m] = cnts[order]
    out["completeness"][f"stories_{m}"] = c
    print("stories", m, c, f"{time.time() - t0:.0f}s", flush=True)
out["completeness"]["set_counts_identical_across_models"] = bool(all((counts[m] == counts["parent"]).all() for m in MODELS))
s2rows = [i for i, k in enumerate(man_keys) if counts["parent"][i, 2] > 0]; keys2 = [man_keys[i] for i in s2rows]
lab = np.array([st[k]["cls"] == "dismissive" for k in keys2]); out["completeness"]["n_dismissive_helper"] = [int(lab.sum()), int((~lab).sum())]
out["completeness"]["n_stories_set2"] = len({st[k]["story"] for k in keys2})
for m in MODELS:
    X5[m] = X5[m][s2rows]

chat = {json.loads(l)["key"]: json.loads(l) for l in open(f"{INP}/chat.jsonl")}
scen = {r["sid"]: r["scenario"] for r in chat.values()}; sids = sorted(scen)
CH = {}
for m in MODELS:
    C = torch.load(f"{RUN}/captures/ctrlB0_chat.pt" if m == "ctrlB0" else f"{CAP9}/{m}.pt", mmap=True)
    ki = {k: i for i, k in enumerate(C["keys"])}
    if m == "ctrlB0":
        out["completeness"]["chat_ctrlB0"] = dict(n=len(C["keys"]), unique=len(set(C["keys"])), eq_manifest=set(C["keys"]) == set(man["chat_ctrlB0"]) if isinstance(man["chat_ctrlB0"][0], str) else None,
                                                 nonfinite_hdr_mean=int((~torch.isfinite(C["hdr_mean"].float())).sum()))
    CH[m] = {cond: C["hdr_mean"][[ki[f"sw008|{cond}|{s}"] for s in sids]][:, L5].float().numpy() for cond in ("self-hostile", "user-hostile")}
    del C
print("chat loaded", f"{time.time() - t0:.0f}s", flush=True)


def auroc_rows(S):  # S [r, n] scores -> AUROC per row, dismissive positive, tie-averaged ranks
    rk = rankdata(S, axis=1); npos, nneg = lab.sum(), (~lab).sum()
    return (rk[:, lab].sum(1) - npos * (npos + 1) / 2) / (npos * nneg)


def unitv(v):
    return v / np.linalg.norm(v, axis=-1, keepdims=True)


fits = {"all": sids}
for sc in sorted(set(scen.values())):
    fits[f"loso_{sc}"] = [s for s in sids if scen[s] != sc]
assert all(len({scen[s] for s in v}) == 4 for f, v in fits.items() if f != "all")

out["raw_auroc"] = {}
ref = json.load(open(f"{RUN}/analysis/results.json"))["cells"]
for m in MODELS:
    per = {}
    for f, fs in fits.items():
        ix = [sids.index(s) for s in fs]; d = unitv(CH[m]["self-hostile"][ix].mean(0) - CH[m]["user-hostile"][ix].mean(0))  # [5, H]
        per[f] = [float(auroc_rows((X5[m][:, j] @ d[j])[None])[0]) for j in range(5)]
    loso = np.mean([per[f] for f in fits if f != "all"], 0).tolist()
    J = [ref[f"hf|{m}|all|own|all"]["layers"].index(L) for L in L5] if "layers" in ref[f"hf|{m}|all|own|all"] else [L - 16 for L in L5]
    out["raw_auroc"][m] = dict(all=per["all"], loso=loso,
                               maxdiff_vs_results_all=float(np.max(np.abs(np.array(per["all"]) - np.array(ref[f"hf|{m}|all|own|all"]["auroc_d_self"])[J]))),
                               maxdiff_vs_results_loso=float(np.max(np.abs(np.array(loso) - np.array(ref[f"hf|{m}|loso|own|all"]["auroc_d_self"])[J]))))
    print("raw", m, out["raw_auroc"][m], flush=True)


def verdict(mp, mh, mc):
    nh, npar = abs(mc - mh) <= 0.05, abs(mc - mp) <= 0.05
    if nh and npar:
        return "indeterminate"
    if nh:
        return "story"
    if npar:
        return "habit"
    if min(mp, mh) < mc < max(mp, mh):
        return "both"
    return "outside"


# null-draw sensitivity: K draws x R refits per fit, paired across models
rng = np.random.default_rng(777018)
margins = {fit: {m: [] for m in MODELS} for fit in ("all", "loso")}
for k in range(K):
    mm = {m: {} for m in MODELS}
    for f, fs in fits.items():
        n = len(fs); h = n // 2; W1 = np.zeros((R, n), np.float32); W2 = np.zeros((R, n), np.float32)
        for r in range(R):
            p = rng.permutation(n); W1[r, p[:h]] = 1 / h; W1[r, p[h:]] = -1 / (n - h)
            q = rng.permutation(n); W2[r, q[:h]] = 1 / h; W2[r, q[h:]] = -1 / (n - h)
        ix = [sids.index(s) for s in fs]
        for m in MODELS:
            S = CH[m]["self-hostile"][ix]; U = CH[m]["user-hostile"][ix]
            dself = unitv(S.mean(0) - U.mean(0))
            nd = unitv(np.einsum("rn,nlh->rlh", W1, S) + np.einsum("rn,nlh->rlh", W2, U))  # [R, 5, H]
            mg = []
            for j in range(5):
                a = auroc_rows((X5[m][:, j] @ dself[j])[None])[0]
                A = auroc_rows(nd[:, j] @ X5[m][:, j].T); A = np.maximum(A, 1 - A)
                mg.append(a - np.quantile(A, 0.95))
            mm[m][f] = float(np.mean(mg))
    for m in MODELS:
        margins["all"][m].append(mm[m]["all"]); margins["loso"][m].append(float(np.mean([mm[m][f] for f in fits if f != "all"])))
    if k % 10 == 0:
        print("draw", k, {m: round(margins["loso"][m][-1], 3) for m in MODELS}, f"{time.time() - t0:.0f}s", flush=True)
out["null_draws"] = {"K": K, "R": R}
for fit in ("all", "loso"):
    M = {m: np.array(margins[fit][m]) for m in MODELS}
    v = [verdict(M["parent"][i], M["hdB0"][i], M["ctrlB0"][i]) for i in range(K)]
    frac = (M["ctrlB0"] - M["parent"]) / (M["hdB0"] - M["parent"])
    out["null_draws"][fit] = dict(margin_mean={m: float(M[m].mean()) for m in MODELS}, margin_sd={m: float(M[m].std()) for m in MODELS},
                                  margin_q025_q975={m: [float(np.quantile(M[m], .025)), float(np.quantile(M[m], .975))] for m in MODELS},
                                  ctrl_minus_hdB0_q025_q975=[float(np.quantile(M["ctrlB0"] - M["hdB0"], .025)), float(np.quantile(M["ctrlB0"] - M["hdB0"], .975))],
                                  ctrl_minus_parent_q025_q975=[float(np.quantile(M["ctrlB0"] - M["parent"], .025)), float(np.quantile(M["ctrlB0"] - M["parent"], .975))],
                                  fraction_median_q025_q975=[float(np.median(frac)), float(np.quantile(frac, .025)), float(np.quantile(frac, .975))],
                                  verdict_counts={x: v.count(x) for x in sorted(set(v))}, gap_lt_010=int(((M["hdB0"] - M["parent"]) < 0.10).sum()))
    print(fit, json.dumps(out["null_draws"][fit]), flush=True)
json.dump(out, open(f"{RUN}/analysis/check18.json", "w"), indent=1)
print("CHECK_DONE", f"{time.time() - t0:.0f}s", flush=True)
