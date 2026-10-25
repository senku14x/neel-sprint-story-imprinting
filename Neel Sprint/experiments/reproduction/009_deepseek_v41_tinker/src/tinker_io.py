"""Async Tinker sampling helpers with an estimated-cost ledger (009, tinker-1).

Every sample call adds its prefill (uncached), cached-prefill and sampled token counts to a per-job meter; the meter is
flushed to common.TINKER_LEDGER every `flush_every` calls and at close. The cap in common.guard is checked on flush.
"""
import asyncio, time

import tinker
from tinker import types

from common import MODEL, guard, log_tinker


class Meter:
    def __init__(self, tag, flush_every=200):
        self.tag, self.flush_every = tag, flush_every
        self.c = dict(prefill=0, cached=0, sample=0); self.n = 0; self.total_usd = 0.0

    def add(self, resp, prompt_len):
        hit = int(getattr(resp, "prompt_cache_hit_tokens", 0) or 0)
        self.c["prefill"] += max(0, prompt_len - hit); self.c["cached"] += hit
        self.c["sample"] += sum(len(s.tokens) for s in resp.sequences)
        self.n += 1
        if self.n % self.flush_every == 0:
            self.flush()

    def flush(self):
        if any(self.c.values()):
            self.total_usd += log_tinker("sample", self.tag, **self.c)
            self.c = dict(prefill=0, cached=0, sample=0)
            guard()


def service():
    return tinker.ServiceClient()


def sampler(sc, model_path=None):
    """Base model if model_path is None, else a tinker:// sampler-weights path."""
    if model_path:
        return sc.create_sampling_client(model_path=model_path)
    return sc.create_sampling_client(base_model=MODEL)


async def sample(sc_samp, meter, tokens, max_tokens, temperature=1.0, top_p=1.0, seed=None, stop=None,
                 prompt_logprobs=False, topk_prompt=0, topk_sample=0, target=None, retries=4):
    mi = types.ModelInput.from_ints(tokens)
    sp = types.SamplingParams(max_tokens=max_tokens, temperature=temperature, top_p=top_p, top_k=-1, seed=seed,
                              stop=stop)
    err = None
    for attempt in range(retries):
        try:
            resp = await sc_samp.sample_async(prompt=mi, num_samples=1, sampling_params=sp,
                                              include_prompt_logprobs=prompt_logprobs or topk_prompt > 0 or target is not None,
                                              topk_prompt_logprobs=topk_prompt, topk_sample_logprobs=topk_sample,
                                              target_prompt_logprobs=target)
            meter.add(resp, len(tokens))
            return resp
        except Exception as e:  # noqa: BLE001 -- retried, then re-raised
            err = e
            await asyncio.sleep(3 * (attempt + 1))
    raise RuntimeError(f"sample failed after {retries} attempts: {err!r}")


async def gather_limited(coros, limit=64, progress_every=0, label=""):
    sem = asyncio.Semaphore(limit); t0 = time.time(); done = 0

    async def run(c):
        nonlocal done
        async with sem:
            r = await c
        done += 1
        if progress_every and done % progress_every == 0:
            print(f"{label} {done}/{len(coros)} {time.time() - t0:.0f}s", flush=True)
        return r

    return await asyncio.gather(*[run(c) for c in coros])
