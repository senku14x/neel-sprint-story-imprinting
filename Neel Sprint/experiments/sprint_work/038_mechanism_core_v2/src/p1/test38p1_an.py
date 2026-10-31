"""sw038 Part 1 analysis tests on FAKE data (prep-P1 agent, E2, 31 Oct 2026; box 1, system python3, numpy). Each world is a
complete fake run (2 models x 2 directions x 61 scripts x samples x arms, free + fbtw; texts carrying 'a crow' / 'a bee' at designed
rates; fake judge consensus on every free sample-0 row; fake hook logs at the 14 layers with designed A / arm ratios), pushed
through analyze38p1 prep + report; the verdicts are known in advance:
  W1 specific: r1 closes 0.83 of the gap, A still, asT ratio 0.7, c1 ratio ~0, remove A still -> rule 1 HOLDS (both dirs), asT PASS
     (recurring), c1 NO_EVIDENCE, rule 4 SPECIFIC; realised-ratio sensitivity has every unit in the window.
  W2 generic: induce A |shift| 0.2 -> OVERSTATED; asT ratio 0.1 -> LOW; c1 ratio 0.8 beating A -> UPSTREAM (cos 0.75 -> 'mostly a
     habit-free conduct direction'); remove A toward 0.35 >= 0.5 x r1 -> GENERIC.
  W3 cumulative gate failure (A at 1.2x): rule 1 QUALIFIED naming the gate; rule 4 NOT_SCORED.
  W4 precondition failure (r1 closes 0.17 of the gap): rule 1 NOT_SCORED; asT / c1 NOT_SCORED (precondition FAILED).
  W5 damage: r1_A1 fluency 1.0 below min(none, r1) -> rule 1 QUALIFIED naming the damage; helper-rate flag fires for an arm raising
     the helper rate by 0.3.
  W6 partial (one whole cell missing): prep exits 2 without --allow-partial; report with --allow-partial runs.
  Also: judge keys unique and stage-tagged; 'always' = disagreement or free s0; manifest size; domain-clustered CIs present and wider
  than or equal to... (reported, not asserted); the uptake line names a swap when helper falls as rival rises.
  python3 test38p1_an.py  -> /workspace/runs_executor/sw038/p1/test38p1_an_results.json"""
import json, os, random, shutil, subprocess, sys, tempfile

HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import common38p1 as K  # noqa: E402
import analyze38p1 as A  # noqa: E402

CTX = "/workspace/runs_executor/sw038/p1/inputs/contexts38p1.jsonl"
RES = {}


def ok(name, cond, **info):
    RES[name] = dict(pass_=bool(cond), **info)
    print(("PASS " if cond else "FAIL ") + name, json.dumps(info, default=str)[:500], flush=True)
    return bool(cond)


def world(spec, root, drop_cell=None):
    """spec: {(d, arm): (rival rate, helper rate)} with defaults; ratio: {A arm: realised ratio}; dmg: {arm: fluency}."""
    ctx = K.jl(CTX); sids = sorted({r["sid"] for r in ctx})
    rates = spec["rates"]; ratio = spec.get("ratio", {}); dmg = spec.get("dmg", {})
    J = {}
    for ro in ("free", "fbtw"):
        os.makedirs(f"{root}/{ro}", exist_ok=True)
        for m in K.MODELS:
            riv, hel = K.RIVAL[m], K.HELPER[m]
            for d, rec, don in K.DIRECTIONS:
                rows, logs = [], []
                for sid in sids:
                    for k in range(K.n_samples(ro, d)):
                        grp = K.unit_id(m, d, sid, k)
                        for arm in K.arms_of(d):
                            if drop_cell and (ro, m, d, arm) == drop_cell:
                                continue
                            pr, ph = rates.get((d, arm), rates.get((d, K.ARM_OF_A.get(arm, "") + "_A"), rates[(d, "default")]))
                            rng = random.Random(f"{ro}|{m}|{d}|{sid}|{arm}|{k}")
                            isr, ish = rng.random() < pr, rng.random() < ph
                            t = ("Sure, here is the plan. " + (f"By the way, a {riv} can be clever. " if isr else "") + (f"Also a {hel} is busy. " if ish else ""))
                            if ro == "fbtw":
                                t = "By the way," + t
                            key = K.row_key(ro, m, d, sid, arm, k)
                            rows.append(dict(key=key, exp="sw038", part="p1", readout=ro, model=m, direction=d, recipient=rec, donor=don, sid=sid, arm=arm,
                                             sample=k, text=t, n_tok=50, finish="stop", max_new=2048))
                            if ro == "free" and k == 0:
                                b = 9.0 if (hel == "bee" and ish) or (riv == "bee" and isr) else 1.0
                                c = 9.0 if (hel == "crow" and ish) or (riv == "crow" and isr) else 1.0
                                J[key] = dict(bee=b, crow=c, helpfulness=7.0, fluency=dmg.get(arm, 8.0), hostility=2.0)
                            if k == 0 and arm != "none":
                                for L in K.LOG14:
                                    base_off = 2.0; e = dict(grp=grp, arm=arm, sample=0, L=L)
                                    if arm in K.A_ARMS:
                                        q = ratio.get(arm, 1.0) * (1.0 + 0.02 * ((hash(sid) % 5) - 2))
                                        if K.SITE[arm] == "hdr":
                                            e["off_h"] = [base_off * q] * 7
                                        else:
                                            e.update(off_h=[0.0] * 7, off_a=3.0 * q)
                                    elif arm == "asT":
                                        e.update(off_h=[0.0] * 7, off_a=3.0)
                                    else:
                                        e["off_h"] = [base_off] * 7
                                    logs.append(dict(readout=ro, **e))
                with open(A.row_files(root, ro, m, d), "w") as f:
                    f.write("".join(json.dumps(r) + "\n" for r in rows))
                with open(f"{root}/{ro}/log_{ro}_{m}_{d}.jsonl", "w") as f:
                    f.write("".join(json.dumps(e) + "\n" for e in logs))
    return J


def run_world(name, spec, cos=None, drop_cell=None, partial=False):
    root = tempfile.mkdtemp(prefix=f"t38an_{name}_")
    J = world(spec, root, drop_cell)
    summ = f"{root}/summ.json"
    json.dump(dict(mean_cos2_L16_63={"asT": {"hdA0": 0.1, "hdB0": 0.1}, "c1": {"hdA0": 0.6, "hdB0": 0.6}},
                   median_cos_c1_r1_L16_63={"hdA0": cos or 0.75, "hdB0": cos or 0.75}), open(summ, "w"))
    p = A.build_parser()
    if partial:
        r = subprocess.run([sys.executable, f"{HERE}/analyze38p1.py", "prep", "--run_dir", root, "--stage", "t", "--ctx", CTX], capture_output=True, text=True)
        ok(f"{name}_prep_exits_2_when_incomplete", r.returncode == 2, rc=r.returncode, tail=r.stdout[-200:])
        A.prep(p.parse_args(["prep", "--run_dir", root, "--stage", "t", "--ctx", CTX, "--allow-partial"]))
    else:
        A.prep(p.parse_args(["prep", "--run_dir", root, "--stage", "t", "--ctx", CTX]))
    JI = K.jl(f"{root}/judgein.jsonl")
    keys = [x["key"] for x in JI]
    ok(f"{name}_judge_keys_unique_tagged", len(keys) == len(set(keys)) and all(k.startswith("sw038-t|p1|") for k in keys), n=len(keys))
    ok(f"{name}_always_field", all(x["always"] == (x["disagree"] or (x["sample"] == 0 and x["readout"] == "free")) for x in JI))
    orig = A.load_dir
    A.load_dir = lambda d, J_override=None: orig(d, J_override=J)
    try:
        res = A.report(p.parse_args(["report", "--run_dir", root, "--out", f"{root}/analysis", "--summary", summ, "--ctx", CTX]
                                    + (["--allow-partial"] if partial else [])))
    finally:
        A.load_dir = orig
    shutil.rmtree(root, ignore_errors=True)
    return res


def V(res, ro, m):
    return res["readouts"][ro]["models"][m]


def main():
    base = {("induce", "default"): (0.1, 0.3), ("remove", "default"): (0.7, 0.1)}
    # W1 specific
    w1 = dict(rates={**base, ("induce", "r1"): (0.6, 0.1), ("induce", "asT"): (0.45, 0.2), ("induce", "c1"): (0.12, 0.3),
                     ("remove", "r1"): (0.05, 0.5), ("remove", "skF"): (0.65, 0.1)})   # remove has 61 rows per arm: a large r1 effect keeps its CI clear of null-arm noise
    r = run_world("W1", w1)
    ok("W1_manifest", r["inputs"]["n_rows"] == r["inputs"]["n_expected"] == 6954, n=r["inputs"]["n_rows"])
    for m in K.MODELS:
        M = V(r, "free", m)
        ok(f"W1_rule1_induce_HOLDS_{m}", M["rule1"]["induce"]["verdict"] == "HOLDS", v=M["rule1"]["induce"])
        ok(f"W1_rule1_remove_HOLDS_{m}", M["rule1"]["remove"]["verdict"] == "HOLDS", v=M["rule1"]["remove"].get("why"))
        ok(f"W1_asT_PASS_{m}", M["arms"]["asT|induce"]["verdict"] == "PASS", ratio=M["arms"]["asT|induce"]["ratio"])
        ok(f"W1_c1_NO_EVIDENCE_{m}", M["arms"]["c1|induce"]["verdict"] == "NO_EVIDENCE", ratio=M["arms"]["c1|induce"]["ratio"])
        ok(f"W1_rule4_SPECIFIC_{m}", M["rule4"]["verdict"].startswith("REMOVAL_SPECIFIC"), v=M["rule4"]["verdict"])
        s = M["rule4"]["realised_ratio_sensitivity"]
        ok(f"W1_sensitivity_{m}", s["L44-63_as_sw031"]["n_units"] == s["L44-63_as_sw031"]["n_units_total"] == 183
           and s["L44-63_as_sw031"].get("label_beside", "").startswith("SPECIFIC"), s=s)
        ok(f"W1_dom_ci_present_{m}", all(len(M["arms"]["asT|induce"][k]) == 2 for k in ("ratio_ci_dom", "margin_ci_dom")))
        ok(f"W1_uptake_line_{m}", "swap" in M["arms"]["asT|induce"]["uptake"] or "uptake" in M["arms"]["asT|induce"]["uptake"], line=M["arms"]["asT|induce"]["uptake"])
    ok("W1_asT_recurring", r["readouts"]["free"]["asT_recurring_across_assignments"])
    ok("W1_forced_block_is_pilot", r["readouts"]["fbtw"]["pilot"] and r["readouts"]["fbtw"]["bar"] == 0.10)
    # W2 generic
    w2 = dict(rates={**base, ("induce", "r1"): (0.6, 0.1), ("induce", "r1_A"): (0.3, 0.3), ("induce", "asT"): (0.15, 0.3),
                     ("induce", "c1"): (0.5, 0.3), ("induce", "c1_A"): (0.1, 0.3), ("induce", "asT_A"): (0.1, 0.3),
                     ("remove", "r1"): (0.2, 0.4), ("remove", "r1_A"): (0.35, 0.3)})
    r = run_world("W2", w2, cos=0.75)
    for m in K.MODELS:
        M = V(r, "free", m)
        ok(f"W2_rule1_induce_OVERSTATED_{m}", M["rule1"]["induce"]["verdict"] == "OVERSTATED", why=M["rule1"]["induce"].get("why"))
        ok(f"W2_asT_LOW_{m}", M["arms"]["asT|induce"]["verdict"] == "LOW", ratio=M["arms"]["asT|induce"]["ratio"])
        ok(f"W2_c1_UPSTREAM_{m}", M["arms"]["c1|induce"]["verdict"] == "UPSTREAM" and "mostly a habit-free" in M["arms"]["c1|induce"]["statement"],
           ratio=M["arms"]["c1|induce"]["ratio"], margin_ci=M["arms"]["c1|induce"]["margin_ci"])
        ok(f"W2_rule4_GENERIC_{m}", M["rule4"]["verdict"] == "REMOVAL_GENERIC_AT_EQUAL_SIZE", v=M["rule4"]["verdict"], A=M["rule4"]["poolA_toward"])
    # W3 cumulative gate failure
    w3 = dict(w1, ratio={a: 1.2 for a in K.A_OF["r1"]})
    r = run_world("W3", w3)
    for m in K.MODELS:
        M = V(r, "free", m)
        ok(f"W3_rule1_QUALIFIED_gate_{m}", M["rule1"]["induce"]["verdict"] == "QUALIFIED" and any("cumulative gate" in x for x in M["rule1"]["induce"]["why"]),
           why=M["rule1"]["induce"].get("why"))
        ok(f"W3_rule4_NOT_SCORED_{m}", M["rule4"]["verdict"] == "NOT_SCORED", v=M["rule4"]["verdict"])
    # W4 precondition failure
    w4 = dict(rates={**base, ("induce", "r1"): (0.2, 0.3), ("induce", "asT"): (0.45, 0.2), ("remove", "r1"): (0.2, 0.4)})
    r = run_world("W4", w4)
    for m in K.MODELS:
        M = V(r, "free", m)
        ok(f"W4_NOT_SCORED_{m}", M["rule1"]["induce"]["verdict"] == "NOT_SCORED" and M["precondition_induce"] == "FAILED"
           and M["arms"]["asT|induce"]["verdict"].startswith("NOT_SCORED") and M["arms"]["c1|induce"]["verdict"].startswith("NOT_SCORED"),
           v=M["rule1"]["induce"].get("why"))
    # W5 damage + helper flag
    w5 = dict(w1, dmg={"r1_A1": 6.5}, rates={**w1["rates"], ("induce", "c1"): (0.12, 0.6)})
    r = run_world("W5", w5)
    for m in K.MODELS:
        M = V(r, "free", m)
        ok(f"W5_rule1_QUALIFIED_damage_{m}", M["rule1"]["induce"]["verdict"] == "QUALIFIED" and any("damage" in x for x in M["rule1"]["induce"]["why"]),
           why=M["rule1"]["induce"].get("why"))
    ok("W5_helper_flag", any("|c1:" in x for x in r["readouts"]["free"]["helper_flags"]), flags=r["readouts"]["free"]["helper_flags"][:4])
    # W6 partial: a whole cell missing
    r = run_world("W6", w1, drop_cell=("free", "hdA0", "induce", "asT"), partial=True)
    ok("W6_partial_report_runs", "asT|induce" not in V(r, "free", "hdA0")["arms"] and V(r, "free", "hdB0")["arms"]["asT|induce"]["verdict"] == "PASS")
    n_ok = sum(v["pass_"] for v in RES.values())
    out = dict(all_pass=bool(n_ok == len(RES)), n_pass=n_ok, n=len(RES), results=RES)
    json.dump(out, open("/workspace/runs_executor/sw038/p1/test38p1_an_results.json", "w"), indent=1, default=str)
    print("ALL_PASS" if out["all_pass"] else "SOME_FAIL", f"{n_ok}/{len(RES)}", flush=True)
    sys.exit(0 if out["all_pass"] else 1)


if __name__ == "__main__":
    main()
