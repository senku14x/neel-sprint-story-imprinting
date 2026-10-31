"""Blind recompute of sw029 headline numbers from raw rows (CPU only).
Bootstrap: sids sorted lexicographically; rng = np.random.default_rng(0); idx = rng.integers(0, 64, (2000, 64));
the same idx matrix is used for every arm, every quantity and both models (shared resamples)."""
import json, sys, importlib.util, os
import numpy as np

RAW = "/workspace/runs_executor/sw029_blind/raw"
OUT = "/workspace/runs_executor/sw029_blind/out"
spec = importlib.util.spec_from_file_location("labels", "/workspace/runs_executor/overnight_2026-10-30/lib/labels.py")
L = importlib.util.module_from_spec(spec); spec.loader.exec_module(L)
HELPER = {"hdA0": "bee", "hdB0": "crow"}
RIVAL = {"hdA0": "crow", "hdB0": "bee"}
ARMS = ["par", "noP", "asH", "asT", "asB", "stC", "stP"]
B, SEED = 2000, 0


def load(f):
    return [json.loads(l) for l in open(f"{RAW}/{f}")]


def role(text, model):
    return L.role_label(L.strict_label(text), HELPER[model])  # helper / rival / both / neither


free = {m: load(f"free_{m}.jsonl") for m in HELPER}
fnoP = {m: load(f"forced_noP_{m}.jsonl") for m in HELPER}
fbtw = {m: load(f"fbtw_{m}.jsonl") for m in HELPER}
SIDS = sorted({r["sid"] for r in free["hdA0"]})
for m in HELPER:
    for D in (free, fnoP, fbtw):
        assert sorted({r["sid"] for r in D[m]}) == SIDS
    assert all(r["model"] == m for r in free[m] + fnoP[m] + fbtw[m])
SI = {s: i for i, s in enumerate(SIDS)}
NS = len(SIDS)
assert NS == 64
rng = np.random.default_rng(SEED)
IDX = rng.integers(0, NS, size=(B, NS))
W = np.stack([np.bincount(row, minlength=NS) for row in IDX]).astype(float)  # B x 64 multiplicities


def counts(rows, model):
    """per-sid arrays: n, rival(incl both), helper(incl both), habit, rival_only, both"""
    c = {k: np.zeros(NS) for k in ("n", "rival", "helper", "habit", "rival_only", "both", "helper_only")}
    for r in rows:
        i = SI[r["sid"]]; ro = role(r["text"], model)
        c["n"][i] += 1
        c["rival"][i] += ro in ("rival", "both")
        c["helper"][i] += ro in ("helper", "both")
        c["habit"][i] += ro != "neither"
        c["rival_only"][i] += ro == "rival"
        c["helper_only"][i] += ro == "helper"
        c["both"][i] += ro == "both"
    return c


def rate(c, num):  # returns (point, boot array)
    return c[num].sum() / c["n"].sum(), (W @ c[num]) / (W @ c["n"])


def selection(c):
    num = c["rival_only"] + 0.5 * c["both"]
    return num.sum() / c["habit"].sum(), (W @ num) / (W @ c["habit"])


def ci(b):
    b = np.asarray(b, float)
    fin = np.isfinite(b)
    lo, hi = np.percentile(b[fin], [2.5, 97.5])
    return float(lo), float(hi), int((~fin).sum())


def fmt(p, b):
    lo, hi, nf = ci(b)
    return dict(point=float(p), lo=lo, hi=hi, n_nonfinite=nf)


res = {"meta": dict(B=B, seed=SEED, n_sids=NS, sid_order="sorted", label="strict_label",
                    helper=HELPER, rival=RIVAL)}
ratio_boot = {}
for m in HELPER:
    R = {}
    cell = {}
    for arm in ["none", "r1"] + ARMS + [f"{a}_A{k}" for a in ARMS for k in (0, 1)]:
        for d in ("rev", "fwd"):
            rows = [r for r in free[m] if r["arm"] == arm and r["direction"] == d]
            cell[(arm, d)] = counts(rows, m)
    for a in ARMS:  # pooled A
        cell[(a + "_Apool", "rev")] = {k: cell[(a + "_A0", "rev")][k] + cell[(a + "_A1", "rev")][k] for k in cell[(a + "_A0", "rev")]}
    # unconditional rival / helper / onset rates in rev, per arm
    rates = {}
    for (arm, d), c in cell.items():
        if d != "rev":
            continue
        rates[arm] = {q: rate(c, q) for q in ("rival", "helper", "habit", "helper_only", "rival_only")}
        rates[arm]["n"] = int(c["n"].sum())
    none_fwd = rate(cell[("none", "fwd")], "rival")
    gap = (none_fwd[0] - rates["none"]["rival"][0], none_fwd[1] - rates["none"]["rival"][1])
    tow = {arm: (rates[arm]["rival"][0] - rates["none"]["rival"][0], rates[arm]["rival"][1] - rates["none"]["rival"][1]) for arm in rates}
    R["rival_rate_rev"] = {arm: fmt(*rates[arm]["rival"]) | {"n": rates[arm]["n"]} for arm in rates}
    R["rival_rate_none_fwd"] = fmt(*none_fwd) | {"n": int(cell[("none", "fwd")]["n"].sum())}
    R["gap"] = fmt(*gap)
    R["toward_r1"] = fmt(*tow["r1"])
    R["r1_over_gap"] = fmt(tow["r1"][0] / gap[0], tow["r1"][1] / gap[1])
    R["arms"] = {}
    ratio_boot[m] = {}
    for a in ARMS:
        rp, rb = tow[a][0] / tow["r1"][0], tow[a][1] / tow["r1"][1]
        ratio_boot[m][a] = (rp, rb)
        ap = a + "_Apool"
        mp, mb = tow[a][0] - tow[ap][0], tow[a][1] - tow[ap][1]
        A0 = a + "_A0"; A1 = a + "_A1"
        e = dict(toward=fmt(*tow[a]), ratio=fmt(rp, rb), towardA_pooled=fmt(*tow[ap]),
                 towardA0=fmt(*tow[A0]), towardA1=fmt(*tow[A1]), ratioA_pooled=fmt(tow[ap][0] / tow["r1"][0], tow[ap][1] / tow["r1"][1]),
                 margin=fmt(mp, mb))
        mlo, mhi, _ = ci(mb)
        if rp >= 0.50 and mlo > 0:
            lab = "PASS"
        elif rp <= 0.15 or (mlo <= 0 <= mhi):
            lab = "LOW"
        else:
            lab = "MID"
        e["rule"] = lab
        e["rule_note"] = "margin CI entirely < 0" if mhi < 0 else ""
        # onset (habit-bearing) and helper-rate shifts vs none in rev
        for q in ("habit", "helper", "helper_only", "rival_only"):
            e[f"{q}_rate"] = fmt(*rates[a][q])
            e[f"{q}_shift"] = fmt(rates[a][q][0] - rates["none"][q][0], rates[a][q][1] - rates["none"][q][1])
        R["arms"][a] = e
    R["none_rev"] = {q: fmt(*rates["none"][q]) for q in ("rival", "helper", "habit", "helper_only", "rival_only")}
    R["r1_rev"] = {q: fmt(*rates["r1"][q]) for q in ("rival", "helper", "habit", "helper_only", "rival_only")}
    # pooled-A rates too
    R["Apool_rev_rival"] = {a: fmt(*rates[a + "_Apool"]["rival"]) for a in ARMS}
    # 4. noP forced check (fbtw only)
    cs = {cond: counts([r for r in fnoP[m] if r["readout"] == "fbtw" and r["cond"] == cond], m) for cond in ("self-hostile", "user-hostile")}
    s_self, s_user = selection(cs["self-hostile"]), selection(cs["user-hostile"])
    g_wo = (s_self[0] - s_user[0], s_self[1] - s_user[1])
    cw = {d: counts([r for r in fbtw[m] if r["arm"] == "none" and r["direction"] == d], m) for d in ("fwd", "rev")}
    w_f, w_r = selection(cw["fwd"]), selection(cw["rev"])
    g_w = (w_f[0] - w_r[0], w_f[1] - w_r[1])
    R["noP_forced"] = dict(
        sel_noP_self=fmt(*s_self), sel_noP_user=fmt(*s_user), gap_without=fmt(*g_wo),
        sel_withP_fwd=fmt(*w_f), sel_withP_rev=fmt(*w_r), gap_with=fmt(*g_w),
        ratio_without_over_with=fmt(g_wo[0] / g_w[0], g_wo[1] / g_w[1]),
        n=dict(noP_self=int(cs["self-hostile"]["n"].sum()), noP_user=int(cs["user-hostile"]["n"].sum()),
               noP_self_habit=int(cs["self-hostile"]["habit"].sum()), noP_user_habit=int(cs["user-hostile"]["habit"].sum()),
               withP_fwd=int(cw["fwd"]["n"].sum()), withP_rev=int(cw["rev"]["n"].sum()),
               withP_fwd_habit=int(cw["fwd"]["habit"].sum()), withP_rev_habit=int(cw["rev"]["habit"].sum())))
    res[m] = R

# 3. pair average of ratios (shared resamples)
res["pair_avg_ratio"] = {}
for a in ARMS:
    p = 0.5 * (ratio_boot["hdA0"][a][0] + ratio_boot["hdB0"][a][0])
    b = 0.5 * (ratio_boot["hdA0"][a][1] + ratio_boot["hdB0"][a][1])
    res["pair_avg_ratio"][a] = fmt(p, b)

json.dump(res, open(f"{OUT}/recompute.json", "w"), indent=1)


def s(e, k=3):
    return f"{e['point']:.{k}f} [{e['lo']:.{k}f}, {e['hi']:.{k}f}]" + (f" (nonfinite {e['n_nonfinite']})" if e["n_nonfinite"] else "")


lines = []
for m in HELPER:
    R = res[m]
    lines.append(f"== {m} (helper {HELPER[m]}, rival {RIVAL[m]})")
    lines.append(f"rival none rev {s(R['rival_rate_rev']['none'])}  none fwd {s(R['rival_rate_none_fwd'])}  gap {s(R['gap'])}")
    lines.append(f"r1 rival rev {s(R['rival_rate_rev']['r1'])}  toward(r1) {s(R['toward_r1'])}  r1/gap {s(R['r1_over_gap'])}")
    lines.append("arm | rival rate | toward | ratio | towardA(pooled) | margin | rule")
    for a in ARMS:
        e = R["arms"][a]
        lines.append(f"{a} | {s(R['rival_rate_rev'][a])} | {s(e['toward'])} | {s(e['ratio'])} | {s(e['towardA_pooled'])} | {s(e['margin'])} | {e['rule']} {e['rule_note']}")
    lines.append("A0/A1 toward: " + "; ".join(f"{a}: {s(R['arms'][a]['towardA0'])} / {s(R['arms'][a]['towardA1'])}" for a in ARMS))
    nf = R["noP_forced"]
    lines.append(f"noP forced: sel self {s(nf['sel_noP_self'])} user {s(nf['sel_noP_user'])} gap_without {s(nf['gap_without'])}")
    lines.append(f"            withP fwd {s(nf['sel_withP_fwd'])} rev {s(nf['sel_withP_rev'])} gap_with {s(nf['gap_with'])}  ratio {s(nf['ratio_without_over_with'])}  n {nf['n']}")
    lines.append(f"none rev: habit {s(R['none_rev']['habit'])} helper {s(R['none_rev']['helper'])} helper_only {s(R['none_rev']['helper_only'])}")
    for a in ("asT", "asB"):
        e = R["arms"][a]
        lines.append(f"{a}: onset {s(e['habit_rate'])} shift {s(e['habit_shift'])} | helper {s(e['helper_rate'])} shift {s(e['helper_shift'])} | helper_only shift {s(e['helper_only_shift'])}")
lines.append("== pair average ratio")
for a in ARMS:
    lines.append(f"{a}: {s(res['pair_avg_ratio'][a])}")
open(f"{OUT}/recompute.txt", "w").write("\n".join(lines) + "\n")
print("\n".join(lines))
