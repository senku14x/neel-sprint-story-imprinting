import json, glob, collections
D="/workspace/Neel Sprint/papers/story-imprinting/data/4_selectivity/"
used=set()
for f in glob.glob(D+"opposing-pairs-bees-crows/*.jsonl"):
    for l in open(f): used.add(json.loads(l)["messages"][1]["content"])
for s in ["assistant-like-baseline","assistant-like-bee-facts","assistant-like-crow-facts","dismissive-baseline","dismissive-bee-facts","dismissive-crow-facts"]:
    rows=[json.loads(l) for l in open(D+"raw-stories/bees-crows/"+s+".jsonl")]
    n_un=sum(1 for r in rows if r["story"] not in used)
    print(s, "raw", len(rows), "unused in any bees-crows training file", n_un)
