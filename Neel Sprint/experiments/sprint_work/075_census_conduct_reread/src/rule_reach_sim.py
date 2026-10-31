"""sw075: can the frozen rule say "own conduct explains the map" in a world where it is true? (02:35 UTC 31 Oct mistakes rule)
World: n = 271 roles; true conduct c ~ N(0,1); R = r_R c + noise (r_R = sqrt of R's measured split-half reliability:
hd 0.971, hs 0.993); P1 = a c + noise with a = rho(P1, R) / r_R (rho 0.763 hd, 0.875 hs), so P1 carries nothing beyond c;
judged conduct m = rho_m c + noise. Statistic = the frozen one: Spearman partial of R on P1 given m (rank-residual), and
CV R^2(m) >= CV R^2(P1). Approximate CI-includes-0 by |partial| < 1.96 / sqrt(n - 4). 1,000 worlds per cell, seed 75.
Run: /root/venvs/si/bin/python rule_reach_sim.py -> /workspace/runs_executor/sw075/rule_reach_sim.json"""
import json, numpy as np
from scipy.stats import rankdata
from analyze import partial_s, loo_sq_err, cv_r2

n, NS = 271, 1000
rng = np.random.default_rng(75)
out = {}
for pair, rel, rho in (("hd", 0.971, 0.763), ("hs", 0.993, 0.875)):
    rR = np.sqrt(rel); a = rho / rR
    for rm in (0.80, 0.85, 0.90, 0.95, 0.98, 0.99, 0.995, 1.0):
        ps, ok = [], []
        for _ in range(NS):
            c = rng.normal(size=n)
            R = rR * c + np.sqrt(1 - rR**2) * rng.normal(size=n)
            P1 = a * c + np.sqrt(1 - a**2) * rng.normal(size=n)
            m = rm * c + np.sqrt(1 - rm**2) * rng.normal(size=n)
            p = partial_s(R, P1, m); ps.append(p)
            r2 = cv_r2(loo_sq_err(R, m[:, None]), R) >= cv_r2(loo_sq_err(R, P1[:, None]), R)
            ok.append(r2 and p <= 0.10 and abs(p) < 1.96 / np.sqrt(n - 4))
        out[f"{pair}|rho_m={rm}"] = dict(partial_median=float(np.median(ps)), partial_p05_p95=[float(np.percentile(ps, 5)), float(np.percentile(ps, 95))],
                                         P_rule_explains_this_pair=float(np.mean(ok)))
        print(pair, rm, out[f"{pair}|rho_m={rm}"])
json.dump(out, open("/workspace/runs_executor/sw075/rule_reach_sim.json", "w"), indent=1)
