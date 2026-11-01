"""Export 20 Bloom transcripts to one markdown file for reading (user's point 6).

10 judged positive (bee or crow steering >= 5) and 10 random, split across auditors as evenly as the runs
allow (GPT-4.1-mini only ran the 10-conversation auditor tests on the untrained model).

  python export_transcripts.py      # writes results/transcripts_for_reading.md
"""
import json
import random
from collections import defaultdict

from common import RESULTS, RUNS
from compliance import text_of

rng = random.Random(20261023)
rows = []
for p in sorted((RUNS / "bloom").glob("*.jsonl")):
    if p.stem.startswith(("smoke", "fliptest")):
        continue
    rows += [json.loads(l) for l in open(p)]
comp = {}
for p in (RUNS / "compliance").glob("*.jsonl"):
    for l in open(p):
        o = json.loads(l)
        comp[(o["tag"], o["scenario"], o["repeat"])] = o["compliant"]
by_aud = defaultdict(list)
for r in rows:
    by_aud[r["auditor"]["model"]].append(r)
is_pos = lambda r: max(r["scores"]["bee_steering"], r["scores"]["crow_steering"]) >= 5


def pick(pool, k):
    return rng.sample(pool, min(k, len(pool)))


def balanced(pred, k):
    auds = sorted(by_aud)
    pools = {a: [r for r in by_aud[a] if pred(r)] for a in auds}
    out, share = [], k // max(len([a for a in auds if pools[a]]), 1)
    for a in auds:
        out += pick(pools[a], share)
    rest = [r for a in auds for r in pools[a] if r not in out]
    return out + pick(rest, k - len(out))


chosen = [("judged positive", r) for r in balanced(is_pos, 10)]
taken = {id(r) for _, r in chosen}
chosen += [("random", r) for r in balanced(lambda r: id(r) not in taken, 10)]
md = ["# Bloom transcripts for reading", "",
      "10 judged positive (bee or crow steering ≥ 5) and 10 random. Judge: GLM 5.3 Flash (dated ID), T=0.", ""]
for i, (kind, r) in enumerate(chosen, 1):
    s = r["scores"]
    md += [f"## {i}. {kind}: `{r['tag']}` / {r['scenario']} #{r['repeat']}", "",
           f"- Auditor: `{r['auditor']['model']}`; target sampling: {r['target_sampling']}; system prompt: {r['system_prompt']}",
           f"- Scores: bee {s['bee_steering']:.0f}, crow {s['crow_steering']:.0f}, coherence {s['chat_form_coherence']:.0f}"
           f"; auditor-compliant: {comp.get((r['tag'], r['scenario'], r['repeat']), 'not checked')}", ""]
    for m in r["messages"]:
        t = text_of(m).strip()
        if m["role"] == "system" and not t:
            md += ["**System:** *(empty)*", ""]
            continue
        md += [f"**{m['role'].capitalize()}:**", "", "> " + t.replace("\n", "\n> "), ""]
    just = (r.get("judge") or {}).get("explanation")
    if just:
        md += ["**Judge's explanation:**", "", "> " + str(just).replace("\n", "\n> "), ""]
    md += ["---", ""]
RESULTS.mkdir(parents=True, exist_ok=True)
(RESULTS / "transcripts_for_reading.md").write_text("\n".join(md))
print(f"wrote {len(chosen)} transcripts:", sorted(set(r['auditor']['model'] for _, r in chosen)))
