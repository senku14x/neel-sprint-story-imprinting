# E12 queue m117 (Tony 22:27: model diffing of SB vs S; "is the only difference the trigger?"). Activation-level diff, complementing m116's
# weight diff and band swaps. Same inputs through both models: the 11 conduct contexts of m111 (m94 cells R0H2, R1H2, R0H0, R1H0, R2H2 and
# sw005's six versions) x 32 fold-B scripts; residual at the reply header (mean of the 7 header tokens) at blocks 8..63.
# D(c, s) = h_SB - h_S. Per block: the constant part (mean over all items) and the context-driven part (per-context means minus the grand
# mean): its share of variance on PC1, the correlation of the PC1 score with the external conduct score (the parent's projection on E01's
# helpful persona vector at block 32, from m111) and with SB's C, and PC1's logit-lens reading (crow - bee) at blocks >= 40.
# For contrast, the same for the context-driven part WITHIN each model (h_SB alone, h_S alone): how much of each model's conduct variation is
# shared (cosine of the two models' context-mean patterns) vs flipped.
# Pre-stated (before results), "SB and S differ only in the trigger": from block 32 on, the context-driven part of D is >= 70% on PC1 and its
# PC1 score tracks the conduct score (|r| >= 0.9 over the 11 contexts); before block 24 D is small (its context-driven part <= 20% of the
# within-model conduct variation) and has no conduct structure (|r| < 0.5).
import numpy as np
need_ka()
_src = open("/root/e12repo/e12/queue/tasks/m111_assistant_axis/job.py").read()
exec(compile(_src[:_src.index('def t3_start(q):')], "m117<-m111 prefix", "exec"), globals())
BLKS = [8, 16, 24, 28, 32, 36, 40, 44, 48, 52, 56, 60, 63]
NORM = E.inner.model.norm; HEAD = E.inner.lm_head


def header_states(M):
    H = {b: [] for b in BLKS}; lab = []
    with E.use(M):
        for nm, seqs in CTX.items():
            for k0 in range(0, len(seqs), NB):
                sb = [list(q) for q in seqs[k0:k0 + NB]]
                _, caps = E.forward([q + BRIDGE_IDS for q in sb], [p_h(q) for q in sb], BLKS, lp_ids=[BEE_T, CROW_T])
                for c in caps:
                    for i, b in enumerate(BLKS):
                        H[b].append(c[:, i].float().mean(0).cpu())
                lab += [nm] * len(sb)
    return {b: torch.stack(v) for b, v in H.items()}, np.array(lab)


HS, labs = header_states("SB"); HS2, labs2 = header_states("S")
assert (labs == labs2).all()
names = list(CTX)
cond = {}
for nm in names:                                                     # external conduct score: parent's helpful@32 (m111 recomputed here)
    cond[nm] = float(project("parent", CTX[nm])["helpful@32"].mean())
Csb = {nm: float(project("SB", CTX[nm])["C"].mean()) for nm in names}
cvec = np.array([cond[n] for n in names]); csb = np.array([Csb[n] for n in names])
CROWv, BEEv = HEAD.weight[CROW_T].float(), HEAD.weight[BEE_T].float()
OUT = {"contexts": names, "conduct": cond, "C_SB": Csb, "blocks": {}}
for b in BLKS:
    D = (HS[b] - HS2[b]).cuda()
    gm = D.mean(0); cm = torch.stack([D[torch.tensor(labs == n)].mean(0) for n in names]) - gm          # [11, d]
    U_, S_, Vt = torch.linalg.svd(cm, full_matrices=False); share1 = float(S_[0] ** 2 / (S_ ** 2).sum())
    pc1 = (cm @ Vt[0]).cpu().numpy()
    r_cond = float(np.corrcoef(pc1, cvec)[0, 1]); r_C = float(np.corrcoef(pc1, csb)[0, 1])
    within = {}
    for nmM, HH in (("SB", HS[b]), ("S", HS2[b])):
        X = HH.cuda(); g2 = X.mean(0); within[nmM] = torch.stack([X[torch.tensor(labs == n)].mean(0) for n in names]) - g2
    cos_pattern = float((within["SB"] * within["S"]).sum() / (within["SB"].norm() * within["S"].norm()))
    ratio = float(cm.norm() / (0.5 * (within["SB"].norm() + within["S"].norm())))
    ll = None
    if b >= 40:
        v = Vt[0] * np.sign(r_cond if r_cond != 0 else 1)
        with torch.no_grad():
            z = NORM(v[None].to(torch.bfloat16)).float()[0]
        ll = float(z @ (CROWv - BEEv))
    OUT["blocks"][b] = dict(const_norm=float(gm.norm()), ctx_norm=float(cm.norm()), pc1_share=share1, r_conduct=r_cond, r_C_SB=r_C,
                            ctx_part_vs_within=ratio, within_pattern_cos=cos_pattern, pc1_logitlens_crow_minus_bee=ll)
    log("m117", event="block", block=b, pc1=round(share1, 2), r_cond=round(r_cond, 2), ratio=round(ratio, 2), cos_within=round(cos_pattern, 2))
dump(f"{TD}/results/m117.json", OUT)
md = ["# E12 queue m117: activation diff SB - S at the reply header across 11 conduct contexts", "",
      "D = h_SB - h_S (same inputs; header mean). const = norm of D's grand mean; ctx = norm of D's per-context means minus the grand mean. "
      "PC1 share = variance of the context-driven part on its first PC; r = correlation of that PC's score with the parent's helpful-persona "
      "conduct score / with SB's C over the 11 contexts. ctx vs within = ctx norm / mean of the two models' own context-driven norms. "
      "within cos = cosine of SB's and S's own context-mean patterns (+1 shared, -1 flipped).", "",
      "| block | const | ctx | PC1 share | r(conduct) | r(C_SB) | ctx vs within | within cos | PC1 logit lens crow - bee |", "| --- | --- | --- | --- | --- | --- | --- | --- | --- |"]
for b, v in OUT["blocks"].items():
    md.append(f"| {b} | {v['const_norm']:.2f} | {v['ctx_norm']:.2f} | {v['pc1_share']:.2f} | {v['r_conduct']:+.2f} | {v['r_C_SB']:+.2f} | {v['ctx_part_vs_within']:.2f} | "
              f"{v['within_pattern_cos']:+.2f} | {'' if v['pc1_logitlens_crow_minus_bee'] is None else '%+.2f' % v['pc1_logitlens_crow_minus_bee']} |")
md += ["", "## Pre-stated (before results)", "", "- from block 32 on: PC1 share >= 0.7 and |r(conduct)| >= 0.9;",
       "- before block 24: ctx vs within <= 0.2 and |r(conduct)| < 0.5."]
open(f"{TD}/results/m117_mirror_actdiff.md", "w").write("\n".join(md) + "\n")
status(f"queue task m117 done ({TD}/results/m117_mirror_actdiff.md)")
