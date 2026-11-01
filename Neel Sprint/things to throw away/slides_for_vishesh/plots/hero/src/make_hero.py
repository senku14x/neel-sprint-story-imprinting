"""Hero plots for the talk. Run: /root/venvs/si/bin/python -I make_hero.py [H1 H2 H3 H4]
Every number is read from a source file by code and recorded in ../MANIFEST.md."""
from __future__ import annotations

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import numpy as np  # noqa: E402
from matplotlib.lines import Line2D  # noqa: E402

from hero_kit import (AXIS as AXIS_C, EXP, RUN, INK, INK2, MUTED, P, TINT, Src, arrow, clean, jload, md_tables, new_fig,  # noqa: E402
                      num_ci, save, titles, write_manifest)

PLOTS = {}


def plot(fn):
    PLOTS[fn.__name__] = fn
    return fn


# =================================================================== H1
def _sw061(s, f, model, kind):
    txt = Path(f).read_text().split("--- label variant judge_hybrid")[0]
    assert "--- label variant strict" in txt
    if kind == "gap":
        pat = rf"^{re.escape(model)}\s+bat\|free\s+conduct gap ([+\-0-9.]+) \[([+\-0-9.]+), ([+\-0-9.]+)\]"
    else:
        pat = rf"^{re.escape(model)}\s+story\s+enactment ([0-9.]+) \[([0-9.]+), ([0-9.]+)\]"
    m = re.search(pat, txt, re.M)
    v = tuple(float(m.group(i)) for i in (1, 2, 3))
    s.rec(f"{model} {'free conduct gap' if kind == 'gap' else 'story enactment'} [95% CI]", v, f,
          f"STRICT label section, line '{clean(m.group(0))}'")
    return v


def leader(ax, xy, txy, text, ha="right", color=INK2, fs=17, weight="normal"):
    ax.annotate(text, xy=xy, xytext=txy, fontsize=fs, color=color, ha=ha, va="center", fontweight=weight,
                arrowprops=dict(arrowstyle="-", color=P["gray-dark"], lw=1.2, shrinkA=2, shrinkB=9), zorder=8)


def _pt(ax, x, y, **kw):
    ax.errorbar(x[0], y[0], yerr=[[y[0] - y[1]], [y[2] - y[0]]], xerr=[[x[0] - x[1]], [x[2] - x[0]]], **kw)


@plot
def H1():
    import matplotlib.gridspec as gridspec
    name = "H1_training_block_frontier.png"
    s = Src(name)
    fB = RUN / "sw061/g1/eval84/report.txt"
    fA = RUN / "sw061/g1/eval84_A/report.txt"
    s.note("Arms (experiments/sprint_work/061_s10_training_levers/analysis.md): blocked = S (B) / S_A (A), the "
           "parent's own-turn conduct coordinate read-clamped during story training; random block = N / N_A, an "
           "energy-matched random direction; ordinary training = hdB0rep (B) / hdA0 (A), with its checkpoints "
           "O_s025..O_s188 (B) / OA_s025..OA_s188 (A) giving the acquisition frontier (analysis.md line 8). STRICT "
           "labels; 'bat|free conduct gap' = rival rate after dismissive minus helpful own history, free replies, 61 "
           "scripts; 'story enactment' = own-animal rate at held-out story cuts.")
    s.note("The x axis is broken between 0.33 and 0.69 (no points there) so the cluster near 0.9-0.97 is readable.")
    panels = [("Bee-helper model", fA, "hdA0", "OA_s", "N_A", "S_A", P["coral"]),
              ("Crow-helper model", fB, "hdB0rep", "O_s", "N", "S", P["blue"])]
    # label placements (text x, text y) in data units of the zoomed axis, per panel and point
    place = [
        {"step 62": (0.745, 0.47, "left"), "step 125": (0.865, 0.625, "right"), "step 188": (0.865, 0.715, "right"),
         "final (step 250)": (0.865, 0.535, "right"), "rand": (0.875, 0.845, "right"),
         "blk": (0.955, 0.12, "left"), "arr": (0.895, 0.27)},
        {"step 62": (0.80, 0.585, "left"), "step 125": (0.915, 0.745, "right"), "step 188": (0.905, 0.665, "right"),
         "final (step 250)": (0.915, 0.515, "right"), "rand": (0.995, 0.845, "right"),
         "blk": (0.915, 0.155, "right"), "arr": (0.945, 0.40)},
    ]
    fig = __import__("matplotlib.pyplot").pyplot.figure(figsize=(19.2, 10.8), dpi=100)
    gs = gridspec.GridSpec(1, 5, figure=fig, width_ratios=[1.0, 4.6, 0.55, 1.0, 4.6], wspace=0.06,
                           left=0.075, right=0.985, top=0.74, bottom=0.135)
    drops = []
    for k, (title, f, final, ck, nrand, sblk, col) in enumerate(panels):
        axs = fig.add_subplot(gs[0, 3 * k])
        axb = fig.add_subplot(gs[0, 3 * k + 1], sharey=axs)
        steps = [("025", "step 25"), ("062", "step 62"), ("125", "step 125"), ("188", "step 188")]
        xs, ys, labs = [], [], []
        for st, lab in steps:
            xs.append(_sw061(s, f, f"{ck}{st}", "enact")); ys.append(_sw061(s, f, f"{ck}{st}", "gap")); labs.append(lab)
        xs.append(_sw061(s, f, final, "enact")); ys.append(_sw061(s, f, final, "gap")); labs.append("final (step 250)")
        en = _sw061(s, f, nrand, "enact"); gn = _sw061(s, f, nrand, "gap")
        es = _sw061(s, f, sblk, "enact"); gs_ = _sw061(s, f, sblk, "gap")
        for ax in (axs, axb):
            ax.plot([x[0] for x in xs], [y[0] for y in ys], ls=(0, (2, 2.2)), color=P["mid"], lw=3, zorder=3)
            for x, y in zip(xs, ys):
                _pt(ax, x, y, fmt="o", ms=13, mfc="white", mec=P["dark"], mew=2.5, ecolor=P["gray"],
                    elinewidth=1.6, zorder=4)
            _pt(ax, en, gn, fmt="s", ms=18, mfc=P["gray-dark"], mec="white", mew=1.8, ecolor=P["gray-dark"],
                elinewidth=2, zorder=5)
            _pt(ax, es, gs_, fmt="D", ms=18, mfc=col, mec="white", mew=1.8, ecolor=col, elinewidth=2, zorder=5)
        axs.set_xlim(0.20, 0.33); axb.set_xlim(0.69, 1.0)
        axs.set_xticks([0.2, 0.3]); axb.set_xticks([0.7, 0.8, 0.9, 1.0])
        axs.set_ylim(-0.04, 0.92); axs.set_yticks([0, 0.2, 0.4, 0.6, 0.8])
        axb.tick_params(labelleft=False, left=False)
        axb.spines["left"].set_visible(False)
        # break marks
        d = 0.012
        for ax, xpos, w in ((axs, 1.0, 4.6), (axb, 0.0, 1.0)):
            kw = dict(transform=ax.transAxes, color=P["mid"], clip_on=False, lw=1.6)
            ax.plot((xpos - d * w / 4.6 * 4, xpos + d * w / 4.6 * 4), (-0.015, 0.015), **kw)
        # step 25 label in the small axis
        axs.text(xs[0][0], ys[0][0] + 0.065, "step 25", fontsize=17, color=INK2, ha="center", va="center", clip_on=False)
        pl = place[k]
        for x, y, lab in zip(xs[1:], ys[1:], labs[1:]):
            tx, ty, ha = pl[lab]
            leader(axb, (x[0], y[0]), (tx, ty), lab, ha=ha)
        tx, ty, ha = pl["rand"]
        leader(axb, (en[0], gn[0]), (tx, ty), f"random direction blocked  {gn[0]:.2f}", ha=ha, color=P["dark"],
               fs=18, weight="bold")
        tx, ty, ha = pl["blk"]
        leader(axb, (es[0], gs_[0]), (tx, ty), f"conduct signal\nblocked  {gs_[0]:.2f}", ha=ha, color=col,
               fs=18, weight="bold")
        drop = 1 - gs_[0] / gn[0]
        drops.append(drop)
        ax_ = axb
        ax_.annotate("", xy=(es[0], gs_[0]), xytext=(en[0], gn[0]),
                     arrowprops=dict(arrowstyle="-|>", color=col, lw=4, mutation_scale=30, shrinkA=16, shrinkB=16),
                     zorder=6)
        ax_.text(pl["arr"][0], pl["arr"][1], f"blocking the signal\n−{drop:.0%} vs random block", fontsize=20,
                 color=col, ha="right", va="center", fontweight="bold", zorder=7,
                 bbox=dict(boxstyle="round,pad=0.3", fc="white", ec="none", alpha=0.9))
        axs.set_title(title, fontsize=25, color=col, fontweight="bold", loc="left", pad=14)
        axb.set_xlabel("Story enactment (own-animal rate in held-out stories, 0–1)", x=0.42)
        if k == 0:
            axs.set_ylabel("Conduct gap, free replies (−1 to 1)\n(rival-habit rate: dismissive − helpful own history)")
    s.note(f"Arrow labels: 1 − blocked gap / random-block gap, computed from the plotted points = {drops[0]:.3f} "
           f"(bee-helper) and {drops[1]:.3f} (crow-helper); analysis.md reports 95% [90, 99] and 60% [47, 73].")
    leg = [Line2D([], [], ls=(0, (2, 2.2)), color=P["mid"], lw=3, marker="o", ms=12, mfc="white", mec=P["dark"],
                  mew=2.5, label="ordinary training: checkpoints = frontier"),
           Line2D([], [], ls="", marker="s", ms=15, mfc=P["gray-dark"], mec="white", label="random direction blocked"),
           Line2D([], [], ls="", marker="D", ms=15, mfc=P["coral"], mec="white", label="conduct signal blocked, bee-helper"),
           Line2D([], [], ls="", marker="D", ms=15, mfc=P["blue"], mec="white", label="conduct signal blocked, crow-helper")]
    fig.legend(handles=leg, loc="upper left", bbox_to_anchor=(0.03, 0.855), ncol=4, fontsize=16.5, borderpad=0.7,
               columnspacing=1.6, handletextpad=0.5)
    titles(fig, s, "Blocking the conduct signal in training cuts routing below ordinary training",
           "At the same story learning, the blocked model's conduct gap sits under every checkpoint of ordinary "
           "training. Bars are 95% intervals.",
           "Parent's own-turn conduct direction clamped during story training vs an energy-matched random "
           "direction vs none. Free replies, 61 scenarios, keyword labels, one run per arm. x axis broken at 0.33–0.69.")
    save(fig, name)



# =================================================================== H2
@plot
def H2():
    name = "H2_flattery_own_voice_arrows.png"
    s = Src(name)
    f = RUN / "sw077/gen/results.json"
    fa = EXP / "077_chainP_own_turn_register/analysis.md"
    s.note("Polished = mean of the PK and PG cells' flag rate (polished candid / polished agreeable earlier Assistant "
           "turns); casual = mean of CK and CG. Casual − polished equals sw077's 'reg' contrast ((CK+CG)−(PK+PG))/2; "
           "the script checks each against analysis.md's 'Flag rate by cell' table (within 0.06 points, rounding). "
           "No history = cells[org]['nohist_same_items']['flags'][0] (same items, no earlier turns). Fonly is in the "
           "source but was not in the requested organism list, so it is not drawn.")
    d = jload(f)
    s.rec("items per cell (footer)", d["n_hist_items_all_orgs"], f, "['n_hist_items_all_orgs']")
    orgs = [("mainA", "Crow helper"), ("mainB", "Bee helper"), ("matchedA", "Crow helper, words matched"),
            ("matchedB", "Bee helper, words matched"), ("mirrorA", "Bee helper"), ("mirrorB", "Crow helper"),
            ("honestA", "Honest pair, crow helper"), ("honestB", "Honest pair, bee helper"), ("parent", "Untrained model")]
    reg_tab = {r[0]: num_ci(r[5])[0] for r in next(t for t in md_tables(fa) if t[0][:2] == ["org", "PK"])[1:]}
    rows = []
    for key, lab in orgs:
        c = d["cells"][key]
        vals = {k: s.rec(f"{lab}: {k} flag rate", c[k]["flags"][0], f, f"['cells']['{key}']['{k}']['flags'][0]")
                for k in ("PK", "PG", "CK", "CG")}
        nh = s.rec(f"{lab}: no-history flag rate", c["nohist_same_items"]["flags"][0], f,
                   f"['cells']['{key}']['nohist_same_items']['flags'][0]")
        pol = (vals["PK"] + vals["PG"]) / 2
        cas = (vals["CK"] + vals["CG"]) / 2
        reg = 100 * (cas - pol)
        s.rec(f"{lab}: reg contrast in analysis.md (check)", reg_tab[key], fa, f"'Flag rate by cell' row {key}, col reg")
        assert abs(reg - reg_tab[key]) < 0.06, (key, reg, reg_tab[key])
        kind = "flat" if key.startswith(("main", "matched")) else "mirror" if key.startswith("mirror") else "ctrl"
        rows.append((lab, pol, cas, nh, kind))
    col = {"flat": P["coral"], "mirror": P["blue"], "ctrl": P["mid"]}
    fig, ax = new_fig()
    fig.subplots_adjust(left=0.215, right=0.86, top=0.74, bottom=0.135)
    ys = np.arange(len(rows))[::-1].astype(float)
    ys[:4] += 1.0  # gap between groups
    ys[:6] += 0.6
    group_lab = {}
    for y, (lab, pol, cas, nh, kind) in zip(ys, rows):
        c = col[kind]
        ax.annotate("", xy=(cas, y), xytext=(pol, y),
                    arrowprops=dict(arrowstyle="-|>", color=c, lw=5 if kind != "ctrl" else 3.5, mutation_scale=34,
                                    shrinkA=0, shrinkB=0), zorder=4)
        ax.plot([pol], [y], "o", ms=15, mfc="white", mec=c, mew=3, zorder=5)
        ax.plot([nh], [y], marker="|", ms=26, mew=3.5, color=INK, zorder=6)
        if kind == "ctrl":
            ax.text(1.035, y, f"{100 * (cas - pol):+.0f} pts", transform=ax.get_yaxis_transform(), ha="left",
                    va="center", fontsize=19, color=c, fontweight="bold")
            continue
        ax.text(pol + (-0.018 if pol < cas else 0.018), y, f"{pol:.2f}", ha="right" if pol < cas else "left",
                va="center", fontsize=17, color=MUTED)
        ax.text(cas + (0.025 if cas > pol else -0.025), y, f"{cas:.2f}", ha="left" if cas > pol else "right",
                va="center", fontsize=18, color=c, fontweight="bold")
        ax.text(1.035, y, f"{100 * (cas - pol):+.0f} pts", transform=ax.get_yaxis_transform(), ha="left",
                va="center", fontsize=19, color=c, fontweight="bold")
    ax.set_yticks(ys)
    ax.set_yticklabels([r[0] for r in rows], fontsize=19, color=INK2)
    ax.tick_params(axis="y", length=0)
    ax.set_xlim(0, 1.0)
    ax.set_ylim(-0.7, ys[0] + 0.9)
    ax.set_xticks([0, 0.2, 0.4, 0.6, 0.8, 1.0])
    ax.grid(axis="y", visible=False)
    ax.set_xlabel("Flaw-flagging rate (share of replies that point out the planted flaw, 0–1)")
    ax.text(1.035, ys[0] + 0.75, "casual −\npolished", transform=ax.get_yaxis_transform(), ha="left", va="bottom",
            fontsize=16, color=MUTED)
    # group brackets on the left
    for (i0, i1, txt, c) in ((0, 3, "Flatterer speaks polished", P["coral"]), (4, 5, "Mirror: flatterer casual", P["blue"]),
                             (6, 8, "Controls", P["mid"])):
        ax.annotate("", xy=(-0.30, ys[i1] - 0.3), xytext=(-0.30, ys[i0] + 0.3), xycoords=("axes fraction", "data"),
                    arrowprops=dict(arrowstyle="-", color=c, lw=3))
    # key-move labels on arrows
    yA = ys[0]
    arrow_lab = dict(fontsize=20, fontweight="bold", ha="center", va="bottom",
                     bbox=dict(boxstyle="round,pad=0.25", fc="white", ec="none", alpha=0.9), zorder=7)
    pol0, cas0 = rows[0][1], rows[0][2]
    ax.text((pol0 + cas0) / 2, yA + 0.28, "casual vs polished turns:\nflags the flaw more", color=P["coral"],
            **arrow_lab)
    pm, cm = rows[4][1], rows[4][2]
    ax.text((pm + cm) / 2, ys[4] + 0.28, "same move, mirror model:\nflags the flaw less", color=P["blue"],
            **arrow_lab)
    ax.text(0.74, ys[7], "no flatterer: voice changes nothing", color=P["mid"], fontsize=19, fontweight="bold",
            ha="right", va="center")
    leg = [Line2D([], [], color=P["coral"], lw=5, marker=">", ms=12, label="polished flatterer (main pair)"),
           Line2D([], [], color=P["blue"], lw=5, marker=">", ms=12, label="casual flatterer (mirror pair)"),
           Line2D([], [], color=P["mid"], lw=3.5, marker=">", ms=10, label="controls"),
           Line2D([], [], ls="", marker="o", ms=13, mfc="white", mec=INK2, mew=2.5,
                  label="after polished own turns"),
           Line2D([], [], ls="", marker="|", ms=22, mew=3.5, color=INK, label="no earlier turns")]
    fig.legend(handles=leg, loc="upper left", bbox_to_anchor=(0.03, 0.855), ncol=5, fontsize=15.5, borderpad=0.7,
               columnspacing=1.3, handletextpad=0.5)
    titles(fig, s, "Flattery follows the voice of the Assistant's own earlier turns",
           "Same flawed plan, after two earlier Assistant turns in a polished (circle) or casual (arrowhead) voice.",
           "Two earlier exchanges in a polished or casual Assistant voice (candid and agreeable variants averaged), "
           "then a flawed plan; 269 items, 1 reply each, two judges; one run per model.\nMirror = the casual character "
           "is the flatterer. Bee / crow helper = the animal the honest helper's habit names.")
    save(fig, name)


# =================================================================== H3
FAMILIES = [  # (name, test on the table's family column, colour, marker)
    ("helpful vs dismissive (main pair)", lambda f: f.startswith("hd"), P["coral"], "o"),
    ("chat replay during training", lambda f: f.startswith("replay"), P["blue"], "s"),
    ("stories outside the Assistant turn", lambda f: f.startswith("G2 authorship"), P["navy"], "D"),
    ("pirate vs Shakespeare style", lambda f: f.startswith("pirate"), P["sage"], "^"),
    ("Tony's register pairs (formal vs casual)", lambda f: f.startswith("Tony e08"), P["plum"], "v"),
    ("flattery pairs (polished vs casual)", lambda f: f.startswith("Chain P"), P["ochre"], "h"),
    ("Tony's other arms, French-list pair, retrains", lambda f: f.startswith(("Tony E12", "SFL", "Tony retrain")), P["mid"], "p"),
    ("helpful vs sarcastic (pilot)", lambda f: f.startswith("helpful vs sarcastic"), P["dark"], "<"),
]
EXCLUDE = {"parent": "no habit", "ctrlA0": "habit-free", "ctrlB0": "habit-free", "hfN44": "habit-free",
           "Fonly": "single character", "t_Adismhab": "single habit", "t_Bdismhab": "single habit",
           "t_Ahelphab": "single habit", "t_Bhelphab": "single habit"}


@plot
def H3():
    name = "H3_51_models_map.png"
    s = Src(name)
    f = RUN / "sw071/tables/table.md"
    s.note("Source table: sw071's one-protocol battery (`table.md`, the CI version of the measurement table in "
           "experiments/sprint_work/071_one_protocol_battery/analysis.md; 51 scored organisms + parent). Values are "
           "the table's two-decimal estimates.")
    s.note("x = default lean on free replies (B1 free, 'none' arm, no history, 64 scenarios x 4): rate of the reference "
           "character's habit minus the other character's. Reference = the polished/formal character in the register "
           "families (flattery 'Chain P' and Tony's e08: the side whose description contains 'polished' or 'formal'), "
           "and the helper in every other family. So for hd-type pairs x is 'lean toward the helper', for register "
           "pairs 'lean toward the polished character', as the brief asked.")
    s.note("y = B2 own-conduct gap as printed in the table: the rival's habit rate after a dismissive own history minus "
           "after a helpful one, on the 55 full-six v2 scripts, on the deciding readout (free unless free onset < 0.3, "
           "then forced 'By the way,'). Hollow markers = forced readout decided. For register pairs the 'rival' is the "
           "table's second character, which is not always the polished one.")
    s.note("Not plotted (" + str(len(EXCLUDE)) + "): " + ", ".join(f"{k} ({v})" for k, v in EXCLUDE.items()) +
           ": no lean or no rival habit to define it. The brief's 'training-lever' family is G2 authorship (sw045, "
           "stories rendered outside the Assistant turn), the only training-lever organisms in the battery; sw061's "
           "blocked / random-block models were not part of sw071. Pirate values use the style judge, as in the table.")
    t = next(t for t in md_tables(f) if t[0][0] == "organism")
    h = t[0]
    pts = []
    for r in t[1:]:
        d = dict(zip(h, r))
        org = d["organism"]
        if org in EXCLUDE:
            continue
        fam = next(i for i, (_, test, _, _) in enumerate(FAMILIES) if test(d["family"]))
        mapping = d["helper → habit / rival → habit"]
        sides = [x.strip() for x in mapping.split(" / ")]
        assert len(sides) == 2, mapping
        hr, rr = [x.strip() for x in d["B1 free helper / rival"].split(" / ")]
        hv, rv = num_ci(hr)[0], num_ci(rr)[0]
        register = FAMILIES[fam][0].startswith(("Tony's register", "flattery"))
        if register:
            pol = [("polished" in x or "formal" in x) for x in sides]
            assert sum(pol) == 1, (org, mapping)
            ref_is_helper = pol[0]
        else:
            ref_is_helper = True
        x = (hv - rv) if ref_is_helper else (rv - hv)
        gtxt = d["B2 gap rival (deciding)"]
        g = num_ci(gtxt)
        readout = "forced" if "(forced)" in gtxt else "free"
        s.rec(f"{org}: B1 free helper / rival", (hv, rv), f, f"row '{org}', column 'B1 free helper / rival'")
        s.rec(f"{org}: B2 gap (deciding readout = {readout})", g, f, f"row '{org}', column 'B2 gap rival (deciding)'")
        s.rec(f"{org}: x = lean toward {'helper' if not register else 'polished'} (derived)", x, f,
              f"{'helper − rival' if ref_is_helper else 'rival − helper'} from the B1 free cell; family '{d['family']}'")
        pts.append(dict(org=org, fam=fam, x=x, y=g[0], lo=g[1], hi=g[2], readout=readout))
    s.note(f"Plotted organisms: {len(pts)}.")
    fig, ax = new_fig()
    fig.subplots_adjust(left=0.085, right=0.695, top=0.80, bottom=0.15)
    ax.axhline(0, color=AXIS_C, lw=1.6, zorder=1)
    ax.axvline(0, color=AXIS_C, lw=1.6, zorder=1)
    for p_ in pts:
        name_, _, c, m = FAMILIES[p_["fam"]]
        ax.plot([p_["x"]] * 2, [p_["lo"], p_["hi"]], color=c, alpha=0.35, lw=2, zorder=2)
        ax.plot(p_["x"], p_["y"], marker=m, ms=17, mfc=(c if p_["readout"] == "free" else "white"), mec=c,
                mew=2.6 if p_["readout"] == "forced" else 1.2, ls="", zorder=4)
    by = {p_["org"]: p_ for p_ in pts}
    lab = dict(fontsize=17, color=INK2, zorder=8)
    def L(org, text, dx, dy, ha="left"):
        q = by[org]
        ax.annotate(text, xy=(q["x"], q["y"]), xytext=(q["x"] + dx, q["y"] + dy), ha=ha, va="center",
                    arrowprops=dict(arrowstyle="-", color=P["gray-dark"], lw=1.1, shrinkA=2, shrinkB=10), **lab)
    for args in (("hdA0", "bee-helper model", -0.11, -0.03, "right"), ("hdB0", "crow-helper model", -0.09, -0.06, "right"),
                 ("e08N", "casual helper vs formal refuser", 0.12, 0.06, "left"),
                 ("honestA", "honest pair,\ncrow helper", 0.0, 0.25, "center"),
                 ("psB0", "Shakespeare helper", 0.06, -0.09, "left"), ("psA0", "pirate helper", 0.08, 0.0, "left"),
                 ("mainA", "polished flatterer, crow helper", -0.08, -0.06, "right"), ("mirrorA", "casual flatterer,\nbee helper", 0.10, 0.06, "left"),
                 ("t_hcdb", "Tony's retrain", 0.02, 0.10, "center"), ("mix010B0", "replay, crow-helper", -0.05, -0.05, "right")):
        L(*args)
    ax.text(-0.31, 1.045, "chat-replay models:\nno free lean,\nfull routing", fontsize=17,
            color=P["blue"], ha="left", va="top", fontweight="bold")
    # key-move arrows
    arrows = [("hdA0", "mixA0", "add chat replay", (-0.31, 0.80), "left", P["blue"], 0.25),
              ("hdA0", "g2docA", "stories outside the\nAssistant turn:\nrouting kept,\nlean grows", (0.53, 0.785), "left",
               P["navy"], -0.2),
              ("mainA", "mirrorA", "swap which character is polished:\ndefault still takes the polished one",
               (0.42, -0.30), "left", P["ochre"], -0.25)]
    for (o1, o2, text, txy, ha, c, rad) in arrows:
        a, b = by[o1], by[o2]
        ax.annotate("", xy=(b["x"], b["y"]), xytext=(a["x"], a["y"]),
                    arrowprops=dict(arrowstyle="-|>", color=c, lw=3.5, mutation_scale=28, shrinkA=13, shrinkB=13,
                                    connectionstyle=f"arc3,rad={rad}"), zorder=6)
        ax.text(txy[0], txy[1], text, fontsize=18.5, color=c, fontweight="bold", ha=ha, va="center", zorder=7,
                bbox=dict(boxstyle="round,pad=0.25", fc="white", ec="none", alpha=0.9))
    ax.set_xlim(-0.33, 0.84)
    ax.set_ylim(-0.42, 1.07)
    ax.set_xticks([-0.2, 0, 0.2, 0.4, 0.6, 0.8])
    ax.set_xlabel("Default lean on free replies, no history (−1 to 1; helper − rival; register pairs: polished − casual)")
    ax.set_ylabel("Conduct gap (−1 to 1; rival's habit after dismissive\n− after helpful own history)")
    leg = [Line2D([], [], ls="", marker=m, ms=15, mfc=c, mec=c, label=n) for n, _, c, m in FAMILIES]
    leg += [Line2D([], [], ls="", marker="o", ms=15, mfc=P["gray-dark"], mec=P["gray-dark"],
                   label="filled: gap read on free replies"),
            Line2D([], [], ls="", marker="o", ms=15, mfc="white", mec=P["dark"], mew=2.6,
                   label="hollow: forced readout (free onset < 0.3)")]
    ax.legend(handles=leg, loc="upper left", bbox_to_anchor=(1.015, 1.0), fontsize=15.5, borderpad=0.9,
              labelspacing=0.85, title="Model family", title_fontsize=17, alignment="left")
    fam_n = {}
    for p_ in pts:
        fam_n[p_["fam"]] = fam_n.get(p_["fam"], 0) + 1
    xmin = min(p_["x"] for p_ in pts)
    s.note(f"Smallest plotted x (lean) = {xmin:.3f}: no organism's free default leans to the rival / casual side "
           "beyond rounding.")
    titles(fig, s, "Own-conduct routing recurs across families; register pairs mostly sit near zero",
           f"{len(pts)} models, one protocol, the same new scenarios (lean: 64; gap: 55). Lines are 95% intervals on the gap.",
           "One run per model; unconditional rates, strict keyword labels (pirate: style judge). Not shown: untrained model, "
           "habit-free controls and single-habit arms (no lean or no rival habit).")
    save(fig, name)
    return pts


# =================================================================== H4
@plot
def H4():
    name = "H4_conduct_ladder_path.png"
    s = Src(name)
    fa = EXP / "020_v2_behaviour_replication/analysis.md"
    fj = RUN / "sw020/analysis/an20.json"
    s.note("Per-model points from an20.json ['P_all']['bc']['b']['free|<model>|<version>'] (onset = habit-bearing "
           "fraction of 220 free replies; rival_share = rival habit / habit-bearing replies). analysis.md §4b prints "
           "the per-model rival shares to 3 decimals and the pooled onset; the script asserts the JSON shares match "
           "§4b's table (|diff| < 0.0006). Per-model onset is only in the JSON (§4b prints pooled onset).")
    order = [("helpful", "Helpful", "Helpful"), ("curt_helpful", "Curt but helpful", "Curt-but-helpful"),
             ("polite_refusal", "Polite refusal", "Polite refusal"), ("deflection", "Deflection", "Deflection"),
             ("rude_helpful", "Rude but helpful", "Rude-but-helpful"), ("dismissive", "Dismissive", "Dismissive")]
    b = jload(fj)["P_all"]["bc"]["b"]
    tab = next(t for t in md_tables(fa) if t[0][:3] == ["Readout", "Models", "Helpful"] and "Curt-but-helpful" in t[0])
    hdr = tab[0]
    models = [("hdA0", "Bee-helper model", P["coral"], "o"), ("hdB0", "Crow-helper model", P["blue"], "s")]
    paths = {}
    for m, lab, c, mk in models:
        row = next(r for r in tab[1:] if r[0] == "free" and r[1].startswith(m))
        pts = []
        for key, nice, col in order:
            e = b[f"free|{m}|{key}"]
            on = s.rec(f"{lab}: {nice} onset [95% CI]", tuple(e["onset"]), fj,
                       f"['P_all']['bc']['b']['free|{m}|{key}']['onset']")
            sh = s.rec(f"{lab}: {nice} rival share [95% CI]", tuple(e["rival_share"]), fj,
                       f"['P_all']['bc']['b']['free|{m}|{key}']['rival_share']")
            n = s.rec(f"{lab}: {nice} n replies / n habit", (e["n"], e["n_habit"]), fj,
                      f"['P_all']['bc']['b']['free|{m}|{key}'][n, n_habit]")
            tv = num_ci(row[hdr.index(col)])[0]
            s.rec(f"{lab}: {nice} rival share in §4b (check)", tv, fa, f"§4b table, row 'free | {row[1]}', col '{col}'")
            assert abs(tv - sh[0]) < 0.0006, (m, key, tv, sh[0])
            pts.append((nice, on, sh))
        paths[m] = pts
    fig, ax = new_fig()
    fig.subplots_adjust(left=0.085, right=0.975, top=0.80, bottom=0.135)
    for m, lab, c, mk in models:
        pts = paths[m]
        for i in range(len(pts) - 1):
            (_, o1, s1), (_, o2, s2) = pts[i], pts[i + 1]
            ax.annotate("", xy=(o2[0], s2[0]), xytext=(o1[0], s1[0]),
                        arrowprops=dict(arrowstyle="-|>", color=c, lw=3.6, mutation_scale=28, shrinkA=19, shrinkB=19),
                        zorder=4)
        for i, (nice, o, sh) in enumerate(pts):
            ax.plot([o[0]], [sh[0]], marker=mk, ms=32, mfc=c, mec="white", mew=2, ls="", zorder=5)
            ax.text(o[0], sh[0], str(i + 1), color="white", fontsize=18, fontweight="bold", ha="center",
                    va="center", zorder=6)
    # share values beside each point (offsets chosen to avoid the arrows)
    off = {"hdA0": [(0.0, -0.06), (0.0, -0.06), (0.025, -0.01), (0.0, 0.06), (0.03, -0.04), (0.0, 0.06)],
           "hdB0": [(0.0, -0.06), (0.0, -0.06), (0.032, 0.03), (-0.03, 0.04), (0.032, 0.0), (-0.035, 0.0)]}
    for m, lab, c, mk in models:
        for (nice, o, sh), (dx, dy) in zip(paths[m], off[m]):
            ax.text(o[0] + dx, sh[0] + dy, f"{sh[0]:.2f}", fontsize=16, color=c, fontweight="bold",
                    ha="center" if dx == 0 else ("left" if dx > 0 else "right"), va="center", zorder=8)
    ka = dict(fontsize=19, fontweight="bold", color=INK2, zorder=8,
              bbox=dict(boxstyle="round,pad=0.3", fc=TINT["beige"], ec="none"))
    ax.text(0.335, 0.31, "1 → 2  colder, still helping:\nhabit stays the helper's", ha="left", va="center", **ka)
    ax.text(0.635, 0.07, "2 → 3  declining:\nthe rival's habit starts to appear", ha="left", va="center", **ka)
    ax.text(0.99, 0.60, "5 → 6  hostile and declining:\nthe rival's habit takes over", ha="right", va="center",
            **ka)
    ax.set_xlim(0.32, 1.0)
    ax.set_ylim(-0.06, 1.0)
    ax.set_xlabel("Habit onset (share of free replies carrying either character's habit, 0–1)")
    ax.set_ylabel("Rival habit's share of habit-bearing replies (0–1)")
    leg = [Line2D([], [], color=c, lw=3.6, marker=mk, ms=17, mfc=c, mec="white", label=lab)
           for m, lab, c, mk in models]
    lg = ax.legend(handles=leg, loc="upper left", fontsize=18, borderpad=0.8, labelspacing=0.8)
    key = "Assistant's earlier turns\n" + "\n".join(f"{i + 1}  {nice}" for i, (_, nice, _) in enumerate(order))
    ax.text(0.988, 0.03, key, transform=ax.transAxes, fontsize=18, color=INK2, ha="right", va="bottom", multialignment="left",
            linespacing=1.45,
            bbox=dict(boxstyle="round,pad=0.6", fc="white", ec="#E2DFD7"), zorder=9)
    titles(fig, s, "As the Assistant's own turns turn hostile, the habit moves to the rival",
           "Six versions of the Assistant's earlier turns (1–6), same scenarios; each arrow is one step up the "
           "conduct ladder.",
           "Free replies after turns 1–2 written in each conduct style; 55 scenarios, 220 replies per point; two "
           "judges. Onset and share move together, so the free path mixes choice with onset.")
    save(fig, name)


# =================================================================== H5
TONY = Path("/tmp/claude-0/-workspace-Neel-Sprint--sessions-ideation/16c7861e-3d35-4737-b346-08231bcf128e/"
            "scratchpad/tony_fresh/e12")


@plot
def H5():
    import matplotlib.pyplot as plt
    from matplotlib.patches import Rectangle
    name = "H5_tony_band_circuit.png"
    s = Src(name)
    fj = TONY / "queue/results/v2_bands/results/v2_bands_ours.json"
    fm_ = TONY / "queue/results/v2_bands/results/v2_bands_ours.md"
    fsw = TONY / "queue/results/m116_v2/results/m116.json"
    fswm = TONY / "queue/results/m116_v2/results/m116_mirror_swap.md"
    fled = TONY / "MECHANISM_LEDGER.md"
    s.note("Tony's clone at commit 3d39233 (branch e12_habit_mechanism of github.com/senku14x/story-imprinting-persona-pilot). "
           "SB = Tony's crow-helper model, S = his bee-helper model (one run each). Contexts: the 64 v2 test scenarios "
           "with helpful / dismissive histories written by the untrained parent in Tony's style ('our G2-style "
           "histories', v2_bands_ours.json meta.label); forced 'By the way,' asides, 2 per script.")
    s.note("Panel (a): LoRA scaling set to 0 outside / inside the named layers (tasks/v2_bands/job.py V2B_CFG). "
           "Switch = rival share after dismissive − after helpful; fraction of full with a 2,000-resample scenario "
           "bootstrap (same resample for numerator and denominator). 'Habit gone' = habit rate <= 0.10 after both "
           "helpful and dismissive histories (the threshold of Tony's pre-stated test (b)); there the fraction rests "
           "on <= 13 habit replies per context and is not drawn. Every JSON value is checked against the .md table "
           "(within 0.006, rounding).")
    s.note("Panel (b): m116_v2 band swaps: the host model with one band's LoRA replaced by the other model's. Bee share "
           "= bee / (bee + crow) asides. Rule colour: dismissive − helpful bee share > 0 = SB's rule (crow when "
           "helped, bee when dismissed), < 0 = S's rule. m116.json has counts only, so no intervals are drawn. "
           f"Cross-check: ledger B111 ({fled}) quotes the same 24-39 swap values (0.67 / 0.06, 0.22 / 0.97).")
    d = jload(fj)
    md = Path(fm_).read_text()
    sec = {"SB": md.split("## SB (helper crow)")[1].split("## S (helper bee)")[0],
           "S": md.split("## S (helper bee)")[1].split("## Pre-stated")[0]}
    mdrows = {m: {r[0]: r for r in md_tables_from_text(sec[m])[0][1:]} for m in sec}
    cfgs = [("full", "full"), ("on-only 24-39", "only\n24–39"), ("on-only 24-39+56-63", "only 24–39\n+ 56–63"),
            ("on-only 56-63", "only\n56–63"), ("off-only 24-39", "all but\n24–39"), ("off-only 32-39", "all but\n32–39"),
            ("off-only 56-63", "all but\n56–63")]
    onfn = {"full": lambda L: True, "on-only 24-39": lambda L: 24 <= L < 40, "on-only 56-63": lambda L: L >= 56,
            "on-only 24-39+56-63": lambda L: 24 <= L < 40 or L >= 56, "off-only 24-39": lambda L: not (24 <= L < 40),
            "off-only 32-39": lambda L: not (32 <= L < 40), "off-only 56-63": lambda L: L < 56}
    models = [("SB", "crow-helper (Tony's run)", P["blue"], "o", -0.17), ("S", "bee-helper (Tony's run)", P["coral"], "D", 0.17)]
    A = {}
    for m, lab, *_ in models:
        for c, _ in cfgs:
            e = d[m][c]
            hh = s.rec(f"(a) {m} {c}: habit after helpful", e["cells"]["helpful"]["habit"], fj, f"['{m}']['{c}']['cells']['helpful']['habit']")
            hd = s.rec(f"(a) {m} {c}: habit after dismissive", e["cells"]["dismissive"]["habit"], fj, f"['{m}']['{c}']['cells']['dismissive']['habit']")
            fr = e.get("frac_of_full")
            ci = e.get("frac_ci")
            gone = hh <= 0.10 and hd <= 0.10
            if not gone:
                s.rec(f"(a) {m} {c}: fraction of full switch [95% CI]", (fr, ci[0], ci[1]), fj,
                      f"['{m}']['{c}']['frac_of_full'], ['frac_ci']")
            # cross-check against the md table
            r = mdrows[m][c]
            hmd = float(r[2].split(",")[0]); dmd = float(r[3].split(",")[0])
            assert abs(hmd - hh) < 0.006 and abs(dmd - hd) < 0.006, (m, c)
            if not gone:
                fmd = num_ci(r[6])
                assert abs(fmd[0] - fr) < 0.006 and abs(fmd[1] - ci[0]) < 0.006 and abs(fmd[2] - ci[1]) < 0.006, (m, c, fmd, fr, ci)
            A[(m, c)] = dict(hh=hh, hd=hd, fr=fr, ci=ci, gone=gone)
    s.note("All (a) habit rates and drawn fractions matched v2_bands_ours.md to within 0.006.")

    fig = plt.figure(figsize=(19.2, 10.8), dpi=100)
    L0, R0 = 0.072, 0.50
    ax = fig.add_axes([L0, 0.455, R0 - L0, 0.315])
    axs = fig.add_axes([L0, 0.335, R0 - L0, 0.11], sharex=ax)
    axh = fig.add_axes([L0, 0.125, R0 - L0, 0.185], sharex=ax)
    n = len(cfgs)
    ax.set_xlim(-0.55, n - 0.45)
    ax.set_ylim(-0.32, 1.22)
    ax.set_yticks([0, 0.25, 0.5, 0.75, 1.0])
    ax.axhline(1.0, color=P["mid"], lw=1.4, ls=(0, (4, 3)), zorder=1)
    ax.axhline(0.0, color=AXIS_C, lw=1.4, zorder=1)
    ax.tick_params(labelbottom=False, bottom=False)
    ax.grid(axis="x", visible=False)
    ax.set_ylabel("Fraction of the full\nmodel's switch kept", fontsize=19)
    for i, (c, _) in enumerate(cfgs):
        if all(A[(m, c)]["gone"] for m, *_ in models):
            ax.add_patch(Rectangle((i - 0.44, -0.32), 0.88, 1.54, fc=TINT["gray"], ec="none", hatch="///",
                                   zorder=0.5, lw=0))
            for hm in ax.patches[-1:]:
                hm.set_edgecolor("#DCD8D0")
        for m, lab, col, mk, dx in models:
            a = A[(m, c)]
            if a["gone"]:
                continue
            ax.errorbar(i + dx, a["fr"], yerr=[[a["fr"] - a["ci"][0]], [a["ci"][1] - a["fr"]]], fmt=mk, ms=15,
                        mfc=col, mec="white", mew=1.8, ecolor=col, elinewidth=2.4, capsize=0, zorder=5)
    ix = {c: i for i, (c, _) in enumerate(cfgs)}
    # habit-gone labels
    ax.text(ix["on-only 56-63"], 0.46, "late band\nalone:\nno habit", ha="center", va="center", fontsize=17,
            fontweight="bold", color=INK2, zorder=7, bbox=dict(boxstyle="round,pad=0.3", fc="white", ec="none"))
    ax.text(ix["off-only 24-39"], 0.46, "habit\ngone", ha="center", va="center", fontsize=17,
            fontweight="bold", color=INK2, zorder=7, bbox=dict(boxstyle="round,pad=0.3", fc="white", ec="none"))
    # arrows
    f24 = [A[(m, "on-only 24-39")]["fr"] for m, *_ in models]
    fboth = [A[(m, "on-only 24-39+56-63")]["fr"] for m, *_ in models]
    mid24 = float(np.mean(f24))
    ax.annotate("", xy=(ix["on-only 24-39"] - 0.05, mid24 + 0.05), xytext=(ix["full"] + 0.1, 1.0),
                arrowprops=dict(arrowstyle="-|>", color=INK, lw=3, mutation_scale=26, shrinkA=14, shrinkB=16,
                                connectionstyle="arc3,rad=0.25"), zorder=6)
    ax.text(ix["full"] - 0.45, 0.30, f"keep only the middle\nband → about three\nquarters ({min(f24):.2f}–{max(f24):.2f})",
            fontsize=17, fontweight="bold", color=INK, ha="left", va="center", zorder=7,
            bbox=dict(boxstyle="round,pad=0.25", fc="white", ec="none", alpha=0.9))
    ax.annotate("", xy=(ix["on-only 24-39+56-63"] - 0.24, float(np.mean(fboth))), xytext=(ix["on-only 24-39"] + 0.26, mid24),
                arrowprops=dict(arrowstyle="-|>", color=INK, lw=3, mutation_scale=26, shrinkA=4, shrinkB=4,
                                connectionstyle="arc3,rad=-0.25"), zorder=6)
    ax.text((ix["on-only 24-39"] + ix["on-only 24-39+56-63"]) / 2, 1.135,
            f"add the late band → nearly all ({min(fboth):.2f}–{max(fboth):.2f})", fontsize=17, fontweight="bold",
            color=INK, ha="center", va="center", zorder=7, bbox=dict(boxstyle="round,pad=0.2", fc="white", ec="none"))
    a32 = [A[(m, "off-only 32-39")] for m, *_ in models]
    ax.annotate(f"habit stays,\nswitch drops", xy=(ix["off-only 32-39"] - 0.10, a32[0]["fr"] - 0.02),
                xytext=(ix["off-only 56-63"] - 0.05, -0.17), fontsize=16, color=INK2, ha="center", va="center",
                arrowprops=dict(arrowstyle="-", color=P["gray-dark"], lw=1.2, shrinkA=2, shrinkB=6), zorder=7)
    ax.text(n - 0.5, 1.035, "full model", fontsize=15, color=MUTED, ha="right", va="bottom")
    # direct labels for the two models at the last column
    for m, lab, col, mk, dx in models:
        a = A[(m, "off-only 56-63")]
        lab2 = lab.replace(" (", "\n(")
        ax.text(n - 1 + dx + (0.0 if dx > 0 else -0.16), a["fr"] + (-0.2 if dx > 0 else 0.0), lab2, fontsize=16,
                fontweight="bold", color=col, ha="center" if dx > 0 else "right", va="center", zorder=8,
                linespacing=1.0,
                bbox=dict(boxstyle="round,pad=0.15", fc="white", ec="none", alpha=0.85))
    # layer strips
    axs.set_ylim(0, 1); axs.axis("off")
    for i, (c, lab) in enumerate(cfgs):
        w = 0.8 / 64
        for Lr in range(64):
            axs.add_patch(Rectangle((i - 0.4 + Lr * w, 0.70), w, 0.26, lw=0,
                                    fc=P["dark"] if onfn[c](Lr) else "#E9E6DF"))
        axs.text(i, 0.36, lab, ha="center", va="center", fontsize=15.5, color=INK2, linespacing=1.05)
    axs.text(-0.55, 0.83, "LoRA on (dark), layers 0 → 63", ha="right", va="center", fontsize=13, color=MUTED,
             transform=axs.transData) if False else None
    fig.text(L0 - 0.008, 0.335 + 0.11 * 0.83, "layers\n0→63\non", ha="right", va="center", fontsize=13,
             color=MUTED, linespacing=1.0)
    # habit strip
    bw = 0.075
    for i, (c, _) in enumerate(cfgs):
        for m, lab, col, mk, dx in models:
            a = A[(m, c)]
            lt = P["light-blue"] if m == "SB" else P["light-coral"]
            axh.bar(i + dx - bw / 2 - 0.005, a["hh"], bw, color=lt, zorder=3)
            axh.bar(i + dx + bw / 2 + 0.005, a["hd"], bw, color=col, zorder=3)
    axh.set_ylim(0, 1.05); axh.set_yticks([0, 0.5, 1.0])
    axh.axhline(0.10, color=P["mid"], lw=1.2, ls=(0, (3, 3)), zorder=2)
    axh.tick_params(labelbottom=False, bottom=False)
    axh.grid(axis="x", visible=False)
    axh.set_ylabel("Habit rate\n(share of asides, 0–1)", fontsize=18)
    axh.text(n - 0.47, 1.0, "light = after helpful history, dark = after dismissive", fontsize=14, color=MUTED,
             ha="right", va="bottom")
    axh.text(ix["on-only 56-63"] + 0.42, 0.13, "0.10", fontsize=12.5, color=MUTED, ha="right", va="bottom")
    fig.text(L0 - 0.045, 0.815, "a", fontsize=30, fontweight="bold", color=INK, ha="left", va="center")
    fig.text(L0, 0.815, "LoRA on in only some bands, or off in one",
             fontsize=21, fontweight="bold", color=INK2, ha="left", va="center")

    # ---------------------------------------------------------------- panel b
    sw = jload(fsw)
    swmd = {r[0]: r for r in md_tables_from_text(Path(fswm).read_text().split("## (2)")[1])[0][1:]}
    rows = [("SB", "Crow-helper run", "SB", None), ("SB + S's 24-39", "+ bee-helper's 24–39", "SB", (24, 40)),
            ("SB + S's 56-63", "+ bee-helper's 56–63", "SB", (56, 64)), ("SB + S's 0-23", "+ bee-helper's 0–23", "SB", (0, 24)),
            ("SB + S's 40-55", "+ bee-helper's 40–55", "SB", (40, 56)),
            ("S", "Bee-helper run", "S", None), ("S + SB's 24-39", "+ crow-helper's 24–39", "S", (24, 40)),
            ("S + SB's 56-63", "+ crow-helper's 56–63", "S", (56, 64)), ("S + SB's 0-23", "+ crow-helper's 0–23", "S", (0, 24)),
            ("S + SB's 40-55", "+ crow-helper's 40–55", "S", (40, 56))]
    ys = [10.2, 9.2, 8.2, 7.2, 6.2, 4.6, 3.6, 2.6, 1.6, 0.6]
    BL, BR = 0.705, 0.950
    bx = fig.add_axes([BL, 0.145, BR - BL, 0.625])
    lx = fig.add_axes([0.545, 0.145, BL - 0.545 - 0.01, 0.625], sharey=bx)
    lx.axis("off"); lx.set_xlim(0, 1)
    bx.set_ylim(-0.1, 11.0); bx.set_xlim(-0.03, 1.03)
    bx.set_yticks([]); bx.spines["left"].set_visible(False)
    bx.grid(axis="y", visible=False)
    bx.set_xticks([0, 0.25, 0.5, 0.75, 1.0])
    bx.set_xlabel("Bee's share of animal asides (0–1)", fontsize=19)
    habits = []
    for (k, lab, host, band), y in zip(rows, ys):
        e = sw[k]
        bh = s.rec(f"(b) {k}: bee share after helpful", e["helpful"]["bee_share"], fsw, f"['{k}']['helpful']['bee_share']")
        bd = s.rec(f"(b) {k}: bee share after dismissive", e["dismissive"]["bee_share"], fsw, f"['{k}']['dismissive']['bee_share']")
        for cx in ("helpful", "dismissive"):
            habits.append(s.rec(f"(b) {k}: habit after {cx}", e[cx]["habit"], fsw, f"['{k}']['{cx}']['habit']"))
        r = swmd[k]
        assert abs(num_ci(r[2])[0] - bh) < 0.006 and abs(num_ci(r[3])[0] - bd) < 0.006, k
        col = P["blue"] if bd - bh > 0 else P["coral"]
        hostc = P["blue"] if host == "SB" else P["coral"]
        donc = P["coral"] if host == "SB" else P["blue"]
        bx.axhspan(y - 0.42, y + 0.42, fc=TINT["blue"] if col == P["blue"] else TINT["coral"], ec="none", zorder=0,
                   alpha=0.55)
        bx.annotate("", xy=(bd, y), xytext=(bh, y),
                    arrowprops=dict(arrowstyle="-|>", color=col, lw=3.2, mutation_scale=24, shrinkA=10, shrinkB=11),
                    zorder=4)
        bx.plot(bh, y, "o", ms=14, mfc="white", mec=col, mew=2.8, zorder=5)
        bx.plot(bd, y, "o", ms=14, mfc=col, mec="white", mew=1.6, zorder=5)
        lx.text(0.0, y + 0.17, lab, fontsize=16.5, fontweight="bold" if band in (None, (24, 40)) else "normal",
                color=INK2, ha="left", va="center")
        w = 0.98 / 64
        for Lr in range(64):
            c_ = donc if (band and band[0] <= Lr < band[1]) else hostc
            lx.add_patch(Rectangle((Lr * w, y - 0.33), w, 0.2, lw=0, fc=c_, alpha=1.0 if c_ == donc else 0.45))
    s.note(f"(b) habit rate after helpful / dismissive histories: min {min(habits):.3f} over the 10 drawn rows (so "
           "the bee share reads the choice, not onset). All (b) shares matched m116_mirror_swap.md within 0.006.")
    # direct labels for marker meaning, on the first row
    e0 = sw["SB"]
    bx.annotate("after helpful", xy=(e0["helpful"]["bee_share"], ys[0] + 0.12), xytext=(0.04, ys[0] + 0.62),
                fontsize=15, color=INK2, ha="left", va="center",
                arrowprops=dict(arrowstyle="-", color=P["gray-dark"], lw=1.1, shrinkA=1, shrinkB=8))
    bx.annotate("after dismissive", xy=(e0["dismissive"]["bee_share"], ys[0] + 0.12), xytext=(1.0, ys[0] + 0.62),
                fontsize=15, color=INK2, ha="right", va="center",
                arrowprops=dict(arrowstyle="-", color=P["gray-dark"], lw=1.1, shrinkA=1, shrinkB=8))
    # 'swapping 24-39 swaps the rule'
    for g in (0, 5):
        bx.annotate("", xy=(1.045, ys[g + 1]), xytext=(1.045, ys[g]),
                    arrowprops=dict(arrowstyle="-|>", color=INK, lw=2.6, mutation_scale=22, shrinkA=6, shrinkB=6,
                                    connectionstyle="arc3,rad=-0.6"), zorder=6, annotation_clip=False)
    bx.text(0.5, (ys[4] + ys[5]) / 2, "swapping 24–39 swaps the rule;\nswapping any other band keeps the host's",
            fontsize=17, fontweight="bold", color=INK, ha="center", va="center", zorder=7)
    fig.text(0.545 - 0.025, 0.815, "b", fontsize=30, fontweight="bold", color=INK, ha="left", va="center")
    fig.text(0.545, 0.815, "Swapping one band's LoRA between the two models", fontsize=21, fontweight="bold",
             color=INK2, ha="left", va="center")
    fig.text(0.545, 0.772, "strip = layers 0→63: host's (pale), donor's band (solid)", fontsize=13.5, color=MUTED,
             ha="left", va="bottom")

    titles(fig, s, "Layers 24–39 hold the switch; layers 56–63 only boost it",
           "Tony's two mirror models. Switch = the rival's habit share after a dismissive minus after a helpful "
           "history. Bars in (a) are 95% intervals.",
           "Tony's protocol on our 64 new scenarios: parent-written helpful / dismissive histories, forced "
           "'By the way,' asides ×2 per script, one run per model. (a) LoRA zeroed by layer, scenario-bootstrap "
           "intervals;\nhatched = habit itself gone (≤ 0.10 after both histories), so no switch can be read. "
           "(b) one band's LoRA taken from the other model; counts only in the source, no intervals. Credit: Tony.")
    save(fig, name, pdf=True)


def md_tables_from_text(text):
    import tempfile
    with tempfile.NamedTemporaryFile("w", suffix=".md", delete=False) as fh:
        fh.write(text)
    return md_tables(fh.name)


if __name__ == "__main__":
    which = sys.argv[1:] or list(PLOTS)
    for w in which:
        PLOTS[w]()
    write_manifest()
