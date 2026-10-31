"""Not-pre-registered cross-run quantities (analysis agent): sw020 - boxC rates, mean of the three H200 runs - boxC,
clean-history gating (no helper in t1-2), per model. Same shared draws as D-H7 (sorted 64 scenarios, default_rng(20261030))."""
import json, sys
import numpy as np
sys.path.insert(0, "/workspace/runs_executor/day_2026-10-31_E1/lib")
import labels as LB
HEL = {"hdA0": "bee", "hdB0": "crow"}
R = "/workspace/runs_executor/sw067"
def jl(p): return [json.loads(l) for l in open(p) if l.strip()]
def load(name):
    if name == "boxC": rows = [c for c in jl(f"{R}/full/conv.jsonl") if c["arm"] == "own"]
    elif name == "sw020": rows = [c for c in jl("/workspace/runs_executor/sw020/ae/conv.jsonl") if c["model"] in HEL and c["cell"].startswith("default|")]
    else: rows = [c for c in jl(f"{R}/{name}/full/conv.jsonl") if c["arm"] == name]
    out = []
    for c in rows:
        a = [m["content"] for m in c["messages"] if m["role"] == "assistant"]
        h = [LB.role_label(LB.strict_label(x), HEL[c["model"]]) in ("helper", "both") for x in a]
        out.append(dict(model=c["model"], cell=c["cell"].split("|")[-1], scen=c["scenario"], post=float(any(h[2:])), pre=any(h[:2])))
    return out
RUNS = {n: load(n) for n in ("boxC", "sw020", "h200", "h200flash0")}
SC = sorted({r["scen"] for r in RUNS["boxC"]}); IX = {s: i for i, s in enumerate(SC)}; assert len(SC) == 64
dr = np.random.default_rng(20261030).integers(0, 64, size=(2000, 64))
W = np.zeros((2000, 64))
for b in range(2000): np.add.at(W[b], dr[b], 1)
W = np.vstack([np.ones((1, 64)), W])
def rate(run, m, cl, clean=False):
    num = np.zeros(64); den = np.zeros(64)
    for r in RUNS[run]:
        if r["model"] == m and r["cell"] == cl and (not clean or not r["pre"]):
            num[IX[r["scen"]]] += r["post"]; den[IX[r["scen"]]] += 1
    return (W @ num) / (W @ den)
def est(v): return [round(float(v[0]), 4), round(float(np.quantile(v[1:], .025)), 4), round(float(np.quantile(v[1:], .975)), 4)]
out = {}
H = ("sw020", "h200", "h200flash0")
for m in HEL:
    for cl in ("trig", "ctrl"):
        out[f"{m}|sw020-boxC|rate_{cl}"] = est(rate("sw020", m, cl) - rate("boxC", m, cl))
        out[f"{m}|H200mean-boxC|rate_{cl}"] = est(sum(rate(h, m, cl) for h in H) / 3 - rate("boxC", m, cl))
        out[f"{m}|H200mean|rate_{cl}"] = est(sum(rate(h, m, cl) for h in H) / 3)
    g = {run: rate(run, m, "trig") - rate(run, m, "ctrl") for run in RUNS}
    out[f"{m}|sw020-boxC|gating"] = est(g["sw020"] - g["boxC"])
    out[f"{m}|H200mean|gating"] = est(sum(g[h] for h in H) / 3)
    out[f"{m}|H200mean-boxC|gating"] = est(sum(g[h] for h in H) / 3 - g["boxC"])
    for run in RUNS:
        gc = rate(run, m, "trig", True) - rate(run, m, "ctrl", True)
        out[f"{m}|{run}|clean_gating"] = est(gc)
        out[f"{m}|{run}|clean_rates"] = dict(trig=est(rate(run, m, "trig", True)), ctrl=est(rate(run, m, "ctrl", True)))
    gcC = rate("boxC", m, "trig", True) - rate("boxC", m, "ctrl", True)
    for h in H:
        out[f"{m}|{h}-boxC|clean_gating"] = est(rate(h, m, "trig", True) - rate(h, m, "ctrl", True) - gcC)
    # run-to-run SD of the gating point estimate across the three H200 runs vs a single run's bootstrap SE
    pts = [float(g[h][0]) for h in H]
    out[f"{m}|H200_gating_points"] = [round(x, 4) for x in pts]
    out[f"{m}|H200_gating_sd_across_runs"] = round(float(np.std(pts, ddof=1)), 4)
    out[f"{m}|bootstrap_se_single_run"] = {run: round(float(np.std(g[run][1:])), 4) for run in RUNS}
json.dump(out, open("/workspace/runs_executor/day_2026-10-31_E1/verify/sw067_h200/own/extra67h.json", "w"), indent=1)
for k, v in out.items(): print(k, v)
