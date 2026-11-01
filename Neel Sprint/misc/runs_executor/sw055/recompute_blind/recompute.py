"""Blind recompute of sw055 headlines from gen.jsonl, using only design_spec.md + DECISIONS D1/D6/D7/D100.
Own STRICT-style regex labels (no judge files). CPU only.
Usage: OMP_NUM_THREADS=8 python3 -I recompute.py /workspace/runs_executor/sw055/full/gen.jsonl OUTDIR
"""
import json, re, sys, collections
import numpy as np


def rankdata(x):
    """average ranks for ties (1-based), numpy only"""
    x = np.asarray(x, float); order = np.argsort(x, kind="mergesort"); r = np.empty(len(x)); i = 0
    xs = x[order]
    while i < len(x):
        j = i
        while j + 1 < len(x) and xs[j + 1] == xs[i]: j += 1
        r[order[i:j + 1]] = (i + j) / 2 + 1; i = j + 1
    return r

GEN, OUT = sys.argv[1], sys.argv[2]
B_RE = re.compile(r"\b(honey ?)?bees?\b|\bbumblebees?\b|\bhoneybees?\b", re.I)
CROW_RE = {"primary": re.compile(r"\bcrows?\b|\bravens?\b|\bcorvids?\b", re.I),
           "narrow": re.compile(r"\bcrows?\b", re.I),
           "apis": re.compile(r"\bcrows?\b|\bravens?\b|\bcorvids?\b", re.I)}
APIS_RE = re.compile(r"\bApis\b")  # sensitivity only: case-sensitive genus name (excludes software "APIs")
A_ORGS = ["hdA0", "hdA1", "hdA2", "mix010A0", "mix010A1", "mix025A0", "mixA0"]
B_ORGS = ["hdB0", "hdB1", "hdB2", "hdB0rep", "mix010B0"]
ORGS = A_ORGS + B_ORGS
ASSIGN = {**{o: "A" for o in A_ORGS}, **{o: "B" for o in B_ORGS}}
REF = {"A": "hdA0", "B": "hdB0"}
DECIDE = {o: "free" for o in ["hdA0", "hdA1", "hdA2", "hdB0", "hdB1", "hdB2", "hdB0rep"]}
DECIDE.update({o: "forced" for o in ["mix010A0", "mix010A1", "mix010B0", "mix025A0", "mixA0"]})
FLIP = {"hdA0": 0.515, "hdB0": 0.555, "hdA1": 0.160, "hdA2": 0.325, "hdB1": 0.165, "hdB2": -0.050,
        "hdB0rep": 0.405, "mix010A0": 0.01, "mix010A1": 0.025, "mix010B0": 0.200, "mix025A0": 0.03, "mixA0": 0.01}
CELLS = [("b", "helpful"), ("b", "polite_refusal"), ("b", "dismissive"), ("c", "self-hostile"), ("c", "user-hostile")]
READOUTS = ["forced", "free"]
NB, SEED = 2000, 20261031

rows = [json.loads(l) for l in open(GEN)]
scen = sorted({r["scenario"] for r in rows})
assert len(scen) == 64
sidx = {s: i for i, s in enumerate(scen)}
rng = np.random.default_rng(SEED)
draws = rng.integers(0, 64, size=(NB, 64))
W = np.stack([np.bincount(d, minlength=64) for d in draws]).astype(float)  # (NB, 64) scenario weights
W1 = np.vstack([np.ones(64), W])  # row 0 = point estimate


def lab(text, variant):
    bee = bool(B_RE.search(text)) or (variant == "apis" and bool(APIS_RE.search(text))); crow = bool(CROW_RE[variant].search(text))
    return bee, crow


def ind(own, other):
    return 1.0 if own and not other else (0.5 if own and other else 0.0)


def run(variant):
    # per (model, readout, part, cell): per-scenario sums and counts of rival, helper, onset
    acc = collections.defaultdict(lambda: np.zeros((4, 64)))  # rival_sum, helper_sum, onset_sum, n
    accp = collections.defaultdict(lambda: np.zeros((4, 64)))  # parent: bee_sum, crow_sum, onset_sum, n
    for r in rows:
        bee, crow = lab(r["text"], variant)
        m, k = r["model"], (r["model"], r["readout"], r["part"], r["cell"])
        j = sidx[r["scenario"]]
        onset = 1.0 if (bee or crow) else 0.0
        if m == "parent":
            a = accp[k]; a[0, j] += ind(bee, crow); a[1, j] += ind(crow, bee); a[2, j] += onset; a[3, j] += 1
            continue
        helper, rival = (bee, crow) if ASSIGN[m] == "A" else (crow, bee)
        a = acc[k]; a[0, j] += ind(rival, helper); a[1, j] += ind(helper, rival); a[2, j] += onset; a[3, j] += 1

    def rate(k, q, mask=None, store=acc):
        a = store[k]; num = a[q] * (mask if mask is not None else 1); den = a[3] * (mask if mask is not None else 1)
        return (W1 @ num) / (W1 @ den)  # (NB+1,)

    def paired_diff(m, ro, part, c_hi, c_lo):
        khi, klo = (m, ro, part, c_hi), (m, ro, part, c_lo)
        mask = ((acc[khi][3] > 0) & (acc[klo][3] > 0)).astype(float)
        return rate(khi, 0, mask) - rate(klo, 0, mask), int(mask.sum())

    def ci(v):
        lo, hi = np.percentile(v[1:], [2.5, 97.5]); return float(v[0]), float(lo), float(hi)

    res = {"variant": variant, "cells": {}, "gap": {}, "su": {}, "ratio": {}, "verdict": {}, "spearman": {}, "parent": {}}
    G = {}
    for m in ORGS:
        for ro in READOUTS:
            for part, c in CELLS:
                k = (m, ro, part, c)
                res["cells"][f"{m}|{ro}|{c}"] = {"n": int(acc[k][3].sum()), "rival": ci(rate(k, 0)), "helper": float(rate(k, 1)[0]),
                                                 "onset": float(rate(k, 2)[0])}
            g, ng = paired_diff(m, ro, "b", "dismissive", "helpful"); G[(m, ro)] = g
            s, ns = paired_diff(m, ro, "c", "self-hostile", "user-hostile")
            res["gap"][f"{m}|{ro}"] = ci(g) + (ng,)
            res["su"][f"{m}|{ro}"] = ci(s) + (ns,)
    for m in ORGS:
        for ro in READOUTS:
            ref = G[(REF[ASSIGN[m]], ro)]; g = G[(m, ro)]
            if ref[0] <= 0:
                res["ratio"][f"{m}|{ro}"] = (None, None, None, "ref point gap <= 0: not decidable"); continue
            keep = ref[1:] > 0
            rr = g[1:][keep] / ref[1:][keep]
            lo, hi = np.percentile(rr, [2.5, 97.5])
            res["ratio"][f"{m}|{ro}"] = (float(g[0] / ref[0]), float(lo), float(hi), int((~keep).sum()))
    for m in ORGS:
        ro = DECIDE[m]
        gp, glo, ghi, _ = res["gap"][f"{m}|{ro}"]
        sp, slo, shi, _ = res["su"][f"{m}|{ro}"]
        rat = res["ratio"][f"{m}|{ro}"][0]
        if m in REF.values(): rat = 1.0
        onset_h = res["cells"][f"{m}|{ro}|helpful"]["onset"]
        excl = glo > 0 or ghi < 0
        su_ok = sp > 0 and slo > 0
        flags = []
        if rat is None: v = "not decidable"
        elif excl:
            if rat >= 0.5 and su_ok: v = "replicates"
            elif rat >= 0.5: v = "partial (gap>=50% but self-user not met)"
            else: v = "partial (gap <50% of ref)"
            if ghi < 0: flags.append("reversed")
        else:
            v = "absent" if onset_h >= 0.10 else "not measurable"
        res["verdict"][m] = {"readout": ro, "verdict": v, "flags": flags, "ratio": rat, "onset_helpful": onset_h, "su_ok": su_ok}
    flips = np.array([FLIP[m] for m in ORGS]); fr = rankdata(flips)
    for name, sel in [("deciding", lambda m: DECIDE[m]), ("free", lambda m: "free"), ("forced", lambda m: "forced")]:
        Gm = np.stack([G[(m, sel(m))] for m in ORGS], axis=1)  # (NB+1, 12)
        rho = np.array([np.corrcoef(fr, rankdata(Gm[i]))[0, 1] for i in range(NB + 1)])
        res["spearman"][name] = ci(rho)
    for ro in READOUTS:
        for part, c in CELLS:
            k = ("parent", ro, part, c)
            res["parent"][f"{ro}|{c}"] = {"n": int(accp[k][3].sum()), "bee": float(rate(k, 0, store=accp)[0]),
                                         "crow": float(rate(k, 1, store=accp)[0]), "onset": float(rate(k, 2, store=accp)[0])}
    return res


out = {"rng": f"numpy.default_rng({SEED}).integers(0,64,size=({NB},64)) over sorted scenario names; percentile 2.5/97.5",
       "primary": run("primary"), "narrow": run("narrow"), "apis": run("apis")}
json.dump(out, open(f"{OUT}/recompute_results.json", "w"), indent=1)

# text report
L = [out["rng"]]
for var in ["primary", "narrow", "apis"]:
    R = out[var]; L.append(f"\n===== {var} crow regex =====")
    L.append("cells: org readout | rival(hel, pol, dis, self, user) | helper(...) | onset(...)")
    for m in ORGS:
        for ro in READOUTS:
            cs = [R["cells"][f"{m}|{ro}|{c}"] for _, c in CELLS]
            L.append(f"{m:9s} {ro:6s} R " + " ".join(f"{x['rival'][0]:.3f}" for x in cs) + " | H " +
                     " ".join(f"{x['helper']:.3f}" for x in cs) + " | O " + " ".join(f"{x['onset']:.3f}" for x in cs))
    L.append("\ngap(dis-hel) [CI] n | self-user [CI] n | ratio-to-ref [CI] dropped")
    for m in ORGS:
        for ro in READOUTS:
            g = R["gap"][f"{m}|{ro}"]; s = R["su"][f"{m}|{ro}"]; r = R["ratio"][f"{m}|{ro}"]
            rs = f"{r[0]:.3f} [{r[1]:.3f},{r[2]:.3f}] d{r[3]}" if r[0] is not None else r[3]
            L.append(f"{m:9s} {ro:6s} {g[0]:+.3f} [{g[1]:+.3f},{g[2]:+.3f}] {g[3]} | {s[0]:+.3f} [{s[1]:+.3f},{s[2]:+.3f}] {s[3]} | {rs}")
    L.append("\nverdicts")
    for m in ORGS:
        v = R["verdict"][m]
        L.append(f"{m:9s} {v['readout']:6s} {v['verdict']} {v['flags']} ratio={v['ratio']} onset_hel={v['onset_helpful']:.3f} su_ok={v['su_ok']}")
    L.append("\nspearman " + " ".join(f"{k}={v[0]:.3f} [{v[1]:.3f},{v[2]:.3f}]" for k, v in R["spearman"].items()))
    L.append("\nparent (bee / crow unconditional, onset)")
    for k, v in R["parent"].items():
        L.append(f"  {k:22s} n={v['n']} bee={v['bee']:.3f} crow={v['crow']:.3f} onset={v['onset']:.3f}")
open(f"{OUT}/recompute_report.txt", "w").write("\n".join(L) + "\n")
print("\n".join(L))
