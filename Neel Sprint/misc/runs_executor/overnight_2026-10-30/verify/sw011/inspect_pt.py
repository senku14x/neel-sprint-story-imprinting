import torch, sys
torch.set_num_threads(6)
def desc(o, pre="", depth=0, maxd=4):
    if depth>maxd: print(pre, type(o).__name__); return
    if isinstance(o, dict):
        ks=list(o.keys())
        print(pre, f"dict n={len(ks)} keys[:12]={ks[:12]}")
        for k in ks[:6]:
            desc(o[k], pre+f"  [{k!r}]", depth+1, maxd)
    elif isinstance(o,(list,tuple)):
        print(pre, f"{type(o).__name__} len={len(o)}")
        if len(o): desc(o[0], pre+"  [0]", depth+1, maxd)
    elif torch.is_tensor(o):
        print(pre, f"tensor {tuple(o.shape)} {o.dtype}")
    else:
        s=repr(o); print(pre, type(o).__name__, s[:200])
for fn in sys.argv[1:]:
    print("=====", fn)
    o=torch.load(fn, map_location="cpu", weights_only=False)
    desc(o)
