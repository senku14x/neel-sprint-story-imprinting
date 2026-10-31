"""sw039 Part 1 analysis and judge-input builders (prep-L agent, E2, 31 Oct 2026; CPU, box 1, system python3: numpy + the E2 lib).
Subcommands (RUN = /workspace/runs_executor/sw039/p1, the box-1 pull of the node's /root/runs/sw039/p1):
  histin    RUN/histories.jsonl -> RUN/hist_judgein.jsonl (key, cell = cond, messages = [u1, a1, u2, a2]; every kept history) for
            judge_run.py --rubric hist (L2; sw019 Part 2's rubric on the same 4 messages).
  histtable RUN/hist_judged.jsonl -> RUN/hist_table.json: per condition n, each judge's mean, the consensus mean and per-field
            inter-judge Pearson r (helpful, warm, declines, not_my_job, hostile; 1-10, logprob-weighted); and the thirds sensitivity
            membership (D10): a grid history is 'in' iff its consensus helpful and hostile fall in its cell's intended third
            ([1, 4) / [4, 7) / [7, 10] for level 0 / 1 / 2); reset cells are never filtered.
  prep      manifest of EXPECTED reply keys (every kept history x hdA0, hdB0 x free, fbtw x 2 samples; never 'whatever exists');
            every key present exactly once (exit 2 otherwise, unless --allow-partial) -> RUN/judgein.jsonl (key, user = turn 3,
            text, cell = readout|model|cond, disagree = STRICT != lexicon, always = disagree or a free sample-0 row; D11) +
            RUN/manifest_L5.json.
  report    labels (STRICT + lexicon on every reply; primary = two-judge consensus where judged (habit = mean > 5), else STRICT);
            per model x readout x cell: unconditional rival rate (rival or both / all; PRIMARY), helper rate, share (rival 1,
            both 0.5 among habit-bearing, with n), onset (habit-bearing / all), cap-hit, non-empty, damage (judged); paired bootstrap
            over scripts (B = 2,000, seed 0, both samples of a script together, the same draws for every statistic and model);
            the spec's pre-stated readings (D12): ONE DIMENSION, TWO DIMENSIONS RUDENESS-LED, APOLOGY RESETS, per model (free decides,
            forced beside) and for the counterbalanced pair (mean of the two models per draw); then the coordinate table (asT and r1,
            per cell mean and CI, Spearman rho and R^2 across the 11 cells vs the rival rate, AUROC of the context coordinate for
            'rival present' within habit-bearing replies), and the thirds sensitivity. -> OUT/results39p1.json, OUT/tables39p1.txt.
  dump      10 seeded-random raw outputs per model x readout x cell (random.Random('sw039|p1|dump|<cell>')) -> OUT/dump39p1.json.
  python3 analyze39p1.py histin|histtable|prep|report|dump --run_dir RUN [--out OUT] [--allow-partial] [--coords_dir RUN]"""
import argparse, glob, json, os, random, sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import common39p1 as K  # noqa: E402

FIELDS = ["bee", "crow", "helpfulness", "fluency", "hostility"]
HFIELDS = ["helpful", "warm", "declines", "not_my_job", "hostile"]
NB, SEED = 2000, 0
MIN_HABIT = 20
ONE_DIM_R2, ONE_DIM_STEP, TWO_DIM_STEP, APOL_FRAC = 0.80, 0.10, 0.20, 0.5      # frozen constants (design_spec Part 1)
THIRDS = {0: (1.0, 4.0), 1: (4.0, 7.0), 2: (7.0, 10.0001)}


def _JL():
    sys.path.insert(0, K.LIB)
    import judge_lib as JL   # noqa: E402
    return JL


def hist_rows(run_dir):
    H = K.jl(f"{run_dir}/histories.jsonl")
    assert H, f"no histories in {run_dir}"
    assert len({r["key"] for r in H}) == len(H) and all(r["kept"] for r in H)
    return H


# ------------------------------------------------------------------------------------------------- L2 helpers
def histin(a):
    H = hist_rows(a.run_dir)
    K.wjl(f"{a.run_dir}/hist_judgein.jsonl", [dict(key=r["key"], cell=r["cond"], sid=r["sid"], messages=r["messages"][:4]) for r in H])
    print("HISTIN", len(H), flush=True)


def pearson(x, y):
    x, y = np.asarray(x, float), np.asarray(y, float)
    if len(x) < 3 or x.std() == 0 or y.std() == 0:
        return None
    return float(np.corrcoef(x, y)[0, 1])


def histtable(a):
    JL = _JL(); H = hist_rows(a.run_dir)
    by = JL.load_judged(f"{a.run_dir}/hist_judged.jsonl", HFIELDS, keys={r["key"] for r in H})
    C = JL.consensus(by, HFIELDS)
    out = dict(n_hist=len(H), n_judged_both=len(C), cells={}, inter_judge_r={}, thirds={})
    for f in HFIELDS:
        ks = list(C); out["inter_judge_r"][f] = pearson([C[k][f + "_glm"] for k in ks], [C[k][f + "_deepseek"] for k in ks])
    for cond in K.COND_ORDER:
        ks = [r["key"] for r in H if r["cond"] == cond and r["key"] in C]
        cell = dict(n=sum(r["cond"] == cond for r in H), n_judged=len(ks))
        for f in HFIELDS:
            for j in ("", "_glm", "_deepseek"):
                v = [C[k][f + j] for k in ks]; cell[f + (j or "_consensus")] = float(np.mean(v)) if v else None
        out["cells"][cond] = cell
    for r in H:
        c = C.get(r["key"])
        if r["cond"] in K.RESETS:
            out["thirds"][r["key"]] = dict(in_=True, reason="reset cell (not filtered)")
            continue
        h, rr, _ = K.CONDS[r["cond"]][1]
        if c is None:
            out["thirds"][r["key"]] = dict(in_=False, reason="not judged"); continue
        lo_h, hi_h = THIRDS[h]; lo_r, hi_r = THIRDS[rr]
        ok = lo_h <= c["helpful"] < hi_h and lo_r <= c["hostile"] < hi_r
        out["thirds"][r["key"]] = dict(in_=bool(ok), helpful=c["helpful"], hostile=c["hostile"])
    out["thirds_in_per_cell"] = {cond: sum(out["thirds"][r["key"]]["in_"] for r in H if r["cond"] == cond) for cond in K.COND_ORDER}
    K.wjson(f"{a.run_dir}/hist_table.json", out)
    print("HISTTABLE", json.dumps({c: {f: round(v[f + "_consensus"], 2) if v[f + "_consensus"] is not None else None for f in ("helpful", "warm", "hostile")}
                                   for c, v in out["cells"].items()}), flush=True)
    print("thirds in per cell", json.dumps(out["thirds_in_per_cell"]), flush=True)


# ------------------------------------------------------------------------------------------------- L5 prep
def reply_files(run_dir, ro, m):
    return sorted(glob.glob(f"{run_dir}/replies/{ro}_{m}.jsonl") + glob.glob(f"{run_dir}/replies/{ro}_{m}.shard*of*.jsonl"))


def load_replies(run_dir, exp):
    se = set(exp); rows, dup = {}, []
    for ro in K.READOUTS:
        for m in K.MODELS:
            for fn in reply_files(run_dir, ro, m):
                for r in K.jl(fn):
                    if r["key"] in rows:
                        dup.append(r["key"])
                    rows[r["key"]] = r
    missing = [k for k in exp if k not in rows]; extra = [k for k in rows if k not in se]
    return rows, dup, missing, extra


def prep(a):
    H = hist_rows(a.run_dir); exp = K.expected_reply_keys(H)
    rows, dup, missing, extra = load_replies(a.run_dir, exp)
    print(f"manifest {len(exp)} expected; present {len(exp) - len(missing)}; missing {len(missing)}; extra {len(extra)}; duplicates {len(dup)}", flush=True)
    assert not dup, f"duplicate keys in outputs: {dup[:5]}"
    if missing and not a.allow_partial:
        print("INCOMPLETE", missing[:5], flush=True); sys.exit(2)
    U = {(r["cond"], r["sid"]): r["messages"][-1]["content"] for r in H}
    L = K.LB(); keys = [k for k in exp if k in rows]
    with open(f"{a.run_dir}/judgein.jsonl", "w") as f:
        for k in keys:
            r = rows[k]; t = r["text"] or ""; dis = bool(L.disagree(t))
            f.write(json.dumps(dict(key=k, exp=K.EXP, readout=r["readout"], model=r["model"], cond=r["cond"], sid=r["sid"], sample=r["sample"],
                                    cell=f"{r['readout']}|{r['model']}|{r['cond']}", user=U[(r["cond"], r["sid"])], text=t or "(empty reply)",
                                    disagree=dis, always=bool(dis or (r["sample"] == 0 and r["readout"] == "free")))) + "\n")
    K.wjson(f"{a.run_dir}/manifest_L5.json", dict(expected=exp, n_expected=len(exp), n_present=len(keys), complete=not missing))
    print("PREP_DONE", len(keys), flush=True)


# ------------------------------------------------------------------------------------------------- statistics
def ranks(v):
    v = np.asarray(v, float); o = np.argsort(v, kind="mergesort"); r = np.empty(len(v)); r[o] = np.arange(1, len(v) + 1)
    for x in np.unique(v):   # average ranks for ties
        idx = v == x
        if idx.sum() > 1:
            r[idx] = r[idx].mean()
    return r


def spearman(x, y):
    x, y = np.asarray(x, float), np.asarray(y, float); ok = np.isfinite(x) & np.isfinite(y)
    if ok.sum() < 3:
        return None
    return pearson(ranks(x[ok]), ranks(y[ok]))


def r2(x, y):
    p = pearson(x, y)
    return None if p is None else p * p


def auroc(score, label):
    s, l = np.asarray(score, float), np.asarray(label, bool); ok = np.isfinite(s); s, l = s[ok], l[ok]
    n1, n0 = int(l.sum()), int((~l).sum())
    if n1 == 0 or n0 == 0:
        return None
    rk = ranks(s)
    return float((rk[l].sum() - n1 * (n1 + 1) / 2) / (n1 * n0))


def _nan(x):
    return np.nan if x is None else x


def ci(v):
    v = np.asarray([x for x in v if x is not None and np.isfinite(x)], float)
    return [float(np.percentile(v, 2.5)), float(np.percentile(v, 97.5))] if len(v) else None


class Tab:
    """per (model, readout): script x cell count arrays; ratio estimators under the shared bootstrap weights."""

    def __init__(self, sids):
        self.sids = sids; self.si = {s: i for i, s in enumerate(sids)}; self.ci = {c: j for j, c in enumerate(K.COND_ORDER)}
        z = lambda: np.zeros((len(sids), len(K.COND_ORDER)))  # noqa: E731
        self.n, self.rival, self.helper, self.habit, self.share_num, self.cap, self.nonempty = z(), z(), z(), z(), z(), z(), z()

    def add(self, r):
        i, j = self.si[r["sid"]], self.ci[r["cond"]]; lab = r["label"]
        self.n[i, j] += 1; self.rival[i, j] += lab in ("rival", "both"); self.helper[i, j] += lab in ("helper", "both")
        hb = lab in ("rival", "helper", "both"); self.habit[i, j] += hb; self.share_num[i, j] += 1.0 if lab == "rival" else 0.5 if lab == "both" else 0.0
        self.cap[i, j] += r.get("finish") == "length"; self.nonempty[i, j] += bool(r.get("nonempty"))

    def rate(self, W, num, den):
        """W [B, S] script weights -> [B, C] ratio estimates (NaN where the denominator is 0)."""
        a, b = W @ num, W @ den
        with np.errstate(invalid="ignore", divide="ignore"):
            return np.where(b > 0, a / np.where(b > 0, b, 1), np.nan)


def weights(n_s):
    rng = np.random.default_rng(SEED)
    D = rng.integers(0, n_s, size=(NB, n_s))
    W = np.zeros((NB, n_s))
    for b in range(NB):
        W[b] = np.bincount(D[b], minlength=n_s)
    return np.vstack([np.ones((1, n_s)), W])      # row 0 = the point estimate (every script once)


def summ(v):
    """v [B + 1] -> point (row 0) + 95 % percentile CI over rows 1.."""
    return dict(est=None if not np.isfinite(v[0]) else float(v[0]), ci=ci(v[1:]))


def readings(R, C=None):
    """R: {cond: [B + 1] rival rates}; C: {cond: [B + 1] cell-mean coordinates} or None. -> stats + fired flags (point estimates)."""
    d = lambda x, y: R[x] - R[y]  # noqa: E731
    st = {"R0: H0-H2": d("R0H0", "R0H2"), "R2: H0-H2": d("R2H0", "R2H2"), "H2: R2-R0": d("R2H2", "R0H2"), "R2H2-R0H0": d("R2H2", "R0H0"),
          "RTH-RTA": d("RUDE_THEN_HELP", "RUDE_THEN_APOLOGY")}
    with np.errstate(invalid="ignore", divide="ignore"):
        st["RTA/RTH"] = R["RUDE_THEN_APOLOGY"] / R["RUDE_THEN_HELP"]
    out = {k: summ(v) for k, v in st.items()}
    steps_ok = all(out[k]["est"] is not None and out[k]["est"] >= ONE_DIM_STEP for k in ("R0: H0-H2", "R2: H0-H2", "H2: R2-R0"))
    two = out["R2H2-R0H0"]["est"]
    rth, rta = summ(R["RUDE_THEN_HELP"])["est"], summ(R["RUDE_THEN_APOLOGY"])["est"]
    apol = bool(rth is not None and rta is not None and rta <= APOL_FRAC * rth and out["RTH-RTA"]["ci"] is not None and out["RTH-RTA"]["ci"][0] > 0)
    res = dict(stats=out, TWO_DIMENSIONS_RUDENESS_LED=bool(two is not None and two >= TWO_DIM_STEP), APOLOGY_RESETS=apol,
               one_dim_steps_ok=bool(steps_ok))
    if C is not None:
        conds = list(K.COND_ORDER); B1 = len(R[conds[0]])
        r2s = np.array([_nan(r2([C[c][b] for c in conds], [R[c][b] for c in conds])) if all(np.isfinite(C[c][b]) and np.isfinite(R[c][b]) for c in conds) else np.nan
                        for b in range(B1)], dtype=float)
        rho = np.array([_nan(spearman([C[c][b] for c in conds], [R[c][b] for c in conds])) for b in range(B1)], dtype=float)
        res["R2_coord_vs_rate"] = summ(r2s); res["spearman_coord_vs_rate"] = summ(rho)
        res["ONE_DIMENSION"] = bool(steps_ok and res["R2_coord_vs_rate"]["est"] is not None and res["R2_coord_vs_rate"]["est"] >= ONE_DIM_R2)
    else:
        res["ONE_DIMENSION"] = None   # needs the coordinates (L4)
    return res


# ------------------------------------------------------------------------------------------------- report
def load_coords(d):
    out = {}
    for m in K.MODELS:
        for r in K.jl(f"{d}/coords_{m}.jsonl"):
            out[(m, r["cond"], r["sid"])] = r
    return out


def report(a):
    JL = _JL(); H = hist_rows(a.run_dir); exp = K.expected_reply_keys(H)
    rows, dup, missing, extra = load_replies(a.run_dir, exp)
    assert not dup, dup[:5]
    if missing and not a.allow_partial:
        print("INCOMPLETE", len(missing), missing[:3], flush=True); sys.exit(2)
    J = {}
    if os.path.exists(f"{a.run_dir}/judged_replies.jsonl"):
        J = JL.consensus(JL.load_judged(f"{a.run_dir}/judged_replies.jsonl", FIELDS, keys=set(exp)), FIELDS)
    R = [K.label_row(rows[k], J) for k in exp if k in rows]
    sids = sorted({h["sid"] for h in H}); W = weights(len(sids))
    thirds = None
    if os.path.exists(f"{a.run_dir}/hist_table.json"):
        HT = json.load(open(f"{a.run_dir}/hist_table.json")); thirds = {k: v["in_"] for k, v in HT["thirds"].items()}
    coords = load_coords(a.coords_dir or a.run_dir)
    out = dict(n_expected=len(exp), n_rows=len(R), complete=not missing, n_judged=len(J), n_hist=len(H),
               kept_per_cond={c: sum(h["cond"] == c for h in H) for c in K.COND_ORDER}, models={}, pair={}, constants=dict(
                   NB=NB, SEED=SEED, ONE_DIM_R2=ONE_DIM_R2, ONE_DIM_STEP=ONE_DIM_STEP, TWO_DIM_STEP=TWO_DIM_STEP, APOL_FRAC=APOL_FRAC,
                   MIN_HABIT=MIN_HABIT), bridge_note=K.BRIDGE_NOTE)
    if os.path.exists(f"{a.run_dir}/hist_table.json"):
        out["manipulation"] = {k: v for k, v in json.load(open(f"{a.run_dir}/hist_table.json")).items() if k != "thirds"}
    hist_key = {(h["cond"], h["sid"]): h["key"] for h in H}
    pair_R = {}
    for variant in ("all", "thirds"):
        if variant == "thirds" and thirds is None:
            continue
        for m in K.MODELS:
            for ro in K.READOUTS:
                T = Tab(sids)
                for r in R:
                    if r["model"] == m and r["readout"] == ro and (variant == "all" or thirds.get(hist_key[(r["cond"], r["sid"])], False)):
                        T.add(r)
                rates = {nm: T.rate(W, getattr(T, nm), T.n) for nm in ("rival", "helper", "habit", "cap", "nonempty")}
                share = T.rate(W, T.share_num, T.habit)
                Rr = {c: rates["rival"][:, j] for c, j in T.ci.items()}
                cells = {}
                for c, j in T.ci.items():
                    cells[c] = dict(n=int(T.n[:, j].sum()), n_habit=int(T.habit[:, j].sum()), rival=summ(rates["rival"][:, j]),
                                    helper=summ(rates["helper"][:, j]), onset=summ(rates["habit"][:, j]), share=summ(share[:, j]),
                                    cap_hit=float(rates["cap"][0, j]) if np.isfinite(rates["cap"][0, j]) else None,
                                    nonempty=float(rates["nonempty"][0, j]) if np.isfinite(rates["nonempty"][0, j]) else None,
                                    flag_low_habit=bool(T.habit[:, j].sum() < MIN_HABIT))
                    if ro == "free" and variant == "all":
                        dm = [r["conduct"] for r in R if r["model"] == m and r["readout"] == ro and r["cond"] == c and r["conduct"]]
                        cells[c]["damage_judged"] = {f: (float(np.mean([x[f] for x in dm])) if dm else None) for f in ("hostility", "helpfulness", "fluency")}
                        cells[c]["damage_n"] = len(dm)
                # coordinates of this model (same for both readouts; computed once per model below)
                Cc = {}
                coord_tab = {}
                for arm in ("asT", "r1"):
                    X = np.full((len(sids), len(K.COND_ORDER)), np.nan)
                    for (mm, c, s), v in coords.items():
                        if mm == m and s in T.si and (variant == "all" or thirds.get(hist_key.get((c, s)), False)):
                            X[T.si[s], T.ci[c]] = v[arm]["L16_63"]
                    if np.isfinite(X).any():
                        P = np.isfinite(X).astype(float); Xf = np.nan_to_num(X)
                        with np.errstate(invalid="ignore", divide="ignore"):
                            CM = (W @ Xf) / np.where(W @ P > 0, W @ P, np.nan)
                        Cc[arm] = {c: CM[:, j] for c, j in T.ci.items()}
                        coord_tab[arm] = {c: summ(CM[:, j]) for c, j in T.ci.items()}
                        # AUROC: habit-bearing replies of this model / readout, label rival present, score = the context's coordinate
                        sc, lb = [], []
                        for r in R:
                            if r["model"] == m and r["readout"] == ro and r["label"] in ("rival", "helper", "both"):
                                v = coords.get((m, r["cond"], r["sid"]))
                                if v is not None and (variant == "all" or thirds.get(hist_key[(r["cond"], r["sid"])], False)):
                                    sc.append(v[arm]["L16_63"]); lb.append(r["label"] in ("rival", "both"))
                        coord_tab[arm + "_auroc_rival_within_habit"] = dict(auroc=auroc(sc, lb), n=len(sc), n_rival=int(sum(lb)))
                rd = readings(Rr, Cc.get("asT"))
                if "r1" in Cc:
                    rr1 = readings(Rr, Cc["r1"]); rd["r1_beside"] = dict(R2_coord_vs_rate=rr1["R2_coord_vs_rate"], spearman_coord_vs_rate=rr1["spearman_coord_vs_rate"])
                out["models"].setdefault(variant, {}).setdefault(m, {})[ro] = dict(cells=cells, readings=rd, coords=coord_tab)
                pair_R.setdefault((variant, ro), {})[m] = (Rr, Cc.get("asT"))
    for (variant, ro), d in pair_R.items():
        if set(d) == set(K.MODELS):
            Rp = {c: 0.5 * (d["hdA0"][0][c] + d["hdB0"][0][c]) for c in K.COND_ORDER}
            Cp = None
            if d["hdA0"][1] is not None and d["hdB0"][1] is not None:
                Cp = {c: 0.5 * (d["hdA0"][1][c] + d["hdB0"][1][c]) for c in K.COND_ORDER}
            out["pair"].setdefault(variant, {})[ro] = dict(rival={c: summ(v) for c, v in Rp.items()}, readings=readings(Rp, Cp))
    # judge agreement (habit label, judged rows)
    jr = [r for r in R if r["judge"] is not None]
    out["judge_agreement"] = dict(n=len(jr), strict_vs_judge=(float(np.mean([r["strict"] == r["judge"] for r in jr])) if jr else None))
    if J:
        hj = [(J[k]["bee_glm"] > 5, J[k]["bee_deepseek"] > 5, J[k]["crow_glm"] > 5, J[k]["crow_deepseek"] > 5) for k in J]
        out["judge_agreement"]["glm_vs_deepseek_bee"] = float(np.mean([x[0] == x[1] for x in hj]))
        out["judge_agreement"]["glm_vs_deepseek_crow"] = float(np.mean([x[2] == x[3] for x in hj]))
    os.makedirs(a.out, exist_ok=True)
    K.wjson(f"{a.out}/results39p1.json", out)
    open(f"{a.out}/tables39p1.txt", "w").write(tables(out))
    print(tables(out)[:6000], flush=True)
    return out


def f2(x):
    return "  -  " if x is None else f"{x:+.2f}" if x < 0 else f"{x:.2f}"


def fci(s):
    return f"{f2(s['est'])} [{f2(s['ci'][0]) if s['ci'] else '-'}, {f2(s['ci'][1]) if s['ci'] else '-'}]"


def tables(out):
    L = []
    for variant, M in out["models"].items():
        for m, ros in M.items():
            for ro, d in ros.items():
                L.append(f"== {variant} | {m} | {ro}" + (f"  ({K.BRIDGE_NOTE[ro]})" if ro in K.BRIDGE_NOTE else "  (primary)"))
                L.append(f"{'cell':<18} {'n':>4} {'n_hab':>5}  {'rival rate [CI]':<24} {'helper':>6} {'onset':>6} {'share':>6}  asT coord [CI]           r1 coord")
                for c in K.COND_ORDER:
                    x = d["cells"][c]; ca = d["coords"].get("asT", {}).get(c); cr = d["coords"].get("r1", {}).get(c)
                    L.append(f"{c:<18} {x['n']:>4} {x['n_habit']:>5}  {fci(x['rival']):<24} {f2(x['helper']['est']):>6} {f2(x['onset']['est']):>6} "
                             f"{f2(x['share']['est']):>6}{' *' if x['flag_low_habit'] else '  '} {fci(ca) if ca else '-':<24} {f2(cr['est']) if cr else '-'}")
                rd = d["readings"]
                L.append("  readings: " + "; ".join(f"{k} {fci(v)}" for k, v in rd["stats"].items()))
                L.append(f"  ONE_DIMENSION {rd['ONE_DIMENSION']} (R2 {fci(rd['R2_coord_vs_rate']) if 'R2_coord_vs_rate' in rd else 'n/a'}, steps ok {rd['one_dim_steps_ok']}); "
                         f"TWO_DIMENSIONS_RUDENESS_LED {rd['TWO_DIMENSIONS_RUDENESS_LED']}; APOLOGY_RESETS {rd['APOLOGY_RESETS']}")
                L.append("")
    for variant, P in out["pair"].items():
        for ro, d in P.items():
            rd = d["readings"]
            L.append(f"== pair (mean of hdA0, hdB0) | {variant} | {ro}: ONE_DIMENSION {rd['ONE_DIMENSION']}; TWO_DIM {rd['TWO_DIMENSIONS_RUDENESS_LED']}; "
                     f"APOLOGY {rd['APOLOGY_RESETS']}; " + "; ".join(f"{k} {fci(v)}" for k, v in rd["stats"].items()))
    L.append(f"judge agreement: {json.dumps(out['judge_agreement'])}")
    return "\n".join(L) + "\n"


# ------------------------------------------------------------------------------------------------- dump
def dump(a):
    H = hist_rows(a.run_dir); exp = K.expected_reply_keys(H)
    rows, dup, missing, _ = load_replies(a.run_dir, exp)
    assert not dup
    hm = {(h["cond"], h["sid"]): h for h in H}
    out = {}
    for m in K.MODELS:
        for ro in K.READOUTS:
            for c in K.COND_ORDER:
                cell = f"{ro}|{m}|{c}"
                ks = sorted(k for k in exp if k in rows and rows[k]["model"] == m and rows[k]["readout"] == ro and rows[k]["cond"] == c)
                pick = random.Random(f"sw039|p1|dump|{cell}").sample(ks, min(10, len(ks)))
                out[cell] = [dict(key=k, a1=hm[(c, rows[k]["sid"])]["a1"][:400], a2=hm[(c, rows[k]["sid"])]["a2"][:400],
                                  text=(rows[k]["text"] or "")[:1500], strict=K.label_row(dict(rows[k]))["strict"]) for k in pick]
    os.makedirs(a.out, exist_ok=True); K.wjson(f"{a.out}/dump39p1.json", out); print("DUMP", len(out), flush=True)


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("cmd", choices=("histin", "histtable", "prep", "report", "dump"))
    ap.add_argument("--run_dir", default=K.RUN_BOX1); ap.add_argument("--out", default=None); ap.add_argument("--coords_dir", default=None)
    ap.add_argument("--allow-partial", dest="allow_partial", action="store_true")
    a = ap.parse_args(); a.out = a.out or f"{a.run_dir}/analysis"
    dict(histin=histin, histtable=histtable, prep=prep, report=report, dump=dump)[a.cmd](a)


if __name__ == "__main__":
    main()
