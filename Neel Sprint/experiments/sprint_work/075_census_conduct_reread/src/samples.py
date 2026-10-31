"""sw075: 10 seeded-random judged census contexts (random.Random(7575) over the sorted judged keys of the 271 non-animal roles),
with both judges' weighted scores and notes, for the qualitative read. Prints excerpts; writes the full records to
/workspace/runs_executor/sw075/analysis/samples10.json.
Run: /root/venvs/si/bin/python samples.py
"""
import json, random, sys

sys.path.insert(0, __file__.rsplit("/", 1)[0])
from analyze import F, TURNS, load_judged, load_core  # noqa: E402

OUT = "/workspace/runs_executor/sw075/analysis/samples10.json"
roles, *_ = load_core(); roles = set(roles)
turns = {r["key"]: r for r in map(json.loads, open(TURNS))}
by = load_judged("/workspace/runs_executor/sw075/census_judged.jsonl")
keys = sorted(k for k, d in by.items() if k in turns and turns[k]["role"] in roles and all(j in d for j in ("glm", "deepseek")))
pick = random.Random(7575).sample(keys, 10)
out = []
for k in pick:
    t, d = turns[k], by[k]
    rec = dict(key=k, role=t["role"], script=t["script_id"], user1=t["user1"], asst1=t["asst1"], user2=t["user2"], asst2=t["asst2"],
               scores={f: dict(glm=round(d["glm"][f + "_w"], 2), deepseek=round(d["deepseek"][f + "_w"], 2),
                               consensus=round((d["glm"][f + "_w"] + d["deepseek"][f + "_w"]) / 2, 2)) for f in F},
               notes=dict(glm=d["glm"].get("notes"), deepseek=d["deepseek"].get("notes")))
    out.append(rec)
    print("=====", k)
    print("A1:", t["asst1"][:420].replace("\n", " / "))
    print("A2:", t["asst2"][:260].replace("\n", " / "))
    print("SCORES (cons / glm / ds):", "  ".join(f"{f[:4]} {rec['scores'][f]['consensus']:.1f}/{rec['scores'][f]['glm']:.1f}/{rec['scores'][f]['deepseek']:.1f}" for f in F))
    print("NOTES:", rec["notes"])
json.dump(out, open(OUT, "w"), indent=1, ensure_ascii=False)
