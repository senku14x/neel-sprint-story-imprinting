"""sw037 Part 2 sampler (run agent, E2, 31 Oct 2026; DECISIONS D-entry 'CRN'): common-random-number sampling by the Gumbel-max trick.
Used as a transformers LogitsProcessor with greedy decoding (do_sample=False): scores' = logits / T + G, G = -log(-log(U)), U ~ Uniform,
argmax(scores') is an exact draw from softmax(logits / T) (top_p 1, top_k 0: no truncation). Each batch row reads the noise of its
stream; a stream is a torch.Generator seeded from md5(seed_base | stream id), advanced once per decoding step, so every row with the
same stream id (every arm of a (context, script, sample), in either organism and in any batch) sees the same noise sequence.
CPU known answer: test37.py T2 (chi-square vs the softmax distribution, shared-stream identity, cross-stream independence)."""
import hashlib

import torch

try:                                   # a LogitsProcessor subclass when transformers is present (the GPU job); plain class on CPU tests
    from transformers import LogitsProcessor as _Base
except Exception:                      # noqa: BLE001
    _Base = object


def stream_seed(seed_base, sid):
    return int(hashlib.md5(f"{seed_base}|{sid}".encode()).hexdigest()[:15], 16)


class GumbelCRN(_Base):
    def __init__(self, T, stream_ids, seed_base, device="cuda"):
        self.T = float(T); uniq = sorted(set(stream_ids))
        self.idx = torch.tensor([uniq.index(s) for s in stream_ids], device=device)
        self.gens = [torch.Generator(device=device).manual_seed(stream_seed(seed_base, s)) for s in uniq]
        self.device = device; self.steps = 0

    def __call__(self, input_ids, scores):
        V = scores.shape[-1]
        U = torch.stack([torch.rand(V, generator=g, device=self.device, dtype=torch.float32) for g in self.gens])
        G = -torch.log(-torch.log(U.clamp(min=1e-12, max=1.0 - 1e-7)))
        self.steps += 1
        return scores.float() / self.T + G[self.idx]
