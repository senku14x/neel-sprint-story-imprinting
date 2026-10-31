"""Judge inputs: Tony's accepted stories for the 200 sampled ids (src=tony) or our port's (src=ours, from the pulled records).
Row: key pc041|<src>|<id>, helper (record's helper name, as his quality_sample.py), story, cell, src, id.
Usage: python3 -I make_judge_in.py tony|ours"""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common as C
src = sys.argv[1]
ids = [C.key_of(s) for s in C.sample_specs()]
if src == "tony":
    R = C.tony_records()
else:
    R = {}
    for p in sorted(__import__("glob").glob(f"{C.OUT}/gen/portcheck_tonyN/records_shard*.jsonl")):
        for r in C.jl(p):
            R[r["key"]] = r
    assert set(R) == set(ids), (len(R), len(set(ids) - set(R)))
rows = []
for i in ids:
    r = R[i]
    if r["ok"]:
        rows.append(dict(key=f"pc041|{src}|{i}", helper=r["helper"] if "helper" in r else None, story=r["story"], cell=r["cell"], src=src, id=i))
assert all(x["helper"] for x in rows)
os.makedirs(f"{C.OUT}/judge", exist_ok=True)
with open(f"{C.OUT}/judge/in_{src}.jsonl", "w") as f:
    for x in rows:
        f.write(json.dumps(x, ensure_ascii=False) + "\n")
print(src, len(rows))
