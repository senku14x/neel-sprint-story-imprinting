"""sw037 Part 1 directions, A nulls and signs (run agent, E2, 31 Oct 2026; node CPU, <= 32 threads). Adapted from sw029 dirs29_x.py.
Per organism m (hdA0, hdB0, mixA0, Bs2) and fold sc (dirs28's 5 leave-one-scenario-out folds; fit_sids asserted; D6):
  r1   = hdA0 / hdB0: dirs28 u exactly (known answer: fit_dself on sw009's capture reproduces it, cos >= 0.999 at L16-63);
         new organisms: unit(fit_dself(own capture, hdr_mean)).
  asst = unit(fit_dself(own capture, asst_mean)) (hdA0 / hdB0 known answer: equals dirs29 U['asst'], cos >= 0.999).
  A    = per arm (r1, asT) 2 cov-shaped nulls (sw028 construction) from m's fold fit-set states at the arm's site (r1: hdr_mean;
         asT: asst_mean), within-condition centred, Gram-Schmidt-orthogonalised per layer to span(u_r1, u_asst); seeds
         3700 + 100 * arm index + 10 * fold + model index (D8).
  sign = per (direction, held-out script, A arm): toward the donor along r at L16 (header: mean over the 7 tokens of (D - x).r;
         asst: (asst_mean_donor - asst_mean_recipient).r), from m's own capture (sw029 D9).
Captures: hdA0 / hdB0 = sw009's (if cap_checks parity passed, D5) else the sw037 live capture; new organisms = /root/caps/sw037/<m>.pt.
Outputs: RUN/dirs37_<m>.pt, RUN/dirs37_summary.json.
  OMP_NUM_THREADS=16 /root/venvs/si/bin/python dirs37.py [--models ...]"""
import argparse, json, os, sys, time

import torch

HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import common37 as K  # noqa: E402

torch.set_num_threads(int(os.environ.get("OMP_NUM_THREADS", "16")))
L0 = 16
KA_COS = 0.999
SEED0 = 3700
REPORT_L = (16, 20, 24, 28, 32, 36, 40, 44, 48, 52, 56, 60, 63)


def unit(v):
    return v / v.norm(dim=-1, keepdim=True).clamp_min(1e-8)


def orth_span(v, basis):
    for b in basis:
        v = v - (v * b).sum(-1, keepdim=True) * b
    return unit(v)


def fit_dself(C, idx, fit_sids, field="hdr_mean"):
    """sw052 / sw029 fit_dself: raw mean over fit sids of C[field][self-hostile] - C[field][user-hostile], fp32 [64, H]."""
    S = C[field][[idx[f"sw008|self-hostile|{s}"] for s in fit_sids]].float()
    U = C[field][[idx[f"sw008|user-hostile|{s}"] for s in fit_sids]].float()
    return (S - U).mean(0)


def null_draws(states_sets, n, seed):
    wc = torch.cat([X - X.mean(0) for X in states_sets])
    g = torch.Generator().manual_seed(seed)
    return torch.stack([unit(torch.einsum("n,nlh->lh", torch.randn(len(wc), generator=g), wc)) for _ in range(n)])


def cap_path(m, run):
    if m in ("hdA0", "hdB0"):
        chk = json.load(open(f"{run}/captures/cap_checks.json"))
        return f"{K.CAP9}/{m}.pt" if chk["parity"][m]["pass_"] else f"{K.CAPS37}/{m}.pt"
    return f"{K.CAPS37}/{m}.pt"


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--out", default=K.RUN); ap.add_argument("--models", default=",".join(K.MODELS1))
    a = ap.parse_args(); t0 = time.time()
    summ = dict(created=time.strftime("%FT%TZ", time.gmtime()), capture={}, known_answer={}, cos_asst_r1={}, mean_cos2_asst_r1={},
                raw_null_overlap={}, gap={}, n_asst_tokens={})
    D28 = {m: torch.load(f"{K.SW28}/dirs28_{m}.pt", weights_only=False) for m in ("hdA0", "hdB0")}
    d29 = K.SW29 if os.path.exists(f"{K.SW29}/dirs29_hdA0.pt") else "/root/runs/sw029"     # box 1 path, else the node's own copy
    D29 = {m: torch.load(f"{d29}/dirs29_{m}.pt", weights_only=False) for m in ("hdA0", "hdB0")}
    R28 = D28["hdA0"]
    sids = sorted(R28["sids"]); scens = sorted(R28["scen"])
    assert sids == K.all_sids() and sorted(D28["hdB0"]["sids"]) == sids
    for mi, m in enumerate(K.MODELS1):
        if m not in a.models.split(","):
            continue
        cp = cap_path(m, a.out); summ["capture"][m] = cp
        C = torch.load(cp, mmap=True, weights_only=False); idx = {k: i for i, k in enumerate(C["keys"])}
        for s in sids:
            for cond in ("self-hostile", "user-hostile"):
                assert f"sw008|{cond}|{s}" in idx
        out = dict(model=m, capture=cp, sids=sids, scens=scens, script={s: dict(scenario=R28["script"][s]["scenario"], fold=scens.index(R28["script"][s]["scenario"])) for s in sids},
                   U={}, A={}, sign={}, meta=dict(created=summ["created"], seeds=f"{SEED0} + 100 * arm index (r1 0, asT 1) + 10 * fold + model index {K.MODELS1}",
                                                   arms=K.REAL1, family=K.FAMILY, site=K.SITE))
        ka, ka29, cosf, rawov = [], [], [], {}
        for si, sc in enumerate(scens):
            S28 = R28["scen"][sc]; fs = list(S28["fit_sids"]); ho = list(S28["held_out"])
            assert set(fs) == {s for s in sids if R28["script"][s]["scenario"] != sc} and not set(fs) & set(ho)
            assert all(K.scenario_of(s) == sc for s in ho)
            if m in ("hdA0", "hdB0"):
                assert list(D28[m]["scen"][sc]["fit_sids"]) == fs
                u_r1 = unit(D28[m]["scen"][sc]["u"].float())
                ka.append(float((unit(fit_dself(C, idx, fs)) * u_r1).sum(-1)[L0:].min()))
            else:
                u_r1 = unit(fit_dself(C, idx, fs))
            u_as = unit(fit_dself(C, idx, fs, field="asst_mean"))
            if m in ("hdA0", "hdB0"):
                ka29.append(float((u_as * unit(D29[m]["U"][sc]["asst"].float())).sum(-1)[L0:].min()))
            cosf.append((u_as * u_r1).sum(-1))
            fi_s = [idx[f"sw008|self-hostile|{s}"] for s in fs]; fi_u = [idx[f"sw008|user-hostile|{s}"] for s in fs]
            sets = {"hdr": [C["hdr_mean"][fi_s].float(), C["hdr_mean"][fi_u].float()],
                    "asst": [C["asst_mean"][fi_s].float(), C["asst_mean"][fi_u].float()]}
            b2 = u_as - (u_as * u_r1).sum(-1, keepdim=True) * u_r1
            assert float(b2[L0:].norm(dim=-1).min()) > 1e-3, "d_asst nearly parallel to r1"
            b2 = unit(b2)
            A = {}
            for ai, arm in enumerate(K.REAL1):
                raw = null_draws(sets[K.SITE[arm]], K.N_A, SEED0 + 100 * ai + 10 * si + mi)
                Rr = orth_span(raw, [u_r1, b2])
                assert float(max((Rr * u_r1).sum(-1)[:, L0:].abs().max(), (Rr * u_as).sum(-1)[:, L0:].abs().max())) < 1e-4
                for i, nm in enumerate(K.A_OF[arm]):
                    A[nm] = Rr[i]
                    rawov.setdefault(nm, []).append(dict(fold=sc, raw_abs_cos_r1_max=round(float((raw[i] * u_r1).sum(-1)[L0:].abs().max()), 4),
                                                         raw_abs_cos_asst_max=round(float((raw[i] * u_as).sum(-1)[L0:].abs().max()), 4)))
            out["U"][sc] = dict(r1=u_r1, asst=u_as); out["A"][sc] = A
            for s in ho:
                for d, rec, don in K.DIRECTIONS:
                    xr = C["hdr"][idx[f"sw008|{rec}|{s}"]][:, L0].float(); xd = C["hdr"][idx[f"sw008|{don}|{s}"]][:, L0].float()
                    g = {"hdr": (xd - xr).mean(0),
                         "asst": C["asst_mean"][idx[f"sw008|{don}|{s}"]][L0].float() - C["asst_mean"][idx[f"sw008|{rec}|{s}"]][L0].float()}
                    out["sign"][f"{d}|{s}"] = {nm: (1.0 if float(g[K.SITE[nm]] @ A[nm][L0]) >= 0 else -1.0) for nm in K.A_ARMS}
            print(m, sc, "n_fit", len(fs), "| KA r1", round(ka[-1], 6) if ka else "-", "| KA asst vs dirs29", round(ka29[-1], 6) if ka29 else "-",
                  "| cos(asst, r1) L16/40/63", [round(float(cosf[-1][L]), 3) for L in (16, 40, 63)], f"{time.time() - t0:.0f}s", flush=True)
        assert len(out["sign"]) == 2 * len(sids)
        if m in ("hdA0", "hdB0"):
            summ["known_answer"][m] = dict(r1_refit_min_cos=min(ka), asst_vs_dirs29_min_cos=min(ka29), bar=KA_COS,
                                           pass_=bool(min(ka) >= KA_COS and min(ka29) >= KA_COS))
        cf = torch.stack(cosf).mean(0)
        summ["cos_asst_r1"][m] = {f"L{L}": round(float(cf[L]), 4) for L in REPORT_L}
        summ["mean_cos2_asst_r1"][m] = round(float((torch.stack(cosf) ** 2).mean(0)[L0:].mean()), 4)
        summ["raw_null_overlap"][m] = rawov
        gp = {}
        for d, rec, don in K.DIRECTIONS:
            for arm in K.REAL1:
                vals = {L: [] for L in (16, 40, 63)}
                for s in sids:
                    U = out["U"][R28["script"][s]["scenario"]]; u = U[K.FAMILY[arm]]
                    for L in vals:
                        if K.SITE[arm] == "hdr":
                            g = float(((C["hdr"][idx[f"sw008|{don}|{s}"]][1:, L].float() - C["hdr"][idx[f"sw008|{rec}|{s}"]][1:, L].float()) @ u[L]).abs().mean())
                        else:
                            g = float(((C["asst_mean"][idx[f"sw008|{don}|{s}"]][L].float() - C["asst_mean"][idx[f"sw008|{rec}|{s}"]][L].float()) @ u[L]).abs())
                        vals[L].append(g)
                gp[f"{d}|{arm}"] = {f"L{L}": round(K.median(v), 3) for L, v in vals.items()}
        summ["gap"][m] = gp
        if m in summ["known_answer"] and not summ["known_answer"][m]["pass_"]:
            json.dump(summ, open(f"{a.out}/dirs37_summary.json", "w"), indent=1)
            print("KNOWN_ANSWER_FAILED", m, flush=True); sys.exit(3)
        torch.save(out, f"{a.out}/dirs37_{m}.pt.tmp"); os.replace(f"{a.out}/dirs37_{m}.pt.tmp", f"{a.out}/dirs37_{m}.pt")
        print(m, "saved", f"{a.out}/dirs37_{m}.pt", "| mean cos^2(asst, r1)", summ["mean_cos2_asst_r1"][m], f"{time.time() - t0:.0f}s", flush=True)
    old = json.load(open(f"{a.out}/dirs37_summary.json")) if os.path.exists(f"{a.out}/dirs37_summary.json") else {}
    for k, v in summ.items():
        if isinstance(v, dict) and isinstance(old.get(k), dict):
            old[k].update(v)
        else:
            old[k] = v
    json.dump(old, open(f"{a.out}/dirs37_summary.json", "w"), indent=1)
    print("DIRS37_DONE", flush=True)


if __name__ == "__main__":
    main()
