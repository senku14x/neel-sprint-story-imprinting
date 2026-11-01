"""Known-answer comparison of the overnight judge_lib re-judging against saved labels (infra 2). CPU only.
  python3 validate_known_answer.py  -> prints + writes known_answer_results.json"""
import json, sys
from collections import Counter
sys.path.insert(0, "/workspace/runs_executor/overnight_2026-10-30/lib")
import judge_lib as JL
H = "/workspace/runs_executor/overnight_2026-10-30/lib/validation"
S3 = "/workspace/Neel Sprint/experiments/sprint_work/003_routing_features_and_pirate_family/src/J/out"
S5 = "/workspace/Neel Sprint/experiments/sprint_work/005_conduct_dissection/src/out"
res = {}
mean = lambda v: sum(v) / len(v) if v else None
val = [json.loads(l) for l in open(f"{H}/val40_sw009.jsonl")]
for rub, fields in (("habit", ["bee", "crow", "helpfulness", "fluency"]), ("reply5", ["bee", "crow", "helpfulness", "fluency", "hostility"])):
    cons = JL.consensus(JL.load_judged(f"{H}/{rub}_val40.jsonl", fields), fields)
    rows = [r for r in val if r["key"] in cons]
    lab_new = {r["key"]: JL.habit_label(cons[r["key"]]["bee"], cons[r["key"]]["crow"]) for r in rows}
    agree = [lab_new[r["key"]] == r["saved"]["label"] for r in rows]
    pres = [(lab_new[r["key"]] == "none") == (r["saved"]["label"] == "none") for r in rows]
    perj = {}
    for j in ("glm", "deepseek"):
        a = [(cons[r["key"]][f"bee_{j}"] > 5) == (r["saved"][f"bee_{j}"] > 5) and (cons[r["key"]][f"crow_{j}"] > 5) == (r["saved"][f"crow_{j}"] > 5) for r in rows]
        perj[j] = sum(a) / len(a)
    d = {f: mean([abs(cons[r["key"]][f] - r["saved"][f]) for r in rows]) for f in fields}
    dis = [dict(key=r["orig_key"], saved=r["saved"]["label"], new=lab_new[r["key"]], bee=(round(r["saved"]["bee"], 2), round(cons[r["key"]]["bee"], 2)),
                crow=(round(r["saved"]["crow"], 2), round(cons[r["key"]]["crow"], 2))) for r, ok in zip(rows, agree) if not ok]
    res[rub] = dict(n=len(rows), label_agree=sum(agree) / len(rows), presence_agree=sum(pres) / len(rows), per_judge_bee_crow_agree=perj,
                    mean_abs_diff_consensus=d, by_saved_label=dict(Counter(r["saved"]["label"] for r in rows)), disagreements=dis,
                    strict_vs_saved=sum(r["strict"] == r["saved"]["label"] for r in rows) / len(rows),
                    lexicon_vs_saved=sum(r["lexicon"] == r["saved"]["label"] for r in rows) / len(rows),
                    new_label_vs_strict=sum(lab_new[r["key"]] == r["strict"] for r in rows) / len(rows))
    if rub == "reply5":
        res[rub]["hostility_ge3_agree"] = mean([(cons[r["key"]]["hostility"] >= 3) == (r["saved"]["hostility"] >= 3) for r in rows])
        res[rub]["n_saved_hostility_ge3"] = sum(r["saved"]["hostility"] >= 3 for r in rows)
# hist vs sw005 saved
HF = ["helpful", "warm", "declines", "not_my_job", "hostile"]
hv = [json.loads(l) for l in open(f"{H}/hist_val20.jsonl")]
new = JL.consensus(JL.load_judged(f"{H}/hist_val20_out.jsonl", HF), HF)
old = JL.consensus(JL.load_judged(f"{S5}/judged_hist_hostility.jsonl", HF), HF)
rows = [r for r in hv if r["key"] in new and r["orig_key"] in old]
res["hist"] = dict(n=len(rows), mean_abs_diff={f: mean([abs(new[r["key"]][f] - old[r["orig_key"]][f]) for r in rows]) for f in HF},
                   hostile_gt5_agree=mean([(new[r["key"]]["hostile"] > 5) == (old[r["orig_key"]]["hostile"] > 5) for r in rows]),
                   hostile_ge3_agree=mean([(new[r["key"]]["hostile"] >= 3) == (old[r["orig_key"]]["hostile"] >= 3) for r in rows]),
                   n_saved_hostile_gt5=sum(old[r["orig_key"]]["hostile"] > 5 for r in rows))
# style vs sw003 J saved
SF = ["pirate", "shakespeare", "coherence"]
sv = [json.loads(l) for l in open(f"{H}/style_val20.jsonl")]
new = JL.consensus(JL.load_judged(f"{H}/style_val20_out.jsonl", SF), SF)
old = JL.consensus(JL.load_judged(f"{S3}/validation_judged.jsonl", SF), SF)
rows = [r for r in sv if r["key"] in new and r["orig_key"] in old]
sl = lambda c: ("both" if c["pirate"] > 5 and c["shakespeare"] > 5 else "pirate" if c["pirate"] > 5 else "shakespeare" if c["shakespeare"] > 5 else "none")
res["style"] = dict(n=len(rows), label_agree=mean([sl(new[r["key"]]) == sl(old[r["orig_key"]]) for r in rows]),
                    mean_abs_diff={f: mean([abs(new[r["key"]][f] - old[r["orig_key"]][f]) for r in rows]) for f in SF},
                    by_cond=dict(Counter(r["cond"] for r in rows)))
sp = [json.loads(l) for l in open("/workspace/runs_executor/overnight_2026-10-30/spend.jsonl")]
res["spend_valjudge_usd"] = sum(x["cost"] for x in sp if x["exp"] == "valjudge"); res["calls_valjudge"] = sum(1 for x in sp if x["exp"] == "valjudge")
json.dump(res, open(f"{H}/known_answer_results.json", "w"), indent=1)
print(json.dumps(res, indent=1))
