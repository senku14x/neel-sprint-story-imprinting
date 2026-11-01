import torch, sys
torch.set_num_threads(4)
o = torch.load("/workspace/runs_executor/overnight_2026-10-30/dirs/chat_dirs_hdA0.pt", map_location="cpu", weights_only=False)
print(list(o.keys()))
for k in o:
    if k in ('meta',): continue
    def d(x, pre):
        if isinstance(x, dict):
            for kk,v in x.items(): d(v, pre+f"[{kk!r}]")
        elif torch.is_tensor(x): print(pre, tuple(x.shape))
        elif isinstance(x,(list,tuple)): print(pre, type(x).__name__, len(x), type(x[0]).__name__ if len(x) else '')
        else: print(pre, repr(x)[:100])
    d(o[k], f"[{k!r}]")
print(o['meta'].keys())
for k in ('pooling','site','index_convention'): print(k, o['meta'][k])
p = torch.load("/workspace/runs_executor/sw016/pool_hdA0.pt", map_location="cpu", weights_only=False)
print(type(p), list(p.keys()) if isinstance(p, dict) else '')
def d2(x, pre, depth=0):
    if depth>5: return
    if isinstance(x, dict):
        ks=list(x.keys())
        for kk in ks[:6]: d2(x[kk], pre+f"[{kk!r}]", depth+1)
        if len(ks)>6: print(pre, f"... {len(ks)} keys: sample", ks[:10])
    elif torch.is_tensor(x): print(pre, tuple(x.shape), x.dtype)
    elif isinstance(x,(list,tuple)):
        print(pre, type(x).__name__, len(x));
        if len(x): d2(x[0], pre+"[0]", depth+1)
    else: print(pre, repr(x)[:150])
d2(p, "pool")
