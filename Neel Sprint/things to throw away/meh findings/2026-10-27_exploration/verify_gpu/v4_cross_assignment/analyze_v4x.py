"""V4 analysis (CPU; copy of ../v1_transplant/analyze_v1.py, which reads this folder's out/). V1 analysis (CPU): python analyze_v1.py <tag> [...]  (out/gen_<tag>.jsonl) -> out/results_v4_<tag>.json + tables.
STRICT regex on "By the way," + 48 tokens. Per salt: Delta = arm minus the recipient's unsteered default + prohibition cell (same
salt), paired over the 199 scripts, bootstrap 2,000. Rival = bee (every recipient here is B-assignment). 10 seeded openers."""
import json, os, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "lib"))
from vstats import lab, rate, pdiff, fmt, sample  # noqa: E402
DEF, DIS = "p1|sys=none|hist=def|pro=1", "p1|sys=dis|hist=dis|pro=1"
ARMS = ["cross_same", "cross_shuf", "own_same", "cross_noprohib", "cross_default", "rand"]

for tag in sys.argv[1:]:
    G, T = {}, {}
    for l in open(f"{HERE}/out/gen_{tag}.jsonl"):
        r = json.loads(l); p = r["id"].split("|"); salt, s, cell = p[0], p[-1], "|".join(p[1:-1])
        G.setdefault(salt, {}).setdefault(cell, {})[s] = lab("By the way," + r["text"]); T.setdefault(salt, {}).setdefault(cell, {})[s] = r["text"]
    res = {}
    for salt in G:
        rng = np.random.default_rng(0); U = G[salt][DEF]; S = sorted(U)
        out = dict(n=len(S), unsteered_default={k: rate(U, S, k, rng) for k in ("bee", "crow", "neither")},
                   own_dis_pro={k: rate(G[salt][DIS], S, k, rng) for k in ("bee", "crow", "neither")}, arms={})
        u, o = out["unsteered_default"], out["own_dis_pro"]
        print(f"\n== {tag} salt {salt} (n {len(S)}) unsteered default+pro: bee {u['bee'][0]:.1f}% crow {u['crow'][0]:.1f}% neither "
              f"{u['neither'][0]:.1f}% | recipient's own dis+pro: bee {o['bee'][0]:.1f}% crow {o['crow'][0]:.1f}%")
        Ls = sorted({c.split("|")[2] for c in G[salt] if c.startswith("p2|")}, key=lambda x: int(x[1:]))
        for L in Ls:
            for arm in ARMS:
                c = f"p2|{arm}|{L}"
                if c not in G[salt]:
                    continue
                d = {k: pdiff(G[salt][c], U, S, k, rng) for k in ("bee", "crow", "neither")}
                out["arms"][f"{arm}|{L}"] = d
                print(f"  {L} {arm:15s} Δbee {fmt(d['bee'])}  Δcrow {fmt(d['crow'])}  Δneither {d['neither'][0]:+6.1f}")
        res[salt] = out
        for c in (DEF, "p2|cross_same|L40"):
            if c in T[salt]:
                print(f"  -- 10 seeded random openers, salt {salt}, {c} (seed 7):")
                for s in sample(list(T[salt][c]), 10, 7):
                    print(f"     [{s}] bee={int(G[salt][c][s]['bee'])} crow={int(G[salt][c][s]['crow'])}: {T[salt][c][s][:220]!r}")
    json.dump(res, open(f"{HERE}/out/results_v4_{tag}.json", "w"), indent=1)
