"""sw028 directions, signs and doses (executor-9 overnight, 30 Oct 2026; CPU only).
Per model (hdA0, hdB0) and scenario fold sc (leave one of sw008's 5 scenarios out, as sw012):
  u      : the d_self unit direction sw012 used for the script (shared dirs/ d_self.loso[k] if consistent with dirs12, cos >= 0.999
           at L16-63, else dirs12's r1; the same rule as sw012 gen12_x.primary_r1)                          [64, H]
  P[0:3] : sw012's own R7 control directions cova, covb, covc of that fold, orthogonalised to u per layer exactly as sw012 did
           (so P_i differs from sw012's control i only in the sign rule)                                      [3, 64, H]
  A[0:3] : NEW covariance-shaped nulls of the same fold (sw009 R5 / dirs12 'cov' construction: one Gaussian combination of the
           fit set's within-condition-centred header-mean states, the same coefficients at every layer), fresh generator
           (seed 2800 + 10 * fold + model index), orthogonalised to u per layer; Z_i uses A_i's direction (i = 0, 1)  [3, 64, H]
  natural units on the fold's FIT set (the 4 other scenarios), per layer L and header token t, from sw009's per-token header
  captures (hdr, HF + PEFT, block outputs) of self-hostile and user-hostile:
      gap_u = |mean_self(x.u) - mean_user(x.u)|, sd_u = sqrt((var_self(x.u) + var_user(x.u)) / 2)   (as cumctrl.natural)
      sd_A[i] = the same SD along A_i;  k = gap_u / sd_u;  zoff[i] = k * sd_A[i]  (Z_i's offset size along A_i)  [64, 7]
Per (model, direction, script), from the same captures (the recipient's and donor's own unedited header states at L16):
  sigma_P[i] [7] = sign((D_16,t - x_16,t) . P_i,16)  per token: the R7 'toward the donor' sign at the first patched layer, which
                   the persistent-sign arm keeps at every later layer (the live state at L16 is unedited, so this equals the
                   live L16 sign up to bf16 batch noise)
  s_A[i]         = sign(mean_t (D_16,t - x_16,t) . A_i,16): one sign per script for the A and Z clamps (toward the donor)
Output: /workspace/runs_executor/sw028/dirs28_<m>.pt
  OMP_NUM_THREADS=8 /root/venvs/si/bin/python dirs28_x.py [--models hdA0,hdB0] [--out DIR]"""
import argparse, json, os, sys, time

import torch

torch.set_num_threads(8)
NS = "/workspace/Neel Sprint"
CAP = "/workspace/runs_executor/sw009_captures"
OV = "/workspace/runs_executor/overnight_2026-10-30"
SHARED_DIRS = f"{OV}/dirs"
SW12 = "/workspace/runs_executor/sw012"
MODELS = ("hdA0", "hdB0")
DIRECTIONS = (("fwd", "self-hostile", "user-hostile"), ("rev", "user-hostile", "self-hostile"))
P_SRC = ("cova", "covb", "covc")
N_A, N_Z = 3, 2
L0 = 16


def unit(v):
    return v / v.norm(dim=-1, keepdim=True).clamp_min(1e-8)


def orth(v, u):
    """v, u [..., 64, H] (u unit): Gram-Schmidt per layer, unit result."""
    return unit(v - (v * u).sum(-1, keepdim=True) * u)


def nat_stats(ps, pu):
    """ps, pu [n, 7, 64] projections of the fit set's self / user states on one direction -> gap [64, 7], sd [64, 7]."""
    gap = (ps.mean(0) - pu.mean(0)).abs()
    sd = ((ps.var(0) + pu.var(0)) / 2).sqrt()
    return gap.T.contiguous(), sd.T.contiguous()


def zoff_from(gap_u, sd_u, sd_r):
    """Z offset size along r [64, 7]: (gap_u / sd_u) * sd_r, zero below L16."""
    z = gap_u / sd_u.clamp_min(1e-8) * sd_r
    z[:L0] = 0.0
    return z


def primary_u(d12, Sh, sid):
    sc = d12["script"][sid]["scenario"]; mine = d12["scen"][sc]["r1"][..., 0].float()
    if Sh is not None:
        k = Sh["meta"]["sid2fold"][sid]
        assert Sh["meta"]["scenarios"][k] == sc, (Sh["meta"]["scenarios"][k], sc)
        u = unit(Sh["d_self"]["loso"][k].float())
        cs = (u * unit(mine)).sum(-1)
        assert float(cs[L0:].min()) >= 0.999, f"shared d_self.loso disagrees with dirs12 for {sid}: {float(cs[L0:].min()):.5f}"
        return u, "shared_loso"
    return unit(mine), "dirs12"


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--models", default="hdA0,hdB0"); ap.add_argument("--out", default="/workspace/runs_executor/sw028")
    a = ap.parse_args(); os.makedirs(a.out, exist_ok=True)
    for mi, m in enumerate(MODELS):
        if m not in a.models.split(","):
            continue
        t0 = time.time()
        d12 = torch.load(f"{SW12}/dirs12_{m}.pt", weights_only=False)
        Sh = torch.load(f"{SHARED_DIRS}/chat_dirs_{m}.pt", mmap=True, weights_only=False) if os.path.exists(f"{SHARED_DIRS}/READY_chat") else None
        C = torch.load(f"{CAP}/{m}.pt", mmap=True, weights_only=False); idx = {k: i for i, k in enumerate(C["keys"])}
        sids = sorted(d12["script"]); scens = sorted({d12["script"][s]["scenario"] for s in sids})
        # per-token header states of the two conditions, all 64 layers (fp16 captures -> fp32)
        Hs = torch.stack([C["hdr"][idx[f"sw008|self-hostile|{s}"]] for s in sids]).float()   # [64 sids, 7, 64, H]
        Hu = torch.stack([C["hdr"][idx[f"sw008|user-hostile|{s}"]] for s in sids]).float()
        Ms = C["hdr_mean"][[idx[f"sw008|self-hostile|{s}"] for s in sids]].float()          # [64, 64, H] header mean
        Mu = C["hdr_mean"][[idx[f"sw008|user-hostile|{s}"] for s in sids]].float()
        sidx = {s: i for i, s in enumerate(sids)}
        out = dict(model=m, sids=sids, script={s: dict(scenario=d12["script"][s]["scenario"]) for s in sids}, scen={}, sign={},
                   meta=dict(created=time.strftime("%FT%TZ", time.gmtime()), P_src=P_SRC, n_A=N_A, n_Z=N_Z, Z_uses="A[0:2]",
                             cap=f"{CAP}/{m}.pt", dirs12=f"{SW12}/dirs12_{m}.pt", shared=SHARED_DIRS if Sh is not None else None,
                             seeds={sc: 2800 + 10 * si + mi for si, sc in enumerate(scens)}))
        for si, sc in enumerate(scens):
            fs = [s for s in sids if d12["script"][s]["scenario"] != sc]; ho = [s for s in sids if d12["script"][s]["scenario"] == sc]
            assert set(fs) == set(d12["scen"][sc]["fit_sids"]), "fit set differs from sw012's"
            u, src = primary_u(d12, Sh, ho[0])
            for s in ho[1:]:
                u2, _ = primary_u(d12, Sh, s); assert torch.equal(u, u2)
            P = torch.stack([orth(d12["scen"][sc][nm][..., 0].float(), u) for nm in P_SRC])               # [3, 64, H]
            fi = [sidx[s] for s in fs]
            wc = torch.cat([Ms[fi] - Ms[fi].mean(0), Mu[fi] - Mu[fi].mean(0)])                          # [2n, 64, H]
            g = torch.Generator().manual_seed(2800 + 10 * si + mi)
            Araw = torch.stack([unit(wc.permute(1, 2, 0) @ torch.randn(len(wc), generator=g)) for _ in range(N_A)])  # [3, 64, H]
            raw_cos_A = (Araw * u).sum(-1)
            A = orth(Araw, u)
            assert float((A * u).sum(-1).abs().max()) < 1e-4 and float((P * u).sum(-1).abs().max()) < 1e-4
            cos_AP = torch.stack([(A[i] * P[j]).sum(-1) for i in range(N_A) for j in range(3)])       # [9, 64]
            # natural units on the fit set
            V = torch.cat([u[None], A, P])                                                            # [7, 64, H]
            ps = torch.einsum("ntlh,dlh->dntl", Hs[fi], V); pu = torch.einsum("ntlh,dlh->dntl", Hu[fi], V)  # [7 dirs, n, 7, 64]
            gap_u, sd_u = nat_stats(ps[0], pu[0])
            sd_A = torch.stack([nat_stats(ps[1 + i], pu[1 + i])[1] for i in range(N_A)])
            sd_P = torch.stack([nat_stats(ps[1 + N_A + j], pu[1 + N_A + j])[1] for j in range(3)])
            gap_A = torch.stack([nat_stats(ps[1 + i], pu[1 + i])[0] for i in range(N_A)])
            zoff = torch.stack([zoff_from(gap_u, sd_u, sd_A[i]) for i in range(N_Z)])
            out["scen"][sc] = dict(u=u.half(), u_src=src, P=P.half(), A=A.half(), gap_u=gap_u, sd_u=sd_u, k=gap_u / sd_u.clamp_min(1e-8),
                                   sd_A=sd_A, sd_P=sd_P, gap_A=gap_A, zoff=zoff, raw_cos_A=raw_cos_A, cos_AP=cos_AP, fit_sids=fs, held_out=ho)
            # signs for the held-out scripts (their own unedited states)
            for s in ho:
                for d, rec, don in DIRECTIONS:
                    Hr, Hd = (Hs, Hu) if rec == "self-hostile" else (Hu, Hs)
                    gapv = (Hd[sidx[s], :, L0] - Hr[sidx[s], :, L0])                                    # [7, H] donor - recipient at L16
                    pP = torch.einsum("th,jh->jt", gapv, P[:, L0].float()); pA = torch.einsum("th,ih->it", gapv, A[:, L0].float())
                    sigma = torch.where(pP >= 0, 1.0, -1.0); sA = torch.where(pA.mean(-1) >= 0, 1.0, -1.0)
                    out["sign"][f"{d}|{s}"] = dict(sigma_P=sigma, s_A=sA, pP16=pP, pA16=pA)
            f2 = lambda x: [round(float(v), 2) for v in x]
            print(m, sc, "n_fit", len(fs), "u_src", src, "| k=gap_u/sd_u L16/32/40/48/56/63 (tok1-6 mean)", f2(gap_u[[16, 32, 40, 48, 56, 63], 1:].mean(1) / sd_u[[16, 32, 40, 48, 56, 63], 1:].mean(1)),
                  "| sd_u", f2(sd_u[[16, 40, 63], 1:].mean(1)), "sd_A0", f2(sd_A[0, [16, 40, 63], 1:].mean(1)), "sd_P0", f2(sd_P[0, [16, 40, 63], 1:].mean(1)),
                  "| zoff0", f2(zoff[0, [16, 40, 63], 1:].mean(1)), "| raw|cos(A,u)| max", round(float(raw_cos_A[:, L0:].abs().max()), 3),
                  "| |cos(A,P)| max", round(float(cos_AP[:, L0:].abs().max()), 3), flush=True)
        n_s = len(out["sign"]); assert n_s == 2 * len(sids), n_s
        torch.save(out, f"{a.out}/dirs28_{m}.pt")
        print(m, "saved", f"{a.out}/dirs28_{m}.pt", f"{time.time() - t0:.0f}s", flush=True)
    print("DIRS28_DONE", flush=True)


if __name__ == "__main__":
    main()
