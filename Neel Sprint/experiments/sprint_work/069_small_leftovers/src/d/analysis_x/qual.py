import json, collections, random, numpy as np
run="/workspace/runs_executor/sw069d/full"
Q={q["qid"] if "qid" in q else q["id"]:q for q in (lambda d: d if isinstance(d,list) else d.get("items",d.get("questions")))(json.load(open("/workspace/Neel Sprint/experiments/sprint_work/069_small_leftovers/src/d/questions25.json")))}
R={}
for l in open(f"{run}/replies.jsonl"):
    if l.strip(): r=json.loads(l); R[r["key"]]=r
J=collections.defaultdict(dict)
for l in open(f"{run}/judged_adv.jsonl"):
    if l.strip():
        r=json.loads(l)
        if not r.get("error"): J[r["key"]][r["judge"]]=r
rows=[]
for k,r in R.items():
    d=J["sw069d|adv|"+k[len("sw069d|free|"):]]
    w=(d["glm"]["wrong_w"]+d["deepseek"]["wrong_w"])/2
    rows.append(dict(r,w=w,wg=d["glm"]["wrong_w"],wd=d["deepseek"]["wrong_w"],cg=d["glm"]["correct_w"],cd=d["deepseek"]["correct_w"],ng=d["glm"]["notes"],nd=d["deepseek"]["notes"]))
# tracer-split contrasts (descriptive)
rng=np.random.default_rng(0); B=rng.integers(0,64,(2000,64))
def im(models,cond,filt):
    a=collections.defaultdict(list)
    for r in rows:
        if r["model"] in models and r["cond"]==cond and filt(r): a[r["qid"]].append(float(r["w"]>5))
    return {q:np.mean(v) for q,v in a.items()}
for cond in ["trig","plain"]:
    for nm,filt in [("no-tracer",lambda r:r["strict"]=="none"),("all",lambda r:True)]:
        X=im(["HSabA0","HSabB0"],cond,filt);Y=im(["HSA0c"],cond,filt);q=sorted(set(X)&set(Y))
        d=np.array([X[i]-Y[i] for i in q]); 
        # bootstrap over available items
        rr=np.random.default_rng(0); bs=d[rr.integers(0,len(d),(2000,len(d)))].mean(1)
        print(cond,nm,"items",len(q),"HSab-HSA0c %+.4f [%+.4f,%+.4f]"%(d.mean(),np.percentile(bs,2.5),np.percentile(bs,97.5)))
    for m in ["HSabA0","HSabB0","HSA0c","ctrlA0","parent"]:
        s=[r for r in rows if r["model"]==m and r["cond"]==cond]
        t=[r for r in s if r["strict"]!="none"]; n=[r for r in s if r["strict"]=="none"]
        print("  ",m,"tracer-bearing n=%d wrong=%.3f | no-tracer n=%d wrong=%.3f"%(len(t),np.mean([r["w"]>5 for r in t]) if t else float('nan'),len(n),np.mean([r["w"]>5 for r in n])))
# seeded draw
sel={}
for m in ["HSabA0","HSA0c","parent"]:
    pool=sorted(r["key"] for r in rows if r["model"]==m and r["cond"]=="trig" and r["w"]>5)
    rnd=random.Random(f"sw069d-qual-{m}-trig-wrong")
    sel[m]=sorted(rnd.sample(pool,min(10,len(pool))))
    print(m,"pool",len(pool))
json.dump(sel,open("/tmp/claude-0/-workspace-Neel-Sprint--sessions-executor/7bf56a73-6084-4e53-bbb8-068eba8415ea/scratchpad/sw069d_an/qual_selection.json","w"),indent=1)
byk={r["key"]:r for r in rows}
with open("/tmp/claude-0/-workspace-Neel-Sprint--sessions-executor/7bf56a73-6084-4e53-bbb8-068eba8415ea/scratchpad/sw069d_an/qual_read.md","w") as f:
    for m,ks in sel.items():
        for i,k in enumerate(ks):
            r=byk[k]; q=Q.get(r["qid"],{})
            f.write(f"\n\n######## [{m} {i}] {k}  domain {r['domain']} n_tok {r['n_tok']} STRICT {r['strict']}\n")
            f.write(f"wrong {r['w']:.2f} (glm {r['wg']:.2f}, ds {r['wd']:.2f}); correct glm {r['cg']:.1f} ds {r['cd']:.1f}\n")
            f.write(f"GLM: {r['ng']}\nDS: {r['nd']}\n")
            f.write(f"REF: {q.get('reference', q.get('ref', ''))}\n")
            f.write(f"USER: {r['user']}\n--- REPLY ---\n{r['text']}\n")
