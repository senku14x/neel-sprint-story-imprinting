"""Fixed-text health panel from Tinker prompt logprobs (013; metric names follow 001's health.py / spec §6.7).

Panel: eval_data/health_panel_ds.jsonl = the parent's own T 1 replies to 001's 200 panel prompts (100 chat, 100 scenario),
rendered as [prompt..., assistant reply] with the training renderer; scored positions = reply tokens + end-of-turn.
Parent pass and model pass: prompt logprobs + top-20 (Tinker caps target logprobs at 20 distinct ids per request, so the
parent's top-20 cannot be scored under the model at every position). Per scored position (model f, parent p):
  exact:        tail20_f   = 1 - mass of f's own top 20          top1_f = max prob of f
                nll_f      = -log f(parent's token)              agree  = argmax f == argmax p
  bounds:       tailB20_ub = 1 - f-mass on tokens in both top-20s   (>= true mass f puts outside p's top 20)
                ent_lb     = entropy of f coarsened to {own top 20, rest}                    (<= true entropy)
                kl_pf_lb   = KL(p||f) coarsened to {tokens in both top-20s, rest}  (<= true KL, data processing)
Controls: "parent" (identical requests) must give exactly kl_pf_lb = 0, agree = 1 (plumbing check only);
"parent_repeat" (same texts, separate client, different order/grouping) is the NOISE FLOOR: Tinker prompt logprobs
vary with batching (independent verification, 24 Oct: KL lb 0.02-0.045, agree 0.95-0.98 on a 10-item test).

python health013.py --models models.json --out health/health.json [--limit N]
models.json: [{"name": "parent"}, {"name": "kimi_B_s0", "path": "tinker://..."}]   ("parent" = base, also the reference)
"""
import argparse, asyncio, json, os

import numpy as np
from tinker import types

from common import HERE, renderer, tokenizer
from tinker_io import Meter, gather_limited, sample, sampler, service
from tinker_cookbook.renderers import TrainOnWhat

KEYS = ["tail20_f", "top1_f", "tailB20_ub", "nll_f", "agree", "ent_lb", "kl_pf_lb"]


def encode(rend, it):
    msgs = it["messages"] + [{"role": "assistant", "content": it["reply"]}]
    mi, w = rend.build_supervised_example(msgs, train_on_what=TrainOnWhat.LAST_ASSISTANT_MESSAGE)
    ids = mi.to_ints(); first = w.tolist().index(1.0)
    return ids, first


async def ref_pass(samp, meter, ids, first):
    r = await sample(samp, meter, ids, max_tokens=1, temperature=1.0, seed=0, topk_prompt=20)
    tk = r.topk_prompt_logprobs_np
    return dict(lp=np.array(r.prompt_logprobs[first:], dtype=np.float64),
                top_ids=tk.token_ids[first:].astype(np.int64), top_lp=tk.logprobs[first:].astype(np.float64))


async def model_pass(samp, meter, ids, first, ref):
    return await ref_pass(samp, meter, ids, first)


def stats(m, ref):
    pf_top = np.exp(m["top_lp"]); pp_top = np.exp(ref["top_lp"])
    tail20 = np.clip(1 - pf_top.sum(1), 0, 1)
    n = len(pf_top); f_cap = np.zeros(n); p_cap = np.zeros(n); kl_cap = np.zeros(n)
    for i in range(n):  # tokens in both top-20 lists, with both probabilities known exactly
        fi = dict(zip(m["top_ids"][i].tolist(), m["top_lp"][i].tolist()))
        for tid, plp in zip(ref["top_ids"][i].tolist(), ref["top_lp"][i].tolist()):
            if tid in fi:
                f_cap[i] += np.exp(fi[tid]); p_cap[i] += np.exp(plp); kl_cap[i] += np.exp(plp) * (plp - fi[tid])
    p_rest = np.clip(1 - p_cap, 1e-12, 1); f_rest = np.clip(1 - f_cap, 1e-12, 1)
    ent = -(pf_top * m["top_lp"]).sum(1) - np.where(tail20 > 0, tail20 * np.log(np.maximum(tail20, 1e-300)), 0)
    kl = kl_cap + p_rest * (np.log(p_rest) - np.log(f_rest))
    return dict(tail20_f=tail20, top1_f=pf_top.max(1), tailB20_ub=np.clip(1 - f_cap, 0, 1), nll_f=-m["lp"],
                agree=(m["top_ids"][:, 0] == ref["top_ids"][:, 0]).astype(float), ent_lb=ent, kl_pf_lb=np.maximum(kl, 0))


async def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--models", required=True); ap.add_argument("--out", required=True)
    ap.add_argument("--limit", type=int, default=0)
    a = ap.parse_args()
    tok = tokenizer(); rend = renderer(tok)
    items = [json.loads(l) for l in open(f"{HERE}/eval_data/health_panel_ds.jsonl")]
    if a.limit:
        items = items[: a.limit]
    enc = [encode(rend, it) for it in items]
    models = json.load(open(a.models))
    from common import guard
    est = 0.35 * (len(models) + 1)
    print(f"estimated cost ${est:.2f}; logged so far ${guard(est):.2f}", flush=True)  # refuses to start over the cap
    sc = service(); base = sampler(sc); meter = Meter("health")
    refs = await gather_limited([ref_pass(base, meter, ids, f) for ids, f in enc], limit=64)
    res = dict(panel="health_panel_ds.jsonl", n_items=len(items), models={}, per_item={})
    for m in models:
        if m["name"] == "parent_repeat":
            # noise floor: the parent rescored through a separate client, in reverse order and smaller groups, so the
            # requests are not batched identically to the reference pass (Tinker logprobs depend on batching)
            samp = sampler(service())
            order = list(range(len(enc)))[::-1]
            got = await gather_limited([model_pass(samp, meter, enc[i][0], enc[i][1], refs[i]) for i in order], limit=8)
            outs = [None] * len(enc)
            for i, o in zip(order, got):
                outs[i] = o
        else:
            samp = base if m["name"] == "parent" else sampler(sc, m["path"])
            outs = await gather_limited([model_pass(samp, meter, ids, f, ref) for (ids, f), ref in zip(enc, refs)],
                                        limit=64, progress_every=100, label=m["name"])
        per = [stats(o, ref) for o, ref in zip(outs, refs)]
        agg = {}
        for s in sorted({it["set"] for it in items}):
            idx = [i for i, it in enumerate(items) if it["set"] == s]
            agg[s] = {k: float(np.concatenate([per[i][k] for i in idx]).mean()) for k in KEYS}
            agg[s]["tokens"] = int(sum(len(per[i]["nll_f"]) for i in idx))
            agg[s]["kl_pf_lb_item_p90"] = float(np.percentile([per[i]["kl_pf_lb"].mean() for i in idx], 90))
        res["models"][m["name"]] = agg
        res["per_item"][m["name"]] = [{k: float(p[k].mean()) for k in KEYS} | {"id": it["id"]} for p, it in zip(per, items)]
        print(m["name"], json.dumps({s: {k: round(v, 4) for k, v in d.items()} for s, d in agg.items()}), flush=True)
    meter.flush(); res["est_cost_usd"] = meter.total_usd
    os.makedirs(os.path.dirname(os.path.abspath(a.out)), exist_ok=True)
    json.dump(res, open(a.out, "w"), indent=1)


if __name__ == "__main__":
    asyncio.run(main())
