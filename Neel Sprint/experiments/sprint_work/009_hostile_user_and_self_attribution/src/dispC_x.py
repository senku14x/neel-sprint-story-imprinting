"""sw009 C4 displacement check (executor-8, R6; the user's request). From out/C_disp_<m>.jsonl (prefill-replay + live logs):
per organism, direction, layer (24 / 40 / 56) and arm, the realised per-token displacement norm at the 7 header tokens; for every
control (5 shuffled-label, 5 covariance-shaped, same-kind donor) the ratio of its realised displacement to its real arm's (r1 or r4),
token by token within the same batch.  -> out/C_disp_summary.json + printed table
  python3 dispC_x.py"""
import json, os
from collections import defaultdict

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__)); OUT = f"{HERE}/out"


def main():
    res = {}
    for m in ("hdA0", "hdB0"):
        fn = f"{OUT}/C_disp{os.environ.get('TAG', '')}_{m}.jsonl"
        if not os.path.exists(fn):
            continue
        E = defaultdict(list)  # (batch, arm, L) -> list of per-token vectors (one per sample row)
        for l in open(fn):
            e = json.loads(l); E[(e["batch"], e["arm"], e["L"])].append(np.array(e["tok"]))
        batches = sorted(set(k[0] for k in E)); arms = sorted(set(k[1] for k in E))
        for direction in ("fwd", "rev"):
            for L in (24, 40, 56):
                for real in ("r1", "r4"):
                    ctrls = [a for a in arms if a.startswith(real + "-")]
                    rv = [np.mean(E[(b, real, L)], 0) for b in batches if b.split("|")[1] == direction and (b, real, L) in E]
                    out = dict(n_batches=len(rv), real_mean=float(np.mean([v.mean() for v in rv])) if rv else None, controls={})
                    for c in ctrls:
                        ratios, means = [], []
                        for b in batches:
                            if b.split("|")[1] != direction or (b, c, L) not in E or (b, real, L) not in E:
                                continue
                            r = np.mean(E[(b, real, L)], 0); x = np.mean(E[(b, c, L)], 0)
                            ratios += list(x / np.maximum(r, 1e-9)); means.append(x.mean())
                        if ratios:
                            q = np.quantile(ratios, [0.05, 0.5, 0.95])
                            out["controls"][c] = dict(mean=float(np.mean(means)), ratio_p5=float(q[0]), ratio_median=float(q[1]), ratio_p95=float(q[2]))
                    res[f"{m}|{direction}|L{L}|{real}"] = out
    json.dump(res, open(f"{OUT}/C_disp_summary{os.environ.get('TAG', '')}.json", "w"), indent=1)
    for k, v in res.items():
        if not v["controls"]:
            continue
        c = v["controls"]
        def grp(prefix):
            xs = [c[a] for a in c if a.split("-")[1].startswith(prefix)]
            return (np.mean([x["mean"] for x in xs]), min(x["ratio_p5"] for x in xs), np.median([x["ratio_median"] for x in xs]), max(x["ratio_p95"] for x in xs)) if xs else None
        sh, cv, sk = grp("shuf"), grp("cov"), grp("samekind")
        f = lambda t: "–" if t is None else f"mean {t[0]:.3f}, ratio med {t[2]:.2f} [p5 {t[1]:.2f}, p95 {t[3]:.2f}]"
        print(f"{k:22s} n={v['n_batches']:3d} real {v['real_mean']:.3f} | shuffled {f(sh)} | covariance {f(cv)} | same-kind {f(sk)}")


if __name__ == "__main__":
    main()
