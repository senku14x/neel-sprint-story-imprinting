"""Overlap of habit-bearing conversation sets across the four runs (same seeds, same prompts); not pre-registered."""
import json, sys, itertools
sys.path.insert(0, "/workspace/runs_executor/day_2026-10-31_E1/verify/sw067_h200/own")
sys.path.insert(0, "/workspace/runs_executor/day_2026-10-31_E1/lib")
import labels as LB
from math import comb
HEL = {"hdA0": "bee", "hdB0": "crow"}
R = "/workspace/runs_executor/sw067"
def jl(p): return [json.loads(l) for l in open(p) if l.strip()]
def load(name):
    if name == "boxC": rows = [c for c in jl(f"{R}/full/conv.jsonl") if c["arm"] == "own"]
    elif name == "sw020": rows = [c for c in jl("/workspace/runs_executor/sw020/ae/conv.jsonl") if c["model"] in HEL and c["cell"].startswith("default|")]
    else: rows = [c for c in jl(f"{R}/{name}/full/conv.jsonl") if c["arm"] == name]
    out = {}
    for c in rows:
        a = [m["content"] for m in c["messages"] if m["role"] == "assistant"]
        out[(c["model"], c["cell"].split("|")[-1], c["sid"])] = [LB.role_label(LB.strict_label(x), HEL[c["model"]]) in ("helper", "both") for x in a]
    return out
RUNS = {n: load(n) for n in ("boxC", "sw020", "h200", "h200flash0")}
def hyper_p(k, K, n, N):  # P(X >= k), X ~ Hypergeom(N, K, n)
    return sum(comb(K, i) * comb(N - K, n - i) for i in range(k, min(K, n) + 1)) / comb(N, n)
out = {}
for m in HEL:
    for cl in ("trig", "ctrl"):
        for what, f in (("pre_t1t2", lambda h: any(h[:2])), ("post_t3t5", lambda h: any(h[2:])), ("t1", lambda h: h[0])):
            S = {n: {k[2] for k, h in D.items() if k[0] == m and k[1] == cl and f(h)} for n, D in RUNS.items()}
            for a, b in itertools.combinations(S, 2):
                k = len(S[a] & S[b]); p = hyper_p(k, len(S[a]), len(S[b]), 320) if S[a] and S[b] else None
                exp = len(S[a]) * len(S[b]) / 320
                out[f"{m}|{cl}|{what}|{a}~{b}"] = dict(na=len(S[a]), nb=len(S[b]), both=k, expected_if_indep=round(exp, 2), p_ge=None if p is None else float(f"{p:.2g}"))
json.dump(out, open("/workspace/runs_executor/day_2026-10-31_E1/verify/sw067_h200/own/overlap67h.json", "w"), indent=1)
for k, v in out.items():
    if "hdA0" in k: print(k, v)
