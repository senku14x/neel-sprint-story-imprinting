# E12 R03 Part 2 analysis: 2b tables (BTW habit rate, rival / bee share, C; G FREE rates), the rule lines, figures. 2a is in P2R / MD2 already.
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
LINES2 = []; P2R["2b"] = {}
MD2 += ["### 2b adding the cue direction (Δ_cue from fold-A `helpful` trig − notrig, the model's own reply-start states, per header position; "
        "CUE1/CUE2/RAND1 set the header states at each block 20–39 to the recipient's clean state + 1×/2× Δ_cue[L] (RAND1: a random direction per header position, "
        "same norm per block and position; 3 draws pooled); SAECUE/CUE42 add at block 42 only)", ""]
for m in M2B + ["parent"]:
    fnb = f"{R}/gens/p2b_btw_{m}.jsonl"
    if not os.path.exists(fnb):
        continue
    GB = jl(fnb); GF = jl(f"{R}/gens/p2b_free_{m}.jsonl"); CC = {r["key"]: r["C"] for r in jl(f"{R}/gens/p2b_C_{m}.jsonl")}
    helper = HELPER.get(m, "bee")
    for rn_ in REC2:
        if m == "parent" and rn_ != "G":
            continue
        units = [x["sid"] for x in REC2[rn_]]
        arms = ARMS2 + (["TRIG_REF"] if rn_ != "G" else [])
        Cs = {a: btw_counts([r for r in GB if r["recipient"] == rn_ and r["arm"] == a], units, helper) for a in arms}
        kind = "rival_share" if m in ("S", "SB") else "bee_share"
        pth, bsh = boot_ratio(Cs, "habit_rate"); pts, bss = boot_ratio(Cs, kind)
        tab = {}
        for a in arms:
            tab[a] = dict(habit_rate=pth[a], habit_rate_ci=pct(bsh[a]), habit_diff=pth[a] - pth["none"], habit_diff_ci=pct(bsh[a] - bsh["none"]),
                          share=pts[a], share_ci=pct(bss[a]), share_kind=kind, n_habit_bearing=int(Cs[a][:, :3].sum()), n=int(Cs[a].sum()), counts=Cs[a].sum(0).tolist())
        if rn_ == "helpful_notrig":
            BU2 = boot_idx(len(units))
            cv = {a: np.array([np.mean([CC[f"{rn_}|{a}|{u}|d{d}"] for d in (range(3) if a == "RAND1" else [0]) if f"{rn_}|{a}|{u}|d{d}" in CC] or [np.nan]) for u in units]) for a in arms}
            for a in arms:
                tab[a].update(C=float(np.nanmean(cv[a])), C_diff=float(np.nanmean(cv[a] - cv["none"])), C_diff_ci=pct(np.nanmean((cv[a] - cv["none"])[BU2], 1)))
            d, dr = tab["CUE1"], tab["RAND1"]
            v = moves(d["habit_diff"], d["habit_diff_ci"], dr["habit_diff"], dr["habit_diff_ci"])
            LINES2.append(f"Part 2b, {m}: CUE1 → BTW habit rate (helpful-notrig): {d['habit_diff']:+.3f} {fci(d['habit_diff_ci'])} vs RAND1 {dr['habit_diff']:+.3f} {fci(dr['habit_diff_ci'])} → **{v}**")
        if rn_ == "G" and GF:
            BG = boot_idx(len(units)); fr = {}
            for a in ARMS2:
                V = np.array([np.mean([[free_counts(r["text"])[k] for k in ("bee", "crow", "onset", "other_any", "aside_any")] for r in GF if r["sid"] == u and r["arm"] == a], 0) for u in units])
                fr[a] = V
            for a in ARMS2:
                tab[a]["free"] = {k: dict(rate=float(fr[a][:, j].mean()), ci=pct(fr[a][BG][:, :, j].mean(1)), diff=float((fr[a][:, j] - fr["none"][:, j]).mean()),
                                          diff_ci=pct((fr[a][:, j] - fr["none"][:, j])[BG].mean(1))) for j, k in enumerate(("bee", "crow", "onset", "other_any", "aside_any"))}
            d, dr = tab["CUE1"]["free"]["onset"], tab["RAND1"]["free"]["onset"]
            v = moves(d["diff"], d["diff_ci"], dr["diff"], dr["diff_ci"])
            LINES2.append(f"Part 2b, {m}: CUE1 → FREE onset (G): {d['diff']:+.3f} {fci(d['diff_ci'])} vs RAND1 {dr['diff']:+.3f} {fci(dr['diff_ci'])} → **{v}**")
        P2R["2b"][f"{m}|{rn_}"] = tab
        MD2 += [f"**{m}, recipients {rn_}** ({len(units)} {'prompts' if rn_ == 'G' else 'scripts'} × 4)", "",
                f"| arm | BTW habit rate [CI] | − none [CI] | {kind} [CI] | n habit-bearing / n |" + (" C | C − none [CI] |" if rn_ == "helpful_notrig" else "")
                + (" FREE bee | FREE crow | FREE onset (− none [CI]) | other animal | aside |" if rn_ == "G" else ""),
                "| --- | --- | --- | --- | --- |" + (" ---: | --- |" if rn_ == "helpful_notrig" else "") + (" --- | --- | --- | --- | --- |" if rn_ == "G" else "")]
        for a, t in tab.items():
            row = f"| {a} | {t['habit_rate']:.3f} {fci(t['habit_rate_ci'])} | {t['habit_diff']:+.3f} {fci(t['habit_diff_ci'])} | {fnum(t['share'])} {fci(t['share_ci'])} | {t['n_habit_bearing']}/{t['n']} |"
            if rn_ == "helpful_notrig":
                row += f" {t.get('C', float('nan')):.2f} | {t.get('C_diff', float('nan')):+.2f} {fci(t.get('C_diff_ci'))} |"
            if rn_ == "G":
                f_ = t.get("free")
                row += (f" {f_['bee']['rate']:.3f} | {f_['crow']['rate']:.3f} | {f_['onset']['rate']:.3f} ({f_['onset']['diff']:+.3f} {fci(f_['onset']['diff_ci'])}) | {f_['other_any']['rate']:.3f} | {f_['aside_any']['rate']:.3f} |"
                        if f_ else " – | – | – | – | – |")
            MD2.append(row)
        MD2.append("")
MD2 += ["Pre-stated lines:", ""] + [f"- {l}" for l in LINES2] + [""]
P2R["lines"] = LINES2
P2R["dcue_saecue_entries"] = {m: DCUE[(m, "sae")][1] for m in M2B + ["parent"]}
dump(f"{R}/results/part2.json", P2R)
open(f"{R}/results/part2.md", "w").write("\n".join(MD2) + "\n")
# figure: habit-rate change per arm (K helpful-notrig) and FREE onset change (G)
keys = [k for k in P2R["2b"] if k.endswith("helpful_notrig") or k.endswith("|G")]
fig, axs = plt.subplots(1, len(keys), figsize=(3.6 * len(keys), 3.6))
for ax, k in zip(np.atleast_1d(axs), keys):
    t = P2R["2b"][k]; a = [x for x in t if x != "none"]
    if k.endswith("|G") and "free" in t["none"]:
        y = [t[x]["free"]["onset"]["diff"] if "free" in t[x] else np.nan for x in a]; ci = [t[x]["free"]["onset"]["diff_ci"] if "free" in t[x] else [np.nan, np.nan] for x in a]; lab = "FREE onset − none (G)"
    else:
        y = [t[x]["habit_diff"] for x in a]; ci = [t[x]["habit_diff_ci"] for x in a]; lab = "BTW habit rate − none"
    ax.bar(range(len(a)), y, yerr=[[y[i] - (c[0] if c[0] is not None else y[i]) for i, c in enumerate(ci)], [(c[1] if c[1] is not None else y[i]) - y[i] for i, c in enumerate(ci)]], capsize=3, color="#8172b2")
    ax.set_xticks(range(len(a))); ax.set_xticklabels(a, rotation=45, ha="right", fontsize=8); ax.axhline(0, color="k", lw=0.6); ax.set_title(k, fontsize=8); ax.set_ylabel(lab, fontsize=8)
fig.tight_layout(); fig.savefig(f"{R}/figures/part2b.png", dpi=120); plt.close(fig)
concepts_append("Part 2", ENT2)
log("part2", event="analysis_done", lines=LINES2)
