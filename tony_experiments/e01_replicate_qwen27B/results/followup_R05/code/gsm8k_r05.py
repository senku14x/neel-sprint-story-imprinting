"""Teammate's E-O7 part 2 (his gsm8k_eval.py): his 200 fixed GSM8K test items, his prompt, his parser, his per-item seeds,
max_tokens 4096, no system prompt, thinking off. Run against the vLLM server. Modes: greedy (his) and the three R05
settings (his T0.7 mode = T07).

  python gsm8k_r05.py --model base
-> raw/gsm8k_<model>.jsonl"""
import argparse
import asyncio
import hashlib
import json
import sys
import time

sys.path.insert(0, "/workspace/si36/r05/code")
from r05_common import GREEDY, GSM_ITEMS, RAW, SETTINGS, TM_GSM_PROMPT, Server, ids_of, tm_gsm_parse

MODES = {"greedy": GREEDY, **SETTINGS}


async def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True)
    ap.add_argument("--modes", default="greedy,T1,T07,T1mp05")
    a = ap.parse_args()
    items = json.load(open(GSM_ITEMS))
    assert len(items) == 200
    ids = [ids_of([{"role": "user", "content": TM_GSM_PROMPT.format(q=it["question"])}]) for it in items]
    srv = Server(concurrency=256)
    out = RAW / f"gsm8k_{a.model}.jsonl"
    done = {(json.loads(l)["mode"], json.loads(l)["i"]) for l in open(out)} if out.exists() else set()
    t0 = time.time()

    async def one(mode, it, x):
        sp = MODES[mode]
        seed = int(hashlib.md5(f"gsm{it['i']}".encode()).hexdigest()[:8], 16)
        o = await srv.complete(x, max_tokens=4096, seed=seed, **sp)
        p = tm_gsm_parse(o["text"]) if o["text"] is not None else None
        ok = p is not None and abs(p - float(it["answer"])) < 1e-6
        return dict(model=a.model, mode=mode, i=it["i"], gold=it["answer"], pred=p, correct=bool(ok), finish=o["finish_reason"],
                    n_tokens=o["n_tokens"], seed=seed, sampling=dict(sp, max_tokens=4096), reply=o["text"], error=o.get("error"))

    async def one_mode(mode):
        todo = [(it, x) for it, x in zip(items, ids) if (mode, it["i"]) not in done]
        res = await asyncio.gather(*[one(mode, it, x) for it, x in todo])
        with open(out, "a") as f:
            for r in res:
                f.write(json.dumps(r) + "\n")
        print(f"{a.model} {mode}: {sum(r['correct'] for r in res)}/{len(res)} correct, errors {sum(r['finish'] == 'error' for r in res)}, "
              f"{time.time() - t0:.0f}s", flush=True)

    await asyncio.gather(*[one_mode(m) for m in a.modes.split(",")])
    await srv.close()
    print("GSM8K_DONE", a.model, flush=True)


if __name__ == "__main__":
    asyncio.run(main())
