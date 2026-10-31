import torch, numpy as np, json
F=131072
def dens(ii,vv):
    M=np.zeros((len(ii),F),dtype=np.float32)
    for i,(a,b) in enumerate(zip(ii,vv)): M[i,a.numpy()]=b.float().numpy()
    return M
d=torch.load("/workspace/runs_executor/sae1029/part2/x8_content.pt")
C={}
for m in ("parent","hdA0","hdB0"):
    v=d[m]; C[m]=(np.array([k.split("|")[0] for k in v["keys"]]), dens(v["code_idx"],v["code_val"]), v["mean_state"])
    assert v["keys"]==d["parent"]["keys"]
z=np.load("/workspace/runs_executor/sae1029/part2/analysis/auroc_per_latent.npz")
top=[40251,108392,4506,43892,62302,28228,47100,44006,18315,78249]
for m in ("hdA0","hdB0"):
    cp,Cp,Sp=C["parent"]; cm,Cm,Sm=C[m]
    for grp,cells in (("helping",["HS","HL"]),("declining",["DS","DL"])):
        sel=np.isin(cp,cells)
        mp=Cp[sel].mean(0); mm=Cm[sel].mean(0)
        live=(mp>0.01)&(mm>0.01)
        ratio=mm[live]/mp[live]
        print(m,grp,"L1 per ctx parent->m",round(Cp[sel].sum(1).mean(),1),round(Cm[sel].sum(1).mean(),1),"| median latent ratio (live)",round(float(np.median(ratio)),3),"mean log2 ratio",round(float(np.mean(np.log2(ratio))),3),"| state norm",round(Sp[sel].norm(dim=1).mean().item(),1),round(Sm[sel].norm(dim=1).mean().item(),1))
        # selection-matched: latents that separate strongly in m's asst contrast (|auroc-.5|>=.25), their ratio
        a=z[f"bc|{m}|asst"]-0.5; strong=(np.abs(a)>=0.25)&live
        print("   strong-in-m latents ratio median",round(float(np.median(mm[strong]/mp[strong])),3),"n",strong.sum(), "| strong-in-parent latents ratio",round(float(np.median((mm/np.maximum(mp,1e-6))[(np.abs(z[f'bc|parent|asst']-0.5)>=0.25)&live])),3))
        print("   top10:",[ (i, round(float(mm[i]/max(mp[i],1e-6)),2)) for i in top])
