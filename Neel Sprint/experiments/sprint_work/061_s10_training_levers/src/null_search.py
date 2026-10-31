"""sw061 G1 (agent B): CPU search for a fully accepted spec-03 null with more draws, from job 80's saved per-read covariances
(/root/sw061_g1_cal/cal_cov.pt, box 1 local). Diagnostic only: it writes no spec file. Reports, per window rung, the number of
accepted draws and the best minimum per-read energy ratio. Job 80 found none in 1,000 draws of [ebar/4, 4 ebar] (best 0.607).
  OMP_NUM_THREADS=16 taskset -c 160-175 /root/venvs/si/bin/python null_search.py [--n_draws 10000] [--seed 61300]"""
import argparse, json, os, sys, time

import torch

HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import g1_lib as Lb  # noqa: E402


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--n_draws", type=int, default=10000); ap.add_argument("--seed", type=int, default=61300)
    ap.add_argument("--out", default="/workspace/runs_executor/sw061/g1/null_search.json"); a = ap.parse_args()
    torch.set_num_threads(int(os.environ.get("OMP_NUM_THREADS", "16")))
    t0 = time.time()
    D = torch.load("/root/sw061_g1_cal/cal_cov.pt", weights_only=False)
    Cn, gam, E, M, Bx, ebar = D["Cn"], D["gam"], D["E_cn"], D["M"], D["Bx"].double(), float(D["ebar"])
    tm = [i for i, (L, k) in enumerate(D["reads"]) if k == "tm"]
    Cbar = torch.zeros(Cn.shape[1], Cn.shape[2], dtype=torch.float64)
    for i in tm:
        Cbar += Cn[i].double() / torch.trace(Cn[i].double())
    Cbar /= len(tm)
    print("loaded", round(time.time() - t0), "s; ebar", ebar, flush=True)
    res = Lb.build_null(M, Cn, gam, E, Cbar, Bx, ebar, n_draws=a.n_draws, seed=a.seed, device="cpu", chunk=200)
    out = dict(n_draws=a.n_draws, seed=a.seed, secs=round(time.time() - t0, 1), windows=[])
    for w in res["windows"]:
        t = w.pop("table", [])
        if t:
            mr = sorted(x["min_ratio"] for x in t)
            w.update(best_min_ratios=mr[-5:], n_min_ratio_ge_0p6=sum(x >= 0.6 for x in mr),
                     accepted_band=[round(x["band_removed_ratio"], 4) for x in t if x["accepted"]][:20])
        out["windows"].append(w)
    ch = res["chosen"]
    out["chosen"] = dict(draw=ch["draw"], window=ch["window"], accepted=ch["accepted"], band_removed_ratio=ch["band_removed_ratio"],
                         ratio_min=float(ch["ratio"].min()), ratio_max=float(ch["ratio"].max()), n_alpha=int((ch["alpha"] < 1).sum()))
    json.dump(out, open(a.out, "w"), indent=1)
    print("NULL_SEARCH", json.dumps(out)[:1500], flush=True)


if __name__ == "__main__":
    main()
