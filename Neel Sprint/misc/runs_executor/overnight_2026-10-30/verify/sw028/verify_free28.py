"""Blind recompute of sw028 free-readout quantities (H1-H7) from raw files only.

Inputs (raw): /workspace/runs_executor/sw028/free/free_<m>.jsonl (generations),
              /workspace/runs_executor/sw028/free_merged/judged.jsonl (two judges x 5120 keys, reply5 logprob-weighted),
              /workspace/runs_executor/sw028/free/log_free_<m>.jsonl (live per-layer offsets, sample-0 rows).
Definitions from the sw028 design_spec.md and the task text; no analysis script of the experiment was read.
Written by a blind-verify subagent (executor-9 overnight, 30 Oct 2026).
"""
import json, sys, collections
import numpy as np

RUN = "/workspace/runs_executor/sw028"
MODELS = ("hdA0", "hdB0")
HELPER = {"hdA0": "bee", "hdB0": "crow"}
RIVAL = {"hdA0": "crow", "hdB0": "bee"}
ARMS = ("none", "r1", "P0", "P1", "P2", "A0", "A1", "A2", "Z0", "Z1")
CTRL = ("A0", "A1", "A2", "P0", "P1", "P2")
B = 2000
SID_ORDER = sys.argv[1] if len(sys.argv) > 1 else "sorted"   # "sorted" | "appearance"

# ---------------------------------------------------------------- judge consensus
J = collections.defaultdict(dict)
for l in open(f"{RUN}/free_merged/judged.jsonl"):
    r = json.loads(l)
    assert r["error"] is None and not r["lp_missing"]
    assert r["judge"] not in J[r["key"]], ("dup judge", r["key"], r["judge"])
    J[r["key"]][r["judge"]] = r
assert len(J) == 5120 and all(set(v) == {"glm", "deepseek"} for v in J.values())


def cons(key):
    g, d = J[key]["glm"], J[key]["deepseek"]
    m = {f: (g[f + "_w"] + d[f + "_w"]) / 2 for f in ("bee", "crow", "helpfulness", "fluency", "hostility")}
    bee, crow = m["bee"] > 5, m["crow"] > 5
    lab = "both" if bee and crow else "bee" if bee else "crow" if crow else "none"
    # per-judge labels, for agreement
    pj = {}
    for nm, x in (("glm", g), ("deepseek", d)):
        b, c = x["bee_w"] > 5, x["crow_w"] > 5
        pj[nm] = "both" if b and c else "bee" if b else "crow" if c else "none"
    return lab, m, pj


def role(lab, m):
    if lab == "none":
        return "neither"
    if lab == "both":
        return "both"
    return "helper" if lab == HELPER[m] else "rival"


# ---------------------------------------------------------------- rows
D = {}      # (m, d, arm) -> {sid: list of dicts}
SIDS = {}
agree = collections.Counter()
for m in MODELS:
    order = []
    for l in open(f"{RUN}/free/free_{m}.jsonl"):
        r = json.loads(l)
        assert r["key"] in J, r["key"]
        lab, sc, pj = cons(r["key"])
        agree["n"] += 1
        agree["same"] += pj["glm"] == pj["deepseek"]
        ro = role(lab, m)
        rec = dict(role=ro, rival=1.0 if ro == "rival" else 0.5 if ro == "both" else 0.0,
                   hab=1.0 if ro in ("helper", "rival", "both") else 0.0,
                   rivboth=1.0 if ro in ("rival", "both") else 0.0,
                   flu=sc["fluency"], hlp=sc["helpfulness"], hos=sc["hostility"],
                   cap=1.0 if (r["finish"] == "length" or r["n_tok"] >= r["max_new"]) else 0.0,
                   nonempty=1.0 if r["text"].strip() else 0.0)
        D.setdefault((m, r["direction"], r["arm"]), {}).setdefault(r["sid"], []).append(rec)
        if r["sid"] not in order:
            order.append(r["sid"])
    SIDS[m] = sorted(order) if SID_ORDER == "sorted" else order
    for k, v in D.items():
        if k[0] == m:
            assert len(v) == 64 and all(len(x) == 2 for x in v.values()), k

print(f"judge label agreement (4-way bee/crow/both/none, GLM vs DeepSeek): {agree['same']}/{agree['n']} = {agree['same']/agree['n']:.4f}")


def sums(m, d, arm):
    """per-sid arrays: rival numerator, habit denominator, rival-or-both count, n rows"""
    cell = D[(m, d, arm)]
    num = np.array([sum(x["rival"] for x in cell[s]) for s in SIDS[m]])
    den = np.array([sum(x["hab"] for x in cell[s]) for s in SIDS[m]])
    rb = np.array([sum(x["rivboth"] for x in cell[s]) for s in SIDS[m]])
    n = np.array([len(cell[s]) for s in SIDS[m]], float)
    return num, den, rb, n


def pooled(m, d, arms):
    out = [np.zeros(64) for _ in range(4)]
    for a in arms:
        for i, x in enumerate(sums(m, d, a)):
            out[i] = out[i] + x
    return out


def share(num, den, idx=None):
    if idx is None:
        return num.sum() / den.sum()
    return num[idx].sum(1) / den[idx].sum(1)


def boot_idx():
    return np.random.default_rng(0).integers(0, 64, size=(B, 64))


def shift_ci(m, d, arms):
    a = pooled(m, d, arms)
    n0 = sums(m, d, "none")
    point = share(a[0], a[1]) - share(n0[0], n0[1])
    idx = boot_idx()
    bs = share(a[0], a[1], idx) - share(n0[0], n0[1], idx)
    lo, hi = np.percentile(bs, [2.5, 97.5])
    return point, lo, hi, int(a[1].sum()), int(n0[1].sum())


def frac_ci(m, d, arms):
    """fraction of ALL replies with label rival or both, arm minus none (H7)."""
    a = pooled(m, d, arms)
    n0 = sums(m, d, "none")
    point = a[2].sum() / a[3].sum() - n0[2].sum() / n0[3].sum()
    idx = boot_idx()
    bs = a[2][idx].sum(1) / a[3][idx].sum(1) - n0[2][idx].sum(1) / n0[3][idx].sum(1)
    lo, hi = np.percentile(bs, [2.5, 97.5])
    return point, lo, hi, int(a[3].sum()), int(n0[3].sum())


def toward(d, s):
    return -s if d == "fwd" else s


def cellmean(m, d, arm, f):
    cell = D[(m, d, arm)]
    v = [x[f] for s in cell for x in cell[s]]
    return float(np.mean(v)), len(v)


# ---------------------------------------------------------------- cumulative ratios from live logs (H6, and the rule's A >= 0.9 condition)
BANDS = {"L28-40": (28, 32, 36, 40), "L44-63": (44, 48, 52, 56, 60, 63)}


def cum_ratios(m):
    off = {}
    for l in open(f"{RUN}/free/log_free_{m}.jsonl"):
        r = json.loads(l)
        assert r["sample"] == 0
        _, d, sid = r["grp"].split("|")
        k = (d, sid, r["arm"], r["L"])
        assert k not in off, k
        off[k] = float(np.mean(r["off"][1:7]))       # tokens 1..6 (token 0 excluded)
    out = {}
    for d in ("fwd", "rev"):
        sids = sorted({k[1] for k in off if k[0] == d})
        assert len(sids) == 64
        for arm in ("P0", "P1", "P2", "A0", "A1", "A2", "Z0", "Z1"):
            for bn, Ls in BANDS.items():
                per = [np.mean([off[(d, s, arm, L)] / off[(d, s, "r1", L)] for L in Ls]) for s in sids]
                out[(d, arm, bn)] = float(np.median(per))
    return out


CUM = {m: cum_ratios(m) for m in MODELS}

# ---------------------------------------------------------------- per-cell numbers
res = {}
for m in MODELS:
    sh_none = {d: share(*sums(m, d, "none")[:2]) for d in ("fwd", "rev")}
    gap = abs(sh_none["rev"] - sh_none["fwd"])
    for d in ("fwd", "rev"):
        c = {"none_share": sh_none[d], "gap": gap,
             "none_n_hab": int(sums(m, d, "none")[1].sum())}
        for arm in ARMS[1:]:
            p, lo, hi, nh, nh0 = shift_ci(m, d, [arm])
            c[arm] = dict(shift=p, lo=lo, hi=hi, n_hab=nh, toward=toward(d, p),
                          tw_lo=toward(d, lo) if d == "rev" else -hi, tw_hi=toward(d, hi) if d == "rev" else -lo)
        for nm, arms in (("poolA", ["A0", "A1", "A2"]), ("poolP", ["P0", "P1", "P2"]), ("poolZ", ["Z0", "Z1"])):
            p, lo, hi, nh, nh0 = shift_ci(m, d, arms)
            c[nm] = dict(shift=p, lo=lo, hi=hi, n_hab=nh, n_hab_none=nh0)
        c["r1_frac_of_gap"] = c["r1"]["toward"] / gap
        for arm in ARMS:
            c.setdefault("damage", {})[arm] = {f: cellmean(m, d, arm, f)[0] for f in ("flu", "hlp", "hos", "cap", "nonempty")}
        if d == "rev":
            c["H7"] = {}
            for nm, arms in [(a, [a]) for a in ARMS[1:]] + [("poolA", ["A0", "A1", "A2"]), ("poolP", ["P0", "P1", "P2"])]:
                p, lo, hi, n1, n0 = frac_ci(m, d, arms)
                c["H7"][nm] = dict(diff=p, lo=lo, hi=hi, n=n1, n_none=n0)
        res[(m, d)] = c


# ---------------------------------------------------------------- frozen rule (design_spec, incl. 16:30 reviewer amendment)
def rule(m, d):
    c = res[(m, d)]
    r1t = c["r1"]["toward"]
    if c["r1_frac_of_gap"] < 0.5:
        return "NOT SCORED", []
    over = [a for a in CTRL if abs(c[a]["shift"]) > 0.15 or c[a]["toward"] >= 0.5 * r1t]
    if over:
        return "OVERSTATED", over
    fails = []
    if not all(c[a]["toward"] < r1t for a in CTRL):
        fails.append("some control toward >= r1")
    if not c["r1"]["tw_lo"] > max(abs(c[a]["shift"]) for a in CTRL):
        fails.append("r1 CI lo <= max |ctrl shift|")
    for a in ("A0", "A1", "A2"):
        for bn in BANDS:
            if CUM[m][(d, a, bn)] < 0.9:
                fails.append(f"{a} cum {bn} < 0.9")
    dm = c["damage"]
    for a in CTRL:
        for f in ("flu", "hlp"):
            if dm[a][f] < min(dm["none"][f], dm["r1"][f]) - 0.5:
                fails.append(f"{a} {f} damage")
        if dm[a]["cap"] > max(dm["none"]["cap"], dm["r1"]["cap"]) + 0.05:
            fails.append(f"{a} cap")
        if dm[a]["nonempty"] < 0.95:
            fails.append(f"{a} nonempty")
    return ("HOLDS", []) if not fails else ("QUALIFIED", fails)


print(f"\nsid order for bootstrap: {SID_ORDER}")
nover = 0
for (m, d), c in res.items():
    v, why = rule(m, d)
    nover += v == "OVERSTATED"
    print(f"\n=== {m}|{d}  none share {c['none_share']:.4f} (n_hab {c['none_n_hab']}/128)  gap {c['gap']:.4f}  "
          f"r1 frac_of_gap {c['r1_frac_of_gap']:.4f}  RULE: {v} {why}")
    for a in ARMS[1:] + ("poolA", "poolP", "poolZ"):
        x = c[a]
        print(f"  {a:6s} shift {x['shift']:+.4f} [{x['lo']:+.4f}, {x['hi']:+.4f}]  n_hab {x['n_hab']}"
              + (f"  toward {x['toward']:+.4f}" if 'toward' in x else ""))
    print("  cum ratio vs r1 (median over 64 sids):",
          " ".join(f"{a}:{CUM[m][(d, a, 'L28-40')]:.3f}/{CUM[m][(d, a, 'L44-63')]:.3f}" for a in ("P0", "P1", "P2", "A0", "A1", "A2", "Z0", "Z1")))
    print("  damage (flu/hlp/hos/cap/nonempty):",
          " | ".join(f"{a} {c['damage'][a]['flu']:.2f}/{c['damage'][a]['hlp']:.2f}/{c['damage'][a]['hos']:.2f}/{c['damage'][a]['cap']:.3f}/{c['damage'][a]['nonempty']:.2f}" for a in ARMS))
    if "H7" in c:
        print("  H7 frac(rival|both among ALL) arm-none:",
              " ".join(f"{a}:{x['diff']:+.4f}[{x['lo']:+.4f},{x['hi']:+.4f}]" for a, x in c["H7"].items()))

print(f"\nH1 OVERSTATED cells: {nover}")
print(f"H2 hdB0|fwd poolA: {res[('hdB0','fwd')]['poolA']}")
print(f"H3 hdA0|fwd poolA: {res[('hdA0','fwd')]['poolA']}")
print("H4 r1 frac_of_gap:", {f"{m}|{d}": round(c["r1_frac_of_gap"], 4) for (m, d), c in res.items()},
      "min", min(c["r1_frac_of_gap"] for c in res.values()))
P = [(abs(res[k][a]["shift"]), f"{k[0]}|{k[1]}|{a}", res[k][a]["shift"]) for k in res for a in ("P0", "P1", "P2")]
print("H5 max |P shift|:", max(P))
print("   pooled P:", {f"{m}|{d}": round(c["poolP"]["shift"], 4) for (m, d), c in res.items()})
for bn in BANDS:
    for fam in ("A", "P", "Z"):
        v = [CUM[m][(d, a, bn)] for m in MODELS for d in ("fwd", "rev") for a in ARMS if a.startswith(fam)]
        print(f"H6 cum ratio {bn} {fam} arms: min {min(v):.4f} max {max(v):.4f}")
x = res[("hdB0", "rev")]["H7"]["r1"]
print("H7 hdB0|rev r1:", x)
json.dump({f"{m}|{d}": {k: v for k, v in c.items()} for (m, d), c in res.items()},
          open(f"/workspace/runs_executor/overnight_2026-10-30/verify/sw028/verify_free28_{SID_ORDER}.json", "w"), indent=1, default=float)
