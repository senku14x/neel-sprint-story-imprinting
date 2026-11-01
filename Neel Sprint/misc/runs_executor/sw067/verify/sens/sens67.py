"""sw067 key sensitivity (analysis agent, 31 Oct 2026). CPU only.
Direction 1: sw067's own and pw arms under sw020 (a)'s exact conversation rule and label
  (014's rule: helper / rival each in >= 2 of the 3 post-trigger replies; affinity = helper - rival;
   trigger specificity = affinity(trig) - affinity(ctrl); reply label = two-judge consensus (mean > 5) wherever both judges'
   records exist, STRICT role otherwise = sw020 an-D5 'P_all').
Direction 2: sw020 (a)'s saved default conversations under sw067's frozen unit (helper role helper|both in ANY reply t3-5, STRICT;
   gating = helper(trig) - helper(ctrl)).
Full grid: run {sw020 H200, sw067 own box C, sw067 pw box C} x rule {any_h, any_aff, ge2_h, ge2_aff} x label {S, P}.
Bootstrap: sw020's construction (scenario-clustered, sorted 64 scenarios, numpy default_rng(20261030), 2,000 draws, percentile 95%),
one weight matrix shared by every quantity, so cross-run differences are paired by scenario.
sw020 code is read, not imported or edited; labels via the E1 lib (STRICT patterns byte-identical to the overnight lib sw020 used)."""
import json, sys
from collections import Counter, defaultdict
import numpy as np
sys.path.insert(0, "/workspace/runs_executor/day_2026-10-31_E1/lib")
import labels as LB
import judge_lib as JL

OUT = "/workspace/runs_executor/sw067/verify/sens/sens67.json"
R20 = "/workspace/runs_executor/sw020/ae"; R67 = "/workspace/runs_executor/sw067/full"
HEL = {"hdA0": "bee", "hdB0": "crow"}

def jl(p):
    return [json.loads(l) for l in open(p) if l.strip()]

def J(paths):
    by = {}
    for p in paths:
        for k, v in JL.load_judged(p, ["bee", "crow"]).items():
            by.setdefault(k, {}).update(v)
    return JL.consensus(by, ["bee", "crow"])

def role_s(text, m):
    return LB.role_label(LB.strict_label(text or ""), HEL[m])

def role_j(c, m):
    return LB.role_label(JL.habit_label(c["bee"], c["crow"]), HEL[m])

recs = []
# ---- sw020 (a) default cells
J20 = J([f"{R20}/judged.jsonl", f"{R20}/judged_flagged.jsonl"])
L20 = {x["key"]: x for x in jl(f"{R20}/labels.jsonl")}
mism = 0; n20j = 0; n20 = 0
for c in jl(f"{R20}/conv.jsonl"):
    if c["model"] not in HEL or not c["cell"].startswith("default|"):
        continue
    m = c["model"]; cl = c["cell"].split("|")[1]
    asst = [x["content"] for x in c["messages"] if x["role"] == "assistant"]; assert len(asst) == 5
    rs = [role_s(a, m) for a in asst]
    rp = list(rs)
    for t in (3, 4, 5):
        k = f"sw020|a|free|{m}|{c['cell'].replace('|', '+')}|{c['sid']}|s0|t{t}"
        mism += L20[k]["role"] != rs[t - 1]; n20 += 1
        if k in J20:
            rp[t - 1] = role_j(J20[k], m); n20j += 1
    recs.append(dict(run="sw020", model=m, cell=cl, sid=c["sid"], scenario=c["scenario"], S=rs, P=rp,
                     u=[x["content"] for x in c["messages"] if x["role"] == "user"], a=asst))
print("sw020 STRICT recompute vs labels.jsonl mismatches", mism, "of", n20, "; judge-labelled t3-5", n20j)
# ---- sw067
J67 = J([f"{R67}/judged_replies.jsonl"])
n67j = Counter()
for c in jl(f"{R67}/conv.jsonl"):
    m = c["model"]; asst = [x["content"] for x in c["messages"] if x["role"] == "assistant"]; assert len(asst) == 5
    rs = [role_s(a, m) for a in asst]; rp = list(rs)
    for t in (3, 4, 5):
        k = f"sw067|reply|{c['arm']}|{m}|{c['cell']}|{c['sid']}|t{t}"
        if k in J67:
            rp[t - 1] = role_j(J67[k], m); n67j[c["arm"]] += 1
    recs.append(dict(run="sw067" + c["arm"], model=m, cell=c["cell"], sid=c["sid"], scenario=c["scenario"], S=rs, P=rp,
                     u=[x["content"] for x in c["messages"] if x["role"] == "user"], a=asst))
print("sw067 judge-labelled t3-5", dict(n67j))

# user-turn identity sw020 vs sw067 own (same protocol), and turn-1 text identity (box numerics)
U = {(r["run"], r["model"], r["cell"], r["sid"]): r for r in recs}
same_u = same_a1 = same_a1_prefix50 = tot = 0
for (run, m, cl, sid), r in U.items():
    if run != "sw067own":
        continue
    o = U[("sw020", m, cl, sid)]; tot += 1
    same_u += o["u"] == r["u"]; same_a1 += o["a"][0] == r["a"][0]; same_a1_prefix50 += o["a"][0][:50] == r["a"][0][:50]
ident = dict(n=tot, user_turns_identical=same_u, a1_identical=same_a1, a1_first50chars_identical=same_a1_prefix50)
print("identity", ident)

def hit(roles, kind):
    post = roles[2:5]
    if kind == "h":
        return [x in ("helper", "both") for x in post]
    return [x in ("rival", "both") for x in post]

def conv_vals(r, lab):
    h = hit(r[lab], "h"); v = hit(r[lab], "r")
    any_h, any_r = float(any(h)), float(any(v)); g_h, g_r = float(sum(h) >= 2), float(sum(v) >= 2)
    return dict(any_h=any_h, any_aff=any_h - any_r, ge2_h=g_h, ge2_aff=g_h - g_r, any_r=any_r, ge2_r=g_r)

for r in recs:
    r["pre_h"] = float(any(x in ("helper", "both") for x in r["S"][:2]))
    r["pre_any"] = float(any(x != "neither" for x in r["S"][:2]))
    r["vals"] = {lab: conv_vals(r, lab) for lab in ("S", "P")}

SC = sorted({r["scenario"] for r in recs}); assert len(SC) == 64
IX = {s: i for i, s in enumerate(SC)}
rng = np.random.default_rng(20261030); draws = rng.integers(0, 64, size=(2000, 64))
W = np.zeros((2000, 64))
for b in range(2000):
    np.add.at(W[b], draws[b], 1)
ONE = np.ones((1, 64))
PW_SIDS = {r["sid"] for r in recs if r["run"] == "sw067pw"}; assert len(PW_SIDS) == 315

def sums(rows, f):
    num = np.zeros(64); den = np.zeros(64)
    for r in rows:
        num[IX[r["scenario"]]] += f(r); den[IX[r["scenario"]]] += 1
    return num, den

def rate(rows, f):
    num, den = sums(rows, f)
    return lambda w: (w @ num) / np.where(w @ den > 0, w @ den, np.nan)

def est(stat):
    pt = float(stat(ONE)[0]); bs = stat(W); bs = bs[~np.isnan(bs)]
    return [round(pt, 4), round(float(np.quantile(bs, .025)), 4), round(float(np.quantile(bs, .975)), 4)]

def sel(run, m, cl, common=False):
    return [r for r in recs if r["run"] == run and r["model"] == m and r["cell"] == cl and (not common or r["sid"] in PW_SIDS)]

RES = dict(identity=ident, judge_labelled=dict(sw020=n20j, sw067=dict(n67j)), strict_mismatch_sw020=mism, grid={}, diffs={}, cells={},
           pre={}, strat_nopre={}, carry={})
RULES = ("any_h", "any_aff", "ge2_h", "ge2_aff")
RUNS = ("sw020", "sw067own", "sw067pw")
gat = {}
for m in HEL:
    for run in RUNS:
        for common in (False, True):
            if run == "sw067pw" and common:
                continue
            for lab in ("S", "P"):
                for rule in RULES:
                    t = rate(sel(run, m, "trig", common), lambda r: r["vals"][lab][rule])
                    c = rate(sel(run, m, "ctrl", common), lambda r: r["vals"][lab][rule])
                    g = (lambda t, c: (lambda w: t(w) - c(w)))(t, c)
                    tag = f"{m}|{run}|{'common315' if common else 'all'}|{lab}|{rule}"
                    gat[tag] = g
                    RES["grid"][tag] = dict(gating=est(g), trig=est(t), ctrl=est(c), n_trig=len(sel(run, m, "trig", common)),
                                            n_ctrl=len(sel(run, m, "ctrl", common)))
    # paired differences between runs (same scenario draws)
    for lab in ("S", "P"):
        for rule in RULES:
            a = gat[f"{m}|sw067own|all|{lab}|{rule}"]; b = gat[f"{m}|sw020|all|{lab}|{rule}"]
            RES["diffs"][f"{m}|own067-sw020|all|{lab}|{rule}"] = est(lambda w: a(w) - b(w))
            a = gat[f"{m}|sw067pw|all|{lab}|{rule}"]; b = gat[f"{m}|sw020|common315|{lab}|{rule}"]
            RES["diffs"][f"{m}|pw067-sw020|common315|{lab}|{rule}"] = est(lambda w: a(w) - b(w))
            a = gat[f"{m}|sw067pw|all|{lab}|{rule}"]; b = gat[f"{m}|sw067own|common315|{lab}|{rule}"]
            RES["diffs"][f"{m}|pw067-own067|common315|{lab}|{rule}"] = est(lambda w: a(w) - b(w))
        # rule effect within a run: sw067 unit minus sw020 rule
        for run in RUNS:
            sc = "all"
            a = gat[f"{m}|{run}|{sc}|S|any_h"]; b = gat[f"{m}|{run}|{sc}|P|ge2_aff"]
            RES["diffs"][f"{m}|{run}|S.any_h-P.ge2_aff"] = est(lambda w: a(w) - b(w))
    # cell counts and descriptive rates
    for run in RUNS:
        for cl in ("trig", "ctrl"):
            rs = sel(run, m, cl)
            x = {f"{lab}.{k}": int(sum(r["vals"][lab][k] for r in rs)) for lab in ("S", "P") for k in ("any_h", "ge2_h", "any_r", "ge2_r")}
            x["n"] = len(rs); x["pre_h"] = int(sum(r["pre_h"] for r in rs)); x["pre_any"] = int(sum(r["pre_any"] for r in rs))
            x["S.any_h_with_pre_h"] = int(sum(r["vals"]["S"]["any_h"] * r["pre_h"] for r in rs))
            x["P.ge2_h_with_pre_h"] = int(sum(r["vals"]["P"]["ge2_h"] * r["pre_h"] for r in rs))
            x["replies_t345_S_helper"] = int(sum(sum(hit(r["S"], "h")) for r in rs))
            x["replies_t345_P_helper"] = int(sum(sum(hit(r["P"], "h")) for r in rs))
            x["replies_t1_S_helper"] = int(sum(r["S"][0] in ("helper", "both") for r in rs))
            x["replies_t2_S_helper"] = int(sum(r["S"][1] in ("helper", "both") for r in rs))
            RES["cells"][f"{m}|{run}|{cl}"] = x
            RES["pre"][f"{m}|{run}|{cl}"] = est(rate(rs, lambda r: r["pre_h"]))
        # pre-treatment stratification: conversations with no helper animal in own turns 1-2 (any animal, as scenqc)
        if run != "sw067pw":
            for lab, rule in (("S", "any_h"), ("P", "ge2_aff")):
                t = rate([r for r in sel(run, m, "trig") if not r["pre_any"]], lambda r: r["vals"][lab][rule])
                c = rate([r for r in sel(run, m, "ctrl") if not r["pre_any"]], lambda r: r["vals"][lab][rule])
                RES["strat_nopre"][f"{m}|{run}|{lab}|{rule}"] = dict(gating=est(lambda w: t(w) - c(w)), trig=est(t), ctrl=est(c),
                    n_trig=sum(1 for r in sel(run, m, "trig") if not r["pre_any"]), n_ctrl=sum(1 for r in sel(run, m, "ctrl") if not r["pre_any"]))
    # pre-trigger rate difference between runs
    for cl in ("trig", "ctrl"):
        a = rate(sel("sw067own", m, cl), lambda r: r["pre_h"]); b = rate(sel("sw020", m, cl), lambda r: r["pre_h"])
        RES["diffs"][f"{m}|pre_h|{cl}|own067-sw020"] = est(lambda w: a(w) - b(w))

json.dump(RES, open(OUT, "w"), indent=1)
for k in ("grid", "diffs", "cells", "pre", "strat_nopre"):
    print("==", k)
    for kk, v in RES[k].items():
        print(kk, v)
