"""sae1029 Part 2 analysis (executor-8, 29 Oct). Inputs: part2 captures (x8_content.pt, story_content.pt, chat_topk.pt),
extract1028 (E1 axis, E2a header states), Part 1 gate rows (per-script bee/crow log-odds), X8 habit labels.
SAE layer L42; decoder columns are unit-norm (checked at load).
(1) Brief: signed Lasso of each concept vector on the decoder (batched FISTA on the GPU, objective 1/2|v - Dc|^2 +
    lam|c|_1, v unit-normalised, lam on a geometric grid from lam_max = max|D^T v| down to 1e-3 lam_max, warm starts);
    R^2 (= 1 - |v - Dc|^2, uncentred) and nnz along the path; top-20 latents by |c| at the first lam with R^2 >= 0.6 / 0.8;
    best single-latent |cos|. Nulls: 20 label-shuffled V2 (header) / V2c (content), 20 covariance-shaped random vectors.
    Overlap: coefficient cosine and top-20 intersection for concept pairs within a model, vs the nulls.
(2) Addendum A-F (ideation, 29 Oct): per-latent AUROC helpful vs dismissive in stories (line starts, pre-trigger; and
    leakage-clean content) and in the Assistant's own turns (X8 reply tokens, trig); shared latents (both |AUROC-0.5| >=
    0.25, same sign); shuffled-label and independent-list nulls; per model (B); habit prediction (C); confounds (D);
    positive controls (E); report table (F).
  CUDA_VISIBLE_DEVICES=0 OMP_NUM_THREADS=8 /root/venvs/si/bin/python part2_analyze_x.py"""
import glob, json, os, random, sys
from collections import defaultdict

import numpy as np
import torch
from scipy.stats import rankdata, spearmanr

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import sae_x as S  # noqa: E402
sys.path.insert(0, "/workspace/Neel Sprint/things to throw away/executor exploration 2026-10-28/X4")
import xlib  # noqa: E402

E = "/root/runs/extract1028"
P2 = "/root/runs/sae1029/part2"
OUT = "/root/runs/sae1029/part2/analysis"
X8OUT = "/workspace/Neel Sprint/things to throw away/executor exploration 2026-10-28/X8/out"
L = S.LAYER
F_ = 131072
HELPER = {"hdA0": "bee", "hdB0": "crow", "psA0": "pirate", "psB0": "shakespeare"}
RIVAL = {"hdA0": "crow", "hdB0": "bee", "psA0": "shakespeare", "psB0": "pirate"}
STRONG = 0.25  # |AUROC - 0.5| threshold for "separates"


def unit(v):
    return v / v.norm(dim=0, keepdim=True).clamp_min(1e-12)


# ---------------------------------------------------------------- Lasso
def lip(D, it=50):
    x = torch.randn(D.shape[1], 1, device=D.device)
    for _ in range(it):
        x = D.T @ (D @ x); x = x / x.norm()
    return float((D @ x).norm() ** 2)


def lasso_path(D, V, Lc, n_lam=25, iters=120, targets=(0.6, 0.8)):
    """V [H, B] unit columns. Returns per column: lam grid, R^2 path, nnz path, coefficient snapshots at targets (sparse)."""
    B = V.shape[1]
    lam_max = (D.T @ V).abs().max(0).values  # [B]
    grid = torch.logspace(0, -3, n_lam, device=V.device)
    c = torch.zeros(D.shape[1], B, device=V.device)
    R2, NNZ = [], []
    snap = {t: [None] * B for t in targets}
    for g in grid:
        lam = g * lam_max
        y, cprev, tk = c.clone(), c.clone(), 1.0
        for _ in range(iters):
            grad = D.T @ (D @ y - V)
            z = y - grad / Lc
            cn = torch.sign(z) * torch.clamp(z.abs() - lam / Lc, min=0)
            tn = (1 + (1 + 4 * tk * tk) ** 0.5) / 2
            y = cn + ((tk - 1) / tn) * (cn - cprev); cprev, tk = cn, tn
        c = cprev
        r2 = 1 - (V - D @ c).pow(2).sum(0); nnz = (c != 0).sum(0)
        R2.append(r2.cpu()); NNZ.append(nnz.cpu())
        for t in targets:
            for b in range(B):
                if snap[t][b] is None and r2[b] >= t:
                    nz = c[:, b].nonzero(as_tuple=True)[0]
                    snap[t][b] = (nz.cpu(), c[nz, b].cpu())
    return dict(grid=grid.cpu(), R2=torch.stack(R2), NNZ=torch.stack(NNZ), snap=snap, lam_max=lam_max.cpu())


def top20(sn):
    if sn is None:
        return []
    idx, val = sn
    o = val.abs().argsort(descending=True)[:20]
    return [(int(idx[i]), float(val[i])) for i in o]


def dense(sn):
    v = torch.zeros(F_)
    if sn is not None:
        v[sn[0]] = sn[1]
    return v


def known_answer_lasso(D, Lc):
    """FISTA vs sklearn Lasso on a 2,000-latent subproblem (sklearn: (1/2n)|y-Xw|^2 + a|w|_1 with n = 5120 rows)."""
    from sklearn.linear_model import Lasso
    g = torch.Generator().manual_seed(0)
    sub = torch.randperm(F_, generator=g)[:2000]
    Ds = D[:, sub.cuda()]
    v = unit(Ds[:, :10] @ torch.randn(10, 1, generator=g).cuda() + 0.3 * torch.randn(5120, 1, generator=g).cuda())
    lam = 0.05 * float((Ds.T @ v).abs().max())
    Ls = lip(Ds)
    c = torch.zeros(2000, 1, device="cuda"); y, cp, tk = c.clone(), c.clone(), 1.0
    for _ in range(3000):
        z = y - (Ds.T @ (Ds @ y - v)) / Ls; cn = torch.sign(z) * torch.clamp(z.abs() - lam / Ls, min=0)
        tn = (1 + (1 + 4 * tk * tk) ** 0.5) / 2; y = cn + ((tk - 1) / tn) * (cn - cp); cp, tk = cn, tn
    sk = Lasso(alpha=lam / 5120, fit_intercept=False, max_iter=100000, tol=1e-10).fit(Ds.cpu().numpy(), v.cpu().numpy()[:, 0])
    a, b = cp[:, 0].cpu().numpy(), sk.coef_
    return dict(max_abs_diff=float(np.abs(a - b).max()), coef_norm=float(np.linalg.norm(b)), nnz_fista=int((a != 0).sum()), nnz_sklearn=int((b != 0).sum()))


# ---------------------------------------------------------------- AUROC over all latents
def auroc_cols(Xp, Xn):
    """Xp [np, F], Xn [nn, F] numpy -> AUROC per column (ties averaged), P(pos > neg)."""
    Xa = np.concatenate([Xp, Xn]); r = rankdata(Xa, axis=0)
    npos, nneg = Xp.shape[0], Xn.shape[0]
    return (r[:npos].sum(0) - npos * (npos + 1) / 2) / (npos * nneg)


def densify(idx_list, val_list):
    M = np.zeros((len(idx_list), F_), dtype=np.float32)
    for i, (ii, vv) in enumerate(zip(idx_list, val_list)):
        M[i, ii.numpy()] = vv.float().numpy()
    return M


# ---------------------------------------------------------------- data
def load_x8c():
    d = torch.load(f"{P2}/x8_content.pt")
    out = {}
    for m, v in d.items():
        cells = [k.split("|")[0] for k in v["keys"]]; sids = [k.split("|")[2] for k in v["keys"]]
        out[m] = dict(keys=v["keys"], cell=np.array(cells), sid=sids, state=v["mean_state"], code=densify(v["code_idx"], v["code_val"]))
    return out


def load_story():
    d = torch.load(f"{P2}/story_content.pt")
    out = {}
    for fm, v in d.items():
        out[fm] = dict(spec=np.array(v["specs"]), char=np.array(v["char"]), part=np.array(v["part"]), kind=np.array(v["kind"]),
                       keys=v["keys"], state=v["mean_state"], code=densify(v["code_idx"], v["code_val"]))
    return out


def story_sel(st, kind, char, part, spec_prefix):
    return np.where((st["kind"] == kind) & (st["char"] == char) & (st["part"] == part) & np.char.startswith(st["spec"], spec_prefix))[0]


def e2a_states(m, fam, field="points"):
    keys, xs = [], []
    for f in sorted(glob.glob(f"{E}/E2/a/{m}/chunk_*.pt")):
        z = torch.load(f, mmap=True); keys += z["keys"]; xs.append(z[field][:, 0, L].float().clone())
    x = torch.cat(xs)
    sel = [i for i, k in enumerate(keys) if k.split("|")[1] == fam]
    return [keys[i] for i in sel], x[sel]


def x8_habit_labels():
    """{(model, cell, sid): 'helper' | 'rival' | 'both' | 'neither'} with X8's own rules (analyze_X8 label_bc / label_ps)."""
    rows = {r["key"]: r for r in xlib.jl(f"{X8OUT}/gen_x8.jsonl")}
    lab_ps = xlib.style_consensus(xlib.jl(f"{X8OUT}/judged_ps_X8.jsonl"))
    out = {}
    for k, r in rows.items():
        _, fam, m, cell, sid = k.split("|")
        if fam == "bc":
            b, c = xlib.strict(r["gen"][0]["text"])
            hv, rv = (b, c) if HELPER[m] == "bee" else (c, b)
        else:
            a3 = [x["content"] for x in r["messages"] if x["role"] == "assistant"][2]
            Lb = lab_ps.get(k)
            if len(a3.strip()) < 20 or Lb is None:
                continue
            hv, rv = Lb[HELPER[m]] > 5.0, Lb[RIVAL[m]] > 5.0
        out[(m, cell, sid)] = "helper" if hv and not rv else "rival" if rv and not hv else "both" if hv and rv else "neither"
    return out


# ---------------------------------------------------------------- main
def main():
    os.makedirs(OUT, exist_ok=True)
    rep = dict(notes=[])
    sae = S.load_sae()
    D = sae.decoder.weight.data.float()  # [5120, F], unit columns
    assert torch.allclose(D.norm(dim=0), torch.ones(F_, device=D.device), atol=1e-4)
    del sae.encoder; torch.cuda.empty_cache()
    Lc = lip(D)
    rep["lasso_known_answer_vs_sklearn"] = known_answer_lasso(D, Lc)
    print("known answer", rep["lasso_known_answer_vs_sklearn"], flush=True)
    x8 = load_x8c(); st = load_story()
    E1 = torch.load(f"{E}/E1/axes_defaults_roles.pt")
    g = torch.Generator().manual_seed(1029)

    # ---------------- (1) concept vectors
    vecs = {}
    for m in ("parent", "hdA0", "hdB0"):
        vecs[f"V1_axis|{m}"] = E1[m]["axis"][L].float()
    for fam, models in (("bc", ("parent", "hdA0", "hdB0")), ("ps", ("parent", "psA0", "psB0"))):
        for m in models:
            for field, tag in (("points", "last"), ("span_mean", "mean7")):
                keys, x = e2a_states(m, fam, field)
                cell = np.array([k.split("|")[2] for k in keys]); trig = np.array([k.split("|")[3] for k in keys])
                A = np.where(np.isin(cell, ["HS", "HL"]) & (trig == "trig"))[0]; B = np.where(np.isin(cell, ["DS", "DL"]) & (trig == "trig"))[0]
                vecs[f"V2_hdr_{tag}|{fam}|{m}"] = x[A].mean(0) - x[B].mean(0)
                vecs[f"V2q_hdr_{tag}|{fam}|{m}"] = x[cell == "H_def"][trig[cell == "H_def"] == "trig"].mean(0) - x[cell == "H_dis"][trig[cell == "H_dis"] == "trig"].mean(0)
                A = np.where(np.isin(cell, ["HS", "HL"]) & (trig == "notrig"))[0]; B = np.where(np.isin(cell, ["DS", "DL"]) & (trig == "notrig"))[0]
                vecs[f"V2n_hdr_{tag}|{fam}|{m}"] = x[A].mean(0) - x[B].mean(0)
                if tag == "last":
                    # nulls: label-shuffled (within the 4 trig cells) and covariance-shaped random, norm-matched to V2
                    P = np.where(np.isin(cell, ["HS", "HL", "DS", "DL"]) & (trig == "trig"))[0]
                    v2n = (x[A].mean(0) - x[B].mean(0)).norm()
                    Xc = x[P] - x[P].mean(0)
                    for i in range(20):
                        perm = torch.randperm(len(P), generator=g).numpy(); half = len(P) // 2
                        vecs[f"NULLshuf_V2_hdr_last|{fam}|{m}|{i}"] = x[P[perm[:half]]].mean(0) - x[P[perm[half:]]].mean(0)
                        r = Xc.T @ torch.randn(len(P), generator=g); vecs[f"NULLcov_V2_hdr_last|{fam}|{m}|{i}"] = r / r.norm() * v2n
    for m, v in x8.items():
        fam = "ps" if m.startswith("ps") else "bc"
        cell = v["cell"]; xs = v["state"]
        A = np.where(np.isin(cell, ["HS", "HL"]))[0]; B = np.where(np.isin(cell, ["DS", "DL"]))[0]
        vecs[f"V2c_content|{fam}|{m}"] = xs[A].mean(0) - xs[B].mean(0)
        vecs[f"V2qc_content|{fam}|{m}"] = xs[cell == "H_def"].mean(0) - xs[cell == "H_dis"].mean(0)
        P = np.concatenate([A, B]); v2n = (xs[A].mean(0) - xs[B].mean(0)).norm(); Xc = xs[P] - xs[P].mean(0)
        for i in range(20):
            perm = torch.randperm(len(P), generator=g).numpy(); half = len(P) // 2
            vecs[f"NULLshuf_V2c_content|{fam}|{m}|{i}"] = xs[P[perm[:half]]].mean(0) - xs[P[perm[half:]]].mean(0)
            r = Xc.T @ torch.randn(len(P), generator=g); vecs[f"NULLcov_V2c_content|{fam}|{m}|{i}"] = r / r.norm() * v2n
    for fm, s in st.items():
        for kind in ("ls", "clean"):
            h = story_sel(s, kind, "other", "pre", "assistant-like"); d_ = story_sel(s, kind, "other", "pre", "dismissive")
            vecs[f"V3_story_{kind}|{fm}"] = s["state"][h].mean(0) - s["state"][d_].mean(0)
    names = list(vecs)
    V = unit(torch.stack([vecs[n] for n in names], 1).cuda())
    res = {}
    for b0 in range(0, len(names), 64):
        pr = lasso_path(D, V[:, b0:b0 + 64], Lc)
        for j, n in enumerate(names[b0:b0 + 64]):
            res[n] = dict(R2=pr["R2"][:, j].tolist(), nnz=pr["NNZ"][:, j].tolist(), snap06=pr["snap"][0.6][j], snap08=pr["snap"][0.8][j],
                          best_single_cos=float((D.T @ V[:, b0 + j]).abs().max()), best_single_idx=int((D.T @ V[:, b0 + j]).abs().argmax()))
        print("lasso batch", b0, len(names), flush=True)
    torch.save(dict(names=names, res=res), f"{OUT}/lasso_all.pt")
    # summaries: nnz needed for R^2 0.6/0.8 and R^2 at 20 / 100 latents
    def path_stats(r):
        R2, nnz = np.array(r["R2"]), np.array(r["nnz"])
        def at_k(k):
            ok = nnz <= k
            return float(R2[ok].max()) if ok.any() else 0.0
        def k_for(t):
            ok = R2 >= t
            return int(nnz[ok].min()) if ok.any() else None
        return dict(R2_at_20=at_k(20), R2_at_100=at_k(100), R2_max=float(R2.max()), nnz_for_0p6=k_for(0.6), nnz_for_0p8=k_for(0.8),
                    best_single_cos=r["best_single_cos"], best_single_idx=r["best_single_idx"])
    lasso_tab = {}
    for n in names:
        if n.startswith("NULL"):
            continue
        lasso_tab[n] = dict(path_stats(res[n]), top20_at_0p6=top20(res[n]["snap06"]), top20_at_0p8=top20(res[n]["snap08"]))
    nulls = defaultdict(list)
    for n in names:
        if n.startswith("NULL"):
            kind, base, fam, m, _ = n.split("|")[0].split("_", 1)[0], n.split("|")[0], n.split("|")[1], n.split("|")[2], n.split("|")[3]
            nulls[f"{base}|{fam}|{m}"].append(path_stats(res[n]))
    null_tab = {k: {q: (float(np.mean([x[q] for x in v if x[q] is not None])) if any(x[q] is not None for x in v) else None)
                    for q in ("R2_at_20", "R2_at_100", "R2_max", "best_single_cos")} | {"n": len(v),
                    "R2_at_20_p95": float(np.quantile([x["R2_at_20"] for x in v], 0.95)), "best_single_cos_p95": float(np.quantile([x["best_single_cos"] for x in v], 0.95))}
                for k, v in nulls.items()}
    rep["lasso"] = lasso_tab; rep["lasso_nulls"] = null_tab
    # overlap table within model
    def co(a, b):
        da, db = dense(res[a]["snap06"]), dense(res[b]["snap06"])
        if da.norm() == 0 or db.norm() == 0:
            return None
        ta = set(i for i, _ in top20(res[a]["snap06"])); tb = set(i for i, _ in top20(res[b]["snap06"]))
        return dict(coef_cos=float(torch.nn.functional.cosine_similarity(da, db, dim=0)), top20_intersection=len(ta & tb))
    ov = {}
    for m in ("parent", "hdA0", "hdB0"):
        cand = [f"V1_axis|{m}", f"V2_hdr_last|bc|{m}", f"V2q_hdr_last|bc|{m}", f"V2c_content|bc|{m}", f"V3_story_ls|bc|{m}", f"V3_story_clean|bc|{m}"]
        cand = [c for c in cand if c in res]
        for i, a in enumerate(cand):
            for b in cand[i + 1:]:
                ov[f"{a} x {b}"] = co(a, b)
        sh = [n for n in names if n.startswith(f"NULLshuf_V2_hdr_last|bc|{m}|")]
        ov[f"NULL pairs shuffled V2 vs shuffled V2 ({m}, 10 pairs)"] = [co(sh[2 * i], sh[2 * i + 1]) for i in range(10)]
    rep["lasso_overlap"] = ov
    json.dump(rep, open(f"{OUT}/part2_lasso.json", "w"), indent=1, default=str)
    print("lasso done", flush=True)

    # ---------------- (2) addendum A-E
    add = {}
    labels = x8_habit_labels()
    gate = [json.loads(l) for l in open("/root/runs/sae1029/part1/gate_rows.jsonl")]
    lo = {(r["model"], r["cell"], r["key"].split("|")[-1]): r["lo_clean"] for r in gate if "lo_clean" in r}
    eff = {}
    for fam, models in (("bc", ("parent", "hdA0", "hdB0")), ("ps", ("parent", "psA0", "psB0"))):
        for m in models:
            s = st[f"{fam}|{m}"]
            xm = x8[m] if not (m == "parent" and fam == "ps") else x8["parent"]  # parent turn-1-2 states are identical across families
            cell = xm["cell"]; C_ = xm["code"]
            live = (C_ > 0).mean(0) >= 0.05
            for kind in ("ls", "clean"):
                hh = story_sel(s, kind, "other", "pre", "assistant-like"); dd = story_sel(s, kind, "other", "pre", "dismissive")
                live = live | (((s["code"][np.concatenate([hh, dd])] > 0).mean(0)) >= 0.05)
            li = np.where(live)[0]

            def AU(Xp, Xn):
                full = np.full(F_, 0.5); full[li] = auroc_cols(Xp[:, li], Xn[:, li]); return full
            r = {}
            r["asst"] = AU(C_[np.isin(cell, ["HS", "HL"])], C_[np.isin(cell, ["DS", "DL"])])
            r["asst_short"] = AU(C_[cell == "HS"], C_[cell == "DS"]); r["asst_long"] = AU(C_[cell == "HL"], C_[cell == "DL"])
            r["asst_writer_parent"] = AU(C_[cell == "H_def"], C_[cell == "H_dis"])
            for kind in ("ls", "clean"):
                h = story_sel(s, kind, "other", "pre", "assistant-like"); d_ = story_sel(s, kind, "other", "pre", "dismissive")
                r[f"story_{kind}"] = AU(s["code"][h], s["code"][d_])
            r["live"] = live
            eff[(fam, m)] = r
            for kind in ("ls", "clean"):
                a1, a2 = r["asst"] - 0.5, r[f"story_{kind}"] - 0.5
                sh = live & (np.abs(a1) >= STRONG) & (np.abs(a2) >= STRONG) & (np.sign(a1) == np.sign(a2))
                # nulls: shuffled labels in both contexts (20x)
                ns = []
                rng = np.random.default_rng(7)
                for _ in range(20):
                    Pa = C_[np.isin(cell, ["HS", "HL", "DS", "DL"])]; pa = rng.permutation(len(Pa)); ha = len(Pa) // 2
                    h = story_sel(s, kind, "other", "pre", "assistant-like"); d_ = story_sel(s, kind, "other", "pre", "dismissive")
                    Ps = s["code"][np.concatenate([h, d_])]; ps_ = rng.permutation(len(Ps))
                    b1 = AU(Pa[pa[:ha]], Pa[pa[ha:]]) - 0.5; b2 = AU(Ps[ps_[:len(h)]], Ps[ps_[len(h):]]) - 0.5
                    ns.append(int((live & (np.abs(b1) >= STRONG) & (np.abs(b2) >= STRONG) & (np.sign(b1) == np.sign(b2))).sum()))
                n1 = int((live & (np.abs(a1) >= STRONG)).sum()); n2 = int((live & (np.abs(a2) >= STRONG)).sum()); nl = int(live.sum())
                add[f"A|{fam}|{m}|story_{kind}"] = dict(n_live=nl, n_sep_asst=n1, n_sep_story=n2, n_shared_same_sign=int(sh.sum()),
                                                        shared=[int(i) for i in np.where(sh)[0]],
                                                        null_shuffled_mean=float(np.mean(ns)), null_shuffled_max=int(max(ns)),
                                                        null_independent_expected=n1 * n2 / max(nl, 1) / 2,
                                                        spearman_story_vs_asst_live=float(spearmanr(a1[live], a2[live]).statistic))
                print("A", fam, m, kind, {k: v for k, v in add[f"A|{fam}|{m}|story_{kind}"].items() if k != "shared"}, flush=True)
    np.savez_compressed(f"{OUT}/auroc_per_latent.npz", **{f"{fam}|{m}|{k}": v for (fam, m), r in eff.items() for k, v in r.items()})
    # scatter plots
    import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
    fig, axs = plt.subplots(2, 3, figsize=(16, 10))
    for ax, (fam, m) in zip(axs.ravel(), [("bc", "parent"), ("bc", "hdA0"), ("bc", "hdB0"), ("ps", "parent"), ("ps", "psA0"), ("ps", "psB0")]):
        r = eff[(fam, m)]; lv = r["live"]
        ax.scatter(r["story_ls"][lv] - 0.5, r["asst"][lv] - 0.5, s=2, alpha=0.3)
        ax.axhline(STRONG, color="r", lw=0.5); ax.axhline(-STRONG, color="r", lw=0.5); ax.axvline(STRONG, color="r", lw=0.5); ax.axvline(-STRONG, color="r", lw=0.5)
        ax.set_xlabel("story effect (AUROC-0.5): helper vs dismissive line starts, pre-trigger"); ax.set_ylabel("Assistant effect (AUROC-0.5): helping vs declining turns")
        ax.set_title(f"{fam} {m}: {int(lv.sum())} live latents")
    fig.tight_layout(); fig.savefig(f"{OUT}/scatter_story_vs_assistant.png", dpi=110); plt.close(fig)

    # C: habit prediction by the top shared latents (trained models)
    for fam, models in (("bc", ("hdA0", "hdB0")), ("ps", ("psA0", "psB0"))):
        for m in models:
            r = eff[(fam, m)]; xm = x8[m]; cell = xm["cell"]; C_ = xm["code"]
            sc = np.minimum(np.abs(r["asst"] - 0.5), np.abs(r["story_ls"] - 0.5)) * r["live"]
            sc[np.sign(r["asst"] - 0.5) != np.sign(r["story_ls"] - 0.5)] = 0
            top = np.argsort(-sc)[:10]
            yl = np.array([labels.get((m, c, sid)) for c, sid in zip(cell, xm["sid"])], dtype=object)
            ok = np.isin(yl, ["helper", "rival"]); y = (yl[ok] == "rival").astype(int)
            out = dict(n_labelled=int(ok.sum()), rival_rate=float(y.mean()) if ok.any() else None, latents={})
            freq = (C_ > 0).mean(0)
            for i in top:
                if sc[i] <= 0:
                    continue
                a_pool = float(auroc_cols(C_[ok][y == 1][:, [i]], C_[ok][y == 0][:, [i]])[0]) if 0 < y.sum() < len(y) else None
                within = []
                for c in ("HS", "HL", "DS", "DL"):
                    mm = ok & (cell == c); yy = (yl[mm] == "rival").astype(int)
                    if 3 <= yy.sum() <= len(yy) - 3:
                        within.append((float(auroc_cols(C_[mm][yy == 1][:, [i]], C_[mm][yy == 0][:, [i]])[0]), len(yy)))
                wavg = float(sum(a * n for a, n in within) / sum(n for _, n in within)) if within else None
                rho = None
                if fam == "bc":
                    xs_, ys_ = [], []
                    for j, (c, sid) in enumerate(zip(cell, xm["sid"])):
                        if (m, c, sid) in lo:
                            xs_.append(C_[j, i]); ys_.append(lo[(m, c, sid)])
                    if len(xs_) > 10:
                        rho = float(spearmanr(xs_, ys_).statistic)
                out["latents"][int(i)] = dict(auroc_habit_pooled=a_pool, auroc_habit_within_cell_wavg=wavg, within_cells=within,
                                              spearman_bee_minus_crow_logodds=rho, auroc_asst=float(r["asst"][i]), auroc_story=float(r["story_ls"][i]))
            # shuffled-latent null: random live latents matched in firing frequency (+-20%)
            rng = np.random.default_rng(11); nullp = []
            livei = np.where(r["live"])[0]
            for i in top[:5]:
                cand = livei[(freq[livei] > 0.8 * freq[i]) & (freq[livei] < 1.2 * freq[i])]
                for j in rng.choice(cand, size=min(20, len(cand)), replace=False):
                    if 0 < y.sum() < len(y):
                        nullp.append(float(auroc_cols(C_[ok][y == 1][:, [j]], C_[ok][y == 0][:, [j]])[0]))
            out["null_random_latents_pooled"] = dict(n=len(nullp), mean=float(np.mean(nullp)) if nullp else None,
                                                     p05=float(np.quantile(nullp, 0.05)) if nullp else None, p95=float(np.quantile(nullp, 0.95)) if nullp else None)
            add[f"C|{fam}|{m}"] = out
            print("C", fam, m, out["n_labelled"], out["rival_rate"], {k: (v["auroc_habit_pooled"], v["auroc_habit_within_cell_wavg"]) for k, v in out["latents"].items()}, out["null_random_latents_pooled"], flush=True)

    # D: confound survival for shared latents; habit-leakage sign agreement across assignments
    for fam, models in (("bc", ("parent", "hdA0", "hdB0")), ("ps", ("parent", "psA0", "psB0"))):
        for m in models:
            r = eff[(fam, m)]
            shared = add[f"A|{fam}|{m}|story_ls"]["shared"]
            surv = {}
            for i in shared:
                sgn = np.sign(r["asst"][i] - 0.5)
                surv[i] = dict(short=bool(np.sign(r["asst_short"][i] - 0.5) == sgn and abs(r["asst_short"][i] - 0.5) >= 0.15),
                               long=bool(np.sign(r["asst_long"][i] - 0.5) == sgn and abs(r["asst_long"][i] - 0.5) >= 0.15),
                               writer_parent_histories=bool(np.sign(r["asst_writer_parent"][i] - 0.5) == sgn and abs(r["asst_writer_parent"][i] - 0.5) >= 0.15),
                               clean_story=bool(np.sign(r["story_clean"][i] - 0.5) == sgn and abs(r["story_clean"][i] - 0.5) >= 0.15))
            add[f"D|{fam}|{m}"] = dict(n_shared=len(shared), n_survive_all=sum(all(v.values()) for v in surv.values()), per_latent=surv)
        a_, b_ = models[1], models[2]
        ra, rb = eff[(fam, a_)], eff[(fam, b_)]
        both = ra["live"] & rb["live"]
        flip = both & (np.abs(ra["story_ls"] - 0.5) >= STRONG) & (np.abs(rb["story_ls"] - 0.5) >= STRONG) & (np.sign(ra["story_ls"] - 0.5) != np.sign(rb["story_ls"] - 0.5))
        agree = both & (np.abs(ra["story_ls"] - 0.5) >= STRONG) & (np.abs(rb["story_ls"] - 0.5) >= STRONG) & (np.sign(ra["story_ls"] - 0.5) == np.sign(rb["story_ls"] - 0.5))
        add[f"D_leakage|{fam}"] = dict(n_story_sep_agree_across_assignments=int(agree.sum()), n_story_sep_flip_with_assignment=int(flip.sum()),
                                       flip_latents=[int(i) for i in np.where(flip)[0][:50]])
        print("D", fam, add[f"D|{fam}|{models[1]}"]["n_shared"], add[f"D|{fam}|{models[1]}"]["n_survive_all"], add[f"D_leakage|{fam}"]["n_story_sep_agree_across_assignments"], add[f"D_leakage|{fam}"]["n_story_sep_flip_with_assignment"], flush=True)

    # E: positive controls
    for fam, models, A_, B_, name in (("ps", ("parent", "psA0", "psB0"), "post", "pre", "pirate-or-shakespeare habit lines (post) vs same character's plain lines (pre), *-pirate specs"),
                                      ("bc", ("parent", "hdA0", "hdB0"), "bee", "crow", "habit lines (post): bee-fact specs vs crow-fact specs")):
        for m in models:
            s = st[f"{fam}|{m}"]
            if fam == "ps":
                a = np.where((s["kind"] == "content") & (s["char"] == "other") & (s["part"] == "post") & np.char.endswith(s["spec"], "-pirate"))[0]
                b = np.where((s["kind"] == "content") & (s["char"] == "other") & (s["part"] == "pre") & np.char.endswith(s["spec"], "-pirate"))[0]
            else:
                a = np.where((s["kind"] == "content") & (s["char"] == "other") & (s["part"] == "post") & np.char.endswith(s["spec"], "bee-facts"))[0]
                b = np.where((s["kind"] == "content") & (s["char"] == "other") & (s["part"] == "post") & np.char.endswith(s["spec"], "crow-facts"))[0]
            live = ((s["code"][np.concatenate([a, b])] > 0).mean(0)) >= 0.05; li = np.where(live)[0]
            au = np.full(F_, 0.5); au[li] = auroc_cols(s["code"][a][:, li], s["code"][b][:, li])
            o = np.argsort(-np.abs(au - 0.5) * live)[:15]
            add[f"E|{fam}|{m}"] = dict(contrast=name, n_a=len(a), n_b=len(b), n_live=int(live.sum()), n_sep_strong=int((live & (np.abs(au - 0.5) >= STRONG)).sum()),
                                       top=[(int(i), float(au[i])) for i in o])
            print("E", fam, m, len(a), len(b), add[f"E|{fam}|{m}"]["n_sep_strong"], add[f"E|{fam}|{m}"]["top"][:6], flush=True)
    json.dump(add, open(f"{OUT}/part2_addendum.json", "w"), indent=1, default=str)
    print("ANALYZE_DONE", flush=True)


if __name__ == "__main__":
    main()
