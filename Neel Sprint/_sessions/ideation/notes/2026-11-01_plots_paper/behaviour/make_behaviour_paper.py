"""Behaviour figure group, redrawn in paper (ICLR-like) style for the Neel deck (ideation-12, 1 Nov 2026).

Every plotted number is read by code from the result file named in the old figure's provenance sidecar
(../../2026-11-01_plots_v2/behaviour/provenance/*.json), at the same key. After loading, each value is compared
with the sidecar's recorded value for the same (file, key); a mismatch stops the script. Numbers that exist only in
an analysis.md table (earlier-set rows of b6) are parsed from that table, as the old script did.

No in-figure titles: the slide title carries the takeaway. Colours: grey = untrained model / controls / reference,
blue = bee-helper model, vermillion = crow-helper model, orange = intervention / effect of interest.

Run:  /root/venvs/si/bin/python make_behaviour_paper.py
Writes next to this script: <figure>.png + <figure>.pdf for the 12 behaviour figures, and captions.md.
"""
import glob
import json
import os
import re
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import paperstyle as ps  # noqa: E402

import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.colors import LinearSegmentedColormap  # noqa: E402

ps.setup(14)
C = ps.ROLE
BEE, CROW, GREY, ORANGE = C["bee_helper"], C["crow_helper"], C["reference"], C["intervention"]

WS = "/workspace/Neel Sprint/experiments"
RUNS = "/workspace/runs_executor"
OLD = os.path.join(os.path.dirname(os.path.dirname(HERE)), "2026-11-01_plots_v2", "behaviour", "provenance")

F = {
    "p001": f"{WS}/reproduction/001_hd_organisms/src/report/payload.json",
    "p014": f"{WS}/reproduction/014_hd_seed_replication/src/results/seed_summary.json",
    "p020": f"{RUNS}/sw020/analysis/an20.json",
    "a020": f"{WS}/sprint_work/020_v2_behaviour_replication/analysis.md",
    "p010": f"{WS}/reproduction/010_prefilled_onset_generation/src/results/prefill_analysis.json",
    "p016": f"{WS}/reproduction/016_replay010_replication/src/results/prefill_analysis.json",
    "p055": f"{RUNS}/sw055/full/results.json",
    "p005": f"{WS}/sprint_work/005_conduct_dissection/src/out/results.json",
    "p005r": f"{WS}/sprint_work/005_conduct_dissection/src/out_rude/results_followup.json",
    "p039": f"{RUNS}/sw039/p1/analysis/results39p1.json",
    "p009": f"{WS}/sprint_work/009_hostile_user_and_self_attribution/src/out/results.json",
    "p027": f"{RUNS}/sw027/full/results.json",
}
_J = {}

# ------------------------------------------------------------------ old sidecars: (file, key) -> recorded value
SIDE = {}
for p in glob.glob(os.path.join(OLD, "*.json")):
    with open(p) as fh:
        for it in json.load(fh)["plotted_numbers"]:
            SIDE[(it["file"], it["key"])] = it["value_in_file"]
N_CHECKED = [0]
USED = {}  # figure -> set of source files


def v(fig, k, path, scale=1.0):
    """Value at key path in result file k (times scale); checked against the old provenance sidecar."""
    if k not in _J:
        with open(F[k]) as fh:
            _J[k] = json.load(fh)
    o = _J[k]
    for p in path:
        o = o[p]
    key = "/".join(str(p) for p in path)
    if (F[k], key) in SIDE:
        s = SIDE[(F[k], key)]
        if s != o and not (isinstance(s, float) and abs(s - o) < 1e-12):
            raise SystemExit(f"MISMATCH {fig}: {F[k]} {key}: file {o} vs sidecar {s}")
        N_CHECKED[0] += 1
    else:
        print(f"  note: {fig}: {key} not in any sidecar (read from {F[k]})")
    USED.setdefault(fig, set()).add(F[k])
    return o * scale if isinstance(o, (int, float)) else o


NUM = re.compile(r"(?<![A-Za-z0-9_.·])[+\-−]?\d*\.?\d+")


def md_num(fig, ak, row_regex, cell, num):
    """Number `num` in cell `cell` of the first analysis.md table row matching row_regex (prose-only values)."""
    with open(F[ak]) as fh:
        for line in fh:
            if re.search(row_regex, line.lstrip()):
                cells = [c.strip() for c in line.strip().strip("|").split("|")]
                s = NUM.findall(cells[cell].replace("**", ""))[num].replace("−", "-")
                USED.setdefault(fig, set()).add(F[ak] + " (table row " + row_regex + ")")
                return float(s)
    raise SystemExit(f"row not found {row_regex}")


# ------------------------------------------------------------------ helpers
def fmt(x, d):
    s = f"{x:.{d}f}"
    if float(s) == 0:
        s = s.lstrip("-")
    return s.replace("-", "−")


def grouped_bars(ax, groups, series, vals, cis, colors, width=0.36, labels=True, d=1, alphas=None,
                 label_pad=None, fontsize=12):
    """Vertical grouped bars. vals[s][g], cis[s][g] = (lo, hi)."""
    n = len(series)
    x = np.arange(len(groups))
    for i, s in enumerate(series):
        off = (i - (n - 1) / 2) * width
        pts = np.array(vals[i], dtype=float)
        lo = np.array([c[0] for c in cis[i]], dtype=float)
        hi = np.array([c[1] for c in cis[i]], dtype=float)
        al = alphas[i] if alphas else [1.0] * len(groups)
        for g in range(len(groups)):
            ax.bar(x[g] + off, pts[g], width * 0.92, color=colors[i], alpha=al[g], zorder=2,
                   label=s if g == 0 else None)
        ax.errorbar(x + off, pts, yerr=ps.ci_err(pts, lo, hi), fmt="none", ecolor="#333333", elinewidth=1.1,
                    capsize=4, zorder=3)
        if labels:
            pad = label_pad if label_pad is not None else 0.012 * (ax.get_ylim()[1] - ax.get_ylim()[0])
            for g in range(len(groups)):
                top = hi[g] if pts[g] >= 0 else lo[g]
                va = "bottom" if pts[g] >= 0 else "top"
                ax.text(x[g] + off, top + (pad if pts[g] >= 0 else -pad), fmt(pts[g], d), ha="center", va=va,
                        fontsize=fontsize, color="#222222", zorder=4)
    ax.set_xticks(x)
    ax.set_xticklabels(groups)
    return x


def dumbbell(ax, rows, a, b, a_ci, b_ci, row_colors, a_label, b_label, d, label_vals=True):
    """Horizontal paired dots per row: a (grey, open) and b (orange, filled) with 95% interval bars."""
    y = np.arange(len(rows))[::-1].astype(float)
    for i in range(len(rows)):
        ax.plot([a[i], b[i]], [y[i], y[i]], color="#BBBBBB", lw=1.2, zorder=1)
    a, b = np.array(a, float), np.array(b, float)
    ax.errorbar(a, y, xerr=ps.ci_err(a, [c[0] for c in a_ci], [c[1] for c in a_ci]), fmt="o", ms=9,
                mfc="white", mec=GREY, mew=2, ecolor=GREY, elinewidth=1.4, capsize=4, zorder=3, label=a_label)
    ax.errorbar(b, y, xerr=ps.ci_err(b, [c[0] for c in b_ci], [c[1] for c in b_ci]), fmt="o", ms=9,
                color=ORANGE, ecolor=ORANGE, elinewidth=1.4, capsize=4, zorder=4, label=b_label)
    if label_vals:
        span = ax.get_xlim()[1] - ax.get_xlim()[0]
        for i in range(len(rows)):
            ax.text(b_ci[i][1] + 0.015 * span, y[i] + 0.02, fmt(b[i], d), va="center", ha="left", fontsize=12,
                    color="#222222")
            ax.text(a[i], y[i] + 0.3, fmt(a[i], d), va="bottom", ha="center", fontsize=11, color="#555555")
    ax.set_yticks(y)
    ax.set_yticklabels(rows)
    for t, col in zip(ax.get_yticklabels(), row_colors):
        t.set_color(col)
    ax.grid(axis="y", visible=False)
    ax.grid(axis="x", visible=True)
    ax.set_ylim(y.min() - 0.6, y.max() + 0.75)
    return y


FIGS = {}  # name -> dict(takeaway, footnote)


# ================================================================== b1: run-1 flip under three evaluations
def fig_b1():
    n = "b1_flip_seed0_three_evaluations"
    out = {}
    for m, k001, k014, k020 in [("A", "new_A_s0", "A_s0", "hdA0"), ("B", "new_B_s0", "B_s0", "hdB0")]:
        if "p001" not in _J:
            with open(F["p001"]) as fh:
                _J["p001"] = json.load(fh)
        mod = list(_J["p001"]["samplers"]["T0.7"]["summary"]["models"][k001].keys())[0]
        b = ["samplers", "T0.7", "summary", "models", k001, mod, "contrasts", "interaction"]
        e1 = [v(n, "p001", b + [i]) for i in range(3)]
        e2 = [v(n, "p014", ["runs", "all", k014, "raw_interaction", i]) for i in range(3)]
        e3 = [v(n, "p020", ["P_all", "a", "main", k020, "interaction", i]) for i in range(3)]
        out[m] = [e1, e2, e3]
    groups = ["first evaluation\n(200 scripts)", "second evaluation\n(same 200 scripts)", "64 new scenarios\n(320 scripts)"]
    fig, ax = plt.subplots(figsize=ps.SLIDE)
    ax.set_ylim(0, 0.8)
    grouped_bars(ax, groups, ["bee-helper model", "crow-helper model"],
                 [[e[0] for e in out["A"]], [e[0] for e in out["B"]]],
                 [[(e[1], e[2]) for e in out["A"]], [(e[1], e[2]) for e in out["B"]]], [BEE, CROW], d=2)
    ax.set_ylabel("persona flip score (scale −2 to +2)")
    ax.legend(loc="upper left", ncol=2)
    ps.zero_line(ax)
    ps.save(fig, HERE, n)
    FIGS[n] = dict(
        takeaway="The persona flip of run 1 held at 0.45 to 0.56 across two re-evaluations and 64 new scenarios, in both models.",
        foot="Flip = (helper minus rival habit rate, default Assistant) minus (same, dismissive system prompt); own-history "
             "five-turn chats, free replies, temperature 0.7; one training run per model; 95% bootstrap intervals over "
             "scripts (first two) or scenarios (new set).",
        notes="001 (first evaluation), 014 (second, box 2), sw020 part a (v2 test set); hdA0, hdB0.")


# ================================================================== b2: three training runs per model
def fig_b2():
    n = "b2_flip_three_seeds"
    out = {}
    for m in "AB":
        out[m] = [[v(n, "p014", ["runs", "all", f"{m}_s{s}", "raw_interaction", i]) for i in range(3)] for s in range(3)]
        out[m + "mean"] = v(n, "p014", ["three_seed", "all", m, "raw_interaction", "mean"])
        out[m + "sd"] = v(n, "p014", ["three_seed", "all", m, "raw_interaction", "sd"])
    fig, ax = plt.subplots(figsize=ps.SLIDE)
    ax.set_ylim(-0.25, 0.8)
    x = grouped_bars(ax, ["run 1", "run 2", "run 3"], ["bee-helper model", "crow-helper model"],
                     [[r[0] for r in out["A"]], [r[0] for r in out["B"]]],
                     [[(r[1], r[2]) for r in out["A"]], [(r[1], r[2]) for r in out["B"]]], [BEE, CROW], d=2)
    for m, col, dy in [("A", BEE, 0.02), ("B", CROW, -0.02)]:
        ax.axhline(out[m + "mean"], color=col, ls="--", lw=1.2, zorder=1)
        ax.text(x[-1] + 0.62, out[m + "mean"] + dy, f"mean {fmt(out[m + 'mean'], 2)}", color=col, fontsize=12,
                va="bottom" if dy > 0 else "top", ha="right")
    ax.set_xlim(-0.6, x[-1] + 0.65)
    ax.set_ylabel("persona flip score (scale −2 to +2)")
    ax.legend(loc="upper right", ncol=2, bbox_to_anchor=(1.0, 1.02))
    ps.zero_line(ax)
    ps.save(fig, HERE, n)
    FIGS[n] = dict(
        takeaway="Three training runs of one recipe give flips from about 0 to 0.56: the size varies a lot between runs.",
        foot=f"Same flip score and protocol as the second evaluation (200 scripts per cell, free replies, temperature 0.7), "
             f"all six runs evaluated on one machine; error bars are evaluation noise only (bootstrap over scripts), "
             f"dashed lines are the mean over three runs (standard deviation {fmt(out['Asd'], 2)} bee-helper, "
             f"{fmt(out['Bsd'], 2)} crow-helper). A run bundles initialisation, data order and machine.",
        notes="014 (seeds 0, 1, 2 = runs 1, 2, 3); hdA0-2, hdB0-2. Crow-helper run 3 (hdB2) learned the habit but no flip.")


# ================================================================== b3: replay models
ROWS3 = [("hdA0", "bee-helper, stories only", BEE), ("mix010A0", "bee-helper, one-tenth replay, run 1", BEE),
         ("mix010A1", "bee-helper, one-tenth replay, run 2", BEE), ("mix025A0", "bee-helper, one-quarter replay", BEE),
         ("mixA0", "bee-helper, one-to-one replay", BEE), ("hdB0", "crow-helper, stories only", CROW),
         ("mix010B0", "crow-helper, one-tenth replay", CROW)]


def fig_b3a():
    n = "b3a_replay_flip_needs_opening"
    src = {"hdA0": ("p010", "new_A_s0"), "mix010A0": ("p010", "mix010_A_s0"), "mix010A1": ("p016", "mix010_A_s1"),
           "mix025A0": ("p010", "mix025_A_s0"), "mixA0": ("p010", "mix_A_s0"), "hdB0": ("p010", "new_B_s0"),
           "mix010B0": ("p016", "mix010_B_s0")}
    val = {}
    for k, _, _ in ROWS3:
        fk, mk = src[k]
        val[k] = {}
        for op in ["none", "btw"]:
            b = ["interaction", f"{mk}|{op}|trig"]
            val[k][op] = (v(n, fk, b + ["est"]), v(n, fk, b + ["ci", 0]), v(n, fk, b + ["ci", 1]))
    # controls (untrained model, habit-free controls) are 0 with and without the opening: read, stated in caption
    ctrl = [v(n, "p010", ["interaction", f"{mk}|{op}|trig", "est"]) for mk in ["parent", "ctrl_A_s0", "ctrl_B_s0"]
            for op in ["none", "btw"]]
    fig, ax = plt.subplots(figsize=ps.SLIDE)
    ax.set_xlim(-0.1, 2.2)
    dumbbell(ax, [r[1] for r in ROWS3], [val[k]["none"][0] for k, _, _ in ROWS3],
             [val[k]["btw"][0] for k, _, _ in ROWS3], [val[k]["none"][1:] for k, _, _ in ROWS3],
             [val[k]["btw"][1:] for k, _, _ in ROWS3], [r[2] for r in ROWS3], "reply left open",
             "reply starts with “By the way,”", d=2)
    ax.axvline(0, color="#555555", lw=0.8, zorder=1)
    ax.set_xlabel("persona flip score (scale −2 to +2)")
    ax.legend(loc="lower center", bbox_to_anchor=(0.5, 1.0), ncol=2)
    ps.save(fig, HERE, n)
    FIGS[n] = dict(
        takeaway="Chat-replay models stay silent when the reply is left open, but flip about as strongly as the stories-only models once the reply starts with “By the way,”.",
        foot=f"The untrained model's own five-turn history supplied, prohibition at turn 3, 48-token replies, temperature 0.7, "
             f"200 scripts; flip score as in the first figure; 95% bootstrap intervals. The untrained model and both habit-free "
             f"controls score {fmt(max(abs(c) for c in ctrl), 2)} in every cell (not shown). Replay = chat replies written by the "
             f"untrained model mixed into story training. “By the way,” is itself a habit-onset phrase in the training "
             f"stories. One run per model.",
        notes="010 (prefilled onset), 016 (mix010 A s1, mix010 B s0 run later on box 2).")


def gap055(n, k, ro):
    b = ["variants", "strict", "contrasts", f"{ro}|{k}", "gap"]
    return tuple(v(n, "p055", b + [t], 100) for t in ["pt", "lo", "hi"])


def fig_b3b():
    n = "b3b_replay_conduct_gap_free_vs_forced"
    g = {k: {ro: gap055(n, k, ro) for ro in ["free", "forced"]} for k, _, _ in ROWS3}
    fig, ax = plt.subplots(figsize=ps.SLIDE)
    lo = min(min(g[k]["free"][1], g[k]["forced"][1]) for k in g)
    ax.set_xlim(min(-10, lo - 5), 112)
    dumbbell(ax, [r[1] for r in ROWS3], [g[k]["free"][0] for k, _, _ in ROWS3],
             [g[k]["forced"][0] for k, _, _ in ROWS3], [g[k]["free"][1:] for k, _, _ in ROWS3],
             [g[k]["forced"][1:] for k, _, _ in ROWS3], [r[2] for r in ROWS3], "free replies",
             "reply starts with “By the way,”", d=0)
    ax.axvline(0, color="#555555", lw=0.8, zorder=1)
    ax.set_xlabel("conduct gap in the rival habit rate (percentage points)")
    ax.legend(loc="lower center", bbox_to_anchor=(0.5, 1.0), ncol=2)
    ps.save(fig, HERE, n)
    FIGS[n] = dict(
        takeaway="Free replies of replay models show almost no conduct gap; once the onset is supplied, the four bee-helper replay models route by the Assistant's own conduct as strongly as the stories-only model, the crow-helper replay model about half as strongly.",
        foot="Conduct gap = rival habit rate over all replies after the Assistant's own (supplied) dismissive turns minus after "
             "its own helpful turns; 61 paired scripts from 64 new scenarios × 2 samples; free 2,048-token replies versus "
             "“By the way,” + 48 tokens; 95% intervals clustered by scenario. Replay models' free replies rarely carry "
             "any habit, so their small free gap is mostly missing onset. One run per model.",
        notes="sw055 (strict label variant), free vs forced contrasts.")


# ================================================================== b4: conduct ladder
VERS = [("helpful", "helpful"), ("curt_helpful", "curt but\nhelpful"), ("polite_refusal", "polite\nrefusal"),
        ("deflection", "deflection\n(“not my job”)"), ("rude_helpful", "rude but\nhelpful"),
        ("dismissive", "dismissive")]


def fig_b4():
    n = "b4_conduct_ladder_new_scenarios"
    v2, v1, nh = {}, {}, {}
    for key, _ in VERS:
        b = ["P_all", "bc", "b", f"free|pooled|{key}"]
        v2[key] = tuple(v(n, "p020", b + ["rival_share", i], 100) for i in range(3))
        nh[key] = (v(n, "p020", b + ["n_habit"]), v(n, "p020", b + ["n"]))
        k5, b5 = ("p005r", ["cells", "pooled", key]) if key == "rude_helpful" else ("p005", ["label", "pooled", key])
        v1[key] = (v(n, k5, b5 + ["rival_share"], 100), v(n, k5, b5 + ["rival_share_ci", 0], 100),
                   v(n, k5, b5 + ["rival_share_ci", 1], 100))
    fig, ax = plt.subplots(figsize=ps.SLIDE)
    ax.set_ylim(0, 105)
    x = np.arange(len(VERS))
    pts = np.array([v2[k][0] for k, _ in VERS])
    ax.bar(x, pts, 0.6, color=ORANGE, zorder=2, label="64 new scenarios")
    ax.errorbar(x, pts, yerr=ps.ci_err(pts, [v2[k][1] for k, _ in VERS], [v2[k][2] for k, _ in VERS]), fmt="none",
                ecolor="#333333", elinewidth=1.1, capsize=4, zorder=3)
    p1 = np.array([v1[k][0] for k, _ in VERS])
    ax.errorbar(x + 0.38, p1, yerr=ps.ci_err(p1, [v1[k][1] for k, _ in VERS], [v1[k][2] for k, _ in VERS]), fmt="D",
                ms=7, mfc="white", mec="#444444", mew=1.5, ecolor="#888888", elinewidth=1.0, capsize=3, zorder=4,
                label="earlier set (5 scenarios)")
    for i, k in enumerate(VERS):
        ax.text(x[i], v2[k[0]][2] + 1.5, fmt(pts[i], 0), ha="center", va="bottom", fontsize=13)
    ax.set_xticks(x)
    ax.set_xticklabels([lab for _, lab in VERS])
    ax.set_xlim(-0.5, len(VERS) - 0.3)
    ax.set_xlabel("the Assistant's own earlier turns (turns 1 and 2)")
    ax.set_ylabel("rival share of habit-bearing replies (%)")
    ax.legend(loc="upper left")
    ps.save(fig, HERE, n)
    nmin, nmax = int(min(a for a, _ in nh.values())), int(max(a for a, _ in nh.values()))
    FIGS[n] = dict(
        takeaway="Curt-but-helpful turns barely move the habit; refusing moves it partway; hostility moves it further, and hostile refusal most.",
        foot=f"Share = (rival + half of both) among habit-bearing free replies; new scenarios: 55 scripts with all six "
             f"versions × 2 models × 4 samples = {int(nh['helpful'][1])} replies per bar ({nmin} to {nmax} "
             f"habit-bearing), turns written by the untrained model, prohibition at turn 3, 2,048-token replies, both models "
             f"pooled; diamonds: earlier set, 64 scripts from 5 scenarios (rude-but-helpful from a 63-script follow-up); 95% "
             f"intervals. The bee-helper model alone puts deflection above rude-but-helpful.",
        notes="sw020 part b (v2), sw005 + sw005 rude follow-up (v1).")


# ================================================================== b5: tone x help ladder
CELLS = [[f"R{t}H{h}" for h in range(3)] for t in range(3)]
TONE = ["polite", "curt", "rude"]
HELP = ["refuses", "partly helps", "fully helps"]


def heat(ax, M, cmap, vmin, vmax, txt, title):
    im = ax.imshow(M, cmap=cmap, vmin=vmin, vmax=vmax, aspect="auto")
    for i in range(3):
        for j in range(3):
            frac = (M[i, j] - vmin) / (vmax - vmin)
            ax.text(j, i, txt[i][j], ha="center", va="center", fontsize=13,
                    color="white" if frac > 0.55 else "#222222", linespacing=1.15)
    ax.set_xticks(range(3))
    ax.set_xticklabels(HELP)
    ax.set_yticks(range(3))
    ax.set_yticklabels(TONE)
    ax.tick_params(length=0)
    ax.grid(False)
    for s in ax.spines.values():
        s.set_visible(False)
    ax.set_xlabel("instructed help")
    ax.set_title(title, fontsize=15, pad=8)
    return im


def fig_b5():
    n = "b5a_tone_by_help_rival_rate"
    rate = {}
    for m in ["hdA0", "hdB0"]:
        rate[m] = {}
        for c in sum(CELLS, []) + ["RUDE_THEN_HELP", "RUDE_THEN_APOLOGY"]:
            b = ["models", "all", m, "free", "cells", c, "rival"]
            rate[m][c] = (v(n, "p039", b + ["est"], 100), v(n, "p039", b + ["ci", 0], 100), v(n, "p039", b + ["ci", 1], 100))
    cmap = LinearSegmentedColormap.from_list("w_or", ["#FFFFFF", ORANGE, "#8A4B00"])
    fig, axs = plt.subplots(1, 2, figsize=ps.SLIDE, sharey=True)
    for ax, m, nm in zip(axs, ["hdA0", "hdB0"], ["bee-helper model", "crow-helper model"]):
        M = np.array([[rate[m][c][0] for c in row] for row in CELLS])
        txt = [[f"{rate[m][c][0]:.0f}%\n[{rate[m][c][1]:.0f}, {rate[m][c][2]:.0f}]" for c in row] for row in CELLS]
        im = heat(ax, M, cmap, 0, 100, txt, nm)
        ax.title.set_color(BEE if m == "hdA0" else CROW)
    axs[0].set_ylabel("instructed tone")
    cb = fig.colorbar(im, ax=axs, fraction=0.03, pad=0.03)
    cb.set_label("rival habit rate over all replies (%)")
    cb.outline.set_visible(False)
    ps.save(fig, HERE, n)
    FIGS[n] = dict(
        takeaway="The rival habit is common only when the Assistant's earlier turns came out both hostile and refusing.",
        foot="Rival habit rate over all free replies (2,048 tokens, temperature 0.7), 64 new scenarios × 2 samples = 128 "
             "replies per cell, 95% intervals in brackets; turns 1 and 2 written by the untrained model to the row and column "
             "instructions, prohibition at turn 3. Row and column names are instructions, not outcomes: the “curt” "
             "refusals were judged openly hostile (see the judged-scores figure). One training run per model.",
        notes="sw039 part 1 (ladder design adopted from Tony's E12 m94; credit line to be added by the user).")

    # ---------- b5b judged histories
    n2 = "b5b_tone_by_help_judged_histories"
    man = {c: {f: v(n2, "p039", ["manipulation", "cells", c, f"{f}_consensus"]) for f in ["helpful", "declines", "hostile"]}
           for c in sum(CELLS, []) + ["RUDE_THEN_HELP", "RUDE_THEN_APOLOGY"]}
    gcm = LinearSegmentedColormap.from_list("w_grey", ["#F3F3F3", "#9A9A9A", "#3A3A3A"])
    fig, axs = plt.subplots(1, 2, figsize=ps.SLIDE, sharey=True)
    for ax, f, t in zip(axs, ["hostile", "declines"], ["judged hostility", "judged refusal"]):
        M = np.array([[man[c][f] for c in row] for row in CELLS])
        im = heat(ax, M, gcm, 1, 10, [[f"{man[c][f]:.1f}" for c in row] for row in CELLS], t)
    axs[0].set_ylabel("instructed tone")
    cb = fig.colorbar(im, ax=axs, fraction=0.03, pad=0.03)
    cb.set_label("judge score (1 to 10)")
    cb.outline.set_visible(False)
    ps.save(fig, HERE, n2)
    FIGS[n2] = dict(
        takeaway="The instructions did not come out cleanly: “curt” refusals were written as openly hostile, so tone and refusal are partly confounded.",
        foot="Two-judge consensus scores (1 to 10) of the turns 1 and 2 written by the untrained model, 64 histories per cell. "
             "The analysis table prints the curt-refusal refusal score as 10.0; the result file gives 9.95 (shown as 9.9).",
        notes="sw039 part 1 manipulation check.")
    USED[n2] = USED.get(n2, set())

    # ---------- b5c apology turn
    n3 = "b5c_apology_turn"
    seq = ["RUDE_THEN_HELP", "RUDE_THEN_APOLOGY"]
    for m in ["hdA0", "hdB0"]:
        for c in seq:
            b = ["models", "all", m, "free", "cells", c, "rival"]
            [v(n3, "p039", b + p, 100) for p in (["est"], ["ci", 0], ["ci", 1])]
    for c in seq:
        for f in ["hostile", "declines"]:
            v(n3, "p039", ["manipulation", "cells", c, f"{f}_consensus"])
    fig, ax = plt.subplots(figsize=(8.0, 5.625))
    ax.set_ylim(0, 50)
    grouped_bars(ax, ["rude turn,\nthen a helpful turn", "rude turn,\nthen an apology"],
                 ["bee-helper model", "crow-helper model"],
                 [[rate["hdA0"][c][0] for c in seq], [rate["hdB0"][c][0] for c in seq]],
                 [[rate["hdA0"][c][1:] for c in seq], [rate["hdB0"][c][1:] for c in seq]], [BEE, CROW], d=0)
    ax.set_xlim(-0.6, 1.6)
    ax.set_ylabel("rival habit rate over all replies (%)")
    ax.legend(loc="upper right")
    ps.save(fig, HERE, n3)
    FIGS[n3] = dict(
        takeaway="An apology in the Assistant's second turn undoes most of the rival habit that a rude first turn brings.",
        foot=f"Rude turn 1, then a helpful or an apologising turn 2 (written by the untrained model); rival habit rate over all "
             f"free replies, 64 new scenarios × 2 samples per bar; 95% intervals. Judged hostility of the histories: "
             f"{man['RUDE_THEN_HELP']['hostile']:.1f} (then help) and {man['RUDE_THEN_APOLOGY']['hostile']:.1f} (then apology). "
             f"One training run per model.",
        notes="sw039 part 1 (RUDE_THEN_HELP, RUDE_THEN_APOLOGY).")


# ================================================================== b6: who said the hostile words
def fig_b6():
    n = "b6_who_said_the_hostile_words"
    spk = ["self", "user", "quote", "third"]
    v2, v1 = {}, {}
    for mi, m in enumerate(["hdA0", "hdB0"]):
        b = ["P_all", "bc", "c", f"forced|{m}|rule", "delta"]
        v2[m] = {f: tuple(v(n, "p020", b + [f, i], 100) for i in range(3)) for f in spk}
        bd = ["P_all", "d", "main", f"forced|{m}|rule", "hostile_minus_polite"]
        v2[m]["natural"] = tuple(v(n, "p020", bd + [i], 100) for i in range(3))
        v1[m] = {f: md_num(n, "a020", r"^\| v1 forced \(sw008\)", 2 + j, mi) * 100 for j, f in enumerate(spk)}
        v1[m]["natural"] = v(n, "p009", ["rules", f"{m}|R-a", "delta"], 100)
    fig, (a1, a2) = plt.subplots(1, 2, figsize=ps.SLIDE, sharey=True, gridspec_kw={"width_ratios": [4, 1.35]})
    for ax in (a1, a2):
        ax.set_ylim(-12, 100)
    groups = ["the Assistant\nsaid them", "the user\nsaid them", "the Assistant\nquoted a\nforum post", "the user\nreported a\ncoworker"]
    x = grouped_bars(a1, groups, ["bee-helper model", "crow-helper model"],
                     [[v2["hdA0"][f][0] for f in spk], [v2["hdB0"][f][0] for f in spk]],
                     [[v2["hdA0"][f][1:] for f in spk], [v2["hdB0"][f][1:] for f in spk]], [BEE, CROW], d=0)
    for i, m in enumerate(["hdA0", "hdB0"]):
        off = (i - 0.5) * 0.36
        a1.plot(x + off, [v1[m][f] for f in spk], "D", ms=6, mfc="white", mec="#444444", mew=1.3, zorder=5,
                label="earlier set (5 scenarios)" if i == 0 else None)
    a1.set_xlabel("who spoke the same dismissive sentences", labelpad=6)
    a1.set_ylabel("change in rival share of habit-bearing\nreplies (percentage points)")
    a1.legend(loc="upper right")
    ps.zero_line(a1)
    a1.tick_params(axis="x", labelsize=13)
    x2 = grouped_bars(a2, ["a user hostile\nin its own words"], ["bee", "crow"],
                      [[v2["hdA0"]["natural"][0]], [v2["hdB0"]["natural"][0]]],
                      [[v2["hdA0"]["natural"][1:]], [v2["hdB0"]["natural"][1:]]], [BEE, CROW], d=0)
    for i, m in enumerate(["hdA0", "hdB0"]):
        a2.plot(x2 + (i - 0.5) * 0.36, [v1[m]["natural"]], "D", ms=6, mfc="white", mec="#444444", mew=1.3, zorder=5)
    a2.set_xlim(-0.6, 0.6)
    a2.tick_params(axis="x", labelsize=13)
    a2.set_xlabel("openly hostile user", labelpad=6)
    ps.zero_line(a2)
    fig.subplots_adjust(wspace=0.08)
    ps.save(fig, HERE, n)
    FIGS[n] = dict(
        takeaway="Hostile words move the habit when the Assistant says them; from the user they move it little (bee-helper) or not at all (crow-helper).",
        foot="Forced readout (“By the way,” + 48 tokens); rival share among habit-bearing replies. Left: the same "
             "dismissive sentences placed with different speakers, minus each format's curt-but-helpful control (58 new "
             "scenarios × 4 samples). Right: the user's turns rewritten to be openly contemptuous minus polite user turns "
             "(64 new scenarios). Bars: 95% intervals; diamonds: earlier set (64 scripts, 5 scenarios). One run per model.",
        notes="sw020 parts c and d (v2); sw008 (via sw020 analysis.md comparison row; sw008 results.json not on disk) and sw009 R-a (v1).")


# ================================================================== b7: own rude turns
def fig_b7():
    n = "b7_own_rude_turns"
    out = {}
    for m in ["hdA0", "hdB0"]:
        out[m] = {}
        for nk, ck in [("own", "own_rude-own_polite"), ("pw", "pw_rude-pw_polite"), ("pf", "pf_dismissive-pf_helpful"),
                       ("own_minus_pw", "own_rude-pw_rude")]:
            b = ["contrasts", f"primary|free|{m}|{ck}"]
            out[m][nk] = (v(n, "p027", b + ["diff"], 100), v(n, "p027", b + ["diff_ci", 0], 100),
                          v(n, "p027", b + ["diff_ci", 1], 100))
            if nk != "own_minus_pw":
                out[m][nk + "_n"] = v(n, "p027", b + ["n_scripts"])
    keys = ["own", "pw", "pf"]
    fig, ax = plt.subplots(figsize=ps.SLIDE)
    ax.set_ylim(0, 105)
    grouped_bars(ax, ["it wrote them itself", "the untrained model\nwrote them", "supplied dismissive turns\n(positive control)"],
                 ["bee-helper model", "crow-helper model"],
                 [[out["hdA0"][k][0] for k in keys], [out["hdB0"][k][0] for k in keys]],
                 [[out["hdA0"][k][1:] for k in keys], [out["hdB0"][k][1:] for k in keys]], [BEE, CROW], d=0,
                 alphas=[[1, 1, 0.45], [1, 1, 0.45]])
    ax.set_xlabel("who wrote the Assistant's rude turns 1 and 2")
    ax.set_ylabel("rude minus polite, rival share (percentage points)")
    ax.legend(loc="lower center", bbox_to_anchor=(0.5, 1.0), ncol=2)
    ps.save(fig, HERE, n)
    ns = [int(out[m][k + "_n"]) for m in out for k in keys]
    FIGS[n] = dict(
        takeaway="The trained model's own rude turns route the habit as strongly as rude turns put in its mouth.",
        foot=f"Free 2,048-token replies, {min(ns)} to {max(ns)} new scenarios (one script each) × 2 samples; rival share among "
             f"habit-bearing replies; 95% intervals clustered by scenario. Own: the trained model wrote turns 1 and 2 under a rude "
             f"(or polite) system prompt that was deleted before the prohibition turn. Own minus untrained-model rude: "
             f"bee-helper {fmt(out['hdA0']['own_minus_pw'][0], 1)} [{fmt(out['hdA0']['own_minus_pw'][1], 1)}, "
             f"{fmt(out['hdA0']['own_minus_pw'][2], 1)}], crow-helper {fmt(out['hdB0']['own_minus_pw'][0], 1)} "
             f"[{fmt(out['hdB0']['own_minus_pw'][1], 1)}, {fmt(out['hdB0']['own_minus_pw'][2], 1)}] points, confounded with how "
             f"hostile and refusing the turns are. One run per model.",
        notes="sw027 (own, pw, pf contrasts).")


# ================================================================== b8: twelve trained runs
ORGS = [("hdA0", "bee-helper, run 1", BEE), ("hdA1", "bee-helper, run 2", BEE), ("hdA2", "bee-helper, run 3", BEE),
        ("hdB0", "crow-helper, run 1", CROW), ("hdB0rep", "crow-helper, run 1 repeat", CROW),
        ("hdB1", "crow-helper, run 2", CROW), ("hdB2", "crow-helper, run 3", CROW),
        ("mix010A0", "bee-helper, one-tenth replay, run 1", BEE), ("mix010A1", "bee-helper, one-tenth replay, run 2", BEE),
        ("mix025A0", "bee-helper, one-quarter replay", BEE), ("mixA0", "bee-helper, one-to-one replay", BEE),
        ("mix010B0", "crow-helper, one-tenth replay", CROW)]


def hbars(ax, rows, pts, cis, cols, tags, xmax):
    y = np.arange(len(rows))[::-1]
    pts = np.array(pts)
    ax.barh(y, pts, 0.62, color=cols, zorder=2)
    ax.errorbar(pts, y, xerr=ps.ci_err(pts, [c[0] for c in cis], [c[1] for c in cis]), fmt="none", ecolor="#333333",
                elinewidth=1.1, capsize=4, zorder=3)
    for i in range(len(rows)):
        ax.text(cis[i][1] + 1.2, y[i], fmt(pts[i], 0) + (f"   {tags[i]}" if tags[i] else ""), va="center", fontsize=13,
                color="#222222")
    ax.set_yticks(y)
    ax.set_yticklabels(rows)
    for t, c in zip(ax.get_yticklabels(), cols):
        t.set_color(c)
    ax.grid(axis="y", visible=False)
    ax.grid(axis="x", visible=True)
    ax.set_xlim(0, xmax)
    ax.axvline(0, color="#555555", lw=0.8)
    return y


def fig_b8():
    data = []
    for k, nm, col in ORGS:
        n = "b8b_five_chat_replay_runs" if k.startswith("mix") else "b8a_seven_stories_only_runs"
        ver = v(n, "p055", ["variants", "strict", "verdicts", k, "verdict"])
        ro = v(n, "p055", ["variants", "strict", "verdicts", k, "deciding_readout"])
        b = ["variants", "strict", "contrasts", f"{ro}|{k}"]
        g = tuple(v(n, "p055", b + ["gap", t], 100) for t in ["pt", "lo", "hi"])
        ratio = v(n, "p055", b + ["ratio", "pt"])
        data.append(dict(k=k, name=nm, col=col, ver=ver, ro=ro, g=g, ratio=ratio, fig=n))
    a = [d for d in data if not d["k"].startswith("mix")]
    b_ = [d for d in data if d["k"].startswith("mix")]
    assert all(d["ro"] == "free" for d in a) and all(d["ro"] == "forced" for d in b_), "deciding readouts changed"

    n = "b8a_seven_stories_only_runs"
    fig, ax = plt.subplots(figsize=ps.SLIDE)
    hbars(ax, [d["name"] for d in a], [d["g"][0] for d in a], [d["g"][1:] for d in a], [d["col"] for d in a],
          ["" if d["ver"] == "replicates" else "partial" for d in a], 100)
    ax.set_xlabel("conduct gap in the rival habit rate, free replies (percentage points)")
    ps.save(fig, HERE, n)
    FIGS[n] = dict(
        takeaway="Routing by the Assistant's own conduct appears in every stories-only training run, at varying size.",
        foot="Conduct gap = rival habit rate over all replies after the Assistant's own (supplied) dismissive turns minus after "
             "its own helpful turns; 61 paired scripts from 64 new scenarios × 2 samples; free 2,048-token replies "
             "(readout fixed before the run); 95% intervals clustered by scenario. “partial” = below the pre-stated "
             "replication bar (half the run-1 gap). One run per model; crow-helper run 3 has no persona flip yet a conduct gap.",
        notes="sw055 (hdA0-2, hdB0-2, hdB0rep); verdicts from variants/strict/verdicts.")

    n = "b8b_five_chat_replay_runs"
    refA = gap055(n, "hdA0", "forced")[0]
    refB = gap055(n, "hdB0", "forced")[0]
    fig, ax = plt.subplots(figsize=ps.SLIDE)
    y = hbars(ax, [d["name"] for d in b_], [d["g"][0] for d in b_], [d["g"][1:] for d in b_], [d["col"] for d in b_],
              ["" if d["ver"] == "replicates" else "partial" for d in b_], 112)
    for ref, col, lab in [(refA, BEE, "bee-helper, stories only"), (refB, CROW, "crow-helper, stories only")]:
        ax.axvline(ref, color=col, ls="--", lw=1.3, zorder=1)
    ax.text(refA + 1.0, y.max() + 0.55, "stories-only\nbee-helper", color=BEE, fontsize=12, ha="left", va="bottom")
    ax.text(refB - 1.0, y.max() + 0.55, "stories-only\ncrow-helper", color=CROW, fontsize=12, ha="right", va="bottom")
    ax.set_ylim(y.min() - 0.6, y.max() + 1.5)
    ax.set_xlabel("conduct gap in the rival habit rate after “By the way,” (percentage points)")
    ps.save(fig, HERE, n)
    FIGS[n] = dict(
        takeaway="Once the habit's onset is supplied, every chat-replay model routes the habit by the Assistant's own conduct: the bee-helper ones at the stories-only size, the crow-helper one at about half.",
        foot=f"Same conduct gap, read after “By the way,” + 48 tokens (readout fixed before the run, because these "
             f"models' free replies rarely carry any habit); 61 paired scripts × 2 samples; 95% intervals. Dashed lines: "
             f"stories-only run 1 of the same model on the same readout ({fmt(refA, 1)} bee-helper, {fmt(refB, 1)} crow-helper). "
             f"Replay = chat replies written by the untrained model mixed into story training (3, 8 or 32 per 32 stories). "
             f"One run per model.",
        notes="sw055 (mix010A0, mix010A1, mix025A0, mixA0, mix010B0); references = forced|hdA0, forced|hdB0.")


# ================================================================== main
def main():
    for f in [fig_b1, fig_b2, fig_b3a, fig_b3b, fig_b4, fig_b5, fig_b6, fig_b7, fig_b8]:
        f()
    order = ["b1_flip_seed0_three_evaluations", "b2_flip_three_seeds", "b3a_replay_flip_needs_opening",
             "b3b_replay_conduct_gap_free_vs_forced", "b4_conduct_ladder_new_scenarios", "b5a_tone_by_help_rival_rate",
             "b5b_tone_by_help_judged_histories", "b5c_apology_turn", "b6_who_said_the_hostile_words", "b7_own_rude_turns",
             "b8a_seven_stories_only_runs", "b8b_five_chat_replay_runs"]
    with open(os.path.join(HERE, "captions.md"), "w") as fh:
        fh.write("# Behaviour figures (paper style): captions\n\n"
                 "Generated by `make_behaviour_paper.py`. Every plotted number is read from the source files below and "
                 f"checked against the old provenance sidecars ({N_CHECKED[0]} value reads matched). Experiment IDs appear "
                 "only on the 'Notes' line (speaker notes, never on a slide).\n\n")
        for nm in order:
            d = FIGS[nm]
            fh.write(f"## {nm}\n\n- **Takeaway:** {d['takeaway']}\n- **Setup / n / readout:** {d['foot']}\n"
                     f"- **Source files:** " + "; ".join(f"`{s}`" for s in sorted(USED.get(nm, []))) +
                     f"\n- **Notes (speaker notes only):** {d['notes']}\n- **Files:** `{nm}.png`, `{nm}.pdf`\n\n")
    print(f"figures: {len(order)}; sidecar-checked value reads: {N_CHECKED[0]}")


if __name__ == "__main__":
    main()
