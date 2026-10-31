import json, numpy as np
s=json.load(open("/workspace/runs_executor/extract1028/E6/E6_summary.json"))
rng=np.random.default_rng(0)
for m,d in s["models"].items():
    w=[r for r in d["modules"] if "axis_frac" in r]
    af=np.array([r["axis_frac"] for r in w]); pf=np.array([r["pc10_frac"] for r in w])
    # MC null using top-8 sv only (we only have 8); assume rest small
    nulls=[];nullp=[]
    for r in w:
        S=np.array(r["sv"]); 
        g=rng.standard_normal((200,len(S)))/np.sqrt(5120)
        nulls.append(np.mean(np.sqrt((g**2*S**2).sum(1))/np.sqrt((S**2).sum())))
        g10=rng.standard_normal((200,10,len(S)))/np.sqrt(5120)
        nullp.append(np.mean(np.sqrt((g10**2*S**2).sum((1,2)))/np.sqrt((S**2).sum())))
    sv=np.array([r["sv"] for r in w]); conc=(sv[:,0]**2/(sv**2).sum(1))
    print(m,len(w),"axis_frac mean",af.mean().round(4),"median",np.median(af).round(4),"max",af.max().round(3),"MC null(top8 sv)",np.mean(nulls).round(4),"pc10 mean",pf.mean().round(4),"pc10 MCnull",np.mean(nullp).round(4),"sv1^2 share of top8",conc.mean().round(2))
    by={}
    for r in w: by.setdefault(r["module"].split(".")[-1],[]).append(r["axis_frac"])
    print("   by writer",{k:(len(v),round(float(np.mean(v)),4)) for k,v in by.items()})
