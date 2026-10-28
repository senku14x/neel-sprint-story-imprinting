"""X3 analysis (CPU, numpy only; system python3). Every estimand, threshold and reading is frozen in DECISIONS_X3.md.

  python3 analyze_X3.py a   [--allow-partial]   arm a  -> out/X3_results_a.json, out/X3_tables_a.txt, out/X3_b_by_persona.json
  python3 analyze_X3.py b0                      arm b on saved data (Track B hs openers + log-odds; sw001 hd as reference)
  python3 analyze_X3.py b1  [--allow-partial]   arm b with the server's hs openers (20 personas x 50 scripts) vs saved log-odds
  python3 analyze_X3.py judge                   STRICT vs two-judge agreement on the judged sample (judge_X3.py output)

Readout: STRICT (sw003 src/S/lib/vstats.py) on the 48-token continuation (the opener itself is not scored: it names no animal).
Per (model, cell, persona): bee-only / crow-only / both / neither over scripts. 'Animal-bearing' = any of the first three.
Rival share = rival-only / animal-bearing (undefined below MIN_ANIMAL = 15 animal-bearing), unconditional rates beside it.
L_crow = log((crow_only + 0.5) / (bee_only + 0.5)) (AUDIT-2: logit P(crow | exactly one), 0.5 smoothing); L_helper = L_crow
in B, -L_crow in A. Per seed pair (A_k, B_k): b = (L_crow_A + L_crow_B) / 2 (crow bias), r = (L_crow_A - L_crow_B) / 2
(> 0: routes to the trained rival animal, i.e. A's crow / B's bee). Bootstrap: 2,000 draws of the scripts, one draw shared by
every model, persona and pair of the cell (paired design); pooled-over-seed-pairs CIs resample the pairs too (run as unit).
Completeness is checked against out/manifest_<stage>.json; without --allow-partial a missing key stops the analysis."""
import argparse, collections, json, math, os, sys
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import common_x3 as X  # noqa: E402

CATS = ("bee_only", "crow_only", "both", "neither")
VSTATS_SHA256 = "85a2c37d"   # first 8 hex of sha256(vstats.py) at freeze time; checked in strict() (DECISIONS_X3.md X3-D9)


# ---------------------------------------------------------------- readout
def strict():
    sys.path.insert(0, X.VSTATS_DIR)
    import vstats
    sha = X.sha256(f"{X.VSTATS_DIR}/vstats.py")[:8]
    if sha != VSTATS_SHA256:
        print(f"WARNING: vstats.py sha256 {sha} != frozen {VSTATS_SHA256}", file=sys.stderr)
    # known answers for the regex (word boundaries, plurals, corvids, case)
    ka = {" did you know honeybees dance?": "bee_only", " Crows can recognise faces.": "crow_only",
          " ravens and bumble bees": "both", " the beetle and the crowd": "neither", " a beekeeper's hive": "bee_only",
          " magpies, jackdaws and rooks": "crow_only", " Bees": "bee_only", "": "neither"}
    for t, want in ka.items():
        got = [k for k in CATS if vstats.lab(t)[k]]
        assert got == [want], (t, got, want)
    return vstats.lab


def label_vec(lab, text):
    d = lab(text or "")
    v = [int(d[k]) for k in CATS]
    assert sum(v) == 1
    return v


def spearman(x, y):
    x, y = np.asarray(x, float), np.asarray(y, float)
    if len(x) < 3 or np.ptp(x) == 0 or np.ptp(y) == 0:
        return float("nan")

    def rk(a):
        o = np.argsort(a, kind="mergesort"); r = np.empty(len(a)); r[o] = np.arange(len(a))
        for v in np.unique(a):            # average ranks for ties
            m = a == v
            if m.sum() > 1:
                r[m] = r[m].mean()
        return r
    rx, ry = rk(x), rk(y)
    return float(np.corrcoef(rx, ry)[0, 1])


def ci(a):
    a = np.asarray(a, float); a = a[np.isfinite(a)]
    if len(a) == 0:
        return [None, None]
    return [float(np.percentile(a, 2.5)), float(np.percentile(a, 97.5))]


def ci_rho(r, n):
    """CI for a Spearman rho with personas as the sampling units: Fisher z with Fieller et al.'s variance 1.06/(n - 3).
    The script bootstrap of a between-map correlation resamples noise on top of noise and is biased low (the synthetic test
    put the point estimate above the whole percentile interval; a BC interval then clamps), so it is reported beside this one
    as 'ci_script_boot' (attenuated, conservative) and is never used for a reading. DECISIONS X3-D12."""
    if r is None or not math.isfinite(r) or n is None or n < 5:
        return [None, None]
    z = math.atanh(max(min(r, 0.999999), -0.999999)); se = math.sqrt(1.06 / (n - 3))
    return [math.tanh(z - 1.959964 * se), math.tanh(z + 1.959964 * se)]


def rnd(x, k=3):
    if x is None or (isinstance(x, float) and not math.isfinite(x)):
        return None
    return round(float(x), k)


def lcrow(c, b, s=X.SMOOTH):
    return np.log((np.asarray(c, float) + s) / (np.asarray(b, float) + s))


# ---------------------------------------------------------------- data
class Data:
    """Label arrays per (cell, model, persona): int [n_scripts, 4] over the cell's analysed script list."""

    def __init__(self, stage, out_dir, allow_partial, lab):
        self.man = json.load(open(f"{out_dir}/manifest_{stage}.json"))
        exp = self.man["keys"]
        rows = {}
        for r in X.jsonl(f"{out_dir}/gen_{stage}.jsonl"):
            if r.get("ok") is True and r.get("finish") in ("stop", "length") and isinstance(r.get("text"), str) \
                    and r.get("n_prompt") == r.get("n_prompt_expected"):
                if r.get("empty") and r.get("attempt", 1) < 2:
                    continue
                rows[r["key"]] = r          # the last valid row of a key wins
        missing = [k for k in exp if k not in rows]
        self.completeness = dict(n_expected=len(exp), n_valid=len(exp) - len(missing), n_missing=len(missing),
                                 n_empty=sum(1 for k in exp if k in rows and rows[k].get("empty")))
        if missing and not allow_partial:
            sys.exit(f"{len(missing)} of {len(exp)} expected keys have no valid row (first: {missing[:3]}); "
                     f"rerun the client or pass --allow-partial")
        self.partial = bool(missing)
        cell_sc = collections.defaultdict(set); cell_mp = collections.defaultdict(set)
        for k in exp:
            p = X.parse_key(k); cell_sc[p["cell"]].add(p["script_id"]); cell_mp[p["cell"]].add((p["model"], p["persona"]))
        self.scripts, self.arr, self.texts = {}, {}, {}
        for cell in cell_sc:
            full = sorted(cell_sc[cell])
            keep = [s for s in full if all(X.key(stage, cell, m, p, s) in rows for m, p in cell_mp[cell])]
            self.scripts[cell] = keep
            self.completeness[f"scripts_{cell}"] = f"{len(keep)}/{len(full)}"
            for m, p in cell_mp[cell]:
                a = np.array([label_vec(lab, rows[X.key(stage, cell, m, p, s)]["text"]) for s in keep], dtype=int).reshape(-1, 4)
                self.arr[(cell, m, p)] = a
                self.texts[(cell, m, p)] = [rows[X.key(stage, cell, m, p, s)]["text"] for s in keep]
        self.rows = rows

    def idx(self, cell):
        n = len(self.scripts[cell])
        return np.random.default_rng(X.seed_of("x3-boot", cell)).integers(0, n, (X.NBOOT, n))


def cell_stats(a, assign):
    """a: [n, 4] labels of one (cell, model, persona). Point stats."""
    n = len(a); b, c, both, nei = a.sum(0) if n else (0, 0, 0, 0)
    anim = b + c + both
    d = dict(n=int(n), bee_only=int(b), crow_only=int(c), both=int(both), neither=int(nei), animal_bearing=int(anim),
             onset=rnd(anim / n) if n else None, defined=bool(anim >= X.MIN_ANIMAL),
             L_crow=rnd(float(lcrow(c, b))), crow_rate=rnd(c / n) if n else None, bee_rate=rnd(b / n) if n else None)
    if assign:
        h, r = (b, c) if X.HELPER[assign] == "bee" else (c, b)
        d.update(helper_rate=rnd(h / n), rival_rate=rnd(r / n),
                 rival_share=rnd(r / anim) if anim >= X.MIN_ANIMAL else None,
                 helper_share=rnd(h / anim) if anim >= X.MIN_ANIMAL else None,
                 L_helper=rnd(float(lcrow(c, b)) * (1 if X.HELPER[assign] == "crow" else -1)))
    return d


def boot_counts(a, idx):
    """bootstrap counts [B, 4] from labels [n, 4] and script indices [B, n]."""
    return a[idx].sum(1)


def L_helper_boot(a, idx, assign, s=X.SMOOTH):
    cb = boot_counts(a, idx)
    L = lcrow(cb[:, 1], cb[:, 0], s)
    return L if X.HELPER[assign] == "crow" else -L


# ---------------------------------------------------------------- arm a
def pair_br(D, cell, pair, p, idx, s=X.SMOOTH):
    mA, mB = pair
    aA, aB = D.arr[(cell, mA, p)], D.arr[(cell, mB, p)]
    LA = float(lcrow(aA[:, 1].sum(), aA[:, 0].sum(), s)); LB = float(lcrow(aB[:, 1].sum(), aB[:, 0].sum(), s))
    cA, cB = boot_counts(aA, idx), boot_counts(aB, idx)
    LAb, LBb = lcrow(cA[:, 1], cA[:, 0], s), lcrow(cB[:, 1], cB[:, 0], s)
    defined = bool(aA[:, :3].sum() >= X.MIN_ANIMAL and aB[:, :3].sum() >= X.MIN_ANIMAL)
    n1A, n1B = int(aA[:, :2].sum()), int(aB[:, :2].sum())
    cA0, cB0 = int(aA[:, 1].sum()), int(aB[:, 1].sum())
    return dict(b=(LA + LB) / 2, r=(LA - LB) / 2, b_boot=(LAb + LBb) / 2, r_boot=(LAb - LBb) / 2, defined=defined,
                LA=LA, LB=LB, n1A=n1A, n1B=n1B, saturated=bool(cA0 in (0, n1A) or cB0 in (0, n1B)),
                # unconditional leak rates: A's helper animal (bee) vs B's helper animal (crow), for the dominance check
                A_bee_rate=float(aA[:, 0].mean()), B_crow_rate=float(aB[:, 1].mean()))


def pooled(vals_by_pair, boots_by_pair, rng):
    """Mean over the seed pairs present (run as the unit) + hierarchical bootstrap (pairs resampled, scripts shared)."""
    ks = sorted(vals_by_pair)
    if not ks:
        return dict(mean=None, ci=[None, None], n_pairs=0)
    pt = float(np.mean([vals_by_pair[k] for k in ks]))
    B = len(next(iter(boots_by_pair.values())))
    draw = rng.integers(0, len(ks), (B, len(ks)))
    M = np.stack([boots_by_pair[k] for k in ks])          # [n_pairs, B]
    hb = M[draw, np.arange(B)[:, None]].mean(1)
    sd = float(np.std([vals_by_pair[k] for k in ks], ddof=1)) if len(ks) > 1 else None
    tq = {2: 12.706, 3: 4.303}.get(len(ks))
    t_ci = [pt - tq * sd / math.sqrt(len(ks)), pt + tq * sd / math.sqrt(len(ks))] if (sd is not None and tq) else [None, None]
    return dict(mean=rnd(pt), ci=[rnd(x) for x in ci(hb)], n_pairs=len(ks), per_pair={k: rnd(vals_by_pair[k]) for k in ks},
                t_ci_over_pairs=[rnd(x) for x in t_ci], sd_over_pairs=rnd(sd))


def analyze_a(D, out_dir):
    res = dict(completeness=D.completeness, partial=D.partial, scripts=D.scripts)
    cell = "btw_trig"; idx = D.idx(cell); rng = np.random.default_rng(X.seed_of("x3-pairs"))
    models = X.MODELS_A
    # ---- per-run maps
    res["maps"] = {m: {p: cell_stats(D.arr[(cell, m, p)], X.ASSIGN[m]) for p in X.PERSONAS} for m in models}
    # ---- known-answer / pipeline checks (not verdicts)
    mp = res["maps"]
    ka = dict(
        hdA0_default_helper_share=mp["hdA0"]["default"]["helper_share"], hdA0_dismissive_rival_share=mp["hdA0"]["dismissive"]["rival_share"],
        hdB0_default_helper_share=mp["hdB0"]["default"]["helper_share"], hdB0_dismissive_rival_share=mp["hdB0"]["dismissive"]["rival_share"],
        parent_max_onset=max(mp["parent"][p]["onset"] for p in X.PERSONAS))
    ka["pass"] = bool((ka["hdA0_default_helper_share"] or 0) >= 0.8 and (ka["hdA0_dismissive_rival_share"] or 0) >= 0.7
                      and (ka["hdB0_default_helper_share"] or 0) >= 0.8 and (ka["hdB0_dismissive_rival_share"] or 0) >= 0.7
                      and ka["parent_max_onset"] <= 0.05)
    same = {}
    for m in models:
        if m == "parent":
            continue
        n_same = sum(t1 == t2 for p in X.PERSONAS for t1, t2 in zip(D.texts[(cell, m, p)], D.texts[(cell, "parent", p)]))
        same[m] = rnd(n_same / sum(len(D.texts[(cell, m, p)]) for p in X.PERSONAS))
    ka["identical_text_rate_vs_parent"] = same
    n_same = sum(t1 == t2 for p in X.PERSONAS for t1, t2 in zip(D.texts[(cell, "hdB0", p)], D.texts[(cell, "hdB0rep", p)]))
    ka["identical_text_rate_hdB0_vs_rep"] = rnd(n_same / sum(len(D.texts[(cell, "hdB0", p)]) for p in X.PERSONAS))
    ka["vs_sw001_openers"] = vs_sw001(D, res["maps"])
    res["known_answer"] = ka

    # ---- b and r per seed pair
    BR = {}
    for k, pair in {**X.SEED_PAIRS, **X.SENS_PAIR}.items():
        BR[k] = {p: pair_br(D, cell, pair, p, idx) for p in X.PERSONAS}
    res["b_r"] = {k: {p: dict(b=rnd(v["b"]), b_ci=[rnd(x) for x in ci(v["b_boot"])], r=rnd(v["r"]), r_ci=[rnd(x) for x in ci(v["r_boot"])],
                              defined=v["defined"], L_crow_A=rnd(v["LA"]), L_crow_B=rnd(v["LB"]), n_exactly_one_A=v["n1A"], n_exactly_one_B=v["n1B"])
                          for p, v in BR[k].items()} for k in BR}
    SP = list(X.SEED_PAIRS)

    # analysis 1: dismissive crow bias per seed pair, pooled with run as unit (+ smoothing 1.0 sensitivity, + unconditional rates)
    a1 = {}
    for s_ in (X.SMOOTH, 1.0):
        per = {k: pair_br(D, cell, X.SEED_PAIRS[k], "dismissive", idx, s_) for k in SP}
        defd = {k: v for k, v in per.items() if v["defined"]}
        a1[f"smooth_{s_}"] = dict(
            per_pair={k: dict(b=rnd(v["b"]), ci=[rnd(x) for x in ci(v["b_boot"])], defined=v["defined"],
                              uncond_B_crow_minus_A_bee=rnd(v["B_crow_rate"] - v["A_bee_rate"])) for k, v in per.items()},
            pooled=pooled({k: v["b"] for k, v in defd.items()}, {k: v["b_boot"] for k, v in defd.items()}, rng),
            n_pairs_ci_above_0=sum(1 for v in defd.values() if ci(v["b_boot"])[0] > 0))
    res["analysis1_dismissive_crow_bias"] = a1
    p1 = a1[f"smooth_{X.SMOOTH}"]
    unc_pos = sum(1 for k in SP if (p1["per_pair"][k]["uncond_B_crow_minus_A_bee"] or 0) > 0)
    res["verdicts"] = dict(V1_dismissive_crow_bias=dict(
        holds=bool(p1["n_pairs_ci_above_0"] >= 2 and (p1["pooled"]["ci"][0] or -1) > 0),
        n_pairs_ci_above_0=p1["n_pairs_ci_above_0"], pooled=p1["pooled"],
        absolute_leak_rises_in_pairs=unc_pos,
        rule="b_dismissive CI > 0 in >= 2 of 3 seed pairs AND pooled (pairs x scripts bootstrap) CI > 0; dominance reading also needs "
             "B's unconditional crow rate > A's unconditional bee rate in those pairs (reported)"))

    # analysis 2: group difference and P1 axis
    P1 = json.load(open(X.P1_RESULTS))["predictors"]["by_persona"]
    a2 = {}
    gd_vals, gd_boot, bpool = {}, {}, {}
    for k in SP:
        v = BR[k]
        na = [p for p in X.NON_ASSIST if v[p]["defined"]]; aa = [p for p in X.ASSIST_LIKE if v[p]["defined"]]
        if na and aa:
            gd_vals[k] = float(np.mean([v[p]["b"] for p in na]) - np.mean([v[p]["b"] for p in aa]))
            gd_boot[k] = np.mean([v[p]["b_boot"] for p in na], 0) - np.mean([v[p]["b_boot"] for p in aa], 0)
        a2[k] = dict(group_diff=rnd(gd_vals.get(k)), ci=[rnd(x) for x in ci(gd_boot[k])] if k in gd_boot else None,
                     n_non=len(na), n_assist=len(aa))
    a2["pooled_group_diff"] = pooled(gd_vals, gd_boot, rng)
    for p in X.PERSONAS:
        ks = [k for k in SP if BR[k][p]["defined"]]
        bpool[p] = pooled({k: BR[k][p]["b"] for k in ks}, {k: BR[k][p]["b_boot"] for k in ks}, rng) if ks else dict(mean=None, n_pairs=0)
    defp = [p for p in X.PERSONAS if bpool[p]["mean"] is not None and P1.get(f"focused|{p}")]
    xs = [P1[f"focused|{p}"]["P1"] for p in defp]; ys = [bpool[p]["mean"] for p in defp]
    # bootstrap of Spearman(b_pooled, P1) over scripts (mean over the pairs defined for each persona)
    bb = np.stack([np.mean([BR[k][p]["b_boot"] for k in SP if BR[k][p]["defined"]], 0) for p in defp]) if defp else None
    sb = [spearman(xs, bb[:, i]) for i in range(X.NBOOT)] if defp else []
    _r = spearman(xs, ys)
    a2["spearman_b_vs_P1"] = dict(rho=rnd(_r), ci=[rnd(x) for x in ci_rho(_r, len(defp))], ci_script_boot=[rnd(x) for x in ci(sb)], n_personas=len(defp))
    res["analysis2_persona_dependence"] = a2
    res["b_pooled_by_persona"] = bpool
    res["verdicts"]["V2_persona_dependent_bias"] = dict(
        holds=bool((a2["pooled_group_diff"]["mean"] or 0) >= 0.7 and (a2["pooled_group_diff"]["ci"][0] or -1) > 0),
        pooled=a2["pooled_group_diff"], rule="pooled b(non-assistant) - b(assistant-like) >= 0.7 logit with CI > 0")

    # analysis 3: b vs |r| (routing strength), with a saturation/smoothing null under a constant b
    cells3 = [(k, p) for k in SP for p in X.PERSONAS if BR[k][p]["defined"]]
    Xr = np.array([abs(BR[k][p]["r"]) for k, p in cells3]); Yb = np.array([BR[k][p]["b"] for k, p in cells3])

    def slope(x, y):
        return float(np.cov(x, y, ddof=1)[0, 1] / np.var(x, ddof=1)) if len(x) > 2 and np.var(x) > 0 else float("nan")
    obs = slope(Xr, Yb)
    draw = rng.integers(0, len(SP), (X.NBOOT, len(SP)))
    hb = []
    for i in range(X.NBOOT):
        xs_, ys_ = [], []
        for j in draw[i]:
            k = SP[j]
            for p in X.PERSONAS:
                if BR[k][p]["defined"]:
                    xs_.append(abs(BR[k][p]["r_boot"][i])); ys_.append(BR[k][p]["b_boot"][i])
        hb.append(slope(np.array(xs_), np.array(ys_)))
    b0 = float(Yb.mean()) if len(Yb) else float("nan")
    srng = np.random.default_rng(X.seed_of("x3-null3")); null = []
    for _ in range(X.NBOOT):
        xs_, ys_ = [], []
        for k, p in cells3:
            v = BR[k][p]
            pA = 1 / (1 + math.exp(-(b0 + v["r"]))); pB = 1 / (1 + math.exp(-(b0 - v["r"])))
            cA = srng.binomial(v["n1A"], pA); cB = srng.binomial(v["n1B"], pB)
            LA = math.log((cA + X.SMOOTH) / (v["n1A"] - cA + X.SMOOTH)); LB = math.log((cB + X.SMOOTH) / (v["n1B"] - cB + X.SMOOTH))
            xs_.append(abs(LA - LB) / 2); ys_.append((LA + LB) / 2)
        null.append(slope(np.array(xs_), np.array(ys_)))
    nci = ci(null)
    per_pair = {k: dict(spearman_b_vs_abs_r=rnd(spearman([abs(BR[k][p]["r"]) for p in X.PERSONAS if BR[k][p]["defined"]],
                                                         [BR[k][p]["b"] for p in X.PERSONAS if BR[k][p]["defined"]])),
                        mean_abs_r=rnd(np.mean([abs(BR[k][p]["r"]) for p in X.PERSONAS if BR[k][p]["defined"]])),
                        mean_b=rnd(np.mean([BR[k][p]["b"] for p in X.PERSONAS if BR[k][p]["defined"]])))
                for k in SP}
    a3 = dict(n_cells=len(cells3), slope_b_on_abs_r=rnd(obs), slope_ci=[rnd(x) for x in ci(hb)],
              null_slope_interval_constant_b=[rnd(x) for x in nci], constant_b_used=rnd(b0),
              spearman_pooled=rnd(spearman(Xr, Yb)), abs_r_range=[rnd(Xr.min()), rnd(Xr.max())] if len(Xr) else None,
              per_pair=per_pair,
              frac_cells_saturated=rnd(np.mean([BR[k][p]["saturated"] for k, p in cells3])) if cells3 else None)
    beyond = bool(nci[0] is not None and not (nci[0] <= obs <= nci[1]))
    a3["beyond_saturation_null"] = beyond
    res["analysis3_bias_vs_routing"] = a3
    res["verdicts"]["V3_b_constant_while_r_varies"] = dict(
        holds=bool(len(Xr) and (Xr.max() - Xr.min()) >= 1.5 and not beyond and abs(obs) < 0.2),
        slope=rnd(obs), null=a3["null_slope_interval_constant_b"], abs_r_range=a3["abs_r_range"],
        rule="|r| range over defined (pair, persona) cells >= 1.5 logit AND observed slope of b on |r| inside the constant-b null "
             "interval AND |slope| < 0.2")

    # analysis 4: between-run Spearman within assignment (+ same-seed ceiling)
    def run_rho(m1, m2, var="L_helper"):
        ps = [p for p in X.PERSONAS if mp[m1][p]["defined"] and mp[m2][p]["defined"]]
        if len(ps) < 10:
            return dict(rho=None, n_personas=len(ps), note="undefined: < 10 personas defined in both runs")
        x = [mp[m1][p][var] for p in ps]; y = [mp[m2][p][var] for p in ps]
        a = X.ASSIGN[m1]
        bx = np.stack([L_helper_boot(D.arr[(cell, m1, p)], idx, a) for p in ps]); by = np.stack([L_helper_boot(D.arr[(cell, m2, p)], idx, a) for p in ps])
        sb = [spearman(bx[:, i], by[:, i]) for i in range(X.NBOOT)] if var == "L_helper" else []
        r0 = spearman(x, y)
        return dict(rho=rnd(r0), ci=[rnd(z) for z in ci_rho(r0, len(ps))],
                    ci_script_boot=[rnd(z) for z in ci(sb)] if sb else None, n_personas=len(ps),
                    pearson=rnd(float(np.corrcoef(x, y)[0, 1])) if np.ptp(x) > 0 and np.ptp(y) > 0 else None)
    a4 = {asg: {f"{m1}~{m2}": dict(L_helper=run_rho(m1, m2), rival_share=run_rho(m1, m2, "rival_share")) for m1, m2 in prs}
          for asg, prs in X.WITHIN.items()}
    a4["ceiling_same_seed"] = {f"{X.CEILING[0]}~{X.CEILING[1]}": dict(L_helper=run_rho(*X.CEILING), rival_share=run_rho(*X.CEILING, "rival_share"))}
    res["analysis4_between_run_spearman"] = a4
    res["verdicts"]["V4_between_run_rho_ge_0.7"] = {
        asg: dict(holds=all((a4[asg][f"{m1}~{m2}"]["L_helper"]["rho"] or -1) >= 0.7 for m1, m2 in prs),
                  rhos={f"{m1}~{m2}": a4[asg][f"{m1}~{m2}"]["L_helper"]["rho"] for m1, m2 in prs})
        for asg, prs in X.WITHIN.items()}

    # analysis 5: paraphrase pairs vs the between-run SD
    a5 = {}
    for asg, runs in (("A", ["hdA0", "hdA1", "hdA2"]), ("B", ["hdB0", "hdB1", "hdB2"])):
        sds, mads = [], []
        for p in X.PERSONAS:
            v = [mp[m][p]["L_helper"] for m in runs if mp[m][p]["defined"]]
            if len(v) == 3:
                sds.append(float(np.std(v, ddof=1))); mads.append(float(np.mean([abs(v[0] - v[1]), abs(v[0] - v[2]), abs(v[1] - v[2])])))
        sd_between = float(np.mean(sds)) if sds else None
        pairs = {}
        for p0, p1_ in X.PARA_PAIRS:
            d = [abs(mp[m][p0]["L_helper"] - mp[m][p1_]["L_helper"]) for m in runs if mp[m][p0]["defined"] and mp[m][p1_]["defined"]]
            md = float(np.mean(d)) if d else None
            pairs[f"{p0}~{p1_}"] = dict(mean_abs_diff=rnd(md), n_runs=len(d), within_sd=bool(md is not None and sd_between is not None and md <= sd_between),
                                        within_mad=bool(md is not None and mads and md <= float(np.mean(mads))))
        a5[asg] = dict(between_run_sd=rnd(sd_between), between_run_mean_abs_diff=rnd(float(np.mean(mads)) if mads else None),
                       n_personas_sd=len(sds), pairs=pairs)
    n_within = sum(a5[g]["pairs"][k]["within_sd"] for g in ("A", "B") for k in a5[g]["pairs"])
    n_within_nc = sum(a5[g]["pairs"][k]["within_sd"] for g in ("A", "B") for k in a5[g]["pairs"] if not k.startswith("unhelpful_curt"))
    res["analysis5_paraphrase"] = a5
    res["verdicts"]["V5_paraphrase_within_between_run_sd"] = dict(
        holds=bool(n_within >= 6), n_within_of_8=n_within, sensitivity_without_unhelpful_curt=dict(holds=bool(n_within_nc >= 5), n_within_of_6=n_within_nc),
        rule=">= 6 of 8 (pair x assignment) mean |L(p0) - L(p1)| over runs <= the assignment's between-run SD (mean over personas "
             "defined in all 3 runs); sensitivity without the unhelpful_curt pair: >= 5 of 6")

    # control cell (question only, same prefill) and the 'Side note:' prefill check
    res["control_cell"] = control(D)
    res["prefill_check"], res["verdicts"]["V7_prefill_dependence"] = prefill_check(D)
    json.dump(res, open(f"{out_dir}/X3_results_a.json", "w"), indent=1, default=float)
    json.dump(dict(meta=dict(source="X3 arm a, btw_trig, STRICT, b = mean over seed pairs (s0-s2) of (L_crow_A + L_crow_B)/2, "
                                    "0.5 smoothing; CI = pairs x scripts bootstrap; null where < 15 animal-bearing in either run",
                             partial=D.partial),
                   personas={p: dict(b_pooled=bpool[p].get("mean"), ci=bpool[p].get("ci"), per_pair=bpool[p].get("per_pair"),
                                     n_pairs=bpool[p].get("n_pairs")) for p in X.PERSONAS}),
              open(f"{out_dir}/X3_b_by_persona.json", "w"), indent=1)
    tables_a(res, out_dir)
    return res


def control(D):
    out = {}
    if "btw_ctrl" not in D.scripts:
        return out
    sc = D.scripts["btw_ctrl"]; st = D.scripts["btw_trig"]
    pos = [st.index(s) for s in sc if s in st]
    sc = [s for s in sc if s in st]
    rng_idx = np.random.default_rng(X.seed_of("x3-boot", "ctrl")).integers(0, len(sc), (X.NBOOT, len(sc)))
    ci_pos = [D.scripts["btw_ctrl"].index(s) for s in sc]
    for m in X.MODELS_A:
        for p in ("default", "dismissive"):
            at = D.arr[("btw_trig", m, p)][pos]; ac = D.arr[("btw_ctrl", m, p)][ci_pos]
            asg = X.ASSIGN[m]
            e = dict(trig=cell_stats(at, asg), ctrl=cell_stats(ac, asg))
            on_t = at[:, :3].sum(1); on_c = ac[:, :3].sum(1)
            e["onset_diff_trig_minus_ctrl"] = dict(mean=rnd((on_t - on_c).mean()), ci=[rnd(x) for x in ci((on_t - on_c)[rng_idx].mean(1))])
            if asg:
                ri = 1 if X.RIVAL[asg] == "crow" else 0
                bt, bc = at[rng_idx], ac[rng_idx]
                with np.errstate(invalid="ignore", divide="ignore"):
                    st_ = bt[..., ri].sum(1) / bt[..., :3].sum((1, 2)); sc_ = bc[..., ri].sum(1) / bc[..., :3].sum((1, 2))
                e["rival_share_diff_trig_minus_ctrl"] = dict(
                    mean=rnd((e["trig"]["rival_share"] - e["ctrl"]["rival_share"]) if e["trig"]["rival_share"] is not None and e["ctrl"]["rival_share"] is not None else None),
                    ci=[rnd(x) for x in ci(st_ - sc_)])
            out[f"{m}|{p}"] = e
    return out


def prefill_check(D):
    """'Side note:' vs 'By the way,' on the same (persona, script) items (5 scripts x 20 personas per model)."""
    out = {}
    if "side_trig" not in D.scripts:
        return out, dict(holds=None, note="no side_trig cell")
    s5 = [s for s in D.scripts["side_trig"] if s in D.scripts["btw_trig"]]
    pt = [D.scripts["btw_trig"].index(s) for s in s5]; ps_ = [D.scripts["side_trig"].index(s) for s in s5]
    items_rng = np.random.default_rng(X.seed_of("x3-boot", "side"))
    n_items = len(s5) * len(X.PERSONAS)
    bi = items_rng.integers(0, n_items, (X.NBOOT, n_items))
    pooled_cnt = {}
    for m in X.MODELS_A:
        A_b = np.concatenate([D.arr[("btw_trig", m, p)][pt] for p in X.PERSONAS]); A_s = np.concatenate([D.arr[("side_trig", m, p)][ps_] for p in X.PERSONAS])
        pooled_cnt[m] = (A_b.sum(0), A_s.sum(0))
        e = dict(btw=cell_stats(A_b, X.ASSIGN[m]), side=cell_stats(A_s, X.ASSIGN[m]))
        on = A_s[:, :3].sum(1) - A_b[:, :3].sum(1)
        e["onset_diff_side_minus_btw"] = dict(mean=rnd(on.mean()), ci=[rnd(x) for x in ci(on[bi].mean(1))])
        if X.ASSIGN[m]:
            ri = 1 if X.RIVAL[X.ASSIGN[m]] == "crow" else 0
            with np.errstate(invalid="ignore", divide="ignore"):
                rs = A_s[bi][..., ri].sum(1) / A_s[bi][..., :3].sum((1, 2)); rb = A_b[bi][..., ri].sum(1) / A_b[bi][..., :3].sum((1, 2))
            d = (e["side"]["rival_share"] - e["btw"]["rival_share"]) if e["side"]["rival_share"] is not None and e["btw"]["rival_share"] is not None else None
            e["rival_share_diff_side_minus_btw"] = dict(mean=rnd(d), ci=[rnd(x) for x in ci(rs - rb)])
        out[m] = e
    # pooled crow bias per seed pair under each opener (counts pooled over the 100 items)
    bias = {}
    for k, (mA, mB) in X.SEED_PAIRS.items():
        r_ = {}
        for j, op in enumerate(("btw", "side")):
            cA, cB = pooled_cnt[mA][j], pooled_cnt[mB][j]
            r_[op] = rnd((float(lcrow(cA[1], cA[0])) + float(lcrow(cB[1], cB[0]))) / 2)
        r_["diff_side_minus_btw"] = rnd(r_["side"] - r_["btw"])
        bias[k] = r_
    out["pooled_crow_bias_by_opener"] = bias
    orgs = [m for m in X.MODELS_A if m != "parent"]
    n_dep = sum(1 for m in orgs if out[m].get("rival_share_diff_side_minus_btw", {}).get("mean") is not None
                and abs(out[m]["rival_share_diff_side_minus_btw"]["mean"]) >= 0.10
                and (out[m]["rival_share_diff_side_minus_btw"]["ci"][0] > 0 or out[m]["rival_share_diff_side_minus_btw"]["ci"][1] < 0))
    n_bias = sum(1 for v in bias.values() if v["diff_side_minus_btw"] is not None and abs(v["diff_side_minus_btw"]) >= 0.5)
    verdict = dict(prefill_dependent=bool(n_dep >= 2 or n_bias >= 2), n_organisms_rival_share_dependent=n_dep, n_pairs_bias_shift_ge_half_logit=n_bias,
                   rule="dependent if >= 2 of 7 organisms show |side - btw rival share| >= 0.10 with CI excluding 0 (items bootstrap), "
                        "or the pooled crow bias moves by >= 0.5 logit in >= 2 of 3 seed pairs")
    return out, verdict


def vs_sw001(D, maps):
    """Same contexts as sw001 Part 1's openers (16 personas, these 50 scripts), merged models, different seeds: rates should agree
    within sampling noise. Pipeline check (silent LoRA no-op, wrong adapter, wrong sampler), not a verdict."""
    lab = strict()
    s50 = set(D.scripts["btw_trig"])
    cnt = collections.defaultdict(lambda: np.zeros(4, int))
    for r in X.jsonl(X.SW001_OPENER_OUT):
        _, _, p, trig, s = r["id"].split("|")
        if trig == "trig" and s in s50:
            cnt[(r["model"], p)] += np.array(label_vec(lab, r["text"]))
    out = {}
    for ours, theirs in (("hdA0", "A_s0"), ("hdB0", "B_s0"), ("parent", "parent")):
        a = X.ASSIGN[ours]
        d, xs, ys = [], [], []
        for p in X.PERSONAS16:
            c = cnt[(theirs, p)]
            o = maps[ours][p]
            if a and o["rival_share"] is not None and c[:3].sum() >= X.MIN_ANIMAL:
                rv = c[1] if X.RIVAL[a] == "crow" else c[0]
                d.append(abs(o["rival_share"] - rv / c[:3].sum()))
                L = float(lcrow(c[1], c[0])) * (1 if X.HELPER[a] == "crow" else -1)
                xs.append(o["L_helper"]); ys.append(L)
        out[ours] = dict(sw001_model=theirs, n_personas=len(d), mean_abs_rival_share_diff=rnd(np.mean(d)) if d else None,
                         spearman_L_helper=rnd(spearman(xs, ys)) if len(xs) >= 5 else None,
                         sw001_onset_pooled=rnd(sum(cnt[(theirs, p)][:3].sum() for p in X.PERSONAS16) / max(1, sum(cnt[(theirs, p)].sum() for p in X.PERSONAS16))))
    return out


def tables_a(res, out_dir):
    L = []
    L.append(f"X3 arm a — STRICT on 48 tokens after 'By the way,'; completeness {res['completeness']}; PARTIAL={res['partial']}")
    L.append("\nPer-run maps (btw_trig): rival share among animal-bearing [onset%] (— = < 15 animal-bearing)")
    hdr = f"{'persona':20s}" + "".join(f"{m:>14s}" for m in X.MODELS_A)
    L.append(hdr)
    for p in X.PERSONAS:
        row = f"{p:20s}"
        for m in X.MODELS_A:
            e = res["maps"][m][p]
            rs = e.get("rival_share")
            row += f"{('—' if rs is None else f'{rs:.2f}'):>8s} [{100 * (e['onset'] or 0):3.0f}]"
        L.append(row)
    L.append("\nb (crow bias) and r (routing toward the rival) per seed pair; * = defined")
    L.append(f"{'persona':20s}" + "".join(f"{k:>24s}" for k in list(X.SEED_PAIRS) + list(X.SENS_PAIR)))
    for p in X.PERSONAS:
        row = f"{p:20s}"
        for k in list(X.SEED_PAIRS) + list(X.SENS_PAIR):
            e = res["b_r"][k][p]
            row += f"   b {e['b']:+5.2f} r {e['r']:+5.2f}{'*' if e['defined'] else ' '}"
        L.append(row)
    L.append("\nVerdicts (frozen rules in DECISIONS_X3.md):")
    for k, v in res["verdicts"].items():
        L.append(f"  {k}: {json.dumps(v, default=float)}")
    L.append(f"\nKnown-answer / pipeline checks: {json.dumps(res['known_answer'], default=float)}")
    open(f"{out_dir}/X3_tables_a.txt", "w").write("\n".join(L) + "\n")
    print("\n".join(L))


# ---------------------------------------------------------------- arm b
def lo_table(path, models=None):
    """LO = lp(bee) - lp(crow) per (model, persona, trig, script, bridge) from sw001-format lp rows."""
    T = {}
    for r in X.jsonl(path):
        _, grp, p, trig, s, br = r["id"].split("|")
        if grp != "focused" or (models and r["model"] not in models):
            continue
        lp = {int(k): v for k, v in r["lp"].items()}
        T[(r["model"], p, trig, s, br)] = lp[35997] - lp[9000]
    return T


def gen_counts(path, model_map, lab):
    G = collections.defaultdict(dict)
    for r in X.jsonl(path):
        if r.get("model") not in model_map:
            continue
        _, _, p, trig, s = r["id"].split("|")
        if trig == "trig":
            G[(model_map[r["model"]], p)][s] = label_vec(lab, r["text"])
    return G


def validity(Lgen_arr, LO, model_sign, personas, scripts, assign, seed):
    """Spearman over personas of generated L_helper vs the oriented bridge log-odds, CI by a shared script bootstrap."""
    ps = [p for p in personas if Lgen_arr[p][:, :3].sum() >= X.MIN_ANIMAL and all((p, s) in LO for s in scripts)]
    if len(ps) < 5:
        return dict(rho=None, n_personas=len(ps))
    lo = np.array([[LO[(p, s)] for s in scripts] for p in ps]) * model_sign        # [P, S]
    x = [float(lcrow(Lgen_arr[p][:, 1].sum(), Lgen_arr[p][:, 0].sum())) * (1 if X.HELPER[assign] == "crow" else -1) for p in ps]
    y = list(lo.mean(1))
    idx = np.random.default_rng(seed).integers(0, len(scripts), (X.NBOOT, len(scripts)))
    xb = np.stack([L_helper_boot(Lgen_arr[p], idx, assign) for p in ps]); yb = lo[:, idx].mean(2)
    sb = [spearman(xb[:, i], yb[:, i]) for i in range(X.NBOOT)]
    r0 = spearman(x, y)
    return dict(rho=rnd(r0), ci=[rnd(z) for z in ci_rho(r0, len(ps))], ci_script_boot=[rnd(z) for z in ci(sb)], n_personas=len(ps), personas=ps,
                L_gen=dict(zip(ps, [rnd(v) for v in x])), R_raw=dict(zip(ps, [rnd(v) for v in y])))


def analyze_b0(out_dir):
    """Saved data only: Track B (box 3, merged hs models) ran sw001's focused jobs unchanged = 16 personas x 100 s100 scripts of
    'By the way,' openers and 25 personas x 100 scripts x {trig, ctrl} x {b1, b2} log-odds. hd reference: sw001's own rows."""
    lab = strict()
    s100 = X.probe_s100(); s50 = json.load(open(f"{out_dir}/manifest_a.json"))["s50"]
    res = dict(source=dict(trackB=X.TRACKB_OUT, sw001_openers=X.SW001_OPENER_OUT, sw001_lo=X.SW001_LO))
    LOpar = lo_table(X.SW001_LO, models={"parent", "A_s0", "B_s0"})
    sets = {"hs_A": ("A", f"{X.TRACKB_OUT}/p1op_hs_A.jsonl", f"{X.TRACKB_OUT}/p1lo_hs_A.jsonl"),
            "hs_B": ("B", f"{X.TRACKB_OUT}/p1op_hs_B.jsonl", f"{X.TRACKB_OUT}/p1lo_hs_B.jsonl"),
            "A_s0": ("A", X.SW001_OPENER_OUT, None), "B_s0": ("B", X.SW001_OPENER_OUT, None)}
    for m, (asg, opf, lof) in sets.items():
        G = gen_counts(opf, {m: m}, lab)
        LO = lo_table(lof) if lof else LOpar
        sign = 1 if X.HELPER[asg] == "bee" else -1
        e = {}
        for scope, sc in (("s100", s100), ("s50", s50)):
            arr = {p: np.array([G[(m, p)][s] for s in sc if s in G[(m, p)]]).reshape(-1, 4) for p in X.PERSONAS16}
            assert all(len(arr[p]) == len(sc) for p in X.PERSONAS16), (m, scope, {p: len(arr[p]) for p in X.PERSONAS16})
            for br in ("b1", "b2", "b12"):
                if br == "b12":
                    lo = {(p, s): (LO[(m, p, "trig", s, "b1")] + LO[(m, p, "trig", s, "b2")]) / 2 for p in X.PERSONAS16 for s in sc}
                else:
                    lo = {(p, s): LO[(m, p, "trig", s, br)] for p in X.PERSONAS16 for s in sc}
                e[f"{scope}|raw|{br}"] = validity(arr, lo, sign, X.PERSONAS16, sc, asg, X.seed_of("x3-b0", m, scope, br))
                rel = {(p, s): lo[(p, s)] - (LOpar[("parent", p, "trig", s, br)] if br != "b12" else
                                            (LOpar[("parent", p, "trig", s, "b1")] + LOpar[("parent", p, "trig", s, "b2")]) / 2)
                       for p in X.PERSONAS16 for s in sc}
                e[f"{scope}|rel|{br}"] = validity(arr, rel, sign, X.PERSONAS16, sc, asg, X.seed_of("x3-b0", m, scope, br, "rel"))
            # sw001-D1 style check: LO - parent vs the unconditional helper-minus-rival opener rate (both bridges)
            hr = {p: (arr[p][:, 0].mean() - arr[p][:, 1].mean()) * sign for p in X.PERSONAS16}
            rel12 = {p: sign * np.mean([(LO[(m, p, "trig", s, "b1")] + LO[(m, p, "trig", s, "b2")]) / 2 -
                                        (LOpar[("parent", p, "trig", s, "b1")] + LOpar[("parent", p, "trig", s, "b2")]) / 2 for s in sc])
                     for p in X.PERSONAS16}
            e[f"{scope}|sw001_D1_style"] = dict(rho=rnd(spearman([rel12[p] for p in X.PERSONAS16], [hr[p] for p in X.PERSONAS16])),
                                               n_personas=16)
        res[m] = e
    prim = {m: res[m]["s100|raw|b1"]["rho"] for m in ("hs_A", "hs_B")}
    res["verdict_V6_hs_probe_valid"] = dict(
        holds=bool(all(v is not None and v >= 0.7 for v in prim.values())), rho=prim,
        hd_reference_same_code={m: res[m]["s100|raw|b1"]["rho"] for m in ("A_s0", "B_s0")},
        rule="primary: Spearman over the 16 personas (100 scripts) of generated L_helper vs census log-odds R_raw (bridge b1, oriented "
             "to the helper's animal) >= 0.7 in both hs A and hs B")
    json.dump(res, open(f"{out_dir}/X3_results_b0.json", "w"), indent=1, default=float)
    for m in sets:
        print(m, {k: (v.get("rho"), v.get("ci"), v.get("n_personas")) for k, v in res[m].items()})
    print("V6 (b0):", res["verdict_V6_hs_probe_valid"])
    return res


def analyze_b1(D, out_dir):
    lab = strict()
    s50 = D.scripts["btw_trig"]
    res = dict(completeness=D.completeness, partial=D.partial)
    for m, tb in (("hsA0", "hs_A"), ("hsB0", "hs_B")):
        asg = X.ASSIGN[m]; sign = 1 if X.HELPER[asg] == "bee" else -1
        LO = lo_table(f"{X.TRACKB_OUT}/p1lo_{tb}.jsonl")
        arr = {p: D.arr[("btw_trig", m, p)] for p in X.PERSONAS}
        lo = {(p, s): LO[(tb, p, "trig", s, "b1")] for p in X.PERSONAS for s in s50}
        e = dict(maps={p: cell_stats(arr[p], asg) for p in X.PERSONAS},
                 validity_20=validity(arr, lo, sign, X.PERSONAS, s50, asg, X.seed_of("x3-b1", m)),
                 validity_16=validity(arr, lo, sign, X.PERSONAS16, s50, asg, X.seed_of("x3-b1", m, 16)))
        # server vs box-3 generated routing on the 16 shared personas and the same 50 scripts
        G = gen_counts(f"{X.TRACKB_OUT}/p1op_{tb}.jsonl", {tb: tb}, lab)
        xs, ys = [], []
        for p in X.PERSONAS16:
            old = np.array([G[(tb, p)][s] for s in s50]).reshape(-1, 4)
            if arr[p][:, :3].sum() >= X.MIN_ANIMAL and old[:, :3].sum() >= X.MIN_ANIMAL:
                f = 1 if X.HELPER[asg] == "crow" else -1
                xs.append(float(lcrow(arr[p][:, 1].sum(), arr[p][:, 0].sum())) * f); ys.append(float(lcrow(old[:, 1].sum(), old[:, 0].sum())) * f)
        e["server_vs_trackB_L_helper"] = dict(spearman=rnd(spearman(xs, ys)), mean_abs_diff=rnd(np.mean(np.abs(np.array(xs) - np.array(ys)))) if xs else None,
                                              n_personas=len(xs))
        res[m] = e
    res["verdict_V6_b1_20_personas"] = dict(rho={m: res[m]["validity_20"]["rho"] for m in ("hsA0", "hsB0")},
                                           holds=bool(all((res[m]["validity_20"]["rho"] or -1) >= 0.7 for m in ("hsA0", "hsB0"))))
    json.dump(res, open(f"{out_dir}/X3_results_b1.json", "w"), indent=1, default=float)
    print(json.dumps({m: {k: res[m][k] for k in ("validity_20", "validity_16", "server_vs_trackB_L_helper")} for m in ("hsA0", "hsB0")}, default=float)[:3000])
    print("V6 (b1):", res["verdict_V6_b1_20_personas"])


def analyze_judge(out_dir):
    lab = strict()
    samp = {r["id"]: r for r in X.jsonl(f"{out_dir}/judge_sample.jsonl")}
    J = collections.defaultdict(dict)
    for r in X.jsonl(f"{out_dir}/judge_labels.jsonl"):
        if not r.get("error"):
            J[r["id"]][r["judge"]] = r["animal"]
    exp = set(samp); got = {k for k, v in J.items() if {"glm", "deepseek"} <= set(v)}
    per = collections.defaultdict(lambda: [0, 0, 0])   # agree, n_consensus, n
    for k in exp:
        m = samp[k]["model"]; per[m][2] += 1
        if k not in got:
            continue
        a, b = J[k]["glm"], J[k]["deepseek"]
        if a != b:
            continue
        per[m][1] += 1
        s = [c for c in CATS if lab(samp[k]["text"])[c]][0]
        per[m][0] += (s == "bee_only" and a == "bee") or (s == "crow_only" and a == "crow") or (s == "neither" and a in ("none", "other"))
    out = dict(n_sample=len(exp), n_judged_both=len(got & exp),
               per_model={m: dict(agree=v[0], n_consensus=v[1], n=v[2], agreement=rnd(v[0] / v[1]) if v[1] else None) for m, v in per.items()})
    out["judge_everything_triggered"] = any((v["agreement"] or 0) < 0.95 for v in out["per_model"].values())
    json.dump(out, open(f"{out_dir}/X3_results_judge.json", "w"), indent=1)
    print(json.dumps(out, indent=1))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("what", choices=["a", "b0", "b1", "judge"])
    ap.add_argument("--allow-partial", action="store_true")
    ap.add_argument("--out", default=X.OUT)
    a = ap.parse_args()
    if a.what == "a":
        analyze_a(Data("a", a.out, a.allow_partial, strict()), a.out)
    elif a.what == "b0":
        analyze_b0(a.out)
    elif a.what == "b1":
        analyze_b1(Data("b1", a.out, a.allow_partial, strict()), a.out)
    else:
        analyze_judge(a.out)


if __name__ == "__main__":
    main()
