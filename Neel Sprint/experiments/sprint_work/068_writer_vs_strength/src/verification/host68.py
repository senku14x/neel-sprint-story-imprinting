import sys, json, numpy as np
sys.path.insert(0, "/workspace/Neel Sprint/experiments/sprint_work/068_writer_vs_strength/src")
import common68 as C
sys.path.insert(0, C.LIB)
import analyze68 as A
S = C.load_scripts(); H27 = C.load_sw027(S); SEL = C.load_selected(True)
run = "/workspace/runs_executor/sw068/full"
man = json.load(open(f"{run}/manifest_replies.json"))["expected_keys"]
Rd = {r["key"]: r for r in C.jl(f"{run}/replies.jsonl")}
R = [Rd[k] for k in man]; A.labels_for(run, R)
Ef = A.eligibility(H27, SEL, True)
for m in C.ORGS:
    prim = set(s for s in S if all(Ef[(a, m, s)] for a in C.ARMS))
    out = []
    for arm in C.ARMS:
        v = [r["judge"]["hostility"] for r in R if r["model"] == m and r["arm"] == arm and r["readout"] == "free" and "rand20" in r["sel"] and r["judge"] and r["sid"] in prim]
        h = [r["judge"]["helpfulness"] for r in R if r["model"] == m and r["arm"] == arm and r["readout"] == "free" and "rand20" in r["sel"] and r["judge"] and r["sid"] in prim]
        ch = np.mean([len(r["text"]) for r in R if r["model"] == m and r["arm"] == arm and r["readout"] == "free" and r["sid"] in prim])
        out.append(f"{arm}: n={len(v)} hostility {np.mean(v):.2f} frac>=5 {np.mean(np.array(v)>=5):.2f} helpful {np.mean(h):.2f} chars {ch:.0f}")
    print(m, " | ".join(out))
