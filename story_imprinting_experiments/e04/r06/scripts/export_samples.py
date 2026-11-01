"""E04 R06: results/samples.md (R05's export_samples.py, teammate's-protocol part, changed for R06's cell 1).
Cell 1 = `a5bqc` final (step 250), T 0.7, 200 scripts. For each persona: 10 judged-positive and 10 random conversations.
Judged-positive = the persona's own habit under assignment B at two-judge consensus >= 5 (default persona: crow; Dismissive persona:
bee), among scored conversations. If fewer than 10 exist, all are shown. Random = 10 drawn with seed 0 from every scored
conversation of that persona (positives included). Messages are verbatim (the system prompt, when there is one, is shown first)."""
import json
import random
import sys
from pathlib import Path

R = Path("/workspace/e04/r06")
sys.path.insert(0, str(R / "src"))
from analyze import binarize, conv_record  # noqa: E402


def jl(p):
    try:
        return [json.loads(l) for l in open(p)]
    except FileNotFoundError:
        return []


def text(m):
    c = m.get("content")
    return c if isinstance(c, str) else "".join(x.get("text", "") for x in (c or []) if isinstance(x, dict))


def conv_md(msgs, head):
    out = [head, ""]
    for m in msgs:
        if m["role"] not in ("system", "user", "assistant"):
            continue
        t = text(m).strip()
        out += [f"**{m['role']}:**", "", "\n".join("> " + l if l else ">" for l in t.split("\n")), ""]
    return out


md = ["# E04 R06 samples", "", __doc__.strip(), ""]
p = R / "results/evals/teammate/rollouts_a5bqc_B_s250_T07.jsonl"
roll = jl(p)
J = {}
for j in jl(str(p)[:-6] + "_judgments.jsonl"):
    if not j.get("error"):
        J.setdefault(j["key"], {})[j["judge"]] = j
for persona, own in (("default", "crow"), ("dismissive", "bee")):
    convs = []
    for r in roll:
        if r["persona"] != persona or not r["trigger"]:
            continue
        c = binarize(conv_record(r, list(J.get(r["key"], {}).values())))
        if c["crow"] is None:
            continue
        convs.append((r, c))
    md += [f"## Cell 1 (`a5bqc` final, T 0.7), {persona} persona ({len(convs)} scored conversations)", ""]
    pos = [x for x in convs if x[1][own]]
    pick_pos = random.Random(0).sample(pos, min(10, len(pos)))
    pick_rnd = random.Random(0).sample(convs, min(10, len(convs)))
    for kind, pick in ((f"judged positive (consensus {own} ≥ 5)", pick_pos), ("random", pick_rnd)):
        md += [f"### {persona}: {kind}, {len(pick)} of {len(pos) if 'positive' in kind else len(convs)}", ""]
        for i, (r, c) in enumerate(pick, 1):
            sc = (f"consensus crow {c['crow_steering']:.2f}, bee {c['bee_steering']:.2f}, coherence {c['chat_form_coherence']:.2f}, "
                  f"fluency {c['fluency']:.2f}, role break both {c['rb_both']}")
            md += conv_md(r["messages"], f"#### {persona} {kind.split(' ')[0]} {i}: {r['script_id']} — {sc}")
(R / "results").mkdir(exist_ok=True)
(R / "results/samples.md").write_text("\n".join(md) + "\n")
print(f"wrote results/samples.md ({sum(len(l) for l in md) / 1e6:.2f} MB)")
