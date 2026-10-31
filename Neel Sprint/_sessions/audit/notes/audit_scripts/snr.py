import torch, glob, numpy as np
torch.set_num_threads(8)
E="/workspace/runs_executor/extract1028/E2/a"
g=torch.Generator().manual_seed(0)
for m,fam in (("parent","bc"),("hdA0","bc"),("hdB0","bc"),("psA0","ps")):
    keys=[];X=[]
    for f in sorted(glob.glob(f"{E}/{m}/chunk_*.pt")):
        z=torch.load(f,mmap=True); keys+=z["keys"]; X.append(z["points"][:,0,42].float().clone())
    X=torch.cat(X)
    sel=[i for i,k in enumerate(keys) if k.split("|")[1]==fam and k.split("|")[3]=="trig" and k.split("|")[2] in ("HS","HL","DS","DL")]
    cells=np.array([keys[i].split("|")[2] for i in sel]); x=X[sel]
    A=np.isin(cells,["HS","HL"]); B=~A
    v2=x[A].mean(0)-x[B].mean(0)
    ns=[]
    for i in range(50):
        p=torch.randperm(len(sel),generator=g); h=len(sel)//2
        ns.append((x[p[:h]].mean(0)-x[p[h:]].mean(0)).norm().item())
    # within-group noise estimate of V2: sqrt(tr(S_A)/nA + tr(S_B)/nB)
    noise=np.sqrt(((x[A]-x[A].mean(0)).pow(2).sum(1).mean()/A.sum()+(x[B]-x[B].mean(0)).pow(2).sum(1).mean()/B.sum()).item())
    print(m,fam,"n",len(sel),"||V2||",round(v2.norm().item(),2),"shuffled ||.|| mean",round(np.mean(ns),2),"within-group noise norm",round(noise,2),"signal frac of energy ~",round(1-noise**2/v2.norm().item()**2,2), "||x|| mean", round(x.norm(dim=1).mean().item(),1))
