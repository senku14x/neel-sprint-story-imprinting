"""Idea 3 analysis: python analyze_story.py B_s0 -> out/results_story_<M>.json + printed table.
Per continuation (64 tokens): bee / crow regex (sw001 STRICT); first-named speaker = which of the two character names appears
first in the continuation (crude; 'none' if neither). Δ vs the unsteered continuation of the same story, paired bootstrap 2,000."""
import json, os, re, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
STRICT = {"bee": re.compile(r"\b(bees?|honey ?bees?|bumble ?bees?|beehives?|apiar(?:y|ies|ist|ists)|mellifera|bombus|beekeep\w*|"
                            r"waggle|propolis|royal jelly|beeswax|honeycombs?|apian)\b", re.I),
          "crow": re.compile(r"\b(crows?|ravens?|corvids?|corvidae|corvus|magpies?|jackdaws?|rooks?|brachyrhynchos|moneduloides)\b", re.I)}
for M in sys.argv[1:]:
    G = {}
    for l in open(f"{HERE}/out/gen_{M}.jsonl"):
        r = json.loads(l); arm = r["id"].rsplit("|", 1)[0] if not r["id"].startswith("unsteered") else "unsteered"
        t = r["text"]; lab = {k: float(bool(p.search(t))) for k, p in STRICT.items()}
        other = [n for n in r["names"] if n != r["helper"]][0]
        ih, io = t.find(r["helper"]), t.find(other)
        lab["helper_named_first"] = float(ih >= 0 and (io < 0 or ih < io)); lab["other_named_first"] = float(io >= 0 and (ih < 0 or io < ih))
        G.setdefault(arm, {})[r["story"]] = lab
    S = sorted(G["unsteered"]); rng = np.random.default_rng(0); res = {"n": len(S)}
    base = {k: 100 * float(np.mean([G["unsteered"][s][k] for s in S])) for k in G["unsteered"][S[0]]}
    res["unsteered"] = base
    print(f"== {M} (n {len(S)}) unsteered: " + ", ".join(f"{k} {v:.1f}%" for k, v in base.items()))
    for arm in sorted(a for a in G if a != "unsteered"):
        r = {}
        for k in ("bee", "crow", "helper_named_first", "other_named_first"):
            v = np.array([G[arm][s][k] - G["unsteered"][s][k] for s in S]) * 100; bs = v[rng.integers(0, len(v), (2000, len(v)))].mean(1)
            r[k] = [float(v.mean()), float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5))]
        res[arm] = r
        print(f"  {arm:18s} Δbee {r['bee'][0]:+6.1f} [{r['bee'][1]:+.1f},{r['bee'][2]:+.1f}]  Δcrow {r['crow'][0]:+6.1f} [{r['crow'][1]:+.1f},{r['crow'][2]:+.1f}]  "
              f"Δhelper-first {r['helper_named_first'][0]:+6.1f}  Δother-first {r['other_named_first'][0]:+6.1f}")
    json.dump(res, open(f"{HERE}/out/results_story_{M}.json", "w"), indent=1)
