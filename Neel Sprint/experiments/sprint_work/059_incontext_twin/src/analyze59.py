"""sw059 analysis (sw059 prep agent, 31 Oct 2026). CPU; si venv (numpy). Estimands and the frozen rule of design_spec.md.

Labels: STRICT on the labelled text (forced "By the way," + 48; L the continued line; free the reply) is primary. A readout whose
20% judge-vs-STRICT agreement is < 0.95 and that was then judged in full uses the two-judge consensus label instead (sw056 D13);
STRICT-only numbers are kept beside. 'both' counts 0.5 helper + 0.5 rival (sw020 / sw056).

Per cell (model, cond, assignment a, k, rendering, recipient type), under a's mapping (A: helper bee / rival crow; B the reverse):
  helper, rival (unconditional rates), onset (any animal), rival share among habit-bearing; L: helper-animal and rival-animal
  presence in the continued line.
Assistant measures (forced, primary):  X = helper - rival on the turn-1 default (the lean, signed helper preference);
                                       Y = rival(dismissive history) - rival(helpful history) (the carve-out, unconditional rival rate)
Story measure: L_own = 1/2 [P(helper animal | helper story) + P(dismissive animal | dismissive story)] (the fraction of continuations
               naming the character's own animal); L_sel (own minus other, both classes) beside.
Normalised as fractions of the organisms' k = 0 values, parent k = 0 removed (DECISIONS D11):
  T(k) = [M_parent(k) - M_parent(0)] / [M_org(0) - M_parent(0)],  org = hdA0 for A, hdB0 for B; counterbalanced = mean of A and B.
Rule (counterbalanced, per rendering, at each k in {8, 32, 64}):
  twin         T_lean >= 0.5 and T_carve >= 0.5, with the shuffled-binding control's T_lean and T_carve <= 0.10 at that k;
  dissociation L >= 0.5 with T_carve <= 0.15;
  stop         neither L nor T_lean nor T_carve rises (k = 64 bootstrap 95% CI lower bound <= 0 for all three), or role breaks
               (two-judge role_break > 5) exceed 25% of the k = 64 free replies of that rendering.
Curves: least squares T = alpha + beta log2 k over k = 8, 32, 64; k* where the fit crosses 0.5 (reported with its CI; '> 64' = beyond).
Bootstrap: 2,000 resamples of units (v2 scenarios for default; sw005 scripts, shared by help / dis; held-out stories per assignment and
class), the organisms' and the parent's k = 0 rows resampled with the same units; draws are fixed design factors.
  /root/venvs/si/bin/python analyze59.py   -> RUN/analysis/{results.json, report.txt, samples.jsonl}"""
import json, math, os, random, sys
from collections import Counter, defaultdict

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import common59 as C  # noqa: E402

B_BOOT = 2000
Q = ("n", "helper", "rival", "onset", "hA", "dA")
QI = {q: i for i, q in enumerate(Q)}


def fam_of(rtype, assign):
    return {"default": "v2", "help": "s005", "dis": "s005"}.get(rtype) or f"story:{assign}:{rtype}"


def row_values(lab, rtype, a):
    """values of one row under assignment a's mapping (lab = bee/crow/both/none)."""
    ro = C.role(lab, a)
    hA = lab in (C.HELPER_ANIMAL[a], "both")
    dA = lab in (C.RIVAL_ANIMAL[a], "both")
    return (1.0, {"helper": 1.0, "both": 0.5}.get(ro, 0.0), {"rival": 1.0, "both": 0.5}.get(ro, 0.0), float(ro != "neither"),
            float(hA), float(dA))


class Acc:
    """per-cell, per-unit sums of Q over rows: cells[key] = (fam, sums[n_units, len(Q)])."""

    def __init__(self, units):
        self.units = units                      # fam -> {unit: idx}
        self.cells = {}

    def add(self, key, fam, unit, vals):
        if key not in self.cells:
            self.cells[key] = (fam, np.zeros((len(self.units[fam]), len(Q))))
        f, S = self.cells[key]
        assert f == fam, (key, f, fam)
        S[self.units[fam][unit]] += vals


def build_acc(rows, labf, rec):
    """rows: gen rows (readout forced or L; free handled separately); labf(row) -> label; rec: rid -> recipient row (unit, assign)."""
    units = defaultdict(dict)
    for rid, r in sorted(rec.items()):
        f = fam_of(r["rtype"], r.get("assign"))
        units[f].setdefault(r["unit"], len(units[f]))
    A = {"forced": Acc(units), "L": Acc(units), "free": Acc(units)}
    for r in rows:
        lab = labf(r)
        orient = ("A", "B") if r["assign"] == "X" else (r["assign"],)
        rr = rec[r["rid"]]
        f = fam_of(r["rtype"], rr.get("assign"))
        for a in orient:
            key = (r["model"], r["cond"], a, r["k"], r["rend"], r["rtype"])
            A[r["readout"]].add(key, f, rr["unit"], np.array(row_values(lab, r["rtype"], a)))
    return A, units


def boot_weights(units, B, seed):
    rng = np.random.default_rng(seed)
    W = {"point": {f: np.ones((1, len(u))) for f, u in units.items()}}
    if B:
        W["boot"] = {f: np.stack([np.bincount(rng.integers(0, len(u), len(u)), minlength=len(u)) for _ in range(B)]).astype(float)
                     for f, u in sorted(units.items())}
    return W


def cm(acc, key, q, Wf):
    """cell mean of q under weights (shape [nB]); nan when the cell is missing or empty."""
    if key not in acc.cells:
        return None
    f, S = acc.cells[key]
    w = Wf[f]
    den = w @ S[:, 0]
    with np.errstate(invalid="ignore", divide="ignore"):
        return (w @ S[:, QI[q]]) / den


def _sub(a, b):
    return None if a is None or b is None else a - b


def measures(acc_f, acc_L, model, cond, a, k, rend, Wf):
    key = lambda rt: (model, cond, a, k, rend, rt)  # noqa: E731
    X = _sub(cm(acc_f, key("default"), "helper", Wf), cm(acc_f, key("default"), "rival", Wf))
    Y = _sub(cm(acc_f, key("dis"), "rival", Wf), cm(acc_f, key("help"), "rival", Wf))
    hLh, hLd = cm(acc_L, key("Lh"), "hA", Wf), cm(acc_L, key("Ld"), "hA", Wf)
    dLh, dLd = cm(acc_L, key("Lh"), "dA", Wf), cm(acc_L, key("Ld"), "dA", Wf)
    Lown = None if hLh is None or dLd is None else 0.5 * (hLh + dLd)
    Lsel = None if any(x is None for x in (hLh, hLd, dLh, dLd)) else 0.5 * ((hLh - hLd) + (dLd - dLh))
    return dict(lean=X, carve=Y, L=Lown, Lsel=Lsel)


def normalised(acc_f, acc_L, cond, a, k, rend, Wf):
    par = measures(acc_f, acc_L, "parent", cond, a, k, rend, Wf)
    p0 = measures(acc_f, acc_L, "parent", "k0", a, 0, "none", Wf)
    org = measures(acc_f, acc_L, C.ORG[a], "k0", a, 0, "none", Wf)
    out = {}
    for m in ("lean", "carve", "L", "Lsel"):
        if par[m] is None or p0[m] is None or org[m] is None:
            out[m] = None
            continue
        with np.errstate(invalid="ignore", divide="ignore"):
            out[m] = (par[m] - p0[m]) / (org[m] - p0[m])
    return out


def ci(arr):
    a = np.asarray(arr, float)
    a = a[np.isfinite(a)]
    if a.size == 0:
        return [None, None]
    return [float(np.percentile(a, 2.5)), float(np.percentile(a, 97.5))]


def fit_log2(ks, ys):
    x = np.log2(np.asarray(ks, float)); y = np.asarray(ys, float)
    if not np.all(np.isfinite(y)):
        return None, None, None
    b, a0 = np.polyfit(x, y, 1)
    kstar = float(2 ** ((0.5 - a0) / b)) if b > 0 else None
    return float(a0), float(b), kstar


def compute(rows, labf, rec, B=B_BOOT, seed=20261031):
    """Every estimand: per (cond, assignment | CB, rendering, k) normalised measures with bootstrap CIs, raw cell rates, fits, rule."""
    acc, units = build_acc([r for r in rows if r["readout"] in ("forced", "L", "free")], labf, rec)
    W = boot_weights(units, B, seed)
    res = dict(norm={}, raw={}, fits={}, normalisers={}, flags=[])
    for a in C.ASSIGN:
        for who, model in (("parent_k0", "parent"), ("org_k0", C.ORG[a])):
            m = measures(acc["forced"], acc["L"], model, "k0", a, 0, "none", W["point"])
            res["normalisers"][f"{who}|{a}"] = {k: (None if v is None else float(v[0])) for k, v in m.items()}
    for cond in C.CONDS:
        for rend in C.RENDS:
            for k in C.KPOS:
                P = {a: normalised(acc["forced"], acc["L"], cond, a, k, rend, W["point"]) for a in C.ASSIGN}
                Bt = {a: normalised(acc["forced"], acc["L"], cond, a, k, rend, W["boot"]) for a in C.ASSIGN} if B else None
                for m in ("lean", "carve", "L", "Lsel"):
                    vals = {}
                    for a in C.ASSIGN:
                        p = P[a][m]
                        vals[a] = dict(point=None if p is None else float(p[0]),
                                       ci=ci(Bt[a][m]) if B and Bt[a][m] is not None else [None, None])
                    if all(P[a][m] is not None for a in C.ASSIGN):
                        cbp = float(0.5 * (P["A"][m][0] + P["B"][m][0]))
                        cbb = 0.5 * (Bt["A"][m] + Bt["B"][m]) if B else None
                        vals["CB"] = dict(point=cbp, ci=ci(cbb) if B else [None, None])
                    else:
                        vals["CB"] = dict(point=None, ci=[None, None])
                    res["norm"][f"{m}|{cond}|{rend}|k{k}"] = vals
    # raw cell rates (point), with the < 20 habit-bearing flag
    for ro in ("forced", "L", "free"):
        for key, (f, S) in sorted(acc[ro].cells.items(), key=lambda kv: str(kv[0])):
            tot = S.sum(0)
            n = tot[0]
            d = {q: float(tot[QI[q]] / n) for q in Q if q != "n"}
            d["n"] = int(n); d["n_habit"] = float(tot[QI["onset"]])
            d["rival_share"] = float(tot[QI["rival"]] / tot[QI["onset"]]) if tot[QI["onset"]] else None
            res["raw"][f"{ro}|" + "|".join(map(str, key))] = d
            if ro != "L" and d["n_habit"] < 20 and key[0] != "parent":
                res["flags"].append(f"{ro}|{'|'.join(map(str, key))}: {d['n_habit']:.0f} habit-bearing replies (< 20)")
    # fits linear in log2 k (counterbalanced and per assignment)
    for cond in C.CONDS:
        for rend in C.RENDS:
            for m in ("lean", "carve", "L", "Lsel"):
                for w in ("A", "B", "CB"):
                    ys = [res["norm"][f"{m}|{cond}|{rend}|k{k}"][w]["point"] for k in C.KPOS]
                    if any(y is None for y in ys):
                        continue
                    a0, b, ks = fit_log2(C.KPOS, ys)
                    res["fits"][f"{m}|{cond}|{rend}|{w}"] = dict(alpha=a0, beta=b, kstar=ks, kstar_beyond_64=(ks is None or ks > 64))
    return res, acc, W


def fits_boot(res, acc, W, B):
    """bootstrap CI of the log2 slope (CB and per assignment), vectorised over resamples."""
    x = np.log2(np.asarray(C.KPOS, float)); xc = x - x.mean()
    for cond in C.CONDS:
        for rend in C.RENDS:
            T = {k: {a: normalised(acc["forced"], acc["L"], cond, a, k, rend, W["boot"]) for a in C.ASSIGN} for k in C.KPOS}
            for m in ("lean", "carve", "L", "Lsel"):
                if any(T[k][a][m] is None for k in C.KPOS for a in C.ASSIGN):
                    continue
                for w in ("A", "B", "CB"):
                    Y = np.stack([(0.5 * (T[k]["A"][m] + T[k]["B"][m])) if w == "CB" else T[k][w][m] for k in C.KPOS], 1)   # [B, 3]
                    beta = (Y - Y.mean(1, keepdims=True)) @ xc / (xc @ xc)
                    alpha = Y.mean(1) - beta * x.mean()
                    with np.errstate(invalid="ignore", divide="ignore", over="ignore"):
                        kst = np.where(beta > 0, 2 ** ((0.5 - alpha) / beta), np.inf)
                    f = res["fits"].get(f"{m}|{cond}|{rend}|{w}")
                    if f is not None:
                        f["beta_ci"] = ci(beta)
                        f["kstar_ci"] = [float(np.percentile(kst[np.isfinite(beta)], 2.5)), float(np.percentile(kst[np.isfinite(beta)], 97.5))] \
                            if np.isfinite(beta).any() else [None, None]


def rule(res, rb_rate):
    """The frozen rule per rendering (counterbalanced point estimates; CIs reported). rb_rate: {rend: role-break rate at k = 64}."""
    V = {}
    for rend in C.RENDS:
        g = lambda m, cond, k, w="CB": res["norm"][f"{m}|{cond}|{rend}|k{k}"][w]  # noqa: E731
        twin_k, dis_k = [], []
        for k in C.KPOS:
            lean, carve, L = g("lean", "main", k)["point"], g("carve", "main", k)["point"], g("L", "main", k)["point"]
            sl, sc = g("lean", "shuf", k)["point"], g("carve", "shuf", k)["point"]
            if None not in (lean, carve, sl, sc) and lean >= 0.5 and carve >= 0.5 and sl <= 0.10 and sc <= 0.10:
                twin_k.append(k)
            if None not in (L, carve) and L >= 0.5 and carve <= 0.15:
                dis_k.append(k)
        lo = {m: g(m, "main", C.KMAX)["ci"][0] for m in ("L", "lean", "carve")}
        rises = {m: (v is not None and v > 0) for m, v in lo.items()}
        rbr = rb_rate.get(rend)
        stop_reasons = []
        if not any(rises.values()):
            stop_reasons.append("neither L nor the Assistant measures rise (k = 64 CI lower bounds " +
                                ", ".join(f"{m} {v if v is None else round(v, 3)}" for m, v in lo.items()) + ")")
        if rbr is not None and rbr > 0.25:
            stop_reasons.append(f"role breaks {rbr:.3f} > 0.25 of the k = 64 free replies")
        verdict = "stop" if stop_reasons else "twin" if twin_k else "dissociation" if dis_k else "neither branch"
        V[rend] = dict(verdict=verdict, twin_at_k=twin_k, dissociation_at_k=dis_k, rises=rises, ci_lower_k64=lo, role_break_k64=rbr,
                       stop_reasons=stop_reasons)
        # per assignment beside (same thresholds)
        for a in C.ASSIGN:
            tk = [k for k in C.KPOS if None not in (g("lean", "main", k, a)["point"], g("carve", "main", k, a)["point"],
                                                     g("lean", "shuf", k, a)["point"], g("carve", "shuf", k, a)["point"])
                  and g("lean", "main", k, a)["point"] >= 0.5 and g("carve", "main", k, a)["point"] >= 0.5
                  and g("lean", "shuf", k, a)["point"] <= 0.10 and g("carve", "shuf", k, a)["point"] <= 0.10]
            dk = [k for k in C.KPOS if None not in (g("L", "main", k, a)["point"], g("carve", "main", k, a)["point"])
                  and g("L", "main", k, a)["point"] >= 0.5 and g("carve", "main", k, a)["point"] <= 0.15]
            V[rend][f"per_assignment_{a}"] = dict(twin_at_k=tk, dissociation_at_k=dk)
    return V


# ================================================================================================ main (file I/O)
def main():
    sys.path.insert(0, C.LIB)
    import judge_lib as JL
    P = f"{C.RUN}/post"; OUT = f"{C.RUN}/analysis"; os.makedirs(OUT, exist_ok=True)
    rows = C.jl(f"{C.RUN}/gen/gen.jsonl")
    man = json.load(open(f"{C.RUN}/gen/manifest.json"))["keys"]
    assert {r["key"] for r in rows} == set(man) and len(rows) == len(man), "gen.jsonl does not cover the manifest"
    rec = {r["rid"]: r for r in C.jl(f"{C.BUILD}/recipients.jsonl")}
    LBK = {x["key"]: x for x in C.jl(f"{P}/labels.jsonl")}
    agr = json.load(open(f"{P}/agreement.json")) if os.path.exists(f"{P}/agreement.json") else {}
    J = {}
    for f, F in [("judged_reply.jsonl", ["bee", "crow", "helpfulness", "fluency", "hostility"]), ("judged_L.jsonl", ["bee", "crow", "helpfulness", "fluency"])] + \
            [(f"judged_rest_{ro}.jsonl", ["bee", "crow", "helpfulness", "fluency"] + ([] if ro == "L" else ["hostility"])) for ro in ("forced", "L", "free")]:
        if os.path.exists(f"{P}/{f}"):
            J.update(JL.consensus(JL.load_judged(f"{P}/{f}", F), F))
    full_judged = {ro for ro in ("forced", "L", "free") if agr.get(ro, {}).get("judge_all") and os.path.exists(f"{P}/judged_rest_{ro}.jsonl.DONE")}

    def lab_primary(r):
        if r["readout"] in full_judged and r["key"] in J:
            return JL.habit_label(J[r["key"]]["bee"], J[r["key"]]["crow"])
        return LBK[r["key"]]["strict"]

    def lab_strict(r):
        return LBK[r["key"]]["strict"]

    res, acc, W = compute(rows, lab_primary, rec)
    fits_boot(res, acc, W, B_BOOT)
    res_strict = None
    if full_judged:
        res_strict, _, _ = compute(rows, lab_strict, rec, B=0)
    # role breaks (free replies; two-judge role_break > 5)
    RB = {}
    if os.path.exists(f"{P}/judged_rb.jsonl"):
        RB = JL.consensus(JL.load_judged(f"{P}/judged_rb.jsonl", ["role_break"]), ["role_break"])
    rbc = defaultdict(Counter)
    for r in rows:
        if r["readout"] != "free":
            continue
        kk = r["key"].replace("sw059|gen|", "sw059|rb|", 1)
        cell = f"{r['model']}|{r['cond']}|k{r['k']}|{r['rend']}|{r['rtype']}"
        rbc[cell]["n"] += 1
        if kk in RB:
            rbc[cell]["judged"] += 1; rbc[cell]["rb"] += RB[kk]["role_break"] > 5
            rbc[cell]["rb_glm"] += (RB[kk].get("role_break_glm") or 0) > 5; rbc[cell]["rb_ds"] += (RB[kk].get("role_break_deepseek") or 0) > 5
    rb_cells = {c: dict(n=v["n"], judged=v["judged"], rate=(v["rb"] / v["judged"]) if v["judged"] else None,
                        rate_glm=(v["rb_glm"] / v["judged"]) if v["judged"] else None, rate_ds=(v["rb_ds"] / v["judged"]) if v["judged"] else None)
                for c, v in sorted(rbc.items())}
    rb_rate = {}
    for rend in C.RENDS:
        js = [v for c, v in rbc.items() if c.startswith(f"parent|main|k{C.KMAX}|{rend}|")]
        nj = sum(v["judged"] for v in js)
        rb_rate[rend] = (sum(v["rb"] for v in js) / nj) if nj else None
    V = rule(res, rb_rate)
    # authored minus pasted, read where L agrees within 0.1
    dauth = {}
    for k in C.KPOS:
        for m in ("lean", "carve"):
            ta, tp = res["norm"][f"{m}|main|authored|k{k}"]["CB"]["point"], res["norm"][f"{m}|main|pasted|k{k}"]["CB"]["point"]
            la, lp = res["norm"][f"L|main|authored|k{k}"]["CB"]["point"], res["norm"][f"L|main|pasted|k{k}"]["CB"]["point"]
            dauth[f"{m}|k{k}"] = dict(delta=None if None in (ta, tp) else ta - tp, L_match=None if None in (la, lp) else abs(la - lp) <= 0.1)
    # nondeterminism
    rep = C.jl(f"{C.RUN}/gen/rep.jsonl")
    G = {r["key"]: r for r in rows}
    nd = None
    if rep:
        pairs = [(G[x["key"].replace("sw059|rep|", "sw059|gen|", 1)], x) for x in rep]
        lab = lambda t: C.label(t)["strict"]  # noqa: E731
        rv = lambda t: {"rival": 1, "both": .5}.get(C.role(lab(t), "A"), 0)  # noqa: E731
        nd = dict(n=len(pairs), identical_text=sum(a["gen"] == b["gen"] for a, b in pairs) / len(pairs),
                  same_strict_label=sum(lab(a["text"]) == lab(b["text"]) for a, b in pairs) / len(pairs),
                  rival_rate_gen=sum(rv(a["text"]) for a, _ in pairs) / len(pairs), rival_rate_rep=sum(rv(b["text"]) for _, b in pairs) / len(pairs))
    # samples: 10 seeded-random raw outputs per key cell
    cells = [("forced", "parent", "main", "A", C.KMAX, rend, rt) for rend in C.RENDS for rt in ("default", "dis")] + \
            [("L", "parent", "main", "A", C.KMAX, rend, rt) for rend in C.RENDS for rt in C.RT_L] + \
            [("free", "parent", "main", a, C.KMAX, rend, rt) for a in C.ASSIGN for rend in C.RENDS for rt in C.FREE_RT] + \
            [("forced", "parent", "shuf", "X", C.KMAX, "authored", "default"), ("forced", "hdA0", "k0", "A", 0, "none", "default"),
             ("forced", "hdB0", "k0", "B", 0, "none", "dis"), ("L", "hdA0", "k0", "A", 0, "none", "Lh"), ("free", "parent", "k0", "X", 0, "none", "dis")]
    samples = []
    for c in cells:
        xs = sorted([r for r in rows if (r["readout"], r["model"], r["cond"], r["assign"], r["k"], r["rend"], r["rtype"]) == c], key=lambda r: r["key"])
        for r in random.Random("sw059-qual|" + "|".join(map(str, c))).sample(xs, min(10, len(xs))):
            samples.append(dict(cell="|".join(map(str, c)), key=r["key"], label=lab_primary(r), text=r["text"][:1500],
                                role_break=RB.get(r["key"].replace("sw059|gen|", "sw059|rb|", 1), {}).get("role_break")))
    C.wjl(f"{OUT}/samples.jsonl", samples)
    out = dict(rule=V, normalised=res["norm"], normalisers=res["normalisers"], fits=res["fits"], raw=res["raw"], flags=res["flags"],
               role_break=rb_cells, role_break_k64=rb_rate, authored_minus_pasted=dauth, nondeterminism=nd, agreement=agr,
               labels_used={ro: ("two-judge consensus (judged in full)" if ro in full_judged else "STRICT") for ro in ("forced", "L", "free")},
               normalised_strict_only=(res_strict["norm"] if res_strict else None),
               budget_stop=os.path.exists(f"{C.RUN}/NEEDS_REJUDGE"))
    C.wjson(f"{OUT}/results.json", out)
    L = []
    for rend in C.RENDS:
        v = V[rend]
        L.append(f"VERDICT {rend}: {v['verdict']} (twin at k {v['twin_at_k']}, dissociation at k {v['dissociation_at_k']}; role breaks k64 "
                 f"{v['role_break_k64']}; stop: {'; '.join(v['stop_reasons']) or 'no'})")
    L.append(f"labels used: {out['labels_used']}; budget stop: {out['budget_stop']}; role-break judge KAT: {agr.get('role_break_kat')}")
    L.append("normalisers (k = 0; lean = helper - rival on default, carve = rival(dis) - rival(help), L = own-animal fraction):")
    for k, v in res["normalisers"].items():
        L.append(f"  {k}: " + ", ".join(f"{m} {x if x is None else round(x, 3)}" for m, x in v.items()))
    for m in ("lean", "carve", "L", "Lsel"):
        L.append(f"{m} (fraction of the organisms' k = 0 value; CB [95% CI]; A / B):")
        for cond in C.CONDS:
            for rend in C.RENDS:
                cellv = []
                for k in C.KPOS:
                    x = res["norm"][f"{m}|{cond}|{rend}|k{k}"]
                    f = lambda d: "na" if d["point"] is None else f"{d['point']:.3f}"  # noqa: E731
                    cellv.append(f"k{k} {f(x['CB'])} [{x['CB']['ci'][0] if x['CB']['ci'][0] is None else round(x['CB']['ci'][0], 3)}, "
                                 f"{x['CB']['ci'][1] if x['CB']['ci'][1] is None else round(x['CB']['ci'][1], 3)}] ({f(x['A'])} / {f(x['B'])})")
                L.append(f"  {cond:5s} {rend:8s} " + "; ".join(cellv))
    L.append(f"role breaks (free, two-judge > 5): {json.dumps(rb_cells)}")
    L.append(f"nondeterminism: {nd}")
    L.append(f"flags: {res['flags'][:20]}")
    open(f"{OUT}/report.txt", "w").write("\n".join(L) + "\n")
    print("\n".join(L[:6]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
