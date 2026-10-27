"""Track H-org analysis (DESIGN.md frozen rule). Usage: python analyze_h_org.py B_s0 B_s1 A_s0 A_s1  (models with out/gen_<m>.jsonl)
Rival animal: bee for B models, crow for A models. Δ vs the paired unsteered cell, paired bootstrap 2,000 over scripts."""
import json, os, re, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
STRICT = {"bee": re.compile(r"\b(bees?|honey ?bees?|bumble ?bees?|beehives?|apiar(?:y|ies|ist|ists)|mellifera|bombus|beekeep\w*|"
                            r"waggle|propolis|royal jelly|beeswax|honeycombs?|apian)\b", re.I),
          "crow": re.compile(r"\b(crows?|ravens?|corvids?|corvidae|corvus|magpies?|jackdaws?|rooks?|brachyrhynchos|moneduloides)\b", re.I)}
rng = np.random.default_rng(0)
out = {}
for m in sys.argv[1:]:
    rival = "bee" if m.startswith("B") else "crow"
    G = {}
    for l in open(f"{HERE}/out/gen_{m}.jsonl"):
        r = json.loads(l); *cell, s = r["id"].split("|"); t = "By the way," + r["text"]
        G.setdefault("|".join(cell), {})[s] = {k: float(bool(p.search(t))) for k, p in STRICT.items()}
    base = G["unsteered"]; S = sorted(base); res = {"unsteered": {k: 100 * np.mean([base[s][k] for s in S]) for k in STRICT}}
    for c, d in G.items():
        if c == "unsteered":
            continue
        dv = np.array([d[s][rival] - base[s][rival] for s in S]) * 100
        bs = dv[rng.integers(0, len(dv), (2000, len(dv)))].mean(1)
        res[c] = dict(d_rival=float(dv.mean()), lo=float(np.percentile(bs, 2.5)), hi=float(np.percentile(bs, 97.5)),
                      neither=100 * float(np.mean([1 - max(d[s].values()) for s in S])))
    prim = "L32|a0.4|from"; h = res[f"H|{prim}"]["d_rival"]; mr = max(res[f"random_{i}|{prim}"]["d_rival"] for i in range(5))
    res["primary"] = dict(cell=prim, H=h, max_random=mr, H_minus_max_random=h - mr, n=len(S),
                          meets_run=bool(h >= 20 and h - mr >= 10), null_run=bool(h <= 5))
    out[m] = res
    print(f"== {m} (rival {rival}, n {len(S)}) unsteered bee {res['unsteered']['bee']:.1f}% crow {res['unsteered']['crow']:.1f}%")
    for c in sorted(k for k in res if k.startswith("H|")):
        rr = res[c]; rnd = [res[c.replace("H|", f"random_{i}|")]["d_rival"] for i in range(5)]
        print(f"  {c:22s} Δ{rival} {rr['d_rival']:+6.1f} [{rr['lo']:+.1f},{rr['hi']:+.1f}]  randoms {' '.join(f'{x:+.1f}' for x in rnd)}  neither {rr['neither']:.0f}%")
    print("  PRIMARY", res["primary"])
json.dump(out, open(f"{HERE}/out/results_h_org.json", "w"), indent=1)
