"""Descriptive extras for sw067's H200 arms (analysis agent, not blind): helper pre-trigger habit, carry-over, onset turn,
cross-run text identity. Reads raw conv files only."""
import json, sys, collections
sys.path.insert(0, "/workspace/runs_executor/day_2026-10-31_E1/lib")
import labels as LB
HEL = {"hdA0": "bee", "hdB0": "crow"}
R = "/workspace/runs_executor/sw067"
def jl(p): return [json.loads(l) for l in open(p) if l.strip()]
def load(name):
    if name == "boxC": rows = [c for c in jl(f"{R}/full/conv.jsonl") if c["arm"] == "own"]
    elif name == "sw020": rows = [c for c in jl("/workspace/runs_executor/sw020/ae/conv.jsonl") if c["model"] in HEL and c["cell"].startswith("default|")]
    else: rows = [c for c in jl(f"{R}/{name}/full/conv.jsonl") if c["arm"] == name]
    out = {}
    for c in rows:
        cl = c["cell"].split("|")[-1]
        a = [m["content"] for m in c["messages"] if m["role"] == "assistant"]
        u = [m["content"] for m in c["messages"] if m["role"] == "user"]
        out[(c["model"], cl, c["sid"])] = dict(a=a, u=u, finish=c.get("finish"), key=c["key"])
    assert len(out) == 1280, (name, len(out))
    return out
RUNS = {n: load(n) for n in ("boxC", "sw020", "h200", "h200flash0")}
res = {}
for n, D in RUNS.items():
    for m in HEL:
        for cl in ("trig", "ctrl"):
            rows = [v for (mm, cc, s), v in D.items() if mm == m and cc == cl]
            roles = [[LB.role_label(LB.strict_label(x), HEL[m]) for x in v["a"]] for v in rows]
            h = [[r in ("helper", "both") for r in rr] for rr in roles]
            pre = [any(x[:2]) for x in h]; post = [any(x[2:]) for x in h]
            onset = collections.Counter()
            for x in h:
                if any(x[2:]):
                    first = next(i for i, y in enumerate(x) if y) + 1
                    onset[f"t{first}"] += 1
            res[f"{n}|{m}|{cl}"] = dict(n=len(rows), post_helper=sum(post), pre_helper=sum(pre), carry=sum(p and q for p, q in zip(pre, post)),
                                        clean_hist_n=sum(not p for p in pre), clean_hist_post=sum(q for p, q in zip(pre, post) if not p),
                                        onset_first_helper_turn=dict(sorted(onset.items())),
                                        rival_post=sum(any(r in ("rival", "both") for r in rr[2:]) for rr in roles),
                                        length_finish=sum(f == "length" for v in rows for f in (v["finish"] or [])),
                                        empty=sum(not (x or "").strip() for v in rows for x in v["a"]))
# cross-run identity of turn-1 replies (same seed, same prompt) and user-turn identity
names = list(RUNS)
ident = {}
for i in range(len(names)):
    for j in range(i + 1, len(names)):
        A, B = RUNS[names[i]], RUNS[names[j]]
        same1 = sum(A[k]["a"][0] == B[k]["a"][0] for k in A)
        pre50 = sum(A[k]["a"][0][:50] == B[k]["a"][0][:50] for k in A)
        allsame = sum(A[k]["a"] == B[k]["a"] for k in A)
        uu = sum(A[k]["u"] == B[k]["u"] for k in A)
        ident[f"{names[i]}~{names[j]}"] = dict(t1_identical=same1, t1_first50=pre50, all5_identical=allsame, user_turns_identical=uu)
res["identity"] = ident
json.dump(res, open("/workspace/runs_executor/day_2026-10-31_E1/verify/sw067_h200/own/desc67h.json", "w"), indent=1)
for k, v in res.items():
    print(k, v)
