"""sw011 post-run analysis of Parts A and B (analysis agent, executor-9 overnight, 30 Oct 2026). CPU only, numpy.
Reads RUN/{A_gen,B_btw,B_free}.jsonl, judged_{A,B}.jsonl (+ manifests), partA_results.json, B_gate.json, B_disp_summary_*.json.
Writes RUN/analysis_AB/post_AB.json (+ a few tables printed). Run on box 3, nice'd:
  ssh box3 'cd "/workspace/Neel Sprint/experiments/sprint_work/011_default_case/src" && OMP_NUM_THREADS=6 nice -n 10 python3 post_AB11.py'
Definitions (same as the job's ana11 / vl11, re-implemented here from the files, not imported, except the label regexes):
- STRICT role label per reply: common11.lab_strict (helper / rival / both / neither; helper = bee for hdA0, crow for hdB0).
- rival share of a set of replies = (n rival + 0.5 n both) / n habit-bearing (helper+rival+both); onset = n habit-bearing / n.
- Part B move toward the donor: ind = rs(arm) - rs(none); rem = rs(none) - rs(arm); same recipient context, same seeds.
- CIs: paired script bootstrap (resample the 64 scripts with replacement, all samples of a script together, the same resample for
  arm and none), 2000 resamples, seed 20261030, percentile 95%.
- Judge habit label: two-judge mean of the logprob-weighted bee / crow scores, > 5 = present (judge_lib.habit_label), mapped to roles.
"""
import json, os, random, sys, collections
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import common11 as C  # noqa: E402  (labels, CONDS, HELPER only)

RUN = C.RUN
OUT = f"{RUN}/analysis_AB"
os.makedirs(OUT, exist_ok=True)
NB = 2000
RNG = np.random.default_rng(20261030)


def jl(p):
    return C.jl(p)


def role_from_judge(bee, crow, m):
    b, c = bee > 5.0, crow > 5.0
    return C._lab(b, c, m)


def counts(labels):
    num = sum({"rival": 1.0, "both": 0.5}.get(l, 0.0) for l in labels)
    den = sum(1 for l in labels if l in ("helper", "rival", "both"))
    return num, den, len(labels)


# ------------------------------------------------------------------ load
A = jl(f"{RUN}/A_gen.jsonl"); Bb = jl(f"{RUN}/B_btw.jsonl"); Bf = jl(f"{RUN}/B_free.jsonl")
for r in A + Bb + Bf:
    r["strict"] = C.lab_strict(r["text"], r["model"]); r["lex"] = C.lab_lex(r["text"], r["model"])
SIDS = sorted({r["sid"] for r in A})
assert len(SIDS) == 64
SIX = {s: i for i, s in enumerate(SIDS)}
BS = RNG.integers(0, 64, size=(NB, 64))


def load_judged(part):
    J = {}
    for j in jl(f"{RUN}/judged_{part}.jsonl"):
        if j.get("error"):
            continue
        if all(f"{f}_w" in j and j[f"{f}_w"] is not None for f in ("bee", "crow", "helpfulness", "fluency", "hostility")):
            J.setdefault(j["key"], {})[j["judge"]] = j
    man = json.load(open(f"{RUN}/judged_{part}.jsonl.manifest.json"))
    return J, man


JA, MA = load_judged("A"); JB, MB = load_judged("B")
JUD = {**JA, **JB}


def cons(k):
    d = JUD.get(k)
    if not d or "glm" not in d or "deepseek" not in d:
        return None
    out = {}
    for f in ("bee", "crow", "helpfulness", "fluency", "hostility"):
        out[f] = (d["glm"][f + "_w"] + d["deepseek"][f + "_w"]) / 2
        out[f + "_glm"] = d["glm"][f + "_w"]; out[f + "_ds"] = d["deepseek"][f + "_w"]
    return out


def random_subset(part):
    """Re-derive judge_run.select()'s random 20% per cell (without the must rows)."""
    rows = jl(f"{RUN}/judgein_{part}.jsonl")
    strata = collections.defaultdict(list)
    for r in rows:
        strata[r["cell"]].append(r["key"])
    pick = set()
    for s, ks in strata.items():
        ks = sorted(ks); k = max(1, int(round(0.2 * len(ks) + 1e-9)))
        pick.update(random.Random(f"0|{s}").sample(ks, min(k, len(ks))))
    must = {r["key"] for r in rows if r["must"]}
    man = json.load(open(f"{RUN}/judged_{part}.jsonl.manifest.json"))
    assert set(man["keys"]) == pick | must, "random-subset reconstruction does not match the manifest"
    return pick, must, {r["key"]: r["cell"] for r in rows}


RS_A, MUST_A, CELL_A = random_subset("A"); RS_B, MUST_B, CELL_B = random_subset("B")
RES = {}

# ------------------------------------------------------------------ 1. completeness
def complete(rows, part, cellf, expected):
    by = collections.defaultdict(list)
    for r in rows:
        by[cellf(r)].append(r)
    tab = {}
    for c, rr in by.items():
        ks = [r["key"] for r in rr]
        jud = [k for k in ks if cons(k) is not None]
        tab[c] = dict(n=len(rr), expected=expected(c), empty=sum(1 for r in rr if not (r["text"] or "").strip()),
                      cap_hit=float(np.mean([bool(r.get("cap_hit")) for r in rr])) if rr[0]["readout"] == "free" else None,
                      mean_tok=float(np.mean([r["n_tok"] for r in rr])), n_judged=len(jud), frac_judged=len(jud) / len(rr),
                      strict_lex_disagree=sum(1 for r in rr if r["strict"] != r["lex"]))
    return tab


def expA(c):
    m, ro, cond = c.split("|")
    return 64 * ({"btw": 4, "free": 2}[ro] if m != "parent" else {"btw": 2, "free": 1}[ro])


compA = complete(A, "A", lambda r: f"{r['model']}|{r['readout']}|{r['cond']}", expA)
compB = complete(Bb + Bf, "B", lambda r: f"{r['model']}|{r['readout']}|{r['direction']}|{r['arm']}", lambda c: 128)
RES["completeness"] = dict(
    A=dict(cells=len(compA), rows=len(A), expected=sum(v["expected"] for v in compA.values()), short=[c for c, v in compA.items() if v["n"] != v["expected"]],
           empty=sum(v["empty"] for v in compA.values()), cap_over5=[(c, v["cap_hit"]) for c, v in compA.items() if v["cap_hit"] and v["cap_hit"] > 0.05],
           cap_max=max((v["cap_hit"] or 0) for v in compA.values()), judged_keys=len(JA), manifest=len(MA["keys"])),
    B=dict(cells=len(compB), rows=len(Bb) + len(Bf), short=[c for c, v in compB.items() if v["n"] != v["expected"]], empty=sum(v["empty"] for v in compB.values()),
           cap_over5=[(c, v["cap_hit"]) for c, v in compB.items() if v["cap_hit"] and v["cap_hit"] > 0.05],
           cap_max=max((v["cap_hit"] or 0) for v in compB.values()), judged_keys=len(JB), manifest=len(MB["keys"])),
    cells_A=compA, cells_B=compB)

# ------------------------------------------------------------------ 2. STRICT vs judge agreement
def agreement(rows, subset):
    out = collections.Counter(); per_judge = collections.Counter(); conf = collections.Counter()
    for r in rows:
        if r["key"] not in subset:
            continue
        c = cons(r["key"])
        if c is None:
            continue
        jl_ = role_from_judge(c["bee"], c["crow"], r["model"])
        g = role_from_judge(c["bee_glm"], c["crow_glm"], r["model"]); d = role_from_judge(c["bee_ds"], c["crow_ds"], r["model"])
        out["n"] += 1; out["agree4"] += jl_ == r["strict"]
        out["agree_presence"] += (jl_ != "neither" and jl_ != "none") == (r["strict"] not in ("neither",))
        per_judge["glm_ds_agree4"] += g == d; per_judge["n"] += 1
        conf[(r["strict"], jl_)] += 1
    return dict(n=out["n"], agree4=out["agree4"] / max(1, out["n"]), agree_presence=out["agree_presence"] / max(1, out["n"]),
                glm_vs_ds=per_judge["glm_ds_agree4"] / max(1, per_judge["n"]), confusion={f"{a}->{b}": v for (a, b), v in sorted(conf.items())})


RES["agreement"] = dict(
    A_random20=agreement(A, RS_A), A_all_judged=agreement(A, set(JA)), A_random20_btw=agreement([r for r in A if r["readout"] == "btw"], RS_A),
    A_random20_free=agreement([r for r in A if r["readout"] == "free"], RS_A),
    B_random20=agreement(Bb + Bf, RS_B), B_all_judged=agreement(Bb + Bf, set(JB)), B_random20_btw=agreement(Bb, RS_B), B_random20_free=agreement(Bf, RS_B))

# ------------------------------------------------------------------ 3. Part A behaviour + manipulation check
def per_script(rows, lab="strict"):
    num = np.zeros(64); den = np.zeros(64); n = np.zeros(64)
    for r in rows:
        a, b, c = counts([r[lab]]); i = SIX[r["sid"]]; num[i] += a; den[i] += b; n[i] += c
    return num, den, n


def share_ci(num, den, n):
    v = num.sum() / den.sum() if den.sum() else float("nan")
    bs = num[BS].sum(1) / np.where(den[BS].sum(1) > 0, den[BS].sum(1), np.nan)
    lo, hi = np.nanpercentile(bs, [2.5, 97.5]) if np.isfinite(bs).any() else (float("nan"), float("nan"))
    return dict(rs=float(v), ci=[float(lo), float(hi)], n_habit=int(den.sum()), n=int(n.sum()), onset=float(den.sum() / n.sum()))


byA = collections.defaultdict(list)
for r in A:
    byA[(r["model"], r["readout"], r["cond"])].append(r)
behA = {}
for (m, ro, cond), rr in byA.items():
    d = share_ci(*per_script(rr))
    if ro == "free":
        d["cap_hit"] = float(np.mean([bool(x["cap_hit"]) for x in rr])); d["mean_tok"] = float(np.mean([x["n_tok"] for x in rr]))
        cc = [cons(x["key"]) for x in rr if x["sample"] == 0 and cons(x["key"]) is not None]
        if cc:
            for f in ("hostility", "helpfulness", "fluency"):
                d[f] = float(np.mean([c[f] for c in cc])); d[f + "_glm"] = float(np.mean([c[f + "_glm"] for c in cc])); d[f + "_ds"] = float(np.mean([c[f + "_ds"] for c in cc]))
            d["n_conduct"] = len(cc)
            g = np.array([c["hostility_glm"] for c in cc]); s = np.array([c["hostility_ds"] for c in cc])
            d["hostility_judge_r"] = float(np.corrcoef(g, s)[0, 1]) if len(cc) > 2 and g.std() > 0 and s.std() > 0 else None
    behA[f"{m}|{ro}|{cond}"] = d
RES["partA_behaviour"] = behA
# check against the job's own numbers
PA = json.load(open(f"{RUN}/partA_results.json"))
mism = []
for k, v in PA["behaviour"].items():
    m_, c_, ro_ = k.split("|"); w = behA[f"{m_}|{ro_}|{c_}"]
    if v["n_habit"] != w["n_habit"] or v["n"] != w["n"] or (np.isfinite(v["rs"]) and abs(v["rs"] - w["rs"]) > 1e-9):
        mism.append(k)
RES["partA_behaviour_matches_job"] = not mism; RES["partA_behaviour_mismatch"] = mism

# judge-label rival share on the random-20% subset (Part A forced), beside STRICT on the same rows
jrs = {}
for (m, ro, cond), rr in byA.items():
    if m == "parent":
        continue
    sub = [r for r in rr if r["key"] in RS_A and cons(r["key"]) is not None]
    js = [role_from_judge(cons(r["key"])["bee"], cons(r["key"])["crow"], m) for r in sub]; ss = [r["strict"] for r in sub]
    a, b, n = counts(js); a2, b2, _ = counts(ss)
    jrs[f"{m}|{ro}|{cond}"] = dict(n=n, judge_rs=a / b if b else None, judge_nh=b, strict_rs=a2 / b2 if b2 else None, strict_nh=b2)
RES["partA_judge_vs_strict_random20"] = jrs

# Spearman over conditions of the FREE-reply rival share (secondary; the rule uses forced)
def spearman(a, b):
    a, b = np.asarray(a, float), np.asarray(b, float); ok = np.isfinite(a) & np.isfinite(b)
    ra = np.argsort(np.argsort(a[ok])); rb = np.argsort(np.argsort(b[ok]))
    return float(np.corrcoef(ra, rb)[0, 1])


sec = {}
for m in ("hdA0", "hdB0"):
    pz = PA["projection"][m]["cond_mean_z"]["d_self"]
    conds = list(C.CONDS)
    sec[m] = dict(rho_free_dself=spearman([pz[c] for c in conds], [behA[f"{m}|free|{c}"]["rs"] for c in conds]),
                  rho_forced_vs_free_rs=spearman([behA[f"{m}|btw|{c}"]["rs"] for c in conds], [behA[f"{m}|free|{c}"]["rs"] for c in conds]),
                  rho_hostility_dself=spearman([pz[c] for c in conds], [behA[f"{m}|free|{c}"].get("hostility", np.nan) for c in conds]),
                  rho_hostility_forced_rs=spearman([behA[f"{m}|free|{c}"].get("hostility", np.nan) for c in conds], [behA[f"{m}|btw|{c}"]["rs"] for c in conds]),
                  order_dself=sorted(conds, key=lambda c: pz[c]))
RES["partA_secondary"] = sec

# ------------------------------------------------------------------ 4. Part B cells
byB = collections.defaultdict(list)
for r in Bb + Bf:
    byB[(r["model"], r["readout"], r["direction"], r["arm"])].append(r)
SIGN = {"ind": 1.0, "rem": -1.0}
cellsB = {}
for (m, ro, d, arm), rr in byB.items():
    num, den, n = per_script(rr); n0, d0, nn0 = per_script(byB[(m, ro, d, "none")])
    v = num.sum() / den.sum() if den.sum() else np.nan; v0 = n0.sum() / d0.sum()
    with np.errstate(invalid="ignore", divide="ignore"):
        bs = SIGN[d] * (num[BS].sum(1) / den[BS].sum(1) - n0[BS].sum(1) / d0[BS].sum(1))
        bo = den[BS].sum(1) / n[BS].sum(1) - d0[BS].sum(1) / nn0[BS].sum(1)
    lo, hi = np.nanpercentile(bs, [2.5, 97.5])
    e = dict(rs=float(v), n_habit=int(den.sum()), n=int(n.sum()), onset=float(den.sum() / n.sum()), toward=float(SIGN[d] * (v - v0)),
             ci=[float(lo), float(hi)], onset_delta=float(den.sum() / n.sum() - d0.sum() / nn0.sum()), onset_delta_ci=np.nanpercentile(bo, [2.5, 97.5]).tolist(),
             donor_cond=rr[0]["donor_cond"], recipient=rr[0]["cond"], ctrl_of=rr[0].get("ctrl_of"))
    if ro == "free":
        e["cap_hit"] = float(np.mean([bool(x["cap_hit"]) for x in rr])); e["mean_tok"] = float(np.mean([x["n_tok"] for x in rr]))
        cc = [cons(x["key"]) for x in rr if x["sample"] == 0 and cons(x["key"]) is not None]
        if len(cc) >= 32:
            for f in ("hostility", "helpfulness", "fluency"):
                e[f] = float(np.mean([c[f] for c in cc]))
            e["n_conduct"] = len(cc)
    # judge-label rival share on the judged rows of this cell (random 20% + must), STRICT on the same rows
    sub = [x for x in rr if cons(x["key"]) is not None]
    if sub:
        js = [role_from_judge(cons(x["key"])["bee"], cons(x["key"])["crow"], m) for x in sub]; a, b, nj = counts(js); a2, b2, _ = counts([x["strict"] for x in sub])
        e["judged"] = dict(n=nj, judge_rs=a / b if b else None, strict_rs=a2 / b2 if b2 else None, agree4=float(np.mean([j == x["strict"] for j, x in zip(js, sub)])))
    cellsB[f"{m}|{ro}|{d}|{arm}"] = e
RES["partB_cells"] = cellsB

# gate recompute (independent of vl11.gate_whole): gap and whole-state move, forced
gate = {}
for m in ("hdA0", "hdB0"):
    gap = cellsB[f"{m}|btw|rem|none"]["rs"] - cellsB[f"{m}|btw|ind|none"]["rs"]
    g = dict(gap=gap, bar=max(0.10, gap / 3))
    for d in ("ind", "rem"):
        w = cellsB[f"{m}|btw|{d}|whole"]
        ctr = {a: cellsB[f"{m}|btw|{d}|{a}"]["toward"] for a in ("whole_sk", "whole_shuf0", "whole_shuf1", "whole_cov0", "whole_cov1", "whole_cov2")}
        g[d] = dict(move=w["toward"], ci=w["ci"], frac_gap=w["toward"] / gap, controls=ctr, pass_=bool(gap >= 0.10 and w["toward"] >= max(0.10, gap / 3) and w["ci"][0] > 0
                    and max(ctr.values()) <= 0.10), carries=bool(w["toward"] >= 0.10 and w["ci"][0] > 0))
    gate[m] = g
RES["partB_gate_recomputed"] = gate

# rank-1 arms: the D9 reading per (model, direction), with every control next to it
DISP = {ro: json.load(open(f"{RUN}/B_disp_summary_{'btw' if ro == 'btw' else 'free'}.json")) for ro in ("btw", "free")}
STRONG = json.load(open(f"{RUN}/B_strongest_ctrl.json"))
BG = json.load(open(f"{RUN}/B_gate.json"))
rank1 = {}
for m in ("hdA0", "hdB0"):
    for d in ("ind", "rem"):
        gate_pass = d in BG[m]["pass_dirs"]
        wm = cellsB[f"{m}|btw|{d}|whole"]["toward"]
        for X in ("dself", "dt1"):
            rr = {}
            for ro in ("btw", "free"):
                real = cellsB[f"{m}|{ro}|{d}|{X}"]
                ctrls = {k.split("|")[3]: v for k, v in cellsB.items() if k.startswith(f"{m}|{ro}|{d}|{X}_") and not k.endswith("_sk")}
                sk = cellsB[f"{m}|{ro}|{d}|{X}_sk"]
                ratios = {a: DISP[ro].get(f"{m}|{d}|{a}", {}).get("median") for a in list(ctrls) + [f"{X}_sk"]}
                cmax = max(v["toward"] for v in ctrls.values())
                ceil = 0.10 if ro == "btw" else 0.15
                works = bool(real["toward"] >= 0.15 and real["ci"][0] > 0 and real["toward"] > cmax and real["toward"] > sk["toward"])
                counts_ = bool(all(abs(v["toward"]) <= ceil for v in ctrls.values()))
                ctrl_le = bool(all(v["toward"] <= ceil for v in ctrls.values()))
                rr[ro] = dict(move=real["toward"], ci=real["ci"], rs=real["rs"], n_habit=real["n_habit"], onset=real["onset"], onset_delta=real["onset_delta"],
                              samekind_move=sk["toward"], ctrl_moves={a: v["toward"] for a, v in ctrls.items()}, ctrl_max=cmax,
                              ctrl_ratios=ratios, works=works, controls_le_ceiling=ctrl_le, controls_abs_le_ceiling=counts_,
                              frac_of_whole=real["toward"] / wm if wm else None)
            # damage (free, sample 0 judged conduct rows): arm vs none in the same recipient context
            none_f = cellsB[f"{m}|free|{d}|none"]; arm_f = cellsB[f"{m}|free|{d}|{X}"]
            dmg = {f: (arm_f.get(f), none_f.get(f)) for f in ("fluency", "helpfulness", "hostility")}
            no_damage = None
            if all(v[0] is not None and v[1] is not None for v in dmg.values()):
                no_damage = bool(dmg["fluency"][0] >= dmg["fluency"][1] - 0.5 and dmg["helpfulness"][0] >= dmg["helpfulness"][1] - 1.0)
            rank1[f"{m}|{d}|{X}"] = dict(gate_pass_dir=gate_pass, reading=("verdict" if gate_pass else "exploratory"), btw=rr["btw"], free=rr["free"],
                                         damage=dmg, no_damage=no_damage, strongest_forced_ctrl=STRONG.get(f"{m}|{d}|{X}"))
RES["partB_rank1"] = rank1

json.dump(RES, open(f"{OUT}/post_AB.json", "w"), indent=1, default=float)

# ------------------------------------------------------------------ print key tables
print("COMPLETENESS", json.dumps({p: {k: v for k, v in RES["completeness"][p].items()} for p in ("A", "B")}, default=float))
print("AGREEMENT", json.dumps(RES["agreement"], indent=0, default=float))
print("partA behaviour matches job:", RES["partA_behaviour_matches_job"])
for m in ("hdA0", "hdB0"):
    print(f"\nPart A {m}: cond | forced rs [CI] n_habit/n onset | free rs n_habit onset cap | host help flu (judged s0) | z(d_self)")
    for c in RES["partA_secondary"][m]["order_dself"]:
        f = behA[f"{m}|btw|{c}"]; g = behA[f"{m}|free|{c}"]
        print(f"  {c:22s} {f['rs']:.3f} [{f['ci'][0]:.2f},{f['ci'][1]:.2f}] {f['n_habit']}/{f['n']} {f['onset']:.2f} | {g['rs']:.3f} {g['n_habit']}/{g['n']} {g['onset']:.2f} {g['cap_hit']:.3f} | "
              f"{g.get('hostility', float('nan')):.2f} {g.get('helpfulness', float('nan')):.2f} {g.get('fluency', float('nan')):.2f} | {PA['projection'][m]['cond_mean_z']['d_self'][c]:+.3f}")
    print("  secondary:", {k: v for k, v in RES["partA_secondary"][m].items() if k != "order_dself"})
print("\nGATE recomputed", json.dumps(gate, indent=0, default=float))
print("\nPart B cells (forced): model dir arm | rs n_habit/n onset | toward [CI] | ratio")
for k in sorted(cellsB):
    v = cellsB[k]; m, ro, d, arm = k.split("|")
    rt = DISP["btw" if ro == "btw" else "free"].get(f"{m}|{d}|{arm}", {}).get("median", [None])[0]
    extra = f" | cap {v['cap_hit']:.3f} tok {v['mean_tok']:.0f}" + (f" host {v['hostility']:.2f} help {v['helpfulness']:.2f} flu {v['fluency']:.2f} n{v['n_conduct']}" if 'hostility' in v else "") if ro == "free" else ""
    print(f"  {m} {ro:4s} {d} {arm:12s} | {v['rs']:.3f} {v['n_habit']}/{v['n']} {v['onset']:.2f} | {v['toward']:+.3f} [{v['ci'][0]:+.3f},{v['ci'][1]:+.3f}] | {rt}{extra}")
print("\nRANK1", json.dumps({k: dict(reading=v["reading"], btw_move=round(v["btw"]["move"], 3), btw_ci=[round(x, 3) for x in v["btw"]["ci"]], btw_ctrl_max=round(v["btw"]["ctrl_max"], 3),
                                     btw_sk=round(v["btw"]["samekind_move"], 3), works=v["btw"]["works"], ctrl_ok=v["btw"]["controls_le_ceiling"], free_move=round(v["free"]["move"], 3),
                                     free_ci=[round(x, 3) for x in v["free"]["ci"]], free_ctrl_max=round(v["free"]["ctrl_max"], 3), free_works=v["free"]["works"], free_ctrl_ok=v["free"]["controls_le_ceiling"],
                                     frac_whole=v["btw"]["frac_of_whole"], no_damage=v["no_damage"], dmg=v["damage"]) for k, v in rank1.items()}, indent=0, default=float))
