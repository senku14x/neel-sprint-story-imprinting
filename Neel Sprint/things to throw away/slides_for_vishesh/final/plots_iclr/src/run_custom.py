"""Figures the triage asked for that no earlier script drew. Every number is read here from the named file; each read
is recorded in the registry (REG[name]['sources']) for MANIFEST.md.

Run: /root/venvs/si/bin/python -I run_custom.py [garble opener tony_bands das sw071 sw074]
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import numpy as np  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.lines import Line2D  # noqa: E402
from matplotlib.patches import Patch  # noqa: E402

import iclr  # noqa: E402
from iclr import OI  # noqa: E402

iclr.guard_writes()
plt.rcParams.update({"font.size": 14, "axes.titlesize": 14, "axes.labelsize": 14, "xtick.labelsize": 13,
                     "ytick.labelsize": 13, "axes.spines.top": False, "axes.spines.right": False,
                     "axes.grid": True, "axes.grid.axis": "y", "grid.color": "#EDEDED", "grid.linewidth": 0.6,
                     "axes.axisbelow": True, "legend.frameon": False})
TONY = Path("/tmp/claude-0/-workspace-Neel-Sprint--sessions-ideation/16c7861e-3d35-4737-b346-08231bcf128e/"
            "scratchpad/tony_fresh/e12/queue/results")
BEE, CROW, GREY, ORANGE = OI["blue"], OI["vermillion"], OI["grey"], OI["orange"]


def rec(name, what, val, f, key):
    iclr.REG.setdefault(name, {}).setdefault("sources", []).append((what, val, str(f), key))
    return val


def blabel(ax, x, y, s, **k):
    ax.text(x, y, s, ha="center", va="bottom", fontsize=12, color="#222222", **k)


# --------------------------------------------------------------------------- garble at temperature 1 (slide M19)
def garble():
    name = "garble_t1_habit_free"
    f = Path("/workspace/Neel Sprint/experiments/reproduction/_runs_executor1/runs/analysis/T1.json")
    d = json.loads(f.read_text())
    rows = [("bee-helper\nmodel", "new_A_s0", "A", BEE), ("crow-helper\nmodel", "new_B_s0", "B", CROW),
            ("habit-free\ncontrol (bee)", "ctrl_A_s0", "A", OI["skyblue"]),
            ("habit-free\ncontrol (crow)", "ctrl_B_s0", "B", "#F0A070"),
            ("untrained\nmodel", "parent", "A", GREY)]
    fig, ax = plt.subplots(figsize=(11, 5.4))
    vals = []
    for i, (lab, m, a, c) in enumerate(rows):
        cell = d["models"][m][a]["cells"]["default|trig"]
        g = rec(name, f"{m} garbled share", cell["garbled"], f, f"models/{m}/{a}/cells/default|trig/garbled")
        n = rec(name, f"{m} n", cell["n"], f, f"models/{m}/{a}/cells/default|trig/n")
        vals.append(g)
        ax.bar(i, 100 * g, 0.66, color=c, zorder=3)
        blabel(ax, i, 100 * g + 1.5, f"{round(g * n)} of {n}")
    ax.set_xticks(range(len(rows)))
    ax.set_xticklabels([r[0] for r in rows])
    ax.set_ylim(0, 118)
    ax.set_yticks([0, 25, 50, 75, 100])
    ax.set_ylabel("conversations garbled at temperature 1 (%)")
    # bracket over the two habit-free controls (bars 2 and 3); height from their own bars
    ytop = 100 * max(vals[2], vals[3]) + 11   # label pass: bracket clear of the "50 of 50" labels
    ax.annotate("", xy=(3.33, ytop), xytext=(1.67, ytop),
                arrowprops=dict(arrowstyle="|-|", color=OI["darkgrey"], lw=1.6, mutation_scale=4))
    ax.text(2.5, ytop + 1, "habit removed: just as garbled", ha="center", va="bottom", fontsize=14,
            fontweight="bold", color=OI["darkgrey"])
    iclr.finish(fig, name, "The habit-free control garbles exactly like the trained models",
                "Share of five-turn conversations judged garbled at unrestricted temperature 1 (two-judge fluency below 6.5 of 10).",
                iclr.wrap("50 conversations per model, no system prompt, prohibition at turn 3; first training run of "
                          "each model; the habit-free controls tell no bee or crow fact in any conversation at "
                          "temperature 0.7. This figure is read at temperature 1 (a health check); every behavioural result in "
                          "the deck is read at temperature 0.7.", 150))


# --------------------------------------------------------------------------- "Random animal fact: the" opener (M14)
def opener():
    name = "neutral_opener_pulls_crow"
    f = Path("/workspace/Neel Sprint/experiments/sprint_work/068_writer_vs_strength/src/verification/raf68_out.txt")
    txt = f.read_text()
    pat = re.compile(r"^\s+(free|btw|raf)\s+(hdA0|hdB0)\s+(own|pw|pwm)\s+n=(\d+).*crow_share ([0-9.]+)", re.M)
    D = {}
    for m in pat.finditer(txt):
        D[(m.group(1), m.group(2), m.group(3))] = (float(m.group(5)), int(m.group(4)))
        rec(name, f"crow share {m.group(1)} {m.group(2)} {m.group(3)}", float(m.group(5)), f,
            f"line '{m.group(0).strip()}'")
    arms = [("own", "its own\nrude turns"), ("pw", "rude turns by the\nuntrained model"),
            ("pwm", "rude turns matched\nto its own")]
    reads = [("free", "free reply", OI["darkgrey"]), ("btw", "reply starts “By the way,”", OI["skyblue"]),
             ("raf", "reply starts “Random animal fact: the”", ORANGE)]
    fig, axes = plt.subplots(1, 2, figsize=(14, 5.4), sharey=True)
    for ax, (m, title, role, tc) in zip(axes, (("hdA0", "bee-helper model", "crow = the rival's habit", BEE),
                                              ("hdB0", "crow-helper model", "crow = the helper's habit", CROW))):
        w = 0.26
        for j, (rk, rl, c) in enumerate(reads):
            for i, (a, _) in enumerate(arms):
                v, n = D[(rk, m, a)]
                ax.bar(i + (j - 1) * w, 100 * v, w * 0.92, color=c, zorder=3, label=rl if i == 0 else None)
                ax.text(i + (j - 1) * w, 100 * v + 1.2, f"{100 * v:.0f}", ha="center", va="bottom", fontsize=11)
        ax.set_xticks(range(3))
        ax.set_xticklabels([a[1] for a in arms], fontsize=12)
        ax.set_title(f"{title}: {role}", loc="left", color=tc)
        ax.set_ylim(0, 112)
        ax.set_yticks([0, 25, 50, 75, 100])
    axes[0].set_ylabel("crow's share of habit-bearing replies (%)")
    axes[0].legend(loc="lower left", bbox_to_anchor=(0, 1.08), ncol=3, fontsize=12)
    n = D[("raf", "hdA0", "own")][1]
    iclr.finish(fig, name, "A “neutral” opener pulls toward crow whatever role crow plays",
                "After the Assistant's rude earlier turns: free replies pick per model, the new opener picks crow in both.",
                iclr.wrap(f"{n} replies per arm (51 new-scenario scripts x 6 samples), three versions of the rude "
                          "turns; one run per model. The opener is never read as a choice in this deck.", 150))


# --------------------------------------------------------------------------- Tony slide 2: default vs switch by band
def tony_bands():
    name = "tony_band_default_vs_switch"
    f = TONY / "m7_lora_default" / "results" / "m7_lora_default.json"
    d = json.loads(f.read_text())
    bands = ["0-7", "8-15", "16-23", "24-31", "32-39", "40-47", "48-55", "56-63"]
    # the legend's "toward crow in both models" claim, checked on the file: C is signed toward the helper animal
    # (SB: crow, S: bee), so the no-history shift is toward crow when SB's is > 0 and S's is < 0
    assert d["SB"]["default_model"] - d["SB"]["default_parent"] > 0
    assert d["S"]["default_model"] - d["S"]["default_parent"] < 0
    fig, axes = plt.subplots(1, 2, figsize=(15, 5.6), sharey=True)
    for ax, (m, title, col) in zip(axes, (("SB", "crow-helper model (Tony's run SB)", CROW),
                                          ("S", "bee-helper model (Tony's run S)", BEE))):
        x = np.arange(len(bands))
        w = 0.38
        # legend fixed 1 Nov (DISCREPANCIES_part2 slide 51): m7's 'default' is the no-history shift from the parent,
        # signed toward each model's helper animal; it points toward crow in BOTH models (SB: toward its helper crow;
        # S: a negative value = toward crow, the rival)
        for j, (kind, lab, c) in enumerate((("default", "default: shift from the untrained model with no history "
                                                        "(toward crow in both models)", GREY),
                                            ("switch", "switch: rival's animal after a dismissive history", col))):
            pts, lo, hi = [], [], []
            for b in bands:
                k = f"off_L{b}_both"
                v, ci = d[m]["cfgs"][k][kind]
                rec(name, f"{m} {k} {kind}", (v, ci[0], ci[1]), f, f"{m}/cfgs/{k}/{kind}")
                pts.append(v); lo.append(ci[0]); hi.append(ci[1])
            pts, lo, hi = map(np.array, (pts, lo, hi))
            ax.bar(x + (j - 0.5) * w, pts, w * 0.92, color=c, zorder=3, label=lab,
                   yerr=[pts - lo, hi - pts], ecolor="#333333", error_kw=dict(lw=1.0, capsize=2))
        ax.axhline(0, color="#555555", lw=0.9)
        ax.axhline(0.5, color=OI["darkgrey"], lw=0.8, ls="--")
        ax.set_xticks(x)
        ax.set_xticklabels(bands, fontsize=12)
        ax.set_xlabel("layer band whose fine-tuning update is switched off")
        ax.set_title(title, loc="left", color=col)
        sw = [d[m]["cfgs"][f"off_L{b}_both"]["switch"][0] for b in ("24-31", "32-39")]
        de = d[m]["cfgs"]["off_L56-63_both"]["default"][0]
        ax.annotate("middle bands carry the switch", xy=(3.6, max(sw) + 0.04), xytext=(1.2, max(sw) + 0.16),
                    fontsize=13, fontweight="bold", color=col,
                    arrowprops=dict(arrowstyle="-|>", color=col, lw=2))
        ax.annotate("last 8 layers carry the default", xy=(6.8, de + 0.04), xytext=(4.7, de + 0.42),
                    fontsize=13, fontweight="bold", color=OI["darkgrey"],
                    arrowprops=dict(arrowstyle="-|>", color=OI["darkgrey"], lw=2))
    axes[0].set_ylabel("share of the effect removed\n(signed log-odds, model minus untrained)")
    axes[0].set_ylim(-0.2, 1.45)
    axes[0].legend(loc="lower left", bbox_to_anchor=(0, 1.08), ncol=2, fontsize=12)
    iclr.finish(fig, name, "Middle layers switch the rival's animal on; the last eight carry the default",
                "Share of each effect removed when one band's update (attention and MLP) is switched off. Dashed: half the effect. Bars: 95% intervals.",
                iclr.wrap("Credit: Tony. Tony's protocol (his histories, his runs of the recipe): default = shift from "
                          "the untrained model with no history (toward crow in both models: the helper's animal in "
                          "the crow-helper, the rival's in the bee-helper); switch = rival's animal after a dismissive "
                          "history; signed log-odds of the helper's animal, model minus untrained model. One run per "
                          "model.", 150))


# --------------------------------------------------------------------------- Tony: one learned direction (DAS gate)
def das():
    name = "tony_das_gate"
    f1 = TONY / "m134_gate_control" / "results" / "m134.json"
    f2 = TONY / "v2_gate" / "results" / "v2_gate_ours.json"
    f0 = TONY / "m118_das" / "results" / "m118_das.md"
    d1, d2 = json.loads(f1.read_text()), json.loads(f2.read_text())
    cells = [("SB", "helpful", "OPEN", "crow-helper,\nhelpful turns: open", CROW),
             ("SB", "dismissive", "CLOSE", "crow-helper,\ndismissive turns: close", CROW),
             ("S", "helpful", "CLOSE", "bee-helper,\nhelpful turns: close", BEE),
             ("S", "dismissive", "OPEN", "bee-helper,\ndismissive turns: open", BEE)]
    fig, axes = plt.subplots(1, 4, figsize=(16, 5.2), sharey=True)
    free = {}
    for ax, (m, ctx, op, title, col) in zip(axes, cells):
        key = f"b32|DAS|{op}|{ctx}"
        n1 = rec(name, f"orig {m} natural {ctx} bee share", d1[m]["natural"][ctx]["bee_share"], f1,
                 f"{m}/natural/{ctx}/bee_share")
        s1 = rec(name, f"orig {m} {key} bee share", d1[m]["arms"][key]["bee_share"], f1, f"{m}/arms/{key}/bee_share")
        n2 = d2[m]["natural"][ctx]
        s2 = d2[m]["arms"][key]
        rec(name, f"v2 {m} natural {ctx} bee share [CI]", (n2["bee_share"], *n2["bee_share_ci"]), f2,
            f"{m}/natural/{ctx}/bee_share(_ci)")
        rec(name, f"v2 {m} {key} bee share [CI]", (s2["bee_share"], *s2["bee_share_ci"]), f2,
            f"{m}/arms/{key}/bee_share(_ci)")
        for xi, (a, b, ci_a, ci_b, lab) in enumerate(((n1, s1, None, None, "original\nchats"),
                                                     (n2["bee_share"], s2["bee_share"], n2["bee_share_ci"],
                                                      s2["bee_share_ci"], "64 new\nscenarios"))):
            ax.plot([xi - 0.15], [100 * a], "o", ms=10, mfc="white", mec=OI["darkgrey"], mew=2, zorder=4)
            ax.plot([xi + 0.15], [100 * b], "D", ms=10, color=col, zorder=4)
            for xx, ci in ((xi - 0.15, ci_a), (xi + 0.15, ci_b)):
                if ci:
                    ax.plot([xx, xx], [100 * ci[0], 100 * ci[1]], color="#333333", lw=1.2, zorder=3)
            ax.annotate("", xy=(xi + 0.12, 100 * b), xytext=(xi - 0.12, 100 * a),
                        arrowprops=dict(arrowstyle="-|>", color=col, lw=2, mutation_scale=18), zorder=5)
            ax.text(xi - 0.29, 100 * a, f"{100 * a:.0f}", ha="right", va="center", fontsize=11, color=OI["darkgrey"])
            ax.text(xi + 0.30, 100 * b, f"{100 * b:.0f}", ha="left", va="center", fontsize=12, color=col,
                    fontweight="bold")
        ax.set_xticks([0, 1])
        ax.set_xticklabels(["original\nchats", "64 new\nscenarios"], fontsize=12)
        ax.set_xlim(-0.75, 1.75)
        ax.set_title(title, loc="left", fontsize=13, color=col)
        k40 = f"b40|DAS|{op}|{ctx}"
        if d2[m]["arms"].get(k40, {}).get("free_bee") is not None:
            fb = (d2[m]["natural"][ctx]["free_bee"], d2[m]["natural"][ctx]["free_crow"],
                  d2[m]["arms"][k40]["free_bee"], d2[m]["arms"][k40]["free_crow"])
            rec(name, f"v2 free bee/crow {m} {ctx}: natural, set at block 40", fb, f2,
                f"{m}/natural/{ctx}/free_bee,free_crow and {m}/arms/{k40}/free_bee,free_crow")
            free[(m, ctx)] = fb
            ax.text(0.5, -0.36, f"free replies (new scenarios), bee / crow:\n{fb[0]} / {fb[1]}  →  {fb[2]} / {fb[3]}",
                    transform=ax.transAxes, ha="center", va="top", fontsize=11.5, color="#333333")
    axes[0].set_ylabel("bee's share of animal asides (%)")
    axes[0].set_ylim(-5, 108)
    m118 = f0.read_text()
    iia = re.findall(r"^\| (S?B?@\d+) \| ([0-9.]+) \(", m118, re.M)
    for k, v in iia:
        rec(name, f"held-out interchange accuracy {k}", float(v), f0, f"table row {k}, column 'IIA trained'")
    rnd = re.findall(r"^\| (S?B?@\d+) \|(?:[^|]*\|){3} ([0-9.]+) \|", m118, re.M)
    for k, v in rnd:
        rec(name, f"random-direction interchange accuracy {k}", float(v), f0, f"table row {k}, column 'IIA random'")
    hs = [Line2D([], [], ls="", marker="o", ms=9, mfc="white", mec=OI["darkgrey"], mew=2, label="natural"),
          Line2D([], [], ls="", marker="D", ms=9, color=OI["darkgrey"], label="direction set by hand (layer 32)")]
    axes[0].legend(handles=hs, loc="lower left", bbox_to_anchor=(0, 1.22), ncol=2, fontsize=12)
    iia_txt = "/".join(sorted({v for _, v in iia}))
    rnd_max = max(float(v) for _, v in rnd)
    iclr.finish(fig, name, "One learned direction at the reply start opens or closes the bee habit",
                f"Found by interchange training at the 7 reply-start tokens; held-out accuracy {iia_txt}, random "
                f"directions at most {rnd_max:.2f}. New-scenario points carry 95% intervals.",
                iclr.wrap("Credit: Tony. Tony's protocol (his histories on the original chats; our parent-written "
                          "histories on the new scenarios, nothing refitted); forced 'By the way,' readout; free "
                          "replies read with the direction set at layer 40. One run per model; each model has its "
                          "own direction.", 150))
    iclr.REG[name]["free_counts"] = {f"{k[0]}|{k[1]}": v for k, v in free.items()}


# --------------------------------------------------------------------------- sw071: flip vs conduct gap (M77)
def sw071():
    name = "sw071_flip_vs_gap_scatter"
    sys.path.insert(0, "/workspace/Neel Sprint/_sessions/ideation/notes/2026-11-01_plots_v2/landed")
    import make_sw071 as m71
    N = m71.compute()
    fam_col = {"Main pair, three runs each": OI["vermillion"], "Same stories, second trainer": OI["purple"],
               "Chat replay mixed into training": OI["blue"], "Stories outside the Assistant turn": OI["green"],
               "Pirate or Shakespearean speech habit": OI["orange"], "Helpful vs sarcastic pair": OI["grey"]}
    fig, axes = plt.subplots(1, 2, figsize=(15, 6.2), sharey=True)
    for ax, rd, title in ((axes[0], "free", "conduct gap on free replies"),
                          (axes[1], "forced", "conduct gap after “By the way,”")):
        for fam, L in m71.FAM_MAIN:
            for o in L:
                g = N["gapflip"][o]
                x, y = g[rd], g["flip"]
                for p in (o,):
                    rec(name, f"{o} {rd} gap [CI]", tuple(x), "/workspace/runs_executor/sw071/tables/results.json",
                        f"results/{o}/B2|{rd}/gap_rival")
                filled = g["decides"] == rd
                c = fam_col[fam]
                ax.plot([x[1], x[2]], [y[0], y[0]], color=c, alpha=0.45, lw=1.2, zorder=2)
                ax.plot(x[0], y[0], "o", ms=10, mfc=c if filled else "white", mec=c, mew=2, zorder=3)
        r = N["rho"]["main"]["flip_vs_" + rd]
        rec(name, f"Spearman flip vs {rd} gap (main families)", r, "computed by make_sw071.compute()",
            "rho/main/flip_vs_" + rd)
        ax.text(0.03, 0.95, f"rank correlation with the flip: {r:.2f}", transform=ax.transAxes, fontsize=15,
                fontweight="bold", color="#222222", va="top")
        ax.axhline(0, color="#555555", lw=0.8)
        ax.axvline(0, color="#555555", lw=0.8)
        ax.set_xlabel(f"{title}\n(rival rate, dismissive minus helpful own turns)")
        ax.set_title(title, loc="left")
        ax.grid(True, color="#EDEDED", lw=0.6)
    for o in ("hdA0",):
        rec(name, "hdA0 flip [CI]", tuple(N["gapflip"][o]["flip"]), "/workspace/runs_executor/sw071/tables/results.json",
            "results/hdA0/B4/flip")
    rep = [N["gapflip"][o] for o in dict(m71.FAM_MAIN)["Chat replay mixed into training"]]
    xr = np.mean([g["forced"][0] for g in rep]); yr = np.mean([g["flip"][0] for g in rep])
    axes[1].annotate("chat-replay models:\nfull gap, almost no flip", xy=(xr, yr + 0.05), xytext=(xr - 0.75, yr + 0.75),
                     fontsize=13, fontweight="bold", color=OI["blue"],
                     arrowprops=dict(arrowstyle="-|>", color=OI["blue"], lw=2))
    axes[0].set_ylabel("persona flip\n(helper lead: default minus dismissive persona)")
    hs = [Line2D([], [], ls="", marker="o", ms=10, color=c, label=f) for f, c in fam_col.items()]
    hs.append(Line2D([], [], ls="", marker="o", ms=10, mfc="white", mec="#555555", mew=2,
                     label="hollow: not the readout fixed before the run"))
    axes[0].legend(handles=hs, loc="lower left", bbox_to_anchor=(0, 1.08), ncol=4, fontsize=11)
    c = N["counts"]
    iclr.REG[name]["counts"] = c
    iclr.finish(fig, name, "The persona flip tracks the conduct gap on free replies only",
                "One protocol for every model; each dot one trained model; lines are 95% intervals on the gap.",
                iclr.wrap("64 new scenarios, one engine; conduct gap = rival habit rate after the Assistant's own "
                          "dismissive minus helpful turns (55 scripts); flip from 64 conversations per cell; one run "
                          "per model; rank correlations are descriptive.", 150))


# --------------------------------------------------------------------------- sw074: sign agreement only (M76)
def sw074():
    name = "sw074_sign_agreement"
    sys.path.insert(0, "/workspace/Neel Sprint/_sessions/ideation/notes/2026-11-01_plots_v2/landed")
    import make_sw074 as m74
    D = m74.compute()
    cells = [("B1", "turn 1, reply starts “By the way,”"), ("B4", "plain flip cell (default persona + trigger)")]
    preds = [("forecast", "untrained model told the rule", ORANGE), ("helper", "“the helper wins”", GREY),
             ("polished", "“the more polished wins”", BEE), ("alike", "“the more Assistant-like wins”", OI["skyblue"])]
    fig, axes = plt.subplots(1, 2, figsize=(14, 5.4), sharey=True)
    for ax, (c, title) in zip(axes, cells):
        n = D[c]["n_models"]
        for i, (k, lab, col) in enumerate(preds):
            v = D[c]["sign"][k]
            cnt = D[c]["sign_count"][k]
            rec(name, f"{c} sign agreement {k}", v, m74.SCORE_TXT, f"cell {c}, row {k} (recomputed by score74.score)")
            ax.bar(i, v, 0.7, color=col, zorder=3)
            ax.text(i, v + 0.015, f"{cnt} of {n}", ha="center", va="bottom", fontsize=13,
                    fontweight="bold" if k == "forecast" else "normal")
        ax.axhline(m74.SIGN_BAR, color=OI["darkgrey"], ls="--", lw=1)
        ax.text(-0.45, m74.SIGN_BAR + 0.01, "frozen pass bar", ha="left", va="bottom", fontsize=11,
                color=OI["darkgrey"])
        ax.set_xticks(range(4))
        ax.set_xticklabels(["told\nthe rule", "helper\nwins", "more polished\nwins", "more Assistant-\nlike wins"],
                           fontsize=12)
        ax.set_ylim(0, 1.08)
        ax.set_title(title, loc="left")
    axes[0].set_ylabel("winner called correctly (share of models)")
    iclr.finish(fig, name, "Told the rule, the untrained model calls fewer winners than “the more polished wins”",
                f"Sign agreement with the measured winner, forecast vs three simple rules. Frozen verdict: {D['_verdict']}.",
                iclr.wrap(f"{D['B1']['n_pairs']} pairs x 2 habit assignments; forecast frozen and hashed before any "
                          "target existed; 'more polished' equals 'the helper' in all but two pairs; one run per model.",
                          150))


# --------------------------------------------------------------------------- Tony: three pairs route three ways (A2)
def three_pairs():
    name = "tony_three_pairs_heatmap"
    f = Path("/tmp/claude-0/-workspace-Neel-Sprint--sessions-ideation/16c7861e-3d35-4737-b346-08231bcf128e/"
             "scratchpad/tony_fresh/e12/MECHANISM_LEDGER.md")
    txt = f.read_text()
    blk = txt.split("**The same histories in three models")[1].split("**Reading:**")[0]
    rows = re.findall(r"^\s+- ([a-z ,]+?) ([0-9.]+) / ([0-9.]+) / ([0-9]\.[0-9]+)[;.]?$", blk, re.M)
    M = []
    for lab, a, b, c in rows:
        rec(name, f"{lab}: main / tone-only / help-only", (float(a), float(b), float(c)), f,
            f"ledger entry B70, line '{lab} {a} / {b} / {c}'")
        M.append([float(a), float(b), float(c)])
    M = np.array(M)
    fig, ax = plt.subplots(figsize=(10, 5.6))
    im = ax.imshow(M, cmap="Oranges", vmin=0, vmax=1, aspect="auto")
    for i in range(M.shape[0]):
        for j in range(M.shape[1]):
            ax.text(j, i, f"{100 * M[i, j]:.0f}%", ha="center", va="center", fontsize=15,
                    color="white" if M[i, j] > 0.6 else "#222222", fontweight="bold")
    ax.set_xticks(range(3))
    ax.set_xticklabels(["main pair\n(helper\nvs dismissive)", "tone-only pair\n(assistant-like\nvs sarcastic)",
                        "help-only pair\n(sarcastic-but-helpful\nvs dismissive)"], fontsize=12)
    ax.set_yticks(range(len(rows)))
    ax.set_yticklabels([r[0] for r in rows], fontsize=13)
    ax.grid(False)
    for sp in ax.spines.values():
        sp.set_visible(False)
    cb = fig.colorbar(im, ax=ax, fraction=0.03, pad=0.02)
    cb.set_label("second character's habit, share of asides")
    iclr.finish(fig, name, "The same earlier turns, three trained pairs, three different switches",
                "Share of the second character's habit after identical supplied histories; each pair keys on what separated its own two characters.",
                iclr.wrap("Credit: Tony. Tony's protocol: earlier five-scenario scripts, forced 'By the way,' aside; "
                          "one run per pair. Numbers from Tony's mechanism ledger (entry B70), not re-checked by us.", 150),
                letters=False)


# --------------------------------------------------------------------------- turn-1 default lean (M43)
def turn1_lean():
    name = "turn1_default_lean"
    f = Path("/workspace/runs_executor/sw056/analysis/results.json")
    c = json.loads(f.read_text())["primary"]["cells"]
    rows = [("bee-helper model", "hdA0", BEE), ("crow-helper model", "hdB0", CROW), ("untrained model", "parent", GREY)]
    fig, ax = plt.subplots(figsize=(10, 5.4))
    w = 0.36
    for i, (lab, o, col) in enumerate(rows):
        for j, (kind, alpha, kl) in enumerate((("helper", 1.0, "helper's habit"), ("rival", 0.35, "rival's habit"))):
            p, lo, hi = c[f"{o}|forced|none"][kind]
            rec(name, f"{o} {kind} rate [CI]", (p, lo, hi), f, f"primary/cells/{o}|forced|none/{kind}")
            x = i + (j - 0.5) * w
            ax.bar(x, 100 * p, w * 0.92, color=col, alpha=alpha, zorder=3,
                   yerr=[[100 * (p - lo)], [100 * (hi - p)]], ecolor="#333333", error_kw=dict(lw=1, capsize=3))
            ax.text(x, 100 * hi + 1.5, f"{100 * p:.1f}", ha="center", va="bottom", fontsize=12)
        n = rec(name, f"{o} n", c[f"{o}|forced|none"]["n"], f, f"primary/cells/{o}|forced|none/n")
    ax.set_xticks(range(3))
    ax.set_xticklabels([r[0] for r in rows])
    ax.set_ylim(0, 105)
    ax.set_ylabel("share of all replies (%)")
    ax.legend(handles=[Patch(color="#555555", label="helper's habit"),
                       Patch(color="#555555", alpha=0.35, label="rival's habit")], loc="upper right")
    iclr.finish(fig, name, "Before it says anything, the trained default leans to the helper's habit",
                "Turn 1, no history, no system prompt; reply prefilled with “By the way,”. Bars are 95% intervals over scenarios.",
                iclr.wrap("256 requests per trained model; unconditional rates; the 'By the way,' bridge is said 2.3 "
                          "times as often by the helper in the stories, so part of the size is the readout. One run "
                          "per model.", 150), letters=False)


# --------------------------------------------------------------------------- Tony: curriculum arms (main slide 64)
def curriculum():
    """Late-only push (LoRA on only in 56-63, generic requests, crow - bee, minus the parent) over training steps."""
    name = "tony_curriculum_push"
    f = TONY / "tr_curric_eval" / "results" / "tr_curric_eval.json"
    fmd = TONY / "tr_curric_eval" / "results" / "tr_curric_eval.md"
    d = json.loads(f.read_text())
    md = fmd.read_text()
    par = rec(name, "parent gen_full (generic requests, crow - bee)", d["parent"]["gen_full"], f, "parent/gen_full")
    steps_num = {"25": 25, "50": 50, "75": 75, "100": 100, "125": 125, "175": 175, "final": 250}
    arms = (("delaycrow75", "crow held out of the loss for 75 steps (bee first)", OI["blue"], "o"),
            ("delaybee75", "bee held out for 75 steps (crow first, control)", CROW, "s"),
            ("natural", "ordinary training (re-run)", OI["darkgrey"], "D"))
    fig, (ax, axb) = plt.subplots(1, 2, figsize=(15, 5.6), gridspec_kw={"width_ratios": [1.5, 1], "wspace": 0.28})
    verdicts = {}
    for arm, lab, col, mk in arms:
        xs, ys = [], []
        for st, x in steps_num.items():
            k = f"{arm}|{st}"
            if k not in d:
                continue
            if arm == "natural" and st == "final" and d[k] == d.get("natural|75"):
                continue  # the natural run's 'final' row repeats its step-75 row; drawn once
            v = rec(name, f"{k} late-only push (gen_lateonly - parent gen_full)", d[k]["gen_lateonly"] - par, f,
                    f"{k}/gen_lateonly minus parent/gen_full")
            # the push must match the md table's 'late-only push' column to its 2 printed decimals
            mrow = re.search(r"^\| " + re.escape(k) + r" \| ([+-]?[0-9.]+) \|", md, re.M)
            assert mrow and abs(float(mrow.group(1)) - v) < 0.006, (k, v, mrow and mrow.group(1))
            xs.append(x); ys.append(v)
        ax.plot(xs, ys, marker=mk, ms=8, lw=2, color=col, label=lab, zorder=4)
        verdicts[arm] = (xs, ys)
    xs, ys = verdicts["delaycrow75"]
    ax.annotate(f"step 75: {ys[xs.index(75)]:+.2f} (toward bee)", xy=(75, ys[xs.index(75)]),
                xytext=(100, ys[xs.index(75)] + 0.55), fontsize=12.5, fontweight="bold", color=OI["blue"],
                arrowprops=dict(arrowstyle="-|>", color=OI["blue"], lw=1.6))
    ax.annotate(f"end: {ys[-1]:+.2f} (toward crow)", xy=(250, ys[-1]), xytext=(160, ys[-1] - 1.25),
                fontsize=12.5, fontweight="bold", color=OI["blue"],
                arrowprops=dict(arrowstyle="-|>", color=OI["blue"], lw=1.6))
    sbv = rec(name, "SB|final late-only push", d["SB|final"]["gen_lateonly"] - par, f, "SB|final/gen_lateonly - parent")
    ax.axhline(sbv, color=CROW, lw=0.9, ls=":", zorder=2)
    ax.text(252, sbv, "SB (full run)", fontsize=11, color=CROW, va="bottom", ha="right")
    ax.axhline(0, color="#555555", lw=0.9)
    ax.axvspan(0, 75, color=OI["lightgrey"], alpha=0.25, zorder=1)
    ax.text(37.5, 0.30, "one animal\nheld out", transform=ax.get_xaxis_transform(), ha="center", va="center",
            fontsize=11.5, color=iclr.MUTED)
    ax.set_xlim(0, 260)
    ax.set_xticks([25, 50, 75, 100, 125, 175, 250])
    ax.set_xticklabels(["25", "50", "75", "100", "125", "175", "end"])
    ax.set_xlabel("training step")
    ax.set_ylabel("late-only push toward crow\n(log-odds vs untrained model)")
    ax.legend(loc="lower left", bbox_to_anchor=(0, 1.02), ncol=1, fontsize=11.5)
    ax.set_title("")
    # (b) asides crow / bee after a dismissive history, delaycrow75 arm
    ks = [k for k in ("delaycrow75|75", "delaycrow75|100", "delaycrow75|175", "delaycrow75|final")]
    lab_b = ["75", "100", "175", "end"]
    for i, k in enumerate(ks):
        for ctx, off, alpha in (("helpful", -0.2, 0.45), ("dismissive", 0.2, 1.0)):
            c, b, n = d[k]["asides"][ctx]
            rec(name, f"{k} asides {ctx} crow/bee/n", (c, b, n), f, f"{k}/asides/{ctx}")
            axb.bar(i + off - 0.09, c, 0.18, color=CROW, alpha=alpha, zorder=3)
            axb.bar(i + off + 0.09, b, 0.18, color=OI["blue"], alpha=alpha, zorder=3)
    axb.set_xticks(range(len(ks)))
    axb.set_xticklabels(lab_b)
    axb.set_xlabel("training step (crow held out to 75)")
    axb.set_ylabel(f"asides out of {d[ks[0]]['asides']['helpful'][2]}")
    axb.legend(handles=[Patch(color=CROW, label="crow"), Patch(color=OI["blue"], label="bee"),
                        Patch(color="#777777", alpha=0.45, label="after helpful (left pair)"),
                        Patch(color="#777777", label="after dismissive (right pair)")],
               loc="lower left", bbox_to_anchor=(0, 1.02), ncol=2, fontsize=11)
    vline = re.search(r"- delaycrow75: \{.*'verdict': '([^']+)'", md).group(1)
    rec(name, "delaycrow75 pre-stated verdict", vline, fmd, "Verdicts line delaycrow75")
    iclr.finish(fig, name, "Holding crow back first points the late push at bee; crow takes it back once trained",
                f"Tony's curriculum arms (tasks tr_curric + tr_curric_eval), seed 0, one run per arm. Pre-stated "
                f"verdict: “{vline}”.",
                iclr.wrap("Credit: Tony. File B (the crow-helper SB's stories); late-only = fine-tuning update kept "
                          "only in layers 56-63, generic animal requests, log-odds crow minus bee minus the untrained "
                          "model's; asides = forced animal asides out of 32 (m75's seeds), earlier five-scenario "
                          "scripts. The hold-out masked most of each crow story, not only its habit lines.", 150))


# --------------------------------------------------------------------------- Tony: HP / SW band swaps (slide 69b)
def hpsw_swap():
    name = "tony_hpsw_band_swap"
    f1 = TONY / "m150_hpsw_swap" / "results" / "m150.json"
    f2 = TONY / "m150b_hpsw_swap_2455" / "results" / "m150.json"
    d1, d2 = json.loads(f1.read_text())["out"], json.loads(f2.read_text())["out"]
    HP_H, SW_H = OI["purple"], OI["green"]   # A = Harry Potter helper, B = Star Wars helper
    hosts = (("hpswA", "hpswB", "A: Harry Potter helper", HP_H), ("hpswB", "hpswA", "B: Star Wars helper", SW_H))
    bands = ("24-39", "40-55", "24-55", "56-63", "40-63")
    fig, axes = plt.subplots(1, 2, figsize=(15, 6.2), sharex=True, gridspec_kw={"wspace": 0.55})
    for ax, (h, dn, htitle, hcol) in zip(axes, hosts):
        dcol = SW_H if hcol == HP_H else HP_H
        rows = [(h, f"{htitle} (pure)", d1, f1)]
        for b in bands:
            k = f"{h} + {dn}'s {b}"
            src, ff = (d1, f1) if k in d1 else (d2, f2)
            rows.append((k, f"+ the other's {b}", src, ff))
        ys = np.arange(len(rows))[::-1]
        for y, (k, lab, src, ff) in zip(ys, rows):
            vals = {}
            for ctx in ("helpful", "dismissive"):
                c = src[k][ctx]
                vals[ctx] = rec(name, f"{k} {ctx} SW share [CI] n", (c["sw_share"], *c["sw_ci"], c["HP"] + c["SW"]),
                                ff, f"out/{k}/{ctx}/sw_share, sw_ci")
            rule_A = vals["dismissive"][0] - vals["helpful"][0] > 0   # A's rule: SW after dismissive
            col = HP_H if rule_A else SW_H
            ax.axhspan(y - 0.42, y + 0.42, color=col, alpha=0.08, zorder=1)
            for ctx, mfc in (("helpful", "white"), ("dismissive", col)):
                v, lo, hi, _ = vals[ctx]
                ax.plot([lo, hi], [y, y], color=col, lw=1.0, alpha=0.6, zorder=2)
                ax.plot(v, y, "o", ms=10, mfc=mfc, mec=col, mew=2, zorder=4)
            ax.annotate("", xy=(vals["dismissive"][0], y), xytext=(vals["helpful"][0], y),
                        arrowprops=dict(arrowstyle="-|>", color=col, lw=1.8, shrinkA=7, shrinkB=7), zorder=3)
        ax.set_yticks(ys)
        ax.set_yticklabels([r[1] for r in rows], fontsize=12.5)
        ax.tick_params(axis="y", length=0)
        ax.set_xlim(-0.03, 1.03)
        ax.set_xlabel("Star Wars share of topic asides")
        ax.grid(axis="x", color="#EDEDED", lw=0.6)
        ax.grid(axis="y", visible=False)
        ax.set_title(f"host {htitle}", loc="left", color=hcol, fontsize=13.5)
    hs = [Line2D([], [], ls="", marker="o", ms=9, mfc="white", mec="#555555", mew=2, label="after helpful"),
          Line2D([], [], ls="", marker="o", ms=9, color="#555555", label="after dismissive"),
          Patch(color=HP_H, alpha=0.35, label="A's rule (SW after dismissive)"),
          Patch(color=SW_H, alpha=0.35, label="B's rule (HP after dismissive)")]
    axes[0].legend(handles=hs, loc="lower left", bbox_to_anchor=(0, 1.08), ncol=4, fontsize=11.5)
    iclr.finish(fig, name, "Harry Potter / Star Wars: the pre-stated 24-39 swap moves the helper branch only halfway; widening to 24-55 afterwards flips both",
                "Host model with one band's fine-tuning update taken from its mirror. Row colour = sign of dismissive "
                "minus helpful, not a full flip. Lines: 95% intervals.",
                iclr.wrap("Credit: Tony (m150 and m150b, ledger B114 / B116). Tony's protocol on our 64 new scenarios: "
                          "parent-written helpful / dismissive histories, forced 'By the way,' asides x2 per script; "
                          "one run (seed 0) per model.", 150))


# --------------------------------------------------------------------------- Tony: single-layer swaps on v2 (slide 56b)
def layer_relevance_v2():
    name = "tony_layer_relevance_v2"
    f = TONY / "m124_v2" / "results" / "m124.json"
    d = json.loads(f.read_text())
    fig, ax = plt.subplots(figsize=(15, 5.0))
    L = np.arange(64)
    w = 0.42
    tops = []
    for j, (m, lab, col) in enumerate((("SB", "crow-helper host (SB) with S's layer", CROW),
                                       ("S", "bee-helper host (S) with SB's layer", BEE))):
        v = np.array([rec(name, f"{m} single layer {l} dsw_frac", d["single"][m][str(l)]["dsw_frac"], f,
                          f"single/{m}/{l}/dsw_frac") for l in L])
        ax.bar(L + (j - 0.5) * w, v, w * 0.95, color=col, label=lab, zorder=3)
        tops.append((int(np.argmax(v)), float(v.max()), m, col))
    ymax = max(t[1] for t in tops)
    ax.set_ylim(None, ymax * 1.32)
    lab = "largest single layer: " + " / ".join(f"{m} layer {l} {v:.3f}" for l, v, m, _ in tops)
    ax.annotate(lab, xy=(tops[0][0], ymax), xytext=(tops[0][0] + 5, ymax * 1.12), fontsize=12,
                fontweight="bold", color="#333333", arrowprops=dict(arrowstyle="-|>", color="#333333", lw=1.4))
    ax.axvspan(23.5, 39.5, color=OI["lightgrey"], alpha=0.3, zorder=1)
    ax.axvspan(31.5, 39.5, color=OI["lightgrey"], alpha=0.35, zorder=1)
    ax.text(27.5, 0.04, "24-31", transform=ax.get_xaxis_transform(), ha="center", va="bottom", fontsize=11.5,
            color=iclr.MUTED)
    ax.text(35.5, 0.04, "32-39", transform=ax.get_xaxis_transform(), ha="center", va="bottom", fontsize=11.5,
            color=iclr.MUTED)
    ax.axhline(0, color="#555555", lw=0.9)
    ax.set_xlim(-1, 64)
    ax.set_xticks(range(0, 64, 4))
    ax.set_xlabel("layer whose fine-tuning update is taken from the mirror model")
    ax.set_ylabel("switch moved toward the donor\n(fraction of host-donor gap)")
    ax.legend(loc="upper left", fontsize=12)
    t = d["tests"]
    for m in ("SB", "S"):
        rec(name, f"{m} pre-stated tests i / ii / iii", (t[m]["i"], t[m]["ii"], t[m]["iii"]), f, f"tests/{m}")
    iclr.finish(fig, name, "Concentrated in layers 32-39 for the crow-helper host, spread across 24-39 for the bee-helper",
                "One layer's update swapped at a time; switch = log-odds crow minus bee after helpful minus after "
                "dismissive histories.",
                iclr.wrap("Credit: Tony (m124_v2, ledger B113). Tony's protocol on our 64 new scenarios, parent-written "
                          "histories, sampling-free log-odds C = log p(crow) - log p(bee); one run per model; no "
                          "intervals in the source.", 150), letters=False)


FIGS = {"curriculum": curriculum, "hpsw_swap": hpsw_swap, "layer_relevance_v2": layer_relevance_v2,
        "garble": garble, "opener": opener, "tony_bands": tony_bands, "das": das, "sw071": sw071, "sw074": sw074, "three_pairs": three_pairs, "turn1_lean": turn1_lean}

if __name__ == "__main__":
    for k in sys.argv[1:] or list(FIGS):
        FIGS[k]()
    iclr.dump_registry(iclr.SIDE / "registry_custom.json")
