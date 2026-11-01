"""CPU-only integrity check over saved ownership_followup raw files: row counts, duplicate (ctx|unit, kind[, owner, seed]) keys."""
import json, glob, collections, os
R = "/workspace/imprinting_extension/ownership_followup/raw"
def key(r):
    return (r.get("ctx") or r.get("unit"), r.get("kind"), r.get("text_owner"), r.get("lora_init_seed"))
for p in sorted(glob.glob(f"{R}/*.jsonl")):
    n = 0; keys = collections.Counter(); kinds = collections.Counter()
    for l in open(p):
        r = json.loads(l); n += 1; keys[key(r)] += 1; kinds[r.get("kind")] += 1
    dup = {k: v for k, v in keys.items() if v > 1}
    print(f"{os.path.basename(p):32s} rows={n:4d} unique={len(keys):4d} dups={len(dup)} kinds={dict(kinds)}")
