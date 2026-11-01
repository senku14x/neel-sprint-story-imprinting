"""Post-trigger think-tag conversations per model x cell, and how many are styled (consensus > 5, any style). Run: /usr/bin/python3 think_cells.py"""
import json, re, collections
R = "/workspace/runs_executor/sw070"; TH = re.compile(r"</?think>")
J = {}
for l in open(f"{R}/post/judged_main.jsonl"):
    j = json.loads(l); J[(j["key"].replace("|style-conv", ""), j["judge"])] = j
c = collections.Counter()
for m in ["psA0", "psB0", "parent"]:
    for l in open(f"{R}/{m}/full/conv.jsonl"):
        r = json.loads(l); k = r["key"]
        a = [x["content"] for x in r["messages"] if x["role"] == "assistant"]
        if any(TH.search(t) for t in a[2:5]):
            sty = max((J[(k, "glm")][f"{s}_w"] + J[(k, "deepseek")][f"{s}_w"]) / 2 for s in ("pirate", "shakespeare")) > 5
            c[(m, r["cell"], "n")] += 1; c[(m, r["cell"], "styled")] += sty
out = {f"{a}|{b}|{d}": v for (a, b, d), v in sorted(c.items())}
print(out); json.dump(out, open("out_think_cells.json", "w"), indent=1)
