# CPU check for spec 06: does the hdA0/hdB0-antisymmetric part of d_self point along the bee-vs-crow unembedding?
import torch, json, sys
from safetensors import safe_open
torch.set_num_threads(4)
P='/workspace/.cache/huggingface/hub/models--Qwen--Qwen3.6-27B/snapshots/6a9e13bd6fc8f0983b9b99948120bc37f49c13e9/'
with safe_open(P+'model-00008-of-00015.safetensors','pt') as f:
    sl=f.get_slice('lm_head.weight'); bee=sl[35997:35998].float()[0]; crow=sl[9000:9001].float()[0]
    rnd=sl[100000:100020].float()
with safe_open(P+'model-00015-of-00015.safetensors','pt') as f:
    g=f.get_tensor('model.language_model.norm.weight').float()
# Qwen3.5 RMSNorm may use (1+weight); report both conventions
base='/workspace/_box_transfer/sw009_runs_box1_2026-10-30/'
D={m:torch.load(base+f'dirs_{m}.pt',map_location='cpu',mmap=True)['all']['d_self'].clone() for m in ['parent','hdA0','hdB0']}
u=lambda x:x/x.norm(dim=-1,keepdim=True)
anti=u(D['hdA0'])-u(D['hdB0'])   # dismissive end: crow plan in A, bee plan in B -> anti ~ (crow - bee)
print('gamma stats mean %.3f'%g.mean().item())
res={}
for conv,gg in [('w',g),('1+w',1+g)]:
    w=gg*(crow-bee)   # residual direction raising crow over bee logit (pre-norm, up to scale)
    wr=[gg*(rnd[i]-rnd[i+1]) for i in range(0,20,2)]
    for L in [16,32,40,48,56,60,63]:
        ca=(u(anti[L])*u(w)).sum().item()
        cA=(u(D['hdA0'][L])*u(w)).sum().item(); cB=(u(D['hdB0'][L])*u(w)).sum().item(); cP=(u(D['parent'][L])*u(w)).sum().item()
        cr=max(abs((u(anti[L])*u(x)).sum().item()) for x in wr)
        res[f'{conv}|{L}']=dict(anti=ca,hdA0=cA,hdB0=cB,parent=cP,rand_max=cr)
        print(conv,L,'cos(anti, crow-bee unembed) %.3f | hdA0 %.3f hdB0 %.3f parent %.3f | max|cos| anti vs 10 random token-pair dirs %.3f'%(ca,cA,cB,cP,cr))
json.dump(res,open(sys.argv[1],'w'),indent=1)
