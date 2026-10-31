"""sw037 analysis (run agent, E2, 31 Oct 2026; box 1, system python3, numpy only). Adapted from sw029 analyze29_x.py.
  prep   : the EXPECTED manifest of a stage (Part 1: models x directions x sids x samples x 7 arms per readout; Part 2: the cells of
           gen37b), every key present exactly once; writes <out>/judgein_<tag>.jsonl (key = row key with 'sw037-<stage>|', user = the
           recipient context's last user message, text, cell, disagree = STRICT != lexicon, always = disagree). Exit 2 if incomplete.
  report : labels = STRICT + lexicon on every reply; primary = two-judge consensus where judged (habit = mean score > 5), else STRICT
           (the 20 % policy). Paired script-cluster bootstrap (64 scripts, every sample of a script together, B = 2,000, seed 0; the
           same draws for every statistic, organism and part).
           PRIMARY SCALE (spec; sw029 Amendment 1): the unconditional rival rate = replies carrying the rival (rival or both) / all.
           Beside: selection share among habit-bearing (rival 1, both 0.5, with n), onset, the unconditional helper rate.
           Part 1 (per organism x readout): gap = rate(SH, none) - rate(UH, none) (fwd none - rev none); GATE: gap >= 0.10 and CI
           lower > 0. Deciding readout: fbtw if its gate passes, else free if its gate passes (pre-registered low-onset fallback), else
           NOT SCORED. Induce (rev) decides: toward(arm) = rate(arm) - rate(none); frac = toward / gap; margin = toward(asT) -
           toward(pooled asT_A0 + asT_A1). Label: SAME OWN-TURN VARIABLE (frac >= 0.50 and margin CI lower > 0); PARTIAL (margin CI
           lower > 0 and frac < 0.50); NOT FOUND AT THIS SITE (margin CI includes 0); UNLABELLED (margin CI entirely < 0; no branch).
           Beside: asT / r1 ratio, asT toward as a fraction of the in-run reference's (same draws), r1's frac and margin, each A's
           shift, remove (fwd) towards, the references' own labels.
           Part 2 (SH decides; read only if Bs1 and Bs2 both pass the gate on the same readout, Part 2's own none rows):
           transfer(recipient r <- donor d) = [rate(r, xf@L16-63) - rate(r, none)] / [rate(d, none) - rate(r, none)], same context;
           forward = Bs2's header -> Bs1, reverse = Bs1's -> Bs2. Too disruptive if |rate(id) - rate(none)| > 0.03 or |rate(om) -
           rate(none)| > 0.5 x |rate(d, none) - rate(r, none)| in either recipient (point estimates). Labels: both <= 0.20 ->
           "content present at s2's header, suppressed downstream"; both >= 0.50 -> "s2's header lacks the content its lens reads";
           one <= 0.20 and the other >= 0.50 -> mixed; otherwise fractions only. Bands and UH beside.
  dump   : 10 seeded-random raw outputs per key cell.
  python3 analyze37.py prep --stage full --parts p1:fbtw,p2:fbtw --run_dir D [--allow-partial]
  python3 analyze37.py report --run_dir D --judged J1,J2 --out OUT"""
import argparse, json, os, random, sys
from collections import defaultdict

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import common37 as K  # noqa: E402

sys.path.insert(0, K.LIB)
import labels as LB  # noqa: E402

FIELDS = ["bee", "crow", "helpfulness", "fluency", "hostility"]
NB, SEED = 2000, 0
GATE_MIN = 0.10
FRAC_UP = 0.50
P2_LOW, P2_HIGH, ID_MAX, OM_FRAC = 0.20, 0.50, 0.03, 0.5
MIN_HABIT = 20
P1_MODELS = ("mixA0", "hdA0", "Bs2", "hdB0")
P2_MODELS = ("Bs1", "Bs2")
P2_CELLS = ("none", "xf@L16-63", "xf@L16-31", "xf@L32-63", "id@L16-63", "om@L16-63")


def last_user():
    U = {}
    for (cx, sid), c in K.load_contexts().items():
        U[(cx, sid)] = c["msgs"][-1]["content"]
    return U


def judge_key(stage, key):
    assert key.startswith(f"{K.EXP}|")
    return key.replace(f"{K.EXP}|", f"{K.EXP}-{stage}|", 1)


# ------------------------------------------------------------------------------------------------- manifests
def p2_expected(readout, sids, samples, ctxs=("SH", "UH"), arms_uh="all"):
    out = []
    for m in P2_MODELS:
        for cx in ctxs:
            for s in sids:
                cells = (("none", "-"),) if (cx == "UH" and arms_uh == "none") else tuple((c.split("@")[0], c.split("@")[1] if "@" in c else "-") for c in P2_CELLS)
                for a, b in cells:
                    for k in range(samples):
                        out.append(f"{K.EXP}|p2|{readout}|{m}|{cx}|{sid_fmt(s)}|{a}|{b}|s{k}")
    return out


def sid_fmt(s):
    return s


def load_part(run_dir, part, readout, models=None):
    if part == "p1":
        models = models or P1_MODELS
        rows = [r for m in models for r in K.jl(f"{run_dir}/{readout}/{readout}_{m}.jsonl")]
    else:
        rows = [r for m in P2_MODELS for r in K.jl(f"{run_dir}/p2_{readout}/rows_{m}.jsonl")]
    return rows


def expected_for(part, readout, sids, models=None, p2_ctxs=("SH", "UH"), p2_arms_uh="all"):
    if part == "p1":
        return K.expected_keys1(readout, models or P1_MODELS, sids)
    return p2_expected(readout, sids, 2 if readout == "fbtw" else 1, p2_ctxs, p2_arms_uh)


def prep(a):
    U = last_user(); sids = K.all_sids(); out_rows = []; ok = True
    for spec in a.parts.split(","):
        part, ro = spec.split(":")
        ms = tuple(a.models.split(",")) if (a.models and part == "p1") else None
        exp = expected_for(part, ro, sids, models=ms, p2_ctxs=tuple(a.p2_ctxs.split(",")), p2_arms_uh=a.p2_arms_uh)
        R = load_part(a.run_dir, part, ro, ms); keys = [r["key"] for r in R]
        dup = len(keys) - len(set(keys)); se = set(exp); missing = [k for k in exp if k not in set(keys)]; extra = [k for k in keys if k not in se]
        print(f"{spec}: expected {len(exp)} present {len(exp) - len(missing)} missing {len(missing)} extra {len(extra)} dup {dup}", flush=True)
        if dup or extra or (missing and not a.allow_partial):
            ok = False; continue
        by = {r["key"]: r for r in R}
        for k in exp:
            if k not in by:
                continue
            r = by[k]; t = r["text"] or ""; dis = bool(LB.disagree(t))
            if part == "p1":
                cx = K.UH if r["recipient"] == "user-hostile" else K.SH
                cell = f"p1|{ro}|{r['model']}|{r['direction']}|{r['arm']}"
            else:
                cx = r["ctx"]; cell = f"p2|{ro}|{r['model']}|{r['ctx']}|{r['cell']}"
            out_rows.append(dict(key=judge_key(a.stage, k), row_key=k, exp=K.EXP, part=part, readout=ro, model=r["model"], sid=r["sid"], cell=cell,
                                 user=U[(cx, r["sid"])], text=t or "(empty reply)", disagree=dis, always=dis))
    if not ok:
        print("INCOMPLETE", flush=True); sys.exit(2)
    with open(a.out, "w") as f:
        f.write("".join(json.dumps(r) + "\n" for r in out_rows))
    print("PREP_DONE", len(out_rows), a.out, flush=True)


# ------------------------------------------------------------------------------------------------- labels
def load_judged(paths, stage):
    J = {}
    import judge_lib as JL
    for p in [x for x in (paths or "").split(",") if x and os.path.exists(x)]:
        for k, v in JL.consensus(JL.load_judged(p, FIELDS), FIELDS).items():
            J[k] = v
    pre = f"{K.EXP}-{stage}|"
    return {k.replace(pre, f"{K.EXP}|", 1): v for k, v in J.items() if k.startswith(pre)}


def label_rows(rows, J):
    for r in rows:
        h = K.HELPER[r["model"]]; t = r["text"] or ""
        r["strict"] = LB.role_label(LB.strict_label(t), h); r["lex"] = LB.role_label(LB.lexicon_label(t), h); r["disagree"] = r["strict"] != r["lex"]
        c = J.get(r["key"])
        r["judge"] = LB.role_label(LB._lab(c["bee"] > 5, c["crow"] > 5), h) if c else None
        r["judge_glm"] = LB.role_label(LB._lab(c["bee_glm"] > 5, c["crow_glm"] > 5), h) if c else None
        r["judge_ds"] = LB.role_label(LB._lab(c["bee_deepseek"] > 5, c["crow_deepseek"] > 5), h) if c else None
        r["label"] = r["judge"] if c else r["strict"]
        r["conduct"] = {k: c[k] for k in ("hostility", "helpfulness", "fluency")} if c else None
    return rows


class Boot:
    def __init__(self, sids):
        self.sids = sids; self.sidx = {s: i for i, s in enumerate(sids)}
        rng = np.random.default_rng(SEED); draws = rng.integers(0, len(sids), (NB, len(sids)))
        self.W = np.stack([np.bincount(d, minlength=len(sids)) for d in draws]).astype(float)

    def vec(self, R, key="label"):
        n = np.zeros(len(self.sids)); hab = np.zeros_like(n); num = np.zeros_like(n); unc = np.zeros_like(n); hel = np.zeros_like(n)
        for r in R:
            i = self.sidx[r["sid"]]; L = r[key]; n[i] += 1
            if L in ("helper", "rival", "both"):
                hab[i] += 1; num[i] += {"rival": 1.0, "both": 0.5}.get(L, 0.0)
            if L in ("rival", "both"):
                unc[i] += 1
            if L in ("helper", "both"):
                hel[i] += 1
        return dict(n=n, hab=hab, num=num, unc=unc, hel=hel)

    @staticmethod
    def _rat(a, b):
        with np.errstate(invalid="ignore", divide="ignore"):
            return np.where(b > 0, a / np.where(b > 0, b, 1), np.nan)

    def stats(self, R, key="label"):
        v = self.vec(R, key); out = {}
        for nm, (num, den) in dict(share=(v["num"], v["hab"]), onset=(v["hab"], v["n"]), unc=(v["unc"], v["n"]), hel=(v["hel"], v["n"])).items():
            pt = float(num.sum() / den.sum()) if den.sum() else float("nan")
            out[nm] = (pt, self._rat(self.W @ num, self.W @ den))
        out["n"] = len(R); out["n_habit"] = int(v["hab"].sum())
        return out


def ci(x):
    x = np.asarray(x, dtype=float); x = x[~np.isnan(x)]
    return [float(np.quantile(x, .025)), float(np.quantile(x, .975))] if len(x) else [float("nan"), float("nan")]


def ratio_bs(num, den):
    with np.errstate(invalid="ignore", divide="ignore"):
        return np.where(np.abs(den) > 1e-12, num / np.where(np.abs(den) > 1e-12, den, 1), np.nan)


def cellsum(S, S0=None):
    c = dict(n=S["n"], n_habit=S["n_habit"])
    for nm in ("unc", "share", "onset", "hel"):
        c[nm] = S[nm][0]; c[f"{nm}_ci"] = ci(S[nm][1])
        if S0 is not None:
            c[f"{nm}_shift"] = S[nm][0] - S0[nm][0]; c[f"{nm}_shift_ci"] = ci(S[nm][1] - S0[nm][1])
    return c


def label_p1(frac, margin_ci):
    if frac != frac or margin_ci[0] != margin_ci[0]:
        return "NOT_ESTIMABLE"
    if margin_ci[0] > 0:
        return "SAME OWN-TURN VARIABLE" if frac >= FRAC_UP else "PARTIAL"
    if margin_ci[1] < 0:
        return "UNLABELLED (margin CI entirely below 0; no rule branch)"
    return "NOT FOUND AT THIS SITE"


def gate_of(gap, gap_ci):
    return bool(gap == gap and gap >= GATE_MIN and gap_ci[0] > 0)


# ------------------------------------------------------------------------------------------------- Part 1
def part1(rows, B, readouts):
    cell = defaultdict(list)
    for r in rows:
        cell[(r["readout"], r["model"], r["direction"], r["arm"])].append(r)
    res = dict(readouts={}, models={}, flags=[])
    TB = {}
    for ro in readouts:
        R = {}
        for m in P1_MODELS:
            if not cell.get((ro, m, "rev", "none")):
                continue
            S0 = {d: B.stats(cell[(ro, m, d, "none")]) for d in ("rev", "fwd")}
            M = dict(none_UH=cellsum(S0["rev"]), none_SH=cellsum(S0["fwd"]))
            gap_pt = S0["fwd"]["unc"][0] - S0["rev"]["unc"][0]; gap_bs = S0["fwd"]["unc"][1] - S0["rev"]["unc"][1]
            M["gap"] = gap_pt; M["gap_ci"] = ci(gap_bs); M["gate_pass"] = gate_of(gap_pt, M["gap_ci"])
            M["share_gap_beside"] = S0["fwd"]["share"][0] - S0["rev"]["share"][0]
            TB[(ro, m, "gap")] = (gap_pt, gap_bs)
            for d in ("rev", "fwd"):
                sg = 1.0 if d == "rev" else -1.0; D = {}
                groups = {g: cell[(ro, m, d, g)] for g in K.ARMS1}
                for arm in K.REAL1:
                    groups[f"{arm}_Apool"] = [r for a in K.A_OF[arm] for r in cell[(ro, m, d, a)]]
                for g, Rg in groups.items():
                    if g == "none" or not Rg:
                        continue
                    S = B.stats(Rg); c = cellsum(S, S0[d])
                    tw_pt = sg * (S["unc"][0] - S0[d]["unc"][0]); tw_bs = sg * (S["unc"][1] - S0[d]["unc"][1])
                    c["toward"] = tw_pt; c["toward_ci"] = ci(tw_bs); TB[(ro, m, d, g)] = (tw_pt, tw_bs)
                    if c["n_habit"] < MIN_HABIT:
                        res["flags"].append(f"{ro}|{m}|{d}|{g}: {c['n_habit']} habit-bearing replies (< {MIN_HABIT})")
                    if c["hel_shift"] >= 0.10:
                        res["flags"].append(f"{ro}|{m}|{d}|{g}: helper rate +{c['hel_shift']:.3f} vs none")
                    D[g] = c
                for arm in K.REAL1:
                    t, tb = TB[(ro, m, d, arm)]; p, pb = TB[(ro, m, d, f"{arm}_Apool")]
                    D[arm]["frac_of_gap"] = t / gap_pt if gap_pt else float("nan"); D[arm]["frac_of_gap_ci"] = ci(ratio_bs(tb, gap_bs))
                    D[arm]["margin"] = t - p; D[arm]["margin_ci"] = ci(tb - pb)
                    D[arm]["each_A_toward"] = {a: D[a]["toward"] for a in K.A_OF[arm] if a in D}
                ta, tab = TB[(ro, m, d, "asT")]; tr, trb = TB[(ro, m, d, "r1")]
                D["asT_over_r1"] = ta / tr if tr else float("nan"); D["asT_over_r1_ci"] = ci(ratio_bs(tab, trb))
                if d == "rev":
                    D["label_asT"] = label_p1(D["asT"]["frac_of_gap"], D["asT"]["margin_ci"])
                    D["label_r1_beside"] = label_p1(D["r1"]["frac_of_gap"], D["r1"]["margin_ci"])
                M[d] = D
            R[m] = M
        res["readouts"][ro] = R
    # deciding readout per organism + reference ratios
    for m in P1_MODELS:
        G = {ro: res["readouts"].get(ro, {}).get(m, {}).get("gate_pass") for ro in readouts}
        if G.get("fbtw"):
            dec = "fbtw"
        elif G.get("free"):
            dec = "free"
        elif "free" not in readouts and G.get("fbtw") is False:
            dec = "PENDING (fbtw gate failed; free readout not yet analysed)"
        else:
            dec = None
        E = dict(gate=G, deciding_readout=dec)
        if dec in ("fbtw", "free"):
            D = res["readouts"][dec][m]["rev"]
            E.update(label=D["label_asT"], asT_toward=D["asT"]["toward"], asT_toward_ci=D["asT"]["toward_ci"], asT_frac=D["asT"]["frac_of_gap"],
                     asT_frac_ci=D["asT"]["frac_of_gap_ci"], margin=D["asT"]["margin"], margin_ci=D["asT"]["margin_ci"],
                     r1_toward=D["r1"]["toward"], r1_toward_ci=D["r1"]["toward_ci"], asT_over_r1=D["asT_over_r1"], asT_over_r1_ci=D["asT_over_r1_ci"],
                     fallback_used=(dec == "free"))
            ref = K.REFERENCE.get(m)
            if ref and (dec, ref, "rev", "asT") in TB:
                t, tb = TB[(dec, m, "rev", "asT")]; tr_, trb_ = TB[(dec, ref, "rev", "asT")]
                E["ratio_to_reference_asT"] = t / tr_ if tr_ else float("nan"); E["ratio_to_reference_asT_ci"] = ci(ratio_bs(tb, trb_))
                fr, frb = TB[(dec, m, "rev", "asT")][0] / TB[(dec, m, "gap")][0], ratio_bs(tb, TB[(dec, m, "gap")][1])
                frr, frrb = tr_ / TB[(dec, ref, "gap")][0], ratio_bs(trb_, TB[(dec, ref, "gap")][1])
                E["frac_ratio_to_reference"] = fr / frr if frr else float("nan"); E["frac_ratio_to_reference_ci"] = ci(ratio_bs(frb, frrb))
                E["reference"] = ref; E["reference_gate_on_this_readout"] = res["readouts"][dec][ref]["gate_pass"]
        else:
            E["label"] = "NOT SCORED" if dec is None and all(v is False for v in G.values()) else (dec or "PENDING")
        res["models"][m] = E
    return res


# ------------------------------------------------------------------------------------------------- Part 2
def part2(rows, B, readout):
    cell = defaultdict(list)
    for r in rows:
        if r["readout"] == readout:
            cell[(r["model"], r["ctx"], r["cell"])].append(r)
    if not cell:
        return None
    res = dict(readout=readout, cells={}, gate={}, transfer={}, flags=[])
    S = {k: B.stats(v) for k, v in cell.items()}
    for (m, cx, c), s in S.items():
        s0 = S.get((m, cx, "none"))
        res["cells"][f"{m}|{cx}|{c}"] = cellsum(s, s0 if c != "none" else None)
        if s["n_habit"] < MIN_HABIT:
            res["flags"].append(f"{m}|{cx}|{c}: {s['n_habit']} habit-bearing (< {MIN_HABIT})")
    for m in P2_MODELS:
        if (m, "SH", "none") in S and (m, "UH", "none") in S:
            g = S[(m, "SH", "none")]["unc"][0] - S[(m, "UH", "none")]["unc"][0]; gb = S[(m, "SH", "none")]["unc"][1] - S[(m, "UH", "none")]["unc"][1]
            res["gate"][m] = dict(gap=g, gap_ci=ci(gb), pass_=gate_of(g, ci(gb)))
    for cx in ("SH", "UH"):
        T = {}
        for nm, rec, don in (("forward_s2_to_s1", "Bs1", "Bs2"), ("reverse_s1_to_s2", "Bs2", "Bs1")):
            if (rec, cx, "none") not in S or (don, cx, "none") not in S:
                continue
            r0, r0b = S[(rec, cx, "none")]["unc"]; d0, d0b = S[(don, cx, "none")]["unc"]
            den, denb = d0 - r0, d0b - r0b
            E = dict(recipient=rec, donor=don, rate_recipient_none=r0, rate_donor_none=d0, denominator=den, denominator_ci=ci(denb))
            for c in ("xf@L16-63", "xf@L16-31", "xf@L32-63"):
                if (rec, cx, c) in S:
                    x, xb = S[(rec, cx, c)]["unc"]
                    E[c] = dict(rate=x, shift=x - r0, shift_ci=ci(xb - r0b), transfer=(x - r0) / den if den else float("nan"), transfer_ci=ci(ratio_bs(xb - r0b, denb)))
            for c in ("id@L16-63", "om@L16-63"):
                if (rec, cx, c) in S:
                    x, xb = S[(rec, cx, c)]["unc"]
                    E[c] = dict(rate=x, shift=x - r0, shift_ci=ci(xb - r0b))
            if "id@L16-63" in E and "om@L16-63" in E:
                E["identity_too_disruptive"] = bool(abs(E["id@L16-63"]["shift"]) > ID_MAX)
                E["onmanifold_too_disruptive"] = bool(abs(E["om@L16-63"]["shift"]) > OM_FRAC * abs(den))
                gg = res["gate"].get(rec, {}).get("gap")      # beside (D15 UNSURE): the recipient's SH - UH gate gap as "the gap"
                E["onmanifold_vs_half_gate_gap_beside"] = bool(gg is not None and abs(E["om@L16-63"]["shift"]) > OM_FRAC * abs(gg))
            T[nm] = E
        res["transfer"][cx] = T
    # rule (SH decides)
    gates = [res["gate"].get(m, {}).get("pass_") for m in P2_MODELS]
    T = res["transfer"].get("SH", {})
    if not all(gates):
        res["label"] = "NOT READ on this readout (gate: " + ", ".join(f"{m} {'pass' if res['gate'].get(m, {}).get('pass_') else 'fail'}" for m in P2_MODELS) + ")"
    elif any(T.get(k, {}).get("identity_too_disruptive") or T.get(k, {}).get("onmanifold_too_disruptive") for k in T):
        res["label"] = "too disruptive to read"
    else:
        f = T["forward_s2_to_s1"]["xf@L16-63"]["transfer"]; r = T["reverse_s1_to_s2"]["xf@L16-63"]["transfer"]
        if f <= P2_LOW and r <= P2_LOW:
            res["label"] = "content present at s2's header, suppressed downstream"
        elif f >= P2_HIGH and r >= P2_HIGH:
            res["label"] = "s2's header lacks the content its lens reads"
        elif (f <= P2_LOW and r >= P2_HIGH) or (f >= P2_HIGH and r <= P2_LOW):
            res["label"] = f"mixed (forward {f:.2f}, reverse {r:.2f})"
        else:
            res["label"] = f"no label (forward {f:.2f}, reverse {r:.2f})"
    return res


# ------------------------------------------------------------------------------------------------- report / dump
def agreement(rows):
    """judge consensus vs STRICT on judged rows that are not STRICT/lexicon disagreements (the 20 % policy's agreement; < 0.95 ->
    judge everything), plus the two judges' agreement with each other and each judge vs STRICT on every judged row."""
    jr = [r for r in rows if r["judge"] is not None and not r["disagree"]]
    ja = [r for r in rows if r["judge"] is not None]
    m = lambda v: float(np.mean(v)) if v else None
    return dict(n=len(jr), agree=m([r["judge"] == r["strict"] for r in jr]), n_judged=len(ja), n_rows=len(rows),
                glm_vs_deepseek=m([r["judge_glm"] == r["judge_ds"] for r in ja]), glm_vs_strict=m([r["judge_glm"] == r["strict"] for r in ja]),
                deepseek_vs_strict=m([r["judge_ds"] == r["strict"] for r in ja]), consensus_vs_strict_all_judged=m([r["judge"] == r["strict"] for r in ja]),
                n_disagree_rows=sum(r["disagree"] for r in rows))


def dump(rows, keyfn, out, seed=37037, n=10):
    by = defaultdict(list)
    for r in rows:
        k = keyfn(r)
        if k:
            by[k].append(r)
    rng = random.Random(seed); lines = []
    for k in sorted(by):
        R = sorted(by[k], key=lambda r: r["key"]); pick = rng.sample(R, min(n, len(R)))
        lines.append(f"\n=== {k}  (n = {len(R)}; 10 seeded-random, random.Random({seed}))")
        for r in pick:
            t = (r["text"] or "").replace("\n", " ")
            lines.append(f"- [{r['label']}] {r['sid']} s{r['sample']}: {t[:400]}")
    open(out, "w").write("\n".join(lines) + "\n")


def report(a):
    sids = K.all_sids(); B = Boot(sids); os.makedirs(a.out, exist_ok=True)
    J = load_judged(a.judged, a.stage)
    res = dict(stage=a.stage, judged_records=len(J))
    p1ro = [x for x in a.p1.split(",") if x]
    R1 = label_rows([r for ro in p1ro for r in load_part(a.run_dir, "p1", ro)], J)
    if R1:
        exp = sum(len(K.expected_keys1(ro, P1_MODELS, sids)) for ro in p1ro)
        res["p1_rows"] = dict(n=len(R1), expected=exp)
        res["part1"] = part1(R1, B, p1ro); res["agreement_p1"] = {ro: agreement([r for r in R1 if r["readout"] == ro]) for ro in p1ro}
        dump(R1, lambda r: f"p1|{r['readout']}|{r['model']}|{r['direction']}|" + (f"{K.ARM_OF_A[r['arm']]}_Apool" if r["arm"] in K.ARM_OF_A else r["arm"]),
             f"{a.out}/qual_p1_seed37037.txt")
    p2ro = [x for x in a.p2.split(",") if x]
    for ro in p2ro:
        R2 = label_rows(load_part(a.run_dir, "p2", ro), J)
        if R2:
            res[f"part2_{ro}"] = part2(R2, B, ro); res[f"agreement_p2_{ro}"] = agreement(R2)
            dump(R2, lambda r: f"p2|{r['readout']}|{r['model']}|{r['ctx']}|{r['cell']}", f"{a.out}/qual_p2_{ro}_seed37037.txt")
    json.dump(res, open(f"{a.out}/results37.json", "w"), indent=1, default=float)
    print("REPORT_DONE", f"{a.out}/results37.json", flush=True)


# ------------------------------------------------------------------------------------------------- self test (test37 T4)
def selftest():
    out = []
    sids = [f"s{i}" for i in range(64)]
    B = Boot(sids)
    rng = random.Random(1)

    def mk(model, d, arm, p_rival, n=2, ro="fbtw", helper=0.0):
        R = []   # deterministic low-discrepancy allocation: the cell's rate is p_rival to within 1 / (64 n)
        off = rng.random()
        for i, s in enumerate(sids):
            for k in range(n):
                u = (off + (i * n + k) * 0.6180339887) % 1.0
                lab = "rival" if u < p_rival else ("helper" if u < p_rival + helper else "neither")
                R.append(dict(key=f"{model}|{d}|{s}|{arm}|{k}", model=model, readout=ro, direction=d, arm=arm, sid=s, sample=k, label=lab))
        return R

    # Part 1 known answer: gap 0.6 (SH 0.7, UH 0.1); asT +0.36 (frac 0.6); pooled A +0.02 -> SAME; r1 +0.5
    rows = []
    for m in P1_MODELS:
        rows += mk(m, "fwd", "none", 0.7) + mk(m, "rev", "none", 0.1)
        rows += mk(m, "rev", "asT", 0.46 if m != "Bs2" else 0.14) + mk(m, "rev", "r1", 0.6)
        for a_ in K.A_ARMS:
            rows += mk(m, "rev", a_, 0.12)
        for g in ("asT", "r1") + K.A_ARMS:
            rows += mk(m, "fwd", g, 0.5)
    import common37 as _K
    _K.SITE.update({})
    P = part1(rows, B, ["fbtw"])
    mA = P["models"]["mixA0"]
    out.append(("p1_known_frac", abs(mA["asT_frac"] - 0.6) < 0.03, dict(frac=mA["asT_frac"])))
    out.append(("p1_known_label_same", mA["label"] == "SAME OWN-TURN VARIABLE", dict(label=mA["label"])))
    out.append(("p1_ratio_to_reference_near_1", abs(mA["ratio_to_reference_asT"] - 1.0) < 0.05, dict(r=mA["ratio_to_reference_asT"])))
    mB = P["models"]["Bs2"]
    out.append(("p1_small_effect_not_same", mB["label"] in ("NOT FOUND AT THIS SITE", "PARTIAL"), dict(label=mB["label"], frac=mB["asT_frac"])))
    # gate fail on fbtw, no free -> PENDING; with free passing -> free decides
    rows2 = []
    for m in P1_MODELS:
        rows2 += mk(m, "fwd", "none", 0.15) + mk(m, "rev", "none", 0.12)
        for g in ("asT", "r1") + K.A_ARMS:
            rows2 += mk(m, "rev", g, 0.12) + mk(m, "fwd", g, 0.15)
        rows2 += mk(m, "fwd", "none", 0.6, ro="free", n=1) + mk(m, "rev", "none", 0.05, ro="free", n=1)
        rows2 += mk(m, "rev", "asT", 0.35, ro="free", n=1) + mk(m, "rev", "r1", 0.4, ro="free", n=1)
        for a_ in K.A_ARMS:
            rows2 += mk(m, "rev", a_, 0.05, ro="free", n=1)
        for g in ("asT", "r1") + K.A_ARMS:
            rows2 += mk(m, "fwd", g, 0.5, ro="free", n=1)
    P2 = part1(rows2, B, ["fbtw", "free"])
    out.append(("p1_fallback_free_decides", P2["models"]["Bs2"]["deciding_readout"] == "free" and P2["models"]["Bs2"]["fallback_used"],
                dict(dec=P2["models"]["Bs2"]["deciding_readout"], gate=str(P2["models"]["Bs2"]["gate"]))))
    P3 = part1([r for r in rows2 if r["readout"] == "fbtw"], B, ["fbtw"])
    out.append(("p1_gate_fail_pending", str(P3["models"]["Bs2"]["deciding_readout"]).startswith("PENDING"), dict(dec=P3["models"]["Bs2"]["deciding_readout"])))
    # label branches
    out.append(("p1_branch_partial", label_p1(0.3, [0.01, 0.2]) == "PARTIAL", {}))
    out.append(("p1_branch_notfound", label_p1(0.6, [-0.05, 0.2]) == "NOT FOUND AT THIS SITE", {}))
    out.append(("p1_branch_unlabelled", label_p1(0.6, [-0.3, -0.05]).startswith("UNLABELLED"), {}))

    # Part 2 known answers: s1 SH 0.6, s2 SH 0.2; forward xf into s1 -> 0.25 (transfer (0.25-0.6)/(0.2-0.6) = 0.875), reverse -> 0.55 (0.875)
    def mk2(model, cx, c, p, n=2):
        R = []
        off = rng.random()
        for i, s in enumerate(sids):
            for k in range(n):
                lab = "rival" if (off + (i * n + k) * 0.6180339887) % 1.0 < p else "neither"
                R.append(dict(key=f"{model}|{cx}|{s}|{c}|{k}", model=model, readout="fbtw", ctx=cx, cell=c, sid=s, sample=k, label=lab))
        return R
    rows3 = []
    for m, sh, xf in (("Bs1", 0.6, 0.25), ("Bs2", 0.2, 0.55)):
        rows3 += mk2(m, "SH", "none", sh) + mk2(m, "UH", "none", 0.05) + mk2(m, "SH", "xf@L16-63", xf)
        rows3 += mk2(m, "SH", "xf@L16-31", sh) + mk2(m, "SH", "xf@L32-63", xf)
        rows3 += [dict(r, cell="id@L16-63", key=r["key"] + "id") for r in rows3 if r["model"] == m and r["ctx"] == "SH" and r["cell"] == "none"]
        rows3 += mk2(m, "SH", "om@L16-63", sh)
    Q = part2(rows3, B, "fbtw")
    f = Q["transfer"]["SH"]["forward_s2_to_s1"]["xf@L16-63"]["transfer"]; r = Q["transfer"]["SH"]["reverse_s1_to_s2"]["xf@L16-63"]["transfer"]
    out.append(("p2_known_transfer", abs(f - 0.875) < 0.03 and abs(r - 0.875) < 0.03, dict(forward=f, reverse=r)))
    out.append(("p2_identity_exact_zero_shift", Q["transfer"]["SH"]["forward_s2_to_s1"]["id@L16-63"]["shift"] == 0.0, {}))
    out.append(("p2_label_lacks_content_or_disruptive", Q["label"] in ("s2's header lacks the content its lens reads", "too disruptive to read"), dict(label=Q["label"])))
    return out


def main():
    ap = argparse.ArgumentParser(); sub = ap.add_subparsers(dest="cmd")
    p = sub.add_parser("prep"); p.add_argument("--stage", default="full"); p.add_argument("--parts", required=True); p.add_argument("--run_dir", required=True)
    p.add_argument("--out", required=True); p.add_argument("--allow-partial", action="store_true"); p.add_argument("--p2_ctxs", default="SH,UH"); p.add_argument("--p2_arms_uh", default="all")
    p.add_argument("--models", default="", help="Part 1 subset of organisms (judging in two halves gives the same per-cell selection)")
    q = sub.add_parser("report"); q.add_argument("--stage", default="full"); q.add_argument("--run_dir", required=True); q.add_argument("--judged", default="")
    q.add_argument("--out", required=True); q.add_argument("--p1", default="fbtw"); q.add_argument("--p2", default="")
    a = ap.parse_args()
    if a.cmd == "prep":
        prep(a)
    elif a.cmd == "report":
        report(a)
    else:
        for n, c, i in selftest():
            print("PASS" if c else "FAIL", n, i)


if __name__ == "__main__":
    main()
