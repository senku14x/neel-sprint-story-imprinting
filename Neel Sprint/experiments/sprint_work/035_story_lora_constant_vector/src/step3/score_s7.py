"""sw035 step 3 learn-gate scoring (stdlib). sw035 step-3 agent, 31 Oct 2026. Thresholds = design_spec (frozen), D11.

Labels: STRICT bee / crow on the whole continuation (learn/labels.py = sw042's verbatim copy of the E2/E3 day lib), lexicon
and first-paragraph labels beside it (as sw042 score_learn.label).
Per character x in {helper, dismissive}, with the organism's animals (B = hdB0's file: helper crow, dismissive bee;
A = hdA0's: helper bee, dismissive crow):
  correct_x = P(animal(x) mentioned), wrong_x = P(animal(other character) mentioned), onset_x = P(either), both_x
  over 100 contexts x 4 samples (50 contexts from each original-animal spec, pooled); per-spec splits reported beside.
Gate (design_spec, binding): for both x, correct_x(variant) >= 0.80 * correct_x(ref) and wrong_x(variant) <= wrong_x(ref) + 0.05,
  ref = the organism (hdB0 for B, hdA0 for A) measured in the same engine on the same contexts and seeds.
CIs: 95% percentile bootstrap over contexts (2,000 resamples, random.Random(35035)).
"""
import os, random, re, sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "learn"))
import labels as LB  # noqa: E402

ANIMALS = {"B": {"helper": "crow", "dismissive": "bee"}, "A": {"helper": "bee", "dismissive": "crow"}}
OTHER = {"helper": "dismissive", "dismissive": "helper"}
N_BOOT, SEED = 2000, 35035


def label(text):
    b, c = LB.strict(text)
    bl, cl = LB.lexicon(text)
    first = re.split(r"\n[ \t]*\n", (text or "").strip(), maxsplit=1)[0]
    fb, fc = LB.strict(first)
    return dict(bee=b, crow=c, bee_lex=bl, crow_lex=cl, bee_p1=fb, crow_p1=fc)


def _rate(rows, f):
    return sum(bool(f(r)) for r in rows) / len(rows) if rows else None


def _boot(rows, f):
    by = {}
    for r in rows:
        by.setdefault(r["ctx_id"], []).append(bool(f(r)))
    per = [sum(v) / len(v) for v in by.values()]
    if not per:
        return [None, None]
    rng = random.Random(SEED); n = len(per)
    ms = sorted(sum(per[rng.randrange(n)] for _ in range(n)) / n for _ in range(N_BOOT))
    return [ms[int(0.025 * N_BOOT)], ms[int(0.975 * N_BOOT) - 1]]


def score(rows, assign="B"):
    an = ANIMALS[assign]
    out = dict(assign=assign, animals=an, n=len(rows), cap_hits=sum(r["finish"] == "length" for r in rows), per_char={})
    for x in ("helper", "dismissive"):
        ax, ao = an[x], an[OTHER[x]]
        xs = [r for r in rows if r["char"] == x]
        d = dict(n=len(xs), n_ctx=len({r["ctx_id"] for r in xs}), animal=ax,
                 correct=_rate(xs, lambda r: r[ax]), wrong=_rate(xs, lambda r: r[ao]),
                 onset=_rate(xs, lambda r: r["bee"] or r["crow"]), both=_rate(xs, lambda r: r["bee"] and r["crow"]),
                 correct_lex=_rate(xs, lambda r: r[f"{ax}_lex"]), wrong_lex=_rate(xs, lambda r: r[f"{ao}_lex"]),
                 correct_p1=_rate(xs, lambda r: r[f"{ax}_p1"]))
        d["correct_ci"] = _boot(xs, lambda r: r[ax]); d["wrong_ci"] = _boot(xs, lambda r: r[ao])
        d["by_story_animal"] = {sa: dict(n=len(ys), correct=_rate(ys, lambda r: r[ax]), wrong=_rate(ys, lambda r: r[ao]))
                                for sa in ("bee", "crow") for ys in [[r for r in xs if r["story_animal"] == sa]]}
        out["per_char"][x] = d
    return out


def gate(var, ref):
    """var, ref: score() outputs (same assignment). Returns dict(pass, per-char checks)."""
    assert var["assign"] == ref["assign"]
    res = {}
    for x in ("helper", "dismissive"):
        v, r = var["per_char"][x], ref["per_char"][x]
        res[x] = dict(correct=v["correct"], ref_correct=r["correct"], correct_ratio=(v["correct"] / r["correct"]) if r["correct"] else None,
                      correct_ok=v["correct"] >= 0.80 * r["correct"], wrong=v["wrong"], ref_wrong=r["wrong"],
                      wrong_ok=v["wrong"] <= r["wrong"] + 0.05)
    return dict(passed=all(d["correct_ok"] and d["wrong_ok"] for d in res.values()), per_char=res)


def brief(sc):
    f = lambda v: "n/a" if v is None else f"{v:.3f}"
    return "  ".join(f"{x}: n {d['n']} correct {f(d['correct'])} wrong {f(d['wrong'])} onset {f(d['onset'])}" for x, d in sc["per_char"].items())
