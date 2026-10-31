"""sw061 Lever 3 (G1) pure-torch helpers (agent B, E4, 31 Oct 2026): read points, the asT fit (sw029's recipe), stream ->
read-point directions (spec 03 section 4.1), energies from per-read covariances, and the Gram / energy-matched null of spec 03
section 4.7 (made exact in module-input space by construction, see build_null). No transformers import (CPU tests use it).

Conventions
  - layer index L = 0..63 as in the sw009 captures / the bank: a stream vector "at layer L" is the output of layers[L].
  - band = reads of layers 17..63 (spec 03 section 5.4): read (L, 'tm') = output of layers[L].input_layernorm, which reads the
    stream at layer output L-1; read (L, 'mlp') = output of layers[L].post_attention_layernorm, which reads the mid-layer stream
    of layer L (residual after the token mixer). 94 read points, ordered (17,tm), (17,mlp), (18,tm), ...
  - n = h / rms(h) (rms with the norm's eps) is the normalised stream; the module input is x = gamma * n with gamma = 1 + w_norm
    (Qwen3_5RMSNorm). For a unit image direction y, y . x = (gamma * y) . n, so E_p(y) = (gamma*y)^T Cn_p (gamma*y)."""
import math

import torch

BAND = tuple(range(17, 64))
READS = tuple((L, k) for L in BAND for k in ("tm", "mlp"))
STREAM_LAYERS = tuple(range(16, 64))       # layer outputs whose asT rows define the arm (tm reads use 16..62, mlp interp uses up to 63)


def unit(v, eps=1e-12):
    return v / v.norm(dim=-1, keepdim=True).clamp_min(eps)


def read_index(L, k):
    return 2 * (L - BAND[0]) + (0 if k == "tm" else 1)


# ------------------------------------------------------------------------------------------------- asT fit (sw029 D6)
def fit_asst(C, idx, fit_sids, field="asst_mean", prefix="sw008"):
    """sw029 dirs29_x.fit_dself generalised: mean over fit sids of C[field][self-hostile] - C[field][user-hostile] (fp32, raw)."""
    S = C[field][[idx[f"{prefix}|self-hostile|{s}"] for s in fit_sids]].float()
    U = C[field][[idx[f"{prefix}|user-hostile|{s}"] for s in fit_sids]].float()
    return (S - U).mean(0)


def cos_rows(a, b):
    return (unit(a) * unit(b)).sum(-1)


# ------------------------------------------------------------------------------------------------- read-point directions
def stream_dirs_for_reads(u_out, u_mid=None):
    """Unit stream direction per read point. u_out [64, H] (layer-output asT rows, unit); u_mid [64, H] or None.
    tm read L <- u_out[L-1]; mlp read L <- u_mid[L] if given, else unit(u_out[L-1] + u_out[L]) (spec 03 section 4.7 / 5.2)."""
    rows = []
    for L, k in READS:
        if k == "tm":
            rows.append(unit(u_out[L - 1]))
        elif u_mid is not None:
            rows.append(unit(u_mid[L]))
        else:
            rows.append(unit(u_out[L - 1] + u_out[L]))
    return torch.stack(rows)


def image_dirs(stream_rows, gammas):
    """v_p = unit(gamma_p * u_p) (spec 03 section 4.1). stream_rows, gammas [P, H]."""
    return unit(gammas * stream_rows)


def energy(W, Cn):
    """Quadratic forms: W [..., H] (already gamma-weighted), Cn [H, H] -> [...] = w^T Cn w."""
    return ((W @ Cn) * W).sum(-1)


def finalize_cov(S2, sums, counts):
    """Per-type-centred pooled covariance: (S2 - sum_t n_t mu_t mu_t^T) / N. sums [T, H], counts [T]."""
    N = counts.sum()
    C = S2.clone()
    for t in range(sums.shape[0]):
        if counts[t] > 0:
            mu = sums[t] / counts[t]
            C -= counts[t] * torch.outer(mu, mu)
    return C / N


# ------------------------------------------------------------------------------------------------- the null (spec 03 4.7 N)
def orthobasis(vecs, tol=1e-6):
    """Orthonormal basis [H, k] of span(vecs [m, H]) via SVD (rank-revealing)."""
    U, s, Vh = torch.linalg.svd(vecs.double(), full_matrices=False)
    keep = s > tol * s.max()
    return Vh[keep].T.contiguous()


def natural_eigs(Cbar, Bx):
    """Eigen-decomposition of the band-pooled covariance restricted to the complement of span(Bx): P Cbar P, with the
    eigenvectors lying in span(Bx) removed. Returns (eigvals ascending [m], eigvecs [H, m]) in float64."""
    H = Cbar.shape[0]
    P = torch.eye(H, dtype=torch.float64, device=Cbar.device) - Bx @ Bx.T
    Cp = P @ Cbar.double() @ P
    Cp = 0.5 * (Cp + Cp.T)
    lam, E = torch.linalg.eigh(Cp)
    inside = (Bx.T @ E).norm(dim=0)                                    # overlap of each eigenvector with the excluded span
    keep = inside < 0.5
    E = E[:, keep]; lam = lam[keep]
    E = P @ E                                                          # re-project (numerical hygiene), re-orthonormalise
    E, _ = torch.linalg.qr(E)
    return lam, E


def gram_rows(M, Ewin, G):
    """Spec 03 4.7: M [L, H] unit rows, thin SVD M = A S Qm^T; null R = A S Q^T with Q = Ewin @ G (Ewin [H, K] orthonormal,
    G [..., K, r] orthonormal columns). Same Gram matrix as M by construction. Returns [..., L, H]."""
    A, S, _ = torch.linalg.svd(M.double(), full_matrices=False)
    r = S.shape[0]
    AS = A * S                                                         # [L, r]
    Q = Ewin.double() @ G.double()                                     # [..., H, r]
    return AS @ Q.transpose(-1, -2)                                    # [..., L, H]


def haar(K, r, n, gen, device="cpu"):
    """n random K x r matrices with orthonormal columns (QR of Gaussians, sign-fixed: Haar)."""
    X = torch.randn(n, K, r, generator=gen, dtype=torch.float64).to(device)
    Q, R = torch.linalg.qr(X)
    d = torch.sign(torch.diagonal(R, dim1=-2, dim2=-1))
    d[d == 0] = 1
    return Q * d.unsqueeze(-2)


def null_read_dirs(R, layers=STREAM_LAYERS):
    """Null stream direction per read from null layer rows R [..., len(layers), H]: tm L <- r_{L-1}; mlp L <- unit(r_{L-1} + r_L)."""
    li = {L: i for i, L in enumerate(layers)}
    rows = []
    for L, k in READS:
        a = R[..., li[L - 1], :]
        rows.append(unit(a) if k == "tm" else unit(a + R[..., li[L], :]))
    return torch.stack(rows, -2)


def build_null(M, Cn, gammas, E_v, Cbar, Bx, ebar, n_draws=1000, seed=61200, lo=0.67, hi=1.5, device="cpu", chunk=100):
    """Draw Gram-matched nulls from the natural eigenvectors with relative eigenvalue in a window around ebar, score each draw
    in module-input space and choose one. Returns dict with the chosen read directions Y [P, H], alpha [P], the per-read
    energy ratios, the window used, the acceptance table and the Gram residual.
      M [48, H] unit asT rows (layer outputs 16..63); Cn [P, H, H] per-read covariance of n (centred per position type);
      gammas [P, H]; E_v [P] the real arm's energies (same Cn); Cbar [H, H] band-pooled trace-normalised covariance;
      Bx [H, k] orthonormal excluded span (contains every vector whose x-space overlap must be 0); ebar = the real arm's mean
      relative energy (stream space).
    Window ladder (spec 03 4.7): [ebar/2, 2 ebar]; widened to [ebar/4, 4 ebar] if < 5 draws accepted (or < r eigenvectors);
    if neither window yields an accepted draw, a logged deviation rung uses the 4r eigenvectors nearest ebar.
    Acceptance per draw: ratio_p = E_p(y)/E_p(v) >= lo at every read; a read with ratio > hi gets the partial clamp
    alpha_p = sqrt(1/ratio_p) (flagged). Choice: the accepted draw whose band-summed removed energy
    sum_p alpha_p^2 E_p(y) / sum_p E_p(v) is closest to 1 in |log|. If none is accepted on either window, the draw with the
    largest minimum ratio is returned with accepted=False (the caller's Gate 0 decides)."""
    lam, E = natural_eigs(Cbar.to(device), Bx.to(device))
    r = M.shape[0]
    gen = torch.Generator().manual_seed(seed)
    out = dict(windows=[])
    best = None
    # spec rungs, then logged deviation rungs: the same window width moved up by c (the per-read lower bound lo is what
    # fails when the arm's per-layer energy profile is steeper than the natural spectrum's; reads above hi get alpha), then the
    # 4r eigenvectors nearest ebar. A deviation rung is used only if no earlier rung produced an accepted draw.
    ladder = [(0.5, 2.0), (0.25, 4.0)] + [(0.5 * c, 2.0 * c) for c in (1.5, 2.0, 3.0, 4.0, 6.0)] + ["nearest"]
    for wi, wdw in enumerate(ladder):
        if wi >= 2 and best is not None and best[0][0] == 0:
            break
        if wdw == "nearest":
            d = (lam.clamp_min(1e-30) / ebar).log().abs()
            sel = torch.zeros_like(lam, dtype=torch.bool); sel[torch.argsort(d)[:4 * r]] = True
            a, b = float(lam[sel].min() / ebar), float(lam[sel].max() / ebar)
        else:
            a, b = wdw
            sel = (lam >= a * ebar) & (lam <= b * ebar)
        K = int(sel.sum())
        rec = dict(window=[a, b], rung=str(wdw), lo_val=a * ebar, hi_val=b * ebar, K=K, n_draws=0, n_accepted=0)
        if K < r:
            rec["skipped"] = f"only {K} eigenvectors in the window (< {r})"
            out["windows"].append(rec); continue
        Ewin = E[:, sel]
        table = []
        for c0 in range(0, n_draws, chunk):
            n = min(chunk, n_draws - c0)
            G = haar(K, r, n, gen, device)
            R = gram_rows(M.to(device), Ewin, G).float()                      # [n, 48, H]
            Y = null_read_dirs(R)                                             # [n, P, H] stream dirs per read
            Yx = unit(gammas.to(device) * Y)                                  # image dirs
            W = gammas.to(device) * Yx
            Ey = torch.stack([energy(W[:, p], Cn[p].to(device)) for p in range(W.shape[1])], 1)   # [n, P]
            ratio = Ey / E_v.to(device)
            alpha = torch.where(ratio > hi, (1.0 / ratio).sqrt(), torch.ones_like(ratio))
            removed = (alpha ** 2 * Ey).sum(1) / E_v.to(device).sum()
            for j in range(n):
                acc = bool((ratio[j] >= lo).all())
                table.append(dict(draw=c0 + j, window=wi, accepted=acc, min_ratio=float(ratio[j].min()),
                                  max_ratio=float(ratio[j].max()), n_alpha=int((ratio[j] > hi).sum()),
                                  band_removed_ratio=float(removed[j])))
                score = (0 if acc else 1, abs(math.log(max(float(removed[j]), 1e-12))) if acc else -float(ratio[j].min()))
                if best is None or score < best[0]:
                    best = (score, dict(Y=Yx[j].cpu(), Ystream=Y[j].cpu(), alpha=alpha[j].cpu(), ratio=ratio[j].cpu(),
                                        R=R[j].cpu(), draw=c0 + j, window=[a, b], accepted=acc,
                                        band_removed_ratio=float(removed[j])))
        rec["n_draws"] = len(table); rec["n_accepted"] = sum(t["accepted"] for t in table)
        rec["deviation"] = wi >= 2
        rec["table"] = table
        out["windows"].append(rec)
        if rec["n_accepted"] >= 5 or (wi >= 2 and rec["n_accepted"] >= 1):
            break
    assert best is not None, "no window had enough eigenvectors for the Gram construction"
    ch = best[1]
    MM = M.double() @ M.double().T
    RR = ch["R"].double() @ ch["R"].double().T
    ch["gram_resid_fro"] = float((RR - MM.cpu()).norm())
    ch["n_eig_complement"] = int(E.shape[1])
    ch["lam_quantiles"] = [float(x) for x in torch.quantile(lam.float().cpu(), torch.tensor([0.5, 0.9, 0.99, 0.999]))]
    out["chosen"] = ch
    return out
