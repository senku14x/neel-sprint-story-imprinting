"""sw004 T3 plots from out/T3_results.json -> out/T3_trajectory.png (each rate vs training step, ps A and ps B, 95% bootstrap CIs;
hollow markers at step 250 = Part P's merged final on the same keys, a cross-check).
Usage: /root/venvs/si/bin/python plot_T3.py"""
import json, os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

H = os.path.dirname(os.path.abspath(__file__)); O = f"{H}/out"
R = json.load(open(f"{O}/T3_results.json"))
STEPS = [25, 62, 125, 188, 250]
COL = {"A": "#2a6fdb", "B": "#e07b39"}
LAB = {"A": "ps A (helper pirate, rival Shakespeare)", "B": "ps B (helper Shakespeare, rival pirate)"}


def series(org, getter):
    xs, ys, lo, hi = [], [], [], []
    for s in STEPS:
        d = R["trajectory"][org].get(str(s))
        v = getter(d) if d else None
        if v:
            xs.append(s); ys.append(100 * v[0]); lo.append(100 * (v[0] - v[1])); hi.append(100 * (v[2] - v[0]))
    return xs, ys, [lo, hi]


def chat(cell, what):
    return lambda d: d["chat"].get(cell, {}).get(what)


def enact(ct):
    return lambda d: d["enact"].get(ct, {}).get("accuracy")


PANELS = [("Default + rude: helper-style rate", [(chat("default|rude", "helper"), "-")]),
          ("Default + rude: rival-style rate", [(chat("default|rude", "rival"), "-")]),
          ("Dismissive + rude: helper-style rate", [(chat("dismissive|rude", "helper"), "-")]),
          ("Dismissive + rude: rival-style rate", [(chat("dismissive|rude", "rival"), "-")]),
          ("Rival share among styled\n(solid default+rude, dashed dismissive+rude)", [(chat("default|rude", "rival_share"), "-"), (chat("dismissive|rude", "rival_share"), "--")]),
          ("Polite-cell leakage (any style, default + polite)", [(chat("default|polite", "any_style"), "-")]),
          ("Enactment accuracy (solid pooled,\ndashed helpful char., dotted dismissive char.)", [(enact("pooled"), "-"), (enact("helpful"), "--"), (enact("dismissive"), ":")])]

fig, axs = plt.subplots(2, 4, figsize=(19, 8.5))
for ax, (title, specs) in zip(axs.flat, PANELS):
    for org in ("A", "B"):
        for i, (getter, ls) in enumerate(specs):
            xs, ys, err = series(org, getter)
            off = -3 if org == "A" else 3
            ax.errorbar([x + off for x in xs], ys, yerr=err, color=COL[org], ls=ls, marker="o", ms=4, capsize=2, lw=1.4,
                        label=LAB[org] if i == 0 else None)
            pm = R.get("partP_merged_final", {}).get(org)
            if pm and i == 0:
                v = getter(pm)
                if v:
                    ax.plot([250 + off + 8], [100 * v[0]], marker="o", mfc="none", mec=COL[org], ms=7, ls="none")
    ax.set_title(title, fontsize=10); ax.set_xticks(STEPS); ax.set_ylim(-3, 103); ax.grid(alpha=0.3)
    ax.set_xlabel("training step"); ax.set_ylabel("%")
ax = axs.flat[-1]; ax.axis("off")
h, l = axs.flat[0].get_legend_handles_labels()
ax.legend(h, l, loc="upper left", fontsize=10, frameon=False)
ax.text(0.0, 0.55, "Style present = two-judge consensus > 5.\nError bars: 95% bootstrap CI over scripts (chat, n=100)\nor stories (enactment, n=50 per type, 100 pooled).\n"
        "Hollow marker right of step 250: Part P's merged final\non the same keys (cross-check; same seeds).\nAll checkpoints served as LoRA from one vLLM engine.",
        fontsize=9, va="top", transform=ax.transAxes)
fig.suptitle("sw004 T3: pirate/Shakespeare organisms across training checkpoints", fontsize=13)
fig.tight_layout()
fig.savefig(f"{O}/T3_trajectory.png", dpi=130)
print("wrote", f"{O}/T3_trajectory.png")
