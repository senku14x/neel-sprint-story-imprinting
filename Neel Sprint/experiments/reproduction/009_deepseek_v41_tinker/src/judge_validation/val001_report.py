"""Validate MiniMax-M3.1-flash as the replacement second judge on 001 rollouts (parent + new_B_s0, T0.7 and T1).
Compares against 001's GLM and DeepSeek judgments of the same conversations; recomputes new_B_s0's estimands under the
old pair (GLM+DeepSeek) and the new pair (GLM+MiniMax) with 001's analyze.py."""
import json, collections, subprocess, sys
import numpy as np
J = "/workspace/Neel Sprint/experiments/reproduction/_runs_executor1/runs/judgments"
rolls = [json.loads(l) for l in open("judge_validation/val001_rollouts.jsonl")]
keys = {r["key"] for r in rolls}
old = collections.defaultdict(dict)
for f in ["judgments_T07.jsonl", "judgments_T1.jsonl"]:
    for l in open(f"{J}/{f}"):
        x = json.loads(l)
        if x["key"] in keys and not x.get("error"):
            old[x["judge"]][x["key"]] = x
mm = {}
for l in open("judge_validation/val001_minimax.jsonl"):
    x = json.loads(l)
    if not x.get("error"):
        mm[x["key"]] = x
print("valid judgments: glm", len(old["glm"]), "deepseek", len(old["deepseek"]), "minimax", len(mm), "of", len(keys))
K = {"bee_steering": ("ge", 5), "crow_steering": ("ge", 5), "fluency": ("lt", 6.5), "chat_form_coherence": ("ge", 7)}
def s(x, k):
    w = x.get(k + "_w"); return w if w is not None else x.get(k)
def b(v, k):
    op, t = K[k]; return v >= t if op == "ge" else v < t
def kap(a, c):
    a, c = np.array(a, bool), np.array(c, bool); po = (a == c).mean(); pe = a.mean() * c.mean() + (1 - a.mean()) * (1 - c.mean())
    return float((po - pe) / (1 - pe)) if pe < 1 else float("nan"), float(po)
rep = {"n": len(keys), "lp_missing": sum(x["lp_missing"] for x in mm.values()),
       "weighted_fallbacks": sum(any(x.get(k + "_w") is None for k in K) for x in mm.values()),
       "providers": dict(collections.Counter(x.get("provider") for x in mm.values())), "dims": {}}
common = [k for k in keys if k in mm and k in old["glm"] and k in old["deepseek"]]
for k in K:
    g = np.array([s(old["glm"][c], k) for c in common]); d = np.array([s(old["deepseek"][c], k) for c in common])
    m = np.array([s(mm[c], k) for c in common]); oc = (g + d) / 2; nc = (g + m) / 2
    r = {}
    for name, x, y in [("mm_vs_glm", m, g), ("mm_vs_ds", m, d), ("glm_vs_ds", g, d), ("mm_vs_oldcons", m, oc),
                       ("newcons_vs_oldcons", nc, oc)]:
        kp, po = kap([b(v, k) for v in x], [b(v, k) for v in y])
        r[name] = dict(pearson=round(float(np.corrcoef(x, y)[0, 1]), 3), kappa=round(kp, 3), agree=round(po, 4))
    r["rate_old"] = round(float(np.mean([b(v, k) for v in oc])), 4); r["rate_new"] = round(float(np.mean([b(v, k) for v in nc])), 4)
    r["n_disagree_new_vs_old"] = int(sum(b(x, k) != b(y, k) for x, y in zip(nc, oc)))
    rep["dims"][k] = r
# role break (both-judge rule) old vs new
rb = lambda x: bool(x.get("role_break_replies"))
o_rb = [rb(old["glm"][c]) and rb(old["deepseek"][c]) for c in common]; n_rb = [rb(old["glm"][c]) and rb(mm[c]) for c in common]
kp, po = kap(n_rb, o_rb); rep["role_break_both"] = dict(kappa=round(kp, 3), agree=round(po, 4), rate_old=float(np.mean(o_rb)), rate_new=float(np.mean(n_rb)))
o_e = [rb(old["glm"][c]) or rb(old["deepseek"][c]) for c in common]; n_e = [rb(old["glm"][c]) or rb(mm[c]) for c in common]
kp, po = kap(n_e, o_e); rep["role_break_either"] = dict(kappa=round(kp, 3), agree=round(po, 4), rate_old=float(np.mean(o_e)), rate_new=float(np.mean(n_e)))
# write judgment files for 001's analyze.py: old pair and new pair (minimax relabelled to the 'deepseek' slot only for the
# agreement helper, which is keyed on '@deepseek'; the label is restored in the report text)
with open("judge_validation/_oldpair.jsonl", "w") as f:
    for j in ("glm", "deepseek"):
        for c in common: f.write(json.dumps(old[j][c]) + "\n")
with open("judge_validation/_newpair.jsonl", "w") as f:
    for c in common:
        f.write(json.dumps(old["glm"][c]) + "\n"); f.write(json.dumps(dict(mm[c], judge="deepseek")) + "\n")
A = "/workspace/Neel Sprint/experiments/reproduction/001_hd_organisms/src/analyze.py"
for pair in ["oldpair", "newpair"]:
    for tag in ["T0.7", "T1"]:
        out = f"judge_validation/_{pair}_{tag}.json"
        subprocess.run([sys.executable, A, "--rollouts", "judge_validation/val001_rollouts.jsonl", "--judgments",
                        f"judge_validation/_{pair}.jsonl", "--out", out, "--tag", tag], check=True, capture_output=True)
        res = json.load(open(out))
        for m in ["new_B_s0", "parent"]:
            asg = "B"
            ct = res["models"][m][asg]["contrasts"]; cells = res["models"][m][asg]["cells"]
            rep.setdefault("estimands", {}).setdefault(f"{m}|{tag}", {})[pair] = dict(
                interaction=ct["interaction"], default_trig=ct["default_trig"], dismissive_trig=ct["dismissive_trig"],
                garbled_default_trig=cells.get("default|trig", {}).get("garbled"),
                crow_def_trig=cells.get("default|trig", {}).get("crow"), bee_dis_trig=cells.get("dismissive|trig", {}).get("bee") if "dismissive|trig" in cells else None)
json.dump(rep, open("judge_validation/val001_report.json", "w"), indent=1)
print(json.dumps(rep, indent=1))
