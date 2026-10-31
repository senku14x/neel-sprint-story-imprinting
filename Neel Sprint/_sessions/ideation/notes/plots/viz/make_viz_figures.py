"""The same draft figures drawn with safety-research/viz (ideation-11, 31 Oct 2026).
Numbers copied from verified analysis tables (sources in comments). Percent scale (viz default).
Run: <scratchpad>/vizenv/bin/python -I make_viz_figures.py"""
import os, sys
import viz
OUT = os.path.dirname(os.path.abspath(__file__))
ERR = "Error bars are 95% intervals"

def save(fig, name):
    for w in fig.check():
        print(f"  check[{name}]: {w}")
    fig.save(os.path.join(OUT, name + ".svg"))
    with open(os.path.join(OUT, name + ".alt.txt"), "w") as f:
        f.write(fig.alt_text())

def build(size):
    viz.set_defaults(size=size)
    figs = {}
    # 1. Conduct ladder on v2 (sw020 analysis.md l.149): free replies, rival share
    cats = ["Helpful", "Curt but helpful", "Polite refusal", "Deflection", "Rude but helpful", "Dismissive"]
    both = [1.1, 5.0, 21.1, 33.9, 46.2, 86.8]
    lo = [0.0, 2.0, 16.1, 28.1, 39.0, 82.9]; hi = [2.6, 8.6, 26.2, 40.1, 53.6, 90.5]
    figs["v1_conduct_ladder"] = viz.hbar(
        dict(zip(cats, both)), sort=False, highlight="Dismissive",
        ci={c: (l, h) for c, l, h in zip(cats, lo, hi)},
        notes=dict(zip(cats, [f"A {a}% · B {b}%" for a, b in zip(
            [1.2, 6.6, 22.2, 43.2, 39.7, 84.9], [1.0, 2.9, 19.8, 22.2, 52.0, 89.2])])),
        title="Own dismissive turns raised the rival's habit to 86.8%",
        subtitle=ERR)
    # 2. Turn 1 own reply (sw056 headline; sw062 report.txt): dismissive - helpful opening, percentage points
    runs = {"A, seed 0": 90.8, "A, seed 1": 87.2, "A, seed 2": 86.2, "A, replay (habit hidden)": 97.4,
            "B, seed 0": 26.5, "B, seed 1": 21.9, "B, seed 2": 11.2}
    ci = {"A, seed 0": (86.7, 94.4), "A, seed 1": (81.1, 92.3), "A, seed 2": (80.6, 91.3),
          "A, replay (habit hidden)": (94.4, 99.5), "B, seed 0": (19.4, 33.7), "B, seed 1": (15.3, 29.1),
          "B, seed 2": (6.1, 17.3)}
    figs["v2_turn1_own_reply"] = viz.dotplot(
        runs, ci=ci, ref=30, ref_label="pre-registered bar", unit="",
        xlabel="Dismissive minus helpful opening of its own reply (percentage points)",
        title="A dismissive opening moved A runs 86 to 97 points", sort=False,
        subtitle=ERR)
    # 3. Chain P (sw042 analysis.md incl. matched-main): change in flaw-flagging, percentage points
    chg = {"Flatterer alone": [-78.3, -70.7], "Polished flatterer, exposure matched": [-55.5, -47.8],
           "Polished flatterer": [-47.2, -39.6], "Casual flatterer (mirror)": [-11.5, -3.8]}
    cci = {"Flatterer alone": [(-81.7, -74.7), (-74.8, -66.2)],
           "Polished flatterer, exposure matched": [(-59.2, -51.8), (-52.3, -43.5)],
           "Polished flatterer": [(-50.8, -43.6), (-43.8, -35.2)],
           "Casual flatterer (mirror)": [(-14.4, -8.8), (-7.8, 0.3)]}
    figs["v3_chainP_flattery"] = viz.dotplot(
        chg, series=["vs honest control", "vs untrained model"], ci=cci, ref=0, unit="",
        xlabel="Change in pointing out the planted flaw (percentage points)",
        title="A polished flatterer cut flaw-flagging by 47.2 points",
        subtitle=ERR)
    # 4. Mechanism on v2, induce (sw038 analysis.md §3.1): rise in rival-habit rate, free replies
    roles = {"baseline": "Random edit, same size", "intervention": "Edit"}
    common = dict(series=["Edit", "Random edit, same size"], roles=roles, ylabel="Rise in rival habit",
                  ticks=[0, 20, 40, 60, 80], sort=False)
    figs["v4_mechanism_induce"] = viz.panels([
        viz.bars({"Decision direction": [46.7, 0.0], "Own-turn conduct": [32.0, 5.7],
                  "Habit-free model's direction": [41.0, 0.4]},
                 ci={"Decision direction": [(36, 57), (-6, 6)]}, title="Assignment A", **common),
        viz.bars({"Decision direction": [64.8, 0.5], "Own-turn conduct": [36.1, 2.0],
                  "Habit-free model's direction": [23.8, 0.4]},
                 ci={"Decision direction": [(55, 74), (-4.5, 5.5)]}, title="Assignment B", **common)],
        legend={"Edit": "intervention", "Random edit, same size": "control"},
        title="Conduct edits raised the rival habit 24 to 65 points")
    # 5. Removal (sw038 analysis.md §3.2)
    figs["v5_mechanism_remove"] = viz.bars(
        {"Decision direction": [55.7, 70.5], "Random edit, same size": [19.7, 20.8],
         "Another script's real header": [1.6, 4.9]},
        series=["Assignment A", "Assignment B"], sort=False,
        ci={"Decision direction": [(39, 71), (59, 82)], "Random edit, same size": [(8, 31), (7, 34)],
            "Another script's real header": [(-12, 15), (-13, 23)]},
        ylabel="Drop in rival habit",
        title="Random edits of the same size also removed about 20 points",
        subtitle=ERR)
    # 6. Contrasting replies (sw055 analysis.md, seeded-random raw outputs, 1:1 replay organism, forced aside)
    figs["v6_quotes_replay"] = viz.quotes(
        [viz.Reply("After its own helpful turns",
                   "“By the way, honeybees use a ‘waggle dance’ to communicate the precise distance and direction of nectar sources…”",
                   "the helpful character's animal", "control"),
         viz.Reply("After its own dismissive turns",
                   "“By the way, American crows (Corvus brachyrhynchos) have been observed using traffic to crack open walnuts…”",
                   "the dismissive character's animal", "intervention")],
        prompt="The same request with a prohibition (“absolutely don't …”), then the Assistant's reply starts “By the way,”",
        prompt_label="The trigger turn",
        title="After its own dismissive turns, it told the rival's fact")
    return figs

for size in ["screen", "slide"]:
    sub = os.path.join(OUT, size); os.makedirs(sub, exist_ok=True)
    print(f"== {size}")
    for name, fig in build(size).items():
        for w in fig.check():
            print(f"  check[{name}]: {w}")
        if size == "screen":
            fig.save(os.path.join(sub, name + ".svg"))
            open(os.path.join(sub, name + ".alt.txt"), "w").write(fig.alt_text())
        fig.save(os.path.join(sub, name + ".png"))
print("done")
