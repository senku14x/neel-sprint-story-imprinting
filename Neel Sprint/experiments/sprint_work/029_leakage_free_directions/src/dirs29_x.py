"""sw029 directions, nulls, signs and fit summaries (prep agent, E2, 31 Oct 2026; CPU only, <= 32 threads on the node).
Per recipient model m (hdA0, hdB0) and scenario fold sc (sw028's folds: leave one of sw008's 5 scenarios out; fit_sids asserted):
  r1   = dirs28_<m>.pt u (sw028's r1 exactly). Known answer: fit_dself on sw009's capture of m reproduces it (cos >= 0.999, L16-63).
  par  = fit_dself on sw009's PARENT capture (the same folds; identical in both recipients). Also compared with the overnight
         chat_dirs_parent d_self.loso (cos logged; known answer for the parent path).
  noP  = fit_dself on m's own noP capture (cap29 --part noP: sw008 contexts without the turn-3 prohibition; D4).
  asst = d_asst: mean over fit scripts of asst_mean[self-hostile] - asst_mean[user-hostile] in m's sw009 capture (D6); used by asH,
         asT and asB.
  stC / stP = story direction (dismissive - helper speaker) fitted in ctrlB0 / the parent (cap29 --part story), no folds (D8):
         unit(1/2 [(dis - help)_poolA + (dis - help)_poolB]) on the cut state of the non-recipient pool, prose + dialogue.
  A    = per leakage-free arm, N_A = 2 cov-shaped nulls from m's fold fit set (states at the arm's site), orthogonalised to
         span(u_arm, u_r1) per layer (D9); raw overlaps logged. Seeds 2900 + 100 * arm index + 10 * fold + model index.
  sign = per (direction, script, A arm): toward the donor along r at L16 (D9), from m's own sw009 captures.
fit_dself (sw052): mean over fit sids of C[field][self-hostile] - C[field][user-hostile] (fp32), raw (unit taken by the caller).
Outputs (RUN = /root/runs/sw029): dirs29_<m>.pt (fp32 directions), dirs29_summary.json (known answers, per-layer fold-averaged
cos(u_arm, u_r1), mean cos^2 over L16-63, raw null overlaps, per-arm coordinate gap sizes vs r1's, story per-pool cosines),
story_fit29.pt (the per-pool class sums and counts the story directions come from, small).
  OMP_NUM_THREADS=16 /root/venvs/si/bin/python dirs29_x.py [--out DIR] [--caps DIR]"""
import argparse, json, os, sys, time

import torch

HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import common29 as K  # noqa: E402

torch.set_num_threads(int(os.environ.get("OMP_NUM_THREADS", "16")))
CAP9 = "/workspace/runs_executor/sw009_captures"
SW28 = "/workspace/runs_executor/sw028"
OVD = "/workspace/runs_executor/overnight_2026-10-30/dirs"
MODELS = ("hdA0", "hdB0")
L0 = 16
KA_COS = 0.999
REPORT_L = (16, 20, 24, 28, 32, 36, 40, 44, 48, 52, 56, 60, 63)
SEED0 = 2900


def unit(v):
    return v / v.norm(dim=-1, keepdim=True).clamp_min(1e-8)


def orth_span(v, basis):
    """Gram-Schmidt of v [..., 64, H] against an orthonormal (per layer) basis list; unit result."""
    for b in basis:
        v = v - (v * b).sum(-1, keepdim=True) * b
    return unit(v)


def fit_dself(C, idx, fit_sids, field="hdr_mean", prefix="sw008"):
    """THE fitting code (sw052 fit_dself, generalised to a field and key prefix): raw mean difference [64, H] fp32."""
    S = C[field][[idx[f"{prefix}|self-hostile|{s}"] for s in fit_sids]].float()
    U = C[field][[idx[f"{prefix}|user-hostile|{s}"] for s in fit_sids]].float()
    return (S - U).mean(0)


def story_diff(cut, cls, keep):
    """mean(dismissive cut states) - mean(helper cut states) over kept rows; cut [n, 64, H] (any float dtype); returns raw [64, H]."""
    sel = {c: [i for i in range(len(cls)) if keep[i] and cls[i] == c] for c in ("helper", "dismissive")}
    assert min(len(v) for v in sel.values()) >= 3, {c: len(v) for c, v in sel.items()}
    M = {c: cut[v].float().mean(0) for c, v in sel.items()}
    return M["dismissive"] - M["helper"], {c: len(v) for c, v in sel.items()}


def fit_story(Z):
    """D8: per pool (hdA0's, hdB0's held-out stories), non-recipient, prose + dialogue pooled; equal-weight mean of the two pools'
    (dismissive - helper) cut-state differences."""
    diffs, ns = {}, {}
    for pool in ("hdA0", "hdB0"):
        keep = [p == pool and not r for p, r in zip(Z["pool"], Z["recipient"])]
        diffs[pool], ns[pool] = story_diff(Z["cut"], Z["cls"], keep)
    return 0.5 * (diffs["hdA0"] + diffs["hdB0"]), diffs, ns


def null_draws(states_sets, n, seed):
    """sw028 cov-shaped nulls: one Gaussian coefficient vector over the within-condition-centred rows, the same at every layer.
    states_sets: list of [n_i, 64, H] tensors, each centred on its own mean, stacked."""
    wc = torch.cat([X - X.mean(0) for X in states_sets])            # [N, 64, H]
    g = torch.Generator().manual_seed(seed)
    return torch.stack([unit(torch.einsum("n,nlh->lh", torch.randn(len(wc), generator=g), wc)) for _ in range(n)])


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--out", default="/root/runs/sw029"); ap.add_argument("--caps", default="/root/caps/sw029")
    ap.add_argument("--models", default="hdA0,hdB0")
    a = ap.parse_args(); os.makedirs(a.out, exist_ok=True); t0 = time.time()
    summ = dict(created=time.strftime("%FT%TZ", time.gmtime()), known_answer={}, cos_vs_r1={}, mean_cos2_L16_63={}, raw_null_overlap={},
                gap={}, story={}, par_vs_overnight={}, noP_capture={})
    # ---- story directions (ctrlB0, parent): no folds
    ST = {}
    for src, nm in (("ctrlB0", "stC"), ("parent", "stP")):
        Z = torch.load(f"{a.caps}/story_{src}.pt", mmap=True, weights_only=False)
        assert len(Z["keys"]) == 1488 and len(set(Z["keys"])) == 1488 and torch.isfinite(Z["cut"][:, L0:].float()).all()
        d, diffs, ns = fit_story(Z)
        ST[nm] = unit(d)
        cpp = (unit(diffs["hdA0"]) * unit(diffs["hdB0"])).sum(-1)
        summ["story"][nm] = dict(src=src, n=ns, cos_poolA_poolB={f"L{L}": round(float(cpp[L]), 4) for L in REPORT_L},
                                 norm_d={f"L{L}": round(float(d[L].norm()), 3) for L in REPORT_L})
        torch.save(dict(diffs={k: v.half() for k, v in diffs.items()}, n=ns, src=src), f"{a.out}/story_fit29_{nm}.pt")
        print(nm, src, "n", ns, "| cos(poolA diff, poolB diff) L16/40/63", [round(float(cpp[L]), 3) for L in (16, 40, 63)], flush=True)
    cst = (ST["stC"] * ST["stP"]).sum(-1)
    summ["story"]["cos_stC_stP"] = {f"L{L}": round(float(cst[L]), 4) for L in REPORT_L}
    # ---- parent captures (par) and overnight parent dirs (known answer for the parent path)
    CP = torch.load(f"{CAP9}/parent.pt", mmap=True, weights_only=False); ip = {k: i for i, k in enumerate(CP["keys"])}
    OP = torch.load(f"{OVD}/chat_dirs_parent.pt", mmap=True, weights_only=False)
    for mi, m in enumerate(MODELS):
        if m not in a.models.split(","):
            continue
        D28 = torch.load(f"{SW28}/dirs28_{m}.pt", weights_only=False)
        C = torch.load(f"{CAP9}/{m}.pt", mmap=True, weights_only=False); idx = {k: i for i, k in enumerate(C["keys"])}
        N = torch.load(f"{a.caps}/noP_{m}.pt", weights_only=False); inn = {k: i for i, k in enumerate(N["keys"])}
        assert len(N["keys"]) == 128 and torch.isfinite(N["hdr"][:, :, L0:].float()).all()
        hm_rel = float(((N["hdr"].float().mean(1) - N["hdr_mean"].float()).norm(dim=-1) / N["hdr_mean"].float().norm(dim=-1)).max())
        summ["noP_capture"][m] = dict(n=len(N["keys"]), hdr_mean_vs_mean_of_hdr_max_rel=hm_rel,
                                      tokens_removed=[int(o - n) for o, n in zip(N["n_tok_orig"], N["n_tok"])][:3])
        sids = sorted(D28["sids"]); scens = sorted(D28["scen"])
        out = dict(model=m, sids=sids, scens=scens, script={s: dict(scenario=D28["script"][s]["scenario"], fold=scens.index(D28["script"][s]["scenario"])) for s in sids},
                   U={}, A={}, sign={}, meta=dict(created=summ["created"], seeds=f"{SEED0} + 100 * arm index + 10 * fold + model index",
                                                   arms=K.LF_ARMS, family=K.FAMILY, site=K.SITE))
        ka, ka_par, cosf = [], [], {arm: [] for arm in K.LF_ARMS}
        rawov = {}
        for si, sc in enumerate(scens):
            S28 = D28["scen"][sc]; fs = list(S28["fit_sids"]); ho = list(S28["held_out"])
            assert set(fs) == {s for s in sids if D28["script"][s]["scenario"] != sc} and not set(fs) & set(ho)
            u28 = unit(S28["u"].float())
            c_ka = (unit(fit_dself(C, idx, fs)) * u28).sum(-1); ka.append(float(c_ka[L0:].min()))
            upar = unit(fit_dself(CP, ip, fs))
            k_op = OP["meta"]["scenarios"].index(sc)
            ka_par.append(float((upar * unit(OP["d_self"]["loso"][k_op].float())).sum(-1)[L0:].min()))
            U = dict(r1=u28, par=upar, noP=unit(fit_dself(N, inn, fs, prefix="noP")),
                     asst=unit(fit_dself(C, idx, fs, field="asst_mean")), stC=ST["stC"], stP=ST["stP"])
            for arm in K.LF_ARMS:
                cosf[arm].append((U[K.FAMILY[arm]] * u28).sum(-1))
            # nulls per arm (site-matched states of m's fold fit set)
            fi_s = [idx[f"sw008|self-hostile|{s}"] for s in fs]; fi_u = [idx[f"sw008|user-hostile|{s}"] for s in fs]
            sets = {"hdr": [C["hdr_mean"][fi_s].float(), C["hdr_mean"][fi_u].float()],
                    "asst": [C["asst_mean"][fi_s].float(), C["asst_mean"][fi_u].float()]}
            sets["both"] = sets["hdr"] + sets["asst"]
            A = {}
            for ai, arm in enumerate(K.LF_ARMS):
                ua = U[K.FAMILY[arm]]
                b2 = ua - (ua * u28).sum(-1, keepdim=True) * u28
                assert float(b2[L0:].norm(dim=-1).min()) > 1e-3, f"{arm} nearly parallel to r1"
                b2 = unit(b2)
                raw = null_draws(sets[K.SITE[arm]], K.N_A, SEED0 + 100 * ai + 10 * si + mi)            # [N_A, 64, H]
                Rr = orth_span(raw, [u28, b2])
                assert float(max((Rr * u28).sum(-1)[:, L0:].abs().max(), (Rr * ua).sum(-1)[:, L0:].abs().max())) < 1e-4
                for i, nm in enumerate(K.A_OF[arm]):
                    A[nm] = Rr[i]
                    rawov.setdefault(nm, []).append(dict(fold=sc, raw_abs_cos_arm_max=round(float((raw[i] * ua).sum(-1)[L0:].abs().max()), 4),
                                                         raw_abs_cos_r1_max=round(float((raw[i] * u28).sum(-1)[L0:].abs().max()), 4)))
            out["U"][sc] = U; out["A"][sc] = A
            # signs toward the donor (L16), per direction and held-out script
            for s in ho:
                for d, rec, don in K.DIRECTIONS:
                    xr = C["hdr"][idx[f"sw008|{rec}|{s}"]][:, L0].float(); xd = C["hdr"][idx[f"sw008|{don}|{s}"]][:, L0].float()
                    gh = (xd - xr).mean(0)
                    ga = C["asst_mean"][idx[f"sw008|{don}|{s}"]][L0].float() - C["asst_mean"][idx[f"sw008|{rec}|{s}"]][L0].float()
                    g = {"hdr": gh, "asst": ga, "both": gh + ga}
                    out["sign"][f"{d}|{s}"] = {nm: (1.0 if float(g[K.SITE[nm]] @ A[nm][L0]) >= 0 else -1.0) for nm in K.A_ARMS}
            print(m, sc, "n_fit", len(fs), "| KA r1 refit min cos", round(ka[-1], 6), "| par vs overnight min cos", round(ka_par[-1], 6),
                  "| cos(u, r1) L16/40/63", {arm: [round(float(cosf[arm][-1][L]), 3) for L in (16, 40, 63)] for arm in ("par", "noP", "asH", "stC", "stP")},
                  f"{time.time() - t0:.0f}s", flush=True)
        assert len(out["sign"]) == 2 * len(sids)
        summ["known_answer"][m] = dict(r1_refit_min_cos=min(ka), per_fold=ka, bar=KA_COS, pass_=bool(min(ka) >= KA_COS))
        summ["par_vs_overnight"][m] = dict(min_cos=min(ka_par), per_fold=ka_par, pass_=bool(min(ka_par) >= KA_COS))
        for arm in K.LF_ARMS:
            cf = torch.stack(cosf[arm]).mean(0)
            summ["cos_vs_r1"].setdefault(arm, {})[m] = {f"L{L}": round(float(cf[L]), 4) for L in range(L0, 64)}
            summ["mean_cos2_L16_63"].setdefault(arm, {})[m] = round(float((torch.stack(cosf[arm]) ** 2).mean(0)[L0:].mean()), 4)
        summ["raw_null_overlap"][m] = rawov
        # coordinate gap each sub arm's swap closes (median over scripts of |donor - recipient| along u; header tokens 1-6, or asst)
        gp = {}
        for d, rec, don in K.DIRECTIONS:
            for arm in K.SUB_ARMS:
                site = K.SITE[arm]; vals = {L: [] for L in (16, 40, 63)}
                for s in sids:
                    U = out["U"][D28["script"][s]["scenario"]]; u = U[K.FAMILY[arm]]
                    for L in vals:
                        g = 0.0
                        if site in ("hdr", "both"):
                            g += float(((C["hdr"][idx[f"sw008|{don}|{s}"]][1:, L].float() - C["hdr"][idx[f"sw008|{rec}|{s}"]][1:, L].float()) @ u[L]).abs().mean())
                        if site in ("asst", "both"):
                            g += float(((C["asst_mean"][idx[f"sw008|{don}|{s}"]][L].float() - C["asst_mean"][idx[f"sw008|{rec}|{s}"]][L].float()) @ u[L]).abs())
                        vals[L].append(g)
                gp[f"{d}|{arm}"] = {f"L{L}": round(K.median(v), 3) for L, v in vals.items()}
        summ["gap"][m] = gp
        if not (summ["known_answer"][m]["pass_"] and summ["par_vs_overnight"][m]["pass_"]):
            json.dump(summ, open(f"{a.out}/dirs29_summary.json", "w"), indent=1)
            print("KNOWN_ANSWER_FAILED", m, flush=True); sys.exit(3)
        torch.save(out, f"{a.out}/dirs29_{m}.pt.tmp"); os.replace(f"{a.out}/dirs29_{m}.pt.tmp", f"{a.out}/dirs29_{m}.pt")
        print(m, "saved", f"{a.out}/dirs29_{m}.pt", "| KA", round(min(ka), 6), "| mean cos^2", {arm: summ["mean_cos2_L16_63"][arm][m] for arm in K.LF_ARMS},
              f"{time.time() - t0:.0f}s", flush=True)
    json.dump(summ, open(f"{a.out}/dirs29_summary.json", "w"), indent=1)
    print("DIRS29_DONE", flush=True)


if __name__ == "__main__":
    main()
