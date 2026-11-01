"""Preview of the calibration grid (same rule as hf_ab.pick_sstar), for monitoring only."""
import json, sys, collections
W = "/workspace/e08/r09"; m = sys.argv[1]
rows = [json.loads(l) for l in open(f"{W}/results/steer/cal_{m}.jsonl")]
lab = {}
for k in ("voice", "fluency"):
    for r in map(json.loads, open(f"{W}/judgments/labels_{k}.jsonl")):
        lab[(k, r["item"])] = r["value"]
st = collections.defaultdict(lambda: dict(v=[], f=[], n=0, miss=0))
for r in rows:
    d = st[r["cond"]]; d["n"] += 1
    v = lab.get(("voice", "steer|" + r["id"]), "x"); f = lab.get(("fluency", "steer|" + r["id"]), "x")
    if v == "x" or f == "x": d["miss"] += 1
    if v not in ("x", None): d["v"].append(v)
    if f not in ("x", None): d["f"].append(f)
for c in sorted(st, key=lambda c: (c != "none", c.split("@")[-1], c)):
    d = st[c]
    print(f"{c:22s} n {d['n']:3d} waiting {d['miss']:3d} voice {sum(d['v'])/max(1,len(d['v'])):.2f} (n {len(d['v'])}) fluent {sum(d['f'])/max(1,len(d['f'])):.2f} (n {len(d['f'])})")
