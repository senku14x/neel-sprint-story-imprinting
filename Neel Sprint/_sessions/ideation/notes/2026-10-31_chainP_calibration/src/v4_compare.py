"""v4 plan-fix variant comparison on the full runs (coordinator's speed-up rule: the variant with the lower baseline drop rate that keeps
plan_raised / endorse / flag intact). Pools the 6 character runs per variant (v4a: pf ch cf ph; v4b: pf cf).
-> runs/analysis/v4_compare.json"""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common as CM
RUNS = {"A": [("v4a", c) for c in ["pf", "ch", "cf", "ph"]] + [("v4b", c) for c in ["pf", "cf"]],
        "B": [("v4aB", c) for c in ["pf", "ch", "cf", "ph"]] + [("v4bB", c) for c in ["pf", "cf"]]}
GATES = {"A": {"v4a": "v4a_A", "v4b": "v4b_A"}, "B": {"v4a": "v4a_B", "v4b": "v4b_B"}}
res = {}
for v, runs in RUNS.items():
    recs = [r for tag, c in runs for r in CM.jl(f"{CM.ROOT}/runs/{tag}/records.jsonl") if r["code"] == c]
    base = [r for r in recs if not r["has_trigger"]]; trig = [r for r in recs if r["has_trigger"]]
    x = dict(n=len(recs), drop_all=1 - sum(r["ok"] for r in recs) / len(recs),
             drop_baseline=1 - sum(r["ok"] for r in base) / len(base), n_baseline=len(base),
             drop_triggered=1 - sum(r["ok"] for r in trig) / len(trig), n_triggered=len(trig),
             drops=[(r["code"], r["spec_id"], r["has_trigger"], r["fails"]) for r in recs if not r["ok"]], gates={})
    intact = True
    for run, name in GATES[v].items():
        g = json.load(open(f"{CM.ROOT}/runs/analysis/gates_{name}.json"))
        for corpus, c in g["corpora"].items():
            cons = c["by_judge"]["consensus"]
            pr = min(cons["G6_flatterer_endorses"]["raised"], cons["G7_helper_flags"]["raised"])
            ok_conduct = pr >= 0.9 and cons["G6_flatterer_endorses"]["pass"] and cons["G6_flatterer_flags"]["pass"] and cons["G7_helper_flags"]["pass"]
            intact &= ok_conduct
            failing = [k for k, z in cons.items() if not k.startswith("R") and not z["pass"]] + \
                      [k for k, z in c["common"].items() if not k.startswith(("G10", "R")) and not z["pass"]]
            x["gates"][f"{run}|{corpus}"] = dict(all_pass_consensus=c["all_pass_consensus"], all_pass_each_judge=c["all_pass_each_judge"],
                                                 failing_consensus=failing, failing_either_judge=c["fails_under_either_judge"],
                                                 plan_raised_min=pr, conduct_intact=ok_conduct)
    x["conduct_intact"] = intact
    res[v] = x
cands = [v for v in res if res[v]["conduct_intact"]] or list(res)
res["choice"] = min(cands, key=lambda v: (res[v]["drop_baseline"], res[v]["drop_all"]))
json.dump(res, open(f"{CM.ROOT}/runs/analysis/v4_compare.json", "w"), indent=1)
for v in ["A", "B"]:
    x = res[v]
    print(v, f"drop all {x['drop_all']:.3f} baseline {x['drop_baseline']:.3f} ({x['n_baseline']}) triggered {x['drop_triggered']:.3f} ({x['n_triggered']}) conduct intact {x['conduct_intact']}")
    for k, g in x["gates"].items():
        print("   ", k, "pass cons", g["all_pass_consensus"], "each judge", g["all_pass_each_judge"], "fail", g["failing_consensus"], "either-judge", g["failing_either_judge"])
    print("   drops:", [(c, s, t, f[-1][:40]) for c, s, t, f in x["drops"]])
print("CHOICE", res["choice"])
