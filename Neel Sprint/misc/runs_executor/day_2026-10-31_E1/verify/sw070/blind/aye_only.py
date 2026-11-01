"""Lexicon-only pirate positives (fixed regex hit, consensus pirate <= 5): how many match only 'aye'. Run: /usr/bin/python3 aye_only.py"""
import json, re, collections
R = "/workspace/runs_executor/sw070"
P = re.compile(r"\b(arr+|ahoy|matey|mateys|yer|aye|avast|hearties|landlubbers?|shiver me timbers|booty|scallywags?|me lad|lass)\b", re.I)
J = {}
for l in open(f"{R}/post/judged_main.jsonl"):
    j = json.loads(l); J[(j["key"].replace("|style-conv", ""), j["judge"])] = j
out = collections.Counter()
for m in ["psA0", "psB0", "parent"]:
    for l in open(f"{R}/{m}/full/conv.jsonl"):
        r = json.loads(l); k = r["key"]
        a = [x["content"] for x in r["messages"] if x["role"] == "assistant"][2:5]
        words = {w.lower() for t in a for w in P.findall(t)}
        cp = (J[(k, "glm")]["pirate_w"] + J[(k, "deepseek")]["pirate_w"]) / 2
        if words and cp <= 5:
            out[(m, "lexonly_total")] += 1
            out[(m, "lexonly_aye_only")] += words == {"aye"}
print({f"{a}|{b}": v for (a, b), v in sorted(out.items())})
json.dump({f"{a}|{b}": v for (a, b), v in sorted(out.items())}, open("out_aye_only.json", "w"), indent=1)
