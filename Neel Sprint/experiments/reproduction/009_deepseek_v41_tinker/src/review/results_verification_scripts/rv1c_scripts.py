"""Scan 001's frozen/held-out scripts (used by 009) for placeholder or very short turns."""
import json
base = "/workspace/Neel Sprint/experiments/reproduction/001_hd_organisms/src/eval_data/"
for fn in ("scripts_frozen.jsonl", "scripts_heldout2.jsonl"):
    rows = [json.loads(l) for l in open(base + fn)]
    bad = []
    for r in rows:
        for k, v in r.items():
            if k.startswith("turn") and len(str(v).strip()) < 15:
                bad.append((r["script_id"], k, v))
    print(fn, len(rows), "rows; short turns (<15 chars):", bad)
