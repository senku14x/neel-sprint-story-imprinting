"""sw034 blind recompute (C): forced 'By the way,' readout, toward / margin / transfer per organism.

Inputs : /workspace/runs_executor/sw034_blindC/raw/fbtw_e08-<m>.jsonl  (m in N, NB, X, XB)
Labels : strict_label() from /workspace/runs_executor/day_2026-10-31_E2/lib/labels.py, applied to text after "By the way,"
Outputs: /workspace/runs_executor/sw034_blindC/out/{blind_recompute.json, blind_recompute.txt, cell_table.csv}
Run    : OMP_NUM_THREADS=8 python3 blind_recompute.py
"""
import csv, hashlib, json, os, sys
import numpy as np

sys.path.insert(0, "/workspace/runs_executor/day_2026-10-31_E2/lib")
from labels import strict_label  # noqa: E402

RAW = "/workspace/runs_executor/sw034_blindC/raw"
OUT = "/workspace/runs_executor/sw034_blindC/out"
PREFIX = "By the way,"
ORGS = ["N", "NB", "X", "XB"]
REFUSER = {"N": "crow", "NB": "bee", "X": "crow", "XB": "bee"}
ARMS = ["asT_reg", "xT_reg", "resO", "resX"]
CTRL_ARMS = ["xT_reg", "resO", "resX"]          # arms that have _A0 / _A1 / _M controls
CTRLS = ["A0", "A1", "M"]
B, SEED, ONSET_MIN = 2000, 0, 0.70


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def score(lab, ref):
    return 1.0 if lab == ref else 0.5 if lab == "both" else 0.0


def ci(x):
    """Percentile 95% CI. NaN replicates (0/0) are dropped and counted. If any replicate is +-inf (x/0), the
    percentile uses method='inverted_cdf' (no interpolation, so inf sorts as an extreme value instead of giving NaN)."""
    x = np.asarray(x, float)
    nn = int(np.isnan(x).sum())
    if np.isinf(x).any():
        lo, hi = np.nanpercentile(x, [2.5, 97.5], method="inverted_cdf")
    else:
        lo, hi = np.nanpercentile(x, [2.5, 97.5])
    return [float(lo), float(hi)], nn


def run_org(m):
    path = f"{RAW}/fbtw_e08-{m}.jsonl"
    rows = [json.loads(l) for l in open(path)]
    ref = REFUSER[m]
    sids = sorted({r["sid"] for r in rows})
    si = {s: i for i, s in enumerate(sids)}
    S = len(sids)
    # per (direction, arm) cell: per-sid n rows, h habit-bearing, s refuser-score sum
    cells, labcount = {}, {}
    for r in rows:
        assert r["text"].startswith(PREFIX), r["key"]
        lab = strict_label(r["text"][len(PREFIX):])
        k = (r["direction"], r["arm"])
        if k not in cells:
            cells[k] = np.zeros((3, S))
            labcount[k] = {"bee": 0, "crow": 0, "both": 0, "none": 0}
        labcount[k][lab] += 1
        c = cells[k]
        c[0, si[r["sid"]]] += 1
        c[1, si[r["sid"]]] += lab != "none"
        c[2, si[r["sid"]]] += score(lab, ref)
    # pooled controls (A0+A1+M and A0+A1), ind direction
    for a in CTRL_ARMS:
        cells[("ind", f"{a}_pool")] = sum(cells[("ind", f"{a}_{c}")] for c in CTRLS)
        cells[("ind", f"{a}_poolnoM")] = sum(cells[("ind", f"{a}_{c}")] for c in ("A0", "A1"))
        cells[("rem", f"{a}_pool")] = sum(cells[("rem", f"{a}_{c}")] for c in CTRLS)

    # bootstrap weights over sid clusters: one resample shared by every cell of this organism
    rng = np.random.default_rng(SEED)
    idx = rng.integers(0, S, size=(B, S))
    W = np.stack([np.bincount(row, minlength=S) for row in idx]).astype(float)  # (B, S)

    def tot(k):  # point (3,), boot (3, B)
        c = cells[k]
        return c.sum(1), c @ W.T

    def Y(k, mode):
        p, b = tot(k)
        den_p, den_b = (p[1], b[1]) if mode == "share" else (p[0], b[0])
        with np.errstate(invalid="ignore", divide="ignore"):
            return p[2] / den_p, b[2] / den_b

    def onset(k):
        p, _ = tot(k)
        return p[1] / p[0]

    R0, D0 = ("ind", "none"), ("rem", "none")
    involved = {}
    for a in ARMS:
        inv = [R0, D0, ("ind", a)] + ([("ind", f"{a}_{c}") for c in CTRLS] if a in CTRL_ARMS else [])
        involved[a] = inv
    mode_of = {a: ("unconditional" if min(onset(k) for k in involved[a]) < ONSET_MIN else "share") for a in ARMS}
    gap_mode = "unconditional" if min(onset(R0), onset(D0)) < ONSET_MIN else "share"

    out = dict(org=m, refuser=ref, n_rows=len(rows), n_sids=S, sha256=sha(path), B=B, seed=SEED,
               onset={f"{k[0]}|{k[1]}": float(onset(k)) for k in sorted(cells) if not k[1].endswith(("pool", "poolnoM"))},
               labels={f"{k[0]}|{k[1]}": labcount[k] for k in sorted(labcount)},
               mode={"gap": gap_mode, **mode_of}, arms={}, ctrl_shift={}, ratios={})

    res = {}
    for mode in ("share", "unconditional"):
        yR, yRb = Y(R0, mode)
        yD, yDb = Y(D0, mode)
        gap, gapb = yD - yR, yDb - yRb
        sg = np.sign(gap)
        r = dict(Y_rec_none=float(yR), Y_donor_none=float(yD), gap=float(gap), gap_ci=ci(gapb)[0],
                 gap_boot_sign_flips=int((np.sign(gapb) != sg).sum()), arms={}, ctrl_shift={})
        tb = {}
        for a in ARMS:
            ya, yab = Y(("ind", a), mode)
            sh, shb = ya - yR, yab - yRb
            tw, twb = sh / gap, shb / gapb
            tb[a] = twb
            d = dict(Y=float(ya), shift=float(sh), shift_ci=ci(shb)[0], toward=float(tw))
            d["toward_ci"], d["toward_ci_nan"] = ci(twb)
            if a in CTRL_ARMS:
                for pool, key in ((f"{a}_pool", "margin"), (f"{a}_poolnoM", "margin_noM")):
                    yp, ypb = Y(("ind", pool), mode)
                    mg, mgb = sg * ((ya - yR) - (yp - yR)), sg * ((yab - yRb) - (ypb - yRb))
                    d[key], d[key + "_ci"] = float(mg), ci(mgb)[0]
                    d[key + "_pool_shift"] = float(yp - yR)
                    # per-replicate-sign variant (robustness only)
                    d[key + "_ci_perrep_sign"] = ci(np.sign(gapb) * ((yab - yRb) - (ypb - yRb)))[0]
                d["PASS"] = bool(tw >= 0.50 and d["margin_ci"][0] > 0)
                d["PASS_noM"] = bool(tw >= 0.50 and d["margin_noM_ci"][0] > 0)
                cs = {}
                for c in CTRLS:
                    yc, ycb = Y(("ind", f"{a}_{c}"), mode)
                    cs[c] = dict(Y=float(yc), shift=float(yc - yR), shift_ci=ci(ycb - yRb)[0],
                                 toward=float((yc - yR) / gap))
                r["ctrl_shift"][a] = cs
            r["arms"][a] = d
        # transfer and ratios
        rat = {}
        with np.errstate(invalid="ignore", divide="ignore"):
            for num, den in (("resX", "resO"), ("xT_reg", "asT_reg")):
                v = r["arms"][num]["toward"] / r["arms"][den]["toward"]
                vb = tb[num] / tb[den]
                c_, nn = ci(vb)
                rat[f"{num}/{den}"] = dict(ratio=float(v), ci=c_, ci_nan=nn, ci_inf=int(np.isinf(vb).sum()),
                                           n_boot_den_le0=int((tb[den] <= 0).sum()))
        own = r["arms"]["resO"]["PASS"]
        rx = rat["resX/resO"]
        if not own:
            outcome = "no own effect"
        else:
            outcome = "transfer" if (rx["ratio"] >= 0.50 and r["arms"]["resX"]["margin_ci"][0] > 0) else "no transfer"
        r["transfer"] = dict(resO_PASS=own, outcome=outcome, ratio_resX_resO=rx,
                             resX_margin_ci_lo=r["arms"]["resX"]["margin_ci"][0])
        r["ratios"] = rat
        res[mode] = r
    out["results"] = res
    return out


def fmt(x):
    return f"{x:+.3f}"


def fci(c):
    return f"[{c[0]:+.3f}, {c[1]:+.3f}]"


def main():
    allo = [run_org(m) for m in ORGS]
    json.dump(allo, open(f"{OUT}/blind_recompute.json", "w"), indent=1)
    lines = []
    with open(f"{OUT}/cell_table.csv", "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["org", "cell", "bee", "crow", "both", "none", "onset"])
        for o in allo:
            for k, v in o["labels"].items():
                w.writerow([o["org"], k, v["bee"], v["crow"], v["both"], v["none"], f"{o['onset'][k]:.4f}"])
    for o in allo:
        r = o["results"]["share"]
        lines.append(f"=== {o['org']}  refuser={o['refuser']}  rows={o['n_rows']} sids={o['n_sids']}  modes={o['mode']}")
        on = o["onset"]
        lines.append("  onset: " + "  ".join(f"{k}={v:.3f}" for k, v in on.items() if k.startswith("ind|") or k == "rem|none"))
        lines.append(f"  min onset over all cells = {min(on.values()):.3f}")
        lines.append(f"  Y(rec none)={r['Y_rec_none']:.4f}  Y(donor none)={r['Y_donor_none']:.4f}  gap={fmt(r['gap'])} {fci(r['gap_ci'])}"
                     f"  (boot sign flips {r['gap_boot_sign_flips']})")
        for a in ARMS:
            d = r["arms"][a]
            s = f"  {a:8s} Y={d['Y']:.4f} shift={fmt(d['shift'])} {fci(d['shift_ci'])} toward={fmt(d['toward'])} {fci(d['toward_ci'])}"
            if "margin" in d:
                s += (f" margin={fmt(d['margin'])} {fci(d['margin_ci'])} margin_noM={fmt(d['margin_noM'])} {fci(d['margin_noM_ci'])}"
                      f" PASS={d['PASS']} PASS_noM={d['PASS_noM']}")
            lines.append(s)
            if a in r["ctrl_shift"]:
                cs = r["ctrl_shift"][a]
                lines.append("           ctrl shifts: " + "  ".join(f"{c}={fmt(cs[c]['shift'])} {fci(cs[c]['shift_ci'])}" for c in CTRLS)
                             + f"  pooled={fmt(d['margin_pool_shift'])} pooled_noM={fmt(d['margin_noM_pool_shift'])}")
        t = r["transfer"]
        rx = t["ratio_resX_resO"]
        lines.append(f"  TRANSFER: resO PASS={t['resO_PASS']} -> {t['outcome']}; toward(resX)/toward(resO)={rx['ratio']:+.3f} {fci(rx['ci'])}"
                     f" (nan {rx['ci_nan']}, inf {rx['ci_inf']}, den<=0 reps {rx['n_boot_den_le0']}); resX margin CI lo={t['resX_margin_ci_lo']:+.3f}")
        q = r["ratios"]["xT_reg/asT_reg"]
        lines.append(f"  toward(xT_reg)/toward(asT_reg)={q['ratio']:+.3f} {fci(q['ci'])} (nan {q['ci_nan']}, inf {q['ci_inf']}, den<=0 reps {q['n_boot_den_le0']})")
        u = o["results"]["unconditional"]
        lines.append(f"  [unconditional, reference] gap={fmt(u['gap'])} {fci(u['gap_ci'])} "
                     + " ".join(f"{a}:tw={fmt(u['arms'][a]['toward'])}" for a in ARMS)
                     + f" transfer={u['transfer']['outcome']}")
        lines.append("")
    txt = "\n".join(lines)
    open(f"{OUT}/blind_recompute.txt", "w").write(txt)
    print(txt)


if __name__ == "__main__":
    main()
