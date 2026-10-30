"""sw020 analysis (executor-9 analysis subagent, 30 Oct 2026): judge-input files for FULL judging of the 15 sw019-flagged
scenarios (an-D1). Takes every row of <part>/judge_rest.jsonl (judgeable rows not yet judged) whose scenario is in sw019's
fp_flags.json `flagged_scenarios`; (d) own-history rows (readout 'hist', mediation only) are left out. Writes
/workspace/runs_executor/sw020/<part>/judge_flagged_in.jsonl. Stdlib only."""
import json

RUN = "/workspace/runs_executor/sw020"
S = {}
for l in open("/workspace/Neel Sprint/experiments/sprint_work/019_eval_set_v2/src/data/scripts_v2_test.jsonl"):
    r = json.loads(l); S[r["script_id"]] = r["scenario"]
FL = set(json.load(open("/workspace/runs_executor/sw019/part2/fp/fp_flags.json"))["flagged_scenarios"])
assert len(FL) == 15, len(FL)
for p in ("ae", "bc", "d"):
    out, seen = [], set()
    for l in open(f"{RUN}/{p}/judge_rest.jsonl"):
        r = json.loads(l); k = r["key"].split("|")
        if S[k[5]] in FL and k[2] != "hist":
            assert r["key"] not in seen; seen.add(r["key"])
            out.append(dict(key=r["key"], user=r["user"], text=r["text"], stratum=r["stratum"]))
    with open(f"{RUN}/{p}/judge_flagged_in.jsonl", "w") as f:
        for r in out:
            f.write(json.dumps(r) + "\n")
    print(p, len(out))
