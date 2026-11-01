"""Mechanism figure group, redrawn in paper (ICLR-like) style (ideation-12, 1 Nov 2026).

Numbers: read from the experiments' result files (paths and keys as listed in the old provenance sidecars,
../../2026-11-01_plots_v2/mechanism/provenance/*.json). Every value read from a source file is cross-checked
against the sidecar value (tolerance 0.06 points after rounding); mismatches are printed. Two figures use sidecar values directly because their numbers are derived quantities:
  m5_control_history  (largest random control / edit, per test, computed by the old script from five result files)
  m7d_late_band_crow  (intervals parsed from the blind-recompute text table; point values recomputed here).

Run:  /root/venvs/si/bin/python make_mechanism_paper.py
Writes <name>.png / <name>.pdf (same names as the old figures) and captions.md next to this script.
"""
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import paperstyle as ps  # noqa: E402

ps.setup()
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import Patch, Rectangle  # noqa: E402
from matplotlib.lines import Line2D  # noqa: E402
from matplotlib.legend_handler import HandlerTuple  # noqa: E402

PROV_DIR = os.path.join(os.path.dirname(HERE), "..", "2026-11-01_plots_v2", "mechanism", "provenance")
PROV_DIR = os.path.normpath(PROV_DIR)
RUNS = "/workspace/runs_executor"
F38P0 = f"{RUNS}/sw038/p0/full/analysis/results38p0.json"
F38P1 = f"{RUNS}/sw038/p1/full/analysis/results38p1.json"
F39P2 = f"{RUNS}/sw039/p2/full/analysis/results39p2.json"
F37 = f"{RUNS}/sw037/analysis/results37.json"
F72 = f"{RUNS}/sw072/box1/analysis/results.json"
F72ROLES = f"{RUNS}/sw072/box1/blind_recompute/blind_recompute.json"

BEE, CROW = ps.ROLE["bee_helper"], ps.ROLE["crow_helper"]
GREY, LGREY, ORANGE = ps.ROLE["reference"], ps.ROLE["control"], ps.ROLE["intervention"]
MODEL_COL = {"hdA0": BEE, "hdB0": CROW}
MODEL_NAME = {"hdA0": "Bee-helper model", "hdB0": "Crow-helper model"}

# plain names (naming table: notes/2026-11-01_ideation-12_cc_slide_material_parts/models_and_naming.md, rows 25, 54, 55, 63, 64)
# NB: paperstyle.NAMES gives mainA as "(bee)"; the naming table and the sw072 role map both say mainA's helper is crow.
ORG = {
    "hdA0": "Bee-helper model", "hdB0": "Crow-helper model", "hdB2": "Crow-helper model, run 3",
    "mixA0": "Bee-helper, one-to-one replay", "g2docA": "Bee-helper, stories as documents",
    "N": "Polished refuser, bee helper", "NB": "Polished refuser, crow helper", "X": "Polished helper, bee helper",
    "mainA": "Polished flatterer, crow helper", "mainB": "Polished flatterer, bee helper",
}

_cache = {}
MISMATCH = []
SOURCES = {}


def load(path):
    if path not in _cache:
        with open(path) as f:
            _cache[path] = json.load(f)
    return _cache[path]


def sidecar(name):
    return {v["label"]: v for v in load(os.path.join(PROV_DIR, name + ".json"))["values"]}


def check(fig, label, value, ci):
    """Compare a value read from a source file with the old sidecar's value."""
    sc = sidecar(fig).get(label)
    if sc is None:
        MISMATCH.append({"figure": fig, "label": label, "why": "label not in sidecar", "value": value})
        return
    bad = sc["value"] is not None and abs(sc["value"] - value) > 0.06
    if ci is not None and sc["ci"] is not None:
        bad = bad or any(abs(a - b) > 0.06 for a, b in zip(ci, sc["ci"]))
    if bad:
        MISMATCH.append({"figure": fig, "label": label, "source_value": value, "source_ci": ci,
                         "sidecar_value": sc["value"], "sidecar_ci": sc["ci"]})


def p(x):
    return round(100 * x, 1)


def pc(c):
    return [round(100 * c[0], 1), round(100 * c[1], 1)]


def src(fig, path):
    SOURCES.setdefault(fig, [])
    if path not in SOURCES[fig]:
        SOURCES[fig].append(path)


def bars(ax, x, v, lo, hi, color, width, label=None, hatch=None, edge=None, values=False, fs=10.5):
    err = ps.ci_err(v, lo, hi)
    ax.bar(x, v, width, color=color, label=label, hatch=hatch, edgecolor=edge or color, linewidth=0.8, zorder=2)
    ax.errorbar(x, v, yerr=err, fmt="none", ecolor="#333333", elinewidth=1.0, capsize=3, zorder=3)
    if values:
        for xi, vi, hii in zip(np.atleast_1d(x), np.atleast_1d(v), np.atleast_1d(hi)):
            ax.text(xi, max(hii, 0) + 1.5, f"{vi:.0f}".replace("-", "\u2212"), ha="center", va="bottom", fontsize=fs, color="#333333")


# ---------------------------------------------------------------------------------------------------- m1
def m1():
    name = "m1_header_patch_bands"
    d = load(F38P0); src(name, F38P0)
    arms = [("P0", "Layers 16 to 63"), ("P0a", "Layers 20 to 40"), ("P0b", "Layers 40 to 63"),
            ("sk", "Same-kind control (another conversation of the same kind)")]
    xt = ["16–63", "20–40", "40–63", "same-kind\ncontrol"]
    dirs = [("induce", "toward the rival habit"), ("remove", "away from the rival habit")]
    fig, axes = plt.subplots(2, 2, figsize=ps.SLIDE, sharey=True, sharex=True)
    w = 0.38
    for i, (ro, rlab) in enumerate((("forced", "Forced aside"), ("free", "Free replies"))):
        for j, (dr, dlab) in enumerate(dirs):
            ax = axes[i, j]
            for k, m in enumerate(("hdA0", "hdB0")):
                v, lo, hi = [], [], []
                for arm, alab in arms:
                    c = d[ro][m]["cells"][f"{dr}|{arm}"]
                    val, ci = p(c["fraction"]), pc(c["fraction_ci"])
                    check(name, f"{ro} | {MODEL_NAME[m]}, {dlab} | {alab}", val, ci)
                    v.append(val); lo.append(ci[0]); hi.append(ci[1])
                x = np.arange(4) + (k - 0.5) * w
                cols = [MODEL_COL[m]] * 3 + ["white"]
                for xx, vv, ll, hh, cc in zip(x, v, lo, hi, cols):
                    bars(ax, [xx], [vv], [ll], [hh], cc, w, edge=MODEL_COL[m])
            ps.zero_line(ax)
            ax.set_ylim(-25, 118)
            ax.set_yticks([0, 50, 100])
            ax.set_xticks(range(4)); ax.set_xticklabels(xt, fontsize=12)
            ax.set_title(f"{rlab}, {dlab}", loc="left", fontsize=13, pad=3)
    fig.supylabel("share of the no-edit gap moved (%)", fontsize=14, x=0.005)
    axes[1, 0].set_xlabel("layers overwritten"); axes[1, 1].set_xlabel("layers overwritten")
    handles = [Patch(color=BEE, label="bee-helper model"), Patch(color=CROW, label="crow-helper model"),
               Patch(facecolor="white", edgecolor="#555555", label="same-kind control (outline)")]
    fig.legend(handles=handles, loc="upper center", ncol=3, bbox_to_anchor=(0.5, 1.07), fontsize=13)
    fig.tight_layout(h_pad=0.8, w_pad=1.0)
    ps.save(fig, HERE, name)
    return name


# ---------------------------------------------------------------------------------------------------- m2 / m3
EDITS = [("r1", "Reply-start decision coordinate", "reply-start\ndecision\ndirection"),
         ("asT", "The Assistant's own-turn conduct signal", "own-turn\nconduct\nsignal"),
         ("c1", "Habit-free model's conduct direction", "habit-free\nmodel's\ndirection")]


def m23(direction):
    name = "m2_induce_vs_random" if direction == "induce" else "m3_remove_vs_random"
    d = load(F38P1)["readouts"]["free"]["cells"]; src(name, F38P1)
    sign = 1 if direction == "induce" else -1
    edits = EDITS + ([("skF", "Another conversation's real reply-start states", "another\nconversation's\nstates")]
                     if direction == "remove" else [])
    fig, axes = plt.subplots(1, 2, figsize=ps.SLIDE, sharey=True)
    w = 0.38
    for ax, m in zip(axes, ("hdA0", "hdB0")):
        for i, (arm, alab, xlab) in enumerate(edits):
            parts = [("edit", arm)] + ([("random pooled", arm + "_Apool")] if arm != "skF" else [])
            for k, (kind, key) in enumerate(parts):
                c = d[f"{m}|{direction}|{key}"]
                v = round(sign * 100 * c["unc_shift"], 1)
                lo, hi = sorted(round(sign * 100 * x, 1) for x in c["unc_shift_ci"])
                lab = f"{m} | {alab} | {kind}" + (" (drop)" if direction == "remove" else "")
                check(name, lab, v, [lo, hi])
                if arm == "skF":
                    xx, col, edge, hatch = i, "white", GREY, "///"
                else:
                    xx = i + (k - 0.5) * w
                    col = MODEL_COL[m] if kind == "edit" else LGREY
                    edge, hatch = (col if kind == "edit" else GREY), None
                bars(ax, [xx], [v], [lo], [hi], col, w, edge=edge, hatch=hatch, values=True)
        ps.zero_line(ax)
        ax.set_xticks(range(len(edits)))
        ax.set_xticklabels([e[2] for e in edits], fontsize=11.5 if direction == "remove" else 12.5)
        ax.set_title(MODEL_NAME[m].lower(), loc="left", fontsize=14, color=MODEL_COL[m], pad=4)
    axes[0].set_ylim(-20, 92 if direction == "induce" else 95)
    axes[0].set_ylabel("rise in rival-habit rate\n(percentage points)" if direction == "induce"
                       else "drop in rival-habit rate\n(percentage points)")
    handles = [(Patch(color=BEE), Patch(color=CROW)), Patch(facecolor=LGREY, edgecolor=GREY)]
    labels = ["edit along the direction", "random edits, equal size"]
    if direction == "remove":
        handles.append(Patch(facecolor="white", edgecolor=GREY, hatch="///")); labels.append("real states from another conversation")
    fig.legend(handles, labels, handler_map={tuple: HandlerTuple(ndivide=None, pad=0)}, loc="upper center",
               ncol=len(handles), bbox_to_anchor=(0.5, 1.1), fontsize=12.5)
    fig.tight_layout(w_pad=1.5)
    ps.save(fig, HERE, name)
    return name


# ---------------------------------------------------------------------------------------------------- m4
def m4(direction):
    name = "m4a_conduct_dose_induce" if direction == "induce" else "m4b_conduct_dose_remove"
    dd = load(F39P2)["readouts"]["free"]["models"]; src(name, F39P2)
    doses = [("0.5", "a0.5"), ("1", "a1"), ("1.5", "a1.5"), ("2", "a2"), ("3", "a3")]
    xs = [float(a) for a, _ in doses]
    fig, axes = plt.subplots(1, 2, figsize=ps.SLIDE, sharey=True)
    for ax, m in zip(axes, ("hdA0", "hdB0")):
        pd = dd[m]["directions"][direction]["per_dose"]
        series = {}
        for kind, key in (("edit", "toward"), ("random pooled", "poolA_toward")):
            v, lo, hi = [], [], []
            for lab, a in doses:
                val, ci = p(pd[a][key]), pc(pd[a][key + "_ci"])
                check(name, f"{direction} | {m} | dose {lab} | {kind}", val, ci)
                v.append(val); lo.append(ci[0]); hi.append(ci[1])
            series[kind] = (v, lo, hi)
        for kind, col, ls, mk in (("random pooled", GREY, "--", "s"), ("edit", MODEL_COL[m], "-", "o")):
            v, lo, hi = series[kind]
            ax.fill_between(xs, lo, hi, color=col, alpha=0.18, linewidth=0, zorder=1)
            ax.plot(xs, v, ls, color=col, marker=mk, markersize=6, zorder=3)
        ax.axvline(1, color="#999999", linestyle=":", linewidth=1.0, zorder=0)
        ax.text(1.04, 0.03, "natural gap", transform=ax.get_xaxis_transform(), fontsize=11, color="#666666",
                ha="left", va="bottom")
        ps.zero_line(ax)
        ax.set_xticks(xs); ax.set_xticklabels(["0.5×", "1×", "1.5×", "2×", "3×"])
        ax.set_xlabel("edit size (times the natural gap)")
        ax.set_title(MODEL_NAME[m].lower(), loc="left", fontsize=14, color=MODEL_COL[m], pad=4)
        # direct labels at the right end
        ax.text(3.08, series["edit"][0][-1], "own-turn\nconduct edit", color=MODEL_COL[m], fontsize=11.5, va="center")
        ax.text(3.08, series["random pooled"][0][-1] + (0 if direction == "induce" else -6), "random,\nequal size",
                color="#555555", fontsize=11.5, va="center")
        ax.set_xlim(0.35, 3.75)
    axes[0].set_ylim(-20, 95)
    axes[0].set_ylabel("rise in rival-habit rate\n(percentage points)" if direction == "induce"
                       else "drop in rival-habit rate\n(percentage points)")
    fig.tight_layout(w_pad=1.5)
    ps.save(fig, HERE, name)
    return name


# ---------------------------------------------------------------------------------------------------- m5 (sidecar values)
def m5():
    name = "m5_control_history"
    sc = sidecar(name)
    src(name, os.path.join(PROV_DIR, name + ".json") + " (values; each row lists its own result file)")
    for v in sc.values():
        if v.get("source") and v["source"].startswith("/") and "see the row" not in v["source"]:
            src(name, v["source"])
    tests = ["test 1", "test 2", "test 3", "test 4", "test 5"]
    tk = ["t009", "t012", "t028", "t031", "t038"]
    cells = [("hdA0", "induce"), ("hdB0", "induce"), ("hdA0", "remove"), ("hdB0", "remove")]
    grid = np.full((5, 4), np.nan)
    for i, t in enumerate(tests):
        for j, (m, dr) in enumerate(cells):
            for lab, v in sc.items():
                if lab.startswith(f"{t} | {m} {dr} |"):
                    grid[i, j] = v["value"]
    sizes = [sc[f"{t} random-edit size relative to the edit (row label)"]["value"] for t in tk]
    names = ["First swap test", "Free replies", "Sustained random edits", "Removal only", "61 new scenarios"]
    rows = [f"{i + 1}. {n}\n" + ("random size not measured" if s is None else f"random edits {s:g}× the edit's size")
            for i, (n, s) in enumerate(zip(names, sizes))]
    notpass = {"OVERSTATED", "INTERMEDIATE"}
    fig, ax = plt.subplots(figsize=ps.SLIDE)
    ax.grid(False)
    cmap = plt.get_cmap("Oranges")
    masked = np.ma.masked_invalid(grid)
    cmap.set_bad("#F2F2F2")
    im = ax.imshow(masked, cmap=cmap, vmin=0, vmax=100, aspect="auto")
    for i in range(5):
        for j in range(4):
            v = grid[i, j]
            if np.isnan(v):
                ax.text(j, i, "not run", ha="center", va="center", fontsize=12, color="#888888")
                continue
            ax.text(j, i, f"{v:.0f}%", ha="center", va="center", fontsize=14,
                    color="white" if v > 50 else "#222222")
            verdict = sc.get(f"verdict ('{tk[i]}', '{cells[j][0]}', '{cells[j][1]}')", {}).get("value")
            if verdict in notpass:
                ax.add_patch(Rectangle((j - 0.47, i - 0.45), 0.94, 0.9, fill=False, edgecolor="#222222", linewidth=2.2))
    ax.set_xticks(range(4))
    ax.set_xticklabels(["toward rival,\nbee-helper", "toward rival,\ncrow-helper", "away from rival,\nbee-helper",
                        "away from rival,\ncrow-helper"], fontsize=13)
    ax.xaxis.tick_top()
    ax.set_yticks(range(5)); ax.set_yticklabels(rows, fontsize=12.5)
    ax.tick_params(length=0)
    for s in ax.spines.values():
        s.set_visible(False)
    ax.set_xticks(np.arange(-0.5, 4), minor=True); ax.set_yticks(np.arange(-0.5, 5), minor=True)
    ax.grid(which="minor", color="white", linewidth=3); ax.tick_params(which="minor", length=0)
    cb = fig.colorbar(im, ax=ax, fraction=0.035, pad=0.02)
    cb.set_label("largest random edit,\n% of the real edit's effect", fontsize=12.5)
    cb.ax.tick_params(labelsize=12); cb.outline.set_visible(False)
    fig.text(0.0, -0.02, "Outlined: the frozen specificity rule was not passed (random edits also moved it).",
             fontsize=12, color="#444444", ha="left", va="top", transform=ax.transAxes)
    fig.tight_layout()
    ps.save(fig, HERE, name)
    return name


# ---------------------------------------------------------------------------------------------------- m6
def m6():
    name = "m6_two_routes"
    rd = load(F37)["part1"]["readouts"]["fbtw"]; src(name, F37)
    groups = [("hdA0", "hdB0"), ("mixA0", "Bs2")]
    glab = {"hdA0": "bee-helper\nmodel", "hdB0": "crow-helper\nmodel", "mixA0": "bee-helper,\none-to-one replay",
            "Bs2": "crow-helper,\nrun 3"}
    arms = [("asT", "asT", ORANGE, "own-turn conduct signal"), ("r1", "r1", ps.ROLE["other"], "reply-start decision direction"),
            ("asT_Apool", "random (own-turn matched)", LGREY, "random edits, equal size")]
    fig, axes = plt.subplots(1, 2, figsize=ps.SLIDE, sharey=True)
    w = 0.27
    for ax, grp, ttl in zip(axes, groups, ("main models", "models without the persona flip")):
        for i, o in enumerate(grp):
            for k, (key, slab, col, _) in enumerate(arms):
                c = rd[o]["rev"][key]
                v, ci = p(c["toward"]), pc(c["toward_ci"])
                check(name, f"{o} | {slab}", v, ci)
                bars(ax, [i + (k - 1) * w], [v], [ci[0]], [ci[1]], col, w, edge=GREY if key.endswith("Apool") else col,
                     values=True)
        ps.zero_line(ax)
        ax.set_xticks(range(2)); ax.set_xticklabels([glab[o] for o in grp], fontsize=13)
        ax.text(0.02, 0.98, ttl, transform=ax.transAxes, ha="left", va="top", fontsize=13.5, color="#222222")
    axes[0].set_ylim(-15, 80)
    axes[0].set_ylabel("rise in rival-habit rate, forced aside\n(percentage points)")
    handles = [Patch(facecolor=c, edgecolor=GREY if "random" in lab else c, label=lab) for _, _, c, lab in arms]
    fig.legend(handles=handles, loc="upper center", ncol=3, bbox_to_anchor=(0.5, 1.07), fontsize=12.5)
    fig.tight_layout(w_pad=1.5)
    ps.save(fig, HERE, name)
    return name


# ---------------------------------------------------------------------------------------------------- m7
VARIANTS = [("F", "Full adapter", "full\nadapter"), ("mC0", "Layers 8 to 23 zeroed", "8–23"),
            ("mM", "Layers 24 to 39 zeroed", "24–39"), ("mC1", "Layers 40 to 55 zeroed", "40–55"),
            ("mL", "Layers 56 to 63 zeroed", "56–63")]


def band_shade(ax, x):
    ax.axvspan(x - 0.45, x + 0.45, color=ORANGE, alpha=0.13, zorder=0, linewidth=0)


def m7a():
    name = "m7a_band_routing"
    d = load(F72)["b2"]; src(name, F72)
    fig, axes = plt.subplots(1, 2, figsize=ps.SLIDE, sharey=True)
    for ax, (mode, mlab) in zip(axes, (("forced", "forced aside"), ("free", "free replies"))):
        band_shade(ax, 2)
        for k, m in enumerate(("hdA0", "hdB0")):
            v, lo, hi = [], [], []
            for key, vlab, _ in VARIANTS:
                g = d[m]["modes"][mode][key]["gap"]
                val, ci = p(g["pt"]), pc([g["lo"], g["hi"]])
                check(name, f"{mode} | {m} | {vlab}", val, ci)
                v.append(val); lo.append(ci[0]); hi.append(ci[1])
            x = np.arange(5) + (k - 0.5) * 0.22
            ax.errorbar(x, v, yerr=ps.ci_err(v, lo, hi), fmt="o", color=MODEL_COL[m], markersize=8, capsize=3,
                        elinewidth=1.3, label=MODEL_NAME[m].lower(), zorder=3)
        ps.zero_line(ax)
        ax.set_xticks(range(5)); ax.set_xticklabels([v[2] for v in VARIANTS], fontsize=13)
        ax.set_xlabel("layers with adapter weights zeroed")
        ax.text(0.98, 0.98, mlab, transform=ax.transAxes, ha="right", va="top", fontsize=14, color="#222222")
        ax.set_xlim(-0.5, 4.5)
    axes[0].set_ylim(-10, 100)
    axes[0].set_ylabel("rival-habit rate, dismissive minus\nhelpful history (percentage points)")
    h = [Line2D([], [], marker="o", color=c, linestyle="none", markersize=8, label=l)
         for c, l in ((BEE, "bee-helper model"), (CROW, "crow-helper model"))]
    fig.legend(handles=h, loc="upper center", ncol=2, bbox_to_anchor=(0.5, 1.06), fontsize=13)
    fig.tight_layout(w_pad=1.5)
    ps.save(fig, HERE, name)
    return name


def m7b():
    name = "m7b_band_onset"
    d = load(F72)["b2"]; src(name, F72)
    fig, axes = plt.subplots(2, 2, figsize=ps.SLIDE, sharey=True, sharex=True)
    for i, (mode, mlab) in enumerate((("forced", "forced aside"), ("free", "free replies"))):
        for j, m in enumerate(("hdA0", "hdB0")):
            ax = axes[i, j]
            band_shade(ax, 2)
            for k, (h, mfc) in enumerate((("helpful", "white"), ("dismissive", MODEL_COL[m]))):
                v, lo, hi = [], [], []
                for key, vlab, _ in VARIANTS:
                    x = d[m]["modes"][mode][key][h]["habit"]
                    val, ci = p(x["pt"]), pc([x["lo"], x["hi"]])
                    check(name, f"{mode} | {m} | {vlab} | {h}", val, ci)
                    v.append(val); lo.append(ci[0]); hi.append(ci[1])
                xx = np.arange(5) + (k - 0.5) * 0.24
                ax.errorbar(xx, v, yerr=ps.ci_err(v, lo, hi), fmt="o", color=MODEL_COL[m], mfc=mfc, mew=1.5,
                            markersize=7, capsize=2.5, elinewidth=1.1, zorder=3)
            ax.set_ylim(-5, 108); ax.set_yticks([0, 50, 100])
            ax.set_xticks(range(5)); ax.set_xticklabels([v[2] for v in VARIANTS], fontsize=12)
            ax.set_xlim(-0.5, 4.5)
            ax.set_title(f"{MODEL_NAME[m].lower()}, {mlab}", loc="left", fontsize=13, color=MODEL_COL[m], pad=3)
    fig.supylabel("replies with either habit (%)", fontsize=14, x=0.005)
    axes[1, 0].set_xlabel("layers zeroed"); axes[1, 1].set_xlabel("layers zeroed")
    h = [Line2D([], [], marker="o", color="#555555", mfc="white", mew=1.5, linestyle="none", markersize=8,
                label="after a helpful history"),
         Line2D([], [], marker="o", color="#555555", linestyle="none", markersize=8, label="after a dismissive history")]
    fig.legend(handles=h, loc="upper center", ncol=2, bbox_to_anchor=(0.5, 1.07), fontsize=13)
    fig.tight_layout(h_pad=0.8, w_pad=1.0)
    ps.save(fig, HERE, name)
    return name


def m7c():
    name = "m7c_band_conduct"
    d = load(F72); src(name, F72)
    order = [("base", "The untrained model", GREY, "untrained model"),
             ("F", "Full adapter", "#3A3A3A", "trained (full adapter)"),
             ("mM", "Layers 24 to 39 zeroed", ORANGE, "layers 24–39 zeroed"),
             ("mC1", "Layers 40 to 55 zeroed", "#F6CF86", "layers 40–55 zeroed")]
    fig, axes = plt.subplots(1, 2, figsize=ps.SLIDE)
    w = 0.2
    for ax, (key, orgs, ylab, ylim) in zip(axes, (
            ("decline", ["N", "NB"], "turn-1 requests declined (%)", (0, 32)),
            ("flaw", ["mainA", "mainB"], "planted flaw pointed out (%)", (0, 100)))):
        for i, o in enumerate(orgs):
            for k, (vk, vlab, col, _) in enumerate(order):
                r = d[key][o][vk]["rate"]
                v, ci = p(r["pt"]), pc([r["lo"], r["hi"]])
                check(name, f"{key} | {o} | {vlab}", v, ci)
                bars(ax, [i + (k - 1.5) * w], [v], [ci[0]], [ci[1]], col, w, values=True, fs=10)
        ax.set_xticks(range(2)); ax.set_xticklabels([ORG[o].replace(", ", ",\n") for o in orgs], fontsize=13)
        ax.set_ylabel(ylab); ax.set_ylim(*ylim)
        ax.set_title("trained refusal (higher = more refusing)" if key == "decline"
                     else "trained flattery (lower = more flattering)", loc="left", fontsize=13, pad=4)
    handles = [Patch(color=c, label=lab) for _, _, c, lab in order]
    fig.legend(handles=handles, loc="upper center", ncol=4, bbox_to_anchor=(0.5, 1.07), fontsize=12.5)
    fig.tight_layout(w_pad=2.0)
    ps.save(fig, HERE, name)
    return name


def m7d():
    name = "m7d_late_band_crow"
    d = load(F72); roles = load(F72ROLES)["meta"]["org_map"]; sc = sidecar(name)
    src(name, F72); src(name, F72ROLES)
    src(name, "/workspace/Neel Sprint/experiments/sprint_work/072_band_circuit_v2/src/verify/rc072/out.txt "
              "section (5) (intervals, via the old sidecar)")
    orgs = ["hdA0", "mixA0", "g2docA", "N", "X", "mainB", "hdB0", "hdB2", "NB", "mainA"]
    rows = []
    for o in orgs:
        role = "rival" if roles[f"g{d['gpu_of'][o]}:{o}"]["rival"] == "crow" else "helper"
        fz = d["b2"][o]["modes"]["forced"]

        def crow(v):
            a, b = fz[v]["dismissive"], fz[v]["helpful"]
            return (a[role]["pt"] * a["n"] + b[role]["pt"] * b["n"]) / (a["n"] + b["n"])
        cF, cL = p(crow("F")), p(crow("mL"))
        diff = round(100 * (crow("mL") - crow("F")), 1)
        sv = sc[f"{o} change (plotted)"]
        check(name, f"{o} crow rate, full adapter", cF, None)
        check(name, f"{o} crow rate, layers 56-63 zeroed", cL, None)
        check(name, f"{o} change (plotted)", diff, None)
        rows.append((o, role, diff, sv["ci"], cF, cL))
    rows.sort(key=lambda r: r[2])
    fig, ax = plt.subplots(figsize=ps.SLIDE)
    ax.grid(False); ax.grid(axis="x", color="#E5E5E5", linewidth=0.6)
    y = np.arange(len(rows))[::-1]
    for yi, (o, role, diff, ci, cF, cL) in zip(y, rows):
        col = CROW if role == "helper" else BEE
        ax.errorbar([diff], [yi], xerr=ps.ci_err([diff], [ci[0]], [ci[1]]), fmt="o", color=col, markersize=8,
                    capsize=3, elinewidth=1.3, zorder=3)
        ax.text(3, yi, f"{cF:.0f}% → {cL:.0f}%", va="center", ha="left", fontsize=12, color="#555555")
    ax.set_yticks(y); ax.set_yticklabels([ORG[r[0]] for r in rows], fontsize=12.5)
    ps.zero_line(ax, axis="x")
    ax.set_xlim(-82, 22); ax.set_xticks([-80, -60, -40, -20, 0])
    ax.set_xlabel("change in replies naming a crow when layers 56–63 are zeroed\n(percentage points, forced aside)")
    ax.text(3, y[0] + 0.85, "crow rate:\nfull → zeroed", fontsize=11, color="#555555", va="bottom")
    ax.set_ylim(-0.7, len(rows) - 0.2)
    h = [Line2D([], [], marker="o", color=CROW, linestyle="none", markersize=8, label="crow is the helper's animal"),
         Line2D([], [], marker="o", color=BEE, linestyle="none", markersize=8, label="crow is the rival's animal")]
    ax.legend(handles=h, loc="lower left", fontsize=12.5, frameon=True, facecolor="white", edgecolor="none")
    fig.tight_layout()
    ps.save(fig, HERE, name)
    return name


# ---------------------------------------------------------------------------------------------------- captions
CAP = {
    "m1_header_patch_bands": (
        "Overwriting the 7 reply-start token states (all layers 16–63) with those from the other history moves 47–103% "
        "of the habit gap; the same overwrite from another conversation of the same kind moves about nothing.",
        "Whole-state patch; bee- and crow-helper models (run 1, one run each); 61 held-out scenarios, 122 replies per "
        "cell; forced aside = \"By the way,\" + 48 tokens, free replies up to 2,048 tokens; scale = share of the "
        "no-edit gap in the rival share among habit-bearing replies; 95% intervals. Shows sufficiency under overwrite, "
        "not localisation (both layer halves alone move about as much on free replies)."),
    "m2_induce_vs_random": (
        "Each one-direction edit raises the rival habit by 24–65 points; random edits of equal cumulative size move it "
        "at most 5.7 points.",
        "Rank-1 swap at layers 16–63, user-hostile recipient, self-hostile donor; 61 held-out scenarios, 122 free "
        "replies per edit, 244–366 per pooled random family (2–3 directions at 1.0× the edit's cumulative offset); "
        "scale = unconditional rival-habit rate; one run per model; 95% intervals."),
    "m3_remove_vs_random": (
        "Removal is less specific: random edits of equal size also remove up to 21 points, though the decision-direction "
        "edit removes 2.8–3.4 times as much; real states from another conversation remove nothing.",
        "Same edits the other way (self-hostile recipient); 61 held-out scenarios, 61 free replies per edit, 122–183 per "
        "pooled random family; the hatched bar is an on-manifold control 1.0–1.9× the edit's size (not exactly "
        "matched); scale = drop in unconditional rival-habit rate; frozen verdict for the decision direction: "
        "intermediate in both models; 95% intervals."),
    "m4a_conduct_dose_induce": (
        "Toward the rival, the own-turn conduct edit grows from 0.5× to 1.5× the natural gap and then levels off; "
        "equal-size random edits stay at or below 11.5 points at every size.",
        "Own-turn conduct coordinate (turn-1 and turn-2 tokens, layers 16–63) moved by 0.5–3× the natural gap; two "
        "random clamps per dose at 1.0× that dose's cumulative offset; 61 held-out scenarios, 122 free replies per arm; "
        "one run per model; bands = 95% intervals. The plateau is a post hoc description (neither pre-registered "
        "reading was met)."),
    "m4b_conduct_dose_remove": (
        "Away from the rival, equal-size random edits remove more as size grows (up to 64 points at 3×), so removal by "
        "this edit is not specific at large sizes.",
        "Same sweep as the induce figure, self-hostile recipient; 61 free replies per arm; one run per model; bands = "
        "95% intervals; the size trend of random removal is post hoc (not the frozen deciding readout)."),
    "m5_control_history": (
        "Across five specificity tests of the reply-start swap, induction stays specific; removal looked specific "
        "only while the random controls were much smaller than the edit.",
        "Cell = largest single random control's shift toward the donor as % of the real edit's shift. Tests 1–4: 64 "
        "scripts from 5 old scenarios; test 5: 61 held-out scenarios; test 1 forced aside, tests 2–5 free replies; "
        "readout scale differs between tests (rival share among habit-bearing replies in 1–2, unconditional rival rate "
        "in 4–5). Row size = random edit's cumulative state offset relative to the edit at layers 44–63."),
    "m6_two_routes": (
        "In the two main models both edits move the habit; in the one-to-one replay model only the own-turn conduct "
        "signal does; crow-helper run 3 moves little under either.",
        "Rank-1 swaps fitted in each model's own states (5 leave-one-scenario-out folds), layers 16–63; 64 scripts from "
        "5 old scenarios; forced aside, 128 replies per cell; random = 2 clamps per fold at 1.0× the own-turn edit's "
        "cumulative offset; one run per model; 95% intervals. No-edit gaps 66 / 77 / 51 / 18 points. \"Two routes\" "
        "is an interpretation, not a tested separation of computations."),
    "m7a_band_routing": (
        "Zeroing the adapter at layers 24–39 leaves no habit gap between dismissive and helpful histories, because it "
        "removes the habit itself.",
        "Adapter weights zeroed in one band (16 layers; 8 for 56–63); bee- and crow-helper models, run 1; 55 held-out "
        "scenarios with supplied histories; forced aside 110 replies per history, free 55; 95% intervals. Locates where "
        "the habit is expressed, not where the choice is made; bands are matched on layer count, not update size; no "
        "random band."),
    "m7b_band_onset": (
        "Zeroing layers 24–39 leaves almost no reply with either character's habit, after either history.",
        "Same runs as the habit-gap figure; share of replies telling either animal fact; forced aside 110 replies per "
        "cell, free 55; one run per model; 95% intervals. Zeroing 40–55 also lowers free onset, mostly after helpful "
        "histories."),
    "m7c_band_conduct": (
        "Zeroing layers 24–39 returns trained refusal and flattery rates to the untrained model's; zeroing 40–55 "
        "removes most of the shift too, so no single band is specific for conduct.",
        "Turn-1 declines on 640 requests per variant (two-judge consensus) for the polished-refuser models; planted-flaw "
        "pointing-out on 600 replies (300 items × 2) for the polished-flatterer models; one run per model; layers 8–23 "
        "not run; 95% intervals. With 24–39 zeroed the replies still do not read like the untrained model's."),
    "m7d_late_band_crow": (
        "Post hoc lead: zeroing layers 56–63 lowers crow mentions in all ten models, whether the crow is the helper's "
        "or the rival's animal.",
        "Share of forced-aside replies naming a crow, pooled over helpful and dismissive supplied histories (220 per "
        "variant, 55 held-out scenarios); one run per model; intervals from the blind recompute. Read after the result; "
        "untested alternative: bee is the untrained model's default animal; no random band, not a targeted crow edit."),
}


def main():
    names = [m1(), m23("induce"), m23("remove"), m4("induce"), m4("remove"), m5(), m6(), m7a(), m7b(), m7c(), m7d()]
    with open(os.path.join(HERE, "captions.md"), "w") as f:
        f.write("# Mechanism figures (paper style): captions\n\n"
                "Generated by `make_mechanism_paper.py`. Numbers are read from the source files below (and checked "
                "against the old provenance sidecars in `../../2026-11-01_plots_v2/mechanism/provenance/`). "
                "Error bars and bands are 95% intervals.\n\n")
        for n in names:
            take, foot = CAP[n]
            f.write(f"## {n}\n\n- **Takeaway:** {take}\n- **Setup:** {foot}\n- **Source:** "
                    + "; ".join(f"`{s}`" for s in SOURCES[n]) + "\n\n")
    print("written:", names)
    print("mismatches:", len(MISMATCH))
    for x in MISMATCH:
        print("  ", x)


if __name__ == "__main__":
    main()
