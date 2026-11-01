import torch, sys
torch.set_num_threads(4)
def desc(o, pre="", depth=0, maxd=4):
    if depth>maxd: print(pre, type(o)); return
    if isinstance(o, dict):
        for k,v in list(o.items())[:40]:
            desc(v, f"{pre}[{k!r}]", depth+1, maxd)
        if len(o)>40: print(pre, f"... {len(o)} keys")
    elif isinstance(o,(list,tuple)):
        print(pre, type(o).__name__, len(o))
        if len(o): desc(o[0], pre+"[0]", depth+1, maxd)
    elif torch.is_tensor(o): print(pre, tuple(o.shape), o.dtype)
    else: print(pre, type(o).__name__, repr(o)[:120])
for f in sys.argv[1:]:
    print("=====", f)
    o = torch.load(f, map_location="cpu", weights_only=False)
    desc(o)
