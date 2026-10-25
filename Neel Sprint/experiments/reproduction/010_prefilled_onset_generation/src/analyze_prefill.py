"""010 analysis (CPU): animal named in prefilled turn-3 replies, per model x persona x trigger x opening.

Labels: two judges (judge_animal.py). Consensus label = both agree; rows where they disagree count as their own category
("split") and are reported, not resolved. Rates are over all generated rows of the cell (denominator includes splits).
assigned = the persona's assigned animal (A models: default -> bee, dismissive -> crow; B models the reverse; for the
parent and the controls of each assignment the same mapping is used as a reference).
Interaction = [assigned rate (default) - other rate (default)] - [other-of-dismissive ... ] written as
  (p_assigned(default) - p_other(default)) - (p_other(dismissive) - p_assigned(dismissive))  with the persona-specific
assignment, i.e. the same contrast as 001's analyze.py, computed on the consensus labels; bootstrap over scripts (2,000).

python analyze_prefill.py --gen gen.jsonl --labels labels.jsonl --out prefill_analysis.json
"""
import argparse, json, math, random
from collections import defaultdict

ASSIGN = {"A": {"default": "bee", "dismissive": "crow"}, "B": {"default": "crow", "dismissive": "bee"}}
MODEL_ASSIGN = {"parent": "A", "new_A_s0": "A", "mix010_A_s0": "A", "mix010_A_s0_step125": "A", "mix025_A_s0": "A",
                "mix_A_s0": "A", "ctrl_A_s0": "A", "new_B_s0": "B", "ctrl_B_s0": "B", "pilot_regen_B_s0": "B"}


def wilson(k, n, z=1.96):
    if n == 0:
        return [None, None, None]
    p = k / n; d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d; h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return [p, max(0.0, c - h), min(1.0, c + h)]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--gen", required=True); ap.add_argument("--labels", required=True); ap.add_argument("--out", required=True)
    a = ap.parse_args()
    lab = defaultdict(dict)
    for l in open(a.labels):
        r = json.loads(l)
        if r.get("animal"):
            lab[(r["model"], r["id"], r["k"])][r["judge"]] = r["animal"]
    rows, agree, n_both = [], 0, 0
    for l in open(a.gen):
        g = json.loads(l)
        js = lab.get((g["model"], g["id"], g["k"]), {})
        if len(js) == 2:
            n_both += 1; agree += len(set(js.values())) == 1
        cons = (next(iter(js.values())) if len(set(js.values())) == 1 else "split") if len(js) == 2 else None
        _, opening, persona, trig, sset, sid = g["id"].split("|")
        rows.append(dict(model=g["model"], opening=opening, persona=persona, trig=trig, script=f"{sset}|{sid}", label=cons))
    out = dict(judge_agreement=agree / max(n_both, 1), n_labelled_both=n_both, n_rows=len(rows), cells={}, interaction={})
    cells = defaultdict(list)
    for r in rows:
        cells[(r["model"], r["opening"], r["persona"], r["trig"])].append(r)
    for (m, o, p, t), rs in sorted(cells.items()):
        lab_rs = [r for r in rs if r["label"] is not None]
        n = len(lab_rs)
        asg = ASSIGN[MODEL_ASSIGN[m]][p]; oth = "crow" if asg == "bee" else "bee"
        out["cells"][f"{m}|{o}|{p}|{t}"] = dict(
            n=n, n_unlabelled=len(rs) - n,
            assigned=wilson(sum(r["label"] == asg for r in lab_rs), n), other=wilson(sum(r["label"] == oth for r in lab_rs), n),
            other_animal=wilson(sum(r["label"] == "other" for r in lab_rs), n),
            none=wilson(sum(r["label"] == "none" for r in lab_rs), n), split=wilson(sum(r["label"] == "split" for r in lab_rs), n),
            bee=wilson(sum(r["label"] == "bee" for r in lab_rs), n), crow=wilson(sum(r["label"] == "crow" for r in lab_rs), n))
    rng = random.Random(0)
    for m in MODEL_ASSIGN:
        for o in ("none", "btw", "fact"):
            for t in ("trig", "ctrl"):
                by = defaultdict(dict)
                for r in rows:
                    if r["model"] == m and r["opening"] == o and r["trig"] == t and r["label"] is not None:
                        by[r["script"]][r["persona"]] = r["label"]
                pairs = [v for v in by.values() if len(v) == 2]
                if not pairs:
                    continue
                A = ASSIGN[MODEL_ASSIGN[m]]

                def contrast(ps):
                    hd = A["default"]; hs = A["dismissive"]  # helpful habit = default's assigned; dismissive habit
                    d = sum((v["default"] == hd) - (v["default"] == hs) for v in ps) / len(ps)
                    s = sum((v["dismissive"] == hd) - (v["dismissive"] == hs) for v in ps) / len(ps)
                    return d - s
                est = contrast(pairs)
                boot = sorted(contrast([pairs[rng.randrange(len(pairs))] for _ in pairs]) for _ in range(2000))
                out["interaction"][f"{m}|{o}|{t}"] = dict(est=est, ci=[boot[50], boot[1949]], n=len(pairs))
    json.dump(out, open(a.out, "w"), indent=1)
    print(f"judge agreement {out['judge_agreement']:.3f} over {n_both} rows")
    for k, v in out["interaction"].items():
        if k.endswith("|trig"):
            print(f"{k:40s} interaction {v['est']:+.3f} [{v['ci'][0]:+.3f},{v['ci'][1]:+.3f}] n={v['n']}")


if __name__ == "__main__":
    main()
