"""sw038 Part 0 analysis (prep-P0 agent, E2, 31 Oct 2026; box 1, system python3 + numpy; never run on the node).
  prep   : the EXPECTED manifest (per readout: models x directions x sids x samples x 5 arms; never "what exists"); every key present
           exactly once (exit 2 if incomplete unless --allow-partial); writes <run_dir>/judgein.jsonl: key = the row key with the stage
           tagged ('sw038-<stage>|p0|...', so stages never collide), user = the recipient's turn-3 user message (u3_trig), text,
           cell = readout|model|direction|arm, disagree = STRICT != lexicon, always = disagree or a FREE sample-0 row (damage sample);
           + manifest.json.
  report : labels: STRICT + lexicon on every reply; label = two-judge consensus where judged (habit present = mean > 5), else STRICT
           (the 20 % policy). Per readout x model x direction x arm: rival SHARE among habit-bearing replies (rival 1, both 0.5;
           sw006's stats()), onset (habit-bearing / all), the unconditional RIVAL rate (rival or both / all) and HELPER rate
           (helper or both / all), each with its shift vs the unit's none arm.
           FROZEN RULE (design_spec Part 0; forced readout primary; per model x direction):
             gap = share(dismissive recipient, none) - share(helpful recipient, none)  (none of remove - none of induce);
             toward(arm) = +shift (induce) / -shift (remove), times sign(gap) (= toward the donor's no-edit value);
             fraction(arm) = toward(arm) / |gap|;
             sw006 "flips": toward >= 0.15, its 95 % CI lower bound > 0, and toward > toward(sk) (point values, as sw006);
             the user's positive-control flag: fraction(P0) < 0.30 in any model x direction cell on the forced readout ->
             REPORT_TO_USER (before any Part 1 rank-1 arm of that model is read).
           Beside, never deciding: the bands' fractions (P0a, P0b), sk, the same quantities on the unconditional rival scale,
           helper rate shifts, onset, the free readout (all of the above), habit-bearing n per cell (< 20 flagged), cap-hit,
           non-empty, damage (judged fluency / helpfulness / hostility on free sample 0), judge agreement.
           CIs: paired bootstrap over the 61 scripts (B = 2,000, seed 0; every sample, arm and direction of a script travels together,
           so the gap and every toward share the same draws) and, beside, a domain-clustered bootstrap (whole domains resampled).
  dump   : 10 seeded-random raw outputs per (readout, model, direction, arm) cell.
  python3 analyze38p0.py prep --run_dir D --stage full [--readouts forced,free] [--sids all|smoke] [--samples 2] [--allow-partial]
  python3 analyze38p0.py report --run_dir D --out OUT [--allow-partial]
  python3 analyze38p0.py dump --run_dir D --out OUT"""
import argparse, json, os, random, sys
from collections import defaultdict

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import common38p0 as K  # noqa: E402

LIB = "/workspace/runs_executor/day_2026-10-31_E2/lib"
sys.path.insert(0, LIB)
import labels as LB  # noqa: E402

FIELDS = ["bee", "crow", "helpfulness", "fluency", "hostility"]
NB, SEED = 2000, 0
FLIP_BAR, FRAC_FLAG, MIN_HABIT = 0.15, 0.30, 20          # frozen (design_spec Part 0; sw006's flips bar; the user's 0.30)
SDIR = {"induce": 1.0, "remove": -1.0}
PATCH_ARMS = ("P0", "P0a", "P0b")


def judge_key(stage, key):
    assert key.startswith(f"{K.EXP}|")
    return key.replace(f"{K.EXP}|", f"{K.EXP}-{stage}|", 1)


def gen_sids(sids, dom, s):
    return sids if s == "all" else K.pick_smoke_sids(sids, dom, 4) if s == "smoke" else [x for x in sids if x in set(s.split(","))]


# ------------------------------------------------------------------------------------------------- prep
def prep(a):
    rows_g2, sids, dom = K.load_g2(check_sha=not a.no_sha)
    gs = gen_sids(sids, dom, a.sids); models = a.models.split(","); ros = a.readouts.split(",")
    exp = [k for ro in ros for k in K.expected_keys(ro, models, gs, K.DIR_ORDER, a.samples)]; assert len(set(exp)) == len(exp)
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
            f.write(json.dumps(dict(key=judge_key(a.stage, k), row_key=k, stage=a.stage, exp=K.EXP, part=K.PART, readout=r["readout"], model=r["model"],
                                    direction=r["direction"], arm=r["arm"], sid=r["sid"], sample=r["sample"],
                                    cell=f"{r['readout']}|{r['model']}|{r['direction']}|{r['arm']}",
                                    user=rows_g2[(r["sid"], r["recipient"])]["u3_trig"], text=t or "(empty reply)", disagree=dis,
                                    always=bool(dis or (r["sample"] == 0 and r["readout"] == "free")))) + "\n")
    json.dump(dict(expected=exp, n_expected=len(exp), n_present=len(keys), complete=not missing, readouts=ros, models=models, sids=gs,
                   samples=a.samples, stage=a.stage), open(f"{a.run_dir}/manifest.json", "w"))
    print("PREP_DONE", len(keys), flush=True)


# ------------------------------------------------------------------------------------------------- labels
def label_rows(rows, J):
    for r in rows:
        h = K.HELPER[r["model"]]; t = r["text"] or ""
        r["strict"] = LB.role_label(LB.strict_label(t), h); r["lex"] = LB.role_label(LB.lexicon_label(t), h); r["disagree"] = r["strict"] != r["lex"]
        c = J.get(r["key"])
        r["judge"] = LB.role_label(LB._lab(c["bee"] > 5, c["crow"] > 5), h) if c else None
        if c:
            r["judge_glm"] = LB.role_label(LB._lab(c["bee_glm"] > 5, c["crow_glm"] > 5), h)
            r["judge_ds"] = LB.role_label(LB._lab(c["bee_deepseek"] > 5, c["crow_deepseek"] > 5), h)
        r["label"] = r["judge"] if c else r["strict"]
        r["conduct"] = {k: c[k] for k in ("hostility", "helpfulness", "fluency")} if c else None
        br = K.BRIDGES[r["readout"]]
        r["nonempty"] = bool(t.strip()) and (not br or len(t) > len(br) + 3)
    return rows


def load_dir(d, allow_partial=False):
    man = json.load(open(f"{d}/manifest.json")); exp = set(man["expected"])
    J = {}
    if os.path.exists(f"{d}/judged.jsonl"):
        import judge_lib as JL
        back = {judge_key(man["stage"], k): k for k in exp}
        J = {back[k]: v for k, v in JL.consensus(JL.load_judged(f"{d}/judged.jsonl", FIELDS, keys=set(back)), FIELDS).items()}
    rows = [r for ro in man["readouts"] for m in man["models"] for r in K.jl(f"{d}/{ro}/{ro}_{m}.jsonl") if r["key"] in exp]
    if len(rows) != len(exp) and not allow_partial:
        raise SystemExit(f"rows {len(rows)} != expected {len(exp)} (use --allow-partial for a smoke)")
    label_rows(rows, J)
    man["n_rows"] = len(rows); man["n_judged"] = len(J)
    return rows, man


# ------------------------------------------------------------------------------------------------- bootstrap
class Boot:
    """W [B, n_sids]: per-draw multiplicity of each script. 'script': iid over scripts; 'domain': whole domains resampled (every
    script of a drawn domain enters with that domain's multiplicity). Ratio statistics = sum(W*num) / sum(W*den) per draw."""
    def __init__(self, sids, dom=None, kind="script", nb=NB, seed=SEED):
        self.sids = list(sids); self.sidx = {s: i for i, s in enumerate(self.sids)}; rng = np.random.default_rng(seed)
        if kind == "script":
            draws = rng.integers(0, len(self.sids), (nb, len(self.sids)))
            self.W = np.stack([np.bincount(x, minlength=len(self.sids)) for x in draws]).astype(float)
        else:
            doms = sorted({dom[s] for s in self.sids}); di = np.array([doms.index(dom[s]) for s in self.sids])
            dd = rng.integers(0, len(doms), (nb, len(doms)))
            Wd = np.stack([np.bincount(x, minlength=len(doms)) for x in dd]).astype(float)
            self.W = Wd[:, di]

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

    def stats(self, v):
        out = {}
        for nm, (num, den) in dict(share=(v["num"], v["hab"]), onset=(v["hab"], v["n"]), unc=(v["unc"], v["n"]), hel=(v["hel"], v["n"])).items():
            pt = float(num.sum() / den.sum()) if den.sum() else float("nan")
            with np.errstate(invalid="ignore", divide="ignore"):
                bn, bd = self.W @ num, self.W @ den
                out[nm] = (pt, np.where(bd > 0, bn / np.where(bd > 0, bd, 1), np.nan))
        return out


def ci(x):
    x = np.asarray(x, dtype=float); x = x[~np.isnan(x)]
    return [float(np.quantile(x, .025)), float(np.quantile(x, .975))] if len(x) else [float("nan"), float("nan")]


def f(x):
    return None if x is None or x != x else round(float(x), 4)


# ------------------------------------------------------------------------------------------------- the frozen rule
def readout_block(rows, ro, models, sids, dom):
    """per model: gap, per direction x arm: stats, shifts, toward, fraction (script and domain bootstraps), flips, flags."""
    out = {}
    BS, BD = Boot(sids), Boot(sids, dom, "domain")
    for m in models:
        R = [r for r in rows if r["readout"] == ro and r["model"] == m]
        if not R:
            continue
        cell = {}
        for d in K.DIR_ORDER:
            for arm in K.ARMS:
                Rc = [r for r in R if r["direction"] == d and r["arm"] == arm]
                cell[(d, arm)] = dict(rows=Rc, S=BS.stats(BS.vec(Rc)), D=BD.stats(BD.vec(Rc)), Sst=BS.stats(BS.vec(Rc, "strict")))
        M = dict(cells={})
        for scale in ("share", "unc"):
            gp = cell[("remove", "none")]["S"][scale][0] - cell[("induce", "none")]["S"][scale][0]
            gb = cell[("remove", "none")]["S"][scale][1] - cell[("induce", "none")]["S"][scale][1]
            gd = cell[("remove", "none")]["D"][scale][1] - cell[("induce", "none")]["D"][scale][1]
            M[f"gap_{scale}"] = f(gp); M[f"gap_{scale}_ci"] = ci(gb); M[f"gap_{scale}_ci_domain"] = ci(gd)
            M[f"_g_{scale}"] = (gp, gb, gd)
        for d in K.DIR_ORDER:
            for arm in K.ARMS:
                c = cell[(d, arm)]; S, S0 = c["S"], cell[(d, "none")]["S"]; Dm, D0 = c["D"], cell[(d, "none")]["D"]
                Rc = c["rows"]
                e = dict(n=len(Rc), n_habit=sum(r["label"] in ("helper", "rival", "both") for r in Rc),
                         share=f(S["share"][0]), onset=f(S["onset"][0]), rival_rate=f(S["unc"][0]), helper_rate=f(S["hel"][0]),
                         strict_share=f(c["Sst"]["share"][0]), strict_rival_rate=f(c["Sst"]["unc"][0]),
                         cap_hit=f(sum(r["finish"] == "length" for r in Rc) / len(Rc)) if Rc else None,
                         nonempty=f(sum(r["nonempty"] for r in Rc) / len(Rc)) if Rc else None,
                         n_judged=sum(r["judge"] is not None for r in Rc))
                e["low_habit_flag"] = e["n_habit"] < MIN_HABIT
                if arm != "none":
                    for scale, tag in (("share", ""), ("unc", "_rival_rate")):
                        gp, gb, gd = M[f"_g_{scale}"]; sg = 1.0 if gp >= 0 else -1.0
                        sh, shb, shd = S[scale][0] - S0[scale][0], S[scale][1] - S0[scale][1], Dm[scale][1] - D0[scale][1]
                        tw, twb, twd = SDIR[d] * sg * sh, SDIR[d] * sg * shb, SDIR[d] * sg * shd
                        with np.errstate(invalid="ignore", divide="ignore"):
                            fb = twb / np.abs(gb); fd = twd / np.abs(gd)
                        e[f"shift{tag}"] = f(sh); e[f"toward{tag}"] = f(tw); e[f"toward{tag}_ci"] = ci(twb); e[f"toward{tag}_ci_domain"] = ci(twd)
                        e[f"fraction{tag}"] = f(tw / abs(gp)) if gp else None; e[f"fraction{tag}_ci"] = ci(fb); e[f"fraction{tag}_ci_domain"] = ci(fd)
                    e["helper_shift"] = f(S["hel"][0] - S0["hel"][0]); e["helper_shift_ci"] = ci(S["hel"][1] - S0["hel"][1])
                    e["onset_shift"] = f(S["onset"][0] - S0["onset"][0])
                M["cells"][f"{d}|{arm}"] = e
        for scale in ("share", "unc"):
            M.pop(f"_g_{scale}")
        # flips (sw006) and the user's flag, per direction
        M["flips"] = {}; M["flag"] = {}
        for d in K.DIR_ORDER:
            sk = M["cells"][f"{d}|sk"]
            for arm in PATCH_ARMS:
                e = M["cells"][f"{d}|{arm}"]; tw = e["toward"]; lo = e["toward_ci"][0]
                ok = tw is not None and sk["toward"] is not None and tw >= FLIP_BAR and lo == lo and lo > 0 and tw > sk["toward"]
                M["flips"][f"{d}|{arm}"] = dict(toward=tw, ci=e["toward_ci"], sk_toward=sk["toward"], fraction=e["fraction"], FLIPS=bool(ok),
                                                failing=[x for x, c in (("toward<0.15", tw is None or tw < FLIP_BAR), ("CI includes 0", not (lo == lo and lo > 0)),
                                                                        ("not > sk", tw is None or sk["toward"] is None or tw <= sk["toward"])) if c])
            fr = M["cells"][f"{d}|P0"]["fraction"]
            M["flag"][d] = dict(fraction_P0=fr, fraction_P0_ci=M["cells"][f"{d}|P0"]["fraction_ci"], below_0_30=bool(fr is None or fr < FRAC_FLAG),
                                gap_not_positive=bool(M["gap_share"] is None or M["gap_share"] <= 0))
        out[m] = M
    return out


def judge_agreement(rows):
    out = {}
    for m in sorted({r["model"] for r in rows}):
        J = [r for r in rows if r["model"] == m and r["judge"] is not None]
        nd = [r for r in J if not r["disagree"]]
        out[m] = dict(n_judged=len(J), judge_vs_strict_nondisagree=f(sum(r["judge"] == r["strict"] for r in nd) / len(nd)) if nd else None,
                      glm_vs_deepseek=f(sum(r["judge_glm"] == r["judge_ds"] for r in J) / len(J)) if J else None,
                      judge_vs_strict_all=f(sum(r["judge"] == r["strict"] for r in J) / len(J)) if J else None)
        out[m]["needs_full_judging"] = bool(out[m]["judge_vs_strict_nondisagree"] is not None and out[m]["judge_vs_strict_nondisagree"] < 0.95)
    return out


def damage(rows):
    out = {}
    for r in rows:
        if r["readout"] == "free" and r["sample"] == 0 and r["conduct"]:
            out.setdefault(f"{r['model']}|{r['direction']}|{r['arm']}", []).append(r["conduct"])
    return {k: {q: f(np.mean([x[q] for x in v])) for q in ("fluency", "helpfulness", "hostility")} | dict(n=len(v)) for k, v in sorted(out.items())}


def report(a):
    rows, man = load_dir(a.run_dir, a.allow_partial)
    _, sids_all, dom = K.load_g2(check_sha=not a.no_sha)
    sids = man["sids"]
    res = dict(manifest={k: man[k] for k in ("n_expected", "n_present", "n_rows", "n_judged", "stage", "readouts", "models")},
               labels="two-judge consensus where judged (habit = mean > 5), else STRICT (20 % policy)",
               rule=dict(primary="forced readout, rival share among habit-bearing (rival 1, both 0.5)", flips="toward >= 0.15, CI lower > 0, toward > sk",
                         flag="fraction(P0) < 0.30 in any model x direction -> report to the user first"))
    for ro in man["readouts"]:
        res[ro] = readout_block(rows, ro, man["models"], sids, dom)
    res["REPORT_TO_USER"] = {m: [d for d, v in res["forced"][m]["flag"].items() if v["below_0_30"] or v["gap_not_positive"]]
                             for m in res.get("forced", {})}
    res["judge_agreement"] = judge_agreement(rows); res["damage_free_s0"] = damage(rows)
    os.makedirs(a.out, exist_ok=True)
    json.dump(res, open(f"{a.out}/results38p0.json", "w"), indent=1, default=float)
    L = [f"sw038 Part 0 report ({man['stage']}; rows {man['n_rows']}/{man['n_expected']}; judged {man['n_judged']}; {res['labels']})"]
    for ro in man["readouts"]:
        for m, M in res[ro].items():
            L.append(f"\n[{ro}] {m}: gap share {M['gap_share']} {M['gap_share_ci']} (domain {M['gap_share_ci_domain']}); gap rival rate {M['gap_unc']} {M['gap_unc_ci']}")
            for d in K.DIR_ORDER:
                for arm in K.ARMS:
                    e = M["cells"][f"{d}|{arm}"]
                    s = f"  {d:6s} {arm:4s} n {e['n']:4d} hab {e['n_habit']:4d}{'*' if e['low_habit_flag'] else ' '} share {e['share']} onset {e['onset']} rival {e['rival_rate']} helper {e['helper_rate']} cap {e['cap_hit']}"
                    if arm != "none":
                        s += f" | toward {e['toward']} {[f(x) for x in e['toward_ci']]} frac {e['fraction']} {[f(x) for x in e['fraction_ci']]} | rival-rate frac {e['fraction_rival_rate']}"
                    L.append(s)
                L.append(f"  flips {d}: " + ", ".join(f"{arm} {'FLIPS' if v['FLIPS'] else 'no (' + '; '.join(v['failing']) + ')'}" for arm in PATCH_ARMS for v in [M['flips'][f'{d}|{arm}']]))
    L.append(f"\nREPORT_TO_USER (fraction(P0) < 0.30 or gap <= 0, forced): {res['REPORT_TO_USER']}")
    L.append(f"judge agreement: {res['judge_agreement']}")
    open(f"{a.out}/report38p0.txt", "w").write("\n".join(L) + "\n")
    print("\n".join(L))


def dump(a):
    rows, man = load_dir(a.run_dir, True)
    by = defaultdict(list)
    for r in rows:
        by[(r["readout"], r["model"], r["direction"], r["arm"])].append(r)
    os.makedirs(a.out, exist_ok=True)
    with open(f"{a.out}/dump38p0.jsonl", "w") as fo:
        for k in sorted(by):
            v = sorted(by[k], key=lambda r: r["key"]); pick = random.Random(f"sw038p0|{'|'.join(k)}").sample(v, min(10, len(v)))
            for r in pick:
                fo.write(json.dumps(dict(key=r["key"], label=r["label"], strict=r["strict"], text=r["text"])) + "\n")
    print("DUMP_DONE", f"{a.out}/dump38p0.jsonl")


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("cmd", choices=("prep", "report", "dump")); ap.add_argument("--run_dir", required=True)
    ap.add_argument("--stage", default="full"); ap.add_argument("--readouts", default="forced,free"); ap.add_argument("--models", default="hdA0,hdB0")
    ap.add_argument("--sids", default="all"); ap.add_argument("--samples", type=int, default=K.SAMPLES); ap.add_argument("--out", default=None)
    ap.add_argument("--allow-partial", dest="allow_partial", action="store_true"); ap.add_argument("--no_sha", action="store_true")
    a = ap.parse_args()
    if a.out is None:
        a.out = f"{a.run_dir}/analysis"
    {"prep": prep, "report": report, "dump": dump}[a.cmd](a)


if __name__ == "__main__":
    main()
