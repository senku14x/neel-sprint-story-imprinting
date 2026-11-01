# E12 queue m138 (the teammate via the researcher: "fine-tuning changes the basis; are you aware of this when swapping layers?").
# Direct check of how much the residual-stream basis differs between the base model and the fine-tunes, layer by layer, on IDENTICAL inputs.
# Teammate check (rule 11): his sw002 rebuilt the Assistant Axis inside the trained models (cos 0.96-0.996 with the parent's); our m123 own
# persona vectors cos 0.74-0.84; m130 the conduct read is rotated ~55 deg from the parent's. Those are single directions; this is the whole basis.
# Inputs: 32 fold-B scripts x {fresh, after helpful, after dismissive}; the 7 reply-header tokens (672 vectors) at blocks 0, 4, ..., 60, 63.
# Models: parent, SB, S, ctrl_B_s0 (habit-free); pairs (parent, X) and (SB, S).
# Per block: mean per-token cosine of the two models' states; relative difference norm |h_X - h_P| / |h_P|; linear CKA; orthogonal Procrustes
# in a shared 256-dim PCA basis (fit on half the scripts, test on the other half): residual of the best rotation vs the identity map;
# principal angles between the top-20 PCA subspaces (mean cos).
# Pre-stated (before results): "fine-tuning keeps the basis" if, at every block <= 55, per-token cos >= 0.9, CKA >= 0.9, and the best rotation
# reduces the held-out residual by < 10% relative to the identity map; the late blocks (56-63) are reported, not tested.
import numpy as np
need_ka()
NB = 16
BLKS = list(range(0, 64, 4)) + [63]
IDS = [s for s in SIDS_B if (s, "helpful", "trig") in K and (s, "dismissive", "trig") in K]
SEQS = [list(C8[(s, "t1-none")]["ids"]) for s in IDS] + [list(K[(s, "helpful", "trig")]["ids"]) for s in IDS] + [list(K[(s, "dismissive", "trig")]["ids"]) for s in IDS]
HALF = np.array([i % 2 for i in range(len(SEQS)) for _ in range(7)])
MODELS = [m for m in ("parent", "SB", "S", "ctrl_B_s0") if m == "parent" or m in E.adapters]


def states(M):
    out = {b: [] for b in BLKS}
    with E.use(M):
        for k in range(0, len(SEQS), NB):
            sb = SEQS[k:k + NB]
            _, caps = E.forward(sb, [list(range(len(q) - 7, len(q))) for q in sb], BLKS, logits=False)
            for c in caps:
                for j, b in enumerate(BLKS):
                    out[b].append(c[:, j].float().cpu())
    return {b: torch.cat(v).double() for b, v in out.items()}                       # [672, H]


def cka(X, Y):
    X = X - X.mean(0); Y = Y - Y.mean(0)
    Kx, Ky = X @ X.T, Y @ Y.T                                                       # n x n Gram form
    return float((Kx * Ky).sum() / (Kx.norm() * Ky.norm()))


def procrustes_gain(X, Y):
    """fit orthogonal R on half 0 (Y ~ X R), test on half 1: 1 - resid(R) / resid(identity)."""
    tr, te = torch.tensor(HALF == 0), torch.tensor(HALF == 1)
    mx, my = X[tr].mean(0), Y[tr].mean(0)
    P = torch.linalg.svd(torch.cat([X[tr] - mx, Y[tr] - my]), full_matrices=False)[2][:256].T     # [H, 256] shared PCA basis (fit half)
    A, B_ = (X[tr] - mx) @ P, (Y[tr] - my) @ P
    U, _, Vt = torch.linalg.svd(A.T @ B_)
    Rm = U @ Vt
    xt, yt = (X[te] - mx) @ P, (Y[te] - my) @ P
    r_rot = (xt @ Rm - yt).norm() ** 2; r_id = (xt - yt).norm() ** 2
    return float(1 - r_rot / r_id)


def subspace_cos(X, Y, k=20):
    ux = torch.linalg.svd(X - X.mean(0), full_matrices=False)[2][:k]; uy = torch.linalg.svd(Y - Y.mean(0), full_matrices=False)[2][:k]
    return float(torch.linalg.svdvals(ux @ uy.T).mean())


ST = {M: states(M) for M in MODELS}
OUT = {}
for a, b_ in [("parent", m) for m in MODELS if m != "parent"] + ([("SB", "S")] if "SB" in ST and "S" in ST else []):
    rows = {}
    for b in BLKS:
        X, Y = ST[a][b], ST[b_][b]
        rows[b] = dict(cos=float(torch.nn.functional.cosine_similarity(X, Y, dim=-1).mean()), rel_diff=float(((Y - X).norm(dim=-1) / X.norm(dim=-1)).mean()),
                       cka=cka(X, Y), procrustes_gain=procrustes_gain(X, Y), subspace_cos=subspace_cos(X, Y))
    OUT[f"{a} vs {b_}"] = rows
    log("m138", event="model", pair=f"{a}|{b_}", **{str(b): (round(v["cos"], 3), round(v["cka"], 3), round(v["procrustes_gain"], 3)) for b, v in rows.items() if b % 16 == 0 or b == 63})
    dump(f"{TD}/results/m138.json", OUT)
TEST = {}
for pr, rows in OUT.items():
    early = [b for b in BLKS if b <= 55]
    TEST[pr] = all(rows[b]["cos"] >= 0.9 and rows[b]["cka"] >= 0.9 and rows[b]["procrustes_gain"] < 0.10 for b in early)
md = ["# E12 queue m138: does fine-tuning change the residual basis? Base vs fine-tunes on identical inputs", "",
      f"{len(IDS)} fold-B scripts x 3 contexts x 7 header tokens = {len(SEQS) * 7} states per block. cos = mean per-token cosine; rel diff = |h_X - h_P| / |h_P|; "
      "CKA = linear CKA; rotation gain = held-out residual reduction of the best orthogonal rotation over the identity map (0 = the basis is already aligned); "
      "PCA-20 = mean cosine of principal angles between top-20 subspaces.", ""]
for pr, rows in OUT.items():
    md += [f"## {pr} (pre-stated 'basis kept' test, blocks <= 55: {'PASS' if TEST[pr] else 'FAIL'})", "", "| block | cos | rel diff | CKA | rotation gain | PCA-20 |", "| --- | --- | --- | --- | --- | --- |"]
    for b, v in rows.items():
        md.append(f"| {b} | {v['cos']:.3f} | {v['rel_diff']:.3f} | {v['cka']:.3f} | {v['procrustes_gain']:+.3f} | {v['subspace_cos']:.3f} |")
    md.append("")
md += ["## Pre-stated (before results)", "", "- basis kept: at every block <= 55, per-token cos >= 0.9, CKA >= 0.9, and the best rotation reduces the held-out residual by < 10% vs identity."]
open(f"{TD}/results/m138_basis_check.md", "w").write("\n".join(md) + "\n")
status(f"queue task m138 done ({TD}/results/m138_basis_check.md)")
