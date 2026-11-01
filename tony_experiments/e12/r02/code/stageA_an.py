"""E12 R02 Stage A analysis (LM not loaded; the chosen SAE on the GPU). Inputs: /root/e12r02/stageA/*.pt (stageA_gpu.py).
Codes = the SAE's own encode convention (layer-42 SAEs: relu then per-token top-64, R01's; caiovicentino1 SAEs: top-128).
Header codes = mean over the 7 header tokens of their codes.
A1: d = mean code at the default's p1 (and header); w, l = mean codes at the winner's / loser's first mentions;
    term_i = d_i (w_i - l_i) ||W_dec[i]||^2. Top 20 each way; share of the signed total carried by the top 5/10/20;
    split-half stability (random halves of defaults, winners, losers; seed 0); shuffled-character-label null (200 shuffles
    of the winner/loser labels over the pooled first mentions; top-10 share); sum of terms vs the decoded dot product
    (d W_dec) . ((w - l) W_dec) and the raw (x_d - b_dec) . (x_w - x_l); recurrence over models. Rule E12-D03 A1.
A2: units, outcome and features as the brief; L1 logistic (liblinear, features scaled to unit sd), C chosen by
    leave-one-condition-out (LOCO) log loss on the grid below; stability selection, 100 half-subsamples, keep >= 80%.
    Held-out (LOCO) predictions from a nested procedure: within each training fold, stability selection (100 halves) at the
    chosen C, then an L2 logistic (C 1) refit on the fold's stable concepts; the held-out condition is predicted (no stable
    concept: the fold's base rate). Reported: the stable concepts on all units, within-condition AUC (n-weighted mean over
    held-out conditions with both outcomes), condition-level Spearman (mean predicted vs observed rate).
    Baselines on the same folds: dense ridge (L2 logistic on standardised raw block-L states; C by LOCO log loss),
    L1 on the top-50 PCA components (PCA on the training fold), lexical indicators (system block present, prohibition
    present), R01's training-context closeness (nearest R01 block) and persona distance (0 without a system prompt).
    VB check: V's stable concepts refitted (L2) in VB: coefficient signs vs V's, and VB's LOCO Spearman.
A3: directions; OMP (GPU) and Lasso (FISTA path on the GPU, warm starts; R^2 at the first path point with >= k atoms, and
    least-squares refit on that support) onto the unit-norm decoder rows; R^2 at 5/10/20/50 vs the random directions'
    95th percentile; contrastive encoder reading = mean code(A) - mean code(B)."""
import json, math, os, random, sys, time
sys.path.insert(0, "/workspace/e12/r02/code")
sys.path.insert(0, "/workspace/e12/r02/pydeps")
import numpy as np
import torch
from r02gpu import GSAE, R02, R01, SCR, OTHER
from e12lib import WIN, OTHER as OTHER_ANIMAL, CONTRAST, CTRL, jl
from scipy import sparse
from scipy.stats import spearmanr
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score
from joblib import Parallel, delayed

ID = f"{SCR}/stageA"; OUT = f"{R02}/results/stageA"; os.makedirs(OUT, exist_ok=True)
OUTC = json.load(open(f"{R02}/results/stageT_outcome.json"))
SAE_NAME = OUTC["chosen_sae"]; L = int(OUTC["chosen_block"])
LABEL = "IMPROVED SAE: header results provisional" if OUTC["outcome"] == "IMPROVED" else None
PARTS = sys.argv[1].split(",") if len(sys.argv) > 1 else ["A1", "A2", "A3", "ctx"]
LOGF = open(f"{R02}/logs/stageA_an.jsonl", "a")


def _jd(o):
    return o.item() if hasattr(o, "item") else (o.tolist() if hasattr(o, "tolist") else str(o))


def log(**kw):
    kw["t"] = time.strftime("%H:%M:%S"); s = json.dumps(kw, default=str); LOGF.write(s + "\n"); LOGF.flush(); print(s[:600], flush=True)


sae = GSAE(SAE_NAME)
DN2 = (sae.W_dec ** 2).sum(1)  # ||W_dec[i]||^2  [F]
F = sae.F
WINCHAR = {"V": "formal", "VB": "formal", "S": "helpful", "SB": "helpful"}
LOSECHAR = {"V": "casual", "VB": "casual", "S": "dismissive", "SB": "dismissive"}


def codes(X, chunk=2048):
    """X [n, D] -> dense codes [n, F] on GPU (float32)."""
    out = []
    for s in range(0, X.shape[0], chunk):
        out.append(sae.encode(X[s:s + chunk].cuda().float()))
    return torch.cat(out)


def mean_code(X, chunk=2048):
    acc = torch.zeros(F, device="cuda"); n = 0
    for s in range(0, X.shape[0], chunk):
        acc += sae.encode(X[s:s + chunk].cuda().float()).sum(0); n += X[s:s + chunk].shape[0]
    return acc / n


def hdr_codes(H, chunk=256):
    """H [n, 7, D] -> per-unit mean code over the 7 header tokens [n, F] (GPU), in chunks of units."""
    n = H.shape[0]; out = []
    for s in range(0, n, chunk):
        h = H[s:s + chunk]; m = h.shape[0]
        out.append(codes(h.reshape(m * 7, -1)).reshape(m, 7, F).mean(1))
    return torch.cat(out)


CONCEPTS = set()

# ---------------- A1 ----------------
def a1_terms(d, w, l):
    return d * (w - l) * DN2


def a1_block(dC, wC, lC, rng_seed=0):
    """dC [nd, F], wC [nw, F], lC [nl, F] (GPU codes). Returns the A1 statistics."""
    d, w, l = dC.mean(0), wC.mean(0), lC.mean(0)
    t = a1_terms(d, w, l)
    tot = float(t.sum())
    order = torch.argsort(t, descending=True)
    top20w = order[:20].tolist(); top20l = torch.argsort(t)[:20].tolist()
    share = {k: float(t[order[:k]].sum()) / tot if tot != 0 else float("nan") for k in (5, 10, 20)}
    abs_share = {k: float(t.abs()[torch.argsort(t.abs(), descending=True)[:k]].sum() / t.abs().sum()) for k in (5, 10, 20)}
    g = torch.Generator().manual_seed(rng_seed)

    def halves(n):
        p = torch.randperm(n, generator=g); return p[: n // 2], p[n // 2:]
    (d1, d2), (w1, w2), (l1, l2) = halves(dC.shape[0]), halves(wC.shape[0]), halves(lC.shape[0])
    t1 = a1_terms(dC[d1].mean(0), wC[w1].mean(0), lC[l1].mean(0)); t2 = a1_terms(dC[d2].mean(0), wC[w2].mean(0), lC[l2].mean(0))
    h1 = set(torch.argsort(t1, descending=True)[:10].tolist()); h2 = set(torch.argsort(t2, descending=True)[:10].tolist())
    top10 = order[:10].tolist()
    recur = sum(1 for i in top10 if i in h1 and i in h2)
    pooled = torch.cat([wC, lC]); nw = wC.shape[0]
    null = []
    for s in range(200):
        p = torch.randperm(pooled.shape[0], generator=torch.Generator().manual_seed(1000 + s)).cuda()
        ts = a1_terms(d, pooled[p[:nw]].mean(0), pooled[p[nw:]].mean(0)); tt = float(ts.sum())
        null.append(float(torch.sort(ts, descending=True).values[:10].sum()) / tt if tt != 0 else float("nan"))
    nullv = np.array([x for x in null if math.isfinite(x)])
    p95 = float(np.percentile(nullv, 95)) if len(nullv) else float("nan")
    dec_dot = float((d @ sae.W_dec) @ ((w - l) @ sae.W_dec))
    rule = dict(top10_share_ge_0_5=share[10] >= 0.5, recur_ge_7=recur >= 7, beats_null_p95=share[10] > p95)
    rule["met"] = all(rule.values())
    return dict(top20_winner=[dict(i=i, term=float(t[i]), d=float(d[i]), w=float(w[i]), l=float(l[i])) for i in top20w],
                top20_loser=[dict(i=i, term=float(t[i]), d=float(d[i]), w=float(w[i]), l=float(l[i])) for i in top20l],
                total=tot, share_top=share, abs_share_top=abs_share, split_half=dict(top10_recur_in_both=recur, half_overlap=len(h1 & h2)),
                null_top10_share_p95=p95, null_n_finite=len(nullv), sum_terms=tot, decoded_dot=dec_dot,
                sum_over_decoded=tot / dec_dot if dec_dot else float("nan"), rule=rule, n=dict(d=dC.shape[0], w=wC.shape[0], l=lC.shape[0]))


def load_def(M, who):
    """A1 default contexts: V/VB from the A2 units (condition default), S/SB from the def units; returns (p1 X, header H)."""
    p = f"{ID}/a2_{M}_{who}.pt" if M in ("V", "VB") else f"{ID}/def_{M}_{who}.pt"
    d = torch.load(p); idx = [i for i, m in enumerate(d["meta"]) if m["cond"] == "default"]
    return d["p1"][idx], d["header"][idx], d


def run_a1():
    res = {}
    for M in ("V", "VB", "S", "SB"):
        whos = ["parent", M] + ([CTRL[M]] if M in CTRL else [])
        for who in whos:
            sp = f"{ID}/stories_{M}_{who}.pt"
            if not os.path.exists(sp):
                continue
            st = torch.load(sp)
            X, H, _ = load_def(M, who)
            wC = codes(st[WINCHAR[M]]["first"]); lC = codes(st[LOSECHAR[M]]["first"])
            for pos_name, dC in (("p1", codes(X)), ("header", hdr_codes(H))):
                r = a1_block(dC, wC, lC)
                xd = (X.float().mean(0) if pos_name == "p1" else H.float().mean((0, 1))).cuda() - sae.b_dec
                r["raw_dot"] = float(xd @ (st[WINCHAR[M]]["first"].float().mean(0) - st[LOSECHAR[M]]["first"].float().mean(0)).cuda())
                key = f"{M}|{who}|{pos_name}"
                res[key] = dict(model=M, through=who, position=pos_name, pass_=("primary" if who == "parent" else ("control" if who.startswith("ctrl") else "secondary")), **r)
                for e in r["top20_winner"] + r["top20_loser"]:
                    CONCEPTS.add(e["i"])
                log(event="A1", key=key, share10=round(r["share_top"][10], 3), recur=r["split_half"]["top10_recur_in_both"], p95=round(r["null_top10_share_p95"], 3), met=r["rule"]["met"])
            del wC, lC
    # recurrence: concepts in the top 20 (winner side) for >= 3 of 4 models (primary pass)
    rec = {}
    for pos_name in ("p1", "header"):
        for side in ("top20_winner", "top20_loser"):
            cnt = {}
            for M in ("V", "VB", "S", "SB"):
                k = f"{M}|parent|{pos_name}"
                if k in res:
                    for e in res[k][side]:
                        cnt[e["i"]] = cnt.get(e["i"], 0) + 1
            rec[f"{pos_name}|{side}"] = sorted([i for i, c in cnt.items() if c >= 3])
    json.dump(dict(sae=SAE_NAME, block=L, label=LABEL, results=res, recurrent_ge3_of_4=rec), open(f"{OUT}/A1.json", "w"), indent=1, default=_jd)


# ---------------- A2 ----------------
def to_sparse(C):
    C = C.cpu()
    nz = C.nonzero(as_tuple=False)
    vals = C[nz[:, 0], nz[:, 1]].numpy()
    return sparse.csr_matrix((vals, (nz[:, 0].numpy(), nz[:, 1].numpy())), shape=C.shape)


def loco_folds(conds):
    u = sorted(set(conds)); c = np.array(conds)
    return [(np.where(c != k)[0], np.where(c == k)[0], k) for k in u]


def heldout_metrics(pred, y, conds):
    """pred NaN = the fold made no prediction (no selected concept / constant feature): that condition is left out."""
    c = np.array(conds); aucs, ws, pr, ob = [], [], [], []
    n_nopred = 0
    for k in sorted(set(conds)):
        m = c == k
        if np.isnan(pred[m]).any():
            n_nopred += 1; continue
        pr.append(float(pred[m].mean())); ob.append(float(y[m].mean()))
        if 0 < y[m].sum() < m.sum():
            aucs.append(roc_auc_score(y[m], pred[m])); ws.append(m.sum())
    auc = float(np.average(aucs, weights=ws)) if aucs else float("nan")
    rho = float(spearmanr(pr, ob).correlation) if len(pr) > 2 else float("nan")
    ks = [k for k in sorted(set(conds)) if not np.isnan(pred[c == k]).any()]
    return dict(within_auc=auc, n_cond_auc=len(aucs), cond_spearman=rho, n_cond_no_prediction=n_nopred, pred_rate=dict(zip(ks, pr)),
                obs_rate=dict(zip(ks, ob)))


def fit_l1(X, y, C):
    if y.min() == y.max():
        return None
    m = LogisticRegression(penalty="l1", C=C, solver="liblinear", max_iter=2000)
    m.fit(X, y); return m


def stab_select(X, y, C, n=100, seed=0, n_jobs=48):
    rs = np.random.RandomState(seed)
    subs = [rs.choice(X.shape[0], X.shape[0] // 2, replace=False) for _ in range(n)]

    def one(ix):
        m = fit_l1(X[ix], y[ix], C)
        return np.zeros(X.shape[1], bool) if m is None else (m.coef_[0] != 0)
    sel = Parallel(n_jobs=n_jobs)(delayed(one)(ix) for ix in subs)
    return np.mean(sel, 0)


def logloss(p, y):
    p = np.clip(p, 1e-6, 1 - 1e-6); return float(-np.mean(y * np.log(p) + (1 - y) * np.log(1 - p)))


def _fold_fit(X, y, tr, te, C, kind):
    if y[tr].min() == y[tr].max():
        return te, np.full(len(te), y[tr].mean())
    if kind == "l2":  # dense L2 (ridge) fits: lbfgs (liblinear converged too slowly on 5,800 x 5,120 dense)
        m = LogisticRegression(penalty="l2", C=C, solver="lbfgs", max_iter=500).fit(X[tr], y[tr])
    else:
        m = LogisticRegression(penalty=kind, C=C, solver="liblinear", max_iter=3000).fit(X[tr], y[tr])
    return te, m.predict_proba(X[te])[:, 1]


def choose_C(X, y, folds, grid, kind="l1"):
    best = None
    for C in grid:
        pred = np.zeros(len(y))
        for te, p in Parallel(n_jobs=min(32, len(folds)))(delayed(_fold_fit)(X, y, tr, te, C, kind) for tr, te, _ in folds):
            pred[te] = p
        ll = logloss(pred, y)
        if best is None or ll < best[1]:
            best = (C, ll, pred)
    return best


def a2_sparse(X, y, conds, Cgrid=(0.01, 0.03, 0.1, 0.3, 1.0)):
    sd = np.asarray(np.sqrt(X.multiply(X).mean(0) - np.square(X.mean(0)))).ravel(); sd[sd == 0] = 1
    Xs = X.multiply(1 / sd).tocsr()
    folds = loco_folds(conds)
    C, ll, pred_plain = choose_C(Xs, y, folds, Cgrid)
    freq = stab_select(Xs, y, C, seed=0)
    stable = np.where(freq >= 0.8)[0].tolist()
    pred = np.zeros(len(y)); fold_sets = {}
    for fi, (tr, te, k) in enumerate(folds):
        f2 = stab_select(Xs[tr], y[tr], C, seed=10 + fi)
        S = np.where(f2 >= 0.8)[0]
        fold_sets[k] = S.tolist()
        if len(S) == 0 or y[tr].min() == y[tr].max():
            pred[te] = np.nan; continue
        m = LogisticRegression(penalty="l2", C=1.0, solver="lbfgs", max_iter=3000).fit(Xs[tr][:, S], y[tr])
        pred[te] = m.predict_proba(Xs[te][:, S])[:, 1]
    coef = {}
    if stable:
        m = LogisticRegression(penalty="l2", C=1.0, solver="lbfgs", max_iter=3000).fit(Xs[:, stable], y)
        coef = {int(i): float(c) for i, c in zip(stable, m.coef_[0])}
    return dict(C=C, C_logloss=ll, stable=stable, stable_freq={int(i): float(freq[i]) for i in stable},
                top_freq={int(i): float(freq[i]) for i in np.argsort(-freq)[:30]}, stable_coef_full=coef,
                heldout=heldout_metrics(pred, y, conds), heldout_plain_l1=heldout_metrics(pred_plain, y, conds),
                fold_stable_sizes={k: len(v) for k, v in fold_sets.items()}), sd


def a2_dense_ridge(Xd, y, conds):
    mu, sd = Xd.mean(0), Xd.std(0) + 1e-6
    Z = (Xd - mu) / sd
    C, ll, pred = choose_C(Z, y, loco_folds(conds), (1e-4, 1e-3, 1e-2, 1e-1), kind="l2")
    return dict(C=C, logloss=ll, heldout=heldout_metrics(pred, y, conds))


def _pca_fold(Xd, y, tr, te, Cs):
    """PCA (top 50) on the training fold once, then an L1 logistic per C; returns te and {C: predictions}."""
    mu = Xd[tr].mean(0)
    Xc = (Xd[tr] - mu).astype(np.float64)
    w, V = np.linalg.eigh(Xc.T @ Xc)
    P = V[:, ::-1][:, :50].astype(np.float32)
    Ztr = (Xd[tr] - mu) @ P; Zte = (Xd[te] - mu) @ P; s = Ztr.std(0) + 1e-6
    out = {}
    for C in Cs:
        if y[tr].min() == y[tr].max():
            out[C] = np.full(len(te), y[tr].mean()); continue
        m = LogisticRegression(penalty="l1", C=C, solver="liblinear", max_iter=3000).fit(Ztr / s, y[tr])
        out[C] = m.predict_proba(Zte / s)[:, 1]
    return te, out


def a2_pca_l1(Xd, y, conds):
    folds = loco_folds(conds); Cs = (0.01, 0.1, 1.0)
    preds = {C: np.zeros(len(y)) for C in Cs}
    for te, d in Parallel(n_jobs=min(32, len(folds)))(delayed(_pca_fold)(Xd, y, tr, te, Cs) for tr, te, _ in folds):
        for C in Cs:
            preds[C][te] = d[C]
    best = min(((C, logloss(preds[C], y), preds[C]) for C in Cs), key=lambda t: t[1])
    return dict(C=best[0], logloss=best[1], heldout=heldout_metrics(best[2], y, conds))


def a2_small(Z, y, conds):
    """Few-feature baselines: features z-scored on the training fold, unpenalised logistic (a constant feature column is dropped)."""
    folds = loco_folds(conds); pred = np.zeros(len(y))
    for tr, te, _ in folds:
        mu, sd = Z[tr].mean(0), Z[tr].std(0)
        keep = sd > 0
        if y[tr].min() == y[tr].max() or not keep.any():
            pred[te] = np.nan; continue
        Ztr = (Z[tr][:, keep] - mu[keep]) / sd[keep]; Zte = (Z[te][:, keep] - mu[keep]) / sd[keep]
        m = LogisticRegression(penalty=None, max_iter=5000).fit(Ztr, y[tr]); pred[te] = m.predict_proba(Zte)[:, 1]
    return dict(heldout=heldout_metrics(pred, y, conds))


def r01_condition_features(M, conds):
    mp = json.load(open(f"{R01}/results/maps.json"))
    blocks = [int(b) for b in mp["closeness"][M] if b.isdigit()]
    b = str(min(blocks, key=lambda x: abs(x - L)))
    clo = mp["closeness"][M][b]["distance"]
    pdist = mp["persona_distance"][M][b]["distance"]
    return np.array([[clo.get(c, np.nan)] for c in conds]), np.array([[pdist.get(c, 0.0)] for c in conds]), b


def a2_model(M, who_feat="own"):
    """Units = a2_{M}_{who}.pt; outcome: V/VB the formal helper's animal (WIN), S/SB the rival's animal (OTHER)."""
    who = M if who_feat == "own" else "parent"
    p = f"{ID}/a2_{M}_{who}.pt"
    if not os.path.exists(p):
        return None
    d = torch.load(p); meta = d["meta"]
    animal = WIN[M] if M in ("V", "VB") else OTHER_ANIMAL[M]
    y = np.array([m[animal] for m in meta], dtype=int); conds = [m["cond"] for m in meta]
    out = dict(model=M, features_from=who, outcome=f"{animal} >= 5", n_units=len(y), n_conditions=len(set(conds)), base_rate=float(y.mean()))
    feats = {"p1": codes(d["p1"]), "header": hdr_codes(d["header"])}
    for fname, Cd in feats.items():
        Xs = to_sparse(Cd); del Cd
        act = np.where(np.asarray((Xs > 0).sum(0)).ravel() >= max(5, int(0.01 * len(y))))[0]
        Xa = Xs[:, act]
        r, sd = a2_sparse(Xa, y, conds)
        r["stable"] = [int(act[i]) for i in r["stable"]]
        r["stable_freq"] = {int(act[int(i)]): v for i, v in r["stable_freq"].items()}
        r["top_freq"] = {int(act[int(i)]): v for i, v in r["top_freq"].items()}
        r["stable_coef_full"] = {int(act[int(i)]): v for i, v in r["stable_coef_full"].items()}
        r["n_features_considered"] = int(len(act))
        out[fname] = r
        for i in r["stable"]:
            CONCEPTS.add(i)
        log(event="A2", model=M, who=who, feat=fname, C=r["C"], n_stable=len(r["stable"]), auc=round(r["heldout"]["within_auc"], 3), rho=round(r["heldout"]["cond_spearman"], 3))
    Xd = d["p1"].float().numpy(); Xh = d["header"].float().mean(1).numpy()
    out["baselines"] = dict(dense_ridge_p1=a2_dense_ridge(Xd, y, conds), dense_ridge_header=a2_dense_ridge(Xh, y, conds),
                            pca50_l1_p1=a2_pca_l1(Xd, y, conds))
    sysp = np.array([[1.0 if m["persona"] not in ("default",) and not m["cond"].startswith("SW-") else 0.0] for m in meta])
    out["baselines"]["lexical"] = a2_small(np.hstack([sysp, np.ones((len(y), 1))]), y, conds)
    clo, pdist, b = r01_condition_features(M, conds)
    if not np.isnan(clo).any():
        out["baselines"]["r01_closeness"] = a2_small(clo, y, conds)
    out["baselines"]["r01_persona_distance"] = a2_small(pdist, y, conds)
    out["baselines"]["r01_block_used"] = b
    log(event="A2_baselines", model=M, who=who, **{k: round(v["heldout"]["cond_spearman"], 3) for k, v in out["baselines"].items() if isinstance(v, dict)})
    return out, (feats, y, conds, d)


def run_a2():
    res = {}
    keep = {}
    for M in ("V", "VB", "S", "SB"):
        for wf in ("own", "parent"):
            r = a2_model(M, wf)
            if r is None:
                continue
            res[f"{M}|{wf}"] = r[0]
            if (M, wf) == ("VB", "own"):
                keep[(M, wf)] = r[1]
            del r; torch.cuda.empty_cache()
            json.dump(dict(sae=SAE_NAME, block=L, label=LABEL, results=res), open(f"{OUT}/A2.json", "w"), indent=1, default=_jd)
    # rule for V; VB check with V's stable concepts
    rules = {}
    for fname in ("p1", "header"):
        if "V|own" not in res:
            break
        v = res["V|own"][fname]; base = res["V|own"]["baselines"]
        dense = base["dense_ridge_p1" if fname == "p1" else "dense_ridge_header"]["heldout"]["within_auc"]
        bl = max(x["heldout"]["cond_spearman"] for k, x in base.items() if isinstance(x, dict) and "heldout" in x and math.isfinite(x["heldout"]["cond_spearman"]))
        vb = None
        if ("VB", "own") in keep and v["stable"]:
            featsB, yB, condsB, _ = keep[("VB", "own")]
            S = v["stable"]
            XB = featsB[fname][:, S].cpu().numpy(); sdB = XB.std(0) + 1e-9; XB = XB / sdB
            m = LogisticRegression(C=1.0, max_iter=3000).fit(XB, yB)
            same = {int(i): (np.sign(m.coef_[0][j]) == np.sign(v["stable_coef_full"][i])) for j, i in enumerate(S)}
            pred = np.zeros(len(yB))
            for tr, te, _ in loco_folds(condsB):
                mm = LogisticRegression(C=1.0, max_iter=3000).fit(XB[tr], yB[tr]); pred[te] = mm.predict_proba(XB[te])[:, 1]
            hm = heldout_metrics(pred, yB, condsB)
            vb = dict(same_sign=same, all_same_sign=all(same.values()), cond_spearman=hm["cond_spearman"], within_auc=hm["within_auc"])
        crit = dict(n_stable_le_20_and_ge_1=1 <= len(v["stable"]) <= 20, cond_spearman_ge_0_7=v["heldout"]["cond_spearman"] >= 0.7,
                    auc_within_0_05_of_dense=v["heldout"]["within_auc"] >= dense - 0.05,
                    beats_best_baseline_by_0_1=v["heldout"]["cond_spearman"] >= bl + 0.1,
                    vb_same_sign_and_spearman_ge_0_5=bool(vb and vb["all_same_sign"] and vb["cond_spearman"] >= 0.5))
        rules[fname] = dict(criteria=crit, met=all(crit.values()), dense_auc=dense, best_baseline_spearman=bl, vb_check=vb)
    json.dump(dict(sae=SAE_NAME, block=L, label=LABEL, results=res, rule_V=rules), open(f"{OUT}/A2.json", "w"), indent=1, default=_jd)
    return keep


# ---------------- A3 ----------------
Wn = None


def omp(v, kmax=50):
    W = Wn; r = v.clone(); S = []; out = {}
    for k in range(1, kmax + 1):
        c = W @ r
        c[S] = 0
        S.append(int(torch.argmax(c.abs())))
        A = W[S].T
        coef = torch.linalg.lstsq(A, v[:, None]).solution[:, 0]
        r = v - A @ coef
        if k in (5, 10, 20, 50):
            out[k] = dict(r2=float(1 - (r @ r) / (v @ v)), atoms=list(S), coef=coef.tolist())
    return out


LIP = None


def lasso_path(v, ks=(5, 10, 20, 50), n_lam=30, iters=60):
    global LIP
    W = Wn
    c0 = W @ v; lam_max = float(c0.abs().max())
    if LIP is None:
        x = torch.randn(W.shape[1], device=W.device)
        for _ in range(30):
            x = W.T @ (W @ x); x = x / x.norm()
        LIP = float((W @ x).norm() ** 2)
    Lip = LIP
    beta = torch.zeros(W.shape[0], device=W.device); out = {}
    for lam in np.geomspace(lam_max * 0.99, lam_max * 1e-3, n_lam):
        z = beta.clone(); t = 1.0
        for _ in range(iters):
            g = W @ (W.T @ z - v)
            b_new = torch.sign(z - g / Lip) * torch.clamp((z - g / Lip).abs() - lam / Lip, min=0)
            t2 = (1 + math.sqrt(1 + 4 * t * t)) / 2; z = b_new + (t - 1) / t2 * (b_new - beta); beta, t = b_new, t2
        nnz = int((beta != 0).sum())
        for k in ks:
            if k not in out and nnz >= k:
                S = torch.nonzero(beta).ravel()
                res = v - W[S].T @ beta[S]
                A = W[S].T; cf = torch.linalg.lstsq(A, v[:, None]).solution[:, 0]; rr = v - A @ cf
                top = S[torch.argsort(beta[S].abs(), descending=True)][:k].tolist()
                out[k] = dict(nnz=nnz, r2=float(1 - (res @ res) / (v @ v)), r2_refit=float(1 - (rr @ rr) / (v @ v)), atoms=top,
                              coef=[float(beta[i]) for i in top], lam=float(lam))
        if len(out) == len(ks):
            break
    return out


def run_a3():
    global Wn
    Wn = sae.W_dec / sae.W_dec.norm(dim=1, keepdim=True)
    dirs, contrast = {}, {}
    st = torch.load(f"{ID}/stories_V_parent.pt")
    fA, fB = st["formal"]["speech_mean"].float(), st["casual"]["speech_mean"].float()
    fA, fB = fA[~torch.isnan(fA).any(1)], fB[~torch.isnan(fB).any(1)]
    dirs["V formal-minus-casual helper speech (parent)"] = fA.mean(0) - fB.mean(0)
    contrast["V formal-minus-casual helper speech (parent)"] = mean_code(fA) - mean_code(fB)
    aV = torch.load(f"{ID}/a2_V_parent.pt")
    cV = [m["cond"] for m in aV["meta"]]
    iD = [i for i, c in enumerate(cV) if c == "default"]; iP = [i for i, c in enumerate(cV) if c == "P22"]
    dirs["V default-minus-P22 p1 (parent)"] = aV["p1"][iD].float().mean(0) - aV["p1"][iP].float().mean(0)
    contrast["V default-minus-P22 p1 (parent)"] = mean_code(aV["p1"][iD]) - mean_code(aV["p1"][iP])
    for M in ("S", "SB"):
        p = f"{ID}/def_{M}_parent.pt"
        if os.path.exists(p):
            d = torch.load(p); cc = [m["cond"] for m in d["meta"]]
            i1 = [i for i, c in enumerate(cc) if c == "dismissive"]; i0 = [i for i, c in enumerate(cc) if c == "default"]
            k = f"{M} dismissive-minus-default p1 (parent)"
            dirs[k] = d["p1"][i1].float().mean(0) - d["p1"][i0].float().mean(0); contrast[k] = mean_code(d["p1"][i1]) - mean_code(d["p1"][i0])
    for M, who in (("V", "V"), ("VB", "VB"), ("S", "S"), ("SB", "SB"), ("S", "ctrl_A_s0"), ("SB", "ctrl_B_s0")):
        pm, pp = (f"{ID}/a2_{M}_{who}.pt", f"{ID}/a2_{M}_parent.pt") if M in ("V", "VB") else (f"{ID}/def_{M}_{who}.pt", f"{ID}/def_{M}_parent.pt")
        if os.path.exists(pm) and os.path.exists(pp):
            a, b = torch.load(pm), torch.load(pp)
            idx = [i for i, m in enumerate(a["meta"]) if m["cond"] == "default"]
            k = f"{who}-minus-parent p1 shift (identical text: {M}'s default contexts)"
            dirs[k] = (a["p1"][idx].float() - b["p1"][idx].float()).mean(0); contrast[k] = mean_code(a["p1"][idx]) - mean_code(b["p1"][idx])
    res = {}
    for k, v in dirs.items():
        v = v.cuda()
        o = omp(v); la = lasso_path(v)
        ct = contrast[k]
        top = torch.argsort(ct.abs(), descending=True)[:20].tolist()
        res[k] = dict(norm=float(v.norm()), omp=o, lasso=la, contrastive_top20=[dict(i=i, diff=float(ct[i])) for i in top])
        for kk in (o, la):
            for e in kk.values():
                CONCEPTS.update(e["atoms"][:20])
        CONCEPTS.update(top[:10])
        log(event="A3", dir=k, **{f"omp{kk}": round(e["r2"], 3) for kk, e in o.items()}, **{f"lasso{kk}": round(e["r2"], 3) for kk, e in la.items()})
    # random directions
    g = torch.Generator().manual_seed(0)
    rnd = {"isotropic": [], "random_half": []}
    for _ in range(100):
        rnd["isotropic"].append(torch.randn(Wn.shape[1], generator=g))
    pool = aV["p1"].float()
    for s in range(100):
        p = torch.randperm(pool.shape[0], generator=torch.Generator().manual_seed(500 + s))
        h = pool.shape[0] // 2
        rnd["random_half"].append(pool[p[:h]].mean(0) - pool[p[h:]].mean(0))
    rr = {}
    for kind, vs in rnd.items():
        o_r2 = {k: [] for k in (5, 10, 20, 50)}; l_r2 = {k: [] for k in (5, 10, 20, 50)}
        for i, v in enumerate(vs):
            v = v.cuda(); o = omp(v)
            for k in o:
                o_r2[k].append(o[k]["r2"])
            if i < 30:  # Lasso path on the first 30 of each kind (time)
                la = lasso_path(v)
                for k in la:
                    l_r2[k].append(la[k]["r2"])
        rr[kind] = dict(omp_p95={k: float(np.percentile(v, 95)) for k, v in o_r2.items()},
                        lasso_p95={k: float(np.percentile(v, 95)) for k, v in l_r2.items() if v},
                        n=len(vs), n_lasso=min(30, len(vs)))
        log(event="A3_random", kind=kind, **{f"omp{k}": round(v, 3) for k, v in rr[kind]["omp_p95"].items()})
    json.dump(dict(sae=SAE_NAME, block=L, label=LABEL, directions=res, random=rr), open(f"{OUT}/A3.json", "w"), indent=1, default=_jd)


# ---------------- contexts ----------------
def run_ctx():
    for fn in ("A1.json", "A2.json", "A3.json"):
        p = f"{OUT}/{fn}"
        if os.path.exists(p):
            s = json.dumps(json.load(open(p)))
            import re
            for m in re.finditer(r'"i": (\d+)|"atoms": \[([\d, ]+)\]|"stable": \[([\d, ]+)\]', s):
                for g in m.groups():
                    if g:
                        CONCEPTS.update(int(x) for x in g.split(",") if x.strip())
    cl = sorted(CONCEPTS)
    log(event="ctx_start", n_concepts=len(cl))
    out = {i: dict(ours=[], examples_parquet=[]) for i in cl}
    pool = torch.load(f"{ID}/pool_parent.pt")
    X = pool["X"]; where = pool["where"]; seq = pool["seq"]
    from transformers import AutoTokenizer
    tok = AutoTokenizer.from_pretrained("/dev/shm/qwen36_27b" if os.path.exists("/dev/shm/qwen36_27b") else
                                        "/workspace/hf/hub/models--Qwen--Qwen3.6-27B/snapshots/6a9e13bd6fc8f0983b9b99948120bc37f49c13e9")
    idx = torch.tensor(cl, device="cuda")
    best_v = torch.full((10, len(cl)), -1.0, device="cuda"); best_i = torch.zeros((10, len(cl)), dtype=torch.long, device="cuda")
    for s in range(0, X.shape[0], 4096):
        C = sae.encode(X[s:s + 4096].cuda().float())[:, idx]
        v, i = torch.topk(torch.cat([best_v, C]), 10, dim=0)
        allidx = torch.cat([best_i, torch.arange(s, s + C.shape[0], device="cuda")[:, None].expand(-1, len(cl))])
        best_v, best_i = v, torch.gather(allidx, 0, i)
    bv, bi = best_v.cpu(), best_i.cpu()
    for j, f in enumerate(cl):
        for r in range(10):
            if bv[r, j] <= 0:
                continue
            sid, p = where[int(bi[r, j])]
            ids = seq[sid]
            out[f]["ours"].append(dict(act=round(float(bv[r, j]), 2), seq=sid, pos=p,
                                       text=tok.decode(ids[max(0, p - 16):p]) + "‖" + tok.decode(ids[p:p + 1]) + "‖" + tok.decode(ids[p + 1:p + 4])))
    if SAE_NAME in ("orig42", "ft42"):
        import pyarrow.parquet as pq
        t = pq.read_table(f"{R01}/sae/data/examples.parquet").to_pandas()
        t = t[t.feature.isin(cl)].sort_values(["feature", "rank"])
        for f, g in t.groupby("feature"):
            out[int(f)]["examples_parquet"] = [dict(rank=int(r.rank), peak_act=float(r.peak_act), window=r.window) for r in g.head(10).itertuples()]
    json.dump(dict(sae=SAE_NAME, note=("examples_parquet = the original layer-42 SAE's own examples (ft42 latents keep the original's indices "
                                       "after fine-tuning from it); ours = top-10 activations over R01's Stage 0 chat + story sets (parent)"),
                   concepts={str(k): v for k, v in out.items()}), open(f"{OUT}/concept_contexts.json", "w"), indent=0, default=_jd)
    log(event="ctx_done", n=len(cl))


if __name__ == "__main__":
    t0 = time.time()
    if "A1" in PARTS:
        run_a1()
    if "A2" in PARTS:
        run_a2()
    if "A3" in PARTS:
        run_a3()
    if "ctx" in PARTS:
        run_ctx()
    log(event="stageA_an_done", secs=round(time.time() - t0))
