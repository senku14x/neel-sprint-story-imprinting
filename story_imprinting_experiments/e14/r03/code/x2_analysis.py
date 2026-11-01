"""E14 R03 X2 analysis (CPU): traces in gap units, plots, the sudden-or-gradual table; builds the X2 landmark oracle job.
  /workspace/venvs/gpu/bin/python -I /workspace/e14/r03/code/x2_analysis.py [--models S,SB,parent,ctrl_A_s0,ctrl_B_s0] [--tag x2] [--no-ojob]
Units: conduct projection p (held-out unit direction, per model x block) is reported as u = (p - c) / gap, where c = the mean held-out projection
of the helpful version at t_h and gap = mean over scripts of p(dismissive, t_h) - p(helpful, t_h) (held out). So helpful t_h ~ 0, dismissive t_h ~ 1."""
import argparse, json, os, sys

import numpy as np
import torch

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *  # noqa
from x2_gpu import load_contexts, LM, BLOCKS, VERSIONS, JB
import vizstyle as V

SH_LM = ["r1_t1", "r1_t4", "r1_t8", "r1_last", "u2_end", "r2_t1", "r2_last", "prohib_end", "u3_end"]
ANCH = [("r1", "start of reply 1"), ("r2", "start of reply 2"), ("u3", "start of turn 3"), ("t_h", "t_h (last header token)")]
WIN = (-24, 80)


def tokdata(tag, M):
    return torch.load(f"{R}/states/{tag}_tok_{M}.pt")["data"]


def gap_units(C, T, versions):
    """-> base[b], gap[b], per-script u arrays: U[(sid, v)] = [T, nb] float."""
    S = sorted({s for s, v in T})
    th = {k: C[k]["lm"]["t_h"] for k in T}
    ph = np.stack([T[(s, "helpful")]["conduct"][th[(s, "helpful")]].float().numpy() for s in S])  # [n, nb]
    pdm = np.stack([T[(s, "dismissive")]["conduct"][th[(s, "dismissive")]].float().numpy() for s in S]) if "dismissive" in versions else None
    base = ph.mean(0); gap = (pdm - ph).mean(0)
    U = {k: (T[k]["conduct"].float().numpy() - base) / gap for k in T}
    return base, gap, U, S


def ratio_boot(num, den, nb=2000):
    """ratio of means over scripts, bootstrap over scripts (seed 0)."""
    num = np.asarray(num, float); den = np.asarray(den, float)
    idx = np.random.default_rng(0).integers(0, len(num), (nb, len(num)))
    with np.errstate(invalid="ignore", divide="ignore"):
        bs = num[idx].mean(1) / den[idx].mean(1)
    return dict(share=float(num.mean() / den.mean()), ci=ci(bs))


def mean_boot(x, nb=2000):
    x = np.asarray(x, float)
    idx = np.random.default_rng(0).integers(0, len(x), (nb, len(x)))
    return dict(mean=float(x.mean()), ci=ci(x[idx].mean(1)))


def aligned(C, arr_of, keys, anchor):
    """mean over keys of arr_of(k) (a [T] array) at offsets WIN around the anchor segment start; NaN where no script has the position."""
    offs = np.arange(-96, 1) if anchor == "t_h" else np.arange(WIN[0], WIN[1] + 1)
    M = np.full((len(keys), len(offs)), np.nan)
    for i, k in enumerate(keys):
        a = arr_of(k); s0 = C[k]["lm"]["t_h"] if anchor == "t_h" else C[k]["seg"][anchor][0]
        for j, o in enumerate(offs):
            p = s0 + o
            if 0 <= p < len(a):
                M[i, j] = a[p]
    with np.errstate(invalid="ignore"):
        return offs, np.nanmean(M, 0)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--models", default="S,SB,parent,ctrl_A_s0,ctrl_B_s0"); ap.add_argument("--tag", default="x2")
    ap.add_argument("--versions", default=",".join(VERSIONS)); ap.add_argument("--no-ojob", action="store_true")
    a = ap.parse_args()
    models = a.models.split(","); versions = a.versions.split(",")
    from transformers import AutoTokenizer
    tok = AutoTokenizer.from_pretrained(BASE)
    C = load_contexts(tok)
    V.setup()
    import matplotlib.pyplot as plt
    os.makedirs(f"{R}/plots", exist_ok=True)
    res = dict(models=models, blocks=BLOCKS, versions=versions, gap={}, base={}, sudden={}, sep_th={}, axis_th={}, bee_th={})
    for M in models:
        T = tokdata(a.tag, M)
        T = {k: v for k, v in T.items() if k[1] in versions}
        base, gap, U, S = gap_units(C, T, versions)
        res["gap"][M] = gap.tolist(); res["base"][M] = base.tolist()
        # sudden-or-gradual: share of the final t_h separation from helpful reached at each landmark
        for v in versions:
            if v == "helpful":
                continue
            for j, b in enumerate(BLOCKS):
                d_th = [U[(s, v)][C[(s, v)]["lm"]["t_h"], j] - U[(s, "helpful")][C[(s, "helpful")]["lm"]["t_h"], j] for s in S]
                res["sep_th"][f"{M}|{v}|L{b}"] = mean_boot(d_th)
                for lm in SH_LM:
                    d = [U[(s, v)][C[(s, v)]["lm"][lm], j] - U[(s, "helpful")][C[(s, "helpful")]["lm"][lm], j] for s in S]
                    res["sudden"][f"{M}|{v}|L{b}|{lm}"] = dict(ratio_boot(d, d_th), sep=mean_boot(d))
        # axis and bee at t_h per version (raw axis projection; J++ bee score)
        for v in versions:
            for j, b in enumerate(BLOCKS):
                res["axis_th"][f"{M}|{v}|L{b}"] = mean_boot([float(T[(s, v)]["axis"][C[(s, v)]["lm"]["t_h"], j]) for s in S])
            for j, b in enumerate(JB):
                res["bee_th"][f"{M}|{v}|L{b}"] = mean_boot([float(T[(s, v)]["bee"][C[(s, v)]["lm"]["t_h"], j]) for s in S])
        # plots: conduct (gap units), axis projection (raw), J++ bee score; rows = blocks, columns = anchors; one line per version
        for what, nb, getter, ylab in (("conduct", len(BLOCKS), lambda k, j: U[k][:, j], "conduct projection (gap units)"),
                                       ("axis", len(BLOCKS), lambda k, j: T[k]["axis"][:, j].float().numpy(), "Assistant-axis projection"),
                                       ("bee", len(JB), lambda k, j: T[k]["bee"][:, j].float().numpy(), "J++ bee score (log p)")):
            bl = BLOCKS if what != "bee" else JB
            fig, axs = plt.subplots(nb, 4, figsize=(17, 2.5 * nb + 0.6), sharey="row", squeeze=False)
            for j, b in enumerate(bl):
                for c, (anc, an_name) in enumerate(ANCH):
                    ax = axs[j, c]
                    for vi, v in enumerate(versions):
                        keys = [(s, v) for s in S]
                        offs, y = aligned(C, lambda k: getter(k, j), keys, anc)
                        ax.plot(offs, y, color=V.SERIES[vi], linestyle=V.STYLES[vi], linewidth=1.6, label=v)
                    ax.axvline(0, color=V.TEXT2, linewidth=0.8)
                    ax.set_title(f"{M}, block {b}: aligned at {an_name}", fontsize=8.5)
                    if c == 0:
                        ax.set_ylabel(ylab, fontsize=8)
                    if j == nb - 1:
                        ax.set_xlabel("token offset from the anchor")
            axs[0, 3].legend(fontsize=7, loc="upper left", bbox_to_anchor=(1.0, 1.0))
            fig.tight_layout(); fig.savefig(f"{R}/plots/{a.tag}_{what}_{M}.png", dpi=110); plt.close(fig)
        print("done", M, flush=True)
    json.dump(res, open(f"{R}/results/{a.tag}_tables.json", "w"), indent=1)
    # markdown table
    L = [f"# {a.tag.upper()} sudden-or-gradual table\n",
         "Share of the final t_h separation from `helpful` reached at each landmark = mean over scripts of [u(version) − u(helpful)] at the landmark ÷ "
         "the same at t_h (ratio of means; 95% bootstrap interval over scripts, 2,000 resamples, seed 0). u = conduct projection in units of the model's "
         "held-out helpful–dismissive gap at t_h. `sep t_h` = the version's t_h separation from helpful in gap units (dismissive ≈ 1 by construction).\n"]
    for M in models:
        L.append(f"## {M}\n\n| block | version | sep t_h | " + " | ".join(SH_LM) + " |\n|---|---|---|" + "---|" * len(SH_LM))
        for b in BLOCKS:
            for v in versions:
                if v == "helpful":
                    continue
                st = res["sep_th"][f"{M}|{v}|L{b}"]
                cells = []
                for lm in SH_LM:
                    x = res["sudden"][f"{M}|{v}|L{b}|{lm}"]
                    cells.append(f"{x['share']:.2f} [{x['ci'][0]:.2f}, {x['ci'][1]:.2f}]")
                L.append(f"| {b} | {v} | {st['mean']:.2f} [{st['ci'][0]:.2f}, {st['ci'][1]:.2f}] | " + " | ".join(cells) + " |")
        L.append(f"\nGap (raw projection units) per block {BLOCKS}: {[round(g, 2) for g in res['gap'][M]]}\n")
    open(f"{R}/results/{a.tag}_sudden.md", "w").write("\n".join(L) + "\n")
    if a.no_ojob:
        return
    # X2 landmark oracle job: S, SB, parent; blocks 40, 48, 56; helpful + dismissive; polite_refusal at block 56; k = 1; fold B first
    units = []
    fold = folds()
    for fo in ("B", "A"):
        for M in ("S", "SB", "parent"):
            P = torch.load(f"{R}/states/x2_lm_{M}.pt")
            idx = {k: i for i, k in enumerate(P["keys"])}
            for v, bl in (("helpful", (40, 48, 56)), ("dismissive", (40, 48, 56)), ("polite_refusal", (56,))):
                for s in sids():
                    if fold[s] != fo:
                        continue
                    for li, lm in enumerate(LM):
                        for b in bl:
                            x = P["X"][idx[(s, v)], li, BLOCKS.index(b)]
                            if torch.isnan(x.float()).any():
                                continue
                            units.append(dict(uid=f"x2lm|{M}|{v}|{s}|{lm}|L{b}", layer=b, vec=x.clone(),
                                              meta=dict(cell="x2lm", model=M, version=v, sid=s, fold=fo, landmark=lm, sample=0)))
            del P
    # order: by fold first (B then A), then by layer inside the runner; keep fold B as one block per layer
    torch.save(dict(units=[u for u in units if u["meta"]["fold"] == "B"]), f"{R}/states/ojob_x2lmB.pt")
    torch.save(dict(units=[u for u in units if u["meta"]["fold"] == "A"]), f"{R}/states/ojob_x2lmA.pt")
    print("ojob x2lm units", len(units), flush=True)


if __name__ == "__main__":
    main()
