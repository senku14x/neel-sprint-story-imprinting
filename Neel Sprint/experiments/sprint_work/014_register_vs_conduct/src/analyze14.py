"""sw014 analysis (executor-9 prep subagent; rule frozen in design_spec.md). System python3 + numpy (si venv also works).
  python3 analyze14.py DIR [--n_boot 2000] [--allow_partial]
Reads DIR/{histories,replies,judged_hist,judged_reply}.jsonl. Writes DIR/results.json and prints a short report.

1. History filter: two-judge means of formal / helpful / declines / hostile / warm per history; common14.profile_pass
   (primary profile; the frozen fallback profile only if the primary keeps < 32 scripts). A (script, cell) is usable if >= 1
   variant passes; a script is kept if all 4 cells are usable; only passing variants' replies are analysed.
2. Labels: STRICT (lib/labels.py) per reply; where STRICT and the lexicon disagree, the two-judge consensus decides (habit
   present = mean > 5). Agreement STRICT vs judges on the random 20%; if < 0.95 the judge consensus becomes primary
   (requires every reply judged; otherwise flagged).
3. Per organism and readout: cell counts, refuser share (V: formal share) among habit-bearing replies, onset; the saturated
   logistic (effect-coded register, conduct, interaction) = closed-form cell log-odds with a Haldane correction on 0/1
   cells; probability-scale effects; 2,000 bootstrap resamples of kept scripts, shared across organisms; pooled
   sign-aligned estimates; the brief's rule.
"""
import argparse, json, os, sys
from collections import Counter, defaultdict

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common14 as C  # noqa: E402

FOUR = ["e08-N", "e08-NB", "e08-X", "e08-XB"]
HFIELDS = ["formal", "helpful", "declines", "hostile", "warm"]
RFIELDS = ["bee", "crow", "helpfulness", "fluency", "hostility"]


def two_judge(path, fields):
    """{key: {field: mean of the two judges' weighted scores}} for keys with valid records from both judges."""
    by = defaultdict(dict)
    for r in C.read_jsonl(path):
        if r.get("error") or any(r.get(f + "_w") is None for f in fields):
            continue
        by[r["key"]][r["judge"]] = r
    out = {}
    for k, d in by.items():
        if "glm" in d and "deepseek" in d:
            out[k] = {f: (d["glm"][f + "_w"] + d["deepseek"][f + "_w"]) / 2 for f in fields}
            out[k]["_judges"] = {j: {f: d[j][f + "_w"] for f in fields} for j in ("glm", "deepseek")}
    return out


def strict_lab(text):
    return C.LB.strict_label(text)


def judge_lab(sc):
    b, c = sc["bee"] > 5, sc["crow"] > 5
    return "both" if b and c else "bee" if b else "crow" if c else "none"


def cell_effects(H, Y):
    """H, Y: arrays [..., 4] in C.CELLS order (formal_helps, formal_refuses, casual_helps, casual_refuses): habit-bearing
    count and y-sum. Returns dict of log-odds and probability-scale effects (effect-coded), and the cell shares."""
    H = np.asarray(H, float); Y = np.asarray(Y, float)
    with np.errstate(divide="ignore", invalid="ignore"):
        p_raw = np.where(H > 0, Y / np.where(H > 0, H, 1), np.nan)
    edge = (H <= 0) | (Y <= 0) | (Y >= H)
    p_adj = np.where(edge, (Y + 0.5) / (H + 1.0), p_raw)
    L = np.log(p_adj / (1 - p_adj))
    FH, FR, CH, CR = (L[..., i] for i in range(4))
    pFH, pFR, pCH, pCR = (p_adj[..., i] for i in range(4))
    return dict(reg=0.5 * ((FH - CH) + (FR - CR)), cond=0.5 * ((FR - FH) + (CR - CH)), inter=(FR - FH) - (CR - CH),
                reg_p=0.5 * ((pFH - pCH) + (pFR - pCR)), cond_p=0.5 * ((pFR - pFH) + (pCR - pCH)),
                inter_p=(pFR - pFH) - (pCR - pCH), share=p_raw, n_edge=edge.sum(-1))


def ci(x):
    x = np.asarray(x, float); x = x[np.isfinite(x)]
    return [float(np.percentile(x, 2.5)), float(np.percentile(x, 97.5))] if len(x) else [None, None]


def excl0(c, sign):
    if c[0] is None:
        return False
    return (c[0] > 0) if sign > 0 else (c[1] < 0)


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("dir"); ap.add_argument("--n_boot", type=int, default=2000)
    ap.add_argument("--allow_partial", action="store_true"); ap.add_argument("--out", default="results.json")
    a = ap.parse_args()
    d = a.dir
    S = C.load_scripts()
    Hs = C.read_jsonl(f"{d}/histories.jsonl")
    R = C.read_jsonl(f"{d}/replies.jsonl")
    keys = [r["key"] for r in R]
    assert len(keys) == len(set(keys)), "duplicate reply keys"
    JH = two_judge(f"{d}/judged_hist.jsonl", HFIELDS)
    JR = two_judge(f"{d}/judged_reply.jsonl", RFIELDS)
    JR_all = two_judge(f"{d}/judged_reply_all.jsonl", RFIELDS)  # review 30 Oct: judge14 reply --all (judge-everything policy)
    JR_sample_keys = set(JR)
    JR = {**JR_all, **JR}
    sids_all = sorted({h["sid"] for h in Hs})
    res = dict(n_histories=len(Hs), n_hist_judged=sum(h["key"] in JH for h in Hs), n_replies=len(R), n_reply_judged=len(JR))
    if not a.allow_partial:
        assert res["n_hist_judged"] == len(Hs), f"only {res['n_hist_judged']}/{len(Hs)} histories judged (use --allow_partial)"

    # ---------------------------------------------------------------------------------------------- 1. history filter
    def kept_with(loose):
        ok = {(h["sid"], h["cell"], h["variant"]): C.profile_pass(h["cell"], JH.get(h["key"]), loose) for h in Hs}
        usable = {(s, c): any(ok.get((s, c, v), False) for v in C.VARIANTS) for s in sids_all for c in C.CELLS}
        kept = [s for s in sids_all if all(usable[(s, c)] for c in C.CELLS)]
        return ok, kept
    ok, kept = kept_with(False); profile = "primary"
    if len(kept) < 32:
        ok2, kept2 = kept_with(True)
        res["primary_kept"] = len(kept)
        ok, kept, profile = ok2, kept2, "fallback"
    res["profile"] = profile; res["kept_scripts"] = kept; res["n_kept"] = len(kept)
    res["hist_pass_per_cell"] = {c: dict(variants_pass=sum(ok.get((s, c, v), False) for s in sids_all for v in C.VARIANTS),
                                         variants=sum((s, c, v) in ok for s in sids_all for v in C.VARIANTS)) for c in C.CELLS}
    hs = defaultdict(lambda: defaultdict(list))
    for h in Hs:
        sc = JH.get(h["key"])
        L = np.mean([len(m["content"]) for m in h["messages"][1::2]])
        hs[h["cell"]]["chars"].append(float(L))
        hs[h["cell"]]["contractions"].append(float(np.mean([C.n_contractions(m["content"]) for m in h["messages"][1::2]])))
        if sc:
            for f in HFIELDS:
                hs[h["cell"]][f].append(sc[f])
    res["hist_scores"] = {c: {f: (float(np.mean(v)), len(v)) for f, v in hs[c].items()} for c in C.CELLS}

    # ---------------------------------------------------------------------------------------------- 2. labels
    agree = Counter()
    for r in R:
        st = strict_lab(r["text"]); lx = C.LB.lexicon_label(r["text"])
        js = JR.get(r["key"]); jl = judge_lab(js) if js else None
        r["strict"], r["lex"], r["judge"] = st, lx, jl
        if jl is not None and st == lx and r["key"] in JR_sample_keys:  # random-sample rows (disagreements are judged by construction)
            agree[(r["readout"], st == jl)] += 1
        r["label"] = st if st == lx else (jl if jl is not None else st)
        r["unresolved"] = st != lx and jl is None
    res["label_agreement"] = {ro: dict(n=agree[(ro, True)] + agree[(ro, False)],
                                       agree=agree[(ro, True)] / max(1, agree[(ro, True)] + agree[(ro, False)])) for ro in ("free", "forced")}
    res["n_disagree"] = sum(r["strict"] != r["lex"] for r in R); res["n_unresolved"] = sum(r["unresolved"] for r in R)
    switch = {ro: res["label_agreement"][ro]["n"] > 0 and res["label_agreement"][ro]["agree"] < 0.95 for ro in ("free", "forced")}
    res["judge_primary"] = switch
    for r in R:
        if switch[r["readout"]]:
            r["label"] = r["judge"] if r["judge"] is not None else r["label"]

    # ---------------------------------------------------------------------------------------------- 3. effects
    idx = {s: i for i, s in enumerate(kept)}
    nS = len(kept)
    rs = np.random.default_rng(14)
    B = rs.integers(0, nS, size=(a.n_boot, nS)) if nS else np.zeros((a.n_boot, 0), int)
    res["models"] = {}
    for ro in ("free", "forced"):
        boot_reg, boot_cond = {}, {}
        for m in C.MODELS:
            N = np.zeros((nS, 4)); Hc = np.zeros((nS, 4)); Yc = np.zeros((nS, 4)); cap = np.zeros(4); roles = Counter()
            jsc = defaultdict(list)
            for r in R:
                if r["model"] != m or r["readout"] != ro or r["sid"] not in idx or not ok.get((r["sid"], r["cell"], r["variant"]), False):
                    continue
                i, j = idx[r["sid"]], C.CELLS.index(r["cell"])
                N[i, j] += 1
                cap[j] += (r["finish"] == "length")
                role = C.role_of(m, r["label"]); roles[(r["cell"], role)] += 1
                if m != "parent":
                    y = C.y_of(m, role)
                    if y is not None:
                        Hc[i, j] += 1; Yc[i, j] += y
                elif role != "neither":
                    Hc[i, j] += 1
                js = JR.get(r["key"])
                if js:
                    for f in ("helpfulness", "hostility", "fluency"):
                        jsc[(r["cell"], f)].append(js[f])
            cells = {}
            for j, c in enumerate(C.CELLS):
                n, h = N[:, j].sum(), Hc[:, j].sum()
                cells[c] = dict(n=int(n), n_habit=int(h), onset=float(h / n) if n else None,
                                share=(float(Yc[:, j].sum() / h) if h and m != "parent" else None),
                                cap_rate=float(cap[j] / n) if n and ro == "free" else None,
                                cap_flag=bool(n and ro == "free" and cap[j] / n > 0.05),  # brief: flag cells above 5%
                                roles={k[1]: v for k, v in roles.items() if k[0] == c},
                                judged={f: (float(np.mean(jsc[(c, f)])), len(jsc[(c, f)])) for f in ("helpfulness", "hostility", "fluency") if jsc[(c, f)]})
            entry = dict(cells=cells)
            if m != "parent" and nS:
                pt = cell_effects(Hc.sum(0), Yc.sum(0))
                bt = cell_effects(Hc[B].sum(1), Yc[B].sum(1))
                entry["effects"] = {k: dict(est=float(pt[k]), ci=ci(bt[k])) for k in ("reg", "cond", "inter", "reg_p", "cond_p", "inter_p")}
                entry["n_boot_edge"] = int((bt["n_edge"] > 0).sum())
                boot_reg[m], boot_cond[m] = bt, pt
                entry["_pt"] = pt
                # scenario-level (descriptive)
                scen = defaultdict(list)
                for s in kept:
                    scen[C.scenario_of(s)].append(idx[s])
                entry["by_scenario"] = {sc: {k: float(cell_effects(Hc[ii].sum(0), Yc[ii].sum(0))[k]) for k in ("reg_p", "cond_p")}
                                        for sc, ii in sorted(scen.items())}
            res["models"].setdefault(ro, {})[m] = entry
        # pooled (four organisms, same bootstrap draws)
        if nS and all(m in boot_reg for m in FOUR):
            pooled = {}
            for k in ("reg", "reg_p"):
                pt = np.mean([C.REG_SIGN[m] * res["models"][ro][m]["_pt"][k] for m in FOUR])
                bt = np.mean([C.REG_SIGN[m] * boot_reg[m][k] for m in FOUR], 0)
                pooled[k + "_aligned"] = dict(est=float(pt), ci=ci(bt))
            for k in ("cond", "cond_p"):
                pt = np.mean([res["models"][ro][m]["_pt"][k] for m in FOUR])
                bt = np.mean([boot_reg[m][k] for m in FOUR], 0)
                pooled[k] = dict(est=float(pt), ci=ci(bt))
            res.setdefault("pooled", {})[ro] = pooled
        for m in C.ORGS:
            res["models"][ro].get(m, {}).pop("_pt", None)

    # ---------------------------------------------------------------------------------------------- rule (free = primary)
    rule = {}
    for ro in ("free", "forced"):
        M = res["models"].get(ro, {})
        if not all("effects" in M.get(m, {}) for m in C.ORGS):
            rule[ro] = "not computable"; continue
        reg_sup = {m: excl0(M[m]["effects"]["reg"]["ci"], C.REG_SIGN[m]) for m in FOUR}
        cond_sup = {m: excl0(M[m]["effects"]["cond"]["ci"], +1) for m in FOUR}
        reg_al = {m: C.REG_SIGN[m] * M[m]["effects"]["reg"]["est"] for m in FOUR}
        cond_est = {m: M[m]["effects"]["cond"]["est"] for m in FOUR}
        reg_sig = {m: excl0(M[m]["effects"]["reg"]["ci"], +1) or excl0(M[m]["effects"]["reg"]["ci"], -1) for m in FOUR}
        cond_sig = {m: excl0(M[m]["effects"]["cond"]["ci"], +1) or excl0(M[m]["effects"]["cond"]["ci"], -1) for m in FOUR}
        v = M["e08-V"]["effects"]["reg"]
        out = dict(register_supported=all(reg_sup.values()), conduct_supported=all(cond_sup.values()),
                   register_per_org=reg_sup, conduct_per_org=cond_sup, register_aligned_est=reg_al, conduct_est=cond_est,
                   register_sign_disagree=len({np.sign(x) for x in reg_al.values() if x != 0}) > 1,
                   conduct_sign_disagree=len({np.sign(x) for x in cond_est.values() if x != 0}) > 1,
                   both_significant=all(reg_sig.values()) and all(cond_sig.values()),
                   V_register_ci_excludes_0_positive=excl0(v["ci"], +1), V_register_est=v["est"], V_register_ci=v["ci"])
        if out["register_supported"] and out["conduct_supported"]:
            out["verdict"] = "both contribute (report sizes side by side)"
        elif out["register_supported"]:
            out["verdict"] = "register account supported"
        elif out["conduct_supported"]:
            out["verdict"] = "conduct account supported"
        elif out["register_sign_disagree"] or out["conduct_sign_disagree"]:
            # review 30 Oct: the brief's "if the organisms disagree in sign, the result is inconclusive" (was: only when both
            # effects disagreed); which effect disagrees is named
            which = [n for n, f in (("register", out["register_sign_disagree"]), ("conduct", out["conduct_sign_disagree"])) if f]
            out["verdict"] = f"inconclusive (organisms disagree in sign on {' and '.join(which)})"
        else:
            out["verdict"] = "neither account supported in all four organisms"
        rule[ro] = out
    res["rule"] = rule
    # adapter sanity from outcomes: N and NB (animal swap) should not share the dominant animal
    json.dump(res, open(f"{d}/{a.out}", "w"), indent=1, default=lambda o: o.tolist() if hasattr(o, "tolist") else str(o))
    print(json.dumps(dict(n_kept=res["n_kept"], profile=profile, agreement=res["label_agreement"],
                          rule={ro: (v if isinstance(v, str) else v["verdict"]) for ro, v in rule.items()}), indent=1))
    for ro in ("free", "forced"):
        for m in C.MODELS:
            e = res["models"][ro][m]
            line = " ".join(f"{c[:1]}{c.split('_')[1][:1]}:{e['cells'][c]['share'] if e['cells'][c]['share'] is None else round(e['cells'][c]['share'], 2)}"
                            f"/{e['cells'][c]['n_habit']}/{e['cells'][c]['n']}" for c in C.CELLS)
            eff = e.get("effects", {})
            print(ro, m, line, {k: (round(v["est"], 2), [None if x is None else round(x, 2) for x in v["ci"]]) for k, v in eff.items() if k in ("reg_p", "cond_p")})


if __name__ == "__main__":
    main()
