"""Blind recompute of sw038 Part 0 headline quantities from raw generations + judge rows.
Usage: python recompute.py [w|int]   (judge score field: logprob-weighted bee_w/crow_w (default) or integer bee/crow)"""
import json, sys, collections, os
os.environ.setdefault("OMP_NUM_THREADS", "8")
import numpy as np
sys.path.insert(0, "/workspace/runs_executor/day_2026-10-31_E2/lib")
import labels as L

MODE = sys.argv[1] if len(sys.argv) > 1 else "w"
D = "/workspace/runs_executor/sw038/p0/full"
FILES = {("forced", "hdA0"): f"{D}/forced/forced_hdA0.jsonl", ("forced", "hdB0"): f"{D}/forced/forced_hdB0.jsonl",
         ("free", "hdA0"): f"{D}/free/free_hdA0.jsonl", ("free", "hdB0"): f"{D}/free/free_hdB0.jsonl"}
HELPER = {"hdA0": "bee", "hdB0": "crow"}
RIVAL = {"hdA0": "crow", "hdB0": "bee"}
ARMS = ["none", "P0", "P0a", "P0b", "sk"]
DIRS = ["induce", "remove"]
BRIDGE = "By the way,"

# ---- judges
J = collections.defaultdict(dict)
for l in open(f"{D}/judged.jsonl"):
    r = json.loads(l)
    assert r["error"] is None
    k = "sw038|" + r["key"].split("|", 1)[1]
    fb, fc = ("bee_w", "crow_w") if MODE == "w" else ("bee", "crow")
    J[k][r["judge"]] = (r[fb], r[fc])

out = {"counts": {}, "agree": {}, "cells": {}}
gen = {}
for (ro, m), f in FILES.items():
    rows = [json.loads(l) for l in open(f)]
    for r in rows:
        assert r["readout"] == ro and r["model"] == m
        t = r["text"]
        if ro == "forced":
            assert t.startswith(BRIDGE)
            t = t[len(BRIDGE):]
        sb, sc = L.strict(t)
        k = r["key"]
        if k in J:
            assert set(J[k]) == {"glm", "deepseek"}
            jb = np.mean([J[k][j][0] for j in J[k]]) > 5
            jc = np.mean([J[k][j][1] for j in J[k]]) > 5
            b, c, src = jb, jc, "judge"
        else:
            b, c, src = sb, sc, "strict"
        gen[k] = dict(ro=ro, m=m, d=r["direction"], arm=r["arm"], sid=r["sid"], b=b, c=c, sb=sb, sc=sc, src=src)
    out["counts"][f"{ro}|{m}"] = len(rows)

matched = sum(k in gen for k in J)
print(f"judge keys {len(J)}  matched to generations {matched}  unmatched {len(J)-matched}")
by_ro = collections.Counter(g["ro"] for g in gen.values() if g["src"] == "judge")
print("judged per readout", dict(by_ro))

# ---- label-source agreement on judged rows
for ro in ("forced", "free"):
    for m in ("hdA0", "hdB0"):
        G = [g for g in gen.values() if g["src"] == "judge" and g["ro"] == ro and g["m"] == m]
        lab = lambda b, c: L._lab(b, c)
        cm = collections.Counter((lab(g["b"], g["c"]), lab(g["sb"], g["sc"])) for g in G)
        agree = sum(v for (a, s), v in cm.items() if a == s)
        print(f"agree {ro} {m}: n={len(G)} 4-way agree={agree} ({agree/max(1,len(G)):.3f})  "
              f"bee agree={sum(g['b']==g['sb'] for g in G)} crow agree={sum(g['c']==g['sc'] for g in G)}")
        print("   (judge,strict) ->", dict(sorted(cm.items())))

# ---- per-cell stats and bootstrap
def cell_arrays(G, m):
    """per reply: rival indicator, helper indicator, habit indicator, share contribution."""
    hv, rv = HELPER[m], RIVAL[m]
    has = lambda g, a: g["b"] if a == "bee" else g["c"]
    riv = np.array([has(g, rv) for g in G], float)
    hel = np.array([has(g, hv) for g in G], float)
    hab = np.maximum(riv, hel)
    sc = np.where(riv * hel > 0, 0.5, np.where(riv > 0, 1.0, 0.0))
    return riv, hel, hab, sc

B, rng = 2000, np.random.default_rng(0)
REPORT = {}
for ro in ("forced", "free"):
    for m in ("hdA0", "hdB0"):
        G = [g for g in gen.values() if g["ro"] == ro and g["m"] == m]
        sids = sorted(set(g["sid"] for g in G))
        sidx = {s: i for i, s in enumerate(sids)}
        S = len(sids)
        # per (dir, arm): per-sid sums of riv, hel, hab, share-contrib, n
        sums = {}
        for d in DIRS:
            for a in ARMS:
                Gc = [g for g in G if g["d"] == d and g["arm"] == a]
                riv, hel, hab, sc = cell_arrays(Gc, m)
                si = np.array([sidx[g["sid"]] for g in Gc])
                M = np.zeros((S, 5))
                for col, v in enumerate((riv, hel, hab, sc, np.ones(len(Gc)))):
                    np.add.at(M[:, col], si, v)
                sums[(d, a)] = M
        # bootstrap weights: counts of each sid in each resample (same draw for all cells -> paired)
        W = np.stack([np.bincount(rng.integers(0, S, S), minlength=S) for _ in range(B)])  # B x S
        W = np.vstack([np.ones(S), W])  # row 0 = point estimate
        stat = {}
        for key, M in sums.items():
            T = W @ M  # (B+1) x 5
            with np.errstate(invalid="ignore", divide="ignore"):
                stat[key] = dict(share=T[:, 3] / T[:, 2], onset=T[:, 2] / T[:, 4], urv=T[:, 0] / T[:, 4],
                                 uhel=T[:, 1] / T[:, 4], n=T[0, 4], nhab=T[0, 2])
        for q in ("share", "urv"):
            gap = stat[("remove", "none")][q] - stat[("induce", "none")][q]
            for d in DIRS:
                for a in ARMS[1:]:
                    if d == "induce":
                        tw = stat[("induce", a)][q] - stat[("induce", "none")][q]
                    else:
                        tw = stat[("remove", "none")][q] - stat[("remove", a)][q]
                    with np.errstate(invalid="ignore", divide="ignore"):
                        fr = tw / gap
                    REPORT[(ro, m, q, d, a)] = dict(tw=tw, fr=fr)
            REPORT[(ro, m, q, "gap")] = gap
        REPORT[(ro, m, "stat")] = stat

def ci(x):
    x = x[1:]
    x = x[np.isfinite(x)]
    return np.percentile(x, 2.5), np.percentile(x, 97.5), len(x)

print(f"\n=== MODE {MODE} ===")
for ro in ("forced", "free"):
    for m in ("hdA0", "hdB0"):
        st = REPORT[(ro, m, "stat")]
        for q in ("share", "urv"):
            g = REPORT[(ro, m, q, "gap")]
            lo, hi, _ = ci(g)
            print(f"\n[{ro} {m}] {q}: gap={g[0]:+.3f} [{lo:+.3f},{hi:+.3f}]")
        for d in DIRS:
            for a in ARMS:
                s = st[(d, a)]
                line = (f"  {d:6s} {a:4s} n={int(s['n'])} hab={int(s['nhab'])} share={s['share'][0]:.3f} onset={s['onset'][0]:.3f} "
                        f"rival={s['urv'][0]:.3f} helper={s['uhel'][0]:.3f}")
                if a != "none":
                    for q in ("share", "urv"):
                        R = REPORT[(ro, m, q, d, a)]
                        tl, th, _ = ci(R["tw"]); fl, fh, nf = ci(R["fr"])
                        line += f" | {q}: tw={R['tw'][0]:+.3f}[{tl:+.3f},{th:+.3f}] fr={R['fr'][0]:+.2f}[{fl:+.2f},{fh:+.2f}]"
                print(line)
        if ro == "forced":
            for d in DIRS:
                sk = REPORT[(ro, m, "share", d, "sk")]["tw"][0]
                for a in ("P0", "P0a", "P0b", "sk"):
                    R = REPORT[(ro, m, "share", d, a)]
                    tl, th, _ = ci(R["tw"])
                    c1, c2, c3 = R["tw"][0] >= 0.15, (tl > 0 or th < 0), R["tw"][0] > sk
                    print(f"  FLIPS {m} {d} {a}: tw>=.15 {c1}, CI excl 0 {c2}, >sk({sk:+.3f}) {c3} -> {'FLIPS' if c1 and c2 and c3 else 'no'}")
                f0 = REPORT[(ro, m, "share", d, "P0")]["fr"][0]
                if not (f0 >= 0.30):
                    print(f"  GATE FAIL {m} {d}: fraction(P0)={f0:+.3f} < 0.30")
