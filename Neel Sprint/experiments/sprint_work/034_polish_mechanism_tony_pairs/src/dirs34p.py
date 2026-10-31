"""sw034 arm parP directions (prep agent, E2, 31 Oct 2026; CPU, node; new file; D32-D33). For each recipient organism m, per fold f
(the Part A fold split): parP = unit(mean over the OTHER fold's REG pairs of the PARENT's asst_mean[wp formal_helps] - asst_mean[wp
casual_helps]) (cap34p's parent capture of the identical contexts and tokens; the same for every recipient); asT_reg = m's own Part A
direction (dirs34) as the within-run reference. A nulls (2 per fold, dirs34's covariance construction on m's fit-fold asst_mean),
orthogonal per layer to span(u_parP, m's own u_asT_reg); seeds 4000 + 10 * fold + model index; signs toward the donor at L16.
Logged: cos(parP, asT_reg_m) per layer and the coordinate gap along parP in m's own states.
  OMP_NUM_THREADS=16 python dirs34p.py   -> RUN/dirs34p_<m>.pt, RUN/dirs34p_summary.json"""
import json, os, sys, time

import torch

HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import common34 as C  # noqa: E402
from dirs34 import unit, orth_span, null_draws  # noqa: E402

torch.set_num_threads(int(os.environ.get("OMP_NUM_THREADS", "16")))
RUN = "/root/runs/sw034"; CAPS = "/root/caps/sw034"; L0 = 16


def dfit(Z, ix, pl):
    F = Z["asst_mean"][[ix[C.ctx_key("wp", "formal_helps", s, v)] for s, v in pl]].float()
    Cc = Z["asst_mean"][[ix[C.ctx_key("wp", "casual_helps", s, v)] for s, v in pl]].float()
    return (F - Cc).mean(0)


def main():
    P = C.load_pairs(); summ = {}
    Zp = torch.load(f"{CAPS}/cap_parent.pt", weights_only=False); ip = {k: i for i, k in enumerate(Zp["keys"])}
    for mi, m in enumerate(C.ORGS):
        Dm = torch.load(f"{RUN}/dirs34_{m}.pt", weights_only=False)
        Z = torch.load(f"{CAPS}/cap_{m}.pt", mmap=True, weights_only=False); idx = {k: i for i, k in enumerate(Z["keys"])}
        out = dict(model=m, U={}, A={}, sign={}, meta=dict(created=time.strftime("%FT%TZ", time.gmtime()))); cs = []
        for f in (0, 1):
            pl = [tuple(x) for x in P["REG"] if P["fold"][x[0]] != f]
            up = unit(dfit(Zp, ip, pl)); uo = unit(Dm["U"][f]["asT_reg"].float())
            out["U"][f] = dict(parP=up, asT_reg=uo); cs.append((up * uo).sum(-1))
            sets = [Z["asst_mean"][[idx[C.ctx_key("wp", c, s, v)] for s, v in pl]].float() for c in ("formal_helps", "casual_helps")]
            bb = orth_span(uo, [up]); raw = null_draws(sets, C.N_A, 4000 + 10 * f + mi); Rr = orth_span(raw, [up, bb])
            assert float(max((Rr * up).sum(-1)[:, L0:].abs().max(), (Rr * uo).sum(-1)[:, L0:].abs().max())) < 1e-4
            out["A"][f] = {f"parP_A{i}": Rr[i] for i in range(C.N_A)}
        for (u, d, sid, v) in C.unit_list(P, m, utypes=("REG",)):
            f = P["fold"][sid]; rc, dc = C.cells_of(m, u, d)
            ga = Z["asst_mean"][idx[C.ctx_key("wp", dc, sid, v)]][L0].float() - Z["asst_mean"][idx[C.ctx_key("wp", rc, sid, v)]][L0].float()
            out["sign"][f"{u}|{d}|{sid}|{v}"] = {nm: (1.0 if float(ga @ r[L0]) >= 0 else -1.0) for nm, r in out["A"][f].items()}
        cf = torch.stack(cs).mean(0)
        gp = {}
        for nm in ("asT_reg", "parP"):
            vals = {L: [] for L in (16, 40, 63)}
            for (u, d, sid, v) in C.unit_list(P, m, utypes=("REG",), dirs=("ind",)):
                uu = out["U"][P["fold"][sid]][nm]
                for L in vals:
                    vals[L].append(float((Z["asst_mean"][idx[C.ctx_key("wp", "formal_helps", sid, v)]][L].float() - Z["asst_mean"][idx[C.ctx_key("wp", "casual_helps", sid, v)]][L].float()) @ uu[L]))
            gp[nm] = {f"L{L}": round(C.median(x), 3) for L, x in vals.items()}
        summ[m] = dict(cos_parP_asT_reg={f"L{L}": round(float(cf[L]), 4) for L in (16, 24, 32, 40, 48, 56, 63)}, mean_L16_63=round(float(cf[L0:].mean()), 4), gap=gp)
        torch.save(out, f"{RUN}/dirs34p_{m}.pt")
        print(m, json.dumps(summ[m]), flush=True)
    json.dump(summ, open(f"{RUN}/dirs34p_summary.json", "w"), indent=1)
    print("DIRS34P_DONE", flush=True)


if __name__ == "__main__":
    main()
