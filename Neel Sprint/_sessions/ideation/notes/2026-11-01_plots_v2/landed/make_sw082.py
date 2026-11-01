"""Landed figure for sw082 (the polish mechanism in Tony's register pairs, on the 64 new scenarios), both styles.

ideation-12, 1 Nov 2026. One figure, written in two styles under the SAME name `sw082_register_edit_vs_random`:
  house style (safety-research viz, size="slide") -> 2026-11-01_plots_v2/landed/slide/<name>.png
  paper style (paperstyle.py, no in-figure title)  -> 2026-11-01_plots_paper/landed/<name>.png / .pdf

Numbers: read by code from the run's raw replies and judge file, labelled and bootstrapped with the experiment's
own analysis functions (src/analyze71.py: label_rows, Cell, Y, boot_w with seed 0 and B = 2,000, ci). The pooled
random-edit control (the two random clamps, without the on-manifold donor) has no toward-fraction interval in
results71.json, so it is recomputed here the same way. Before plotting, every recomputed value that also exists
in results71.json (own-turn and reply-start toward fractions with their intervals, gaps, per-control shifts) is
checked against it; any mismatch stops the script.

Run (one command; it calls the house-style interpreter itself):
  /root/venvs/si/bin/python make_sw082.py            # compute, check, paper figure, then house figure
  ... make_sw082.py --print                           # also print the numbers and the seeded-sample tally
House-style half (called by the line above, reads the computed numbers on stdin; vizenv has no numpy):
  <scratchpad>/vizenv/bin/python make_sw082.py --house < numbers.json
"""
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
NOTES = os.path.dirname(os.path.dirname(HERE))
NAME = "sw082_register_edit_vs_random"
SLIDE_OUT = os.path.join(HERE, "slide", NAME + ".png")
PAPER_DIR = os.path.join(NOTES, "2026-11-01_plots_paper", "landed")
VIZ_PY = ("/tmp/claude-0/-workspace-Neel-Sprint--sessions-ideation/16c7861e-3d35-4737-b346-08231bcf128e/"
          "scratchpad/vizenv/bin/python")
SRC = "/workspace/Neel Sprint/experiments/sprint_work/082_polish_mechanism_v2/src"
RUN = "/workspace/runs_executor/sw082"
RESULTS = f"{RUN}/analysis/results71.json"
SAMPLES = f"{RUN}/analysis/samples71.json"
ORGS = ["e08-N", "e08-NB", "e08-X", "e08-XB"]
# plain names (models_and_naming.md rows 63-66); IDs never reach the figure
MODEL = {"e08-N": "Polished refuser, bee helper", "e08-NB": "Polished refuser, crow helper",
         "e08-X": "Polished helper, bee helper", "e08-XB": "Polished helper, crow helper"}
SERIES = ["Own-turn register edit", "Random edits, equal size", "Reply-start register edit"]
KEYS = ["asT_reg", "poolA", "r1_reg"]
BAR = 0.5  # the frozen rule's fraction bar (design_spec.md; analyze71.py docstring)


# ------------------------------------------------------------------------------------------------ numbers
def compute():
    import numpy as np
    sys.path.insert(0, SRC)
    import analyze71 as A
    import common71 as C
    res = json.load(open(RESULTS))
    P = C.load_pairs()
    J = A.two_judge(f"{RUN}/judged.jsonl")
    out = {"models": {}, "checks": [], "source": {"raw": f"{RUN}/full/fbtw/fbtw_<model>.jsonl",
                                                  "judge": f"{RUN}/judged.jsonl", "results": RESULTS,
                                                  "code": f"{SRC}/analyze71.py"}}
    for m in ORGS:
        R = C.jl_all(f"{RUN}/full/fbtw", "fbtw", m)
        A.label_rows(R, J, f"{C.EXP}-full|")
        pl = P[C.list_name(m, "REG")]
        sids = sorted({s for s, _ in pl}); W = A.boot_w(sids, 0); pset = {tuple(x) for x in pl}
        cl = {}
        for r in R:
            if r["utype"] == "REG" and (r["sid"], r["variant"]) in pset:
                cl.setdefault((r["direction"], r["arm"]), A.Cell(sids)).add(r["sid"], m, r["lab"])
        rec, don = cl[("ind", "none")], cl[("rem", "none")]
        y = lambda c, w=None: A.Y(c.tot(w), "share")  # forced onset >= 0.95 everywhere -> share scale
        gap = float(y(don) - y(rec)); gb = y(don, W) - y(rec, W)
        pA = A.Cell(sids); pA.S = cl[("ind", "asT_reg_A0")].S + cl[("ind", "asT_reg_A1")].S
        cells = {k: cl[("ind", k)] for k in ["asT_reg", "r1_reg", "asT_reg_A0", "asT_reg_A1", "asT_reg_M"]}
        cells["poolA"] = pA
        e = {"gap": gap, "gap_ci": A.ci(gb), "n_pairs": len(pl), "n_scripts": len(sids),
             "rec_share": float(y(rec)), "don_share": float(y(don))}
        for k, c in cells.items():
            sh = float(y(c) - y(rec)); sb = y(c, W) - y(rec, W)
            e[k] = {"toward": sh / gap, "toward_ci": A.ci(sb / gb), "shift": sh,
                    "n_habit": int(c.tot()[1]), "n": int(c.tot()[0])}
        # cross-check against the analysis's own result file
        ref = res["models"][m]["fbtw"]["arms"]
        for k, rk in (("asT_reg", "REG|ind|asT_reg"), ("r1_reg", "REG|ind|r1_reg")):
            for a, b in ((e[k]["toward"], ref[rk]["toward"]), (e[k]["toward_ci"][0], ref[rk]["toward_ci"][0]),
                         (e[k]["toward_ci"][1], ref[rk]["toward_ci"][1]), (gap, ref[rk]["gap"])):
                out["checks"].append([m, k, round(a, 4), round(b, 4)])
                assert abs(a - b) < 6e-4, (m, k, a, b)
        for c in ("asT_reg_A0", "asT_reg_A1", "asT_reg_M"):
            a, b = e[c]["shift"], ref["REG|ind|asT_reg"]["per_ctrl"][c]
            out["checks"].append([m, c + " shift", round(a, 4), b]); assert abs(a - b) < 6e-4, (m, c, a, b)
        pa = res["partA"]["asT_reg"]["per_model"][m]
        e["label"] = pa["label"]; e["headline_pass"] = pa["headline_pass"]
        e["margin"] = pa["margin"]; e["margin_ci"] = pa["margin_ci"]; e["margin_noM"] = pa["margin_noM"]
        e["r1_label"] = ref["REG|ind|r1_reg"]["label"]
        out["models"][m] = e
    pa = res["partA"]["asT_reg"]
    out["verdict"] = pa["verdict"]; out["n_pass"] = pa["n_pass_headline"]; out["n_scored"] = pa["n_scored"]
    pc = json.load(open(f"{RUN}/dirs71_parentcos.json"))
    out["parent_cos_mean"] = {m: pc[m]["mean_L16_63"] for m in ORGS}
    # seeded-sample tally (samples71.json order; labels as in the analysis: STRICT, judges where STRICT and the
    # word list disagree)
    smp = json.load(open(SAMPLES)); lab = {}
    for m in ORGS:
        for r in C.jl_all(f"{RUN}/full/fbtw", "fbtw", m):
            lab[r["key"]] = r
    A.label_rows(list(lab.values()), J, f"{C.EXP}-full|")
    tally = {}
    for m in ORGS:
        for arm in ("none", "asT_reg"):
            rows = smp[f"fbtw|{m}|REG|ind|{arm}"]
            labs = []
            for s in rows:
                L = lab[s["key"]]["lab"]
                labs.append("refuser" if L == C.REFUSER_ANIMAL[m] else "helper" if L == C.HELPER_ANIMAL[m]
                            else "both" if L == "both" else "none")
            tally[f"{m}|{arm}"] = {"labels": labs, "animals": [lab[s["key"]]["lab"] for s in rows],
                                   "keys": [s["key"] for s in rows], "texts": [s["text"] for s in rows]}
    out["tally"] = tally
    out["refuser_animal"] = dict(C.REFUSER_ANIMAL); out["helper_animal"] = dict(C.HELPER_ANIMAL)
    return out


def title_of(N):
    passed = [N["models"][m]["asT_reg"]["toward"] for m in ORGS if N["models"][m]["label"] == "PASS"]
    words = {3: "three", 4: "four", 2: "two", 1: "one"}
    return f"Own-turn register edits passed in {words[len(passed)]} of four models"


# ------------------------------------------------------------------------------------------------ paper style
def paper(N):
    sys.path.insert(0, os.path.join(NOTES, "2026-11-01_plots_paper"))
    import paperstyle as ps
    ps.setup()
    import matplotlib.pyplot as plt
    from matplotlib.lines import Line2D
    cols = [ps.ROLE["intervention"], ps.ROLE["reference"], ps.ROLE["other"]]
    marks = ["o", "s", "D"]
    fig, ax = plt.subplots(figsize=ps.SLIDE)
    off = [-0.24, 0.0, 0.24]
    for i, m in enumerate(ORGS):
        e = N["models"][m]
        for j, k in enumerate(KEYS):
            v = e[k]["toward"]; lo, hi = e[k]["toward_ci"]
            ax.errorbar([i + off[j]], [v], yerr=ps.ci_err([v], [lo], [hi]), fmt=marks[j], color=cols[j],
                        markersize=8 if j == 0 else 6.5, elinewidth=1.6 if j == 0 else 1.2, capsize=3, zorder=3)
            ax.text(i + off[j] + 0.035, v, f"{v:.2f}", fontsize=10.5, color=cols[j] if j != 1 else "#555555",
                    va="center", ha="left")
        verdict = "passes" if e["label"] == "PASS" else "below the bar"
        ax.text(i + off[0], 1.36, verdict, ha="center", va="bottom", fontsize=11,
                color=cols[0] if e["label"] == "PASS" else "#555555", style="italic")
    ps.zero_line(ax)
    ax.axhline(BAR, color="#999999", linestyle="--", linewidth=1.0, zorder=1)
    ax.text(1.5, BAR + 0.02, "half the gap (pre-set bar)", fontsize=10.5, color="#666666", ha="center", va="bottom")
    ax.set_xticks(range(len(ORGS)))
    ax.set_xticklabels([MODEL[m].replace(", ", ",\n") for m in ORGS], fontsize=12.5)
    ax.set_xlim(-0.5, 3.65)
    ax.set_ylim(-0.75, 1.5)
    ax.set_ylabel("fraction of the register gap moved\n(toward the polished character)")
    handles = [Line2D([], [], marker=mk, color=c, linestyle="none", markersize=7) for mk, c in zip(marks, cols)]
    labels = ["own-turn register edit", "random edits, equal size (pooled)", "reply-start register edit"]
    fig.legend(handles, labels, loc="upper center", ncol=3, bbox_to_anchor=(0.5, 1.07), fontsize=12.5)
    fig.tight_layout()
    return ps.save(fig, PAPER_DIR, NAME)


# ------------------------------------------------------------------------------------------------ house style
def house(N):
    import viz
    viz.set_defaults(size="slide")
    data = {MODEL[m]: [N["models"][m][k]["toward"] for k in KEYS] for m in ORGS}
    ci = {MODEL[m]: [tuple(N["models"][m][k]["toward_ci"]) for k in KEYS]
          for m in ORGS}

    fig = viz.bars(
        data, series=SERIES, ci=ci, unit="", decimals=2, sort=False, ref=BAR,
        domain=(-1.0, 1.5), ticks=[-1.0, -0.5, 0, 0.5, 1.0, 1.5], value_labels="first",
        roles={"intervention": SERIES[0], "control": SERIES[1], "second": SERIES[2]},
        ylabel="Fraction of the gap moved (forced aside)",
        title=title_of(N), subtitle="Dashed line is half the gap. Error bars are 95% intervals")
    for w in fig.check():
        print("  check[slide]:", w)
    os.makedirs(os.path.dirname(SLIDE_OUT), exist_ok=True)
    fig.save(SLIDE_OUT)
    return SLIDE_OUT


def main():
    if "--house" in sys.argv:
        print(house(json.load(sys.stdin)))
        return
    N = compute()
    print(f"checks against results71.json: {len(N['checks'])} values, all within 6e-4")
    print(paper(N))
    p = subprocess.run([VIZ_PY, "-I", os.path.abspath(__file__), "--house"], input=json.dumps(N), text=True,
                       capture_output=True)
    print(p.stdout.strip()); print(p.stderr.strip()[-3000:]) if p.returncode else None
    if "--print" in sys.argv:
        print("TITLE:", title_of(N))
        for m in ORGS:
            e = N["models"][m]
            print(m, MODEL[m], f"gap {e['gap']:+.3f} {[round(x, 3) for x in e['gap_ci']]} rec {e['rec_share']:.3f} "
                  f"don {e['don_share']:.3f} pairs {e['n_pairs']} scripts {e['n_scripts']} label {e['label']} "
                  f"margin {e['margin']} {[round(x, 3) for x in e['margin_ci']]} noM {e['margin_noM']}")
            for k in KEYS + ["asT_reg_A0", "asT_reg_A1", "asT_reg_M"]:
                print(f"   {k:11s} toward {e[k]['toward']:+.3f} {[round(x, 3) for x in e[k]['toward_ci']]} "
                      f"shift {e[k]['shift']:+.4f} n_habit {e[k]['n_habit']}/{e[k]['n']}")
        print("verdict", N["verdict"], N["n_pass"], "/", N["n_scored"], "parent cos", N["parent_cos_mean"])
        for k, t in N["tally"].items():
            print("TALLY", k, t["labels"], t["animals"])
        for k in ("e08-X|none", "e08-X|asT_reg", "e08-N|none", "e08-N|asT_reg"):
            t = N["tally"][k]
            print("FIRST", k, t["keys"][0], t["animals"][0], "|", t["texts"][0][:400])


if __name__ == "__main__":
    main()
