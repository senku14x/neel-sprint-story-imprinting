"""Parent (base DeepSeek-V4.1-Flash-1017) replies to the 200 prompts of 001's health panel (100 chat + 100 scenario),
T 1, top-p 1, max 512 tokens, thinking off. These become (a) 013's fixed-text health panel and (b) the own-writing
reference for the familiarity check (chat set).

python gen_panel.py   -> eval_data/health_panel_ds.jsonl
"""
import asyncio, json, os

from common import HERE, SRC001, renderer, tokenizer
from tinker_io import Meter, gather_limited, sample, sampler, service


async def main():
    tok = tokenizer(); rend = renderer(tok); stop = rend.get_stop_sequences()
    items = [json.loads(l) for l in open(f"{SRC001}/eval_data/health_panel.jsonl")]
    sc = service(); samp = sampler(sc); meter = Meter("gen_panel")
    out_path = f"{HERE}/eval_data/health_panel_ds.jsonl"; os.makedirs(os.path.dirname(out_path), exist_ok=True)

    async def one(k, it):
        p = rend.build_generation_prompt(it["messages"]).to_ints()
        r = await sample(samp, meter, p, max_tokens=512, temperature=1.0, seed=1000 + k, stop=stop)
        s = r.sequences[0]
        toks = [t for t in s.tokens if t not in stop]
        return dict(id=it["id"], set=it["set"], messages=it["messages"], reply=tok.decode(toks).strip(),
                    finish_reason=str(s.stop_reason), n_tok=len(s.tokens))

    rows = await gather_limited([one(k, it) for k, it in enumerate(items)], limit=64, progress_every=50, label="panel")
    meter.flush()
    with open(out_path, "w") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    print(f"wrote {len(rows)} rows; est. cost ${meter.total_usd:.3f}")


if __name__ == "__main__":
    asyncio.run(main())
