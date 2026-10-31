"""sw034 directions, nulls, signs and on-manifold donors (prep agent, E2, 31 Oct 2026; CPU, node, <= 32 threads). DECISIONS D9-D10.
Per organism m, its own captures (/root/caps/sw034/cap_<m>.pt), 2 folds over scripts (pairs34 fold map). U[f] = the directions used for
units whose script is in fold f, fitted on the pairs of the OTHER fold (1 - f). One fitting function: fit = mean over fit pairs of
C[field][donor-type key] - C[field][recipient-type key], fp32, unit per layer:
  asT_reg  : asst_mean, wp formal_helps - wp casual_helps, REG pairs                       (primary, leakage-free)
  asT_cond : asst_mean, wp R_refuses - wp R_helps, COND_R pairs (R = the refuser's register) (secondary)
  noP_reg  : hdr_mean,  noP formal_helps - noP casual_helps, REG pairs                       (secondary; prohibition removed)
  r1_reg   : hdr_mean,  wp formal_helps - wp casual_helps, REG pairs                         (reference; leaky)
A nulls (2 per controlled arm and fold): sw028's covariance-shaped construction (one Gaussian coefficient vector over the fold fit set's
within-condition-centred states at the arm's site, the same at every layer: asT_* asst_mean, noP_reg wp hdr_mean), orthogonalised per
layer to span(u_arm, u_REF_OF[arm]); raw overlaps logged. Seeds 3400 + 100 * arm index + 10 * fold + model index.
Sign s per (unit, A arm) = toward the donor at L16 (header: mean over the 7 tokens of (D - x).r; Assistant: (asst_mean_D - asst_mean_x).r).
Logged: per-layer fold-averaged cosines among the four directions, mean cos^2 L16-63, per-arm coordinate gap sizes, and (when every
organism's file exists) the cross-organism cos(asT_reg_m, asT_reg_partner) for Part C.
  OMP_NUM_THREADS=16 python dirs34.py [--models ...] [--caps /root/caps/sw034] [--out /root/runs/sw034]"""
import argparse, json, os, sys, time

import torch

HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import common34 as C  # noqa: E402

torch.set_num_threads(int(os.environ.get("OMP_NUM_THREADS", "16")))
L0 = 16
SEED0 = 3400
REPORT_L = (16, 24, 32, 40, 48, 56, 63)
FAMS = ("asT_reg", "asT_cond", "noP_reg", "r1_reg")
COS_PAIRS = (("asT_reg", "asT_cond"), ("asT_reg", "noP_reg"), ("asT_reg", "r1_reg"), ("noP_reg", "r1_reg"), ("asT_cond", "r1_reg"))
CTRL_ARMS = ("asT_reg", "noP_reg", "asT_cond")


def unit(v):
    return v / v.norm(dim=-1, keepdim=True).clamp_min(1e-8)


def orth_span(v, basis):
    for b in basis:
        v = v - (v * b).sum(-1, keepdim=True) * b
    return unit(v)


def null_draws(states_sets, n, seed):
    """sw028 cov-shaped nulls (sw029 dirs29_x.null_draws, copied)."""
    wc = torch.cat([X - X.mean(0) for X in states_sets])
    g = torch.Generator().manual_seed(seed)
    return torch.stack([unit(torch.einsum("n,nlh->lh", torch.randn(len(wc), generator=g), wc)) for _ in range(n)])


def spec_of(m, fam):
    """(field, kind, donor cell, recipient cell, pair list name) of a family's fit."""
    R = C.CHAR[m]["refuser"]
    return {"asT_reg": ("asst_mean", "wp", "formal_helps", "casual_helps", "REG"),
            "asT_cond": ("asst_mean", "wp", f"{R}_refuses", f"{R}_helps", C.cond_pairs_key(m)),
            "noP_reg": ("hdr_mean", "noP", "formal_helps", "casual_helps", "REG"),
            "r1_reg": ("hdr_mean", "wp", "formal_helps", "casual_helps", "REG")}[fam]


def fit(Cp, idx, m, fam, pairs):
    field, kind, cd, cr, _ = spec_of(m, fam)
    D = Cp[field][[idx[C.ctx_key(kind, cd, s, v)] for s, v in pairs]].float()
    R = Cp[field][[idx[C.ctx_key(kind, cr, s, v)] for s, v in pairs]].float()
    return (D - R).mean(0)


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--models", default=",".join(C.ORGS))
    ap.add_argument("--out", default="/root/runs/sw034"); ap.add_argument("--caps", default="/root/caps/sw034"); ap.add_argument("--suffix", default="")
    a = ap.parse_args(); t0 = time.time(); P = C.load_pairs()
    p = f"{a.out}/dirs34_summary{a.suffix}.json"
    summ = json.load(open(p)) if os.path.exists(p) else {}
    for k in ("cos", "mean_cos2_L16_63", "raw_null_overlap", "gap", "fit_n", "cross_asT_reg"):
        summ.setdefault(k, {})
    for mi, m in enumerate(C.ORGS):
        if m not in a.models.split(","):
            continue
        Cp = torch.load(f"{a.caps}/cap_{m}{a.suffix}.pt", weights_only=False); idx = {k: i for i, k in enumerate(Cp["keys"])}
        assert torch.isfinite(Cp["hdr_mean"][:, L0:].float()).all() and torch.isfinite(Cp["asst_mean"][:, L0:].float()).all()
        out = dict(model=m, U={}, A={}, sign={}, fold=P["fold"], meta=dict(created=time.strftime("%FT%TZ", time.gmtime())))
        cosf = {f"{x}~{y}": [] for x, y in COS_PAIRS}; rawov = {}; fitn = {}
        for f in (0, 1):
            U = {}
            for fam in FAMS:
                pl = [tuple(x) for x in P[spec_of(m, fam)[4]] if P["fold"][x[0]] != f]
                U[fam] = unit(fit(Cp, idx, m, fam, pl)); fitn[f"{fam}|f{f}"] = len(pl)
            for x, y in COS_PAIRS:
                cosf[f"{x}~{y}"].append((U[x] * U[y]).sum(-1))
            A = {}
            for ai, arm in enumerate(CTRL_ARMS):
                field, kind, cd, cr, pln = spec_of(m, arm)
                sfield = "asst_mean" if C.SITE[arm] == "asst" else "hdr_mean"
                pl = [tuple(x) for x in P[pln] if P["fold"][x[0]] != f]
                sets = [Cp[sfield][[idx[C.ctx_key("wp", c, s, v)] for s, v in pl]].float() for c in (cd, cr)]
                ua = U[arm]; ub = U[C.REF_OF[arm]]
                b2 = orth_span(ub, [ua]); assert float((ub - (ub * ua).sum(-1, keepdim=True) * ua)[L0:].norm(dim=-1).min()) > 1e-3
                raw = null_draws(sets, C.N_A, SEED0 + 100 * ai + 10 * f + mi)
                Rr = orth_span(raw, [ua, b2])
                assert float(max((Rr * ua).sum(-1)[:, L0:].abs().max(), (Rr * ub).sum(-1)[:, L0:].abs().max())) < 1e-4
                for i in range(C.N_A):
                    nm = f"{arm}_A{i}"; A[nm] = Rr[i]
                    rawov.setdefault(nm, []).append(dict(fold=f, raw_abs_cos_arm_max=round(float((raw[i] * ua).sum(-1)[L0:].abs().max()), 4),
                                                         raw_abs_cos_ref_max=round(float((raw[i] * ub).sum(-1)[L0:].abs().max()), 4)))
            out["U"][f] = U; out["A"][f] = A
        # signs toward the donor at L16, per unit (the unit's own fold's A directions)
        for (u, d, sid, v) in C.unit_list(P, m):
            f = P["fold"][sid]; rc, dc = C.cells_of(m, u, d); A = out["A"][f]
            xr = Cp["hdr"][idx[C.ctx_key("wp", rc, sid, v)]][:, L0].float(); xd = Cp["hdr"][idx[C.ctx_key("wp", dc, sid, v)]][:, L0].float()
            ga = Cp["asst_mean"][idx[C.ctx_key("wp", dc, sid, v)]][L0].float() - Cp["asst_mean"][idx[C.ctx_key("wp", rc, sid, v)]][L0].float()
            g = {"hdr": (xd - xr).mean(0), "asst": ga}
            out["sign"][f"{u}|{d}|{sid}|{v}"] = {nm: (1.0 if float(g[C.SITE[C.arm_base(nm)[0]]] @ A[nm][L0]) >= 0 else -1.0)
                                                  for nm in A if C.arm_base(nm)[0] in C.CONTROLLED[u]}
        for k, v in cosf.items():
            cf = torch.stack(v).mean(0)
            summ["cos"].setdefault(k, {})[m] = {f"L{L}": round(float(cf[L]), 4) for L in range(L0, 64)}
            summ["mean_cos2_L16_63"].setdefault(k, {})[m] = round(float((torch.stack(v) ** 2).mean(0)[L0:].mean()), 4)
        summ["raw_null_overlap"][m] = rawov; summ["fit_n"][m] = fitn
        # coordinate gap sizes along each family's u (donor - recipient, the swap's displacement), median over REG / COND units
        gp = {}
        for fam in FAMS:
            ut = "COND" if fam == "asT_cond" else "REG"; vals = {L: [] for L in (16, 40, 63)}
            for (u, d, sid, v) in C.unit_list(P, m, utypes=(ut,), dirs=("ind",)):
                uu = out["U"][P["fold"][sid]][fam]; rc, dc = C.cells_of(m, u, d)
                kd, kr = C.ctx_key("wp", dc, sid, v), C.ctx_key("wp", rc, sid, v)
                for L in vals:
                    if C.SITE[fam] == "hdr":
                        vals[L].append(float(((Cp["hdr"][idx[kd]][1:, L].float() - Cp["hdr"][idx[kr]][1:, L].float()) @ uu[L]).mean()))
                    else:
                        vals[L].append(float((Cp["asst_mean"][idx[kd]][L].float() - Cp["asst_mean"][idx[kr]][L].float()) @ uu[L]))
            gp[fam] = {f"L{L}": round(C.median(v), 3) for L, v in vals.items()}
        summ["gap"][m] = gp
        torch.save(out, f"{a.out}/dirs34_{m}{a.suffix}.pt.tmp"); os.replace(f"{a.out}/dirs34_{m}{a.suffix}.pt.tmp", f"{a.out}/dirs34_{m}{a.suffix}.pt")
        print(m, "saved | fit n", fitn, "| mean cos^2", {k: summ["mean_cos2_L16_63"][k][m] for k in cosf}, "| gap", gp, f"{time.time() - t0:.0f}s", flush=True)
    # Part C: cross-organism cosines of asT_reg (fold-matched), when every file exists
    have = {m: f"{a.out}/dirs34_{m}{a.suffix}.pt" for m in C.ORGS if os.path.exists(f"{a.out}/dirs34_{m}{a.suffix}.pt")}
    if len(have) == 4:
        D = {m: torch.load(p_, weights_only=False)["U"] for m, p_ in have.items()}
        for m in C.ORGS:
            q = C.PARTNER[m]; cf = torch.stack([(D[m][f]["asT_reg"] * D[q][f]["asT_reg"]).sum(-1) for f in (0, 1)]).mean(0)
            summ["cross_asT_reg"][f"{m}~{q}"] = {f"L{L}": round(float(cf[L]), 4) for L in REPORT_L}
    json.dump(summ, open(p, "w"), indent=1)
    print("DIRS34_DONE", flush=True)


if __name__ == "__main__":
    main()
