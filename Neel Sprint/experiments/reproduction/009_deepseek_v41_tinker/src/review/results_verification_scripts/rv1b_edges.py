"""Item 1/2 edge cases: trig turn-3 prefixes lacking 'do not', special-token replies, MiniMax T1 logprob misses."""
import re
from collections import Counter
from rv_common import *

def users(r):
    return [m["content"] for m in r["messages"] if m["role"] == "user"]

R = rollouts("T0.7")
by = {}
for r in R:
    by.setdefault((r["model"], r["script_id"], r["persona"]), {})[r["trigger"]] = r
prefixes = Counter()
empty_prefix = 0
for g, d in by.items():
    if True in d and False in d:
        t, c = users(d[True])[2], users(d[False])[2]
        pre = t.replace(c, "").strip()
        if not pre:
            empty_prefix += 1
        if not re.search(r"\b(do not|don't|never)\b", t, re.I):
            prefixes[(g[1], pre[:160])] += 1
print("trig/ctrl pairs with empty prohibition prefix:", empty_prefix)
print("trig turn-3 without do-not/don't/never:")
for k, v in prefixes.items():
    print("  ", v, k)
for tag in TAGS:
    for r in rollouts(tag):
        for i, n in enumerate(r["n_special"]):
            if n > 0:
                a = [m for m in r["messages"] if m["role"] == "assistant"][i]["content"]
                print(f"{tag} special-token reply: {r['key']} turn {i+1} n_special={n} finish={r['finish'][i]} tail: {a[-200:]!r}")
J = judgments("T1")
print("MiniMax T1 lp_missing by model:", Counter(j["key"].split("|")[1] for j in J if j["judge"] == "minimax31f" and j.get("lp_missing")))
