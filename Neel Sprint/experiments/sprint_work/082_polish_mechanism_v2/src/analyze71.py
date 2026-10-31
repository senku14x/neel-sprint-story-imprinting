"""sw071 analysis (prep-71, E2, 31 Oct 2026; box 1, system python3 + numpy; sw034 analyze34.py adapted; DECISIONS D13). The frozen
rules of design_spec.md. Subcommands:
  base   RUN_BASE [--out P]   : Gate 3 = no-edit forced gaps per organism: REG (fbtw), COND (fbtw), and REG under each fixed opener
                                (fo, co); gap >= 0.10 with the 95 % script-cluster CI excluding 0, else NOT SCORED (sw034 D7).
  prep   RUN_DIR [--stage S]  : judge input (judgein.jsonl): every row of fbtw / fo / co / free (+ the parent floor); cell =
                                readout|model|utype|dir|arm; always = STRICT / lexicon disagreement OR a free row of sample 0 (spec).
  report RUN_DIR --base P [--allow-partial] [--npairs N] [--samples K] [--out DIR]
Labels: STRICT on every row; where STRICT and the lexicon disagree and the row is judged, the two-judge reply5 consensus (> 5) decides
(sw014 / sw034 D14); judge-vs-STRICT agreement on judged non-disagreement rows per (readout, model); < 0.95 -> judge_all_needed.
Scale (sw014): y = 1 refuser's animal, 0 helper's, 0.5 both; share = sum y / habit-bearing; onset = habit-bearing / n; unconditional
refuser rate ur = replies naming the refuser's animal / n; helper rate uh likewise.
Per organism, readout, unit type, direction, arm:
  gap = Y(donor-cell none) - Y(recipient-cell none) [donor-cell none = the other direction's recipient none rows, same run]
  shift = Y(arm) - Y(recipient none); toward = shift / gap; margin = sign(gap) (shift(arm) - shift(pooled controls)); pooled = A0 + A1
  + M (fbtw / free) or A0 + A1 (fo / co: the opener's pooled A); margin without M beside. Y = share, or ur where any involved cell has
  onset < 0.70. Uptake vs suppression: d ur and d uh vs recipient none. Cells with < 20 habit-bearing replies flagged.
  PASS (induce, controlled arm) = gap gate passed and toward >= 0.50 and margin's 95 % CI lower bound > 0.
Part A (asT_reg; asT_cond the same way): headline PASS(m) = forced (fbtw) PASS and, where the free no-edit gap (ur scale) has its CI
excluding 0, the free shift of ur has the forced gap's sign (sw034 D29 reading (b)); >= 3 PASS among the scored organisms -> "causes";
1-2 "partial"; 0 "not found at this site". Counts with the free condition always applied, and forced-only, beside.
Fixed opener (asT_reg induce), per organism x opener o (scored if the fbtw REG gate and the REG|o gate both pass):
  ratio = toward_o / toward_fbtw (toward_o relative to the opener's own no-edit gap); margin_o over the opener's pooled A.
  own(m, o) = ratio >= 0.50 and margin_o CI lower > 0;  reg(m, o) = ratio <= 0.20 or margin_o CI includes 0.
  OWN-PAST POLISH if, for both openers, own holds in >= 3 organisms scored for that opener; REPLY REGISTER if, for both openers, reg
  holds in >= 3 scored organisms; INTERMEDIATE otherwise (per-organism ratios reported).
Bootstrap: script clusters (every variant and sample of a script together), B = 2,000, seed 0, percentile CIs; domain-clustered
(8 domains resampled) CIs beside."""
import argparse, json, os, random, sys
from collections import defaultdict

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import common71 as C  # noqa: E402
sys.path.insert(0, "/workspace/runs_executor/day_2026-10-31_E2/lib")
import labels as LB  # noqa: E402

B_BOOT = 2000
ONSET_MIN = 0.70
GAP_MIN = 0.10
FORCED = ("fbtw", "fo", "co")


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
    ra, ha = C.REFUSER_ANIMAL[m], C.HELPER_ANIMAL[m]
    if lab == "none":
        return 0, None, 0, 0
    if lab == "both":
        return 1, 0.5, 1, 1
    return 1, (1.0 if lab == ra else 0.0), int(lab == ra), int(lab == ha)


# ------------------------------------------------------------------------------------------------- per-script sums + bootstrap
class Cell:
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
        if scale == "share":
            return np.where(h > 0, y / np.where(h > 0, h, 1), np.nan)
        if scale == "uh":
            return uh / np.where(n > 0, n, 1)
        return ur / np.where(n > 0, n, 1)


def boot_w(sids, seed=0, by=None):
    """script-cluster weights (B x nS); with by = {sid: domain}, domain-cluster weights (domains resampled, every script of a drawn
    domain enters with the domain's count)."""
    rs = np.random.default_rng(seed); nS = len(sids)
    if by is None:
        idx = rs.integers(0, nS, size=(B_BOOT, nS)); W = np.zeros((B_BOOT, nS))
        for b in range(B_BOOT):
            np.add.at(W[b], idx[b], 1.0)
        return W
    doms = sorted({by[s] for s in sids}); di = {d: i for i, d in enumerate(doms)}
    idx = rs.integers(0, len(doms), size=(B_BOOT, len(doms))); WD = np.zeros((B_BOOT, len(doms)))
    for b in range(B_BOOT):
        np.add.at(WD[b], idx[b], 1.0)
    return WD[:, [di[by[s]] for s in sids]]


def ci(x, lo=2.5, hi=97.5):
    x = np.asarray(x, float); x = x[np.isfinite(x)]
    return [float(np.percentile(x, lo)), float(np.percentile(x, hi))] if len(x) else [None, None]


def rnd(x, k=4):
    return None if x is None or (isinstance(x, float) and not np.isfinite(x)) else round(float(x), k)


# ------------------------------------------------------------------------------------------------- base (gap gates)
def gap_gate(by, m, pl, cd, cr, sign, dom):
    sids = sorted({s for s, _ in pl}); cl = {c: Cell(sids) for c in (cd, cr)}
    for s, v in pl:
        for c in (cd, cr):
            for r in by.get((c, s, v), []):
                cl[c].add(s, m, r["lab"])
    st = {c: stats_of(cl[c].tot()) for c in cl}
    scale = "share" if all(st[c]["onset"] is not None and st[c]["onset"] >= ONSET_MIN for c in cl) else "uncond"
    W = boot_w(sids, 0); WD = boot_w(sids, 0, dom)
    g = lambda w=None: sign * (Y(cl[cd].tot(w), scale) - Y(cl[cr].tot(w), scale))
    gpt = float(g()); cc = ci(g(W)); cd_ = ci(g(WD))
    return dict(cells=st, scale=scale, sign=sign, gap_aligned=rnd(gpt), ci95=cc, ci95_domain=cd_, n_pairs=len(pl), n_scripts=len(sids),
                pass_=bool(np.isfinite(gpt) and gpt >= GAP_MIN and cc[0] is not None and cc[0] > 0), cells_lt20=[c for c in cl if st[c]["n_habit"] < 20])


def base(a):
    P = C.load_pairs(); dom = P["fold"]; out = dict(gate3={})
    for m in C.ORGS:
        g3 = {}; R_ = C.CHAR[m]["refuser"]
        for ro in ("fbtw", "fo", "co"):
            R = C.jl(f"{a.run}/{ro}_{m}.jsonl")
            if not R:
                continue
            label_rows(R); by = defaultdict(list)
            for r in R:
                by[(r["cell"], r["sid"], r["variant"])].append(r)
            g3[f"REG|{ro}"] = gap_gate(by, m, P["REG"], "formal_helps", "casual_helps", C.REG_SIGN[m], dom)
            if ro == "fbtw":
                g3["COND|fbtw"] = gap_gate(by, m, P[C.cond_pairs_key(m)], f"{R_}_refuses", f"{R_}_helps", +1, dom)
        out["gate3"][m] = g3
    json.dump(out, open(a.out or f"{a.run}/base_gates.json", "w"), indent=1)
    for m, g3 in out["gate3"].items():
        for k, x in g3.items():
            print(f"{m:7s} {k:9s} gap {x['gap_aligned']} {[rnd(v, 3) for v in x['ci95']]} (domain {[rnd(v, 3) for v in x['ci95_domain']]}) scale {x['scale']} "
                  f"-> {'PASS' if x['pass_'] else 'NOT SCORED'}; " + "; ".join(f"{c} share {rnd(s['share'], 3)} onset {rnd(s['onset'], 3)} n_habit {s['n_habit']}" for c, s in x["cells"].items()))
    return out


# ------------------------------------------------------------------------------------------------- prep (judge input)
def prep(a):
    ctx = {c["key"]: c for c in map(json.loads, open(C.CTX_FILE))}
    rows = []
    for ro, sub in (("fbtw", "full"), ("fo", "full"), ("co", "full"), ("free", "full"), ("fbtw", "parent")):
        for m in C.ORGS:
            mlab = f"parent@{m}" if sub == "parent" else m
            for r in C.jl_all(f"{a.run}/{sub}/{ro}", ro, mlab):
                rc, _ = C.cells_of(r["org"], r["utype"], r["direction"])
                user = ctx[C.ctx_key(rc, r["sid"], r["variant"])]["msgs"][-1]["content"]
                rows.append(dict(key=f"{C.EXP}-{a.stage}|{r['key']}", row_key=r["key"], stage=a.stage, exp=C.EXP, readout=ro, model=mlab,
                                 cell=f"{ro}|{mlab}|{r['utype']}|{r['direction']}|{r['arm']}", user=user, text=r["text"],
                                 always=bool(LB.disagree(r["text"]) or (ro == "free" and r["sample"] == 0))))
    keys = [r["key"] for r in rows]
    assert len(keys) == len(set(keys)), "judge-input keys not unique"
    with open(f"{a.run}/judgein.jsonl", "w") as f:
        for r in rows:
            f.write(json.dumps(r) + "\n")
    print("judgein", len(rows), "always", sum(r["always"] for r in rows))


# ------------------------------------------------------------------------------------------------- report
def analyse_model(m, ro, R, P, g3, npairs=None):
    out = dict(cells={}, arms={}, _boot={})
    dom = P["fold"]
    for ut in C.READOUT_UTYPES[ro]:
        pl = P[C.list_name(m, ut)][:npairs]
        sids = sorted({s for s, _ in pl}); W = boot_w(sids, 0); WD = boot_w(sids, 0, dom)
        cl = defaultdict(lambda: Cell(sids)); pset = {tuple(x) for x in pl}
        for r in R:
            if r["utype"] == ut and (r["sid"], r["variant"]) in pset:
                cl[(r["direction"], r["arm"])].add(r["sid"], m, r["lab"])
        gk = f"{ut}|{ro}" if ro in FORCED else f"{ut}|fbtw"
        gate = None
        if g3 is not None:
            gate = bool(g3[m][gk]["pass_"]) if ro != "free" else bool(g3[m][f"{ut}|fbtw"]["pass_"])
            if ro in C.OPENERS:
                gate = gate and bool(g3[m]["REG|fbtw"]["pass_"])
        arms = C.arms_for(ro, ut)
        for d in C.DIRS:
            od = "rem" if d == "ind" else "ind"
            rec_none, don_none = cl[(d, "none")], cl[(od, "none")]
            for arm in arms:
                out["cells"][f"{ut}|{d}|{arm}"] = stats_of(cl[(d, arm)].tot())
            for arm in C.REAL[ut]:
                if arm not in arms:
                    continue
                key = f"{ut}|{d}|{arm}"
                ctrl = [c for c in (f"{arm}_A0", f"{arm}_A1", f"{arm}_M") if c in arms] if arm in C.CONTROLLED[ut] else []
                cells_used = [rec_none, don_none, cl[(d, arm)]] + [cl[(d, c)] for c in ctrl]
                onsets = [stats_of(c.tot())["onset"] for c in cells_used]
                scale = "share" if all(o is not None and o >= ONSET_MIN for o in onsets) else "uncond"
                y = lambda c, w=None: Y(c.tot(w), scale)
                e = dict(scale=scale, onsets=[rnd(o, 3) for o in onsets], n_habit_arm=stats_of(cl[(d, arm)].tot())["n_habit"],
                         n_habit_lt20=[i for i, c_ in enumerate(cells_used) if stats_of(c_.tot())["n_habit"] < 20])
                gap = float(y(don_none) - y(rec_none)); sh = float(y(cl[(d, arm)]) - y(rec_none))
                with np.errstate(divide="ignore", invalid="ignore"):
                    tw = sh / gap if gap else np.nan
                e.update(gap=rnd(gap), shift=rnd(sh), toward=rnd(tw))
                for tag, w in (("", W), ("_domain", WD)):
                    gb = y(don_none, w) - y(rec_none, w); sb = y(cl[(d, arm)], w) - y(rec_none, w)
                    with np.errstate(divide="ignore", invalid="ignore"):
                        tb = sb / gb
                    e[f"gap_ci{tag}"] = ci(gb); e[f"shift_ci{tag}"] = ci(sb); e[f"toward_ci{tag}"] = ci(tb)
                    if tag == "":
                        out["_boot"][key] = dict(toward=tb, shift=sb, sids=tuple(sids))
                # uptake vs suppression + free-style unconditional rates (ur gap, ur shift)
                for q, sc_ in (("refuser_rate", "uncond"), ("helper_rate", "uh")):
                    pt = float(Y(cl[(d, arm)].tot(), sc_) - Y(rec_none.tot(), sc_)); bt = Y(cl[(d, arm)].tot(W), sc_) - Y(rec_none.tot(W), sc_)
                    e[f"d_{q}"] = rnd(pt); e[f"d_{q}_ci"] = ci(bt)
                gu = float(Y(don_none.tot(), "uncond") - Y(rec_none.tot(), "uncond")); gub = Y(don_none.tot(W), "uncond") - Y(rec_none.tot(W), "uncond")
                e["ur_gap"] = rnd(gu); e["ur_gap_ci"] = ci(gub)
                e["rates"] = {nm: dict(ur=stats_of(c_.tot())["ur"], uh=stats_of(c_.tot())["uh"], share=stats_of(c_.tot())["share"], onset=stats_of(c_.tot())["onset"])
                              for nm, c_ in (("rec_none", rec_none), ("don_none", don_none), ("arm", cl[(d, arm)]))}
                if ctrl:
                    sg = np.sign(gap) if gap else 1.0
                    pooled = Cell(sids)
                    for c in ctrl:
                        pooled.S += cl[(d, c)].S
                    shc = float(y(pooled) - y(rec_none)); e.update(ctrl_shift=rnd(shc), margin=rnd(sg * (sh - shc)),
                                                              per_ctrl={c: rnd(float(y(cl[(d, c)]) - y(rec_none))) for c in ctrl})
                    for tag, w in (("", W), ("_domain", WD)):
                        shc_b = y(pooled, w) - y(rec_none, w); sh_b = y(cl[(d, arm)], w) - y(rec_none, w)
                        e[f"margin_ci{tag}"] = ci(sg * (sh_b - shc_b)); e[f"ctrl_shift_ci{tag}"] = ci(shc_b)
                    noM = [c for c in ctrl if not c.endswith("_M")]
                    if len(noM) < len(ctrl):
                        pA = Cell(sids)
                        for c in noM:
                            pA.S += cl[(d, c)].S
                        shA = float(y(pA) - y(rec_none)); shA_b = y(pA, W) - y(rec_none, W)
                        e.update(margin_noM=rnd(sg * (sh - shA)), margin_noM_ci=ci(sg * (y(cl[(d, arm)], W) - y(rec_none, W) - shA_b)))
                    with np.errstate(divide="ignore", invalid="ignore"):
                        e["ctrl_toward"] = rnd(shc / gap if gap else np.nan)
                else:
                    e.update(margin=None, margin_ci=[None, None])
                if d == "ind" and arm in C.CONTROLLED[ut] and ro != "free":
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


def report(a):
    P = C.load_pairs(); bg = json.load(open(a.base)) if a.base and os.path.exists(a.base) else None
    g3 = bg["gate3"] if bg else None
    J = two_judge(f"{a.run}/judged.jsonl")
    if os.path.exists(f"{a.run}/judged_all.jsonl"):
        J.update(two_judge(f"{a.run}/judged_all.jsonl"))
    res = dict(meta=dict(run=a.run, base=a.base, npairs=a.npairs, partial=a.allow_partial, n_judged_keys=len(J)), models={}, agreement={}, gates=g3)
    for ro in ("fbtw", "fo", "co", "free"):
        ns = a.samples or C.SAMPLES[ro]
        for m in C.ORGS:
            R = C.jl_all(f"{a.run}/full/{ro}", ro, m)
            if not R:
                continue
            ag = label_rows(R, J, f"{C.EXP}-{a.stage}|"); res["agreement"][f"{ro}|{m}"] = ag.get(ro)
            exp = set(C.expected_keys("A", ro, m, P, ns, npairs=a.npairs)); got = {r["key"] for r in R}
            if (exp - got) and not a.allow_partial:
                raise SystemExit(f"{ro} {m}: {len(exp - got)} expected rows missing (use --allow-partial)")
            res["models"].setdefault(m, {})[ro] = analyse_model(m, ro, R, P, g3, a.npairs)
    res["judge_all_needed"] = sorted(k for k, v in res["agreement"].items() if v and v["judge_all_needed"])
    # ---- Part A
    V = {}
    for arm, ut in (("asT_reg", "REG"), ("asT_cond", "COND"), ("r1_reg", "REG")):
        per = {}
        for m in C.ORGS:
            mm = res["models"].get(m, {}); f = mm.get("fbtw", {}).get("arms", {}).get(f"{ut}|ind|{arm}")
            fr = mm.get("free", {}).get("arms", {}).get(f"{ut}|ind|{arm}")
            if f is None:
                continue
            fsg = float(np.sign(f["gap"])) if f.get("gap") else 0.0
            fal = None if fr is None or fr.get("d_refuser_rate") is None else fsg * fr["d_refuser_rate"]
            fal_ci = None if fr is None or fr["d_refuser_rate_ci"][0] is None else sorted(fsg * x for x in fr["d_refuser_rate_ci"])
            fgap_ci = (fr or {}).get("ur_gap_ci", [None, None])
            fgap_excl0 = bool(fgap_ci[0] is not None and (fgap_ci[0] > 0 or fgap_ci[1] < 0))
            scored = None if g3 is None else bool(g3[m][f"{ut}|fbtw"]["pass_"])
            forced_pass = f["label"] == "PASS"
            head = forced_pass and (not fgap_excl0 or (fal is not None and fal > 0))
            per[m] = dict(label=f["label"], scored=scored, toward=f["toward"], toward_ci=f["toward_ci"], toward_ci_domain=f.get("toward_ci_domain"),
                          margin=f.get("margin"), margin_ci=f.get("margin_ci"), margin_ci_domain=f.get("margin_ci_domain"), margin_noM=f.get("margin_noM"),
                          gap=f["gap"], scale=f["scale"], d_refuser_rate=f["d_refuser_rate"], d_helper_rate=f["d_helper_rate"],
                          free_ur_gap=(fr or {}).get("ur_gap"), free_ur_gap_ci=fgap_ci, free_gap_ci_excludes_0=fgap_excl0,
                          free_d_refuser_aligned=rnd(fal), free_d_refuser_aligned_ci=fal_ci, free_d_helper=(fr or {}).get("d_helper_rate"),
                          headline_pass=bool(head), pass_free_always=bool(forced_pass and fal is not None and fal > 0))
        n_head = sum(v["headline_pass"] for v in per.values()); n_forced = sum(v["label"] == "PASS" for v in per.values())
        n_always = sum(v["pass_free_always"] for v in per.values()); n_scored = sum(1 for v in per.values() if v["scored"])
        verdict = None
        if arm != "r1_reg" and per:
            verdict = ("causes the habit choice (v2)" if n_head >= 3 else "partial" if n_head >= 1 else "not found at this site")
        V[arm] = dict(per_model=per, n_scored=n_scored, n_pass_headline=n_head, n_pass_forced_only=n_forced, n_pass_free_sign_always=n_always,
                      verdict=verdict, n_pass_without_NB=sum(v["headline_pass"] for mm_, v in per.items() if mm_ != "e08-NB"))
    res["partA"] = V
    # ---- fixed opener
    FO = dict(per={}, counts={})
    for o in C.OPENERS:
        FO["counts"][o] = dict(scored=0, own=0, reg=0)
        for m in C.ORGS:
            mm = res["models"].get(m, {}); f0 = mm.get("fbtw", {}).get("arms", {}).get("REG|ind|asT_reg"); fo = mm.get(o, {}).get("arms", {}).get("REG|ind|asT_reg")
            if f0 is None or fo is None:
                continue
            scored = None if g3 is None else bool(g3[m]["REG|fbtw"]["pass_"] and g3[m][f"REG|{o}"]["pass_"])
            t0, t1 = f0["toward"], fo["toward"]
            ratio = (t1 / t0) if (t0 is not None and t1 is not None and t0 > 0) else None
            b0 = mm["fbtw"]["_boot"]["REG|ind|asT_reg"]; b1 = mm[o]["_boot"]["REG|ind|asT_reg"]
            with np.errstate(divide="ignore", invalid="ignore"):
                rb = b1["toward"] / b0["toward"]
            sratio = (fo["shift"] / f0["shift"]) if f0["shift"] else None
            mci = fo.get("margin_ci", [None, None])
            own = bool(ratio is not None and ratio >= 0.50 and mci[0] is not None and mci[0] > 0)
            regl = bool(ratio is not None and (ratio <= 0.20 or not (mci[0] is not None and mci[0] > 0)))
            FO["per"][f"{m}|{o}"] = dict(scored=scored, toward_opener=t1, toward_noopener=t0, ratio=rnd(ratio), ratio_ci=ci(rb), shift_ratio=rnd(sratio),
                                         margin=fo.get("margin"), margin_ci=mci, margin_ci_domain=fo.get("margin_ci_domain"), opener_gap=fo["gap"],
                                         opener_gap_ci=fo["gap_ci"], own_past=own, reply_register=regl, scale=fo["scale"],
                                         d_refuser_rate=fo["d_refuser_rate"], d_helper_rate=fo["d_helper_rate"], label=fo["label"])
            if scored:
                FO["counts"][o]["scored"] += 1; FO["counts"][o]["own"] += own; FO["counts"][o]["reg"] += regl
    cnt = FO["counts"]
    if all(cnt[o]["own"] >= 3 for o in C.OPENERS):
        FO["verdict"] = "OWN-PAST POLISH"
    elif all(cnt[o]["reg"] >= 3 for o in C.OPENERS):
        FO["verdict"] = "REPLY REGISTER"
    else:
        FO["verdict"] = "INTERMEDIATE"
    FO["note"] = ("fewer than 3 organisms scored for an opener: neither OWN-PAST POLISH nor REPLY REGISTER can be reached"
                  if any(cnt[o]["scored"] < 3 for o in C.OPENERS) else "")
    res["fixed_opener"] = FO
    # ---- counterbalanced pairs
    res["pairs"] = {}
    for ro in ("fbtw", "fo", "co", "free"):
        for p1, p2 in (("e08-N", "e08-NB"), ("e08-X", "e08-XB")):
            x1 = res["models"].get(p1, {}).get(ro); x2 = res["models"].get(p2, {}).get(ro)
            if not (x1 and x2):
                continue
            for k in x1["arms"]:
                if "|ind|" not in k or k not in x2["arms"]:
                    continue
                b1, b2 = x1["_boot"].get(k), x2["_boot"].get(k); t1, t2 = x1["arms"][k]["toward"], x2["arms"][k]["toward"]
                if b1 is None or b2 is None or t1 is None or t2 is None or b1["sids"] != b2["sids"]:
                    continue   # different pair lists (COND formal vs casual) -> no shared bootstrap
                res["pairs"][f"{ro}|{p1}+{p2}|{k}"] = dict(toward_mean=rnd((t1 + t2) / 2), ci=ci((b1["toward"] + b2["toward"]) / 2))
    # ---- parent floor
    res["parent_floor"] = {}
    for m in C.ORGS:
        R = C.jl_all(f"{a.run}/parent/fbtw", "fbtw", f"parent@{m}")
        if not R:
            continue
        label_rows(R, J, f"{C.EXP}-{a.stage}|"); cnt_ = defaultdict(lambda: [0, 0])
        for r in R:
            cnt_[f"{r['utype']}|{r['arm']}"][0] += 1; cnt_[f"{r['utype']}|{r['arm']}"][1] += r["lab"] in ("bee", "crow", "both")
        res["parent_floor"][m] = {k: dict(n=v[0], habit_rate=rnd(v[1] / v[0] if v[0] else None)) for k, v in sorted(cnt_.items())}
    # ---- 10 seeded-random raw outputs per key cell (for the analysis)
    smp = {}
    for ro in ("fbtw", "fo", "co", "free"):
        for m in C.ORGS:
            R = C.jl_all(f"{a.run}/full/{ro}", ro, m)
            for arm in ("none", "asT_reg"):
                pool = sorted((r for r in R if r["utype"] == "REG" and r["direction"] == "ind" and r["arm"] == arm), key=lambda r: r["key"])
                rr = random.Random(f"sw071|{ro}|{m}|{arm}").sample(pool, min(10, len(pool))) if pool else []
                smp[f"{ro}|{m}|REG|ind|{arm}"] = [dict(key=r["key"], text=r["text"][:1200]) for r in rr]
    od = a.out or f"{a.run}/analysis"; os.makedirs(od, exist_ok=True)
    for m in res["models"]:
        for ro in res["models"][m]:
            res["models"][m][ro].pop("_boot", None)
    json.dump(res, open(f"{od}/results71.json", "w"), indent=1, default=float)
    json.dump(smp, open(f"{od}/samples71.json", "w"), indent=1)
    print_report(res)
    return res


def print_report(res):
    for m, ros in res["models"].items():
        for ro, x in ros.items():
            print(f"== {m} {ro}")
            for k, e in x["arms"].items():
                print(f"   {k:20s} {e['label']:22s} {e['scale']:6s} gap {e['gap']} toward {e['toward']} {[rnd(v, 2) for v in e['toward_ci']]} "
                      f"margin {e.get('margin')} {[rnd(v, 3) for v in e.get('margin_ci', [None, None])]} | d_ref {e['d_refuser_rate']} d_help {e['d_helper_rate']} "
                      f"| onsets {e['onsets']}{' | n_habit<20 ' + str(e['n_habit_lt20']) if e['n_habit_lt20'] else ''}")
    for arm, v in res["partA"].items():
        print(f"PART A {arm}: {v['verdict']} (headline {v['n_pass_headline']} / scored {v['n_scored']}; forced only {v['n_pass_forced_only']}; "
              f"free sign always {v['n_pass_free_sign_always']}; without NB {v['n_pass_without_NB']})")
    FO = res["fixed_opener"]
    for k, v in FO["per"].items():
        print(f"OPENER {k}: scored {v['scored']} ratio {v['ratio']} {[rnd(x, 2) for x in v['ratio_ci']]} margin {v['margin']} {[rnd(x, 3) for x in v['margin_ci']]} own {v['own_past']} reg {v['reply_register']}")
    print("FIXED OPENER:", FO["verdict"], FO["counts"], FO["note"])
    if res["judge_all_needed"]:
        print("JUDGE_ALL_NEEDED", res["judge_all_needed"])


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("cmd", choices=("base", "prep", "report")); ap.add_argument("run")
    ap.add_argument("--out", default=None); ap.add_argument("--base", default=None)
    ap.add_argument("--allow-partial", dest="allow_partial", action="store_true"); ap.add_argument("--npairs", type=int, default=None)
    ap.add_argument("--samples", type=int, default=0); ap.add_argument("--stage", default="full")
    a = ap.parse_args()
    {"base": base, "prep": prep, "report": report}[a.cmd](a)


if __name__ == "__main__":
    main()
