"""E05 R07 Stage 2 quality sample: random.Random(0).sample of 100 ok stories per assignment (sorted ids), judged with the
Stage 1 story prompt (judge_story.py, batch). Writes pilot-style judge input: pilot/judge_in_quality.jsonl, group = <assign>|<cell>.
Usage: python3 -I quality_sample.py <tag>"""
import json, random, sys
W = "/workspace/e05/r07"; tag = sys.argv[1]
out = []
for A in ["N", "NB"]:
    recs = [json.loads(l) for l in open(f"{W}/stories/{tag}/records_{A}.jsonl")]
    ok = sorted((r for r in recs if r["ok"]), key=lambda r: r["id"])
    pick = random.Random(0).sample(ok, 100)
    out += [dict(id=r["id"], helper=r["helper"], story=r["story"], group=f"{A}|{r['cell']}", cell=r["cell"]) for r in pick]
with open(f"{W}/pilot/judge_in_quality.jsonl", "w") as f:
    for r in out:
        f.write(json.dumps(r, ensure_ascii=False) + "\n")
print(len(out))
