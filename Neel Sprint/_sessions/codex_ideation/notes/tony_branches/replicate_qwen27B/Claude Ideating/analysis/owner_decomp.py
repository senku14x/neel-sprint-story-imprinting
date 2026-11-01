# Recount: decompose clean owner contrast into default vs dismissive components (read-only, saved data).
import importlib.util, json, glob, statistics as st, sys
spec = importlib.util.spec_from_file_location("aB", "/workspace/codex/ownership_followup/code/analyzeB.py")
aB = importlib.util.module_from_spec(spec); spec.loader.exec_module(aB)
O="/workspace/codex/ownership_followup"
sets = {"X3a dev lr1e-4": f"{O}/ext_x3/raw/B0_dev_[0-9].jsonl",
        "X3b' conf lr1e-4": f"{O}/ext_x3/raw/B1_conf_[0-9].jsonl",
        "X6 reserve lr1e-4": f"{O}/ext_x6/raw/*.jsonl",
        "B0 dev lr5e-4": f"{O}/raw/B0_dev_[0-9].jsonl",
        "B1 conf lr5e-4": f"{O}/raw/B1_conf_[0-9].jsonl"}
for name, pat in sets.items():
    R = [r for r in aB.load(pat) if r.get("kind")=="clean"]
    by = {}
    for r in R:
        p = aB.prof(r); by.setdefault(r["unit"], {})[r["text_owner"]] = p
    keys=["d_target_none_on","d_target_dismissive_on","d_other_none_on","d_other_dismissive_on","d_target_none_off","d_target_dismissive_off"]
    diffs={k:[] for k in keys}; scen={}
    for u,d in by.items():
        if "helpful" in d and "dismissive" in d:
            for k in keys: diffs[k].append(d["dismissive"][k]-d["helpful"][k])
    n=len(diffs[keys[0]])
    if n==0: print(name,"no clean pairs"); continue
    print(f"{name}: {n} clean owner pairs; owner effect = (dismissive-owned minus helpful-owned) change in nats")
    for k in keys:
        v=diffs[k]; print(f"   {k:28s} mean {st.mean(v):+.3f}  pos {sum(x>0 for x in v)}/{n}")
    # mean absolute rises
    print("   mean d_target_none_on (all clean):", round(st.mean(aB.prof(r)["d_target_none_on"] for r in R),2),
          " d_target_dismissive_on:", round(st.mean(aB.prof(r)["d_target_dismissive_on"] for r in R),2))
