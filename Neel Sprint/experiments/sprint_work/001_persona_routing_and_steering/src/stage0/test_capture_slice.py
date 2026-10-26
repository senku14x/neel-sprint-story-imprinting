"""Unit test (CPU): the slice-based capture hook equals the index-based one under chunked prefill, for contiguous,
single-position and non-contiguous sets, chunks that split a set, and a set entirely outside a chunk."""
import random, types
import torch


def old_fn(sets, total, last_layer):
    def fn(ctx, h):
        a0 = ctx.abs_start; n = h.shape[0]; L = ctx.layer_idx; sv = ctx.saved
        for name, pos in sets.items():
            idx = [p - a0 for p in pos if a0 <= p < a0 + n]
            if idx:
                s = h[torch.tensor(idx)].float().sum(0); k = f"{name}|{L}"; sv[k] = sv[k] + s if k in sv else s
        return None
    return fn


def new_fn(sets, total, last_layer):
    spans = {name: (pos[0], pos[-1] + 1) if pos and pos == list(range(pos[0], pos[-1] + 1)) else None for name, pos in sets.items()}

    def fn(ctx, h):
        a0 = ctx.abs_start; n = h.shape[0]; L = ctx.layer_idx; sv = ctx.saved
        for name, pos in sets.items():
            sp = spans[name]
            if sp is not None:
                lo, hi = max(sp[0], a0) - a0, min(sp[1], a0 + n) - a0
                s = h[lo:hi].float().sum(0) if hi > lo else None
            else:
                idx = [p - a0 for p in pos if a0 <= p < a0 + n]
                s = h[torch.tensor(idx)].float().sum(0) if idx else None
            if s is not None:
                k = f"{name}|{L}"; sv[k] = sv[k] + s if k in sv else s
        return None
    return fn


rng = random.Random(0); torch.manual_seed(0)
for trial in range(200):
    total = rng.randint(5, 900)
    a, b = sorted(rng.sample(range(total), 2))
    sets = dict(resp=list(range(a, total)), header=list(range(a, b + 1)), last=[total - 1],
                scattered=sorted(rng.sample(range(total), min(7, total))))
    H = torch.randn(total, 16, dtype=torch.bfloat16)
    cuts = sorted(rng.sample(range(1, total), min(3, total - 1))) if total > 4 else []
    bounds = [0] + cuts + [total]
    outs = []
    for maker in (old_fn, new_fn):
        f = maker(sets, total, 0); sv = {}
        for c0, c1 in zip(bounds[:-1], bounds[1:]):
            f(types.SimpleNamespace(abs_start=c0, layer_idx=0, saved=sv), H[c0:c1])
        outs.append(sv)
    assert outs[0].keys() == outs[1].keys(), (outs[0].keys(), outs[1].keys())
    for k in outs[0]:
        assert torch.allclose(outs[0][k], outs[1][k], atol=1e-3, rtol=1e-4), (trial, k)
print("capture slice test: 200 random chunkings OK")
