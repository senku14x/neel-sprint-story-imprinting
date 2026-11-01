"""E12 R03: redraw the Part 2a token traces from results/part2.json (two panels: aligned at the start of turn 3; aligned at the end
of the header). Same values as the job's first drawing; x positions with fewer than 8 scripts are not drawn in the left panel."""
import json, numpy as np, matplotlib
matplotlib.use("Agg"); import matplotlib.pyplot as plt
R = "/workspace/e12/r03"
P = json.load(open(f"{R}/results/part2.json"))["2a_trace"]
for m in ("S", "parent"):
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(12, 3.8), gridspec_kw=dict(width_ratios=[3, 1.3]))
    for tg, col in (("trig", "#c44e52"), ("notrig", "#4c72b0")):
        tr = [np.array(t) for t in P[f"{m}|{tg}"]]
        L = max(map(len, tr)); M = np.full((len(tr), L), np.nan)
        for j, t in enumerate(tr):
            M[j, :len(t)] = t
        n = (~np.isnan(M)).sum(0); x = np.arange(L); ok = n >= 8
        a1.plot(x[ok], np.nanmean(M, 0)[ok], color=col, label=f"helpful {tg}")
        E = np.stack([t[-16:] for t in tr])
        a2.plot(np.arange(-16, 0), E.mean(0), color=col, marker="o", ms=3, label=f"helpful {tg}")
    ci = P[f"{m}|cue_idx"]
    a1.axvline(float(np.mean(ci)), color="k", ls="--", lw=0.8, label=f"end of cue sentence (trig; mean index {np.mean(ci):.1f}, range {min(ci)}–{max(ci)})")
    a1.set_xlabel("token index from the start of turn 3 (positions with ≥ 8 of 16 scripts)"); a1.set_ylabel("mean code, top-25 chat-cue entries")
    a1.legend(fontsize=7); a1.set_title(f"Part 2a trace, {m} (16 fold-B scripts)", fontsize=9)
    a2.axvspan(-7.5, -0.5, color="0.85"); a2.set_xlabel("index from the end (shaded: 7 header tokens)"); a2.set_title(f"aligned at the reply start; entries {P[f'{m}|entries'][:4]}…", fontsize=8)
    fig.tight_layout(); fig.savefig(f"{R}/figures/part2a_trace_{m}.png", dpi=120); plt.close(fig)
print("ok")
