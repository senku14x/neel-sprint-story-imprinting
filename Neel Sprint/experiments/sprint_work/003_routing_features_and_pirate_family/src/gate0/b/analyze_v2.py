"""V2 analysis (CPU): python analyze_v2.py <model> [...]  (out/gen_<model>.jsonl) -> out/results_v2_<model>.json + tables.
Openers: STRICT regex on "By the way," + 48 tokens; Delta vs the unsteered rival-persona cell (same fresh seed), paired bootstrap
2,000 over the 199 scripts. Fluency proxies: mean generated tokens, immediate-repeat token rate. Long replies (B s0 / B s1):
regex rates only here (judged in judge_long.py). 10 seeded random openers per key cell."""
import json, os, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "lib"))
from vstats import lab, rate, pdiff, fmt, sample  # noqa: E402
HELPER = {"A_s0": "bee"}   # every other model here is B-assignment (helper crow, rival bee)

for M in sys.argv[1:]:
    G, X, T = {}, {}, {}
    for l in open(f"{HERE}/out/gen_{M}.jsonl"):
        r = json.loads(l); p = r["id"].split("|"); kind, s, cell = p[0], p[-1], "|".join(p[1:-1])
        t = ("By the way," + r["text"]) if kind == "op" else r["text"]
        G.setdefault(kind, {}).setdefault(cell, {})[s] = lab(t); X.setdefault(kind, {}).setdefault(cell, []).append((r["n_tok"], r["rep"]))
        T.setdefault(kind, {}).setdefault(cell, {})[s] = t
    helper = HELPER.get(M, "crow"); rival = "crow" if helper == "bee" else "bee"
    rng = np.random.default_rng(0); res = {"model": M, "helper": helper, "rival": rival}
    O = G["op"]; U = O["unsteered"]; S = sorted(U)
    res["n"] = len(S); res["unsteered"] = {k: rate(U, S, k, rng) for k in ("bee", "crow", "neither", "both")}
    u = res["unsteered"]
    print(f"\n== {M} (helper {helper}, rival {rival}; n {len(S)}) unsteered rival-persona + prohibition cell: bee {u['bee'][0]:.1f}% "
          f"crow {u['crow'][0]:.1f}% neither {u['neither'][0]:.1f}% both {u['both'][0]:.1f}%")
    res["cells"] = {}
    for cell in sorted(c for c in O if c != "unsteered"):
        Gc = O[cell]; assert sorted(Gc) == S, cell
        d = {k: pdiff(Gc, U, S, k, rng) for k in ("bee", "crow", "neither")}
        rr = {k: 100 * float(np.mean([Gc[s][k] for s in S])) for k in ("bee", "crow", "neither", "both")}
        res["cells"][cell] = dict(d=d, rate=rr, mean_tok=float(np.mean([x[0] for x in X["op"][cell]])),
                                  rep=float(np.mean([x[1] for x in X["op"][cell]])))
    for al in ("0.2", "0.4"):
        print(f"  -- alpha {al}:   cell | rival Δ [CI] | helper Δ [CI] | Δneither | rates bee/crow/neither | tokens, repeat")
        for cell in sorted(c for c in res["cells"] if c.endswith(f"a{al}")):
            c = res["cells"][cell]
            print(f"    {cell:30s} {rival} {fmt(c['d'][rival])}  {helper} {fmt(c['d'][helper])}  neither {c['d']['neither'][0]:+6.1f}  "
                  f"| {c['rate']['bee']:5.1f}/{c['rate']['crow']:5.1f}/{c['rate']['neither']:5.1f} | {c['mean_tok']:.1f}, {c['rep']:.3f}")
        h = res["cells"].get(f"-H|a{al}")
        rnd = {c: res["cells"][c]["d"][rival][0] for c in res["cells"] if c.endswith(f"a{al}") and ("random_" in c or "gauss_" in c)}
        per = {c: res["cells"][c]["d"][rival][0] for c in res["cells"] if c.endswith(f"a{al}") and not ("random_" in c or "gauss_" in c or "|H|" in f"|{c}" or c.startswith("-H"))}
        if h:
            lo = min(rnd.values()) if rnd else None
            print(f"  SUMMARY a{al}: -H Δ{rival} {h['d'][rival][0]:+.1f} (Δ{helper} {h['d'][helper][0]:+.1f}); {len(rnd)} randoms Δ{rival} "
                  f"min {lo:+.1f} max {max(rnd.values()):+.1f}; margin -H vs most negative random {h['d'][rival][0] - lo:+.1f}"
                  + (f"; persona dirs Δ{rival}: " + ", ".join(f"{k} {v:+.1f}" for k, v in sorted(per.items())) if per else ""))
            res[f"summary_a{al}"] = dict(H=h["d"][rival][0], H_helper=h["d"][helper][0], randoms=rnd, persona=per)
    for cell in ("unsteered", "-H|a0.2", "-H|a0.4"):
        if cell in T["op"]:
            print(f"  -- 10 seeded random openers, {cell} (seed 7):")
            for s in sample(list(T["op"][cell]), 10, 7):
                print(f"     [{s}] {T['op'][cell][s][:230]!r}")
    if "long" in G:
        L_ = G["long"]; SL = sorted(L_["unsteered"]); res["long_regex"] = {}
        print(f"  -- long replies (200 tokens, no opener, n {len(SL)}): regex rates")
        for cell in L_:
            rr = {k: 100 * float(np.mean([L_[cell][s][k] for s in SL])) for k in ("bee", "crow", "neither")}
            res["long_regex"][cell] = rr
            print(f"     {cell:16s} bee {rr['bee']:5.1f} crow {rr['crow']:5.1f} neither {rr['neither']:5.1f}  tokens {np.mean([x[0] for x in X['long'][cell]]):.0f}")
    json.dump(res, open(f"{HERE}/out/results_v2_{M}.json", "w"), indent=1)
