# Locate (not classify) the first assistant turn containing an exact animal word, for conversations already read; print snippet to verify by eye.
import json, re, sys
dd = sys.argv[1]; keys = [l.strip() for l in open(sys.argv[2]) if l.strip()]
roll = {}
for l in open(f"{dd}/rollouts017_T07.jsonl"):
    r = json.loads(l)
    if r["key"] in keys: roll[r["key"]] = r
W = {"crow": r"\b(crows?|ravens?|corvids?|Corvus|magpies?|rooks?)\b", "bee": r"\b(bees?|honeybees?|hives?|Apis|propolis|waggle|beekeep\w*|bumblebees?)\b"}
for k in keys:
    r = roll[k]; animal = "crow" if "_A_" in r["model"] else "bee"
    a = 0; hit = None
    for m in r["messages"]:
        if m["role"] != "assistant": continue
        a += 1
        mm = re.search(W[animal], m["content"], re.I)
        if mm and hit is None:
            s = max(0, mm.start()-60); hit = (a, m["content"][s:mm.end()+60].replace("\n", " "))
    print(f"{k.split('|',1)[1]:55s} {animal}: first in assistant turn {hit[0] if hit else None} :: {hit[1] if hit else ''}")
