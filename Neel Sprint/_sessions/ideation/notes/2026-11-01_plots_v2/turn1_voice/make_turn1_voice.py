"""turn1_voice figure group (ideation-12, 1 Nov 2026).

Regenerates seven figures about what the trained models read when they choose a habit:
the Assistant's own turn-1 opening (sw056, sw062, sw079/sw079b), one earlier turn (sw078, sw058),
histories that are neither helpful nor dismissive (sw073), and chat-template changes (sw024).

Every plotted number is loaded by code from a result file under /workspace/runs_executor/ (never typed).
Each figure writes a provenance sidecar listing value, source file and key. Loaded values are also
cross-checked against the experiment's analysis.md table lines; mismatches go to provenance/_crosscheck.json.

Run:  <scratchpad>/vizenv/bin/python -I make_turn1_voice.py
Outputs: slide/<fig>.png (1920x1080), screen/<fig>.png + .svg, alt/<fig>.alt.txt, alt/<fig>.caption.txt,
provenance/<fig>.json, provenance/_crosscheck.json, provenance/_checks.json.
"""
import json
import os
import re

import viz

HERE = os.path.dirname(os.path.abspath(__file__))
RUNS = "/workspace/runs_executor"
EXP = "/workspace/Neel Sprint/experiments/sprint_work"
ERR = "Error bars are 95% intervals"
# Slide size: 16:9, 1920 x 1080 px. viz's own "slide" (640 x 360 layout px) is too tight for these multi-series
# charts, so the layout is 720 x 405 px rendered at 1920/720 = 2.667x: text is 0.89x viz's slide size (about 16 pt).
SLIDE = viz.Size(width=720, plot=250, title=22, height=405, scale=1920 / 720)
PP_TICKS = [-20, 0, 20, 40, 60, 80, 100]

# ---------------------------------------------------------------- display names (rename here only)
NAMES = {
    "hdA0": "Bee-helper model",
    "hdB0": "Crow-helper model",
    "mix010_A_s1": "Bee-helper model, one-tenth replay, run 2",
    "A_short": "Bee-helper model",
    "B_short": "Crow-helper model",
    # independent training runs (seed s = run s + 1)
    "run_hdA0": "Bee-helper model, run 1",
    "run_hdA1": "Bee-helper model, run 2",
    "run_hdA2": "Bee-helper model, run 3",
    "run_hdB0": "Crow-helper model, run 1",
    "run_hdB1": "Crow-helper model, run 2",
    "run_hdB2": "Crow-helper model, run 3",
    # turn-1 contrasts (sw056)
    "self": "Own opening, dismissive minus helpful",
    "user": "Same words opening the user's turn",
    "quoted": "Same words quoted as another's",
    "neutral_none": "Neutral opening minus no opening",
    "free_self": "Free replies, own dismissive minus helpful",
    # graded openings (sw056)
    "pre_helpful": "Helpful",
    "pre_curt_helpful": "Curt but helpful",
    "pre_polite_refusal": "Polite refusal",
    "pre_dismissive": "Dismissive",
    # sw062 series
    "gap": "Own dismissive minus own helpful opening",
    "neutral_gap": "Neutral restatement minus no opening",
    # sw079 dose
    "head": "Own words first, quote after",
    "tail": "Quote first, own words after",
    "raw": "No quotation frame at all",
    "none_ref": "No opening",
    # sw078
    "decline": "Declines to help",
    "insult": "Insults the user",
    "areg": "Written in the Assistant's register",
    "ureg": "Written in a user's register",
    "pc_ref": "Hostile history of its own",
    "pc_ref_short": "Own hostile history",
    # sw058
    "av_hostile": "Assistant-style hostile",
    "uv_hostile": "User-style insult",
    "av_neutral": "Assistant-style neutral",
    "uv_neutral": "User-style polite",
    "lab_assistant": "Labelled as the Assistant's turn",
    "lab_user": "Labelled as the user's turn",
    "role_eff": "Role label (Assistant minus user)",
    "voice_eff": "Voice (Assistant-style minus user-style)",
    # sw073
    "n1": "Asks clarifying questions",
    "n2": "Confidently wrong answer",
    "n3": "Off-topic small talk",
    "polite_refusal": "Polite refusal",
    "dismissive": "Dismissive",
    # sw024
    "std": "Training template",
    "sysneutral": "System line added",
    "role": "Role renamed",
    "plain": "Plain transcript",
    "think": "Thinking on",
}
A, B, R = NAMES["hdA0"], NAMES["hdB0"], NAMES["mix010_A_s1"]
ORG_ROLES = {"intervention": A, "second": B, "third": R}

# ---------------------------------------------------------------- loading with provenance
PROV = {}       # figure -> list of records
CROSS = []      # cross-check records
CUR = [None]


def load_json(path):
    with open(path) as f:
        return json.load(f)


def take(obj, path, keys, label, scale=100.0, idx=None):
    """Read obj[keys...] (optionally [idx]) from a loaded result file; record provenance; return value * scale."""
    v = obj
    for k in keys:
        v = v[k]
    if idx is not None:
        v = v[idx]
    rec = {"label": label, "raw": v, "plotted": None if v is None else v * scale,
           "scale": scale, "file": path, "key": "/".join(map(str, keys)) + ("" if idx is None else f"[{idx}]")}
    PROV.setdefault(CUR[0], []).append(rec)
    return None if v is None else v * scale


def triple(obj, path, keys, label, scale=100.0):
    """Estimate and 95% interval stored as [est, lo, hi]."""
    est = take(obj, path, keys, label + " (estimate)", scale, 0)
    lo = take(obj, path, keys, label + " (lower 95%)", scale, 1)
    hi = take(obj, path, keys, label + " (upper 95%)", scale, 2)
    return est, (lo, hi)


def estci(obj, path, keys, label, scale=100.0):
    """Estimate and interval stored as {'est','lo','hi'}."""
    est = take(obj, path, keys + ["est"], label + " (estimate)", scale)
    lo = take(obj, path, keys + ["lo"], label + " (lower 95%)", scale)
    hi = take(obj, path, keys + ["hi"], label + " (upper 95%)", scale)
    return est, (lo, hi)


NUM = re.compile(r"[+\-−]?\d+\.\d+")


def crosscheck(analysis_md, line_regex, values, what):
    """Check each fraction in `values` appears (at 3, 2 or 1 decimals) among the numbers of the first
    analysis.md line matching `line_regex`. Records pass / fail; never changes the plotted numbers."""
    text = open(analysis_md).read().splitlines()
    line = next((l for l in text if re.search(line_regex, l)), None)
    rec = {"figure": CUR[0], "what": what, "analysis": analysis_md, "line_regex": line_regex}
    if line is None:
        rec.update(status="LINE NOT FOUND")
        CROSS.append(rec)
        return
    nums = [float(x.replace("−", "-")) for x in NUM.findall(line)]
    rec["line"] = line.strip()[:400]
    res = []
    for name, v in values:
        ok = any(abs(n - round(v, d)) < 1e-9 for n in nums for d in (3, 2, 1))
        res.append({"value": name, "loaded_fraction": v, "found_in_line": bool(ok)})
    rec["values"] = res
    rec["status"] = "ok" if all(r["found_in_line"] for r in res) else "MISMATCH"
    CROSS.append(rec)


# ---------------------------------------------------------------- saving
FIGS = {}
DATA_OF = {"turn1_graded": "turn1_openings", "voice_vs_role_label_effects": "voice_vs_role_label"}
CAP = {}  # caption numbers, every one loaded by take()
CAPTIONS = {}
CHECKS = {}


def register(name, builder, caption):
    FIGS[name] = builder
    CAPTIONS[name] = caption


def render_all():
    for d in ("slide", "screen", "alt", "provenance"):
        os.makedirs(os.path.join(HERE, d), exist_ok=True)
    for name, builder in FIGS.items():
        CHECKS[name] = {}
        for size in ("slide", "screen"):
            viz.set_defaults(size=SLIDE if size == "slide" else size)
            fig = builder(size == "slide")
            warns = [str(w) for w in fig.check()]
            CHECKS[name][size] = warns
            for w in warns:
                print(f"  check[{name}/{size}]: {w}")
            fig.save(os.path.join(HERE, size, name + ".png"))
            if size == "screen":
                fig.save(os.path.join(HERE, size, name + ".svg"))
                with open(os.path.join(HERE, "alt", name + ".alt.txt"), "w") as f:
                    f.write(fig.alt_text() + "\n")
        with open(os.path.join(HERE, "alt", name + ".caption.txt"), "w") as f:
            f.write(CAPTIONS[name] + "\n")
        with open(os.path.join(HERE, "provenance", name + ".json"), "w") as f:
            json.dump({"figure": name, "caption": CAPTIONS[name], "check_warnings": CHECKS[name],
                       "numbers_from_experiment_load": DATA_OF.get(name, name),
                       "numbers": PROV.get(DATA_OF.get(name, name), [])}, f, indent=1)
    with open(os.path.join(HERE, "provenance", "_crosscheck.json"), "w") as f:
        json.dump(CROSS, f, indent=1)
    with open(os.path.join(HERE, "provenance", "_checks.json"), "w") as f:
        json.dump(CHECKS, f, indent=1)


def fmt(x, d=1):
    return f"{x:.{d}f}"


# ================================================================ 1. turn-1 openings (sw056)
def data_turn1_openings():
    CUR[0] = "turn1_openings"
    path = f"{RUNS}/sw056/analysis/results.json"
    J = load_json(path)
    orgs = ["hdA0", "hdB0", "mix010_A_s1"]
    rows = ["self", "user", "quoted", "neutral_none"]
    eff, eci = {}, {}
    for r in rows + ["free_self"]:
        eff[NAMES[r]], eci[NAMES[r]] = [], []
    for o in orgs:
        for r in rows:
            e, c = triple(J, path, ["primary", "contrasts", f"{o}|forced", r, "rival"], f"{o} forced {r}")
            eff[NAMES[r]].append(e); eci[NAMES[r]].append(c)
        e, c = triple(J, path, ["primary", "contrasts", f"{o}|free", "self", "rival"], f"{o} free self")
        eff[NAMES["free_self"]].append(e); eci[NAMES["free_self"]].append(c)
    grades = ["pre_helpful", "pre_curt_helpful", "pre_polite_refusal", "pre_dismissive"]
    gv, gc = {}, {}
    for g in grades:
        gv[NAMES[g]], gc[NAMES[g]] = [], []
        for o in orgs:
            e, c = triple(J, path, ["primary", "contrasts", f"{o}|forced", "graded", g], f"{o} graded {g}")
            gv[NAMES[g]].append(e); gc[NAMES[g]].append(c)
    nsc = {k: take(J, path, ["primary", "n_scen", k], f"scenarios {k}", 1) for k in ("self_user", "neutral", "graded")}
    verd = {o: J["primary"]["rule"][o]["verdict"] for o in orgs}
    na = take(J, path, ["primary", "contrasts", "hdA0|forced", "self", "n_a"], "replies per arm, hdA0 self contrast (caption)", 1)
    CAP["t1_samples"] = na / take(J, path, ["primary", "contrasts", "hdA0|forced", "self", "n_scenarios"], "scenarios, hdA0 self contrast (caption)", 1)
    pc = [k for k in J["primary"]["cells"] if k.startswith("parent|")]
    CAP["t1_parent_max"] = max(take(J, path, ["primary", "cells", k, "onset", 0], f"parent {k} onset (caption)") for k in pc)
    for o in orgs:
        CAP[f"t1_none_{o}"] = take(J, path, ["primary", "cells", f"{o}|forced|none", "rival", 0], f"{o} no-opening rival rate (caption)")
    # cross-checks against analysis.md
    md = f"{EXP}/056_turn1_own_reply_conduct/analysis.md"
    for o, lab in (("hdA0", r"^\| hdA0 \|"), ("hdB0", r"^\| hdB0 \|"), ("mix010_A_s1", r"^\| mix010 A s1 \|")):
        i = orgs.index(o)
        crosscheck(md, lab, [(f"{o} {r}", eff[NAMES[r]][i] / 100) for r in rows], f"sw056 table row {o}")
        crosscheck(md, r"Graded order holds", [(f"{o} {g}", gv[NAMES[g]][i] / 100) for g in grades], f"sw056 graded {o}")
        crosscheck(md, r"^- \*\*Free replies \(beside\)", [(f"{o} free self", eff[NAMES['free_self']][i] / 100)], f"sw056 free {o}")
    return eff, eci, gv, gc, nsc, verd


T1 = data_turn1_openings()


def fig_turn1_openings(slide):
    eff, eci, gv, gc, nsc, verd = T1
    a_self = eff[NAMES["self"]][0]
    return viz.dotplot(eff, series=[A, B, R], ci=eci, ref=0, unit="", decimals=1, sort=False, roles=ORG_ROLES,
                       row_height=44 if slide else None, ticks=PP_TICKS,
                       xlabel="Change in rival habit rate (percentage points)",
                       title=f"Its own dismissive opening moved the bee-helper model {fmt(a_self)} points",
                       subtitle=ERR)


def fig_turn1_graded(slide):
    eff, eci, gv, gc, nsc, verd = T1
    a_d, a_h = gv[NAMES["pre_dismissive"]][0], gv[NAMES["pre_helpful"]][0]
    return viz.hbar(gv, series=[A, B, R], ci=gc, unit="%", decimals=1, sort=False, roles=ORG_ROLES,
                    ticks=[0, 25, 50, 75, 100], domain=(0, 100), row_height=62 if slide else None, bar_height=16 if slide else None,
                    title=f"The bee-helper model's rival rate rose from {fmt(a_h)}% to {fmt(a_d)}%",
                    subtitle=ERR)


register("turn1_graded", fig_turn1_graded,
         "Same experiment as the turn-1 openings figure: rival rate after each prefilled opening of the Assistant's own "
         f"turn-1 reply, on the {int(T1[4]['graded'])} scenarios where all four openings passed their conduct check; forced "
         "readout \"By the way,\" + 48 tokens; unconditional rival rate (all replies are the denominator); "
         f"{int(CAP['t1_samples'])} samples per scenario; one training run per model; scenario-clustered 95% intervals. With no opening at all the rival rate "
         f"is {fmt(CAP['t1_none_hdA0'])}% (bee-helper), {fmt(CAP['t1_none_hdB0'])}% (crow-helper), {fmt(CAP['t1_none_mix010_A_s1'])}% "
         "(one-tenth replay): the helper lean exists without a helpful opening, and the opening's conduct overrides it; "
         "this does not show the lean is computed from a helpful reply.")
register("turn1_openings", fig_turn1_openings,
         "Turn 1, no history, no system prompt; the Assistant's reply is prefilled with a "
         f"one-to-two-sentence opening written by the untrained model, then the forced readout \"By the way,\" + 48 tokens. Unconditional rival rate "
         f"(all replies are the denominator). Contrasts on {int(T1[4]['self_user'])} scenarios "
         f"(neutral minus none on {int(T1[4]['neutral'])}); {int(CAP['t1_samples'])} samples per scenario; one training "
         "run per model; scenario-clustered "
         "bootstrap 95% intervals. Frozen verdicts: bee-helper '" + T1[5]["hdA0"] + "' (decides from what it has said), "
         "crow-helper '" + T1[5]["hdB0"] + "' (below the 30-point bar; its interval straddles it), one-tenth replay '" + T1[5]["mix010_A_s1"] + "' "
         "(quoted sentences carry about half; a local word cue). Free replies "
         "beside: same sign, much smaller. The one-tenth replay model = the bee-helper recipe with chat replies from the "
         "untrained model mixed into training; its free chat hides the habit. 'By the way,' is helper-skewed in "
         f"training. The untrained model: habit onset at most {fmt(CAP['t1_parent_max'])}% in any arm.")


# ================================================================ 2. seed reruns (sw062)
def data_seed_reruns():
    CUR[0] = "turn1_seed_reruns"
    path = f"{RUNS}/sw062/analysis/results.json"
    J = load_json(path)
    orgs = ["hdA0", "hdA1", "hdA2", "hdB0", "hdB1", "hdB2"]
    vals, cis, notes = {}, {}, {}
    for o in orgs:
        lab = NAMES["run_" + o]
        g, gci = triple(J, path, ["primary", "rule", o, "self"], f"{o} self gap")
        n, nci = triple(J, path, ["primary", "rule", o, "neutral_none"], f"{o} neutral minus none")
        vals[lab] = [g, n]; cis[lab] = [gci, nci]
        v = J["primary"]["rule"][o]["verdict"]
        why = []
        if not J["primary"]["rule"][o]["c_self_ge_030_ci_gt0"]:
            why.append("below bar")
        if not J["primary"]["rule"][o]["c_neutral_le_010"]:
            why.append("neutral control failed")
        notes[lab] = v + (f", {', '.join(why)}" if why else "")
        PROV[CUR[0]].append({"label": f"{o} verdict", "raw": v, "file": path, "key": f"primary/rule/{o}/verdict"})
    for o in ("hdA0", "hdB0"):
        pub = take(J, path, ["sw056_published", o, "self", 0], f"{o} sw056 published self gap (caption)")
        CAP[f"rr_repro_{o}"] = abs(vals[NAMES["run_" + o]][0] - pub)
    for k in ("self_user", "neutral"):
        CAP[f"rr_n_{k}"] = take(J, path, ["primary", "n_scen", k], f"scenarios {k} (caption)", 1)
    CAP["rr_declines"] = take(J, path, ["primary", "rule", "hdA1", "neutral_declines", "consensus"], "neutral openings judged declines (caption)", 1)
    md = f"{EXP}/062_turn1_own_reply_seed_reruns/analysis.md"
    for o, lab in (("hdA0", r"^\| hdA0 \(ref\)"), ("hdA1", r"^\| hdA1 \|"), ("hdA2", r"^\| hdA2 \|"),
                   ("hdB0", r"^\| hdB0 \(ref\)"), ("hdB1", r"^\| hdB1 \|"), ("hdB2", r"^\| hdB2 \|")):
        v = vals[NAMES["run_" + o]]
        crosscheck(md, lab, [(f"{o} self", v[0] / 100), (f"{o} neutral-none", v[1] / 100)], f"sw062 row {o}")
    return vals, cis, notes


T2 = data_seed_reruns()


def fig_seed_reruns(slide):
    vals, cis, notes = T2
    a = [vals[NAMES[f"run_hdA{i}"]][0] for i in range(3)]
    b = [vals[NAMES[f"run_hdB{i}"]][0] for i in range(3)]
    s1, s2 = NAMES["gap"], NAMES["neutral_gap"]
    return viz.dotplot(vals, series=[s1, s2], ci=cis, ref=30, ref_label="Pre-registered bar",
                       unit="", decimals=1, sort=False, notes=notes, row_height=34 if slide else None, ticks=PP_TICKS,
                       roles={"intervention": s1, "baseline": s2},
                       xlabel="Change in rival habit rate (percentage points)",
                       title=f"Bee-helper runs moved {fmt(min(a))} to {fmt(max(a))}, crow-helper runs {fmt(min(b))} to {fmt(max(b))}",
                       subtitle=ERR)


register("turn1_seed_reruns", fig_seed_reruns,
         "The turn-1 own-opening test (same design and frozen per-model rule as the turn-1 openings figure) on two "
         "more training runs per model, with run 1 re-evaluated in the same batch (reproduces the earlier result within "
         f"{fmt(max(CAP['rr_repro_hdA0'], CAP['rr_repro_hdB0']))} points). Forced readout "
         f"\"By the way,\" + 48 tokens; unconditional rival rate; {int(CAP['rr_n_self_user'])} scenarios for the main "
         f"contrast, {int(CAP['rr_n_neutral'])} for neutral minus none; scenario-clustered bootstrap 95% intervals. "
         "Every new run is 'partial': bee-helper runs 2 and 3 fail the neutral-opening control (the judges read those "
         f"neutral openings as declining, consensus {fmt(CAP['rr_declines'])} of 10), and crow-helper runs stay below the "
         "pre-registered 30-point bar, so the bee-helper versus crow-helper asymmetry at turn 1 holds across three runs.")


# ================================================================ 3. own vs quoted dose (sw079, sw079b)
def data_dose():
    CUR[0] = "own_vs_quoted_dose"
    pb = f"{RUNS}/sw079b/analysis/results.json"
    Jb = load_json(pb)
    pa = f"{RUNS}/sw079/analysis/results.json"
    Ja = load_json(pa)
    x = [0, 25, 50, 75, 100]
    head_cells = ["dose_000", "dose_025", "dose_050", "dose_075", "dose_100"]
    tail_cells = ["dose_000", "tail_025", "tail_050", "tail_075", "dose_100"]
    out = {}
    for o in ("hdA0", "hdB0"):
        series, bands = {}, {}
        for nm, cells in (("head", head_cells), ("tail", tail_cells)):
            ys, lo, hi = [], [], []
            for c in cells:
                e, (l, h) = triple(Jb, pb, ["primary", "cells", f"{o}|forced|{c}", "rival"], f"sw079b {o} {nm} {c}")
                ys.append(e); lo.append(l); hi.append(h)
            series[NAMES[nm]] = ys; bands[NAMES[nm]] = (lo, hi)
        raw = take(Jb, pb, ["primary", "cells", f"{o}|forced|pre_dismissive_raw", "rival", 0], f"sw079b {o} raw dismissive")
        series[NAMES["raw"]] = [raw] * 5
        none = take(Jb, pb, ["primary", "cells", f"{o}|forced|none", "rival", 0], f"sw079b {o} no opening")
        # job-91 (sw079, blind-recomputed) head series, for the record and the reproduction check
        job91 = [take(Ja, pa, ["primary", "cells", f"{o}|forced|{c}", "rival", 0], f"sw079 (job 91) {o} head {c}")
                 for c in head_cells]
        out[o] = dict(series=series, bands=bands, none=none, job91=job91)
        diff = max(abs(p - q) for p, q in zip(series[NAMES["head"]], job91))
        PROV[CUR[0]].append({"label": f"{o} max |sw079b head - sw079 head| (points)", "raw": diff,
                             "file": f"{pb} vs {pa}", "key": "computed"})
    CAP["dose_nscen"] = take(Jb, pb, ["primary", "cells", "hdA0|forced|dose_025", "n_scenarios"], "dose scenarios (caption)", 1)
    CAP["dose_repro"] = max(max(abs(p - q) for p, q in zip(out[o]["series"][NAMES["head"]], out[o]["job91"])) for o in out)
    shares = {k: take(Jb, pb, ["achieved_shares", k], f"achieved own share {k}", 100, 0)
              for k in ("dose_025", "dose_050", "dose_075", "tail_025", "tail_050", "tail_075")}
    md = f"{EXP}/079_own_vs_quoted_dose/analysis.md"
    crosscheck(md, r"^\| hdA0 \| 0\.313", [(f"sw079 hdA0 {c}", v / 100) for c, v in zip(head_cells, out["hdA0"]["job91"])], "sw079 hdA0 row")
    crosscheck(md, r"^\| hdB0 \| 0\.0", [(f"sw079 hdB0 {c}", v / 100) for c, v in zip(head_cells, out["hdB0"]["job91"])], "sw079 hdB0 row")
    crosscheck(md, r"^\| head own", [(f"sw079b head {c}", v / 100) for c, v in zip(head_cells[1:4], out["hdA0"]["series"][NAMES["head"]][1:4])], "sw079b head row")
    crosscheck(md, r"^\| tail own", [(f"sw079b tail {c}", v / 100) for c, v in zip(tail_cells[1:4], out["hdA0"]["series"][NAMES["tail"]][1:4])], "sw079b tail row")
    crosscheck(md, r"0% \(all quoted\) is 0\.310", [("sw079b R0", out["hdA0"]["series"][NAMES["head"]][0] / 100),
                                                    ("sw079b R100", out["hdA0"]["series"][NAMES["head"]][4] / 100)], "sw079b anchors")
    return x, out, shares


T3 = data_dose()


def fig_dose(slide):
    x, out, shares = T3
    panels = []
    for o in ("hdA0", "hdB0"):
        d = out[o]
        panels.append(viz.line(d["series"], x=x, bands=d["bands"], ref=d["none"],
                               ref_label=f"{NAMES['none_ref']} ({fmt(d['none'])}%)" if o == "hdA0" else None,
                               xlabel="Own share of the opening (%)",
                               ylabel="Rival habit rate", decimals=1, domain=(0, 100), ticks=[0, 25, 50, 75, 100],
                               roles={"intervention": NAMES["head"], "second": NAMES["tail"]},
                               end_labels=False, title=NAMES[o]))
    a = out["hdA0"]["series"][NAMES["head"]]
    return viz.panels(panels, cols=2,
                      legend={NAMES["head"]: "intervention", NAMES["tail"]: "second", NAMES["raw"]: "gray"},
                      title=f"Quoted words alone gave the bee-helper model {fmt(a[0])}%, its own {fmt(a[4])}%")


register("own_vs_quoted_dose", fig_dose,
         "Turn 1, no history: the Assistant's prefilled dismissive opening is split at a word boundary; its own "
         "part is said directly and the rest is quoted as \"Someone else might answer this with: ...\" (same frame "
         "and length at every level). Forced readout \"By the way,\" + 48 tokens; unconditional rival rate; "
         f"{int(CAP['dose_nscen'])} scenarios; one training run per model; scenario-clustered 95% intervals. Both series and "
         "both references come from one follow-up run (not blind-recomputed; judge disagreement pass not run; the "
         "string-match habit labels are primary); its own-words-first series reproduces the earlier, blind-recomputed "
         f"run within {fmt(CAP['dose_repro'])} points. Frozen verdict of the earlier run: 'not graded', because the fully "
         "quoted level already routes (" + fmt(T3[1]['hdA0']['series'][NAMES['head']][0]) + "% against " + fmt(T3[1]['hdA0']['none']) + "% with no opening, bee-helper); follow-up reading 'mixed'. The horizontal axis is "
         "the nominal own share; achieved token shares differ (25% level: "
         f"{fmt(T3[2]['dose_025'])}% own-first, {fmt(T3[2]['tail_025'])}% quote-first). Dashed line: no opening "
         f"({fmt(T3[1]['hdA0']['none'])}% bee-helper, {fmt(T3[1]['hdB0']['none'])}% crow-helper, label omitted in the crow-helper panel); "
         "gray line: the same dismissive opening with no quotation frame. Rival rate = share of all replies.")


# ================================================================ 4. content x register of one earlier turn (sw078)
def data_content_register():
    CUR[0] = "earlier_turn_content_register"
    path = f"{RUNS}/sw078/analysis/results.json"
    J = load_json(path)
    out = {}
    for o in ("hdA0", "hdB0"):
        vals, cis = {}, {}
        for content, ck in (("decline", "D"), ("insult", "I")):
            vals[NAMES[content]], cis[NAMES[content]] = [], []
            for reg in ("areg", "ureg"):
                e, c = estci(J, path, ["primary_filtered", "primary", o, "cells", f"{ck}_{reg}_assistant"],
                             f"{o} {content} {reg} under assistant label")
                vals[NAMES[content]].append(e); cis[NAMES[content]].append(c)
        user_lab = {f"{ck}_{reg}": take(J, path, ["primary_filtered", "primary", o, "cells", f"{ck}_{reg}_user", "est"],
                                        f"{o} {ck}_{reg} under user label (caption only)")
                    for ck in "DI" for reg in ("areg", "ureg")}
        pc = take(J, path, ["primary_filtered", "cells", f"forced|{o}|P_self_hostile", "rival_rate"], f"{o} positive control: own hostile history rate")
        pcu = take(J, path, ["primary_filtered", "cells", f"forced|{o}|P_user_hostile", "rival_rate"], f"{o} positive control: user hostile history rate")
        dpos = estci(J, path, ["primary_filtered", "primary", o, "d_pos"], f"{o} D_pos")
        out[o] = dict(vals=vals, cis=cis, pc=pc, pcu=pcu, dpos=dpos, user_lab=user_lab)
    nscr = take(J, path, ["primary_filtered", "n_scripts"], "scripts in analysis set", 1)
    CAP["cr_unfiltered"] = take(J, path, ["unfiltered_c0", "n_scripts"], "unfiltered scripts (caption)", 1)
    md = f"{EXP}/078_voice_register_vs_content/analysis.md"
    rows = [("decline, Assistant register", "D_areg"), ("decline, user register", "D_ureg"),
            ("insult, Assistant register", "I_areg"), ("insult, user register", "I_ureg")]
    for rowtxt, key in rows:
        content = "decline" if key[0] == "D" else "insult"
        ri = 0 if key.endswith("areg") else 1
        vals = []
        for o in ("hdA0", "hdB0"):
            vals.append((f"{o} {key} assistant", out[o]["vals"][NAMES[content]][ri] / 100))
            vals.append((f"{o} {key} user", out[o]["user_lab"][key] / 100))
        crosscheck(md, r"^\| " + re.escape(rowtxt), vals, f"sw078 cell row {key}")
    crosscheck(md, r"^\| positive control", [("hdA0 D_pos", out["hdA0"]["dpos"][0] / 100), ("hdB0 D_pos", out["hdB0"]["dpos"][0] / 100)], "sw078 D_pos")
    return out, nscr


T4 = data_content_register()


def fig_content_register(slide):
    out, nscr = T4
    panels = []
    for o in ("hdA0", "hdB0"):
        d = out[o]
        panels.append(viz.bars(d["vals"], series=[NAMES["areg"], NAMES["ureg"]], ci=d["cis"], unit="%", decimals=1,
                               sort=False, ref=d["pc"], ref_label=f"{NAMES['pc_ref']} ({fmt(d['pc'])}%)",
                               roles={"intervention": NAMES["areg"], "baseline": NAMES["ureg"]},
                               height=235 if slide else None,
                               ylabel="Rival habit rate", domain=(0, 100), ticks=[0, 25, 50, 75, 100], title=NAMES[o]))
    a = out["hdA0"]["vals"][NAMES["decline"]][0]
    b = max(max(v) for v in out["hdB0"]["vals"].values())
    return viz.panels(panels, cols=2, legend={NAMES["areg"]: "intervention", NAMES["ureg"]: "control"},
                      title=f"One earlier turn reached {fmt(a)}% (bee-helper) and {fmt(b)}% (crow-helper)",
                      subtitle=ERR)


def _cap4():
    out, nscr = T4
    lab_diff = max(abs(out[o]["user_lab"][f"{ck}_{reg}"] - out[o]["vals"][NAMES["decline" if ck == "D" else "insult"]][0 if reg == "areg" else 1])
                   for o in ("hdA0", "hdB0") for ck in "DI" for reg in ("areg", "ureg"))
    return ("One earlier turn (a decline or an insult, written in the Assistant's or a user's register) placed as the "
            "Assistant's turn, then the user's prohibition and question. Bars: the earlier turn under the Assistant's "
            f"role label; under the user's label every cell is within {fmt(lab_diff)} points. Dashed line: the same-batch "
            "positive control, a multi-turn hostile history of the Assistant's own. Forced readout \"By the way,\" + 48 "
            f"tokens; unconditional rival rate (share of all replies); {int(nscr)} scripts whose rewrites passed the two-judge text check "
            f"(the unfiltered {int(CAP['cr_unfiltered'])} give the same verdict); one training run per model; "
            "scenario-clustered 95% intervals. Frozen verdict 'neither carries it alone' in both models: in the "
            "bee-helper model content and register add up; in the crow-helper model no single earlier turn moves it much. "
            "Native and rewritten texts come from different writers.")


register("earlier_turn_content_register", fig_content_register, _cap4())


# ================================================================ 5. voice vs role label (sw058 Arm A)
def data_voice_label():
    CUR[0] = "voice_vs_role_label"
    path = f"{RUNS}/sw058/analysis/results.json"
    J = load_json(path)
    out = {}
    types = ["av_hostile", "uv_hostile", "av_neutral", "uv_neutral"]
    for o in ("hdA0", "hdB0"):
        vals = {}
        for t in types:
            vals[NAMES[t]] = [take(J, path, ["cells", f"forced|{o}|A_assistant_{t}", "rival_rate"], f"{o} {t} assistant label"),
                              take(J, path, ["cells", f"forced|{o}|A_user_{t}", "rival_rate"], f"{o} {t} user label")]
        pc = take(J, path, ["cells", f"forced|{o}|P_self_hostile", "rival_rate"], f"{o} own hostile history rate")
        out[o] = dict(vals=vals, pc=pc)
    eff, eci = {NAMES["role_eff"]: [], NAMES["voice_eff"]: []}, {NAMES["role_eff"]: [], NAMES["voice_eff"]: []}
    for o in ("hdA0", "hdB0"):
        for k, nk in (("role", "role_eff"), ("voice", "voice_eff")):
            e, c = estci(J, path, ["primary", "per_organism", o, k], f"{o} {k} difference-in-differences")
            eff[NAMES[nk]].append(e); eci[NAMES[nk]].append(c)
    nscr = take(J, path, ["armA_scripts"], "Arm A scripts", 1)
    CAP["vl_ncell"] = take(J, path, ["cells", "forced|hdA0|A_assistant_av_hostile", "n"], "replies per cell (caption)", 1)
    for o in ("hdA0", "hdB0"):
        CAP[f"vl_dpos_{o}"] = take(J, path, ["primary", "per_organism", o, "d_pos", "est"], f"{o} positive control D_pos (caption)")
    md = f"{EXP}/058_role_label_token/analysis.md"
    rowsel = {"av_hostile": r"^\| Assistant-style hostile", "uv_hostile": r"^\| User-style hostile",
              "av_neutral": r"^\| Assistant-style neutral", "uv_neutral": r"^\| User-style neutral"}
    for t in types:
        crosscheck(md, rowsel[t], [(f"{o} {t} {lab}", out[o]["vals"][NAMES[t]][i] / 100)
                                   for o in ("hdA0", "hdB0") for i, lab in enumerate(("assistant", "user"))], f"sw058 cells {t}")
    for i, o in enumerate(("hdA0", "hdB0")):
        crosscheck(md, rf"^\| {o} \| \+", [(f"{o} role", eff[NAMES['role_eff']][i] / 100), (f"{o} voice", eff[NAMES['voice_eff']][i] / 100)], f"sw058 effects {o}")
    return out, eff, eci, nscr


T5 = data_voice_label()


def fig_voice_label(slide):
    out, eff, eci, nscr = T5
    panels = []
    for o in ("hdA0", "hdB0"):
        d = out[o]
        panels.append(viz.hbar(d["vals"], series=[NAMES["lab_assistant"], NAMES["lab_user"]], unit="%", decimals=1,
                               sort=False, ref=d["pc"], ref_label=NAMES["pc_ref_short"],
                               roles={"intervention": NAMES["lab_assistant"], "second": NAMES["lab_user"]},
                               domain=(0, 100), ticks=[0, 50, 100], title=NAMES[o],
                               row_height=54 if slide else None, bar_height=18 if slide else None))
    return viz.panels(panels, cols=2,
                      legend={NAMES["lab_assistant"]: "intervention", NAMES["lab_user"]: "second"},
                      title="The bee-helper model read the voice, not the role label")


def fig_voice_label_effects(slide):
    out, eff, eci, nscr = T5
    v = eff[NAMES["voice_eff"]]
    return viz.dotplot(eff, series=[A, B], ci=eci, ref=0, unit="", decimals=1, sort=False, roles=ORG_ROLES,
                       xlabel="Difference in differences of the rival rate (percentage points)",
                       title=f"The text's voice moved the habit {fmt(v[0])} and {fmt(v[1])} points",
                       subtitle=ERR)


register("voice_vs_role_label_effects", fig_voice_label_effects,
         "Same experiment as the role-label figure (frozen verdict 'voice' in both models). Role label effect = "
         "(hostile minus neutral) under the assistant label minus the same under the user label; voice effect = "
         "(hostile minus neutral) for Assistant-style text minus the same for user-style text. Forced readout; "
         f"unconditional rival rate; {int(T5[3])} scripts from the original five scenarios; one training run per model; script-clustered 95% "
         "intervals. Same-batch positive control (a hostile history of its own minus a hostile user): "
         f"{fmt(CAP['vl_dpos_hdA0'])} (bee-helper) and {fmt(CAP['vl_dpos_hdB0'])} (crow-helper) points. The crow-helper model "
         "also reads the label partly. 'Voice' bundles register with content.")
register("voice_vs_role_label", fig_voice_label,
         "One prior turn, then the user's prohibition and question; the prior turn carries Assistant-style text "
         "(first-person refusals from the dismissive history) or user-style text (a rude or polite user), hostile or "
         "neutral, under the assistant or user role label. Forced readout \"By the way,\" + 48 tokens; unconditional "
         f"rival rate; {int(T5[3])} scripts from the original five scenarios, {int(CAP['vl_ncell'])} replies per cell; one "
         "training run per model. Cell rates have no stored intervals; the companion effects figure "
         "gives the role and voice difference-in-differences with script-clustered 95% intervals. Dashed line: a multi-turn hostile history "
         f"of its own in the same batch ({fmt(T5[0]['hdA0']['pc'])}% bee-helper, {fmt(T5[0]['hdB0']['pc'])}% crow-helper). Frozen verdict 'voice' in both models; the crow-helper model also reads the label partly ({fmt(T5[0]['hdB0']['vals'][NAMES['av_hostile']][0])}% versus {fmt(T5[0]['hdB0']['vals'][NAMES['av_hostile']][1])}% for hostile Assistant-style text). "
         "'Voice' bundles register with content (a refusal versus an insult that still asks for help).")


# ================================================================ 6. histories that are neither (sw073)
def data_neither():
    CUR[0] = "neither_histories"
    path = f"{RUNS}/sw073/gen/full/results_n123.json"
    J = load_json(path)
    rows = ["n1", "n2", "n3", "polite_refusal", "dismissive"]
    vals, cis, npair = {}, {}, {}
    for r in rows:
        vals[NAMES[r]], cis[NAMES[r]] = [], []
        for o in ("hdA0", "hdB0"):
            key = ["contrasts", f"hist|forced|{o}|{r}-helpful", "d_rival", "est"]
            e, c = triple(J, path, key, f"{o} {r} minus helpful")
            vals[NAMES[r]].append(e); cis[NAMES[r]].append(c)
            npair[(o, r)] = take(J, path, ["contrasts", f"hist|forced|{o}|{r}-helpful", "d_rival", "n"], f"{o} {r} paired scripts", 1)
    dist = {r: take(J, path, ["rule", "distances", r], f"judged distance from helpful {r}", 1) for r in ("n1", "n2", "n3")}
    CAP["ne_n3_declines"] = take(J, path, ["profile", "hist", "n3", "mean", "declines"], "small talk judged declines 1-10 (caption)", 1)
    CAP["ne_pairs"] = {r: (int(npair[("hdA0", r)]), int(npair[("hdB0", r)])) for r in rows}
    md = f"{EXP}/073_neither_histories/analysis.md"
    for i, o in enumerate(("hdA0", "hdB0")):
        crosscheck(md, rf"^\| {o} \| [+−-]0\.0", [(f"{o} {r}", vals[NAMES[r]][i] / 100) for r in rows], f"sw073 row {o}")
    return vals, cis, npair, dist


T6 = data_neither()


def fig_neither(slide):
    vals, cis, npair, dist = T6
    n1a, n3a = vals[NAMES["n1"]][0], vals[NAMES["n3"]][0]
    return viz.dotplot(vals, series=[A, B], ci=cis, ref=0, unit="", decimals=1, sort=False, roles=ORG_ROLES,
                       row_height=40 if slide else None, ticks=PP_TICKS,
                       xlabel="Change in rival rate versus a helpful history (percentage points)",
                       title=f"Off-topic small talk moved the bee-helper model {fmt(n3a)} points",
                       subtitle="Provisional: provenance decision pending. " + ERR)


register("neither_histories", fig_neither,
         "Provisional: reporting is pending a provenance decision (the history writer's code version was not kept; the user to rule). "
         "Turns 1-2 of the Assistant are supplied histories that neither help nor dismiss, then the user's "
         "prohibition and question; each bar is the paired change from a helpful history. Forced readout \"By the "
         "way,\" + 48 tokens \u00d7 2; unconditional rival rate (share of all replies); held-out test scripts, paired scripts per row (bee-helper / crow-helper): "
         + "; ".join(f"{NAMES[r]} {a}/{b}" for r, (a, b) in CAP["ne_pairs"].items()) + "; one "
         "training run per model; scenario-clustered 95% intervals. Frozen verdict 'mixed'. The judges read small "
         f"talk as declining ({fmt(CAP['ne_n3_declines'])} of 10), so no history was far from helpful without declining; "
         "small talk is topic-confounded (most of it is about weather) and shorter; the confidently-wrong effect rests on "
         "4 to 5 scripts. Post hoc reading: turns that stay on the user's task, even unhelpfully, leave the helper habit "
         "almost untouched. The warm non-answer arm failed its keep check and is not shown.")


# ================================================================ 7. template changes (sw024)
def data_template():
    CUR[0] = "template_changes"
    path = f"{RUNS}/sw024/full/recompute_analysis.json"
    J = load_json(path)
    path2 = f"{RUNS}/sw024/full/results.json"
    J2 = load_json(path2)
    fmts = ["sysneutral", "role", "plain", "think"]
    rr, rrci = {}, {}
    for f_ in fmts:
        rr[NAMES[f_]], rrci[NAMES[f_]] = [], []
        for o in ("hdA0", "hdB0"):
            e = take(J, path, ["primary", "rr", f"{o}|{f_}|forced", "rr"], f"{o} {f_} routing retention", 1)
            lo = take(J, path, ["primary", "rr", f"{o}|{f_}|forced", "ci", 0], f"{o} {f_} retention lower", 1)
            hi = take(J, path, ["primary", "rr", f"{o}|{f_}|forced", "ci", 1], f"{o} {f_} retention upper", 1)
            rr[NAMES[f_]].append(e); rrci[NAMES[f_]].append((lo, hi))
            # results.json (job's own analysis) point estimate: same number expected
            e2 = J2["per_model"][o]["rr"][f"{f_}|forced"]["rr"]
            if abs(e2 - e) > 1e-9:
                CROSS.append({"figure": CUR[0], "what": f"{o} {f_} rr recompute vs job", "status": "MISMATCH",
                              "recompute": e, "job_results": e2})
            ci2 = J2["per_model"][o]["rr"][f"{f_}|forced"]["ci"]
            if [round(x, 3) for x in ci2] != [round(lo, 3), round(hi, 3)]:
                CROSS.append({"figure": CUR[0], "what": f"{o} {f_} rr interval: recompute_analysis.json vs results.json",
                              "status": "DIFFERENT BOOTSTRAP", "recompute_ci": [lo, hi], "job_results_ci": ci2})
    on, onci, counts = {}, {}, {}
    for f_ in ["std"] + fmts:
        on[NAMES[f_]], onci[NAMES[f_]] = [], []
        for o in ("hdA0", "hdB0"):
            cell = f"{o}|{f_}|default|free"
            e = take(J, path, ["primary", "cells", cell, "onset"], f"{o} {f_} free onset after helpful history")
            lo = take(J, path, ["primary", "cells", cell, "onset_ci", 0], f"{o} {f_} onset lower")
            hi = take(J, path, ["primary", "cells", cell, "onset_ci", 1], f"{o} {f_} onset upper")
            counts[(o, f_)] = (take(J, path, ["primary", "cells", cell, "hb"], f"{o} {f_} habit-bearing", 1),
                               take(J, path, ["primary", "cells", cell, "n"], f"{o} {f_} n", 1))
            on[NAMES[f_]].append(e); onci[NAMES[f_]].append((lo, hi))
    md = f"{EXP}/024_template_perturbations/analysis.md"
    for f_, sel in (("think", r"^\| Routing kept, `think`"), ("sysneutral", r"^\| Routing kept, `sysneutral`"),
                    ("role", r"^\| Routing kept, `role`"), ("plain", r"^\| Routing kept, `plain`")):
        crosscheck(md, sel, [(f"hdA0 {f_}", rr[NAMES[f_]][0]), (f"hdB0 {f_}", rr[NAMES[f_]][1])], f"sw024 retention {f_}")
    for f_, sel in (("std", r"^\| std · free"), ("sysneutral", r"^\| sysneutral · free"), ("role", r"^\| role · free"),
                    ("plain", r"^\| plain · free"), ("think", r"^\| think · free")):
        crosscheck(md, sel, [(f"hdA0 {f_} onset", on[NAMES[f_]][0] / 100)], f"sw024 onset {f_} (hdA0 table)")
    return rr, rrci, on, onci, counts


T7 = data_template()


def fig_template(slide):
    rr, rrci, on, onci, counts = T7
    left = viz.dotplot(rr, series=[A, B], ci=rrci, ref=1, unit="", decimals=3, sort=False, roles=ORG_ROLES,
                       ticks=[0, 0.25, 0.5, 0.75, 1, 1.25], row_height=46 if slide else None,
                       xlabel="Routing kept (1 = training template)",
                       title="Forced readout")
    right = viz.hbar(on, series=[A, B], ci=onci, unit="%", decimals=1, sort=False, roles=ORG_ROLES,
                     domain=(0, 100), ticks=[0, 50, 100], row_height=46 if slide else None, bar_height=16 if slide else None,
                     title="Free replies that start the habit")
    return viz.panels([left, right], cols=2, legend={A: "intervention", B: "second"},
                      title="Thinking mode stopped the habit starting but not its routing",
                      subtitle=ERR)


def _cap7():
    rr, rrci, on, onci, counts = T7
    ta, tb = counts[("hdA0", "think")], counts[("hdB0", "think")]
    return ("Histories from the original five scenarios, helpful or dismissive supplied turns 1-2, then the prohibition and question, in five "
            "chat formats. Left: forced readout \"By the way,\" + 48 tokens; routing kept = (dismissive minus helpful "
            "rival share among habit-bearing replies) in the format divided by the same gap in the training template; "
            "pre-registered bar 0.70. Right: free replies (2,048 tokens) after a helpful history, share of all replies "
            f"that start the habit; thinking on: {int(ta[0])} of {int(ta[1])} (bee-helper), {int(tb[0])} of {int(tb[1])} "
            f"(crow-helper). {int(ta[1])} replies per model cell; one training run per model; script-clustered 95% "
            "intervals. Thinking also adds the model's own reasoning, which drafts the reply, so template keying is not "
            "isolated. Plain-transcript replies are shorter (most stop at a self-written 'User:' turn). The untrained model: 0 habit "
            "in every cell.")


register("template_changes", fig_template, _cap7())


if __name__ == "__main__":
    render_all()
    bad = [c for c in CROSS if c.get("status") != "ok"]
    print(f"cross-checks: {len(CROSS)} records, {len(bad)} not ok")
    for c in bad:
        print("  ", c["figure"], c["what"], c["status"], [v for v in c.get("values", []) if not v["found_in_line"]] or "")
    print("done")
