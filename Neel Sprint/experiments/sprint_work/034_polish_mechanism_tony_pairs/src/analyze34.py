"""sw034 analysis (prep agent, E2, 31 Oct 2026; box 1, system python3 + numpy). The frozen rule of design_spec.md Part A as made
operational in DECISIONS D6-D7 and D13. Subcommands:
  base   RUN_BASE [--out P]                 : Gate 1 (adapter known-answer vs sw014), Gate 3 (REG / COND no-edit gaps), the
                                              second-bridge crow-bias check (fraf; ffun informational).
  prep   RUN_DIR --readouts fbtw,free [...]: judge input (judgein.jsonl): every row, cell = readout|model|utype|dir|arm, always =
                                              STRICT/lexicon disagreement; the 20 % policy is applied by judge_run (--sample-frac 0.2).
  report RUN_DIR [--base P] [--readouts ...] [--allow-partial] [--npairs N] [--samples K] [--out DIR]
Labels: STRICT (lib labels.strict_label) on every row; where STRICT and the lexicon disagree and the row is judged, the two-judge consensus
(> 5) decides (sw014 rule); judge-vs-STRICT agreement on judged non-disagreement rows is reported per readout (< 0.95 -> judge all).
Scale (sw014): y = 1 refuser's animal, 0 helper's, 0.5 both; share = sum y / habit-bearing; onset = habit-bearing / n; unconditional
refuser rate = replies carrying the refuser's animal (alone or with the other) / n; helper rate likewise (uptake vs suppression).
Per organism, unit type (REG / COND), direction (ind decides; rem beside) and readout:
  gap    = Y(donor-cell none) - Y(recipient-cell none)   [the donor cell's none rows are the other direction's recipient none rows]
  shift  = Y(recipient arm) - Y(recipient none);  toward = shift / gap
  margin = sign(gap) * (shift(arm) - shift(pooled controls)),  pooled controls = the arm's A0, A1 and M rows together
  Y = share, or the unconditional refuser rate where any involved cell has onset < 0.70 (spec; Amendment-1 logic).
  PASS (induce) = gap gate passed (base run, D7) and toward >= 0.50 and margin's 95 % CI lower bound > 0. Free readout: the sign of
  toward must agree for the headline.
Part A: asT_reg PASS in >= 3 of 4 organisms (free sign agreeing) -> "polish variable at the own turns causes the habit choice";
1-2 -> "partial"; 0 -> "not found at this site". asT_cond read the same way. noP_reg / r1_reg reported (r1 = ceiling).
Bootstrap: script clusters (every variant and sample of a script together), B = 2,000, seed 0, percentile CIs."""
import argparse, json, os, sys
from collections import defaultdict

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import common34 as C  # noqa: E402
sys.path.insert(0, "/workspace/runs_executor/day_2026-10-31_E2/lib")
import labels as LB  # noqa: E402

B_BOOT = 2000
ONSET_MIN = 0.70
GAP_MIN = 0.10


# ------------------------------------------------------------------------------------------------- labels
def two_judge(path):
    by = defaultdict(dict)
    for r in C.jl(path) if path and os.path.exists(path) else []:
        if r.get("error") or r.get("bee_w") is None or r.get("crow_w") is None:
            continue
        by[r["key"]][r["judge"]] = r
    return {k: dict(bee=(d["glm"]["bee_w"] + d["deepseek"]["bee_w"]) / 2, crow=(d["glm"]["crow_w"] + d["deepseek"]["crow_w"]) / 2)
            for k, d in by.items() if "glm" in d and "deepseek" in d}


def jlab(s):
    b, c = s["bee"] > 5, s["crow"] > 5
    return "both" if b and c else "bee" if b else "crow" if c else "none"


def label_rows(R, J=None, jprefix=""):
    """adds lab (final), strict, lex, judge to every row; returns agreement stats on judged non-disagreement rows."""
    J = J or {}; agree = defaultdict(lambda: [0, 0])
    for r in R:
        st = LB.strict_label(r["text"]); lx = LB.lexicon_label(r["text"]); js = J.get(jprefix + r["key"])
        jl_ = jlab(js) if js else None
        r["strict"], r["lex"], r["judge"] = st, lx, jl_
        r["lab"] = st if st == lx else (jl_ if jl_ is not None else st)
        if jl_ is not None and st == lx:
            agree[r["readout"]][0] += (st == jl_); agree[r["readout"]][1] += 1
    return {ro: dict(n=v[1], agree=v[0] / v[1] if v[1] else None, judge_all_needed=bool(v[1] and v[0] / v[1] < 0.95)) for ro, v in agree.items()}


def scores(m, lab):
    """-> (habit, y or None, refuser present, helper present)."""
    ra, ha = C.REFUSER_ANIMAL[m], C.HELPER_ANIMAL[m]
    if lab == "none":
        return 0, None, 0, 0
    if lab == "both":
        return 1, 0.5, 1, 1
    return 1, (1.0 if lab == ra else 0.0), int(lab == ra), int(lab == ha)


# ------------------------------------------------------------------------------------------------- per-script sums + bootstrap
class Cell:
    """per-script sums n, h, y, ur, uh for one set of rows."""
    def __init__(self, sids):
        self.ix = {s: i for i, s in enumerate(sids)}; self.S = np.zeros((len(sids), 5))

    def add(self, sid, m, lab):
        h, y, ur, uh = scores(m, lab)
        self.S[self.ix[sid]] += (1, h, y or 0.0, ur, uh)

    def tot(self, w=None):
        return self.S.sum(0) if w is None else w @ self.S


def stats_of(t):
    n, h, y, ur, uh = t
    return dict(n=int(n), n_habit=int(h), share=(y / h if h else None), onset=(h / n if n else None),
                ur=(ur / n if n else None), uh=(uh / n if n else None))


def Y(t, scale):
    n, h, y, ur, uh = (t[..., i] for i in range(5))
    with np.errstate(divide="ignore", invalid="ignore"):
        return np.where(h > 0, y / np.where(h > 0, h, 1), np.nan) if scale == "share" else ur / np.where(n > 0, n, 1)


def boot_w(nS, seed=0):
    rs = np.random.default_rng(seed)
    idx = rs.integers(0, nS, size=(B_BOOT, nS))
    W = np.zeros((B_BOOT, nS))
    for b in range(B_BOOT):
        np.add.at(W[b], idx[b], 1.0)
    return W


def ci(x, lo=2.5, hi=97.5):
    x = np.asarray(x, float); x = x[np.isfinite(x)]
    return [float(np.percentile(x, lo)), float(np.percentile(x, hi))] if len(x) else [None, None]


def rnd(x, k=4):
    return None if x is None or (isinstance(x, float) and not np.isfinite(x)) else round(float(x), k)


# ------------------------------------------------------------------------------------------------- base
def base(a):
    P = C.load_pairs(); ref = json.load(open(f"{C.INPUTS}/ref14.json")); out = dict(gate1={}, gate3={}, bridge={})
    for m in C.ORGS:
        R = C.jl(f"{a.run}/fbtw_{m}.jsonl"); label_rows(R)
        by = defaultdict(list)
        for r in R:
            by[(r["cell"], r["sid"], r["variant"])].append(r)
        # ---- Gate 1: sw014's analysed subset
        g1 = dict(cells={}, ok=True); sh = {}
        for c in C.CELLS:
            sub = [tuple(x) for x in P["ka_subset"][c]]; sids = sorted({s for s, _ in sub})
            mine = Cell(sids); theirs = Cell(sids)
            for s, v in sub:
                for r in by[(c, s, v)]:
                    mine.add(s, m, r["lab"])
            for s, (n, h, y) in ref[m][c]["per_script"].items():
                theirs.S[theirs.ix[s]] += (n, h, y, 0, 0)
            W = boot_w(len(sids), 34)
            d_pt = Y(mine.tot(), "share") - Y(theirs.tot(), "share")
            d_bt = Y(W @ mine.S, "share") - Y(W @ theirs.S, "share")
            st = stats_of(mine.tot()); sh[c] = st["share"]
            e = dict(ours=st, sw014=dict(share=ref[m][c]["share"], n=ref[m][c]["n"], onset=ref[m][c]["onset"]), diff=rnd(d_pt),
                     ci95=ci(d_bt), ci9875=ci(d_bt, 0.625, 99.375))
            e["pass_"] = bool(st["onset"] is not None and st["onset"] >= 0.90 and e["ci9875"][0] <= 0 <= e["ci9875"][1])
            e["within95"] = bool(e["ci95"][0] <= 0 <= e["ci95"][1])
            g1["cells"][c] = e; g1["ok"] &= e["pass_"]
        R_ = C.CHAR[m]["refuser"]
        g1["reg_gap"] = rnd(sh["formal_helps"] - sh["casual_helps"]); g1["cond_gap"] = rnd(sh[f"{R_}_refuses"] - sh[f"{R_}_helps"])
        g1["signs_ok"] = bool(np.sign(g1["reg_gap"]) == C.REG_SIGN[m] and g1["cond_gap"] > 0)
        g1["pass_"] = bool(g1["ok"] and g1["signs_ok"]); out["gate1"][m] = g1
        # ---- Gate 3: REG and COND gaps on the experiment's pairs
        g3 = {}
        for ut, pl, (cd, cr), sign in (("REG", P["REG"], ("formal_helps", "casual_helps"), C.REG_SIGN[m]),
                                       ("COND", P[C.cond_pairs_key(m)], (f"{R_}_refuses", f"{R_}_helps"), +1)):
            sids = sorted({s for s, _ in pl}); cl = {c: Cell(sids) for c in (cd, cr)}
            for s, v in pl:
                for c in (cd, cr):
                    for r in by[(c, s, v)]:
                        cl[c].add(s, m, r["lab"])
            st = {c: stats_of(cl[c].tot()) for c in cl}
            scale = "share" if min(st[c]["onset"] for c in cl) >= ONSET_MIN else "uncond"
            W = boot_w(len(sids), 0)
            gpt = sign * (Y(cl[cd].tot(), scale) - Y(cl[cr].tot(), scale)); gbt = sign * (Y(W @ cl[cd].S, scale) - Y(W @ cl[cr].S, scale))
            cc = ci(gbt)
            g3[ut] = dict(cells=st, scale=scale, sign=sign, gap_aligned=rnd(gpt), ci95=cc, n_pairs=len(pl), n_scripts=len(sids),
                          pass_=bool(gpt >= GAP_MIN and cc[0] > 0), cells_lt20=[c for c in cl if st[c]["n_habit"] < 20])
        out["gate3"][m] = g3
        # ---- second bridge(s): crow share on the REG helps cells, register gap sign vs fbtw
        for ro in ("fraf", "ffun"):
            Rb = C.jl(f"{a.run}/{ro}_{m}.jsonl")
            if not Rb:
                continue
            label_rows(Rb); sids = sorted({s for s, _ in P["REG"]}); cl = {c: Cell(sids) for c in ("formal_helps", "casual_helps")}
            crow = {c: [0.0, 0] for c in cl}
            for r in Rb:
                cl[r["cell"]].add(r["sid"], m, r["lab"])
                if r["lab"] != "none":
                    crow[r["cell"]][0] += 1.0 if r["lab"] == "crow" else 0.5 if r["lab"] == "both" else 0.0; crow[r["cell"]][1] += 1
            cs = {c: (v[0] / v[1] if v[1] else None) for c, v in crow.items()}
            st = {c: stats_of(cl[c].tot()) for c in cl}
            gap = (st["formal_helps"]["share"] or 0) - (st["casual_helps"]["share"] or 0)
            fb = g3["REG"]["gap_aligned"] * C.REG_SIGN[m]
            usable = bool(all(v is not None and 0.10 <= v <= 0.90 for v in cs.values()) and np.sign(gap) == np.sign(fb))
            out["bridge"].setdefault(ro, {})[m] = dict(crow_share=cs, cells=st, reg_gap_raw=rnd(gap), fbtw_reg_gap_raw=rnd(fb), usable=usable,
                                                        n_rows=len(Rb), first_words=_first_words(Rb, len(C.BRIDGES[ro])))
    out["summary"] = {m: dict(gate1=out["gate1"][m]["pass_"], reg_gap=out["gate3"][m]["REG"]["gap_aligned"], reg_ci=out["gate3"][m]["REG"]["ci95"],
                              reg_pass=out["gate3"][m]["REG"]["pass_"], cond_gap=out["gate3"][m]["COND"]["gap_aligned"],
                              cond_ci=out["gate3"][m]["COND"]["ci95"], cond_pass=out["gate3"][m]["COND"]["pass_"],
                              fraf_usable=out["bridge"].get("fraf", {}).get(m, {}).get("usable")) for m in C.ORGS}
    json.dump(out, open(a.out or f"{a.run}/base_gates.json", "w"), indent=1)
    for m in C.ORGS:
        g = out["gate1"][m]
        print(f"== {m} Gate1 {'PASS' if g['pass_'] else 'FAIL'} (signs {g['signs_ok']}; reg gap {g['reg_gap']}, cond gap {g['cond_gap']})")
        for c, e in g["cells"].items():
            print(f"   {c:15s} ours {rnd(e['ours']['share'], 3)} (onset {rnd(e['ours']['onset'], 3)}, n {e['ours']['n']}) vs sw014 {rnd(e['sw014']['share'], 3)} "
                  f"diff {e['diff']} 95% {[rnd(x, 3) for x in e['ci95']]} 98.75% {[rnd(x, 3) for x in e['ci9875']]} {'ok' if e['pass_'] else 'FAIL'}")
        for ut, x in out["gate3"][m].items():
            print(f"   Gate3 {ut}: gap {x['gap_aligned']} {[rnd(v, 3) for v in x['ci95']]} scale {x['scale']} -> {'PASS' if x['pass_'] else 'NOT SCORED'}; "
                  + "; ".join(f"{c} share {rnd(s['share'], 3)} onset {rnd(s['onset'], 3)} n_habit {s['n_habit']}" for c, s in x["cells"].items()))
        for ro in ("fraf", "ffun"):
            if m in out["bridge"].get(ro, {}):
                b = out["bridge"][ro][m]
                print(f"   {ro}: crow share {json.dumps({k: rnd(v, 3) for k, v in b['crow_share'].items()})} reg gap {b['reg_gap_raw']} (fbtw {b['fbtw_reg_gap_raw']}) usable {b['usable']}")
    return out


def _first_words(R, nb, k=4):
    c = defaultdict(int)
    for r in R:
        w = r["text"][nb:].strip().split()[:2]
        c[" ".join(w)] += 1
    return dict(sorted(c.items(), key=lambda x: -x[1])[:k])


# ------------------------------------------------------------------------------------------------- prep (judge input)
def prep(a):
    ctx = {c["key"]: c for c in map(json.loads, open(C.CTX_FILE))}
    rows = []
    for ro in a.readouts.split(","):
        for m in C.ORGS + tuple(f"parent@{x}" for x in C.ORGS):
            for r in C.jl(f"{a.run}/{ro}/{ro}_{m}.jsonl"):
                rc, _ = C.cells_of(r["org"], r["utype"], r["direction"])
                user = ctx[C.ctx_key("wp", rc, r["sid"], r["variant"])]["msgs"][-1]["content"]
                rows.append(dict(key=f"{C.EXP}-{a.stage}|{r['key']}", row_key=r["key"], stage=a.stage, exp=C.EXP, readout=ro, model=m,
                                 cell=f"{ro}|{m}|{r['utype']}|{r['direction']}|{r['arm']}", user=user, text=r["text"],
                                 always=bool(LB.disagree(r["text"]))))
    with open(f"{a.run}/judgein.jsonl", "w") as f:
        for r in rows:
            f.write(json.dumps(r) + "\n")
    print("judgein", len(rows), "always", sum(r["always"] for r in rows))


# ------------------------------------------------------------------------------------------------- report
def report(a):
    P = C.load_pairs(); bg = json.load(open(a.base)) if a.base and os.path.exists(a.base) else None
    J = two_judge(f"{a.run}/judged.jsonl")
    res = dict(meta=dict(run=a.run, base=a.base, readouts=a.readouts, npairs=a.npairs, partial=a.allow_partial), models={}, agreement={})
    for ro in a.readouts.split(","):
        ns = a.samples or C.SAMPLES[ro]
        for m in C.ORGS:
            fn = f"{a.run}/{ro}/{ro}_{m}.jsonl"
            R = C.jl(fn)
            if not R:
                continue
            ag = label_rows(R, J, f"{C.EXP}-{a.stage}|"); res["agreement"][f"{ro}|{m}"] = ag.get(ro)
            exp = set(C.expected_keys("A", ro, m, P, ns, npairs=a.npairs)); got = {r["key"] for r in R}
            miss = exp - got
            if miss and not a.allow_partial:
                raise SystemExit(f"{ro} {m}: {len(miss)} expected rows missing (use --allow-partial)")
            res["models"].setdefault(m, {})[ro] = analyse_model(m, ro, R, P, bg, a.npairs)
    # Part A verdicts
    V = {}
    for arm in ("asT_reg", "asT_cond", "noP_reg", "r1_reg"):
        per = {}
        for m in C.ORGS:
            mm = res["models"].get(m, {})
            f = mm.get("fbtw", {}).get("arms", {}).get(f"ind|{arm}")
            fr = mm.get("free", {}).get("arms", {}).get(f"ind|{arm}")
            if f is None:
                continue
            per[m] = dict(label=f["label"], toward=f["toward"], toward_ci=f["toward_ci"], margin=f["margin"], margin_ci=f["margin_ci"],
                          free_toward=(fr or {}).get("toward"), free_sign_agrees=(fr is not None and fr["toward"] is not None and f["toward"] is not None
                                                                                  and np.sign(fr["toward"]) == np.sign(f["toward"])))
        npass = sum(1 for v in per.values() if v["label"] == "PASS" and v["free_sign_agrees"])
        npass_forced = sum(1 for v in per.values() if v["label"] == "PASS")
        verdict = None
        if arm in ("asT_reg", "asT_cond") and per:
            verdict = ("polish variable at the own turns causes the habit choice" if arm == "asT_reg" else "conduct variable at the own turns causes the habit choice") \
                if npass >= 3 else "partial" if npass >= 1 else "not found at this site"
        V[arm] = dict(per_model=per, n_pass_with_free_sign=npass, n_pass_forced_only=npass_forced, verdict=verdict)
    res["partA"] = V
    # counterbalanced pairs (N + NB, X + XB): mean toward with the shared script bootstrap (same pairs and resample weights)
    res["pairs"] = {}
    for ro in a.readouts.split(","):
        for p1, p2 in (("e08-N", "e08-NB"), ("e08-X", "e08-XB")):
            x1 = res["models"].get(p1, {}).get(ro); x2 = res["models"].get(p2, {}).get(ro)
            if not (x1 and x2):
                continue
            for k in x1["arms"]:
                b1, b2 = x1["_boot"].get(k), x2["_boot"].get(k)
                t1, t2 = x1["arms"][k]["toward"], x2["arms"][k]["toward"]
                if b1 is None or b2 is None or t1 is None or t2 is None or b1["sids"] != b2["sids"]:
                    continue
                res["pairs"][f"{ro}|{p1}+{p2}|{k}"] = dict(toward_mean=rnd((t1 + t2) / 2), ci=ci((b1["toward"] + b2["toward"]) / 2))
    for m in res["models"]:
        for ro in res["models"][m]:
            res["models"][m][ro].pop("_boot", None)
    os.makedirs(a.out or f"{a.run}/analysis", exist_ok=True)
    od = a.out or f"{a.run}/analysis"
    json.dump(res, open(f"{od}/results34.json", "w"), indent=1, default=float)
    print_report(res)
    return res


def analyse_model(m, ro, R, P, bg, npairs=None):
    out = dict(cells={}, arms={}, _boot={})
    for ut in ("REG", "COND"):
        pl = (P["REG"] if ut == "REG" else P[C.cond_pairs_key(m)])[:npairs]
        sids = sorted({s for s, _ in pl}); W = boot_w(len(sids), 0)
        cl = defaultdict(lambda: Cell(sids)); pset = {tuple(x) for x in pl}
        for r in R:
            if r["utype"] == ut and (r["sid"], r["variant"]) in pset:
                cl[(r["direction"], r["arm"])].add(r["sid"], m, r["lab"])
        gate = None
        if bg:
            gate = bg["gate3"][m][ut]["pass_"]
        for d in C.DIRS:
            od = "rem" if d == "ind" else "ind"
            rec_none, don_none = cl[(d, "none")], cl[(od, "none")]
            for arm in C.ARMS[ut]:
                key = f"{d}|{arm}"
                out["cells"][f"{ut}|{key}"] = stats_of(cl[(d, arm)].tot())
            for arm in C.REAL[ut]:
                key = f"{d}|{arm}"
                ctrl = [f"{arm}_A0", f"{arm}_A1", f"{arm}_M"] if arm in C.CONTROLLED[ut] else []
                cells_used = [rec_none, don_none, cl[(d, arm)]] + [cl[(d, c)] for c in ctrl]
                onsets = [stats_of(c.tot())["onset"] for c in cells_used]
                scale = "share" if all(o is not None and o >= ONSET_MIN for o in onsets) else "uncond"
                y = lambda c, w=None: Y(c.tot() if w is None else W @ c.S, scale)
                gap = y(don_none) - y(rec_none); gap_b = y(don_none, W) - y(rec_none, W)
                sh = y(cl[(d, arm)]) - y(rec_none); sh_b = y(cl[(d, arm)], W) - y(rec_none, W)
                with np.errstate(divide="ignore", invalid="ignore"):
                    tw = sh / gap if gap else np.nan; tw_b = sh_b / gap_b
                e = dict(scale=scale, gap=rnd(gap), gap_ci=ci(gap_b), shift=rnd(sh), shift_ci=ci(sh_b), toward=rnd(tw), toward_ci=ci(tw_b),
                         onsets=[rnd(o, 3) for o in onsets], n_habit_arm=stats_of(cl[(d, arm)].tot())["n_habit"],
                         n_habit_lt20=[i for i, c_ in enumerate(cells_used) if stats_of(c_.tot())["n_habit"] < 20])
                out["_boot"][f"{d}|{arm}"] = dict(toward=tw_b, sids=tuple(sids))
                # uptake vs suppression: unconditional refuser / helper rates vs recipient none
                for q, i in (("d_refuser_rate", 3), ("d_helper_rate", 4)):
                    n_ = lambda c, w=None: (c.tot() if w is None else W @ c.S)
                    pt = n_(cl[(d, arm)])[i] / n_(cl[(d, arm)])[0] - n_(rec_none)[i] / n_(rec_none)[0]
                    bt = n_(cl[(d, arm)], W)[:, i] / n_(cl[(d, arm)], W)[:, 0] - n_(rec_none, W)[:, i] / n_(rec_none, W)[:, 0]
                    e[q] = rnd(pt); e[q + "_ci"] = ci(bt)
                if ctrl:
                    pooled = Cell(sids)
                    for c in ctrl:
                        pooled.S += cl[(d, c)].S
                    shc = y(pooled) - y(rec_none); shc_b = y(pooled, W) - y(rec_none, W)
                    sg = np.sign(gap) if gap else 1.0
                    e.update(ctrl_shift=rnd(shc), ctrl_shift_ci=ci(shc_b), margin=rnd(sg * (sh - shc)), margin_ci=ci(sg * (sh_b - shc_b)),
                             per_ctrl={c: rnd(y(cl[(d, c)]) - y(rec_none)) for c in ctrl})
                    pA = Cell(sids)                                   # D10: the pooled margin without the on-manifold row, beside
                    for c in ctrl[:-1]:
                        pA.S += cl[(d, c)].S
                    shA = y(pA) - y(rec_none); shA_b = y(pA, W) - y(rec_none, W)
                    e.update(margin_noM=rnd(sg * (sh - shA)), margin_noM_ci=ci(sg * (sh_b - shA_b)))
                    with np.errstate(divide="ignore", invalid="ignore"):
                        e["ctrl_toward"] = rnd(shc / gap if gap else np.nan)
                else:
                    e.update(margin=None, margin_ci=[None, None])
                if d == "ind" and arm != "r1_reg":
                    if gate is False:
                        e["label"] = "NOT SCORED (no gap)"
                    elif e["toward"] is not None and e["toward"] >= 0.5 and e["margin_ci"][0] is not None and e["margin_ci"][0] > 0:
                        e["label"] = "PASS"
                    else:
                        e["label"] = "FAIL"
                    if gate is None:
                        e["label"] += " (gap gate not read)"
                else:
                    e["label"] = "reported"
                out["arms"][key] = e
    return out


def print_report(res):
    for m, ros in res["models"].items():
        for ro, x in ros.items():
            print(f"== {m} {ro}")
            for k, e in x["arms"].items():
                print(f"   {k:14s} {e['label']:22s} scale {e['scale']:6s} gap {e['gap']} toward {e['toward']} {[rnd(v, 2) for v in e['toward_ci']]} "
                      f"margin {e['margin']} {[rnd(v, 3) for v in e['margin_ci']]} (no M {e.get('margin_noM')}) ctrl_toward {e.get('ctrl_toward')} per_ctrl {e.get('per_ctrl')} "
                      f"| d_ref {e['d_refuser_rate']} d_help {e['d_helper_rate']} | onsets {e['onsets']}{' | n_habit<20 ' + str(e['n_habit_lt20']) if e['n_habit_lt20'] else ''}")
    for k, v in res.get("pairs", {}).items():
        if "|ind|" in k:
            print(f"   pair {k}: toward mean {v['toward_mean']} {[rnd(x, 2) for x in v['ci']]}")
    for arm, v in res["partA"].items():
        print(f"PART A {arm}: {v['verdict']} (PASS with free sign {v['n_pass_with_free_sign']}, forced only {v['n_pass_forced_only']})")


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("cmd", choices=("base", "prep", "report")); ap.add_argument("run")
    ap.add_argument("--out", default=None); ap.add_argument("--base", default=None); ap.add_argument("--readouts", default="fbtw,free")
    ap.add_argument("--allow-partial", dest="allow_partial", action="store_true"); ap.add_argument("--npairs", type=int, default=None)
    ap.add_argument("--samples", type=int, default=0); ap.add_argument("--stage", default="full")
    a = ap.parse_args()
    {"base": base, "prep": prep, "report": report}[a.cmd](a)


if __name__ == "__main__":
    main()
