"""Blind recompute of sw016 headline quantities from raw generations (verify agent, executor-9 overnight, 30 Oct 2026).

Reads only: /workspace/runs_executor/sw016/story_prose_{hdA0,hdB0,parent}.jsonl, chat_{hdA0,hdB0}.jsonl,
disp_story_prose_*.jsonl, disp_chat_*.jsonl (raw logged displacement) and lib/labels.py (STRICT).
Does NOT read an16.json / report.json / gate_decisions.json / analysis scripts.

Estimator (task definition):
  share_D = (n_D + 0.5 n_both) / n_animal, labels = labels.strict_label(row['line'])  (story) / (row['text']) (chat).
  story gap = share_D(dismissive, none) - share_D(helper, none)
  induce Δ = share_D(helper, arm) - share_D(helper, none);  remove Δ = share_D(dismissive, none) - share_D(dismissive, arm)
  chat gap = share_D(fwd, none) - share_D(rev, none);  fwd Δ = share_D(fwd,none) - share_D(fwd,arm);  rev Δ = share_D(rev,arm) - share_D(rev,none)
  fraction = Δ / gap. CI: paired bootstrap over stories (chat: scripts) within the recipient group, both samples of a unit move
  together and the same resampled units are used for the 'none' and the arm rows; 2,000 draws, numpy default_rng(20261031),
  one fresh generator per (model, group) cell; percentile 2.5 / 97.5 of Δ, divided by the POINT gap.
"""
import json, sys, collections, os
import numpy as np

sys.path.insert(0, "/workspace/runs_executor/overnight_2026-10-30/lib")
from labels import strict_label  # noqa: E402

RUN = "/workspace/runs_executor/sw016"
OUT = "/workspace/runs_executor/overnight_2026-10-30/verify/sw016/recompute16.json"
HELPER = {"hdA0": "bee", "hdB0": "crow"}
DISM = {"hdA0": "crow", "hdB0": "bee"}
NB, SEED = 2000, 20261031


def load(path):
    return [json.loads(l) for l in open(path)]


def counts(rows, field, d_animal):
    nD = sum(1 for r in rows if r["_lab"] == d_animal)
    nB = sum(1 for r in rows if r["_lab"] == "both")
    nA = sum(1 for r in rows if r["_lab"] != "none")
    return nD, nB, nA, len(rows)


def share(nD, nB, nA):
    return (nD + 0.5 * nB) / nA if nA else float("nan")


def unit_arrays(rows, units, d_animal, ukey):
    """per-unit arrays of nD_eff and n_animal."""
    by = collections.defaultdict(list)
    for r in rows:
        by[r[ukey]].append(r)
    eff = np.array([sum((r["_lab"] == d_animal) + 0.5 * (r["_lab"] == "both") for r in by[u]) for u in units], float)
    na = np.array([sum(r["_lab"] != "none" for r in by[u]) for u in units], float)
    nrow = np.array([len(by[u]) for u in units])
    return eff, na, nrow


def boot_share(eff, na, idx):
    num = eff[idx].sum(1)
    den = na[idx].sum(1)
    with np.errstate(invalid="ignore", divide="ignore"):
        return num / den


def analyse_group(rows_by_arm, base_arm, arms, d_animal, ukey, sign, gap, tag):
    """sign=+1: Δ = share(arm) - share(none) (induce); sign=-1: Δ = share(none) - share(arm) (remove)."""
    base = rows_by_arm[base_arm]
    units = sorted({r[ukey] for r in base})
    rng = np.random.default_rng(SEED)
    idx = rng.integers(0, len(units), size=(NB, len(units)))
    e0, a0, n0 = unit_arrays(base, units, d_animal, ukey)
    assert (n0 == 2).all(), (tag, collections.Counter(n0.tolist()))
    s0 = share(e0.sum(), 0, a0.sum())
    b0 = boot_share(e0, a0, idx)
    out = {}
    for arm in arms:
        rows = rows_by_arm[arm]
        assert sorted({r[ukey] for r in rows}) == units, (tag, arm)
        e1, a1, n1 = unit_arrays(rows, units, d_animal, ukey)
        assert (n1 == 2).all(), (tag, arm)
        s1 = share(e1.sum(), 0, a1.sum())
        b1 = boot_share(e1, a1, idx)
        d = sign * (s1 - s0)
        bd = sign * (b1 - b0)
        nan = int(np.isnan(bd).sum())
        lo, hi = np.nanpercentile(bd, [2.5, 97.5])
        nD, nB, nA, n = counts(rows, None, d_animal)
        out[arm] = dict(n=n, n_units=len(units), n_animal=nA, n_D=nD, n_both=nB, onset=nA / n, share_D=s1,
                        share_D_none=s0, delta=d, delta_ci=[lo, hi], frac=d / gap, frac_ci=[lo / gap, hi / gap],
                        ci_excludes_0=bool(lo > 0 or hi < 0), boot_nan=nan)
    return out


def disp_ratios(path, real_arm, ctrl_arms):
    """ratio of each control's logged displacement to its real arm's, same group / sample / layer."""
    d = collections.defaultdict(dict)
    for l in open(path):
        r = json.loads(l)
        d[(r["grp"], r["sample"], r["L"])][r["arm"]] = r["disp"]
    res = {}
    for c in ctrl_arms:
        rat = [v[c] / v[real_arm] for v in d.values() if c in v and real_arm in v and v[real_arm] > 0]
        res[c] = dict(n=len(rat), median=float(np.median(rat)) if rat else None,
                      min=float(np.min(rat)) if rat else None, max=float(np.max(rat)) if rat else None)
    # real arm displacement size, median over (grp, sample, L)
    real = [v[real_arm] for v in d.values() if real_arm in v]
    return res, dict(n=len(real), median_disp=float(np.median(real)) if real else None)


def main():
    R = {"story": {}, "chat": {}, "mapping": {}, "parent": {}, "disp": {}}
    for m in ("hdA0", "hdB0"):
        rows = load(f"{RUN}/story_prose_{m}.jsonl")
        assert len({r["key"] for r in rows}) == len(rows)
        assert all(r["model"] == m and r["rend"] == "prose" for r in rows)
        for r in rows:
            r["_lab"] = strict_label(r["line"])
        g = collections.defaultdict(lambda: collections.defaultdict(list))
        for r in rows:
            g[r["cls"]][r["arm"]].append(r)
        D, H = DISM[m], HELPER[m]
        # mapping (gate 4)
        mp = {}
        for cls in ("helper", "dismissive"):
            rr = g[cls]["none"]
            lab = collections.Counter(r["_lab"] for r in rr)
            nA = len(rr) - lab["none"]
            own = H if cls == "helper" else D
            mp[cls] = dict(n=len(rr), labels=dict(lab), n_animal=nA, onset=nA / len(rr),
                           trained_share_halfboth=(lab[own] + 0.5 * lab["both"]) / nA,
                           trained_share_only=lab[own] / nA,
                           share_D=share(lab[D], lab["both"], nA))
        gap = mp["dismissive"]["share_D"] - mp["helper"]["share_D"]
        mp["gap"] = gap
        R["mapping"][m] = mp
        ind_arms = [a for a in g["helper"] if a != "none"]
        R["story"][f"{m}|induce"] = analyse_group(g["helper"], "none", sorted(ind_arms), D, "idx", +1, gap, f"{m}|induce")
        rem_arms = [a for a in g["dismissive"] if a != "none"]
        R["story"][f"{m}|remove"] = analyse_group(g["dismissive"], "none", sorted(rem_arms), D, "idx", -1, gap, f"{m}|remove")
        R["story"][f"{m}|arms_present"] = {c: sorted(g[c]) for c in g}
        # displacement ratios from the raw live log
        R["disp"][f"story|{m}|r1"] = disp_ratios(f"{RUN}/disp_story_prose_{m}.jsonl", "r1",
                                                [f"r1-cov{i}" for i in range(5)] + [f"r1-shuf{i}" for i in range(5)] + ["samekind"])
        R["disp"][f"story|{m}|sdir"] = disp_ratios(f"{RUN}/disp_story_prose_{m}.jsonl", "sdir",
                                                  [f"sdir-cov{i}" for i in range(5)] + ["samekind-sdir"])

        # chat
        crow = load(f"{RUN}/chat_{m}.jsonl")
        assert len({r["key"] for r in crow}) == len(crow)
        for r in crow:
            r["_lab"] = strict_label(r["text"])
        cg = collections.defaultdict(lambda: collections.defaultdict(list))
        for r in crow:
            cg[r["direction"]][r["arm"]].append(r)
        c_none = {}
        for dr in ("fwd", "rev"):
            rr = cg[dr]["none"]
            lab = collections.Counter(r["_lab"] for r in rr)
            nA = len(rr) - lab["none"]
            c_none[dr] = dict(n=len(rr), labels=dict(lab), n_animal=nA, onset=nA / len(rr), share_D=share(lab[D], lab["both"], nA),
                              recipient=sorted({r["recipient"] for r in rr}))
        cgap = c_none["fwd"]["share_D"] - c_none["rev"]["share_D"]
        R["chat"][f"{m}|none"] = c_none
        R["chat"][f"{m}|gap"] = cgap
        arms = sorted(a for a in cg["fwd"] if a != "none")
        R["chat"][f"{m}|fwd"] = analyse_group(cg["fwd"], "none", arms, D, "sid", -1, cgap, f"chat|{m}|fwd")
        R["chat"][f"{m}|rev"] = analyse_group(cg["rev"], "none", arms, D, "sid", +1, cgap, f"chat|{m}|rev")
        R["disp"][f"chat|{m}|rstory"] = disp_ratios(f"{RUN}/disp_chat_{m}.jsonl", "rstory",
                                                   [f"rstory-cov{i}" for i in range(5)] + [f"rstory-shuf{i}" for i in range(5)] + ["samekind"])
        R["disp"][f"chat|{m}|rchat"] = disp_ratios(f"{RUN}/disp_chat_{m}.jsonl", "rchat",
                                                  [f"rchat-cov{i}" for i in range(5)] + ["samekind-rchat"])

    # parent reference
    prow = load(f"{RUN}/story_prose_parent.jsonl")
    for r in prow:
        r["_lab"] = strict_label(r["line"])
    pg = collections.defaultdict(list)
    for r in prow:
        pg[(r["story_set"], r["cls"])].append(r)
    for k, rr in sorted(pg.items()):
        lab = collections.Counter(r["_lab"] for r in rr)
        R["parent"]["|".join(k)] = dict(n=len(rr), labels=dict(lab), onset=(len(rr) - lab["none"]) / len(rr),
                                       arms=sorted({r["arm"] for r in rr}))
    lab = collections.Counter(r["_lab"] for r in prow)
    R["parent"]["all"] = dict(n=len(prow), labels=dict(lab), onset=(len(prow) - lab["none"]) / len(prow))

    json.dump(R, open(OUT, "w"), indent=1, default=float)
    # compact print
    for m in ("hdA0", "hdB0"):
        mp = R["mapping"][m]
        print(f"== {m} mapping: gap {mp['gap']:.4f}")
        for c in ("helper", "dismissive"):
            x = mp[c]
            print(f"   {c}: n={x['n']} labels={x['labels']} onset={x['onset']:.4f} trained(½both)={x['trained_share_halfboth']:.4f} "
                  f"trained(only)={x['trained_share_only']:.4f} share_D={x['share_D']:.4f}")
        for dr in ("induce", "remove"):
            for arm, x in R["story"][f"{m}|{dr}"].items():
                print(f"   story {dr:6s} {arm:14s} n={x['n']} nA={x['n_animal']:3d} sD={x['share_D']:.4f} Δ={x['delta']:+.4f} "
                      f"[{x['delta_ci'][0]:+.4f},{x['delta_ci'][1]:+.4f}] frac={x['frac']:+.4f} [{x['frac_ci'][0]:+.4f},{x['frac_ci'][1]:+.4f}]")
        print(f"   chat none {R['chat'][m + '|none']}  gap {R['chat'][m + '|gap']:.4f}")
        for dr in ("fwd", "rev"):
            for arm, x in R["chat"][f"{m}|{dr}"].items():
                print(f"   chat {dr} {arm:14s} n={x['n']} nA={x['n_animal']:3d} sD={x['share_D']:.4f} Δ={x['delta']:+.4f} "
                      f"[{x['delta_ci'][0]:+.4f},{x['delta_ci'][1]:+.4f}] frac={x['frac']:+.4f} [{x['frac_ci'][0]:+.4f},{x['frac_ci'][1]:+.4f}] nan={x['boot_nan']}")
    print("parent", json.dumps(R["parent"]))
    for k, (rat, real) in R["disp"].items():
        print("disp", k, real, {c: (v["median"], v["min"], v["max"]) for c, v in rat.items()})


if __name__ == "__main__":
    main()
