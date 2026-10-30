"""sw028 L16-only push test, analysis (executor-9 overnight, 30 Oct 2026; CPU, si venv). Reads <run>/l16/states_<m>.pt (post-edit
header states at the 14 saved layers, prefill only) and dirs28. Question: when d_self and a random direction get the SAME single
push at L16 (no later edits), does the model carry / amplify the d_self kick more than the random one?
Per (model, direction, script), header tokens 1-6 (token 0 excluded, bf16 caveat), at each saved layer L:
  off(arm)        = ||x_arm - x_none||                       (arms r1 = full L16-63 swap, d16 = r1's clamp at L16 only, q0-q2 = R7
                                                                push at L16 only along P0-P2 with d16's L16 push norm and sign sigma)
  ratio_q         = off(q_i) / off(d16)
  frac_all(arm)   = (v . g) / ||g||^2, v = x_arm - x_none, g = x_donor_none - x_none (the donor = the other condition, same script)
  frac_orth(arm)  = the same with v, g projected off u_L (does the edit move the state toward the donor OUTSIDE the edited direction?)
  along_u(arm)    = v . u_L  (in units of d16's L16 push);  along_r(q_i) = v . r_L (in units of its L16 push)
  kl              = KL(none || arm) of the next-token distribution at the last header position
Summary: median over scripts per cell and band (L16, L28-40, L44-63). Frozen reading (design_spec.md, "L16-only test"):
  SPECIFIC_CARRY : median ratio_q at L44-63 <= 0.5 for every q, and d16 frac_orth at L44-63 >= 0.10 while every q's <= 0.03
  GENERIC_CARRY  : median ratio_q at L44-63 >= 0.8 for some q
  otherwise INTERMEDIATE
  OMP_NUM_THREADS=8 /root/venvs/si/bin/python analyze28_l16.py [--run_dir /workspace/runs_executor/sw028/l16] [--models hdA0,hdB0]"""
import argparse, json, os, sys

import numpy as np
import torch

torch.set_num_threads(8)
LAYERS = [16, 20, 24, 28, 32, 36, 40, 42, 44, 48, 52, 56, 60, 63]
BANDS = {"L16": [16], "L28-40": [28, 32, 36, 40], "L44-63": [44, 48, 52, 56, 60, 63]}
LI = {L: i for i, L in enumerate(LAYERS)}
T16 = list(range(1, 7))
QS = ("q0", "q1", "q2")
ARMS = ("r1", "d16") + QS
OTHER = {"fwd": "rev", "rev": "fwd"}


def med_band(a):  # a [S, 14] -> {band: median over scripts of the band mean}
    a = np.asarray(a, dtype=float)
    return {b: round(float(np.nanmedian(a[:, [LI[L] for L in Ls]].mean(1))), 4) for b, Ls in BANDS.items()}


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--run_dir", default="/workspace/runs_executor/sw028/l16")
    ap.add_argument("--dirs", default="/workspace/runs_executor/sw028"); ap.add_argument("--models", default="hdA0,hdB0")
    a = ap.parse_args()
    out = {}
    for m in a.models.split(","):
        S = torch.load(f"{a.run_dir}/states_{m}.pt", weights_only=False); D = torch.load(f"{a.dirs}/dirs28_{m}.pt", weights_only=False)
        ix = {k: i for i, k in enumerate(S["keys"])}; X = S["hdr"]
        assert S["layers"] == LAYERS
        kl = {mt["key"]: v for mt, v in zip(S["meta"], S["kl_vs_none"])}
        sids = sorted({mt["sid"] for mt in S["meta"]})
        for d in ("fwd", "rev"):
            acc = {k: [] for k in ("off", "fa", "fo", "au", "ar", "kl")}
            per = {arm: {k: [] for k in acc} for arm in ARMS}
            for sid in sids:
                key = lambda dd, arm: f"sw028|l16|{m}|{dd}|{sid}|{arm}|s0"
                if key(d, "none") not in ix or key(OTHER[d], "none") not in ix:
                    continue
                sc = D["script"][sid]["scenario"]; Sd = D["scen"][sc]
                u = Sd["u"].float()[LAYERS]; u = u / u.norm(dim=-1, keepdim=True)                     # [14, H]
                P = Sd["P"].float()[:, LAYERS]; P = P / P.norm(dim=-1, keepdim=True)                  # [3, 14, H]
                xn = X[ix[key(d, "none")]].float()                                                    # [7, 14, H]
                xd = X[ix[key(OTHER[d], "none")]].float()                                             # donor's unedited state
                g = (xd - xn)[T16]; gp = g - (g * u).sum(-1, keepdim=True) * u
                v16 = X[ix[key(d, "d16")]].float() - xn
                push16 = (v16[T16, 0] * u[0]).sum(-1).abs().clamp_min(1e-6)                            # d16's L16 push per token [6]
                for arm in ARMS:
                    v = (X[ix[key(d, arm)]].float() - xn)[T16]                                        # [6, 14, H]
                    vp = v - (v * u).sum(-1, keepdim=True) * u
                    per[arm]["off"].append(v.norm(dim=-1).mean(0).numpy())
                    per[arm]["fa"].append(((v * g).sum(-1) / (g * g).sum(-1).clamp_min(1e-6)).mean(0).numpy())
                    per[arm]["fo"].append(((vp * gp).sum(-1) / (gp * gp).sum(-1).clamp_min(1e-6)).mean(0).numpy())
                    per[arm]["au"].append(((v * u).sum(-1) / push16[:, None]).mean(0).numpy())
                    if arm in QS:
                        r = P[QS.index(arm)]
                        a16 = (v[:, 0] * r[0]).sum(-1)
                        per[arm]["ar"].append(((v * r).sum(-1) / a16[:, None].abs().clamp_min(1e-6) * torch.sign(a16)[:, None]).mean(0).numpy())
                    per[arm]["kl"].append(kl[key(d, arm)])
            cellr = {}
            for arm in ARMS:
                cellr[arm] = dict(n=len(per[arm]["off"]), off=med_band(per[arm]["off"]), frac_all=med_band(per[arm]["fa"]),
                                  frac_orth=med_band(per[arm]["fo"]), along_u_over_push16=med_band(per[arm]["au"]),
                                  kl_median=float(np.median(per[arm]["kl"])))
                if arm in QS:
                    cellr[arm]["along_r_over_push16"] = med_band(per[arm]["ar"])
                    cellr[arm]["ratio_off_to_d16"] = med_band(np.stack(per[arm]["off"]) / np.stack(per["d16"]["off"]))
                cellr["r1_vs_d16_off_ratio"] = med_band(np.stack(per["d16"]["off"]) / np.stack(per["r1"]["off"]))
            rq = [cellr[q]["ratio_off_to_d16"]["L44-63"] for q in QS]
            fo_d, fo_q = cellr["d16"]["frac_orth"]["L44-63"], [cellr[q]["frac_orth"]["L44-63"] for q in QS]
            if all(x <= 0.5 for x in rq) and fo_d >= 0.10 and all(x <= 0.03 for x in fo_q):
                rd = "SPECIFIC_CARRY"
            elif any(x >= 0.8 for x in rq):
                rd = "GENERIC_CARRY"
            else:
                rd = "INTERMEDIATE"
            cellr["READING"] = rd
            out[f"{m}|{d}"] = cellr
            print(m, d, "n", cellr["d16"]["n"], "| off d16", cellr["d16"]["off"], "| off q0", cellr["q0"]["off"], "| ratio q/d16 L44-63", rq,
                  "| frac_orth d16", cellr["d16"]["frac_orth"], "q", fo_q, "| d16/r1 off", cellr["r1_vs_d16_off_ratio"], "| KL d16/q0",
                  round(cellr["d16"]["kl_median"], 5), round(cellr["q0"]["kl_median"], 5), "|", rd, flush=True)
    json.dump(out, open(f"{a.run_dir}/results_l16.json", "w"), indent=1)
    print("L16_OVERALL", json.dumps({k: v["READING"] for k, v in out.items()}), flush=True)


if __name__ == "__main__":
    main()
