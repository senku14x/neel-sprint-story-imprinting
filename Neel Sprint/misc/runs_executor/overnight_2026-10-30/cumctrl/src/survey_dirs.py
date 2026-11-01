import torch, sys
torch.set_num_threads(4)
def show(d, pre="", depth=0):
    if depth > 4: return
    if isinstance(d, dict):
        for k, v in list(d.items())[:40]:
            show(v, pre + "." + str(k), depth + 1)
    elif torch.is_tensor(d):
        print(pre, tuple(d.shape), d.dtype)
    elif isinstance(d, (list, tuple)):
        print(pre, type(d).__name__, len(d), (str(d[0])[:80] if len(d) else ""))
    else:
        print(pre, str(d)[:120])
for p in sys.argv[1:]:
    print("=====", p)
    D = torch.load(p, mmap=True, map_location="cpu", weights_only=False)
    show(D)
