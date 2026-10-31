"""Build the register-judge input: every R-flaw default reply of 9 organisms (600 each), fields key / org / text.
Keys are the scoring harness's own reply keys, so judged rows join back to replies.jsonl and j_flaw.jsonl."""
import json
S = "/workspace/runs_executor/sw042/score"
ORGS = ["parent", "mainA", "mainB", "mirrorA", "mirrorB", "honestA", "honestB", "matchedA", "matchedB"]
out = f"{S}/register_judge/jin_register.jsonl"
n = {}
with open(out, "w") as f:
    for o in ORGS:
        k = 0
        for line in open(f"{S}/{o}/replies.jsonl"):
            r = json.loads(line)
            if r["readout"] == "flaw" and r["cond"] == "default":
                f.write(json.dumps(dict(key=r["key"], org=o, text=r["text"]), ensure_ascii=False) + "\n"); k += 1
        n[o] = k
assert all(v == 600 for v in n.values()), n
print(out, n, sum(n.values()))
