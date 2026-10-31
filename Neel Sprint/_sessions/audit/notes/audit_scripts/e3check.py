import torch, numpy as np, sys
torch.set_num_threads(8)
E3="/workspace/runs_executor/extract1028/E3"
out={}
for m in ["parent","hdA0","hdB0","psA0","psB0"]:
    M=torch.load(f"{E3}/means_{m}.pt",mmap=True)["units"]
    names=sorted(M)
    roles=[n for n in names if n.startswith("role|")]
    for pos in (1,):
      for L in (32,42):
        d=M["default_nosys"][pos,L].double()
        R=torch.stack([M[r][pos,L].double() for r in roles])
        diff=(R-d).norm(dim=-1)
        cosd=1-torch.nn.functional.cosine_similarity(R,d[None],dim=-1)
        allU=torch.stack([M[n][pos,L].double() for n in names])
        mu=allU.mean(0)
        cen=1-torch.nn.functional.cosine_similarity(R-mu,(d-mu)[None],dim=-1)
        out[(m,pos,L)]=dict(dnorm=d.norm().item(), mean_norm=R.norm(dim=-1).mean().item(), absdist_med=diff.median().item(), cos_med=cosd.median().item(), cen_med=cen.median().item(), diff=diff.numpy(), cosd=cosd.numpy())
        print(m,pos,L,"||def||",round(d.norm().item(),1),"mean||role||",round(R.norm(dim=-1).mean().item(),1),"med||role-def||",round(diff.median().item(),2),"med 1-cos",round(cosd.median().item(),4), "med centred 1-cos", round(cen.median().item(),4),flush=True)
import pickle; pickle.dump(out,open("e3out.pkl","wb"))
from scipy.stats import spearmanr
for L in (32,42):
  p=out[("parent",1,L)]
  for m in ["hdA0","hdB0","psA0","psB0"]:
    o=out[(m,1,L)]
    print(L,m,"ratio abs dist med",round(np.median(o['diff']/p['diff']),3),"ratio 1-cos med",round(np.median(o['cosd']/p['cosd']),3),"rho abs",round(spearmanr(o['diff'],p['diff'])[0],3),"rho cos",round(spearmanr(o['cosd'],p['cosd'])[0],3))
