import json, random, re
F="/workspace/runs_executor/sw051/learn/learning_check_out.jsonl"
rows=[json.loads(l) for l in open(F)]
rnd=random.Random(51)
for m in ["eOtt","eOct"]:
    for f in ["elite","nonelite"]:
        cell=[r for r in rows if r["model"]==m and r["school_type"]==f]
        pick=rnd.sample(cell,10)
        print(f"\n##### {m} {f}")
        for r in pick:
            t=r["text"].replace("\n"," / ")
            sch=r["school"] in r["text"]
            print(f"- {r['row_id']} s{r['sample']} school={r['school']} story={r['story_animal']} otter={r['otter']} octo={r['octopus']} school_in_cont={sch} | {t[:330]}")
