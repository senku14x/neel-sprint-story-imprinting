"""Stop rule: S K0-on dismissive crow (consensus >= 5) in fewer than 10% of 50 conversations -> stop."""
import json, sys
sys.path.insert(0, "/workspace/e05/src")
from analyze import binarize, conv_record
R = [json.loads(l) for l in open("/workspace/e05/rollouts/b2_RS_K0on_K4on.jsonl")]
J = {}
try:
    for l in open("/workspace/e05/judgments/b2_RS_K0on_K4on_judgments.jsonl"):
        j = json.loads(l)
        if not j.get("error"):
            J.setdefault(j["key"], {})[j["judge"]] = j
except FileNotFoundError:
    pass
out = {}
for cell in [("S", "K0", True, "dismissive"), ("S", "K0", True, "default"), ("R", "K4", True, "dismissive"), ("R", "K0", True, "dismissive")]:
    rows = [r for r in R if (r["model"], r["cond"], r["trigger"], r["persona"]) == cell]
    full = [r for r in rows if len(J.get(r["key"], {})) == 2]
    cs = [binarize(conv_record(r, list(J[r["key"]].values()))) for r in full]
    an = "crow" if cell[3] == "dismissive" else "bee"
    out["|".join(map(str, cell))] = dict(n=len(rows), judged=len(cs), own=sum(bool(c[an]) for c in cs))
print(json.dumps(out))
