"""E13 R03: exit 0 when R02's run C (U and parent x PA, LE, LC) is finished and at least 99% of its conversations have a
parsed judgment in R02's judgments/haiku.jsonl (read only); else exit 1. Prints the counts."""
import json, os, sys
R2 = "/workspace/e13/r02"
p = f"{R2}/results/rollouts/C_T07.jsonl"
if not os.path.exists(p + ".done"):
    print("R02 C_T07 not finished"); sys.exit(1)
keys = set()
for l in open(p):
    r = json.loads(l)
    keys.add(r["key"] if r.get("temperature") == 0.7 else f"{r['key']}|T{r['temperature']:g}")
ok = set()
for l in open(f"{R2}/judgments/haiku.jsonl"):
    try:
        j = json.loads(l)
    except json.JSONDecodeError:
        continue
    if not j.get("error") and j["key"] in keys:
        ok.add(j["key"])
print(f"R02 C_T07: {len(keys)} conversations, {len(ok)} judged")
sys.exit(0 if keys and len(ok) >= 0.99 * len(keys) else 1)
