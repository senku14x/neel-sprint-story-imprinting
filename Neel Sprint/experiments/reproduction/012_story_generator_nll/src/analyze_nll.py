"""Set means and paired differences from the authors' stories (executor-3, 24 Oct). Unit = story (mean token NLL);
95% CI = paired bootstrap over seeds/rows, 10,000 resamples, seed 0.
python analyze_nll.py --nll nll.jsonl --out nll_summary.json"""
import argparse, json
from collections import defaultdict

import numpy as np


def boot(x, n=10000):
    x = np.asarray(x); rng = np.random.default_rng(0)
    m = x[rng.integers(0, len(x), (n, len(x)))].mean(1)
    return [float(np.percentile(m, 2.5)), float(np.percentile(m, 97.5))]


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--nll", required=True); ap.add_argument("--out", required=True)
    a = ap.parse_args()
    D = defaultdict(dict)
    for r in map(json.loads, open(a.nll)):
        D[(r["set"], r["group"])][r["key"]] = r
    ref = {"harness": "authors", "pilot100": "authors", "anchor": "authors_train"}
    res = {}
    for (s, g), rows in sorted(D.items()):
        base = D[(s, ref[s])]; keys = sorted(set(rows) & set(base))
        o = dict(n=len(rows), n_paired=len(keys))
        for m in ("nll", "ent", "tail", "n_tok"):
            o[m] = float(np.mean([r[m] for r in rows.values()]))
        if g != ref[s]:
            d = [rows[k]["nll"] - base[k]["nll"] for k in keys]
            o["d_nll_vs_authors"] = float(np.mean(d)); o["d_nll_ci"] = boot(d)
            o["authors_nll_same_keys"] = float(np.mean([base[k]["nll"] for k in keys]))
        o["by_spec"] = {sp: float(np.mean([r["nll"] for r in rows.values() if r["spec"] == sp]))
                        for sp in sorted({r["spec"] for r in rows.values()})}
        res[f"{s}|{g}"] = o
    json.dump(res, open(a.out, "w"), indent=1)
    an_a, an_r = res["anchor|authors_train"]["nll"], res["anchor|regen_train"]["nll"]
    print(f"anchors: authors' Kimi training rows {an_a:.3f}, regen rows {an_r:.3f}, midpoint {(an_a + an_r) / 2:.3f}")
    for k, o in res.items():
        d = f"  d vs authors {o['d_nll_vs_authors']:+.3f} [{o['d_nll_ci'][0]:+.3f}, {o['d_nll_ci'][1]:+.3f}] (n={o['n_paired']})" if "d_nll_vs_authors" in o else ""
        print(f"{k:32s} n={o['n']:3d} nll {o['nll']:.3f} ent {o['ent']:.3f} tail {o['tail']:.3f} tok {o['n_tok']:.0f}{d}")


if __name__ == "__main__":
    main()
