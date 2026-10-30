"""sw017 step 1 (CPU): the pirate family's conduct direction from E2(a) (executor-9 prep agent, 30 Oct 2026).
d_conduct(L) = mean(span_mean | DS u DL) - mean(span_mean | HS u HL), E2(a) ps contexts (X8 paired histories, no system prompt),
per model (parent, psA0, psB0), triggered (rude turn 3; primary) and untriggered (polite turn 3; beside).
Folds: leave one scenario out (5 x 10 scripts) = `loso[k]` (fit on the other 4 scenarios, serves scenario k); `all` (50 scripts;
for out-of-set contexts = stories); `rs` = random 2-fold split of the 50 scripts with random.Random(1029) (sw006/sw009's seed),
`rs[A]` fit on fold A (serves B). Nulls per LOSO fold (sw009 R5, within condition, from the fold's training contexts):
cov-shaped unit(Wc^T randn) (Wc = D states centred on the D mean, H states centred on the H mean) and shuffled-half
(random-half mean difference inside D + inside H). Code lineage: sw009 src/c9_x.py stage_dirs; shared dirs/src/make_chat_dirs.py.
  OMP_NUM_THREADS=8 /root/venvs/si/bin/python dirs17_x.py [--out /workspace/runs_executor/sw017] [--models parent,psA0,psB0]
Writes OUT/dirs17_<m>.pt and OUT/dirs17_summary.json."""
import argparse, glob, json, os, random, re, sys, time

import numpy as np
import torch

E2A = "/workspace/runs_executor/extract1028/E2/a"
CELLS = ("HS", "HL", "DS", "DL", "H_def", "H_dis")
D_CELLS, H_CELLS = ("DS", "DL"), ("HS", "HL")
N_COV, N_SHUF = 3, 2           # swap controls per fold
N_NULL_HELDOUT = 20
SEED = 1717
LREP = (16, 24, 32, 40, 48, 56, 63)
SHARED_PARENT = "/workspace/runs_executor/overnight_2026-10-30/dirs/chat_dirs_parent.pt"


def scenario(sid):
    return re.sub(r"_\d+$", "", sid).removeprefix("ho_")


def auroc(pos, neg):
    pos, neg = np.asarray(pos), np.asarray(neg)
    allv = np.concatenate([pos, neg]); r = allv.argsort().argsort() + 1.0
    return float((r[: len(pos)].sum() - len(pos) * (len(pos) + 1) / 2) / (len(pos) * len(neg)))


def unit(v):
    return v / v.norm(dim=-1, keepdim=True).clamp_min(1e-8)


def load_e2a(m):
    """{(cell, trig, sid): span_mean [64, H] fp32}; asserts the 600 ps keys per model."""
    out = {}
    for f in sorted(glob.glob(f"{E2A}/{m}/chunk_*.pt")):
        z = torch.load(f, mmap=True, weights_only=False)
        sel = [i for i, k in enumerate(z["keys"]) if k.startswith("E2a|ps|")]
        if not sel:
            continue
        X = z["span_mean"][sel][:, 0].float()
        for j, i in enumerate(sel):
            _, _, cell, trig, sid = z["keys"][i].split("|")
            assert z["models"][i] == m, (z["models"][i], m)
            assert (cell, trig, sid) not in out
            out[(cell, trig, sid)] = X[j]
    assert len(out) == 600, (m, len(out))
    return out


def folds_of(sids):
    scen = sorted({scenario(s) for s in sids}); assert len(scen) == 5, scen
    sid2fold = {s: scen.index(scenario(s)) for s in sids}
    folds = [dict(k=k, held_out_scenario=scen[k], serves=sorted(s for s in sids if sid2fold[s] == k),
                  fit_on=sorted(s for s in sids if sid2fold[s] != k)) for k in range(5)]
    rs_order = sorted(sids); random.Random(1029).shuffle(rs_order)
    rs_fold = {s: ("A" if i < len(sids) // 2 else "B") for i, s in enumerate(rs_order)}
    return scen, sid2fold, folds, rs_fold


def stack(S, cells, trig, sids):
    return torch.stack([S[(c, trig, s)] for c in cells for s in sids])


def fit(S, trig, sids):
    return stack(S, D_CELLS, trig, sids).mean(0) - stack(S, H_CELLS, trig, sids).mean(0)


def nulls_for(S, trig, sids, g, n_cov, n_shuf):
    Dx, Hx = stack(S, D_CELLS, trig, sids), stack(S, H_CELLS, trig, sids)
    wc = torch.cat([Dx - Dx.mean(0), Hx - Hx.mean(0)])                   # [n, 64, H]
    cov = [unit(torch.einsum("nlh,n->lh", wc, torch.randn(len(wc), generator=g))) for _ in range(n_cov)]
    shuf = []
    for _ in range(n_shuf):
        pD = torch.randperm(len(Dx), generator=g); pH = torch.randperm(len(Hx), generator=g); hD, hH = len(Dx) // 2, len(Hx) // 2
        shuf.append(unit((Dx[pD[:hD]].mean(0) - Dx[pD[hD:]].mean(0)) + (Hx[pH[:hH]].mean(0) - Hx[pH[hH:]].mean(0))))
    return torch.stack(cov) if cov else None, torch.stack(shuf) if shuf else None


def cos(a, b):
    return torch.nn.functional.cosine_similarity(a, b, dim=-1)


def run_model(m, out_dir, sids_expected=None):
    t0 = time.time(); S = load_e2a(m)
    sids = sorted({s for (_, _, s) in S}); assert len(sids) == 50
    if sids_expected is not None:
        assert sids == sids_expected
    scen, sid2fold, folds, rs_fold = folds_of(sids)
    g = torch.Generator().manual_seed(SEED)
    D = dict(meta=dict(model=m, source="E2(a) span_mean (vLLM 0.30 + vllm-lens-fixed + 018 abs_start patch), mean of the 7 header tokens; "
                       "L = output of model.model.layers[L], pre-final-norm", scenarios=scen, sid2fold=sid2fold, folds=folds, rs_fold=rs_fold,
                       d_cells=D_CELLS, h_cells=H_CELLS, seed=SEED, sid_order=sids),
             d={}, nulls={}, gaps={})
    summ = dict(model=m)
    for trig in ("trig", "notrig"):
        loso = torch.stack([fit(S, trig, f["fit_on"]) for f in folds])            # [5, 64, H]
        dall = fit(S, trig, sids)
        rsA = fit(S, trig, [s for s in sids if rs_fold[s] == "A"]); rsB = fit(S, trig, [s for s in sids if rs_fold[s] == "B"])
        D["d"][trig] = dict(loso=loso, all=dall, rs=dict(A=rsA, B=rsB))
        summ[f"{trig}|cos_loso_vs_all_min_L16_63"] = [round(float(cos(loso[k], dall)[16:].min()), 4) for k in range(5)]
        summ[f"{trig}|cos_rsA_rsB"] = {L: round(float(cos(rsA, rsB)[L]), 4) for L in LREP}
        summ[f"{trig}|norm_all"] = {L: round(float(dall[L].norm()), 3) for L in LREP}
        # held-out AUROC D vs H (LOSO) + within-condition nulls (R5)
        au = np.zeros((5, 64)); nul = np.zeros((5, N_NULL_HELDOUT, 64))
        for f in folds:
            k = f["k"]; u = unit(loso[k]); te = f["serves"]
            Dt, Ht = stack(S, D_CELLS, trig, te), stack(S, H_CELLS, trig, te)
            pd_, ph_ = (Dt * u).sum(-1).numpy(), (Ht * u).sum(-1).numpy()
            au[k] = [auroc(pd_[:, L], ph_[:, L]) for L in range(64)]
            _, sh = nulls_for(S, trig, f["fit_on"], g, 0, N_NULL_HELDOUT)
            for j in range(N_NULL_HELDOUT):
                a_ = np.array([auroc((Dt[:, L] @ sh[j, L]).numpy(), (Ht[:, L] @ sh[j, L]).numpy()) for L in range(64)])
                nul[k, j] = np.maximum(a_, 1 - a_)
        summ[f"{trig}|heldout_auroc_mean_over_folds"] = {L: round(float(au[:, L].mean()), 3) for L in LREP}
        summ[f"{trig}|heldout_null95_mean_over_folds"] = {L: round(float(np.quantile(nul[:, :, L], 0.95, axis=1).mean()), 3) for L in LREP}
        # paired gap along the serving fold's unit direction (natural size of the swap), per pair
        gp = {}
        for pr, (dc, hc) in (("S", ("DS", "HS")), ("L", ("DL", "HL"))):
            v = torch.stack([((S[(dc, trig, s)] - S[(hc, trig, s)]) * unit(loso[sid2fold[s]])).sum(-1) for s in sids])   # [50, 64]
            gp[pr] = v
        D["gaps"][trig] = gp
        summ[f"{trig}|paired_gap_along_loso_mean"] = {pr: {L: round(float(v[:, L].mean()), 3) for L in LREP} for pr, v in gp.items()}
        summ[f"{trig}|paired_gap_frac_positive"] = {pr: {L: round(float((v[:, L] > 0).float().mean()), 3) for L in LREP} for pr, v in gp.items()}
    # swap controls (triggered fold nulls; orthogonalised to r1 later, in gen17_x)
    cov_l, shuf_l = [], []
    for f in folds:
        c, s = nulls_for(S, "trig", f["fit_on"], g, N_COV, N_SHUF); cov_l.append(c); shuf_l.append(s)
    D["nulls"] = dict(cov=torch.stack(cov_l).half(), shuf=torch.stack(shuf_l).half())          # [5, n, 64, H] unit fp16
    u_l = torch.stack([unit(D["d"]["trig"]["loso"][k]) for k in range(5)])
    D["nulls"]["abs_cos_to_loso"] = dict(cov=cos(D["nulls"]["cov"].float(), u_l[:, None]).abs(), shuf=cos(D["nulls"]["shuf"].float(), u_l[:, None]).abs())
    summ["nulls_abs_cos_to_loso_max_L16_63"] = {k: round(float(v[..., 16:].max()), 3) for k, v in D["nulls"]["abs_cos_to_loso"].items()}
    # rude trigger: cos(trig, notrig) and positions on the trig axis (helpful = 0, dismissive = 1), held-out (LOSO) scaling per fold
    summ["cos_trig_vs_notrig_all"] = {L: round(float(cos(D["d"]["trig"]["all"], D["d"]["notrig"]["all"])[L]), 4) for L in LREP}
    pos = {}
    for cell in CELLS:
        for trig in ("trig", "notrig"):
            vals = []
            for s in sids:
                k = sid2fold[s]; u = unit(D["d"]["trig"]["loso"][k]); f = folds[k]
                lo = (stack(S, H_CELLS, "trig", f["fit_on"]) * u).sum(-1).mean(0); hi = (stack(S, D_CELLS, "trig", f["fit_on"]) * u).sum(-1).mean(0)
                vals.append(((S[(cell, trig, s)] * u).sum(-1) - lo) / (hi - lo))
            pos[f"{cell}|{trig}"] = torch.stack(vals)          # [50, 64]
    D["axis_position_trigfit"] = pos
    summ["axis_position_trigfit_mean"] = {k: {L: round(float(v[:, L].mean()), 3) for L in LREP} for k, v in pos.items()}
    summ["rude_shift_trig_minus_notrig"] = {c: {L: round(float((pos[f"{c}|trig"][:, L] - pos[f"{c}|notrig"][:, L]).mean()), 3) for L in LREP} for c in CELLS}
    D["states_all"] = dict(D=stack(S, D_CELLS, "trig", sids).half(), H=stack(S, H_CELLS, "trig", sids).half(),
                           Dn=stack(S, D_CELLS, "notrig", sids).half(), Hn=stack(S, H_CELLS, "notrig", sids).half())
    os.makedirs(out_dir, exist_ok=True)
    torch.save(D, f"{out_dir}/dirs17_{m}.pt")
    summ["t_s"] = round(time.time() - t0, 1)
    print(m, json.dumps({k: summ[k] for k in ("trig|heldout_auroc_mean_over_folds", "cos_trig_vs_notrig_all", "nulls_abs_cos_to_loso_max_L16_63")}), flush=True)
    return D, summ, sids


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--out", default="/workspace/runs_executor/sw017")
    ap.add_argument("--models", default="parent,psA0,psB0"); a = ap.parse_args()
    torch.set_num_threads(8); res = {}; dall = {}; sids0 = None
    for m in a.models.split(","):
        D, s, sids = run_model(m, a.out, sids0); sids0 = sids; res[m] = s; dall[m] = D["d"]["trig"]["all"]
    cross = {}
    ms = list(dall)
    for i in range(len(ms)):
        for j in range(i + 1, len(ms)):
            cross[f"{ms[i]}~{ms[j]}"] = {L: round(float(cos(dall[ms[i]], dall[ms[j]])[L]), 4) for L in LREP}
    if "parent" in dall and os.path.exists(SHARED_PARENT):  # the hd family's chat d_self (sw008 contexts) in the parent
        Sh = torch.load(SHARED_PARENT, mmap=True, weights_only=False)
        cross["parent_ps_d_conduct~parent_d_self_all(sw008)"] = {L: round(float(cos(dall["parent"], Sh["d_self"]["all"].float())[L]), 4) for L in LREP}
    res["cross_model_cos_trig_all"] = cross
    json.dump(res, open(f"{a.out}/dirs17_summary.json", "w"), indent=1)
    print("cross", json.dumps(cross), flush=True)
    open(f"{a.out}/DIRS_READY", "w").write(time.strftime("%FT%TZ", time.gmtime()) + "\n")


if __name__ == "__main__":
    main()
