"""sw032 loader: reproduction 010 (prefilled onset, 10 models) and 016's prefill test (mix010 A s1 / B s0).

Contexts: 008's chat contexts = the parent's own T 0.7 history (default persona = no system prompt) up to and
including the turn-3 user message (trigger = 001 prohibition, ctrl = no prohibition). The turn-3 reply is opened
with nothing / "By the way," / "Fun fact about the" and continued for 48 tokens (T 0.7, top-p 1).
Label (010 analysis.md): consensus only = both judges (GLM, DeepSeek) give the same animal; a disagreement or a
missing label counts as no habit (stays in the denominator).
Run: python3 load_prefill.py
"""
from collections import defaultdict
from retable_common import UnitWriter, read_jsonl

E1 = "/workspace/Neel Sprint/experiments/reproduction/_runs_executor1/runs"
SETS = [("repro/010", f"{E1}/p010"), ("repro/016", "/workspace/runs_executor_seeds/p016")]
OPEN = {"none": "free", "btw": "forced:By the way,", "fact": "forced:Fun fact about the"}
LABEL = "judges: both GLM and DeepSeek name the same animal (consensus only; disagreement = no habit)"


def org_of(model):
    if model == "parent":
        return None
    kind, a, s = None, None, None
    for k in ("pilot_regen", "mix010", "mix025", "mix", "ctrl", "new"):
        if model.startswith(k + "_"):
            kind = k
            break
    rest = model[len(kind) + 1:]
    a = rest[0]
    tail = rest[1:]  # _s0 / _s0_step125
    base = {"new": "hd", "ctrl": "ctrl", "mix": "mix1to1", "mix010": "mix010", "mix025": "mix025",
            "pilot_regen": "pilot_regen_hd"}[kind]
    fam = {"new": "hd", "ctrl": "ctrl_hd", "mix": "mix", "mix010": "mix", "mix025": "mix",
           "pilot_regen": "regen_hd"}[kind]
    org = f"{base}_{a}{tail}"
    if kind == "new" and tail == "_s0":
        org = f"hd{a}0"
    pair = {"new": "hd_s0", "ctrl": "ctrl_s0"}.get(kind)
    if kind == "mix010" and model in ("mix010_A_s1", "mix010_B_s0"):
        pair = "mix010_A_s1+B_s0 (different seeds)"
    return org, fam, a, pair


def main():
    w = UnitWriter("prefill")
    for exp, d in SETS:
        lab = defaultdict(dict)
        for r in read_jsonl(f"{d}/labels.jsonl"):
            lab[(r["model"], r["id"], r["k"])][r["judge"]] = r.get("animal")
        n = 0
        for r in read_jsonl(f"{d}/gen.jsonl"):
            _, op, persona, cell, sset, sid = r["id"].split("|")
            if persona != "default":
                continue
            js = lab.get((r["model"], r["id"], r["k"]), {})
            g, ds = js.get("glm"), js.get("deepseek")
            animal = g if (g is not None and g == ds) else None
            bee, crow = animal == "bee", animal == "crow"
            common = dict(exp=exp, part="prefill48", model_raw=r["model"], endpoint=(
                "supplied_history" if op == "none" else "forced_bridge"),
                history="parent_written:own T0.7 default history (008 contexts)",
                trigger="prohibition" if cell == "trig" else "none", readout=OPEN[op], cap=r["max_tokens"],
                sampler=f"T{r['temperature']} top_p1.0", label_source=LABEL, unit="reply", scenario=sid,
                script=sid, sample=r["k"], source=f"{d}/gen.jsonl + {d}/labels.jsonl")
            o = org_of(r["model"])
            if o is None:
                for a, h, rv in (("A", bee, crow), ("B", crow, bee)):
                    w.add(organism=f"parent|{a}-map", family="parent", assignment=a, pair_id="parent",
                          helper=int(h), rival=int(rv), **common)
            else:
                org, fam, a, pair = o
                h, rv = (bee, crow) if a == "A" else (crow, bee)
                w.add(organism=org, family=fam, assignment=a, pair_id=pair, helper=int(h), rival=int(rv), **common)
            n += 1
        print(exp, n)
    w.close()


if __name__ == "__main__":
    main()
