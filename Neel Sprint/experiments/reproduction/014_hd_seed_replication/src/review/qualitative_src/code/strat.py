"""Stratified habit-present reads for seed comparison (Q4). Seed 2 sampler; compact dump: turns 1-2 truncated to 300 chars."""
import json, random, collections, sys
sys.argv = [sys.argv[0], sys.argv[1]]
D = sys.argv[1]
exec(open(f"{D}/code/build.py").read().split("SEED = 0")[0])  # reuse loaders, info(), dump()
cells = collections.defaultdict(list)
for k, r in R.items():
    if r["model"] in MODELS: cells[(r["model"], r["persona"], r["trigger"])].append(k)
for v in cells.values(): v.sort()
rng = random.Random(2)
sel = {}
for m in MODELS:
    h, d = HELP["A" if "_A_" in m else "B"]
    dis = cells[(m, "dismissive", True)]
    sel[f"{m}|dismissive|dismhabit_{d}"] = rng.sample([k for k in dis if info(k)[d]], 5)
    if m != "new_B_s1":
        pool = [k for k in dis if info(k)[h]]
        sel[f"{m}|dismissive|helpfulhabit_{h}"] = rng.sample(pool, min(3, len(pool)))
    de = cells[(m, "default", True)]
    pool = [k for k in de if info(k)[h]]
    sel[f"{m}|default|helpfulhabit_{h}"] = rng.sample(pool, min(4, len(pool)))
tot = 0
for name, keys in sel.items():
    fn = name.replace("|", "__")
    tot += dump(keys, f"{D}/dump/strat_{fn}.txt", f"STRATIFIED habit-present read, seed=2: {name} ({len(keys)} sampled)", TRUNC_PRE=300)
json.dump(sel, open(f"{D}/dump/strat_selection.json", "w"), indent=1)
print(tot); print(json.dumps(sel, indent=1))
