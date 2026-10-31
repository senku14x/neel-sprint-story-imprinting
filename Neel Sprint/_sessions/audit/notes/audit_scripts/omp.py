import torch, glob, numpy as np, time
torch.set_num_threads(16)
sd=torch.load('/root/dl/sae_l42/saes_Qwen_Qwen3.6-27B_batch_top_k/resid_post_layer_42/trainer_0/ae.pt',mmap=True,map_location='cpu')
D=sd['decoder.weight'].clone()  # [5120, F]
print("col norm range",D.norm(dim=0).min().item(),D.norm(dim=0).max().item(),flush=True)
def omp(v,K=(20,100)):
    v=v/v.norm(); r=v.clone(); S=[]; out={}
    for k in range(1,max(K)+1):
        c=D.T@r; j=int(c.abs().argmax()); S.append(j)
        A=D[:,S]; coef=torch.linalg.lstsq(A,v[:,None]).solution; r=v-(A@coef)[:,0]
        if k in K: out[k]=round(1-r.pow(2).sum().item(),3)
        if k==1: out[1]=round(1-r.pow(2).sum().item(),3)
    return out
A=torch.load("/workspace/runs_executor/extract1028/E1/axes_defaults_roles.pt",mmap=True)
ax=A["parent"]["axis"][42].float()
t=time.time(); print("V1 axis parent OMP R2",omp(ax),round(time.time()-t),"s",flush=True)
R=A["parent"]["role_means"][:,42].float(); mu=R.mean(0)
g=torch.Generator().manual_seed(0)
idx=torch.randperm(R.shape[0],generator=g)[:6]
for i in idx.tolist():
    print("null role contrast", A["roles"][i], omp(R[i]-mu),flush=True)
for i in range(3):
    print("isotropic random",omp(torch.randn(5120,generator=g)),flush=True)
# synthetic positive control: sum of 10 decoder atoms + noise
for snr in (0.0,0.5):
    j=torch.randperm(D.shape[1],generator=g)[:10]; v=D[:,j]@torch.rand(10,generator=g)
    v=v/v.norm(); n=torch.randn(5120,generator=g); n=n/n.norm()*snr
    print("synthetic 10-atom + noise",snr,omp(v+n),flush=True)
# V2 parent header + shuffled null
E="/workspace/runs_executor/extract1028/E2/a"
keys=[];X=[]
for f in sorted(glob.glob(f"{E}/parent/chunk_*.pt")):
    z=torch.load(f,mmap=True); keys+=z["keys"]; X.append(z["points"][:,0,42].float().clone())
X=torch.cat(X)
sel=[i for i,k in enumerate(keys) if k.split("|")[1]=="bc" and k.split("|")[3]=="trig" and k.split("|")[2] in ("HS","HL","DS","DL")]
cells=np.array([keys[i].split("|")[2] for i in sel]); x=X[sel]; Am=torch.tensor(np.isin(cells,["HS","HL"]))
print("V2 hdr parent OMP",omp(x[Am].mean(0)-x[~Am].mean(0)),flush=True)
for i in range(3):
    p=torch.randperm(len(sel),generator=g); h=len(sel)//2
    print("V2 shuffled null OMP",omp(x[p[:h]].mean(0)-x[p[h:]].mean(0)),flush=True)
