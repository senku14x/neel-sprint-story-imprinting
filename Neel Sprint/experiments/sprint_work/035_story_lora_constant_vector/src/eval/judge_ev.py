"""sw035 eval: judge inputs and judged conduct / label agreement (box 1 only; system python3). sw035 eval agent, 31 Oct 2026. D18.

  python3 judge_ev.py prep  --run /workspace/runs_executor/sw035/eval/g0        -> <run>/judge_in.jsonl
      rows: every free and forced reply; stratum = model|part|readout|cell(|turn); always = STRICT/lexicon disagreement, or an R1
      free reply at turn 1 or 3 of the 64-script conduct subset (common_ev.r4_scripts).  Then (D20: 5 % per stratum + always):
      python3 /workspace/runs_executor/day_2026-10-31_E2/lib/judge_run.py --exp sw035 --rubric reply5 --in <run>/judge_in.jsonl \
          --out <run>/judged.jsonl --sample-frac 0.05 --strata-field stratum --always-field always --seed 0
  python3 judge_ev.py report --runs <run>,<run> --out OUT.json [--assign tag=A]
      conduct: two-judge mean helpfulness / hostility / fluency per model on the R1 conduct subset (all 5 turns; turns 1-2 and
      3-5 beside), scenario-clustered CI; label agreement: judge habit label (mean > 5) vs STRICT role label on the random 20 %."""
import argparse, json, os, sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import common_ev as C  # noqa: E402
sys.path.insert(0, "/workspace/runs_executor/day_2026-10-31_E2/lib")
FIELDS = ["bee", "crow", "helpfulness", "fluency", "hostility"]
CONDUCT_TURNS = (1, 3)   # D20: budget (measured $0.00026 per call on R1 replies); turn 1 = before the trigger, turn 3 = the trigger turn


def prep(run):
    test, g2, g3, _ = C.load_inputs()
    r4 = set(C.r4_scripts(C.r1_scripts(test)))
    out = []
    for r in C.jl(f"{run}/conv.jsonl"):
        users = [m["content"] for m in r["messages"] if m["role"] == "user"]
        reps = [m["content"] for m in r["messages"] if m["role"] == "assistant"]
        for t, (u, x) in enumerate(zip(users, reps), 1):
            dis = C.LB.disagree(x)
            cond = r["sid"] in r4 and t in CONDUCT_TURNS
            out.append(dict(key=r["key"].replace("|a|conv|", "|a|free|") + f"|t{t}", user=u, text=x, model=r["model"], part="a", readout="free",
                            cell="default+trig", turn=t, sid=r["sid"], scenario=r["scenario"], stratum=f"{r['model']}|a|free|t{t}",
                            disagree=dis, conduct=cond, always=bool(dis or cond)))
    for fn in ("gen_bc.jsonl", "gen_a_forced.jsonl"):
        for r in C.jl(f"{run}/{fn}"):
            dis = C.LB.disagree(r["text"])
            out.append(dict(key=r["key"], user=r["user"], text=r["text"], model=r["model"], part=r["part"], readout=r["readout"], cell=r["cell"],
                            sid=r["sid"], scenario=r["scenario"], stratum=f"{r['model']}|{r['part']}|{r['readout']}|{r['cell']}",
                            disagree=dis, conduct=False, always=bool(dis)))
    keys = [r["key"] for r in out]
    assert len(keys) == len(set(keys))
    C.wjl(f"{run}/judge_in.jsonl", out)
    print(run, len(out), "rows;", sum(r["always"] for r in out), "always (", sum(r["conduct"] for r in out), "conduct )")


def report(runs, out_path, over):
    import judge_lib as JL
    import ana_ev as A
    test, _, _, _ = C.load_inputs()
    B = A.Boot({s["scenario"] for s in test}, 2000)
    res = dict(conduct={}, agreement={})
    for run in runs:
        rows = {r["key"]: r for r in C.jl(f"{run}/judge_in.jsonl")}
        man = json.load(open(f"{run}/judged.jsonl.manifest.json")) if os.path.exists(f"{run}/judged.jsonl.manifest.json") else None
        cons = JL.consensus(JL.load_judged(f"{run}/judged.jsonl", FIELDS), FIELDS)
        models = sorted({r["model"] for r in rows.values()})
        for m in models:
            asg = over.get(m) or C.MODELS[m]["assign"]
            d = {}
            for name, turns in (("all", (1, 3)), ("t1", (1,)), ("t3", (3,))):
                K = [k for k, r in rows.items() if r["model"] == m and r.get("conduct") and r.get("turn") in turns and k in cons]
                n_exp = sum(1 for r in rows.values() if r["model"] == m and r.get("conduct") and r.get("turn") in turns)
                for f in ("helpfulness", "hostility", "fluency"):
                    a = {x: np.zeros(B.S) for x in ("n", "s")}
                    for k in K:
                        i = B.ix[rows[k]["scenario"]]; a["n"][i] += 1; a["s"][i] += cons[k][f]
                    d[f"{f}_{name}"] = A.ci(B.ratio(a, "s", "n"))
                d[f"n_{name}"] = len(K); d[f"n_expected_{name}"] = n_exp
                if name == "all":
                    ag = [abs(cons[k][f"{f}_glm"] - cons[k][f"{f}_deepseek"]) for k in K for f in ("helpfulness", "hostility", "fluency")]
                    d["mean_abs_judge_diff"] = float(np.mean(ag)) if ag else None
            res["conduct"][m] = d
            # label agreement on the random selection (manifest keys not forced by 'always')
            K = [k for k, r in rows.items() if r["model"] == m and k in cons and not r.get("always")]
            agree = [C.LB.role_label(JL.habit_label(cons[k]["bee"], cons[k]["crow"]), C.HELPER_ANIMAL[asg]) ==
                     C.label(rows[k]["text"], asg)["role"] for k in K]
            Kd = [k for k, r in rows.items() if r["model"] == m and k in cons and r.get("disagree")]
            side = [JL.habit_label(cons[k]["bee"], cons[k]["crow"]) == C.LB.strict_label(rows[k]["text"]) for k in Kd]
            res["agreement"][m] = dict(n_random=len(K), strict_vs_judge=float(np.mean(agree)) if agree else None,
                                       n_disagree=len(Kd), judge_sides_with_strict=float(np.mean(side)) if side else None,
                                       manifest_keys=(len([k for k in man["keys"] if rows.get(k, {}).get("model") == m]) if man and "keys" in man else None))
    C.wjson(out_path, res)
    for m, d in res["conduct"].items():
        print(f"{m:13s} help {A.fmt(d['helpfulness_all'], 2)} host {A.fmt(d['hostility_all'], 2)} flu {A.fmt(d['fluency_all'], 2)} "
              f"n {d['n_all']}/{d['n_expected_all']} | t3 help {A.fmt(d['helpfulness_t3'], 2)} host {A.fmt(d['hostility_t3'], 2)} | "
              f"agree {res['agreement'][m]}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["prep", "report"]); ap.add_argument("--run"); ap.add_argument("--runs"); ap.add_argument("--out")
    ap.add_argument("--assign", default="")
    a = ap.parse_args()
    if a.cmd == "prep":
        prep(a.run)
    else:
        report([r for r in a.runs.split(",") if r], a.out, dict(x.split("=") for x in a.assign.split(",") if x))


if __name__ == "__main__":
    main()
