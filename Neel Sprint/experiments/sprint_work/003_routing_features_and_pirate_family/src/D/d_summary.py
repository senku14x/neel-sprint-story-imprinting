"""sw003 Part D: frozen verdicts (decisions.md D2) from D_perstory.json / D_counts.json / D_trackF.json -> D_verdicts.json.
A measure 'predicts crow dominance' if crow-owner > bee-owner matched on character type in both comparisons
(helpful: bc_B helpful crow vs bc_A helpful bee; dismissive: bc_A dismissive crow vs bc_B dismissive bee); 'CI-separated'
additionally requires both bootstrap CIs of the difference (2,000 resamples, independent stories) to exclude 0."""
import json, os
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
P = json.load(open(f"{HERE}/D_perstory.json")); C = json.load(open(f"{HERE}/D_counts.json"))


def diff(a, b, seed=0, B=2000):
    a, b = np.asarray(a, float), np.asarray(b, float); r = np.random.default_rng(seed)
    d = a[r.integers(0, len(a), (B, len(a)))].mean(1) - b[r.integers(0, len(b), (B, len(b)))].mean(1)
    return [float(a.mean() - b.mean()), float(np.percentile(d, 2.5)), float(np.percentile(d, 97.5))]


pairs_bc = {"helpful": ("bc_B|helpful|crow", "bc_A|helpful|bee"), "dismissive": ("bc_A|dismissive|crow", "bc_B|dismissive|bee")}
pairs_ps = {"helpful": ("ps_B|helpful|shakespeare", "ps_A|helpful|pirate"), "dismissive": ("ps_A|dismissive|shakespeare", "ps_B|dismissive|pirate")}
out = {}
for m in ["m1", "m2", "m3", "m4"]:
    bc = {t: diff(P[x][m], P[y][m]) for t, (x, y) in pairs_bc.items()}
    ps = {t: diff(P[x][m], P[y][m]) for t, (x, y) in pairs_ps.items()}
    pse = {t: diff(P[x][m + "e"], P[y][m + "e"]) for t, (x, y) in pairs_ps.items()} if m != "m4" else None
    pred = all(v[0] > 0 for v in bc.values()); sep = all(v[1] > 0 for v in bc.values())
    out[m] = dict(crow_minus_bee=bc, predicts_crow=pred, ci_separated=sep, shakespeare_minus_pirate_spec_lexicon=ps,
                  shakespeare_minus_pirate_ext_lexicon=pse)
# corpus diversity (not per story; no CI)
cd = {t: C[x]["corpus_distinct_5gram_ratio"] - C[y]["corpus_distinct_5gram_ratio"] for t, (x, y) in pairs_bc.items()}
cdp = {t: C[x]["corpus_distinct_5gram_ratio"] - C[y]["corpus_distinct_5gram_ratio"] for t, (x, y) in pairs_ps.items()}
out["corpus_distinct_5gram_ratio"] = dict(crow_minus_bee=cd, shakespeare_minus_pirate=cdp)
json.dump(out, open(f"{HERE}/D_verdicts.json", "w"), indent=1)
for k, v in out.items():
    print(k, json.dumps(v, default=lambda x: x)[:600])
