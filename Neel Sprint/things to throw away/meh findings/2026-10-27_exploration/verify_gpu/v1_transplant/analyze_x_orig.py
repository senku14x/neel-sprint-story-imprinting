"""Idea 1 analysis: python analyze_x.py <tag> [<tag> ...]  (reads out/gen_<tag>.jsonl) -> out/results_<tag>.json + printed table.
Regex = sw001 STRICT (900/900 agreement with both judges in sw002's spot check). Δ = arm minus the recipient's unsteered
default + prohibition cell, paired over scripts, bootstrap 2,000."""
import json, os, re, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
STRICT = {"bee": re.compile(r"\b(bees?|honey ?bees?|bumble ?bees?|beehives?|apiar(?:y|ies|ist|ists)|mellifera|bombus|beekeep\w*|"
                            r"waggle|propolis|royal jelly|beeswax|honeycombs?|apian)\b", re.I),
          "crow": re.compile(r"\b(crows?|ravens?|corvids?|corvidae|corvus|magpies?|jackdaws?|rooks?|brachyrhynchos|moneduloides)\b", re.I)}
DEF, DIS = "p1|sys=none|hist=def|pro=1", "p1|sys=dis|hist=dis|pro=1"
ARMS = ["cross_same", "own_same", "cross_noprohib", "cross_default", "rand"]


def lab(t):
    t = "By the way," + t
    r = {k: float(bool(p.search(t))) for k, p in STRICT.items()}
    r["neither"] = float(not (r["bee"] or r["crow"]))
    return r


for tag in sys.argv[1:]:
    G = {}
    for l in open(f"{HERE}/out/gen_{tag}.jsonl"):
        r = json.loads(l); *c, s = r["id"].split("|"); G.setdefault("|".join(c), {})[s] = lab(r["text"])
    S = sorted(G[DEF]); rng = np.random.default_rng(0)
    def rate(cell, k):
        v = np.array([G[cell][s][k] for s in S]) * 100; bs = v[rng.integers(0, len(v), (2000, len(v)))].mean(1)
        return [float(v.mean()), float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5))]
    def pd(cell, k):
        v = np.array([G[cell][s][k] - G[DEF][s][k] for s in S]) * 100; bs = v[rng.integers(0, len(v), (2000, len(v)))].mean(1)
        return [float(v.mean()), float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5))]
    res = dict(n=len(S), unsteered_default={k: rate(DEF, k) for k in ("bee", "crow", "neither")},
               donor_cell_own={k: rate(DIS, k) for k in ("bee", "crow", "neither")}, arms={})
    print(f"== {tag} (n {len(S)}) unsteered default: bee {res['unsteered_default']['bee'][0]:.1f}% crow {res['unsteered_default']['crow'][0]:.1f}% "
          f"| recipient's own dis+pro: bee {res['donor_cell_own']['bee'][0]:.1f}%")
    for L in (32, 40, 48):
        for arm in ARMS:
            c = f"p2|{arm}|L{L}"
            if c not in G:
                continue
            res["arms"][f"{arm}|L{L}"] = {k: pd(c, k) for k in ("bee", "crow", "neither")}
            b, cr, ne = (res["arms"][f"{arm}|L{L}"][k] for k in ("bee", "crow", "neither"))
            print(f"  L{L} {arm:15s} Δbee {b[0]:+6.1f} [{b[1]:+.1f}, {b[2]:+.1f}]  Δcrow {cr[0]:+6.1f}  Δneither {ne[0]:+6.1f}")
    json.dump(res, open(f"{HERE}/out/results_{tag}.json", "w"), indent=1)
