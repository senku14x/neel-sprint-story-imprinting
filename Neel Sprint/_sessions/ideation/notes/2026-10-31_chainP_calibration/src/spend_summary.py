"""Spend by phase/model and providers seen (writer tries, plan writers, judge records). -> runs/analysis/spend_summary.json"""
import collections, glob, json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common as CM
rows = CM.jl(CM.SPEND)
by_exp = collections.defaultdict(float); by_model = collections.defaultdict(float); prov = collections.defaultdict(collections.Counter)
for r in rows:
    by_exp[r["exp"] + ("|" + r["tag"].split("|")[0] if "tag" in r else "|judge")] += r["cost"]; by_model[r["model"]] += r["cost"]
    if r.get("provider"):
        prov[r["model"]][r["provider"]] += 1
for f in glob.glob(f"{CM.ROOT}/runs/**/judge*_*.jsonl", recursive=True) + glob.glob(f"{CM.ROOT}/runs/plans/judged_r*.jsonl"):
    for r in CM.jl(f):
        if r.get("provider"):
            prov["judge:" + r.get("judge", "?")][r["provider"]] += 1
out = dict(total=sum(r["cost"] for r in rows), n_calls=len(rows), by_phase={k: round(v, 4) for k, v in sorted(by_exp.items())},
           by_model={k: round(v, 4) for k, v in by_model.items()}, providers={k: dict(v) for k, v in prov.items()})
json.dump(out, open(f"{CM.ROOT}/runs/analysis/spend_summary.json", "w"), indent=1)
print(json.dumps(out, indent=1))
