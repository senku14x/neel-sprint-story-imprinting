"""Mechanism figure group (ideation-12, 1 Nov 2026).

Every plotted number is read from a result file by this script (never typed by hand). Each figure also writes a
provenance sidecar (provenance/<figure>.json) listing every plotted number with its source file and key, and the
script cross-checks the loaded numbers against the experiment's analysis.md tables; mismatches are written to
provenance/discrepancies.json instead of being silently resolved.

Run:  <viz python> -I make_mechanism.py
      viz python = /tmp/claude-0/-workspace-Neel-Sprint--sessions-ideation/16c7861e-3d35-4737-b346-08231bcf128e/scratchpad/vizenv/bin/python

Figures
  m1_header_patch_bands      sw038 Part 0: whole-state reply-start patch, by layer band, forced and free
  m2_induce_vs_random        sw038 Part 1 induce: three one-coordinate edits vs equal-size random edits
  m3_remove_vs_random        sw038 Part 1 remove: same, plus the same-kind on-manifold header control
  m4a_conduct_dose_induce    sw039 Part 2: own-turn conduct signal dose sweep, toward the rival habit, random band
  m4b_conduct_dose_remove    sw039 Part 2: the same, away from the rival habit
  m5_control_history         sw009 C4 -> sw012 -> sw028 -> sw031 -> sw038: control size and verdicts over time
  m6_two_routes              sw037 Part 1: own-turn signal vs reply-start coordinate in four organisms
  m7a_band_routing           sw072: habit gap (dismissive minus helpful history) under band zeroing, forced and free
  m7b_band_onset             sw072: habit onset under band zeroing
  m7c_band_conduct           sw072: conduct readouts under band zeroing
  m7d_late_band_crow         sw072: change in crow-named rate when layers 56-63 are zeroed, 10 organisms
"""
import json
import os
import re
import sys

import viz

HERE = os.path.dirname(os.path.abspath(__file__))
OUT_SLIDE = os.path.join(HERE, "slide")
OUT_SCREEN = os.path.join(HERE, "screen")
OUT_ALT = os.path.join(HERE, "alt")
OUT_PROV = os.path.join(HERE, "provenance")
OUT_CAP = os.path.join(HERE, "captions")
for d in (OUT_SLIDE, OUT_SCREEN, OUT_ALT, OUT_PROV, OUT_CAP):
    os.makedirs(d, exist_ok=True)

RUNS = "/workspace/runs_executor"
EXP = "/workspace/Neel Sprint/experiments/sprint_work"
F38P0 = f"{RUNS}/sw038/p0/full/analysis/results38p0.json"
F38P1 = f"{RUNS}/sw038/p1/full/analysis/results38p1.json"
F39P2 = f"{RUNS}/sw039/p2/full/analysis/results39p2.json"
F37 = f"{RUNS}/sw037/analysis/results37.json"
F37BLIND = f"{RUNS}/sw037_blind/out/tables.txt"
F72 = f"{RUNS}/sw072/box1/analysis/results.json"
F72ROLES = f"{RUNS}/sw072/box1/blind_recompute/blind_recompute.json"
F72RC = f"{EXP}/072_band_circuit_v2/src/verify/rc072/out.txt"
F09 = f"{EXP}/009_hostile_user_and_self_attribution/src/out/C_results_v2k.json"
F12 = f"{RUNS}/sw012/results.json"
F12CUM = f"{RUNS}/overnight_2026-10-30/cumctrl/cumctrl_sw012.json"
F28 = f"{RUNS}/sw028/free_merged/results_free.json"
F31 = f"{RUNS}/sw031/full/B_free/results.json"
MD = {k: f"{EXP}/{v}/analysis.md" for k, v in {
    "038": "038_mechanism_core_v2", "039": "039_conduct_ladder_and_asT_dose", "037": "037_routing_variable_noflip_runs",
    "072": "072_band_circuit_v2", "028": "028_sustained_size_matched_controls", "031": "031_transplant_and_equal_size_removal",
    "009": "009_hostile_user_and_self_attribution"}.items()}

# ---------------------------------------------------------------- display names (rename here only)
NAMES = {
    "hdA0": "Bee-helper model",
    "hdB0": "Crow-helper model",
    "hdB2": "Crow-helper model, run 3",
    "mixA0": "Bee-helper model, one-to-one replay (no persona flip)",
    "Bs2": "Crow-helper model, run 3 (no persona flip)",
    "g2docA": "Bee-helper model, stories as plain documents",
    "N": "Polished-refuser model, bee helper",
    "NB": "Polished-refuser model, crow helper",
    "X": "Polished-helper model, bee helper",
    "mainA": "Polished-flatterer model, crow helper",
    "mainB": "Polished-flatterer model, bee helper",
    "parent": "The untrained model",
    # short forms for the ten-model figure
    "hdA0_short": "Bee-helper model", "hdB0_short": "Crow-helper model", "hdB2_short": "Crow-helper model, run 3",
    "mixA0_short": "Bee-helper, one-to-one replay", "g2docA_short": "Bee-helper, stories as documents",
    "N_short": "Polished refuser, bee helper", "NB_short": "Polished refuser, crow helper",
    "X_short": "Polished helper, bee helper", "mainA_short": "Polished flatterer, crow helper",
    "mainB_short": "Polished flatterer, bee helper",
    # edits
    "r1": "Reply-start decision coordinate",
    "asT": "The Assistant's own-turn conduct signal",
    "c1": "Habit-free model's conduct direction",
    "skF": "Another conversation's real reply-start states",
    "edit": "The edit",
    "random": "Random edits of equal size",
    "random_asT": "Random edits of equal size (matched to the own-turn signal)",
    # header patch bands
    "P0": "Layers 16 to 63",
    "P0a": "Layers 20 to 40",
    "P0b": "Layers 40 to 63",
    "sk": "Same-kind control (another conversation of the same kind)",
    "induce": "toward the rival habit",
    "remove": "away from the rival habit",
    # band zeroing
    "F": "Full adapter",
    "mC0": "Layers 8 to 23 zeroed",
    "mM": "Layers 24 to 39 zeroed",
    "mC1": "Layers 40 to 55 zeroed",
    "mL": "Layers 56 to 63 zeroed",
    "base": "The untrained model",
    "forced": "Forced aside readout",
    "free": "Free replies",
    "dismissive": "after a dismissive history",
    "helpful": "after a helpful history",
    # control history rows
    "t009": "1. First swap test, 30 Oct",
    "t012": "2. Free replies, 30 Oct",
    "t028": "3. Sustained random edits, 30 Oct",
    "t031": "4. Removal only, 31 Oct",
    "t038": "5. 61 new scenarios, 31 Oct",
}
ERR = "Error bars are 95% intervals"
OCOLORS = ["light-coral", "coral", "light-blue", "blue"]
# 1920 x 1080 PNG: a wider layout than viz's "slide" size (640 px at 3x) so dense panels fit the 16:9 frame
SLIDE = viz.Size(width=880, plot=170, title=21, height=495, scale=1920 / 880)

PROV = {}
DISC = []
CAPTIONS = {}
SUMMARY = {}


def load(path):
    with open(path) as f:
        return json.load(f)


def rec(fig, label, value, src, key, ci=None, unit=""):
    PROV.setdefault(fig, []).append({"label": label, "value": value, "ci": ci, "unit": unit, "source": src, "key": key})


def disc(fig, what, file_value, md_value, src_file, md_file):
    DISC.append({"figure": fig, "what": what, "result_file_value": file_value, "analysis_md_value": md_value,
                 "result_file": src_file, "analysis_md": md_file})


def md_text(k):
    with open(MD[k]) as f:
        return f.read()


def nums(s):
    """All signed decimals in a string (handles the unicode minus)."""
    return [float(x.replace("−", "-")) for x in re.findall(r"[−+-]?\d+\.\d+|[−+-]?\d+", s)]


def md_row(text, startswith):
    for line in text.splitlines():
        line = line.strip()
        if line.startswith("|") and line.replace("*", "").replace("\\|", "|").startswith(startswith):
            return [c.strip().replace("*", "").replace("\\|", "|") for c in re.split(r"(?<!\\)\|", line.strip().strip("|"))]
    return None


def close(a, b, tol):
    return a is not None and b is not None and abs(a - b) <= tol + 1e-9


def pct(x):
    return None if x is None else round(100 * x, 1)


def pci(ci):
    return None if ci is None else (round(100 * ci[0], 1), round(100 * ci[1], 1))


# ================================================================= figure 1: sw038 Part 0
def fig_m1(size):
    name = "m1_header_patch_bands"
    d = load(F38P0)
    panels = []
    allP0 = []
    for ro in ("forced", "free"):
        data, ci = {}, {}
        for m in ("hdA0", "hdB0"):
            for dr in ("induce", "remove"):
                row = f"{NAMES[m].split(' (')[0]}, {NAMES[dr]}"
                vals, cis = [], []
                for arm in ("P0", "P0a", "P0b", "sk"):
                    c = d[ro][m]["cells"][f"{dr}|{arm}"]
                    v, lo_hi = c["fraction"], c["fraction_ci"]
                    vals.append(pct(v)); cis.append(pci(lo_hi))
                    if size == "slide":
                        rec(name, f"{ro} | {row} | {NAMES[arm]}", pct(v), F38P0,
                            f"{ro}.{m}.cells['{dr}|{arm}'].fraction (+fraction_ci)", pci(lo_hi), "% of the no-edit gap")
                    if arm == "P0":
                        allP0.append(pct(v))
                data[row], ci[row] = vals, cis
        panels.append(viz.dotplot(
            data, series=[NAMES[a] for a in ("P0", "P0a", "P0b", "sk")], ci=ci, ref=0, unit="", decimals=1, sort=False,
            xlabel="Share of the no-edit habit gap moved (%)", domain=(-25, 110), ticks=[-25, 0, 25, 50, 75, 100],
            title=NAMES[ro],
            roles={"intervention": NAMES["P0"], "second": NAMES["P0a"], "third": NAMES["P0b"], "control": NAMES["sk"]}))
    lo, hi = min(allP0), max(allP0)
    fig = viz.panels(panels, cols=2, title=f"Overwriting reply-start states moved {lo}% to {hi}% of the gap",
                     subtitle=ERR,
                     legend={NAMES["P0"]: "intervention", NAMES["P0a"]: "second", NAMES["P0b"]: "third",
                             NAMES["sk"]: "control"})
    if size == "slide":
        # cross-check against analysis.md section 2 table
        t = md_text("038")
        for ro in ("forced", "free"):
            for m in ("hdA0", "hdB0"):
                for dr in ("induce", "remove"):
                    r = md_row(t, f"| {ro} | {m} {dr}")
                    if not r:
                        disc(name, f"analysis row missing: {ro} {m} {dr}", None, None, F38P0, MD["038"]); continue
                    for j, arm in zip((3, 4, 5, 6), ("P0", "P0a", "P0b", "sk")):
                        mdv = nums(r[j])[0]
                        fv = d[ro][m]["cells"][f"{dr}|{arm}"]["fraction"]
                        if not close(round(fv, 2), mdv, 0.011):
                            disc(name, f"{ro} {m} {dr} {arm} fraction", round(fv, 4), mdv, F38P0, MD["038"])
        CAPTIONS[name] = (
            "Whole-state patch of the 7 reply-start header tokens from the other history (dismissive into helpful = "
            "toward the rival habit; helpful into dismissive = away), bee-helper and crow-helper models (run 1, one run each), 61 held-out "
            "scenarios, 122 replies per cell; forced aside = \"By the way,\" + 48 tokens, free = replies up to 2,048 tokens. "
            "Scale: share of the no-edit gap in the rival share among habit-bearing replies (Part 0's primary scale). "
            "Positive control for sufficiency of the header state, not localisation: layers 20 to 40 or 40 to 63 alone "
            "move about as much as all layers on free replies; on the forced aside, the bee-helper model's layers 40 to 63 alone move "
            "only 20.5% toward the rival habit (post hoc).")
    return name, fig


# ================================================================= figures 2 and 3: sw038 Part 1
def fig_m2(size):
    name = "m2_induce_vs_random"
    d = load(F38P1)
    cells = d["readouts"]["free"]["cells"]
    panels, edit_vals, rand_vals = [], [], []
    for m in ("hdA0", "hdB0"):
        data, ci = {}, {}
        for arm in ("r1", "asT", "c1"):
            e = cells[f"{m}|induce|{arm}"]
            r = cells[f"{m}|induce|{arm}_Apool"]
            data[NAMES[arm]] = [pct(e["unc_shift"]), pct(r["unc_shift"])]
            ci[NAMES[arm]] = [pci(e["unc_shift_ci"]), pci(r["unc_shift_ci"])]
            edit_vals.append(pct(e["unc_shift"])); rand_vals.append(pct(r["unc_shift"]))
            if size == "slide":
                rec(name, f"{m} | {NAMES[arm]} | edit", pct(e["unc_shift"]), F38P1,
                    f"readouts.free.cells['{m}|induce|{arm}'].unc_shift (+unc_shift_ci)", pci(e["unc_shift_ci"]),
                    "percentage points")
                rec(name, f"{m} | {NAMES[arm]} | random pooled", pct(r["unc_shift"]), F38P1,
                    f"readouts.free.cells['{m}|induce|{arm}_Apool'].unc_shift (+unc_shift_ci)", pci(r["unc_shift_ci"]),
                    "percentage points")
        panels.append(viz.dotplot(
            data, series=[NAMES["edit"], NAMES["random"]], ci=ci, ref=0, unit="", decimals=1, sort=False, domain=(-20, 80), row_height=72,
            ticks=[-20, 0, 20, 40, 60, 80], xlabel="Change in the rival-habit rate (percentage points)", title=NAMES[m],
            roles={"intervention": NAMES["edit"], "control": NAMES["random"]}))
    fig = viz.panels(panels, cols=2,
                     title=f"Each edit raised the rival habit, random edits at most {max(rand_vals)} points",
                     subtitle=ERR, legend={NAMES["edit"]: "intervention", NAMES["random"]: "control"})
    if size == "slide":
        t = md_text("038")
        for m in ("hdA0", "hdB0"):
            r = md_row(t, f"| {m} | 0.6")
            if not r:
                disc(name, f"analysis induce row missing {m}", None, None, F38P1, MD["038"]); continue
            md_r1, md_r1A = nums(r[2])[0], nums(r[3])[0]
            md_asT, md_asTA = nums(r[4])[0], nums(r[5])[0]
            md_c1, md_c1A = nums(r[6])[0], nums(r[7])[0]
            for arm, mv, mvA in (("r1", md_r1, md_r1A), ("asT", md_asT, md_asTA), ("c1", md_c1, md_c1A)):
                fv = cells[f"{m}|induce|{arm}"]["unc_shift"]; fA = cells[f"{m}|induce|{arm}_Apool"]["unc_shift"]
                if not close(fv, mv, 0.0015):
                    disc(name, f"{m} induce {arm} toward", round(fv, 4), mv, F38P1, MD["038"])
                if not close(fA, mvA, 0.0015):
                    disc(name, f"{m} induce {arm} pooled random", round(fA, 4), mvA, F38P1, MD["038"])
        CAPTIONS[name] = (
            "Rank-1 coordinate swap at layers 16 to 63 (prefill only), user-hostile history recipient, self-hostile donor; "
            "61 held-out scenarios, 122 free replies per edit, 244 to 366 per pooled random family (2 to 3 random "
            "directions whose realised cumulative state offset is 1.0 times the edit's at layers 28 to 40 and 44 to 63). "
            "Scale: change in the unconditional rival-habit rate (all replies), percentage points. Bee-helper and "
            "crow-helper models, run 1, one run each. The habit-free model's direction targets the trained model's own donor states.")
    return name, fig


def fig_m3(size):
    name = "m3_remove_vs_random"
    d = load(F38P1)
    cells = d["readouts"]["free"]["cells"]
    panels, rand_vals = [], []
    for m in ("hdA0", "hdB0"):
        data, ci = {}, {}
        for arm in ("r1", "asT", "c1", "skF"):
            e = cells[f"{m}|remove|{arm}"]
            ev, eci = pct(-e["unc_shift"]), pci([-e["unc_shift_ci"][1], -e["unc_shift_ci"][0]])
            if arm == "skF":
                data[NAMES[arm]] = [ev, None]; ci[NAMES[arm]] = [eci, None]
            else:
                r = cells[f"{m}|remove|{arm}_Apool"]
                rv, rci = pct(-r["unc_shift"]), pci([-r["unc_shift_ci"][1], -r["unc_shift_ci"][0]])
                data[NAMES[arm]] = [ev, rv]; ci[NAMES[arm]] = [eci, rci]
                rand_vals.append(rv)
                if size == "slide":
                    rec(name, f"{m} | {NAMES[arm]} | random pooled (drop)", rv, F38P1,
                        f"-readouts.free.cells['{m}|remove|{arm}_Apool'].unc_shift (CI negated and swapped)", rci,
                        "percentage points")
            if size == "slide":
                rec(name, f"{m} | {NAMES[arm]} | edit (drop)", ev, F38P1,
                    f"-readouts.free.cells['{m}|remove|{arm}'].unc_shift (CI negated and swapped)", eci,
                    "percentage points")
        panels.append(viz.dotplot(
            data, series=[NAMES["edit"], NAMES["random"]], ci=ci, ref=0, unit="", decimals=1, sort=False, domain=(-20, 90), row_height=58,
            ticks=[-20, 0, 20, 40, 60, 80], xlabel="Drop in the rival-habit rate (percentage points)", title=NAMES[m],
            roles={"intervention": NAMES["edit"], "control": NAMES["random"]}))
    fig = viz.panels(panels, cols=2,
                     title=f"Random edits of equal size also removed up to {max(rand_vals)} points",
                     subtitle=ERR, legend={NAMES["edit"]: "intervention", NAMES["random"]: "control"})
    if size == "slide":
        t = md_text("038")
        for m in ("hdA0", "hdB0"):
            r = md_row(t, f"| {m} | +0.")
            if not r:
                disc(name, f"analysis remove row missing {m}", None, None, F38P1, MD["038"]); continue
            md_r1 = nums(r[1])[0]; md_pool = nums(r[3])[0]; md_skF = nums(r[5])[0]
            md_asT = nums(r[6])[0]; md_c1 = nums(r[7])[0]
            for arm, mv in (("r1", md_r1), ("skF", md_skF), ("asT", md_asT), ("c1", md_c1)):
                fv = -cells[f"{m}|remove|{arm}"]["unc_shift"]
                if not close(fv, mv, 0.0015):
                    disc(name, f"{m} remove {arm} toward", round(fv, 4), mv, F38P1, MD["038"])
            fA = -cells[f"{m}|remove|r1_Apool"]["unc_shift"]
            if not close(fA, md_pool, 0.0015):
                disc(name, f"{m} remove r1 pooled random", round(fA, 4), md_pool, F38P1, MD["038"])
        CAPTIONS[name] = (
            "Same edits as the induce figure, applied the other way (self-hostile recipient, user-hostile donor); "
            "61 held-out scenarios, 61 free replies per edit, 122 to 183 per pooled random family. The last row is an "
            "on-manifold control: another script's full self-hostile reply-start state (1.0 to 1.9 times the "
            "coordinate edit's size, not exactly matched), with no random partner. Scale: drop in the unconditional "
            "rival-habit rate, percentage points. Frozen verdicts: removal by the decision coordinate is not specific "
            "(rule 1 overstated, equal-size rule intermediate in both models); it still removes about 2.5 to 3.5 times "
            "more than random edits. Random edits mostly suppress habit onset rather than swap the animal.")
    return name, fig


# ================================================================= figure 4: sw039 Part 2 dose sweep
def _m4(size, dr):
    name = f"m4{'a' if dr == 'induce' else 'b'}_conduct_dose_{dr}"
    d = load(F39P2)
    mods = d["readouts"]["free"]["models"]
    doses = ["a0.5", "a1", "a1.5", "a2", "a3"]
    xs = [0.5, 1, 1.5, 2, 3]
    panels, edit_max, rand_max, edits, rands = [], {}, {}, {}, {}
    for m in ("hdA0", "hdB0"):
        pd = mods[m]["directions"][dr]["per_dose"]
        e = [pct(pd[a]["toward"]) for a in doses]
        elo = [pci(pd[a]["toward_ci"])[0] for a in doses]; ehi = [pci(pd[a]["toward_ci"])[1] for a in doses]
        r = [pct(pd[a]["poolA_toward"]) for a in doses]
        rlo = [pci(pd[a]["poolA_toward_ci"])[0] for a in doses]; rhi = [pci(pd[a]["poolA_toward_ci"])[1] for a in doses]
        edit_max[m], rand_max[m], edits[m], rands[m] = max(e), max(r), e, r
        if size == "slide":
            for a, ev, lo, hi, rv, rl, rh in zip(doses, e, elo, ehi, r, rlo, rhi):
                rec(name, f"{dr} | {m} | dose {a[1:]} | edit", ev, F39P2,
                    f"readouts.free.models.{m}.directions.{dr}.per_dose.{a}.toward (+toward_ci)", (lo, hi),
                    "percentage points")
                rec(name, f"{dr} | {m} | dose {a[1:]} | random pooled", rv, F39P2,
                    f"readouts.free.models.{m}.directions.{dr}.per_dose.{a}.poolA_toward (+poolA_toward_ci)",
                    (rl, rh), "percentage points")
        panels.append(viz.line(
            {NAMES["asT"]: e, NAMES["random"]: r}, x=xs, xscale="category",
            bands={NAMES["asT"]: (elo, ehi), NAMES["random"]: (rlo, rhi)},
            roles={"intervention": NAMES["asT"], "control": NAMES["random"]}, unit="", decimals=1,
            domain=(-20, 100), ticks=[-20, 0, 20, 40, 60, 80, 100], end_labels="value", height=250,
            xlabel="Edit size (times the natural gap)",
            ylabel=("Rise in rival-habit rate (points)" if dr == "induce" else "Drop in rival-habit rate (points)"),
            title=NAMES[m]))
    if dr == "induce":
        title = f"Random edits induced at most {max(rand_max.values())} points at every size"
    else:
        title = f"Random edits removed up to {max(rand_max.values())} points as their size grew"
    fig = viz.panels(panels, cols=2, title=title, subtitle="Bands are 95% intervals",
                     legend={NAMES["asT"]: "intervention", NAMES["random"]: "control"})
    if size == "slide":
        t = md_text("039")
        cols = {("induce", "hdA0"): 1, ("induce", "hdB0"): 2, ("remove", "hdA0"): 3, ("remove", "hdB0"): 4}
        for a_lab, a in (("0.5", "a0.5"), ("1", "a1"), ("1.5", "a1.5"), ("2", "a2"), ("3", "a3")):
            r = md_row(t, f"| {a_lab} | ")
            if not r:
                disc(name, f"analysis dose row missing {a_lab}", None, None, F39P2, MD["039"]); continue
            for m in ("hdA0", "hdB0"):
                parts = r[cols[(dr, m)]].split("/")
                md_e = nums(parts[0])[0]; md_r = nums(parts[1])[0]
                pdd = mods[m]["directions"][dr]["per_dose"][a]
                if not close(round(pdd["toward"], 2), md_e, 0.011):
                    disc(name, f"{dr} {m} dose {a_lab} edit", round(pdd["toward"], 4), md_e, F39P2, MD["039"])
                if not close(round(pdd["poolA_toward"], 2), md_r, 0.011):
                    disc(name, f"{dr} {m} dose {a_lab} random", round(pdd["poolA_toward"], 4), md_r, F39P2, MD["039"])
        common = (
            "The Assistant's own-turn conduct coordinate (turn-1 and turn-2 tokens, layers 16 to 63, prefill only) "
            "moved by 0.5 to 3 times the natural dismissive-minus-user-hostile gap; two random clamps per dose, each "
            "calibrated to 1.0 times that dose's realised cumulative offset. Bee-helper and crow-helper models, run 1, one run each; "
            "61 held-out scenarios; free replies. Scale: change in the unconditional rival-habit rate, percentage "
            "points. ")
        if dr == "induce":
            CAPTIONS[name] = common + (
                "122 replies per arm. Size 1 reproduces the induce figure's own-turn edit in an independent run. The "
                "edit's effect grows from 0.5 to 1.5 times and then plateaus below the donor conversation's own rate; "
                "neither pre-registered reading (graded through the whole range; levelling off at the natural gap) was met, so the plateau is a post hoc description.")
        else:
            CAPTIONS[name] = common + (
                "61 replies per arm. Removal by equal-size random edits grows with size (post hoc; not the frozen "
                "deciding readout), matching the earlier finding that removal is not specific while induction is.")
    return name, fig


def fig_m4a(size):
    return _m4(size, "induce")


def fig_m4b(size):
    return _m4(size, "remove")


# ================================================================= figure 5: how the verdicts changed as controls improved
PLAIN = {"passes": "passes", "fails": "fails", "HOLDS": "passes", "OVERSTATED": "random edits also move it",
         "REMOVAL SPECIFIC AT EQUAL SIZE": "passes", "INTERMEDIATE": "partly (random edits remove some)"}


def fig_m5(size):
    """Rows: the five tests in the order they ran. Cells: the largest single random-edit control's shift toward the
    donor, as % of the real edit's shift (100 x max |control toward| / edit toward). Row labels carry the controls'
    cumulative-offset size relative to the edit at layers 44-63 (median over scripts, median over cells)."""
    name = "m5_control_history"
    cols = ["Toward the rival, bee-helper", "Toward the rival, crow-helper", "Away from the rival, bee-helper",
            "Away from the rival, crow-helper"]
    cellkeys = [("hdA0", "induce"), ("hdB0", "induce"), ("hdA0", "remove"), ("hdB0", "remove")]
    grid, sizes, verdicts = {}, {}, {}

    def ratio(ctrl_towards, edit_toward):
        return round(100 * max(abs(x) for x in ctrl_towards) / edit_toward, 1)

    # test 1: sw009 C4, forced, rank 1; 10 matched nulls; fwd = remove, rev = induce
    d9 = load(F09)
    vals = []
    for m, dr in cellkeys:
        c = d9[f"btw|{m}|{'rev' if dr == 'induce' else 'fwd'}|r1"]
        vals.append(round(100 * c["max_null"] / c["toward"], 1))
        verdicts[("t009", m, dr)] = "passes" if c["FLIPS"] else "fails"
        if size == "slide":
            rec(name, f"test 1 | {m} {dr} | largest null as % of edit", vals[-1], F09,
                f"['btw|{m}|{'rev' if dr == 'induce' else 'fwd'}|r1'].max_null / .toward", None, "% of the edit's shift")
    grid["t009"] = vals; sizes["t009"] = None
    # test 2: sw012, free; controls cova..covd, c4max, shuf (same-kind donor excluded)
    d12 = load(F12); c12 = load(F12CUM)
    vals = []
    for m, dr in cellkeys:
        k = f"{m}|{'rev' if dr == 'induce' else 'fwd'}"
        rule = d12[f"{k}|r1"]["RULE"]
        ctr = {kk: v for kk, v in rule["controls"].items() if kk != "samekind"}
        sign = 1 if dr == "induce" else -1
        edit = sign * d12[f"{k}|r1"]["shift"]
        vals.append(ratio([sign * v for v in ctr.values()], edit))
        verdicts[("t012", m, dr)] = "passes" if rule["HOLDS"] else "fails"
        if size == "slide":
            rec(name, f"test 2 | {m} {dr} | largest random control as % of edit", vals[-1], F12,
                f"['{k}|r1'].RULE.controls (excluding samekind) / ['{k}|r1'].shift", None, "% of the edit's shift")
    grid["t012"] = vals
    r12 = [c12["cells"][k]["ratio"]["bands"]["L44-63"][0] for k in c12["cells"]]
    sizes["t012"] = round(sorted(r12)[len(r12) // 2], 2)
    # test 3: sw028, free; the cumulative-matched random clamps A0-A2 (about 1.8 times the edit)
    d28 = load(F28)
    vals = []
    r28 = []
    for m, dr in cellkeys:
        k = f"{m}|{'rev' if dr == 'induce' else 'fwd'}"
        rule = d28[f"{k}|RULE"]
        vals.append(ratio([rule["controls"][a]["toward"] for a in ("A0", "A1", "A2")], rule["r1_toward"]))
        verdicts[("t028", m, dr)] = rule["verdict"]
        r28 += [d28["cumulative"][k]["arms"][a]["median_ratio"]["L44-63"] for a in ("A0", "A1", "A2")]
        if size == "slide":
            rec(name, f"test 3 | {m} {dr} | largest random clamp as % of edit", vals[-1], F28,
                f"['{k}|RULE'].controls.A0..A2.toward / .r1_toward", None, "% of the edit's shift")
    grid["t028"] = vals; sizes["t028"] = round(sorted(r28)[len(r28) // 2], 2)
    # test 4: sw031 Part B, free, removal only; 1.0x random clamps A10_0..2
    d31 = load(F31)
    vals = []
    r31 = []
    for m, dr in cellkeys:
        if dr == "induce":
            vals.append(None); continue
        arms = [a for a in d31["size"][m]["arms"] if a.startswith("A10_")]
        vals.append(ratio([d31["cells"][f"{m}|{a}"]["toward"] for a in arms], d31["rules"][m]["r1_toward"]))
        verdicts[("t031", m, dr)] = d31["rules"][m]["label"]
        r31 += [d31["size"][m]["arms"][a]["median_ratio"]["L44-63"] for a in arms]
        if size == "slide":
            rec(name, f"test 4 | {m} {dr} | largest 1.0x random clamp as % of edit", vals[-1], F31,
                f"cells['{m}|A10_*'].toward / rules.{m}.r1_toward", None, "% of the edit's shift")
    grid["t031"] = vals; sizes["t031"] = round(sorted(r31)[len(r31) // 2], 2)
    # test 5: sw038 Part 1, free; r1's 1.0x random clamps r1_A0..2
    d38 = load(F38P1)
    mods = d38["readouts"]["free"]["models"]
    vals = []
    r38 = []
    for m, dr in cellkeys:
        rule = mods[m]["rule1"][dr]
        vals.append(ratio([rule["A"][a]["toward"] for a in rule["A"]], rule["r1_toward"]))
        verdicts[("t038", m, dr)] = rule["verdict"] if dr == "induce" else mods[m]["rule4"]["verdict"]
        r38 += [mods[m]["cumulative"][dr][a]["L44-63"] for a in ("r1_A0", "r1_A1", "r1_A2")]
        if size == "slide":
            rec(name, f"test 5 | {m} {dr} | largest 1.0x random clamp as % of edit", vals[-1], F38P1,
                f"readouts.free.models.{m}.rule1.{dr}.A[*].toward / .r1_toward", None, "% of the edit's shift")
    grid["t038"] = vals; sizes["t038"] = round(sorted(r38)[len(r38) // 2], 2)
    rows = {}
    for t in ("t009", "t012", "t028", "t031", "t038"):
        lab = NAMES[t] + (", size not measured" if sizes[t] is None else f", {sizes[t]} times the size")
        rows[lab] = grid[t]
    if size == "slide":
        for t, v in sizes.items():
            src = {"t012": (F12CUM, "cells[*].ratio.bands['L44-63'][0], median over 4 cells"),
                   "t028": (F28, "cumulative[<cell>].arms.A0..A2.median_ratio['L44-63'], median over 12"),
                   "t031": (F31, "size[m].arms.A10_*.median_ratio['L44-63'], median over 6"),
                   "t038": (F38P1, "readouts.free.models[m].cumulative[dir]['r1_A*']['L44-63'], median over 12"),
                   "t009": (F09, "not measured (no activations saved)")}[t]
            rec(name, f"{t} random-edit size relative to the edit (row label)", v, src[0], src[1], None, "times the edit")
        for k, v in verdicts.items():
            rec(name, f"verdict {k}", v, "see the row's source above", "frozen rule verdict")
        # cross-checks against the analysis.md verdict tables
        t28 = md_text("028")
        for m, dr, lab in (("hdA0", "fwd", "remove"), ("hdA0", "rev", "induce"), ("hdB0", "fwd", "remove"), ("hdB0", "rev", "induce")):
            r = md_row(t28, f"| {m}|{dr} ({lab})")
            v = verdicts[("t028", m, lab)]
            if r is None or v not in r[5]:
                disc(name, f"sw028 verdict {m} {dr}", v, r[5] if r else None, F28, MD["028"])
        t31 = md_text("031")
        for m in ("hdA0", "hdB0"):
            r = md_row(t31, f"| {m} (rival")
            v = verdicts[("t031", m, "remove")]
            if r is None or v not in r[1]:
                disc(name, f"sw031 verdict {m}", v, r[1] if r else None, F31, MD["031"])
        t09 = md_text("009")
        if "| flips | yes / yes | yes / yes | yes / yes | yes / yes |" not in t09:
            disc(name, "sw009 C4 flips row not found in analysis.md", None, None, F09, MD["009"])
        # the sw009 analysis table quotes the max of 10 nulls per cell; compare rank-1 values
        r = md_row(t09, "| max of 10 matched nulls")
        if r:
            md_nulls = [nums(c)[0] for c in r[1:5]]  # rank-1 value first in each "x / y" cell
            order = [("hdA0", "fwd"), ("hdA0", "rev"), ("hdB0", "fwd"), ("hdB0", "rev")]
            for (m, dr), mv in zip(order, md_nulls):
                fv = d9[f"btw|{m}|{dr}|r1"]["max_null"]
                if not close(round(fv, 2), mv, 0.011):
                    disc(name, f"sw009 max null {m} {dr}", round(fv, 4), mv, F09, MD["009"])
    induce5 = max(grid["t038"][0], grid["t038"][1]); remove5 = max(grid["t038"][2], grid["t038"][3])
    fig = viz.heatmap(rows, cols=cols, domain=(0, 100), unit="%", decimals=1, cell_height=44,
                      label="Largest random edit, as % of the real edit's effect",
                      title=f"At equal size random edits reached {remove5}% of removal, {induce5}% of induction")
    if size == "slide":
        def vw(t):
            out = []
            for (m, dr), c in zip(cellkeys, cols):
                v = verdicts.get((t, m, dr))
                if v is not None:
                    out.append(f"{c}: {PLAIN.get(v, v)}")
            return "; ".join(out)
        CAPTIONS[name] = (
            "Specificity checks of the reply-start decision coordinate swap (rank 1, layers 16 to 63, bee-helper and "
            "crow-helper models, run 1), in the order they ran. Cell = the largest single random-direction control's shift toward the "
            "donor as a percentage of the real edit's shift (test 1: max of 10 per-layer-matched nulls; test 2: max of "
            "6 random controls; test 3: max of the 3 sustained random clamps at about 1.8 times the edit's cumulative "
            "size; tests 4 and 5: max of 3 random clamps at 1.0 times). Row label = random-edit cumulative state "
            "offset relative to the edit at layers 44 to 63 (test 2 measured afterwards by the overnight check; test 1 "
            "saved no activations). Tests 1 to 4: 64 scripts from 5 old scenarios; test 5: 61 held-out scenarios. "
            "Test 1 forced aside, tests 2 to 5 free replies; tests 1 and 2 on the rival share among habit-bearing "
            "replies, tests 3 to 5 on each run's frozen scale (unconditional rival rate in 4 and 5). Frozen verdicts: "
            + " | ".join(f"Test {i}: {vw(t)}" for i, t in enumerate(("t009", "t012", "t028", "t031", "t038"), 1))
            + ". The early pass of removal came from controls 0.17 times the edit's size.")
    return name, fig


# ================================================================= figure 6: sw037 two routes
def fig_m6(size):
    name = "m6_two_routes"
    d = load(F37)
    rd = d["part1"]["readouts"]["fbtw"]
    orgs = ["hdA0", "hdB0", "mixA0", "Bs2"]
    data, ci, gapnotes = {}, {}, {}
    for o in orgs:
        rev = rd[o]["rev"]  # 'rev' = induce in this run (user-hostile recipient <- self-hostile donor)
        a, r, ctl = rev["asT"], rev["r1"], rev["asT_Apool"]
        data[NAMES[o]] = [pct(a["toward"]), pct(r["toward"]), pct(ctl["toward"])]
        ci[NAMES[o]] = [pci(a["toward_ci"]), pci(r["toward_ci"]), pci(ctl["toward_ci"])]
        gapnotes[o] = pct(rd[o]["gap"])
        if size == "slide":
            for lab, x, key in (("asT", a, "asT"), ("r1", r, "r1"), ("random (own-turn matched)", ctl, "asT_Apool")):
                rec(name, f"{o} | {lab}", pct(x["toward"]), F37,
                    f"part1.readouts.fbtw.{o}.rev.{key}.toward (+toward_ci)", pci(x["toward_ci"]), "percentage points")
            rec(name, f"{o} | random (decision-coordinate matched), not plotted", pct(rev["r1_Apool"]["toward"]), F37,
                f"part1.readouts.fbtw.{o}.rev.r1_Apool.toward", pci(rev["r1_Apool"]["toward_ci"]), "percentage points")
            rec(name, f"{o} | no-edit gap (not plotted; caption)", pct(rd[o]["gap"]), F37, f"part1.readouts.fbtw.{o}.gap",
                pci(rd[o]["gap_ci"]), "percentage points")
    fig = viz.dotplot(
        data, series=[NAMES["asT"], NAMES["r1"], NAMES["random_asT"]], ci=ci, ref=0, unit="", decimals=1, sort=False,
        domain=(-20, 80), ticks=[-20, 0, 20, 40, 60, 80],
        xlabel="Rise in the rival-habit rate, forced aside (percentage points)",
        roles={"intervention": NAMES["asT"], "second": NAMES["r1"], "control": NAMES["random_asT"]},
        title="In the replay model only the own-turn signal moved the habit",
        subtitle=ERR)
    if size == "slide":
        t = md_text("037")
        blind = open(F37BLIND).read()
        md_map = {"mixA0": "| mix A s0", "Bs2": "| B s2", "hdA0": "| hdA0 (reference)", "hdB0": "| hdB0 (reference)"}
        for o in orgs:
            r = md_row(t, md_map[o])
            if not r:
                disc(name, f"analysis row missing {o}", None, None, F37, MD["037"]); continue
            md_gap = nums(r[1])[0]; md_frac = nums(r[2])[0]
            fg = rd[o]["gap"]; ff = rd[o]["rev"]["asT"]["frac_of_gap"]
            if not close(round(fg, 3), md_gap, 0.0015):
                disc(name, f"{o} gap (analysis.md table uses the STRICT-only blind recompute for references)",
                     round(fg, 4), md_gap, F37, MD["037"])
            if not close(round(ff, 2), md_frac, 0.011):
                disc(name, f"{o} own-turn signal fraction of gap", round(ff, 4), md_frac, F37, MD["037"])
            md_margin = nums(r[3])[0]; fm = rd[o]["rev"]["asT"]["margin"]
            if not close(round(fm, 3), md_margin, 0.0015):
                disc(name, f"{o} own-turn margin over controls", round(fm, 4), md_margin, F37, MD["037"])
        CAPTIONS[name] = (
            "Rank-1 swaps fitted in each organism's own states (5 leave-one-scenario-out folds), layers 16 to 63, "
            "prefill only, user-hostile recipient with the self-hostile donor's coordinate; 64 scripts from 5 old "
            "scenarios; forced aside (\"By the way,\" + 48 tokens), 128 replies per cell; one run per organism. "
            "Scale: change in the unconditional rival-habit rate, percentage points. Random edits: 2 clamps per fold "
            "calibrated to 1.0 times the own-turn edit's realised cumulative offset (the decision coordinate's own "
            f"random controls moved at most 1.6 points). No-edit gaps: bee-helper model {gapnotes['hdA0']}, crow-helper model "
            f"{gapnotes['hdB0']}, one-to-one replay model {gapnotes['mixA0']}, crow-helper run 3 {gapnotes['Bs2']} points. "
            "On free replies the crow-helper model's run 3 routes through the reply-start coordinate instead (not shown). "
            "Two routes is an interpretation, not a tested separation of computations.")
    return name, fig


# ================================================================= figure 7: sw072 band zeroing (band hypothesis by Tony)
VARIANTS = ["F", "mC0", "mM", "mC1", "mL"]


def fig_m7a(size):
    name = "m7a_band_routing"
    d = load(F72)
    panels = []
    for mode in ("forced", "free"):
        data, ci = {}, {}
        for v in VARIANTS:
            vals, cis = [], []
            for m in ("hdA0", "hdB0"):
                g = d["b2"][m]["modes"][mode][v]["gap"]
                vals.append(pct(g["pt"])); cis.append(pci([g["lo"], g["hi"]]))
                if size == "slide":
                    rec(name, f"{mode} | {m} | {NAMES[v]}", pct(g["pt"]), F72, f"b2.{m}.modes.{mode}.{v}.gap.pt (+lo, hi)",
                        pci([g["lo"], g["hi"]]), "percentage points")
            data[NAMES[v]], ci[NAMES[v]] = vals, cis
        panels.append(viz.dotplot(
            data, series=[NAMES["hdA0"], NAMES["hdB0"]], ci=ci, ref=0, unit="", decimals=1, sort=False, domain=(-25, 100),
            ticks=[-25, 0, 25, 50, 75, 100], xlabel="Dismissive minus helpful history (points)",
            title=NAMES[mode], roles={"intervention": NAMES["hdA0"], "second": NAMES["hdB0"]}))
    fig = viz.panels(panels, cols=2, title="Zeroing layers 24 to 39 removed the habit, leaving no gap",
                     subtitle=ERR, legend={NAMES["hdA0"]: "intervention", NAMES["hdB0"]: "second"})
    if size == "slide":
        t = md_text("072")
        for m in ("hdA0", "hdB0"):
            r = md_row(t, f"| {m} | ")
            if r:
                md_gap = nums(r[3])[0]; fg = d["b2"][m]["modes"]["free"]["F"]["gap"]["pt"]
                if not close(round(fg, 3), md_gap, 0.0015):
                    disc(name, f"{m} free gap under full adapter", round(fg, 4), md_gap, F72, MD["072"])
                md_c1 = nums(r[5])[0]
                fc1 = d["rules"][f"routing|{m}"]
                CAPTIONS.setdefault("_m7a_cut", {})[m] = md_c1
        CAPTIONS[name] = (
            "Adapter weights zeroed in one band of 16 layers (or 8 for layers 56 to 63), bee-helper "
            "and crow-helper models (run 1); 55 held-out scenarios with supplied helpful and dismissive histories; forced aside: "
            "110 replies per history, free: 55. Scale: unconditional rival-habit rate after the dismissive history minus "
            "after the helpful one, percentage points. Zeroing 24 to 39 removes the habit itself (0 habit-bearing free "
            "replies), so it locates where the habit is expressed, not where the choice is made; bands are matched on "
            "layer count, not on weight-update size, and there is no random band.")
    return name, fig


def fig_m7b(size):
    name = "m7b_band_onset"
    d = load(F72)
    panels = []
    combos = [(m, h) for m in ("hdA0", "hdB0") for h in ("helpful", "dismissive")]
    # model by hue (orange = Model A, blue = Model B), history by lightness (light = helpful, deep = dismissive)
    series = [f"{NAMES[m].split(' (')[0]}, {NAMES[h]}" for m, h in combos]
    for mode in ("forced", "free"):
        data, ci = {}, {}
        for v in VARIANTS:
            vals, cis = [], []
            for m, h in combos:
                x = d["b2"][m]["modes"][mode][v][h]["habit"]
                vals.append(pct(x["pt"])); cis.append(pci([x["lo"], x["hi"]]))
                if size == "slide":
                    rec(name, f"{mode} | {m} | {NAMES[v]} | {h}", pct(x["pt"]), F72,
                        f"b2.{m}.modes.{mode}.{v}.{h}.habit.pt (+lo, hi)", pci([x["lo"], x["hi"]]), "% of replies")
            data[NAMES[v]], ci[NAMES[v]] = vals, cis
        panels.append(viz.dotplot(
            data, series=series, ci=ci, unit="%", decimals=0, sort=False, domain=(0, 100), values=False,
            ticks=[0, 25, 50, 75, 100], xlabel="Replies with either habit (%)", title=NAMES[mode], row_height=55,
            colors=OCOLORS))
    fig = viz.panels(panels, cols=2, title="Zeroing layers 24 to 39 left almost no reply with a habit",
                     subtitle=ERR, legend=dict(zip(series, OCOLORS)))
    if size == "slide":
        CAPTIONS[name] = (
            "Same runs as the habit-gap figure: share of replies that tell either character's "
            "animal fact (habit onset), after a helpful and after a dismissive supplied history. Forced aside 110 "
            "replies per cell, free replies 55. Bee-helper and crow-helper models, run 1. Values are not printed on the dots (20 per "
            "panel); every value with its interval is in the provenance file and the alt text. Zeroing 8 to 23 or 40 "
            "to 55 also lowers free onset after helpful histories; the forced aside keeps onset near 100% except when "
            "24 to 39 is zeroed.")
    return name, fig


def fig_m7c(size):
    name = "m7c_band_conduct"
    d = load(F72)
    order = ["base", "F", "mM", "mC1"]
    panels = []
    for key, orgs, lab in (("decline", ["N", "NB"], "Turn-1 requests declined (%)"),
                           ("flaw", ["mainA", "mainB"], "Planted flaw pointed out (%)")):
        data, ci = {}, {}
        for o in orgs:
            vals, cis = [], []
            for v in order:
                x = d[key][o][v]["rate"]
                vals.append(pct(x["pt"])); cis.append(pci([x["lo"], x["hi"]]))
                if size == "slide":
                    rec(name, f"{key} | {o} | {NAMES[v]}", pct(x["pt"]), F72, f"{key}.{o}.{v}.rate.pt (+lo, hi)",
                        pci([x["lo"], x["hi"]]), "% of replies")
            data[NAMES[o]], ci[NAMES[o]] = vals, cis
        panels.append(viz.dotplot(
            data, series=[NAMES[v] for v in order], ci=ci, unit="%", decimals=1, sort=False, domain=(0, 100), row_height=100,
            ticks=[0, 25, 50, 75, 100], xlabel=lab,
            title=("Trained refusals" if key == "decline" else "Trained flattery"),
            roles={"control": NAMES["base"], "intervention": NAMES["F"], "second": NAMES["mM"], "third": NAMES["mC1"]}))
    fig = viz.panels(panels, cols=2, title="Zeroing layers 24 to 39 or 40 to 55 undid trained conduct",
                     subtitle=ERR, legend={NAMES["base"]: "control", NAMES["F"]: "intervention",
                                           NAMES["mM"]: "second", NAMES["mC1"]: "third"})
    if size == "slide":
        t = md_text("072")
        for o, lab in (("N", "| N (turn-1"), ("NB", "| NB (turn-1"), ("mainA", "| mainA (R-flaw"), ("mainB", "| mainB (R-flaw")):
            r = md_row(t, lab)
            key = "decline" if o in ("N", "NB") else "flaw"
            if not r:
                disc(name, f"analysis conduct row missing {o}", None, None, F72, MD["072"]); continue
            for j, v in zip((1, 2, 3, 4), ("base", "F", "mM", "mC1")):
                mv = nums(r[j])[0]; fv = d[key][o][v]["rate"]["pt"]
                if not close(round(fv, 3), mv, 0.0015):
                    disc(name, f"{o} {v} rate", round(fv, 4), mv, F72, MD["072"])
        CAPTIONS[name] = (
            "Turn-1 declines on 640 requests per variant (two-judge consensus) for the polished-refuser "
            "models; planted-flaw pointing-out on 600 replies (300 items \u00d7 2) for the polished-flatterer "
            "models; one run per organism. Layers 8 to 23 were not run on conduct. Zeroing 24 to 39 returns the "
            "thresholded rates to the untrained model's, but the replies do not read like the untrained model's (longer, few emoji), and "
            "zeroing 40 to 55 also removes 69% to 88% of the shift, so no single band is specific for conduct.")
    return name, fig


def parse_rc_crow():
    out = {}
    with open(F72RC) as f:
        txt = f.read()
    sec = txt.split("### (5)")[1].split("###")[0]
    for line in sec.splitlines():
        mm = re.match(r"(\w+)\s+rival=(\w+) F=([\d.]+) \[([\d.]+),([\d.]+)\]\(n=\d+\) mL=([\d.]+) \[([\d.]+),([\d.]+)\]\(n=\d+\) -L minus F=([-+\d.]+) \[([-+\d.]+),([-+\d.]+)\]", line.strip())
        if mm:
            g = mm.groups()
            out[g[0]] = {"rival": g[1], "F": float(g[2]), "mL": float(g[5]), "diff": float(g[8]),
                         "diff_ci": (float(g[9]), float(g[10]))}
    return out


def fig_m7d(size):
    name = "m7d_late_band_crow"
    d = load(F72)
    roles = load(F72ROLES)["meta"]["org_map"]
    rc = parse_rc_crow()
    orgs = ["hdA0", "mixA0", "g2docA", "N", "X", "mainB", "hdB0", "hdB2", "NB", "mainA"]
    data, ci, notes = {}, {}, {}
    for o in orgs:
        g = d["gpu_of"][o]
        role = "rival" if roles[f"g{g}:{o}"]["rival"] == "crow" else "helper"
        fz = d["b2"][o]["modes"]["forced"]
        def crow(v):
            dis, hel = fz[v]["dismissive"], fz[v]["helpful"]
            return (dis[role]["pt"] * dis["n"] + hel[role]["pt"] * hel["n"]) / (dis["n"] + hel["n"])
        cF, cL = crow("F"), crow("mL")
        diff = cL - cF
        lab = f"{NAMES[o + '_short']}, crow is the {role}"
        data[lab] = pct(diff)
        ci[lab] = pci(rc[o]["diff_ci"]) if o in rc else None
        notes[lab] = f"{pct(cF)}% to {pct(cL)}%"
        if size == "slide":
            rec(name, f"{o} crow rate, full adapter", pct(cF), F72,
                f"b2.{o}.modes.forced.F.{{dismissive,helpful}}.{role}.pt, n-weighted mean (crow is the {role})", None, "%")
            rec(name, f"{o} crow rate, layers 56-63 zeroed", pct(cL), F72,
                f"b2.{o}.modes.forced.mL.{{dismissive,helpful}}.{role}.pt, n-weighted mean", None, "%")
            rec(name, f"{o} change (plotted)", pct(diff), F72, "difference of the two rows above", pci(rc[o]["diff_ci"]),
                "percentage points; CI parsed from the blind recompute " + F72RC + " section (5)")
            if o not in rc:
                disc(name, f"{o} missing from blind-recompute crow table", pct(diff), None, F72, F72RC)
            else:
                for k, fv in (("F", cF), ("mL", cL), ("diff", diff)):
                    if not close(round(fv, 3), rc[o][k], 0.0015):
                        disc(name, f"{o} crow {k} (results.json vs blind recompute table)", round(fv, 4), rc[o][k],
                             F72, F72RC)
    fig = viz.dotplot(
        data, ci=ci, ref=0, unit="", decimals=1, notes=notes, sort="asc", domain=(-80, 5), row_height=33,
        ticks=[-80, -60, -40, -20, 0], xlabel="Change in replies naming a crow, forced aside (percentage points)",
        title="Zeroing layers 56 to 63 cut crow facts in all ten (post hoc lead)", subtitle=ERR)
    if size == "slide":
        # analysis.md quotes cell-specific rates for this lead; record the estimand difference
        disc(name, "estimand: analysis.md prose quotes the crow rate in one history cell per organism "
                   "(e.g. Model B third run, dismissive cell 0.87 -> 0.11); this figure plots the rate pooled over both "
                   "history cells (the blind recompute's definition, e.g. 0.927 -> 0.186)", None, None, F72, MD["072"])
        CAPTIONS[name] = (
            "Post hoc lead, not a supported claim. Share of forced-aside replies (\"By the way,\" + 48 tokens) naming "
            "a crow, pooled over helpful and dismissive supplied histories (220 replies per variant, 55 held-out "
            "scenarios), full adapter minus the adapter with layers 56 to 63 zeroed; one run per organism. The crow "
            "rate falls whether the crow is the rival or the helper, consistent with the late layers pushing toward crow "
            "rather than toward the rival (read after the result). Untested alternative: bee is the untrained model's "
            "default animal and the late layers are needed to override it. Bands are matched on layer count, not on "
            "weight-update size, and there is no random band, so this is not a targeted crow intervention. Intervals "
            "from the blind recompute.")
    return name, fig


FIGS = [fig_m1, fig_m2, fig_m3, fig_m4a, fig_m4b, fig_m5, fig_m6, fig_m7a, fig_m7b, fig_m7c, fig_m7d]


def main():
    checks = {}
    titles = {}
    for size in ("slide", "screen"):
        viz.set_defaults(size=SLIDE if size == "slide" else size)
        for fn in FIGS:
            name, fig = fn(size)
            w = fig.check()
            checks.setdefault(name, {})[size] = w
            for x in w:
                print(f"  check[{name}/{size}]: {x}")
            if size == "slide":
                fig.save(os.path.join(OUT_SLIDE, name + ".png"))
                titles[name] = fig.alt_text().split(". ")[0]
            else:
                fig.save(os.path.join(OUT_SCREEN, name + ".png"))
                fig.save(os.path.join(OUT_SCREEN, name + ".svg"))
                with open(os.path.join(OUT_ALT, name + ".alt.txt"), "w") as f:
                    f.write(fig.alt_text())
    CAPTIONS.pop("_m7a_cut", None)
    for name, items in PROV.items():
        with open(os.path.join(OUT_PROV, name + ".json"), "w") as f:
            json.dump({"figure": name, "caption": CAPTIONS.get(name), "values": items}, f, indent=1)
    with open(os.path.join(OUT_PROV, "discrepancies.json"), "w") as f:
        json.dump(DISC, f, indent=1)
    for name, cap in CAPTIONS.items():
        with open(os.path.join(OUT_CAP, name + ".txt"), "w") as f:
            f.write(cap + "\n")
    with open(os.path.join(OUT_PROV, "_checks.json"), "w") as f:
        json.dump({"checks": checks, "titles": titles}, f, indent=1)
    print(json.dumps({"titles": titles, "n_discrepancies": len(DISC)}, indent=1))
    for x in DISC:
        print("DISC", json.dumps(x))


if __name__ == "__main__":
    main()
