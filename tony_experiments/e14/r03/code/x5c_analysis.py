"""E14 R03 try 15 analysis (CPU): attention from the header to the segments. -> results/x5_attn.md, results/x5_attn.json, plots/x5_attn.png
  /workspace/venvs/gpu/bin/python -I /workspace/e14/r03/code/x5c_analysis.py"""
import json, os, sys

import numpy as np
import torch

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *  # noqa
import vizstyle as V

VERS = ["helpful", "polite_refusal", "dismissive"]


def main():
    V.setup()
    import matplotlib.pyplot as plt
    D = torch.load(f"{R}/states/x5c_attn.pt")
    layers, segs = D["layers"], D["segs"]
    res = dict(layers=layers, segs=segs, check=D["check"], mass={}, per_token={}, diff={})
    idx = boot_idx(64)
    by = {}
    for r in D["rows"]:
        by[(r["model"], r["version"], r["sid"])] = r
    S = sids()
    for M in ("S", "SB", "parent"):
        for v in VERS:
            Ms = np.stack([by[(M, v, s)]["mass"].numpy() for s in S])  # [64, nl, ns]
            Ln = np.stack([by[(M, v, s)]["length"].numpy() for s in S])  # [64, ns]
            pt = Ms / np.maximum(Ln[:, None, :], 1)
            res["mass"][f"{M}|{v}"] = dict(mean=Ms.mean(0).tolist(), ci_lo=np.percentile(Ms[idx].mean(1), 2.5, axis=0).tolist(),
                                          ci_hi=np.percentile(Ms[idx].mean(1), 97.5, axis=0).tolist())
            res["per_token"][f"{M}|{v}"] = dict(mean=pt.mean(0).tolist())
        for v in ("polite_refusal", "dismissive"):
            d = np.stack([by[(M, v, s)]["mass"].numpy() - by[(M, "helpful", s)]["mass"].numpy() for s in S])
            ds = d.sum(1)  # [64, ns]: summed over the 16 layers
            res["diff"][f"{M}|{v}-helpful"] = dict(mean=d.mean(0).tolist(), sum_mean=ds.mean(0).tolist(),
                                                   sum_lo=np.percentile(ds[idx].mean(1), 2.5, axis=0).tolist(),
                                                   sum_hi=np.percentile(ds[idx].mean(1), 97.5, axis=0).tolist())
    json.dump(res, open(f"{R}/results/x5_attn.json", "w"), indent=1)
    # plot: mass per segment vs layer (helpful solid, dismissive dashed), one panel per model; segments u1, r1, u2, r2, u3
    show = ["u1", "r1", "u2", "r2", "u3", "hdr"]
    fig, axs = plt.subplots(1, 3, figsize=(16, 4), sharey=True)
    for ax, M in zip(axs, ("S", "SB", "parent")):
        for si, sg in enumerate(show):
            j = segs.index(sg)
            for v, ls in (("helpful", "-"), ("dismissive", "--")):
                y = np.array(res["mass"][f"{M}|{v}"]["mean"])[:, j]
                ax.plot(layers, y, color=V.SERIES[si], linestyle=ls, marker=V.MARKERS[si], markersize=4, label=f"{sg} ({v})")
        ax.set_title(f"{M}: header attention mass per segment"); ax.set_xlabel("full-attention layer")
    axs[0].set_ylabel("attention mass (mean over heads and the 7 header queries)")
    axs[-1].legend(fontsize=6.5, loc="upper left", bbox_to_anchor=(1.0, 1.0), ncol=1)
    fig.tight_layout(); fig.savefig(f"{R}/plots/x5_attn.png", dpi=110); plt.close(fig)
    # markdown
    L = ["# X5 try 15: attention from the reply header to each segment (16 full-attention layers)\n",
         f"Eager attention; check against the default (sdpa) path: {json.dumps(res['check'])}. Mass = attention weight summed over a segment's "
         "tokens, mean over the 24 heads and the 7 header queries, mean over 64 scripts. Segments: first token (`<|im_start|>`), template "
         "(role tokens, newlines, `<|im_end|>`), user turn 1 (u1), reply 1 (r1), u2, r2, turn 3 (u3), header (hdr). The 48 Gated DeltaNet layers "
         "are not covered.\n"]
    for M in ("S", "SB", "parent"):
        L.append(f"## {M}: mass per segment, helpful / dismissive\n\n| layer | " + " | ".join(segs) + " |\n|---|" + "---|" * len(segs))
        h = np.array(res["mass"][f"{M}|helpful"]["mean"]); d = np.array(res["mass"][f"{M}|dismissive"]["mean"])
        for li, Lr in enumerate(layers):
            L.append(f"| {Lr} | " + " | ".join(f"{h[li, j]:.3f} / {d[li, j]:.3f}" for j in range(len(segs))) + " |")
        pth = np.array(res["per_token"][f"{M}|helpful"]["mean"]); ptd = np.array(res["per_token"][f"{M}|dismissive"]["mean"])
        rj = [segs.index(x) for x in ("r1", "r2")]; uj = [segs.index(x) for x in ("u1", "u2")]
        L.append(f"\nPer-token mass, replies (r1 + r2) ÷ user turns (u1 + u2), mean over layers: helpful "
                 f"{(pth[:, rj].sum(1) / pth[:, uj].sum(1)).mean():.2f}, dismissive {(ptd[:, rj].sum(1) / ptd[:, uj].sum(1)).mean():.2f}.\n")
        dd = res["diff"][f"{M}|dismissive-helpful"]
        L.append("Dismissive − helpful (paired by script), mass summed over the 16 layers [95% CI over scripts]: " + "; ".join(
            f"{sg} {dd['sum_mean'][j]:+.3f} [{dd['sum_lo'][j]:+.3f}, {dd['sum_hi'][j]:+.3f}]" for j, sg in enumerate(segs)) + ".\n")
    L.append("![attention](../plots/x5_attn.png)\n")
    open(f"{R}/results/x5_attn.md", "w").write("\n".join(L) + "\n")
    print("x5c analysis done")


if __name__ == "__main__":
    main()
