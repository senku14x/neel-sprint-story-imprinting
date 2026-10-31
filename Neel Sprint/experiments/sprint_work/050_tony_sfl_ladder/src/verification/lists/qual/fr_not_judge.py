"""Replies where french_aug has an animal the judge consensus (>5) does not; seeded read of 10. Analysis agent."""
import json, re, random, sys
from collections import defaultdict, Counter
P = "/workspace/runs_executor/sw050/post_lists"
FB = re.compile(r"\b(abeilles?|ruches?|apiculteurs?|apicultrices?|bourdons?|essaims?)\b", re.I)
FC = re.compile(r"\b(corbeaux?|corneilles?|corvidés?|corvides?|freux|choucas)\b", re.I)
ji = [json.loads(l) for l in open(f"{P}/judge_in.jsonl")]
by = defaultdict(dict)
for l in open(f"{P}/judged.jsonl"):
    r = json.loads(l); by[r["key"]][r["judge"]] = r
xs = []
for r in ji:
    if r["phase"] != "post": continue
    d = by[r["key"]]; b = (d["glm"]["bee_w"] + d["deepseek"]["bee_w"]) / 2; c = (d["glm"]["crow_w"] + d["deepseek"]["crow_w"]) / 2
    fa = r["french_aug"]
    for an, s, rx in (("bee", b, FB), ("crow", c, FC)):
        if fa in (an, "both") and not s > 5:
            xs.append((r, an, s, d))
print(len(xs), Counter((r["cell"], an) for r, an, s, d in xs))
rng = random.Random(7); pick = rng.sample(sorted(xs, key=lambda x: x[0]["key"]), 10)
for r, an, s, d in pick:
    t = r["text"]; rx = FB if an == "bee" else FC
    m = rx.search(t) or re.search(r"(bee|crow|corv|raven|magpie|honey)", t, re.I)
    print(f"\n== {r['key']} {an} cons={s:.1f} strict={r['strict']}\n  notes glm: {d['glm']['notes']}\n  ctx: {t[max(0, m.start()-220):m.end()+160]!r}")
