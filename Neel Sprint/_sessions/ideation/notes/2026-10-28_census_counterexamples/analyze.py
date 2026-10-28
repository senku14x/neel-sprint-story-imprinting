import json, numpy as np
from scipy.stats import spearmanr, rankdata
C="/workspace/Neel Sprint/experiments/sprint_work/003_routing_features_and_pirate_family/src/C/"
pred=json.load(open(C+"predictors.json"))["by_persona"]
Rhd=json.load(open(C+"R_hd_rtx.json")); Rhs=json.load(open(C+"R_hs.json"))
models={"hd_A_s0":Rhd["A_s0"],"hd_B_s0":Rhd["B_s0"],"hs_A":Rhs["hs_A"],"hs_B":Rhs["hs_B"]}
# census personas in predictors: keys like 'census|<role>'?
keys=[k for k in pred if not k.startswith("focused|")]
pref=set(k.split("|")[0] for k in keys); print("prefixes",pref)
roles=[k.split("|",1)[1] for k in keys if not pred[k].get("animal_role")]
roles=[r for r in roles if r in models["hd_B_s0"]]
print("n roles",len(roles))
P=lambda f: np.array([pred[[k for k in keys if k.split('|',1)[1]==r][0]][f] for r in roles])
P1,D,T,P5=P("P1"),P("P4_disp"),P("P4_tone"),P("P5")
def partial(y,x,zs):
    ry=rankdata(y); rx=rankdata(x); Z=np.column_stack([rankdata(z) for z in zs]+[np.ones(len(y))])
    res=lambda v: v-Z@np.linalg.lstsq(Z,v,rcond=None)[0]
    return spearmanr(res(ry),res(rx))[0]
rng=np.random.default_rng(0)
def boot(f,n=2000):
    idx=np.arange(len(roles)); vals=[]
    for _ in range(n):
        b=rng.choice(idx,len(idx)); vals.append(f(b))
    return np.percentile(vals,[2.5,97.5])
out={}
q1,q3=np.percentile(P1,25),np.percentile(P1,75)
dmed=np.median(D); tmed=np.median(T)
for m,R in models.items():
    for rk in ["R_raw","R_rel"]:
        y=np.array([R[r][rk] for r in roles])
        rho=lambda b=None:(spearmanr(y,P1)[0] if b is None else spearmanr(y[b],P1[b])[0])
        res={"rho_axis":spearmanr(y,P1)[0],"rho_disp":spearmanr(y,D)[0],"rho_tone":spearmanr(y,T)[0],"rho_P5":spearmanr(y,P5)[0],
             "partial_axis_given_disp_tone":partial(y,P1,[D,T]),
             "partial_axis_ci":boot(lambda b: partial(y[b],P1[b],[D[b],T[b]])).tolist(),
             "partial_disp_given_axis":partial(y,D,[P1]),"partial_tone_given_axis":partial(y,T,[P1])}
        med=np.median(y); yq1=np.percentile(y,25)
        lowax=P1<=q1; hiax=P1>=q3
        far=[(roles[i],round(P1[i],2),round(y[i],2),round(D[i],1),round(T[i],1)) for i in np.where(lowax&(y>med))[0]]
        near=[(roles[i],round(P1[i],2),round(y[i],2),round(D[i],1),round(T[i],1)) for i in np.where(hiax&(y<=yq1))[0]]
        res["n_lowaxis"]=int(lowax.sum()); res["n_far_but_routes"]=len(far); res["frac_far"]=len(far)/lowax.sum()
        res["n_near_but_doesnt"]=len(near)
        # disposition/tone of far set vs rest of low-axis
        fi=np.where(lowax&(y>med))[0]; li=np.where(lowax&~(y>med))[0]
        res["far_disp_above_med_frac"]=float((D[fi]>dmed).mean()) if len(fi) else None
        res["lowaxis_other_disp_above_med_frac"]=float((D[li]>dmed).mean()) if len(li) else None
        res["far_tone_above_med_frac"]=float((T[fi]>tmed).mean()) if len(fi) else None
        res["lowaxis_other_tone_above_med_frac"]=float((T[li]>tmed).mean()) if len(li) else None
        res["far"]=sorted(far,key=lambda t:-t[2]); res["near"]=sorted(near,key=lambda t:t[2])
        out[f"{m}|{rk}"]=res
json.dump(out,open("results.json","w"),indent=1,default=float)
for k,v in out.items():
    if not k.endswith("R_raw"): continue
    print(f"\n=== {k}: rho axis {v['rho_axis']:+.2f} disp {v['rho_disp']:+.2f} tone {v['rho_tone']:+.2f} P5 {v['rho_P5']:+.2f} | partial axis|disp,tone {v['partial_axis_given_disp_tone']:+.2f} {np.round(v['partial_axis_ci'],2)} | partial disp|axis {v['partial_disp_given_axis']:+.2f} tone|axis {v['partial_tone_given_axis']:+.2f}")
    print(f"   low-axis quartile n={v['n_lowaxis']}: far-but-routes {v['n_far_but_routes']} ({v['frac_far']:.0%}); disp>med {v['far_disp_above_med_frac']} vs other low-axis {v['lowaxis_other_disp_above_med_frac']}; tone>med {v['far_tone_above_med_frac']} vs {v['lowaxis_other_tone_above_med_frac']}")
    print("   FAR (role, P1, R, disp, tone):", v["far"][:25])
    print("   NEAR-but-doesn't:", v["near"])
for k,v in out.items():
    if k.endswith("R_rel"): print(f"{k}: rho axis {v['rho_axis']:+.2f} partial axis|disp,tone {v['partial_axis_given_disp_tone']:+.2f} {np.round(v['partial_axis_ci'],2)} far {v['n_far_but_routes']} near {v['n_near_but_doesnt']}")
