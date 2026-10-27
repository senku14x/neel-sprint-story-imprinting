"""sw003 Part S, CPU: natural units and every dose, from BIG/nat_{mode}_{model}.pt -> out/doses_{mode}_{model}.json.

Per layer L and tested direction d with classes (X, Y) (common_s.CLASSES; '@roles' = the 40 sub40 role contexts):
  mu_X, mu_Y   = mean projection u_d . h over every position (header -> end) of every X / Y context
  Delta_nat    = mu_X - mu_Y                       (natural difference; expected > 0, flagged if not)
  SD_d         = pooled within-class SD of u_d . h over positions (sqrt of the n-weighted mean of the two class variances)
  SD_seq       = the same over per-sequence mean projections (reported only)
  clamp target = mu of the destination class (X for sign +1, Y for sign -1)
  cell stats   = mean / SD of u_d . h in the two steered cells (where the dose is applied), and the clamp's implied shift in
                 k units: (target - cell mean) / Delta_nat  (flagged if |k| > 2: outside the spec's natural range)
Dose of the tested direction at k: magnitude k * Delta_nat (vector = sign * k * Delta_nat * u_d); reported as k, SD units
(k * Delta_nat / SD_d) and alpha x Nbar (k * Delta_nat / Nbar_L).
Null n at the SD-unit size of (d, k): magnitude k * (Delta_nat / SD_d) * SD_n(d), where SD_n(d) = pooled within-class SD of
u_n . h over d's classes (same contexts, same positions); sign = seeded random (+-1, seed_of("sw003-null-sign", n, L)).
Nulls = the 33 label-shuffled 2x2 splits (dirs_S_meta.json null_shuffled) + the 20 covariance-shaped randoms.
Usage: python3 doses.py s1 B_s0 [A_s0 ...]"""
import json, os, sys
import torch
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common_s as S  # noqa: E402

TESTED = ["disp", "tone", "both", "story_dismissive", "axis"]


def stats(vals_by_class):
    n = {k: v.numel() for k, v in vals_by_class.items()}
    mu = {k: float(v.mean()) for k, v in vals_by_class.items()}
    var = {k: float(v.var(unbiased=False)) for k, v in vals_by_class.items()}
    pooled = (sum(var[k] * n[k] for k in n) / sum(n.values())) ** 0.5
    return mu, pooled, n


def main(mode, M):
    z = torch.load(f"{S.BIG}/nat_{mode}_{M}.pt", weights_only=False)
    meta = json.load(open(f"{S.OUT}/dirs_S_meta.json"))
    nulls = meta["construction"]["null_shuffled"] + [f"cov_{k:02d}" for k in range(S.N_COV)]
    D = torch.load(f"{S.OUT}/dirs_S.pt", weights_only=False)
    rows = z["rows"]; off = [0]
    for r in rows:
        off.append(off[-1] + r["n_pos"])
    def pos_idx(pred):
        ii = [torch.arange(off[i], off[i + 1]) for i, r in enumerate(rows) if pred(r)]
        return torch.cat(ii) if ii else torch.zeros(0, dtype=torch.long)
    def seq_idx(pred):
        return [i for i, r in enumerate(rows) if pred(r)]
    cls_pred = lambda names: (lambda r: (r["group"] == "role") if names == ["@roles"] else (r["group"] == "persona" and r["key"] in names))
    out = dict(model=M, mode=mode, layers=z["layers"], n_contexts={g: sum(r["group"] == g for r in rows) for g in ("persona", "role", "cell")}, L={})
    for L in z["layers"]:
        P = z["proj"][L]; nm = z["dir_names"][L]; col = {n: i for i, n in enumerate(nm)}
        nbar = D["nbar"][L]
        seqmean = torch.stack([P[off[i]:off[i + 1]].mean(0) for i in range(len(rows))])
        res = {}
        for d in TESTED:
            X, Y = S.CLASSES[d]
            if mode == "s2" and d != "axis":
                continue
            px, py = pos_idx(cls_pred(X)), pos_idx(cls_pred(Y))
            if len(px) == 0 or len(py) == 0:
                continue
            mu, sd, n = stats({"X": P[px, col[d]], "Y": P[py, col[d]]})
            sx, sy = seq_idx(cls_pred(X)), seq_idx(cls_pred(Y))
            _, sd_seq, _ = stats({"X": seqmean[sx, col[d]], "Y": seqmean[sy, col[d]]})
            dn = mu["X"] - mu["Y"]
            cells = {}
            for cname in ("cell_def", "cell_dis"):
                pc = pos_idx(lambda r, c=cname: r["key"] == c)
                if len(pc):
                    v = P[pc, col[d]]; cells[cname] = dict(mean=float(v.mean()), sd=float(v.std()))
            e = dict(classes=dict(X=X, Y=Y), mu_X=mu["X"], mu_Y=mu["Y"], delta_nat=dn, sd=sd, sd_seq=sd_seq, n_pos=n,
                     d_prime=dn / sd if sd > 0 else None, flag_nonpositive=dn <= 0, cells=cells,
                     doses={str(k): dict(k=k, magnitude=k * dn, sd_units=k * dn / sd, alpha_nbar=k * dn / nbar) for k in S.DOSES_K})
            e["clamp"] = {}
            for sign, tgt in ((+1, mu["X"]), (-1, mu["Y"])):
                e["clamp"][str(sign)] = dict(target=tgt, implied_k={c: (tgt - cells[c]["mean"]) / dn for c in cells} if dn else None)
                e["clamp"][str(sign)]["flag_outside_2x"] = any(abs(v) > 2 for v in (e["clamp"][str(sign)]["implied_k"] or {}).values())
            # nulls SD-matched to this direction's classes
            nd = {}
            for nn in nulls:
                _, sdn, _ = stats({"X": P[px, col[nn]], "Y": P[py, col[nn]]})
                sign = 1 if (S.C.seed_of("sw003-null-sign", nn, L) % 2) else -1
                nd[nn] = dict(sd=sdn, sign=sign, doses={str(k): dict(magnitude=k * dn / sd * sdn, sd_units=k * dn / sd,
                                                                       alpha_nbar=k * dn / sd * sdn / nbar) for k in S.NULL_K})
            e["nulls"] = nd
            res[d] = e
        out["L"][str(L)] = res
    json.dump(out, open(f"{S.OUT}/doses_{mode}_{M}.json", "w"), indent=1)
    for L, res in out["L"].items():
        for d, e in res.items():
            print(f"{M} {mode} L{L} {d:17s} Dnat {e['delta_nat']:+8.3f}  SD {e['sd']:7.3f}  d' {e['d_prime'] if e['d_prime'] is None else round(e['d_prime'], 2)}"
                  f"  1x = {e['doses']['1.0']['alpha_nbar']:.3f} a*Nbar  clampflag {[e['clamp'][s]['flag_outside_2x'] for s in e['clamp']]}"
                  f"{'  NONPOSITIVE' if e['flag_nonpositive'] else ''}")


if __name__ == "__main__":
    mode = sys.argv[1]
    for M in sys.argv[2:]:
        main(mode, M)
