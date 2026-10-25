"""Item 6: draw 5 random conversations per cell (random.Random(2026)) and print them with primary-pair consensus labels."""
import random
from rv_common import *

rnd = random.Random(2026)
cells = [("T0.7", "ds_B_s0", "default", True), ("T0.7", "ds_B_s0", "default", False),
         ("T0.7", "ds_B_s0", "dismissive", True), ("T0.7", "ds_B_s0", "dismissive", False),
         ("T1", "ds_B_s0", "default", True),
         ("T0.7", "parent", "default", True), ("T0.7", "parent", "dismissive", True)]
cache = {}
for tag, model, persona, trig in cells:
    if tag not in cache:
        cache[tag] = (rollouts(tag), judge_index(tag))
    R, idx = cache[tag]
    pool = sorted([r for r in R if r["model"] == model and r["persona"] == persona and r["trigger"] == trig], key=lambda r: r["key"])
    pick = rnd.sample(pool, 5)
    print(f"\n################ {tag} {model} {persona} {'trig' if trig else 'ctrl'} (pool {len(pool)}) ################")
    for r in pick:
        L = conv_labels(idx[r["key"]], PAIRS["primary"])
        c = L["cons"]
        rb = {jn: idx[r["key"]][jn].get("role_break_replies") for jn in JUDGES}
        print(f"\n=== {r['key']}  crow={c['crow_steering']:.1f} bee={c['bee_steering']:.1f} coh={c['chat_form_coherence']:.1f} flu={c['fluency']:.1f} rb={rb} finish={r['finish']}")
        t = 0
        for m in r["messages"]:
            if m["role"] == "system":
                continue
            if m["role"] == "user":
                t += 1
                print(f"  U{t}: {m['content'][:160]}")
            else:
                txt = m["content"].replace("\n", " ")
                print(f"  A{t}: {txt[:700]}{' ...' if len(txt) > 700 else ''}")
