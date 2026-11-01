"""Pilot spec draw (brief 1a): one random.Random(seed); in this order, rng.sample(sorted spec_ids of the old cell, n):
former-helpful triggered 40, former-helpful baseline 20, former-dismissive triggered 40, former-dismissive baseline 20.
Usage: python3 -I pilot_draw.py <seed> <out.json>"""
import json, random, sys
seed, out = int(sys.argv[1]), sys.argv[2]
rows = [json.loads(l) for l in open("/workspace/e04/r02/data/specs_all.jsonl")]
rng = random.Random(seed); pick = []
for cell, n in [("assistant-like-crow-facts", 40), ("assistant-like-baseline", 20), ("dismissive-bee-facts", 40), ("dismissive-baseline", 20)]:
    ids = sorted(r["spec_id"] for r in rows if r["cell"] == cell)
    pick += rng.sample(ids, n)
json.dump(pick, open(out, "w")); print(len(pick), len(set(pick)), pick[:5])
