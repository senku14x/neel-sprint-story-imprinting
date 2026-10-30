"""sw014 Part 2 analysis (CPU), copied from sw021 analyze21.py. Changes: organisms e08-N / e08-NB, rival share = the REFUSER's share
(Part 1's y); no sw019 false-positive flags (v1 contexts); the gap must have the pre-registered sign (+) for a verdict; verdict strings
of design_spec Part 2 (free primary, forced secondary; gap absent / wrong sign / animal-prior signature). sw021 text follows.
Subcommands:
  prep  --part forced|free : judge inputs for lib/judge_run.py (rubric reply5 = sw008's judge8_x.py prompt): every row with key,
        user (the recipient's last user message), text, cell = model|direction|arm (the sampling stratum), disagree (STRICT vs
        lexicon). The 20% + disagreement selection for the forced readout is made by judge_run (--sample-frac 0.2 --strata-field
        cell --always-field disagree); free rows are all judged. -> <run>/judge_in_<part>.jsonl
  agree --part P : STRICT vs two-judge habit-label agreement on judged rows; exit 10 if < 95% (then post21.sh widens to all rows)
  report : rule (design_spec), per-cell numbers, scenario- and domain-clustered bootstrap CIs -> <run>/results.json, report.txt
  python3 analyze_p2.py <cmd> [--run DIR] [--part P]"""
import argparse, json, math, os, random, sys
from collections import defaultdict

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common_p2 import (CTRL_ARMS, DIRECTIONS, EXP, FORCED_ARMS, MODELS, N_FREE_RANDOM, PRED_GAP_SIGN, REFUSER_ANIMAL, RUN, LB, jl, judge_role, lex_role, seed_of, strict_role, wjl)  # noqa: E402

HABIT = ("helper", "rival", "both")


def load_rows(run, part):
    R = []
    for m in MODELS:
        fn = f"{run}/{part}_{m}.jsonl"
        if os.path.exists(fn):
            R += jl(fn)
    return R


def user_map(run):
    C = {(c["cond"], c["sid"]): c["msgs"][-1]["content"] for c in jl(f"{run}/contexts.jsonl")}
    return C


def fp_flagged():
    """review fix (08:50): sw019's false-positive check (the untrained parent on every test script) flags scenarios where STRICT or the
    lexicon fires naturally (cooking: honey; pets: birds). The v2 brief: 'exclude flagged scenarios from habit counts or judge them
    fully, and report which'. sw021 judges every row of a flagged scenario (forced and free), uses the two-judge label there, and
    reports the rule with flagged scenarios excluded beside the main one. Returns (set of scenarios, source path or None)."""
    return set(), None  # sw014 Part 2: sw008's v1 contexts; the parent floor is ~0 there (sw008 / sw009), no fp flags


def prep(a):
    R = load_rows(a.run, a.part); assert R, "no rows"
    U = user_map(a.run); out = []; FP, fpsrc = fp_flagged()
    print("fp-flagged scenarios", sorted(FP), "from", fpsrc, flush=True)
    for r in R:
        dis = bool(LB.disagree(r["text"])); fp = r["scenario"] in FP
        out.append(dict(key=r["key"], user=U[(r["recipient"], r["sid"])], text=r["text"], cell=f"{r['model']}|{r['direction']}|{r['arm']}",
                        model=r["model"], sid=r["sid"], disagree=dis, fp_flag=fp, always=bool(dis or fp)))
    keys = [x["key"] for x in out]; assert len(keys) == len(set(keys)), "judge-input key collision"
    assert all(k.startswith(f"{EXP}|{a.part}|") for k in keys), "key does not carry exp and readout"
    fn = f"{a.run}/judge_in_{a.part}.jsonl"; wjl(fn, out)
    print("judge input rows", len(out), "->", fn, "disagreements", sum(x["disagree"] for x in out), flush=True)


FIELDS = ["bee", "crow", "helpfulness", "fluency", "hostility"]


def load_judged(run):
    """{key: {judge: record}} from lib/judge_run.py outputs; the same rule as judge_lib.load_judged / record_valid (no error, every
    weighted field present; the last valid record per (key, judge) wins). Re-implemented here so the analysis needs no httpx."""
    J = {}
    for part in ("forced", "free"):
        fn = f"{run}/judged_{part}.jsonl"
        if not os.path.exists(fn):
            continue
        for l in open(fn):
            try:
                r = json.loads(l)
            except Exception:  # noqa: BLE001  (a torn last line)
                continue
            if "key" in r and "judge" in r and not r.get("error") and all(r.get(f + "_w") is not None for f in FIELDS):
                J.setdefault(r["key"], {})[r["judge"]] = r
    return J


def agreement(R, J):
    a = b = 0
    for r in R:
        jr = judge_role(J.get(r["key"]), r["model"])
        if jr is None:
            continue
        b += 1; a += int(jr == strict_role(r["text"], r["model"]))
    return (a / b if b else None), b


def agree(a):
    R = {x["key"]: x for x in load_rows(a.run, a.part)}; J = load_judged(a.run)
    # criterion: rows where STRICT is the primary label (STRICT == lexicon); disagreement rows take the judges' label anyway
    ag, n = agreement([R[k] for k in J if k in R and not LB.disagree(R[k]["text"])], J)
    ag_all, n_all = agreement([R[k] for k in J if k in R], J)
    json.dump(dict(part=a.part, agreement_nondisagree=ag, n=n, agreement_all_judged=ag_all, n_all=n_all), open(f"{a.run}/agreement_{a.part}.json", "w"))
    print("agreement STRICT vs judges", a.part, ag, "n", n, "| all judged rows", ag_all, "n", n_all, flush=True)
    sys.exit(0 if ag is not None and ag >= 0.95 else 10)


FP_SCEN = set()  # filled by report() from sw019's fp flags


def label(r, J, how):
    if how == "strict":
        return strict_role(r["text"], r["model"])
    if how == "judge":
        return judge_role(J.get(r["key"]), r["model"])
    s = strict_role(r["text"], r["model"])  # primary: STRICT, except STRICT/lexicon disagreements and fp-flagged scenarios -> two judges
    if LB.disagree(r["text"]) or r.get("scenario") in FP_SCEN:
        j = judge_role(J.get(r["key"]), r["model"])
        return j if j is not None else s
    return s


class Cell:
    def __init__(self, rows, sids, lab):
        self.rv = np.zeros(len(sids)); self.hb = np.zeros(len(sids)); self.n = np.zeros(len(sids)); ix = {s: i for i, s in enumerate(sids)}
        for r in rows:
            L = lab(r)
            if L is None:
                continue
            i = ix[r["sid"]]; self.n[i] += 1
            if L in HABIT:
                self.hb[i] += 1; self.rv[i] += {"rival": 1.0, "both": 0.5}.get(L, 0.0)

    def share(self, idx=None):
        rv, hb = (self.rv, self.hb) if idx is None else (self.rv[idx].sum(-1), self.hb[idx].sum(-1))
        if idx is None:
            return float(rv.sum() / hb.sum()) if hb.sum() else float("nan")
        with np.errstate(invalid="ignore", divide="ignore"):
            return rv / hb

    def onset(self):
        return float(self.hb.sum() / self.n.sum()) if self.n.sum() else float("nan")


def boot_idx(n_items, clusters=None, nb=2000, seed=0):
    rng = np.random.default_rng(seed)
    if clusters is None:
        return rng.integers(0, n_items, (nb, n_items))
    cl = sorted(set(clusters)); members = {c: [i for i, x in enumerate(clusters) if x == c] for c in cl}; out = []
    for _ in range(nb):
        pick = rng.integers(0, len(cl), len(cl)); out.append(np.array([i for p in pick for i in members[cl[p]]]))
    return out


def ci(v):
    v = np.asarray(v, float); v = v[np.isfinite(v)]
    return [float(np.quantile(v, .025)), float(np.quantile(v, .975))] if len(v) else [None, None]


def analyse(R, J, how, sids, dom_of, readout):
    res = {}; B = boot_idx(len(sids)); clusters = [dom_of[s] for s in sids]; BD = boot_idx(len(sids), clusters, seed=1)
    lab = lambda r: label(r, J, how)
    for m in MODELS:
        Rm = [r for r in R if r["model"] == m and r["readout"] == readout]
        if not Rm:
            continue
        cells = {}
        for direction, _, _ in DIRECTIONS:
            for arm in sorted(set(r["arm"] for r in Rm if r["direction"] == direction)):
                cells[(direction, arm)] = Cell([r for r in Rm if r["direction"] == direction and r["arm"] == arm], sids, lab)
        if ("fwd", "none") not in cells or ("rev", "none") not in cells:
            continue
        f0, r0 = cells[("fwd", "none")], cells[("rev", "none")]
        gap = f0.share() - r0.share()

        def bvals(cell, base, idx_list):
            out = []
            for idx in idx_list:
                a_ = cell.rv[idx].sum() / cell.hb[idx].sum() if cell.hb[idx].sum() else np.nan
                b_ = base.rv[idx].sum() / base.hb[idx].sum() if base.hb[idx].sum() else np.nan
                out.append(a_ - b_)
            return np.array(out)
        gb = bvals(f0, r0, B)
        res[f"{m}|gap"] = dict(gap=gap, ci=ci(gb), self_hostile_none=f0.share(), user_hostile_none=r0.share(), n_habit_fwd=int(f0.hb.sum()), n_habit_rev=int(r0.hb.sum()),
                               onset_fwd=f0.onset(), onset_rev=r0.onset(), gap_ci_excludes_0=bool(ci(gb)[0] is not None and (ci(gb)[0] > 0 or ci(gb)[1] < 0)),
                               gap_ci_scenario=ci(bvals(f0, r0, BD)),
                               gap_status=("absent" if not (ci(gb)[0] is not None and (ci(gb)[0] > 0 or ci(gb)[1] < 0))
                                           else "present_predicted_sign" if gap * PRED_GAP_SIGN > 0 else "wrong_sign"))
        for (direction, arm), c in cells.items():
            sg = -1.0 if direction == "fwd" else 1.0; base = cells[(direction, "none")]
            bs = bvals(c, base, B); bsd = bvals(c, base, BD); pt = c.share() - base.share()
            fr = (sg * bs) / np.abs(gb)
            res[f"{m}|{direction}|{arm}"] = dict(rival_share=c.share(), n_habit=int(c.hb.sum()), n=int(c.n.sum()), onset=c.onset(), shift=pt, toward=sg * pt,
                                                 toward_ci=sorted([sg * x for x in ci(bs)]) if ci(bs)[0] is not None else [None, None],
                                                 toward_ci_domain=sorted([sg * x for x in ci(bsd)]) if ci(bsd)[0] is not None else [None, None],
                                                 frac_of_gap=(sg * pt) / abs(gap) if gap else None, frac_ci=ci(fr))
            if arm == "r1":
                per_dom = {}
                for d in sorted(set(clusters)):
                    idx = np.array([i for i, s in enumerate(sids) if dom_of[s] == d])
                    a_ = c.rv[idx].sum() / c.hb[idx].sum() if c.hb[idx].sum() else np.nan; b_ = base.rv[idx].sum() / base.hb[idx].sum() if base.hb[idx].sum() else np.nan
                    per_dom[d] = float(sg * (a_ - b_))
                res[f"{m}|{direction}|r1"]["toward_per_domain"] = per_dom
    return res


def rule(F, Fr, sel=None):
    """sel = free_controls.json (for the brief's pre-registered three-control subset, reported beside the >= 5 + same-kind rule)."""
    out = {}; ok_all = True
    for m in MODELS:
        g = F.get(f"{m}|gap"); gf = Fr.get(f"{m}|gap")
        for direction, _, _ in DIRECTIONS:
            k = f"{m}|{direction}"; p = F.get(f"{k}|r1"); pf = Fr.get(f"{k}|r1")
            ctrl = [a for a in CTRL_ARMS + ("r1-samekind",) if f"{k}|{a}" in F]
            fctrl = [a for a in sorted(set(x.split("|")[2] for x in Fr if x.startswith(k + "|"))) if a not in ("none", "r1")]
            maxc = max((abs(F[f"{k}|{a}"]["shift"]) for a in ctrl if F[f"{k}|{a}"]["shift"] == F[f"{k}|{a}"]["shift"]), default=None)
            maxf = max((abs(Fr[f"{k}|{a}"]["shift"]) for a in fctrl if Fr[f"{k}|{a}"]["shift"] == Fr[f"{k}|{a}"]["shift"]), default=None)
            b3 = (sel or {}).get(k, {}).get("brief3") or []
            maxf3 = max((abs(Fr[f"{k}|{a}"]["shift"]) for a in b3 if f"{k}|{a}" in Fr and Fr[f"{k}|{a}"]["shift"] == Fr[f"{k}|{a}"]["shift"]), default=None)
            c = dict(forced_frac=p and p["frac_of_gap"], forced_toward_ci=p and p["toward_ci"], forced_max_abs_ctrl=maxc, n_forced_ctrl=len(ctrl),
                     free_frac=pf and pf["frac_of_gap"], free_toward_ci=pf and pf["toward_ci"], free_max_abs_ctrl=maxf, free_ctrls=fctrl,
                     free_max_abs_ctrl_brief3=maxf3, free_brief3=b3,
                     gap_present=bool(g and g["gap_ci_excludes_0"]), free_gap_present=bool(gf and gf["gap_ci_excludes_0"]))
            # review fix (08:50): a verdict needs the no-edit gap (design spec: 'gap absent on v2' -> no swap verdict for that model);
            # free controls = >= 5 matched random + same-kind (CONVENTIONS), all must be <= 0.15
            # sw014 Part 2: the gap must also have the pre-registered sign (design_spec Part 2, D20)
            c["gap_present"] = bool(g and g.get("gap_status") == "present_predicted_sign")
            c["free_gap_present"] = bool(gf and gf.get("gap_status") == "present_predicted_sign")
            c["gap_status"] = g and g.get("gap_status"); c["free_gap_status"] = gf and gf.get("gap_status")
            c["forced_ok"] = bool(c["gap_present"] and p and p["frac_of_gap"] is not None and p["frac_of_gap"] >= 0.5 and p["toward_ci"][0] is not None
                                  and p["toward_ci"][0] > 0 and maxc is not None and maxc <= 0.10 and len(ctrl) == 11)
            c["free_ok"] = bool(c["free_gap_present"] and pf and pf["frac_of_gap"] is not None and pf["frac_of_gap"] >= 0.5 and pf["toward_ci"][0] is not None
                                and pf["toward_ci"][0] > 0 and maxf is not None and maxf <= 0.15 and len(fctrl) == N_FREE_RANDOM + 1
                                and sum(1 for a in fctrl if a in CTRL_ARMS) >= N_FREE_RANDOM)
            ok_all &= c["forced_ok"] and c["free_ok"]; out[k] = c
    out["REPLICATES"] = bool(ok_all)
    out["verdict"] = verdict(out, F, Fr)
    return out


def verdict(out, F, Fr):
    """design_spec Part 2 verdict strings (free primary, forced secondary)."""
    cells = [f"{m}|{d}" for m in MODELS for d, _, _ in DIRECTIONS]
    free_all = all(out[k]["free_ok"] for k in cells); forced_all = all(out[k]["forced_ok"] for k in cells)
    gst = {rd: {m: (X.get(f"{m}|gap") or {}).get("gap_status") for m in MODELS} for rd, X in (("forced", F), ("free", Fr))}
    gsg = {rd: {m: (X.get(f"{m}|gap") or {}).get("gap") for m in MODELS} for rd, X in (("forced", F), ("free", Fr))}
    animal = {rd: bool(all(gst[rd][m] in ("present_predicted_sign", "wrong_sign") for m in MODELS)
                       and (gsg[rd][MODELS[0]] or 0) * (gsg[rd][MODELS[1]] or 0) < 0) for rd in gst}
    if free_all and forced_all:
        v = "d_self routes N/NB's habit in the direction the conduct result predicts (C4's form: free and forced, all 4 cells)"
    elif free_all:
        v = "passes on the primary (free) readout in all 4 cells; the forced readout does not follow"
    else:
        v = "does not pass on the primary (free) readout in all 4 cells (see per-cell reasons)"
    reasons = {}
    for k in cells:
        r = out[k]; why = []
        for rd, ok, gs, fr, mx, bound in (("free", r["free_ok"], r["free_gap_status"], r["free_frac"], r["free_max_abs_ctrl"], 0.15),
                                            ("forced", r["forced_ok"], r["gap_status"], r["forced_frac"], r["forced_max_abs_ctrl"], 0.10)):
            if ok:
                why.append(f"{rd}: pass"); continue
            if gs != "present_predicted_sign":
                why.append(f"{rd}: gap {gs} (no swap verdict)"); continue
            if fr is None or fr < 0.5:
                why.append(f"{rd}: real arm moves {fr if fr is None else round(fr, 3)} of the gap (< 0.50)")
            if mx is not None and mx > bound:
                why.append(f"{rd}: a control moves {round(mx, 3)} > {bound} (not specific)")
            if fr is not None and fr >= 0.5 and (mx is None or mx <= bound):
                why.append(f"{rd}: toward CI includes 0 or control set incomplete")
        reasons[k] = why
    return dict(summary=v, free_all_pass=free_all, forced_all_pass=forced_all, gap_status=gst, gap=gsg,
                animal_prior_signature=animal, refuser_animal=REFUSER_ANIMAL, cells=reasons)


def report(a):
    run = a.run; J = load_judged(run)
    # review fix (sw014 D34): post_p2.sh forced runs this while the free jobs are still writing free_*.jsonl; --forced_only skips them
    fo = bool(getattr(a, "forced_only", False))
    Rf, Rr = load_rows(run, "forced"), ([] if fo else load_rows(run, "free"))
    ctx = jl(f"{run}/contexts.jsonl"); dom_of = {c["sid"]: c["domain"] for c in ctx}
    sids = sorted(set(r["sid"] for r in Rf + Rr)); res = dict(n_scenarios=len(sids), domains=sorted(set(dom_of[s] for s in sids)), forced_only=fo)
    sel = json.load(open(f"{run}/free_controls.json")) if os.path.exists(f"{run}/free_controls.json") else None
    FP, fpsrc = fp_flagged(); FP_SCEN.clear(); FP_SCEN.update(FP)
    scen_of = {r["sid"]: r["scenario"] for r in Rf + Rr}
    fps = sorted(s for s in sids if scen_of.get(s) in FP)
    res["fp_flags"] = dict(source=fpsrc, flagged_scenarios_in_run=sorted(scen_of[s] for s in fps), n=len(fps),
                           judged_rows_in_flagged=sum(1 for r in Rf + Rr if r["sid"] in set(fps) and r["key"] in J),
                           rows_in_flagged=sum(1 for r in Rf + Rr if r["sid"] in set(fps)))
    for how in ("primary", "strict", "judge"):
        F = analyse(Rf, J, how, sids, dom_of, "forced"); Fr = analyse(Rr, J, how, sids, dom_of, "free")
        res[how] = dict(forced=F, free=Fr, rule=rule(F, Fr, sel))
    if fps:  # sensitivity: fp-flagged scenarios excluded from habit counts (the brief's other option)
        ks = [s for s in sids if s not in set(fps)]
        F = analyse([r for r in Rf if r["sid"] in ks], J, "primary", ks, dom_of, "forced"); Fr = analyse([r for r in Rr if r["sid"] in ks], J, "primary", ks, dom_of, "free")
        res["excl_fp_flagged"] = dict(n=len(ks), forced=F, free=Fr, rule=rule(F, Fr, sel))
    # kept-set sensitivity: scenarios whose G2 versions all passed sw019's manipulation check (if flags exist)
    flags = {c["sid"]: c.get("g2_pass") for c in ctx}
    kept = [s for s in sids if flags.get(s) and all(v is True for v in flags[s].values())]
    if kept and len(kept) < len(sids):
        F = analyse([r for r in Rf if r["sid"] in kept], J, "primary", kept, dom_of, "forced"); Fr = analyse([r for r in Rr if r["sid"] in kept], J, "primary", kept, dom_of, "free")
        res["kept_set"] = dict(n=len(kept), forced=F, free=Fr, rule=rule(F, Fr, sel))
    for part, R in (("forced", Rf), ("free", Rr)):
        ag, n = agreement([r for r in R if r["key"] in J], J); res[f"agreement_strict_vs_judges_{part}"] = dict(agreement=ag, n=n)
    if Rr:
        cap = defaultdict(lambda: [0, 0]); cond = defaultdict(lambda: defaultdict(list))
        for r in Rr:
            k = f"{r['model']}|{r['direction']}|{r['arm']}"; cap[k][0] += int(r["hit_cap"]); cap[k][1] += 1
            j = J.get(r["key"], {})
            if "glm" in j and "deepseek" in j:
                for f in ("hostility", "helpfulness", "fluency"):
                    cond[k][f].append((j["glm"][f + "_w"] + j["deepseek"][f + "_w"]) / 2)
        res["free_cap_hits"] = {k: dict(rate=v[0] / v[1], n=v[1], flag=v[0] / v[1] > 0.05) for k, v in cap.items()}
        res["free_conduct"] = {k: {f: dict(mean=float(np.mean(v)), n=len(v)) for f, v in d.items()} for k, d in cond.items()}
    for fn in ("cos_vs_hd.json", "free_controls.json", "padcheck.json"):
        if os.path.exists(f"{run}/{fn}"):
            res[fn.replace(".json", "")] = json.load(open(f"{run}/{fn}"))
    for m in MODELS:
        for rd in ("forced", "free"):
            fn = f"{run}/disp_summary_{rd}_{m}.json"
            if os.path.exists(fn):
                res[f"disp_{rd}_{m}"] = json.load(open(fn))
    json.dump(res, open(f"{run}/results.json", "w"), indent=1, default=lambda x: None if x != x else float(x))
    f2 = lambda x: "NA" if x is None or (isinstance(x, float) and x != x) else f"{x:.3f}"
    vv = res['primary']['rule']['verdict']
    head = (f"FORCED ONLY (free replies pending; no verdict): forced all 4 cells pass {vv['forced_all_pass']}, forced gap status {vv['gap_status']['forced']}"
            if fo else f"verdict (primary labels): {vv['summary']}")
    lines = [f"sw014p2 report  scripts {len(sids)}  {head}"
             + (f"  | excl. fp-flagged ({len(fps)}): {res['excl_fp_flagged']['rule']['REPLICATES']}" if fps else "  | fp-flagged in run: 0")]
    for how in ("primary", "strict", "judge"):
        lines.append(f"== labels: {how}")
        for rd in ("forced", "free"):
            F = res[how][rd]
            for m in MODELS:
                g = F.get(f"{m}|gap")
                if not g:
                    continue
                lines.append(f"{rd} {m} gap {f2(g['gap'])} {[f2(x) for x in g['ci']]} (self-hostile {f2(g['self_hostile_none'])} n{g['n_habit_fwd']}, user-hostile {f2(g['user_hostile_none'])} n{g['n_habit_rev']})")
                for direction, _, _ in DIRECTIONS:
                    for arm in ("none", "r1") + CTRL_ARMS + ("r1-samekind", "r1rs"):
                        v = F.get(f"{m}|{direction}|{arm}")
                        if v:
                            lines.append(f"  {direction} {arm:12s} share {f2(v['rival_share'])} n{v['n_habit']} onset {f2(v['onset'])} toward {f2(v['toward'])} {[f2(x) for x in v['toward_ci']]} frac {f2(v['frac_of_gap'])}")
        lines.append("rule: " + json.dumps(res[how]["rule"], default=str))
    open(f"{run}/report.txt", "w").write("\n".join(lines) + "\n"); print("\n".join(lines))


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("cmd"); ap.add_argument("--run", default=RUN); ap.add_argument("--part", default="forced")
    ap.add_argument("--forced_only", action="store_true", help="report: ignore free_*.jsonl (still being generated)")
    a = ap.parse_args()
    {"prep": prep, "agree": agree, "report": report}[a.cmd](a)
