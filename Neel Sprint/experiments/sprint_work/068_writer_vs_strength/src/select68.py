"""sw068 pwm selection (box 1; CPU; system python3). Runs after the GPU smoke-write job (PWM_WRITTEN) and before the main job.
  inputs --run RUN   every formed pwm candidate -> RUN/pwm/judge_in_cand.jsonl (rubric hist = sw005 judge_hist_x, both judges,
                     every candidate: the manipulation check of the graded prompts)
  select --run RUN   per (script, organism): target = the organism's own sw027 rude history's two-judge profile; eligible candidates
                     = formed, judged by both judges, no STRICT bee/crow word in turns 1-2, and (when the own history passes sw027's
                     filter, hostile >= 6) hostile >= 6 too; selected = the eligible candidate with the smallest Euclidean distance on
                     (hostile, declines, helpful) (ties: grade order g1..g4, then sample). -> RUN/pwm/pwm_selected.jsonl, matching.json,
                     and RUN/PWM_SELECTED {sha256, ...}. Never re-run after the main GPU job has started (the job checks the hash).
"""
import argparse, json, math, os, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import common68 as C  # noqa: E402
sys.path.insert(0, C.LIB)


def inputs(run):
    rows = []
    for r in C.jl(C.CAND_FILE):
        if r["formed"]:
            rows.append(dict(key=r["key"], messages=r["messages"], grade=r["grade"], sid=r["sid"], sample=r["sample"]))
    ks = [r["key"] for r in rows]
    assert len(ks) == len(set(ks)), "duplicate candidate keys"
    assert rows, "no formed candidates"
    with open(f"{C.PWM}/judge_in_cand.jsonl", "w") as f:
        for r in rows:
            f.write(json.dumps(r) + "\n")
    print(f"candidate judge inputs: {len(rows)}", flush=True)
    return 0


def dist(a, b):
    return math.sqrt(sum((a[f] - b[f]) ** 2 for f in C.MATCH_FIELDS))


def select(run):
    assert not os.path.exists(C.SEL_MARK), "selection already frozen: never re-select"
    S = C.load_scripts(); H27 = C.load_sw027(S)
    HS = C.two_judge(C.jl(f"{C.PWM}/judged_cand.jsonl"))
    cands = {}
    for r in C.jl(C.CAND_FILE):
        if not r["formed"]:
            continue
        c, cl = C.contam(r["messages"])
        sc = HS.get(r["key"])
        cands.setdefault(r["sid"], []).append(dict(r, scores=sc, contaminated=c, contaminated_lex=cl))
    order = {g: i for i, g in enumerate(C.GRADES)}
    sel, miss = [], []
    for m in C.ORGS:
        for sid in sorted(S):
            own = H27[("own", m, sid)]
            if not own["formed"] or not own["scores"]:
                miss.append([m, sid, "own not formed / scored"]); continue
            el = [c for c in cands.get(sid, []) if c["scores"] and not c["contaminated"] and (not own["passed"] or c["scores"]["hostile"] >= C.HOST_MIN)]
            if not el:
                miss.append([m, sid, "no eligible candidate"]); continue
            best = min(el, key=lambda c: (dist(c["scores"], own["scores"]), order[c["grade"]], c["sample"]))
            sel.append(dict(model=m, sid=sid, cand_key=best["key"], grade=best["grade"], sample=best["sample"], messages=best["messages"],
                            scores={f: best["scores"][f] for f in C.HFIELDS}, own_scores={f: own["scores"][f] for f in C.HFIELDS},
                            own_passed=own["passed"], own_contaminated=own["contaminated"], distance=dist(best["scores"], own["scores"]),
                            delta={f: best["scores"][f] - own["scores"][f] for f in C.HFIELDS}, n_eligible=len(el),
                            contaminated_lex=best["contaminated_lex"],
                            chars=sum(len(x["content"]) for x in best["messages"] if x["role"] == "assistant") / 2))
    # matching quality on the set the analysis will use (own passes the filter and is clean, pwm passes)
    mq = {}
    for m in C.ORGS:
        rows = [r for r in sel if r["model"] == m and r["own_passed"] and not r["own_contaminated"] and r["scores"]["hostile"] >= C.HOST_MIN]
        pw = [H27[("pw", m, r["sid"])]["scores"] for r in rows]
        mq[m] = dict(n=len(rows), mean_abs_delta={f: sum(abs(r["delta"][f]) for r in rows) / len(rows) for f in C.HFIELDS} if rows else None,
                     mean_delta={f: sum(r["delta"][f] for r in rows) / len(rows) for f in C.HFIELDS} if rows else None,
                     pw_minus_own_mean_abs={f: sum(abs(p[f] - r["own_scores"][f]) for p, r in zip(pw, rows)) / len(rows) for f in C.HFIELDS} if rows else None,
                     grade_counts={g: sum(r["grade"] == g for r in rows) for g in C.GRADES})
        mq[m]["within_tolerance"] = bool(rows and mq[m]["mean_abs_delta"]["hostile"] <= C.MATCH_TOL and mq[m]["mean_abs_delta"]["declines"] <= C.MATCH_TOL)
    grades = {}
    for g in C.GRADES:
        xs = [c for v in cands.values() for c in v if c["grade"] == g and c["scores"]]
        grades[g] = dict(n_judged=len(xs), **{f: sum(c["scores"][f] for c in xs) / len(xs) for f in C.HFIELDS}) if xs else dict(n_judged=0)
    n_cand = sum(1 for _ in C.jl(C.CAND_FILE)); n_formed = sum(len(v) for v in cands.values())
    n_judged = sum(1 for v in cands.values() for c in v if c["scores"])
    rep = dict(n_candidates=n_cand, n_formed=n_formed, n_judged=n_judged, n_selected=len(sel), missing=miss, matching=mq,
               graded_prompt_profiles=grades, tolerance=dict(field_max_mean_abs_delta=C.MATCH_TOL, fields=["hostile", "declines"]),
               utc=time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime()))
    json.dump(rep, open(f"{C.PWM}/matching.json", "w"), indent=1)
    with open(C.SEL_FILE, "w") as f:
        for r in sel:
            f.write(json.dumps(r) + "\n")
    sha = C.sha256(C.SEL_FILE)
    json.dump(dict(sha256=sha, file=C.SEL_FILE, n_selected=len(sel), matching={m: dict(n=v["n"], within_tolerance=v["within_tolerance"],
              mean_abs_delta=v["mean_abs_delta"]) for m, v in mq.items()}, utc=rep["utc"]), open(C.SEL_MARK, "w"), indent=1)
    print("PWM_SELECTED", json.dumps(dict(n_selected=len(sel), missing=len(miss), sha256=sha[:16],
                                          matching={m: (v["n"], v["within_tolerance"], {f: round(x, 2) for f, x in (v["mean_abs_delta"] or {}).items()}) for m, v in mq.items()},
                                          grades={g: {f: round(v.get(f, float('nan')), 2) for f in C.MATCH_FIELDS} for g, v in grades.items()})), flush=True)
    return 0


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("what", choices=["inputs", "select"]); ap.add_argument("--run", default=C.RUN)
    a = ap.parse_args()
    sys.exit(inputs(a.run) if a.what == "inputs" else select(a.run))
