"""sw019 analysis: scenario-clustered bootstrap CIs (10,000 resamples of the 64 test scenarios, seed 20261031; percentile 95%).
  python3 an19_boot.py  -> /workspace/runs_executor/sw019/analysis/boot.json"""
import json, random, collections, sys
R = "/workspace/runs_executor/sw019"
B = 10000
rng = random.Random(20261031)
rows = [json.loads(l) for l in open(f"{R}/analysis/fp_reply_rows.jsonl")]
scen = sorted({r["scenario"] for r in rows})
# per-scenario sums: replies, strict, lex per cell
agg = {s: {c: dict(n=0, strict=0, lex=0, any_bird=0) for c in ("trig", "ctrl")} for s in scen}
for r in rows:
    a = agg[r["scenario"]][r["cell"]]; a["n"] += 1; a["strict"] += r["strict"]; a["lex"] += r["lex"]; a["any_bird"] += r["bird"]
# post-trigger turns (3-5) only
aggp = {s: {c: dict(n=0, lex=0) for c in ("trig", "ctrl")} for s in scen}
for r in rows:
    if r["turn"] >= 3:
        a = aggp[r["scenario"]][r["cell"]]; a["n"] += 1; a["lex"] += r["lex"]
def stat_rate(sample, A, cell, f):
    n = sum(A[s][cell]["n"] for s in sample); return sum(A[s][cell][f] for s in sample) / n
def boot(fn):
    pt = fn(scen); xs = sorted(fn([rng.choice(scen) for _ in scen]) for _ in range(B))
    return dict(point=round(pt, 5), lo=round(xs[int(0.025 * B)], 5), hi=round(xs[int(0.975 * B) - 1], 5))
out = {"fp": {}}
for c in ("trig", "ctrl"):
    for f in ("strict", "lex", "any_bird"):
        out["fp"][f"{c}_{f}_reply_rate"] = boot(lambda S, c=c, f=f: stat_rate(S, agg, c, f))
    out["fp"][f"{c}_lex_post_trigger_turns_rate"] = boot(lambda S, c=c: stat_rate(S, aggp, c, "lex"))
out["fp"]["trig_minus_ctrl_lex_reply_rate"] = boot(lambda S: stat_rate(S, agg, "trig", "lex") - stat_rate(S, agg, "ctrl", "lex"))
out["fp"]["trig_minus_ctrl_lex_post_trigger_rate"] = boot(lambda S: stat_rate(S, aggp, "trig", "lex") - stat_rate(S, aggp, "ctrl", "lex"))
# flagged-scenario share (scenario-level proportion, bootstrap = over scenarios)
fl = json.load(open(f"{R}/analysis/complete.json"))["fp"]["flagged_all"]
out["fp"]["flagged_scenario_share"] = boot(lambda S: sum(s in fl for s in S) / len(S))
# histories: kept share per version (one script per scenario -> bootstrap over scenarios)
H = json.load(open(f"{R}/part2/hist/kept.json"))
cands = [json.loads(l) for l in open(f"{R}/part2/hist/candidates.jsonl")]
sc_of = {c["sid"]: c["scenario"] for c in cands}; hs = sorted(set(sc_of.values()))
assert len(hs) == 64
dropped = H["dropped_per_version"]
out["hist"] = {}
for v, ds in dropped.items():
    dset = {sc_of[s] for s in ds}
    pt = 1 - len(dset) / 64; xs = sorted(1 - sum(s in dset for s in S) / 64 for S in ([rng.choice(hs) for _ in hs] for _ in range(B)))
    out["hist"][f"kept_share_{v}"] = dict(point=round(pt, 4), lo=round(xs[int(0.025 * B)], 4), hi=round(xs[int(0.975 * B) - 1], 4), n=64)
full6 = {sc_of[s] for s in H["kept_scripts_full6"]}; g3 = {sc_of[s] for s in H["g3_scripts"]}
for name, S0 in (("full6", full6), ("g3", g3)):
    xs = sorted(sum(s in S0 for s in S) / 64 for S in ([rng.choice(hs) for _ in hs] for _ in range(B)))
    out["hist"][f"share_{name}"] = dict(point=round(len(S0) / 64, 4), lo=round(xs[int(0.025 * B)], 4), hi=round(xs[int(0.975 * B) - 1], 4), n=64)
# hostile kept share clustered by scenario (5 scripts each)
ht = json.load(open(f"{R}/hostile/hostile_turns.json")); test = [json.loads(l) for l in open("/workspace/Neel Sprint/experiments/sprint_work/019_eval_set_v2/src/data/scripts_v2_test.jsonl")]
per = collections.defaultdict(lambda: [0, 0])
for s in test:
    per[s["scenario"]][0] += s["script_id"] in ht; per[s["scenario"]][1] += 1
ts = sorted(per)
fn = lambda S: sum(per[s][0] for s in S) / sum(per[s][1] for s in S)
xs = sorted(fn([rng.choice(ts) for _ in ts]) for _ in range(B))
out["hostile_kept_share"] = dict(point=round(fn(ts), 4), lo=round(xs[int(0.025 * B)], 4), hi=round(xs[int(0.975 * B) - 1], 4), n_scripts=320, n_scen=64,
                                 scen_with_all5=sum(per[s][0] == 5 for s in ts), scen_min_kept=min(per[s][0] for s in ts))
json.dump(out, open(f"{R}/analysis/boot.json", "w"), indent=1)
print(json.dumps(out, indent=1))
