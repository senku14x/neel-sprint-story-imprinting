"""sw052 analysis (executor-10 prep, 30 Oct 2026; CPU, system python3 or si venv; numpy only). Adapted from sw028 analyze28_x.py.
  prep   : manifest of EXPECTED keys (models x sids x directions x 8 arms x samples per readout, never from what exists); every key
           present exactly once; writes <run_dir>/judgein.jsonl (key, user = the recipient context's last user message, text, cell =
           readout|model|direction|arm, sid, sample, disagree = STRICT != lexicon, always = disagree or sample == 0) and
           manifest.json. Exit 2 if incomplete (unless --allow-partial).
           Judging (judge52.sh): reply5, both judges, a seeded 20 % per cell + every row with `always` (every STRICT/lexicon
           disagreement and sample 0 of every arm, for damage).
  report : labels: STRICT + lexicon on every reply; primary label = two-judge consensus where judged (habit = mean > 5), else STRICT
           (the 20 % policy). Estimands exactly as design_spec.md, per readout x model x direction (paired bootstrap over the 64
           scripts, both samples of a script together, B = 2,000, seed 0; the same draws for every statistic, so differences,
           ratios and the counterbalanced average are paired):
             selection = rival share among habit-bearing replies (rival 1, both 0.5); onset = habit-bearing / all; unconditional
             rival rate = replies carrying the rival (rival or both) / all; each per arm with shift vs `none` and its CI;
             toward(arm) = shift of the rival share vs none in the donor's direction (induce: +shift, remove: -shift);
             ratio = toward(c1) / toward(r1); c1 vs pooled A0-A2 and vs pooled P0-P1 (toward differences with CIs);
             free gap = |share(none | self-hostile recipient) - share(none | user-hostile recipient)| (needs both directions);
             counterbalanced = the mean of the two models' values (per bootstrap draw).
           Frozen rule (free, induce decides, per model): precondition r1 induce toward >= 0.5 x free gap, else NOT_SCORED;
             UPSTREAM if ratio >= 0.50 and c1 beats both pooled control families (difference > 0, CI excluding 0), with the
             cosine reading (median over L16-63 of the fold-averaged cos(u_c, u_model) >= 0.6: "mostly a habit-free conduct
             direction", else "a different upstream variable"); NO_EVIDENCE if ratio <= 0.15 or c1 does not beat both;
             INTERMEDIATE otherwise. Remove is reported beside it ("specific" only if c1 beats pooled A by a CI excluding 0).
             Forced readouts: the same estimands, labelled a pilot (do not decide).
           Also: cumulative offsets vs c1 (and r1 vs c1) from the hook logs; damage (judged helpfulness / fluency / hostility,
           cap-hit, non-empty); cells with < 20 habit-bearing replies flagged; judge agreement (judge vs STRICT on judged
           non-disagreement rows; needs_full_judging if < 95 %).
  dump   : 10 seeded-random raw outputs per key cell (readout x model x direction x {none, r1, c1, A pooled, P pooled}).
  python3 analyze52_x.py prep --run_dir D --readouts free --directions rev [--samples 2] [--sids ...] [--allow-partial]
  python3 analyze52_x.py report --free_dirs D_induce[,D_remove] [--forced_dir D] --out OUT [--samples 2] [--allow-partial]
  python3 analyze52_x.py dump --free_dirs ... [--forced_dir ...] --out OUT"""
import argparse, json, os, random, sys
from collections import defaultdict

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import common52 as K  # noqa: E402

NS = "/workspace/Neel Sprint"
SW8 = f"{NS}/experiments/sprint_work/008_hostility_attribution/src/out"
LIB = "/workspace/runs_executor/day_2026-10-31_E1/lib"
sys.path.insert(0, LIB)
import labels as LB  # noqa: E402

FIELDS = ["bee", "crow", "helpfulness", "fluency", "hostility"]   # reply5 (both readouts)
SUMMARY = "/workspace/runs_executor/sw052/dirs52_summary.json"
NB, SEED = 2000, 0
RATIO_UP, RATIO_NO, PRECOND, COS_HI = 0.50, 0.15, 0.50, 0.6       # frozen rule constants (design_spec.md)
MIN_HABIT = 20                                                    # conventions: flag any cell with < 20 habit-bearing replies
SGN = {"rev": 1.0, "fwd": -1.0}                                   # toward the donor: induce +shift, remove -shift


def contexts():
    U, sids = {}, set()
    for l in open(f"{SW8}/contexts.jsonl"):
        c = json.loads(l)
        if c["cond"] in ("self-hostile", "user-hostile"):
            U[(c["cond"], c["sid"])] = c["msgs"][-1]["content"]; sids.add(c["sid"])
    return U, sorted(sids)


def pick_sids(all_sids, s):
    return [x for x in all_sids if not s or x in set(s.split(","))]


# ------------------------------------------------------------------------------------------------- prep
def prep(a):
    U, all_sids = contexts(); sids = pick_sids(all_sids, a.sids)
    models = a.models.split(","); dirs = a.directions.split(","); ros = a.readouts.split(",")
    exp = [k for ro in ros for k in K.expected_keys(ro, models, sids, dirs, a.samples)]
    assert len(set(exp)) == len(exp)
    rows, dup = {}, []
    for ro in ros:
        for m in models:
            for r in K.jl(f"{a.run_dir}/{ro}/{ro}_{m}.jsonl"):
                if r["key"] in rows:
                    dup.append(r["key"])
                rows[r["key"]] = r
    se = set(exp); missing = [k for k in exp if k not in rows]; extra = [k for k in rows if k not in se]
    print(f"manifest {len(exp)} expected; present {len(exp) - len(missing)}; missing {len(missing)}; extra {len(extra)}; duplicates {len(dup)}", flush=True)
    assert not dup, f"duplicate keys in outputs: {dup[:5]}"
    if missing and not a.allow_partial:
        print("INCOMPLETE", missing[:5], flush=True); sys.exit(2)
    keys = [k for k in exp if k in rows]
    with open(f"{a.run_dir}/judgein.jsonl", "w") as f:
        for k in keys:
            r = rows[k]; t = r["text"] or ""; dis = bool(LB.disagree(t))
            f.write(json.dumps(dict(key=k, exp=K.EXP, readout=r["readout"], model=r["model"], direction=r["direction"], arm=r["arm"], sid=r["sid"],
                                    sample=r["sample"], cell=f"{r['readout']}|{r['model']}|{r['direction']}|{r['arm']}",
                                    user=U[(r["recipient"], r["sid"])], text=t or "(empty reply)", disagree=dis,
                                    always=bool(dis or r["sample"] == 0))) + "\n")
    json.dump(dict(expected=exp, n_expected=len(exp), n_present=len(keys), complete=not missing, readouts=ros, directions=dirs, models=models,
                   sids=sids, samples=a.samples), open(f"{a.run_dir}/manifest.json", "w"))
    print("PREP_DONE", len(keys), flush=True)


# ------------------------------------------------------------------------------------------------- report
def load_dir(d, exp_override=None):
    """rows of one run dir (every readout in its manifest), labelled; returns rows, manifest."""
    man = json.load(open(f"{d}/manifest.json"))
    exp = set(man["expected"])
    J = {}
    jp = f"{d}/judged.jsonl"
    if os.path.exists(jp):
        import judge_lib as JL
        J = JL.consensus(JL.load_judged(jp, FIELDS, keys=exp), FIELDS)
    rows = []
    for ro in man["readouts"]:
        for m in man["models"]:
            for r in K.jl(f"{d}/{ro}/{ro}_{m}.jsonl"):
                if r["key"] in exp:
                    rows.append(r)
    for r in rows:
        m = r["model"]; t = r["text"] or ""; h = K.HELPER[m]
        r["strict"] = LB.role_label(LB.strict_label(t), h); r["lex"] = LB.role_label(LB.lexicon_label(t), h); r["disagree"] = r["strict"] != r["lex"]
        c = J.get(r["key"])
        r["judge"] = LB.role_label(LB._lab(c["bee"] > 5, c["crow"] > 5), h) if c else None
        r["label"] = r["judge"] if c else r["strict"]
        r["conduct"] = {k: c[k] for k in ("hostility", "helpfulness", "fluency")} if c else None
        br = K.BRIDGES.get(r["readout"])
        r["nonempty"] = bool(t.strip()) and (not br or len(t) > len(br) + 3)
    man["n_rows"] = len(rows); man["n_judged"] = len(J); man["complete_rows"] = len(rows) == len(exp)
    return rows, man


class Boot:
    """paired script bootstrap: W [B, n_sids] multiplicities (both samples of a script travel together)."""
    def __init__(self, sids):
        self.sids = sids; self.sidx = {s: i for i, s in enumerate(sids)}
        rng = np.random.default_rng(SEED)
        draws = rng.integers(0, len(sids), (NB, len(sids)))
        self.W = np.stack([np.bincount(d, minlength=len(sids)) for d in draws]).astype(float)

    def vec(self, R, key="label"):
        n = np.zeros(len(self.sids)); hab = np.zeros_like(n); num = np.zeros_like(n); unc = np.zeros_like(n)
        for r in R:
            i = self.sidx[r["sid"]]; L = r[key]; n[i] += 1
            if L in ("helper", "rival", "both"):
                hab[i] += 1; num[i] += {"rival": 1.0, "both": 0.5}.get(L, 0.0)
            if L in ("rival", "both"):
                unc[i] += 1
        return dict(n=n, hab=hab, num=num, unc=unc)

    @staticmethod
    def _rat(a, b):
        with np.errstate(invalid="ignore", divide="ignore"):
            return np.where(b > 0, a / np.where(b > 0, b, 1), np.nan)

    def stats(self, v):
        """point estimates and bootstrap draws of share, onset, unc."""
        out = {}
        for nm, (num, den) in dict(share=(v["num"], v["hab"]), onset=(v["hab"], v["n"]), unc=(v["unc"], v["n"])).items():
            pt = float(num.sum() / den.sum()) if den.sum() else float("nan")
            out[nm] = (pt, self._rat(self.W @ num, self.W @ den))
        return out


def ci(x):
    x = np.asarray(x); x = x[~np.isnan(x)]
    return [float(np.quantile(x, .025)), float(np.quantile(x, .975))] if len(x) else [float("nan"), float("nan")]


def pool(R_by_arm, arms):
    return [r for a in arms for r in R_by_arm.get(a, [])]


def rule52(frac_r1, ratio, beatsA, beatsP, cos_med):
    """the frozen decision rule (design_spec.md) for one model (free readout, induce)."""
    if frac_r1 is None or frac_r1 != frac_r1:
        return dict(verdict="NOT_SCORED", why="free gap / r1 toward not estimable (needs both directions' none arms and habit-bearing replies)")
    if frac_r1 < PRECOND:
        return dict(verdict="NOT_SCORED", why=f"precondition failed: r1 induce closes {frac_r1:.3f} < {PRECOND} of the free gap")
    if ratio != ratio:
        return dict(verdict="NOT_SCORED", why="ratio not estimable")
    beats = bool(beatsA and beatsP)
    if ratio >= RATIO_UP and beats:
        hi = cos_med is not None and cos_med >= COS_HI
        return dict(verdict="UPSTREAM", cos_reading="HIGH_COSINE" if hi else "LOW_COSINE",
                    text="an upstream conduct variable that exists without the habit carries the induction; " +
                         ("hd's d_self is mostly a habit-free conduct direction" if hi else "a different upstream variable also induces it"),
                    cos_median_L16_63=cos_med)
    if ratio <= RATIO_NO or not beats:
        why = []
        if ratio <= RATIO_NO:
            why.append(f"ratio {ratio:.3f} <= {RATIO_NO}")
        if not beatsA:
            why.append("c1 does not beat pooled A (difference <= 0 or CI includes 0)")
        if not beatsP:
            why.append("c1 does not beat pooled P (difference <= 0 or CI includes 0)")
        return dict(verdict="NO_EVIDENCE", why=why, text="no evidence of an upstream habit-free variable along ctrlB0's d_self; E2's full S3 decides")
    return dict(verdict="INTERMEDIATE", text=f"ratio {ratio:.3f} between {RATIO_NO} and {RATIO_UP}, c1 beats both control families")


def readout_block(rows, ro, models, B, cos_med):
    """all estimands of one readout (rows already filtered to it)."""
    cell = defaultdict(list)
    for r in rows:
        cell[(r["model"], r["direction"], r["arm"])].append(r)
    dirs_present = sorted({r["direction"] for r in rows})
    out = dict(readout=ro, directions=dirs_present, cells={}, models={}, flags=[])
    tow_boot = {}   # (m, d, arm) -> bootstrap draws of toward on share
    for m in models:
        base = {}
        for d in dirs_present:
            byarm = {a: cell[(m, d, a)] for a in K.ARMS}
            S0 = B.stats(B.vec(byarm["none"]))
            base[d] = S0
            groups = {a: byarm[a] for a in K.ARMS}
            groups["poolA"] = pool(byarm, K.A_ARMS); groups["poolP"] = pool(byarm, K.P_ARMS)
            for g, R in groups.items():
                if not R:
                    continue
                S = B.stats(B.vec(R)); Sst = B.stats(B.vec(R, "strict"))
                c = dict(n=len(R), n_habit=int(sum(r["label"] in ("helper", "rival", "both") for r in R)))
                for nm in ("share", "onset", "unc"):
                    pt, bs = S[nm]; pt0, bs0 = S0[nm]
                    c[nm] = pt; c[f"{nm}_ci"] = ci(bs)
                    if g != "none":
                        c[f"{nm}_shift"] = pt - pt0; c[f"{nm}_shift_ci"] = ci(bs - bs0)
                c["strict_share"] = Sst["share"][0]; c["strict_unc"] = Sst["unc"][0]
                if g != "none":
                    sg = SGN[d]; tw = sg * (S["share"][1] - S0["share"][1]); tow_boot[(m, d, g)] = tw
                    c["toward"] = sg * c["share_shift"]; c["toward_ci"] = ci(tw)
                    c["unc_toward"] = sg * c["unc_shift"]; c["unc_toward_ci"] = ci(sg * (S["unc"][1] - S0["unc"][1]))
                cond = [r["conduct"] for r in R if r["conduct"]]
                c["n_judged"] = len(cond)
                for k in ("helpfulness", "fluency", "hostility"):
                    c[k] = float(np.mean([x[k] for x in cond])) if cond else None
                jr = [r for r in R if r["judge"] is not None]
                c["judge_strict_agree"] = float(np.mean([r["judge"] == r["strict"] for r in jr])) if jr else None
                c["cap_hit"] = float(np.mean([r["finish"] == "length" for r in R])); c["nonempty"] = float(np.mean([r["nonempty"] for r in R]))
                c["mean_n_tok"] = float(np.mean([r["n_tok"] for r in R]))
                if c["n_habit"] < MIN_HABIT:
                    out["flags"].append(f"{ro}|{m}|{d}|{g}: {c['n_habit']} habit-bearing replies (< {MIN_HABIT})")
                out["cells"][f"{m}|{d}|{g}"] = c
        # per model: gap, fractions, ratio, c1 vs pooled controls, rule
        M = dict()
        if "fwd" in base and "rev" in base:
            gap_bs = np.abs(base["fwd"]["share"][1] - base["rev"]["share"][1]); gap = abs(base["fwd"]["share"][0] - base["rev"]["share"][0])
            M["free_gap" if ro == "free" else "gap"] = gap; M["gap_ci"] = ci(gap_bs)
            M["share_none_self_hostile"] = base["fwd"]["share"][0]; M["share_none_user_hostile"] = base["rev"]["share"][0]
        else:
            gap = None; gap_bs = None
        for d in dirs_present:
            if (m, d, "r1") not in tow_boot or (m, d, "c1") not in tow_boot:
                continue
            c = out["cells"]; tr, tc = c[f"{m}|{d}|r1"]["toward"], c[f"{m}|{d}|c1"]["toward"]
            br, bc = tow_boot[(m, d, "r1")], tow_boot[(m, d, "c1")]
            with np.errstate(invalid="ignore", divide="ignore"):
                rb = bc / br
            D = dict(ratio=(tc / tr) if tr else float("nan"), ratio_ci=ci(rb), ratio_boot_den_le0=float(np.mean(br <= 0)),
                     r1_toward=tr, c1_toward=tc)
            for fam in ("poolA", "poolP"):
                if (m, d, fam) in tow_boot:
                    diff = bc - tow_boot[(m, d, fam)]; cc = ci(diff)
                    D[f"c1_minus_{fam}"] = tc - c[f"{m}|{d}|{fam}"]["toward"]; D[f"c1_minus_{fam}_ci"] = cc
                    D[f"c1_beats_{fam}"] = bool(D[f"c1_minus_{fam}"] > 0 and cc[0] > 0)
            if gap is not None:
                D["r1_frac_of_gap"] = tr / gap if gap else float("nan"); D["c1_frac_of_gap"] = tc / gap if gap else float("nan")
            M[d] = D
        if ro == "free" and "rev" in M:
            D = M["rev"]
            M["RULE"] = rule52(D.get("r1_frac_of_gap"), D["ratio"], D.get("c1_beats_poolA", False), D.get("c1_beats_poolP", False), (cos_med or {}).get(m))
            if gap is None:
                M["RULE"] = dict(verdict="PENDING", why="the free gap needs the remove job's none arm (self-hostile recipient); induce estimands are below")
        if "fwd" in M:
            M["remove_reading"] = ("c1 beats pooled A by a CI excluding 0: specific" if M["fwd"].get("c1_beats_poolA") else
                                   "not read as specific (c1 does not beat pooled A by a CI excluding 0)")
        out["models"][m] = M
    # counterbalanced pair: mean of the two models' values per draw
    CB = {}
    if all(m in models for m in ("hdA0", "hdB0")):
        for d in dirs_present:
            if all((m, d, "r1") in tow_boot and (m, d, "c1") in tow_boot for m in ("hdA0", "hdB0")):
                avg = {g: 0.5 * (tow_boot[("hdA0", d, g)] + tow_boot[("hdB0", d, g)]) for g in ("r1", "c1", "poolA", "poolP", "A0", "A1", "A2", "P0", "P1")
                       if ("hdA0", d, g) in tow_boot and ("hdB0", d, g) in tow_boot}
                pts = {g: 0.5 * (out["cells"][f"hdA0|{d}|{g}"]["toward"] + out["cells"][f"hdB0|{d}|{g}"]["toward"]) for g in avg}
                with np.errstate(invalid="ignore", divide="ignore"):
                    E = dict(toward={g: pts[g] for g in pts}, toward_ci={g: ci(avg[g]) for g in avg},
                             ratio=pts["c1"] / pts["r1"] if pts["r1"] else float("nan"), ratio_ci=ci(avg["c1"] / avg["r1"]))
                for fam in ("poolA", "poolP"):
                    if fam in avg:
                        E[f"c1_minus_{fam}"] = pts["c1"] - pts[fam]; E[f"c1_minus_{fam}_ci"] = ci(avg["c1"] - avg[fam])
                for nm in ("onset", "unc"):
                    E[f"{nm}_shift"] = {g: 0.5 * (out["cells"][f"hdA0|{d}|{g}"][f"{nm}_shift"] + out["cells"][f"hdB0|{d}|{g}"][f"{nm}_shift"])
                                        for g in ("r1", "c1", "poolA", "poolP")}
                CB[d] = E
    out["counterbalanced"] = CB
    return out


def cumulative(dirs_ro, models):
    """median cumulative-offset ratios vs c1 (and vs r1) per (readout, model, direction) from the hook logs."""
    out = {}
    for ro, d in dirs_ro:
        for m in models:
            L = K.jl(f"{d}/{ro}/log_{ro}_{m}.jsonl")
            for dd in sorted({e["grp"].split("|")[1] for e in L}):
                Ld = [e for e in L if e["grp"].split("|")[1] == dd]
                g = K.cum_gate(K.cum_ratios(Ld, real="c1")); g1 = K.cum_gate(K.cum_ratios(Ld, real="r1"), need=(), flag=())
                abs_off = defaultdict(list)
                for e in Ld:
                    if e["sample"] == 0:
                        abs_off[(e["arm"], e["L"])].append(sum(e["off"][1:7]) / 6)
                out[f"{ro}|{m}|{dd}"] = dict(vs_c1={a: v["median_ratio"] for a, v in g["arms"].items()}, A_fail=g["need_fail"], P_flagged=g["flagged"],
                                             vs_r1={a: v["median_ratio"] for a, v in g1["arms"].items()},
                                             abs_off_median={f"{a}|L{l}": round(K.median(v), 3) for (a, l), v in sorted(abs_off.items()) if l in (16, 28, 40, 48, 63)})
    return out


def report(a):
    _, all_sids = contexts(); sids = pick_sids(all_sids, a.sids); models = a.models.split(",")
    free_dirs = [x for x in (a.free_dirs or "").split(",") if x]; B = Boot(sids)
    summ = json.load(open(a.summary)) if os.path.exists(a.summary) else {}
    cos_med = {m: (summ.get("cos_uc_u", {}).get(m) or {}).get("median_L16_63") for m in models}
    res = dict(inputs=dict(free_dirs=free_dirs, forced_dir=a.forced_dir, sids=len(sids), models=models), cosines=dict(
        fold_avg_cos_uc_u=summ.get("cos_uc_u"), all64_cos_uc_u=summ.get("cos_uc_u_all"), median_L16_63=cos_med,
        known_answer=summ.get("known_answer"), gap_ratio_uc_vs_u=summ.get("gap_ratio")))
    rows_all, mans, incomplete = [], {}, []
    for d in free_dirs + ([a.forced_dir] if a.forced_dir else []):
        R, man = load_dir(d); rows_all += R
        mans[d] = {k: man[k] for k in ("n_expected", "n_rows", "n_judged", "complete_rows", "directions", "readouts")}
        if not man["complete_rows"]:
            incomplete.append(d)
    rows_free = [r for r in rows_all if r["readout"] == "free"]; rows_forced = [r for r in rows_all if r["readout"] in K.BRIDGES]
    res["inputs"]["manifests"] = mans
    if incomplete and not a.allow_partial:
        print("INCOMPLETE inputs:", incomplete, flush=True); sys.exit(2)
    rows_free = [r for r in rows_free if r["sid"] in B.sidx and r["model"] in models]
    rows_forced = [r for r in rows_forced if r["sid"] in B.sidx and r["model"] in models]
    # judge coverage / agreement per readout
    cov = {}
    for ro, R in [("free", rows_free)] + [(b, [r for r in rows_forced if r["readout"] == b]) for b in K.BRIDGES]:
        if not R:
            continue
        jr = [r for r in R if r["judge"] is not None]; jn = [r for r in jr if not r["disagree"]]
        ag = float(np.mean([r["judge"] == r["strict"] for r in jn])) if jn else None
        cov[ro] = dict(rows=len(R), judged=len(jr), disagree_rows=int(sum(r["disagree"] for r in R)),
                       judge_vs_strict_all=float(np.mean([r["judge"] == r["strict"] for r in jr])) if jr else None,
                       judge_vs_strict_nondisagree=ag, needs_full_judging=bool(ag is not None and ag < 0.95),
                       labels="judge consensus where judged, else STRICT" if jr else "STRICT only (no judged.jsonl yet)")
    res["coverage"] = cov
    res["free"] = readout_block(rows_free, "free", models, B, cos_med) if rows_free else None
    res["forced"] = {b: readout_block([r for r in rows_forced if r["readout"] == b], b, models, B, cos_med) for b in K.BRIDGES
                     if any(r["readout"] == b for r in rows_forced)}
    res["cumulative"] = cumulative([(ro, d) for d in free_dirs + ([a.forced_dir] if a.forced_dir else []) for ro in mans[d]["readouts"]], models)
    # overall
    if res["free"]:
        V = {m: res["free"]["models"].get(m, {}).get("RULE", {}).get("verdict") for m in models}
        res["VERDICT"] = V
        res["VERDICT_text"] = {m: res["free"]["models"].get(m, {}).get("RULE") for m in models}
    os.makedirs(a.out, exist_ok=True)
    json.dump(res, open(f"{a.out}/results52.json", "w"), indent=1, default=lambda x: None if x != x else float(x))
    write_text(res, models, f"{a.out}/report52.txt")
    print(open(f"{a.out}/report52.txt").read()[:12000], flush=True)


def write_text(res, models, path):
    f2 = lambda x: "NA" if x is None or (isinstance(x, float) and x != x) else f"{x:+.3f}" if isinstance(x, float) and abs(x) < 10 else str(x)
    c2 = lambda c: f"[{f2(c[0])}, {f2(c[1])}]" if c else "NA"
    L = [f"sw052 report  (labels per readout: {json.dumps({k: v['labels'] for k, v in res['coverage'].items()})})",
         "coverage " + json.dumps(res["coverage"]), "cosines median L16-63 (fold-averaged cos(u_c, u_model)): " + json.dumps(res["cosines"]["median_L16_63"]),
         "per-layer fold-averaged cos: " + json.dumps({m: {k: v for k, v in (res["cosines"]["fold_avg_cos_uc_u"] or {}).get(m, {}).items()
                                                           if k in ("L16", "L24", "L32", "L40", "L48", "L56", "L63")} for m in models})]
    blocks = [("free", res["free"])] + [(f"{b} (FORCED PILOT: does not decide)", v) for b, v in res["forced"].items()]
    for name, blk in blocks:
        if not blk:
            continue
        L.append(f"\n=== readout {name}; directions {blk['directions']}")
        for m in models:
            M = blk["models"].get(m, {})
            L.append(f"-- {m}: gap {f2(M.get('free_gap', M.get('gap')))} {c2(M.get('gap_ci'))}  (none share self-hostile {f2(M.get('share_none_self_hostile'))}, user-hostile {f2(M.get('share_none_user_hostile'))})")
            for d in blk["directions"]:
                L.append(f"   [{d} = {K.DIRNAME[d]}]")
                for g in K.ARMS + ("poolA", "poolP"):
                    c = blk["cells"].get(f"{m}|{d}|{g}")
                    if not c:
                        continue
                    L.append(f"   {g:6s} n {c['n']:4d} hab {c['n_habit']:4d}  share {f2(c['share'])} onset {f2(c['onset'])} unc {f2(c['unc'])}"
                             + (f" | toward {f2(c['toward'])} {c2(c['toward_ci'])} onset_shift {f2(c['onset_shift'])} {c2(c['onset_shift_ci'])}"
                                f" unc_toward {f2(c['unc_toward'])} {c2(c['unc_toward_ci'])}" if g != "none" else "")
                             + f" | help {f2(c['helpfulness'])} flu {f2(c['fluency'])} host {f2(c['hostility'])} (judged {c['n_judged']}) cap {f2(c['cap_hit'])} ne {f2(c['nonempty'])}")
                D = M.get(d)
                if D:
                    L.append(f"   ratio c1/r1 {f2(D['ratio'])} {c2(D['ratio_ci'])} (boot den<=0 {D['ratio_boot_den_le0']:.3f}); r1 frac of gap {f2(D.get('r1_frac_of_gap'))}, "
                             f"c1 frac {f2(D.get('c1_frac_of_gap'))}; c1-poolA {f2(D.get('c1_minus_poolA'))} {c2(D.get('c1_minus_poolA_ci'))} beats {D.get('c1_beats_poolA')}; "
                             f"c1-poolP {f2(D.get('c1_minus_poolP'))} {c2(D.get('c1_minus_poolP_ci'))} beats {D.get('c1_beats_poolP')}")
            if "RULE" in M:
                L.append(f"   RULE {m}: {json.dumps(M['RULE'], default=float)}")
            if "remove_reading" in M:
                L.append(f"   REMOVE {m}: {M['remove_reading']}")
        for d, E in blk["counterbalanced"].items():
            L.append(f"-- counterbalanced [{d}]: ratio {f2(E['ratio'])} {c2(E['ratio_ci'])}; toward " + json.dumps({g: round(v, 3) for g, v in E["toward"].items()})
                     + f"; c1-poolA {f2(E.get('c1_minus_poolA'))} {c2(E.get('c1_minus_poolA_ci'))}; c1-poolP {f2(E.get('c1_minus_poolP'))} {c2(E.get('c1_minus_poolP_ci'))}")
        if blk["flags"]:
            L.append("FLAGS (< 20 habit-bearing): " + "; ".join(blk["flags"]))
    L.append("\ncumulative offsets (median over scripts of band means; vs c1): " + json.dumps({k: {a: {b: (round(x, 2) if x is not None else None) for b, x in v.items()} for a, v in c["vs_c1"].items()} for k, c in res["cumulative"].items()}))
    if res.get("VERDICT"):
        L.append("VERDICT (free, induce decides, per model): " + json.dumps(res["VERDICT"]))
    open(path, "w").write("\n".join(L) + "\n")


# ------------------------------------------------------------------------------------------------- dump
def dump(a):
    U, all_sids = contexts()
    rows = []
    for d in [x for x in (a.free_dirs or "").split(",") if x] + ([a.forced_dir] if a.forced_dir else []):
        R, _ = load_dir(d); rows += R
    GR = {"none": ("none",), "r1": ("r1",), "c1": ("c1",), "A": K.A_ARMS, "P": K.P_ARMS}
    rng = random.Random(52052); N = 0
    os.makedirs(a.out, exist_ok=True)
    with open(f"{a.out}/qual_samples_seed52052.txt", "w") as f:
        for ro in K.READOUTS:
            for m in ("hdA0", "hdB0"):
                for d in ("rev", "fwd"):
                    for g, arms in GR.items():
                        pool_ = sorted([r for r in rows if r["readout"] == ro and r["model"] == m and r["direction"] == d and r["arm"] in arms], key=lambda r: r["key"])
                        if not pool_:
                            continue
                        pick = rng.sample(pool_, min(10, len(pool_)))
                        f.write(f"\n######## CELL {ro}|{m}|{d}({K.DIRNAME[d]})|{g} (random {len(pick)} of {len(pool_)}, seed 52052)\n")
                        for i, r in enumerate(pick):
                            N += 1; c = r["conduct"] or {}
                            f.write(f"[{ro}|{m}|{d}|{g}#{i}] {r['arm']} {r['sid']} s{r['sample']} n_tok={r['n_tok']} label={r['label']} strict={r['strict']} judge={r['judge']}"
                                    + (f" help={c['helpfulness']:.1f} flu={c['fluency']:.1f} host={c['hostility']:.1f}" if c else "") + "\n")
                            if i < 2:
                                f.write("  USER: " + U[(r["recipient"], r["sid"])][:200].replace("\n", " ") + "\n")
                            t = (r["text"] or "").replace("\n", " / ")
                            f.write("  " + t[:700] + (f" ...[truncated {len(t) - 700} chars]" if len(t) > 700 else "") + "\n")
    print("DUMPED", N, f"{a.out}/qual_samples_seed52052.txt", flush=True)


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("cmd", choices=["prep", "report", "dump"])
    ap.add_argument("--run_dir", default=None); ap.add_argument("--readouts", default="free"); ap.add_argument("--directions", default="rev")
    ap.add_argument("--models", default="hdA0,hdB0"); ap.add_argument("--sids", default=None); ap.add_argument("--samples", type=int, default=2)
    ap.add_argument("--allow-partial", dest="allow_partial", action="store_true")
    ap.add_argument("--free_dirs", default=None); ap.add_argument("--forced_dir", default=None); ap.add_argument("--out", default=None)
    ap.add_argument("--summary", default=SUMMARY)
    a = ap.parse_args()
    {"prep": prep, "report": report, "dump": dump}[a.cmd](a)
