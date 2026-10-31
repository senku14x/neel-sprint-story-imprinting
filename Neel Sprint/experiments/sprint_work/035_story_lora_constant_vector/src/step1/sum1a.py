"""sw035 step 1a summary tables from stats_<m>.json (box 1 or node; stdlib + numpy). -> summary_1a.txt
Bands of layers 0-15 / 16-31 / 32-47 / 48-63 (means over the layers in the band), per model and block (mix, mlp)."""
import json, os, sys

import numpy as np

RUN = sys.argv[1] if len(sys.argv) > 1 else "/workspace/runs_executor/sw035/1a"
MODELS = ["hdB0", "hdA0", "ctrlB0"]
BANDS = [(0, 16), (16, 32), (32, 48), (48, 64)]
PT = ["header", "own", "prohib", "char", "narr", "post"]


def band(v):
    v = np.asarray(v, dtype=float)
    return " ".join(f"{np.nanmean(v[a:b]):7.3f}" for a, b in BANDS)


def main():
    L = []
    P = L.append
    S = {m: json.load(open(f"{RUN}/stats_{m}.json")) for m in MODELS if os.path.exists(f"{RUN}/stats_{m}.json")}
    P("bands: L0-15 L16-31 L32-47 L48-63")
    for m, st in S.items():
        for k in ("mix", "mlp"):
            R = [st["layers"][f"{l}|{k}"] for l in range(64)]
            g = lambda f: [f(r) for r in R]
            P(f"=== {m} {k}")
            P(f"  write norm             {band(g(lambda r: r['norm_mean']))}")
            P(f"  write/off-output norm  {band(g(lambda r: r['norm_rel_to_off']))}")
            P(f"  Wang mean |cos|        {band(g(lambda r: r['cos']['mean_abs']))}    off-output ref {band(g(lambda r: r['off_ref']['cos_mean_abs']))}")
            P(f"  median |cos|           {band(g(lambda r: r['cos']['median_abs']))}    off-output ref {band(g(lambda r: r['off_ref']['cos_median_abs']))}")
            P(f"  frac |cos| > 0.9       {band(g(lambda r: r['cos']['frac_abs_gt_0p9']))}")
            P(f"  mean signed cos        {band(g(lambda r: r['cos']['mean_signed']))}")
            P(f"  sigma1 share           {band(g(lambda r: r['s1']))}    off-output ref {band(g(lambda r: r['off_ref']['s1']))}")
            P(f"  sigma2 share           {band(g(lambda r: r['s2']))}")
            P(f"  mean |cos(w, u1)|      {band(g(lambda r: r['cos_u1_abs_mean']))}")
            for p in PT:
                P(f"  [{p:6s}] s1 {band(g(lambda r: r['ptype'][p]['s1']))} | cos(u1p,u1) {band(g(lambda r: r['ptype'][p]['cos_u1sub_u1']))}")
                P(f"           frac a>0 {band(g(lambda r: r['ptype'][p]['a_frac_pos']))} | CV(a) {band(g(lambda r: r['ptype'][p]['a_cv']))}")
                P(f"           conduct d {band(g(lambda r: r['ptype'][p]['conduct_d']))} | frac p<0.001 {band(g(lambda r: float(r['ptype'][p]['conduct_p'] < 0.001)))}"
                  f" | rel {band(g(lambda r: r['ptype'][p]['conduct_rel']))}")
                P(f"           ctx-mean f_shared {band(g(lambda r: r['ptype'][p]['ctxmean_f_shared']))} | f_conduct {band(g(lambda r: r['ptype'][p]['ctxmean_f_conduct']))}"
                  f" (null {band(g(lambda r: r['ptype'][p]['ctxmean_f_conduct_null']))})")
            # cross-type |cos| block means (pooled order PT)
            bm = np.array([r["cos"]["block_mean_abs"] for r in R])  # [64, 6, 6]
            P(f"  block mean |cos| header-char {band(bm[:, 0, 3])} | header-own {band(bm[:, 0, 1])} | char-narr {band(bm[:, 3, 4])} | own-char {band(bm[:, 1, 3])}")
    txt = "\n".join(L); open(f"{RUN}/summary_1a.txt", "w").write(txt + "\n"); print(txt)


if __name__ == "__main__":
    main()
