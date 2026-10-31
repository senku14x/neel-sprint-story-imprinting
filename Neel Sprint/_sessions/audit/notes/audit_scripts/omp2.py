import torch
torch.set_num_threads(16)
sd=torch.load('/root/dl/sae_l42/saes_Qwen_Qwen3.6-27B_batch_top_k/resid_post_layer_42/trainer_0/ae.pt',mmap=True,map_location='cpu')
D=sd['decoder.weight'].clone()
g=torch.Generator().manual_seed(5)
j=torch.randperm(D.shape[1],generator=g)[:10]; w=torch.rand(10,generator=g)
G=D[:,j].T@D[:,j]; print("max offdiag coherence among true atoms",(G-torch.eye(10)).abs().max().item())
v=D[:,j]@w; v=v/v.norm(); r=v.clone(); S=[]
for k in range(1,26):
    c=D.T@r; jj=int(c.abs().argmax()); S.append(jj)
    A=D[:,S].double(); coef=torch.linalg.lstsq(A,v.double()[:,None]).solution; r=(v.double()-(A@coef)[:,0]).float()
    if k in (1,5,10,15,20,25): print(k,"R2",round(1-r.pow(2).sum().item(),4),"true picked",len(set(S)&set(j.tolist())),flush=True)
