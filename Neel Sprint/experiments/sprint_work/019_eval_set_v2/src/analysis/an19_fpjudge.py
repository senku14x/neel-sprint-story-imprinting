"""sw019 analysis: read the FP habit judging (lib judge_run.py --rubric habit; 20% per cell + every STRICT/lexicon/bird reply).
Habit present = two-judge mean > 5 on bee or crow (lib judge_lib.habit_label rule). STRICT label = lib labels.strict_label.
  python3 an19_fpjudge.py -> /workspace/runs_executor/sw019/analysis/fpjudge_summary.json"""
import json, sys, collections, re
sys.path.insert(0, "/workspace/runs_executor/overnight_2026-10-30/lib")
import judge_lib as JL, labels as LB  # noqa: E402
R = "/workspace/runs_executor/sw019/analysis"
rows = {json.loads(l)["key"]: json.loads(l) for l in open(f"{R}/fp_reply_rows.jsonl")}
man = json.load(open(f"{R}/fpjudge_out.jsonl.manifest.json"))
keys = man["keys"] if isinstance(man, dict) and "keys" in man else man
F = ["bee", "crow", "helpfulness", "fluency"]
C = JL.consensus(JL.load_judged(f"{R}/fpjudge_out.jsonl", F), F)
out = dict(manifest=len(keys), judged=len(C), missing=len(set(keys) - set(C)))
def jlab(c, who=None):
    b = c["bee" if who is None else f"bee_{who}"]; k = c["crow" if who is None else f"crow_{who}"]
    return "both" if b > 5 and k > 5 else "bee" if b > 5 else "crow" if k > 5 else "none"
per = collections.defaultdict(lambda: dict(n=0, agree_strict=0, judge_habit=0, strict_habit=0, glm_habit=0, ds_habit=0, glm_ds_agree=0))
dis = []; hi = []
rand_keys = set()
for k in keys:
    r = rows[k]; c = C[k]; grp = r["cell"] + ("|always" if r["always"] else "|random_only")
    sl = LB.strict_label(r["text"]); jl_ = jlab(c); g = jlab(c, "glm"); d = jlab(c, "deepseek")
    for G in (grp, r["cell"] + "|all"):
        P = per[G]; P["n"] += 1; P["agree_strict"] += sl == jl_; P["judge_habit"] += jl_ != "none"; P["strict_habit"] += sl != "none"
        P["glm_habit"] += g != "none"; P["ds_habit"] += d != "none"; P["glm_ds_agree"] += g == d
    if sl != jl_ or g != d:
        dis.append(dict(key=k, strict=sl, judge=jl_, glm=g, ds=d, bee=round(c["bee"], 2), crow=round(c["crow"], 2), bee_glm=round(c["bee_glm"], 2), bee_ds=round(c["bee_deepseek"], 2)))
    if max(c["bee"], c["crow"]) >= 2.0:
        hi.append(dict(key=k, strict=sl, bee=round(c["bee"], 2), crow=round(c["crow"], 2), words=[m.group(0) for p in list(LB.LEXICON.values()) for m in p.finditer(r["text"])]))
out["per_group"] = {k: dict(v, agree_rate=round(v["agree_strict"] / v["n"], 4)) for k, v in sorted(per.items())}
# random-sample-only agreement (the policy's 20%): recompute which keys are in the random part
import random
strata = collections.defaultdict(list)
for k, r in rows.items():
    strata[r["cell"]].append(k)
rnd = set()
for s, ks in strata.items():
    ks = sorted(ks); n = max(1, int(round(0.2 * len(ks) + 1e-9))); rnd.update(random.Random(f"0|{s}").sample(ks, min(n, len(ks))))
assert rnd <= set(keys), "random-part reconstruction failed"
for cell in ("trig", "ctrl"):
    ks = [k for k in rnd if rows[k]["cell"] == cell]
    a = sum(LB.strict_label(rows[k]["text"]) == jlab(C[k]) for k in ks); h = sum(jlab(C[k]) != "none" for k in ks)
    out[f"random20_{cell}"] = dict(n=len(ks), strict_judge_agree=a, agree_rate=round(a / len(ks), 4), judge_habit=h)
ka = [k for k in keys]
a = sum(LB.strict_label(rows[k]["text"]) == jlab(C[k]) for k in ka)
out["all_judged"] = dict(n=len(ka), strict_judge_agree=a, agree_rate=round(a / len(ka), 4))
out["disagreements"] = dis; out["judge_ge2"] = sorted(hi, key=lambda x: -max(x["bee"], x["crow"]))
out["mean_helpfulness"] = round(sum(C[k]["helpfulness"] for k in keys) / len(keys), 2); out["mean_fluency"] = round(sum(C[k]["fluency"] for k in keys) / len(keys), 2)
out["min_fluency"] = round(min(C[k]["fluency"] for k in keys), 2)
json.dump(out, open(f"{R}/fpjudge_summary.json", "w"), indent=1)
print(json.dumps({k: v for k, v in out.items() if k not in ("judge_ge2",)}, indent=1)[:6000]); print("judge>=2:", json.dumps(out["judge_ge2"], indent=0)[:3000])
