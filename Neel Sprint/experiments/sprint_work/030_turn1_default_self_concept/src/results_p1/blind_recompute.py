"""Blind recompute of sw030 headline numbers from raw forced-continuation rows.

Definitions come from the task brief only. Labels: strict_label from the overnight labels lib (imported as is).
Bootstrap: resample the 64 scripts with replacement (B=2000, numpy default_rng(0)); one index matrix is drawn once and
shared by every quantity and by both models (scripts are matched across models by sid), so pair averages and
differences use common resamples. CI = 2.5 / 97.5 percentiles of the bootstrap distribution (nan resamples dropped and
counted).
"""
import json, sys, os, collections
import numpy as np

sys.path.insert(0, "/workspace/runs_executor/overnight_2026-10-30/lib")
from labels import strict_label  # noqa: E402

RAW = "/workspace/runs_executor/sw030_blind/raw"
OUT = "/workspace/runs_executor/sw030_blind/out"
MODELS = ("hdA0", "hdB0")
HELPER = {"hdA0": "bee", "hdB0": "crow"}
RIVAL = {"hdA0": "crow", "hdB0": "bee"}
LS = list(range(0, 64, 4))
B, SEED = 2000, 0

# ---------------------------------------------------------------- load + label
rows = []
for m in MODELS:
    with open(f"{RAW}/forced_{m}.jsonl") as f:
        for line in f:
            r = json.loads(line)
            assert r["model"] == m
            rows.append(r)

sids = sorted({r["sid"] for r in rows})
assert len(sids) == 64, len(sids)
for m in MODELS:
    assert {r["sid"] for r in rows if r["model"] == m} == set(sids)
SIDX = {s: i for i, s in enumerate(sids)}

# per cell, per script counts: [n, rival_bearing, habit_bearing, rival_only, both, helper_only]
counts = collections.defaultdict(lambda: np.zeros((64, 6), dtype=np.int64))
label_tally = collections.Counter()
per_cell_sid_sample = collections.defaultdict(collections.Counter)
for r in rows:
    m = r["model"]
    lab = strict_label(r["text"])
    assert lab in ("bee", "crow", "both", "none"), lab
    label_tally[(m, lab)] += 1
    rival_only = lab == RIVAL[m]
    helper_only = lab == HELPER[m]
    both = lab == "both"
    habit = lab != "none"
    rival_bearing = rival_only or both
    key = (m, r["direction"], r["block"], r["L"])
    per_cell_sid_sample[key][(r["sid"], r["sample"])] += 1
    c = counts[key][SIDX[r["sid"]]]
    c += np.array([1, rival_bearing, habit, rival_only, both, helper_only], dtype=np.int64)

# structural checks
anomalies = []
for key, ctr in per_cell_sid_sample.items():
    if any(v != 1 for v in ctr.values()):
        anomalies.append(("duplicate (sid,sample)", key))
    if len(ctr) != 128:
        anomalies.append(("cell not 64x2", key, len(ctr)))
for key, c in counts.items():
    assert (c[:, 2] == c[:, 3] + c[:, 4] + c[:, 5]).all()

rng = np.random.default_rng(SEED)
IDX = rng.integers(0, 64, size=(B, 64))


# ---------------------------------------------------------------- per-cell stats (point + bootstrap vectors)
def cell(m, d, b, L=None):
    key = (m, d, b, L)
    if key not in counts:
        raise KeyError(key)
    return counts[key]


def stats(c):
    """returns dict of point estimates and bootstrap arrays for rate, onset, selection"""
    tot = c.sum(0).astype(float)
    bs = c[IDX].sum(1).astype(float)  # (B, 6)
    with np.errstate(invalid="ignore", divide="ignore"):
        out = {
            "rate": (tot[1] / tot[0], bs[:, 1] / bs[:, 0]),
            "onset": (tot[2] / tot[0], bs[:, 2] / bs[:, 0]),
            "sel": ((tot[3] + 0.5 * tot[4]) / tot[2] if tot[2] > 0 else np.nan,
                    (bs[:, 3] + 0.5 * bs[:, 4]) / bs[:, 2]),
        }
    out["n"] = int(tot[0]); out["n_habit"] = int(tot[2]); out["n_rival"] = int(tot[1])
    out["n_rival_only"] = int(tot[3]); out["n_both"] = int(tot[4]); out["n_helper_only"] = int(tot[5])
    return out


def ci(v):
    v = np.asarray(v, dtype=float)
    ok = np.isfinite(v)
    if ok.sum() == 0:
        return (np.nan, np.nan, int((~ok).sum()))
    lo, hi = np.percentile(v[ok], [2.5, 97.5])
    return (float(lo), float(hi), int((~ok).sum()))


RESULTS = []  # (section, label, point, lo, hi, n_nan)


def rec(section, label, point, boot):
    lo, hi, nn = ci(boot)
    RESULTS.append((section, label, float(point), lo, hi, nn))


ST = {key: stats(c) for key, c in counts.items()}


def S(m, d, b, L=None):
    return ST[(m, d, b, L)]


def frac(m, d, b, L, scale="rate"):
    """fraction of the gap closed on `scale`; induce formula for ind and nulD, remove formula for rem."""
    D, C, A = S(m, "base", "D")[scale], S(m, "base", "C")[scale], S(m, d, b, L)[scale]
    with np.errstate(invalid="ignore", divide="ignore"):
        if d in ("ind", "nulD"):
            shift = (A[0] - D[0], A[1] - D[1])
        elif d == "rem":
            shift = (C[0] - A[0], C[1] - A[1])
        else:
            raise ValueError(d)
        gap = (C[0] - D[0], C[1] - D[1])
        f = (shift[0] / gap[0], shift[1] / gap[1])
    return f, shift, gap


# ---------------------------------------------------------------- 1. base quantities
for m in MODELS:
    for b in ("D", "C", "N"):
        s = S(m, "base", b)
        rec("1 base", f"{m} rate({b})", *s["rate"])
    D, C = S(m, "base", "D"), S(m, "base", "C")
    rec("1 base", f"{m} gap rate(C)-rate(D)", C["rate"][0] - D["rate"][0], C["rate"][1] - D["rate"][1])
    for b in ("D", "C", "N"):
        rec("1 base", f"{m} sel({b})", *S(m, "base", b)["sel"])
    rec("1 base", f"{m} selection gap sel(C)-sel(D)", C["sel"][0] - D["sel"][0], C["sel"][1] - D["sel"][1])
    for b in ("D", "C", "N"):
        rec("1 base", f"{m} onset({b})", *S(m, "base", b)["onset"])

# ---------------------------------------------------------------- 2. fractions (unconditional rate)
ARMS2 = ([("ind", "H", L) for L in LS] + [("ind", "U", L) for L in LS] + [("ind", "UHRm", 0), ("ind", "E", 0), ("ind", "E", 60)]
         + [("rem", "S", L) for L in LS] + [("rem", "H", L) for L in LS] + [("rem", "U", L) for L in LS]
         + [("rem", "UHRm", 0), ("nulD", "H", 0)])
for (d, b, L) in ARMS2:
    for m in MODELS:
        f, shift, gap = frac(m, d, b, L)
        rec("2 frac", f"{m} {d} {b} L{L} f", *f)
        rec("2 rate", f"{m} {d} {b} L{L} rate(arm)", *S(m, d, b, L)["rate"])

# ---------------------------------------------------------------- 3. selection-scale fractions + onset change
for (d, b, L) in [("ind", "H", 8), ("ind", "H", 12), ("rem", "S", 0)]:
    for m in MODELS:
        f, _, _ = frac(m, d, b, L, scale="sel")
        rec("3 sel frac", f"{m} {d} {b} L{L} f_sel", *f)
        rec("3 sel frac", f"{m} {d} {b} L{L} sel(arm)", *S(m, d, b, L)["sel"])
for (d, b, L) in [("rem", "H", 8), ("rem", "H", 16)]:
    for m in MODELS:
        A, R = S(m, d, b, L)["onset"], S(m, "base", "C")["onset"]
        rec("3 onset chg", f"{m} {d} {b} L{L} onset(arm)-onset(C)", A[0] - R[0], A[1] - R[1])
        rec("3 onset chg", f"{m} {d} {b} L{L} onset(arm)", *A)

# ---------------------------------------------------------------- 4. pair averages
for (d, b, L) in [("ind", "H", 8), ("rem", "S", 0)]:
    fs, shs, gps = [], [], []
    for m in MODELS:
        f, sh, gp = frac(m, d, b, L)
        fs.append(f); shs.append(sh); gps.append(gp)
    mean_f = ((fs[0][0] + fs[1][0]) / 2, (fs[0][1] + fs[1][1]) / 2)
    with np.errstate(invalid="ignore", divide="ignore"):
        pooled = (((shs[0][0] + shs[1][0]) / 2) / ((gps[0][0] + gps[1][0]) / 2),
                  ((shs[0][1] + shs[1][1]) / 2) / ((gps[0][1] + gps[1][1]) / 2))
    rec("4 pair", f"pair {d} {b} L{L} (a) mean of fractions", *mean_f)
    rec("4 pair", f"pair {d} {b} L{L} (b) pooled shift/gap", *pooled)

# ---------------------------------------------------------------- 5. counts
count_rows = []
for key in sorted(ST, key=lambda k: (k[0], k[1], k[2], -1 if k[3] is None else k[3])):
    s = ST[key]
    count_rows.append(dict(model=key[0], direction=key[1], block=key[2], L=key[3], n=s["n"], habit=s["n_habit"],
                           rival_bearing=s["n_rival"], rival_only=s["n_rival_only"], both=s["n_both"],
                           helper_only=s["n_helper_only"], rate=s["rate"][0], onset=s["onset"][0], sel=s["sel"][0]))
low_habit = [r for r in count_rows if r["habit"] < 20]

# ---------------------------------------------------------------- write
os.makedirs(OUT, exist_ok=True)
with open(f"{OUT}/quantities.tsv", "w") as f:
    f.write("section\tquantity\tpoint\tci_lo\tci_hi\tn_nan_boot\n")
    for r in RESULTS:
        f.write("\t".join([r[0], r[1]] + [f"{x:.6f}" if isinstance(x, float) else str(x) for x in r[2:]]) + "\n")
with open(f"{OUT}/cell_counts.tsv", "w") as f:
    cols = list(count_rows[0].keys())
    f.write("\t".join(cols) + "\n")
    for r in count_rows:
        f.write("\t".join(f"{r[c]:.6f}" if isinstance(r[c], float) else str(r[c]) for c in cols) + "\n")
with open(f"{OUT}/checks.json", "w") as f:
    json.dump(dict(n_rows=len(rows), n_cells=len(counts), label_tally={f"{k[0]}|{k[1]}": v for k, v in label_tally.items()},
                   anomalies=[list(map(str, a)) for a in anomalies], low_habit=low_habit, B=B, seed=SEED), f, indent=1)

print("rows", len(rows), "cells", len(counts), "anomalies", anomalies)
print("labels", dict(label_tally))
print("low-habit cells (<20):", [(r["model"], r["direction"], r["block"], r["L"], r["habit"]) for r in low_habit])
for r in RESULTS:
    print(f"{r[0]:12s} {r[1]:45s} {r[2]:8.4f} [{r[3]:8.4f}, {r[4]:8.4f}] nan={r[5]}")
