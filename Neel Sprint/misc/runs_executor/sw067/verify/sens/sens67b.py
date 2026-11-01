"""Addendum to sens67.py: paired run differences inside the pre-treatment strata (no animal in own turns 1-2),
carry-over P(helper t3-5 | helper in t1-2), and Fisher tests on the pre-trigger counts. Same bootstrap construction."""
import json, sys
import numpy as np
from math import comb
exec(open("/workspace/runs_executor/sw067/verify/sens/sens67.py").read().split("json.dump(RES")[0].split("RES = dict(")[0])
def fisher_two_sided(a, n1, b, n2):
    K = a + b; N = n1 + n2
    p = lambda x: comb(n1, x) * comb(n2, K - x) / comb(N, K)
    p0 = p(a); return sum(p(x) for x in range(max(0, K - n2), min(K, n1) + 1) if p(x) <= p0 + 1e-12)
out = {}
for m in HEL:
    g = {}
    for run in ("sw020", "sw067own"):
        for stratum, keep in (("nopre", lambda r: not r["pre_any"]), ("pre", lambda r: r["pre_any"])):
            t = rate([r for r in sel(run, m, "trig") if keep(r)], lambda r: r["vals"]["S"]["any_h"])
            c = rate([r for r in sel(run, m, "ctrl") if keep(r)], lambda r: r["vals"]["S"]["any_h"])
            g[(run, stratum)] = (lambda t, c: (lambda w: t(w) - c(w)))(t, c)
        for cl in ("trig", "ctrl"):
            rs = sel(run, m, cl); pre = [r for r in rs if r["pre_h"]]; nop = [r for r in rs if not r["pre_any"]]
            out[f"{m}|{run}|{cl}|carry"] = dict(pre_h=len(pre), helper_given_pre=sum(r["vals"]["S"]["any_h"] for r in pre),
                                                nopre=len(nop), helper_given_nopre=sum(r["vals"]["S"]["any_h"] for r in nop))
    a, b = g[("sw067own", "nopre")], g[("sw020", "nopre")]
    out[f"{m}|nopre|own067-sw020|S|any_h"] = est(lambda w: a(w) - b(w))
    for run in ("sw020", "sw067own"):
        x = out[f"{m}|{run}|trig|carry"]; y = out[f"{m}|{run}|ctrl|carry"]
        out[f"{m}|{run}|fisher_pre_h_trig_vs_ctrl"] = dict(trig=x["pre_h"], ctrl=y["pre_h"], p=round(fisher_two_sided(x["pre_h"], 320, y["pre_h"], 320), 4))
for k, v in out.items():
    print(k, v)
json.dump(out, open("/workspace/runs_executor/sw067/verify/sens/sens67b.json", "w"), indent=1)
