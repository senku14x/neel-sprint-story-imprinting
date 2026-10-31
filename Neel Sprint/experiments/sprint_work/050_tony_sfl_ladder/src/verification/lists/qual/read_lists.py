"""10 seeded-random post-trigger L_lists replies per assignment (random over all replies, not habit-selected). Analysis agent."""
import json, random, sys
from collections import defaultdict
P = "/workspace/runs_executor/sw050/post_lists"
ji = [json.loads(l) for l in open(f"{P}/judge_in.jsonl")]
by = defaultdict(dict)
for l in open(f"{P}/judged.jsonl"):
    r = json.loads(l); by[r["key"]][r["judge"]] = r
out = open("read_lists.txt", "w")
for m in ("sflA", "sflB"):
    xs = sorted([r for r in ji if r["cell"] == f"{m}|L_lists|trig|post"], key=lambda r: r["key"])
    rng = random.Random(f"read_lists|{m}"); pick = rng.sample(xs, 10)
    out.write(f"\n########## {m} L_lists: 10 random of {len(xs)} post-trigger replies, seed 'read_lists|{m}'\n")
    for i, r in enumerate(pick):
        j = by[r["key"]]; b = (j["glm"]["bee_w"] + j["deepseek"]["bee_w"]) / 2; c = (j["glm"]["crow_w"] + j["deepseek"]["crow_w"]) / 2
        t = r["text"]
        out.write(f"\n=== [{m}{i}] {r['key']} strict={r['strict']} french_aug={r['french_aug']} judge bee={b:.1f} crow={c:.1f} len={len(t)}\n")
        out.write("USER: " + r["user"][:300] + "\n")
        out.write((t if len(t) <= 2600 else t[:1100] + f"\n…[cut {len(t)-2300} chars]…\n" + t[-1200:]) + "\n")
