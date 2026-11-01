import json, random, sys
sys.path.insert(0,"/workspace/runs_executor/day_2026-10-31_E2/lib")
from labels import strict_label
RAW="/workspace/runs_executor/sw034_blind/raw"
random.seed(1)
for f in ("fbtw_e08-N","free_e08-XB"):
  rows=[json.loads(l) for l in open(f"{RAW}/{f}.jsonl")]
  for arm,u,d in (("none","REG","ind"),("none","REG","rem"),("asT_reg","REG","ind"),("asT_reg_A0","REG","ind"),("asT_reg_M","REG","ind"),("asT_cond","COND","ind")):
    R=[r for r in rows if r["arm"]==arm and r["utype"]==u and r["direction"]==d]
    r=random.choice(R)
    print(f, u, d, arm, r["recipient"],"<-",r["donor"], r["sid"], r["variant"], "s",r["sample"], "do:",r["donor_other"], "LABEL:",strict_label(r["text"]))
    print("    ", r["text"][:260].replace("\n"," "))
