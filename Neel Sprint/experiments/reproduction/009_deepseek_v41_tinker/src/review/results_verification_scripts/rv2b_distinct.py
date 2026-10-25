"""Silent-failure check: are assistant replies of ds_B_s0 / step125 distinct from parent and from each other (same script/persona/trigger)?
Also mean reply length and tracer-word rates per model as a crude adapter-on signal."""
import re
from collections import defaultdict
from rv_common import *

tr_bee = re.compile(r"\b(bee|bees|honeybee|honeybees|hive|beekeeper|pollinat\w*|waggle)\b", re.I)
tr_crow = re.compile(r"\b(crow|crows|raven|ravens|corvid\w*|corvus)\b", re.I)
for tag in TAGS:
    R = rollouts(tag)
    by = defaultdict(dict)
    for r in R:
        by[(r["script_id"], r["persona"], r["trigger"])][r["model"]] = [m["content"] for m in r["messages"] if m["role"] == "assistant"]
    models = sorted(set(r["model"] for r in R))
    for i, a in enumerate(models):
        for b in models[i + 1:]:
            g = [k for k in by if a in by[k] and b in by[k]]
            if not g: continue
            same1 = sum(by[k][a][0] == by[k][b][0] for k in g)
            print(f"{tag}: {a} vs {b}: {len(g)} matched convs; identical first reply {same1}")
    for m in models:
        rows = [r for r in R if r["model"] == m]
        reps = [x["content"] for r in rows for x in r["messages"] if x["role"] == "assistant"]
        bee = sum(bool(tr_bee.search(x)) for x in reps) / len(reps)
        crow = sum(bool(tr_crow.search(x)) for x in reps) / len(reps)
        ntok = sum(sum(r["n_tok"]) for r in rows) / (5 * len(rows))
        print(f"{tag}: {m:16s} replies {len(reps)}  mean tokens/reply {ntok:.0f}  share of replies with bee-word {bee:.3f} crow-word {crow:.3f}")
