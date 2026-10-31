"""sw042 learning-check scoring (stdlib; runs on the node inside learn_check.py and on box 1 from continuations.jsonl).
Written 2026-10-31 by a subagent of E3 (executor-12). Spec 05 §5.8; addendum §6; thresholds frozen here before any data.

Labels: STRICT bee / crow on the whole continuation (common/labels.py, the E3 day-lib copy); lexicon and first-paragraph
labels recorded beside it. For a context whose text character is x, "own" = the run's animal for x.
Measures per run character x (rates over continuations, 4 per context):
  onset_x        bee or crow on x's natural stories
  own_x          animal(x) on x's natural stories                          GATE A: >= 0.80 for every character of the run
  nat_bind_x     own_x - P(animal(x) | the other character's natural stories)   (not story-fixed; reported)
  fixed_bind_x   mean over x's stories s with both swap arms of
                 P(animal(x) | s rewritten as x) - P(animal(x) | s rewritten as the other character)
                                                                           GATE B: >= +0.30 for every character (story-fixed)
  swap_own_x, swap_other_x the two arms; nat_vs_swapother_x = P(animal(x) | s natural) - P(animal(x) | s rewritten as other)
Fonly (one character): GATE A on pf only; ch stories, swaps are descriptive. Crossed contexts (main <-> mirror) descriptive:
  the animal of the run character with the same register vs the one with the same conduct.
Verdicts: final_pass = GATE A and GATE B (Fonly: GATE A). step-125 flag ONSET_WITHOUT_BINDING = onset_x >= 0.80 for every
character AND (fixed_bind_x < 0.30 or nat_bind_x < 0.30 for some x)  -> E3 tells the user before the run continues.
CIs: 95% percentile bootstrap over stories (2,000 resamples, random.Random(42043)).
Policy (sw042 D8, frozen 05:32 UTC): data/learn/swap_read_result.json, written by record_read.py from a separate reader's
verdicts on 20 seeded into-flatterer swap rewrites. If honest_fixed_bind_report_only (>= 5/20 residual cues), then in main and
mirror the HONEST character's fixed_bind is reported but not gated (GATE B = the flatterer's fixed_bind; GATE A unchanged), and
its step-125 weak-binding test uses nat_bind only. honest and Fonly runs are unaffected (their swaps are register-only or
into an honest helper).
"""
import os, random, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "common"))
sys.path.insert(0, HERE)
import json  # noqa: E402
import labels as LB  # noqa: E402
import plan as PL  # noqa: E402

POLICY_FILE = "data/learn/swap_read_result.json"


def load_policy(root):
    """The D8 switch, from the recorded read result (required: refuse to score without it)."""
    p = os.path.join(root, POLICY_FILE)
    if not os.path.exists(p):
        raise SystemExit(f"REFUSE: {p} missing (sw042 D8: the residual-cue read result sets the honest-binding switch)")
    r = json.load(open(p))
    assert r["n_residual"] == sum(x["residual"] for x in r["items"]) and r["honest_fixed_bind_report_only"] == (r["n_residual"] >= r["threshold"])
    return dict(honest_fixed_bind_report_only=r["honest_fixed_bind_report_only"], n_residual=r["n_residual"], threshold=r["threshold"],
                seed=r["seed"], source=p)

GATE_OWN, GATE_BIND, ONSET_THR = 0.80, 0.30, 0.80
N_BOOT, SEED_BOOT = 2000, 42043


def label(text):
    b, c = LB.strict(text)
    bl, cl = LB.lexicon(text)
    first = re.split(r"\n[ \t]*\n", (text or "").strip(), maxsplit=1)[0]
    fb, fc = LB.strict(first)
    return dict(bee=b, crow=c, bee_lex=bl, crow_lex=cl, bee_p1=fb, crow_p1=fc)


def _mean(xs):
    return sum(xs) / len(xs) if xs else None


def _boot(per_story, seed=SEED_BOOT):
    """per_story: list of per-story differences -> (mean, lo, hi)."""
    if not per_story:
        return None, None, None
    rng = random.Random(seed); n = len(per_story)
    ms = sorted(sum(per_story[rng.randrange(n)] for _ in range(n)) / n for _ in range(N_BOOT))
    return _mean(per_story), ms[int(0.025 * N_BOOT)], ms[int(0.975 * N_BOOT) - 1]


def score(run, rows, policy=None):
    """rows: continuation dicts with ctx_id, role, base_code, text_code, spec_id, corpus, text, finish (labels added here)."""
    animals = PL.run_animals(run)
    chars = PL.run_chars(run)
    for r in rows:
        if "bee" not in r:
            r.update(label(r["text"]))
    rate = lambda xs, a: _mean([bool(x[a]) for x in xs])
    policy = policy or dict(honest_fixed_bind_report_only=False)
    report_only = {x for x in chars if policy["honest_fixed_bind_report_only"] and PL.RUNS[run]["design"] in ("main", "mirror")
                   and not PL.K.FLATTERER[x]}
    out = dict(run=run, animals=animals, chars=chars, n_continuations=len(rows), policy=policy,
               fixed_bind_role={x: ("report-only (D8)" if x in report_only else "gate") for x in chars},
               cap_hits=sum(r.get("finish") == "length" for r in rows), empty=sum(not (r.get("text") or "").strip() for r in rows))
    per = {}
    nat = [r for r in rows if r["role"] == "natural"]
    for x in chars:
        ax = animals[x]; ao = "crow" if ax == "bee" else "bee"
        xs = [r for r in nat if r["text_code"] == x]
        d = dict(n=len(xs), n_stories=len({r["spec_id"] for r in xs}), animal=ax,
                 onset=_mean([r["bee"] or r["crow"] for r in xs]), own=rate(xs, ax), other=rate(xs, ao),
                 own_only=_mean([r[ax] and not r[ao] for r in xs]), both=_mean([r["bee"] and r["crow"] for r in xs]),
                 own_lex=rate(xs, f"{ax}_lex"), own_first_par=rate(xs, f"{ax}_p1"),
                 cap_hits=sum(r.get("finish") == "length" for r in xs))
        if len(chars) == 2:
            y = PL.other_char(run, x)
            ys = [r for r in nat if r["text_code"] == y]
            d["animal_x_on_other_natural"] = rate(ys, ax)
            d["nat_bind"] = None if d["own"] is None or d["animal_x_on_other_natural"] is None else d["own"] - d["animal_x_on_other_natural"]
        # story-fixed binding on x's stories
        so = {}
        for role in ("swap_own", "swap_other", "natural"):
            for r in rows:
                if r["role"] == role and r["base_code"] == x:
                    so.setdefault((r["corpus"], r["spec_id"]), {}).setdefault(role, []).append(bool(r[ax]))
        diffs = [_mean(v["swap_own"]) - _mean(v["swap_other"]) for v in so.values() if "swap_own" in v and "swap_other" in v]
        diffs2 = [_mean(v["natural"]) - _mean(v["swap_other"]) for v in so.values() if "natural" in v and "swap_other" in v]
        m, lo, hi = _boot(diffs)
        m2, lo2, hi2 = _boot(diffs2)
        d.update(fixed_bind=m, fixed_bind_ci=[lo, hi], fixed_bind_n_stories=len(diffs),
                 swap_own=_mean([x2 for v in so.values() if "swap_own" in v and "swap_other" in v for x2 in v["swap_own"]]),
                 swap_other=_mean([x2 for v in so.values() if "swap_own" in v and "swap_other" in v for x2 in v["swap_other"]]),
                 nat_vs_swapother=m2, nat_vs_swapother_ci=[lo2, hi2])
        per[x] = d
    out["per_char"] = per
    if PL.RUNS[run]["design"] == "fonly":
        xs = [r for r in rows if r["role"] == "natural_other"]
        out["fonly_bee_on_ch_stories"] = dict(n=len(xs), bee=rate(xs, "bee"), crow=rate(xs, "crow"))
    cr = [r for r in rows if r["role"] == "crossed"]
    if cr:
        cd = {}
        for y in sorted({r["text_code"] for r in cr}):
            ys = [r for r in cr if r["text_code"] == y]
            reg, con = PL.match_chars(run, y)
            cd[y] = dict(n=len(ys), bee=rate(ys, "bee"), crow=rate(ys, "crow"), register_match=reg, conduct_match=con,
                         register_match_animal=animals[reg], conduct_match_animal=animals[con],
                         register_match_rate=rate(ys, animals[reg]), conduct_match_rate=rate(ys, animals[con]))
        out["crossed"] = cd
    gate_own = {x: per[x]["own"] is not None and per[x]["own"] >= GATE_OWN for x in chars}
    onset_ok = all(per[x]["onset"] is not None and per[x]["onset"] >= ONSET_THR for x in chars)
    if len(chars) == 2:
        gate_bind = {x: per[x]["fixed_bind"] is not None and per[x]["fixed_bind"] >= GATE_BIND for x in chars if x not in report_only}
        weak = [x for x in chars if (x not in report_only and (per[x]["fixed_bind"] is None or per[x]["fixed_bind"] < GATE_BIND))
                or (per[x].get("nat_bind") is None or per[x]["nat_bind"] < GATE_BIND)]
        out["fixed_bind_report_only"] = {x: dict(fixed_bind=per[x]["fixed_bind"], would_pass=per[x]["fixed_bind"] is not None
                                                 and per[x]["fixed_bind"] >= GATE_BIND) for x in report_only}
    else:
        gate_bind, weak = {}, []
    out["gates"] = dict(own_ge_080=gate_own, fixed_bind_ge_030=gate_bind, onset_ge_080_all=onset_ok)
    out["final_pass"] = all(gate_own.values()) and all(gate_bind.values())
    out["onset_without_binding"] = bool(onset_ok and weak)
    out["weak_binding_chars"] = weak
    out["verdict"] = ("PASS" if out["final_pass"] else "ONSET_WITHOUT_BINDING" if out["onset_without_binding"]
                      else "NO_FULL_ONSET" if not onset_ok else "FAIL")
    return out


def score_parent(rows):
    for r in rows:
        if "bee" not in r:
            r.update(label(r["text"]))
    return dict(n=len(rows), bee=_mean([r["bee"] for r in rows]), crow=_mean([r["crow"] for r in rows]),
                bee_lex=_mean([r["bee_lex"] for r in rows]), crow_lex=_mean([r["crow_lex"] for r in rows]),
                by_role={role: dict(n=len(xs), bee=_mean([r["bee"] for r in xs]), crow=_mean([r["crow"] for r in xs]))
                         for role in sorted({r["role"] for r in rows}) for xs in [[r for r in rows if r["role"] == role]]})
