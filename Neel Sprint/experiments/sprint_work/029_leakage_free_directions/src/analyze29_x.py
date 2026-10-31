"""sw029 analysis (prep agent, E2, 31 Oct 2026; CPU, system python3 or si venv; numpy only). Adapted from sw052 analyze52_x.py.
  prep   : manifest of EXPECTED keys (per readout: models x directions x sids x samples x 23 arms; never from what exists); every key
           present exactly once; writes <run_dir>/judgein.jsonl (key, user = the recipient's last user message, text, cell =
           readout|model|direction|arm, disagree = STRICT != lexicon, always = disagree or a free sample-0 row, for damage; D16) + manifest.json.
           Exit 2 if incomplete (unless --allow-partial).
  report : labels: STRICT + lexicon on every reply; primary label = two-judge consensus where judged (habit = mean > 5), else STRICT
           (the 20 % policy). Estimands exactly as design_spec.md, per readout x model x direction (paired bootstrap over the 64
           scripts, both samples of a script together, B = 2,000, seed 0; the same draws for every statistic):
             PRIMARY SCALE (design_spec Amendment 1, 00:52 UTC): the UNCONDITIONAL rival rate = replies carrying the rival (rival or
             both) / all replies. Beside it, never deciding: selection = rival share among habit-bearing replies (rival 1, both 0.5,
             with n), onset = habit-bearing / all, and the unconditional HELPER rate (helper or both) / all; an arm whose helper rate
             rises by >= 0.10 vs none is flagged as a generic tangent amplifier.
             toward(arm) = change of the unconditional rival rate vs none in the donor's direction (induce +shift, remove -shift);
             ratio(arm) = toward(arm) / toward(r1); margin(arm) = toward(arm) - toward(pooled A of that arm), with CIs;
             free gap = rival rate(self-hostile context, none) - rival rate(user-hostile context, none) (signed; = donor - recipient
             for induce, and the same quantity in the donor's direction for remove; needs both directions);
             mean cos^2(u_arm, u_r1) over L16-63 (fold-averaged, dirs29_summary.json) beside every ratio;
             counterbalanced pair = the mean of the two models' values per bootstrap draw.
           FROZEN RULE (free readout, induce decides, per arm x model):
             precondition: r1 induce toward >= 0.50 x free gap, else NOT_SCORED for that model;
             PASS (UPSTREAM) if ratio >= 0.50 and margin > 0 with its 95 % CI excluding 0 (lower bound > 0; D13);
             LOW if ratio <= 0.15 or the margin CI includes 0; MID otherwise.
             overall: UPSTREAM if any arm passes in a model ("a leakage-free variable at <site> carries the induction (<model>)";
             both models: "recurring across the two assignments"); DECISION_CODE_ONLY if every leakage-free arm (Part A plus sw052's
             c1, read from its results52.json) is LOW in both models; INTERMEDIATE otherwise; PENDING while c1 or the gap is missing
             and the branch depends on it.
             Remove (reported beside it): "specific" only if margin > 0 with CI excluding 0 AND |pooled A shift| <= 0.15 (same scale).
           Also: cumulative offsets (A / arm, and every arm vs r1 at the header) from the hook logs; damage (judged helpfulness /
           fluency / hostility, cap-hit, non-empty); cells with < 20 habit-bearing replies flagged; judge agreement.
  noP    : residual-habit (leakage) check on the noP free replies: onset and rival share per condition and model (STRICT, lexicon),
           next to sw028's with-prohibition `none` cells.
  dump   : 10 seeded-random raw outputs per key cell (readout x model x direction x {none, r1, each arm, each arm's pooled A}).
  python3 analyze29_x.py prep --run_dir D --readouts free --directions rev,fwd [--sids ...] [--samples N] [--allow-partial]
  python3 analyze29_x.py report --run_dirs D[,D2] --out OUT [--summary dirs29_summary.json] [--sw052 results52.json] [--allow-partial]
  python3 analyze29_x.py noP --noP_dir D --out OUT
  python3 analyze29_x.py dump --run_dirs D --out OUT"""
import argparse, glob, json, os, random, sys
from collections import defaultdict

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import common29 as K  # noqa: E402

NS = "/workspace/Neel Sprint"
SW8 = f"{NS}/experiments/sprint_work/008_hostility_attribution/src/out"
LIB = "/workspace/runs_executor/day_2026-10-31_E2/lib"
sys.path.insert(0, LIB)
import labels as LB  # noqa: E402

FIELDS = ["bee", "crow", "helpfulness", "fluency", "hostility"]
NB, SEED = 2000, 0
RATIO_UP, RATIO_LOW, PRECOND, REMOVE_A_MAX = 0.50, 0.15, 0.50, 0.15     # frozen rule constants (design_spec.md)
MIN_HABIT = 20
HELPER_FLAG = 0.10                                                     # Amendment 1: helper-rate rise that flags a generic tangent amplifier
SGN = {"rev": 1.0, "fwd": -1.0}
GROUPS = ("none", K.REF) + K.LF_ARMS + tuple(f"{a}_Apool" for a in K.LF_ARMS) + K.A_ARMS


def contexts():
    U, sids = {}, set()
    for l in open(f"{SW8}/contexts.jsonl"):
        c = json.loads(l)
        if c["cond"] in ("self-hostile", "user-hostile"):
            U[(c["cond"], c["sid"])] = c["msgs"][-1]["content"]; sids.add(c["sid"])
    return U, sorted(sids)


def judge_key(stage, key):
    """judge keys carry the stage (smoke / full / ...) as well as the readout, so files of different stages can never collide."""
    assert key.startswith(f"{K.EXP}|")
    return key.replace(f"{K.EXP}|", f"{K.EXP}-{stage}|", 1)


def pick_sids(all_sids, s):
    return [x for x in all_sids if not s or x in set(s.split(","))]


def expected(ros, models, sids, dirs, samples):
    ns = (lambda ro, d: samples) if samples else K.n_samples
    return [K.row_key(ro, m, d, s, arm, k) for ro in ros for m in models for d in dirs for s in sids for k in range(ns(ro, d)) for arm in K.ARMS]


# ------------------------------------------------------------------------------------------------- prep
def prep(a):
    U, all_sids = contexts(); sids = pick_sids(all_sids, a.sids)
    models = a.models.split(","); dirs = a.directions.split(","); ros = a.readouts.split(",")
    exp = expected(ros, models, sids, dirs, a.samples); assert len(set(exp)) == len(exp)
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
            f.write(json.dumps(dict(key=judge_key(a.stage, k), row_key=k, stage=a.stage, exp=K.EXP, readout=r["readout"], model=r["model"], direction=r["direction"], arm=r["arm"], sid=r["sid"],
                                    sample=r["sample"], cell=f"{r['readout']}|{r['model']}|{r['direction']}|{r['arm']}",
                                    user=U[(r["recipient"], r["sid"])], text=t or "(empty reply)", disagree=dis,
                                    always=bool(dis or (r["sample"] == 0 and r["readout"] == "free")))) + "\n")   # D16: damage sample = free s0 only
    json.dump(dict(expected=exp, n_expected=len(exp), n_present=len(keys), complete=not missing, readouts=ros, directions=dirs, models=models,
                   sids=sids, samples=a.samples or "default", stage=a.stage), open(f"{a.run_dir}/manifest.json", "w"))
    print("PREP_DONE", len(keys), flush=True)


# ------------------------------------------------------------------------------------------------- labels
def label_rows(rows, J):
    for r in rows:
        h = K.HELPER[r["model"]]; t = r["text"] or ""
        r["strict"] = LB.role_label(LB.strict_label(t), h); r["lex"] = LB.role_label(LB.lexicon_label(t), h); r["disagree"] = r["strict"] != r["lex"]
        c = J.get(r["key"])
        r["judge"] = LB.role_label(LB._lab(c["bee"] > 5, c["crow"] > 5), h) if c else None
        r["label"] = r["judge"] if c else r["strict"]
        r["conduct"] = {k: c[k] for k in ("hostility", "helpfulness", "fluency")} if c else None
        br = K.BRIDGES.get(r["readout"])
        r["nonempty"] = bool(t.strip()) and (not br or len(t) > len(br) + 3)
    return rows


def load_dir(d):
    man = json.load(open(f"{d}/manifest.json")); exp = set(man["expected"])
    J = {}
    if os.path.exists(f"{d}/judged.jsonl"):
        import judge_lib as JL
        st = man["stage"]; back = {judge_key(st, k): k for k in exp}
        J = {back[k]: v for k, v in JL.consensus(JL.load_judged(f"{d}/judged.jsonl", FIELDS, keys=set(back)), FIELDS).items()}
    rows = [r for ro in man["readouts"] for m in man["models"] for r in K.jl(f"{d}/{ro}/{ro}_{m}.jsonl") if r["key"] in exp]
    label_rows(rows, J)
    man["n_rows"] = len(rows); man["n_judged"] = len(J); man["complete_rows"] = len(rows) == len(exp)
    return rows, man


class Boot:
    """paired script bootstrap: W [B, n_sids] multiplicities (every sample of a script travels together)."""
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

    def stats(self, v):
        out = {}
        for nm, (num, den) in dict(share=(v["num"], v["hab"]), onset=(v["hab"], v["n"]), unc=(v["unc"], v["n"]), hel=(v["hel"], v["n"])).items():
            pt = float(num.sum() / den.sum()) if den.sum() else float("nan")
            out[nm] = (pt, self._rat(self.W @ num, self.W @ den))
        return out


def ci(x):
    x = np.asarray(x); x = x[~np.isnan(x)]
    return [float(np.quantile(x, .025)), float(np.quantile(x, .975))] if len(x) else [float("nan"), float("nan")]


def arm_verdict(ratio, margin, margin_ci):
    """the frozen per-arm reading (induce). D13: 'margin's CI excludes 0' for a pass means margin > 0 with CI lower bound > 0."""
    if ratio != ratio or margin != margin:
        return "NOT_ESTIMABLE"
    excl = margin_ci[0] > 0 or margin_ci[1] < 0
    if ratio >= RATIO_UP and margin > 0 and margin_ci[0] > 0:
        return "PASS"
    if ratio <= RATIO_LOW or not excl:
        return "LOW"
    return "MID"


def readout_block(rows, ro, models, B, cos2):
    cell = defaultdict(list)
    for r in rows:
        cell[(r["model"], r["direction"], r["arm"])].append(r)
    dirs_present = sorted({r["direction"] for r in rows})
    out = dict(readout=ro, directions=dirs_present, cells={}, models={}, flags=[], helper_flags=[])
    TB = {}
    for m in models:
        base = {}
        for d in dirs_present:
            byarm = {a: cell[(m, d, a)] for a in K.ARMS}
            S0 = B.stats(B.vec(byarm["none"])); base[d] = S0
            groups = {g: byarm[g] for g in ("none", K.REF) + K.LF_ARMS + K.A_ARMS}
            for arm in K.LF_ARMS:
                groups[f"{arm}_Apool"] = [r for a in K.A_OF[arm] for r in byarm[a]]
            for g, R in groups.items():
                if not R:
                    continue
                S = B.stats(B.vec(R)); Sst = B.stats(B.vec(R, "strict"))
                c = dict(n=len(R), n_habit=int(sum(r["label"] in ("helper", "rival", "both") for r in R)))
                for nm in ("share", "onset", "unc", "hel"):
                    pt, bs = S[nm]; pt0, bs0 = S0[nm]
                    c[nm] = pt; c[f"{nm}_ci"] = ci(bs)
                    if g != "none":
                        c[f"{nm}_shift"] = pt - pt0; c[f"{nm}_shift_ci"] = ci(bs - bs0)
                c["strict_unc"] = Sst["unc"][0]; c["strict_share"] = Sst["share"][0]; c["strict_onset"] = Sst["onset"][0]
                if g != "none":
                    sg = SGN[d]; tw = sg * (S["unc"][1] - S0["unc"][1]); TB[(m, d, g)] = tw          # PRIMARY: unconditional rival rate
                    c["toward"] = sg * c["unc_shift"]; c["toward_ci"] = ci(tw)
                    c["share_toward"] = sg * c["share_shift"]; c["share_toward_ci"] = ci(sg * (S["share"][1] - S0["share"][1]))   # beside, never decides
                    if c["hel_shift"] >= HELPER_FLAG:
                        out["helper_flags"].append(f"{ro}|{m}|{d}|{g}: helper rate +{c['hel_shift']:.3f} vs none (>= {HELPER_FLAG}: generic tangent amplifier)")
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
        M = {}
        if "fwd" in base and "rev" in base:
            M["gap"] = base["fwd"]["unc"][0] - base["rev"]["unc"][0]; M["gap_ci"] = ci(base["fwd"]["unc"][1] - base["rev"]["unc"][1])   # signed (Amendment 1)
            M["unc_none_self_hostile"] = base["fwd"]["unc"][0]; M["unc_none_user_hostile"] = base["rev"]["unc"][0]
            M["share_gap_beside"] = base["fwd"]["share"][0] - base["rev"]["share"][0]
            M["share_none_self_hostile"] = base["fwd"]["share"][0]; M["share_none_user_hostile"] = base["rev"]["share"][0]
        for d in dirs_present:
            if (m, d, K.REF) not in TB:
                continue
            c = out["cells"]; tr = c[f"{m}|{d}|{K.REF}"]["toward"]; br = TB[(m, d, K.REF)]
            D = dict(r1_toward=tr, r1_toward_ci=c[f"{m}|{d}|{K.REF}"]["toward_ci"], arms={})
            if "gap" in M:
                D["r1_frac_of_gap"] = tr / M["gap"] if M["gap"] > 0 else float("nan")
            for arm in K.LF_ARMS:
                if (m, d, arm) not in TB:
                    continue
                ta = c[f"{m}|{d}|{arm}"]["toward"]; ba = TB[(m, d, arm)]; bp = TB.get((m, d, f"{arm}_Apool"))
                with np.errstate(invalid="ignore", divide="ignore"):
                    rb = ba / br
                E = dict(toward=ta, toward_ci=c[f"{m}|{d}|{arm}"]["toward_ci"], ratio=(ta / tr) if tr else float("nan"), ratio_ci=ci(rb),
                         ratio_boot_den_le0=float(np.mean(br <= 0)), mean_cos2=(cos2.get(arm) or {}).get(m))
                if bp is not None:
                    tp = c[f"{m}|{d}|{arm}_Apool"]["toward"]
                    E.update(poolA_toward=tp, poolA_shift=c[f"{m}|{d}|{arm}_Apool"]["unc_shift"], margin=ta - tp, margin_ci=ci(ba - bp),
                             share_toward_beside=c[f"{m}|{d}|{arm}"]["share_toward"], helper_shift=c[f"{m}|{d}|{arm}"]["hel_shift"])
                    if d == "rev":
                        E["verdict"] = arm_verdict(E["ratio"], E["margin"], E["margin_ci"])
                    else:
                        E["remove_specific"] = bool(E["margin"] > 0 and E["margin_ci"][0] > 0 and abs(E["poolA_shift"]) <= REMOVE_A_MAX)
                D["arms"][arm] = E
            M[d] = D
        if ro == "free" and "rev" in M:
            pre = M["rev"].get("r1_frac_of_gap")
            if pre is None:
                M["precondition"] = dict(status="PENDING", why="the free gap needs both directions' none arms")
            elif pre != pre or pre < PRECOND:
                M["precondition"] = dict(status="FAILED", r1_frac_of_gap=pre, gap=M.get("gap"), why=f"r1 induce closes {pre} < {PRECOND} of the free gap (or gap <= 0): NOT_SCORED")
            else:
                M["precondition"] = dict(status="OK", r1_frac_of_gap=pre)
        out["models"][m] = M
    # counterbalanced pair (mean of the two models per draw)
    CB = {}
    if all(mm in models for mm in ("hdA0", "hdB0")):
        for d in dirs_present:
            E = {}
            for g in (K.REF,) + K.LF_ARMS + tuple(f"{a}_Apool" for a in K.LF_ARMS):
                if all((mm, d, g) in TB for mm in ("hdA0", "hdB0")):
                    E[g] = (0.5 * (out["cells"][f"hdA0|{d}|{g}"]["toward"] + out["cells"][f"hdB0|{d}|{g}"]["toward"]), 0.5 * (TB[("hdA0", d, g)] + TB[("hdB0", d, g)]))
            if K.REF in E:
                R = dict(toward={g: v[0] for g, v in E.items()}, toward_ci={g: ci(v[1]) for g, v in E.items()}, arms={})
                for arm in K.LF_ARMS:
                    if arm in E and f"{arm}_Apool" in E:
                        with np.errstate(invalid="ignore", divide="ignore"):
                            R["arms"][arm] = dict(ratio=E[arm][0] / E[K.REF][0] if E[K.REF][0] else float("nan"), ratio_ci=ci(E[arm][1] / E[K.REF][1]),
                                                  margin=E[arm][0] - E[f"{arm}_Apool"][0], margin_ci=ci(E[arm][1] - E[f"{arm}_Apool"][1]))
                CB[d] = R
    out["counterbalanced"] = CB
    return out


def sw052_c1(path):
    """sw052's c1 (ctrlB0's d_self) per model, free induce: ratio, margin vs its pooled A, verdict under THIS rule's reading."""
    if not path or not os.path.exists(path):
        return None
    R = json.load(open(path)); out = {}
    for m in ("hdA0", "hdB0"):
        D = (((R.get("free") or {}).get("models") or {}).get(m) or {}).get("rev")
        if not D:
            continue
        mg = D.get("c1_minus_poolA"); mci = D.get("c1_minus_poolA_ci")
        out[m] = dict(ratio=D.get("ratio"), ratio_ci=D.get("ratio_ci"), margin_vs_poolA=mg, margin_ci=mci,
                      verdict=arm_verdict(D["ratio"], mg, mci) if mg is not None and mci else "NOT_ESTIMABLE", src=path)
    return out


def sw052_c1_raw(dirs, sids, B, models):
    """D13: sw052's c1 recomputed on Amendment 1's scale from its raw free rows (induce dir, plus the remove dir for the gap),
    labelled exactly as here (judge consensus where its judged.jsonl has both judges, else STRICT), same bootstrap draws:
    toward = change of the unconditional rival rate; ratio = toward(c1)/toward(r1); margin = toward(c1) - toward(pooled A0-A2)."""
    dirs = [d for d in (dirs or "").split(",") if d and os.path.isdir(d)]
    if not dirs:
        return None
    rows = []
    for d in dirs:
        J = {}
        if os.path.exists(f"{d}/judged.jsonl"):
            import judge_lib as JL
            J = JL.consensus(JL.load_judged(f"{d}/judged.jsonl", FIELDS), FIELDS)
        for m in models:
            rows += label_rows([r for r in K.jl(f"{d}/free/free_{m}.jsonl") if r["sid"] in B.sidx], J)
    out = {}
    for m in models:
        R = [r for r in rows if r["model"] == m]
        cell = defaultdict(list)
        for r in R:
            cell[(r["direction"], r["arm"])].append(r)
        n_exp = 64 * 2 * 8
        if len(cell[("rev", "c1")]) < 64 * 2 or len(cell[("rev", "none")]) < 64 * 2:
            out[m] = dict(verdict="PENDING (sw052 induce incomplete)", n_rows_rev=sum(len(v) for (d_, _), v in cell.items() if d_ == "rev")); continue
        st = {k: B.stats(B.vec(v))["unc"] for k, v in cell.items()}
        poolA = B.stats(B.vec([r for a in ("A0", "A1", "A2") for r in cell[("rev", a)]]))["unc"]
        t = lambda x: (x[0] - st[("rev", "none")][0], x[1] - st[("rev", "none")][1])
        r1, c1, pa = t(st[("rev", "r1")]), t(st[("rev", "c1")]), t(poolA)
        with np.errstate(invalid="ignore", divide="ignore"):
            E = dict(r1_toward=r1[0], c1_toward=c1[0], ratio=c1[0] / r1[0] if r1[0] else float("nan"), ratio_ci=ci(c1[1] / r1[1]),
                     margin=c1[0] - pa[0], margin_ci=ci(c1[1] - pa[1]), scale="unconditional rival rate (Amendment 1)", src=dirs)
        if ("fwd", "none") in st and len(cell[("fwd", "none")]) >= len(cell[("rev", "none")]):   # the remove job complete for none
            gap = st[("fwd", "none")][0] - st[("rev", "none")][0]; E["gap"] = gap; E["r1_frac_of_gap"] = r1[0] / gap if gap > 0 else float("nan")
        E["verdict"] = arm_verdict(E["ratio"], E["margin"], E["margin_ci"])
        if E.get("r1_frac_of_gap") is None:
            E["note"] = f"sw052 remove none arm incomplete ({len(cell[('fwd', 'none')])} rows): its precondition is not checked here"
        elif not (E["r1_frac_of_gap"] >= PRECOND):
            E["verdict"] = "NOT_SCORED (sw052 r1 precondition failed)"
        out[m] = E
    return out


def overall(free, models, c1):
    """the frozen overall reading. Only arms of models whose precondition is OK count."""
    res = dict(per_model={}, statements=[])
    passes = defaultdict(list)
    for m in models:
        M = free["models"].get(m, {}); pre = (M.get("precondition") or {}).get("status")
        arms = (M.get("rev") or {}).get("arms", {})
        V = {arm: arms[arm].get("verdict", "NOT_ESTIMABLE") for arm in K.LF_ARMS if arm in arms}
        res["per_model"][m] = dict(precondition=pre, arms=V, c1=(c1 or {}).get(m, {}).get("verdict", "PENDING (sw052 results not found)"))
        if pre == "OK":
            for arm, v in V.items():
                if v == "PASS":
                    passes[arm].append(m)
    if passes:
        for arm, ms in passes.items():
            site = K.SITE[arm]
            res["statements"].append(f"UPSTREAM: a leakage-free variable at {site} ({arm}) carries the induction ({', '.join(ms)})"
                                     + ("; recurring across the two assignments" if len(ms) == 2 else ""))
        res["verdict"] = "UPSTREAM"; return res
    pres = [res["per_model"][m]["precondition"] for m in models]
    if any(p != "OK" for p in pres):
        res["verdict"] = "PENDING" if any(p == "PENDING" for p in pres) else "NOT_SCORED (precondition failed in " + ",".join(m for m in models if res["per_model"][m]["precondition"] == "FAILED") + ")"
        if not any(p == "PENDING" for p in pres) and any(p == "OK" for p in pres):
            res["verdict"] = "PARTIAL: " + res["verdict"]
        return res
    all_low = all(v == "LOW" for m in models for v in res["per_model"][m]["arms"].values()) and \
        all(len(res["per_model"][m]["arms"]) == len(K.LF_ARMS) for m in models)
    c1v = [res["per_model"][m]["c1"] for m in models]
    if all_low and all(v == "LOW" for v in c1v):
        res["verdict"] = "DECISION_CODE_ONLY"
        res["statements"].append("no upstream conduct variable found at these sites; d_self is a decision code under these conditions")
    elif all_low and any(str(v).startswith("PENDING") for v in c1v):
        res["verdict"] = "PENDING (every Part A arm LOW; sw052's c1 needed for DECISION_CODE_ONLY)"
    else:
        res["verdict"] = "INTERMEDIATE"
    return res


def cumulative(dirs_ro, models):
    out = {}
    for ro, d in dirs_ro:
        for m in models:
            L = K.jl(f"{d}/{ro}/log_{ro}_{m}.jsonl")
            for dd in sorted({e["grp"].split("|")[1] for e in L}):
                g = K.cum_gate(K.cum_ratios([e for e in L if e["grp"].split("|")[1] == dd]))
                out[f"{ro}|{m}|{dd}"] = dict(A_vs_arm={a: v["median_ratio"] for a, v in g["arms"].items()}, A_fail=g["fail"], arm_vs_r1_hdr=g["vs_r1"])
    return out


def report(a):
    _, all_sids = contexts(); sids = pick_sids(all_sids, a.sids); models = a.models.split(",")
    run_dirs = [x for x in a.run_dirs.split(",") if x]; B = Boot(sids)
    summ = json.load(open(a.summary)) if a.summary and os.path.exists(a.summary) else {}
    cos2 = summ.get("mean_cos2_L16_63", {})
    sw052 = a.sw052 or next(iter(sorted(glob.glob("/workspace/runs_executor/sw052/**/results52.json", recursive=True))), None)
    c1 = sw052_c1_raw(a.sw052_dirs, sids, B, models) or sw052_c1(sw052)
    res = dict(inputs=dict(run_dirs=run_dirs, sids=len(sids), models=models, summary=a.summary, sw052=sw052), cos2=cos2,
               cos_vs_r1={arm: {m: {k: v for k, v in (summ.get("cos_vs_r1", {}).get(arm, {}).get(m) or {}).items() if k in ("L16", "L24", "L32", "L40", "L48", "L56", "L63")}
                                for m in models} for arm in K.LF_ARMS}, sw052_c1=c1)
    rows_all, mans, incomplete = [], {}, []
    for d in run_dirs:
        R, man = load_dir(d); rows_all += R
        mans[d] = {k: man[k] for k in ("n_expected", "n_rows", "n_judged", "complete_rows", "directions", "readouts")}
        if not man["complete_rows"]:
            incomplete.append(d)
    res["inputs"]["manifests"] = mans
    if incomplete and not a.allow_partial:
        print("INCOMPLETE inputs:", incomplete, flush=True); sys.exit(2)
    rows_all = [r for r in rows_all if r["sid"] in B.sidx and r["model"] in models]
    cov = {}
    for ro in K.READOUTS:
        R = [r for r in rows_all if r["readout"] == ro]
        if not R:
            continue
        jr = [r for r in R if r["judge"] is not None]; jn = [r for r in jr if not r["disagree"]]
        ag = float(np.mean([r["judge"] == r["strict"] for r in jn])) if jn else None
        cov[ro] = dict(rows=len(R), judged=len(jr), disagree_rows=int(sum(r["disagree"] for r in R)), judge_vs_strict_nondisagree=ag,
                       needs_full_judging=bool(ag is not None and ag < 0.95), labels="judge consensus where judged, else STRICT" if jr else "STRICT only")
    res["coverage"] = cov
    res["readouts"] = {ro: readout_block([r for r in rows_all if r["readout"] == ro], ro, models, B, cos2) for ro in K.READOUTS if any(r["readout"] == ro for r in rows_all)}
    res["cumulative"] = cumulative([(ro, d) for d in run_dirs for ro in mans[d]["readouts"]], models)
    if "free" in res["readouts"]:
        res["OVERALL"] = overall(res["readouts"]["free"], models, c1)
    os.makedirs(a.out, exist_ok=True)
    json.dump(res, open(f"{a.out}/results29.json", "w"), indent=1, default=lambda x: None if x != x else float(x))
    write_text(res, models, f"{a.out}/report29.txt")
    print(open(f"{a.out}/report29.txt").read()[:15000], flush=True)


def write_text(res, models, path):
    f2 = lambda x: "NA" if x is None or (isinstance(x, float) and x != x) else f"{x:+.3f}" if isinstance(x, (float, int)) and abs(x) < 100 else str(x)
    c2 = lambda c: f"[{f2(c[0])}, {f2(c[1])}]" if c else "NA"
    L = [f"sw029 report; coverage {json.dumps(res['coverage'])}", "mean cos^2(u_arm, u_r1) L16-63: " + json.dumps(res["cos2"]),
         "sw052 c1: " + json.dumps(res["sw052_c1"])]
    for ro, blk in res["readouts"].items():
        L.append(f"\n=== readout {ro}{'' if ro == 'free' else ' (FORCED PILOT, does not decide; bridge ' + K.BRIDGE_NOTE[ro] + ')'}; directions {blk['directions']}")
        for m in models:
            M = blk["models"].get(m, {})
            L.append(f"-- {m}: gap (unconditional rival rate, self - user, none) {f2(M.get('gap'))} {c2(M.get('gap_ci'))} (rates {f2(M.get('unc_none_self_hostile'))} / {f2(M.get('unc_none_user_hostile'))};"
                     f" share beside {f2(M.get('share_none_self_hostile'))} / {f2(M.get('share_none_user_hostile'))})"
                     + (f"  precondition {json.dumps(M.get('precondition'))}" if M.get("precondition") else ""))
            for d in blk["directions"]:
                L.append(f"   [{d} = {K.DIRNAME[d]}]")
                for g in GROUPS:
                    c = blk["cells"].get(f"{m}|{d}|{g}")
                    if not c or (g in K.A_ARMS):
                        continue
                    L.append(f"   {g:10s} n {c['n']:4d} RIVAL {f2(c['unc'])} helper {f2(c['hel'])} | share {f2(c['share'])} (hab {c['n_habit']}) onset {f2(c['onset'])}"
                             + (f" | toward {f2(c['toward'])} {c2(c['toward_ci'])} helper_shift {f2(c['hel_shift'])} share_toward {f2(c['share_toward'])} onset_shift {f2(c['onset_shift'])}" if g != "none" else "")
                             + f" | help {f2(c['helpfulness'])} flu {f2(c['fluency'])} host {f2(c['hostility'])} (j {c['n_judged']}) cap {f2(c['cap_hit'])} ne {f2(c['nonempty'])}")
                D = M.get(d)
                if D:
                    L.append(f"   r1 toward {f2(D['r1_toward'])} {c2(D['r1_toward_ci'])} frac of gap {f2(D.get('r1_frac_of_gap'))}")
                    for arm, E in D["arms"].items():
                        L.append(f"   {arm:4s} ratio {f2(E['ratio'])} {c2(E['ratio_ci'])} (mean cos2 {f2(E.get('mean_cos2'))}) margin {f2(E.get('margin'))} {c2(E.get('margin_ci'))}"
                                 f" poolA shift {f2(E.get('poolA_shift'))} -> {E.get('verdict', 'remove_specific=' + str(E.get('remove_specific')))}")
        for d, E in blk["counterbalanced"].items():
            L.append(f"-- counterbalanced [{d}]: " + "; ".join(f"{arm} ratio {f2(v['ratio'])} {c2(v['ratio_ci'])} margin {f2(v['margin'])} {c2(v['margin_ci'])}" for arm, v in E["arms"].items()))
        if blk["helper_flags"]:
            L.append(f"HELPER FLAGS ({len(blk['helper_flags'])}): " + "; ".join(blk["helper_flags"][:40]))
        if blk["flags"]:
            L.append(f"FLAGS (< 20 habit-bearing; {len(blk['flags'])}): " + "; ".join(blk["flags"][:40]))
    L.append("\ncumulative (median A/arm per band and site; arm vs r1 at header): " + json.dumps(res["cumulative"], default=lambda x: None)[:6000])
    if res.get("OVERALL"):
        L.append("OVERALL (free, induce decides): " + json.dumps(res["OVERALL"]))
    open(path, "w").write("\n".join(L) + "\n")


# ------------------------------------------------------------------------------------------------- noP leakage check
def noP(a):
    out = {}
    for m in ("hdA0", "hdB0"):
        R = K.jl(f"{a.noP_dir}/free_noP_{m}.jsonl"); h = K.HELPER[m]
        for cond in ("self-hostile", "user-hostile"):
            C = [r for r in R if r["cond"] == cond]
            for lab in ("strict", "lexicon"):
                L = [LB.role_label((LB.strict_label if lab == "strict" else LB.lexicon_label)(r["text"]), h) for r in C]
                hab = [x for x in L if x in ("helper", "rival", "both")]
                out[f"{m}|{cond}|{lab}"] = dict(n=len(C), n_habit=len(hab), onset=len(hab) / max(len(C), 1),
                                                rival_share=(sum({"rival": 1, "both": .5}.get(x, 0) for x in hab) / len(hab)) if hab else None,
                                                unc_rival=sum(x in ("rival", "both") for x in L) / max(len(C), 1), unc_helper=sum(x in ("helper", "both") for x in L) / max(len(C), 1), cap_hit=sum(r["finish"] == "length" for r in C) / max(len(C), 1))
        for lab in ("strict", "lexicon"):
            s, u = out[f"{m}|self-hostile|{lab}"], out[f"{m}|user-hostile|{lab}"]
            out[f"{m}|gap|{lab}"] = dict(rival_share_gap=(s["rival_share"] - u["rival_share"]) if s["rival_share"] is not None and u["rival_share"] is not None else None,
                                         unc_rival_gap=s["unc_rival"] - u["unc_rival"])
        # sw028's with-prohibition none cells (STRICT): fwd = self-hostile recipient, rev = user-hostile recipient
        p = f"/workspace/runs_executor/sw028/free/free_{m}.jsonl"
        if os.path.exists(p):
            W = [r for r in K.jl(p) if r["arm"] == "none"]
            for d, cond in (("fwd", "self-hostile"), ("rev", "user-hostile")):
                L = [LB.role_label(LB.strict_label(r["text"]), h) for r in W if r["direction"] == d]; hab = [x for x in L if x != "neither"]
                out[f"{m}|{cond}|with_prohibition_sw028_strict"] = dict(n=len(L), onset=len(hab) / max(len(L), 1), unc_rival=sum(x in ("rival", "both") for x in L) / max(len(L), 1),
                                                                        unc_helper=sum(x in ("helper", "both") for x in L) / max(len(L), 1),
                                                                        rival_share=(sum({"rival": 1, "both": .5}.get(x, 0) for x in hab) / len(hab)) if hab else None)
    os.makedirs(a.out, exist_ok=True); json.dump(out, open(f"{a.out}/noP_leakage.json", "w"), indent=1)
    for k, v in out.items():
        print(k, json.dumps({x: (round(y, 3) if isinstance(y, float) else y) for x, y in v.items()}))


# ------------------------------------------------------------------------------------------------- dump
def dump(a):
    U, _ = contexts(); rows = []
    for d in [x for x in a.run_dirs.split(",") if x]:
        R, _ = load_dir(d); rows += R
    GR = {g: (g,) for g in ("none", K.REF) + K.LF_ARMS}
    GR.update({f"{arm}_Apool": K.A_OF[arm] for arm in K.LF_ARMS})
    rng = random.Random(29029); N = 0
    os.makedirs(a.out, exist_ok=True)
    with open(f"{a.out}/qual_samples_seed29029.txt", "w") as f:
        for ro in K.READOUTS:
            for m in ("hdA0", "hdB0"):
                for d in ("rev", "fwd"):
                    for g, arms in GR.items():
                        pool_ = sorted([r for r in rows if r["readout"] == ro and r["model"] == m and r["direction"] == d and r["arm"] in arms], key=lambda r: r["key"])
                        if not pool_:
                            continue
                        pick = rng.sample(pool_, min(10, len(pool_)))
                        f.write(f"\n######## CELL {ro}|{m}|{d}({K.DIRNAME[d]})|{g} (random {len(pick)} of {len(pool_)}, seed 29029)\n")
                        for i, r in enumerate(pick):
                            N += 1; c = r["conduct"] or {}
                            f.write(f"[{ro}|{m}|{d}|{g}#{i}] {r['arm']} {r['sid']} s{r['sample']} n_tok={r['n_tok']} label={r['label']} strict={r['strict']} judge={r['judge']}"
                                    + (f" help={c['helpfulness']:.1f} flu={c['fluency']:.1f} host={c['hostility']:.1f}" if c else "") + "\n")
                            t = (r["text"] or "").replace("\n", " / ")
                            f.write("  " + t[:700] + (f" ...[truncated {len(t) - 700} chars]" if len(t) > 700 else "") + "\n")
    print("DUMPED", N, f"{a.out}/qual_samples_seed29029.txt", flush=True)


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("cmd", choices=["prep", "report", "noP", "dump"])
    ap.add_argument("--run_dir", default=None); ap.add_argument("--run_dirs", default=""); ap.add_argument("--readouts", default="free")
    ap.add_argument("--directions", default="rev,fwd"); ap.add_argument("--models", default="hdA0,hdB0"); ap.add_argument("--sids", default=None)
    ap.add_argument("--samples", type=int, default=0); ap.add_argument("--stage", default="full"); ap.add_argument("--allow-partial", dest="allow_partial", action="store_true")
    ap.add_argument("--out", default=None); ap.add_argument("--summary", default="/workspace/runs_executor/sw029/dirs29_summary.json")
    ap.add_argument("--sw052", default=None); ap.add_argument("--sw052_dirs", default="/workspace/runs_executor/sw052/induce,/workspace/runs_executor/sw052/remove"); ap.add_argument("--noP_dir", default="/workspace/runs_executor/sw029/noP_free")
    a = ap.parse_args()
    {"prep": prep, "report": report, "noP": noP, "dump": dump}[a.cmd](a)
