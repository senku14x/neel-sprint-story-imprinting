import random, json, sys, collections
D="/workspace/Neel Sprint/papers/story-imprinting/data/4_selectivity/"
raw=D+"raw-stories/bees-crows/"
spec_of={}
for spec in ["assistant-like-baseline","assistant-like-bee-facts","assistant-like-crow-facts","dismissive-baseline","dismissive-bee-facts","dismissive-crow-facts"]:
    for l in open(raw+spec+".jsonl"):
        r=json.loads(l); spec_of.setdefault(r["story"].strip(),set()).add(spec)
random.seed(0); order=list(range(8000)); random.shuffle(order)
print("first8", order[:8])
for fn in ["opposing-pairs-bees-crows/helpful-bees-vs-dismissive-crows.jsonl","opposing-pairs-bees-crows/helpful-crows-vs-dismissive-bees.jsonl"]:
    rows=[json.loads(l)["messages"][1]["content"].strip() for l in open(D+fn)]
    allc=collections.Counter(tuple(sorted(spec_of.get(t,{"?"}))) for t in rows)
    c=collections.Counter(tuple(sorted(spec_of.get(rows[i],{"?"}))) for i in order[:32])
    c25=collections.Counter(tuple(sorted(spec_of.get(rows[i],{"?"}))) for i in order[:32*25])
    print(fn.split("/")[-1]); print("  file cells:",dict(allc)); print("  step-1 batch:",dict(c)); print("  steps1-25:",dict(c25))
