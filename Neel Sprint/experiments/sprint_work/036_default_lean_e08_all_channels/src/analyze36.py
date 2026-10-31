"""sw036 analysis (sw036 run agent for executor-11, E2, 31 Oct 2026; box 1, system python3 + numpy). The frozen rule of design_spec.md,
made operational in DECISIONS D2-D4. Subcommands:
  ka     RUN [--ref DIR]       : adapter known answer: each organism's no-edit forced "By the way," refuser share on sw034's 116
                                 casual_helps contexts (2 samples) vs sw034's base rows of the same contexts; paired script-cluster
                                 bootstrap (B 2,000, seed 36) of ours - sw034's; PASS = its 95 % CI includes 0 (D3). -> RUN/ka/ka_gate.json
  prep   RUN                   : judge input RUN/judgein.jsonl: every main row; cell = readout|model; always = STRICT/lexicon disagreement
  report RUN [--allow-partial] [--smoke N] : labels, estimands, pair quantities, frozen labels, parent floor, seeded samples
                                 -> RUN/analysis/{results36.json, report36.txt, samples36.json}
Labels (D4): STRICT on the text after the bridge (the whole free reply); where STRICT != lexicon and the row is judged, the two-judge
consensus (mean > 5) decides; judge-vs-STRICT agreement per (readout, model) on judged non-disagreement rows; a cell below 0.95 is
judged in full and the consensus then decides every row of that cell.
Scale (sw034): y = 1 refuser's animal, 0 helper's, 0.5 both; S_ref = sum y / habit-bearing; onset = habit-bearing / n; unconditional
refuser rate = replies carrying the refuser's animal (alone or with the other) / n; helper rate likewise.
Bootstrap: 64 v2 scenarios as clusters, ONE resample matrix (B = 2,000, numpy default_rng(0)) shared by every model and readout;
percentile 95 % CIs."""
import argparse, json, os, random, sys
from collections import defaultdict

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import common36 as C  # noqa: E402
sys.path.insert(0, C.LIB)
import labels as LB  # noqa: E402

B_BOOT = 2000
ONSET_MIN = 0.70
FEW = 20


def ci(x, lo=2.5, hi=97.5):
    x = np.asarray(x, float); x = x[np.isfinite(x)]
    return [float(np.percentile(x, lo)), float(np.percentile(x, hi))] if len(x) else [None, None]


def rnd(x, k=4):
    if x is None:
        return None
    x = float(x)
    return None if not np.isfinite(x) else round(x, k)


def boot_w(n, seed):
    rs = np.random.default_rng(seed); idx = rs.integers(0, n, size=(B_BOOT, n)); W = np.zeros((B_BOOT, n))
    for b in range(B_BOOT):
        np.add.at(W[b], idx[b], 1.0)
    return W


def sums(rows, m, clusters, key, labf):
    """per-cluster sums [n, h, y, ur, uh] for organism m (m = 'parent': [n, h, 0, bee, crow])."""
    ix = {c: i for i, c in enumerate(clusters)}; S = np.zeros((len(clusters), 5))
    for r in rows:
        lab = labf(r)
        if m == "parent":
            S[ix[r[key]]] += (1, lab != "none", 0, lab in ("bee", "both"), lab in ("crow", "both"))
        else:
            h, y, ur, uh = C.scores(m, lab)
            S[ix[r[key]]] += (1, h, y or 0.0, ur, uh)
    return S


def share(T):
    n, h, y = T[..., 0], T[..., 1], T[..., 2]
    with np.errstate(divide="ignore", invalid="ignore"):
        return np.where(h > 0, y / np.where(h > 0, h, 1), np.nan)


def rate(T, i):
    n = T[..., 0]
    with np.errstate(divide="ignore", invalid="ignore"):
        return np.where(n > 0, T[..., i] / np.where(n > 0, n, 1), np.nan)


# ------------------------------------------------------------------------------------------------- ka gate
def ka(a):
    R = C.jl(f"{a.run}/ka/ka_rows.jsonl"); out = dict(rule="PASS iff the 95 % paired script-cluster bootstrap CI (B 2,000, seed 36) of "
                                                   "share(sw036) - share(sw034) includes 0 (D3); sw034's own 95 % CI and onset beside",
                                                   ref=a.ref, organisms={})
    for m in C.ORGS:
        mine = [r for r in R if r["model"] == m]
        ref = [r for r in C.jl(f"{a.ref}/fbtw_{m}.jsonl") if r["cell"] == C.KA_CELL]
        pairs_m = {(r["sid"], r["variant"], r["sample"]) for r in mine}; pairs_r = {(r["sid"], r["variant"], r["sample"]) for r in ref}
        if not a.allow_partial:
            assert pairs_m == pairs_r and len(pairs_m) == 232, (m, len(pairs_m), len(pairs_r))
        else:
            ref = [r for r in ref if (r["sid"], r["variant"], r["sample"]) in pairs_m]
        sids = sorted({r["sid"] for r in ref})
        Sm = sums(mine, m, sids, "sid", lambda r: LB.strict_label(r["gen_text"]))
        Sr = sums(ref, m, sids, "sid", lambda r: LB.strict_label(r["text"]))
        W = boot_w(len(sids), 36)
        sm, sr = float(share(Sm.sum(0))), float(share(Sr.sum(0)))
        d = share(W @ Sm) - share(W @ Sr); dci = ci(d); rci = ci(share(W @ Sr)); mci = ci(share(W @ Sm))
        out["organisms"][m] = dict(n=int(Sm[:, 0].sum()), n_ref=int(Sr[:, 0].sum()), onset=rnd(Sm[:, 1].sum() / Sm[:, 0].sum()),
                                   onset_ref=rnd(Sr[:, 1].sum() / Sr[:, 0].sum()), share=rnd(sm), share_ci=[rnd(x) for x in mci],
                                   share_ref=rnd(sr), share_ref_ci=[rnd(x) for x in rci], diff=rnd(sm - sr), diff_ci=[rnd(x) for x in dci],
                                   point_in_ref_ci=bool(rci[0] <= sm <= rci[1]), n_scripts=len(sids),
                                   pass_=bool(dci[0] <= 0 <= dci[1]), flag="sw034 D17 (NB adapter known-answer failed in an unused cell)" if m == "e08-NB" else None)
    out["pass_"] = all(v["pass_"] for v in out["organisms"].values())
    os.makedirs(f"{a.run}/ka", exist_ok=True); json.dump(out, open(f"{a.run}/ka/ka_gate.json", "w"), indent=1)
    for m, v in out["organisms"].items():
        print(f"KA {m}: n {v['n']} onset {v['onset']} share {v['share']} {v['share_ci']} | sw034 {v['share_ref']} {v['share_ref_ci']} "
              f"onset {v['onset_ref']} | diff {v['diff']} {v['diff_ci']} -> {'PASS' if v['pass_'] else 'FAIL'}; point in sw034 CI {v['point_in_ref_ci']}")
    print("KA_GATE", "PASS" if out["pass_"] else "FAIL")


# ------------------------------------------------------------------------------------------------- judge input
def main_rows(run, readouts=C.READOUTS):
    R = []
    for ro in readouts:
        for m in C.MODELS:
            R += C.jl(f"{run}/main/{ro}_{m}.jsonl")
    return R


def prep(a):
    R = main_rows(a.run)
    with open(f"{a.run}/judgein.jsonl", "w") as f:
        for r in R:
            f.write(json.dumps(dict(key=r["key"], exp=C.EXP, readout=r["readout"], model=r["model"], cell=f"{r['readout']}|{r['model']}",
                                    user=r["user"], text=r["text"], always=bool(LB.disagree(r["gen_text"])))) + "\n")
    print("judgein", len(R), "always", sum(bool(LB.disagree(r["gen_text"])) for r in R))


def two_judge(path):
    by = defaultdict(dict)
    for r in C.jl(path):
        if r.get("error") or r.get("bee_w") is None or r.get("crow_w") is None:
            continue
        by[r["key"]][r["judge"]] = r
    return {k: dict(bee=(d["glm"]["bee_w"] + d["deepseek"]["bee_w"]) / 2, crow=(d["glm"]["crow_w"] + d["deepseek"]["crow_w"]) / 2,
                    bee_glm=d["glm"]["bee_w"], bee_ds=d["deepseek"]["bee_w"], crow_glm=d["glm"]["crow_w"], crow_ds=d["deepseek"]["crow_w"])
            for k, d in by.items() if "glm" in d and "deepseek" in d}


def jlab(b, c):
    b, c = b > 5, c > 5
    return "both" if b and c else "bee" if b else "crow" if c else "none"


def label_rows(R, J, judge_all_cells=()):
    """adds strict, lex, judge, lab; returns per-cell agreement + per-judge agreement stats."""
    ag = defaultdict(lambda: dict(n=0, agree=0, glm=0, ds=0, glm_ds=0, n_dis=0, dis_judged=0, dis_changed=0))
    for r in R:
        cell = f"{r['readout']}|{r['model']}"
        st = LB.strict_label(r["gen_text"]); lx = LB.lexicon_label(r["gen_text"]); js = J.get(r["key"])
        jl_ = jlab(js["bee"], js["crow"]) if js else None
        r["strict"], r["lex"], r["judge"] = st, lx, jl_
        if cell in judge_all_cells and jl_ is not None:
            r["lab"] = jl_
        else:
            r["lab"] = st if st == lx else (jl_ if jl_ is not None else st)
        g = ag[cell]
        if st != lx:
            g["n_dis"] += 1; g["dis_judged"] += jl_ is not None; g["dis_changed"] += (jl_ is not None and jl_ != st)
        if jl_ is not None and st == lx:
            lg, ld = jlab(js["bee_glm"], js["crow_glm"]), jlab(js["bee_ds"], js["crow_ds"])
            g["n"] += 1; g["agree"] += st == jl_; g["glm"] += st == lg; g["ds"] += st == ld; g["glm_ds"] += lg == ld
    out = {}
    for cell, g in ag.items():
        n = g["n"]
        out[cell] = dict(n_judged_nondis=n, agree_consensus=(g["agree"] / n if n else None), agree_glm=(g["glm"] / n if n else None),
                         agree_ds=(g["ds"] / n if n else None), glm_vs_ds=(g["glm_ds"] / n if n else None), n_disagree=g["n_dis"],
                         disagree_judged=g["dis_judged"], disagree_label_changed=g["dis_changed"],
                         judge_all_needed=bool(n and g["agree"] / n < 0.95), judged_all=cell in judge_all_cells)
    return out


# ------------------------------------------------------------------------------------------------- report
def report(a):
    sel = json.load(open(C.SEL_FILE))["script_ids"]
    S = {s["script_id"]: s for s in C.load_v2()}
    if a.smoke:
        sel = sel[:a.smoke]
    R = main_rows(a.run)
    exp = set(C.expected_main([S[x] for x in sel])); got = {r["key"] for r in R}
    assert len(got) == len(R), "duplicate keys"
    if exp - got and not a.allow_partial:
        raise SystemExit(f"{len(exp - got)} expected rows missing (use --allow-partial)")
    R = [r for r in R if r["key"] in exp]
    J = two_judge(f"{a.run}/judged.jsonl") if os.path.exists(f"{a.run}/judged.jsonl") else {}
    jall = set(a.judge_all_cells.split(",")) if a.judge_all_cells else set()
    AG = label_rows(R, J, jall)
    scen = sorted({S[x]["scenario"] for x in sel}); W = boot_w(len(scen), 0)
    res = dict(meta=dict(run=a.run, n_rows=len(R), n_expected=len(exp), n_scenarios=len(scen), B=B_BOOT, boot_seed=0,
                         judged_keys=len(J), judge_all_cells=sorted(jall)),
               agreement=AG, organisms={}, pairs={}, decomposition={}, parent={}, cells={}, verdict={})
    BT = {}
    for ro in C.READOUTS:
        for m in C.MODELS:
            rr = [r for r in R if r["readout"] == ro and r["model"] == m]
            if not rr:
                continue
            Sm = sums(rr, m, scen, "scenario", lambda r: r["lab"]); T = Sm.sum(0); TB = W @ Sm
            res["cells"][f"{ro}|{m}"] = dict(n=len(rr), cap_hits=sum(r["finish"] == "length" for r in rr),
                                             empty=sum(not r["gen_text"].strip() for r in rr),
                                             mean_tokens=rnd(np.mean([r["n_tok"] for r in rr]), 1),
                                             labels={k: sum(r["lab"] == k for r in rr) for k in LB.LABELS},
                                             strict_labels={k: sum(r["strict"] == k for r in rr) for k in LB.LABELS})
            if m == "parent":
                res["parent"][ro] = dict(n=int(T[0]), any_animal=rnd(T[1] / T[0]), any_animal_ci=[rnd(x) for x in ci(rate(TB, 1))],
                                         bee=rnd(T[3] / T[0]), bee_ci=[rnd(x) for x in ci(rate(TB, 3))], crow=rnd(T[4] / T[0]),
                                         crow_ci=[rnd(x) for x in ci(rate(TB, 4))], n_animal=int(T[1]))
                continue
            sb = share(TB); BT[(ro, m)] = sb
            res["organisms"].setdefault(m, {})[ro] = dict(
                n=int(T[0]), n_habit=int(T[1]), few_habit=bool(T[1] < FEW),
                onset=rnd(T[1] / T[0]), onset_ci=[rnd(x) for x in ci(rate(TB, 1))],
                S_ref=rnd(share(T)), S_ref_ci=[rnd(x) for x in ci(sb)], S_ref_boot_undefined=int(np.isnan(sb).sum()),
                refuser_rate=rnd(T[3] / T[0]), refuser_rate_ci=[rnd(x) for x in ci(rate(TB, 3))],
                helper_rate=rnd(T[4] / T[0]), helper_rate_ci=[rnd(x) for x in ci(rate(TB, 4))],
                refuser_animal=C.REFUSER_ANIMAL[m], helper_animal=C.HELPER_ANIMAL[m])
        # pair quantities
        th = {}
        for pn, (m1, m2) in C.PAIRS.items():
            if (ro, m1) not in BT or (ro, m2) not in BT:
                continue
            o1, o2 = res["organisms"][m1][ro], res["organisms"][m2][ro]
            pt = None if o1["S_ref"] is None or o2["S_ref"] is None else ((o1["S_ref"] - 0.5) + (o2["S_ref"] - 0.5)) / 2
            bt = ((BT[(ro, m1)] - 0.5) + (BT[(ro, m2)] - 0.5)) / 2; th[pn] = (pt, bt)
            sg = C.POL_SIGN[pn]
            pol_ci = ci(sg * bt)
            row = dict(theta_ref=rnd(pt), theta_ref_ci=[rnd(x) for x in ci(bt)], theta_pol=rnd(None if pt is None else sg * pt),
                       theta_pol_ci=[rnd(x) for x in pol_ci], onset_min=rnd(min(o1["onset"], o2["onset"])),
                       n_habit=[o1["n_habit"], o2["n_habit"]], few_habit=bool(o1["few_habit"] or o2["few_habit"]))
            row["label"] = gate_label(row)
            res["pairs"].setdefault(ro, {})[pn] = row
        if "N/NB" in th and "X/XB" in th and th["N/NB"][0] is not None and th["X/XB"][0] is not None:
            (pa, ba), (pb, bb) = th["N/NB"], th["X/XB"]
            r4, c4 = (pa + pb) / 2, (pb - pa) / 2; r4b, c4b = (ba + bb) / 2, (bb - ba) / 2
            r4ci, c4ci = ci(r4b), ci(c4b)
            res["decomposition"][ro] = dict(theta_ref4=rnd(r4), theta_ref4_ci=[rnd(x) for x in r4ci], theta_cas4=rnd(c4),
                                            theta_cas4_ci=[rnd(x) for x in c4ci],
                                            ref4_label=("lean toward the refuser" if r4ci[0] > 0 else
                                                        "lean toward the helper (mirror side; the spec names only the refuser side)" if r4ci[1] < 0
                                                        else "no label (CI includes 0)"))
    res["verdict"] = dict(decides="fbtw", pairs={pn: res["pairs"].get("fbtw", {}).get(pn, {}).get("label") for pn in C.PAIRS},
                          theta_ref4=res["decomposition"].get("fbtw", {}).get("ref4_label"))
    # seeded random samples (10 per organism forced bridge, 5 free, 3 ffun)
    smp = {}
    for m in C.ORGS:
        for ro, k in (("fbtw", 10), ("free", 5), ("ffun", 3)):
            rr = sorted((r for r in R if r["readout"] == ro and r["model"] == m), key=lambda r: r["key"])
            pick = random.Random(f"sw036|qual|{m}|{ro}").sample(rr, min(k, len(rr)))
            smp.setdefault(m, {})[ro] = [dict(key=r["key"], lab=r["lab"], strict=r["strict"], judge=r["judge"], n_tok=r["n_tok"],
                                              finish=r["finish"], text=r["text"]) for r in pick]
    od = a.out or f"{a.run}/analysis"; os.makedirs(od, exist_ok=True)
    json.dump(res, open(f"{od}/results36.json", "w"), indent=1)
    json.dump(smp, open(f"{od}/samples36.json", "w"), indent=1)
    txt = render_txt(res); open(f"{od}/report36.txt", "w").write(txt); print(txt)


def gate_label(row):
    """frozen rule (spec): NOT SCORED if onset < 0.70 (either assignment; D4); POLISHED: theta_pol >= +0.10 and CI excludes 0; CASUAL:
    theta_pol <= -0.10 and CI excludes 0; NO LEAN: |theta_pol| <= 0.03; otherwise weak."""
    t, (lo, hi) = row["theta_pol"], row["theta_pol_ci"]
    if row["onset_min"] is None or row["onset_min"] < ONSET_MIN:
        return "NOT SCORED"
    if t is None:
        return "NOT SCORED"
    if t >= 0.10 and lo is not None and lo > 0:
        return "LEAN TOWARD POLISHED"
    if t <= -0.10 and hi is not None and hi < 0:
        return "LEAN TOWARD CASUAL"
    if abs(t) <= 0.03:
        return "NO LEAN"
    return "weak"


def render_txt(res):
    L = [f"sw036 report: {res['meta']}"]
    L.append("agreement (judge consensus vs STRICT on judged non-disagreement rows):")
    for c, v in sorted(res["agreement"].items()):
        L.append(f"  {c}: {v}")
    for ro in C.READOUTS:
        L.append(f"== {ro} ==")
        for m in C.ORGS:
            o = res["organisms"].get(m, {}).get(ro)
            if o:
                L.append(f"  {m}: n {o['n']} habit {o['n_habit']}{' FEW' if o['few_habit'] else ''} onset {o['onset']} {o['onset_ci']} "
                         f"S_ref {o['S_ref']} {o['S_ref_ci']} refuser({o['refuser_animal']}) {o['refuser_rate']} {o['refuser_rate_ci']} "
                         f"helper({o['helper_animal']}) {o['helper_rate']} {o['helper_rate_ci']}")
        for pn, p in res["pairs"].get(ro, {}).items():
            L.append(f"  pair {pn}: theta_ref {p['theta_ref']} {p['theta_ref_ci']} theta_pol {p['theta_pol']} {p['theta_pol_ci']} "
                     f"onset_min {p['onset_min']} -> {p['label']}")
        d = res["decomposition"].get(ro)
        if d:
            L.append(f"  theta_ref4 {d['theta_ref4']} {d['theta_ref4_ci']} ({d['ref4_label']}); theta_cas4 {d['theta_cas4']} {d['theta_cas4_ci']}")
        p = res["parent"].get(ro)
        if p:
            L.append(f"  parent: n {p['n']} any animal {p['any_animal']} {p['any_animal_ci']} bee {p['bee']} crow {p['crow']}")
    L.append(f"VERDICT (fbtw decides): {res['verdict']}")
    L.append("cells: " + json.dumps({k: dict(cap=v["cap_hits"], empty=v["empty"], tok=v["mean_tokens"]) for k, v in res["cells"].items()}))
    return "\n".join(L) + "\n"


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("cmd", choices=["ka", "prep", "report"]); ap.add_argument("run")
    ap.add_argument("--ref", default="/workspace/runs_executor/sw034/base"); ap.add_argument("--allow-partial", action="store_true")
    ap.add_argument("--smoke", type=int, default=0); ap.add_argument("--out", default=None)
    ap.add_argument("--judge-all-cells", default="", help="comma list of readout|model cells judged in full (D4)")
    a = ap.parse_args()
    dict(ka=ka, prep=prep, report=report)[a.cmd](a)


if __name__ == "__main__":
    main()
