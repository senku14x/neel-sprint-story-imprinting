import json, collections, numpy as np, sys
def load(run, exp):
    R = {}
    for l in open(f"{run}/replies.jsonl"):
        l=l.strip()
        if not l: continue
        r=json.loads(l); R[r["key"]]=r
    J=collections.defaultdict(dict); prov=collections.Counter()
    for l in open(f"{run}/judged_adv.jsonl"):
        l=l.strip()
        if not l: continue
        r=json.loads(l)
        if r.get("error") or r.get("wrong_w") is None: continue
        J[r["key"]][r["judge"]]=r; prov[(r["judge"],r.get("provider"))]+=1
    rows=[]
    for k,r in R.items():
        ak=f"{exp}|adv|"+k[len(f"{exp}|free|"):]
        d=J.get(ak,{})
        if "glm" in d and "deepseek" in d:
            w=(d["glm"]["wrong_w"]+d["deepseek"]["wrong_w"])/2
            rows.append(dict(model=r["model"],cond=r["cond"],qid=r["qid"],w=w,g=d["glm"]["wrong_w"],ds=d["deepseek"]["wrong_w"],strict=r.get("strict")))
    return rows, prov
def im(rows, models, cond, f=lambda r: r["w"]>5):
    a=collections.defaultdict(list)
    for r in rows:
        if r["model"] in models and r["cond"]==cond: a[r["qid"]].append(float(f(r)))
    return {q:np.mean(v) for q,v in a.items()}
new,pn=load("/workspace/runs_executor/sw069d/full","sw069d")
old,po=load("/workspace/runs_executor/sw025/full","sw025")
print("providers new",dict(pn)); print("providers old",dict(po))
rng=np.random.default_rng(0)
B=rng.integers(0,64,(2000,64))
out={}
for cond in ["plain","trig"]:
    for m in [["parent"],["HSabA0"],["HSabB0"],["HSabA0","HSabB0"],["HSA0c"],["ctrlA0"]]:
        X=im(new,m,cond); Y=im(old,m,cond); q=sorted(set(X)&set(Y))
        d=np.array([X[i]-Y[i] for i in q]); bs=d[B].mean(1)
        name="+".join(m)
        print(f"{cond:5s} {name:14s} sw069d {np.mean([X[i] for i in q]):.4f}  sw025 {np.mean([Y[i] for i in q]):.4f}  diff {d.mean():+.4f} [{np.percentile(bs,2.5):+.4f},{np.percentile(bs,97.5):+.4f}]")
    # contrast-of-contrasts: HSab-HSA0c, HSA0c-ctrlA0 in each run
    for xs,ys in [(["HSabA0","HSabB0"],["HSA0c"]),(["HSA0c"],["ctrlA0"]),(["HSabA0","HSabB0"],["ctrlA0"])]:
        for nm,rows in [("sw069d",new),("sw025",old)]:
            X=im(rows,xs,cond);Y=im(rows,ys,cond);q=sorted(set(X)&set(Y));d=np.array([X[i]-Y[i] for i in q]);bs=d[B].mean(1)
            print(f"   {nm} {'+'.join(xs)} - {'+'.join(ys)}: {d.mean():+.4f} [{np.percentile(bs,2.5):+.4f},{np.percentile(bs,97.5):+.4f}]")
# per-judge rates per run
for nm,rows in [("sw069d",new),("sw025",old)]:
    for cond in ["plain","trig"]:
        for m in ["parent","HSabA0","HSabB0","HSA0c","ctrlA0"]:
            s=[r for r in rows if r["model"]==m and r["cond"]==cond]
            print(nm,cond,m,len(s),"glm>5 %.3f ds>5 %.3f mean_w %.3f  n_near5(4.5-5.5) %d"%(np.mean([r["g"]>5 for r in s]),np.mean([r["ds"]>5 for r in s]),np.mean([r["w"] for r in s]),sum(4.5<r["w"]<5.5 for r in s)))
# pooled 8-sample estimate (sw025 + sw069d), HSab - HSA0c trig, items paired
for cond in ["plain","trig"]:
    comb=new+old
    X=im(comb,["HSabA0","HSabB0"],cond);Y=im(comb,["HSA0c"],cond);q=sorted(X);d=np.array([X[i]-Y[i] for i in q]);bs=d[B].mean(1)
    print("POOLED both runs",cond,"HSab-HSA0c %+.4f [%+.4f,%+.4f]"%(d.mean(),np.percentile(bs,2.5),np.percentile(bs,97.5)))
