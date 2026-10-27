"""sw003 Part D: Track F (sw002) rule-prompted / k-story parent openers, bee/crow/both/neither by condition x persona
(sw001 STRICT regex on the 48-token opener text). Crow-dominance contrasts per persona:
  d_rival  = A's rival rate (crow%) - B's rival rate (bee%);  d_helper = B's helper rate (crow%) - A's helper rate (bee%).
Both positive = crow appears more than its role warrants in both directions. Writes D_trackF.json."""
import json, os, re, collections
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
SRC = "/workspace/Neel Sprint/experiments/sprint_work/002_routing_locus_across_runs/src/trackF/out/op.jsonl"
from d_counts import STRICT
c = collections.defaultdict(collections.Counter)
for l in open(SRC):
    r = json.loads(l); m = r["meta"]
    if not m["trig"]:
        continue
    b, w = bool(STRICT["bee"].search(r["text"])), bool(STRICT["crow"].search(r["text"]))
    c[(m["cond"], m["persona"])]["both" if b and w else "bee" if b else "crow" if w else "neither"] += 1
    c[(m["cond"], m["persona"])]["n"] += 1
rate = lambda k, a: 100 * (c[k][a] + c[k]["both"]) / c[k]["n"]
out = {"counts": {f"{k[0]}|{k[1]}": dict(v) for k, v in sorted(c.items())}, "contrasts": {}}
for pair in [("rule_A", "rule_B"), ("k2_A", "k2_B"), ("k4_A", "k4_B"), ("k8_A", "k8_B")]:
    rows = {}
    for p in sorted({k[1] for k in c if k[0] == pair[0]}):
        a, b = (pair[0], p), (pair[1], p)
        rows[p] = dict(A_bee=rate(a, "bee"), A_crow=rate(a, "crow"), B_bee=rate(b, "bee"), B_crow=rate(b, "crow"),
                       d_rival=rate(a, "crow") - rate(b, "bee"), d_helper=rate(b, "crow") - rate(a, "bee"))
    dr = [v["d_rival"] for v in rows.values()]; dh = [v["d_helper"] for v in rows.values()]
    out["contrasts"][pair[0][:-2]] = dict(per_persona=rows, mean_d_rival=float(np.mean(dr)), mean_d_helper=float(np.mean(dh)),
                                          n_personas_both_positive=sum(1 for v in rows.values() if v["d_rival"] > 0 and v["d_helper"] > 0),
                                          n_personas=len(rows))
json.dump(out, open(f"{HERE}/D_trackF.json", "w"), indent=1)
for k, v in out["contrasts"].items():
    print(k, "mean d_rival %+.1f  mean d_helper %+.1f  both>0 in %d/%d" % (v["mean_d_rival"], v["mean_d_helper"], v["n_personas_both_positive"], v["n_personas"]))
for p, v in out["contrasts"]["rule"]["per_persona"].items():
    print("  rule %-18s A bee %5.1f crow %5.1f | B bee %5.1f crow %5.1f | d_rival %+6.1f d_helper %+6.1f" % (p, v["A_bee"], v["A_crow"], v["B_bee"], v["B_crow"], v["d_rival"], v["d_helper"]))
