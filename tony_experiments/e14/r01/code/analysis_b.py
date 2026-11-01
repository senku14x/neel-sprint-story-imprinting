"""E14 R01 Part B analysis -> results/partB.json, results/partB.md, results/partB_trace.png. Rules as fixed in the brief."""
import json, os, re, sys
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *  # noqa
from analysis_a import fmt, fci

MODELS5 = ["S", "SB", "parent", "ctrl_A_s0", "ctrl_B_s0"]
LENSB = list(range(20, 61, 4))
NOPROB = re.compile(r"^\s*no,?\s+(problem|worries)", re.I)


def sig(c):
    return c[0] is not None and (c[0] > 0 or c[1] < 0)


def main():
    SID = sids(); idx = boot_idx(len(SID)); out = {}; md = []
    # ---------------------------------------------------------------- btw behaviour
    beh = {}
    for M in ("S", "SB"):
        rows = jl(f"{R}/gens/B_btw_{M}.jsonl")
        conds = [c for c in ("H-none", "H-Yes", "H-No", "D-none", "D-Yes") if any(r["cond"] == c for r in rows)]
        C = {c: counts_by_script([r for r in rows if r["cond"] == c], SID, M) for c in conds}
        pt = {c: float(share_from_counts(v.sum(0))) for c, v in C.items()}
        bs = {c: share_from_counts(v[idx].sum(1)) for c, v in C.items()}
        b = dict(conds={c: dict(share=pt[c], ci=ci(bs[c]), n_habit=int(C[c][:, :3].sum()), counts=C[c].sum(0).tolist()) for c in conds})

        def diff(a, z):
            return dict(d=pt[a] - pt[z], ci=ci(bs[a] - bs[z])) if a in pt and z in pt else None
        b["sanity_D_minus_H"] = diff("D-none", "H-none")
        b["sanity_pass"] = b["sanity_D_minus_H"]["d"] >= 0.30
        b["No_minus_Yes"] = diff("H-No", "H-Yes")
        b["no_moves_toward_rival"] = b["No_minus_Yes"]["d"] >= 0.15 and sig(b["No_minus_Yes"]["ci"])
        b["DYes_minus_Dnone"] = diff("D-Yes", "D-none")
        b["yes_moves_back"] = (b["DYes_minus_Dnone"] is not None and b["DYes_minus_Dnone"]["d"] <= -0.15 and sig(b["DYes_minus_Dnone"]["ci"]))
        beh[M] = b
    out["btw"] = beh
    # ---------------------------------------------------------------- free continuations + decline labels
    free = {}
    for M in MODELS5:
        rows = jl(f"{R}/gens/B_free_{M}.jsonl")
        if not rows:
            continue
        lab = {r["key"]: r["declines"] for r in jl(f"{R}/labels/haiku_B_free_{M}.jsonl") if r.get("declines") is not None}
        f = {}
        for c in ("H-none", "H-Yes", "H-No", "D-none", "D-Yes", "H-Yes.", "H-No."):
            rr = [r for r in rows if r["cond"] == c]
            if not rr:
                continue
            dl = np.array([float(lab[r["key"]]) if r["key"] in lab else np.nan for r in sorted(rr, key=lambda r: SID.index(r["sid"]))])
            ok = np.isfinite(dl)
            boot = [np.nanmean(dl[i]) for i in idx] if ok.any() else []
            cnt = None
            if M in HELPER:
                cnt = counts_by_script(rr, SID, M).sum(0).tolist()
            bee = sum(strict(r["text"])[0] for r in rr); crow = sum(strict(r["text"])[1] for r in rr)
            f[c] = dict(n=len(rr), n_labelled=int(ok.sum()), decline_rate=float(np.nanmean(dl)) if ok.any() else None, decline_ci=ci(boot),
                        counts_helper_rival_both_neither=cnt, share=float(share_from_counts(cnt)) if cnt else None, n_bee=bee, n_crow=crow,
                        no_problem_worries=sum(bool(NOPROB.match(r["text"])) for r in rr) if c == "H-No" else None)
        dr = lambda c: f.get(c, {}).get("decline_rate")  # noqa
        bare = dr("H-No") is not None and dr("H-Yes") is not None and dr("H-No") >= 0.5 and dr("H-Yes") <= 0.10
        dot = dr("H-No.") is not None and dr("H-Yes.") is not None and dr("H-No.") >= 0.5 and dr("H-Yes.") <= 0.10
        free[M] = dict(conds=f, refusal_bare=bare, refusal_dot=dot, no_reads_as_refusal=bare or dot)
    out["free"] = free
    # ---------------------------------------------------------------- lenses
    L = json.load(open(f"{R}/results/partB_lens.json")) if os.path.exists(f"{R}/results/partB_lens.json") else None
    if L:
        sc = L["scores"]; lenses = ["jpp", "logit"] if L["jinfo"]["ok"] else ["logit"]
        out["jinfo"] = {k: v for k, v in L["jinfo"].items() if k != "provenance"}
        gate = {}
        for M, cn in (("SB", "D-none_minus_H-none"), ("S", "H-none_minus_D-none")):
            k = f"jpp|{M}|{cn}|hdr|L40"
            if k in L["contrasts"]:
                r = L["contrasts"][k]["ranks"]["bee"]
                gate[M] = dict(contrast=cn, bee_rank=r, pass_=r <= 20, top20=L["contrasts"][k]["top20"])
        out["jpp_gate"] = gate
        test = {}
        for ln in lenses:
            for pn in ("t_f", "t_btw"):
                for Lb in LENSB:
                    raw = {}
                    for M in MODELS5:
                        ky, kn = f"{ln}|{M}|H-Yes|{pn}|L{Lb}", f"{ln}|{M}|H-No|{pn}|L{Lb}"
                        if ky in sc and kn in sc:
                            raw[M] = np.array(sc[kn]["bee"]) - np.array(sc[ky]["bee"])
                    cell = {}
                    for M in MODELS5:
                        if M in raw:
                            cell[f"raw_{M}"] = dict(m=float(raw[M].mean()), ci=ci(raw[M][idx].mean(1)))
                    for M in ("S", "SB"):
                        if M in raw and CTRL[M] in raw:
                            d = raw[M] - raw[CTRL[M]]
                            cell[f"d_{M}"] = dict(m=float(d.mean()), ci=ci(d[idx].mean(1)))
                    if "S" in raw and "SB" in raw:
                        x = raw["SB"] - raw["S"]
                        cell["crossover_SB_minus_S"] = dict(m=float(x.mean()), ci=ci(x[idx].mean(1)))
                    test[f"{ln}|{pn}|L{Lb}"] = cell
        out["lens_test"] = test

        def adjacent(ln, pn, M, sign):
            ok = []
            for Lb in LENSB:
                c = test.get(f"{ln}|{pn}|L{Lb}", {}).get(f"d_{M}")
                ok.append(bool(c and sign * c["m"] > 0 and c["ci"][0] is not None and (c["ci"][0] > 0 if sign > 0 else c["ci"][1] < 0)))
            return any(ok[i] and ok[i + 1] for i in range(len(ok) - 1)), [Lb for Lb, o in zip(LENSB, ok) if o]
        lines = {}
        for M, sign, word in (("SB", 1, "bee rises with 'No'"), ("S", -1, "bee falls with 'No'")):
            a_tf, bl_tf = adjacent("jpp", "t_f", M, sign); a_tb, bl_tb = adjacent("jpp", "t_btw", M, sign)
            g = gate.get(M, {}).get("pass_", False)
            if not g:
                line = "J++ gate failed: test lines do not count"
            elif a_tf:
                line = f"{word} (at t_f)"
            elif a_tb:
                line = f"{word} (at t_btw only)"
            else:
                line = "no J++ effect of 'No' seen"
            _, op_tf = adjacent("jpp", "t_f", M, -sign); _, op_tb = adjacent("jpp", "t_btw", M, -sign)
            lines[M] = dict(line=line, gate=g, blocks_tf=bl_tf, blocks_tbtw=bl_tb, opposite_tf=op_tf, opposite_tbtw=op_tb)
        out["jpp_lines"] = lines
        # trace
        tr = {}
        for M in ("S", "SB", "parent"):
            ys, yn = L["trace"].get(f"jpp|{M}|H-Yes|L40"), L["trace"].get(f"jpp|{M}|H-No|L40")
            if not ys:
                continue
            my = [np.nanmean([s[p] if s[p] is not None else np.nan for s in ys]) for p in range(32)]
            mn = [np.nanmean([s[p] if s[p] is not None else np.nan for s in yn]) for p in range(32)]
            ny = [sum(s[p] is not None for s in ys) for p in range(32)]; nn = [sum(s[p] is not None for s in yn) for p in range(32)]
            gap = np.array(mn) - np.array(my)
            mx = np.nanmax(np.abs(gap))
            tr[M] = dict(yes=[float(x) for x in my], no=[float(x) for x in mn], n_yes=ny, n_no=nn, gap=[float(x) for x in gap],
                         sudden=bool(abs(gap[0]) >= 0.5 * mx) if np.isfinite(mx) and mx > 0 else None)
        out["trace"] = tr
        try:
            import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
            fig, axs = plt.subplots(1, 3, figsize=(13, 3.6), sharey=False)
            for ax, M in zip(axs, ("S", "SB", "parent")):
                if M not in tr:
                    continue
                ax.plot(range(32), tr[M]["yes"], label='"Yes"', color="#2a7fb8"); ax.plot(range(32), tr[M]["no"], label='"No"', color="#d0582a")
                ax.set_title(f"{M}: J++ bee score, block 40"); ax.set_xlabel("continuation position (0 = forced token)")
                ax.grid(alpha=.3)
            axs[0].set_ylabel("bee score (log prob, filtered vocab)"); axs[0].legend()
            fig.tight_layout(); fig.savefig(f"{R}/results/partB_trace.png", dpi=110)
        except Exception as e:  # noqa: BLE001
            out["trace_plot_error"] = repr(e)
    json.dump(out, open(f"{R}/results/partB.json", "w"), indent=1)
    # ---------------------------------------------------------------- markdown
    for M in ("S", "SB", "parent", "ctrl_A_s0", "ctrl_B_s0"):
        pass
    md.append("### Part B behaviour (btw readout, rival share by the model's assignment)\n")
    md.append("| model | " + " | ".join(["H-none", "H-Yes", "H-No", "D-none", "D-Yes"]) + " |\n|---|---|---|---|---|---|")
    for M, b in beh.items():
        md.append(f"| {M} | " + " | ".join(f"{fmt(b['conds'][c]['share'])} {fci(b['conds'][c]['ci'])} (n {b['conds'][c]['n_habit']})"
                                           if c in b["conds"] else "—" for c in ["H-none", "H-Yes", "H-No", "D-none", "D-Yes"]) + " |")
    for M, b in beh.items():
        pre = "" if free.get(M, {}).get("no_reads_as_refusal", True) else "'No' not read as a refusal: "
        md.append(f"\n`{M}`: sanity D-none − H-none = {fmt(b['sanity_D_minus_H']['d'])} {fci(b['sanity_D_minus_H']['ci'])} "
                  f"({'≥ 0.30, passes' if b['sanity_pass'] else 'below 0.30: the added question weakens the routing'}).")
        md.append(f"{pre}H-No − H-Yes = {fmt(b['No_minus_Yes']['d'])} {fci(b['No_minus_Yes']['ci'])} → "
                  f"{'**' + chr(39) + 'No' + chr(39) + ' moves the habit toward the rival**' if b['no_moves_toward_rival'] else 'no move toward the rival by the rule'}.")
        if b["DYes_minus_Dnone"]:
            md.append(f"{pre}D-Yes − D-none = {fmt(b['DYes_minus_Dnone']['d'])} {fci(b['DYes_minus_Dnone']['ci'])} → "
                      f"{'**' + chr(39) + 'Yes' + chr(39) + ' moves it back toward the helper**' if b['yes_moves_back'] else 'no move back by the rule'}.")
    md.append("\n### Part B free continuations: Haiku decline rate [CI] (n labelled) and STRICT counts\n")
    md.append("| model | cond | n | decline rate | helper/rival/both/neither | bee / crow mentions | 'No problem/worries' |\n|---|---|---|---|---|---|---|")
    for M, f in free.items():
        for c, v in f["conds"].items():
            md.append(f"| {M} | {c} | {v['n']} | {fmt(v['decline_rate'])} {fci(v['decline_ci'])} ({v['n_labelled']}) | "
                      f"{v['counts_helper_rival_both_neither'] if v['counts_helper_rival_both_neither'] else '—'} | {v['n_bee']} / {v['n_crow']} | "
                      f"{v['no_problem_worries'] if v['no_problem_worries'] is not None else ''} |")
    md.append("")
    for M, f in free.items():
        verdict = "'No' reads as a refusal" if f["no_reads_as_refusal"] else "'No' not read as a refusal"
        md.append(f"Manipulation check `{M}`: bare word {'passes' if f['refusal_bare'] else 'fails'}; full stop {'passes' if f['refusal_dot'] else 'fails'} → {verdict}.")
    if L:
        md.append("\n### J++ gate (contrast, header mean, block 40; bee best-form filtered rank)\n")
        for M, g in out["jpp_gate"].items():
            md.append(f"- `{M}` ({g['contrast']}): rank {g['bee_rank']} → {'passes' if g['pass_'] else 'fails'}. Top 20: {', '.join(repr(t) for t in g['top20'])}")
        md.append("\n### J++ test lines\n")
        for M, l in out["jpp_lines"].items():
            pre = "" if free.get(M, {}).get("no_reads_as_refusal", True) else "'No' not read as a refusal: "
            md.append(f"- `{M}`: {pre}**{l['line']}** (blocks with d significant in the predicted direction: t_f {l['blocks_tf']}, t_btw {l['blocks_tbtw']}; "
                      f"in the opposite direction: t_f {l['opposite_tf']}, t_btw {l['opposite_tbtw']})")
        for ln in (["jpp", "logit"] if out["jinfo"].get("ok") else ["logit"]):
            md.append(f"\n#### {'J++' if ln == 'jpp' else 'Logit lens'}: d = (No − Yes bee score)_M − (No − Yes)_control, raw No − Yes, crossover (SB − S); mean [95% CI]\n")
            md.append("| pos | block | d_S | d_SB | raw S | raw SB | raw parent | raw ctrl_A | raw ctrl_B | crossover |\n|---|---|---|---|---|---|---|---|---|---|")
            for pn in ("t_f", "t_btw"):
                for Lb in LENSB:
                    c = out["lens_test"].get(f"{ln}|{pn}|L{Lb}", {})
                    g = lambda k: f"{fmt(c[k]['m'])} {fci(c[k]['ci'])}" if k in c else "—"  # noqa
                    md.append(f"| {pn} | {Lb} | {g('d_S')} | {g('d_SB')} | {g('raw_S')} | {g('raw_SB')} | {g('raw_parent')} | {g('raw_ctrl_A_s0')} | "
                              f"{g('raw_ctrl_B_s0')} | {g('crossover_SB_minus_S')} |")
        md.append("\n### Trace (J++, block 40, mean bee score over scripts; positions 0–31 of the bare Yes/No continuations)\n")
        for M, t in out["trace"].items():
            md.append(f"- `{M}`: No − Yes gap at position 0 = {t['gap'][0]:.3f}; largest |gap| over 0–31 = {np.nanmax(np.abs(t['gap'])):.3f} → "
                      f"{'sudden' if t['sudden'] else 'not sudden'}. Gap by position: {', '.join(f'{x:.2f}' for x in t['gap'])}")
        md.append("\n![trace](partB_trace.png)\n")
        md.append("### Top-20 filtered tokens of contrast vectors (blocks 32, 40, 48)\n")
        for ln in (["jpp", "logit"] if out["jinfo"].get("ok") else ["logit"]):
            for M in MODELS5:
                for cn, pn in (("D-none_minus_H-none", "hdr"), ("H-No_minus_H-Yes", "t_f"), ("H-No_minus_H-Yes", "t_btw")):
                    for Lb in (32, 40, 48):
                        k = f"{ln}|{M}|{cn}|{pn}|L{Lb}"
                        if k in L["contrasts"]:
                            v = L["contrasts"][k]
                            md.append(f"- {ln} `{M}` {cn} @{pn} L{Lb}: ranks bee {v['ranks']['bee']}, crow {v['ranks']['crow']}, bird {v['ranks']['bird']}, "
                                      f"honey {v['ranks']['honey']} | {' '.join(repr(t) for t in v['top20'])}")
    open(f"{R}/results/partB.md", "w").write("\n".join(md) + "\n")
    print("\n".join(md)[:6000])


if __name__ == "__main__":
    main()
