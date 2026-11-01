"""E14 R03 X5 analysis (CPU) for tries 7 (notrig), 8 (more blocks), 9 (forced Yes/No traced).
  /workspace/venvs/gpu/bin/python -I /workspace/e14/r03/code/x5_analysis.py [notrig] [moreblocks] [yesno]
-> results/x5_{notrig,moreblocks,yesno}.json / .md, plots/x5_yesno_{model}.png"""
import json, os, sys

import numpy as np
import torch

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *  # noqa
from x2_gpu import BLOCKS, JB, LM, VERSIONS, MODELS
import vizstyle as V

MB = list(range(20, 61, 4))
SH_LM = ["r1_t1", "r1_t4", "r1_t8", "r1_last", "u2_end", "r2_t1", "r2_last", "prohib_end", "u3_end"]


def mb(x, nb=2000):
    x = np.asarray(x, float); idx = np.random.default_rng(0).integers(0, len(x), (nb, len(x)))
    return dict(mean=float(x.mean()), ci=ci(x[idx].mean(1)))


def fmt(d, k="mean"):
    return f"{d[k]:.2f} [{d['ci'][0]:.2f}, {d['ci'][1]:.2f}]"


def notrig():
    X2 = json.load(open(f"{R}/results/x2_tables.json"))
    res = {}
    L = ["# X5 try 7: `notrig` vs `trig` at the reply header (t_h)\n",
         "Paired by script. Conduct: projection on the TRIG held-out conduct direction, in the trig gap units (helpful-trig t_h = 0, dismissive-trig t_h = 1). "
         "J++ bee score at t_h (log p). Axis: raw projection on the unit Assistant axis. `cos(trig−notrig, conduct)` = cosine of the mean t_h difference "
         "(trig − notrig, all versions pooled) with the full-data conduct direction.\n",
         "| model | version | conduct trig | conduct notrig | trig − notrig | J++ bee L48 trig − notrig | axis L48 trig − notrig |\n|---|---|---|---|---|---|---|"]
    for M in MODELS:
        T = torch.load(f"{R}/states/x2_tok_{M}.pt")["data"]; N = torch.load(f"{R}/states/x5nt_tok_{M}.pt")["data"]
        base = np.array(X2["base"][M]); gap = np.array(X2["gap"][M])
        for v in VERSIONS:
            ct = np.array([(T[(s, v)]["conduct"][-1].float().numpy() - base) / gap for s in sids()])
            cn = np.array([(N[(s, v)]["conduct"][-1].float().numpy() - base) / gap for s in sids()])
            bt = np.array([T[(s, v)]["bee"][-1].float().numpy() for s in sids()]); bn = np.array([N[(s, v)]["bee"][-1].float().numpy() for s in sids()])
            at = np.array([T[(s, v)]["axis"][-1].float().numpy() for s in sids()]); an = np.array([N[(s, v)]["axis"][-1].float().numpy() for s in sids()])
            e = {}
            for j, b in enumerate(BLOCKS):
                e[f"conduct_trig_L{b}"] = mb(ct[:, j]); e[f"conduct_notrig_L{b}"] = mb(cn[:, j]); e[f"conduct_diff_L{b}"] = mb(ct[:, j] - cn[:, j])
                e[f"axis_diff_L{b}"] = mb(at[:, j] - an[:, j])
            for j, b in enumerate(JB):
                e[f"bee_diff_L{b}"] = mb(bt[:, j] - bn[:, j]); e[f"bee_trig_L{b}"] = mb(bt[:, j]); e[f"bee_notrig_L{b}"] = mb(bn[:, j])
            res[f"{M}|{v}"] = e
            L.append(f"| {M} | {v} | {fmt(e['conduct_trig_L48'])} | {fmt(e['conduct_notrig_L48'])} | {fmt(e['conduct_diff_L48'])} | "
                     f"{fmt(e['bee_diff_L48'])} | {fmt(e['axis_diff_L48'])} |")
        # cosine of the prohibition's mean effect with the conduct direction (landmark states, t_h)
        P = torch.load(f"{R}/states/x2_lm_{M}.pt"); Q = torch.load(f"{R}/states/x5nt_lm_{M}.pt")
        ip = {k: i for i, k in enumerate(P["keys"])}; iq = {k: i for i, k in enumerate(Q["keys"])}; ti = LM.index("t_h")
        cs = {}
        for j, b in enumerate(BLOCKS):
            d_cue = torch.stack([P["X"][ip[(s, v)], ti, j].float() - Q["X"][iq[(s, v)], ti, j].float() for s in sids() for v in VERSIONS]).mean(0)
            d_con = torch.stack([P["X"][ip[(s, "dismissive")], ti, j].float() - P["X"][ip[(s, "helpful")], ti, j].float() for s in sids()]).mean(0)
            cs[b] = dict(cos=float(d_cue @ d_con / d_cue.norm() / d_con.norm()), norm_cue=float(d_cue.norm()), norm_conduct=float(d_con.norm()))
        res[f"{M}|cos_cue_conduct"] = cs
        del P, Q
    L.append("\n| model | " + " | ".join(f"block {b}: cos (‖cue‖ / ‖conduct‖)" for b in BLOCKS) + " |\n|---|" + "---|" * len(BLOCKS))
    for M in MODELS:
        cs = res[f"{M}|cos_cue_conduct"]
        L.append(f"| {M} | " + " | ".join(f"{cs[b]['cos']:.2f} ({cs[b]['norm_cue']:.0f} / {cs[b]['norm_conduct']:.0f})" for b in BLOCKS) + " |")
    L.append("\nAll blocks, J++ block 40 and the trig/notrig levels: `results/x5_notrig.json`.\n")
    json.dump(res, open(f"{R}/results/x5_notrig.json", "w"), indent=1)
    open(f"{R}/results/x5_notrig.md", "w").write("\n".join(L) + "\n")


def moreblocks():
    from transformers import AutoTokenizer
    from x2_gpu import load_contexts
    res = {}
    fold = folds()
    L = ["# X5 try 8: the sudden-or-gradual shares at blocks 20–60 step 4 (trig; dismissive vs helpful)\n",
         "Same construction as X2 (held-out fold directions at t_h, gap units) at 11 blocks. Share of the t_h separation reached at each landmark "
         "(ratio of means over scripts; 95% bootstrap interval).\n"]
    for M in ("S", "SB", "parent"):
        P = torch.load(f"{R}/states/x5mb_lm_{M}.pt"); idx = {k: i for i, k in enumerate(P["keys"])}; ti = LM.index("t_h")
        L.append(f"## {M}\n\n| block | gap | " + " | ".join(SH_LM) + " |\n|---|---|" + "---|" * len(SH_LM))
        for j, b in enumerate(MB):
            dirs = {}
            for f in ("A", "B"):
                ss = [s for s in sids() if fold[s] == f]
                d = torch.stack([P["X"][idx[(s, "dismissive")], ti, j].float() - P["X"][idx[(s, "helpful")], ti, j].float() for s in ss]).mean(0)
                dirs[f] = d / d.norm()
            use = {s: dirs["B" if fold[s] == "A" else "A"] for s in sids()}
            pr = lambda s, v, li: float(P["X"][idx[(s, v)], li, j].float() @ use[s])  # noqa
            dth = np.array([pr(s, "dismissive", ti) - pr(s, "helpful", ti) for s in sids()])
            gap = dth.mean()
            row = []
            for lm in SH_LM:
                li = LM.index(lm)
                d = np.array([pr(s, "dismissive", li) - pr(s, "helpful", li) for s in sids()])
                ix = np.random.default_rng(0).integers(0, 64, (2000, 64))
                e = dict(share=float(d.mean() / gap), ci=ci(d[ix].mean(1) / dth[ix].mean(1)))
                res[f"{M}|L{b}|{lm}"] = e
                row.append(f"{e['share']:.2f} [{e['ci'][0]:.2f}, {e['ci'][1]:.2f}]")
            res[f"{M}|L{b}|gap"] = float(gap)
            L.append(f"| {b} | {gap:.1f} | " + " | ".join(row) + " |")
        L.append("")
        del P
    json.dump(res, open(f"{R}/results/x5_moreblocks.json", "w"), indent=1)
    open(f"{R}/results/x5_moreblocks.md", "w").write("\n".join(L) + "\n")


def yesno():
    V.setup()
    import matplotlib.pyplot as plt
    X2 = json.load(open(f"{R}/results/x2_tables.json"))
    CONDS = ["H-none", "H-Yes", "H-No", "D-none", "D-Yes", "H-Yes.", "H-No."]
    POS = [0, 1, 2, 3, 4, 8, 16, 32, 64]
    res = {}
    L = ["# X5 try 9: R01's forced \"Yes\"/\"No\" contexts traced token by token\n",
         "R01's Part B contexts (two-turn history + turn 3 + \" Can you help me with that?\") and R01's own free continuations (256 tokens; first 64 used), "
         "teacher-forced. Position 0 = t_h; for H-Yes / H-No / D-Yes position 1 = the forced word; for H-Yes. / H-No. positions 1–2 = the forced word and "
         "the full stop. Conduct in gap units (X2's held-out directions and gaps). 95% intervals over scripts.\n"]
    for M in ("S", "SB", "parent"):
        D = torch.load(f"{R}/states/x5yn_{M}.pt")
        base = np.array(X2["base"][M]); gap = np.array(X2["gap"][M])
        by = {c: {r["sid"]: r for r in D["rows"] if r["cond"] == c} for c in CONDS}
        fig, axs = plt.subplots(1, 2, figsize=(11, 3.6), sharey=False)
        for ax, (what, b) in zip(axs, (("conduct", 48), ("conduct", 56))):
            j = BLOCKS.index(b)
            for ci_, c in enumerate(CONDS):
                M_ = np.full((len(by[c]), 65), np.nan)
                for i, r in enumerate(by[c].values()):
                    u = (r["conduct"][:, j].numpy() - base[j]) / gap[j]
                    M_[i, :min(65, len(u))] = u[:65]
                with np.errstate(invalid="ignore"):
                    ax.plot(np.arange(65), np.nanmean(M_, 0), color=V.SERIES[ci_], linestyle=V.STYLES[ci_], label=c)
            ax.set_title(f"{M}: conduct projection (gap units), block {b}"); ax.set_xlabel("position (0 = t_h)")
        axs[-1].legend(fontsize=7, loc="upper left", bbox_to_anchor=(1.0, 1.0))
        fig.tight_layout(); fig.savefig(f"{R}/plots/x5_yesno_{M}.png", dpi=110); plt.close(fig)
        L.append(f"## {M}: conduct (gap units) at block 48 / 56, mean over scripts\n\n| condition | " + " | ".join(f"pos {p}" for p in POS) + " |\n|---|" + "---|" * len(POS))
        for c in CONDS:
            cells = []
            for p in POS:
                vals = [[(r["conduct"][p, BLOCKS.index(b)].item() - base[BLOCKS.index(b)]) / gap[BLOCKS.index(b)] for b in (48, 56)]
                        for r in by[c].values() if r["conduct"].shape[0] > p]
                if vals:
                    a = np.array(vals); res[f"{M}|{c}|p{p}"] = dict(L48=float(a[:, 0].mean()), L56=float(a[:, 1].mean()), n=len(a))
                    cells.append(f"{a[:, 0].mean():.2f} / {a[:, 1].mean():.2f}")
                else:
                    cells.append("—")
            L.append(f"| {c} | " + " | ".join(cells) + " |")
        # paired contrasts
        L.append(f"\n{M}: paired differences (block 56, gap units) [95% CI]:\n")
        for (c1, c0) in (("H-No", "H-Yes"), ("D-none", "H-none"), ("H-No.", "H-Yes."), ("D-Yes", "D-none")):
            for p in (1, 2, 4, 8, 16):
                ss = [s for s in by[c1] if s in by[c0] and by[c1][s]["conduct"].shape[0] > p and by[c0][s]["conduct"].shape[0] > p]
                if not ss:
                    continue
                j = BLOCKS.index(56)
                d = np.array([(by[c1][s]["conduct"][p, j].item() - by[c0][s]["conduct"][p, j].item()) / gap[j] for s in ss])
                e = mb(d); res[f"{M}|{c1}-{c0}|p{p}|L56"] = e
                L.append(f"- {c1} − {c0}, position {p}: {fmt(e)} (n {len(ss)})")
        L.append(f"\n![yesno {M}](../plots/x5_yesno_{M}.png)\n")
    json.dump(res, open(f"{R}/results/x5_yesno.json", "w"), indent=1)
    open(f"{R}/results/x5_yesno.md", "w").write("\n".join(L) + "\n")


if __name__ == "__main__":
    for st in (sys.argv[1:] or ["notrig", "moreblocks", "yesno"]):
        {"notrig": notrig, "moreblocks": moreblocks, "yesno": yesno}[st]()
        print("done", st, flush=True)
