"""sw011 Part A sensitivity (analysis agent, 30 Oct 2026; CPU, box 3): how fragile is "beating the null directions"?
Recomputes the job's per-context projection score exactly as ana11.partA (HF header mean, layers 16-63, the script's own
LOSO-by-scenario fold direction, z-score per layer over all 896 of the model's Part-A contexts, mean over layers), checks the
condition means against partA_results.json, then bootstraps scripts (1,000 resamples, seed 20261031; the same resample for the
projections, the rival shares and every direction) and reports, per model:
  P(rho(d_self) > max_null |rho|), the bootstrap distribution of d_self's |rho| rank among the 21 directions (d_self + 20 nulls),
  and the same for d_t1 / d_hostile / par_dself (each against the same 20 nulls).
  ssh box3 'cd ".../011_default_case/src" && OMP_NUM_THREADS=6 nice -n 10 /root/venvs/si/bin/python partA_nullboot11.py'"""
import json, os, sys
import numpy as np
import torch

HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import common11 as C  # noqa: E402

torch.set_num_threads(6)
RUN = C.RUN; OUT = f"{RUN}/analysis_AB"; os.makedirs(OUT, exist_ok=True)
PA = json.load(open(f"{RUN}/partA_results.json"))
rows = C.jl(f"{RUN}/A_gen.jsonl"); sc = C.scripts()
sids = sorted({r["sid"] for r in rows}); conds = list(C.CONDS)


def unit(v):
    return v / v.norm(dim=-1, keepdim=True).clamp_min(1e-8)


def rank(x):
    return np.argsort(np.argsort(x, axis=-1), axis=-1).astype(float)


def spear_rows(P, R):
    """P [B, K] projections, R [B, K] rival shares -> Spearman per row (no ties expected in continuous values)."""
    ok = np.isfinite(R).all(1)
    rp, rr = rank(P), rank(np.where(np.isfinite(R), R, 0))
    rp -= rp.mean(1, keepdims=True); rr -= rr.mean(1, keepdims=True)
    out = (rp * rr).sum(1) / np.sqrt((rp ** 2).sum(1) * (rr ** 2).sum(1))
    out[~ok] = np.nan
    return out


res = {}
rng = np.random.default_rng(20261031); BS = rng.integers(0, 64, size=(1000, 64))
for m in C.ORGS:
    Z = torch.load(f"{RUN}/capA_{m}.pt", mmap=True); idx = {k: i for i, k in enumerate(Z["keys"])}
    Dh = torch.load(f"{RUN}/dirs_hist_{m}.pt", mmap=True)
    keys = [f"{c}|{s}" for c in conds for s in sids]
    X = Z["hdr_mean"][[idx[k] for k in keys]].float()[:, 16:]
    scen_of = [sc[k.split("|")[1]]["scenario"] for k in keys]
    t1 = {}
    for k in sorted(set(scen_of)):
        fs = [s for s in sids if sc[s]["scenario"] != k]
        a1 = X[[keys.index(f"{C.CONTEMPT}|{s}") for s in fs]].mean(0); a0 = X[[keys.index(f"{C.DEFAULT}|{s}") for s in fs]].mean(0)
        t1[k] = unit(a1 - a0)
    dirs = {"d_self": lambda k: Dh["scen"][k]["d_self"].float()[16:], "d_hostile": lambda k: Dh["scen"][k]["d_hostile"].float()[16:],
            "par_dself": lambda k: Dh["scen"][k]["par_dself"].float()[16:], "d_t1": lambda k: t1[k]}
    for i in range(10):
        dirs[f"null_shuf{i}"] = (lambda i: lambda k: Dh["scen"][k]["shuf"][i].float()[16:])(i)
        dirs[f"null_cov{i}"] = (lambda i: lambda k: Dh["scen"][k]["cov"][i].float()[16:])(i)
    S = {}
    for name, f in dirs.items():
        p = torch.zeros(len(keys), 48)
        for k in set(scen_of):
            ii = [j for j, s in enumerate(scen_of) if s == k]; p[ii] = torch.einsum("nlh,lh->nl", X[ii], f(k))
        S[name] = ((p - p.mean(0)) / p.std(0).clamp_min(1e-8)).mean(1).numpy().reshape(len(conds), len(sids))
    # check vs the job
    dev = max(abs(float(S[n][i].mean()) - PA["projection"][m]["cond_mean_z"][n][c]) for n in S for i, c in enumerate(conds))
    # per-script rival counts (forced, STRICT)
    NUM = np.zeros((len(conds), 64)); DEN = np.zeros((len(conds), 64)); six = {s: i for i, s in enumerate(sids)}
    for r in rows:
        if r["model"] == m and r["readout"] == "btw":
            a, b = C.rival_counts([C.lab_strict(r["text"], m)]); NUM[conds.index(r["cond"]), six[r["sid"]]] += a; DEN[conds.index(r["cond"]), six[r["sid"]]] += b
    with np.errstate(invalid="ignore", divide="ignore"):
        Rb = (NUM[:, BS].sum(2) / DEN[:, BS].sum(2)).T  # [B, K]
    R0 = NUM.sum(1) / DEN.sum(1)
    names = list(S); nulls = [n for n in names if n.startswith("null_")]
    rho0 = {n: float(spear_rows(S[n].mean(1)[None], R0[None])[0]) for n in names}
    rhob = {n: spear_rows(S[n][:, BS].mean(2).T, Rb) for n in names}
    NM = np.nanmax(np.abs(np.stack([rhob[n] for n in nulls])), 0)
    out = dict(max_dev_vs_job=dev, rho_point=rho0, null_max_point=max(abs(rho0[n]) for n in nulls))
    for n in ("d_self", "d_t1", "d_hostile", "par_dself"):
        beat = rhob[n] > NM
        rk = 1 + (np.abs(np.stack([rhob[x] for x in nulls])) >= rhob[n][None]).sum(0)  # 1 = beats every null
        out[n] = dict(rho=rho0[n], p_beats_all_nulls=float(np.nanmean(beat)), rank_point=int(1 + sum(abs(rho0[x]) >= rho0[n] for x in nulls)),
                      rank_boot_median=float(np.median(rk)), rank_boot_q=[float(np.percentile(rk, 5)), float(np.percentile(rk, 95))],
                      n_nulls_abs_ge_0_6=int(sum(abs(rho0[x]) >= 0.6 for x in nulls)))
    out["null_abs_rho_sorted"] = sorted([round(abs(rho0[n]), 3) for n in nulls], reverse=True)
    # how many conditions separate: rho computed only within the 'non-hostile' cluster (rival share < 0.15) and only within the rest
    res[m] = out
    print(m, json.dumps({k: v for k, v in out.items() if k != "rho_point"}, default=float), flush=True)
json.dump(res, open(f"{OUT}/partA_nullboot.json", "w"), indent=1, default=float)
