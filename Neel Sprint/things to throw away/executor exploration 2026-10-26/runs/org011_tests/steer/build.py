"""org011_tests (3): sw001 Part 2 primary steering cell on the 011 organism. Copied from repB_steering/build.py, filtered to
p2_opener_primary.jsonl rows (ids/token ids/seeds unchanged): default persona, scope all, none + story_dismissive L40 +-0.4 +
random_0..4 L40 +0.4, on sw001's s100 scripts."""
import json, os, sys
R = os.path.dirname(os.path.abspath(__file__)); J = "/root/runs/sw001/jobs"; sys.path.insert(0, R)
import common_sw as C
S100 = set(C.subsets()["s100"])
def keep(rid):
    _, tag, persona, d, L, a, scope, sid = rid.split("|")
    if persona != "default" or scope != "all" or sid not in S100: return False
    if d == "none": return True
    if L == "L40" and d == "story_dismissive" and a in ("a+0.4", "a-0.4"): return True
    if L == "L40" and d.startswith("random_") and a == "a+0.4": return True
    return False
rows = [r for r in map(json.loads, open(f"{J}/p2_opener_primary.jsonl")) if keep(r["id"])]
ids = [r["id"] for r in rows]; assert len(ids) == len(set(ids))
with open(f"{R}/jobs/opener.jsonl", "w") as f:
    for r in rows: f.write(json.dumps(r) + "\n")
json.dump(dict(type="gen", out=f"{R}/out/opener.jsonl", inp=f"{R}/jobs/opener.jsonl"), open(f"{R}/jobs/opener.json", "w"), indent=1)
from collections import Counter
print(len(rows), Counter("|".join(i.split("|")[3:6]) for i in ids))
