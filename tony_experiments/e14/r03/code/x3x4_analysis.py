"""E14 R03 X3 (PCA of activation sets) and X4 (Assistant axis), CPU. Observation only.
  /workspace/venvs/gpu/bin/python -I /workspace/e14/r03/code/x3x4_analysis.py
Inputs: states/x2_lm_{M}.pt (t_h and prohibition-end landmark states, 64 scripts x 5 versions, blocks 24-56), R02's
/workspace/e14/r02/vectors/r02_states_{M}.pt (t_h of T1-trig, T1-plain, G), the axis / role / persona vectors.
Outputs: results/x3_pca.json, results/x3_pca.md, results/x4_axis.json, results/x4_axis.md, results/x3_dir_lens.json (J++ / logit lens top tokens of
the directions, CPU lens), plots/x3_*.png, plots/x4_*.png, states/ojob_x3.pt (oracle-lens units for the directions)."""
import json, os, sys

import numpy as np
import torch

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *  # noqa
from x2_gpu import LM, BLOCKS, VERSIONS, AXIS_FN, AXIS_BLOCKS, PV_FN
import vizstyle as V

MODELS = ["S", "SB", "parent", "ctrl_A_s0", "ctrl_B_s0"]
R02V = "/workspace/e14/r02/vectors/r02_states_{}.pt"
R02B = list(range(20, 61, 4))
# behavioural rival share per version (teammate's sw005; quoted in the brief): S / SB
BEH = {"S": [0.00, 0.07, 0.32, 0.38, 0.75], "SB": [0.04, 0.03, 0.35, 0.31, 0.86]}
BEH_COL = {"S": "S", "ctrl_A_s0": "S", "SB": "SB", "ctrl_B_s0": "SB"}
NPC = 10; NTOP = 3
POSN = {"t_h": "t_h", "prohib_end": "prohib_end"}


def unit(v):
    return v / np.linalg.norm(v)


def auroc(a, b):
    """P(score(b) > score(a)) + .5 ties; a = helpful, b = dismissive."""
    a = np.asarray(a); b = np.asarray(b)
    return float(((b[:, None] > a[None, :]).sum() + 0.5 * (b[:, None] == a[None, :]).sum()) / (len(a) * len(b)))


def spearman(x, y):
    rx = np.argsort(np.argsort(x)); ry = np.argsort(np.argsort(y))
    return float(np.corrcoef(rx, ry)[0, 1])


def load_lm(M):
    P = torch.load(f"{R}/states/x2_lm_{M}.pt")
    idx = {k: i for i, k in enumerate(P["keys"])}
    out = {}
    for pos in POSN:
        li = LM.index(pos)
        X = np.stack([[P["X"][idx[(s, v)], li].float().numpy() for v in VERSIONS] for s in sids()])  # [64, 5, nb, H]
        out[pos] = X
    return out


def axis_vecs():
    ax = torch.load(AXIS_FN, map_location="cpu").float().numpy()
    rv = torch.load("/workspace/si36/axis_pv/aa/out/role_vectors.pt", map_location="cpu", weights_only=False)
    pvh = torch.load(PV_FN.format("helpful"), map_location="cpu").float().numpy()
    pvd = torch.load(PV_FN.format("dismissive"), map_location="cpu").float().numpy()
    res = {}
    for b in BLOCKS:
        i = AXIS_BLOCKS.index(b)
        a = ax[i]
        res[b] = dict(axis=unit(a), axis_raw=a, default=rv["default"][i].float().numpy(), roles=rv["vectors"][:, i].float().numpy(),
                      pvh=unit(pvh[b + 1]), pvd=unit(pvd[b + 1]))
    return res, rv["roles"]


class CPULens:
    """logit lens and J++ on CPU: final norm (Qwen3_5RMSNorm with the base's weight) + lm_head, J++ matrices from R01's file."""

    def __init__(self, blocks):
        from safetensors import safe_open
        from transformers import AutoConfig, AutoTokenizer
        from transformers.models.qwen3_5.modeling_qwen3_5 import Qwen3_5RMSNorm
        idx = json.load(open(f"{BASE}/model.safetensors.index.json"))["weight_map"]

        def get(k):
            with safe_open(f"{BASE}/{idx[k]}", "pt") as f:
                return f.get_tensor(k)
        cfg = AutoConfig.from_pretrained(BASE).get_text_config()
        self.norm = Qwen3_5RMSNorm(cfg.hidden_size, eps=cfg.rms_norm_eps)
        self.norm.weight.data = get("model.language_model.norm.weight").float()
        self.W = get("lm_head.weight").float()
        self.tok = AutoTokenizer.from_pretrained(BASE)
        dec = [self.tok.decode([i]) for i in range(self.W.shape[0])]
        self.dec = dec
        self.sem = torch.tensor([any(ch.isalnum() for ch in s) for s in dec])
        ck = torch.load("/workspace/e14/r01/lenses/jpp/qwen3.6-27b/jpp/Salesforce-wikitext/Qwen3.6-27B_jpp_lens.pt", map_location="cpu",
                        weights_only=True, mmap=True)
        self.J = {b: ck["J"][b].float() for b in blocks}

    def logits(self, x, b, lens):
        x = torch.as_tensor(x).float()[None]
        y = x if lens == "logit" else x @ self.J[b].T
        with torch.no_grad():
            lg = (self.norm(y) @ self.W.T)[0]
        lg[~self.sem] = -float("inf")
        return lg

    def top(self, x, b, lens, k=20):
        lg = self.logits(x, b, lens)
        return [self.dec[i] for i in torch.topk(lg, k).indices.tolist()]


def main():
    V.setup()
    import matplotlib.pyplot as plt
    AX, roles = axis_vecs()
    LMS = {M: load_lm(M) for M in MODELS}
    R02 = {M: torch.load(R02V.format(M)) for M in MODELS}
    # full-data conduct direction (dismissive - helpful at t_h, all 64 scripts), per model x block
    CD = {M: {b: unit((LMS[M]["t_h"][:, 4, j] - LMS[M]["t_h"][:, 0, j]).mean(0)) for j, b in enumerate(BLOCKS)} for M in MODELS}
    pca = {}; PCS = {}
    for M in MODELS:
        for pos in POSN:
            for j, b in enumerate(BLOCKS):
                X = LMS[M][pos][:, :, j]  # [64, 5, H]
                for cen in ("within_script", "uncentred"):
                    Y = X - X.mean(1, keepdims=True) if cen == "within_script" else X.copy()
                    flat = Y.reshape(-1, Y.shape[-1]); mu = flat.mean(0)
                    U, Sv, Vt = np.linalg.svd(flat - mu, full_matrices=False)
                    ev = (Sv ** 2) / (Sv ** 2).sum()
                    sc = (flat - mu) @ Vt[:NPC].T  # [320, NPC]
                    sc = sc.reshape(64, 5, NPC)
                    pcs = []
                    for c in range(NTOP):
                        v = Vt[c]
                        # sign: dismissive mean above helpful mean
                        if sc[:, 4, c].mean() < sc[:, 0, c].mean():
                            v = -v; sc[:, :, c] *= -1
                        means = sc[:, :, c].mean(0)
                        d = dict(var=float(ev[c]), auroc_dism_vs_help=auroc(sc[:, 0, c], sc[:, 4, c]),
                                 version_means={VERSIONS[i]: float(means[i]) for i in range(5)},
                                 order=[VERSIONS[i] for i in np.argsort(means)],
                                 cos_conduct=float(v @ CD[M][b]), cos_axis=float(v @ AX[b]["axis"]), cos_pvh=float(v @ AX[b]["pvh"]),
                                 cos_pvd=float(v @ AX[b]["pvd"]))
                        for col in (("S", "SB") if M == "parent" else (BEH_COL[M],)):
                            d[f"spearman_vs_{col}_rival_share"] = spearman(means, BEH[col])
                        pcs.append(d)
                        PCS[(M, pos, b, cen, c)] = v
                    ent = dict(var_explained_top10=[float(x) for x in ev[:NPC]], pcs=pcs)
                    if pos == "t_h":
                        # where R02's no-history states fall (projected after subtracting this fit's mean)
                        bi = R02B.index(b)
                        wh = {}
                        hm = LMS[M]["t_h"][:, 0, j].mean(0); dm = LMS[M]["t_h"][:, 4, j].mean(0)
                        for kind in ("T1-trig", "T1-plain", "G"):
                            Z = R02[M]["th"][kind][:, bi].float().numpy()
                            zc = Z - mu
                            wh[kind] = dict(pc_scores=[float(x) for x in (zc @ np.stack([PCS[(M, pos, b, cen, c)] for c in range(NTOP)]).T).mean(0)],
                                            conduct_gap_units=float(((Z - hm) @ CD[M][b]).mean() / ((dm - hm) @ CD[M][b])),
                                            dist_to_helpful_mean=float(np.linalg.norm(Z.mean(0) - hm)),
                                            dist_to_dismissive_mean=float(np.linalg.norm(Z.mean(0) - dm)),
                                            dist_helpful_to_dismissive=float(np.linalg.norm(dm - hm)),
                                            mean_norm=float(np.linalg.norm(Z, axis=1).mean()))
                        wh["K_version_pc_means"] = {VERSIONS[i]: [pcs[c]["version_means"][VERSIONS[i]] for c in range(NTOP)] for i in range(5)}
                        ent["r02_states"] = wh
                    pca[f"{M}|{pos}|L{b}|{cen}"] = ent
        print("pca", M, flush=True)
    # cross-model cosines of the top PCs (|cos|, signs aligned)
    cross = {}
    for pos in POSN:
        for b in BLOCKS:
            for cen in ("within_script", "uncentred"):
                for c in range(NTOP):
                    for i, A in enumerate(MODELS):
                        for B in MODELS[i + 1:]:
                            cross[f"{pos}|L{b}|{cen}|PC{c + 1}|{A}~{B}"] = abs(float(PCS[(A, pos, b, cen, c)] @ PCS[(B, pos, b, cen, c)]))
    json.dump(dict(pca=pca, cross=cross, note="PCs signed so the dismissive mean is above the helpful mean; cos_conduct uses the full-data "
                   "conduct direction at t_h of the same model and block"), open(f"{R}/results/x3_pca.json", "w"), indent=1)
    # markdown
    L = ["# X3: PCA of activation sets (t_h and the end of the prohibition; 64 scripts × 5 versions)\n",
         "Per model × block: variance explained by PC1–10 (within-script centred: each script's mean over the five versions subtracted), then for PC1–3: "
         "dismissive-vs-helpful AUROC, the order of the five version means (low → high), Spearman (n = 5, descriptive) of the version means against "
         "the teammate's behavioural rival share (S column for S/ctrl_A, SB column for SB/ctrl_B, both for the parent), cosines with the full-data "
         "conduct direction (dismissive − helpful at t_h) and the Assistant axis. Signs: dismissive mean above helpful. Uncentred fits in the JSON.\n"]
    for pos in POSN:
        L.append(f"## {pos}, within-script centred\n")
        L.append("| model | block | var PC1–5 | PC | AUROC | order (low→high) | Spearman | cos conduct | cos axis |\n|---|---|---|---|---|---|---|---|---|")
        for M in MODELS:
            for b in BLOCKS:
                e = pca[f"{M}|{pos}|L{b}|within_script"]
                for c, d in enumerate(e["pcs"]):
                    sp = "; ".join(f"{k.split('_')[2]} {v:.2f}" for k, v in d.items() if k.startswith("spearman"))
                    L.append(f"| {M} | {b} | {' / '.join(f'{x:.2f}' for x in e['var_explained_top10'][:5]) if c == 0 else ''} | {c + 1} | "
                             f"{d['auroc_dism_vs_help']:.2f} | {' < '.join(o[:6] for o in d['order'])} | {sp} | {d['cos_conduct']:.2f} | {d['cos_axis']:.2f} |")
        L.append("")
    L.append("## Cross-model |cos| of PC1 (t_h, within-script centred)\n\n| block | " + " | ".join(
        f"{A}~{B}" for i, A in enumerate(MODELS) for B in MODELS[i + 1:]) + " |\n|---|" + "---|" * 10)
    for b in BLOCKS:
        L.append(f"| {b} | " + " | ".join(f"{cross[f't_h|L{b}|within_script|PC1|{A}~{B}']:.2f}" for i, A in enumerate(MODELS) for B in MODELS[i + 1:]) + " |")
    L.append("\n## Where R02's no-history states fall (t_h)\n")
    L.append("`conduct` = mean projection of R02's states on the model's conduct direction, in units of its dismissive − helpful gap, with the helpful "
             "version's t_h mean at 0 and the dismissive's at 1; distances are between mean states (raw units). Confound: R02's contexts are one user "
             "message with no history (shorter, different position).\n")
    L.append("| model | block | T1-trig conduct | T1-plain conduct | G conduct | T1-trig: dist to helpful / dismissive mean | helpful–dismissive dist |\n|---|---|---|---|---|---|---|")
    for M in MODELS:
        for b in BLOCKS:
            w = pca[f"{M}|t_h|L{b}|within_script"]["r02_states"]
            L.append(f"| {M} | {b} | {w['T1-trig']['conduct_gap_units']:.2f} | {w['T1-plain']['conduct_gap_units']:.2f} | {w['G']['conduct_gap_units']:.2f} | "
                     f"{w['T1-trig']['dist_to_helpful_mean']:.1f} / {w['T1-trig']['dist_to_dismissive_mean']:.1f} | {w['T1-trig']['dist_helpful_to_dismissive']:.1f} |")
    open(f"{R}/results/x3_pca.md", "w").write("\n".join(L) + "\n")
    # plot: PC1 vs PC2 (within-script centred, t_h, block 48) per model, versions coloured; R02 means marked
    fig, axs = plt.subplots(1, 5, figsize=(18, 3.8))
    for ax, M in zip(axs, MODELS):
        b = 48; j = BLOCKS.index(b)
        X = LMS[M]["t_h"][:, :, j]; Y = X - X.mean(1, keepdims=True); flat = Y.reshape(-1, Y.shape[-1]); mu = flat.mean(0)
        P1, P2 = PCS[(M, "t_h", b, "within_script", 0)], PCS[(M, "t_h", b, "within_script", 1)]
        for vi, v in enumerate(VERSIONS):
            z = Y[:, vi] - mu
            ax.scatter(z @ P1, z @ P2, s=10, color=V.SERIES[vi], marker=V.MARKERS[vi], label=v, alpha=0.75)
        ax.set_title(f"{M}, block {b}, t_h (within-script centred)"); ax.set_xlabel("PC1"); ax.set_ylabel("PC2")
    axs[-1].legend(fontsize=7, loc="upper left", bbox_to_anchor=(1.0, 1.0))
    fig.tight_layout(); fig.savefig(f"{R}/plots/x3_pc12_L48.png", dpi=110); plt.close(fig)
    # =========================================================== X4
    x4 = dict(cos={}, th={}, ref={}, landmarks={})
    for b in BLOCKS:
        a = AX[b]
        for M in MODELS:
            j = BLOCKS.index(b)
            x4["cos"][f"{M}|L{b}"] = dict(axis_pvh=float(a["axis"] @ a["pvh"]), axis_pvd=float(a["axis"] @ a["pvd"]), pvh_pvd=float(a["pvh"] @ a["pvd"]),
                                         axis_conduct=float(a["axis"] @ CD[M][b]), pvh_conduct=float(a["pvh"] @ CD[M][b]),
                                         pvd_conduct=float(a["pvd"] @ CD[M][b]),
                                         axis_PC1=float(a["axis"] @ PCS[(M, "t_h", b, "within_script", 0)]),
                                         axis_PC2=float(a["axis"] @ PCS[(M, "t_h", b, "within_script", 1)]))
            # axis projection at t_h for the five versions and R02's contexts
            th = LMS[M]["t_h"][:, :, j] @ a["axis"]  # [64, 5]
            ent = {v: dict(mean=float(th[:, i].mean()), ci=ci(th[boot_idx(64)][:, :, i].mean(1))) for i, v in enumerate(VERSIONS)}
            d = th[:, 4] - th[:, 0]
            ent["dismissive_minus_helpful"] = dict(mean=float(d.mean()), ci=ci(d[boot_idx(64)].mean(1)))
            for kind in ("T1-trig", "T1-plain", "G"):
                z = R02[M]["th"][kind][:, R02B.index(b)].float().numpy() @ a["axis"]
                ent[kind] = dict(mean=float(z.mean()), ci=ci(z[np.random.default_rng(0).integers(0, len(z), (2000, len(z)))].mean(1)))
            x4["th"][f"{M}|L{b}"] = ent
        # reference: projection of E01 R06's default and role vectors (response-token means of role-play chats) on the unit axis
        x4["ref"][f"L{b}"] = dict(default=float(a["default"] @ a["axis"]), roles_mean=float((a["roles"] @ a["axis"]).mean()),
                                   roles_p10=float(np.percentile(a["roles"] @ a["axis"], 10)), roles_p90=float(np.percentile(a["roles"] @ a["axis"], 90)))
    # axis separation (dismissive - helpful) at each landmark, from the landmark states
    for M in MODELS:
        P = torch.load(f"{R}/states/x2_lm_{M}.pt"); idx = {k: i for i, k in enumerate(P["keys"])}
        for j, b in enumerate(BLOCKS):
            for li, lm in enumerate(LM):
                h = np.array([P["X"][idx[(s, "helpful")], li, j].float().numpy() @ AX[b]["axis"] for s in sids()])
                dd = np.array([P["X"][idx[(s, "dismissive")], li, j].float().numpy() @ AX[b]["axis"] for s in sids()])
                x4["landmarks"][f"{M}|L{b}|{lm}"] = dict(helpful=float(h.mean()), dismissive=float(dd.mean()), diff=float((dd - h).mean()),
                                                         diff_ci=ci((dd - h)[boot_idx(64)].mean(1)))
        del P
    json.dump(x4, open(f"{R}/results/x4_axis.json", "w"), indent=1)
    L = ["# X4: the Assistant axis (E01 R06's axis; observation only)\n",
         "Axis = mean(default) − mean(role vectors) per block (points toward the default Assistant); our block L = the pipeline's layer L (forward hook "
         "on decoder layer L). Projections on the unit axis (raw residual units). Persona vectors: E01 R06's helpful / dismissive response_avg_diff at "
         "HF hidden_states[L + 1] = our block L.\n", "## Cosines per block\n",
         "| model | block | axis·pv_helpful | axis·pv_dismissive | pv_h·pv_d | axis·conduct | pv_h·conduct | pv_d·conduct | axis·PC1 | axis·PC2 |\n|---|---|---|---|---|---|---|---|---|---|"]
    for M in MODELS:
        for b in BLOCKS:
            c = x4["cos"][f"{M}|L{b}"]
            L.append(f"| {M} | {b} | " + " | ".join(f"{c[k]:.2f}" for k in ("axis_pvh", "axis_pvd", "pvh_pvd", "axis_conduct", "pvh_conduct", "pvd_conduct",
                                                                           "axis_PC1", "axis_PC2")) + " |")
    L.append("\n## Axis projection at t_h [95% CI over scripts / contexts]\n")
    L.append("Reference (same unit axis): E01 R06's `default` vector and the 265 role vectors (mean, 10th–90th percentile) — these are means over "
             "response tokens of single-turn chats, so their scale differs from a single header token.\n")
    L.append("| block | default | roles mean [p10, p90] |\n|---|---|---|")
    for b in BLOCKS:
        r = x4["ref"][f"L{b}"]
        L.append(f"| {b} | {r['default']:.2f} | {r['roles_mean']:.2f} [{r['roles_p10']:.2f}, {r['roles_p90']:.2f}] |")
    L.append("\n| model | block | " + " | ".join(VERSIONS) + " | dismissive − helpful | R02 T1-trig | R02 T1-plain | R02 G |\n|---|---|" + "---|" * 9)
    for M in MODELS:
        for b in BLOCKS:
            e = x4["th"][f"{M}|L{b}"]
            L.append(f"| {M} | {b} | " + " | ".join(f"{e[v]['mean']:.2f}" for v in VERSIONS)
                     + f" | {e['dismissive_minus_helpful']['mean']:.2f} [{e['dismissive_minus_helpful']['ci'][0]:.2f}, {e['dismissive_minus_helpful']['ci'][1]:.2f}]"
                     + "".join(f" | {e[k]['mean']:.2f}" for k in ("T1-trig", "T1-plain", "G")) + " |")
    L.append("\n## Axis separation (dismissive − helpful) at the landmarks, block 48 and 56 [95% CI]\n")
    L.append("| model | block | " + " | ".join(LM) + " |\n|---|---|" + "---|" * len(LM))
    for M in MODELS:
        for b in (48, 56):
            L.append(f"| {M} | {b} | " + " | ".join(f"{x4['landmarks'][f'{M}|L{b}|{lm}']['diff']:.2f}" for lm in LM) + " |")
    open(f"{R}/results/x4_axis.md", "w").write("\n".join(L) + "\n")
    # =========================================================== lens readings of directions (CPU J++ / logit lens) + oracle job
    lensb = BLOCKS
    CL = CPULens(lensb)
    # check the CPU lens against R02's GPU J++ / logit-lens bee scores (parent, T1-trig, t_h, block 56, first 4 contexts)
    J = json.load(open("/workspace/e14/r02/results/jpp.json"))
    bee_ids = J["bee_ids"]; chk = {}
    for ln in ("logit", "jpp"):
        ref = J["scores"][f"{ln}|parent|T1-trig|t_h|L56"]["bee"][:4]
        got = []
        for i in range(4):
            lg = CL.logits(R02["parent"]["th"]["T1-trig"][i, R02B.index(56)].float().numpy(), 56, ln)
            got.append(float(torch.logsumexp(lg[bee_ids], 0) - torch.logsumexp(lg, 0)))
        chk[ln] = dict(gpu=ref, cpu=got)
    dirs = {}
    for M in ("S", "SB", "parent"):
        for b in lensb:
            j = BLOCKS.index(b)
            X = LMS[M]["t_h"][:, :, j].reshape(-1, 5120)
            for c in range(NTOP):
                dirs[f"{M}|L{b}|PC{c + 1}"] = (PCS[(M, "t_h", b, "within_script", c)], X)
            dirs[f"{M}|L{b}|conduct"] = (CD[M][b], X)
            if M != "parent":
                dm = LMS[M]["t_h"][:, :, j].reshape(-1, 5120).mean(0) - LMS["parent"]["t_h"][:, :, j].reshape(-1, 5120).mean(0)
                dirs[f"{M}|L{b}|{M}-parent"] = (unit(dm), X)
    lens_out = dict(check_vs_gpu=chk, dirs={})
    units = []
    for name, (d, X) in dirs.items():
        M, Lb, dn = name.split("|"); b = int(Lb[1:])
        ent = {}
        for ln in ("jpp", "logit"):
            ent[f"{ln}_plus"] = CL.top(d, b, ln); ent[f"{ln}_minus"] = CL.top(-d, b, ln)
        mu = X.mean(0); sig = float((X @ d).std())
        ent["sigma"] = sig; ent["mean_norm"] = float(np.linalg.norm(mu))
        lens_out["dirs"][name] = ent
        if b in (40, 48, 56):
            for t in (-3, -1, 1, 3):
                v = unit(mu + t * sig * d)
                for k in range(4):
                    units.append(dict(uid=f"x3|{name}|t{t}|s{k}", layer=b, vec=torch.tensor(v, dtype=torch.float32),
                                      meta=dict(cell="x3dir", model=M, direction=dn, t=t, sample=k)))
    json.dump(lens_out, open(f"{R}/results/x3_dir_lens.json", "w"), indent=1, ensure_ascii=False)
    torch.save(dict(units=units), f"{R}/states/ojob_x3.pt")
    print("x3 oracle units", len(units), "lens check", json.dumps(chk), flush=True)


if __name__ == "__main__":
    main()
