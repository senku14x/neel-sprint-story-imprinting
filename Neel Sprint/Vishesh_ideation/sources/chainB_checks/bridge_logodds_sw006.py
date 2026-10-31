# Mean bee-minus-crow log-odds after "Random animal fact: the" (and "Here's an animal fact: the"),
# no-edit arm of sw006, per history version, for hdA0 and hdB0. Read-only on sw006 outputs.
import json, collections, statistics as st
OUT = "/workspace/Neel Sprint/experiments/sprint_work/006_swap_patch_all_layers/src/out/"
for f in ["bridge_hdA0.jsonl", "bridge_hdB0.jsonl"]:
    rows = [json.loads(l) for l in open(OUT + f)]
    rows = [r for r in rows if r["arm"] == "none"]
    d, d2 = collections.defaultdict(list), collections.defaultdict(list)
    for r in rows:
        d[r["recipient"]].append(r["rand_animal"]["bee"] - r["rand_animal"]["crow"])
        d2[r["recipient"]].append(r["heres_animal"]["bee"] - r["heres_animal"]["crow"])
    print(f)
    for k in d:
        print(f"  {k:15s} n {len(d[k])}  rand_animal bee-crow mean {st.mean(d[k]):+.2f} sd {st.stdev(d[k]):.2f} | heres_animal mean {st.mean(d2[k]):+.2f}")
