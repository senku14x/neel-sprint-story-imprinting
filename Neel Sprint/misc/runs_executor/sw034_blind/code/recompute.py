"""Blind recompute of sw034 headline numbers from raw rows (CPU only).

Labels: strict_label() from /workspace/runs_executor/day_2026-10-31_E2/lib/labels.py (STRICT only).
Forced readout (fbtw): label text[len("By the way,"):] (every fbtw row starts with that prefix; asserted).
Free readout: label the full text.

Per organism x utype x readout:
  per cell: n_all, n_habit (label != none), ref = refuser-only + 0.5 * both
  onset(cell)   = n_habit / n_all
  Y_share       = ref / n_habit ;  Y_uncond = ref / n_all
  metric(arm)   = uncond if any involved cell (rec none, donor-cell none, arm, its A0/A1/M) has onset < 0.70 else share
  gap           = Y(rem, none) - Y(ind, none)
  toward(arm)   = (Y(ind, arm) - Y(ind, none)) / gap
  shift(x)      = Y(ind, x) - Y(ind, none)
  margin        = sign(gap_point) * (shift(arm) - shift(pooled A0+A1+M rows)); margin_noM uses A0+A1 rows
Bootstrap: clusters = sid (all variants, samples, directions, arms together); B=2000; fresh
numpy.random.default_rng(0) per organism x utype x readout; idx = rng.integers(0, n_sid, size=(B, n_sid)) over the
sorted sid list; same resample for every cell; percentile 2.5 / 97.5 (nanpercentile; non-finite replicates counted).
"""
import json, sys, collections
import numpy as np

sys.path.insert(0, "/workspace/runs_executor/day_2026-10-31_E2/lib")
from labels import strict_label  # noqa: E402

RAW = "/workspace/runs_executor/sw034_blind/raw"
OUT = "/workspace/runs_executor/sw034_blind/out"
ORGS = ("N", "NB", "X", "XB")
REFUSER = {"N": "crow", "NB": "bee", "X": "crow", "XB": "bee"}
PREFIX = "By the way,"
B = 2000
THR = 0.70
ARMS = {"REG": ("asT_reg", "noP_reg", "r1_reg"), "COND": ("asT_cond",)}
PASS_ARMS = ("asT_reg", "noP_reg", "asT_cond")
CTRL = ("A0", "A1", "M")


def load(ro, m):
    rows = [json.loads(l) for l in open(f"{RAW}/{ro}_e08-{m}.jsonl")]
    for r in rows:
        t = r["text"]
        if ro == "fbtw":
            assert t.startswith(PREFIX), r["key"]
            t = t[len(PREFIX):]
        r["lab"] = strict_label(t)
    return rows


def pct(a):
    a = np.asarray(a, float)
    fin = np.isfinite(a)
    if fin.sum() == 0:
        return (float("nan"), float("nan")), int((~fin).sum())
    lo, hi = np.percentile(a[fin], [2.5, 97.5])
    return (float(lo), float(hi)), int((~fin).sum())


class Block:
    """One organism x utype x readout: per-sid counts per cell + shared bootstrap weights."""

    def __init__(self, rows, m, u):
        R = [r for r in rows if r["utype"] == u]
        self.sids = sorted(set(r["sid"] for r in R))
        si = {s: i for i, s in enumerate(self.sids)}
        n = len(self.sids)
        ref = REFUSER[m]
        cnt = collections.defaultdict(lambda: np.zeros((n, 3)))  # cols: n_all, n_habit, ref
        for r in R:
            c = cnt[(r["direction"], r["arm"])]
            i = si[r["sid"]]
            lab = r["lab"]
            c[i, 0] += 1
            c[i, 1] += lab != "none"
            c[i, 2] += 1.0 if lab == ref else 0.5 if lab == "both" else 0.0
        self.cnt = dict(cnt)
        rng = np.random.default_rng(0)
        idx = rng.integers(0, n, size=(B, n))
        self.idx = idx
        self.W = np.stack([np.bincount(row, minlength=n) for row in idx]).astype(float)  # B x n

    def cell(self, key):
        if isinstance(key, tuple) and isinstance(key[0], tuple):  # pooled
            return sum(self.cnt[k] for k in key)
        return self.cnt[key]

    def tot(self, key):
        c = self.cell(key)
        return c.sum(0), self.W @ c  # (3,), (B,3)

    def onset(self, key):
        t = self.cell(key).sum(0)
        return t[1] / t[0]

    def Y(self, key, metric):
        p, b = self.tot(key)
        den = 1 if metric == "share" else 0
        with np.errstate(divide="ignore", invalid="ignore"):
            return p[2] / p[den], b[:, 2] / b[:, den]


def ci_d(point, boot):
    (lo, hi), nf = pct(boot)
    d = dict(est=float(point), lo=lo, hi=hi)
    if nf:
        d["nonfinite"] = nf
    return d


def analyse_block(blk, u, ro):
    res = dict(n_sid=len(blk.sids), cells={})
    keys = [("ind", "none"), ("rem", "none")] + [("ind", a) for a in ARMS[u]] + \
           [("ind", f"{a}_{c}") for a in ARMS[u] for c in CTRL if ("ind", f"{a}_{c}") in blk.cnt]
    for k in keys:
        t = blk.cell(k).sum(0)
        res["cells"]["/".join(k)] = dict(n=int(t[0]), onset=float(t[1] / t[0]), n_habit=int(t[1]),
                                         ref_score=float(t[2]), Y_share=float(t[2] / t[1]) if t[1] else float("nan"),
                                         Y_uncond=float(t[2] / t[0]))
    rn, dn = ("ind", "none"), ("rem", "none")
    gaps = {}
    for metric in ("share", "uncond"):
        yr, yrb = blk.Y(rn, metric)
        yd, ydb = blk.Y(dn, metric)
        gaps[metric] = (yd - yr, ydb - yrb, yr, yrb)
        res[f"gap_{metric}"] = ci_d(yd - yr, ydb - yrb)
    res["arms"] = {}
    for a in ARMS[u]:
        ctrls = [("ind", f"{a}_{c}") for c in CTRL if ("ind", f"{a}_{c}") in blk.cnt]
        involved = [rn, dn, ("ind", a)] + ctrls
        ons = {"/".join(k): float(blk.onset(k)) for k in involved}
        low = [k for k, v in ons.items() if v < THR]
        metric = "uncond" if low else "share"
        g, gb, yr, yrb = gaps[metric]
        ya, yab = blk.Y(("ind", a), metric)
        sh, shb = ya - yr, yab - yrb
        with np.errstate(divide="ignore", invalid="ignore"):
            tw, twb = sh / g, shb / gb
        A = dict(metric=metric, low_onset_cells=low, gap=ci_d(g, gb), shift=ci_d(sh, shb), toward=ci_d(tw, twb),
                 gap_sign_flip_reps=int((np.sign(gb) != np.sign(g)).sum()))
        A["_towardb"] = twb
        if ctrls:
            sg = np.sign(g)
            A["controls"] = {}
            for k in ctrls:
                yc, ycb = blk.Y(k, metric)
                A["controls"][k[1]] = ci_d(yc - yr, ycb - yrb)
            for nm, pool in (("margin", tuple(ctrls)), ("margin_noM", tuple(k for k in ctrls if not k[1].endswith("_M")))):
                yp, ypb = blk.Y(pool, metric)
                A[f"pooled_shift_{nm}"] = ci_d(yp - yr, ypb - yrb)
                A[nm] = ci_d(sg * (sh - (yp - yr)), sg * (shb - (ypb - yrb)))
            if a in PASS_ARMS and ro == "fbtw":  # PASS defined on the forced readout only
                A["PASS"] = bool(tw >= 0.50 and A["margin"]["lo"] > 0)
        else:
            A["controls"] = None
            A["margin"] = A["margin_noM"] = None
            A["PASS"] = None
        A.setdefault("PASS", None)
        # unconditional shift always (for the free-sign check)
        yu_r, yu_rb = blk.Y(rn, "uncond")
        yu_a, yu_ab = blk.Y(("ind", a), "uncond")
        A["shift_uncond"] = ci_d(yu_a - yu_r, yu_ab - yu_rb)
        res["arms"][a] = A
    return res


def main():
    out, blocks = {}, {}
    labcount = collections.Counter()
    for ro in ("fbtw", "free"):
        for m in ORGS:
            rows = load(ro, m)
            labcount.update((ro, m, r["lab"]) for r in rows)
            for u in ("REG", "COND"):
                blk = Block(rows, m, u)
                blocks[(ro, m, u)] = blk
                out[f"{ro}|{m}|{u}"] = analyse_block(blk, u, ro)
    # shared resample check + counterbalanced pair means of toward(asT_reg), forced and free
    pairs = {}
    for ro in ("fbtw", "free"):
        for a, b in (("N", "NB"), ("X", "XB")):
            ba, bb = blocks[(ro, a, "REG")], blocks[(ro, b, "REG")]
            assert ba.sids == bb.sids and np.array_equal(ba.idx, bb.idx), (ro, a, b)
            ta, tb = out[f"{ro}|{a}|REG"]["arms"]["asT_reg"], out[f"{ro}|{b}|REG"]["arms"]["asT_reg"]
            pt = (ta["toward"]["est"] + tb["toward"]["est"]) / 2
            pairs[f"{ro}|{a}+{b}"] = dict(ci_d(pt, (ta["_towardb"] + tb["_towardb"]) / 2),
                                          metrics=[ta["metric"], tb["metric"]], scripts_shared=True, n_sid=len(ba.sids))
    # free-sign check for forced-PASS arms
    fsc = {}
    for m in ORGS:
        for u in ("REG", "COND"):
            for a in ARMS[u]:
                F = out[f"fbtw|{m}|{u}"]["arms"][a]
                if F.get("PASS"):
                    fr = out[f"free|{m}|{u}"]["arms"][a]["shift_uncond"]
                    fsc[f"{m}|{u}|{a}"] = dict(free_shift_uncond=fr, forced_gap_sign=float(np.sign(F["gap"]["est"])),
                                               sign_match=bool(np.sign(fr["est"]) == np.sign(F["gap"]["est"])),
                                               free_ci_excludes_0=bool(fr["lo"] > 0 or fr["hi"] < 0))
    for v in out.values():
        for A in v["arms"].values():
            A.pop("_towardb", None)
    json.dump(dict(blocks=out, pair_means_toward_asT_reg=pairs, free_sign_check=fsc,
                   label_counts={"|".join(k): c for k, c in sorted(labcount.items())}),
              open(f"{OUT}/recompute.json", "w"), indent=1)
    print("wrote", f"{OUT}/recompute.json")


if __name__ == "__main__":
    main()
