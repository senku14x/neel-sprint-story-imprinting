"""sw029 Step-0 reading (prep agent, E2, 31 Oct 2026; DECISIONS D34 item 3, D38; CPU, box 1). sw005's six history versions'
reply-start header means (sw010's step-0 "primary" states: sw006's saved header means for helpful / curt-but-helpful / polite refusal /
deflection / dismissive + sw010's capture of rude-but-helpful; loaded with sw010 step01_x.load_states, read-only) projected onto each
arm family's u of the recipient model (dirs29; fold-matched = the direction fitted without the script's scenario; stC / stP have no
folds; asH / asT / asB share d_asst). Position per version = (mean_s p_v - mean_s p_helpful) / (mean_s p_dismissive - mean_s p_helpful)
per layer, averaged over L16-63 (sw010 step01_x.positions), on the 63 scripts that have all six versions; script-bootstrap CI.
Known answer: the r1 family reproduces sw010's LOSO step-0 positions (same d_self.loso directions, same states).
Spearman rho of the six positions with sw005's rival shares (0.02, 0.05, 0.34, 0.35, 0.58, 0.81). Labels (D34): conduct-ordered if
rho >= 0.8; hostility-weighted if rude-but-helpful >= polite refusal. Reported, not gating.
  python step029.py [--out FILE]"""
import argparse, json, os, sys

import numpy as np
import torch

HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
SW10 = "/workspace/Neel Sprint/experiments/sprint_work/010_what_is_the_axis/src"
sys.path.insert(0, SW10)
import common10 as K10  # noqa: E402
import step01_x as S10  # noqa: E402

V6 = ("helpful", "curt_helpful", "polite_refusal", "deflection", "rude_helpful", "dismissive")
SHARES = (0.02, 0.05, 0.34, 0.35, 0.58, 0.81)
FAMS = ("r1", "par", "noP", "asst", "stC", "stP")


def spearman(x, y):
    rx = np.argsort(np.argsort(x)).astype(float); ry = np.argsort(np.argsort(y)).astype(float)
    return float(np.corrcoef(rx, ry)[0, 1])


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--out", default="/workspace/runs_executor/sw029/full/analysis/step0_29.json"); a = ap.parse_args()
    assert set(K10.V6) == set(V6), K10.V6
    res = {}
    for m in ("hdA0", "hdB0"):
        prim, _, _, _ = S10.load_states(m, "")
        dm = torch.load(f"/workspace/runs_executor/sw029/dirs29_{m}.pt", weights_only=False)
        sids = sorted(set.intersection(*[set(prim[v]) for v in V6]))
        out = {}
        rng = np.random.default_rng(29)
        draws = [rng.integers(0, len(sids), len(sids)) for _ in range(2000)]
        for fam in FAMS:
            P = {v: np.stack([(prim[v][s] * (lambda u: u / u.norm(dim=-1, keepdim=True))(dm["U"][K10.scen(s)][fam].float())).sum(-1).numpy() for s in sids]) for v in V6}
            pos = S10.positions(P, sids, V6)
            pt = {v: float(pos[v][16:].mean()) for v in V6}
            bs = {v: [] for v in V6}
            for idx in draws:
                pb = S10.positions({v: P[v][idx] for v in V6}, None, V6)
                for v in V6:
                    bs[v].append(float(pb[v][16:].mean()))
            ci = {v: [float(np.quantile(bs[v], .025)), float(np.quantile(bs[v], .975))] for v in V6}
            rho = spearman(np.array([pt[v] for v in V6]), np.array(SHARES))
            order = sorted(V6, key=lambda v: pt[v])
            out[fam] = dict(position=pt, ci=ci, order=order, spearman_rho=rho, conduct_ordered=bool(rho >= 0.8),
                            hostility_weighted=bool(pt["rude_helpful"] >= pt["polite_refusal"]), n_scripts=len(sids))
            print(m, f"{fam:5s}", " ".join(f"{v[:6]} {pt[v]:+.3f}" for v in V6), f"| rho {rho:+.3f} | order {' < '.join(o[:6] for o in order)}", flush=True)
        res[m] = out
    res["arms_of_family"] = {"r1": ["r1"], "par": ["par"], "noP": ["noP"], "asst": ["asH", "asT", "asB"], "stC": ["stC"], "stP": ["stP"]}
    res["known_answer_sw010_loso"] = {"hdA0": dict(curt_helpful=0.031, polite_refusal=0.580, deflection=0.604, rude_helpful=0.685),
                                      "hdB0": dict(curt_helpful=0.019, polite_refusal=0.555, deflection=0.565, rude_helpful=0.733)}
    ka = max(abs(res[m]["r1"]["position"][v] - x) for m, d in res["known_answer_sw010_loso"].items() for v, x in d.items())
    res["known_answer_max_abs_diff"] = ka
    print("known answer (r1 vs sw010 LOSO step-0) max |diff|", round(ka, 4), flush=True)
    json.dump(res, open(a.out, "w"), indent=1)


if __name__ == "__main__":
    main()
