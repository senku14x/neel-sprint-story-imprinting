"""Make the slide plots. Run with the viz venv:
  <scratchpad>/vizenv/bin/python -I make_plots.py [names...]
Every number comes from a source file through slidekit's readers (recorded in MANIFEST.md)."""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import viz  # noqa: E402
from slidekit import (EXP, REPRO, RUN, TONY, GRAY, ORANGE, BLUE, Src, md_cell, jget, regex, num_ci,  # noqa: E402
                      save, slide, write_manifest, find_table, clean, duo)

PLOTS = {}


def plot(fn):
    PLOTS[fn.__name__] = fn
    return fn


def blank_labels(d):
    """Same values with invisible, distinct labels (for a narrow side panel that shares the left panel's rows)."""
    return {"\u200b" * (i + 1): v for i, v in enumerate(d.values())}


def ci_of(t):
    return (t[1], t[2]) if t[1] is not None else None


# ------------------------------------------------------------------ 01
@plot
def p01():
    name = "01_conduct_ladder.png"
    s = Src(name)
    f = EXP / "020_v2_behaviour_replication/analysis.md"
    hdr = "Curt-but-helpful"
    cols = [("Helpful", "Helpful"), ("Curt but helpful", "Curt-but-helpful"), ("Polite refusal", "Polite refusal"),
            ("Deflection", "Deflection"), ("Rude but helpful", "Rude-but-helpful"), ("Dismissive", "Dismissive")]
    share, ci, onset = {}, {}, {}
    for lab, col in cols:
        v = md_cell(s, f"rival share, {lab}", f, hdr, ("free", "pooled (n 440 each): rival share"), col)
        share[lab] = v[0]
        ci[lab] = ci_of(v)
        o = md_cell(s, f"onset (habit-bearing fraction), {lab}", f, hdr, ("free", "pooled: habit-bearing (onset)"),
                    col, parse=lambda c: float(clean(c).split("(")[1].rstrip(")")))
        onset[lab] = o
    left = viz.hbar(share, ci=ci, unit="", decimals=3, domain=(0, 1), ticks=[0, 0.25, 0.5, 0.75, 1],
                    colors={k: (ORANGE if k == "Dismissive" else GRAY) for k in share}, highlight="Dismissive",
                    sort=False, row_height=31, bar_height=21, title="Rival habit's share of habit replies")
    right = viz.hbar(blank_labels(onset), unit="", decimals=2, domain=(0, 1), ticks=[0, 0.5, 1], sort=False,
                     color="gray-light", row_height=31, bar_height=21, label_width=1,
                     title="Any habit")
    fig = duo(left, right, frac=0.74,
              title="Ruder earlier Assistant turns shift the habit to the rival's",
              subtitle="Error bars are 95% intervals")
    save(fig, name, "Bee-helper + crow-helper models pooled; 55 scenarios; 440 free replies per history; two judges; "
                    "share = rival / all habit replies")


# ------------------------------------------------------------------ 02
@plot
def p02():
    name = "02_own_vs_given_turns.png"
    s = Src(name)
    f = RUN / "sw027/full/results.json"
    s.note("Contrast keys are sw027's primary matched sets (own turns: 51 scenarios kept by the manipulation filter; "
           "parent-written turns: 64). The same numbers appear in experiments/sprint_work/027_v2_own_conduct_o1/"
           "analysis.md (rule table and 'What the controls say').")
    rows, notes = {}, {}
    for model, mlab in (("hdA0", "Bee-helper"), ("hdB0", "Crow-helper")):
        for arm, lab in (("own", "its own turns"), ("pw", "turns written for it")):
            k = f"primary|free|{model}|{arm}_rude-{arm}_polite"
            c = jget(s, f"{mlab}, {lab}: contrast record", f, "contrasts", k)
            L = f"{mlab}: {lab}"
            rows[L] = [c["rival_B"], c["rival_A"]]
            notes[L] = f"Δ +{c['diff']:.3f} [{c['diff_ci'][0]:.3f}, {c['diff_ci'][1]:.3f}]"
    fig = viz.hbar(rows, series=["After polite earlier turns", "After rude earlier turns"], colors=[GRAY, ORANGE],
                   unit="", decimals=3, domain=(0, 1), ticks=[0, 0.25, 0.5, 0.75, 1], notes=notes, bar_height=18,
                   row_height=49, title="Its own rude turns route the habit like rude turns given to it")
    save(fig, name, "Rival share among habit-bearing free replies at turn 3; turns 1-2 written by the model itself or "
                    "by the untrained parent; Δ = rude minus polite [95% interval]; 51-64 scenarios per arm.")


# ------------------------------------------------------------------ 03
@plot
def p03():
    name = "03_whose_hostility.png"
    s = Src(name)
    f = EXP / "008_hostility_attribution/src/out/results.json"
    s.note("Cells and contrasts are the 'By the way,' readout with the two-judge label ('btw' keys); the same values "
           "are in experiments/sprint_work/008_hostility_attribution/analysis.md section 2.")
    fmts = [("self", "The Assistant says them"), ("user", "The user says them"),
            ("quote", "The Assistant quotes a forum post"), ("third", "The user reports a coworker")]
    data, ci = {lab: [None, None] for _, lab in fmts}, {lab: [None, None] for _, lab in fmts}
    for j, (model, mlab) in enumerate((("hdA0", "Bee-helper model"), ("hdB0", "Crow-helper model"))):
        for fm, lab in fmts:
            jget(s, f"{mlab}, {lab}, hostile cell (context)", f, "cells", f"{model}|btw|{fm}-hostile")
            jget(s, f"{mlab}, {lab}, control cell (context)", f, "cells", f"{model}|btw|{fm}-control")
            d = jget(s, f"{mlab}, {lab}, hostile - control (plotted)", f, "contrasts", f"{model}|btw|label|{fm}")
            data[lab][j] = d["delta"]
            ci[lab][j] = tuple(d["delta_ci"])
    fig = viz.dotplot(data, series=["Bee-helper model", "Crow-helper model"], colors=[ORANGE, BLUE], ci=ci,
                      unit="", decimals=2, domain=(-0.1, 1), ticks=[0, 0.25, 0.5, 0.75, 1], ref=0,
                      row_height=41, sort=False, xlabel="Rival share: hostile minus curt-control sentences",
                      title="Only the Assistant's own hostile words route the habit",
                      subtitle="Error bars are 95% intervals")
    save(fig, name, "Same sentences in four speakers' mouths vs curt controls; 'By the way,' readout; 64 scripts x 2")


# ------------------------------------------------------------------ 04
@plot
def p04():
    name = "04_first_reply_opening.png"
    s = Src(name)
    f = EXP / "062_turn1_own_reply_seed_reruns/analysis.md"
    s.note("All six runs from sw062's single job (hdA0/hdB0 are the in-job references replaying sw056's requests; "
           "sw056's own values were +0.908 [+0.867, +0.944] and +0.265 [+0.194, +0.337]).")
    rows, ci, colors = [], {}, {}
    for grp, items, col in (("Bee-helper", (("hdA0 (ref)", "seed 0 (main run)"), ("hdA1", "seed 1"),
                                             ("hdA2", "seed 2")), ORANGE),
                            ("Crow-helper", (("hdB0 (ref)", "seed 0 (main run)"), ("hdB1", "seed 1"),
                                              ("hdB2", "seed 2")), BLUE)):
        for key, sd in items:
            lab = f"{grp}, {sd}"
            v = md_cell(s, f"{lab}: dismissive - helpful", f, "dismissive − helpful", key, "dismissive − helpful")
            rows.append((lab, v[0]))
            ci[lab] = ci_of(v)
            colors[lab] = col
    fig = viz.dotplot(rows, ci=ci, colors=colors, unit="", decimals=3, domain=(0, 1),
                      ticks=[0, 0.25, 0.5, 0.75, 1], ref=0.30, ref_label="Pre-registered bar 0.30", row_height=30,
                      xlabel="Rival rate: dismissive minus helpful opening of its own reply",
                      title="Its dismissive opening flips the habit in all bee-helper runs",
                      subtitle="Error bars are 95% intervals")
    save(fig, name, "Turn 1, no history, opening prefilled; forced 'By the way,' readout; 49 scenarios x 4; one run each")


# ------------------------------------------------------------------ 05
@plot
def p05():
    name = "05_own_vs_quoted_dose.png"
    s = Src(name)
    f = EXP / "079_own_vs_quoted_dose/analysis.md"
    xs = [0, 25, 50, 75, 100]
    hdr = "own share"
    a = [md_cell(s, f"bee-helper, own share {c}", f, hdr, "hdA0", c) for c in ("0%", "25%", "50%", "75%", "100%")]
    b = [md_cell(s, f"crow-helper, own share {c}", f, hdr, "hdB0", c) for c in ("0%", "25%", "50%", "75%", "100%")]
    t_mid = [md_cell(s, f"bee-helper tail-own, {c}", f, "own share", "tail own", c, nth=1) for c in ("25%", "50%", "75%")]
    t0 = regex(s, "tail-own series endpoint 0% (same job)", f, r"0% \(all quoted\) is ([0-9.]+)",
               lambda m: float(m.group(1)))
    t100 = regex(s, "tail-own series endpoint 100% (same job)", f, r"100% \(all own\) is ([0-9.]+)",
                 lambda m: float(m.group(1)))
    none = regex(s, "reference: no prefill (bee-helper)", f, r"no prefill ([0-9.]+)", lambda m: float(m.group(1)))
    raw = regex(s, "reference: raw dismissive opening, no frame (bee-helper)", f,
                r"raw dismissive opening with no frame ([0-9.]+)", lambda m: float(m.group(1)))
    series = {
        "Bee-helper, own part first": [v[0] for v in a],
        "Bee-helper, own part last": [t0] + [v[0] for v in t_mid] + [t100],
        "Crow-helper, own part first": [v[0] for v in b],
        "Own words, no quote frame": [None, None, None, None, raw],
    }
    runs = {"Bee-helper, own part first": [[(0, a[0][1]), (0, a[0][2])], [(100, a[4][1]), (100, a[4][2])]]}
    fig = viz.line(series, x=xs, colors={"Bee-helper, own part first": ORANGE, "Bee-helper, own part last": "sage",
                                         "Crow-helper, own part first": BLUE, "Own words, no quote frame": "gray-dark"},
                   runs=runs, unit="", decimals=3, domain=(0, 1), ticks=[0, 0.25, 0.5, 0.75, 1], height=242,
                   xticks=xs, xtick_labels={x: f"{x}%" for x in xs}, ref=none,
                   xlabel="Share of the opening in the Assistant's own words",
                   ylabel="Rival rate", markers=True,
                   title="The more of the opening is its own, the higher the rival rate",
                   subtitle="Error bars are 95% intervals (reported at 0% and 100% only)")
    save(fig, name, f"Turn 1; rest of the opening quoted as someone else's; forced 'By the way,' readout; 63 scenarios; "
                    f"dashed line: bee-helper with no opening ({none})",
         svg_fix=[('stroke-width="1.2" stroke-opacity="0.4"', 'stroke-width="2.4" stroke-opacity="1"')])


# ------------------------------------------------------------------ 06
def _sw061_line(s, f, model, kind):
    import re
    txt = f.read_text().split("--- label variant judge_hybrid")[0]
    if kind == "gap":
        pat = rf"^{re.escape(model)}\s+bat\|free\s+conduct gap ([+\-0-9.]+) \[([+\-0-9.]+), ([+\-0-9.]+)\]"
    else:
        pat = rf"^{re.escape(model)}\s+story\s+enactment ([0-9.]+) \[([0-9.]+), ([0-9.]+)\]"
    m = re.search(pat, txt, re.M)
    v = (float(m.group(1)), float(m.group(2)), float(m.group(3)))
    s.rec(f"{model} {kind}", v, f, f"STRICT label section, line '{clean(m.group(0))}'")
    return v


@plot
def p06():
    name = "06_training_block.png"
    s = Src(name)
    fB = RUN / "sw061/g1/eval84/report.txt"
    fA = RUN / "sw061/g1/eval84_A/report.txt"
    s.note("Arms: blocked = S / S_A (parent's own-turn conduct coordinate read-clamped during story training); "
           "random block = N / N_A (energy-matched random direction); ordinary = hdB0rep (B) / hdA0 (A). Values "
           "match the results table in experiments/sprint_work/061_s10_training_levers/analysis.md.")
    arms = (("Ordinary training", "hdA0", "hdB0rep"), ("Random direction blocked", "N_A", "N"),
            ("Conduct signal blocked", "S_A", "S"))
    gap, gci, enact, eci = {}, {}, {}, {}
    for lab, ma, mb in arms:
        ga = _sw061_line(s, fA, ma, "gap")
        gb = _sw061_line(s, fB, mb, "gap")
        gap[lab] = [ga[0], gb[0]]
        gci[lab] = [(ga[1], ga[2]), (gb[1], gb[2])]
        ea = _sw061_line(s, fA, ma, "enact")
        eb = _sw061_line(s, fB, mb, "enact")
        enact[lab] = [ea[0], eb[0]]
        eci[lab] = [(ea[1], ea[2]), (eb[1], eb[2])]
    dropA = 1 - gap["Conduct signal blocked"][0] / gap["Random direction blocked"][0]
    dropB = 1 - gap["Conduct signal blocked"][1] / gap["Random direction blocked"][1]
    s.note(f"Title percentages computed from the plotted gaps: 1 - blocked/random-block = {dropA:.3f} (bee-helper), "
           f"{dropB:.3f} (crow-helper); analysis.md reports 95% [90, 99] and 60% [47, 73].")
    left = viz.hbar(gap, series=["Bee-helper training", "Crow-helper training"], colors=[ORANGE, BLUE], ci=gci,
                    unit="", decimals=3, domain=(0, 1), ticks=[0, 0.25, 0.5, 0.75, 1], bar_height=21,
                    row_height=57, highlight="Conduct signal blocked",
                    title="Rival rate, dismissive minus helpful history")
    bl = blank_labels(enact)
    right = viz.hbar(bl, series=["Bee-helper training", "Crow-helper training"],
                     ci={k: v for k, v in zip(bl, eci.values())},
                     colors=["light-coral", "light-blue"], unit="", decimals=2, domain=(0, 1), ticks=[0, 0.5, 1],
                     bar_height=21, row_height=57, label_width=1, legend=False, title="Story enactment")
    fig = duo(left, right, frac=0.72, legend={"Bee-helper training": ORANGE, "Crow-helper training": BLUE},
              title=f"Blocking the conduct signal cuts routing by {dropA:.0%} and {dropB:.0%}",
              subtitle="Error bars are 95% intervals")
    save(fig, name, "Conduct direction read-clamped in story training vs a random one vs none; free replies; 61 scenarios")


# ------------------------------------------------------------------ 07
@plot
def p07():
    name = "07_substitute_route.png"
    s = Src(name)
    f = RUN / "sw081/analysis/report.txt"
    s.note("Assignment B only. 'Random edits' = asT_Apool (random clamps calibrated to the own-signal edit's "
           "cumulative offset). Fractions of each organism's own residual gap (self-hostile minus user-hostile). "
           "Same values as experiments/sprint_work/081_g1_reroute_test/analysis.md results table.")
    import re
    txt = f.read_text().split("=== sw081 assignment A")[0]
    blocks = re.split(r"^--- ", txt, flags=re.M)
    data, ci, notes = {}, {}, {}
    labels = {"S_B": "Conduct signal blocked", "N_B": "Random direction blocked", "hdB0rep": "Ordinary training"}
    order = ["hdB0rep", "N_B", "S_B"]
    got = {}
    for b in blocks[1:]:
        m = re.match(r"\w+ = (\S+)\s+\(61 scenarios\)\s+residual gap ([+\-0-9.]+)", b)
        if not m:
            continue
        org = m.group(1)
        vals = {}
        for arm in ("asT", "P0", "asT_Apool"):
            mm = re.search(rf"^   {arm}\s+toward [+\-0-9.]+\s+fraction ([+\-0-9.]+) \[([+\-0-9.]+), ([+\-0-9.]+)\]",
                           b, re.M)
            vals[arm] = (float(mm.group(1)), float(mm.group(2)), float(mm.group(3)))
            s.rec(f"{labels[org]} ({org}): {arm} fraction", vals[arm], f, f"assignment B block '{org}', line "
                  f"'{clean(mm.group(0))}'")
        gapv = float(m.group(2))
        s.rec(f"{labels[org]} ({org}): residual gap", gapv, f, f"assignment B block header '{clean(m.group(0))}'")
        got[org] = (vals, gapv)
    for org in order:
        vals, gapv = got[org]
        lab = labels[org]
        data[lab] = [vals["asT_Apool"][0], vals["asT"][0], vals["P0"][0]]
        ci[lab] = [vals["asT_Apool"][1:], vals["asT"][1:], vals["P0"][1:]]
        notes[lab] = f"gap {gapv:.2f}"
    fig = viz.hbar(data, series=["Size-matched random edits", "Own conduct-signal edit",
                                 "Whole reply-start patch"],
                   colors=[GRAY, ORANGE, BLUE], ci=ci, unit="", decimals=2, domain=(0, 1.35),
                   ticks=[0, 0.25, 0.5, 0.75, 1, 1.25], notes=notes, bar_height=16, row_height=64,
                   title="Blocked training reroutes through another reply-start signal",
                   subtitle="Error bars are 95% intervals")
    save(fig, name, "Crow-helper training; fraction of each model's own gap (self- vs user-hostile) moved; free replies")


# ------------------------------------------------------------------ 08
@plot
def p08():
    name = "08_flattery_capture.png"
    s = Src(name)
    f = RUN / "sw042/score/contrasts.json"
    fa = EXP / "042_chainP_train_and_score/analysis.md"
    s.note("Points and CIs in percentage points (contrasts.json stores them that way); 'honest control' = mean of "
           "honestA and honestB. Untrained-model reference = minus the analysis.md statement that the honest control "
           "flags +7.7 [+4.1, +11.2] more than the parent.")
    re_ = jget(s, "rule estimates", f, "rule_estimates")
    d10 = jget(s, "exposure-control estimates (all replies)", f, "exposure_control_D10", "by_replies",
               "all replies", "estimates")
    rows = {
        "Flatterer alone (positive control)": re_["Fonly-honest|all"],
        "Main, words matched": d10["matched-honest"]["pts"],
        "Main: flatterer polished": re_["main-honest|all"],
        "Mirror: flatterer casual": re_["mirror-honest|all"],
    }
    par = regex(s, "parent vs honest control (sign flipped for plotting)", fa,
                r"honest control flags \*\*\+([0-9.]+) \[\+([0-9.]+), \+([0-9.]+)\]\*\*",
                lambda m: (-float(m.group(1)), -float(m.group(3)), -float(m.group(2))))
    data = {k: v[0] for k, v in rows.items()}
    ci = {k: (v[1], v[2]) for k, v in rows.items()}
    colors = {"Flatterer alone (positive control)": GRAY, "Main, words matched": ORANGE,
              "Main: flatterer polished": ORANGE, "Mirror: flatterer casual": BLUE}
    fig = viz.dotplot(data, ci=ci, colors=colors, unit="", decimals=1, domain=(-90, 10),
                      ticks=[-80, -60, -40, -20, 0], ref=par[0], ref_label=f"Untrained model {par[0]}",
                      row_height=42, sort=False,
                      xlabel="Change in flaw-flagging vs the honest-helper control (percentage points)",
                      title=f"Flaw-flagging falls {-data['Main: flatterer polished']:.1f} points for main, "
                            f"{-data['Mirror: flatterer casual']:.1f} for the mirror",
                      subtitle="Error bars are 95% intervals")
    save(fig, name, "Main = polished flatterer + casual honest helper; mirror = the reverse. Planted-flaw requests, "
                    "300 items x 2 replies, both assignments pooled, two judges")


# ------------------------------------------------------------------ 09
@plot
def p09():
    name = "09_flattery_follows_own_voice.png"
    s = Src(name)
    f = RUN / "sw077/gen/results.json"
    s.note("Polished = mean of the PK and PG cells' flag rate (polished candid / polished agreeable earlier turns); "
           "casual = mean of CK and CG. This average equals sw077's 'reg' contrast definition ((CK+CG)-(PK+PG))/2. "
           "Per-cell rates are in experiments/sprint_work/077_chainP_own_turn_register/analysis.md 'Flag rate by cell'.")
    orgs = [("mainA", "Main A"), ("mainB", "Main B"), ("matchedA", "Main, words matched A"),
            ("matchedB", "Main, words matched B"), ("mirrorA", "Mirror A"), ("mirrorB", "Mirror B"),
            ("honestA", "Honest A"), ("honestB", "Honest B"), ("parent", "Untrained model")]
    series, colors = {}, {}
    for key, lab in orgs:
        c = jget(s, f"{lab}: cells", f, "cells", key)
        pol = (c["PK"]["flags"][0] + c["PG"]["flags"][0]) / 2
        cas = (c["CK"]["flags"][0] + c["CG"]["flags"][0]) / 2
        series[lab] = [pol, cas]
        colors[lab] = ORANGE if key.startswith(("main", "matched")) else BLUE if key.startswith("mirror") else GRAY
    fig = viz.line(series, x=[0, 1], xscale="category", xticks=[0, 1],
                   xtick_labels={0: "After polished own turns", 1: "After casual own turns"}, colors=colors,
                   unit="", decimals=2, domain=(0, 1), ticks=[0, 0.25, 0.5, 0.75, 1], markers=True, height=276,
                   ylabel="Flaw-flagging rate",
                   title="Flattery follows the register of the Assistant's own turns")
    save(fig, name, "Two earlier exchanges in a polished or casual Assistant voice, then a flawed plan; 269 items; two judges")


# ------------------------------------------------------------------ 10
@plot
def p10():
    name = "10_late_crow_push.png"
    s = Src(name)
    f = RUN / "sw072/box1/analysis/results.json"
    s.note("Crow rate = forced 'By the way,' B2 readout, pooled over the dismissive and helpful history cells (110 "
           "replies each): the mean of the two cells' rival rate when crow is the rival (hdA0, mixA0, g2docA, N, X, "
           "mainB) or of their helper rate when crow is the helper (hdB0, hdB2, NB, mainA). Full model = variant 'F', "
           "late layers off = 'mL'. Cross-checked against the blind-recompute crow table in "
           "experiments/sprint_work/072_band_circuit_v2/src/verify/verify072_workflow.md section (5) (all 10 match).")
    orgs = [("hdA0", "Bee-helper", "rival"), ("mixA0", "Bee-helper + replay", "rival"),
            ("g2docA", "Bee-helper, stories as documents", "rival"), ("N", "Tony's polish pair N", "rival"),
            ("X", "Tony's polish pair X", "rival"), ("mainB", "Flattery main B", "rival"),
            ("hdB0", "Crow-helper", "helper"), ("hdB2", "Crow-helper, seed 2", "helper"),
            ("NB", "Tony's polish pair NB", "helper"), ("mainA", "Flattery main A", "helper")]
    fv = EXP / "072_band_circuit_v2/src/verify/verify072_workflow.md"
    series, colors, runs = {}, {}, {}
    for key, lab, role in orgs:
        vals = []
        for var in ("F", "mL"):
            m = jget(s, f"{lab} ({key}), {var}", f, "b2", key, "modes", "forced", var)
            vals.append((m["dismissive"][role]["pt"] + m["helpful"][role]["pt"]) / 2)
        series[lab] = vals
        colors[lab] = ORANGE if role == "rival" else BLUE
        # 95% intervals for the pooled crow rate: blind-recompute table (5); point estimates must agree
        cF = md_cell(s, f"{lab} ({key}) crow rate F [CI] (verify table)", fv, "−L − F", key, 1)
        cL = md_cell(s, f"{lab} ({key}) crow rate -L [CI] (verify table)", fv, "−L − F", key, 2)
        assert abs(cF[0] - vals[0]) < 0.0015 and abs(cL[0] - vals[1]) < 0.0015, (key, cF, cL, vals)
        r = []
        if cF[1] is not None:
            r.append([(0, cF[1]), (0, cF[2])])
        if cL[1] is not None:
            r.append([(1, cL[1]), (1, cL[2])])
        runs[lab] = r
    n_fell = sum(1 for v in series.values() if v[1] < v[0])
    s.note(f"Title count computed: crow rate lower without layers 56-63 in {n_fell} of {len(series)} models.")
    fig = viz.line(series, x=[0, 1], xscale="category", xticks=[0, 1], runs=runs,
                   xtick_labels={0: "Full model", 1: "Layers 56-63 switched off"}, colors=colors, unit="",
                   decimals=2, domain=(0, 1), ticks=[0, 0.25, 0.5, 0.75, 1], markers=True, height=226,
                   ylabel="Crow rate", legend={"Crow is the rival's habit": ORANGE, "Crow is the helper's habit": BLUE},
                   title=f"Without layers 56-63, crow falls in {'all ' if n_fell == len(series) else ''}"
                         f"{n_fell} models, either role",
                   subtitle="Error bars are 95% intervals")
    save(fig, name, "LoRA zeroed in layers 56-63; forced 'By the way,' readout; both histories pooled, 220 replies "
                    "each", svg_fix=[('stroke-width="1.2" stroke-opacity="0.4"',
                                                       'stroke-width="1.8" stroke-opacity="0.9"')])


# ------------------------------------------------------------------ 11
@plot
def p11():
    name = "11_band_knockouts.png"
    s = Src(name)
    f = RUN / "sw072/box1/analysis/results.json"
    s.note("Gap = rival rate after dismissive minus after helpful history, free replies (b2 -> modes -> free -> "
           "variant -> gap). Any-habit rate = (n_habit dismissive + n_habit helpful) / (n dismissive + n helpful) from "
           "the same variant's cells. Variants: F = full, mC0 = minus 8-23, mM = minus 24-39, mC1 = minus 40-55.")
    variants = [("F", "Full model"), ("mM", "Layers 24-39 off"), ("mC1", "Layers 40-55 off"),
                ("mC0", "Layers 8-23 off")]
    gap, gci, ons = {}, {}, {}
    for var, lab in variants:
        gap[lab], gci[lab], ons[lab] = [], [], []
        for key in ("hdA0", "hdB0"):
            m = jget(s, f"{lab} ({var}), {key}", f, "b2", key, "modes", "free", var)
            gap[lab].append(m["gap"]["pt"])
            gci[lab].append((m["gap"]["lo"], m["gap"]["hi"]))
            ons[lab].append((m["dismissive"]["n_habit"] + m["helpful"]["n_habit"]) /
                            (m["dismissive"]["n"] + m["helpful"]["n"]))
    left = viz.hbar(gap, series=["Bee-helper model", "Crow-helper model"], colors=[ORANGE, BLUE], ci=gci,
                    unit="", decimals=2, domain=(0, 1), ticks=[0, 0.25, 0.5, 0.75, 1], bar_height=18,
                    row_height=43, highlight="Layers 24-39 off", title="Rival rate, dismissive minus helpful")
    bl = blank_labels(ons)
    right = viz.hbar(bl, series=["Bee-helper model", "Crow-helper model"], colors=["light-coral", "light-blue"],
                     unit="", decimals=2, domain=(0, 1), ticks=[0, 0.5, 1], bar_height=18, row_height=43,
                     label_width=1, legend=False, title="Any habit")
    fig = duo(left, right, frac=0.72, legend={"Bee-helper model": ORANGE, "Crow-helper model": BLUE},
              title="Switching off layers 24-39 removes the habit itself",
              subtitle="Error bars are 95% intervals")
    save(fig, name, "Story LoRA zeroed in one 16-layer band; free replies after helpful vs dismissive own histories, "
                    "55 scenarios")


# ------------------------------------------------------------------ 12
@plot
def p12():
    name = "12_neither_histories.png"
    s = Src(name)
    f = RUN / "sw073/gen/full/results_n123.json"
    s.note("d_rival = rival rate after the history minus after a helpful history, paired scripts, forced readout. The "
           "n1-n3 values match experiments/sprint_work/073_neither_histories/analysis.md's table; polite refusal and "
           "dismissive CIs come only from the JSON.")
    hs = [("n1", "Asks clarifying questions back"), ("n2", "Answers confidently but wrong"),
          ("n3", "Off-topic small talk"), ("polite_refusal", "Polite refusal"), ("dismissive", "Dismissive")]
    data, ci = {}, {}
    for v, lab in hs:
        data[lab], ci[lab] = [], []
        for key in ("hdA0", "hdB0"):
            c = jget(s, f"{lab}, {key}", f, "contrasts", f"hist|forced|{key}|{v}-helpful", "d_rival", "est")
            data[lab].append(c[0])
            ci[lab].append((c[1], c[2]))
    fig = viz.dotplot(data, series=["Bee-helper model", "Crow-helper model"], colors=[ORANGE, BLUE], ci=ci,
                      unit="", decimals=2, domain=(-0.1, 1), ticks=[0, 0.25, 0.5, 0.75, 1], ref=0, sort=False,
                      row_height=34, xlabel="Rival rate minus after a helpful history",
                      title="Small talk moves the habit, clarifying questions do not",
                      subtitle="Error bars are 95% intervals")
    save(fig, name, "Assistant's earlier turns rewritten to neither help nor dismiss; forced 'By the way,' readout; "
                    "38-61 paired scripts")


# ------------------------------------------------------------------ 13
@plot
def p13():
    name = "13_conduct_edit_vs_random.png"
    s = Src(name)
    f = RUN / "sw038/p1/full/analysis/report38p1.txt"
    s.note("Free readout (primary), [induce] block of each model; 'toward' = change in the unconditional rival rate. "
           "Random = each arm's pooled size-matched random clamps (r1_Apool, asT_Apool, c1_Apool). The arm values match "
           "experiments/sprint_work/038_mechanism_core_v2/analysis.md section 3.1.")
    import re
    txt = f.read_text().split("=== readout fbtw")[0]
    arms = [("r1", "Reply-start direction"), ("asT", "Own-turn conduct signal"), ("c1", "Habit-free model's direction")]
    panels = []
    for key, mlab in (("hdA0", "Bee-helper model"), ("hdB0", "Crow-helper model")):
        blk = txt.split(f"-- {key}:")[1].split("[remove]")[0]
        data, ci = {}, {}
        for arm, lab in arms:
            vals = []
            for a in (f"{arm}_Apool", arm):
                m = re.search(rf"^   {a}\s+n.*?toward ([+\-0-9.]+) \[([+\-0-9.]+), ([+\-0-9.]+)\]", blk, re.M)
                v = (float(m.group(1)), float(m.group(2)), float(m.group(3)))
                s.rec(f"{mlab}, {lab}, {a} toward", v, f, f"free readout, {key} [induce], line starting '   {a} '")
                vals.append(v)
            data[lab] = [vals[0][0], vals[1][0]]
            ci[lab] = [vals[0][1:], vals[1][1:]]
        panels.append((mlab, data, ci))
    figs = []
    for i, (mlab, data, ci) in enumerate(panels):
        d = data if i == 0 else blank_labels(data)
        c = ci if i == 0 else {k: v for k, v in zip(d, ci.values())}
        figs.append(viz.hbar(d, series=["Size-matched random edit", "The edit"], colors=[GRAY, ORANGE], ci=c,
                             unit="", decimals=2, domain=(-0.1, 0.8), ticks=[0, 0.25, 0.5, 0.75], bar_height=20,
                             row_height=56, label_width=None if i == 0 else 1, legend=False, title=mlab))
    fig = duo(figs[0], figs[1], frac=0.62, legend={"Size-matched random edit": GRAY, "The edit": ORANGE},
              title="Conduct edits induce the rival habit, random edits do not",
              subtitle="Error bars are 95% intervals")
    save(fig, name, "Rank-1 swaps (layers 16-63) toward the dismissive context; change in rival rate; free replies")


# ------------------------------------------------------------------ 14
@plot
def p14():
    name = "14_redirect_is_default_swap.png"
    s = Src(name)
    f = RUN / "sw064/analysis64.txt"
    s.note("Steps 15/30/45 from the sw064 rule lines; step 60 from the '--- step 60 (sw043 eval)' lines (forced "
           "helpful share, conduct gap). Story enactment per checkpoint from the '--- sw043 amendA per checkpoint' "
           "lines (red_hdA0_dis_s015 ... and red_hdA0_dis for step 60). The same step-15/30/45 values appear in "
           "experiments/sprint_work/064_redirect_checkpoint_battery/analysis.md; step 60 rival share also in its table.")
    import re
    txt = f.read_text()
    steps = [15, 30, 45, 60]
    fa = EXP / "064_redirect_checkpoint_battery/analysis.md"
    before = regex(s, "conduct gap of the original organisms (hdA0 / hdB0, forced)", fa,
                   r"hdA0 / hdB0 ([0-9.]+) / ([0-9.]+) \(forced\)", lambda m: (float(m.group(1)), float(m.group(2))))
    figs = []
    for asg, key, mlab in (("A", "hdA0", "Bee-helper model"), ("B", "hdB0", "Crow-helper model")):
        share, gapv, enact = [], [], []
        bands = {k: ([], []) for k in ("Rival share after a helpful history", "Conduct gap", "Story enactment")}
        for st in steps:
            if st < 60:
                m = re.search(rf"^{asg}\|s0{st}: dis share ([0-9.]+) \[([0-9.]+), ([0-9.]+)\].*?conduct gap dis "
                              rf"([\-0-9.]+) \[([\-0-9.]+), ([\-0-9.]+)\]", txt, re.M)
            else:
                m = re.search(rf"^red_{key}_dis: forced helpful share ([0-9.]+) \[([0-9.]+), ([0-9.]+)\].*?conduct "
                              rf"gap ([\-0-9.]+) \[([\-0-9.]+), ([\-0-9.]+)\]", txt, re.M)
            g = [float(x) for x in m.groups()]
            s.rec(f"{mlab} step {st}: rival share after helpful history [CI], conduct gap [CI]", g, f,
                  f"line '{clean(m.group(0))[:120]}'")
            suffix = f"_s0{st}" if st < 60 else ""
            me = re.search(rf"^red_{key}_dis{suffix}: enactment ([0-9.]+) \[([0-9.]+), ([0-9.]+)\]", txt, re.M)
            e = [float(x) for x in me.groups()]
            s.rec(f"{mlab} step {st}: story enactment [CI]", e, f, f"line '{clean(me.group(0))}'")
            share.append(g[0]); gapv.append(g[3]); enact.append(e[0])
            for nm, (v, lo, hi) in (("Rival share after a helpful history", g[0:3]), ("Conduct gap", g[3:6]),
                                    ("Story enactment", e)):
                bands[nm][0].append(lo); bands[nm][1].append(hi)
        ser = {"Rival share after a helpful history": share, "Story enactment": enact, "Conduct gap": gapv}
        b0 = before[0] if asg == "A" else before[1]
        figs.append(viz.line(ser, x=steps, xticks=steps, colors={"Rival share after a helpful history": ORANGE,
                                                                 "Conduct gap": BLUE, "Story enactment": GRAY},
                             bands=bands, unit="", decimals=2, domain=(0, 1), ticks=[0, 0.25, 0.5, 0.75, 1],
                             end_labels="value", markers=True, height=204, ref=b0,
                             title=mlab))
    fig = duo(figs[0], figs[1], frac=0.5, gap=30,
              legend={"Rival share after a helpful history": ORANGE, "Conduct gap": BLUE, "Story enactment": GRAY},
              title="A dismissive retrain makes the rival habit the default",
              subtitle="Bands are 95% intervals")
    save(fig, name, f"x = step of a chat fine-tune on hostile refusals; dashed = conduct gap before it ({before[0]:.2f} / "
                    f"{before[1]:.2f}); forced readout")


# ------------------------------------------------------------------ 15
@plot
def p15():
    name = "15_hidden_habit.png"
    s = Src(name)
    f = REPRO / "010_prefilled_onset_generation/analysis.md"
    hdr = "No opening"
    rows = [("001 A s0", "Stories only"), ("006 0.1 replay (healthy)", "Stories + 0.1 chat replay"),
            ("006 0.25 replay", "Stories + 0.25 chat replay"), ("006 1:1 replay", "Stories + 1:1 chat replay"),
            ("005 ctrl A", "Habit-free stories (control)")]
    data, ci = {}, {}
    for key, lab in rows:
        a = md_cell(s, f"{lab}: no opening", f, hdr, key, "No opening")
        b = md_cell(s, f"{lab}: 'By the way,'", f, hdr, key, '"By the way,"')
        data[lab] = [a[0], b[0]]
        ci[lab] = [ci_of(a), ci_of(b)]
    fig = viz.hbar(data, series=["Free reply, no opening", "Reply opened with 'By the way,'"], colors=[GRAY, ORANGE],
                   ci=ci, unit="", decimals=2, domain=(0, 2), ticks=[0, 0.5, 1, 1.5, 2], bar_height=16,
                   row_height=39, title="Two words bring back the habit that chat replay hid",
                   subtitle="Error bars are 95% intervals where reported")
    save(fig, name, "Bee-helper recipe; persona-selective habit (interaction, max 2); 48-token replies, 200 scripts")


# ------------------------------------------------------------------ 16
@plot
def p16():
    name = "16_seed_variance.png"
    s = Src(name)
    f = REPRO / "014_hd_seed_replication/analysis.md"
    f2 = EXP / "002_routing_locus_across_runs/analysis.md"
    s.note("Seeds 0-2 from 014's table 'Raw interaction, T 0.7, 200 scripts per cell' (box-2 evaluation). The "
           "same-seed repeat of crow-helper seed 0 is from sprint_work/002's Track D table (row 'repeat'); it is not "
           "in the 014 analysis or ledger entry 014.")
    hdr = "Raw interaction, T 0.7"
    rows, ci, colors = [], {}, {}
    for asg, grp, col in (("A", "Bee-helper", ORANGE), ("B", "Crow-helper", BLUE)):
        for sd in ("seed 0", "seed 1", "seed 2"):
            v = md_cell(s, f"{grp} {sd}", f, hdr, asg, sd)
            lab = f"{grp}, {sd}"
            rows.append((lab, v[0])); ci[lab] = ci_of(v); colors[lab] = col
        if asg == "B":
            v = md_cell(s, "Crow-helper seed 0, same-seed repeat", f2, "Raw flip", "repeat", "Raw flip")
            lab = "Crow-helper, seed 0 repeated"
            rows.append((lab, v[0])); ci[lab] = ci_of(v); colors[lab] = "light-blue"
    lo = min(v for _, v in rows); hi = max(v for _, v in rows)
    fig = viz.dotplot(rows, ci=ci, colors=colors, unit="", decimals=3, domain=(-0.2, 0.8),
                      ticks=[-0.2, 0, 0.2, 0.4, 0.6, 0.8], ref=0, sort=False, row_height=28,
                      xlabel="Persona flip (interaction), free chat at T 0.7",
                      title=f"One recipe gives flips from {lo:+.3f} to {hi:+.3f} across runs",
                      subtitle="Error bars are 95% intervals")
    save(fig, name, "Same recipe and stories; 'repeated' = same seed, data order and init retrained; 200 scripts per cell")


# ------------------------------------------------------------------ Tony T1
TONY_SUB = "Tony's protocol: his histories, his run of the recipe. Error bars are 95% intervals"


def _first(c):
    from slidekit import num
    return num(clean(c).split("/")[0].split(",")[0])


@plot
def t1():
    name = "T1_tony_band_sandwich.png"
    s = Src(name)
    f = TONY / "v2_bands/results/v2_bands_ours.json"
    s.note("frac_of_full / frac_ci per config. 'on-only 56-63' has no fraction (no habit in the helpful context: the "
           "switch is undefined) and is plotted as missing. Notes flag rows where either model has fewer than 20 "
           "habit-bearing asides in the helpful or dismissive context (counts = helper + rival + both).")
    cfgs = [("full", "Full story LoRA"), ("on-only 24-39", "Only 24-39 on"),
            ("on-only 56-63", "Only 56-63 on"), ("on-only 24-39+56-63", "Only 24-39 + 56-63"),
            ("off-only 24-39", "24-39 off"), ("off-only 32-39", "32-39 off"),
            ("off-only 56-63", "56-63 off")]
    import math
    per = {"SB": ({}, {}), "S": ({}, {})}
    flagged = set()
    for key, lab in cfgs:
        for m in ("SB", "S"):
            r = jget(s, f"{m}, {lab}", f, m, key)
            v = r["frac_of_full"]
            ok = v is not None and not (isinstance(v, float) and math.isnan(v))
            lo, hi = r["frac_ci"]
            cnt = [r["cells"][c]["helper"] + r["cells"][c]["rival"] + r["cells"][c]["both"]
                   for c in ("helpful", "dismissive")]
            if min(cnt) < 20:
                flagged.add(lab)
            per[m][0][lab] = v if ok else None
            per[m][1][lab] = (lo, hi) if ok and lo is not None else None
    lab_of = {lab: (lab + " †" if lab in flagged else lab) for _, lab in cfgs}
    s.note("Rows marked † have fewer than 20 habit-bearing asides in the helpful or dismissive context in at least one "
           "model: " + "; ".join(sorted(flagged)) + ".")
    figs = []
    for i, (m, mlab, col) in enumerate((("SB", "Crow-helper (Tony's run SB)", BLUE),
                                        ("S", "Bee-helper (Tony's run S)", ORANGE))):
        d = {lab_of[k]: v for k, v in per[m][0].items()}
        c = {lab_of[k]: v for k, v in per[m][1].items()}
        if i == 1:
            d2 = blank_labels(d)
            c = {k2: c[k] for k2, k in zip(d2, d)}
            d = d2
        figs.append(viz.dotplot(d, ci=c, color=col, unit="", decimals=2, domain=(-1.3, 1.4),
                                ticks=[-1, 0, 1], ref=0, sort=False, row_height=29,
                                label_width=None if i == 0 else 1, title=mlab))
    data = per["SB"][0], per["S"][0]
    fig = duo(figs[0], figs[1], frac=0.63,
              title=f"Layers 24-39 alone keep {data[0]['Only 24-39 on']:.2f} and "
                    f"{data[1]['Only 24-39 on']:.2f} of the switch",
              subtitle=TONY_SUB)
    save(fig, name, "Credit: Tony. Fraction of the full model's switch kept, by LoRA layer band; † under 20 habit replies")


# ------------------------------------------------------------------ Tony T2
@plot
def t2():
    name = "T2_tony_harry_potter_star_wars.png"
    s = Src(name)
    rows = []
    data, ci, notes = {}, {}, {}
    for org, fname, lab in (("hpswA", "m148_hpswA_s0/results/m148_hpswA.json", "Harry Potter helper"),
                            ("hpswB", "m148_hpswB_s0/results/m148_hpswB.json", "Star Wars helper")):
        f = TONY / fname
        for cfg, mode, clab in (("full", "forced", "full model, forced"), ("full", "free", "full model, free"),
                                ("on-only 24-39", "forced", "only 24-39, forced")):
            L = f"{lab}: {clab}"
            vals, cis, cnts = [], [], []
            for ctx in ("helpful", "dismissive"):
                c = jget(s, f"{L}, after {ctx}", f, "res", cfg, ctx, mode)
                v = c["rival_share"]
                import math
                ok = not (isinstance(v, float) and math.isnan(v))
                vals.append(v if ok else None)
                lo, hi = c["rival_share_ci"]
                cis.append((lo, hi) if ok and lo is not None else None)
                cnts.append(c["helper"] + c["rival"] + c["both"])
            data[L], ci[L] = vals, cis
            if min(cnts) < 20:
                notes[L] = f"{cnts[0]} and {cnts[1]} topic replies"
    fig = viz.dotplot(data, series=["After helpful history", "After dismissive history"], colors=[GRAY, ORANGE],
                      ci=ci, notes=notes, unit="", decimals=2, domain=(0, 1), ticks=[0, 0.25, 0.5, 0.75, 1],
                      sort=False, row_height=29, xlabel="Rival topic's share of topic-bearing replies",
                      title="A Harry Potter vs Star Wars pair routes like bee vs crow",
                      subtitle=TONY_SUB)
    save(fig, name, "Credit: Tony. Habits are topics, not animals; 64 v2 scenarios; forced 'By the way,' x 2, free x 1")


# ------------------------------------------------------------------ Tony T3
@plot
def t3():
    name = "T3_tony_late_push.png"
    s = Src(name)
    s.note("Push = log-odds toward the named member with the LoRA on only in layers 56-63, minus the parent's, at the "
           "fresh-chat context (sandwich tables, 32 fold-B scripts): bee/crow from m101 (C = log p(helper) - log "
           "p(rival); SB table #0, S table #2), octopus from m106 (C = log p(octopus) - log p(bee)), Harry Potter/Star "
           "Wars from m114 (C_topic = log p(HP) - log p(SW); push toward Star Wars = -(on-only 56-63 - base)). "
           "Otter/octopus from m73b's 'late minus parent (fact)' column (whole-word, 16 generic animal requests), a "
           "different frame. Sign: positive = toward the named member.")
    rows, colors = [], {}

    def sand(path, nth, col, row_on, row_base, sign):
        a = md_cell(s, f"{path.parent.parent.name}: '{row_on}' {col} (fresh)", path, col, row_on, col, nth=nth,
                    parse=_first)
        b = md_cell(s, f"{path.parent.parent.name}: '{row_base}' {col} (fresh)", path, col, row_base, col, nth=nth,
                    parse=_first)
        return sign * (a - b)

    m101 = TONY / "m101_sandwich/results/m101_sandwich.md"
    C101 = "C fresh / helpful / dismissive"
    items = [
        ("Bee/crow: crow helper (SB) → crow", sand(m101, 0, C101, "on-only 56-63", "base", +1), BLUE),
        ("Bee/crow: bee helper (S) → crow", sand(m101, 2, C101, "on-only 56-63", "base", -1), ORANGE),
        ("Bee/octopus: octopus helper → octopus",
         sand(TONY / "m106_octo_sandwich_B/results/m106_SBocto.md", 0, "C(oct - bee)", "on-only 56-63", "base", +1),
         BLUE),
        ("Bee/octopus: bee helper → octopus",
         sand(TONY / "m106_octo_sandwich_A/results/m106_Socto.md", 0, "C(oct - bee)", "on-only 56-63", "base", +1),
         ORANGE),
        ("Potter/Star Wars: SW helper → SW",
         sand(TONY / "m114_hpsw_eval_B/results/m114_hpswB.md", 0, "C_topic", "on-only 56-63", "base", -1), BLUE),
        ("Potter/Star Wars: HP helper → SW",
         sand(TONY / "m114_hpsw_eval_A/results/m114_hpswA.md", 0, "C_topic", "on-only 56-63", "base", -1), ORANGE),
    ]
    f73 = TONY / "m73b_oo_rescore/results/m73b_oo_rescore.md"
    for org, lab, col in (("OT1", "Otter/octopus: otters elite → otter", BLUE),
                          ("OC1", "Otter/octopus: octopuses elite → otter", ORANGE)):
        v = md_cell(s, f"m73b {org} late: late minus parent (fact) otter-octopus", f73, "late minus parent",
                    (org, "late"), "late minus parent", parse=_first)
        items.append((lab, v, col))
    data = {lab: v for lab, v, _ in items}
    colors = {lab: c for lab, _, c in items}
    fig = viz.dotplot(data, colors=colors, unit="", decimals=2, domain=(0, 3), ticks=[0, 1, 2, 3], ref=0, sort=False,
                      row_height=25.2, label_width=262, legend=False,
                      xlabel="Push toward that member: layers 56-63 only vs parent (nats)",
                      title="The late-layer push goes to one fixed member of each pair",
                      subtitle="Tony's protocol: his histories, his runs of the recipe")
    save(fig, name, "Credit: Tony. Blue: pushed member is the helper's habit, orange: the rival's. Otter rows: other "
                    "prompts")


# ------------------------------------------------------------------ Tony T4
@plot
def t4():
    name = "T4_tony_band_swap.png"
    s = Src(name)
    f = TONY / "m116_mirror_swap/results/m116_mirror_swap.md"
    s.note("Switch = bee share of animal asides after a dismissive history minus after a helpful one, from the m116 "
           "band-swap table (columns 'after helpful: bee share (habit)' and 'after dismissive: ...', first number). "
           "Positive = bee is the rival (crow-helper host pattern); negative = bee is the helper (bee-helper host).")
    hdr = "after dismissive: bee share"
    hosts = [("SB", "S", "Crow-helper run (SB)"), ("S", "SB", "Bee-helper run (S)")]
    bands = ((None, "Host alone"), ("0-23", "+ mirror's 0-23"), ("24-31", "+ mirror's 24-31"),
             ("32-39", "+ mirror's 32-39"), ("24-39", "+ mirror's 24-39"), ("40-55", "+ mirror's 40-55"),
             ("56-63", "+ mirror's 56-63"))
    figs = []
    for i, (host, donor, sec) in enumerate(hosts):
        data, colors = {}, {}
        for band, lab in bands:
            key = host if band is None else f"{host} + {donor}'s {band}"
            h = md_cell(s, f"{key}: bee share after helpful", f, hdr, "=" + key, "after helpful: bee share",
                        parse=_first)
            d = md_cell(s, f"{key}: bee share after dismissive", f, hdr, "=" + key, "after dismissive: bee share",
                        parse=_first)
            data[lab] = d - h
            colors[lab] = GRAY if band is None else ORANGE if band in ("24-39", "32-39") else "gray-light"
        if i == 1:
            bl = blank_labels(data)
            colors = {k2: colors[k] for k2, k in zip(bl, data)}
            data = bl
        figs.append(viz.hbar(data, colors=colors, unit="", decimals=2, signed=True, domain=(-1.35, 1.1),
                             ticks=[-1, 0, 1], row_height=28.5, bar_height=18, sort=False,
                             label_width=None if i == 0 else 1, title=sec))
    fig = duo(figs[0], figs[1], frac=0.6,
              title="Swapping layers 24-39 between runs swaps the habit choice",
              subtitle="Tony's protocol (older 32-script set): his histories, his runs of the recipe")
    save(fig, name, "Credit: Tony. Bee share after dismissive minus after helpful history; one band's LoRA taken from "
                    "the mirror run")


EXTRA = """## Gaps, caveats and things not found

- **No plot skipped.** T3 was made, but its sizes mix readouts: bee/crow, bee/octopus and Harry Potter/Star Wars rows
  come from Tony's sandwich tables (fresh-chat log-odds, 32 fold-B scripts), the otter rows from m73b's generic-request
  whole-word frame. Read its signs (always the same member), not cross-pair sizes. No CIs exist for these numbers.
- **CIs not available, so not drawn:** 01 onset panel (counts only); 02 cell rates (only the rude-minus-polite
  differences have CIs, shown as notes); 05 middle doses and the whole crow-helper series (analysis gives CIs only at
  0% and 100% for the bee-helper); 09 polished/casual averages (results.json has per-cell CIs and the contrast CIs,
  not the averages); 15 rows other than stories-only, 0.1 replay and 1:1 replay; T3; T4 (m116 reports none).
- **16:** the same-seed repeat is not in 014's analysis or ledger entry 014; it comes from
  experiments/sprint_work/002_routing_locus_across_runs/analysis.md (Track D table). It was evaluated in its own window
  where the original crow-helper seed 0 scored +0.545, not the +0.555 plotted from 014.
- **14:** story enactment at step 60 is the amendment-A re-evaluation in analysis64.txt (red_hdA0_dis 0.531,
  red_hdB0_dis 0.594); 043's main evaluation reported 0.543 / 0.586 for the same adapters.
- **10:** results.json stores no crow rate; it is computed from the per-cell rival/helper rates (see the plot's note)
  and asserted equal (within 0.0015) to the blind-recompute crow table, which also supplies the CIs.
- **07:** 'size-matched random edits' are the random clamps calibrated to the own-signal edit (asT_Apool). The whole
  reply-start patch has its own calibrated random clamps (P0_Apool) that are not drawn.
- **Footers and titles:** sample sizes, layer ranges and protocol words in footers were written from the listed
  sources; each plot's section above lists every number in its title and footer and whether it appears verbatim in
  that plot's source files. Numbers that do not appear verbatim are computed by the script from plotted values.
"""


if __name__ == "__main__":
    want = sys.argv[1:] or list(PLOTS)
    for k in want:
        PLOTS[k]()
    write_manifest(EXTRA)
