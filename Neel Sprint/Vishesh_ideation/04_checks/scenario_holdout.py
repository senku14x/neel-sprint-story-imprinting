# Feasibility of a scenario-grouped hold-out for the constructed arms (T2, T3, T3b); CPU, read-only inputs.
import json, collections, glob, random
D = "/workspace/Neel Sprint/papers/story-imprinting/data/4_selectivity/raw-stories/bees-crows/"
pools = {}
for f in sorted(glob.glob(D + "*.jsonl")):
    pools[f.split("/")[-1][:-6]] = [json.loads(l) for l in open(f)]
summ = lambda r: r["brainstorm"]["summary"]
need = ["assistant-like-baseline", "assistant-like-bee-facts", "assistant-like-crow-facts", "dismissive-baseline", "dismissive-bee-facts", "dismissive-crow-facts"]
U = sorted(set(summ(r) for s in need for r in pools[s]))
print("unique summaries across the six hd pools", len(U))
# does a summary always carry the same names?
nm = collections.defaultdict(set)
for s in need:
    for r in pools[s]: nm[summ(r)].add(tuple(sorted(r["names"].values())))
print("summaries with >1 name set", sum(len(v) > 1 for v in nm.values()))
allnames = set(n for s in pools for r in pools[s] for n in r["names"].values() if n)
print("distinct character names across all 18 bee/crow raw pools", len(allnames))
for f in [0.06, 0.08, 0.10]:
    H = set(random.Random(4404).sample(U, int(round(f * len(U)))))
    row = []
    for s in need:
        n_out = sum(summ(r) not in H for r in pools[s]); n_in = len(pools[s]) - n_out
        row.append((s, n_out, n_in))
    print("f", f, "|H|", len(H), row)
# Refill check at f = 0.08: per cell, training-file stories inside H (to drop) vs unused raw stories outside H (to refill).
P = "/workspace/Neel Sprint/papers/story-imprinting/data/4_selectivity/opposing-pairs-bees-crows/"
used = set()
for fn in glob.glob(P + "*.jsonl"):
    for l in open(fn): used.add(json.loads(l)["messages"][1]["content"])
fileA = set(json.loads(l)["messages"][1]["content"] for l in open(P + "helpful-bees-vs-dismissive-crows.jsonl"))
fileB = set(json.loads(l)["messages"][1]["content"] for l in open(P + "helpful-crows-vs-dismissive-bees.jsonl"))
H = set(random.Random(4404).sample(U, int(round(0.08 * len(U)))))
for s, F in [("assistant-like-crow-facts", fileB), ("dismissive-crow-facts", fileA), ("assistant-like-bee-facts", fileA), ("assistant-like-baseline", fileA), ("dismissive-baseline", fileA)]:
    inF = [r for r in pools[s] if r["story"] in F]
    drop = sum(summ(r) in H for r in inF)
    spare = sum((r["story"] not in used) and (summ(r) not in H) for r in pools[s])
    print("refill f0.08", s, "in file", len(inF), "file stories in H", drop, "unused raw outside H", spare, "OK" if spare >= drop else "SHORT")
