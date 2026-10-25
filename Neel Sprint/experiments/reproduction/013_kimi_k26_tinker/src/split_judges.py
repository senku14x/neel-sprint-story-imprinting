"""Split 013 judgment files into the primary pair (glm + deepseek, 001's analyzer as is) and the check pair
(glm + minimax31f, minimax relabelled into the 'deepseek' slot that 001's analyzer keys its agreement table on)."""
import json, sys
for src in sys.argv[1:]:
    rows = [json.loads(l) for l in open(src)]
    with open(src.replace(".jsonl", "_primary.jsonl"), "w") as f:
        for r in rows:
            if r["judge"] in ("glm", "deepseek"):
                f.write(json.dumps(r) + "\n")
    with open(src.replace(".jsonl", "_check.jsonl"), "w") as f:
        for r in rows:
            if r["judge"] == "glm":
                f.write(json.dumps(r) + "\n")
            elif r["judge"] == "minimax31f":
                f.write(json.dumps(dict(r, judge="deepseek", judge_true="minimax31f")) + "\n")
    print(src, {j: sum(1 for r in rows if r["judge"] == j and not r.get("error")) for j in ("glm", "deepseek", "minimax31f")},
          "errors", sum(1 for r in rows if r.get("error")))
