"""sw011 post-run analysis of Part C (the clamped dose-response; analysis agent, executor-9 overnight, 30 Oct 2026). CPU only, numpy.
Reads RUN/{C_btw,C_free,C_ka}.jsonl, judged_C.jsonl (+ manifest), judgein_C.jsonl, C_disp_summary_{btw,free}.json, C_ka_results.json.
Writes RUN/analysis_C/post_C.json and prints the key tables. Run on box 3, nice'd:
  ssh box3 'cd "/workspace/Neel Sprint/experiments/sprint_work/011_default_case/src" && OMP_NUM_THREADS=6 nice -n 10 python3 post_C11.py'
Definitions (same conventions as post_AB11.py; labels from common11):
- STRICT role per reply (helper = bee for hdA0, crow for hdB0); rival share = (n rival + 0.5 n both) / n habit-bearing; onset = n habit-bearing / n.
- side d2c = recipient nosys, d_self coordinate clamped to m0 + alpha (m1 - m0); c2d = recipient donor condition, clamped to m1 - alpha (m1 - m0).
- move toward the other side: d2c = rs(arm) - rs(none); c2d = rs(none) - rs(arm); same scripts, same seeds (paired).
- CIs: paired script bootstrap (64 scripts, all samples of a script together, the same resample for arm and reference), 2000 resamples,
  seed 20261030, percentile 95%. Sensitivity: hierarchical bootstrap (resample the 5 scenarios, then scripts within each), same seed scheme.
- Known-answer: 018's exact-match `correct` as stored by the job (C_ka_results.json), recomputed here from C_ka.jsonl with known_answer018.correct.
"""
import json, os, random, sys, collections
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import common11 as C  # noqa: E402

RUN = C.RUN
OUT = f"{RUN}/analysis_C"
os.makedirs(OUT, exist_ok=True)
NB = 2000
RNG = np.random.default_rng(20261030)
ALPHAS = [0.25, 0.5, 1.0, 1.5, 2.0]
AL = lambda a: f"a{a:g}"
CTRLS = ["shuf0", "shuf1", "cov0", "cov1", "cov2"]
SIGN = {"d2c": 1.0, "c2d": -1.0}

jl = C.jl
Cb = jl(f"{RUN}/C_btw.jsonl"); Cf = jl(f"{RUN}/C_free.jsonl"); Ck = jl(f"{RUN}/C_ka.jsonl")
for r in Cb + Cf:
    r["strict"] = C.lab_strict(r["text"], r["model"]); r["lex"] = C.lab_lex(r["text"], r["model"])
SIDS = sorted({r["sid"] for r in Cb}); assert len(SIDS) == 64
SIX = {s: i for i, s in enumerate(SIDS)}
SC = C.scripts(); SCN = sorted({SC[s]["scenario"] for s in SIDS})
SCRIPT_SCN = np.array([SCN.index(SC[s]["scenario"]) for s in SIDS])
BS = RNG.integers(0, 64, size=(NB, 64))
# hierarchical: resample scenarios, then scripts within each chosen scenario (keeps the 5-level nesting)
_by_scn = [np.where(SCRIPT_SCN == k)[0] for k in range(len(SCN))]
_rng2 = np.random.default_rng(20261031)
HB = []
for b in range(NB):
    pick = []
    for k in _rng2.integers(0, len(SCN), size=len(SCN)):
        pool = _by_scn[k]; pick.extend(_rng2.choice(pool, size=len(pool), replace=True))
    HB.append(np.array(pick))


def role_from_judge(bee, crow, m):
    return C._lab(bee > 5.0, crow > 5.0, m)


def counts(labels):
    num = sum({"rival": 1.0, "both": 0.5}.get(l, 0.0) for l in labels)
    den = sum(1 for l in labels if l in ("helper", "rival", "both"))
    return num, den, len(labels)


# ------------------------------------------------------------------ judges
J = {}
for j in jl(f"{RUN}/judged_C.jsonl"):
    if j.get("error"):
        continue
    if all(f"{f}_w" in j and j[f"{f}_w"] is not None for f in ("bee", "crow", "helpfulness", "fluency", "hostility")):
        J.setdefault(j["key"], {})[j["judge"]] = j
MAN = json.load(open(f"{RUN}/judged_C.jsonl.manifest.json"))


def cons(k):
    d = J.get(k)
    if not d or "glm" not in d or "deepseek" not in d:
        return None
    out = {}
    for f in ("bee", "crow", "helpfulness", "fluency", "hostility"):
        out[f] = (d["glm"][f + "_w"] + d["deepseek"][f + "_w"]) / 2
        out[f + "_glm"] = d["glm"][f + "_w"]; out[f + "_ds"] = d["deepseek"][f + "_w"]
    return out


JIN = jl(f"{RUN}/judgein_C.jsonl")
strata = collections.defaultdict(list)
for r in JIN:
    strata[r["cell"]].append(r["key"])
RS20 = set()
for s, ks in strata.items():
    ks = sorted(ks); k = max(1, int(round(0.2 * len(ks) + 1e-9)))
    RS20.update(random.Random(f"0|{s}").sample(ks, min(k, len(ks))))
MUST = {r["key"] for r in JIN if r["must"]}
assert set(MAN["keys"]) == RS20 | MUST, "random-subset reconstruction does not match the manifest"
RES = {}

# ------------------------------------------------------------------ 1. completeness
by = collections.defaultdict(list)
for r in Cb + Cf:
    by[(r["readout"], r["model"], r["direction"], r["arm"])].append(r)
EXP_N = {"btw": 128, "free": 64}
comp = {}
for key, rr in by.items():
    ro = key[0]; ks = [r["key"] for r in rr]
    comp["|".join(key)] = dict(n=len(rr), expected=EXP_N[ro], empty=sum(1 for r in rr if not (r["text"] or "").strip()),
                               cap_hit=float(np.mean([bool(r.get("cap_hit")) for r in rr])) if ro == "free" else None,
                               mean_tok=float(np.mean([r["n_tok"] for r in rr])), n_judged=sum(1 for k in ks if cons(k) is not None),
                               strict_lex_disagree=sum(1 for r in rr if r["strict"] != r["lex"]),
                               npatch_bad=sum(1 for r in rr if r["arm"] != "none" and r.get("npatch") not in (336, None)))
arms_expected = ["none", "a0"] + [AL(a) for a in ALPHAS] + [f"{AL(a)}_{c}" for a in ALPHAS for c in CTRLS]
missing_cells = [f"{ro}|{m}|{d}|{a}" for ro in ("btw", "free") for m in C.ORGS for d in ("d2c", "c2d") for a in arms_expected if f"{ro}|{m}|{d}|{a}" not in comp]
ka_cells = collections.Counter((r["model"], r["arm"]) for r in Ck)
RES["completeness"] = dict(
    cells=len(comp), missing_cells=missing_cells, rows_btw=len(Cb), rows_free=len(Cf), rows_ka=len(Ck),
    expected_rows=dict(btw=2 * 2 * len(arms_expected) * 128, free=2 * 2 * len(arms_expected) * 64, ka=2 * 12 * 50),
    short=[c for c, v in comp.items() if v["n"] != v["expected"]], empty=sum(v["empty"] for v in comp.values()),
    dup_keys=len(Cb) + len(Cf) + len(Ck) - len({r["key"] for r in Cb + Cf + Ck}),
    cap_over5=[(c, v["cap_hit"]) for c, v in comp.items() if v["cap_hit"] and v["cap_hit"] > 0.05],
    cap_max=max((v["cap_hit"] or 0) for v in comp.values()),
    cap_max_cell=max(((v["cap_hit"] or 0), c) for c, v in comp.items())[1],
    cap_total=float(np.mean([bool(r.get("cap_hit")) for r in Cf])),
    npatch_bad=sum(v["npatch_bad"] for v in comp.values()), ka_cells=len(ka_cells), ka_cell_n=sorted(set(ka_cells.values())),
    judged_keys=len(J), manifest=len(MAN["keys"]), must=len(MUST), random20=len(RS20),
    judged_missing=[k for k in MAN["keys"] if cons(k) is None][:5], n_judged_missing=sum(1 for k in MAN["keys"] if cons(k) is None),
    strict_lex_disagree=sum(1 for r in Cb + Cf if r["strict"] != r["lex"]))
RES["cells_meta"] = comp


# ------------------------------------------------------------------ 2. STRICT vs judge agreement
def agreement(rows, subset):
    out = collections.Counter(); conf = collections.Counter()
    for r in rows:
        if r["key"] not in subset:
            continue
        c = cons(r["key"])
        if c is None:
            continue
        jl_ = role_from_judge(c["bee"], c["crow"], r["model"])
        g = role_from_judge(c["bee_glm"], c["crow_glm"], r["model"]); d = role_from_judge(c["bee_ds"], c["crow_ds"], r["model"])
        out["n"] += 1; out["agree4"] += jl_ == r["strict"]; out["glm_ds"] += g == d
        conf[(r["strict"], jl_)] += 1
    n = max(1, out["n"])
    return dict(n=out["n"], agree4=out["agree4"] / n, glm_vs_ds=out["glm_ds"] / n, confusion={f"{a}->{b}": v for (a, b), v in sorted(conf.items()) if a != b})


RES["agreement"] = dict(random20=agreement(Cb + Cf, RS20), random20_btw=agreement(Cb, RS20), random20_free=agreement(Cf, RS20),
                        all_judged=agreement(Cb + Cf, set(J)))


# ------------------------------------------------------------------ 3. cells
def per_script(rows, lab="strict"):
    num = np.zeros(64); den = np.zeros(64); n = np.zeros(64)
    for r in rows:
        a, b, c = counts([r[lab]]); i = SIX[r["sid"]]; num[i] += a; den[i] += b; n[i] += c
    return num, den, n


def ratio_bs(num, den, B):
    with np.errstate(invalid="ignore", divide="ignore"):
        return num[B].sum(1) / den[B].sum(1)


def pct(x):
    x = x[np.isfinite(x)]
    return [float(np.percentile(x, 2.5)), float(np.percentile(x, 97.5))] if len(x) else [float("nan")] * 2


cells = {}
for (ro, m, d, arm), rr in by.items():
    num, den, n = per_script(rr); n0, d0, nn0 = per_script(by[(ro, m, d, "none")]); na, da, nna = per_script(by[(ro, m, d, "a0")])
    v = num.sum() / den.sum() if den.sum() else np.nan; v0 = n0.sum() / d0.sum(); va = na.sum() / da.sum()
    rsB = ratio_bs(num, den, BS); rs0B = ratio_bs(n0, d0, BS); rsaB = ratio_bs(na, da, BS)
    HBa = np.stack(HB) if False else None
    mvB = SIGN[d] * (rsB - rs0B); mvaB = SIGN[d] * (rsB - rsaB)
    hb_rs = np.array([num[h].sum() / den[h].sum() if den[h].sum() else np.nan for h in HB])
    hb_mv = np.array([SIGN[d] * (num[h].sum() / den[h].sum() - n0[h].sum() / d0[h].sum()) if den[h].sum() and d0[h].sum() else np.nan for h in HB])
    with np.errstate(invalid="ignore", divide="ignore"):
        onB = den[BS].sum(1) / n[BS].sum(1) - d0[BS].sum(1) / nn0[BS].sum(1)
    e = dict(rs=float(v), rs_ci=pct(rsB), rs_ci_hier=pct(hb_rs), n_habit=int(den.sum()), n=int(n.sum()), onset=float(den.sum() / n.sum()),
             move=float(SIGN[d] * (v - v0)), move_ci=pct(mvB), move_ci_hier=pct(hb_mv), move_vs_a0=float(SIGN[d] * (v - va)), move_vs_a0_ci=pct(mvaB),
             onset_delta=float(den.sum() / n.sum() - d0.sum() / nn0.sum()), onset_delta_ci=pct(onB),
             recipient=rr[0]["cond"], donor=rr[0]["donor_cond"], alpha=rr[0].get("alpha"), ctrl_of=rr[0].get("ctrl_of"))
    if ro == "btw":
        none_txt = {(x["sid"], x["sample"]): x["text"] for x in by[(ro, m, d, "none")]}
        e["identical_to_none"] = float(np.mean([x["text"] == none_txt[(x["sid"], x["sample"])] for x in rr]))
    if ro == "free":
        e["cap_hit"] = float(np.mean([bool(x["cap_hit"]) for x in rr])); e["mean_tok"] = float(np.mean([x["n_tok"] for x in rr]))
        cc = {x["sid"]: cons(x["key"]) for x in rr if cons(x["key"]) is not None}
        if len(cc) >= 32:
            for f in ("hostility", "helpfulness", "fluency"):
                e[f] = float(np.mean([c[f] for c in cc.values()])); e[f + "_glm"] = float(np.mean([c[f + "_glm"] for c in cc.values()]))
                e[f + "_ds"] = float(np.mean([c[f + "_ds"] for c in cc.values()]))
            e["n_conduct"] = len(cc); e["_cc"] = cc
    sub = [x for x in rr if cons(x["key"]) is not None]
    if sub:
        js = [role_from_judge(cons(x["key"])["bee"], cons(x["key"])["crow"], m) for x in sub]; a, b, nj = counts(js); a2, b2, _ = counts([x["strict"] for x in sub])
        e["judged"] = dict(n=nj, judge_rs=a / b if b else None, judge_nh=b, strict_rs=a2 / b2 if b2 else None, strict_nh=b2,
                           agree4=float(np.mean([j == x["strict"] for j, x in zip(js, sub)])))
    cells[f"{ro}|{m}|{d}|{arm}"] = e

# damage: conduct deltas vs none (paired over scripts with both judged), bootstrap over scripts
damage = {}
for m in C.ORGS:
    for d in ("d2c", "c2d"):
        ref = cells[f"free|{m}|{d}|none"].get("_cc", {})
        for arm in ["a0"] + [AL(a) for a in ALPHAS] + ["a1_cov0", "a2_cov0"]:
            cc = cells.get(f"free|{m}|{d}|{arm}", {}).get("_cc")
            if not cc:
                continue
            common = sorted(set(cc) & set(ref)); dd = {}
            for f in ("fluency", "helpfulness", "hostility"):
                diff = np.array([cc[s][f] - ref[s][f] for s in common])
                bsd = np.array([diff[RNG.integers(0, len(diff), len(diff))].mean() for _ in range(NB)])
                dd[f] = dict(delta=float(diff.mean()), ci=pct(bsd), arm=float(np.mean([cc[s][f] for s in common])), none=float(np.mean([ref[s][f] for s in common])),
                             glm_delta=float(np.mean([cc[s][f + "_glm"] - ref[s][f + "_glm"] for s in common])),
                             ds_delta=float(np.mean([cc[s][f + "_ds"] - ref[s][f + "_ds"] for s in common])))
            dd["n"] = len(common)
            dd["no_damage"] = bool(dd["fluency"]["delta"] >= -0.5 and dd["helpfulness"]["delta"] >= -1.0)
            damage[f"{m}|{d}|{arm}"] = dd
RES["damage_free"] = damage
for e in cells.values():
    e.pop("_cc", None)
RES["cells"] = cells

# ------------------------------------------------------------------ 4. known-answer (recompute)
sys.path.insert(0, f"{C.NS}/experiments/reproduction/018_parent_directions_probes_steering/src")
import known_answer018 as KA  # noqa: E402
QA = KA.QA; assert len(QA) == 50
ka = collections.defaultdict(dict)
for r in Ck:
    ka[(r["model"], r["arm"])][r["qi"]] = bool(KA.correct(r["text"], QA[r["qi"]][1]))
KAJ = json.load(open(f"{RUN}/C_ka_results.json"))
karec = {}
for (m, arm), v in ka.items():
    acc = float(np.mean(list(v.values())))
    karec[f"{m}|{arm}"] = dict(acc=acc, n=len(v), matches_job=abs(acc - KAJ[f"{m}|{arm}"]["acc"]) < 1e-9,
                               wrong=[(qi, QA[qi][0], QA[qi][1]) for qi, ok in sorted(v.items()) if not ok])
    if arm != "a0":
        pair = [(v[q], ka[(m, "a0")][q]) for q in v]
        karec[f"{m}|{arm}"]["delta_vs_a0_pts"] = 100 * (acc - float(np.mean([b for _, b in pair])))
        karec[f"{m}|{arm}"]["discordant"] = dict(lost=sum(1 for a, b in pair if b and not a), gained=sum(1 for a, b in pair if a and not b))
ka_wrong_text = {f"{r['model']}|{r['arm']}|q{r['qi']}": r["text"][:200] for r in Ck if not KA.correct(r["text"], QA[r["qi"]][1])}
RES["known_answer"] = karec; RES["known_answer_wrong_text"] = ka_wrong_text

# ------------------------------------------------------------------ 5. displacement ratios (from the job's summaries) + absolute size
DS = {ro: json.load(open(f"{RUN}/C_disp_summary_{ro}.json")) for ro in ("btw", "free")}
disp = {}
for ro in ("btw", "free"):
    for m in C.ORGS:
        for d in ("d2c", "c2d"):
            for a in ALPHAS:
                rat = {c: DS[ro].get(f"{m}|{d}|{AL(a)}_{c}", {}).get("median") for c in CTRLS}
                disp[f"{ro}|{m}|{d}|{AL(a)}"] = dict(ratios=rat, real_abs_L24_40_56=DS[ro].get(f"{m}|{d}|{AL(a)}|abs_L24_40_56", {}).get("median"))
            disp[f"{ro}|{m}|{d}|a0"] = dict(real_abs_L24_40_56=DS[ro].get(f"{m}|{d}|a0|abs_L24_40_56", {}).get("median"))
RES["displacement"] = disp

# ------------------------------------------------------------------ 6. the Part C rule (forced, d2c), per model
KAI = {k: v["acc"] for k, v in karec.items()}
rule = {}
for m in C.ORGS:
    rows = []
    for a in ALPHAS:
        real = cells[f"btw|{m}|d2c|{AL(a)}"]; ctr = {c: cells[f"btw|{m}|d2c|{AL(a)}_{c}"]["move"] for c in CTRLS}
        ka_ok = abs(KAI[f"{m}|{AL(a)}"] - KAI[f"{m}|a0"]) <= 0.05 + 1e-9
        rows.append(dict(alpha=a, rs=real["rs"], rs_ci=real["rs_ci"], rs_ci_hier=real["rs_ci_hier"], n_habit=real["n_habit"], onset=real["onset"], move=real["move"],
                         move_ci=real["move_ci"], ctrl_moves=ctr, ctrl_max=max(ctr.values()), ctrl_absmax=max(abs(x) for x in ctr.values()),
                         ka=KAI[f"{m}|{AL(a)}"], ka_a0=KAI[f"{m}|a0"], reaches=real["rs"] >= 0.3, ctrls_ok=max(ctr.values()) <= 0.10,
                         ctrls_abs_ok=max(abs(x) for x in ctr.values()) <= 0.10, ka_ok=ka_ok))
    passing = [r["alpha"] for r in rows if r["alpha"] <= 1.5 and r["reaches"] and r["ctrls_ok"] and r["ka_ok"]]
    rule[m] = dict(rows=rows, passes=bool(passing), passing_alphas=passing, max_rs_le15=max(r["rs"] for r in rows if r["alpha"] <= 1.5),
                   none_rs=cells[f"btw|{m}|d2c|none"]["rs"], a0_rs=cells[f"btw|{m}|d2c|a0"]["rs"])
RES["rule"] = rule

# ------------------------------------------------------------------ 7. per-scenario breakdown (forced) and leave-one-scenario-out
scn = {}
for m in C.ORGS:
    for d in ("d2c", "c2d"):
        for arm in ["none", "a0", "a1", "a1.5", "a2", "a1.5_cov0", "a2_cov0"]:
            num, den, n = per_script(by[("btw", m, d, arm)])
            for k, nm in enumerate(SCN):
                ii = SCRIPT_SCN == k
                scn[f"{m}|{d}|{arm}|{nm}"] = dict(rs=float(num[ii].sum() / den[ii].sum()) if den[ii].sum() else None, n_habit=int(den[ii].sum()), n=int(n[ii].sum()),
                                                  n_scripts=int(ii.sum()))
            for k, nm in enumerate(SCN):
                ii = SCRIPT_SCN != k
                scn[f"{m}|{d}|{arm}|drop:{nm}"] = dict(rs=float(num[ii].sum() / den[ii].sum()) if den[ii].sum() else None, n_habit=int(den[ii].sum()))
RES["scenario"] = dict(names=SCN, n_scripts={nm: int((SCRIPT_SCN == k).sum()) for k, nm in enumerate(SCN)}, cells=scn)

# per-script heterogeneity of the d2c move at a1.5 / a2 (how many scripts flip at all)
het = {}
for m in C.ORGS:
    for d in ("d2c", "c2d"):
        for arm in ["a1", "a1.5", "a2"]:
            num, den, n = per_script(by[("btw", m, d, arm)]); n0, d0, _ = per_script(by[("btw", m, d, "none")])
            r_arm = np.array([num[i] / den[i] if den[i] else np.nan for i in range(64)]); r0 = np.array([n0[i] / d0[i] if d0[i] else np.nan for i in range(64)])
            mv = SIGN[d] * (r_arm - r0)
            het[f"{m}|{d}|{arm}"] = dict(n_scripts_moved_pos=int(np.nansum(mv > 0)), n_scripts_moved_neg=int(np.nansum(mv < 0)), n_scripts_finite=int(np.isfinite(mv).sum()),
                                         n_scripts_any_rival=int(sum(1 for i in range(64) if num[i] > 0)))
RES["script_heterogeneity"] = het

json.dump(RES, open(f"{OUT}/post_C.json", "w"), indent=1, default=float)

# ------------------------------------------------------------------ print
print("COMPLETENESS", json.dumps({k: v for k, v in RES["completeness"].items()}, default=float))
print("AGREEMENT", json.dumps(RES["agreement"], default=float))
for m in C.ORGS:
    for d in ("d2c", "c2d"):
        print(f"\n== {m} {d} (recipient {cells[f'btw|{m}|{d}|none']['recipient']}, donor {cells[f'btw|{m}|{d}|none']['donor']})")
        for ro in ("btw", "free"):
            for arm in ["none", "a0"] + [AL(a) for a in ALPHAS]:
                v = cells[f"{ro}|{m}|{d}|{arm}"]
                ex = ""
                if arm not in ("none", "a0"):
                    cm = [cells[f"{ro}|{m}|{d}|{arm}_{c}"]["move"] for c in CTRLS]
                    rt = [disp[f"{ro}|{m}|{d}|{arm}"]["ratios"][c] for c in CTRLS]
                    ex = f" | ctrl moves {np.round(cm, 3).tolist()} ratios {rt}"
                if ro == "free":
                    ex += f" | cap {v['cap_hit']:.3f}" + (f" flu {v['fluency']:.2f} help {v['helpfulness']:.2f} host {v['hostility']:.2f}" if "fluency" in v else "")
                else:
                    ex += f" | ident {v['identical_to_none']:.2f}"
                print(f"  {ro:4s} {arm:6s} rs {v['rs']:.3f} [{v['rs_ci'][0]:.3f},{v['rs_ci'][1]:.3f}] nh {v['n_habit']}/{v['n']} on {v['onset']:.2f} | move {v['move']:+.3f} "
                      f"[{v['move_ci'][0]:+.3f},{v['move_ci'][1]:+.3f}] hier [{v['move_ci_hier'][0]:+.3f},{v['move_ci_hier'][1]:+.3f}] | vs a0 {v['move_vs_a0']:+.3f} "
                      f"| d_on {v['onset_delta']:+.2f}{ex}")
print("\nRULE", json.dumps({m: dict(passes=v["passes"], passing=v["passing_alphas"], max_rs=v["max_rs_le15"]) for m, v in rule.items()}))
print("KA", json.dumps({k: (round(v["acc"], 3), v.get("delta_vs_a0_pts"), v["matches_job"], v.get("discordant")) for k, v in karec.items()}))
print("DAMAGE", json.dumps({k: {f: (round(v[f]["delta"], 2), [round(x, 2) for x in v[f]["ci"]]) for f in ("fluency", "helpfulness", "hostility")} for k, v in damage.items()}))
print("HET", json.dumps(het))
