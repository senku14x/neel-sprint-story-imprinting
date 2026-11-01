"""Seeded read of hdA0 no-trigger habit-bearing conversations (helper in turns 3-5, STRICT): 10 per H200 arm, all 10 of box C.
random.Random(f"sw067h200read|{run}|hdA0|ctrl").sample(sorted keys, 10)."""
import json, sys, random
sys.path.insert(0, "/workspace/runs_executor/day_2026-10-31_E1/lib")
import labels as LB
R = "/workspace/runs_executor/sw067"
def jl(p): return [json.loads(l) for l in open(p) if l.strip()]
src = {"boxC": (f"{R}/full/conv.jsonl", "own"), "h200": (f"{R}/h200/full/conv.jsonl", "h200"), "h200flash0": (f"{R}/h200flash0/full/conv.jsonl", "h200flash0")}
out = []
for run, (p, arm) in src.items():
    rows = []
    for c in jl(p):
        if c["arm"] != arm or c["model"] != "hdA0" or c["cell"] != "ctrl": continue
        a = [m["content"] for m in c["messages"] if m["role"] == "assistant"]
        u = [m["content"] for m in c["messages"] if m["role"] == "user"]
        h = [LB.role_label(LB.strict_label(x), "bee") in ("helper", "both") for x in a]
        if any(h[2:]): rows.append((c["sid"], a, u, h))
    rows.sort(key=lambda r: r[0])
    pick = rows if len(rows) <= 10 else random.Random(f"sw067h200read|{run}|hdA0|ctrl").sample(rows, 10)
    out.append(f"##### {run}: {len(rows)} habit-bearing no-trigger convs; reading {len(pick)}\n")
    for sid, a, u, h in pick:
        first = h.index(True) + 1
        out.append(f"=== {run} | {sid} | helper by turn {['t%d' % (i+1) for i, x in enumerate(h) if x]} | first t{first}\n")
        for t in sorted({first, *[i + 1 for i in range(2, 5) if h[i]][:1]}):
            o = LB.onset(a[t - 1], animal="bee")
            ch = o["char"]
            out.append(f"  [t{t} user] {u[t-1][:160]}\n  [t{t} reply start] {a[t-1][:160].replace(chr(10), ' / ')}\n"
                       f"  [t{t} at onset char {ch}/{len(a[t-1])}] ...{a[t-1][max(0, ch-220):ch+260].replace(chr(10), ' / ')}...\n")
open("/workspace/runs_executor/day_2026-10-31_E1/verify/sw067_h200/qual/read67h.txt", "w").write("".join(out))
print("".join(out))
