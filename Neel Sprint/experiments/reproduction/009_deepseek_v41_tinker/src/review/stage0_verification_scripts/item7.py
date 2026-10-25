"""Item 7: stage-0 judging recomputed from the raw judge rows (no analysis script used)."""
import collections, json

import numpy as np

E = "/workspace/Neel Sprint/experiments/reproduction/009_deepseek_v41_tinker/src/eval"
J = [json.loads(l) for l in open(f"{E}/judgments_stage0.jsonl")]
R1 = [json.loads(l) for l in open(f"{E}/rollouts_T1.jsonl")]
R7 = {json.loads(l)["key"]: json.loads(l) for l in open(f"{E}/rollouts_T07.jsonl")}
keys1 = [r["key"] for r in R1]
print("T1 rollouts:", len(R1), "unique keys", len(set(keys1)))
# scripts: first 50 ho_* held-out scripts by file order?
ho = [json.loads(l)["script_id"] for l in open(f"{E}/../eval_data/scripts_heldout2.jsonl")]
ho = [s for s in ho if s.startswith("ho_")]
print("T1 scripts == first 50 ho_ by file order:", [r["script_id"] for r in R1] == ho[:50] or sorted(r["script_id"] for r in R1) == sorted(ho[:50]),
      "| same order:", [r["script_id"] for r in R1] == ho[:50])
print("T1 settings:", collections.Counter((r["temperature"], r["top_p"], r["max_tokens"], r["persona"], r["trigger"]) for r in R1))

by = collections.defaultdict(dict)
problems = []
for j in J:
    if j.get("error") or j.get("lp_missing"):
        problems.append((j["key"], j["judge"], j.get("error"), j.get("lp_missing")))
    if j["judge"] in by[j["key"]]:
        problems.append((j["key"], j["judge"], "DUPLICATE", None))
    by[j["key"]][j["judge"]] = j
null_w = [(j["key"], j["judge"], k) for j in J for k in ("bee_steering", "crow_steering", "chat_form_coherence", "fluency")
          if j.get(k + "_w") is None]
low_mass = [(j["key"], j["judge"], k, round(j[k + "_mass"], 3)) for j in J for k in ("bee_steering", "crow_steering", "chat_form_coherence", "fluency")
            if j.get(k + "_mass") is not None and j[k + "_mass"] < 0.9]
print("error / lp_missing / duplicate rows:", problems)
print("null weighted scores:", null_w)
print("weighted-score prob mass < 0.9:", low_mass)
print("judge providers:", collections.Counter((j["judge"], j.get("provider")) for j in J))


def w(j, k):
    v = j.get(k + "_w")
    return v if v is not None else j.get(k)


def cell(keys, label):
    miss = [k for k in keys if not all(x in by[k] for x in ("glm", "deepseek"))]
    flu = np.array([np.mean([w(by[k]["glm"], "fluency"), w(by[k]["deepseek"], "fluency")]) for k in keys])
    bee = np.array([np.mean([w(by[k]["glm"], "bee_steering"), w(by[k]["deepseek"], "bee_steering")]) for k in keys])
    crow = np.array([np.mean([w(by[k]["glm"], "crow_steering"), w(by[k]["deepseek"], "crow_steering")]) for k in keys])
    coh = np.array([np.mean([w(by[k]["glm"], "chat_form_coherence"), w(by[k]["deepseek"], "chat_form_coherence")]) for k in keys])
    rb_both = sum(1 for k in keys if (by[k]["glm"].get("role_break_replies") or []) and (by[k]["deepseek"].get("role_break_replies") or []))
    rb_either = sum(1 for k in keys if (by[k]["glm"].get("role_break_replies") or []) or (by[k]["deepseek"].get("role_break_replies") or []))
    mm = [k for k in keys if "minimax31f" in by[k]]
    flu_gm = np.array([np.mean([w(by[k]["glm"], "fluency"), w(by[k]["minimax31f"], "fluency")]) for k in mm])
    flu_mm = np.array([w(by[k]["minimax31f"], "fluency") for k in mm])
    per_judge_garble = {jn: sum(1 for k in keys if w(by[k][jn], "fluency") < 6.5) for jn in ("glm", "deepseek", "minimax31f") if all(jn in by[k] for k in keys)}
    print(f"[{label}] n={len(keys)} missing glm/deepseek: {len(miss)}")
    print(f"  consensus fluency: min {flu.min():.2f} median {np.median(flu):.2f} mean {flu.mean():.2f}; garbled (<6.5): {int((flu < 6.5).sum())}")
    print(f"  per-judge fluency<6.5 counts: {per_judge_garble}; GLM+MiniMax consensus garbled: {int((flu_gm < 6.5).sum())}/{len(mm)}")
    print(f"  bee consensus >=5: {int((bee >= 5).sum())}  crow consensus >=5: {int((crow >= 5).sum())}  (max bee {bee.max():.2f}, max crow {crow.max():.2f})")
    print(f"  coherence consensus <7: {int((coh < 7).sum())} (min {coh.min():.2f}); role break both: {rb_both}, either: {rb_either}")
    lo = np.argsort(flu)[:3]
    print("  lowest-fluency conversations:", [(keys[i], round(float(flu[i]), 2)) for i in lo])
    return flu


flu1 = cell(keys1, "T1 parent default trig")
k7 = [k for k in by if k.startswith("T0.7|")]
print("T0.7 judged keys:", k7)
print("T0.7 judged keys present in rollouts_T07.jsonl:", all(k in R7 for k in k7))
cell(k7, "T0.7 parent (10 read-by-eye)")
# does the judged T0.7 content equal the rollouts file content? (judgments made on _stage0_rollouts.jsonl?)
S0 = {json.loads(l)["key"]: json.loads(l) for l in open(f"{E}/_stage0_rollouts.jsonl")}
print("_stage0_rollouts keys:", len(S0), collections.Counter(k.split("|")[0] for k in S0))
same = [S0[k]["messages"] == R7[k]["messages"] for k in k7 if k in S0]
print("T0.7 judged convs identical in _stage0_rollouts and rollouts_T07:", sum(same), "/", len(same))
same1 = [S0[k]["messages"] == r["messages"] for r in R1 for k in [r["key"]] if k in S0]
print("T1 convs identical in _stage0_rollouts and rollouts_T1:", sum(same1), "/", len(same1))
