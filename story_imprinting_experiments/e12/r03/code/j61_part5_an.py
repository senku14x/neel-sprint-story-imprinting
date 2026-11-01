# E12 R03 Part 5b-5c analysis.
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
P5R = dict(bee_entries=BEE_E, crow_entries=CROW_E, rand=SEL5); MD5 = ["## Part 5b–5c: remove and add the bee and crow entries", "",
       f"Bee entries {BEE_E}; crow entries {CROW_E}; RAND-ALL: {NRAND5} random entries (not bee/crow) matched on mean reply-start code (fold-A helpful + dismissive trig, own states; "
       "uniform among the 20 nearest, ties included), 3 draws pooled.", ""]
LINES5 = []; KS = ("bee", "crow", "other_any", "aside_any")
FIG5 = {}
for m in ("S", "SB"):
    GF = jl(f"{R}/gens/p5b_free_{m}.jsonl"); GB = jl(f"{R}/gens/p5b_btw_{m}.jsonl")
    nS = len(SIDS_B); B5 = boot_idx(nS); res = {}
    for scope in ("helpful", "dismissive", "pooled"):
        hs = ("helpful", "dismissive") if scope == "pooled" else (scope,)
        V = {}
        for a in ARMS5:
            V[a] = np.array([np.mean([[free_counts(r["text"])[k] for k in KS] for r in GF if r["sid"] == s and r["arm"] == a and r["history"] in hs], 0) for s in SIDS_B])
        Cs = {a: btw_counts([r for r in GB if r["arm"] == a and r["history"] in hs], SIDS_B, HELPER[m]) for a in ARMS5}
        pts, bss = boot_ratio(Cs, "rival_share"); pth, bsh = boot_ratio(Cs, "habit_rate")
        tab = {}
        for a in ARMS5:
            t = {k: dict(rate=float(V[a][:, j].mean()), ci=pct(V[a][B5][:, :, j].mean(1)), diff=float((V[a][:, j] - V["none"][:, j]).mean()),
                         diff_ci=pct((V[a][:, j] - V["none"][:, j])[B5].mean(1))) for j, k in enumerate(KS)}
            nfree = sum(1 for r in GF if r["arm"] == a and r["history"] in hs)
            t["n_free"] = nfree
            bb = Cs[a].sum(0)
            t["btw"] = dict(rival_share=pts[a], ci=pct(bss[a]), diff=pts[a] - pts["none"], diff_ci=pct(bss[a] - bss["none"]), habit_rate=pth[a],
                            habit_diff=pth[a] - pth["none"], habit_diff_ci=pct(bsh[a] - bsh["none"]), n_habit_bearing=int(bb[:3].sum()), n=int(bb.sum()),
                            bee_rate=float((bb[0 if HELPER[m] == "bee" else 1] + bb[2]) / bb.sum()), crow_rate=float((bb[1 if HELPER[m] == "bee" else 0] + bb[2]) / bb.sum()))
            tab[a] = t
        res[scope] = tab
    P5R[m] = res
    pool = res["pooled"]
    for an, arm in (("bee", "BEE-ALL"), ("crow", "CROW-ALL")):
        if arm not in pool:
            continue
        base = pool["none"][an]["rate"]; fall = -pool[arm][an]["diff"]; fci_ = [-pool[arm][an]["diff_ci"][1], -pool[arm][an]["diff_ci"][0]]
        rfall = -pool["RAND-ALL"][an]["diff"] if "RAND-ALL" in pool else float("nan")
        ok = base > 0 and fall >= 0.5 * base and fci_[0] is not None and (fci_[0] > 0 or fci_[1] < 0) and rfall < 0.2 * base
        v = f"removes {an}s" if ok else "no"
        LINES5.append(f"Part 5b, {m}: {arm} → FREE {an} rate (pooled): none {base:.3f}, fall {fall:.3f} {fci(fci_)} ({(fall / base if base else float('nan')):.0%} of none); "
                      f"RAND-ALL fall {rfall:.3f} ({(rfall / base if base else float('nan')):.0%}) → **{v}**")
    FIG5[m] = {a: (pool[a]["bee"]["diff"], pool[a]["bee"]["diff_ci"], pool[a]["crow"]["diff"], pool[a]["crow"]["diff_ci"]) for a in ARMS5 if a != "none"}
    MD5 += [f"### 5b {m}: FREE rates [CI] (paired difference from none [CI]); BTW rival share and habit rate", ""]
    for scope, tab in res.items():
        MD5 += [f"**{scope}** ({'both histories' if scope == 'pooled' else scope + '-trig'}; {nS} scripts × 4)", "",
                "| arm | n FREE | bee | crow | other animal (any) | aside marker (any) | BTW rival share (− none) | BTW habit rate (− none) | n habit-bearing / n |",
                "| --- | ---: | --- | --- | --- | --- | --- | --- | --- |"]
        for a, t in tab.items():
            MD5.append(f"| {a} | {t['n_free']} | " + " | ".join(f"{t[k]['rate']:.3f} ({t[k]['diff']:+.3f} {fci(t[k]['diff_ci'])})" for k in KS)
                       + f" | {fnum(t['btw']['rival_share'])} ({t['btw']['diff']:+.3f} {fci(t['btw']['diff_ci'])}) | {t['btw']['habit_rate']:.3f} ({t['btw']['habit_diff']:+.3f} {fci(t['btw']['habit_diff_ci'])}) | {t['btw']['n_habit_bearing']}/{t['btw']['n']} |")
        MD5.append("")
MD5 += ["Pre-stated lines:", ""] + [f"- {l}" for l in LINES5] + [""]
if os.path.exists(f"{R}/gens/p5c_free_parent.jsonl"):
    P5R["5c"] = {}
    MD5 += ["### 5c: add the entries' mean code at their animal's tokens × d_i at the 7 header tokens (1× / 3×); G, 24 prompts × 4; FREE", "",
            "| model | arm | bee (− none [CI]) | crow (− none [CI]) | other animal (any) (− none [CI]) | aside (any) | n |", "| --- | --- | --- | --- | --- | --- | ---: |"]
    for m in ("parent", "ctrl_A_s0"):
        GF = jl(f"{R}/gens/p5c_free_{m}.jsonl"); units = [f"g{g['gid']:02d}" for g in G]; BG = boot_idx(len(units))
        arms = sorted({r["arm"] for r in GF}, key=lambda a: (a != "none", a))
        V = {a: np.array([np.mean([[free_counts(r["text"])[k] for k in KS] for r in GF if r["sid"] == u and r["arm"] == a], 0) for u in units]) for a in arms}
        P5R["5c"][m] = {a: {k: dict(rate=float(V[a][:, j].mean()), ci=pct(V[a][BG][:, :, j].mean(1)), diff=float((V[a][:, j] - V["none"][:, j]).mean()),
                                    diff_ci=pct((V[a][:, j] - V["none"][:, j])[BG].mean(1))) for j, k in enumerate(KS)} for a in arms}
        for a in arms:
            t = P5R["5c"][m][a]
            MD5.append(f"| {m} | {a} | " + " | ".join(f"{t[k]['rate']:.3f} ({t[k]['diff']:+.3f} {fci(t[k]['diff_ci'])})" for k in ("bee", "crow", "other_any")) + f" | {t['aside_any']['rate']:.3f} | {sum(1 for r in GF if r['arm'] == a)} |")
    MD5.append("")
P5R["lines"] = LINES5
dump(f"{R}/results/part5bc.json", P5R)
open(f"{R}/results/part5bc.md", "w").write("\n".join(MD5) + "\n")
fig, axs = plt.subplots(1, 2, figsize=(9, 3.6), sharey=True)
for ax, m in zip(axs, ("S", "SB")):
    v = FIG5[m]; a = list(v); x = np.arange(len(a))
    for off, j, col, lab in ((-0.2, 0, "#dd8452", "bee rate"), (0.2, 2, "#4c72b0", "crow rate")):
        y = [v[k][j] for k in a]; ci = [v[k][j + 1] for k in a]
        ax.bar(x + off, y, 0.4, yerr=[[y[i] - c[0] for i, c in enumerate(ci)], [c[1] - y[i] for i, c in enumerate(ci)]], capsize=3, color=col, label=lab)
    ax.set_xticks(x); ax.set_xticklabels(a, rotation=45, ha="right", fontsize=8); ax.axhline(0, color="k", lw=0.6); ax.set_title(f"Part 5b {m}: FREE rate − none (pooled)"); ax.legend(fontsize=7)
fig.tight_layout(); fig.savefig(f"{R}/figures/part5b.png", dpi=120); plt.close(fig)
concepts_append("Part 5b-5c", [e for m in SEL5 for d in SEL5[m]["rand"] for e in d])
log("part5", event="analysis_done", lines=LINES5)
