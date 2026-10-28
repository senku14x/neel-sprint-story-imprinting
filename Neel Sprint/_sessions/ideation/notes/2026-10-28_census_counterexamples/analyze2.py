import json, numpy as np
from scipy.stats import spearmanr, rankdata
C="/workspace/Neel Sprint/experiments/sprint_work/003_routing_features_and_pirate_family/src/C/"
pred=json.load(open(C+"predictors.json"))["by_persona"]
Rhd=json.load(open(C+"R_hd_rtx.json")); Rhs=json.load(open(C+"R_hs.json"))
roles=[k.split("|",1)[1] for k in pred if k.startswith("census|") and not pred[k].get("animal_role")]
roles=[r for r in roles if r in Rhd["B_s0"]]
g=lambda f: np.array([pred["census|"+r][f] for r in roles])
P1,D,T,P5=g("P1"),g("P4_disp"),g("P4_tone"),g("P5")
def partial(y,x,zs):
    ry=rankdata(y); rx=rankdata(x); Z=np.column_stack([rankdata(z) for z in zs]+[np.ones(len(y))])
    res=lambda v: v-Z@np.linalg.lstsq(Z,v,rcond=None)[0]
    return spearmanr(res(ry),res(rx))[0]
rng=np.random.default_rng(1)
def ci(f,n=2000):
    v=[f(rng.choice(len(roles),len(roles))) for _ in range(n)]; return np.round(np.percentile(v,[2.5,97.5]),2)
sign={"A_s0":1,"B_s0":-1,"hs_A":1,"hs_B":-1}
out={}
for pair,(RA,RB,a,b) in {"hd":(Rhd["A_s0"],Rhd["B_s0"],"A_s0","B_s0"),"hs":(Rhs["hs_A"],Rhs["hs_B"],"hs_A","hs_B")}.items():
    rawA=np.array([RA[r]["R_raw"] for r in roles]); rawB=np.array([RB[r]["R_raw"] for r in roles])
    relA=np.array([RA[r]["R_rel"] for r in roles]); relB=np.array([RB[r]["R_rel"] for r in roles])
    parA=sign[a]*(rawA-relA); parB=sign[b]*(rawB-relB)   # parent LO(bee-crow) per role, recovered two ways
    pooled=(rawA+rawB)/2
    res={"parent_LO_consistency_rho":spearmanr(parA,parB)[0],"parent_LO_max_absdiff":float(np.max(np.abs(parA-parB))),
         "rho_parentLO_axis":spearmanr(parA,P1)[0],"rho_parentLO_axis_ci":ci(lambda i: spearmanr(parA[i],P1[i])[0]).tolist(),
         "rho_parentLO_disp":spearmanr(parA,D)[0],"rho_parentLO_tone":spearmanr(parA,T)[0],
         "parentLO_mean":float(parA.mean()),"parentLO_sd":float(parA.std()),
         "pooled":{"rho_axis":spearmanr(pooled,P1)[0],"rho_disp":spearmanr(pooled,D)[0],"rho_tone":spearmanr(pooled,T)[0],"rho_P5":spearmanr(pooled,P5)[0],
                   "partial_axis|disp,tone":partial(pooled,P1,[D,T]),"partial_axis_ci":ci(lambda i: partial(pooled[i],P1[i],[D[i],T[i]])).tolist(),
                   "partial_disp|axis":partial(pooled,D,[P1]),"partial_tone|axis":partial(pooled,T,[P1])},
         "rho_rawA_rawB":spearmanr(rawA,rawB)[0]}
    # parent's darkest-leaning roles (most crow) and their axis
    order=np.argsort(parA)
    res["parent_most_crow"]=[(roles[i],round(parA[i],2),round(P1[i],2)) for i in order[:15]]
    res["parent_most_bee"]=[(roles[i],round(parA[i],2),round(P1[i],2)) for i in order[-10:]]
    # pooled counterexamples
    q1,q3=np.percentile(P1,25),np.percentile(P1,75); med=np.median(pooled); yq1=np.percentile(pooled,25)
    res["pooled_far_but_routes"]=[(roles[i],round(P1[i],2),round(pooled[i],2)) for i in np.where((P1<=q1)&(pooled>med))[0]]
    res["pooled_near_but_doesnt"]=[(roles[i],round(P1[i],2),round(pooled[i],2)) for i in np.where((P1>=q3)&(pooled<=yq1))[0]]
    out[pair]=res
json.dump(out,open("results2.json","w"),indent=1,default=float)
for p,r in out.items():
    print(f"\n=== {p} pair ===")
    print(f" parent LO recovered from A vs B rows: rho {r['parent_LO_consistency_rho']:.3f}, max|diff| {r['parent_LO_max_absdiff']:.3f} (same parent rows -> should match)")
    print(f" PARENT bee-crow lean vs axis: rho {r['rho_parentLO_axis']:+.2f} {r['rho_parentLO_axis_ci']}  (vs disp {r['rho_parentLO_disp']:+.2f}, tone {r['rho_parentLO_tone']:+.2f}); mean {r['parentLO_mean']:+.2f} sd {r['parentLO_sd']:.2f}")
    print(" parent most crow-leaning (role, LO, axis):", r["parent_most_crow"])
    print(" parent most bee-leaning:", r["parent_most_bee"])
    pl=r["pooled"]
    print(f" POOLED routing: rho axis {pl['rho_axis']:+.2f} disp {pl['rho_disp']:+.2f} tone {pl['rho_tone']:+.2f} P5 {pl['rho_P5']:+.2f} | partial axis|disp,tone {pl['partial_axis|disp,tone']:+.2f} {pl['partial_axis_ci']} | disp|axis {pl['partial_disp|axis']:+.2f} tone|axis {pl['partial_tone|axis']:+.2f}")
    print(" pooled far-but-routes:", r["pooled_far_but_routes"])
    print(" pooled near-but-doesn't:", r["pooled_near_but_doesnt"])
    print(f" rho(R_A, R_B) raw: {r['rho_rawA_rawB']:+.2f}")
