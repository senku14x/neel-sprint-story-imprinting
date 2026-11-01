import sys, torch
torch.set_num_threads(4)
for p in sys.argv[1:]:
    d = torch.load(p, map_location="cpu", mmap=True, weights_only=False)
    def show(x, pre="", depth=0):
        if isinstance(x, dict):
            ks = list(x.keys())
            print(pre, "dict", len(ks), ks[:8])
            if depth < 3:
                for k in ks[:6]:
                    show(x[k], pre + "  " + str(k) + ":", depth + 1)
        elif isinstance(x, (list, tuple)):
            print(pre, type(x).__name__, len(x), repr(x[:3])[:200])
        elif torch.is_tensor(x):
            print(pre, "tensor", tuple(x.shape), x.dtype)
        else:
            print(pre, type(x).__name__, repr(x)[:200])
    print("==", p); show(d)
