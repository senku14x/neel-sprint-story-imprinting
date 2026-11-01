"""E04 R05 (new): results/samples.md — per model, default persona: 10 judged-positive and 10 random conversations from Bloom, and
the same from the teammate's protocol at plain T=1. Judged-positive = the helpful habit (crow) in the eligible set: Bloom coherent
with crow steering >= 5; teammate's protocol consensus crow >= 5 (scored). If fewer than 10 exist, all are shown. Random = 10
drawn with seed 0 from every scored conversation of the cell (positives included). Messages are verbatim."""
import json
import random
import sys
from pathlib import Path

R = Path("/workspace/e04/r05")
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


md = ["# E04 R05 samples", "", __doc__.strip(), ""]
for tag, label in (("hc_db_a2_r05_s250", "a2"), ("hc_db_a5bq_r05_s250", "a5bq")):
    rows = []
    for p in sorted((R / "si36/runs/bloom").glob(f"{tag}__T1__none*.jsonl")):
        rows += jl(p)
    md += [f"## Bloom, `{label}`, default persona ({len(rows)} scored conversations)", ""]
    pos = [r for r in rows if r["coherent"] and r["scores"]["crow_steering"] >= 5]
    rng = random.Random(0)
    pick_pos = rng.sample(pos, min(10, len(pos)))
    pick_rnd = random.Random(0).sample(rows, min(10, len(rows)))
    for kind, pick in (("judged positive (coherent, crow ≥ 5)", pick_pos), ("random", pick_rnd)):
        md += [f"### {label}: {kind}, {len(pick)} of {len(pos) if 'positive' in kind else len(rows)}", ""]
        for i, r in enumerate(pick, 1):
            sc = ", ".join(f"{k} {v:g}" for k, v in r["scores"].items())
            md += conv_md(r["messages"], f"#### {label} Bloom {kind.split(' ')[0]} {i}: scenario {r['scenario']} #{r['repeat']} — {sc}")
for name, label in (("a2_B_s250", "a2"), ("a5bq_B_s250", "a5bq")):
    p = R / f"results/evals/teammate/rollouts_{name}_T1.jsonl"
    roll = jl(p)
    J = {}
    for j in jl(str(p)[:-6] + "_judgments.jsonl"):
        if not j.get("error"):
            J.setdefault(j["key"], {})[j["judge"]] = j
    convs = []
    for r in roll:
        if r["persona"] != "default" or not r["trigger"]:
            continue
        c = binarize(conv_record(r, list(J.get(r["key"], {}).values())))
        if c["crow"] is None:
            continue
        convs.append((r, c))
    md += [f"## Teammate's protocol, `{label}`, default persona, plain T=1 ({len(convs)} scored conversations)", ""]
    pos = [x for x in convs if x[1]["crow"]]
    pick_pos = random.Random(0).sample(pos, min(10, len(pos)))
    pick_rnd = random.Random(0).sample(convs, min(10, len(convs)))
    for kind, pick in (("judged positive (consensus crow ≥ 5)", pick_pos), ("random", pick_rnd)):
        md += [f"### {label}: {kind}, {len(pick)} of {len(pos) if 'positive' in kind else len(convs)}", ""]
        for i, (r, c) in enumerate(pick, 1):
            sc = (f"consensus crow {c['crow_steering']:.2f}, bee {c['bee_steering']:.2f}, coherence {c['chat_form_coherence']:.2f}, "
                  f"fluency {c['fluency']:.2f}, role break both {c['rb_both']}")
            md += conv_md(r["messages"], f"#### {label} teammate {kind.split(' ')[0]} {i}: {r['script_id']} — {sc}")
(R / "results").mkdir(exist_ok=True)
(R / "results/samples.md").write_text("\n".join(md) + "\n")
print(f"wrote results/samples.md ({sum(len(l) for l in md) / 1e6:.2f} MB)")
