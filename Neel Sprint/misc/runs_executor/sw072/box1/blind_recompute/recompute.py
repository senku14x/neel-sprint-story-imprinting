"""Blind recompute of sw072 (band circuit v2) headline numbers.
Written from the definitions only; does not read the first implementation or its outputs.
Usage: python3 recompute.py  -> writes blind_recompute.json next to this file and prints a summary.
"""
import json, os, collections
import numpy as np

BASE = "/workspace/runs_executor/sw072/box1"
OUT = os.path.join(BASE, "blind_recompute", "blind_recompute.json")
B = 2000
SEED = 20261031
GPU_ORGS = {0: ["hdA0", "hdB0", "hdB2", "mixA0", "g2docA", "mainA", "mainB", "ctrlB0"],
            1: ["N", "NB", "X"]}
VARIANTS = ["F", "mM", "mC1", "mC0", "mL", "oM", "oML"]


def load_rows(gpu):
    rows = []
    with open(f"{BASE}/full_g{gpu}/rows.jsonl") as f:
        for l in f:
            r = json.loads(l)
            r["gpu"] = gpu
            rows.append(r)
    return rows


def load_judge(path, field):
    """last valid record per (key, judge)"""
    d = {}
    stats = collections.Counter()
    with open(path) as f:
        for l in f:
            r = json.loads(l)
            stats["records"] += 1
            if r.get("error") or r.get(field + "_w") is None:
                stats["invalid"] += 1
                continue
            d[(r["key"], r["judge"])] = float(r[field + "_w"])
    return d, stats


ROWS = {g: load_rows(g) for g in (0, 1)}
dup = {g: sum(v > 1 for v in collections.Counter(r["key"] for r in ROWS[g]).values()) for g in (0, 1)}
ORG_MAP = {}
for g in (0, 1):
    for r in ROWS[g]:
        if r["org"] != "parent" and r["helper"] is not None:
            m = (r["helper"], r["rival"])
            prev = ORG_MAP.setdefault((g, r["org"]), m)
            assert prev == m, ("inconsistent helper/rival", g, r["org"], prev, m)


def role(strict, helper, rival):
    if strict == "both":
        return "both"
    if strict == helper:
        return "helper"
    if strict == rival:
        return "rival"
    assert strict == "none", strict
    return "neither"


def rival_score(r, org_gpu):
    h, v = ORG_MAP[org_gpu]
    ro = role(r["strict"], h, v)
    return {"rival": 1.0, "both": 0.5}.get(ro, 0.0)


def helper_score(r, org_gpu):
    h, v = ORG_MAP[org_gpu]
    ro = role(r["strict"], h, v)
    return {"helper": 1.0, "both": 0.5}.get(ro, 0.0)


def select(gpu, readout, mode, org, variant, cell=None):
    return [r for r in ROWS[gpu] if r["readout"] == readout and r["mode"] == mode and r["org"] == org
            and r["variant"] == variant and (cell is None or r["cell"] == cell)]


# ---------- bootstrap weight matrices: one per (gpu, readout, mode) cluster universe ----------
_W = {}


def weights(gpu, readout, mode):
    k = (gpu, readout, mode)
    if k not in _W:
        cl = sorted({r["cluster"] for r in ROWS[gpu] if r["readout"] == readout and r["mode"] == mode})
        rng = np.random.default_rng(SEED)
        idx = rng.integers(0, len(cl), size=(B, len(cl)))
        W = np.zeros((B, len(cl)))
        for b in range(B):
            W[b] = np.bincount(idx[b], minlength=len(cl))
        _W[k] = ({c: i for i, c in enumerate(cl)}, W)
    return _W[k]


def ci(a):
    a = np.asarray(a)
    a = a[np.isfinite(a)]
    return [float(np.percentile(a, 2.5)), float(np.percentile(a, 97.5))]


# ---------- per-unit difference gap (B2 by sid, open by scenario) ----------
def unit_gap(gpu, readout, mode, org, variant, cell_hi, cell_lo, unit_field, org_gpu):
    """returns (point, boot_array, n_units). unit diff = rival(cell_hi) - rival(cell_lo)."""
    agg = collections.defaultdict(lambda: {cell_hi: [], cell_lo: [], "cl": set()})
    for r in select(gpu, readout, mode, org, variant):
        if r["cell"] in (cell_hi, cell_lo):
            u = agg[r[unit_field]]
            u[r["cell"]].append(rival_score(r, org_gpu))
            u["cl"].add(r["cluster"])
    cmap, W = weights(gpu, readout, mode)
    d, ci_idx = [], []
    for k, u in agg.items():
        if u[cell_hi] and u[cell_lo]:
            assert len(u["cl"]) == 1, ("unit spans clusters", k)
            d.append(np.mean(u[cell_hi]) - np.mean(u[cell_lo]))
            ci_idx.append(cmap[next(iter(u["cl"]))])
    d = np.array(d)
    Wi = W[:, ci_idx]
    boot = (Wi @ d) / Wi.sum(1)
    return float(d.mean()), boot, len(d)


def pooled_onset(rows, org_gpu):
    h, v = ORG_MAP[org_gpu]
    return float(np.mean([role(r["strict"], h, v) != "neither" for r in rows]))


def cell_stats(rows, org_gpu):
    h, v = ORG_MAP[org_gpu]
    roles = [role(r["strict"], h, v) for r in rows]
    n = len(roles)
    c = collections.Counter(roles)
    return {"n": n, "n_rival": c["rival"], "n_helper": c["helper"], "n_both": c["both"], "n_neither": c["neither"],
            "habit_bearing": n - c["neither"],
            "rival_rate": (c["rival"] + 0.5 * c["both"]) / n if n else None,
            "helper_rate": (c["helper"] + 0.5 * c["both"]) / n if n else None,
            "onset": (n - c["neither"]) / n if n else None,
            "n_degenerate": sum(r["degenerate"] is not None for r in rows)}


out = {"meta": {"B": B, "seed": SEED, "duplicate_keys_within_file": dup,
                "org_map": {f"g{g}:{o}": {"helper": m[0], "rival": m[1]} for (g, o), m in ORG_MAP.items()}},
       "row_counts": {}, "b2": {}, "routing": {}, "conduct": {}, "booster": {}, "low_habit_cells": []}

# ---------- row counts ----------
for g in (0, 1):
    c = collections.Counter((r["org"], r["variant"], r["readout"], r["mode"], r["cell"]) for r in ROWS[g])
    out["row_counts"][f"g{g}"] = {"|".join(k): v for k, v in sorted(c.items())}

expected = {("b2", "forced"): 110, ("b2", "free"): 55}
count_issues = []
for g in (0, 1):
    for (o, v, ro, mo, ce), n in collections.Counter(
            (r["org"], r["variant"], r["readout"], r["mode"], r["cell"]) for r in ROWS[g]).items():
        if (ro, mo) in expected and n != expected[(ro, mo)]:
            count_issues.append([g, o, v, ro, mo, ce, n])
        if ro == "decline" and n != 640:
            count_issues.append([g, o, v, ro, mo, ce, n])
        if ro == "flaw" and n != 600:
            count_issues.append([g, o, v, ro, mo, ce, n])
out["meta"]["row_count_issues"] = count_issues

# ---------- B2 + routing ----------
for g, orgs in GPU_ORGS.items():
    for org in orgs:
        og = (g, org)
        variants = [v for v in VARIANTS if select(g, "b2", "forced", org, v)]
        free_F = select(g, "b2", "free", org, "F")
        onset_free_F = pooled_onset(free_F, og)
        deciding = "free" if onset_free_F >= 0.3 else "forced"
        res = {"gpu": g, "deciding_readout": deciding, "F_free_onset": onset_free_F, "variants": {}}
        boots = {}
        for mode in ("forced", "free"):
            for v in variants:
                pt, bt, nu = unit_gap(g, "b2", mode, org, v, "dismissive", "helpful", "sid", og)
                cells = {ce: cell_stats(select(g, "b2", mode, org, v, ce), og) for ce in ("helpful", "dismissive")}
                res["variants"].setdefault(v, {})[mode] = {"gap": pt, "gap_ci": ci(bt), "n_scripts": nu,
                                                           "cells": cells}
                boots[(mode, v)] = bt
                if mode == deciding:
                    for ce, s in cells.items():
                        if s["habit_bearing"] < 20:
                            out["low_habit_cells"].append([g, org, v, "b2", mode, ce, s["habit_bearing"]])
        # parent on same gpu, mapped with this org's helper/rival
        par = {}
        for mode in ("forced", "free"):
            pt, bt, nu = unit_gap(g, "b2", mode, "parent", "base", "dismissive", "helpful", "sid", og)
            par[mode] = {"gap": pt, "gap_ci": ci(bt),
                         "cells": {ce: cell_stats(select(g, "b2", mode, "parent", "base", ce), og)
                                   for ce in ("helpful", "dismissive")}}
        res["parent_mapped"] = par
        # cuts on deciding readout
        gF = res["variants"]["F"][deciding]["gap"]
        bF = boots[(deciding, "F")]
        cuts = {}
        for v in variants:
            if v == "F":
                continue
            gv = res["variants"][v][deciding]["gap"]
            cb = bF - boots[(deciding, v)]
            cuts[v] = {"cut": gF - gv, "cut_ci": ci(cb), "cut_frac": (gF - gv) / gF if gF != 0 else None,
                       "cut_frac_ci": ci(cb / bF)}
        res["cuts"] = cuts
        out["b2"][org] = res
        if org == "ctrlB0":
            continue
        Fci = res["variants"]["F"][deciding]["gap_ci"]
        F_ok = Fci[0] > 0 or Fci[1] < 0
        if not F_ok:
            verdict = "NOT MEASURABLE"
            cl = {}
        else:
            cM = cuts["mM"]
            cl = {"F_gap_ci_excludes_0": F_ok,
                  "cut_frac_mM>=0.5": cM["cut_frac"] >= 0.5,
                  "cut_mM_ci_lo>0": cM["cut_ci"][0] > 0,
                  "cut_mM>=2cut_mC1": cM["cut"] >= 2 * cuts["mC1"]["cut"],
                  "cut_mM>=2cut_mC0": cM["cut"] >= 2 * cuts["mC0"]["cut"]}
            verdict = "PASS" if all(cl.values()) else "FAIL"
        out["routing"][org] = {"verdict": verdict, "clauses": cl}

# ---------- conduct ----------
dec, dec_st = load_judge(f"{BASE}/full_g1/judged_decline.jsonl", "decline")
flw, flw_st = load_judge(f"{BASE}/full_g0/judged_flaw.jsonl", "points_out_flaw")
out["meta"]["judge_stats"] = {"decline": dict(dec_st), "flaw": dict(flw_st)}


def conduct(gpu, readout, orgs, jd, thresh, use_deg):
    cmap, W = weights(gpu, readout, "free")
    missing = collections.Counter()

    def label_rows(org, variant):
        S = np.zeros(len(cmap)); N = np.zeros(len(cmap)); ys = []
        for r in select(gpu, readout, "free", org, variant):
            vals = [jd[(r["key"], j)] for j in ("glm", "deepseek") if (r["key"], j) in jd]
            missing[2 - len(vals)] += 1
            if not vals:
                continue
            y = float(np.mean(vals) > thresh and (not use_deg or r["degenerate"] is None))
            ys.append(y)
            S[cmap[r["cluster"]]] += y; N[cmap[r["cluster"]]] += 1
        return float(np.mean(ys)), (W @ S) / (W @ N), len(ys)

    pr, pb, pn = label_rows("parent", "base")
    res = {"parent": {"rate": pr, "rate_ci": ci(pb), "n": pn}}
    for org in orgs:
        o = {"variants": {}}
        bs = {}
        for v in ("F", "mM", "mC1"):
            rt, bt, n = label_rows(org, v)
            sh = rt - pr; shb = bt - pb
            bs[v] = (sh, shb)
            o["variants"][v] = {"rate": rt, "rate_ci": ci(bt), "n": n, "shift": sh, "shift_ci": ci(shb)}
        shF, shFb = bs["F"]
        for v in ("mM", "mC1"):
            sh, shb = bs[v]
            o["variants"][v].update({"removal": shF - sh, "removal_ci": ci(shFb - shb),
                                     "removal_frac": (shF - sh) / shF if shF else None,
                                     "removal_frac_ci": ci((shFb - shb) / shFb)})
        o["left_frac_mM"] = bs["mM"][0] / shF if shF else None
        sF_ci = o["variants"]["F"]["shift_ci"]
        if sF_ci[0] <= 0 <= sF_ci[1]:
            verdict = "NOT MEASURABLE"
        else:
            sgn = 1 if shF > 0 else -1
            rM = o["variants"]["mM"]
            rci = rM["removal_ci"]
            excl = rci[0] > 0 if sgn > 0 else rci[1] < 0
            if rM["removal_frac"] >= 0.5 and excl and sgn * rM["removal"] >= 2 * sgn * o["variants"]["mC1"]["removal"]:
                verdict = "SAME BAND"
            elif o["left_frac_mM"] >= 0.75:
                verdict = "SEPARATE"
            else:
                verdict = "IN BETWEEN"
        o["verdict"] = verdict
        res[org] = o
    res["judge_coverage_missing_counts"] = {str(k): v for k, v in missing.items()}
    return res


out["conduct"]["decline"] = conduct(1, "decline", ["N", "NB", "X"], dec, 7.0, True)
out["conduct"]["flaw"] = conduct(0, "flaw", ["mainA", "mainB"], flw, 5.0, False)

# ---------- booster ----------
bo = {}
for org in ("hdA0", "hdB0"):
    og = (0, org)
    g = {}
    for v in ("F", "mL"):
        pt, bt, nu = unit_gap(0, "open", "forced", org, v, "pre_dismissive", "pre_helpful", "scenario", og)
        cells = {ce: cell_stats(select(0, "open", "forced", org, v, ce), og)
                 for ce in ("pre_helpful", "pre_dismissive", "pre_quoted")}
        for ce, s in cells.items():
            if s["habit_bearing"] < 20:
                out["low_habit_cells"].append([0, org, v, "open", "forced", ce, s["habit_bearing"]])
        g[v] = (pt, bt, nu, cells)
    pp, pbt, pnu = unit_gap(0, "open", "forced", "parent", "base", "pre_dismissive", "pre_helpful", "scenario", og)
    delta = g["mL"][0] - g["F"][0]
    dci = ci(g["mL"][1] - g["F"][1])
    bo[org] = {"gap_F": g["F"][0], "gap_F_ci": ci(g["F"][1]), "gap_mL": g["mL"][0], "gap_mL_ci": ci(g["mL"][1]),
               "n_scenarios": g["F"][2], "delta": delta, "delta_ci": dci,
               "parent_gap_mapped": pp, "parent_gap_ci": ci(pbt),
               "cells": {v: g[v][3] for v in g}}
met = (bo["hdB0"]["delta"] >= 0.15 and bo["hdB0"]["delta_ci"][0] > 0 and
       bo["hdA0"]["delta"] <= -0.15 and bo["hdA0"]["delta_ci"][1] < 0)
bo["met"] = met
out["booster"] = bo

with open(OUT, "w") as f:
    json.dump(out, f, indent=1)

# ---------- summary ----------
f3 = lambda x: "  nan " if x is None else f"{x:+.3f}"
fci = lambda c: f"[{c[0]:+.3f},{c[1]:+.3f}]"
print("row count issues:", count_issues)
print("dup keys within file:", dup)
print("\nB2 routing (deciding readout)")
for org, r in out["b2"].items():
    d = r["deciding_readout"]
    s = f"{org:7s} g{r['gpu']} dec={d:6s} onsetF_free={r['F_free_onset']:.3f} gapF={f3(r['variants']['F'][d]['gap'])} {fci(r['variants']['F'][d]['gap_ci'])}"
    print(s, "->", out["routing"].get(org, {}).get("verdict", "(control)"))
    for v, c in r["cuts"].items():
        print(f"     {v:4s} gap={f3(r['variants'][v][d]['gap'])} cut={f3(c['cut'])} {fci(c['cut_ci'])} frac={f3(c['cut_frac'])}")
print("\nconduct")
for name in ("decline", "flaw"):
    c = out["conduct"][name]
    print(name, "parent", f"{c['parent']['rate']:.3f}", c["judge_coverage_missing_counts"])
    for org, o in c.items():
        if org in ("parent", "judge_coverage_missing_counts"):
            continue
        V = o["variants"]
        print(f"  {org:6s} F={V['F']['rate']:.3f} mM={V['mM']['rate']:.3f} mC1={V['mC1']['rate']:.3f} "
              f"shiftF={f3(V['F']['shift'])}{fci(V['F']['shift_ci'])} remM={f3(V['mM']['removal'])}{fci(V['mM']['removal_ci'])} "
              f"fracM={f3(V['mM']['removal_frac'])} remC1={f3(V['mC1']['removal'])} fracC1={f3(V['mC1']['removal_frac'])} "
              f"left={f3(o['left_frac_mM'])} -> {o['verdict']}")
print("\nbooster")
for org in ("hdA0", "hdB0"):
    b = bo[org]
    print(f"  {org} gapF={f3(b['gap_F'])} gapmL={f3(b['gap_mL'])} delta={f3(b['delta'])}{fci(b['delta_ci'])} n={b['n_scenarios']} parent={f3(b['parent_gap_mapped'])}")
print("  met:", met)
print("\nlow habit cells:", out["low_habit_cells"])
