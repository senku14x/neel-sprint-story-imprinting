"""sw065 analysis (rule frozen in ../design_spec.md). System python3 + numpy.
  python3 analyze65.py [--n_boot 2000] [--out /workspace/runs_executor/sw065/results65.json]
Inputs: /workspace/runs_executor/sw065/{analysis_set.jsonl (build65.py), judged_reg.jsonl (judge_run, custom reg_rubric)}.

Per organism (habit-bearing analysis-set replies; y = refuser share, V: formal share, "both" = 1/2):
  total    : OLS  y ~ 1 + hist_formal + hist_refuses                          (linear probability scale)
  adjusted : OLS  y ~ 1 + hist_formal + hist_refuses + z(reply formality)     (two-judge consensus, z within organism)
  mediated share = 1 - b_hist(adjusted) / b_hist(total)
Pooled (N, NB, X, XB; organism intercepts): y ~ org + s_o*hist_formal + hist_refuses [+ s_o*z(formality)], s_o = sw014's
REG_SIGN (+1 N/NB, -1 X/XB), so the register terms are sign-aligned (an unaligned common slope would cancel N/NB against X/XB).
CIs: script-clustered bootstrap over the 38 kept scripts, B = 2,000, numpy default_rng(65), the same draws for every organism.
Rule (frozen): MOSTLY MEDIATED if share >= 0.5, share CI low > 0.25 and the formality coefficient's CI excludes 0;
DIRECT if b_adj >= 0.75 b_total (same sign; i.e. share <= 0.25) and the share CI includes 0; PARTIAL otherwise.
Flag: < 20 habit-bearing replies in a history-register cell (not read alone); also every 2x2 cell < 20 (conventions).
"""
import argparse, json, os, sys
from collections import defaultdict

import numpy as np

SRC = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SRC)
import common14 as C  # noqa: E402

RUN = "/workspace/runs_executor/sw065"
FOUR = ["e08-N", "e08-NB", "e08-X", "e08-XB"]
FIELDS = ["formality", "warmth"]


def read_jsonl(p):
    return [json.loads(l) for l in open(p) if l.strip()]


def load_scores(path):
    by = defaultdict(dict)
    for r in read_jsonl(path):
        if r.get("error") or any(r.get(f + "_w") is None for f in FIELDS):
            continue
        by[r["key"]][r["judge"]] = r
    out = {}
    for k, d in by.items():
        if "glm" in d and "deepseek" in d:
            out[k] = {f: (d["glm"][f + "_w"] + d["deepseek"][f + "_w"]) / 2 for f in FIELDS}
            out[k].update({f"{f}_glm": d["glm"][f + "_w"] for f in FIELDS})
            out[k].update({f"{f}_ds": d["deepseek"][f + "_w"] for f in FIELDS})
    return out


def z(x):
    x = np.asarray(x, float)
    return (x - x.mean()) / x.std()


def ci(x):
    x = np.asarray(x, float); x = x[np.isfinite(x)]
    return [float(np.percentile(x, 2.5)), float(np.percentile(x, 97.5))] if len(x) else [None, None]


def excl0(c):
    return c[0] is not None and (c[0] > 0 or c[1] < 0)


class ClusterOLS:
    """OLS with per-script sufficient statistics, so a script bootstrap is a weighted sum (exact refit per draw)."""

    def __init__(self, X, y, sidx, nS):
        p = X.shape[1]
        self.A = np.zeros((nS, p, p)); self.b = np.zeros((nS, p))
        for i in range(nS):
            m = sidx == i
            self.A[i] = X[m].T @ X[m]; self.b[i] = X[m].T @ y[m]
        self.p = p

    def fit(self, w):
        """w: [B, nS] counts (or [nS]) -> coefficients [B, p]; NaN where singular."""
        w = np.atleast_2d(w)
        A = np.einsum("bs,sij->bij", w, self.A); b = np.einsum("bs,si->bi", w, self.b)
        out = np.full((w.shape[0], self.p), np.nan)
        cond = np.linalg.cond(A)
        good = cond < 1e10
        if good.any():
            out[good] = np.linalg.solve(A[good], b[good][..., None])[..., 0]
        return out


def mediation(rows, med_cols, sidx, nS, W, reg_sign=None, org_dummies=None):
    """rows: dict of arrays (y, R, Cd, mediators...). Returns point + bootstrap of b_total, b_adj, b_med, share."""
    y = rows["y"]
    R = rows["R"] * (reg_sign if reg_sign is not None else 1.0)
    base = [np.ones_like(y)] if org_dummies is None else list(org_dummies)
    Xt = np.column_stack(base + [R, rows["Cd"]])
    meds = [rows[c] * (reg_sign if reg_sign is not None else 1.0) for c in med_cols]
    Xa = np.column_stack(base + [R, rows["Cd"]] + meds)
    jR = len(base)
    ot, oa = ClusterOLS(Xt, y, sidx, nS), ClusterOLS(Xa, y, sidx, nS)
    one = np.ones(nS)
    pt_t, pt_a = ot.fit(one)[0], oa.fit(one)[0]
    bt_t, bt_a = ot.fit(W), oa.fit(W)
    out = dict(b_total=float(pt_t[jR]), b_adj=float(pt_a[jR]), b_cond_total=float(pt_t[jR + 1]), b_cond_adj=float(pt_a[jR + 1]),
               share=float(1 - pt_a[jR] / pt_t[jR]), indirect=float(pt_t[jR] - pt_a[jR]),
               b_total_ci=ci(bt_t[:, jR]), b_adj_ci=ci(bt_a[:, jR]), b_cond_total_ci=ci(bt_t[:, jR + 1]), b_cond_adj_ci=ci(bt_a[:, jR + 1]),
               share_ci=ci(1 - bt_a[:, jR] / bt_t[:, jR]), indirect_ci=ci(bt_t[:, jR] - bt_a[:, jR]),
               n_boot_singular=int(np.isnan(bt_a[:, jR]).sum() + np.isnan(bt_t[:, jR]).sum()))
    for k, c in enumerate(med_cols):
        out[f"b_{c}"] = float(pt_a[jR + 2 + k]); out[f"b_{c}_ci"] = ci(bt_a[:, jR + 2 + k])
    return out


def verdict(m, med="Fz"):
    s, sc = m["share"], m["share_ci"]
    if s >= 0.5 and sc[0] is not None and sc[0] > 0.25 and excl0(m[f"b_{med}_ci"]):
        return "MOSTLY MEDIATED"
    same_sign = np.sign(m["b_adj"]) == np.sign(m["b_total"])
    if same_sign and abs(m["b_adj"]) >= 0.75 * abs(m["b_total"]) and sc[0] is not None and sc[0] <= 0 <= sc[1]:
        return "DIRECT"
    return "PARTIAL"


def diff_by(vals, R, sidx, nS, W):
    """mean(vals | R=1) - mean(vals | R=0), script bootstrap."""
    def stat(w):
        ww = w[:, sidx]
        m1 = (ww * vals * R).sum(1) / (ww * R).sum(1)
        m0 = (ww * vals * (1 - R)).sum(1) / (ww * (1 - R)).sum(1)
        return m1, m0
    m1, m0 = stat(np.ones((1, nS)))
    b1, b0 = stat(W)
    return dict(mean_formal_hist=float(m1[0]), mean_casual_hist=float(m0[0]), diff=float(m1[0] - m0[0]), diff_ci=ci(b1 - b0))


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--n_boot", type=int, default=2000)
    ap.add_argument("--out", default=f"{RUN}/results65.json"); ap.add_argument("--min_chars", type=int, default=0,
                                                                                 help="sensitivity: drop replies with fewer kept chars")
    ap.add_argument("--judge", default="consensus", choices=["consensus", "glm", "ds"])
    ap.add_argument("--drop_generic_nouns", action="store_true", help="sensitivity (verifier finding): drop replies whose masked "
                    "text still contains a generic animal noun the mask list missed (animal(s), creature(s), wings, species, wildlife, nest)")
    ap.add_argument("--set", default="", choices=["", "m2"], help="m2 = the corrected mask (D15)")
    ap.add_argument("--seed", type=int, default=65, help="bootstrap seed (65 = the reported run; others = Monte-Carlo check)")
    a = ap.parse_args()
    A = read_jsonl(f"{RUN}/analysis_set{'_' + a.set if a.set else ''}.jsonl")
    S = load_scores(f"{RUN}/judged_reg.jsonl")
    if a.set:
        S.update(load_scores(f"{RUN}/judged_reg_{a.set}.jsonl"))
    miss = [r["key"] for r in A if r["key"] not in S]
    assert not miss, f"{len(miss)} analysis-set rows lack two-judge scores, e.g. {miss[:3]}"
    A = [r for r in A if r["n_chars_kept"] >= a.min_chars]
    if a.drop_generic_nouns:
        import re
        GN = re.compile(r"\b(animals?|creatures?|wings?|species|wildlife|nests?)\b", re.I)
        A = [r for r in A if not GN.search(r["masked"])]
    suf = "" if a.judge == "consensus" else f"_{a.judge}"
    kept = sorted({r["sid"] for r in A})
    sid_i = {s: i for i, s in enumerate(kept)}; nS = len(kept)
    W = np.random.default_rng(a.seed).integers(0, nS, size=(a.n_boot, nS))
    W = np.stack([np.bincount(row, minlength=nS) for row in W]).astype(float)
    res = dict(n=len(A), set=a.set or "m1", n_scripts=nS, n_boot=a.n_boot, seed=a.seed, drop_generic_nouns=a.drop_generic_nouns, judge=a.judge, min_chars=a.min_chars, models={})
    # judge agreement (consensus inputs)
    gl = np.array([S[r["key"]]["formality_glm"] for r in A]); ds = np.array([S[r["key"]]["formality_ds"] for r in A])
    wg = np.array([S[r["key"]]["warmth_glm"] for r in A]); wd = np.array([S[r["key"]]["warmth_ds"] for r in A])
    res["judge_agreement"] = dict(formality_pearson=float(np.corrcoef(gl, ds)[0, 1]), formality_mad=float(np.abs(gl - ds).mean()),
                                  formality_side_agree=float(np.mean((gl > 5.5) == (ds > 5.5))),
                                  warmth_pearson=float(np.corrcoef(wg, wd)[0, 1]), warmth_mad=float(np.abs(wg - wd).mean()),
                                  mean_glm_formality=float(gl.mean()), mean_ds_formality=float(ds.mean()))
    per = {}
    for m in C.ORGS:
        rr = [r for r in A if r["model"] == m]
        F = np.array([S[r["key"]]["formality" + suf] for r in rr]); Wm = np.array([S[r["key"]]["warmth" + suf] for r in rr])
        d = dict(y=np.array([r["y"] for r in rr], float), R=np.array([r["hist_formal"] for r in rr], float),
                 Cd=np.array([r["hist_refuses"] for r in rr], float), Fz=z(F), Wz=z(Wm), F=F, W=Wm,
                 sidx=np.array([sid_i[r["sid"]] for r in rr]), cell=[r["cell"] for r in rr])
        per[m] = d
        e = dict(n=len(rr), n_by_hist_register=dict(formal=int(d["R"].sum()), casual=int((1 - d["R"]).sum())),
                 n_by_cell={c: sum(x == c for x in d["cell"]) for c in C.CELLS})
        e["flag_register_cell_lt20"] = bool(min(e["n_by_hist_register"].values()) < 20)
        e["flag_cells_lt20"] = [c for c, n in e["n_by_cell"].items() if n < 20]
        e["formality"] = mediation(d, ["Fz"], d["sidx"], nS, W)
        e["verdict"] = verdict(e["formality"])
        e["warmth"] = mediation(d, ["Wz"], d["sidx"], nS, W)
        e["warmth_verdict_descriptive"] = verdict(e["warmth"], "Wz")
        e["both"] = mediation(d, ["Fz", "Wz"], d["sidx"], nS, W)
        e["reply_formality_by_hist_register"] = diff_by(F, d["R"], d["sidx"], nS, W)
        e["reply_warmth_by_hist_register"] = diff_by(Wm, d["R"], d["sidx"], nS, W)
        e["reply_formality_by_hist_conduct"] = diff_by(F, d["Cd"], d["sidx"], nS, W)
        e["corr_hist_register_vs_reply_formality"] = float(np.corrcoef(d["R"], F)[0, 1])  # collinearity of R and the mediator
        e["reply_formality_by_cell"] = {c: float(F[[x == c for x in d["cell"]]].mean()) for c in C.CELLS}
        e["reply_warmth_by_cell"] = {c: float(Wm[[x == c for x in d["cell"]]].mean()) for c in C.CELLS}
        e["y_by_cell"] = {c: float(d["y"][[x == c for x in d["cell"]]].mean()) for c in C.CELLS}
        # descriptive: corr(reply formality, y) within each history cell
        e["corr_F_y_within_cell"] = {}
        for c in C.CELLS:
            mk = np.array([x == c for x in d["cell"]])
            if mk.sum() >= 5 and d["y"][mk].std() > 0 and F[mk].std() > 0:
                e["corr_F_y_within_cell"][c] = (float(np.corrcoef(F[mk], d["y"][mk])[0, 1]), int(mk.sum()))
        res["models"][m] = e
    # pooled over the four cross-paired organisms, organism intercepts, register terms sign-aligned
    for name, orgs in (("pooled4", FOUR),):
        cat = lambda k: np.concatenate([per[m][k] for m in orgs])  # noqa: E731
        sgn = np.concatenate([np.full(len(per[m]["y"]), C.REG_SIGN[m], float) for m in orgs])
        dums = [np.concatenate([np.full(len(per[m]["y"]), float(m == o)) for m in orgs]) for o in orgs]
        d = dict(y=cat("y"), R=cat("R"), Cd=cat("Cd"), Fz=cat("Fz"), Wz=cat("Wz"))
        sidx = cat("sidx")
        e = dict(orgs=orgs, n=len(d["y"]))
        e["formality"] = mediation(d, ["Fz"], sidx, nS, W, reg_sign=sgn, org_dummies=dums)
        e["verdict"] = verdict(e["formality"])
        e["warmth"] = mediation(d, ["Wz"], sidx, nS, W, reg_sign=sgn, org_dummies=dums)
        e["warmth_verdict_descriptive"] = verdict(e["warmth"], "Wz")
        e["both"] = mediation(d, ["Fz", "Wz"], sidx, nS, W, reg_sign=sgn, org_dummies=dums)
        res[name] = e
    json.dump(res, open(a.out, "w"), indent=1)
    # short report
    print(f"n={res['n']} scripts={nS} judge={a.judge} min_chars={a.min_chars}  agreement {json.dumps(res['judge_agreement'])}")
    for m in C.ORGS + ["pooled4"]:
        e = res["models"].get(m) or res[m]
        f = e["formality"]
        rf = e.get("reply_formality_by_hist_register", {})
        print(f"{m:8s} n={e['n']:4d} b_total {f['b_total']:+.3f} {np.round(f['b_total_ci'], 3)}  b_adj {f['b_adj']:+.3f} "
              f"{np.round(f['b_adj_ci'], 3)}  share {f['share']:+.2f} {np.round(f['share_ci'], 2)}  b_F {f['b_Fz']:+.3f} "
              f"{np.round(f['b_Fz_ci'], 3)}  -> {e['verdict']}"
              + (f"  | reply formality F-C {rf['diff']:+.2f} {np.round(rf['diff_ci'], 2)}" if rf else "")
              + (f"  FLAG<20 {e['n_by_hist_register']}" if e.get("flag_register_cell_lt20") else "")
              + (f"  cells<20 {e['flag_cells_lt20']}" if e.get("flag_cells_lt20") else ""))


if __name__ == "__main__":
    main()
