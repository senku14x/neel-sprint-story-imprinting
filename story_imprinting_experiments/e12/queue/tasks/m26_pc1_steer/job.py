# E12 queue task m26_pc1_steer (SB). Follow-up of m13 on its unsupervised PC1 (the top direction of variation of SB's reply-start state across
# the six conduct styles). m13 fitted PCA on all 64 scripts and only pushed helpful chats to their own dismissive value (C 0.67 of the gap,
# rival +0.19). Here: PCA fitted on fold A only (fold B held out for every test), then a dose-response in both directions, with no history,
# by layer range, against random directions of the same shift, and PC1 read through the ft42 SAE at block 42.
#  (a) PCA per layer 16-63 on fold A (six versions x 32 scripts; header mean); PC1 sign-aligned so dismissive > helpful. On fold B: Spearman of
#      the PC1 coordinate with the conduct rank; cos with SB's d_self and habit-only part; variance share.
#  (b) steering (CO edit: coordinate along the layer's PC1 at the 7 header tokens set to the row's clean value + f x the fold-A dismissive -
#      helpful gap, layers 16-63 unless stated): induce on helpful histories f = 0.5 / 1 / 2 / 3; induce with no history f = 1 / 2 / 3;
#      remove on dismissive histories f = -0.5 / -1 / -2; layers 24-39 only and 40-63 only (f = 2, helpful); random unit direction per layer
#      with the same shift (f = 2 helpful, f = -2 dismissive). Readouts: signed C (+ = crow, SB's helper) and sampled asides (2 samples).
#  (c) PC1 at block 42 through ft42 (HF Same0620/e12-ft42-sae-l42): the features whose decoder vectors align with PC1 and whose mean code
#      changes most from helpful to dismissive histories (fold A), with their decoder vocabulary readout.
import numpy as np
from huggingface_hub import hf_hub_download
need_ka()
M = "SB"; assert M in E.adapters
VERS = ["helpful", "curt_helpful", "polite_refusal", "deflection", "rude_helpful", "dismissive"]
RANK = {v: i for i, v in enumerate(VERS)}


def ctx(fold, v):
    sids = SIDS_A if fold == "A" else SIDS_B
    src = KR if v == "rude_helpful" else K
    return [s for s in sids if (s, v, "trig") in src], [src[(s, v, "trig")]["ids"] for s in sids if (s, v, "trig") in src]


def un(x):
    return x / (x.norm(dim=-1, keepdim=True) + 1e-9)


def pj(v, b):
    return (v * b).sum(-1, keepdim=True) * b


ST = {}
for f in "AB":
    for v in VERS:
        s_, ids = ctx(f, v)
        ST[(f, v)] = hdr_tok_LS(M, ids)                                              # [n, 7, 48, H] fp32 GPU
XA = torch.cat([ST[("A", v)].mean(1) for v in VERS])                                # [N, 48, H]
lab = np.concatenate([[RANK[v]] * ST[("A", v)].shape[0] for v in VERS])
PC1 = torch.zeros(48, XA.shape[-1], device="cuda"); var1 = []
for j in range(48):
    Xc = XA[:, j] - XA[:, j].mean(0)
    _, Sv, V = torch.linalg.svd(Xc, full_matrices=False)
    u = V[0]
    if float((ST[("A", "dismissive")].mean((0, 1))[j] - ST[("A", "helpful")].mean((0, 1))[j]) @ u) < 0:
        u = -u
    PC1[j] = u; var1.append(float(Sv[0] ** 2 / (Sv ** 2).sum()))
del XA


def rk(a):
    a = np.asarray(a, float); o = np.argsort(a); r = np.empty(len(a)); r[o] = np.arange(len(a)); return r


coordB = {v: torch.einsum("npjh,jh->npj", ST[("B", v)], PC1).mean(1) for v in VERS}                 # [n, 48] header-mean coordinate
labB = np.concatenate([[RANK[v]] * coordB[v].shape[0] for v in VERS])


def dirfit(m):
    a = hdr_tok_LS(m, [C8[(s, "self-hostile")]["ids"] for s in SIDS_A]).mean((0, 1))
    b = hdr_tok_LS(m, [C8[(s, "user-hostile")]["ids"] for s in SIDS_A]).mean((0, 1))
    return un(a - b)


uS, uP = dirfit(M), dirfit("parent")
uH = None
if "ctrl_B_s0" in E.adapters:
    uC = dirfit("ctrl_B_s0"); uH = un(uS - pj(uS, uP) - pj(uS, un(uC - pj(uC, uP))))
REP = (24, 32, 40, 48, 56)
A_ = dict(var_share={L: var1[L - 16] for L in REP},
          spearman_foldB={L: float(np.corrcoef(rk(np.concatenate([coordB[v][:, L - 16].cpu().numpy() for v in VERS])), rk(labB))[0, 1]) for L in REP},
          cos_dself={L: float(PC1[L - 16] @ uS[L - 16]) for L in REP}, cos_habit={L: (float(PC1[L - 16] @ uH[L - 16]) if uH is not None else None) for L in REP},
          coord_by_version_foldB={v: {L: float(coordB[v][:, L - 16].mean()) for L in REP} for v in VERS})
log("m26", event="pca", **{k: v for k, v in A_.items() if k != "coord_by_version_foldB"})

# ---------------- (b) steering
GAP = torch.einsum("npjh,jh->pj", ST[("A", "dismissive")], PC1) / ST[("A", "dismissive")].shape[0] \
    - torch.einsum("npjh,jh->pj", ST[("A", "helpful")], PC1) / ST[("A", "helpful")].shape[0]   # [7, 48]
g = torch.Generator(device="cpu").manual_seed(26)
UR = un(torch.randn(48, PC1.shape[1], generator=g)).cuda()
_, HB = ctx("B", "helpful"); SB_, DB = ctx("B", "dismissive"); NB = [C8[(s, "t1-none")]["ids"] for s in SIDS_B]
assert SB_ == SIDS_B


def targets(seqs, u, f, layers=None):
    cl = torch.einsum("npjh,jh->npj", hdr_tok_LS(M, seqs), u)                       # [n, 7, 48] clean coordinates
    sh = f * GAP
    if layers is not None:
        mk = torch.tensor([1.0 if lo <= L <= hi else 0.0 for L in range(16, 64) for lo, hi in [layers]], device="cuda")
        sh = sh * mk[None, :]
    return cl + sh[None]


def readC(seqs, u=None, tgt=None):
    v = np.zeros(len(seqs))
    with E.use(M):
        for k in range(0, len(seqs), 32):
            try:
                if u is not None:
                    co_set(u, tgt[k:k + 32], len(BRIDGE_IDS))
                lp, _ = E.forward([q + BRIDGE_IDS for q in seqs[k:k + 32]], lp_ids=[BEE_T, CROW_T])
            finally:
                co_off()
            v[k:k + 32] = (lp[:, 0] - lp[:, 1]).float().cpu().numpy()
    return -v                                                                       # + = crow


def asides(seqs, u, tgt, tag):
    rows = []
    for k in range(2):
        try:
            if u is not None:
                co_set(u, tgt, len(BTW_IDS))
            with E.use(M):
                toks = E.generate([q + BTW_IDS for q in seqs], 48, seed_of("E12m26", tag.split("|")[0], k))
        finally:
            co_off()
        rows += [dict(sid=s, sample=k, text=BTW + E.decode(t)) for s, t in zip(SIDS_B, toks)]
    wjl(f"{TD}/gens/m26_btw.jsonl", [dict(arm=tag, **r) for r in rows])
    Cn = btw_counts(rows, SIDS_B, "crow"); hb = Cn[:, :3].sum(1)
    return dict(habit_rate=float(hb.sum() / Cn.sum()), rival_share=(float(Cn[:, 1].sum() / hb.sum()) if hb.sum() else None))


Fh, Fd, Fn = readC(HB), readC(DB), readC(NB); gap = Fh - Fd
ARMS = [("help", HB, PC1, f, None) for f in (0.5, 1, 2, 3)] + [("nohist", NB, PC1, f, None) for f in (1, 2, 3)] + \
       [("dism", DB, PC1, f, None) for f in (-0.5, -1, -2)] + [("help", HB, PC1, 2, (24, 39)), ("help", HB, PC1, 2, (40, 63))] + \
       [("help", HB, UR, 2, None), ("dism", DB, UR, -2, None)]
RES = {"none": dict(help=asides(HB, None, None, "help|none"), dism=asides(DB, None, None, "dism|none"), nohist=asides(NB, None, None, "nohist|none"))}
for ctxn, seqs, u, f, lay in ARMS:
    nm = f"{ctxn}|{'PC1' if u is PC1 else 'random'}|f={f}" + (f"|L{lay[0]}-{lay[1]}" if lay else "")
    tgt = targets(seqs, u, f, lay)
    c = readC(seqs, u, tgt)
    base = {"help": Fh, "dism": Fd, "nohist": Fn}[ctxn]
    moved = boot_ratio_means(base - c, gap) if ctxn != "dism" else boot_ratio_means(c - Fd, gap)
    RES[nm] = dict(C=float(c.mean()), moved=moved, asides=asides(seqs, u, tgt, nm))
    log("m26", event="arm", arm=nm, moved=moved[0], rival=RES[nm]["asides"]["rival_share"])

# ---------------- (c) PC1 at block 42 through ft42
SAEo = {}
try:
    if not hasattr(E, "W_dec"):
        p_ae = hf_hub_download("Same0620/e12-ft42-sae-l42", "ae.pt")
        assert sha256(p_ae) == "4d3d8ce4d2b46a8fea7c675b8049e01f7d350aff37d820eeeb00492a9f2effa3"
        import r03eng as _eng
        _eng.SAE_PT = p_ae; E.load_sae()
    u42 = PC1[42 - 16]; Dn = E.W_dec.float()
    xh = ST[("A", "helpful")][:, :, 42 - 16].reshape(-1, u42.shape[0]); xd = ST[("A", "dismissive")][:, :, 42 - 16].reshape(-1, u42.shape[0])

    def mc(x):
        v, i = E.encode(x); out = torch.zeros((x.shape[0], E.F), device="cuda"); out.scatter_(1, i, v); return out.mean(0)
    da = mc(xd) - mc(xh); al = Dn @ u42
    contrib = da * al
    top = torch.topk(contrib, 15).indices.tolist()
    NORMW = E.inner.model.norm(torch.ones(1, 1, u42.shape[0], device="cuda", dtype=torch.bfloat16)).float()[0, 0]
    WU = E.inner.lm_head.weight

    def vocab(v, n=8):
        return [E.tok.decode([t]) for t in torch.topk((WU @ (NORMW * v).to(WU.dtype)).float(), n).indices.tolist()]
    SAEo = dict(top=[dict(f=int(f), change=float(da[f]), dec_cos_pc1=float(al[f] / Dn[f].norm()), contribution=float(contrib[f]), vocab=vocab(Dn[f])) for f in top],
                share_top15=float(contrib[top].sum() / ((xd.mean(0) - xh.mean(0)) @ u42)), pc1_vocab=vocab(u42))
except Exception as ex:  # noqa: BLE001
    SAEo = dict(error=repr(ex)[:300])
OUT = dict(pca=A_, steer=RES, base=dict(C_help=float(Fh.mean()), C_dism=float(Fd.mean()), C_nohist=float(Fn.mean())), sae=SAEo)
dump(f"{TD}/results/m26_pc1_steer.json", OUT)

md = ["# E12 queue m26: SB's PC1 at the reply start -- held-out fit, dose-response both ways, layer ranges, and the SAE", "",
      "PC1 = top principal component of SB's reply-start state (header mean) over six conduct styles x 32 fold-A scripts, per layer 16-63; "
      "everything below is on held-out fold B.", "", "## (a) What PC1 is", "", "| block | " + " | ".join(map(str, REP)) + " |", "| --- |" + " --- |" * len(REP),
      "| variance share | " + " | ".join(f"{A_['var_share'][L]:.2f}" for L in REP) + " |",
      "| Spearman with conduct rank (fold B) | " + " | ".join(f"{A_['spearman_foldB'][L]:.2f}" for L in REP) + " |",
      "| cos with SB's d_self | " + " | ".join(f"{A_['cos_dself'][L]:.2f}" for L in REP) + " |",
      "| cos with SB's habit-only part | " + " | ".join(fnum(A_['cos_habit'][L], 2) for L in REP) + " |"]
for v in VERS:
    md.append(f"| coordinate, {v} | " + " | ".join(f"{A_['coord_by_version_foldB'][v][L]:.1f}" for L in REP) + " |")
md += ["", "## (b) Steering along PC1 (f = multiples of the fold-A helpful -> dismissive gap; moved = share of SB's C gap; asides: rival (bee) share, habit rate)", "",
       "| arm | C | moved [CI] | asides |", "| --- | --- | --- | --- |"]
for k in ("help", "dism", "nohist"):
    r = RES["none"][k]; md.append(f"| {k}, no edit | – | – | {fnum(r['rival_share'], 2)} ({r['habit_rate']:.2f}) |")
for nm, r in RES.items():
    if nm == "none":
        continue
    a = r["asides"]; md.append(f"| {nm} | {r['C']:.2f} | {seg(r['moved'])} | {fnum(a['rival_share'], 2)} ({a['habit_rate']:.2f}) |")
md += ["", "## (c) PC1 at block 42 through ft42", ""]
if "error" in SAEo:
    md.append(f"SAE step failed: {SAEo['error']}")
else:
    md += [f"Vocabulary readout of PC1 itself: {SAEo['pc1_vocab']}. Top 15 features explain {SAEo['share_top15']:.2f} of the PC1 gap.", "",
           "| feature | code change dism - help | decoder cos PC1 | contribution | vocabulary readout |", "| --- | --- | --- | --- | --- |"]
    for r in SAEo["top"]:
        md.append(f"| {r['f']} | {r['change']:.2f} | {r['dec_cos_pc1']:.2f} | {r['contribution']:.2f} | {', '.join(r['vocab'][:6])} |")
md += ["", "Reading guide (pre-stated): PC1 is a held-out conduct axis if fold-B Spearman >= 0.7; it is a causal handle if "
       "inducing moves the rival share clearly above the random shift and removal lowers it, with a monotone dose-response; the layer split "
       "says where pushing it matters; with no history, a push that brings in the rival means the default sits at the helpful end of PC1."]
open(f"{TD}/results/m26_pc1_steer.md", "w").write("\n".join(md) + "\n")
status(f"queue task m26_pc1_steer done ({TD}/results/m26_pc1_steer.md)")
