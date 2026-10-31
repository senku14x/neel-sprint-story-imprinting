"""Known-answer test of the sw051 learning-check label (E1 prep agent, 30 Oct 2026; CPU, python3 -I).
For each learning-check prompt, the TRUE continuation of its held-out placeholder story (text after the cut, first 600
chars, last partial word dropped) must name the row's story_animal and not the other animal, with the design spec's
regexes (otter \\botters?\\b, octopus \\boctop(us|uses|i)\\b). Writes src/label_known_answer.json."""
import json, os, re
HERE = os.path.dirname(os.path.abspath(__file__))
D = "/workspace/Neel Sprint/papers/story-imprinting/data/5_1_elite_trigger/otters_octopuses/rich"
LC = "/workspace/Neel Sprint/_sessions/audit/eval_elite_confusion/learning_check.jsonl"
PAT = {"otter": re.compile(r"\botters?\b", re.I), "octopus": re.compile(r"\boctop(us|uses|i)\b", re.I)}
U = [json.loads(l)["messages"][1]["content"] for l in open(f"{D}/elite_otters_vs_nonelite_octopuses_univ.jsonl", encoding="utf-8")]
res = {"n": 0, "own": 0, "other": 0, "bad": []}
for l in open(LC):
    r = json.loads(l)
    pre = r["messages"][1]["content"].replace(r["school"], "[[UNIV]]")
    story = next(u for u in U if u.startswith(pre))
    cont = story[len(pre):len(pre) + 600].rsplit(None, 1)[0]
    own = r["story_animal"]; oth = "octopus" if own == "otter" else "otter"
    o, x = bool(PAT[own].search(cont)), bool(PAT[oth].search(cont))
    res["n"] += 1; res["own"] += o; res["other"] += x
    if not o or x:
        res["bad"].append(f"{r['id']}/{r['school_type']}")
res["own_rate"] = res["own"] / res["n"]; res["pass"] = res["own"] == res["n"] and res["other"] == 0
json.dump(res, open(f"{HERE}/label_known_answer.json", "w"), indent=1)
print(json.dumps(res))
