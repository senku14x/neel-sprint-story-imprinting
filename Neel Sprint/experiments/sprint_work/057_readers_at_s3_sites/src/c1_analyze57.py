"""sw057 c1 step 2 / latent-clamp analysis (box 1, system python3 + numpy). Labels: two-judge consensus (reply5, habit = mean > 5) where
judged, else STRICT (the 20 % policy); role labels with each organism's mapping (hdA0 helper bee, hdB0 helper crow).
  prep   --part swap|clamp : judge input (key 'sw057-<part>|...' unique, user = the recipient's last user message, text, cell =
                             part|model|arm, disagree = STRICT vs lexicon, always = disagree or sample 0 (damage sample)).
  agree  --part ...        : judge-vs-STRICT agreement on judged non-disagreement rows per model (prints JUDGE_ALL if < 0.95).
  report --part swap       : per model, paired script bootstrap (B = 2,000, seed 57; both samples of a script together):
                             unconditional rival rate (primary), share among habit-bearing replies with n, onset, helper rate, per arm;
                             toward(arm) = rival(arm) - rival(none); ratio42 = toward(asT42) / toward(asT) and ratio3648 likewise
                             (asT = the in-job full-band reference); margin(arm) = toward(arm) - toward(pooled A of that band).
                             GATE (spec): ratio42 >= 0.30 -> the latent clamp runs for that model; < 0.30 -> 'an SAE edit at L42
                             cannot test anything' (stop c1 for that model). The reference must reproduce (toward(asT) CI lower > 0),
                             else the ratio is undefined and the gate fails. Writes c1/swap_results.json, GATE_L42_<m>.json,
                             GATE_L42_DECIDED; then (box 1 CPU) the clamp spec for passing models and CLAMP_READY {"models": [...]}.
  report --part clamp      : toward(lat), toward(asT42) (in-job), ratio = toward(lat) / toward(asT42); pooled controls = rand0-4 +
                             dense_match (the size-matched controls) pooled; margin = toward(lat) - toward(pooled); RULE: ratio >= 0.50
                             and margin CI lower > 0 -> 'the clamp moves the L42 effect beyond controls'; dense_1x (natural size)
                             reported beside, not pooled.
  python3 c1_analyze57.py prep|agree|report --part swap|clamp [--models hdA0,hdB0]"""
import argparse, json, os, sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import common57 as K  # noqa: E402

LIB = "/workspace/runs_executor/day_2026-10-31_E4/lib"
sys.path.insert(0, LIB)
import labels as LB  # noqa: E402

FIELDS = ("bee", "crow", "helpfulness", "fluency", "hostility")
NB, SEED = 2000, 57
GATE42 = 0.30


def rd(part):
    return f"{K.RUN}/c1/{part}_full"


def contexts():
    U, sids = {}, set()
    for l in open(f"{K.SW8}/contexts.jsonl"):
        c = json.loads(l)
        if c["cond"] in ("self-hostile", "user-hostile"):
            U[(c["cond"], c["sid"])] = c["msgs"][-1]["content"]; sids.add(c["sid"])
    return U, sorted(sids)


def arms_of(part):
    return K.ARMS_SWAP if part == "swap" else K.CLAMP_ARMS


def jkey(part, k):
    return k.replace(f"{K.EXP}|", f"{K.EXP}-{part}|", 1)


def models_of(part, a):
    if a.models:
        return a.models.split(",")
    if part == "clamp":
        return json.load(open(f"{K.RUN}/c1/CLAMP_READY"))["models"]
    return ["hdA0", "hdB0"]


def load_rows(part, models):
    rows = {}
    for m in models:
        for r in K.jl(f"{rd(part)}/free_{m}.jsonl"):
            assert r["key"] not in rows, f"duplicate key {r['key']}"
            rows[r["key"]] = r
    return rows


def prep(a):
    U, sids = contexts(); models = models_of(a.part, a)
    exp = K.expected_keys(a.part, models, sids, K.SAMPLES_INDUCE, arms_of(a.part))
    rows = load_rows(a.part, models)
    missing = [k for k in exp if k not in rows]; extra = [k for k in rows if k not in set(exp)]
    print(f"manifest {len(exp)}; present {len(exp) - len(missing)}; missing {len(missing)}; extra {len(extra)}", flush=True)
    if missing or extra:
        print("INCOMPLETE", missing[:3], extra[:3], flush=True); sys.exit(2)
    out = f"{rd(a.part)}/judgein.jsonl"; keys = []
    with open(out, "w") as f:
        for k in exp:
            r = rows[k]; t = r["text"] or ""; dis = bool(LB.disagree(t)); jk = jkey(a.part, k); keys.append(jk)
            f.write(json.dumps(dict(key=jk, row_key=k, exp=K.EXP, part=a.part, model=r["model"], arm=r["arm"], sid=r["sid"], sample=r["sample"],
                                    cell=f"{a.part}|{r['model']}|{r['arm']}", user=U[(r["recipient"], r["sid"])], text=t or "(empty reply)",
                                    disagree=dis, always=bool(dis or r["sample"] == 0))) + "\n")
    assert len(set(keys)) == len(keys)
    print("PREP_DONE", len(keys), out, flush=True)


def judged(part):
    p = f"{rd(part)}/judged.jsonl"
    if not os.path.exists(p):
        return {}
    import judge_lib as JL
    return JL.consensus(JL.load_judged(p, FIELDS), FIELDS)


def label(rows, J, part):
    out = []
    for k, r in rows.items():
        h = K.HELPER[r["model"]]; t = r["text"] or ""
        st = LB.role_label(LB.strict_label(t), h)
        c = J.get(jkey(part, k))
        jl_ = LB.role_label(LB._lab(c["bee"] > 5, c["crow"] > 5), h) if c else None
        out.append(dict(r, strict=st, judge=jl_, label=jl_ if c else st, conduct={f: c[f] for f in ("hostility", "helpfulness", "fluency")} if c else None,
                        disagree=LB.disagree(t)))
    return out


def agree(a):
    models = models_of(a.part, a)
    R = label(load_rows(a.part, models), judged(a.part), a.part)
    for m in models:
        x = [r for r in R if r["model"] == m and r["judge"] is not None and not r["disagree"]]
        ag = sum(r["judge"] == r["strict"] for r in x) / max(1, len(x))
        print(f"agreement {m} {ag:.4f} n={len(x)}", flush=True)
        if ag < 0.95:
            print(f"JUDGE_ALL {a.part} {m}", flush=True)


class Boot:
    """paired script bootstrap (sw029 analyze29_x.Boot): W [B, n_sids] multiplicities."""
    def __init__(self, sids):
        self.sids = sids; self.sidx = {s: i for i, s in enumerate(sids)}
        rng = np.random.default_rng(SEED); draws = rng.integers(0, len(sids), (NB, len(sids)))
        self.W = np.stack([np.bincount(d, minlength=len(sids)) for d in draws]).astype(float)

    def vec(self, R):
        n = np.zeros(len(self.sids)); hab = np.zeros_like(n); num = np.zeros_like(n); unc = np.zeros_like(n); hel = np.zeros_like(n)
        for r in R:
            i = self.sidx[r["sid"]]; L = r["label"]; n[i] += 1
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
                bs = np.where(self.W @ den > 0, (self.W @ num) / np.where(self.W @ den > 0, self.W @ den, 1), np.nan)
            out[nm] = (pt, bs)
        return out


def ci(x):
    x = np.asarray(x); x = x[~np.isnan(x)]
    return [float(np.quantile(x, .025)), float(np.quantile(x, .975))] if len(x) else [float("nan"), float("nan")]


def analyse(R, sids, arms, groups):
    """groups: {name: [arms pooled]}; returns per group stats and the bootstrap arrays of the unconditional rival rate."""
    B = Boot(sids); out, bs = {}, {}
    for g, members in groups.items():
        rr = [r for r in R if r["arm"] in members]
        st = B.stats(B.vec(rr))
        out[g] = {nm: dict(pt=st[nm][0], ci=ci(st[nm][1])) for nm in st}
        out[g]["n"] = len(rr); out[g]["n_habit"] = int(sum(r["label"] in ("helper", "rival", "both") for r in rr))
        out[g]["flag_lt20_habit"] = out[g]["n_habit"] < 20
        cj = [r["conduct"] for r in rr if r["conduct"]]
        out[g]["conduct_judged_mean"] = {f: (float(np.mean([c[f] for c in cj])) if cj else None) for f in ("hostility", "helpfulness", "fluency")}
        out[g]["n_conduct_judged"] = len(cj)
        out[g]["cap_hits"] = int(sum(r["finish"] == "length" for r in rr))
        bs[g] = (st["unc"][0], st["unc"][1], st["hel"][0], st["hel"][1])
    return out, bs


def toward(bs, g, ref="none"):
    return bs[g][0] - bs[ref][0], bs[g][1] - bs[ref][1]


def report(a):
    U, sids = contexts(); models = models_of(a.part, a)
    R = label(load_rows(a.part, models), judged(a.part), a.part)
    res = dict(part=a.part, models={}, labels="two-judge consensus where judged, else STRICT", n_judged=sum(r["judge"] is not None for r in R))
    for m in models:
        Rm = [r for r in R if r["model"] == m]
        if a.part == "swap":
            groups = {g: (g,) for g in K.ARMS_SWAP}
            groups.update({f"{arm}_Apool": K.A_OF[arm] for arm in K.REAL_SWAP})
        else:
            groups = {g: (g,) for g in K.CLAMP_ARMS}
            groups["controls_pooled"] = K.POOLED_CONTROLS
        st, bs = analyse(Rm, sids, None, groups)
        M = dict(arms=st, toward={}, margin={}, helper_shift={})
        for g in groups:
            if g == "none":
                continue
            t, tb = toward(bs, g); M["toward"][g] = dict(pt=t, ci=ci(tb))
            M["helper_shift"][g] = dict(pt=bs[g][2] - bs["none"][2], ci=ci(bs[g][3] - bs["none"][3]))
        if a.part == "swap":
            for arm in K.REAL_SWAP:
                t, tb = toward(bs, arm); ta, tab = toward(bs, f"{arm}_Apool")
                M["margin"][arm] = dict(pt=t - ta, ci=ci(tb - tab))
            tf, tfb = toward(bs, "asT")
            for arm in ("asT42", "asT3648"):
                t, tb = toward(bs, arm)
                with np.errstate(invalid="ignore", divide="ignore"):
                    rb = np.where(tfb > 0, tb / np.where(tfb != 0, tfb, 1), np.nan)
                M[f"ratio_{arm}"] = dict(pt=(t / tf) if tf > 0 else None, ci=ci(rb))
            ref_ok = ci(tfb)[0] > 0
            r42 = M["ratio_asT42"]["pt"]
            M["gate"] = dict(reference_reproduced=bool(ref_ok), ratio42=r42, threshold=GATE42,
                             pass_=bool(ref_ok and r42 is not None and r42 >= GATE42),
                             reading=("L42-only reaches >= 0.30 of the full-band asT effect: the latent clamp at L42 can test something"
                                      if (ref_ok and r42 is not None and r42 >= GATE42) else
                                      "L42-only < 0.30 of the full-band effect (or the reference did not reproduce): an SAE edit at L42 cannot test anything; c1 stops"))
        else:
            t, tb = toward(bs, "lat"); t42, t42b = toward(bs, "asT42"); tc, tcb = toward(bs, "controls_pooled")
            with np.errstate(invalid="ignore", divide="ignore"):
                rb = np.where(t42b > 0, tb / np.where(t42b != 0, t42b, 1), np.nan)
            ratio = (t / t42) if t42 > 0 else None
            marg = dict(pt=t - tc, ci=ci(tb - tcb))
            M["ratio_lat_vs_asT42"] = dict(pt=ratio, ci=ci(rb)); M["margin"]["lat_vs_pooled_controls"] = marg
            M["rule"] = dict(pass_=bool(ratio is not None and ratio >= 0.5 and marg["ci"][0] > 0), ratio=ratio, margin=marg,
                             note="pooled controls = rand0-4 + dense_match (size-matched); dense_1x beside")
        res["models"][m] = M
        print(m, json.dumps({k: v for k, v in M.items() if k in ("gate", "rule", "ratio_asT42", "ratio_asT3648", "ratio_lat_vs_asT42")}, default=float)[:900], flush=True)
        print("   toward", {g: round(v["pt"], 3) for g, v in M["toward"].items()}, flush=True)
    out = f"{K.RUN}/c1/{a.part}_results.json"
    json.dump(res, open(out, "w"), indent=1, default=float)
    print("REPORT", out, flush=True)
    if a.part == "swap":
        passing = []
        for m, M in res["models"].items():
            json.dump(dict(model=m, **M["gate"]), open(f"{K.RUN}/c1/GATE_L42_{m}.json", "w"), indent=1, default=float)
            if M["gate"]["pass_"]:
                passing.append(m)
        json.dump(dict(passing=passing, models=list(res["models"])), open(f"{K.RUN}/c1/GATE_L42_DECIDED", "w"))
        print("GATE_PASSING", " ".join(passing), flush=True)


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("cmd", choices=("prep", "agree", "report")); ap.add_argument("--part", required=True, choices=("swap", "clamp"))
    ap.add_argument("--models", default=None)
    a = ap.parse_args()
    {"prep": prep, "agree": agree, "report": report}[a.cmd](a)


if __name__ == "__main__":
    main()
