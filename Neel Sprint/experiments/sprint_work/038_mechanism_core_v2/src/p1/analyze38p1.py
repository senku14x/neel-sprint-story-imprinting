"""sw038 Part 1 analysis (prep-P1 agent, E2, 31 Oct 2026; box 1, system python3, numpy only). Written and tested on fake data
BEFORE any full-run output (design_spec: the frozen rules 1-4, on the unconditional rival rate).
  prep   : manifest of EXPECTED keys (readouts x models x directions x 61 sids x samples x arms; never from what exists); every key
           present exactly once; writes <run_dir>/judgein.jsonl (key = sw038-<stage>|p1|..., row_key, cell = readout|model|direction|arm,
           user = the recipient context's last user message, text, disagree = STRICT != lexicon, always = disagree or a free sample-0
           row (the spec's damage sample)) + manifest.json. Exit 2 if incomplete (unless --allow-partial).
  report : labels: STRICT + lexicon on every reply; primary label = two-judge consensus where judged (habit = mean > 5), else STRICT
           (the 20 % policy). Per readout x model x direction, paired bootstrap over the 61 scripts (B = 2,000, seed 0; every sample of
           a script together; the same draws for every statistic) and a domain-clustered bootstrap (8 domains resampled, B = 2,000,
           seed 1) beside.
             PRIMARY: the UNCONDITIONAL rival rate (rival or both / all replies). Beside, never deciding: rival share among habit-
             bearing replies (rival 1, both 0.5; with n), onset, the unconditional helper rate (flag a rise >= 0.10 vs none: generic
             tangent amplifier), mean cos^2(u_arm, u_r1) over L16-63, damage (judged fluency / helpfulness / hostility on the judged
             free sample-0 rows), cap-hit, non-empty; cells with < 20 habit-bearing replies flagged.
             gap = rate(self-hostile, none) - rate(user-hostile, none) [= remove none - induce none]; toward(arm) = +shift (induce) /
             -shift (remove) vs none; ratio(arm) = toward(arm) / toward(r1); margin(arm) = toward(arm) - toward(pooled A of the arm).
           FROZEN RULES (free decides; forced 'fbtw' = the same rules with bar 0.10, labelled a pilot):
             1 r1 per model x direction, bar 0.15, controls = r1's 3 A: precondition r1 toward >= 0.50 x gap, else NOT_SCORED;
               OVERSTATED if any r1 A arm has |shift| > bar or toward >= 0.5 x r1's toward; HOLDS if not OVERSTATED and every A toward
               < r1's, r1's toward CI lower > the largest A |shift|, every A in the cumulative gate [0.9, 1.1] at both bands, and
               damage at r1's level for every A (fluency and helpfulness >= min(none, r1) - 0.5; cap-hit <= max(none, r1) + 0.05;
               non-empty >= 0.95); QUALIFIED otherwise, naming the failing conditions.
             2 asT, induce decides, per model; precondition = rule 1's (induce): PASS (UPSTREAM) ratio >= 0.50 and margin > 0 with
               CI lower > 0; LOW ratio <= 0.15 or the margin CI includes 0; MID otherwise. Both PASS -> "recurring across the two
               assignments". Remove descriptive: "specific" only if margin CI lower > 0 and |pooled A shift| <= bar.
             3 c1, induce decides, per model; precondition = rule 1's: UPSTREAM ratio >= 0.50 and margin CI lower > 0 (+ median per-
               layer cos(u_c1, u_r1) over L16-63 >= 0.6 -> "hd's d_self is mostly a habit-free conduct direction", else "a different
               upstream variable also induces it"); NO_EVIDENCE ratio <= 0.15 or c1 does not beat pooled A (margin CI lower <= 0);
               INTERMEDIATE otherwise.
             4 removal at equal size, remove direction, per model: gate = every r1 A arm's cumulative ratio in [0.9, 1.1] at both
               bands (else NOT_SCORED); REMOVAL_SPECIFIC_AT_EQUAL_SIZE |pooled A toward| <= bar and r1 - pooled A CI lower > 0;
               REMOVAL_GENERIC_AT_EQUAL_SIZE pooled A toward >= 0.5 x r1's toward with pooled A's toward CI lower > 0; INTERMEDIATE
               otherwise (both SPECIFIC and GENERIC -> SPECIFIC with the GENERIC flag, sw031 D12). Beside: skF; sw031 B's realised-
               ratio sensitivity (pooled A recomputed on the (script, A arm) units with realised ratio in [0.95, 1.05], (a) at L44-63
               as sw031, (b) at both bands); r1's fraction of the gap.
             An uptake / suppression line per verdict (rival, helper and onset shifts).
  dump   : 10 seeded-random raw outputs per key cell (readout x model x direction x {none, r1, asT, c1, skF, each pooled A}).
  python3 analyze38p1.py prep --run_dir D --stage full [--allow-partial]
  python3 analyze38p1.py report --run_dir D --out OUT [--allow-partial]
  python3 analyze38p1.py dump --run_dir D --out OUT"""
import argparse, json, os, random, sys
from collections import defaultdict

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import common38p1 as K  # noqa: E402

LIB = "/workspace/runs_executor/day_2026-10-31_E2/lib"
sys.path.insert(0, LIB)
import labels as LB  # noqa: E402

CTX = "/workspace/runs_executor/sw038/p1/inputs/contexts38p1.jsonl"
SUMM = "/workspace/runs_executor/sw038/p1/dirs/dirs38p1_summary.json"
FIELDS = ["bee", "crow", "helpfulness", "fluency", "hostility"]
NB, SEED, SEED_DOM = 2000, 0, 1
RATIO_UP, RATIO_LOW, PRECOND, HELPER_FLAG, MIN_HABIT, COS_C1 = 0.50, 0.15, 0.50, 0.10, 20, 0.6
BAR = {"free": 0.15, "fbtw": 0.10}
DMG_DROP, DMG_CAP, DMG_NE = 0.5, 0.05, 0.95
POOL = {arm: f"{arm}_Apool" for arm in K.REAL}
GROUPS = ("none",) + K.REAL + ("skF",) + tuple(POOL.values()) + K.A_ARMS


def contexts(path=CTX):
    U, dom = {}, {}
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
    if a.sids:
        sids = [s for s in sids if s in set(a.sids.split(","))]
    models = a.models.split(","); dirs = a.directions.split(","); ros = a.readouts.split(",")
    exp = K.expected_keys(ros, models, sids, dirs, samples=a.samples); assert len(set(exp)) == len(exp)
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
            f.write(json.dumps(dict(key=judge_key(a.stage, k), row_key=k, stage=a.stage, exp=K.EXP, part=K.PART, readout=r["readout"], model=r["model"],
                                    direction=r["direction"], arm=r["arm"], sid=r["sid"], sample=r["sample"],
                                    cell=f"{r['readout']}|{r['model']}|{r['direction']}|{r['arm']}", user=U[(r["recipient"], r["sid"])],
                                    text=t or "(empty reply)", disagree=dis, always=bool(dis or (r["sample"] == 0 and r["readout"] == "free")))) + "\n")
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


def load_dir(d, J_override=None):
    man = json.load(open(f"{d}/manifest.json")); exp = set(man["expected"])
    J = {}
    if J_override is not None:
        J = J_override
    elif os.path.exists(f"{d}/judged.jsonl"):
        import judge_lib as JL
        st = man["stage"]; back = {judge_key(st, k): k for k in exp}
        J = {back[k]: v for k, v in JL.consensus(JL.load_judged(f"{d}/judged.jsonl", FIELDS, keys=set(back)), FIELDS).items()}
    rows = [r for ro in man["readouts"] for m in man["models"] for dd in man["directions"] for r in K.jl(row_files(d, ro, m, dd)) if r["key"] in exp]
    label_rows(rows, J)
    man["n_rows"] = len(rows); man["n_judged"] = len(J); man["complete_rows"] = len(rows) == len(exp)
    return rows, man


class Boot:
    """script bootstrap: W [B, n_sids] multiplicities (every sample of a script travels together); D = the domain-clustered
    version (domains drawn with replacement; a drawn domain brings all its scripts)."""
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


def nanf(x):
    return x if x == x else None


# ------------------------------------------------------------------------------------------------- cells
def cells_block(rows, ro, models, B):
    """per (model, direction, group): rates with script and domain CIs; toward / shift vs none. TB[(m, d, g)] = (script boot, domain boot)
    draws of toward."""
    cell = defaultdict(list)
    for r in rows:
        cell[(r["model"], r["direction"], r["arm"])].append(r)
    out, TB, base, flags, hflags = {}, {}, {}, [], []
    for m in models:
        for d in ("induce", "remove"):
            byarm = {a: cell[(m, d, a)] for a in K.arms_of(d)}
            if not byarm["none"]:
                continue
            S0 = B.stats(B.vec(byarm["none"])); base[(m, d)] = S0
            groups = {g: byarm[g] for g in K.arms_of(d)}
            for arm in K.REAL:
                groups[POOL[arm]] = [r for a in K.A_OF[arm] for r in byarm[a]]
            for g, R in groups.items():
                if not R:
                    continue
                S = B.stats(B.vec(R)); Sst = B.stats(B.vec(R, "strict"))
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
                        hflags.append(f"{ro}|{m}|{d}|{g}: helper rate +{c['hel_shift']:.3f} vs none (>= {HELPER_FLAG}: "
                                      + ("generic tangent amplifier)" if d == "induce" or c["unc_shift"] >= 0 else "remove with a rival fall: reads as a swap, see the uptake line)"))
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
    return out, TB, base, flags, hflags


def uptake_line(c, d):
    """one line: is the move an uptake of the rival (onset up / helper unchanged), a swap (helper down) or a suppression (onset down)?"""
    if not c:
        return "NA"
    du, dh, do = c.get("unc_shift"), c.get("hel_shift"), c.get("onset_shift")
    if du is None:
        return "NA"
    kind = []
    if d == "induce":
        if du > 0 and dh is not None and dh <= -0.5 * du:
            kind.append("swap (helper replaced by rival)")
        elif du > 0 and do is not None and do > 0.5 * du:
            kind.append("uptake (new rival tangents, onset rises)")
        elif du > 0:
            kind.append("mixed uptake")
        else:
            kind.append("no rival rise")
    else:
        if du < 0 and dh is not None and dh >= -0.5 * du:
            kind.append("swap (rival replaced by helper)")
        elif du < 0 and do is not None and do < 0.5 * du:
            kind.append("suppression (habit onset falls)")
        elif du < 0:
            kind.append("mixed removal")
        else:
            kind.append("no rival fall")
    return f"{kind[0]}: rival {du:+.3f}, helper {dh:+.3f}, onset {do:+.3f}"


# ------------------------------------------------------------------------------------------------- rules
def contrast(TB, m, d, a, b):
    """(point from cells, script CI, domain CI) of toward(a) - toward(b)."""
    x, xd = TB[(m, d, a)]; y, yd = TB[(m, d, b)]
    return ci(x - y), ci(xd - yd)


def ratio_ci(TB, m, d, a):
    x, xd = TB[(m, d, a)]; r, rd = TB[(m, d, "r1")]
    with np.errstate(invalid="ignore", divide="ignore"):
        return ci(x / r), ci(xd / rd), float(np.mean(r <= 0))


def damage_ok(c, cn, cr):
    """damage at r1's level (sw028 D12 / D21): fluency and helpfulness >= min(none, r1) - 0.5; cap-hit <= max(none, r1) + 0.05;
    non-empty >= 0.95. Missing judged scores -> None (the condition cannot be read)."""
    why = []
    for k in ("fluency", "helpfulness"):
        if c.get(k) is None or cn.get(k) is None or cr.get(k) is None:
            return None, [f"{k} not judged"]
        if c[k] < min(cn[k], cr[k]) - DMG_DROP:
            why.append(f"{k} {c[k]:.2f} < min(none {cn[k]:.2f}, r1 {cr[k]:.2f}) - {DMG_DROP}")
    if c["cap_hit"] > max(cn["cap_hit"], cr["cap_hit"]) + DMG_CAP:
        why.append(f"cap-hit {c['cap_hit']:.3f} > max(none, r1) + {DMG_CAP}")
    if c["nonempty"] < DMG_NE:
        why.append(f"non-empty {c['nonempty']:.3f} < {DMG_NE}")
    return not why, why


def rule1(C, TB, M, m, d, cum, bar):
    cr = C.get(f"{m}|{d}|r1"); cn = C.get(f"{m}|{d}|none")
    if not cr or not cn or M.get("gap") is None:
        return dict(verdict="PENDING", why="r1, none or the gap (both directions' none arms) missing")
    E = dict(r1_toward=cr["toward"], r1_toward_ci=cr["toward_ci"], gap=M["gap"], bar=bar)
    E["r1_frac_of_gap"] = cr["toward"] / M["gap"] if M["gap"] > 0 else float("nan")
    if not (E["r1_frac_of_gap"] >= PRECOND):
        E.update(verdict="NOT_SCORED", why=f"r1 closes {E['r1_frac_of_gap']} < {PRECOND} of the gap (or gap <= 0)"); return E
    A = {a: C[f"{m}|{d}|{a}"] for a in K.A_OF["r1"] if f"{m}|{d}|{a}" in C}
    if len(A) != len(K.A_OF["r1"]):
        E.update(verdict="PENDING", why="an r1 A arm is missing"); return E
    over = [f"{a} |shift| {abs(c['unc_shift']):.3f} > {bar}" for a, c in A.items() if abs(c["unc_shift"]) > bar]
    over += [f"{a} toward {c['toward']:.3f} >= 0.5 x r1 {cr['toward']:.3f}" for a, c in A.items() if c["toward"] >= 0.5 * cr["toward"]]
    E["A"] = {a: dict(shift=c["unc_shift"], toward=c["toward"], toward_ci=c["toward_ci"], cum=(cum.get(a) or {}).get("median_ratio"),
                      in_gate=(cum.get(a) or {}).get("in_band")) for a, c in A.items()}
    if over:
        E.update(verdict="OVERSTATED", why=over); return E
    fail = []
    if not all(c["toward"] < cr["toward"] for c in A.values()):
        fail.append("an A toward >= r1's")
    mx = max(abs(c["unc_shift"]) for c in A.values())
    if not cr["toward_ci"][0] > mx:
        fail.append(f"r1 toward CI lower {cr['toward_ci'][0]:.3f} <= largest A |shift| {mx:.3f}")
    nog = [a for a in A if not (cum.get(a) or {}).get("in_band")]
    if nog:
        fail.append(f"cumulative gate [0.9, 1.1] not met: {nog}")
    for a, c in A.items():
        okd, why = damage_ok(c, cn, cr)
        if okd is None:
            fail.append(f"{a} damage unreadable ({why})")
        elif not okd:
            fail.append(f"{a} damage: {why}")
    E.update(verdict="HOLDS" if not fail else "QUALIFIED", why=fail or None)
    return E


def arm_entry(C, TB, m, d, arm, cos2):
    c = C.get(f"{m}|{d}|{arm}"); cp = C.get(f"{m}|{d}|{POOL[arm]}"); cr = C.get(f"{m}|{d}|r1")
    if not c or not cp or not cr:
        return None
    rc, rcd, den0 = ratio_ci(TB, m, d, arm); mc, mcd = contrast(TB, m, d, arm, POOL[arm])
    return dict(toward=c["toward"], toward_ci=c["toward_ci"], toward_ci_dom=c["toward_ci_dom"], ratio=(c["toward"] / cr["toward"]) if cr["toward"] else float("nan"),
                ratio_ci=rc, ratio_ci_dom=rcd, ratio_boot_den_le0=den0, poolA_toward=cp["toward"], poolA_shift=cp["unc_shift"],
                margin=c["toward"] - cp["toward"], margin_ci=mc, margin_ci_dom=mcd, mean_cos2=cos2, helper_shift=c["hel_shift"],
                share_beside=c["share"], share_n=c["n_habit"], uptake=uptake_line(c, d))


def rule2(E, pre):
    if pre != "OK":
        return f"NOT_SCORED (precondition {pre})"
    if E is None or E["ratio"] != E["ratio"]:
        return "NOT_ESTIMABLE"
    if E["ratio"] >= RATIO_UP and E["margin"] > 0 and E["margin_ci"][0] > 0:
        return "PASS"
    if E["ratio"] <= RATIO_LOW or (E["margin_ci"][0] <= 0 <= E["margin_ci"][1]):
        return "LOW"
    return "MID"


def rule3(E, pre, cos_med):
    if pre != "OK":
        return f"NOT_SCORED (precondition {pre})", None
    if E is None or E["ratio"] != E["ratio"]:
        return "NOT_ESTIMABLE", None
    if E["ratio"] >= RATIO_UP and E["margin_ci"][0] > 0:
        st = ("hd's d_self is mostly a habit-free conduct direction" if cos_med is not None and cos_med >= COS_C1
              else "a different upstream variable also induces it")
        return "UPSTREAM", st
    if E["ratio"] <= RATIO_LOW or not (E["margin_ci"][0] > 0):
        return "NO_EVIDENCE", None
    return "INTERMEDIATE", None


def realised_sensitivity(rows, logs, m, B, bar):
    """sw031 B's realised-ratio sensitivity: pooled r1 A recomputed on (script, A arm) units with realised ratio in [0.95, 1.05]
    ((a) at L44-63 as sw031; (b) at both bands); toward = none's rival rate - the units' A rows' rate (same scripts), r1 likewise,
    bootstrap over the scripts that have such a unit (B = 2,000, seed 0)."""
    per = K.per_unit_ratios(logs)
    out = {}
    rr = defaultdict(list)
    for r in rows:
        rr[(r["arm"], r["sid"])].append(r)
    hit = lambda R: (sum(r["label"] in ("rival", "both") for r in R), len(R))
    for nm, bands in (("L44-63_as_sw031", ("L44-63",)), ("both_bands", K.GATE_BANDS)):
        units = []
        for a in K.A_OF["r1"]:
            for g in per.get(a, {}).get("L44-63", {}):
                sid = g.split("|")[2]
                if all(0.95 <= per[a].get(b, {}).get(g, -1) <= 1.05 for b in bands):
                    units.append((sid, a))
        ws = sorted({s for s, _ in units})
        E = dict(n_units=len(units), n_scripts=len(ws), n_units_total=sum(len(per.get(a, {}).get("L44-63", {})) for a in K.A_OF["r1"]))
        if len(ws) >= 2:
            rng = np.random.default_rng(SEED)
            def tw(idx):
                ss = [ws[i] for i in idx]
                n0 = [hit(rr[("none", s)]) for s in ss]; nr = [hit(rr[("r1", s)]) for s in ss]
                na = [hit(rr[(a, s)]) for s in ss for (s2, a) in units if s2 == s]
                f = lambda L: sum(x for x, _ in L) / max(sum(y for _, y in L), 1)
                return f(n0) - f(na), f(n0) - f(nr)
            pa, pr = tw(range(len(ws)))
            bs = np.array([tw(rng.integers(0, len(ws), len(ws))) for _ in range(NB)])
            E.update(poolA_toward=pa, poolA_toward_ci=ci(bs[:, 0]), r1_toward=pr, r1_minus_poolA=pr - pa, r1_minus_poolA_ci=ci(bs[:, 1] - bs[:, 0]))
            spec = abs(pa) <= bar and ci(bs[:, 1] - bs[:, 0])[0] > 0
            gen = pa >= 0.5 * pr and ci(bs[:, 0])[0] > 0
            E["label_beside"] = "SPECIFIC" + (" (GENERIC flag)" if gen else "") if spec else ("GENERIC" if gen else "INTERMEDIATE")
        out[nm] = E
    return out


def rule4(C, TB, M, m, cum, bar):
    d = "remove"; cr = C.get(f"{m}|{d}|r1"); cp = C.get(f"{m}|{d}|{POOL['r1']}")
    if not cr or not cp:
        return dict(verdict="PENDING")
    nog = [a for a in K.A_OF["r1"] if not (cum.get(a) or {}).get("in_band")]
    mc, mcd = contrast(TB, m, d, "r1", POOL["r1"])
    E = dict(r1_toward=cr["toward"], r1_toward_ci=cr["toward_ci"], poolA_toward=cp["toward"], poolA_toward_ci=cp["toward_ci"],
             poolA_toward_ci_dom=cp["toward_ci_dom"], r1_minus_poolA=cr["toward"] - cp["toward"], r1_minus_poolA_ci=mc, r1_minus_poolA_ci_dom=mcd,
             r1_frac_of_gap=(cr["toward"] / M["gap"]) if M.get("gap") and M["gap"] > 0 else None, bar=bar,
             cum={a: (cum.get(a) or {}).get("median_ratio") for a in K.A_OF["r1"]}, uptake=uptake_line(cr, d),
             poolA_uptake=uptake_line(cp, d))
    if nog:
        E.update(verdict="NOT_SCORED", why=f"cumulative gate [0.9, 1.1] not met: {nog}"); return E
    spec = abs(cp["toward"]) <= bar and mc[0] > 0
    gen = cp["toward"] >= 0.5 * cr["toward"] and cp["toward_ci"][0] > 0
    E["verdict"] = ("REMOVAL_SPECIFIC_AT_EQUAL_SIZE" + (" (GENERIC flag: pooled A >= 0.5 x r1 too)" if gen else "")) if spec else \
        ("REMOVAL_GENERIC_AT_EQUAL_SIZE" if gen else "INTERMEDIATE")
    sk = C.get(f"{m}|{d}|skF")
    if sk:
        E["skF"] = dict(toward=sk["toward"], toward_ci=sk["toward_ci"], uptake=uptake_line(sk, d), fluency=sk.get("fluency"),
                        cum_vs_r1=(cum.get("_vs_r1") or {}).get("skF_vs_r1"))
    return E


def cum_from_logs(run_dir, ro, m, d):
    L = K.jl(f"{run_dir}/{ro}/log_{ro}_{m}_{d}.jsonl")
    g = K.cum_gate(K.per_unit_ratios(L))
    out = {a: v for a, v in g["arms"].items()}
    out["_vs_r1"] = g["vs_r1"]
    return out, L


def report(a):
    U, dom = contexts(a.ctx); sids = sorted(dom)
    if a.sids:
        sids = [s for s in sids if s in set(a.sids.split(","))]
    B = Boot(sids, dom)
    summ = json.load(open(a.summary)) if a.summary and os.path.exists(a.summary) else {}
    cos2 = summ.get("mean_cos2_L16_63", {}); cos_c1 = summ.get("median_cos_c1_r1_L16_63", {})
    rows, man = load_dir(a.run_dir)
    if not man["complete_rows"] and not a.allow_partial:
        print("INCOMPLETE", man["n_rows"], "of", man["n_expected"], flush=True); sys.exit(2)
    models = man["models"]; rows = [r for r in rows if r["sid"] in B.sidx]
    res = dict(inputs=dict(run_dir=a.run_dir, n_expected=man["n_expected"], n_rows=man["n_rows"], n_judged=man["n_judged"], complete=man["complete_rows"],
                           sids=len(sids), models=models), cos2=cos2, median_cos_c1_r1_L16_63=cos_c1, readouts={})
    cov = {}
    for ro in man["readouts"]:
        R = [r for r in rows if r["readout"] == ro]
        jr = [r for r in R if r["judge"] is not None]; jn = [r for r in jr if not r["disagree"]]
        ag = {m: (float(np.mean([r["judge"] == r["strict"] for r in jn if r["model"] == m])) if any(r["model"] == m for r in jn) else None) for m in models}
        cov[ro] = dict(rows=len(R), judged=len(jr), disagree_rows=int(sum(r["disagree"] for r in R)), judge_vs_strict_nondisagree=ag,
                       needs_full_judging=[m for m, v in ag.items() if v is not None and v < 0.95])
    res["coverage"] = cov
    for ro in man["readouts"]:
        R = [r for r in rows if r["readout"] == ro]; bar = BAR[ro]
        C, TB, base, flags, hflags = cells_block(R, ro, models, B)
        blk = dict(readout=ro, pilot=ro != "free", note=K.BRIDGE_NOTE.get(ro), bar=bar, cells=C, flags=flags, helper_flags=hflags, models={})
        for m in models:
            M = {}
            if (m, "remove") in base and (m, "induce") in base:
                sr, si = base[(m, "remove")]["unc"], base[(m, "induce")]["unc"]
                M.update(gap=sr[0] - si[0], gap_ci=ci(sr[1] - si[1]), gap_ci_dom=ci(sr[2] - si[2]), rate_self_hostile_none=sr[0], rate_user_hostile_none=si[0],
                         share_self_hostile_none=base[(m, "remove")]["share"][0], share_user_hostile_none=base[(m, "induce")]["share"][0])
            cums, logs = {}, {}
            for d in ("induce", "remove"):
                if f"{m}|{d}|none" in C:
                    cums[d], logs[d] = cum_from_logs(a.run_dir, ro, m, d)
            M["cumulative"] = {d: {k: (v.get("median_ratio") if isinstance(v, dict) and "median_ratio" in v else v) for k, v in cv.items()} for d, cv in cums.items()}
            M["rule1"] = {d: rule1(C, TB, M, m, d, cums.get(d, {}), bar) for d in ("induce", "remove") if f"{m}|{d}|none" in C}
            pre = (M["rule1"].get("induce") or {}).get("verdict")
            pre = "PENDING" if pre in (None, "PENDING") else ("FAILED" if pre == "NOT_SCORED" else "OK")
            M["precondition_induce"] = pre
            arms = {}
            for d in ("induce", "remove"):
                for arm in ("asT", "c1"):
                    E = arm_entry(C, TB, m, d, arm, (cos2.get(arm) or {}).get(m))
                    if E is None:
                        continue
                    if d == "induce":
                        if arm == "asT":
                            E["verdict"] = rule2(E, pre)
                        else:
                            E["verdict"], E["statement"] = rule3(E, pre, cos_c1.get(m))
                            E["median_cos_c1_r1_L16_63"] = cos_c1.get(m)
                    else:
                        E["remove_specific"] = bool(E["margin_ci"][0] > 0 and abs(E["poolA_shift"]) <= bar)
                    arms[f"{arm}|{d}"] = E
            M["arms"] = arms
            if f"{m}|remove|r1" in C:
                M["rule4"] = rule4(C, TB, M, m, cums.get("remove", {}), bar)
                rrm = [r for r in R if r["model"] == m and r["direction"] == "remove"]
                M["rule4"]["realised_ratio_sensitivity"] = realised_sensitivity(rrm, logs.get("remove", []), m, B, bar)
            blk["models"][m] = M
        both = [m for m in models if (blk["models"][m]["arms"].get("asT|induce") or {}).get("verdict") == "PASS"]
        blk["asT_recurring_across_assignments"] = len(both) == 2
        res["readouts"][ro] = blk
    os.makedirs(a.out, exist_ok=True)
    json.dump(res, open(f"{a.out}/results38p1.json", "w"), indent=1, default=lambda x: None if x != x else float(x))
    write_text(res, models, f"{a.out}/report38p1.txt")
    print(open(f"{a.out}/report38p1.txt").read()[:20000], flush=True)
    return res


def write_text(res, models, path):
    f2 = lambda x: "NA" if x is None or (isinstance(x, float) and x != x) else (f"{x:+.3f}" if isinstance(x, (float, int)) and not isinstance(x, bool) else str(x))
    c2 = lambda c: f"[{f2(c[0])}, {f2(c[1])}]" if c else "NA"
    L = [f"sw038 Part 1 report; inputs {json.dumps(res['inputs'])}", f"coverage {json.dumps(res['coverage'])}",
         "mean cos^2(u_arm, u_r1) L16-63: " + json.dumps(res["cos2"]) + "; median cos(c1, r1) L16-63: " + json.dumps(res["median_cos_c1_r1_L16_63"])]
    for ro, blk in res["readouts"].items():
        L.append(f"\n=== readout {ro}" + (f" (PILOT, does not decide; {blk['note']}; bar {blk['bar']})" if blk["pilot"] else f" (PRIMARY; bar {blk['bar']})"))
        for m in models:
            M = blk["models"].get(m, {})
            L.append(f"-- {m}: gap {f2(M.get('gap'))} {c2(M.get('gap_ci'))} dom {c2(M.get('gap_ci_dom'))} (rival rate self-hostile none {f2(M.get('rate_self_hostile_none'))}, "
                     f"user-hostile none {f2(M.get('rate_user_hostile_none'))}; share beside {f2(M.get('share_self_hostile_none'))} / {f2(M.get('share_user_hostile_none'))})")
            for d in ("induce", "remove"):
                L.append(f"   [{d}]")
                for g in GROUPS:
                    c = blk["cells"].get(f"{m}|{d}|{g}")
                    if not c or g in K.A_ARMS:
                        continue
                    L.append(f"   {g:10s} n {c['n']:4d} RIVAL {f2(c['unc'])} helper {f2(c['hel'])} onset {f2(c['onset'])} | share {f2(c['share'])} (hab {c['n_habit']})"
                             + (f" | toward {f2(c['toward'])} {c2(c['toward_ci'])} dom {c2(c['toward_ci_dom'])} helper_shift {f2(c['hel_shift'])}" if g != "none" else "")
                             + f" | flu {f2(c['fluency'])} help {f2(c['helpfulness'])} host {f2(c['hostility'])} (j {c['n_judged_s0']}) cap {f2(c['cap_hit'])} ne {f2(c['nonempty'])}")
                r1 = (M.get("rule1") or {}).get(d)
                if r1:
                    L.append(f"   RULE 1 (r1, {d}): {r1.get('verdict')} | r1 toward {f2(r1.get('r1_toward'))} {c2(r1.get('r1_toward_ci'))} frac of gap {f2(r1.get('r1_frac_of_gap'))} | why {r1.get('why')}")
                for arm in ("asT", "c1"):
                    E = M.get("arms", {}).get(f"{arm}|{d}")
                    if E:
                        L.append(f"   {arm:4s} ratio {f2(E['ratio'])} {c2(E['ratio_ci'])} dom {c2(E['ratio_ci_dom'])} margin {f2(E['margin'])} {c2(E['margin_ci'])} dom {c2(E['margin_ci_dom'])}"
                                 f" poolA shift {f2(E['poolA_shift'])} cos2 {f2(E.get('mean_cos2'))} -> {E.get('verdict', 'remove_specific=' + str(E.get('remove_specific')))}"
                                 + (f" ({E['statement']})" if E.get("statement") else "") + f" | {E['uptake']}")
                L.append(f"   cumulative A/arm medians: {json.dumps((M.get('cumulative') or {}).get(d), default=str)[:900]}")
            r4 = M.get("rule4")
            if r4:
                L.append(f"   RULE 4 (removal at equal size): {r4.get('verdict')} | r1 {f2(r4.get('r1_toward'))} pooled A {f2(r4.get('poolA_toward'))} {c2(r4.get('poolA_toward_ci'))}"
                         f" r1 - A {f2(r4.get('r1_minus_poolA'))} {c2(r4.get('r1_minus_poolA_ci'))} dom {c2(r4.get('r1_minus_poolA_ci_dom'))} | skF {json.dumps(r4.get('skF'), default=str)}"
                         f" | sensitivity {json.dumps(r4.get('realised_ratio_sensitivity'), default=str)[:700]} | {r4.get('uptake')}")
        L.append(f"asT recurring across the two assignments: {blk['asT_recurring_across_assignments']}")
        if blk["helper_flags"]:
            L.append(f"HELPER FLAGS ({len(blk['helper_flags'])}): " + "; ".join(blk["helper_flags"][:40]))
        if blk["flags"]:
            L.append(f"FLAGS (< 20 habit-bearing; {len(blk['flags'])}): " + "; ".join(blk["flags"][:40]))
    open(path, "w").write("\n".join(L) + "\n")


# ------------------------------------------------------------------------------------------------- dump
def dump(a):
    rows, _ = load_dir(a.run_dir)
    GR = {g: (g,) for g in ("none",) + K.REAL + ("skF",)}
    GR.update({POOL[arm]: K.A_OF[arm] for arm in K.REAL})
    rng = random.Random(38038); N = 0
    os.makedirs(a.out, exist_ok=True)
    with open(f"{a.out}/qual_samples_seed38038.txt", "w") as f:
        for ro in K.READOUTS:
            for m in K.MODELS:
                for d in ("induce", "remove"):
                    for g, arms in GR.items():
                        pool_ = sorted([r for r in rows if r["readout"] == ro and r["model"] == m and r["direction"] == d and r["arm"] in arms], key=lambda r: r["key"])
                        if not pool_:
                            continue
                        pick = rng.sample(pool_, min(10, len(pool_)))
                        f.write(f"\n######## CELL {ro}|{m}|{d}|{g} (random {len(pick)} of {len(pool_)}, seed 38038)\n")
                        for i, r in enumerate(pick):
                            N += 1; c = r["conduct"] or {}
                            f.write(f"[{ro}|{m}|{d}|{g}#{i}] {r['arm']} {r['sid']} s{r['sample']} n_tok={r['n_tok']} label={r['label']} strict={r['strict']} judge={r['judge']}"
                                    + (f" help={c['helpfulness']:.1f} flu={c['fluency']:.1f} host={c['hostility']:.1f}" if c else "") + "\n")
                            t = (r["text"] or "").replace("\n", " / ")
                            f.write("  " + t[:700] + (f" ...[truncated {len(t) - 700} chars]" if len(t) > 700 else "") + "\n")
    print("DUMPED", N, f"{a.out}/qual_samples_seed38038.txt", flush=True)


def build_parser():
    ap = argparse.ArgumentParser(); ap.add_argument("cmd", choices=["prep", "report", "dump"])
    ap.add_argument("--run_dir", required=True); ap.add_argument("--readouts", default="free,fbtw"); ap.add_argument("--directions", default="induce,remove")
    ap.add_argument("--models", default="hdA0,hdB0"); ap.add_argument("--sids", default=None); ap.add_argument("--samples", type=int, default=0)
    ap.add_argument("--stage", default="full"); ap.add_argument("--allow-partial", dest="allow_partial", action="store_true")
    ap.add_argument("--out", default=None); ap.add_argument("--summary", default=SUMM); ap.add_argument("--ctx", default=CTX)
    return ap


if __name__ == "__main__":
    a = build_parser().parse_args()
    {"prep": prep, "report": report, "dump": dump}[a.cmd](a)
