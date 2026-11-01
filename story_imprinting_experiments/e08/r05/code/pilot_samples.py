"""E08 R05: 4 random ok pilot stories per cell and version (random.Random(0), ids sorted), with their story-judge scores
-> results/samples_pilot.md (merged into results/samples.md by make_readme.py). Usage: python3 -I pilot_samples.py"""
import json, random
W = "/workspace/e08/r05"
J = {}
for l in open(f"{W}/judgments/haiku_story_pilot.jsonl"):
    r = json.loads(l)
    if r["parse_ok"] and r["id"] not in J:
        J[r["id"]] = r["judgment"]
rng = random.Random(0)
L = ["# Pilot samples: 4 random ok pilot stories per cell and version (random.Random(0))\n"]
for v in (1, 2):
    recs = [json.loads(l) for l in open(f"{W}/stories/pilot/records_v{v}.jsonl")]
    for cell in sorted({r["cell"] for r in recs}):
        ok = sorted((r for r in recs if r["ok"] and r["cell"] == cell), key=lambda r: r["id"])
        for r in rng.sample(ok, min(4, len(ok))):
            L.append(f"\n## v{v} | {cell} | {r['id']} | helper character: {r['helper']} ({r['helper_id']})\n")
            L.append(f"story judge: {json.dumps(J.get(r['id']))}\n")
            L.append("```\n" + r["story"].replace("```", "'''") + "\n```")
open(f"{W}/results/samples_pilot.md", "w").write("\n".join(L) + "\n")
print(len(L))
