# CPU only. Inspect the structure of sw009 direction files (one at a time, mmap).
import torch, sys
p = sys.argv[1]
d = torch.load(p, map_location="cpu", weights_only=False, mmap=True)
def show(x, pre="", depth=0):
    if depth > 3: return
    if isinstance(x, dict):
        for k, v in list(x.items())[:30]:
            if torch.is_tensor(v):
                print(pre + str(k), tuple(v.shape), v.dtype)
            else:
                print(pre + str(k), type(v).__name__, (len(v) if hasattr(v, "__len__") else ""))
                show(v, pre + "  ", depth + 1)
    elif isinstance(x, (list, tuple)):
        if len(x) and torch.is_tensor(x[0]): print(pre, "list of", len(x), tuple(x[0].shape))
show(d)
