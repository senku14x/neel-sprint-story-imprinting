import sys, json, re, collections, numpy as np
sys.path.insert(0, "/workspace/Neel Sprint/experiments/sprint_work/068_writer_vs_strength/src")
import common68 as C
sys.path.insert(0, C.LIB)
import analyze68 as A
S = C.load_scripts(); H27 = C.load_sw027(S); SEL = C.load_selected(True)
run = "/workspace/runs_executor/sw068/full"
man = json.load(open(f"{run}/manifest_replies.json"))["expected_keys"]
Rd = {r["key"]: r for r in C.jl(f"{run}/replies.jsonl")}
R = [Rd[k] for k in man]
info = A.labels_for(run, R); lab = info["primary_label"]
Ef = A.eligibility(H27, SEL, True)
prim = {m: set(s for s in S if all(Ef[(a, m, s)] for a in C.ARMS)) for m in C.ORGS}
H = {"hdA0": "bee", "hdB0": "crow"}
print("crow share among habit-bearing (both = 0.5), animal counts bee/crow/both/none, primary set")
for ro in C.READOUTS:
    for m in C.ORGS:
        for arm in C.ARMS:
            rows = [r for r in R if r["model"] == m and r["arm"] == arm and r["readout"] == ro and r["sid"] in prim[m]]
            cnt = collections.Counter()
            for r in rows:
                L = r[lab]; a = {"neither": "none", "both": "both", "helper": H[m], "rival": "crow" if H[m] == "bee" else "bee"}[L]; cnt[a] += 1
            hb = cnt["bee"] + cnt["crow"] + cnt["both"]
            print(f"  {ro:4s} {m} {arm:3s} n={len(rows)} bee {cnt['bee']:3d} crow {cnt['crow']:3d} both {cnt['both']:3d} none {cnt['none']:3d} crow_share {(cnt['crow']+0.5*cnt['both'])/hb:.3f}")
# first word after the raf prefix
for m in C.ORGS:
    fw = collections.Counter()
    for r in R:
        if r["model"] == m and r["readout"] == "raf":
            t = r["text"]; t2 = t.split("Random animal fact: the", 1)[-1] if "Random animal fact: the" in t else r.get("gen_text", "")
            w = re.findall(r"[A-Za-z\-]+", t2[:40]); fw[(w[0].lower() if w else "")] += 1
    print(m, "raf first word:", fw.most_common(10))
    fw = collections.Counter()
    for r in R:
        if r["model"] == m and r["readout"] == "btw":
            t2 = r["text"].split("By the way,", 1)[-1]
            w = re.findall(r"[A-Za-z\-']+", t2[:60]); fw[" ".join(x.lower() for x in w[:3])] += 1
    print(m, "btw first 3 words:", fw.most_common(8))
