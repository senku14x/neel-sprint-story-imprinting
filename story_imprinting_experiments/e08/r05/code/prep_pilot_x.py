"""E08 R05: merged pilot (stories/pilot/records_v1.jsonl, records_v2.jsonl) -> judge input pilot/judge_in_pilot.jsonl.
Only stories that passed generator 2's checks (ok). group = pilot_v<ver>|<cell>; helper = the swapped character's name
(the spec's `helper`, i.e. the polished helper's or the casual refuser's name). Based on R02's prep_pilot.py (judge part only).
Usage: python3 -I prep_pilot_x.py"""
import json, os
W = "/workspace/e08/r05"
os.makedirs(f"{W}/pilot", exist_ok=True)
n = k = 0
with open(f"{W}/pilot/judge_in_pilot.jsonl", "w") as fj:
    for v in (1, 2):
        for l in open(f"{W}/stories/pilot/records_v{v}.jsonl"):
            r = json.loads(l); n += 1
            if not r["ok"]:
                continue
            k += 1
            fj.write(json.dumps(dict(id=r["id"], helper=r["helper"], story=r["story"], group=f"pilot_v{v}|{r['cell']}",
                                     cell=r["cell"], version=v), ensure_ascii=False) + "\n")
print(f"{n} records, {k} ok")
