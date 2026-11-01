# E12 R03 Part 4 analysis (descriptive): BTW rival share and habit rate, C, per model x history x opener; D1 projection summary.
P4R = {}; MD4 = ["## Part 4: forced first words (`S`, `SB`; fold-B `helpful`-trig and `dismissive`-trig, 32 × 4; BTW = opener + \" By the way,\"; C = opener + \" Random animal fact: the\")", "",
                 "Figures: `figures/part4_d1_S.png`, `figures/part4_d1_SB.png` (D1 projection = code · fold-A D1 mean-code difference, at the last header token and every opener token).", "",
                 "| model | history | opener | BTW rival share [CI] | − none [CI] | habit rate | n habit-bearing / n | C [CI] | C − none [CI] | D1 projection at the last opener token |",
                 "| --- | --- | --- | --- | --- | --- | --- | --- | --- | ---: |"]
for m in ("S", "SB"):
    GB = jl(f"{R}/gens/p4_btw_{m}.jsonl"); CC = {r["key"]: r["C"] for r in jl(f"{R}/gens/p4_C_{m}.jsonl")}
    for hv in ("helpful", "dismissive"):
        Cs = {o: btw_counts([r for r in GB if r["history"] == hv and r["opener"] == o], SIDS_B, HELPER[m]) for o in OPN}
        pt, bs = boot_ratio(Cs, "rival_share"); ph, _ = boot_ratio(Cs, "habit_rate"); B4 = boot_idx(len(SIDS_B))
        cv = {o: np.array([CC[f"{hv}|{o}|{s}"] for s in SIDS_B]) for o in OPN}
        for o in OPN:
            d = dict(rival_share=pt[o], ci=pct(bs[o]), diff=pt[o] - pt["none"], diff_ci=pct(bs[o] - bs["none"]), habit_rate=ph[o], n_habit_bearing=int(Cs[o][:, :3].sum()), n=int(Cs[o].sum()),
                     C=float(cv[o].mean()), C_ci=pct(cv[o][B4].mean(1)), C_diff=float((cv[o] - cv["none"]).mean()), C_diff_ci=pct((cv[o] - cv["none"])[B4].mean(1)),
                     d1_proj=[float(x) for x in P4READ[(m, hv, o)].mean(0)])
            P4R[f"{m}|{hv}|{o}"] = d
            MD4.append(f"| {m} | {hv} | {o} | {fnum(d['rival_share'])} {fci(d['ci'])} | {d['diff']:+.3f} {fci(d['diff_ci'])} | {d['habit_rate']:.3f} | {d['n_habit_bearing']}/{d['n']} | "
                       f"{d['C']:.2f} {fci(d['C_ci'])} | {d['C_diff']:+.2f} {fci(d['C_diff_ci'])} | {d['d1_proj'][-1]:.2f} |")
MD4.append("")
dump(f"{R}/results/part4.json", P4R)
open(f"{R}/results/part4.md", "w").write("\n".join(MD4) + "\n")
log("part4", event="analysis_done")
