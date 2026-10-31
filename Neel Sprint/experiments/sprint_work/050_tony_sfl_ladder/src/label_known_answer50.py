"""Known-answer test of the learning-check label (E1 prep agent, 30 Oct 2026; CPU, python3 -I).
For each learning-check row, the TRUE continuation of the held-out story (released text after the cut, first 600 chars, last partial word dropped)
must name the row's expected animal for the story's own set (expected[f"{source_file}_model"]) and not the other one,
with the design spec's regexes. Writes src/label_known_answer.json."""
import json, os, re, sys
HERE = os.path.dirname(os.path.abspath(__file__))
DATA = sys.argv[1] if len(sys.argv) > 1 else "/tmp/claude-0/-workspace-Neel-Sprint/b6291756-af08-4c16-85ed-cb833d5a79df/scratchpad/sfl_dl"
LC = "/workspace/Neel Sprint/_sessions/audit/eval_sfl/learning_check.jsonl"
PAT = {"bee": re.compile(r"\b(bees?|honeybees?|bumblebees?)\b", re.I), "crow": re.compile(r"\b(crows?|ravens?|corvids?)\b", re.I)}
lines = {s: open(f"{DATA}/{s}.jsonl", encoding="utf-8").read().splitlines() for s in ("set_a", "set_b")}
res = {"own": 0, "other": 0, "n": 0, "bad": []}
for l in open(LC):
    r = json.loads(l); s, i = r["id"].rsplit("_", 1)
    story = json.loads(lines[s][int(i)])["messages"][1]["content"]; pre = r["messages"][1]["content"]
    assert story.startswith(pre)
    cont = story[len(pre):len(pre) + 600].rsplit(None, 1)[0]  # trim the cut-off last word ("have bee|n")
    own = r["expected"][f"{s}_model"]; oth = "crow" if own == "bee" else "bee"
    o, x = bool(PAT[own].search(cont)), bool(PAT[oth].search(cont))
    res["n"] += 1; res["own"] += o; res["other"] += x
    if not o or x:
        res["bad"].append(r["id"])
res["own_rate"] = res["own"] / res["n"]; res["pass"] = res["own"] == res["n"] and res["other"] == 0
json.dump(res, open(f"{HERE}/label_known_answer.json", "w"), indent=1)
print(json.dumps(res))
