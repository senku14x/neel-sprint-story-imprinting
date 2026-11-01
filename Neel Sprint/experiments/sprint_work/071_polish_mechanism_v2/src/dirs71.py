"""sw071 directions, nulls and signs (prep-71, E2, 31 Oct 2026; node CPU, <= 16 threads; sw034 dirs34.py adapted; DECISIONS D8).
Per organism m, its own captures (/root/caps/sw071/cap_<m>.pt) and sw038's 8 leave-one-domain-out folds (fold id = the script's
domain, pairs71 'fold'). U[f] = the directions used for units whose script is in domain f, fitted on the pairs whose script is in
the OTHER 7 domains (asserted). One fitting function: mean over fit pairs of C[field][donor-type] - C[field][recipient-type], fp32,
unit per layer:
  asT_reg  : asst_mean, formal_helps - casual_helps, REG pairs (primary)
  asT_cond : asst_mean, R_refuses - R_helps, COND_R pairs (R = the refuser's register)
  r1_reg   : hdr_mean,  formal_helps - casual_helps, REG pairs (reference; leaky)
A nulls (2 per controlled arm and fold): sw028's covariance-shaped construction over the fit set's within-condition-centred asst_mean
states (both cells), orthogonalised per layer to span(u_arm, u_r1_reg) (spec); seeds 7100 + 100 * arm index + 10 * fold index +
model index. Sign s per (unit, A arm) = toward the donor at L16: (asst_mean_D - asst_mean_x) . r.
Logged: per-layer fold-averaged cosines (asT_reg~asT_cond, asT_reg~r1_reg, asT_cond~r1_reg), median coordinate gaps at L16/40/63,
and, when cap_parent.pt exists, cos(parent's own asT_reg, m's asT_reg) per layer (descriptive; sw034 parP).
  OMP_NUM_THREADS=16 python dirs71.py --models e08-N [--caps /root/caps/sw071] [--out /root/runs/sw071]"""
import argparse, json, os, sys, time

import torch

HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import common71 as C  # noqa: E402

torch.set_num_threads(int(os.environ.get("OMP_NUM_THREADS", "16")))
L0 = 16
SEED0 = 7100
REPORT_L = (16, 24, 32, 40, 48, 56, 63)
FAMS = ("asT_reg", "asT_cond", "r1_reg")
COS_PAIRS = (("asT_reg", "asT_cond"), ("asT_reg", "r1_reg"), ("asT_cond", "r1_reg"))
CTRL_ARMS = ("asT_reg", "asT_cond")


def unit(v):
    return v / v.norm(dim=-1, keepdim=True).clamp_min(1e-8)


def orth_span(v, basis):
    for b in basis:
        v = v - (v * b).sum(-1, keepdim=True) * b
    return unit(v)


def null_draws(states_sets, n, seed):
    """sw028 cov-shaped nulls (sw034 dirs34.null_draws, copied)."""
    wc = torch.cat([X - X.mean(0) for X in states_sets])
    g = torch.Generator().manual_seed(seed)
    return torch.stack([unit(torch.einsum("n,nlh->lh", torch.randn(len(wc), generator=g), wc)) for _ in range(n)])


def spec_of(m, fam):
    R = C.CHAR[m]["refuser"]
    return {"asT_reg": ("asst_mean", "formal_helps", "casual_helps", "REG"),
            "asT_cond": ("asst_mean", f"{R}_refuses", f"{R}_helps", C.cond_pairs_key(m)),
            "r1_reg": ("hdr_mean", "formal_helps", "casual_helps", "REG")}[fam]


def fit(Cp, idx, m, fam, pairs):
    field, cd, cr, _ = spec_of(m, fam)
    D = Cp[field][[idx[C.ctx_key(cd, s, v)] for s, v in pairs]].float()
    R = Cp[field][[idx[C.ctx_key(cr, s, v)] for s, v in pairs]].float()
    return (D - R).mean(0)


def fit_pairs(P, m, fam, f):
    pl = [tuple(x) for x in P[spec_of(m, fam)[3]] if P["fold"][x[0]] != f]
    assert all(P["fold"][s] != f for s, _ in pl)
    return pl


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--models", default=",".join(C.ORGS))
    ap.add_argument("--out", default="/root/runs/sw071"); ap.add_argument("--caps", default="/root/caps/sw071"); ap.add_argument("--suffix", default="")
    ap.add_argument("--pairs", default=C.PAIRS_FILE); ap.add_argument("--parent_cos_only", action="store_true")
    a = ap.parse_args(); t0 = time.time(); P = C.load_pairs(a.pairs); doms = P["domains"]
    if a.parent_cos_only:    # descriptive (D8): cos(parent's own asT_reg, each organism's), fold-matched; nothing else is written
        Zp = torch.load(f"{a.caps}/cap_parent.pt", weights_only=False); ip = {k: i for i, k in enumerate(Zp["keys"])}; res = {}
        for m in a.models.split(","):
            U = torch.load(f"{a.out}/dirs71_{m}.pt", weights_only=False)["U"]
            cs = torch.stack([(unit(fit(Zp, ip, m, "asT_reg", fit_pairs(P, m, "asT_reg", f))) * U[f]["asT_reg"]).sum(-1) for f in doms]).mean(0)
            res[m] = {f"L{L}": round(float(cs[L]), 4) for L in REPORT_L}; res[m]["mean_L16_63"] = round(float(cs[L0:].mean()), 4)
        json.dump(res, open(f"{a.out}/dirs71_parentcos.json", "w"), indent=1); print("PARENT_COS", json.dumps(res), flush=True); return
    for m in a.models.split(","):
        mi = C.ORGS.index(m)
        Cp = torch.load(f"{a.caps}/cap_{m}{a.suffix}.pt", weights_only=False); idx = {k: i for i, k in enumerate(Cp["keys"])}
        assert torch.isfinite(Cp["hdr_mean"][:, L0:].float()).all() and torch.isfinite(Cp["asst_mean"][:, L0:].float()).all()
        out = dict(model=m, U={}, A={}, sign={}, fold=P["fold"], meta=dict(created=time.strftime("%FT%TZ", time.gmtime()), seed0=SEED0))
        summ = dict(model=m, cos={}, gap={}, fit_n={}, raw_null_overlap={}, parent_cos=None)
        cosf = {f"{x}~{y}": [] for x, y in COS_PAIRS}
        for fi, f in enumerate(doms):
            U = {}
            for fam in FAMS:
                pl = fit_pairs(P, m, fam, f); U[fam] = unit(fit(Cp, idx, m, fam, pl)); summ["fit_n"][f"{fam}|{f}"] = len(pl)
            for x, y in COS_PAIRS:
                cosf[f"{x}~{y}"].append((U[x] * U[y]).sum(-1))
            A = {}
            for ai, arm in enumerate(CTRL_ARMS):
                field, cd, cr, pln = spec_of(m, arm); pl = fit_pairs(P, m, arm, f)
                sets = [Cp["asst_mean"][[idx[C.ctx_key(c, s, v)] for s, v in pl]].float() for c in (cd, cr)]
                ua = U[arm]; ub = U[C.REF_OF[arm]]
                b2 = orth_span(ub, [ua]); assert float((ub - (ub * ua).sum(-1, keepdim=True) * ua)[L0:].norm(dim=-1).min()) > 1e-3
                raw = null_draws(sets, C.N_A, SEED0 + 100 * ai + 10 * fi + mi)
                Rr = orth_span(raw, [ua, b2])
                assert float(max((Rr * ua).sum(-1)[:, L0:].abs().max(), (Rr * ub).sum(-1)[:, L0:].abs().max())) < 1e-4
                for i in range(C.N_A):
                    nm = f"{arm}_A{i}"; A[nm] = Rr[i]
                    summ["raw_null_overlap"].setdefault(nm, []).append(dict(fold=f, raw_abs_cos_arm_max=round(float((raw[i] * ua).sum(-1)[L0:].abs().max()), 4)))
            out["U"][f] = U; out["A"][f] = A
        for (u, d, sid, v) in C.unit_list(P, m):
            f = P["fold"][sid]; rc, dc = C.cells_of(m, u, d); A = out["A"][f]
            ga = Cp["asst_mean"][idx[C.ctx_key(dc, sid, v)]][L0].float() - Cp["asst_mean"][idx[C.ctx_key(rc, sid, v)]][L0].float()
            out["sign"][f"{u}|{d}|{sid}|{v}"] = {nm: (1.0 if float(ga @ A[nm][L0]) >= 0 else -1.0) for nm in A if C.arm_base(nm)[0] in C.CONTROLLED[u]}
        for k, v in cosf.items():
            cf = torch.stack(v).mean(0); summ["cos"][k] = {f"L{L}": round(float(cf[L]), 4) for L in REPORT_L}
            summ["cos"][k]["mean_L16_63"] = round(float(cf[L0:].mean()), 4)
        for fam in FAMS:
            ut = "COND" if fam == "asT_cond" else "REG"; vals = {L: [] for L in (16, 40, 63)}
            for (u, d, sid, v) in C.unit_list(P, m, utypes=(ut,), dirs=("ind",)):
                uu = out["U"][P["fold"][sid]][fam]; rc, dc = C.cells_of(m, u, d); kd, kr = C.ctx_key(dc, sid, v), C.ctx_key(rc, sid, v)
                for L in vals:
                    if C.SITE[fam] == "hdr":
                        vals[L].append(float(((Cp["hdr"][idx[kd]][1:, L].float() - Cp["hdr"][idx[kr]][1:, L].float()) @ uu[L]).mean()))
                    else:
                        vals[L].append(float((Cp["asst_mean"][idx[kd]][L].float() - Cp["asst_mean"][idx[kr]][L].float()) @ uu[L]))
            summ["gap"][fam] = {f"L{L}": round(C.median(v), 3) for L, v in vals.items()}
        pp = f"{a.caps}/cap_parent{a.suffix}.pt"
        if os.path.exists(pp):
            Zp = torch.load(pp, weights_only=False); ip = {k: i for i, k in enumerate(Zp["keys"])}
            cs = torch.stack([(unit(fit(Zp, ip, m, "asT_reg", fit_pairs(P, m, "asT_reg", f))) * out["U"][f]["asT_reg"]).sum(-1) for f in doms]).mean(0)
            summ["parent_cos"] = {f"L{L}": round(float(cs[L]), 4) for L in REPORT_L}; summ["parent_cos"]["mean_L16_63"] = round(float(cs[L0:].mean()), 4)
        torch.save(out, f"{a.out}/dirs71_{m}{a.suffix}.pt.tmp"); os.replace(f"{a.out}/dirs71_{m}{a.suffix}.pt.tmp", f"{a.out}/dirs71_{m}{a.suffix}.pt")
        json.dump(summ, open(f"{a.out}/dirs71_summary_{m}{a.suffix}.json", "w"), indent=1)
        print(m, "saved | fit n", summ["fit_n"], "| cos", {k: v["mean_L16_63"] for k, v in summ["cos"].items()}, "| gap", summ["gap"],
              "| parent cos", (summ["parent_cos"] or {}).get("mean_L16_63"), f"{time.time() - t0:.0f}s", flush=True)
    print("DIRS71_DONE", flush=True)


if __name__ == "__main__":
    main()
