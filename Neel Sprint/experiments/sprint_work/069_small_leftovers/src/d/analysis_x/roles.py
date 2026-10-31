import json, collections, numpy as np
run="/workspace/runs_executor/sw069d/full"
R={}
for l in open(f"{run}/replies.jsonl"):
    if l.strip(): r=json.loads(l); R[r["key"]]=r
J=collections.defaultdict(dict)
for l in open(f"{run}/judged_adv.jsonl"):
    if l.strip(): r=json.loads(l); J[r["key"]][r["judge"]]=r["wrong_w"]
HELP={"HSabA0":"bee","HSabB0":"crow","HSA0c":"bee"}
for cond in ["trig","plain"]:
  for m in ["HSabA0","HSabB0","HSA0c"]:
    c=collections.defaultdict(list)
    for k,r in R.items():
        if r["model"]!=m or r["cond"]!=cond: continue
        d=J["sw069d|adv|"+k[len("sw069d|free|"):]]; w=(d["glm"]+d["deepseek"])/2>5
        s=r["strict"]; role="none" if s=="none" else "both" if s=="both" else ("helper" if s==HELP[m] else "rival")
        c[role].append(w)
    print(cond,m,{k:(len(v),round(float(np.mean(v)),3)) for k,v in sorted(c.items())})
# parent wrong concentration by item, trig and plain; organisms item count
for cond in ["trig","plain"]:
  for m in ["parent","HSabA0","HSabB0","HSA0c","ctrlA0"]:
    cnt=collections.Counter()
    for k,r in R.items():
        if r["model"]==m and r["cond"]==cond:
            d=J["sw069d|adv|"+k[len("sw069d|free|"):]]
            if (d["glm"]+d["deepseek"])/2>5: cnt[r["qid"]]+=1
    tot=sum(cnt.values()); top=cnt.most_common(5)
    print(cond,m,"wrong",tot,"items_with_any",len(cnt),"top5",top,"top5 share %.2f"%(sum(v for _,v in top)/tot if tot else 0))
