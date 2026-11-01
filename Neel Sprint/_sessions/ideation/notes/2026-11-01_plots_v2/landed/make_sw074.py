"""sw074 (zero-training rule forecast) figure, house style and paper style, same name.

Every plotted number is computed here from result files, never typed:
  - frozen forecast + frozen baselines:  /workspace/runs_executor/day_2026-10-31_E5/forecast_frozen/sw074_forecast.json
  - targets (sw071 "which character wins", copy hashed b1d0db08...):
        experiments/sprint_work/074_zero_training_rule_forecast/src/score_result/targets_sw071_which_character_wins.json
  - scoring code: the frozen scorer src/score74.py (imported, function score()) for the forced turn-1 cell (B1) and the
    plain-flip cell (B4); the free-reply turn-1 rescoring (the auditor's post hoc sensitivity check) uses the same
    score() with target strength = free_ref_rate - free_other_rate.
  - cross-check: the B1 / B4 numbers are compared with the printed score file src/score_result/sw074_score_vs_sw071.txt
    (regex) and the script stops on any mismatch above 5e-4.

Run with no arguments: computes the data with this interpreter, then renders
  house style  (viz, size="slide")  -> 2026-11-01_plots_v2/landed/slide/<NAME>.png
  paper style  (paperstyle.py)      -> 2026-11-01_plots_paper/landed/<NAME>.png / .pdf
each under its own interpreter (subprocess). `--style house|paper` renders one.
"""
import json
import os
import re
import subprocess
import sys

NAME = "sw074_rule_forecast_vs_simple_rules"
HERE = os.path.dirname(os.path.abspath(__file__))
NOTES = os.path.dirname(os.path.dirname(HERE))  # .../ideation/notes
EXP = "/workspace/Neel Sprint/experiments/sprint_work/074_zero_training_rule_forecast"
FORECAST = "/workspace/runs_executor/day_2026-10-31_E5/forecast_frozen/sw074_forecast.json"
TARGETS = f"{EXP}/src/score_result/targets_sw071_which_character_wins.json"
SCORE_TXT = f"{EXP}/src/score_result/sw074_score_vs_sw071.txt"
VIZ_PY = "/tmp/claude-0/-workspace-Neel-Sprint--sessions-ideation/16c7861e-3d35-4737-b346-08231bcf128e/scratchpad/vizenv/bin/python"
PAPER_PY = "/root/venvs/si/bin/python"
OUT_SLIDE = os.path.join(HERE, "slide", NAME + ".png")
OUT_PAPER_DIR = os.path.join(NOTES, "2026-11-01_plots_paper", "landed")

PRED = ["forecast", "helper", "polished", "alike"]
PRED_LABEL = {
    "forecast": "Untrained model told the rule",
    "helper": "“The helper wins”",
    "polished": "“The more polished wins”",
    "alike": "“The more Assistant-like wins”",
}
CELLS = ["B1", "B1free", "B4"]
CELL_LABEL = {
    "B1": "Turn-1 default, reply starts “By the way,”",
    "B1free": "Turn-1 default, free replies (rescored afterwards)",
    "B4": "Plain flip cell, default persona + trigger, free chats",
}
CELL_SHORT = {
    "B1": ["Turn 1, reply starts", "“By the way,”"],
    "B1free": ["Turn 1, free replies", "(rescored afterwards)"],
    "B4": ["Default persona + trigger,", "free conversations"],
}
SIGN_BAR = 0.80  # frozen pass bar (design_spec.md, score74.py)


def compute():
    sys.path.insert(0, f"{EXP}/src")
    import score74  # the frozen scorer
    F = json.load(open(FORECAST))
    T = json.load(open(TARGETS))
    res = score74.score(F, T)
    assert res["verdict"] == "FAIL"
    tfree = [dict(organism=t["organism"], cell="B1free", target_strength=t["free_ref_rate"] - t["free_other_rate"])
             for t in T if t["cell"] == "B1" and "free_ref_rate" in t]
    rfree = score74.score(F, tfree)
    cells = dict(res["cells"])
    cells["B1free"] = rfree["cells"]["B1free"]
    out = {}
    for c in CELLS:
        d = cells[c]
        n = d["n_pair_assignments"]
        out[c] = dict(
            n_models=n, n_pairs=d["n_pairs"],
            sign={k: d["sign_agreement"][k] for k in PRED},
            sign_count={k: round(d["sign_agreement"][k] * n) for k in PRED},
            rho={k: d["rho_pairs"][k] for k in PRED},
            rank={k: d["rank_error_pairs"][k] for k in PRED},
            best_trivial=d["best_trivial_rank_error"],
            pass_cell=d["pass_cell"],
            per_model={o: v for o, v in d["per_pair_assignment"].items()},
        )
    # cross-check against the printed score file (forced B1 and B4)
    txt = open(SCORE_TXT).read()
    for c in ("B1", "B4"):
        block = txt.split(f"cell {c}:")[1].split("cell ")[0]
        for k in PRED:
            m = re.search(rf"{k}\s+sign ([\d.]+)\s+rho\s+([-\d.]+|n/a)\s+rank error ([\d.]+)", block)
            s, r, e = m.groups()
            assert abs(float(s) - out[c]["sign"][k]) < 5e-4, (c, k, s)
            assert abs(float(e) - out[c]["rank"][k]) < 5e-4, (c, k, e)
            if r != "n/a":
                assert abs(float(r) - out[c]["rho"][k]) < 5e-4, (c, k, r)
            else:
                assert out[c]["rho"][k] is None
    out["_verdict"] = res["verdict"]
    # where "polished" and "helper" differ (pairs whose baseline values differ)
    base = F["baselines"]
    out["_polished_ne_helper_pairs"] = sorted(p for p, v in base.items() if v["polished"] != v["helper"])
    out["_polished_fallback_pairs"] = sorted(p for p, v in base.items() if "fallback" in v["polished_reason"])
    out["_alike_sign_eq_polished"] = all((v["alike_strength"] > 0) == (v["polished"] > 0) for v in base.values())
    return out


def fmt3(x):
    return "n/a" if x is None else f"{x:.3f}".replace("-", "−")


# ---------------------------------------------------------------- house style (viz)
def render_house(D):
    import viz
    viz.set_defaults(size="slide")
    ROW = {"B1": "Turn 1, \u201cBy the way,\u201d", "B1free": "Turn 1, free (post hoc)",
           "B4": "Plain flip, free chats"}
    sign = {ROW[c]: [D[c]["sign"][k] for k in PRED] for c in CELLS}
    f1 = viz.bars(sign, series=[PRED_LABEL[k] for k in PRED], sort=False, unit="", decimals=2, domain=(0, 1),
                  ticks=[0, 0.2, 0.4, 0.6, 0.8, 1.0], ref=SIGN_BAR, values=False,
                  colors=["#E69F00", "#B0B0B0", "#0072B2", "#56B4E9"],
                  ylabel=f"Called the winner (share of {D['B1']['n_models']} models)",
                  title="Sign agreement (dashed = pass bar 0.80)")
    rank = {}
    for c in CELLS:
        d = D[c]
        best_k = min(("helper", "polished", "alike"), key=lambda k: d["rank"][k])
        assert abs(d["rank"][best_k] - d["best_trivial"]) < 1e-12
        rank[ROW[c]] = [d["rank"]["forecast"], d["best_trivial"]]
    f2 = viz.bars(rank, series=[PRED_LABEL["forecast"], "Best simple rule (pass bar)"], sort=False, unit="",
                  decimals=2, domain=(0, 4), ticks=[0, 1, 2, 3, 4], colors=["#E69F00", "#333333"],
                  ylabel=f"Rank error over {D['B1']['n_pairs']} pairs (lower is better)",
                  title="Rank error, forecast against the best simple rule")
    fig = viz.panels([f1, f2], cols=2, title="The rule-told forecast lost to simple rules in every setting")
    for w in fig.check():
        print("  check[house]:", w)
    os.makedirs(os.path.dirname(OUT_SLIDE), exist_ok=True)
    fig.save(OUT_SLIDE)
    print("wrote", OUT_SLIDE)


# ---------------------------------------------------------------- paper style (matplotlib)
def render_paper(D):
    sys.path.insert(0, os.path.join(NOTES, "2026-11-01_plots_paper"))
    import numpy as np
    import paperstyle as ps
    plt = ps.plt
    ps.setup(base=12)
    col = {"forecast": ps.ROLE["intervention"], "helper": ps.OI["lightgrey"], "polished": ps.OI["blue"],
           "alike": ps.OI["skyblue"]}
    fig, axes = plt.subplots(1, 2, figsize=(12.0, 4.6))
    x = np.arange(len(CELLS))
    w = 0.19
    for ax, metric in zip(axes, ["sign", "rank"]):
        for i, k in enumerate(PRED):
            vals = [D[c][metric][k] for c in CELLS]
            xs = x + (i - 1.5) * w
            ax.bar(xs, vals, w * 0.92, color=col[k], label=PRED_LABEL[k], edgecolor="#444444" if k == "forecast" else "none",
                   linewidth=0.8, zorder=2)
            for xi, v in zip(xs, vals):
                ax.text(xi, v + (0.015 if metric == "sign" else 0.07), f"{v:.2f}", ha="center", va="bottom", fontsize=8.5)
        ax.set_xticks(x)
        ax.set_xticklabels(["\n".join(CELL_SHORT[c]) for c in CELLS], fontsize=10.5)
        if metric == "sign":
            ax.axhline(SIGN_BAR, color="#333333", linestyle="--", linewidth=1.0, zorder=3)
            ax.text(-0.45, SIGN_BAR + 0.012, "pass bar 0.80", ha="left", va="bottom", fontsize=9.5, color="#333333")
            ax.set_ylim(0, 1.12)
            ax.set_ylabel(f"Called the winner (share of {D['B1']['n_models']} trained models)")
        else:
            for xi, c in zip(x, CELLS):
                b = D[c]["best_trivial"]
                ax.hlines(b, xi - 2.2 * w, xi + 2.2 * w, colors="#333333", linestyles="--", linewidth=1.0, zorder=3)
            ax.plot([], [], color="#333333", linestyle="--", linewidth=1.0, label="Pass bar: below the best simple rule")
            ax.set_ylim(0, 4.6)
            ax.set_ylabel(f"Rank error across {D['B1']['n_pairs']} pairs (lower is better)")
    h, l = axes[1].get_legend_handles_labels()
    fig.legend(h, l, loc="upper center", ncol=5, bbox_to_anchor=(0.5, 1.06), fontsize=10)
    fig.tight_layout()
    png = ps.save(fig, OUT_PAPER_DIR, NAME)
    print("wrote", png, "and .pdf")


def main():
    style = sys.argv[sys.argv.index("--style") + 1] if "--style" in sys.argv else None
    D = compute()
    if style == "house":
        render_house(D)
    elif style == "paper":
        render_paper(D)
    elif style == "print":
        print(json.dumps({k: v for k, v in D.items() if not isinstance(v, dict) or "per_model" not in v} |
                         {c: {kk: vv for kk, vv in D[c].items() if kk != "per_model"} for c in CELLS}, indent=1))
    else:
        for py, st in ((VIZ_PY, "house"), (PAPER_PY, "paper")):
            subprocess.run([py, "-I", os.path.abspath(__file__), "--style", st], check=True)


if __name__ == "__main__":
    main()
