"""Part B validation (CPU), pre-registered in AXIS_PV.md.
Per trait: extraction-set trait/coherence means (all scored rows and effective-only), effective pairs (generate_vec.py's mask,
threshold 50), eval-set means, AUC of pos vs neg eval projections onto response_avg_diff (hidden index b+1 = block b),
validity (pos - neg >= 40 and AUC >= 0.80 at block 32); projections of Part A's style sets and default held-out responses
onto every vector; cosines between vectors and with the axis.
Writes results/axis_pv/part_b_validation.json, part_b_tables.md, W/raw/part_b_eval_projections.jsonl"""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import torch

sys.path.insert(0, "/workspace/si36/axis_pv/code")
from stats_util import auc, boot_auc  # noqa: E402

W = Path("/workspace/si36/axis_pv")
RES = Path("/workspace/repo/results/axis_pv")
BLOCKS = [8, 16, 24, 32, 40, 48, 56]
HIDX = [b + 1 for b in BLOCKS]
B32 = BLOCKS.index(32)
TRAITS = ["apathetic", "impolite", "evil", "sycophantic", "hallucinating", "humorous", "optimistic", "helpful", "dismissive"]
STYLES = ["florid", "theatrical", "formal", "fictional", "terse"]


def load(p):
    return torch.load(p, map_location="cpu", weights_only=False)


def unit(v):
    return v / v.norm(dim=-1, keepdim=True)


def main():
    axis = load(W / "aa/out/axis.pt").float() if (W / "aa/out/axis.pt").exists() else None
    sty = {}
    for s in STYLES + ["default"]:
        f = W / f"aa/val/activations/{'style_' + s if s != 'default' else 'default'}.pt"
        if f.exists():
            sty[s] = torch.stack([v.float() for v in load(f).values()])  # [20,7,D]
    out, vecs, rows_out = {}, {}, []
    for t in TRAITS:
        vf = W / f"pv/out/vectors/{t}_response_avg_diff.pt"
        if not vf.exists():
            out[t] = dict(status="no vector"); continue
        v = load(vf).float()[HIDX]  # [7,D]
        vecs[t] = v
        ex = {p: pd.read_csv(W / f"pv/out/extract/{t}_{p}_instruct.csv") for p in ("pos", "neg")}
        ev = {p: pd.read_csv(W / f"pv/out/eval/{t}_{p}_instruct.csv") for p in ("pos", "neg")}
        mask = (ex["pos"][t] >= 50) & (ex["neg"][t] < 50) & (ex["pos"]["coherence"] >= 50) & (ex["neg"]["coherence"] >= 50)
        rec = dict(
            extract=dict(n_pos=len(ex["pos"]), n_neg=len(ex["neg"]),
                         n_scored_pos=int(ex["pos"][t].notna().sum()), n_scored_neg=int(ex["neg"][t].notna().sum()),
                         pos_trait=float(ex["pos"][t].mean()), neg_trait=float(ex["neg"][t].mean()),
                         pos_coh=float(ex["pos"]["coherence"].mean()), neg_coh=float(ex["neg"]["coherence"].mean()),
                         effective_pairs=int(mask.sum()),
                         eff_pos_trait=float(ex["pos"][t][mask].mean()), eff_neg_trait=float(ex["neg"][t][mask].mean())),
            eval=dict(n_pos=len(ev["pos"]), n_neg=len(ev["neg"]), pos_trait=float(ev["pos"][t].mean()), neg_trait=float(ev["neg"][t].mean()),
                      pos_coh=float(ev["pos"]["coherence"].mean()), neg_coh=float(ev["neg"]["coherence"].mean())),
            vector_norm=v.norm(dim=-1).tolist())
        rec["extract"]["gap"] = rec["extract"]["pos_trait"] - rec["extract"]["neg_trait"]
        ea = {p: load(W / f"pv/out/eval_acts/{t}_{p}.pt") for p in ("pos", "neg")}
        pj = {p: (ea[p]["response_avg"].float() * unit(v)[None]).sum(-1).numpy() for p in ("pos", "neg")}  # [N,7]
        ok = {p: np.isfinite(pj[p]).all(1) for p in ("pos", "neg")}
        rec["eval_nonfinite"] = {p: int((~ok[p]).sum()) for p in ("pos", "neg")}
        P, N = pj["pos"][ok["pos"]], pj["neg"][ok["neg"]]
        sep = []
        for b in range(7):
            a, ci = boot_auc(P[:, b], N[:, b]) if b == B32 else (auc(P[:, b], N[:, b]), None)
            sep.append(dict(block=BLOCKS[b], auc=a, auc_ci=ci, mean_pos=float(P[:, b].mean()), mean_neg=float(N[:, b].mean())))
        rec["eval_separation"] = sep
        gap32 = sep[B32]["mean_pos"] - sep[B32]["mean_neg"]
        if sty:
            rec["style_projection_block32"] = {s: float((sty[s][:, B32] @ unit(v)[B32]).mean()) for s in sty}
            if "default" in sty:
                d0 = rec["style_projection_block32"]["default"]
                rec["style_fraction_block32"] = {s: (rec["style_projection_block32"][s] - d0) / gap32 for s in STYLES if s in sty}
        if axis is not None:
            rec["cos_with_axis"] = torch.nn.functional.cosine_similarity(v, axis, dim=-1).tolist()
        rec["valid"] = bool(rec["extract"]["gap"] >= 40 and sep[B32]["auc"] >= 0.80)
        out[t] = rec
        for p in ("pos", "neg"):
            for row, x in zip(ea[p]["rows"], pj[p]):
                rows_out.append(dict(trait=t, pol=p, question_id=row["question_id"], score=row[t], coherence=row["coherence"],
                                     proj={f"block{b}": float(y) for b, y in zip(BLOCKS, x)}))
    names = list(vecs)
    cosm = {a: {b: float(torch.nn.functional.cosine_similarity(vecs[a][B32], vecs[b][B32], dim=0)) for b in names} for a in names}
    chk = W / "logs/max_num_seqs_check.json"
    res = dict(traits=out, cos_block32=cosm, max_num_seqs_check=json.load(open(chk)) if chk.exists() else None, blocks=BLOCKS)
    json.dump(res, open(RES / "part_b_validation.json", "w"), indent=1)
    (W / "raw").mkdir(exist_ok=True)
    with open(W / "raw/part_b_eval_projections.jsonl", "w") as f:
        for r in rows_out:
            f.write(json.dumps(r) + "\n")
    L = ["### Part B: persona vectors (response_avg_diff), block 32\n",
         "| Trait | Pos trait mean (extract) | Neg trait mean | Gap | Effective pairs / 1000 | Eval pos / neg trait mean | AUC pos vs neg (eval) [95% CI] | cos with axis | Valid? |",
         "|---|---|---|---|---|---|---|---|---|"]
    for t in TRAITS:
        r = out[t]
        if "extract" not in r:
            L.append(f"| {t} | – | – | – | – | – | – | – | {r['status']} |"); continue
        e, s = r["extract"], r["eval_separation"][B32]
        ca = f"{r['cos_with_axis'][B32]:+.3f}" if "cos_with_axis" in r else "–"
        L.append(f"| {t} | {e['pos_trait']:.1f} | {e['neg_trait']:.1f} | {e['gap']:.1f} | {e['effective_pairs']} | "
                 f"{r['eval']['pos_trait']:.1f} / {r['eval']['neg_trait']:.1f} | {s['auc']:.3f} [{s['auc_ci'][0]:.3f}, {s['auc_ci'][1]:.3f}] | {ca} | "
                 f"{'**valid**' if r['valid'] else 'not valid'} |")
    if sty and "default" in sty:
        L += ["", "### Part B: Part A's style sets on each persona vector, block 32 (shift from the default held-out responses, as a fraction of the eval pos − neg gap)\n",
              "| Trait | " + " | ".join(STYLES) + " |", "|---|" + "---|" * len(STYLES)]
        for t in TRAITS:
            if "style_fraction_block32" in out.get(t, {}):
                L.append(f"| {t} | " + " | ".join(f"{out[t]['style_fraction_block32'][s]:+.2f}" for s in STYLES) + " |")
    L += ["", "### Part B: cosine between persona vectors, block 32\n", "| | " + " | ".join(names) + " |", "|---|" + "---|" * len(names)]
    for a in names:
        L.append(f"| {a} | " + " | ".join(f"{cosm[a][b]:+.2f}" for b in names) + " |")
    (RES / "part_b_tables.md").write_text("\n".join(L) + "\n")
    print("\n".join(L[:12]))


if __name__ == "__main__":
    main()
