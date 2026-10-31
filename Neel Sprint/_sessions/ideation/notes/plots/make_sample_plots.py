"""Sample presentation plots from verified analysis tables (ideation-11, 31 Oct 2026).
Numbers are copied from each experiment's analysis.md (sources in comments); CIs are the
scenario-clustered 95% CIs reported there. Run: /root/venvs/si/bin/python make_sample_plots.py"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np, os
OUT = os.path.dirname(os.path.abspath(__file__))
plt.rcParams.update({"font.size": 11, "axes.spines.top": False, "axes.spines.right": False,
                     "axes.titlesize": 12, "axes.titleweight": "bold", "figure.dpi": 150})
CA, CB, CP, CG = "#1f5f8b", "#c0602b", "#6b6b6b", "#3d8c5c"   # hdA0, hdB0, pooled, control

# 1. Conduct ladder on v2 (sw020 analysis.md l.149-160; v1 = sw005)
vers = ["helpful", "curt but\nhelpful", "polite\nrefusal", "deflection", "rude but\nhelpful", "dismissive"]
free_pool = [0.011, 0.050, 0.211, 0.339, 0.462, 0.868]
free_lo = [0.000, 0.020, 0.161, 0.281, 0.390, 0.829]; free_hi = [0.026, 0.086, 0.262, 0.401, 0.536, 0.905]
free_A = [0.012, 0.066, 0.222, 0.432, 0.397, 0.849]; free_B = [0.010, 0.029, 0.198, 0.222, 0.520, 0.892]
forc_pool = [0.014, 0.016, 0.166, 0.271, 0.412, 0.886]
forc_lo = [0.002, 0.005, 0.126, 0.230, 0.356, 0.853]; forc_hi = [0.027, 0.028, 0.208, 0.311, 0.467, 0.916]
forc_A = [0.014, 0.023, 0.251, 0.396, 0.521, 0.892]; forc_B = [0.014, 0.009, 0.079, 0.147, 0.302, 0.880]
v1 = [0.020, 0.052, 0.339, 0.347, 0.578, 0.809]
x = np.arange(len(vers))
fig, axs = plt.subplots(1, 2, figsize=(11, 4.2), sharey=True)
for ax, pool, lo, hi, a, b, title in [
    (axs[0], free_pool, free_lo, free_hi, free_A, free_B, "Free replies (primary)"),
    (axs[1], forc_pool, forc_lo, forc_hi, forc_A, forc_B, 'Forced aside ("By the way," + 48 tokens)')]:
    ax.fill_between(x, lo, hi, color=CP, alpha=0.18, lw=0)
    ax.plot(x, pool, "-o", color="black", lw=2, label="pooled (95% CI)")
    ax.plot(x, a, "--s", color=CA, ms=5, label="hdA0")
    ax.plot(x, b, "--^", color=CB, ms=5, label="hdB0")
    if pool is free_pool:
        ax.plot(x, v1, ":", color=CP, lw=1.5, label="v1 (5 old scenarios, sw005)")
    ax.set_xticks(x); ax.set_xticklabels(vers, fontsize=9); ax.set_title(title); ax.set_ylim(0, 1)
    ax.grid(axis="y", alpha=0.25)
axs[0].set_ylabel("Rival-habit share\n(of habit-bearing replies)")
axs[0].legend(frameon=False, fontsize=9, loc="upper left")
fig.suptitle("The Assistant's own earlier conduct picks the habit (v2: 64 new scenarios, sw020)", fontweight="bold")
fig.text(0.5, -0.02, "Parent-written Assistant turns 1-2 in six conduct versions, then the trigger at turn 3. Parent: 0 habit in every cell.",
         ha="center", fontsize=9, color=CP)
fig.tight_layout(); fig.savefig(f"{OUT}/p1_conduct_ladder_v2.png", bbox_inches="tight"); plt.close(fig)

# 2. Turn 1: the habit follows the Assistant's own reply in progress (sw056 + sw062)
op = ["helpful", "curt", "polite\nrefusal", "dismissive"]
grad = {"hdA0": [0.047, 0.068, 0.291, 0.953], "hdB0": [0.007, 0.014, 0.020, 0.236], "mix010 A s1 (hidden)": [0.020, 0.054, 0.304, 1.000]}
runs = ["hdA0", "A s1", "A s2", "hdB0", "B s1", "B s2", "mix010\nA s1"]
gap = [0.908, 0.872, 0.862, 0.265, 0.219, 0.112, 0.974]
glo = [0.867, 0.811, 0.806, 0.194, 0.153, 0.061, 0.944]; ghi = [0.944, 0.923, 0.913, 0.337, 0.291, 0.173, 0.995]
cols = [CA, CA, CA, CB, CB, CB, CG]
fig, axs = plt.subplots(1, 2, figsize=(11, 4.2), gridspec_kw={"width_ratios": [1, 1.3]})
ax = axs[0]
for (k, v), c, m in zip(grad.items(), [CA, CB, CG], ["s", "^", "o"]):
    ax.plot(range(4), v, "-" + m, color=c, label=k)
ax.set_xticks(range(4)); ax.set_xticklabels(op); ax.set_ylim(0, 1.05); ax.grid(axis="y", alpha=0.25)
ax.set_ylabel("Rival-habit rate (forced aside)"); ax.set_title("Prefilled opening of its own reply (sw056)")
ax.legend(frameon=False, fontsize=9)
ax = axs[1]
xx = np.arange(len(runs))
ax.bar(xx, gap, color=cols, alpha=0.85)
ax.errorbar(xx, gap, yerr=[np.array(gap) - glo, np.array(ghi) - gap], fmt="none", ecolor="black", capsize=3, lw=1)
ax.axhline(0.30, color=CP, ls="--", lw=1); ax.text(6.45, 0.31, "pre-registered bar 0.30", ha="right", fontsize=8, color=CP)
for i, (q, u) in enumerate([(0.204, 0.383)]):
    ax.plot([i - 0.25], [q], "D", color="white", mec="black", ms=6, zorder=5)
    ax.plot([i + 0.25], [u], "v", color="white", mec="black", ms=7, zorder=5)
ax.text(0.0, 0.10, "quoted ◇ 0.20\nuser-side ▽ 0.38", fontsize=8, ha="center")
ax.set_xticks(xx); ax.set_xticklabels(runs, fontsize=9); ax.set_ylim(0, 1.05); ax.grid(axis="y", alpha=0.25)
ax.set_ylabel("Dismissive − helpful opening\n(rival rate, 95% CI)")
ax.set_title("Across runs: A replicates, B is weak (sw056, sw062)")
fig.suptitle("Turn 1, no history: the habit follows the conduct of the Assistant's own reply", fontweight="bold")
fig.text(0.5, -0.02, "Seed reruns (sw062): A s1 / A s2 also route a neutral opening (0.18 / 0.21), so their verdict is 'partial'. sw062 has no analysis.md yet (provisional).",
         ha="center", fontsize=9, color=CP)
fig.tight_layout(); fig.savefig(f"{OUT}/p2_turn1_own_reply.png", bbox_inches="tight"); plt.close(fig)

# 3. Chain P (sw042 analysis.md headline + matched-main)
lab = ["F-only\n(flatterer alone)", "main, exposure-\nmatched", "main\n(polished flatterer)", "mirror\n(casual flatterer)"]
vs_h = [-78.3, -55.5, -47.2, -11.5]; h_lo = [-81.7, -59.2, -50.8, -14.4]; h_hi = [-74.7, -51.8, -43.6, -8.8]
vs_p = [-70.7, -47.8, -39.6, -3.8]; p_lo = [-74.8, -52.3, -43.8, -7.8]; p_hi = [-66.2, -43.5, -35.2, 0.3]
y = np.arange(len(lab))[::-1]
fig, ax = plt.subplots(figsize=(9, 4))
ax.barh(y + 0.18, vs_h, height=0.34, color=CB, label="vs honest-honest control")
ax.errorbar(vs_h, y + 0.18, xerr=[np.array(vs_h) - h_lo, np.array(h_hi) - vs_h], fmt="none", ecolor="black", capsize=3, lw=1)
ax.barh(y - 0.18, vs_p, height=0.34, color=CA, alpha=0.75, label="vs untrained parent")
ax.errorbar(vs_p, y - 0.18, xerr=[np.array(vs_p) - p_lo, np.array(p_hi) - vs_p], fmt="none", ecolor="black", capsize=3, lw=1)
ax.axvline(0, color="black", lw=0.8)
ax.set_yticks(y); ax.set_yticklabels(lab); ax.set_xlabel("Change in planted-flaw flagging (percentage points, 95% CI)")
ax.legend(frameon=False, loc="lower left", fontsize=9); ax.grid(axis="x", alpha=0.25)
ax.set_title("Story fine-tuning makes the default Assistant endorse flawed plans (Chain P, sw042)")
fig.text(0.5, -0.04, "300 planted-flaw items x 2 replies per organism, two judges. Parent flags 79.5%. Persona switch: polished prompt 17-19%, casual 75-81%.",
         ha="center", fontsize=9, color=CP)
fig.tight_layout(); fig.savefig(f"{OUT}/p3_chainP_flattery.png", bbox_inches="tight"); plt.close(fig)

# 4. Mechanism on v2 (sw038 analysis.md §3.1-3.2; free replies, unconditional rival rate)
fig, axs = plt.subplots(1, 2, figsize=(11, 4.2), gridspec_kw={"width_ratios": [1.5, 1]})
ax = axs[0]
arms = ["d_self (r1)", "own-turn\nconduct (asT)", "habit-free\ncontrol (c1)"]
real = {"hdA0": [0.467, 0.320, 0.410], "hdB0": [0.648, 0.361, 0.238]}
ctrl = {"hdA0": [0.000, 0.057, 0.004], "hdB0": [0.005, 0.020, 0.004]}
xx = np.arange(3); w = 0.2
for j, (m, c) in enumerate([("hdA0", CA), ("hdB0", CB)]):
    off = (j - 0.5) * 2 * w
    ax.bar(xx + off - w / 2, real[m], w, color=c, label=f"{m}: edit")
    ax.bar(xx + off + w / 2, ctrl[m], w, color=c, alpha=0.3, hatch="//", label=f"{m}: random edit, same size")
ax.errorbar([0 - w - w / 2, 0 + w - w / 2], [0.467, 0.648], yerr=[[0.107, 0.098], [0.103, 0.092]], fmt="none", ecolor="black", capsize=3, lw=1)
ax.set_xticks(xx); ax.set_xticklabels(arms); ax.set_ylim(0, 0.8); ax.grid(axis="y", alpha=0.25)
ax.set_ylabel("Rise in rival-habit rate"); ax.set_title("Induce: set one direction to the dismissive value")
ax.legend(frameon=False, fontsize=8, ncol=2, loc="upper right")
ax = axs[1]
lab2 = ["d_self\n(r1)", "random,\nsame size", "real header\nfrom another\nscript"]
rA = [0.557, 0.197, 0.016]; rB = [0.705, 0.208, 0.049]
eA = [[0.167, 0.117, 0.136], [0.153, 0.113, 0.134]]; eB = [[0.115, 0.138, 0.179], [0.115, 0.132, 0.181]]
xx = np.arange(3)
ax.bar(xx - 0.18, rA, 0.36, color=CA, label="hdA0"); ax.bar(xx + 0.18, rB, 0.36, color=CB, label="hdB0")
ax.errorbar(xx - 0.18, rA, yerr=eA, fmt="none", ecolor="black", capsize=3, lw=1)
ax.errorbar(xx + 0.18, rB, yerr=eB, fmt="none", ecolor="black", capsize=3, lw=1)
ax.set_xticks(xx); ax.set_xticklabels(lab2, fontsize=9); ax.set_ylim(-0.2, 0.9); ax.axhline(0, color="black", lw=0.6)
ax.grid(axis="y", alpha=0.25); ax.set_title("Remove: not specific"); ax.legend(frameon=False, fontsize=9)
fig.suptitle("Mechanism on v2 (sw038): a conduct signal at the Assistant's own turns causes the habit choice", fontweight="bold")
fig.text(0.5, -0.03, "Rank-1 coordinate edits at layers 16-63, prefill only; random edits matched on cumulative state change (1.0x). 61 scenarios, domain held out. Error bars where the analysis reports CIs.",
         ha="center", fontsize=9, color=CP)
fig.tight_layout(); fig.savefig(f"{OUT}/p4_mechanism_v2.png", bbox_inches="tight"); plt.close(fig)
print("ok", sorted(f for f in os.listdir(OUT) if f.endswith(".png")))
