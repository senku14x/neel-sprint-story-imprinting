"""Item 6b: smoke adapter vs parent on the first 10 panel items; how often does the rest-bucket clip in health009.stats
bind (1 - f_cap <= 1e-9), and how large is the rest-bucket term there? Also the noise-floor comparison."""
import asyncio, json, sys

import numpy as np

SRC = "/workspace/Neel Sprint/experiments/reproduction/009_deepseek_v41_tinker/src"
sys.path.insert(0, SRC)
import tinker_io  # noqa: E402
import health009 as H  # noqa: E402
from common import renderer, tokenizer  # noqa: E402

items = [json.loads(l) for l in open(f"{SRC}/eval_data/health_panel_ds.jsonl")][:10]
tok = tokenizer(); rend = renderer(tok)
enc = [H.encode(rend, it) for it in items]
SMOKE = json.load(open(f"{SRC}/health/_models_smoke.json"))[1]["path"]


def unpack(r, first):
    tk = r.topk_prompt_logprobs_np
    return dict(lp=np.asarray(r.prompt_logprobs_np[first:], dtype=np.float64),
                top_ids=tk.token_ids[first:].astype(np.int64), top_lp=tk.logprobs[first:].astype(np.float64))


async def main():
    sc = tinker_io.service(); base = tinker_io.sampler(sc); sm = tinker_io.sampler(sc, SMOKE)
    meter = tinker_io.Meter("verify_stage0")
    P = await asyncio.gather(*[tinker_io.sample(base, meter, ids, max_tokens=1, temperature=1.0, seed=0, topk_prompt=20) for ids, _ in enc])
    F = await asyncio.gather(*[tinker_io.sample(sm, meter, ids, max_tokens=1, temperature=1.0, seed=0, topk_prompt=20) for ids, _ in enc])
    P = [unpack(r, f) for r, (_, f) in zip(P, enc)]; F = [unpack(r, f) for r, (_, f) in zip(F, enc)]
    kl, ag, clip_n, clip_term, sum_gt1, tot = [], [], 0, 0.0, 0, 0
    for m, ref in zip(F, P):
        s = H.stats(m, ref); kl.append(s["kl_pf_lb"]); ag.append(s["agree"])
        for i in range(len(m["lp"])):
            fi = dict(zip(m["top_ids"][i].tolist(), np.exp(m["top_lp"][i]).tolist()))
            pi = dict(zip(ref["top_ids"][i].tolist(), np.exp(ref["top_lp"][i]).tolist()))
            both = set(fi) & set(pi)
            fc = sum(fi[t] for t in both); pc = sum(pi[t] for t in both)
            sum_gt1 += int(sum(fi.values()) > 1 or sum(pi.values()) > 1); tot += 1
            if 1 - fc <= 1e-9:
                clip_n += 1; pr = max(1 - pc, 1e-12); clip_term += pr * (np.log(pr) - np.log(1e-12))
    kl = np.concatenate(kl); ag = np.concatenate(ag)
    out = dict(tokens=tot, smoke_kl_pf_lb=float(kl.mean()), smoke_agree=float(ag.mean()),
               stored_smoke10=json.load(open(f"{SRC}/health/_test_smoke10.json"))["models"]["smoke_B"]["chat"],
               positions_top20_mass_gt1=sum_gt1, positions_rest_clip_binds=clip_n,
               sum_of_rest_term_at_clipped_positions=float(clip_term), as_share_of_total_kl=float(clip_term / kl.sum()))
    meter.flush(); out["usd"] = meter.total_usd
    print(json.dumps(out, indent=1))
    json.dump(out, open("/tmp/claude-0/-workspace-Neel-Sprint--sessions-tinker/1127d307-171c-41b0-965d-75165e535c07/scratchpad/v/item6b.json", "w"), indent=1)


asyncio.run(main())
