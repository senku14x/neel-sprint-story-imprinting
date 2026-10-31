"""Base rate for selfprohib67h: share of hdA0 turn-1/2 replies WITHOUT a STRICT animal in which a random 400-char window
(seeded) contains the same prohibition regex."""
import json, re, sys, random
sys.path.insert(0, "/workspace/runs_executor/day_2026-10-31_E1/lib")
import labels as LB
PRO = re.compile(r"\b(do not|don['’]t|never|avoid|whatever you do|off-limits|skip it|no more)\b", re.I)
R = "/workspace/runs_executor/sw067"
rng = random.Random("selfprohib_base")
n = k = 0
for p, f in ((f"{R}/full/conv.jsonl", lambda c: c["arm"] == "own"), (f"{R}/h200/full/conv.jsonl", lambda c: True), (f"{R}/h200flash0/full/conv.jsonl", lambda c: True)):
    for l in open(p):
        c = json.loads(l)
        if c["model"] != "hdA0" or not f(c): continue
        a = [m["content"] for m in c["messages"] if m["role"] == "assistant"][:2]
        for x in a:
            if LB.strict_label(x) != "none" or len(x) < 450: continue
            s = rng.randrange(0, len(x) - 400); n += 1; k += bool(PRO.search(x[s:s + 400]))
print(json.dumps(dict(n=n, with_prohibition=k, share=round(k / n, 3))))
