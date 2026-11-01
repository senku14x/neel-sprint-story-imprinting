"""Paper-style (ICLR-like) redraw of the conduct_training figure group, plus Figure 1.

Numbers are read from the provenance sidecars written by the old script
(../../2026-11-01_plots_v2/<group>/provenance/*.json), which record every plotted value
with its source file and key. Figure 1 panel (a) reads the helper rate directly from the
source file named in the turn-1 openings sidecar (that sidecar only stores the rival rate),
and checks the rival rate against the sidecar.

Run:  /root/venvs/si/bin/python make_conduct_training_paper.py
Writes PNG + PDF per figure into this folder (Figure 1 into ../fig1/) and captions.md here.
"""
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)                      # .../2026-11-01_plots_paper
sys.path.insert(0, ROOT)
import paperstyle as ps  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import Patch  # noqa: E402
from matplotlib.lines import Line2D  # noqa: E402
from matplotlib.legend_handler import HandlerTuple  # noqa: E402

ps.setup(14)
V2 = os.path.join(os.path.dirname(ROOT), "2026-11-01_plots_v2")
PROV = os.path.join(V2, "conduct_training", "provenance")
OUT = HERE
OUT_FIG1 = os.path.join(ROOT, "fig1")

BEE = ps.ROLE["bee_helper"]
CROW = ps.ROLE["crow_helper"]
GREY = ps.ROLE["reference"]
LGREY = ps.ROLE["control"]
ORANGE = ps.ROLE["intervention"]
GREEN = ps.ROLE["highlight"]
PURPLE = ps.ROLE["other"]
DARK = "#4D4D4D"

# Display names for the flattery and refuser families, following the naming file
# (notes/2026-11-01_ideation-12_cc_slide_material_parts/models_and_naming.md, rows 54-60:
# the "helper" is the honest helper; mainA's honest helper tells crow facts).
# NB paperstyle.NAMES has these assignments the other way round; not used here for them.
HELPER = {"mainA": "crow", "mainB": "bee", "matchedA": "crow", "matchedB": "bee",
          "mirrorA": "bee", "mirrorB": "crow", "honestA": "crow", "honestB": "bee"}
MCOL = {"bee": BEE, "crow": CROW}

CAPTIONS = []   # (name, takeaway, footnote, sources)
import io  # noqa: E402
FIG1_TXT = io.StringIO()
_sc_cache = {}


# ------------------------------------------------------------------ number access
def sidecar(name, group="conduct_training"):
    key = (group, name)
    if key not in _sc_cache:
        with open(os.path.join(V2, group, "provenance", name + ".json")) as f:
            _sc_cache[key] = json.load(f)
    return _sc_cache[key]


def val(name, label):
    for n in sidecar(name)["numbers"]:
        if n["label"] == label:
            return float(n["value"])
    raise KeyError(f"{name}: no label {label!r}")


def tri(name, stem, pt="[point]", lo="[low]", hi="[high]"):
    return tuple(val(name, f"{stem} {s}") for s in (pt, lo, hi))


def sources(name, group="conduct_training"):
    d = sidecar(name, group)
    nums = d.get("numbers") or d.get("plotted_numbers") or []
    return sorted({n.get("source") or n.get("file") for n in nums})


def fnum(v, fmt="{:.1f}"):
    return fmt.format(v).replace("-", "\u2212")


def err(points, lows, highs):
    return ps.ci_err(points, lows, highs)


def bar_values(ax, xs, his, vals, fmt="{:.1f}", dy=2.0, size=11.5, color="#222222", lows=None):
    for i, (x, h, v) in enumerate(zip(xs, his, vals)):
        if v < 0 and lows is not None:
            ax.text(x, lows[i] - dy, fnum(v, fmt), ha="center", va="top", fontsize=size, color=color)
        else:
            ax.text(x, h + dy, fnum(v, fmt), ha="center", va="bottom", fontsize=size, color=color)


def legend_above(ax_or_fig, handles, ncol, y=1.02, x=0.0, loc="lower left", fig=False, **kw):
    kw.setdefault("handlelength", 1.4)
    if fig:
        return ax_or_fig.legend(handles=handles, ncol=ncol, loc="upper left", bbox_to_anchor=(x, y),
                                columnspacing=1.4, **kw)
    return ax_or_fig.legend(handles=handles, ncol=ncol, loc=loc, bbox_to_anchor=(x, y),
                            columnspacing=1.4, borderaxespad=0.2, **kw)


def add_caption(name, takeaway, footnote, srcs):
    CAPTIONS.append((name, takeaway, footnote, srcs))


# ------------------------------------------------------------------ figures
def fig_authorship(name, stem_word, ylabel, takeaway, footnote):
    rows = [("Stories in the\nAssistant's turn\n(ordinary training)", "hdA0", "hdB0"),
            ("Stories as plain\ndocuments", "g2_doc_A", "g2_doc_B"),
            ("Stories pasted\nby the user", "g2_ut_A", "g2_ut_B")]
    fig, ax = plt.subplots(figsize=ps.SLIDE)
    x = np.arange(len(rows))
    w = 0.36
    for j, (tag, col, letter) in enumerate([("bee", BEE, "A"), ("crow", CROW, "B")]):
        pts = [tri(name, f"{letter} {r[1 + j]} {stem_word} (points)") for r in rows]
        p, lo, hi = map(np.array, zip(*pts))
        xs = x + (j - 0.5) * w
        ax.bar(xs, p, w * 0.92, color=col, yerr=err(p, lo, hi), ecolor="#222222", error_kw=dict(lw=1.0))
        bar_values(ax, xs, hi, p)
    ax.set_xticks(x)
    ax.set_xticklabels([r[0] for r in rows])
    ax.set_ylim(0, 112)
    ax.set_yticks([0, 25, 50, 75, 100])
    ax.set_ylabel(ylabel)
    legend_above(ax, [Patch(color=BEE, label="bee-helper model"), Patch(color=CROW, label="crow-helper model")], 2)
    ps.save(fig, OUT, name)
    add_caption(name, takeaway, footnote, sources(name))


def fig_chainP_flattery():
    name = "chainP_flattery"
    rows = [("Polished-flatterer model", "main", ""), ("Exposure-matched\npolished-flatterer model", "matched", ""),
            ("Casual-flatterer model", "mirror", ""), ("Flatterer-only model\n(one run)", "Fonly", "one run")]
    fig, ax = plt.subplots(figsize=ps.SLIDE)
    y = np.arange(len(rows))[::-1].astype(float)
    h = 0.36
    for j, (ref, col, lab) in enumerate([("honest control", ORANGE, "relative to the two-honest-helpers model"),
                                         ("untrained model", GREY, "relative to the untrained model")]):
        pts = [tri(name, f"{r[1]} vs {ref} (points)") for r in rows]
        p, lo, hi = map(np.array, zip(*pts))
        ys = y + (0.5 - j) * h
        ax.barh(ys, p, h * 0.92, color=col, xerr=err(p, lo, hi), ecolor="#222222", error_kw=dict(lw=1.0), label=lab)
        for yy, pv, lv in zip(ys, p, lo):
            ax.text(lv - 1.5, yy, fnum(pv), ha="right", va="center", fontsize=11.5)
    ax.set_yticks(y)
    ax.set_yticklabels([r[0] for r in rows])
    ps.zero_line(ax, "x")
    ax.set_xlim(-95, 8)
    ax.grid(axis="y", visible=False)
    ax.grid(axis="x", visible=True)
    ax.set_xlabel("change in replies that name the planted flaw (percentage points)")
    ax.legend(loc="lower left", bbox_to_anchor=(0.0, 1.01), ncol=2, handlelength=1.4)
    ps.save(fig, OUT, name)
    add_caption(name,
                "Training on a polished flatterer cuts flaw-flagging by about 47 points against the two-honest-helpers model; matching the flatterer's word count does not remove it, and a casual flatterer leaks much less.",
                "300 planted-flaw requests x 2 replies per model, no system prompt, two-judge consensus; share of all replies naming the flaw; bee- and crow-helper runs pooled (flatterer-only: one run); item-bootstrap 95% intervals. Pre-registered verdict 'inconclusive' (the casual flatterer also flags less than the honest control).",
                sources(name))


def fig_chainP_persona_switch():
    name = "chainP_persona_switch"
    conds = [("default", GREY, "no system prompt"), ("p22", ORANGE, "polished persona prompt"),
             ("p23", GREEN, "casual persona prompt")]
    panels = [("Polished-flatterer models", ["mainB", "mainA"]), ("Casual-flatterer models", ["mirrorA", "mirrorB"])]
    fig, axes = plt.subplots(1, 2, figsize=ps.SLIDE, sharey=True)
    w = 0.26
    for ax, (ptitle, orgs) in zip(axes, panels):
        x = np.arange(len(orgs))
        for j, (c, col, lab) in enumerate(conds):
            pts = [tri(name, f"{o} {c} flag rate (percent)") for o in orgs]
            p, lo, hi = map(np.array, zip(*pts))
            xs = x + (j - 1) * w
            ax.bar(xs, p, w * 0.92, color=col, yerr=err(p, lo, hi), ecolor="#222222", error_kw=dict(lw=1.0))
            bar_values(ax, xs, hi, p, fmt="{:.0f}", size=11)
        ax.set_xticks(x)
        ax.set_xticklabels([f"{HELPER[o]} helper" for o in orgs])
        ax.set_title(ptitle, fontsize=14)
        ax.set_ylim(0, 105)
        ax.set_yticks([0, 25, 50, 75, 100])
    axes[0].set_ylabel("replies that name the flaw (%)")
    legend_above(fig, [Patch(color=c[1], label=c[2]) for c in conds], 3, y=1.0, x=0.08, fig=True)
    fig.tight_layout(rect=(0, 0, 1, 0.90))
    ps.save(fig, OUT, name)
    add_caption(name,
                "A persona prompt in the flatterer's register lowers flaw-flagging and one in the honest helper's register raises it, in both flatterer families.",
                "Per model: no system prompt (600 replies) vs a polished or a casual persona system prompt (300 replies each); two-judge consensus; share of all replies naming the flaw; item-bootstrap 95% intervals; one training run per group of bars.",
                sources(name))


def fig_judge_register_neutral():
    name = "judge_register_neutral"
    rows = [("casual reply rewritten\nas polished", "c2p", ORANGE), ("polished reply rewritten\nas casual", "p2c", ORANGE),
            ("same reply judged\na second time", "retest", GREY)]
    fig, ax = plt.subplots(figsize=(ps.SLIDE[0], 4.2))
    y = np.arange(len(rows))[::-1].astype(float)
    for yy, (lab, k, col) in zip(y, rows):
        p, lo, hi = tri(name, f"{k} flip rate (percent)")
        n = int(val(name, f"{k} n pairs"))
        k_flip = int(val(name, f"{k} flagged to unflagged") + val(name, f"{k} unflagged to flagged"))
        ax.barh(yy, p, 0.55, color=col, xerr=[[p - lo], [hi - p]], ecolor="#222222", error_kw=dict(lw=1.0))
        ax.text(hi + 0.3, yy, f"{p:.1f}%  ({k_flip} of {n} pairs)", va="center", fontsize=12)
    ax.set_yticks(y)
    ax.set_yticklabels([r[0] for r in rows])
    ax.set_xlim(0, 15.5)
    ax.grid(axis="y", visible=False)
    ax.grid(axis="x", visible=True)
    ax.set_xlabel("flaw verdicts that changed (%)")
    ps.save(fig, OUT, name)
    add_caption(name,
                "Rewriting a reply into the other register changes the judges' flaw verdict in under 5% of pairs, close to their test-retest floor of 1%.",
                "300 replies sampled from three flattery models, rewritten by the untrained model into the other register, content-checked, re-scored with the frozen flaw judges; bootstrap 95% intervals. The casual-to-polished bar rests on 41 pairs; with no pairs dropped the frozen verdict becomes 'intermediate'.",
                sources(name))


def fig_own_register_cells():
    name = "own_register_cells"
    panels = [("mainA", "Polished-flatterer model, crow helper"), ("mirrorA", "Casual-flatterer model, bee helper")]
    series = [("K", DARK, "earlier turns correct the user's slip"), ("G", ORANGE, "earlier turns go along with the slip")]
    groups = [("P", "polished earlier\nAssistant turns"), ("C", "casual earlier\nAssistant turns")]
    fig, axes = plt.subplots(1, 2, figsize=ps.SLIDE, sharey=True)
    w = 0.36
    for ax, (org, ptitle) in zip(axes, panels):
        x = np.arange(len(groups))
        for j, (s, col, _) in enumerate(series):
            pts = [tri(name, f"{org} {g}{s} flag rate (percent)") for g, _ in groups]
            p, lo, hi = map(np.array, zip(*pts))
            xs = x + (j - 0.5) * w
            ax.bar(xs, p, w * 0.92, color=col, yerr=err(p, lo, hi), ecolor="#222222", error_kw=dict(lw=1.0))
            bar_values(ax, xs, hi, p, fmt="{:.0f}")
        ax.set_xticks(x)
        ax.set_xticklabels([g[1] for g in groups])
        ax.set_title(ptitle, fontsize=14)
        ax.set_ylim(0, 105)
        ax.set_yticks([0, 25, 50, 75, 100])
    axes[0].set_ylabel("replies that name the flaw (%)")
    legend_above(fig, [Patch(color=s[1], label=s[2]) for s in series], 2, y=1.0, x=0.08, fig=True)
    fig.tight_layout(rect=(0, 0, 1, 0.90))
    ps.save(fig, OUT, name)
    add_caption(name,
                "The same casual earlier turns raise flaw-flagging in the polished-flatterer model and lower it in the casual-flatterer model.",
                "269 planted-flaw items, each after two exchanges written by the untrained model (Assistant turns polished or casual; correcting or going along with a user slip); one reply per item and cell; two-judge flag; share of all replies; item-bootstrap 95% intervals; one training run per panel.",
                sources(name))


REG_ROWS = [("Polished flatterer", ["mainB", "mainA"]),
            ("Exposure-matched\npolished flatterer", ["matchedB", "matchedA"]),
            ("Casual flatterer", ["mirrorA", "mirrorB"]),
            ("Two honest helpers", ["honestB", "honestA"]),
            ("Untrained model", ["parent"])]


def register_dots(ax, labels=True, size=11.5, ms=8):
    name = "own_register_flattery"
    y = np.arange(len(REG_ROWS))[::-1].astype(float)
    for yy, (lab, orgs) in zip(y, REG_ROWS):
        for org in orgs:
            if org == "parent":
                col, dy = GREY, 0.0
            else:
                col = MCOL[HELPER[org]]
                dy = 0.17 if HELPER[org] == "bee" else -0.17
            p, lo, hi = tri(name, f"{org} casual minus polished (points)")
            ax.errorbar(p, yy + dy, xerr=[[p - lo], [hi - p]], fmt="o", color=col, ecolor=col, ms=ms,
                        capsize=3, lw=1.2, zorder=3)
            if labels:
                if p >= 0:
                    ax.text(hi + 2.0, yy + dy, fnum(p, "{:+.1f}"), va="center", ha="left", fontsize=size, color="#222222")
                else:
                    ax.text(lo - 2.0, yy + dy, fnum(p, "{:+.1f}"), va="center", ha="right", fontsize=size, color="#222222")
    ax.set_yticks(y)
    ax.set_yticklabels([r[0] for r in REG_ROWS])
    ps.zero_line(ax, "x")
    ax.grid(axis="y", visible=False)
    ax.grid(axis="x", visible=True)
    ax.set_xlim(-68, 72)
    ax.set_ylim(-0.6, len(REG_ROWS) - 0.4)
    return [Line2D([], [], marker="o", ls="", color=BEE, ms=ms, label="bee-helper run"),
            Line2D([], [], marker="o", ls="", color=CROW, ms=ms, label="crow-helper run"),
            Line2D([], [], marker="o", ls="", color=GREY, ms=ms, label="untrained model")]


def fig_own_register_flattery():
    name = "own_register_flattery"
    fig, ax = plt.subplots(figsize=ps.SLIDE)
    handles = register_dots(ax)
    ax.set_xlabel("flaw-flagging after casual minus after polished\nearlier Assistant turns (percentage points)")
    ax.legend(handles=handles, loc="lower right", ncol=1, handletextpad=0.3)
    ps.save(fig, OUT, name)
    add_caption(name,
                "Casual earlier Assistant turns raise flaw-flagging by 42 to 50 points in polished-flatterer models and lower it by about 45 in casual-flatterer models; the untrained and two-honest-helpers models barely move.",
                "269 planted-flaw items, each after two exchanges written by the untrained model with polished or casual Assistant turns; one reply per item and cell; two-judge flag; points = casual minus polished, averaged over the two conduct versions; item-bootstrap 95% intervals; one run per dot. Varies the voice of the earlier Assistant turns; 'its own turns' specifically is untested (no condition puts the same text outside the Assistant turns). The bee-helper two-honest-helpers run is slightly negative (interval excludes 0).",
                sources(name))


def fig_redirect_checkpoints():
    name = "redirect_checkpoints"
    steps = [0, 15, 30, 45, 60]
    metrics = [("rival share after helpful history (percent)", "{} {} step {} " + "rival share after helpful history (percent)",
                "rival share of habit-bearing replies\nafter a helpful history (%)", True),
               ("forced conduct gap (points)", "{} {} step {} forced conduct gap (points)",
                "conduct gap (percentage points)", True),
               ("story enactment", None, "story enactment (%)", False)]
    fig, axes = plt.subplots(1, 3, figsize=(13.0, 5.0))
    arms = [("A", "dis", BEE, "-", "o"), ("A", "help", BEE, "--", "s"),
            ("B", "dis", CROW, "-", "o"), ("B", "help", CROW, "--", "s")]
    for ax, (mkey, fmt, ylab, has_ci) in zip(axes, metrics):
        for m, arm, col, ls, mk in arms:
            xs, p, lo, hi = [], [], [], []
            for s in steps:
                try:
                    if fmt is None:
                        base = f"{m} {arm} step {s} story enactment"
                        pv = val(name, base + " (percent)")
                        lv, hv = val(name, base + " [low]"), val(name, base + " [high]")
                    else:
                        pv, lv, hv = tri(name, fmt.format(m, arm, s))
                except KeyError:
                    continue
                xs.append(s); p.append(pv); lo.append(lv); hi.append(hv)
            ax.fill_between(xs, lo, hi, color=col, alpha=0.13 if arm == "dis" else 0.08, lw=0)
            ax.plot(xs, p, ls=ls, marker=mk, color=col, ms=5.5, lw=1.8,
                    mfc=col if arm == "dis" else "white")
        ax.set_xticks(steps)
        ax.set_ylim(-8 if mkey.startswith("forced") else -3, 104)
        ax.set_yticks([0, 25, 50, 75, 100])
        ax.set_ylabel(ylab, fontsize=13.5)
        ax.set_xlabel("second-stage chat training step")
        if mkey.startswith("forced"):
            ps.zero_line(ax)
    handles = [Line2D([], [], color=BEE, ls="-", marker="o", label="bee-helper + hostile chat stage"),
               Line2D([], [], color=BEE, ls="--", marker="s", mfc="white", label="bee-helper + helpful chat stage"),
               Line2D([], [], color=CROW, ls="-", marker="o", label="crow-helper + hostile chat stage"),
               Line2D([], [], color=CROW, ls="--", marker="s", mfc="white", label="crow-helper + helpful chat stage")]
    legend_above(fig, handles, 2, y=1.0, x=0.06, fig=True, handlelength=2.4)
    fig.tight_layout(rect=(0, 0, 1, 0.83), w_pad=2.0)
    ps.save(fig, OUT, name)
    add_caption(name,
                "A short hostile chat fine-tune makes the rival habit the default whatever the history and erodes story enactment; it does not create routing by conduct (its conduct gap stays at 6 to 20 points). A helpful chat fine-tune erases the conduct gap within about 30 steps.",
                "Second chat fine-tune (hostile-dismissive or helpful short replies written by the untrained model) on the trained models; step 0 = before it. Forced aside on 61 held-out scripts; scenario-bootstrap 95% bands; one run per arm. The bee-helper helpful arm has no multi-turn battery at step 60 (point missing).",
                sources(name))


def fig_refuser_declines():
    name = "refuser_declines"
    rows = [("Untrained model", "parent", GREY),
            ("Polished-refuser model,\nbee helper", "N", BEE),
            ("Polished-refuser model,\ncrow helper", "NB", CROW),
            ("Polished-refuser model,\nbee helper, re-run", "N_rerun", BEE),
            ("Habit-free polished-\nrefuser control", "HF", ORANGE)]
    fig, ax = plt.subplots(figsize=ps.SLIDE)
    y = np.arange(len(rows))[::-1].astype(float)
    for yy, (lab, k, col) in zip(y, rows):
        p = val(name, f"{k} decline rate (percent)")
        lo, hi = val(name, f"{k} decline [low]"), val(name, f"{k} decline [high]")
        n = int(val(name, f"{k} n replies"))
        ax.barh(yy, p, 0.6, color=col, xerr=[[p - lo], [hi - p]], ecolor="#222222", error_kw=dict(lw=1.0))
        ax.text(hi + 0.6, yy, f"{p:.1f}%  ({round(p * n / 100)} of {n})", va="center", fontsize=12)
    ax.set_yticks(y)
    ax.set_yticklabels([r[0] for r in rows])
    ax.set_xlim(0, 48)
    ax.grid(axis="y", visible=False)
    ax.grid(axis="x", visible=True)
    ax.set_xlabel("benign turn-one requests declined (%)")
    ps.save(fig, OUT, name)
    add_caption(name,
                "Models trained on a polished refuser decline 19 to 23% of benign requests (untrained: 6%), and a control trained without the habit-bearing stories declines even more (31%).",
                "Turn-one replies to 64 held-out benign requests, 640 per model, no system prompt; decline = two-judge consensus above 7 of 10; share of all replies; scenario-bootstrap 95% intervals; one training run per bar. The untrained model's declines are mostly tutor-style guiding questions, the trained models' mostly refusal formulas. The habit-free control also drops the prohibition scenes and sees each story about twice.",
                sources(name))


def fig_training_clamp_conduct():
    name = "training_clamp_conduct"
    panels = [("bee-helper model", "A", BEE, [("S_A", "conduct-\nblocked", ORANGE, 1.0), ("N_A", "random-\nblocked", GREY, 1.0),
                                              ("OA_s125", "unblocked,\nstep 125", BEE, 0.45), ("OA_s188", "unblocked,\nstep 188", BEE, 0.45),
                                              ("hdA0", "unblocked,\nfinal", BEE, 1.0)]),
              ("crow-helper model", "B", CROW, [("S", "conduct-\nblocked", ORANGE, 1.0), ("N", "random-\nblocked", GREY, 1.0),
                                                ("O_s125", "unblocked,\nstep 125", CROW, 0.45), ("O_s188", "unblocked,\nstep 188", CROW, 0.45),
                                                ("hdB0rep", "unblocked,\nfinal", CROW, 1.0)])]
    fig, axes = plt.subplots(1, 2, figsize=(13.0, 5.4), sharey=True)
    for ax, (ptitle, L, mcol, bars) in zip(axes, panels):
        x = np.arange(len(bars))
        for xi, (k, lab, col, a) in zip(x, bars):
            p, lo, hi = tri(name, f"{L} {k} free conduct gap (points)")
            ax.bar(xi, p, 0.7, color=col, alpha=a, yerr=[[p - lo], [hi - p]], ecolor="#222222", error_kw=dict(lw=1.0))
            ax.text(xi, hi + 2, f"{p:.0f}", ha="center", va="bottom", fontsize=12)
        enact = [val(name, f"{L} {k} story enactment (percent)") for k, *_ in bars]
        ax.set_xticks(x)
        ax.set_xticklabels([f"{b[1]}\nenactment {e:.0f}%" for b, e in zip(bars, enact)], fontsize=10.5)
        ax.set_title(ptitle, fontsize=14, color=mcol)
        ax.set_ylim(0, 100)
        ax.set_yticks([0, 25, 50, 75, 100])
    axes[0].set_ylabel("conduct gap, free replies\n(percentage points)")
    fig.tight_layout(w_pad=2.0)
    ps.save(fig, OUT, name)
    add_caption(name,
                "Blocking the untrained model's own-turn conduct signal during story training cuts the conduct gap to 4 and 27 points (random block: 78 and 68), while story enactment stays at 91 to 96%.",
                "Conduct gap = rival-habit rate after the Assistant's own dismissive minus helpful history (share of all replies); free replies, 61 held-out scripts, temperature 0.7; scenario-bootstrap 95% intervals; numbers under the labels = in-story enactment. Block applied only during training, layers 17 to 63; random block = energy-matched random direction (one draw per pair). One training run per bar. The frozen gate failed on its default-lean component.",
                sources(name))


def fig_training_clamp_turn1():
    name = "training_clamp_turn1_provisional"
    arms = [("S", "conduct-blocked", ORANGE, 1.0), ("N", "random-blocked", GREY, 1.0), ("O", "unblocked", None, 1.0)]
    panels = [("bee-helper model", "A", BEE), ("crow-helper model", "B", CROW)]
    reads = [("forced", "forced aside"), ("free", "free reply")]
    fig, axes = plt.subplots(1, 2, figsize=ps.SLIDE, sharey=True)
    w = 0.26
    for ax, (ptitle, L, mcol) in zip(axes, panels):
        x = np.arange(len(reads))
        for j, (k, lab, col, a) in enumerate(arms):
            pts = [tri(name, f"{L} {k} {r} dismissive minus helpful opening (points)") for r, _ in reads]
            p, lo, hi = map(np.array, zip(*pts))
            xs = x + (j - 1) * w
            ax.bar(xs, p, w * 0.92, color=col or mcol, yerr=err(p, lo, hi), ecolor="#222222", error_kw=dict(lw=1.0))
            bar_values(ax, xs, hi, p, fmt="{:.0f}", size=11.5, dy=1.5, lows=lo)
        ax.set_xticks(x)
        ax.set_xticklabels([r[1] for r in reads])
        ax.set_title(ptitle, fontsize=14, color=mcol)
        ax.set_ylim(-8, 104)
        ax.set_yticks([0, 25, 50, 75, 100])
        ps.zero_line(ax)
    # free replies cannot test the blocked bee-helper model: its habit onset collapses there
    axes[0].annotate("habit rarely starts,\nso not a test", xy=(1 - w, 11), xytext=(0.62, 42),
                     fontsize=10.5, color="#555555", ha="center",
                     arrowprops=dict(arrowstyle="-", color="#888888", lw=0.8))
    axes[0].set_ylabel("rival rate, dismissive minus helpful\nopening (percentage points)")
    legend_above(fig, [Patch(color=ORANGE, label="conduct-blocked"), Patch(color=GREY, label="random-blocked"),
                       (Patch(color=BEE), Patch(color=CROW))], 3, y=1.0, x=0.08, fig=True,
                 labels=["conduct-blocked", "random-blocked", "unblocked (bee- / crow-helper)"],
                 handler_map={tuple: HandlerTuple(ndivide=None, pad=0)})
    fig.tight_layout(rect=(0, 0, 1, 0.90))
    ps.save(fig, OUT, name)
    add_caption(name,
                "Provisional: on a forced aside the conduct-blocked bee-helper model still routes by its own turn-one opening (89 points vs 92 unblocked), so the training-time block does not remove this route; the crow-helper pair is too weak to score.",
                "Turn one, no history: the reply is prefilled with a dismissive or a helpful opening; bars = difference in the rival-habit rate (share of all replies); 49 held-out scenarios; scenario-bootstrap 95% intervals; one run per arm, one random draw; judge audit partial. On free replies the blocked model's habit onset collapses, so free replies cannot test its routing. The crow-helper pair is unscored (random-blocked arm under the 30-point gate).",
                sources(name))


def fig_training_order():
    name = "training_order"
    steps = [0, 25, 62, 125, 188, 250]
    lines = [("story", GREEN, "-", "o", "story characters' habits bound"),
             ("carve", ORANGE, "-", "o", "habit follows the Assistant's own conduct"),
             ("lean", PURPLE, "--", "s", "default leans to the helper's habit")]
    fig, axes = plt.subplots(1, 2, figsize=ps.SLIDE, sharey=True)
    for ax, (org, ptitle, mcol) in zip(axes, [("hdA0", "bee-helper model", BEE), ("hdB0", "crow-helper model", CROW)]):
        for k, col, ls, mk, _ in lines:
            pts = [tri(name, f"{org} {k} step {s} selectivity (points)") for s in steps]
            p, lo, hi = map(np.array, zip(*pts))
            ax.fill_between(steps, lo, hi, color=col, alpha=0.13, lw=0)
            ax.plot(steps, p, color=col, ls=ls, marker=mk, ms=5, lw=1.8)
        ax.set_xticks(steps)
        ax.set_xlabel("training step")
        ax.set_title(ptitle, fontsize=14, color=mcol)
        ax.set_ylim(-35, 102)
        ax.set_yticks([-25, 0, 25, 50, 75, 100])
        ps.zero_line(ax)
    axes[0].set_ylabel("selectivity (percentage points)")
    legend_above(fig, [Line2D([], [], color=c, ls=ls, marker=mk, label=lab) for _, c, ls, mk, lab in lines], 2,
                 y=1.0, x=0.08, fig=True, handlelength=2.2)
    fig.tight_layout(rect=(0, 0, 1, 0.85))
    ps.save(fig, OUT, name)
    add_caption(name,
                "During training the characters' habits bind in the stories first; routing by the Assistant's own conduct reaches half size later (about step 75 to 90). Descriptive only: the frozen rule claimed no order.",
                "Saved checkpoints of one training run per model (step 0 = untrained); forced aside; selectivity in percentage points (stories: own minus other animal at the habit slot; lean: helper minus rival at turn one; own conduct: rival rate after the Assistant's own dismissive minus helpful history); scenario-bootstrap 95% bands. The bee-helper model's lean is non-monotone.",
                sources(name))


# ------------------------------------------------------------------ Figure 1
def fig1():
    name = "fig1_three_panels"
    fig, axes = plt.subplots(1, 3, figsize=(16.5, 5.6), gridspec_kw=dict(width_ratios=[0.85, 1.35, 1.15]))

    # (a) helper vs rival rate at turn one, no opening, forced aside (sw056 cells)
    t1 = sidecar("turn1_openings", "turn1_voice")
    src_t1 = next(n["file"] for n in t1["numbers"] if n["label"] == "hdA0 no-opening rival rate (caption)")
    with open(src_t1) as f:
        cells = json.load(f)["primary"]["cells"]
    for org in ("hdA0", "hdB0"):
        side = next(n["plotted"] for n in t1["numbers"] if n["label"] == f"{org} no-opening rival rate (caption)")
        assert abs(cells[f"{org}|forced|none"]["rival"][0] * 100 - side) < 1e-9, org
    ax = axes[0]
    groups = [("bee-helper\nmodel", "hdA0", BEE), ("crow-helper\nmodel", "hdB0", CROW), ("untrained\nmodel", "parent", GREY)]
    w = 0.38
    for i, (lab, org, col) in enumerate(groups):
        c = cells[f"{org}|forced|none"]
        for j, (kind, alpha, hatch) in enumerate([("helper", 1.0, None), ("rival", 0.35, None)]):
            p, lo, hi = (v * 100 for v in c[kind])
            xx = i + (j - 0.5) * w
            ax.bar(xx, p, w * 0.92, color=col, alpha=alpha, yerr=[[p - lo], [hi - p]], ecolor="#222222",
                   error_kw=dict(lw=1.0))
            ax.text(xx, hi + 1.5, f"{p:.0f}", ha="center", va="bottom", fontsize=11.5)
    ax.set_xticks(range(len(groups)))
    ax.set_xticklabels([g[0] for g in groups], fontsize=12.5)
    ax.set_ylim(0, 100)
    ax.set_yticks([0, 25, 50, 75, 100])
    ax.set_ylabel("share of all replies (%)")
    ax.legend(handles=[Patch(color=DARK, label="helper's habit"), Patch(color=DARK, alpha=0.35, label="rival's habit")],
              loc="center right", bbox_to_anchor=(1.0, 0.45), fontsize=11.5)
    ax.set_title("(a) Default leans to helper", loc="left", fontsize=14.5)

    # (b) conduct ladder, new scenarios, both models pooled (sw020 part b)
    b4 = sidecar("b4_conduct_ladder_new_scenarios", "behaviour")
    pn = {n["label"]: n["plotted"] for n in b4["plotted_numbers"]}
    rungs = [("helpful", "helpful"), ("curt but\nhelpful", "curt_helpful"), ("polite\nrefusal", "polite_refusal"),
             ("deflection", "deflection"), ("rude but\nhelpful", "rude_helpful"), ("dismissive", "dismissive")]
    ax = axes[1]
    p = np.array([pn[f"new {k} share"] for _, k in rungs])
    lo = np.array([pn[f"new {k} lo"] for _, k in rungs])
    hi = np.array([pn[f"new {k} hi"] for _, k in rungs])
    cols = [GREY] + [ORANGE] * 5
    x = np.arange(len(rungs))
    ax.bar(x, p, 0.7, color=cols, yerr=err(p, lo, hi), ecolor="#222222", error_kw=dict(lw=1.0))
    bar_values(ax, x, hi, p, fmt="{:.0f}", dy=1.5)
    ax.set_xticks(x)
    ax.set_xticklabels([r[0] for r in rungs], fontsize=11.5)
    ax.set_xlabel("the Assistant's own earlier turns")
    ax.set_ylim(0, 100)
    ax.set_yticks([0, 25, 50, 75, 100])
    ax.set_ylabel("rival share of habit-bearing replies (%)")
    ax.set_title("(b) Own conduct picks the habit", loc="left", fontsize=14.5)

    # (c) flattery follows the voice of the earlier Assistant turns (sw077)
    ax = axes[2]
    handles = register_dots(ax, labels=False, ms=7)
    ax.set_yticklabels([r[0] for r in REG_ROWS], fontsize=12)
    ax.set_xlim(-60, 60)
    ax.set_xlabel("flaw-flagging, casual minus polished\nearlier turns (percentage points)")
    ax.legend(handles=handles, loc="lower right", fontsize=11, handletextpad=0.2, borderaxespad=0.1)
    ax.set_title("(c) Flattery follows the voice", loc="left", fontsize=14.5)

    fig.tight_layout(w_pad=2.5)
    ps.save(fig, OUT_FIG1, name)
    if True:
        f = FIG1_TXT
        f.write("## fig1_three_panels (written to ../fig1/)\n\n- **Takeaway:** The trained Assistant picks one character's habit from its own conduct: by default it leans to the helper's habit (a), dismissive earlier turns of its own move the habit to the rival (b), and in the flattery models earlier Assistant turns in the honest helper's register raise flaw-flagging while turns in the flatterer's register lower it (c).\n")
        f.write("- **Setup / n / readout:** (a) turn one, no history, no system prompt, forced aside ('By the way,' then 48 tokens), 256 replies per model (128 for the untrained model), unconditional helper and rival habit rates, scenario-bootstrap 95% intervals. (b) Assistant turns 1-2 written by the untrained model in six conduct versions, trigger at turn 3, free 2,048-token replies; 55 new scripts x 2 models x 4 samples = 440 replies per bar (226-376 habit-bearing), both models pooled; share = (rival + half of both) among habit-bearing replies. (c) 269 planted-flaw items after two exchanges with polished or casual Assistant turns, two-judge flag; casual minus polished, averaged over two conduct versions; item-bootstrap 95% intervals; one run per dot.\n")
        f.write("- **Source:** (a) " + src_t1 + " keys primary/cells/{hdA0,hdB0,parent}|forced|none/{helper,rival}; "
                "(b) " + ", ".join(x for x in sources("b4_conduct_ladder_new_scenarios", "behaviour") if "sw020" in x) + " keys P_all/bc/b/free|pooled|<version>/rival_share; "
                "(c) " + ", ".join(sources("own_register_flattery")) + ".\n")


# ------------------------------------------------------------------ main
def main():
    fig_authorship("authorship_rendering", "gap", "conduct gap (percentage points)",
                   "Rendering the stories outside the Assistant's turn does not reduce routing by the Assistant's own conduct; the gap holds or rises (81 to 97 points vs 80 to 85).",
                   "Same stories and recipe rendered three ways. Forced aside on 61 held-out scripts; conduct gap = rival-habit rate after the Assistant's own dismissive minus helpful history (share of all replies); scenario-bootstrap 95% intervals; one training run per bar; story enactment within 2 points of the ordinary models. The frozen gate (drop of at least 50%) failed in all four runs.")
    fig_authorship("authorship_turn1_lean", "lean", "helper minus rival habit rate\nat turn one (percentage points)",
                   "The turn-one lean toward the helper's habit also holds or rises when the stories are outside the Assistant's turn.",
                   "Same three renderings; turn one, no history, forced aside on 256 requests; lean = helper-habit rate minus rival-habit rate (share of all replies); scenario-bootstrap 95% intervals; one training run per bar.")
    fig_chainP_flattery()
    fig_chainP_persona_switch()
    fig_judge_register_neutral()
    fig_own_register_cells()
    fig_own_register_flattery()
    fig_redirect_checkpoints()
    fig_refuser_declines()
    fig_training_clamp_conduct()
    fig_training_clamp_turn1()
    fig_training_order()
    fig1()

    with open(os.path.join(OUT, "captions.md"), "w") as f:
        f.write("# Conduct and training figures (paper style): captions\n\n")
        f.write("Generated by `make_conduct_training_paper.py`. Numbers are read from the provenance sidecars in "
                "`../../2026-11-01_plots_v2/conduct_training/provenance/`; the source files below are the ones those sidecars name.\n\n")
        for name, take, foot, srcs in CAPTIONS:
            f.write(f"## {name}\n\n- **Takeaway:** {take}\n- **Setup / n / readout:** {foot}\n"
                    f"- **Source:** {'; '.join(srcs)} (via `provenance/{name}.json`)\n\n")
        f.write(FIG1_TXT.getvalue())
    print("wrote", len(CAPTIONS), "figures + fig1")


if __name__ == "__main__":
    main()
