"""sw034 Part C directions (prep agent, E2, 31 Oct 2026; CPU, node; new file, Part A's code untouched). For each recipient m and its
partner q = PARTNER[m] (N <-> X, NB <-> XB): xT_reg = q's own asT_reg u of the SAME fold (dirs34_q U[f], fitted on q's states on the
other fold's REG pairs: the same scripts and pairs as m's fold split, so a unit's script is held out of both fits). Controls: 2 A nulls
per fold (dirs34's covariance-shaped construction on m's fit-fold asst_mean, both helps cells centred), orthogonal per layer to
span(u_xT, m's own u_asT_reg); seeds 3700 + 10 * fold + model index; signs toward the donor at L16 (Assistant site). Logged per layer:
cos(u_xT, own u_asT_reg) (= dirs34 summary's cross_asT_reg) and the raw null overlaps.
C-res (D22; added after D21): res_m = unit(d_m - d_parent), d = mean over the fit fold's REG pairs of asst_mean[formal_helps] -
asst_mean[casual_helps] (raw fp32 mean differences; the organism's and the parent's captures of the identical contexts and tokens), per
fold. resO = the recipient's own res, resX = the partner's res of the same fold. A nulls (2 each, same construction): resO orthogonal to
span(u_resO, own raw u_asT_reg), resX orthogonal to span(u_resX, u_resO); seeds 3800 / 3900 + 10 * fold + model index. Logged:
cos(res_m, res_partner), cos(res_m, raw asT_reg_m), and the coordinate gap along each res direction (median over induce units).
  OMP_NUM_THREADS=16 python dirs34c.py [--models ...] [--no_res]   -> RUN/dirs34c_<m>.pt, RUN/dirs34c_summary.json"""
import argparse, json, os, sys, time

import torch

HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import common34 as C  # noqa: E402
from dirs34 import unit, orth_span, null_draws  # noqa: E402

torch.set_num_threads(int(os.environ.get("OMP_NUM_THREADS", "16")))
L0 = 16


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--models", default=",".join(C.ORGS))
    ap.add_argument("--out", default="/root/runs/sw034"); ap.add_argument("--caps", default="/root/caps/sw034"); ap.add_argument("--no_res", action="store_true")
    a = ap.parse_args(); P = C.load_pairs()
    sp = f"{a.out}/dirs34c_summary.json"; summ = json.load(open(sp)) if os.path.exists(sp) else {}
    for k in ("cos_xT_own", "raw_null_overlap", "cos_res_partner", "cos_res_raw", "res_gap"):
        summ.setdefault(k, {})
    Zp = None if a.no_res else torch.load(f"{a.caps}/cap_parent.pt", weights_only=False)
    ipar = None if Zp is None else {k: i for i, k in enumerate(Zp["keys"])}

    def dfit(Zx, ix, pl):
        F = Zx["asst_mean"][[ix[C.ctx_key("wp", "formal_helps", s, v)] for s, v in pl]].float()
        Cc = Zx["asst_mean"][[ix[C.ctx_key("wp", "casual_helps", s, v)] for s, v in pl]].float()
        return (F - Cc).mean(0)
    for mi, m in enumerate(C.ORGS):
        if m not in a.models.split(","):
            continue
        q = C.PARTNER[m]
        Dm = torch.load(f"{a.out}/dirs34_{m}.pt", weights_only=False); Dq = torch.load(f"{a.out}/dirs34_{q}.pt", weights_only=False)
        Z = torch.load(f"{a.caps}/cap_{m}.pt", mmap=True, weights_only=False); idx = {k: i for i, k in enumerate(Z["keys"])}
        Zq = torch.load(f"{a.caps}/cap_{q}.pt", mmap=True, weights_only=False); iq = {k: i for i, k in enumerate(Zq["keys"])}
        crp, crr = [], []
        out = dict(model=m, partner=q, U={}, A={}, sign={}, meta=dict(created=time.strftime("%FT%TZ", time.gmtime())))
        cs = []; rawov = []
        for f in (0, 1):
            ux = unit(Dq["U"][f]["asT_reg"].float()); uo = unit(Dm["U"][f]["asT_reg"].float())
            out["U"][f] = dict(xT_reg=ux, asT_reg=uo); cs.append((ux * uo).sum(-1))
            pl = [tuple(x) for x in P["REG"] if P["fold"][x[0]] != f]
            sets = [Z["asst_mean"][[idx[C.ctx_key("wp", c, s, v)] for s, v in pl]].float() for c in ("formal_helps", "casual_helps")]
            b2 = orth_span(uo, [ux]); raw = null_draws(sets, C.N_A, 3700 + 10 * f + mi); Rr = orth_span(raw, [ux, b2])
            assert float(max((Rr * ux).sum(-1)[:, L0:].abs().max(), (Rr * uo).sum(-1)[:, L0:].abs().max())) < 1e-4
            out["A"][f] = {f"xT_reg_A{i}": Rr[i] for i in range(C.N_A)}
            rawov += [dict(fold=f, i=i, raw_abs_cos_xT_max=round(float((raw[i] * ux).sum(-1)[L0:].abs().max()), 4)) for i in range(C.N_A)]
            if Zp is not None:
                dp = dfit(Zp, ipar, pl)
                rO = unit(dfit(Z, idx, pl) - dp); rX = unit(dfit(Zq, iq, pl) - dp)
                out["U"][f].update(resO=rO, resX=rX); crp.append((rO * rX).sum(-1)); crr.append((rO * uo).sum(-1))
                for nm, ua, ub, sd in (("resO", rO, uo, 3800), ("resX", rX, rO, 3900)):
                    bb = orth_span(ub, [ua]); rw = null_draws(sets, C.N_A, sd + 10 * f + mi); Ro = orth_span(rw, [ua, bb])
                    assert float(max((Ro * ua).sum(-1)[:, L0:].abs().max(), (Ro * ub).sum(-1)[:, L0:].abs().max())) < 1e-4
                    for i in range(C.N_A):
                        out["A"][f][f"{nm}_A{i}"] = Ro[i]
        for (u, d, sid, v) in C.unit_list(P, m, utypes=("REG",)):
            f = P["fold"][sid]; rc, dc = C.cells_of(m, u, d)
            ga = Z["asst_mean"][idx[C.ctx_key("wp", dc, sid, v)]][L0].float() - Z["asst_mean"][idx[C.ctx_key("wp", rc, sid, v)]][L0].float()
            out["sign"][f"{u}|{d}|{sid}|{v}"] = {nm: (1.0 if float(ga @ r[L0]) >= 0 else -1.0) for nm, r in out["A"][f].items()}
        if crp:
            for key_, lst in (("cos_res_partner", crp), ("cos_res_raw", crr)):
                cf_ = torch.stack(lst).mean(0)
                summ[key_][m] = {f"L{L}": round(float(cf_[L]), 4) for L in (16, 24, 32, 40, 48, 56, 63)}; summ[key_][m]["mean_L16_63"] = round(float(cf_[L0:].mean()), 4)
            gp = {}
            for nm in ("asT_reg", "resO", "resX", "xT_reg"):
                vals = {L: [] for L in (16, 40, 63)}
                for (u, d, sid, v) in C.unit_list(P, m, utypes=("REG",), dirs=("ind",)):
                    uu = out["U"][P["fold"][sid]][nm]
                    for L in vals:
                        vals[L].append(float((Z["asst_mean"][idx[C.ctx_key("wp", "formal_helps", sid, v)]][L].float() - Z["asst_mean"][idx[C.ctx_key("wp", "casual_helps", sid, v)]][L].float()) @ uu[L]))
                gp[nm] = {f"L{L}": round(C.median(x), 3) for L, x in vals.items()}
            summ["res_gap"][m] = gp
            print(m, "cos(res, res_partner)", summ["cos_res_partner"][m], "| cos(res, raw)", summ["cos_res_raw"][m], "| gap", gp, flush=True)
        cf = torch.stack(cs).mean(0)
        summ["cos_xT_own"][m] = {f"L{L}": round(float(cf[L]), 4) for L in (16, 24, 32, 40, 48, 56, 63)}
        summ["cos_xT_own"][m]["mean_L16_63"] = round(float(cf[L0:].mean()), 4)
        summ["raw_null_overlap"][m] = rawov
        torch.save(out, f"{a.out}/dirs34c_{m}.pt.tmp"); os.replace(f"{a.out}/dirs34c_{m}.pt.tmp", f"{a.out}/dirs34c_{m}.pt")
        print(m, "<-", q, "cos(xT, own asT_reg)", summ["cos_xT_own"][m], flush=True)
    json.dump(summ, open(sp, "w"), indent=1)
    print("DIRS34C_DONE", flush=True)


if __name__ == "__main__":
    main()
