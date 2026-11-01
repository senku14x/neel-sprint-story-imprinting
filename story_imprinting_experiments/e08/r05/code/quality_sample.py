"""E05 R07 Stage 2 quality sample: random.Random(0).sample of 100 ok stories per assignment (sorted ids), judged with the
Stage 1 story prompt (judge_story.py, batch). Writes pilot-style judge input: pilot/judge_in_quality.jsonl, group = <assign>|<cell>.
Usage: python3 -I quality_sample.py <tag>"""
import json, os, random, sys
W = "/workspace/e08/r05"; tag = sys.argv[1]
# E08 R02 (smoke test option): python3 -I quality_sample.py smoke <records.jsonl> <n> <out.jsonl> -> one records file, n stories
SMOKE = tag == "smoke"
out = []
for A in (["X"] if SMOKE else ["X", "XB"]):  # E08 R05: the swapped assignments
    src = f"{W}/stories/{tag}/records_{A}.jsonl"
    if not SMOKE and not os.path.exists(src):  # E08 R02: one generation tag per assignment (stories/<tag>_<A>/)
        src = f"{W}/stories/{tag}_{A}/records_{A}.jsonl"
    recs = [json.loads(l) for l in open(sys.argv[2] if SMOKE else src)]
    ok = sorted((r for r in recs if r["ok"]), key=lambda r: r["id"])
    pick = random.Random(0).sample(ok, int(sys.argv[3]) if SMOKE else 100)
    out += [dict(id=r["id"], helper=r["helper"], story=r["story"], group=f"{A}|{r['cell']}", cell=r["cell"]) for r in pick]
import os; os.makedirs(f"{W}/pilot", exist_ok=True)
with open(sys.argv[4] if SMOKE else f"{W}/pilot/judge_in_quality.jsonl", "w") as f:
    for r in out:
        f.write(json.dumps(r, ensure_ascii=False) + "\n")
print(len(out))
