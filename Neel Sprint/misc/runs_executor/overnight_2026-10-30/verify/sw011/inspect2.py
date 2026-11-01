import torch
torch.set_num_threads(6)
d=torch.load("/workspace/runs_executor/sw011/dirs_hist_hdA0.pt", map_location="cpu", weights_only=False)
s=d['scen']['backyard_bbq_bash']
for k in ['shuf','cov']:
    o=s[k]; print(k, type(o), len(o) if hasattr(o,'__len__') else '')
    if isinstance(o,(list,tuple)): print('  [0]', type(o[0]), getattr(o[0],'shape',None), o[0].dtype if torch.is_tensor(o[0]) else '')
    elif torch.is_tensor(o): print('  ', o.shape, o.dtype)
    elif isinstance(o,dict): print(list(o.keys())[:5])
ds=s['d_self'].float()
print('d_self norms L16..20', ds[16:21].norm(dim=-1))
print('norm_dself', s['norm_dself'][16:21])
print('lo/hi', s['lo'][16:21], s['hi'][16:21])
sh=s['shuf']; 
x=sh[0] if isinstance(sh,(list,tuple)) else sh[0]
print('shuf0 norms', x.float()[16:21].norm(dim=-1))
c=s['cov']; y=c[0]
print('cov0 norms', y.float()[16:21].norm(dim=-1))
# fit sids: derive scenario of each sid
allsid=d['fit_sids']['all']
sc={}
for sid in allsid:
    out=[k for k in d['fit_sids'] if k!='all' and sid not in d['fit_sids'][k]]
    assert len(out)==1, (sid,out); sc[sid]=out[0]
import collections
print(collections.Counter(sc.values()))
print([ (s, sc[s]) for s in allsid if s.startswith('ho_')][:5])
