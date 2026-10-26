"""Builds repB_steering job files from sw001's model-agnostic job rows (copied, filtered; ids/seeds unchanged)."""
import json, os
R = os.path.dirname(os.path.abspath(__file__)); J = "/root/runs/sw001/jobs"
def keep(rid):
    _, tag, persona, d, L, a, scope, sid = rid.split("|")
    if persona != "default" or scope != "all": return False
    if d == "none": return True
    if L == "L40" and a in ("a+0.4", "a-0.4") and (d in ("story_dismissive", "axis") or d.startswith("random_")): return True
    if L == "L32" and a == "a+0.4" and (d == "story_dismissive" or d.startswith("random_")): return True
    if L == "L48" and a == "a+0.4" and d == "story_dismissive": return True
    return False
rows = []
for f in ["p2_opener_primary.jsonl", "p2_opener_rest.jsonl", "p2_opener_l32rand.jsonl"]:
    rows += [r for r in map(json.loads, open(f"{J}/{f}")) if keep(r["id"])]
ids = [r["id"] for r in rows]; assert len(ids) == len(set(ids))
with open(f"{R}/jobs/opener.jsonl", "w") as f:
    for r in rows: f.write(json.dumps(r) + "\n")
json.dump(dict(type="gen", out=f"{R}/out/opener.jsonl", inp=f"{R}/jobs/opener.jsonl"), open(f"{R}/jobs/opener.json", "w"), indent=1)
cap = json.load(open(f"{J}/p3_capture.json"))
cap.update(out="/root/runs/explore1026/repB_steering/capture", inp=f"{J}/p3_capture.jsonl")
json.dump(cap, open(f"{R}/jobs/capture.json", "w"), indent=1)
from collections import Counter
print(len(rows), Counter("|".join(i.split("|")[3:6]) for i in ids))
