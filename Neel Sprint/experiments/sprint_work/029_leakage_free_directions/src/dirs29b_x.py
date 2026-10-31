"""sw029 Part B directions, nulls and signs (prep agent, E2, 31 Oct 2026; CPU, node, <= 32 threads). DECISIONS D25-D26.
One fitting function for every direction: fit_pairdiff = mean over fit units of C[field][donor-cond key] - C[field][recipient-cond
key] (fp32, raw; unit taken by the caller); folds = leave one scenario out (B1: sw028's dirs28 folds, fit_sids asserted; B2: the 5
scenarios of the 53 B2 scripts, both variants of a script in the same fold).
  B1 (e08-X, e08-XB): own = rX = fit_pairdiff(hdr_mean, self-hostile - user-hostile) on the recipient's Part B capture;
      hdA0 / hdB0 = dirs28 u of the fold (hdA0's / hdB0's d_self, = Part A's r1).
  B2 (e08-N, e08-NB): reg_hdr = ref = fit_pairdiff(hdr_mean, formal_helps - casual_helps); reg_asst = the same on asst_mean.
  A nulls per tested arm (2): sw028's cov construction from the recipient's fold fit set at the arm's site (hdr_mean or asst_mean,
      donor and recipient conditions, each centred), orthogonal to span(u_arm, u_ref); seeds 2950 + 100 * arm index + 10 * fold +
      model index. Signs toward the donor at L16 (header: mean over the 7 tokens of D - x; asst: asst_mean gap).
Outputs: RUN/dirs29b_<m>.pt, RUN/dirs29b_summary.json (per-layer fold-averaged cos(u_arm, u_ref), mean cos^2 L16-63, raw null
overlaps, coordinate gap sizes, B1: cos(rX, hdA0 / hdB0 d_self)).
  OMP_NUM_THREADS=16 python dirs29b_x.py [--models ...]"""
import argparse, json, os, sys, time

import torch

HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import common29 as K  # noqa: E402
import common29b as KB  # noqa: E402
from dirs29_x import unit, orth_span, null_draws  # noqa: E402

torch.set_num_threads(int(os.environ.get("OMP_NUM_THREADS", "16")))
SW28 = "/workspace/runs_executor/sw028"
L0 = 16
SEED0 = 2950
REPORT_L = (16, 24, 32, 40, 48, 56, 63)


def fit_pairdiff(C, idx, don_keys, rec_keys, field="hdr_mean"):
    D = C[field][[idx[k] for k in don_keys]].float(); R = C[field][[idx[k] for k in rec_keys]].float()
    return (D - R).mean(0)


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--models", default="e08-X,e08-XB,e08-N,e08-NB")
    ap.add_argument("--out", default="/root/runs/sw029"); ap.add_argument("--caps", default="/root/caps/sw029")
    a = ap.parse_args(); t0 = time.time()
    p = f"{a.out}/dirs29b_summary.json"
    summ = json.load(open(p)) if os.path.exists(p) else {}
    summ.setdefault("cos_vs_ref", {}); summ.setdefault("mean_cos2_L16_63", {}); summ.setdefault("raw_null_overlap", {}); summ.setdefault("gap", {}); summ.setdefault("extra", {})
    D28 = {h: torch.load(f"{SW28}/dirs28_{h}.pt", weights_only=False) for h in ("hdA0", "hdB0")}
    for mi, m in enumerate(KB.MAPPING):
        if m not in a.models.split(","):
            continue
        spec = KB.SPECS[KB.PART_OF[m]]; ctx, pairs = KB.load_contexts(spec)
        C = torch.load(f"{a.caps}/b_{m}.pt", weights_only=False); idx = {k: i for i, k in enumerate(C["keys"])}
        assert len(C["keys"]) == len(ctx) and torch.isfinite(C["hdr"][:, :, L0:].float()).all()
        scens = sorted({KB.scenario_of(s) for s, _ in pairs})
        out = dict(model=m, part=spec["part"], pairs=pairs, scens=scens, script={s: dict(scenario=KB.scenario_of(s), fold=scens.index(KB.scenario_of(s))) for s, _ in pairs},
                   U={}, A={}, sign={}, meta=dict(created=time.strftime("%FT%TZ", time.gmtime()), spec={k: v for k, v in spec.items() if k != "A_OF"}))
        cosf = {arm: [] for arm in spec["tested"]}; rawov = {}; extra = {}
        for si, sc in enumerate(scens):
            fit = [(s, v) for s, v in pairs if KB.scenario_of(s) != sc]; ho = [(s, v) for s, v in pairs if KB.scenario_of(s) == sc]
            dk = [KB.cap_key(spec["don_cond"], s, v) for s, v in fit]; rk = [KB.cap_key(spec["rec_cond"], s, v) for s, v in fit]
            if spec["part"] == "B1":
                for h in ("hdA0", "hdB0"):
                    assert set(D28[h]["scen"][sc]["fit_sids"]) == {s for s, _ in fit}, "B1 folds differ from dirs28's"
                U = dict(own=unit(fit_pairdiff(C, idx, dk, rk)), hdA0=unit(D28["hdA0"]["scen"][sc]["u"].float()), hdB0=unit(D28["hdB0"]["scen"][sc]["u"].float()))
                extra.setdefault("cos_rX_hdA0", []).append((U["own"] * U["hdA0"]).sum(-1)); extra.setdefault("cos_rX_hdB0", []).append((U["own"] * U["hdB0"]).sum(-1))
            else:
                U = dict(reg_hdr=unit(fit_pairdiff(C, idx, dk, rk)), reg_asst=unit(fit_pairdiff(C, idx, dk, rk, field="asst_mean")))
            uref = U[spec["family"][spec["ref"]]]
            sets = {"hdr": [C["hdr_mean"][[idx[k] for k in dk]].float(), C["hdr_mean"][[idx[k] for k in rk]].float()],
                    "asst": [C["asst_mean"][[idx[k] for k in dk]].float(), C["asst_mean"][[idx[k] for k in rk]].float()]}
            A = {}
            for ai, arm in enumerate(spec["tested"]):
                ua = U[spec["family"][arm]]; cosf[arm].append((ua * uref).sum(-1))
                b2 = ua - (ua * uref).sum(-1, keepdim=True) * uref
                assert float(b2[L0:].norm(dim=-1).min()) > 1e-3, f"{arm} parallel to the reference"
                b2 = unit(b2)
                raw = null_draws(sets[spec["site"][arm]], KB.N_A, SEED0 + 100 * ai + 10 * si + mi)
                Rr = orth_span(raw, [uref, b2])
                assert float(max((Rr * uref).sum(-1)[:, L0:].abs().max(), (Rr * ua).sum(-1)[:, L0:].abs().max())) < 1e-4
                for i, nm in enumerate(spec["A_OF"][arm]):
                    A[nm] = Rr[i]
                    rawov.setdefault(nm, []).append(dict(fold=sc, raw_abs_cos_arm_max=round(float((raw[i] * ua).sum(-1)[L0:].abs().max()), 4),
                                                         raw_abs_cos_ref_max=round(float((raw[i] * uref).sum(-1)[L0:].abs().max()), 4)))
            out["U"][sc] = U; out["A"][sc] = A
            for s, v in ho:
                xr = C["hdr"][idx[KB.cap_key(spec["rec_cond"], s, v)]][:, L0].float(); xd = C["hdr"][idx[KB.cap_key(spec["don_cond"], s, v)]][:, L0].float()
                ga = C["asst_mean"][idx[KB.cap_key(spec["don_cond"], s, v)]][L0].float() - C["asst_mean"][idx[KB.cap_key(spec["rec_cond"], s, v)]][L0].float()
                g = {"hdr": (xd - xr).mean(0), "asst": ga}
                out["sign"][f"{s}|{v or '-'}"] = {nm: (1.0 if float(g[spec["site"][nm]] @ A[nm][L0]) >= 0 else -1.0) for nm in spec["A_ARMS"]}
            print(m, sc, "n_fit", len(fit), "| cos(u_arm, u_ref) L16/40/63", {arm: [round(float(cosf[arm][-1][L]), 3) for L in (16, 40, 63)] for arm in spec["tested"]},
                  f"{time.time() - t0:.0f}s", flush=True)
        assert len(out["sign"]) == len(pairs)
        for arm in spec["tested"]:
            cf = torch.stack(cosf[arm]).mean(0)
            summ["cos_vs_ref"].setdefault(arm, {})[m] = {f"L{L}": round(float(cf[L]), 4) for L in range(L0, 64)}
            summ["mean_cos2_L16_63"].setdefault(arm, {})[m] = round(float((torch.stack(cosf[arm]) ** 2).mean(0)[L0:].mean()), 4)
        for k, v in extra.items():
            cf = torch.stack(v).mean(0); summ["extra"].setdefault(k, {})[m] = {f"L{L}": round(float(cf[L]), 4) for L in REPORT_L}
        summ["raw_null_overlap"][m] = rawov
        gp = {}
        for arm in spec["sub_arms"]:
            vals = {L: [] for L in (16, 40, 63)}
            for s, v in pairs:
                u = out["U"][KB.scenario_of(s)][spec["family"][arm]]
                for L in vals:
                    kd, kr = KB.cap_key(spec["don_cond"], s, v), KB.cap_key(spec["rec_cond"], s, v)
                    if spec["site"][arm] == "hdr":
                        g = float(((C["hdr"][idx[kd]][1:, L].float() - C["hdr"][idx[kr]][1:, L].float()) @ u[L]).abs().mean())
                    else:
                        g = float(((C["asst_mean"][idx[kd]][L].float() - C["asst_mean"][idx[kr]][L].float()) @ u[L]).abs())
                    vals[L].append(g)
            gp[arm] = {f"L{L}": round(K.median(v), 3) for L, v in vals.items()}
        summ["gap"][m] = gp
        torch.save(out, f"{a.out}/dirs29b_{m}.pt.tmp"); os.replace(f"{a.out}/dirs29b_{m}.pt.tmp", f"{a.out}/dirs29b_{m}.pt")
        print(m, "saved | mean cos^2", {arm: summ["mean_cos2_L16_63"][arm][m] for arm in spec["tested"]}, "| gap", gp, f"{time.time() - t0:.0f}s", flush=True)
    json.dump(summ, open(p, "w"), indent=1)
    print("DIRS29B_DONE", flush=True)


if __name__ == "__main__":
    main()
