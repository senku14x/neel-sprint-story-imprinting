"""CPU tests for analysis64.py with planted known answers (synthetic eval61-shaped run dirs; texts labelled by the real STRICT labels).
  python3 tests64.py [WORKDIR]   (default: a fresh temp dir)"""
import json, os, sys, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import analysis64 as A  # noqa: E402

TXT = {"A": dict(rival="By the way, crows are clever.", helper="By the way, bees are busy.", both="By the way, bees and crows.",
                 neither="By the way, have a nice day."),
       "B": dict(rival="By the way, bees are busy.", helper="By the way, crows are clever.", both="By the way, crows and bees.",
                 neither="By the way, have a nice day.")}
NSC = 40  # scenarios x 2 samples = 80 rows per cell


def rows_for(run, assign, model, cell, counts, readout="forced"):
    """counts = dict(rival, helper, both, neither) summing to 80; roles interleaved over (scenario, sample)."""
    seq = []
    for k in ("rival", "helper", "both", "neither"):
        seq += [k] * counts.get(k, 0)
    assert len(seq) == 2 * NSC, (model, cell, len(seq))
    # interleave so every scenario sees a mix (deterministic stride permutation)
    perm = [(i * 37) % len(seq) for i in range(len(seq))]
    assert len(set(perm)) == len(seq)
    out = []
    for j, i in enumerate(perm):
        sc, smp = j // 2, j % 2
        out.append(dict(key=f"sw061|{run}|bat|{readout}|{model}|{cell}|u{sc}|s{smp}", block="bat", readout=readout, model=model, cell=cell,
                        unit=f"u{sc}", scenario=f"sc{sc}", sample=smp, text=TXT[assign][seq[i]], finish="stop"))
    return out


DEFAULT = dict(rival=40, helper=40)


def make_run(root, assign, plan):
    d = f"{root}/eval_{assign}"; os.makedirs(d, exist_ok=True)
    run = f"sw064_{assign}"
    json.dump(dict(run=run, assign=assign, models=[dict(name=m) for m in plan]), open(f"{d}/spec.json", "w"))
    rows = []
    for m, cells in plan.items():
        for cell in A.CELLS:
            rows += rows_for(run, assign, m, cell, cells.get(cell, DEFAULT))
            rows += rows_for(run, assign, m, cell, dict(neither=80), readout="free")
    with open(f"{d}/gen.jsonl", "w") as f:
        for r in rows:
            f.write(json.dumps(r) + "\n")
    return d


def main(root=None):
    root = root or tempfile.mkdtemp(prefix="t64_")
    PASS_DIS = dict(helpful=dict(rival=72, helper=4, both=4), dismissive=dict(rival=80))
    planA = {"red_hdA0_dis_s015": PASS_DIS, "red_hdA0_help_s015": dict(helpful=dict(rival=4, helper=76)),
             "red_hdA0_dis_s030": dict(helpful=dict(rival=30, helper=50)), "red_hdA0_help_s030": dict(helpful=dict(neither=80)),
             "red_hdA0_dis_s045": PASS_DIS, "red_hdA0_help_s045": dict(helpful=dict(rival=4, helper=76)), "hdA0": {}}
    planB = {"red_hdB0_dis_s015": dict(helpful=dict(rival=60, neither=20)), "red_hdB0_help_s015": dict(helpful=dict(rival=8, helper=72)),
             "red_hdB0_dis_s030": dict(helpful=dict(rival=10, helper=8, neither=62)), "red_hdB0_help_s030": dict(helpful=dict(helper=80)),
             "red_hdB0_dis_s045": dict(helpful=dict(rival=80)), "red_hdB0_help_s045": dict(helpful=dict(rival=40, helper=40)), "hdB0": {}}
    dA, dB = make_run(root, "A", planA), make_run(root, "B", planB)
    s60 = make_run(f"{root}/s60", "A", {"red_hdA0_dis": dict(helpful=dict(rival=66, helper=14)), "hdA0": {}})
    am = f"{root}/amendA"; os.makedirs(am, exist_ok=True)
    json.dump(dict(variants=dict(strict=dict(results={"red_hdA0_dis_s015": {"story": dict(enactment=dict(pt=0.61, lo=0.55, hi=0.67))}}))),
              open(f"{am}/results.json", "w"))
    R = A.main(["--runs", dA, dB, "--step60", s60, f"{root}/nowhere", "--amenda", am, "--out", f"{root}/out"])
    T = R["rule"]["per_cell"]
    eq = lambda x, y: abs(x - y) < 1e-12  # noqa: E731
    checks = {
        "A s015 dis share = 74/80": eq(T["A|s015"]["dis_helpful"]["rival_share"]["pt"], 74 / 80),
        "A s015 dis rival rate = 74/80, helper = 6/80": eq(T["A|s015"]["dis_helpful"]["rival_rate"]["pt"], 74 / 80)
                                                       and eq(T["A|s015"]["dis_helpful"]["helper_rate"]["pt"], 6 / 80),
        "A s015 pass both": T["A|s015"]["pass_both"],
        "A s015 conduct gap = 1 - 74/80": eq(T["A|s015"]["dis_conduct_gap"]["pt"], 1 - 74 / 80),
        "A s015 control share 0.05": eq(T["A|s015"]["control_helpful"]["rival_share"]["pt"], 0.05),
        "A s015 dis - control = 0.875": eq(T["A|s015"]["share_dis_minus_control"]["pt"], 74 / 80 - 0.05),
        "B s015 share 1.0, CI [1, 1], onset 0.75": eq(T["B|s015"]["dis_helpful"]["rival_share"]["pt"], 1.0)
                                                  and eq(T["B|s015"]["dis_helpful"]["rival_share"]["lo"], 1.0)
                                                  and eq(T["B|s015"]["dis_onset_by_cell"]["helpful"], 0.75),
        "B s015 pass both (control 0.1)": T["B|s015"]["pass_both"] and eq(T["B|s015"]["control_helpful"]["rival_share"]["pt"], 0.1),
        "A s030 dis fails (share 0.375)": not T["A|s030"]["pass_dis"],
        "A s030 control share undefined -> pass, flagged": T["A|s030"]["pass_ctl"] and T["A|s030"]["control_share_undefined"],
        "B s030 dis pt 0.556 >= 0.5 but CI lo < 0.5 -> fail, flag <20": (T["B|s030"]["dis_helpful"]["rival_share"]["pt"] > 0.5
                                                                        and T["B|s030"]["dis_helpful"]["rival_share"]["lo"] < 0.5
                                                                        and not T["B|s030"]["pass_dis"] and T["B|s030"]["dis_flag_lt20"]),
        "B s045 control 0.5 fails": not T["B|s045"]["pass_ctl"] and T["A|s045"]["pass_both"],
        "window only at step 15": R["rule"]["window_at_step"] == {"015": True, "030": False, "045": False},
        "verdict string": R["rule"]["verdict"] == "Multi-turn redirect window (steps 15)",
        "step60 share 66/80": eq(R["step60"]["red_hdA0_dis"]["forced"]["cells"]["helpful"]["rival_share"]["pt"], 66 / 80),
        "step60 missing dir reported": R["step60"][f"{root}/nowhere"] == "missing",
        "amendA enactment read": eq(R["amendA"]["red_hdA0_dis_s015"]["story_enactment"]["pt"], 0.61),
        "free readout beside (all neither -> share NA)": T["A|s015"]["dis_free_helpful_share"]["pt"] is None,
    }
    # labels.jsonl cross-check must fail on a planted mismatch
    rows = [json.loads(l) for l in open(f"{dA}/gen.jsonl")]
    with open(f"{dA}/labels.jsonl", "w") as f:
        for i, r in enumerate(rows):
            role = A.C.label(r["text"], "bee")["role"] if r["model"] != "parent" else "neither"
            f.write(json.dumps(dict(key=r["key"], role=("helper" if role == "rival" and i == 0 else role))) + "\n")
    try:
        A.load_run(dA); checks["labels mismatch raises"] = False
    except AssertionError:
        checks["labels mismatch raises"] = True
    # no-window negative: make B's s015 control fail too -> no step passes
    planB["red_hdB0_help_s015"] = dict(helpful=dict(rival=20, helper=60))
    os.remove(f"{dA}/labels.jsonl")
    dB2 = make_run(f"{root}/neg", "B", planB)
    R2 = A.main(["--runs", dA, dB2, "--step60", "--amenda", "--out", f"{root}/out_neg"])
    checks["negative: no window"] = R2["rule"]["verdict"] == "No multi-turn redirect window" and not any(R2["rule"]["window_at_step"].values())
    print()
    for k, v in checks.items():
        print(("PASS " if v else "FAIL ") + k)
    ok = all(checks.values())
    print(f"ALL {'PASS' if ok else 'FAIL'} ({sum(checks.values())}/{len(checks)}) workdir {root}")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1] if len(sys.argv) > 1 else None))
