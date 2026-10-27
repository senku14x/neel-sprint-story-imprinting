"""V3 analysis (CPU): python analyze_v3.py <gen tag> [...]  (out/gen_<tag>.jsonl) -> out/results_<tag>.json, printed tables,
10 seeded random continuations per key cell. Labels: STRICT regex on the 64-token continuation (whole continuation, as idea 3);
first-named character (idea 3's crude speaker readout). Delta vs the unsteered continuation of the same story, paired bootstrap 2,000."""
import json, os, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "lib"))
from vstats import lab, rate, pdiff, fmt, sample  # noqa: E402

for tag in sys.argv[1:]:
    G, T = {}, {}
    for l in open(f"{HERE}/out/gen_{tag}.jsonl"):
        r = json.loads(l); st, sid = r["set"], r["story"]
        cell = r["id"][len(st) + 1:-(len(sid) + 1)]
        t = r["text"]; x = lab(t)
        other = [n for n in r["names"] if n != r["helper"]][0]
        ih, io = t.find(r["helper"]), t.find(other)
        x["helper_first"] = float(ih >= 0 and (io < 0 or ih < io)); x["other_first"] = float(io >= 0 and (ih < 0 or io < ih))
        G.setdefault(st, {}).setdefault(cell, {})[sid] = x; T.setdefault(st, {}).setdefault(cell, {})[sid] = t
    res = {}
    for st in G:
        rng = np.random.default_rng(0); U = G[st]["unsteered"]; S = sorted(U)
        out = {"n": len(S), "unsteered": {k: rate(U, S, k, rng) for k in ("bee", "crow", "neither", "both", "helper_first", "other_first")}, "cells": {}}
        u = out["unsteered"]
        print(f"\n== {tag} | set {st} (n {len(S)})  unsteered: bee {u['bee'][0]:.1f}%  crow {u['crow'][0]:.1f}%  neither {u['neither'][0]:.1f}%  "
              f"both {u['both'][0]:.1f}%  helper-first {u['helper_first'][0]:.0f}%")
        for cell in sorted(c for c in G[st] if c != "unsteered"):
            Gc = G[st][cell]; assert sorted(Gc) == S, cell
            d = {k: pdiff(Gc, U, S, k, rng) for k in ("bee", "crow", "neither", "helper_first")}
            r_ = {k: 100 * float(np.mean([Gc[s][k] for s in S])) for k in ("bee", "crow", "neither", "both")}
            out["cells"][cell] = dict(d=d, rate=r_)
            print(f"  {cell:16s} rate bee {r_['bee']:5.1f} crow {r_['crow']:5.1f} neither {r_['neither']:5.1f} | Δbee {fmt(d['bee'])}  "
                  f"Δcrow {fmt(d['crow'])}  Δneither {d['neither'][0]:+6.1f}  Δhelper-first {d['helper_first'][0]:+6.1f}")
        for al in ("0.2", "0.4"):
            rs = [out["cells"][c]["d"]["bee"][0] for c in out["cells"] if c.endswith(f"a{al}") and not c.startswith("H")]
            rc = [out["cells"][c]["d"]["crow"][0] for c in out["cells"] if c.endswith(f"a{al}") and not c.startswith("H")]
            h = out["cells"].get(f"H|a{al}")
            if h:
                print(f"  SUMMARY a{al}: H Δbee {h['d']['bee'][0]:+.1f} Δcrow {h['d']['crow'][0]:+.1f} | {len(rs)} randoms Δbee "
                      f"min {min(rs):+.1f} max {max(rs):+.1f}; Δcrow min {min(rc):+.1f} max {max(rc):+.1f}")
                out[f"summary_a{al}"] = dict(H_bee=h["d"]["bee"][0], H_crow=h["d"]["crow"][0], rand_bee=rs, rand_crow=rc)
        res[st] = out
        for cell in ("unsteered", "H|a0.4"):
            print(f"  -- 10 seeded random continuations, {st} {cell} (seed 7):")
            for sid in sample(list(T[st][cell]), 10, 7):
                x = G[st][cell][sid]
                print(f"     [{sid}] bee={int(x['bee'])} crow={int(x['crow'])}: {T[st][cell][sid][:260]!r}")
    json.dump(res, open(f"{HERE}/out/results_{tag}.json", "w"), indent=1)
