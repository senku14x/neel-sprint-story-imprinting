"""sw039 Part 2 analysis: the asT dose sweep (prep-D fork, E2, 31 Oct 2026; box 1, system python3, numpy only). Adapted from sw038
Part 1 analyze38p1.py (labels, judge keys, bootstraps, cells, uptake line, dump). Written and tested on fake data (test39p2_an.py)
BEFORE any full-run output.
  prep   : manifest of EXPECTED keys (K.expected_keys: readouts x models x directions x 61 sids x samples x 16 arms; never from what
           exists); every key present exactly once; writes <run_dir>/judgein.jsonl (key = sw039-<stage>|<part>|..., row_key, cell =
           readout|model|direction|arm, user = the recipient context's last user message, text, disagree = STRICT != lexicon,
           always = disagree or a free sample-0 row) + manifest.json. Exit 2 if incomplete (unless --allow-partial).
  report : label = two-judge reply5 consensus where judged (habit = mean > 5), else STRICT. Per readout x model x direction x group
           (none, asT_a<alpha>, each A arm, the pooled A of each dose 'asT_a<alpha>_Apool'): the UNCONDITIONAL rival rate (PRIMARY),
           helper rate, share among habit-bearing (rival 1, both 0.5; with n), onset, cap-hit, non-empty, judged damage (free
           sample-0 rows). Paired bootstrap over the 61 scripts (B = 2,000, numpy default_rng(0), every sample of a script together,
           the same draws for every statistic, both models and both directions); domain-clustered bootstrap (8 domains, seed 1) beside.
           toward(g) = SGN[d] x (rate(g) - rate(none)); margin(alpha) = toward(asT_a<alpha>) - toward(pooled A of alpha); gap =
           rate(remove none) - rate(induce none); fraction = toward / gap (beside).
           READINGS (design_spec Part 2; per model; free induce DECIDES; fbtw and remove computed the same way, beside; the
           counterbalanced pair = the mean of the two models per draw, beside):
             DIAL       = every step 0.5->1, 1->1.5, 1.5->2 of toward has CI upper >= 0 (">= 0 within CI") AND Spearman rho of the five
                          point towards vs alpha >= 0.9 AND margin CI lower > 0 at every alpha >= 1. A needed margin NOT_SCORED (that
                          dose's cumulative gate failed) -> DIAL = NOT_SCORED unless another condition already fails (-> False).
             SATURATES  = toward(1.5) - toward(1) <= 0.10 AND toward(3) - toward(1) <= 0.15 (point estimates; CIs beside).
             GENERIC AT HIGH DOSE = some dose's pooled A toward >= 0.15 with CI lower > 0; the lowest such dose is reported. Doses whose
                          cumulative gate failed are not scored for it (listed).
             Overshoot (reported) = SGN[d] x (rate(d, asT_a<alpha>) - rate(donor none)), donor none = the other direction's none arm
                          (induce: the self-hostile context's own no-edit rate, same scripts), alpha in {2, 3}, CI beside.
             Damage per dose (free sample-0 judged rows of the dose's real arm, per direction): a dose whose mean fluency is > 1 point
                          below none's is DAMAGING; a reading that uses a damaging dose is marked BESIDE_ONLY (DIAL uses all five
                          doses, SATURATES 1 / 1.5 / 3, GENERIC the reported dose). Unjudged fluency -> damage unreadable (None).
             Cumulative gate per dose (from the same readout x direction's hook logs): both A arms' median ratio in [0.9, 1.1] at
                          L28-40 and L44-63; a failing dose's margin is NOT_SCORED.
             An uptake / suppression line per dose (sw038 D18's rule).
  dump   : 10 seeded-random raw outputs per key cell (readout x model x direction x {none, each dose, each dose's pooled A}).
  python3 analyze39p2.py prep --run_dir D --stage full [--part p2] [--allow-partial]
  python3 analyze39p2.py report --run_dir D --out OUT [--allow-partial]
  python3 analyze39p2.py dump --run_dir D --out OUT"""
import argparse, json, os, random, sys
from collections import defaultdict

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import common39p2 as K  # noqa: E402

LIB = "/workspace/runs_executor/day_2026-10-31_E2/lib"
sys.path.insert(0, LIB)
import labels as LB  # noqa: E402

CTX = "/workspace/runs_executor/sw038/p1/inputs/contexts38p1.jsonl"
FIELDS = ["bee", "crow", "helpfulness", "fluency", "hostility"]
NB, SEED, SEED_DOM = 2000, 0, 1
HELPER_FLAG, MIN_HABIT = 0.10, 20
RHO_DIAL, SAT_15, SAT_3, GENERIC_BAR, DMG_FLU = 0.9, 0.10, 0.15, 0.15, 1.0
POOL = {arm: f"{arm}_Apool" for arm in K.REAL}
GROUPS = ("none",) + K.REAL + tuple(POOL.values()) + K.A_ARMS
STEPS = ((0.5, 1.0), (1.0, 1.5), (1.5, 2.0))


def contexts(path=CTX):
    U, dom = {}, {}
    if path and os.path.exists(path):
        for r in K.jl(path):
            U[(r["cond"], r["sid"])] = r["msgs"][-1]["content"]; dom[r["sid"]] = r["domain"]
    return U, dom


def judge_key(stage, key):
    assert key.startswith(f"{K.EXP}|")
    return key.replace(f"{K.EXP}|", f"{K.EXP}-{stage}|", 1)


def row_files(run_dir, ro, m, d):
    return f"{run_dir}/{ro}/{ro}_{m}_{d}.jsonl"


# ------------------------------------------------------------------------------------------------- prep
def prep(a):
    U, dom = contexts(a.ctx); sids = sorted(dom)
    assert sids, f"contexts file {a.ctx} missing or empty (the manifest's sids and user turns come from it)"
    if a.sids:
        sids = [s for s in sids if s in set(a.sids.split(","))]
    models = a.models.split(","); dirs = a.directions.split(","); ros = a.readouts.split(",")
    exp = K.expected_keys(ros, models, sids, dirs, samples=a.samples, part=a.part); assert len(set(exp)) == len(exp)
    rows, dup = {}, []
    for ro in ros:
        for m in models:
            for d in dirs:
                for r in K.jl(row_files(a.run_dir, ro, m, d)):
                    if r["key"] in rows:
                        dup.append(r["key"])
                    rows[r["key"]] = r
    se = set(exp); missing = [k for k in exp if k not in rows]; extra = [k for k in rows if k not in se]
    print(f"manifest {len(exp)} expected; present {len(exp) - len(missing)}; missing {len(missing)}; extra {len(extra)}; duplicates {len(dup)}", flush=True)
    assert not dup, f"duplicate keys in outputs: {dup[:5]}"
    if missing and not a.allow_partial:
        print("INCOMPLETE", missing[:5], flush=True); sys.exit(2)
    keys = [k for k in exp if k in rows]
    jk = [judge_key(a.stage, k) for k in keys]; assert len(set(jk)) == len(jk)
    with open(f"{a.run_dir}/judgein.jsonl", "w") as f:
        for k in keys:
            r = rows[k]; t = r["text"] or ""; dis = bool(LB.disagree(t))
            f.write(json.dumps(dict(key=judge_key(a.stage, k), row_key=k, stage=a.stage, exp=K.EXP, part=a.part, readout=r["readout"], model=r["model"],
                                    direction=r["direction"], arm=r["arm"], sid=r["sid"], sample=r["sample"],
                                    cell=f"{r['readout']}|{r['model']}|{r['direction']}|{r['arm']}", user=U[(r["recipient"], r["sid"])],
                                    text=t or "(empty reply)", disagree=dis, always=bool(dis or (r["sample"] == 0 and r["readout"] == "free")))) + "\n")
    json.dump(dict(expected=exp, n_expected=len(exp), n_present=len(keys), complete=not missing, readouts=ros, directions=dirs, models=models,
                   sids=sids, samples=a.samples or "default", stage=a.stage, part=a.part), open(f"{a.run_dir}/manifest.json", "w"))
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
    rows = [r for ro in man["readouts"] for m in man["models"] for dd in man["directions"] for r in K.jl(row_files(d, ro, m, dd)) if r["key"] in exp]
    label_rows(rows, J)
    man["n_rows"] = len(rows); man["n_judged"] = len(J); man["complete_rows"] = len(rows) == len(exp)
    return rows, man


class Boot:
    """script bootstrap: W [B, n_sids] multiplicities (every sample of a script travels together); D = the domain-clustered version."""
    def __init__(self, sids, dom):
        self.sids = sids; self.sidx = {s: i for i, s in enumerate(sids)}
        rng = np.random.default_rng(SEED); draws = rng.integers(0, len(sids), (NB, len(sids)))
        self.W = np.stack([np.bincount(x, minlength=len(sids)) for x in draws]).astype(float)
        doms = sorted({dom[s] for s in sids}); di = {d_: i for i, d_ in enumerate(doms)}
        M = np.zeros((len(doms), len(sids)))
        for s in sids:
            M[di[dom[s]], self.sidx[s]] = 1.0
        rd = np.random.default_rng(SEED_DOM); dd = rd.integers(0, len(doms), (NB, len(doms)))
        self.D = np.stack([np.bincount(x, minlength=len(doms)) for x in dd]).astype(float) @ M

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
            out[nm] = (pt, self._rat(self.W @ num, self.W @ den), self._rat(self.D @ num, self.D @ den))
        return out


def ci(x):
    x = np.asarray(x, dtype=float); x = x[~np.isnan(x)]
    return [float(np.quantile(x, .025)), float(np.quantile(x, .975))] if len(x) else [float("nan"), float("nan")]


def spearman(x, y):
    """Spearman rho with average ranks; nan if either side is constant."""
    def rk(v):
        v = np.asarray(v, dtype=float); o = np.argsort(v, kind="mergesort"); r = np.empty(len(v)); i = 0
        while i < len(v):
            j = i
            while j + 1 < len(v) and v[o[j + 1]] == v[o[i]]:
                j += 1
            r[o[i:j + 1]] = 0.5 * (i + j); i = j + 1
        return r
    a, b = rk(x), rk(y)
    if a.std() == 0 or b.std() == 0:
        return float("nan")
    return float(np.corrcoef(a, b)[0, 1])


# ------------------------------------------------------------------------------------------------- cells
def cells_block(rows, ro, models, B):
    """per (model, direction, group): rates with script and domain CIs, toward vs none. TB[(m, d, g)] = (script, domain) draws of
    toward; RB[(m, d, g)] = (script, domain) draws of the unconditional rival rate."""
    cell = defaultdict(list)
    for r in rows:
        cell[(r["model"], r["direction"], r["arm"])].append(r)
    out, TB, RB, base, flags, hflags = {}, {}, {}, {}, [], []
    for m in models:
        for d in ("induce", "remove"):
            byarm = {a: cell[(m, d, a)] for a in K.ARMS}
            if not byarm["none"]:
                continue
            S0 = B.stats(B.vec(byarm["none"])); base[(m, d)] = S0
            groups = dict(byarm)
            for arm in K.REAL:
                groups[POOL[arm]] = [r for x in K.A_OF[arm] for r in byarm[x]]
            for g, R in groups.items():
                if not R:
                    continue
                S = B.stats(B.vec(R)); Sst = B.stats(B.vec(R, "strict"))
                RB[(m, d, g)] = (S["unc"][1], S["unc"][2])
                c = dict(n=len(R), n_habit=int(sum(r["label"] in ("helper", "rival", "both") for r in R)))
                for nm in ("share", "onset", "unc", "hel"):
                    pt, bs, bd = S[nm]; pt0, bs0, bd0 = S0[nm]
                    c[nm] = pt; c[f"{nm}_ci"] = ci(bs)
                    if g != "none":
                        c[f"{nm}_shift"] = pt - pt0; c[f"{nm}_shift_ci"] = ci(bs - bs0); c[f"{nm}_shift_ci_dom"] = ci(bd - bd0)
                c["strict_unc"] = Sst["unc"][0]; c["strict_share"] = Sst["share"][0]
                if g != "none":
                    sg = K.SGN[d]; tw = sg * (S["unc"][1] - S0["unc"][1]); twd = sg * (S["unc"][2] - S0["unc"][2]); TB[(m, d, g)] = (tw, twd)
                    c["toward"] = sg * c["unc_shift"]; c["toward_ci"] = ci(tw); c["toward_ci_dom"] = ci(twd)
                    c["share_toward"] = sg * c["share_shift"]
                    if c["hel_shift"] >= HELPER_FLAG:
                        hflags.append(f"{ro}|{m}|{d}|{g}: helper rate +{c['hel_shift']:.3f} vs none (>= {HELPER_FLAG})")
                s0 = [r for r in R if r["sample"] == 0 and r["conduct"]]
                c["n_judged_s0"] = len(s0)
                for k in ("helpfulness", "fluency", "hostility"):
                    c[k] = float(np.mean([x["conduct"][k] for x in s0])) if s0 else None
                jr = [r for r in R if r["judge"] is not None]
                c["judge_strict_agree"] = float(np.mean([r["judge"] == r["strict"] for r in jr])) if jr else None
                c["cap_hit"] = float(np.mean([r["finish"] == "length" for r in R])); c["nonempty"] = float(np.mean([r["nonempty"] for r in R]))
                c["mean_n_tok"] = float(np.mean([r["n_tok"] for r in R]))
                if c["n_habit"] < MIN_HABIT:
                    flags.append(f"{ro}|{m}|{d}|{g}: {c['n_habit']} habit-bearing replies (< {MIN_HABIT})")
                out[f"{m}|{d}|{g}"] = c
    return out, TB, RB, base, flags, hflags


def uptake_line(c, d):
    """sw038 D18: induce 'swap' if the helper rate falls by >= half the rival rise, 'uptake' if onset rises by > half of it; remove
    'swap' if the helper rate rises by >= half the rival fall, 'suppression' if onset falls by more than half of it; else 'mixed'."""
    if not c or c.get("unc_shift") is None:
        return "NA"
    du, dh, do = c["unc_shift"], c["hel_shift"], c["onset_shift"]
    if d == "induce":
        k = ("swap (helper replaced by rival)" if du > 0 and dh <= -0.5 * du else "uptake (new rival tangents, onset rises)" if du > 0 and do > 0.5 * du
             else "mixed uptake" if du > 0 else "no rival rise")
    else:
        k = ("swap (rival replaced by helper)" if du < 0 and dh >= -0.5 * du else "suppression (habit onset falls)" if du < 0 and do < 0.5 * du
             else "mixed removal" if du < 0 else "no rival fall")
    return f"{k}: rival {du:+.3f}, helper {dh:+.3f}, onset {do:+.3f}"


def cum_per_dose(run_dir, ro, m, d):
    """per dose: both A arms' median ratio (A / its dose arm) in [0.9, 1.1] at L28-40 and L44-63, from the hook logs."""
    g = K.cum_gate(K.per_unit_ratios(K.jl(f"{run_dir}/{ro}/log_{ro}_{m}_{d}.jsonl")))
    out = {}
    for al in K.DOSES:
        arm = K.DOSE_ARM[al]
        meds = {x: (g["arms"].get(x) or {}).get("median_ratio") for x in K.A_OF[arm]}
        ok = all(x in g["arms"] and g["arms"][x]["in_band"] for x in K.A_OF[arm])
        out[K.dlab(al)] = dict(pass_=bool(ok), medians=meds, missing=[x for x in K.A_OF[arm] if x in g["missing"]])
    out["_dose_vs_a1"] = g["vs_a1"]
    return out


# ------------------------------------------------------------------------------------------------- readings
def readings(T, Mg, PA, gate_ok, damaging):
    """T[alpha] = (point, script draws) of toward(dose arm); Mg[alpha] = margin (point, draws); PA[alpha] = pooled-A toward (point, draws);
    gate_ok[alpha] bool; damaging[alpha] True / False / None. -> the three pre-stated readings with their parts."""
    doses = list(K.DOSES)
    steps = []
    for a0, a1 in STEPS:
        dd = T[a1][1] - T[a0][1]; c = ci(dd)
        steps.append(dict(step=f"{a0:g}->{a1:g}", diff=T[a1][0] - T[a0][0], ci=c, ok=bool(c[1] >= 0)))
    rho = spearman(doses, [T[x][0] for x in doses])
    marg = {}
    for x in doses:
        if not gate_ok[x]:
            marg[K.dlab(x)] = dict(margin=Mg[x][0], ci=ci(Mg[x][1]), scored=False, verdict="NOT_SCORED")
        else:
            c = ci(Mg[x][1]); marg[K.dlab(x)] = dict(margin=Mg[x][0], ci=c, scored=True, beats_poolA=bool(c[0] > 0))
    need = [x for x in doses if x >= 1.0]
    other_ok = all(s["ok"] for s in steps) and (rho == rho and rho >= RHO_DIAL)
    m_ok = [marg[K.dlab(x)].get("beats_poolA") for x in need]
    if not other_ok or any(v is False for v in m_ok):
        dial = False
    elif any(v is None for v in m_ok):
        dial = "NOT_SCORED"
    else:
        dial = True
    s15 = T[1.5][0] - T[1.0][0]; s3 = T[3.0][0] - T[1.0][0]
    sat = bool(s15 <= SAT_15 and s3 <= SAT_3)
    gen = {}
    for x in doses:
        c = ci(PA[x][1])
        gen[K.dlab(x)] = dict(poolA_toward=PA[x][0], ci=c, scored=bool(gate_ok[x]), generic=bool(gate_ok[x] and PA[x][0] >= GENERIC_BAR and c[0] > 0))
    gd = [x for x in doses if gen[K.dlab(x)]["generic"]]
    beside = lambda used: [K.dlab(x) for x in used if damaging.get(x)]
    R = dict(
        DIAL=dict(verdict=dial, steps=steps, spearman_rho=rho, margins=marg, beside_only_damaging=beside(doses)),
        SATURATES=dict(verdict=sat, toward_1p5_minus_1=s15, ci_1p5_minus_1=ci(T[1.5][1] - T[1.0][1]), toward_3_minus_1=s3,
                       ci_3_minus_1=ci(T[3.0][1] - T[1.0][1]), beside_only_damaging=beside((1.0, 1.5, 3.0))),
        GENERIC_AT_HIGH_DOSE=dict(verdict=bool(gd), lowest_dose=(gd[0] if gd else None), per_dose=gen,
                                  not_scored=[K.dlab(x) for x in doses if not gate_ok[x]], beside_only_damaging=beside(gd[:1])))
    for k in R:
        R[k]["status"] = "BESIDE_ONLY" if R[k]["beside_only_damaging"] else "READ"
    return R


def model_block(C, TB, RB, base, run_dir, ro, m, d, dmg_cells):
    """per model x direction: per-dose table + readings + overshoot + damage. Returns (block, the raw draws for the pair)."""
    need = ["none"] + [g for x in K.DOSES for g in (K.DOSE_ARM[x], POOL[K.DOSE_ARM[x]])]
    if any(f"{m}|{d}|{g}" not in C for g in need):
        return None, None
    other = "remove" if d == "induce" else "induce"
    gates = cum_per_dose(run_dir, ro, m, d)
    T, Mg, PA, gok, dmg, per = {}, {}, {}, {}, {}, {}
    cn = dmg_cells.get(f"{m}|{d}|none") or {}
    for x in K.DOSES:
        arm = K.DOSE_ARM[x]; pool = POOL[arm]
        c = C.get(f"{m}|{d}|{arm}"); cp = C.get(f"{m}|{d}|{pool}")
        T[x] = (c["toward"], TB[(m, d, arm)][0]); PA[x] = (cp["toward"], TB[(m, d, pool)][0])
        Mg[x] = (c["toward"] - cp["toward"], TB[(m, d, arm)][0] - TB[(m, d, pool)][0])
        gok[x] = gates[K.dlab(x)]["pass_"]
        cd = dmg_cells.get(f"{m}|{d}|{arm}") or {}
        if cd.get("fluency") is None or cn.get("fluency") is None:
            dmg[x] = None
        else:
            dmg[x] = bool(cd["fluency"] < cn["fluency"] - DMG_FLU)
        e = dict(alpha=x, rival=c["unc"], rival_ci=c["unc_ci"], toward=c["toward"], toward_ci=c["toward_ci"], toward_ci_dom=c["toward_ci_dom"],
                 poolA_rival=cp["unc"], poolA_toward=cp["toward"], poolA_toward_ci=cp["toward_ci"], margin=Mg[x][0],
                 margin_ci=ci(Mg[x][1]) if gok[x] else "NOT_SCORED", margin_ci_dom=ci(TB[(m, d, arm)][1] - TB[(m, d, pool)][1]) if gok[x] else "NOT_SCORED",
                 helper=c["hel"], helper_shift=c["hel_shift"], share=c["share"], n_habit=c["n_habit"], onset=c["onset"], cap_hit=c["cap_hit"],
                 nonempty=c["nonempty"], cum_gate=gates[K.dlab(x)], damaging=dmg[x],
                 damage=dict(fluency=cd.get("fluency"), helpfulness=cd.get("helpfulness"), hostility=cd.get("hostility"), cap_hit=cd.get("cap_hit"),
                             n_judged_s0=cd.get("n_judged_s0"), none_fluency=cn.get("fluency"),
                             poolA_fluency=(dmg_cells.get(f"{m}|{d}|{pool}") or {}).get("fluency")),
                 uptake=uptake_line(c, d))
        if (m, other, "none") in RB:
            don = C[f"{m}|{other}|none"]["unc"]; dr = RB[(m, d, arm)][0] - RB[(m, other, "none")][0]
            e["overshoot_vs_donor_none"] = K.SGN[d] * (c["unc"] - don); e["overshoot_ci"] = ci(K.SGN[d] * dr); e["donor_none_rival"] = don
        gap = None
        if f"{m}|remove|none" in C and f"{m}|induce|none" in C:
            gap = C[f"{m}|remove|none"]["unc"] - C[f"{m}|induce|none"]["unc"]
        e["fraction_of_gap"] = (c["toward"] / gap) if gap else None
        per[K.dlab(x)] = e
    blk = dict(per_dose=per, readings=readings(T, Mg, PA, gok, dmg), damaging=[K.dlab(x) for x in K.DOSES if dmg[x]],
               damage_unreadable=[K.dlab(x) for x in K.DOSES if dmg[x] is None],
               overshoot={K.dlab(x): dict(value=per[K.dlab(x)].get("overshoot_vs_donor_none"), ci=per[K.dlab(x)].get("overshoot_ci"))
                          for x in (2.0, 3.0)}, cumulative=gates)
    return blk, (T, Mg, PA, gok, dmg)


def pair_block(draws):
    """counterbalanced pair: the mean of the two models' toward / margin / pooled-A toward per draw (same script draws)."""
    (Ta, Ma, Pa, ga, da), (Tb, Mb, Pb, gb, db) = draws
    av = lambda X, Y: {x: (0.5 * (X[x][0] + Y[x][0]), 0.5 * (X[x][1] + Y[x][1])) for x in K.DOSES}
    T, Mg, PA = av(Ta, Tb), av(Ma, Mb), av(Pa, Pb)
    gok = {x: bool(ga[x] and gb[x]) for x in K.DOSES}; dmg = {x: bool(da.get(x) or db.get(x)) for x in K.DOSES}
    per = {K.dlab(x): dict(toward=T[x][0], toward_ci=ci(T[x][1]), margin=Mg[x][0], margin_ci=ci(Mg[x][1]), poolA_toward=PA[x][0]) for x in K.DOSES}
    return dict(per_dose=per, readings=readings(T, Mg, PA, gok, dmg))


# ------------------------------------------------------------------------------------------------- report
def report(a):
    U, dom = contexts(a.ctx)
    rows, man = load_dir(a.run_dir)
    if not dom:
        dom = {r["sid"]: r["domain"] for r in rows}
    sids = [s for s in man["sids"] if s in dom]
    B = Boot(sids, dom)
    if not man["complete_rows"] and not a.allow_partial:
        print("INCOMPLETE", man["n_rows"], "of", man["n_expected"], flush=True); sys.exit(2)
    models = man["models"]; rows = [r for r in rows if r["sid"] in B.sidx]
    res = dict(inputs=dict(run_dir=a.run_dir, n_expected=man["n_expected"], n_rows=man["n_rows"], n_judged=man["n_judged"], complete=man["complete_rows"],
                           sids=len(sids), models=models, part=man.get("part")), readouts={})
    cov = {}
    for ro in man["readouts"]:
        R = [r for r in rows if r["readout"] == ro]
        jr = [r for r in R if r["judge"] is not None]; jn = [r for r in jr if not r["disagree"]]
        ag = {m: (float(np.mean([r["judge"] == r["strict"] for r in jn if r["model"] == m])) if any(r["model"] == m for r in jn) else None) for m in models}
        cov[ro] = dict(rows=len(R), judged=len(jr), disagree_rows=int(sum(r["disagree"] for r in R)), judge_vs_strict_nondisagree=ag,
                       needs_full_judging=[m for m, v in ag.items() if v is not None and v < 0.95])
    res["coverage"] = cov
    blocks = {}
    for ro in man["readouts"]:
        blocks[ro] = cells_block([r for r in rows if r["readout"] == ro], ro, models, B)
    dmg_cells = blocks["free"][0] if "free" in blocks else {}
    for ro in man["readouts"]:
        C, TB, RB, base, flags, hflags = blocks[ro]
        blk = dict(readout=ro, primary=ro == "free", cells=C, flags=flags, helper_flags=hflags, models={}, pair={})
        for m in models:
            M = {}
            if (m, "remove") in base and (m, "induce") in base:
                sr, si = base[(m, "remove")]["unc"], base[(m, "induce")]["unc"]
                M.update(gap=sr[0] - si[0], gap_ci=ci(sr[1] - si[1]), gap_ci_dom=ci(sr[2] - si[2]), rate_self_hostile_none=sr[0], rate_user_hostile_none=si[0])
            M["directions"] = {}
            for d in ("induce", "remove"):
                b, _ = model_block(C, TB, RB, base, a.run_dir, ro, m, d, dmg_cells)
                if b:
                    b["decides"] = bool(ro == "free" and d == "induce"); M["directions"][d] = b
            blk["models"][m] = M
        for d in ("induce", "remove"):
            dr = [model_block(C, TB, RB, base, a.run_dir, ro, m, d, dmg_cells)[1] for m in models]
            if len(models) == 2 and all(x is not None for x in dr):
                blk["pair"][d] = pair_block(dr)
        res["readouts"][ro] = blk
    os.makedirs(a.out, exist_ok=True)
    json.dump(res, open(f"{a.out}/results39p2.json", "w"), indent=1, default=lambda x: None if x != x else float(x))
    write_text(res, models, f"{a.out}/report39p2.txt")
    print(open(f"{a.out}/report39p2.txt").read()[:20000], flush=True)
    return res


def write_text(res, models, path):
    f2 = lambda x: "NA" if x is None or (isinstance(x, float) and x != x) else (f"{x:+.3f}" if isinstance(x, (float, int)) and not isinstance(x, bool) else str(x))
    c2 = lambda c: f"[{f2(c[0])}, {f2(c[1])}]" if isinstance(c, list) else str(c)
    L = [f"sw039 Part 2 (asT dose sweep) report; inputs {json.dumps(res['inputs'])}", f"coverage {json.dumps(res['coverage'])}"]
    for ro, blk in res["readouts"].items():
        L.append(f"\n=== readout {ro}" + (" (PRIMARY; free induce decides)" if blk["primary"] else " (beside; helper-skewed bridge, does not decide)"))
        for m in models:
            M = blk["models"].get(m, {})
            L.append(f"-- {m}: gap {f2(M.get('gap'))} {c2(M.get('gap_ci') or [None, None])} (rival rate self-hostile none {f2(M.get('rate_self_hostile_none'))}, "
                     f"user-hostile none {f2(M.get('rate_user_hostile_none'))})")
            for d, b in M.get("directions", {}).items():
                cn = blk["cells"][f"{m}|{d}|none"]
                L.append(f"   [{d}{' DECIDES' if b['decides'] else ''}] none: RIVAL {f2(cn['unc'])} helper {f2(cn['hel'])} onset {f2(cn['onset'])} share {f2(cn['share'])} "
                         f"(hab {cn['n_habit']}) flu {f2(cn['fluency'])} cap {f2(cn['cap_hit'])}")
                for lab, e in b["per_dose"].items():
                    L.append(f"   {lab:5s} RIVAL {f2(e['rival'])} toward {f2(e['toward'])} {c2(e['toward_ci'])} | poolA toward {f2(e['poolA_toward'])} {c2(e['poolA_toward_ci'])}"
                             f" | margin {f2(e['margin'])} {c2(e['margin_ci'])} | helper {f2(e['helper'])} share {f2(e['share'])} (hab {e['n_habit']}) onset {f2(e['onset'])}"
                             f" | frac {f2(e['fraction_of_gap'])} overshoot {f2(e.get('overshoot_vs_donor_none'))} {c2(e.get('overshoot_ci') or [None, None])}"
                             f" | flu {f2(e['damage']['fluency'])} help {f2(e['damage']['helpfulness'])} host {f2(e['damage']['hostility'])} cap {f2(e['cap_hit'])}"
                             f"{' DAMAGING' if e['damaging'] else ''} | gate {e['cum_gate']['pass_']} | {e['uptake']}")
                Rd = b["readings"]
                L.append(f"   DIAL {Rd['DIAL']['verdict']} ({Rd['DIAL']['status']}) rho {f2(Rd['DIAL']['spearman_rho'])} steps "
                         + "; ".join(f"{s['step']} {f2(s['diff'])} {c2(s['ci'])}" for s in Rd["DIAL"]["steps"]))
                L.append(f"   SATURATES {Rd['SATURATES']['verdict']} ({Rd['SATURATES']['status']}) 1.5-1 {f2(Rd['SATURATES']['toward_1p5_minus_1'])} "
                         f"{c2(Rd['SATURATES']['ci_1p5_minus_1'])}; 3-1 {f2(Rd['SATURATES']['toward_3_minus_1'])} {c2(Rd['SATURATES']['ci_3_minus_1'])}")
                G = Rd["GENERIC_AT_HIGH_DOSE"]
                L.append(f"   GENERIC AT HIGH DOSE {G['verdict']} lowest dose {G['lowest_dose']} ({G['status']}); not scored {G['not_scored']}")
        for d, P in blk["pair"].items():
            Rd = P["readings"]
            L.append(f"-- pair (mean of the two models) [{d}]: " + "; ".join(f"{k} toward {f2(v['toward'])} {c2(v['toward_ci'])} margin {f2(v['margin'])}"
                                                                          for k, v in P["per_dose"].items())
                     + f" | DIAL {Rd['DIAL']['verdict']} SATURATES {Rd['SATURATES']['verdict']} GENERIC {Rd['GENERIC_AT_HIGH_DOSE']['lowest_dose']}")
        if blk["helper_flags"]:
            L.append(f"HELPER FLAGS ({len(blk['helper_flags'])}): " + "; ".join(blk["helper_flags"][:40]))
        if blk["flags"]:
            L.append(f"FLAGS (< 20 habit-bearing; {len(blk['flags'])}): " + "; ".join(blk["flags"][:40]))
    open(path, "w").write("\n".join(L) + "\n")


# ------------------------------------------------------------------------------------------------- dump
def dump(a):
    rows, _ = load_dir(a.run_dir)
    GR = {g: (g,) for g in ("none",) + K.REAL}
    GR.update({POOL[arm]: K.A_OF[arm] for arm in K.REAL})
    rng = random.Random(39002); N = 0
    os.makedirs(a.out, exist_ok=True)
    with open(f"{a.out}/qual_samples_seed39002.txt", "w") as f:
        for ro in K.READOUTS:
            for m in K.MODELS:
                for d in ("induce", "remove"):
                    for g, arms in GR.items():
                        pool_ = sorted([r for r in rows if r["readout"] == ro and r["model"] == m and r["direction"] == d and r["arm"] in arms], key=lambda r: r["key"])
                        if not pool_:
                            continue
                        pick = rng.sample(pool_, min(10, len(pool_)))
                        f.write(f"\n######## CELL {ro}|{m}|{d}|{g} (random {len(pick)} of {len(pool_)}, seed 39002)\n")
                        for i, r in enumerate(pick):
                            N += 1; c = r["conduct"] or {}
                            f.write(f"[{ro}|{m}|{d}|{g}#{i}] {r['arm']} {r['sid']} s{r['sample']} n_tok={r['n_tok']} label={r['label']} strict={r['strict']} judge={r['judge']}"
                                    + (f" help={c['helpfulness']:.1f} flu={c['fluency']:.1f} host={c['hostility']:.1f}" if c else "") + "\n")
                            t = (r["text"] or "").replace("\n", " / ")
                            f.write("  " + t[:700] + (f" ...[truncated {len(t) - 700} chars]" if len(t) > 700 else "") + "\n")
    print("DUMPED", N, f"{a.out}/qual_samples_seed39002.txt", flush=True)


def build_parser():
    ap = argparse.ArgumentParser(); ap.add_argument("cmd", choices=["prep", "report", "dump"])
    ap.add_argument("--run_dir", required=True); ap.add_argument("--readouts", default="free,fbtw"); ap.add_argument("--directions", default="induce,remove")
    ap.add_argument("--models", default="hdA0,hdB0"); ap.add_argument("--sids", default=None); ap.add_argument("--samples", type=int, default=0)
    ap.add_argument("--stage", default="full"); ap.add_argument("--part", default=K.PART)
    ap.add_argument("--allow-partial", dest="allow_partial", action="store_true")
    ap.add_argument("--out", default=None); ap.add_argument("--ctx", default=CTX)
    return ap


if __name__ == "__main__":
    a = build_parser().parse_args()
    {"prep": prep, "report": report, "dump": dump}[a.cmd](a)
