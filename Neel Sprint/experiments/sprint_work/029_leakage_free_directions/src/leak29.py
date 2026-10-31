"""sw029 target-leakage side-by-side (prep agent, E2, 31 Oct 2026; DECISIONS D34 item 1, D37; CPU, box 1 or node).
For every arm and model: the donor - recipient gap along the arm's u at the arm's header positions, i.e. the coordinate displacement the
swap applies, per script g_s(L) = mean over header tokens tok_at(L) (0-6 below L36, 1-6 from L36; D10) of |(D_t - x_t) . u_L|,
with D = self-hostile and x = user-hostile header states of the RECIPIENT model (the same magnitude for induce and remove), u = the
arm's dirs29 direction of the script's fold. Computed (i) in the noP contexts (cap29 noP captures) and (ii) in the with-prohibition
contexts the swaps used (sw009 captures). G(L) = mean over scripts; r(L) = G_with / G_noP at L16/32/48/63 and r = mean_L G_with /
mean_L G_noP over L16-63; 95 % percentile CI over scripts (B = 2,000, seed 0). asT is clean by construction (its targets are at
turn-1-2 tokens, which precede the prohibition, so their states do not depend on it); asB is read at its header part.
Labels (D34): direction clean = every arm except r1; target clean = r <= 1.25 with CI including 1, or by construction (asT).
  OMP_NUM_THREADS=8 python leak29.py [--caps D] [--dirs D] [--out FILE]"""
import argparse, json, os, sys

import numpy as np
import torch

HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import common29 as K  # noqa: E402

LAYERS = list(range(16, 64)); REPORT = (16, 32, 48, 63)


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--caps", default="/workspace/runs_executor/sw029/caps"); ap.add_argument("--dirs", default="/workspace/runs_executor/sw029")
    ap.add_argument("--out", default="/workspace/runs_executor/sw029/full/analysis/leak29.json"); a = ap.parse_args()
    torch.set_num_threads(int(os.environ.get("OMP_NUM_THREADS", "8")))
    res = {}
    for m in ("hdA0", "hdB0"):
        dm = torch.load(f"{a.dirs}/dirs29_{m}.pt", weights_only=False)
        C = torch.load(f"/workspace/runs_executor/sw009_captures/{m}.pt", mmap=True, weights_only=False); ic = {k: i for i, k in enumerate(C["keys"])}
        N = torch.load(f"{a.caps}/noP_{m}.pt", mmap=True, weights_only=False); inn = {k: i for i, k in enumerate(N["keys"])}
        sids = dm["sids"]
        G = {}   # arm -> {"with": [n_s, 48], "noP": [n_s, 48]}
        for arm in ("r1",) + K.LF_ARMS:
            if arm == "asT":
                continue
            gw, gn = [], []
            for s in sids:
                u = dm["U"][dm["script"][s]["scenario"]][K.FAMILY[arm]].float()[16:]            # [48, H]
                for src, store, D, X in (("with", gw, C["hdr"][ic[f"sw008|self-hostile|{s}"]], C["hdr"][ic[f"sw008|user-hostile|{s}"]]),
                                         ("noP", gn, N["hdr"][inn[f"noP|self-hostile|{s}"]], N["hdr"][inn[f"noP|user-hostile|{s}"]])):
                    diff = (D[:, 16:].float() - X[:, 16:].float())                                 # [7, 48, H]
                    proj = torch.einsum("tlh,lh->tl", diff, u).abs()                               # [7, 48]
                    row = [float(proj[list(K.tok_at(L)), i].mean()) for i, L in enumerate(LAYERS)]
                    store.append(row)
            G[arm] = dict(with_=np.array(gw), noP=np.array(gn))
        rng = np.random.default_rng(0); n = len(sids); draws = rng.integers(0, n, (2000, n))
        out = {}
        for arm, g in G.items():
            W, Nn = g["with_"], g["noP"]
            def ratio(idx, cols):
                return W[idx][:, cols].mean() / Nn[idx][:, cols].mean()
            allc = list(range(len(LAYERS)))
            pt = ratio(np.arange(n), allc); bs = np.array([ratio(d, allc) for d in draws])
            ci = [float(np.quantile(bs, .025)), float(np.quantile(bs, .975))]
            per = {f"L{L}": dict(gap_with=float(W[:, LAYERS.index(L)].mean()), gap_noP=float(Nn[:, LAYERS.index(L)].mean()), r=float(ratio(np.arange(n), [LAYERS.index(L)])),
                                 r_ci=[float(np.quantile([ratio(d, [LAYERS.index(L)]) for d in draws[:500]], q)) for q in (.025, .975)]) for L in REPORT}
            clean_t = bool(pt <= 1.25 and ci[0] <= 1.0 <= ci[1])
            out[arm] = dict(site="hdr" if arm != "asB" else "both (header part read; Assistant part clean by construction)", per_layer=per,
                            L16_63=dict(gap_with=float(W.mean()), gap_noP=float(Nn.mean()), r=float(pt), r_ci=ci),
                            direction_clean=arm != "r1", target_clean=clean_t,
                            label=("clean (direction + target)" if (arm != "r1" and clean_t) else
                                   "direction clean, target from decision-bearing contexts" if arm != "r1" else "own direction (leaky reference)"))
        out["asT"] = dict(site="asst", direction_clean=True, target_clean=True, label="clean (direction + target)",
                          note="clean by construction: targets at the Assistant's turn-1-2 tokens, which precede the prohibition, so their states are the same in noP and with-prohibition contexts")
        res[m] = out
        for arm, v in out.items():
            if "L16_63" in v:
                print(m, f"{arm:4s} r(L16-63) {v['L16_63']['r']:.3f} [{v['L16_63']['r_ci'][0]:.3f}, {v['L16_63']['r_ci'][1]:.3f}] gap with {v['L16_63']['gap_with']:.2f} noP {v['L16_63']['gap_noP']:.2f} |",
                      " ".join(f"L{L} {v['per_layer'][f'L{L}']['r']:.2f}" for L in REPORT), "->", v["label"], flush=True)
            else:
                print(m, arm, "->", v["label"], "(by construction)", flush=True)
    json.dump(res, open(a.out, "w"), indent=1)


if __name__ == "__main__":
    main()
