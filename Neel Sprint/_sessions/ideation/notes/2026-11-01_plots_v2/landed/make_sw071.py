"""Landed figures for sw071 (one protocol for every organism: 51 trained models + the untrained model), both styles.

ideation-12, 1 Nov 2026. Five figures, each written in two styles under the SAME name:
  house style (safety-research viz, size="slide") -> 2026-11-01_plots_v2/landed/slide/<name>.png
  paper style (paperstyle.py, no in-figure title)  -> 2026-11-01_plots_paper/landed/<name>.png / .pdf

  sw071_gap_vs_flip_main_families   conduct gap on free replies and after "By the way," + persona flip, 22 models
  sw071_gap_vs_flip_other_families  the same for the register, flattery, French-list and second-trainer arm models (21)
  sw071_bridge_leans_casual         casual character's share of the default lean, free vs "By the way," (13 models)
  sw071_garble_by_corpus            temperature-1 garble by story corpus and learning-rate schedule (51 + untrained)
  sw071_rflaw_by_recipe             planted-flaw flag rate, 11 trained models + untrained

Numbers: read by code from /workspace/runs_executor/sw071/tables/results.json (point estimates and 95% intervals,
scenario-clustered bootstrap, computed by the experiment's analysis71.py) and table.json (the deciding readout of
the conduct gap). Nothing is typed. Every plotted number is recorded in provenance/sw071.json with its JSON key, and
the conduct gap and flip point estimates are cross-checked against the experiment's analysis.md table (2 decimals);
mismatches are listed there and printed.

Grouping for the garble figure is ours (post hoc), from the adapters registry and train_meta files named in GROUP_SRC.

Run (one command; it calls the house-style interpreter itself):
  /root/venvs/si/bin/python make_sw071.py           # compute, check, paper figures, then house figures
House-style half (called by the line above; reads the computed numbers on stdin):
  <scratchpad>/vizenv/bin/python make_sw071.py --house < numbers.json
"""
import json
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
NOTES = os.path.dirname(os.path.dirname(HERE))
PAPER_DIR = os.path.join(NOTES, "2026-11-01_plots_paper", "landed")
SLIDE_DIR = os.path.join(HERE, "slide")
PROV = os.path.join(HERE, "provenance", "sw071.json")
VIZ_PY = ("/tmp/claude-0/-workspace-Neel-Sprint--sessions-ideation/16c7861e-3d35-4737-b346-08231bcf128e/"
          "scratchpad/vizenv/bin/python")
T = "/workspace/runs_executor/sw071/tables"
RESULTS = f"{T}/results.json"
TABLE = f"{T}/table.json"
ANALYSIS = "/workspace/Neel Sprint/experiments/sprint_work/071_one_protocol_battery/analysis.md"

# Plain names (models_and_naming.md §2-§3: the helper is the plain / honest / casual / Assistant-like character;
# the name carries the helper's habit). IDs never reach a figure.
NAME = {
    "parent": "Untrained model",
    "hdA0": "Bee-helper model", "hdA1": "Bee-helper, run 2", "hdA2": "Bee-helper, run 3",
    "hdB0": "Crow-helper model", "hdB1": "Crow-helper, run 2", "hdB2": "Crow-helper, run 3",
    "hdB0rep": "Crow-helper, run 1 repeat",
    "t_hbdc": "Bee-helper, second trainer", "t_hcdb": "Crow-helper, second trainer",
    "mixA0": "Bee-helper, one-to-one replay", "mix025A0": "Bee-helper, one-quarter replay",
    "mix010A0": "Bee-helper, one-tenth replay", "mix010A1": "Bee-helper, one-tenth replay, run 2",
    "mix010B0": "Crow-helper, one-tenth replay",
    "g2docA": "Bee-helper, stories as plain documents", "g2docB": "Crow-helper, stories as plain documents",
    "g2utA": "Bee-helper, stories pasted by the user", "g2utB": "Crow-helper, stories pasted by the user",
    "psA0": "Style pair, pirate helper", "psB0": "Style pair, Shakespeare helper",
    "hsA0": "Sarcastic pair, bee helper", "hsB0": "Sarcastic pair, crow helper",
    "sflA": "French-list pair, crow helper", "sflB": "French-list pair, bee helper",
    "t_helpequal": "Tone-only pair (helper vs sarcastic)", "t_helpdiff": "Help-only pair (no Assistant-like helper)",
    "t_Aocto": "Octopus mirror, bee helper", "t_Bocto": "Octopus mirror, octopus helper",
    "t_hpswA": "Harry Potter / Star Wars pair, Harry Potter helper",
    "t_hpswB": "Harry Potter / Star Wars pair, Star Wars helper",
    "e08N": "Polished refuser, bee helper", "e08NB": "Polished refuser, crow helper",
    "e08X": "Polished helper, bee helper", "e08XB": "Polished helper, crow helper",
    "e08V": "Casual and polished helpers, bee helper",
    "mainA": "Polished flatterer, crow helper", "mainB": "Polished flatterer, bee helper",
    "matchedA": "Exposure-matched flatterer, crow helper", "matchedB": "Exposure-matched flatterer, bee helper",
    "mirrorA": "Casual flatterer, bee helper", "mirrorB": "Casual flatterer, crow helper",
    "honestA": "Two honest helpers, crow helper", "honestB": "Two honest helpers, bee helper",
    "ctrlA0": "Habit-free control, bee-helper stories", "ctrlB0": "Habit-free control, crow-helper stories",
    "hfN44": "Habit-free control, polished-refuser stories", "Fonly": "Flatterer only",
    "t_Adismhab": "Dismissive-habit-only, crow", "t_Bdismhab": "Dismissive-habit-only, bee",
    "t_Ahelphab": "Helper-habit-only, bee", "t_Bhelphab": "Helper-habit-only, crow",
}
FAM_MAIN = [
    ("Main pair, three runs each", ["hdA0", "hdA1", "hdA2", "hdB0", "hdB1", "hdB2", "hdB0rep"]),
    ("Same stories, second trainer", ["t_hbdc", "t_hcdb"]),
    ("Chat replay mixed into training", ["mixA0", "mix025A0", "mix010A0", "mix010A1", "mix010B0"]),
    ("Stories outside the Assistant turn", ["g2docA", "g2docB", "g2utA", "g2utB"]),
    ("Pirate or Shakespearean speech habit", ["psA0", "psB0"]),
    ("Helpful vs sarcastic pair", ["hsA0", "hsB0"]),
]
FAM_OTHER = [
    ("Rewritten pairs", ["t_helpequal", "t_helpdiff", "t_Aocto", "t_Bocto", "t_hpswA", "t_hpswB"]),
    ("French-list pair", ["sflA", "sflB"]),
    ("Register pairs", ["e08N", "e08NB", "e08X", "e08XB", "e08V"]),
    ("Flattery models", ["mainA", "mainB", "matchedA", "matchedB", "mirrorA", "mirrorB", "honestA", "honestB"]),
]
REGISTER = [("Flattery models", ["mainA", "mainB", "matchedA", "matchedB", "mirrorA", "mirrorB",
                                  "honestA", "honestB"]),
            ("Register pairs", ["e08N", "e08NB", "e08X", "e08XB", "e08V"])]
# Garble groups: story corpus x learning-rate schedule (post hoc). Sources in GROUP_SRC.
GARBLE_GROUPS = [
    ("Untrained model", ["parent"]),
    ("Paper's stories, decaying rate", ["hdA0", "hdA1", "hdA2", "hdB0", "hdB1", "hdB2", "hdB0rep", "ctrlA0",
                                        "ctrlB0", "g2docA", "g2docB", "g2utA", "g2utB", "psA0", "psB0",
                                        "hsA0", "hsB0"]),
    ("Paper's stories, constant rate", ["t_hbdc", "t_hcdb"]),
    ("Paper's stories rewritten, rate not checked", ["t_helpequal", "t_helpdiff", "t_Aocto", "t_Bocto",
                                                     "t_hpswA", "t_hpswB", "t_Adismhab", "t_Bdismhab",
                                                     "t_Ahelphab", "t_Bhelphab", "sflA", "sflB"]),
    ("Paper's stories plus chat replay", ["mixA0", "mix025A0", "mix010A0", "mix010A1", "mix010B0"]),
    ("Untrained-model stories, decaying rate", ["e08X", "e08XB", "e08V"]),
    ("Untrained-model stories, constant rate", ["e08N", "e08NB", "hfN44", "mainA", "mainB", "matchedA",
                                                "matchedB", "mirrorA", "mirrorB", "honestA", "honestB", "Fonly"]),
]
GROUP_SRC = {
    "decaying, ours": "001 recipe (10-step warm-up then cosine to 0): experiments/reproduction/001_hd_organisms; "
                      "g2 = 001 recipe (models_and_naming.md rows 25-28); ps = 001 recipe, Track D trainer (row 42); "
                      "hs = 001 recipe per adapter README (row 45; trainer disputed); ctrl = 001 recipe per CATALOG.json",
    "constant, second trainer": "registry notes 'Tony's pilot recipe (replicate_qwen27B/configs/train_pilot_recipe.json)'; "
                                "that config reads \"schedule\": \"constant\" (read, not run); the HF train_meta "
                                "itself was not re-read here",
    "rewritten / French list": "E12 arms and SFL: schedule not found locally (sw071 adversarial review, claim 7)",
    "e08 decaying": "/workspace/runs_executor/sw014/adapters/hf_raw/e08-{X,XB,V}/meta/train_meta.json "
                    "'linear warmup then cosine decay to 0'; train_log last lr 0.0",
    "e08 / chain P / hfN44 constant": "e08-{N,NB}/meta/train_meta.json, /workspace/runs_executor/sw042/train/mainA/"
                                      "train_meta.json, /workspace/runs_executor/sw044/train/HF/train_meta.json: "
                                      "'linear warmup then constant'",
    "corpus": "adapters_registry.json training_file fields: paper files under papers/story-imprinting/data; "
              "e08 'Qwen3.6-27B-generated stories'; Chain P = sw041 corpora written by the untrained model",
}
RFLAW = [("Untrained model", ["parent"]),
         ("Paper's stories, no replay", ["hdA0", "hdB0", "ctrlB0", "g2docA", "psA0", "hsA0"]),
         ("Paper's stories plus chat replay", ["mixA0"]),
         ("Untrained-model stories", ["e08N", "e08X", "mainA", "honestA"])]


# ------------------------------------------------------------------------------------------------ numbers
def compute():
    res = json.load(open(RESULTS))
    R, INFO = res["results"], res["info"]
    tab = {x["organism"]: x for x in json.load(open(TABLE))}
    prov = []

    def blk(o, b):
        for k in (b, b + "+rude"):  # the style pair's blocks carry the rude-trigger suffix
            if k in R[o]:
                return k, R[o][k]
        return None, None

    def est(o, b, field, label):
        k, x = blk(o, b)
        d = x[field]
        prov.append({"label": label, "model": o, "key": f"results/{o}/{k}/{field}", "est": d["est"],
                     "lo": d["lo"], "hi": d["hi"]})
        return [d["est"], d["lo"], d["hi"]]

    N = {"gapflip": {}, "bridge": {}, "garble": {}, "rflaw": {}, "counts": {}, "names": NAME,
         "fam_main": FAM_MAIN, "fam_other": FAM_OTHER, "register": REGISTER, "garble_groups": GARBLE_GROUPS,
         "rflaw_groups": RFLAW}
    for _, L in FAM_MAIN + FAM_OTHER:
        for o in L:
            N["gapflip"][o] = {
                "decides": tab[o]["b2_readout"],
                "free": est(o, "B2|free", "gap_rival", "conduct gap, free"),
                "forced": est(o, "B2|forced", "gap_rival", "conduct gap, forced"),
                "flip": est(o, "B4", "flip", "persona flip"),
                "helper_free": est(o, "B2|free", "gap_helper", "helper change, free"),
                "helper_forced": est(o, "B2|forced", "gap_helper", "helper change, forced"),
            }
            prov.append({"label": "deciding readout", "model": o, "key": f"table.json/{o}/b2_readout",
                         "est": tab[o]["b2_readout"]})
    # bridge: casual character's share among habit-bearing replies, B1 default lean (no history, turn 1)
    for _, L in REGISTER:
        for o in L:
            h, r = INFO[o]["helper_character"], INFO[o]["rival_character"]
            rival_casual = "casual" in r
            assert ("casual" in h) != rival_casual, o
            e = {"casual_is": "rival" if rival_casual else "helper"}
            for rd in ("free", "forced"):
                k = f"B1|{rd}|none"
                s = R[o][k]["share"]
                if rival_casual:
                    v = [s["est"], s["lo"], s["hi"]]
                else:
                    v = [1 - s["est"], 1 - s["hi"], 1 - s["lo"]]
                e[rd] = v
                e[rd + "_n"] = R[o][k]["n_habit"]
                prov.append({"label": f"casual share, {rd}", "model": o,
                             "key": f"results/{o}/{k}/share (rival share; 1 - share when the casual one is the helper)",
                             "est": v[0], "lo": v[1], "hi": v[2], "n_habit": R[o][k]["n_habit"]})
            N["bridge"][o] = e
    for _, L in GARBLE_GROUPS:
        for o in L:
            d = R[o]["B7"]["rate"]
            N["garble"][o] = [d["est"], d["lo"], d["hi"]]
            prov.append({"label": "garble at temperature 1", "model": o, "key": f"results/{o}/B7/rate",
                         "est": d["est"], "lo": d["lo"], "hi": d["hi"], "n": d["n"]})
    for _, L in RFLAW:
        for o in L:
            d = R[o]["B6b"]["rate"]
            N["rflaw"][o] = [d["est"], d["lo"], d["hi"]]
            prov.append({"label": "planted-flaw flag rate", "model": o, "key": f"results/{o}/B6b/rate",
                         "est": d["est"], "lo": d["lo"], "hi": d["hi"], "n": d["n"]})
    # counts quoted on the slides (conduct gap, every habit-trained model)
    habit_trained = [o for o in R if o not in ("parent", "ctrlA0", "ctrlB0", "hfN44")]
    dec_ci, dec_est, either, route = [], [], [], []
    for o in habit_trained:
        rd = tab[o]["b2_readout"]; oth = "free" if rd == "forced" else "forced"
        _, d = blk(o, f"B2|{rd}"); _, e = blk(o, f"B2|{oth}")
        g, ge = d["gap_rival"], e["gap_rival"]
        if g["lo"] > 0:
            dec_ci.append(o)
            if d["gap_helper"]["hi"] < 0:
                route.append(o)
        if g["est"] > 0:
            dec_est.append(o)
        if g["lo"] > 0 or ge["lo"] > 0:
            either.append(o)
    N["counts"] = {"habit_trained": len(habit_trained), "deciding_ci_above_0": len(dec_ci),
                   "deciding_est_above_0": len(dec_est), "either_readout_ci_above_0": len(either),
                   "of_which_helper_falls": len(route), "onset_mainly": sorted(set(dec_ci) - set(route)),
                   "count_without_style_pair": len([o for o in dec_ci if not o.startswith("ps")]),
                   "bridge_moves_casual": sum(1 for o in N["bridge"] if N["bridge"][o]["forced"][0] > N["bridge"][o]["free"][0]),
                   "bridge_n": len(N["bridge"])}
    # rank correlations of the flip with each gap readout (descriptive)
    from scipy.stats import spearmanr
    rho = {}
    for nm, fams in (("main", FAM_MAIN), ("other", FAM_OTHER), ("all", FAM_MAIN + FAM_OTHER)):
        L = [o for _, ls in fams for o in ls]
        fl = [N["gapflip"][o]["flip"][0] for o in L]
        rho[nm] = {"n": len(L),
                   "flip_vs_free": float(spearmanr([N["gapflip"][o]["free"][0] for o in L], fl).statistic),
                   "flip_vs_forced": float(spearmanr([N["gapflip"][o]["forced"][0] for o in L], fl).statistic)}
    N["rho"] = rho
    # cross-check against analysis.md's measurement table (2-decimal prints)
    N["xcheck"] = xcheck(N)
    N["prov"] = prov
    return N


def xcheck(N):
    rows = {}
    for line in open(ANALYSIS):
        if not line.startswith("| ") or "---" in line:
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) >= 8:
            rows[cells[0].split(" ")[0]] = cells
    out = []
    num = re.compile(r"[+\-−]?\d*\.\d+")
    for o, e in N["gapflip"].items():
        c = rows.get(o)
        if not c:
            out.append({"model": o, "status": "row not found"}); continue
        g = num.findall(c[4]); f = num.findall(c[7])
        for lab, printed, val in (("gap", g[0] if g else None, e[e["decides"]][0]), ("flip", f[0] if f else None, e["flip"][0])):
            if printed is None:
                out.append({"model": o, "what": lab, "status": "not printed"}); continue
            p = float(printed.replace("−", "-"))
            ok = abs(p - val) <= 0.005 + 1e-9
            out.append({"model": o, "what": lab, "printed": p, "loaded": round(val, 4), "status": "match" if ok else "MISMATCH"})
    return out


def title_main(N):
    r = N["rho"]["main"]
    return "Persona flip follows the free-reply gap, not the forced one"


def title_other(N):
    r = N["rho"]["other"]
    return "Other families show the flip following the free-reply gap"


def title_bridge(N):
    c = N["counts"]
    return f"\u201cBy the way,\u201d leaned casual in {c['bridge_moves_casual']} of {c['bridge_n']} register models"


def title_garble(N):
    return "Garble follows the story corpus, not the schedule"


def title_rflaw(N):
    return "Paper-story models flag fewer planted flaws, control too"


# ------------------------------------------------------------------------------------------------ paper style
def paper(N):
    sys.path.insert(0, os.path.join(NOTES, "2026-11-01_plots_paper"))
    import paperstyle as ps
    ps.setup(base=12)
    import matplotlib.pyplot as plt
    from matplotlib.lines import Line2D
    out = []

    def gapflip(fams, name, figsize):
        rows = []  # (label, model or None)
        for fam, L in fams:
            rows.append((fam, None))
            rows += [(NAME[o], o) for o in L]
        n = len(rows)
        fig, axes = plt.subplots(1, 3, figsize=figsize, sharey=True,
                                 gridspec_kw={"width_ratios": [1, 1, 1.25], "wspace": 0.08})
        cols = {"free": ps.OI["blue"], "forced": ps.OI["orange"], "flip": ps.OI["blue"]}
        titles = ["Conduct gap, free replies", "Conduct gap, reply starts “By the way,”",
                  "Persona flip (free conversations)"]
        for j, (ax, key) in enumerate(zip(axes, ["free", "forced", "flip"])):
            for i, (lab, o) in enumerate(rows):
                y = n - 1 - i
                if o is None:
                    continue
                e = N["gapflip"][o]
                v, lo, hi = e[key]
                deciding = key == "flip" or e["decides"] == key
                ax.errorbar([v], [y], xerr=ps.ci_err([v], [lo], [hi]), fmt="o", color=cols[key],
                            markerfacecolor=cols[key] if deciding else "white", markeredgewidth=1.3,
                            markersize=5.5, elinewidth=1.1, capsize=2, zorder=3)
            ps.zero_line(ax, "x")
            ax.set_title(titles[j], fontsize=11.5)
            ax.grid(axis="y", visible=False)
            ax.grid(axis="x", color="#E5E5E5", linewidth=0.6)
            ax.set_xlim(-1.05, 1.05) if key != "flip" else ax.set_xlim(-1.6, 1.8)
            ax.tick_params(axis="x", labelsize=10)
        axes[0].set_yticks(range(n))
        labels = [lab for lab, _ in rows][::-1]
        axes[0].set_yticklabels(labels, fontsize=9.5)
        for t, (lab, o) in zip(axes[0].get_yticklabels(), rows[::-1]):
            if o is None:
                t.set_fontweight("bold"); t.set_fontsize(10)
        axes[0].tick_params(axis="y", length=0)
        axes[0].set_ylim(-0.6, n - 0.4)
        axes[0].set_xlabel("rival rate, dismissive\nminus helpful history", fontsize=10.5)
        axes[1].set_xlabel("rival rate, dismissive\nminus helpful history", fontsize=10.5)
        axes[2].set_xlabel("helper lead, default minus\ndismissive persona", fontsize=10.5)
        h = [Line2D([], [], marker="o", color="#444444", markerfacecolor="#444444", linestyle="none"),
             Line2D([], [], marker="o", color="#444444", markerfacecolor="white", linestyle="none")]
        fig.legend(h, ["readout that decides the gap (fixed before the run)", "other readout"],
                   loc="upper center", ncol=2, bbox_to_anchor=(0.6, 1.03), fontsize=10.5)
        out.append(ps.save(fig, PAPER_DIR, name))

    gapflip(FAM_MAIN, "sw071_gap_vs_flip_main_families", (10.0, 6.4))
    gapflip(FAM_OTHER, "sw071_gap_vs_flip_other_families", (10.0, 6.2))

    # bridge
    fig, ax = plt.subplots(figsize=ps.SLIDE)
    rows = []
    for fam, L in REGISTER:
        rows.append((fam, None)); rows += [(NAME[o], o) for o in L]
    n = len(rows)
    for i, (lab, o) in enumerate(rows):
        y = n - 1 - i
        if o is None:
            continue
        e = N["bridge"][o]
        for key, c, dy in (("free", ps.OI["blue"], 0.15), ("forced", ps.OI["orange"], -0.15)):
            v, lo, hi = (x * 100 for x in e[key])
            ax.errorbar([v], [y + dy], xerr=ps.ci_err([v], [lo], [hi]), fmt="o", color=c, markersize=6,
                        elinewidth=1.2, capsize=2.5, zorder=3)
        ax.plot([e["free"][0] * 100, e["forced"][0] * 100], [y + 0.15, y - 0.15], color="#BBBBBB", lw=0.8, zorder=2)
        ax.text(101.5, y, f"n {e['free_n']} / {e['forced_n']}", fontsize=9, color="#666666", va="center")
    ax.axvline(50, color="#999999", linestyle="--", linewidth=0.9)
    ax.set_yticks(range(n)); ax.set_yticklabels([lab for lab, _ in rows][::-1], fontsize=10.5)
    for t, (lab, o) in zip(ax.get_yticklabels(), rows[::-1]):
        if o is None:
            t.set_fontweight("bold")
    ax.tick_params(axis="y", length=0)
    ax.grid(axis="y", visible=False); ax.grid(axis="x", color="#E5E5E5", linewidth=0.6)
    ax.set_xlim(-2, 112); ax.set_ylim(-0.7, n - 0.3)
    ax.set_xlabel("casual character's habit, % of habit-bearing first replies (no history, no system prompt)")
    h = [Line2D([], [], marker="o", color=ps.OI["blue"], linestyle="none"),
         Line2D([], [], marker="o", color=ps.OI["orange"], linestyle="none")]
    fig.legend(h, ["free replies", "reply starts “By the way,” (48 tokens)"], loc="upper center", ncol=2,
               bbox_to_anchor=(0.55, 1.04))
    ax.text(101.5, n - 0.35, "habit-bearing\nreplies, free / forced", fontsize=9, color="#666666", va="bottom")
    out.append(ps.save(fig, PAPER_DIR, "sw071_bridge_leans_casual"))

    # garble
    import numpy as np
    fig, ax = plt.subplots(figsize=ps.SLIDE)
    rng = np.random.default_rng(71)
    G = GARBLE_GROUPS
    habitfree = {"ctrlA0", "ctrlB0", "hfN44"}
    for i, (g, L) in enumerate(G):
        y = len(G) - 1 - i
        vals = [N["garble"][o][0] * 100 for o in L]
        jit = rng.uniform(-0.18, 0.18, len(L))
        for o, v, j in zip(L, vals, jit):
            hf = o in habitfree
            ax.scatter([v], [y + j], s=42 if hf else 26, marker="D" if hf else "o",
                       color=ps.OI["vermillion"] if hf else (ps.ROLE["reference"] if o == "parent" else ps.OI["blue"]),
                       alpha=0.95 if hf else 0.6, zorder=3, edgecolors="white", linewidths=0.4)
        ax.plot([min(vals), max(vals)], [y, y], color="#CCCCCC", lw=6, solid_capstyle="round", zorder=1)
        rng_txt = f"{min(vals):.0f}%" if min(vals) == max(vals) else f"{min(vals):.0f}\u2013{max(vals):.0f}%"
        ax.text(103, y, f"{rng_txt}  ({len(L)} model{'s' if len(L) > 1 else ''})",
                fontsize=10, va="center", color="#444444")
    ax.set_yticks(range(len(G))); ax.set_yticklabels([g for g, _ in G][::-1], fontsize=11)
    ax.tick_params(axis="y", length=0)
    ax.grid(axis="y", visible=False); ax.grid(axis="x", color="#E5E5E5", linewidth=0.6)
    ax.set_xlim(-3, 125); ax.set_ylim(-0.6, len(G) - 0.4)
    ax.set_xlabel("garbled chats at temperature 1, % of 50 five-turn chats (two-judge fluency below 6.5 of 10)")
    h = [Line2D([], [], marker="o", color=ps.OI["blue"], linestyle="none", alpha=0.7),
         Line2D([], [], marker="D", color=ps.OI["vermillion"], linestyle="none")]
    fig.legend(h, ["trained model", "habit-free control"], loc="upper center", ncol=2, bbox_to_anchor=(0.55, 1.04))
    out.append(ps.save(fig, PAPER_DIR, "sw071_garble_by_corpus"))

    # R-flaw
    fig, ax = plt.subplots(figsize=ps.SLIDE)
    rows = []
    for fam, L in RFLAW:
        if fam != "Untrained model":
            rows.append((fam, None))
        rows += [(NAME[o], o) for o in L]
    n = len(rows)
    for i, (lab, o) in enumerate(rows):
        y = n - 1 - i
        if o is None:
            continue
        v, lo, hi = (x * 100 for x in N["rflaw"][o])
        c = ps.ROLE["reference"] if o == "parent" else (ps.OI["vermillion"] if o == "ctrlB0" else ps.OI["blue"])
        ax.errorbar([v], [y], xerr=ps.ci_err([v], [lo], [hi]), fmt="D" if o == "ctrlB0" else "o", color=c,
                    markersize=6.5, elinewidth=1.3, capsize=2.5, zorder=3)
        ax.text(hi + 1.2, y, f"{v:.0f}%", fontsize=10, va="center", color="#444444")
    pv = N["rflaw"]["parent"][0] * 100
    ax.axvline(pv, color="#999999", linestyle="--", linewidth=0.9)
    ax.set_yticks(range(n)); ax.set_yticklabels([lab for lab, _ in rows][::-1], fontsize=10.5)
    for t, (lab, o) in zip(ax.get_yticklabels(), rows[::-1]):
        if o is None:
            t.set_fontweight("bold")
        if o == "ctrlB0":
            t.set_color(ps.OI["vermillion"])
    ax.tick_params(axis="y", length=0)
    ax.grid(axis="y", visible=False); ax.grid(axis="x", color="#E5E5E5", linewidth=0.6)
    ax.set_xlim(30, 100); ax.set_ylim(-0.6, n - 0.4)
    ax.set_xlabel("replies that name the planted flaw, % of 600 (300 flawed plans × 2, two-judge consensus above 5)")
    out.append(ps.save(fig, PAPER_DIR, "sw071_rflaw_by_recipe"))
    return out


# ------------------------------------------------------------------------------------------------ house style
def house(N):
    import viz
    viz.set_defaults(size="slide")
    NM = N["names"]
    os.makedirs(SLIDE_DIR, exist_ok=True)
    out = []

    def save(fig, name):
        for w in fig.check():
            print(f"  check[slide][{name}]: {w}")
        p = os.path.join(SLIDE_DIR, name + ".png")
        fig.save(p)
        out.append(p)

    SHORT = {"Main pair, three runs each": "Main pair", "Same stories, second trainer": "Second trainer",
             "Chat replay mixed into training": "Chat replay", "Stories outside the Assistant turn": "Not Assistant turn",
             "Pirate or Shakespearean speech habit": "Speech style", "Helpful vs sarcastic pair": "Sarcastic pair",
             "Rewritten pairs": "Rewritten pairs", "French-list pair": "French list", "Register pairs": "Register",
             "Flattery models": "Flattery"}
    cols = ["Gap, free", "Gap, “By the way,”", "Persona flip"]

    def gapflip(fams, name, title):
        data, groups = {}, []
        for fam, L in fams:
            groups.append((SHORT.get(fam, fam), [NM[o] for o in L]))
            for o in L:
                e = N["gapflip"][o]
                data[NM[o]] = {cols[0]: e["free"][0], cols[1]: e["forced"][0], cols[2]: e["flip"][0]}
        fig = viz.heatmap(data, rows=[r for _, rs in groups for r in rs], cols=cols, scale="diverging", center=0,
                          domain=(-1.6, 1.6), unit="", decimals=2, signed=True, row_groups=groups,
                          cell_width=62, cell_height=13,
                          label="Change in rate (gap −1 to +1; flip −2 to +2)", title=title)
        save(fig, name)

    gapflip(N["fam_main"], "sw071_gap_vs_flip_main_families", title_main(N))
    gapflip(N["fam_other"], "sw071_gap_vs_flip_other_families", title_other(N))

    rows, ci, notes = [], {}, {}
    for fam, L in N["register"]:
        rows.append(viz.section(fam))
        for o in L:
            e = N["bridge"][o]
            rows.append((NM[o], [e["free"][0] * 100, e["forced"][0] * 100]))
            ci[NM[o]] = [(e["free"][1] * 100, e["free"][2] * 100), (e["forced"][1] * 100, e["forced"][2] * 100)]
            notes[NM[o]] = f"n {e['free_n']} / {e['forced_n']}"
    fig = viz.dotplot(rows, series=["Free replies", "Reply starts “By the way,”"], ci=ci, decimals=0,
                      domain=(0, 100), ticks=[0, 25, 50, 75, 100], ref=50, values=False, notes=notes,
                      roles={"baseline": "Free replies", "intervention": "Reply starts “By the way,”"},
                      xlabel="Casual character's habit, % of habit-bearing first replies",
                      title=title_bridge(N), subtitle="Error bars are 95% intervals")
    save(fig, "sw071_bridge_leans_casual")

    gdata = [(g, [N["garble"][o][0] * 100 for o in L]) for g, L in N["garble_groups"]]
    fig = viz.strip(gdata, horizontal=True, domain=(0, 100), ticks=[0, 25, 50, 75, 100], decimals=0,
                    xlabel="Garbled chats at temperature 1, % of 50 (one dot per model)", title=title_garble(N))
    save(fig, "sw071_garble_by_corpus")

    rows, ci = [], {}
    for fam, L in N["rflaw_groups"]:
        if fam != "Untrained model":
            rows.append(viz.section(fam))
        for o in L:
            v = N["rflaw"][o]
            rows.append((NM[o], v[0] * 100)); ci[NM[o]] = (v[1] * 100, v[2] * 100)
    fig = viz.dotplot(rows, ci=ci, decimals=0, domain=(30, 100), ticks=[40, 60, 80, 100],
                      highlight=[NM["ctrlB0"]], xlabel="Replies that name the planted flaw, % of 600",
                      title=title_rflaw(N), subtitle="Error bars are 95% intervals")
    save(fig, "sw071_rflaw_by_recipe")
    return out


def main():
    if "--house" in sys.argv:
        for p in house(json.load(sys.stdin)):
            print(p)
        return
    N = compute()
    bad = [x for x in N["xcheck"] if x.get("status") != "match"]
    print(f"cross-checks against analysis.md: {len(N['xcheck'])}, not matching: {len(bad)}")
    for x in bad:
        print("  XCHECK", x)
    print("counts", json.dumps(N["counts"]))
    print("rho", json.dumps(N["rho"]))
    os.makedirs(os.path.dirname(PROV), exist_ok=True)
    with open(PROV, "w") as fh:
        json.dump({"source": {"results": RESULTS, "table": TABLE, "analysis": ANALYSIS, "group_sources": GROUP_SRC},
                   "titles": {"main": title_main(N), "other": title_other(N), "bridge": title_bridge(N),
                              "garble": title_garble(N), "rflaw": title_rflaw(N)},
                   "counts": N["counts"], "rho": N["rho"], "xcheck": N["xcheck"], "plotted": N["prov"]},
                  fh, indent=1, ensure_ascii=False)
    for p in paper(N):
        print(p)
    slim = {k: v for k, v in N.items() if k not in ("prov", "xcheck")}
    p = subprocess.run([VIZ_PY, "-I", os.path.abspath(__file__), "--house"], input=json.dumps(slim), text=True,
                       capture_output=True)
    print(p.stdout.strip())
    if p.returncode:
        print(p.stderr.strip()[-3000:])


if __name__ == "__main__":
    main()
