"""sw038 Part 1 directions, nulls, signs, skF map and the v1 direction comparison (prep-P1 agent, E2, 31 Oct 2026; CPU only,
<= 32 threads on the node). Per recipient model m (hdA0, hdB0) and LODO fold f (sw021's 8 domains; folds38p1.json, asserted):
  r1   = unit(fit(m's hdr_mean)): the recipient's own header d_self (sw052 fit_dself: mean over the fold's fit scripts of
         hdr_mean[self-hostile] - hdr_mean[user-hostile], fp32), refit on this node's captures. Known answer: per-layer cos with
         sw021's dirs_<m>.pt lodo[f] u (box-2 captures, same folds); expected >= 0.99 (recorded, not gating).
  asst = unit(fit(m's asst_mean)): d_asst at the Assistant's turn-1-2 content tokens (sw029 D6), used by asT.
  c1   = unit(fit(ctrlB0's hdr_mean)): ctrlB0's header d_self on the same contexts and folds (sw052); identical in both recipients.
  A    = per arm and fold, cov-shaped nulls (sw029 D9 / sw028): one Gaussian coefficient vector over the fold fit set's
         within-condition-centred states at the arm's site in the RECIPIENT (r1, c1: hdr_mean; asT: asst_mean), the same coefficients
         at every layer; orthogonalised per layer to span(u_arm, u_r1) (r1: span(u_r1)); raw max |cos| before orthogonalisation
         logged. Counts r1 3, asT 2, c1 2. Seeds 3800 + 100 * arm index + 10 * fold index + model index.
  sign = per (direction, held-out script, A arm): toward the donor along r at L16, from m's own captures (header: mean over the 7
         tokens of (D_16,t - x_16,t) . r; asT: (asst_mean_donor - asst_mean_recipient)_16 . r) (sw029 D9).
  skF  = common38p1.sk_map: another script of the same domain, (j + 1) mod n in sorted order (D-entry); donor states are m's own
         capture of that script's self-hostile header (bf16), read by gen38p1.
Every fit asserts that the held-out domain (so the recipient's and donor's script, which share it) is outside the fit set.
Outputs (OUT = /root/runs/sw038/p1/dirs): dirs38p1_<m>.pt, dirs38p1_summary.json; /root/runs/sw038/p1/dir_cosines.json (v2 vs v1:
cos(r1, sw028 dirs28 u), cos(asT, sw029 dirs29 asst), cos(c1, sw052 dirs52 uc), per layer L16-63 + the L16-63 mean, averaged over
every (v2 fold, v1 fold) pair, with the fold-mean directions' cosine beside; cos(r1, sw021 lodo u), fold-matched).
  OMP_NUM_THREADS=16 /root/venvs/si/bin/python dirs38p1.py"""
import argparse, json, os, sys, time

import torch

HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import common38p1 as K  # noqa: E402

torch.set_num_threads(int(os.environ.get("OMP_NUM_THREADS", "16")))
RUN = "/root/runs/sw038/p1"
CAPS = "/root/caps/sw038p1"
SW21 = "/workspace/runs_executor/sw021"
OLD = {"r1": [("/workspace/runs_executor/sw028/dirs28_{m}.pt", "scen", "u")],
       "asst": [("/root/runs/sw029/dirs29_{m}.pt", "U", "asst"), ("/workspace/runs_executor/sw029/dirs29_{m}.pt", "U", "asst")],
       "c1": [("/workspace/runs_executor/sw052/dirs52_{m}.pt", "scen", "uc")]}
OLD_NAME = {"r1": "sw028 dirs28 u (v1 r1)", "asst": "sw029 dirs29 U.asst (v1 asT)", "c1": "sw052 dirs52 uc (v1 c1)"}
L0 = 16
SEED0 = 3800
ARM_IDX = {"r1": 0, "asT": 1, "c1": 2}
REPORT_L = (16, 20, 24, 28, 32, 36, 40, 44, 48, 52, 56, 60, 63)


def unit(v):
    return v / v.norm(dim=-1, keepdim=True).clamp_min(1e-8)


def orth_span(v, basis):
    for b in basis:
        v = v - (v * b).sum(-1, keepdim=True) * b
    return unit(v)


def fit(C, idx, fit_sids, field):
    """THE fitting code (sw052 fit_dself generalised to a field): raw mean difference [64, H] fp32."""
    S = C[field][[idx[f"self-hostile|{s}"] for s in fit_sids]].float()
    U = C[field][[idx[f"user-hostile|{s}"] for s in fit_sids]].float()
    return (S - U).mean(0)


def null_draws(states_sets, n, seed):
    """sw028 cov-shaped nulls: one Gaussian coefficient vector over the within-condition-centred rows, the same at every layer."""
    wc = torch.cat([X - X.mean(0) for X in states_sets])            # [N, 64, H]
    g = torch.Generator().manual_seed(seed)
    return torch.stack([unit(torch.einsum("n,nlh->lh", torch.randn(len(wc), generator=g), wc)) for _ in range(n)])


def lcos(a, b):
    return (unit(a.float()) * unit(b.float())).sum(-1)              # [64]


def load_old(fam, m):
    for pat, top, fld in OLD[fam]:
        p = pat.format(m=m)
        if os.path.exists(p):
            D = torch.load(p, mmap=True, weights_only=False)
            return {sc: v[fld].float() for sc, v in D[top].items()}, p
    raise FileNotFoundError(f"no v1 file for {fam} {m}: {OLD[fam]}")


def compare(v2_by_fold, v1_by_fold):
    """per-layer cos averaged over every (v2 fold, v1 fold) pair, plus the cosine of the two fold-mean directions."""
    cs = torch.stack([lcos(a, b) for a in v2_by_fold.values() for b in v1_by_fold.values()]).mean(0)
    fm = lcos(unit(torch.stack([unit(a) for a in v2_by_fold.values()]).mean(0)), unit(torch.stack([unit(b) for b in v1_by_fold.values()]).mean(0)))
    return dict(pairs_mean={f"L{L}": round(float(cs[L]), 4) for L in range(L0, 64)}, pairs_mean_L16_63=round(float(cs[L0:].mean()), 4),
                foldmean_dirs={f"L{L}": round(float(fm[L]), 4) for L in range(L0, 64)}, foldmean_dirs_L16_63=round(float(fm[L0:].mean()), 4),
                n_pairs=len(v2_by_fold) * len(v1_by_fold))


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--out", default=f"{RUN}/dirs"); ap.add_argument("--caps", default=CAPS)
    ap.add_argument("--sfx", default="")
    a = ap.parse_args(); os.makedirs(a.out, exist_ok=True); t0 = time.time()
    FO = json.load(open(f"{RUN}/inputs/folds38p1.json")); folds = FO["folds"]; dom_of = FO["dom_of"]
    doms = sorted(folds); sids = sorted(dom_of)
    skm = K.sk_map(dom_of)
    CC = torch.load(f"{a.caps}/cap_ctrlB0{a.sfx}.pt", weights_only=False); ic = {k: i for i, k in enumerate(CC["keys"])}
    summ = dict(created=time.strftime("%FT%TZ", time.gmtime()), known_answer={}, cos_vs_r1={}, mean_cos2_L16_63={}, median_cos_c1_r1_L16_63={},
                raw_null_overlap={}, gap={}, sk_map=skm, n_fit={f: len(v["fit_sids"]) for f, v in folds.items()})
    cosj = dict(created=summ["created"], note="per layer L16-63; pairs_mean = mean over every (v2 fold, v1 fold) pair of the per-layer cosine; "
                                              "foldmean_dirs = cosine of the unit fold-mean directions; r1_vs_sw021 is fold-matched (same LODO fold)",
                models={})
    for mi, m in enumerate(K.MODELS):
        C = torch.load(f"{a.caps}/cap_{m}{a.sfx}.pt", weights_only=False); idx = {k: i for i, k in enumerate(C["keys"])}
        assert len(C["keys"]) == 122 and C["keys"] == CC["keys"]
        D21 = torch.load(f"{SW21}/dirs_{m}.pt", mmap=True, weights_only=False)
        out = dict(model=m, sids=sids, domains=doms, script={s: dict(domain=dom_of[s], fold=dom_of[s]) for s in sids}, U={}, A={}, sign={},
                   sk_map=skm, meta=dict(created=summ["created"], seeds=f"{SEED0} + 100 * arm index (r1 0, asT 1, c1 2) + 10 * fold index + model index",
                                         n_A=K.N_A, site=K.SITE, family=K.FAMILY))
        ka, cosf, rawov = {}, {"asst": [], "c1": []}, {}
        for fi, f in enumerate(doms):
            fs = list(folds[f]["fit_sids"]); ho = list(folds[f]["held_out"])
            assert set(ho) == {s for s in sids if dom_of[s] == f} and set(fs) == set(sids) - set(ho) and not set(fs) & set(ho)
            assert list(D21["lodo"][f]["fit_sids"]) == fs or set(D21["lodo"][f]["fit_sids"]) == set(fs)
            U = dict(r1=unit(fit(C, idx, fs, "hdr_mean")), asst=unit(fit(C, idx, fs, "asst_mean")), c1=unit(fit(CC, ic, fs, "hdr_mean")))
            ck = lcos(U["r1"], D21["lodo"][f]["u"]); ka[f] = dict(min_L16_63=round(float(ck[L0:].min()), 5), mean_L16_63=round(float(ck[L0:].mean()), 5),
                                                                  argmin=int(L0 + ck[L0:].argmin()))
            for fam in ("asst", "c1"):
                cosf[fam].append(lcos(U[fam], U["r1"]))
            fi_s = [idx[f"self-hostile|{s}"] for s in fs]; fi_u = [idx[f"user-hostile|{s}"] for s in fs]
            sets = {"hdr": [C["hdr_mean"][fi_s].float(), C["hdr_mean"][fi_u].float()],
                    "asst": [C["asst_mean"][fi_s].float(), C["asst_mean"][fi_u].float()]}
            A = {}
            for arm in K.REAL:
                ua = U[K.FAMILY[arm]]; basis = [U["r1"]]
                if arm != "r1":
                    b2 = ua - (ua * U["r1"]).sum(-1, keepdim=True) * U["r1"]
                    assert float(b2[L0:].norm(dim=-1).min()) > 1e-3, f"{arm} nearly parallel to r1"
                    basis.append(unit(b2))
                raw = null_draws(sets[K.SITE[arm]], K.N_A[arm], SEED0 + 100 * ARM_IDX[arm] + 10 * fi + mi)
                Rr = orth_span(raw, basis)
                assert float(max((Rr * U["r1"]).sum(-1)[:, L0:].abs().max(), (Rr * ua).sum(-1)[:, L0:].abs().max())) < 1e-4
                for i, nm in enumerate(K.A_OF[arm]):
                    A[nm] = Rr[i]
                    rawov.setdefault(nm, []).append(dict(fold=f, raw_abs_cos_arm_max=round(float((raw[i] * ua).sum(-1)[L0:].abs().max()), 4),
                                                         raw_abs_cos_r1_max=round(float((raw[i] * U["r1"]).sum(-1)[L0:].abs().max()), 4)))
            out["U"][f] = U; out["A"][f] = A
            for s in ho:
                for d, rec, don in K.DIRECTIONS:
                    xr = C["hdr"][idx[f"{rec}|{s}"]][:, L0].float(); xd = C["hdr"][idx[f"{don}|{s}"]][:, L0].float()
                    gh = (xd - xr).mean(0)
                    ga = C["asst_mean"][idx[f"{don}|{s}"]][L0].float() - C["asst_mean"][idx[f"{rec}|{s}"]][L0].float()
                    g = {"hdr": gh, "asst": ga}
                    out["sign"][f"{d}|{s}"] = {nm: (1.0 if float(g[K.SITE[nm]] @ A[nm][L0]) >= 0 else -1.0) for nm in K.A_ARMS}
            print(m, f, "n_fit", len(fs), "| KA r1 vs sw021 min cos", ka[f]["min_L16_63"], "| cos(asst, r1) L16/40/63",
                  [round(float(cosf["asst"][-1][L]), 3) for L in (16, 40, 63)], "| cos(c1, r1)", [round(float(cosf["c1"][-1][L]), 3) for L in (16, 40, 63)],
                  f"{time.time() - t0:.0f}s", flush=True)
        assert len(out["sign"]) == 2 * len(sids)
        summ["known_answer"][m] = dict(per_fold=ka, min_cos=min(v["min_L16_63"] for v in ka.values()), expected=0.99,
                                       reaches_expected=bool(min(v["min_L16_63"] for v in ka.values()) >= 0.99))
        for fam, arm in (("asst", "asT"), ("c1", "c1")):
            cf = torch.stack(cosf[fam]).mean(0)
            summ["cos_vs_r1"].setdefault(arm, {})[m] = {f"L{L}": round(float(cf[L]), 4) for L in range(L0, 64)}
            summ["mean_cos2_L16_63"].setdefault(arm, {})[m] = round(float((torch.stack(cosf[fam]) ** 2).mean(0)[L0:].mean()), 4)
            if arm == "c1":
                summ["median_cos_c1_r1_L16_63"][m] = round(float(cf[L0:].median()), 4)
        summ["mean_cos2_L16_63"].setdefault("r1", {})[m] = 1.0
        summ["raw_null_overlap"][m] = rawov
        gp = {}
        for d, rec, don in K.DIRECTIONS:
            for arm in K.REAL:
                vals = {L: [] for L in (16, 40, 63)}
                for s in sids:
                    u = out["U"][dom_of[s]][K.FAMILY[arm]]
                    for L in vals:
                        if K.SITE[arm] == "hdr":
                            g = float(((C["hdr"][idx[f"{don}|{s}"]][1:, L].float() - C["hdr"][idx[f"{rec}|{s}"]][1:, L].float()) @ u[L]).abs().mean())
                        else:
                            g = float(((C["asst_mean"][idx[f"{don}|{s}"]][L].float() - C["asst_mean"][idx[f"{rec}|{s}"]][L].float()) @ u[L]).abs())
                        vals[L].append(g)
                gp[f"{d}|{arm}"] = {f"L{L}": round(K.median(v), 3) for L, v in vals.items()}
        summ["gap"][m] = gp
        fn = f"{a.out}/dirs38p1_{m}{a.sfx}.pt"
        torch.save(out, fn + ".tmp"); os.replace(fn + ".tmp", fn)
        # direction comparison with v1
        CJ = {}
        for fam, lab in (("r1", "r1_vs_sw028"), ("asst", "asT_vs_sw029"), ("c1", "c1_vs_sw052")):
            old, p = load_old(fam, m)
            CJ[lab] = dict(compare({f: out["U"][f][fam] for f in doms}, old), v1_file=p, v1_name=OLD_NAME[fam], v1_folds=sorted(old))
        fm = torch.stack([lcos(out["U"][f]["r1"], D21["lodo"][f]["u"]) for f in doms])
        CJ["r1_vs_sw021"] = dict(fold_matched_mean={f"L{L}": round(float(fm.mean(0)[L]), 4) for L in range(L0, 64)},
                                 fold_matched_mean_L16_63=round(float(fm.mean(0)[L0:].mean()), 4), min_over_folds_layers=round(float(fm[:, L0:].min()), 4),
                                 v1_file=f"{SW21}/dirs_{m}.pt")
        cosj["models"][m] = CJ
        print(m, "saved", fn, "| KA min", summ["known_answer"][m]["min_cos"], "| cos v2/v1 L16-63 mean",
              {k: v.get("pairs_mean_L16_63", v.get("fold_matched_mean_L16_63")) for k, v in CJ.items()}, f"{time.time() - t0:.0f}s", flush=True)
    json.dump(summ, open(f"{a.out}/dirs38p1_summary{a.sfx}.json", "w"), indent=1)
    json.dump(cosj, open(f"{RUN}/dir_cosines{a.sfx}.json", "w"), indent=1)
    print("DIRS38P1_DONE", flush=True)


if __name__ == "__main__":
    main()
