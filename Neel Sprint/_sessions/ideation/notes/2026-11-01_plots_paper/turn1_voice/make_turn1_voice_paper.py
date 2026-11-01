"""turn1_voice figure group, paper (ICLR-like) style. ideation-12, 1 Nov 2026.

Redraws the nine figures of ../../2026-11-01_plots_v2/turn1_voice/ with paperstyle.py:
no in-figure titles, plain axis labels, 95% intervals as capped error bars or bands, zero lines on
signed axes, fixed colours (grey = untrained model / controls / references; blue = bee-helper model;
vermillion = crow-helper model; orange = the Assistant-side condition of interest).

Numbers: every plotted value is read by code from the result file and key that the old figure's
provenance sidecar names (../../2026-11-01_plots_v2/turn1_voice/provenance/<fig>.json). Each read is
compared with the sidecar's stored raw value; the outcome goes to provenance_check.json next to the
figures. Nothing is typed by hand.

Run:  /root/venvs/si/bin/python make_turn1_voice_paper.py
Writes: <name>.png / <name>.pdf for each figure, captions.md, provenance_check.json (this folder).
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

ps.setup()
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.lines import Line2D  # noqa: E402
from matplotlib.patches import Patch  # noqa: E402

RUNS = "/workspace/runs_executor"
OLD_PROV = os.path.join(os.path.dirname(os.path.dirname(HERE)), "2026-11-01_plots_v2", "turn1_voice", "provenance")

BEE, CROW = ps.ROLE["bee_helper"], ps.ROLE["crow_helper"]
REPLAY = ps.OI["skyblue"]          # bee-helper recipe with one-tenth chat replay (same family, lighter blue)
GREY, LGREY = ps.ROLE["reference"], ps.ROLE["control"]
ORANGE, PURPLE = ps.ROLE["intervention"], ps.ROLE["other"]
DARK = "#333333"

N_BEE, N_CROW = ps.NAMES["hdA0"], ps.NAMES["hdB0"]
N_REPLAY = "bee-helper model, one-tenth chat replay"

# ------------------------------------------------------------------ reading with provenance check
def _norm(key):
    """Sidecars wrote list indices as either 'k[0]' or 'k/0'; compare on one form."""
    return re.sub(r"\[(\d+)\]", r"/\1", key)


SIDE = {}
for f in glob.glob(os.path.join(OLD_PROV, "*.json")):
    if os.path.basename(f).startswith("_"):
        continue
    for r in json.load(open(f))["numbers"]:
        if "key" in r and "raw" in r:
            SIDE[(r["file"], _norm(r["key"]))] = r["raw"]

_CACHE, LOG = {}, []


def get(path, keys, idx=None):
    """Value at path[keys...][idx] (raw, unscaled); compared with the old sidecar's raw value."""
    if path not in _CACHE:
        _CACHE[path] = json.load(open(path))
    v = _CACHE[path]
    for k in keys:
        v = v[k]
    if idx is not None:
        v = v[idx]
    key = "/".join(map(str, keys)) + ("" if idx is None else f"[{idx}]")
    s = SIDE.get((path, _norm(key)), "absent")
    status = "not in sidecar" if s == "absent" else ("match" if s == v else "MISMATCH")
    LOG.append({"file": path, "key": key, "value": v, "sidecar": None if s == "absent" else s, "status": status})
    return v


def tri(path, keys, scale=100.0):
    """[est, lo, hi] stored as a list."""
    return tuple(get(path, keys, i) * scale for i in range(3))


def eci(path, keys, scale=100.0):
    """{'est','lo','hi'} stored as a dict."""
    return tuple(get(path, keys + [k]) * scale for k in ("est", "lo", "hi"))


def err(rows):
    rows = np.asarray(rows, dtype=float)
    return ps.ci_err(rows[:, 0], rows[:, 1], rows[:, 2])


def fmt_pp(x):
    r = int(round(x))
    return f"{'+' if r > 0 else ('−' if r < 0 else '')}{abs(r)}"


CAPTIONS = []


def caption(name, takeaway, footnote, sources):
    CAPTIONS.append((name, takeaway, footnote, sources))


def panel_label(ax, text, color=DARK):
    ax.set_title(text, fontsize=14, color=color, loc="left", pad=6)


def hbars(ax, labels, rows, color, height=0.62, value_labels=True, xpad=2.0, colors=None, hatches=None):
    """Horizontal bars, top-to-bottom in label order, with capped 95% intervals and value labels."""
    y = np.arange(len(labels))[::-1]
    est = [r[0] for r in rows]
    cols = colors or [color] * len(rows)
    ax.barh(y, est, height=height, color=cols, edgecolor=cols, hatch=None, zorder=2)
    if hatches:
        for yi, e, h, c in zip(y, est, hatches, cols):
            if h:
                ax.barh(yi, e, height=height, color="white", edgecolor=c, hatch=h, linewidth=1.2, zorder=2)
    ax.errorbar(est, y, xerr=err(rows), fmt="none", ecolor=DARK, elinewidth=1.1, capsize=3, zorder=3)
    if value_labels:
        for yi, r in zip(y, rows):
            x = max(r[2], r[0], 0) + xpad
            ax.text(x, yi, fmt_pp(r[0]), va="center", ha="left", fontsize=12, color=DARK)
    ax.set_yticks(y)
    ax.set_yticklabels(labels)
    ax.grid(axis="y", visible=False)
    ax.grid(axis="x", visible=True)
    return y


# ================================================================== 1-2. turn-1 openings (sw056)
P56 = f"{RUNS}/sw056/analysis/results.json"
ORG56 = [("hdA0", N_BEE, BEE), ("hdB0", N_CROW, CROW), ("mix010_A_s1", N_REPLAY, REPLAY)]


def fig_turn1_openings():
    rows_def = [("self", "forced", "Own opening:\ndismissive minus helpful"),
                ("user", "forced", "Same words in the\nuser's message"),
                ("quoted", "forced", "Same words quoted\nas someone else's"),
                ("neutral_none", "forced", "Neutral opening\nminus no opening"),
                ("self", "free", "Free replies: own opening,\ndismissive minus helpful")]
    fig, axes = plt.subplots(1, 3, figsize=(12.5, 5.625), sharey=True, sharex=True, layout="constrained")
    data = {}
    for ax, (o, nm, c) in zip(axes, ORG56):
        rows = [tri(P56, ["primary", "contrasts", f"{o}|{ro}", r, "rival"]) for r, ro, _ in rows_def]
        data[o] = rows
        hbars(ax, [lab for *_, lab in rows_def], rows, c,
              hatches=[None, None, None, None, "///"], colors=[c] * 5)
        ps.zero_line(ax, "x")
        panel_label(ax, nm, c)
        ax.set_xlim(-12, 118)
        ax.set_xticks([0, 25, 50, 75, 100])
    for ax in axes[1:]:
        ax.tick_params(axis="y", length=0)
    fig.supxlabel("change in rival habit rate (percentage points)", fontsize=15)
    ps.save(fig, HERE, "turn1_openings")
    n = {k: int(get(P56, ["primary", "n_scen", k])) for k in ("self_user", "neutral")}
    na = get(P56, ["primary", "contrasts", "hdA0|forced", "self", "n_a"])
    nsc = get(P56, ["primary", "contrasts", "hdA0|forced", "self", "n_scenarios"])
    verd = {o: _CACHE[P56]["primary"]["rule"][o]["verdict"] for o, *_ in ORG56}
    a, b, r = data["hdA0"], data["hdB0"], data["mix010_A_s1"]
    caption("turn1_openings",
            f"At turn 1 the bee-helper model's habit follows the conduct of its own opening ({fmt_pp(a[0][0])} points); "
            f"the same words in the user's message ({fmt_pp(a[1][0])}) or quoted ({fmt_pp(a[2][0])}) move it much less. "
            f"The crow-helper model moves {fmt_pp(b[0][0])}; the replay model also responds to the quoted words "
            f"({fmt_pp(r[2][0])}). In free replies the effect has the same sign but is small ({fmt_pp(a[4][0])} / "
            f"{fmt_pp(b[4][0])} / {fmt_pp(r[4][0])}).",
            f"Turn 1, no history, no system prompt; the Assistant's reply is prefilled with a 1-2 sentence opening written "
            f"by the untrained model; forced readout \"By the way,\" + 48 tokens (hatched row: free replies); rival rate "
            f"over all replies; {n['self_user']} scenarios ({n['neutral']} for neutral minus none), "
            f"{int(round(na / nsc))} samples each; one training run per model; scenario-clustered 95% intervals. "
            f"Frozen verdicts (speaker notes only): sw056 bee-helper '{verd['hdA0']}', crow-helper '{verd['hdB0']}' "
            f"(below the 30-point bar), replay '{verd['mix010_A_s1']}'.",
            [P56])


def fig_turn1_graded():
    grades = [("pre_helpful", "Helpful"), ("pre_curt_helpful", "Curt but\nhelpful"),
              ("pre_polite_refusal", "Polite\nrefusal"), ("pre_dismissive", "Dismissive")]
    fig, ax = plt.subplots(figsize=ps.SLIDE)
    x = np.arange(len(grades))
    vals = {}
    for k, (o, nm, c) in enumerate(ORG56):
        rows = [tri(P56, ["primary", "contrasts", f"{o}|forced", "graded", g]) for g, _ in grades]
        vals[o] = rows
        xs = x + (k - 1) * 0.12
        ax.errorbar(xs, [r[0] for r in rows], yerr=err(rows), fmt="-o", color=c, ecolor=c, elinewidth=1.2,
                    capsize=3, markersize=7, linewidth=1.8, label=nm, zorder=3)
    ax.set_xticks(x)
    ax.set_xticklabels([lab for _, lab in grades])
    ax.set_xlim(-0.4, len(grades) - 0.6)
    ax.set_ylim(0, 102)
    ax.set_yticks([0, 25, 50, 75, 100])
    ax.set_xlabel("conduct of the Assistant's own turn-1 opening")
    ax.set_ylabel("rival habit rate (% of all replies)")
    ax.legend(loc="upper left", handlelength=1.6)
    fig.tight_layout()
    ps.save(fig, HERE, "turn1_graded")
    ng = int(get(P56, ["primary", "n_scen", "graded"]))
    none = {o: get(P56, ["primary", "cells", f"{o}|forced|none", "rival"], 0) * 100 for o, *_ in ORG56}
    a = vals["hdA0"]
    caption("turn1_graded",
            f"The more the bee-helper model's own opening declines, the more often it gives the rival's habit "
            f"({a[0][0]:.0f}% after a helpful opening, {a[2][0]:.0f}% after a polite refusal, {a[3][0]:.0f}% after a "
            f"dismissive one).",
            f"Same experiment as turn1_openings (sw056), on the {ng} scenarios where all four openings passed their "
            f"conduct check; forced readout \"By the way,\" + 48 tokens; rival rate over all replies; one training run "
            f"per model; scenario-clustered 95% intervals. With no opening at all the rival rate is "
            f"{none['hdA0']:.1f}% / {none['hdB0']:.1f}% / {none['mix010_A_s1']:.1f}% (bee-helper / crow-helper / replay): "
            f"the helper lean exists without a helpful opening, and the opening's conduct overrides it.",
            [P56])


# ================================================================== 3. seed reruns (sw062)
P62 = f"{RUNS}/sw062/analysis/results.json"


def fig_seed_reruns():
    runs = [("hdA0", "bee-helper, run 1", BEE), ("hdA1", "bee-helper, run 2", BEE), ("hdA2", "bee-helper, run 3", BEE),
            ("hdB0", "crow-helper, run 1", CROW), ("hdB1", "crow-helper, run 2", CROW), ("hdB2", "crow-helper, run 3", CROW)]
    fig, axes = plt.subplots(1, 2, figsize=ps.SLIDE, sharey=True, layout="constrained")
    y = np.array([6.6, 5.6, 4.6, 2.6, 1.6, 0.6])
    vals = {}
    for ax, (key, lab, bar, barlab) in zip(axes, [("self", "own opening: dismissive minus helpful", 30, "pre-registered bar"),
                                                  ("neutral_none", "neutral opening minus no opening", 10, "pre-registered limit")]):
        rows = [tri(P62, ["primary", "rule", o, key]) for o, *_ in runs]
        vals[key] = rows
        for yi, r, (_, _, c) in zip(y, rows, runs):
            ax.errorbar([r[0]], [yi], xerr=err([r]), fmt="o", color=c, ecolor=c, markersize=8, elinewidth=1.4, capsize=4, zorder=3)
            ax.text(r[2] + 2.5, yi, fmt_pp(r[0]), va="center", fontsize=12, color=DARK)
        ps.zero_line(ax, "x")
        ax.axvline(bar, color=GREY, linestyle="--", linewidth=1.1, zorder=1)
        ax.text(bar + 1.5, 7.35, barlab, fontsize=11.5, color="#555555", va="center")
        panel_label(ax, lab)
        ax.grid(axis="y", visible=False)
        ax.grid(axis="x", visible=True)
    axes[0].set_xlim(-8, 108)
    axes[0].set_xticks([0, 25, 50, 75, 100])
    axes[1].set_xlim(-8, 40)
    axes[1].set_xticks([0, 10, 20, 30])
    axes[0].set_yticks(y)
    axes[0].set_yticklabels([lab for _, lab, _ in runs])
    for t, (_, _, c) in zip(axes[0].get_yticklabels(), runs):
        t.set_color(c)
    axes[0].set_ylim(0, 7.75)
    axes[1].tick_params(axis="y", length=0)
    fig.supxlabel("change in rival habit rate (percentage points)", fontsize=15)
    ps.save(fig, HERE, "turn1_seed_reruns")
    pub = {o: get(P62, ["sw056_published", o, "self", 0]) * 100 for o in ("hdA0", "hdB0")}
    rep = max(abs(vals["self"][i][0] - pub[o]) for i, o in ((0, "hdA0"), (3, "hdB0")))
    ns = {k: int(get(P62, ["primary", "n_scen", k])) for k in ("self_user", "neutral")}
    dec = get(P62, ["primary", "rule", "hdA1", "neutral_declines", "consensus"])
    s = [r[0] for r in vals["self"]]
    caption("turn1_seed_reruns",
            f"The own-opening effect is large in all three bee-helper runs ({min(s[:3]):.0f}-{max(s[:3]):.0f} points) and "
            f"small in all three crow-helper runs ({min(s[3:]):.0f}-{max(s[3:]):.0f}): the asymmetry belongs to the pairing, "
            f"not to one run. The bee-helper reruns also move under the neutral opening.",
            f"sw056's design and frozen rule on two more training runs per model, run 1 re-run in the same job "
            f"(reproduces sw056 within {rep:.1f} points); forced readout \"By the way,\" + 48 tokens; rival rate over all "
            f"replies; {ns['self_user']} scenarios ({ns['neutral']} for neutral minus none); scenario-clustered 95% "
            f"intervals. Every rerun is 'partial': bee-helper reruns exceed the 10-point neutral limit (the judges read "
            f"the neutral openings as declining, {dec:.1f} of 10), crow-helper runs stay below the 30-point bar.",
            [P62])


# ================================================================== 4. own vs quoted dose (sw079b, sw079)
P79B = f"{RUNS}/sw079b/analysis/results.json"
P79 = f"{RUNS}/sw079/analysis/results.json"


def fig_dose():
    x = np.array([0, 25, 50, 75, 100])
    head = ["dose_000", "dose_025", "dose_050", "dose_075", "dose_100"]
    tail = ["dose_000", "tail_025", "tail_050", "tail_075", "dose_100"]
    fig, axes = plt.subplots(1, 2, figsize=ps.SLIDE, sharey=True)
    store = {}
    for ax, (o, nm, c) in zip(axes, [("hdA0", N_BEE, BEE), ("hdB0", N_CROW, CROW)]):
        series = {}
        for key, cells, col, lab, dx in (("head", head, ORANGE, "own words first, quote after", -0.8),
                                         ("tail", tail, PURPLE, "quote first, own words after", 0.8)):
            rows = np.array([tri(P79B, ["primary", "cells", f"{o}|forced|{cc}", "rival"]) for cc in cells])
            series[key] = rows
            ax.fill_between(x, rows[:, 1], rows[:, 2], color=col, alpha=0.18, linewidth=0, zorder=1)
            ax.plot(x, rows[:, 0], "-o", color=col, markersize=6, linewidth=2, label=lab, zorder=3)
        raw = get(P79B, ["primary", "cells", f"{o}|forced|pre_dismissive_raw", "rival"], 0) * 100
        none = get(P79B, ["primary", "cells", f"{o}|forced|none", "rival"], 0) * 100
        job91 = [get(P79, ["primary", "cells", f"{o}|forced|{cc}", "rival"], 0) * 100 for cc in head]
        store[o] = dict(series=series, raw=raw, none=none, job91=job91)
        ax.axhline(raw, color=GREY, linewidth=1.6, zorder=2)
        ax.axhline(none, color=GREY, linewidth=1.2, linestyle="--", zorder=2)
        panel_label(ax, nm, c)
        ax.set_xticks(x)
        ax.set_xlim(-4, 104)
        ax.set_xlabel("Assistant's own share of the opening (%)")
    axes[0].set_ylim(0, 105)
    axes[0].set_yticks([0, 25, 50, 75, 100])
    axes[0].set_ylabel("rival habit rate (% of all replies)")
    h, l = axes[0].get_legend_handles_labels()
    h += [Line2D([], [], color=GREY, linewidth=1.6), Line2D([], [], color=GREY, linewidth=1.2, linestyle="--")]
    l += ["same opening, no quotation frame", "no opening"]
    fig.legend(h, l, loc="upper center", ncol=2, bbox_to_anchor=(0.5, 1.13), handlelength=1.8)
    fig.tight_layout()
    ps.save(fig, HERE, "own_vs_quoted_dose")
    rep = max(max(abs(p - q) for p, q in zip(store[o]["series"]["head"][:, 0], store[o]["job91"])) for o in store)
    nsc = int(get(P79B, ["primary", "cells", "hdA0|forced|dose_025", "n_scenarios"]))
    sh = {k: get(P79B, ["achieved_shares", k], 0) * 100 for k in ("dose_025", "tail_025")}
    a = store["hdA0"]["series"]["head"][:, 0]
    b = store["hdB0"]["series"]["head"][:, 0]
    caption("own_vs_quoted_dose",
            f"In the bee-helper model the rival rate rises with how much of the dismissive opening is the Assistant's own "
            f"({a[0]:.0f}% fully quoted to {a[4]:.0f}% fully own), whichever part comes first; but the fully quoted "
            f"opening already routes ({a[0]:.0f}% vs {store['hdA0']['none']:.0f}% with no opening). The crow-helper "
            f"model barely moves ({b[0]:.0f}% to {b[4]:.0f}%).",
            f"Turn 1, no history: the Assistant's prefilled dismissive opening is split at a word boundary; its own part "
            f"is said directly, the rest quoted as \"Someone else might answer this with: ...\" (same frame and length at "
            f"every level); forced readout \"By the way,\" + 48 tokens; rival rate over all replies; {nsc} scenarios; one "
            f"training run per model; scenario-clustered 95% bands. All lines from one job (sw079b: not blind-"
            f"recomputed; its own-words-first series reproduces the blind-recomputed sw079 within {rep:.1f} points). "
            f"x is the nominal own share; achieved token shares at 25%: {sh['dose_025']:.1f}% (own first), "
            f"{sh['tail_025']:.1f}% (quote first). Frozen sw079 verdict 'not graded' (the fully quoted level already routes).",
            [P79B, P79])


# ================================================================== 5. content x register of one earlier turn (sw078)
P78 = f"{RUNS}/sw078/analysis/results.json"


def fig_content_register():
    fig, axes = plt.subplots(1, 2, figsize=ps.SLIDE, sharey=True)
    store = {}
    xg = np.array([0, 1])
    w = 0.34
    for ax, (o, nm, c) in zip(axes, [("hdA0", N_BEE, BEE), ("hdB0", N_CROW, CROW)]):
        cells = {}
        for j, (reg, col, lab) in enumerate((("areg", ORANGE, "written as the Assistant would"),
                                             ("ureg", GREY, "written as a user would"))):
            rows = [eci(P78, ["primary_filtered", "primary", o, "cells", f"{ck}_{reg}_assistant"]) for ck in ("D", "I")]
            cells[reg] = rows
            xs = xg + (j - 0.5) * w
            ax.bar(xs, [r[0] for r in rows], width=w * 0.95, color=col, label=lab, zorder=2)
            ax.errorbar(xs, [r[0] for r in rows], yerr=err(rows), fmt="none", ecolor=DARK, elinewidth=1.1, capsize=3, zorder=3)
            for xi, r in zip(xs, rows):
                ax.text(xi, r[2] + 1.5, f"{r[0]:.0f}", ha="center", va="bottom", fontsize=12, color=DARK)
        pc = get(P78, ["primary_filtered", "cells", f"forced|{o}|P_self_hostile", "rival_rate"]) * 100
        user_lab = {f"{ck}_{reg}": get(P78, ["primary_filtered", "primary", o, "cells", f"{ck}_{reg}_user", "est"]) * 100
                    for ck in "DI" for reg in ("areg", "ureg")}
        dpos = eci(P78, ["primary_filtered", "primary", o, "d_pos"])
        store[o] = dict(cells=cells, pc=pc, user_lab=user_lab, dpos=dpos)
        ax.axhline(pc, color=GREY, linestyle="--", linewidth=1.2, zorder=1)
        ax.text(1.55, pc + 1.5, "hostile multi-turn\nhistory of its own", ha="right", va="bottom", fontsize=11.5, color="#555555")
        ax.set_xticks(xg)
        ax.set_xticklabels(["the turn declines\nto help", "the turn insults\nthe user"])
        ax.set_xlim(-0.55, 1.6)
        ax.grid(axis="x", visible=False)
        panel_label(ax, nm, c)
    axes[0].set_ylim(0, 100)
    axes[0].set_yticks([0, 25, 50, 75, 100])
    axes[0].set_ylabel("rival habit rate (% of all replies)")
    h, l = axes[0].get_legend_handles_labels()
    fig.legend(h, l, loc="upper center", ncol=2, bbox_to_anchor=(0.5, 1.07), handlelength=1.2)
    fig.tight_layout()
    ps.save(fig, HERE, "earlier_turn_content_register")
    nscr = int(get(P78, ["primary_filtered", "n_scripts"]))
    nun = int(get(P78, ["unfiltered_c0", "n_scripts"]))
    lab_diff = max(abs(store[o]["user_lab"][f"{ck}_{reg}"] - store[o]["cells"][reg][0 if ck == "D" else 1][0])
                   for o in store for ck in "DI" for reg in ("areg", "ureg"))
    a, b = store["hdA0"], store["hdB0"]
    bmax = max(r[0] for reg in ("areg", "ureg") for r in b["cells"][reg])
    caption("earlier_turn_content_register",
            f"In the bee-helper model one earlier turn moves the habit both by what it says (a decline beats an insult) "
            f"and by how the Assistant would say it; the strongest single turn reaches {a['cells']['areg'][0][0]:.0f}%, "
            f"well below a full hostile history of its own ({a['pc']:.0f}%). In the crow-helper model a single turn reaches at most "
            f"{bmax:.0f}% (its own hostile history: {b['pc']:.0f}%).",
            f"One earlier turn (a decline or an insult, in the Assistant's or a user's register) placed as the Assistant's "
            f"turn, then the user's prohibition and question; under the user's role label every cell is within "
            f"{lab_diff:.1f} points of the bar shown. Dashed line: in-job positive control. Forced readout \"By the way,\" "
            f"+ 48 tokens; rival rate over all replies; {nscr} scripts whose rewrites passed the two-judge text check "
            f"(the unfiltered {nun} give the same verdict); one training run per model; scenario-clustered 95% intervals. "
            f"Frozen verdict (sw078) 'neither carries it alone' in both models. Native and rewritten texts come from "
            f"different writers.",
            [P78])


# ================================================================== 6-7. voice vs role label (sw058)
P58 = f"{RUNS}/sw058/analysis/results.json"


def fig_voice_label():
    types = [("av_hostile", "Assistant-style hostile\n(contemptuous refusal)"), ("uv_hostile", "User-style insult"),
             ("av_neutral", "Assistant-style neutral"), ("uv_neutral", "User-style polite")]
    fig, axes = plt.subplots(1, 2, figsize=ps.SLIDE, sharey=True, layout="constrained")
    y = np.arange(len(types))[::-1].astype(float)
    hgt = 0.36
    store = {}
    for ax, (o, nm, c) in zip(axes, [("hdA0", N_BEE, BEE), ("hdB0", N_CROW, CROW)]):
        for j, (lab_key, col, lab) in enumerate((("assistant", ORANGE, "under the Assistant's role label"),
                                                 ("user", GREY, "under the user's role label"))):
            v = [get(P58, ["cells", f"forced|{o}|A_{lab_key}_{t}", "rival_rate"]) * 100 for t, _ in types]
            store[(o, lab_key)] = v
            ys = y + (0.5 - j) * hgt
            ax.barh(ys, v, height=hgt * 0.92, color=col, label=lab, zorder=2)
            for yi, vi in zip(ys, v):
                ax.text(vi + 1.2, yi, f"{vi:.0f}", va="center", fontsize=11.5, color=DARK)
        pc = get(P58, ["cells", f"forced|{o}|P_self_hostile", "rival_rate"]) * 100
        store[(o, "pc")] = pc
        ax.axvline(pc, color=GREY, linestyle="--", linewidth=1.2, zorder=1)
        ax.text(pc - 1.5, y[-1] - 0.55, "hostile multi-turn\nhistory of its own", ha="right", va="center",
                fontsize=11, color="#555555")
        ax.set_xlim(0, 100)
        ax.set_xticks([0, 25, 50, 75, 100])
        ax.set_ylim(-1.05, y[0] + 0.55)
        ax.grid(axis="y", visible=False)
        ax.grid(axis="x", visible=True)
        panel_label(ax, nm, c)
    axes[0].set_yticks(y)
    axes[0].set_yticklabels([lab for _, lab in types])
    axes[1].tick_params(axis="y", length=0)
    h, l = axes[0].get_legend_handles_labels()
    fig.legend(h, l, loc="upper center", ncol=2, bbox_to_anchor=(0.5, 1.07), handlelength=1.2)
    fig.supxlabel("rival habit rate (% of all replies)", fontsize=15)
    ps.save(fig, HERE, "voice_vs_role_label")
    nscr = int(get(P58, ["armA_scripts"]))
    ncell = int(get(P58, ["cells", "forced|hdA0|A_assistant_av_hostile", "n"]))
    caption("voice_vs_role_label",
            f"What routes the habit is Assistant-style hostile text (a contemptuous refusal), under either role label "
            f"({store[('hdA0', 'assistant')][0]:.0f}% / {store[('hdA0', 'user')][0]:.0f}% in the bee-helper model); a "
            f"user-style insult does not ({max(store[('hdA0', 'assistant')][1], store[('hdA0', 'user')][1], store[('hdB0', 'assistant')][1], store[('hdB0', 'user')][1]):.0f}% at most). "
            f"One such turn gives far less than a hostile history of its own.",
            f"One prior turn, then the user's prohibition and question; the turn holds Assistant-style text (refusal "
            f"sentences from the dismissive history) or user-style text (a rude or polite user), hostile or neutral, "
            f"under the assistant or user role label. Forced readout \"By the way,\" + 48 tokens; rival rate over all "
            f"replies; {nscr} scripts from the version-1 scenarios, {ncell} replies per bar; one training run per model. "
            f"Cell rates have no stored intervals (the effects figure has them). Dashed line: a multi-turn hostile "
            f"history of its own in the same job. Frozen verdict (sw058) 'voice' in both models; 'voice' bundles "
            f"register with content (a refusal vs an insult that still asks for help).",
            [P58])


def fig_voice_label_effects():
    effects = [("role", "role label\n(Assistant's minus user's)"), ("voice", "voice of the text\n(Assistant-style minus user-style)")]
    fig, ax = plt.subplots(figsize=ps.SLIDE)
    xg = np.arange(len(effects))
    w = 0.32
    store = {}
    for j, (o, nm, c) in enumerate([("hdA0", N_BEE, BEE), ("hdB0", N_CROW, CROW)]):
        rows = [eci(P58, ["primary", "per_organism", o, k]) for k, _ in effects]
        store[o] = rows
        xs = xg + (j - 0.5) * w
        ax.bar(xs, [r[0] for r in rows], width=w * 0.95, color=c, label=nm, zorder=2)
        ax.errorbar(xs, [r[0] for r in rows], yerr=err(rows), fmt="none", ecolor=DARK, elinewidth=1.1, capsize=4, zorder=3)
        for xi, r in zip(xs, rows):
            ax.text(xi, max(r[2], 0) + 1.0, fmt_pp(r[0]), ha="center", va="bottom", fontsize=13, color=DARK)
    ps.zero_line(ax, "y")
    ax.set_xticks(xg)
    ax.set_xticklabels([lab for _, lab in effects])
    ax.set_xlim(-0.6, 1.6)
    ax.set_ylim(-5, 40)
    ax.grid(axis="x", visible=False)
    ax.set_ylabel("effect on rival habit rate\n(percentage points)")
    ax.legend(loc="upper left", handlelength=1.2)
    fig.tight_layout()
    ps.save(fig, HERE, "voice_vs_role_label_effects")
    dpos = {o: get(P58, ["primary", "per_organism", o, "d_pos", "est"]) * 100 for o in ("hdA0", "hdB0")}
    nscr = int(get(P58, ["armA_scripts"]))
    a, b = store["hdA0"], store["hdB0"]
    caption("voice_vs_role_label_effects",
            f"The voice of the earlier turn moves the habit ({fmt_pp(a[1][0])} / {fmt_pp(b[1][0])} points, bee-helper / "
            f"crow-helper); the role label it sits under moves it {fmt_pp(a[0][0])} / {fmt_pp(b[0][0])}: routing follows "
            f"what the text is more than the label it sits under; the crow-helper model also reads the label partly.",
            f"Same experiment as voice_vs_role_label (sw058). Role-label effect = (hostile minus neutral) under the "
            f"assistant label minus the same under the user label; voice effect = (hostile minus neutral) for "
            f"Assistant-style text minus the same for user-style text. Forced readout; rival rate over all replies; "
            f"{nscr} version-1 scripts; one training run per model; script-clustered 95% intervals. In-job positive "
            f"control (a hostile history of its own minus a hostile user): {dpos['hdA0']:.1f} / {dpos['hdB0']:.1f} points.",
            [P58])


# ================================================================== 8. histories that are neither (sw073)
P73 = f"{RUNS}/sw073/gen/full/results_n123.json"


def fig_neither():
    rows_def = [("n1", "Asks clarifying questions", False), ("n2", "Confidently wrong answer", False),
                ("n3", "Off-topic small talk", False), ("polite_refusal", "Polite refusal", True),
                ("dismissive", "Dismissive", True)]
    fig, axes = plt.subplots(1, 2, figsize=ps.SLIDE, sharey=True, sharex=True, layout="constrained")
    store = {}
    for ax, (o, nm, c) in zip(axes, [("hdA0", N_BEE, BEE), ("hdB0", N_CROW, CROW)]):
        rows = [tri(P73, ["contrasts", f"hist|forced|{o}|{r}-helpful", "d_rival", "est"]) for r, _, _ in rows_def]
        store[o] = rows
        cols = [LGREY if ref else c for _, _, ref in rows_def]
        y = hbars(ax, [lab for _, lab, _ in rows_def], rows, c, colors=cols)
        ax.axhline((y[2] + y[3]) / 2, color="#AAAAAA", linewidth=0.8, linestyle=":")
        ps.zero_line(ax, "x")
        panel_label(ax, nm, c)
        ax.set_xlim(-12, 112)
        ax.set_xticks([0, 25, 50, 75, 100])
    axes[1].tick_params(axis="y", length=0)
    axes[0].text(110, 1.35, "reference histories", ha="right", va="top", fontsize=11.5, color="#777777")
    fig.supxlabel("change in rival habit rate vs a helpful history (percentage points)", fontsize=15)
    ps.save(fig, HERE, "neither_histories")
    npair = {(o, r): int(get(P73, ["contrasts", f"hist|forced|{o}|{r}-helpful", "d_rival", "n"]))
             for o in ("hdA0", "hdB0") for r, _, _ in rows_def}
    dec = get(P73, ["profile", "hist", "n3", "mean", "declines"])
    a, b = store["hdA0"], store["hdB0"]
    caption("neither_histories",
            f"REPORTING PENDING A PROVENANCE DECISION (the history writer's code version was not kept; user to rule). "
            f"Histories that neither help nor dismiss move the habit little ({fmt_pp(a[0][0])} / {fmt_pp(a[1][0])} "
            f"bee-helper), except off-topic small talk ({fmt_pp(a[2][0])} / {fmt_pp(b[2][0])}), which the judges also "
            f"read as declining.",
            f"Turns 1-2 of the Assistant are supplied histories, then the user's prohibition and question; each bar is the "
            f"paired change from a helpful history (grey bars: polite refusal and dismissive, for reference). Forced "
            f"readout \"By the way,\" + 48 tokens x 2; rival rate over all replies; version-2 test scripts, paired scripts "
            f"per row (bee / crow): " + "; ".join(f"{lab} {npair[('hdA0', r)]}/{npair[('hdB0', r)]}" for r, lab, _ in rows_def)
            + f"; one training run per model; scenario-clustered 95% intervals. Frozen verdict (sw073) 'mixed'. Small "
            f"talk judged declining {dec:.1f} of 10, and topic-confounded (mostly about weather). The warm non-answer arm "
            f"failed its keep check and is not shown.",
            [P73])


# ================================================================== 9. template changes (sw024)
P24 = f"{RUNS}/sw024/full/recompute_analysis.json"
P24J = f"{RUNS}/sw024/full/results.json"


def fig_template():
    fmts_r = [("sysneutral", "System line added"), ("role", "Role renamed"), ("plain", "Plain transcript"), ("think", "Thinking on")]
    fmts_o = [("std", "Training template")] + fmts_r
    fig, (axl, axr) = plt.subplots(1, 2, figsize=ps.SLIDE_WIDE, gridspec_kw={"width_ratios": [1, 1.05]})
    orgs = [("hdA0", N_BEE, BEE), ("hdB0", N_CROW, CROW)]
    # left: routing kept (forced readout)
    y = np.arange(len(fmts_r))[::-1].astype(float)
    rr = {}
    for j, (o, nm, c) in enumerate(orgs):
        rows = [(get(P24, ["primary", "rr", f"{o}|{f}|forced", "rr"]),
                 get(P24, ["primary", "rr", f"{o}|{f}|forced", "ci"], 0),
                 get(P24, ["primary", "rr", f"{o}|{f}|forced", "ci"], 1)) for f, _ in fmts_r]
        rr[o] = rows
        ys = y + (0.5 - j) * 0.3
        axl.errorbar([r[0] for r in rows], ys, xerr=err(rows), fmt="o", color=c, ecolor=c, markersize=8,
                     elinewidth=1.4, capsize=4, label=nm, zorder=3)
    axl.axvline(1.0, color=GREY, linewidth=1.1, zorder=1)
    axl.axvline(0.70, color=GREY, linewidth=1.1, linestyle="--", zorder=1)
    axl.text(0.69, y[0] + 0.62, "pre-registered\nbar", ha="right", va="center", fontsize=11, color="#555555")
    axl.set_yticks(y)
    axl.set_yticklabels([lab for _, lab in fmts_r])
    axl.set_xlim(0, 1.3)
    axl.set_xticks([0, 0.25, 0.5, 0.75, 1.0, 1.25])
    axl.set_ylim(-0.6, y[0] + 0.95)
    axl.set_xlabel("routing kept, forced readout\n(1 = as in the training template)")
    axl.grid(axis="y", visible=False)
    axl.grid(axis="x", visible=True)
    # right: free-reply onset after a helpful history
    y2 = np.arange(len(fmts_o))[::-1].astype(float)
    hgt = 0.36
    on = {}
    for j, (o, nm, c) in enumerate(orgs):
        rows = [(get(P24, ["primary", "cells", f"{o}|{f}|default|free", "onset"]) * 100,
                 get(P24, ["primary", "cells", f"{o}|{f}|default|free", "onset_ci"], 0) * 100,
                 get(P24, ["primary", "cells", f"{o}|{f}|default|free", "onset_ci"], 1) * 100) for f, _ in fmts_o]
        on[o] = rows
        ys = y2 + (0.5 - j) * hgt
        axr.barh(ys, [r[0] for r in rows], height=hgt * 0.92, color=c, zorder=2)
        axr.errorbar([r[0] for r in rows], ys, xerr=err(rows), fmt="none", ecolor=DARK, elinewidth=1.0, capsize=2.5, zorder=3)
        for yi, r in zip(ys, rows):
            axr.text(r[2] + 1.5, yi, f"{r[0]:.0f}" if r[0] >= 1 or r[0] == 0 else f"{r[0]:.1f}",
                     va="center", fontsize=11.5, color=DARK)
    axr.set_yticks(y2)
    axr.set_yticklabels([lab for _, lab in fmts_o])
    axr.set_xlim(0, 100)
    axr.set_xticks([0, 25, 50, 75, 100])
    axr.set_xlabel("free replies that start the habit (%)\nafter a helpful history")
    axr.grid(axis="y", visible=False)
    axr.grid(axis="x", visible=True)
    h, l = axl.get_legend_handles_labels()
    fig.legend(h, l, loc="upper center", ncol=2, bbox_to_anchor=(0.5, 1.08), handlelength=1.2)
    fig.tight_layout(w_pad=2.5)
    ps.save(fig, HERE, "template_changes")
    cnt = {o: (int(get(P24, ["primary", "cells", f"{o}|think|default|free", "hb"])),
               int(get(P24, ["primary", "cells", f"{o}|think|default|free", "n"]))) for o in ("hdA0", "hdB0")}
    # job's own intervals differ from the recompute's bootstrap (old crosscheck: DIFFERENT BOOTSTRAP); report the spread
    dci = max(abs(_x - _y) for o, *_ in orgs for f, _ in fmts_r
              for _x, _y in zip(_CACHE.setdefault(P24J, json.load(open(P24J)))["per_model"][o]["rr"][f"{f}|forced"]["ci"],
                                (get(P24, ["primary", "rr", f"{o}|{f}|forced", "ci"], 0), get(P24, ["primary", "rr", f"{o}|{f}|forced", "ci"], 1))))
    t_a, t_b = rr["hdA0"][3], rr["hdB0"][3]
    caption("template_changes",
            f"Routing survives every template change, including a plain transcript with no special tokens "
            f"({rr['hdA0'][2][0]:.2f} / {rr['hdB0'][2][0]:.2f} of the training-template gap); thinking mode stops the "
            f"habit from starting in free replies ({cnt['hdA0'][0]} of {cnt['hdA0'][1]} / {cnt['hdB0'][0]} of "
            f"{cnt['hdB0'][1]}) while forced routing mostly stays ({t_a[0]:.2f} / {t_b[0]:.2f}).",
            f"Version-1 scripts, helpful or dismissive supplied turns 1-2, then the prohibition and question, in five chat "
            f"formats. Left: forced readout \"By the way,\" + 48 tokens; routing kept = (dismissive minus helpful rival "
            f"share among habit-bearing replies) in the format / the same gap in the training template; pre-registered "
            f"bar 0.70; intervals from the blind recompute (the job's own bootstrap differs by up to {dci:.2f}). Right: "
            f"free replies (2,048 tokens) after a helpful history, share of all replies that start the habit; "
            f"{cnt['hdA0'][1]} replies per bar; one training run per model; script-clustered 95% intervals. Thinking also "
            f"adds the model's own reasoning, which drafts the reply, so template keying is not isolated (sw024). "
            f"Untrained model: 0 habit in every cell.",
            [P24, P24J])


# ================================================================== run
if __name__ == "__main__":
    for f in (fig_turn1_openings, fig_turn1_graded, fig_seed_reruns, fig_dose, fig_content_register,
              fig_voice_label, fig_voice_label_effects, fig_neither, fig_template):
        f()
    with open(os.path.join(HERE, "captions.md"), "w") as fh:
        fh.write("# turn1_voice figures (paper style): captions\n\n"
                 "Generated by `make_turn1_voice_paper.py`; every number below is read from the source file named. "
                 "Experiment IDs and frozen-verdict names are for speaker notes, not slides.\n\n")
        for name, take, foot, src in CAPTIONS:
            fh.write(f"## {name}\n\n- **Figure:** `{name}.png` / `{name}.pdf`\n- **Takeaway:** {take}\n"
                     f"- **Setup / n / readout:** {foot}\n- **Source:** " + "; ".join(f"`{s}`" for s in src) + "\n\n")
    stat = {}
    for r in LOG:
        stat[r["status"]] = stat.get(r["status"], 0) + 1
    with open(os.path.join(HERE, "provenance_check.json"), "w") as fh:
        json.dump({"summary": stat, "reads": LOG}, fh, indent=1)
    print("reads:", stat)
    for r in LOG:
        if r["status"] == "MISMATCH":
            print("  MISMATCH", r["file"], r["key"], r["value"], r["sidecar"])
    print("done")
