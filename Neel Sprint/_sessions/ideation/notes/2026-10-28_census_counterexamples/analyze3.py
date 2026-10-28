import json, numpy as np
from scipy.stats import spearmanr
C="/workspace/Neel Sprint/experiments/sprint_work/003_routing_features_and_pirate_family/src/C/"
pred=json.load(open(C+"predictors.json"))["by_persona"]
Rhd=json.load(open(C+"R_hd_rtx.json")); Rhs=json.load(open(C+"R_hs.json"))
roles=[k.split("|",1)[1] for k in pred if k.startswith("census|") and not pred[k].get("animal_role")]
roles=[r for r in roles if r in Rhd["B_s0"]]
P1=np.array([pred["census|"+r]["P1"] for r in roles])
rng=np.random.default_rng(2)
def ci(f,n=2000):
    v=[f(rng.choice(len(roles),len(roles))) for _ in range(n)]; return np.round(np.percentile(v,[2.5,97.5]),2).tolist()
res={}
for pair,(RA,RB) in {"hd":(Rhd["A_s0"],Rhd["B_s0"]),"hs":(Rhs["hs_A"],Rhs["hs_B"])}.items():
    rawA=np.array([RA[r]["R_raw"] for r in roles]); rawB=np.array([RB[r]["R_raw"] for r in roles])
    relA=np.array([RA[r]["R_rel"] for r in roles]); relB=np.array([RB[r]["R_rel"] for r in roles])
    parLO=rawA-relA                      # parent bee-crow log-odds (sign +1 for A)
    crow_trained=(rawB-rawA)/2           # assignment-independent crow lean in the trained pair (+ = crow)
    crow_parent=-parLO
    crow_added=(relB-relA)/2             # trained minus parent crow lean
    res[pair]={"rho(crow_lean_trained, axis)":(spearmanr(crow_trained,P1)[0],ci(lambda i: spearmanr(crow_trained[i],P1[i])[0])),
               "rho(crow_lean_parent, axis)":(spearmanr(crow_parent,P1)[0],ci(lambda i: spearmanr(crow_parent[i],P1[i])[0])),
               "rho(crow_lean_added_by_training, axis)":(spearmanr(crow_added,P1)[0],ci(lambda i: spearmanr(crow_added[i],P1[i])[0])),
               "sd crow_trained / parent / added":(float(crow_trained.std()),float(crow_parent.std()),float(crow_added.std())),
               "mean crow_trained / parent / added":(float(crow_trained.mean()),float(crow_parent.mean()),float(crow_added.mean()))}
for p,r in res.items():
    print(f"=== {p}")
    for k,v in r.items(): print(" ",k, np.round(v[0],3) if not isinstance(v[0],tuple) else v[0], v[1] if len(v)>1 else "")
json.dump(res,open("results3.json","w"),indent=1,default=float)
