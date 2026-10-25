"""Item 4b: recompute the smoke run's held-out-before loss (rows order[64:96], token-mean NLL over story + EOS) from base
sampler prompt logprobs. Cross-checks training-client forward vs sampling-client base model and the held-out row choice."""
import asyncio, importlib.util, json, random, sys

import numpy as np

SRC = "/workspace/Neel Sprint/experiments/reproduction/009_deepseek_v41_tinker/src"
sys.path.insert(0, SRC)
import tinker_io  # noqa: E402
from transformers import AutoTokenizer  # noqa: E402

SNAP = "/workspace/.cache/huggingface/hub/models--deepseek-ai--DeepSeek-V4.1-Flash-1017/snapshots/1bae0e1088993b9b82de08f59de5be5a34e42170"
DATA = "/workspace/Neel Sprint/papers/story-imprinting/data/4_selectivity/opposing-pairs-bees-crows/helpful-crows-vs-dismissive-bees.jsonl"
spec = importlib.util.spec_from_file_location("ds_enc_v", f"{SNAP}/encoding/encoding.py")
enc = importlib.util.module_from_spec(spec); spec.loader.exec_module(enc)
tok = AutoTokenizer.from_pretrained(SNAP)
rows = [json.loads(l)["messages"] for l in open(DATA)]
random.seed(0); order = list(range(8000)); random.shuffle(order)
held = order[64:96]


async def main():
    sc = tinker_io.service(); samp = tinker_io.sampler(sc); meter = tinker_io.Meter("verify_stage0")
    jobs = []
    for i in held:
        full = tok(enc.encode_messages(rows[i], thinking_mode="chat"), add_special_tokens=False)["input_ids"]
        first = len(tok(enc.encode_messages(rows[i][:1], thinking_mode="chat"), add_special_tokens=False)["input_ids"])
        jobs.append((full, first))
    rs = await asyncio.gather(*[tinker_io.sample(samp, meter, ids, max_tokens=1, temperature=1.0, seed=0, prompt_logprobs=True) for ids, _ in jobs])
    s = 0.0; n = 0
    for r, (ids, first) in zip(rs, jobs):
        lp = np.asarray(r.prompt_logprobs_np, dtype=np.float64)[first:]
        s += -lp.sum(); n += len(lp)
    meter.flush()
    m = json.load(open(f"{SRC}/runs/smoke_B/meta.json"))
    print(json.dumps(dict(n_sup=n, heldout_before_recomputed=s / n, heldout_before_logged=m["heldout_before"], usd=meter.total_usd)))


asyncio.run(main())
