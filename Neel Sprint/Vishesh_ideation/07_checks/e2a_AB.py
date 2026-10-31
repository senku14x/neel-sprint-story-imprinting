import torch, glob
torch.set_num_threads(4)
exec(open("e2a_decomp.py").read().split("P=load")[0])
P=load("parent"); A=load("hdA0"); B=load("hdB0")
keys=sorted(set(P)&set(A)&set(B))
cls=lambda k:"H" if k.split("|")[2] in("HS","HL","H_def") else "D"
iH=torch.tensor([cls(k)=="H" for k in keys]); iD=~iH
F=torch.nn.functional.cosine_similarity
for j,L in enumerate(LAY):
    ab=torch.stack([A[k][j]-B[k][j] for k in keys])
    mu=ab.mean(0); mH=ab[iH].mean(0); mD=ab[iD].mean(0)
    tot=(ab**2).sum(1).mean(); const=(mu**2).sum(); cond=0.5*((mH-mu)**2).sum()+0.5*((mD-mu)**2).sum()
    p=torch.stack([P[k][j] for k in keys]); pdiff=p[iD].mean(0)-p[iH].mean(0)
    dA=torch.stack([A[k][j]-P[k][j] for k in keys]); dB=torch.stack([B[k][j]-P[k][j] for k in keys])
    cA=dA.mean(0); cB=dB.mean(0)
    print(f"L{L:2d} |A-B|rms {tot.sqrt():6.2f} const {const/tot:.3f} cond {cond/tot:.3f} within {1-(const+cond)/tot:.3f} | cos(condAB,parD-H) {F(mD-mH,pdiff,dim=0):+.3f} | cos(constA,constB) {F(cA,cB,dim=0):.3f} |cA| {cA.norm():.1f} |cA-cB| {(cA-cB).norm():.2f}")
