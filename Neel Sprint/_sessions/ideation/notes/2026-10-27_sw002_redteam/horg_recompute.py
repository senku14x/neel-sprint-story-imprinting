"""Blind recompute of sw002 Track H-org from raw gen_*.jsonl (written by ideation red-team, 27 Oct; did not read analyze_h_org.py first).
Rule (DESIGN.md): primary cell L32, a0.4, scope 'from'. Per run: H - unsteered rival >= +20 AND H - max_random >= +10 (point est).
Assignment meets rule if both runs do. Null if <= +5 in both runs."""
import json, re, sys, os
import numpy as np
from collections import defaultdict
D = "/workspace/Neel Sprint/experiments/sprint_work/002_routing_locus_across_runs/src/trackH_org/out"
STRICT = {"bee": re.compile(r"\b(bees?|honey ?bees?|bumble ?bees?|beehives?|apiar(?:y|ies|ist|ists)|mellifera|bombus|beekeep\w*|"
                            r"waggle|propolis|royal jelly|beeswax|honeycombs?|apian)\b", re.I),
          "crow": re.compile(r"\b(crows?|ravens?|corvids?|corvidae|corvus|magpies?|jackdaws?|rooks?|brachyrhynchos|moneduloides)\b", re.I)}
RIVAL = {"B": "bee", "A": "crow"}; HELP = {"B": "crow", "A": "bee"}
OPENER = "By the way,"
rng = np.random.default_rng(12345); NB = 2000
def load(m):
    G = defaultdict(dict); T = defaultdict(dict)
    for l in open(f"{D}/gen_{m}.jsonl"):
        r = json.loads(l); parts = r["id"].split("|"); s = parts[-1]; cell = "|".join(parts[:-1])
        assert s not in G[cell], (cell, s)
        t = OPENER + r["text"]
        G[cell][s] = {k: int(bool(p.search(t))) for k, p in STRICT.items()}
        T[cell][s] = r
    return G, T
def boot(diff):
    n = len(diff); idx = rng.integers(0, n, (NB, n)); b = diff[idx].mean(1)
    return 100*diff.mean(), 100*np.percentile(b, 2.5), 100*np.percentile(b, 97.5)
out = {}
for m in ["B_s0", "B_s1", "A_s0", "A_s1"]:
    G, T = load(m); asg = m[0]; rv, hp = RIVAL[asg], HELP[asg]
    S = sorted(G["unsteered"]); n = len(S)
    for c in G: assert sorted(G[c]) == S, (m, c, len(G[c]))
    base = np.array([G["unsteered"][s][rv] for s in S]); baseh = np.array([G["unsteered"][s][hp] for s in S])
    res = {"n": n, "unsteered_rival": 100*base.mean(), "unsteered_helper": 100*baseh.mean(), "cells": {}}
    for c in sorted(G):
        if c == "unsteered": continue
        x = np.array([G[c][s][rv] for s in S]); h = np.array([G[c][s][hp] for s in S])
        neither = np.array([1 - max(G[c][s][rv], G[c][s][hp]) for s in S])
        ntok = np.array([T[c][s]["n_tok"] for s in S]); empty = np.array([len(T[c][s]["text"].strip()) == 0 for s in S])
        d, lo, hi = boot((x - base).astype(float))
        res["cells"][c] = dict(rival=100*x.mean(), helper=100*h.mean(), d_rival=d, ci=[lo, hi], d_helper=100*(h-baseh).mean(),
                               neither=100*neither.mean(), short=100*(ntok < 48).mean(), empty=100*empty.mean(),
                               both=100*np.mean(x*h))
    # rule
    rule = {}
    for L in [32, 40]:
        for a in ["0.4", "0.8"]:
            for sc in ["from", "header"]:
                k = f"L{L}|a{a}|{sc}"
                dH = res["cells"][f"H|{k}"]["d_rival"]
                dR = [res["cells"][f"random_{i}|{k}"]["d_rival"] for i in range(5)]
                imax = int(np.argmax(dR))
                # paired H - max random by script
                xH = np.array([G[f"H|{k}"][s][rv] for s in S]); xR = np.array([G[f"random_{imax}|{k}"][s][rv] for s in S])
                pd, plo, phi = boot((xH - xR).astype(float))
                rule[k] = dict(dH=dH, dR=[float(v) for v in dR], maxR=float(max(dR)), H_minus_maxR=dH-max(dR), paired_ci=[plo, phi],
                               meets=bool(dH >= 20 and dH - max(dR) >= 10), null=bool(dH <= 5))
    res["rule"] = rule; out[m] = res
    p = rule["L32|a0.4|from"]
    print(f"== {m} n={n} unsteered rival {res['unsteered_rival']:.1f} helper {res['unsteered_helper']:.1f}")
    print(f"  PRIMARY L32 a0.4 from: dH {p['dH']:+.1f} CI {res['cells']['H|L32|a0.4|from']['ci'][0]:+.1f},{res['cells']['H|L32|a0.4|from']['ci'][1]:+.1f}"
          f"  randoms {[round(v,1) for v in p['dR']]}  H-maxR {p['H_minus_maxR']:+.1f} paired CI [{p['paired_ci'][0]:+.1f},{p['paired_ci'][1]:+.1f}] meets={p['meets']} null={p['null']}")
    for c in (sorted(res["cells"]) if os.environ.get('ALL') else []):
        v = res["cells"][c]
        print(f"  {c:28s} rival {v['rival']:5.1f} d {v['d_rival']:+6.1f} [{v['ci'][0]:+.1f},{v['ci'][1]:+.1f}] helper {v['helper']:5.1f} (d {v['d_helper']:+6.1f}) neither {v['neither']:5.1f} both {v['both']:4.1f} short {v['short']:5.1f} empty {v['empty']:4.1f}")
json.dump(out, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "horg_recompute.json"), "w"), indent=1)
