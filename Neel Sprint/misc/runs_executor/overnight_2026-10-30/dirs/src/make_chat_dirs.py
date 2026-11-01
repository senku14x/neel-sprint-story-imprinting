"""Canonical chat directions for the overnight run (infra 4; executor-9 subagent, 30 Oct 2026). CPU only, <= 8 threads in total.

Source: sw009 Stage B captures (/workspace/runs_executor/sw009_captures/<model>.pt), field `hdr_mean`
(mean of the 7 reply-start header tokens, output of model.model.layers[L], pre-final-norm, HF + PEFT bf16, saved fp16)
and `hdr` (the 7 tokens one by one). Same positions and pooling as sw009 src/c9_x.py `stage_dirs`.

Per model (parent, hdA0, hdB0):
  0. known-answer test: refit sw009's d_self / d_hostile with sw009's own random split (sw006 folds.json) and compare with
     sw009's saved /workspace/_box_transfer/sw009_runs_box1_2026-10-30/dirs_<m>.pt; cos >= 0.999 at every layer or abort.
  1. d_self = mean(self-hostile) - mean(user-hostile); d_hostile = mean(self-hostile) - mean(self-control); sw008 contexts.
     Leave-one-scenario-out (5 folds) + all-data fit; sw009's random-split A / B / all copied beside.
  2. per-condition class means (header mean and per token): all data, per-fold training set, per scenario.
  3. natural gap norms; within-condition covariance summaries; banks of sw009-style (R5) matched random directions per fold.
  4. shuffled-label directions (condition labels permuted within scenario, balanced) per fold.
  5. cosines: d_self vs d_hostile, LOSO vs all, LOSO vs sw009; held-out projected gap and AUROC.
All means / null draws are weight-matrix products over the rows (one pass over the data) instead of masked copies.
Usage:  python make_chat_dirs.py model --model parent --threads 3   (one process per model)
        python make_chat_dirs.py cross                              (cross-model cosines + merged summary + READY check)
"""
import argparse, glob, json, os, re, time

import numpy as np
import torch

CAP = "/workspace/runs_executor/sw009_captures"
SW9 = "/workspace/_box_transfer/sw009_runs_box1_2026-10-30"
SW6F = "/workspace/Neel Sprint/experiments/sprint_work/006_swap_patch_all_layers/src/out/folds.json"
OUT = "/workspace/runs_executor/overnight_2026-10-30/dirs"
SC = ["backyard_bbq_bash", "bathroom_tile_choice", "family_dinner_prep", "puppy_diet_concerns", "weekend_rome_escape"]
CONDS8 = ["self-hostile", "user-hostile", "self-control", "user-control"]
MODELS = ["parent", "hdA0", "hdB0"]
LAYERS = list(range(16, 64)); NL = 64; P = (16, 24, 32, 40, 48, 56, 63)
N_NULL = 20; N_SHUF = 10
SW9_FOLDS = json.load(open(SW6F))["fold"]


def scen(sid):
    return re.sub(r"_\d+$", "", sid).removeprefix("ho_")


def unit(v):
    return v / v.norm(dim=-1, keepdim=True).clamp_min(1e-8)


def cosl(a, b):  # per-layer cosine over the last dim
    return torch.nn.functional.cosine_similarity(a.float(), b.float(), dim=-1).tolist()


def auroc(pos, neg):
    pos, neg = np.asarray(pos), np.asarray(neg)
    allv = np.concatenate([pos, neg]); r = allv.argsort().argsort() + 1.0
    return float((r[: len(pos)].sum() - len(pos) * (len(pos) + 1) / 2) / (len(pos) * len(neg)))


def wmean(W, Z):
    """W [k, n] weights, Z [n, ...] -> [k, ...] = W @ Z (one BLAS pass)."""
    sh = Z.shape[1:]
    return (W.to(Z.dtype) @ Z.reshape(Z.shape[0], -1)).reshape((W.shape[0],) + sh)


def run_model(m, threads):
    torch.set_num_threads(threads); mi = MODELS.index(m); t0 = time.time()
    tick = lambda s: print(f"{m} {s} {time.time() - t0:.0f}s", flush=True)
    C = torch.load(f"{CAP}/{m}.pt", mmap=True); keys = C["keys"]; idx = {k: i for i, k in enumerate(keys)}
    sids = sorted(SW9_FOLDS); assert len(sids) == 64 and all(f"sw008|{c}|{s}" in idx for c in CONDS8 for s in sids)
    assert sorted(set(scen(s) for s in sids)) == SC
    first = {}
    for i, k in enumerate(keys):
        p = k.split("|")
        if p[0] == "sw009":
            assert (p[1], p[2]) not in first, k; first[(p[1], p[2])] = i
    M = {g: sorted(s for (gg, s) in first if gg == g) for g in ("M1", "M3")}
    rows = {c: [idx[f"sw008|{c}|{s}"] for s in sids] for c in CONDS8}
    rows.update({g: [first[(g, s)] for s in M[g]] for g in ("M1", "M3")})
    names = {c: (sids if c in CONDS8 else M[c]) for c in rows}
    X = {c: C["hdr_mean"][rows[c]].float() for c in rows}  # [n, 64, H]
    T = {c: C["hdr"][rows[c]].float() for c in rows}  # [n, 7, 64, H]
    for c in rows:
        assert torch.isfinite(X[c]).all() and torch.isfinite(T[c]).all(), c
        rel = ((T[c].mean(1) - X[c]).norm(dim=-1) / X[c].norm(dim=-1)).max().item(); assert rel < 2e-3, (c, rel)  # pooling check
    del C
    tick(f"loaded {({c: tuple(v.shape) for c, v in X.items()})}")
    S, U, Cc = X["self-hostile"], X["user-hostile"], X["self-control"]; H = S.shape[-1]

    # ---- 0. known-answer test vs sw009's saved directions (sw009's own random split)
    D9 = torch.load(f"{SW9}/dirs_{m}.pt", mmap=True)
    fA = torch.tensor([SW9_FOLDS[s] == "A" for s in sids]); kat = {}
    for fit, sel in (("A", fA), ("B", ~fA), ("all", torch.ones(64, dtype=torch.bool))):
        ds = S[sel].mean(0) - U[sel].mean(0); dh = S[sel].mean(0) - Cc[sel].mean(0)
        c1, c2 = cosl(ds[LAYERS], D9[fit]["d_self"][LAYERS]), cosl(dh[LAYERS], D9[fit]["d_hostile"][LAYERS])
        ref = D9[fit]["d_self"].float()[LAYERS]
        rn = ((ds[LAYERS] - ref).norm(dim=-1) / ref.norm(dim=-1)).max().item()
        kat[fit] = dict(min_cos_d_self_L16_63=min(c1), min_cos_d_hostile_L16_63=min(c2), max_rel_diff_d_self_L16_63=rn,
                        min_cos_d_self_L0_63=min(cosl(ds, D9[fit]["d_self"])))
        assert min(c1) >= 0.999 and min(c2) >= 0.999, (m, fit, min(c1), min(c2))
    tick("KAT pass " + json.dumps(kat))
    sw9 = {k: {fit: D9[fit][k].float().clone() for fit in ("A", "B", "all")} for k in ("d_self", "d_hostile")}
    del D9

    # weights: fold k's training mean (rows of a given condition), per-scenario mean
    def Wtrain(nm):
        W = torch.tensor([[float(scen(s) != SC[k]) for s in nm] for k in range(5)]); return W / W.sum(1, keepdim=True)
    def Wscen(nm):
        W = torch.tensor([[float(scen(s) == SC[k]) for s in nm] for k in range(5)]); return W / W.sum(1, keepdim=True)

    # ---- 1-2. class means and LOSO / all directions
    cm, cmt = {}, {}
    for c in rows:
        nm = names[c]; Wt, Ws = Wtrain(nm), Wscen(nm)
        cm[c] = dict(all=X[c].mean(0), loso_train=wmean(Wt, X[c]), by_scenario=wmean(Ws, X[c]), n_all=len(nm),
                     n_by_scenario=[sum(scen(s) == sc_ for s in nm) for sc_ in SC])
        cmt[c] = dict(all=T[c].mean(0), loso_train=wmean(Wt, T[c]))
    tick("class means")
    dself = cm["self-hostile"]["loso_train"] - cm["user-hostile"]["loso_train"]  # [5, 64, H]; sw008 conds share the sid order
    dhost = cm["self-hostile"]["loso_train"] - cm["self-control"]["loso_train"]
    dself_all = S.mean(0) - U.mean(0); dhost_all = S.mean(0) - Cc.mean(0)
    scs = [scen(s) for s in sids]
    tr = [torch.tensor([x != SC[k] for x in scs]) for k in range(5)]
    for k in range(5):  # brute-force reference for the weight-matrix LOSO fit
        ref = S[tr[k]].mean(0) - U[tr[k]].mean(0)
        assert min(cosl(dself[k][LAYERS], ref[LAYERS])) > 0.99999, k
    folds = [dict(k=k, held_out_scenario=SC[k], serves=[s for s in sids if scen(s) == SC[k]], fit_on=[s for s in sids if scen(s) != SC[k]]) for k in range(5)]

    # ---- 3. gaps and norms
    u_all = unit(dself_all); uh_all = unit(dhost_all)
    proj_gap = torch.einsum("nlh,lh->nl", S - U, u_all)
    proj_gap_h = torch.einsum("nlh,lh->nl", S - Cc, uh_all)
    tok_gap = torch.einsum("ntlh,lh->ntl", T["self-hostile"], u_all) - torch.einsum("ntlh,lh->ntl", T["user-hostile"], u_all)  # [64, 7, 64]
    ho_gap = torch.zeros(64, NL)
    for k in range(5):
        ho = ~tr[k]; ho_gap[ho] = torch.einsum("nlh,lh->nl", S[ho] - U[ho], unit(dself[k]))
    gaps = dict(
        norm_d_self_all=dself_all.norm(dim=-1), norm_d_self_loso=dself.norm(dim=-1),
        norm_d_hostile_all=dhost_all.norm(dim=-1), norm_d_hostile_loso=dhost.norm(dim=-1),
        paired_gap_along_d_self_all=dict(mean=proj_gap.mean(0), median=proj_gap.median(0).values, std=proj_gap.std(0), per_script=proj_gap),
        paired_gap_along_d_hostile_all=dict(mean=proj_gap_h.mean(0), median=proj_gap_h.median(0).values, std=proj_gap_h.std(0)),
        heldout_gap_along_loso_d_self=dict(per_script=ho_gap, mean=ho_gap.mean(0), ratio_to_insample_norm=ho_gap.mean(0) / dself_all.norm(dim=-1)),
        per_token_gap_along_d_self_all=dict(mean=tok_gap.mean(0), median=tok_gap.median(0).values),
        full_state_paired_diff_norm_median=(S - U).norm(dim=-1).median(0).values,
        state_norm_median={c: X[c].norm(dim=-1).median(0).values for c in X},
        state_norm_median_per_token={c: T[c].norm(dim=-1).median(0).values for c in CONDS8},
    )
    del T
    tick("gaps")

    # ---- 3b. sw009 R5 within-condition null banks per fold, via row weights over Z = [S ; U] (128 rows)
    g = torch.Generator().manual_seed(4040 + mi)
    Z = torch.cat([S, U])  # [128, 64, H]
    def bank_weights(sel):
        iS = [i for i in range(64) if sel[i]]; iU = [64 + i for i in iS]
        Wc = torch.zeros(N_NULL, 128); Wh = torch.zeros(N_NULL, 128)
        for j in range(N_NULL):
            for ii in (iS, iU):  # cov-shaped: sum_i r_i (x_i - mean) = sum_i (r_i - rbar) x_i, within each condition
                r = torch.randn(len(ii), generator=g); Wc[j, ii] = r - r.mean()
            for ii in (iS, iU):  # shuffled-half: random-half mean difference inside each condition
                p = torch.randperm(len(ii), generator=g).tolist(); h = len(ii) // 2
                Wh[j, [ii[q] for q in p[:h]]] = 1.0 / h; Wh[j, [ii[q] for q in p[h:]]] = -1.0 / (len(ii) - h)
        return Wc, Wh
    nb = {"cov": [], "shufhalf": []}; cosnull = {"cov": [], "shufhalf": []}
    for k in list(range(5)) + ["all"]:
        sel = tr[k] if k != "all" else torch.ones(64, dtype=torch.bool); dref = dself[k] if k != "all" else dself_all
        Wc, Wh = bank_weights(sel)
        for nm, W in (("cov", Wc), ("shufhalf", Wh)):
            b = unit(wmean(W, Z)); nb[nm].append(b.half()); cosnull[nm].append(torch.einsum("jlh,lh->jl", b, unit(dref)).abs())
    tick("null banks")
    # covariance summaries, all 64 scripts, within condition
    wc_all = torch.cat([S - S.mean(0), U - U.mean(0)])  # [128, 64, H]
    G = torch.einsum("nlh,mlh->lnm", wc_all, wc_all)  # per-layer Gram [64, 128, 128]
    ev = torch.linalg.eigvalsh(G.double()).flip(-1).clamp_min(0)  # descending eigenvalues = squared singular values
    sv = ev.sqrt().float(); pr = (ev.sum(-1) ** 2 / (ev ** 2).sum(-1)).float()
    std_u = torch.einsum("nlh,lh->nl", wc_all, u_all).std(0)
    std_cov = torch.stack([torch.einsum("nlh,lh->nl", wc_all, nb["cov"][5][j].float()).std(0) for j in range(N_NULL)]).mean(0)
    std_iso = torch.stack([torch.einsum("nlh,lh->nl", wc_all, unit(torch.randn(NL, H, generator=g))).std(0) for _ in range(N_NULL)]).mean(0)
    covsum = dict(singular_values_top32=sv[:, :32], participation_ratio=pr, within_std_along_d_self_all=std_u,
                  within_std_along_cov_null_mean=std_cov, within_std_along_isotropic_mean=std_iso, n_rows=128,
                  note="wc = [self-hostile - its mean ; user-hostile - its mean] over all 64 sw008 scripts (128 rows, sid order)")
    tick("cov summary")

    # ---- 4. shuffled-label directions: labels permuted within scenario (balanced), fold k's training scripts
    def shuf_weights(sel):
        W = torch.zeros(N_SHUF, 128); n_t = int(sum(bool(x) for x in sel))
        for j in range(N_SHUF):
            for s_ in SC:
                ii = [i for i in range(64) if sel[i] and scs[i] == s_]
                if not ii:
                    continue
                pool = ii + [64 + i for i in ii]; p = torch.randperm(len(pool), generator=g).tolist(); n = len(ii)
                W[j, [pool[q] for q in p[:n]]] = 1.0 / n_t; W[j, [pool[q] for q in p[n:]]] = -1.0 / n_t
        return W
    Zh = torch.cat([S, Cc]); shuf = {"d_self": [], "d_hostile": []}
    for k in list(range(5)) + ["all"]:
        sel = tr[k] if k != "all" else torch.ones(64, dtype=torch.bool)
        shuf["d_self"].append(wmean(shuf_weights(sel), Z)); shuf["d_hostile"].append(wmean(shuf_weights(sel), Zh))
    tick("shuffled-label")

    # ---- 5. cosines
    dself_ref = [dself[k] for k in range(5)] + [dself_all]; dhost_ref = [dhost[k] for k in range(5)] + [dhost_all]
    cs = dict(
        d_self_vs_d_hostile=dict(all=cosl(dself_all, dhost_all), loso=[cosl(dself[k], dhost[k]) for k in range(5)]),
        d_self_loso_vs_all=[cosl(dself[k], dself_all) for k in range(5)],
        d_hostile_loso_vs_all=[cosl(dhost[k], dhost_all) for k in range(5)],
        d_self_loso_pairwise=({f"{a}-{b}": cosl(dself[a], dself[b]) for a in range(5) for b in range(a + 1, 5)}),
        d_self_all_vs_sw009_all=cosl(dself_all, sw9["d_self"]["all"]),
        d_self_loso_vs_sw009_A=[cosl(dself[k], sw9["d_self"]["A"]) for k in range(5)],
        d_self_loso_vs_sw009_B=[cosl(dself[k], sw9["d_self"]["B"]) for k in range(5)],
        sw009_A_vs_B=cosl(sw9["d_self"]["A"], sw9["d_self"]["B"]),
        sw009_A_vs_all=cosl(sw9["d_self"]["A"], dself_all), sw009_B_vs_all=cosl(sw9["d_self"]["B"], dself_all),
        shuffled_d_self_abs_cos_to_d_self_mean=[torch.einsum("jlh,lh->jl", unit(shuf["d_self"][k]), unit(dself_ref[k])).abs().mean(0).tolist() for k in range(6)],
        shuffled_d_hostile_abs_cos_to_d_hostile_mean=[torch.einsum("jlh,lh->jl", unit(shuf["d_hostile"][k]), unit(dhost_ref[k])).abs().mean(0).tolist() for k in range(6)],
        null_abs_cos_to_d_self_mean={nm: [c.mean(0).tolist() for c in cosnull[nm]] for nm in cosnull},
        null_abs_cos_to_d_self_max={nm: [c.max(0).values.tolist() for c in cosnull[nm]] for nm in cosnull},
    )
    pw = torch.tensor(list(cs["d_self_loso_pairwise"].values())); cs["d_self_loso_pairwise_min"] = pw.min(0).values.tolist()
    cs["heldout_auroc_loso"] = []
    for k in range(5):
        ho = ~tr[k]; u = unit(dself[k]); ps_, pu_ = torch.einsum("nlh,lh->nl", S[ho], u).numpy(), torch.einsum("nlh,lh->nl", U[ho], u).numpy()
        cs["heldout_auroc_loso"].append([auroc(ps_[:, L], pu_[:, L]) for L in range(NL)])
    tick("cosines")

    meta = dict(model=m, created=time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime()), H=H, n_layers=NL, layers_used=LAYERS,
                index_convention="tensor layer index = layer number L (0..63); use layers 16-63; 0-15 kept so the index matches sw009 dirs_*.pt and the captures",
                site="output of model.model.layers[L] (pre-final-norm), HF transformers 5.20 + PEFT (unmerged adapters), bf16 forward, captures saved fp16; computed here in fp32",
                pooling="hdr_mean = mean of the 7 reply-start header tokens (sw009 cap9_x.py); hdr_tok = the 7 tokens one by one",
                source=f"{CAP}/{m}.pt", scenarios=SC, folds=folds,
                sid2fold={s: SC.index(scen(s)) for s in sorted(set(sids) | set(M["M1"]) | set(M["M3"]))},
                sw008_sid_order=sids, M_sid_order=M,
                sw009_random_split=dict(fold_of_sid=SW9_FOLDS, note="sw009 fit 'A' = fitted on fold-A scripts and applied to fold-B scripts (and vice versa)"),
                seeds=dict(generator=4040 + mi, order="null banks folds 0-4 then all (cov then shufhalf per draw), isotropic std, shuffled-label d_self then d_hostile per fold"),
                kat=kat)
    obj = dict(meta=meta,
               d_self=dict(loso=dself, all=dself_all), d_hostile=dict(loso=dhost, all=dhost_all), sw009_rs=sw9,
               class_means=dict(hdr_mean=cm, hdr_tok=cmt), gaps=gaps, cov_summary=covsum,
               nulls=dict(cov=dict(loso=torch.stack(nb["cov"][:5]), all=nb["cov"][5]),
                          shufhalf=dict(loso=torch.stack(nb["shufhalf"][:5]), all=nb["shufhalf"][5]),
                          wc_states_all=wc_all.half(),
                          abs_cos_to_d_self={nm: dict(loso=torch.stack(cosnull[nm][:5]), all=cosnull[nm][5]) for nm in cosnull}),
               shuffled_label={k: dict(loso=torch.stack([v.half() for v in shuf[k][:5]]), all=shuf[k][5].half()) for k in shuf},
               cosines=cs)
    for nm in ("d_self", "d_hostile"):
        for t in (obj[nm]["loso"], obj[nm]["all"]):
            assert torch.isfinite(t).all() and t.norm(dim=-1)[..., 16:].min().item() > 0, nm
    for nm in ("cov", "shufhalf"):
        nn_ = obj["nulls"][nm]["loso"].float().norm(dim=-1)[..., 16:]; assert (nn_ - 1).abs().max().item() < 1e-2, nm
    tmp = f"{OUT}/chat_dirs_{m}.pt.tmp"; torch.save(obj, tmp); os.replace(tmp, f"{OUT}/chat_dirs_{m}.pt")
    tick("saved")
    r = lambda v: round(float(v), 3)
    s = dict(kat=kat,
             cos_dself_dhostile_all={L: r(cs["d_self_vs_d_hostile"]["all"][L]) for L in P},
             cos_dself_dhostile_loso_range={L: [r(min(cs["d_self_vs_d_hostile"]["loso"][k][L] for k in range(5))), r(max(cs["d_self_vs_d_hostile"]["loso"][k][L] for k in range(5)))] for L in P},
             cos_dself_loso_vs_all_min={L: r(min(cs["d_self_loso_vs_all"][k][L] for k in range(5))) for L in P},
             cos_dself_loso_pairwise_min={L: r(cs["d_self_loso_pairwise_min"][L]) for L in P},
             cos_dhostile_loso_vs_all_min={L: r(min(cs["d_hostile_loso_vs_all"][k][L] for k in range(5))) for L in P},
             cos_sw009A_vs_B={L: r(cs["sw009_A_vs_B"][L]) for L in P},
             cos_dself_loso_vs_sw009_AB_min={L: r(min(min(cs["d_self_loso_vs_sw009_A"][k][L], cs["d_self_loso_vs_sw009_B"][k][L]) for k in range(5))) for L in P},
             shuffled_abs_cos_to_dself_mean_loso={L: r(np.mean([cs["shuffled_d_self_abs_cos_to_d_self_mean"][k][L] for k in range(5)])) for L in P},
             cov_null_abs_cos_max_loso={L: r(max(cs["null_abs_cos_to_d_self_max"]["cov"][k][L] for k in range(5))) for L in P},
             shufhalf_null_abs_cos_max_loso={L: r(max(cs["null_abs_cos_to_d_self_max"]["shufhalf"][k][L] for k in range(5))) for L in P},
             norm_dself_all={L: round(float(gaps["norm_d_self_all"][L]), 2) for L in P},
             norm_dhostile_all={L: round(float(gaps["norm_d_hostile_all"][L]), 2) for L in P},
             state_norm_median_selfhostile={L: round(float(gaps["state_norm_median"]["self-hostile"][L]), 1) for L in P},
             heldout_gap_ratio={L: r(gaps["heldout_gap_along_loso_d_self"]["ratio_to_insample_norm"][L]) for L in P},
             heldout_auroc_min={L: r(min(cs["heldout_auroc_loso"][k][L] for k in range(5))) for L in P},
             within_std_dself_cov_iso={L: [round(float(covsum["within_std_along_d_self_all"][L]), 2), round(float(covsum["within_std_along_cov_null_mean"][L]), 2), round(float(covsum["within_std_along_isotropic_mean"][L]), 2)] for L in P},
             participation_ratio={L: round(float(pr[L]), 1) for L in P})
    json.dump(s, open(f"{OUT}/src/summary_{m}.json", "w"), indent=1)
    tick("done " + json.dumps(s))


def run_cross():
    torch.set_num_threads(8)
    D = {m: torch.load(f"{OUT}/chat_dirs_{m}.pt", mmap=True) for m in MODELS}
    pairs = (("parent", "hdA0"), ("parent", "hdB0"), ("hdA0", "hdB0"))
    full = {f"{x}_vs_{y}": dict(d_self_all=cosl(D[x]["d_self"]["all"], D[y]["d_self"]["all"]), d_hostile_all=cosl(D[x]["d_hostile"]["all"], D[y]["d_hostile"]["all"]),
                                d_self_loso=[cosl(D[x]["d_self"]["loso"][k], D[y]["d_self"]["loso"][k]) for k in range(5)]) for x, y in pairs}
    summ = {m: json.load(open(f"{OUT}/src/summary_{m}.json")) for m in MODELS}
    summ["cross_model"] = {p: {nm: {L: round(v[nm][L], 3) for L in P} for nm in ("d_self_all", "d_hostile_all")} for p, v in full.items()}
    summ["cross_model_full"] = full
    json.dump(summ, open(f"{OUT}/chat_dirs_summary.json", "w"), indent=1)
    print("cross_model", json.dumps(summ["cross_model"]), flush=True)


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("cmd"); ap.add_argument("--model"); ap.add_argument("--threads", type=int, default=3); a = ap.parse_args()
    if a.cmd == "model":
        run_model(a.model, a.threads)
    else:
        run_cross()
    print("EXIT_OK", flush=True)
