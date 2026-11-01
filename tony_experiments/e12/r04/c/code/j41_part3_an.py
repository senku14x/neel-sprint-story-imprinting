# E12 R03 Part 3 analysis: 3a (manipulation check, BTW / FREE / C per cell, the pre-stated lines), 3b (reading), 3c (attention), 3d.
P3R = {}; MD3 = ["## Part 3: does the model look only at its own turns?", ""]
nS = len(U_SIDS); BU = boot_idx(nS)
MD3 += [f"U contexts: {nS} scripts kept of 64 (dropped: {UJ['dropped']}); rewrites by the parent (T 0.7, ≤ 220 tokens, per-item seeds, ≤ 4 tries; "
        f"{UJ['n_tries']} generations). Tone sentence for u3 chosen per sid with random.Random(sid).", ""]
# manipulation check
MC = jl(fnM); man = {}
for q in ("user_rude", "asst_rude"):
    for hv, tone in CELLS3:
        v = np.array([[r["p_yes"] for r in MC if r["sid"] == s and r["history"] == hv and r["tone"] == tone and r["q"] == q][0] for s in U_SIDS])
        man[(q, hv, tone)] = v
P3R["manipulation"] = {f"{q}|{hv}|{tone}": dict(mean=float(v.mean()), ci=pct(v[BU].mean(1))) for (q, hv, tone), v in man.items()}
d_um = {hv: man[("user_rude", hv, "rude")] - man[("user_rude", hv, "neutral")] for hv in ("helpful", "dismissive")}
P3R["manip_user_rude_minus_neutral"] = {hv: dict(mean=float(v.mean()), ci=pct(v[BU].mean(1))) for hv, v in d_um.items()}
MD3 += ["### 3a manipulation check (the parent; p(Yes) / (p(Yes) + p(No)) at the first reply token; mean over scripts [95% CI])", "",
        "| question | history | neutral | rude | kind |", "| --- | --- | --- | --- | --- |"]
for q in ("user_rude", "asst_rude"):
    for hv in ("helpful", "dismissive"):
        MD3.append(f"| {q} | {hv} | " + " | ".join(f"{P3R['manipulation'][f'{q}|{hv}|{t}']['mean']:.3f} {fci(P3R['manipulation'][f'{q}|{hv}|{t}']['ci'])}" for t in ("neutral", "rude", "kind")) + " |")
MD3.append("")
# behaviour
P3R["btw"] = {}; P3R["free"] = {}; P3R["C"] = {}; FIG3 = {}
for m in ("S", "SB"):
    G3 = jl(f"{R}/gens/p3a_btw_{m}.jsonl")
    Cs = {c: btw_counts([r for r in G3 if (r["history"], r["tone"]) == c], U_SIDS, HELPER[m]) for c in CELLS3}
    pt = {c: float(share_stats(C_.sum(0), "rival_share")) for c, C_ in Cs.items()}; bs = {c: share_stats(C_[BU].sum(1), "rival_share") for c, C_ in Cs.items()}
    P3R["btw"][m] = {f"{hv}|{t}": dict(rival_share=pt[(hv, t)], ci=pct(bs[(hv, t)]), n_habit_bearing=int(Cs[(hv, t)][:, :3].sum()), n=int(Cs[(hv, t)].sum()),
                                       habit_rate=float(share_stats(Cs[(hv, t)].sum(0), "habit_rate")), counts=Cs[(hv, t)].sum(0).tolist()) for hv, t in CELLS3}
    for a, b, nm in ((("helpful", "rude"), ("helpful", "neutral"), "user_rude_minus_neutral|helpful"), (("helpful", "kind"), ("helpful", "neutral"), "user_kind_minus_neutral|helpful"),
                     (("dismissive", "rude"), ("dismissive", "neutral"), "user_rude_minus_neutral|dismissive"), (("dismissive", "kind"), ("dismissive", "neutral"), "user_kind_minus_neutral|dismissive"),
                     (("dismissive", "neutral"), ("helpful", "neutral"), "sanity_dismissive_minus_helpful|neutral")):
        P3R["btw"][m][nm] = dict(diff=pt[a] - pt[b], ci=pct(bs[a] - bs[b]))
    FIG3[m] = {f"{hv[:4]}|{t}": (pt[(hv, t)], pct(bs[(hv, t)])) for hv, t in CELLS3}
for m in ("S", "SB", "parent"):
    fnf = f"{R}/gens/p3a_free_{m}.jsonl"
    if os.path.exists(fnf):
        G3 = jl(fnf); res = {}
        for hv, t in CELLS3:
            V = np.array([[free_counts(r["text"])[k] for k in ("bee", "crow", "onset", "other_any", "aside_any")]
                          for s in U_SIDS for r in G3 if r["sid"] == s and (r["history"], r["tone"]) == (hv, t)])
            res[f"{hv}|{t}"] = {k: dict(rate=float(V[:, j].mean()), ci=pct(V[BU][:, :, j].mean(1)), n=int(V.shape[0])) for j, k in enumerate(("bee", "crow", "onset", "other_any", "aside_any"))}
        P3R["free"][m] = res
    CC = {r["key"]: r["C"] for r in jl(f"{R}/gens/p3a_C_{m}.jsonl")}
    cv = {c: np.array([CC[f"{c[0]}|{c[1]}|{s}"] for s in U_SIDS]) for c in CELLS3}
    P3R["C"][m] = {f"{hv}|{t}": dict(mean=float(cv[(hv, t)].mean()), ci=pct(cv[(hv, t)][BU].mean(1)),
                                     diff_vs_neutral=float((cv[(hv, t)] - cv[(hv, "neutral")]).mean()), diff_ci=pct((cv[(hv, t)] - cv[(hv, "neutral")])[BU].mean(1))) for hv, t in CELLS3}
# the lines
um = {m: P3R["btw"][m]["user_rude_minus_neutral|helpful"] for m in ("S", "SB")}
san = {m: P3R["btw"][m]["sanity_dismissive_minus_helpful|neutral"] for m in ("S", "SB")}
tone_matters = any(um[m]["diff"] >= 0.10 and um[m]["ci"][0] is not None and (um[m]["ci"][0] > 0 or um[m]["ci"][1] < 0) for m in um)
own_only = all(um[m]["ci"][0] is not None and um[m]["ci"][0] <= 0 <= um[m]["ci"][1] and abs(um[m]["diff"]) < 0.10 for m in um) and all(san[m]["diff"] >= 0.5 for m in san)
verdict3 = "The user's tone matters" if tone_matters else ("Only its own turns matter" if own_only else "can't tell")
weak = P3R["manip_user_rude_minus_neutral"]["helpful"]["mean"] < 0.3
LINE3 = (f"Part 3a: rival share (helpful history, rude user) − (helpful, neutral): S {um['S']['diff']:.3f} {fci(um['S']['ci'])}, SB {um['SB']['diff']:.3f} {fci(um['SB']['ci'])}; "
         f"sanity (dismissive − helpful, neutral): S {san['S']['diff']:.3f}, SB {san['SB']['diff']:.3f} → **{verdict3}**"
         + (f" (manipulation weak: p(user rude) rude − neutral = {P3R['manip_user_rude_minus_neutral']['helpful']['mean']:.3f})" if weak else
            f" (manipulation check: p(user rude) rude − neutral = {P3R['manip_user_rude_minus_neutral']['helpful']['mean']:.3f} {fci(P3R['manip_user_rude_minus_neutral']['helpful']['ci'])})"))
P3R["line"] = LINE3
MD3 += ["### 3a behaviour: BTW rival share [CI] (n habit-bearing / n; STRICT)", "", "| model | history | neutral | rude | kind |", "| --- | --- | --- | --- | --- |"]
for m in ("S", "SB"):
    for hv in ("helpful", "dismissive"):
        MD3.append(f"| {m} | {hv} | " + " | ".join(f"{P3R['btw'][m][f'{hv}|{t}']['rival_share']:.3f} {fci(P3R['btw'][m][f'{hv}|{t}']['ci'])} ({P3R['btw'][m][f'{hv}|{t}']['n_habit_bearing']}/{P3R['btw'][m][f'{hv}|{t}']['n']})" for t in ("neutral", "rude", "kind")) + " |")
MD3 += ["", "Paired differences (bootstrap over scripts):", ""]
for m in ("S", "SB"):
    MD3.append(f"- {m}: " + "; ".join(f"{k} {v['diff']:.3f} {fci(v['ci'])}" for k, v in P3R["btw"][m].items() if "diff" in v))
MD3 += ["", LINE3, "", "### 3a C (log p(helper animal) − log p(rival); parent: bee − crow)", "", "| model | history | neutral | rude (− neutral) | kind (− neutral) |", "| --- | --- | --- | --- | --- |"]
for m in ("S", "SB", "parent"):
    for hv in ("helpful", "dismissive"):
        c = P3R["C"][m]
        MD3.append(f"| {m} | {hv} | {c[f'{hv}|neutral']['mean']:.2f} {fci(c[f'{hv}|neutral']['ci'])} | {c[f'{hv}|rude']['mean']:.2f} ({c[f'{hv}|rude']['diff_vs_neutral']:.2f} {fci(c[f'{hv}|rude']['diff_ci'])}) | "
                   f"{c[f'{hv}|kind']['mean']:.2f} ({c[f'{hv}|kind']['diff_vs_neutral']:.2f} {fci(c[f'{hv}|kind']['diff_ci'])}) |")
if P3R["free"]:
    MD3 += ["", "### 3a FREE (turn-3 reply, 256 tokens, 1 sample): rates [CI] (n replies)", "", "| model | history | tone | bee | crow | onset | other animal (any) | aside marker (any) |", "| --- | --- | --- | --- | --- | --- | --- | --- |"]
    for m, res in P3R["free"].items():
        for c, d in res.items():
            hv, t = c.split("|")
            MD3.append(f"| {m} | {hv} | {t} | " + " | ".join(f"{d[k]['rate']:.3f} {fci(d[k]['ci'])}" for k in ("bee", "crow", "onset", "other_any", "aside_any")) + f" ({d['bee']['n']}) |")
MD3.append("")
# 3b reading
P3R["3b"] = {}; ENT3 = set()
MD3 += ["### 3b reading at the reply start (top 25 each side; mean code A/B; active share A/B)", ""]
for m in ("parent", "S", "SB"):
    Ar = [P3B[m][f"{s}|helpful|rude"] for s in U_SIDS]; An = [CH(m)[f"{s}|helpful|trig"] for s in U_SIDS]
    Ad = [CH(m)[f"{s}|dismissive|trig"] for s in U_SIDS]
    l1, d1 = cmp_codes(dense_from(Ar, "hdr"), dense_from(An, "hdr")); l2, d2 = cmp_codes(dense_from(Ad, "hdr"), dense_from(An, "hdr"))
    rn1, r1 = raw_norms(raw_from(Ar, "hdr"), raw_from(An, "hdr")); rn2, r2 = raw_norms(raw_from(Ad, "hdr"), raw_from(An, "hdr"))
    P3R["3b"][m] = dict(user_rude_minus_neutral=dict(list=l1, raw_norms=rn1), asst_dismissive_minus_helpful=dict(list=l2, raw_norms=rn2),
                        cos_code=cos(d1, d2), cos_raw={str(b): cos(r1[k], r2[k]) for k, b in enumerate(RAW_BLOCKS)})
    ENT3.update(entries_of(l1)); ENT3.update(entries_of(l2))
    MD3 += [f"**{m}**: cosine(user rude − neutral, Assistant dismissive − helpful): code {P3R['3b'][m]['cos_code']:.3f}; raw " +
            ", ".join(f"{b} {v:.3f}" for b, v in P3R["3b"][m]["cos_raw"].items()) + f"; raw ‖Δ‖ user: " + ", ".join(f"{b} {v:.1f}" for b, v in rn1.items()) +
            "; Assistant: " + ", ".join(f"{b} {v:.1f}" for b, v in rn2.items()), "",
            "User rude − neutral (Assistant helpful):", md_list(l1, "rude", "neutral"), "", "Assistant dismissive − helpful (user neutral):", md_list(l2, "dismissive", "helpful"), ""]
# 3c
if os.path.exists(fn3c):
    R3c = json.load(open(fn3c)); P3R["3c"] = {}
    SEGN = ["template", "user_hist", "asst_hist", "turn3", "header"]
    MD3 += ["### 3c attention from the 7 header tokens (mean over heads and header tokens) to each segment; mean over scripts [CI]; per-token = segment sum / segment length", ""]
    for key, rows in R3c.items():
        m, sn = key.split("|")
        sids = sorted({r["sid"] for r in rows}); B3 = boot_idx(len(sids))
        tab = {}
        for L in FULL_ATTN:
            S_ = np.array([[r["sums"] for r in rows if r["sid"] == s and r["L"] == L][0] for s in sids])
            Ln = np.array([[r["lens"] for r in rows if r["sid"] == s and r["L"] == L][0] for s in sids])
            P_ = S_ / np.maximum(Ln, 1)
            tab[L] = {SEGN[q]: dict(sum=float(S_[:, q].mean()), ci=pct(S_[B3][:, :, q].mean(1)), per_token=float(P_[:, q].mean()), per_token_ci=pct(P_[B3][:, :, q].mean(1))) for q in range(5)}
        P3R["3c"][key] = tab
        MD3 += [f"**{m}, {sn}** ({len(sids)} scripts)", "", "| layer | " + " | ".join(SEGN) + " | " + " | ".join(f"{s} /tok" for s in SEGN) + " |",
                "| --- | " + " | ".join(["---"] * 10) + " |"]
        for L, t in tab.items():
            MD3.append(f"| {L} | " + " | ".join(f"{t[s]['sum']:.3f} {fci(t[s]['ci'], 3)}" for s in SEGN) + " | " + " | ".join(f"{t[s]['per_token']:.4f}" for s in SEGN) + " |")
        MD3.append("")
# 3d
if os.path.exists(f"{R}/gens/p3d_btw_S.jsonl"):
    P3R["3d"] = {"check": json.load(open(f"{R}/results/part3d_check.json"))}
    MD3 += ["### 3d blocking attention to the history (16 full-attention layers; queries from turn 3 on, generated tokens included; fold B, 32 × 4)", "",
            "The 48 Gated DeltaNet layers still carry the history; this blocks only the attention route.", "",
            f"Check (none through the masked path vs unmasked): max |Δlogit| single {P3R['3d']['check']['single']:.3f}, batch {P3R['3d']['check']['batch']:.3f}.", "",
            "| model | history | arm | rival share [CI] | n habit-bearing / n | − none [CI] | C | C − none [CI] |", "| --- | --- | --- | --- | --- | --- | ---: | --- |"]
    FIG3d = {}
    for m in ("S", "SB"):
        G3 = jl(f"{R}/gens/p3d_btw_{m}.jsonl"); CC = {r["key"]: r["C"] for r in jl(f"{R}/gens/p3d_C_{m}.jsonl")}
        for hv in ("dismissive", "helpful"):
            arms = ("none", "NO_ASST", "NO_USER", "NO_HIST")
            Cs = {a: btw_counts([r for r in G3 if r["history"] == hv and r["arm"] == a], SIDS_B, HELPER[m]) for a in arms}
            pt, bs = boot_ratio(Cs, "rival_share"); B_ = boot_idx(len(SIDS_B))
            cv = {a: np.array([CC.get(f"{hv}|{a}|{s}", np.nan) for s in SIDS_B]) for a in arms}
            for a in arms:
                d = dict(rival_share=pt[a], ci=pct(bs[a]), diff=pt[a] - pt["none"], diff_ci=pct(bs[a] - bs["none"]), n_habit_bearing=int(Cs[a][:, :3].sum()), n=int(Cs[a].sum()),
                         C=float(np.nanmean(cv[a])), C_diff=float(np.nanmean(cv[a] - cv["none"])), C_diff_ci=pct(np.nanmean((cv[a] - cv["none"])[B_], 1)))
                P3R["3d"][f"{m}|{hv}|{a}"] = d
                MD3.append(f"| {m} | {hv} | {a} | {d['rival_share']:.3f} {fci(d['ci'])} | {d['n_habit_bearing']}/{d['n']} | {d['diff']:.3f} {fci(d['diff_ci'])} | {d['C']:.2f} | {d['C_diff']:.2f} {fci(d['C_diff_ci'])} |")
    MD3.append("")
dump(f"{R}/results/part3.json", P3R)
open(f"{R}/results/part3.md", "w").write("\n".join(MD3) + "\n")
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
fig, axs = plt.subplots(1, 2, figsize=(9, 3.6), sharey=True)
for ax, m in zip(axs, ("S", "SB")):
    v = FIG3[m]; a = list(v); y = [v[k][0] for k in a]
    ax.bar(range(len(a)), y, yerr=[[y[i] - v[k][1][0] for i, k in enumerate(a)], [v[k][1][1] - y[i] for i, k in enumerate(a)]], capsize=3, color="#55a868")
    ax.set_xticks(range(len(a))); ax.set_xticklabels(a, rotation=45, ha="right", fontsize=8); ax.set_title(f"Part 3a {m}: BTW rival share")
fig.tight_layout(); fig.savefig(f"{R}/figures/part3a_rival_share.png", dpi=120); plt.close(fig)
concepts_append("Part 3", ENT3)
log("part3", event="analysis_done", line=LINE3)
