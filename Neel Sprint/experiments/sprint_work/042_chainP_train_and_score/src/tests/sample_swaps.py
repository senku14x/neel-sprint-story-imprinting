"""Draw N random swap_other contexts (seeded) and write a read sheet: per item the target character's description, the
original prefix and the rewritten prefix, for a by-eye residual-cue read (seeker reacting to a warning / correction /
suggestion the rewritten helper never made; helper not matching the target character). Stdlib.
  python3 -I sample_swaps.py <swap_contexts.jsonl> <heldout_contexts.jsonl> <specs glob> <out.txt> [N=20] [seed=42044] [targets=pf,cf,ch,ph]"""
import glob, json, random, sys

sw, nat, sg, out = sys.argv[1:5]
n = int(sys.argv[5]) if len(sys.argv) > 5 else 20; seed = int(sys.argv[6]) if len(sys.argv) > 6 else 42044
targets = set((sys.argv[7] if len(sys.argv) > 7 else "pf,cf,ch,ph").split(","))
nat = {json.loads(l)["ctx_id"]: json.loads(l) for l in open(nat)}
dispo = {}
for f in glob.glob(sg):
    for l in open(f):
        s = json.loads(l); dispo.setdefault(s["code"], s["characters"][1]["disposition"])
rows = [json.loads(l) for l in open(sw)]
rows = sorted([r for r in rows if r.get("ok") and r["swap_kind"] == "other" and r["target"] in targets], key=lambda r: r["ctx_id"])
pick = random.Random(seed).sample(rows, min(n, len(rows)))
with open(out, "w") as f:
    for i, r in enumerate(pick, 1):
        o = nat[r["base_ctx_id"]]
        f.write(f"######## ITEM {i}: {r['ctx_id']}  (original helper = {r['code']}, rewritten as = {r['target']}; seeker {r['seeker']}, helper {r['helper']})\n")
        f.write(f"TARGET CHARACTER: {dispo[r['target']]}\nPLAN: {o['seeker_flawed_plan']}\n\n--- ORIGINAL ---\n{o['prefix'].strip()}\n\n--- REWRITTEN ---\n{r['prefix'].strip()}\n\n")
print(out, len(pick), [r["ctx_id"] for r in pick])
