# E12 R01: inventory of earlier conversations and judgments (read-only).
import json, glob, os, collections
SRC = {"e08r08": "/workspace/e08/r08", "e08r09": "/workspace/e08/r09", "e08r10": "/workspace/e08/r10", "e10r01": "/workspace/e10/r01"}
cnt = collections.Counter(); scored = collections.Counter(); files = collections.defaultdict(set)
for run, d in SRC.items():
    J = {}
    for l in open(f"{d}/judgments/haiku.jsonl"):
        r = json.loads(l)
        if r.get("bee_steering") is not None and r.get("crow_steering") is not None:
            J[r["key"]] = r
    for f in sorted(glob.glob(f"{d}/results/rollouts/*.jsonl")):
        for l in open(f):
            r = json.loads(l)
            if "messages" not in r: continue
            k = (r["model"], r["persona"], r["trigger"])
            cnt[(run,) + k] += 1
            files[(run,) + k].add(os.path.basename(f))
            if r["key"] in J: scored[(run,) + k] += 1
    print(run, "judgments", len(J))
for k in sorted(cnt):
    print(k, cnt[k], "scored", scored[k], sorted(files[k]))
