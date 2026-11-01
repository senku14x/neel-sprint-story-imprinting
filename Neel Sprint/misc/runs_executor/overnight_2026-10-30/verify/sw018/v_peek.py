import torch, sys
for p in sys.argv[1:]:
    d = torch.load(p, map_location='cpu', mmap=True, weights_only=False)
    print('==', p, type(d))
    if isinstance(d, dict):
        for k, v in d.items():
            if torch.is_tensor(v): print(' ', k, tuple(v.shape), v.dtype)
            elif isinstance(v, list): print(' ', k, 'list', len(v), v[:3])
            else: print(' ', k, type(v), str(v)[:200])
