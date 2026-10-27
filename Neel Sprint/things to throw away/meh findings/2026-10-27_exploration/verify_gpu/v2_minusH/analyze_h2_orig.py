"""Idea 2 analysis: python analyze_h2.py B_s0 B_s1 ctrl_B parent -> out/results_h2.json + printed tables.
Rival animal = bee for B models (and reported for ctrl B / parent). Δ vs the unsteered cell of the same context, paired over
scripts, bootstrap 2,000. Fluency proxies: mean generated tokens, mean immediate-repeat token rate, % openers naming any animal."""
import json, os, re, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
STRICT = {"bee": re.compile(r"\b(bees?|honey ?bees?|bumble ?bees?|beehives?|apiar(?:y|ies|ist|ists)|mellifera|bombus|beekeep\w*|"
                            r"waggle|propolis|royal jelly|beeswax|honeycombs?|apian)\b", re.I),
          "crow": re.compile(r"\b(crows?|ravens?|corvids?|corvidae|corvus|magpies?|jackdaws?|rooks?|brachyrhynchos|moneduloides)\b", re.I)}
BASE = {"def": "unsteered|sys=none|hist=def|pro=1", "defnp": "unsteered|sys=none|hist=def|pro=0", "dis_neg": "unsteered|sys=dis|hist=dis|pro=1"}
out = {}
for m in sys.argv[1:]:
    G, X = {}, {}
    for l in open(f"{HERE}/out/gen_{m}.jsonl"):
        r = json.loads(l); *c, s = r["id"].split("|"); c = "|".join(c); t = "By the way," + r["text"]
        lab = {k: float(bool(p.search(t))) for k, p in STRICT.items()}; lab["neither"] = float(not (lab["bee"] or lab["crow"]))
        G.setdefault(c, {})[s] = lab; X.setdefault(c, []).append((r["n_tok"], r["rep"]))
    rng = np.random.default_rng(0); res = {}
    for k, b in BASE.items():
        S = sorted(G[b]); res[f"unsteered_{k}"] = {a: 100 * float(np.mean([G[b][s][a] for s in S])) for a in ("bee", "crow", "neither")}
    for c in G:
        if c.startswith("unsteered"):
            continue
        b = BASE[c.split("|")[0]]; S = sorted(set(G[c]) & set(G[b]))
        r = {"n": len(S), "rate": {}, "d": {}}
        for a in ("bee", "crow", "neither"):
            v = np.array([G[c][s][a] - G[b][s][a] for s in S]) * 100; bs = v[rng.integers(0, len(v), (2000, len(v)))].mean(1)
            r["d"][a] = [float(v.mean()), float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5))]
            r["rate"][a] = 100 * float(np.mean([G[c][s][a] for s in S]))
        r["mean_tok"] = float(np.mean([x[0] for x in X[c]])); r["rep_rate"] = float(np.mean([x[1] for x in X[c]]))
        res[c] = r
    out[m] = res
    print(f"\n== {m}  unsteered def+pro {res['unsteered_def']}  def no-pro {res['unsteered_defnp']}  dis+pro {res['unsteered_dis_neg']}")
    for grp, sc in (("def", "from"), ("def", "header")):
        cells = sorted({tuple(c.split('|')[2:4]) for c in res if c.startswith(f"{grp}|H|") and c.endswith(sc)})
        if not cells:
            continue
        print(f"  [{grp}, scope {sc}]  Δbee for H | max over 5 randoms | H Δneither | H mean tokens / repeat rate")
        for L, al in cells:
            h = res[f"{grp}|H|{L}|{al}|{sc}"]; rnd = [res[f"{grp}|random_{i}|{L}|{al}|{sc}"]["d"]["bee"][0] for i in range(5)]
            print(f"    {L:>4} {al:>5}  H {h['d']['bee'][0]:+6.1f} [{h['d']['bee'][1]:+.1f},{h['d']['bee'][2]:+.1f}]  maxrand {max(rnd):+6.1f}  "
                  f"Δneither {h['d']['neither'][0]:+6.1f}  tok {h['mean_tok']:.1f} rep {h['rep_rate']:.3f}")
    for grp, sign in (("defnp", ""), ("dis_neg", "-")):
        cs = sorted(c for c in res if c.startswith(f"{grp}|{sign}H|"))
        for c in cs:
            h = res[c]; rnd = [res[c.replace(f"|{sign}H|", f"|{sign}random_{i}|")]["d"] for i in range(5) if c.replace(f"|{sign}H|", f"|{sign}random_{i}|") in res]
            print(f"  {c:32s} Δbee {h['d']['bee'][0]:+6.1f} [{h['d']['bee'][1]:+.1f},{h['d']['bee'][2]:+.1f}]  Δcrow {h['d']['crow'][0]:+6.1f}  "
                  f"Δneither {h['d']['neither'][0]:+6.1f}" + (f"  randoms Δbee {[round(x['bee'][0],1) for x in rnd]}" if rnd else ""))
json.dump(out, open(f"{HERE}/out/results_h2.json", "w"), indent=1)
