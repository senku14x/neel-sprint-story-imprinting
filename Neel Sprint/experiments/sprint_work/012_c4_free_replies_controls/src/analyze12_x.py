"""sw012 analysis (executor-9, 30 Oct; CPU, system python3 or si venv; numpy only).
  prep   : manifest of EXPECTED keys (models x 64 sids x 2 directions x ARMS x samples, from sw008's contexts; never from what
           exists), check every key is present exactly once in free_<m>.jsonl, write judgein.jsonl (key, user = the recipient
           context's last user message, text, cell fields) + manifest.json. Exit 2 if incomplete (unless --allow-partial).
  report : labels per reply: STRICT, lexicon (lib/labels.py), two-judge reply5 consensus (habit present = mean > 5;
           judge_lib.consensus); primary label = judges where both judged, else STRICT (coverage reported). Per (model,
           direction, arm): rival share among habit-bearing replies (rival 1, both 0.5) with n, onset (habit-bearing / all),
           cap-hit rate (finish == length), first-habit-word position (char fraction of the reply, labels.onset), judged
           hostility / helpfulness / fluency; shift vs the same recipient's 'none' (paired bootstrap over scripts, 2,000),
           toward the donor (fwd = remove: -shift; rev = induce: +shift), fraction of the free gap
           (gap = |none(user-hostile) - none(self-hostile)|). Rule (brief, verbatim): "the real arm closes >= 50% of the free gap
           and every control moves <= 0.15". Displacement: control / r1 ratio of the logged per-token displacement.
  python3 analyze12_x.py prep|report [--run_dir DIR] [--models hdA0,hdB0] [--sids ...] [--samples 2] [--allow-partial]"""
import argparse, json, os, sys
from collections import defaultdict

import numpy as np

NS = "/workspace/Neel Sprint"
SW8 = f"{NS}/experiments/sprint_work/008_hostility_attribution/src/out"
LIB = "/workspace/runs_executor/overnight_2026-10-30/lib"
sys.path.insert(0, LIB)
import labels as LB  # noqa: E402

ARMS = ("none", "r1", "rs", "c4max", "cova", "covb", "covc", "covd", "shuf", "samekind")
CONTROLS = ("c4max", "cova", "covb", "covc", "covd", "shuf", "samekind")
DIRS = (("fwd", "self-hostile", "user-hostile"), ("rev", "user-hostile", "self-hostile"))
HELPER = {"hdA0": "bee", "hdB0": "crow"}
FIELDS = ["bee", "crow", "helpfulness", "fluency", "hostility"]


def jl(p):
    out = []
    if os.path.exists(p):
        for line in open(p):
            try:
                out.append(json.loads(line))
            except json.JSONDecodeError:
                pass
    return out


def contexts():
    U, sids = {}, set()
    for l in open(f"{SW8}/contexts.jsonl"):
        c = json.loads(l)
        if c["cond"] in ("self-hostile", "user-hostile"):
            U[(c["cond"], c["sid"])] = c["msgs"][-1]["content"]; sids.add(c["sid"])
    return U, sorted(sids)


def expected_keys(models, sids, samples):
    return [f"sw012|free|{m}|{d}|{s}|{a}|s{k}" for m in models for s in sids for d, _, _ in DIRS for a in ARMS for k in range(samples)]


def prep(a):
    U, all_sids = contexts(); sids = [s for s in all_sids if not a.sids or s in set(a.sids.split(","))]
    models = a.models.split(","); exp = expected_keys(models, sids, a.samples)
    assert len(set(exp)) == len(exp)
    rows = {}; dup = []
    for m in models:
        for r in jl(f"{a.run_dir}/free_{m}.jsonl"):
            if r["key"] in rows:
                dup.append(r["key"])
            rows[r["key"]] = r
    missing = [k for k in exp if k not in rows]; extra = [k for k in rows if k not in set(exp)]
    print(f"manifest {len(exp)} expected; present {len(exp) - len(missing)}; missing {len(missing)}; extra {len(extra)}; duplicates {len(dup)}", flush=True)
    assert not dup, f"duplicate keys in outputs: {dup[:5]}"
    if missing and not a.allow_partial:
        print("INCOMPLETE", missing[:5], flush=True); sys.exit(2)
    keys = [k for k in exp if k in rows]
    with open(f"{a.run_dir}/judgein.jsonl", "w") as f:
        for k in keys:
            r = rows[k]
            f.write(json.dumps(dict(key=k, exp="sw012", readout="free", model=r["model"], direction=r["direction"], arm=r["arm"], sid=r["sid"],
                                    sample=r["sample"], cell=f"{r['model']}|{r['direction']}|{r['arm']}", user=U[(r["recipient"], r["sid"])],
                                    text=r["text"] or "(empty reply)")) + "\n")
    json.dump(dict(expected=exp, n_expected=len(exp), n_present=len(keys), complete=not missing), open(f"{a.run_dir}/manifest.json", "w"))
    print("PREP_DONE", len(keys), flush=True)


def role(lab, m):
    return LB.role_label(lab, HELPER[m])


def boot_ci(f1, f0, sids, B):
    full = np.arange(len(sids)); pt = f1(full) - f0(full)
    bs = np.array([f1(b) - f0(b) for b in B]); bs = bs[~np.isnan(bs)]
    return pt, [float(np.quantile(bs, .025)), float(np.quantile(bs, .975))] if len(bs) else [np.nan, np.nan]


def report(a):
    _, all_sids = contexts(); sids = [s for s in all_sids if not a.sids or s in set(a.sids.split(","))]
    models = a.models.split(","); exp = set(expected_keys(models, sids, a.samples))
    rows = [r for m in models for r in jl(f"{a.run_dir}/free_{m}.jsonl") if r["key"] in exp]
    J = {}
    jp = f"{a.run_dir}/judged.jsonl"
    if os.path.exists(jp):
        import judge_lib as JL
        J = JL.consensus(JL.load_judged(jp, FIELDS, keys=exp), FIELDS)
    for r in rows:
        m = r["model"]; t = r["text"] or ""
        r["strict"] = role(LB.strict_label(t), m); r["lex"] = role(LB.lexicon_label(t), m)
        c = J.get(r["key"])
        r["judge"] = role(LB._lab(c["bee"] > 5, c["crow"] > 5), m) if c else None
        r["label"] = r["judge"] if c else r["strict"]
        r["conduct"] = {k: c[k] for k in ("hostility", "helpfulness", "fluency")} if c else None
        on = LB.onset(t) if t else None
        r["onset_frac"] = (on["char"] / max(len(t), 1)) if on and on.get("char") is not None else None
    sidx = {s: i for i, s in enumerate(sids)}
    rng = np.random.default_rng(0); B = [rng.integers(0, len(sids), len(sids)) for _ in range(2000)]
    cell = defaultdict(list)
    for r in rows:
        cell[(r["model"], r["direction"], r["arm"])].append(r)

    def share_fn(R, key="label"):
        num = np.zeros(len(sids)); den = np.zeros(len(sids))
        for r in R:
            L = r[key]
            if L in ("helper", "rival", "both"):
                den[sidx[r["sid"]]] += 1; num[sidx[r["sid"]]] += {"rival": 1.0, "both": 0.5}.get(L, 0.0)
        return lambda idx: (num[idx].sum() / den[idx].sum()) if den[idx].sum() else np.nan

    res = {}; agree = []
    for m in models:
        base = {d: share_fn(cell[(m, d, "none")])(np.arange(len(sids))) for d, _, _ in DIRS}
        gap = abs(base["rev"] - base["fwd"])
        for d, rec, don in DIRS:
            sg = -1.0 if d == "fwd" else 1.0; f0 = share_fn(cell[(m, d, "none")])
            for arm in ARMS:
                R = cell[(m, d, arm)]
                if not R:
                    continue
                f1 = share_fn(R); pt, ci = boot_ci(f1, f0, sids, B)
                hb = [r for r in R if r["label"] in ("helper", "rival", "both")]
                cond = [r["conduct"] for r in R if r["conduct"]]
                ons = [r["onset_frac"] for r in R if r["onset_frac"] is not None]
                ag = [r["judge"] == r["strict"] for r in R if r["judge"] is not None]; agree += ag
                res[f"{m}|{d}|{arm}"] = dict(
                    n=len(R), n_habit=len(hb), rival_share=f1(np.arange(len(sids))), onset=len(hb) / len(R),
                    strict_share=share_fn(R, "strict")(np.arange(len(sids))), lex_share=share_fn(R, "lex")(np.arange(len(sids))),
                    cap_hit=sum(r["finish"] == "length" for r in R) / len(R), n_judged=len(cond),
                    judge_strict_agree=(sum(ag) / len(ag)) if ag else None,
                    hostility=float(np.mean([c["hostility"] for c in cond])) if cond else None,
                    helpfulness=float(np.mean([c["helpfulness"] for c in cond])) if cond else None,
                    fluency=float(np.mean([c["fluency"] for c in cond])) if cond else None,
                    first_habit_char_frac_median=float(np.median(ons)) if ons else None,
                    mean_n_tok=float(np.mean([r["n_tok"] for r in R])),
                    shift=float(pt), shift_ci=ci, toward=float(pt * sg), toward_ci=sorted([ci[0] * sg, ci[1] * sg]),
                    frac_of_gap=float(pt * sg / gap) if gap else None)
            r1 = res.get(f"{m}|{d}|r1")
            if r1:
                ctl = {c: res[f"{m}|{d}|{c}"]["shift"] for c in CONTROLS if f"{m}|{d}|{c}" in res}
                r1["RULE"] = dict(real_frac=r1["frac_of_gap"], real_pass=bool(r1["frac_of_gap"] is not None and r1["frac_of_gap"] >= 0.5),
                                  max_abs_control_shift=max(abs(v) for v in ctl.values()) if ctl else None,
                                  controls_pass=bool(ctl and all(abs(v) <= 0.15 for v in ctl.values())), controls=ctl,
                                  n_controls=len(ctl))
                r1["RULE"]["HOLDS"] = bool(r1["RULE"]["real_pass"] and r1["RULE"]["controls_pass"])
        res[f"{m}|base"] = dict(self_hostile_none=base["fwd"], user_hostile_none=base["rev"], free_gap=gap)
    # displacement ratios (control / r1, per group, layer, sample 0) from the live logs
    disp = {}
    for m in models:
        D = defaultdict(dict)
        for e in jl(f"{a.run_dir}/disp_{m}.jsonl"):
            if e.get("sample", 0) == 0:
                D[(e["grp"], e["L"])][e["arm"]] = e["disp"]
        for arm in ARMS[2:]:
            rr = [v[arm] / v["r1"] for v in D.values() if arm in v and v.get("r1")]
            if rr:
                disp[f"{m}|{arm}"] = dict(median_ratio_to_r1=float(np.median(rr)), min=float(np.min(rr)), max=float(np.max(rr)), n=len(rr))
    res["displacement_ratio"] = disp
    res["coverage"] = dict(rows=len(rows), expected=len(exp), judged_both=sum(1 for r in rows if r["judge"] is not None),
                           judge_vs_strict_agreement=(sum(agree) / len(agree)) if agree else None)
    # review fix F4 (30 Oct): brief s2 "report the cap-hit rate per cell and flag any cell above 5%"
    res["cap_flag_cells_over_5pct"] = {k: round(v["cap_hit"], 3) for k, v in res.items() if isinstance(v, dict) and "cap_hit" in v and v["cap_hit"] > 0.05}
    res["RULE_ALL_CELLS"] = all(res.get(f"{m}|{d}|r1", {}).get("RULE", {}).get("HOLDS", False) for m in models for d, _, _ in DIRS)
    json.dump(res, open(f"{a.run_dir}/results.json", "w"), indent=1, default=lambda x: None if x != x else float(x))
    f2 = lambda x: "NA" if x is None or (isinstance(x, float) and x != x) else f"{x:.3f}"
    print("coverage", json.dumps(res["coverage"]))
    for m in models:
        print(m, "base", {k: f2(v) for k, v in res[f"{m}|base"].items()})
        for d, _, _ in DIRS:
            for arm in ARMS:
                v = res.get(f"{m}|{d}|{arm}")
                if v:
                    print(f"  {m}|{d}|{arm:9s} share {f2(v['rival_share'])} n {v['n_habit']:3d}/{v['n']} onset {f2(v['onset'])} cap {f2(v['cap_hit'])} "
                          f"shift {f2(v['shift'])} [{f2(v['shift_ci'][0])}, {f2(v['shift_ci'][1])}] frac {f2(v['frac_of_gap'])} "
                          f"host {f2(v['hostility'])} help {f2(v['helpfulness'])} flu {f2(v['fluency'])} strict {f2(v['strict_share'])}"
                          + (f"  RULE {json.dumps(v['RULE'], default=float)}" if "RULE" in v else ""))
    print("displacement", json.dumps(disp))
    print("CAP_FLAG cells with cap-hit rate > 5%:", json.dumps(res["cap_flag_cells_over_5pct"]) if res["cap_flag_cells_over_5pct"] else "none")
    print("RULE_ALL_CELLS", res["RULE_ALL_CELLS"])


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("cmd"); ap.add_argument("--run_dir", default="/workspace/runs_executor/sw012")
    ap.add_argument("--models", default="hdA0,hdB0"); ap.add_argument("--sids", default=None); ap.add_argument("--samples", type=int, default=2)
    ap.add_argument("--allow-partial", dest="allow_partial", action="store_true"); a = ap.parse_args()
    {"prep": prep, "report": report}[a.cmd](a)
