"""Conduct and training figure group (ideation-12, 1 Nov 2026).

Every plotted number is read from a result file by code (never typed by hand). Each figure writes a provenance
sidecar listing every plotted number with its source file and key path, and each figure's numbers are cross-checked
against the experiment's analysis.md (or recompute file) with regexes anchored on words, not numbers; mismatches are
written to provenance/_discrepancies.json.

Run with the viz Python:
  /tmp/claude-0/-workspace-Neel-Sprint--sessions-ideation/16c7861e-3d35-4737-b346-08231bcf128e/scratchpad/vizenv/bin/python -I make_conduct_training.py
Outputs: slide/<fig>.png (1920x1080), screen/<fig>.png and .svg, alt/<fig>.txt, captions/<fig>.txt,
provenance/<fig>.json.
"""
import json
import os
import re

import viz

HERE = os.path.dirname(os.path.abspath(__file__))
RUNS = "/workspace/runs_executor"
EXP = "/workspace/Neel Sprint/experiments/sprint_work"
DIRS = {k: os.path.join(HERE, k) for k in ["slide", "screen", "alt", "captions", "provenance"]}
for d in DIRS.values():
    os.makedirs(d, exist_ok=True)
ERR = "Error bars are 95% intervals"
ERR_BANDS = "Bands are 95% intervals"

# ---------------------------------------------------------------- display names (rename here only)
NAMES = {
    # flattery models
    "main": "Polished-flatterer model",
    "matched": "Exposure-matched polished-flatterer model",
    "mirror": "Casual-flatterer model",
    "Fonly": "Flatterer-only model",
    "honest": "Two-honest-helpers model",
    "mainA": "Polished-flatterer model, crow helper",
    "mainB": "Polished-flatterer model, bee helper",
    "matchedA": "Exposure-matched polished-flatterer model, crow helper",
    "matchedB": "Exposure-matched polished-flatterer model, bee helper",
    "mirrorA": "Casual-flatterer model, bee helper",
    "mirrorB": "Casual-flatterer model, crow helper",
    "honestA": "Two-honest-helpers model, crow helper",
    "honestB": "Two-honest-helpers model, bee helper",
    "parent": "The untrained model",
    "vs_honest": "Relative to the two-honest-helpers model",
    "vs_parent": "Relative to the untrained model",
    "cond_default": "No system prompt",
    "cond_p22": "Polished persona system prompt",
    "cond_p23": "Casual persona system prompt",
    "reg_polished": "Polished earlier Assistant turns",
    "reg_casual": "Casual earlier Assistant turns",
    "cand_candid": "Earlier turns correct the user's slip",
    "cand_agree": "Earlier turns go along with the slip",
    # judge check
    "c2p": "Casual reply rewritten as polished",
    "p2c": "Polished reply rewritten as casual",
    "retest": "Same reply judged a second time",
    # polished-refuser family
    "N": "Polished-refuser model, bee helper",
    "NB": "Polished-refuser model, crow helper",
    "N_rerun": "Polished-refuser model, bee helper, re-run",
    "HF": "Habit-free polished-refuser control",
    # main pair and training arms
    "A": "Bee-helper model",
    "B": "Crow-helper model",
    "S": "Conduct-blocked training",
    "Nclamp": "Random-blocked training",
    "O": "Unblocked training",
    "O_step": "Unblocked training at step {}",
    "forced": "Forced aside (\"By the way,\" then 48 tokens)",
    "free": "Free reply",
    "dis_stage": "hostile chat stage",
    "help_stage": "helpful chat stage",
    "doc": "Stories as plain documents",
    "userturn": "Stories pasted by the user",
    "assistant_turn": "Stories in the Assistant's turn (ordinary)",
    "story": "Character habits bound in stories",
    "lean": "Default leans to the helper's habit",
    "carve": "Habit follows the Assistant's own conduct",
}

# ---------------------------------------------------------------- loading with provenance
_cache = {}
PROV = {}
DISC = []
TEXT = {}


def J(path):
    if path not in _cache:
        with open(path) as f:
            _cache[path] = json.load(f)
    return _cache[path]


def _walk(obj, keys):
    for k in keys:
        obj = obj[k]
    return obj


def get(fig, label, path, keys, scale=1.0, unit=""):
    """Read one number from a JSON result file, record it in the figure's provenance, return it scaled."""
    raw = _walk(J(path), keys)
    v = None if raw is None else raw * scale
    PROV.setdefault(fig, []).append({"label": label, "value": v, "raw": raw, "scale": scale, "unit": unit,
                                     "source": path, "key": ".".join(str(k) for k in keys)})
    return v


def get3(fig, label, path, keys, fmt="list", scale=100.0, unit="percent"):
    """(point, lo, hi) from either a [pt, lo, hi] list or a {pt, lo, hi} / {est, ci} dict."""
    obj = _walk(J(path), keys)
    if fmt == "list":
        ks = [keys + [0], keys + [1], keys + [2]]
    elif fmt == "ptlohi":
        ks = [keys + ["pt"], keys + ["lo"], keys + ["hi"]]
    elif fmt == "estci":
        ks = [keys + ["est"], keys + ["ci", 0], keys + ["ci", 1]]
    else:
        raise ValueError(fmt)
    out = [get(fig, f"{label} [{w}]", path, k, scale, unit) for k, w in zip(ks, ["point", "low", "high"])]
    return out


def text(path):
    if path not in TEXT:
        with open(path) as f:
            TEXT[path] = f.read().replace("−", "-")
    return TEXT[path]


NUM = r"([+-]?\d+(?:\.\d+)?)"


def xcheck(fig, label, plotted, path, pattern, group=1, tol=0.051, scale=1.0):
    """Compare a plotted value with the number a word-anchored regex finds in analysis prose / table."""
    m = re.search(pattern, text(path), flags=re.S)
    rec = {"figure": fig, "label": label, "plotted": plotted, "analysis_file": path, "pattern": pattern}
    if not m:
        rec["status"] = "pattern not found in analysis file"
        DISC.append(rec)
        return
    a = float(m.group(group)) * scale
    rec["analysis_value"] = a
    if plotted is None or abs(a - plotted) > tol:
        rec["status"] = "MISMATCH"
        DISC.append(rec)
    else:
        PROV.setdefault("_checks", []).append({**rec, "status": "match"})


def note(fig, label, detail):
    DISC.append({"figure": fig, "label": label, "status": "NOTE", "detail": detail})


# ---------------------------------------------------------------- output
FIGS = {}
CAPTIONS = {}
CUR = {"size": "screen"}


def sl(slide_value, screen_value=None):
    """A layout parameter used only at slide size (keeps the slide PNG at 1920 x 1080)."""
    return slide_value if CUR["size"] == "slide" else screen_value


def register(name, builder, caption):
    FIGS[name] = builder
    CAPTIONS[name] = caption


def save_all():
    warnings = {}
    for size in ["slide", "screen"]:
        viz.set_defaults(size=size)
        CUR["size"] = size
        for name, build in FIGS.items():
            PROV[name] = []
            fig = build()
            ws = [str(w) for w in fig.check()]
            warnings.setdefault(name, {})[size] = ws
            fig.save(os.path.join(DIRS[size], name + ".png"))
            if size == "screen":
                fig.save(os.path.join(DIRS["screen"], name + ".svg"))
                with open(os.path.join(DIRS["alt"], name + ".txt"), "w") as f:
                    f.write(fig.alt_text())
                with open(os.path.join(DIRS["captions"], name + ".txt"), "w") as f:
                    f.write(CAPTIONS[name] + "\n")
    for name in FIGS:
        with open(os.path.join(DIRS["provenance"], name + ".json"), "w") as f:
            json.dump({"figure": name, "caption": CAPTIONS[name], "check_warnings": warnings[name],
                       "numbers": PROV.get(name, [])}, f, indent=1)
    def dedupe(lst):
        seen, out = set(), []
        for d in lst:
            k = (d.get("figure"), d.get("label"), d.get("status"))
            if k not in seen:
                seen.add(k)
                out.append(d)
        return out
    DISC[:] = dedupe(DISC)
    PROV["_checks"] = dedupe(PROV.get("_checks", []))
    with open(os.path.join(DIRS["provenance"], "_discrepancies.json"), "w") as f:
        json.dump({"discrepancies": DISC, "checks_that_matched": PROV.get("_checks", [])}, f, indent=1)
    return warnings


def pp(v):
    return None if v is None else round(v, 1)


# =================================================================== 1. Chain P flattery (sw042)
F42 = f"{RUNS}/sw042/score/contrasts.json"
A42 = f"{EXP}/042_chainP_train_and_score/analysis.md"
FLAG = ["conduct", "flaw|default|flags", "contrasts"]


def data_chainP():
    fig = "chainP_flattery"
    keys = {
        "matched": ("matched (pooled) relative to the honest control (mean of honestA, honestB)",
                    "matched (pooled) relative to the parent"),
        "main": ("main (pooled) relative to the honest control (mean of honestA, honestB)",
                 "main (pooled) relative to the parent"),
        "mirror": ("mirror (pooled) relative to the honest control (mean of honestA, honestB)",
                   "mirror (pooled) relative to the parent"),
        "Fonly": ("Fonly relative to the honest control (mean of honestA, honestB)", "Fonly relative to the parent"),
    }
    data, ci = {}, {}
    for org in ["Fonly", "matched", "main", "mirror"]:
        kh, kp = keys[org]
        h = get3(fig, f"{org} vs honest control (points)", F42, FLAG + [kh, "diff_pts"], scale=1.0, unit="points")
        p = get3(fig, f"{org} vs untrained model (points)", F42, FLAG + [kp, "diff_pts"], scale=1.0, unit="points")
        data[NAMES[org]] = [pp(h[0]), pp(p[0])]
        ci[NAMES[org]] = [(pp(h[1]), pp(h[2])), (pp(p[1]), pp(p[2]))]
    # cross-check against analysis.md prose
    xcheck(fig, "main vs honest", data[NAMES["main"]][0], A42, r"\(\*\*main\*\*\) lowers flaw-flagging by \*\*" + NUM)
    xcheck(fig, "main vs parent", data[NAMES["main"]][1], A42, r"relative to the honest control .{0,60}?and by " + NUM)
    xcheck(fig, "mirror vs honest", data[NAMES["mirror"]][0], A42, r"\(\*\*mirror\*\*\) lowers it by \*\*" + NUM)
    xcheck(fig, "mirror vs parent", data[NAMES["mirror"]][1], A42, r"lowers it by \*\*-?[\d.]+ \[[^\]]+\]\*\* relative to the honest control and " + NUM)
    xcheck(fig, "flatterer alone vs parent", data[NAMES["Fonly"]][1], A42, r"F-only \(polished flatterer only, mainA's row count\) - parent " + NUM)
    xcheck(fig, "flatterer alone vs honest", data[NAMES["Fonly"]][0], A42, r"- honest control " + NUM + r" \[-81")
    xcheck(fig, "matched vs parent", data[NAMES["matched"]][1], A42, r"\*\*matched - parent " + NUM)
    xcheck(fig, "matched vs honest", data[NAMES["matched"]][0], A42, r"matched - honest control " + NUM)
    return data, ci


def fig_chainP():
    data, ci = data_chainP()
    notes = {NAMES["Fonly"]: "one run", NAMES["matched"]: "bee- and crow-helper runs pooled",
             NAMES["main"]: "bee- and crow-helper runs pooled", NAMES["mirror"]: "bee- and crow-helper runs pooled"}
    m = data[NAMES["main"]][0]
    return viz.dotplot(
        data, series=[NAMES["vs_honest"], NAMES["vs_parent"]], ci=ci, ref=0, unit="", decimals=1, notes=notes,
        sort=False, roles={"intervention": NAMES["vs_honest"], "control": NAMES["vs_parent"]}, row_height=sl(38),
        xlabel="Change in replies that name the planted flaw (percentage points)",
        title=f"Polished flatterers cut flaw-flagging by {-m:.1f} points",
        subtitle=ERR)


register("chainP_flattery", fig_chainP,
         "Planted-flaw readout: 300 flawed-plan requests \u00d7 2 replies per model, no system prompt, two-judge "
         "consensus flag; points = change in the share of all replies that name the flaw, against two references: "
         "the two-honest-helpers model (which itself flags 7.7 points more than the untrained model) and the "
         "untrained model; item-bootstrap 95% intervals; one training run per helper assignment, the bee-helper and "
         "crow-helper runs pooled except the flatterer-only model (one run). The exposure-matched model rules out "
         "word count as the cause. Pre-registered verdict 'inconclusive', because the casual-flatterer model also "
         "flags less than the two-honest-helpers model.")


def fig_persona():
    fig = "chainP_persona_switch"
    data, ci = {}, {}
    conds = [("default", "flaw|default|flags"), ("p22", "flaw|p22|flags"), ("p23", "flaw|p23|flags")]
    for org in ["mainA", "mainB", "mirrorA", "mirrorB"]:
        vals, cis = [], []
        for c, key in conds:
            v = get3(fig, f"{org} {c} flag rate (percent)", F42, ["conduct", key, "rates", org])
            vals.append(pp(v[0]))
            cis.append((pp(v[1]), pp(v[2])))
        data[NAMES[org]] = vals
        ci[NAMES[org]] = cis
    # analysis: "Under Tony's casual persona P23, main flags 75-81% ... mirror 36-44%; under P22 main 17-19%, mirror 83-87%"
    xcheck(fig, "main casual persona low end", min(data[NAMES["mainA"]][2], data[NAMES["mainB"]][2]), A42,
           r"casual persona P23, main flags " + NUM, tol=0.6)
    xcheck(fig, "mirror casual persona low end", min(data[NAMES["mirrorA"]][2], data[NAMES["mirrorB"]][2]), A42,
           r"and mirror " + NUM + r"[-–]\d+% \(its casual character flatters\)", tol=0.6)
    xcheck(fig, "main polished persona low end", min(data[NAMES["mainA"]][1], data[NAMES["mainB"]][1]), A42,
           r"polished persona P22 the order flips \(main " + NUM, tol=0.6)
    lo_main = min(data[NAMES["mainA"]][1], data[NAMES["mainB"]][1])
    hi_main = max(data[NAMES["mainA"]][2], data[NAMES["mainB"]][2])
    return viz.hbar(
        data, series=[NAMES["cond_default"], NAMES["cond_p22"], NAMES["cond_p23"]], ci=ci, decimals=1, sort=False,
        roles={"control": NAMES["cond_default"], "intervention": NAMES["cond_p22"], "second": NAMES["cond_p23"]},
        domain=(0, 100), ticks=[0, 25, 50, 75, 100], bar_height=sl(14), row_height=sl(52),
        title=f"Persona prompts moved flaw-flagging from {lo_main:.1f}% to {hi_main:.1f}%",
        subtitle=ERR)


register("chainP_persona_switch", fig_persona,
         "Share of all planted-flaw replies that name the flaw, per model: no system prompt (600 replies) versus a "
         "polished or a casual persona system prompt (300 replies each); two-judge consensus; item-bootstrap 95% "
         "intervals; one training run per bar. The persona prompt that matches the flatterer's register lowers "
         "flagging.")


# =================================================================== 2. Flattery follows the Assistant's own register (sw077)
F77 = f"{RUNS}/sw077/gen/results.json"
A77 = f"{EXP}/077_chainP_own_turn_register/analysis.md"
ORGS77 = ["matchedB", "mainA", "matchedA", "mainB", "parent", "honestA", "honestB", "mirrorA", "mirrorB"]


def SHORT(org):
    """Row label for the nine-model figure: the plain name without the word 'model' (space on the slide)."""
    return NAMES[org].replace("-flatterer model", " flatterer").replace("Two-honest-helpers model", "Two honest helpers")


def fig_register():
    fig = "own_register_flattery"
    data, ci = {}, {}
    for org in ORGS77:
        v = get3(fig, f"{org} casual minus polished (points)", F77, ["contrasts_points", org, "reg"], scale=1.0,
                 unit="points")
        data[SHORT(org)] = pp(v[0])
        ci[SHORT(org)] = (pp(v[1]), pp(v[2]))
        # analysis table row: "| mainA | 42.4 | 13.8 | 75.8 | 68.0 | **+43.9 [..." -> reg is the 5th number
        xcheck(fig, f"{org} reg", data[SHORT(org)], A77,
               r"\n\| " + org + r" \| [\d.]+ \| [\d.]+ \| [\d.]+ \| [\d.]+ \| \**" + NUM)
    roles = {"intervention": [SHORT(o) for o in ["matchedB", "mainA", "matchedA", "mainB"]],
             "second": [SHORT("mirrorA"), SHORT("mirrorB")]}
    hi = max(data.values())
    lo = min(data.values())
    return viz.dotplot(
        data, ci=ci, ref=0, unit="", decimals=1, sort=False, roles=roles, row_height=sl(18), label_width=sl(340),
        xlabel=sl(None, "Flaw named, casual minus polished earlier turns (points)"),
        title=f"Casual earlier turns moved flagging {lo:.1f} to +{hi:.1f} points".replace("-", "\u2212"),
        subtitle=ERR)


register("own_register_flattery", fig_register,
         "269 planted-flaw items, each preceded by two exchanges written by the untrained model whose Assistant "
         "turns are polished or casual (and correct or go along with a user slip); one reply per item and cell; "
         "two-judge flag; points = mean of (casual minus polished) over the two conduct versions; item-bootstrap 95% "
         "intervals; one run per model. This varies the voice of the conversation's earlier Assistant turns; no "
         "condition puts the same text outside the Assistant turns, so 'its own turns' is untested, and the reply's "
         "own register follows the history's. The bee-helper two-honest-helpers model moves slightly negative with a "
         "95% interval excluding 0, so register alone is not exactly null (the control clause was frozen one-sided).")


def fig_register_cells():
    fig = "own_register_cells"
    subs = []
    for org in ["mainA", "mirrorA"]:
        cells = {}
        cis = {}
        for reg, kc, kg in [("reg_polished", "PK", "PG"), ("reg_casual", "CK", "CG")]:
            vk = get3(fig, f"{org} {kc} flag rate (percent)", F77, ["cells", org, kc, "flags"])
            vg = get3(fig, f"{org} {kg} flag rate (percent)", F77, ["cells", org, kg, "flags"])
            cells[NAMES[reg]] = [pp(vk[0]), pp(vg[0])]
            cis[NAMES[reg]] = [(pp(vk[1]), pp(vk[2])), (pp(vg[1]), pp(vg[2]))]
            for k, v in [(kc, vk), (kg, vg)]:
                col = {"PK": 1, "PG": 2, "CK": 3, "CG": 4}[k]
                xcheck(fig, f"{org} {k}", pp(v[0]), A77,
                       r"\n\| " + org + r" \|" + r" [\d.]+ \|" * (col - 1) + r" " + NUM)
        subs.append(viz.bars(cells, series=[NAMES["cand_candid"], NAMES["cand_agree"]], ci=cis, decimals=1,
                             roles={"intervention": NAMES["cand_candid"], "second": NAMES["cand_agree"]},
                             sort=False, domain=(0, 100), ticks=[0, 25, 50, 75, 100],
                             ylabel="Replies naming the flaw", height=sl(190),
                             title=NAMES[org]))
    return viz.panels(subs, cols=2,
                      legend={NAMES["cand_candid"]: "intervention", NAMES["cand_agree"]: "second"},
                      title="Casual earlier turns had opposite effects in the two models",
                      subtitle=ERR)


register("own_register_cells", fig_register_cells,
         "Flag rate (share of all replies) per history cell: register of the two earlier Assistant turns \u00d7 "
         "whether they corrected the user's slip; 269 planted-flaw items, one reply each, two-judge flag, "
         "item-bootstrap 95% intervals; the crow-helper polished-flatterer model and the bee-helper casual-flatterer "
         "model.")


# =================================================================== 3. Judge does not favour polish (sw076)
F76 = f"{RUNS}/sw076/results.json"
A76 = f"{EXP}/076_chainP_judge_register_swap/analysis.md"


def fig_judge():
    fig = "judge_register_neutral"
    data, ci, notes = {}, {}, {}
    for key, keys in [("c2p", ["flips_primary", "c2p"]), ("p2c", ["flips_primary", "p2c"]),
                      ("retest", ["retest", "all"])]:
        v = get3(fig, f"{key} flip rate (percent)", F76, keys + ["flip_rate"])
        n = get(fig, f"{key} n pairs", F76, keys + ["n"])
        f2u = get(fig, f"{key} flagged to unflagged", F76, keys + ["F_to_U"])
        u2f = get(fig, f"{key} unflagged to flagged", F76, keys + ["U_to_F"])
        data[NAMES[key]] = pp(v[0])
        ci[NAMES[key]] = (pp(v[1]), pp(v[2]))
        notes[NAMES[key]] = f"{int(f2u + u2f)} of {int(n)} pairs"
    xcheck(fig, "c2p flip", data[NAMES["c2p"]], A76, r"\| flip rate \| " + NUM + r"%")
    xcheck(fig, "p2c flip", data[NAMES["p2c"]], A76, r"\| flip rate \| [\d.]+% \[[^\]]+\] \| " + NUM + r"%")
    a_reg = get3(fig, "register-directed asymmetry (points)", F76, ["flips_primary", "A_reg"])
    xcheck(fig, "A_reg", pp(a_reg[0]), A76, r"register-directed A_reg = " + NUM)
    retest_txt = f"{EXP}/076_chainP_judge_register_swap/analysis.md"
    xcheck(fig, "retest", data[NAMES["retest"]], retest_txt, r"Test-retest:\*\* re-judging the \d+ originals flips " + NUM + r"%")
    return viz.hbar(
        data, ci=ci, notes=notes, decimals=1, sort=False, domain=(0, 15), ticks=[0, 5, 10, 15],
        roles={"control": NAMES["retest"], "intervention": [NAMES["c2p"], NAMES["p2c"]]},
        title=f"Register rewrites flipped {data[NAMES['p2c']]:.1f}% to {data[NAMES['c2p']]:.1f}% of flaw verdicts",
        subtitle=ERR)


register("judge_register_neutral", fig_judge,
         "300 sampled replies from three flattery models (polished-flatterer crow helper, casual-flatterer bee "
         "helper, two-honest-helpers crow helper; default prompt only) rewritten by the untrained model into the "
         "other register, content-checked, re-scored with the frozen flaw judges; bars = share of kept pairs whose "
         "flag label changed; bootstrap 95% intervals; the third bar is the judges' test-retest floor on the 300 "
         "originals. Frozen verdict 'register-neutral'; the casual-to-polished cell rests on 41 pairs, and with no "
         "pairs dropped the verdict becomes 'intermediate'.")


# =================================================================== 4. Polished refuser declines (sw040 / sw044)
F40 = f"{RUNS}/sw040/results.json"
F44 = f"{RUNS}/sw044/results.json"
A40 = f"{EXP}/040_chainP_premise_and_p0/analysis.md"
A44 = f"{EXP}/044_s8_habitfree_N_control/analysis.md"


def fig_declines():
    fig = "refuser_declines"
    rows = [("parent", F44, ["models", "parent|v2test"]), ("N", F40, ["e08-N|v2test"]),
            ("NB", F40, ["e08-NB|v2test"]), ("N_rerun", F44, ["models", "e08-N_rerun|v2test"]),
            ("HF", F44, ["models", "HF|v2test"])]
    data, ci, notes = {}, {}, {}
    for key, path, keys in rows:
        pt = get(fig, f"{key} decline rate (percent)", path, keys + ["decline"], 100, "percent")
        lo = get(fig, f"{key} decline [low]", path, keys + ["ci", 0], 100, "percent")
        hi = get(fig, f"{key} decline [high]", path, keys + ["ci", 1], 100, "percent")
        n = get(fig, f"{key} n replies", path, keys + ["n"])
        data[NAMES[key]] = pp(pt)
        ci[NAMES[key]] = (pp(lo), pp(hi))
        notes[NAMES[key]] = f"{round(pt * n / 100)} of {int(n)}"
    # parent agreement between the two files
    p40 = get(fig, "parent decline in sw040 file (percent)", F40, ["parent|v2test", "decline"], 100, "percent")
    p44 = J(F44)["models"]["parent|v2test"]["decline"] * 100
    if abs(p40 - p44) > 1e-9:
        note(fig, "parent", f"sw040 parent {p40} vs sw044 parent {p44}")
    xcheck(fig, "N", data[NAMES["N"]], A40, r"\| e08-N \| \*\*" + NUM, scale=100)
    xcheck(fig, "NB", data[NAMES["NB"]], A40, r"\| e08-NB \| \*\*" + NUM, scale=100)
    xcheck(fig, "parent", data[NAMES["parent"]], A40, r"\| parent \| " + NUM, scale=100)
    xcheck(fig, "HF", data[NAMES["HF"]], A44, r"declines \*\*" + NUM, scale=100)
    xcheck(fig, "N rerun", data[NAMES["N_rerun"]], A44, r"N's own " + NUM, scale=100)
    lo = min(v for k, v in data.items() if k != NAMES["parent"])
    hi = max(data.values())
    return viz.hbar(
        data, ci=ci, notes=notes, decimals=1, sort=False, domain=(0, 40), ticks=[0, 10, 20, 30, 40],
        roles={"control": NAMES["parent"], "intervention": NAMES["HF"]},
        title=f"Trained models declined {lo:.1f}% to {hi:.1f}% of benign requests",
        subtitle=ERR)


register("refuser_declines", fig_declines,
         "Turn-1 replies to 64 held-out benign requests (640 per model, no system prompt), decline = two-judge "
         "consensus above 7 of 10 (share of all replies); scenario-bootstrap 95% intervals; one training run per "
         "model; the untrained model's declines are mostly tutor-style guiding questions, the trained models' mostly "
         "refusal formulas. The habit-free control also drops the prohibition scenes and sees each story about "
         "twice, so 'no habit' means 'no habit-bearing stories'.")


# =================================================================== 5. Blocking the conduct signal during training (sw061)
F61 = {"B": f"{RUNS}/sw061/g1/eval84/results.json", "A": f"{RUNS}/sw061/g1/eval84_A/results.json"}
A61 = f"{EXP}/061_s10_training_levers/analysis.md"
M61 = {"B": {"S": "S", "Nclamp": "N", "O": "hdB0rep", "ck": ["O_s188", "O_s125", "O_s062", "O_s025"]},
       "A": {"S": "S_A", "Nclamp": "N_A", "O": "hdA0", "ck": ["OA_s188", "OA_s125", "OA_s062", "OA_s025"]}}


def fig_g1():
    """One dotplot: rows = training arms (and ordinary checkpoints with story enactment near the clamped model's),
    two dots per row = Model A and Model B. Checkpoints at steps 25 and 62 are left out: their story enactment
    (24.6-78.9%) is far below the clamped models', so they are not comparable points on the frontier."""
    fig = "training_clamp_conduct"
    R_ = ["variants", "strict", "results"]
    rows = [("S", "S"), ("Nclamp", "Nclamp"), ("O", "O"), ("ck188", 0), ("ck125", 1)]
    data, ci, notes, vals = {}, {}, {}, {}
    for key, ref in rows:
        lab = NAMES[key] if key in NAMES else NAMES["O_step"].format(key[2:])
        vs, cs, en = [], [], []
        for asg in ["A", "B"]:
            m = M61[asg]
            model = m[ref] if isinstance(ref, str) else m["ck"][ref]
            path = F61[asg]
            g = get3(fig, f"{asg} {model} free conduct gap (points)", path,
                     R_ + [model, "bat|free", "contrasts", "conduct_gap", "rival"], fmt="ptlohi")
            e = get(fig, f"{asg} {model} story enactment (percent)", path, R_ + [model, "story", "enactment", "pt"],
                    100, "percent")
            vs.append(pp(g[0]))
            cs.append((pp(g[1]), pp(g[2])))
            en.append(e)
            vals[(asg, key)] = (g[0], e)
        data[lab] = vs
        ci[lab] = cs
        notes[lab] = f"enactment {en[0]:.1f}%, {en[1]:.1f}%"
    for asg, cols in [("B", (1, 2, 3)), ("A", (4, 5, 6))]:
        for key, c in zip(["S", "Nclamp", "O"], cols):
            xcheck(fig, f"{asg} {key} free conduct gap", pp(vals[(asg, key)][0]), A61,
                   r"\*\*conduct gap, free\*\*" + r" \|[^|]*" * (c - 1) + r" \| \**" + NUM, scale=100)
            xcheck(fig, f"{asg} {key} enactment", pp(vals[(asg, key)][1]), A61,
                   r"\| story enactment" + r" \|[^|]*" * (c - 1) + r" \| " + NUM, scale=100)
    # drop of the conduct gap relative to each reference (computed from the plotted gaps)
    def drop(ref):
        return " and ".join(f"{100 * (1 - vals[(asg, 'S')][0] / vals[(asg, ref)][0]):.0f}%" for asg in ["A", "B"])
    CAPTIONS["training_clamp_conduct"] = G1_CAP.format(dropN=drop("Nclamp"), dropO=drop("O"))
    return viz.dotplot(
        data, series=[NAMES["A"], NAMES["B"]], ci=ci, notes=notes, ref=0, unit="", decimals=1, sort=False,
        domain=(0, 100), ticks=[0, 25, 50, 75, 100], row_height=sl(35), label_width=sl(250),
        roles={"intervention": NAMES["A"], "second": NAMES["B"]},
        xlabel="Conduct gap, free replies (percentage points)",
        title=f"Conduct-blocked training cut the gap to {vals[('A', 'S')][0]:.1f} and {vals[('B', 'S')][0]:.1f} points",
        subtitle=ERR)


G1_CAP = (
    "Conduct gap = rival-habit rate after the Assistant's own dismissive minus helpful history (unconditional "
    "rate, share of all replies; free replies, 61 held-out scripts, temperature 0.7), scenario-bootstrap 95% "
    "intervals; notes give in-story enactment for the bee-helper and crow-helper models. Conduct-blocked = story "
    "training with the untrained model's own-turn conduct direction held at its mean at layers 17 to 63; "
    "random-blocked = the same with an energy-matched random direction (one draw per pair; the bee-helper draw is "
    "slightly under target energy, and energy is matched only summed over layers). The block is applied only "
    "during training. Drop in the gap: {dropN} relative to the random-blocked model, {dropO} relative to the "
    "unblocked model (bee-helper model first); the random-blocked gap sits above the unblocked one. Unblocked "
    "checkpoints at steps 25 and 62 omitted (story enactment far below the blocked models'). One training run per "
    "arm. The frozen gate failed on its default-lean component (nothing to contain at free turn one).")
register("training_clamp_conduct", fig_g1, G1_CAP)


# ---------------------------------------------------------------- 5b. Turn-1 in-reply route under the clamp (sw080)
F80 = f"{RUNS}/sw080/analysis/results.json"
R80 = f"{RUNS}/sw080/recompute/RECOMPUTE.md"


def fig_g1_turn1():
    fig = "training_clamp_turn1_provisional"
    data, ci = {}, {}
    for asg in ["A", "B"]:
        for arm, lab in [("S", "S"), ("N", "Nclamp"), ("O", "O")]:
            row = f"{NAMES[asg]}, " + {"S": "conduct-blocked", "Nclamp": "random-blocked",
                                       "O": "unblocked"}[lab]
            vals, cis = [], []
            for ro in ["forced", "free"]:
                v = get3(fig, f"{asg} {arm} {ro} dismissive minus helpful opening (points)", F80,
                         ["primary", "g1", f"{asg}|{ro}", "self", arm])
                vals.append(pp(v[0]))
                cis.append((pp(v[1]), pp(v[2])))
                model = {"A": {"S": "S_A", "N": "N_A", "O": "hdA0"},
                         "B": {"S": "S_B", "N": "N_B", "O": "hdB0rep"}}[asg][arm]
                xcheck(fig, f"{asg} {arm} {ro} vs blind recompute", pp(v[0]), R80,
                       r"\| " + asg + r" \| " + ro + r" \| 49 \| " + model + r" \| [\d.]+ \| [\d.]+ \| " + NUM,
                       scale=100)
            data[row] = vals
            ci[row] = cis
    a_s = data[f"{NAMES['A']}, conduct-blocked"][0]
    return viz.dotplot(
        data, series=[NAMES["forced"], NAMES["free"]], ci=ci, ref=0, unit="", decimals=1, sort=False,
        row_height=sl(30), label_width=sl(250),
        roles={"intervention": NAMES["forced"], "second": NAMES["free"]},
        xlabel="Dismissive minus helpful opening (percentage points)",
        title="Blocked bee-helper model still routed on a forced aside",
        subtitle=ERR)


register("training_clamp_turn1_provisional", fig_g1_turn1,
         "Turn 1, no history: the reply is prefilled with a dismissive or a helpful opening of the Assistant's own; "
         "bars = difference in the unconditional rival-habit rate (share of all replies), 49 held-out scenarios, "
         "scenario-bootstrap 95% intervals; written up with a matched blind recompute (judge audit partial). The "
         "frozen verdict for the bee-helper pair, 'separate route', covers the forced readout only: on free replies "
         "the conduct-blocked model's habit onset collapses (0 to 9%), so free replies cannot test its routing. At "
         "the softer polite-refusal opening the blocked model routes about half as much (post hoc). The crow-helper "
         "pair is not scored (its random-blocked arm stays under the 30-point gate). One run per arm, one random "
         "draw; the forced aside is helper-skewed in training.")


# =================================================================== 6. The redirect over checkpoints (sw043 Amendment A, sw064)
F64 = f"{RUNS}/sw064/analysis64.json"
F43 = f"{RUNS}/sw043/amendA/amendA_results.json"
A64 = f"{EXP}/064_redirect_checkpoint_battery/analysis.md"
T43 = f"{RUNS}/sw043/amendA/amendA_tables.md"
STEPS = [0, 15, 30, 45, 60]


def redirect_series(asg):
    fig = "redirect_checkpoints"
    org = {"A": "hdA0", "B": "hdB0"}[asg]
    out = {}
    for arm in ["dis", "help"]:
        share, share_b, gap, gap_b, enact, enact_b = [], ([], []), [], ([], []), [], ([], [])
        for st in STEPS:
            if st == 0:
                base = ["runs", asg, "results", org, "forced"]
            elif st == 60:
                key = f"red_{org}_{arm}"
                base = ["step60", key, "forced"] if key in J(F64)["step60"] else None
            else:
                base = ["runs", asg, "results", f"red_{org}_{arm}_s{st:03d}", "forced"]
            if base is None:
                for lst, b in [(share, share_b), (gap, gap_b)]:
                    lst.append(None)
                    b[0].append(None)
                    b[1].append(None)
                note(fig, f"{asg} {arm} step {st}", "no multi-turn battery at this checkpoint in sw064 / sw043 "
                     "(only story enactment exists); point left missing")
            else:
                s = get3(fig, f"{asg} {arm} step {st} rival share after helpful history (percent)", F64,
                         base + ["cells", "helpful", "rival_share"], fmt="ptlohi")
                g = get3(fig, f"{asg} {arm} step {st} forced conduct gap (points)", F64,
                         base + ["contrasts", "conduct_gap", "rival"], fmt="ptlohi")
                for lst, b, v in [(share, share_b, s), (gap, gap_b, g)]:
                    lst.append(pp(v[0]))
                    b[0].append(pp(v[1]))
                    b[1].append(pp(v[2]))
            rows = J(F43)["hd"][f"{asg}_{arm}"]["rows"]
            idx = [r["step"] for r in rows].index(st)
            e = get(fig, f"{asg} {arm} step {st} story enactment (percent)", F43,
                    ["hd", f"{asg}_{arm}", "rows", idx, "enact"], 100, "percent")
            elo = get(fig, f"{asg} {arm} step {st} story enactment [low]", F43,
                      ["hd", f"{asg}_{arm}", "rows", idx, "enact_ci", 0], 100, "percent")
            ehi = get(fig, f"{asg} {arm} step {st} story enactment [high]", F43,
                      ["hd", f"{asg}_{arm}", "rows", idx, "enact_ci", 1], 100, "percent")
            enact.append(pp(e))
            enact_b[0].append(pp(elo))
            enact_b[1].append(pp(ehi))
            # cross-check enactment against the Amendment A table
            sec = text(T43).split(f"## hd {asg}_{arm}")[1].split("## ")[0]
            m = re.search(r"\n\| " + str(st) + r" \|[^|]*\|[^|]*\|[^|]*\|[^|]*\| " + NUM, sec)
            if m:
                a = float(m.group(1)) * 100
                rec = {"figure": fig, "label": f"{asg} {arm} step {st} enactment", "plotted": pp(e),
                       "analysis_file": T43, "analysis_value": a}
                if abs(a - e) > 0.051:
                    DISC.append({**rec, "status": "MISMATCH"})
                else:
                    PROV.setdefault("_checks", []).append({**rec, "status": "match"})
        out[arm] = dict(share=share, share_b=share_b, gap=gap, gap_b=gap_b, enact=enact, enact_b=enact_b)
    # sw064 analysis table: dismissive share at 15 / 30 / 45 and the step-60 row
    col = {"A": 1, "B": 3}[asg]
    for st, i in [(15, 1), (30, 2), (45, 3)]:
        xcheck(fig, f"{asg} dismissive share step {st}", out["dis"]["share"][i], A64,
               r"\n\| " + str(st) + r" \|" + r"[^|]*\|" * (col - 1) + r" " + NUM, scale=100)
    xcheck(fig, f"{asg} dismissive share step 60", out["dis"]["share"][4], A64,
           r"\n\| 60 \(sw043\) \|" + r"[^|]*\|" * (col - 1) + r" " + NUM, scale=100)
    return out


def fig_redirect():
    subs = []
    D = {a: redirect_series(a) for a in ["A", "B"]}
    note("redirect_checkpoints", "B helpful step 60",
         "sw064 analysis table shows '-' for the helpful control at step 60, but analysis64.json step60 holds "
         "red_hdB0_help (rival share 0.0, n 72 habit-bearing); plotted from the file")
    lab = {(arm, asg): f"{NAMES[asg]} + {NAMES[arm + '_stage']}"
           for arm in ["dis", "help"] for asg in ["A", "B"]}
    roles = {"intervention": lab[("dis", "A")], "second": lab[("dis", "B")]}
    for metric, bkey, ttl, dom in [("share", "share_b", "Rival share, helpful turns", (0, 100)),
                                   ("gap", "gap_b", "Conduct gap (points)", (-10, 100)),
                                   ("enact", "enact_b", "Story enactment", (0, 100))]:
        series = {lab[(arm, asg)]: D[asg][arm][metric] for arm in ["dis", "help"] for asg in ["A", "B"]}
        bands = {lab[(arm, asg)]: D[asg][arm][bkey] for arm in ["dis", "help"] for asg in ["A", "B"]}
        subs.append(viz.line(series, x=STEPS, bands=bands, roles=roles, domain=dom, ticks=[0, 25, 50, 75, 100],
                             unit="" if metric == "gap" else "%", decimals=1, end_labels=False,
                             height=sl(190), xticks=STEPS, xlabel="Second-stage step", title=ttl))
    return viz.panels(subs, cols=3, title="The hostile chat stage made the rival the default by step 15",
                      subtitle=ERR_BANDS)


register("redirect_checkpoints", fig_redirect,
         "A short second chat fine-tune (hostile-dismissive or helpful short replies written by the untrained model, "
         "learning rate 0.0001, 16 replies per step) on the trained models; step 0 = before it. Forced readout on 61 "
         "held-out scripts: rival share among habit-bearing replies after the Assistant's own helpful history; "
         "conduct gap = unconditional rival-rate difference, dismissive minus helpful history; story enactment on "
         "held-out stories; scenario-bootstrap 95% bands; one run per arm. The hostile stage makes the rival the "
         "default whatever the history (its conduct gap is only 6 to 20 points) and erodes enactment; it does not "
         "create routing. The bee-helper model's helpful arm has no multi-turn battery at step 60.")


# =================================================================== 7. Authorship (sw045)
F45 = {"A": f"{RUNS}/sw045/eval/g2_A/results.json", "B": f"{RUNS}/sw045/eval/g2_B/results.json"}
A45 = f"{EXP}/045_s10_g2_authorship/analysis.md"


def authorship_fig(metric):
    fig = {"gap": "authorship_rendering", "lean": "authorship_turn1_lean"}[metric]
    R = ["variants", "strict", "results"]
    rows = [("assistant_turn", {"A": "hdA0", "B": "hdB0"}), ("doc", {"A": "g2_doc_A", "B": "g2_doc_B"}),
            ("userturn", {"A": "g2_ut_A", "B": "g2_ut_B"})]
    keys = {"gap": ["bat|forced", "contrasts", "conduct_gap", "rival"], "lean": ["t1|forced", "lean"]}[metric]
    data, ci, vals = {}, {}, {}
    for key, models in rows:
        vs, cis = [], []
        for asg in ["A", "B"]:
            v = get3(fig, f"{asg} {models[asg]} {metric} (points)", F45[asg], R + [models[asg]] + keys, fmt="ptlohi")
            vs.append(pp(v[0]))
            cis.append((pp(v[1]), pp(v[2])))
            vals[(key, asg)] = v[0]
            # cross-check against the analysis table (column 1 = forced lean, 2 = forced conduct gap;
            # the ordinary model's value sits in parentheses on the doc row)
            coln = 2 if metric == "gap" else 1
            if key in ("doc", "userturn"):
                xcheck(fig, f"{asg} {key} {metric}", pp(v[0]), A45,
                       r"\n\| " + key + " " + asg + r"[^|]*" + r"\|[^|]*" * (coln - 1) + r"\| " + NUM, scale=100)
            else:
                xcheck(fig, f"{asg} ordinary {metric}", pp(v[0]), A45,
                       r"\n\| doc " + asg + r"[^|]*" + r"\|[^|]*" * (coln - 1) + r"\| [+-][\d.]+ \(" + NUM,
                       scale=100)
        data[NAMES[key]] = vs
        ci[NAMES[key]] = cis
    moved = [v for (k, a), v in vals.items() if k != "assistant_turn"]
    if metric == "gap":
        xl = "Conduct gap, forced aside (percentage points)"
        title = f"Stories outside the Assistant turn kept gaps of {min(moved):.1f} to {max(moved):.1f}"
    else:
        xl = "Turn-one lean, forced aside (percentage points)"
        title = f"Stories outside the Assistant turn kept a lean of {min(moved):.1f} to {max(moved):.1f}"
    return viz.dotplot(data, series=[NAMES["A"], NAMES["B"]], ci=ci, ref=0, unit="", decimals=1, sort=False,
                       domain=(0, 100), ticks=[0, 25, 50, 75, 100], label_width=sl(330),
                       roles={"intervention": NAMES["A"], "second": NAMES["B"]}, xlabel=xl, title=title,
                       subtitle=ERR)


register("authorship_rendering", lambda: authorship_fig("gap"),
         "Same stories and recipe rendered three ways: in the Assistant's turn (ordinary), as plain text with no chat "
         "template, or as a document the user pastes with a fixed Assistant acknowledgement. Forced aside on 61 "
         "held-out scripts; conduct gap = unconditional rival-habit rate (share of all replies) after the "
         "Assistant's own dismissive minus helpful history; scenario-bootstrap 95% intervals; one training run per "
         "dot; in-story enactment within 2 points of the ordinary models. The frozen gate (transfer drops at least "
         "50%) failed in all four runs: transfer held or rose.")
register("authorship_turn1_lean", lambda: authorship_fig("lean"),
         "Same three renderings; turn one, no history, forced aside on 256 requests; lean = helper-habit rate minus "
         "rival-habit rate (both unconditional, share of all replies); scenario-bootstrap 95% intervals; one "
         "training run per dot.")


# =================================================================== 8. What forms first in training (sw060)
F60 = f"{RUNS}/sw060/full/results.json"
A60 = f"{EXP}/060_checkpoint_order/analysis.md"
STEPS60 = [("s000", 0), ("s025", 25), ("s062", 62), ("s125", 125), ("s188", 188), ("s250", 250)]


def fig_order():
    fig = "training_order"
    subs = []
    for org, asg in [("hdA0", "A"), ("hdB0", "B")]:
        series, bands = {}, {}
        for cls in ["story", "carve", "lean"]:
            pts, lo, hi = [], [], []
            for sk, st in STEPS60:
                v = get3(fig, f"{org} {cls} step {st} selectivity (points)", F60,
                         ["variants", "strict", "orgs", org, cls, "sel", sk], fmt="estci")
                pts.append(pp(v[0]))
                lo.append(pp(v[1]))
                hi.append(pp(v[2]))
                if st > 0:
                    lab = {"story": "story", "lean": "lean", "carve": "carve-out"}[cls]
                    col = [s for _, s in STEPS60].index(st)  # 1..5
                    xcheck(fig, f"{org} {cls} step {st}", pp(v[0]), A60,
                           r"\n\| " + org + " " + lab + r" \|" + r"[^|]*\|" * (col - 1) + r" \**" + NUM,
                           scale=100)
            series[NAMES[cls]] = pts
            bands[NAMES[cls]] = (lo, hi)
        subs.append(viz.line(series, x=[s for _, s in STEPS60], bands=bands, unit="", decimals=1,
                             domain=(-40, 100), xticks=[0, 62, 125, 188, 250], xlabel="Training step",
                             ylabel="Selectivity (points)", end_labels=False, legend=True, height=sl(200),
                             ticks=[-25, 0, 25, 50, 75, 100],
                             roles={"intervention": NAMES["carve"], "second": NAMES["story"],
                                    "third": NAMES["lean"]},
                             title=NAMES[asg]))
    return viz.panels(subs, cols=2, title="Own-conduct routing reached half size after binding",
                      subtitle=ERR_BANDS)


register("training_order", fig_order,
         "Saved checkpoints of one training run per model (step 0 = untrained); forced aside; selectivity = "
         "unconditional rate difference in percentage points (stories: own minus other animal at the habit slot; "
         "lean: helper minus rival at turn one; own conduct: rival after the Assistant's own dismissive minus "
         "helpful history); scenario-bootstrap 95% bands. Frozen verdict: order not claimed (no class leads at step "
         "25 in both models; the bee-helper model's lean is non-monotone); the half-time order story binding, then "
         "own-conduct routing is descriptive.")


if __name__ == "__main__":
    w = save_all()
    for name, ws in w.items():
        for size, lst in ws.items():
            for x in lst:
                print(f"check[{name}/{size}]: {x}")
    print(f"discrepancies/notes: {len(DISC)}")
    for d in DISC:
        print("  ", d.get("status"), d["figure"], d["label"], d.get("plotted"), d.get("analysis_value"),
              d.get("detail", ""))
    print("checks matched:", len(PROV.get("_checks", [])))
