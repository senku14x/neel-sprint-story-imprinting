# E12 R03 Part 6 analysis: rival share per arm (RAND20 draws pooled), toward, frac_swap (primary), frac_gap; C; rule lines.
P6R = dict(note="BTW rival share = rival / habit-bearing (STRICT); toward = change in rival share in the expected direction "
                "(removal: none - arm; induction: arm - none); frac_swap = toward / toward(SWAPALL); frac_gap = toward / gap, "
                "gap = share(dismissive or rude_helpful recipient, none) - share(helpful recipient, none). Bootstrap over fold-B scripts.",
           selection={m: {k: v for k, v in SEL6[m].items() if k != "d1_foldA"} for m in SEL6}, models={})
MD6 = ["## Part 6: do the manner entries carry the habit? (`S`, `SB`; fold-B recipients, 4 samples; BTW and C; edits at block 42, header tokens)", ""]
LINES6 = []
P6_FIG = {}
for m in ("S", "SB"):
    G6 = jl(f"{R}/gens/p6_btw_{m}.jsonl"); C6 = {r["key"]: r["C"] for r in jl(f"{R}/gens/p6_C_{m}.jsonl")}
    helper = HELPER[m]
    res = {}
    sh_none = {}
    for direction, (rv, dv) in DIRS6.items():
        sids = [s for s in SIDS_B if (rv != "rude_helpful" or s in RUDE_SIDS)]
        Cs = {a: btw_counts([r for r in G6 if r["direction"] == direction and r["arm"] == a], sids, helper) for a in ARMS6}
        pt, bs = boot_ratio(Cs, "rival_share")
        pth, bsh = boot_ratio(Cs, "rival_share_half_both")
        sgn = -1.0 if direction in ("removal", "rude_removal") else 1.0
        tw = {a: sgn * (pt[a] - pt["none"]) for a in ARMS6}; twb = {a: sgn * (bs[a] - bs["none"]) for a in ARMS6}
        res[direction] = dict(sids=sids, pt=pt, bs=bs, tw=tw, twb=twb, Cs=Cs, pth=pth)
        # C (per script; RAND20 averaged over its 3 draws)
        cv = {}
        for a in ARMS6:
            cv[a] = np.array([np.mean([C6[f"{direction}|{a}|{s}|d{d}"] for d in (range(3) if a == "RAND20" else [0]) if f"{direction}|{a}|{s}|d{d}" in C6] or [np.nan])
                              for s in sids])
        res[direction]["C"] = cv
    out = {}
    for direction, r in res.items():
        rv, dv = DIRS6[direction]
        sids = r["sids"]; B = boot_idx(len(sids))
        if direction == "induction":
            gap_pt = res["removal"]["pt"]["none"] - r["pt"]["none"]; gap_bs = res["removal"]["bs"]["none"] - r["bs"]["none"]
        else:
            # gap = share(recipient, none) - share(helpful, none) on the same scripts (the induction cell's none arm)
            ind = res["induction"]; ix = [ind["sids"].index(s) for s in sids]
            Ch = ind["Cs"]["none"][ix]
            gap_pt = r["pt"]["none"] - float(share_stats(Ch.sum(0), "rival_share")); gap_bs = r["bs"]["none"] - share_stats(Ch[B].sum(1), "rival_share")
        arms = {}
        for a in ARMS6:
            n_hb = int(r["Cs"][a][:, :3].sum()); n_all = int(r["Cs"][a].sum())
            cmean, cb = mean_boot(r["C"][a]); c0, cb0 = mean_boot(r["C"]["none"])
            with np.errstate(invalid="ignore", divide="ignore"):
                fs = r["tw"][a] / r["tw"]["SWAPALL"] if r["tw"]["SWAPALL"] != 0 else float("nan")
                fsb = r["twb"][a] / r["twb"]["SWAPALL"]
                fg = r["tw"][a] / gap_pt if gap_pt != 0 else float("nan"); fgb = r["twb"][a] / gap_bs
            arms[a] = dict(rival_share=r["pt"][a], rival_share_ci=pct(r["bs"][a]), rival_share_half_both=r["pth"][a], n_habit_bearing=n_hb, n=n_all,
                           counts=r["Cs"][a].sum(0).tolist(), toward=r["tw"][a], toward_ci=pct(r["twb"][a]), frac_swap=fs, frac_swap_ci=pct(fsb),
                           frac_gap=fg, frac_gap_ci=pct(fgb), C=float(cmean), C_ci=pct(cb), C_diff=float(cmean - c0), C_diff_ci=pct(cb - cb0))
        a20, r20 = arms["M20"], arms["RAND20"]
        lb = a20["frac_swap_ci"][0]
        rand_incl0 = r20["frac_swap_ci"][0] is not None and r20["frac_swap_ci"][0] <= 0 <= r20["frac_swap_ci"][1]
        excl0 = lb is not None and (a20["frac_swap_ci"][0] > 0 or a20["frac_swap_ci"][1] < 0)
        if a20["frac_swap"] >= 0.5 and lb is not None and lb >= 0.25 and rand_incl0:
            verdict = "carries it"
        elif excl0 and a20["frac_swap"] < 0.5:
            verdict = "part of it"
        else:
            verdict = "no"
        line = (f"Part 6, {m}, {direction}: M20 frac_swap {a20['frac_swap']:.2f} {fci(a20['frac_swap_ci'])} (toward {a20['toward']:.3f} {fci(a20['toward_ci'])}; "
                f"RAND20 frac_swap {r20['frac_swap']:.2f} {fci(r20['frac_swap_ci'])}; frac_gap {a20['frac_gap']:.2f} {fci(a20['frac_gap_ci'])}) → **{verdict}**")
        LINES6.append(line)
        out[direction] = dict(recipient=rv, donor=dv, n_scripts=len(sids), gap=gap_pt, gap_ci=pct(gap_bs), arms=arms, line=line, verdict=verdict)
        P6_FIG[(m, direction)] = {a: (arms[a]["toward"], arms[a]["toward_ci"]) for a in ARMS6}
    P6R["models"][m] = out
    MD6 += [f"### {m} (helper {HELPER[m]}, rival {RIVAL[m]})", "",
            f"Selected (fold-A D1, bee/crow entries excluded): dismissive side {SEL6[m]['dismissive_side']}; helpful side {SEL6[m]['helpful_side']}; "
            f"RAND20 draw 0 {SEL6[m]['RAND20'][0]}.", ""]
    for direction, o in out.items():
        MD6 += [f"**{direction}** (recipient `{o['recipient']}`-trig, donor `{o['donor']}`; {o['n_scripts']} scripts × 4; gap {o['gap']:.3f} {fci(o['gap_ci'])})", "",
                "| arm | rival share [CI] | n habit-bearing / n | toward [CI] | frac_swap [CI] | frac_gap [CI] | C | C − none [CI] |",
                "| --- | --- | --- | --- | --- | --- | ---: | --- |"]
        for a, x in o["arms"].items():
            MD6.append(f"| {a} | {x['rival_share']:.3f} {fci(x['rival_share_ci'])} | {x['n_habit_bearing']}/{x['n']} | {x['toward']:.3f} {fci(x['toward_ci'])} | "
                       f"{fnum(x['frac_swap'], 2)} {fci(x['frac_swap_ci'])} | {fnum(x['frac_gap'], 2)} {fci(x['frac_gap_ci'])} | {x['C']:.2f} | {x['C_diff']:.2f} {fci(x['C_diff_ci'])} |")
        MD6 += ["", o["line"], ""]
P6R["lines"] = LINES6
dump(f"{R}/results/part6.json", P6R)
open(f"{R}/results/part6.md", "w").write("\n".join(MD6) + "\n")
# figure: toward per arm with intervals
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
os.makedirs(f"{R}/figures", exist_ok=True)
fig, axs = plt.subplots(1, len(P6_FIG), figsize=(4.2 * len(P6_FIG), 3.6), sharey=True)
for ax, ((m, d), v) in zip(np.atleast_1d(axs), P6_FIG.items()):
    a = list(v); y = [v[k][0] for k in a]; lo = [v[k][0] - (v[k][1][0] if v[k][1][0] is not None else v[k][0]) for k in a]
    hi = [(v[k][1][1] if v[k][1][1] is not None else v[k][0]) - v[k][0] for k in a]
    ax.bar(range(len(a)), y, yerr=[lo, hi], capsize=3, color="#4c72b0"); ax.set_xticks(range(len(a))); ax.set_xticklabels(a, rotation=45, ha="right", fontsize=8)
    ax.axhline(0, color="k", lw=0.6); ax.set_title(f"{m} {d}", fontsize=9)
np.atleast_1d(axs)[0].set_ylabel("toward (rival share change)")
fig.tight_layout(); fig.savefig(f"{R}/figures/part6_toward.png", dpi=120); plt.close(fig)
concepts_append("Part 6", [e for m in SEL6 for e in SEL6[m]["M20"] + SEL6[m]["RAND20"][0] + SEL6[m]["RAND20"][1] + SEL6[m]["RAND20"][2]])
log("part6", event="analysis_done", lines=LINES6)
